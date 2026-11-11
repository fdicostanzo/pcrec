#!/usr/bin/env bash
# S3032 ([UCP] U3 hazard H2, review 2026-11-10 r4 ucpu3 checks-9, lane
# ucpu3fix) -- A BYTE SCAN EDGE ON THE CHARACTER-STEPPED REVERSE MACHINE. The
# driver's island branch builds the reverse machine's scan edge as a byte
# machine's would (ucp_design.md §3.8 H2: a skip steps a character's bytes one
# at a time). Measured at landing: 15 charstep corpus cells red (the subject
# tip's corpus: 9). The same plant on the RETRY machine's guard
# (build_notempty_dfa) is answer-equivalent -- the char-step retry walk reads
# no scan-edge field -- and is not a row (lane report).
SAB_ID="S3032-charstep-scan-edge"
SAB_FILE="src/core/compile.c"
SAB_SUITES="charstep"
SAB_DESC="the character-stepped reverse machine gets a byte scan edge (hazard H2)"
SAB_DOC_FIGURE='charstep arm: 15 corpus cells red (measured at landing, lane ucpu3fix); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3032.'
SAB_REACH='"$PCREC" -e utf8 --features all -p rx -o "$REACH_TMP/o0.c" --pattern "(*UCP)\\b\\w+\\b" >/dev/null 2>&1 && grep -c "define RX_DFA_SCAN \"char-step\"" "$REACH_TMP/o0.c"'
SAB_REACH_EXPECT="1"
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='                if (island) {
                    build_notempty_dfa(&cx);'
SAB_AFTER='                if (island) {
                    pcrec_scanedge_dfa(&cx, &cx.job->rdfa,   /* SABOTAGE S3032 */
                                       pcrec_dfa_scan_state_written(&cx, &cx.job->rdfa), false);
                    build_notempty_dfa(&cx);'
