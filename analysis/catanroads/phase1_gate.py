"""Fail-closed intake for the registered Phase-1 disturbance screen, not road validation."""
from __future__ import annotations

import argparse
import csv
from datetime import date
import hashlib
import json
import math
from pathlib import Path

DEVELOPMENT = ("dev-01-braided", "dev-02-recovering", "dev-03-gobi")
NEGATIVE = "negative-01"
REQUIRED = set(DEVELOPMENT) | {NEGATIVE}
CONFIG = dict(early_years="2018-2021", recent_years="2023-2026",
    analysis_crs="EPSG:3857", analysis_scale_m=10, control_inner_m=200,
    control_outer_m=800, min_control_pixels=500, month=7, z_min=1.0,
    yearly_effect_min=0.02, persistence_min=2/3, min_valid_recent_years=2,
    min_component_pixels=50)


def _number(value):
    if isinstance(value, bool):
        raise ValueError("boolean is not a measurement")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("non-finite number")
    return number


def _dated(value):
    return isinstance(value, str) and date.fromisoformat(value).isoformat() == value


def evaluate_gate(manifest, rows, *, evidence_kind="synthetic"):
    """Validate supplied metadata; source authenticity still needs human review.

    SCREEN_PASS is only the fixed large-component screen. Explicitly synthetic
    fixtures can exercise its arithmetic but never receive that evidence label.
    """
    errors = []
    values = {}
    try:
        if evidence_kind not in ("synthetic", "earth-engine-export"):
            raise ValueError("unknown evidence kind")
        if manifest["_phase1_gate"]["preregistered_on"] != "2026-08-23":
            raise ValueError("unknown registered design version")
        sites = {}
        for feature in manifest["features"]:
            props = feature["properties"]
            key = props["id"]
            if key in sites:
                raise ValueError("duplicate manifest site: " + key)
            sites[key] = props
        if not REQUIRED <= sites.keys():
            raise ValueError("missing registered sites")
        by_id = {}
        for row in rows:
            key = row["site_id"]
            if key in by_id:
                raise ValueError("duplicate metric row: " + key)
            by_id[key] = row
        if by_id.keys() != REQUIRED:
            raise ValueError("require exactly three development rows and negative-01; no holdout rows")
        for key in sorted(REQUIRED):
            site, row = sites[key], by_id[key]
            expected_stratum = "negative_control" if key == NEGATIVE else "development"
            if site["stratum"] != expected_stratum or row["stratum"] != expected_stratum:
                raise ValueError(key + ": stratum mismatch")
            if site["verified"] is not True or not _dated(site["ref_imagery_date"]):
                raise ValueError(key + ": site unverified or reference date invalid")
            provenance = site["provenance"]
            if not isinstance(provenance, str) or not provenance.strip() or provenance.strip().lower() in ("tbd", "unknown", "starting guess"):
                raise ValueError(key + ": missing reference provenance")
            if str(row["gate_eligible"]).lower() not in ("true", "1"):
                raise ValueError(key + ": export marked ineligible")
            for field, source in (("reference_imagery_date", "ref_imagery_date"), ("site_provenance", "provenance")):
                if row[field] != site[source]:
                    raise ValueError(key + ": reference metadata mismatch: " + field)
            for field in ("center_lat", "center_lon", "half_km"):
                if _number(row[field]) != _number(site[field]):
                    raise ValueError(key + ": AOI mismatch: " + field)
            if not (-90 <= _number(site["center_lat"]) <= 90
                    and -180 <= _number(site["center_lon"]) <= 180
                    and _number(site["half_km"]) > 0):
                raise ValueError(key + ": invalid geographic bounds or radius")
            for field, expected in CONFIG.items():
                actual = row[field]
                match = actual == expected if isinstance(expected, str) else math.isclose(
                    _number(actual), expected, rel_tol=1e-12, abs_tol=1e-12)
                if not match:
                    raise ValueError(key + ": frozen setting mismatch: " + field)
            value = _number(row["large_component_fraction"])
            coverage = _number(row["coverage_fraction"])
            if not 0 <= value <= 1 or not 0.90 <= coverage <= 1:
                raise ValueError(key + ": invalid fraction or coverage below 0.90")
            # Same denominator: components are a subset of analyzable pixels.
            # Four ULPs covers representation roundoff, not measurement tolerance.
            if value > coverage + 4 * math.ulp(coverage):
                raise ValueError(key + ": component fraction exceeds analyzable coverage")
            values[key] = value
    except (KeyError, TypeError, ValueError, AttributeError, OverflowError) as exc:
        errors.append(str(exc))
    if errors:
        return dict(status="INCONCLUSIVE", errors=errors, scope="Metadata intake only; no road verdict")
    threshold = max(2.0 * values[NEGATIVE], 0.0001)
    passing = [key for key in DEVELOPMENT if values[key] >= threshold]
    arithmetic = "SCREEN_PASS" if len(passing) >= 2 else "SCREEN_FAIL"
    return dict(status="DEVELOPMENT_ONLY" if evidence_kind == "synthetic" else arithmetic,
        arithmetic_result=arithmetic, threshold=threshold, passing_development_sites=passing,
        denominator=3, errors=[], evidence_kind=evidence_kind,
        scope="Large-component positive-disturbance screen only; not road precision, recovery detection or source authentication")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sites", type=Path, required=True)
    parser.add_argument("--metrics", type=Path, nargs="+", required=True,
                        help="One combined CSV or four one-row Earth Engine CSVs")
    parser.add_argument("--evidence-kind", choices=("synthetic", "earth-engine-export"), required=True)
    args = parser.parse_args()
    try:
        manifest = json.loads(args.sites.read_text())
        rows = []
        for path in args.metrics:
            with path.open(newline="", encoding="utf-8-sig") as stream:
                reader = csv.DictReader(stream)
                headers = reader.fieldnames or []
                if not headers or any(not h.strip() for h in headers) or len(set(headers)) != len(headers):
                    raise ValueError("CSV headers missing, empty or duplicated")
                incoming = list(reader)
                if any(None in row or None in row.values() for row in incoming):
                    raise ValueError("CSV row width does not match header")
                rows.extend(incoming)
        result = evaluate_gate(manifest, rows, evidence_kind=args.evidence_kind)
        result["input_sha256"] = {
            str(path): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in [args.sites, *args.metrics]
        }
    except (OSError, ValueError, csv.Error) as exc:
        result = dict(status="INCONCLUSIVE", errors=[str(exc)])
    print(json.dumps(result, indent=2, allow_nan=False))
    return {"SCREEN_PASS": 0, "SCREEN_FAIL": 1, "INCONCLUSIVE": 2, "DEVELOPMENT_ONLY": 3}[result["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
