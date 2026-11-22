"""Three concept cases in a strict 55 (W) x 13 (D) x 85 (H) mm envelope.
Holds 6 cigarettes, 8 mm dia, up to 80 mm long (king size 84-85 mm will NOT fit 85 mm outside height).
A  Ridgeline  - pull-off cap, friction + detent bumps
B  Switchback - side-swivel lid on an internal corner pin (Hiking Container hinge, shrunk inside the envelope)
C  Summit     - pull-off cap on a slanted ridgeline seam
"""
import numpy as np, manifold3d as m3, sys, os
sys.path.insert(0, os.path.dirname(__file__))
import case as K
from shapely.geometry import Polygon, LineString, MultiPolygon
from shapely.ops import unary_union
from skimage import measure

W, D, H = 55.0, 13.0, 85.0
CIG_D, CIG_L, N = 8.0, 80.0, 6
FLOOR, TOP = 1.6, 1.6
WF = 2.0                # front/back wall
POCK = 1.0              # insert pocket depth (insert 0.6 base + 0.4 flush lines)
DC = D - 2 * WF         # 9.0 cavity depth
CV = 1.6                # vertical edge chamfer
CIG_TOP = FLOOR + CIG_L
chbox, prism_xz, cyl_y, cyl_z = K.chbox, K.prism_xz, K.cyl_y, K.cyl_z

def cav(x0, x1, z0, z1, d=DC):
    return chbox(x0, x1, -d / 2, d / 2, z0, z1, cv=0.3)

def pockets(poly, which=('f', 'b')):
    out = []
    pts = list(poly.exterior.coords)[:-1]
    if 'f' in which: out.append(prism_xz(pts, -D / 2 - 1, -D / 2 + POCK))
    if 'b' in which: out.append(prism_xz([(-x, z) for x, z in pts], D / 2 - POCK, D / 2 + 1))
    return out

def chpoly(x0, x1, z0, z1, c):
    return Polygon(K.chrect(x0, x1, z0, z1, c))

def step_poly(x0, x1, z0, z1, c, step, at=0.55, top=True):
    xs = x0 + at * (x1 - x0)
    if top:
        return Polygon([(x0 + c, z0), (x1 - c, z0), (x1, z0 + c), (x1, z1 - step - c * .6), (x1 - c * .6, z1 - step),
                        (xs + step, z1 - step), (xs, z1), (x0 + c, z1), (x0, z1 - c), (x0, z0 + c)])
    return Polygon([(x0 + c, z0), (xs, z0), (xs + step, z0 + step), (x1 - c * .6, z0 + step), (x1, z0 + step + c * .6),
                    (x1, z1 - c), (x1 - c, z1), (x0 + c, z1), (x0, z1 - c), (x0, z0 + c)])

# ---------------- topo insert ----------------
def field(seed):
    rng = np.random.default_rng(seed)
    hills = [(rng.uniform(-30, 30), rng.uniform(0, H), rng.uniform(7, 16), rng.uniform(-1, 1)) for _ in range(8)]
    def f(x, z):
        v = 0.015 * x + 0.008 * z
        for hx, hz, s, a in hills: v = v + a * np.exp(-((x - hx) ** 2 + (z - hz) ** 2) / (2 * s * s))
        return v
    X, Z = np.meshgrid(np.linspace(-W / 2, W / 2, 150), np.linspace(0, H, 150))
    F = f(X, Z); return f, (np.percentile(F, 1), np.percentile(F, 99))

