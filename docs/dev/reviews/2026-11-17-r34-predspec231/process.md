# process.md — round predspec231 (coordinator, opus)
- Freeze 2026-11-17: subject predicates_draft.md blob 6acb64d8 (commit 82924825e; main HEAD f2070d701 same blob).
  COND-FAMILY.md blob ec72ef3f (commit 0cdcb524b); decisions.md 6ae67eab; plan.md b15291d3 (commit 85fba0d20);
  predicates_future.md ff6f8cc7.
- Round dir created empty. Evidence predspec23c re-run from read-only copy: 10.2 s, byte-identical.
- Lenses: fixinduced (+ruling folded), modeclosure (+ attack of manager readings, + family/unlocks), simulate. All opus.
+ 03:36 critics all complete in launch turn (~11-14 min each), files full, lanecheck DONE x3
- ~03:2x launch 3 critics (opus, background, unnamed); all returned in the launch turn: fixinduced 13.1 min, modeclosure 10.8 min, simulate 13.7 min; files complete, CRITIC COMPLETE, lanecheck DONE. No resends, nudges or stalls.
- Verifier (opus) 7.2 min, 8 grouped items: all HOLDS; 1 PARTLY, 1 sub-claim REFUTED, 1 witness withdrawn.
- DELIVERY GLITCH (mine): the Bash call that pre-created verify/verify.md was BLOCKED by the no_cd_worktree hook (a trailing `cd /dev/null` I appended); the verifier created its own file in the asked shape. Lesson: never end a setup command with a cd; check the setup call's result before launching.
- Blinding: no leaks noticed; critics worked only from R/subject and R/tree copies.
- Per lens raised: fixinduced 13 (1 sub-claim refuted), modeclosure 11, simulate 10 (1 witness withdrawn). Overlap: A2 found by all three; D2 by all three.
- Time to draft ~15 min after the verifier.

## Process observations
- Three opus critics with two sub-parts each, against a COMMON with read-only copies + a runnable tree, finished in 11-14 min with no tool-building: the R/subject + R/tree pattern keeps paying.
- Folding the ruling lens into fix-induced worked at this size (13 findings, quotes 0 drift), but the file was the longest; a 4th critic would have been justified if the record had more than ~3 new manager readings.
- The biggest answer-level finding (A1, value vs canonical numerals) was a CARRY-OVER: r33's verifier had the right number (281) and the fix lane published the engine's (371). Nothing in the process diffs a prior verifier's numbers against the revision.
## Proposed changes
- Skill §4 fix-induced lens, append: "On a re-check, diff every count the previous round's VERIFIER printed against the number the revision publishes; a mismatch is a finding (2026-11-17 predspec231 A1: r33's verifier printed 281, rev 23.1 published the engine's 371)."
- Skill §4 mode closure lens: name FIND-ALL places as a mode of their own beside WHOLE and SEARCHED top level (predspec231 A3: hold-equality true at the top, false in a find-all argument).
- Skill §4 ruling lens: a manager ruling stated as a DERIVATION is read literally everywhere its premise applies (predspec231 MODECLOSURE-4).
- Skill §5 coordinator setup: check every setup command's result before launching; a hook-blocked pre-create silently skips the file (this round).
## Framework notes
- Coordinator pattern at its smallest useful size (3 critics + verifier, ~40 min wall) still produced 4 answer-level items on a revision billed as applying fixes; the from-the-text evaluator with the document's own set rules remains the highest-yield single tool for design rounds with an evidence engine.
