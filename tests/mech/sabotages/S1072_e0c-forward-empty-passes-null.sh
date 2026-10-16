#!/usr/bin/env bash
# S1072 ([COMPOUND] E0c, lane e0c; docs/design/compound_entries.md §4.1, §5.1 E0c; docs/dev/lanes/e0c_report.md) -- the forward emitter's EMPTY binding (the [CC-DIFF] forward rungs) passes a NULL descriptor to `_in` instead of the empty one.
SAB_ID='S1072-e0c-forward-empty-passes-null'
SAB_FILE='src/gen/emit_comb.c'
SAB_SUITES='harness'
SAB_DESC='on a forward-rung VM artifact the un-suffixed entry calls its _in sibling with NULL, which spec §10.3 defines as the un-suffixed call itself: the two recurse until the stack overflows'
SAB_DOC_FIGURE='HAND-MEASURED by lane e0c 2026-10-16 (plant applied to a git-archive HEAD tree): corpus (tests/vars/basic.rxt) 18fail/6pass. The matrix figure is owed at the slot.'
SAB_EXPECT=DETECTED
SAB_HARNESS_TARGET='tests/vars/basic.rxt'
# REACH: the vars witness takes the forward rung.
SAB_REACH='"$PCREC" -p rx --features all -o - --pattern "a\${v}b" | grep -c "_no_buffers);"'
SAB_REACH_EXPECT='3'
SAB_COUNT=1
SAB_BEFORE='            "    return %s_in(%s, &%s_no_buffers);\n"'
SAB_AFTER='            "    return %s_in(%s, 0 ? &%s_no_buffers : (void *)0);   /* SABOTAGE S1072 */\n"'
