#!/usr/bin/env python3
"""Build the keyed SBS 96-well plate holder for PandaDeck."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import math
from pathlib import Path

import FreeCAD
import MeshPart
import Part


MM = 1.0


@dataclass(frozen=True)
class HolderSpec:
    # SBS/ANSI 96-well plate footprint. The holder orients plate length along
    # deck Y to match CubOS panda_deck.yaml's A1 -> A2 direction.
    plate_width_x: float = 85.48 * MM
    plate_length_y: float = 127.76 * MM
    plate_height: float = 14.35 * MM

    # Snug clearance for nominal SBS plates. This is total clearance across the
    # pocket, not per-side clearance.
    plate_clearance: float = 0.20 * MM

    # Body dimensions: spans a 4x4 PandaDeck insert block, with the imported
    # keys landing at the four block corners.
    outer_x: float = 100.0 * MM
    outer_y: float = 164.0 * MM
    body_height: float = 6.0 * MM
    seat_height: float = 3.0 * MM

    # Open center keeps the underside of the wells clear and reduces material.
    window_x: float = 69.0 * MM
    window_y: float = 110.0 * MM

    # Straight registration band above the seat. This band, not the upper
    # funnel, controls the final seated plate location.
    registration_wall_height: float = 1.50 * MM

    # Lead-in taper above the registration band. This is the total top-opening
    # increase over the seated pocket, so each side gains half this amount.
    lead_in_clearance: float = 1.7320508075688776 * MM

    # Optional centered access openings on the left/right long rails so a
    # gripper can reach the plate's long sides.
    long_side_grip_gap_y: float = 70.0 * MM

    # Deck insert grid spacing from PandaDeck.step.
    key_span_x: float = 75.0 * MM  # 3 intervals at 25 mm = 4 columns.
    key_span_y: float = 135.0 * MM  # 3 intervals at 45 mm = 4 rows.

    @property
    def pocket_x(self) -> float:
        return self.plate_width_x + self.plate_clearance

    @property
    def pocket_y(self) -> float:
        return self.plate_length_y + self.plate_clearance

    @property
    def lead_in_x(self) -> float:
        return self.pocket_x + self.lead_in_clearance

    @property
    def lead_in_y(self) -> float:
        return self.pocket_y + self.lead_in_clearance

    @property
    def registration_top_z(self) -> float:
        return self.seat_height + self.registration_wall_height

    @property
    def funnel_height(self) -> float:
        return self.body_height - self.registration_top_z

    @property
    def plate_surface_height(self) -> float:
        return self.seat_height + self.plate_height


def box_centered_xy(x_size: float, y_size: float, z_size: float, z_min: float) -> Part.Shape:
    return Part.makeBox(
        x_size,
        y_size,
        z_size,
        FreeCAD.Vector(-x_size / 2.0, -y_size / 2.0, z_min),
    )


def centered_rectangle_wire(x_size: float, y_size: float, z: float) -> Part.Wire:
    x = x_size / 2.0
    y = y_size / 2.0
    return Part.Wire(
        Part.makePolygon(
            [
                FreeCAD.Vector(-x, -y, z),
                FreeCAD.Vector(x, -y, z),
                FreeCAD.Vector(x, y, z),
                FreeCAD.Vector(-x, y, z),
                FreeCAD.Vector(-x, -y, z),
            ]
        )
    )


def validate_spec(spec: HolderSpec) -> None:
    if spec.plate_clearance <= 0.0:
        raise ValueError("plate_clearance must be positive")
    if spec.registration_wall_height <= 0.0:
        raise ValueError("registration_wall_height must be positive")
    if spec.registration_top_z >= spec.body_height:
        raise ValueError("registration_wall_height must leave room for the lead-in funnel")
    if spec.lead_in_clearance < 0.0:
        raise ValueError("lead_in_clearance must not be negative")


def pocket_cut(spec: HolderSpec) -> Part.Shape:
    bottom = centered_rectangle_wire(spec.pocket_x, spec.pocket_y, spec.seat_height)
    registration_top = centered_rectangle_wire(
        spec.pocket_x,
        spec.pocket_y,
        spec.registration_top_z,
    )
    top = centered_rectangle_wire(spec.lead_in_x, spec.lead_in_y, spec.body_height)
    return Part.makeLoft([bottom, registration_top, top], True, True, False)


def build_body(spec: HolderSpec) -> Part.Shape:
    validate_spec(spec)
    body = box_centered_xy(spec.outer_x, spec.outer_y, spec.body_height, 0.0)

    # Two-stage plate pocket: a straight lower band registers the seated plate;
    # the upper funnel guides lower-precision robotic placement into that band.
    body = body.cut(pocket_cut(spec))

    # Through-window under the well field, leaving a ledge around the skirt.
    window = box_centered_xy(spec.window_x, spec.window_y, spec.body_height + 2.0, -1.0)
    body = body.cut(window)

    if spec.long_side_grip_gap_y > 0.0:
        if spec.long_side_grip_gap_y >= spec.outer_y:
            raise ValueError("long_side_grip_gap_y must be smaller than outer_y")
        gap_reach_x = (spec.outer_x - spec.window_x) / 2.0 + 2.0
        # Keep the lower registration band continuous even where the upper rim
        # has gripper access gaps, otherwise the seated plate can yaw.
        gap_z_min = spec.registration_top_z
        for side in (-1.0, 1.0):
            gap = Part.makeBox(
                gap_reach_x,
                spec.long_side_grip_gap_y,
                spec.body_height - gap_z_min + 2.0,
                FreeCAD.Vector(
                    side * spec.outer_x / 2.0 - (gap_reach_x if side > 0 else 0.0),
                    -spec.long_side_grip_gap_y / 2.0,
                    gap_z_min,
                ),
            )
            body = body.cut(gap)
    return body.removeSplitter()


def import_key(path: Path) -> Part.Shape:
    key = Part.Shape()
    key.read(str(path))
    if key.isNull() or not key.isValid():
        raise ValueError(f"Invalid key STEP: {path}")
    return key


def placed_key(key: Part.Shape, x: float, y: float) -> Part.Shape:
    clone = key.copy()
    clone.translate(FreeCAD.Vector(x, y, 0.0))
    return clone


def build_holder(key_step: Path, spec: HolderSpec) -> Part.Shape:
    body = build_body(spec)
    key = import_key(key_step)
    keys = []
    for x in (-spec.key_span_x / 2.0, spec.key_span_x / 2.0):
        for y in (-spec.key_span_y / 2.0, spec.key_span_y / 2.0):
            keys.append(placed_key(key, x, y))
    holder = body.multiFuse(keys).removeSplitter()
    if holder.isNull() or not holder.isValid() or not holder.isClosed():
        raise ValueError(
            "Generated holder is not a valid closed solid "
            f"(valid={holder.isValid()}, closed={holder.isClosed()}, null={holder.isNull()})"
        )
    if len(holder.Solids) != 1:
        raise ValueError(f"Expected one fused solid, got {len(holder.Solids)}")
    return holder


def make_plate_dummy(spec: HolderSpec) -> Part.Shape:
    # QA-only envelope for visual clearance checks; not exported as part of the
    # printable holder.
    return box_centered_xy(
        spec.plate_width_x,
        spec.plate_length_y,
        spec.plate_height,
        spec.seat_height,
    )


def make_deck_fit_assembly(holder: Part.Shape, deck_step: Path, spec: HolderSpec) -> Part.Shape:
    deck = Part.Shape()
    deck.read(str(deck_step))

    # Slot block: X centers 52.5..127.5, Y centers -45..-180 on the deck.
    # Local holder key centers are +/-37.5 and +/-67.5, so this origin aligns
    # the four keyed feet to a concrete 4x4 insert block.
    holder_on_deck = holder.copy()
    holder_on_deck.translate(FreeCAD.Vector(90.0, -112.5, 10.0))

    plate = make_plate_dummy(spec)
    plate.translate(FreeCAD.Vector(90.0, -112.5, 10.0))
    return Part.makeCompound([deck, holder_on_deck, plate])


def orient_top_face_down_for_print(shape: Part.Shape) -> Part.Shape:
    """Return a copy with the holder top face on the build plate.

    The design STEP keeps +Z as the installed holder's upward direction. For
    printing, the top/pocket face should be generated first on the build plate
    while the deck keys are printed last. A 180 degree X rotation flips the
    holder, then a Z translation puts the new low face at Z=0.
    """
    printable = shape.copy()
    printable.rotate(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(1, 0, 0), 180)
    printable.translate(FreeCAD.Vector(0, 0, -printable.BoundBox.ZMin))
    return printable


def export_stl(shape: Part.Shape, path: Path, *, orient_for_print: bool = False) -> None:
    export_shape = orient_top_face_down_for_print(shape) if orient_for_print else shape
    mesh = MeshPart.meshFromShape(
        Shape=export_shape,
        LinearDeflection=0.08,
        AngularDeflection=0.20,
        Relative=False,
    )
    mesh.write(str(path))


def lead_in_clearance_for_angle(
    body_height: float,
    seat_height: float,
    registration_wall_height: float,
    angle_degrees: float,
) -> float:
    ramp_height = body_height - (seat_height + registration_wall_height)
    if ramp_height <= 0:
        raise ValueError("registration_wall_height must leave room for the lead-in funnel")
    if angle_degrees <= 0.0 or angle_degrees >= 90.0:
        raise ValueError("lead-in angle must be between 0 and 90 degrees")

    # Angle is measured from the horizontal seat plane in cross-section. Return
    # the total opening increase; per-side offset is half this value.
    per_side_offset = ramp_height / math.tan(math.radians(angle_degrees))
    return 2.0 * per_side_offset


def default_lead_in_clearance(
    body_height: float,
    seat_height: float,
    registration_wall_height: float,
) -> float:
    return lead_in_clearance_for_angle(
        body_height,
        seat_height,
        registration_wall_height,
        60.0,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--key-step",
        type=Path,
        default=Path("labware/ursa_vial_holder/9VialHolder-key.step"),
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
        default="PandaSBSWellplateHolder",
        help="Output file stem for STEP/STL/QA assembly.",
    )
    parser.add_argument(
        "--body-height",
        type=float,
        default=6.0,
        help="Printed holder body height in mm, excluding keys below the body.",
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
        help=(
            "Total top-opening increase over the seated pocket in mm. "
            "Overrides --lead-in-angle-deg when set."
        ),
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
    args.out_dir.mkdir(parents=True, exist_ok=True)

    holder = build_holder(args.key_step, spec)
    step_path = args.out_dir / f"{args.name}.step"
    stl_path = args.out_dir / f"{args.name}.stl"
    assembly_step_path = args.out_dir / f"{args.name}-deck-fit.step"

    holder.exportStep(str(step_path))
    export_stl(holder, stl_path, orient_for_print=True)
    assembly = make_deck_fit_assembly(holder, args.deck_step, spec)
    assembly.exportStep(str(assembly_step_path))

    bb = holder.BoundBox
    print(f"wrote: {step_path}")
    print(f"wrote: {stl_path}")
    stl_shape = orient_top_face_down_for_print(holder)
    stl_bb = stl_shape.BoundBox
    print(
        "stl_print_orientation_bbox_mm: "
        f"min=({stl_bb.XMin:.3f}, {stl_bb.YMin:.3f}, {stl_bb.ZMin:.3f}) "
        f"max=({stl_bb.XMax:.3f}, {stl_bb.YMax:.3f}, {stl_bb.ZMax:.3f}) "
        f"span=({stl_bb.XLength:.3f}, {stl_bb.YLength:.3f}, {stl_bb.ZLength:.3f})"
    )
    print("stl_print_orientation: top/pocket face on build plate, keys printed last")
    print(f"wrote: {assembly_step_path}")
    print(
        "holder_bbox_mm: "
        f"min=({bb.XMin:.3f}, {bb.YMin:.3f}, {bb.ZMin:.3f}) "
        f"max=({bb.XMax:.3f}, {bb.YMax:.3f}, {bb.ZMax:.3f}) "
        f"span=({bb.XLength:.3f}, {bb.YLength:.3f}, {bb.ZLength:.3f})"
    )
    print(f"holder_volume_mm3: {holder.Volume:.3f}")
    print(f"plate_pocket_mm: {spec.pocket_x:.3f} x {spec.pocket_y:.3f}")
    print(f"lead_in_opening_mm: {spec.lead_in_x:.3f} x {spec.lead_in_y:.3f}")
    print(f"plate_clearance_total_mm: {spec.plate_clearance:.3f}")
    print(f"holder_body_height_mm: {spec.body_height:.3f}")
    print(f"seat_height_mm: {spec.seat_height:.3f}")
    print(f"registration_wall_height_mm: {spec.registration_wall_height:.3f}")
    print(f"registration_top_z_mm: {spec.registration_top_z:.3f}")
    print(f"funnel_height_mm: {spec.funnel_height:.3f}")
    print(f"lead_in_horizontal_offset_per_side_mm: {spec.lead_in_clearance / 2.0:.3f}")
    print(f"lead_in_angle_from_horizontal_deg: {args.lead_in_angle_deg:.3f}")
    print(f"long_side_grip_gap_y_mm: {spec.long_side_grip_gap_y:.3f}")
    print(f"plate_surface_height_mm: {spec.plate_surface_height:.3f}")
    print(f"key_centers_mm: x=+/-{spec.key_span_x / 2:.3f}, y=+/-{spec.key_span_y / 2:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
