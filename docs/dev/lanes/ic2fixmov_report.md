# ic2fixmov report: triage of the mover-census red of job 640-ic2fix-test

## Summary
Job 640's full make test and strict were green. The census was red for one
reason: `ic2_movers.py` classified two composition asymmetries as unexpected.
Both are review fix F7's intended behaviour (a file build compiles every
target before writing any). No answer change, no unexpected mover outside
callout/code/dump artifacts. Tool fixed (ic2_movers.py only); my own rerun ends
`movers: DONE rows=221 unexpected=0`. The job's witness pins rows=219; the
true count is now 221 (the two F7 rows were already counted as unexpected, but
the witness was recorded before them being classified: re-pin to 221 on requeue).

## Sweep failures
- `emit_sweep: DONE rc=1` cause: `COMPOSITION ARTIFACTS FLOOR VIOLATION: 86 < 100`
  (composition_artifacts_floor, emit_sweep.py PINS). The WORK side now writes
  fewer composition artifacts (F7 below), so the plain-arm count (floor 100,
  was measured at 106) falls. A sweep-tool pin, not a compile failure. The job
  script does not test emit_sweep's rc, so this alone did not fail the job.
  emit_sweep.py was NOT edited: re-measuring that floor is the manager's call
  (a pin move, owed to the F7 landing).
- The `-rc=1 / +rc=0` lines are MOVER diff hunks (the "default rc=1" the brief
  saw): REF refuses `(?C`c: ...`)` patterns (side A rc=1), WORK compiles them
  (module code-c). That is the ic2 feature itself, 34 rows per c-stream; all
  contain `(?C`, 0 unexpected.
- Not a refusal on one side at the pattern level: no pattern asymmetry.

## Mover census
Ran the job's steps in build/ic2fixmov/ (ref 6d0974b74 at abi 90, nice, jobs 8,
corpus + 336 bench patterns). Result `movers: DONE rows=221 unexpected=0`.
Per stream: c-default 34, c-vm 34, emit-ir-auto 21 (x4 prefilter arms), emit-ir-vm
21, facts 21, stderr 21 (all `(?C` patterns: code-c now a module row), dumps 3
(--list-syntax, --list-families, --list-schema: new code-c row / code-header
line), composition asymmetric 3 (below).
The job's two unexpected rows (composition, both F7, CON-9):
1. tests/rxtsource/fixtures/compose_encoding_clash.rxtin: target `ok` compiles,
   target `clash` is refused (encoding utf8 vs byte). REF wrote ok.c/ok.h then
   failed; WORK writes nothing (F7). Expected: F7.
2. tests/rxtsource/fixtures/bench_altwide_0_2.rxtin: 11 targets, `s_4096` is
   refused on both sides (1624182 bytes > max-emit 1000000). REF wrote the 22
   earlier artifacts; WORK writes none. Expected: F7.
Third composition row: tests/code/ipv4.rxt (REF: 'code-header' not a file-level
directive; WORK compiles): expected (tests/code file).

## Fixes
docs/dev/lanes/ic2_movers.py: a composition row is expected when the WORK side
wrote no artifact (`side_b_ok=artifacts=[]`), documented as F7/CON-9 in the
docstring. Narrow: REF-empty or other name-set diffs still flag. No src/ edit.

## STATE AT HANDOFF
Branch lane/ic2fix, tool fix committed on top of 0245c93b2. Census rerun
unexpected=0. Rulings file: none present (no entries applied). Owed to the
manager: re-pin job witness movers rows=219 -> 221; re-measure
composition_artifacts_floor for the plain arm (86 now vs floor 100) in
scripts/emit_sweep.py, or leave since the job ignores the sweep rc; requeue.
Scratch: build/ic2fixmov/ (gitignored).
