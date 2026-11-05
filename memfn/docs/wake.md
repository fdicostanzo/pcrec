# memfn kit — wake-up brief

Rewritten 2026-11-04 ~18:10 while 1c's gates run, split around Frank's hold. Committed docs win on any conflict.

## Who you are
The kit manager (`/pcrec-memfn-manager`). Main is the pcrec manager session `pcrec-main`. Frank rules, sometimes directly to the kit.
Kit worktree: worktrees/memfn on branch lane/memfn-k1102 (main 7b671bc2c + later main + kit commits: journal, review r2, skill).

## Read in order
1. This file.
2. The memfn/docs/journal.md tail (2026-11-03/04).
3. docs/design/memfn/span_pick.md REV 5.2, the design of record.
4. The reviews docs/dev/reviews/2026-11-04-r1-memfn-sp1b.md and r2-memfn-sp1c.md.
5. D186 + addenda, and D187 (positions travel as sets; cubes derived).

## CURRENT STATE: span_pick STAGE 1, unit 1c IN GATES
Landed: 1a, 1f, 1g, 1b (main 7b671bc2c). Next: 1c, then 1d, then 1e.
The per-unit process: an opus build lane, then a pcrec-critic code round, then a sonnet fix lane, then box-queue gates, then the done line, then main merges.

- **1c:** lane/memfn-sp1c @ 0eed05873. Reports: docs/dev/lanes/sp1c_report.md and sp1cfix_report.md.
  - Contents: unit 1c (run_scan asks run_member; translate's rank reads T_MASS_STRETCH) PLUS D187's set-only kit_mass and the normal-form refusal.
  - MF_SITE_ABI 22 -> 23 (ruled). No pcrec abi change, no emitted byte moved.
  - Gates 390-399 (keys kit-sp1c2-*) run in worktrees/sp1cfix. DO NOT touch it or worktrees/sp1c while they run.
    - 390 strict, 391 memfn, 392 reach and 393 ident1 run in the evening.
    - 394-399 have not-before 2026-11-05T01:05.
  - A watcher (background shell) exits on any kit-sp1c2 failure or on mech3 done.
  - A red stage gets a TRIAGE lane before you read its log.
  - If all green, post the 1c `done:` line in responses.md and tell main:
    - MF_SITE_ABI 23;
    - the new kit refusal, a pspans RUN byte outside its mask, unreachable from pcrec;
    - the ratchet per main's roadmap §5 recipes (R24 delta, from sp1c_report "Ratchet");
    - the stage-1 end count, 3 or 4.
- **Next: 1d** (T-PICK, the one candidate builder), cut from main after 1c merges. Fold in review r2's F12 (one normal-form predicate) and F13 (the position primitives' home), and r1's R10 if the call shape still repeats.

## Lessons (put them in every unit's briefs)
- An expect regex must match digits: use [a-z0-9-]+.
- make test runs ALONE via perfrun.
- VALIDATE_ONLY is not a mech run.
- Never merge into a worktree while a job runs there.
- A dump-stream declaration goes to every arm that runs that stream.
- `--analysis` refuses with `--emit-ir`, so an analysis identity arm lists C streams only.
- Stale main floors are main's to re-pin.
- boxqueue refuses a job FILE without a literal `--ready` case.
- Use `boxqueue: not-before T` to keep jobs out of Frank's hold.
- Verify gate jobs in a scratch queue (PCREC_BOXQUEUE_DIR) before the real add.
- Lanes run the anchor checker (scripts/m6read_check_sab_anchors.py) when they delete text.
- Never commit a header or ABI change while a test run is in flight.
- Review drafts carry no `plan.md:N` cites (PL14).
- Check every scripted skill edit's exit status before committing.
- Watchers match state, never labels.

## Box
Frank holds 20:00-01:00 daily: light work only, no suites or timing. The queue orders everything.

## Owner questions
None open.
