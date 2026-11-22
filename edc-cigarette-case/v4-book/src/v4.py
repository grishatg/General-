"""v4 BOOK - refined for hand-feel and strength. 55 x 13 x 85 mm.
- vertical rollie channels (ribs on the tray back), no horizontal divider
- thicker walls, 6.5 mm solid end blocks carrying 6x2 mm magnets
- 2 mm steel rod hinge pin (blind at the bottom), free-spinning yellow spine sleeve
- flush yellow 'AB' on the bottom face
"""
import numpy as np, manifold3d as m3, sys, os
sys.path.insert(0, os.path.dirname(__file__))
import case as K, v3
from v3 import W, D, H, chbox, prism_xz, inlay, knurl, frame_line, notched_panel, pat_topo, pat_grid, to_face, cs
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union
from shapely import affinity

FONT = os.path.join(os.path.dirname(__file__), '..', 'fonts', 'BlackOpsOne-Regular.ttf')
P = dict(TC=2.8, WB=2.4, WS=2.4, END=6.5, R=2.4, G=0.3, PIN=2.1, SLOTS=6, SLOT_W=6.6, RIB_T=1.4, RIB_H=3.0,
         MAG_D=6.2, MAG_H=2.1, INITIALS='AB', CH=1.0)

def text_poly(txt, height):
    from matplotlib.textpath import TextPath
    from matplotlib.font_manager import FontProperties
    tp = TextPath((0, 0), txt, size=10, prop=FontProperties(fname=FONT))
    polys = [Polygon(p) for p in tp.to_polygons() if len(p) > 2]
    g = None
    for p in sorted(polys, key=lambda q: -q.area):
        p = p.buffer(0); g = p if g is None else g.symmetric_difference(p)
    x0, y0, x1, y1 = g.bounds; s = height / (y1 - y0)
    g = affinity.scale(g, s, s, origin=(x0, y0)); x0, y0, x1, y1 = g.bounds
    return affinity.translate(g, -(x0 + x1) / 2, -(y0 + y1) / 2)

