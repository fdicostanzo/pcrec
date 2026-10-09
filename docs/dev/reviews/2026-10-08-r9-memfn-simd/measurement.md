# R-9 D6 panel, lens: MEASUREMENT REGIME AND ACCEPTANCE

Critic: read-only, 2026-10-08. Subject: `integration.md` rev 4.9 §R4.9 and
`docs/dev/lanes/r9d_report.md` (worktree r9d). Judged against Frank's two
2026-10-08 rulings, which postdate the design:

- **R1** unofficial short-form benches may happen anywhere (kit, dev box,
  Mac); an OFFICIAL acceptance verdict is a planned pcrec-bench run, via the
  pcrec manager (D78).
- **R2** the bench box `budu-ryzen1600` (= ubuntubudu) is a Ryzen 5 1600
  (Zen 1; AVX2 as 2x128-bit; slow microcoded PDEP/PEXT; no AVX-512). It is
  the performance measure. The dev box is a 7700X (Zen 4).

Also read: D144 (+add. 1), D147 (+add. 11), D149, learnings §3 (K35),
R-1's tables as quoted in §R4.9.7.

## Summary

The design's regime is internally careful (one binary per arm, same-`-march`
arms, DENY floor, reach derived from the level) but it is built around the
wrong verdict box. Q-R9-1 recommends the dev box (Zen 4, v4-capable) as the
verdict box and demotes the Zen 1 bench box to a "second box" whose
disagreement is "an issue row". Under R1/R2 that is inverted: the bench CPU
is the official class and the dev box is the unofficial tier. Everything that
hangs on the verdict box (the record schema, C19's box-dependent half, the
D149 "MEASURED" label, RQ-4/RQ-5 ordering) must be re-hung. The rest of the
bar is mostly salvageable; its weak points are the floor/band statistic,
the bin rule, and C19.

Counts: 1 BLOCKER, 10 MAJOR, 5 MINOR.

## Proposed two-tier regime (the fix the findings below point at)

This is largely D144's own structure (item 1 alpha merges; item 2 batch gate
on the bench is FINAL approval; item 3 regressions become issue rows),
which §R4.9.5 collapsed into one tier.

**Tier U, unofficial** (kit harness, any box; "short-form bench" in R1's
words). Sub-labels so a reading names its class: U0 Mac (aarch64, floor text
only), U1 dev box 7700X (Zen 4), U2 ubuntubudu via a manager slot with the
kit harness (SAME CPU as the bench, NOT the bench harness). What U decides:
- correctness, CPU-independent and decisive: answer sweep per level,
  G2 per level, ASan/UBSan, I2 zero movers, C9-x86, C18, C-SEL. The dev box
  is the only box that executes v4, so it owns v4 correctness.
- D77 triggers (a cell justifies building) and D144 item 1 alpha: a row may
  MERGE behind the default-OFF switch as `CANDIDATE` on a U1/U2 alpha. SIMD
  is opt-in, so an unofficial merge costs nothing a revert cannot undo.
- which constants and which rows to SUBMIT (sweeps of reach, unroll, KB run
  here first, to cut the bench arm count).
- a VETO on submission: a U1 loss past floor means do not spend a bench
  slot, unless a stated Zen 1 hypothesis says otherwise.
- U NEVER grants acceptance, never labels a constant MEASURED, never sets a
  default, and is never quoted as a verdict (D144 add. 1's "directional" rule
  already says this for the Mac; extend it to U1).

