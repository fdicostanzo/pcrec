#!/usr/bin/env bash
# S3127 -- R-38 Part D D3 (docs/design/memfn/part_d.md rev 4 section 5.1 D3, plant p11; lane partd2).
# The same plant as memfn/tests/run_g2_pres.sh --plant S3127 (its plant_spec; one source of the text).
SAB_ID="S3127-census-parser-skips-set-terms"
SAB_FILE="docs/design/memfn/span_pick/census0.py"
SAB_SUITES="g2pres"
SAB_DESC='the census parser of the derived run part record skips its SET terms: the census counts no unspelled position where G2 counts some (D3 reds)'
SAB_DOC_FIGURE="DESIGNED by lane partd2 2026-11-13; MEASURED by the lane's box gate job (memfn/tests/run_g2_pres.sh --plant S3127, docs/dev/lanes/partd2_report.md). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3127."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        off, kind, val = t.split(":", 2)
'
SAB_AFTER='        off, kind, val = t.split(":", 2)
        if kind == "SET":   # SABOTAGE S3127
            continue
'
SAB_REACH='TMPDIR="$REACH_TMP" bash "$TREE/memfn/tests/run_g2_pres.sh" --reach'
SAB_REACH_EXPECT="REACH-G2P-LEVER-PASS"
