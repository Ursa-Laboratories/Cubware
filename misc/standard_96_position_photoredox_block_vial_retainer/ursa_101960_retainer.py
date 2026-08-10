#!/usr/bin/env python3
"""CadQuery model for an open-access 101960 vial anti-lift retainer.

Coordinate system:
    - Origin is centered on the cover footprint in X/Y.
    - X runs along the 12-column vial direction.
    - Y runs along the 8-row vial direction.
    - Z is upward; the rigid retainer underside is Z=0 and bosses extend
      downward to negative Z.

Run:
    python ursa_101960_retainer.py

The source drawing is Analytical Sales 101960_rev6f_PUBLIC.pdf, rev 6F.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Literal

import math

try:
    import cadquery as cq
except ImportError as exc:  # pragma: no cover - convenience for CAD users
    raise SystemExit(
        "CadQuery 2.x is required. Install with `python -m pip install cadquery` "
        "or run in a CadQuery environment."
    ) from exc


Source = Literal[
    "explicit PDF dimension",
    "inferred from scaled PDF geometry",
    "user-chosen design parameter",
]


@dataclass(frozen=True)
class DimensionRecord:
    name: str
    value_mm: float | str
    source: Source
    confidence: str
    note: str = ""


@dataclass(frozen=True)
class RetainerParams:
    # Explicit PDF dimensions.
    footprint_x: float = 127.8
    footprint_y: float = 85.5
    corner_r: float = 5.5
    cols: int = 12
    rows: int = 8
    pitch_x: float = 9.0
    pitch_y: float = 9.0
    vial_od: float = 8.0

    # Retainer design parameters.
    plate_t: float = 2.5
    access_d: float = 6.7
    access_d_min: float = 5.8
    access_d_max: float = 7.2
    access_chamfer: float = 0.3
    exterior_chamfer: float = 0.5
    boss_od: float = 8.3
    boss_height: float = 0.4

    # OEM side clamp screw features. Centers and counterbore diameter come
    # from scaled PDF geometry. Clearance diameter and counterbore depth are
    # editable because the drawing does not label the screw shank.
    mount_x: float = 58.39
    mount_y: float = 18.00
    mount_clearance_d: float = 5.2
    mount_counterbore_d: float = 12.7
    mount_counterbore_depth: float = 1.2

    # 6-32 accessory holes from the lid corners. Positions are inferred
    # confidently; clearance diameter is chosen for printed through-clearance.
    include_accessory_holes: bool = True
    accessory_x: float = 58.39
    accessory_y: float = 37.24
    accessory_clearance_d: float = 3.7

    # Thermocouple hole shown near the upper-right corner.
    include_thermocouple_hole: bool = True
    thermocouple_x: float = 58.39
    thermocouple_y: float = 29.24
    thermocouple_d: float = 3.3

    # Gasket and coupon.
    gasket_t: float = 0.8
    gasket_hole_extra: float = 0.2
    coupon_cols: int = 3
    coupon_rows: int = 4
    coupon_margin: float = 10.0
    coupon_corner_r: float = 4.0
    coupon_clamp_d: float = 4.0

    @property
    def boss_id(self) -> float:
        return self.access_d


PARAMS = RetainerParams()


DIMENSIONS: tuple[DimensionRecord, ...] = (
    DimensionRecord("Overall footprint length", 127.8, "explicit PDF dimension", "high", "5.030 in [127.8 mm]"),
    DimensionRecord("Overall footprint width", 85.5, "explicit PDF dimension", "high", "3.365 in [85.5 mm]"),
    DimensionRecord("Outer corner radius", 5.5, "explicit PDF dimension", "high", "R0.217 in [R5.5 mm]"),
    DimensionRecord("Vial array", "12 x 8 = 96", "explicit PDF dimension", "high", "drawing row/column labels"),
    DimensionRecord("Vial pitch X", 9.0, "explicit PDF dimension", "high", "0.354 in [9.0 mm]"),
    DimensionRecord("Vial pitch Y", 9.0, "explicit PDF dimension", "high", "0.354 in [9.0 mm]"),
    DimensionRecord("Left edge to first vial center", 14.4, "explicit PDF dimension", "high", "0.566 in [14.4 mm]"),
    DimensionRecord("Top edge to first vial center", 11.2, "explicit PDF dimension", "high", "0.443 in [11.2 mm]"),
    DimensionRecord("Holes in lid", 4.0, "explicit PDF dimension", "high", "0.157 in [4.0 mm]"),
    DimensionRecord("Holes in bottom", 6.0, "explicit PDF dimension", "high", "0.236 in [6.0 mm]"),
    DimensionRecord("Thermocouple hole diameter", 3.3, "explicit PDF dimension", "high", "0.130 in [3.3 mm]"),
    DimensionRecord("Height with vials", 46.2, "explicit PDF dimension", "high", "1.820 in [46.2 mm]"),
    DimensionRecord("Section dimension", 6.1, "explicit PDF dimension", "high", "0.241 in [6.1 mm]"),
    DimensionRecord("Section dimension", 5.1, "explicit PDF dimension", "high", "0.202 in [5.1 mm]"),
    DimensionRecord("OEM screw center X", 58.39, "inferred from scaled PDF geometry", "medium-high", "symmetric side clamp screw centers"),
    DimensionRecord("OEM screw center Y", 18.00, "inferred from scaled PDF geometry", "medium-high", "symmetric side clamp screw centers"),
    DimensionRecord("OEM screw head/counterbore diameter", 12.7, "inferred from scaled PDF geometry", "medium", "visible head rings vary about 12.3-12.7 mm"),
    DimensionRecord("OEM screw clearance diameter", 5.2, "user-chosen design parameter", "low", "PDF does not label screw shank"),
    DimensionRecord("OEM screw counterbore depth", 1.2, "user-chosen design parameter", "low", "thin printed cover default"),
    DimensionRecord("Accessory 6-32 hole center X", 58.39, "inferred from scaled PDF geometry", "high", "corner threaded-hole locations"),
    DimensionRecord("Accessory 6-32 hole center Y", 37.24, "inferred from scaled PDF geometry", "high", "corner threaded-hole locations"),
    DimensionRecord("Accessory through-clearance diameter", 3.7, "user-chosen design parameter", "medium", "clearance for #6 / 6-32 fastener"),
    DimensionRecord("Thermocouple hole center X", 58.39, "inferred from scaled PDF geometry", "medium-high", "upper-right thermocouple hole"),
    DimensionRecord("Thermocouple hole center Y", 29.24, "inferred from scaled PDF geometry", "medium-high", "upper-right thermocouple hole"),
    DimensionRecord("Rigid retainer thickness", 2.5, "user-chosen design parameter", "medium", "printable default"),
    DimensionRecord("Access-hole diameter", 6.7, "user-chosen design parameter", "medium", "parameter access_d, valid 5.8-7.2 mm"),
    DimensionRecord("Underside boss OD", 8.3, "user-chosen design parameter", "medium", "gentle vial-lip bearing land"),
    DimensionRecord("Underside boss height", 0.4, "user-chosen design parameter", "medium", "set to 0 to disable"),
    DimensionRecord("Gasket thickness", 0.8, "user-chosen design parameter", "medium", "TPU/silicone default"),
)


def vial_centers(cols: int, rows: int, pitch_x: float, pitch_y: float) -> list[tuple[float, float]]:
    return [
        ((col - (cols - 1) / 2) * pitch_x, ((rows - 1) / 2 - row) * pitch_y)
        for row in range(rows)
        for col in range(cols)
    ]


def mount_centers(p: RetainerParams) -> list[tuple[float, float]]:
    return [(sx * p.mount_x, sy * p.mount_y) for sx in (-1, 1) for sy in (-1, 1)]


def accessory_centers(p: RetainerParams) -> list[tuple[float, float]]:
    return [(sx * p.accessory_x, sy * p.accessory_y) for sx in (-1, 1) for sy in (-1, 1)]


def rounded_plate(length: float, width: float, radius: float, thickness: float) -> cq.Workplane:
    return cq.Workplane("XY").sketch().rect(length, width).vertices().fillet(radius).finalize().extrude(thickness)


def cylinder_solid(diameter: float, z_min: float, z_max: float, x: float, y: float) -> cq.Shape:
    return (
        cq.Workplane("XY")
        .workplane(offset=z_min)
        .circle(diameter / 2)
        .extrude(z_max - z_min)
        .translate((x, y, 0))
        .val()
    )


def compound(shapes: Iterable[cq.Shape]) -> cq.Compound | None:
    shape_list = list(shapes)
    if not shape_list:
        return None
    return cq.Compound.makeCompound(shape_list)


def cut_tools_for_access_holes(
    centers: Iterable[tuple[float, float]], p: RetainerParams, top_z: float, bottom_z: float, hole_d: float
) -> cq.Compound:
    shapes: list[cq.Shape] = []
    for x, y in centers:
        shapes.append(cylinder_solid(hole_d, bottom_z - 1.0, top_z + 1.0, x, y))
    tools = compound(shapes)
    assert tools is not None
    return tools


def chamfer_access_edges(model: cq.Workplane, chamfer: float) -> cq.Workplane:
    if chamfer <= 0:
        return model
    # Apply only immediately after vial access-hole cuts so the circular edges
    # on the top and lowest bottom faces are the vial openings.
    return model.faces(">Z").edges("%Circle").chamfer(chamfer).faces("<Z").edges("%Circle").chamfer(chamfer)


def boss_solids(centers: Iterable[tuple[float, float]], p: RetainerParams) -> cq.Compound | None:
    if p.boss_height <= 0:
        return None
    return compound(cylinder_solid(p.boss_od, -p.boss_height, 0.0, x, y) for x, y in centers)


def point_in_rounded_rect(x: float, y: float, length: float, width: float, radius: float) -> bool:
    hx = length / 2
    hy = width / 2
    ax = abs(x)
    ay = abs(y)
    if ax <= hx - radius and ay <= hy:
        return True
    if ay <= hy - radius and ax <= hx:
        return True
    return (ax - (hx - radius)) ** 2 + (ay - (hy - radius)) ** 2 <= radius**2 + 1e-9


def validate_params(p: RetainerParams) -> None:
    assert p.cols == 12, "retainer must have 12 columns"
    assert p.rows == 8, "retainer must have 8 rows"
    assert math.isclose(p.pitch_x, 9.0, abs_tol=1e-9), "X pitch must be 9.0 mm"
    assert math.isclose(p.pitch_y, 9.0, abs_tol=1e-9), "Y pitch must be 9.0 mm"
    assert len(vial_centers(p.cols, p.rows, p.pitch_x, p.pitch_y)) == 96, "must have 96 holes"
    assert p.access_d_min <= p.access_d <= p.access_d_max, "access_d outside valid range"
    assert p.access_d < p.vial_od, "access_d must be smaller than vial OD"
    assert p.pitch_x - p.access_d >= 1.5, "minimum X web between access holes is too small"
    assert p.pitch_y - p.access_d >= 1.5, "minimum Y web between access holes is too small"
    assert math.isclose(p.mount_x, p.accessory_x, abs_tol=0.05), "mount/accessory X symmetry changed"
    assert p.mount_x > 0 and p.mount_y > 0, "mount dimensions must be positive half-spacings"

    hole_checks = vial_centers(p.cols, p.rows, p.pitch_x, p.pitch_y) + mount_centers(p)
    if p.include_accessory_holes:
        hole_checks += accessory_centers(p)
    if p.include_thermocouple_hole:
        hole_checks.append((p.thermocouple_x, p.thermocouple_y))
    for x, y in hole_checks:
        assert point_in_rounded_rect(x, y, p.footprint_x, p.footprint_y, p.corner_r), (
            f"hole center ({x:.2f}, {y:.2f}) is outside footprint"
        )


def validate_bbox(model: cq.Workplane, p: RetainerParams, expected_x: float, expected_y: float) -> None:
    box = model.val().BoundingBox()
    assert math.isclose(box.xlen, expected_x, abs_tol=0.15), f"X bbox {box.xlen:.3f} != {expected_x:.3f}"
    assert math.isclose(box.ylen, expected_y, abs_tol=0.15), f"Y bbox {box.ylen:.3f} != {expected_y:.3f}"


def make_retainer(p: RetainerParams = PARAMS) -> cq.Workplane:
    validate_params(p)
    centers = vial_centers(p.cols, p.rows, p.pitch_x, p.pitch_y)

    model = rounded_plate(p.footprint_x, p.footprint_y, p.corner_r, p.plate_t)
    model = model.edges(">Z or <Z").chamfer(p.exterior_chamfer)

    bosses = boss_solids(centers, p)
    if bosses is not None:
        model = model.union(bosses, clean=False)

    bottom_z = -p.boss_height if p.boss_height > 0 else 0.0
    model = model.cut(cut_tools_for_access_holes(centers, p, p.plate_t, bottom_z, p.access_d), clean=False)
    model = chamfer_access_edges(model, p.access_chamfer)

    mount_shapes: list[cq.Shape] = []
    for x, y in mount_centers(p):
        mount_shapes.append(cylinder_solid(p.mount_clearance_d, -p.boss_height - 1.0, p.plate_t + 1.0, x, y))
        mount_shapes.append(
            cylinder_solid(
                p.mount_counterbore_d,
                p.plate_t - p.mount_counterbore_depth,
                p.plate_t + 1.0,
                x,
                y,
            )
        )
    if p.include_accessory_holes:
        for x, y in accessory_centers(p):
            mount_shapes.append(cylinder_solid(p.accessory_clearance_d, -p.boss_height - 1.0, p.plate_t + 1.0, x, y))
    if p.include_thermocouple_hole:
        mount_shapes.append(
            cylinder_solid(
                p.thermocouple_d,
                -p.boss_height - 1.0,
                p.plate_t + 1.0,
                p.thermocouple_x,
                p.thermocouple_y,
            )
        )

    mount_tools = compound(mount_shapes)
    if mount_tools is not None:
        model = model.cut(mount_tools, clean=False)

    validate_bbox(model, p, p.footprint_x, p.footprint_y)
    return model


def make_gasket(p: RetainerParams = PARAMS) -> cq.Workplane:
    validate_params(p)
    centers = vial_centers(p.cols, p.rows, p.pitch_x, p.pitch_y)
    model = rounded_plate(p.footprint_x, p.footprint_y, p.corner_r, p.gasket_t)
    model = model.cut(
        cut_tools_for_access_holes(centers, p, p.gasket_t, 0.0, p.access_d + p.gasket_hole_extra),
        clean=False,
    )
    model = chamfer_access_edges(model, min(p.access_chamfer, p.gasket_t / 3))

    shapes: list[cq.Shape] = []
    for x, y in mount_centers(p):
        shapes.append(cylinder_solid(p.mount_clearance_d, -1.0, p.gasket_t + 1.0, x, y))
    if p.include_accessory_holes:
        for x, y in accessory_centers(p):
            shapes.append(cylinder_solid(p.accessory_clearance_d, -1.0, p.gasket_t + 1.0, x, y))
    if p.include_thermocouple_hole:
        shapes.append(cylinder_solid(p.thermocouple_d, -1.0, p.gasket_t + 1.0, p.thermocouple_x, p.thermocouple_y))
    tools = compound(shapes)
    if tools is not None:
        model = model.cut(tools, clean=False)

    validate_bbox(model, p, p.footprint_x, p.footprint_y)
    return model


def make_coupon(p: RetainerParams = PARAMS) -> cq.Workplane:
    centers = vial_centers(p.coupon_cols, p.coupon_rows, p.pitch_x, p.pitch_y)
    length = (p.coupon_cols - 1) * p.pitch_x + p.boss_od + 2 * p.coupon_margin
    width = (p.coupon_rows - 1) * p.pitch_y + p.boss_od + 2 * p.coupon_margin
    model = rounded_plate(length, width, p.coupon_corner_r, p.plate_t)
    model = model.edges(">Z or <Z").chamfer(p.exterior_chamfer)

    bosses = boss_solids(centers, p)
    if bosses is not None:
        model = model.union(bosses, clean=False)

    bottom_z = -p.boss_height if p.boss_height > 0 else 0.0
    model = model.cut(cut_tools_for_access_holes(centers, p, p.plate_t, bottom_z, p.access_d), clean=False)
    model = chamfer_access_edges(model, p.access_chamfer)

    clamp_x = length / 2 - 6.0
    clamp_shapes = [
        cylinder_solid(p.coupon_clamp_d, -p.boss_height - 1.0, p.plate_t + 1.0, -clamp_x, 0.0),
        cylinder_solid(p.coupon_clamp_d, -p.boss_height - 1.0, p.plate_t + 1.0, clamp_x, 0.0),
    ]
    model = model.cut(compound(clamp_shapes), clean=False)

    validate_bbox(model, p, length, width)
    assert len(centers) == 12, "coupon must have 3 x 4 = 12 vial holes"
    return model


def print_parameter_table() -> None:
    print("| Name | Value (mm) | Source | Confidence | Notes |")
    print("| --- | ---: | --- | --- | --- |")
    for d in DIMENSIONS:
        value = d.value_mm if isinstance(d.value_mm, str) else f"{d.value_mm:.2f}"
        print(f"| {d.name} | {value} | {d.source} | {d.confidence} | {d.note} |")

    print("\nMounting dimensions inferred rather than explicitly dimensioned:")
    for d in DIMENSIONS:
        if "OEM screw" in d.name and d.source == "inferred from scaled PDF geometry":
            value = d.value_mm if isinstance(d.value_mm, str) else f"{d.value_mm:.2f} mm"
            print(f"- {d.name}: {value} ({d.confidence})")
    print("- OEM screw clearance diameter and counterbore depth are editable low-confidence design parameters.")


def export_step(model: cq.Workplane, path: Path) -> None:
    cq.exporters.export(model, str(path))
    print(f"exported {path.name}")


def main() -> None:
    out_dir = Path(__file__).resolve().parent
    print_parameter_table()
    export_step(make_retainer(PARAMS), out_dir / "ursa_101960_open_access_vial_retainer.step")
    export_step(make_gasket(PARAMS), out_dir / "ursa_101960_open_access_gasket.step")
    export_step(make_coupon(PARAMS), out_dir / "ursa_101960_3x4_test_coupon.step")


if __name__ == "__main__":
    main()
