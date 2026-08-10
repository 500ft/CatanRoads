# Design — Desire Lines

This document is the **research vision** for the project. The repository itself
starts with a much smaller "fun" scope (see the README); this is the fuller
concept that scope could grow toward. It is deliberately honest about where the
hard problems and the unproven assumptions are.

## Refined problem definition

> Detect active informal roads and abandoned tracks in Mongolia by analyzing
> multi-year satellite imagery around known mapped road intersections, then
> tracing previously unmapped branches using changes in vegetation cover,
> apparent road width, surface disturbance, continuity, terrain feasibility, and
> surrounding road-network structure.

The system is not searching the country blindly. It uses mapped intersections as
seed nodes, searches outward within a radius, detects candidate unmapped
branches, follows them, and classifies their activity state over time.

## System logic

### 1. Seed-node generation

Start from a mapped road graph `G_m = (V_m, E_m)` where `V_m` are intersections
and endpoints and `E_m` are segments. Not every point where two polylines touch
is a useful seed — distinguish true intersections, endpoints, forks,
grade-separated crossings, and mapping artifacts, and **prioritize rural forks,
endpoints, and low-degree nodes**.

For each node `v_i`, search a region `Ω_i = { p : |p − v_i| ≤ r_i }`. The radius
should not be a single fixed value; it depends on imagery resolution, node type,
road density, terrain, and expected branch length. Prototype by testing
`r ∈ {250, 500, 1000, 2000} m` and reporting sensitivity.

### 2. Detect unrecorded branches

Within a search region, score a candidate branch by evidence, not appearance
alone:

```
S_branch = w1·C_origin + w2·C_continuity + w3·C_surface
         + w4·C_width  + w5·C_terrain    − w6·C_overlap
```

- `C_origin` — begins at the node
- `C_continuity` — uninterrupted trail strength
- `C_surface` — disturbed soil / reduced vegetation
- `C_width` — consistent with an off-road vehicle track
- `C_terrain` — physically traversable
- `C_overlap` — similarity to already-mapped roads or non-road features (penalty)

### 3. Trail following

Once detected, follow a branch outside the node radius — this is graph growth,
not whole-image segmentation. At each step choose the continuation direction:

```
d* = argmax_d [ w1·I_d + w2·K_d + w3·W_d + w4·T_d − w5·Δθ_d ]
```

(image evidence, continuity, width, terrain feasibility, minus an
abrupt-turn penalty). Terminate when confidence drops, the branch joins a mapped
road, it reaches a destination, disappears, or the terrain becomes implausible.
**Allow branching** — informal tracks split.

## Multi-year activity classification

The temporal comparison is the point. For a segment `e` and year `t`, estimate
`F_{e,t} = [W, V, D, C, B]` (width, vegetation encroachment, surface
disturbance, continuity, neighboring-branch strength) and an activity index:

```
A_{e,t} = αW − βV + γD + δC + εB      ΔA_e = A_{e,late} − A_{e,early}
```

| Classification | Expected pattern |
| --- | --- |
| Active, increasing | wider track, more exposed soil, less vegetation, more branches |
| Active, stable | similar width and disturbance across years |
| Active, decreasing | narrower, more vegetation, weaker continuity |
| Abandoned | progressive vegetation recovery, loss of continuity, no recent disturbance |
| Uncertain | conflicting imagery, poor resolution, seasonal obstruction |

Treat this probabilistically. The defensible output is *evidence of increasing /
stable / decreasing / absent recent use* — **not** vehicle counts.

## The distinctive problem: braided tracks

In open terrain drivers spread into several parallel ruts around potholes, mud,
sand, snow, and steep sections. Several physical tracks `{e_1, …, e_n}` are
functionally **one route corridor** `R_j`. Treating each visible rut as a
separate road makes the graph wrong. Model a corridor with: total width, number
of parallel tracks, average separation, dominant centerline, active-track
fraction, and lateral migration over time. This is the most novel and
Mongolia-specific contribution.

## Reference vehicle

"Any off-road vehicle" is not an engineering requirement. Use a class:

- **Light 4×4 (SUV / utility pickup):** ~1.8–2.1 m wide, needs ~2.5–3.0 m usable
  track, moderate rough-terrain capability, no heavy-truck assumption.

Classify passability as *likely traversable by light 4×4 / uncertain /
unlikely* rather than predicting exact accessibility.

## Research questions

1. Can multi-year imagery + graph-based tracing from mapped rural intersections
   identify previously unmapped active and abandoned corridors in Mongolia?
2. Can vegetation encroachment, corridor width, surface disturbance, and branch
   connectivity distinguish active informal roads from abandoned tracks?
3. Does node-seeded tracing outperform full-area segmentation in precision,
   processing cost, and network connectivity?

## Experiment structure

Compare, and show each subsystem earns its place:

- **A** — full-area segmentation (search all pixels)
- **B** — node-seeded search + branch tracing
- **C** — B + multi-year temporal analysis
- **D** — C + terrain constraints + corridor grouping + graph topology

## Ground truth

Classification cannot be evaluated without independent labels
`Y ∈ {active, abandoned, non-road, uncertain}`. Sources: GPS traces from local
drivers, field visits, recent drone imagery, expert manual interpretation,
repeated very-high-resolution imagery, or transportation records. Without this,
the project produces plausible maps, not defensible results.

## Known confounds and honest limits (fix these before believing any output)

- **Season/sensor mismatch** — compare same-month, comparable-condition imagery;
  otherwise you measure grass, not roads.
- **Vegetation ≠ abandonment** — normalize against local control regions and
  climate; drought/grazing/fire/rain all move NDVI independently.
- **Persistent scars** — abandoned tracks stay visible for years; require
  temporal *recovery* evidence, not just current visibility.
- **Width from pixels is noisy** — report width as an interval with a minimum
  pixel count across the road.
- **Mapping bias** — more mapped branches may just mean better imagery; keep
  observed topology separate from inferred topology.
- **Data source** — use OSM or an authorized GIS layer as the seed graph, not a
  scraped commercial provider.
- **Short archive** — three years (2024–2026) may be noise; use the longest
  consistent archive available, ideally five or more.

## Attribution

Design shaped by an external project-scoping review. Imagery: Copernicus
Sentinel-2. Road graph: OpenStreetMap contributors.
