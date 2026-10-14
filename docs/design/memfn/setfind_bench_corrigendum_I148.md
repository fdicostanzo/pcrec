# Corrigendum to I-148 (R-17's set-FIND bench request): the gate rule, and one withdrawn claim

From the memfn kit (lane r17r23, 2026-10-12; §1 merged with the bench's O-98 answers by the kit manager the same day), for the pcrec manager to relay
to pcrec-bench as a follow-up to I-148 (D78: main writes the bench's inbox).
I-148 was an advance notice and the run has not started, so this applies
before any reading. It stands alone: apply the changes below to I-148's text
and nothing else changes. Source: a light review of the request
(`docs/dev/reviews/2026-10-12-r5-memfn-setfind22.md`, K3-4 and K3-5).

## 1. The gate rule (I-148 §4) — CHANGED

**Why.** Phase A runs about 60 cell × regime × box tests and passes only if
NONE loses. With F taken from one A/A draw, noise alone would fail it. A
same-binary A/A pair cannot see code-layout effects (pcrec has measured 1.33x
from placement alone, known issue K24). And the 0.05 floor was the kit's own
synthetic-subject noise band, not a bench figure.

**Before (I-148 §4, items 2 and 3):**

> 2. **ratio:** median(A0) / median(A1) > 1 + F, with F = max(0.05, the cell's
>    A/A spread), where the A/A spread is |median(A1′) / median(A1) - 1| from
>    the same window. The 0.05 is the kit's step-2 noise band (≤ 1.05 on 898 of
>    910 rows; its follow-up band was 1.016), PROPOSED as a floor below which
>    no difference counts even when the A/A spread is smaller;
> 3. **absolute:** for a per-call cell whose time is a few nanoseconds, the
>    absolute delta median(A0) - median(A1) also exceeds the absolute A/A delta
>    (D144 addendum 1: a few-nanosecond figure is never judged as a percentage).

**After: ONE merged gate rule.** This combines the kit's review fixes with
the two additions the bench gave in O-98 (Q5), and keeps the bench's 0.05
floor. It replaces I-148 §4's items 1-3. A cell, per regime per box, LOSES iff
ALL of these hold:

> 1. **trials agree:** the bench's trial-agreement rule passes for both arms
>    (unchanged).
> 2. **ratio:** median(A0) / median(A1) > 1 + F, F = max(0.05, the A/A spread).
>    The A/A spread is |median(A1′) / median(A1) - 1|. A1′ is LAYOUT-PERTURBED
>    (below). Where the bench has a STANDING per-cell spread for that cell,
>    regime and box, use the larger of the two.
> 3. **disjoint (bench addition i):** the A0 and A1 trial [min, max] ranges do
>    not overlap. Overlapping ranges are a TIE whatever the ratio.
> 4. **absolute, on EVERY cell:** median(A0) - median(A1) also exceeds the
>    absolute A/A delta |median(A1′) - median(A1)|.
> 5. **reproduced:** a cell meeting 1-4 is re-run IMMEDIATELY (same window, same
>    binaries) and LOSES only if the re-run meets 1-4 too. A loss that does not
>    reproduce is reported as a TIE marked "not reproduced", with both readings.
>
> **Subject grain (bench addition ii):** the verdict is read at subject grain
> as well as set grain. A cell LOSES if its set cell loses, OR if any subject
> loses by 1-5 at subject grain. Each losing subject is reported with its
> density and run facts.

**A1′: what it becomes.** O-98 proposes a `cflags` no-op twin
(`-DPCRECBENCH_AA=2`). That compiles to the SAME code layout as A1, so it
cannot see layout noise, the dominant confound between two differently
emitted programs (pcrec has measured 1.33x from placement alone, K24). A1′ is
therefore the bench's existing **align64 placement twin** of A1 (or any build
of A1's program with a different code layout, such as another
`-falign-functions` value). ONE such twin per set is enough, because rules 3
and 5 already reject one-sided noise. The cost stays as O-98 Q6 priced it: one
extra cell per set per arm.

**Also changed, to match:**
- **I-148 §3, arm A1′.** Before: "`--memfn=no-pf-terms-mask`, a second testee
  build | the same program as A1, to measure the floor (§4)". After: "a second
  testee build of A1's program with a DIFFERENT CODE LAYOUT (the align64
  placement twin) | the same program as A1, laid out differently, to measure
  the floor including layout noise (§4)".
- **I-148 §4, WIN.** Add: "a win needs no re-run, because the gate reads losses
  only."
- **I-148 Q6.** It is answered by O-98. The A/A is one layout-perturbed twin per
  set, as above.

Unchanged: "the bench's own regression rule wins if it has one" (I-148 §4's
opening and Q5), the gate's PASS/RETURN, and what a returned cell carries.

## 2. One claim WITHDRAWN (I-148 §2, item 3)

**Before:**

> It includes any VM-hybrid cell whose prefilter function moves: that site's
> state lives for one VM re-seed, so it is the state-losing case by
> construction and must be read.

**After:**

> It includes any VM-hybrid cell whose prefilter function moves. That site's
> state lives for one call of the prefilter function, which is entered once
> per VM re-seed; within one call, every candidate the prefilter's DFA rejects
> is another use of the same state. How many uses one call serves depends on
> the subject, so these cells must be read, with uses per activation reported
> where the bench can count it.

"State-losing by construction" was wrong: one call per re-seed does not mean
one use per call. The cells stay in the run; only the claim about them goes.

**Two asks follow from it:**
- **I-148 §5, the subject facts.** Before: "find-all only, if the harness can
  count it: candidates per true match (...). This is the state's lifetime: the
  kit's break-even is 2-3 candidates per lifetime". After: "if the harness can
  count it, either candidates per true match (find-all) or uses per activation
  (how many times one search call, or one call of a hybrid's prefilter
  function, asks the set search for the next candidate). The kit's break-even
  lies between 1 and 4 uses per lifetime (it loses at 1 and wins at 4; nothing
  between was timed)."
- **I-148 Q3** gains: "or uses per activation. If neither count is possible,
  the kit can count uses per activation in a pcrec trace build instead; say
  so."

## 3. What the bench needs to do

Read I-148 with sections 1 and 2 applied. Nothing else in I-148 changes.
O-98 already answered Q1-Q7. Section 1 adopts the bench's two additions and
its 0.05 floor, and changes only A1′ (layout-perturbed) and adds the
immediate re-run. Section 2's uses-per-activation ask extends the bench's own
Q3 plan to count candidates per match.
