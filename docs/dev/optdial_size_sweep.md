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
growing-population formulation, 4,121 `pattern` lines across 314 files at
this lane's branch point (`git -C . grep -c '^pattern '` summed). The
sweep does not hand-pick files: it invokes `tests/harness/run.sh` with no
file/dir arguments, `run.sh`'s own "every `*.rxt` under `tests/`" rule —
the same population `docs/dev/artifact_size_log.tsv`'s committed baseline
uses. A pattern block that refuses to compile under a flag, or is
excluded from `SIZELOG` for any other harness reason (`perr`, a routed
cell), contributes no row on that side and is accounted as LOST/GAINED
below rather than silently dropped from the denominator.

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

<!-- RESULTS_TABLE -->

## 2. Per-switch findings

<!-- PER_SWITCH_SECTIONS -->

## 3. Updated inventory verdicts

<!-- VERDICT_TABLE -->

## 4. What this changes about §3's draft policy table

<!-- POLICY_TABLE_UPDATE -->

## 5. What is still owed

<!-- OWED -->
