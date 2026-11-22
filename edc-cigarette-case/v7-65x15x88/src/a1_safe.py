"""Version-safe A1 project config.
Uses ONLY the key set (and key order) of a real Bambu project that loads, with values from Bambu's released A1 presets.
Bambu's loader aborts the whole config at the first unknown key, so no keys outside that proven set are written."""
import json
import tagprofile as TP, bbsvalidate as BV

TAG_VALUES = 'v02.08.04.61'
TAG_CHECK = ('v02.03.01.51', 'v02.09.01.70')
PER_FILAMENT_EXTRA = {'activate_air_filtration', 'additional_cooling_fan_speed', 'chamber_temperatures', 'close_fan_the_first_x_layers',
                      'complete_print_exhaust_fan_speed', 'cool_plate_temp', 'cool_plate_temp_initial_layer', 'default_filament_colour',
                      'during_print_exhaust_fan_speed', 'enable_overhang_bridge_fan', 'enable_pressure_advance', 'eng_plate_temp',
                      'eng_plate_temp_initial_layer', 'fan_cooling_layer_time', 'fan_max_speed', 'fan_min_speed', 'full_fan_speed_layer',
                      'hot_plate_temp', 'hot_plate_temp_initial_layer', 'nozzle_temperature', 'nozzle_temperature_initial_layer',
                      'nozzle_temperature_range_high', 'nozzle_temperature_range_low', 'overhang_fan_speed', 'overhang_fan_threshold',
                      'overhang_threshold_participating_cooling', 'pressure_advance', 'reduce_fan_stop_start_freq', 'required_nozzle_HRC',
                      'slow_down_for_layer_cooling', 'slow_down_layer_time', 'slow_down_min_speed', 'supertack_plate_temp',
                      'supertack_plate_temp_initial_layer', 'temperature_vitrification', 'textured_plate_temp', 'textured_plate_temp_initial_layer'}

def _enum_ok(k, value, defs_list):
    for opts, maps, enum_of, ignore in defs_list:
        if opts.get(k) not in ('coEnum', 'coEnums') or k not in enum_of: continue
        t = enum_of[k]; allowed = None
        for cand in (t, t.replace('Type', ''), t + 'Type'):
            if cand in maps: allowed = maps[cand]; break
        if allowed is None: continue
        vals = value if isinstance(value, list) else str(value).split(',')
        if any(x not in allowed for x in vals if x != ''): return False
    return True

def project_config(template, colours, overrides):
    machine = TP.resolve(TAG_VALUES, 'machine', 'Bambu Lab A1 0.4 nozzle')
    process = TP.resolve(TAG_VALUES, 'process', '0.16mm High Quality @BBL A1')
    fil = TP.resolve(TAG_VALUES, 'filament', 'Bambu PETG HF @BBL A1')
    defs = [BV.optiondefs(t) for t in TAG_CHECK]
    n, n0 = len(colours), len(template['filament_colour'])
    cfg, src = {}, {}
    for k, tv in template.items():                        # proven key set, proven order
        if k in fil and k not in machine and k not in process:
            v = fil[k]; vv = v if isinstance(v, list) else [v]
            val = [str(vv[0])] * n if len(vv) == 1 else [str(x) for x in (vv * n)[:n]]
            if k in ('compatible_printers', 'compatible_prints'): val = [str(x) for x in vv]
            src[k] = 'filament'
        elif k in machine or k in process:
            v = machine.get(k, process.get(k))
            if isinstance(tv, str):
                val = str(v[0]) if isinstance(v, list) and v else (str(v) if not isinstance(v, list) else tv)
            else:
                val = [str(x) for x in v] if isinstance(v, list) else [str(v)]
            if not _enum_ok(k, val, defs): val = tv; src[k] = 'template (enum differs across releases)'
            else: src[k] = 'machine' if k in machine else 'process'
        else:
            if isinstance(tv, list) and len(tv) == n0 and (k.startswith('filament_') or k in PER_FILAMENT_EXTRA):
                val = (tv + [tv[-1]] * n)[:n]
            else:
                val = tv
            src[k] = 'template'
        cfg[k] = val
    cfg['filament_colour'] = list(colours)
    if 'default_filament_colour' in cfg: cfg['default_filament_colour'] = [''] * n
    cfg['filament_settings_id'] = ['Bambu PETG HF @BBL A1'] * n
    cfg['filament_ids'] = [str(fil.get('filament_id', 'GFG02'))] * n
    cfg['print_settings_id'] = '0.16mm High Quality @BBL A1'
    cfg['printer_settings_id'] = 'Bambu Lab A1 0.4 nozzle'
    cfg['printer_model'] = 'Bambu Lab A1'
    cfg['printer_variant'] = '0.4'
    cfg['print_compatible_printers'] = ['Bambu Lab A1 0.4 nozzle']
    M = [[0, 150, 320], [280, 0, 460], [150, 150, 0]]
    cfg['flush_volumes_matrix'] = [str(x) for row in M for x in row]
    cfg['flush_volumes_vector'] = ['140'] * (2 * n)
    for k, v in overrides.items():
        assert k in template, f'override {k} is not in the proven key set'
        cfg[k] = v
    cfg['different_settings_to_system'] = [';'.join(sorted(k for k in overrides if k in process))] + [''] * n + [';'.join(sorted(k for k in overrides if k in machine))]
    return cfg, src

def check(cfg, template):
    problems = []
    extra = [k for k in cfg if k not in template]
    if extra: problems.append(f'keys outside the proven set: {extra[:8]}')
    if list(cfg)[:len(template)] != list(template)[:len(cfg)]: problems.append('key order differs from the proven file')
    n = len(cfg['filament_colour'])
    for k, v in cfg.items():
        if isinstance(v, list) and any(not isinstance(x, str) for x in v): problems.append(f'{k}: non-string array element')
        if not isinstance(v, (str, list)): problems.append(f'{k}: non-string value')
        tv = template[k]
        if isinstance(tv, list) and len(tv) == len(template['filament_colour']) and isinstance(v, list) and len(v) not in (n, 1) and k not in ('compatible_printers', 'different_settings_to_system', 'start_end_points', 'wipe_tower_x', 'wipe_tower_y') and not k.startswith('machine_'):
            problems.append(f'{k}: per-filament list length {len(v)} != {n}')
    if len(cfg['different_settings_to_system']) != n + 2: problems.append('different_settings_to_system length')
    if len(cfg['flush_volumes_matrix']) != n * n: problems.append('flush matrix size')
    return problems
