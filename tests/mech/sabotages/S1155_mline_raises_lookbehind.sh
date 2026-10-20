#!/usr/bin/env bash
# S1155 ([DD-11.5] P2c SP-4d, lane ctxbuild; A8) -- THE (?m) BUILDER COPIES \b's
# LOOKBEHIND RAISE. libpcre2 reports a maximum lookbehind of 0 for `(?m)^a`; the
# plant raises pcrec's LB fact to 1, so `<PREFIX>_VALID_LB` moves under utf8.
# Detector: tests/assertions/run_assertions_tests.sh §1c's A8 cell (`(?m)^a`
# under -e utf8 stamps VALID_LB 0; control `\ba` stamps 1).
SAB_ID="S1155-mline-raises-lookbehind"
SAB_FILE="src/parse/parse.c"
SAB_SUITES="assertions"
SAB_DESC='the (?m) anchor builder raises the lookbehind length to 1 as \b does, so VALID_LB is 1 on (?m)^a where libpcre2 reports 0'
SAB_DOC_FIGURE='MEASURED 2026-10-20 (lane ctxbuild validation, solo mech row on the Linux dev box): asrt:1fail/56pass -- DETECTED'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='    pcrec_cpset_add_bits(&s, nc->set);'
SAB_AFTER='    pcrec_cpset_add_bits(&s, nc->set); pcrec_lb_raise(cx, 1);   /* SABOTAGE S1155 */'
