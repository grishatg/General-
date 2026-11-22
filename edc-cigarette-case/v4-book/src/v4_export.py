"""Bambu Studio 3MF for the v4 Book. One plate: tray (back down), cover (face down), yellow spine sleeve (standing).
Per-object: 4 walls, 50% gyroid. Modifiers: 100% infill on hinge knuckles and magnet end blocks."""
import sys, os, io, json, uuid, zipfile
import numpy as np, manifold3d as m3
sys.path.insert(0, os.path.dirname(__file__))
import v4
from v3 import W, D, H, chbox

surf, out, orig = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(out, exist_ok=True)
GREEN, YELLOW = '#3B4A2F', '#F2B705'
d = v4.book(surf); p = d['p']

def mesh(man):
    mm = man.to_mesh(); return np.asarray(mm.vert_properties)[:, :3].astype(float), np.asarray(mm.tri_verts).astype(int)

def model_xml(oid, man):
    v, t = mesh(man); s = io.StringIO()
    s.write('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
            'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" requiredextensions="p">\n'
            ' <metadata name="BambuStudio:3mfVersion">1</metadata>\n <resources>\n'
            f'  <object id="{oid}" p:UUID="{uuid.uuid4()}" type="model">\n   <mesh>\n    <vertices>\n')
    for x, y, z in v: s.write(f'     <vertex x="{x:.5f}" y="{y:.5f}" z="{z:.5f}"/>\n')
    s.write('    </vertices>\n    <triangles>\n')
    for a, b, c in t: s.write(f'     <triangle v1="{a}" v2="{b}" v3="{c}"/>\n')
    s.write('    </triangles>\n   </mesh>\n  </object>\n </resources>\n <build/>\n</model>\n')
    return s.getvalue()

