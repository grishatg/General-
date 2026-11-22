"""Slim EDC cigarette case - parametric generator.
Design language borrowed (not copied) from JanBerry Design's Hiking Container:
faceted chamfered shell, screw-pin side hinge on lug fins, latch block on the
opposite side, recessed front panels with an angular step, lanyard hole.
Two-colour: forest/military green shell, yellow topographic-line inserts.
Axes: X width, Y depth (front = -Y), Z up. Units mm.
"""
import numpy as np, manifold3d as m3
from shapely.geometry import Polygon, LineString, MultiPolygon, box as sbox
from shapely.ops import unary_union
from skimage import measure

# ---------------- parameters ----------------
N_CIG   = 10      # cigarettes in a single row
CIG_D   = 8.0     # king size ~7.8-8.0 mm diameter
CIG_L   = 85.0    # king size length (100s: 100)
STICK   = 18.0    # how far cigs stand proud of the body (grab length)
W_IN    = N_CIG * CIG_D + 2.6      # 82.6 - slack checked by hinge sim
D_IN    = CIG_D + 1.0              # 9.0
WALL_S  = 2.2     # side walls
WALL_F  = 2.6     # front/back walls (1.2 pocket + 1.4 skin)
FLOOR   = 2.0
TOP     = 2.4
W  = W_IN + 2 * WALL_S             # 87.0
D  = D_IN + 2 * WALL_F             # 14.2
HS = FLOOR + CIG_L - STICK         # seam height 69.0
HL = STICK + 1.0 + TOP             # lid height 21.4
LIP_H, LIP_T, GAP = 3.0, 1.0, 0.2
CV = 2.0                           # vertical edge chamfer
POCKET = 1.2
# hinge
PX, PZ_OFF, R_LOBE = 5.0, 3.0, 3.4
XP, ZP = -W / 2 - PX, HS + PZ_OFF
LUG_T, HGAP = 4.0, 0.3
PIN_CLR, PIN_TAP = 3.3, 2.5        # M3 x 14 SHCS, self-taps into back lug
# latch block (2 pairs 5x3 mm magnets)
BLK = 5.0
MAG_D, MAG_H = 5.2, 3.2
MAG_X, MAG_Y = W_IN / 2 + 3.5, 3.3

SEG = 64

def xs_poly(pts):
    p = np.array(pts, float)
    a = 0.5 * np.sum(p[:, 0] * np.roll(p[:, 1], -1) - np.roll(p[:, 0], -1) * p[:, 1])
    if a < 0: p = p[::-1]
    return m3.CrossSection([p], m3.FillRule.Positive)

def prism_xz(pts_xz, y0, y1):
    cs = xs_poly(pts_xz)                    # sketch coords (x, z)
    s = cs.extrude(y1 - y0)                 # (x, z_s, t)
    s = s.rotate((90, 0, 0))                # (x, z_s, t) -> (x, -t, z_s)
    return s.translate((0, y1, 0))          # Y spans [y0, y1]

def chrect(x0, x1, y0, y1, c):
    return [(x0 + c, y0), (x1 - c, y0), (x1, y0 + c), (x1, y1 - c),
            (x1 - c, y1), (x0 + c, y1), (x0, y1 - c), (x0, y0 + c)]

def chbox(x0, x1, y0, y1, z0, z1, cv=CV, cb=0.0, ct=0.0):
    """Box with chamfered vertical edges (cv) and bottom/top perimeter chamfers."""
    def slab(inset, za, zb):
        cs = xs_poly(chrect(x0 + inset, x1 - inset, y0 + inset, y1 - inset, max(cv - inset * 0.414, 0.01)))
        return cs.extrude(zb - za).translate((0, 0, za))
    parts = [slab(0, z0 + cb, z1 - ct)]
    if cb: parts.append(slab(cb, z0, z0 + 0.01))
    if ct: parts.append(slab(ct, z1 - 0.01, z1))
    return m3.Manifold.batch_hull(parts) if len(parts) > 1 else parts[0]

