# r32 — [MEMFN] R-32: re-aim sabotage row S526

STATE: delivered (mech proof OWED: one queue job staged, not queued)

## Cause

S526's catch is C14 (`tests/memfn/form_checks.py`, arm `memfnforms`): a syntax-only probe TU of
`_Static_assert`s compiled against the tree's headers. The check already FAILS BY ASSERTION in
python (`bad(...)`, "checks failed: 1"), not by breaking the suite's own build. But its FAIL line
quoted the probe compile's raw stderr (`' '.join(err.split())[:300]`), which carries gcc's
`/path/real.c:L:C: error: static assertion failed: ...`. Since 7047b69e4 `score_arm` greps a failing
arm's log for `NOCOMPILE_ERE` (`file:L:C: error:`) and marks the row `any_nocompile`, which the verdict
block renders as ANOMALY ahead of DETECTED. So the scorer misread the check's quoted diagnostic as
code under test failing to compile.

## Chosen option

Neither (a) nor (b) as phrased; a smaller third: C14 keeps its probe-compile design and control
structure, and its FAIL line now prints only the tripped assert messages (`c14_asserts` in
`tests/memfn/form_checks.py`: the `static assertion failed: "..."` strings, joined; fallback is the
raw text with `: error:` rewritten so it cannot match the ERE). Why not (a): replacing the static
assert with a python int comparison of MF_MAX_TERM vs VM_MAX_STRIDE would drop the compile of the
real header against the real `core/internal.h` (limits.def), which is the check's point, and the
two parsed numbers would come from the same text the plant edits. Why not (b): no other existing
check observes MF_MAX_TERM 31 (the forms/finder checks do not exercise a 32-wide strided site).
The row file changed only in a header note and SAB_DOC_FIGURE; plant, SAB_REACH and its expect are
untouched. Nothing under `src/`, `cli/`, `lib/` or `memfn/` changed; no byte reaches a pcrec
artifact (no abi event).

## By-hand plant evidence

Scratch copy `/var/tmp/pcrec-pcrec/scratch/memfn/r32/plant` (lib, src, memfn/include, tests/memfn
from the worktree), plant applied as the row does (MF_MAX_TERM 32 -> 31; emit_vm.c's build assert
removed), `bash tests/memfn/run_form_checks.sh <copy>`:

    FAIL: C14: a shape bound fails: C14 stride: MF_MAX_TERM must hold VM_MAX_STRIDE positions (one strided site)
    PASS: C14 control: ... PASS: C14 stride control: ...
    checks passed: 4 / checks failed: 1

`grep -cE` of the scorer's `NOCOMPILE_ERE` over that output: 0. Clean worktree: `checks passed: 5`,
`checks failed: 0`, the SAB_REACH_EXPECT lines present.

## Control independence

Unchanged and untouched by the edit. The two in-script controls compile the same asserts against
copies of memfn.h lowered to the offset-skip bound (4) and to `stride - 1`; each must trip ITS OWN
assert message and not the other (`'PCREC_OFSK_MAX_SET' not in err3`). They read the bounds from
limits.def and emit_vm.c, not from the MF_MAX_TERM the plant edits, and the row's REACH line is a
clean-tree pass of the stride control. The edit only changes how the failure is worded, not what
counts as one, so the check's ability to fail is as before (the plant run above is the witness).

## Owed

`docs/dev/lanes/r32_jobs/mech-s526.sh` (dry-run clean; est 180 s, cap 900; steps: mech S526
requiring the trailer `1 rows (unexpected: 0, undetected: 0, unreached: 0, anomalies: 0`, then
`make strict`, then `make test-memfn-forms`). NOT queued. The scorer's DETECTED reading itself is
unmeasured until that job runs; SAB_DOC_FIGURE says so ("Read the current figure from a run").
