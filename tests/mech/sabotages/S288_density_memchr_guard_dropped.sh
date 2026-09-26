# S288 — [OPT-LITSCAN] S1 THE DENSITY CLAUSE'S MEMCHR-FORM GUARD DROPPED
# (src/gen/emit_dfa.c, `req_byte_dominated_by`): the DENSITY conjunct's
# `!cs->memchr_form` guard is deleted, so the byte-frequency comparison runs
# for an OFFSET-SET (table) candidate scan too, not only a `memchr` one --
# admitting a one-byte pre-check as "dominated" by a set-membership test that
# is not the single-byte judgement the density rule is about. litscan_s1.md
# §7.1 row (e).
#
# STRUCTURAL, NOT ANSWER-LEVEL, for the same reason as row (c): an
# over-elided pre-check is dominated by a SOUND scan on the corpus this row
# reaches, so no `.rxt` cell moves. The detector is `run_prechecks.sh`
# §5.10's own witness -- a one-byte check on 0x81 beside an offset-set
# scanning 0x80 of equal ppm -- whose `REQ_WHY` must stay "emitted" and
# reads "dominated" under the plant.
SAB_ID="S288-density-memchr-guard-dropped"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="prechecks"
SAB_DESC="req_byte_dominated_by drops the density conjunct's !cs->memchr_form guard, so the byte-frequency (ppm) comparison runs for an offset-set (table) candidate scan too -- [ab]\\x80[0-9]{3}\\x81 flips its one-byte pre-check on 0x81 from REQ_WHY \"emitted\" to \"dominated\" by an offset-set scan of 0x80 that is not a memchr form at all"
SAB_DOC_FIGURE="Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S288."
# [MECH-REACH] the witness's one-byte pre-check stays emitted (never
# dominated by the offset-set scan) on the clean tree.
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "[ab]\x80[0-9]{3}\x81" && grep -q "^#define RX_REQ_WHY \"emitted\"" "$REACH_TMP/o.c" && echo REACH-DENSITY-PRECHECK-NOT-DOMINATED'
SAB_REACH_EXPECT="REACH-DENSITY-PRECHECK-NOT-DOMINATED"
SAB_COUNT=1
SAB_BEFORE='    if (cx->job->req_run.len >= 2) return false;
    if (!cs->memchr_form) return false;
    if (cx->opt->encoding != PCREC_ENC_BYTE) return false;'
SAB_AFTER='    if (cx->job->req_run.len >= 2) return false;
    /* SABOTAGE S288: memchr-form guard dropped */
    if (cx->opt->encoding != PCREC_ENC_BYTE) return false;'
