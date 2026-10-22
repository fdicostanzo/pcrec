# wsc7 - D172 S2 commit 6, the final fixes (the kit manager's brief; main's conditions)

Lane wsc7, 2026-10-22. Worktree `worktrees/wsc7`, branch `lane/memfn-wsc7`, cut from `lane/memfn-wsc6` @ 9c29d8f15.
Read wsc6_report.md first. Heavy job 582 was RED with no miscompile and no answer change; this lane fixes
exactly what its triage named. Rulings file `wsc7_rulings.md`: last entry applied = "2026-10-22, main
APPROVED" (the declared facts delta, F-3 added to scope).

STATE AT HANDOFF:
- Items 1, 2, 3, 4 and F-3: done, light checks green at the tip (section 3).
- **Owed:** heavy job `583-kit-wsc7-heavy` QUEUED at the final tip (section 5); every verdict is the fresh
  agent's to read. The tree is clean after queueing; do not edit `worktrees/wsc7` until it has started.

## 1. The commits (path class per commit; main reviews the pcrec-path ones)

| # | sha | path class | what |
|---|---|---|---|
| 7-p1 | 416a1cbe6 | PCREC PATH (src/ only: facts.c, facts.h, known.c, emit_dfa.c) | item 1 and item 2 |
| 7-p2 | 0ce972b9b | PCREC PATH (src/core/limits.def only) | F-3 |
| 7-t1 | 79dc8af42 | TESTS + TOOLING (tests/mech/sabotages, scripts/) | item 3 and item 4's check |
| (r) | this commit | docs (`docs/dev/lanes/`, the lane index, the kit journal) | this report |

Condition 1: each commit's file list was checked before committing. Condition 3: pcrec states only R-29's
facts; no D157 breach (no kit method named anywhere in the pcrec-path hunks).

### 7-p1, item 1: the trace shadow's span read is a non-pass ask
`pcrec_fact_span_stated` (`pf_ask(cx, PF_SPAN, false)`, src/facts/facts.c, beside
`pcrec_fact_req_run_stated`). C8's `cc_exact` (src/gen/known.c) reads it unless
`pcrec_kit_proof_routed(cx)`, where the harness-routed cover decision keeps the pass ask. The trace build's
`locate_cover_applies` -> `pcrec_cover` walk no longer sets `span_facts` used, so its `used` column is the
default build's. `make test-cand-oracle`: 171 passed, 0 failed (582 had 21 FAILs in `[pres-picks-used]`).

### 7-p1, item 2: the 6-p4 positional read
`struct MemfnFind` (src/gen/emit_dfa.c) records the D11 bound its define stated (`holdback`, from
`PcrecFind.holdback`). `unanch_scan`'s storage point passes it to `pf_find_of`, and `find_use`'s loud check
compares it with the use's, so neither reads the bound back from the statement's span length by position.
Byte identity: 28 compiles (14 patterns, each with and without `-fno-offset-skip`, among them `\bx`,
`\B(?<!a)d`, `\bcat\b`, `a\Bb`) identical to the wsc6 tip's build; the heavy job's five sweeps are the witness.

### 7-p2, F-3
`PCREC_OFSK_MAX_SET`'s `--list-limits` description is "how many offsets the selected offset-set prefilter
candidate may carry" (no file name). A declared dumps delta: that one line, checked by item 4's check.
Measured against the 3cd809da1 binary: `--list-limits` differs by that row only; the other six surfaces are
identical.

