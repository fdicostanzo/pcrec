#!/usr/bin/env bash
# S636 ([DEC-FALLBACK] B2, lane decfbB2) -- drop-anchored's sets cell keeps size_drop_rung, so the anchored machine would be built again and the retry refuse (K53 restored).
# S-F15. Detector at B2: the oracle's post-row sdr check on \p{L} -e utf8 (fbt (a) seq-anch, (d) or-anch); from B3 run_anchored_match.sh's K53 cell.
# B2 builds the tables BESIDE the old derivations and switches no reader, so
# until the reader switches the trace build's both-derivations oracle (abort
# on a difference, both orders) or fit_tables_selfcheck is the detector;
# the default build is unchanged by the plant.
# s636tri (2026-10-13): UNDETECTED since [OPT-REVEND] L2 moved the machine drop
# onto the row's FIRED bit (`Ctx.anchored_dropped`): `sdr` is now only the
# ladder's ordinal, which the later rungs compare with `<` (NONE and
# NO_ANCHORED both pass), so the plant moves no artifact byte -- the trace
# tuple's `sdr=` field is its one visible effect. Detector: run_fallback_table.sh
# (a)'s `fstate seq-anch 1 'sdr=1'` and the default-path chain `seq-anchland`
# (`\p{N}\p{L}\p{Lu}` -e utf8: 1,301,271 B with the machine, 761,331 B after).
SAB_ID='S636-t1-drop-anchored-keeps-sdr'
SAB_FILE='src/core/compile.c'
SAB_SUITES='fallbacktable'
SAB_DESC="drop-anchored's sets cell keeps size_drop_rung (the ladder ordinal stays NONE; the artifact is unchanged since L2, only the trace tuple's sdr= moves)"
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S636. docs/dev/lanes/decfbB2_report.md carries the B2 run.'
SAB_REACH='"$PCREC" --features all -e utf8 -p rx -o - --pattern "\p{N}\p{L}\p{Lu}" 2>/dev/null | grep -E "^#define RX_(ENGINE_SEL \"size-cap-retry\"|DFA_MATCH \"search-filter\")$"'
SAB_REACH_EXPECT='#define RX_ENGINE_SEL "size-cap-retry"
#define RX_DFA_MATCH "search-filter"'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='      .sets = { FIT_DD_KEEP, FIT_CR_KEEP, FIT_SDR_TO_ANCHORED, 0, 0, false, false },'
SAB_AFTER='      .sets = { FIT_DD_KEEP, FIT_CR_KEEP, FIT_SDR_KEEP, 0, 0, false, false },   /* SABOTAGE S636 */'
