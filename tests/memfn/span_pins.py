#!/usr/bin/env python3
"""tests/memfn/span_pins.py -- the vector span's T-TABLE PIN CELLS and SPAN-SEED's
V-site census (R-47 U4, docs/design/memfn/block_span.md §10.1, §10.2). Run
inside C18's section (simd_floor_check.py calls `run`), or alone:

    span_pins.py --pcrec BIN --harness BIN --trace BIN [--tree TREE]

THE PIN CELLS (20, §10.2's table). Each cell is a pattern, a width and flags,
rendered by pcrec, and the check COUNTS TEXT: the selector calls
`<p>_mf<h>_vs<j>(<p>_mf<h>_s, <p>_mf<h>_c)` in the walk and, at the SIMD layer,
`__w32(<p>_mf<h>_s, <p>_mf<h>_c)` in the selector ("present" = 1 and 1,
"absent" = 0 and 0; the definition heads match neither spelling). The
expectations below are LITERALS written from the design's table, never read
from window.c or from the kit's own answer. Their control is the §10.1 k
source, which shares no code with the table: per cell the finder row and
frame from the traced build's `MFTRACE FDROUTE` record, k from the head-0
lever compile's loop text (`<p>_mf<h>_j = LO; for (; <p>_mf<h>_j < END`, k = END
- LO), and the predicate (D-hors 16..1000, R7w 24..64, frame E-find) applied
HERE. A cell is red when (a) its row or k is not the literal the design names
(the cell no longer reaches the row it guards, K35), (b) the text count is not
the literal, or (c) the predicate and the literal disagree.

SPAN-SEED (§10.1): the 41 patterns of tests/memfn/span_seed.rxt (read with
`pcrec --list-source`, never a copied list), at width 32 and 4095, at the SIMD
layer: the V sites by the k source (per site, any stretch the predicate admits)
against the selector calls of the shipped text, per site, printed both ways and
red on a disagreement; floored 28 / 31 (the design's literals).
"""
import argparse
import concurrent.futures
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TREE = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(TREE, 'scripts'))

V3 = '-fmemfn-simd=x86-64-v3'
OFF = '-fno-memfn-simd'
HEX = '[0-9a-f]'
DIG = '[0-9]'
# (cell, pattern, width, binary, extra flags, layers, selector calls, row, k)
# row/k: what the k source must read (the cell's reach); calls: the literal expectation
# (present = 1, absent = 0) at the SIMD layer, and 0 at the default layer where the
# cell names one (cells 17-20 only).
CELLS = [
    (1, HEX + '{16}', 32, 'pcrec', [], ['v3'], 0, 'D-hors', 15),
    (2, HEX + '{16}', 4095, 'pcrec', [], ['v3'], 0, 'D-hors', 15),
    (3, HEX + '{17}', 32, 'pcrec', [], ['v3'], 1, 'D-hors', 16),
    (4, HEX + '{17}', 4095, 'pcrec', [], ['v3'], 1, 'D-hors', 16),
    (5, HEX + '{1001}', 4095, 'pcrec', [], ['v3'], 1, 'D-hors', 1000),
    (6, HEX + '{1002}', 4095, 'pcrec', [], ['v3'], 0, 'D-hors', 1001),
    (7, DIG + '{24}', 32, 'pcrec', [], ['v3'], 0, 'R7w', 23),
    (8, DIG + '{24}', 4095, 'pcrec', [], ['v3'], 0, 'R7w', 23),
    (9, DIG + '{25}', 32, 'pcrec', [], ['v3'], 1, 'R7w', 24),
    (10, DIG + '{25}', 4095, 'pcrec', [], ['v3'], 1, 'R7w', 24),
    (11, DIG + '{65}', 4095, 'pcrec', [], ['v3'], 1, 'R7w', 64),
    (12, DIG + '{66}', 4095, 'pcrec', [], ['v3'], 0, 'R7w', 65),
    (13, 'ab' + DIG + '{26}', 32, 'pcrec', [], ['v3'], 0, 'D1', 26),
    (14, '[xy]' + DIG + '{26}', 32, 'pcrec', [], ['v3'], 0, 'PAIR', 26),
    (15, 'ab' + DIG + '{26}', 32, 'pcrec', ['--memfn=no-fd-d1'], ['v3'], 0, 'D1w', 26),
    (16, HEX + '{20}[g-z]{20}', 4095, 'pcrec', [], ['v3'], 1, 'D-hors', 20),
    (17, HEX + '{17}', 32, 'harness', ['--harness=span-head=8'], ['off'], 0, 'D-hors', 16),
    (18, HEX + '{17}', 32, 'harness', ['--harness=span-head=8'], ['v3'], 0, 'D-hors', 16),
    (19, HEX + '{17}', 32, 'pcrec', ['--memfn=span-loop'], ['off'], 0, 'D-hors', 16),
    (20, HEX + '{17}', 32, 'pcrec', ['--memfn=span-loop'], ['v3'], 0, 'D-hors', 16),
]
CELLS_FLOOR = 20            # the cells, not the 11 patterns
SEED_FLOOR = {32: 28, 4095: 31}
SEED_PATTERNS = 41
OVERRIDE = ('--harness=span-head=', '--memfn=span-loop')    # T-lever, T-force ahead of V

