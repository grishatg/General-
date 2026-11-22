import sys, os, json, zipfile, uuid, io
import numpy as np, manifold3d as m3
sys.path.insert(0, os.path.dirname(__file__))
import case as C

OUT = sys.argv[1]; ORIG = sys.argv[2]
os.makedirs(OUT, exist_ok=True)
GREEN, YELLOW = '#3B4A2F', '#F2B705'

def mesh(man):
    mm = man.to_mesh()
    return np.asarray(mm.vert_properties)[:, :3].astype(float), np.asarray(mm.tri_verts).astype(int)

def write_stl(path, man):
    v, t = mesh(man)
    tri = v[t]; n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    data = np.zeros(len(t), dtype=[('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')])
    data['n'] = n; data['v'] = tri
    with open(path, 'wb') as f:
        f.write(b'EDC cigarette case'.ljust(80, b' ')); f.write(np.uint32(len(t)).tobytes()); f.write(data.tobytes())

def drop(man):  # put on z=0, centre xy
    b = man.bounding_box()
    return man.translate((-(b[0] + b[3]) / 2, -(b[1] + b[4]) / 2, -b[2]))

# ---------- build ----------
body, lid = C.build_body(), C.build_lid()
xs = np.linspace(-C.W / 2, C.W / 2, 200); zs = np.linspace(0, C.HS + C.HL, 200)
X, Z = np.meshgrid(xs, zs)
ins = {}
for name, seed in (('front', 7), ('back', 23)):
    f = C.field(seed); F = f(X, Z)
    C.field_full_range = (np.percentile(F, 1), np.percentile(F, 99))
    for part, panel in (('body', C.body_panel()), ('lid', C.lid_panel())):
        region = panel.buffer(-0.15, join_style=2)
        ins[f'{part}_{name}'] = (C.build_insert(panel, f), (region.centroid.x, region.centroid.y))

# print orientations
body_p = drop(body)                                  # upright, open top up
lid_p = drop(lid.mirror((0, 0, 1)))                  # upside down, top on the bed
def placed_insert(key):
    (base, lines), _ = ins[key]
    return base, lines

# ---------- STL ----------
write_stl(f'{OUT}/body_green.stl', body_p)
write_stl(f'{OUT}/lid_green.stl', lid_p)
for k in ins:
    base, lines = ins[k][0]
    write_stl(f'{OUT}/insert_{k}_base_green.stl', base)
    write_stl(f'{OUT}/insert_{k}_lines_yellow.stl', lines)

# ---------- Bambu Studio 3MF (2 plates) ----------
def model_xml(oid, man):
    v, t = mesh(man)
    out = io.StringIO()
    out.write('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" '
              'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
              'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" '
              'xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" requiredextensions="p">\n'
              ' <metadata name="BambuStudio:3mfVersion">1</metadata>\n <resources>\n'
              f'  <object id="{oid}" p:UUID="{uuid.uuid4()}" type="model">\n   <mesh>\n    <vertices>\n')
    for x, y, z in v: out.write(f'     <vertex x="{x:.5f}" y="{y:.5f}" z="{z:.5f}"/>\n')
    out.write('    </vertices>\n    <triangles>\n')
    for a, b, c in t: out.write(f'     <triangle v1="{a}" v2="{b}" v3="{c}"/>\n')
    out.write('    </triangles>\n   </mesh>\n  </object>\n </resources>\n <build/>\n</model>\n')
    return out.getvalue()

# objects: (name, [(part_name, manifold, extruder)], plate, (x, y) on plate)
objs = [
    ('Case Body', [('body', body_p, 1)], 1, (128, 150)),
    ('Case Lid', [('lid', lid_p, 1)], 1, (128, 100)),
]
pos = {'body_front': (86, 150), 'body_back': (170, 150), 'lid_front': (86, 95), 'lid_back': (170, 95)}
for k in ins:
    base, lines = ins[k][0]
    objs.append((f'Topo insert {k}', [(f'{k} base', base, 1), (f'{k} topo lines', lines, 2)], 2, pos[k]))

files = {}; rels = []; res = []; build = []; settings = []
pid = 1; oid_top = 1000; ident = 200
plates = {1: [], 2: []}
for name, parts, plate, (px, py) in objs:
    comps = []; part_cfg = []
    bb = m3.Manifold.batch_boolean([p[1] for p in parts], m3.OpType.Add).bounding_box()
    cx, cy = (bb[0] + bb[3]) / 2, (bb[1] + bb[4]) / 2
    for pname, man, ext in parts:
        path = f'3D/Objects/object_{pid}.model'
        files[path] = model_xml(pid, man.translate((-cx, -cy, 0)))
        rels.append(path)
        comps.append(f'    <component p:path="/{path}" objectid="{pid}" p:UUID="{uuid.uuid4()}" transform="1 0 0 0 1 0 0 0 1 0 0 0" />')
        part_cfg.append(f'''    <part id="{pid}" subtype="normal_part">
      <metadata key="name" value="{pname}"/>
      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>
      <metadata key="extruder" value="{ext}"/>
    </part>''')
        pid += 1
    oid_top += 1
    res.append(f'  <object id="{oid_top}" p:UUID="{uuid.uuid4()}" type="model">\n   <components>\n' + '\n'.join(comps) + '\n   </components>\n  </object>')
    build.append(f'  <item objectid="{oid_top}" p:UUID="{uuid.uuid4()}" transform="1 0 0 0 1 0 0 0 1 {px + (307.2 if plate == 2 else 0)} {py} 0" printable="1" />')
    settings.append(f'''  <object id="{oid_top}">
    <metadata key="name" value="{name}"/>
    <metadata key="extruder" value="1"/>
{chr(10).join(part_cfg)}
  </object>''')
    ident += 1
    plates[plate].append((oid_top, ident))

