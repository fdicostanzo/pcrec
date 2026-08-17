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
    ap.add_argument('--no-lattice', action='store_true',
                    help='SABOTAGE CONTROL: emit the clamp WITHOUT rounding '
                         'onto the iteration lattice, i.e. this note\'s '
                         'pre-R26 form. Exists so the stride/residue corpus '
                         'can be validated in the failing direction -- a '
                         'corpus that does not go red under this flag is not '
                         'testing the lattice rule. Never a candidate.')
    ap.add_argument('--prefilter-ceiling', action='store_true',
                    help='R26 E4 PROTOTYPE: use the DFA prefilter\'s MATCH-END '
                         'window as the clamp ceiling instead of the subject '
                         'end. rx_search already computes win[0][1] and drops '
                         'it on the next line; this plumbs it through a '
                         'file-scope variable, which is a PROTOTYPE shortcut '
                         '(TS-1 forbids mutable globals in generated code, so '
                         'a real version carries it in rx_work). Closes the '
                         'trailing-suffix residual -- not a curiosity: K23 '
                         'RETURNS at a 16-byte suffix.')
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
        # THE LATTICE RULE (R26 E1). A stride-W span loop admits ONLY the
        # positions pos, pos+W, pos+2W, ...  Clamping to the raw
        # `ceiling - minrest` lands the cursor OFF that lattice whenever the
        # gap is not a multiple of W, and an off-lattice cursor poisons the
        # whole retreat chain: the retreat walks down by W from a position
        # that was never an iteration boundary, so the CORRECT cursor value is
        # DELETED from the choice set. That is not pruning, it is
        # substitution, and it violates soundness step 3 ("never introduces a
        # candidate that was not there") in the introducing direction.
        # Measured before the fix on ((?:ab){10,20}){10,50}: 5 of 8 subjects
        # answered nomatch where baseline and python matched.
        # The repair rounds DOWN onto the lattice:
        #     cap = pos + W * floor((ceiling - minrest - pos) / W)
        # `pos` is the iteration start, which the scan block has in hand (it
        # is what the low-water slot was just set to). A ceiling below `pos`
        # means the whole continuation is infeasible and the replica fails.
        W = 1 if a.no_lattice else a.stride
        ceil_ = 'rx_ceil_' if a.prefilter_ceiling else 'n'
        clampblk = (
            '    /* MRL prune (K23 prototype): replica %d still owes %d bytes,\n'
            '     * rounded onto the stride-%d iteration lattice (R26 E1). */\n'
            '    if (%s < %dUL || %s - %dUL < pos) goto rx_fail;\n'
            '    { const size_t cap_ = pos + %dUL * ((%s - %dUL - pos) / %dUL);\n'
            '      if (rx_cur > cap_) rx_cur = cap_; }\n'
            % (k, minrest, W, ceil_, minrest, ceil_, minrest,
               W, ceil_, minrest, W))
        if a.clamp_scan:
            # Same cap, computed BEFORE the greedy walk and used as its bound,
            # so the scan never steps past the feasible end either -- the half
            # the step counter cannot see (D49's territory).
            blk = text[h.start():h.end()]
            new = blk.replace(
                '        unsigned long it_ = 0;\n',
                '        unsigned long it_ = 0;\n'
                '        const size_t cap_ = (%s < %dUL || %s - %dUL < pos)\n'
                '            ? pos : pos + %dUL * ((%s - %dUL - pos) / %dUL);\n'
                % (ceil_, minrest, ceil_, minrest, W, ceil_, minrest, W))
            new = new.replace('while (rx_cur + ',
                              'while (rx_cur < cap_ && rx_cur + ', 1)
            if new == blk:
                print('prune_proto: --clamp-scan did not land at slot %d'
                      % (k + base), file=sys.stderr)
                sys.exit(1)
            out.append(text[last:h.start()])
            out.append(new)
            out.append(clampblk)
            last = h.end()
        else:
            out.append(text[last:h.end()])
            last = h.end()
            out.append(clampblk)
        n_patched += 1
    out.append(text[last:])
    text = ''.join(out)
    if a.prefilter_ceiling:
        text = plumb_ceiling(text)
    open(a.dst, 'w').write(text)
    print('prune_proto: %d scan sites, %d clamps inserted (slot base %d)%s'
          % (len(hits), n_patched, base,
             ', prefilter ceiling' if a.prefilter_ceiling else ''),
          file=sys.stderr)
    if n_patched == 0:
        sys.exit(1)


def plumb_ceiling(text):
    """Make the prefilter's match-END window visible to the clamp.

    `rx_search` computes `win[0][1]` and uses only `win[0][0]` on the very
    next line -- the tight ceiling the clamp wants already exists at runtime
    and is discarded. This carries it in a file-scope variable, which a real
    implementation may NOT do (TS-1: no mutable globals in generated code);
    there it belongs in `rx_work`, which every entry already threads. The
    entries that run no prefilter (`rx_match`) default it to the subject end,
    so the clamp degrades to the plain form rather than reading a stale value.
    """
    anchor = 'static ptrdiff_t rx_match_impl'
    if anchor not in text:
        print('prune_proto: impl anchor not found', file=sys.stderr)
        sys.exit(1)
    text = text.replace(
        anchor,
        "/* R26 E4 prototype: the prefilter's match-end window, which\n"
        " * rx_search computes and then discards. File-scope ONLY because\n"
        " * this is a patch on emitted C -- see plumb_ceiling()'s docstring. */\n"
        'static size_t rx_ceil_;\n\n' + anchor, 1)
    text = text.replace(
        '        start = (size_t)win[0][0];\n',
        '        start = (size_t)win[0][0];\n'
        '        rx_ceil_ = (size_t)win[0][1];\n', 1)
    text = text.replace(
        'ptrdiff_t rx_match(const rx_ctx *ctx)\n{\n',
        'ptrdiff_t rx_match(const rx_ctx *ctx)\n{\n'
        '    rx_ceil_ = ctx->len;\n', 1)
    for needle in ('rx_ceil_ = (size_t)win[0][1];',
                   'rx_ceil_ = ctx->len;',
                   'static size_t rx_ceil_;'):
        if text.count(needle) != 1:
            print('prune_proto: --prefilter-ceiling plumbing did not land: %s'
                  % needle, file=sys.stderr)
            sys.exit(1)
    return text


if __name__ == '__main__':
    main()
