# crit-stream2 process record (coordinator)

- 17:24 freeze: subject approach.md rev 2 @ 44c512807 (branch head e66e89564), sha256 492209b1...; copies
  in subject/. Build-landing = main 8e846f501; no src/cli/lib/memfn change since f574eab2d (the
  subject's cited base). Review tree worktrees/crit-stream2, nice make -j2 unlocked, rc 0 (~1 min).
- 17:26 COMMON written; 17:26 launched 4 critics, all opus, background, unnamed:
  FIXIND (fix-induced), SOUND (soundness), CARD (plan-time card + slot tracing + ruling check +
  sibling/general form), OWNER (owner criteria + goals).
- All four returned IN THE LAUNCH TURN with "ended without SubagentHandback" (no reply text). Files and
  lanecheck .done markers carried everything: OWNER 17:32, CARD 17:33, SOUND 17:35, FIXIND 17:38. No
  resends, no nudges.
- Findings raised: FIXIND 12 (all CONFIRMED), SOUND 10 (8 CONFIRMED, 2 SUSPECTED), CARD 10 (7 CONFIRMED,
  3 SUSPECTED), OWNER 7 (6 CONFIRMED, 1 SUSPECTED). Overlap: SOUND-5 = FIXIND-1 (Nfa.erased vs \K/\G;
  OPPOSITE fix shapes: SOUND adds bits, FIXIND keeps the record language-only); FIXIND-6 / CARD-1 /
  CARD-8 touch the profitability column; FIXIND-7 = CARD-4 (give-up vocabulary); FIXIND-3 / CARD-8
  (row 5's sound/profit split); FIXIND-10 / CARD-3 partially.
- Blinding: CARD copied lane/p1build's whole plan.md (382 KB) into its lens dir (card/plan_p1.md)
  instead of reading by tag; no denied p1build row is known for this round, so no leak, but it is the
  "never print neighbours" shape. Both pcre2 notes appeared at 17:26/17:28; FIXIND used
  backref-referent-choice.md.
- 17:40 verifier (opus) launched over 33 CONFIRMED ids; returned in launch turn, no handback; verify.md
  complete 17:51 (VERIFY COMPLETE, .done): 23 HOLDS, 10 PARTLY, 0 REFUTED (one sub-claim refuted in
  FIXIND-11). Adjudicated SOUND-5 vs FIXIND-1: FIXIND's fix for \K/\G, SOUND's for superset lowerings.
- 17:55 draft review.md; critic texts + verify.md + COMMON copied to review/; freeze re-checked OK;
  review worktree removed via wtprune --force --quiet-min 1.
- Per lens: FIXIND 12 raised (9/4 HOLDS/PARTLY counting -6 in both), severity: 1 answer, 4 bytes/stamp/
  give-up, rest design/doc. SOUND 10 (4 answer HOLDS + 1 design HOLDS + 1 doc HOLDS, 2 PARTLY, 2
  suspected). CARD 10 (5 HOLDS, 2 PARTLY, 3 suspected). OWNER 7 (4 HOLDS, 2 PARTLY, 1 suspected).
- Time: ~31 min freeze to draft.

## Process observations
- Every agent ended in its launch turn without a handback, as in round 1. The file + lanecheck
  pattern is the only channel that works and it worked without one resend.
- Two lenses saw the same fact and proposed OPPOSITE fixes (SOUND-5/FIXIND-1). Without the verifier's
  explicit "say which fix is right" clause the draft would have had to pick blind. Worth keeping.
- The fix-induced lens produced the largest and most launcher-relevant set (bytes/stamps moved by
  fixes), but also an answer finding (FIXIND-12) that the soundness lens's PROBED-AND-HELD missed
  (it probed the backref in the other direction). Overlap between fix-induced and soundness is
  useful on an answer-identity re-check.
- CARD copied the whole lane/p1build plan.md into its dir rather than grepping the tag: no denied row
  this round, but the shape the skill forbids for denied rows.
- The owner-criteria lens's replay of real merges (OWNER-1) found what text reading could not.

## Proposed changes
1. Lens table, fix-induced row, append: "When a fix names an existing record or field as a fact's
   HOME, quote that owner's definition and trace every reader: a fact outside the definition moves
   every reader (2026-11-01 r2 stream2: `\K`/`\G` into `Nfa.erased` flips today's exact windows)."
2. Lens table, owner-criteria row, append: "Replay 2-3 real past changes through each measurable form
   the subject states (r2 stream2: 3 of 3 row-adding merges failed F1's change-set check)."
3. Verifier brief template (section 6.2): "where two findings share an observation with different
   fixes, say which fix is right and why" (r2 stream2 SOUND-5/FIXIND-1).
4. COMMON template: "read plan.md rows by tag; never copy plan.md whole into your dir".

## Framework notes
- Two consecutive rounds on one subject: the coordinator pattern carried a re-check cheaply (one
  coordinator context, ~31 min, five agents) and stayed blind (no known findings from the manager;
  only the previous review as allowed input). A re-check's lenses differ from the first round's
  (fix-induced + card instead of premise + cost), which the per-subject lens table supported.
- The verifier as adjudicator of conflicting fixes is a role the framework did not name; it fits.
