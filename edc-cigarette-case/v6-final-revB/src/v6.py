"""v6 - five new VISUAL directions on the unchanged v5 Book structure (PETG-HF palette).
Only surfaces, colour assignment and typography change. Initials: small, dead-centre of the bottom face.
"""
import numpy as np, manifold3d as m3, sys, os
sys.path.insert(0, os.path.dirname(__file__))
import case as K, v3, v5
from v3 import W, D, H, to_face, cs, recess
from v5 import inlay
from shapely.geometry import Polygon, LineString, MultiPolygon, Point, box as sbox
from shapely.ops import unary_union
from shapely import affinity

FONTS = os.path.join(os.path.dirname(__file__), '..', 'fonts')
COL = {'grey': '#9da1a3', 'black': '#1e1e20', 'blue': '#1f4fbf', 'green': '#00ae42', 'forest': '#39541a', 'yellow': '#ffd00b'}
INL = 0.6

def text_poly(txt, height, font, thicken=0.15):
    from matplotlib.textpath import TextPath
    from matplotlib.font_manager import FontProperties
    tp = TextPath((0, 0), txt, size=10, prop=FontProperties(fname=os.path.join(FONTS, font)))
    # nonzero fill: contours with the outer winding are unioned, opposite-winding contours are counters (holes).
    # (even-odd XOR breaks fonts with overlapping contours, e.g. Inter's A crossbar)
    from shapely.geometry import LinearRing
    rings = [np.asarray(a) for a in tp.to_polygons() if len(a) > 2]
    big = max(rings, key=lambda a: abs(Polygon(a).area))
    outer_ccw = LinearRing(big).is_ccw
    outers = unary_union([Polygon(a).buffer(0) for a in rings if LinearRing(a).is_ccw == outer_ccw])
    holes = [Polygon(a).buffer(0) for a in rings if LinearRing(a).is_ccw != outer_ccw]
    g = outers.difference(unary_union(holes)) if holes else outers
    x0, y0, x1, y1 = g.bounds; s = height / (y1 - y0)
    g = affinity.scale(g, s, s, origin=(x0, y0))
    if thicken:   # widen vertical stems only (bottom face prints upright: x-width is the critical one)
        g = unary_union([affinity.translate(g, t, 0) for t in np.linspace(-thicken, thicken, 5)]).buffer(0)
        polys = []
        for q in getattr(g, 'geoms', [g]):
            polys.append(Polygon(q.exterior, [h for h in q.interiors if Polygon(h).area > 0.35]))
        g = unary_union(polys)
    x0, y0, x1, y1 = g.bounds
    return affinity.translate(g, -(x0 + x1) / 2, -(y0 + y1) / 2)

def stroke_ok(g, min_w=0.8):
    """Fraction of glyph area that survives an inward offset of min_w/2 (thin strokes vanish)."""
    er = g.buffer(-min_w / 2)
    n0 = len(getattr(g, 'geoms', [g])); n1 = len(getattr(er, 'geoms', [er])) if not er.is_empty else 0
    return round(er.area / g.area, 2), n0, n1

# ---------------- shared geometry ----------------
P0 = dict(v5.P); P0['INSIDE_PLATE'] = False; P0['BOTTOM_MONO'] = False
XA = -W / 2 + P0['R'] + 0.1
xz = [(-W / 2 + P0['CE'], 0), (W / 2 - P0['FACET'], 0), (W / 2, P0['FACET']), (W / 2, H - P0['FACET']), (W / 2 - P0['FACET'], H),
      (-W / 2 + P0['CE'], H), (-W / 2, H - P0['CE']), (-W / 2, P0['CE'])]
FRONT = Polygon(xz).buffer(-1.8, join_style=2).intersection(sbox(XA + 1.6, -1, W, H + 1))
BACK = affinity.scale(Polygon(xz).buffer(-2.3, join_style=2), -1, 1, origin=(0, 0))
MX = W / 2 - P0['WS'] - 4.6
KEEP = unary_union([Point(MX, P0['END'] / 2).buffer(4.3), Point(MX, H - P0['END'] / 2).buffer(4.3)])

def grooves(shell, lines, side, w=1.4, steps=((1.4, 0.2), (1.0, 0.4), (0.6, 0.6))):
    """V-ish grooves as 45-degree stepped recesses (prints support-free face-down)."""
    for wi, di in steps:
        g = unary_union([l.buffer(wi / 2, cap_style=2, join_style=1) for l in lines])
        shell = recess(shell, g, side, di)
    return shell

