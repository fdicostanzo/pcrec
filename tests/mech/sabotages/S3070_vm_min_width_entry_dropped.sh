#!/usr/bin/env bash
# S3070 ([FIND-MINW], lane s1fix, review r1-s1 CHECKS-2) -- the VM search entry's general minimum-width check (`if (subject_length - search_from < W) return 0;`) is never emitted.
# The plant removes answers nothing (the stop only removes work), so the corpus
# stays green; the detector is run_prechecks.sh §1.3b, which holds the emitted
# text to "present by default, absent under --harness=no-min-width".
SAB_ID='S3070-vm-min-width-entry-dropped'
SAB_FILE='src/gen/emit_vm.c'
SAB_SUITES='prechecks'
SAB_DESC='the VM search entry'\''s general minimum-width check (`if (subject_length - search_from < W) return 0;`) is never emitted'
SAB_DOC_FIGURE='OWED: not yet run (lane s1fix, 2026-11-12; cloud mechrows). Expected: prechecks red on [1.3b].'
SAB_REACH='"$PCREC" --features all -p rx --engine=vm -o "$REACH_TMP/o.c" --pattern '\''a(b|c)+d'\'' && grep -Eq '\''^    if \(subject_length - search_from < 3ULL\) return 0;$'\'' "$REACH_TMP/o.c" && echo REACH-VM-ENTRY-MINW'
SAB_REACH_EXPECT='REACH-VM-ENTRY-MINW'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (vm_general_min_width(width))
        pcrec_emit_min_width_check(c, "    ", "search_from", "subject_length",
                                   v->root_minw);'
SAB_AFTER='    if (0 && vm_general_min_width(width))   /* SABOTAGE S3070 */
        pcrec_emit_min_width_check(c, "    ", "search_from", "subject_length",
                                   v->root_minw);'
