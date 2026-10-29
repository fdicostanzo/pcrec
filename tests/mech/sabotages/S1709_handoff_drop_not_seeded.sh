#!/usr/bin/env bash
# S1709 ([REQRUN-VM], lane reqvm1rung) -- THE RETRY FORGETS THE `drop-handoff` ROW FIRED. `Ctx.req_handoff_dropped` is
# seeded from the fired record on every attempt; the plant never sets it, so
# the retry emits the same rows again and the row is asked a second time (the
# trace build's once invariant aborts: CANDORACLE fit-once).
# Detector (arm fallbacktable): tests/codegen/run_fallback_table.sh (a)'s
# seq-pfcd2 / seq-hodrop / seq-horef sequences.
SAB_ID='S1709-handoff-drop-not-seeded'
SAB_FILE='src/core/compile.c'
SAB_SUITES='fallbacktable'
SAB_DESC='the retry after the drop-handoff row is not told it fired, so the VM-side handoff rows are emitted again'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/reqvm1rung_report.md, Tests and sabotage); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1709.'
SAB_REACH='"$PCREC" --features all -e utf8 -p rx -o - --pattern "(\p{Xwd})x" 2>&1 >/dev/null | grep -c "required-run handoff"'
SAB_REACH_EXPECT='1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        cx.req_handoff_dropped =
            (fit_fired >> (fit_rung_of(FIT_DROP_HANDOFF) - fit_rungs)) & 1u;'
SAB_AFTER='        cx.req_handoff_dropped = false;   /* SABOTAGE S1709 */'
