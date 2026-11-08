#!/usr/bin/env bash
# S2990 -- span_pick unit 3.0a (docs/design/memfn/plan_frame.md rev 2.2 §5 row (O), [rev2 F4]; lane s30a). THE
# RENDERABILITY GATE UNSCOPED: fd_holds applies the frame's renderable set to slot PRES too.
#
# Plant: the gate's `r->slot == FD_FIND` scope is dropped, so every PRES row (pick FF_UNSTATED, which no search
# renderer row names) declines and every pre-check link decision falls to no terminal.
# Detector: tests/memfn/run_finder.sh (arm memfnfinder): its presence checks' sites are refused ("the presence
# decision refuses this site: a presence span no routed PRES row decides", "fd-P0: PRES decided []"; measured by
# lane s30a). REACH equality on P0-P9 and emit_sweep on the pre-check composites see it too (landing jobs).
SAB_ID="S2990-renderable-gate-unscoped"
SAB_FILE="memfn/src/finder.c"
SAB_SUITES="memfnfinder"
SAB_DESC='the renderable set gates slot PRES as well as FIND: every PRES row declines, every presence span is refused'
SAB_DOC_FIGURE='MEASURED by lane s30a 2026-11-07, planted and reverted by hand (test-memfn-finder red, then green); exact re-run: bash tests/mech/run_sabotage_matrix.sh S2990.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (r->slot == FD_FIND && !wf_renders(q->frame, fd_pick_of(r, q), q->site)) return 0;'
SAB_AFTER='    if (!wf_renders(q->frame, fd_pick_of(r, q), q->site)) return 0;   /* SABOTAGE S2990 */'
