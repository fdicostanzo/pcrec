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
SAB_DOC_FIGURE='MEASURED 2026-10-20 (lane ctxbuild validation, solo mech row on the Linux dev box): corpus:3fail/71278pass,asrt:0fail/57pass -- DETECTED'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='        pcrec_sb_puts(b, "    if (scan_position == 0 || (scan_position < subject_length && (");'
SAB_AFTER='        pcrec_sb_puts(b, "    if (scan_position == 0 || (1 && (");   /* SABOTAGE S1161 */'
