#!/usr/bin/env bash
# S3072 ([FIND-MINW], lane s1fix, review r1-s1 CHECKS-2) -- the DFA forward scan's candidate-start filter block (`pf_close`) never ends the search where fewer than W bytes remain past its landing.
# The plant removes answers nothing (the stop only removes work), so the corpus
# stays green; the detector is run_prechecks.sh §1.3b, which holds the emitted
# text to "present by default, absent under the minimum-width test lever".
SAB_ID='S3072-dfa-pf-close-minw-dropped'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='prechecks'
SAB_DESC='the DFA forward scan'\''s candidate-start filter block (`pf_close`) never ends the search where fewer than W bytes remain past its landing'
SAB_DOC_FIGURE='OWED: not yet run (lane s1fix, 2026-11-12; cloud mechrows). Expected: prechecks red on [1.3b].'
SAB_REACH='"$PCREC" --features all -p rx  -o "$REACH_TMP/o.c" --pattern '\''cat|dog|cow|calf|camel'\'' && grep -Eq '\''^ {8,}if \(subject_length - [a-z_]+ < 3ULL\) return 0;$'\'' "$REACH_TMP/o.c" && echo REACH-DFA-PFCLOSE-MINW'
SAB_REACH_EXPECT='REACH-DFA-PFCLOSE-MINW'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (f->minw)
        pcrec_sb_printf(c, "%s    if (subject_length - %s < %lluULL) return 0;\n",'
SAB_AFTER='    if (0 && f->minw)   /* SABOTAGE S3072 */
        pcrec_sb_printf(c, "%s    if (subject_length - %s < %lluULL) return 0;\n",'
