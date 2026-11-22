"""Bambu Studio 3MF for v7 (65 x 15 x 88): 3 plates, quality profile, magnet pauses embedded, flush-into-infill."""
import sys, os, json, uuid, zipfile
sys.path.insert(0, os.path.dirname(__file__))
import v7, v5, v6_final, manifold3d as m3
from v3 import chbox

def export(r, out, orig):
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
    PW = 256 * 1.2                                    # Bambu plate pitch (plate size x (1 + 1/5 gap)); 3 plates -> 2 columns
    def origin(i): return ((i % 2) * PW, -(i // 2) * PW)
    objs = [  # name, parts, plate index, object extruder, flush_into_infill
        ('Cover (grey)', drop([(cover_rot(r['cover']), 'normal', GREY)] + [(cover_rot(y), 'normal', YEL) for y in r['yel_cover']] + [(cover_rot(mod_solid), 'mod', 0)]), 0, GREY, True),
        ('Tray (black)', drop([(tray_rot(r['tray']), 'normal', BLACK)] + [(tray_rot(y), 'normal', YEL) for y in r['yel_tray']] + [(tray_rot(mod_solid), 'mod', 0)]), 1, BLACK, True),
        ('Spine sleeve (yellow)', drop([(r['sleeve'], 'normal', YEL)]), 2, YEL, False)]
    files, rels, res, build, sets = {}, [], [], [], []
    plates = {0: [], 1: [], 2: []}
    pid, top, ident = 1, 1000, 300
    for name, parts, pl, oext, fii in objs:
        comps, pcfg = [], []
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
        ox, oy = origin(pl)
        res.append(f'  <object id="{top}" p:UUID="{uuid.uuid4()}" type="model">\n   <components>\n' + '\n'.join(comps) + '\n   </components>\n  </object>')
        build.append(f'  <item objectid="{top}" p:UUID="{uuid.uuid4()}" transform="1 0 0 0 1 0 0 0 1 {ox + 128:.3f} {oy + 128:.3f} 0" printable="1" />')
        dens = '100%' if 'sleeve' in name else '50%'
        sets.append(f'  <object id="{top}">\n    <metadata key="name" value="{name}"/>\n    <metadata key="extruder" value="{oext}"/>\n'
                    f'    <metadata key="sparse_infill_density" value="{dens}"/>\n    <metadata key="sparse_infill_pattern" value="gyroid"/>\n'
                    f'    <metadata key="wall_loops" value="4"/>\n' + (f'    <metadata key="flush_into_infill" value="1"/>\n' if fii else '') +
                    '\n'.join(pcfg) + '\n  </object>')
        plates[pl].append((top, ident))
    pnames = {0: 'Plate 1 - Cover (grey + yellow) - PAUSE at Z 4.04 for magnet', 1: 'Plate 2 - Tray (black + yellow) - PAUSE at Z 10.12 for magnet',
              2: 'Plate 3 - Spine sleeve (yellow)'}
    plate_xml = []
    for pl, items in plates.items():
        inst = '\n'.join(f'    <model_instance>\n      <metadata key="object_id" value="{o}"/>\n      <metadata key="instance_id" value="0"/>\n'
                         f'      <metadata key="identify_id" value="{i}"/>\n    </model_instance>' for o, i in items)
        plate_xml.append(f'  <plate>\n    <metadata key="plater_id" value="{pl + 1}"/>\n    <metadata key="plater_name" value="{pnames[pl]}"/>\n'
                         f'    <metadata key="locked" value="false"/>\n{inst}\n  </plate>')
    title = 'AB Rollie Book v7 65x15x88'
    desc = ('Slim rollie case 65x15x88 mm, 6 channels (rollies up to 6 x 60 mm) + 2 filter-tip bays. PETG-HF: 1 grey (cover), 2 black (tray), 3 yellow. '
            'Hardware: ONLY 2 x 9.51x2.51 mm magnets (sealed in: pause Z 4.04 on plate 1, Z 10.12 on plate 2) + 1.75 mm filament hinge pin. No supports, no glue.')
    files['3D/3dmodel.model'] = ('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
        'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" requiredextensions="p">\n'
        ' <metadata name="Application">BambuStudio-01.10.02.76</metadata>\n <metadata name="BambuStudio:3mfVersion">1</metadata>\n'
        f' <metadata name="Title">{title}</metadata>\n <metadata name="Description">{desc}</metadata>\n'
        ' <resources>\n' + '\n'.join(res) + '\n </resources>\n <build>\n' + '\n'.join(build) + '\n </build>\n</model>\n')
    files['3D/_rels/3dmodel.model.rels'] = ('<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n' +
        '\n'.join(f' <Relationship Target="/{q}" Id="rel-{i+1}" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>' for i, q in enumerate(rels)) + '\n</Relationships>\n')
    files['Metadata/model_settings.config'] = '<?xml version="1.0" encoding="UTF-8"?>\n<config>\n' + '\n'.join(sets) + '\n' + '\n'.join(plate_xml) + '\n</config>\n'
    # magnet pauses: run at the START of the first skin layer above each pocket (verified in the test slice)
    files['Metadata/custom_gcode_per_layer.xml'] = (
        '<?xml version="1.0" encoding="utf-8"?>\n<custom_gcodes_per_layer>\n'
        f'<plate>\n<plate_info id="1"/>\n<layer top_z="{r["pause_cover_z"]:.2f}" type="1" extruder="1" color="" extra="Insert cover magnet, marked face UP" gcode="M400 U1"/>\n<mode value="MultiAsSingle"/>\n</plate>\n'
        f'<plate>\n<plate_info id="2"/>\n<layer top_z="{r["pause_tray_z"]:.2f}" type="1" extruder="2" color="" extra="Insert tray magnet, marked face UP" gcode="M400 U1"/>\n<mode value="MultiAsSingle"/>\n</plate>\n'
        '</custom_gcodes_per_layer>\n')
    ps = v6_final.project_settings(orig, ['#9DA1A3', '#1E1E20', '#FFD00B'])
    ps.update({   # quality-first, still sensible time (test slice: about 4.5 h for all three plates)
        'layer_height': '0.16', 'initial_layer_print_height': '0.2', 'wall_loops': '4', 'top_shell_layers': '6', 'bottom_shell_layers': '5',
        'sparse_infill_density': '50%', 'sparse_infill_pattern': 'gyroid', 'wall_generator': 'arachne', 'seam_position': 'back',
        'outer_wall_speed': '80', 'inner_wall_speed': '150', 'sparse_infill_speed': '250', 'internal_solid_infill_speed': '200',
        'top_surface_speed': '100', 'initial_layer_speed': '40', 'outer_wall_acceleration': '3000', 'top_surface_acceleration': '2000',
        'default_acceleration': '6000', 'elefant_foot_compensation': '0.15', 'enable_support': '0', 'enable_prime_tower': '1', 'print_sequence': 'by layer'})
    files['Metadata/project_settings.config'] = json.dumps(ps, indent=4)
    files['[Content_Types].xml'] = open(f'{orig}/[Content_Types].xml').read()
    files['_rels/.rels'] = ('<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
                            ' <Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>\n</Relationships>\n')
    fn = f'{out}/AB_Rollie_Book_v7_65x15x88.3mf'
    with zipfile.ZipFile(fn, 'w', zipfile.ZIP_DEFLATED) as z:
        for k, v in files.items(): z.writestr(k, v)
    sd = f'{out}/stl'; os.makedirs(sd, exist_ok=True)
    for name, parts, pl, _o, _f in objs:
        for k, (man, kind, ext) in enumerate(parts):
            if kind != 'mod': v6_final.write_stl(f'{sd}/{name.split(" (")[0].replace(" ", "_")}_{k}_{ {1: "grey", 2: "black", 3: "yellow"}[ext]}.stl', man)
    return fn

if __name__ == '__main__':
    r = v7.build(); print(v7.checks(r)); print(export(r, sys.argv[1], sys.argv[2]))
