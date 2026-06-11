# Agent Guide

This file tells agents (Claude, Codex, etc.) and humans how to add or
update parts in Cubware consistently. The repo holds 3D-printed STL and
design files for the Cub / CubOS ecosystem.

## Top-level layout

| Directory | What lives here |
| --- | --- |
| `labware/` | Deck accessories: holders, racks, tip racks, calibration plates that ship as Cub "labware" (each with a CubOS YAML config). |
| `gantry/`  | Gantry parts and base plates that define the deck geometry of a Cub configuration. |
| `mounts/`  | Mounts and brackets that bolt instrumentation onto a Cub system. |
| `scripts/` | Tooling — currently just the preview-render script. |

Within each top-level directory, every part has its own folder so it
can carry its own README, source CAD, mesh, and preview image.

## What a part folder must contain

Required:

| File | Purpose |
| --- | --- |
| `<Part>.stl` | Printable mesh. The thing the slicer eats. |
| `<Part>.png` | Isometric line-drawing preview, generated with `scripts/render_preview.py`. |
| `README.md`  | Title, embedded `<Part>.png`, what the part is, file table, assembly notes, compatibility (Cub / Cub-XL / which configuration). |

Strongly preferred when available:

| File | Purpose |
| --- | --- |
| `<Part>.step` | Source CAD. Lets future contributors modify the design instead of re-deriving from mesh. |

Labware folders only (consumed by CubOS):

| File | Purpose |
| --- | --- |
| `<Part>.yaml` | Labware definition (wells, dimensions, capacity, etc.). |
| `<Part>.glb`  | Web/local 3D preview for the CubOS viewer. |

A multi-part assembly may ship multiple stems (e.g. `OT2Backboard.stl`
and `Spacers.stl` in the same folder). Render one PNG per stem.

## Naming conventions

- **Folder names**: lowercase `snake_case`, descriptive. Examples:
  `ot2_backboard`, `vial_decapper_mount`, `cub_wellplate_holder`.
- **File names**: `PascalCase` matching the part purpose. Examples:
  `OT2Backboard.stl`, `VialDecapperMount.stl`, `TipRack.stl`.
- **One stem per part**: the `.stl`, `.step`, and `.png` for the same
  part share the same filename stem.
- **No source-system cruft**: drop vendor prefixes (`PAW-V2 -`), revision
  tags (`_REV. 1`), and exporter junk (`Part 1`, `Copy 1`) when bringing
  files in from CAD tools.
- **Folder name = README title**: the README's H1 should read like the
  PascalCase form with spaces (`ot2_backboard` → `# OT2 Backboard`).

## Generating the preview PNG

Use `scripts/render_preview.py`. It uses VTK with feature-edge overlay,
flat fill, and FXAA — no lighting, so multiple parts in the repo render
consistently and read like CAD line drawings.

```bash
pip install vtk
python scripts/render_preview.py path/to/Part.stl path/to/Part.png
```

Re-render the PNG whenever the underlying STL changes. Commit the PNG
alongside the STL.

## README template

```markdown
# <Part Name>

![<Part Name> preview](<Part>.png)

One- or two-sentence description: what this is, what system it bolts to.

## Files

| File | Purpose |
| --- | --- |
| `<Part>.stl` | Printable mesh. |
| `<Part>.step` | Source CAD. |

## Assembly (optional)

Numbered steps if non-obvious.

## Compatibility

- Deck: **Cub** / **Cub-XL** (which one — they are not interchangeable).
- Any other system this part bolts onto (link to that repo).
```

For multi-part folders, include a small preview table showing each
stem's PNG (see `mounts/ot2_backboard/README.md` for an example).

## Adding a new part — checklist

1. Pick a folder under `labware/`, `gantry/`, or `mounts/`. Create a new
   `snake_case` subfolder for the part.
2. Drop in `<Part>.stl` and `<Part>.step` (rename source files to drop
   any cruft, see naming conventions above).
3. Run `scripts/render_preview.py` to make `<Part>.png`.
4. Write `README.md` from the template above.
5. If the part attaches to another part in this repo, cross-link both
   READMEs (e.g. the OT2 attachments all link back to `ot2_backboard`).
