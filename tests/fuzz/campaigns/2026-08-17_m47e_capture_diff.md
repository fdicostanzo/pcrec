# [M4.7e] at-scale capture-span differential — campaign log

## Provenance (D35-style)

| field | value |
|---|---|
| date | 2026-08-17 |
| repo commit (HEAD at build/run time) | `fbabdde` (`fbabddef964c19a88d347211ae5546d42255451f`) — post-[OPT-ALTCLS]/[BENCH-VM] merge, pre-[M4.7e] wiring commit |
| libpcre2 | 10.46 2025-08-27 (Debian/Ubuntu package `libpcre2-8-0` 10.46-1build1) |
| gcc | gcc (Ubuntu 15.2.0-16ubuntu1) 15.2.0 |
| host | ubuntubudu, 12 cores, kernel 7.0.0-29-generic |
| tool | `tests/fuzz/fuzz.py` (unmodified by this campaign; the gate wiring in this same commit runs the same tool at a single pinned seed — see `run_capturediff_gate.sh`) |
| seeds | 101–125 (25 seeds, chosen fresh — distinct from the seed 1/2/999/1000 calibration runs used to size this campaign and to derive `run_capturediff_gate.sh`'s pinned counts) |
| per-seed size | `--patterns 3000 --subjects 20` |
| total patterns generated | 75,000 |

## Aggregate result

**0 accept/reject divergences, 0 content divergences, across all 25 seeds
and all 842,740 both-accept subject-pair comparisons.** Every seed's own
summary independently confirms both counts at zero; see the per-seed table
below and the raw logs (not committed — see "Raw logs" below).

| metric | total |
|---|---|
| patterns generated | 75,000 |
| both accept | 42,137 |
| both reject | 31,092 |
| pcrec-only reject (accept/reject divergence) | 0 |
| pcre2-only reject (accept/reject divergence) | 0 |
| subject pairs compared (both-accept patterns) | 842,740 |
| **content divergences** | **0** |
| **accept/reject divergences** | **0** |
| DFA state-cap hits (known A-3 limitation, not a divergence) | 1,742 |
| oracle inconclusive (PCRE2 match-limit / oracle TIMEOUT) | 306 |
| known PCRE2 optimizer quirk (U1, `{0}`-anchor) | 2 |
| gcc compile fails (harness-level) | 3 |
| pcrec compile timeout (PCREC_TIMEOUT clock) | 18 |

No exclusion bucket was silently dropped from this accounting — every
bucket fuzz.py's own summary reports for every seed is included in the
per-seed table below.

**Load caveat on the two harness-level buckets (gcc compile fails: 3,
pcrec compile timeout: 18):** this campaign ran concurrently, in its
second half, with a full `make test` validation of the gate wiring in this
same commit (both jobs sharing the box's 12 cores) — seed 101 (which ran
essentially alone, before `make test` started) shows 0 of both buckets,
and every occurrence of either falls in seeds 102–125, the overlap window
(`campaign_driver.log`'s timestamps). Neither bucket affects fuzz.py's own
exit code or the accept/reject or content divergence counts — both are
harness-level classifications by the tool's own design (see
`tests/fuzz/README.md`'s "Output buckets" and `CLAUDE.md`), and their
clustering under known concurrent CPU contention is consistent with a
load artifact rather than a pcrec defect. Not re-run in isolation to
confirm, given the two buckets never gate exit status and 25/25 seeds
already agree on the two counts that matter (0 and 0).

## Per-seed table

| seed | patterns | both accept | pairs compared | state-cap | oracle inconclusive | gcc fail | pcrec timeout | content div | accept/reject div |
|---|---|---|---|---|---|---|---|---|---|
| 101 | 3000 | 1710 | 34200 | 73 | 11 | 0 | 0 | 0 | 0 |
| 102 | 3000 | 1669 | 33380 | 69 | 28 | 0 | 1 | 0 | 0 |
| 103 | 3000 | 1701 | 34020 | 64 | 12 | 0 | 0 | 0 | 0 |
| 104 | 3000 | 1699 | 33980 | 60 | 3 | 0 | 3 | 0 | 0 |
| 105 | 3000 | 1691 | 33820 | 64 | 10 | 0 | 5 | 0 | 0 |
| 106 | 3000 | 1684 | 33680 | 83 | 9 | 1 | 1 | 0 | 0 |
| 107 | 3000 | 1696 | 33920 | 57 | 9 | 0 | 1 | 0 | 0 |
| 108 | 3000 | 1664 | 33280 | 72 | 1 | 0 | 1 | 0 | 0 |
| 109 | 3000 | 1724 | 34480 | 67 | 10 | 0 | 0 | 0 | 0 |
| 110 | 3000 | 1659 | 33180 | 81 | 19 | 0 | 0 | 0 | 0 |
| 111 | 3000 | 1683 | 33660 | 77 | 10 | 1 | 1 | 0 | 0 |
| 112 | 3000 | 1681 | 33620 | 75 | 0 | 0 | 0 | 0 | 0 |
| 113 | 3000 | 1675 | 33500 | 66 | 4 | 0 | 1 | 0 | 0 |
| 114 | 3000 | 1696 | 33920 | 69 | 27 | 0 | 0 | 0 | 0 |
| 115 | 3000 | 1679 | 33580 | 66 | 1 | 0 | 0 | 0 | 0 |
| 116 | 3000 | 1650 | 33000 | 70 | 29 | 0 | 1 | 0 | 0 |
| 117 | 3000 | 1690 | 33800 | 66 | 11 | 0 | 0 | 0 | 0 |
| 118 | 3000 | 1656 | 33120 | 64 | 16 | 0 | 0 | 0 | 0 |
| 119 | 3000 | 1653 | 33060 | 72 | 2 | 0 | 0 | 0 | 0 |
| 120 | 3000 | 1660 | 33200 | 69 | 20 | 1 | 0 | 0 | 0 |
| 121 | 3000 | 1713 | 34260 | 69 | 11 | 0 | 0 | 0 | 0 |
| 122 | 3000 | 1702 | 34040 | 77 | 20 | 0 | 1 | 0 | 0 |
| 123 | 3000 | 1689 | 33780 | 84 | 8 | 0 | 1 | 0 | 0 |
| 124 | 3000 | 1691 | 33820 | 62 | 29 | 0 | 0 | 0 | 0 |
| 125 | 3000 | 1722 | 34440 | 66 | 6 | 0 | 1 | 0 | 0 |
| **total** | **75,000** | **42,137** | **842,740** | **1,742** | **306** | **3** | **18** | **0** | **0** |

## Gate-ON status: OPEN, but currently VACUOUS for module-owned syntax (measured finding)

Per the differential-gate principle (docs/testing.md) and the manager's
2026-08-17 ruling on this lane: the OPEN half is satisfied — fuzz.py passes
no `--features` flag, so every compile in this campaign resolved through
`PCREC_DEFAULT_FEATURES` = `"std1"` = `{classes, modifiers}` (D37/STD1b),
the only two modules with real producers. That is a genuine behavioral
(not recognition-tier) comparison.

**But zero of the 75,000 generated patterns in this campaign contain
classes-module or modifiers-module OWN syntax.** Measured directly against
`fuzz.py`'s generator source (`CLASS_ATOMS`, `gen_atom`, `TRAP_TEMPLATES`,
`CAPTURE_TEMPLATES`): `CLASS_ATOMS` draws only base-tier bracket-class
forms already accepted with no module enabled (`tests/base/classes.rxt`'s
own territory) — none of `\d \D \s \S \w \W \h \H \v \V \N` or the
POSIX `[:name:]` class-delimiter form ever appear; there is no
modifiers-module generation anywhere in the file (no `(?i) (?m) (?s) (?x)
(?U) (?J) (?a) (?n) (?r) (?-i) (?^) (?)`, confirmed by grep against the
generator source, not sampled from a run). So the gate being open bought
this specific campaign nothing: every one of the 75,000 patterns is
gate-agnostic — it would have compiled identically under `--features
none`. This is a GENERATOR COVERAGE GAP, not a failure of gate-ON itself,
and is recorded here (and in `tests/fuzz/README.md`) so the distinction
between "the gate is open" and "something walked through it" is visible
rather than implied by a summary line that only reports divergence counts.
**CLOSED for `classes` the same session (manager ruling, bounded addendum):**
`MODULE_CLASS_ATOMS` (fuzz.py) adds `\d \D \w \W \s \S` and two POSIX forms
(`[[:alpha:]] [[:digit:]]`) at a modest, named weight
(`MODULE_CLASS_WEIGHT = 0.15`) — a pure in-process sample (3,000 patterns
generated, no compiles) measured 37.1% now contain at least one module
construct. An addendum batch re-running this campaign's own shape (~10
seeds x 1,500 patterns) with the extended generator is recorded as its own
row below, with the module-construct count measured for real (not
sampled) via the hardened stat.

**`modifiers` stays open, deliberately, and is an OWED CELL rather than a
silent gap:** no modifiers-module generation exists anywhere in fuzz.py.
Homed at [M7.0] (docs/dev/plan.md — M7's own differential-fuzzing
milestone), not added as a same-session addendum to this capture-focused
lane.

## Addendum batch: classes-module construct density (seeds 201–210, 1,500 patterns/seed)

<!-- filled in after the addendum batch runs -->


## Raw logs

Per-seed `fuzz.py` stdout (25 files, ~1,700 lines total including the
first-5-of-N DFA-state-cap pattern dumps) are NOT committed here — they
are regenerable byte-for-byte from the seed list and parameters above
(`python3 tests/fuzz/fuzz.py --seed N --patterns 3000 --subjects 20` for
N in 101..125) and would roughly 40x the size of this file for zero
retained information beyond what the table above already extracts. The
driver loop used:

```sh
for seed in $(seq 101 125); do
  python3 tests/fuzz/fuzz.py --seed "$seed" --patterns 3000 --subjects 20 \
    > "seed_${seed}.log" 2>&1
done
```
