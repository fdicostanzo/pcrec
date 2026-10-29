#!/usr/bin/env python3
"""p48 census reader: census.py's TSV -> the Population section's counts.

usage: census_read.py CENSUS_TSV DEFAULT_PPM_TSV [--list N]

A machine's edge/skip identity across twins is (machine, kind, span, accept,
membership) -- never the state number, because the pass renumbers heads to the
top rows and the twins' numberings differ.
"""
import collections, sys


def ppm_table(path):
    t = {}
    for l in open(path):
        if l.startswith('#') or not l.strip():
            continue
        b, v = l.split()[:2]
        t[int(b)] = int(v)
    return t


def members(hexs):
    out = []
    for i, ch in enumerate(hexs):
        v = int(ch, 16)
        for j in range(4):
            if v >> j & 1:
                out.append(i * 4 + j)
    return out


def parse(v):
    if v in ('FAIL', 'TIMEOUT'):
        return None
    eng, _, tr = v.partition('|')
    sites, seed = [], {}
    for item in tr.split(';') if tr else []:
        f = item.split(',')
        if f[0] == 'P48M':
            seed[f[1]] = f[2] == 'seedhead=1'
        elif f[0] == 'P48':
            # P48,machine,kind,state,span,acc,hex,is_s0,nscan
            sites.append((f[1], f[2], int(f[4]), int(f[5]), f[6], f[7] == '1'))
    return eng, sites, seed


def main():
    rows = collections.defaultdict(dict)
    for l in open(sys.argv[1], errors='replace'):
        p = l.rstrip('\n').split('\t')
        if len(p) < 4:
            continue
        rows[(p[0], p[1])][p[2]] = parse(p[3])
    ppm = ppm_table(sys.argv[2])
    nlist = int(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[3] == '--list' else 0
    mass = lambda h: sum(ppm.get(b, 0) for b in members(h)) / 1e6
    C = collections.Counter()
    ex = collections.defaultdict(list)
    relax_mass = collections.Counter()
    for (src, pat), arms in rows.items():
        bench = src.startswith('bench:')
        pop = 'bench' if bench else 'corpus'
        C[pop, 'patterns'] += 1
        s, g, r = arms.get('set'), arms.get('single'), arms.get('relax')
        if not s or not g or not r:
            C[pop, 'any-arm-failed'] += 1
            continue
        key = lambda x: (x[0], x[2], x[3], x[4])
        sedge = {key(x) for x in s[1] if x[1] == 'edge'}
        gedge = {key(x) for x in g[1] if x[1] == 'edge'}
        gskip = {key(x)[0:1] + (0, key(x)[2], key(x)[3]) for x in g[1] if x[1] == 'skip'}
        redge = {key(x) for x in r[1] if x[1] == 'edge'}
        sskip = {(x[0], 0, x[3], x[4]) for x in s[1] if x[1] == 'skip'}
        if sedge:
            C[pop, 'set: artifacts with >=1 edge'] += 1
        for e in sedge:
            C[pop, 'set: edges (' + e[0] + (', bounded)' if e[1] > 0 else ', unbounded)')] += 1
        if sedge != gedge:
            C[pop, 'SET movers (edges differ set vs single)'] += 1
            gained = sedge - gedge
            stolen = [e for e in gained if e[1] < 0 and (e[0], 0, e[2], e[3]) in gskip]
            fresh = [e for e in gained if e not in stolen]
            if stolen:
                C[pop, '  SET took a pre-SET STAY state'] += 1
                ex['stolen', pop].append(pat)
            if fresh:
                C[pop, '  SET gained an edge on a state with no run loop before'] += 1
                ex['fresh', pop].append(pat)
            if gedge - sedge:
                C[pop, '  SET lost/changed a pre-SET edge'] += 1
        # entry dispatch: seedhead true on a machine whose edges are all unbounded
        for m, sh in s[2].items():
            if not sh:
                continue
            spans = [x[2] for x in s[1] if x[0] == m and x[1] == 'edge']
            C[pop, 'set: machines with an entry jump (seedhead)'] += 1
            if spans and all(sp < 0 for sp in spans):
                C[pop, '  ... all heads unbounded (jump removed by the bounded-only rule)'] += 1
                ex['jump', pop].append(pat)
            gsh = g[2].get(m, False)
            if not gsh:
                C[pop, '  ... new since SET (single twin has no jump there)'] += 1
        # relaxation: edges relax adds over set
        radd = redge - sedge
        if radd:
            C[pop, 'RELAX adds >=1 edge'] += 1
            ex['relax', pop].append(pat)
            mach_new = {e[0] for e in radd} - {e[0] for e in sedge}
            if mach_new:
                C[pop, '  ... to a machine that had no edge (first edge: loop-shape change)'] += 1
            for e in radd:
                C[pop, 'RELAX added edges (' + e[0] + ')'] += 1
                p = mass(e[3])
                relax_mass[pop, 'p<0.1' if p < 0.1 else 'p<0.5' if p < 0.5 else 'p>=0.5'] += 1
                if (e[0], 0, e[2], e[3]) in sskip:
                    C[pop, '  ... added edge replaces a STAY'] += 1
            if redge - radd != sedge:
                C[pop, '  ... RELAX displaced a set edge (cap of 4)'] += 1
    for pop in ('corpus', 'bench'):
        print('==', pop)
        for (pp, k), v in sorted(C.items(), key=lambda kv: kv[0][1]):
            if pp == pop:
                print('  %-75s %6d' % (k, v))
        for b in ('p<0.1', 'p<0.5', 'p>=0.5'):
            print('  %-75s %6d' % ('RELAX added edges, prior mass ' + b, relax_mass[pop, b]))
    if nlist:
        for k, v in sorted(ex.items()):
            print('--', k, len(v))
            for p in v[:nlist]:
                print('    ', p[:110])


main()
