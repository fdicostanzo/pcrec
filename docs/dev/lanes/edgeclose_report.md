# edgeclose — OPT-EDGE close-out + manifest re-pin (2026-09-21, lane edgeclose, sonnet)

Branch `lane/edgeclose` from main `b735df4d` (abi 28). Four tasks, all
admin. `git -C worktrees/edgeclose rev-parse --show-toplevel` confirmed
the worktree before any edit.

## Task 1 — stamp census manifest re-pin

The darwin gate at `579588da` was red on
`tests/codegen/run_cpset_structure.sh` CHECK 3: `tests/codegen/manifests/
m5_stage1_stamps.tsv` had drifted. Read the whole diff from the gate log
(`build/gate_579588da/test.log`) before re-recording, per r49: all 12
moved rows are `EMITTED_BYTES`, each +11 bytes exactly (e.g. `a`:
21292 -> 21303), and no `RX_ENGINE`/`RX_ENGINE_SEL`/`RX_DFA_TABLE`/
`RX_VM_RUNGS`/`RX_VM_STRATS`/`RX_VM_ALT_ISLANDS`/`RX_VM_FRAMELESS`/
`RX_DFA_PREFILTER` stamp moved — [REL-1.4]'s version stamp (D115, lane
rel1b), the unconditional " 0.1.0-beta" text plus the same-length
`.abi: 27 -> 28` digit substitution.

Re-recorded by moving the manifest aside and letting CHECK 3 write it
fresh, then diffed old vs new to confirm exactly these 12 rows moved by
exactly +11 each:

```
$ diff old_manifest tests/codegen/manifests/m5_stage1_stamps.tsv
5c5
< a	EMITTED_BYTES	21292
---
> a	EMITTED_BYTES	21303
... (11 more rows, identical +11 shape)
```

`make test-cpset-structure CC=gcc-16` run TWICE: first run recorded the
manifest fresh (28/28, `[3] manifest recorded for the first time`);
second run confirms it matches exactly:

```
== CHECK 3: the stamp census manifest (stage 1's half of §8.1.1 check 3) ==
PASS: [3] the census compiled 12 sample artifacts and recorded 76 stamp readings
PASS: [3] every stamp the census names was reached on at least one sample artifact — the instrument is live, not vacuous
PASS: [3] the recorded manifest (.../tests/codegen/manifests/m5_stage1_stamps.tsv) matches this run exactly

== CHECK 4: the interval algebra, model-checked against a bitset oracle ==
PASS: [4] cpset model check: PASS (400 trials x 60 ops + 7 edge cases)

checks passed: 28
checks failed: 0
```

Recorded in `tests/codegen/CLAUDE.md`'s CHECK 3 bullet (the manifest's
history is kept there, per the brief).

Commit: `828592bc`.

## Task 2 — [OPT-EDGE] close-out text (D117)

D117 (docs/dev/decisions.md, last entry) closes [OPT-EDGE] on
measured-no-gap: I-82 re-measured the scan-edge floor on the
edgefix-fixed harness, 0 of 16 cells separate under D77,
`PCREC_MIN_SCAN_CHAIN` stays at 2.

**(a) `docs/spec/tuning.md` §2.18** — one sentence appended to the
paragraph citing the 2026-09-04 floor measurement: "Re-confirmed
2026-09-21 on the fixed harness (I-82, D117): 0 of 16 cells separate —
the floor stays 2."

**(b) `src/core/limits.def:371`** — the `PCREC_MIN_SCAN_CHAIN` row's
measurement string (this is `--list-limits` OUTPUT, caller-observable
text) gains a matching re-confirmation clause. Grepped EVERY reader of
the row/string before editing:

- `tests/registry/limits_check.sh:134` — pins only the 58-name LIST
  (`PCREC_MIN_SCAN_CHAIN` appears as a bare name in an `EXPECT_NAMES`
  heredoc), not the measurement text; unaffected.
- `docs/spec/limits.md` — no mention of this row at all (`grep` empty).
- `oracle_store/`, every `.tsv` in the tree — none stores `--list-limits`
  output or this row's text verbatim (only `limits_check.sh` itself).

No reader pins the exact string, so the notes-text edit needed no
re-pin. Edited directly; verified `pcrec --list-limits | grep MIN_SCAN_CHAIN`
renders the new text and `tests/registry/limits_check.sh` is 24/24 green
(the 58-name pin unmoved).

