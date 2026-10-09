#!/usr/bin/env bash
# S690 ([MEMFN] R4e'.0b, lane r4e0b) -- THE SELECTOR DOES WORK.
#
# WHAT IT BREAKS. Since R4e'.0b (D155 item 6) every offset-skip/pre-check
# function `<fn>` is a SELECTOR: its loop is the helper `<fn>__body` and its
# whole body is one call, the SIMD-off arm a later CPU-guarded helper adds
# `#if` arms above (integration.md §R4.9.2.5). Frank's rule (D155 addendum
# 1): "a selector function's whole body may be the #if chain, one call per
# arm, and nothing else". The plant gives the selector a statement before its
# call (a bound test that changes no answer), the shape of a forwarder that
# grew work.
#
# WHERE IT IS SEEN. C11's routing leg (tests/memfn/routing_shape.py, arm
# memfnstamps: "a line that is not one call"), the rule itself rather than a
# digest; and C5's pins of every FUNC-bearing fixture (arm memfnarms).
SAB_ID="S690-fn-selector-does-work"
SAB_FILE="memfn/src/ofsskip.c"
SAB_SUITES="memfnstamps memfnarms"
SAB_DESC="the offset-skip function's selector runs a statement before its one call to <fn>__body, so the selector does work (D155 addendum 1)"
SAB_DOC_FIGURE="HAND-MEASURED by lane r4e0b 2026-10-09 (one mech row, solo): see docs/dev/lanes/r4e0b_report.md §5. Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S690."
SAB_REACH='"$PCREC" --features all -p rx -o - --pattern "abc[0-9]+xyz"'
SAB_REACH_EXPECT='    return rx_ofsskip__body(subject, n, pos);'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    kit_out(o, "    return %s(subject, n, pos", callee);'
SAB_AFTER='    o->puts(o->u, "    if (pos > n) return n;\n");   /* SABOTAGE S690 */
    kit_out(o, "    return %s(subject, n, pos", callee);'