def cyl_y(x, z, r, y0, y1):
    c = m3.Manifold.cylinder(y1 - y0, r, r, SEG)        # along +Z
    return c.rotate((-90, 0, 0)).translate((x, y0, z))  # +Z -> +Y

def cyl_z(x, y, r, z0, z1):
    return m3.Manifold.cylinder(z1 - z0, r, r, SEG).translate((x, y, z0))

def circ_pts(cx, cz, r, n=SEG):
    a = np.linspace(0, 2 * np.pi, n, endpoint=False)
    return list(zip(cx + r * np.cos(a), cz + r * np.sin(a)))

# --------------- panels (pockets / inserts), sketched in face coords (u=x, v=z) -------
def body_panel():
    x0, x1, z0, z1 = -W / 2 + 4.5, W / 2 - 4.5, 5.5, HS - 4.0
    c, xs = 4.0, x0 + 0.55 * (x1 - x0)
    step = 4.5
    return Polygon([(x0 + c, z0), (x1 - c, z0), (x1, z0 + c), (x1, z1 - step - c * 0.6),
                    (x1 - c * 0.6, z1 - step), (xs + step, z1 - step), (xs, z1),
                    (x0 + c, z1), (x0, z1 - c), (x0, z0 + c)])

def lid_panel():
    x0, x1, z0, z1 = -W / 2 + 4.5, W / 2 - 4.5, HS + 4.6, HS + HL - 3.6
    c = 3.0
    return Polygon(chrect(x0, x1, z0, z1, c))

def pocket_cut(poly, front=True):
    pts = list(poly.exterior.coords)[:-1]
    if front:
        return prism_xz(pts, -D / 2 - 1, -D / 2 + POCKET)
    return prism_xz(pts, D / 2 - POCKET, D / 2 + 1)

# ---------------- body ----------------
def build_body():
    b = chbox(-W / 2, W / 2, -D / 2, D / 2, 0, HS, cb=0.8)
    # hinge fin: full depth low, two lugs high
    zf = HS - 22.0
    fin_low = [(-W / 2 + 1, HS - 7), (XP - R_LOBE, HS - 7), (XP - R_LOBE, zf), (-W / 2 + 1, zf - (PX + R_LOBE))]
    finbox = chbox(XP - R_LOBE, 0, -D / 2, D / 2, -10, HS + 20, cv=1.5)
    b += prism_xz(fin_low, -D / 2, D / 2) ^ finbox
    lug_lo = [(-W / 2 + 1, HS - 7.01), (XP - R_LOBE, HS - 7.01), (XP - R_LOBE, ZP), (-W / 2 + 1, ZP)]
    for y0, y1 in [(-D / 2, -D / 2 + LUG_T), (D / 2 - LUG_T, D / 2)]:
        lug = prism_xz(circ_pts(XP, ZP, R_LOBE), y0, y1)
        lug += prism_xz([(XP - R_LOBE, HS - 7.01), (-W / 2 + 1, HS - 7.01), (-W / 2 + 1, HS), (XP - R_LOBE, HS)], y0, y1)
        lug += prism_xz([(XP - R_LOBE, HS), (-W / 2 - 0.4, HS), (-W / 2 - 0.4, ZP), (XP - R_LOBE, ZP)], y0, y1)
        b += lug ^ finbox
    # latch block right
    blk = [(W / 2 - 1, HS - 14 - (BLK + 1)), (W / 2 + BLK, HS - 14), (W / 2 + BLK, HS), (W / 2 - 1, HS)]
    b += prism_xz(blk, -D / 2, D / 2) ^ chbox(0, W / 2 + BLK, -D / 2, D / 2, -10, HS + 20, cv=CV)
    # lip ring
    lip = (chbox(-W_IN / 2 - LIP_T, W_IN / 2 + LIP_T, -D_IN / 2 - LIP_T, D_IN / 2 + LIP_T, HS - 1, HS + LIP_H, cv=0.6, ct=0.5)
           - chbox(-W_IN / 2, W_IN / 2, -D_IN / 2, D_IN / 2, HS - 2, HS + LIP_H + 1, cv=0.3))
    # no lip on the hinge side: the skirt swings through it otherwise (found by swing check)
    lip -= chbox(-W, -W_IN / 2 + 0.01, -D, D, HS - 0.5, HS + LIP_H + 1, cv=0.1)
    b += lip
    # cavity
    b -= chbox(-W_IN / 2, W_IN / 2, -D_IN / 2, D_IN / 2, FLOOR, HS + 10, cv=0.3)
    # pockets front & back (back mirrored so it reads right from behind)
    bp = body_panel()
    b -= pocket_cut(bp, True)
    b -= pocket_cut(Polygon([(-x, z) for x, z in bp.exterior.coords]), False)
    # hinge pin: clearance through front lug, tap hole in back lug
    b -= cyl_y(XP, ZP, PIN_CLR / 2, -D / 2 - 1, D / 2 - LUG_T)
    b -= cyl_y(XP, ZP, PIN_TAP / 2, D / 2 - LUG_T - 0.1, D / 2 + 1)
    # lanyard hole through the solid fin
    b -= cyl_y(XP + 0.3, zf + 3.5, 1.8, -D / 2 - 1, D / 2 + 1)
    # magnets (open pockets at seam, glue in)
    for sy in (-1, 1):
        b -= cyl_z(MAG_X, sy * MAG_Y, MAG_D / 2, HS - MAG_H, HS + 1)
    # thumb notch under lid on latch side
    b -= prism_xz([(W / 2 + BLK + 1, HS + 0.01), (W / 2 + BLK - 3.2, HS + 0.01), (W / 2 + BLK + 1, HS - 4.2)], -D / 2 - 1, D / 2 + 1)
    return b

