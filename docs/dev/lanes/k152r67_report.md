# k152r67 report — review r67's K152 fixes

## Summary
Applied F1-F10 of docs/dev/reviews/2026-11-21-r67-k152.md on lane/k152r67 (cut from lane/k152fix 62752e60c). No src behaviour change: only comments in src/ir/nfa.c and a limits.def text figure, so no emitted-byte mover and no abi event. PREMISE TEST: `python3 -I scripts/m6read_check_sab_anchors.py` on the base listed STALE ANCHORS: 3 (S1100, S14, S1176); it now reads "all anchors resolve".

## Anchors
F1: S1100 and S14 re-anchored with one indent level less (12 to 8 spaces); S1176's anchor is the 4-space text, which matches both nfa_ctx sites as a substring (SAB_COUNT 2 kept). Each row run alone on committed HEAD: S1100 DETECTED (memfnfinder 3 fail / 28910 pass), S14 DETECTED (trie 2 fail / 5 pass), S1176 DETECTED (corpus 4365 fail, assertions 2 fail). Logs under $PCREC_TMPDIR/scratch/k152r67/.

## Limits doc
F2-F5: limits.md §3.10¶3 restated: worst 319,504 B (`^(abcdefghijklmnopqrstuvwxyz|abcdefghijklmnopqrstuvwxy_(…abe)*)*|b$`; 318,032 with short atoms), `+`/`{2}` refusal 190,224 B, search-code figures re-measured on this box (a 36,864 / abc 38,448 / (a) 40,848 / engine 2 about 41 KB), ¶4's lookahead item spelled with `d`. limits.def: 1.38x, 319,504 bytes. Two new DEPTH_FAMILIES rows in tests/thread/run_compile_stack.sh, `capwrap` and `longwrap` (measured: 318,032 and 319,504 at depth 250, gcc 15.2.0 Ubuntu 15.2.0-16ubuntu1, both refused at 251). NOTE: the review called the capturing shape "the compound route", but a stamp check shows it does not take the compound route (my first attempt put it under the compound reach check and it failed), so the rows are named `*wrap` and are not in the reach loop; the text says "wrapper alternative". Also one clause on K152 in known_issues.md.

## Comments
F6: DEPTH_FAMILIES comment says nclitrep/litpost/nclitpost were green at BASE and litcompound is the undo witness. F8: trie_key's header names the mark's second use; the group comment says the leaves are kept out of the dispatcher's frame; nfa_cat's "these three arms" says ten functions carry the mark; "moved verbatim" now says one indent level out, whitespace only, except nfa_cat's merge. Process change: one clause in .claude/skills/pcrec-critic/SKILL.md's check-adequacy lens (moves/re-indents).

## Plan rows
F7 and F10: a Note on [LINT-FRAME] (frame census makes a partial undo visible; vm_rev_emit's shape, trigger a lookbehind depth row over 70% of the budget). F9: new row [STACKDRIVER-ENC] (Backlog, not-started, trigger the growth runner or the next utf8 depth finding). [K152-NFA-DEPTH]'s status line no longer says litpost is the worst. plan_lint tree scan: 0 violations.

## Validation dispatched
Local: test-stackdepth green (78 passed, 0 failed, 75 records); anchor check clean; three rows DETECTED; plan_lint 0. Cloud `make test` on the tip: see STATE AT HANDOFF.

## STATE AT HANDOFF
Last R-n applied: none (the rulings file was empty). Cloud run name k152r67-test OWED, ref the tip sha in the lane's final message; verdict via monread/queuewatch.
OWED: none (the cloud make test, run k152r67-test, branch cloud/main/test/k152r67-test at 9ed03afe6, is dispatched; its verdict arrives via queuewatch).
