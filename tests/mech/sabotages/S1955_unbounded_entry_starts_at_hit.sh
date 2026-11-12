#!/usr/bin/env bash
# S1955 ([REQ-PAST-LAST], lane reqpast) -- THE UNBOUNDED ROW STARTS AT THE HIT.
# With K unbounded the move `c - K` is never ahead, so the attempts must begin
# at the startpos; the plant keeps the whole run's first hit as the first
# attempt position, so a match beginning before the run (`a+xyz` over
# "aaaaxyz" from 0) is reported late or lost. Detector:
# tests/litscan/handoff_vm.rxt.
SAB_ID='S1955-unbounded-entry-starts-at-hit'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='harness'
SAB_HARNESS_TARGET='tests/litscan/handoff_vm.rxt'
SAB_DESC='the attempt-loop handoff with an unbounded K starts its attempts at the whole run'\''s first hit instead of the startpos'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/reqpast_report.md, CHANGES); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1955.'
SAB_REACH='"$PCREC" --features all -p rx --engine=vm -o "$REACH_TMP/o.c" --pattern '\''a+xyz'\'' && grep -q '\''^#define RX_REQ_HANDOFF "unbounded"'\'' "$REACH_TMP/o.c" && grep -q '\''handoff_position = search_from;'\'' "$REACH_TMP/o.c" && echo REACH-UNBOUNDED-ENTRY'
SAB_REACH_EXPECT='REACH-UNBOUNDED-ENTRY'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        pcrec_sb_printf(c, "%shandoff_position = %s;\n", indent, posvar);'
SAB_AFTER='        (void)posvar;   /* SABOTAGE S1955: the attempts begin at the hit */'