def write_stl(path, man):
    v, t = mesh(man); tri = v[t]; n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    a = np.zeros(len(t), dtype=[('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]); a['n'] = n; a['v'] = tri
    with open(path, 'wb') as f: f.write(b'book'.ljust(80, b' ')); f.write(np.uint32(len(t)).tobytes()); f.write(a.tobytes())

U = lambda vs: m3.Manifold.batch_boolean(vs, m3.OpType.Add) if len(vs) > 1 else vs[0]
end_blocks = chbox(-W / 2 - 1, W / 2 + 1, -D, D, -1, p['END'] + 0.5, cv=0.1) + chbox(-W / 2 - 1, W / 2 + 1, -D, D, H - p['END'] - 0.5, H + 1, cv=0.1)
mod_solid = d['knuckle_mod'] + end_blocks

# print orientation
tray_rot = lambda m: m.rotate((-90, 0, 0))      # back (+Y) down
cover_rot = lambda m: m.rotate((90, 0, 0))      # face (-Y) down
def drop_all(parts):
    bb = U([q for q, kind, _e in parts if kind != 'mod']).bounding_box()
    outp = []
    for q, k, e in parts:
        q = q.translate((-(bb[0] + bb[3]) / 2, -(bb[1] + bb[4]) / 2, -bb[2]))
        if k == 'mod': q = q ^ chbox(-200, 200, -200, 200, 0.0, 200, cv=0.1)
        outp.append((q, k, e))
    return outp

objs = [
    ('Book tray', drop_all([(tray_rot(d['tray']), 'normal', 1)] + [(tray_rot(y), 'normal', 2) for y in d['yel_tray']] +
                           [(tray_rot(mod_solid), 'mod', 0)]), (85, 128)),
    ('Book cover', drop_all([(cover_rot(d['cover']), 'normal', 1)] + [(cover_rot(y), 'normal', 2) for y in d['yel_cover']] +
                            [(cover_rot(mod_solid), 'mod', 0)]), (160, 128)),
    ('Spine sleeve', drop_all([(d['sleeve'], 'normal', 2)]), (210, 128)),
]

files, rels, res, build, sets, inst = {}, [], [], [], [], []
pid, top, ident = 1, 1000, 300
for name, parts, (px, py) in objs:
    comps, pcfg = [], []
    for k, (man, kind, ext) in enumerate(parts):
        path = f'3D/Objects/object_{pid}.model'; files[path] = model_xml(pid, man); rels.append(path)
        comps.append(f'    <component p:path="/{path}" objectid="{pid}" p:UUID="{uuid.uuid4()}" transform="1 0 0 0 1 0 0 0 1 0 0 0" />')
        if kind == 'mod':
            pcfg.append(f'''    <part id="{pid}" subtype="modifier_part">
      <metadata key="name" value="100% infill - hinge and magnet blocks"/>
      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>
      <metadata key="sparse_infill_density" value="100%"/>
      <metadata key="wall_loops" value="6"/>
    </part>''')
        else:
            nm = ('yellow inlay' if ext == 2 else 'green shell') if name != 'Spine sleeve' else 'yellow sleeve'
            pcfg.append(f'''    <part id="{pid}" subtype="normal_part">
      <metadata key="name" value="{nm} {k}"/>
      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>
      <metadata key="extruder" value="{ext}"/>
    </part>''')
        pid += 1
    top += 1; ident += 1
    res.append(f'  <object id="{top}" p:UUID="{uuid.uuid4()}" type="model">\n   <components>\n' + '\n'.join(comps) + '\n   </components>\n  </object>')
    build.append(f'  <item objectid="{top}" p:UUID="{uuid.uuid4()}" transform="1 0 0 0 1 0 0 0 1 {px} {py} 0" printable="1" />')
    sets.append(f'''  <object id="{top}">
    <metadata key="name" value="{name}"/>
    <metadata key="extruder" value="{2 if name == 'Spine sleeve' else 1}"/>
    <metadata key="sparse_infill_density" value="{'100%' if name == 'Spine sleeve' else '50%'}"/>
    <metadata key="sparse_infill_pattern" value="gyroid"/>
    <metadata key="wall_loops" value="4"/>
{chr(10).join(pcfg)}
  </object>''')
    inst.append(f'''    <model_instance>
      <metadata key="object_id" value="{top}"/>
      <metadata key="instance_id" value="0"/>
      <metadata key="identify_id" value="{ident}"/>
    </model_instance>''')

title = {'topo': 'Contour Book', 'knurl': 'Trailhead Book', 'grid': 'Gridline Book'}[surf]
desc = (f'{title} - slim rollie case 55x13x85 mm, 6 channels (rollies up to 6 x 60 mm). Green PLA/PETG + yellow. '
        'Hardware: 2 mm x 84 mm steel rod hinge pin, 4 x 6x2 mm N52 magnets. Tray prints back-down, cover face-down, sleeve standing. No supports.')
files['3D/3dmodel.model'] = ('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
    'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" requiredextensions="p">\n'
    ' <metadata name="Application">BambuStudio-01.10.02.76</metadata>\n <metadata name="BambuStudio:3mfVersion">1</metadata>\n'
    f' <metadata name="Title">{title}</metadata>\n <metadata name="Description">{desc}</metadata>\n'
    ' <resources>\n' + '\n'.join(res) + '\n </resources>\n <build>\n' + '\n'.join(build) + '\n </build>\n</model>\n')
files['3D/_rels/3dmodel.model.rels'] = ('<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n' +
    '\n'.join(f' <Relationship Target="/{q}" Id="rel-{i+1}" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>' for i, q in enumerate(rels)) + '\n</Relationships>\n')
files['Metadata/model_settings.config'] = ('<?xml version="1.0" encoding="UTF-8"?>\n<config>\n' + '\n'.join(sets) +
    '\n  <plate>\n    <metadata key="plater_id" value="1"/>\n    <metadata key="plater_name" value="' + title + '"/>\n    <metadata key="locked" value="false"/>\n' +
    '\n'.join(inst) + '\n  </plate>\n</config>\n')
ps = json.load(open(f'{orig}/Metadata/project_settings.config'))
ps.update({'filament_colour': [GREEN, YELLOW], 'enable_support': '0', 'wall_loops': '4', 'sparse_infill_density': '50%',
           'sparse_infill_pattern': 'gyroid', 'top_shell_layers': '6', 'bottom_shell_layers': '5', 'layer_height': '0.16',
           'enable_prime_tower': '1', 'seam_position': 'back'})
files['Metadata/project_settings.config'] = json.dumps(ps, indent=4)
files['[Content_Types].xml'] = open(f'{orig}/[Content_Types].xml').read()
files['_rels/.rels'] = ('<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
                        ' <Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>\n</Relationships>\n')
fn = f'{out}/{title.replace(" ", "_")}_55x13x85.3mf'
with zipfile.ZipFile(fn, 'w', zipfile.ZIP_DEFLATED) as z:
    for k, v in files.items(): z.writestr(k, v)
sd = f'{out}/stl_{surf}'; os.makedirs(sd, exist_ok=True)
for name, parts, _ in objs:
    for k, (man, kind, ext) in enumerate(parts):
        if kind != 'mod': write_stl(f'{sd}/{name.replace(" ", "_")}_{k}_{"yellow" if ext == 2 else "green"}.stl', man)
print(fn, os.path.getsize(fn) // 1024, 'KB')
