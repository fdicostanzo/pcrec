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
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "(?i)sel(?:ab)*ect" && grep -qE "^#define RX_REQ_RUN \"(53454c|454354)(@[0-9])?/dfdfdf\"$" "$REACH_TMP/o.c" && echo REACH-MIN0-SPLIT'
SAB_REACH_EXPECT="REACH-MIN0-SPLIT"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    RbRuns gap = rr_none(rr_rep_w(n < 0 ? -1 : n - m, b.maxw));'
SAB_AFTER='    RbRuns gap = m == 0 ? b : rr_none(rr_rep_w(n < 0 ? -1 : n - m, b.maxw));   /* SABOTAGE S446 */'
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
# RE-AIMED (lane sar1fix, 2026-11-09): since span arms R1 a min-0 repeat is
# T2 row 3 (`rr_rep_split`, the optional part a gap); the old anchor, the
# post-switch gap, was reached only under `--harness=restore=rep`. The plant
# now joins the body's runs across the optional part at the live site, the
# repeat's width kept. Intent unchanged.
# RE-AIMED (lane k382cm, 2026-11-12, R-38 K38-2): the reach still reads the necessary run split at the
# min-0 repeat (SEL or ECT, never SELABECT), but `<PREFIX>_REQ_RUN` now carries `@idx` only where this
# artifact's search reads a run position (match_api.md §6.3.7¶7 rows 1-2); this witness is row 3
# (`RX_REQ_WHY "dominated"`, no run part rendered), so it emits `454354/dfdfdf` with no `@` and the
# old pattern, which required one, read UNREACHED (cloud run 43239936557 shard 3). The `@` is now
# optional; the site (rr_rep_split's gap) and the intent are unchanged.
