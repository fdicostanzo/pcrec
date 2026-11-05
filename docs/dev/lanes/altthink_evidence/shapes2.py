import sys, collections
groups = collections.defaultdict(set)
for line in open(sys.argv[1], encoding='utf-8'):
    line = line.split('#')[0].strip()
    if not line: continue
    f = [x.strip() for x in line.split(';')]
    if f[1] not in ('C', 'S'): continue
    s = int(f[0], 16); d = int(f[2], 16)
    groups[d] |= {s, d}
def contiguous(cps):
    cps = sorted(cps); return cps[-1] - cps[0] == len(cps) - 1
def cube(bs):
    bs = list(bs); k = 0xFF
    for b in bs[1:]: k &= ~(b ^ bs[0])
    return (1 << (8 - bin(k & 0xFF).count('1'))) == len(bs)
c = collections.Counter()
for t, mem in groups.items():
    encs = [chr(x).encode() for x in mem]
    lens = {len(e) for e in encs}
    if lens == {1}: c['ascii'] += 1; continue
    if len(lens) > 1: c['mixed'] += 1; continue
    n = lens.pop()
    pos = [{e[i] for e in encs} for i in range(n)]
    prod = 1
    for p in pos: prod *= len(p)
    exact = prod == len(encs)
    today_one_branch = contiguous(mem)  # u8_box single box only if contiguous (and same lead structure); approx
    allcube = all(cube(p) for p in pos)
    key = ('exact' if exact else 'superset') + '/' + ('allcube<=2' if allcube and all(len(p) <= 2 for p in pos) else ('allcube' if allcube else 'noncube')) + '/' + ('contig' if today_one_branch else 'noncontig')
    c[key] += 1
for k in sorted(c): print(c[k], k)
