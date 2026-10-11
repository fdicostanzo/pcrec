#!/usr/bin/env python3
"""rollup.py cells.tsv causes_dfa.tsv — per-cause TOTAL ns lost (vs the best
non-SIMD comparator: jit or a scalar engine; rust-only cells vs rust and
listed apart), ranked. Prints the per-cell table rows too (TSV)."""
import csv, sys, collections
cells = list(csv.DictReader(open(sys.argv[1]), delimiter='\t'))
rules = []
for ln in open(sys.argv[2]):
    if ln.startswith('#') or not ln.strip(): continue
    s, p, rg, c = ln.rstrip('\n').split('\t'); rules.append((s, p, rg, c))
def cause(r):
    for s, p, rg, c in rules:
        if s == r['set'] and p == r['pattern'] and (rg == '*' or r['regime'].startswith(rg)): return c
    return None
tot = collections.OrderedDict(); out = []
for r in cells:
    if r['set'] in ('utf8', 'litrun'): continue
    c = cause(r)
    if c is None: sys.exit('UNASSIGNED %s %s %s' % (r['set'], r['pattern'], r['regime']))
    lost = float(r['lost_ns']); alg = r['best_nonsimd'].split(':')[0] in ('re2', 'oniguruma', 'tre') or r['best_nonsimd'] in ('libpcre2:interp-caps', 'libpcre2:dfa-nocaps')
    t = tot.setdefault(c, [0.0, 0, 0.0, set()]); t[0] += lost; t[1] += 1; t[3].add(r['pattern'])
    if alg: t[2] += lost
    out.append((c, r['set'], r['pattern'], r['regime'], r['tier'], r['best_nonsimd'], r['ratio_best'], round(lost)))
print('cause\tcells\tpatterns\tlost_ns_total\tof_which_vs_scalar')
for c, (l, n, a, ps) in sorted(tot.items(), key=lambda kv: -kv[1][0]):
    print('%s\t%d\t%d\t%.0f\t%.0f' % (c, n, len(ps), l, a))
print()
for o in sorted(out, key=lambda o: (o[0], -o[7])): print('\t'.join(str(x) for x in o))
