# w1stage0_report.md — [REVW.1] wave 1 stage 0 (2026-09-17/18, lane w1stage0, sonnet)

Task: wave 1 stage 0 of the emission-kit refactor, plan row [REVW.1].
Authority: `docs/dev/reviews/lens_reports/lens10_emission_kit_charter.md`
STAGE 0, plus EP2's two additions in `emitvm_second_pass.md` §5/§7. Branch
`lane/w1stage0`, worktree `worktrees/w1stage0`, off `main` at `272bf970`.

**Full findings and validation transcripts: `docs/dev/w1stage0.md`.** This
report is the delivery summary.

## Deliverables, all landed

1. **The long-prefix full-corpus sweep**
   (`tests/codegen/run_longprefix_sweep.sh` +
   `docs/dev/w1stage0_evidence/longprefix_sweep.py`). Repairs the
   [MECH-REACH] gap the charter's F3b names — the tree's only prior
   long-prefix control compiles the pattern `a`. Compiles every corpus
   pattern at `-p rx` and at the legal 60-byte prefix boundary, gcc-compiles
   the 60-byte artifact under the harness's own GENCFLAGS wherever pcrec
   accepts it. Committed baseline:
   `docs/dev/w1stage0_evidence/longprefix_baseline.tsv` (3,938 rows).
   **MEASURED: 1,499 of 1,500 rx-compiling patterns also compile at 60
   bytes (the one exception is a size-cap refusal on a deliberately
   pathological witness, `k18_cost_gates.rxt`, not a miscompile); zero gcc
   `-Werror` anomalies — no live K38 recurrence found.**
2. **The irsb byte-neutrality arm** (EP2). A new BYTE-NEUTRALITY block in
   `tests/codegen/run_ir_listing.sh`, riding its existing 11-pattern
   population, diffing each pattern's `--emit-ir` listing byte-for-byte
   against a committed baseline (`tests/codegen/manifests/
   ir_listing_baseline/`, captured via the new opt-in
   `CAPTURE_IR_BASELINE=1` mode). Pins the OUTPUT bytes, not the render
   mechanism (D108). Sabotage row S258 added and verified DETECTED (both
   directions: UNDETECTED against the pre-arm commit, per mech's own
   `git archive HEAD` shape; DETECTED against the commit that lands the
   arm).
3. **The listing-reach census** (EP2). `docs/dev/w1stage0_evidence/
   listing_reach_census.py`: measures whether `run_ir_listing.sh`'s
   population actually reaches the rung emitters whose `vm_rolef` role text
   is the listing's own content. **MEASURED: 27 of 41 `vm_rolef` call
   sites reached (66%) by the 11-pattern fixture; 31 of 41 (76%) by the
   whole corpus at default engine selection — both miss lookbehind and
   subroutine-call emission entirely.** Measurement only, per stage 0's own
   charter; recorded as the population fact a future stage-3 lane needs.

Stage 0 is nets + measurement only, as briefed: nothing under
`src/`/`cli/`/`lib/` was touched, and no kit primitives were built.

## Commits (in order, each independently validated before the next)

1. `4f2a387d` — deliverable 1 (script + wrapper + committed baseline).
2. `27cc5ab0` — deliverable 2 (the arm + baseline `.ir` files + S258).
3. `bc28a257` — deliverable 3 (the census script + its log).
4. `40ba734c` — docs (`docs/dev/w1stage0.md`,
   `docs/dev/w1stage0_evidence/CLAUDE.md`, `docs/dev/CLAUDE.md`,
   `docs/testing.md`, `tests/codegen/CLAUDE.md`).

## Validation performed

- `make -j4 CC=gcc-16`: clean.
- `bash tests/codegen/run_longprefix_sweep.sh`: PASS, row count 3,938
  matches `run_rxtsource_tests.sh`'s `CENSUS_BLOCKS` pin exactly; 0 gcc
  anomalies. Re-run a second time after all commits to confirm stability
  (owed — see below).
- `CC=gcc-16 bash tests/codegen/run_ir_listing.sh`: **93 passed / 0
  failed**, both before and after all four commits.
- Sabotage S258 via `bash tests/mech/run_sabotage_matrix.sh S258`: ran
  TWICE by design — UNDETECTED before the arm's own commit landed
  (`irlisting` arm's own log showed no red; mech builds from `git archive
  HEAD`, so this is the expected shape, not a failure), **DETECTED** after
  (`irlist:3fail/90pass`).
- `bash tests/rxtsource/run_rxtsource_tests.sh`: **212 passed / 1 recorded
  / 0 failed**, `INV-COMPAT holds over 211 files / 3938 blocks / 28949
  expectation lines` — unaffected by this lane (no `.rxt` file touched),
  confirmed unchanged from its pre-lane count.
- `make strict CC=gcc-16`: clean (`whole tree compiles clean with -Werror
  -Wshadow`).
- Full `make test`: launched backgrounded as this lane's last act per
  BOILERPLATE's DO-THEN-FINISH. Log: `build/w1stage0_test.log` in the
  worktree, sentinel line `TEST_RC=<n>` appended at completion. **OWED** —
  see the handback message for the exact command and how to poll it. Known
  pre-existing red per the brief: the darwin `inline_capability` nm-probe
  FAIL (carries TEST_RC=2) — not this lane's.
- The second `run_longprefix_sweep.sh` re-check (started as this report was
  being written, to confirm post-commit stability) is also owed — its
  output path is `build/longprefix_recheck.tsv`; if it has not completed by
  hand-off, a fresh agent or the manager can poll it, though the FIRST run
  (pre-commit, identical script and identical corpus) already gives the
  numbers in this report and the script makes no state-dependent choice
  that a commit could change.

## Notes for whoever picks up stage 1/2/3

- The BYTE-NEUTRALITY arm's reach is exactly `run_ir_listing.sh`'s existing
  11-pattern population (66% of `vm_rolef` sites). A stage-3 lane touching
  the counter rung, a lookbehind branch, or subroutine-call emission should
  NOT read this arm's green as proof those paths are byte-neutral on
  `irsb` — see `docs/dev/w1stage0.md` §3's "Consequence" paragraph.
  Widening `PATTERNS` (or adding a second population) is a stage-3-scoped
  decision, deliberately not made here.
- The long-prefix sweep's committed baseline
  (`docs/dev/w1stage0_evidence/longprefix_baseline.tsv`) is keyed by `idx`
  (the pattern's position in a `find`-sorted, `--list-source`-ordered
  enumeration of `tests/**/*.rxt`). A stage-3 lane diffing against it
  should re-derive the same enumeration via the same script rather than
  assume row order is stable across an unrelated corpus edit — the row
  COUNT is tripwired against `CENSUS_BLOCKS`, but nothing pins that row 500
  is still the same pattern text after a `.rxt` file is added/removed
  elsewhere in sort order. (The `pattern` column carries the actual text
  for exactly this reason — a future diff should join on it, not on `idx`,
  if the corpus has moved.)
- `k18_cost_gates.rxt`'s witness is now doubly interesting: it is both the
  D6 panel R23's original chartering witness for a different study
  (`dfa_online_minimization_study.md`) AND, per this stage's sweep, the
  ONE corpus pattern that hits `PCREC_MAX_EMIT_BYTES` under a 60-byte
  prefix. Not a defect — named here so nobody re-discovers it as one.

## Rulings received

None — no ruling was requested or issued during this lane's run.
