#!/usr/bin/env bash
# S3048 -- R-38 K38-2 fix round (review 2026-11-11 r1 k382 F15; lane k382fix), S449's successor.
# THE K66 WHOLE RUN's MASK DROPPED AT THE STATEMENT: src/gen/emit_dfa.c req_pres_spans states each
# run position as the cube (whole[j], 0xFF) instead of (whole[j], whole_mask[j]), so a caseless
# run is stated exact: the run part compares T alone (an unmasked compare, a false NOMATCH on a
# subject holding the other member) and the pair position scans one stream.
# Detector: tests/codegen/reqcube_check.py (test-codegen): the k66 witness
# `(x?)(?i:abcdefghijkl)\1` (its words spell K=ff.., not the fact's K; the pair position scans one
# member; the VM route's run part does not verify the whole run), and the (?i)select rows.
# tests/base/k66_precheck_whole_run.rxt does NOT red under it (16/16 measured): its subjects carry
# the run's T bytes.
SAB_ID="S3048-k66-run-mask-dropped"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="codegen"
SAB_DESC="the run presence span states every position exact (mask 0xFF): reqcube_check's k66 and (?i)select rows must red"
SAB_DOC_FIGURE="HAND-MEASURED by lane k382fix 2026-11-11: reqcube_check.py against a planted build RED on the k66 witness (words K=ff.. vs the fact's dfdf..; pair position 9 scanned on [74]; S448's whole-run row) and on '(?i)select'; k66_precheck_whole_run.rxt 16/16 (not a detector). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3048."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            pcrec_memfn_wpos_cube(sp, j, run->whole[j], run->whole_mask[j]);'
SAB_AFTER='            pcrec_memfn_wpos_cube(sp, j, run->whole[j], 0xFF);   /* SABOTAGE S3048 */'
SAB_REACH='"$PCREC" --features all -p rx --engine=vm -o "$REACH_TMP/k.c" --pattern "(x?)(?i:abcdefghijkl)\\1" && grep -q "RX_REQ_RUN \"4142434445464748494a4b4c@[0-9]*/dfdf" "$REACH_TMP/k.c" && echo REACH-K66-MASKED-RUN'
SAB_REACH_EXPECT="REACH-K66-MASKED-RUN"
