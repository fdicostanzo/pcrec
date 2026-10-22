#!/usr/bin/env python3
"""tests/memfn/rank_check.py -- [MEMFN] RQ-2's check (D157; memfn.h's
`mf_pred.rank_n`/`rank_pos`/`rank_ppm`). Driven by tests/memfn/run_rank.sh,
which builds the PROBE compiler (`-DPCREC_RANK_PROBE`: src/gen/memfn_sites.c
prints one `RANK` line per predicate of every PRE/OFS site it hands the kit,
with the ranking that predicate carries).

THE CLAIM (since D172 S2 commit 6, lane wsc6; the kit manager's R1). pcrec
hands the kit NO ranking: the ranking (`rank_n`/`rank_pos`/`rank_ppm`) and
`plan_hint` are the kit's RENDERER INTERFACE, written by the window family's
translation and by G2, never by a host. Every predicate of every PRE/OFS site
pcrec defines therefore carries rank_n 0 and names no RUN term. (Until then
the claim was that pcrec's ranking equals a brute force; that ranking, its
builder `ofs_pred_rank` and its reader `pcrec_find_run_rank` retired with
it, and the kit's own ranking is the translation's.)

N4, THE FIND DOOR (R17-a, setfind.md §11.1 item 4): the same probe build
asserts, wherever pcrec emits the table a DEFINED FIND names (the DFA set
rows' `can_begin_match`/`start_bytes`, the VM hat's `start_set`), that its
bytes are the set the kit was handed; a pass prints one `FINDDOOR` line, a
difference fails the compile with an `N4 door` internal error. Red on any
such error; the passes are floored per table (K35).

NON-VACUITY (K35): a floor on the predicates seen, and the door floors.

Prints `checks passed: N` / `checks failed: N`; exit 1 on any failure.
"""
import argparse
import concurrent.futures
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TREE = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(TREE, 'scripts'))
import emit_sweep as es  # noqa: E402

ARMS = [
    ('byte', []),
    ('utf8', ['-e', 'utf8']),
    ('vm', ['--engine=vm']),
]
# Named witnesses (R-1's four timed cells, design §R4.9.7's two OFS shapes,
# a masked run whose prior pick is not positional).
NAMED = [
    'SELECT', '(?i)union.*?select.*?from', '(?:username|USERNAME|user|USER)=',
    '(?i)cat', 'it\\Nm', '/user|/users', 'abcdefghijklmn', '(?i)enzyme',
    'x[0-9]+Qz',
]
# N4's door floors (R17-a): set from lane r17a's landing measurement
# (r17a_report.md, the figure beside each), ~10% below it.
DOOR_CBM_FLOOR = 1400   # 1,574
DOOR_SB_FLOOR = 70      # 78
DOOR_SS_FLOOR = 3100    # 3,441
# The predicates seen (lane wsc6, D172 S2 commit 6; the figure beside it).
PRED_FLOOR = 5300  # rq2's landing read 5,891 predicate records (4,643 + 1,111 + 137); each remains, now rank_n 0
# Floors (K35), ~10% below the figure measured at the landing beside each:
# a FLOOR, never an equality pin.
FLOORS = {
    'pred': PRED_FLOOR,    # every predicate of every PRE/OFS site defined
    # R17-a (lane r17a): N4's door passes, per table (measured at landing)
    'door-can_begin_match': DOOR_CBM_FLOOR,
    'door-start_bytes': DOOR_SB_FLOOR,
    'door-start_set': DOOR_SS_FLOOR,
}


def doors(stderr):
    """(FINDDOOR passes per table, whether an `N4 door` error was raised)."""
    text = stderr.decode('utf-8', 'replace')
    n = {}
    for ln in text.splitlines():
        if ln.startswith('FINDDOOR\t'):
            tag = ln.split('\t')[1]
            n[tag] = n.get(tag, 0) + 1
    return n, 'N4 door' in text


def parse(stderr):
    recs = []
    for ln in stderr.decode('utf-8', 'replace').splitlines():
        if not ln.startswith('RANK\t'):
            continue
        _, site, idx, run, mask, ka, n, pos, mass = ln.split('\t')
        ints = (lambda f: [int(x) for x in f.split(',')] if f else [])
        recs.append((site, None if run == '-' else bytes.fromhex(run),
                     None if mask == '-' else bytes.fromhex(mask),
                     None if ka == '-' else int(ka), int(n), ints(pos), ints(mass)))
    return recs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--probe', required=True)
    ap.add_argument('--every', type=int, default=1)
    ap.add_argument('--jobs', type=int, default=8)
    ap.add_argument('--timeout', type=int, default=60)
    a = ap.parse_args()

    passed, failed = [0], []

    def ok(msg):
        passed[0] += 1
        print('PASS: ' + msg)

    def bad(msg):
        failed.append(msg)
        print('FAIL: ' + msg)

    corpus = es.enumerate_corpus(a.probe, TREE, 30)
    pats = sorted({p for _, _, p in corpus})
    pats = [p for i, p in enumerate(pats) if i % a.every == 0] + NAMED
    print('== RQ-2 rank check: %d distinct patterns, %d arms ==' % (len(pats), len(ARMS)))

    def one(job):
        pat, arm, argv = job
        cmd = [a.probe, '-p', 'rx', '--features', 'all'] + argv + ['-o', '-'] \
            + es._pattern_argv(a.probe, pat)
        rc, _, err = es.run(cmd, a.timeout)
        return pat, arm, rc, parse(err), doors(err)

    jobs = [(p, arm, argv) for p in pats for arm, argv in ARMS]
    n = {k: 0 for k in FLOORS}
    stated, door_bad = [], []
    with concurrent.futures.ThreadPoolExecutor(a.jobs) as ex:
        for pat, arm, rc, recs, (dn, derr) in ex.map(one, jobs):
            for tag, k in dn.items():
                n['door-' + tag] = n.get('door-' + tag, 0) + k
            if derr:
                door_bad.append((pat, arm))
            for site, run, mask, ka, rn, pos, mass in recs:
                n['pred'] += 1
                if run is not None or rn != 0:
                    stated.append((pat, arm, site, rn))
    for w in stated[:20]:
        print('  %r [%s] %s: a ranking or a scanned RUN term stated (rank_n %d)' % w)
    if stated:
        bad('%d predicates pcrec hands the kit state a ranking or a plan_hint naming a RUN '
            'term (the renderer interface is the kit\'s)' % len(stated))
    else:
        ok('no predicate pcrec hands the kit states a ranking or a scanned RUN term (%d)'
           % n['pred'])
    for w in door_bad[:20]:
        print('  %r [%s]: N4 door: a FIND set differs from its emitted table' % w)
    if door_bad:
        bad('%d compiles raised the N4 door assertion' % len(door_bad))
    else:
        ok('N4 door: every defined FIND\'s set equals its emitted table (%d tables)'
           % sum(v for k, v in n.items() if k.startswith('door-')))
    for k, floor in FLOORS.items():
        got = n.get(k, 0)
        if a.every != 1:
            print('NOTE: population %s: %d (floor %d NOT applied: --every %d is a sample)'
                  % (k, got, floor, a.every))
            continue
        (ok if got >= floor else bad)('population %s: %d (floor %d)' % (k, got, floor))
    print('checks passed: %d' % passed[0])
    print('checks failed: %d' % len(failed))
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