def topo(region, f, rng, n=22, w=0.65, wi=1.2):
    x0, z0, x1, z1 = region.bounds; res = 0.2
    xs = np.arange(x0 - 2, x1 + 2, res); zs = np.arange(z0 - 2, z1 + 2, res)
    X, Z = np.meshgrid(xs, zs); F = f(X, Z)
    sh = []
    for i, lv in enumerate(np.linspace(rng[0], rng[1], n)):
        for c in measure.find_contours(F, lv):
            ls = LineString([(xs[0] + p[1] * res, zs[0] + p[0] * res) for p in c]).simplify(0.05)
            if ls.length > 5: sh.append(ls.buffer((wi if i % 5 == 0 else w) / 2, quad_segs=4))
    lines = unary_union(sh).intersection(region.buffer(-0.9, join_style=2))
    neat = region.buffer(-0.3, join_style=2).difference(region.buffer(-1.0, join_style=2))
    g = unary_union([lines, neat]).buffer(0)
    return MultiPolygon([p for p in getattr(g, 'geoms', [g]) if p.area > 0.3])

def insert(panel, f, rng, base=0.6, line=0.4):
    region = panel.buffer(-0.15, join_style=2)
    L = topo(region, f, rng)
    b = K.shapely_to_cs(region).extrude(base)
    y = K.shapely_to_cs(L).extrude(line).translate((0, 0, base))
    return b, y, (0.0, 0.0)   # geometry already in face coords

def place(man, c, side):
    cx, cz = c
    if side == 'f': M = np.array([[1, 0, 0, cx], [0, 0, -1, -D / 2 + POCK], [0, 1, 0, cz]], float)
    else:           M = np.array([[-1, 0, 0, -cx], [0, 0, 1, D / 2 - POCK], [0, 1, 0, cz]], float)
    return man.transform(M)

def grooves(zt, xs=(-5, 0, 5)):
    return [chbox(x - 0.7, x + 0.7, -D / 2 + 2.5, D / 2 - 2.5, zt - 0.5, zt + 1, cv=0.3) for x in xs]

# ================= A  RIDGELINE : pull-off cap =================
def design_A():
    WS = 3.0; CW = W - 2 * WS              # 49 cavity
    SEAM, NECK, GAP, CAPW = 60.0, 7.0, 0.15, 0.9
    o = GAP + CAPW
    body = chbox(-W / 2, W / 2, -D / 2, D / 2, 0, SEAM, cv=CV, cb=0.6)
    neck = chbox(-W / 2 + o, W / 2 - o, -D / 2 + o, D / 2 - o, SEAM - 0.5, SEAM + NECK, cv=max(CV - o, 0.3), ct=0.4)
    body += neck
    for sx in (-1, 1):                     # detent bumps on the thick side walls
        body += m3.Manifold.sphere(1.0, 24).scale((0.3, 1.6, 1.0)).translate((sx * (W / 2 - o), 0, SEAM + 3.5))
    body -= cav(-CW / 2, CW / 2, FLOOR, SEAM + NECK + 5)
    bp = step_poly(-W / 2 + 3.5, W / 2 - 3.5, 4.0, SEAM - 3.5, 3.0, 3.5)
    for p in pockets(bp): body -= p
    cap = chbox(-W / 2, W / 2, -D / 2, D / 2, SEAM, H, cv=CV, ct=1.4)
    cap -= chbox(-W / 2 + o - GAP, W / 2 - o + GAP, -D / 2 + o - GAP, D / 2 - o + GAP, SEAM - 1, SEAM + NECK + GAP, cv=max(CV - o, 0.3) + 0.1)
    cap -= cav(-CW / 2, CW / 2, SEAM, H - TOP)
    for sx in (-1, 1):
        cap -= m3.Manifold.sphere(1.0, 24).scale((0.35, 1.8, 1.15)).translate((sx * (W / 2 - o + GAP), 0, SEAM + 3.5))
    lp = chpoly(-W / 2 + 3.5, W / 2 - 3.5, SEAM + NECK + 1.5, H - 3.0, 2.5)
    for p in pockets(lp): cap -= p
    for g in grooves(H): cap -= g
    return dict(name='A_Ridgeline', body=body, lid=cap, panels={'body': bp, 'lid': lp},
                lid_motion=('lift', 30.0), seam=SEAM, cavity=CW)

