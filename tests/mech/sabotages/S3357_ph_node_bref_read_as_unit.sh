#!/usr/bin/env bash
# S3357 (review r53 F3, lane l1fix 2026-11-19; docs/design/span_arms.md §14.3 D-10, remodel 3) -- THE HEAD'S PER-KIND RULE READS A BACKREFERENCE AS A ZERO-WIDTH UNIT instead of a wall (`pcrec_ph_node`, src/facts/desc.c, the BREF/VAR/CALL arm). The head of `\1dd` then reads `d` at its first position, so in `(a)(?:ab|\1dd|ad)` the alternation owner merges `ad` past `\1dd`: on `aadd` pcrec answers (0,3) where libpcre2 answers (0,4), group 1 (0,1).
# Detector: tests/altcls/altnf_rules.rxt's S-b block (generated from libpcre2 10.46 by docs/dev/lanes/altbuild_evidence/altnf_rules_gen.py). The wall was unbound before remodel 3 too (the same wall in anf_head, the same corpus).
# HAND-MEASURED by lane l1fix 2026-11-19 (plant on a scratch export of lane/l1build, harness on the one file): 2 of 84 cases fail (the S-b block's `aadd` span and its group slot); unplanted 84/84.
SAB_ID='S3357-ph-node-bref-read-as-unit'
SAB_FILE='src/facts/desc.c'
SAB_SUITES='harness'
SAB_HARNESS_TARGET='tests/altcls/altnf_rules.rxt'
SAB_DESC='the head rule reads a backreference as a zero-width unit, so (a)(?:ab|\1dd|ad) merges ad past \1dd and answers (0,3) on aadd where libpcre2 answers (0,4)'
SAB_DOC_FIGURE='HAND-MEASURED by lane l1fix 2026-11-19: altnf_rules.rxt 2 of 84 fail; read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3357.'
SAB_REACH='"$PCREC" -p rx --features all -o - --pattern "(a)(?:ab|\\1dd|ad)" | grep -o "ALTCLS_[A-Z]* [0-9]*" | sort -u'
SAB_REACH_EXPECT='ALTCLS_FACTORED 1
ALTCLS_MERGES 0'
SAB_REACH_POP='tests/altcls/altnf_rules.rxt|^pattern \(a\)\(\?:ab\|\\1dd\|ad\)$|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    case A_BREF:
    case A_VAR:
    case A_CALL:
        return pcrec_ph_wall(0, false, 0, true);'
SAB_AFTER='    case A_BREF:
        return pcrec_ph_unit();   /* SABOTAGE S3357 */
    case A_VAR:
    case A_CALL:
        return pcrec_ph_wall(0, false, 0, true);'
