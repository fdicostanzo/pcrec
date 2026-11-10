#!/usr/bin/env bash
# S2990 -- span_pick unit 3.0a (docs/design/memfn/plan_frame.md rev 2.2 §5 row (O), [rev2 F4]; lane s30a). THE
# RENDERABILITY GATE UNSCOPED: fd_holds applies the frame's renderable set to slot PRES too.
#
# Plant: the gate's `r->slot == FD_FIND` scope is dropped, so every PRES row (pick FF_UNSTATED, which no search
# renderer row names) declines and every pre-check link decision falls to no terminal.
# Detector: tests/memfn/run_finder.sh (arm memfnfinder): its presence checks' sites are refused ("the presence
# decision refuses this site: a presence span no routed PRES row decides", "fd-P0: PRES decided []"; measured by
# lane s30a). REACH equality on P0-P9 and emit_sweep on the pre-check composites see it too (landing jobs).
# RE-ANCHORED at the r1 s30a review fixes (lane s30arev, F2): the gate compares wf_renders to its named
# answer WF_RENDERS_NOT; intent unchanged.
SAB_ID="S2990-renderable-gate-unscoped"
SAB_FILE="memfn/src/finder.c"
SAB_SUITES="memfnfinder"
SAB_DESC='the renderable set gates slot PRES as well as FIND: every PRES row declines, every presence span is refused'
SAB_DOC_FIGURE='MEASURED 2026-11-09 BY HAND after the re-aim, planted by hand on a git archive of lane/memfn-s30a c8d54df7c (lane s30arev, review r1 s30a fixes), built with nice make -j2; 15 patterns x 4 arms compiled by the planted and the clean pcrec and classed: LOUD 26 ("the memfn kit refuses the pre-check'"'"'s presence spans"), SAME 34; memfnfinder 56fail/3227pass. Earlier: lane s30a 2026-11-07 (test-memfn-finder red). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S2990.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (r->slot == FD_FIND && wf_renders(q->frame, fd_pick_of(r, q), q->site) == WF_RENDERS_NOT) return 0;'
SAB_AFTER='    if (wf_renders(q->frame, fd_pick_of(r, q), q->site) == WF_RENDERS_NOT) return 0;   /* SABOTAGE S2990 */'
