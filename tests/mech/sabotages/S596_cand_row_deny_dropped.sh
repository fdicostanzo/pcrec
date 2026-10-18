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
# suite. [MEMFN] R17-b' B3b (lane b3b, 2026-10-18) RE-AIMED: the set-leads
# row's deny left cand_rows[] with bit 45 (retired): it is the memfn kit's
# PRES row P4's `pres-set-lead` (memfn/src/finder.c), which the
# `-fno-req-set-lead` alias reaches. The plant drops THAT row's deny name, so
# under the alias (or `--memfn=no-pres-set-lead`) P4 still leads and the
# admission still reads `set-leads` where its emitted row should apply
# (intent unchanged: a dropped deny). Detector unchanged: the cand oracle's
# witness `emitted -fno-req-set-lead`.
SAB_ID='S596-cand-row-deny-dropped'
SAB_FILE='memfn/src/finder.c'
SAB_SUITES='candoracle'
SAB_DESC='a dropped deny: the kit PRES row P4 (set-leads, bit 45 retired into it at B3b) loses its pres-set-lead deny, so under -fno-req-set-lead (the alias) the admission still chooses set-leads where its emitted row should apply'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/stc2_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S596.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='      FF_UNSTATED, FF_UNSTATED, { 1, 0, 0, 0 }, 1, "pres-set-lead", FB_UNMEASURED_DEFAULT, "B3b",'
SAB_AFTER='      FF_UNSTATED, FF_UNSTATED, { 1, 0, 0, 0 }, 1, NULL /* SABOTAGE S596 */, FB_UNMEASURED_DEFAULT, "B3b",'
