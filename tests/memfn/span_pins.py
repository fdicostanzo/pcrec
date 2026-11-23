#!/usr/bin/env python3
"""tests/memfn/span_pins.py -- the vector span's T-TABLE PIN CELLS and SPAN-SEED's
V-site census (R-47 U4, docs/design/memfn/block_span.md §10.1, §10.2). Run
inside C18's section (simd_floor_check.py calls `run`), or alone:

    span_pins.py --pcrec BIN --harness BIN --trace BIN [--tree TREE]

THE PIN CELLS (22, §10.2's table). Each cell is a pattern, a width and flags,
rendered by pcrec, and the check COUNTS TEXT: the selector calls
`<p>_mf<h>_vs<j>(<p>_mf<h>_s, <p>_mf<h>_c)` and, at the SIMD layer,
`__w32(<p>_mf<h>_s, <p>_mf<h>_c)` ("present" = 1 and 1, "absent" = 0 and 0;
the definition heads match neither spelling). The counts are WHOLE-FILE
counts of those spellings, not "in the walk" / "in the selector": WHERE the
call sits (the walk calls the selector, the selector calls its level) is the
routing leg's (tests/memfn/routing_shape.py, C18 (d)) structure check, not
this one's (r78 PINS-8). The expectations below are LITERALS written from the
design's table, never read from window.c or from the kit's own answer; the
cell ids run 1..22 and no two cells are the same cell (checked). Their
control is the §10.1 k source (tests/memfn/span_ksource.py, the one reader
G2-V shares), which shares no code with the table: per cell the finder row
and frame from the traced build's `MFTRACE FDROUTE` record, k and C-own from
the head-0 lever compile's loop text, and the predicate applied THERE. A cell
is red when (a) its row or k is not the literal the design names (the cell no
longer reaches the row it guards, K35), (b) the text count is not the
literal, or (c) the predicate and the literal disagree. Cell 16 (two
eligible stretches) also holds the FIRST stretch's k and second's, and that
the selector call is the first stretch's test (the call is followed by the
test of the byte at the first stretch's END).

SPAN-SEED (§10.1): the 41 patterns of tests/memfn/span_seed.rxt (read with
`pcrec --list-source`, never a copied list), at width 32 and 4095, byte AND
`-e utf8`, at the SIMD layer: the V sites by the k source (each site's first
eligible stretch) against the selector calls of the shipped text, PER HANDLE
(each V site exactly one call), printed both ways and red on a disagreement;
floored 28 / 31 (byte) and 20 / 21 (utf8), the design's literals. It prints
the populations of the predicate's terms no site may reach (K35):
not-own eligible loops (R-5's C-own; 0 on SPAN-SEED) and non-E-find sites
with an in-range loop (the frame term's: 0, because SPAN-SEED's non-E-find
sites, E-stmt at width 32, render no head-0 loop at all, so the frame term
is UNREACHABLE on this population; the non-E-find site count is printed
beside it). Both terms are failable all the same: the run first holds
span_ksource's synthetic controls, one per predicate term (frame, C-own,
the bounds, the first eligible stretch).
"""
import argparse
import collections
import concurrent.futures
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TREE = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(TREE, 'scripts'))
sys.path.insert(0, HERE)
import span_ksource as ks    # noqa: E402  (the one k-source reader, r78 PINS-7)

V3 = '-fmemfn-simd=x86-64-v3'
OFF = '-fno-memfn-simd'
HEX = '[0-9a-f]'
DIG = '[0-9]'
# (cell, pattern, width, binary, extra flags, layers, selector calls, row, k)
# row/k: what the k source must read (the cell's reach; k a tuple = every stretch's k, in
# order); calls: the literal expectation (present = 1, absent = 0) at the SIMD layer, and 0
# at the default layer where the cell names one (cells 17-22 only).
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
    (16, HEX + '{20}[g-z]{20}', 4095, 'pcrec', [], ['v3'], 1, 'D-hors', (20, 19)),
    (17, HEX + '{17}', 32, 'harness', ['--harness=span-head=8'], ['off'], 0, 'D-hors', 16),
    (18, HEX + '{17}', 32, 'harness', ['--harness=span-head=8'], ['v3'], 0, 'D-hors', 16),
    (19, HEX + '{17}', 32, 'pcrec', ['--memfn=span-loop'], ['off'], 0, 'D-hors', 16),
    (20, HEX + '{17}', 32, 'pcrec', ['--memfn=span-loop'], ['v3'], 0, 'D-hors', 16),
    # r78 PLANTSA-2: T-deny ahead of V (§3), both layers
    (21, HEX + '{17}', 32, 'pcrec', ['--memfn=no-span-loop'], ['off'], 0, 'D-hors', 16),
    (22, HEX + '{17}', 32, 'pcrec', ['--memfn=no-span-loop'], ['v3'], 0, 'D-hors', 16),
]
CELLS_FLOOR = 22            # the cells, not the 11 patterns
SEED_FLOOR = {('byte', 32): 28, ('byte', 4095): 31, ('utf8', 32): 20, ('utf8', 4095): 21}
ENCS = {'byte': [], 'utf8': ['-e', 'utf8']}
SEED_PATTERNS = 41
# T-lever, T-force and T-deny ahead of V: a cell carrying one expects 0 calls though V's row holds
OVERRIDE = ('--harness=span-head=', '--memfn=span-loop', '--memfn=no-span-loop')
# the k source reads the head-0 LOOP text; T-deny's text is all-inline (no loop), so a deny cell's
# k source is read without the deny (the site's own row and k, which the deny overrides)
KSRC_DROP = ('--memfn=no-span-loop',)

