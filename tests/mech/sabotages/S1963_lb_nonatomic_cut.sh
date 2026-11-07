# S1963 ([VLOOKBEHIND] stage 1, design §7 W5) -- THE NON-ATOMIC RETRY. A
# non-atomic lookbehind leaves its candidate frames live, so a later failure
# retries the next candidate; cut, only the first candidate is ever seen.
# RE-PLANTED 2026-11-06 (lane vlbfix, review r4 F6): the first plant only made
# `vm_look_needs_mark` answer true, but the body-success cut is `if (atomic)`,
# so the mark was written and never read (UNDETECTED by construction, 54/0).
# A TWO-SITE ROW by necessity: the cut needs a mark slot (site 1) AND must be
# emitted for the non-atomic form (site 2); either alone is a no-op.
SAB_ID="S1963-lb-nonatomic-cut"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/lookaround/lookbehind_variable_witness.rxt"
SAB_DESC='every positive lookaround cuts its frames at body success (a mark for every form, the cut unconditional), so the non-atomic (?<* keeps no candidate retry'
SAB_DOC_FIGURE='MEASURED (lane vlbfix, tools/review/plant.sh + harness on the target): 47 pass / 7 fail, W5 both cells (lines 45, 52: match 3 5 -> nomatch) and W16 (line 229: match 2 4 -> nomatch); clean 54/0.'
SAB_COUNT=1
SAB_BEFORE='    return a->u.look.atomic || a->u.look.neg;'
SAB_AFTER='    return a->u.look.atomic || true;   /* SABOTAGE S1963 */'
SAB_FILE2="src/gen/emit_vm.c"
SAB_COUNT2=1
SAB_BEFORE2='        if (atomic)
            vm_cut(v, mslot, "cut: the assertion is committed; every choice "'
SAB_AFTER2='        if (1)   /* SABOTAGE S1963 */
            vm_cut(v, mslot, "cut: the assertion is committed; every choice "'
