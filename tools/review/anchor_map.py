#!/usr/bin/env python3
"""Sabotage anchor map: every mech sabotage row whose SAB_FILE[n] starts with PREFIX,
and the enclosing C function (brace-at-column-0 heuristic) of each anchor hit.
An anchor is SAB_BEFORE[n] as an exact substring of the file (the applier's rule).
For the critic skill's first-unit identity lens: run it over EVERY function a subject
moves or splits. Rows printed STALE or MISSING FILE are findings in themselves.
Adopted from review r91 memfn-archrev (2026-11-24; main accepted process proposal 3).
Usage: python3 -I tools/review/anchor_map.py TREE [PREFIX]   (PREFIX default 'memfn/';
'' = every file)  -> TSV on stdout: row  file  line  function  hits"""
import os, re, sys
D = sys.argv[1]
PREFIX = sys.argv[2] if len(sys.argv) > 2 else 'memfn/'
def field(txt, name):
    m = re.search(r'^' + re.escape(name) + r"=(['\"])", txt, re.M)
    if not m: return None
    q = m.group(1); i = m.end(); out = []
    while i < len(txt):
        c = txt[i]
        if q == "'" and txt.startswith("'\\''", i): out.append("'"); i += 4; continue
        if q == '"' and c == '\\' and i + 1 < len(txt): out.append(txt[i+1]); i += 2; continue
        if c == q: break
        out.append(c); i += 1
    return ''.join(out)
cache = {}
def funcs(path):
    if path in cache: return cache[path]
    L = open(os.path.join(D, path), encoding='utf-8', errors='replace').read().split('\n')
    owner = [''] * (len(L) + 1); cur = ''; last = ''
    for i, l in enumerate(L, 1):
        if re.match(r'^[A-Za-z_].*\(', l) and not l.rstrip().endswith(';'): last = l.strip()[:70]
        if l.startswith('{'): cur = last
        owner[i] = cur if cur else '(file scope)'
        if l.startswith('}'): cur = ''
    cache[path] = (L, owner); return cache[path]
sd = os.path.join(D, 'tests/mech/sabotages')
print('row\tfile\tline\tfunction\thits')
for fn in sorted(os.listdir(sd)):
    if not fn.endswith('.sh'): continue
    txt = open(os.path.join(sd, fn), encoding='utf-8', errors='replace').read()
    rid = field(txt, 'SAB_ID') or fn
    for suf in [''] + [str(k) for k in range(2, 10)]:
        sf = field(txt, 'SAB_FILE' + suf); b = field(txt, 'SAB_BEFORE' + suf)
        if not sf or not b or not sf.startswith(PREFIX): continue
        if not os.path.exists(os.path.join(D, sf)): print(f'{rid}\t{sf}\t-\tMISSING FILE\t0'); continue
        L, owner = funcs(sf)
        full = '\n'.join(L); hits = []; j = full.find(b)
        while j >= 0: hits.append(full.count('\n', 0, j) + 1); j = full.find(b, j + 1)
        if not hits: print(f'{rid}\t{sf}\t-\tSTALE (SAB_BEFORE{suf} not a substring)\t0')
        for h in hits: print(f'{rid}\t{sf}\t{h}\t{owner[h]}\t{len(hits)}')
