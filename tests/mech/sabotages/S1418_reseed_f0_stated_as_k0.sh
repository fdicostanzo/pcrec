#!/usr/bin/env bash
# S1418 (D172 S2 commit 6, lane wsc5) -- MISCOMPILE-1 RESTORED IN THE
# STATEMENT: pcrec states the RESEED alternative's offset-0 span F0 as the DFA
# escape set k0 (`us->cand.set`, can_begin_match's question) with no table
# offer, instead of the walk's own frontier[0] (src/gen/emit_dfa.c
# `pf_window_of`), so the family's verify at offset 0 tests the SCAN's set
# against the START's question. Every \b-before-a-non-word-atom pattern
# (`\b\.[0-9]{4}Z`) then refuses its real candidates and LOSES MATCHES.
#
# SUCCESSOR of S188 (retired at commit 6 with src/opt/prefix_k.c, whose
# selection it fed a walk with k0 at offset 0): since commit 6 the verify
# plan is the kit's, built from what pcrec STATES, so the defect's home is
# the statement (window_site.md rev 3.2 §1.1: F0 never k0). Same detectors.
SAB_ID="S1418-reseed-f0-stated-as-k0"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="harness offsetskip"
SAB_HARNESS_TARGET="tests/offsetskip/offset_skip.rxt"
SAB_DESC="the RESEED alternative's offset-0 span F0 is stated as the DFA escape set k0 (no table offer) instead of the walk's frontier[0], so the family's offset-0 verify refuses real candidates of every \\b-before-a-non-word-atom pattern and LOSES MATCHES"
SAB_DOC_FIGURE="Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1418."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        pcrec_memfn_wpos_table(&sp[0], 0, wk->k[0].set,
                               wk->k[0].count > 1 ? WIN_OFFER_OFS + 0u : 0u);'
SAB_AFTER='        pcrec_memfn_wpos_table(&sp[0], 0, us->cand.set, 0u);   /* SABOTAGE S1418 */'
