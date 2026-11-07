#!/usr/bin/env bash
# S2968 -- span_pick stage 2 unit S2e, sabotage (v1) (docs/design/memfn/span_cards.md §3.8 READY-4, §9's S2e
# row; lane memfn-s2e). THE MAKEFILE'S STRIP STEP KEEPS THE `cells` ROWS.
#
# Plant: the strip rule's awk never drops a row, so the stripped copy embed_text.sh embeds is the whole file.
# Detector: tests/knowledge/run_measures_tests.sh (arm knowledge) re-runs the strip step
# (`make meas-strip MEAS_STRIP_DIR=<scratch>`) and compares each copy with its OWN awk's strip of the committed
# file (no shared source). READING (lane s2e): §9 names the embedded-text compare (iii); that compare reads the
# COMMITTED measures_store.inc, which a Makefile edit moves only at the next `make gen-measures`, and no suite
# regenerates it; the fresh re-run is the detector that sees the strip step itself, and (iii) sees its output
# once regenerated.
SAB_ID="S2968-meas-strip-keeps-cells"
SAB_FILE="Makefile"
SAB_SUITES="knowledge"
SAB_DESC='the measures strip step keeps the cells rows (the embed would carry every cell)'
SAB_DOC_FIGURE='MEASURED by lane memfn-s2e planted and reverted by hand (report, Sabotage); exact re-run: bash tests/mech/run_sabotage_matrix.sh S2968.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='	awk '"'"'/^#section /{ s = $$2 } s == "cells" && !/^#/ && $$0 != "" { next } { print }'"'"' $< > $@.tmp'
SAB_AFTER='	awk '"'"'/^#section /{ s = $$2 } 0 && s == "cells" && !/^#/ && $$0 != "" { next } { print }'"'"' $< > $@.tmp   # SABOTAGE S2968'
