"""Retain the selected Rust binding identity and its candidate source trees."""

import hashlib
import importlib
import importlib.metadata
import importlib.util
import json
import os
import platform
import shutil
import subprocess
import sys
import sysconfig
from datetime import datetime, timezone
from pathlib import Path


def digest_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def command(argv, *, cwd=None):
    result = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, timeout=30)
    return {"command": argv, "returncode": result.returncode,
            "stdout": result.stdout, "stderr": result.stderr}


def selected_source(path):
    return (path.suffix in {".rs", ".toml", ".lock", ".h", ".hpp", ".cpp", ".cc"}
            or path.name.startswith("rust-toolchain"))


archive = Path(sys.argv[1])
image = sys.argv[2]
output = archive / os.environ["KUBEBRAIN_RJOB_NAME"]
output.mkdir(parents=True, exist_ok=False)
package = Path(importlib.util.find_spec("sglang").origin).resolve().parent
checkout = package.parents[1]
rust = checkout / "rust"
distribution = importlib.metadata.distribution("sglang")
files = []


def retain(path, relative):
    content = path.read_bytes()
    destination = output / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(content)
    files.append({"source": str(path), "path": str(relative), "bytes": len(content),
                  "sha256": hashlib.sha256(content).hexdigest()})


if rust.is_dir():
    for directory, children, names in os.walk(rust):
        children[:] = sorted(name for name in children if name not in {"target", ".git"})
        for name in sorted(names):
            path = Path(directory) / name
            if selected_source(path):
                retain(path, Path("checkout") / "rust" / path.relative_to(rust))
for name in ("pyproject.toml", "setup.py", "rust-toolchain", "rust-toolchain.toml"):
    path = checkout / name
    if path.is_file():
        retain(path, Path("checkout") / name)
for name in ("METADATA", "direct_url.json", "WHEEL"):
    path = Path(distribution._path) / name
    if path.is_file():
        retain(path, Path("distribution") / name)

environment_names = ("SGLANG_IMAGE_TAG", "SGLANG_BUILD_COMMIT", "SGLANG_RUST_BUILD_MODE",
                     "SGLANG_BUILD_RUST_EXTS", "SGLANG_CACHE_DIR", "RUSTUP_TOOLCHAIN")
environment = {name: os.environ.get(name) for name in environment_names}
receipt = {"image": image, "requested_gpus": 0, "collected_at": datetime.now(timezone.utc).isoformat(),
           "python": platform.python_version(), "executable": sys.executable,
           "package": str(package), "checkout": str(checkout), "rust_workspace": str(rust),
           "sglang_version": distribution.version, "extension_suffix": sysconfig.get_config_var("EXT_SUFFIX"),
           "environment": environment, "files": files, "binary_source_commit": "UNVERIFIED"}
git_head = command(["git", "rev-parse", "HEAD"], cwd=checkout)
receipt["git_head"] = git_head
receipt["git_rust_status"] = command(["git", "status", "--porcelain", "--", "rust"], cwd=checkout)
receipt["git_rust_last_change"] = command(["git", "log", "-1", "--format=%H%n%ad", "--", "rust"], cwd=checkout)
candidate_commits = [git_head["stdout"].strip(), environment["SGLANG_BUILD_COMMIT"]]
receipt["git_source_candidates"] = []
for revision in dict.fromkeys(value for value in candidate_commits if value):
    available = command(["git", "cat-file", "-e", revision + "^{commit}"], cwd=checkout)
    candidate = {"revision": revision, "available": available["returncode"] == 0, "files": []}
    receipt["git_source_candidates"].append(candidate)
    if not candidate["available"]:
        candidate["error"] = available["stderr"]
        continue
    listing = subprocess.run(["git", "ls-tree", "-r", "--name-only", revision, "--", "rust"],
                             cwd=checkout, capture_output=True, text=True, timeout=30, check=True)
    for relative in listing.stdout.splitlines():
        if not selected_source(Path(relative)):
            continue
        content = subprocess.check_output(["git", "show", revision + ":" + relative], cwd=checkout, timeout=30)
        destination = Path("git") / revision / relative
        path = output / destination
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        row = {"source": revision + ":" + relative, "path": str(destination), "bytes": len(content),
               "sha256": hashlib.sha256(content).hexdigest()}
        files.append(row)
        candidate["files"].append(str(destination))

toolchains = Path(os.environ.get("RUSTUP_HOME", str(Path.home() / ".rustup"))) / "toolchains"
receipt["installed_toolchains"] = []
if toolchains.is_dir():
    for toolchain in sorted(toolchains.iterdir()):
        versions = {"name": toolchain.name}
        for name, flags in (("cargo", ["--version", "--verbose"]), ("rustc", ["-vV"])):
            binary = toolchain / "bin" / name
            if binary.is_file():
                versions[name] = command([str(binary), *flags])
        receipt["installed_toolchains"].append(versions)

failure = None
try:
    if environment["SGLANG_RUST_BUILD_MODE"] != "never":
        raise RuntimeError("Identity collector refuses a Rust load mode that might build")
    import torch
    if torch.cuda.is_initialized():
        raise RuntimeError("CUDA was initialized before the CPU-only binding inspection")
    extension = importlib.import_module("sglang.srt.mem_cache.rust_tree_core.extension")
    binding = extension.bindings
    origin = Path(binding.__file__).resolve()
    receipt["loaded_binding"] = {"module": binding.__name__, "origin": str(origin),
                                 "bytes": origin.stat().st_size, "sha256": digest_file(origin),
                                 "bundled": origin.is_relative_to(package),
                                 "module_version": getattr(binding, "__version__", None),
                                 "torch_version": str(torch.__version__),
                                 "torch_cxx11_abi": bool(torch.compiled_with_cxx11_abi()),
                                 "cuda_initialized": torch.cuda.is_initialized()}
    if receipt["loaded_binding"]["cuda_initialized"]:
        raise RuntimeError("CUDA was initialized during the CPU-only binding inspection")
    readelf = shutil.which("readelf")
    if readelf:
        receipt["binary_notes"] = command([readelf, "-n", str(origin)])
        receipt["binary_comment"] = command([readelf, "-p", ".comment", str(origin)])
        dynamic = command([readelf, "-d", str(origin)])
        dynamic["stdout"] = "\n".join(line for line in dynamic["stdout"].splitlines()
                                          if any(name in line for name in ("NEEDED", "RPATH", "RUNPATH")))
        receipt["binary_dependencies"] = dynamic
    strings = shutil.which("strings")
    if strings:
        binary_strings = command([strings, str(origin)])
        terms = ("sglang-radix-tree", "sgl-workspace", "rustc ", "297e54fd", "056f871")
        receipt["binary_source_hints"] = [line for line in binary_strings["stdout"].splitlines()
                                           if any(term in line for term in terms)][:64]
    receipt["binary_hint_limit"] = "Paths, compiler strings, and image environment do not prove a source commit."
except Exception as error:
    failure = error
    receipt["binding_error"] = {"type": type(error).__name__, "message": str(error)}

(output / "source.json").write_text(json.dumps(receipt, indent=2) + "\n")
for row in files:
    retained = output / row["path"]
    assert retained.stat().st_size == row["bytes"] and digest_file(retained) == row["sha256"]
print("RUST_SOURCE_RETAINED", len(files), "FILES", len([row for row in files if row["path"].endswith(".rs")]), "RUST", flush=True)
if failure is not None:
    raise failure
print("RUST_BINDING_IDENTITY", json.dumps(receipt["loaded_binding"]), flush=True)
