# Results

Exported figures and analysis outputs.

The main [`README`](../README.md) displays the synthetic method demonstration.
**`ndvi_change.png`** remains a legacy full-field-rendering placeholder in this
directory. Do not replace it with a claimed result until
the sites are verified and the pre-registered Phase-1 gate outcome is recorded.

## Workflow

1. **Verify** — freeze dated reference-imagery provenance for all three development
   sites and `negative-01` in [`../config/sites.geojson`](../config/sites.geojson).
2. **Gate** — run [`../gee/ndvi_change.js`](../gee/ndvi_change.js) at those four
   registered sites. Preserve each one-row gate-metrics CSV and apply the exact
   2× large-component-fraction rule in [`../docs/design.md`](../docs/design.md).
3. **Generate** — only after preserving the primary metrics, click the candidate
   thumbnail URL or use the raster Drive export for the figure input.
4. **Compose** — turn the raw export into a self-contained figure with a title,
   legend, scale bar, and the required attribution:

   ```bash
   python tools/compose_figure.py \
     --input path/to/gee_export.png \
     --title "Persistent candidate disturbance around <place>" \
     --years "2018-2021 -> 2023-2026" \
     --region "<region>, Mongolia" \
     --scale 10 \
     --year-attr "2018-2021, 2023-2026" \
     --output results/ndvi_change.png
   ```
5. **Report** the gate result next to the figure, including the negative-control
   metric, development-site metrics, coverage, and whether the registered rule
   passed. A failed gate is a valid result; do not replace it with a sensitivity run.

## Caption template

> **Candidate surface disturbance, `<region>`, `<early-window>` vs `<recent-window>` (July).**
> Brown marks pixels meeting the registered water-safe candidate mask (`z >= 1.0`,
> persistence `>= 2/3`, at least two valid recent years). The registered Phase-1
> gate `<passed/failed>`: `large_component_fraction=<values>` with
> `coverage_fraction=<values>`. No active/abandoned claim is made. Contains modified
> Copernicus Sentinel-2 data, processed in Google Earth Engine.

## Attribution & licensing

Sentinel-2 imagery is free and openly licensed (Copernicus). When you publish a
figure, include: *"Contains modified Copernicus Sentinel-2 data (`<years>`),
processed in Google Earth Engine."* `compose_figure.py` bakes this line in.

Do **not** commit raw imagery exports here — GeoTIFFs and archives are ignored by
`.gitignore` to keep the repo light. Keep only finished figures.


## `extractor_stress_cases.json` — where the extractor detects, misses, or fabricates (CR-R03, 2026-09-12)

Ten fixed synthetic cases (`analysis/catanroads/stress_cases.py`), each with its own truth mask; scored by pixel recall/precision within 2 px and by false-candidate count. Regenerate with `python -m catanroads.stress_cases`; `tests/test_stress_cases.py` pins the observed behaviour. **Synthetic constructions only — nothing here is imagery or a site result.**

| case | candidates | false | pixel recall | verdict |
|---|---:|---:|---:|---|
| demo_reference | 6 | 0 | 0.92 | the favourable demo, for scale |
| wide_corridor (13 px) | 1 | 0 | 1.00 | detects |
| low_snr (3× noise) | 1 | 0 | 1.00 | detects, but reports width 53 px for a 3 px corridor |
| gradient_background | 3 | 2 | 1.00 | detects, plus two small false candidates on the ramp |
| tight_curve (hairpin) | 1 | 0 | 1.00 | detects, **misrepresents**: one straight 128 × 22 px segment |
| faint_corridor (1.15 × thresh) | 7 | 0 | 0.93 | detects, **fragmented** into seven pieces |
| **crossing** | 0 | 0 | 0.00 | **misses both** roads: the union component fails `min_elongation` |
| **short_segments** (9 px dashes) | 0 | 0 | 0.00 | **misses**: every dash is below `min_length_px` |
| **linear_confound_riverbank** | 1 | 1 | — | **fabricates**: a river bank ranks like a strong road (precision 0) |
| speckle_only (up to 4000 specks) | 0 | 0 | — | robust: no false candidates |

Detection cliff: the same corridor at 1.3 / 1.15 / 1.05 / 1.0 / 0.9 × `disturb_thresh` gives recall 1.00 / 0.93 / 0.48 / 0.27 / 0.00. Consequences for the false-positive taxonomy (CR-09): linear non-road features are the failure class the extractor cannot see; junctions and dashed tracks are the miss classes; width and straight-segment summaries are not trustworthy under noise or curvature.
