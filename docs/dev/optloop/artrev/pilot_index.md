# [ARTREV] pilot index (collected 2026-10-06, lane artcollect)

Four blind reviews at pin 57db5152 (abi 62, gcc-16 16.2.0 -O2, Mac M1), each in its own D27 cell:
rvA01 -> `A01/` (loglines_stack_frame), rvA07a -> `A07a/` and rvA07b -> `A07b/` (both
capability_doubled_word, the dual-review pair), rvA09 -> `A09/` (loglines_level_context).
Every reviewer file is verbatim from its cell (`review.md`, `leads.tsv`, `CELL.md`, sealed `twins/`
patches, `controls/`, `tools/`, `edge_subjects/`); the notebook entries are under `notebook/`.
No collected file was edited. Edge subjects are committed (A01 96 KB, A09 1.2 MB: under the 2 MB bar).

"Scratch verdict" is what the lane itself measured on the Mac (scratch tier, never reported). Only A07b
timed anything (one run, `iterations.tsv`: orig/orig2/null/L1-L4, 11 rounds, 3 subjects); A01, A07a and
A09 timed nothing (suite lock / load gate / timing lock refused every attempt, none overridden), so
their "expected effect" is the reviewer's work-count estimate. "Hardened identity" results for every
sealed twin are in `docs/dev/lanes/artcollect_report.md`.

## A01 loglines_stack_frame (DFA find-all, losing cell) -- 4 counted leads, 3 controls

| id | class | origin | idea | reviewer's expected effect | scratch verdict |
|---|---|---|---|---|---|
| L1 | algorithmic | fresh | scan the rarer required byte '(' instead of memchr('a'); walk back over the `[A-Za-z0-9_$.]` run; run the anchored DFA there | largest of the set: memchr calls 33,377 -> 3,820 per MiB on fail (several-fold) | none (identity PASS, timing owed) |
| L2 | redundant-work | fresh | memchr 't' (offset 1) instead of 'a' in rx_reqrun | -17% memchr calls on fail, ~-15% on hit; small, superseded by L1 | none |
| L3 | redundant-work | fresh | replace the reverse DFA pass by a backward scan for the last "at " | hit only, ~10-15% of hit; cell median unmoved | none |
| L4 | redundant-work | fresh | skip the first-iteration rx_ofsskip when the position is the handoff | 1 memchr/call, ~2% of hit's memchrs; expect NOISE | none |

Controls (uncounted, all FAIL as intended): ctldollar, ctlfrom, ctlat. No combined twin (L1 subsumes L2-L4).

## A07a capability_doubled_word (VM + backref, losing cell) -- 6 counted leads, 2 controls

| id | class | origin | idea | reviewer's expected effect | scratch verdict |
|---|---|---|---|---|---|
| L1 | control-flow | fresh | start only at word starts; after a failed attempt skip the rest of the word and the gap | large: ~3/4 of attempt calls removed | none |
| L2 | algorithmic | fresh | drop the two give-back RX_PUSH frames (spans possessive) | medium | none |
| L3 | redundant-work | fresh | the attempt as straight-line code; slots 2/3 written only on accept | medium-large over L2 | none |
| L4 | loop-structure | fresh | fuse L1+L3: inline word walk, resume at end of the `\s` run | medium over L1+L3 | none |
| L5 | data-layout | fresh | one 256-byte table (bit0 `\w`, bit1 `\s`) | small-medium on L4 | none |
| L6 | compiler-hint | fresh | run counters/pointers in locals for the attempt (RX_RET) | small-medium on the original VM; the general VM lead | none |

Controls: ctlskip (FAILS identity), ctlclamp (PASSES plain, FAILS under --san). Reviewer's expected order (unmeasured): L4/L5 >> L1 > L3 > L2 > L6.

## A07b capability_doubled_word (same artifact, independent review) -- 6 leads, 7 counted revisions

| id | class | origin | idea | reviewer's expected effect | scratch verdict |
|---|---|---|---|---|---|
| L1 | algorithmic | fresh | fold the leading `\b` into the start filter (rx_next_word_start) | ~77% fewer matcher calls; scratch -20% | WIN (-19..-21%, run 001) |
| L2 | redundant-work | fresh | delete the two give-back frames and their labels | scratch -45% alone | WIN (-45%) |
| L3 | redundant-work | fresh | on L2: RX_SET a plain store (no trail) | scratch -53% (L2+L3) | WIN (-53%) |
| L4 | call-boundary | fresh | L1+L2+L3 + rx_fail = return -1 + always_inline matcher (r1 rejected for a stray file, r2 sealed) | scratch -72% | WIN (-72%) |
| L5 | algorithmic | fresh | matcher reports the furthest dead span cursor; the search restarts there | fewer bytes classified, ~1 fewer mispredict/word | none (never timed: gate/lock refusals) |
| L6 | data-layout | fresh | 256-entry tables for `\w`/`\s` | small, perhaps noise | none (never timed) |

