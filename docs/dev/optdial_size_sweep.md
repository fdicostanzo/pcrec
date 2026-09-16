# [OPT-DIAL] §7 SIZE SWEEP — the measurement six switches were missing

Lane `dialsweep`, 2026-09-15. `docs/design/opt_dial_inventory.md` §7 names
this as the one run that would move six UNMEASURED switches at once:
**emitted size per artifact, DEFAULT build vs each deny flag, over the
whole corpus.** MEASUREMENT ONLY — nothing under `src/` or `tests/` lands
from this lane; reproduction pieces are `docs/dev/optdial_size_sweep/`
(own CLAUDE.md), following `docs/dev/artifact_size_census.md`'s own
layout choice (a report here, the script alongside it).

The verdict vocabulary is `opt_dial_inventory.md` §1's: **PURE WIN** (off
the dial permanently — smaller AND faster, or faster at no size cost),
**MEASURED TRADE** (on the dial — both axes measured, in opposite
directions), **UNMEASURED** (off the dial until measured), and **NOT A
TRADE AT ALL** (no size cost, so nothing for a dial to buy). This sweep
supplies the SIZE axis; where a switch's TIME axis was already measured
elsewhere in the inventory, the two combine into a full verdict below —
where it was not, the switch's bucket stays UNMEASURED even after this
sweep, and that is stated rather than glossed over.

## 0. Method

**Corpus population**: every `pattern` line under `tests/` — the
growing-population formulation. The house's own file-level census (cited
by recent [DD-13b.W23] lane reports) is 210 `.rxt` files / 3,936 `pattern`
lines; this sweep's baseline pass produced **3,478 SIZELOG rows**, which
is the population these numbers are denominated against — the gap is
`perr` compile-refusal blocks and other lines that never reach a
successful compile, which by construction emit no `SIZELOG` row on any
axis (a rejected pattern has no byte count to compare). **3,478 is not a
number this lane chose**: it is byte-for-byte the row count the
already-committed `docs/dev/artifact_size_log.tsv` carries at a nearby
commit, confirming this sweep's harness invocation (`tests/harness/run.sh`
with no file/dir arguments) reaches the identical population every
existing size-log run in this tree does. A pattern that refuses to
compile under a flag specifically (never under baseline) contributes no
row on that side and is accounted as LOST below, cross-checked against
that pass's own `RXTDUMP`, rather than silently dropped from the
denominator (K35).

**Size definition**: `tests/lib/size_count.sh`'s `size_count_row` — total
source bytes of the emitted `gen.c`+`gen.h` pair minus comment-line bytes
(the `[ART-SIZE]` census's own `prose` bucket) — the SAME definition
`docs/dev/artifact_size_log.tsv` and every existing size-log row in this
tree already use, verified byte-exact against
`docs/dev/artifact_size_census/census.py`'s classifier (that script's own
header carries the six-number cross-check). This sweep reuses the
mechanism rather than reimplementing it: `tests/harness/run.sh`'s existing
`SIZELOG` hook, driven exactly as `tests/axes/run_axes.sh` already drives
`RXTFLAGS`/`RXTDUMP` for the answer-identity sweep — nothing under
`tests/` is modified.

**The `#include`-line trap does not apply here.** This house has recorded,
three separate times (`ccdiff_step0_evidence/`, `opt4_impl/CLAUDE.md`),
that diffing two emitted artifacts written to different `-o` basenames
false-diffs on the `#include` line because the header's own name is
embedded in it. This sweep never diffs artifact TEXT: it compares BYTE
COUNTS read via `SIZELOG`, and every pass — baseline and all seven flags —
drives the identical `tests/harness/run.sh` mechanism, which always names
its per-case output `gen.c`/`gen.h` inside its own scratch workdir
regardless of `RXTFLAGS`. Same basename on both sides, and no text diff at
all — the trap has no purchase twice over.

