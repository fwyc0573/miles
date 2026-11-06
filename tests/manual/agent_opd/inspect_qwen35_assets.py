"""Inspect explicitly authorized model sources and personal training-source availability."""

import argparse
import hashlib
import json
import os
from pathlib import Path


_PERSONAL_ROOT = Path("/mnt/codesign-exp/ycfeng")


def _read_path(path: Path, roots: tuple[Path, ...] = (_PERSONAL_ROOT,)) -> Path:
    resolved = path.resolve()
    if not any(resolved.is_relative_to(root.absolute()) for root in roots):
        raise ValueError(f"Read outside the authorized source directories: {path}")
    return resolved


def _model_metadata(directory: Path, roots: tuple[Path, ...]) -> dict:
    directory = _read_path(directory, roots)
    config_path = _read_path(directory / "config.json", roots)
    index_path = _read_path(directory / "model.safetensors.index.json", roots)
    result = {"path": str(directory), "config_exists": config_path.is_file(), "index_exists": index_path.is_file()}
    if not result["config_exists"] or not result["index_exists"]:
        return result
    config = json.loads(config_path.read_text())
    index = json.loads(index_path.read_text())
    text_config = config.get("text_config", config)
    result.update(
        architecture=config.get("architectures"),
        model_type=config.get("model_type"),
        text_model_type=text_config.get("model_type"),
        max_position_embeddings=text_config.get("max_position_embeddings"),
        tensor_count=len(index["weight_map"]),
        metadata_sha256={},
        shards=[],
    )
    for name in ("config.json", "tokenizer.json", "tokenizer_config.json", "chat_template.jinja", index_path.name):
        path = _read_path(directory / name, roots)
        result["metadata_sha256"][name] = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
    for name in sorted(set(index["weight_map"].values())):
        path = _read_path(directory / name, roots)
        result["shards"].append({"name": name, "size": path.stat().st_size if path.is_file() else None})
    result["all_indexed_shards_exist"] = all(row["size"] is not None for row in result["shards"])
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", nargs=2, action="append", required=True, metavar=("NAME", "AUTHORIZED_DIRECTORY"))
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    model_roots = (_PERSONAL_ROOT, *(Path(path) for _, path in args.model))
    result = {
        "job": os.environ.get("KUBEBRAIN_RJOB_NAME"),
        "model_sources": dict(args.model),
        "models": {},
        "sources": [],
    }
    for name, path in args.model:
        model = _read_path(Path(path), model_roots)
        candidates = [model] if _read_path(model / "config.json", model_roots).is_file() else []
        if model.is_dir() and not candidates:
            candidates = sorted(path for path in model.iterdir() if not path.is_symlink() and path.is_dir())
        result["models"][name] = [_model_metadata(path, model_roots) for path in candidates]
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    result["manifest_sha256"] = hashlib.sha256(manifest_bytes).hexdigest()
    for file in manifest["files"]:
        path = _read_path(Path(file["path"]))
        size = path.stat().st_size if path.is_file() else None
        result["sources"].append({"path": str(path), "expected_size": file["size"], "actual_size": size})
    args.report.parent.mkdir(parents=True, exist_ok=True)
    with args.report.open("x") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print("QWEN35_ASSET_INSPECTION", json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
