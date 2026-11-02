# Bench request DRAFT: the official verdict on the built vrun SIMD family

Draft by the memfn kit (lane vrunreqd, 2026-11-02) for the pcrec manager to
relay to pcrec-bench (D78: main writes the bench's inbox; the kit never writes
to pcrec-bench). It stands alone: the bench needs nothing else to act on it.
Shape and gate rule follow `setfind_bench_request.md` revision 2 and
`setfind_bench_corrigendum_I148.md` §1. Authority: Frank's go to the kit,
2026-10-29 (`memfn/docs/responses.md`, the notice "Frank's go to the kit
(direct): expand the SIMD layer"), item (1): "the official verdict on the built
vrun family (14 CANDIDATE lines in tests/memfn/simd_accept.tsv: w16/w32, kb,
trim, pad, Zen 1 + Zen 4) is taken at the next cleared timing window, via main,
per D144 add. 4". The bar is `integration.md` §R4.9.6; the measurement regime is
§R4.9.5 (tier O). Status: DRAFT, nothing here is a reading.

## 0. Read this first: the evidence is older than the scalar layer

The kit's only timing of this family is job 640 (lane rq4h's harness, Zen 4
7700X, 2026-11-01), tier U: unofficial, directional, the kit's own driver. It
measured pcrec tree `6e0789d07`. That tree PREDATES D172 S3 (abi 92), which
moved the scalar layer at 751 cover sites and 25 pair sites (responses.md,
2026-10-29, "R-29 / D172 S3"). So job 640's OFF arm is NOT the current scalar
layer, and D147 requires SIMD to beat the CURRENT scalar layer. Job 640 is
therefore a reason to ask, never a verdict, and none of its numbers below may be
read as the answer for current main. The official run builds from current main
(`657e23231`, abi 94, or a later commit main pins), both layers (SIMD-off and
SIMD-on), on both target boxes. Nothing in this request changes pcrec's
emission; the arms differ only by flags.

## 1. What changes, in one paragraph

