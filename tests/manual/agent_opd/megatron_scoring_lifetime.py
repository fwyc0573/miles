"""Apply the two PP1 output-lifetime indentation changes to one pinned dependency.

This preflight uses only the standard library and must precede the native Ray
driver launch. It never imports Megatron or changes an unrecognized source.

    python -m tests.manual.agent_opd.megatron_scoring_lifetime \
        --megatron-path "$MEGATRON_PATH" --image "$IMAGE" \
        --archive-dir "$ARCHIVE" --release-scoring-output
"""

import argparse
import hashlib
import importlib.metadata
import json
import subprocess
from pathlib import Path


_MANIFEST = Path(__file__).with_suffix(".json")
_PATCH = Path(__file__).with_suffix(".patch")


def source_manifest() -> dict:
    return json.loads(_MANIFEST.read_text())


def expected_source_sha256(release: bool) -> str:
    return source_manifest()["after_sha256" if release else "before_sha256"]


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _git(root: Path, *arguments: str) -> bytes:
    return subprocess.check_output(
        ["git", "-c", f"safe.directory={root}", "-C", str(root), *arguments], stderr=subprocess.STDOUT
    )


def _archive(path: Path, content: bytes) -> None:
    if path.exists():
        if path.read_bytes() != content:
            raise ValueError(f"Scoring lifetime archive differs from the verified source: {path}")
    else:
        path.write_bytes(content)


def prepare_source(root: Path, *, image: str, release: bool, archive_dir: Path) -> dict:
    """Verify the dependency and archive the exact original/current source and diff."""
    manifest = source_manifest()
    patch = _PATCH.read_bytes()
    if _sha256(patch) != manifest["patch_sha256"]:
        raise ValueError("Scoring lifetime patch differs from the verified two-indentation diff")
    root = root.resolve()
    if type(release) is not bool:
        raise ValueError("release_scoring_output must be a JSON boolean")
    if image != manifest["image"]:
        raise ValueError("Scoring lifetime preflight requires the qualified pinned image")
    commit = _git(root, "rev-parse", "HEAD").decode().strip()
    version = importlib.metadata.version("megatron-core")
    if commit != manifest["megatron_commit"] or version != manifest["distribution_version"]:
        raise ValueError(f"Scoring lifetime dependency identity differs: commit={commit}, version={version}")
    source = root / manifest["source_path"]
    original = _git(root, "show", f"HEAD:{manifest['source_path']}")
    if _sha256(original) != manifest["before_sha256"]:
        raise ValueError("Pinned Megatron HEAD does not contain the verified scoring schedule")
    before = source.read_bytes()
    observed_before = _sha256(before)
    allowed = {manifest["before_sha256"], manifest["after_sha256"]} if release else {manifest["before_sha256"]}
    if observed_before not in allowed:
        raise ValueError(f"Unrecognized scoring schedule; refusing to alter it: {source} ({observed_before})")

    archive_dir.mkdir(parents=True, exist_ok=True)
    _archive(archive_dir / "schedules.before.py", original)
    _archive(archive_dir / _PATCH.name, patch)
    _archive(archive_dir / _MANIFEST.name, _MANIFEST.read_bytes())
    applied = release and observed_before == manifest["before_sha256"]
    if applied:
        _git(root, "apply", "--check", str(_PATCH))
        _git(root, "apply", str(_PATCH))
    after = source.read_bytes()
    observed_after = _sha256(after)
    if observed_after != expected_source_sha256(release):
        raise ValueError(f"Scoring lifetime patch produced an unexpected schedule: {observed_after}")
    _archive(archive_dir / "schedules.after.py", after)
    receipt = {
        **manifest,
        "megatron_path": str(root),
        "release_scoring_output": release,
        "observed_before_sha256": observed_before,
        "observed_after_sha256": observed_after,
        "patch_applied": applied,
        "archive_dir": str(archive_dir),
    }
    with (archive_dir / "preflight.jsonl").open("a") as stream:
        stream.write(json.dumps(receipt, allow_nan=False) + "\n")
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--megatron-path", type=Path, required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--archive-dir", type=Path, required=True)
    parser.add_argument("--release-scoring-output", action="store_true")
    args = parser.parse_args()
    print(
        json.dumps(
            prepare_source(
                args.megatron_path, image=args.image, release=args.release_scoring_output, archive_dir=args.archive_dir
            ),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
