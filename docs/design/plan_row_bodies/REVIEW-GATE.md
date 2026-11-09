# [REVIEW-GATE] body: process rules enforced by the tools, not by prose

Filed 2026-11-08 by Frank, after the per-CPU SIMD code units (kit K0 d9df92c0d, pcrec P1 bfecd6143, kit U2 lane/memfn-u2, pcrec U3 lane/u3tgt) reached main, or the edge of it, with NO code critic round and no waiver. UNSCHEDULED. Trigger: the next missing critic round (tally below). Ideas only; nothing designed or built.

## Why it happened (lane critgap, 2026-11-08; findings kept at /var/tmp/pcrec-pcrec/scratch/critgap/findings.md)

1. The rule (pcrec-manager skill §5: "major code (before landing) gets a critic round") has no trigger at the merge step: CLAUDE.md's "merge a lane branch" row and the landing checklist never mention a round.
2. "Major" is undefined where the rule lives; the only definition is the full-suite ledger's major/minor class (U2+U3: abi 98, 174 files, is major).
3. No landing checklist, ledger line, brief template or wake gate has a review field.
4. A joint kit+main landing has no round owner (the kit's skill requires panels for kit designs only).
A drift, not a one-off: about 10 of 19 ledger "major" landings since 2026-10-18 had a code round.

## Interim rule (prose, from 2026-11-08)

At a merge, a landing in the ledger's MAJOR class needs a ruled code round or a written waiver naming who waived it; main owns the round of a joint kit+main landing, run on the joint tip.

## Candidate mechanism (Frank's sketch, refined by the manager)

1. `scripts/lanestart NAME TIER`: creates the worktree, the deliver file and the rulings file in one step (today by hand; two name collisions on 2026-11-08). The deliver file is the lane's effort file; it gains a `review: required | light | none` line, set from the table, never freely chosen.
2. A declared first-match table (e.g. `docs/dev/review_rules.tsv`) classifying a lane's DIFF, never its self-description: abi number changed, kit header, emitted scaffolding, a check's expectations re-aimed -> required; other src/cli/lib/memfn code over N changed lines -> required; smaller code -> light (one critic); docs only -> none.
3. A stage in `pre-push-light`: per merge commit pushed to main, classify its diff; for required/light, demand a review file in docs/dev/reviews/ whose header names a subject commit that is an ANCESTOR of the merged tip with at most a small delta since (a review of an early commit followed by big fix lanes does not count: U3 had three fix lanes after delivery), or a `waived:` line in the merge message naming who. Missing -> push blocked, with the existing "fix it, or --no-verify as a deliberate choice" message.
   Why the push, not a merge hook: git's pre-merge-commit hook skips conflicted merges (finished by a plain `git commit`: the risky ones); kit-branch merges would trip it needlessly; every path to main crosses the push.
4. Acceptance test: replay the last three weeks of merges through the table; it must flag the ~9 major landings without a round plus K0 and P1, and leave docs-only merges alone. One sabotage row: a required-class merge without a review blocks the push.

## Ride-along candidates (Frank asked which other items could travel with the change)

- DESIGN REVIEW at the build go: `lanestart` with a build tier asks for the design note's review file (docs/dev/reviews/) or a waiver, the design-side twin of the code gate.
- POLICY REMINDERS PRINTED BY THE SCRIPTS at the moment they apply (prose output, no blocking): lanestart prints the review class and the brief fields owed; `boxqueue add` prints the box-hold rule; lanecheck prints the merge rule for its class.
- EVENING HOLD in queued jobs (2026-11-08: the queue has no built-in hold; U3 jobs started at 18:44 in a live tree; a kit job ready at 18:55 would have run 2 h into 20:00-01:00): `boxqueue add` (or lanestart's queue helper) supplies a hold-aware --ready that refuses a start whose expected length crosses 20:00.
- RULINGS ADDENDA READ: a running lane missed its rulings-file addendum twice on 2026-11-08 (u3mov R6; earlier lanes per memory pcrec-no-addenda-to-running-lanes): lanecheck could list rulings-file entries newer than the lane's last commit and require each to be cited in the report.
- One writer per worktree: a job queued to run IN a lane's worktree while a lane still edits it (2026-11-08, twice): lanestart/boxqueue could refuse queueing into a tree whose lane is live, or snapshot the tree.

## Tally (when it repeats)

| date | what was missed | caught by | cost |
|---|---|---|---|
| 2026-11-08 | code rounds for K0, P1, U2, U3 | Frank's question | none landed broken; three fix lanes after delivery found defects a round targets |