# ---------------- lid ----------------
def build_lid():
    zt = HS + HL
    l = chbox(-W / 2, W / 2, -D / 2, D / 2, HS, zt, ct=1.6)
    finbox = chbox(XP - R_LOBE, 0, -D / 2, D / 2, HS - 10, zt + 5, cv=1.5)
    y0, y1 = -D / 2 + LUG_T + HGAP, D / 2 - LUG_T - HGAP
    kn = prism_xz(circ_pts(XP, ZP, R_LOBE), y0, y1)
    kn += prism_xz([(XP - R_LOBE, ZP), (-W / 2 + 1, ZP), (-W / 2 + 1, zt), (XP - R_LOBE + 3.0, zt), (XP - R_LOBE, zt - 3.0)], y0, y1)
    kn += prism_xz([(XP, HS), (-W / 2 + 1, HS), (-W / 2 + 1, ZP), (XP, ZP)], y0, y1)
    l += kn ^ finbox
    blk = [(W / 2 - 1, HS), (W / 2 + BLK, HS), (W / 2 + BLK, zt - 1.6), (W / 2 + BLK - 1.6, zt), (W / 2 - 1, zt)]
    l += prism_xz(blk, -D / 2, D / 2) ^ chbox(0, W / 2 + BLK, -D / 2, D / 2, HS - 10, zt + 10, cv=CV)
    # cavity + skirt over the lip
    l -= chbox(-W_IN / 2, W_IN / 2, -D_IN / 2, D_IN / 2, HS - 1, HS + STICK + 1.0, cv=0.3)
    o = LIP_T + GAP
    l -= chbox(-W_IN / 2 - o, W_IN / 2 + o, -D_IN / 2 - o, D_IN / 2 + o, HS - 1, HS + LIP_H + GAP, cv=0.6)
    lp = lid_panel()
    l -= pocket_cut(lp, True)
    l -= pocket_cut(Polygon([(-x, z) for x, z in lp.exterior.coords]), False)
    # three grip grooves on top (echo of the original's lid ridges)
    for gx in (-7, 0, 7):
        l -= chbox(gx - 0.8, gx + 0.8, -D / 2 + 3.0, D / 2 - 3.0, zt - 0.6, zt + 1, cv=0.4)
    l -= cyl_y(XP, ZP, PIN_CLR / 2, -D / 2 - 1, D / 2 + 1)
    for sy in (-1, 1):
        l -= cyl_z(MAG_X, sy * MAG_Y, MAG_D / 2, HS - 1, HS + MAG_H)
    return l

