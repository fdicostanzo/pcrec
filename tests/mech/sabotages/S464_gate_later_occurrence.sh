#!/usr/bin/env bash
# S464 ([K82] (B), lane k82hbuild) -- THE GATE RETURNS A LATER OCCURRENCE.
#
# The handoff makes the run search's RETURN VALUE load-bearing (litscan_k82h.md
# §1.1a): it must be the LEFTMOST occurrence >= search_from. This plant keeps a
# correct discard answer (an occurrence exists iff one is returned) and hands
# off the NEXT one when there is a next one. Witness: (?i)cat on "CAT CAT":
# (0,3) becomes (4,7). Detector: handoff.rxt's two-occurrence and find-all rows.
SAB_ID="S464-gate-later-occurrence"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/litscan/handoff.rxt"
SAB_DESC='the handoff gate returns a LATER occurrence of the run'\''s window than the first at or after search_from (the leftmost-occurrence contract, r1 S-F1): a correct discard gate, and under the handoff the scan starts past the match'\''s own window'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/k82hbuild_report.md §6); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S464.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern '\''(?i)cat'\'' && grep -q '\''size_t handoff_position = rx_reqrun(subject, subject_length, search_from);'\'' "$REACH_TMP/o.c" && echo REACH-HANDOFF-GATE'
SAB_REACH_EXPECT='REACH-HANDOFF-GATE'
SAB_REACH_POP='tests/litscan/handoff.rxt|^ms 0 "CAT CAT" 0 3$|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    pcrec_sb_printf(c, "%ssize_t handoff_position = %s(%s, %s, %s);\n"
                       "%sif (handoff_position >= %s) return 0;\n",
                    indent, req_run_fn_name(cx, 0), subjvar, lenvar, posvar,
                    indent, lenvar);'
SAB_AFTER='    pcrec_sb_printf(c, "%ssize_t handoff_position = %s(%s, %s, %s);\n"
                       "%sif (handoff_position >= %s) return 0;\n",
                    indent, req_run_fn_name(cx, 0), subjvar, lenvar, posvar,
                    indent, lenvar);
    pcrec_sb_printf(c, "%s{ size_t s464 = %s(%s, %s, handoff_position + 1); if (s464 < %s) handoff_position = s464; } /* SABOTAGE S464 */\n",
                    indent, req_run_fn_name(cx, 0), subjvar, lenvar, lenvar);'
