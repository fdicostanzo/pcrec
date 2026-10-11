#!/usr/bin/env python3
"""lane lrvm: the VM-route trailing cells' bench numbers, one TSV row per
(set, pattern, regime) with every comparator's set-grain median and the
ns lost vs pcre2-jit and vs the best non-vectorscan peer that beats auto.
    python3 cells_vm.py GAP_ROWS.json vmcells.txt > cells.tsv
GAP_ROWS.json is gapreport's gap.py output for the 10-11 instance
(gaprep3's scratch, worktrees/gaprep3/build/gapscratch/gap_rows.json)."""
import json, sys
g = json.load(open(sys.argv[1]))
want = set(l.strip() for l in open(sys.argv[2]) if l.strip())
short = {'libpcre2:jit-caps': 'jit', 'libpcre2:interp-caps': 'interp',
         're2:default-caps': 're2', 're2:longest-caps': 're2L',
         'rust:default-caps': 'rust', 'oniguruma:default-caps': 'onig',
         'libpcre2:dfa-nocaps': 'p2dfa', 'tre:default-caps': 'tre'}
cols = ['jit', 'interp', 're2', 'rust', 'onig', 'p2dfa']
print('\t'.join(['set_pattern', 'regime', 'auto_caps_ns', 'auto_nocaps_ns'] +
                [c + '_ns' for c in cols] + ['lost_vs_jit_ns', 'best_peer', 'lost_vs_best_ns', 'interp_slower']))
for r in g:
    k = r['sb'] + '/' + r['pattern']
    if k not in want or r['form'] != 'plain' or not r['auto_caps']:
        continue
    ns = {short.get(c, c): v.get('ns') for c, v in r['cmp'].items()}
    behind = [(v['ns'], c) for c, v in r['cmp'].items()
              if v.get('verdict') == 'behind' and v.get('ns') and not c.startswith('vectorscan')]
    if not behind:
        continue
    j = r['cmp'].get('libpcre2:jit-caps', {})
    lj = r['auto_caps'] - j['ns'] if j.get('verdict') == 'behind' else 0
    bns, bc = min(behind)
    it = r['cmp'].get('libpcre2:interp-caps', {})
    print('\t'.join([k, r['regime'], '%.0f' % r['auto_caps'], '%.0f' % (r['auto_nocaps'] or 0)] +
                    ['%.0f' % ns[c] if ns.get(c) else '-' for c in cols] +
                    ['%.0f' % lj, short.get(bc, bc), '%.0f' % (r['auto_caps'] - bns),
                     'yes' if it.get('ns') and it['ns'] > r['auto_caps'] else 'no']))