With `-fmemfn-simd` OFF (today's default) a pcrec artifact looks for the next
place a required literal run can start by pcrec's own scalar search forms, or by
a libc call such as `memchr`. With `-fmemfn-simd` ON, at sites the kit admits,
the kit emits a vector form instead (the "vrun" family): it loads 16 bytes (SSE2,
"w16", the `-march=x86-64` level) or 32 bytes (AVX2, "w32", the `-march=x86-64-v3`
level) at a time, compares one or two chosen positions of the run in every
lane at once (the second position is "kb", w32 only), and then checks only the
lanes that survive. Three options refine the check of a surviving lane: "trim"
verifies only the run positions the filter did not already test, "pad" verifies
a 3- or 5-to-7-byte run with one masked word in the main loop, and "kb" is the
second filter position. The switch is OFF by default and stays OFF unless this
reading accepts the rows (R4f is its own ruled event). The kit's Zen 4 numbers
(tier U, older tree, §0) show it faster at most cells and slower at a few,
named in §6; whether that holds on current main and on Zen 1 is what the bench
is asked to decide.

## 2. What is judged: the CANDIDATE lines

`tests/memfn/simd_accept.tsv` holds 14 CANDIDATE lines (state CANDIDATE, tier
`unofficial`, every digest column `-` until a timing run writes it). Each is one
row x level x CPU class, and the verdict rules on each line separately:

| row | levels | classes | what it is |
|---|---|---|---|
| vrun-w16 | w16 | zen1, zen4 | the SSE2 vector form (`-O2 -march=x86-64 -mtune=generic`) |
| vrun-w32 | w32 | zen1, zen4 | the AVX2 vector form (`-O2 -march=x86-64-v3 -mtune=generic`) |
| vrun-kb | w32 only | zen1, zen4 | the second filter position; its w16 lines were removed with R-16 because the w16 helper reads no second position, so its deny moves nothing there |
| vrun-trim | w16, w32 | zen1, zen4 | the trimmed per-candidate verify (R-14) |
| vrun-pad | w16, w32 | zen1, zen4 | the padded main-path verify (R-14 follow-up) |

That is 2 + 2 + 2 + 4 + 4 = 14 lines. A line becomes ACCEPTED, REJECTED or stays
CANDIDATE by §5; the kit (not the bench) edits the file from the bench's
transcript (§R4.9.6: the digest columns are written by a timing run, never by
hand).

## 3. Which cells

The bench names its own cells; the kit does not know the bench's current cell
list (Q1). What the kit can state is which SITE SHAPES must be covered, from the
pre-registered population rule (§R4.9.6 item 3: the movers are the pcrec-side
text diff `-fmemfn-simd` against `-fno-memfn-simd` over the corpus and the
bench's patterns, counted as distinct site shapes; every bin needs at least one
official cell, a bench pattern or a synthetic witness).

1. **The mover population, from main.** Main supplies the list of every bench
   cell whose artifact differs between `-fno-memfn-simd` and `-fmemfn-simd` at
   the pinned commit (the mover census; the bench's own patterns, not the kit's).
   This is the target population. A bench cell whose two artifacts are
   byte-identical is a NULL cell: it feeds the noise band (§4), never a verdict.
2. **The kit's twins of the job 640 cells** (patterns the kit used; they are the
   kit's cells, not bench cells, and the bench is asked whether it has or can
   build twins, Q2):
   - `(?i)azqb` (kit id `sp`, engine auto): rare letters at both filter
     positions, the regime where `memchr` is strongest. KNOWN QUESTION (§6).
   - `(?i)x/1234` (kit ids `n04` engine auto and `v17` engine vm): KNOWN
     QUESTION (§6).
   - `(?i)cat` (`mi`) and `(?i)union.*?select.*?from` (`us`): the R-1 evidence
     cells, vrun movers (job 640 reports bench subjects for these two, from the
     `cap` and `syn` bench sets, as `bench/cap-t-*` and `bench/syn-t-*`).
   - the 18 default-engine and 19 `--engine=vm` mover patterns of job 640
     (`m01`-`m19` without `m18`, `v01`-`v19`): the per-call cost (§6) shows on
     them. The exact pattern list is `docs/design/memfn/probes/rq4/cells.tsv`.
   - `(?i)cat` with KA's byte injected as common filler (`kb`): KB's own case.
   - the non-vrun controls `xyzzy`, `\d+xyzzy`, `(?i)\d+ab/cd`, `[a-z]*select[a-z]*`
     (auto) and `xyzzy`, `(a|b)+xyzzy`, `(?i)\d+ab/cd` (vm), the pattern
     `it\Nm`, and the userpass pattern (`wild-secrets-username-password-pair`):
     byte-identical OFF vs ON in job 640, kept as the null population.
3. **The real-subject cells the bench already has.** Every bench cell in the
   mover list of item 1, on its own subjects, in the bench's own regimes. The
   kit cannot name them (Q1). The bench is asked to include any cell whose
   required run is 3 to 8 bytes or whose subject is short (the per-call cost is
   largest there, §6).
4. **The named loss cells explicitly, at both levels:** `sp`, `n04`, `v17` on
   the isolated whole-subject scan ("gate/tail") and the find-all sparse
   regime, and every `pc16` cell (§6). They are cells of the gate like any
   other; naming them only makes sure they are read and reported, not hidden.
