#!/usr/bin/env bash
# S3283 -- lane formsfixb (review r35 F17): THE LOOP TESTS THE NEXT BYTE. wf_loop (memfn/src/window.c)
# reads S[C + J + 1] for entry J, so each looped entry tests its neighbour's byte (one past the
# stretch at its end): the loop's text, start and end unchanged, so G2's exact loop pin holds, and
# only an answer whose looped stretch is broken at a known entry can see it. The detector is G2's
# WINDOW family's DETERMINISTIC BREAKS (memfn/tests/run_g2_win.sh; g2_win_run.c run_breaks: the
# stretch's first two and last two entries, the head's three, the stop's sides) and the long rows'
# breaks, in every head pass.
SAB_ID="S3283-span-loop-reads-next"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="g2win"
SAB_DESC="wf_loop tests S[C + J + 1]: a looped entry reads its neighbour, G2's window family's deterministic breaks must red"
SAB_DOC_FIGURE="G2's WINDOW family (memfn/tests/run_g2_win.sh, arm g2win), the deterministic breaks: lane formsfixb 2026-11-17. Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3283."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    kb_printf(&byte, "%s[%s + %s]", rc->S, rc->C, rc->J);'
SAB_AFTER='    kb_printf(&byte, "%s[%s + %s + 1]", rc->S, rc->C, rc->J);   /* SABOTAGE S3283 */'
