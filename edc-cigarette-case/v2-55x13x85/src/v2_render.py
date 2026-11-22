import sys, os, json, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import v2, manifold3d as m3
out = sys.argv[1]
def pk(man, col):
    mm = man.to_mesh(); v = np.asarray(mm.vert_properties)[:, :3]; t = np.asarray(mm.tri_verts)
    return {'v': np.round(v, 3).ravel().tolist(), 't': t.ravel().tolist(), 'c': col}
G, Y, PAPER, FILT = '#3b4a2f', '#f2b705', '#f4f1ea', '#c98b4a'
for fn in (v2.design_A, v2.design_B, v2.design_C):
    d = fn(); ins = v2.inserts(d)
    body = [d['body']] + [v2.place(i['base'], i['c'], i['side']) for i in ins if i['part'] == 'body']
    bodyY = [v2.place(i['lines'], i['c'], i['side']) for i in ins if i['part'] == 'body']
    lid = [d['lid']] + [v2.place(i['base'], i['c'], i['side']) for i in ins if i['part'] == 'lid']
    lidY = [v2.place(i['lines'], i['c'], i['side']) for i in ins if i['part'] == 'lid']
    mot = d['lid_motion']
    if mot[0] == 'lift':
        T = lambda m: m.translate((0, 0, mot[1]))
    else:
        (px, pz), ang = mot[1], 60
        T = lambda m: m.translate((-px, 0, -pz)).rotate((0, -ang, 0)).translate((px, 0, pz))
    cw = d['cavity']; x0 = d.get('cx', 0) - cw / 2 + (cw - 6 * 8) / 2
    cig = [m3.Manifold.cylinder(80 - 25, 3.95, 3.95, 32).translate((x0 + 4 + i * 8, 0, 1.6)) for i in range(6)]
    fil = [m3.Manifold.cylinder(25, 3.96, 3.96, 32).translate((x0 + 4 + i * 8, 0, 1.6 + 55)) for i in range(6)]
    closed = [pk(m, G) for m in body + lid] + [pk(m, Y) for m in bodyY + lidY]
    opened = [pk(m, G) for m in body] + [pk(T(m), G) for m in lid] + [pk(m, Y) for m in bodyY] + [pk(T(m), Y) for m in lidY] \
        + [pk(m, PAPER) for m in cig] + [pk(m, FILT) for m in fil]
    json.dump(closed, open(f"{out}/{d['name']}_closed.json", 'w'))
    json.dump(opened, open(f"{out}/{d['name']}_open.json", 'w'))
    print(d['name'], 'ok')
