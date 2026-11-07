# S2d (s2d-20261106, lane/memfn-s2c @ 508178bd2) REFUSED: analysis of the five failing floors

Read-only. Sources: the run dir's cells.J2.tsv / cells.J4.tsv / transcript.tsv / J4/placement.tsv, est.py's
own `compute()` (internals dumped by bin/dump.py here: D, Db, aa_D per row), and objdump of
J4/L1/J4.L1. Units: cells are ns x 10^6 per subject; 1 wb (walk byte) = ctl slope ~ 0.196 ns/byte at 1 Mi;
J4 E = 16384 events per 1 Mi subject (a candidate every 64 bytes).

## 0. One fact behind all of it: a two-state box over time

Per-ROUND values (each round is its own process, ASLR on, same linked executable within a launch) show the box
flipping between two states DURING launches, not between placements:

- J2 ctl and walk at 1 Mi: 7.89e8 vs 8.05e8 per round (+2.0 %); libc 9.4e5 vs 1.00-1.07e6 (+7 %).
- L5 switches after R1 (R1 low, R2-R7 high); L7 switches after R3. L1/L4/L6 stay low; L2/L3 mostly high.
- J4: the 1 Mi verify/base rounds swing 8.0 to 10.5 us within one launch (~10-25 %), in runs of rounds.
- No mod-64 placement pattern: base.null.l1's high launches have hot-loop mod 64 = 16, 0, 48; its low ones 0, 16, 16, 32.

load1 at every quiet check was 1.08-2.18 (the gate allows < 2 or waits); the box was not idle. A slow state
that hurts the L3/bandwidth-bound memchr 3.5x more than the compute-bound walk fits a co-runner competing for
the shared L3 (7700X: one CCD, 32 MiB L3, our pool 16 MiB) or memory; it does not fit a placement effect.
Cause of the second state: not identified from the artifacts (no process list was recorded).

## 1. floor:byte.libc (kit.find_byte.libc 39024, noise 1295 = 3.3 %, gate 3 %)

Numbers (x_l = libc slope / ctl slope per launch, / W, x10^6):
L1 37993, L2 40837, L3 39991, L4 37774, L5 39024, L6 37517, L7 39248. med 39024.
- A/A (libc vs libc#b) aa = 191 (0.5 %): the twins agree round by round; the noise is launch-to-launch.
- Trimmed six (drops L2): sp2 from 37517..39991; noise = isqrt(191^2 + sp2) = 1295.
- Low-state launches (L1, L4, L6): 37517-37993, spread 1.3 %; high/mixed (L3, L5, L7): 39024-39991.
- Raw slopes: libc 1 Mi cells 7.68e9 (L1/L4/L6) vs 8.11-8.47e9 (others), +6-10 %; ctl 202.0e9 vs 205.1-206.1e9, +2 %.
  The per-launch normalization by u_l cancels only the 2 % both share; libc's extra ~5 % stays in x_l.

Cause: (c) noise on this box tonight, with a structural reason it recurs on a busy box: the ctl normalization
cannot cancel a slowdown that is memory-side. 3.3 % is not libc's own variance (twins 0.5 %; one-state launches
1.3 %) and not placement (twins share a launch; switches happen mid-launch, between rounds of one binary).
On a box in ONE state for the whole of J2, noise ~ 0.5-1.5 %, a pass with margin.

What makes it pass:
- (i) Plain rerun of the window in a quieter period: no design change; needs a new window (J1-J5 ~31 min tonight,
  21:49-22:20). Risk: same co-runner, same result. Cheap guard: record `ps`/load at each quiet check, and/or a
  stricter quiet threshold for the window (a run.py parameter: code + a dry run; small).
- (ii) Policy: raise find_byte's gate (3 % -> 4-5 %) or z: a policy-table edit, a kit-manager/Frank ruling; it
  accepts a value whose spread is box-state, not libc. Not recommended.
- (iii) Design: a memory-bound control alongside ctl, or per-round (not per-launch) pairing: design revision +
  review + code + window. Out of proportion for one row.

## 2. floor:verify.rc-memcmp.l1 and floor:verify.settest.c1 (p0, p50 NULL: "negative per-event cost")

Per-launch D_l = c(arm) - c(base.null.<cls>) at 1 Mi, x1e-9 (us per subject); aa_D in the same units:

