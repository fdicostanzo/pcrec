#!/usr/bin/env bash
# S645 ([DEC-FALLBACK] B2, lane decfbB2) -- the attribution walk reads a fired row's off cell when the prefilter survived (kept/off swapped), so a surviving collapsed prefilter would stamp overflowed-*.
# The walk's cell choice (§1.7). Detector at B2: the attribution oracle on W_SEL1 (fbt (d) or-e-cpf; (a) through the old-first build); from B5 fbt (b).
# B2 builds the tables BESIDE the old derivations and switches no reader, so
# until the reader switches the trace build's both-derivations oracle (abort
# on a difference, both orders) or fit_tables_selfcheck is the detector;
# the default build is unchanged by the plant.
SAB_ID='S645-attrib-cells-swapped'
SAB_FILE='src/opt/select_engine.c'
SAB_SUITES='fallbacktable'
SAB_DESC="the attribution walk reads a fired row's off cell when the prefilter survived (kept/off swapped), so a surviving collapsed prefilter would stamp overflowed-*"
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S645. docs/dev/lanes/decfbB2_report.md carries the B2 run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        const unsigned char c = cx->fit_seq[i]->esel[fit->prefilter ? FIT_KEPT : FIT_OFF];'
SAB_AFTER='        const unsigned char c = cx->fit_seq[i]->esel[fit->prefilter ? FIT_OFF : FIT_KEPT];   /* SABOTAGE S645 */'
