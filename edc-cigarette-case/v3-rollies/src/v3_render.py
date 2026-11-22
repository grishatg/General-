import sys, os, json, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import v3, manifold3d as m3
out = sys.argv[1]; which = sys.argv[2:]
G, Y, PAPER, TIP = '#3b4a2f', '#f2b705', '#f1ede4', '#d9b27a'
def pk(man, col):
    mm = man.to_mesh(); v = np.asarray(mm.vert_properties)[:, :3]; t = np.asarray(mm.tri_verts)
    return {'v': np.round(v, 3).ravel().tolist(), 't': t.ravel().tolist(), 'c': col}
jobs = {'contour_book': (v3.book, 'topo'), 'trailhead_book': (v3.book, 'knurl'), 'gridline_book': (v3.book, 'grid'),
        'ridgeline_cap': (v3.cap, 'knurl'), 'hazard_cap': (v3.cap, 'hazard')}
for k in which:
    fn, s = jobs[k]; d = fn(s); P = d['parts']; yel = d['yellow']
    if 'axis' in d:
        XA, YA = d['axis']; mov = P['cover']; fix = P['tray']
        T = lambda m: m.translate((-XA, -YA, 0)).rotate((0, 0, -150)).translate((XA, YA, 0))
        # yellow parts: last one is the spine sleeve (stays put); inlays belong to cover (front) or tray (back)
        movY = [y for y in yel[:-1] if y.bounding_box()[1] < -D_half] if False else None
        cy, ty = [], []
        for y in yel:
            bb = y.bounding_box()
            (cy if bb[4] < -3.0 and bb[1] < -6.0 and (bb[0] > -24) else ty).append(y)
        R = v3.rollups(d['cavity'], z0=6.0)
    else:
        mov = P['cap']; fix = P['body']; T = lambda m: m.translate((0, 0, 32))
        cy = [y for y in yel if y.bounding_box()[2] >= d['lift'] - 0.5]; ty = [y for y in yel if y not in cy]
        R = v3.rollups(d['cavity'])
    tips = [m3.Manifold.cylinder(14, 2.96, 2.96, 32).translate((r.bounding_box()[0] + 3, (r.bounding_box()[1] + r.bounding_box()[4]) / 2, r.bounding_box()[2])) for r in R]
    closed = [pk(fix, G), pk(mov, G)] + [pk(y, Y) for y in yel]
    opened = [pk(fix, G), pk(T(mov), G)] + [pk(y, Y) for y in ty] + [pk(T(y), Y) for y in cy] + [pk(r, PAPER) for r in R] + [pk(t, TIP) for t in tips]
    json.dump(closed, open(f'{out}/{k}_closed.json', 'w')); json.dump(opened, open(f'{out}/{k}_open.json', 'w'))
    print(k, 'ok', flush=True)
