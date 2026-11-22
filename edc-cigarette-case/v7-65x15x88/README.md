# AB Rollie Book v7: 65 × 15 × 88 mm, Bambu Lab A1 (current)

![v7](v7_a1_sheet.png)

| File | Use |
|---|---|
| **`AB_Rollie_Book_v7_A1_by_object.3mf`** | **Open this one.** A full Bambu Studio project for the **A1 + AMS lite**: one plate, by object, every setting included. |
| `AB_Rollie_Book_v7_A1_geometry_only.3mf` | **Fallback.** Identical parts, colours, modifiers and plate, but no print profile: it uses your own A1 presets, so it cannot raise a config error. |

![plate](v7_a1_plate.png)

## Fix in this revision: "Invalid configuration file"
- **Problem:** the previous A1 file failed to open ("Invalid configuration file", then "no geometry data").
- **Cause:** its settings were built from Bambu's **development** profiles.
  - That added 193 options beyond the creator's file. Released versions flag 43 to 123 of them as unknown.
  - It also added the new dual-nozzle (H2D) "extruder variant" keys.
  - As a result, the filament colours never loaded, and Bambu Studio rejects a project with no filaments.
- **Fix:** the project now uses **only the exact settings layout of the creator's original file**, which your Bambu Studio already opens (366 options, same order).
  - The values are Bambu's **released** A1 presets: Bambu Lab A1 0.4 nozzle, 0.16mm High Quality @BBL A1, and Bambu PETG HF @BBL A1 ×3.
  - **Removed:** no multi-extruder keys and no unknown options.
- **Geometry is unchanged:** the STLs are byte-identical.

## The only extra parts you need
| Part | Qty | Notes |
|---|---|---|
| Round magnets **Ø9.51 × 2.51 mm** | 2 | **Snap into** the printed pockets after printing |
| **1.75 mm filament** (PETG-HF) | ≈ 87 mm | Hinge pin |
| PETG-HF **grey / black / yellow** | AMS lite slots 1 / 2 / 3 | Cover / tray / yellow details and spine sleeve |

## How to print
1. Open `AB_Rollie_Book_v7_A1_by_object.3mf`.
   - If Bambu Studio asks about **customised presets**, keep the project's settings; this file deliberately differs from the stock presets.
   - Load **grey, black and yellow PETG-HF** into AMS lite slots 1, 2 and 3, then press **Sync AMS**.
2. Check that the plate shows **Print sequence: By object** and the **Textured PEI** plate. Slice and print. No pauses, no supports.
3. **Magnets:** stick the two magnets together and mark the two faces that touch. Press each magnet into its pocket **marked face OUT** until it clicks, so the magnets attract when the case closes.
4. **Hinge:** slide the yellow sleeve between the cover knuckles, then push the filament pin through from the top and trim it flush. Optionally, heat the ends briefly to flare them so the pin stays put.

**If the main file still refuses to open,** use `..._geometry_only.3mf`.
- **What comes with it:** Bambu keeps each part's filament, the 100% modifiers, and the per-object walls and infill. This is confirmed in its source; it adds the filament slots itself.
- **What you set:**
  - **Presets:** printer **Bambu Lab A1 0.4 nozzle**, process **0.16mm High Quality @BBL A1**, filaments **Bambu PETG HF** ×3.
  - **Plate:** Textured PEI.
  - **Plate settings:** print sequence **By object**.
  - **Prime tower:** off.
  - **Shells:** top 6 / bottom 5.
  - **Seam:** back.
  - **Elephant foot:** 0.15.

## Print profile (in the main file)
- **Base:** Bambu's **0.16mm High Quality @BBL A1** (outer wall 60 mm/s at 2000 mm/s², default acceleration 4000, nozzle 240 °C, Textured PEI 70 °C).
- **Walls and shells:** 4 walls (arachne), 6 top / 5 bottom shells.
- **Infill:** 50% gyroid, with **100% infill and 6 walls** on the hinge, end blocks and magnet clasp.
- **Seam and first layer:** seam at the back (the top end of the case); elephant-foot compensation 0.15.
- **By object on the A1:** parts sit 74 mm apart (clearance 73 mm), and all are under the 25 mm rod height.
- **Purge:** prime tower off; flush into infill on the cover and tray.

## Test slice and re-slice (PrusaSlicer 2.7.2 with A1 clearances, speeds and limits, sequential)
| | Slice from CAD | **Re-slice of the shipped 3MF** (meshes, filaments and modifiers read back out of the file) |
|---|---|---|
| Time (incl. AMS lite load/unload) | 3 h 44 m 11 s | **3 h 44 m 08 s** |
| Colour swaps / layers | 47 / 121 | 47 / 121 |
| Filament in parts (grey / black / yellow) | 19.5 / 36.6 / 0.6 g | 19.5 / 36.6 / 0.6 g |

- **Real-world time:** add the A1 purge (≈ 15–30 s per swap), giving **≈ 4 to 4¼ h**. Purge adds ≈ 15–20 g to the chute.
- **Swaps:** most of them come from the A·B on the bottom face, which stands upright in print.
- **"Long bridging" note:** this is benign. It is the 0.6 mm groove ceilings at z 0.68, plus the first solid layer over the gyroid inside the 3.0 / 2.6 mm floors. No supports are needed.
- **Reproduce:** `prusa-slicer --export-gcode --load test-slice/a1_hq_petghf_0.16.ini test-slice/roundtrip_from_shipped_3mf.3mf`

## Verification
| Check | Status |
|---|---|
| Envelope 65 × 15 × 88, single solid parts, no overlaps | PASS |
| 6 rollies clear; cover swings to 165° without contact | PASS |
| Magnet pockets: walls ≥ 0.8 mm, slotted snap lips present | PASS |
| Settings vs Bambu's option rules at releases **2.03, 2.08 and 2.09** | PASS: no flag that the creator's (working) file doesn't also raise. The previous file raised 60 to 123 more, plus the dual-nozzle keys |
| 3MF integrity: 9 manifold meshes, part filaments 1/2/3, 2 modifiers, 1 plate by object | PASS (read back from the shipped file) |
| Re-slice of the shipped file | PASS (see above) |
| Opened and sliced in real Bambu Studio (owner, A1) | PASS: "opened fine, sliced great" (22 Nov 2026) |
| Test print | PENDING: printer busy; first print planned for 23 Nov 2026 |

`src/` holds the generators:
- `a1_safe.py`: settings builder
- `bbsvalidate.py`: loader check
- `roundtrip_reslice.py`: re-slice of the shipped file

`superseded/` holds the earlier P1S three-plate file.
