#!/usr/bin/env python3
"""Measure the deterministic layout rules of a generated slide image.

Usage:
    python3 validate_slide.py slide.png [--json] [options]

Checks (see references/visual-presentation-framework.md, Sections 3 and 9):
    dimensions, aspect ratio, left gutter width / color / continuity,
    top-right and bottom-right empty zones, title-row clearance,
    background in unobstructed edge areas, and an advisory title position.

This script only measures. It does not fix anything, and it cannot check text
accuracy, numbers, prohibited elements, clipping, or composition. Those still
need visual inspection.

Exit code: 0 = no FAIL, 1 = at least one FAIL, 2 = the image could not be read.
Requires Python 3 and Pillow.
"""

import argparse
import json
import sys

try:
    from PIL import Image, ImageChops
except ImportError:  # pragma: no cover
    print("ERROR: Pillow is required (pip install pillow).", file=sys.stderr)
    sys.exit(2)

# Targets from the framework. Keep in sync with Section 3.
GUTTER_RGB = (0x1E, 0xA7, 0xF2)
TOP_RIGHT = (0.80, 0.00, 1.00, 0.16)      # x0, y0, x1, y1 as fractions
BOTTOM_RIGHT = (0.80, 0.88, 1.00, 1.00)
TITLE_ROW = (0.78, 0.00, 1.00, 0.16)      # nothing may reach here (title ends before X=78%)
TITLE_SEARCH = (0.03, 0.00, 1.00, 0.16)   # where the title block is looked for
EDGE_STRIPS = {                            # unobstructed background areas
    "top strip": (0.03, 0.000, 1.00, 0.015),
    "bottom strip": (0.03, 0.985, 1.00, 1.000),
    "right strip": (0.98, 0.000, 1.00, 1.000),
}


def box_px(frac, w, h):
    x0, y0, x1, y1 = frac
    return (int(round(x0 * w)), int(round(y0 * h)), int(round(x1 * w)), int(round(y1 * h)))


def channel_mask(band, lo, hi):
    """255 where lo <= value <= hi, else 0."""
    return band.point(lambda v: 255 if lo <= v <= hi else 0)


def and_masks(masks):
    out = masks[0]
    for m in masks[1:]:
        out = ImageChops.multiply(out, m)
    return out


def fraction_matching(region, ranges):
    """Fraction of pixels whose R, G, B fall inside the given (lo, hi) ranges."""
    r, g, b = region.split()
    mask = and_masks([channel_mask(r, *ranges[0]), channel_mask(g, *ranges[1]), channel_mask(b, *ranges[2])])
    total = region.size[0] * region.size[1]
    return mask.histogram()[255] / total if total else 0.0


def near_white_fraction(img, frac_box, white_min):
    region = img.crop(box_px(frac_box, *img.size))
    return fraction_matching(region, [(white_min, 255)] * 3)


def ink_bbox(img, frac_box, white_min):
    """Bounding box (px, absolute) of non-white pixels inside frac_box, or None."""
    x0, y0, x1, y1 = box_px(frac_box, *img.size)
    region = img.crop((x0, y0, x1, y1))
    r, g, b = region.split()
    white = and_masks([channel_mask(r, white_min, 255), channel_mask(g, white_min, 255), channel_mask(b, white_min, 255)])
    ink = ImageChops.invert(white)
    bb = ink.getbbox()
    if bb is None:
        return None
    return (bb[0] + x0, bb[1] + y0, bb[2] + x0, bb[3] + y0)


def measure_gutter(img, tol, min_col_fraction=0.5):
    """Measure the gutter as the run of columns from X=0 that are mostly gutter-colored.

    Returns (width_px, min_fraction_inside_gutter, mean_rgb_at_left_edge).
    A column counts toward the width when at least min_col_fraction of its rows
    match the gutter color, so an interrupted gutter is still measured and then
    fails the continuity check instead of being reported as missing.
    """
    w, h = img.size
    ranges = [(max(0, c - tol), min(255, c + tol)) for c in GUTTER_RGB]
    scan = max(2, int(w * 0.06))
    fractions = []
    for x in range(scan):
        col = img.crop((x, 0, x + 1, h))
        fractions.append(fraction_matching(col, ranges))
    width = 0
    for f in fractions:
        if f >= min_col_fraction:
            width += 1
        else:
            break
    min_frac = min(fractions[:width]) if width else 0.0
    edge = img.crop((0, 0, 1, h)).resize((1, 1), Image.BOX).getpixel((0, 0))
    return width, min_frac, edge