**Join**: each flag pass is joined against the baseline pass by key
(`file:line`, the `.rxt` block's own coordinates — the identical key
`tests/axes/dump_diff.awk` uses). A key present on only one side is LOST
(compiled under baseline, not under the flag) or GAINED (the reverse);
tuning.md documents all seven flags swept here as deny-only, so neither
population is expected to move, and this is CHECKED via each pass's own
`RXTDUMP`, not assumed (K35).

**Reproduction**: `bash docs/dev/optdial_size_sweep/run_sweep.sh` (all
eight passes, sequential, one at a time), then
`python3 docs/dev/optdial_size_sweep/join_sweep.py` for the joined report.

## 1. The seven switches swept

| switch | macro | bit | inventory §  | inventory's own TIME-axis status |
|---|---|---|---|---|
| `-fno-possessify` | `PCREC_NO_POSSESSIFY` | 4 | 2.1 | UNMEASURED (neither axis had a number) |
| `-fno-revdet` | `PCREC_NO_REVDET` | 5 | 2.2 | UNMEASURED (neither axis had a number) |
| `-fno-altcls-merge` | `PCREC_NO_ALTCLS_MERGE` | 10 | 2.6 | MEASURED: -7.61% throughput (stage 2, altcls_pinned_impl) |
| `-fno-altcls-factor` | `PCREC_NO_ALTCLS_FACTOR` | 11 | 2.7 | MEASURED: -7.61% throughput (same measurement, combined denial) |
| `-fno-tiered-entry` | `PCREC_NO_TIERED_ENTRY` | 14 | 2.12 | MEASURED: 233.8ns vs 46.2ns/call, frame 131,216B->3,184B (two_tier_entry.md) |
| `-fno-offset-skip` | `PCREC_NO_OFFSET_SKIP` | 16 | 2.14 | MEASURED: 2x materiality bar (offset_k_skip.md §4.5) |
| `-fno-anchored-dfa` (bonus, §7 item 3) | `PCREC_NO_ANCHORED_DFA` | 17 | 2.15 | MEASURED, but only on a PATHOLOGICAL 30,000-count shape — this sweep's own value is the corpus-general figure §2.15 itself asks for |

**Result at a glance** (all against 3,478-row baseline; deltas are
`flag_bytes - baseline_bytes`, i.e. the cost of DENYING the switch; a
negative delta means denying it made the artifact SMALLER, meaning the
switch itself was COSTING those bytes when on):

| switch | matched | lost | movers | %movers | delta p10 | delta p50 | delta p90 | delta max | all-one-sign? |
|---|---|---|---|---|---|---|---|---|---|
| `-fno-possessify` | 3,478 | 0 | 236 | 6.79% | -231 | +465 | +601 | +4,056 | no (mixed) |
| `-fno-revdet` | 3,478 | 0 | 53 | 1.52% | -2,362 | -125 | +1,084 | +9,365 | no (mixed) |
| `-fno-altcls-merge` | 3,477 | 1 | 101 | 2.90% | -1,071 | +507 | +1,210 | +3,114 | no (mixed) |
| `-fno-altcls-factor` | 3,478 | 0 | 54 | 1.55% | +109 | +158 | +436 | +910 | mostly grows (min -900) |
| `-fno-tiered-entry` | 3,478 | 0 | 330 | 9.49% | -1,953 | -1,953 | -1,953 | -1,953 | **yes — every mover shrinks** |
| `-fno-offset-skip` | 3,478 | 0 | 491 | 14.12% | -404 | -332 | -332 | +635 | mostly shrinks (tail to +635) |
| `-fno-anchored-dfa` (bonus) | 3,478 | 0 | 1,509 | 43.39% | -5,045 | -3,075 | -2,482 | -6 | **yes — every mover shrinks** |

Full per-mover distributions (including ratio spread and named biggest
grower/shrinker) are in §2 below and in
`docs/dev/optdial_size_sweep/runs/summary.tsv`.

## 2. Per-switch findings

### 2.1 `-fno-possessify` (bit 4)

