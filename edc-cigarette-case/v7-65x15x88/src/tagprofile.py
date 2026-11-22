"""Resolve Bambu presets as they exist at a given release tag (reads blobs with git show; no checkout)."""
import json, subprocess, re
REPO = '/home/user/bambulab/bambustudio'
META = {'name', 'inherits', 'include', 'from', 'instantiation', 'setting_id', 'type', 'description'}
def show(tag, path):
    return subprocess.run(['git', '-C', REPO, 'show', f'{tag}:{path}'], capture_output=True, text=True, check=True).stdout
def load(tag, sub, name):
    return json.loads(show(tag, f'resources/profiles/BBL/{sub}/{name}.json'))
def resolve(tag, sub, name):
    d = load(tag, sub, name)
    base = resolve(tag, sub, d['inherits']) if d.get('inherits') else {}
    for inc in d.get('include', []) or []:
        base.update({k: v for k, v in load(tag, sub, inc).items() if k not in META})
    base.update({k: v for k, v in d.items() if k not in META})
    return base
def placeholders(g):
    g = g if isinstance(g, str) else ''.join(g)
    toks = set(re.findall(r'\{\s*([A-Za-z_][A-Za-z0-9_]*)', g)) | set(re.findall(r'\[([A-Za-z_][A-Za-z0-9_]*)\]', g))
    return toks - {'if', 'else', 'elsif', 'endif', 'local', 'global', 'is_nil', 'int', 'abs', 'min', 'max', 'round', 'digits', 'zdigits', 'true', 'false', 'and', 'or', 'not'}
if __name__ == '__main__':
    import sys
    sets = {}
    for t in sys.argv[1:]:
        m = resolve(t, 'machine', 'Bambu Lab A1 0.4 nozzle')
        g = m.get('machine_start_gcode', ''); sets[t] = placeholders(g)
        print(t, 'start gcode lines', (g if isinstance(g, str) else ''.join(g)).count('\n'), 'placeholders', len(sets[t]))
    ts = sys.argv[1:]
    for a, b in zip(ts, ts[1:]):
        print(f'{a} -> {b}: added {sorted(sets[b] - sets[a])} removed {sorted(sets[a] - sets[b])}')
