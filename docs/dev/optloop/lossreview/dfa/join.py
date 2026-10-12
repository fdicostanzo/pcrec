#!/usr/bin/env python3
"""Join population.tsv (bench ns + stamps), the walk instrument's per-phase
loads (ws_dfa.tsv) and the counted find-all (facount.tsv) per DFA cell.
Usage: join.py population.tsv WS.tsv FACOUNT.tsv > cells.tsv"""
import csv, sys, collections
pop = list(csv.DictReader(open(sys.argv[1]), delimiter='\t'))
ws = collections.defaultdict(collections.Counter)
for r in csv.DictReader(open(sys.argv[2]), delimiter='\t'):
    if r['regime'] != 'throughput': continue
    a = ws[r['pid']]
    for c in ['n', 'T', 'T_scan', 'T_fwd', 'T_skip', 'T_pre', 'T_rev', 'T_endw', 'm_gap']:
        a[c] += int(r.get(c) or 0)
fc = collections.defaultdict(collections.Counter)
for ln in open(sys.argv[3]):
    f = ln.rstrip('\n').split('\t')
    a = fc[f[0] + '/' + f[1]]
    for i, c in enumerate(['bytes', 'calls', 'matches', 'mc', 'mcb', 'mrc', 'mcmp'], 3):
        a[c] += int(f[i])
cols = ['set', 'pattern', 'regime', 'tier', 'group', 'auto_ns', 'best_nonsimd', 'best_ns', 'ratio_best',
        'lost_ns', 'jit_ratio', 'rust_ratio', 'RX_DFA_SCAN', 'RX_DFA_PREFILTER', 'RX_DFA_START', 'RX_REQ_WHY']
print('\t'.join(cols + ['ns_B', 'loads_B', 'fwd_B', 'skip_B', 'pre_B', 'rev_B', 'calls', 'matches', 'memchr_calls',
                        'memchr_B', 'ns_per_call', 'lost_per_call', 'ns_per_memchr']))
for r in pop:
    if r['RX_ENGINE'] != 'dfa': continue
    pid = r['set'] + '/' + r['pattern']
    w, c = ws.get(pid), fc.get(pid)
    auto = float(r['auto_ns']); lost = float(r['lost_ns'])
    ex = []
    if r['regime'] == 'large-subject-throughput' and w and c:
        n = w['n']
        ex = ['%.3f' % (auto / n), '%.3f' % (w['T'] / n), '%.3f' % (w['T_fwd'] / n), '%.3f' % (w['T_skip'] / n),
              '%.3f' % (w['T_pre'] / n), '%.3f' % (w['T_rev'] / n), c['calls'], c['matches'], c['mc'],
              '%.3f' % (c['mcb'] / n), '%.1f' % (auto / c['calls']), '%.1f' % (lost / c['calls']),
              '%.2f' % (auto / c['mc']) if c['mc'] else '-']
    print('\t'.join([str(r[k]) for k in cols] + [str(x) for x in ex]))
