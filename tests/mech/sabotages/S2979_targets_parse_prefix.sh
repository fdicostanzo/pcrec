#!/usr/bin/env bash
# S2979 -- [XARCH-DEV] unit K0 (request R-36; lane k0). THE TOKEN PARSER ACCEPTS A PREFIX.
#
# Plant: memfn/src/targets.c's tok_names stops requiring the row's name to end with the token, so a
# token that is a prefix of a row's name parses as that row.
# Detector: tests/memfn/targets_check.c (part 2 of tests/memfn/run_targets.sh, arm memfntargets): the
# refusal of a token that is a prefix of a target's name.
SAB_ID="S2979-targets-parse-prefix"
SAB_FILE="memfn/src/targets.c"
SAB_SUITES="memfntargets"
SAB_DESC='the token parser accepts a prefix of a row name as that row'
SAB_DOC_FIGURE='MEASURED by lane k0, planted and reverted by hand in a scratch copy (k0_report.md, Sabotage); exact re-run: bash tests/mech/run_sabotage_matrix.sh S2979.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return i == len && !name[i];'
SAB_AFTER='    return i == len;'