5. **The regimes, from §R4.9.5 item 7 (job 640 used these names):**
   - throughput: gate/tail (one call from 0, the only hit at the end) and
     find-all sweep sparse (a hit about every 16 KiB) and dense (about every
     256 B), at 64 KiB and 1 MiB;
   - per call: `pc16`, `pc64`, `pc256`, `pc1024` (one call from 0 on each of up
     to 256 consecutive chunks of the sparse 64 KiB subject) and `short75`
     (the capability set's 75 short subjects);
   - density: the witness planted every 8, 16, 32, 64, 128 or 256 bytes in a
     64 KiB subject (job 640 `space8`..`space256`);
   - bench: the bench's own subjects at 64 KiB and 1 MiB.
   The bench has no per-call span cells of its own today (§R4.9.5.1 item 4 asked
   for a span-ladder subbench); Q3 asks whether one exists now. Until it does,
   the per-call leg is read from the kit's driver on the bench box and labelled
   tier U.

## 4. Which arms

All arms are ONE pinned pcrec commit; they differ only by flags, so a difference
is the form and nothing else. Recipe at each level L: `-O2 -march=L
-mtune=generic`, never `-march=native` (§R4.9.5 item 4, r9 M-4), so one build
runs on both CPUs. L is `x86-64` (w16 live) and `x86-64-v3` (w32 live). Each arm
at each L is its own binary, interleaved ABAB within a launch.

| arm | flags | what it is |
|---|---|---|
| OFF | `-fno-memfn-simd` | the CURRENT scalar layer at that commit and level; the comparator |
| ON | `-fmemfn-simd` | the full family: w16 at `x86-64`, w32 (with its w16 rung) at `x86-64-v3` |
| DENY-pad | `-fmemfn-simd --memfn=no-vrun-pad` | ON without the padded verify |
| DENY-trim | `-fmemfn-simd --memfn=no-vrun-pad,no-vrun-trim` | ON without pad and trim (R-13's whole-run verify) |
| DENY-kb | `-fmemfn-simd --memfn=no-vrun-kb` | ON without the second position (changes nothing at `x86-64`; skip it there) |
| DENY-w32 (v3 only) | `-fmemfn-simd --memfn=no-vrun-w32` | the narrower form displaced by w32 (§R4.9.5 item 4 DISPLACED; w32 must not lose to the w16 it pre-empts, §R4.9.6 item 2) |
| A/A twin | OFF and ON, each a second build with a DIFFERENT CODE LAYOUT | the bench's existing align64 placement twin (corrigendum §1), one per set per arm; measures the floor including layout noise |

Job 640 used the arm names DEFAULT, NOPAD, FULL, KBDENY, FULLKB, OFF with the
same flags (its `table.md` header). The `--memfn=` names above are job 640's,
read from its header; the bench should confirm `--list-axes` prints them at the
pinned commit (Q4). Any pair of arms is compared only after the pcrec-side
check that a DENY artifact equals the one it should equal (a lone row's deny
byte-identical to OFF where it moves nothing) is shown by main; the bench does
not need to check it.

**Both layers (D147).** The OFF reading of this family is zero movers against
the parent commit (main's I2 gate, not the bench's). The ON reading is the
verdict. The comparator is OFF at the same commit and the same `-march`.
Where OFF is a glibc-backed `memchr` body, glibc picks that `memchr` by CPU,
not by `-march`, so the comparator runs at each CPU's own glibc tier
(§R4.9.6 item 1, r9fu). The bench reports each box's glibc version (Q5).

**Boxes.** ubuntubudu (Ryzen 5 1600, Zen 1: AVX2 executed as 2 x 128-bit, no
AVX-512) AND the dev box (Ryzen 7 7700X, Zen 4: AVX2 and AVX-512), because w16
and w32 are each judged on both (§R4.9.5's table; D144 addendum 4; the Zen 1
2 x 128 execution is exactly what the bench must show). AVX-512 (w64) is not
filed and not asked. The Mac is not asked (aarch64 has no level in this
family). Main schedules the boxes and the timing window (one heavy run at a
time, a window cleared with Frank and clear of the 20:00-01:00 hold).

## 5. The gate rule, per CANDIDATE line

This is the merged rule of the corrigendum, written for this family. The
bench's own regression rule wins where it has one, and the bench should say so
in its result (Q6).

A cell (one cell, one regime, one box, one level) **LOSES** iff ALL hold:

1. **trials agree:** the bench's trial-agreement rule passes for both arms
   (a failing cell is reported, re-run once, and if still disagreeing is
   UNJUDGED, not a pass);
2. **ratio:** median(ON) / median(OFF) > 1 + F, where F = max(the bench's
   standing per-cell spread for that cell, regime and box, the A/A spread
   |median(A/A twin) / median(arm) - 1| from a layout-perturbed twin in the
   same window). Throughput cells only; the 0.05 floor is the bench's call
   (Q6), the kit does not impose one;
3. **disjoint:** the ON and OFF trial [min, max] ranges do not overlap
   (overlapping is a TIE whatever the ratio);
4. **absolute, on EVERY cell:** median(ON) - median(OFF) exceeds the absolute
   A/A delta from the same source as F. For a per-call cell (a few nanoseconds)
   this IS the criterion: the delta is judged in ns against the absolute A/A
   delta, never as a percentage (D144 addendum 1). A median shift outside the
   null band at a below-reach per-call cell is a LOSS even if each launch alone
   sits inside it (§R4.9.5 item 6);
5. **reproduced:** a cell meeting 1-4 is re-run immediately (same window, same
   binaries) and LOSES only if the re-run meets 1-4 too; otherwise it is a TIE
   marked "not reproduced", with both readings.

A cell **WINS** symmetrically (ratio < 1 - F, delta beyond the A/A delta, ranges
disjoint); a win needs no re-run, the gate reads losses only.

**The noise band is the null population** (§R4.9.5 item 5): the cells whose OFF
and ON artifacts are byte-identical, per regime and per CPU class, in the same
run and binary set. Their ON - OFF delta distribution is the placement-plus-noise
band. The kit's own analysis took the maximum over null cells as the floor
(`UNMEASURED DEFAULT:`, job 640 header); the bench is asked what it uses (Q6).
A null band measured on 7 or 8 cells is thin: the bench should report n beside
every band.

**A line is decided so (§R4.9.6):**
- ACCEPTED at level L on class C iff the pre-registered target cells improve
  beyond the band by at least a stated minimum effect on at least one official
  box running L, AND no cell in the pre-registered population loses on ANY
  official box running L (throughput and per-call alike, below-reach cells
  included). A null on one box with a win on the other is accepted and recorded
  (Zen 1's 2 x 128 may null w32 per call). The minimum effect is
  `UNMEASURED DEFAULT:` an absolute ns or ns/B figure per regime until the null
  distribution gives it; the kit proposes none (Q7).
- Lines are per class, but a loss on ANY official box that executes L blocks
  ACCEPTED at L: both boxes compile the same bytes for one `-march`, so the
  remedy is per level (the level is removed from the rungs, or the row's
  admission narrowed by a stated site fact, or the row is REJECTED).
- vrun-w32 additionally must not lose to DENY-w32 on any box running both.
- vrun-kb, vrun-trim and vrun-pad are read against their own deny (the
  difference they add), AND the family as a whole against OFF; a sub-option that
  loses to its deny is reported even when the family beats OFF.
- A wrong answer anywhere is a defect, not a reading (§R4.9.6): the bench
  reports it at once.

**The gate.** The family PASSES at (level, class) iff no cell LOSES there; a
cell that loses returns to the kit (§6). Wins and ties are reported too: the
decision record needs all three. The outcome is a per-line table for the 14
lines, not one verdict.

## 6. The known questions, to answer and not to hide

Both come from job 640 (tier U, Zen 4, tree `6e0789d07`, the OLD scalar layer
as OFF). They are not evidence of a loss on current main, only the places the
kit expects the bench to look hardest. Job 640 totals, ON - OFF against the
cell's null band (comparisons counted per pair): throughput 184 wins / 2 nulls /
12 losses at `x86-64` and 192 / 4 / 4 at `x86-64-v3`; density 190 / 0 / 0 and
188 / 1 / 0; per call 133 / 9 / 28 and 126 / 7 / 30; bench subjects 3 / 0 / 0
and 4 / 0 / 0. Median OFF/ON speed-up for the sweep and gate regimes 2.33x at
`x86-64` and 4.41x at `x86-64-v3`; for the density ladder 1.86x and 1.78x; for
per-call 1.33x and 1.30x. Of 74 losses past the floor, almost all are the first.

**Q-A. The per-call cost at the shortest span (`pc16`).** Most `pc16`
cells lose at both levels, +0.3 to +1.4 ns above a floor of 0.22 ns (`x86-64`)
and 0.33 ns (`x86-64-v3`): 57 of the 74 losses past the floor (27 at `x86-64`,
30 at `x86-64-v3`), on `mi`, `kb` and many of `m01`-`m17` and `v01`-`v19`. At 16 bytes the vector form pays its entry tests and
loses to the scalar form; at 64 bytes and up it wins. The kit's account (not
yet verified on a current tree): the dispatch prefix is the cost (`[D155]`).
What the kit will do with a reproduced `pc16` loss is in §7. The bench is asked
to report, per cell, the span at which ON stops losing to OFF (Q8).

**Q-B. The sparse-pick loss at `x86-64` (w16): `sp`, `n04`, `v17`.** On
gate/tail and sweep/sparse, w16 against OFF: `sp` +70% to +96% (all four
gate/tail and sparse cells, plus `pc1024` +2.18 ns); `n04` +53% to +72%; `v17` +5% to
+23% at the gate/tail and sparse cells at `x86-64`. `n04` also at `x86-64-v3`: +14% (gate
64 KiB), +3% and +9% (sparse). `v17` at `x86-64-v3` loses at gate/tail 64 KiB
(+18.5%) and `pc16`; `sp` has no `x86-64-v3` loss. `sp` and `n04` win the dense
regimes (`sp` sweep/dense -30% and -33% at `x86-64`). The kit's untested guess
is that OFF at these sites is a glibc-backed `memchr` on rare letters or an
unusual first byte, the regime where glibc is strongest (§R4.9.7.1), and
that w16 (16 bytes per step, no `memchr` tail) cannot match it. That is a
hypothesis. The current OFF arm may differ, since S3 moved the scalar layer, so
the first thing the run answers is whether the loss exists on current main.

## 7. What the kit does with each outcome

- **WIN or TIE** on every cell of a (level, class): the line is ACCEPTED (if
  the target cells meet the stated minimum effect) and the kit writes the
  bench's run id, commits, gcc and glibc into the `simd_accept.tsv` line.
  ACCEPTED is what R4f (a default flip) reads and what any "faster" wording
  needs; nothing flips here.
- **LOSS, reproduced:** the cell returns to the kit with its regime, box, level,
  both medians, the A/A delta and the subject facts (§8). The kit decides, in a
  follow-up with its own tier-U alpha and its own submission: remove the level
  from the row's rungs, narrow the admission by a stated, measured site fact,
  or REJECT the row (the line stays as the record). The `pc16` cost and the
  sparse `sp`/`n04`/`v17` loss are expected candidates for the first two. The
  route a losing bin takes is not a site fact the kit can read, so a losing
  route bin blocks the level or needs a pcrec-stated fact (a request to main,
  §R4.9.6 item 3).
- **Loss on one box only:** blocks ACCEPTED at that level (remedy per level), and
  is reported with the other box's reading; the kit cannot key on the box.
- **UNJUDGED or "not reproduced":** reported as such, never counted as a pass;
  the kit may ask for one more window.
- **Correctness:** `make test`, the answer sweep per level, G2 per level,
  ASan/UBSan over the movers are main's and the kit's, CPU-independent, and not
  asked of the bench. A wrong answer in a bench cell is a disaster (D144 item 3):
  the row is removed at once.
- **Result file:** the bench's transcript names the pins of §9, and the kit's
  verdict is written from it into `tests/memfn/simd_accept.tsv` (state, tier
  `bench`, run id, commits, the digests the run writes).

## 8. What to report beside each cell

The kit supplies the pattern and, where known, the filter positions; the bench
measures from its subject (as `setfind_bench_request.md` §5):
- the median and trial [min, max] of each arm, the A/A twin's median, F (and
  where it came from), the verdict WIN / TIE / LOSS / UNJUDGED;
- the null band per regime and per CPU class, with n, and `|DENY - OFF|` on the
  movers beside it as a second same-text reading;
- the candidate density at the first filter position and the hit spacing, in
  ppm and in bytes, per subject; the subject size, and whether the timed loop
  rescans the same subject (the 64 KiB branch-predictor caveat of
  `setfind_bench_request.md` §5 applies to a vector form as well);
- for a per-call cell, the span.

## 9. Pins and the pre-registration

Main fixes these before the run and the bench records them (§R4.9.5.1 items 1
and 5):
- the pcrec commit (current main, `657e23231` abi 94 or later, one commit for all
  arms); the kit is in tree at the same commit; the bench commit;
- per box: the CPU model and class (`zen1` / `zen4`), governor, boost, glibc and
  gcc as the box reports them (asked, never assumed), the load1 at start and
  before each launch, and the bench's pinning and idle discipline (the kit's own
  tier-U discipline was `taskset` on one core with its SMT sibling idle,
  sibling-busy readings above 5% discarded: `UNMEASURED DEFAULT:` all of it; the
  bench's own discipline wins);
- the pre-registration, committed BEFORE the run
  (`docs/design/memfn/probes/simd/<batch>/prereg.md`): the target cells with
  predicted deltas, the bins, the controls, the minimum effect (Q7). Main
  writes it from the mover census; this request does not.
- statistic: each timed loop at least about 50 ms, the min of 3 loops per
  launch, the median of 3 launches, with the number of cells tested printed
  (the multiple-comparison exposure). These are the kit's tier-U figures and
  `UNMEASURED DEFAULT:`; the bench's own statistic wins where it has one.

## 10. Questions for the bench

- **Q1.** Which bench cells are in the mover list at the pinned commit, and which
  of those are short-subject cells or have a 3 to 8 byte required run? (Main
  supplies the list; the bench says what it adds.)
- **Q2.** Can the bench host the kit's twin cells of §3 item 2 (`sp`, `n04`/`v17`,
  the `pc16`-to-`pc1024` span ladder, the density ladder, the null controls) as
  a subbench, or should the kit's driver run on the bench boxes labelled tier U?
