# dd11set report (survey, 2026-10-18)

Lane dd11set, sonnet, worktree `worktrees/lostset`, branch `lane/lostset`. Survey and report only; no src, no plan.md
edit, no builds. Deliverable: `docs/dev/dd11_family_2026-10-18.md` (full evidence).

[DD-11.5] in five lines:
1. Sets and tags are wired (UCP U1; three production callers of `pcrec_def_resolve*` consume only DEFK_SET or the tag); NO text entry (`$`, `\Z`, `(?m)^`, `(?m)$`, `\b`) is consumed by compilation.
2. Gate M6.6 is met; the "exact one-byte lookbehind" gate is met only for single-character-language lookarounds (A_CTX, U2); everything else is still `A_LOOK` erased to `N_EPS` in the DFA; [ENG-LOOK] is unbuilt.
3. Of the four assertion entries only `(?m)$` is exact today; `(?m)^` (the `(?!\z)` conjunct) and `$`/`\Z` are not.
4. `\b`/`\B` took the node route (A_CTX built directly), superseding the substitute-text premise; S3's stamp precondition is owed as a check and changes shape for A_CTX.
5. Frank's `\b` next-character fold is a general prev x next FIRST-set fold over A_CTX; it is the same mechanism that would make `(?m)^` exact, and it must be framed generally to honour [ENG-LOOK]'s no-one-character-fold ruling.

Dispositions (proposals): [DD-11.5] REVIEW-FIRST then COMPLETE re-scoped; [DD-11.6] (no plan row) FOLD into the review, then CLEAR; literal escapes CLEAR (8 of 9 rows, the ninth is conditional by design); UCP second-predicate rows CLEAR (shipped); encoding `\N{U+}` oracle probe small COMPLETE if the options pin allows; NEWLINE_CONV CLEAR; LIB_NAME_BOUND FOLD into [LIB]; cls_bits.inc-derived REVIEW-FIRST question; kit_proof Q3/UL-6/UL-8 REVIEW-FIRST jointly; [ENG-LOOK] status line.

Not verified: no runtime tests; `lang_charset` declining `A_END` read from source.
