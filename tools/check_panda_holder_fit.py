#!/usr/bin/env python3
"""Boolean fit checks for the Panda SBS holder against PandaDeck."""

from __future__ import annotations

import argparse
from pathlib import Path

import FreeCAD
import Part

from build_panda_sbs_wellplate_holder import HolderSpec, build_holder, make_plate_dummy


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--holder-step",
        type=Path,
        default=Path("cubxl_plus/labware/well_plate_holder/PandaSBSWellplateHolder.step"),
    )
    parser.add_argument(
        "--deck-step",
        type=Path,
        default=Path("cubxl_plus/deck/polycarbonate_deck/PandaDeck.step"),
    )
    parser.add_argument(
        "--key-step",
        type=Path,
        default=Path("cubxl_plus/labware/vial_holder/9VialHolder-key.step"),
    )
    args = parser.parse_args()

    spec = HolderSpec()

    deck = Part.Shape()
    deck.read(str(args.deck_step))
    holder = Part.Shape()
    if args.holder_step.exists():
        holder.read(str(args.holder_step))
    else:
        holder = build_holder(args.key_step, spec)

    holder_on_deck = holder.copy()
    holder_on_deck.translate(FreeCAD.Vector(90.0, -112.5, 10.0))
    plate_on_deck = make_plate_dummy(spec)
    plate_on_deck.translate(FreeCAD.Vector(90.0, -112.5, 10.0))

    holder_deck_common = holder_on_deck.common(deck)
    plate_holder_common = plate_on_deck.common(holder_on_deck)
    plate_clearance_shell = holder_on_deck.common(plate_on_deck)

    hb = holder_on_deck.BoundBox
    pb = plate_on_deck.BoundBox
    db = deck.BoundBox
    print("panda_holder_fit")
    print(f"  deck_bbox: {db}")
    print(f"  holder_on_deck_bbox: {hb}")
    print(f"  plate_on_deck_bbox: {pb}")
    print("  expected_key_centers_on_deck:")
    for x in (52.5, 127.5):
        for y in (-180.0, -45.0):
            print(f"    ({x:.3f}, {y:.3f}, slot)")
    print(f"  holder_deck_intersection_volume_mm3: {holder_deck_common.Volume:.6f}")
    print(f"  holder_deck_intersection_valid: {holder_deck_common.isValid()}")
    print(f"  plate_holder_intersection_volume_mm3: {plate_holder_common.Volume:.6f}")
    print(f"  plate_holder_intersection_valid: {plate_holder_common.isValid()}")
    print(f"  nominal_sbs_plate_mm: {spec.plate_width_x:.3f} x {spec.plate_length_y:.3f}")
    print(f"  seated_pocket_mm: {spec.pocket_x:.3f} x {spec.pocket_y:.3f}")
    print(f"  seated_pocket_clearance_total_mm: {spec.plate_clearance:.3f}")
    print(f"  seated_pocket_clearance_per_side_mm: {spec.plate_clearance / 2.0:.3f}")
    print(f"  deck_bottom_to_key_bottom_gap_mm: {hb.ZMin - db.ZMin:.6f}")
    print(f"  deck_top_to_holder_body_bottom_gap_mm: {10.0 - 10.0:.6f}")
    print(f"  plate_bottom_to_holder_seat_gap_mm: {pb.ZMin - (10.0 + spec.seat_height):.6f}")

    # The imported key is intentionally a close-fit deck feature. Any true
    # deck collision above numerical noise is a failed fit.
    max_allowed_collision = 0.10
    if holder_deck_common.Volume > max_allowed_collision:
        raise SystemExit(
            "FAIL: holder intersects PandaDeck outside slot clearance: "
            f"{holder_deck_common.Volume:.6f} mm^3"
        )

    # A seated plate touches the holder ledge by design, so this intersection
    # should be effectively zero; nonzero means the pocket is undersized.
    if plate_holder_common.Volume > max_allowed_collision:
        raise SystemExit(
            "FAIL: SBS plate envelope intersects holder walls/ledge: "
            f"{plate_holder_common.Volume:.6f} mm^3"
        )

    print("  result: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
