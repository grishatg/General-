# DESIGN.md: "Trail Kit" design language for the EDC case family

> Status: **v0.2, provisional.** These values were codified from the v1–v5 builds and revised after a research agent and an independent design critique. Nothing has been checked against user testing yet. Anything marked ⚠ is a sensible default awaiting a test print.

This is an original design language inspired by JanBerry Design's *Hiking Container* (rugged outdoor kit: faceted, grippy, honest hardware). No geometry from that model is used.

## 1. Principles
1. **Kit, not gadget.** It should read as outdoor or tactical equipment. Use flat planes, chamfers and visible fixings; avoid organic curves and logos.
2. **Flush by default.** Colour is inlaid flush with the surface. Only a deliberate grip texture may break the surface, and even then its tips stay level with the face.
3. **Design the inside.** Opening the case is a moment. The inside of the cover gets a detail too.
4. **Strong where it's loaded.** Hinge, magnet blocks and edges are solid; the faces can be lighter.
5. **One accent colour, used sparingly.** Yellow marks information (lines, frames, initials) and one piece of hardware. It is never a fill.

## 2. Colour tokens
| Token | Hex | Use |
|---|---|---|
| `shell` | `#39541A`, Bambu PETG HF Forest Green (design intent `#3B4A2F`) | All structure |
| `accent` | `#FFD00B`, Bambu PETG HF Yellow (design intent `#F2B705`) | Inlays, monogram, spine sleeve, inside data plate |
| Ratio | about 85–90% shell : 10–15% accent | Measured by face area |

⚠ The hex values come from retailer copies of Bambu's colour tables. Check them against real spools.

## 3. Geometry tokens (mm)
| Token | Value | Notes |
|---|---|---|
| `env` | 55 × 13 × 85 | Outer envelope, fixed |
| `edge.chamfer` | 1.5 front / 2.0 back / 1.0 top and bottom | Bed-side edges are chamfered, not filleted, so they print without overhang |
| `facet` | 5.0 × 45° | Opening-side corners of the front outline (octagonal silhouette); panels repeat this as 9 mm corner cuts |
| `wall.face` | 2.4–2.8 | Tray back / cover plate |
| `wall.side` | 2.4 | |
| `block.end` | 8.5 | Solid end blocks: magnets (1.1 mm wall) and strength. v4 at 6.5 mm left only 0.15 mm of wall |
| `inlay.depth` | 0.6 | About 4 layers at 0.16 mm |
| `inlay.line.min` | 1.0 (detail) / 1.4–1.6 (frames, index lines) | Thinner lines smear on a 0.4 mm nozzle |
| `inlay.keepout` | ≥ 0.8 from magnets | Yellow never sits over a magnet pocket |
| `knurl` | Truncated pyramids: 2.2 base, 0.6 flat top, 2.4 pitch, 0.9 high; tops flush | Flat tops print on the bed and feel less sharp |
| `panel.notch` | 45° step, 3–3.5 deep, at 55% of panel width | The signature stepped notch on the panel's top edge |
| `fit.hinge` | 0.3 knuckle gap; tray knuckles Ø1.95 (press fit, ream with a 2.0 drill); cover knuckles Ø2.2 (slip); sleeve Ø2.3; teardrop bores | ⚠ print the test block first |
| `channel` | 6.8 slot / 1.2 rib / 3.0 high | For rollies 5–6 mm; use 7.4 for fatter rolls |
| `fit.lip` | 0.15 per side | ⚠ |
| `magnet` | 6 × 2 N52; pocket Ø6.3 × 2.4 (tray), × 2.1 (cover); thick CA or epoxy | ⚠ check polarity |

## 4. Motifs (surface library)
| Motif | Type | Rules |
|---|---|---|
| **Contour** | Flush inlay | 13 levels; every 4th is an index line (1.6 mm); 1.0 mm otherwise; plus a 1.2 mm neatline border |
| **Trailhead** | Knurl + flush frame | Recessed flat-top knurl panel with the stepped notch; 1.4 mm yellow frame offset 2.0 mm out from it; kept clear of the end blocks |
| **Gridline** | Flush inlay | 12 mm grid, 1.0 mm lines, Ø13 waypoint ring, 1.2 mm frame |
| **Hazard** | Flush inlay | 45° chevrons, 6 mm pitch, in a framed band. For caps only |

## 5. Typography
- **Monogram:** Black Ops One (SIL OFL), stencil-military. Cap height 5.6 mm on the 13 mm bottom edge, flanked by 3.5 × 1.0 mm index bars.
- No other text appears on the product.

## 6. Hardware language
- The pin, the magnets and the spine sleeve are **visible on purpose**: the hardware is part of the look.
- **Accent hardware:** one yellow element per product (the spine sleeve on the Book, a latch clip on the Hiking Container).

## 7. Print rules
- Decorated faces print **on the bed** (face-down), so inlays come out crisp and flush.
- **No supports.** Overhangs are 45° or less, and horizontal holes are 3 mm or smaller.
- **Infill:** 4 walls and 50% gyroid as baseline; **100% with 6 walls** on the hinge and magnet blocks via modifiers.
- **Material:** **Bambu PETG HF** (heat deflection 62 °C under load; UK car cabins reach about 55 °C). PLA Matte is for display pieces only.
- Raise *Bottom painting layer penetration* to the inlay layer count, then check layer 1 in the preview.
- Use a small prime tower. Flushing into infill can show through thin walls.

## 8. Inside language
- **Inside the cover:** a raised 0.8 mm notched-octagon stiffening frame, a flush yellow 60 mm ruler (5 mm ticks), and a mirrored monogram that reads correctly when the case is open.
