#!/usr/bin/env bash
# S689 ([MEMFN] R4e'.0, lane r4e0; RE-AIMED by lane rowfix 2026-10-18) -- A
# PREFIX WALK THAT CHOOSES NO ROW IS TRACED AS A REFUSAL.
#
# WHAT IT GUARDS. fn_rows[]' PREFIX slot needs no row: a FUNC part whose
# PREFIX walk chooses none renders BODY alone, which is the ordinary answer,
# not a refused site. The row was written (lane r4e0) when the slot was
# EMPTY, and its first plant dropped kit_walk's empty-slot rule
# (memfn/src/compose.c `if (!any) return t->n;`), which made every PREFIX walk
# write a no-row END. Since R-13 batch 1 (55d5ece2c, lane r13) the PREFIX slot
# holds the SIMD rows vrun-w32/vrun-w16, so no walk of any kit table asks an
# empty slot any more (fn: BODY and PREFIX hold rows; fd: FIND and PRES hold
# rows; arms and rc have one slot), the empty-slot rule never fires, and that
# plant became an equivalent mutant (UNDETECTED on main 65dd423ee and on
# lane/memfn-b3b; docs/dev/lanes/rowfix_report.md). The choice now lives in
# the walk's tctx: fn_select marks the PREFIX walk OPTIONAL, and
# gate_trace_end then spells a no-row END `chosen=none`, never a refusal's
# `chosen=-`.
#
# WHAT IT BREAKS. The plant marks the PREFIX walk non-optional, so every FUNC
# part whose PREFIX walk chooses none (every one at -fno-memfn-simd, where the
# SIMD rows decline) writes `END ... chosen=-`, the trace's spelling of a
# REFUSED site (memfn/docs/trace_format.md), for a site the kit rendered.
#
# WHY NO ARTIFACT BYTE MOVES, AND WHERE IT IS SEEN. The default build traces
# nothing and the PREFIX answer is still "none", so no answer, artifact byte
# or pin moves. The N2 census reads the trace: its zero rule (rc 5: a
# would-decline or a no-row selection, `noend`) is the detector, on the
# sample the arm `n2sample` runs (tests/memfn/run_n2_sample.sh), which holds
# offset-skip and pre-check witnesses (SAB_REACH_POP).
SAB_ID="S689-empty-slot-walked"
SAB_FILE="memfn/src/ofsskip.c"
SAB_SUITES="n2sample"
SAB_DESC="fn_select stops marking the PREFIX walk optional, so a PREFIX walk that chooses no row writes a no-row END (a refusal, in the trace) for every FUNC part"
SAB_DOC_FIGURE="PENDING: re-aimed by lane rowfix 2026-10-18; the solo figure is recorded below once measured."
SAB_REACH='"$PCREC" --features all -p rx -o - --pattern "abc[0-9]+xyz"'
SAB_REACH_EXPECT='static inline size_t rx_ofsskip(const unsigned char *subject, size_t n, size_t pos)'
SAB_REACH_POP="tests/memfn/n2_sample_patterns.txt|^abc\\[0-9\\]\\+xyz\$|1"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    gate_tctx tc = { art, "fn", handle, MF_PH_DEFINE, &in, slot == FN_PREFIX, 0, 0 };'
SAB_AFTER='    gate_tctx tc = { art, "fn", handle, MF_PH_DEFINE, &in, 0 /* SABOTAGE S689 */, 0, 0 };'
