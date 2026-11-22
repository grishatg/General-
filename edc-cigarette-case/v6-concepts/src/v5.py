"""v5 BOOK - review-driven revision of v4 (agent research + independent ID critique + user brief).
55 x 13 x 85 mm, 6 vertical channels (6.8 mm) for rollies <= 6 x 60 mm, AB on the bottom.
"""
import numpy as np, manifold3d as m3, sys, os
sys.path.insert(0, os.path.dirname(__file__))
import case as K, v3
from v3 import W, D, H, chbox, prism_xz, to_face, cs, field, recess, frame_line, notched_panel
from shapely.geometry import Polygon, LineString, MultiPolygon, Point, box as sbox
from shapely.ops import unary_union
from shapely import affinity
from skimage import measure
from v4 import text_poly

P = dict(TC=2.8, WB=2.4, WS=2.4, END=8.5, R=2.4, G=0.3,
         PIN_PRESS=1.95, PIN_SLIP=2.2, PIN_SLEEVE=2.3,
         SLOTS=6, SLOT_W=6.8, RIB_T=1.2, RIB_H=3.0,
         MAG_D=6.3, MAG_H_T=2.4, MAG_H_C=2.1,
         CF=1.5, CB=2.0, CE=1.0, FACET=5.0, INL=0.6, INITIALS='AB')

def prism_xy(pts, z0, z1):
    return K.xs_poly(pts).extrude(z1 - z0).translate((0, 0, z0))

def prism_yz(pts_yz, x0, x1):
    s = K.xs_poly(pts_yz).extrude(x1 - x0)          # sketch (y, z), extrude along +Z -> map to X
    return s.transform(np.array([[0, 0, 1, x0], [1, 0, 0, 0], [0, 1, 0, 0]], float))

def envelope(p):
    cf, cb, ce, fa = p['CF'], p['CB'], p['CE'], p['FACET']
    x0, x1, y0, y1 = -W / 2, W / 2, -D / 2, D / 2
    xy = [(x0 + cf, y0), (x1 - cf, y0), (x1, y0 + cf), (x1, y1 - cb), (x1 - cb, y1), (x0 + cb, y1), (x0, y1 - cb), (x0, y0 + cf)]
    xz = [(x0 + ce, 0), (x1 - fa, 0), (x1, fa), (x1, H - fa), (x1 - fa, H), (x0 + ce, H), (x0, H - ce), (x0, ce)]
    yz = [(y0 + cf, 0), (y1 - cb, 0), (y1, cb), (y1, H - cb), (y1 - cb, H), (y0 + cf, H), (y0, H - cf), (y0, cf)]
    return prism_xy(xy, -1, H + 1) ^ prism_xz(xz, -D, D) ^ prism_yz(yz, -W, W)

def teardrop(x, y, r, up, z0, z1):
    """Horizontal-in-print bore along world Z with a 45 deg roof pointing to world +y (up=+1) or -y (up=-1)."""
    pts = [(x + r * np.cos(a), y + r * np.sin(a)) for a in np.linspace(0, 2 * np.pi, 40, endpoint=False)]
    c = Polygon(pts).union(Polygon([(x - r * 0.7071, y + up * r * 0.7071), (x + r * 0.7071, y + up * r * 0.7071), (x, y + up * r * 1.4142)]))
    return K.shapely_to_cs(c).extrude(z1 - z0).translate((0, 0, z0))

def pat_topo(region, seed=5, n=13, w=1.0, wi=1.6):
    f, rng = field(seed)
    x0, z0, x1, z1 = region.bounds; res = 0.2
    xs = np.arange(x0 - 2, x1 + 2, res); zs = np.arange(z0 - 2, z1 + 2, res)
    X, Z = np.meshgrid(xs, zs); F = f(X, Z); sh = []
    for i, lv in enumerate(np.linspace(rng[0], rng[1], n)):
        for c in measure.find_contours(F, lv):
            ls = LineString([(xs[0] + q[1] * res, zs[0] + q[0] * res) for q in c]).simplify(0.05)
            if ls.length > 8: sh.append(ls.buffer((wi if i % 4 == 0 else w) / 2, quad_segs=4))
    g = unary_union(sh).intersection(region)
    return MultiPolygon([q for q in getattr(g, 'geoms', [g]) if q.area > 0.8])

def pat_grid(region, pitch=12.0, w=1.0):
    x0, z0, x1, z1 = region.bounds; sh = []
    for x in np.arange(np.ceil(x0 / pitch) * pitch, x1, pitch): sh.append(sbox(x - w / 2, z0, x + w / 2, z1))
    for z in np.arange(np.ceil(z0 / pitch) * pitch, z1, pitch): sh.append(sbox(x0, z - w / 2, x1, z + w / 2))
    cx, cz = (x0 + x1) / 2 + 6, (z0 + z1) / 2 + 12
    sh += [Point(cx, cz).buffer(6.5).difference(Point(cx, cz).buffer(5.3))]
    return unary_union(sh).intersection(region)

