# Lane w12 brief — [DD-13b.W1.2] (preserved for relaunch)

PRESERVED 2026-08-31 (forty-eighth session close): the lane was launched,
oriented, and PARKED on Frank's shutdown instruction ~20 minutes in.
Branch `lane/w12` carries its WIP; `w12_log.md` (in the worktree /
branch) is the lane's own resume note. AT RELAUNCH: re-issue this brief
to a fresh opus agent, REPLACE the "BOX HOLD" section with the box state
of that day (the [B25] bench window it references is over), and have the
agent read `w12_log.md` first. The 22:05 probe amendment is dead. The
lane-self-keepalive-cron instruction (memory `pcrec-subagent-cache-warmth`)
now rides every brief. Original brief follows.

---

You are lane **w12** for pcrec (ahead-of-time PCRE→C compiler,
/home/duxevents/pcrec), implementing plan row **[DD-13b.W1.2] — targets,
rx_info.name, nentries, the abi ritual, H11**. The manager (pcrecdev1)
reviews and merges; you deliver a committed branch.

## SCOPE MANDATE (restated from CLAUDE.md, mandatory)
Touch ONLY /home/duxevents/pcrec — and for writes, ONLY your worktree
under worktrees/. Never /home/duxevents/pcrec-bench, never any other
directory, home config, or repo. Session-temporary files go in your
session scratchpad, never committed.

## BOX HOLD — IN FORCE AT LAUNCH [STALE — re-write at relaunch]
The sibling bench project is running a measurement window on this box
RIGHT NOW. Until the file `/home/duxevents/pcrec/worktrees/w12.lift`
exists, the following are FORBIDDEN BY SHAPE: `make` (any target), any
gcc/clang invocation, running `build/pcrec`, harness sections, any test
script, sweeps, background jobs — anything multi-process or CPU-bound.
ALLOWED: reading files, writing/editing files in your worktree, `git`
operations (worktree add, add, WIP commits). Check for the .lift file
between work units. Your FIRST WIP commit message must ack the hold.
After lift: builds allowed; `export PROCS=4` for any harness suite; run
TARGETED sections only (never full `make test`/san/mech — the manager's
battery covers those); validation runs go ASYNC (background, poll the
log artifact), never blocking foreground.

## Setup
`git -C /home/duxevents/pcrec worktree add worktrees/w12 -b lane/w12`
(from main). Work there with absolute paths or `git -C` (a `cd` in a
compound command persists to its tail).

## Read, in this order (all paths relative to the worktree)
1. `docs/design/dd13_format/w1_impl.md` — §0.2 (design in one
   paragraph), §1.2 (file by file), §1.5 (`config`, `target`, output
   naming), §1.6 (`rx_info.name`, `nentries`, the abi's FOUR sites),
   §1.7 (H11 — run.sh's target build path), §1.8, the spec-delta table
   around line 1807 (rows S9, S11), and §5's **[DD-13b.W1.2]**
   paragraph (~line 1911) — that paragraph IS your charter and
   acceptance bar.
2. The landed W1.1 code (git log for the lane/w1 merge; the head
   parser/composer entry points it added under src/ and cli/, and
   `tests/harness/run.sh`).
3. `docs/spec/match_api.md` §6 and `docs/spec/cli.md` (your D80 spec
   hunks land there).
4. `docs/dev/decisions.md` D76 (abi ritual), D80 (spec-in-same-change),
   D87 as referenced.

## STALENESS CORRECTION (important — the manager's note)
w1_impl.md predates [OPT-5]'s landing: **abi is ALREADY 13** (the scan
edge bumped it; pin a7e0bdf). Your change (rx_info.name + nentries =
new emitted scaffolding) is ONE further abi bump — write it as
**13→14** in your branch. The FINAL number is assigned by the manager
at merge time (other lanes also carry bumps; merges serialize). D76's
FOUR sites all move in your one change: (1) `src/gen/emit_dfa.c`'s
`.abi`; (2) `tests/codegen/run_codegen_tests.sh`'s [DD-14.FB] §10.4
expectation; (3) `docs/spec/match_api.md` §6's "abi is N" sentence;
(4) the identity gate's (B) pin — re-pinned to this step's last src
commit (see `run_recursion_identity.sh` / the FILEPIN mechanism).

## Build (from §5's charter paragraph)
`target … [with]` grammar; `config` composition and `from`; the output
naming rule (§1.5); F11's `rx_info.name` + `nentries`; F13's
prefix-taking driver; run.sh's target build path (H11). New CLI surface
per S11 (`--source`, `--target`, `--lib-path` as assigned to W1.2).
D80: the cli.md and match_api.md spec hunks travel in the SAME change.
Update every owning directory CLAUDE.md whose files change role.

## Acceptance (verify after lift, record results in your report)
- N targets → N artifacts, N prefixes, one `rx_info.name`.
- §6.3's three-config file compiles three ways and the three agree on
  the block's cases.
- abi 14 at all four sites; identity gate (A) byte-identical, (B)
  re-pinned.
- F9's `.name` assertion over the corpus's artifacts.
- `make test-codegen` green (PROCS=4, async).
- `make strict` clean.
- Test expectations oracle-verified (python3 `re` base tier) where new
  cells are written.
- D26 tiering: do not gold-plate diagnostic wording.

## Process rules (mandatory, from measured incidents)
- WIP-commit incrementally at every stage boundary — the watchdog's
  liveness signal; a death then strands minutes, not hours.
- `gnutimeout N cmd` on every command of uncertain run length (this
  box's bare `timeout` is uutils, ~105 ms wall per call; test scripts
  use `tests/lib/timeout_bin.sh` → `"$TIMEOUT_BIN"`).
- Runs that could exceed 10 min: `setsid nohup … < /dev/null &` + PID
  file — and the LAUNCHER command must EXIT FAST (scrape the PID in a
  SEPARATE later command: the process with sid==pid AND ppid==1,
  cwd-verified). `run_in_background` has a 10-min cap.
- Kill by PID only (`scripts/safekill PID`); NEVER `pkill -f`/`pgrep -f`.
- Never edit a shell script that is currently executing.
- mech measures COMMITTED HEAD only — never solo-run uncommitted
  sabotage/row edits.
- One heavy suite on the box at a time; if in doubt, ask the manager
  before starting anything heavy.
- If you need to go idle, create your OWN keepalive cron (~30 min,
  off-minute) whose tick doubles as your hold/rulings-file poll; delete
  it when active or delivered.

## Deliverable
Committed branch `lane/w12` + `docs/dev/lanes/w12_report.md` in the
worktree: what landed where, acceptance results with numbers, open
items, and anything the manager must decide. Do NOT merge to main; do
NOT push. Message the manager when delivered or blocked.