- **Q3.** Does a per-call span-ladder subbench exist now (asked at §R4.9.5.1
  item 4)? If not, is one feasible for this window?
- **Q4.** Can the pcrec testee adapter pass `-fno-memfn-simd`, `-fmemfn-simd` and
  `--memfn=no-vrun-pad`, `no-vrun-trim`, `no-vrun-kb`, `no-vrun-w32` through to
  pcrec at `-march=x86-64` and `-march=x86-64-v3`, or must main hand over
  separately built testees per arm and level?
- **Q5.** What do the two boxes report for governor, boost, glibc and gcc, and
  what is the bench's pinning and idle discipline? (Never assumed.)
- **Q6.** Does the bench have a standing per-cell spread to use as F, a trial
  agreement rule, an A/A (align64 placement twin) per set, and a regression
  floor of its own (the 0.05 in I-148)? The kit asks the bench to state which it
  used in place of §5 where they differ.
- **Q7.** What minimum effect should a target cell show for a WIN to count toward
  ACCEPTED? The kit proposes no number (no tuning constant presented as settled);
  main's pre-registration sets one from the null distribution.
- **Q8.** Can the bench report, for the `pc*` cells, the span at which ON stops
  losing to OFF on each box?
- **Q9.** Is a window available on both boxes, and does the Zen 1 run (ubuntubudu,
  the box the bench lives on) and the Zen 4 run (the dev box) fit one window
  shape each, or does each need its own slot request?
