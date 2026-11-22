"""Test-slice v7 with PrusaSlicer CLI on a Bambu-P1S-like single-nozzle 3-filament setup (AMS-equivalent wipe tower).
Writes a PrusaSlicer 3MF (per-volume extruders + 100% infill modifiers + pause codes), slices at the requested layer heights,
and reports time / filament / tool changes / warnings."""
import sys, os, io, re, subprocess, zipfile, json
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import v7, v5, manifold3d as m3
from v3 import chbox

OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
LH = [float(x) for x in (sys.argv[2:] or ['0.16'])]

def mesh(man):
    mm = man.to_mesh(); return np.asarray(mm.vert_properties)[:, :3].astype(float), np.asarray(mm.tri_verts).astype(int)

def prusa_3mf(path, objects, pauses):
    """objects: list of (name, [(manifold, kind, extruder, settings)], (x, y))"""
    model = io.StringIO(); cfg = io.StringIO()
    model.write('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
                'xmlns:slic3rpe="http://schemas.slic3r.org/3mf/2017/06">\n <metadata name="slic3rpe:Version3mf">1</metadata>\n <resources>\n')
    cfg.write('<?xml version="1.0" encoding="UTF-8"?>\n<config>\n')
    build = []
    for oid, (name, parts, (px, py)) in enumerate(objects, start=1):
        V, T, vols = [], [], []; tri0 = 0
        for man, kind, ext, settings in parts:
            v, t = mesh(man); T.append(t + sum(len(a) for a in V)); V.append(v)
            vols.append((tri0, tri0 + len(t) - 1, kind, ext, settings)); tri0 += len(t)
        V = np.vstack(V); T = np.vstack(T)
        model.write(f'  <object id="{oid}" type="model">\n   <mesh>\n    <vertices>\n')
        for x, y, z in V: model.write(f'     <vertex x="{x:.5f}" y="{y:.5f}" z="{z:.5f}"/>\n')
        model.write('    </vertices>\n    <triangles>\n')
        for a, b, c in T: model.write(f'     <triangle v1="{a}" v2="{b}" v3="{c}"/>\n')
        model.write('    </triangles>\n   </mesh>\n  </object>\n')
        build.append(f'  <item objectid="{oid}" transform="1 0 0 0 1 0 0 0 1 {px} {py} 0" printable="1"/>')
        cfg.write(f' <object id="{oid}" instances_count="1">\n  <metadata type="object" key="name" value="{name}"/>\n')
        for f0, f1, kind, ext, settings in vols:
            cfg.write(f'  <volume firstid="{f0}" lastid="{f1}">\n   <metadata type="volume" key="name" value="{name} {kind} {ext}"/>\n'
                      f'   <metadata type="volume" key="volume_type" value="{"ParameterModifier" if kind == "mod" else "ModelPart"}"/>\n')
            if kind != 'mod': cfg.write(f'   <metadata type="volume" key="extruder" value="{ext}"/>\n')
            for k, v in settings.items(): cfg.write(f'   <metadata type="volume" key="{k}" value="{v}"/>\n')
            cfg.write('  </volume>\n')
        cfg.write(' </object>\n')
    model.write(' </resources>\n <build>\n' + '\n'.join(build) + '\n </build>\n</model>\n'); cfg.write('</config>\n')
    pz = '<?xml version="1.0" encoding="utf-8"?>\n<custom_gcodes_per_print_z>\n' + ''.join(
        f'<code print_z="{z:.3f}" type="1" extruder="1" color="" extra="Insert magnet" gcode="M601"/>\n' for z in pauses) + \
        '<mode value="MultiAsSingle"/>\n</custom_gcodes_per_print_z>\n'
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', '<?xml version="1.0" encoding="UTF-8"?>\n<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                   '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                   '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
        z.writestr('_rels/.rels', '<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   '<Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
        z.writestr('3D/3dmodel.model', model.getvalue()); z.writestr('Metadata/Slic3r_PE_model.config', cfg.getvalue())
        z.writestr('Metadata/Prusa_Slicer_custom_gcode_per_print_z.xml', pz)

def config(lh, path):
    """Bambu P1S + AMS approximated in PrusaSlicer terms. PETG-HF on Textured PEI."""
    c = {
        # printer
        'printer_technology': 'FFF', 'bed_shape': '0x0,256x0,256x256,0x256', 'max_print_height': '250', 'nozzle_diameter': '0.4,0.4,0.4',
        'gcode_flavor': 'marlin2', 'use_relative_e_distances': '1', 'single_extruder_multi_material': '1', 'wipe_tower': '1',
        'wipe_tower_x': '200', 'wipe_tower_y': '200', 'wipe_tower_width': '35', 'wipe_tower_brim_width': '2',
        'machine_max_acceleration_extruding': '10000,10000', 'machine_max_acceleration_x': '20000,20000', 'machine_max_acceleration_y': '20000,20000',
        'machine_max_feedrate_x': '500,500', 'machine_max_feedrate_y': '500,500', 'machine_max_feedrate_z': '20,20',
        'machine_max_jerk_x': '9,9', 'machine_max_jerk_y': '9,9', 'retract_length': '0.8,0.8,0.8', 'retract_speed': '30,30,30',
        'retract_length_toolchange': '2,2,2', 'cooling_tube_retraction': '0', 'parking_pos_retraction': '0', 'extra_loading_move': '0',
        # AMS-like swap: cut + unload + load + purge ~ 70 s on a P1S/AMS (purge volume via wiping_volumes_matrix)
        'filament_unload_time': '35,35,35', 'filament_load_time': '35,35,35', 'filament_toolchange_delay': '0,0,0',
        'filament_cooling_moves': '0,0,0',
        'wiping_volumes_matrix': '0,150,320,280,0,460,150,150,0', 'wiping_volumes_extruders': '70,70,70,70,70,70',
        # filament: PETG-HF grey / black / yellow
        'filament_type': 'PETG;PETG;PETG', 'filament_diameter': '1.75,1.75,1.75', 'filament_density': '1.27,1.27,1.27',
        'filament_colour': '#9DA1A3;#1E1E20;#FFD00B', 'temperature': '250,250,250', 'first_layer_temperature': '250,250,250',
        'bed_temperature': '70,70,70', 'first_layer_bed_temperature': '70,70,70', 'filament_max_volumetric_speed': '22,22,22',
        'fan_always_on': '1,1,1', 'min_fan_speed': '20,20,20', 'max_fan_speed': '50,50,50', 'slowdown_below_layer_time': '6,6,6', 'min_print_speed': '20,20,20',
        # print: quality-first but sensible
        'layer_height': f'{lh}', 'first_layer_height': '0.2', 'perimeters': '4', 'top_solid_layers': '6', 'bottom_solid_layers': '5',
        'fill_density': '50%', 'fill_pattern': 'gyroid', 'perimeter_generator': 'arachne', 'thin_walls': '0', 'seam_position': 'rear',
        'external_perimeters_first': '0', 'extra_perimeters': '0', 'ensure_vertical_shell_thickness': 'ensure_all',
        'external_perimeter_speed': '80', 'perimeter_speed': '150', 'small_perimeter_speed': '50', 'infill_speed': '220',
        'solid_infill_speed': '180', 'top_solid_infill_speed': '90', 'first_layer_speed': '40', 'gap_fill_speed': '80', 'travel_speed': '400',
        'bridge_speed': '40', 'default_acceleration': '6000', 'external_perimeter_acceleration': '3000', 'perimeter_acceleration': '5000',
        'infill_acceleration': '8000', 'top_solid_infill_acceleration': '3000', 'first_layer_acceleration': '800', 'travel_acceleration': '10000',
        'extrusion_width': '0.42', 'external_perimeter_extrusion_width': '0.42', 'first_layer_extrusion_width': '0.5',
        'elefant_foot_compensation': '0.15', 'support_material': '0', 'skirts': '0', 'brim_width': '0', 'avoid_crossing_perimeters': '1',
        'gcode_label_objects': 'firmware', 'complete_objects': '0', 'pause_print_gcode': 'M400 U1', 'gcode_comments': '0', 'layer_gcode': 'G92 E0',
    }
    with open(path, 'w') as f:
        for k, v in c.items(): f.write(f'{k} = {v}\n')

def plate(r):
    P = v7.P
    U = lambda vs: m3.Manifold.batch_boolean(vs, m3.OpType.Add) if len(vs) > 1 else vs[0]
    end_blocks = chbox(-v7.W / 2 - 1, v7.W / 2 + 1, -v7.D, v7.D, -1, P['END'] + 0.5, cv=0.1) + chbox(-v7.W / 2 - 1, v7.W / 2 + 1, -v7.D, v7.D, v7.H - P['END'] - 0.5, v7.H + 1, cv=0.1)
    mod = r['d']['knuckle_mod'] + end_blocks
    tray_rot = lambda m: m.rotate((-90, 0, 0)); cover_rot = lambda m: m.rotate((90, 0, 0))
    def drop(parts):
        bb = U([q for q, k, e, s in parts if k != 'mod']).bounding_box(); out = []
        for q, k, e, s in parts:
            q = q.translate((-(bb[0] + bb[3]) / 2, -(bb[1] + bb[4]) / 2, -bb[2]))
            if k == 'mod': q = q ^ chbox(-200, 200, -200, 200, 0.0, 200, cv=0.1)
            out.append((q, k, e, s))
        return out
    M100 = {'fill_density': '100%', 'perimeters': '6'}
    tray = drop([(tray_rot(r['tray']), 'part', 2, {})] + [(tray_rot(y), 'part', 3, {}) for y in r['yel_tray']] + [(tray_rot(mod), 'mod', 0, M100)])
    cover = drop([(cover_rot(r['cover']), 'part', 1, {})] + [(cover_rot(y), 'part', 3, {}) for y in r['yel_cover']] + [(cover_rot(mod), 'mod', 0, M100)])
    sleeve = drop([(r['sleeve'], 'part', 3, {})])
    badge = drop([(r['badge_black'], 'part', 2, {}), (r['badge_yellow'], 'part', 3, {})]) if r.get('badge_black') is not None else None
    return [('Cover', cover, (110, 128))], [('Tray', tray, (110, 128))], [('Sleeve', sleeve, (128, 128))], ([('Badge', badge, (128, 128))] if badge else [])

def slice_one(p3mf, ini, gcode):
    cmd = ['prusa-slicer', '--export-gcode', '--load', ini, '--output', gcode, p3mf]
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=1800, env=dict(os.environ, QT_QPA_PLATFORM='offscreen'))
    return res