### 7-t1, item 3: the stale plants
- **S293 retired** (file deleted; its reader `ofs_pred_of` is gone). S1415/S1416 do not cover it (they plant
  the window family's C-pin), so the successor is **S1421-reqrun-member-offset-dropped**: the kit renderer's
  `hit - member` subtraction (memfn/src/ofsskip.c `memchr_body`, `- %d` with k) dropped. Same witness
  (tests/base/k66_precheck_whole_run.rxt, `a=b` under `-fno-offset-skip`). Solo
  `run_sabotage_matrix.sh S1421`: **DETECTED** (reach ok 1/1, prechecks 4 fail / 391 pass, corpus 4 fail /
  12 pass).
- **S1138 re-aimed**: widens the stated window's span 0, position 0 (`s->alts[0]` span 0 `set[0]`) between
  `pcrec_cover_site` and `pcrec_memfn_define` (a cast through the statement's const spans). Solo: **DETECTED**
  (reach ok 1/1, kitproof 71 fail / 17 pass).

### 7-t1, item 4: the declared facts delta (main APPROVED; no abi event, no spec hunk)
6-p3 removed the default build's only pass-ask of `span_facts`, so the `--emit-facts` `used` column flips
yes -> no wherever it read yes (about 3,356 patterns; the heavy job's count is the record). The reason is
facts_listing.md section 4.1 paragraph 2: stating a span to the kit never sets `used`. Do NOT re-add the pass
ask.

The check is in `scripts/emit_sweep.py`, with self-tests in `scripts/tests/emit_sweep.py.test`:
- `--facts-declared-moves FACT:COLUMN:FROM>TO` (here `span_facts:used:yes>no`): per pattern, every data row
  of the NEW listing equals REF's except the declared cells, and EVERY REF row holding FROM has moved to TO
  (a declared move that did not happen, the move the other way, any undeclared row, a comment line or a line
  count that moved each fail). The stream is then required at movers=0 and reports
  `DECLARED MOVES ... patterns=N rows=M`.
- `--dumps-declared-rows FLAG:KEY` (here `--list-limits:PCREC_OFSK_MAX_SET`): on that surface the keyed row
  must differ and every other line must be byte-identical.
Smoke against the 3cd809da1 binary: 20 patterns, 17 with the declared move, 0 problems.

## 3. Light checks at the tip (79dc8af42; `build/wsc7/light.sh`, logs `build/wsc7/light/`)

| check | result |
|---|---|
| `make strict` | clean |
| sabotage anchors (`m6read_check_sab_anchors.py`) | rc 0 |
| `tests/codegen/run_codegen_tests.sh` | 331 / 0 |
| `make test-core` | rc 0 |
| test-memfn-manifest / arch / forms / reach / link / stamps / guarded / simdfloor | 15 / 17 / 5 / 4 / 8 / 25 / 10 / 51, 0 failed each |
| test-memfn-rank / arms / deleg / rows / finder | 6 / 374 / 14 / 231 / 2267, 0 failed |
| test-memfn-g2 (quick) | 70,358,651 / 0 |
| `memfn/tests/run_g2_win.sh` | 6032 / 0 |
| `run_wreply.sh` | 112 / 0; `--plants` rc 0 |
| lever fence (`tests/compound/run_lever_fence.sh`) | rc 0 |
| test-kitproof | 88 / 0 |
| `make test-cand-oracle` | 171 / 0 |
| limits_check / `make test-registry` | 37 / 0; rc 0 |
| S1421, S1138 solo | DETECTED, DETECTED |
| emit_sweep.py.test | 0 failed (run once before the dumps control was added; the dumps control was run directly) |

## 5. The heavy job: `583-kit-wsc7-heavy` (OWED)

Queued at the final tip (the tip is this report's commit). Its `--ready` holds on main's `i2build-parity`
(`pending*|running*` -> held, 75); `idle-ok`; cap 18000. Script: `build/wsc7/583-kit-wsc7-heavy`, queue
copy and `job.log` under `worktrees/.boxqueue/done/<ts>-583-kit-wsc7-heavy/`; step logs
`worktrees/wsc7/build/wsc7/heavy/*.log`. Steps (every one runs):
1. `make -j16`
2. five `emit_sweep` arms against 3cd809da1 (plain with the dumps stream added, `--arms start`,
   `-fno-run-prefilter`, `-fmemfn-simd`, `--engine=vm --no-differ-floor`), every one with
   `--facts-declared-moves='span_facts:used:yes>no'` and `--dumps-declared-rows=--list-limits:PCREC_OFSK_MAX_SET`;
   artifact streams at movers=0
3. `run_wreply.sh` and `--plants`
4. `REACH_ONLY=1 PROCS=4` over 582's reach set (373 rows; S293 out, S1421 in)
5. ONE `PROCS=4 run_sabotage_matrix.sh` over 582's 155 ids (S293 out, S1421 in, S1138 re-aimed)
6. `scripts/perfrun --label wsc7` (make test)

Completion lines to read (job.log): `== wsc7 heavy: 0 step(s) failed`; five `emit_sweep: DONE rc=0`
(declared counts: `DECLARED MOVES ... patterns=N rows=M` in `build/wsc7/heavy/sweep_plain.log`'s facts
stream, and the dumps stream's 1); `== mech run COMPLETE: 155 rows (unexpected: 0, undetected: 0, ...)`;
`mech-reach-only: DONE`; the make verdict `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'
build/wsc7/heavy/maketest.make.log` (empty = green).
