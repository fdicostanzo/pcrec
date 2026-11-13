#!/usr/bin/env bash
# S3104 -- R-38 K38-3 (docs/design/memfn/span_runs_sheet.md §5's K38-3 row; §3.5 W-K4a/W-K4b;
# lane k383). THE PASS LIST DROPS THE WIDER-LEVEL TARGET: G2's presence family runs only the baseline and generic passes, so no pass's target admits the wider vector level and its cells are never
# measured (every remaining floor still holds: the floors are per pass).
# Detector: the family's LEVEL-LIST COVERAGE check (every level the kit lists, mf_levels through
# tests/memfn/simd_levels.c, admitted by a target the pass list runs on this host): "level has
# no runnable target", a named failure, not a pass with fewer floors. Its vehicle is this mech row
# (the script is the planted file; --plant edits files under memfn/src only).
SAB_ID="S3104-g2pres-pass-list-drops-v3"
SAB_FILE="memfn/tests/run_g2_pres.sh"
SAB_SUITES="g2pres"
SAB_DESC="the presence family's pass list loses the wider-level target: the level-list coverage check must red (a level has no runnable target)"
SAB_DOC_FIGURE="HAND-MEASURED by lane k383 2026-11-12 (docs/dev/lanes/k383_report.md): a copy of memfn/tests/run_g2_pres.sh with this edit RED, checks failed 1 (FAIL: level has no runnable target). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3104."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='TARGETS="x86-64-v3 x86-64 generic"'
SAB_AFTER='TARGETS="x86-64 generic"   # SABOTAGE S3104'
SAB_REACH='TMPDIR="$REACH_TMP" bash "$TREE/memfn/tests/run_g2_pres.sh" --reach'
SAB_REACH_EXPECT="REACH-G2P-LEVELS"