def inside_inlay(cover, geom, ys):
    pc = K.shapely_to_cs(affinity.scale(geom, -1, 1, origin=(0, 0))).extrude(INL + 0.3)   # mirrored: read from inside
    cut = pc.transform(np.array([[1, 0, 0, 0], [0, 0, -1, ys + 0.3], [0, 1, 0, 0]], float))
    return cover - cut, cut ^ cover

def bottom_mark(tray, geom):
    cut = cs(geom).extrude(INL + 0.5).translate((0, 0, -0.5)).mirror((0, 1, 0))        # centred at x=0, y=0
    return tray - cut, cut ^ tray

def layer(*shapes):
    """Painter's order: later shapes sit on top. Returns list of visible geometries in the same order."""
    out = []
    for i, s in enumerate(shapes):
        above = unary_union(shapes[i + 1:]) if i + 1 < len(shapes) else None
        out.append(s.difference(above) if above is not None and not above.is_empty else s)
    return out

def seigaiha(region, r=6.0, n=3, w=1.0, z0=None, z1=None):
    x0, zb, x1, zt = region.bounds
    z0 = zb - r if z0 is None else z0; z1 = zt + r if z1 is None else z1
    rows = np.arange(z1, z0 - r, -r / 2)
    acc = None
    for j, z in enumerate(rows):
        off = r if j % 2 else 0
        for x in np.arange(x0 - 2 * r + off, x1 + 2 * r, 2 * r):
            disk = Point(x, z).buffer(r, quad_segs=24)
            rings = unary_union([Point(x, z).buffer(r - k * (r / n), quad_segs=24).difference(Point(x, z).buffer(r - k * (r / n) - w, quad_segs=24)) for k in range(n)])
            acc = rings if acc is None else acc.difference(disk).union(rings)
    return acc.intersection(region)

def kumo(x0, x1, z, h=2.2):
    return LineString([(x0, z), (x1, z)]).buffer(h / 2, cap_style=1)

# ---------------- concepts ----------------
def base(p=None):
    d = v5.book('none', p=p or P0)
    return d

def concept_monolith():
    """h3li0-inspired: clean, functional, quietly architectural. Grey cover / black tray, fluting, one yellow datum."""
    d = base(); tray, cover, ys = d['tray'], d['cover'], d['ys']
    parts = []
    fl = [LineString([(x, 9.8), (x, 75.2)]) for x in np.arange(1.8, 24.0, 2.8)]
    fl = [l.intersection(FRONT.buffer(-1.0)).difference(KEEP) for l in fl]
    cover = grooves(cover, [l for l in fl if not l.is_empty], 'f')
    datum = sbox(-23.0, 32.0, -0.6, 33.0)
    cover, y1 = inlay(cover, datum, 'f', INL)
    tray, y2 = inlay(tray, sbox(-26.0, 32.0, -9.0, 33.0), 'b', INL)              # wraps round the opening edge
    cover, y3 = inside_inlay(cover, sbox(-17.5, 32.0, 19.0, 33.0), ys)
    raw = text_poly('a·b', 4.2, 'SpaceGrotesk-Bold.ttf', thicken=0)
    dot_c = min(raw.geoms, key=lambda q: q.area).centroid
    th = text_poly('a·b', 4.2, 'SpaceGrotesk-Bold.ttf')
    mono = unary_union([q for q in th.geoms if q.area > 1.5] + [Point(dot_c.x, dot_c.y).buffer(0.62, quad_segs=16)])
    tray, y4 = bottom_mark(tray, mono)
    parts = [(cover, 'grey', 'cover'), (tray, 'black', 'tray'), (d['sleeve'], 'yellow', 'sleeve'),
             (y1, 'yellow', 'cover'), (y3, 'yellow', 'cover'), (y2, 'yellow', 'tray'), (y4, 'yellow', 'tray')]
    return dict(key='monolith', name='MONOLITH', d=d, parts=parts, mono=mono, font='Space Grotesk Bold',
                colours=['grey', 'black', 'yellow'])

