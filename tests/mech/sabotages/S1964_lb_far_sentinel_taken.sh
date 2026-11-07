# S1964 ([VLOOKBEHIND] stage 1, design §7, READY-1) -- THE FAR STEP'S
# SENTINEL RETRY. Under UTF-8 the far count min(hi - lo, LO) is an upper bound
# and the far step can return the sentinel; the loop retries ONE shorter.
# RE-AIMED 2026-11-06 (lane vlbfix, review r4 F7): the first plant (the
# sentinel test always passes, so the sentinel is tried as a candidate)
# moves NO answer -- the candidate falls out through the end-check -- and is
# seen only as an out-of-bounds read under -fsanitize=address (no row arm runs
# the harness under a sanitizer; the report lists that as the residual). This
# plant breaks the same retry so that an answer moves: it retries TWO shorter,
# skipping the length that reaches the start. Same cells as S1965/S1966 (the
# corpus cannot tell the three apart; review r4 F12 NOTED).
SAB_ID="S1964-lb-far-sentinel-taken"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/lookaround/lookbehind_variable_witness.rxt"
SAB_DESC='a far step that returns the sentinel retries two shorter instead of one, so the farthest real candidate is skipped'
SAB_DOC_FIGURE='MEASURED (lane vlbfix, tools/review/plant.sh + harness on the target): 51 pass / 3 fail, W6 lines 60, 208, 216: group 1 (0,2) -> (2,2), (1,2) -> (2,2), (1,3) -> (3,3); clean 54/0.'
SAB_COUNT=1
SAB_BEFORE='    pcrec_vm_b_lset(v->sb, kx, VLO_ASSIGN, vm_rolef(v, "%s - 1", kn), 0, false);'
SAB_AFTER='    pcrec_vm_b_lset(v->sb, kx, VLO_ASSIGN, vm_rolef(v, "%s - 2", kn), 0, false);   /* SABOTAGE S1964 */'
