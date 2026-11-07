#!/usr/bin/env bash
# S2969 -- span_pick stage 2 unit S2e, sabotage (v2) (docs/design/memfn/span_cards.md §3.8 READY-4, §9's S2e
# row; lane memfn-s2e). KSGEN'S PRE-PARSE KEEPS THE CELLS.
#
# Plant: scripts/ksgen.c writes each set's pre-parse with the committed file's cells table.
# Detector: tests/knowledge/run_measures_tests.sh (arm knowledge) builds ksgen from source and runs it over the
# committed store: its table must equal the committed measures_table.inc, and meas_store_check.c over that
# fresh table (-DMSC_TABLE) must find every pre-parse equal to a fresh parse of the runner's stripped text with
# 0 cells (the named assertion). READING (lane s2e): the same compares over the COMMITTED table see this plant
# only after a `make gen-measures`, which no suite runs; the fresh generation is the detector of the generator.
SAB_ID="S2969-ksgen-preparse-keeps-cells"
SAB_FILE="scripts/ksgen.c"
SAB_SUITES="knowledge"
SAB_DESC='ksgen writes the measures pre-parse with the committed file cells (the embed is cell-less)'
SAB_DOC_FIGURE='MEASURED by lane memfn-s2e planted and reverted by hand (report, Sabotage); exact re-run: bash tests/mech/run_sabotage_matrix.sh S2969.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        put_tab(out, nsets, "cells", cells, pcrec_ks_meas_cell_w(set));'
SAB_AFTER='        put_tab(out, nsets, "cells", cells = &set->cells, pcrec_ks_meas_cell_w(set));   /* SABOTAGE S2969 */'