def run(path, opts):
    try:
        img = Image.open(path).convert("RGB")
    except Exception as exc:  # unreadable or not an image
        print(f"ERROR: cannot read image: {exc}", file=sys.stderr)
        sys.exit(2)

    w, h = img.size
    results = []

    def add(name, status, detail):
        results.append({"check": name, "status": status, "detail": detail})

    # Dimensions and aspect ratio
    add("dimensions", "PASS" if w >= 2560 and h >= 1440 else "WARN",
        f"{w}x{h} px" + ("" if w >= 2560 and h >= 1440 else " (default is 2560x1440 when supported)"))
    ratio_err = abs((w / h) / (16 / 9) - 1)
    add("aspect_ratio", "PASS" if ratio_err <= opts.ratio_tol else "FAIL",
        f"{w / h:.4f} vs 1.7778 (off by {ratio_err * 100:.2f}%, accepted {opts.ratio_tol * 100:.1f}%)")

    # Gutter
    width_px, min_frac, edge = measure_gutter(img, opts.color_tol)
    width_pct = width_px / w * 100
    if width_px == 0:
        add("gutter_width", "FAIL", f"no gutter-colored columns start at the left edge (average color of column X=0: RGB{edge})")
        add("gutter_color", "FAIL", f"left edge RGB{edge} is not within +/-{opts.color_tol} of #1EA7F2")
        add("gutter_continuity", "FAIL", "no gutter found at the left edge")
    else:
        ok_w = opts.gutter_min <= width_pct <= opts.gutter_max
        add("gutter_width", "PASS" if ok_w else "FAIL",
            f"{width_pct:.2f}% ({width_px} px), accepted {opts.gutter_min}% to {opts.gutter_max}%")
        add("gutter_color", "PASS", f"matches #1EA7F2 within +/-{opts.color_tol} per channel")
        add("gutter_continuity", "PASS" if min_frac >= 0.98 else "FAIL",
            f"{min_frac * 100:.1f}% of rows are gutter-colored in the weakest gutter column (accepted 98%+)")

    # Reserved zones and title-row clearance
    for name, frac_box, label in (
        ("top_right_zone_empty", TOP_RIGHT, "X 80-100%, Y 0-16%"),
        ("bottom_right_zone_empty", BOTTOM_RIGHT, "X 80-100%, Y 88-100%"),
        ("title_row_clearance", TITLE_ROW, "X 78-100%, Y 0-16%"),
    ):
        frac = near_white_fraction(img, frac_box, opts.white_min)
        add(name, "PASS" if frac >= opts.zone_clean else "FAIL",
            f"{frac * 100:.2f}% near-white in {label} (accepted {opts.zone_clean * 100:.1f}%+)")

    # Background in unobstructed areas. Start right of the measured gutter, so a wrong
    # gutter width is reported once (above) and not again as a background problem.
    x0 = max(0.03, width_px / w + 0.005)
    bad = []
    for label, frac_box in EDGE_STRIPS.items():
        frac_box = (max(frac_box[0], x0),) + tuple(frac_box[1:]) if frac_box[0] < 0.5 else frac_box
        frac = near_white_fraction(img, frac_box, opts.white_min)
        if frac < opts.zone_clean:
            bad.append(f"{label} {frac * 100:.1f}%")
    add("background_edges", "FAIL" if bad else "PASS",
        ("not plain white: " + ", ".join(bad)) if bad else "top, bottom, and right edge strips are plain white")

    # Advisory title position (heuristic: first ink in the top band)
    bb = ink_bbox(img, (x0,) + TITLE_SEARCH[1:], opts.white_min)
    if bb is None:
        add("title_position", "WARN", "no text-like content found in the top band (X 3-100%, Y 0-16%); check the title visually")
    else:
        left, top, right = bb[0] / w * 100, bb[1] / h * 100, bb[2] / w * 100
        problems = []
        if not 2 <= top <= 6:
            problems.append(f"top at Y={top:.1f}% (target 4%, accepted 2-6%)")
        if not 4 <= left <= 6:
            problems.append(f"left at X={left:.1f}% (target 5%, accepted 4-6%)")
        if right > 79:
            problems.append(f"right edge at X={right:.1f}% (must end before 78%, accepted up to 79%)")
        add("title_position", "WARN" if problems else "PASS",
            ("; ".join(problems) + ". Heuristic only, confirm visually.") if problems
            else f"first content top Y={top:.1f}%, left X={left:.1f}%, right X={right:.1f}% (heuristic)")

    return results


def main():
    p = argparse.ArgumentParser(description="Measure deterministic layout rules of a slide image.")
    p.add_argument("image", help="path to the slide image (PNG or JPEG)")
    p.add_argument("--json", action="store_true", help="print results as JSON")
    p.add_argument("--white-min", type=int, default=245, help="channel value that counts as white (default 245)")
    p.add_argument("--zone-clean", type=float, default=0.995, help="required near-white fraction of empty zones (default 0.995)")
    p.add_argument("--color-tol", type=int, default=30, help="per-channel tolerance for the gutter color (default 30)")
    p.add_argument("--gutter-min", type=float, default=1.2, help="minimum gutter width in %% of width (default 1.2)")
    p.add_argument("--gutter-max", type=float, default=1.8, help="maximum gutter width in %% of width (default 1.8)")
    p.add_argument("--ratio-tol", type=float, default=0.01, help="aspect ratio tolerance as a fraction (default 0.01)")
    opts = p.parse_args()

    results = run(opts.image, opts)
    counts = {s: sum(1 for r in results if r["status"] == s) for s in ("PASS", "FAIL", "WARN")}
    note = ("These checks cover layout geometry only. Text accuracy, numbers, prohibited elements, "
            "clipping, and composition still need visual inspection.")

    if opts.json:
        print(json.dumps({"image": opts.image, "results": results, "summary": counts, "note": note}, indent=2))
    else:
        for r in results:
            print(f"[{r['status']}] {r['check']}: {r['detail']}")
        print(f"\nAutomated checks: {counts['PASS']} passed, {counts['FAIL']} failed, {counts['WARN']} warnings.")
        print(note)

    sys.exit(1 if counts["FAIL"] else 0)


if __name__ == "__main__":
    main()
