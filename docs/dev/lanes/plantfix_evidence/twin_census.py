#!/usr/bin/env python3
"""EVIDENCE, NOT A CHECK (lane plantfix, 2026-11-24; rulings R-1 (a)). For every runner plant
whose id has a mech row (tests/mech/sabotages/<id>_*.sh), apply the runner plant through THE
applier's decoder (tests/lib/plants.py `decode`, imported, never re-implemented) and the mech
row's SAB_BEFORE/SAB_AFTER (and site 2) by its own rule (exact replace, mech's apply), each in
memory over the clean tree, and compare the RESULTING FILES. Prints one TSV row per twin:
    runner  id  EQUAL|DIFFERS|RUNNER-STALE|TWIN-STALE  files  detail
then the totals. Usage: python3 -I twin_census.py TREE

The edit list per plant is each runner's own `plant_edits` (bash, the runner's plant_spec and
PERTS extracted verbatim and evaluated): its per-runner edit count is printed so it can be held
to the runner's --plant-check count (89 edits at this lane's tree)."""
import glob, os, re, subprocess, sys
T = os.path.abspath(sys.argv[1])
sys.path.insert(0, os.path.join(T, 'tests/lib'))
import plants  # noqa: E402

RUNNERS = (('memfn/tests/run_g2_win.sh', 'win'), ('memfn/tests/run_g2_pres.sh', 'pres'),
           ('tests/memfn/run_proof.sh', 'win'), ('tests/memfn/run_wreply.sh', 'wreply'))


def block(txt, start, end):
    out, on = [], False
    for ln in txt.split('\n'):
        if ln.startswith(start):
            on = True
        if on:
            out.append(ln)
            if ln == end:
                break
    return '\n'.join(out)


def edits_of(rel, txt):
    """{id: [edit...]} by the runner's own plant_edits, evaluated in bash."""
    one = re.search(r'^plant_edits\(\) \{.*\}$', txt, re.M)   # the one-line form (win, proof)
    pe = one.group(0) if one else block(txt, 'plant_edits() {', '}')
    src = block(txt, 'plant_spec() {', '}') + '\n' + pe
    if 'PERTS=(' in txt:
        src = block(txt, 'PERTS=(', ')') + '\n' + src
    ids = re.search(r'^PLANTS="([^"]*)"', txt, re.M).group(1).split()
    prog = src + '\nfor id in "$@"; do plant_edits "$id" || continue; printf "%s\\0%d\\0" "$id" "${#EDITS[@]}"; printf "%s\\0" "${EDITS[@]}"; done'
    out = subprocess.run(['bash', '-c', prog, 'x'] + ids, capture_output=True, text=True, check=True).stdout
    f = out.split('\0')[:-1]
    res, i = {}, 0
    while i < len(f):
        n = int(f[i + 1])
        res[f[i]] = f[i + 2:i + 2 + n]
        i += 2 + n
    return res


def twin_sites(row):
    out = subprocess.run(['bash', '-c', 'set -a; SAB_FILE=; SAB_BEFORE=; SAB_AFTER=; SAB_FILE2=; SAB_BEFORE2=; '
                          'SAB_AFTER2=; . "$1"; printf "%s\\0" "$SAB_FILE" "$SAB_BEFORE" "$SAB_AFTER" '
                          '"$SAB_FILE2" "$SAB_BEFORE2" "$SAB_AFTER2"', 'x', row],
                         capture_output=True, text=True, check=True).stdout.split('\0')
    sites = [(out[0], out[1], out[2])]
    if out[3].strip():
        sites.append((out[3], out[4], out[5]))
    return sites


def read(cur, p):
    if p not in cur:
        cur[p] = open(p).read() if os.path.isfile(p) else None
    return cur[p]


tot = {}
for rel, dialect in RUNNERS:
    txt = open(os.path.join(T, rel)).read()
    eds = edits_of(rel, txt)
    print('# %s: %d plants, %d edits' % (rel, len(eds), sum(len(v) for v in eds.values())))
    base = os.path.join(T, 'memfn/src') if dialect != 'wreply' else T
    c0 = os.path.join(T, 'docs/design/memfn/span_pick')
    for pid, ed in eds.items():
        rows = glob.glob(os.path.join(T, 'tests/mech/sabotages', pid + '_*.sh'))
        if not rows:
            continue
        a, st = {}, 'EQUAL'
        for spec in ed:
            p, f, t = plants.decode(dialect, spec, base, c0)
            p = os.path.normpath(p)
            s = read(a, p)
            if s is None or s.count(f) != 1:
                st = 'RUNNER-STALE'
                break
            a[p] = s.replace(f, t)
        b = {}
        for f_, bef, aft in twin_sites(rows[0]):
            p = os.path.normpath(os.path.join(T, f_))
            s = read(b, p)
            if st == 'EQUAL' and (s is None or bef not in s):
                st = 'TWIN-STALE'
                break
            b[p] = s.replace(bef, aft, 1) if s is not None else None
        files = sorted(set(a) | set(b))
        detail = ''
        if st == 'EQUAL':
            clean = {}
            diffs = [p for p in files if a.get(p, read(clean, p)) != b.get(p, read(clean, p))]
            if diffs:
                st = 'DIFFERS'
                # what kind: only comment text, or code
                def strip(x):
                    return re.sub(r'/\*.*?\*/|#[^\n]*|[ \t]+', '', x or '', flags=re.S)
                code = [p for p in diffs if strip(a.get(p, read(clean, p))) != strip(b.get(p, read(clean, p)))]
                detail = ('code differs in ' if code else 'comments/whitespace only in ') + \
                    ','.join(os.path.relpath(p, T) for p in (code or diffs))
        tot[st] = tot.get(st, 0) + 1
        print('%s\t%s\t%s\t%s\t%s' % (os.path.basename(rel), pid, st,
                                      ','.join(os.path.relpath(p, T) for p in files), detail))
print('# twins: %d; %s' % (sum(tot.values()), ', '.join('%s %d' % kv for kv in sorted(tot.items()))))
