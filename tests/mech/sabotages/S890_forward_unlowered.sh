#!/usr/bin/env bash
# S890 (D164 B3, lane b3build; docs/design/endmark.md §R.7.2 P10; docs/dev/lanes/b3build_report.md) -- the tagged form's forward (and anchored) machine built WITHOUT the end mark's lowering: a mixed artifact (S1)
# Detector: tests/endmark/b3_rows.rxt under -fno-anchored-dfa (endmark arm): `(?:\s+|x\s*?)$` on "x\n" relocates over the view-based forward machine and the tagged reverse one, which disagree about the end, and loses (0,1).
# Reach: `(?:\s+|x\s*?)$` under -fno-anchored-dfa takes form tagged, mark_prio state-dependent (--emit-facts' end_mark: the form is internal bookkeeping with no
# stamp, D164 add. 2 Q4, and a DFA artifact has no --emit-ir listing).
SAB_ID='S890-forward-unlowered'
SAB_FILE='src/core/compile.c'
SAB_SUITES='endmark'
SAB_DESC='the tagged form'\''s forward (and anchored) machine built WITHOUT the end mark'\''s lowering: a mixed artifact (S1)'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S890.'
SAB_REACH='"$PCREC" --emit-facts --features all -fno-anchored-dfa --pattern "(?:\\s+|x\\s*?)$" | grep -F "form=tagged,prio=state-dependent" >/dev/null && echo REACH-FORM'
SAB_REACH_EXPECT='REACH-FORM'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    pcrec_build_nfa_marked(cx, root, &job->xnfa, false, &lo);'
SAB_AFTER='    pcrec_build_nfa_marked(cx, root, &job->xnfa, false, NULL);   /* SABOTAGE S890 */'
