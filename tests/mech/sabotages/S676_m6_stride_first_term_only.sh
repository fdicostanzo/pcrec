#!/usr/bin/env bash
# S676 ([MEMFN] M6, lane m6) -- THE STRIDED ADVANCE TESTS ONE POSITION.
# The kit's generic ADVANCE (stmt_advance) renders one `(member)` per term of
# a strided site (RULED Q-R10-2, MF_SITE_ABI 8); the plant keeps only term 0,
# so the VM cursor rung's strided span loop steps W bytes whenever position 0
# holds. A wrong answer on every strided body the corpus reaches (the capture
# route in tests/possessify/possessify.rxt: z(ab)*y), and the pins move.
# RE-ANCHORED 2026-11-04 (lane mechfix1): the loop bound `(strided ? 1u : nterm)` skipped the later terms'
# member_test, so their class tables were defined and never referenced (-Werror=unused-const-variable
# in the artifact: ANOMALY). The later terms are still built, and left out of
# the test (`&& (1 || ...)`): the same mutant, the tables stay referenced.
SAB_ID="S676-m6-stride-first-term-only"
SAB_FILE="memfn/src/generic.c"
SAB_SUITES="harness memfnarms"
SAB_HARNESS_TARGET="tests/possessify/possessify.rxt"
SAB_DESC='the kit'"'"'s ADVANCE render tests only term 0 of a STRIDED site (nterm > 1): the VM'"'"'s strided span loop advances W bytes when the FIRST position matches, so (ab)* consumes '"'"'ax'"'"''
SAB_DOC_FIGURE="HAND-MEASURED by lane m6 2026-10-08 (plant applied, tree rebuilt; docs/dev/lanes/m6_report.md section 6): harness tests/possessify/possessify.rxt 20 failed / 3517 passed (wrong answers, (?:a\.)+\b on \"aa.a.\" answers (0,2) not (1,3), plus the unused class-bitmap compile failures of (?:a[a.])+\b); memfnarms 14 failed / 324 passed (six strided pins and six m6_target freezes move; check 13 answers 829,945 of 5,142,837 calls wrong). The matrix figure is owed at the slot."
SAB_REACH='"$PCREC" -p rx --engine=vm -o - --pattern "(?:ab)+c"'
SAB_REACH_EXPECT='while ((rx_span_cursor + 2 <= subject_length) && (subject[rx_span_cursor + 0] == 97) && (subject[rx_span_cursor + 1] == 98)) {'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (t) kb_puts(&test, " && ");
        member_test(rc, &test, &s->pred.term[t], t, byte.p ? byte.p : "0");'
SAB_AFTER='        if (strided && t) {   /* SABOTAGE S676: later terms are built but never decide (`1 ||`), so their class tables stay referenced */
            kb drop;
            kb_init(&drop, rc->art->a);
            member_test(rc, &drop, &s->pred.term[t], t, byte.p ? byte.p : "0");
            kb_printf(&test, " && (1 || (%s))", drop.p ? drop.p : "0");
            continue;
        }
        if (t) kb_puts(&test, " && ");
        member_test(rc, &test, &s->pred.term[t], t, byte.p ? byte.p : "0");'
