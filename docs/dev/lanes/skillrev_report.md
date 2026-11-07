# skillrev: manager skills reviewed against what went wrong (2026-11-07)

Lane skillrev (opus), docs/skills only. Frank's five asks (2026-11-07):
(1) the kit missed REDs because it did not use the standard monitor tool;
(2) other misses, from both journals; (3) conditional statements; (4)
conditional loads; (5) interface-skill recommendations. Plus his remark:
"you guys are [too literal] with exact wording compliance. If you need a
response then always ask each other for a response unconditionally."

Branch `lane/skillrev`. The proposed skill edits are COMMITTED on the
branch (section "Proposed changes", marked COMMITTED); hook, script, memory
and settings changes are proposals only (marked PROPOSED), as ruled.

## For the owner, in plain words

- **Why the kit missed the reds.** Neither manager skill names the standard
  queue monitor at all (0 mentions of `queuemon`, `monread`, `boxqueue`,
  `lanecheck`, `pcrec-test` in either skill). The only place it is
  described is a "trial note" inside the monitor skill. So the kit wrote
  its own watchers, and its handoff notes (wake.md) passed the recipe on.
  They failed four times in four days; on 11-07 two reds (jobs 485 and
  482) sat in the monitor journal for an hour while the kit's private
  watcher stayed silent. Main saw them only because a hook shows main's
  lines when you type to main. That hook also has a flaw: it always reads
  `main`'s lines and it fires in ANY top-level session in this project, so
  if you type in the kit's session it shows the kit main's lines and marks
  them read for main. The post-compaction hook has the same blindness: a
  kit compaction re-injects MAIN's owner.md and wake.md.
- **The fix I made in the skills:** one path for both managers: every
  heavy run is a queue job, verdicts are read with `scripts/monread
  main|kit`, and every heartbeat tick runs it. No private watchers.
- **Conditional rules.** The ones that fail are the ones that ask a
  session to remember a state across compactions ("only if you are
  waiting on a peer") or to send nothing in one case ("reply only on a
  conflict"). I turned the first into a list in a file the heartbeat
  reads every tick, and the second into "always reply, either way".
- **Size.** The lane rulebook every lane loads was 25 KB; 14.7 KB of it is
  only for lanes that run things on the box. It is now 10.9 KB plus a
  separate `RUNS.md` read only when a lane builds, runs or queues. The
  main skill is 14.7 KB core (was 18.8) plus three short files read when
  a situation fires (monitoring, landing, peers).
- **Offering you commands.** The main skill now has a small table: when
  questions pile up it offers `/q`; when a full suite is due, `/pcrec-test
  full`; at a clean point with a big context, `/close`.
- **What needs your OK** (not done, hooks/scripts/settings): make the two
  hooks know which session they are in; teach `lanecheck` to catch a
  lane that says "owed: none" while it has jobs queued, and one that
  skipped a rulings entry.

## Misses found in the journals

Window: dev_journal.md 2026-10-24..11-07 and the kit's journal (its branch,
`worktrees/memfn`) for the same dates, plus the 11-07 cases the manager
named. "Rule" says whether a rule existed: EXISTS (ignored), BURIED
(exists but conditional or deep in a long file), MISSING, or TOOL (since
replaced by a tool, which held).