| row | D_1..D_7 | med D | aa_D | per event (wb) |
|---|---|---|---|---|
| l1.p0  | -0.065 -0.189 -0.987 -0.359 -0.843 -0.317 -0.286 | -0.317 | 0.022 | -0.10 |
| l1.p50 | -0.202 -0.271 -0.779 -0.293 -0.851 -0.301 -0.290 | -0.293 | 0.020 | -0.09 |
| c1.p0  | +0.275 -0.304 -0.956 -0.318 +0.155 -0.426 -0.309 | -0.309 | 0.026 | -0.10 |
| c1.p50 | +0.096 -0.294 -1.089 -0.334 -0.109 -0.339 -0.277 | -0.294 | 0.047 | -0.09 |

Twins (Db) track D within 0.02-0.05 us: the A/A is tight; the base-vs-arm difference is where the spread is.
Base cells (1 Mi): base.null.l1 9.30 8.50 9.21 8.57 9.15 8.57 8.63; arm l1.p0 9.24 8.31 8.22 8.21 8.31 8.25 8.35.
In launches where both sit in the low state the arm is ~3 % FASTER than its base (8.2-8.35 vs 8.4-8.6).

The code (objdump of J4/L1/J4.L1):
- base.null.l1 (`WRAP_NULL`, link.py:171): `mov (%rsi,%rax,4),%edx; movzbl (%rdi,%rdx),%edx; add $1,%rax;
  cmp; jne` - 5 instructions, indexed addressing, a byte load, the loop at a 16-byte boundary.
- rc-memcmp.l1.p0: `mov (%rdx),%ecx; cmpl $imm,(%rdi,%rcx); sete; add $4,%rdx; movzbl; add; cmp; jne` -
  8 instructions, pointer bump, a dword load fused into the compare, branchless, loop padded to 32 bytes.
- settest.c1: the same with `cmpb`. rc-words.w1: `mov; and $0xdfdfdfdf; cmp; sete; ...` (one more ALU op).
- Both loops are throughput-bound on the two loads per candidate (the candidate line from the 16 MiB pool:
  ~0.5 ns = ~2.5 cycles per event); sete/movzx/add are 3 extra ALU uops on a 6-wide core, off the critical path.

Cause: (a) primarily, with a (b) bias on top.
- (a) the compare's true marginal cost in this fixture is ~0: under ~0.1 cycle/event, below the resolution of
  ~0.1 wb/event (the trimmed D spread ~0.3 us / 16384; ~0.1 cycle at ~5 GHz). It is 1-2 orders of magnitude
  below the classes that priced (w2 7.8 wb, cn 6.9 wb, w3 13.6 wb, all with a branch or a second load).
- (b) the null base is NOT the arm's loop minus the compare: different addressing (indexed + counter vs pointer
  bump), load width (byte vs dword) and loop alignment (16 vs 32). That residual (~ -0.1 wb, the arm faster) is
  what makes the median NEGATIVE rather than ~0. It is a fixture artifact exactly as §3.5¶3 names it. (Which of
  the three differences carries it is not established without a timing experiment.)
- Box noise (c) inflates the spread (L3/L5's -0.8..-1.0 come from base rounds in the slow state while the arm's
  were not: the bases run as a block at the start of the round, the twins adjacent to their arm, so aa_D never
  sees base-vs-arm time separation), but it does not create the sign.

A rerun WILL NOT pass these: the sign is consistent over all four rows and seven launches (25 of 28 launch values negative).

## 3. floor:verify.rc-words.w1 and floor:verify.settest.c2 (p0, p50 NULL: "below A/A or signs mixed")

| row | D_1..D_7 (us) | med D | aa_D | per event (wb) |
|---|---|---|---|---|
| w1.p0  | +0.077 -0.130 -0.337 +0.243 -0.516 +0.198 +0.200 | +0.077 | 0.027 | +0.02 |
| w1.p50 | +0.084 +0.078 -0.636 +0.117 -0.409 +0.247 +0.192 | +0.084 | 0.065 | +0.03 |
| c2.p0  | +0.305 +0.111 -0.961 -0.228 +0.284 +0.158 -0.001 | +0.111 | 0.110 | +0.03 |
| c2.p50 | +0.503 -0.015 -0.863 -0.023 +0.270 +0.114 +0.060 | +0.060 | 0.159 | +0.02 |

Signs mixed in the trimmed six on all four (the trim drops L3 but L5/L2/L4/L7 stay negative). Cause: (a) - the
same single-load branchless shape plus ONE ALU op (w1's `and` mask, c2's alu1 majority shape `and`+`cmp`), so
~+0.1 wb above l1/c1, which lands the median near zero, inside the ~0.1-0.3 wb spread. The (b) base bias
(~ -0.1 wb) is present here too and pulls them toward zero. A rerun would most likely give null again
(perhaps one of the four rows priced by luck, not reliably).

## 4. What would make the verify floors pass, and its cost

