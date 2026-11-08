"""Consume the pinned Steptron DEFAULT SWE turn stream through Miles DataSource.

The external loader owns file/conversation/turn ordering and epoch wrapping.
Only native role normalization and Qwen-specific rendering happen here; no
conversation pool, shuffle, deduplication or target-message training is added.
"""

import copy
import hashlib
import importlib.util
import json
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType

from examples.agentic_opd.glm_turns import normalize_tool_arguments, token_hash

from miles.rollout.data_source import DataSource
from miles.utils.args.schema import A, Arg, BaseConfig
from miles.utils.processing_utils import load_tokenizer
from miles.utils.types import Sample

logger = logging.getLogger(__name__)


class SWEInputConfig(BaseConfig):
    swe_source_root: A[str, Arg()]
    swe_source_manifest: A[str, Arg()]
    swe_native_loader_path: A[str, Arg()]
    swe_native_loader_sha256: A[str, Arg()]
    swe_skip_masked_assistant_turns: A[bool, Arg()] = False
    swe_visual_filter_receipt: A[str | None, Arg()] = None


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def load_native_module(path: Path, expected_sha256: str) -> ModuleType:
    """Load the pinned CPU module, registering it before dataclass exec."""
    content = path.read_bytes()
    actual = hashlib.sha256(content).hexdigest()
    if actual != expected_sha256:
        raise ValueError(f"Native SWE loader SHA256 mismatch: expected {expected_sha256}, got {actual}")
    name = f"_steptron_swe_turn_loader_{actual}"
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        try:
            # Execute the verified bytes, not a second filesystem read.
            exec(compile(content, str(path), "exec"), module.__dict__)
        except BaseException:
            del sys.modules[name]
            raise
    return sys.modules[name]


def load_swe_native_module(args) -> ModuleType:
    path = Path(args.swe_native_loader_path).resolve()
    if args.swe_skip_masked_assistant_turns:
        # The pinned SWE1003 module imports its CPU-only native package peers.
        # Its existing playground/users/cj/opd package layout owns this root.
        root = str(path.parents[4])
        if root not in sys.path:
            sys.path.insert(0, root)
    return load_native_module(path, args.swe_native_loader_sha256)


@dataclass(frozen=True)
class SWESourcePopulation:
    files: tuple[dict, ...]
    manifest: dict
    manifest_sha256: str

    @property
    def filelist(self) -> list[str]:
        return [entry["local_path"] for entry in self.files]


def load_source_population(source_root: Path, manifest_path: Path) -> SWESourcePopulation:
    """Verify source bytes once at construction, in the manifest's recipe order."""
    content = manifest_path.read_bytes()
    manifest = json.loads(content)
    if manifest["status"] != "COMPLETE":
        raise ValueError("SWE source manifest is not COMPLETE")
    files = []
    for entry in manifest["files"]:
        path = (source_root / Path(entry["path"]).name).resolve()
        if path.stat().st_size != entry["bytes"] or file_sha256(path) != entry["sha256"]:
            raise ValueError(f"SWE source bytes differ from the manifest: {path}")
        files.append({**entry, "local_path": str(path)})
    if sum(entry["bytes"] for entry in files) != manifest["total_bytes"]:
        raise ValueError("SWE source manifest total_bytes disagrees with its files")
    return SWESourcePopulation(tuple(files), manifest, hashlib.sha256(content).hexdigest())


def native_chat_messages(conversation: list[dict]) -> list[dict]:
    """Match the native recipe's convert_to_chatml_with_tool (lines 527-553)."""
    messages = copy.deepcopy(conversation)
    for message in messages:
        role = message.get("role", message.get("from"))
        if not isinstance(role, str):
            raise NotImplementedError(f"Non compatible type for data: {message}")
        role = role.lower()
        if role == "human":
            role = "user"
        if role not in {"user", "assistant", "system", "context", "tool"}:
            raise NotImplementedError(f"Non compatible type for data: {message}")
        message["role"] = role
        message.pop("from", None)
        if "content" not in message and "value" in message:
            message["content"] = message.pop("value")
        else:
            message.pop("value", None)
        if "content" not in message and role != "assistant":
            raise NotImplementedError(f"Non compatible type for data: {message}")
    return messages


def render_qwen_history(tokenizer, history: list[dict], tools: list[dict] | None, kwargs: dict) -> tuple[str, list[int]]:
    prompt = tokenizer.apply_chat_template(
        normalize_tool_arguments(history),
        tools=tools,
        tokenize=False,
        add_generation_prompt=True,
        **kwargs,
    )
    return prompt, tokenizer.encode(prompt, add_special_tokens=False)