# ================= B  SWITCHBACK : side-swivel lid =================
def design_B(STICK=12.0, WL=4.0, R=1.8):
    WR = 1.8; CW = W - WL - WR
    cx0 = -W / 2 + WL
    SEAM = CIG_TOP - STICK
    G = 0.3
    PX, PZ = -W / 2 + R, SEAM
    LIP_H, LIP_T, LG = 2.5, 0.8, 0.15
    body = chbox(-W / 2, W / 2, -D / 2, D / 2, 0, SEAM, cv=CV, cb=0.6)
    lip = chbox(cx0, W / 2 - WR + LIP_T, -DC / 2 - LIP_T, DC / 2 + LIP_T, SEAM - 0.5, SEAM + LIP_H, cv=0.5, ct=0.4)
    body += lip
    # body hinge lugs (front & back layers) = rounded corner around the pin
    lug_y = [(-D / 2, -2.0 - G), (2.0 + G, D / 2)]
    for y0, y1 in lug_y:
        body += prism_xz(K.circ_pts(PX, PZ, R), y0, y1) ^ chbox(-W / 2, 0, -D / 2, D / 2, 0, H, cv=CV)
    body -= cav(cx0, W / 2 - WR, FLOOR, SEAM + 10)
    # clear the middle layer around the pin for the lid knuckle
    body -= prism_xz(K.circ_pts(PX, PZ, R + G), -2.0 - G, 2.0 + G)
    bp = step_poly(-W / 2 + 6.0, W / 2 - 3.5, 4.0, SEAM - 3.5, 3.0, 3.5)
    for p in pockets(bp): body -= p
    body -= cyl_y(PX, PZ, 1.05, -D / 2 - 1, D / 2 + 1)        # M2 x 12 screw / 1.75 filament pin (ream to fit)
    # lid
    lid = chbox(-W / 2, W / 2, -D / 2, D / 2, SEAM, H, cv=CV, ct=1.4)
    lid -= prism_xz(K.circ_pts(PX, PZ, R + G, 48), -D / 2 - 1, D / 2 + 1)     # clearance ring...
    lid += prism_xz(K.circ_pts(PX, PZ, R), -2.0, 2.0) ^ chbox(-W / 2, 0, -D / 2, D / 2, SEAM - 5, H, cv=CV)  # ...knuckle in middle layer
    lid += prism_xz([(PX, PZ), (PX, PZ + R), (-W / 2 + WL + 1, PZ + R), (-W / 2 + WL + 1, PZ)], -2.0, 2.0)
    lid -= cav(cx0, W / 2 - WR, SEAM - 1, H - TOP)
    o = LIP_T + LG
    lid -= chbox(cx0, W / 2 - WR + o, -DC / 2 - o, DC / 2 + o, SEAM - 1, SEAM + LIP_H + LG, cv=0.5)
    lid -= cyl_y(PX, PZ, 1.05, -D / 2 - 1, D / 2 + 1)
    lp = chpoly(-W / 2 + 6.0, W / 2 - 3.5, SEAM + LIP_H + 1.5, H - 3.0, 2.0)
    for p in pockets(lp): lid -= p
    for g in grooves(H, (2, 7, 12)): lid -= g
    return dict(name='B_Switchback', body=body, lid=lid, panels={'body': bp, 'lid': lp},
                lid_motion=('swivel', (PX, PZ), 80.0), seam=SEAM, cavity=CW, cx=(cx0 + W / 2 - WR) / 2)

