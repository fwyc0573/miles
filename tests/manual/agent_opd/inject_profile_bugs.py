"""Retain the original 2026-11-08 pre-baseline profile mutations in fresh sandboxes.

Provenance: /data/ycfeng/tmp/agent-opd-image/inject_profile_bugs.py (preserved).
The historical text replacements intentionally remain unchanged. A replacement
that no longer matches is reported as STALE, never as a detected mutation.

Run from the repository root:
  python -m tests.manual.agent_opd.inject_profile_bugs --temporary-root <existing-temp-directory>
Only sandbox copies are modified; pytest logs and results.json stay there.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
MODULE = Path("tests/manual/agent_opd/distillation_profile.py")
TEST = Path("tests/fast/test_distillation_profile.py")
MUTATIONS = {
    "unpatched": None,
    "tie_moves_best": ("        if rkl < self.rkl[self.best]:", "        if rkl <= self.rkl[self.best]:"),
    "token_weighted_conversation_mean": (
        "            rkl = sum(self._rkl_sum[r] / self._tokens[r] for r in rows) / len(rows)",
        "            rkl = sum(self._rkl_sum[r] for r in rows) / sum(self._tokens[r] for r in rows)",
    ),
    "trend_off_by_one": ("self._updates[latest - k - 1].rkl", "self._updates[latest - k].rkl"),
}


def run_mutations(mutations: dict, temporary_root: Path, prefix: str) -> dict:
    parent = temporary_root.resolve(strict=True)
    if parent.is_relative_to(REPO_ROOT):
        raise ValueError("Mutation sandboxes must be outside the repository")
    sandbox = Path(tempfile.mkdtemp(prefix=prefix, dir=parent))
    results = {}
    for name, mutation in mutations.items():
        tree = sandbox / name
        for path in (MODULE, TEST):
            (tree / path).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REPO_ROOT / path, tree / path)
        if mutation is not None:
            source = (tree / MODULE).read_text()
            matches = source.count(mutation[0])
            if matches != 1:
                results[name] = {"status": "STALE", "replacement_matches": matches}
                continue
            (tree / MODULE).write_text(source.replace(mutation[0], mutation[1], 1))
        run = subprocess.run(
            [sys.executable, "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider", "--rootdir", str(tree),
             "--basetemp", str(tree / "pytest-tmp"), str(TEST)],
            cwd=tree, env={"PYTHONPATH": str(tree), "PATH": os.environ["PATH"], "PYTHONDONTWRITEBYTECODE": "1"},
            capture_output=True, text=True,
        )
        (tree / "pytest.log").write_text(run.stdout + run.stderr)
        expected_code = 0 if mutation is None else 1
        lines = (run.stdout + run.stderr).strip().splitlines()
        results[name] = {"status": "PASS" if run.returncode == expected_code else "FAIL",
                         "exit_code": run.returncode, "pytest_summary": lines[-1] if lines else ""}
    result = {"status": "PASS" if all(row["status"] == "PASS" for row in results.values()) else "FAIL",
              "sandbox": str(sandbox), "source_root": str(REPO_ROOT), "results": results}
    (sandbox / "results.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def main(mutations=MUTATIONS, prefix="profile-mutations-") -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--temporary-root", type=Path, required=True)
    args = parser.parse_args()
    result = run_mutations(mutations, args.temporary_root, prefix)
    print(json.dumps(result, indent=2))
    raise SystemExit(result["status"] != "PASS")


if __name__ == "__main__":
    main()