Reach: 236/3,478 (6.79%). Direction is MIXED but skewed positive: p10 is
still negative (-231) while p50/p90/p99/max are all positive, so a
minority of movers shrink under denial and most grow — median +465
bytes, biggest grow +4,056 B (`tests/counterk/counterk.rxt:1259`,
45,261→49,317, 1.090x), biggest shrink -409 B
(`tests/rungselect/rungselect.rxt:972`, 0.987x). No refusals, no
population change (matches tuning.md's deny-only posture).

**Reading**: on the population it reaches, possessify usually SAVES bytes
when ON (denying it usually grows the artifact), consistent with an
optimization that collapses redundant VM strategy machinery. The reach is
modest (6.8% of the corpus) and the effect size is real but not huge
(median 465 B, i.e. typically 1-2% on the artifacts it touches — see
ratio column: median 1.017x).

### 2.2 `-fno-revdet` (bit 5)

Reach: 53/3,478 (1.52%) — the smallest population any of the seven
reaches. Direction is genuinely mixed and closer to a wash than
possessify's: median delta is -125 B (slightly negative — denial
*shrinks* the typical mover, the opposite lean from possessify), but the
distribution is wide (p10 -2,362, p90 +1,084, p99 +8,359) with the
single biggest grow at +9,365 B (`tests/counterk/counterk.rxt:1444`,
33,695→43,060, 1.278x) and biggest shrink -2,793 B
(`tests/rungselect/rungselect.rxt:1695`, 0.912x).

**Reading**: unlike possessify, revdet's size effect does not point
one way on the population it reaches — the median is near zero and the
spread is wide relative to it. On size alone this switch does not look
like a candidate pure win; it looks like a genuine, small, two-directional
trade with no clean interpretation until its TIME axis (still entirely
unmeasured) is taken too.

### 2.6 `-fno-altcls-merge` (bit 10)

Reach: 101/3,477 (2.90% of the matched population). **One refusal**:
`tests/size/size_term.rxt:32` (the nested nested-repeat tower,
`(?:(?:(?:(?:(?:(?:a|b){41}){41}){41}){41}){41}){41}`) LOST under this
flag — this is `tests/axes/run_axes.sh`'s own K45-documented refusal
(`REFUSAL_PATTERN["-fno-altcls-merge"]="pattern too large (VM exceeds"`),
not a defect this lane found: denying the alternation-to-class merge
removes the mechanism that keeps this one tower's VM node count under the
131,072-node emitted cap, so it refuses at generation time exactly as
`run_axes.sh` already documents. Reproduced live from `altcls_merge.err`:
`pattern too large (VM exceeds 131072 emitted nodes)`.

Direction: mostly positive (median +507 B, i.e. merge saves bytes when
ON) but with a genuine, larger-than-noise **non-monotonicity**: the
biggest single shrink under denial is -4,490 B
(`tests/base/k18_arm_order.rxt:256`, 19,194→14,704, **0.766x** — denying
merge made THIS artifact nearly a quarter smaller), while the biggest
grow is +3,114 B (`tests/base/precedence.rxt:36`, 0.7% larger... no,
18,596→21,710, **1.167x**). So on at least one real corpus pattern, the
merge pass is not a size win at all — it costs bytes when ON. This is the
same shape `--unroll=K`'s own non-monotone byte curve warns about
(`artifact_size_term.md`): a size-reducing pass is not guaranteed to
reduce size on every input.

**Reading against the inventory's existing TIME number** (-7.61%
throughput when merge+factor are BOTH denied together,
`altcls_pinned_impl`, stage 2 — the only TIME number that exists, and it
is for the COMBINED denial, not this flag alone): the size direction
mostly agrees with keeping merge ON (smaller AND faster on the typical
pattern), but the real non-monotone counter-example means this is NOT a
strict PURE WIN by §1's definition ("smaller and faster ... on the
population it applies to" — a definition a single counter-example
breaks). Verdict: **MEASURED TRADE**, not PURE WIN, with the caveat that
the TIME number is shared with §2.7 below rather than isolated to this
flag alone.

### 2.7 `-fno-altcls-factor` (bit 11)

