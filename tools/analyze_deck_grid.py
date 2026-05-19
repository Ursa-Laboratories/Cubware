#!/usr/bin/env python3
"""Extract repeated cylindrical/slot features from the PandaDeck STEP."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from pathlib import Path

import FreeCAD
import Part


def _round(value: float, places: int = 3) -> float:
    return round(float(value), places)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("step", type=Path)
    args = parser.parse_args()

    shape = Part.Shape()
    shape.read(str(args.step))

    cylinders = []
    planes = []
    for face in shape.Faces:
        surface = face.Surface
        name = surface.__class__.__name__
        bb = face.BoundBox
        if name == "Cylinder":
            cylinders.append(
                {
                    "radius": _round(surface.Radius),
                    "center": (
                        _round(surface.Center.x),
                        _round(surface.Center.y),
                        _round(surface.Center.z),
                    ),
                    "axis": (
                        _round(surface.Axis.x),
                        _round(surface.Axis.y),
                        _round(surface.Axis.z),
                    ),
                    "bbox": (
                        _round(bb.XMin),
                        _round(bb.YMin),
                        _round(bb.ZMin),
                        _round(bb.XMax),
                        _round(bb.YMax),
                        _round(bb.ZMax),
                    ),
                    "area": _round(face.Area),
                }
            )
        elif name == "Plane":
            planes.append(face)

    print(f"deck: {args.step}")
    print(f"bbox: {shape.BoundBox}")
    print(f"cylindrical_faces: {len(cylinders)}")
    print(f"cylinder_radius_counts: {Counter(c['radius'] for c in cylinders)}")
    print(f"cylinder_axis_counts: {Counter(c['axis'] for c in cylinders)}")

    by_radius = defaultdict(list)
    for cylinder in cylinders:
        by_radius[cylinder["radius"]].append(cylinder)

    for radius, items in sorted(by_radius.items()):
        print(f"\nradius={radius} count={len(items)}")
        xs = sorted({item["center"][0] for item in items})
        ys = sorted({item["center"][1] for item in items})
        zs = sorted({item["center"][2] for item in items})
        print(f"  unique_center_x: {xs[:40]}{' ...' if len(xs) > 40 else ''}")
        print(f"  unique_center_y: {ys[:60]}{' ...' if len(ys) > 60 else ''}")
        print(f"  unique_center_z: {zs}")
        print("  first_40:")
        for item in sorted(items, key=lambda c: (c["center"][1], c["center"][0], c["center"][2]))[:40]:
            print(
                "    "
                f"center={item['center']} axis={item['axis']} "
                f"bbox={item['bbox']} area={item['area']}"
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
