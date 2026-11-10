#!/usr/bin/env bash
# S3010 -- R-38 K38-2a, review 2026-11-10 r2 k382a ORC-1 (lane k382afix; docs/design/memfn/
# span_runs_sheet.md rev 1.3 §3.3 items 1-2, "the floor is the attempt start"). THE USE MOVES ITS
# PART'S FLOOR: every rendered call of a run part (ofsskip.c ofs_fn_call, the call a pre-check's
# entry and re-entry uses make) passes `lo + 1`, so the occurrence AT the attempt start is never
# asked for. Each part call is honest in its own frame, so a record taken from the part's own
# arguments checks the kit's floor against itself (green before the fix, on the same plant).
# Detector: the ORACLE STEP of G2's presence family (memfn/tests/run_g2_pres.sh): its records are
# taken at the CALLER boundary (the host's subject and attempt start), and the oracle
# (tests/memfn/occurrence_oracle.py) reds "least" on every skipped occurrence at the origin.
SAB_ID="S3010-use-passes-part-attempt-start-plus-one"
SAB_FILE="memfn/src/ofsskip.c"
SAB_SUITES="g2pres"
SAB_DESC="every use passes its run part the attempt start + 1: the oracle, reading records taken at the caller boundary, must red"
SAB_DOC_FIGURE="HAND-MEASURED by lane k382afix 2026-11-10 (docs/dev/lanes/k382afix_report.md): memfn/tests/run_g2_pres.sh --plant S3010 RED on the oracle step (rows=50073 violations=1980); the same plant against the pre-fix driver (records from the part's own arguments) GREEN (rows=50112 violations=0). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3010."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    kit_out(o, "%s(%s, %s, %s", fn, h->s, h->n, h->lo);'
SAB_AFTER='    kit_out(o, "%s(%s, %s, %s + 1", fn, h->s, h->n, h->lo);   /* SABOTAGE S3010 */'
SAB_REACH='TMPDIR="$REACH_TMP" bash "$TREE/memfn/tests/run_g2_pres.sh" --reach'
SAB_REACH_EXPECT="REACH-G2P-USE-CALL"
