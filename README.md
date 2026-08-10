# Catan Roads

**A network-conditioned method for finding persistent surface-disturbance
corridors that may represent unmapped informal roads in Mongolia — from
multi-year satellite imagery.**

![License: MIT](https://img.shields.io/badge/license-MIT-2d6a4f)
![Status: early development](https://img.shields.io/badge/status-early%20development-2d6a4f)
![Platform: Google Earth Engine](https://img.shields.io/badge/platform-Google%20Earth%20Engine-2d6a4f)
![Imagery: Sentinel-2](https://img.shields.io/badge/imagery-Sentinel--2-2d6a4f)

![Method overview](assets/method.png)

## Overview

Mongolia has one of the lowest paved-road densities on Earth, and most rural
travel happens on **informal tracks that no map records** — routes that appear,
widen, braid into parallel ruts, and revegetate when disused. Detecting them
matters for logistics and transport planning, disaster response, connectivity
mapping for herder communities, and monitoring the footprint of off-road travel.

Desire Lines is **not** an NDVI road classifier. A single vehicle track is
~2.5–3 m wide and therefore **sub-pixel** at Sentinel-2's 10 m resolution. So the
method targets what a medium-resolution sensor *can* honestly resolve:
**persistent, corridor-scale surface disturbance** — braided corridors, clusters
of parallel tracks, and network-scale change — and produces a **prioritized list
of candidate corridors for confirmation in higher-resolution imagery**. Coarse,
free, and scalable detection feeding targeted high-res confirmation is the design
intent, not a fallback.

> A *desire line* is a path worn into the land by use rather than design.

## Approach

| Stage | What it does |
| --- | --- |
| **Temporal evidence** | Build two multi-year, same-season baselines (e.g. 2019–2021 vs 2024–2026) rather than two single dates, suppressing year-to-year noise. |
| **Composite disturbance** | Fuse vegetation loss (ΔNDVI) and exposed-surface gain (ΔBSI) into one disturbance score — treated as *related* channels, not two independent measurements. |
| **Local-control normalization** | Express disturbance as an anomaly against its own neighbourhood (focal mean/σ), so regional and seasonal drift cancel and only locally anomalous change survives. |
| **Persistence** | Weight by the fraction of recent years the disturbance holds, separating durable change from single-year artifacts. |
| **Network conditioning** | Score proximity to OpenStreetMap intersections/endpoints — as a *ranking signal*, keeping both all-area and network-seeded candidate sets for ablation. |
| **Corridor grouping** | Merge parallel ruts into functional route corridors (the Mongolia-specific target). |

The full technical design, decisions, and the developed Phase 0–4 plan are in
**[`docs/design.md`](docs/design.md)**. Study sites (development, holdout,
confound, and a road-free negative control) are declared in
**[`config/sites.geojson`](config/sites.geojson)**.

## Distinctive decisions

- **Corridors, not single tracks.** Sub-pixel tracks are out of scope for direct
  detection; braided/parallel-track corridors are the resolvable, distinctive target.
- **Soft-handle land cover.** Only permanent water is hard-masked; cropland and
  built-up areas are evaluation *strata* and confounds, not erased (which would
  delete real road branches near settlements).
- **OSM as a score, not a gate.** Requiring every candidate to touch a mapped node
  would discard genuinely disconnected routes, so seeding is a rank, and
  seeded-vs-unseeded detection is itself a planned result.
- **Negative controls first.** The signal must be quantitatively weaker at a
  road-free control site than at development sites *before* any line extraction —
  this is the project's falsification gate.

## Tech stack

- **Imagery:** Copernicus **Sentinel-2** SR (~10 m, 2017–present); optional
  Sentinel-1 backscatter later
- **Compute:** **Google Earth Engine** (free for noncommercial use)
- **Reference network & GIS:** **OpenStreetMap**, **QGIS**
- **Raster→vector (planned):** Python — `rasterio`, `scikit-image`, `shapely`,
  `geopandas`, `networkx`

## Status & roadmap

Early development. **In place:** the reframed problem, the composite-disturbance
Earth Engine pipeline (`gee/ndvi_change.js`), the site manifest, and the figure
workflow. **Next (Phase 1 gate):** produce a real Mongolia disturbance figure and
confirm it survives the negative control. **Then:** raster→vector candidate
extraction, network conditioning, and corridor-level evaluation. See
[`docs/design.md`](docs/design.md).

## Results

![Candidate surface-disturbance map over an area of interest](results/ndvi_change.png)

*Example output. Brown marks locally anomalous, persistent surface disturbance
(a candidate corridor for high-resolution confirmation); teal marks
greening/recovery. No active/abandoned claim is made without validation. Contains
modified Copernicus Sentinel-2 data, processed in Google Earth Engine.*

> The figure above is a placeholder. Generate one with the workflow below; see
> [`results/`](results/) for the one-command compose step.

## Reproduce the analysis

1. Open the [Earth Engine Code Editor](https://code.earthengine.google.com/) and
   paste [`gee/ndvi_change.js`](gee/ndvi_change.js).
2. Set the AOI (right-click Google Maps → paste `lat, lon`), or use a site from
   [`config/sites.geojson`](config/sites.geojson).
3. Run. Read the **run manifest** printed to the console (scene counts per year),
   then inspect the *candidate disturbance (local-normalized z)* layer for
   persistent, linear/corridor-scale features. Export the float raster (for QGIS +
   OSM overlay) or the thumbnail (for `tools/compose_figure.py`).

## Methodological rigor

- **Same season, multi-year baselines** — or the signal measures grass, not roads.
- **Local-control normalization is implemented in code**, not just asserted:
  disturbance is an anomaly against each pixel's surroundings.
- **Related indices, honestly named** — ΔNDVI and ΔBSI share bands, so their
  agreement is a *composite* score, not two independent confirmations.
- **Resolution honesty as a result** — the project reports the minimum corridor
  width/braiding Sentinel-2 can resolve, a defensible finding regardless of outcome.
- The output is *candidate disturbance/recovery evidence* — **not** traffic
  volume, vehicle counts, or a validated active/abandoned label.

## License

[MIT](LICENSE)
