# Lane devmethods — report (2026-10-20)

Docs only. No make, build or test runs; the one check run was the plan lint.

## Delivered (branch lane/devmethods)

- `docs/dev/devmethods/dev_methods_handoff.md`: the portable hand-off. It
  has 13 sections plus two appendices, and each practice gives a rule, the
  incident behind it and how to apply it.
- `docs/dev/devmethods/apply_here.md`: 14 ranked proposals for this
  project, each with evidence, what is already in place, the gap and the
  cost. All are unruled.
- `docs/dev/devmethods/CLAUDE.md`, plus one index line in
  `docs/dev/CLAUDE.md` and one in `docs/dev/lanes/CLAUDE.md`.
- The four journal reader notes stay committed as the evidence inputs.

## Method

1. Read all four reader notes, about 250 KB.
2. Read the rule files: root CLAUDE.md, BOILERPLATE, learnings.md, the
   manager skill, scripts/CLAUDE.md, testing.md headings, the process
   decisions (D5, D6, D26, D27, D45, D46, D48, D69, D77, D78, D80, D86,
   D94, D102, D125, D144, D149, D152, D153, D158), the meta sidecar, and
   about 50 of the manager's memory files.
3. Checked each apply_here "already in place" claim against the current
   files. Examples: which hooks are installed; whether a reach-only mutation
   mode exists; whether BOILERPLATE carries a numeric sweep cap; the
   skill's stale keepalive line; duplicate memory files; sabotage-id
   uniqueness.

## Could not verify

- The brief's "today's session is a fresh example" of lanes not waking.
  Session 120 has no journal entry yet, so the hand-off cites only the
  journalled instances.
- Recurrence counts given as "25+", "about 20", "about 12" and "eight or
  more" come from the reader notes' tallies. They were not re-counted in
  the journal.
- The token figures (61% manager share, about 73M cache-read tokens,
  about 900k per forked agent, 57%/82% small turns) are as quoted in the
  journal and memory. The underlying usage analysis lives in an old
  scratchpad and was not re-read.

## Plan lint

`bash tests/plan_lint/run_plan_lint.sh` was run from the worktree root:
checks passed 2, failed 0 (180 rows, 0 violations; selftest 32 plants
over 17 of 17 rules).
