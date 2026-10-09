#!/usr/bin/env bash
# S678 ([MEMFN] M6, lane m6) -- THE MEMBER HOOK FORGETS ITS TERM.
# Before M6 `adv_member` ignored the term (every ADVANCE had one); at W > 1
# it must return member[term]. The plant returns position 0's test for every
# term: (ab)* runs over "aa..." blocks. pcrec-side: the kit pastes the hook's
# text opaque, so no kit check can see it; only answers can.
SAB_ID="S678-m6-adv-member-ignores-term"
SAB_FILE="src/gen/memfn_sites.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/possessify/possessify.rxt"
SAB_DESC='pcrec'"'"'s ADVANCE member hook (adv_member) ignores the term index again and hands the kit position 0'"'"'s class test for every position, so the VM'"'"'s strided span loop tests the first byte W times'
SAB_DOC_FIGURE="HAND-MEASURED by lane m6 2026-10-08 (plant applied, tree rebuilt; docs/dev/lanes/m6_report.md section 6): harness tests/possessify/possessify.rxt 20 failed / 3517 passed ((?:a\.)+\b on \"aa.a.\" answers (0,2) not (1,3); (?:a[a.])+\b fails to compile, its position-1 class bitmap unused); over the whole corpus every failing cell is in possessify.rxt. memfnarms cannot see it (the kit pastes the hook opaque). The matrix figure is owed at the slot."
SAB_REACH='"$PCREC" -p rx --engine=vm -o - --pattern "(?:ab)+c"'
SAB_REACH_EXPECT='while ((rx_span_cursor + 2 <= subject_length) && (subject[rx_span_cursor + 0] == 97) && (subject[rx_span_cursor + 1] == 98)) {'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return term < (uint32_t)a->stride ? a->member[term] : NULL;'
SAB_AFTER='    return term < (uint32_t)a->stride ? a->member[0] : NULL;  /* SABOTAGE S678 */'
