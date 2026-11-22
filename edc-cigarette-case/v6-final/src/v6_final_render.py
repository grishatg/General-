import sys, os, json, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import v6_final, v5, v6, manifold3d as m3
out = sys.argv[1]
def pk(man, col):
    mm = man.to_mesh(); v = np.asarray(mm.vert_properties)[:, :3]; t = np.asarray(mm.tri_verts)
    return {'v': np.round(v, 3).ravel().tolist(), 't': t.ravel().tolist(), 'c': col}
r = v6_final.build(); d = r['d']; XA, YA = d['axis']; C = v6.COL
T = lambda m: m.translate((-XA, -YA, 0)).rotate((0, 0, -150)).translate((XA, YA, 0))
R = v5.rollups(d)
tips = [m3.Manifold.cylinder(13, 2.96, 2.96, 32).translate(((q.bounding_box()[0] + q.bounding_box()[3]) / 2, (q.bounding_box()[1] + q.bounding_box()[4]) / 2, q.bounding_box()[2])) for q in R]
parts = [(r['cover'], 'grey', 'c'), (r['tray'], 'black', 't'), (r['sleeve'], 'yellow', 's')] + [(y, 'yellow', 'c') for y in r['yel_cover']] + [(y, 'yellow', 't') for y in r['yel_tray']]
json.dump([pk(m, C[c]) for m, c, g in parts], open(f'{out}/final_closed.json', 'w'))
json.dump([pk(T(m) if g == 'c' else m, C[c]) for m, c, g in parts] + [pk(q, '#f1ede4') for q in R] + [pk(t, '#d9b27a') for t in tips], open(f'{out}/final_open.json', 'w'))
print('ok')
