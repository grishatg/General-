"""v3 concepts - 55 (W) x 13 (D) x 85 (H) mm, roll-ups <= 60 mm long, 5-6 mm dia.
Mechanisms: BOOK (spine-hinged clamshell) and CAP (friction pull-off cap).
Surfaces (all flush unless the pattern is a deliberate grip texture):
  topo    - flush yellow contour inlay
  knurl   - JanBerry-style raised pyramid knurl in a recessed panel (tips flush with the face) + flush yellow frame with notch
  hazard  - flush yellow chevron band + recessed MOLLE slots
  grid    - flush yellow map grid, crosshair and tick marks
"""
import numpy as np, manifold3d as m3, sys, os
sys.path.insert(0, os.path.dirname(__file__))
import case as K
from shapely.geometry import Polygon, LineString, MultiPolygon, Point, box as sbox
from shapely.ops import unary_union
from shapely import affinity
from skimage import measure

W, D, H = 55.0, 13.0, 85.0
RD, RL = 6.0, 60.0          # roll-up max diameter / length
INL = 0.6                   # inlay depth (3 layers @ 0.2)
CV = 1.6
chbox, prism_xz, cyl_y, cyl_z = K.chbox, K.prism_xz, K.cyl_y, K.cyl_z

# ---------------- face mapping ----------------
def to_face(man, side, ty):
    if side == 'f': M = np.array([[1, 0, 0, 0], [0, 0, -1, ty], [0, 1, 0, 0]], float)
    else:           M = np.array([[-1, 0, 0, 0], [0, 0, 1, ty], [0, 1, 0, 0]], float)
    return man.transform(M)

def cs(geom):
    geom = geom.buffer(0)
    if geom.is_empty: return None
    return K.shapely_to_cs(geom)

def inlay(shell, geom, side, depth=INL):
    """Cut a flush inlay; returns (shell_cut, yellow_solid)."""
    c = cs(geom)
    if c is None: return shell, None
    t = c.extrude(depth + 0.5)
    ty = (-D / 2 + depth) if side == 'f' else (D / 2 - depth)
    cut = to_face(t, side, ty)
    yel = cut ^ shell
    return shell - cut, yel

def recess(shell, geom, side, depth):
    c = cs(geom)
    if c is None: return shell
    ty = (-D / 2 + depth) if side == 'f' else (D / 2 - depth)
    return shell - to_face(c.extrude(depth + 0.5), side, ty)

# ---------------- surface patterns (face coords u=x as seen, v=z) ----------------
def field(seed):
    rng = np.random.default_rng(seed)
    hills = [(rng.uniform(-30, 30), rng.uniform(0, H), rng.uniform(7, 16), rng.uniform(-1, 1)) for _ in range(8)]
    def f(x, z):
        v = 0.015 * x + 0.008 * z
        for hx, hz, s, a in hills: v = v + a * np.exp(-((x - hx) ** 2 + (z - hz) ** 2) / (2 * s * s))
        return v
    X, Z = np.meshgrid(np.linspace(-W / 2, W / 2, 150), np.linspace(0, H, 150)); F = f(X, Z)
    return f, (np.percentile(F, 1), np.percentile(F, 99))

def pat_topo(region, seed=5, n=24, w=0.7, wi=1.2):
    f, rng = field(seed)
    x0, z0, x1, z1 = region.bounds; res = 0.2
    xs = np.arange(x0 - 2, x1 + 2, res); zs = np.arange(z0 - 2, z1 + 2, res)
    X, Z = np.meshgrid(xs, zs); F = f(X, Z); sh = []
    for i, lv in enumerate(np.linspace(rng[0], rng[1], n)):
        for c in measure.find_contours(F, lv):
            ls = LineString([(xs[0] + p[1] * res, zs[0] + p[0] * res) for p in c]).simplify(0.05)
            if ls.length > 5: sh.append(ls.buffer((wi if i % 5 == 0 else w) / 2, quad_segs=4))
    g = unary_union(sh).intersection(region)
    return MultiPolygon([p for p in getattr(g, 'geoms', [g]) if p.area > 0.3])

