#!/usr/bin/env bash
# S678 ([MEMFN] M6, lane m6) -- THE MEMBER HOOK FORGETS ITS TERM.
# Before M6 `adv_member` ignored the term (every ADVANCE had one); at W > 1
# it must return member[term]. The plant returns position 0's test for every
# term: (ab)* runs over "aa..." blocks. pcrec-side: the kit pastes the hook's
# text opaque, so no kit check can see it; only answers can.
# RE-PLANTED 2026-10-31 (lane r30bfix): the member[0] plant left every
# position >= 1 class bitmap unreferenced, so a pattern like (?:a[a.])+\b
# failed the harness's -Werror compile (m6's own figure below records it)
# and the matrix read the row as ANOMALY, not a catch (job 697; the fault
# predates R-30, whose memfn_sites.c hunk is in pcrec_memfn_art). The plant
# now keeps each term's own class test but reads it at position 0's byte
# (`+ T]` rewritten to `+ 0]` in a copy of member[T], T < 10): the hook still
# forgets its term, every bitmap is still referenced, and at W = 1 the hook
# is unchanged (as before). A reordering plant would not do: the members
# carry their own offsets, so a permuted conjunction is the same test.
SAB_ID="S678-m6-adv-member-ignores-term"
SAB_FILE="src/gen/memfn_sites.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/possessify/possessify.rxt"
SAB_DESC='pcrec'"'"'s ADVANCE member hook (adv_member) ignores the term index again and hands the kit each position'"'"'s class test read at position 0'"'"'s byte, so the VM'"'"'s strided span loop tests the first byte W times'
SAB_DOC_FIGURE="MEASURED by lane sp1gfix 2026-11-03 (the planted tree built from this row's plant, harness run on tests/possessify/possessify.rxt at PROCS=2, outside the matrix runner): 55 failed / 3598 passed, 0 pattern-compile failures, no -Werror: the re-plant is warning-clean (the suitetri 2026-10-27 class-A listing of this row predates it). The matrix trailer is the gate shard's. Before it, HAND-MEASURED by lane m6 2026-10-08 (plant applied, tree rebuilt; docs/dev/lanes/m6_report.md section 6): harness tests/possessify/possessify.rxt 20 failed / 3517 passed ((?:a\.)+\b on \"aa.a.\" answers (0,2) not (1,3); (?:a[a.])+\b fails to compile, its position-1 class bitmap unused); over the whole corpus every failing cell is in possessify.rxt. memfnarms cannot see it (the kit pastes the hook opaque). The matrix figure is owed at the slot."
SAB_REACH='"$PCREC" -p rx --engine=vm -o - --pattern "(?:ab)+c"'
SAB_REACH_EXPECT='while ((rx_span_cursor + 2 <= subject_length) && (subject[rx_span_cursor + 0] == 97) && (subject[rx_span_cursor + 1] == 98)) {'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return term < (uint32_t)a->stride ? a->member[term] : NULL;'
SAB_AFTER='    if (term >= (uint32_t)a->stride) return NULL;   /* SABOTAGE S678 */
    char key[24];
    snprintf(key, sizeof key, "+ %u]", (unsigned)term);
    size_t n = strlen(a->member[term]);
    char *t = pcrec_arena_alloc(&((const PcrecMfU *)u)->cx->arena, n + 1);
    memcpy(t, a->member[term], n + 1);
    for (char *q = t; term && term < 10 && (q = strstr(q, key)) != NULL; q += 3) q[2] = 48;
    return t;'
