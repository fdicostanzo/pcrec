#!/usr/bin/env bash
# S775 ([OPT-REVEND] L2, lane revbuild; docs/design/locate_finish.md §4.3 (LR-G6); docs/dev/lanes/revbuild_report.md) -- PRESENCE no longer defers to a walk that answers presence itself: a pre-check is admitted ahead of the walk.
# Detector: the walk's own assertion refuses the compile (`internal error: a whole-window pre-check was admitted ahead of the rev-end walk`) on every walking pattern with a necessary byte.
SAB_ID='S775-deference-dropped'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='harness'
SAB_DESC='PRESENCE no longer defers to a walk that answers presence itself: a pre-check is admitted ahead of the walk'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S775.'
SAB_HARNESS_TARGET='tests/assertions/rev_end.rxt'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "abc$" && grep -qF "#define RX_REQ_WHY \"dominated\"" "$REACH_TMP/o.c" && echo REACH-DOMINATED'
SAB_REACH_EXPECT='REACH-DOMINATED'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (CAND_READ(CAND_SLOT_PRESENCE, CAND_SLOT_LOCATE, &ls, "req-whole")->u.locate.whole)
            return true;'
SAB_AFTER='        (void)ls;   /* SABOTAGE S775: the LOCATE.whole deference dropped */'