def knurl_flat(shell, panel, side, depth=0.9, pitch=2.4, base=2.2, top=0.6):
    shell = recess(shell, panel, side, depth)
    inner = panel.buffer(-0.5, join_style=2)
    x0, z0, x1, z1 = inner.bounds; h, t = base / 2, top / 2
    unit = m3.Manifold.hull_points(np.array([[-h, 0, 0], [h, 0, 0], [0, -h, 0], [0, h, 0],
                                             [-t, 0, depth], [t, 0, depth], [0, -t, depth], [0, t, depth]], float))
    pyr = []
    for j, z in enumerate(np.arange(z0 + h, z1 - h + 1e-6, pitch / 2)):
        off = pitch / 2 if j % 2 else 0.0
        for x in np.arange(x0 + h + off, x1 - h + 1e-6, pitch):
            if inner.contains(Point(x, z).buffer(h * 0.75)): pyr.append(unit.translate((x, z, 0)))
    ty = (-D / 2 + depth) if side == 'f' else (D / 2 - depth)
    return shell + to_face(m3.Manifold.compose(pyr), side, ty)

def inlay(shell, geom, side, depth):
    c = cs(geom)
    if c is None: return shell, None
    ty = (-D / 2 + depth) if side == 'f' else (D / 2 - depth)
    cut = to_face(c.extrude(depth + 0.5), side, ty)
    return shell - cut, cut ^ shell