| # | date | miss (evidence) | rule |
|---|---|---|---|
| M1 | 11-07 | kit custom watchers (`scratch/memfn/kitmgr/watch_gates.sh` + an inline copy) silent through 485 census RED (10:25) and 482 make test RED (11:12); monitor.log lines 2184/2199 had both; main saw them, Frank relayed (kit journal "MISS ... Now using the standard scripts/monread kit --wait") | MISSING in the kit skill; the kit's wake.md (main copy, line 25) even prescribes `watch_sp1e2.sh` |
| M2 | 11-04/05 | three earlier kit watcher slips: matched the lock LABEL (never fired); matched cancelled jobs in done/ (false fire); "my bash watcher never fired on the RED; the queue monitor's line did. Replaced it with a python watcher" (each time patched, never replaced by the standard) | MISSING (kit skill §4 says "a background watcher script", i.e. write one) |
| M3 | 10-29 x2, 11-04, 11-05 | main launched `queuewatch` by hand with output discarded (consumes an event), twice in one day; event bursts after gaps; "never two watchers" | BURIED (journal lessons only; no skill line) |
| M4 | 11-07 | memory `pcrec-kit-nontiming-runs-no-ask` says "watch its END lines": that phrasing invites a private watcher | wording; memory edit PROPOSED (P9) |
| M5 | by construction | `scripts/hooks/monitor_unread.sh` hardcodes `monread main`, gated only on agent_id, so a typed prompt in the KIT session consumes main's unread lines; `post_compact.sh` re-injects main's owner.md/wake.md into a compacted kit session | MISSING (hooks assume one top-level session per project) |
| M6 | 11-07 | lanes idled "waiting for a notification" with owed jobs (manager's account) | BURIED: BOILERPLATE DO-THEN-FINISH / NEVER IDLE-WAIT, inside a 10 KB process section of a 25 KB file |
| M7 | 11-07 | a lane's lanecheck passed on a quoted "owed: none" while it owed jobs (manager's account); lanecheck's `owed: none` test is a regex over STATE AT HANDOFF (`owed\W[^.\n]*\bnone\b`) and never asks the queue | MISSING in the tool (P3) |
| M8 | 11-06, 11-07 | kit deliver files with prose in `owed:` (lanecheck reads keys): "my error, again in the deliver step" | BURIED: BRIEF_TEMPLATE says the format; the kit skill never names lanecheck |
| M9 | 11-07 | u25's report (committed 09:55) says "Rulings file u25_rulings.md was empty"; the file held R1 and R2 (last write 09:47) | EXISTS (BOILERPLATE RULINGS FILE: re-read before the report); nothing checks it |
| M10 | 11-06 | s2rev1 did not apply D188 add. 1 sent by message to a running lane | EXISTS (memory no-addenda), re-learned |
| M11 | 11-07 | main asked the kit to reply "on conflict only"; the kit: "NO CONFLICT, no reply sent" | conditional ask; the 10-09 memory says answer anyway, but only for deadlock checks |
| M12 | 11-06..07 | C4 arch-vocabulary allowlist patched four times for DATA: d7aaa3bc1 (`adx`, reachtri), 10ae71974 (S2932 anchor), 403aa54c8 (`adx` again, alttri2), d101c07e2 (`zen4-grid3`, s2efix); main then ruled C4 should scan code only | MISSING (no "third patch = scope question" rule; memory forest-for-trees is about design siblings) |
| M13 | 11-07 | a NAMED pcre2-reader was blocked by the D181 guard (manager's account). The guard admits only `agent_type == pcre2-reader` from the hook input; I could not verify what a named teammate spawn passes | MISSING: the CLAUDE.md row says "via a pcre2-reader subagent", not how to spawn it; cause UNVERIFIED (P6) |
| M14 | 10-31 | manager ran `qshard combine` by hand outside the lock, contaminating timing jobs 705/712 | EXISTS for lanes (BOILERPLATE TIMING WINDOWS), MISSING for the manager |
| M15 | 10-29 | a stopped lane left a boxlock waiter (trailgc2-sections) that would have taken the box | MISSING (journal lesson only) -> now monitoring.md §3 |
| M16 | 11-04 | conflicting table row resolved by keeping one side (dropped r5's critic clause) | MISSING -> landing.md |
| M17 | 11-07 | altcatch: both sides moved a count 78 -> 80, git merged "80" over 82 names; test-registry caught it | MISSING -> landing.md |
| M18 | 11-03 | a gate named "mech" was VALIDATE_ONLY (7 s, no row ran) | TOOL (smallfix1 made the line say so) |
| M19 | 11-03, 10-31 | multi-stage jobs under one cap (314, kit 697) | EXISTS (ONE STAGE PER JOB), ignored once more by the kit |
| M20 | 10-28 | manager's /var/tmp sweep deleted the bench's directory (selected by owner+date) | journal lesson; "select by our own prefix" lives nowhere a manager reads |
| M21 | 10-28 | `wtprune --apply --dir` removed 7 kit worktrees | TOOL row filed [WTPRUNE-DIR-SCOPE] |
| M22 | 10-24 | a kit lane took the box lock three times over pending main jobs "despite instructions" | TOOL (lockyield: the lock enforces it) and it held |
| M23 | 10-24 | a lane said "committed" but had only staged | TOOL ([LANECHECK] checks commits) |
| M24 | 10-29 | Frank: "Are we critiquing these designs?": three designs went toward build without rounds | EXISTS (§5), ignored |
| M25 | 11-02/03 | PL14 strips needed on merged kit reviews (plan line cites) | kit-side grep added after; fine |
| M26 | 11-06 | 212 make test ran on a tree a fix lane was editing (contaminated) | TOOL (qspeed: `boxqueue batch --snapshot`) |

The pattern: every miss in the TOOL rows stopped recurring; the EXISTS and
BURIED rows recur (M6, M10, M19, M24 each re-learned). Rules a session must
remember fail; a tool or a step that reads a file holds. That ranks the
proposals below.

## Proposed changes

Ranked by expected effect. Each: problem, rule today, proposal, and its
kind (UNCONDITIONAL / TRIGGER-LOADED / TOOL-HOOK).

### P1. One queue-verdict path for both managers (ask 1) — COMMITTED, TOOL-backed
- Problem: M1-M4.
- Rule today: none in either manager skill; pcrec-monitor's "TRIAL NOTE"
  only; the kit skill §4 says write "a background watcher script".
- Now: `pcrec-manager/monitoring.md` §2 (shared by the kit through its
  trigger table): every heavy run a `PRIO-OWNER-REST` job; `scripts/monread
  OWNER` at wake and on every heartbeat tick; ONE background `monread OWNER
  --wait` while jobs are pending; a RED -> triage lane; never a private
  watcher, never `queuewatch` by hand. Always-on line in both cores. Kit
  §3/§4 rewritten (queue jobs, no Mac executor channel, Linux paths).
- Kind: UNCONDITIONAL (a step at wake and every tick), resting on the
  existing tools.

### P2. Hooks that know which session they serve — PROPOSED (hooks/scripts)
- Problem: M5. `monitor_unread.sh` serves only `main` and is session-blind;
  `post_compact.sh` re-injects main's notes into any session.
- Proposal: a per-session role file. The UserPromptSubmit hook already sees
  the prompt: when it is `/pcrec-manager` or `/pcrec-memfn-manager` (or
  `/pcrec-monitor`), write `worktrees/.mgr/session_role.<session_id>` =
  main | kit | mon. `monitor_unread.sh` then runs `monread <role>` (nothing
  for an unknown role), and `post_compact.sh` injects owner.md + wake.md
  for main, `memfn/docs/wake.md` (kit branch copy) for kit, nothing else.
  A settings.json change is NOT needed (same hook entries); the two
  scripts change. Owner: a scripts lane with a self-test (two fake
  sessions, cursors untouched across roles).
- Kind: TOOL-HOOK. This also gives the kit the "typed prompt shows your
  lines" backup main has.

### P3. lanecheck checks owed jobs against the queue and the rulings file — PROPOSED (script)
- Problem: M6, M7, M9.
- Rule today: BOILERPLATE (rulings re-read; END after owed runs); lanecheck
  regex for `owed: none`.
- Proposal: (a) with `owed: none`, lanecheck asks `boxqueue` for any
  pending/running job whose name carries the lane's name and fails if one
  exists ("you have queued jobs X: list them under owed"). (b) if
  `NAME_rulings.md` has entries, STATE AT HANDOFF must name its last `R-n`
  (an "empty" claim over a non-empty file fails). (c) on DONE with owed
  keys, print one more line: "owed jobs are the manager's now: END; do not
  wait for them." (just-in-time instruction, against M6). Rulings files
  number entries R1, R2, ... (already the manager's practice, u25).
- Kind: TOOL. The committed edits already add the manager-side check
  (peers.md §3, BRIEF_TEMPLATE RULINGS FILE) and the OWED RUNS wording
  ("Do NOT wait for the jobs or for any notification").

### P4. Unconditional replies; purpose over wording (ask 3, Frank's remark) — COMMITTED
- Problem: M11, and the remark.
- Rule today: memory pcrec-hourly-peer-checkin (answer in spirit) covers
  only deadlock checks; no rule on how to ASK.
- Now: `peers.md` §1 + an always-on line in both cores: a message that
  needs anything back ends "REPLY: one line, either way"; receiving, answer
  every question in one line; when a rule's wording and purpose diverge,
  follow the purpose and say so. BRIEF_TEMPLATE REPLY field says the same
  for lanes.
- Kind: UNCONDITIONAL.

### P5. Split always-on cores from situational rule sets (ask 4) — COMMITTED
- Problem: rules recur because they are buried (M6, M14, M19); every lane
  loads 25 KB; both managers load everything every wake.
- Sizes (bytes, before -> after):

  | file | before | after |
  |---|---|---|
  | lanes/BOILERPLATE.md (every lane) | 25,206 | 10,872 core |
  | lanes/RUNS.md (new; lanes that build/run/queue/time) | - | 15,564 |
  | pcrec-manager/SKILL.md | 18,767 | 14,728 core |
  | pcrec-manager/monitoring.md (new) | - | 7,210 |
  | pcrec-manager/landing.md (new) | - | 2,821 |
  | pcrec-manager/peers.md (new) | - | 2,755 |
  | pcrec-memfn-manager/SKILL.md | 16,336 | 18,372 (stale text replaced, trigger table + always-on block added) |
  | lanes/BRIEF_TEMPLATE.md | 4,196 | 4,551 |
  | not changed: pcrec-critic 26,864; pcrec-monitor 15,990; pcrec-test 7,767; q 2,333; close 1,749; idle 1,705 |

- Each core opens with a trigger table ("about to X, read Y FIRST"), the
  shape of root CLAUDE.md's situation index. BOILERPLATE's table sends
  build/run/queue/sabotage/timing work to RUNS.md; the main skill's sends
  heartbeat/idle/queue/RED to monitoring.md, merge/landing/prune to
  landing.md, peer/lane messages to peers.md. Text was MOVED, not
  rewritten, except the NEVER IDLE-WAIT bullet (a short core version stays
  in BOILERPLATE; the chainrun/boxqueue mechanics moved).
- Further splits PROPOSED, not done: pcrec-monitor's TEST MODE + rehearsal
  sections (~4.3 KB) to a file read only under TEST_MODE=1 (the monitor is
  a haiku session that re-reads its context every wake); pcrec-critic
  (26.9 KB, the largest) by role (coordinator / critic / verifier); the kit
  skill's §5 delivery and §6 design to trigger files (~2.2 KB).
- Readers that still cite BOILERPLATE for moved text (comments only,
  harmless): scripts/emit_sweep.py:3071 (sweep cap), scripts/verdict:76
  (triage rule), tests/quoting/k62_class_range_e.rxt:10 (box facts),
  tests/code/card_inline.sh:29. Re-pointed: docs/design/plan_row_bodies/
  BOXQUEUE.md ("Queue template"), the skills.
- Kind: TRIGGER-LOADED.

### P6. pcre2-reader spawn instruction — COMMITTED (skill) + PROPOSED (probe)
- Problem: M13.
- Now: main skill §3: spawn with `subagent_type: "pcre2-reader"` and no
  `name` until a named spawn is shown to carry the type to the guard.
- Proposed: one probe (a named and an unnamed reader each Read one ref
  file; log the hook input's `agent_type`), then either allow named
  readers in the guard or add the "unnamed" note to the root CLAUDE.md row.

### P7. The heartbeat prompt reads state instead of recalling it (ask 3) — COMMITTED
- Problem: "ONLY if you are currently waiting on a specific peer" and "ONLY
  WHILE MONITORING" ask the session to evaluate a state it may have lost
  to compaction.
- Rule today: pcrec-manager §1 step 0 (and kit §1 step 0).
- Now (monitoring.md §1, verbatim prompt): every tick (1) `scripts/monread
  OWNER`; (2) read the wait list (main: owner.md "Waiting on"; kit:
  `worktrees/.mgr/waiting_on.kit`) and check entries older than 60 min;
  (3) deliveries; (4) one line. Keep/drop is a 4-row table of states
  (live lane -> keep; queue-only with queuemon alive and no waits -> may
  drop via /idle).
- Owner.md needs a "Waiting on" section (it is gitignored; the manager
  adds it at the next refresh). The post-compact hook re-injects owner.md,
  so the list survives compaction.
- Kind: UNCONDITIONAL steps over a file.

### P8. The third patch to a check is a scope question — COMMITTED
- Problem: M12.
- Now: delegaudit rule 7 in the main skill: before adding an
  allowlist/exception row, `git log --since=14.days -- <allowlist>`; two or
  more rows for the same cause -> stop and report the scope defect. Belongs
  in the triage brief (`pcrec-test/triage_brief.md`) too: PROPOSED.
- Kind: UNCONDITIONAL step (for triage lanes).

### P9. Memory wording that invites the wrong tool — PROPOSED (memory is read-only to me)
- `pcrec-kit-nontiming-runs-no-ask`: "watch its END lines" -> "watch with
  `scripts/monread kit --wait`".
- `pcrec-hourly-peer-checkin`: add "and every ASK is unconditional
  (REPLY either way), Frank 2026-11-07".
- `pcrec-cache-keepalive-cron` / the heartbeat text: point at
  monitoring.md §1 as the prompt of record.

### P10. Offer the owner the interface commands (ask 5) — COMMITTED
- Problem: nothing told the managers when to suggest `/q`, `/close`,
  `/idle`, `/pcrec-test`; Frank had to discover `/q` was the move.
- Rule today: main skill §1 mentioned `/idle` and `/q` exist; the kit
  skill nothing.
- Now: main skill §2 "Offer the owner": a state -> one-line offer table
  (blocking or 3+ questions -> `/q`; D177 trigger -> `/pcrec-test full`;
  context > ~35% at a natural point -> `/close`; heartbeat kept for a
  reason Frank may not share -> `/idle`; kit/bench question -> `/q kit`);
  one offer per message, not repeated until the state changes. Kit §7
  carries the two that apply to it.
- Not offered on purpose: `/pcrec-monitor` (queuemon is the standing
  monitor since 10-25; the skill's TRIAL NOTE should be promoted to the
  default and the session method marked fallback: PROPOSED edit to
  pcrec-monitor).
- Kind: UNCONDITIONAL table over read state.

### P11. Smaller items — COMMITTED
- Lessons that are rules go into the skill, not only wake.md (main §6
  step 3, kit §7 step 6): the kit's wake.md carried the private-watcher
  recipe 11-04..11-07.
- Kit skill: deliver-file `owed:` holds queue keys or `none` (M8); write
  deliver + rulings files before launch.
- landing.md: merge conflicting table rows by text, recount conflicting
  counts (M16, M17). monitoring.md §3: boxlock waiters + detached runs
  before TaskStop (M15). Main trigger row for timing work (M14).

## STATE AT HANDOFF

- Branch `lane/skillrev`; skill edits in e8e36a228, report in the commit
  that adds this file. Files: `.claude/skills/pcrec-manager/{SKILL,
  monitoring,landing,peers}.md`, `.claude/skills/pcrec-memfn-manager/SKILL.md`,
  `docs/dev/lanes/{BOILERPLATE,RUNS,BRIEF_TEMPLATE,CLAUDE}.md`,
  `docs/design/plan_row_bodies/BOXQUEUE.md`, this report, the history index.
- Rulings file `skillrev_rulings.md`: empty at every checkpoint (0 bytes);
  no entry applied.
- Validation: docs only; the pre-commit staged checks passed (plan_lint,
  52 staged checks, CLAUDE.md size). No suite run.
- OWED: none. Merging needs the manager's review; the PROPOSED items (P2,
  P3, P6 probe, P8 triage brief, P9 memory, pcrec-monitor promotion,
  further splits) need Frank's OK and lanes.
- Note for the merge: the edited skills and BOILERPLATE are read by live
  sessions and lanes; a lane briefed before the merge reads the old
  BOILERPLATE, which is consistent on its own.
