# b4prep item 5: r17b_prime §9.2a's expected-loss list, filled as far as the kit can

PRE-REGISTRATION. This file is committed BEFORE any B4 timing and before E5. Its rule is §9.2a's rule, unchanged
(`r17b_prime.md` §9.2a); no timing result may edit the list afterwards. Every number is grid2's (zen4-grid2 slot,
read by `grid2read/analysis.txt` §6b, §6d, §6e, §8, §8b; V1 at layer OFF against MAIN's walk, find-all, ns per 64 KiB
pass, A/A-floor verdicts R = slower / N / W = faster). The kit can name only grid2's cells and the pcrec-side known
cells; the bench's cells wait for the relay (section 4). Regime: streamed fresh buffers, one box (Ryzen 7 7700X, gcc
15.2); a different box or regime could flip a cell, so the list is for this box and labelled so.

## 1. The rule applied (§9.2a: B4 mover at OFF, landings REGULAR, mean gap <= 8 B)

Regular is a counter reading (walk branch misses per landing < 0.1; `UNMEASURED DEFAULT` between grid2's clusters
0.009 and 0.97-1.44). grid2's regular groups are the ones with no `u` token in the subject name: every g = 2 group (landings 2
apart cannot be anything else) and the `reg` shape at g = 8 and g = 32 (F2: 0.009 / 0.035 misses per landing).

## 2. THE LIST (EXPECTED LOSSES)

| id | cell (cover shape, gap, call length) | landings | grid2 V1 vs walk | 2x line (a FINDING if exceeded) | source |
|---|---|---|---|---|---|
| EL1 | dig (1,0,0), g = 2, L = 32 | regular | +21.8% R | +43.6% | §6b |
| EL2 | dig (1,0,0), g = 2, L = 1k | regular | +15.3% R | +30.6% | §6b |
| EL3 | dig (1,0,0), g = 2, L = 64k | regular | +14.9% R | +29.8% | §6b |
| EL4 | dig (1,0,0), g = 8 `reg`, L = 1k | regular | +34.9% R | +69.8% | §6d |
| EL5 | dfa-hat (0,1,1), g = 2, L = 32 | regular | +41.3% R | +82.6% | §6b |
| EL6 | dfa-hat (0,1,1), g = 2, L = 1k | regular | +44.8% R | +89.6% | §6b |
| EL7 | dfa-hat (0,1,1), g = 2, L = 64k | regular | +45.7% R | +91.4% | §6b |
| EL8 | bounded (1,0,0), g = 2, L = 32 | regular | +21.4% R | +42.8% | §6b |
| EL9 | bounded (1,0,0), g = 2, L = 1k | regular | +17.9% R | +35.8% | §6b |
| EL10 | bounded (1,0,0), g = 2, L = 64k | regular | +17.8% R | +35.6% | §6b |
| EL11 (B5, not B4) | VM hat o-vm, |S| = 1 (F2), g = 2, 64 KiB pass | regular | +38.3% R (54,220 -> 74,966 ns) | +76.6% | §8, §8b.6 |

EL1-EL10 are scored against B4; EL11 joins at B5 (Q-R17P-27 YES; B4 does not move the VM hat, §9.2a). Cells with
g = 2 and the same shapes at other L (L = 8, 128) exist in the slot's subject lists but were not read into the
tables above; if B4's G1 covers them they are listed by the same rule.

## 3. Cells the rule does NOT list, and what the kit says about them

3a. WATCH cells (regular, gap > 8 B; reported, not scored). grid2: dig `reg` g = 32 L = 1k V1 -24.7% W (a win, so
if listed it would be a "listed cell that wins" finding); `burst` shapes are not regular.

3b. **A GAP between the rule and its own "known cells" list (needs main's ruling; not the kit's to resolve).** §9.2a's
known-cells list names "dfa-hat L = 32, where V1 is never faster" and "bounded, which crosses at ~64 B", but the rule's
second conjunct (regular, gap <= 8 B) does not select the cells that make those statements true. grid2's measured V1
losses on UNPREDICTABLE-landing cells at gaps above 8 B are:

| cell | g | V1 vs walk |
|---|---|---|
| dfa-hat (0,1,1), L = 32 | 16 / 32 / 64 / 256 / inf | +8.5% / +13.3% / +11.3% / +9.3% / +8.7% R |
| dig (1,0,0), L = 32 | 16 | +2.6% R |