def book(surface='knurl', seed=(5, 11), p=P):
    TC, WB, WS, END, R, G, INL = p['TC'], p['WB'], p['WS'], p['END'], p['R'], p['G'], p['INL']
    ys = -D / 2 + TC
    XA, YA = -W / 2 + R + 0.1, -D / 2 + R + 0.1
    segs = [(0, 15), (15, 33), (33, 52), (52, 70), (70, 85)]
    own = ['T', 'C', 'S', 'C', 'T']
    env = envelope(p)
    halfT = chbox(-W, W, ys, D, -1, H + 1, cv=0.1); halfC = chbox(-W, W, -D, ys, -1, H + 1, cv=0.1)
    tray = env ^ halfT
    cx0, cx1 = -W / 2 + WS, W / 2 - WS
    cav = chbox(cx0, cx1, ys - 1, D / 2 - WB, END, H - END, cv=0.4)
    tray -= cav
    # vertical channels
    x_left = XA + R + G + 0.4
    span = p['SLOTS'] * p['SLOT_W'] + (p['SLOTS'] - 1) * p['RIB_T']
    slot_x0 = x_left + ((cx1 - x_left) - span) / 2
    x = slot_x0; ribs = []
    for i in range(p['SLOTS'] - 1):
        x += p['SLOT_W']; rt = p['RIB_T']
        ribs.append(prism_xz([(x, END - 0.5), (x + rt, END - 0.5), (x + rt, H - END - 12), (x + rt / 2, H - END - 11), (x, H - END - 12)],
                             D / 2 - WB - p['RIB_H'], D / 2 - WB + 0.1)
                    ^ prism_yz([(D / 2 - WB - p['RIB_H'] - 0.01, END - 1), (D / 2, END - 1), (D / 2, H), (D / 2 - WB - p['RIB_H'] - 0.01, H)], x - 1, x + rt + 1))
        x += rt
    tray += m3.Manifold.batch_boolean(ribs, m3.OpType.Add)
    # cover + lip
    cover = env ^ halfC
    lip = chbox(cx0 + 3.0, cx1 - 0.2, ys - 0.5, ys + 1.4, END + 0.2, H - END - 0.2, cv=0.5) - \
          chbox(cx0 + 4.0, cx1 - 1.2, ys - 1, ys + 2, END + 1.2, H - END - 1.2, cv=0.3)
    cover += lip
    # inside-of-cover stiffening frame (raised 0.8, notched octagon) + data plate inlay
    inner_frame_poly = notched_panel(cx0 + 5.0, cx1 - 2.5, END + 3.0, H - END - 3.0, c=3.0, step=3.0)
    ring = inner_frame_poly.difference(inner_frame_poly.buffer(-1.6, join_style=2))
    cover += _map_inner(K.shapely_to_cs(ring).extrude(1.1), ys - 0.3)
    # hinge
    sleeve = None
    for (z0, z1), o in zip(segs, own):
        g0, g1 = (z0 + (G if z0 > 0 else 0)), (z1 - (G if z1 < H else 0))
        barrel = m3.Manifold.cylinder(g1 - g0, R, R, 48).translate((XA, YA, g0)) ^ env
        clear = m3.Manifold.cylinder(z1 - z0 + 2 * G, R + G, R + G, 48).translate((XA, YA, z0 - G))
        if o == 'T':
            cover -= clear
            tray += barrel + (chbox(-W / 2, XA + R - 0.1, YA, D / 2 - WB + 0.1, g0, g1, cv=0.1) ^ env ^ halfT)
            tray -= teardrop(XA, YA, p['PIN_PRESS'] / 2, -1, z0 - 1, z1 + 1)
        elif o == 'C':
            tray -= clear
            cover += barrel + (chbox(XA, XA + R + 1.5, YA - R, ys, g0, g1, cv=0.1) ^ env)
            cover -= teardrop(XA, YA, p['PIN_SLIP'] / 2, +1, z0 - 1, z1 + 1)
        else:
            tray -= clear; cover -= clear
            hexs = m3.Manifold.cylinder(g1 - g0, R, R, 6).rotate((0, 0, 30)).translate((XA, YA, g0))
            sleeve = hexs - m3.Manifold.cylinder(H + 2, p['PIN_SLEEVE'] / 2, p['PIN_SLEEVE'] / 2, 32).translate((XA, YA, -1))
    keep = chbox(XA, W, -D, D, -1, H + 1, cv=0.1) + m3.Manifold.cylinder(H + 2, R, R, 48).translate((XA, YA, -1))
    cover = cover ^ keep
    SW = m3.Manifold.batch_boolean([cover.translate((-XA, -YA, 0)).rotate((0, 0, -a)).translate((XA, YA, 0)) for a in range(2, 168, 2)], m3.OpType.Add)
    tray -= SW
    # magnets 6x2 discs in the 8.5 mm end blocks
    mx = cx1 - 4.6; mags = []
    for z in (END / 2, H - END / 2):
        tray -= m3.Manifold.cylinder(p['MAG_H_T'] + 0.5, p['MAG_D'] / 2, p['MAG_D'] / 2, 40).rotate((-90, 0, 0)).translate((mx, ys - 0.5, z))
        cover -= m3.Manifold.cylinder(p['MAG_H_C'] + 0.5, p['MAG_D'] / 2, p['MAG_D'] / 2, 40).rotate((90, 0, 0)).translate((mx, ys + 0.5, z))
        mags.append((mx, z))
    # thumb access: notch in the cover inner edge + 45 deg scoop in the tray front edge (z 34-51)
    cover -= prism_xz([(W / 2 + 1, 33), (W / 2 + 1, 52), (W / 2 - 2.0, 42.5)], ys - 1.4, ys + 0.01)
    scoop = prism_xy([(W / 2 + 1, ys - 0.1), (W / 2 - 3.2, ys - 0.1), (W / 2 + 1, ys + 4.2)], 34, 51)
    tray -= scoop
    # top grip grooves (echo the reference lid bars)
    for gx in (-6, 0, 6):
        g = chbox(gx - 0.6, gx + 0.6, -D / 2 + 2.6, D / 2 - 2.6, H - 0.6, H + 1, cv=0.3)
        tray -= g; cover -= g
    yel_c, yel_t = [], []
    keepout = unary_union([Point(mx, z).buffer(4.8) for mx, z in mags])
    fp = Polygon(K.chrect(XA + R + 1.8, W / 2 - 3.0, 3.0, H - 3.0, 3.0))
    cc = 9.0   # big 45 deg corner cuts on the opening side: echo the outer facets and keep the panel clear of the cover magnets
    fp = fp.difference(Polygon([(cc, 0), (W, 0), (W, W - cc)])).difference(Polygon([(cc, H), (W, H), (W, H - (W - cc))]))
    bp = affinity.scale(fp, -1, 1, origin=(0, 0))      # back face in viewer coords (spine appears on the right)
    for part, poly, side, sd in (('cover', fp, 'f', seed[0]), ('tray', bp, 'b', seed[1])):
        sh = cover if part == 'cover' else tray; y = None
        if surface == 'topo':
            geom = pat_topo(poly.buffer(-0.2), sd).union(frame_line(poly, 1.2))
            sh, y = inlay(sh, geom, side, INL)
        elif surface == 'knurl':
            b = poly.buffer(-4.5, join_style=2).bounds
            inner = notched_panel(b[0], b[2], END + 3.5, H - END - 3.5, c=3.5, step=4.0)
            sh = knurl_flat(sh, inner, side)
            sh, y = inlay(sh, frame_line(inner.buffer(2.0, join_style=2), 1.4), side, INL)
        elif surface == 'grid':
            geom = pat_grid(poly).union(frame_line(poly, 1.2))
            sh, y = inlay(sh, geom, side, INL)
        if part == 'cover': cover = sh; yel_c += [y] if y else []
        else: tray = sh; yel_t += [y] if y else []
    if p.get('INSIDE_PLATE', True):
        # inside of cover: 60 mm ruler + monogram, flush yellow on the inner face (prints as the top layers)
        rx = cx1 - 7.0
        ticks = [sbox(rx - (3.0 if k % 2 == 0 else 1.8), END + 6 + k * 5 - 0.5, rx, END + 6 + k * 5 + 0.5) for k in range(13)]
        spine = sbox(rx, END + 5.5, rx + 1.0, END + 6 + 60 + 0.5)
        mono = affinity.rotate(affinity.scale(text_poly(p['INITIALS'], 6.0), -1, 1, origin=(0, 0)), -90, origin=(0, 0))   # read from inside the cover
        mono = affinity.translate(mono, cx0 + 11.0, H / 2)
        plate = unary_union(ticks + [spine, mono])
        pc = K.shapely_to_cs(plate).extrude(INL + 0.3)
        icut = pc.transform(np.array([[1, 0, 0, 0], [0, 0, -1, ys + 0.3], [0, 1, 0, 0]], float))   # local t -> -y from just inside the face
        yel_c.append(icut ^ cover); cover -= icut
    if p.get('BOTTOM_MONO', True):
        # AB on the bottom (tray part), bigger, centred on the usable tray depth
        tp = text_poly(p['INITIALS'], 6.0)
        yc = (ys + 0.3 + D / 2 - p['CB'] - 0.3) / 2
        tcut = cs(tp).extrude(INL + 0.5).translate((0, 0, -0.5)).mirror((0, 1, 0)).translate((0, yc, 0))
        yel_t.append(tcut ^ tray); tray -= tcut
    tray = max(tray.decompose(), key=lambda q: q.volume()); cover = max(cover.decompose(), key=lambda q: q.volume())
    knuck = m3.Manifold.cylinder(H, R + 1.4, R + 1.4, 48).translate((XA, YA, 0))
    return dict(name=f'BOOK5_{surface}', tray=tray, cover=cover, sleeve=sleeve, yel_cover=yel_c, yel_tray=yel_t,
                axis=(XA, YA), ys=ys, slot_x0=slot_x0, knuckle_mod=knuck, p=p)

