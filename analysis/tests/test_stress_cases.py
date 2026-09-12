"""Pin the extractor's OBSERVED behaviour on the fixed stress cases (CR-R03).

These are not aspirations. Each assertion states what extract_candidates does today on a
deterministic construction, including the misses and the false candidate, so that a change to
the extractor shows up here as a named behaviour change rather than a silent shift in a demo
figure. results/extractor_stress_cases.json is the committed record the CLI regenerates.
"""
import json, math
from pathlib import Path
import numpy as np
import pytest
from catanroads import extract_candidates
from catanroads import stress_cases as SC

ROOT = Path(__file__).resolve().parents[2]
RECORD = json.loads((ROOT / "results/extractor_stress_cases.json").read_text())


@pytest.fixture(scope="module")
def live():
    return SC.run_all()


def test_committed_record_matches_live_run(live):
    for name, s in live.items():
        rec = RECORD["cases"][name]
        assert s["n_candidates"] == rec["n_candidates"], name
        assert s["n_false_candidates"] == rec["n_false_candidates"], name
        for k in ("pixel_recall", "pixel_precision"):
            if rec[k] is None:
                assert s[k] is None, (name, k)
            else:
                assert math.isclose(s[k], rec[k], abs_tol=1e-9), (name, k)


# ── where it detects ────────────────────────────────────────────────────────────────────
def test_detects_wide_low_snr_gradient_and_hairpin_corridors(live):
    for name in ("wide_corridor", "low_snr", "gradient_background", "tight_curve"):
        assert live[name]["detected"] and live[name]["pixel_recall"] >= 0.99, name


def test_faint_corridor_is_detected_but_fragmented(live):
    s = live["faint_corridor"]
    assert s["detected"] and s["pixel_recall"] > 0.9
    assert s["n_candidates"] == 7, "one corridor reported as seven pieces"


def test_speckle_alone_produces_no_candidates():
    for n in (400, 1500, 4000):
        d, _ = SC.case_speckle_only(n_specks=n)
        assert extract_candidates(d) == [], n


# ── where it misses ─────────────────────────────────────────────────────────────────────
def test_crossing_corridors_are_both_lost(live):
    # Two full corridors, zero candidates: the union component's elongation is below min_elongation.
    assert live["crossing"]["n_candidates"] == 0 and live["crossing"]["pixel_recall"] == 0.0
    d, _ = SC.case_crossing()
    assert len(extract_candidates(d, min_elongation=1.5)) == 1, "lowering min_elongation recovers ONE component for two roads"


def test_dashed_corridor_is_lost_entirely(live):
    assert live["short_segments"]["n_candidates"] == 0


def test_detection_cliff_sits_at_disturb_thresh():
    sweep = {r["strength"]: r for r in SC.faint_strength_sweep()}
    assert sweep[1.3]["pixel_recall"] == 1.0
    assert sweep[1.05]["pixel_recall"] < 0.5
    assert sweep[0.9]["n_candidates"] == 0


# ── where it fabricates ─────────────────────────────────────────────────────────────────
def test_linear_non_road_feature_is_a_confident_false_candidate(live):
    s = live["linear_confound_riverbank"]
    assert s["n_candidates"] == 1 and s["n_false_candidates"] == 1 and s["pixel_precision"] == 0.0
    d, _ = SC.case_linear_confound_riverbank()
    c = extract_candidates(d)[0]
    assert c["length_px"] > 250 and c["mean_disturbance"] > 2, "ranked like a strong road"


def test_gradient_background_adds_small_false_candidates(live):
    s = live["gradient_background"]
    assert s["n_false_candidates"] == 2 and s["pixel_precision"] > 0.95


# ── where it misrepresents ──────────────────────────────────────────────────────────────
def test_hairpin_is_summarised_as_one_straight_segment():
    d, _ = SC.case_tight_curve(); c = extract_candidates(d)[0]
    (x0, y0), (x1, y1) = c["endpoints_px"]
    assert abs(y0 - y1) < 1.0, "endpoints lie on one horizontal line; the doubling-back is invisible"
    assert c["width_px"] > 20, "the hairpin's height is reported as candidate WIDTH"


def test_low_snr_inflates_reported_width():
    d, _ = SC.case_low_snr(); c = extract_candidates(d)[0]
    assert c["width_px"] > 40, "a 3-px corridor reported as > 40 px wide under 3x noise"