**(c) `studies/scan_edge_ladder/README.md`** — new "Runs" section: archived
runs live under `runs/<date>-<item>-<pin>/`, I-82's run
(`runs/2026-09-21-i82-89d986c3/`) named with its pin, harness (lane
edgefix), `fit.py`/`fit_output.txt` beside the logs, analysis
(`docs/dev/lanes/edgefit_report.md`), ruling (D117). `studies/CLAUDE.md`'s
`scan_edge_ladder/` entry gained the matching one-line pointer.

Commits: `8115c243` (a+b), `18b0143c` (c).

## Task 3 — lane report inventory

`docs/dev/lanes/CLAUDE.md` had no entry for five reports merged today:
`rel1a_report.md`, `rel1b_report.md`, `rel1c_report.md`, `iface_digest.md`,
`edgefit_report.md`. One line each added, matching the file's existing
style (headline finding(s), not a restatement of the report's own intro).

Commit: `8f6a456f`.

## Task 4 — validation

**`make -j4 CC=gcc-16 && make strict CC=gcc-16`**: both clean.
`make strict` final line: `strict: whole tree compiles clean with -Werror -Wshadow`.

**`make test-cpset-structure` (from task 1)**: green both runs, see above
— 28/28, final run's CHECK 3 line `PASS: [3] the recorded manifest ...
matches this run exactly`.

**The `.def` string changed (task 2b), so the three owed follow-ups ran:**

`make test-registry` solo (`build/test_registry.log`, 631 PASS lines / 0
FAIL, every named sub-check's own `checks failed: 0`; PC-3 line
`checks passed: 209 / checks failed: 0`; PC-4/definitions-oracle line
`definitions-oracle: 354 cells, 101244 A==B comparisons, 101244 A==C
comparisons, 0 disagreements`).

`python3 scripts/emit_sweep.py --ref b735df4d`:

```
===== SELF-CHECK (ref vs. independent rebuild of the same rev) =====
-- stream: c-default --   population=3944 both_ok(reach)=3522 both_refuse=422 movers=0 asymmetric=0
-- stream: c-vm --        population=3944 both_ok(reach)=3523 both_refuse=421 movers=0 asymmetric=0
-- stream: emit-ir-vm --  population=3944 both_ok(reach)=3523 both_refuse=421 movers=0 asymmetric=0
-- stream: composition -- population=306  both_ok(reach)=33   both_refuse=273 movers=0 asymmetric=0
-- stream: dumps --       population=7    both_ok(reach)=7    both_refuse=0   movers=0 asymmetric=0
SELF-CHECK PASSED: all-identical, no asymmetry, at full reach.

===== REAL RUN: ref:b735df4d vs bin:.../build/pcrec =====
-- stream: c-default --   population=3944 both_ok(reach)=3522 both_refuse=422 movers=0 asymmetric=0
-- stream: c-vm --        population=3944 both_ok(reach)=3523 both_refuse=421 movers=0 asymmetric=0
-- stream: emit-ir-vm --  population=3944 both_ok(reach)=3523 both_refuse=421 movers=0 asymmetric=0
-- stream: composition -- population=306  both_ok(reach)=33   both_refuse=273 movers=0 asymmetric=0
-- stream: dumps --       population=7    both_ok(reach)=7    both_refuse=0   movers=1 asymmetric=0
```

Streams 1-4 (`.c` default, `.c` vm, `--emit-ir` vm, composition) are 0
movers / 0 asymmetric, as required. Stream 5 (registry dumps) moves by
**exactly 1 row**: `--list-limits`'s `PCREC_MIN_SCAN_CHAIN` row — the
diff hunk printed is exactly task 2(b)'s edit (the trailing
"RE-CONFIRMED 2026-09-21..." clause), nothing else in the dump moved.
`DELIVER witness: OK`.

`python3 scripts/m6read_check_sab_anchors.py` (run twice, before and
after all edits): `sabotages checked: 270 (286 anchor sites) / all
anchors resolve` — 286/286.

**`make test-codegen`**: `run_group: 9/10 scripts passed`, `checks
passed: 65 / checks failed: 0` on the last script before the summary.
The sole red is `run_inline_capability.sh`:
`FAIL: nm could not read arm_a.o (no rx_search symbol) — no verdict is
evidence here` — the standing darwin `nm` probe (BOILERPLATE.md box
facts / wake.md-era notes), matching the expected 9/10 shape exactly.

## Validation: COMPLETE

Every number above is measured on this lane's own tip, not inferred.
Nothing owed.
