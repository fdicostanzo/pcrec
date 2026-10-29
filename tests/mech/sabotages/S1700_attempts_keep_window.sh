#!/usr/bin/env bash
# S1700 ([REQRUN-VM], lane reqvm1) -- THE ATTEMPT LOOP KEEPS THE WINDOW'S HIT
# WITH THE WHOLE RUN'S K. `handoff-attempts` subtracts the whole run's K
# (`whole_maxoff`) from the kept part's position; the plant keeps the WINDOW's
# part (0) instead, a hit up to (window offset - whole offset) bytes later, so
# the first attempt starts past the match. Detector: tests/litscan/
# handoff_vm.rxt (bench subst case 7's pattern, whole `https://www.` at 0,
# window `s://www.` at 4, K 0).
SAB_ID='S1700-attempts-keep-window'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='harness'
SAB_HARNESS_TARGET='tests/litscan/handoff_vm.rxt'
SAB_DESC='the VM attempt loop'\''s handoff keeps the run window'\''s hit but subtracts the whole run'\''s K, so its first attempt starts past matches'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/reqvm1_report.md, Tests and sabotage); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1700.'
SAB_REACH='"$PCREC" --features all -p rx --engine=vm -o "$REACH_TMP/o.c" --pattern '\''(https://www\.(?:acme|hooli)\.(com|de)/[^"?\s]*)'\'' && grep -q '\''^#define RX_REQ_HANDOFF "0"'\'' "$REACH_TMP/o.c" && grep -q '\''^#define RX_REQ_RUN "733a2f2f7777772e@'\'' "$REACH_TMP/o.c" && grep -q '\''attempt_position = handoff_position;'\'' "$REACH_TMP/o.c" && echo REACH-WHOLE-NOT-WINDOW'
SAB_REACH_EXPECT='REACH-WHOLE-NOT-WINDOW'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    int keep = handoff && req_use_whole(cx) ? nrun - 1 : 0;'
SAB_AFTER='    int keep = 0;   /* SABOTAGE S1700: the window kept */'
