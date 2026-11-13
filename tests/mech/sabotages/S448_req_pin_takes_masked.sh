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
SAB_DESC="the run-pinned prefilter row's run term takes the whole masked run compared exactly instead of the pin's exact stretch, so pcrec's record of the candidate test claims a pair position is tested against T alone: the run pre-check reads as dominated and is dropped (REQ_WHY dominated, OFFSETS 0,1,2*,3 on a[bc]de)"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/c3build_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S448."
# RE-AIMED 2026-10-23 (lane s3fix600, D172 S3 job 600): the witness is a fixed-width
# window, a `cover` artifact by default (no scan, so not this site); the probe's
# compile takes the cover row's deny --memfn=no-window-search, the build before S3.
SAB_REACH='"$PCREC" --memfn=no-window-search --features all -p rx -o "$REACH_TMP/o.c" --pattern "a[bc]de" && grep -q "^#define RX_DFA_PREFILTER \"run-pinned\"" "$REACH_TMP/o.c" && grep -q "^#define RX_REQ_RUN \"61626465@2/fffeffff\"" "$REACH_TMP/o.c" && echo REACH-KEPT-PIN'
SAB_REACH_EXPECT="REACH-KEPT-PIN"
SAB_EXPECT=DETECTED
SAB_COUNT=1
# RE-AIMED (D172 S2 commit 6, lane wsc5): the run term's stretch is the
# window family's reply (C-pin's), read by ofs_test_of; the plant takes the
# whole masked window instead, as before.
SAB_BEFORE='        t->run_o = w->run_lo;
        t->run_len = w->run_len;
        t->run_bytes = r->whole + (w->run_lo - (pin.o - pin.at));'
SAB_AFTER='        t->run_o = pin.o - pin.at;   /* SABOTAGE S448 */
        t->run_len = r->whole_len;
        t->run_bytes = r->whole;'
# RE-ANCHORED 2026-11-11 (lane k382, R-38 K38-2; span_runs_sheet.md §4.2): the run's bytes are the WHOLE run's
# (`r->whole`; the cut window `r->bytes` retired); the plant takes the whole masked run
# compared exactly at the run's position 0, as before. Probe unchanged (re-read: the stamp
# is still 61626465@2/fffeffff, run-pinned).
# RE-ANCHORED 2026-11-12 (lane k382mech): K38-2's ReqRun has no `len` (the cut window's
# length retired with it; mech 607 shard 1 read the plant BUILD-FAILED), so the plant takes
# `r->whole_len`, the whole run's, the length that goes with `r->whole`: the same fault. Its
# REACH moved: since K38-2 the OfsTest record no longer feeds the kit's window statement
# (main's `pcrec_memfn_wpos_cube` reader retired), so the emitted rx_ofsskip text is the
# kit's and unchanged under the plant, and answers hold (acde, zzacdezz still match on a
# scratch build with the plant). What moves is the record's readers: the run pre-check's
# `dominated` verdict (`ofs_test_verifies_run`) and the OFFSETS stamp, so a[bc]de reads
# REQ_WHY "dominated" and OFFSETS "0,1,2*,3" (clean: "emitted", "0,2*,3"). Detector:
# reqcube_check.py check 6 (the kept pin's REQ_WHY "emitted"), the codegen arm.
