"""Synthetic intake fixtures; these do not establish any Mongolia result."""
from copy import deepcopy
import json
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[2]


def fixture():
    manifest = json.loads((ROOT / "config/sites.geojson").read_text())
    rows = []
    for feature in manifest["features"]:
        p = feature["properties"]
        p.update(verified=True, ref_imagery_date="2025-07-15",
                 provenance="SYNTHETIC test reference; not inspected imagery")
        if p["stratum"] not in ("development", "negative_control"):
            continue
        rows.append(dict(site_id=p["id"], stratum=p["stratum"], gate_eligible="true",
            reference_imagery_date=p["ref_imagery_date"], site_provenance=p["provenance"],
            center_lat=p["center_lat"], center_lon=p["center_lon"], half_km=p["half_km"],
            large_component_fraction=0.0002 if p["stratum"] == "development" else 0.0001,
            coverage_fraction=0.90, early_years="2018-2021", recent_years="2023-2026",
            analysis_crs="EPSG:3857", analysis_scale_m=10, control_inner_m=200,
            control_outer_m=800, min_control_pixels=500, month=7, z_min=1.0,
            yearly_effect_min=0.02, persistence_min=2/3, min_valid_recent_years=2,
            min_component_pixels=50))
    return manifest, rows


def evaluate(manifest, rows, kind="earth-engine-export"):
    from catanroads.phase1_gate import evaluate_gate
    return evaluate_gate(manifest, rows, evidence_kind=kind)


def test_unverified_real_manifest_never_passes():
    _, rows = fixture()
    actual = json.loads((ROOT / "config/sites.geojson").read_text())
    assert evaluate(actual, rows)["status"] == "INCONCLUSIVE"


def test_exact_boundary_and_synthetic_label():
    manifest, rows = fixture()
    assert evaluate(manifest, rows)["status"] == "SCREEN_PASS"
    assert evaluate(manifest, rows, "synthetic")["status"] == "DEVELOPMENT_ONLY"
    rows[0]["large_component_fraction"] = 0
    assert evaluate(manifest, rows)["status"] == "SCREEN_PASS"
    rows[1]["large_component_fraction"] = 0
    assert evaluate(manifest, rows)["status"] == "SCREEN_FAIL"


@pytest.mark.parametrize("key,value", [
    ("coverage_fraction", 0.89999), ("coverage_fraction", float("nan")),
    ("large_component_fraction", float("inf")), ("large_component_fraction", -1),
    ("large_component_fraction", 1.01), ("large_component_fraction", True),
    ("reference_imagery_date", "TBD"), ("site_provenance", ""),
    ("gate_eligible", "false"), ("persistence_min", 0.5),
    ("min_component_pixels", 49), ("center_lon", 0), ("month", 8),
    ("analysis_crs", "EPSG:4326"), ("recent_years", "2024-2026"),
])
def test_ineligible_or_mismatched_rows_rejected(key, value):
    manifest, rows = fixture()
    rows[0][key] = value
    assert evaluate(manifest, rows)["status"] == "INCONCLUSIVE"

@pytest.mark.parametrize("mutation", ["component_exceeds_coverage", "invalid_aoi"])
def test_reviewer_reproduced_consistency_holes(mutation):
    manifest, rows = fixture()
    if mutation == "component_exceeds_coverage":
        rows[0]["large_component_fraction"] = 1.0
    else:
        props = manifest["features"][0]["properties"]
        for key, value in dict(center_lat=100, center_lon=200, half_km=-1).items():
            props[key] = value
            rows[0][key] = value
    assert evaluate(manifest, rows)["status"] == "INCONCLUSIVE"


def test_duplicate_csv_headers_cannot_overwrite_low_coverage(tmp_path):
    import csv
    import subprocess
    import sys
    manifest, rows = fixture()
    sites = tmp_path / "sites.json"
    sites.write_text(json.dumps(manifest))
    metrics = tmp_path / "metrics.csv"
    fields = list(rows[0]) + ["coverage_fraction"]
    with metrics.open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(fields)
        for row in rows:
            values = [0.1 if key == "coverage_fraction" else row[key] for key in fields[:-1]]
            writer.writerow(values + [0.9])
    result = subprocess.run([sys.executable, "-m", "catanroads.phase1_gate",
        "--sites", str(sites), "--metrics", str(metrics),
        "--evidence-kind", "earth-engine-export"], capture_output=True, text=True)
    assert result.returncode == 2
    assert json.loads(result.stdout)["status"] == "INCONCLUSIVE"


@pytest.mark.parametrize("mutation", ["duplicate", "missing", "extra", "site_duplicate", "missing_date", "string_verified"])
def test_structure_and_manifest_eligibility(mutation):
    manifest, rows = fixture()
    if mutation == "duplicate":
        rows.append(deepcopy(rows[0]))
    elif mutation == "missing":
        rows.pop()
    elif mutation == "extra":
        rows.append(dict(rows[0], site_id="holdout-01"))
    elif mutation == "site_duplicate":
        manifest["features"].append(deepcopy(manifest["features"][0]))
    elif mutation == "missing_date":
        manifest["features"][0]["properties"]["ref_imagery_date"] = "2025-99-99"
    else:
        manifest["features"][0]["properties"]["verified"] = "true"
    assert evaluate(manifest, rows)["status"] == "INCONCLUSIVE"
