"""Download pinned public model assets into the personal codesign volume.

The manifest contains public file names, revisions, sizes and LFS SHA256s.
Existing verified files are reused; incomplete transfers never become final files.
"""

import argparse
import hashlib
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


def _sha256(path):
    with path.open("rb") as stream:
        digest = hashlib.sha256()
        for chunk in iter(lambda: stream.read(8 << 20), b""):
            digest.update(chunk)
        return digest.hexdigest()


def _download(item, *, endpoint, root, timeout):
    destination = root / item["repo_id"] / item["revision"] / item["filename"]
    destination.parent.mkdir(parents=True, exist_ok=True)
    expected_size = item["size"]
    expected_sha = item.get("sha256")
    if destination.exists():
        if destination.stat().st_size != expected_size or (expected_sha and _sha256(destination) != expected_sha):
            raise ValueError(f"Existing model asset does not match the pinned manifest: {destination}")
        return {"path": str(destination), "size": expected_size, "sha256": _sha256(destination), "reused": True}
    temporary = destination.with_name(destination.name + ".agent-opd.partial")
    url = f"{endpoint}/{item['repo_id']}/resolve/{item['revision']}/{item['filename']}"
    subprocess.run(
        [
            "curl",
            "--noproxy",
            "*",
            "--fail",
            "--location",
            "--silent",
            "--show-error",
            "--connect-timeout",
            "30",
            "--max-time",
            str(timeout),
            "--output",
            str(temporary),
            url,
        ],
        check=True,
    )
    actual_sha = _sha256(temporary)
    if temporary.stat().st_size != expected_size or (expected_sha and actual_sha != expected_sha):
        raise ValueError(f"Incomplete or incorrect pinned model asset: {destination}")
    temporary.replace(destination)
    print(f"MODEL_FILE_VERIFIED {destination} {expected_size}", flush=True)
    return {"path": str(destination), "size": expected_size, "sha256": actual_sha, "reused": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--endpoint", required=True)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--timeout", type=int, default=3600)
    args = parser.parse_args()
    args.output_root.resolve().relative_to("/mnt/codesign-exp/ycfeng")
    items = json.loads(args.manifest.read_text())["files"]
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = list(
            pool.map(
                lambda item: _download(item, endpoint=args.endpoint, root=args.output_root, timeout=args.timeout),
                items,
            )
        )
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps({"status": "complete", "files": results}, indent=2) + "\n")
    print("MODEL_DOWNLOAD_COMPLETE", len(results), flush=True)


if __name__ == "__main__":
    main()
