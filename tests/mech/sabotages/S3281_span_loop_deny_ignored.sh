#!/usr/bin/env bash
# S3281 -- lane formsfixb (review r35 F15, R-45 r45_reply.md rev 6 §3 "The option"): THE DENY IS IGNORED.
# the span form table, wfS (memfn/src/window.c; formerly wf_span_head), drops the `--memfn=no-span-loop` arm, so the deny compiles the
# default head: at pcrec's default width (no offset past 32) deny == default by construction, so the
# axes arm's ASSERT_ZERO cell cannot see it, and the cards' arm I would time H(64) under I's name.
# The detector is G2's WINDOW family's long rows (memfn/tests/run_g2_win.sh): stretches of 500 and
# 1024 positions rendered under the deny must loop nowhere (the deny's witness at a width past 64),
# floored by `default deny witnesses`.
# Re-aimed by lane bsu1 (R-47 U1, block_span.md §10.2): wf_span_head retired into THE SPAN FORM TABLE (wfS); the plant is now T-deny's predicate never holding.
SAB_ID="S3281-span-loop-deny-ignored"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="g2win"
SAB_DESC="the span form table's T-deny never holds: --memfn=no-span-loop loops past the head, G2's window family's long-row deny witnesses must red"
SAB_DOC_FIGURE="G2's WINDOW family (memfn/tests/run_g2_win.sh, arm g2win), the long rows' deny witnesses: lane formsfixb 2026-11-17. Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3281."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='static int s_deny_holds(const wf_sx *x)  { return kit_opt_state(x->d->s->opts, WF_LOOP_ID) < 0; }'
SAB_AFTER='static int s_deny_holds(const wf_sx *x)  { (void)x; return 0; }   /* SABOTAGE S3281 */'