def _map_inner(c, ys):
    # (u, v, t) -> (x=u, y=ys+t, z=v); det=-1 so do it as rotate+mirror explicitly
    s = c.rotate((90, 0, 0))            # (u, v, t) -> (u, -t, v)
    s = s.mirror((0, 1, 0))             # -> (u, t, v)
    return s.translate((0, ys, 0))

def rollups(d, dia=6.0):
    p = d['p']; out = []
    for i in range(p['SLOTS']):
        x = d['slot_x0'] + i * (p['SLOT_W'] + p['RIB_T']) + p['SLOT_W'] / 2
        out.append(m3.Manifold.cylinder(60, dia / 2 - 0.05, dia / 2 - 0.05, 32).translate((x, D / 2 - p['WB'] - dia / 2 - 0.05, p['END'])))
    return out

if __name__ == '__main__':
    import time; t = time.time()
    d = book(sys.argv[1] if len(sys.argv) > 1 else 'knurl')
    a, b, s = d['tray'], d['cover'], d['sleeve']
    bb = (a + b + s).bounding_box()
    print('env', [round(bb[i + 3] - bb[i], 2) for i in range(3)], 'vol', round(a.volume()), round(b.volume()), round(s.volume()), 'genus', a.genus(), b.genus())
    print('overlaps', round((a ^ b).volume(), 3), round((a ^ s).volume(), 3), round((b ^ s).volume(), 3))
    RR = m3.Manifold.batch_boolean(rollups(d), m3.OpType.Add)
    print('rollups', len(rollups(d)), 'vs tray', round((RR ^ a).volume(), 3), 'vs cover', round((RR ^ b).volume(), 3))
    XA, YA = d['axis']
    hits = [(g, round((b.translate((-XA, -YA, 0)).rotate((0, 0, -g)).translate((XA, YA, 0)) ^ a).volume(), 2)) for g in range(0, 181, 5)]
    print('swing first contact', [h for h in hits if h[1] > 0.02][:2])
    # magnet wall check: distance from pocket to outer faces
    print('yellow', round(sum(y.volume() for y in d['yel_cover'] + d['yel_tray']), 1), 'time', round(time.time() - t, 1))
