# S286 — [OPT-LITSCAN] S1 G1'S `verifies` CONJUNCT DROPPED
# (src/gen/emit_dfa.c, `req_byte_dominated_by`): the RUN-check-needs-a-
# run-verifying-scan conjunct — "a run pre-check is dominated only where the
# scan's test refuses every window lacking the run" — is deleted, so a run
# pre-check is admitted "dominated" the moment its byte matches the
# candidate-start scan's byte, with no regard to whether that scan actually
# verifies the run. litscan_s1.md §7.1 row (c).
#
# STRUCTURAL, NOT ANSWER-LEVEL: a wrongly-elided run pre-check is dominated
# by a SOUND (if weaker) candidate-start scan on every witness this row's
# own corpus reaches, so no `.rxt` cell sees it — the pre-check being
# skipped never changes an answer, only whether the artifact carries a
# second linear no-match proof. The detector is `run_prechecks.sh` §5.10's
# own two witnesses, whose `REQ_WHY` must stay "emitted" and reads
# "dominated" instead under the plant.
SAB_ID="S286-g1-verifies-conjunct-dropped"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="prechecks"
SAB_DESC="req_byte_dominated_by drops the run_verified conjunct, so a run pre-check is admitted dominated whenever the candidate-start scan's byte matches the pick even though that scan never verifies the run itself -- q[a-z]*qu (class D, memchr on q with the run floating) and \\Bfoo\\B (class C2, the model scans o at 1 not the pick f) both flip from REQ_WHY \"emitted\" to \"dominated\""
SAB_DOC_FIGURE="Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S286."
# [MECH-REACH] the site is exercised: a class-D witness whose run-pre-check
# stays emitted (never dominated) on the clean tree.
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "q[a-z]*qu" && grep -q "^#define RX_REQ_WHY \"emitted\"" "$REACH_TMP/o.c" && echo REACH-RUN-PRECHECK-NOT-DOMINATED'
SAB_REACH_EXPECT="REACH-RUN-PRECHECK-NOT-DOMINATED"
SAB_COUNT=1
SAB_BEFORE='    if (cx->job->req_run.len >= 2 && !cs->run_verified) return false;
    if (p == q) return true;'
SAB_AFTER='    /* SABOTAGE S286: run_verified conjunct dropped */
    if (p == q) return true;'
