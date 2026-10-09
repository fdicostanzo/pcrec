#!/usr/bin/env bash
# S668 ([MEMFN-ROWCON] N2, lane m7fix) -- A KIT ROW'S `applies` ALWAYS HOLDS.
#
# WHAT IT BREAKS. A kit row's predicate (`applies`) is the SELECTOR; the
# contract gate only CHECKS a selection (N3). The plant makes
# `mismatch_inplace`'s predicate hold everywhere, which is exactly M7's
# shipped defect (inplace_applies returned 1, "the gate holds it to its
# sites"): the row sits just before `generic` in the arms walk, so every site
# no specialized row takes first selects it, the gate declines it, and the
# walk MOVES the selection to `generic`, the row it would have chosen anyway.
#
# WHERE IT IS SEEN. Nowhere but the N2 census: no answer, no artifact byte and
# no pin moves (the full census read 7,726,522 would-declines at zero
# movers). The census's own zero rule (rc 5, lane m7fix; until then the count
# was printed and never tested) is the detector, run on a sample by the arm
# `n2sample` (tests/memfn/run_n2_sample.sh). SAB_REACH proves both ends of the
# move are live in pcrec: the in-place fold's site chooses `mismatch_inplace`
# (its signature `unsigned char x, y;`) and the exact compare renders through
# `generic`; SAB_REACH_POP that the sample still holds the SKIP and MISMATCH
# witnesses the triage named (n2_triage.md).
SAB_ID="S668-n2-applies-always-holds"
SAB_FILE="memfn/src/mismatch.c"
SAB_SUITES="n2sample"
SAB_DESC="mismatch_inplace's applies predicate holds on every site, so the contract gate declines it everywhere and the walk moves every generic selection (zero movers; only the N2 census sees it)"
SAB_DOC_FIGURE="HAND-MEASURED by lane m7fix 2026-10-08 (plant applied, tree rebuilt, tests/memfn/run_n2_sample.sh): see docs/dev/lanes/m7fix_report.md section 2. The matrix figure is owed at the slot (the manager runs it solo)."
SAB_REACH='"$PCREC" --features all -p rx -o - --pattern "(?i)(ab)\1"; "$PCREC" --features all -p rx -o - --pattern "(a+)\1"'
SAB_REACH_EXPECT='        unsigned char x, y;
        if (at + i >= n || s[at + i] != ref[i])'
SAB_REACH_POP="tests/memfn/n2_sample_patterns.txt|^\\(\\?'n'a\\)\\+\$|1
tests/memfn/n2_sample_patterns.txt|^\\(\\?<n>\\\\w\\*\\?\\)\\*\\?a\\\\k'n'\$|1
tests/memfn/n2_sample_patterns.txt|^\\(\\?i\\)\\(\\.\\)\\\\1\$|1"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return s->form == MF_FORM_STMT && s->op == MF_OP_MISMATCH &&'
SAB_AFTER='    return 1 ? 1 : /* SABOTAGE S668 */ s->form == MF_FORM_STMT && s->op == MF_OP_MISMATCH &&'
