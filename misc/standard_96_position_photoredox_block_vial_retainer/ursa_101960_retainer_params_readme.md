# Ursa 101960 Open-Access Vial Retainer

Open-access anti-lift vial retainer and optional gasket for the Analytical Sales
101960 Standard 96-Position Photoredox Reaction Block. The retainer is intended
to hold 8 mm OD vial lips down during indentation testing while leaving each
vial center open for the probe.

This is not a hermetic chemistry seal. It is a mechanical vial anti-lift cover
with optional compliant gasket features.

## Files

| File | Purpose |
| --- | --- |
| `ursa_101960_retainer.py` | Parameterized CadQuery 2.x source. |
| `ursa_101960_open_access_vial_retainer.step` | Full 96-position rigid retainer. |
| `ursa_101960_open_access_gasket.step` | Thin matching gasket. |
| `ursa_101960_3x4_test_coupon.step` | 3-column x 4-row retention test coupon. |

## Coordinate System

- Origin: center of the cover footprint in X/Y.
- X axis: 12-column vial direction.
- Y axis: 8-row vial direction.
- Z axis: upward.
- Rigid retainer underside is Z=0; underside bosses extend downward to negative Z.
- Units: millimeters only.

## Dimension Table

| Name | Value (mm) | Source | Confidence | Notes |
| --- | ---: | --- | --- | --- |
| Overall footprint length | 127.80 | explicit PDF dimension | high | 5.030 in [127.8 mm] |
| Overall footprint width | 85.50 | explicit PDF dimension | high | 3.365 in [85.5 mm] |
| Outer corner radius | 5.50 | explicit PDF dimension | high | R0.217 in [R5.5 mm] |
| Vial array | 12 x 8 = 96 | explicit PDF dimension | high | drawing row/column labels |
| Vial pitch X | 9.00 | explicit PDF dimension | high | 0.354 in [9.0 mm] |
| Vial pitch Y | 9.00 | explicit PDF dimension | high | 0.354 in [9.0 mm] |
| Left edge to first vial center | 14.40 | explicit PDF dimension | high | 0.566 in [14.4 mm] |
| Top edge to first vial center | 11.20 | explicit PDF dimension | high | 0.443 in [11.2 mm] |
| Holes in lid | 4.00 | explicit PDF dimension | high | 0.157 in [4.0 mm] |
| Holes in bottom | 6.00 | explicit PDF dimension | high | 0.236 in [6.0 mm] |
| Thermocouple hole diameter | 3.30 | explicit PDF dimension | high | 0.130 in [3.3 mm] |
| Height with vials | 46.20 | explicit PDF dimension | high | 1.820 in [46.2 mm] |
| Section dimension | 6.10 | explicit PDF dimension | high | 0.241 in [6.1 mm] |
| Section dimension | 5.10 | explicit PDF dimension | high | 0.202 in [5.1 mm] |
| OEM screw center X | 58.39 | inferred from scaled PDF geometry | medium-high | symmetric side clamp screw centers |
| OEM screw center Y | 18.00 | inferred from scaled PDF geometry | medium-high | symmetric side clamp screw centers |
| OEM screw head/counterbore diameter | 12.70 | inferred from scaled PDF geometry | medium | visible head rings vary about 12.3-12.7 mm |
| OEM screw clearance diameter | 5.20 | user-chosen design parameter | low | PDF does not label screw shank |
| OEM screw counterbore depth | 1.20 | user-chosen design parameter | low | thin printed cover default |
| Accessory 6-32 hole center X | 58.39 | inferred from scaled PDF geometry | high | corner threaded-hole locations |
| Accessory 6-32 hole center Y | 37.24 | inferred from scaled PDF geometry | high | corner threaded-hole locations |
| Accessory through-clearance diameter | 3.70 | user-chosen design parameter | medium | clearance for #6 / 6-32 fastener |
| Thermocouple hole center X | 58.39 | inferred from scaled PDF geometry | medium-high | upper-right thermocouple hole |
| Thermocouple hole center Y | 29.24 | inferred from scaled PDF geometry | medium-high | upper-right thermocouple hole |
| Rigid retainer thickness | 2.50 | user-chosen design parameter | medium | printable default |
| Access-hole diameter | 6.70 | user-chosen design parameter | medium | parameter `access_d`, valid 5.8-7.2 mm |
| Underside boss OD | 8.30 | user-chosen design parameter | medium | gentle vial-lip bearing land |
| Underside boss height | 0.40 | user-chosen design parameter | medium | set to 0 to disable |
| Gasket thickness | 0.80 | user-chosen design parameter | medium | TPU/silicone default |

## Extraction Notes

The PDF text layer contains the explicit inch and millimeter dimensions listed
above. The top view is drawn at 1:1 scale, so vector coordinates were calibrated
using 72 PDF points per inch and checked against the labeled 127.8 mm length,
85.5 mm width, and 9.0 mm vial pitch.

The vial-grid vector centers produce:

- 96 centers.
- X pitch: 8.996 to 9.017 mm, rounded to the explicit 9.0 mm design value.
- Y pitch: 8.996 to 9.017 mm, rounded to the explicit 9.0 mm design value.
- First vial center offset from left edge: 14.38 mm, matching 14.4 mm.
- First vial center offset from top edge: 11.25 mm, matching 11.2 mm.

## Dimensions To Confirm Before Production

Measure these with calipers on the actual block before production use:

- OEM screw shank / through-clearance diameter. The PDF shows screw head rings
  but does not label the screw shank.
- OEM screw counterbore depth. The 1.2 mm default is chosen for a 2.5 mm printed
  retainer, not extracted from the PDF.
- OEM screw head/counterbore diameter. The visible vector rings vary slightly
  across the four screws and sit very close to the side edge.
- Vial lip height and lip OD for the exact #884001 vial lot.
- Whether the thermocouple hole should remain open for the specific test setup.

## Design Parameters

- `access_d = 6.7 mm`, valid range 5.8 to 7.2 mm.
- `vial_od = 8.0 mm`.
- `boss_od = 8.3 mm`.
- `boss_id = access_d`.
- `boss_height = 0.4 mm`; set to 0 to disable underside bosses.
- Minimum web between neighboring access holes is checked as `pitch - access_d`
  and must be at least 1.5 mm.
- Gasket hole diameter is `access_d + 0.2 mm`.

## Print And Assembly

- Print the rigid retainer flat.
- Avoid supports if possible.
- Rigid retainer materials: PETG, nylon, PC, or aluminum if machined later.
- Gasket materials: TPU, laser-cut silicone, or similar compliant sheet.
- Do not crush glass vials.
- Use spacers, shoulder screws, or controlled screw torque.
- Validate on the 3 x 4 coupon first using the worst-case sticky hydrogel
  pull-off condition.

## Regenerating STEP Files

```bash
python ursa_101960_retainer.py
```

The script prints the parameter table and lists the mounting dimensions inferred
from PDF geometry before exporting the STEP files.
