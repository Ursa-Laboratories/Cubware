#!/usr/bin/env python3
"""Render visual QA previews for the Panda SBS wellplate holder."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import FreeCAD

Path("/private/tmp/cubware-matplotlib").mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", "/private/tmp/cubware-matplotlib")
os.environ.setdefault("XDG_CACHE_HOME", "/private/tmp/cubware-cache")

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import Part

from build_panda_sbs_wellplate_holder import (
    HolderSpec,
    lead_in_clearance_for_angle,
    make_plate_dummy,
    orient_top_face_down_for_print,
)


def tessellate(shape: Part.Shape, tolerance: float = 0.35) -> tuple[np.ndarray, np.ndarray]:
    vertices, faces = shape.tessellate(tolerance)
    return np.asarray([(v.x, v.y, v.z) for v in vertices], dtype=float), np.asarray(faces, dtype=int)


def add_mesh(ax, shape: Part.Shape, color: str, alpha: float, tolerance: float = 0.35) -> None:
    vertices, faces = tessellate(shape, tolerance=tolerance)
    tris = vertices[faces]
    collection = Poly3DCollection(tris, linewidths=0.08, alpha=alpha)
    collection.set_facecolor(color)
    collection.set_edgecolor((0.08, 0.08, 0.08, min(alpha + 0.15, 1.0)))
    ax.add_collection3d(collection)


def set_axes_equal(ax, bounds: tuple[float, float, float, float, float, float]) -> None:
    xmin, xmax, ymin, ymax, zmin, zmax = bounds
    xmid = (xmin + xmax) / 2
    ymid = (ymin + ymax) / 2
    zmid = (zmin + zmax) / 2
    radius = max(xmax - xmin, ymax - ymin, zmax - zmin) / 2
    ax.set_xlim(xmid - radius, xmid + radius)
    ax.set_ylim(ymid - radius, ymid + radius)
    ax.set_zlim(zmid - radius, zmid + radius)


def render_holder(holder: Part.Shape, spec: HolderSpec, out_path: Path) -> None:
    fig = plt.figure(figsize=(12, 9))

    ax = fig.add_subplot(2, 2, 1, projection="3d")
    add_mesh(ax, holder, "#4f8cc9", 0.92, tolerance=0.20)
    set_axes_equal(ax, (-55, 55, -88, 88, -12, 18))
    ax.view_init(elev=28, azim=-50)
    ax.set_title("one-piece keyed holder")
    ax.set_xlabel("X mm")
    ax.set_ylabel("Y mm")
    ax.set_zlabel("Z mm")

    top = fig.add_subplot(2, 2, 2)
    top.set_title("top view: SBS pocket and open well-field window")
    top.add_patch(Rectangle((-spec.outer_x / 2, -spec.outer_y / 2), spec.outer_x, spec.outer_y, facecolor="#4f8cc9", alpha=0.28, edgecolor="#1f4f79"))
    top.add_patch(Rectangle((-spec.lead_in_x / 2, -spec.lead_in_y / 2), spec.lead_in_x, spec.lead_in_y, facecolor="white", alpha=0.55, edgecolor="#2e6f9e", linestyle="-."))
    top.add_patch(Rectangle((-spec.pocket_x / 2, -spec.pocket_y / 2), spec.pocket_x, spec.pocket_y, facecolor="white", alpha=0.95, edgecolor="#1f4f79", linestyle="--"))
    top.add_patch(Rectangle((-spec.window_x / 2, -spec.window_y / 2), spec.window_x, spec.window_y, facecolor="#f7f7f7", alpha=1.0, edgecolor="#777"))
    if spec.long_side_grip_gap_y > 0.0:
        gap_x = (spec.outer_x - spec.window_x) / 2.0 + 2.0
        for x_min in (-spec.outer_x / 2, spec.outer_x / 2 - gap_x):
            top.add_patch(
                Rectangle(
                    (x_min, -spec.long_side_grip_gap_y / 2),
                    gap_x,
                    spec.long_side_grip_gap_y,
                    facecolor="white",
                    alpha=1.0,
                    edgecolor="#9a6500",
                    linewidth=1.0,
                )
            )
    top.add_patch(Rectangle((-spec.plate_width_x / 2, -spec.plate_length_y / 2), spec.plate_width_x, spec.plate_length_y, facecolor="#d59a2b", alpha=0.22, edgecolor="#9a6500"))
    for x in (-spec.key_span_x / 2, spec.key_span_x / 2):
        for y in (-spec.key_span_y / 2, spec.key_span_y / 2):
            top.add_patch(Rectangle((x - 5.304, y - 12.804), 10.607, 25.607, facecolor="#2f5d3a", alpha=0.65, edgecolor="#18351f"))
    top.set_aspect("equal")
    top.set_xlim(-58, 58)
    top.set_ylim(-90, 90)
    top.set_xlabel("X mm")
    top.set_ylabel("Y mm")

    xz = fig.add_subplot(2, 2, 3)
    xz.set_title("X/Z section envelope")
    if spec.long_side_grip_gap_y > 0.0:
        side_base = (spec.outer_x - spec.window_x) / 2.0
        xz.add_patch(Rectangle((-spec.outer_x / 2, 0), side_base, spec.registration_top_z, facecolor="#4f8cc9", alpha=0.28, edgecolor="#1f4f79"))
        xz.add_patch(Rectangle((spec.outer_x / 2 - side_base, 0), side_base, spec.registration_top_z, facecolor="#4f8cc9", alpha=0.28, edgecolor="#1f4f79"))
        xz.plot(
            [
                -spec.pocket_x / 2,
                -spec.pocket_x / 2,
                spec.pocket_x / 2,
                spec.pocket_x / 2,
            ],
            [
                spec.seat_height,
                spec.registration_top_z,
                spec.registration_top_z,
                spec.seat_height,
            ],
            color="#1f4f79",
            linestyle="--",
        )
    else:
        xz.add_patch(Rectangle((-spec.outer_x / 2, 0), spec.outer_x, spec.body_height, facecolor="#4f8cc9", alpha=0.28, edgecolor="#1f4f79"))
        xz.plot(
            [
                -spec.pocket_x / 2,
                -spec.pocket_x / 2,
                -spec.lead_in_x / 2,
                spec.lead_in_x / 2,
                spec.pocket_x / 2,
                spec.pocket_x / 2,
                -spec.pocket_x / 2,
            ],
            [
                spec.seat_height,
                spec.registration_top_z,
                spec.body_height,
                spec.body_height,
                spec.registration_top_z,
                spec.seat_height,
                spec.seat_height,
            ],
            color="#1f4f79",
            linestyle="--",
        )
    xz.add_patch(Rectangle((-spec.plate_width_x / 2, spec.seat_height), spec.plate_width_x, spec.plate_height, facecolor="#d59a2b", alpha=0.22, edgecolor="#9a6500"))
    xz.hlines(0, -60, 60, colors="#333", linewidth=0.8)
    xz.set_aspect("equal")
    xz.set_xlim(-58, 58)
    xz.set_ylim(-12, 22)
    xz.set_xlabel("X mm")
    xz.set_ylabel("Z mm")

    yz = fig.add_subplot(2, 2, 4)
    yz.set_title("Y/Z section envelope")
    yz.add_patch(Rectangle((-spec.outer_y / 2, 0), spec.outer_y, spec.body_height, facecolor="#4f8cc9", alpha=0.28, edgecolor="#1f4f79"))
    yz.plot(
        [
            -spec.pocket_y / 2,
            -spec.pocket_y / 2,
            -spec.lead_in_y / 2,
            spec.lead_in_y / 2,
            spec.pocket_y / 2,
            spec.pocket_y / 2,
            -spec.pocket_y / 2,
        ],
        [
            spec.seat_height,
            spec.registration_top_z,
            spec.body_height,
            spec.body_height,
            spec.registration_top_z,
            spec.seat_height,
            spec.seat_height,
        ],
        color="#1f4f79",
        linestyle="--",
    )
    yz.add_patch(Rectangle((-spec.plate_length_y / 2, spec.seat_height), spec.plate_length_y, spec.plate_height, facecolor="#d59a2b", alpha=0.22, edgecolor="#9a6500"))
    yz.hlines(0, -90, 90, colors="#333", linewidth=0.8)
    yz.set_aspect("equal")
    yz.set_xlim(-90, 90)
    yz.set_ylim(-12, 22)
    yz.set_xlabel("Y mm")
    yz.set_ylabel("Z mm")

    fig.tight_layout()
    fig.savefig(out_path, dpi=180)
    plt.close(fig)


def render_deck_fit(holder: Part.Shape, deck: Part.Shape, spec: HolderSpec, out_path: Path) -> None:
    holder_on_deck = holder.copy()
    holder_on_deck.translate(FreeCAD.Vector(90.0, -112.5, 10.0))
    plate = make_plate_dummy(spec)
    plate.translate(FreeCAD.Vector(90.0, -112.5, 10.0))

    fig = plt.figure(figsize=(14, 9))
    ax = fig.add_subplot(1, 2, 1)
    ax.set_title("PandaDeck top view: holder on 4x4 insert block")
    ax.add_patch(Rectangle((0, -490), 480, 490, facecolor="#d9d9d9", edgecolor="#777", alpha=0.40))
    x_centers = [27.5 + 25.0 * index for index in range(18)]
    y_centers = [-45.0 - 45.0 * index for index in range(10)]
    for x in x_centers:
        for y in y_centers:
            ax.add_patch(Circle((x, y - 7.5), 5.0, facecolor="none", edgecolor="#aaa", linewidth=0.35))
            ax.add_patch(Circle((x, y + 7.5), 5.0, facecolor="none", edgecolor="#aaa", linewidth=0.35))
    ax.add_patch(Rectangle((40.0, -194.5), spec.outer_x, spec.outer_y, facecolor="#4f8cc9", edgecolor="#1f4f79", alpha=0.42))
    if spec.long_side_grip_gap_y > 0.0:
        gap_x = (spec.outer_x - spec.window_x) / 2.0 + 2.0
        for x_min in (40.0, 140.0 - gap_x):
            ax.add_patch(
                Rectangle(
                    (x_min, -112.5 - spec.long_side_grip_gap_y / 2),
                    gap_x,
                    spec.long_side_grip_gap_y,
                    facecolor="#ffffff",
                    edgecolor="#9a6500",
                    alpha=0.90,
                    linewidth=1.0,
                )
            )
    ax.add_patch(Rectangle((90.0 - spec.plate_width_x / 2, -112.5 - spec.plate_length_y / 2), spec.plate_width_x, spec.plate_length_y, facecolor="#d59a2b", edgecolor="#9a6500", alpha=0.28))
    for x in (52.5, 127.5):
        for y in (-180.0, -45.0):
            ax.plot(x, y, marker="x", color="#173f22", markersize=8, markeredgewidth=1.5)
    ax.set_aspect("equal")
    ax.set_xlim(0, 180)
    ax.set_ylim(-220, 0)
    ax.set_xlabel("Deck X mm")
    ax.set_ylabel("Deck Y mm")

    ax3 = fig.add_subplot(1, 2, 2, projection="3d")
    add_mesh(ax3, deck, "#c9c9c9", 0.18, tolerance=1.2)
    add_mesh(ax3, holder_on_deck, "#4f8cc9", 0.86, tolerance=0.35)
    add_mesh(ax3, plate, "#d59a2b", 0.30, tolerance=0.8)
    set_axes_equal(ax3, (0, 180, -220, 0, 0, 35))
    ax3.view_init(elev=26, azim=-62)
    ax3.set_title("deck-fit assembly, including plate envelope")
    ax3.set_xlabel("X mm")
    ax3.set_ylabel("Y mm")
    ax3.set_zlabel("Z mm")

    fig.tight_layout()
    fig.savefig(out_path, dpi=180)
    plt.close(fig)


def render_print_orientation(holder: Part.Shape, out_path: Path) -> None:
    printable = orient_top_face_down_for_print(holder)
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(1, 1, 1, projection="3d")
    add_mesh(ax, printable, "#4f8cc9", 0.90, tolerance=0.25)
    set_axes_equal(ax, (-55, 55, -88, 88, 0, 18))
    ax.view_init(elev=26, azim=-45)
    ax.set_title("STL print orientation: top face first, keys last")
    ax.set_xlabel("X mm")
    ax.set_ylabel("Y mm")
    ax.set_zlabel("Print Z mm")
    fig.tight_layout()
    fig.savefig(out_path, dpi=180)
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--holder-step",
        type=Path,
        default=Path("labware/panda_sbs_wellplate_holder/PandaSBSWellplateHolder.step"),
    )
    parser.add_argument(
        "--deck-step",
        type=Path,
        default=Path("gantry/polycarb/PandaDeck.step"),
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("labware/panda_sbs_wellplate_holder"),
    )
    parser.add_argument(
        "--name",
        default=None,
        help="Output file stem. Defaults to the holder STEP stem.",
    )
    parser.add_argument(
        "--body-height",
        type=float,
        default=6.0,
        help="Printed holder body height in mm for section overlays.",
    )
    parser.add_argument(
        "--plate-clearance",
        type=float,
        default=HolderSpec.plate_clearance,
        help="Total seated-pocket clearance over the SBS footprint in mm.",
    )
    parser.add_argument(
        "--registration-wall-height",
        type=float,
        default=HolderSpec.registration_wall_height,
        help="Straight lower wall height above the 3 mm seat before the lead-in funnel starts.",
    )
    parser.add_argument(
        "--lead-in-clearance",
        type=float,
        default=None,
        help="Total top-opening increase over the seated pocket in mm.",
    )
    parser.add_argument(
        "--lead-in-angle-deg",
        type=float,
        default=60.0,
        help="Lead-in angle measured from the horizontal seat plane.",
    )
    parser.add_argument(
        "--long-side-grip-gap-y",
        type=float,
        default=HolderSpec.long_side_grip_gap_y,
        help="Centered access-gap length in mm on each long side rail.",
    )
    args = parser.parse_args()

    holder = Part.Shape()
    holder.read(str(args.holder_step))
    deck = Part.Shape()
    deck.read(str(args.deck_step))

    args.out_dir.mkdir(parents=True, exist_ok=True)
    output_stem = args.name or args.holder_step.stem
    base_spec = HolderSpec(
        body_height=args.body_height,
        plate_clearance=args.plate_clearance,
        registration_wall_height=args.registration_wall_height,
    )
    lead_in_clearance = (
        args.lead_in_clearance
        if args.lead_in_clearance is not None
        else lead_in_clearance_for_angle(
            base_spec.body_height,
            base_spec.seat_height,
            base_spec.registration_wall_height,
            args.lead_in_angle_deg,
        )
    )
    spec = HolderSpec(
        body_height=args.body_height,
        plate_clearance=args.plate_clearance,
        registration_wall_height=args.registration_wall_height,
        lead_in_clearance=lead_in_clearance,
        long_side_grip_gap_y=args.long_side_grip_gap_y,
    )
    holder_png = args.out_dir / f"{output_stem}.png"
    fit_png = args.out_dir / f"{output_stem}-deck-fit.png"
    print_png = args.out_dir / f"{output_stem}-print-orientation.png"
    render_holder(holder, spec, holder_png)
    render_deck_fit(holder, deck, spec, fit_png)
    render_print_orientation(holder, print_png)
    print(f"wrote: {holder_png}")
    print(f"wrote: {fit_png}")
    print(f"wrote: {print_png}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