- (V1) Plain rerun: no. The quantity is ~0 by the fixture's construction.
- (V2) More events per launch (CAND_STRIDE 64 -> 16, E x4): resolution x~4 at best, but the loop becomes more
  bandwidth-bound and the compare stays hidden; does not create a positive cost. Not recommended.
- (V3) Fix the base: render the null base from the ARM's own wrapper with the compare replaced by a constant
  that gcc keeps (same pointer bump, same load width, same alignment): removes the -0.1 wb bias for EVERY verify
  row (it is in the priced w2/w3/cn rows too, ~1 %). Needs: design text (§3.2 null base), link.py code, review,
  a window. On its own it turns l1/c1 from "negative" to "mixed signs": still null.
- (V4) Bound rows / floor amendment for sub-resolution classes: a delta row that is null with |med D| below its
  stated resolution is recorded as a BOUND ("cost <= r wb/event", r from the trimmed D spread, e.g. 0.2 wb) and a
  floor clause is met by a priced row OR such a bound. The reader prices those classes at ~0 with noise r, which
  is the truth for a branchless single-load compare. Needs: measures.md §3.5¶3 + §2.2 (a status or a value-with-
  noise convention), span_cards rev 1.4 (Goal 2's floor wording, §2.3 resolution for verify), est.py + the
  pcrec-side recompute, a review round. No new window by itself (est re-reads tonight's cells), but byte.libc still
  needs one.
- (V5) A latency-exposing fixture (the next candidate depends on the compare result) would price the compare's
  latency (~1-2 cycles = ~1 wb) but changes the quantity's meaning (span_pick reads throughput costs); design
  revision + review + code + window. Not recommended.
- (V6) Floor amendment only: drop the verify clause for classes whose census shape is single-load branchless
  (l1, c1, w1, c2-alu1), reader treats them as "free" by rule. Cheapest (design + spec text, review), but a
  rule-based 0 is weaker evidence than V4's measured bound.

## 5. Do any of the 33 passing rows look suspect for the same reasons?

- The "gate pass" label on DELTA rows (find_hit, verify w2/w3/cn, enter) is est.py's print default
  (`r.get("gate", True)`, est.py:306): delta rows are never gated (§3.5¶3, only the NULL rule). So:
  - kit.find_hit.walk.random.one.1024: value 51.96e6, noise 23.0e6 (44 %); D_l 6.2-14.2 us, aa_D 3.9 us.
  - kit.find_hit.walk.random.one.256: noise 37 %; D_l bimodal (26.2-27.3 vs 36.9-42.8 us), aa_D 10.6 us
    (29 % of the value): twin and arm land in different modes launch by launch.
  - kit.find_hit.walk.periodic.one.1024: 20 %; .256: 6 %. kit.verify_cmp.settest.cn.p0: 10 %; w3.p50: 6 %.
  These are priced with honest noise, as the spec allows, but the walk.random rows are the weakest numbers in
  the set and look like the same box-state bimodality, not a property of the walk. Worth a sentence in the
  record; not a refusal under the current rules. Suggest est.py print "ungated" for delta rows (cosmetic).
- The verify base bias (V3) is in every priced verify row: ~ -0.1 wb against 7-14 wb, i.e. ~1 % low. Small.
- find_hit.libc rows: x per launch shows the same L4/L7-high pattern (periodic.1024 D 3.05-3.48 us, 5 %);
  passed the NULL rule easily (costs far above resolution).
- find_byte.pair (1.9 %, gate 3 %) and the unit walk (0.2 %) passed with margin; enter rows are huge vs noise.
- Nothing else is negative or below its A/A.

## 6. Recommendation

ONE design revision, then ONE window:
1. span_cards rev 1.4 + measures.md: (V3) the null base rendered from the arm's own loop (fixture fix, removes the
   sign artifact everywhere) AND (V4) the sub-resolution bound for delta rows, with the verify floor clause met
   by a priced row or a bound. A light review (design + spec hunk), then code (link.py WRAP_NULL, est.py, the
   recompute).
2. A fresh S2d window for byte.libc (and to price the verify rows under the fixed base), with the quiet check
   recording who is running (and optionally a tighter load threshold). Night, cleared per house rules.

Alternatives, in order:
- (A) Rerun the window unchanged for byte.libc only and amend the floor by rule (V6) for the four verify classes:
  fastest to an ACCEPTED set, weakest evidence for those classes (a rule, not a bound), keeps the base bias.
- (B) V4 without V3: tonight's cells could already be re-estimated to bounds for the verify rows (no window for
  them); byte.libc still needs a window. Leaves l1/c1 recorded as "negative" artifacts with a bound around them.
- (C) Raise find_byte's gate: not recommended; it would accept a box-state spread as libc's noise.
