#!/usr/bin/env bash
# S463 ([K82] (B), lane k82hbuild) -- THE HANDOFF STARTS ONE BYTE TOO LATE (K - 1).
#
# Witness: (?m)^x{2,5}(?i:cat) on "xxxxxCaT", the attempt route: (0,8) becomes
# NOMATCH. Detector: tests/litscan/handoff.rxt's maximum-offset rows on the
# attempt and hybrid routes. The design's own coverage report for this plant
# over every K > 0 mover is docs/dev/optloop/s4/k82hbuild/k82h_answers.py
# ONLY_K_POS=1 (litscan_k82h.md §4.2a (c)).
SAB_ID="S463-handoff-k-minus-one"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="harness prechecks"
SAB_HARNESS_TARGET="tests/litscan/handoff.rxt"
SAB_DESC='the handoff subtracts K - 1, so the scan starts one byte too late: a match that begins exactly K bytes before its window is lost on the attempt and hybrid routes (the unanchored scan'\''s reverse pass, bounded by search_from, re-finds its start, so that route hides it)'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/k82hbuild_report.md §6); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S463.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern '\''(?m)^x{2,5}(?i:cat)'\'' && grep -q '\''^#define RX_REQ_HANDOFF "3"'\'' "$REACH_TMP/o.c" && echo REACH-HANDOFF-K3'
SAB_REACH_EXPECT='REACH-HANDOFF-K3'
SAB_REACH_POP='tests/litscan/handoff.rxt|^pattern \(\?m\)\^x\{2,5\}|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    long long k = req_handoff_k(cx);
    /* the run is the landmark only where the pre-check TESTS it (part_d.md'
SAB_AFTER='    long long k = req_handoff_k(cx) - (req_handoff_k(cx) > 0 && req_handoff_k(cx) < PCREC_W_UNBOUNDED); /* SABOTAGE S463 */
    /* the run is the landmark only where the pre-check TESTS it (part_d.md'
# RE-AIMED 2026-10-11 (lane rlhbuild, [REQ-HANDOFF-L1]): K is the LANDMARK's
# (`req_landmark_maxoff`, the run window's where a run ships, so every run
# witness reads the same K); the anchor carries the entry's round-up target
# so it cannot land on the re-entry's own K read (`pf_emit_handoff`). Intent
# unchanged: the ENTRY starts one byte too late.
# RE-AIMED 2026-10-27 (lane reqvm1, [REQRUN-VM]): K is `req_handoff_k`, the
# landmark's on the DFA-scan routes and the whole run's on the VM attempt
# loop's rows; the anchor carries the next line so it stays the entry's.
# Intent unchanged: the ENTRY starts one byte too late.
# RE-AIMED 2026-11-09 (lane sar1, span_arms R1 [REPEAT-RUN]): a repeat is
# its copies, so `x{2,5}`'s tail `xx` joins `(?i:cat)` and the run is `xxCAT`,
# at most 3 bytes in (K 3, was 5 for `CAT`). The probe reads the new K. Intent
# unchanged and re-checked by plant: the entry starts one byte too late and
# handoff.rxt reads (1,8) where (0,8) is expected (185 cells).
# RE-ANCHORED 2026-11-11 (lane k382, R-38 K38-2): the context line's `run` reads the whole run (the cut window
# retired); K is the whole run's wherever a run is the landmark. Probe unchanged (re-read:
# REQ_HANDOFF "3"). Intent unchanged: the ENTRY starts one byte too late.
# RE-AIMED 2026-11-12 (lane rpfix2, [REQ-PAST-LAST]; ported onto K38-2's
# whole-run context line by lane rpport 2026-11-13): the round buffer moved
# into the bounded branch, so the anchor is the k/whole/run lines plus the
# next comment; K is lowered only where it is bounded and positive (an
# unbounded K - 1 would leave the unbounded branch). Intent unchanged.
# RE-ANCHORED 2026-11-13 (lane rps3b, [RUN-POS-SET] stage 3, part_d §9 item 4):
# the context line's `run` reads the tested predicate (`req_run_tested_cx`)
# under a new comment, so the anchor is the k line plus that comment's first
# line (unique: `emit_req_landmark_move`'s k line is followed by code). Probe
# unchanged (re-read on the branch: REQ_HANDOFF "3"). Intent unchanged: the
# ENTRY starts one byte too late.
