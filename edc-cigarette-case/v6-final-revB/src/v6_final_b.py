"""Design 6 (HYBRID), rev B: hardware = 2 x Ø9.51 x 2.51 mm magnets + 1.75 mm filament pin. Nothing else.
- one magnet pair at the centre of the opening edge, both magnets CAPTURED in the print (mid-print pause, no glue)
- cover gets a boss on its inner face to house its magnet; tray gets a matching recess + magnet pillar
- 5 rollie channels (6.4 mm) + two filter-tip bays above/below the magnet pillar
- hinge pin = 1.75 mm filament (press in tray end knuckles, slip in cover knuckles)
- initials 'A·B' in Inter Bold (Helvetica-class neo-grotesque, SIL OFL), 5.0 mm, dead-centre on the bottom
"""
import sys, os, json
import numpy as np, manifold3d as m3
sys.path.insert(0, os.path.dirname(__file__))
import v6, v5, v6_final
from v6 import text_poly, Point, unary_union, cs, sbox, LineString, grooves, inlay, inside_inlay, FRONT, BACK, base
from v3 import W, D, H, chbox

MAG_D, MAG_T = 9.51, 2.51
POCKET_D = 9.7                 # snug: holds the magnet against the nozzle's pull while it is sealed in
LAYER0, LAYER = 0.2, 0.16
YD = 1.0                       # yellow inlay depth
FONT, CAP = 'Inter-Bold.ttf', 5.0

P = dict(v6.P0)
P.update(MAG_ENDS=False, SLOTS=5, SLOT_W=6.4, RIB_T=0.8, SLOT_X1=13.3,
         PIN_PRESS=1.80, PIN_SLIP=2.0, PIN_SLEEVE=2.1, SCOOP_Z=(53, 67), NOTCH_Z=(52, 68))
TC, WB, WS, END = P['TC'], P['WB'], P['WS'], P['END']
YS = -D / 2 + TC                       # split plane (cover | tray)
CX1 = W / 2 - WS
MX, MZ = 20.4, 42.5                    # magnet centre (opening edge, mid-height)
BOSS_R, BOSS_H, GAP = 5.7, 1.4, 0.2
REC_R = BOSS_R + GAP
SKIN = 0.4                             # plastic over each sealed magnet

def snap_layer(z, up=True):
    k = np.ceil((z - LAYER0) / LAYER - 1e-9) if up else np.floor((z - LAYER0) / LAYER + 1e-9)
    return LAYER0 + k * LAYER

def ycyl(r, y0, y1, x=MX, z=MZ, seg=64):
    a, b = min(y0, y1), max(y0, y1)
    return m3.Manifold.cylinder(b - a, r, r, seg).rotate((-90, 0, 0)).translate((x, a, z))

def closure_geometry():
    """Returns solids and the print-Z of both pauses. Print frames: cover face-down (z = y + D/2), tray back-down (z = D/2 - y)."""
    # cover magnet: pocket sits in boss + plate, top of pocket on a layer boundary, SKIN below the boss face
    boss_top_y = YS + BOSS_H
    c_top_z = snap_layer((boss_top_y - SKIN) + D / 2, up=False)          # cover print z of pocket top
    c_bot_z = c_top_z - (MAG_T + 0.09)
    c_pocket = ycyl(POCKET_D / 2, c_bot_z - D / 2, c_top_z - D / 2)
    boss = ycyl(BOSS_R, YS - 0.3, boss_top_y)
    # tray magnet: under the recess floor, SKIN thick, top of pocket on a layer boundary (tray print z = D/2 - y)
    rec_floor_y = YS + BOSS_H + GAP
    t_top_z = snap_layer(D / 2 - (rec_floor_y + SKIN), up=False)
    t_bot_z = t_top_z - (MAG_T + 0.09)
    t_pocket = ycyl(POCKET_D / 2, D / 2 - t_top_z, D / 2 - t_bot_z)
    recess = ycyl(REC_R, YS - 1.0, rec_floor_y)
    pillar = chbox(SLOT_RIGHT() + 0.2, CX1 + 0.5, YS, D / 2 - WB + 0.1, MZ - POCKET_D / 2 - 1.4, MZ + POCKET_D / 2 + 1.4, cv=0.1)
    lip_slot = chbox(CX1 - 1.2 - GAP, CX1 + 0.1, YS - 1.0, YS + 1.4 + GAP, MZ - POCKET_D / 2 - 1.6, MZ + POCKET_D / 2 + 1.6, cv=0.1)
    return dict(boss=boss, c_pocket=c_pocket, recess=recess, t_pocket=t_pocket, pillar=pillar, lip_slot=lip_slot,
                pause_cover_z=c_top_z + LAYER, pause_tray_z=t_top_z + LAYER, c_top_z=c_top_z, t_top_z=t_top_z)

def SLOT_RIGHT():
    return P['SLOT_X1']

def monogram():
    raw = text_poly('A·B', CAP, FONT, thicken=0)
    parts = sorted(getattr(raw, 'geoms', [raw]), key=lambda q: q.area)
    dot = parts[0].centroid
    return unary_union(parts[1:] + [Point(dot.x, dot.y).buffer(0.75, quad_segs=16)])

