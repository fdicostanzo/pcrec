#!/usr/bin/env python3
"""K23's step count in CLOSED FORM, with its validation against measurement.

THE LAW (k23_design.md section 2.2). For `(C{m,M}){p,P}` with a single-byte
body C, greedy throughout, P >= p, matched against a subject of exactly the
minimum length n = p*m, the number of backtrack resumptions the emitted VM
spends is

    steps(m, M, p) = SUM over s = 0..n of Comp[m,M](s)   -   p

where Comp[m,M](s) is the number of COMPOSITIONS of s into parts drawn from
[m, M] -- i.e. the number of distinct prefixes of a decomposition the search
can be sitting on. The subtracted p is the accepting path itself, whose
nodes are reached by forward progress and so are never charged.

Why the EXACT minimum is the worst case, and not merely a bad case: at
n = p*m the only decomposition is all-minimum, and the minimum is the LEAST
preferred inner length at every level, so greedy order puts the unique
solution at the very LAST leaf. The whole tree is explored before it is
found. One byte more of subject and the solution moves inward.

Note what the law does NOT contain: P. The outer maximum cancels, because at
n = p*m no composition can have more than floor(n/m) = p parts anyway. That
is D27's black-box observation ("reducing the outer max alone does NOT avoid
it") derived rather than observed.

Usage:
  model.py --check            validate the law against the measured table
  model.py --grid             where the law crosses the 10^6 default budget
  model.py --ratios           python's TIMES vs the law's NODE COUNTS (R26 E8)
"""
import argparse
import os
import re

# MEASURED, by probes/steps.sh on this repo's build. Each row is
#   (m, M, p, n, steps)
# and every one is reproducible with
#   probes/steps.sh '(a{m,M}){p,P}' n
MEASURED = [
    (10, 20, 10, 100, 10621636),
    (10, 15, 10, 100, 1329312),
    (10, 12, 10, 100, 24150),
    (11, 22, 11, 121, 111354519),
    (7, 12, 7, 49, 8626),
    (8, 14, 8, 64, 70731),
    (5, 10, 5, 25, 346),
    (3, 6, 3, 9, 13),
    (2, 3, 2, 4, 2),
]


def comp_prefix_total(m, M, n):
    """SUM_{s=0..n} (number of compositions of s into parts in [m, M])."""
    if m <= 0:
        return None                      # a nullable part makes it infinite
    f = [0] * (n + 1)
    f[0] = 1
    for s in range(1, n + 1):
        f[s] = sum(f[s - d] for d in range(m, min(M, s) + 1))
    return sum(f)


def law(m, M, p):
    t = comp_prefix_total(m, M, p * m)
    return None if t is None else t - p


def check():
    print('%-4s %-4s %-4s %-6s %14s %14s %8s' %
          ('m', 'M', 'p', 'n', 'measured', 'law', 'diff'))
    bad = 0
    for m, M, p, n, meas in MEASURED:
        assert n == p * m, 'the law is stated at n = p*m only'
        got = law(m, M, p)
        d = got - meas
        if d != 0:
            bad += 1
        print('%-4d %-4d %-4d %-6d %14d %14d %8d' % (m, M, p, n, meas, got, d))
    print('\n%d of %d rows exact; the law is stated with the -p term already '
          'applied, so a nonzero diff is a REFUTATION, not a residual.'
          % (len(MEASURED) - bad, len(MEASURED)))
    return bad


# MEASURED python `re` wall-clock, keyed (m, M, p) at n = p*m, milliseconds.
# READ FROM out/python_growth.txt when it is present, so this is a live
# reading of the archive rather than a retyped snapshot -- R24 M-F4, and the
# specific thing R26 M3 caught this note doing with a different pair of
# numbers. The literals below are the fallback for a checkout whose archive
# has not been regenerated; a re-run moves them by well under 1%, and the
# argument is about the RATIOS, which move by less still.
PYTHON_MS_FALLBACK = {
    (10, 12, 10): 0.86,
    (10, 15, 10): 34.83,
    (10, 20, 10): 265.17,
    (11, 22, 11): 2752.03,
    (12, 24, 12): 30789.93,
    (13, 26, 13): 368153.26,
}

_GROWTH_RE = re.compile(
    r'^\(a\{(\d+),(\d+)\}\)\{(\d+),\d+\}\s+n=\s*\d+\s+([\d.]+)\s+ms')


def python_ms():
    """Parse out/python_growth.txt; fall back to the embedded snapshot."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        '..', 'out', 'python_growth.txt')
    try:
        rows = {}
        for line in open(path):
            m = _GROWTH_RE.match(line)
            if m:
                rows[(int(m.group(1)), int(m.group(2)), int(m.group(3)))] = \
                    float(m.group(4))
        if len(rows) >= 5:
            return rows, 'out/python_growth.txt'
    except OSError:
        pass
    return PYTHON_MS_FALLBACK, 'the embedded fallback snapshot'


def ratios():
    """R26 E8's argument: python's TIMES track the law's NODE COUNTS.

    This is stronger evidence that python walks the same tree than any single
    wall-clock comparison, because it is four independent size steps agreeing
    on a RATE rather than one pair agreeing on a value -- and the law was
    derived from pcrec's emitted search, not from python.
    """
    ms, src = python_ms()
    ks = [k for k in [(10, 15, 10), (10, 20, 10), (11, 22, 11),
                      (12, 24, 12), (13, 26, 13)] if k in ms]
    print('python times read from %s\n' % src)
    print('%-18s %-18s %10s %10s %10s'
          % ('from', 'to', 'python', 'law', 'agree'))
    worst = 0.0
    for a, b in zip(ks, ks[1:]):
        pr = ms[b] / ms[a]
        lr = law(b[0], b[1], b[2]) / law(a[0], a[1], a[2])
        d = abs(pr - lr) / lr * 100
        worst = max(worst, d)
        print('%-18s %-18s %9.2fx %9.2fx %9.1f%%' % (a, b, pr, lr, d))
    print('\nworst disagreement %.1f%% over %d size steps.' % (worst, len(ks) - 1))


def grid(budget=1000000):
    print('Smallest inner MINIMUM m at which the family (a{m,m+w}){m,P} '
          'exceeds a %d-step budget\nat its own exact-minimum subject length '
          'n = m*m, by inner-range WIDTH w.\n' % budget)
    print('%-6s %-8s %-10s %16s' % ('width', 'first m', 'n = m*m', 'steps'))
    for w in range(0, 13):
        for m in range(2, 40):
            s = law(m, m + w, m)
            if s is not None and s > budget:
                print('%-6d %-8d %-10d %16d' % (w, m, m * m, s))
                break
        else:
            print('%-6d %-8s %-10s %16s' % (w, '>39', '-', '-'))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--grid', action='store_true')
    ap.add_argument('--ratios', action='store_true')
    ap.add_argument('--budget', type=int, default=1000000)
    a = ap.parse_args()
    if a.ratios:
        ratios()
        raise SystemExit(0)
    if a.check or not (a.check or a.grid):
        rc = 1 if check() else 0
        if not a.grid:
            raise SystemExit(rc)
    if a.grid:
        grid(a.budget)
