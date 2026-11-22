"""Resolve Bambu Studio system presets (inherits + include) from the public BambuStudio repo into a flat project config
for: Bambu Lab A1 0.4 nozzle + 0.16mm High Quality @BBL A1 + 3 x Bambu PETG HF @BBL A1."""
import json, os
BBL = '/home/user/bambulab/bambustudio/resources/profiles/BBL'
META = {'name', 'inherits', 'include', 'from', 'instantiation', 'setting_id', 'type', 'description'}

def _load(sub, name):
    p = os.path.join(BBL, sub, name + '.json')
    if not os.path.exists(p):
        raise FileNotFoundError(p)
    return json.load(open(p))

def resolve(sub, name):
    d = _load(sub, name)
    base = resolve(sub, d['inherits']) if d.get('inherits') else {}
    for inc in d.get('include', []) or []:
        base.update({k: v for k, v in _load(sub, inc).items() if k not in META})
    base.update({k: v for k, v in d.items() if k not in META})
    return base

def scal(v):
    return v[0] if isinstance(v, list) and len(v) == 1 else v

def project_config(template, colours, overrides):
    """template: the 1.10-era project_settings (format reference). Returns a dict in that format."""
    machine = resolve('machine', 'Bambu Lab A1 0.4 nozzle')
    process = resolve('process', '0.16mm High Quality @BBL A1')
    fil = resolve('filament', 'Bambu PETG HF @BBL A1')
    n = len(colours)
    cfg = {}
    for src in (machine, process):
        for k, v in src.items():
            t = template.get(k)
            if isinstance(t, str): cfg[k] = scal(v) if not isinstance(scal(v), list) else ';'.join(map(str, v))
            elif isinstance(t, list) and isinstance(v, list): cfg[k] = v
            elif isinstance(t, list): cfg[k] = [v]
            else: cfg[k] = scal(v)
    for k, v in fil.items():
        vv = v if isinstance(v, list) else [v]
        cfg[k] = [vv[0]] * n if len(vv) == 1 else (vv * n)[:n] if k not in ('compatible_printers', 'compatible_prints') else vv
    cfg['filament_colour'] = colours
    cfg['default_filament_colour'] = [''] * n
    cfg['filament_settings_id'] = ['Bambu PETG HF @BBL A1'] * n
    cfg['print_settings_id'] = '0.16mm High Quality @BBL A1'
    cfg['printer_settings_id'] = 'Bambu Lab A1 0.4 nozzle'
    cfg['printer_model'] = 'Bambu Lab A1'
    cfg['inherits_group'] = ['0.16mm High Quality @BBL A1'] + ['Bambu PETG HF @BBL A1'] * n + ['Bambu Lab A1 0.4 nozzle'] if 'inherits_group' in template else None
    cfg = {k: v for k, v in cfg.items() if v is not None}
    cfg.update(overrides)
    cfg['different_settings_to_system'] = [';'.join(sorted(k for k in overrides if k in process))] + [''] * n + [';'.join(sorted(k for k in overrides if k in machine))]
    return cfg, machine, process, fil

if __name__ == '__main__':
    import sys
    tmpl = json.load(open(sys.argv[1]))
    cfg, m, p, f = project_config(tmpl, ['#9DA1A3', '#1E1E20', '#FFD00B'], {})
    print('keys', len(cfg), '| template keys', len(tmpl), '| missing vs template', sorted(set(tmpl) - set(cfg))[:25])
    for k in ['printer_model', 'printable_area', 'nozzle_height', 'extruder_clearance_max_radius', 'extruder_clearance_height_to_rod', 'outer_wall_speed',
              'outer_wall_acceleration', 'nozzle_temperature', 'textured_plate_temp', 'filament_type', 'machine_load_filament_time', 'machine_unload_filament_time']:
        print(' ', k, '=', str(cfg.get(k))[:90])
    print('  start gcode lines', str(cfg.get('machine_start_gcode', '')).count('\n'), '| first line:', str(cfg.get('machine_start_gcode', '')).split('\n')[0][:60])
