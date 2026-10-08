#!/usr/bin/env bash
# S641 ([DEC-FALLBACK] B2, lane decfbB2) -- T2's overflow-drop row loses its force_off disjunct, so -fno-prefilter on a [SEL-1] retry would list no-fno-prefilter instead of no-dfa-overflow.
# S-T2e. Detector at B2: the listing oracle on --emit-ir -fno-prefilter ^(?:(?:a|b)*a(?:a|b){20})?$ (fbt (d) or-l-ovfs1); from B4 the check_ir_value row.
# B2 builds the tables BESIDE the old derivations and switches no reader, so
# until the reader switches the trace build's both-derivations oracle (abort
# on a difference, both orders) or fit_tables_selfcheck is the detector;
# the default build is unchanged by the plant.
SAB_ID='S641-t2-overflow-drop-no-force-off'
SAB_FILE='src/opt/select_engine.c'
SAB_SUITES='fallbacktable'
SAB_DESC="T2's overflow-drop row loses its force_off disjunct, so -fno-prefilter on a [SEL-1] retry would list no-fno-prefilter instead of no-dfa-overflow"
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S641. docs/dev/lanes/decfbB2_report.md carries the B2 run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='           (s->cx->collapse_reason != CR_SEL1 || s->force_off);'
SAB_AFTER='           (s->cx->collapse_reason != CR_SEL1);   /* SABOTAGE S641 */'
