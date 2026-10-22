# e8why — why V1 loses to the walk on 10 of B4's 19 real-pattern movers

Lane e8why, 2026-10-21. COUNTS ONLY (no timing, no build, no make): `docs/dev/lanes/e8why_count.py` over the subjects in
`build/e8slot_r2/subj` and the V1 artifacts in `build/e8slot_r2/bin/j1-*/`; deltas are run 2's `e8_cells.tsv` (same
cells lose in run 1). Labels: MEASURED = counted from bytes/rows; DERIVED = arithmetic; INTERPRETATION = mine.

## 1. What the two arms are (item 5, MEASURED from the emitted text)
For all 19 movers the V1 and walk `art.c` differ by ONE search line: `while (scan_position + 1 < n && !table[subject[sp]]) sp++;`
becomes `sp = next_candidate(&c, sp)` (8-byte SWAR mask, cached lane mask, ctz) plus a 5-word cursor struct. The walk's
256-byte table equals V1's member set byte-for-byte on all 19 (checked). So both arms stop at the SAME bytes in the same
order and run the same matcher after each stop. The only variable is the cost of getting from one member hit to the next.

## 2. Per-pattern table (MEASURED). G = mean bytes per member hit; E = share of 8-byte blocks with no member;
## Q = walk mispredicts per stop (§3); verdict letters per subject
| pat | shape | set | losers? | d range % | G | E | Q | verdicts |
|---|---|---|---|---|---|---|---|---|
| P14 | r2e0c0 | [A-Za-z] | LOSS 6/6 | +19.8..+22.5 | 1.3 | 0.00 | 0.31 | RRRRRR |
| L10 | r1e0c0 | [a-z] | LOSS 6/7 (bgl W) | -8.5..+40.5 | 1.9-7.1 | 0.13-0.79 | 0.24-0.59 | RRWRRRR |
| C16 | r0e2c0 | {tab,sp} | LOSS 5/5 | +2.8..+23.3 | 3.7-5.7 | 0.27-0.38 | 0.45-0.90 | RRRRR |
| B09 | r1e0c0 | [ -~] | LOSS 2/5 (tars) | -16.2..+9.2 | 1.1-2.7 | 0.03-0.14 | 0.05-1.00 | WRRWW |
| B22 | r1e0c0 | [ -~] | LOSS 2/5 (tars) | -19.6..+3.7 | 1.1-2.7 | 0.03-0.14 | 0.05-1.00 | WRRWW |
| P15 | r1e0c0 | [A-Z] | LOSS 5/6 (small) | -0.2..+7.5 | 36-53 | 0.84-0.88 | 0.70-0.99 | RRRRRN |
| P04,P06,P24 | r1e0c0 | [A-Z] | small, mixed | -4.2..+4.3 | 36-53 | 0.84-0.88 | 0.70-0.99 | R/N mostly |
| S03 | r1e0c0 | [0-9] | R on gazetteer only | -0.6..+2.7 | 1.5-12 | 0.05-0.82 | 0.16-0.76 | RWNWN |
| P12 | r1e0c0 | [A-Z] | no | -6.5..-2.4 | 36-53 | 0.84-0.88 | 0.70-0.99 | WWWWWW |
| P05 | r0e2c0 | {D,M} | no | -34..-27 | 320-990 | 0.98 | 1.0 | WWWWWW |
| C21 | r1e0c0 | [0-9] | no | -39..-20 | 38-175 | 0.94-0.97 | 0.5-1.0 | WWWWW |
| B10 | r0e0c1 | [\x80-\xff] | no | -64..-20 | 2-110 | 0.00-0.98 | 0.32-1.0 | WWWWW |
| N18 | r1e0c0 | [\xc2-\xf4] | no | -17..+0.9 | 25-78 | 0.71-0.90 | 1.0 | NWW |
| N02,N08,N10,N15 | mixed | 2-3 lead bytes | no | -21..-56 | no hits | - | - | W x12 (ZERO member bytes) |

P04/P06/P12/P15/P24 are the SAME set on the SAME six subjects: identical hit sequences, G, E and Q to the digit.
Zero-hit cells (12): all W; V1 scans 8 B per step with no stop at all. The S03 non-gazetteer cells time 14-500 us on
2-42 MB (the scan exits early), so their deltas say nothing about stops.

## 3. Candidate explanations tested (82 cells with hits; "big loss" = d >= +9%, 17 cells)
- Set size, cover shape (r/e/c), scanned position, pattern text: DO NOT separate. Shape r1e0c0 holds losers (L10, B09,
  P15) and winners (C21, N18, P12). Set size 2 holds a loser (C16) and a winner (P05).
