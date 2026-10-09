#!/usr/bin/env bash
# S689 ([MEMFN] R4e'.0, lane r4e0) -- AN EMPTY SLOT IS WALKED AS A SELECTION.
#
# WHAT IT BREAKS. kit_walk (memfn/src/compose.c) asks a table's rows only in
# the asked SLOT, and a slot that holds no row is no selection: it records
# nothing. fn_rows[]' PREFIX slot is born empty (integration.md §R4.9.2.1),
# so the seam's PREFIX walk records nothing today. The plant drops the
# empty-slot rule, so every FUNC part's PREFIX walk writes a SEL and an END
# with no chosen row, the trace's spelling of a REFUSED site
# (memfn/docs/trace_format.md) for a site the kit rendered.
#
# WHY NO ARTIFACT BYTE MOVES, AND WHERE IT IS SEEN. The default build traces
# nothing and the PREFIX answer is still "none", so no answer, artifact byte
# or pin moves. The N2 census reads the trace: its zero rule (rc 5: a
# would-decline or a no-row selection) is the detector, on the sample the arm
# `n2sample` runs (tests/memfn/run_n2_sample.sh), which holds offset-skip and
# pre-check witnesses.
SAB_ID="S689-empty-slot-walked"
SAB_FILE="memfn/src/compose.c"
SAB_SUITES="n2sample"
SAB_DESC="kit_walk walks a slot that holds no row, so fn_rows[]' empty PREFIX slot writes a no-row END (a refusal, in the trace) for every FUNC part"
SAB_DOC_FIGURE="HAND-MEASURED by lane r4e0 2026-10-09 (one mech row, solo): see docs/dev/lanes/r4e0_report.md §4. Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S689."
SAB_REACH='"$PCREC" --features all -p rx -o - --pattern "abc[0-9]+xyz"'
SAB_REACH_EXPECT='static inline size_t rx_ofsskip(const unsigned char *subject, size_t n, size_t pos)'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (!any) return t->n;              /* nothing to ask: no selection */'
SAB_AFTER='    (void)any;   /* SABOTAGE S689 */'
