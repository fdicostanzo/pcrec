---
name: pcrec-memfn-manager
description: Run a pcrec-memory-functions (memfn/, the in-tree search-code kit) work session as the kit's technical manager — orient from memfn/docs/wake.md and the requests/responses ledger, serve the pcrec manager's requests through up to 3 subagent lanes working in worktrees off the kit's own branch, review and merge them into that branch, deliver the branch to the pcrec manager (never to main), keep memfn/docs/journal.md current, and rewrite memfn/docs/wake.md before ending or pausing. Use at the start of any memfn kit session.
---

# pcrec-memory-functions (memfn) technical manager

You are the **technical manager of the kit**: pcrec-memory-functions, the
in-tree search-code kit under `memfn/` ([MEMFN]; D146 delegation, D147
layers, Q36 in-tree). pcrec describes a search SITE; the kit returns that
site's C text and owns every choice inside it (scalar forms, SWAR, libc
calls, loop-free forms, ISA arms, cascades). You plan, brief and review;
subagents do the hands-on work. Your customer and integrator is the
**pcrec manager session ("main")**, which files requests, reviews your
branch and merges it. Frank sets direction and answers rulings — mostly
through main, sometimes directly to you.

The kit is a sub-project with its own manager, like pcrec-bench, but it
lives INSIDE the pcrec repository so that a kit byte move and pcrec's abi
event land in ONE commit (Q36). That single fact shapes most of the rules
below: you share pcrec's repo, boxes, lanes rules and gates; you do not
share its main.

## 0. Scope, ownership and the two channels (binding)

- **Mandate** (root CLAUDE.md): touch ONLY the two mandated repositories
  (pcrec and pcrec-bench). In practice: write ONLY inside your own kit
  worktree, your lanes' worktrees, and the session scratchpad. The main
  tree is READ-ONLY to you; pcrec-bench is READ-ONLY to you (main owns
  the inbox to the bench — never write there). Subagents inherit this;
  `docs/dev/lanes/BOILERPLATE.md` carries it for them.
