#!/usr/bin/env bash
# S3073 ([FIND-MINW], lane s1fix, review r1-s1 CHECKS-2) -- the DFA search entry's minimum-width check (`if (subject_length - search_from < W) return 0;`) is never emitted (the scan's own pf_close check still runs).
# The plant removes answers nothing (the stop only removes work), so the corpus
# stays green; the detector is run_prechecks.sh §1.3b, which holds the emitted
# text to "present by default, absent under the minimum-width test lever".
SAB_ID='S3073-dfa-front-min-width-dropped'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='prechecks'
SAB_DESC='the DFA search entry'\''s minimum-width check (`if (subject_length - search_from < W) return 0;`) is never emitted (the scan'\''s own pf_close check still runs)'
SAB_DOC_FIGURE='OWED: not yet run (lane s1fix, 2026-11-12; cloud mechrows). Expected: prechecks red on [1.3b].'
SAB_REACH='"$PCREC" --features all -p rx  -o "$REACH_TMP/o.c" --pattern '\''cat|dog|cow|calf|camel'\'' && grep -Eq '\''^    if \(subject_length - search_from < 3ULL\) return 0;$'\'' "$REACH_TMP/o.c" && echo REACH-DFA-FRONT-MINW'
SAB_REACH_EXPECT='REACH-DFA-FRONT-MINW'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (fwd.minw)
            pcrec_emit_min_width_check(c, "    ", "search_from", "subject_length", fwd.minw);'
SAB_AFTER='        if (0 && fwd.minw)   /* SABOTAGE S3073 */
            pcrec_emit_min_width_check(c, "    ", "search_from", "subject_length", fwd.minw);'
