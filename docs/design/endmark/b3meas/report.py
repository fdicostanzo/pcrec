#!/usr/bin/env python3
"""b3meas report: reads gen.py's check.json (+ time.tsv when present) and prints
the class split, the per-regime loads and the ns/call ratios.  Classes:

  tie      today emits tie code (`revend_tie`), split by mark_prio (const /
           state-dependent / unobserved) and by X bounded (the tagged reverse
           machine is acyclic) / unbounded (it has a cycle);
  no-tie   the rest (the 223's distinct patterns).

    OUT=build/scratch/b3meas python3 -I docs/design/endmark/b3meas/report.py
"""
import collections, json, os, statistics, sys

OUT = os.environ['OUT']
res = []
for fn in sorted(os.listdir(OUT)):
    if fn.startswith('check') and fn.endswith('.json'):     # check.json + check_synth.json
        res += json.load(open(os.path.join(OUT, fn)))
REGS = ['%s-%s-%s' % (a, b, c) for a in ('L', 'K4', 'M1') for b in ('nl', 'nonl') for c in ('m', 'n')]


def cls(r):
    if not r.get('today_tie'):
        return 'no-tie'
    p = r['prio']
    p = 'const' if p.startswith('const') else p
    return 'tie/%s/%s' % (p, 'unbounded' if r['twin'].get('cyclic') else 'bounded')


def main():
    skips = collections.Counter(r['skip'].split(':')[0] for r in res if 'skip' in r)
    ok = [r for r in res if 'skip' not in r]
    print('# population: %d distinct artifacts (+idioms); twin built and checked on %d; skipped %s'
          % (len(res), len(ok), dict(skips)))
    for r in res:
        if 'skip' in r and r['skip'].startswith('error'):
            print('#   error k=%d %r: %s' % (r['k'], r['pat'], r['skip'][:200]))
    bad = [r for r in ok if tuple(r['wrong']) != (0, 0)]
    cells = sum(r['exh'][0] for r in ok)
    tsub = sum(v['n'] for r in ok for v in r['regs'].values())
    print('# answers vs libpcre2 10.46: %d exhaustive cells (every startpos) + %d regime subjects; '
          'artifacts with any wrong answer: today %d, twin %d'
          % (cells, tsub, sum(r['wrong'][0] > 0 for r in ok), sum(r['wrong'][1] > 0 for r in ok)))
    for r in bad:
        print('#   WRONG k=%d %r today=%d twin=%d' % (r['k'], r['pat'], r['wrong'][0], r['wrong'][1]))
    agree = collections.Counter((bool(r.get('today_tie')), r['twin_ties']) for r in ok)
    print('# tie-code agreement (today emits tie code, tagged machine has an acc=3 state): %s' % dict(agree))
    print()
    byc = collections.defaultdict(list)
    for r in ok:
        byc[cls(r)].append(r)
    print('== classes (distinct artifacts; rows = corpus+bench rows they stand for)')
    print('class\tartifacts\trows\tnocap\tpatterns (first 8)')
    for c in sorted(byc):
        rs = byc[c]
        print('%s\t%d\t%d\t%d\t%s' % (c, len(rs), sum(r['nrows'] for r in rs), sum(bool(r.get('nocap')) for r in rs),
                                      '  '.join(r['pat'] for r in rs[:8])))
    print()
    print('== loads per call (subject byte reads, mean over the regime\'s subjects; today / B3 = ratio), '
          'and tie events (both distances reach s*: today runs the forward finish)')
    print('class\tregime\tartifacts\tsubjects\ttoday\tB3\tratio\tties')
    for c in sorted(byc):
        for g in REGS:
            rr = [r['regs'][g] for r in byc[c] if g in r['regs']]
            if not rr:
                continue
            n = sum(x['n'] for x in rr)
            tl = sum(x['tl'] * x['n'] for x in rr) / n
            bl = sum(x['bl'] * x['n'] for x in rr) / n
            print('%s\t%s\t%d\t%d\t%.1f\t%.1f\t%.2f\t%d' % (c, g, len(rr), n, tl, bl, tl / bl if bl else 0,
                                                          sum(x['ties'] for x in rr)))
    print()
    print('== cost side: table bytes in the search body (static arrays) and -O2 search text, per class (sums)')
    print('class\tartifacts\ttoday_rev_bytes\tB3_bytes\tratio\ttoday_text\tB3_text\tB3_states\tB3_cls\truns')
    for c in sorted(byc):
        rs = byc[c]
        tb = sum(r['today_rev_bytes'] for r in rs)
        bb = sum(r['twin']['bytes'] for r in rs)
        tt = sum(r['T_search_text'] or 0 for r in rs)
        bt = sum(r['B_search_text'] or 0 for r in rs)
        print('%s\t%d\t%d\t%d\t%.2f\t%d\t%d\t%d\t%d\t%d' % (c, len(rs), tb, bb, bb / tb, tt, bt,
              sum(r['twin']['S'] for r in rs), sum(r['twin']['C'] for r in rs), sum(r['twin']['runs'] for r in rs)))
    tp = os.path.join(OUT, 'time.tsv')
    if os.path.exists(tp):
        tim = collections.defaultdict(dict)
        for ln in open(tp):
            f = ln.rstrip('\n').split('\t')
            if len(f) < 9 or not f[0].isdigit():
                continue
            tim[int(f[0])][f[1]] = dict(t=float(f[4]), a=float(f[5]), b=float(f[6]))
        print()
        print('== ns/call (median of rounds); today/B3 and the A/A ratio today/today-copy, '
              'per class x regime: geomean [min..max] over artifacts')
        print('class\tregime\tartifacts\ttoday_ns(med)\tB3_ns(med)\ttoday/B3 gm\t[min..max]\tAA gm\tAA [min..max]')
        for c in sorted(byc):
            for g in REGS:
                rows = [tim[r['k']][g] for r in byc[c] if r['k'] in tim and g in tim[r['k']]]
                if not rows:
                    continue
                q = [x['t'] / x['b'] for x in rows]
                aa = [x['t'] / x['a'] for x in rows]
                print('%s\t%s\t%d\t%.1f\t%.1f\t%.3f\t[%.2f..%.2f]\t%.3f\t[%.2f..%.2f]'
                      % (c, g, len(rows), statistics.median(x['t'] for x in rows), statistics.median(x['b'] for x in rows),
                         statistics.geometric_mean(q), min(q), max(q), statistics.geometric_mean(aa), min(aa), max(aa)))
        print()
        print('== ns/call per timed artifact (today / B3 / A-A)')
        for r in ok:
            if r['k'] not in tim:
                continue
            cells = '  '.join('%s %.0f/%.0f(%.2f)' % (g, tim[r['k']][g]['t'], tim[r['k']][g]['b'],
                                                      tim[r['k']][g]['t'] / tim[r['k']][g]['b'])
                              for g in REGS if g in tim[r['k']])
            print('%d\t%s\t%s\t%s' % (r['k'], cls(r), r['pat'], cells))


main()
