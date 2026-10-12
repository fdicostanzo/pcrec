# b3cost — B3 (the match-end mark on rev-end) at the TAGGED reverse machine's size

Lane b3cost, 2026-10-12, main `a8850e084` (abi 76). Counts only: no clock, no `src/` change.
Owed by D164 add. 3. Instruments: `docs/design/endmark/b3cost_probe.c`, `census/b3cost.py`;
transcript `docs/design/endmark/results/b3cost.txt` (per-artifact TSV at the end).

## Verdict
Tagging costs **1.90x the reverse states of today's machine** (2,853 vs 1,505 over 266 artifacts; median per
artifact 1.75x, p90 2.25x) and **+19% reverse-table bytes** (+4.5% without one outlier, `(\p{L}+)$`). On the
raw machine the tags alone cost at most 2.00x (tagged/untagged, 0 artifacts over). The 35 artifacts over 2x
today are all bounded-repeat shapes that today's scan-edge pass compacts (section 3). The price buys 1.00x
walks for constant-`mark_prio` ties (endmark.md 1.5) and deletes a modest slice of emitter code (section 4).

## 1. Population and how it was counted
`census.py`'s rule, rerun: rows from the bench (pcrec-bench read-only: 367 rows, 351 parsed) and the corpus
(5,645 rows, 5,236 parsed); tail_probe `neol > 0` (path-final non-multiline `$`/`\Z`), then `--emit-facts`
`RX_DFA_SCAN == rev-end`. Result: **bench 9, corpus 257 = 266**, endmark.md's number reproduced. All 266
have `end_pin = eol`; the text scanner rewrote all 266; none excluded. 43 carry tie code today (bench 1).

## 2. Method (the model is the real pipeline, not the twin)
Per artifact, four reverse machines built by pcrec's own `pcrec_build_min_dfa` (after select_engine and
lower_enc, as compile.c orders them), `--features all`, the row's encoding and `-i`:
today `X$`; untagged `X\n?\z` (the mark's reverse walk, no tags); tag0 `X\z`; tag1 `X\n\z` (every
path-final `$` rewritten, same scanner as emcensus). **Tagged = the Moore-minimized product of tag0 and
tag1**: a tagged subset state is a set of (NFA state, tag); the two tags evolve independently, so it is the
pair of the two machines' states, accept info = the pair (acc0, acc1) = the mark-distance set. The twin
(endmark.md part C) is a toy AST; this uses the real classes, utf8 lowering, scan-edge pass and ctx atoms.
Controls (all in the transcript): (1) model today == emitted `rx_reverse_*` states: **266/266**;
(2) model untagged == the CLI-emitted `X\n?\z` artifact's states: **266/266**; (3) product with output
`acc0|acc1` == the untagged machine: **244/266**. The 22 misses are all ctx-atom patterns (`\b`, `\B`,
lookarounds around the `$`): pcrec's single machine carries the previous-byte class in its state, the product
does not, so their tagged figures are UNVERIFIED (reported separately, 133 tagged vs 92 today).

## 3. The table (reverse machine states; "today" = emitted, i.e. after the scan-edge pass)
| set | n | today | untagged | tagged | tagged/today med / p90 / max | >2x |
|---|---|---|---|---|---|---|
| bench | 9 | 46 | 54 (1.17x) | 83 (1.80x) | 1.80 / 1.86 / 1.86 | 0 |
| corpus | 257 | 1459 | 1727 (1.18x) | 2770 (1.90x) | 1.75 / 2.25 / 3.25 | 35 |
| all | 266 | 1505 | 1781 (1.18x) | 2853 (1.90x) | 1.75 / 2.25 / 3.25 | 35 |
| with tie code | 43 | 151 | 178 | 281 (1.86x) | 1.75 / 2.25 / 2.75 | 7 |
| utf8 | 16 | 532 | 545 | 1048 (1.97x) | 1.75 / 1.91 / 2.00 | 0 |
| ctl-3 verified | 244 | 1413 | 1661 | 2720 (1.92x) | 1.75 / 2.25 / 3.25 | 35 |
| no scan-edge today | 231 | 1345 | 1555 | 2446 (1.82x) | 1.75 / 2.00 / 2.00 | 0 |
| scan-edge today | 35 | 160 | 226 | 407 (2.54x) | 2.25 / 3.25 / 3.25 | 35 |

Table bytes (the `rx_reverse_*` static arrays; untagged = the emitted proxy; tagged = the proxy rescaled:
`next_state` by S*C at 2 B, per-state tables by S, `byte_class` fixed, C from the product's distinct
columns): today 230,915 B, untagged +1.4%, tagged **+19.0%** (bench 3,499 -> 3,669, +4.9%). Without
`(\p{L}+)$` (137,364 -> 177,121 B alone): 93,551 -> 97,738, +4.5%. Per-artifact median +21 B, p90 ratio 1.20.

