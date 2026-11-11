#!/usr/bin/env bash
# S3008 -- R-38 K38-2a (docs/design/memfn/span_runs_sheet.md rev 1.3 §5's K38-2a row, plant B;
# §3.3 item 2 "least"; lane k382a). A CANDIDATE ABOVE THE LEAST OCCURRENCE: the run part's
# memchr form (ofsskip.c memchr_body) passes over an occurrence at its origin (a verified
# candidate equal to the call's `lo` is skipped), so the next occurrence above the least (or a
# miss) is yielded. Its reads are unchanged until a candidate verifies.
# Detector: the ORACLE STEP of G2's presence family (memfn/tests/run_g2_pres.sh pipes its
# records to tests/memfn/occurrence_oracle.py, written D27-blinded by lane k382o from §3.3).
# The family's own classifier puts its occurrences ABOVE lo on purpose (the occurrence
# contract is the oracle's, not a second copy of it). An absent oracle file is a FAIL of the
# family (review 2026-11-10 r2 k382a ORC-2), never a green OWED.
# The plant's reach, measured by hand (k382a_report.md "Plants"): over one generic pass's
# records, 415 hold an occurrence at their origin; the clean kit yields the origin on all of
# them, the planted kit on 93 (322 moved).
SAB_ID="S3008-run-part-candidate-above-least"
SAB_FILE="memfn/src/ofsskip.c"
SAB_SUITES="g2pres"
SAB_DESC="the run part's memchr form skips a verified candidate at its origin: a candidate above the least occurrence, the occurrence oracle's plant"
SAB_DOC_FIGURE="HAND-MEASURED by the kit manager 2026-11-10 with the oracle merged (k382o): memfn/tests/run_g2_pres.sh --plant S3008 reads RED on the oracle step (rows=50121 violations=1860); clean: rows=50178 violations=0. Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3008."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    int maxk = x->maxk, k = x->k, a = x->a;
    kit_out(o, "    while (pos + %d < n) {\n", maxk);'
SAB_AFTER='    int maxk = x->maxk, k = x->k, a = x->a;
    o->puts(o->u, "    size_t lo0 = pos;\n");   /* SABOTAGE S3008 */
    kit_out(o, "    while (pos + %d < n) {\n", maxk);'
SAB_FILE2="memfn/src/ofsskip.c"
SAB_COUNT2=1
SAB_BEFORE2='    o->puts(o->u,   ") return cand;\n");'
SAB_AFTER2='    o->puts(o->u,   ") { if (cand == lo0) { pos = cand + 1; continue; } return cand; }\n");   /* SABOTAGE S3008 */'
SAB_REACH='TMPDIR="$REACH_TMP" bash "$TREE/memfn/tests/run_g2_pres.sh" --reach'
SAB_REACH_EXPECT="REACH-G2P-MEMCHR-FORM"