def concept_ripple():
    """Abstractia-inspired: ribbed light-play, organic ripple, tone-on-tone two greens."""
    d = base(); tray, cover = d['tray'], d['cover']
    def ripple_lines(region, flip):
        x0, z0, x1, z1 = region.bounds; out = []
        for xc in np.arange(x0 + 1.4, x1, 2.8):
            t = (xc - x0) / (x1 - x0); t = 1 - t if flip else t
            A = 0.25 + 1.35 * t ** 1.5
            zs = np.linspace(z0 - 2, z1 + 2, 160)
            ln = LineString([(xc + A * np.sin(2 * np.pi * z / 26.0 + 0.22 * xc), z) for z in zs])
            out.append(ln)
        return out
    fr = [l.intersection(FRONT.buffer(-1.4)).difference(KEEP) for l in ripple_lines(FRONT, False)]
    cover = grooves(cover, [l for l in fr if not l.is_empty], 'f')
    br = [l.intersection(BACK.buffer(-1.4)) for l in ripple_lines(BACK, True)]
    tray = grooves(tray, [l for l in br if not l.is_empty], 'b')
    mono = text_poly('AB', 3.8, 'Unbounded-Black.ttf', thicken=0)
    tray, y4 = bottom_mark(tray, mono)
    parts = [(cover, 'green', 'cover'), (tray, 'forest', 'tray'), (d['sleeve'], 'forest', 'sleeve'), (y4, 'green', 'tray')]
    return dict(key='ripple', name='RIPPLE', d=d, parts=parts, mono=mono, font='Unbounded Black', colours=['green', 'forest'])

def concept_tide():
    """XXY2025-inspired: woodblock-print narrative. Seigaiha sea, kumo clouds, sun; mountain on the back; hanko seal."""
    d = base(); tray, cover = d['tray'], d['cover']
    xs = np.linspace(-30, 30, 200)
    def horizon(h0, A, lam, ph):
        return [(x, h0 + A * np.sin(2 * np.pi * x / lam + ph)) for x in xs]
    # front
    hz = horizon(40, 3.5, 38, 0.6)
    sea = Polygon([(-30, -5)] + hz + [(30, -5)]).intersection(FRONT)
    waves = seigaiha(sea, r=6.0)
    hline = LineString(hz).buffer(0.55).intersection(FRONT)
    sun = Point(9, 63).buffer(6.0)
    clouds = unary_union([kumo(-21, 1, 56.5), kumo(-5, 23, 71.0), kumo(-19, -7, 75.5)]).intersection(FRONT)
    sun_v, clouds_v = layer(sun, clouds)
    waves_v = waves.difference(hline.buffer(0.5))
    front_black = unary_union([hline, clouds_v]).difference(KEEP)
    cover, yb = inlay(cover, waves_v.difference(KEEP), 'f', INL)
    cover, yk = inlay(cover, front_black, 'f', INL)
    cover, ys_ = inlay(cover, sun_v.intersection(FRONT), 'f', INL)
    # back (viewer coords)
    hz2 = horizon(28, 2.5, 30, 2.0)
    sea2 = Polygon([(-30, -5)] + hz2 + [(30, -5)]).intersection(BACK)
    waves2 = seigaiha(sea2, r=6.0)
    hline2 = LineString(hz2).buffer(0.55).intersection(BACK)
    mountain = Polygon([(-30, 24), (-12, 44), (-3, 66), (2, 66.5), (9, 55), (30, 30), (30, 24)])
    cap = Polygon([(-9.2, 52), (-4, 70), (4, 70), (6.2, 59.5), (3, 56), (0, 59), (-3, 54), (-6, 57)])
    mtn = mountain.difference(cap).difference(sea2).difference(hline2.buffer(0.3)).intersection(BACK)
    cloud2 = kumo(-14, 16, 76).intersection(BACK)
    tray, yb2 = inlay(tray, waves2.difference(hline2.buffer(0.5)), 'b', INL)
    tray, yk2 = inlay(tray, unary_union([hline2, mtn, cloud2]), 'b', INL)
    # hanko seal on the bottom: black seal, letters knocked out to the grey shell
    letters = text_poly('AB', 3.9, 'ShipporiMinchoB1-ExtraBold.ttf')
    seal = Polygon(K.chrect(-4.2, 4.2, -3.2, 3.2, 0.5)).difference(letters.buffer(0.15))
    tray, ysl = bottom_mark(tray, seal)
    parts = [(cover, 'grey', 'cover'), (tray, 'grey', 'tray'), (d['sleeve'], 'blue', 'sleeve'),
             (yb, 'blue', 'cover'), (yk, 'black', 'cover'), (ys_, 'yellow', 'cover'),
             (yb2, 'blue', 'tray'), (yk2, 'black', 'tray'), (ysl, 'black', 'tray')]
    return dict(key='tide', name='TIDE', d=d, parts=parts, mono=letters, font='Shippori Mincho B1 ExtraBold (seal)',
                colours=['grey', 'blue', 'black', 'yellow'], seal=seal)