CALL = re.compile(r'rxa_mf(\d+)_vs\d+\(rxa_mf\1_s, rxa_mf\1_c\)')
W32 = re.compile(r'__w32\(rxa_mf(\d+)_s, rxa_mf\1_c\)')
# the selector call and the subject offset of the test right after it (PINS-4: the call is the
# first stretch's when the next test reads the first stretch's END)
CALL_NEXT = re.compile(r'rxa_mf(\d+)_vs\d+\(rxa_mf\1_s, rxa_mf\1_c\) && \(+rxa_mf\1_s\[rxa_mf\1_c \+ (\d+)\]')


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


def k_source(trace, harness, pat, width, flags):
    """({site: (row, frame)}, {handle: [(lo, end, own), ...]}) read by §10.1's k source
    (span_ksource's one reader), or None."""
    t = sh([trace, '-p', 'rxa', '--features', 'all'] + flags + ['--window-search-width=%d' % width,
           '-o', '-', '--pattern', pat])
    h = sh([harness, '-p', 'rxa', '--features', 'all', '--harness=span-head=0'] +
           [f for f in flags if not f.startswith('--harness=')] +
           ['--window-search-width=%d' % width, '-o', '-', '--pattern', pat])
    if t is None or h is None or t.returncode or h.returncode:
        return None
    rows = ks.routes(t.stdout.decode('utf-8', 'replace'), t.stderr.decode('utf-8', 'replace'))
    return rows, ks.loops(h.stdout.decode('utf-8', 'surrogateescape'))


def pin_cell(c, pcrec, harness, trace):
    """The pin cell `c`'s verdicts: [(ok, message)]."""
    num, pat, width, which, flags, layers, calls, row, k = c
    out = []
    binp = harness if which == 'harness' else pcrec
    src = k_source(trace, harness, pat, width,
                   [f for f in flags if f.startswith('--memfn=') and f not in KSRC_DROP])
    if src is None:
        return [(False, 'cell %d %s: the k source did not run' % (num, pat))]
    rows, loops = src
    got_row, frame = rows.get(1, ('-', '-'))
    got_ks = tuple(end - lo for lo, end, _ in loops.get(1, []))
    want_ks = k if isinstance(k, tuple) else (k,)
    got_k = got_ks[:len(want_ks)] if isinstance(k, tuple) else got_ks[:1]
    out.append((got_row == row and got_k == want_ks and frame == 'E-find',
                'cell %d %s w%d: the k source reads row %s k %s frame %s (the cell guards %s, k %s)'
                % (num, pat, width, got_row, '/'.join(map(str, got_ks)) or '-', frame, row,
                   '/'.join(map(str, want_ks)))))
    vs = ks.v_sites(rows, loops)
    would_v = 1 in vs
    if isinstance(k, tuple):
        # every stretch the cell names is eligible, and the k source's pick is the FIRST
        elig = [ks.eligible(got_row, frame, end - lo, own) for lo, end, own in loops.get(1, [])]
        out.append((len(elig) >= len(want_ks) and all(elig[:len(want_ks)]) and would_v and vs[1][2] == 0,
                    'cell %d: the k source reads stretches eligible %s, first eligible index %s (all '
                    'eligible, index 0)' % (num, elig, vs[1][2] if would_v else '-')))
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
                    'cell %d %s w%d %s %s: %d selector call(s), %d __w32 call(s) in the file (literal %d, %d)'
                    % (num, pat, width, ly, ' '.join(flags), sel, w32, calls, want_w32)))
        if isinstance(k, tuple) and calls and would_v:
            # the selector call is the FIRST stretch's test: the test after it reads the first
            # stretch's END (the second stretch's first byte)
            nxt = [int(o) for h, o in CALL_NEXT.findall(text) if int(h) == 1]
            end0 = vs[1][4]
            out.append((nxt == [end0],
                        'cell %d %s %s: the test after the selector call reads s[c + %s] (the first '
                        'stretch ends at %d)' % (num, pat, ly, '/'.join(map(str, nxt)) or '-', end0)))
    return out


