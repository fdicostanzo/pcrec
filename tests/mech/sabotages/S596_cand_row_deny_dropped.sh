#!/usr/bin/env bash
# S596 ([START-TABLE] C2, lane stc2; docs/design/start_table.md §3.3 item 6, docs/dev/lanes/stc2_report.md) -- a dropped deny bit: P4 set-leads loses PCREC_NO_REQ_SET_LEAD in cand_rows[], so under -fno-req-set-lead the table still chooses set-leads where its emitted row should apply.
# Detector (arm candoracle): tests/codegen/run_cand_oracle.sh, the both-walks
# oracle over named witnesses. cand_rows[] has no reader in a default build
# until C3, so no artifact byte and no answer moves: the corpus arm is not
# named, by design. [START-TABLE] C4 (lane stc4, 2026-10-07): the table now
# DECIDES PRESENCE (`req_admits[]` is deleted into it), so the plant moves the
# artifact under -fno-req-set-lead, and the witness `emitted -fno-req-set-lead`
# no longer reaches `emitted` (the hit counter, C3's S594/S595 shape). The
# same edit is S462's re-aimed plant; that row's detector is the pre-check
# suite.
SAB_ID='S596-cand-row-deny-dropped'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='candoracle'
SAB_DESC='a dropped deny bit: P4 set-leads loses PCREC_NO_REQ_SET_LEAD in cand_rows[], so under -fno-req-set-lead the table still chooses set-leads where its emitted row should apply (since C4 the table decides, so the artifact moves)'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/stc2_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S596.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    { .c = { "set-leads", PCREC_NO_REQ_SET_LEAD, req_set_leads_applies },'
SAB_AFTER='    { .c = { "set-leads", 0, req_set_leads_applies },   /* SABOTAGE S596 */'
