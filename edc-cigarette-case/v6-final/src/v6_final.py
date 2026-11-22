"""Approved design 6 (HYBRID) with uppercase initials 'A·B' in Michroma, 5.0 mm cap height. Builds the Bambu Studio 3MF.
Filaments: 1 = grey (cover), 2 = black (tray), 3 = yellow (inlays + spine sleeve). All PETG-HF."""
import sys, os, io, json, uuid, zipfile
import numpy as np, manifold3d as m3
sys.path.insert(0, os.path.dirname(__file__))
import v6, v5
from v6 import text_poly, Point, unary_union, cs, sbox, LineString, grooves, inlay, inside_inlay, FRONT, BACK, KEEP, base
from v3 import W, D, H, chbox

FONT = 'Michroma-Regular.ttf'; CAP = 5.0; YD = 1.0   # yellow inlay depth (no show-through)

def monogram(font=FONT, cap=CAP, thicken=0.15):
    raw = text_poly('A·B', cap, font, thicken=0)
    dot_c = min(raw.geoms, key=lambda q: q.area).centroid
    th = text_poly('A·B', cap, font, thicken=thicken)
    letters = [q for q in getattr(th, 'geoms', [th]) if q.area > 2.0]
    return unary_union(letters + [Point(dot_c.x, dot_c.y).buffer(0.75, quad_segs=16)])

def build(font=FONT):
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
    cover = grooves(cover, [g for l in fr for g in getattr(l, 'geoms', [l]) if not g.is_empty and g.length > 15], 'f')
    br = [l.intersection(BACK.buffer(-1.6)).difference(sbox(-40, 30.2, 40, 34.8)) for l in rip(-24.0, -1.8, 9.8, 75.2, False)]
    tray = grooves(tray, [g for l in br for g in getattr(l, 'geoms', [l]) if not g.is_empty and g.length > 15], 'b')
    cover, y1 = inlay(cover, sbox(-23.0, 32.0, -0.8, 33.0), 'f', YD)
    tray, y2 = inlay(tray, sbox(-29.0, 32.0, -6.0, 33.0), 'b', YD)
    cover, y3 = inside_inlay(cover, sbox(-17.5, 32.0, 19.0, 33.0), ys)
    mono = monogram(font)
    cut = cs(mono).extrude(YD + 0.5).translate((0, 0, -0.5)).mirror((0, 1, 0)); y4 = cut ^ tray; tray = tray - cut
    return dict(d=d, tray=tray, cover=cover, sleeve=d['sleeve'], yel_cover=[y1, y3], yel_tray=[y2, y4], mono=mono)

# ----------------------------------------------------------------- 3MF export
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
    with open(path, 'wb') as f: f.write(b'ab case'.ljust(80, b' ')); f.write(np.uint32(len(t)).tobytes()); f.write(a.tobytes())

PER_FILAMENT = {'activate_air_filtration', 'additional_cooling_fan_speed', 'chamber_temperatures', 'close_fan_the_first_x_layers',
                'complete_print_exhaust_fan_speed', 'cool_plate_temp', 'cool_plate_temp_initial_layer', 'default_filament_colour',
                'during_print_exhaust_fan_speed', 'enable_overhang_bridge_fan', 'enable_pressure_advance', 'eng_plate_temp',
                'eng_plate_temp_initial_layer', 'fan_cooling_layer_time', 'fan_max_speed', 'fan_min_speed', 'full_fan_speed_layer',
                'hot_plate_temp', 'hot_plate_temp_initial_layer', 'nozzle_temperature', 'nozzle_temperature_initial_layer',
                'nozzle_temperature_range_high', 'nozzle_temperature_range_low', 'overhang_fan_speed', 'overhang_fan_threshold',
                'overhang_threshold_participating_cooling', 'pressure_advance', 'reduce_fan_stop_start_freq', 'required_nozzle_HRC',
                'slow_down_for_layer_cooling', 'slow_down_layer_time', 'slow_down_min_speed', 'supertack_plate_temp',
                'supertack_plate_temp_initial_layer', 'temperature_vitrification', 'textured_plate_temp', 'textured_plate_temp_initial_layer'}

