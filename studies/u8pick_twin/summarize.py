#!/usr/bin/env python3
"""summarize.py RUN.tsv -- answer identity over every arm, then median +- sd per
(cell, subject, arm), the utf8/byte ratio with the 2*(sd_a+sd_b) test, and the
bench-style pooled table (sum over the seven subjects).
Arms: S = AVX2 packed-pair find-all, P = the bench pin c4c70f2c's compiler, -e utf8; A = -e byte, B = -e utf8 (today), C = -e utf8 under the scratch u8prior
analysis, M = glibc memmem find-all (plain-literal cells only)."""
import csv, statistics as st, sys, collections
rows = list(csv.DictReader(open(sys.argv[1]), delimiter='\t'))
g = collections.defaultdict(list)
meta = collections.defaultdict(lambda: collections.defaultdict(set))
loads = collections.defaultdict(list)
for r in rows:
    g[(r['cell'], r['subj'], r['arm'])].append(float(r['ns_per_call']))
    meta[(r['cell'], r['subj'])][r['arm']].add((r['matches'], r['hash']))
    loads[r['cell']].append(float(r['load1']))
diffs = 0
for ck, m in meta.items():
    allv = set()
    for a, v in m.items():
        if len(v) != 1: diffs += 1; print('UNSTABLE', ck, a)
        allv |= v
    if len(allv) != 1: diffs += 1; print('ANSWER DIFF', ck, dict(m))
print('answer-identity diffs over all cells x subjects x arms:', diffs)
ARMS = 'ABCMPS'
def ms(k):
    v = g[k]; return st.median(v), (st.stdev(v) if len(v) > 1 else 0.0)
def gap(x, y):  # |x-y| beyond 2*(sd_x+sd_y)?
    return abs(x[0] - y[0]) > 2 * (x[1] + x[1] * 0 + y[1])
cells = list(dict.fromkeys(k[0] for k in g)); subs = list(dict.fromkeys(k[1] for k in g))
npass = len(next(iter(g.values())))
def f(v): return '-' if v is None else '%.0f+-%.0f' % v
print('\n## per cell x subject (ns/call, median +- sd, %d passes); ratios are median/median' % npass)
print('cell\tsubj\tmatches\tA_byte\tB_utf8\tC_utf8+prior\tM_memmem\tP_pin\tS_avx2pair\tB/A\tB-vs-A gap>2(sd+sd)\tC/A\tC-vs-A gap>2(sd+sd)')
tot = collections.defaultdict(lambda: collections.defaultdict(float))
tsd = collections.defaultdict(lambda: collections.defaultdict(float))
for c in cells:
    for s in subs:
        if (c, s, 'A') not in g: continue
        v = {a: (ms((c, s, a)) if (c, s, a) in g else None) for a in ARMS}
        n = list(meta[(c, s)]['A'])[0][0]
        def rr(x): return '-' if v[x] is None else '%.2f' % (v[x][0] / v['A'][0])
        def gg(x): return '-' if v[x] is None else ('yes' if gap(v['A'], v[x]) else 'no')
        print('\t'.join([c, s, n, f(v['A']), f(v['B']), f(v['C']), f(v['M']), f(v['P']), f(v['S']), rr('B'), gg('B'), rr('C'), gg('C')]))
        for a in ARMS:
            if v[a]: tot[c][a] += v[a][0]; tsd[c][a] += v[a][1] ** 2
print('\n## pooled over the 7 subjects (us; sum of medians, sd = sqrt(sum sd^2))')
print('cell\tA_byte\tB_utf8\tC_utf8+prior\tM_memmem\tP_pin\tS_avx2pair\tB/A\tB-vs-A gap>2(sd+sd)\tC/A\tC-vs-A gap>2(sd+sd)\tmedian load1')
for c in cells:
    p = {a: ((tot[c][a], tsd[c][a] ** .5) if a in tot[c] else None) for a in ARMS}
    def fm(x): return '-' if x is None else '%.1f+-%.1f' % (x[0] / 1e3, x[1] / 1e3)
    def r(x): return '-' if p[x] is None else '%.2f' % (p[x][0] / p['A'][0])
    def g2(x): return '-' if p[x] is None else ('yes' if gap(p['A'], p[x]) else 'no')
    print('\t'.join([c, fm(p['A']), fm(p['B']), fm(p['C']), fm(p['M']), fm(p['P']), fm(p['S']), r('B'), g2('B'), r('C'), g2('C'), '%.2f' % st.median(loads[c])]))
