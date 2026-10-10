# pcrec-bench wishlist — cells we want but have not asked for

Started 2026-10-08 by the manager at Frank's request ("the rest of stuff you
want to see in bench but we're too afraid to ask"). This is pcrec-side and
nothing here has been sent. When a bench set opens, or a pcrec decision
stalls for lack of a measurement, pull from this list deliberately and record
what was sent (inbox id) beside the entry. Source: lane capsurvey's sweep of
known_issues.md, plan.md, docs/dev/optloop/ and the design notes. "Oracle"
means whether libpcre2-differential can derive the expectation or the
capability@0.2 second verification method is needed.

Already SENT for capability@0.2 (I-136): the O-87 core (long matching and
long near-miss subjects for evil-alt-nested / trim-nested-star; the second
verification method), a mixed-run real-text subject (K81), an end-anchored
tail family on prose ([OPT-REVEND]), and `\b[0-9a-f]{8}\b` on capability
prose (K91 I3).

## HIGH — a pcrec decision is waiting

1. **[OPT-HYB-RESEED-XCALL] / [START-DENSE]: a density-controlled lookahead pair.**
   - Why: XCALL is HELD on "the bench's lka-pos cell decides" (xcall.md:50; O-81 item 2: no density-controlled lka pair exists).
   - Cell: `item(?= done)` plus its matched negative control over ~64 KB prose at 3 densities (1 per 8 KB, 1 word in 3, every word). Single-call and find-all regimes.
   - Oracle: differential. Home set: syntax.
   - lkb-neg ([ENG-LOOK]) could ride the same density axis.
2. **[START-DENSE] (K90 + K91 + RESEED-POLICY + K83): a start-byte density sweep.**
   - Cells: the existing `quoted-delim-match` and `(\w)\1` at controlled start-byte densities of 5, 12, 33 and 80%. Also short subjects whose first byte is a start byte (K90 L3), and aws with the start byte absent (K91 I5).
   - Oracle: differential. The disarm rule's design waits on it.

3a. **[OPT-REVEND] stage 2 (D156 add. 1 Q2, Frank: "it should be built. we can create some patterns for it") — capture-bearing end-anchored tails.**
   - Cells: `(\d+)$`, `(\w+)\.txt$`, `([a-z]+)\s*$`, `(\s*)\z`, plus a lazy tie shape `(\s+?){2}$`, over the existing t-tail-*-1m bodies and one 64 KiB body (size independence). Auto-caps config (the capture/VM route), matching and non-matching tails.
   - Also feeds [CAP-EARLY-STOP]: a capture with a long uncaptured tail, e.g. `(\w+)@[a-z.]+` on prose.
   - Oracle: differential. Home set: capability.

## MED

3. **CTX trio ([ART-HYB-COUNTED], I13, [ART-LAZY-FRAMELESS]): a hit-weighted ctx-* cell.**
   - Cell: ctx-lazy-64/256/1024 and ctx-greedy-256 over ~64 KB with at least one hit per 256 B. The current ctx subjects are hit-sparse.
   - Releases the round-3 HOLD (round3_selection A5). Oracle: differential. Home set: bounded.
4. **[ART-POSS-ARMS] arm B in isolation.**
   - Cell: `([a-z]+)-\1` or `(\w+) \1` with a non-word follow, over 4 KB repeated-token text, a near-miss, and non-repeated text.
   - Gives attribution for the arms (poss_arms.md's work-budget claim). Oracle: differential.
5. **Parked rows whose D77 trigger is "one bench cell".**
   - [OPT-5-PERIODK]: `(?:ab){10,100}` and `(?:abc){1000,2000}` on a non-periodic subject.
   - [ENG-ABS-CARET]: `(^a|b)c`-style partial-caret alternations.
   - [ENG-ISL-S2]: alternations of 8 or more branches with class tails at widths 64/256/1024.
   - Bench question: were parkmeas's A2-A4 I-notes ever sent or answered?

## LOW

6. **[OPT-ENDWIN-ENC]: `^.{5}$` under utf8.** Noise-scale per D144.
7. **[DEC-COLLAPSE-WASTE]: compile-attempt waste.** Needs per-pattern compile timing. Bench question: does the bench time compiles?
8. **K83: a clang testee arm.** Not a set addition. Bench question: is there a clang testee?

## Open bench-only questions (from capsurvey)

1. Were the parkmeas A2-A4 I-notes sent? What are the answers to A9 Q6-Q12?
2. Does any bench subject carry other start-byte densities (K90 L1's "match-dense JSON subject": which set and id)?
3. Does the bench time compiles per pattern?
4. Is there a clang testee?
5. Does 1 MiB `.*\.txt$` stay under the oracle's match limit? This bears on the I-136 tail family.
