#!/usr/bin/env bash
# S3000 -- [XARCH-DEV] unit U2 fix (request R-37; lane u2fix), mf_define REFUSES a policy bit outside
# the kit's named set (MF_P_KIT_NAMED); unconditional since review 2026-11-08 r5 X-5 (lane u2rev
# deleted the staging switch the row first named, and re-aimed its anchor at the refusal itself).
#
# Plant: memfn/src/compose.c's refusal is dropped (`if (0)`), so an unnamed bit is taken again.
# Detector (arm memfnfinder): tests/memfn/policy_check.c, built by run_finder.sh against the library,
# defines a site carrying 1u<<7 and wants the refusal with 0x80 in mf_art_error; the plant takes the
# bit, red.
SAB_ID="S3000-define-unnamed-policy-bit-not-refused"
SAB_FILE="memfn/src/compose.c"
SAB_SUITES="memfnfinder"
SAB_DESC='mf_define takes a site policy bit outside the kit named set'
SAB_DOC_FIGURE='MEASURED by lane u2c4 by hand (u2c4_report.md, The S3000 detector); re-aimed and re-measured by lane u2rev (u2rev_report.md, Sabotage rows); exact re-run: bash tests/mech/run_sabotage_matrix.sh S3000.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (s->policy & ~(uint32_t)MF_P_KIT_NAMED)'
SAB_AFTER='    if (0 && (s->policy & ~(uint32_t)MF_P_KIT_NAMED))   /* SABOTAGE S3000 */'
