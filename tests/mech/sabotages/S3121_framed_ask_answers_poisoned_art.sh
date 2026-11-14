#!/usr/bin/env bash
# S3121 ([MEMFN] span_pick 3.0b, D27 finding F1's second half; lane d27fix) -- THE ASK ANSWERS 0 ON A POISONED ART.
#
# WHAT IT BREAKS AND WHO CATCHES IT: the framed ask's last guard (it answers -1 whenever its plan
# function set the art's sticky error) is dropped. No green input reaches the fenced defect path, so the
# plant also reopens one (S3120's: the pinned ranking under the art's tie): the DEFINE ask then answers
# 0 with the art's error set, where mf_define refuses. The detector is the D27 frame suite
# (tests/memfn/d27_frame/): ask_sets_no_error, poisoning_ask_answers_refusal, refuse_iff_define_refuses.
SAB_ID="S3121-framed-ask-answers-poisoned-art"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="memfnd27frame"
SAB_DESC='the framed ask answers 0 although its plan function set the art'"'"'s error (with a defect path reopened): the ask and mf_define disagree (D27 finding F1)'
SAB_DOC_FIGURE='Validated by plant (lane d27fix, docs/dev/lanes/d27fix_report.md), by hand on a copy of the tree: D27_QUICK=1 tests/memfn/d27_frame/run.sh red. Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3121.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (art->err[0]) {
        memset(out, 0, sizeof *out);
        rc = -1;
    }'
SAB_AFTER='    /* SABOTAGE S3121: no poisoned-art guard */'
SAB_FILE2="memfn/src/window.c"
SAB_COUNT2=1
SAB_BEFORE2='        if (d->pinned) ro.tie = member_opts(d, &m->alt->spans[m->run]).tie;'
SAB_AFTER2='        /* SABOTAGE S3121: the art'"'"'s tie for every ranking (S3120'"'"'s, reopening the path) */'