- **Q10.** Does the bench see any wrong-answer difference between arms on any
  subject (reported at once)?

## 11. What the kit sends back to main after the reading

A verdict table per box and level: cell x regime x arm, the medians, F and its
source, the null bands with n, WIN / TIE / LOSS / UNJUDGED; the 14 lines'
outcomes (ACCEPTED, REJECTED, stays CANDIDATE) with the reason; and for each
LOSS the corner it sits in (the per-call prefix cost, the sparse-pick glibc
case, or a new finding). The kit also records whether job 640's tier-U result
held on the current scalar layer, so the older figures can be retired.

## 12. Standing questions (docs/design/CLAUDE.md)

1. *Measurement regime:* RELEVANT. Stated in §3 (throughput and per call,
   sparse and dense, 64 KiB and 1 MiB), §4 (flags, boxes, compiler recipe) and
   §8 (rescanning). A different regime can flip a decision: the per-call and
   sparse cells are exactly where job 640 lost.
2. *Independent control:* RELEVANT. The null population (§5) is the control for
   the noise band, drawn from byte-identical artifacts in the same run; the
   A/A twin is the layout control; the DENY arms are same-text pairs. The
   comparison is the bench's reading, not the kit's driver.
3. *What moves when data is regenerated:* NOT RELEVANT here. This request
   generates no table, calibration or stamp; the only file it later changes is
   `tests/memfn/simd_accept.tsv`, by a timing run, and that edit moves no
   emitted byte (no abi event, no spec hunk).
