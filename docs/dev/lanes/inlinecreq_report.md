# inlinecreq report — [INLINE-C] requirements (lane inlinecreq, sonnet, 2026-10-26)

Deliverable: `docs/design/inline_c_requirements.md` (rev 0, requirements only,
no build go, no src/cli/lib/memfn/tests touched, no make run). Branch
`lane/inlinecreq`; commit 912ebf9f0 (note + its line in docs/design/CLAUDE.md).

## Summary

- Premise test TRUE (`requires module 'callouts'`). STOP RULE did not fire:
  libpcre2 10.46 (probe linked to -lpcre2-8, in the worktree's gitignored
  build/probe/) accepts `(?C{...})`.
- Facts measured that change the proposal:
  1. PCRE2's `{...}` string ends at the first single `}`; a literal `}` must be
     `}}` (valid PCRE2 needs doubled braces in C code; a C-aware lexer would
     make the pattern invalid PCRE2). Other delimiters (`$`, `#`, `` ` ``, `^`,
     `%`, `'`, `"`) are valid; `(` is refused. Recommendation: PCRE2's rule on the
     pattern side, a C-aware rule on the template side (`${{`/`${(` are refused by
     PCRE2's grammar and by pcrec today; libpcre2's own refusal of them is not yet
     probed).
  2. The SAME pattern and predicate gives different ANSWERS under PCRE2's own
     flags: `(\d+)(?C{p})` on `1234` (fail when > 255) is `[1,4)` by default and
     `[0,3)` with NO_AUTO_POSSESS|NO_START_OPTIMIZE. Fire counts are
     engine-relative (counting callouts over-count by construction).
  3. A negative callout return abandons the whole search (later starts
     included) and `pcre2_match` returns that value; a positive one fails only
     the path. D38 ruled native abort NONE in v1: a requirement to settle.
  4. `rx_ctx` has no match-start field (PCRE2 gives `start_match`); an abi
     question.
  5. The template is compiled independently of the regex (subst_api.md §3), so
     C in a template cannot know group numbers at compile time: the template
     side's one hard problem (R-T3). The `rx_renderfn` sizing pass would run a
     side-effecting segment twice (R-T5).
- Post-match predicate analysis (section 4): equivalent when the callout is a
  pure predicate, its inputs are the same in both modes (tail position, or a
  recorded snapshot), and the candidate is unique at its start (the same fact the
  compound's unique-end admission already computes). Differs on any veto that
  must steer backtracking (worked examples D1-D3, from probes). Rejection
  semantics: reject-and-resume-at-s+1 (equivalent only where proven; refuse
  otherwise) versus optimistic DFA with VM fallback on a veto (always
  equivalent for pure predicates; recommended first). Template side: confirmed
  needs no VM.
- 20 draft usage tests (UNBUILT) across UC-1 IP octet, UC-2 template
  lookup/+1/hex decode, UC-3 user header and source (where `#include` goes: .c
  only, never .h; pcrec never opens the header), UC-4 counting/collecting, plus
  seven casual-user traps. Prior art is from knowledge, not re-fetched (stated in
  the note); the "first PCRE-compatible compiler with inline C" claim is
  unverified and the note says how it is falsified.

## Open questions for Frank (the note's section 8 has the full text)

1. One feature or two? Recommend split: template side first (no engine impact),
   pattern side after [M4-CALLOUTS]'s named binding.
2. Inline C as a second spelling of the planned named-callout call site, not a
   parallel mechanism? Recommend yes.
3. Brace rule: PCRE2's `}}` on the pattern side (valid PCRE2 kept), C-aware on
   the template side. Recommend yes.
4. Post-match mode: build `verify` (optimistic DFA, VM on veto) first; flag per
   pattern or per callout?
5. Where does the opt-in live? Recommend CLI-only `--allow-inline-c`; a file
   cannot grant itself.
6. Return convention: PCRE2's (0/positive/negative) for inline segments;
   decide abort (D38 says none in v1) first.
7. Sugar: generated macros and named-group constants only, no `$1` text
   rewriting in C.
8. Use the "first PCRE-compatible compiler with inline C" claim? Not until the
   survey is re-run with the web.

## Not done / limits

- No web survey (prior-art table from knowledge; flagged owed).
- `pcre2_substitute` on `${{`/`${(` not probed.
- The note names no D/K/I ids; abi movers are unnumbered and uncounted by
  design (the later design counts them by grep).

## STATE AT HANDOFF

Rulings file read at both checkpoints: it held "(none yet)"; no entry applied.
Branch lane/inlinecreq at commit 912ebf9f0 plus the report commit; worktree
clean after it; nothing pushed, nothing merged. Probe sources and binaries
are in the gitignored build/probe/ of this worktree (removable with wtprune).
