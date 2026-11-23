#!/usr/bin/env bash
# S3533 -- plant (f) of block_span.md §10.2 (R-47 unit U4): T-vscan is keyed on the finder's pick FF_WALK (rev 2's key) instead of the brow R7w. D1w shares R7w's pick, so ab[0-9]{26} under --memfn=no-fd-d1 (D1w, k 26) gains a selector call it must not have. Caught by T-table pin cell 15 (tests/memfn/span_pins.py, run inside C18), the only cell that separates the two keys.
SAB_ID='S3533-vscan-keyed-on-walk-pick'
SAB_FILE='memfn/src/window.c'
SAB_SUITES='simdfloor'
SAB_DESC='T-vscan holds on the finder pick FF_WALK instead of the brow R7w, so a D1w site (k 26) renders the vector span'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3533. docs/dev/lanes/bsu4p_report.md carries the lane run.'
SAB_REACH='for p in "ab[0-9]{26}"; do if "$PCREC" --features all -fmemfn-simd=x86-64-v3 --memfn=no-fd-d1 -p rxa -o - --pattern "$p" | grep -q "_vs0("; then echo "V-PRESENT $p"; else echo "V-ABSENT $p"; fi; done; for p in "[0-9]{25}"; do if "$PCREC" --features all -fmemfn-simd=x86-64-v3 -p rxa -o - --pattern "$p" | grep -q "_vs0("; then echo "V-PRESENT $p"; else echo "V-ABSENT $p"; fi; done'
SAB_REACH_EXPECT='V-ABSENT ab[0-9]{26}
V-PRESENT [0-9]{25}'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return fd_brow_is(x->w->brow, FD_NAMED_R7W) && x->k >= WF_VSCAN_LO &&'
SAB_AFTER='    return x->w->pick == FF_WALK && x->k >= WF_VSCAN_LO &&   /* SABOTAGE S3533 */'
