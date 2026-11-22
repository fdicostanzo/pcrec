#!/usr/bin/env bash
# S3531 -- plant (d) of block_span.md §10.2 (R-47 unit U4): the span-vector deny is ignored (the span form table's option column reads as no option for every row). The wrapper is live at SIMD-off, so the deny's artifact equals the default's and answer identity cannot see it; the detector is the repeatable form of the identity gate, tests/axes/memfn_arm.py's span-vector DIFFER rows; under this arm (axesmemfn: MEMFN_EVERY=40, REACH_ONLY) memfn_arm applies the 28 byte / 20 utf8 floors only at full population (every == 1), so what reds here is the row's SPAN_BENCH WITNESSES (`[0-9a-f]{32}`, `\b[0-9a-f]{32}\b`, `\d{32}`, byte and utf8, both layers: 12 checks), which are evaluated whatever the sampling; the floors red too at a full `make test-axes` (r78 PLANTSA-1).
SAB_ID='S3531-span-vector-deny-ignored'
SAB_FILE='memfn/src/window.c'
SAB_SUITES='axesmemfn'
SAB_DESC='the span form table reports no deny option for any row, so --memfn=no-span-vector compiles the default and the span-vector DIFFER rows SPAN_BENCH witnesses must red (the floors only at full population)'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3531. docs/dev/lanes/bsu4p_report.md carries the lane run.'
SAB_REACH='if "$PCREC" --features all -p rxa -o - --memfn=no-span-vector --pattern "[0-9]{25}" | grep -q "_vs0("; then echo DENY-IGNORED; else echo DENY-HONOURED; fi; if "$PCREC" --features all -p rxa -o - --pattern "[0-9]{25}" | grep -q "_vs0("; then echo DEFAULT-V; else echo DEFAULT-NO-V; fi'
SAB_REACH_EXPECT='DENY-HONOURED
DEFAULT-V'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='static const char *s_opt(size_t i) { return wf_spanrows[i].opt; }'
SAB_AFTER='static const char *s_opt(size_t i) { (void)i; return NULL; }   /* SABOTAGE S3531 */'