plate_xml = []
for pl, items in plates.items():
    inst = '\n'.join(f'''    <model_instance>
      <metadata key="object_id" value="{o}"/>
      <metadata key="instance_id" value="0"/>
      <metadata key="identify_id" value="{i}"/>
    </model_instance>''' for o, i in items)
    nm = 'Shell - green only' if pl == 1 else 'Topo inserts - green + yellow'
    plate_xml.append(f'''  <plate>
    <metadata key="plater_id" value="{pl}"/>
    <metadata key="plater_name" value="{nm}"/>
    <metadata key="locked" value="false"/>
{inst}
  </plate>''')

desc = ('Slim EDC cigarette case for 10 king-size cigarettes. Remix-in-spirit of the Hiking Container '
        'design language (chamfered shell, M3 screw-pin side hinge, magnet latch block, lanyard hole). '
        'Plate 1: shell in green. Plate 2: topo-line inserts, green base + yellow raised lines; glue into pockets.')
main = ('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" '
        'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
        'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" '
        'xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" requiredextensions="p">\n'
        ' <metadata name="Application">BambuStudio-01.10.02.76</metadata>\n'
        ' <metadata name="BambuStudio:3mfVersion">1</metadata>\n'
        ' <metadata name="Title">Slim EDC Cigarette Case - Topo</metadata>\n'
        f' <metadata name="Description">{desc}</metadata>\n'
        ' <resources>\n' + '\n'.join(res) + '\n </resources>\n <build>\n' + '\n'.join(build) + '\n </build>\n</model>\n')
files['3D/3dmodel.model'] = main
files['3D/_rels/3dmodel.model.rels'] = ('<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n' +
    '\n'.join(f' <Relationship Target="/{p}" Id="rel-{i+1}" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>' for i, p in enumerate(rels)) + '\n</Relationships>\n')
files['Metadata/model_settings.config'] = '<?xml version="1.0" encoding="UTF-8"?>\n<config>\n' + '\n'.join(settings) + '\n' + '\n'.join(plate_xml) + '\n</config>\n'
ps = json.load(open(f'{ORIG}/Metadata/project_settings.config'))
ps['filament_colour'] = [GREEN, YELLOW]
ps['enable_support'] = '0'
ps['wall_loops'] = '4'
ps['sparse_infill_density'] = '25%'
ps['top_shell_layers'] = '5'; ps['bottom_shell_layers'] = '4'
files['Metadata/project_settings.config'] = json.dumps(ps, indent=4)
files['[Content_Types].xml'] = open(f'{ORIG}/[Content_Types].xml').read()
files['_rels/.rels'] = ('<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
                        ' <Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>\n</Relationships>\n')
with zipfile.ZipFile(f'{OUT}/EDC_Cigarette_Case_Topo.3mf', 'w', zipfile.ZIP_DEFLATED) as z:
    for k, v in files.items(): z.writestr(k, v)

# ---------- assembly for previews ----------
def to_world(man, key):
    (_, (cx, cz)) = ins[key]
    side = key.split('_')[1]
    if side == 'front':   # x<-x_l, y<- -z_l, z<- y_l
        M = np.array([[1, 0, 0, cx], [0, 0, -1, -C.D / 2 + C.POCKET], [0, 1, 0, cz]], float)
    else:
        M = np.array([[-1, 0, 0, -cx], [0, 0, 1, C.D / 2 - C.POCKET], [0, 1, 0, cz]], float)
    return man.transform(M)
asm_g = [body, lid] + [to_world(ins[k][0][0], k) for k in ins]
asm_y = [to_world(ins[k][0][1], k) for k in ins]
np.save(f'{OUT}/_asm.npy', np.array([0]))
import pickle
pickle.dump({'green': [mesh(x) for x in asm_g], 'yellow': [mesh(x) for x in asm_y],
             'lid': mesh(lid), 'pivot': (C.XP, C.ZP), 'body': mesh(body)}, open(f'{OUT}/_asm.pkl', 'wb'))
print('ok', {k: round(v[0][0].volume() + v[0][1].volume(), 1) for k, v in ins.items()})
print('body', round(body.volume(), 1), 'lid', round(lid.volume(), 1))
