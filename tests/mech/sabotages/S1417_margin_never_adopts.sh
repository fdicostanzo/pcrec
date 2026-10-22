#!/usr/bin/env bash
# S1417 (D172 S2 commit 6, lane wsc5) -- THE OFFSET-k SELECTION NEVER FIRES,
# in its new home: the window family's MARGIN row (memfn/src/window.c
# `m_margin_holds`) never adopts the RESEED alternative, so the reply always
# chooses PARKED and no artifact takes the offset-k form. Every answer in the
# tree stays correct and the row's measured 4.5x-17.1x is gone: detectable
# ONLY by a check that counts the population (tests/offsetskip's witnesses).
#
# SUCCESSOR of S187 (retired at commit 6 with src/opt/prefix_k.c, whose
# `pcrec_prefix_ksets` it planted): the selection is the kit's since commit 6
# (window_site.md rev 3.2 §2.1 MARGIN, §3.2). Same detectors, same intent.
SAB_ID="S1417-margin-never-adopts"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="harness offsetskip"
SAB_HARNESS_TARGET="tests/offsetskip/offset_skip.rxt"
SAB_DESC="the window family's MARGIN row never adopts the RESEED alternative, so no artifact takes the offset-k form. Every answer in the tree stays correct and the row's measured 4.5x-17.1x is gone: detectable ONLY by a check that counts the population"
SAB_DOC_FIGURE="Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1417."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return l < r || (l == r && wf_ties[T_MARGIN].to == TIE_RESEED);'
SAB_AFTER='    return 0 && (l < r || (l == r && wf_ties[T_MARGIN].to == TIE_RESEED));   /* SABOTAGE S1417 */'