def seed_site(pcrec, harness, trace, pat, width, enc):
    """(V sites by the k source, {handle: selector calls} in the kit's text, the term census)
    for one seed pattern."""
    src = k_source(trace, harness, pat, width, enc)
    text = render(pcrec, pat, width, enc + [V3])
    if src is None or text is None:
        return None
    rows, loops = src
    byk = set(ks.v_sites(rows, loops))
    kit = collections.Counter(int(h) for h in CALL.findall(text))
    return byk, kit, ks.census(rows, loops)


def check_cells(bad):
    """The cell list itself: ids 1..N in order, no two cells the same (r78 PINS-3)."""
    ids = [c[0] for c in CELLS]
    if ids != list(range(1, len(CELLS) + 1)):
        bad('T-table pins: the cell ids are %s, not 1..%d in order' % (ids, len(CELLS)))
        return False
    keys = [(c[1], c[2], c[3], tuple(c[4]), tuple(c[5])) for c in CELLS]
    dup = sorted({i + 1 for i, kk in enumerate(keys) if keys.count(kk) > 1})
    if dup:
        bad('T-table pins: cells %s are the same cell (pattern, width, binary, flags, layers)' % dup)
        return False
    return True


def run(pcrec, harness, trace, ok, bad, jobs=4, tree=TREE):
    import emit_sweep as es
    # the k source's predicate, term by term, on synthetic records (span_ksource.SELFTEST):
    # the terms SPAN-SEED's population cannot reach (C-own, frame) are failable here
    for name, good, got in ks.selftest():
        ok() if good else bad('k source control %s: got %r' % (name, got))
    with concurrent.futures.ThreadPoolExecutor(jobs) as ex:
        n = 0
        for res in ex.map(lambda c: pin_cell(c, pcrec, harness, trace), CELLS):
            for good, msg in res:
                ok() if good else bad(msg)
            n += 1
        distinct = check_cells(bad)
        if n >= CELLS_FLOOR and distinct:
            ok('T-table pins: %d distinct cells (floor %d)' % (n, CELLS_FLOOR))
        elif n < CELLS_FLOOR:
            bad('T-table pins: %d cells < floor %d (a population nobody counted, K35)' % (n, CELLS_FLOOR))
        seed = os.path.join(tree, 'tests/memfn/span_seed.rxt')
        pats = sorted({p for _, p in es.list_source_patterns(pcrec, seed, 60)})
        if len(pats) < SEED_PATTERNS:
            bad('SPAN-SEED: %d patterns read from tests/memfn/span_seed.rxt, fewer than the committed %d'
                % (len(pats), SEED_PATTERNS))
        for (enc, width), floor in sorted(SEED_FLOOR.items()):
            lab = '%s w%d' % (enc, width)
            res = list(ex.map(lambda p: seed_site(pcrec, harness, trace, p, width, ENCS[enc]), pats))
            if any(r is None for r in res):
                bad('SPAN-SEED %s: a pattern did not compile' % lab)
                continue
            bysrc = sum(len(r[0]) for r in res)
            kit = sum(sum(r[1].values()) for r in res)
            # per handle: the same sites, and each V site exactly ONE selector call (r78 PINS-5)
            dis = [(p, r) for p, r in zip(pats, res) if r[0] != set(r[1]) or any(v != 1 for v in r[1].values())]
            cen = {t: sum(r[2][t] for r in res) for t in res[0][2]} if res else {}
            print('SPAN-SEED %s: %d V sites by the k source, %d selector calls in the shipped text (floor %d); '
                  'not-own eligible loops: %d; non-E-find sites: %d, with an in-range loop: %d'
                  % (lab, bysrc, kit, floor, cen.get('not_own', 0), cen.get('non_efind', 0),
                     cen.get('non_efind_in_range', 0)))
            for p, r in dis[:5]:
                bad('SPAN-SEED %s %r: k source sites %s, the shipped text\'s calls per handle %s'
                    % (lab, p, sorted(r[0]), dict(sorted(r[1].items()))))
            if not dis:
                ok('SPAN-SEED %s: the k source and the shipped text agree on every site, one call each' % lab)
            if bysrc >= floor:
                ok('SPAN-SEED %s: V sites %d >= floor %d' % (lab, bysrc, floor))
            else:
                bad('SPAN-SEED %s: V sites %d < floor %d (K35)' % (lab, bysrc, floor))


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