def pat_grid(region, pitch=9.0, w=0.6):
    x0, z0, x1, z1 = region.bounds; sh = []
    for x in np.arange(np.ceil(x0 / pitch) * pitch, x1, pitch): sh.append(sbox(x - w / 2, z0, x + w / 2, z1))
    for z in np.arange(np.ceil(z0 / pitch) * pitch, z1, pitch): sh.append(sbox(x0, z - w / 2, x1, z + w / 2))
    for x in np.arange(np.ceil(x0 / (pitch / 3)) * pitch / 3, x1, pitch / 3):   # ticks along the bottom edge
        sh.append(sbox(x - 0.25, z0, x + 0.25, z0 + (2.5 if abs(x / pitch - round(x / pitch)) < 1e-6 else 1.3)))
    cx, cz = (x0 + x1) / 2 + 4.5, (z0 + z1) / 2 + 9
    ring = Point(cx, cz).buffer(6.0).difference(Point(cx, cz).buffer(5.1))
    sh += [ring, sbox(cx - 0.45, cz - 9, cx + 0.45, cz + 9), sbox(cx - 9, cz - 0.45, cx + 9, cz + 0.45)]
    g = unary_union(sh).difference(Point(cx, cz).buffer(1.2)).union(Point(cx, cz).buffer(0.6)).intersection(region)
    return g

def pat_chevron(band, pitch=6.0, w=2.6, slope=1.0):
    x0, z0, x1, z1 = band.bounds; hgt = z1 - z0; sh = []
    for x in np.arange(x0 - hgt * 2, x1 + hgt, pitch):
        sh.append(Polygon([(x, z0), (x + w, z0), (x + w + hgt * slope, z1), (x + hgt * slope, z1)]))
    return unary_union(sh).intersection(band)

def frame_line(poly, w=1.0, inset=0.0):
    return poly.buffer(-inset, join_style=2).difference(poly.buffer(-inset - w, join_style=2))

def notched_panel(x0, x1, z0, z1, c=3.0, step=3.5, at=0.55):
    xs = x0 + at * (x1 - x0)
    return Polygon([(x0 + c, z0), (x1 - c, z0), (x1, z0 + c), (x1, z1 - step - c * .6), (x1 - c * .6, z1 - step),
                    (xs + step, z1 - step), (xs, z1), (x0 + c, z1), (x0, z1 - c), (x0, z0 + c)])

def knurl(shell, panel, side, depth=0.9, pitch=2.2, base=2.1):
    """Recess the panel, then fill with pyramids whose tips sit flush with the face (JanBerry signature texture)."""
    shell = recess(shell, panel, side, depth)
    inner = panel.buffer(-0.5, join_style=2)
    x0, z0, x1, z1 = inner.bounds; pyr = []
    h = base / 2
    unit = m3.Manifold.hull_points(np.array([[-h, 0, 0], [h, 0, 0], [0, -h, 0], [0, h, 0], [0, 0, depth]], float))
    for j, z in enumerate(np.arange(z0 + h, z1 - h + 1e-6, pitch / 2)):
        off = (pitch / 2) if j % 2 else 0.0
        for x in np.arange(x0 + h + off, x1 - h + 1e-6, pitch):
            if inner.contains(Point(x, z).buffer(h * 0.75)): pyr.append(unit.translate((x, z, 0)))
    P = m3.Manifold.compose(pyr)
    ty = (-D / 2 + depth) if side == 'f' else (D / 2 - depth)
    return shell + to_face(P, side, ty)

