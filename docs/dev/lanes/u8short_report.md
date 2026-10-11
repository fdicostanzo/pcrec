# u8short — bench O-97 ask 1: utf8 search-short residue (2026-10-11, sonnet, compile-only)

One bounded read-only pass under the one-pass loss rule. No timing, no suite.
Pins built in the lane's own `build/` from `git archive`: 7388f1c0 (abi 73) = A,
b8337c33 (abi 74) = B, plus B with `-fno-start-landing -fno-start-width` = N.
Pattern texts from the bench's `bench/utf8/patterns/*.rx` (read-only); invocation
`-p rx -e utf8 [--no-captures] --emit-main` (asr-lb-neg adds `--features lookaround`);
`--emit-facts` also taken at A and B. The bench's exact flag line was not read.

## Findings common to all 12

- N is byte-identical to A except the abi/banner/include lines (6 lines) for all
  12 and both caps modes: the deny pair restores the reverse-pass code exactly,
  so every difference below is START-LANDING's and nothing else on the path.
- RX_DFA_START: 7 patterns A `reverse-pass` > B `landing`; 5 A `reverse-pass` > B
  `end-minus-width`. The forward scan (skip loop, byte classes, step loop) is
  byte-identical A vs B in all 12 except `landing_position` bookkeeping in the 7.
- `rx_search` object size (gcc -O2 -c): the 7 landing patterns grow 0x197 > 0x316
  bytes (qnt-lazy-2b 0x1ed > 0x352); `rx_decode` is inlined (0 calls in the
  object), so no call/frame term. Whole-object text still shrinks for 6 of 7
  (reverse tables gone).

## Per-pattern classification

| pattern | start form A > B | per-call change on the search path | class |
|---|---|---|---|
| prp-lu `\p{Lu}` | reverse-pass > landing | (a) | (a) |
| ci-neg-fold `(?i)[^é]` | reverse-pass > landing | (a) | (a) |
| cls-dot `.` | reverse-pass > landing | (a) | (a) |
| cls-neg-single `[^é]` | reverse-pass > landing | (a) | (a) |
| prp-greek `\p{Greek}` | reverse-pass > landing | (a) | (a) |
| alt-mixed-width `a\|é\|日\|😀` | reverse-pass > landing | (a) | (a) |
| qnt-lazy-2b `é+?` | reverse-pass > landing | (a) | (a) |
| asr-lb-neg `(?<!日)本` | reverse-pass > end-minus-width | none added; reverse loop removed | (c) |
| lit-offset-at-tail `é@` | reverse-pass > end-minus-width | none added; reverse loop removed | (c) |
| lit-offset-at-head `@é` | reverse-pass > end-minus-width | none added; reverse loop removed | (c) |
| floor `~` | reverse-pass > end-minus-width | none added; reverse loop removed | (c) |
| lit-1ch-2b `é` | reverse-pass > end-minus-width | none added; reverse loop removed | (c) |

Counts: (a) 7, (b) 0, (c) 5.

Evidence, (a): cls-dot diff adds `static inline rx_decode` (UTF-8 validate,
~20 lines, inlined), `size_t landing_position = search_from` at entry, one
store `landing_position = scan_position` inside the candidate-skip block (runs
when `forward_state == 0 && no accept yet`), and after the scan a
`__builtin_expect(!rx_decode(...), 0)` block (one decode at the landing, the
fix-up loop only on ill-formed). It removes the reverse loop (a table-walk per
reported match, bounded by match length). Per-call additions: one entry store,
one skip-block store, one decode per REPORTED match. The decode's multi-byte
branch (lead classify, continuation loop, floor/surrogate checks) is the cost on
the bench's non-ASCII subjects; there is no setup, frame, or walk term.

Evidence, (c): floor/lit-*/asr-lb-neg diff is purely subtractive: the post-scan
reverse block becomes `match_start = last_accept - W`; scan body and `.c.h`
tables are identical (only comment text differs). The B path executes strictly
fewer instructions than A, so a slowdown cannot be the code. `lit-offset-at-head`
and `lit-1ch-2b` carry the [U8-PICK] pick defect, but the pick is identical in A
and B (same scan text), so it explains absolute cost, not the A>B delta; it is
class (c) here. Not (b) for any cell.

## Why the per-match guard may be the whole story (inference, not measured)

The exec summary says +10..92 ns on 770-1,870 ns cells with 75-112 subjects per
pattern. If a cell is the pass over all subjects (not one call), the delta is
0.1-1.2 ns per subject, which is exactly slbuild's measured guard cost (0.13,
0.4, 1.2 ns per match). The summary's "one to two orders larger" rests on
reading the cell as a single call. The five (c) cells (+1.8..5.2%) would then be
layout/alignment noise at the 0.1-1 ns scale on a memchr-floor cell, consistent
with their code strictly shrinking.

## Disposition: ACCEPT, contingent on one bench-only answer

Accept as the guard's priced cost (per reported match, multi-byte decode on
non-ASCII subjects) plus layout noise. No code change proposed: the guard buys
the ill-formed-utf8 exactness (checked against libpcre2 10.46) and a landing
start that removes the reverse pass; the same utf8 set shows 67 better vs 10
worse (end-minus-width) and 69 vs 14 (landing). A cheap fix exists if the bench
answer says per-call and not per-subject: none is named, since there is no
per-call term in the code to remove. If the bench answer says per-call, the
residue is unexplained by code and the N arm (below) is the only attribution.

Relay questions (bench-only):
1. Is a "search-short" cell the sum/mean over the 75-112 subjects of one pattern
   (then the delta is per subject, 0.1-1.2 ns, the guard), or one call?
2. Only if (1) reads per-call: a `-fno-start-landing -fno-start-width` arm of
   b8337c33 on these 12, search-short only.

## Hand twin (not timed, not built into the tree)

Guard-deleted copy of cls-dot at B (drops the post-scan decode block; the
reverse loop stays removed, so spans can differ only on ill-formed subjects):

    build/pcrec -p rx -e utf8 --emit-main -o cls-dot.B.c --pattern '.'
    # delete from "    {\n        unsigned landing_cp;" up to (not including)
    # "    if (capture_spans) { capture_spans[0][0] = (ptrdiff_t)landing_position"
    gcc -O2 -c -I. -o twin.o cls-dot.twin-noguard.c    # compiles; rx_search 0x10f bytes

Timing arms if ever wanted: default vs N vs this twin over the bench's utf8
short subjects (slbuild's harness). I did NOT time it (box under a heavy chain).
Scratch artifacts: `worktrees/u8short/build/out/` (gitignored, not committed).
