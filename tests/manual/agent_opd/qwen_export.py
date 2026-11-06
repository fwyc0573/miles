"""Package Miles' raw Qwen3.5 decoder export for the official text-only loader.

Use ``--custom-megatron-post-save-hook-path
tests.manual.agent_opd.qwen_export.post_save`` with native ``--save-hf`` and no
native ``--save``. The hook receives Miles' immutable custom-function view; it
needs no additional flags. Native export and conversion I/O errors propagate.
Auxiliary contract failures are logged and recorded as unverified, not raised
into healthy training. ``qwen_text_export.json`` records packaging, not a real
full-model inference reload or numerical acceptance.
"""

import json
import logging
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile

import torch
from safetensors import safe_open
from safetensors.torch import save_file
from transformers import AutoConfig, AutoModelForCausalLM

from miles.utils.args.custom_view import ImmutableNamespace

logger = logging.getLogger(__name__)

_INDEX = "model.safetensors.index.json"
_REPORT = "qwen_text_export.json"
_RAW_PREFIX = "model.language_model."
_EXCLUDED_PREFIXES = ("model.visual.", "mtp.")
_PROCESSOR_FILES = ("preprocessor_config.json", "processor_config.json", "video_preprocessor_config.json")
_DTYPES = {"BF16": torch.bfloat16, "F16": torch.float16, "F32": torch.float32}


class QwenTextExportError(ValueError):
    """The saved tensors or metadata do not satisfy the text-loader contract."""


@dataclass(frozen=True)
class _Tensor:
    shard: str
    shape: tuple[int, ...]
    dtype: str


def _text_config(source: Path):
    config = AutoConfig.from_pretrained(source, local_files_only=True)
    if config.model_type != "qwen3_5":
        raise QwenTextExportError(f"Expected the dense Qwen3.5 source, got {config.model_type!r}")
    text = config.get_text_config()
    if text.model_type != "qwen3_5_text" or text.tie_word_embeddings != config.tie_word_embeddings:
        raise QwenTextExportError("Source text configuration or embedding tying disagrees with the full model")
    text.architectures = ["Qwen3_5ForCausalLM"]
    # The actor trains the decoder, not the source checkpoint's MTP predictor.
    text.mtp_num_hidden_layers = 0
    text.__dict__.pop("mtp_use_dedicated_embeddings", None)
    return text


def _expected_shapes(config) -> dict[str, tuple[int, ...]]:
    # Use the official architecture as the schema without allocating model weights.
    with torch.device("meta"):
        model = AutoModelForCausalLM.from_config(config)
    if type(model).__name__ != "Qwen3_5ForCausalLM":
        raise QwenTextExportError(f"Unexpected official text loader {type(model).__name__!r}")
    return {name: tuple(tensor.shape) for name, tensor in model.state_dict().items()}


def _read_tensors(path: Path) -> dict[str, _Tensor]:
    if not (path / _INDEX).is_file():
        raise QwenTextExportError("The native export is missing its shard index")
    index = json.loads((path / _INDEX).read_text())
    weight_map = index["weight_map"]
    shards = set(weight_map.values())
    if any(Path(shard).name != shard for shard in shards):
        raise QwenTextExportError("Native shard names must be local filenames")
    if shards != {file.name for file in path.glob("*.safetensors")}:
        raise QwenTextExportError("Native shard files and shard index disagree")
    tensors = {}
    for shard in sorted(shards):
        with safe_open(path / shard, framework="pt", device="cpu") as handle:
            if set(handle.keys()) != {name for name, file in weight_map.items() if file == shard}:
                raise QwenTextExportError(f"Tensor names in {shard} disagree with the shard index")
            for name in handle.keys():
                tensor = handle.get_slice(name)
                tensors[name] = _Tensor(shard, tuple(tensor.get_shape()), tensor.get_dtype())
    return tensors


def _text_name(name: str) -> str | None:
    if name.startswith(_EXCLUDED_PREFIXES):
        return None
    if name.startswith(_RAW_PREFIX):
        return "model." + name[len(_RAW_PREFIX) :]
    if name == "lm_head.weight":
        return name
    raise QwenTextExportError(f"Unexpected raw decoder tensor {name!r}")


def _validate_tensors(path: Path, tensors: dict[str, _Tensor], config) -> dict[str, str | None]:
    names = {name: _text_name(name) for name in tensors}
    expected = _expected_shapes(config)
    actual = {target for target in names.values() if target is not None}
    required = set(expected)
    if config.tie_word_embeddings:
        required.remove("lm_head.weight")
    if required - actual or actual - set(expected):
        raise QwenTextExportError(
            f"Decoder tensor coverage mismatch: missing={sorted(required - actual)}, "
            f"unexpected={sorted(actual - set(expected))}"
        )
    embedding = tensors[_RAW_PREFIX + "embed_tokens.weight"]
    if embedding.dtype not in _DTYPES:
        raise QwenTextExportError(f"Unsupported decoder dtype {embedding.dtype!r}")
    for raw_name, name in names.items():
        if name is None:
            continue
        tensor = tensors[raw_name]
        if tensor.shape != expected[name]:
            raise QwenTextExportError(f"{raw_name}: shape {tensor.shape} != expected {expected[name]}")
        if tensor.dtype not in {embedding.dtype, "F32"}:
            raise QwenTextExportError(f"{raw_name}: incompatible decoder dtype {tensor.dtype!r}")
    if config.tie_word_embeddings and "lm_head.weight" in tensors:
        head = tensors["lm_head.weight"]
        with (
            safe_open(path / embedding.shard, framework="pt", device="cpu") as embed_file,
            safe_open(path / head.shard, framework="pt", device="cpu") as head_file,
        ):
            if head.dtype != embedding.dtype or not torch.equal(
                embed_file.get_tensor(_RAW_PREFIX + "embed_tokens.weight"), head_file.get_tensor("lm_head.weight")
            ):
                raise QwenTextExportError("Tied embedding and LM head tensors differ")
        # HF's official tied save contract stores just the canonical embedding.
        names["lm_head.weight"] = None
    config.dtype = _DTYPES[embedding.dtype]
    return names


