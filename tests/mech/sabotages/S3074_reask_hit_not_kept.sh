#!/usr/bin/env bash
# S3074 ([REQ-PAST-LAST], lane rpfix, review r2-reqpast CHK-1) -- THE ATTEMPT
# LOOP'S RE-ASK DROPS ITS HIT. The re-ask after a failed attempt must write
# `landmark_position`, the hit the next attempts compare against; the plant
# writes it to a throwaway, so the kept hit stays behind the attempt and every
# attempt re-asks (quadratic on a long subject, THE SAME ANSWERS). No answer
# cell sees it. Detector: run_prechecks.sh [5.12l] (the re-ask keeps its hit).
SAB_ID='S3074-reask-hit-not-kept'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='prechecks'
SAB_DESC='the VM attempt loop'\''s re-ask of the pre-check writes its hit to a throwaway instead of landmark_position'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/rpfix_report.md, CHANGES); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3074.'
SAB_REACH='"$PCREC" --features all -p rx --engine=vm -o "$REACH_TMP/o.c" --pattern '\''a+xyz'\'' && grep -q '\''^ *if (landmark_position < attempt_position) {$'\'' "$REACH_TMP/o.c" && echo REACH-REASK'
SAB_REACH_EXPECT='REACH-REASK'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        .on_miss = REQ_ON_MISS, .result = "landmark_position",
        .miss = MF_MISS_N, .comment_tier = PCREC_CMT_NONESSENTIAL, .u = &u,
    };
    pcrec_memfn_use(cx, pre->handle, &h, c);
    pcrec_memfn_check_use(cx, pre->site, true);'
SAB_AFTER='        .on_miss = REQ_ON_MISS, .result = posvar[0] == '\''a'\'' ? "rx_dropped" : "landmark_position",   /* SABOTAGE S3074 */
        .miss = MF_MISS_N, .comment_tier = PCREC_CMT_NONESSENTIAL, .u = &u,
    };
    pcrec_memfn_use(cx, pre->handle, &h, c);
    pcrec_memfn_check_use(cx, pre->site, true);'
