#!/usr/bin/env python3
"""bytecounts.py SUBJ_DIR CELLS_TSV -- for each literal, how often each of its
distinct bytes occurs in the seven subjects (summed and per subject), so a
pick can be judged against the subjects' actual rarest byte (an ORACLE bound,
not a rule: the oracle reads the subjects)."""
import sys, collections
subj_dir, cells = sys.argv[1], sys.argv[2]
S = ['t-64k', 't-256k', 't-1m', 't-64k-lat', 't-64k-cyr', 't-64k-cjk', 't-64k-asc']
data = {s: open('%s/%s.bin' % (subj_dir, s), 'rb').read() for s in S}
print('cell\tbyte\toffsets\ttotal\t' + '\t'.join(S))
for ln in open(cells, encoding='utf-8').read().splitlines()[1:]:
    cid, pat = ln.split('\t')
    if pat.startswith('^'): pat = pat.strip('^$')
    lit = pat.encode('utf-8')
    offs = collections.defaultdict(list)
    for i, b in enumerate(lit): offs[b].append(i)
    rows = []
    for b, o in offs.items():
        cnt = [data[s].count(bytes([b])) for s in S]
        rows.append((sum(cnt), b, o, cnt))
    for tot, b, o, cnt in sorted(rows):
        print('%s\t%02x\t%s\t%d\t%s' % (cid, b, ','.join(map(str, o)), tot, '\t'.join(map(str, cnt))))
