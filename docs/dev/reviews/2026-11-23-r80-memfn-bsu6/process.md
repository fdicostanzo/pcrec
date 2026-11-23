# process.md: r80 memfn-bsu6 (code)
- 03:00 freeze: SUBJECT lane/bsu6t 715a17a58, BASE 9d796f4ec (= main HEAD). Rulings freeze: main decisions/plan at 69bbcafc7.
- Profile: no product code; measurement harness (timer, reader, CPU-quiet port, DRY), checks (c6selftest rows, dry guard,
  reader refusals), G1 population tool, rulings (abi no-bump; c6_rule.md clauses).
- 03:02 review tree built (nice -j2, ~1.5 min). 03:03 c6selftest 52/0 (0.4 s); one-pattern DRY 5 s; full DRY 49 s, 1008 exes.
- Lenses: fidelity (opus, harness fidelity + standing questions), rule (opus, measurement: code vs c6_rule.md
  clause by clause + estimator drills), checks (sonnet, check adequacy: mutation of cards.py copy; owns ALL plants),
  g1 (sonnet, G1 population contract + abi no-bump ruling check).
- Setup note: lanecheck prints "DONE rc=1" on an incomplete file; COMMON says end on "DONE rc=0".
- 03:05 four critics launched in one message (background, unnamed). All four RETURNED IN THE LAUNCH TURN with
  "ended without delivering a report" (expected nested-agent shape); files complete with CRITIC COMPLETE:
  g1 sonnet 3.4 min (7 findings), rule opus 6.4 min (5), fidelity opus 7.5 min (7), checks sonnet 15.6 min (10 + 62-mutant table).
  No resend, no nudge. No blinding leak noticed (no critic cited a denied file).
- Overlaps: FIDELITY-2 = CHECKS-3 (re-time pool wiring; two independent plants); FIDELITY-4 ~ CHECKS-1 (gate-fail path, two sides).
  The F-2 plant duplicated the checks lens's X9 despite COMMON assigning plants to checks: the fidelity brief's sub-part
  invited ONE plant. Mild duplication, but it gave an independent confirmation.
- 03:23 verification inline (verify.md): RULE-1 re-run via c6decide, F-1 re-run via the critic's lay.py, rest by reading.
- Freeze drift: none (main 9d796f4ec, rulings 69bbcafc7 unchanged at 03:22).
- 03:25 draft review.md; review worktree pruned. Time to draft ~25 min from freeze.

## Process observations
- Setup (build ~1.5 min, a full DRY to size the budget, a reference DRY record in kit/ref) let every critic start probing
  at once; the rule critic spent 0 compiles by editing records built in the subject's own format.
- lanecheck prints "DONE rc=1" on failure: "end on DONE" alone is ambiguous; COMMON said "DONE rc=0".
- The `no_cd_worktree` hook also matches `cd X &&` text inside a heredoc body; writing scripts with the Write tool avoids it.
- Lens table: for a TEST-HARNESS subject (no product code) the measurement row + harness fidelity + check adequacy is the
  right core; the rule lens's "independent decider from the TEXT first" was decisive (found RULE-1, missed by the subject's
  52-row selftest whose drills were written by the same lane).

## Proposed changes
- critics.md / skill §5 COMMON template: "lanecheck's pass line is `DONE rc=0`; `DONE rc=1` is a failure" (seen this round).
- skill §4 harness-fidelity row: add "a DRY or synthetic probe keys its reading on the exe it is handed; plant an exe swap"
  (F-2/C-3: two lenses, the subject's DRY could not see a re-time of the first pool).
- skill §4 check-adequacy row: "a selftest that recomputes a command's exit code instead of calling the command is a
  shared-source control" (C-7).

## Framework notes
- Four critics all returned in the launch turn (~16 min wall for the slowest): the coordinator never needed lanewatch.
  For small code subjects (one file of harness code) the coordinator pattern ran end to end in ~25 min including build.
