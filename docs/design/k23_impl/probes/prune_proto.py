#!/usr/bin/env python3
"""K23 prototype: MINIMUM-REMAINING-LENGTH (MRL) pruning, applied as a
mechanical patch to an ALREADY-EMITTED matcher.

This is a THROWAWAY PROTOTYPE in k18_memo_design.md's precedent: the design
lane does not touch src/. It exists to MEASURE the mechanism's effect on the
real emitted code, not to be the implementation. What it patches by pattern
match, the emitter would compute from the program graph (see k23_design.md
section 4).

WHAT IT DOES
------------
The emitter lowers `(BODY{m,M}){p,P}` as P replicas of the body. Replica k
(0-based) owns span-loop low-water slot `base+k` and emits:

    RX_SET(base+k, (ptrdiff_t)pos);
    { unsigned long it_ = 0; rx_cur = pos;
      while (rx_cur + W <= n && it_ < MUL && (...)) { rx_cur += W; it_++; } }

`rx_cur` is then the greedy furthest inner end, and the following label walks
it DOWN one stride per backtrack. Every one of those positions is a choice
point; the K23 explosion is the product of those choices across replicas.

MRL pruning clamps the cursor ONCE, at the scan, to the largest position from
which the rest of the pattern can still fit:

    rx_cur <= n - minrest(k)      where minrest(k) = max(0, p-(k+1)) * m * W

`minrest(k)` is the minimum number of subject bytes any ACCEPTING
continuation past replica k must still consume -- here, the outstanding
MANDATORY outer iterations times the inner minimum, plus the follow's own
minimum width (0 for this shape; --follow-min sets it). It is a LOWER bound,
so every position the clamp removes is one from which no continuation could
have succeeded: preference order among the SURVIVING positions is untouched,
and the first accepting path in preference order is therefore unchanged.

Usage:
  prune_proto.py IN.c OUT.c --outer-min p --inner-min m --stride W
                            [--slot-base B] [--follow-min F]
Prints the number of clamp sites patched to stderr; exits 1 if that is 0
(a silent no-op patch would report a free speedup, which is the check-design
failure mode this project keeps rediscovering).
"""
import argparse
import re
import sys

SCAN = re.compile(
    r'''    RX_SET\((?P<slot>\d+),\ \(ptrdiff_t\)pos\);\n
        \ {4}\{\n
        \ {8}unsigned\ long\ it_\ =\ 0;\n
        \ {8}rx_cur\ =\ pos;\n
        (?P<loop>\ {8}while\ \(.*?\)\ \{\ rx_cur\ \+=\ \d+;\ it_\+\+;\ \}\n)
        \ {4}\}\n''',
    re.VERBOSE)