def report(gcode):
    txt = open(gcode, errors='ignore').read()
    tail = txt[-12000:]
    g = lambda pat: (re.search(pat, tail) or re.search(pat, txt))
    t = g(r'estimated printing time \(normal mode\) = ([^\n]+)')
    fil = g(r'filament used \[g\] = ([^\n]+)')
    tc = len(re.findall(r'^T\d', txt, flags=re.M))
    zs = sorted(set(float(z) for z in re.findall(r';Z:([\d.]+)', txt)))
    pauses = len(re.findall(r'^M601|^M400 U1', txt, flags=re.M))
    return dict(time=t.group(1) if t else '?', filament_g=fil.group(1) if fil else '?', toolchanges=tc, layers=len(zs), pauses=pauses, zs=zs)

if __name__ == '__main__':
    r = v7.build()
    pz_cover, pz_tray = r['pause_cover_z'], r['pause_tray_z']
    p1, p2, p3, p4 = plate(r)
    TIMING = os.environ.get('TIMING') == '1'
    prusa_3mf(f'{OUT}/plate1_cover.3mf', p1, [] if (TIMING or not r['pause_cover_z']) else [r['pause_cover_z']])
    prusa_3mf(f'{OUT}/plate2_tray.3mf', p2, [] if (TIMING or not r['pause_tray_z']) else [r['pause_tray_z']])
    prusa_3mf(f'{OUT}/plate3_sleeve.3mf', p3, [])
    if p4: prusa_3mf(f'{OUT}/plate3b_badge.3mf', p4, [])
    for lh in LH:
        ini = f'{OUT}/p1s_petghf_{lh}.ini'; config(lh, ini)
        for name in ('plate1_cover', 'plate2_tray', 'plate3_sleeve') + (('plate3b_badge',) if p4 else ()):
            gc = f'{OUT}/{name}_{lh}.gcode'
            res = slice_one(f'{OUT}/{name}.3mf', ini, gc)
            warn = [l for l in (res.stdout + res.stderr).splitlines() if re.search(r'warn|error|empty|thin|floating|fail', l, re.I)]
            if res.returncode != 0 or not os.path.exists(gc):
                print(lh, name, 'SLICE FAILED', res.returncode, (res.stdout + res.stderr)[-1500:]); continue
            rep = report(gc)
            zs = rep.pop('zs')
            chk = {round(z, 2): any(abs(z - q) < 1e-3 for q in zs) for z in ([r['c_top_z']] if 'cover' in name else [r['t_top_z']] if 'tray' in name else [])}
            print(json.dumps(dict(layer=lh, plate=name, **rep, pocket_tops_are_layers=chk, warnings=warn[:6])))
