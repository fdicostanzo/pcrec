#!/usr/bin/env bash
# S3278 -- lane forms (R-45 plan A, r45_reply.md rev 6 §3 "The option"): THE FORCE SPELLING IS IGNORED.
# the span form table, wfS (memfn/src/window.c; formerly wf_span_head), drops the `--memfn=span-loop` arm, so the force compiles the
# default head and moves no byte: the option row's force cell is the base build. The detector is
# the `--memfn=` arm's reach (tests/axes/memfn_arm.py via run_axes.sh, arm axesmemfn): the cell
# `span-loop=force` is DIFFER-class with the witness `[0-9a-f]{32}` at c-default, which no longer
# differs from the default.
# Re-aimed by lane bsu1 (R-47 U1, block_span.md §10.2): wf_span_head retired into THE SPAN FORM TABLE (wfS); the plant is now T-force's predicate never holding.
SAB_ID="S3278-span-loop-force-ignored"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="axesmemfn"
SAB_DESC="the span form table's T-force never holds: --memfn=span-loop compiles the default, the memfn arm's span-loop=force witness must red"
SAB_DOC_FIGURE="tests/axes/memfn_arm.py's span-loop=force DIFFER cell (arm axesmemfn): lane forms 2026-11-17, by hand. Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3278."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='static int s_force_holds(const wf_sx *x) { return kit_opt_state(x->d->s->opts, WF_LOOP_ID) > 0; }'
SAB_AFTER='static int s_force_holds(const wf_sx *x) { (void)x; return 0; }   /* SABOTAGE S3278 */'
