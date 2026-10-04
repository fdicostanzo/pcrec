#!/usr/bin/env bash
# S448 ([OPT-LITSCAN] S4 C3, lane c3build) -- THE RUN ROW'S TERM IS THE WHOLE
# MASKED WINDOW, COMPARED EXACTLY.
#
# A run pin is a fact about EXACT positions: the run-pinned prefilter row
# compares the pinned exact stretch (`bytes + pin.at`, `pin.len`). This plant
# makes ofs_test_of take the whole window instead, at `pin.o - pin.at`, so
# the prefilter compares T exactly at a pair position: `a[bc]de`'s term
# becomes "abde" and `acde`, `zzacdezz` are deleted. Detector: the harness on
# reqcube.rxt's kept-pins block, and reqcube_check.py's ofsskip-equals-deny
# check. (Design's provisional S447, re-aimed by r2 R2-C3 from the pin to the
# run row's term.)
SAB_ID="S448-req-pin-takes-masked"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="harness codegen"
SAB_HARNESS_TARGET="tests/litscan/reqcube.rxt"
SAB_DESC="the run-pinned prefilter row's run term takes the whole masked window compared exactly instead of the pin's exact stretch, so a pair position is tested against T alone and matches carrying the other member are deleted"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/c3build_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S448."
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "a[bc]de" && grep -q "^#define RX_DFA_PREFILTER \"run-pinned\"" "$REACH_TMP/o.c" && grep -q "^#define RX_REQ_RUN \"61626465@2/fffeffff\"" "$REACH_TMP/o.c" && echo REACH-KEPT-PIN'
SAB_REACH_EXPECT="REACH-KEPT-PIN"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    int ro = pin.o, rl = pin.len, sp = ro + pin.idx;
    t->scan_k    = sp;
    t->scan_byte = r->bytes[pin.at + pin.idx];
    t->run_o     = ro;
    t->run_len   = rl;
    t->run_bytes = r->bytes + pin.at;'
SAB_AFTER='    int ro = pin.o - pin.at, rl = r->len, sp = pin.o + pin.idx;   /* SABOTAGE S448 */
    t->scan_k    = sp;
    t->scan_byte = r->bytes[pin.at + pin.idx];
    t->run_o     = ro;
    t->run_len   = rl;
    t->run_bytes = r->bytes;'