(both are movers; dfa-hat L = 32 at g >= 16 is 4 of the 5 R cells in its row.) Read literally, §9.2a calls an UNLISTED cell
that loses beyond its floor a refutation of B4 (§9.4). These cells are already measured to lose, so B4's G1 will report
them as unlisted losses unless main either (a) adds a clause naming short-call (L <= 32) cells or (b) accepts them as the
refutation. The kit lists them here as KNOWN UNLISTED LOSSES so the question is on record before timing, and does not add
them to the list: widening the rule is main's call (and §9.2a says the list is not edited by results).

3c. Real-text residual (user-space cycles, NOT timed; grid2read §3.9): bounded on prose V1 +16.7%, docs +5.0%, code
+4.0%; dfa-hat prose +8.9%, docs +6.1%, code +6.5%; hex-run +0.7 / -3.3 / +0.6%. These are the "named residual" (rev 3
§9.2 item 3) and are counts only, so they are neither listed nor scored; any timed reading of them is reported separately
(D169's revisit trigger applies to a real subject >= 64 KiB).

3d. The 54 byte-arm sites on untimed shapes, and the untimed 1-2 term covers: nothing is known about their landings.
They are movers under the term-count rule and join the list only through a counter reading at B4 (the rule's "no
counters" fallback: the gap sequence itself, marked `selected-without-counters`).

## 3e. `[b4prep-close]` The SHORT-SUBJECT class, registered (ruling 2026-10-21, kit manager, confirmed by main)

3b is RULED: §9.2a gains a SHORT-SUBJECT class (L <= 64 B, D169's reasoning); the regular-landing rule stays as written. The
three unlisted grid2 losses are registered under it before any B4 timing. The 2x FINDING line holds for the class; a loss
outside the listed classes still refutes B4 (§9.4). This section does not edit EL1-EL11.

| id | cell | landings | grid2 V1 vs walk | 2x line (FINDING) | source |
|---|---|---|---|---|---|
| SS1 | dfa-hat (0,1,1), g = 2, L = 32 | regular (also EL5) | +41.3% R | +82.6% | §6b |
| SS2a | dfa-hat (0,1,1), g = 16, L = 32 | unpredictable | +8.5% R | +17.0% | §6b |
| SS2b | dfa-hat (0,1,1), g = 32, L = 32 | unpredictable | +13.3% R | +26.6% | §6b |
| SS2c | dfa-hat (0,1,1), g = 64, L = 32 | unpredictable | +11.3% R | +22.6% | §6b |
| SS2d | dfa-hat (0,1,1), g = 256, L = 32 | unpredictable | +9.3% R | +18.6% | §6b |
| SS2e | dfa-hat (0,1,1), g = inf, L = 32 | unpredictable | +8.7% R | +17.4% | §6b |
| SS3 | dig (1,0,0), g = 16, L = 32 | unpredictable | +2.6% R | +5.2% | §6b |

SS1 is the same cell as EL5 (one cell, two classes; scored once, against the tighter of the two lines, which are equal).

## 4. The relay question to pcrec-bench (DRAFT; main sends it; the lane writes nothing to pcrec-bench)

> pcrec-bench: for the sets B4 (kit routing commit, R17-b prime) will be judged on, which cells have a set-FIND
> site (a byte-class prefilter, a DFA hat, or a hybrid prefilter) whose subject has dense, regular landings: a mean
> gap of at most 8 bytes between candidate landings, with one dominant gap value? Please report, per cell: the cell id,
> the site kind, the subject and its length, the mean landing gap and the share at the dominant gap, and, if you have
> counters, the walk's branch misses per landing on that cell (our boundary for "regular" is 0.1 misses per landing,
> an unmeasured default between two measured clusters, 0.009 and 0.97-1.44). If you have no counters, the gap sequence
> alone will do; say so. Please do not tell us which way you expect those cells to move. We will filter your answer by
> the rule in r17b_prime.md §9.2a and add the survivors to the pre-registered list before any B4 timing.

## 5. What is owed

- The bench's cells (relay, section 4), owner main, trigger: before E5's pre-registration.
- A counter reading of the walk's misses per landing on every B4 G1 cell (to apply the boundary): owner B4's acceptance lane.
- ~~Main's ruling on 3b.~~ `[b4prep-close]` Ruled and registered (3e).
