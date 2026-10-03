#!/usr/bin/env bash
# S452 ([OPT-LITSCAN] S4 C3, lane c3build) -- K65'S WHOLE-SET HALF MARKS A
# PAIR POSITION'S T AS PROVED.
#
# On a VM route with no DFA scan, K65's second half memchrs every necessary
# set member the run did not prove. At a pair position T is one member and
# the subject may hold the other, so T is not proved; this plant marks it.
# On `(x?)([a-z]+)+S\d(?i:select)\1` the set is {S}, select's first T is S,
# K65's memchr('S') disappears, and a hostile subject turns from NOMATCH into
# a step give-up -- the direction D124 item 3 forbids. Detector: the harness
# on reqcube.rxt's S2b blocks (n -> gu), and reqcube_check.py's rq_set check.
# (Design's provisional S451.)
SAB_ID="S452-set-rest-marks-masked"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="harness codegen"
SAB_HARNESS_TARGET="tests/litscan/reqcube.rxt"
SAB_DESC="K65's whole-set half marks every whole-run position's T as already proved, including pair positions, so a set member equal to such a T loses its memchr and a NOMATCH turns into a step give-up"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/c3build_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S452."
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "(x?)([a-z]+)+S\\d(?i:select)\\1" && grep -q "rq_set\[\] = { 83 }" "$REACH_TMP/o.c" && echo REACH-K65-REST'
SAB_REACH_EXPECT="REACH-K65-REST"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            if (r->whole_mask[k] == 0xFF) done[r->whole[k]] = true;'
SAB_AFTER='            done[r->whole[k]] = true;   /* SABOTAGE S452: a pair position marked proved */'
