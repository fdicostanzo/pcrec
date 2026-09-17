# [OPT-DIAL] STEP 0 — the inventory behind a speed-vs-size dial

Lane `ccd2`, 2026-09-04. Chartered by Frank on `[CC-DIFF]` STEP 2's inline
ladder: *"It can be switched. We should have a method of indicating the
relative desire of speed vs size. Say there was a dial of N which indicated
max speed vs min size then these switches could be set as a group depending
on the dial setting."*

> **REVISION 2 — 2026-09-16, lane `dialdesign`, at `[OPT-DIAL]` STEP 1.**
> `docs/dev/optdial_size_sweep.md` (lane `dialsweep`, 2026-09-15) ran the
> one sweep §7 item 2 names, and §7 item 3 with it. **Four switches move
> out of UNMEASURED into the policy table; one moves from
> pathological-population-only to corpus-general and turns out to have the
> LARGEST reach in the inventory; two stay UNMEASURED with only their size
> half discharged.** Two further axes have landed in
> `docs/spec/tuning.md` since STEP 0 was written and were never
> inventoried at all (§2.24, §2.25) — so the headline's own denominator
> moved from twenty-one to twenty-three. Every §2 entry the sweep touches
> carries its own **SIZE SWEEP** block; §3 is rewritten; §7's items 2 and
> 3 are marked DONE. **House style applies: nothing below is silently
> rewritten.** Where the sweep contradicts a STEP 0 verdict the original
> sentence stays and the correction sits under it, because a reader who
> remembers the first version has to be able to see what moved.
>
> The relative (percentage) size figures this revision cites are NOT in
> the sweep memo, which reports absolute byte deltas and three summary
> ratio columns. They were recomputed by this lane directly from the
> sweep's own committed per-pattern tables, which is why every one of
> them carries the command that reproduces it (§3.0).

**This document does not build the dial.** It is D77 in its purest form: the
dial's whole premise is that a switch group can be set from MEASURED trade-offs,
so STEP 0 is the audit of which switches actually have one. The finding up
front, and it is not the finding the charter's framing predicts:

> **Of pcrec's twenty-one generation-time switches, FOUR carry a measured
> two-axis exchange rate and belong on a dial. Two are measured PURE WINS and
> must never be on it. The remaining fifteen are UNMEASURED on at least one
> axis — most of them on the SIZE axis, because pcrec has measured time far
> more often than bytes. A dial built today would be a dial with four
> positions' worth of substance and seventeen switches it must not touch.**

