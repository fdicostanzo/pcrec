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
    ap.add_argument('--placebo', action='store_true',
                    help='THROUGHPUT CONTROL: emit the clamp at exactly the '
                         'same sites, same instruction shape, but with '
                         'minrest forced to 0 so it can never fire. The '
                         'difference between --placebo and the real clamp is '
                         'the clamp; the difference between --placebo and the '
                         'unpatched build is code layout. Without this control '
                         'the two are reported as one number.')
    a = ap.parse_args()

    text = open(a.src).read()
    hits = list(SCAN.finditer(text))
    if not hits:
        print('prune_proto: no span-loop scan sites found', file=sys.stderr)
        sys.exit(1)
    base = a.slot_base if a.slot_base is not None else min(
        int(h.group('slot')) for h in hits)

    out, last, n_patched = [], 0, 0
    for h in hits:
        k = int(h.group('slot')) - base
        if k < 0:
            continue
        minrest = max(0, a.outer_min - (k + 1)) * a.inner_min * a.stride \
            + a.follow_min
        out.append(text[last:h.end()])
        last = h.end()
        if minrest == 0:
            continue                      # nothing to clamp against
        if a.placebo:
            minrest = 0
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
