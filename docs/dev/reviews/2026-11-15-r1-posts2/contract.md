# contract findings

## Findings

### CONTRACT-1 — `rr_alt_rows` scan has no bound; a row after the catch-all is silently dead, an arm on the catch-all reads past the array
CONFIRMED by reading (no plant run). Severity: maintenance (latent answer/UB). Effort: 3 lines. Blast radius: src/facts/req.c only.
src/facts/req.c:633-648. `rr_alt` loops `for (i = 0; (rr_alt_rows[i].arm & w->restored) || !rr_alt_rows[i].row(...); i++)` with no `i < N`.
(1) A later row appended after `{ rr_alt_affix, 0 }` (e.g. stage 2a's next rule, or `look`) is unreachable: affix returns true unconditionally, so the new row never fires and nothing reds (no check counts the table's reachable rows).
(2) If anyone gives the catch-all a nonzero arm (or reorders it before a restorable row) and that arm is restored, the loop runs off the end of a 2-element static array (UB, not a refusal).
The table's own comment ("the last row matches every alternation and is never restored") is the only guard. The SIBLING `rb_rep_row` (req.c:983-990) already uses the bounded idiom (`while (i < last && ...)`, comment "the scan stops there whatever the table above it holds"); `rn_better` bounds by sizeof; `rb_zero_into` (req.c:1074) shares rr_alt's unbounded idiom. Proposal: copy rb_rep_row's `last` bound into rr_alt (and rb_zero_into), so the catch-all is enforced by the loop, not the comment. Expected after a hypothetical appended row: still dead, but no UB; a `/* rows after the catch-all are unreachable */` note or a codegen ST grep (last row's arm == 0) would make (1) visible.

### CONTRACT-2 — §2.28¶4 / §2.39¶1 example `frank|fred` -> `fr[ae]` is not what the compiler lists (pre-existing, in the paragraph rule (1) interacts with)
CONFIRMED. Severity: doc (D80 spec-vs-behaviour). Effort: two words. Blast radius: docs/spec/tuning.md §2.28¶4 (last sentence) and §2.39¶1.
Spec: "An alternation's common prefix and suffix are, position by position, the UNION of both branches' positions, stopping at the first position whose union has more than 128 members: `frank|fred` reports `fr[ae]`" (¶4); §2.39¶1 "(`frank|fred` to `fr[ae]`)".
Observed (SUBJECT and BASE alike, default and `-fno-altcls-merge -fno-altcls-factor`): `build/pcrec --emit-facts --pattern 'frank|fred'` -> `req_whole_run ... 6672[6165][646e] rate:builtin-prior`, i.e. `fr[ae][dn]` (the common head runs to the shorter branch's end, 4 positions). Not introduced by 13f46ea50 (BASE text and listing identical) but it is the ¶4 sentence the new ¶3 exception leans on. Proposal: `fr[ae][dn]`.

### CONTRACT-3 — §2.28¶3's new examples use a second set notation (`A{G,I,K,R}{A,D,I,P}A`, `{a,b}`) beside ¶4's `[cd][ao][tg]` and the listing's `[47494b52]`
CONFIRMED (text). Severity: doc. Effort: trivial. tuning.md §2.28¶3 vs ¶4 (same section), facts_listing.md value column.
Values themselves agree with the code: `AKIA|AGPA|AIDA|AROA` -> `41[47494b52][44494f50]41`, `((a)|b){3}c` -> `[6162][6162][6162]63`, `-+(?:(?=a)|)A` (needs `--features all`) -> `2d41`, `xy(?:ab|abc)zw` -> `78796162`. Only the spelling differs; ¶4 already writes positions as `[..]`. Proposal: `A[GIKR][ADIP]A`, `[ab][ab][ab]c`. Same `{..}` spelling is in docs/dev/history/abi_changelog.md (history, leave) and run_facts_checks.sh's comment (`{c,d}{a,o}{t,g}`).

### CONTRACT-4 — the restore-arm population is hand-listed in five places and no check enumerates walk_arms.def against them (family; rule (1) is the 5th arm)
SUSPECTED gap, CONFIRMED current state correct. Severity: maintenance/design. Effort: small check. Blast radius: tests/axes/run_axes.sh, facts_listing.md §4.1.3¶4a, cli/CLAUDE.md, run_lever_fence.sh comment, req.c tables.
r1on added `alt` by hand to `INTERNAL_ARMS` (run_axes.sh:1779-1781), to ¶4a's arm list, to cli/CLAUDE.md and the fence comment; all present today. But `git grep walk_arms.def -- tests scripts` finds only comments: nothing reds if a future arm (`look`, named in walk_arms.def's own comment) is added to walk_arms.def and a row table but not to INTERNAL_ARMS — the answer-identity sweep would then silently never run that arm (learnings §3 / K35, a population nobody counts). Confirm by: plant a 6th WALK_ARM without touching run_axes.sh; expect green. Proposal: run_axes.sh derives INTERNAL_ARMS' restore entries from walk_arms.def (or a 1-line codegen ST check comparing the two lists).

