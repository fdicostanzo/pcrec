#!/usr/bin/env bash
# S3485 (lane l3r66, 2026-11-21; review r66 CHECK-1) -- DD12a(i)'s one-sided-run arm drops the run-bearing
# side's RUN SCAN from its coverage test, so a run-less side's presence byte the run side covers only by
# scanning its run (`(?<=a)(b)\1x`: utf8 asks {98,120}, byte gates {120} and its run scans {98}) reads as
# uncovered. The plant is the arm's RED-BRANCH witness: on today's tree both reaching pairs are covered,
# and this plant turns them red.
# Detector: the arm's own `cov_bad` finding in tests/codegen/run_encoding_checks.sh DD12a(i).
SAB_ID="S3485-dd12a-one-sided-scan-dropped"
SAB_FILE="tests/codegen/run_encoding_checks.sh"
SAB_SUITES="encoding"
SAB_DESC='DD12a(i)'\''s one-sided-run arm ignores the bytes the run-bearing side scans, so a covered pair reads as an uncovered presence demand'
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/l3r66_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3485."
SAB_REACH='"$PCREC" --features all --emit-facts --pattern '\''(?<=a)(b)\1x'\'' | grep -qP '\''^byte\treq_whole_run\t([^\t]*\t){4}6162\t'\'' && "$PCREC" --features all -e utf8 --emit-facts --pattern '\''(?<=a)(b)\1x'\'' | grep -qP '\''^utf8\treq_whole_run\t([^\t]*\t){4}none\t'\'' && echo REACH-ONE-SIDED'
SAB_REACH_EXPECT="REACH-ONE-SIDED"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                if not (have <= want and want - have <= got):'
SAB_AFTER='                if not (have <= want and want - have <= set()):  # SABOTAGE S3485'
