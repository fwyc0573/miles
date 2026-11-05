"""Record completed-update identity after the native final HF export."""

import json
import subprocess
from pathlib import Path

from safetensors import safe_open


def record_export(args, rollout_id: int, checkpoint_dir: str | None, hf_checkpoint_dir: str | None) -> None:
    if hf_checkpoint_dir is None:
        raise ValueError("The learning test requires a final HF export")
    directory = Path(hf_checkpoint_dir)
    directory.relative_to("/mnt/codesign-exp/ycfeng")
    if not (directory / ".complete").is_file():
        raise ValueError("The native HF export did not publish its completion marker")
    tensors = {}
    for path in sorted(directory.glob("*.safetensors")):
        with safe_open(path, framework="pt", device="cpu") as weights:
            for name in weights.keys():
                if name in tensors:
                    raise ValueError(f"Duplicate exported tensor: {name}")
                tensors[name] = weights.get_slice(name).get_shape()
    if not tensors:
        raise ValueError("The native HF export contains no tensors")
    result = {
        "rollout_id": rollout_id,
        "completed_optimizer_updates": rollout_id + 1,
        "hf_directory": str(directory),
        "megatron_directory": checkpoint_dir,
        "tensor_count": len(tensors),
        "source_commit": subprocess.check_output(
            ["git", "-C", str(Path(__file__).resolve().parents[3]), "rev-parse", "HEAD"], text=True
        ).strip(),
        "identity_scope": "Native save is invoked after training this rollout; reconcile with normal step events",
    }
    (directory / "learning_identity.json").write_text(json.dumps(result, indent=2) + "\n")
    print("AGENT_OPD_FINAL_HF_EXPORTED", json.dumps(result), flush=True)
