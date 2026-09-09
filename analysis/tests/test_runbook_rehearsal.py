"""CR-D02: rehearse docs/PHASE1_RUNBOOK.md end to end on synthetic fixtures.

The runbook is what the owner will type when the Earth Engine exports arrive. These tests
execute the command block *as written in the document* (parsed from the markdown, placeholders
substituted) rather than a copy of it, so the runbook and the CLI cannot drift apart silently.
They also hold the runbook's exit-code table to the mapping in phase1_gate.main.

Synthetic fixtures only; nothing here establishes any Mongolia result. The synthetic path is
required to exit DEVELOPMENT_ONLY (3), and the real, unverified sites manifest is required
to exit INCONCLUSIVE (2) even with well-formed metrics -- the two outcomes the runbook promises.
"""
import csv, json, re, shlex, subprocess, sys
from pathlib import Path
import pytest

from test_phase1_gate import fixture

ROOT = Path(__file__).resolve().parents[2]
RUNBOOK = ROOT / "docs" / "PHASE1_RUNBOOK.md"
PLACEHOLDERS = ("PATH_TO_DEV_01.csv", "PATH_TO_DEV_02.csv", "PATH_TO_DEV_03.csv", "PATH_TO_NEGATIVE_01.csv")
EXIT_CODES = {"SCREEN_PASS": 0, "SCREEN_FAIL": 1, "INCONCLUSIVE": 2, "DEVELOPMENT_ONLY": 3}


def runbook_command() -> str:
    """The gate invocation exactly as documented, joined across its line continuations."""
    text = RUNBOOK.read_text(encoding="utf-8")
    blocks = re.findall(r"```sh\n(.*?)```", text, re.S)
    cmds = [b for b in blocks if "phase1_gate --sites" in b]
    assert len(cmds) == 1, f"expected exactly one documented gate invocation, found {len(cmds)}"
    cmd = " ".join(line.rstrip("\\").strip() for line in cmds[0].strip().splitlines())
    for ph in PLACEHOLDERS:
        assert ph in cmd, f"runbook placeholder {ph} missing from the documented command"
    return cmd


def write_fixture_csvs(tmp_path: Path):
    """One one-row CSV per site, the four-file shape the runbook and --metrics help describe."""
    manifest, rows = fixture()
    sites = tmp_path / "sites.synthetic.geojson"
    sites.write_text(json.dumps(manifest))
    by_id = {r["site_id"]: r for r in rows}
    order = sorted(r for r in by_id if r.startswith("dev-")) + sorted(r for r in by_id if not r.startswith("dev-"))
    assert len(order) == 4, f"fixture should describe 3 development + 1 negative-control site, got {order}"
    paths = []
    for site_id, ph in zip(order, PLACEHOLDERS):
        p = tmp_path / ph
        with p.open("w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(by_id[site_id])); w.writeheader(); w.writerow(by_id[site_id])
        paths.append(p)
    return sites, paths


def run_documented(cmd: str, sites: Path, paths, kind: str):
    # Parse the documented invocation before substituting literal input paths.
    # Downloads with spaces or apostrophes are arguments, not shell syntax.
    substitutions = dict(zip(PLACEHOLDERS, map(str, paths)))
    substitutions.update({"config/sites.geojson": str(sites), "earth-engine-export": kind})
    argv = [substitutions.get(token, token) for token in shlex.split(cmd)]
    assert argv[:2] == ["python", "-m"], "expected a documented Python module invocation"
    argv[0] = sys.executable
    proc = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True)
    assert proc.stdout.strip(), f"documented command emitted no JSON: {proc.stderr}"
    return proc, json.loads(proc.stdout)


def test_runbook_cli_is_importable_in_the_test_environment():
    """Check the test environment, not package installation or distribution.

    PYTHONPATH can also make this pass; no install is performed by this test.
    """
    proc = subprocess.run([sys.executable, "-m", "catanroads.phase1_gate", "--help"], cwd=ROOT, capture_output=True, text=True)
    assert proc.returncode == 0, ("catanroads is not importable as a module; run the runbook's install step "
                                  "`python -m pip install -e ./analysis --no-deps` first.\n" + proc.stderr[-300:])


def test_runbook_exit_code_table_matches_the_cli():
    text = RUNBOOK.read_text(encoding="utf-8")
    for status, code in EXIT_CODES.items():
        assert re.search(rf"\b{code} {status}\b", text), f"runbook does not document exit {code} as {status}"
    src = (ROOT / "analysis" / "catanroads" / "phase1_gate.py").read_text()
    mapping = re.search(r'return (\{"SCREEN_PASS": \d, "SCREEN_FAIL": \d, "INCONCLUSIVE": \d, "DEVELOPMENT_ONLY": \d\})', src)
    assert mapping and json.loads(mapping.group(1)) == EXIT_CODES


def test_documented_command_on_synthetic_fixtures_is_development_only(tmp_path):
    sites, paths = write_fixture_csvs(tmp_path)
    proc, result = run_documented(runbook_command(), sites, paths, "synthetic")
    assert result["status"] == "DEVELOPMENT_ONLY", result.get("errors")
    assert proc.returncode == EXIT_CODES["DEVELOPMENT_ONLY"]
    assert set(result["input_sha256"]) == {str(sites), *map(str, paths)}


@pytest.mark.parametrize("directory", ["export files", "export (July)", "export's files"])
def test_runbook_substitution_preserves_literal_paths(tmp_path, directory):
    export_dir = tmp_path / directory
    export_dir.mkdir()
    sites, paths = write_fixture_csvs(export_dir)
    proc, result = run_documented(runbook_command(), sites, paths, "synthetic")
    assert proc.returncode == EXIT_CODES["DEVELOPMENT_ONLY"], proc.stderr
    assert result["status"] == "DEVELOPMENT_ONLY"
    assert set(result["input_sha256"]) == {str(sites), *map(str, paths)}


def test_documented_command_on_real_unverified_manifest_is_inconclusive(tmp_path):
    # Same well-formed metrics, but the committed sites manifest has verified=false. The runbook
    # promises this cannot pass; it must not, even when declared as an Earth Engine export.
    _, paths = write_fixture_csvs(tmp_path)
    proc, result = run_documented(runbook_command(), ROOT / "config" / "sites.geojson", paths, "earth-engine-export")
    assert result["status"] == "INCONCLUSIVE"
    assert proc.returncode == EXIT_CODES["INCONCLUSIVE"]


def test_documented_command_with_a_missing_export_is_inconclusive_not_a_traceback(tmp_path):
    sites, paths = write_fixture_csvs(tmp_path)
    paths[-1].unlink()
    proc, result = run_documented(runbook_command(), sites, paths, "synthetic")
    assert result["status"] == "INCONCLUSIVE" and proc.returncode == EXIT_CODES["INCONCLUSIVE"]
    assert "Traceback" not in proc.stderr


@pytest.mark.parametrize("kind", ["synthetic", "earth-engine-export"])
def test_synthetic_fixtures_can_never_be_reported_as_a_screen_pass_when_labelled(tmp_path, kind):
    sites, paths = write_fixture_csvs(tmp_path)
    _, result = run_documented(runbook_command(), sites, paths, kind)
    if kind == "synthetic":
        assert result["status"] == "DEVELOPMENT_ONLY"
    else:
        # A synthetic manifest declared as an export is exactly the mislabelling the runbook warns
        # the CLI cannot detect. Record what it does so the limitation is a tested fact, not prose.
        assert result["status"] in ("SCREEN_PASS", "SCREEN_FAIL")
