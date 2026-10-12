# pathreads — [CAND-PATH-READS] delivery report

Lane `pathreads` (opus, 2026-10-12), branch `lane/pathreads` from main
`23fb7a52`. Plan row `[CAND-PATH-READS]` (chunk 1 of
`docs/dev/chunks_2026-10-11.md`). Sabotage id used: **S844**.

## 1. Diagnosis

`cand_rows_selfcheck`'s `table-read-cycle` walks `cand_nodes[].reads` (with
`under`/`by` deny bits). It missed [REQ-HANDOFF-L1]'s recursion
(`axtri_report.md` §2: RECOVER `landing` -> NEXT `handoff-reentry` -> FIRST
`handoff` -> path -> RECOVER, pcrec SIGSEGV on `-e utf8 -fno-offset-skip
'€+'`) because three selection reads were not edges of that graph. The trace
build checked only reads made through `cand_read`; a predicate that selected
through any other reader was invisible to both the static walk and the
`undeclared-read` check. Measured with the new check (§2), the hidden reads on
the cand-oracle witnesses were:

| reader (slot / predicate) | selects | through | route(s) seen |
|---|---|---|---|
| FIRST `handoff` (`req_handoff_applies`) | LOCATE, RECOVER, FINISH | `cand_path_members` -> `cand_path_of` (`cand_locate_of`, `dfa_search_start_of`, `cand_finish_sel`) | LOCATE dfa/attempt/vm, RECOVER dfa, FINISH dfa/attempt/vm |
| RECOVER `landing`, `end-minus-width` | LOCATE | `cand_recover_asked` -> `cand_locate_of` | dfa |
| NEXT `handoff-reentry` (`req_landmark_admits`) | NEXT itself, under `-fno-req-handoff` | a direct `cand_select` for "the row below" | dfa |