# ================= BOOK : spine-hinged clamshell =================
BK = dict(TC=2.6, WB=2.0, WS=2.0, R=2.4, G=0.3)
def book(surface='topo', seed=(5, 11)):
    TC, WB, WS, R, G = BK['TC'], BK['WB'], BK['WS'], BK['R'], BK['G']
    ys = -D / 2 + TC                          # split plane
    XA, YA = -W / 2 + R, -D / 2 + R           # hinge axis (along Z)
    segs = [(0, 16), (16, 34), (34, 51), (51, 69), (69, 85)]   # T C T C T
    own = ['T', 'C', 'T', 'C', 'T']
    env = chbox(-W / 2, W / 2, -D / 2, D / 2, 0, H, cv=0.8, cb=0.8, ct=0.8)
    # tray
    tray = env ^ chbox(-W, W, ys, D, -1, H + 1, cv=0.1)
    tray -= chbox(-W / 2 + WS, W / 2 - WS, ys - 1, D / 2 - WB, 6.0, H - 2.0, cv=0.4)       # cavity (6 mm bottom block for magnets)
    tray += chbox(-W / 2 + WS, W / 2 - WS, ys + 1.6, D / 2 - WB, 66.0, 67.4, cv=0.1)        # divider: roll-ups below, tips bay above
    tray += chbox(W / 2 - WS - 7, W / 2 - WS, ys, D / 2 - WB, H - 9, H - 2, cv=0.1)         # magnet pillar top-right
    cover = env ^ chbox(-W, W, -D, ys, -1, H + 1, cv=0.1)
    lip = chbox(-W / 2 + WS + 0.8, W / 2 - WS - 0.2, ys - 0.5, ys + 1.4, 6.2, H - 2.2, cv=0.5) - \
          chbox(-W / 2 + WS + 1.2, W / 2 - WS - 1.2, ys - 1, ys + 2, 7.2, H - 3.2, cv=0.3)
    lip -= chbox(W / 2 - WS - 7.3, W / 2, ys - 1, ys + 3, H - 9.3, H, cv=0.1)
    cover += lip
    # hinge: barrel spine
    pinhole = m3.Manifold.cylinder(H + 2, 0.95, 0.95, 32).translate((XA, YA, -1))
    for (z0, z1), o in zip(segs, own):
        g0, g1 = (z0 + (G if z0 > 0 else 0)), (z1 - (G if z1 < H else 0))
        barrel = m3.Manifold.cylinder(g1 - g0, R, R, 48).translate((XA, YA, g0)) ^ env
        clear = m3.Manifold.cylinder(z1 - z0 + (2 * G if 0 < z0 else G), R + G, R + G, 48).translate((XA, YA, z0 - (G if z0 > 0 else 1)))
        web = chbox(XA, XA + R + 1.5, YA - R, YA + R, g0, g1, cv=0.1) ^ env
        if o == 'T':
            cover -= clear; tray += barrel + (web ^ chbox(-W, W, ys, D, -1, H + 1, cv=0.1))
            tray += chbox(-W / 2, XA, ys, D / 2 - WB + 0.1, g0, g1, cv=0.1) ^ env
        else:
            tray -= clear; cover += barrel + (web ^ chbox(-W, W, -D, ys, -1, H + 1, cv=0.1))
    tray -= pinhole; cover -= pinhole
    keep = (chbox(XA, W, -D, D, -1, H + 1, cv=0.1) + m3.Manifold.cylinder(H + 2, R, R, 48).translate((XA, YA, -1)))
    cover = cover ^ keep
    sweep = []
    for a in range(2, 168, 2):
        sweep.append(cover.translate((-XA, -YA, 0)).rotate((0, 0, -a)).translate((XA, YA, 0)))
    SW = m3.Manifold.batch_boolean(sweep, m3.OpType.Add)
    tray = tray - SW
    # spine-side corners: tray wall must clear the cover knuckle sweep
    # magnets 5x2 (axis Y): bottom-right block + top-right pillar, matching pockets in the cover
    for z in (3.0, H - 5.5):
        tray -= m3.Manifold.cylinder(2.1, 2.6, 2.6, 32).rotate((90, 0, 0)).translate((W / 2 - WS - 3.5, ys + 2.1 - 0.0, z))
        cover -= m3.Manifold.cylinder(2.1, 2.6, 2.6, 32).rotate((-90, 0, 0)).translate((W / 2 - WS - 3.5, ys - 2.1, z))
    # thumb notch on the opening edge
    cover -= prism_xz([(W / 2 + 1, 30), (W / 2 + 1, 55), (W / 2 - 2.2, 42.5)], ys - 1.2, ys + 0.01)
    yel = []
    fp = Polygon(K.chrect(XA + R + 1.2, W / 2 - 2.5, 2.5, H - 2.5, 3.0))
    bp = Polygon(K.chrect(-W / 2 + 2.5, W / 2 - R * 2 - 1.2, 2.5, H - 2.5, 3.0))   # back face (viewer coords) - spine on the right
    for part, poly, side, sd in (('cover', fp, 'f', seed[0]), ('tray', bp, 'b', seed[1])):
        sh = cover if part == 'cover' else tray
        if surface == 'topo':
            sh, y = inlay(sh, pat_topo(poly.buffer(-0.2), sd).union(frame_line(poly, 0.8)), side)
        elif surface == 'knurl':
            inner = notched_panel(*poly.buffer(-4, join_style=2).bounds)
            sh = knurl(sh, inner, side)
            sh, y = inlay(sh, frame_line(inner.buffer(1.6, join_style=2), 1.0), side)
        elif surface == 'grid':
            sh, y = inlay(sh, pat_grid(poly).union(frame_line(poly, 0.8)), side)
        if part == 'cover': cover = sh
        else: tray = sh
        if y is not None: yel.append(y)
    # yellow accent: the cover's middle barrel segment as a separate yellow sleeve
    z0, z1 = segs[2]
    sleeve = m3.Manifold.cylinder(z1 - z0 - 2 * G, R, R, 48).translate((XA, YA, z0 + G)) - \
             m3.Manifold.cylinder(H, R - 0.8, R - 0.8, 48).translate((XA, YA, -1))
    sleeve = sleeve ^ env
    tray -= sleeve
    yel.append(sleeve)
    return dict(name=f'BOOK_{surface}', parts={'tray': tray, 'cover': cover}, yellow=yel,
                axis=(XA, YA), cavity=(-W / 2 + WS, W / 2 - WS, ys, D / 2 - WB))

