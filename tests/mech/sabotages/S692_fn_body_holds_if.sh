#!/usr/bin/env bash
# S692 ([MEMFN] R4e'.0b, lane r4e0b) -- A DIRECTIVE IN A FUNCTION THAT DOES WORK.
#
# WHAT IT BREAKS. D155 addendum 1: "a function that does work never contains
# #if". `<fn>__body` is the function that does the work (the scalar loop);
# the CPU choice belongs to the selector's whole body or to file scope
# (integration.md §R4.9.2.5). The plant opens the helper's body with an
# empty `#if 1`/`#endif` pair, the shape of a SIMD arm spliced into the
# scalar text. Answer-identical (the pair guards nothing).
#
# WHERE IT IS SEEN. C11's routing leg ("<fn>__body holds a directive", arm
# memfnstamps) and C5's pins (arm memfnarms).
SAB_ID="S692-fn-body-holds-if"
SAB_FILE="memfn/src/ofsskip.c"
SAB_SUITES="memfnstamps memfnarms"
SAB_DESC="the seam writes an #if/#endif pair at the top of <fn>__body, a conditional directive in a function that does work (D155 addendum 1)"
SAB_DOC_FIGURE="HAND-MEASURED by lane r4e0b 2026-10-09 (one mech row, solo): see docs/dev/lanes/r4e0b_report.md §5. Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S692."
SAB_REACH='"$PCREC" --features all -p rx -o - --pattern "abc[0-9]+xyz"'
SAB_REACH_EXPECT='static inline size_t rx_ofsskip__body(const unsigned char *subject, size_t n, size_t pos)'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (fn_head(art, h, p, x.body_fn, o) || body->render(art, h, &x, o)) return -1;'
SAB_AFTER='    if (fn_head(art, h, p, x.body_fn, o) || (o->puts(o->u, "#if 1\n#endif\n"), 0) ||   /* SABOTAGE S692 */
        body->render(art, h, &x, o)) return -1;'