**Tier O, official** (a planned pcrec-bench run, pre-registered, scheduled
by the pcrec manager through the D78 inbox, in the bench's window). What a
submission carries:
1. Pins: pcrec commit, kit commit, bench commit; compiler, glibc and
   governor as the bench box actually has them (ask pcrecdev2, memory
   `pcrec-ask-bench-dev`; they are read-only to us, the design must not
   assume them).
2. Testees per row, per live level L in {default x86-64, x86-64-v3}, each a
   separate binary built from the pcrec-emitted artifact:
   OFF@L (`-fno-memfn-simd`), ON@L, DENY@L (`--memfn=no-<row>`, text
   asserted identical to OFF before submit; it is the same-text control, the
   floor arm), DISPLACED@L for w32 (`no-vrun-w32`). Each testee's recipe
   RECORDS `-O2 -march=<named level> -mtune=generic`. Never `-march=native`:
   native on Zen 1 and Zen 4 are different binaries with different tuning
   and different macro sets, so the two CPUs would not run the same bytes.
   A named level lets one build run on both CPUs.
3. Cells: the FULL capability set of movers (not proposer-chosen evidence
   cells), including the two evidence cells (union-select, mod-i), the
   exact-window bin if any bench pattern reaches it, and the non-mover
   artifacts as the null population (below). Per-call spans pc16..pc1024
   are R-1 harness cells; the bench does not have them. Submission
   therefore includes a request for a small "span ladder" subbench (same
   patterns at 16/32/64/256/1024 B and a hit-spacing ladder), or the per-call
   leg stays unofficial and is labelled so.
4. A pre-registration block (the house prediction-table shape): predicted
   deltas per cell, the bar's thresholds, which cells are controls, which
   sweeps are in. Written before the run.
5. Arm budget: sweeps (reach {1,2,4}x, unroll 1/2/4x, KB) are run at U1/U2
   first; the bench gets the best candidate plus the incumbent, not the
   full cross product (the 20+ testee product would not fit a night window).

**Noise band from the null population (replaces the alignment-flag relink
as the main control).** Every non-mover artifact in the set has
byte-identical text between OFF and ON (floor rule). Its ON-minus-OFF delta
distribution IS the placement-plus-noise band, measured at the same scale and
in the same binary set, on the official CPU. This is how b1ledger read
program-identical artifacts as the null control (56/187, with regressions of
+8.46% on identical `__text`). Movers are judged against that distribution,
not against one relink.

**Acceptance reads both CPUs asymmetrically.**
- Official verdict (bench, Zen 1): the bar of §R4.9.6 items 1-2 must hold
  there. A WIN is required on the official CPU. A LOSS on the official CPU
  is a reject for that row x level (or a narrowing of its APPLIES), whatever
  the dev box says.
- Dev box (Zen 4, U1): a loss past floor does not reject an
  official-accepted row; it is recorded in the record and filed as an
  issue row (D144 item 3 shape), because Frank's ruling makes the bench the
  performance measure. A dev-box win alone is never acceptance.
- Levels the bench CPU cannot execute (v4, any w64 row): status
  `UNOFFICIAL-ONLY`. Eligible for opt-in use and correctness, NEVER for
  R4f default-ON consideration nor for any "faster" claim in spec or docs.
- The record carries a `tier` column and `cpu_class` column (below).

## Findings

### M-1  BLOCKER  §R4.9.5 item 1, §R4.9.10 Q-R9-1, F-R9-4, §R4.9.6 table, RQ-4/RQ-5
**Problem.** The design recommends the dev box as the verdict box and lists
reasons that R2 reverses: "Zen 1 executes AVX2 in halves ... a verdict there
understates the wide levels". That is exactly why Zen 1 is the right
measuring stick: if w32 only wins where 256-bit ops are native, it should
not be accepted on the project's performance measure. F-R9-4 says R-1 is
"not an acceptance verdict on the box that will give verdicts"; under R2,
R-1's CPU IS the verdict CPU and the dev box is the one that cannot give a
verdict. The design also treats ubuntubudu and "the bench" as two things
("ubuntubudu ... stays the batch gate's second box through the bench's wide
reading") when they are one box, and it schedules the bench testees
(RQ-5) "at batch 1's landing", i.e. AFTER acceptance, while RQ-4 (a dev-box
slot) is the gating request. R1 requires the order the other way round.
**Fix.** Replace Q-R9-1 with the two-tier regime above. Rewrite
§R4.9.5 item 1 as "official = pcrec-bench run on budu-ryzen1600, planned via
the manager; dev box = unofficial alpha". Move RQ-5 ahead of acceptance
(rename: bench submission), demote RQ-4 to the unofficial slot, add RQ-6
(bench calendar slot, pre-registration) and RQ-7 (ask pcrecdev2 the bench
box facts). Reword every "verdict box" in §R4.9.6/§R4.9.8 to say which
tier.

### M-2  MAJOR  §R4.9.6 "The acceptance record", `simd_accept.tsv`
**Problem.** The record has one "verdict box" and one "verdict", and "ACCEPTED"
has no states. Nothing distinguishes a row accepted on an unofficial U1
alpha from one accepted on a bench run, so a CANDIDATE can later be read as
ACCEPTED by R4f, by docs, or by the bench note. R1 makes that distinction
the whole point.
**Fix.** Columns: `state` in {CANDIDATE, ACCEPTED-OFFICIAL, STALE,
UNOFFICIAL-ONLY, REJECTED}, `tier`, `cpu_class` (zen1 / zen4 / other), one
line per (row, level, CPU class), `bench_run_id` + bench commit for
official lines, `prereg_path`. C19 and R4f gate on `state`. A row may merge
as CANDIDATE; only ACCEPTED-OFFICIAL feeds default-ON, spec performance
claims, and the "faster than the scalar layer" wording of D147 add. 11.

### M-3  MAJOR  §R4.9.6 bar, §R4.9.10 Q-R9-2, §R4.9.7 filed list (w64)
**Problem.** The bar has no rule for two CPUs that disagree, or for levels
that only one CPU executes. The disagreement path in the design is
"ubuntubudu disagrees past floor -> issue row, not a revert", i.e. the
dev box wins ties. The filed list's w64 trigger ("a probe at v4 showing w64
beats w32") can be satisfied on the dev box alone, and no official verdict
is possible for it (bench has no AVX-512). The same holds for w32 on Zen 1
with 2x128 execution: it may tie w16 per call (R-1 already shows
mod-i pc64 +0.97, `short75` +0.99 across builds on that CPU).
**Fix.** Adopt the asymmetric rule in the two-tier section: bench is the gate
for ACCEPT; dev is a recorded guard-rail. Define `UNOFFICIAL-ONLY` for v4/w64
rows and bar them from any "faster" claim and from default-ON. State that a
`-march=x86-64-v3` user on a Zen 4 box and one on Zen 1 get the same bytes;
if w32 wins on one and ties on the other, that is acceptable (null on the
official CPU is not a loss), but a loss on Zen 1 is not.

### M-4  MAJOR  §R4.9.7 prerequisites, §R4.9.11 RQ-5, Q-R9-2
**Problem.** The design says what the bench should receive (two testees) but
not what an official submission must contain, and R1 says "we need to plan
it". Gaps: (a) no DENY/OFF/DISPLACED/OFF' arms are named as bench testees;
(b) recipes record `-march` but not `-mtune`, and a `native` build is not
excluded; (c) the per-call cells pc16..pc1024, the hit-density ladder and the
"reach" cells are R-1 harness cells, not bench cells, so the per-call regime
of the bar (item 7) has no official instrument; (d) the number of arms
(2 levels x 4 arms + three sweeps) will not fit a bench night window; (e) no
pre-registration, so bins, floors and "evidence bin" are chosen after the
numbers exist; (f) acceptance latency (night window, one writer for the
inbox, D78) is nowhere stated, and §R4.9.6's "re-measure in the same delivery"
(see M-8) cannot be done in a same-day delivery.
**Fix.** Add a "bench submission" subsection with exactly the list in the
two-tier section (pins, testees with recipes, cells incl. the full mover set
and the null population, span-ladder subbench request, pre-registration,
arm budget with U-tier sweeps first). Name it a request the pcrec manager
writes to `inbox_from_pcrec.md` (single-file `[inbox]` commit) and say the kit
session never writes to pcrec-bench.

### M-5  MAJOR  §R4.9.5 items 5, 6, 8, §R4.9.6 item 1
**Problem.** The bar is not fully computable and is gameable.
- "Floor" = `|DENY − OFF|` is one difference of two binaries of the same
  text: one sample of the placement distribution, which can be near zero by
  luck and so shrinks the NULL zone. D144 add. 1 wants the floor measured as
  base-vs-deny, but as a single number it is not a threshold.
- "WIN past the floor" has no magnitude (a 1.01x win past a tiny floor
  counts), "LOSS past the floor" over (cells x levels x CPUs) is a multiple
  comparison with no correction; with dozens of cells one noise excursion
  rejects every row, or the proposer drops cells.
- The "evidence bin" that needs one WIN is named by the proposer, after
  measuring.
- "Min of 3 loops, median of 3 launches" is not stated to interleave arms;
  without interleaving, frequency/thermal drift (Zen 4 boost depends on
  active core count) falls on one arm.
**Fix.** Define floor as a high quantile (or max over the launches) of the
null-population ON-OFF delta (see the null population in the two-tier
section), per CPU class; WIN = better than the floor AND by a stated minimum
effect (state it as an absolute ns/B or ns/call figure, labelled
`UNMEASURED DEFAULT` per D149 until the null distribution gives it); LOSS
likewise; the cell set and the evidence bins are fixed in the pre-registration;
interleave arms ABAB inside each launch; report the count of cells tested so
the multiple-comparison exposure is visible.

### M-6  MAJOR  §R4.9.5 item 6 (placement control), §R4.9.6 item 1 (per-call cells)
**Problem.** The placement band is `|OFF − OFF'|` from ONE relink with
`-falign-functions=64 -falign-loops=32`. (1) One alternative layout is a
single draw. (2) The flags re-align every function and loop in the binary,
including the timing harness, not the one function the ON/OFF delta moves
(a SIMD arm shifts everything after it). (3) The alignment values 64/32 are
unlabelled constants. (4) The threshold `max(floor, band)` then swallows a
real consistent cost: F-R9-1 itself shows a spread of up to 1.7 ns at pc16, and
the house treats real +1..+9 ns entry terms as findings (K81 +1.3..+8.7 ns,
K85, vedge's short-call term). A dispatch prefix costing 0.5-1 ns on every
short call would be called NULL by the band, and short calls are the bench's
main regime.
**Fix.** Use the null population as the band (above), and for the per-call
cells replace the single relink by a padding sweep: N link layouts (nop
padding of the site function in 0..63-byte steps) for OFF and ON each,
compare medians with an interval, report the shift not a threshold. Keep the
below-reach cells honest: they measure the dispatch prefix, so a persistent
median shift above the interval is a LOSS even when each single draw is
inside the band. Label 64/32 as unmeasured until used.

### M-7  MAJOR  §R4.9.6 item 3 (G1 bins), §R4.9.2 row 1 applies
**Problem.** "Bins are (handoff, masked or exact run, run length); a bin with
fewer than 8 timed movers is UNREACHED and the row's APPLIES predicate
EXCLUDES it." (1) Run length 2..8 x handoff x masked is up to 14+ bins, and
the bench/corpus mover count is small (the evidence is two cells: L=6 and
L=3), so most bins fall under 8, and the kit's `applies` becomes a list of
(masked? L in {3,6}?) that exists only because of which patterns happened to be
timed. That is a special-case mechanism of the kind memory
`pcrec-general-mechanisms-not-special-cases` rules out, and the kit cannot
see pcrec's bins at all (it sees the site). (2) The threshold 8 is an inherited
constant, unlabelled here (D149). (3) Bins that were UNREACHED stay excluded
silently when the corpus later grows (nobody recounts them): the K35 shape on
the "excluded" side. (4) Movers are counted from pcrec-side text diffs, so
duplicate-shape patterns inflate a bin.
**Fix.** Bin by CAUSE the cost model reads (handoff x masked, and run length
as T-classes the reach/verify path actually distinguishes), not raw L.
Count distinct site shapes, not patterns. For rows applied to a
shape the bench does not reach, require a synthetic witness cell (the
capability-subbench-first rule) rather than excluding the shape by population.
Add a recount: the `rows.tsv`/`simd_accept.tsv` UNREACHED list is printed with
its counts every G1 run, and a bin crossing the floor flips its record to STALE
(see M-8).

### M-8  MAJOR  §R4.9.6 C19 and "What re-opens a comparison", Q-R9-5, §R4.9.8
**Problem.** C19 is a staleness detector, as the design admits, but it has
five holes.
1. A digest can be re-pinned by editing the record's digest field with no
   re-timing: the plant covers "re-pin `arms.tsv` without touching the
   record", not "touch the record without a transcript". Nothing binds the
   record's digest to the transcript that supposedly measured under it.
2. `arms.tsv` digests the row's FIXTURES, not the real site population.
   Scalar-layer changes that move the comparator without moving a fixture
   (pcrec's pick/prior/findings bundle changing the operands; `cand_rows[]`
   routing; glibc `memchr` ifunc) leave C19 green.
3. Bin populations (M-7) are not in C19's scope: no check fires when an
   UNREACHED bin becomes reached or a mover set changes.
4. The box-dependent half compares glibc/gcc majors only "when run on that
   box": under R2 the official box is the bench box, where this check
   cannot run; the versions the bench used must be IN the record and
   compared to what the bench reports at the next run.
5. Contradiction: the table says the scalar change's own G1 "re-measures the
   SIMD row and re-pins the record in the same delivery", while Q-R9-5 says a
   re-opened comparison "never blocks the scalar change". A RED C19 in
   `make test` does block it. Under R1 the re-measure is an official bench
   run, so "same delivery" is impossible.
**Fix.** (a) Record carries `transcript_comparator_digest` read from the
transcript header at timing time; C19 checks record == transcript == current
`arms.tsv`. (b) Add a site-population digest (the mover manifest, by id) to
the comparator. (c) C19 does NOT go red on a scalar change; it flips the
affected lines to `STALE` (a data change in a committed file, printed) and
goes red only if STALE lines are claimed as ACCEPTED-OFFICIAL or feed R4f.
That resolves the contradiction with Q-R9-5 and with R1. (d) STALE lines
queue a bench re-measure in the next submission. (e) the record stores the
bench's own toolchain versions.

### M-9  MAJOR  §R4.9.3 (reach), §R4.9.5 item 10 (D149 table)
**Problem.** The table marks "reach (short path) = VW + T" as DERIVED and
writes "no other number is written". But `VW + T` is a CORRECTNESS bound (the
smallest span where the vector body never reads a partial block), not a
performance cut-over. Whether w16 beats the scalar body at n just above
`16 + T` (e.g. n = 24 for T = 5) is a cut-over above the reach, which the
design itself calls a tuning constant, and then sweeps ONLY for w32 vs w16.
w16-vs-scalar is never swept, though the bench's short calls live exactly
there (R-1's pc16 column sits below reach for every cell, so it says
nothing about n in [reach, 2 x reach)). Other constants adopted without a
label: 8 (the G1 floor), ~50 ms loops, 3 x 3 repetition, load1 < 0.5, 64/32
alignment, the sweep set {1x, 2x, 4x}, and the unroll's "or left to the
compiler" fallback, which for an intrinsic loop is not a real compiler
choice. And under R1 any constant chosen on the dev box is "measured on
Zen 4", not on the official class.
**Fix.** Split the table's column: `correctness bound (derived)` vs
`performance cut-over (measured or labelled)`. Sweep the w16-vs-scalar
cut-over in {reach, 2 x reach, 4 x reach} too. Label every regime constant
`UNMEASURED DEFAULT:` in place. Add a status word to D149's three states:
`MEASURED-UNOFFICIAL (Zen 4)` vs `MEASURED-OFFICIAL`; a constant becomes
MEASURED only on the bench run.

### M-10  MAJOR  §R4.9.5 item 10 last row, §R4.9.1 F-R9-7, §R4.9.7
**Problem.** "Density cut-over: none, batch 1 makes no density decision; it
wins on mod-i's dense sweep (6,030 hits per MiB)". 6,030 per MiB is one hit
per ~174 bytes. That is sparse for a SIMD restart regime; F-R9-7 (opt3) shows
candidates on real text every few bytes, and a 7x faster skip made bench
subjects slower. The cells that are dense in that sense (cls-n-uc,
userpass) are excluded from batch 1 by K-1, so batch 1's "no density decision"
is a claim with no witness at the density where vector forms lose.
**Fix.** Add a density ladder (hit spacing 8/16/32/64/128/256 B) as a
synthetic witness cell in BOTH tiers; run it unofficially first. Either
measure a cut-over (and label it) or state the density bound batch 1 was
measured up to and decline sites with a pcrec "dense hint" beyond it.

### M-11  MAJOR  §R4.9.2 `levels.def`, §R4.9.7 filed list, R2
**Problem.** A level token (x86-64-v3) says which instructions exist, not
that they are fast. On the official CPU, PDEP/PEXT are microcoded and slow
(v3 includes BMI2), 256-bit operations execute as two 128-bit uops (a w32 row
can be near w16 per block), gathers are slow, and there is no AVX-512. The
design lets `levels.def` imply the capability set and says nothing about
forbidding forms whose cost is CPU-class dependent. A v3 form that uses
`pext` for mask compaction would pass a dev-box alpha and fall off a cliff on
the bench.
**Fix.** `levels.def` gains a column `cost_notes/forbidden_on_zen1`; kit
rule: no PDEP/PEXT/gather in a row unless its official run exists; rows
declare the instruction classes they use (a `mf_formdecl` field), G2/C9 list
them, and the submission names them so the bench result can be read against
them. A w32 row is judged against w16 on Zen 1 in the official run before
being called a gain.

### M-12  MINOR  §R4.9.7 batch-1 evidence, F-R9-4
**Problem.** The batch-1 reading: R-1 ran on the bench CPU (Zen 1), so it
is the official CPU class but not the official harness (a co-linked probe
harness, `taskset` on the kit side, per R1 "unofficial"). The design calls it
"trigger-grade because the box differs"; the correct reason is "harness is
unofficial", and the box difference is in the other direction. Reading,
therefore: R2 STRENGTHENS the case for batch 1 as to CPU (w16 wins over emit
AND swar on every throughput and above-reach per-call row on the verdict CPU;
union-select gate 1m 364,078 -> 48,844 ns vs floor 1,073), and leaves w32's case
as before (throughput WIN over w16, per-call mixed on the same CPU).
It does not repair the gaps: no exact (unmasked) window cell, no VM hybrid
cell, pc16 ran the scalar path, R-1 crossed `-march` (F-R9-2). Both
evidence bins are caseless, one per handoff, so the bench submission needs
the exact bin or a stated exclusion.
**Fix.** Re-label R-1 as "U2 trigger evidence on the official CPU class".
State that w16's submission is justified by it, and add an exact-window
witness cell to the submission.

### M-13  MINOR  §R4.9.1 F-R9-1, §R4.9.2 floor rule
**Problem.** F-R9-1 says the pc16 deltas "are per-binary code generation
and placement of one scalar loop ... not a property of any vector form".
That is an inference: the placement control (item 6) that would show it was
not run. It may also be a real effect of the dispatch prefix changing how gcc
compiles the scalar fall-through (different inlining/register allocation).
The floor rule (C18) establishes TEXT identity of the scalar path, not
MACHINE-CODE identity, so "the scalar arm is every ladder's floor" holds for
text only. Not wrong, but the design leans on it ("by construction").
**Fix.** State the claim as text identity; add to the batch-1 submission an
objdump-level comparison of the scalar path (disassembly of the fall-through
region OFF vs ON) as a reported fact, and let the null population decide the
below-reach reading.

### M-14  MINOR  §R4.9.5 items 1-2, RQ-4
**Problem.** One logical CPU plus an idle SMT sibling on a shared dev box
(load average 7.9 at reading; lanes compile on 12-15/4-7) is asserted via
`load1 < 0.5` at launch. load1 lags by about a minute and says nothing about the sibling;
IRQs and kernel tasks land anywhere; Zen 4 boost depends on how many cores
are active. The pin recipe "`C ± 8`" is box-specific (siblings are
`thread_siblings_list`, N and N+6 on the 6c/12t bench box). For the
unofficial tier this only reduces confidence; for the official tier the
discipline is the bench's, which the design neither knows nor asks.
**Fix.** For U1, record sibling busy% and effective frequency (from
`/proc/stat` and `cpuinfo` deltas) per launch and invalidate a launch above a
stated sibling-busy figure; derive the sibling from `thread_siblings_list`
instead of `C ± 8`; take main's quiet slot (RQ-4) but treat it as a noise
reducer. For O ask pcrecdev2 what the bench pins/idles and put the answer in
the submission.

### M-15  MINOR  §R4.9.8 C18, C-SEL
**Problem.** C18 compares `gcc -E -P -mgeneral-regs-only` text of ON and OFF
artifacts; the artifacts also differ in the `MEMFN_FORMS` stamp line (and,
with comments on, role text), so the comparison needs a stated filter or it
is red at birth; "a plant editing one byte of the floor text" is the only
plant. C-SEL excludes `MEMFN_FORMS` from its stamp compare but the near-cap
witness family is named only by directory. Both are sound in kind (they share
no source with the kit).
**Fix.** Name the C18 filter (exactly the stamp lines C-SEL excludes) and
add its negative control (a plant adding an unguarded byte outside the
filter). Floor the C-SEL population (K35) as a literal.

### M-16  MINOR  §R4.9.6 named-benefit path
**Problem.** SIMD rows are the scalar text plus guarded text (F-R9-5), so a
code-space benefit is structurally impossible for them; under
`MF_P_SIZE_LEANING` no SIMD row could ever apply. The path is correct for D147
add. 11's wording, but vacuous here, and the bar's `INERT:SIZE` row applies to
an empty set.
**Fix.** Say so in the text (named-benefit path available only to rows that
REPLACE scalar text, none in batch 1) so nobody counts it as a second route
into acceptance.

## What is sound

- One binary per arm, no co-linked verdicts (F-R9-1); same-`-march` arms
  (F-R9-2); DENY as byte-identical floor arm; per-row and per-level deny
  granularity (Q-R9-7); the DISPLACED arm for a wider level (first-match's own
  meaning).
- The floor rule and C18 as an independent, timing-free check using the
  preprocessor; the planted-wrong-arm-per-level proof of reach ([MECH-REACH])
  and the answer sweep at every level.
- C-SEL as a selection-neutrality check against pcrec's own stamps, with the
  near-cap family by name; F-R9-5 (length-predicated selections) is a real
  catch and the choice to measure before building RQ-3 is D77-correct.
- ASan/UBSan over movers per level; I2 at `-fno-memfn-simd` for zero movers.
- Compile-time ladder with a derived minimal reach as the DEFAULT, run-time
  cascade filed with its dependency question (Q-R9-8) raised before the
  trigger.
- Q-R9-4/5/6/7 recommendations; the F-R9-3 reading that userpass/cls-n-uc
  cannot be told apart by the kit (lead shape out of batch 1).
- aarch64 handling (floor text only, Mac directional) and clang as compile
  correctness only: consistent with D147 add. 8 and now with R1.
- Batch 1's choice of w16 first: on the official CPU it clears emit and swar
  in every row above reach (see M-12).
