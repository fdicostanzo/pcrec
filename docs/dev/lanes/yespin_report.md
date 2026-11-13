# yespin report

## STATE AT HANDOFF

Re-pin done and committed on lane/yespin (branch pushed). Validation: the
plain and lowthr byte cells are MEASURED (run1: the only two floors that read
red were the 'yes' floors, 1727 < 1740, on `emit-ir-auto` and
`emit-ir-auto[-fno-prefilter-collapse]`; every other floor held, 0 movers, 0
asymmetric, corpus 7,034 rows). The full `--variant all` re-run on the edited
script is OWED: log /var/tmp/pcrec-pcrec/scratch/yespin/run2.log, completion
line `VARIANTS: ok` (or `VARIANTS: FAILED` plus TAG FLOOR lines); it is running
detached. Both runs were manager-approved unlocked runs (PCREC_BOXLOCK=0, nice
-n 19, jobs=2; main's say-so after the first attempt queued 14 min behind
kit job 450). A fresh agent or main reads run2.log; if it names another stale
floor, re-pin it from `out2`'s `--emit-pins`-style tallies.

Cause (bisected): a60681ae2 (lane nevermatch, abi 100 -> 102, merged by
004a7849e) makes a never-matching VM hybrid the DFA empty artifact; a DFA
winner refuses `--emit-ir`, so those patterns moved 'yes' -> 'refused'.
Evidence: 16 distinct corpus patterns read 'yes' at 646a8c0be (kclose4 pin)
and at tip build 233e0af5d none do; at 004a7849e^1 and dac304348 (the WIP
before a60681ae2) all 16 are 'yes', at a60681ae2 and 004a7849e all 16 are
not. They are the never-match set: `(?=a)z`, `((?=[ab])z)`, `((?*a)z)`,
`(?>a\b)c`, `(?>a|ab)\bc`, `(a)\b(b)`, `(a+)\b(?1)`, `a\K\bb`, `a(?=b)\Kc`,
`(?=a)\Kb`, `(?<g>\w\b)(?&g)?x` and the `(?>...)`/`(?*...)` siblings. That is
13 corpus rows (some patterns repeat). Intended effect (nevermatch's "+16
hybrids" in the partlayout set), not a wrong answer or lost optimisation.
S1 51481d1b3 only carries it (its first parent still reads all 16 yes); K38-2 was
not separately built, since the bisect already pins all 16 movers on a60681ae2.

## CHANGES

scripts/emit_sweep.py: `'yes': 1740` -> `'yes': 1727` in four cells
(VARIANT_PINS ('lowthr','byte') and ('plain','byte'), keys `emit-ir-auto`
and `emit-ir-auto[-fno-prefilter-collapse]`), with a RE-PINNED 2026-11-13
comment naming a60681ae2 beside the kclose5 comment. No other cell changed.
Scratch only: bisect builds under $PCREC_TMPDIR/scratch/yespin/b (no
worktrees created).
