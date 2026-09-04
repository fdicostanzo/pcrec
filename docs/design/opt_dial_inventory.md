# [OPT-DIAL] STEP 0 — the inventory behind a speed-vs-size dial

Lane `ccd2`, 2026-09-04. Chartered by Frank on `[CC-DIFF]` STEP 2's inline
ladder: *"It can be switched. We should have a method of indicating the
relative desire of speed vs size. Say there was a dial of N which indicated
max speed vs min size then these switches could be set as a group depending
on the dial setting."*

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

### 2.2 `-fno-revdet` (bit 5)

**Trades:** cursor-rung strategy only; no size or time number exists.

**Measured:** `docs/spec/tuning.md` §2.2, `rungdiff`: 205 patterns agreed, 0
diverged, 395,757 cells. Identity, not exchange.

**Bucket: UNMEASURED.** Same A/B as §2.1.

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

---

## 3. The draft policy table

Rows are the switches with a two-axis measured rate. Columns are dial values.
**Every cell carries the measurement, not a preference**, and a cell reading
"as today" means the measurement gives no reason to move it.

Five positions, `N = 0` (min size) to `N = 4` (max speed), with `N = 2` today's
defaults. The count is a proposal; §6 has the spelling question.

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