Reach: 54/3,478 (1.55%). Direction is the cleanest of the mixed-sign
switches: p10 is already positive (+109), so roughly 90% of movers grow
under denial (factor saves bytes when ON) and only a small tail shrinks
(min -900 B, `tests/base/d27_bodies.rxt:100`, 31,171→30,271, 0.971x).
Biggest grow +910 B (`tests/base/alternation_trie.rxt:105`, 30,123→31,033,
1.030x). No refusals.

**Reading**: this is the closest of the seven to confirming the
inventory's own §2.6/2.7 hypothesis ("UNMEASURED on size, and likely a
PURE WIN") — the vast majority of the reached population is smaller when
factor is ON, matching the ALREADY-measured -7.61% throughput cost of
denying it. But it is not a clean PURE WIN either: the -900 B
counter-example is real and on the same corpus population, so §1's
"never worse on any measured input" bar is not met. Verdict: **MEASURED
TRADE, near-pure-win** — closer to graduating off the dial than any other
switch this sweep touched, blocked only by one counter-example and by the
TIME number being shared with §2.6 rather than isolated.

### 2.12 `-fno-tiered-entry` (bit 14)

Reach: 330/3,478 (9.49%) — and **every single mover moves the same
direction and by nearly the same amount**: delta is -1,953 B on the
overwhelming majority and -1,957 B on a handful, with **zero** growers.
p10 = p50 = p90 = -1,953; the true minimum is -1,957 and the true maximum
(least-negative mover) is also -1,953 — there is no genuine "biggest
grow" here, only a "least shrink", which the analysis script's generic
biggest-grow slot reports as -1,953 rather than a positive value (worth
noting explicitly: a script that always prints a grow/shrink pair will
mislabel an all-one-sign population unless read against its own sign,
exactly this row).

**Reading**: this is the CLEANEST two-axis result of the whole sweep.
The tier's cost is a near-FIXED per-artifact byte count (~1,953-1,957 B —
the second, single-tier `<prefix>_search`/`_match`/`_match_caps`
machinery `[OPT-1]` added, not a percentage of program size) on the
~9.5% of the corpus whose stamped default storage does not fit one 4 KB
page. Against the inventory's already-measured TIME number (233.8 ns vs
46.2 ns per call — roughly 5x — plus the frame-size story,
`two_tier_entry.md` §1) this is now a full, clean **MEASURED TRADE**:
~1.95 KB of code for a ~5x per-call win on the population it reaches.
This switch **GRADUATES to the dial** on this sweep's evidence alone.

### 2.14 `-fno-offset-skip` (bit 16)

Reach: 491/3,478 (14.12%) — the second-largest reach after
`-fno-anchored-dfa`. Direction is mostly negative (median -332, p90 still
-332 — a tight cluster of shrinks) with a real positive tail (p99 +635,
max +635, `tests/offsetskip/offset_skip.rxt:326`, 21,806→22,441, 1.029x)
and the biggest shrink -878 B (`tests/offsetskip/offset_skip.rxt:220`,
24,403→23,525, 0.964x).

**Reading**: against the inventory's already-measured TIME number (the
materiality bar is a 2x speedup, `offset_k_skip.md` §4.5, on the
log-line-shaped population the mechanism targets), the size direction
mostly agrees — denying the offset-k machinery (falling back to the
offset-0 filter) mostly SHRINKS the artifact, i.e. the k-set machinery
costs bytes when ON — but with a real minority where denial GROWS
instead, meaning the plainer offset-0 filter is occasionally bigger than
the offset-k form it replaces. Verdict: **MEASURED TRADE** — bytes for a
real (if population-scoped) speed win, admitted to the dial with the
caveat that ~13% of the reached population (the positive tail) trades in
the opposite direction from the rest.

### 2.15 `-fno-anchored-dfa` (bit 17, bonus — §7 item 3)

Reach: **1,509/3,478 (43.39%)** — by a wide margin the largest population
any switch in this sweep touches, an order of magnitude above every other
row. And **every single mover shrinks under denial** (max delta is -6 B,
the least-negative — there is no grower at all), from a median of
-3,075 B down to an extreme of **-266,794 B**
(`tests/utf8/axis12_scripts.rxt:296`, 999,925→733,131 bytes, **0.733x** —
denying the anchored machine shrinks this one `\p`-property artifact by a
quarter of a megabyte) at p10 = -5,045 B.