def concept_form():
    """Bauhaus / Swiss modernist poster: primary geometry, flat colour fields, asymmetric balance."""
    d = base(); tray, cover = d['tray'], d['cover']
    xl = FRONT.bounds[0]
    blue = Point(xl, 1.8).buffer(31, quad_segs=48)
    bar = sbox(xl - 1, 44.0, 17.5, 47.5)
    line = sbox(4.5, 44.0, 5.5, 84)
    sq = sbox(13.0, 10.5, 19.0, 16.5)
    sun = Point(10.5, 61.0).buffer(9.0, quad_segs=48)
    b_v, bar_v, line_v, sq_v, sun_v = [g.intersection(FRONT).difference(KEEP) for g in layer(blue, bar, line, sq, sun)]
    cover, y1 = inlay(cover, b_v, 'f', INL)
    cover, y2 = inlay(cover, unary_union([bar_v, line_v, sq_v]), 'f', INL)
    cover, y3 = inlay(cover, sun_v, 'f', INL)
    # back: counterpoint composition
    half = Point(6, BACK.bounds[1]).buffer(15, quad_segs=48)
    ybar = sbox(-27, 50.0, 9.0, 53.5)
    bdisc = Point(-9.5, 68.0).buffer(7.0, quad_segs=48)
    vline = sbox(-1.0, 1, 0.0, 50.0)
    h_v, yb_v, bd_v, vl_v = [g.intersection(BACK) for g in layer(half, vline, ybar, bdisc)]
    tray, y4 = inlay(tray, unary_union([h_v, vl_v]), 'b', INL)
    tray, y5 = inlay(tray, yb_v, 'b', INL)
    tray, y6 = inlay(tray, bd_v, 'b', INL)
    mono = text_poly('AB', 4.0, 'Jost-Black.ttf')
    tray, y7 = bottom_mark(tray, mono)
    parts = [(cover, 'grey', 'cover'), (tray, 'grey', 'tray'), (d['sleeve'], 'yellow', 'sleeve'),
             (y1, 'blue', 'cover'), (y2, 'black', 'cover'), (y3, 'yellow', 'cover'),
             (y4, 'black', 'tray'), (y5, 'yellow', 'tray'), (y6, 'blue', 'tray'), (y7, 'black', 'tray')]
    return dict(key='form', name='FORM', d=d, parts=parts, mono=mono, font='Jost Black', colours=['grey', 'blue', 'yellow', 'black'])

def concept_instrument():
    """Precision-instrument / audio-gear language: black body, grey dot grille and scale, one yellow 'open here' dot."""
    d = base(); tray, cover, ys = d['tray'], d['cover'], d['ys']
    field = Polygon(K.chrect(-21.5, 13.5, 47.0, 78.0, 3.0))
    dots = unary_union([Point(x, z).buffer(0.7, quad_segs=10) for x in np.arange(-20.0, 13.0, 3.0) for z in np.arange(48.5, 77.0, 3.0)
                        if field.buffer(-0.8).contains(Point(x, z))])
    ticks = [sbox(24.0 - (3.6 if k % 2 == 0 else 2.0), 10 + k * 5 - 0.5, 24.0, 10 + k * 5 + 0.5) for k in range(14)]
    spine = sbox(23.9, 9.5, 24.9, 75.5)
    scale = unary_union(ticks + [spine]).intersection(FRONT).difference(KEEP)
    cover, y1 = inlay(cover, unary_union([dots, scale]), 'f', INL)
    cover, y2 = inlay(cover, Point(16.5, 42.5).buffer(2.3, quad_segs=32), 'f', INL)
    bfield = Polygon(K.chrect(-25.0, -4.0, 8.0, 30.0, 2.5))
    bdots = unary_union([Point(x, z).buffer(0.7, quad_segs=10) for x in np.arange(-23.5, -4.0, 3.0) for z in np.arange(9.5, 29.5, 3.0)
                         if bfield.buffer(-0.8).contains(Point(x, z))])
    tray, y3 = inlay(tray, bdots, 'b', INL)
    rx = 13.0
    rticks = [sbox(rx - (3.0 if k % 2 == 0 else 1.8), 14 + k * 5 - 0.5, rx, 14 + k * 5 + 0.5) for k in range(13)]
    ruler = unary_union(rticks + [sbox(rx, 13.5, rx + 1.0, 74.5)])
    cover, y4 = inside_inlay(cover, affinity.scale(ruler, -1, 1, origin=(0, 0)), ys)
    mono = text_poly('AB', 3.8, 'JetBrainsMono-ExtraBold.ttf')
    tray, y5 = bottom_mark(tray, mono)
    parts = [(cover, 'black', 'cover'), (tray, 'black', 'tray'), (d['sleeve'], 'grey', 'sleeve'),
             (y1, 'grey', 'cover'), (y2, 'yellow', 'cover'), (y4, 'grey', 'cover'), (y3, 'grey', 'tray'), (y5, 'grey', 'tray')]
    return dict(key='instrument', name='INSTRUMENT', d=d, parts=parts, mono=mono, font='JetBrains Mono ExtraBold',
                colours=['black', 'grey', 'yellow'])