def _validate_tokenizer(source: Path, path: Path) -> None:
    for filename in ("tokenizer.json", "tokenizer_config.json", "chat_template.jinja"):
        original, exported = source / filename, path / filename
        if filename != "chat_template.jinja" and not original.is_file():
            raise QwenTextExportError(f"Source tokenizer is missing {filename}")
        if original.is_file() and (not exported.is_file() or original.read_bytes() != exported.read_bytes()):
            raise QwenTextExportError(f"Exported tokenizer asset {filename} differs from the source")


def _rewrite_shards(path: Path, tensors: dict[str, _Tensor], names: dict[str, str | None]) -> dict:
    weight_map = {}
    total_size = 0
    for shard in sorted({tensor.shard for tensor in tensors.values()}):
        with safe_open(path / shard, framework="pt", device="cpu") as handle:
            retained = {names[name]: handle.get_tensor(name) for name in handle.keys() if names[name] is not None}
            if retained:
                total_size += sum(tensor.numel() * tensor.element_size() for tensor in retained.values())
                weight_map.update({name: shard for name in retained})
                with NamedTemporaryFile(dir=path, suffix=".text-export", delete=False) as temporary:
                    temporary_path = Path(temporary.name)
                try:
                    save_file(retained, temporary_path, metadata={"format": "pt"})
                except Exception:
                    temporary_path.unlink(missing_ok=True)
                    raise
            del retained
        if any(names[name] is not None for name, tensor in tensors.items() if tensor.shard == shard):
            temporary_path.replace(path / shard)
        else:
            (path / shard).unlink()
    return {"metadata": {"total_size": total_size}, "weight_map": weight_map}


def _write_report(path: Path, report: dict) -> None:
    try:
        (path / _REPORT).write_text(json.dumps(report, indent=2))
    except OSError:
        logger.exception("Qwen text export evidence is unverified: auxiliary report could not be saved; training continues")


def export_text_checkpoint(source: str | Path, path: str | Path) -> dict:
    """Strictly convert an already-written native export; never write source assets."""
    source, path = Path(source).resolve(), Path(path).resolve()
    if source == path:
        raise QwenTextExportError("The export destination must not be the source checkpoint")
    try:
        config = _text_config(source)
        tensors = _read_tensors(path)
        names = _validate_tensors(path, tensors, config)
        _validate_tokenizer(source, path)
    except QwenTextExportError:
        raise
    except Exception as error:
        # Model-schema/header/tokenizer inspection is auxiliary. Unexpected
        # validator failures must not terminate a healthy large training run.
        raise QwenTextExportError(f"Text export inspection failed: {type(error).__name__}: {error}") from error
    report = {"status": "unverified", "source": str(source), "reason": "Text packaging has not completed"}
    _write_report(path, report)
    index = _rewrite_shards(path, tensors, names)
    (path / _INDEX).write_text(json.dumps(index, indent=2))
    config.save_pretrained(path)
    for filename in _PROCESSOR_FILES:
        (path / filename).unlink(missing_ok=True)
    report = {
        "status": "packaged",
        "source": str(source),
        "architecture": config.architectures[0],
        "model_type": config.model_type,
        "num_hidden_layers": config.num_hidden_layers,
        "tie_word_embeddings": config.tie_word_embeddings,
        "dtype": str(config.dtype),
        "tensor_dtypes": dict(Counter(tensors[name].dtype for name, target in names.items() if target is not None)),
        "saved_tensor_count": len(index["weight_map"]),
        "total_size": index["metadata"]["total_size"],
        "excluded_tensors": sorted(name for name in tensors if name.startswith(_EXCLUDED_PREFIXES)),
        "omitted_tied_head": config.tie_word_embeddings,
        "reload_verified": False,
    }
    _write_report(path, report)
    return report


def post_save(
    args: ImmutableNamespace, rollout_id: int, checkpoint_dir: str | None, hf_checkpoint_dir: str | None
) -> None:
    """Native rank-zero callback with a nonblocking auxiliary contract verdict."""
    if hf_checkpoint_dir is None:
        raise ValueError("Qwen text-only packaging requires --save-hf")
    if Path(hf_checkpoint_dir).resolve() == Path(args.hf_checkpoint).resolve():
        raise ValueError("The export destination must not be the source checkpoint")
    try:
        report = export_text_checkpoint(args.hf_checkpoint, hf_checkpoint_dir)
    except QwenTextExportError as error:
        report = {"status": "unverified", "rollout_id": rollout_id, "reason": str(error), "reload_verified": False}
        logger.error("Qwen text export is unverified; training continues: %s", error)
        _write_report(Path(hf_checkpoint_dir), report)
        return
    report["rollout_id"] = rollout_id
    _write_report(Path(hf_checkpoint_dir), report)
    logger.info("Qwen text-only checkpoint packaged at %s; real inference reload remains required", hf_checkpoint_dir)