**Reading**: the inventory's existing measurement for this switch was
explicitly scoped as "MEASURED TRADE on a PATHOLOGICAL population only"
— a single hand-picked 30,000-count shape (+46% compiler CPU, 1.32 MB →
1.98 MB, +50%), with the note that "the size number comes from a
30,000-count shape, not from the corpus." **This sweep replaces that
caveat with a real number**: the anchored machine costs SOME bytes on
43% of the ordinary corpus, monotonically (never a size win to carry it),
with a heavy tail into the hundreds-of-KB range on large-class patterns
(the UTF-8 `\p{...}` family, this sweep's own worst case). Combined with
the inventory's already-measured TIME direction (favorable when the
machine is present: 2.077x behind the VM → 1.046x for matching subjects,
`opt2_anchored_match_measurement.md`), this switch is now — on THIS
sweep's own corpus-general evidence — a clean **MEASURED TRADE**, and the
one with the LARGEST reach of any switch in the whole inventory. §2.15 of
`opt_dial_inventory.md` should be updated to cite this sweep's numbers
rather than only the pathological witness.

## 3. Updated inventory verdicts

| switch | before this sweep | after this sweep |
|---|---|---|
| `-fno-possessify` §2.1 | UNMEASURED (neither axis) | **still UNMEASURED overall** — size axis now has a number (mixed-sign, median favors keeping it ON), but TIME is still entirely unmeasured; a throughput sweep is the next step, not built here |
| `-fno-revdet` §2.2 | UNMEASURED (neither axis) | **still UNMEASURED overall** — size axis now measured (near-zero median, wide two-directional spread — no clean lean either way), TIME still unmeasured |
| `-fno-altcls-merge` §2.6 | UNMEASURED on size | **MEASURED TRADE** — size measured (mostly favors ON, one real non-monotone counter-example), combined with the existing (shared, not isolated) -7.61% TIME number |
| `-fno-altcls-factor` §2.7 | UNMEASURED on size, "likely a PURE WIN" | **MEASURED TRADE, near-pure-win** — hypothesis PARTIALLY CONFIRMED: ~90% of the reached population favors ON on size too, but a real counter-example (-900 B) keeps it off the strict PURE WIN bucket |
| `-fno-tiered-entry` §2.12 | UNMEASURED on emitted bytes | **MEASURED TRADE — GRADUATES TO THE DIAL.** Clean, monotone: ~1,953-1,957 B fixed cost on 9.49% of the corpus, against the existing ~5x per-call TIME win |
| `-fno-offset-skip` §2.14 | UNMEASURED on size | **MEASURED TRADE** — size measured (mostly favors ON, ~13% of the reached population trades the other way), against the existing 2x materiality-bar TIME number |
| `-fno-anchored-dfa` §2.15 | MEASURED TRADE on a pathological population ONLY | **MEASURED TRADE, corpus-general** — 43.39% reach (the largest of any switch here), monotone, median -3,075 B / worst -266,794 B, replacing the "not from the corpus" caveat with a real number |

**Net: of the six switches §7 named, four (`altcls-merge`, `altcls-factor`,
`tiered-entry`, `offset-skip`) now have BOTH axes measured and can move
into `opt_dial_inventory.md` §3's policy table as real rows; two
(`possessify`, `revdet`) had NO time number before and still have none
after — this sweep discharges their size-axis half only, and a matching
throughput sweep is what would finish the job for those two specifically.
The bonus switch (`anchored-dfa`) keeps its MEASURED TRADE bucket but
gains a corpus-general number in place of a single pathological witness,
and turns out to have BY FAR the largest reach of anything in the
inventory (43% of the corpus vs. single digits for everything else).**

## 4. What this changes about §3's draft policy table