def concept_hybrid():
    """Judge-proposed Monolith x Ripple: grey cover, ripples that build toward the opening edge, black tray,
    one yellow datum that wraps the edge, yellow sleeve, lowercase a.b. Yellow inlays 1.0 mm deep (no show-through)."""
    d = base(); tray, cover, ys = d['tray'], d['cover'], d['ys']
    def rip(x0, x1, z0, z1, toward_right):
        out = []
        for xc in np.arange(x0, x1, 2.8):
            t = (xc - x0) / (x1 - x0); t = t if toward_right else 1 - t
            A = 0.05 + 1.5 * t ** 1.6
            zs = np.linspace(z0, z1, 140)
            out.append(LineString([(xc + A * np.sin(2 * np.pi * z / 26.0 + 0.22 * xc), z) for z in zs]))
        return out
    fr = [l.intersection(FRONT.buffer(-1.6)).difference(KEEP.buffer(1.0)) for l in rip(1.8, 24.0, 9.8, 75.2, True)]
    cover = grooves(cover, [l for l in fr if not l.is_empty and l.length > 15], 'f')
    br = [l.intersection(BACK.buffer(-1.6)).difference(sbox(-40, 30.2, 40, 34.8)) for l in rip(-24.0, -1.8, 9.8, 75.2, False)]
    tray = grooves(tray, [g for l in br for g in getattr(l, 'geoms', [l]) if not g.is_empty and g.length > 15], 'b')
    cover, y1 = inlay(cover, sbox(-23.0, 32.0, -0.8, 33.0), 'f', 1.0)
    tray, y2 = inlay(tray, sbox(-29.0, 32.0, -6.0, 33.0), 'b', 1.0)                 # runs out over the edge chamfer
    cover, y3 = inside_inlay(cover, sbox(-17.5, 32.0, 19.0, 33.0), ys)
    raw = text_poly('a·b', 4.6, 'SpaceGrotesk-Bold.ttf', thicken=0)
    dot_c = min(raw.geoms, key=lambda q: q.area).centroid
    th = text_poly('a·b', 4.6, 'SpaceGrotesk-Bold.ttf')
    mono = unary_union([q for q in th.geoms if q.area > 1.5] + [Point(dot_c.x, dot_c.y).buffer(0.7, quad_segs=16)])
    cut = cs(mono).extrude(1.0 + 0.5).translate((0, 0, -0.5)).mirror((0, 1, 0)); y4 = cut ^ tray; tray = tray - cut
    parts = [(cover, 'grey', 'cover'), (tray, 'black', 'tray'), (d['sleeve'], 'yellow', 'sleeve'),
             (y1, 'yellow', 'cover'), (y3, 'yellow', 'cover'), (y2, 'yellow', 'tray'), (y4, 'yellow', 'tray')]
    return dict(key='hybrid', name='HYBRID', d=d, parts=parts, mono=mono, font='Space Grotesk Bold', colours=['grey', 'black', 'yellow'])

CONCEPTS = {'monolith': concept_monolith, 'ripple': concept_ripple, 'tide': concept_tide, 'form': concept_form, 'instrument': concept_instrument, 'hybrid': concept_hybrid}

if __name__ == '__main__':
    import time
    for k in (sys.argv[1:] or CONCEPTS):
        t = time.time(); c = CONCEPTS[k]()
        tray = [m for m, col, g in c['parts'] if g == 'tray'][0]; cover = [m for m, col, g in c['parts'] if g == 'cover'][0]
        bb = (tray + cover + c['d']['sleeve']).bounding_box()
        allp = [m for m, col, g in c['parts'] if m is not None]
        ov = sum((a ^ b).volume() for i, a in enumerate(allp) for b in allp[i + 1:])
        print(c['name'], 'env', [round(bb[i + 3] - bb[i], 1) for i in range(3)], 'colours', c['colours'],
              'pieces tray/cover', len(tray.decompose()), len(cover.decompose()), 'overlap', round(ov, 3),
              'mono stroke', stroke_ok(c.get('seal', c['mono'])), 'mono bbox', [round(v, 1) for v in c['mono'].bounds], round(time.time() - t, 1), 's')