# ================= CAP : friction pull-off cap =================
def cap(surface='knurl', seed=(5, 11)):
    WS, WF = 3.0, 2.0; CW = W - 2 * WS; DC = D - 2 * WF
    SEAM, NECK, GAP, CAPW = 40.0, 7.0, 0.15, 0.9
    o = GAP + CAPW
    env = chbox(-W / 2, W / 2, -D / 2, D / 2, 0, H, cv=CV, cb=0.6, ct=1.4)
    body = chbox(-W / 2, W / 2, -D / 2, D / 2, 0, SEAM, cv=CV, cb=0.6)
    body += chbox(-W / 2 + o, W / 2 - o, -D / 2 + o, D / 2 - o, SEAM - 0.5, SEAM + NECK, cv=max(CV - o, 0.3), ct=0.4)
    for sx in (-1, 1):
        body += m3.Manifold.sphere(1.0, 24).scale((0.3, 1.6, 1.0)).translate((sx * (W / 2 - o), 0, SEAM + 3.5))
    body -= chbox(-CW / 2, CW / 2, -DC / 2, DC / 2, 1.6, H, cv=0.3)
    capm = chbox(-W / 2, W / 2, -D / 2, D / 2, SEAM, H, cv=CV, ct=1.4)
    capm -= chbox(-W / 2 + o - GAP, W / 2 - o + GAP, -D / 2 + o - GAP, D / 2 - o + GAP, SEAM - 1, SEAM + NECK + GAP, cv=max(CV - o, 0.3) + 0.1)
    capm -= chbox(-CW / 2, CW / 2, -DC / 2, DC / 2, SEAM, H - 1.6, cv=0.3)
    for sx in (-1, 1):
        capm -= m3.Manifold.sphere(1.0, 24).scale((0.35, 1.8, 1.15)).translate((sx * (W / 2 - o + GAP), 0, SEAM + 3.5))
    for x in (-5, 0, 5):
        capm -= chbox(x - 0.7, x + 0.7, -D / 2 + 2.5, D / 2 - 2.5, H - 0.5, H + 1, cv=0.3)
    yel = []
    bpan = notched_panel(-W / 2 + 4, W / 2 - 4, 4.5, SEAM - 4.0)
    cpan = Polygon(K.chrect(-W / 2 + 4, W / 2 - 4, SEAM + NECK + 3.0, H - 4.0, 3.0))
    for side in ('f', 'b'):
        if surface == 'knurl':
            body = knurl(body, bpan, side); capm = knurl(capm, cpan, side)
            body, y1 = inlay(body, frame_line(bpan.buffer(1.6, join_style=2), 1.0), side)
            capm, y2 = inlay(capm, frame_line(cpan.buffer(1.6, join_style=2), 1.0), side)
        elif surface == 'hazard':
            band = sbox(-W / 2 + 2.5, SEAM - 13, W / 2 - 2.5, SEAM - 4)
            body, y1 = inlay(body, pat_chevron(band).union(frame_line(band.buffer(0.9, join_style=2), 0.7)), side)
            band2 = sbox(-W / 2 + 2.5, SEAM + NECK + 3.5, W / 2 - 2.5, SEAM + NECK + 12.5)
            capm, y2 = inlay(capm, pat_chevron(band2).union(frame_line(band2.buffer(0.9, join_style=2), 0.7)), side)
            for z in np.arange(6.0, SEAM - 16, 5.5):                     # MOLLE-style slots (recessed, green)
                for x0 in (-W / 2 + 5, 3.0):
                    body = recess(body, Polygon(K.chrect(x0, x0 + 19, z, z + 2.4, 0.8)), side, 0.8)
            for z in np.arange(SEAM + NECK + 16, H - 6, 5.5):
                for x0 in (-W / 2 + 5, 3.0):
                    capm = recess(capm, Polygon(K.chrect(x0, x0 + 19, z, z + 2.4, 0.8)), side, 0.8)
        elif surface == 'topo':
            body, y1 = inlay(body, pat_topo(bpan, seed[0]).union(frame_line(bpan, 0.8)), side)
            capm, y2 = inlay(capm, pat_topo(cpan, seed[0]).union(frame_line(cpan, 0.8)), side)
        elif surface == 'grid':
            body, y1 = inlay(body, pat_grid(bpan).union(frame_line(bpan, 0.8)), side)
            capm, y2 = inlay(capm, pat_grid(cpan).union(frame_line(cpan, 0.8)), side)
        yel += [y for y in (y1, y2) if y is not None]
    return dict(name=f'CAP_{surface}', parts={'body': body, 'cap': capm}, yellow=yel,
                lift=SEAM, cavity=(-CW / 2, CW / 2, -DC / 2, DC / 2))

def rollups(cav, n=None, d=RD, z0=None):
    x0, x1, y0, y1 = cav
    n = n or int((x1 - x0) // d)
    sx = x0 + ((x1 - x0) - n * d) / 2 + d / 2
    yc = y1 - d / 2 - 0.3 if z0 is not None else (y0 + y1) / 2
    zb = z0 if z0 is not None else 1.6
    return [m3.Manifold.cylinder(RL, d / 2 - 0.05, d / 2 - 0.05, 32).translate((sx + i * d, yc, zb)) for i in range(n)]
