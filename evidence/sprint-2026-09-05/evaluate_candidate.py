"""Exercise the installed intake CLI on predeclared synthetic consumer inputs."""
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
candidate = json.loads((HERE / "candidate.json").read_text())
for name, digest in candidate["files"].items():
    assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, "Candidate drift: " + name
spec = importlib.util.spec_from_file_location("intake_fixtures", ROOT / "analysis/tests/test_phase1_gate.py")
fixtures = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixtures)
results = []
for number, expected_exit, expected_status in [
    (1, 3, "DEVELOPMENT_ONLY"), (2, 2, "INCONCLUSIVE"), (3, 2, "INCONCLUSIVE"),
    (4, 2, "INCONCLUSIVE"), (5, 2, "INCONCLUSIVE"), (6, 3, "DEVELOPMENT_ONLY"),
]:
    manifest, rows = fixtures.fixture()
    for row in rows:
        row["large_component_fraction"] = 0 if row["site_id"] in ("negative-01", "dev-03-gobi") else 0.0001
    if number == 2:
        manifest = json.loads((ROOT / "config/sites.geojson").read_text())
    if number == 3:
        rows[0]["coverage_fraction"] = "NaN"
    if number == 6:
        rows[1]["large_component_fraction"] = 0
    with tempfile.TemporaryDirectory(prefix="catan-consumer-") as tmp:
        folder = Path(tmp)
        sites, metrics = folder / "sites.json", folder / "metrics.csv"
        sites.write_text(json.dumps(manifest))
        fields = list(rows[0])
        with metrics.open("w", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(fields)
            for index, row in enumerate(rows):
                values = [row[key] for key in fields]
                if index == 0 and number == 4:
                    values = values[:-1]
                if index == 0 and number == 5:
                    values += ["unexpected"]
                writer.writerow(values)
        command = [sys.executable, "-m", "catanroads.phase1_gate", "--sites", str(sites),
                   "--metrics", str(metrics), "--evidence-kind", "synthetic"]
        run = subprocess.run(command, cwd=folder, capture_output=True, text=True)
        output = json.loads(run.stdout)
        match = run.returncode == expected_exit and output["status"] == expected_status
        if number == 6:
            match = match and output["arithmetic_result"] == "SCREEN_FAIL"
        results.append(dict(id=number, expected_exit=expected_exit, expected_status=expected_status,
            observed_exit=run.returncode, matches=match, output=output, stderr=run.stderr))
print(json.dumps(dict(kind="installed CLI; developer synthetic fixtures only",
    denominator=len(results), all_matched=all(r["matches"] for r in results), cases=results), indent=2))
raise SystemExit(0 if all(r["matches"] for r in results) else 1)
