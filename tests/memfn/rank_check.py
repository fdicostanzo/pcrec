#!/usr/bin/env python3
"""tests/memfn/rank_check.py -- [MEMFN] RQ-2's check (D157; memfn.h's
`mf_pred.rank_n`/`rank_pos`/`rank_ppm`). Driven by tests/memfn/run_rank.sh,
which builds the PROBE compiler (`-DPCREC_RANK_PROBE`: src/gen/memfn_sites.c
prints one `RANK` line per predicate of every PRE/OFS site it hands the kit,
with the ranking that predicate carries).

THE CLAIM. A predicate whose plan_hint names a RUN term carries a ranking of
EVERY position of that term (rank_n == the run length), ordered by the
position's rate, lowest first, ties to the higher offset, each with its rate
in ppm summed over the position's members, under the compile's byte-rate (or
the uniform rate where the compile has none). Every other predicate carries
rank_n 0. On the PRE site the scanned position (plan_pos) is rank_pos[0]. The
brute force shares no code with pcrec: it enumerates each cube's members
itself and reads the rate from the `--list-analysis default` listing (NONE
wherever the listing's resolution row has no digest, `-e utf8` today).

NON-VACUITY (K35): floors on the run predicates seen, per site (PRE, OFS),
per encoding, on masked runs, on rankings the rate moves off the positional
order (a positional ranking is red there), on data ties broken by the rule
(a leftmost tie is red there), and on the rank_n-0 predicates.

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
# Floors, measured at the landing (rq2_report.md, the figure in each comment)
# and set ~10% below it: a FLOOR, never an equality pin.
FLOORS = {
    'run-PRE': 1000,       # the pre-check composite's window / whole runs (1,111)
    'run-OFS': 120,        # the offset-skip block's pinned run (137)
    'run-byte': 800,       # a real byte-rate decides, byte and vm arms (879)
    'run-utf8': 330,       # NONE decides (U8-PICK: cube size, then positional) (369)
    'masked': 120,         # a cube position with two members (142)
    'prior-not-positional': 590,  # the ranking is not [n-1, ..., 0] (653)
    'data-tie': 225,       # >= 2 positions share a mass under a real rate (252)
    'norun': 4000,         # predicates that must carry rank_n 0 (4,643)
}


def load_rate(pcrec):
    """{encoding: [256 ppm] or None} from the listing's own sections."""
    rc, out, _ = es.run([pcrec, '--list-analysis', 'default'], 60)
    if rc != 0:
        raise SystemExit('rank_check: --list-analysis default failed')
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


def brute_rank(rate, run, mask):
    """[(pos, mass)] rarest first, ties to the rightmost."""
    cost = [(cube_cost(rate, run[i], mask[i]), -i) for i in range(len(run))]
    return [(-ni, c) for c, ni in sorted(cost)]


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

    rates = load_rate(a.probe)
    if 'byte' not in rates or 'utf8' not in rates:
        bad('the listing has no byte-rate resolution row for byte and utf8')
    corpus = es.enumerate_corpus(a.probe, TREE, 30)
    pats = sorted({p for _, _, p in corpus})
    pats = [p for i, p in enumerate(pats) if i % a.every == 0] + NAMED
    print('== RQ-2 rank check: %d distinct patterns, %d arms ==' % (len(pats), len(ARMS)))

    def one(job):
        pat, arm, argv = job
        cmd = [a.probe, '-p', 'rx', '--features', 'all'] + argv + ['-o', '-'] \
            + es._pattern_argv(a.probe, pat)
        rc, _, err = es.run(cmd, a.timeout)
        return pat, arm, rc, parse(err)

    jobs = [(p, arm, argv) for p in pats for arm, argv in ARMS]
    n = {k: 0 for k in FLOORS}
    n['ofs-ka-rank0'] = 0
    longest = {}
    wrong, ka_wrong, norun_wrong = [], [], []
    with concurrent.futures.ThreadPoolExecutor(a.jobs) as ex:
        for pat, arm, rc, recs in ex.map(one, jobs):
            enc = 'utf8' if arm == 'utf8' else 'byte'
            rate = rates.get(enc)
            for site, run, mask, ka, rn, pos, mass in recs:
                if run is None:
                    n['norun'] += 1
                    if rn != 0:
                        norun_wrong.append((pat, arm, site, rn))
                    continue
                want = brute_rank(rate, run, mask)
                longest[site] = max(longest.get(site, 0), len(run))
                n['run-' + site] = n.get('run-' + site, 0) + 1
                n['run-' + enc] += 1
                n['masked'] += any(m != 0xFF for m in mask)
                n['prior-not-positional'] += [p for p, _ in want] != \
                    sorted(range(len(run)), reverse=True)
                n['data-tie'] += rate is not None and \
                    len({c for _, c in want}) < len(want)
                if rn != len(run) or list(zip(pos, mass)) != want:
                    wrong.append((pat, arm, site, run.hex() + '/' + mask.hex(),
                                  (rn, pos), [p for p, _ in want]))
                if site == 'PRE' and pos[:1] != [ka]:
                    ka_wrong.append((pat, arm, run.hex(), ka, pos[:1]))
                if site == 'OFS':
                    n['ofs-ka-rank0'] += pos[:1] == [ka]
    for w in wrong[:20]:
        print('  %r [%s] %s %s: carries %s, brute force %s' % w)
    if wrong:
        bad('%d run rankings differ from the brute force' % len(wrong))
    else:
        ok('every run ranking (rank_n, positions, rates) equals the brute force '
           '(%d runs)' % (n['run-byte'] + n['run-utf8']))
    for w in norun_wrong[:20]:
        print('  %r [%s] %s: rank_n %d on a predicate with no RUN term' % w)
    if norun_wrong:
        bad('%d predicates without a RUN term carry a ranking' % len(norun_wrong))
    else:
        ok('every predicate without a RUN term carries rank_n 0 (%d)' % n['norun'])
    for w in ka_wrong[:20]:
        print('  %r [%s] %s: scanned %r, rank_pos[0] %r' % w)
    if ka_wrong:
        bad('%d PRE predicates scan a position other than rank_pos[0]' % len(ka_wrong))
    else:
        ok('every PRE predicate scans rank_pos[0] (%d)' % n.get('run-PRE', 0))
    print('NOTE: OFS predicates scanning rank_pos[0]: %d of %d (not asserted: '
          'the OFS scan member is the offset selection\'s, not the run reader\'s)'
          % (n['ofs-ka-rank0'], n.get('run-OFS', 0)))
    print('NOTE: longest run term per site: %s (MF_RANK_MAX 32)'
          % ', '.join('%s %d' % kv for kv in sorted(longest.items())))
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
