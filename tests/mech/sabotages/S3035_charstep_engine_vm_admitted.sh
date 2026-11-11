#!/usr/bin/env bash
# S3035 ([UCP] U3, review 2026-11-10 r4 ucpu3 checks-7, lane ucpu3fix) -- --engine=vm
# IS NOT REFUSED BESIDE A UNICODE WORD CONTEXT. The VM cannot read the
# Unicode word set (U4); without the refusal the VM route is taken. Measured
# at landing: the VM build stops at an internal error, so the reject row
# "--engine=vm" is red; the subject tip's reject table had no such row.
SAB_ID="S3035-charstep-engine-vm-admitted"
SAB_FILE="src/opt/select_engine.c"
SAB_SUITES="reject"
SAB_DESC="--engine=vm beside UCP \\b under utf8 is not refused by selection"
SAB_DOC_FIGURE='reject arm: the char-step "--engine=vm" row red (measured at landing, lane ucpu3fix).'
SAB_REACH='"$PCREC" -e utf8 --features all --engine=vm -p rx -o "$REACH_TMP/o0.c" --pattern "(*UCP)\\bx" 2>&1'
SAB_REACH_EXPECT="which --engine=vm excludes"
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='    if (cx->opt->engine == PCREC_ENGINE_VM)
        pcrec_ctx_fail(cx, iv->pos, "%s needs the character-stepped DFA, which "'
SAB_AFTER='    if (0)   /* SABOTAGE S3035 */
        pcrec_ctx_fail(cx, iv->pos, "%s needs the character-stepped DFA, which "'
