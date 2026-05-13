# Cubware

Cubware is the repository for 3D-printed STL and design files for the open
source **Cub** and **CubOS** ecosystem. It holds the printable meshes,
source CAD (`.step`), preview assets, and any per-part documentation needed
to fabricate hardware for a Cub system.

## Layout

```
Cubware/
├── labware/   # Deck accessories: holders, racks, plates, etc.
├── gantry/    # Gantry parts and assemblies
└── mounts/    # Mounts and brackets for attaching hardware to the system
```

Each part lives in its own folder so that it can carry its own README,
preview images, source CAD, and any other documentation it needs.

## Folder conventions

Inside each part folder you may find:

| File | Purpose |
| --- | --- |
| `*.stl` | Printable mesh — what you send to the slicer. |
| `*.step` | Source CAD — editable in any parametric CAD tool. |
| `*.glb` | Web/local 3D preview. |
| `*.png` | Static preview image. |
| `*.yaml` | Optional labware config consumed by [CubOS](../cubos/). |
| `README.md` | Part-specific assembly, compatibility, and print notes. |

Not every folder has every file type — some parts are mesh-only, some are
CAD-only, and some labware additionally ship a YAML definition.

## Adding a new part

1. Create a new folder under the appropriate top-level directory
   (`labware/`, `gantry/`, or `mounts/`) using a descriptive `snake_case`
   name.
2. Drop in the `.stl` and/or `.step` files for the part.
3. Add a `README.md` covering: what the part is, what files are included,
   assembly steps, and compatibility (which Cub deck / hardware revision
   it fits).
4. Optionally include `.glb` and `.png` previews for quick visual reference.

## Related repos

- [CubOS](../cubos/) — control software for the Cub robot, which consumes
  the labware YAML definitions referenced here.
