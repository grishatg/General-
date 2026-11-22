import sys, os, json, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import v6, v5, manifold3d as m3
out, key = sys.argv[1], sys.argv[2]
def pk(man, col):
    mm = man.to_mesh(); v = np.asarray(mm.vert_properties)[:, :3]; t = np.asarray(mm.tri_verts)
    return {'v': np.round(v, 3).ravel().tolist(), 't': t.ravel().tolist(), 'c': col}
c = v6.CONCEPTS[key](); d = c['d']; XA, YA = d['axis']
T = lambda m: m.translate((-XA, -YA, 0)).rotate((0, 0, -150)).translate((XA, YA, 0))
R = v5.rollups(d)
tips = [m3.Manifold.cylinder(13, 2.96, 2.96, 32).translate(((r.bounding_box()[0] + r.bounding_box()[3]) / 2, (r.bounding_box()[1] + r.bounding_box()[4]) / 2, r.bounding_box()[2])) for r in R]
closed = [pk(m, v6.COL[col]) for m, col, g in c['parts'] if m is not None]
opened = [pk(T(m) if g == 'cover' else m, v6.COL[col]) for m, col, g in c['parts'] if m is not None] + \
         [pk(r, '#f1ede4') for r in R] + [pk(t, '#d9b27a') for t in tips]
json.dump(closed, open(f'{out}/{key}_closed.json', 'w')); json.dump(opened, open(f'{out}/{key}_open.json', 'w'))
print(key, 'ok')
