# S1965 ([VLOOKBEHIND] stage 1, design §7 W6 (a)) -- THE UTF-8 FAR RETRY.
# Two bytes but one character precede the cursor in W6's cell, so K = 2 returns
# the sentinel; only the retry at K = 1 reaches the start.
SAB_ID="S1965-lb-far-sentinel-ends-branch"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/lookaround/lookbehind_variable_witness.rxt"
SAB_DESC='a far step that returns the sentinel ends the branch instead of retrying one shorter'
SAB_DOC_FIGURE='PREDICTED (vlookbehind.md §7, lane vlbbuild): W6 (a) red under utf8: nomatch for (2,3) g1 (0,2).'
SAB_COUNT=1
SAB_BEFORE='    pcrec_vm_b_lset(v->sb, kx, VLO_ASSIGN, vm_rolef(v, "%s - 1", kn), 0, false);'
SAB_AFTER='    pcrec_vm_b_branch(v->sb, vm_condf(v, "1"), pcrec_vm_tgt_fail());   /* SABOTAGE S1965 */
    pcrec_vm_b_lset(v->sb, kx, VLO_ASSIGN, vm_rolef(v, "%s - 1", kn), 0, false);'
