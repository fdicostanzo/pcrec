# Lane o42 brief — [OPT-4.2] (preserved for relaunch)

PRESERVED 2026-08-31 (forty-eighth session close): the lane was
launched, oriented, and PARKED on Frank's shutdown instruction ~20
minutes in. Branch `lane/o42` carries any WIP; `o42_log.md` (in the
worktree / branch, if the lane got that far) is its resume note. AT
RELAUNCH: re-issue this brief to a fresh sonnet agent, REPLACE the
"BOX HOLD" section with the box state of that day, and have the agent
read `o42_log.md` first if it exists. The lane-self-keepalive-cron
instruction rides every brief. Original brief follows.

---

You are lane **o42** for pcrec (ahead-of-time PCRE→C compiler,
/home/duxevents/pcrec), implementing plan row **[OPT-4.2] — extend the
nullability decline to every prefilter rung**. The manager (pcrecdev1)
reviews and merges; you deliver a committed branch.

## SCOPE MANDATE (restated from CLAUDE.md, mandatory)
Touch ONLY /home/duxevents/pcrec — and for writes, ONLY your worktree
under worktrees/. Never /home/duxevents/pcrec-bench, never any other
directory or repo. Session-temporary files go in your session
scratchpad, never committed.

## BOX HOLD [STALE — re-write at relaunch]
Same shape as w12_brief.md's hold section, keyed on
`worktrees/o42.lift`.

## Setup
`git -C /home/duxevents/pcrec worktree add worktrees/o42 -b lane/o42`.
Use absolute paths / `git -C`.

## Charter
Read the **[OPT-4.2]** row in `docs/dev/plan.md` (near line 1672)
FIRST — it is the charter. Summary: today
`fit.prefilter_declined_nullable` requires `collapse_reason != CR_NONE`,
so an ORDINARY hybrid whose EXACT language is nullable still builds a
prefilter — a scan that can never dismiss a position (bench-measured
1.2-9.9x loss on that shape). The general form: decline the prefilter
on EVERY rung whenever the exact language is nullable. The affected
population GREW when [OPT-5] landed: `(a|b){0,30000}`-family patterns
now compile into exactly this config (hybrid/exact/nullable, 34,522 B
measured).

## Design constraints PINNED BY THE MANAGER (do not deviate without asking)
1. The rungless decline gets **its own new ESEL value** — do NOT reuse
   `ESEL_DECLINED_NULLABLE` (rung-scoped) and do NOT silently change
   internal.h's documented invariant (`>= ESEL_OVERFLOWED_DFA` implies
   a state-cap overflow). Place the new value so that invariant stays
   TRUE, and extend the invariant comment to state the placement
   explicitly.
2. General mechanism, not a special case: one nullability predicate
   feeding both the existing rung-scoped decline and the new rungless
   one — if the existing predicate generalizes cleanly, refactor to one
   source of truth rather than duplicating.
3. Registry legs for the new value; D80 spec hunk in the SAME change
   (grep docs/spec/ for `RX_ENGINE_SEL` / `sel=` to find the owning
   spec file and mirror how [OPT-4.1]'s value was documented).
4. abi ritual: mirror [OPT-4.1]'s precedent — check whether that
   landing bumped abi (git log/blame on `src/gen/emit_dfa.c`'s `.abi`
   and decisions.md D76). If your change moves the emitted stamp
   surface the same way, it is ONE abi bump written as **13→14** in
   your branch (final number assigned by the manager at merge). D76's
   four sites: emit_dfa.c `.abi`; tests/codegen/run_codegen_tests.sh
   [DD-14.FB] §10.4; docs/spec/match_api.md §6's "abi is N" sentence;
   the identity gate's (B) FILEPIN re-pin. If [OPT-4.1] did NOT bump
   (stamp VALUES vs stamp SCAFFOLDING may differ), record the
   precedent in your report and follow it.
5. The `tests/resource` **[OPT-4.2 tripwire]** cell was written to flip
   when this row lands — read its comment and flip it to pin the NEW
   behavior (loud and dated).
6. New test expectations oracle-verified (python3 `re` base tier).
   Answer-identity: the decline changes WHICH artifact is built, never
   what it answers — witnesses must show identical match answers with
   and without the decline (deny/force flags exist per axis; see
   `make test-axes` docs in docs/testing.md).

## Also deliver
- Witnesses: the `(a|b){0,30000}` family declines its prefilter (stamp
  movement pinned); a pre-existing VM-chosen nullable pattern's stamp
  movement; a NON-nullable hybrid unchanged (control).
- A corpus stamp-movement sweep (builds allowed only after the
  manager's hold lifts): which patterns' `sel=`/prefilter stamps move;
  counts + examples in the report. The artifact-size log will move —
  expected; the manager handles the ratchet diff at merge
  (`git checkout docs/dev/artifact_size_log.tsv` after any corpus run).
- A mech sabotage row proposal proving the new decline is tested:
  **use id S216** (assigned to this lane). mech measures COMMITTED HEAD
  only — commit before any solo mech run.
- CLAUDE.md updates for any directory whose files change role.
- Report note: the bench re-measures its cls-* hybrid cells after this
  lands (their 1.2-9.9x loss is the predicted WIN) — the manager sends
  that inbox item.

## Process rules
Identical to w12_brief.md's "Process rules" section (WIP commits;
gnutimeout; setsid + fast-exit launcher + PID file for >10 min runs;
kill by PID only; never edit a running script; one heavy suite at a
time; self-keepalive cron when idle; D26).

## Deliverable
Committed branch `lane/o42` + `docs/dev/lanes/o42_report.md`: what
landed, the stamp-movement sweep numbers, witness/tripwire/sabotage
results, the [OPT-4.1] abi precedent found and followed, open items.
Do NOT merge to main; do NOT push. Message the manager when delivered
or blocked.