# ================= C  SUMMIT : pull-off cap on a slanted ridgeline seam =================
def design_C():
    WS = 3.0; CW = W - 2 * WS
    ZL, ZR = 54.0, 66.0                      # seam height at left / right (ridge)
    NECK, GAP, CAPW = 7.0, 0.15, 0.9
    o = GAP + CAPW
    zf = lambda x, dz=0.0: ZL + (ZR - ZL) * (x + W / 2) / W + dz
    def below(dz, pad=1.0):                  # solid below the slanted seam (+dz)
        return prism_xz([(-W, -5), (W, -5), (W, zf(W, dz)), (-W, zf(-W, dz))], -D, D)
    env = chbox(-W / 2, W / 2, -D / 2, D / 2, 0, H, cv=CV, cb=0.6, ct=1.4)
    inner = chbox(-W / 2 + o, W / 2 - o, -D / 2 + o, D / 2 - o, 0, H, cv=max(CV - o, 0.3))
    body = (env ^ below(0)) + (inner ^ below(NECK) - below(-0.5))
    for sx in (-1, 1):
        body += m3.Manifold.sphere(1.0, 24).scale((0.3, 1.6, 1.0)).translate((sx * (W / 2 - o), 0, zf(sx * W / 2, 3.5)))
    body -= cav(-CW / 2, CW / 2, FLOOR, H + 5)
    x0, x1 = -W / 2 + 3.5, W / 2 - 3.5
    bp = Polygon([(x0 + 3, 4), (x1 - 3, 4), (x1, 7), (x1, zf(x1, -3.5) - 2.5), (x1 - 2.5, zf(x1 - 2.5, -3.5)),
                  (x0 + 2.5, zf(x0 + 2.5, -3.5)), (x0, zf(x0, -3.5) - 2.5), (x0, 7)])
    for p in pockets(bp): body -= p
    gapcut = chbox(-W / 2 + o - GAP, W / 2 - o + GAP, -D / 2 + o - GAP, D / 2 - o + GAP, -5, H + 5, cv=max(CV - o, 0.3) + 0.1) ^ below(NECK + GAP)
    cap = env - below(0) - gapcut
    cap -= cav(-CW / 2, CW / 2, 0, H - TOP)
    for sx in (-1, 1):
        cap -= m3.Manifold.sphere(1.0, 24).scale((0.35, 1.8, 1.15)).translate((sx * (W / 2 - o + GAP), 0, zf(sx * W / 2, 3.5)))
    lp = Polygon([(x0 + 2.5, zf(x0 + 2.5, NECK + 1.5)), (x1, zf(x1, NECK + 1.5) + 2.5 * 0), (x1, H - 5.0), (x1 - 2.0, H - 3.0),
                  (x0 + 2.0, H - 3.0), (x0, H - 5.0), (x0, zf(x0, NECK + 1.5) + 2.5)])
    for p in pockets(lp): cap -= p
    for g in grooves(H): cap -= g
    return dict(name='C_Summit', body=body, lid=cap, panels={'body': bp, 'lid': lp},
                lid_motion=('lift', 32.0), seam=ZL, cavity=CW)

def inserts(d, seeds=(5, 11)):
    out = []
    for side, seed in zip(('f', 'b'), seeds):
        f, rng = field(seed)
        for part in ('body', 'lid'):
            b, y, c = insert(d['panels'][part], f, rng)
            out.append(dict(part=part, side=side, base=b, lines=y, c=c))
    return out

def cigs(d):
    cw = d['cavity']; x0 = d.get('cx', 0) - cw / 2 + (cw - N * CIG_D) / 2
    return m3.Manifold.batch_boolean([m3.Manifold.cylinder(CIG_L, CIG_D / 2 - 0.05, CIG_D / 2 - 0.05, 40)
                                      .translate((x0 + CIG_D / 2 + i * CIG_D, 0, FLOOR)) for i in range(N)], m3.OpType.Add)

if __name__ == '__main__':
    for fn in (design_A, design_B, design_C):
        d = fn(); b, l = d['body'], d['lid']
        bb = (b + l).bounding_box()
        print(d['name'], 'env', [round(bb[3] - bb[0], 2), round(bb[4] - bb[1], 2), round(bb[5] - bb[2], 2)],
              'vol', round(b.volume()), round(l.volume()), 'overlap', round((b ^ l).volume(), 3),
              'cigs vs body', round((cigs(d) ^ b).volume(), 3), 'vs lid', round((cigs(d) ^ l).volume(), 3))
