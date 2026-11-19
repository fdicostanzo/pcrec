# l1ftri2 — triage of the RED identity job on lane/l1ffix

## Summary
Class: a POPULATION defect in the job, no code fact. The job ran `emit_sweep.py` inside the BASE tree (`scratch/l1feat/trees/base`), so
its pattern population (`tests/**/*.rxt`) lacked the rows l1ffix/l1feat ADDED; `observed.tsv` (the r55-H compare) was built over the
FEATURE tree, which has them. Re-run with the feature tree as the sweep's cwd (ref-bin still the base build): population 7461 -> 7613,
`ident_check`: **0 unexplained**, facts-stream movers 422 = census movers 422, asymmetric 0 everywhere. No unexplained emitted-C mover.
Fixed job script: `l1ftri2_evidence/ident.sh`; re-run log `l1ftri2_evidence/rerun.log`.

## Why 64 unexplained
All 64 `CENSUS MOVER NOT IN THE FACTS STREAM` patterns are absent from the base tree's tests and present only in new test files
(`classify64.py`, listing every `.rxt` source of both trees): 51 in `tests/lookaround/d27_l1/l1d27_witnesses.rxt`, 12 in
`tests/litscan/spanarms.rxt`, 1 in both `spanarms.rxt` and `tests/litscan/presence_deny.rxt` (new). 0 exceptions: none is in the base
population, none lacks a source in the feature tree. Not a join or escaping defect (the 358 matching ones join fine; the same ident_check
passes once the population holds the rows). The earlier lane (l1ftri) never hit it because l1feat's new rows were all covered by the
base-tree population at its then-census.

## The C movers
Failed run (base-tree population, old rows only): c-default 11, c-vm 10.
c-default: `[a-z]+(?<=a)@x`, `(?:abc)+d`, `\w*(?=a)\w`, `[a-]{1,3}(?<=a|bc)\b`, `\w{1,3}(?<=a)b`, `\w+(?<=a)`, `(?=a(b)?)\w\1?`, `A*(?=a)\w`,
`\b(?=a)\w+\b`, `\w+?(?<=a)`, `\w+(?<=a)b?` (sources: landwalk.rxt, litscan/litrun.rxt, possessify/composition_d27.rxt). c-vm: the same minus `(?:abc)+d`.
The NEW one vs l1feat's 10/10: `(?:abc)+d` (tests/litscan/litrun.rxt), c-default ONLY (c-vm identical C). It moves because the fix's pin rule gives the
substretch `abc` a run_pin (explain.txt: pin-substretch PIN-GAIN, a census mover). First hunk: `RX_DFA_PREFILTER "offset-set"` -> `"run-pinned"`,
`RX_DFA_PREFILTER_OFFSETS "0,1*"` -> `"0,1*,2"`, plus an `rx_w2` helper, `while (pos+1<n)` -> `pos+2<n`, the candidate test `subject[cand]==97` ->
`rx_w2(..)=="ab" && rx_w2(+1)=="bc"`, `RX_RUN_WORDS 0` -> `1`, `.prefilter` string. Content the moved fact feeds, no scaffolding move.
Re-run over the feature population: c-default 62, c-vm 61, facts 533; every one is a census mover (ident_check 0 unexplained).

## Bench patterns 166 168 273
`abcdefghijklmnopqrstuvwxyzABCDE`, `abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMN`, `a+ab`, each compiled with `-e byte|utf8` x default|`--engine=vm`
(`-o - --pattern`), base 07c840368 build vs the l1ffix build (frozen f8e38102b; `git diff f8e38102b 8c7d54594 -- src cli lib memfn` is empty, so it
is also 8c7d54594's compiler): **C IDENTICAL in all 12 compiles** (same byte counts, `diff` 0 lines). The run_pin gain is a facts-only
move for these three; it reaches no emitted text.

## Fixes
`l1ftri2_evidence/ident.sh` (committed): `env -C <feature tree> python3 scripts/emit_sweep.py --ref-bin <base build> --bin <feature build> ...`
and ident_check given the feature tree. The queued job's script is the copy at `scratch/l1ffix/ident.sh`; retry after replacing it
with this one (main's call; I queued nothing and did not touch worktrees/l1ffix).

## STATE AT HANDOFF
Rulings file: present, empty of rulings; none applied. Re-run done by hand: ident_check "0 unexplained" (rerun.log).
OWED: none
