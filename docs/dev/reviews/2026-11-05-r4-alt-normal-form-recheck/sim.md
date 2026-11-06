# simulate lens (SIM), round altnf2 — RELAYED via manager, critic file not written
(The critic's Write of findings.md was refused by a harness rule for subagent report files; it did not bypass it, so no lanecheck DONE. Text as relayed by the manager.)

## Findings
SIM-1 (design/maintenance, CONFIRMED): §6 table vs §3.3 strategy are two specs of sibling merge; table under-determined. `aaa|aab|aba|bba` -> table 3 leaf paths vs strategy 2; `aab|bbb|bab` -> `(?:(?:aa|bb)|ba)b` leaving a legal merge; `ab|ab` -> `ab(?:|)` vs `ab`. 432 of 2,016 distinct equal-width lists worse under the table, 104 better. Stage 2b output depends on the spec chosen. Fix: name one order.
SIM-2 (design/test, CONFIRMED): U1 ">1 box" over-predicts: sample 364 fold classes (357 non-ASCII), 223 predicted, 142 observed (run/table), 80 predicted don't move (`x(?i)σ` tables identical to unsealed spelling), 25 seal-only movers. "Merge fires" subsumed by ">1 box"; "mover" undefined.
SIM-3 (doc, CONFIRMED): "20 of 76" wrong both ways: lists cls-neg-allhigh (ASCII-only), prp-ingreek (not implemented), prp-l-anchored (refused); omits cls-d-ucp (71->39 boxes), cls-s-ucp (10->6), ci-class-range (4->3); cls-w-ucp refused; four multi-box no-merge patterns unlisted; asr-* need --features all (UNPREDICTED).
SIM-4 (test/design, CONFIRMED): nothing gates the declared strategy on wide classes (fold classes confluent under all orders). \p{Lu} 664 boxes -> 67 declared vs 105 first-major; \p{L} 827->330; Nd 71->39; dot 10->8. "76 vs 66" does not reproduce (67 under three orders). Fix: pin counts as a gate.
SIM-5 (speed, low): 2b adjacency scan O(n) per merge (205k tests for 1,296 words); equal-width short-circuit fixes.
SIM-6 (doc): §7 q3 omits property-derived classes (\p, UCP \d/\s/\w) on a UCD bump.

## PROBED-AND-HELD
Table outputs ab[xyz], [xy]ing, a(?:b||d), fr(?:ank|ed), a[bd]|xy; beta ce[92 b2]|cf 90; table soundness vs Python re ~44k cases 0 mismatches; strategy input-order independent, <=2 sweeps over 65,535 exhaustive grids; G4 1,454 classes (1,417/37), 513/766/898/1403/1416/1417, 253/398 splits, 0 mismatches vs compiler on 357 sampled; moskva widths 12-15 with width-12 piece and 12-position run as quoted, xyzkabc 7/9; o head/tail, S-e/S-f bits; all 11 §8 entry figures (αβγ 112, Ελληνικά 1040) and stage-1 run counts; U3 0 growth in 364 classes; stage 2a "today" values.
END OF FINDINGS
