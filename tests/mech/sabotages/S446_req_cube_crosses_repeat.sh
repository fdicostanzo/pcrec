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
SAB_BEFORE='            rb_gap_into(acc, rr_rep_w(a->u.rep.rmax, t[0].runs.maxw));'
SAB_AFTER='            acc->set  = rb_union(rb_empty(), acc->set, rr_rep_w(a->u.rep.rmax, t[0].runs.maxw));
            acc->runs = rr_cat(t[0].runs, acc->runs);   /* SABOTAGE S446 */'
# RE-ANCHORED (lane dd10tri, 2026-10-22, dd10 stack-depth branch): the walk's
# arms became rb_*_into helpers over `acc` by pointer (PCREC_OWN_FRAME); the
# min-0 repeat arm is now one rb_gap_into call (shared with the class and
# unbounded arms, so the plant lands at THIS call site, not in the helper).
# Intent unchanged: the set shift kept, the body's runs joined across the
# zero-iteration repeat.
# RE-AIMED 2026-10-11 (lane rlhbuild, [REQ-HANDOFF-L1]): the min-0 repeat's
# arm now also shifts the SET's offsets (`rb_union(rb_empty(), acc.set, rw)`)
# and names the width `rw`; the plant still joins the body's runs across the
# zero-iteration repeat, the set shift kept.
# RE-ANCHORED 2026-10-05 ([K82] (B), lane k82hbuild), INTENT RE-VERIFIED: the
# min-0 repeat's `rr_none` now carries the body's WIDTH (the run offset walk);
# the plant still joins the body's runs across the zero-iteration repeat.