**Top 10 growers (ratio):** `a{0,4}c$` x2 + `a{0,4}c\Z` x2 + `(a{0,4}c$)` (4 -> 13, 3.25x); `[a-z]{0,5}$`,
`(?:[a-z]{0,5})\Z` (4 -> 13); `a{5,10}b{5,10}$` (15 -> 43, 2.87x); `a{0,4}$` family (4 -> 11, 2.75x). By absolute
growth: `(\p{L}+)$` +453 states (454 -> 907), `a{5,10}b{5,10}$` +28, `a{0,5}b{0,5}c$` +12, `a{0,5}b{0,5}$` +11,
`(.*)\.txt$` +10. Bench growers: `[a-z]+\.txt$` 7 -> 13, `.*\.txt$` 6 -> 11, `done$` 6 -> 11, `abc$` 5 -> 9.

**The >2x list (35, all corpus)**: the five 3.25x/2.87x/2.75x rows above plus the `{1,3}`, `{2,4}`, `{3}`
counted-repeat rows (2.17x-2.25x: `[^c]{1,3}$`, `a{1,3}?$`, `a{2,4}$` x5, `(\d{2,4})$`, `(a{3})$`) and
`ERROR$` (6 -> 13). Full list in the transcript. **Why they exceed 2x:** today's scan-edge pass compacts
the bounded run (`a{0,4}$` 6 -> 4 states) and the lowered `\n?\z` tail mostly defeats it (the untagged proxy
compacts in 19 of 266, today in 35). Against today BEFORE the pass the count over 2x is **0** (max 2.00).
**endmark.md's "at most doubles for L=1" is confirmed on the raw machine** (tagged/untagged raw: median 1.40,
p90 1.67, max 2.00, none over); L is 0/1 for every `$`/`\Z`, so no L>1 case exists in this population (L>1
belongs to forward trailing lookaheads, not rev-end). Whether the pass would compact the TAGGED machine is
unmeasured (it rewires `tr`, so the product cannot be built after it): the honest range for the 35 is 2.0x
(compacted like today) to 3.25x (not), and it is the only place the doubling claim is exceeded.

## 4. What B3 deletes, and what it only replaces (current `src/gen/emit_dfa.c`)
- DELETES: `revend_nl_last` (31 lines with its comment, 11543-11573); the second seed in `emit_rev_end`
  (`bool eol`, the `eol ? 2 : 1` loop bound, the 5-line `revend_seed == 1` block, ~9 source lines); and in the
  EMITTED C of every one of the 266 artifacts the `for (revend_seed...)` wrapper plus the seed-1 block
  (about 6 lines of C each, a loop dimension in the walk).
- REPLACED, not removed: `revend_ties` (7 lines) and `revend_tie_asked` (10 + decl + 1 use) become a
  `mark_prio`-state-dependent ask; the tie arms (`revend_tie`, the verify block, the relocate; about 24 of
  `emit_rev_end`'s ~100 lines touch tie/relocate/seed/eol) are keyed to "an accepting state with >= 2
  distances" instead of two seeds; `cand_locate_hands`' ENDSET line (9428) and the ENDSET FINISH hand STAY
  (D164 add. 1 Q2: state-dependent ties finish forward). New: the tag/`back` tables, `mark_prio`, the
  `- back[state]` in the accept position. Not deleted: `PCREC_EPIN_EOL`/`EW_EOL_SLACK`/`eolvar` (forward `$`
  keeps its view, add. 3). Net removed source is roughly 40 lines plus one function; no new-line count is
  claimed (nothing is built).
- LOADS (cited, not re-derived; endmark.md 1.5): `\s+$` / `\s*?$` on a final-newline subject 3.00x -> 1.00x
  where `mark_prio` is constant, 2.00x where state-dependent; the other 223 artifacts (no tie code) cost the
  same loads (seed n-1 dies at once). So the trade reads: faster walk on 43 of 266 (7 tie rows >2x states),
  bigger table on all 266 (+19% bytes, +90% states), about 40 source lines gone.

## 5. Caveats
- Minimized reachable states (pcrec's own count), not the twin's pre-minimization subset states; the twin's
  untagged column (`\s+` 2 -> 3) differs by pcrec's eol-view state, which control 1 pins to the emitted count.
- Tagged = raw product; no scan-edge pass, no `back`-table encoding choices, no `end_view` removal (the
  proxy's view table is counted in bytes; B3's design may drop it, a few bytes per artifact).
- Tagged bytes are a rescale of the emitted proxy, not an emission. The 22 ctx rows are unverified (control 3).
- Corpus is the test corpus (skewed to edge-case shapes: 35 of 266 are tiny bounded-repeat probes); the
  bench 9 are the representative sample: 1.80x states, +4.9% bytes. The text scanner, not the lowering pass.