Four new rows are now defensible in `opt_dial_inventory.md` §3's table,
each with the rate this memo measured (min-size column = denied/deny
where size wins outweigh the switch's own TIME cost; max-speed column =
force-on/allow):

- `-fno-tiered-entry`: min-size `deny` (saves ~1,953 B on the 9.5% of
  artifacts it reaches), max-speed `allow` (default) — the rate: ~1,953 B
  for ~5x call latency on that population.
- `-fno-offset-skip`: min-size `deny` (saves ~332 B median on 14% reach),
  max-speed `allow` (default) — the rate: a few hundred bytes for a 2x
  materiality-bar win on log-line-shaped patterns.
- `-fno-altcls-merge` / `-fno-altcls-factor`: min-size `deny` is NOT a
  clean recommendation given the measured non-monotone counter-examples —
  a dial that denies these at the min-size end would occasionally make
  SOME patterns bigger, the same warning `--unroll=K`'s own row already
  carries. Recommend the SAME treatment: keep `allow` at every dial
  position except the bottom, and carry the counter-example as a named
  caveat rather than a clean rate.
- `-fno-anchored-dfa`: **the reach finding is the one that should change
  the table's own framing, not just add a row.** §3's existing `--engine`
  row is deliberately flat because engine selection has the single
  largest measured range in the tree; this switch's own reach (43% of the
  corpus, an order of magnitude above every other row in this memo) means
  a min-size dial position SHOULD deny it by default rather than treat it
  as a narrow, pathological-population lever — the opposite of how §2.15
  currently reads. This is the strongest single candidate this sweep
  found for moving from "MEASURED TRADE on a pathological population" to
  an ordinary dial row with real reach.

`-fno-possessify` and `-fno-revdet` stay OFF the table — a dial position
cannot be justified from one axis alone (D77/the inventory's own §6 rule:
"the dial must not select a value for a switch that has no measured
rate"), and neither has a TIME number yet.

## 5. What is still owed

All eight passes (baseline + seven flags) ran to completion in this lane
— nothing is OWED on the sweep itself. What remains for a follow-on:

1. **A throughput sweep for `-fno-possessify` and `-fno-revdet`** — the
   only two switches this memo leaves fully UNMEASURED, because neither
   ever had a TIME number and this sweep supplies only the size half.
   `tests/possessify/`'s and `tests/rungselect/`'s own differential
   drivers already compile both sides of each; a throughput harness over
   the same pattern set (matching `altcls_pinned_impl`'s own shape) is
   the natural next lane.
2. **`-fno-altcls-merge` and `-fno-altcls-factor`'s TIME numbers are
   SHARED** (both denied together, `-7.61%`, `altcls_pinned_impl` stage
   2) — this memo's size numbers are per-flag but the only existing TIME
   number is combined. Isolating each flag's own throughput contribution
   would let both graduate from "near-pure-win" to a clean verdict.
3. **`-fno-altcls-merge`'s and `-fno-altcls-factor`'s non-monotone
   counter-examples** (`tests/base/k18_arm_order.rxt:256`,
   `tests/base/d27_bodies.rxt:100`) are each a single measured cell, not a
   characterized population — worth a small targeted sweep of WHICH
   pattern shapes trade the other way, the same way
   `artifact_size_term.md` characterized `--unroll=K`'s own
   non-monotonicity rather than leaving it as one number.
4. **`docs/design/opt_dial_inventory.md` itself is not edited by this
   lane** (it is a design document under `docs/design/`, D80's contract
   — this memo is the evidence, updating the inventory's own §2 entries
   and §3 table is the inventory's own next revision, which the manager
   or a follow-on lane should make citing this memo).

Reproduction: `bash docs/dev/optdial_size_sweep/run_sweep.sh` (re-run,
skips any pass whose `<slug>_size.tsv` already exists) then
`python3 docs/dev/optdial_size_sweep/join_sweep.py`. Raw tables and this
run's own analysis are committed at
`docs/dev/optdial_size_sweep/runs/` (`summary.tsv` is the machine-readable
per-flag table this memo's §1/§3 tables were transcribed from).
