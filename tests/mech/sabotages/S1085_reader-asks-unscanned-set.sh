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
# RE-POINTED (lane rowfix, 2026-10-18): since lmfacts (fe7ece905) the
# handoff's landmark admission is priced off the readers' class, so on the
# default witness `\B(?<!a)d` the plant flips the start search to `handoff`
# and no PF site is defined: the hold had one side and read UNDETECTED (main
# 65dd423ee 0/141, B3b 0/165). The witness line with `-fno-req-handoff`
# keeps the PF row emitted and defined, so the hold compares again.
SAB_ID="S1085-reader-asks-unscanned-set"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="candoracle"
SAB_DESC="the readers' PF site carries the escape set E, not the row's scanned set (a DFA hat's T)"
SAB_DOC_FIGURE="MEASURED 2026-10-18 by lane rowfix, solo (run_sabotage_matrix.sh S1085 at 3999c287e): DETECTED, candoracle 1fail/165pass, the -fno-req-handoff hat witness (docs/dev/lanes/rowfix_report.md)."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    pf_scan_set_of(cx, &cx->job->dfa, us, pf, sc);
    return pf_site_of(cx, pf, sc->set, us->views);'
SAB_AFTER='    *sc = us->cand;   /* SABOTAGE S1085 */
    return pf_site_of(cx, pf, sc->set, us->views);'
