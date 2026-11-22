"""Emulate Bambu Studio's project-config loader checks against real option definitions at given release tags."""
import re, json, zipfile, sys
import tagprofile as TP

def optiondefs(tag):
    src = TP.show(tag, 'src/libslic3r/PrintConfig.cpp')
    opts = dict(re.findall(r'this->add(?:_nullable)?\("([A-Za-z0-9_]+)",\s*(co[A-Za-z]+)\)', src))
    # enum key maps: static t_config_enum_values s_keys_map_X { {"val", ...}, ... };
    maps = {}
    for name, body in re.findall(r's_keys_map_([A-Za-z0-9_]+)\s*\{(.*?)\};', src, flags=re.S):
        maps[name] = set(re.findall(r'\{\s*"([^"]+)"\s*,', body))
    # option -> enum type: def = this->add("key", coEnum); ... def->enum_keys_map = &ConfigOptionEnum<Type>::get_enum_values();
    enum_of = {}
    for m in re.finditer(r'this->add(?:_nullable)?\("([A-Za-z0-9_]+)",\s*coEnums?\)(.*?)(?=this->add|\Z)', src, flags=re.S):
        t = re.search(r'ConfigOptionEnum(?:sGeneric)?<([A-Za-z0-9_]+)>::get_enum_values', m.group(2))
        if t: enum_of[m.group(1)] = t.group(1)
    legacy_src = src[src.find('void PrintConfigDef::handle_legacy'):]
    ignore = set(re.findall(r'"([a-z0-9_]+)"', legacy_src[:legacy_src.find('if (ignore.find(opt_key)')])) if 'ignore' in legacy_src else set()
    return opts, maps, enum_of, ignore

def validate_cfg(cfg, defs, label):
    opts, maps, enum_of, ignore = defs
    problems = []
    for i, (k, v) in enumerate(cfg.items()):
        if isinstance(v, list):
            if any(not isinstance(x, str) for x in v): problems.append(f'[{label}] key #{i} {k}: array with non-string -> loader STOPS here')
        elif not isinstance(v, str):
            problems.append(f'[{label}] key #{i} {k}: non-string value')
        if k in ('version', 'name', 'from', 'inherits', 'is_custom_defined', 'setting_id', 'type', 'description', 'instantiation', 'url', 'filament_id'):
            continue
        if k not in opts and k not in ignore:
            problems.append(f'[{label}] key #{i} {k}: unknown option')
            continue
        t = opts.get(k, '')
        if t in ('coEnum', 'coEnums') and k in enum_of:
            allowed = maps.get(enum_of[k].replace('Type', '') if enum_of[k].replace('Type', '') in maps else enum_of[k], None)
            if allowed is None:
                for cand in (enum_of[k], enum_of[k].replace('Type', ''), enum_of[k] + 'Type'):
                    if cand in maps: allowed = maps[cand]; break
            vals = v if isinstance(v, list) else v.split(',')
            if allowed and any(x not in allowed for x in vals if x != ''):
                problems.append(f'[{label}] {k}: enum value(s) {vals} not in {sorted(allowed)[:8]}')
    if not cfg.get('filament_colour'): problems.append(f'[{label}] filament_colour empty -> "Invalid configuration file"')
    if 'extruder_variant_list' in cfg:
        n = len(cfg.get('filament_colour', [])); fev = cfg.get('filament_extruder_variant', []); fsi = cfg.get('filament_self_index', [])
        if len(fsi) != len(fev) or len(fev) < n: problems.append(f'[{label}] multi-extruder variant keys inconsistent (older releases throw "Invalid configuration file")')
    return problems

def validate_3mf(path, tags):
    z = zipfile.ZipFile(path)
    cfg = json.loads(z.read('Metadata/project_settings.config'))
    ms = z.read('Metadata/model_settings.config').decode()
    keys_ms = set(re.findall(r'<metadata key="([a-z_0-9]+)"', ms)) - {'name', 'matrix', 'extruder', 'source_object_id', 'source_volume_id', 'source_offset_x',
                                                                     'source_offset_y', 'source_offset_z', 'plater_id', 'plater_name', 'locked', 'object_id',
                                                                     'instance_id', 'identify_id', 'thumbnail_file', 'thumbnail_no_light_file', 'top_file', 'pick_file'}
    out = {}
    for t in tags:
        defs = optiondefs(t)
        pr = validate_cfg(cfg, defs, t)
        pr += [f'[{t}] model_settings key {k}: unknown option' for k in sorted(keys_ms) if k not in defs[0]]
        out[t] = pr
    return out, cfg

if __name__ == '__main__':
    path, tags = sys.argv[1], sys.argv[2:]
    res, cfg = validate_3mf(path, tags)
    for t, pr in res.items():
        print(f'{t}: {len(pr)} problem(s)')
        for p in pr[:12]: print('   ', p)
