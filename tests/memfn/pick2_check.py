#!/usr/bin/env python3
"""tests/memfn/pick2_check.py -- [MEMFN] RQ-2's check (integration.md
§R4.9.11 RQ-2, Q-R9-3 RULED (a); docs/spec/match_api.md §6.3's
`mf_pred.plan_pos2` note). Driven by tests/memfn/run_pick2.sh, which builds
the PROBE compiler (`-DPCREC_PICK2_PROBE`: src/gen/memfn_sites.c prints one
`PICK2` line per predicate of every PRE/OFS site it hands the kit).

THE CLAIM. Every predicate whose plan_hint names a RUN term carries
`plan_pos2` = KB, the BRUTE-FORCE argmin over the run's other positions of
the position's cube mass under the compile's byte-rate, ties to the
rightmost position (the NONE answer: every position's uniform mass, the
cube's member count). KB != KA (the distance rule). Every other predicate
carries MF_NO_POS (65535). The brute force shares no code with pcrec: it
enumerates each cube's members itself and reads the rate from the
`--list-analysis default` listing (the byte-rate is NONE wherever the
listing's resolution row has no digest, `-e utf8` today).

NON-VACUITY (K35): floors on the run predicates seen, per site (PRE, OFS),
per encoding, on masked runs, on predicates where the prior's pick differs
from the positional rightmost (a positional pick2 is red there), and on
data ties broken by the rule (a leftmost tie is red there).

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

NO_POS = 0xFFFF
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
# Floors, measured at the landing (rq2_report.md, the figure in each comment)
# and set ~10% below it: a FLOOR, never an equality pin.
FLOORS = {
    'run-PRE': 1000,       # the pre-check composite's window / whole runs (1,111)
    'run-OFS': 120,        # the offset-skip block's pinned run (137)
    'run-byte': 800,       # a real byte-rate decides, byte and vm arms (879)
    'run-utf8': 330,       # NONE decides (U8-PICK: positional) (369)
    'masked': 120,         # a cube position with two members (142)
    'prior-not-rightmost': 320,  # the prior's KB is not the rightmost other (365)
    'data-tie': 100,       # >= 2 positions share the minimum under a real rate (128)
    'norun': 4000,         # predicates that must carry MF_NO_POS (4,643)
}


def load_rate(pcrec):
    """{encoding: [256 ppm] or None} from the listing's own sections."""
    rc, out, _ = es.run([pcrec, '--list-analysis', 'default'], 60)
    if rc != 0:
        raise SystemExit('pick2_check: --list-analysis default failed')
    sec, have, ppm = None, {}, [0] * 256
    for ln in out.decode().splitlines():
        if ln.startswith('#section '):
            sec = ln.split()[1]
            continue
        if not ln or ln.startswith('#'):
            continue
        f = ln.split('\t')
        if sec == 'resolution' and f[0] == 'byte-rate':
            have[f[1]] = f[6] not in ('', 'none')
        elif sec == 'freq':
            ppm[int(f[0], 16)] = int(f[2])
    return {enc: (ppm if ok else None) for enc, ok in have.items()}


def cube_cost(rate, b, m):
    members = [x for x in range(256) if (x & m) == b]
    if rate is None:
        return len(members) * 1000000 // 256
    return sum(rate[x] for x in members)


def brute_kb(rate, run, mask, ka):
    """(KB, whether >= 2 positions tie at the minimum, rightmost other)."""
    others = [i for i in range(len(run)) if i != ka]
    if not others:
        return NO_POS, False, NO_POS
    cost = {i: cube_cost(rate, run[i], mask[i]) for i in others}
    lo = min(cost.values())
    best = [i for i in others if cost[i] == lo]
    return max(best), len(best) > 1, max(others)


def parse(stderr):
    recs = []
    for ln in stderr.decode('utf-8', 'replace').splitlines():
        if not ln.startswith('PICK2\t'):
            continue
        _, site, idx, kind, run, mask, ka, kb = ln.split('\t')
        recs.append((site, kind, run, mask, ka, int(kb)))
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

    rates = load_rate(a.probe)
    if 'byte' not in rates or 'utf8' not in rates:
        bad('the listing has no byte-rate resolution row for byte and utf8')
    corpus = es.enumerate_corpus(a.probe, TREE, 30)
    pats = sorted({p for _, _, p in corpus})
    pats = [p for i, p in enumerate(pats) if i % a.every == 0] + NAMED
    print('== RQ-2 pick2 check: %d distinct patterns, %d arms ==' % (len(pats), len(ARMS)))

    def one(job):
        pat, arm, argv = job
        cmd = [a.probe, '-p', 'rx', '--features', 'all'] + argv + ['-o', '-'] \
            + es._pattern_argv(a.probe, pat)
        rc, _, err = es.run(cmd, a.timeout)
        return pat, arm, rc, parse(err)

    jobs = [(p, arm, argv) for p in pats for arm, argv in ARMS]
    n = {k: 0 for k in FLOORS}
    wrong = []
    with concurrent.futures.ThreadPoolExecutor(a.jobs) as ex:
        for pat, arm, rc, recs in ex.map(one, jobs):
            enc = 'utf8' if arm == 'utf8' else 'byte'
            rate = rates.get(enc)
            for site, kind, run, mask, ka, kb in recs:
                if kind != 'run':
                    n['norun'] += 1
                    if kb != NO_POS:
                        wrong.append((pat, arm, site, 'norun', kb, NO_POS))
                    continue
                rb, mb, ka = bytes.fromhex(run), bytes.fromhex(mask), int(ka)
                want, tie, right = brute_kb(rate, rb, mb, ka)
                n['run-' + site] = n.get('run-' + site, 0) + 1
                n['run-' + enc] += 1
                n['masked'] += any(m != 0xFF for m in mb)
                n['prior-not-rightmost'] += want != right
                n['data-tie'] += tie and rate is not None
                if kb != want or (kb != NO_POS and kb == ka):
                    wrong.append((pat, arm, site, run + '/' + mask + ' ka=%d' % ka, kb, want))
    for w in wrong[:20]:
        print('  %r [%s] %s %s: plan_pos2 %s, brute force %s' % w)
    if wrong:
        bad('%d predicates carry a plan_pos2 the brute force does not derive' % len(wrong))
    else:
        ok('every predicate\'s plan_pos2 equals the brute force (%d run, %d other)'
           % (n['run-byte'] + n['run-utf8'], n['norun']))
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