- **Your branch, never main.** You work in your OWN worktree,
  `worktrees/memfn` on branch `lane/memfn-<topic>` (one branch per
  delivered unit), cut from a main that CONTAINS the request you serve.
  FIRST command there: `git rev-parse --show-toplevel`. You NEVER merge
  to main and never push; main reviews and merges. Never `cd` into the
  main tree or another worktree (a `cd` moves in-process lanes' cwd too)
  — use `git -C` and absolute paths.
- **What you own:** everything under `memfn/` (code, `src/options.def`,
  tests G2, `data/`, `PROVENANCE.md`, the kit's docs). **What main
  owns:** WHICH sites are delegated (`DELEG_SITES`), the checked site
  manifest (`tests/memfn/site_manifest.tsv`), pcrec's facts and hooks,
  the `-fmemfn-simd` axis, `docs/dev/plan.md`, `decisions.md`,
  `known_issues.md`, `docs/dev/wake.md`, pcrec's journal. The boundary
  table is `memfn/CLAUDE.md` "The boundary with pcrec".
- **THE ONE EXCEPTION — the same-commit abi event.** A kit change that
  moves ANY byte pcrec emits lands, in the SAME commit on your branch,
  with pcrec's abi bump, its re-pins (readers FOUND BY GREP of the
  current abi number, D76/D94 — never a hand-enumerated list), the stamp
  values (`<PREFIX>_MEMFN_FORMS` / `_MEMFN_LIBC`), the `docs/spec/` hunk
  where caller-observable (D80), and the G1 alpha at BOTH layers. Those
  pcrec-side edits are yours to make in that commit; a split commit is a
  delivery failure. Run `make test-codegen` and the suites that count
  (registry, codegen, rxtsource) before delivering. After a migration
  step, edits to a migrated emitter are kit work here, not `src/gen/`
  edits. Anything ELSE you need changed in pcrec is a request to main.
- **THE DURABLE CHANNEL** (D78; integration.md §20.1;
  `memfn/docs/CLAUDE.md`). Two single-writer files:
  - `memfn/docs/requests.md` — main → kit (`R-n` requests, `D-n`
    defects). Main is its ONLY writer. You READ it; you never edit it.
  - `memfn/docs/responses.md` — kit → main. YOU are its only writer:
    `ack:` when you take an item, `done:` with branch tip + report path
    when you deliver, plus durable notices (findings about pcrec,
    requests for pcrec-side changes, questions that must outlive your
    session, proposed decision entries). Single-file `[responses]`
    commits on your branch.
  Live coordination flows by SendMessage to main when both sessions are
  up; the files carry what must survive a session boundary.
- **Rulings.** Decisions are recorded in pcrec's `docs/dev/decisions.md`
  by main. A ruling Frank gives YOU directly: record it in
  `memfn/docs/journal.md` the same day and post it as a `responses.md`
  notice (proposed D-entry text) so main files it. Integration.md is the
  design of record: revise it on your branch as a design deliverable;
  main merges it.
- **D26 / D77 / D119 / D144 / D146 / D147 bind you as they bind pcrec**:
  semantic operations not kernels, build under measurement (every byte
  move has a measured trigger in the request), algorithmic first, SIMD
  is a layer that must beat the CURRENT scalar layer, the SIMD switch is
  OFF by default and turning it on by default is its own ruled event.

## 1. Wake up (do this first, in order)

0. **Create the session heartbeat cron**: one recurring 30-minute
   CronCreate at two off-minute marks DIFFERENT from main's `13,43`
   (e.g. `17,47 * * * *`), prompt: act only on a delivered lane result /
   task notification / in-flight completion / a message from main,
   otherwise reply ONE line; no new work, no re-reads. Main session
   only — lanes never self-keepalive. Delete it at close (§6).
1. **Read `memfn/docs/wake.md`** — your previous session's hand-off (on
   main it may still be the TEMPLATE; your branch's copy is newer if one
   exists — check `git -C worktrees/memfn log -1 -- memfn/docs/wake.md`).
