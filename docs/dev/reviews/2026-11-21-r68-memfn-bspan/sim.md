# CRITIC SIM: memfn-bspan

## Findings


### SIM-1 (CONFIRMED, doc/answer-of-record) §0.1 / §17 "routed to V" counts are wrong under the subject's own rule
Subject rule (§3 T-vwin/T-vscan: frame E-find AND pick HORS 16<=k<=1000, or pick WALK 24<=k<=64) vs census route() (kind = "has rxa_mfN_sh[" else "scan"; k only; no frame, no pick).
Repro (kit/site.py, build tree, `--features all`, span-head=0): corpus row tests/counterk/counterk.rxt:1919 `(?:ab|ba|aa|bb){24}c`
at `--window-search-width=4095`: wfE=E-find, fd=D1 (finder.c: D1 -> FF_LIBC, renderer B-memchr), loop k=48. Not WALK -> T-vscan does not hold ->
T-head H(64). The §0.1 corpus "1 routed (scan k=48)" is a LIBC site: under the subject's rule the corpus routes 0, not 1.
At the DEFAULT width 32 the same pattern is not an E-find site at all (fd P3 then none; no wfE, no span loop): so no k=48 exists at w32.
Consequence for §17: "the 4 are all the default build can show" is false twice: (1) counterk is LIBC so not V under the rule, (2) its k=48 does not
exist at w32 (k<=31 there). Under the subject's rule at the default width the census population shows 3 sites in 3 patterns (bench hex32 HORS k=31,
loglines hex32-id HORS k=31, dig-exact-32 WALK(R7w) k=31), at 4095 the same 3. Total routed = 3 of 6766 pairs, not 4.
The census has a second blind spot in the other direction? candidates checked: every census row with window k>=16 or scan k>=24 (counterk 48 [LIBC], d27_large_counts `[ab]{1000}` k=999 [fd PAIR, scan, k>64 anyway]); no census-"scan" WALK row with 24<=k<=64 exists, no census-"window" non-HORS row exists.
Severity: doc (information-only count per D201 add.1 so does not gate the build). Effort: edit 3 sentences + census script route() to take the fd row. Blast radius: §0.1, §17, spancensus2 report's TOP LINES.
Minimum witness: 1 pattern (counterk 1919) x 2 widths.

### SIM-2 (CONFIRMED, doc) §11 non-mover example `a[0-9a-f]{20}` is not a LIBC/PAIR find and has no span at all
§11 lists "LIBC/PAIR finds (`a[0-9a-f]{20}`)" as not moving. Repro (kit/site.py, w32/w4095 x simd off/x86-64-v3, 4 compiles): wfE=E-stmt, fd=none, 0 span loops
at head 0. It holds (H64, nothing moves) but for the wrong reason: no E-find site, no stretch. A real LIBC E-find witness with an eligible-length stretch is
`[0-9]{30}x` (w4095: E-find, fd D1 -> LIBC, loop k=30 -> T-head) and `[0-9a-f]{30}-[0-9a-f]{20}` style D1 sites (k=10 / k=20); a PAIR witness `[ab]{30}[cd]`
was not needed. The T-vscan WALK-only row (§3.3) does what §11 promises on those. Severity doc; effort one example swap. Minimum witness 1 pattern.

### SIM-3 (CONFIRMED, doc/design) §8 card C6's bound cells and §0.1's four patterns do not exist at the default width, and the card names no width
§8 times window k in {15,16,31,32,1000,1001}, scan k in {23,24,64,65}, "the four routed census patterns", canonical formhash instance `[0-9a-f]{41}`, with no
window width stated. Measured (210-cell sweep, simd off, hex/\w/[^\n] HORS, digit/[A-Z] WALK): k = repeat count - 1 in every cell (so `{N}` gives k=N-1;
cell k=16 is `{17}`, k=15 is `{16}`); at width 32 an N>=33 pattern is E-stmt R7w with NO span loop (k 32, 1000, 1001 window cells and 64, 65 scan cells do not exist);
at 4095 they all exist and route as §11 says (HORS k 16..1000 V, k=1001 H64; WALK k 24..64 V, k=65 H64; digit/[A-Z] {66} k=65 H64; {1000} k=999 H64).
`[0-9a-f]{41}` at width 32 = E-stmt, no span, so its formhash entry would hash NO V text unless the formhash/card compile passes `--window-search-width`
>= 42 (42, 64, 4095 each give E-find D-hors k=40 V; width 41 not probed). Also the card's "four routed patterns": under the subject's rule only 3 route
(SIM-1), and counterk's k=48 cell needs width >= 49 and is LIBC (H64), so it is not a V cell at any width.
Severity design (the card would time H64 against H64 at the default width on half its cells, reading as "no LOSS"). Effort: state the width (4095 for k>31) in §8/§14.
Blast radius: C6, formhash entry. Reached: k 15..1001 window, 23..65 scan, widths 32, 33, 42, 64, 1001..1003, 4095.

