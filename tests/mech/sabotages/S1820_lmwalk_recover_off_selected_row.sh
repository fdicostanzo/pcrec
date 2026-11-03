#!/usr/bin/env bash
# S1820 ([LANDWALK] stage 1, lane p1build; review 2026-10-29 r7 FIX-1;
# docs/dev/lanes/p1build_report.md "Design rev 3") -- RECOVER READ OFF THE
# SELECTED ROW instead of its asker.
#
# WHAT IT BREAKS. The walk relocates to the composite, so RECOVER's asker is
# the route's fallback row (`cand_recover_asker`). The plant returns the
# selected LOCATE row always, so on a walk artifact RECOVER is asked of a row
# whose cells name no RECOVER.
#
# WHERE IT IS SEEN. The path self-check refuses an admitted selection with a
# NULL slot (`cand_path_of`), so every walk witness fails to compile: the
# answer net (tests/landwalk/landwalk.rxt) and tests/codegen/run_landmark_walk.sh.
SAB_ID='S1820-lmwalk-recover-off-selected-row'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='harness landwalk'
SAB_DESC='RECOVER is read off the selected LOCATE row, not the row whose walk runs it'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1820.'
SAB_HARNESS_TARGET='tests/landwalk/landwalk.rxt'
SAB_REACH='"$PCREC" --features all -p rx -o - --pattern "[a-z]+@x" | grep -F "#define RX_DFA_SCAN \"landmark-walk\""'
SAB_REACH_EXPECT='#define RX_DFA_SCAN "landmark-walk"'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if ((r->needs[rt].cells & CN(CAND_SLOT_RECOVER)) || cand_finish_of(cx) == CAND_ROUTE_VM)
        return r;'
SAB_AFTER='    if (1)   /* SABOTAGE S1820 */
        return r;'
