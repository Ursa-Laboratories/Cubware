# Opentrons OT-2 Pipette Setup Guide

This page consolidates the current build, wiring, calibration, and CubOS
integration notes for using an Opentrons OT-2 electronic pipette on a PANDA/Cub
gantry. It covers the PAW/OT2 mechanical mount, Arduino stepper-control path,
tip rack expectations, and the CubOS implementation that maps the legacy
PANDA-BEAR OT2 pipette functions into current protocol commands.

## What The Pipette Setup Does

The setup mounts an Opentrons electronic pipette on the PAW/OT2 backboard and
drives the pipette plunger through the PANDA Arduino firmware. CubOS moves the
gantry to source, destination, tip-rack, and tip-disposal coordinates, then sends
serial commands to the Arduino for plunger actions such as home, aspirate,
dispense, blowout, mix, pick-up-tip, and drop-tip.

The CubOS code path is implemented, but the OT2 pipette hardware path has not
yet been validated on the physical machine in this checkout. Treat every
position, model constant, and serial command as a commissioning value until it
has been tested with the installed pipette, tip rack, and firmware.

## Standalone BOM

Quantities are for one OT-2 pipette station unless noted.

| Qty | Item | Use | Part number / spec | Source | Cost in repo |
| --- | --- | --- | --- | --- | --- |
| 1 | OT-2 single-channel electronic pipette | Liquid handling instrument | P300, `999-00003` in legacy BOM | [Opentrons](https://opentrons.com/products/single-channel-electronic-pipette-p20) | USD 2,750 |
| 1 | Arduino Uno SMD R3 | Serial control path to PAW firmware | `A000073` | [DigiKey](https://www.digikey.com/en/products/detail/arduino/A000073/3476357) | USD 26.30 |
| 1 | Adafruit TMC2209 stepper motor driver breakout | Drives the OT-2 pipette stepper motor | Adafruit `6121` | [Adafruit](https://www.adafruit.com/product/6121) | USD 17.90 |
| 1 | 10-pin socket/socket IDC cable, 6 in | Connection to the OT-2 pipette | Adafruit `370` | [Adafruit](https://www.adafruit.com/product/370) | USD 2.00 |
| 1 | Uno R3 proto shield or equivalent | PAW control circuitry | Legacy BOM used Adafruit `2077`; Cubware capper guide notes a generic Uno R3 protoshield alternative | [Adafruit](https://www.adafruit.com/product/2077) | USD 9.95 |
| 1 set | Jumper wires | Arduino/protoshield wiring | Female-female `4447`, extension `4635`, male-male `4482` | [Adafruit 4447](https://www.adafruit.com/product/4447), [Adafruit 4635](https://www.adafruit.com/product/4635), [Adafruit 4482](https://www.adafruit.com/product/4482) | USD 9.95, USD 11.95, USD 9.95 |
| 1 | USB extension cable | Communication with PAW hardware | 10-15 ft USB extension, UPC `686878976212` | [Amazon](https://a.co/d/3PqFbSj) | USD 8.99 |
| 1 kit | M3-M6 bolt kit | Mounting hardware for PAW/backboard parts | Kwokker M3-M6 bolt kit, 20 sizes | [Amazon](https://www.amazon.com/gp/product/B0CLZC8SQ5/) | USD 23.99 |
| As needed | Opentrons-compatible tips | Disposable pipette tips | Match the installed pipette model and tip rack geometry | Opentrons or equivalent | Not listed |

## Printed / Fabricated Parts

| Qty | Part | File | Notes |
| --- | --- | --- | --- |
| 1 | OT2 backboard mount | [`../mounts/ot2_backboard/`](../mounts/ot2_backboard/) | Main backboard that bolts to the OT-2 frame and carries the PAW-V2 mounts |
| 1 set | OT2 mount spacers | [`../mounts/ot2_backboard/`](../mounts/ot2_backboard/) | Sets the backboard standoff from the OT-2 frame |
| 1 | Legacy PAW-V2 OT2 mount | [`../mounts/ot2_backboard/PAW-V2 - OT2Mount_REV. 1 - OT2Mount.stl`](../mounts/ot2_backboard/PAW-V2%20-%20OT2Mount_REV.%201%20-%20OT2Mount.stl) | Cubware STL copy of the legacy PANDA-BEAR OT2 mount |
| 1 | Tip rack | [`../labware/ursa_tip_rack/`](../labware/ursa_tip_rack/) | CubOS tip-rack labware definition includes `tip_length`, pickup slots, and consumed-tip tracking |
| 1 | Used-tip disposal target | CubOS deck YAML `tip_disposal` labware | Needed for `drop_tip` protocol commands |

## Mount The Pipette

1. Print the OT2 backboard and spacer parts from
   [`../mounts/ot2_backboard/`](../mounts/ot2_backboard/).
2. Bolt the backboard to the OT-2 frame and confirm the plate is rigid before
   adding the pipette.
3. Mount the Opentrons pipette with the PAW-V2 OT2 mount hardware.
4. Route the pipette cable and Arduino USB cable so they cannot enter the
   gantry travel envelope.
5. Install the tip rack and used-tip disposal target on the deck.
6. Confirm the pipette nozzle can reach the intended tip-rack, source, and
   destination positions without the pipette body, cable, or backboard colliding
   with the deck or neighboring tools.

The legacy PANDA-BEAR checkout contains only the OT2 mount STEP file and wiring
evidence for this assembly. It does not contain a full mechanical drawing with
all fastener lengths, cable clips, or installation dimensions.

## Wire The Arduino Control Path

The OT2 pipette is controlled by the PAW Arduino firmware, not by the Opentrons
robot API. CubOS talks to the Arduino over serial at `115200` baud by default.

![Pipette control circuit](images/PipetteControl.png)

Use the diagram as the current wiring reference for the Arduino/TMC2209/pipette
control interface. The legacy PANDA-BEAR wiring docs point to the external
[BU-KABlab/PANDA_Arduino](https://github.com/BU-KABlab/PANDA_Arduino)
repository for firmware source, pin assignments, and installation instructions.

Before running pipette commands:

1. Flash the PAW Arduino firmware that supports the pipette command set.
2. Connect the Arduino to the CubOS host.
3. Identify the serial port, for example `/dev/ttyUSB0`, `/dev/ttyACM0`, or a
   macOS `/dev/tty.usb*` device.
4. Confirm no other process has the serial port open.
5. Keep the pipette clear of tips, liquids, and deck fixtures for the first
   home/status checks.

## Configure CubOS

CubOS loads the pipette as a gantry instrument with `type: pipette` and
`vendor: opentrons`. The vendor is registered in
`CubOS/src/instruments/registry.yaml` and resolves to
`instruments.pipette.vendors.opentrons.OpentronsPipette`.

Example gantry YAML:

```yaml
instruments:
  pipette:
    type: pipette
    vendor: opentrons
    pipette_model: p300_single_gen2
    port: /dev/ttyUSB0
    baud_rate: 115200
    offline: false
    offset_x: 180.0
    offset_y: -25.0
    depth: 0.0
```

Use `offline: true` only for dry runs and simulation. Real hardware requires a
valid `port` and `offline: false`.

The checked-in Sterling simulation config uses `p300_single_gen2` and keeps the
pipette offline. Its offsets are replay values, not installation dimensions:

```yaml
pipette_model: p300_single_gen2
offset_x: 180.0
offset_y: -25.0
depth: 0.0
offline: true
```

## Configure Tip Rack And Disposal Labware

CubOS tip pickup depends on a deck labware definition that can resolve a tip
slot and report tip length. A tip rack entry should include:

```yaml
tip_rack:
  load_name: ursa_tip_rack
  tip_length: 59.3
  pickup_z: 64.7
  drop_z: 34.0
  calibration:
    a1: { x: 210.0, y: 230.0 }
    a2: { x: 218.5, y: 230.0 }
```

`pick_up_tip` marks the chosen slot used and records the rack `tip_length` on
the pipette. CubOS then extends the pipette effective depth by that tip length
for later motion validation and engagement.

A used-tip disposal target can be modeled as `type: tip_disposal` with a named
slot such as `discard`. Protocols then call:

```yaml
- drop_tip:
    position: tip_disposal.discard
```

## CubOS Pipette Code Mapping

CubOS adapts the legacy PANDA-BEAR OT2 pipette control surface into a vendor
driver plus protocol commands. The mapping below describes what is implemented
in code today; it does not prove the current firmware/hardware combination has
been commissioned.

| Legacy PANDA-BEAR operation | CubOS driver method | Arduino serial command in CubOS | YAML protocol command | Notes |
| --- | --- | --- | --- | --- |
| `Pipette.home()` | `OpentronsPipette.home()` | `10` (`_CMD_HOME`) | Indirect via `home` for gantry; plunger home is available on the driver | Real driver sends a home command to Arduino; offline mode sets the plunger position to the model zero |
| `Pipette.prime()` / `OT2P300.prime()` | `OpentronsPipette.prime(speed=50.0)` | `11` (`_CMD_MOVE_TO`) to `prime_position` | No standalone YAML command | CubOS exposes this as driver warm-up behavior, not as a protocol step |
| `Pipette.aspirate(vol, s)` / `OT2P300.aspirate(...)` | `OpentronsPipette.aspirate(volume_ul, speed=50.0)` | `12` (`_CMD_ASPIRATE`) with converted mm travel | `aspirate`, `transfer`, `serial_transfer` | Protocol command first moves the gantry to the source labware position |
| `Pipette.dispense(vol, s)` / `OT2P300.dispense(...)` | `OpentronsPipette.dispense(volume_ul, speed=50.0)` | `13` (`_CMD_DISPENSE`) with converted mm travel | `transfer`, `serial_transfer`; direct `dispense` is intentionally not a YAML command | CubOS records transfer dispenses to the data store when a campaign store is configured |
| `Pipette.blowout()` / `OT2P300.blowout_no_tracker()` | `OpentronsPipette.blowout(speed=50.0)` | `11` (`_CMD_MOVE_TO`) to `blowout_position` | `blowout` | Protocol command moves to the requested labware position before blowout |
| `Pipette.mix(vol, n, s)` / `OT2P300.mix(...)` | `OpentronsPipette.mix(volume_ul, repetitions=3, speed=50.0)` | `15` (`_CMD_MIX`) | `mix` | Offline mode returns a synthetic `MixResult` |
| `Pipette.pick_up_tip()` | `OpentronsPipette.pick_up_tip(speed=50.0)` | `11` (`_CMD_MOVE_TO`) to `zero_position` | `pick_up_tip` | CubOS resolves the tip slot, checks availability, marks it used, and stores tip extension |
| `Pipette.drop_tip()` | `OpentronsPipette.drop_tip(speed=50.0)` | `11` (`_CMD_MOVE_TO`) to `drop_tip_position` | `drop_tip` | CubOS clears the attached-tip extension after dropping |
| `Pipette.get_status()` | `OpentronsPipette.get_status()` | `14` (`_CMD_STATUS`) | No YAML command | Returns homed state, plunger position, max volume, tip flag, and primed flag |
| `Pipette.drip_stop(vol, s)` / `OT2P300.drip_stop()` | `OpentronsPipette.drip_stop(volume_ul=5.0, speed=50.0)` | `28` (`_CMD_DRIP_STOP`) | No YAML command | Implemented on the CubOS driver, but not exposed as a protocol command |

Major differences from PANDA-BEAR:

- CubOS does not use PANDA-BEAR's `PipetteDBHandler` to track pipette contents.
- CubOS records transfer dispenses to its `DataStore` only when a protocol run
  is associated with a campaign data store.
- CubOS models attached disposable-tip length and uses it in motion validation.
- CubOS supports multiple pipette model names in `PIPETTE_MODELS`, but only
  `p300_single_gen2` is marked as using calibrated values sourced from
  PANDA-BEAR. Other model constants are placeholders pending hardware
  calibration.

## Supported CubOS Model Names

Current CubOS model names are:

| Model | Family | Channels | Volume range | Calibration status in code |
| --- | --- | --- | --- | --- |
| `p20_single_gen2` | OT-2 | 1 | 1-20 uL | Placeholder positions/conversion |
| `p300_single_gen2` | OT-2 | 1 | 20-200 uL in current CubOS constants | Calibrated from PANDA-BEAR comments |
| `p1000_single_gen2` | OT-2 | 1 | 100-1000 uL | Placeholder positions/conversion |
| `p20_multi_gen2` | OT-2 | 8 | 1-20 uL | Placeholder positions/conversion |
| `p300_multi_gen2` | OT-2 | 8 | 20-200 uL in current CubOS constants | Placeholder values copied from single P300 |
| `flex_1channel_50` | Flex | 1 | 1-50 uL | Placeholder positions/conversion |
| `flex_1channel_1000` | Flex | 1 | 5-1000 uL | Placeholder positions/conversion |
| `flex_8channel_50` | Flex | 8 | 1-50 uL | Placeholder positions/conversion |
| `flex_8channel_1000` | Flex | 8 | 5-1000 uL | Placeholder positions/conversion |
| `flex_96channel_1000` | Flex | 96 | 5-1000 uL | Placeholder positions/conversion |

Do not assume these non-P300 constants are safe for hardware until each model is
calibrated with its actual pipette, tips, and firmware.

## Example CubOS Protocol

```yaml
protocol:
  - home:

  - pick_up_tip:
      position: tip_rack.A1

  - transfer:
      source: plate.A1
      destination: plate.B1
      volume_ul: 50.0
      source_height: -2.0
      destination_height: 4.0

  - blowout:
      position: plate.B1
      height: 6.0

  - drop_tip:
      position: tip_disposal.discard

  - home:
```

This mirrors the checked-in offline replay at
`CubOS/configs/sim/pipette_tip_transfer/protocol.yaml`. Run it offline first,
then update the gantry/deck YAML paths and hardware flags only after physical
clearances and serial communication have been verified.

## Commissioning Checklist

1. Confirm the pipette is mechanically rigid in the OT2/backboard mount.
2. Confirm the cable path stays outside the gantry travel envelope.
3. Flash the PAW Arduino firmware with pipette command support.
4. Verify the Arduino serial port and baud rate.
5. With no tip installed, run only a status/home check first.
6. Calibrate the pipette instrument offset on the installed machine.
7. Calibrate the tip rack pickup slots and used-tip disposal slot.
8. Run `pick_up_tip` and `drop_tip` without liquid.
9. Confirm the tip is physically seated after pickup and physically released
   after drop-tip.
10. Run a low-volume water transfer into a visible target.
11. Validate aspirate/dispense volume with the balance before using chemistry.
12. Record the tested model, tip type, firmware revision, port, offsets,
   `tip_length`, pickup/drop Z values, volumes, and observed pass/fail results.

## Known Evidence Gaps

This checkout does not contain enough information to specify:

- Full mechanical assembly dimensions for the OT2 pipette mount.
- A verified CubOS hardware commissioning log for the OT2 pipette.
- Firmware source pinned to the exact Arduino command contract used by the
  current CubOS `OpentronsPipette` implementation.
- Calibrated CubOS constants for every supported pipette model.

Use the external `BU-KABlab/PANDA_Arduino` firmware repository and a controlled
hardware commissioning run before treating this setup as production-ready.