Run 001 medians, ns/B at t64k/t256k/t1m: orig 9.41/9.28/9.30; L1 7.60/7.43/7.39; L2 5.21/5.09/5.09; L3 4.42/4.41/4.41; L4 2.51/2.63/2.63; null within 0.04-1.1% of orig. Control sabL1 FAILS identity.

## A09 loglines_level_context (hybrid DFA prefilter + VM, losing cell) -- 6 counted leads, 9 revisions, 8 controls

| id | class | origin | idea | reviewer's expected effect | scratch verdict |
|---|---|---|---|---|---|
| L1 | algorithmic | fresh (r2 rare-byte choice: notebook rvA01) | skip the searching component {0,29} with two memchr streams on 'O' and 'T' (r1 three streams C/E/F; r2 sealed) | fail/syslog DFA steps 1.0M -> 0 per MiB; >=10x on the prefilter | none |
| L2 | algorithmic | fresh | the same skip, pure scalar 256-byte table loop | ~3x on the prefilter | none |
| L3 | algorithmic | fresh | skip the after-level component {406,435} with an exit table | hit only, ~5-15% of post-L1 hit | none |
| L4 | redundant-work | notebook rvA01 | drop the reverse pass (r1) and skip the VM when the window is provably the answer (r2, r3 adds the capacity guard) | hit: reverse steps 12.4k -> 0, VM attempts 193 -> 0 per MiB (~30% of post-L1 hit) | none |
| L5 | control-flow | notebook rvA07a | frameless lazy step (drop RX_PUSH, keep capacity check and step charge) | hit: ~45 -> ~25 instr per lazy position; moot under L4 r3 | none |
| L6 | other | fresh | combination L1 r2 + L3 + L4 r3 + L5 | fail/syslog as L1; hit 6.6k memchr + 5.9k DFA steps/MiB | none |

Revisions: L1 r1/r2, L4 r1/r2/r3 (r2 PASSED default-buffer identity but answered where the original gave up with 0 frames/trail: the
finding that produced the charter's give-up rule), others r1. Controls (uncounted): ctlnb, ctlnof, ctlnb2, ctlbnd (FAILS only under --san),
ctlL4, ctlL4e (livelocks), ctlgap, ctlL3. Transfer from the notebook: 2 of 6 leads (L1's byte choice, L4, L5).

## A07 overlap: rvA07a vs rvA07b (blind to each other until both finished)

a: 6 leads, b: 6 leads (b's L4 is a combined+inline twin; its L1-L3 are the single mechanisms).

| a lead | b lead | match |
|---|---|---|
| L1 word-start filter (+ skip the rest of the word after a failure) | L1 word-start filter (rx_next_word_start) | MATCHED (same mechanism; b's post-failure skip is its L5) |
| L2 drop the two give-back frames | L2 delete the two give-back frames | MATCHED (identical) |
| L5 byte table for `\w`/`\s` | L6 byte tables for `\w`/`\s` | MATCHED (identical) |
| L3 straight-line attempt, slots written only on accept | L3 untrailed slot writes (RX_SET plain store) | PARTIAL (same waste: trail traffic; a removes it by restructuring, b by one macro) |
| L4 fused search loop, resume at the end of the `\s` run | L4 always_inline matcher + L5 restart after the dead spans | PARTIAL (same fusion/skip idea split across two b leads) |
| L6 run counters in locals (RX_RET) | -- | UNIQUE to a |
| -- | (none unique) | UNIQUE to b: 0 whole leads (b's L3, L4, L5 each only partially overlap a's) |

Counts: of a's 6 leads, 3 matched fully, 2 partially, 1 unique to a. Of b's 6, 3 matched fully, 3 partial (L3, L4, L5), 0 unique.
Union of distinct ideas: 7 (L1, L2, table, trail-removal, fusion/inline, restart-after-span, counters-in-locals). Both reviewers independently
found the three highest-value ideas (word-start filter, dead frames, tables) and the same pitfall class (the step budget moves).
The only idea one reviewer alone found: a's counters-in-locals. The only measured data across the pair is b's run 001 (a never timed).
