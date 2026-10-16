#!/usr/bin/env bash
# S1069 ([COMPOUND] E0c, lane e0c; docs/design/compound_entries.md §4.1, §5.1 E0c; docs/dev/lanes/e0c_report.md) -- the forward emitter's INERT binding (the DFA's `_in` entries) answers -1 from `<prefix>_match_in` instead of forwarding to `<prefix>_match`.
SAB_ID='S1069-e0c-forward-inert-match-in-nomatch'
SAB_FILE='src/gen/emit_comb.c'
SAB_SUITES='framebuffer'
SAB_DESC='a DFA artifact'"'"'s <prefix>_match_in returns -1 without calling its un-suffixed sibling, so the inert forward is no longer that sibling (spec §10.4); the old emit_in_entry_defs text is gone, so the forward emitter is the only path that can write it'
SAB_DOC_FIGURE='HAND-MEASURED by lane e0c 2026-10-16 (plant applied to a git-archive HEAD tree, run_frame_buffer.sh): framebuf 2fail/5pass -- the alt-trie and anchored DFA rows diverge, rx_match_in -1 vs rx_match 7/3. The harness on tests/recursion/framebuffer.rxt reads 0fail/16pass (its DFA cells never match AT startpos). The matrix figure is owed at the slot.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (bind == PCREC_FWD_INERT) {
        pcrec_sb_printf(c,
            "    (void)buffers;\n"
            "    return %s(%s%s);\n"
            "}\n",
            name, s->args, va);'
SAB_AFTER='    if (bind == PCREC_FWD_INERT) {
        pcrec_sb_printf(c,
            "    (void)buffers;\n"
            "    return %s%s(%s%s);\n"
            "}\n",
            s->entry == PCREC_ENTRY_MATCH ? "-1; (void)" : "", name, s->args, va);   /* SABOTAGE S1069 */'
