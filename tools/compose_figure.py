#!/usr/bin/env python3
"""Compose a publication-ready figure from a Google Earth Engine NDVI-change export.

Takes the rendered NDVI-change map you export from `gee/ndvi_change.js` (a PNG,
JPG, or 3-band GeoTIFF) and bakes in a title, a diverging legend, an approximate
scale bar, and the required Copernicus Sentinel-2 attribution — so the result is a
self-contained figure that travels well (e.g. on LinkedIn) without relying on a
caption.

Usage:
    python tools/compose_figure.py \
        --input path/to/gee_export.png \
        --title "Vegetation change around <place>" \
        --years "2019 -> 2025" \
        --region "<region>, Mongolia" \
        --scale 10 \
        --output results/ndvi_change.png

Dependencies: matplotlib, numpy, Pillow.
"""
import argparse

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Rectangle
import numpy as np
from PIL import Image

INK = "#1b2a24"
MUTED = "#5f6b64"
# Diverging BrBG, matching gee/ndvi_change.js (brown = NDVI down, teal = NDVI up).
PALETTE = ["#8c510a", "#d8b365", "#f6e8c3", "#ffffff", "#c7eae5", "#5ab4ac", "#01665e"]


def nice_length(meters: float) -> float:
    """Round a target distance down to a 1/2/5 x 10^k value."""
    if meters <= 0:
        return 1.0
    exp = np.floor(np.log10(meters))
    base = meters / (10 ** exp)
    step = 1 if base < 2 else (2 if base < 5 else 5)
    return step * (10 ** exp)


def fmt_dist(meters: float) -> str:
    return f"{meters/1000:g} km" if meters >= 1000 else f"{meters:g} m"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="GEE-exported NDVI-change image")
    ap.add_argument("--output", default="results/ndvi_change.png")
    ap.add_argument("--title", default="Vegetation change over time")
    ap.add_argument("--years", default="")
    ap.add_argument("--region", default="")
    ap.add_argument("--scale", type=float, default=10.0, help="metres per pixel")
    ap.add_argument("--year-attr", default="", help="acquisition years for attribution, e.g. '2019, 2025'")
    args = ap.parse_args()

    img = np.asarray(Image.open(args.input).convert("RGB"))
    h, w = img.shape[:2]

    fig_w = 10.0
    fig_h = fig_w * (h / w) + 2.1           # extra room for title + footer
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=150)
    fig.patch.set_facecolor("white")

    # --- map ---
    ax = fig.add_axes([0.03, 0.12, 0.94, 0.74])
    ax.imshow(img)
    ax.set_xlim(0, w); ax.set_ylim(h, 0)
    ax.axis("off")

    # --- title / subtitle ---
    fig.text(0.03, 0.955, args.title, fontsize=19, fontweight="bold",
             color=INK, ha="left", va="top", family="DejaVu Sans")
    sub = " · ".join(x for x in [args.region, args.years] if x)
    if sub:
        fig.text(0.03, 0.905, sub, fontsize=12, color=MUTED, ha="left", va="top")

    # --- scale bar (approximate; assumes --scale m/px) ---
    target = nice_length(0.22 * w * args.scale)
    bar_px = target / args.scale
    x0, y0 = 0.03 * w, 0.93 * h
    ax.add_patch(Rectangle((x0 - 6, y0 - 22), bar_px + 12, 34,
                           facecolor="white", edgecolor="none", alpha=0.75, zorder=4))
    ax.plot([x0, x0 + bar_px], [y0, y0], color=INK, lw=3, zorder=5)
    ax.text(x0 + bar_px / 2, y0 - 6, fmt_dist(target), ha="center", va="bottom",
            fontsize=10, color=INK, zorder=5)

    # --- diverging legend ---
    cmap = LinearSegmentedColormap.from_list("brbg", PALETTE)
    cax = fig.add_axes([0.30, 0.055, 0.40, 0.022])
    grad = np.linspace(0, 1, 256).reshape(1, -1)
    cax.imshow(grad, aspect="auto", cmap=cmap)
    cax.set_xticks([]); cax.set_yticks([])
    for s in cax.spines.values():
        s.set_edgecolor("#cfd6d1")
    cax.text(-0.02, 0.5, "candidate\ndisturbance", transform=cax.transAxes,
             ha="right", va="center", fontsize=8.3, color=MUTED)
    cax.text(1.02, 0.5, "greening /\nrecovery", transform=cax.transAxes,
             ha="left", va="center", fontsize=8.3, color=MUTED)
    cax.set_title("candidate surface disturbance", fontsize=9, color=INK, pad=4)

    # --- attribution (required for Sentinel-2 redistribution) ---
    yrs = f" ({args.year_attr})" if args.year_attr else ""
    fig.text(0.03, 0.012,
             f"Contains modified Copernicus Sentinel-2 data{yrs} · processed in Google Earth Engine",
             fontsize=8, color=MUTED, ha="left", va="bottom")

    fig.savefig(args.output, facecolor="white", bbox_inches="tight", pad_inches=0.15)
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
