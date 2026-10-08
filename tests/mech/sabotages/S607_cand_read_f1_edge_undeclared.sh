#!/usr/bin/env bash
# S607 ([START-TABLE] C6, lane stc67; docs/design/start_table.md §1.3, docs/dev/lanes/stc67_report.md) -- a SELECTION READ left undeclared: FIRST's read of PRESENCE (F1, the `handoff` row's call of the admission) is dropped from the slot graph (`cand_nodes[CAND_SLOT_FIRST].reads`), so F1 reads PRESENCE over an edge the graph does not list.
# Detector (arm candoracle): tests/codegen/run_cand_oracle.sh. Since C6 F1
# reads the admission through `cand_read` (`req_admit_read`), and the trace
# build checks every read against the graph's `reads` column, aborting
# (`CANDORACLE undeclared-read FIRST PRESENCE`) on an edge it does not
# declare on the read's route. Every witness that asks FIRST evaluates F1
# first (`handoff` is FIRST's first row and undenied by default), so the
# whole witness file aborts. The default build does not check the edge, so
# no artifact byte and no answer moves: the corpus arm is not named, by design.
SAB_ID='S607-cand-read-f1-edge-undeclared'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='candoracle'
SAB_DESC='FIRST reads PRESENCE (F1, the handoff row asking the admission) over an edge the slot graph no longer declares; the trace build read check must abort'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/stc67_report.md §2); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S607.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "\\d\\dxyz" && grep -qF "#define RX_REQ_HANDOFF \"2\"" "$REACH_TMP/o.c" && echo REACH-HANDOFF'
SAB_REACH_EXPECT='REACH-HANDOFF'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                             CN(CAND_SLOT_NEXT),
                             .reads = { [CAND_SLOT_PRESENCE] = CAND_ON(CAND_ROUTE_DFA) } },'
SAB_AFTER='                             CN(CAND_SLOT_NEXT) },   /* SABOTAGE S607 */'
