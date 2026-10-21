# docs/dev/lanes/ — per-lane restart records and delivery reports

Purpose: the lanes' own voice. One `<lane>_report.md` (delivery: commits, the
brief's acceptance table filled with MEASURED values, findings) and/or one
`<lane>_log.md` (running log, in order, for the lane's restart) per lane that
chose to keep them, plus lane-owned evidence/instrument files.

## Standing rules

- `BOILERPLATE.md` (2026-09-06, Frank) is the standing rules every lane reads
  FIRST: scope mandate, worktree ritual, box facts, process rules, lifecycle
  policy (NO self-keepalive crons - subagent caches are 5-minute TTL; finish,
  hand back complete, END, never idle). Briefs name only task, tier and
  deliverable and point there. When a rule changes, update BOILERPLATE.md;
  do not grow briefs back.
- `BRIEF_TEMPLATE.md` (2026-10-20) is the manager's field list for every lane
  brief (rulings quoted, id ranges, the owner's BUILD GO or "NO BUILD GO",
  stop rule and premise test, owed-run wording, deliverable and reply size);
  skill `pcrec-manager` section 3 points at it, BOILERPLATE carries the
  matching STOP rule. Point at these two files; never restate them here.
- A lane's report MUST be added to this directory's history index (the
  per-lane entry list, now in the history file) in the SAME change as the
  report (N-1 / D149; applies to pcrec and kit lanes; kit briefs say so).
- `_log.md` and `_report.md` are optional: briefs allow, never require them.
- `<lane>_brief.md` is the MANAGER's artifact, kept only when a lane is
  PARKED mid-flight across a session boundary: the original launch brief
  verbatim (stale sections marked) so a fresh agent can be relaunched onto
  the lane's branch. Delete it when the lane's row completes and merges.
- Lane files are the lane's voice, not the manager's: plan, journal and
  decisions log carry the manager's record; on disagreement the committed
  docs in docs/dev/ win. Historical once the lane is merged; never edited
  afterwards.
- Lane-written files stay inside this directory (evidence dirs, scripts,
  patches); the scope mandate in the root CLAUDE.md applies.

## Files / subdirectories

- `BOILERPLATE.md` — standing rules every lane reads first.
- `BRIEF_TEMPLATE.md` — the manager's brief field list.
- `<lane>_report.md` — delivery report for lane `<lane>` (about 480 exist,
  each described by one entry in the history file's list: tag, date, lane,
  tier, what it delivered and its key findings).
- `<lane>_log.md` — the lane's running log, where kept.
- `<lane>_brief.md` — parked-lane launch brief, where present
  (A `NAME_rulings.md` file is polled by a running lane.)
- `<name>_evidence/`, `grid1/`, `grid2/`, `gridread/`, `costmodel/`,
  `armread/`, `b3b/`, `m0build/`, `mechpar_chain/`, `origsurvey/`, `pcscope/`,
  `r17b2/`, `regimefacts/`, `rwcorpus/`, `rwquest/`, `rwquest2/`, `sbscope/`,
  `slotarms/` — per-lane instrument/evidence directories (data, drivers,
  logs) cited by the matching report.
- Loose lane artifacts: `*.py`, `*.sh`, `*.c`, `*.patch`, `*.tsv`, `*.out`,
  `*.log`, `*.txt` instruments and data (census scripts, sweeps, movers,
  probes); `I-43_draft.md`, `iface_digest.md`, `mechpar_profile.md`,
  `rel1pre_facts.md`, `tiers88_inbox_draft.md`, `vecspike_reading.md`,
  `w4_facts.md`, `w5_facts.md` — lane-written notes/drafts.

## Pointers

- `docs/dev/lanes/BOILERPLATE.md`, `BRIEF_TEMPLATE.md`; `.claude/skills/pcrec-manager` section 3.
- `docs/dev/plan.md`, `docs/dev/dev_journal.md`, `docs/dev/decisions.md` (the manager's record, which wins on disagreement); `docs/dev/reviews/` (panel reviews lanes cite).

History (long narrative, dated notes, measurements, per-lane records; not auto-injected): docs/dev/history/claude_md/docs__dev__lanes.md
