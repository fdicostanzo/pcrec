#!/usr/bin/env bash
# S694 ([MEMFN] R4e'.0b, lane r4e0b) -- THE SELECTOR DOES NOT FORWARD ITS TABLES.
#
# WHAT IT BREAKS. "Every helper has the FUNC's own parameter list, table
# parameters included (table_params), so every call forwards the same
# argument list" (integration.md §R4.9.2.5). The plant drops the selector's
# table arguments: a function whose verify chain probes a multi-byte set's
# table (an offset-skip predicate with a set term) calls `<fn>__body` with
# too few arguments, and its artifact does not compile.
#
# WHERE IT IS SEEN. C11's routing leg ("a call that does not forward its
# parameters", arm memfnstamps) and C5's pins of the table-bearing fixtures
# (arm memfnarms).
SAB_ID="S694-fn-selector-drops-tables"
SAB_FILE="memfn/src/ofsskip.c"
SAB_SUITES="memfnstamps memfnarms"
SAB_DESC="the offset-skip function's selector calls <fn>__body without its table arguments, so a table-bearing artifact does not compile"
SAB_DOC_FIGURE="HAND-MEASURED by lane r4e0b 2026-10-09 (one mech row, solo): see docs/dev/lanes/r4e0b_report.md §5. Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S694."
SAB_REACH='"$PCREC" --features all -p rx -o - --pattern "[0-9]{4}-[0-9]{2}-[0-9]{2}"'
SAB_REACH_EXPECT='    return rx_ofsskip__body(subject, n, pos, rx_ofs_k0);'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    kit_out(o, "    return %s(subject, n, pos", callee);
    if (table_params(art, h, p, 0, o)) return -1;'
SAB_AFTER='    kit_out(o, "    return %s(subject, n, pos", callee);   /* SABOTAGE S694 */'
