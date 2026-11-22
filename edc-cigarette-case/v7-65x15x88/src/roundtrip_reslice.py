"""Re-slice the SHIPPED Bambu 3MF: read its meshes, part extruders, modifiers and plate positions back out of the file, then slice in PrusaSlicer (A1 by-object ini)."""
import sys, re, json, zipfile, numpy as np, manifold3d as m3
out, src = sys.argv[1], sys.argv[2]
sys.argv = [sys.argv[0], out]   # slicetest parses argv at import
import slicetest as ST
z = zipfile.ZipFile(src)
top = z.read('3D/3dmodel.model').decode(); ms = z.read('Metadata/model_settings.config').decode()
def mesh(path):
    x = z.read(path.lstrip('/')).decode()
    V = np.array(re.findall(r'<vertex x="([^"]+)" y="([^"]+)" z="([^"]+)"', x), dtype=np.float32)
    T = np.array(re.findall(r'<triangle v1="(\d+)" v2="(\d+)" v3="(\d+)"', x), dtype=np.uint32)
    man = m3.Manifold(m3.Mesh(vert_properties=V, tri_verts=T))
    return man, len(T)
place = {o: (float(a), float(b)) for o, a, b in re.findall(r'<item objectid="(\d+)"[^>]*transform="1 0 0 0 1 0 0 0 1 ([-\d.]+) ([-\d.]+) 0"', top)}
objs, stats = [], []
for oid, body in re.findall(r'<object id="(\d+)" p:UUID="[^"]+" type="model">\s*<components>(.*?)</components>', top, flags=re.S):
    oset = re.search(rf'<object id="{oid}">(.*?)</object>', ms, flags=re.S).group(1)
    name = re.search(r'<metadata key="name" value="([^"]+)"', oset).group(1)
    parts = []
    for path, pid in re.findall(r'p:path="([^"]+)" objectid="(\d+)"', body):
        pdef = re.search(rf'<part id="{pid}" subtype="([a-z_]+)">(.*?)</part>', oset, flags=re.S)
        man, nt = mesh(path)
        if pdef.group(1) == 'modifier_part':
            parts.append((man, 'mod', 0, {'fill_density': re.search(r'sparse_infill_density" value="([^"]+)"', pdef.group(2)).group(1),
                                          'perimeters': re.search(r'wall_loops" value="([^"]+)"', pdef.group(2)).group(1)}))
        else:
            parts.append((man, 'part', int(re.search(r'key="extruder" value="(\d)"', pdef.group(2)).group(1)), {}))
        stats.append((name, pdef.group(1), parts[-1][2], nt, man.status().name if hasattr(man.status(), 'name') else str(man.status()), round(man.volume(), 1)))
    objs.append((name, parts, place[oid]))
for s in stats: print('  ', s)
ST.prusa_3mf(f'{out}/roundtrip.3mf', objs, [])
res = ST.slice_one(f'{out}/roundtrip.3mf', f'{out}/a1_hq_petghf_0.16.ini', f'{out}/roundtrip.gcode')
if res.returncode != 0: print('SLICE FAILED', (res.stdout + res.stderr)[-1500:]); sys.exit(1)
r = ST.report(f'{out}/roundtrip.gcode'); r.pop('zs')
msgs = [l for l in (res.stdout + res.stderr).splitlines() if l.strip()]
print(json.dumps(r)); print('slicer messages:', msgs[-6:])
