# Gantry

Cub systems are built on top of an off-the-shelf SainSmart PROVER CNC
gantry. Cubware currently supports three gantry configurations: one
small (**Cub**) and two large (**CubXL-PANDA** and **CubXL-ASMI**),
which differ in gantry size and in what instrumentation they're set up
to carry.

## Configurations

| Configuration | Gantry hardware | Purpose |
| --- | --- | --- |
| **Cub** | SainSmart PROVER 3030 | Compact bench setup. |
| **CubXL-PANDA** | SainSmart PROVER 4030XL | Non-contact multi-instrument deck — see [PANDA-BEAR](https://github.com/BU-KABlab/PANDA-BEAR). |
| **CubXL-ASMI** | SainSmart PROVER 4030XL | Indentation experiments with a force sensor — see [ASMI_new](https://github.com/BU-KABlab/ASMI_new). |

## Parts in this directory

| Folder | Used by | Description |
| --- | --- | --- |
| [`polycarb/`](polycarb/) | CubXL-PANDA | Polycarbonate base plate that reproduces the PANDA-BEAR deck layout. |

Mounts that bolt to a specific configuration (e.g. the Vernier force
sensor mount for ASMI) live under [`../mounts/`](../mounts/) rather than
here.
