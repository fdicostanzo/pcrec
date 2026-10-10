#!/usr/bin/env bash
# S695 ([MEMFN] R4e'.0b, lane r4e0b) -- THE SELECTOR ABOVE ITS HELPER.
#
# WHAT IT BREAKS. The seam writes the pieces in a fixed order: `<fn>__body`,
# then the PREFIX row's helpers, then the selector `<fn>` (integration.md
# §R4.9.2.5: "each helper is defined before the one that falls to it, and
# the selector FUNC follows all of them"). The plant writes the selector
# first, so it calls a function not yet declared (an error under gnu11 at
# gcc 14+) and the artifact does not compile.
#
# WHERE IT IS SEEN. C11's routing leg ("<fn>__body is defined below <fn>",
# arm memfnstamps; it also reads the artifacts' compile in its LIBC half) and
# C5's pins (arm memfnarms).
SAB_ID="S695-fn-helper-below-selector"
SAB_FILE="memfn/src/ofsskip.c"
SAB_SUITES="memfnstamps memfnarms"
SAB_DESC="the seam writes the selector <fn> above its helper <fn>__body, so the selector calls an undeclared function"
SAB_DOC_FIGURE="HAND-MEASURED by lane r4e0b 2026-10-09 (one mech row, solo): see docs/dev/lanes/r4e0b_report.md §5. Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S695."
SAB_REACH='"$PCREC" --features all -p rx -o - --pattern "abc[0-9]+xyz"'
SAB_REACH_EXPECT='    return rx_ofsskip__body(subject, n, pos);'
SAB_EXPECT=DETECTED
SAB_COUNT=1
# Re-aimed by lane r13 (R-13, 2026-10-09): its anchor moved with the R4e' batch 1 seam
# (kit_walk's per-row step / fn_rows[]'s decl column / the seam's level blocks); same intent.
SAB_BEFORE='    if (fn_head(art, h, p, x.body_fn, o) || body->render(art, h, &x, o)) return -1;'
SAB_AFTER='    if (fn_selector(art, h, p, fn, x.body_fn, rung, names, nr, o)) return -1;   /* SABOTAGE S695 */
    if (fn_head(art, h, p, x.body_fn, o) || body->render(art, h, &x, o)) return -1;
    return 0;'
