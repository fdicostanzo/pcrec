#!/usr/bin/env bash
# S3532 -- plant (e) of block_span.md §10.2 (R-47 unit U4): the span form table walks T-vwin and T-vscan BEFORE T-lever and T-force (the enum order puts V's rows first). The escape hatches no longer win where V holds: the cards' lever and the force put a selector call where the table promises none. Caught by the T-table pin cells 17-20 (lever and force on [0-9a-f]{17}, both layers; tests/memfn/span_pins.py, run inside C18). Witness reached: D-hors, k 16, V's own predicate holds there (the pin cells' k source prints it).
SAB_ID='S3532-v-before-lever-and-force'
SAB_FILE='memfn/src/window.c'
SAB_SUITES='simdfloor'
SAB_DESC='V'\''s rows come ahead of T-lever and T-force in the span form table, so the lever and the force render the vector span'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3532. docs/dev/lanes/bsu4p_report.md carries the lane run.'
SAB_REACH='for f in --memfn=span-loop --harness=span-head=8; do if "$TREE/build/pcrec-harness" --features all -fmemfn-simd=x86-64-v3 -p rxa -o - $f --pattern "[0-9a-f]{17}" | grep -q "_vs0("; then echo "OVERRIDE-LOSES $f"; else echo "OVERRIDE-WINS $f"; fi; done'
SAB_REACH_EXPECT='OVERRIDE-WINS --memfn=span-loop
OVERRIDE-WINS --harness=span-head=8'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='enum { S_DENY, S_FORCE, S_LEVER, S_VWIN, S_VSCAN, S_HEAD };'
SAB_AFTER='enum { S_VWIN, S_VSCAN, S_DENY, S_FORCE, S_LEVER, S_HEAD };   /* SABOTAGE S3532 */'
