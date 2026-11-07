# s2d window 2 (s2d-20261107a) l1/c1 negatives — analysis

Read-only. Run s2d-20261107a (FROZEN 1e4999d1c), compared with s2d-20261106 (508178bd2). Values from est.py's own
`compute()` at each run's own commit (bin/dump2.py here prints x, value, aa, medD, aaD per row).

## 1. Units, and window 2's l1/c1 in wb per event

- Cells `ns_e6` = ns x 10^6 per subject (one 1 Mi subject per round). D_l = c(arm) - c(base) at 1 Mi in the same
  unit, so medD -3.66e8 = -366 ns = -0.366 us per subject. E = 16384 events/subject (candidate every 64 B).
- `abs` = med(D_l / E) in ns_e6 per event (l1.p0: -22355 = -0.022 ns/event).
- x_l = (D_l/E) / u_l (ctl slope, ns/byte) / W (the unit walk ratio, ~1.0) x 10^12: wb x 10^6 per event.
  `value` = med x. 1 wb ~ 0.196 ns ~ 1 cycle at ~5 GHz.

| row | win 2 value (wb/event) | win 2 x_l range | aa (wb) | win 1 value | win 1 medD (us) | win 2 medD (us) |
|---|---|---|---|---|---|---|
| l1.p0  | -0.116 | -0.292 .. -0.019 (7/7 neg) | 0.014 | -0.099 | -0.317 | -0.366 |
| l1.p50 | -0.106 | -0.199 .. -0.064 (7/7 neg) | 0.019 | -0.092 | -0.293 | -0.333 |
| c1.p0  | -0.119 | -0.326 .. +0.067 (6/7 neg) | 0.009 | -0.098 | -0.309 | -0.377 |
| c1.p50 | -0.107 | -0.309 .. +0.086 (6/7 neg) | 0.010 | -0.093 | -0.294 | -0.339 |

Window 2 is the SAME size as window 1, ~10-20 % more negative: rev 1.4's base (R14-1) did not move the bias
toward zero. -0.11 wb/event = ~-0.02 ns = ~-0.1 cycle per event, against a total event cost of ~0.57 ns
(base 9.37e9 ns_e6 / 16384) ~ 2.9 cycles. The arm is ~4 % FASTER per event than its "null".
c1's single positive launch (L6: +0.067 / +0.086) is KEPT by the trim (the trim drops the launch farthest from
the median, L4's -0.326 / -0.309), so c1's trimmed six are not all negative: est names it "signs mixed, above r"
while l1 gets the all-negative defect text. Same phenomenon, two NULL reasons.

## 2. The timed code at 1e4999d1c (objdump of J4/L1/J4.L1; every launch links the same objects, placement differs)

Hot loops, one event (candidate) per iteration:

| body | instructions | macro-ops (cmp+jb fused) | loads | what the load writes |
|---|---|---|---|---|
| base.null.c1 (a0) | `mov (%rdx),%eax; movzbl (%r8,%rax),%esi; mov $1,%eax; cmp $1,%eax; sbb $-1,%rcx; add $4,%rdx; cmp; jb` | 7 | 2 | a GPR (esi, dead: only the empty asm reads it) |
| base.null.l1 (a3) = base.null.w1 (a4) | the same with `mov (%r8,%rax),%esi` (dword) | 7 | 2 | a GPR |
| l1.p0 / l1.p50 | `mov (%rdx),%ecx; cmpl $0x6573752f,(%rdi,%rcx); sete %cl; add $4,%rdx; movzbl %cl,%ecx; add %rcx,%rax; cmp; jb` | 7 | 2 | FLAGS only: the load is fused into the compare (one load-op macro-op) |
| c1.p0 / c1.p50 | the same with `cmpb $0x2f,(%rdi,%rcx)` | 7 | 2 | flags only (fused) |
| w1.p0 (for contrast) | `mov; mov (%rdi,%rax),%eax; and $0xdfdfdfdf; cmp $imm,%eax; sete; add; movzbl; add; cmp; jb` | 8 | 2 | a GPR (separate load) |
| c2.p0 (for contrast) | `mov; movzbl (%rdi,%rax),%eax; and $0xffffffdf; cmp $0x58,%al; sete; add; movzbl; add; cmp; jb` | 8 | 2 | a GPR (separate load) |

