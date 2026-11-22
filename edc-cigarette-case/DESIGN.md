# DESIGN.md: "Trail Kit" design language for the EDC case family

> Status: **v0.1, provisional.** These values were codified from the v1–v4 builds, not from user testing. Anything marked ⚠ is a sensible default awaiting a test print.

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
| `shell` | `#3B4A2F` (dark forest / military green) | All structure |
| `accent` | `#F2B705` (signal yellow) | Inlays, monogram, spine sleeve |
| Ratio | about 85–90% shell : 10–15% accent | Measured by face area |

⚠ Filament matches still need confirming in the chosen material, for example a matte dark green and a matte or basic yellow.

## 3. Geometry tokens (mm)
| Token | Value | Notes |
|---|---|---|
| `env` | 55 × 13 × 85 | Outer envelope, fixed |
| `edge.chamfer` | 1.0 ⚠ | Perimeter chamfer on every outer edge. A reviewer may push this to 1.5–2.0 for hand-feel |
| `wall.face` | 2.4–2.8 | Tray back / cover plate |
| `wall.side` | 2.4 | |
| `block.end` | 6.5 | Solid end blocks: magnets and strength |
| `inlay.depth` | 0.6 | About 4 layers at 0.16 mm |
| `inlay.line.min` | 0.6 (detail) / 1.0–1.2 (frames, index lines) | Below 0.6 mm the AMS can smear |
| `knurl` | Pyramids 2.1 base, 2.2 pitch, 0.9 high, tips flush | The signature grip texture |
| `panel.notch` | 45° step, 3–3.5 deep, at 55% of panel width | The signature stepped notch on the panel's top edge |
| `fit.hinge` | 0.3 knuckle gap; pin hole 2.1 for a 2.0 rod | ⚠ |
| `fit.lip` | 0.15 per side | ⚠ |
| `magnet` | 6 × 2 N52, pocket Ø6.2 × 2.1 | ⚠ |

## 4. Motifs (surface library)
| Motif | Type | Rules |
|---|---|---|
| **Contour** | Flush inlay | Every 5th line is an index line (1.2 mm); 0.7 mm otherwise; plus a neatline border |
| **Trailhead** | Knurl + flush frame | Recessed knurl panel with the stepped notch; 1.0 mm yellow frame offset 1.6 mm out from it |
| **Gridline** | Flush inlay | 9 mm grid, 0.6 mm lines, crosshair ring Ø12, tick marks on the bottom edge |
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
- **Material:** PETG-HF or ASA for carry and heat ⚠; PLA Matte for display pieces.