- Hits per match / candidate-to-match rate: DO NOT separate. L10 loses +40% with ZERO matches and +17% with 18,685; P14
  loses equally at 133 and 574 hits per match; C21 wins at 300-2000.
- Member density per byte alone: no. Dense random sets WIN (B09/B22/B10 on zip, gz, bz2: density 0.37-0.50, d -16..-23%);
  dense structured sets LOSE (B09/B22 on tar 0.77-0.90, P14 0.73-0.76, L10 0.39-0.57).
- Mean gap G alone (G < 6): catches all 17 big losses but 16 false alarms (the random-dense binaries). Not clean.
- Gap regularity IS the separating axis. Q = mispredicts per stop of an ideal order-6 context predictor on the per-byte
  member bit (DERIVED; k=10 agrees). Q ~ 1.0: the walk's exit branch misses at every stop (random or sparse hits);
  Q < 0.8: mostly predicted.
- Rule R = (E <= 0.4) AND (Q < 0.8), "many hits per block, and predictable": all 17 big losses at 0.8 (16 at 0.7); 5 false
  positives, all small or at-floor (B09/B22 tar +3..+6%, S03 ne -0.03, S03 usgs -0.55); 60 true negatives. Against the
  verdict R of any size: 19 tp, 2 fp, 16 fn (the 16 are the prose [A-Z] cells).
- Both terms needed: Q alone misses sparse-and-regular wins (bgl, B10 tar: Q 0.24-0.32 but E 0.79-0.88, WIN -8.5/-38%);
  E alone misses random-dense wins (E 0.00-0.14, Q 1.0, WIN -16..-23%).

## 4. grid2's anchors on the same axes (DERIVED from subj_facts.tsv and the generator's regularity)
| cell | G | stops | E | Q | grid2 d |
|---|---|---|---|---|---|
| dig / dfa-hat g2 reg | 2 | periodic | 0 | ~0 | +15..+45% LOSS |
| dig g8 reg L1k | 8 | periodic | 0 | ~0 | +34.9% LOSS |
| dfa-hat g16 u | ~21 | Bernoulli | 0.69 | ~1 | +8.6% (L32) |
| any g >= 4 u, L >= 1k | - | Bernoulli | - | ~1 | V1 wins (grid2 M15) |
Same law in the synthetic grid and in real text: regular, block-occupying stops lose; unpredictable stops win. The SS2
+9..+13% at L32 (also at ginf, no stops) is a per-call cost on 32-byte calls, a different mechanism; J1 is whole-file
find-all (and L10 loses with zero matches, so it is not per-match restart either).

## 5. Interpretation (mine)
Both arms stop at the same bytes. The walk costs ~1 byte/iteration plus a mispredict when the stop pattern is irregular;
V1 costs a per-stop `next_candidate` call (cursor reload, cached-mask shift, ctz) plus a per-block mask. Dense AND
predictable stops (letters in prose/logs, printable runs in tar, tab/space runs in code): the walk's branch is nearly
free and V1's per-stop overhead is pure loss (P14: 73% of bytes are stops, ~+0.6 ns/stop). Unpredictable stops: the walk
pays a mispredict per stop and V1 wins (zip/gz/bz2, grid2 u cells). Rare stops (E >= 0.8): the 8-byte step dominates and V1
wins big (P05, C21, N*). The census's term count describes the set, not the subject, so it cannot see this.
NOT explained by these counts: the 16 small prose cells ([A-Z] sets, d -6.5..+7.5, floor-sized). P12 wins and P15 loses
on identical stop sequences, so that spread is a post-stop interaction (inlining, spills around the address-taken cursor,
the candidate test); counts cannot show it and I did not read the assembly.

## 6. What a rule using it would look like (one paragraph, no design)
The deciding statistic is a property of the subject's hit sequence, so a compile-time rule on the set alone cannot make
it. A rule could take V1 when the set's empty-block share is high (E ~> 0.4: every rare-start set such as P05, C21, N*)
or when stops are unpredictable (Q ~> 0.8), and the walk when stops are dense and regular (E <= 0.4 and Q < 0.8: P14,
L10 on logs, C16, B09/B22 on tar), fed by a profile or run-time estimate of those two quantities. The thresholds here are
fitted to these 94 cells and are unmeasured defaults (SUSPECT per the tuning-constants rule); the 5 false positives sit
within +6%.
