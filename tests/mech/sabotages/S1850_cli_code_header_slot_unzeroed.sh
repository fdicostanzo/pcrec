#!/usr/bin/env bash
# S1850 (lane fsfix, 2026-10-30) -- cli_push_code_header leaves the realloc'd
# PcrecCodeHeader slot unzeroed, so .file/.line are heap garbage. The code arm
# runs --code-header under MALLOC_PERTURB_=190, where the emitter strlen()s the
# garbage file and the CLI dies (SEGV, rc 139).
SAB_ID='S1850-cli-code-header-slot-unzeroed'
SAB_FILE='cli/main.c'
SAB_SUITES='code'
SAB_DESC='cli_push_code_header no longer zeroes the new slot before cli_code_header fills lang/header'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1850. docs/dev/lanes/fsfix_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    hv[st->ncode_headers] = (PcrecCodeHeader){ 0 };'
SAB_AFTER='    /* SABOTAGE S1850: slot left as the allocator gave it */'