The four are `--vm-entry-shape` (this wave's own, `[CC-DIFF]` STEP 2),
`--unroll=K`, `--engine`, and `-fno-premul-table`. `-fno-prefilter-collapse`
and `-fno-splice-calls` are measured on both axes but trade TIME FOR TIME
depending on the workload, which is a different kind of switch and is argued
in §4.

**REVISION 2's count, against the same question.** The sweep changes the
answer and the denominator at once:

> **Of pcrec's TWENTY-THREE generation-time axes, TEN now carry a measured
> two-axis exchange rate. SIX of the ten produce a policy row that is
> actually different at different dial positions** — `--vm-entry-shape`,
> `--unroll=K`, `-fno-premul-table`, and the sweep's three graduates
> `-fno-tiered-entry`, `-fno-offset-skip`, `-fno-anchored-dfa` — **and the
> other four are measured and DELIBERATELY FLAT** (`--engine`,
> `-fno-scan-edge`, `-fno-altcls-merge`, `-fno-altcls-factor`: a row that
> reads the same in every column is a measurement result, not an omission).
> Two remain measured PURE WINS. **Two are STRUCTURALLY excluded for
> reasons no measurement can lift** (§2.24, §2.25) — a distinction STEP 0
> had no bucket for. The rest stay off, and only FOUR of them are off for
> the original reason that a number is missing.

Two arithmetic notes, because an adversarial reader will check them.
**(i)** the STEP 0 headline above says "the remaining fifteen are UNMEASURED
on at least one axis" while §3's own tally of those same fifteen counts two
measured PURE WINS and three fully-measured non-rungs among them — the
blockquote's wording was loose where §3's list was exact, and this revision
does not repeat it. **(ii)** twenty-one became twenty-three by axis
ARRIVALS, not by recount: `-fno-cls-fold` (bit 24) and
`-fno-startpos-guard` (bit 25) landed in `docs/spec/tuning.md` after
2026-09-04. Eighteen bit-axes plus three value axes was twenty-one; twenty
bit-axes plus three is twenty-three.

---

## 1. How a switch earns a place on the dial

Three buckets, and the boundary between them is evidential rather than
architectural.

**PURE WIN — off the dial, permanently.** Smaller AND faster, or faster at no
measured size cost, on the population it applies to. A dial that could turn one
off would be a dial with a strictly-worse setting on it, which is not a
trade-off but a defect. The alternation island and the start-pinned search are
here.

**MEASURED TRADE — on the dial.** Both axes measured, in opposite directions,
on a stated population. This is the only bucket a policy table can hold
numbers for.

**UNMEASURED — off the dial until measured.** One axis has no number. The
entry below names the specific measurement that would admit it, because "we
should measure it some day" is not a plan and the point of an inventory is to
turn the gap into a task.

**A fourth thing exists and is not a bucket: WORKLOAD-DEPENDENT.** Two
switches (`-fno-prefilter-collapse`, `-fno-splice-calls`) are measured
faster on one workload and slower on another, with bytes moving too. A single
ordinal dial cannot express "faster if your subjects reach the call site", so
they need a different mechanism or none. §4.

---

## 2. The inventory

Every entry: what it trades, the measured numbers with their citation, the
bucket. Citations are file paths relative to the repository root; a number is
"measured" only where a ledger, design note or lane report states it.

### 2.1 `-fno-possessify` (bit 4)

**Trades:** nothing measured on either axis. It denies an AST rewrite whose
effect is which VM strategy bit fires; the cited example moves `frame_capacity`
3 -> 4, a RESOURCE field, not emitted bytes.

**Measured:** answer identity only — `docs/spec/tuning.md` §2.1, `possdiff`:
155 patterns agreed, 0 diverged, 77,725 cells.

**Bucket: UNMEASURED.** Admitting it needs an artifact-size and throughput A/B
over the possessified population, which nothing has run.

**SIZE SWEEP (2026-09-15) — HALF DISCHARGED, BUCKET UNCHANGED.** The size
half of that A/B has now run (`docs/dev/optdial_size_sweep.md` §2.1) and the
throughput half has not, so **this entry stays UNMEASURED** and the sweep's
own §3 says so in those words. What the size half found: 236 movers (6.79%
reach), 202 growing and 34 shrinking under denial, median **+1.69% of the
artifact**, extremes −14.00% to +1.42% (this lane's recomputation, §3.0).
The lean is that possessify SAVES bytes when on, weakly — and note the
asymmetry the memo's absolute numbers hide: the biggest single grower is
+4,056 B but the biggest PROPORTIONAL move is a 14% SHRINK under denial,
so the two tails are not the same patterns. **The named missing
measurement, unchanged and now the only one:** throughput, default against
`-fno-possessify`, over the possessified population.
`tests/possessify/`'s own differential driver already compiles both sides.

### 2.2 `-fno-revdet` (bit 5)

**Trades:** cursor-rung strategy only; no size or time number exists.

**Measured:** `docs/spec/tuning.md` §2.2, `rungdiff`: 205 patterns agreed, 0
diverged, 395,757 cells. Identity, not exchange.

**Bucket: UNMEASURED.** Same A/B as §2.1.

**SIZE SWEEP (2026-09-15) — HALF DISCHARGED, BUCKET UNCHANGED.**
`docs/dev/optdial_size_sweep.md` §2.2: **53 movers, the smallest reach of
the seven swept (1.52%)**, and genuinely two-directional — 24 grow, 29
shrink, median **+0.51%** (this lane's recomputation, §3.0), spread −27.79%
to +11.65%. This is not a weak lean like possessify's; it is a switch whose
size effect points both ways on a population of fifty-three. **On the whole
corpus it is a wash to four decimal places: −1,543 bytes of 115,198,573,
i.e. −0.001%.** Throughput is still entirely unmeasured; the bucket stays
UNMEASURED and the named missing measurement is §2.1's, over
`tests/rungselect/`'s population.

### 2.3 `-fno-counter` (bit 6)

**Trades:** denying drops a bounded repeat to full literal replication —
bytes and gcc time for nothing.

**Measured, and it is a floor rather than a rung:**
`docs/dev/artifact_size_census.md` — the denied build is **206% larger** in
source and gcc was CPU-budget-killed at 150.10 s against 55.13 s default (it
never linked); on two corpus outliers the denied build is REFUSED outright,
above the 64-copy replication cap with no fallback; where under the cap, the
literal fallback is about the same size and **21% faster to compile**.

**Bucket: MEASURED, but NOT a dial rung.** The numbers say the counter rung's
absence is catastrophic on the population that needs it and a wash on the
population that does not. There is no setting of this switch a size-seeking
caller wants. It stays a correctness-shaped floor.

### 2.4 `-fno-length-prune` (bit 7)

**Trades:** STEPS, not bytes — `docs/spec/tuning.md` §2.4 states a denied
artifact is byte-for-byte the emitter's own pre-MRL output.

**Measured:** identity (`mrldiff`: 146 pairs agreed, 202,458 cells) and the
step blow-up avoided (`docs/design/k23_impl/`: 10.6M steps -> 1).

**Bucket: NOT A TRADE AT ALL.** With no size cost there is nothing for a dial
to buy. It belongs off the dial for the opposite reason to a pure win: not
"never turn it off" but "turning it off buys nothing".

### 2.5 `-fno-prefilter` / `-fprefilter` (bits 8/9)

**Trades:** whether a VM artifact runs an inlined DFA prefilter ahead of the
program — real bytes (a whole DFA scan) for real time.

**Measured:** not independently. `--engine=vm` strips the same prefilter as a
side effect (D44/R21 E-6) and IS measured — see §2.11 — so the exchange rate
is available only as a proxy that also changes the engine.

**Bucket: UNMEASURED (proxy only).** Admitting it needs the prefilter axis
measured ALONE: emitted bytes and throughput for `-fno-prefilter` against
default on the hybrid population, with the engine held fixed.

### 2.6 / 2.7 `-fno-altcls-merge` (bit 10), `-fno-altcls-factor` (bit 11)

**Trades:** alternation branches folded into a byte class — plausibly fewer
emitted bytes as well as fewer branch tests, but only one axis is measured.

**Measured (time only):** `docs/design/altcls_pinned_impl/CLAUDE.md` — stage 2
factoring confirmed **-7.61%** throughput, n=27, sd 0.226 us against a 47.2 us
mean.

**Bucket: UNMEASURED on size, and likely a PURE WIN.** Admitting it needs the
emitted-bytes delta over the same corpus. If it lands where the shape of the
mechanism predicts, this is a pure win and leaves the dial rather than joining
it.

**SIZE SWEEP (2026-09-15) — MEASURED, AND THE "LIKELY A PURE WIN"
HYPOTHESIS IS CONFIRMED IN BULK AND REFUTED AT THE EDGE.** Both flags were
swept separately (`docs/dev/optdial_size_sweep.md` §2.6, §2.7); the TIME
number remains the combined `-7.61%` for denying both together, which is
why neither can reach a clean per-flag verdict no matter what the size axis
says.

| | `-fno-altcls-merge` | `-fno-altcls-factor` |
|---|---|---|
| movers / reach | 101 / 2.90% | 54 / 1.55% |
| grow : shrink under denial | 84 : 17 | **52 : 2** |
| median size change | +2.40% | +0.56% |
| range | −23.39% … +16.75% | −2.89% … +3.78% |
| whole-corpus cost of denial | +42,833 B (+0.037%) | +10,008 B (+0.009%) |

(Percentages recomputed by this lane, §3.0; the memo's own absolute figures
are `−4,490`/`+3,114` and `−900`/`+910` bytes.) On the bulk of each reached
population the mechanism does what it was predicted to do — most artifacts
are smaller with it on, and denial also costs throughput. **What blocks the
PURE WIN verdict is a single counter-example each**, and §1's definition is
a universal over the reached population, which one counter-example breaks:
`tests/base/k18_arm_order.rxt:256` is **23.4% SMALLER** with merge denied,
and `tests/base/d27_bodies.rxt:100` is 2.9% smaller with factor denied.

**Two consequences, and the second is the one that keeps these rows OUT of
the dial's moving part.** (a) The verdict is MEASURED TRADE, not PURE WIN —
they stay in the inventory rather than leaving it. (b) But a trade whose
size lean is 0.037% of the corpus and whose counter-examples are
proportionally larger than its median gain is not a trade a DIAL POSITION
should express: a min-size setting that denied these would make the typical
artifact BIGGER and one known artifact 16.75% bigger, to save 23.4% on
another. §3 therefore gives both a FLAT row — `allow` at every position —
with the counter-examples carried as named caveats. This is the treatment
`docs/dev/optdial_size_sweep.md` §4 itself recommends, and it is the same
warning label `--unroll=K`'s own non-monotone byte curve already carries.

**`-fno-altcls-merge` also loses one pattern to a refusal** —
`tests/size/size_term.rxt:32`, the nested-repeat tower, above the
131,072-node emitted cap without the merge. That is `tests/axes/
run_axes.sh`'s own already-documented K45 `REFUSAL_PATTERN` entry and not a
defect the sweep found; it matters here because it means this flag is not
answer-identity-preserving in the trivial sense — see §2.25 and the STEP 1
design note's acceptance section for why a REFUSAL-moving flag is a dial
hazard of its own kind.

### 2.8 `-fno-atomic-discharge` (bit 12)

**Trades:** which ENGINE a pattern gets, by deleting cuts a proof shows are
no-ops. Correctness-shaped, not size-shaped.

**Measured:** differential only, `docs/spec/tuning.md` §2.8.

**Bucket: UNMEASURED, and probably not a dial candidate** — the axis it moves
is engine selection, which `--engine` already addresses directly.

### 2.9 `-fno-splice-calls` (bit 13)

**Trades:** SPLICE (default, inline the callee at each site) against HYBRID
(one shared body, linked) — bytes for time, per call site.

**Measured, fully, on both axes:** `docs/design/subroutines_design.md` §6.2a —
SPLICE **855.2 bytes per call site** against HYBRID **171.3**, a factor of 5.
Time: on the mixed corpus SPLICE wins all four rows by 8-26%; on a
lexical-only corpus (subjects that die before the first call) SPLICE **LOSES**
to HYBRID by up to 14% at k=1.

**Bucket: WORKLOAD-DEPENDENT.** See §4. The bytes side is a clean linear rate
and would be a fine dial rung on its own; the time side reverses sign with the
subject population, which a size-vs-speed ordinal cannot express.

### 2.10 `--unroll=K`

**Trades:** body copies for iterations — emitted bytes and gcc time against
per-iteration work.

**Measured, densely:**

- `docs/dev/artifact_size_census.md`, tension curve item 1: `--unroll=1` is
  **75-79% smaller and 12x faster to compile with no throughput cost** on
  NESTED bounded-repeat patterns, and a 1-3% (noise) effect on single-level
  large-count patterns. The payoff tracks nesting structure, not raw count.
- `docs/design/eng_brep_design.md`: gcc `-O2` is quadratic in copy count; the
  throughput advantage is exhausted by K ~ 16; K = 8 ships.
- `docs/design/artifact_size_term.md`: the K ladder is **non-monotone in
  bytes** — 2,449 / 2,469 / 1,334 / 1,635 / 498 / 262 nodes at K = 8/6/4/3/2/1
  on one shape.

**Bucket: MEASURED TRADE — ON THE DIAL.** With the non-monotonicity as the
warning label: a dial that assumes "lower K is smaller" is wrong on real
shapes, so the dial sets K and `[ART-SIZE]`'s ladder still runs.

### 2.11 `--engine=dfa|vm|auto`

**Trades:** the coarsest axis in the tree — a whole engine.

**Measured, and it is the sharpest trade pcrec has:**
`docs/dev/artifact_size_census.md`, tension curve item 3 — `--engine=vm`
shrinks the object to **4-9% of default** on the three `((a)|ab)`-family
outliers, at up to **173,580x slower** on the fail path
(`((a)|bc){0,4000}d`: 0.20 us -> 34,716.0 us, quiet-box re-measured).

**Bucket: MEASURED TRADE — ON THE DIAL, with the largest range and the
loudest caveat.** A ratio of 10^5 is not a dial rung in the same sense as a
factor of 3; the min-size column would have to accept a pathological fail
path. §3 puts it in its own row with that stated.

### 2.12 `-fno-tiered-entry` (bit 14)

**Trades:** call time for STACK FRAME size, which is not the emitted-bytes axis
a dial is about.

**Measured (time and frame):** `docs/design/two_tier_entry.md` §1 — 233.8
ns/call default against 46.2 under `-fno-stack-clash-protection`, ~99% of the
gap being page probing; `docs/dev/plan.md` `[OPT-1]` — `rx_search`'s frame
131,216 B -> 3,184 B.

**Bucket: UNMEASURED on emitted bytes.** The extra `noinline` deep-tier
function costs code bytes nobody has counted. It is very likely a near-pure
win. Admitting it needs the `.text` delta of a tiered against a single-tier
build on the tiered population.

**SIZE SWEEP (2026-09-15) — MEASURED, AND IT IS THE CLEANEST TWO-AXIS
RESULT IN THE WHOLE INVENTORY. THIS ENTRY GRADUATES TO THE DIAL.** The
"very likely a near-pure win" guess above is the one the sweep overturns:
the tier costs real, countable, monotone bytes.

`docs/dev/optdial_size_sweep.md` §2.12: **330 movers (9.49% reach), and all
330 move the same way** — every one SHRINKS under denial, by a near-fixed
−1,953 B (a handful at −1,957). There is no grower anywhere in the
population. In proportional terms (this lane's recomputation, §3.0) that is
a median **7.48%** of the artifact, p10 6.25% / p90 8.76%, never above
9.47%; **312 of the 330 save at least 5% and not one saves 10%**, which is
the tightest distribution any switch here produces. Whole-corpus, the tier
costs **644,522 B, 0.559% of all emitted bytes**.

**The exchange rate, stated once, both axes from their own sources:**
≈1,953 bytes (≈7.5% of the artifact) buys the ~5× per-call entry latency
`two_tier_entry.md` §1 measures (233.8 ns → 46.2 ns) on the ~9.5% of the
corpus whose stamped default storage will not fit one 4 KB page. Nothing
else in this inventory has both halves that clean.

**One reading note the sweep itself flags and this entry repeats**, because
it is a check-design lesson and not a number: an analysis script that
always prints a biggest-grower/biggest-shrinker pair MISLABELS an
all-one-sign population — this row's "biggest grow" is −1,953, a least-
shrink. A reader who takes that column at face value reads a growth that
does not exist.

### 2.13 `-fno-premul-table` (bit 15)

**Trades:** a wider accept table for a shorter loop-carried dependency chain.

**Measured on both axes:**

- Time: **1.794x** on the shipped emitter
  (`docs/design/premultiplied_dfa_table.md` §13), revising STEP 1's 1.276x
  (`docs/dev/opt3_dfa_scan_measurement.md`).
- Size: denying (the indexed form) is **~22-25% smaller** on every
  DFA-scan-bearing pattern (`docs/dev/artifact_size_census.md` item 2) — i.e.
  the pre-multiplied form costs ~29-33% more bytes.

**Bucket: MEASURED TRADE — ON THE DIAL.** The cleanest two-axis rate in the
inventory. One caveat carried from its source: the census's quiet-box re-run
found the THROUGHPUT direction inconsistent on 2 of 5 patterns, flagged there
as noise; the size claim is load-independent and stands either way.

### 2.14 `-fno-offset-skip` (bit 16)

**Trades:** a memchr-plus-verify prefilter against a plain scan.

**Measured (time only):** the materiality bar is 2x
(`docs/design/offset_k_skip.md` §4.5); a DECLINED pattern is byte-for-byte the
pre-`[OPT-K]` output (§5.1), which says nothing about the ADOPTING population's
byte cost.

**Bucket: UNMEASURED on size.** Admitting it needs the emitted-bytes delta on
the offset-set-adopting population. Expected small.

**SIZE SWEEP (2026-09-15) — MEASURED, "EXPECTED SMALL" CONFIRMED, AND THE
ENTRY GRADUATES WITH THAT AS ITS QUALIFICATION RATHER THAN ITS FOOTNOTE.**
`docs/dev/optdial_size_sweep.md` §2.14: **491 movers (14.12% reach, the
second-largest here)**, 464 shrinking under denial and 27 growing. Median
**−1.30%** of the artifact, p90 −1.78%, extremes −3.60% … +3.12% (this
lane's recomputation, §3.0). **451 of 491 movers save at least 1% and only
20 save 2%** — the whole distribution lives inside a two-percent band.
Whole-corpus the machinery costs **144,994 B, 0.126%**.

Against the 2× materiality bar `offset_k_skip.md` §4.5 already holds the
mechanism to, the rate is: **a little over one percent of the artifact for
up to 2× on the log-line-shaped population it targets.** That is a real
MEASURED TRADE and this entry graduates — but it is also the WEAKEST size
lever admitted here, and §3's table says so: at a size notch it is the last
row to fire, not the first. The 27 growers are the caveat: on ~5% of the
reached population the plain offset-0 filter is BIGGER than the offset-k
form it replaces, so denial is not universally a size win even on its own
reached set.

### 2.15 `-fno-anchored-dfa` (bit 17)

**Trades:** an additional anchored machine (bytes, gcc time) for a much faster
match-here entry.

**Measured on both axes, on different populations:**

- Time: matching subjects 2.077x behind the VM -> 1.046x; short valid emails
  1.207x behind -> 0.571x, i.e. ahead (`docs/dev/opt2_anchored_match_measurement.md`).
- Size and gcc: on large bounded-count shapes, **+46% compiler CPU** (24.3 s
  -> 35.9 s on `[a-z]{0,30000}`) and artifact **1.32 MB -> 1.98 MB, +50%**
  (`docs/dev/plan.md` `[ENG-COUNT]`, citing r41 S1).

**Bucket: MEASURED TRADE on a PATHOLOGICAL population only.** The size number
comes from a 30,000-count shape, not from the corpus. It is the closest of the
UNMEASURED entries to admissible; what it needs is the same size delta over
the ordinary corpus.

**SIZE SWEEP (2026-09-15) — MEASURED OVER THE ORDINARY CORPUS, AND THE
FRAMING ABOVE IS THE ONE THING IN THIS DOCUMENT THE SWEEP FLATLY
CONTRADICTS.** "Pathological population only" is wrong, and not by a
little.

`docs/dev/optdial_size_sweep.md` §2.15: **1,509 movers — 43.39% of the
corpus, an order of magnitude more reach than anything else in this
inventory** — and **every single one shrinks under denial**; the
least-negative mover is −6 B and there is no grower at all. Proportionally
(this lane's recomputation, §3.0) the median artifact is **15.32%** smaller
without the anchored machine, p10 12.73% / p90 21.18%, worst case
**39.60%**; 1,493 of 1,509 save at least 10% and 163 save at least 20%. The
absolute extreme is `tests/utf8/axis12_scripts.rxt:296` at **−266,794 B**
(999,925 → 733,131). **Whole-corpus, the optional anchored machine is
12,260,289 bytes — 10.64% of everything pcrec emits over its own test
corpus.**

**Three things follow, and the third is a correction to this document's own
structure.**

1. The rate is now corpus-general on both axes: ≈15% of the artifact on 43%
   of patterns, against `opt2_anchored_match_measurement.md`'s measured
   match-regime win (2.077× behind the VM without it → 1.046× with it, i.e.
   ≈1.99× on matching subjects).
2. **A min-size dial position should DENY this by default.** It is the
   single largest byte lever the dial can legitimately pull — `--engine` is
   larger and is excluded for violence (§3), and this one is monotone.
3. **The "pathological population" reading was an artefact of the witness,
   not of the mechanism.** The 30,000-count shape said +50% on one hostile
   input; the corpus says +15% on nearly half of everything. An entry whose
   only size number comes from a hand-picked witness will describe the
   witness, and this document's §7 item 3 asked for exactly this
   replacement — it is worth recording that the request was right and the
   expected answer was too small.

### 2.16 `-fno-size-term` (bit 18)

**Trades:** nothing directly. It is the mechanism by which `--unroll=K` is
already chosen for size.

**Measured:** materiality bar **0.75** — a new K is kept only if it saves at
least 25% of bytes (`docs/design/artifact_size_term.md`,
`tests/codegen/run_size_term.sh` §9). `PCREC_SIZE_TERM_THRESHOLD` = 120,000
bytes (`src/core/limits.def`) is the emitted-size knee above which the ladder
runs at all.

**Bucket: NOT A RUNG — A PARAMETER OF ONE.** The dial should set the
materiality bar and the threshold as part of `--unroll=K`'s row, not toggle
this switch. §3's table does that.

### 2.17 `-fno-prefilter-collapse` / `-fprefilter-collapse` (bits 19/20)

**Trades:** an exact prefilter against a collapsed one — smaller and
count-independent, sometimes far faster and sometimes catastrophically slower.

**Measured, and it is the best-documented entry here:**
`docs/spec/tuning.md` §2.17's own table — worst case `((a)|b){0,400}c` on
100K `a`s: collapsed 9.24 s / 99,601 attempts / 38,776 B against exact
0.000011 s / 1 attempt / 55,069 B, so collapsed is ~30% smaller and
catastrophically slower there; row 5 is the reverse, collapsed ~2.7x FASTER on
a rejected subject. K39: `((a)|b){0,400}c` and `{0,4000}c` emit the SAME line
count under collapse, against ~2.5x under exact. A fourth axis, the step
budget, moves too: `(a{1,3}){65}` is 0.00 s exact and `PCREC_ERR_STEPS` after
13.34 s collapsed.

**Bucket: WORKLOAD-DEPENDENT.** §4.

### 2.18 `-fno-scan-edge` (bit 21)

**Trades:** a small fixed emitted-byte cost per edge-carrying machine for a
large per-byte win on the population that carries edges.

**Measured on both axes:**

- Time: letters **2.71x / 3.03x** faster (n = 256 / 16,384), the VM gap
  6.00x -> 2.03x; the digits control **1.08x SLOWER** — a fixed entry cost
  (`docs/dev/plan.md` `[OPT-5]` STEP 1).
- Size: **+364 to +612 emitted bytes per edge-carrying machine, zero
  elsewhere** (`docs/dev/dev_journal.md`, lane edge1, 2026-09-03).

**Bucket: MEASURED TRADE, and a very cheap one.** A few hundred bytes for
2-3x is not a trade a size-seeking caller wants to make differently; the digits
control's 1.08x regression is the only reason it is not simply a pure win. It
is a CANDIDATE rung whose range is so lopsided that a policy table row would
read the same in every column. §3 lists it and says so.

### 2.19 `-fno-start-pinned` (bit 22)

**Trades:** nothing. Both axes measured, both favourable.

**Measured:** over 175 pinned artifacts, **-3,232 bytes per pinned artifact**
and **-311,811 bytes corpus-wide (-0.69%)**; time **x1.985** unwrapped against
search-filter, matching the cross-rung x1.97-2.04 prediction
(`docs/dev/plan.md` `[OPT-5]` STEP 2, O-14 ledger).

**Bucket: PURE WIN — OFF THE DIAL.**

### 2.20 `-fno-alt-island` (bit 23)

**Trades:** nothing. Smaller and faster on the population it takes.

**Measured:** max artifact growth **1.03x**, 0 refused, 27,256 answer cells /
0 divergences (`docs/dev/lanes/isl1_report.md`, panel r53); prefix-free islands
run at **0.140-0.175x** of chain time, prefix-bearing width-4+ islands a wash
at ~1.0x, and the two width-2 prefix-bearing cases that measured slower
(1.131x / 1.144x) are DECLINED by the shipped `VM_ISL_MIN_BRANCHES_PREFIXED`
floor, so nothing shipped is slower (`docs/spec/tuning.md` §2.20).

**Bucket: PURE WIN — OFF THE DIAL.** The plan row already rules it so.

### 2.21 `--vm-entry-shape=N` — `[CC-DIFF]` STEP 2, this wave's own

**Trades:** copies of the VM matcher body against the entry's frame, canary
and call — the dial's first native rung, and it is an ORDINAL rather than a
bit, which is what makes it the shape the dial wants everywhere else.

**Measured (`docs/dev/lanes/ccd2_report.md` §3, this box, gcc 15.2.0 `-O2 -c`,
single compiles):** the ratio of rung INLINE (six body copies, what `[CC-DIFF]`
STEP 1(a) shipped) to rung SHARED (one body, three forwarding entries), by the
artifact's own `RX_VM_PROGRAM_BYTES`:

| program bytes | subject | `.text` INLINE / SHARED | gcc INLINE / SHARED |
|---|---|---|---|
| 1,786 | `\d{1,16}` | 1.01x | 1.7x |
| 9,698 | `w-8` | 2.74x | 2.9x |
| 18,916 | `wp-16` | 3.66x | 3.8x |
| 37,357 | `wp-32` | 3.70x | 4.7x |
| 80,591 | `w-64` | 3.85x | 5.4x |
| 306,826 | `w-256` | 6.24x | 6.4x |

Run time is isl1's ladder (`docs/dev/lanes/isl1_report.md` §12.2): the
attribute buys a flat **16-23%** at every width, barely decaying. **The SHARED
rung's own run time is NOT YET MEASURED** — it is this row's post-lift item and
the number the whole rung turns on.

**Bucket: MEASURED TRADE — ON THE DIAL, and the first rung a policy table can
actually hold.** With the finding that changes its shape: on the SIZE and GCC
axes SHARED is smaller and no slower to compile than PLAIN at **every** width
measured, so the ladder's bottom is not "give up the optimisation" but "keep
it with one body copy". §5.

**REVISION 2 — WHAT THIS ROW IS ACTUALLY MEASURED ON, which is not what
STEP 0's own draft table assumed.** No new measurement; a re-read of the
two this entry already cites, prompted by trying to fill five columns from
them. Three things:

1. **THE TWO AXES ARE MEASURED ON TWO DIFFERENT PAIRS OF RUNGS.** The
   `.text` and gcc table above is INLINE ÷ SHARED. The run-time number
   (isl1 §12.2's flat 16-23%) is the `always_inline` ATTRIBUTE's, i.e.
   INLINE against the pre-`[CC-DIFF]` PLAIN shape. There is no cell in
   which one pair is measured on both axes, so "16-23% for 2.7-6.2× bytes"
   — the charter's own framing and §5's — is a ratio assembled from two
   different comparisons.
2. **THE RUNG THE DEFAULT SELECTS HAS NO MEASURED RUN TIME AT ALL.**
   `forward` is established on SIZE (ccd2 §3.4: inline's object-code
   properties exactly, at 0.50-0.61× its `.text` and gcc time, 20 artifacts,
   no exception) and on TIME only STRUCTURALLY — no entry frame, no canary,
   no out-of-line chain symbol, therefore it should run like inline. That
   is a good argument and it is not a measurement.
3. **STEP 0's draft table below puts `shared` in two cells, and STEP 0's own
   allowlist rule (§6) forbids it.** This entry says in its own text that
   the shared rung's run time is "NOT YET MEASURED ... the number the whole
   rung turns on", and §7 item 1 lists it as blocking. A dial position
   naming `shared` would be the dial setting a switch value with no measured
   rate — the exact thing §6's last paragraph exists to prevent. The draft
   table was written before its own rule.

**Consequence for the policy row** (derived in `opt_dial_design.md` §3.4,
not asserted here): the dial moves the **TERM** —
`VM_INLINE_CHAIN_MAX_BYTES`, default 4,096 — and never names a rung.
Raising it is the speed side and has a genuinely measured rate (the plan
row's own 0.061-0.067 bytes per ns/call saved at program sizes
5,183/5,985/6,954, five times better than the next cell up). LOWERING it
buys almost nothing, because at 1,786 bytes of program the INLINE/SHARED
`.text` ratio is already 1.01× — which is the term's own contract
("forward only where it costs nothing") stating that **the default is
already this row's min-size answer.** Frank's 2026-09-04 keep-the-defaults
ruling and the DEFAULT-MIDDLE PRINCIPLE are the same fact here, one
derived from the other.

### 2.22 The emitted-size caps

`PCREC_MAX_EMIT_BYTES` = 1,000,000 (about 170 KB of object) and
`PCREC_MAX_VM_EMIT_CODE_BYTES` = 500,000 (about 85 KB, code outside table
initialisers), both raise-only, both stamped
(`src/core/limits.def`, `docs/spec/limits.md`).

**Bucket: NOT ON THE DIAL.** They are refusal boundaries, not trade-offs: a
dial position that lowered them would manufacture refusals, which is exactly
what raise-only exists to prevent. They belong in the table as the SIZE END's
boundary condition and nothing more.

### 2.23 Named but outside the switch list

`[OPT-CLSPACK]` STEP 0's bitmap-against-256-byte-table question is FILED AND
EXPLICITLY UNMEASURED (plan commit `41337a2`); there is no ledger. The
`[OPT-DIAL]` charter names DFA cell representations as a candidate — the
premultiplied half is §2.13 and admissible, the class-representation half is
not yet a switch at all.

### 2.24 `-fno-cls-fold` (bit 24) — ADDED IN REVISION 2, AND OFF THE DIAL BY RULING

**Not in STEP 0's inventory because it did not exist then.** It is
`docs/spec/tuning.md` §2.22 — the axis is numbered differently in the two
documents, and this section's number follows ARRIVAL ORDER here while
tuning.md's follows its own bit order. Cite by flag name, not by section
number.

**Trades:** which shape a two-member VM pool class's membership test takes
— an ASCII fold pair as `(byte | 0x20) == lower` against a 32-byte bitmap
plus load.

**Measured, on both axes, and the speed half is closed WITHOUT a stopwatch:**
`docs/dev/form_char_step0.md` §2 family A — −38% `.text` on the six-site
witness with its class-table `.rodata` deleted entirely, and a `gcc -O2 -S`
equivalence check showing `c=='a'||c=='A'`, `(c=='a')|(c=='A')` and
`(c|0x20)=='a'` all compile to the same branchless mask+compare+sete with
no load, so there is nothing for the table form's load-latency argument to
beat. Against that, `docs/dev/plan.md` `[FORM-CHAR2]` records the bench
measuring the shipped fold SLOWER on its one corpus witness (`ci-256`
forced-VM ×1.027 search / ×1.045 throughput / ×1.095 match against a 1.34%
noise floor).

**Bucket: OFF THE DIAL BY RULING, not by measurement.** Frank, 2026-09-11
(`[FORM-CHAR2]`): cls-fold is **SUBSUMED INTO THE `[CLS-TREE]` DESIGN
NOTE** — its end state is one kit member among several (the `m = 0x20`
one-cube instance of the study's general cube form), selected by the
sectioning DP and priced by λ, and there is **no standalone dial placement
for a special case** (the general-mechanisms rule). `[FORM-CHAR2]`'s
instruction counts still run, but as calibration inputs to that note's
op-pricing model rather than as evidence for a placement here.

**This is the inventory's first entry whose dial answer is "it becomes λ".**
It is therefore the worked example for `opt_dial_design.md` §4: a switch
that would have been a discrete policy row is replaced by a continuous
currency the same dial position sets. `docs/dev/cls_tree_study.md` §4.3
measures why — the general cube form reaches **8 of the 41 corpus byte
classes where today's fold classifier sees only 4**, so the special case
covers half its own general form's population in this tree's own corpus.

### 2.25 `-fno-startpos-guard` (bit 25) — ADDED IN REVISION 2, AND STRUCTURALLY INELIGIBLE

`docs/spec/tuning.md` §2.23. Same numbering caveat as §2.24.

**Trades:** nothing on either axis. It selects between two ruled SEMANTICS
for a caller-supplied `startpos` inside a multi-byte character — refuse with
`PCREC_ERR_STARTPOS` (guarded, the default, libpcre2's own behaviour under
`PCRE2_UTF`) or answer at the position named (permissive). Under the `byte`
encoding the two builds are byte-identical.

**Bucket: STRUCTURALLY INELIGIBLE — and this is a bucket STEP 0 did not
have.** It is the ONE axis in `docs/spec/tuning.md` that is **not
answer-identity-preserving**, by its own declaration and on purpose: the two
arms give different answers on one input class (`(?<!.)` at offset 1 of
`CE B1 CE B2` reports `(1,1)` permissive and `PCREC_ERR_STARTPOS` guarded).

`[OPT-DIAL]`'s charter makes **answer identity across every dial value the
ACCEPTANCE**. A switch whose two settings disagree about answers therefore
cannot be on the dial *whatever* its exchange rate turns out to be — no
future measurement can admit it, which is what separates this bucket from
UNMEASURED. It is a contract choice wearing a tuning flag's spelling, and a
contract is not something a speed-vs-size preference gets to pick.

The general form of the rule, which `opt_dial_design.md` §6 states as an
eligibility precondition rather than leaving implicit: **the dial's
allowlist is gated on answer identity FIRST and on a measured rate SECOND,
and the first gate is quantified over the values the dial can actually
set.** Two switches meet it differently, and the difference matters:

- **`-fno-startpos-guard` fails it outright.** Its two arms disagree about
  answers, so no dial position may name either — the axis is off the
  allowlist permanently.
- **`-fno-altcls-merge` fails it in ONE ARM ONLY.** Denying the merge moves
  the REFUSAL SET (§2.6's K45 row: one corpus tower stops compiling), which
  is an answer-identity break in the weaker sense that a pattern's answer
  becomes "refused". The axis is therefore eligible **provided no dial
  position ever selects the denying arm** — which is exactly the flat row
  §3 gives it, now forced from two independent directions at once: the size
  measurement does not justify denial, and denial would move the refusal
  set even if it did.

---

## 3. The rate table

> **REVISION 2 RESHAPED THIS SECTION, and the reshaping is the point.**
> STEP 0's §3 was a *draft policy table* — switches down the side, dial
> values across the top, guessed cells. STEP 1 produces the real policy
> table, with its cells DERIVED from a threshold rule rather than placed,
> and that table lives in **`opt_dial_design.md` §3 and only there.** Two
> documents carrying one table is a drift hazard this house has recorded
> more than once. So §3 here is now the **RATE TABLE**: what each switch
> costs and buys, in what units, on what population — the inventory's own
> job — and the dial's columns are the design note's.
>
> The STEP 0 draft table is preserved below the rate table, marked, because
> three of its rows are wrong for reasons worth keeping visible.

### 3.0 Reproducing the relative figures

The sweep memo reports absolute byte deltas plus three ratio columns; every
PERCENTAGE in this revision was recomputed by lane `dialdesign` from the
sweep's own committed per-pattern tables. It is one join over two files and
needs no build:

```
# for SLUG in possessify revdet altcls_merge altcls_factor \
#             tiered_entry offset_skip anchored_dfa
python3 - <<'PY'
BASE="docs/dev/optdial_size_sweep/runs/"
def load(s):
    d={}
    for ln in open(BASE+s+"_size.tsv"):
        f=ln.rstrip("\n").split("\t")
        if len(f)>=5:
            try: d[f[0]]=int(f[4])
            except ValueError: pass
    return d
b=load("baseline")
for s in ("possessify","revdet","altcls_merge","altcls_factor",
          "tiered_entry","offset_skip","anchored_dfa"):
    f=load(s)
    sav=sorted((1-f[k]/b[k])*100 for k in f if k in b and f[k]!=b[k])
    agg=sum(f[k]-b[k] for k in f if k in b)
    print(s, "movers",len(sav), "median %+.2f%%"%sav[len(sav)//2],
          "range %+.2f..%+.2f"%(sav[0],sav[-1]),
          "corpus %+.3f%%"%(100*agg/sum(b[k] for k in f if k in b)))
PY
```

Sign convention throughout: **a positive "saving" means DENYING the switch
makes the artifact smaller**, i.e. the switch was costing those bytes.
Baseline population 3,478 rows, 115,198,573 bytes.

### 3.1 The rate table proper

`reach` is the fraction of the 3,478-row corpus whose artifact the switch
changes at all. `size` is the median across movers, with the range. `time`
is whatever the switch's own ledger measured, **in its own unit and its own
regime, deliberately not normalised** — §3.2 is about why that matters.

| switch | reach | size (median, range) | corpus bytes | time | regime | bucket |
|---|---:|---|---:|---|---|---|
| `--unroll=K` (K=8→1) | nested-repeat shapes | −75…−79% | not swept | no measured cost (nested); 1-3% noise (single-level) | throughput | TRADE, non-monotone |
| `-fno-premul-table` | DFA-scan-bearing | −22…−25% | not swept | **1.794×** slower | throughput | TRADE |
| `-fno-anchored-dfa` | **43.39%** | **−15.32%** (−39.60…0.00) | **−10.643%** | **≈1.99×** slower | whole match, matching subjects | TRADE |
| `-fno-tiered-entry` | 9.49% | **−7.48%** (−9.47…−0.30) | −0.559% | **5.06×** slower | **per-call ENTRY** | TRADE |
| `-fno-scan-edge` | edge-carrying machines | −364…−612 B (abs) | not swept | 2.71-3.03× slower (letters); 1.08× faster (digits) | throughput | TRADE, flat |
| `-fno-offset-skip` | 14.12% | −1.30% (−3.60…+3.12) | −0.126% | up to 2× slower | throughput, log-line shapes | TRADE, sub-material |
| `-fno-altcls-merge` | 2.90% | **+2.40%** (−23.39…+16.75) | +0.037% | −7.61% (combined with factor) | throughput | TRADE, flat, wrong-signed |
| `-fno-altcls-factor` | 1.55% | **+0.56%** (−2.89…+3.78) | +0.009% | −7.61% (combined with merge) | throughput | TRADE, flat, wrong-signed |
| `--vm-entry-shape` term | VM artifacts | 0.061-0.067 B per ns/call at the cheap cells | not swept | 16-23% (attribute, INLINE vs PLAIN) | per-call ENTRY | TRADE, speed side only (§2.21) |
| `--engine=vm` | DFA-eligible | object to **4-9%** of default | not swept | up to **173,580×** slower on the fail path | whole match | TRADE, EXCLUDED for violence |
| λ — the class kit | code-point and byte classes | see `cls_tree_study.md` §5.2 | **46.5× today's** on 312 property sets | probe ops, not time | membership test | **NEW — §3.3** |

Four notes a reader should not have to derive:

- **`-fno-altcls-merge` and `-fno-altcls-factor` are WRONG-SIGNED for a size
  notch.** Their medians are positive, meaning denial makes the typical
  artifact BIGGER. There is no dial position that wants them, which is a
  stronger statement than "they are not worth a position".
- **`-fno-offset-skip` is SUB-MATERIAL.** Its entire mover distribution
  lives inside a two-percent band. Whether that clears a materiality floor
  is a threshold question, and the threshold is Frank's (`opt_dial_design.md`
  §9 Q2).
- **`-fno-tiered-entry`'s 5.06× is NOT a whole-match number**, and nothing
  in this inventory converts it into one. §3.2.
- **`--engine`'s row is flat and that is the point** — STEP 0's own
  paragraph below still stands unamended.

### 3.2 THE UNITS PROBLEM, which is this inventory's real STEP 1 finding

Read the `time` and `regime` columns together. The eleven rows carry their
penalties in **four incommensurable units**: a percentage of throughput
(altcls), a multiplicative slowdown of whole-match time (premul,
anchored-dfa), a multiplicative slowdown of a per-call ENTRY path
(tiered-entry, vm-entry-shape), and a materiality-bar ratio on a named
pattern shape (offset-skip). The λ row carries a fifth — probe operations
per membership test.

Frank's threshold rule-shape is stated in ONE unit: *"performance penalty
under x% AND size savings over y%"*. **Evaluating it against this table
requires a conversion that does not exist anywhere in this repository.**
Specifically: what fraction of a matcher's run time is entry cost, and what
fraction is class-membership probing. Both are subject-dependent.

This is D77 in its own inventory: the honest move is to NAME the
measurement rather than invent the constant. `opt_dial_design.md` §3.2
carries the consequence — the rule is stated PER REGIME, with two regimes
and two threshold pairs, and the cross-regime ratio flagged as the single
number a future measurement would replace.

**And it is why `-fno-tiered-entry` is not simply the best row in the
table.** Its size half is the cleanest measurement here; its time half is
5.06× of a component whose share of total match time nobody has measured.
On a megabyte subject that is nothing; on a find-all sweep over 40-byte log
lines it is most of the cost. Note what this is NOT: it is not §4's
workload-dependent bucket, because the SIGN never reverses — denial is
always smaller and always slower. Only the MAGNITUDE moves with the
regime. **Sign-stable and magnitude-regime-dependent is a dial-holdable
shape; sign-reversing is not.**

### 3.3 λ IS A ROW, and it is the only one that is not a switch

`docs/dev/cls_tree_study.md` §5.1 minimises `rodata + text + λ·ops` over
contiguous partitions to choose a class matcher's sectioning, and **λ is
`[OPT-DIAL]`'s dial arrived at from the algorithm rather than fitted to
it** — the study's own words. Sweeping λ traces the size/speed Pareto
frontier directly.

Two consequences for this inventory, and the second is the more important:

1. **The dial acquires a CONTINUOUS row beside its discrete ones.** Every
   other row selects among a handful of named values; this one sets a real
   number that a dynamic program then spends. `opt_dial_design.md` §4 is
   the mapping from the five ordinal positions to λ, and it is that note's
   hardest section.
2. **λ ABSORBS switches rather than joining them.** `-fno-cls-fold` (§2.24)
   is the first: Frank ruled it has no standalone dial placement because
   its end state is one λ-priced kit member. Any future class-representation
   switch arrives the same way. So the dial's row count does not simply
   grow with the tree — one row can eat several, which is the
   general-mechanisms rule showing up as table structure.

### 3.4 STEP 0's draft policy table, preserved and marked

Kept because three of its rows are wrong in instructive ways. **Do not
build from this table**; `opt_dial_design.md` §3 is the one to build from.

| switch | 0 min size | 1 | 2 = today | 3 | 4 max speed | the rate that justifies the spread |
|---|---|---|---|---|---|---|
| `--vm-entry-shape` | `shared` | `shared` | **auto (term)** | `forward` | `inline` | INLINE costs 2.7-6.2x `.text` and 2.9-6.4x gcc over SHARED above 9.7 KB of program, and 1.01x below 1.8 KB, for a flat 16-23% of run time |
| `--unroll=K` | 1 | 4 | **8** | 8 | 16 | K=1 is 75-79% smaller and 12x faster to compile at no throughput cost on NESTED shapes; the throughput advantage is exhausted by K~16 |
| `-fno-premul-table` | deny | deny | **allow** | allow | allow | the indexed form is 22-25% smaller; the pre-multiplied form is 1.794x faster |
| `--engine` | (see note) | auto | **auto** | auto | auto | `--engine=vm` reaches 4-9% of object size at up to 173,580x slower fail path — the range is too violent for a dial position |
| `-fno-scan-edge` | allow | allow | **allow** | allow | allow | +364..612 bytes per edge-carrying machine for 2.71-3.03x; the row reads the same in every column and is listed to say so |
| size-term bar (`[ART-SIZE]`) | 0.95 | 0.85 | **0.75** | 0.75 | 0.75 | the bar is "keep a new K only if it saves >= 25%"; loosening it takes more of the K ladder's size wins |
| emitted-size caps | boundary | boundary | **boundary** | boundary | boundary | raise-only by ruling; never a dial position |

**THE `--engine` ROW IS DELIBERATELY FLAT AND THAT IS THE POINT.** It has the
largest measured size lever in the tree and a fail-path cost of five orders of
magnitude. Putting `vm` in the min-size column would make one dial position
capable of turning a 0.2 us answer into a 35 ms one. If the dial is ever to
reach it, it needs a per-pattern predicate ("is this pattern's DFA blow-up the
pathological kind"), which is a separate row.

**THREE ROWS ARE ONE ROW'S PARAMETERS.** `--unroll=K`, the size-term bar and
the caps all address emitted size through the same `[ART-SIZE]` mechanism. A
dial that set them inconsistently — a low K with a tight bar — would be setting
one thing twice. They are listed separately because they are separately
spellable, and a policy table has to say they move together.

**WHAT IS NOT IN THE TABLE, and why that is most of the inventory.**
Fifteen switches. Six because they have no size number
(`-fno-possessify`, `-fno-revdet`, `-fno-altcls-merge`, `-fno-altcls-factor`,
`-fno-tiered-entry`, `-fno-offset-skip`), one because its size number is
pathological-only (`-fno-anchored-dfa`), one because it is measured only
through a proxy (`-fno-prefilter`), two because they are workload-dependent
(§4), one because it is a floor (`-fno-counter`), one because it trades
nothing (`-fno-length-prune`), one because it addresses engine selection
(`-fno-atomic-discharge`), and two because they are measured pure wins
(`-fno-start-pinned`, `-fno-alt-island`).

### 3.5 What REVISION 2 found wrong in the table above

Three rows, and none of the three is wrong because a number moved.

**(a) `--vm-entry-shape`'s min-size cells name a rung the allowlist
forbids.** Columns 0 and 1 read `shared`; §2.21's own text says the shared
rung's run time is unmeasured and §7 item 1 lists it as blocking. **The
draft table violates §6's allowlist rule, in §6's own document.** The
mechanism of the error is worth more than the error: the rule was written
in §6 and the table in §3, and nothing checked one against the other —
which is the same shape as a check whose control shares a source with what
it controls (`docs/dev/learnings.md` §3), one document earlier in the
pipeline. `opt_dial_design.md` §3.1 accordingly makes allowlist conformance
a MECHANICAL property of how the table is written, not a rule a reader
applies afterwards.

**(b) `-fno-premul-table` is denied at column 1, and the threshold rule
will not support it there.** Denial costs 1.794× — a 79% slowdown — for
22-25% of bytes. A first size notch that accepts a 79% slowdown is not a
first notch. Under any threshold pair whose tier-one bound is modest, this
row's denial belongs at the EXTREME size position only.
`opt_dial_design.md` §3.3 derives it there.

**(c) The size-term bar row moves three parameters as one and says so, but
the table gives them one row each anyway.** The note under the table ("THREE
ROWS ARE ONE ROW'S PARAMETERS") is correct and the table's shape
contradicts it. The design note folds `--unroll=K`, the materiality bar and
the caps into a single `[ART-SIZE]` row with sub-parameters, so that a dial
position cannot set them inconsistently by construction rather than by a
warning.

And one row that is RIGHT for a reason worth restating: **`--engine` stays
flat.** The sweep's `-fno-anchored-dfa` finding (43% reach, 10.6% of all
corpus bytes) might read as an argument that big levers can be dialled
after all. It is not. The difference is not size, it is the SHAPE of the
time cost: anchored-dfa is ≈1.99× and monotone, `--engine=vm` is up to
173,580× on the fail path. A dial position that can turn a 0.2 µs answer
into a 35 ms one is not a dial position at any size saving.

---

## 4. The workload-dependent pair, and why an ordinal cannot hold them

`-fno-splice-calls` and `-fno-prefilter-collapse` both have complete two-axis
measurements and both REVERSE SIGN on the time axis with the subject
population:

- SPLICE is 8-26% faster on a mixed corpus and up to 14% SLOWER on a
  lexical-only one, at 5x the bytes per call site.
- The collapsed prefilter is ~2.7x faster on a rejected subject and 840,000x
  slower on `((a)|b){0,400}c` over 100K `a`s, at ~30% fewer bytes.

A dial position means "I want speed more than bytes". Neither switch has a
setting that IS faster; each has a setting that is faster **for some subjects**.
Setting them from a speed-vs-size ordinal would be setting them from the wrong
question, and the min-size column is the only one either could honestly occupy
(both are the smaller arm). The recommendation is to leave both off the dial
and note in `tuning.md` that they are chosen from the workload, not the
profile.

---

## 5. What `[CC-DIFF]` STEP 2 changes about the dial's premise

The charter's example rung was the inline ladder read as "16-23% of run time
bought at 2.6x to 6.5x bytes". The four-arm ladder (§2.21) says that framing
conflated two effects:

1. **deleting the entry's frame, canary and out-of-line call** — where STEP 1's
   measured win came from; and
2. **replicating the matcher body into six entries** — which is where all the
   bytes went.

The SHARED rung has (1) without (2). Measured, it is smaller than the
pre-`[CC-DIFF]` shape at every width and no slower to compile. If its run time
lands near INLINE's, the dial's first rung mostly collapses: there is one
setting that is better on every axis and the term picks between SHARED and
INLINE only at the small end, where INLINE is nearly free anyway.

**That is the single most valuable measurement this document points at**, and
it is a quiet-box item. Until it exists, the `--vm-entry-shape` row above is a
size-and-gcc row with a borrowed run-time column.

---

## 6. The spelling question, for the manager

Three alternatives. All three assume explicit per-switch flags OVERRIDE the
dial (explicit beats profile, as D93's file-wins beats the command line).

**(a) `--tune=N`, an ordinal 0..4.** Closest to Frank's words ("a dial of N").
Cheap: one `--unroll=`-shaped value parameter, no bit, no axes-registry entry.
Reads badly at the extremes — nothing about `4` says "speed" — and an ordinal
invites a later `--tune=7` that means nothing.

**(b) An `-O`-family letter: `-Os` / `-O2` / `-Ospeed`.** Instantly legible to
anyone who has used a C compiler, and the analogy is exact. The cost is that
it collides with the reader's expectation that `-O` levels are about the C
COMPILER's optimisation of the artifact, which pcrec does not control (its
`GENCFLAGS` are the harness's, not the artifact's). A caller passing `-O2` to
pcrec and to gcc would reasonably expect them to mean the same thing.

**(c) Named profiles: `--tune=size|balanced|speed`.** A closed token set, which
is what `_ENGINE_SEL` is and for the same reason — a consumer can bucket on it
and a typo is an error rather than a silent neighbour. Extensible without
renumbering. Slightly more to type; the fewest ways to be wrong.

**Recommendation: (c), with the stamp `<PREFIX>_TUNE` carrying the token.**
D82 wants a visible object for a selection, and a token stamp lets an artifact
say which profile built it in the same vocabulary the flag used. Three names is
also an honest match to how much substance §3's table has: four rows with real
spreads do not support five distinguishable positions, and shipping five when
two of them are identical is the kind of surface that later cannot be removed.

**A `tune` line in an `.rxt` config block per D93** follows either way, and its
precedence is D93's: the file wins over the command line, and an explicit
per-switch setting wins over both.

**One thing the dial must NOT do**, and it is worth ruling before it is built:
the dial must not be able to select a value for a switch that has no measured
rate. A profile that quietly turns off `-fno-possessify` because "min size
probably means less of everything" would be exactly the guess this inventory
exists to prevent. The policy table is an allowlist, not a default.

---

## 7. What this document is missing

Named so the gaps are tasks rather than silence.

1. **The SHARED rung's run time** (§5). Quiet box, post-lift. Blocks the
   `--vm-entry-shape` row's speed column.
2. **A size axis for six switches** (§2.1, 2.2, 2.6, 2.7, 2.12, 2.14). One
   sweep would produce all six: emitted `.text` per artifact, default against
   each deny flag, over the corpus. `tests/axes`'s machinery already walks that
   product for ANSWERS; it does not record bytes.
3. **`-fno-anchored-dfa`'s corpus-general size cost** (§2.15), which the same
   sweep would produce.
4. **`-fno-prefilter` measured alone** (§2.5), engine held fixed.
5. **`[OPT-CLSPACK]` STEP 0** (§2.23), which is already filed.

Item 2 is the highest-value one: a single sweep moves six switches out of
UNMEASURED, and it is the sweep that would tell us whether the dial has four
rungs or ten.

### 7.1 REVISION 2 — status of each item

**Item 2 (the size axis for six switches): DONE**, 2026-09-15, lane
`dialsweep`, `docs/dev/optdial_size_sweep.md`. Its own prediction —
"whether the dial has four rungs or ten" — resolves nearer the low end
than the framing invites: **four of the six moved, and only two of those
four produce a policy row that differs between positions.** The other two
(`altcls-merge`, `altcls-factor`) came back measured and WRONG-SIGNED for a
size notch, which is a result the item did not anticipate as a possible
outcome. It is worth recording that the sweep's value was not the
graduations: it was retiring two hypotheses ("likely a PURE WIN") that
would otherwise have been carried indefinitely as probably-true.

**Item 3 (`-fno-anchored-dfa`'s corpus-general size cost): DONE**, same
sweep, and it is the item that most changed its own entry — see §2.15. The
expected answer ("what it needs is the same size delta over the ordinary
corpus") was right about the method and wrong about the scale: the
pathological witness said +50% on one shape, the corpus says ≈15% on 43%
of everything.

**Item 1 (the SHARED rung's run time): STILL OWED, and now BLOCKING rather
than merely missing.** STEP 0 called it a post-lift quiet-box item. STEP 1
finds that §3.4's draft table already spends it — two dial cells name
`shared` — so until it exists, the `--vm-entry-shape` row has no legal
size-side value at all (§2.21, §3.5(a)). The design note's row is
speed-side-only for exactly this reason.

**Item 4 (`-fno-prefilter` measured alone): STILL OWED**, unchanged.

**Item 5 (`[OPT-CLSPACK]` STEP 0): SUPERSEDED, not done.** The question
("bitmap against a 256-byte table") has been overtaken by
`docs/dev/cls_tree_study.md`, which does not ask which of two
representations wins — it finds that **no single representation wins any
real code-point set** and that the answer is a per-section KIT chosen by a
λ-priced dynamic program. `[OPT-CLSPACK]`'s framing contained an assumption
(that the question has a per-class answer) that the study refutes. The
residue of item 5 is now the λ row, §3.3.

**NEW ITEM 6 — the two throughput sweeps the size sweep leaves owed.**
`-fno-possessify` and `-fno-revdet` have a size number and no time number,
so the allowlist still forbids them a dial cell. `tests/possessify/`'s and
`tests/rungselect/`'s own differential drivers already compile both sides
of each; the shape to copy is `altcls_pinned_impl`'s. Note the asymmetry
before anyone runs it: possessify reaches 236 patterns with a weak
one-directional lean, revdet reaches 53 with no lean at all and a
whole-corpus effect of −0.001%. **A time number would admit possessify to
the table and would most likely confirm revdet has nothing to trade** —
which is a legitimate outcome and should be stated as the expected one
rather than discovered as a disappointment.

**NEW ITEM 7 — the units conversion (§3.2).** What fraction of match time
is per-call entry cost, and what fraction is class-membership probing.
Without it, Frank's threshold rule cannot be evaluated across regimes and
λ cannot be calibrated against the discrete rows in any units-exact way.
This is the highest-value unrun measurement the dial now has, and it
replaces item 2 in that position.
