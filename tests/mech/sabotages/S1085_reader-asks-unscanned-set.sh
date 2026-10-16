#!/usr/bin/env bash
# S1085 (lane fdb2fix, [MEMFN] R17-b' B2 review item 2) -- THE READERS ASK A SITE
# THE DEFINE DOES NOT WRITE: `cand_pf_site` hands the kit the start state's
# escape set E instead of the row's scanned set, so on a DFA hat (whose
# scanned set T is a proper subset of E) G1/R4/L4 read the class of a site
# no artifact carries. The realistic divergence: the readers' constructor
# re-deriving the set rather than reading `pf_scan_set_of`.
# Detector (candoracle): the trace build's ASKED-CLASS hold
# (`cand_asked_hold`, the define side at `pf_define_find_at`): CANDORACLE asked-class-differs
# on the DFA-hat witnesses of cand_oracle_witnesses.tsv.
SAB_ID="S1085-reader-asks-unscanned-set"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="candoracle"
SAB_DESC="the readers' PF site carries the escape set E, not the row's scanned set (a DFA hat's T)"
SAB_DOC_FIGURE="MEASURED 2026-10-16 by lane fdb2fix, solo (run_sabotage_matrix.sh S1085): DETECTED, candoracle 1fail/99pass (docs/dev/lanes/fdb2_report.md §10.3)."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    pf_scan_set_of(cx, &cx->job->dfa, us, pf, sc);
    return pf_site_of(cx, pf, sc->set, us->views);'
SAB_AFTER='    *sc = us->cand;   /* SABOTAGE S1085 */
    return pf_site_of(cx, pf, sc->set, us->views);'
