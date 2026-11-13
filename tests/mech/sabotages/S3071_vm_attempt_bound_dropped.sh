#!/usr/bin/env bash
# S3071 ([FIND-MINW], lane s1fix, review r1-s1 CHECKS-2) -- the VM attempt loop's minimum-width bound (`const size_t attempt_max = subject_length - W;`) is never declared, so the loop runs to the subject's end.
# The plant removes answers nothing (the stop only removes work), so the corpus
# stays green; the detector is run_prechecks.sh §1.3b, which holds the emitted
# text to "present by default, absent under the minimum-width test lever".
SAB_ID='S3071-vm-attempt-bound-dropped'
SAB_FILE='src/gen/emit_vm.c'
SAB_SUITES='prechecks'
SAB_DESC='the VM attempt loop'\''s minimum-width bound (`const size_t attempt_max = subject_length - W;`) is never declared, so the loop runs to the subject'\''s end'
SAB_DOC_FIGURE='OWED: not yet run (lane s1fix, 2026-11-12; cloud mechrows). Expected: prechecks red on [1.3b].'
SAB_REACH='"$PCREC" --features all -p rx --engine=vm -o "$REACH_TMP/o.c" --pattern '\''a(b|c)+d'\'' && grep -Eq '\''^    const size_t attempt_max = subject_length - 3ULL;$'\'' "$REACH_TMP/o.c" && echo REACH-VM-ATTEMPT-MAX'
SAB_REACH_EXPECT='REACH-VM-ATTEMPT-MAX'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    } else if (vm_general_min_width(width)) {'
SAB_AFTER='    } else if (0 && vm_general_min_width(width)) {   /* SABOTAGE S3071 */'
