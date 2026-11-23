#!/usr/bin/env python3
"""tests/memfn/span_ksource.py -- THE k SOURCE of the vector span, the ONE reader of
docs/design/memfn/block_span.md §10.1's ruled fact (R-19), imported by every check
that counts V sites independently of the kit's table: tests/memfn/span_pins.py
(the T-table pin cells, SPAN-SEED's census) and memfn/tests/g2_vspan.py (G2-V whole's
populations, G2-V unit's LO/K). Lane bsu4fix, r78 PINS-7 (the cheap part: one
reader; the declared predicate table and a cell TSV stay PLAN).

Two texts feed it, neither the kit's table:
  - the traced build's `MFTRACE FDROUTE ... site=S row=R ... frame=F` records
    (a `-DMF_TRACE` kit: tests/memfn/mk_mftrace_lib.sh), read by `routes`;
  - the head-0 lever compile's loop text (`--harness=span-head=0`):
    `<p>_mf<h>_j = LO; for (; <p>_mf<h>_j < END; <p>_mf<h>_j++) if (COND) break;`,
    k = END - LO, read by `loops`. C-OWN is read off COND: a stretch is C-own when
    its test reads no table (no `[` once the subject reads `<p>_mf<h>_s[...]` are
    removed; R-5).
The predicate (D-hors 16..1000, R7w 24..64, frame E-find, C-own, FIRST eligible
stretch per site) is applied HERE, in `v_sites`, and nowhere else.

Shares no code with the kit (memfn/src/) and reads none of its tables.
"""
import re

LOOP = re.compile(r'\b(\w+?)_mf(\d+)_j = (-?\d+); for \(; \1_mf\2_j < (-?\d+); \1_mf\2_j\+\+\) '
                  r'if \((.*?)\) break;')
FDROUTE = re.compile(r'^MFTRACE FDROUTE \S+ site=(\d+) row=(\S+) \S+ \S+ frame=(\S+)', re.M)
SUBJ_READ = re.compile(r'\w+_mf\d+_s\[[^\]]*\]')

ROW_K = {'D-hors': (16, 1000), 'R7w': (24, 64)}     # the row bounds (§3, T-vwin / T-vscan)
FRAME = 'E-find'


def routes(*texts):
    """{site: (row, frame)} from every `MFTRACE FDROUTE` record in the texts."""
    out = {}
    for t in texts:
        for s, r, f in FDROUTE.findall(t):
            out[int(s)] = (r, f)
    return out


def loops(text):
    """{handle: [(lo, end, own), ...]} in text order: the head-0 lever compile's stretches."""
    out = {}
    for _p, h, lo, end, cond in LOOP.findall(text):
        own = '[' not in SUBJ_READ.sub('', cond)
        out.setdefault(int(h), []).append((int(lo), int(end), own))
    return out


def in_range(row, k):
    b = ROW_K.get(row)
    return b is not None and b[0] <= k <= b[1]


def eligible(row, frame, k, own):
    """The predicate, whole: row bounds, frame E-find, C-own."""
    return frame == FRAME and own and in_range(row, k)


def v_sites(rts, lps):
    """{site: (row, k, index, lo, end)}: each site's FIRST eligible stretch (index = its
    position among the site's head-0 loops)."""
    v = {}
    for site, (row, frame) in rts.items():
        for i, (lo, end, own) in enumerate(lps.get(site, [])):
            if eligible(row, frame, end - lo, own):
                v[site] = (row, end - lo, i, lo, end)
                break
    return v


def census(rts, lps):
    """The populations the predicate's terms decide (K35), so a term no site reaches is
    printed as 0 rather than unseen: `not_own` stretches in range on E-find but not C-own;
    `non_efind` sites whose frame is not E-find; `non_efind_in_range` those of them with an
    in-range stretch (the frame term's own population)."""
    c = {'not_own': 0, 'non_efind': 0, 'non_efind_in_range': 0}
    for site, (row, frame) in rts.items():
        ls = lps.get(site, [])
        if frame != FRAME:
            c['non_efind'] += 1
            if any(own and in_range(row, end - lo) for lo, end, own in ls):
                c['non_efind_in_range'] += 1
            continue
        c['not_own'] += sum(1 for lo, end, own in ls if in_range(row, end - lo) and not own)
    return c


# ---- the predicate's own controls (r78 PINS-1/PINS-2) ----------------------------------------
# SPAN-SEED reaches neither a not-own stretch nor a non-E-find site with an in-range loop (both
# populations print 0), so each term is held here on SYNTHETIC records written from §10.1's
# words: a term dropped from `eligible` or `v_sites` turns its control red.
_OWN = 'rxa_mf1_s[rxa_mf1_c + rxa_mf1_j] >= 48'
_TAB = 'rxa_mf1_t[rxa_mf1_s[rxa_mf1_c + rxa_mf1_j]]'
SELFTEST = [
    # (name, routes, head-0 text, expected v_sites as {site: (row, k, index)})
    ('D-hors k16 own E-find', {1: ('D-hors', 'E-find')},
     'rxa_mf1_j = 0; for (; rxa_mf1_j < 16; rxa_mf1_j++) if (!(%s)) break;' % _OWN, {1: ('D-hors', 16, 0)}),
    ('the frame term: E-stmt', {1: ('D-hors', 'E-stmt')},
     'rxa_mf1_j = 0; for (; rxa_mf1_j < 16; rxa_mf1_j++) if (!(%s)) break;' % _OWN, {}),
    ('the C-own term: a table read', {1: ('D-hors', 'E-find')},
     'rxa_mf1_j = 0; for (; rxa_mf1_j < 16; rxa_mf1_j++) if (!(%s)) break;' % _TAB, {}),
    ('the bounds: D-hors k15', {1: ('D-hors', 'E-find')},
     'rxa_mf1_j = 0; for (; rxa_mf1_j < 15; rxa_mf1_j++) if (!(%s)) break;' % _OWN, {}),
    ('the bounds: R7w k23 / k65', {1: ('R7w', 'E-find'), 2: ('R7w', 'E-find')},
     'rxa_mf1_j = 1; for (; rxa_mf1_j < 24; rxa_mf1_j++) if (!(%s)) break; '
     'rxa_mf2_j = 1; for (; rxa_mf2_j < 66; rxa_mf2_j++) if (!(%s)) break;' % (_OWN, _OWN.replace('mf1', 'mf2')), {}),
    ('the first eligible stretch', {1: ('D-hors', 'E-find')},
     'rxa_mf1_j = 0; for (; rxa_mf1_j < 10; rxa_mf1_j++) if (!(%s)) break; '
     'rxa_mf1_j = 10; for (; rxa_mf1_j < 30; rxa_mf1_j++) if (!(%s)) break; '
     'rxa_mf1_j = 30; for (; rxa_mf1_j < 49; rxa_mf1_j++) if (!(%s)) break;' % (_OWN, _OWN, _OWN),
     {1: ('D-hors', 20, 1)}),
]


def selftest():
    """[(name, ok, got)] for the predicate's synthetic controls."""
    out = []
    for name, rts, text, want in SELFTEST:
        got = {s: v[:3] for s, v in v_sites(rts, loops(text)).items()}
        out.append((name, got == want, got))
    return out


if __name__ == '__main__':
    import sys
    bad = 0
    for name, good, got in selftest():
        print('%s: control %s%s' % ('PASS' if good else 'FAIL', name, '' if good else ' (got %r)' % got))
        bad += not good
    sys.exit(1 if bad else 0)