def project_settings(orig, colours):
    ps = json.load(open(f'{orig}/Metadata/project_settings.config')); n0 = len(ps['filament_colour']); n = len(colours)
    for k, v in list(ps.items()):
        if isinstance(v, list) and len(v) == n0 and (k.startswith('filament_') or k in PER_FILAMENT):
            ps[k] = v + [v[-1]] * (n - n0)
    ps['filament_colour'] = colours
    # purge volumes (mm3), row = from, col = to: grey, black, yellow
    M = [[0, 150, 320], [280, 0, 460], [150, 150, 0]]
    ps['flush_volumes_matrix'] = [str(x) for row in M for x in row]
    ps['flush_volumes_vector'] = ['140'] * (2 * n)
    ps['different_settings_to_system'] = ps['different_settings_to_system'][:1] + [''] * n + ps['different_settings_to_system'][-1:]
    ps.update({'enable_support': '0', 'wall_loops': '4', 'sparse_infill_density': '50%', 'sparse_infill_pattern': 'gyroid',
               'top_shell_layers': '6', 'bottom_shell_layers': '5', 'layer_height': '0.16', 'enable_prime_tower': '1', 'seam_position': 'back'})
    return ps

def export(r, out, orig):
    os.makedirs(out, exist_ok=True)
    p = v5.P
    U = lambda vs: m3.Manifold.batch_boolean(vs, m3.OpType.Add) if len(vs) > 1 else vs[0]
    end_blocks = chbox(-W / 2 - 1, W / 2 + 1, -D, D, -1, p['END'] + 0.5, cv=0.1) + chbox(-W / 2 - 1, W / 2 + 1, -D, D, H - p['END'] - 0.5, H + 1, cv=0.1)
    mod_solid = r['d']['knuckle_mod'] + end_blocks
    tray_rot = lambda m: m.rotate((-90, 0, 0)); cover_rot = lambda m: m.rotate((90, 0, 0))
    def drop(parts):
        bb = U([q for q, k, e in parts if k != 'mod']).bounding_box(); outp = []
        for q, k, e in parts:
            q = q.translate((-(bb[0] + bb[3]) / 2, -(bb[1] + bb[4]) / 2, -bb[2]))
            if k == 'mod': q = q ^ chbox(-200, 200, -200, 200, 0.0, 200, cv=0.1)
            outp.append((q, k, e))
        return outp
    GREY, BLACK, YEL = 1, 2, 3
    objs = [('Tray (black)', drop([(tray_rot(r['tray']), 'normal', BLACK)] + [(tray_rot(y), 'normal', YEL) for y in r['yel_tray']] + [(tray_rot(mod_solid), 'mod', 0)]), (85, 128), BLACK),
            ('Cover (grey)', drop([(cover_rot(r['cover']), 'normal', GREY)] + [(cover_rot(y), 'normal', YEL) for y in r['yel_cover']] + [(cover_rot(mod_solid), 'mod', 0)]), (160, 128), GREY),
            ('Spine sleeve (yellow)', drop([(r['sleeve'], 'normal', YEL)]), (210, 128), YEL)]
    files, rels, res, build, sets, inst = {}, [], [], [], [], []
    pid, top, ident = 1, 1000, 300
    for name, parts, (px, py), oext in objs:
        comps, pcfg = [], []
        for k, (man, kind, ext) in enumerate(parts):
            path = f'3D/Objects/object_{pid}.model'; files[path] = model_xml(pid, man); rels.append(path)
            comps.append(f'    <component p:path="/{path}" objectid="{pid}" p:UUID="{uuid.uuid4()}" transform="1 0 0 0 1 0 0 0 1 0 0 0" />')
            if kind == 'mod':
                pcfg.append(f'    <part id="{pid}" subtype="modifier_part">\n      <metadata key="name" value="100% infill - hinge and magnet blocks"/>\n'
                            f'      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>\n      <metadata key="sparse_infill_density" value="100%"/>\n'
                            f'      <metadata key="wall_loops" value="6"/>\n    </part>')
            else:
                nm = {GREY: 'grey shell', BLACK: 'black shell', YEL: 'yellow'}[ext]
                pcfg.append(f'    <part id="{pid}" subtype="normal_part">\n      <metadata key="name" value="{nm} {k}"/>\n'
                            f'      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>\n      <metadata key="extruder" value="{ext}"/>\n    </part>')
            pid += 1
        top += 1; ident += 1
        res.append(f'  <object id="{top}" p:UUID="{uuid.uuid4()}" type="model">\n   <components>\n' + '\n'.join(comps) + '\n   </components>\n  </object>')
        build.append(f'  <item objectid="{top}" p:UUID="{uuid.uuid4()}" transform="1 0 0 0 1 0 0 0 1 {px} {py} 0" printable="1" />')
        dens = '100%' if 'sleeve' in name else '50%'
        sets.append(f'  <object id="{top}">\n    <metadata key="name" value="{name}"/>\n    <metadata key="extruder" value="{oext}"/>\n'
                    f'    <metadata key="sparse_infill_density" value="{dens}"/>\n    <metadata key="sparse_infill_pattern" value="gyroid"/>\n'
                    f'    <metadata key="wall_loops" value="4"/>\n' + '\n'.join(pcfg) + '\n  </object>')
        inst.append(f'    <model_instance>\n      <metadata key="object_id" value="{top}"/>\n      <metadata key="instance_id" value="0"/>\n'
                    f'      <metadata key="identify_id" value="{ident}"/>\n    </model_instance>')
    title = 'AB Rollie Book - Hybrid'
    desc = ('Slim rollie case 55x13x85 mm, 6 channels (rollies up to 6 x 60 mm). PETG-HF: filament 1 grey (cover), 2 black (tray), 3 yellow (inlays, sleeve). '
            'Hardware: 2 mm x 85 mm steel rod, 4 x 6x2 mm N52 magnets. No supports.')
    files['3D/3dmodel.model'] = ('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
        'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" requiredextensions="p">\n'
        ' <metadata name="Application">BambuStudio-01.10.02.76</metadata>\n <metadata name="BambuStudio:3mfVersion">1</metadata>\n'
        f' <metadata name="Title">{title}</metadata>\n <metadata name="Description">{desc}</metadata>\n'
        ' <resources>\n' + '\n'.join(res) + '\n </resources>\n <build>\n' + '\n'.join(build) + '\n </build>\n</model>\n')
    files['3D/_rels/3dmodel.model.rels'] = ('<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n' +
        '\n'.join(f' <Relationship Target="/{q}" Id="rel-{i+1}" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>' for i, q in enumerate(rels)) + '\n</Relationships>\n')
    files['Metadata/model_settings.config'] = ('<?xml version="1.0" encoding="UTF-8"?>\n<config>\n' + '\n'.join(sets) +
        f'\n  <plate>\n    <metadata key="plater_id" value="1"/>\n    <metadata key="plater_name" value="{title}"/>\n    <metadata key="locked" value="false"/>\n' +
        '\n'.join(inst) + '\n  </plate>\n</config>\n')
    files['Metadata/project_settings.config'] = json.dumps(project_settings(orig, ['#9DA1A3', '#1E1E20', '#FFD00B']), indent=4)
    files['[Content_Types].xml'] = open(f'{orig}/[Content_Types].xml').read()
    files['_rels/.rels'] = ('<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
                            ' <Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>\n</Relationships>\n')
    fn = f'{out}/AB_Rollie_Book_Hybrid_55x13x85.3mf'
    with zipfile.ZipFile(fn, 'w', zipfile.ZIP_DEFLATED) as z:
        for k, v in files.items(): z.writestr(k, v)
    sd = f'{out}/stl'; os.makedirs(sd, exist_ok=True)
    for name, parts, _, _o in objs:
        for k, (man, kind, ext) in enumerate(parts):
            if kind != 'mod': write_stl(f'{sd}/{name.split(" (")[0].replace(" ", "_")}_{k}_{ {1: "grey", 2: "black", 3: "yellow"}[ext]}.stl', man)
    return fn

if __name__ == '__main__':
    r = build()
    a, b, s = r['tray'], r['cover'], r['sleeve']
    allp = [a, b, s] + r['yel_cover'] + r['yel_tray']
    ov = sum((x ^ y).volume() for i, x in enumerate(allp) for y in allp[i + 1:])
    bb = (a + b + s).bounding_box()
    RR = m3.Manifold.batch_boolean(v5.rollups(r['d']), m3.OpType.Add)
    XA, YA = r['d']['axis']
    hit = [g for g in range(0, 166, 5) if (b.translate((-XA, -YA, 0)).rotate((0, 0, -g)).translate((XA, YA, 0)) ^ a).volume() > 0.02]
    print('env', [round(bb[i + 3] - bb[i], 2) for i in range(3)], 'pieces', len(a.decompose()), len(b.decompose()), 'overlap', round(ov, 3),
          'rollups vs tray', round((RR ^ a).volume(), 3), 'swing contacts <=165deg', hit, 'mono bbox', [round(v, 2) for v in r['mono'].bounds])
    if len(sys.argv) > 2:
        print(export(r, sys.argv[1], sys.argv[2]))
