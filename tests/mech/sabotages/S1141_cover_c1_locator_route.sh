#!/usr/bin/env bash
# S1141 ([KIT-VERIFY] Z2, lane z2build; docs/design/kit_proof.md §6.3) -- C1 is keyed on the LOCATOR route: a VM-finisher hybrid whose inlined prefilter is a DFA body is admitted
# kit_proof.md §6.3 S1141: bench `syntax/grp-named-quote` (`(?'w'cat)`, a hybrid) reads RX_DFA_SCAN "cover".
# DECLARED EQUIVALENT at Z2 (lane z2fix, 2026-10-21): the plant cannot admit a
# hybrid, because C4 (anchored-A) declines every one. The anchored machine A is
# built only where a FINISH row on the compile's finisher route declares it
# (build_anchored_dfa, src/core/compile.c: `verify-at`, the DFA route alone),
# so on a VM-finisher route `anchored_ok` is false and C4 fails. Under the plant
# the witness's first failing row moves from C1 finisher-dfa to C4 anchored-A
# (MEASURED, trace build) and its artifact is unchanged; the population figure
# (every census item C1 declines, re-decided planted: cover admissions 0) is
# docs/design/kit_proof/z2/s1141pop.py's, run by the queued z2fix job. What
# would make it DETECTED: a VM-route FINISH row that declares the anchored
# machine; then C1 is the only guard and kitproof's (?'w'cat) verdict fires.
SAB_ID='S1141-cover_c1_locator_route'
SAB_FILE='src/gen/known.c'
SAB_SUITES='kitproof'
SAB_DESC='C1 is keyed on the LOCATOR route: a VM-finisher hybrid whose inlined prefilter is a DFA body is admitted'
SAB_DOC_FIGURE='MEASURED UNDETECTED by lane z2build'"'"'s matrix run (boxqueue 542, at f74db3788): kitproof:0fail/88pass, reach ok; equivalent mutant (see the header), declared by lane z2fix; the solo re-run is the z2fix queue job (docs/dev/lanes/z2build_report.md, FIX (z2fix)).'
SAB_REACH='bash "$TREE/tests/kitproof/reach.sh" "$TREE" '"'"'-'"'"' '"'"'(?'"'"'"'"'"'"'"'"'w'"'"'"'"'"'"'"'"'cat)'"'"''
SAB_REACH_EXPECT='REACH-DECLINE'
SAB_EXPECT=UNDETECTED
SAB_EXPECT_REASON='equivalent at Z2: C4 (anchored-A) declines every VM-finisher hybrid, since the anchored machine is built only on the DFA finisher route (build_anchored_dfa); the planted (?'"'"'w'"'"'cat) moves its first failing row C1 -> C4 and its artifact not at all (lane z2fix, measured)'
SAB_COUNT=1
SAB_BEFORE='    return pcrec_cand_finisher_dfa(st->cx);'
SAB_AFTER='    return pcrec_cand_finisher_dfa(st->cx) || st->cx->job->fit.prefilter;   /* SABOTAGE S1141 */'
