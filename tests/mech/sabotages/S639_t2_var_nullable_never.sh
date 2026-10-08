#!/usr/bin/env bash
# S639 ([DEC-FALLBACK] B2, lane decfbB2) -- T2's var-nullable row (F1's holder) never applies, so a nullable ${...} pattern would lose its declined-nullable-default stamp.
# S-T2a. Detector at B2: the admission oracle's declined-flags check on ^${v}$ (fbt (a) adm-varnul, (d) or-a-vnul/or-l-vnul); from B4 fbt (b)/ir.
# B2 builds the tables BESIDE the old derivations and switches no reader, so
# until the reader switches the trace build's both-derivations oracle (abort
# on a difference, both orders) or fit_tables_selfcheck is the detector;
# the default build is unchanged by the plant.
SAB_ID='S639-t2-var-nullable-never'
SAB_FILE='src/opt/select_engine.c'
SAB_SUITES='fallbacktable'
SAB_DESC="T2's var-nullable row (F1's holder) never applies, so a nullable \${...} pattern would lose its declined-nullable-default stamp"
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S639. docs/dev/lanes/decfbB2_report.md carries the B2 run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return pfa_default_scope(s) && pfa_var(s) && pcrec_fact_nullable(s->cx);'
SAB_AFTER='    return false && pfa_default_scope(s) && pfa_var(s) && pcrec_fact_nullable(s->cx);   /* SABOTAGE S639 */'
