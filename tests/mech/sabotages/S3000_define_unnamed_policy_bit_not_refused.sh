#!/usr/bin/env bash
# S3000 -- [XARCH-DEV] unit U2 fix (request R-37; lane u2fix), mf_define REFUSES a policy bit outside
# the kit's named set (MF_P_KIT_NAMED) when MF_TARGET_REQUIRED is set.
#
# Plant: memfn/src/compose.c's refusal is dropped (`if (0)`), so an unnamed bit is taken again.
# DECLARED UNDETECTED at the branch default (MF_TARGET_REQUIRED 0: the refusal is not reached, and no
# committed check plants an unnamed bit). At 1 the pcrec-side arts that U3 has not moved are refused
# anyway (test-memfn-finder/arms are red before and after), so they cannot tell the plant apart. What
# would close it: a kit check that defines a site with a hand-planted bit under the switch at 1 and
# reads the hex in the message, runnable once the joint merge sets the switch.
SAB_ID="S3000-define-unnamed-policy-bit-not-refused"
SAB_FILE="memfn/src/compose.c"
SAB_SUITES="memfnfinder"
SAB_DESC='mf_define takes a site policy bit outside the kit named set at MF_TARGET_REQUIRED 1'
SAB_DOC_FIGURE='Hand-run at MF_TARGET_REQUIRED 1 in a scratch copy (u2fix_report.md, Sabotage row); exact re-run: bash tests/mech/run_sabotage_matrix.sh S3000.'
SAB_EXPECT=UNDETECTED
SAB_COUNT=1
SAB_BEFORE='    if (MF_TARGET_REQUIRED && (s->policy & ~(uint32_t)MF_P_KIT_NAMED))'
SAB_AFTER='    if (0 && (s->policy & ~(uint32_t)MF_P_KIT_NAMED))   /* SABOTAGE S3000 */'
