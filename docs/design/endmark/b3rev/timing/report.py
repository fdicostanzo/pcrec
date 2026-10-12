#!/usr/bin/env python3
"""b3rev timing report: reads results/echeck.json, acheck.json, etime*.tsv,
atime*.tsv and prints the tables in results/report.txt.

    python3 -I docs/design/endmark/b3rev/timing/report.py > docs/design/endmark/b3rev/timing/results/report.txt
"""
import collections, glob, json, math, os, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, 'results')
REGS = ['%s-%s-%s' % (a, b, c) for a in ('L', 'K4', 'M1') for b in ('nl', 'nonl') for c in ('m', 'n')]


def gm(xs):
    xs = [x for x in xs if x > 0]
    return math.exp(sum(math.log(x) for x in xs) / len(xs)) if xs else float('nan')


def pct(xs, p):
    xs = sorted(xs)
    if not xs:
        return float('nan')
    i = (len(xs) - 1) * p / 100
    lo, hi = int(math.floor(i)), int(math.ceil(i))
    return xs[lo] + (xs[hi] - xs[lo]) * (i - lo)


def load_time(pat):
    """{(k, regime): {arm: median}} over every file matching pat (later files
    overwrite nothing: a cell seen twice keeps the first)."""
    t = collections.defaultdict(dict)
    for fn in sorted(glob.glob(os.path.join(RES, pat))):
        for ln in open(fn):
            f = ln.rstrip('\n').split('\t')
            if len(f) < 7:
                continue
            k, reg, arm, med = int(f[0]), f[1], f[4], float(f[5])
            t[(k, reg)].setdefault(arm, med)
    return t


MEAS = {r['k']: r for r in json.load(open(os.path.join(HERE, '..', '..', 'b3meas', 'results', 'check.json')))}


def cls_of(r):
    if not r.get('tie'):
        return 'no-tie'
    p = MEAS[r['k']]['prio']
    return 'tie/%s/%s' % ('const' if p.startswith('const') else 'state-dep',
                           'unbounded' if MEAS[r['k']]['twin']['cyclic'] else 'bounded')


def ratio_rows(rows, t, num, den, regs, label):
    out = []
    for g in regs:
        xs = [t[(r['k'], g)][num] / t[(r['k'], g)][den] for r in rows
              if (r['k'], g) in t and num in t[(r['k'], g)] and den in t[(r['k'], g)] and t[(r['k'], g)][den] > 0]
        aa = [t[(r['k'], g)]['A'] / t[(r['k'], g)]['T'] for r in rows
              if (r['k'], g) in t and 'A' in t[(r['k'], g)] and 'T' in t[(r['k'], g)]]
        if xs:
            out.append('%s\t%s\t%d\t%.3f\t%.3f-%.3f\t%.3f\t%.3f-%.3f' % (label, g, len(xs), gm(xs), pct(xs, 5), pct(xs, 95),
                                                                     gm(aa), pct(aa, 5), pct(aa, 95)))
    return out


def fit(pts):
    """least squares ns = a + b*loads."""
    n = len(pts)
    if n < 3:
        return None
    mx = sum(x for x, _ in pts) / n
    my = sum(y for _, y in pts) / n
    sxx = sum((x - mx) ** 2 for x, _ in pts)
    if sxx == 0:
        return None
    b = sum((x - mx) * (y - my) for x, y in pts) / sxx
    return my - b * mx, b


