#!/usr/bin/env python3
# docs/dev/lanes/r17b_movers.py (lane r17b, [MEMFN] R17-b): THE MOVER CENSUS
# for abi 76 -> 77, a pcrec-side reader over EMITTED C, never the kit's
# `moved` (setfind.md rev 2.3 §11.2, §16.2).
#
# Every distinct corpus pattern (emit_sweep's own enumeration) is compiled by
# a REFERENCE pcrec (the kit branch before R17-b) and by the tree's, under
# --features all, on each arm, and by the tree's again under the arm plus
# `--memfn=no-pf-terms-mask`. With the abi digit normalized on the lines that
# name the abi:
#   - the DENY artifact must equal the reference on EVERY pattern (the deny
#     is today's walk, byte for byte);
#   - the PREDICTION is read off the reference artifact alone: it holds a
#     table walk `while (X[ + 1] < subject_length && !rx_T[subject[X]]) X++;`
#     over T in {can_begin_match, start_bytes, start_set}, whose table (read
#     from the same artifact) has a cover of at most 4 terms (cubes and
#     modular arcs of width <= 128, of the set or of its complement), found by
#     THIS script's own search below (it shares no code with memfn/src/
#     terms.c: it is written from the definitions of setfind.md §3.1-§3.2);
#   - a predicted artifact must move, carry `__next_candidate(&`, the W8
#     sub-block and no walk or table for that T, or be identical to the
#     reference (`coverable-declined`: the kit's node budget, counted and
#     listed); every other artifact must be identical to the reference, so a
#     mover is ONLY ever at a predicted site.
# Prints the population, the movers per arm and per walk kind, and anything
# outside the rule (BAD-*). Exit 1 on any BAD.
#
# usage: python3 r17b_movers.py TREE REF_PCREC [JOBS] [--every N] [--arms a,b]
#                                [--arm NAME=FLAGS ...] [--list-movers FILE]
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

args = [a for i, a in enumerate(sys.argv[1:]) if not a.startswith('--')
        and (i == 0 or sys.argv[i] not in ('--every', '--arms', '--arm', '--list-movers'))]
opts = sys.argv[1:]
W, REF = args[0], args[1]
JOBS = int(args[2]) if len(args) > 2 else 4
EVERY = int(opts[opts.index('--every') + 1]) if '--every' in opts else 1
sys.path.insert(0, W + '/scripts')
import emit_sweep as es  # noqa: E402

NEW = W + '/build/pcrec'
ALL_ARMS = {'byte': [], 'byte-vm': ['--engine=vm'], 'utf8': ['-e', 'utf8'],
            'utf8-vm': ['-e', 'utf8', '--engine=vm'], 'simd': ['-fmemfn-simd']}
ARMS = [(k, ALL_ARMS[k]) for k in (opts[opts.index('--arms') + 1].split(',') if '--arms' in opts
                                    else list(ALL_ARMS))]
# --arm NAME=FLAGS (repeatable): an extra arm, FLAGS space-separated
for i, o in enumerate(opts):
    if o == '--arm' and i + 1 < len(opts):
        n, f = opts[i + 1].split('=', 1)
        ARMS.append((n, f.split()))
DENY = ['--memfn=no-pf-terms-mask']
ABI = re.compile(rb'(?i)abi')
WALK = re.compile(rb'while \((\w+)( \+ 1)? < subject_length && !rx_(can_begin_match|start_bytes|start_set)'
                  rb'\[subject\[\1\]\]\) \1\+\+;')
TABLE = re.compile(rb'static const unsigned char rx_(can_begin_match|start_bytes|start_set)\[256\] = \{([^}]*)\}')

# ---- the independent cover search (setfind.md §3.1-§3.2, from the definitions) ----
FULL = (1 << 256) - 1
CUBES = []
for m in range(256):
    for v in range(256):
        if v & ~m & 255:
            continue
        b = 0
        for x in range(256):
            if x & m == v:
                b |= 1 << x
        CUBES.append(b)
ARCS = []
for L in range(256):
    b = 0
    for w in range(1, 129):
        b |= 1 << ((L + w - 1) & 255)
        ARCS.append(b)
CANDS = CUBES + ARCS


def maximal(target):
    inside = sorted({c for c in CANDS if c & ~target == 0}, key=lambda c: -bin(c).count('1'))
    keep = []
    for c in inside:
        if not any(c & ~k == 0 and c != k for k in keep):
            keep.append(c)
    return keep


def covers(target, k):
    cands = maximal(target)

    def dfs(unc, d):
        if unc == 0:
            return True
        if d == 0:
            return False
        x = (unc & -unc).bit_length() - 1
        for c in cands:
            if c >> x & 1 and dfs(unc & ~c, d - 1):
                return True
        return False
    return dfs(target, k)


_cov = {}


