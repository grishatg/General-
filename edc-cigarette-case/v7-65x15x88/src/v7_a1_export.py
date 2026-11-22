"""Bambu Studio 3MF for v7 on a Bambu Lab A1 (+ AMS lite): ONE plate, print BY OBJECT, snap-in magnets (no pauses)."""
import sys, os, json, uuid, zipfile
sys.path.insert(0, os.path.dirname(__file__))
import v7, v6_final, a1_safe, manifold3d as m3
from v3 import chbox

GAP_BY_OBJECT = 74.0     # A1: extruder_clearance_max_radius = 73 mm (Bambu doubles half-radius offsets -> 73 mm hull-to-hull)
COLOURS = ['#9DA1A3', '#1E1E20', '#FFD00B']

def layout():
    """Plate positions (object centres). Footprints: cover/tray 65 x 88, sleeve ~5 x 5."""
    cx_cover = 8 + 32.5
    cx_tray = cx_cover + 65 + GAP_BY_OBJECT
    cy = 16 + 44
    return {'cover': (cx_cover, cy), 'tray': (cx_tray, cy), 'sleeve': ((cx_cover + cx_tray) / 2, 200.0)}

def export(r, out, orig, geometry_only=False):
    os.makedirs(out, exist_ok=True)
    P = v7.P; W, D, H = v7.W, v7.D, v7.H
    U = lambda vs: m3.Manifold.batch_boolean(vs, m3.OpType.Add) if len(vs) > 1 else vs[0]
    end_blocks = chbox(-W / 2 - 1, W / 2 + 1, -D, D, -1, P['END'] + 0.5, cv=0.1) + chbox(-W / 2 - 1, W / 2 + 1, -D, D, H - P['END'] - 0.5, H + 1, cv=0.1)
    mod_solid = r['d']['knuckle_mod'] + end_blocks
    tray_rot = lambda m: m.rotate((-90, 0, 0)); cover_rot = lambda m: m.rotate((90, 0, 0))
    def drop(parts):
        bb = U([q for q, k, e in parts if k != 'mod']).bounding_box(); outp = []
        for q, k, e in parts:
            q = q.translate((-(bb[0] + bb[3]) / 2, -(bb[1] + bb[4]) / 2, -bb[2]))
            if k == 'mod': q = q ^ chbox(-300, 300, -300, 300, 0.0, 300, cv=0.1)
            outp.append((q, k, e))
        return outp
    GREY, BLACK, YEL = 1, 2, 3
    pos = layout()
    objs = [('Cover (grey)', drop([(cover_rot(r['cover']), 'normal', GREY)] + [(cover_rot(y), 'normal', YEL) for y in r['yel_cover']] + [(cover_rot(mod_solid), 'mod', 0)]), pos['cover'], GREY, True),
            ('Tray (black)', drop([(tray_rot(r['tray']), 'normal', BLACK)] + [(tray_rot(y), 'normal', YEL) for y in r['yel_tray']] + [(tray_rot(mod_solid), 'mod', 0)]), pos['tray'], BLACK, True),
            ('Spine sleeve (yellow)', drop([(r['sleeve'], 'normal', YEL)]), pos['sleeve'], YEL, False)]
    files, rels, res, build, sets, inst, hulls = {}, [], [], [], [], [], {}
    pid, top, ident = 1, 1000, 300
    for name, parts, (px, py), oext, fii in objs:
        comps, pcfg = [], []
        bb = U([q for q, k, e in parts if k != 'mod']).bounding_box()
        hulls[name] = (px + bb[0], py + bb[1], px + bb[3], py + bb[4], bb[5])
        for k, (man, kind, ext) in enumerate(parts):
            path = f'3D/Objects/object_{pid}.model'; files[path] = v6_final.model_xml(pid, man); rels.append(path)
            comps.append(f'    <component p:path="/{path}" objectid="{pid}" p:UUID="{uuid.uuid4()}" transform="1 0 0 0 1 0 0 0 1 0 0 0" />')
            if kind == 'mod':
                pcfg.append(f'    <part id="{pid}" subtype="modifier_part">\n      <metadata key="name" value="100% infill - hinge, end blocks, magnet clasp"/>\n'
                            f'      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>\n      <metadata key="sparse_infill_density" value="100%"/>\n'
                            f'      <metadata key="wall_loops" value="6"/>\n    </part>')
            else:
                nm = {GREY: 'grey shell', BLACK: 'black shell', YEL: 'yellow'}[ext]
                pcfg.append(f'    <part id="{pid}" subtype="normal_part">\n      <metadata key="name" value="{nm} {k}"/>\n'
                            f'      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>\n      <metadata key="extruder" value="{ext}"/>\n    </part>')
            pid += 1
        top += 1; ident += 1
        res.append(f'  <object id="{top}" p:UUID="{uuid.uuid4()}" type="model">\n   <components>\n' + '\n'.join(comps) + '\n   </components>\n  </object>')
        build.append(f'  <item objectid="{top}" p:UUID="{uuid.uuid4()}" transform="1 0 0 0 1 0 0 0 1 {px:.3f} {py:.3f} 0" printable="1" />')
        dens = '100%' if 'sleeve' in name else '50%'
        sets.append(f'  <object id="{top}">\n    <metadata key="name" value="{name}"/>\n    <metadata key="extruder" value="{oext}"/>\n'
                    f'    <metadata key="sparse_infill_density" value="{dens}"/>\n    <metadata key="sparse_infill_pattern" value="gyroid"/>\n'
                    f'    <metadata key="wall_loops" value="4"/>\n' + (f'    <metadata key="flush_into_infill" value="1"/>\n' if fii else '') +
                    '\n'.join(pcfg) + '\n  </object>')
        inst.append(f'    <model_instance>\n      <metadata key="object_id" value="{top}"/>\n      <metadata key="instance_id" value="0"/>\n'
                    f'      <metadata key="identify_id" value="{ident}"/>\n    </model_instance>')
    title = 'AB Rollie Book v7 - A1 by object'
    desc = ('Slim rollie case 65x15x88 mm, 6 channels (rollies up to 6 x 60 mm) + 2 filter-tip bays. Bambu Lab A1 + AMS lite, PETG-HF: 1 grey (cover), 2 black (tray), 3 yellow. '
            'ONE plate, print by object. Hardware: ONLY 2 x 9.51x2.51 mm magnets (snap into the printed pockets after printing) + 1.75 mm filament hinge pin. No supports, no glue, no pauses.')
    files['3D/3dmodel.model'] = ('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
        'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" requiredextensions="p">\n'
        ' <metadata name="Application">BambuStudio-01.10.02.76</metadata>\n <metadata name="BambuStudio:3mfVersion">1</metadata>\n'
        f' <metadata name="Title">{title}</metadata>\n <metadata name="Description">{desc}</metadata>\n'
        ' <resources>\n' + '\n'.join(res) + '\n </resources>\n <build>\n' + '\n'.join(build) + '\n </build>\n</model>\n')
    files['3D/_rels/3dmodel.model.rels'] = ('<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n' +
        '\n'.join(f' <Relationship Target="/{q}" Id="rel-{i+1}" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>' for i, q in enumerate(rels)) + '\n</Relationships>\n')
    files['Metadata/model_settings.config'] = ('<?xml version="1.0" encoding="UTF-8"?>\n<config>\n' + '\n'.join(sets) +
        '\n  <plate>\n    <metadata key="plater_id" value="1"/>\n    <metadata key="plater_name" value="AB Rollie Book - by object"/>\n'
        '    <metadata key="locked" value="false"/>\n    <metadata key="print_sequence" value="by object"/>\n' + '\n'.join(inst) + '\n  </plate>\n</config>\n')
    # ---- project settings: Bambu's own A1 presets, resolved, in the project-file format ----
    tmpl = json.load(open(f'{orig}/Metadata/project_settings.config'))
    n = len(COLOURS)
    overrides = {'layer_height': '0.16', 'initial_layer_print_height': '0.2', 'wall_loops': '4', 'top_shell_layers': '6', 'bottom_shell_layers': '5',
                 'sparse_infill_density': '50%', 'sparse_infill_pattern': 'gyroid', 'wall_generator': 'arachne', 'seam_position': 'back',
                 'elefant_foot_compensation': '0.15', 'enable_support': '0', 'enable_prime_tower': '0', 'print_sequence': 'by object',
                 'curr_bed_type': 'Textured PEI Plate'}
    cfg, _src = a1_safe.project_config(tmpl, COLOURS, overrides)   # proven key set + order, A1 release values
    probs = a1_safe.check(cfg, tmpl); assert not probs, probs
    if not geometry_only:
        files['Metadata/project_settings.config'] = json.dumps(cfg, indent=4)
    files['[Content_Types].xml'] = open(f'{orig}/[Content_Types].xml').read()
    files['_rels/.rels'] = ('<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
                            ' <Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>\n</Relationships>\n')
    fn = f'{out}/AB_Rollie_Book_v7_A1_' + ('geometry_only' if geometry_only else 'by_object') + '.3mf'
    with zipfile.ZipFile(fn, 'w', zipfile.ZIP_DEFLATED) as z:
        for k, v in files.items(): z.writestr(k, v)
    sd = f'{out}/stl'; os.makedirs(sd, exist_ok=True)
    for name, parts, _p, _o, _f in objs:
        for k, (man, kind, ext) in enumerate(parts):
            if kind != 'mod': v6_final.write_stl(f'{sd}/{name.split(" (")[0].replace(" ", "_")}_{k}_{ {1: "grey", 2: "black", 3: "yellow"}[ext]}.stl', man)
    return fn, hulls, cfg

if __name__ == '__main__':
    r = v7.build(); print(v7.checks(r))
    fn, hulls, cfg = export(r, sys.argv[1], sys.argv[2])
    fn2, _h, _c = export(r, sys.argv[1], sys.argv[2], geometry_only=True); print(fn2)
    names = list(hulls)
    def gap(a, b):
        ax0, ay0, ax1, ay1, _ = hulls[a]; bx0, by0, bx1, by1, _ = hulls[b]
        dx = max(bx0 - ax1, ax0 - bx1, 0); dy = max(by0 - ay1, ay0 - by1, 0); return round((dx * dx + dy * dy) ** 0.5, 1)
    print(fn); print('heights', {k: round(v[4], 2) for k, v in hulls.items()}, '| min gaps', {f'{a}|{b}': gap(a, b) for i, a in enumerate(names) for b in names[i + 1:]})
    print('on bed', all(0 <= v[0] and 0 <= v[1] and v[2] <= 256 and v[3] <= 256 for v in hulls.values()), '| printer', cfg['printer_model'], cfg['print_settings_id'], cfg['print_sequence'], 'prime tower', cfg['enable_prime_tower'])