def native_source_identity(item: dict, file: dict, epoch: int) -> dict:
    ground_truth = item["conversation"][-1]["ground_truth"]
    conversation_index = ground_truth["source_item_index"]
    return {
        "uid": f"{file['sha256']}:{conversation_index}:{ground_truth['assistant_turn_index']}",
        "group_id": f"{file['sha256']}:{conversation_index}",
        "category": "swe",
        "file_sha256": file["sha256"],
        "path": ground_truth["data_path"],
        "original_path": file["path"],
        "epoch": epoch,
        **{name: ground_truth[name] for name in (
            "source_item_index", "source_row_index", "source_message_count",
            "assistant_turn_index", "assistant_turn_ordinal", "num_context_messages",
        )},
        **{name: ground_truth[name] for name in (
            "target_policy", "target_loss_mask", "source_assistant_turn_ordinal", "context_masked_assistant_count",
        ) if name in ground_truth},
    }


class NativeSWEDataSource(DataSource):
    """One independent native cursor per instance; only accepted turns get slots.

    Args use the existing Miles fields hf_checkpoint, chat_template_path,
    apply_chat_template_kwargs, rollout_max_context_len and n_samples_per_prompt. The custom
    data_source_path config adds swe_source_root, swe_source_manifest,
    swe_native_loader_path and swe_native_loader_sha256. The optional native
    mask policy requires swe_skip_masked_assistant_turns and a verified
    swe_visual_filter_receipt. Paths are caller-owned.
    """

    config_class = SWEInputConfig

    def __init__(self, args, *, tokenizer=None, population: SWESourcePopulation | None = None, native_source=None):
        if args.n_samples_per_prompt != 1:
            raise ValueError("Native SWE inputs require n_samples_per_prompt=1")
        if args.rollout_max_context_len is None or args.rollout_max_context_len <= 0:
            raise ValueError("Native SWE rollout_max_context_len must be set and positive")
        if args.rollout_max_response_len < args.rollout_max_context_len:
            raise ValueError("Native SWE remaining-context generation requires rollout_max_response_len >= rollout_max_context_len")
        kwargs = dict(args.apply_chat_template_kwargs)
        if kwargs.get("preserve_thinking") is not True or kwargs.get("enable_thinking") is not True:
            raise ValueError("Native Qwen SWE inputs require preserve_thinking=true and enable_thinking=true")
        reserved = {"tools", "chat_template", "tokenize", "add_generation_prompt", "return_dict"} & kwargs.keys()
        if reserved:
            raise ValueError(f"SWE rendering owns template arguments: {sorted(reserved)}")
        if args.swe_skip_masked_assistant_turns and native_source is None and args.swe_visual_filter_receipt is None:
            raise ValueError("Native mask-aware SWE inputs require a verified swe_visual_filter_receipt")
        native = load_swe_native_module(args)
        self.population = population if population is not None else load_source_population(
            Path(args.swe_source_root), Path(args.swe_source_manifest)
        )
        source_kwargs = dict(domain="reasoning", source_group="swe", source_load_path=None, source_load_safetensors=None)
        if native_source is not None:
            # Test-only injection cannot be supplied through SWEInputConfig.
            self.native = native_source
        elif args.swe_skip_masked_assistant_turns:
            exclusions = native.load_visual_filter_exclusions(args.swe_visual_filter_receipt, self.population.filelist)
            self.native = native.MaskAwareSWETurnSource(
                self.population.filelist, excluded_source_item_indices=exclusions, **source_kwargs,
            )
        else:
            self.native = native.OnlineTrajectoryTurnSource(self.population.filelist, **source_kwargs)
        self._files = {entry["local_path"]: entry for entry in self.population.files}
        self.tokenizer = tokenizer if tokenizer is not None else load_tokenizer(
            args.hf_checkpoint, chat_template_path=args.chat_template_path, local_files_only=True,
        )
        self.template_kwargs = kwargs
        self.context_tokens = args.rollout_max_context_len
        self.sample_index = 0
        self.skipped_overlength = 0
        self.identity = {
            "native_loader_path": str(Path(args.swe_native_loader_path).resolve()),
            "native_loader_sha256": args.swe_native_loader_sha256,
            "source_manifest_path": str(Path(args.swe_source_manifest).resolve()),
            "source_manifest_sha256": self.population.manifest_sha256,
            "files": list(self.population.files),
            "hf_checkpoint": args.hf_checkpoint,
            "tokenizer_json_sha256": file_sha256(Path(args.hf_checkpoint) / "tokenizer.json"),
            "tokenizer_config_json_sha256": file_sha256(Path(args.hf_checkpoint) / "tokenizer_config.json"),
            "chat_template_path": args.chat_template_path,
            "chat_template_sha256": file_sha256(Path(args.chat_template_path)),
            "chat_template_kwargs": kwargs,
            "rollout_max_context_len": self.context_tokens,
            "rollout_max_response_len": args.rollout_max_response_len,
            "n_samples_per_prompt": 1,
            "domain": "reasoning", "source_group": "swe", "reward_fn_type": "noop",
            "source_load_path": None, "source_load_safetensors": None,
            "shuffle": False, "deduplicate": False, "epoch_wrap": True,
            "length_reject": "prompt_token_count >= rollout_max_context_len",
            "generation_budget": "rollout_max_context_len - prompt_token_count",
            "tools_rendering_difference": "Step caller omits system.tools; Qwen passes system.tools explicitly",
            "resume_supported": False,
        }
        if args.swe_skip_masked_assistant_turns:
            base = sys.modules[native.OnlineTrajectoryTurnSource.__module__]
            dependencies = [importlib.import_module(name) for name in (
                "playground.users.cj.opd.s4_swe_visual_filter_1001",
                "playground.users.cj.opd.s4_swe_visual_audit_1001",
                "playground.users.cj.opd.s4_swe_source_manifest_1001",
            )]
            self.identity.update(
                native_base_path=base.__file__, native_base_sha256=file_sha256(Path(base.__file__)),
                native_dependencies=[{"path": module.__file__, "sha256": file_sha256(Path(module.__file__))}
                                     for module in dependencies],
                target_policy=native.TARGET_POLICY,
                visual_exclusion_policy=native.VISUAL_EXCLUSION_POLICY,
                visual_filter_receipt=args.swe_visual_filter_receipt,
                visual_filter_receipt_sha256=(file_sha256(Path(args.swe_visual_filter_receipt))
                                             if args.swe_visual_filter_receipt is not None else None),
                visual_filter_verified=native_source is None,
                native_source_injected_for_test=native_source is not None,
                tools_rendering_difference="Native SWE1003 adaptive Step and Qwen both receive tools; model templates differ",
            )
        logger.info("NATIVE_SWE_INPUT_IDENTITY %s", json.dumps(self.identity))

    def get_samples(self, num_samples: int) -> list[list[Sample]]:
        if num_samples < 0:
            raise ValueError("num_samples must be non-negative")
        samples = []
        while len(samples) < num_samples:
            item = next(self.native)
            messages = native_chat_messages(item["conversation"])
            history = messages[:-1]
            tools = history[0].get("tools") if history else None
            prompt, prompt_ids = render_qwen_history(self.tokenizer, history, tools, self.template_kwargs)
            source = native_source_identity(item, self._files[item["conversation"][-1]["ground_truth"]["data_path"]],
                                            self.native.cursor.epoch)
            source.update(prompt_token_count=len(prompt_ids), prompt_sha256=token_hash(prompt_ids))
            if len(prompt_ids) >= self.context_tokens:
                self.skipped_overlength += 1
                logger.info("NATIVE_SWE_INPUT_REJECT %s", json.dumps({
                    "source": source, "reason": "prompt_at_or_above_context_limit", "rollout_max_context_len": self.context_tokens,
                }))
                continue
            sample = Sample(
                index=self.sample_index, group_index=self.sample_index, prompt=prompt,
                max_seq_len=self.context_tokens, max_response_len=self.context_tokens - len(prompt_ids),
                metadata={
                    "source": source, "history": history, "tools": tools,
                    "thinking_enabled": True, "chat_template_kwargs": dict(self.template_kwargs),
                    "native_ground_truth": messages[-1]["ground_truth"],
                },
            )
            self.sample_index += 1
            samples.append([sample])
        return samples

    def save(self, directory: Path) -> None:
        """Write an audit receipt, not a resumable optimizer/RNG/replay checkpoint."""
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "native_swe_inputs.json").write_text(json.dumps({
            "identity": self.identity, "accepted_turns": self.sample_index,
            "emitted_turns": self.native.emitted_turns, "skipped_overlength": self.skipped_overlength,
            "resume_supported": False,
        }, indent=2) + "\n")

    def load(self, directory: Path) -> None:
        raise NotImplementedError("Native SWE training restore is unsupported; HF-only exports cannot restore cursor/replay/optimizer state")

    def close(self) -> None:
        self.native.close()
