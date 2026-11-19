# process.md — round predspec24 (coordinator, opus), DESIGN
- 14:30 freeze: SUBJECT docs/design/predicates_draft.md rev 24 @ 4e4389ab3 (merged 092e0fd1a); build tree main HEAD f7111da43 (draft blob identical).
  RULINGS at freeze: COND-FAMILY.md @ HEAD f7111da43 (8 lines newer than the subject: the rx-module ADDENDUM ~14:55; hand mapping below);
  predicates_future.md, decisions.md, plan.md @ f7111da43. decisions.md unchanged since subject; plan.md changed only [ARCH-STEP] (unrelated).
- FREEZE DRIFT at freeze (already present): CF ADDENDUM rx-module (~14:55): reopens §2.5's 2026-11-13 lean against a concatenation operator; idea of quantifier operators.
  HAND MAPPING: rev 24 does not rule rx-module (R.8 row "FILED (item 21)"); §2.5 lean: affected only as a pointer (§2.5 should name item 21 as reopening it). No finding of rev 24's §R moves.
- Round dir created empty (absent before). R/subject + R/tree read-only (chmod a-w). Evidence predspec24_model.py re-run from R/tree: 37 s, 166 MB, byte-identical to the committed .out; writes stdout only.
- Setup lesson from r34 applied: two setup calls blocked by the no_cd_worktree hook (a trailing cd / a cd in a compound); both re-run without it and their results checked.
- Fix-induced coordinator step: r34 verify.md numbers extracted (passed to fixinduced as numbers only).
- Profile: re-check of a revised design + a definition replacing a foundation + rulings relied on (manager readings handed to the round) + an evidence engine with tables/counts + a marked-sections change table (G24-1).
- Lenses (5): ruling (opus; + goals/owner criteria folded; the ONE quote-verifying lens; next-revision ruling table; hand mapping of the post-subject CF addendum),
  modeclosure (opus; + standing questions sibling-of-family and general form + unlocks), simulate (opus; from-the-text evaluator, engine header readings, swap/domain drills),
  fixinduced (opus; kept text still true under rev 24; r34 verifier numbers diffed), changetab (sonnet; G24-1 grep + §R.9 marks list vs marks present).
- 14:34 launched 5 critics (4 opus, 1 sonnet), background, unnamed; ALL returned in the launch turn (each harness note: "ended without SubagentHandback"; files complete, CRITIC COMPLETE, lanecheck .done x5). Durations: changetab 3.6 min, fixinduced 7.2, ruling 8.5, modeclosure 9.9, simulate 13.2. No resends, nudges or stalls.
- Raised: ruling 14, modeclosure 10, simulate 9 (1 SUSPECTED), fixinduced 9, changetab 6 = 48.
- 14:47 rulings re-diff: COND-FAMILY / predicates_future unchanged since freeze; decisions.md +1 line (D-row addendum on module vs layer seams, [ARCH-STEP]; unrelated to the subject: no mapping needed).
- Overlaps: W1c carry (MC-1, SIM-1); join-order stake (MC-2, SIM-2, FI-3, FI-4); hits searched re-split (MC-4, SIM-3; RULING-6/9 on hits); atomic monotonicity (MC-3, SIM-5; RULING-2; MC-6 SP2); spelling principle (MC-6, SIM-6); §4.4 (FI-8, CT-2); L61 (FI-1, CT-5); polarity (CT-1, FI-6, FI-7, RULING-9).
- 14:48 verifier (opus) launched; returned in the launch turn, 8.2 min, 10 grouped items: V1, V3, V6, V10 HOLD; V5 HOLDS (one text answer corrected); V8 HOLDS x12 (two corrections); V2, V4, V7, V9 PARTLY. REFUTED sub-claims: FIXINDUCED-3 grouping half; RULING-3 third narrowing; RULING-8 "different shape" half; CHANGETAB-5 "example does not move". Each REFUTED rests on a run/quote in verify.md; spot-checked by reading (quotes cited with CF lines), not re-run by me.
- 14:57-15:05 draft review.md; critic texts, scripts, verify.md, COMMON copied into review/. No review worktree was created (design mode), nothing to prune. Total wall ~35 min from freeze to draft.
- Per lens raised / verified: ruling 14 / 12 held (2 partly); modeclosure 10 / 10; simulate 9 / 8 (+1 suspected skipped); fixinduced 9 / 8 (+1 partly); changetab 6 / 6 (1 corrected).
- Blinding: no leaks noticed; critics used R/subject + R/tree only (no critic reported repo access beyond git show).

## Process observations
- Five critics on narrow one-question briefs, all returning in the launch turn (3.6-13.2 min), with the read-only R/subject + R/tree and a pre-run engine: no tool-building, no resends. The pattern holds at five lenses.
- The two answer-level discoveries that matter most (A1 carried optional label, A3 `&` in subject context) came from critics writing their OWN evaluator / PCRE2 probe before trusting the engine; the evidence's 20 PART C models were all top-level and set-every-path, so they could not see either. The lens table has no explicit "capture state" drill.
- The fix-induced coordinator step (r34 verifier numbers) was cheap (5 min) and produced C5; worth keeping.
- The harness reports every nested agent as "ended without SubagentHandback"; the files were complete each time: files-as-delivery remains the only reliable channel.
- Two setup Bash calls were blocked by the no_cd_worktree hook (a `cd` in a compound command; a trailing cd); r34's lesson caught them because every setup result was checked.

## Proposed changes
- Skill §4 simulate lens, append: "where the design claims a regex model or an independent PCRE2 control for an operator that matches an operand 'whole on the stretch', drill the operand with `$`, `\b` and a lookahead: an engine (and a lookahead-based model) that walks the SUBJECT passes every anchor-free check (2026-11-17 predspec24 A3: the LAW failed inside the engine, 1,344 of 1,365)."
- Skill §4 mode closure lens, append: "add a CAPTURE-STATE drill to every regex-model claim: an OPTIONAL label inside a looped place, a label looped at two depths read from outside, and a place inside a place (atomic or a hole loop inside `occurrences`); top-level models whose items set every label on every path cannot see carry-over (2026-11-17 predspec24 A1/A2: 5/34, 300, 693 differ)."
- Skill §4 simulate lens, append: "when the evidence prints '(labels compared)', check each MODE's comparison key: a WHOLE key that is a bool compares holding only (predspec24 A5: 0 printed, 117 real)."
- COMMON template: name the evidence's ORDER/SWAP switch and ask whether it can fail (predspec24 C1).

## Framework notes
- Coordinator pattern at five critics + one verifier: ~35 min wall from freeze to draft, every agent delivering in its launch turn; the coordinator's context stayed small because every result travelled as a file and the verifier grouped 48 ids into 10 items. Good fit for "re-check of a design with an executable evidence engine"; the cost driver is the verifier's re-runs, not the critics.