## PROBED-AND-HELD

(a) spec vs behaviour, SUBJECT build, pair.sh BASE/SUBJECT, ~170 compiles:
- Every ¶3 example (4) holds, default and altcls-denied; ¶4 `cat|dog`, `Q(?:ab){20}Z` (= its written-out literal, 32-pos run ending `5a`) hold; only `frank|fred` misses (CONTRACT-2).
- 26 byte + 5 utf8 + 3 `-fno-req-run-fold` admitted-class probes: repeats {2},*,?; caseless; `\K`, `$`, callout, lookahead, empty and zero-width branches; 3-/4-way and mixed-width alternations; atomic; backref and call branches (break, affix kept); store-truncated branches (`a{40}|b{40}`, affix, same 32-pos run); union >128 members (falls to affix; same result as ¶4's "breaks contiguity" reading, checked on 3 shapes); utf8 equal-byte-width across scripts (`α|ab` -> `78[61ce][62b1]79`) and unequal (`é|e`, affix). Under -fno-req-run-fold only single-member unions join (`xy(?:ab|ab)zw` whole), matching §2.39¶1.
- Answers: 6 patterns x 3-5 subjects, BASE = SUBJECT = libpcre2 (spans).
- Identity: SUBJECT `--harness=restore=alt` vs BASE, 10 mover patterns: gen.c differs only in the 2 abi lines; listings differ only by the `harness:alt` token.
- ¶4a token: on req_whole_run, req_pieces, req_byte, req_landmark_maxoff, run_pin for movers and non-movers; absent under build/pcrec (option refused); `deny:` facts keep their own reason (-fno-req-run, -fno-req-byte); combined arms list `tie+alt`.
(b) readers: abi 107 at emit_dfa.c:55 (sole constant, 4 emission uses), generated .h guard (3 lines) and provenance/.abi, match_api.md §1 (3) + §6 table + ¶17, run_codegen_tests.sh ABI_EXPECT, S693 BEFORE 107/AFTER 106, abi_changelog top entry, recursion-identity pins re-pinned. Remaining `106` mentions are dated history comments (correct). `alt-union-run`/`alt_union` removed from main.c, internal.h (bit not reused, comment kept), facts_derive.h, facts.c, req.c; remaining mentions are history (lane evidence, rps3b census.py not called by any test/Makefile), the row's concept name (S3129, memfn_arm.py) and plan/changelog text. No reader left on the old value; none moved wrongly.

## Standing questions
(1) Family: rr_alt_rows is the 4th `{row, arm}` first-match restore table in req.c (rn_choice_rows, rb_rep_rows, rb_zero_rows) with three scan idioms (sizeof-bounded, `last`-bounded, unbounded x2). Unify into one bounded scan helper with an enforced arm-0 catch-all (fixes CONTRACT-1 for rb_zero too); the arm population likewise wants one source (CONTRACT-4). Trigger: now cheap; at the latest the L1 `look` arm.
(2) General form: an alternation's value as a set of per-WIDTH runs (the req_pieces domain already lists `6:[..]|7:[..]`); rule (1) is the one-width-class case collapsing to a whole run. Unlock: unequal-width alternations keep head and tail across a bounded gap (`xyab.{0,1}zw`) for a gapped pre-check, and a generated not-restored sabotage row per table row instead of hand rows (S1921/S1930/S3131). Trigger: a mover census showing unequal-width alternations losing a run below PCREC_MIN_REQ_RUN_BITS or a rarer byte on the corpus/bench.
