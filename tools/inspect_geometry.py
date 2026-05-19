#!/usr/bin/env python3
"""Inspect STEP/STL files with FreeCAD for Cubware CAD QA."""

from __future__ import annotations

import argparse
import math
import struct
from pathlib import Path

import FreeCAD
import Mesh
import Part


def _fmt(value: float) -> str:
    return f"{value:.3f}"


def _bbox_text(bb: FreeCAD.BoundBox) -> str:
    return (
        f"min=({_fmt(bb.XMin)}, {_fmt(bb.YMin)}, {_fmt(bb.ZMin)}) "
        f"max=({_fmt(bb.XMax)}, {_fmt(bb.YMax)}, {_fmt(bb.ZMax)}) "
        f"span=({_fmt(bb.XLength)}, {_fmt(bb.YLength)}, {_fmt(bb.ZLength)})"
    )


def inspect_step(path: Path) -> None:
    shape = Part.Shape()
    shape.read(str(path))
    print(f"{path}")
    print("  type: STEP")
    if shape.isNull():
        print("  null: True")
        return
    bb = shape.BoundBox
    solids = shape.Solids
    shells = shape.Shells
    faces = shape.Faces
    edges = shape.Edges
    volume = sum(s.Volume for s in solids) if solids else None
    area = sum(s.Area for s in solids) if solids else None
    print(f"  bbox_mm: {_bbox_text(bb)}")
    print(
        "  topology: "
        f"solids={len(solids)} shells={len(shells)} faces={len(faces)} "
        f"edges={len(edges)}"
    )
    if volume is not None and area is not None:
        print(f"  volume_mm3: {_fmt(volume)}")
        print(f"  area_mm2: {_fmt(area)}")
    else:
        print("  volume_mm3: n/a")
        print("  area_mm2: n/a")
    print(f"  valid: {shape.isValid()} null: {shape.isNull()} closed: {shape.isClosed()}")
    if solids:
        for index, solid in enumerate(solids, start=1):
            print(
                f"  solid_{index}: volume_mm3={_fmt(solid.Volume)} "
                f"bbox={_bbox_text(solid.BoundBox)} valid={solid.isValid()}"
            )


def _is_binary_stl(data: bytes) -> bool:
    if len(data) < 84:
        return False
    tri_count = struct.unpack("<I", data[80:84])[0]
    return 84 + tri_count * 50 == len(data)


def inspect_stl(path: Path) -> None:
    mesh = Mesh.Mesh(str(path))
    bb = mesh.BoundBox
    data = path.read_bytes()
    binary = _is_binary_stl(data)
    facets = mesh.CountFacets
    points = mesh.CountPoints
    self_intersections = (
        mesh.countSelfIntersections() if hasattr(mesh, "countSelfIntersections") else "n/a"
    )
    closed = mesh.isClosed() if hasattr(mesh, "isClosed") else "n/a"
    manifold = mesh.isManifold() if hasattr(mesh, "isManifold") else "n/a"
    components = mesh.countComponents() if hasattr(mesh, "countComponents") else "n/a"
    non_uniform_facets = (
        mesh.countNonUniformOrientedFacets()
        if hasattr(mesh, "countNonUniformOrientedFacets")
        else "n/a"
    )
    segments = mesh.countSegments() if hasattr(mesh, "countSegments") else "n/a"
    print(f"{path}")
    print(f"  type: {'binary' if binary else 'ascii'} STL")
    print(f"  bbox_mm: {_bbox_text(bb)}")
    print(f"  mesh: facets={facets} points={points}")
    print(f"  volume_mm3: {_fmt(mesh.Volume)} area_mm2: {_fmt(mesh.Area)}")
    print(
        "  mesh_checks: "
        f"solid={mesh.isSolid()} closed={closed} "
        f"manifold={manifold} components={components} segments={segments} "
        f"non_uniform_oriented_facets={non_uniform_facets} "
        f"self_intersections={self_intersections}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()

    for path in args.paths:
        suffix = path.suffix.lower()
        if suffix in {".step", ".stp"}:
            inspect_step(path)
        elif suffix == ".stl":
            inspect_stl(path)
        else:
            raise SystemExit(f"Unsupported file type: {path}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
