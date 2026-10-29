"""p1dsg2: reads xo_raw.txt (3 pinned runs per subject x arm) -> per-subject min cycles/instr, answer
identity, and the per-hit cost in CYCLES and instructions: H = (twin - floor*B) / hits, floor taken
from the sparsest point of the same wlen/arm. Usage: python3 -I xo_fit.py xo_raw.txt XODIR"""
import re, sys, collections
raw = collections.defaultdict(lambda: collections.defaultdict(list))
size = {}
for ln in open(sys.argv[1]):
    name, sz, binn, *rest = ln.split()
    kv = dict(x.split('=') for x in rest)
    raw[name][binn].append((int(kv['cycles']), int(kv['instr']), kv['res'], kv['hash']))
    size[name] = int(sz)
rows = []
for name in sorted(raw, key=lambda s: (int(re.match(r'w(\d+)', s).group(1)), s.split('_')[1], -float(s.split('_q')[1]))):
    sh, tw = raw[name]['me_ship'], raw[name]['me_twin']
    ident = {(r[2], r[3]) for r in sh} == {(r[2], r[3]) for r in tw} and len({(r[2], r[3]) for r in sh}) == 1
    hits = open('%s/%s.txt' % (sys.argv[2], name), 'rb').read().count(b'@')
    rows.append((name, size[name], hits, min(r[0] for r in sh), min(r[0] for r in tw), sh[0][1], tw[0][1], ident, sh[0][2]))
print('# subject bytes hits B/hit ship_cyc twin_cyc ratio_cyc ship_instr twin_instr ratio_instr ship_cyc/B identical matches')
for n, b, h, sc, tc, si, ti, ident, res in rows:
    print('%-18s %8d %7d %8.1f %10d %10d %6.3f %10d %10d %6.3f %5.2f %s %s' % (n, b, h, b / max(h, 1), sc, tc, tc / sc, si, ti, ti / si, sc / b, 'yes' if ident else 'NO', res))
print('# per-hit fit (twin side): floor = twin cycles/B at q=0.001; H = (twin - floor*B)/hits; break-even B/hit = H / (ship/B - floor)')
for w in (2, 8, 32):
    for arm in ('fail', 'ok'):
        pts = [r for r in rows if r[0].startswith('w%d_%s_' % (w, arm))]
        sparse = [r for r in pts if r[0].endswith('q0.001')][0]
        for unit, si, ti in (('cyc', 3, 4), ('instr', 5, 6)):
            fl = sparse[ti] / sparse[1] if unit == 'instr' else None
            # floor: fit through the two sparsest points (q=0.01, 0.001) to separate floor and H
            a = [r for r in pts if r[0].endswith('q0.01')][0]
            h = (a[ti] - sparse[ti]) / (a[2] - sparse[2])
            floor = (sparse[ti] - h * sparse[2]) / sparse[1]
            hs = [(r[ti] - floor * r[1]) / r[2] for r in pts if r[2]]
            c = sum(r[si] / r[1] for r in pts) / len(pts)
            print('w%-2d %-4s %-5s floor/B=%.3f H/hit: %s  ship/B=%.2f  break-even=1 hit per %.1f B' % (
                w, arm, unit, floor, ' '.join('%.0f' % x for x in hs), c, (sum(hs) / len(hs)) / (c - floor)))
