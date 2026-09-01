# Lane cc brief — [CC-CLANG] steps 1+2 (preserved for relaunch)

PRESERVED 2026-08-31 (forty-eighth session close): the lane was
launched, oriented, and PARKED on Frank's shutdown instruction ~20
minutes in. Branch `lane/cc` carries its WIP; `cc_log.md` (in the
worktree / branch) is the lane's own resume note. AT RELAUNCH: re-issue
this brief to a fresh sonnet agent, REPLACE the "BOX HOLD" section with
the box state of that day, and have the agent read `cc_log.md` first.
The lane-self-keepalive-cron instruction rides every brief. Original
brief follows.

---

You are lane **cc** for pcrec (ahead-of-time PCRE→C compiler,
/home/duxevents/pcrec), implementing plan row **[CC-CLANG]** steps 1
and 2. The manager (pcrecdev1) reviews and merges; you deliver a
committed branch.

## SCOPE MANDATE (restated from CLAUDE.md, mandatory)
Touch ONLY /home/duxevents/pcrec — and for writes, ONLY your worktree
under worktrees/. Never /home/duxevents/pcrec-bench, never any other
directory or repo. Session-temporary files go in your session
scratchpad, never committed.

## BOX HOLD [STALE — re-write at relaunch]
Same shape as w12_brief.md's hold section, keyed on
`worktrees/cc.lift`.

## Setup
`git -C /home/duxevents/pcrec worktree add worktrees/cc -b lane/cc`.
Use absolute paths / `git -C` (a `cd` in a compound command persists
to its tail).

## Charter
Read the **[CC-CLANG]** row in `docs/dev/plan.md` (near line 1338)
FIRST — it records the manager's probe results and IS the charter.
Summary: clang 21.1.8 compiles and agrees on DFA, backtracking-VM, and
recursion artifacts. The ONE real incompatibility: a FRAMELESS VM
artifact (counter rung, no push sites — e.g. `[a-z]{0,4096}`
--engine=vm) still emits the generic resume dispatch
`goto *run->resume_stack[i].resume_label` with no address-of-label
expression in the function — gcc accepts, clang errors. Also cosmetic:
`__attribute__((noclone))` unknown to clang.

**Step 1 (the code change):**
- Emit the resume dispatch ONLY when a push site exists — prefer the
  structurally honest form (don't emit dead dispatch code); read the VM
  emitter to find the cleanest condition. A dummy address-of-label is
  the fallback only if suppression is structurally hard — say which you
  chose and why in the report.
- Guard `noclone` for clang in the EMITTED text via a general mechanism
  (`#if defined(__has_attribute)`-style feature detection, not a
  clang-name special case) — per the general-mechanisms rule.
- BOTH are emitted-scaffolding changes = **ONE abi bump**, written as
  **13→14** in your branch (final number assigned by the manager at
  merge — other lanes also carry bumps). D76's FOUR sites in the same
  change: (1) `src/gen/emit_dfa.c`'s `.abi`; (2)
  `tests/codegen/run_codegen_tests.sh`'s [DD-14.FB] §10.4 expectation;
  (3) `docs/spec/match_api.md` §6's "abi is N" sentence; (4) the
  identity gate's (B) pin (`run_recursion_identity.sh` FILEPIN —
  re-pin to your step's last src commit).
- D80: if any caller-observable surface moves, the docs/spec/ hunk
  travels in the same change.

**Step 2 (the sweep mechanism):**
- An opt-in corpus sweep with clang as the COMPILEE axis:
  `make test CLANGGEN=1`-shaped, riding the GENCFLAGS/`gen_run` hook
  precedent from SAN-1 — read `docs/testing.md` "Sanitizer + lint
  battery" and `tests/harness` for how LINTGEN=1 rides the
  generated-code compile pass. Writes nothing to build/.
- Document it in docs/testing.md (same change).
- A one-time `make CC=clang` survey of the COMPILER itself: record
  findings in your report only (gcc stays the target, D2) — run async,
  not alongside other heavy work.

## Validation (builds allowed only when the manager's hold is lifted)
- Probe: the original failing shape `[a-z]{0,4096}` --engine=vm
  compiles clean under clang; the other three probed artifact shapes
  still agree gcc-vs-clang cell-for-cell.
- Frameless artifacts under GCC remain answer-identical (the
  suppressed dispatch must not change behavior) — spot-check a few
  frameless VM cells gcc-side.
- `make test-codegen` green, `make strict` clean (PROCS=4, async).
- Small-scale CLANGGEN validation: ONE targeted section with CLANGGEN=1
  (PROCS=4). Do NOT run the FULL CLANGGEN sweep — the manager schedules
  that (battery-scale). Report the mechanism ready + the section result.

## Process rules
Identical to w12_brief.md's "Process rules" section (WIP commits;
gnutimeout; setsid + fast-exit launcher + PID file for >10 min runs;
kill by PID only; never edit a running script; mech measures COMMITTED
HEAD only; one heavy suite at a time; self-keepalive cron when idle;
D26 — don't gold-plate diagnostic wording).

## Deliverable
Committed branch `lane/cc` + `docs/dev/lanes/cc_report.md`: what
landed, the probe/validation numbers, the CC=clang survey findings,
open items. Do NOT merge to main; do NOT push. Message the manager
when delivered or blocked.