def coverable(bits):
    if bits not in _cov:
        _cov[bits] = 0 < bin(bits).count('1') < 256 and (covers(bits, 4) or covers(FULL & ~bits, 4))
    return _cov[bits]


# ---- the census ---------------------------------------------------------------
def comp(b, p, extra):
    r = subprocess.run([b, '-p', 'rx', '--features', 'all'] + extra + ['-o', '-', '--pattern', p],
                       capture_output=True, timeout=120)
    return r.stdout if r.returncode == 0 else None


def norm(t):
    return b'\n'.join(re.sub(rb'\b76\b', b'77', l) if ABI.search(l) else l for l in t.split(b'\n'))


def table_bits(art, kind):
    for m in TABLE.finditer(art):
        if m.group(1) == kind:
            vals = [int(v) for v in m.group(2).replace(b'\n', b' ').split(b',') if v.strip()]
            return sum(1 << i for i, v in enumerate(vals) if v)
    return None


def task(item):
    p, (arm, extra) = item
    try:
        a, b, d = comp(REF, p, extra), comp(NEW, p, extra), comp(NEW, p, extra + DENY)
    except subprocess.TimeoutExpired:
        return (arm, p, 'timeout', '')
    if a is None or b is None or d is None:
        both = a is None and b is None and d is None
        return (arm, p, 'all-refuse' if both else 'BAD-refusal-moved', '')
    na = norm(a)
    if d != na:
        return (arm, p, 'BAD-deny-moved', '')
    walks = [(m.group(3).decode(), bool(m.group(2))) for m in WALK.finditer(a)]
    pred = []
    for kind, bounded in walks:
        bits = table_bits(a, kind.encode())
        if bits is None:
            return (arm, p, 'BAD-walk-without-table', kind)
        if coverable(bits):
            pred.append(kind + ('-bounded' if bounded else ''))
    moved = b != na
    if not pred:
        return (arm, p, 'identical' if not moved else 'BAD-unpredicted-mover',
                ','.join(k for k, _ in walks))
    if not moved:
        # coverable by this script's search, declined by the kit: the kit's
        # node BUDGET (memfn/src/kit.h MF_SET_BUDGET) is the one documented
        # reason a coverable set keeps the walk; counted and listed, a DECLINE
        # is never a wrong answer (setfind.md §3.5)
        return (arm, p, 'coverable-declined', ','.join(pred))
    if b'__next_candidate(&' not in b or b'#ifndef PCREC_MFK_W8_H' not in b:
        return (arm, p, 'BAD-mover-without-kit-form', ','.join(pred))
    for k in pred:
        kind = k.replace('-bounded', '')
        if re.search(rb'static const unsigned char rx_' + kind.encode() + rb'\[256\]', b):
            return (arm, p, 'BAD-mover-keeps-table', k)
    return (arm, p, 'mover', ','.join(pred))


def main():
    pats = es.distinct_patterns(es.enumerate_corpus(NEW, W, 30), every=EVERY)
    items = [((p[2] if isinstance(p, tuple) else p), arm) for p in pats for arm in ARMS]
    with ThreadPoolExecutor(JOBS) as ex:
        res = list(ex.map(task, items))
    tally, kinds, bads = {}, {}, 0
    for arm, p, v, k in res:
        tally.setdefault(arm, {}).setdefault(v, 0)
        tally[arm][v] += 1
        if v == 'mover':
            for kk in k.split(','):
                kinds.setdefault(arm, {}).setdefault(kk, 0)
                kinds[arm][kk] += 1
        if v == 'coverable-declined':
            print('%-8s %-28s %-24s %r' % (arm, v, k, p))
        if v.startswith('BAD') or v == 'timeout':
            bads += 1
            print('%-8s %-28s %-24s %r' % (arm, v, k, p))
    print('patterns', len(pats), 'every', EVERY)
    for arm, _ in ARMS:
        t = tally.get(arm, {})
        print('ARM %-8s ' % arm + ' '.join('%s=%d' % kv for kv in sorted(t.items())))
        print('    movers by walk: ' + ' '.join('%s=%d' % kv for kv in sorted(kinds.get(arm, {}).items())))
    print('distinct walk sets judged', len(_cov), 'coverable', sum(_cov.values()))
    print('BAD', bads)
    # ---- r17c: opt-in --list-movers FILE (absent: nothing here runs, output unchanged) ----
    # One `arm<TAB>verdict<TAB>repr(pattern)` line per `mover` / `coverable-declined`
    # result, in the order the results were produced (the same population and
    # verdicts the ARM lines above count), for slot25's c-stream judge to join.
    if '--list-movers' in opts:
        with open(opts[opts.index('--list-movers') + 1], 'w') as fh:
            for arm, p, v, k in res:
                if v in ('mover', 'coverable-declined'):
                    fh.write('%s\t%s\t%r\n' % (arm, v, p))
    # ---- end r17c ----
    return 1 if bads else 0


if __name__ == '__main__':
    sys.exit(main())
