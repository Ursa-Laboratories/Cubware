"""Render an STL file to a PNG preview for use in a part's README.

Style: flat-fill (no lighting) with feature edges, FXAA anti-aliasing,
orthographic projection. Reads like a clean isometric line drawing so
multiple previews in the repo look consistent.

Usage:
    pip install vtk
    python scripts/render_preview.py path/to/Part.stl path/to/Part.png

Tip: run with `--size 1600` for a larger render if a part is dense and
small features get crushed.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import vtk


def render(stl_path: Path, png_path: Path, size: int = 1200) -> None:
    reader = vtk.vtkSTLReader()
    reader.SetFileName(str(stl_path))
    reader.Update()

    surf_mapper = vtk.vtkPolyDataMapper()
    surf_mapper.SetInputConnection(reader.GetOutputPort())
    surf_mapper.ScalarVisibilityOff()

    surf = vtk.vtkActor()
    surf.SetMapper(surf_mapper)
    sp = surf.GetProperty()
    sp.SetColor(0.85, 0.87, 0.92)
    sp.LightingOff()

    feat = vtk.vtkFeatureEdges()
    feat.SetInputConnection(reader.GetOutputPort())
    feat.BoundaryEdgesOn()
    feat.FeatureEdgesOn()
    feat.SetFeatureAngle(25.0)
    feat.ManifoldEdgesOff()
    feat.NonManifoldEdgesOff()

    edge_mapper = vtk.vtkPolyDataMapper()
    edge_mapper.SetInputConnection(feat.GetOutputPort())
    edge_mapper.ScalarVisibilityOff()

    edges = vtk.vtkActor()
    edges.SetMapper(edge_mapper)
    ep = edges.GetProperty()
    ep.SetColor(0.15, 0.18, 0.22)
    ep.SetLineWidth(1.4)
    ep.LightingOff()

    renderer = vtk.vtkRenderer()
    renderer.SetBackground(1.0, 1.0, 1.0)
    renderer.AddActor(surf)
    renderer.AddActor(edges)
    renderer.UseFXAAOn()

    cam = renderer.GetActiveCamera()
    cam.ParallelProjectionOn()
    renderer.ResetCamera()
    cam.Azimuth(-35)
    cam.Elevation(25)
    cam.OrthogonalizeViewUp()
    renderer.ResetCamera()
    renderer.ResetCameraClippingRange()

    win = vtk.vtkRenderWindow()
    win.SetOffScreenRendering(1)
    win.AddRenderer(renderer)
    win.SetSize(size, size)
    win.SetMultiSamples(8)
    win.Render()

    w2i = vtk.vtkWindowToImageFilter()
    w2i.SetInput(win)
    w2i.SetInputBufferTypeToRGBA()
    w2i.ReadFrontBufferOff()
    w2i.Update()

    writer = vtk.vtkPNGWriter()
    writer.SetFileName(str(png_path))
    writer.SetInputConnection(w2i.GetOutputPort())
    writer.Write()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("stl", help="Input STL file")
    ap.add_argument("png", help="Output PNG file")
    ap.add_argument("--size", type=int, default=1200, help="Square image size in pixels")
    args = ap.parse_args()
    render(Path(args.stl), Path(args.png), size=args.size)
    print(f"wrote {args.png}", file=sys.stderr)
