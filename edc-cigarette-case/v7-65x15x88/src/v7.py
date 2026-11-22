"""v7 - Design 6 'Hybrid' re-proportioned to 65 (W) x 15 (D) x 88 (H) mm.
Hardware: only 2 x Ø9.51 x 2.51 mm magnets (sealed in) + 1.75 mm filament hinge pin.
6 rollie channels (6.6 mm), centred magnet clasp on the opening edge, 2 filter-tip bays, 'A·B' Inter Bold 5 mm on the bottom.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import v3
v3.W, v3.D, v3.H = 65.0, 15.0, 88.0                      # must precede every other project import
W, D, H = v3.W, v3.D, v3.H
import numpy as np, manifold3d as m3
import case as K, v5, v6
from v3 import chbox
from shapely.geometry import Polygon, LineString, Point, box as sbox
from shapely.ops import unary_union
from shapely import affinity

LAYER0, LAYER = 0.2, 0.16
MAG_D, MAG_T = 9.51, 2.51
POCKET_D, SKIN, GAP = 9.7, 0.4, 0.2
YD = 1.0                       # yellow inlay depth: 0.2 + 5 x 0.16
FONT, CAP = 'Inter-Bold.ttf', 5.0

P = dict(v5.P)
P.update(TC=3.0, WB=2.6, WS=2.6, END=9.0, R=2.8, G=0.3, CF=1.6, CB=2.2, CE=1.0, FACET=6.0,
         PIN_PRESS=1.80, PIN_SLIP=2.0, PIN_SLEEVE=2.1, SLOTS=6, SLOT_W=6.6, RIB_T=0.8, RIB_H=3.0,
         MAG_ENDS=False, INSIDE_PLATE=False, BOTTOM_MONO=False,
         SEGS=[(0, 16), (16, 34), (34, 54), (54, 72), (72, 88)],
         SCOOP_Z=(55, 70), NOTCH_Z=(54, 71))
TC, WB, WS, END, R = P['TC'], P['WB'], P['WS'], P['END'], P['R']
YS = -D / 2 + TC
CX0, CX1 = -W / 2 + WS, W / 2 - WS
XA = -W / 2 + R + 0.1
BOSS_R = POCKET_D / 2 + 0.8; BOSS_H = 1.4; REC_R = BOSS_R + GAP
MX = CX1 + (WS - 1.2) - REC_R                 # recess keeps a 1.2 mm side wall
MZ = H / 2
PILLAR_X0 = MX - REC_R - 1.0                  # 1.0 mm wall between recess and the last channel
P['SLOT_X1'] = PILLAR_X0 - 0.2

xz = [(-W / 2 + P['CE'], 0), (W / 2 - P['FACET'], 0), (W / 2, P['FACET']), (W / 2, H - P['FACET']), (W / 2 - P['FACET'], H),
      (-W / 2 + P['CE'], H), (-W / 2, H - P['CE']), (-W / 2, P['CE'])]
FRONT = Polygon(xz).buffer(-(P['CF'] + 0.3), join_style=2).intersection(sbox(XA + R - 0.8, -1, W, H + 1))
BACK = affinity.scale(Polygon(xz).buffer(-(P['CB'] + 0.3), join_style=2), -1, 1, origin=(0, 0))

def snap_down(z):
    return LAYER0 + np.floor((z - LAYER0) / LAYER + 1e-9) * LAYER

def ycyl(r, y0, y1, x=MX, z=MZ, seg=72):
    a, b = min(y0, y1), max(y0, y1)
    return m3.Manifold.cylinder(b - a, r, r, seg).rotate((-90, 0, 0)).translate((x, a, z))

def monogram():
    raw = v6.text_poly('A·B', CAP, FONT, thicken=0)
    parts = sorted(getattr(raw, 'geoms', [raw]), key=lambda q: q.area)
    dot = parts[0].centroid
    return unary_union(parts[1:] + [Point(dot.x, dot.y).buffer(0.75, quad_segs=16)])

def build():
    d = v5.book('none', p=P); tray, cover, ys = d['tray'], d['cover'], d['ys']
    env = v5.envelope(P)
    # ---- magnet clasp (sealed-in magnets) ----
    boss_top = YS + BOSS_H
    c_top_z = snap_down((boss_top - SKIN) + D / 2)                    # cover prints face-down: z = y + D/2
    c_pocket = ycyl(POCKET_D / 2, c_top_z - (MAG_T + 0.09) - D / 2, c_top_z - D / 2)
    rec_floor = YS + BOSS_H + GAP
    t_top_z = snap_down(D / 2 - (rec_floor + SKIN))                   # tray prints back-down: z = D/2 - y
    t_pocket = ycyl(POCKET_D / 2, D / 2 - t_top_z, D / 2 - (t_top_z - (MAG_T + 0.09)))
    pillar = chbox(PILLAR_X0, CX1 + 0.5, YS, D / 2 - WB + 0.1, MZ - POCKET_D / 2 - 1.4, MZ + POCKET_D / 2 + 1.4, cv=0.1)
    lip_slot = chbox(CX1 - 1.2 - GAP, CX1 + 0.1, YS - 1.0, YS + 1.4 + GAP, MZ - POCKET_D / 2 - 1.6, MZ + POCKET_D / 2 + 1.6, cv=0.1)
    fr_poly = v5.notched_panel(CX0 + 5.0, CX1 - 2.5, END + 3.0, H - END - 3.0, c=3.0, step=3.0)
    frame_ring = fr_poly.buffer(GAP, join_style=2).difference(fr_poly.buffer(-1.6 - GAP, join_style=2))
    frame_slot = v5._map_inner(K.shapely_to_cs(frame_ring).extrude(0.8 + GAP + 0.5), YS - 0.5)
    tray = (tray + (pillar ^ env)) - ycyl(REC_R, YS - 1.0, rec_floor) - lip_slot - t_pocket - frame_slot
    cover = (cover + (ycyl(BOSS_R, YS - 0.3, boss_top) ^ env)) - c_pocket
    tray = max(tray.decompose(), key=lambda q: q.volume()); cover = max(cover.decompose(), key=lambda q: q.volume())
    # ---- Design 6 visuals ----
    stone = Point(MX, MZ).buffer(7.2)
    zr0, zr1 = END + 1.5, H - END - 1.5
    def rip(x0, x1, toward_right):
        out = []
        for xc in np.arange(x0, x1, 2.8):
            t = (xc - x0) / (x1 - x0); t = t if toward_right else 1 - t
            A = 0.05 + 1.6 * t ** 1.6
            zs = np.linspace(zr0, zr1, 160)
            out.append(LineString([(xc + A * np.sin(2 * np.pi * z / 27.0 + 0.22 * xc), z) for z in zs]))
        return out
    xr0 = 2.2
    fr = [l.intersection(FRONT.buffer(-1.6)).difference(stone) for l in rip(xr0, FRONT.bounds[2] - 1.0, True)]
    cover = v6.grooves(cover, [g for l in fr for g in getattr(l, 'geoms', [l]) if not g.is_empty and g.length > 8], 'f')
    zd = round(0.382 * H, 1)                                           # golden-section datum
    br = [l.intersection(BACK.buffer(-1.6)).difference(sbox(-60, zd - 2.3, 60, zd + 2.3)) for l in rip(BACK.bounds[0] + 1.0, -2.2, False)]
    tray = v6.grooves(tray, [g for l in br for g in getattr(l, 'geoms', [l]) if not g.is_empty and g.length > 15], 'b')
    cover, y1 = v6.inlay(cover, sbox(FRONT.bounds[0] + 0.4, zd - 0.5, xr0 - 2.6, zd + 0.5), 'f', YD)
    tray, y2 = v6.inlay(tray, sbox(-W / 2 - 2.0, zd - 0.5, -7.0, zd + 0.5), 'b', YD)
    cover, y3 = v6.inside_inlay(cover, sbox(-(W / 2 - 10.0), zd - 0.5, W / 2 - 16.0, zd + 0.5), ys)
    mono = monogram()
    cut = v3.cs(mono).extrude(YD + 0.5).translate((0, 0, -0.5)).mirror((0, 1, 0)); y4 = cut ^ tray; tray = tray - cut
    d['knuckle_mod'] = d['knuckle_mod'] + chbox(PILLAR_X0 - 1, W / 2 + 1, -D, D, MZ - 9, MZ + 9, cv=0.1)
    return dict(d=d, tray=tray, cover=cover, sleeve=d['sleeve'], yel_cover=[y1, y3], yel_tray=[y2, y4], mono=mono,
                c_pocket=c_pocket, t_pocket=t_pocket, pause_cover_z=c_top_z + LAYER, pause_tray_z=t_top_z + LAYER,
                c_top_z=c_top_z, t_top_z=t_top_z, zd=zd)

def checks(r):
    a, b, s = r['tray'], r['cover'], r['sleeve']
    allp = [a, b, s] + r['yel_cover'] + r['yel_tray']
    ov = sum((x ^ y).volume() for i, x in enumerate(allp) for y in allp[i + 1:])
    bb = (a + b + s).bounding_box()
    RR = m3.Manifold.batch_boolean(v5.rollups(r['d']), m3.OpType.Add)
    XA_, YA_ = r['d']['axis']
    swing = [g for g in range(0, 166, 5) if (b.translate((-XA_, -YA_, 0)).rotate((0, 0, -g)).translate((XA_, YA_, 0)) ^ a).volume() > 0.02]
    def wall(part, pocket, grow=0.8):
        bbp = pocket.bounding_box(); g = ycyl(POCKET_D / 2 + grow, bbp[1], bbp[4])
        return round((g - pocket - part).volume(), 3)
    return dict(env=[round(bb[i + 3] - bb[i], 2) for i in range(3)], pieces=(len(a.decompose()), len(b.decompose())), overlap=round(ov, 3),
                rollups=len(v5.rollups(r['d'])), rollups_vs_tray=round((RR ^ a).volume(), 3), swing_contacts=swing,
                tray_wall_void=wall(a, r['t_pocket']), cover_wall_void=wall(b, r['c_pocket']),
                magnet_gap=round((D / 2 - r['t_top_z']) - (r['c_top_z'] - D / 2) - 0.18, 2),
                pause_cover_z=round(r['pause_cover_z'], 2), pause_tray_z=round(r['pause_tray_z'], 2),
                cover_front_skin=round(r['c_top_z'] - (MAG_T + 0.09), 2), MX=round(MX, 2), slot_x1=round(P['SLOT_X1'], 2),
                mono=[round(v, 2) for v in r['mono'].bounds], datum_z=r['zd'])

if __name__ == '__main__':
    r = build(); print(checks(r))
