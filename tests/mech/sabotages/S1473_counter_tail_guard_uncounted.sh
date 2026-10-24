# S1473 (K128, lane corefix) -- THE COUNTER RUNG'S PRE-PASS FORGETS ITS
# TAIL'S GUARD.
#
# The slot layout's bases are computed from the pre-pass TOTALS, so a guard
# the emitter assigns and the pre-pass did not count lands on the next
# family's slot. Before K128 the counter rung's unbounded nullable tail had
# exactly this hole: its star's guard shared the iteration COUNTER's slot,
# harmless only because the star wrote it after the counter was done. K128
# writes the guard DURING the mandatory phase, so the alias now clobbers the
# live counter: the trip loop runs away and the search gives up.
SAB_ID="S1473-counter-tail-guard-uncounted"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/captures/empty_iteration.rxt"
SAB_DESC="vm_count_slots' counter-rung arm stops counting the unbounded nullable tail's guard, so that guard aliases the iteration counter's slot; with K128's mid-phase guard write the counter is clobbered and X{m,} with m >= K gives up or answers wrong"
SAB_DOC_FIGURE="PREDICTED: tests/captures/empty_iteration.rxt RED on the counter rows ({8,}?, {16,}?, {9,}): the pre-fix measurement of the alias (lane corefix, by hand, before this line existed) was PCREC_ERR_FRAMES (-3) at every start position of (?:()|a){16,}?b and {64,}?b. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1473."
SAB_COUNT=1
SAB_BEFORE='        if (a->u.rep.rmax < 0 && pcrec_nullable(a->l)) v->nguard++;
        return;'
SAB_AFTER='        return;   /* SABOTAGE S1473: the tail guard is not counted */'
