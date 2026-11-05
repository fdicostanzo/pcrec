#!/usr/bin/env python3
"""foldsweep.py WORKTREE FOLD_CLASSES.tsv OUT.tsv
For every simple-fold class of CaseFolding.txt, compile (?i)abcd<X>efgh under
-e utf8 (X = the class's first member that is not pure ASCII upper-case, else
the target) and read req_whole_run's position count and mask text."""
import sys, subprocess, csv, os
W, IN, OUT = sys.argv[1:4]
P = os.path.join(W, 'build', 'pcrec')
rows = list(csv.DictReader(open(IN), delimiter='\t'))
with open(OUT, 'w') as fo:
    fo.write('shape\tmembers\tutf8\tpos_hulls\twhole_positions\twhole_run\n')
    for r in rows:
        x = int(r['members'].split()[0][2:], 16)
        # choose the lowest member that is not a lone ASCII upper-case twin
        ch = chr(int(r['target'][2:], 16))
        pat = '(?i)abcd' + ch + 'efgh'
        p = subprocess.run([P, '-e', 'utf8', '--emit-facts', '--pattern', pat],
                           capture_output=True)
        wr = ''
        for ln in p.stdout.decode('utf-8', 'replace').splitlines():
            t = ln.split('\t')
            if len(t) >= 7 and t[1] == 'req_whole_run':
                wr = t[6]
        n = 0 if wr in ('', 'none') else len(wr.split('/')[0]) // 2
        fo.write('\t'.join([r['shape'], r['members'], r['utf8'], r['position_hull_sizes'], str(n), wr]) + '\n')
