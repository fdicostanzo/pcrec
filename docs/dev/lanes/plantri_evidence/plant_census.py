#!/usr/bin/env python3
"""EVIDENCE, NOT A CHECK (lane plantri, 2026-11-24). Static census of the runner-embedded
source plants: decodes each exactly as its runner's own apply code does (rules named in
plantri_report.md), counts the FROM text in the target. Usage: python3 -I plant_census.py TREE
Findings print as 'RUNNER ID [edit n] STATUS count file'. Runs bash only to evaluate each
runner's own plant_spec function (extracted verbatim); never runs a runner."""
import os, re, subprocess, sys
T = sys.argv[1]
def un_win(s):   # run_g2_win.sh:365, run_proof.sh:120 (python3 -I heredoc)
    return s.replace('\\n', '\n').replace('\\&', '&')
def un_pres(s):  # run_g2_pres.sh:676 (un())
    return s.replace('\\\\n', '\x00').replace('\\n', '\n').replace('\x00', '\\n').replace('\\&', '&')
def un_wr(s):    # run_wreply.sh:99 (newline only)
    return s.replace('\\n', '\n')
def spec_fn(path):
    src = open(path).read().split('\n'); out = []; on = False
    for ln in src:
        if ln.startswith('plant_spec() {'): on = True
        if on:
            out.append(ln)
            if ln == '}': break
    return '\n'.join(out)
def run_spec(path, pid):
    p = subprocess.run(['bash', '-c', spec_fn(path) + '\nplant_spec "$1"', 'x', pid],
                       capture_output=True, text=True)
    return p.returncode, p.stdout
def ids_of(path):
    m = re.search(r'^PLANTS="([^"]*)"', open(path).read(), re.M)
    return m.group(1).split() if m else []
def split3(spec):  # run_g2_win.sh:361 / run_proof.sh:116 / run_g2_pres.sh:670 shell splits
    f, rest = spec.split('@@', 1)
    a, b = rest.split('@@', 1) if '@@' in rest else (rest, '')
    return f, a, b
rows = []
def count(runner, pid, n, fpath, a):
    if not os.path.isfile(fpath): rows.append((runner, pid, n, 'MISSING FILE', 0, fpath)); return None
    s = open(fpath).read(); c = s.count(a)
    st = 'OK' if c == 1 else 'STALE' if c == 0 else 'AMBIGUOUS'
    rows.append((runner, pid, n, st, c, fpath)); return s
for runner, rel, un, base in (('run_g2_win', 'memfn/tests/run_g2_win.sh', un_win, 'memfn/src'),
                              ('run_proof', 'tests/memfn/run_proof.sh', un_win, 'memfn/src')):
    path = os.path.join(T, rel)
    for pid in ids_of(path):
        rc, out = run_spec(path, pid)
        if rc: rows.append((runner, pid, 1, 'NO PLANT_SPEC', 0, '')); continue
        f, a, b = split3(out.rstrip('\n'))
        count(runner, pid, 1, os.path.join(T, base, f), un(a))
# pres: one spec per output line, edits applied in order to a per-plant copy
rel = 'memfn/tests/run_g2_pres.sh'; path = os.path.join(T, rel)
for pid in ids_of(path):
    rc, out = run_spec(path, pid)
    if rc: rows.append(('run_g2_pres', pid, 1, 'NO PLANT_SPEC', 0, '')); continue
    cur = {}
    for n, spec in enumerate([l for l in out.split('\n') if l], 1):
        f, a, b = split3(spec); a, b = un_pres(a), un_pres(b)
        fp = os.path.join(T, 'docs/design/memfn/span_pick', f[4:]) if f.startswith('@c0/') else os.path.join(T, 'memfn/src', f)
        if fp not in cur: cur[fp] = open(fp).read() if os.path.isfile(fp) else None
        if cur[fp] is None: rows.append(('run_g2_pres', pid, n, 'MISSING FILE', 0, fp)); continue
        c = cur[fp].count(a)
        rows.append(('run_g2_pres', pid, n, 'OK' if c == 1 else 'STALE' if c == 0 else 'AMBIGUOUS', c, fp))
        if c == 1: cur[fp] = cur[fp].replace(a, b)
# wreply: PERTS first (both, in order), then the spec; S1414 alone
rel = 'tests/memfn/run_wreply.sh'; path = os.path.join(T, rel)
txt = open(path).read()
perts = re.findall(r"^    '(src/gen/[^']*@@[^']*@@[^']*)'$", txt, re.M)
for pid in ids_of(path):
    rc, out = run_spec(path, pid)
    if rc: rows.append(('run_wreply', pid, 1, 'NO PLANT_SPEC', 0, '')); continue
    cur = {}
    seq = ([] if pid == 'S1414' else perts) + [out.rstrip('\n')]
    for n, spec in enumerate(seq, 1):
        parts = spec.split('@@')
        if len(parts) != 3: rows.append(('run_wreply', pid, n, 'UNDECODED', len(parts), spec[:40])); continue
        f, a, b = parts; a, b = un_wr(a), un_wr(b); fp = os.path.join(T, f)
        if fp not in cur: cur[fp] = open(fp).read() if os.path.isfile(fp) else None
        if cur[fp] is None: rows.append(('run_wreply', pid, n, 'MISSING FILE', 0, fp)); continue
        c = cur[fp].count(a)
        tag = pid if n == len(seq) else pid + ' (PERT %d)' % n
        rows.append(('run_wreply', tag, n, 'OK' if c == 1 else 'STALE' if c == 0 else 'AMBIGUOUS', c, fp))
        if c == 1: cur[fp] = cur[fp].replace(a, b)
for r in rows: print('\t'.join(map(str, r)))
