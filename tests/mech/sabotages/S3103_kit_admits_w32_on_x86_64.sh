#!/usr/bin/env bash
# S3103 -- R-38 K38-3 (docs/design/memfn/span_runs_sheet.md §5's K38-3 row; §3.5 W-K4a/W-K4b;
# lane k383). THE EXACT-0 RULE'S CONTROL: the kit's admission rule (kit_target_levels) admits w32 on the x86-64 target while the listing's facts (targets.def features) do not, and the target's region is given avx2 so the text compiles.
# Detector: G2's presence family's per-level cells (K38-3): on the x86-64 passes the w32 cells read nonzero where the target admits none (exactly 0 required).
SAB_ID="S3103-kit-admits-w32-on-x86-64"
SAB_FILE="memfn/src/levels.c"
SAB_SUITES="g2pres"
SAB_DESC="the kit enters w32 arms on a target whose facts admit none: the exact-0 cells must red"
SAB_DOC_FIGURE="HAND-MEASURED by lane k383 2026-11-12 (docs/dev/lanes/k383_report.md): memfn/tests/run_g2_pres.sh --plant S3103 RED (CELL: x86-64.0: w32 U: 111 arm entries where the target admits none). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3103."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (admits(t, &level_table[lv])) m |= 1u << lv;'
SAB_AFTER='        if (admits(t, &level_table[lv]) || (lv == LV_X86_W32 && !strcmp(t->name, "x86-64"))) m |= 1u << lv;   /* SABOTAGE S3103 */'
SAB_FILE2="memfn/src/targets.def"
SAB_COUNT2=1
SAB_BEFORE2='MF_NEEDS("sse2"), "fxsr,mmx,sse,sse2",'
SAB_AFTER2='MF_NEEDS("sse2,avx2"), "fxsr,mmx,sse,sse2",   /* SABOTAGE S3103 */'
SAB_REACH='TMPDIR="$REACH_TMP" bash "$TREE/memfn/tests/run_g2_pres.sh" --reach'
SAB_REACH_EXPECT="REACH-G2P-W32-ARM"