Per event the l1/c1 arm and its base differ in exactly this: the arm's candidate load IS its compare (`cmpb/cmpl
$imm,(mem)`, one macro-op writing flags) followed by sete/movzbl/add (the count, dependent on the load); the base's
candidate load is a plain load into a register, followed by mov $1/cmp $1/sbb (the count, independent of the
load). Same macro-op count (7 vs 7), same two loads at the same addresses and widths (for p0 the subjects are
byte-identical: gen.c's seed is (len, pass, idx) and the base draws its class's p0 instance), same 1-cycle
loop-carried accumulator (sbb vs add), loop bodies 27-28 B each inside one 32-B window, hot loops at mod 64 = 0 or
32 varying by launch with no relation to the sign (base.null.l1 0 in 6/7 launches, l1.p0 32 in 4/7; D negative in all).

Why the base costs MORE: static accounting does NOT explain it. Uops, ports and dependency chains are equal or
favour the base (its count chain does not wait on the load; the arm has four ops waiting on each load). The
sbb/flags chain (REV14-8) is NOT the cause: window 1's base had no compare, no sbb (`movzbl; add $1; cmp; jne`)
and gave the same ~-0.1 wb. What the two bases share, and l1/c1 lack, is a candidate load that writes a GPR (an
un-fused load). The arms-only cross-check (no base involved, est's abs per event) gives the same step:

| arm vs arm (wb/event, window 2 p0) | difference |
|---|---|
| w1 (separate load + and) - l1 (fused) | +0.137 |
| c2 (separate load + and) - c1 (fused) | +0.145 |
| base (separate load) - l1 / c1 | +0.116 / +0.119 |

So in this L3-streaming regime (16 MiB pool, a fresh line per event, ~0.57 ns ~ 2.9 cycles/event, bandwidth-bound)
a body whose candidate load writes a register costs ~0.12-0.14 wb/event (~4 %) more than one whose load is fused
into its compare, and w1's/c2's `and` adds ~0.02-0.03 wb at most. The microarchitectural reason is NOT
established (it would take perf counters or a timing experiment; neither was run). A plausible one: with ~15-20
iterations in flight to cover L3 latency, the extra physical-register/scheduler occupancy of an un-fused load
limits memory-level parallelism; stated as a hypothesis only.

Real and reproducible: yes.
- Per launch: l1 7/7 negative (both pass rates), c1 6/7 (L6 positive), in BOTH windows under two different bases.
- Per round (transcript, 7 rounds x 7 launches = 49 per row; bin/rounds.py, rounds.txt): negative in 39 (l1.p0),
  40 (l1.p50), 45 (c1.p0), 42 (c1.p50). Medians -0.38..-0.45 us per subject. Whether the base runs before or after
  its arm in the round does not matter for l1 (28 rounds before: -0.41 us; 21 after: -0.52). c1's base ran before
  its arm only in round 1, as the round's first verify point right after ctl, where it was fast (7 rounds, med
  -0.03 / +0.72): a first-point effect on 1 of 7 rounds, not the median.
- A/A: aa 0.009-0.019 wb (twins adjacent to their arm), 6-12x tighter than |value|; the base-vs-arm gap is not
  launch noise.
- p0 vs p50: within 0.01 wb (branchless sete: the pass rate is invisible), as expected.

## 3. Is a "null" base for a fused one-instruction compare achievable?

The crux: in l1/c1 the compare and the candidate load are ONE instruction (`cmpb/cmpl $imm,(mem)`). "The loop
with the compare removed" cannot keep the load in that form: removing the compare un-fuses the load into a plain
register load, and that change alone costs ~+0.12 wb in this regime (section 2). So no base built by REMOVING
the compare can be null for these classes; the measured D is the fused-vs-unfused step, not the compare. The
compare's marginal cost over the load it rides on is zero at the instruction level (no extra macro-op) and
measured <= 0.

(a) A base with the arm's shape, comparing against a never-matching register value (`cmpb %reg,(mem)`, sete,
    movzbl, add). For p0 the arm itself never matches, so this base IS the arm with imm -> reg: D ~ 0 by
    construction. It would pass the floor via the sub-resolution branch, but as a control sharing its source
    with what it controls: it cannot fail and measures nothing (learnings §3). Costs: design + review + link.py
    (a new null_body form per load spelling) + a new window. Not recommended.
(b) Rule-price l1/c1 at 0 by an evidence row, scoped by a STATED class fact, not by the sign: "the class's
    compiled compare is a load-op on the candidate load (no separate ALU op)", value 0, noise = max(r_max,
    |med x|) ~ 0.12 wb, source naming the evidence (two windows, two different bases, both negative; the
    arms-only fused/unfused step). This keeps REV14-1 intact (a consistent negative on any OTHER class stays a
    defect). Costs: span_cards §2.3/§3.5 + measures.md §3.5¶3 text (a `bound`/`folded` status or a declared row),
    est.py branch keyed on the class fact + self-test + a sabotage row (a non-fused class wearing the fact is
    refused), the pcrec-side recompute's same rule, a review. NO new window for l1/c1: window 2's cells already
    carry the evidence. Open procedural point for the kit manager: est at a commit later than the run record's
    code_commit re-reading frozen cells (window 1's V4 assumed this is allowed; the record should name the
    estimator commit).
(c) A different regime. L1-hot candidates (front-end/uop-bound): base 7 vs arm 7 macro-ops, so D ~ 0 again, sign
    unknown; it does not expose the compare either. A latency-bound fixture (next candidate depends on the
    result) prices latency (~1 cycle), a different quantity from span_pick's throughput verify_r. Both: design
    revision + review + code + window. Not recommended.
(d) Drop l1/c1 from the floor. Row 1 cannot take that alone: span_pick's verify_r = sum_i cmp(form_i, pass_r(i))
    x prod pass (span_pick.md:217) needs a cmp price for every census class at every verify position, and §The
    pick 4 says a card without noise cannot qualify, so candidates whose verify includes an l1 or c1 position
    (among the commonest shapes) would be unpriceable. Goal 2's floor ("for each census (form, cls), at least
    one verify_cmp row") exists for exactly that reader. (d) is only viable WITH a rule price, which is (b).

What row 1 actually needs from l1/c1: a value with honest noise, not precision. verify_r terms are summed with
find_hit costs of 16-141 wb and enter costs of 5-1097 wb (window 2); any l1/c1 price in [-0.3, +0.3] wb leaves
every pick unchanged. 0 +/- 0.12 wb is sufficient.

Recommendation: (b). It records what was measured (the fused compare costs nothing over its load, bounded by
two windows), needs no new window, and the class fact is checkable from the census/objdump rather than inferred
from the sign. Side note: rev 1.4's D149 trigger for r_max_e6 ("re-derive on the first window timed with rev
1.4's base") has fired with window 2; r_AA over the eight near-zero rows is 15597..56070 (max w1.p50 56070 vs the
pinned 53751), bin/raa.py.

## 4. The other 34 rows (38 in all; the brief said 36), window 2 vs window 1 (w1_vs_w2.txt; est at each run's own commit)

Sound. Every row that both windows priced agrees within its noise: |difference| / sqrt(n1^2 + n2^2) <= 0.69 on
all 34 (largest: find_hit.pair.periodic.alt.1024 -4.4 %, 0.69; find_byte.libc -2.5 %, 0.68). byte.libc now
passes (38049, noise 609 = 1.6 % vs 3.3 % in window 1). The priced verify rows (w2, w3, cn) moved -0.5..-5.6 %,
all within noise: R14-1's base change did not shift them (window 1's prediction of a ~1 % low bias removed by V3
did not materialise, consistent with section 2: both bases are un-fused loads, as are those arms' first loads).
Weak spots, honestly priced and not refusals:
- find_hit.walk.random.one.1024 / .256: noise 52 % / 42 % of value (bimodal note), as in window 1.
- find_hit.pair.periodic.alt.1024: noise 1.0e6 -> 5.5e6 (6.6 %), one launch low.
- verify w1.p50 is priced by the plain NULL rule (trimmed six positive) at 0.039 wb with noise 0.042 (bimodal
  note); w1.p0, c2.p0, c2.p50 sub-resolution at 0.021 / 0.026 / 0 with noise 0.054-0.086. These are the same
  ~0 compares; under the section-2 reading w1/c2 are "separate load + one and", ~0.02-0.03 wb over the base.
- The box-state note fires on every job's control (0.65-1.78 % splits); drift kept on all jobs.
