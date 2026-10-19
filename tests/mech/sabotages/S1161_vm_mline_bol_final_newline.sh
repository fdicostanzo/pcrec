#!/usr/bin/env bash
# S1161 ([DD-11.5] P2b, lane ctxbuild) -- THE VM's (?m)^ FORM DROPS ITS `pos < n`.
# The VM spells MLINE_BOL's (in, absent) cell as `scan_position < subject_length`;
# without it a capture-bearing `(?m)^` (VM-routed) matches after a FINAL
# newline. Witness `(?m)^()` on "a\n" searched from 2: libpcre2 nomatch, the
# plant (2,2).
SAB_ID="S1161-vm-mline-bol-final-newline"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness assertions"
SAB_DESC='the VM'"'"'s (?m)^ test omits pos < n, so a VM-routed (?m)^ holds after a newline that ends the subject'
SAB_DOC_FIGURE='OWED: written by lane ctxbuild 2026-10-19 during a bench timing window (no mech run allowed); the post-window validation lane runs it. Read the figure from a run: bash tests/mech/run_sabotage_matrix.sh S1161.'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='        pcrec_sb_puts(b, "    if (scan_position == 0 || (scan_position < subject_length && (");'
SAB_AFTER='        pcrec_sb_puts(b, "    if (scan_position == 0 || (1 && (");   /* SABOTAGE S1161 */'