The plan row named the first; the other two were found by the check. LOCATE
`empty` (named in axtri's open item) does NOT read the path:
`locate_empty_applies` calls `unanch_start` only; the path read near
`:4610` is `dfa_member_machines`, a stamp reader, not a predicate.

## 2. The change (no emitted byte moves)

All in `src/gen/emit_dfa.c` plus one line in `src/core/compile.c` and a
declaration in `src/core/internal.h`.

- **The edges, declared.** `CAND_PATH_READS` (beside `cand_nodes[]`) is the
  set of slots the path derivation selects in: LOCATE (all routes), RECOVER
  (CAND_ROUTE_DFA), FINISH (all routes). FIRST's `reads` names it. RECOVER
  declares `reads[LOCATE]` (DFA). NEXT declares `reads[NEXT]` (DFA) with
  `under[NEXT] = by[NEXT] = PCREC_NO_REQ_HANDOFF`, the deny its self-read is
  made under and the deny its reading row carries. With today's `under` bits
  the graph stays acyclic (the self-check is clean on every witness).
- **The check that holds the declarations to the code** (trace build only,
  the general mechanism, not a path-specific clause): `cand_select` now runs
  each row's predicate through `cand_applies`, which keeps a stack of the
  slots whose predicates are running; `cand_nested_read` holds every
  selection made while a predicate of slot P runs to `cand_nodes[P].reads` on
  that selection's route, else `CANDORACLE undeclared-read P SLOT route`. So
  the control reads the CALLS the predicates make, not the declaration it
  checks (learnings §3: a control must not share a source with what it
  controls). A check walk (`cand_select_quiet`, the entry slots' cross-route
  check) is not a read and runs with the stack set aside (a `base` index; a
  first draft zeroed the depth and the walk overwrote the reader's stack
  slot, which reported FIRST's path reads as PRESENCE's). A predicate can
  longjmp, so the recovery point in `compile_driver` empties the stack
  (`pcrec_cand_eval_reset`). Depth past 64 aborts `table-read-recursion`
  rather than overflowing the stack.
- **Default build untouched**: `cand_applies`/`cand_nested_read` are macros
  to the old expression outside `PCREC_CAND_TRACE`. Measured: `.text` of
  `emit_dfa.o` and `compile.o` byte-identical to the base build's. Not an abi
  event; no spec hunk (nothing caller-observable, D80).
- **Witness**: `cand_oracle_witnesses.tsv` gains `landing -e utf8
  -fno-offset-skip €+`, the compile on which FIRST `handoff`, NEXT
  `handoff-reentry` and RECOVER `landing` co-select (axtri's "newly
  reachable" combination, until now covered only by its own axis01 run).
- **Re-aim**: S607 (FIRST's `reads` line gained `CAND_PATH_READS`; the plant
  keeps it and still drops PRESENCE). Hand-verified DETECTED:
  `undeclared-read FIRST PRESENCE` on 63 witnesses. Every other anchor
  resolves (`scripts/m6read_check_sab_anchors.py`: 699 rows / 720 sites).

## 3. Sabotage S844 and the reach proof

S844 removes RECOVER's `.under = { [CAND_SLOT_NEXT] = PCREC_NO_REQ_HANDOFF }`
(the 9dec5e6f fix), arm `candoracle`, expected DETECTED. Hand-applied with
`tests/mech/lib/replace.py` (1 occurrence) to `git archive` trees, the same
plant on the base (main `23fb7a52`, hand-spelled for its one-line `reads`):

| tree + S844 | `run_cand_oracle.sh` (trace build) | default build, `-e utf8 -fno-offset-skip '€+'` | trace build, same |
|---|---|---|---|
| main 23fb7a52 (old check) | **90 passed / 0 failed** (the plant is invisible) | rc 139 SIGSEGV | rc 139 SIGSEGV |
| lane (this change) | 5 passed / 85 failed: 71 `table-read-cycle FIRST` + 14 take cells left unreached | rc 139 SIGSEGV | rc 134, `CANDORACLE table-read-cycle FIRST - selfcheck` |

So the plant reaches the binary (it is the real defect: the default build
recurses) and the new graph sees it at the static self-check on EVERY
witness, where the old graph read green. Once the new witness line exists,
main+S844 also goes red, but only by the core dump (`rc=139` on `€+`, 90/1),
never by a named check. Unplanted: lane 91/0, base 90/0 (+1 is the witness).

A second plant, not a row: dropping `CAND_PATH_READS` from FIRST aborts
`undeclared-read FIRST LOCATE` on 23 checks (dfa/attempt/vm), so a future path
reader left undeclared is caught by the nested check. It has no S-id; one is
needed if the manager wants it as a row.

## 4. Validation

Done in-lane (light): `make -j16` and `make strict` clean; trace build
`run_cand_oracle.sh` 91 passed / 0 failed; anchors 720/720; the two object
`.text` compares above; a 40-pattern trial of the trace sweep under `-e utf8
-fno-offset-skip` (0 movers, trace CLEAN).

**OWED** (heavy, one detached chain, `build/land/chain.sh` in the worktree,
log `build/land/chain.log`, completion line `CHAIN DONE`):

1. `make -j16`, `make strict` on the tip;
2. `make test-cand-oracle`;
3. `scripts/emit_sweep.py` lane vs base `23fb7a52` binaries: `--arms start`
   (all streams, every start arm incl. `-e utf8 -fno-offset-skip`) plus
   `--trace` on the default arm (`build/land/sweep_main.log`); then
   `--trace` arms `-e utf8`, `-fno-offset-skip`, `-e utf8 -fno-offset-skip`,
   `--engine=vm` (`build/land/sweep_*.log`). Expected: 0 movers, 0
   asymmetric, trace CLEAN on every arm (an undeclared nested read anywhere
   in the corpus aborts the lane's trace build and fails the trace gate);
4. `make test-recursion-identity`;
5. `make test` via `scripts/perfrun --label pathreads` (`build/land/test.log`;
   verdict `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'`, empty = green);
6. mech: S844 S607 S606 S608 S609 S610 S812 S810 S806 S807
   (`build/land/mech.log`, each row's own `== mech run COMPLETE` trailer).

Verdict lines: OWED (to be filled by the agent that reads the chain).

## 5. For the manager

- Plan row `[CAND-PATH-READS]` left `STATE:started`; flip at merge.
- Mech id used: S844 (one row). The nested-check plant (§3) has no row.
- No abi number, no spec, no pin moved.

## 6. pathtri (triage of the `--engine=vm` trace arm, 2026-10-12)

Lane `pathtri` (branch `lane/pathtri` from `lane/pathreads` d2650157).

**Diagnosis: (d), a sweep-harness issue; the lane's change is not implicated.**
`build/land/sweep___engine_vm_.log` shows 0 movers and 0 asymmetric on both
streams, trace-build stdout identical to the default build on both sides, and
the SET compare itself CLEAN. The two reds were floors calibrated for the
default engine: `RECORDS FLOOR ... c-default: 159657 < 270131` (the forced-VM
run carries the same 159,657 records on both streams) and "13/24 declared keys
reached" (the eleven DFA-machine decisions are never asked when every pattern is
forced to the VM). The same red reproduces with the BASE binaries on both sides
(`emit_sweep.py --ref-bin base --bin base --extra=--engine=vm --trace`, same
159,657 / 13-of-24), so it predates the lane; no `undeclared-read` abort fired
and no emitted byte moved (not (a), (b) or (c)).

**Fix** (`scripts/emit_sweep.py` only): `TRACE_EXTRA_PINS`, keyed by the exact
`--extra` tuple, gives that run its own records floor (measured, main
23fb7a52: 159,657 on each stream, binding both sides) and pins the UNREACHED
key set (the eleven names above) as an EQUALITY, so a key that starts or stops
printing is a re-pin and not a silent pass. Extras with no entry keep the
plain floors and the all-24-keys rule (the other four arms take the same path as
before). Failing directions: floor +1 -> `RECORDS FLOOR ... 159657 < 159658`
rc=1; a pin key renamed -> `UNREACHED SET differs ... newly unreached
['dfa-engine'], newly reached ['dfa-engine-X']` rc=1.

**Verdicts** (lane binaries from this worktree's own build vs the base binaries
under `worktrees/pathreads/scratch/reach/base`, read-only): `make -j16` rc=0,
`make strict` rc=0, trace build rc=0, `make test-cand-oracle` 92 passed / 0
failed, `emit_sweep` trace arms `-e utf8`, `-fno-offset-skip`,
`-e utf8 -fno-offset-skip`, `--engine=vm`: all rc=0, `trace: CLEAN`. The
`--engine=vm` run against the original `pathreads` binaries is also rc=0.

**The main chain must re-run:** only the `--engine=vm` trace arm of
`emit_sweep` with the new `scripts/emit_sweep.py` (merge `lane/pathtri`, or
cherry-pick 4936c259, into `lane/pathreads` before the detached chain's
remaining stages are read; the stages already run need no repeat, the
`main+arms+trace` stage does not use the new table). The chain's recursion
identity, `make test` and mech are untouched by this change.

## pathtri2 (2026-10-12, lane pathtri2, sonnet): triage of the d2650157 `make test` reds

Two reds, both LANE-CAUSED (main 23fb7a52 has neither: it has no
`CAND_EVAL_MAX`, and its `cand_select` calls `r->c.applies(s)` directly), both
CHECK-side, no `src/` change, no emitted byte moved (no abi event).

- **`test-registry` (`limits_check.sh` `[code]`, the D107 numeric-constant
  scan)**: `#define CAND_EVAL_MAX 64` (the trace build's stack of running
  selection predicates, `src/gen/emit_dfa.c`) is a new numeric `#define` on
  neither allowlist. It is the instrument's own overflow guard and fails the
  trace build loudly rather than overrunning; nothing a caller or pattern is
  measured against. Disposed on the LIMIT allowlist beside `LEGEND_MAX_*`
  (a debug-shaped bound), with its reason in the check's header. The scan's
  own pin is unchanged (3a is one PASS line; the registry's 37 stands).
- **`test-codegen` (`run_cand_rows.sh` -> `cand_rows_check.py`
  `[cand-route-walk]`)**: the check located `cand_select`'s predicate call by
  the literal `.applies(`; the lane routed that call through `cand_applies`
  (a trace-build function and a default-build macro), so the literal left the
  body and the check reported "not found". Re-aimed at `cand_applies(` AND
  made to read both definitions of it (each must still reach `.applies(`), so
  the indirection cannot become a way for the walk to stop asking the row.
  Failing direction, on a scratch copy of the tree: the default macro
  rewritten to `(1)` -> red (2 definitions found, one does not call
  `.applies(`); the route test removed from the body -> red (route test not
  before the applies call). Unplanted: green.

Validated on this branch (lane/pathtri2, tip below): `make -j16`, `make
strict` clean; `make test-registry` rc 0 (every section `checks failed: 0`);
`make test-codegen` rc 0 ("run_group: 16/16 scripts passed", no make error line). The default-build
.text claim for `emit_dfa.o`/`compile.o` is not touched by this change (only
`tests/` moved).

## s845row (2026-10-12, lane s845row)

The second plant of section 3 is now a row, S845
(`tests/mech/sabotages/S845_first_drops_path_reads.sh`, arm `candoracle`,
modelled on S844): one anchor line, `CAND_PATH_READS } },` in FIRST's `reads`.

REACH (by hand, trace build via `tests/codegen/run_cand_oracle.sh`): unplanted
tree 92 passed / 0 failed; the same tree planted (scratch `git archive` copy)
69 passed / 23 failed, all 23 `CANDORACLE undeclared-read FIRST LOCATE`.
Anchors: `scripts/m6read_check_sab_anchors.py` 700 rows / 721 sites, all resolve.
Matrix verdicts: see the handback (logs `build/mech_s845.log`,
`build/mech_s844.log` in the worktree).
