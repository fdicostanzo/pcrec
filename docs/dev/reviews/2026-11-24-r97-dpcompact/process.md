freeze: SUBJECT=24126f78cb6511f275088b2f8593f8277296ded5 BASE=2fdbcad3897c235efe41e147b9835e0698c560a0 main=4d26eef02 rulings(decisions/plan)@668b4b784 at 2026-11-24T14:26:07-05:00
setup done 2026-11-24T14:29:56-05:00; main HEAD now 4d26eef02; rulings drift: 
critics launched ~14:30, all returned by 2026-11-24T14:45:01-05:00 (identity 10.2m, modularity 6.9m, checks 14.7m)
checks: deliver.txt found EMPTY at read time (0 bytes; cause unknown, critic or setup); coordinator restored it and lanecheck run by coordinator

## Agents
| agent | model | launched | ended | state |
|---|---|---|---|---|
| identity | opus | ~14:30 | ~14:40 (10.2 min) | file complete, lanecheck DONE rc=0 (identity.done) |
| modularity | opus | ~14:30 | ~14:37 (6.9 min) | file complete, lanecheck DONE rc=0 (modularity.done) |
| checks | opus | ~14:30 | ~14:45 (14.7 min) | file complete; its deliver.txt was found 0 bytes (mtime 14:42, rewritten by the critic or a tool it ran); coordinator restored it, lanecheck DONE rc=0 |
All three returned inside the launch turn (background launch); no resends, no nudges. Final replies undeliverable (expected).
Verifier: inline by the coordinator (all CONFIRMED were quote claims or one-call repros), calls in .coord/verify/.

## Per lens
- identity: 2 findings (speed IDENTITY-1, size IDENTITY-2), both verified HOLDS; ~1,350 compiles; no overlap except MOD-7's SUSPECTED side note.
- modularity: 10 findings (design 2, maintenance 6, doc 2); MOD-3 overlaps CHECKS-1/4, MOD-5 overlaps CHECKS-2.
- checks: 6 findings (1 design, 4 maintenance, 1 doc); 7 silent bypasses + 5 row plants.
Time to draft: setup ~14:20-14:30 (two builds about 1 min each at -j2, 2 plants ~2 min), critics 15 min, verify+draft ~10 min.

## Blinding
No leaks noticed. The lane's report path was denied; one critic (modularity) cited docs/design/data_plan/CLAUDE.md, allowed.

## Process observations
- The modularity brief asked "is the wall check's design the general form", which pulled that lens into the checks
  lens's territory: two overlaps (MOD-3/CHECKS-1, MOD-5/CHECKS-2). Cheap here, but the general-form question should
  name the FAMILY only when another lens owns the check.
- My own verify compare of emitted C first showed a DIFF that was only the basename (`#include "base.h"`): the
  COMMON rule (same basename in two dirs) binds the coordinator's inline verification too.
- kit/cmp.sh first reported DIFF when both trees refused (no .c file): missing-output handling belongs in the kit
  template.
- The critic-edited deliver.txt (0 bytes) would have made the round look undelivered if the coordinator had relied on
  .done files only.

## Proposed changes
- §5 COMMON template: "Your deliver file is an INPUT; do not write it" (motivation: checks' deliver.txt went 0 bytes mid-round).
- §4 lens table, check adequacy: for a text-scan wall ("no file but X names Y"), plant the preprocessor/build-system
  bypasses (line splice, macro-built include name, `-include` in the Makefile, `#include` of a `.c`, a glob-opened
  path) and require one sabotage row whose plant contains no needle word (r97 CHECKS-1: 7 silent bypasses).
- §5: the kit's compare treats "both trees produced no output" as SAME (r97 cmp.sh).
- §4 standing questions: when a check lens runs, the general-form lens is briefed on the family, not the check's needle (r97 overlaps).

## Framework notes
- A light 3-critic code round on a data-layout change finished in 15 minutes of critic time with inline verification;
  the coordinator's set-level BASE/SUBJECT dump (before briefing) let the identity lens spend its budget on the
  second decoder and on cost instead of rediscovering row identity.