# ---------------- topo inserts ----------------
def field(seed):
    rng = np.random.default_rng(seed)
    hills = [(rng.uniform(-45, 45), rng.uniform(0, HS + HL), rng.uniform(9, 22), rng.uniform(-1, 1)) for _ in range(9)]
    def f(x, z):
        v = 0.012 * x + 0.006 * z
        for hx, hz, s, a in hills:
            v = v + a * np.exp(-((x - hx) ** 2 + (z - hz) ** 2) / (2 * s * s))
        return v
    return f

def topo_lines(region, f, n_levels=24, w=0.7, w_idx=1.3, margin=1.0):
    minx, minz, maxx, maxz = region.bounds
    res = 0.2
    xs = np.arange(minx - 2, maxx + 2, res); zs = np.arange(minz - 2, maxz + 2, res)
    X, Z = np.meshgrid(xs, zs)
    F = f(X, Z)
    lo, hi = np.percentile(F, 2), np.percentile(F, 98)
    gF = field_full_range[1]
    levels = np.linspace(field_full_range[0], field_full_range[1], n_levels)
    shapes = []
    inner = region.buffer(-margin, join_style=2)
    for i, lv in enumerate(levels):
        for c in measure.find_contours(F, lv):
            pts = [(xs[0] + p[1] * res, zs[0] + p[0] * res) for p in c]
            if len(pts) < 2: continue
            ls = LineString(pts).simplify(0.05)
            if ls.length < 6: continue
            shapes.append(ls.buffer((w_idx if i % 5 == 0 else w) / 2, cap_style=1, join_style=1, quad_segs=4))
    lines = unary_union(shapes).intersection(inner)
    # cartographic neatline
    neat = region.buffer(-0.35, join_style=2).difference(region.buffer(-1.15, join_style=2))
    out = unary_union([lines, neat]).buffer(0)
    out = MultiPolygon([p for p in getattr(out, 'geoms', [out]) if p.area > 0.4])
    return out

def shapely_to_cs(geom):
    polys = getattr(geom, 'geoms', [geom])
    contours = []
    for p in polys:
        contours.append(np.array(p.exterior.coords[:-1]))
        for h in p.interiors:
            contours.append(np.array(h.coords[:-1]))
    return m3.CrossSection(contours, m3.FillRule.EvenOdd)

def build_insert(panel, f, mirror=False):
    """Returns (base, lines) lying flat, face up, origin at panel centre. Base in green, lines in yellow."""
    region = panel.buffer(-0.15, join_style=2)
    lines = topo_lines(region, f)
    if mirror:
        from shapely import affinity
        region = affinity.scale(region, -1, 1, origin=(0, 0)); lines = affinity.scale(lines, -1, 1, origin=(0, 0))
    base = shapely_to_cs(region).extrude(POCKET)
    raised = shapely_to_cs(lines).extrude(0.5).translate((0, 0, POCKET))
    cx, cy = region.centroid.x, region.centroid.y
    return base.translate((-cx, -cy, 0)), raised.translate((-cx, -cy, 0))

field_full_range = (-0.6, 1.8)

if __name__ == '__main__':
    import sys, pickle
    body, lid = build_body(), build_lid()
    fF, fB = field(7), field(23)
    # calibrate contour levels to the combined front surface range
    xs = np.linspace(-W / 2, W / 2, 200); zs = np.linspace(0, HS + HL, 200)
    X, Z = np.meshgrid(xs, zs)
    out = {'body': body, 'lid': lid}
    for name, f in (('front', fF), ('back', fB)):
        F = f(X, Z); field_full_range = (np.percentile(F, 1), np.percentile(F, 99))
        out[f'ins_body_{name}'] = build_insert(body_panel(), f, mirror=False)
        out[f'ins_lid_{name}'] = build_insert(lid_panel(), f, mirror=False)
    for k, v in out.items():
        if isinstance(v, tuple):
            print(k, [round(x.volume(), 1) for x in v], v[0].bounding_box())
        else:
            print(k, round(v.volume(), 1), v.bounding_box(), 'genus', v.genus())
