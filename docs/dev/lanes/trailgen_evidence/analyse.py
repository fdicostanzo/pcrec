"""analyse.py CENSUS.tsv : the census table (one row per sampled pattern) + group totals.
Recursive = the artifact has a spliced or linked call. Trail share = 1 - i_notrail/i_stock (upper bound).
B share of the trail = 1 - Bcnt_trail/cnt_trail. R and B+R gains in instructions."""
import sys
rows = []
for l in open(sys.argv[1]):
    d = dict(kv.split('=', 1) for kv in l.rstrip('\n').split('\t'))
    rows.append(d)
def f(d, k):
    try: return float(d[k])
    except (KeyError, ValueError): return None
print('| pattern | rec | SET sites | dead (B) | matches | err | trail/byte | push/byte | trail share (instr, bound) | B removes of trail | R | B | B+R | ident |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
G = {}
for d in rows:
    if d.get('status') != 'ok':
        print('| %s | | | | | | | | | | | | | %s |' % (d['name'], d.get('status')))
        G.setdefault('skipped', []).append(d); continue
    n = f(d, 'n') or 1
    rec = (int(d.get('spliced', 0)) + int(d.get('linked', 0))) > 0
    it, ir, inn, ib, ibr = (f(d, 'i_' + k) for k in ('stock', 'R', 'notrail', 'B', 'BR'))
    tr, ps, btr = f(d, 'cnt_trail'), f(d, 'cnt_push'), f(d, 'Bcnt_trail')
    share = (1 - inn / it) if it and inn is not None else None
    brm = (1 - btr / tr) if tr and btr is not None else None
    pct = lambda a: '%+.1f%%' % (100 * (a / it - 1)) if a is not None and it else '-'
    print('| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
        d['name'], 'yes' if rec else 'no', d.get('set_sites'), d.get('dead_sites'), d.get('matches'), d.get('err'),
        '%.3f' % (tr / n) if tr is not None else '-', '%.3f' % (ps / n) if ps is not None else '-',
        '%.0f%%' % (100 * share) if share is not None else '-', '%.0f%%' % (100 * brm) if brm is not None else ('-' if tr else 'no trail'),
        pct(ir), pct(ib), pct(ibr), d.get('ident')))
    g = 'rec' if rec else 'flat'
    G.setdefault(g, []).append((d, it, ir, inn, ib, ibr, tr, ps, btr, n))
print()
for g in ('flat', 'rec'):
    L = G.get(g, [])
    if not L: continue
    S = lambda i: sum(x[i] for x in L if all(x[j] is not None for j in (1, i)))
    it = sum(x[1] for x in L if x[1]);
    def tot(i):
        return sum(x[i] for x in L if x[i] is not None and x[1] is not None)
    def base(i):
        return sum(x[1] for x in L if x[i] is not None and x[1] is not None)
    wtr = [x for x in L if x[6]]
    print('%s: %d artifacts, %d write the trail on their subject; instructions summed: stock %.1f M, notrail %.1f M (share %.1f%%), B %.1f M (%+.1f%%), R %.1f M (%+.1f%%), B+R %.1f M (%+.1f%%); trail entries %d -> %d under B (%.1f%% removed)' % (
        g, len(L), len(wtr), it / 1e6, tot(3) / 1e6, 100 * (1 - tot(3) / base(3)), tot(4) / 1e6, 100 * (tot(4) / base(4) - 1),
        tot(2) / 1e6, 100 * (tot(2) / base(2) - 1), tot(5) / 1e6, 100 * (tot(5) / base(5) - 1),
        sum(x[6] for x in wtr), sum((x[8] or 0) for x in wtr), 100 * (1 - sum((x[8] or 0) for x in wtr) / max(1, sum(x[6] for x in wtr)))))
    # median per-artifact R gain among artifacts that do work
    gains = sorted(100 * (x[2] / x[1] - 1) for x in L if x[1] and x[2] and x[1] > 1e6)
    if gains:
        print('  R per-artifact (>1M instr/pass, %d): min %+.1f%% median %+.1f%% max %+.1f%%' % (len(gains), gains[0], gains[len(gains) // 2], gains[-1]))
    bg = sorted(100 * (x[4] / x[1] - 1) for x in L if x[1] and x[4] and x[1] > 1e6)
    if bg:
        print('  B per-artifact (>1M instr/pass, %d): min %+.1f%% median %+.1f%% max %+.1f%%' % (len(bg), bg[0], bg[len(bg) // 2], bg[-1]))
print('skipped: %d' % len(G.get('skipped', [])))
