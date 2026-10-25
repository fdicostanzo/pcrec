# queuemon lane report ([MON-SCRIPT], lane/queuemon, sonnet)

## STATE AT HANDOFF
- Branch lane/queuemon (worktree worktrees/queuemon), committed incrementally; rulings file read: no entries.
- Built: `scripts/queuemon` (run/start/stop/status), `scripts/monread`, `scripts/hooks/monitor_unread.sh`
  (registered in .claude/settings.json for SessionStart and UserPromptSubmit), `ensure_monitor` hook in
  `scripts/boxqueue` (cmd_start; inert when PCREC_BOXQUEUE_DIR is set or QUEUEMON_AUTOSTART=0),
  `scripts/test_queuemon.sh` (+ `scripts/tests/queuemon.test` wrapper, Makefile dep line): 43 checks pass, the
  hook's agent_id gate sabotaged -> 2 red. boxqueue.test re-run after the boxqueue edit (see reply).
- Docs: scripts/CLAUDE.md, docs/testing.md, skill TRIAL NOTE, plan [MON-SCRIPT] status.
- NEVER run against the live queue/state; the real queuemon was not started.
- Rulings applied: none present beyond the brief.

## Design points to know
- Own queuewatch state (`worktrees/.mgr/queuemon.state`), so the haiku session's state lock never collides; both can
  run in the trial (each reports from its own state; the first launch reports the running job from its START).
- queuewatch's JOB-DONE line carries no `reason=`; the EXPECT-mismatch rule is detected as `rc=0 verdict=GREEN`
  with outcome != green (the survey shows exactly this shape for the 5 stale-expect jobs). Logged as PROBLEM `EXPECT ...`.
- Deviations from the table, all flagged: outcome=cancelled JOB-DONE is INFO (cancelled by hand is no red); UNEXPECTED is
  class PROBLEM with text `UNEXPECTED <line>` (brief's explicit sentence); UP/INFO lines carry OWNER `mon` (journal
  only, never shown to main); rows 2/3/5 and the first RUNNER-DEAD are INFO lines.
- Row 5 still appends to `<logdir>/red_stages.txt` (the owner's triage reads it); not for SIMULATED logdirs.
- Liveness (monread): needs a pending/running job AND (queuemon pid dead OR monitor.log silent > cap 3000 + 300 s).

## Hook output shape (checked against https://code.claude.com/docs/en/hooks, "Add context for Claude")
    {"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":"..."}}   (SessionStart: same, other name)
Docs: plain stdout on exit 0 is also added as context for UserPromptSubmit/SessionStart; additionalContext is capped
at 10,000 chars (we cut at 9,000). The page fetch was cut off before the two events' own sections, so the exact
per-event example is inferred from the general section (the docs say the same structure applies); the live test is
the first real prompt after merge. The main-only gate is the absence of top-level `agent_id`.

## Snafu survey (worktrees/.boxqueue/failed/, 51 jobs, read-only; done/ has 116 green + 42 cancelled-by-hand)
| class | n | what broke | when | mechanical save? |
|---|---|---|---|---|
| A early invocation/start error | 4 | 576 dirty worktree at dry-run, 710 typo'd dependency, 301 and 699-k124diff Python str/bytes TypeError | 0-23 s | no: deterministic, fix the job |
| B stale expect (work green, rc=0) | 5 | 303, 120, 543, 713, 610: declared population wrong | end of run | no: owner corrects the declaration (EXPECT line now says so) |
| C rc=0 but a red line in the log | 3 | 540, 555, 577 (measurement listing steps) | end | no: judgment |
| D killed, rc=143 | 3 | 595 (81 s), 587 (23 s), 602 (60 s): SIGTERM early in the run, no runner event logged | early | a retry would run, but who killed it is unknown: owner call |
| E cap fired | 1 | 618 perfrun wall cap 2700 s in a -j2 shape | 45 min | no: the shape is the datum |
| G/H genuine red after the work ran | 35 | test/mech/axes/sweep steps red (perfrun RED-REAL, kit heavy "N step(s) failed", 300-main-fullsuite axes+mech+recidentity) | end or late | no: a real red; only re-running the RED stages is open (proposal 1) |
Counts: 0 of 51 were a runner death, lock orphan, disk-full or watcher problem; the only runner event in
queue.log is one SIGTERM stop (2026-10-21) that failed no job. So the haiku table's one mechanical recovery
(RUNNER-DEAD -> boxqueue start) had nothing to save in this record; queuemon keeps exactly that and nothing more.
Note on "SHORT" populations: for perfrun jobs "ran=none" is the counter never matching, not steps that never ran.

## PROPOSALS for ruling (nothing below is built)
1. Stage-level resume for fullsuite_job/chainrun-shaped jobs: on a red, a `resume` re-runs only the RED and
   not-yet-run stages of the same frozen commit. The cost it would have saved: 300-main-fullsuite spent 36,878 s and
   its re-run needs only axes/mech/recidentity. Needs a design (frozen commit, trailer-based stage state).
2. `boxqueue retry` is already the manual path for class D; a policy "auto-retry once on rc=143 within 120 s" is NOT
   proposed (cause unknown, could be a deliberate kill).
3. Fix stale expects at the source (class B, 5 jobs): the job author's `expect` after a section-count change; a
   preflight comparing the declared count to the last green count would catch it.
4. Optional later: a supervisor so a dead queuemon restarts itself (boxqueue already restarts it at each add/start).

## How to switch it on
Merge lane/queuemon. From then on any `scripts/boxqueue add|start` on the live queue starts queuemon (or run
`scripts/queuemon start`; `scripts/queuemon stop`; `QUEUEMON_AUTOSTART=0` opts out). The main session sees unread
`main` lines on each prompt via the hook; a background `scripts/monread main --wait` gives one notification.
The running live runner re-execs boxqueue on change. Keep the haiku session through one real run.