### SIM-4 (CONFIRMED, doc) §11 has no encoding column; under `-e utf8` the HORS/WALK split moves, so the mover set changes
Repro: `[0-9a-f]{20}` w4095 simd off: byte = D-hors k=19 V(win); `-e utf8` = fd R7w (WALK) k=19 -> T-vscan needs 24 -> NOT V. `[0-9]{30}` stays WALK either way.
So under utf8 the hex family moves only for {25}..{32} (WALK k 24..31), not {17}..{24}. (`-i` and `--ucp` (byte) do not change the pick on `[a-f]{20}`,
`\w{20}`, `[0-9]{30}`; `-e utf8 --ucp \w{20}` is refused as too large.) The routing rule reads fd, so it is right; §11's table (and G-4's "equals §11's mover classes, counted")
states the byte-encoding set only. Severity doc; the census found no utf8 pattern with k>=16 so the population is unaffected. Effort one column/row.
Minimum witness 2 compiles.

## PROBED-AND-HELD
(about 335 pcrec compiles of the 400 cap; my rule from the text is in sim/rule_from_text.md, written before route() was read; driver sim/drv.py; raw cells sim/sweep.tsv, s11.tsv, w.tsv, c41.tsv)
- §11 mover examples `[0-9a-f]{16,17}`, `[0-9]{24,25}`, `\w{17}`, `\w{32}`, `[^\n]{17}`, `[A-Z]{25}` x {w32, w4095} x {simd off, v3}: 24 cells, all route as §11 says (k 15 / 23 H64; 16 / 24 V).
- Sweep: 5 classes x 15 repeat counts (16,17,18,24,25,26,32,33,34,64,65,66,1000,1001,1002) x {w32, w4095} at simd off = 150 cells, plus hex and digit at v3 = 60 cells: routing (frame, fd, k, V/H) is IDENTICAL between simd off and v3 on all 60 pairs (layer-independent, as §3 says).
- §3.1: k = repeat count - 1 on all 210 cells; bounds 16/24 lower and 1000/64 upper hold exactly; HORS classes = hex, \w, [^\n]; WALK classes = [0-9], [A-Z].
- §3.2 "k<=31 at the default width": n>=33 at w32 is E-stmt with no loop (all 5 classes); window width W: site exists iff n<=W, so k<=W-1 (W=33,64,1001,1002 probed, 8 cells). At w32 a second eligible stretch cannot fit (2x16+probe > 32); at 4095 `[0-9a-f]{20}[g-z]{20}` holds two eligible stretches (k=20, 19) so the first-only rule does decide there.
- §3.2 byte identity of `[0-9a-f]{17}`, `[0-9]{25}`, `[0-9a-f]{32}`, `[0-9]{32}` at w32 vs w4095 (simd off): identical but the include filename; `{33}` differs (146 lines): holds.
- §3.3 WALK-only: LIBC (D1) witnesses `[0-9]{30}x`, `(?:ab|ba|aa|bb){24}c` and PAIR `[ab]{1000}` are E-find with long stretches and stay H64 under the rule (as promised); `[ab]{1000}` at w32 is E-stmt.
- First-match order: `--memfn=no-span-loop` gives no loops (I) on k=19/29 stretches; `--memfn=span-loop` gives loop from offset 0 (L); `--harness=span-head=N` (0, 8, 20, 64) gives a loop from N, none when N>=k (H(N)); all three precede V in the table, so under any of them V can never render, which is what §3 says; text §11 promises nothing more for them. `--memfn=no-span-vector` does not exist (cannot probe).
- Population (a): rows with any span site in the committed census (19 corpus, 11 bench rows) were scanned for k>=15 window / k>=23 scan: only counterk 1919, d27_large_counts, hex32, hex32-id, dig-exact-32 (and dig-exact-16 k=15, not eligible); recompiled at w4095 and w32 with each pattern's own options (counterk with no --features): bench 3 route, corpus 0 (SIM-1). NOT swept: whether a w32-only site exists that w4095 lacks (a full-corpus job).
- census route() vs the subject text: only difference is that route() has no frame or pick (kind = has `_sh[`); all other conditions (16..1000 window, 24..64 scan) match the subject's rows.
CRITIC COMPLETE
