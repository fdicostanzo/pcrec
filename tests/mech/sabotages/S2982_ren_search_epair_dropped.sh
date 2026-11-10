#!/usr/bin/env bash
# S2982 -- span_pick unit 3.0a (docs/design/memfn/plan_frame.md rev 2.2 §5 row (A); lane s30a). E-FIND'S PAIR
# SEARCH RENDERER ROW DROPPED.
#
# Plant: B-pair's row in window.c's search renderer table serves no pick (its keys emptied), so E-find's
# renderable set lacks PAIR: T-FIND's PAIR row declines on every E-find stop (the gate in fd_holds), and the
# stop goes to R7w (B-walk); B-fn, reachable only through B-pair's row (§2.4's dependency), declines too.
# Detector: tests/memfn/finder_check.py via run_finder.sh (arm memfnfinder): formhash's `pair` instance (an
# E-find window site over {X,x}) no longer reaches T-FIND's PAIR (wf_plan_brow returns R7w), so mf_form_hash(pair)
# does not resolve and the resolving-instance floor falls (measured by lane s30a: "mf_form_hash(pair) does not
# resolve", "9 form instances resolve, under the floor 10").
SAB_ID="S2982-ren-search-epair-dropped"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="memfnfinder"
SAB_DESC='E-find'"'"'s PAIR search renderer row serves no pick: PAIR is not renderable on E-find, its stops go to B-walk'
SAB_DOC_FIGURE='MEASURED by lane s30a 2026-11-07, planted and reverted by hand (test-memfn-finder red, then green); exact re-run: bash tests/mech/run_sabotage_matrix.sh S2982.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    [RB_PAIR]   = { { E_FIND, REN_PICK(FF_PAIR), "B-pair", NULL }, 1, "", NULL, b_pair_state,'
SAB_AFTER='    [RB_PAIR]   = { { E_FIND, 0, "B-pair", NULL }, 1, "", NULL, b_pair_state,   /* SABOTAGE S2982 */'