def frames_mode(a):
    """The TEST form of the bound, at FRAMES-rung iteration entries.

    A choice-bearing body cannot take the cursor rung, so there is no range
    to clamp -- each iteration entry commits to ONE position and the bound is
    the plain test of section 4.1. The anchor is the `RX_SET(slot, pos)` that
    opens each iteration (a capture open, or the loop's own entry write);
    `--minrest-py` supplies the per-site constant, because at two levels of
    replication the site index encodes both loop counters and no single
    formula covers it (k23_design.md section 2.6).
    """
    text = open(a.src).read()
    anchor = '    RX_SET(%d, (ptrdiff_t)pos);\n' % a.frames_sites
    parts = text.split(anchor)
    nsites = len(parts) - 1
    if nsites == 0:
        print('prune_proto: no frames-rung entry sites at slot %d'
              % a.frames_sites, file=sys.stderr)
        sys.exit(1)
    if a.replicas is not None and nsites != a.replicas:
        print('prune_proto: DECLINED -- %d entry sites, expected %d'
              % (nsites, a.replicas), file=sys.stderr)
        sys.exit(2)
    out = [parts[0]]
    n_patched = 0
    for k, seg in enumerate(parts[1:]):
        minrest = int(eval(a.minrest_py,  # noqa: S307 - a lane probe
                           {'__builtins__': {'max': max, 'min': min}},
                           {'k': k, 'nsites': nsites})) + a.follow_min
        if a.placebo:
            minrest = 0
        if minrest > 0:
            out.append(
                '    if (n < %dUL || n - %dUL < pos) goto rx_fail;\n'
                % (minrest, minrest))
            n_patched += 1
        out.append(anchor)
        out.append(seg)
    open(a.dst, 'w').write(''.join(out))
    print('prune_proto: %d frames entry sites, %d tests inserted'
          % (nsites, n_patched), file=sys.stderr)
    if n_patched == 0:
        sys.exit(1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('dst')
    ap.add_argument('--outer-min', type=int, required=True)
    ap.add_argument('--inner-min', type=int, required=True)
    ap.add_argument('--stride', type=int, default=1)
    ap.add_argument('--slot-base', type=int, default=None,
                    help='stv slot of replica 0 (default: lowest slot seen)')
    ap.add_argument('--follow-min', type=int, default=0,
                    help='minimum bytes the pattern AFTER the outer loop must '
                         'consume (0 when the loop ends the pattern)')
    ap.add_argument('--replicas', type=int, default=None,
                    help='ASSUMPTION GUARD. The number of scan sites this '
                         'prototype expects to find, i.e. the outer '
                         'quantifier\'s maximum count when the outer is on '
                         'the REPLICATED (frames) rung and each replica owns '
                         'one inner cursor. Refuses if the count differs. '
                         'Without this guard the prototype silently '
                         'mis-patches any shape whose OUTER quantifier took '
                         'the cursor rung itself -- a possessified exact-count '
                         'inner does exactly that, one scan site and zero '
                         'replicas, and the per-replica minrest formula is '
                         'then simply the wrong arithmetic. See '
                         'k23_design.md section 11.1.')
    ap.add_argument('--minrest-py', default=None,
                    help='Override the two-level formula with a python '
                         'expression in `k` (the 0-based scan-site index) and '
                         '`nsites`. For nesting deeper than two levels the '
                         'per-site minrest is still pure compile-time '
                         'arithmetic, but it is no longer one formula -- see '
                         'k23_design.md section 4.3, where the emitter derives '
                         'it by threading an accumulator rather than by '
                         'indexing. Example, for ((a{2,4}){5,10}){5,20} with '
                         'site k = 10*i + j: '
                         '"max(0,5-(j+1))*2 + max(0,5-(i+1))*10" written out '
                         'with i,j derived from k.')
    ap.add_argument('--clamp-scan', action='store_true',
                    help='Fold the clamp into the greedy scan\'s OWN bound '
                         'instead of clamping after it. Same cut, but the '
                         'scan never walks past the feasible end, so it also '
                         'removes FORWARD work -- the quantity D49 gave its '
                         'own bound (RX_ERR_WORK), which the step counter '
                         'does not see.')
    ap.add_argument('--placebo', action='store_true',
                    help='THROUGHPUT CONTROL: emit the clamp at exactly the '
                         'same sites, same instruction shape, but with '
                         'minrest forced to 0 so it can never fire. The '
                         'difference between --placebo and the real clamp is '
                         'the clamp; the difference between --placebo and the '
                         'unpatched build is code layout. Without this control '
                         'the two are reported as one number.')
    ap.add_argument('--frames-sites', type=int, default=None, metavar='SLOT',
                    help='FRAMES-RUNG mode: patch the TEST form of the bound '
                         'at every `RX_SET(SLOT, pos)` iteration entry '
                         'instead of clamping cursor scans. Requires '
                         '--minrest-py.')
    a = ap.parse_args()

    if a.frames_sites is not None:
        if not a.minrest_py:
            print('prune_proto: --frames-sites requires --minrest-py',
                  file=sys.stderr)
            sys.exit(1)
        return frames_mode(a)

    text = open(a.src).read()
    hits = list(SCAN.finditer(text))
    if not hits:
        print('prune_proto: no span-loop scan sites found', file=sys.stderr)
        sys.exit(1)
    if a.replicas is not None and len(hits) != a.replicas:
        print('prune_proto: DECLINED -- %d scan sites, expected %d replicas; '
              'this is not the two-level replicated shape the prototype '
              'patches' % (len(hits), a.replicas), file=sys.stderr)
        sys.exit(2)
    base = a.slot_base if a.slot_base is not None else min(
        int(h.group('slot')) for h in hits)

    out, last, n_patched = [], 0, 0
    for h in hits:
        k = int(h.group('slot')) - base
        if k < 0:
            continue
        if a.minrest_py:
            minrest = int(eval(a.minrest_py,  # noqa: S307 - a lane probe
                               {'__builtins__': {'max': max, 'min': min}},
                               {'k': k, 'nsites': len(hits)})) + a.follow_min
        else:
            minrest = max(0, a.outer_min - (k + 1)) * a.inner_min * a.stride \
                + a.follow_min
        if minrest == 0:
            out.append(text[last:h.end()])
            last = h.end()
            continue                      # nothing to clamp against
        if a.placebo:
            minrest = 0
        if a.clamp_scan:
            # rewrite the scan block itself: bound the walk by the feasible
            # end rather than by the subject end
            blk = text[h.start():h.end()]
            new = blk.replace(
                '        unsigned long it_ = 0;\n',
                '        unsigned long it_ = 0;\n'
                '        const size_t cap_ = (n < %dUL) ? (size_t)0 : n - %dUL;\n'
                % (minrest, minrest))
            new = new.replace('while (rx_cur + ', 'while (rx_cur <= cap_ && rx_cur + ', 1)
            if new == blk:
                print('prune_proto: --clamp-scan did not land at slot %d'
                      % (k + base), file=sys.stderr)
                sys.exit(1)
            out.append(text[last:h.start()])
            out.append(new)
            out.append(
                '    if (n < %dUL) goto rx_fail;\n'
                '    if (rx_cur > n - %dUL) rx_cur = n - %dUL;\n'
                % (minrest, minrest, minrest))
            last = h.end()
        else:
            out.append(text[last:h.end()])
            last = h.end()
            out.append(
                '    /* MRL prune (K23 prototype): replica %d still owes %d bytes */\n'
                '    if (n < %dUL) goto rx_fail;\n'
                '    if (rx_cur > n - %dUL) rx_cur = n - %dUL;\n'
                % (k, minrest, minrest, minrest, minrest))
        n_patched += 1
    out.append(text[last:])
    open(a.dst, 'w').write(''.join(out))
    print('prune_proto: %d scan sites, %d clamps inserted (slot base %d)'
          % (len(hits), n_patched, base), file=sys.stderr)
    if n_patched == 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
