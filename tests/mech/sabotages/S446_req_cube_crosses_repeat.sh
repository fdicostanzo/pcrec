#!/usr/bin/env bash
# S446 ([OPT-LITSCAN] S4 C3, lane c3build) -- THE NECESSARY RUN JOINS ACROSS A
# MIN-0 REPEAT.
#
# The min-0 repeat arm of src/facts/req.c's walk contributes `rr_none`, which
# BREAKS contiguity: the bytes either side abut only in the match where the
# repeat takes no iterations. This plant joins the body's runs instead, so
# `(?i)sel(?:ab)*ect` claims the masked run SELABECT and the pre-check
# deletes `select`, the zero-iteration match. Detector: the harness on
# tests/litscan/reqcube.rxt (that block's `select`/`SELECT`/`xxSeLeCtxx`
# cells), and every corpus pattern of the shape. (litscan_s4.md §5.5's
# provisional S445, renumbered at landing: S445 was taken by C1.)
SAB_ID="S446-req-cube-crosses-repeat"
SAB_FILE="src/facts/req.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/litscan/reqcube.rxt"
SAB_DESC="the necessary-run walk's min-0 repeat arm joins its body's runs to its neighbours instead of breaking contiguity, so a run is claimed across an iteration that may not happen and the pre-check deletes the zero-iteration match"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/c3build_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S446."
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "(?i)sel(?:ab)*ect" && grep -qE "^#define RX_REQ_RUN \"(53454c|454354)@[0-9]/dfdfdf\"$" "$REACH_TMP/o.c" && echo REACH-MIN0-SPLIT'
SAB_REACH_EXPECT="REACH-MIN0-SPLIT"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='             * exactly as a multi-member class is. */
            acc.runs = rr_cat(rr_none(), acc.runs);'
SAB_AFTER='             * exactly as a multi-member class is. */
            acc.runs = rr_cat(rb_walk(w, a->l).runs, acc.runs);   /* SABOTAGE S446 */'
