#!/usr/bin/env bash
# S610 ([START-TABLE] C6, lane stc67; docs/design/start_table.md §1.1 `desc`, §3.2 C6, docs/dev/lanes/stc67_report.md) -- a LISTED row with no `desc`: the `memchr` NEXT row keeps its `--list-axes` listing and loses the one-line text that sits beside it since C6.
# Detectors: (candoracle) tests/codegen/run_cand_oracle.sh -- the trace
# build's table self-check, run at every checked decision, aborts with
# `CANDORACLE table-desc-unlisted` on a listed row without a desc (or an
# unlisted one with); (registry) tests/registry/run_registry_tests.sh --
# `--list-axes` projects the row's desc as the `applies` cell, so the
# listing itself loses the row's text. No artifact byte and no answer moves:
# the corpus arm is not named, by design.
SAB_ID='S610-cand-row-listed-without-desc'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='candoracle registry'
SAB_DESC='a listed cand_rows[] row (memchr) loses the desc the listing projects; the self-check and the axis registry check must fail'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/stc67_report.md §2); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S610.'
SAB_REACH='"$PCREC" --list-axes | grep -qP "^prefilter\t9\tmemchr\t" && echo REACH-LISTED'
SAB_REACH_EXPECT='REACH-LISTED'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='      .desc = "forward scan, one candidate byte",'
SAB_AFTER='      .desc = NULL,   /* SABOTAGE S610 */'