E1 = '''== E1 form elements: today's emitted rev-end walk (T) against b3meas's plain-style R (same algorithm)
element                         T (today, emit_rev_end + emit_reverse_block)            R (plain)
seed loop                       for seed<2; seed 1 re-reads s[n-1]; same seed state       same loop; seed states PRE-VIEWED (seed n = END/EOL view
                                for both seeds, views resolved in the walk                of s0, seed n-1 = EOL view); one eol probe after seed n's 1st step
view resolution                 PER ITERATION at the loop top: __builtin_expect(          none in the loop
                                rewind+1 >= n) + view-state copy; at n-1 re-reads s[n-1]
table layout                    premultiplied u16 next, u8 accept per cell, 256 B class,  identical (R uses the probe's pre-scan-edge machine;
                                u16 view row table, inline accessors (fold away)          T the scan-edge pass's renumbered one)
stop/dead dispatch              st < stop: continue; then st == 65535: break               identical
run skip, accepting self-loop   scan-edge block behind the stop compare (range compare     bitmap table behind the stop compare, then `continue`
                                or u8 bitmap), sets the start, `goto` the loop top          (accept recorded at the top)
run skip, other self-loop       STAY loop at the loop TOP, tested every iteration           same after-compare form as above
                                (`reverse_state == K && rewind+1 < n`), u8 bitmap
run-skip coverage               the scan-edge pass's choice                                every self-loop state of the machine
tie arm                         verify-at via <p>_match (or relocate)                      verify-at via <p>_match
dead-seed skip                  not emitted on this population (no dead seed)              n/a
'''