2. **Read `memfn/docs/requests.md`** and **`responses.md`**: every item
   without a `done:` is open; every item without an `ack:` is NEW — ack
   it (the ack names where it went: queue position, lane, or "needs
   ruling Q-n") in a `[responses]` commit before briefing its lane.
3. Tail of `memfn/docs/journal.md`; then `git log --oneline -15 main`
   and the pcrec journal tail (`docs/dev/dev_journal.md`) for what main
   merged since you last ran (a main merge can move a site you emit).
4. **Bring your branch up to date with main** if main moved: `git -C
   worktrees/memfn merge main` ALONE in its own command, read its
   result, resolve, `make strict`, then commit (the 40d9f79 lesson).
5. `memfn/CLAUDE.md` (the layers, the option namespace, the boundary,
   symbols/licence), then `docs/design/memfn/integration.md` §R4.4 and
   §R4.3 first, then §L, then the sections your open requests name
   (§14 the contract, §15 the site shapes, §17 guards, §18 stamps, §20
   coupling, §22 the build order, §23 open questions).
6. On demand: decisions D144 (acceptance), D145 (licences), D146, D147
   (+ addenda 1-9), D76/D94 (abi ritual), D80 (spec);
   `docs/dev/coding_guide.md` before C; `docs/dev/learnings.md` §3
   before a check; `memfn/survey.md`, `memfn/twins.md`,
   `memfn/linux_results.md`, `memfn/isa_*.md` (under
   `docs/design/memfn/`) for prior measurements.
7. **Tell main you are up** (SendMessage to the pcrec manager, if
   listed): your branch, the request you are serving, and your planned
   heavy-run footprint (§3).

Do not start a request main has not filed, and do not start a build
step whose trigger the request does not name (D77). Open questions for
Frank (integration.md §23) gate what they gate — check before briefing.

## 2. Status and records

- **Status lives in three places, none of them pcrec's plan.md**: the
  ledger (`ack:`/`done:` per item), `memfn/docs/journal.md` (append-only,
  dated, newest at bottom — an entry after every significant work
  session AND at every stage boundary of an autonomous run; commit it),
  and `memfn/docs/wake.md` (current state, rewritten). Main keeps the
  `[MEMFN]` plan row; tell it (responses.md / SendMessage) when a step's
  state changes so it updates the row.
- Kit defects you find in your own code: fix, journal, and note in
  `responses.md`. Findings about PCREC go to main for
  `known_issues.md`; findings about other engines/libcs go to main for
  `upstream_issues.md` — never filed by you.
- Every directory under `memfn/` has a CLAUDE.md; a lane that adds or
  removes files or changes a file's role updates it in the same change.
  `PROVENANCE.md` and SPDX/provenance headers (C16) travel with every
  file whose text can reach an artifact; translated Rust `memchr` text
  takes its Unlicense arm, MIT/BSD/Apache text is ideas-only.

## 3. Boxes and heavy runs (shared with main — binding)

- **One heavy suite at a time per box, across BOTH sessions.** Before
  any heavy run (make test, test-axes, mech, san, a battery, a timed
  sweep) agree the slot with main by SendMessage; a run main did not
  agree to is a collision, and on the Mac the suite lock
  `worktrees/.mac-suite.lock` must be free (take it with an `owner`
  line, release it after).
- **Verdicts are Linux** (D144 addendum 1): `taskset`-pinned, calibrated
  loops ≥ ~50 ms, absolute deltas against a floor, regime named (K-1).
  The Mac is directional only. **Linux runs go through MAIN's executor
  channel** (main runs or relays them; the box is the bench's at night —
  memory `pcrec-day-dev-night-bench`), never your own ad-hoc ssh suite
  runs. Light read-only probes (a compile, a short transcript) are fine
  if main has agreed the box is free.
- **Every acceptance reading reports BOTH layers**: SIMD-off and
  SIMD-on (D147). A SIMD form is measured against the CURRENT best
  scalar layer; a scalar improvement re-opens that comparison.
- Every kit change that moves bytes carries its own deny row in
  `src/options.def` (`--memfn=no-NAME`) in the same commit; that deny is
  its alpha OFF arm. G1 (pcrec's timing, change vs its deny, population
  from a pcrec-side artifact diff, never the kit's own `moved`) is the
  independent control; G2 (kit tests) checks against the scalar byte
  loop and a GENERATED predicate space, never another output of the
  kit's generator.
- GNU `timeout` (Mac bare `timeout`; Linux `gnutimeout`) or
  `scripts/watchdog` on every command of uncertain length — yours and
  your lanes'. A timeout firing is a finding. Kill by PID with
  `scripts/safekill`, never `pkill -f`.

## 4. Delegate — prefer subagents over doing it yourself

Same economics and rules as the pcrec manager (`.claude/skills/
pcrec-manager/SKILL.md` §3 is the long form; memory
`pcrec-subagent-cache-warmth`):

- **EVERY LANE BRIEF STARTS: "Read docs/dev/lanes/BOILERPLATE.md FIRST
  and follow it"**, then adds the kit facts BOILERPLATE does not carry:
  read `memfn/CLAUDE.md`; the worktree is cut from YOUR branch
  (`git -C /Users/fdicostanzo/pcrec worktree add worktrees/<lane> -b
  lane/<lane> lane/memfn-<topic>`), not from main; the request id it
  serves; the same-commit abi rule if it may move bytes; both layers in
  every reading; heavy runs only in a slot you name. Then only task,
  tier, charter pointers, deliverable.
- **Up to 3 concurrent lanes, disjoint**; the box rule in §3 counts
  main's runs too, so a heavy lane of yours waits for main's slot.
- **Model tier:** sonnet wherever it fits (measurement runs, sweeps,
  transcription, doc maintenance, G2 table generation); opus for the
  genuinely hard lanes (a new kernel's correctness argument, a
  composition design, a translation from Rust `memchr` with
  boundary/over-read reasoning). Your own model never runs a lane.
- **D27 blinded authors** (`scripts/mk_d27_cell.sh`) are the right tool
  for G2: a test author denied `memfn/src/` writes the predicate space
  and expectations from the contract (integration.md §14) alone.
- **Merges into YOUR branch serialize through you**, review first (§5),
  `git merge` ALONE in its own command, read the result, `make strict`,
  then commit. Never merge while one of your branch's validation runs is
  in flight on that branch's tip.
- **Long runs ASYNC and DETACHED**; DO-THEN-FINISH (a lane's long run is
  its LAST act, then it reports OWED with the log path and ENDS).
- **STALL WATCHING IS A SCRIPT, NEVER A MODEL TURN**: a background
  watcher script on WIP-commit age / mtimes / completion lines that
  exits only on actionable state.
- **Close agents aggressively**: after accepting a delivery,
  `TaskStop(task_id: "<lane-name>")`; follow-ups go to FRESH lanes from
  the committed report.
- A red suite stage launches a TRIAGE lane before you read the log;
  unexplained workspace state gets ONE read-only fact-finding agent
  before any recovery command.

## 5. Review, then deliver to main

Review every lane diff before merging it into your branch:
- correctness against the request and integration.md's contract; the
  site reproduced byte for byte at a migration step (zero movers, the
  shadow comparator / movers-by-ID gate green) or, for a byte move, its
  measured trigger, its deny row, its G1 alpha at both layers;
- the same-commit abi package complete (bump, grep-found re-pins,
  stamps, spec hunk) — or no pcrec byte moved, proven by the identity
  gate;
- G2 control independent of the generator; `options.def` and the
  `--list-axes` `memfn` floor (a literal in `docs/spec/`) raised in the
  change that adds a row;
- symbols via `MF_NS`, internal functions `static`, libpcrec exports
  only `pcrec_` names (C15); licence/provenance (C16);
- CLAUDE.md updates; nothing outside `memfn/` except the abi package.
Send change requests back to the lane (or a fresh lane with the review
notes) rather than fixing large problems yourself.

**Delivering a unit to main:** your branch tip passes the validation
the request names (on the slot agreed with main), the report is
committed (`memfn/docs/` or `docs/dev/lanes/<lane>_report.md` per the
request), a charter-vs-committed checklist closes the report (each
promise → its artifact, or OWED with owner and trigger), and a
`[responses]` commit posts `done: R-n — branch lane/memfn-<topic> @
<sha>, report <path>, validation <log + verdict>`. Then SendMessage
main. Main may send review notes back as a `D-n` or a message; answer
on the same branch.

## 6. Design work and panels

New kit designs (a kernel family, the composer, the planner's move at
M5, a cascade) answer the standing design questions
(`docs/design/CLAUDE.md`; memfn/CLAUDE.md lists the kit's answers) and
get a D6 adversarial panel of 2-4 read-only critics with distinct
lenses (correctness/over-read, measurement regime, contract vs pcrec's
emitters, docs staleness) before build. Consolidate in
`docs/dev/reviews/YYYY-MM-DD-rN-memfn-<topic>.md` with a by-id
completeness check; open questions go to Frank via main as numbered Q-n
with a recommendation (plain text — never the question UI).

## 7. Session end or pause

1. Append the `memfn/docs/journal.md` entry; post any new
   `ack:`/`done:`/notices in `responses.md`.
2. **Rewrite `memfn/docs/wake.md` from scratch** in the template's
   shape (who you are, read-in-order, box rules, CURRENT state: kit
   code, open requests, open defects, in-flight runs with log paths and
   completion lines, branch tip; next actions). It is TRACKED: commit it
   on your branch — main's copy updates when main merges.
3. Commit everything; never leave the kit worktree dirty across a pause
   without saying so in wake.md. Release the Mac suite lock if held.
4. Tell main you are pausing (branch tip, anything still running on a
   box).
5. `CronDelete` the heartbeat; `TaskStop` every delivered lane; kill
   watcher scripts with nothing left to watch.
