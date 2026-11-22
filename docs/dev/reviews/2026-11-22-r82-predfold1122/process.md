# process.md — round r82 predfold1122 (design)
Coordinator: opus, launched by pcrec-predicate. Setup start ~13:40.
Freeze: subject docs commit 6f1fe4e84 (lane/pred-rev28; branch tip at setup 8997a11d8 = +journal/wake only).
Last reviewed 399ef98f4 (r77). Build-would-land commit (drift only): main 89eaf2cf0.
Record: docs/design/plan_row_bodies/COND-FAMILY.md @6f1fe4e84, in-force entries from line 6999 (array-in-piece: b) to EOF (7456).
Setup: R/subject (frozen copies, diff, record, record_in_force extract), R/tree (git archive of docs + evidence + lint), R/kit/bin/git shim (serves only `show HASH:path` for the two lane START commits).
Setup notes: hook blocked a `cd X && ...` twice (no_cd_worktree); used absolute paths.

## Agents
| agent | model | launched | ended | state |
|---|---|---|---|---|
| ruling | opus | 13:52 | ~14:01 | file complete, lanecheck DONE; final reply undeliverable (expected) |
| examples | opus | 13:52 | ~14:03 | same |
| general | opus | 13:52 | ~14:00 | same |
| fixind | opus | 13:52 | ~14:03 | same |
| modeclosure | opus | 13:52 | ~14:03 | same |
| verifier | opus | 14:04 | ~14:14 | verify.md complete (V1-V12), VERIFY COMPLETE |
All critics returned inside the launch turn (backgrounded, still blocking); no resend, no nudge. Draft ~14:20.

## Per lens: raised / verified / severity / overlaps
- RULING 9 (2 answer-level, PARTLY on RULING-2); EXAMPLES 4 (EXAMPLES-1 PARTLY); GENERAL 11; FIXIND 11; MODECLOSURE 9 (-6, -8 PARTLY).
- Overlaps: prefix-source root (RULING-1/2/7, GENERAL-1/2/3, MODECLOSURE-3/4); value-in-group-question (RULING-6, MODECLOSURE-5);
  occurrences bullet (EXAMPLES-4, GENERAL-7); zero-binding/bound-alone (GENERAL-5, RULING-4, FIXIND-5); evidence red (MODECLOSURE-7, coordinator).
- GENERAL passed two model observations to MODE-CLOSURE through its file (A&A "used 3 times"; zero-binding accepted) — handled via verifier V2/V7.

## Process observations
- COORDINATOR ERROR caught by a critic: my rerun summary recorded rc, and predbound/predcall exit 0 while red; MODECLOSURE-7 disagreed, I re-read last lines. Lesson 1 in the draft.
- The git shim (serve only `show HASH:path` from pre-extracted copies) let the lane models that read their START revision run in a non-git mirror with no log-body exposure. Worth a skill sentence.
- lanecheck prints "DONE rc=1" when failing; COMMON had to say "DONE rc=0" (a critic told "until DONE" could stop early).
- No blinding leak noticed. No critic opened a denied file as far as their files show.
- Lens table: RULING/GENERAL/MODE-CLOSURE converged on name resolution from three sides; a "name-table" drill would have been one lens.

## Proposed changes
1. Skill §3 / COMMON: "an evidence re-run's verdict is the model's last line, never its exit code" (this round).
2. Skill §5 design mode: when lane models read old revisions with `git show START:path`, mirror them through a shim serving only those paths (this round: no repo access needed by critics).
3. pcrec-predicate-manager lane brief: a fold lane re-runs EVERY in-force evidence model and re-greens or declares each red in a successor check; models exit non-zero on failure (EVID-1).
4. Lens table, simulate/mode-closure row: a NAME-TABLE drill (spelling kind x occurrences x read kind -> settings) for subjects that add a naming/prefix rule (ANS-1/ANS-2 found by three lenses).

## Framework notes
- Five opus critics on narrow briefs + one opus verifier finished in ~25 min wall; the verifier's grouping by root (12 items for 44 findings) produced 5 PARTLY corrections, as in r29.
- A coordinator re-running the evidence itself before briefing found the round's only blind evidence finding; it also made the coordinator fallible in a way a critic caught: cross-checking coordinator setup facts against a critic is cheap and should stay.
