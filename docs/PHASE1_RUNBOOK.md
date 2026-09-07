# Phase-1 intake and external run boundary

Updated 2026-09-06. No verified Mongolia result or Earth Engine execution is
supplied by this sprint. Site flags remain false.

## Owner inputs, prepared before predictions

Verify the three existing development sites and negative-01 in dated reference
imagery; retain source/scene identifier, acquisition date, licensing/access
reference and feature judgment. Freeze that selection before looking at gate
predictions. Do not inspect holdout-01 for tuning or mix its row into this screen.
Reference verification is not implied by checking a boolean in a file.

Record verification date, reviewer, analysis source commit/diff identity, the
site manifest hash, scene IDs and per-year usable-scene counts with the run.
If scenes/years are missing, retain the exclusion and n_valid/coverage output.
Do not infer full-year coverage from a filename. No credential is stored here.

Mirror approved reference fields into the GEE SITES block, then run
`node tools/validate_phase1.mjs`. Execute the current GEE script in the Code
Editor and explicitly start the four batch CSV exports. Static validation here
does not prove Earth Engine runtime success. Old exports lacking the newly added
AOI/month fields are rejected; regenerate rather than invent missing metadata.

## Required exported columns

Identity: site_id, stratum, gate_eligible, reference_imagery_date, site_provenance,
center_lat, center_lon, half_km. These must match the selected manifest.

Metrics: large_component_fraction and coverage_fraction. Both must be finite
fractions; coverage must be at least 0.90 at every compared site.

Frozen settings: early_years=2018-2021, recent_years=2023-2026, month=7,
analysis_crs=EPSG:3857, analysis_scale_m=10, control_inner_m=200,
control_outer_m=800, min_control_pixels=500, z_min=1, yearly_effect_min=0.02,
persistence_min=2/3, min_valid_recent_years=2, min_component_pixels=50.
Extra Earth Engine CSV columns are ignored; missing required columns are not.

Install the local package:

```sh
python -m pip install -e ./analysis --no-deps
python -m catanroads.phase1_gate --help
```

The following paths are **placeholders for owner-produced files**, not existing
results. Replace each with its downloaded export:

```sh
python -m catanroads.phase1_gate --sites config/sites.geojson \
  --metrics PATH_TO_DEV_01.csv PATH_TO_DEV_02.csv PATH_TO_DEV_03.csv PATH_TO_NEGATIVE_01.csv \
  --evidence-kind earth-engine-export
```

Exit codes: 0 SCREEN_PASS, 1 SCREEN_FAIL, 2 INCONCLUSIVE (ineligible/invalid/missing),
3 DEVELOPMENT_ONLY (explicit synthetic fixtures). A screen pass means at least
two of the three development metrics meet max(2 × negative-01, 0.0001).
It establishes neither road identity nor precision/recall. Input hashes establish
byte identity, not source authenticity; the evidence-kind declaration is not
independently verified by this CLI.

## Sign and scope

The registered positive-disturbance mask is not a recovery detector. Keep
dev-02-recovering in the original screen and report the mismatch honestly; do not
replace it or invert its sign after seeing data. Stable tracks may also be
invisible. A signed recovery endpoint is separate future preregistered work.
No network-conditioned end-to-end result exists. Until external inputs arrive,
only software counterexamples may be evaluated and reported.
