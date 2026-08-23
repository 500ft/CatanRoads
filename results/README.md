# Results

Exported figures and analysis outputs.

The main [`README`](../README.md) displays **`ndvi_change.png`** — a legacy
full-field-rendering placeholder. Do not replace it with a claimed result until
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
