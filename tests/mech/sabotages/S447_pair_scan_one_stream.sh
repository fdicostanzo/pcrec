#!/usr/bin/env bash
# S447 ([OPT-LITSCAN] S4 C3, lane c3build) -- THE PAIR ARM SCANS ONE MEMBER.
#
# A run pre-check block whose scan position is a two-member cube searches two
# memchr streams, A = T[k*] and B = T[k*] | ~K[k*]. This plant makes B equal
# A, so the block scans the upper member twice and every match carrying the
# lower member at the scan position is deleted -- on BOTH blocks
# (<p>_reqrun and the K66 site's <p>_reqrun_whole). Detector: the harness on
# tests/litscan/reqcube.rxt's lowercase cells, and reqcube_check.py's
# two-member scan check. (Design's provisional S446.)
# RE-AIMED 2026-10-06 ([MEMFN] R4c REPLACE, lane r4ccore): the pair arm's second member is derived in the kit (ofs_fn_scan); the search text moved into the kit; the plant is the same defect in the kit's transcription of the form.
SAB_ID="S447-pair-scan-one-stream"
SAB_FILE='memfn/src/ofsskip.c'
SAB_SUITES="harness codegen"
SAB_HARNESS_TARGET="tests/litscan/reqcube.rxt"
SAB_DESC="the caseless necessary run's pair arm searches its upper member in both streams, so a match whose scan position holds the lower member is never found and the pre-check answers NOMATCH"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/c3build_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S447."
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "(?i)select" && grep -q "^#define RX_REQ_RUN \"53454c454354@4/dfdfdfdfdfdf\"" "$REACH_TMP/o.c" && grep -q "ha < pos + 4" "$REACH_TMP/o.c" && echo REACH-PAIR-ARM'
SAB_REACH_EXPECT="REACH-PAIR-ARM"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    *b = m != 0xFF ? (*a | (~m & 0xFF)) : -1;'
SAB_AFTER='    *b = m != 0xFF ? *a : -1;   /* SABOTAGE S447: the second stream scans the first member */'