def build():
    d = base(P); tray, cover, ys = d['tray'], d['cover'], d['ys']
    cg = closure_geometry()
    # closure
    # clearance for the cover's raised inner frame where it passes the pillar
    fr_poly = v6.v5.notched_panel(-W / 2 + WS + 5.0, CX1 - 2.5, END + 3.0, H - END - 3.0, c=3.0, step=3.0)
    frame_ring = fr_poly.buffer(GAP, join_style=2).difference(fr_poly.buffer(-1.6 - GAP, join_style=2))
    frame_slot = v5._map_inner(v6.K.shapely_to_cs(frame_ring).extrude(0.8 + GAP + 0.5), YS - 0.5)
    tray = (tray + (cg['pillar'] ^ v5.envelope(P))) - cg['recess'] - cg['lip_slot'] - cg['t_pocket'] - frame_slot
    cover = (cover + (cg['boss'] ^ v5.envelope(P))) - cg['c_pocket']
    tray = max(tray.decompose(), key=lambda q: q.volume()); cover = max(cover.decompose(), key=lambda q: q.volume())
    # visuals (design 6), ripples part around the magnet like water around a stone
    stone = Point(MX, MZ).buffer(6.8)
    def rip(x0, x1, z0, z1, toward_right):
        out = []
        for xc in np.arange(x0, x1, 2.8):
            t = (xc - x0) / (x1 - x0); t = t if toward_right else 1 - t
            A = 0.05 + 1.5 * t ** 1.6
            zs = np.linspace(z0, z1, 140)
            out.append(LineString([(xc + A * np.sin(2 * np.pi * z / 26.0 + 0.22 * xc), z) for z in zs]))
        return out
    fr = [l.intersection(FRONT.buffer(-1.6)).difference(stone) for l in rip(1.8, 24.0, 9.8, 75.2, True)]
    cover = grooves(cover, [g for l in fr for g in getattr(l, 'geoms', [l]) if not g.is_empty and g.length > 8], 'f')
    br = [l.intersection(BACK.buffer(-1.6)).difference(sbox(-40, 30.2, 40, 34.8)) for l in rip(-24.0, -1.8, 9.8, 75.2, False)]
    tray = grooves(tray, [g for l in br for g in getattr(l, 'geoms', [l]) if not g.is_empty and g.length > 15], 'b')
    cover, y1 = inlay(cover, sbox(-23.0, 32.0, -0.8, 33.0), 'f', YD)
    tray, y2 = inlay(tray, sbox(-29.0, 32.0, -6.0, 33.0), 'b', YD)
    cover, y3 = inside_inlay(cover, sbox(-17.5, 32.0, 13.0, 33.0), ys)
    mono = monogram()
    cut = cs(mono).extrude(YD + 0.5).translate((0, 0, -0.5)).mirror((0, 1, 0)); y4 = cut ^ tray; tray = tray - cut
    d['knuckle_mod'] = d['knuckle_mod'] + chbox(SLOT_RIGHT(), W / 2 + 1, -D, D, MZ - 8, MZ + 8, cv=0.1)   # 100% around the magnets too
    return dict(d=d, tray=tray, cover=cover, sleeve=d['sleeve'], yel_cover=[y1, y3], yel_tray=[y2, y4], mono=mono, cg=cg)

def checks(r):
    a, b, s = r['tray'], r['cover'], r['sleeve']; cg = r['cg']
    allp = [a, b, s] + r['yel_cover'] + r['yel_tray']
    ov = sum((x ^ y).volume() for i, x in enumerate(allp) for y in allp[i + 1:])
    bb = (a + b + s).bounding_box()
    RR = m3.Manifold.batch_boolean(v5.rollups(r['d']), m3.OpType.Add)
    XA, YA = r['d']['axis']
    swing = [g for g in range(0, 166, 5) if (b.translate((-XA, -YA, 0)).rotate((0, 0, -g)).translate((XA, YA, 0)) ^ a).volume() > 0.02]
    # magnet walls: pocket grown by 0.8 mm must be solid (except the 0.4 skin side, checked separately)
    def wall(part, pocket, grow):
        g = ycyl(POCKET_D / 2 + grow, pocket.bounding_box()[1] - 0.0, pocket.bounding_box()[4])
        return round((g - pocket - part).volume(), 3)
    # magnet-to-magnet air+plastic gap when closed
    c_face_y = cg['c_top_z'] - D / 2; t_face_y = D / 2 - cg['t_top_z']
    return dict(env=[round(bb[i + 3] - bb[i], 2) for i in range(3)], pieces=(len(a.decompose()), len(b.decompose())), overlap=round(ov, 3),
                rollups=len(v5.rollups(r['d'])), rollups_vs_tray=round((RR ^ a).volume(), 3), swing_contacts=swing,
                tray_wall_void=wall(a, cg['t_pocket'], 0.8), cover_wall_void=wall(b, cg['c_pocket'], 0.8),
                magnet_gap_mm=round(t_face_y - c_face_y - 2 * 0.09, 2), pause_cover_z=round(cg['pause_cover_z'], 2),
                pause_tray_z=round(cg['pause_tray_z'], 2), cover_front_skin=round(cg['c_top_z'] - (MAG_T + 0.09), 2),
                mono_bbox=[round(v, 2) for v in r['mono'].bounds])

if __name__ == '__main__':
    r = build(); print(checks(r))
    if len(sys.argv) > 2:
        v6_final.P_EXPORT = P
        v6_final.TITLE = 'AB Rollie Book - Hybrid rev B'
        v6_final.FNAME = 'AB_Rollie_Book_Hybrid_revB_55x13x85.3mf'
        v6_final.DESC = ('Slim rollie case 55x13x85 mm, 5 channels (rollies up to 6 x 60 mm) + 2 filter-tip bays. PETG-HF: filament 1 grey (cover), 2 black (tray), '
                         '3 yellow (inlays, sleeve). Hardware: ONLY 2 x 9.51x2.51 mm magnets (sealed in via 2 pauses) + 1.75 mm filament hinge pin. No supports, no glue.')
        print(v6_final.export(r, sys.argv[1], sys.argv[2]))
