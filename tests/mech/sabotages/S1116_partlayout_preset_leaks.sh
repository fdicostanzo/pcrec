#!/usr/bin/env bash
# S1116 ([ENTRY-TABLE] E1, lane e1; compound_entries.md §3.2.4, §3.6 "preset
# resolution") -- A DAGGER CELL LEAKS. Every part-layout preset cell is `†`
# (docs/spec/tuning.md §5.4), so every `--tune` position resolves to T0 and
# no artifact carries `_PART_LAYOUT` unless a caller set a control. Planted,
# `+2` presets residual `inline` in src/core/tune.c while the spec still says
# `†`. Seen by the evaluator's `--tune=max-speed` rows (expected read from
# the SPEC's §5.4, never from tune.c) and the `preset-empty` fixture.
SAB_ID="S1116-partlayout-preset-leaks"
SAB_FILE="src/core/tune.c"
SAB_SUITES="partlayout"
SAB_DESC='the max-speed row of TUNE_TABLE presets residual inline though tuning.md §5.4 keeps the cell a dagger, so --tune=max-speed lays parts out with no control set'
SAB_DOC_FIGURE="HAND-VALIDATED by lane e1 (2026-10-18, a git-archive copy of the e1 tree with the plant applied by tests/mech/lib/replace.py, rebuilt, and tests/partlayout/run_partlayout_tests.sh run against it): partlayout:10fail/31pass against a clean 0fail/41pass. The solo mech run is OWED (docs/dev/lanes/e1_report.md)."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_REACH='"$PCREC" -p rx --part-layout=prefilter:inline -o "$REACH_TMP/x.c" --pattern "(a)b" && grep -h "RX_PART_LAYOUT" "$REACH_TMP/x.c"'
SAB_REACH_EXPECT='#define RX_PART_LAYOUT "prefilter=inline"'
SAB_BEFORE='    { PCREC_TUNE_MAX_SPEED, "max-speed",  0,      0, 8192, 0, 0, 0, 0 }'
SAB_AFTER='    { PCREC_TUNE_MAX_SPEED, "max-speed",  0,      0, 8192, 0, PCREC_PART_INLINE, 0, 0 }   /* SABOTAGE S1116 */'
