# process — round covs2e (design re-check)

- 20:38 freeze: subject 342ae6586 (rev 5.1), BUILD main e0c4c3816, rulings frozen there; round dir absent (OK).
- Reuse check: src/lib/cli/memfn/tests diff b9b9e8635..e0c4c3816 empty, BUT crit-covs2d's review worktree had been
  pruned (no build/pcrec). Rebuilt once: worktrees/crit-covs2e, `nice make -C ... -j2`, rc 0, about 3 min. Kit
  scripts (emit/facts/ans/oracle) reused, repointed by sed; sanity-run 3 known rows (a{40}(?:b|cc) 41; [0-9a-f]{32}
  cover OK vs libpcre2; {33} unanchored).
- Hook friction: two Bash calls blocked by no_cd_worktree.sh (a `cd` chained before commands); `make -C` instead.
- 20:40 launched 3 opus critics (fixinduced, readyA, readyB), background, unnamed. All returned IN the launch turn
  (11 / 11 / 6 min), each with findings file complete and lanecheck .done. Their final replies were not delivered
  ("ended without SubagentHandback"); files carried everything (as the skill expects).
- Findings: fixinduced 11, readyA 9, readyB 8 = 28 raw -> 20 consolidated + DRIFT-1. Overlaps: 5 clusters (FIND-1,
  -2, -3, -4, -5), two found by two lenses each independently, FIND-4 by all three.
- Verification inline (all quote claims + one sizeof probe); no verifier agent. 0 REFUTED.
- FREEZE DRIFT: D198 addendum 1 landed on main mid-round (owner settles the route lean). Hand-mapped; no fresh critic.
- Draft at 20:55; total about 17 minutes wall.

## Process observations
- Three opus critics at 6-11 minutes each for a 1,300-line subject with a ~550-line revision: right size. Two
  per-unit readiness critics plus fix-induced produced 5 overlap clusters: overlap is high (25% of raw findings), but
  each overlap came with different evidence (e.g. FIND-2: fixinduced saw the facts row; readyA added S3220, S3223's
  REACH and reach.sh).
- "Reuse the previous round's build" needs the worktree to still exist; the previous coordinator pruned it (as §6.4
  says). The reuse rule saved only the kit scripts, not the build.
- The fix-induced lens ran 0 compiles and still found the procedure contradictions (FIND-7, -8) by drilling text:
  the simulate-style drill instruction inside fix-induced's brief (F17/F19) paid.

## Proposed changes
1. Skill §5 (reuse clause): "REUSE that round's kit and trace compiler" add: "if its review worktree was pruned (§6.4
   prunes it), reuse the kit scripts and rebuild the tree once; 3 minutes at -j2 (2026-11-15 covs2e)". Motivation:
   the reuse premise silently failed here.
2. Lens table, readiness row, add: "re-run the design's own reader-finding greps and diff their output against the
   design's hit lists (2026-11-15 covs2e: the subject's own greps printed S526, S3223 and three span writers its
   lists dropped)".
3. Lens table, fix-induced row, add: "a claim that witnesses 'move with X by construction' is drilled per row KIND
   (verdict, facts, answer, mech REACH) at X's extreme admissible values (covs2e FIND-2)".

## Framework notes
- The coordinator pattern handled a mid-round ruling cheaply: one `git diff` of decisions.md at hand-back found
  D198 addendum 1, and the hand mapping took one paragraph. Without the freeze-drift step the draft would have
  carried a stale "owner question open".
- Nested critics' final replies were again lost; the files-plus-lanecheck contract made it irrelevant.
