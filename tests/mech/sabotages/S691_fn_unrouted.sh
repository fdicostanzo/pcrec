#!/usr/bin/env bash
# S691 ([MEMFN] R4e'.0b, lane r4e0b) -- THE ROUTING UNDONE.
#
# WHAT IT BREAKS. R4e'.0b moves each offset-skip/pre-check function's loop
# under `<fn>__body` and makes `<fn>` one call to it (D155 item 6: "the
# SIMD-off artifact routes through the helper too ... so the floor rule stays
# exact"). The plant renders the loop under `<fn>` itself and writes no
# selector: exactly the parent's (abi 68's) text, the shape a later SIMD row
# could only reach by putting a directive inside a function that does work.
# Answer-identical: the parent's function.
#
# WHERE IT IS SEEN. C11's routing leg ("<fn> is not routed: no <fn>__body",
# arm memfnstamps) and C5's pins (arm memfnarms).
SAB_ID="S691-fn-unrouted"
SAB_FILE="memfn/src/ofsskip.c"
SAB_SUITES="memfnstamps memfnarms"
SAB_DESC="the seam renders the offset-skip function's loop under <fn> itself and writes no selector, the pre-R4e'.0b shape (D155 item 6 undone)"
SAB_DOC_FIGURE="HAND-MEASURED by lane r4e0b 2026-10-09 (one mech row, solo): see docs/dev/lanes/r4e0b_report.md §5. Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S691."
SAB_REACH='"$PCREC" --features all -p rx -o - --pattern "abc[0-9]+xyz"'
SAB_REACH_EXPECT='static inline size_t rx_ofsskip__body(const unsigned char *subject, size_t n, size_t pos)'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (fn_head(art, h, p, x.body_fn, o) || body->render(art, h, &x, o)) return -1;
    if (prefix && prefix->render(art, h, &x, o)) return -1;
    return fn_selector(art, h, p, fn, x.body_fn, o);'
SAB_AFTER='    if (fn_head(art, h, p, fn, o) || body->render(art, h, &x, o)) return -1;   /* SABOTAGE S691 */
    if (prefix && prefix->render(art, h, &x, o)) return -1;
    return 0;'