def main():
    print(E1)
    cen = os.path.join(RES, 'e1_census.json')
    if os.path.exists(cen):
        c = collections.Counter()
        for x in json.load(open(cen)):
            c[(x['cls'], 'artifacts')] += 1
            c[(x['cls'], 'view probe in loop')] += x['view_probe']
            c[(x['cls'], 'end view too')] += x['end_view']
            c[(x['cls'], 'stay at top')] += x['stay_top']
            c[(x['cls'], 'scan-edge ' + x['scan_edge_stamp'])] += 1
            c[(x['cls'], 'T run skip (stay or edge)')] += x['stay_top'] or x['edge']
            c[(x['cls'], 'R run skip')] += x['r_runs'] > 0
        print('# E1 census (gen.py e1): ' + '; '.join('%s %s=%d' % (k[0], k[1], v) for k, v in sorted(c.items())))
        print()
    run = os.environ.get('RUN', 'run2')
    E = json.load(open(os.path.join(RES, 'echeck.json' if run == 'run2' else run + '_echeck.json')))
    t = load_time(run + '_etime*.tsv')
    other = load_time(('run1' if run == 'run2' else 'run2') + '_etime*.tsv')
    print('# timing run: %s (cross-run agreement against the other run at the end of section E)' % run)
    ok = [r for r in E if 'skip' not in r]
    skips = collections.Counter(r['skip'].split(':')[0][:40] for r in E if 'skip' in r)
    print('# E population: %d distinct artifacts; built and checked %d; skipped %s' % (len(E), len(ok), dict(skips)))
    tot = collections.Counter()
    wrong = collections.Counter()
    for r in ok:
        for arm, w in r['wrong'].items():
            cells = r['exh'][arm]['cells'] + sum(v[arm]['n'] for v in r['regs'].values())
            tot[arm] += cells
            wrong[arm] += w
    print('# E answers vs libpcre2 10.46 (exhaustive every-startpos cells to length 5 + regime subjects), per arm: %s'
          % ', '.join('%s %d/%d wrong' % (a, wrong[a], tot[a]) for a in sorted(tot)))
    bad = [(r['k'], r['pat'], {a: w for a, w in r['wrong'].items() if w}) for r in ok if any(r['wrong'].values())]
    for b in bad:
        print('#   WRONG (arm not timed) k=%d %r %s' % b)
    by = collections.defaultdict(list)
    for r in ok:
        by[r['cls']].append(r)
    print('# classes: %s' % {c: len(v) for c, v in by.items()})
    print('# no-tie artifacts with stay loops at the top (S arm differs from R): %d of %d'
          % (sum(1 for r in by['notie'] if r.get('s_tops')), len(by['notie'])))
    print('# tie artifacts whose tagged machine has a non-accepting self-loop (Q arm differs from B): %d of %d'
          % (sum(1 for r in by['tie'] if r.get('q_tops')), len(by['tie'])))
    print()
    nt = by['notie']
    print('== E2/E3 no-tie (nl_last false): class geomean of ns ratios per regime, per-cell p5-p95; A/A = A/T')
    print('ratio\tregime\tcells\tgeomean\tp5-p95\tA/A\tA/A p5-p95')
    for num, den in (('T', 'R'), ('V', 'R'), ('S', 'R'), ('T', 'V'), ('U', 'T'), ('P', 'R'), ('W', 'R'), ('U', 'P'),
                     ('U', 'W'), ('W', 'P'), ('T', 'W')):
        for ln in ratio_rows(nt, t, num, den, REGS, '%s/%s' % (num, den)):
            print(ln)
        print()
    # per-call / per-byte fit
    print('== E2 fit ns = a + b*loads per artifact over its 12 regimes (no-tie); median a (ns/call), b (ns/load) over artifacts')
    print('arm\tartifacts\tmedian a\tmedian b\tmedian R^2')
    for arm in ('T', 'A', 'R', 'V', 'S', 'U', 'P', 'W'):
        fa, fb, r2s = [], [], []
        for r in nt:
            pts = [(r['regs'][g][arm if arm != 'A' else 'T']['loads'], t[(r['k'], g)][arm]) for g in REGS
                   if g in r['regs'] and (r['k'], g) in t and arm in t[(r['k'], g)]]
            f = fit(pts)
            if f:
                fa.append(f[0])
                fb.append(f[1])
                my = sum(y for _, y in pts) / len(pts)
                ss = sum((y - my) ** 2 for _, y in pts)
                res = sum((y - f[0] - f[1] * x) ** 2 for x, y in pts)
                r2s.append(1 - res / ss if ss else 1)
        if fa:
            print('%s\t%d\t%.2f\t%.4f\t%.3f' % (arm, len(fa), statistics.median(fa), statistics.median(fb), statistics.median(r2s)))
    print()
    print('== E2 per-artifact fit deltas (T - R and T - V): median and p5-p95 of a and b deltas')
    for x, y in (('T', 'R'), ('T', 'V'), ('V', 'R'), ('S', 'R'), ('U', 'P'), ('U', 'W'), ('W', 'R')):
        da, db = [], []
        for r in nt:
            ps = {}
            for arm in (x, y):
                pts = [(r['regs'][g][arm]['loads'], t[(r['k'], g)][arm]) for g in REGS
                       if g in r['regs'] and (r['k'], g) in t and arm in t[(r['k'], g)]]
                ps[arm] = fit(pts)
            if ps[x] and ps[y]:
                da.append(ps[x][0] - ps[y][0])
                db.append(ps[x][1] / ps[y][1] if ps[y][1] else float('nan'))
        if da:
            print('%s-%s\tn=%d\tda median %.2f ns (p5 %.2f, p95 %.2f)\tb ratio median %.3f (p5 %.3f, p95 %.3f)'
                  % (x, y, len(da), statistics.median(da), pct(da, 5), pct(da, 95), statistics.median(db), pct(db, 5), pct(db, 95)))
    print()
    print('== E loads per call, no-tie, class mean (instrumented subject reads)')
    print('regime\t' + '\t'.join(('T', 'R', 'V', 'S', 'U', 'P', 'W')))
    for g in REGS:
        vals = []
        for arm in ('T', 'R', 'V', 'S', 'U', 'P', 'W'):
            xs = [r['regs'][g][arm]['loads'] for r in nt if g in r['regs'] and arm in r['regs'][g]]
            vals.append('%.2f' % (sum(xs) / len(xs)) if xs else '-')
        print(g + '\t' + '\t'.join(vals))
    print()
    print('== cross-run agreement (no-tie): class geomean per regime, this run | other run')
    for num, den in (('T', 'R'), ('V', 'R'), ('U', 'T'), ('P', 'R'), ('U', 'P'), ('A', 'T')):
        cells = []
        for g in REGS:
            a = [t[(r['k'], g)][num] / t[(r['k'], g)][den] for r in nt
                 if num in t.get((r['k'], g), {}) and den in t.get((r['k'], g), {})]
            b = [other[(r['k'], g)][num] / other[(r['k'], g)][den] for r in nt
                 if num in other.get((r['k'], g), {}) and den in other.get((r['k'], g), {})]
            if a and b:
                cells.append('%s %.2f|%.2f' % (g, gm(a), gm(b)))
        print('%s/%s\t%s' % (num, den, '  '.join(cells)))
    print()
    tie = by['tie']
    print('== E4 tie artifacts: Q (tagged, today step shape) vs B (tagged, plain); T/R style on the two-seed walk')
    for num, den in (('T', 'R'), ('R', 'B'), ('T', 'B'), ('Q', 'B')):
        for c in sorted(set(cls_of(r) for r in tie)):
            rows = [r for r in tie if cls_of(r) == c]
            for ln in ratio_rows(rows, t, num, den, [g for g in REGS if '-nl-m' in g or '-nonl-m' in g], '%s/%s %s' % (num, den, c)):
                print(ln)
        print()
    # ---------------------------------------------------------------- A
    if not os.path.exists(os.path.join(RES, 'acheck.json')):
        return
    A = json.load(open(os.path.join(RES, 'acheck.json')))
    at = load_time(run + '_atime*.tsv')
    aok = [r for r in A if 'skip' not in r]
    print('# A population: %d tie artifacts; built %d; skipped %s' % (
        len(A), len(aok), dict(collections.Counter(r['skip'][:60] for r in A if 'skip' in r))))
    ncells = sum(v['n'] for r in aok for v in r['check'].values())
    print('# A answer check (nl-m subjects; starts == libpcre2 and today; today end == libpcre2 end in {n, n-1}; '
          'lowered end == n): %d subjects x 6 arms, %d wrong; subjects where libpcre2 ends at n-1: %d'
          % (ncells, sum(r['wrong'] for r in aok), sum(v['end_n1'] for r in aok for v in r['check'].values())))
    for r in aok:
        if r['wrong']:
            print('#   WRONG k=%d %r %s' % (r['k'], r['pat'], r['check']))
    print()
    print('== A1 verify-at (_match from s*) and A2 relocate (-fno-rev-end _search from s*): today/lowered, with A/A')
    print('finisher\tclass\tregime\tcells\ttoday/lowered gm\tp5-p95\tA/A gm\tA/A p5-p95')
    acls = lambda r: 'tie/%s/%s' % ('const' if r['prio'].startswith('const') else 'state-dep',
                                    'unbounded' if r['cyclic'] else 'bounded')
    for fin, (x, y, aa) in (('A1', ('T', 'L', 'A')), ('A2', ('N', 'K', 'M'))):
        for c in sorted(set(acls(r) for r in aok)):
            for g in ('L-nl-m', 'K4-nl-m', 'M1-nl-m'):
                xs, fl = [], []
                for r in aok:
                    if acls(r) != c or (r['k'], g) not in at:
                        continue
                    v = at[(r['k'], g)]
                    if x in v and y in v and aa in v:
                        xs.append(v[x] / v[y])
                        fl.append(v[aa] / v[x])
                if xs:
                    print('%s\t%s\t%s\t%d\t%.3f\t%.3f-%.3f\t%.3f\t%.3f-%.3f' % (fin, c, g, len(xs), gm(xs), pct(xs, 5),
                                                                          pct(xs, 95), gm(fl), pct(fl, 5), pct(fl, 95)))
    print()
    print('== A per-artifact: today/lowered ns (L-nl-m | M1-nl-m) and machine states (forward via -fno-rev-end, anchored)')
    print('k\tpattern\tA1 L\tA1 M1\tA2 L\tA2 M1\tfwd today->lowered\tanch today->lowered\trev today->lowered')
    for r in aok:
        def rr(x, y, g):
            v = at.get((r['k'], g), {})
            return '%.2f' % (v[x] / v[y]) if x in v and y in v else '-'
        s = r['states']
        print('%d\t%s\t%s\t%s\t%s\t%s\t%s->%s\t%s->%s\t%s->%s' % (
            r['k'], r['pat'], rr('T', 'L', 'L-nl-m'), rr('T', 'L', 'M1-nl-m'), rr('N', 'K', 'L-nl-m'), rr('N', 'K', 'M1-nl-m'),
            s['N']['forward'], s['K']['forward'], s['T']['anchored'], s['L']['anchored'], s['T']['reverse'], s['L']['reverse']))


if __name__ == '__main__':
    main()
