# Cubware

Cubware is the repository for 3D-printed STL and design files for the open
source **Cub** and **CubOS** ecosystem. It holds the printable meshes,
source CAD (`.step`), preview assets, and any per-part documentation needed
to fabricate hardware for a Cub system.

## Configurations

Cub systems are built on top of an off-the-shelf SainSmart PROVER CNC
gantry. Cubware supports three configurations, and the repository is
organized by configuration:

| Configuration | Directory | Gantry hardware | Purpose |
| --- | --- | --- | --- |
| **Cub** | [`cub/`](cub/) | SainSmart PROVER 3030 | Single-instrument characterization. |
| **CubXL** | [`cubxl/`](cubxl/) | SainSmart PROVER 4030XL | Indentation experiments with a force sensor (ASMI) — see [ASMI_new](https://github.com/BU-KABlab/ASMI_new). |
| **CubXL+** | [`cubxl_plus/`](cubxl_plus/) | SainSmart PROVER 4030XL | Non-contact multi-instrument deck (PANDA) — see [PANDA-BEAR](https://github.com/BU-KABlab/PANDA-BEAR). |

## Layout

```
Cubware/
├── cub/                    # Cub (PROVER 3030)
│   ├── instrument_mounts/  #   uv_vis/, asmi/
│   └── labware/            #   well_plate_holder/, calibration_block/
├── cubxl/                  # CubXL (PROVER 4030XL, ASMI)
│   ├── instrument_mounts/  #   asmi/
│   └── labware/            #   well_plate_holder/, calibration_block/
├── cubxl_plus/             # CubXL+ (PROVER 4030XL, PANDA)
│   ├── deck/               #   polycarbonate_deck/
│   ├── instrument_mounts/  #   backboard/, vial_capper_decapper_mount/,
│   │                       #   raspberry_pi_mount/, potentiostat_mount/
│   └── labware/            #   well_plate_holder/, calibration_block/,
│                           #   vial_holder/, tip_rack_holder/
├── shared/                 # Parts used by every configuration
│                           #   (calibration_block/)
├── misc/                   # Parts not yet assigned to a configuration
├── documentation/          # Build guides and hardware assembly notes
├── tools/                  # CAD generation / QA scripts (FreeCAD)
└── scripts/                # Preview rendering helpers
```

Each part lives in its own folder so that it can carry its own README,
preview images, source CAD, and any other documentation it needs. Parts
shared by all three configurations (like the calibration block) live once
under `shared/`, with pointer READMEs in each configuration's tree.

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

## Documentation

- [Vial Capper / Decapper Build Guide](documentation/vial-capper-decapper-build.md)
  covers the PANDA capper/decapper BOM, cap fabrication, vial-holder setup,
  Arduino wiring, and CubOS integration status.

## Adding a new part

1. Create a new folder under the configuration the part belongs to
   (`cub/`, `cubxl/`, or `cubxl_plus/`), inside the appropriate category
   (`instrument_mounts/`, `labware/`, or `deck/`), using a descriptive
   `snake_case` name. Parts used by every configuration go under
   `shared/`.
2. Drop in the `.stl` and/or `.step` files for the part.
3. Add a `README.md` covering: what the part is, what files are included,
   assembly steps, and compatibility (which Cub deck / hardware revision
   it fits).
4. Optionally include `.glb` and `.png` previews for quick visual reference.

## Related repos

- [CubOS](../cubos/) — control software for the Cub robot, which consumes
  the labware YAML definitions referenced here.
