"""Check closed-seed archival, local cleanup, and archive failure evidence."""

import errno
from pathlib import Path
from types import SimpleNamespace

import pytest

from tests.manual.agent_opd import rjob_benchmark as benchmark


def _scenario(tmp_path: Path):
    logs = tmp_path / "worker" / "logs"
    logs.mkdir(parents=True)
    output = tmp_path / "cloud" / "job"
    output.mkdir(parents=True)
    seed_directory = logs / "step20" / "seed-1731"
    trajectory = seed_directory / "error_trajectories" / "failed.json"
    trajectory.parent.mkdir(parents=True)
    trajectory.write_text('{"meta":{"error_type":"InjectedNativeError"}}\n')
    server_log = logs / "server-20.log"
    server_log.write_text("active server\n")
    sibling = logs / "native-20-1732.log"
    sibling.write_text("active sibling\n")
    args = SimpleNamespace(
        native_python=Path("/usr/bin/python3"),
        native_pythonpath="native/source",
        membership=tmp_path / "membership.json",
        sandbox_backend="basemind",
        sandbox_registry=None,
        task_index=2,
        benchmark_timeout=21600,
    )
    server = {"version": 20, "url": "http://127.0.0.1:12345", "model": "agent-opd-step20"}
    return args, server, output, logs, seed_directory


def _native_exit(monkeypatch, exit_code):
    def run(command, **kwargs):
        kwargs["stdout"].write("closed native pipeline\n")
        return SimpleNamespace(returncode=exit_code)

    monkeypatch.setattr(benchmark.subprocess, "run", run)


@pytest.mark.parametrize("exit_code", [0, 1])
def test_completed_seed_is_available_before_siblings_exit(tmp_path, monkeypatch, exit_code):
    args, server, output, logs, seed_directory = _scenario(tmp_path)
    _native_exit(monkeypatch, exit_code)
    assert benchmark._run_seed(server, 1731, args, output, logs) == exit_code
    assert (output / "diagnostics/step20/seed-1731/error_trajectories/failed.json").read_text() == (
        '{"meta":{"error_type":"InjectedNativeError"}}\n'
    )
    assert (output / "diagnostics/native-20-1731.log").read_text() == "closed native pipeline\n"
    assert not seed_directory.exists()
    assert not (logs / "native-20-1731.log").exists()
    assert (logs / "native-20-1732.log").read_text() == "active sibling\n"
    assert (logs / "server-20.log").read_text() == "active server\n"


def test_archive_failure_preserves_local_native_evidence(tmp_path, monkeypatch):
    args, server, output, logs, seed_directory = _scenario(tmp_path)
    _native_exit(monkeypatch, 0)

    def fail_copy(source, destination):
        raise OSError(errno.EIO, "injected archive failure")

    monkeypatch.setattr(benchmark.shutil, "copytree", fail_copy)
    with pytest.raises(OSError, match="injected archive failure"):
        benchmark._run_seed(server, 1731, args, output, logs)
    assert (seed_directory / "error_trajectories/failed.json").is_file()
    assert (logs / "native-20-1731.log").read_text() == "closed native pipeline\n"
    assert (logs / "native-20-1732.log").read_text() == "active sibling\n"
    assert (logs / "server-20.log").read_text() == "active server\n"


def test_final_archive_preserves_completed_seed_diagnostics(tmp_path, monkeypatch):
    args, server, output, logs, _ = _scenario(tmp_path)
    _native_exit(monkeypatch, 0)
    benchmark._run_seed(server, 1731, args, output, logs)
    benchmark.shutil.copytree(logs, output / "diagnostics", dirs_exist_ok=True)
    assert (output / "diagnostics/step20/seed-1731/error_trajectories/failed.json").is_file()
    assert (output / "diagnostics/native-20-1731.log").read_text() == "closed native pipeline\n"
    assert (output / "diagnostics/server-20.log").read_text() == "active server\n"
