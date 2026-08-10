# Results

Exported figures and analysis outputs.

The main [`README`](../README.md) displays **`ndvi_change.png`** — currently a
placeholder. Replace it with your first real export and the project README
updates automatically (same filename, no edits needed).

## Workflow

1. **Generate** — run [`../gee/ndvi_change.js`](../gee/ndvi_change.js) in the
   [Earth Engine Code Editor](https://code.earthengine.google.com/) over your
   area of interest. Either click the printed thumbnail URL or run the Drive
   export to get the rendered NDVI-change image.
2. **Compose** — turn the raw export into a self-contained figure with a title,
   legend, scale bar, and the required attribution:

   ```bash
   python tools/compose_figure.py \
     --input path/to/gee_export.png \
     --title "Vegetation change around <place>" \
     --years "2019 -> 2025" \
     --region "<region>, Mongolia" \
     --scale 10 \
     --year-attr "2019, 2025" \
     --output results/ndvi_change.png
   ```
3. **Commit** the figure.

## Caption template

> **NDVI change, `<region>`, `<year1>`→`<year2>` (July).** Brown marks vegetation
> loss / surface disturbance (evidence of active use); green marks regrowth
> (evidence of abandonment). Linear features are candidate route corridors.
> Contains modified Copernicus Sentinel-2 data, processed in Google Earth Engine.

## Attribution & licensing

Sentinel-2 imagery is free and openly licensed (Copernicus). When you publish a
figure, include: *"Contains modified Copernicus Sentinel-2 data (`<years>`),
processed in Google Earth Engine."* `compose_figure.py` bakes this line in.

Do **not** commit raw imagery exports here — GeoTIFFs and archives are ignored by
`.gitignore` to keep the repo light. Keep only finished figures.
