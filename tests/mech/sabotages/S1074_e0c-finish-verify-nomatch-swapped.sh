#!/usr/bin/env bash
# S1074 ([COMPOUND] E0c, lane e0c; docs/design/compound_entries.md §4.1, §5.1 E0c; docs/dev/lanes/e0c_report.md) -- the finish-at emitter swaps its two own-body forms: the anchored machine's body where FINISH says nomatch, the nomatch body where it says verify-at.
SAB_ID='S1074-e0c-finish-verify-nomatch-swapped'
SAB_FILE='src/gen/emit_comb.c'
SAB_SUITES='anchoredmatch'
SAB_DESC='every unwrapped <prefix>_match answers -1 at once (the nomatch body) and an empty engine'"'"'s carries the anchored machine; the finish-at dispatch no longer follows the FINISH row'"'"'s action'
SAB_DOC_FIGURE='HAND-MEASURED by lane e0c 2026-10-16 (plant applied to a git-archive HEAD tree, run_anchored_match.sh): anchoredmatch 21fail/13pass -- the unwrapped witnesses carry the nomatch body and no anchored machine. The matrix figure is owed at the slot.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (f->form == PCREC_FIN_VERIFY) pcrec_emit_dfa_anchored_match(cx, c, g);'
SAB_AFTER='        if (f->form != PCREC_FIN_VERIFY) pcrec_emit_dfa_anchored_match(cx, c, g);   /* SABOTAGE S1074 */'