def book(surface='topo', seed=(5, 11), p=P):
    TC, WB, WS, END, R, G = p['TC'], p['WB'], p['WS'], p['END'], p['R'], p['G']
    ys = -D / 2 + TC
    XA, YA = -W / 2 + R, -D / 2 + R
    segs = [(0, 15), (15, 33), (33, 52), (52, 70), (70, 85)]
    own = ['T', 'C', 'S', 'C', 'T']                  # S = yellow free sleeve
    env = chbox(-W / 2, W / 2, -D / 2, D / 2, 0, H, cv=p['CH'], cb=p['CH'], ct=p['CH'])
    halfT = chbox(-W, W, ys, D, -1, H + 1, cv=0.1); halfC = chbox(-W, W, -D, ys, -1, H + 1, cv=0.1)
    tray = env ^ halfT
    cx0, cx1 = -W / 2 + WS, W / 2 - WS
    tray -= chbox(cx0, cx1, ys - 1, D / 2 - WB, END, H - END, cv=0.4)
    # vertical rollie channels: ribs standing off the tray back
    x_left = XA + R + G + 0.4
    span = p['SLOTS'] * p['SLOT_W'] + (p['SLOTS'] - 1) * p['RIB_T']
    x = x_left + ((cx1 - x_left) - span) / 2
    ribs = []
    for i in range(p['SLOTS'] - 1):
        x += p['SLOT_W']
        rib = prism_xz([(x, END - 0.5), (x + p['RIB_T'], END - 0.5), (x + p['RIB_T'], H - END - 8 - 2), (x + p['RIB_T'] / 2, H - END - 8), (x, H - END - 8 - 2)],
                       D / 2 - WB - p['RIB_H'], D / 2 - WB + 0.1)
        ribs.append(rib); x += p['RIB_T']
    tray += m3.Manifold.batch_boolean(ribs, m3.OpType.Add)
    slot_x0 = x_left + ((cx1 - x_left) - span) / 2
    cover = env ^ halfC
    lip = chbox(cx0 + 3.0, cx1 - 0.2, ys - 0.5, ys + 1.4, END + 0.2, H - END - 0.2, cv=0.5) - \
          chbox(cx0 + 4.0, cx1 - 1.2, ys - 1, ys + 2, END + 1.2, H - END - 1.2, cv=0.3)
    cover += lip
    # hinge
    pin_blind = m3.Manifold.cylinder(H - 1.6 + 1, p['PIN'] / 2, p['PIN'] / 2, 32).translate((XA, YA, 1.6))
    sleeve = None
    for (z0, z1), o in zip(segs, own):
        g0, g1 = (z0 + (G if z0 > 0 else 0)), (z1 - (G if z1 < H else 0))
        barrel = m3.Manifold.cylinder(g1 - g0, R, R, 48).translate((XA, YA, g0)) ^ env
        clear = m3.Manifold.cylinder(z1 - z0 + 2 * G, R + G, R + G, 48).translate((XA, YA, z0 - G))
        if o == 'T':
            cover -= clear
            tray += barrel + (chbox(-W / 2, XA + R - 0.1, YA, D / 2 - WB + 0.1, g0, g1, cv=0.1) ^ env ^ halfT)
        elif o == 'C':
            tray -= clear
            cover += barrel + (chbox(XA, XA + R + 1.5, YA - R, ys, g0, g1, cv=0.1) ^ env)
        else:
            tray -= clear; cover -= clear
            sleeve = barrel
    keep = chbox(XA, W, -D, D, -1, H + 1, cv=0.1) + m3.Manifold.cylinder(H + 2, R, R, 48).translate((XA, YA, -1))
    cover = cover ^ keep
    tray -= pin_blind; cover -= pin_blind
    sleeve = sleeve - m3.Manifold.cylinder(H + 2, p['PIN'] / 2 + 0.1, p['PIN'] / 2 + 0.1, 32).translate((XA, YA, -1))
    SW = m3.Manifold.batch_boolean([cover.translate((-XA, -YA, 0)).rotate((0, 0, -a)).translate((XA, YA, 0)) for a in range(2, 168, 2)], m3.OpType.Add)
    tray -= SW
    # magnets 6x2 in the end blocks (opening side) + matching pockets in the cover
    for z in (END / 2, H - END / 2):
        mx = cx1 - 4.2
        tray -= m3.Manifold.cylinder(p['MAG_H'] + 0.5, p['MAG_D'] / 2, p['MAG_D'] / 2, 40).rotate((-90, 0, 0)).translate((mx, ys - 0.5, z))
        cover -= m3.Manifold.cylinder(p['MAG_H'] + 0.5, p['MAG_D'] / 2, p['MAG_D'] / 2, 40).rotate((90, 0, 0)).translate((mx, ys + 0.5, z))
    cover -= prism_xz([(W / 2 + 1, 33), (W / 2 + 1, 52), (W / 2 - 2.0, 42.5)], ys - 1.4, ys + 0.01)   # thumb notch
    yel_c, yel_t = [], []
    fp = Polygon(K.chrect(XA + R + 1.4, W / 2 - 2.6, 2.6, H - 2.6, 3.0))
    bp = Polygon(K.chrect(-W / 2 + 2.6, W / 2 - 2 * R - 1.4, 2.6, H - 2.6, 3.0))
    for part, poly, side, sd in (('cover', fp, 'f', seed[0]), ('tray', bp, 'b', seed[1])):
        sh = cover if part == 'cover' else tray; y = None
        if surface == 'topo':
            sh, y = inlay(sh, pat_topo(poly.buffer(-0.2), sd).union(frame_line(poly, 0.8)), side)
        elif surface == 'knurl':
            inner = notched_panel(*poly.buffer(-4, join_style=2).bounds)
            sh = knurl(sh, inner, side)
            sh, y = inlay(sh, frame_line(inner.buffer(1.6, join_style=2), 1.0), side)
        elif surface == 'grid':
            sh, y = inlay(sh, pat_grid(poly).union(frame_line(poly, 0.8)), side)
        if part == 'cover': cover = sh; yel_c += [y] if y else []
        else: tray = sh; yel_t += [y] if y else []
    # initials on the bottom face of the tray: read with the cover side up when you look at the bottom
    tp = text_poly(p['INITIALS'], 5.6)
    tp = affinity.translate(tp, 3.0, 0)
    c = cs(tp).extrude(v3.INL + 0.5).translate((0, 0, -0.5))            # (gx, gy, t)
    ycen = (ys + D / 2) / 2
    tcut = c.mirror((0, 1, 0)).translate((0, ycen, 0))                   # world x = gx, y = -gy
    yel_t.append(tcut ^ tray); tray -= tcut
    # small yellow index bars either side of the initials (frame the monogram)
    bars = unary_union([Polygon(K.chrect(-12, -8.5, -0.5, 0.5, 0.2)), Polygon(K.chrect(14.5, 18.0, -0.5, 0.5, 0.2))])
    bcut = cs(bars).extrude(v3.INL + 0.5).translate((0, 0, -0.5)).mirror((0, 1, 0)).translate((0, ycen, 0))
    yel_t.append(bcut ^ tray); tray -= bcut
    knuck = m3.Manifold.cylinder(H, R + 1.2, R + 1.2, 48).translate((XA, YA, 0))
    return dict(name=f'BOOK_{surface}', tray=tray, cover=cover, sleeve=sleeve, yel_cover=yel_c, yel_tray=yel_t,
                axis=(XA, YA), ys=ys, slot_x0=slot_x0, knuckle_mod=knuck, p=p)

def rollups(d, dia=6.0):
    p = d['p']; out = []
    for i in range(p['SLOTS']):
        x = d['slot_x0'] + i * (p['SLOT_W'] + p['RIB_T']) + p['SLOT_W'] / 2
        out.append(m3.Manifold.cylinder(60, dia / 2 - 0.05, dia / 2 - 0.05, 32).translate((x, D / 2 - p['WB'] - dia / 2 - 0.05, p['END'])))
    return out

if __name__ == '__main__':
    import time; t = time.time()
    d = book(sys.argv[1] if len(sys.argv) > 1 else 'topo')
    a, b, s = d['tray'], d['cover'], d['sleeve']
    bb = (a + b + s).bounding_box()
    print('env', [round(bb[i + 3] - bb[i], 2) for i in range(3)], 'vol tray/cover/sleeve', round(a.volume()), round(b.volume()), round(s.volume()))
    print('overlaps', round((a ^ b).volume(), 3), round((a ^ s).volume(), 3), round((b ^ s).volume(), 3))
    RR = m3.Manifold.batch_boolean(rollups(d), m3.OpType.Add)
    print('rollups', len(rollups(d)), 'vs tray', round((RR ^ a).volume(), 3), 'vs cover', round((RR ^ b).volume(), 3))
    XA, YA = d['axis']
    hits = [(g, round((b.translate((-XA, -YA, 0)).rotate((0, 0, -g)).translate((XA, YA, 0)) ^ a).volume(), 2)) for g in range(0, 181, 5)]
    print('swing first contact', [h for h in hits if h[1] > 0.02][:2], 'yellow vol', round(sum(y.volume() for y in d['yel_cover'] + d['yel_tray']), 1), round(time.time() - t, 1), 's')
