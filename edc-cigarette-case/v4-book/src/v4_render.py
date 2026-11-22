import sys, os, json, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import v4, manifold3d as m3
out, surf = sys.argv[1], sys.argv[2]
G, Y, PAPER, TIP = '#3b4a2f', '#f2b705', '#f1ede4', '#d9b27a'
def pk(man, col):
    mm = man.to_mesh(); v = np.asarray(mm.vert_properties)[:, :3]; t = np.asarray(mm.tri_verts)
    return {'v': np.round(v, 3).ravel().tolist(), 't': t.ravel().tolist(), 'c': col}
d = v4.book(surf); XA, YA = d['axis']
T = lambda m: m.translate((-XA, -YA, 0)).rotate((0, 0, -150)).translate((XA, YA, 0))
R = v4.rollups(d)
tips = [m3.Manifold.cylinder(13, 2.96, 2.96, 32).translate(((r.bounding_box()[0] + r.bounding_box()[3]) / 2, (r.bounding_box()[1] + r.bounding_box()[4]) / 2, r.bounding_box()[2])) for r in R]
closed = [pk(d['tray'], G), pk(d['cover'], G), pk(d['sleeve'], Y)] + [pk(y, Y) for y in d['yel_cover'] + d['yel_tray']]
opened = [pk(d['tray'], G), pk(T(d['cover']), G), pk(d['sleeve'], Y)] + [pk(y, Y) for y in d['yel_tray']] + [pk(T(y), Y) for y in d['yel_cover']] \
    + [pk(r, PAPER) for r in R] + [pk(t, TIP) for t in tips]
json.dump(closed, open(f'{out}/{surf}_closed.json', 'w')); json.dump(opened, open(f'{out}/{surf}_open.json', 'w')); print(surf, 'ok')
