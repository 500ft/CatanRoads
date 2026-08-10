# Desire Lines

*Detecting active and abandoned informal route corridors in Mongolia from
multi-year satellite imagery.*

A **desire line** is a path worn into the land by use rather than design. In
Mongolia's open steppe and desert, most travel happens on informal tracks that
no map records — and those tracks are constantly being born, widening, braiding
into parallel ruts, and quietly greening over when people stop driving them.

This project seeds from **known mapped road intersections**, searches outward
for **unmapped branches**, traces them, and uses **year-over-year change** in
vegetation, track width, and surface disturbance to estimate whether a route is
**active or abandoned** — with special treatment of the *braided* parallel
tracks that are characteristic of Mongolian off-road travel.

> Status: exploratory, built for fun. This repo is an on-ramp and a design
> sketch, not a finished pipeline. See [`docs/design.md`](docs/design.md) for
> the full concept and the honest scope boundaries.

## The idea in one picture

```
mapped intersection ──▶ search a radius around it
                        │
                        ├─ find linear features not in the reference map
                        ├─ trace each branch outward (graph growth)
                        └─ group braided parallel tracks into ONE corridor
                                     │
                        compare the corridor across years (same season):
                            NDVI ↑  = vegetation regrowth   → likely abandoned
                            NDVI ↓  = surface disturbance    → likely active
```

## Getting started (the fun 20%)

The most satisfying first result needs no pipeline — just look at vegetation
change over a few years on a region you know.

1. Open the [Google Earth Engine Code Editor](https://code.earthengine.google.com/)
   (free account required).
2. Paste [`gee/ndvi_change.js`](gee/ndvi_change.js).
3. Edit the `aoi` rectangle to a rural area you care about and pick two years
   in the **same month** (season matters — see below).
4. Run it. Brown = vegetation lost (disturbance / active use); green = vegetation
   regrown (possible abandonment). Look for the *linear* features — those are
   your tracks.

To overlay the mapped road network, pull [OpenStreetMap](https://www.openstreetmap.org)
roads for the area (via [Geofabrik](https://download.geofabrik.de/asia/mongolia.html)
or the Overpass API) and view them in [QGIS](https://qgis.org) alongside the
exported NDVI-change raster.

## Data

- **Imagery:** Sentinel-2 Surface Reflectance (free, ~10 m, 2017–present) via
  Google Earth Engine.
- **Seed road graph:** OpenStreetMap or an authorized Mongolian GIS layer —
  *not* a commercial map provider, for licensing and reproducibility.

## What this can and cannot claim

- ✅ *Evidence of increasing, stable, decreasing, or absent recent use* of a
  track, from imagery.
- ❌ *Number of vehicles* using a road. Annual imagery does not measure traffic
  volume, and abandoned surface scars can persist for years.

Vegetation change alone is confounded by drought, grazing, fire, and rainfall,
so any real classification must compare a track against its **surrounding
control area** and match imagery by season.

## Roadmap

This repo intentionally starts small. The fuller research design — node
filtering, branch/trail scoring, corridor modeling, a reference-vehicle
envelope, quantitative activity thresholds, and ground truth — lives in
[`docs/design.md`](docs/design.md) as a vision, not a promise.

## License

[MIT](LICENSE)