CALL = re.compile(r'rxa_mf(\d+)_vs\d+\(rxa_mf\1_s, rxa_mf\1_c\)')
W32 = re.compile(r'__w32\(rxa_mf(\d+)_s, rxa_mf\1_c\)')
LOOP = re.compile(r'rxa_mf(\d+)_j = (\d+); for \(; rxa_mf\1_j < (\d+)')
FDR = re.compile(r'MFTRACE FDROUTE \S+ site=(\d+) row=(\S+) \S+ \S+ frame=(\S+)')


def sh(argv, timeout=60):
    try:
        return subprocess.run(argv, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None


def render(binp, pat, width, flags):
    r = sh([binp, '-p', 'rxa', '--features', 'all'] + flags + ['--window-search-width=%d' % width,
            '-o', '-', '--pattern', pat])
    if r is None or r.returncode:
        return None
    return r.stdout.decode('utf-8', 'surrogateescape')


def eligible(row, frame, k):
    """§10.1's predicate, applied here and nowhere else: D-hors 16..1000, R7w 24..64, E-find."""
    return frame == 'E-find' and ((row == 'D-hors' and 16 <= k <= 1000) or (row == 'R7w' and 24 <= k <= 64))


def k_source(trace, harness, pat, width, flags):
    """({site: (row, frame)}, {handle: [k, ...]}) read by §10.1's k source, or None."""
    t = sh([trace, '-p', 'rxa', '--features', 'all'] + flags + ['--window-search-width=%d' % width,
           '-o', '-', '--pattern', pat])
    h = sh([harness, '-p', 'rxa', '--features', 'all', '--harness=span-head=0'] +
           [f for f in flags if not f.startswith('--harness=')] +
           ['--window-search-width=%d' % width, '-o', '-', '--pattern', pat])
    if t is None or h is None or t.returncode or h.returncode:
        return None
    rows = {int(s): (r, f) for s, r, f in FDR.findall((t.stdout + t.stderr).decode('utf-8', 'replace'))}
    ks = {}
    for hd, lo, end in LOOP.findall(h.stdout.decode('utf-8', 'surrogateescape')):
        ks.setdefault(int(hd), []).append(int(end) - int(lo))
    return rows, ks


def pin_cell(c, pcrec, harness, trace):
    """The pin cell `c`'s verdicts: [(ok, message)]."""
    num, pat, width, which, flags, layers, calls, row, k = c
    out = []
    binp = harness if which == 'harness' else pcrec
    ks = k_source(trace, harness, pat, width, [f for f in flags if f.startswith('--memfn=')])
    if ks is None:
        return [(False, 'cell %d %s: the k source did not run' % (num, pat))]
    rows, loops = ks
    got_row, frame = rows.get(1, ('-', '-'))
    got_k = loops.get(1, [0])[0]
    out.append((got_row == row and got_k == k and frame == 'E-find',
                'cell %d %s w%d: the k source reads row %s k %d frame %s (the cell guards %s, k %d)'
                % (num, pat, width, got_row, got_k, frame, row, k)))
    would_v = eligible(got_row, frame, got_k) and 1 in loops
    overridden = any(f.startswith(OVERRIDE) for f in flags)
    # the literal expectation against the predicate: an override cell expects 0 though V's
    # own predicate holds there (the plant of an out-of-order V would put a call in)
    exp_by_k = 1 if (would_v and not overridden) else 0
    out.append((exp_by_k == calls and (not overridden or would_v),
                'cell %d: the literal expectation %d, the k source\'s predicate %d%s'
                % (num, calls, exp_by_k, ' (V\'s own row holds, the override is ahead of it)'
                   if overridden and would_v else '')))
    for ly in layers:
        text = render(binp, pat, width, flags + [V3 if ly == 'v3' else OFF])
        if text is None:
            out.append((False, 'cell %d %s %s: pcrec failed to render' % (num, pat, ly)))
            continue
        sel, w32 = len(CALL.findall(text)), len(W32.findall(text))
        want_w32 = calls if ly == 'v3' else 0
        out.append((sel == calls and w32 == want_w32,
                    'cell %d %s w%d %s %s: %d selector call(s) in the walk, %d __w32 call(s) (literal %d, %d)'
                    % (num, pat, width, ly, ' '.join(flags), sel, w32, calls, want_w32)))
    return out


def seed_site(pcrec, harness, trace, pat, width):
    """(V sites by the k source, V sites by the kit's text) for one seed pattern: sets of handles."""
    ks = k_source(trace, harness, pat, width, [])
    text = render(pcrec, pat, width, [V3])
    if ks is None or text is None:
        return None
    rows, loops = ks
    byk = {h for h, ls in loops.items() if h in rows and any(eligible(rows[h][0], rows[h][1], k) for k in ls)}
    kit = {int(h) for h in CALL.findall(text)}
    return byk, kit


def run(pcrec, harness, trace, ok, bad, jobs=4, tree=TREE):
    import emit_sweep as es
    with concurrent.futures.ThreadPoolExecutor(jobs) as ex:
        n = 0
        for res in ex.map(lambda c: pin_cell(c, pcrec, harness, trace), CELLS):
            for good, msg in res:
                ok() if good else bad(msg)
            n += 1
        if n >= CELLS_FLOOR:
            ok('T-table pins: %d cells (floor %d)' % (n, CELLS_FLOOR))
        else:
            bad('T-table pins: %d cells < floor %d (a population nobody counted, K35)' % (n, CELLS_FLOOR))
        seed = os.path.join(tree, 'tests/memfn/span_seed.rxt')
        pats = sorted({p for _, p in es.list_source_patterns(pcrec, seed, 60)})
        if len(pats) < SEED_PATTERNS:
            bad('SPAN-SEED: %d patterns read from tests/memfn/span_seed.rxt, fewer than the committed %d'
                % (len(pats), SEED_PATTERNS))
        for width, floor in sorted(SEED_FLOOR.items()):
            res = list(ex.map(lambda p: seed_site(pcrec, harness, trace, p, width), pats))
            if any(r is None for r in res):
                bad('SPAN-SEED w%d: a pattern did not compile' % width)
                continue
            bysrc = sum(len(r[0]) for r in res)
            kit = sum(len(r[1]) for r in res)
            dis = [(p, r) for p, r in zip(pats, res) if r[0] != r[1]]
            print('SPAN-SEED w%d: %d V sites by the k source, %d selector calls in the shipped text (floor %d)'
                  % (width, bysrc, kit, floor))
            for p, r in dis[:5]:
                bad('SPAN-SEED w%d %r: k source sites %s, the shipped text %s' % (width, p, sorted(r[0]), sorted(r[1])))
            if not dis:
                ok('SPAN-SEED w%d: the k source and the shipped text agree on every site' % width)
            if bysrc >= floor:
                ok('SPAN-SEED w%d: V sites %d >= floor %d' % (width, bysrc, floor))
            else:
                bad('SPAN-SEED w%d: V sites %d < floor %d (K35)' % (width, bysrc, floor))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pcrec', required=True)
    ap.add_argument('--harness', required=True)
    ap.add_argument('--trace', required=True)
    ap.add_argument('--tree', default=TREE)
    a = ap.parse_args()
    passed, failed = [0], []

    def ok(msg=None):
        passed[0] += 1
        if msg:
            print('PASS: ' + msg)

    def bad(msg):
        failed.append(msg)
        print('FAIL: ' + msg)

    run(a.pcrec, a.harness, a.trace, ok, bad, tree=a.tree)
    print('checks passed: %d' % passed[0])
    print('checks failed: %d' % len(failed))
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
