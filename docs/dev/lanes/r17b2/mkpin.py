import sys
src, dst = sys.argv[1], sys.argv[2]
rows = []
for l in open(src):
    h, prov = l.split()
    rows.append((h, ','.join(sorted({p.split(':')[0] for p in prov.split(',')}))))
hdr = '''# tests/memfn/pins/setfind_t3_sets.txt -- the set FIND population T3 reads
# (setfind.md §12.1; tests/memfn/setfind_t3.c): every distinct set a table
# WALK reads in a --memfn=no-pf-terms-mask artifact (byte-identical to abi 76,
# the r17b census) of every distinct corpus pattern and every pcrec-bench
# bench/*/patterns/*.rx, under the arms byte, --engine=vm, -e utf8, -e utf8
# --engine=vm, -fno-start-set, -fno-offset-skip, -fno-req-handoff,
# -fno-req-run, --tune=min-size, --tune=max-speed, -fcomments. Lane r17b2,
# 2026-10-12, written by docs/dev/lanes/r17b2/collect.py. A FIXED population:
# a corpus change does not move it; re-collecting it is a deliberate re-pin.
# One set per line: set[0..31] as hex (bit x of set[x >> 3] at x & 7), then
# where it was seen. %d sets.
''' % len(rows)
with open(dst, 'w') as f:
    f.write(hdr)
    for h, k in rows:
        f.write('%s %s\n' % (h, k))
print(len(rows), sum(1 for _, k in rows if k == 'bench'))
