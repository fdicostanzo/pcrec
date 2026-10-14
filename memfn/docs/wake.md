# memfn wake — kit session hand-off (rewritten 2026-10-13 ~13:30, session close)

This is the kit session's orientation file. Run it as `/pcrec-memfn-manager`;
its §1 is the wake order. It is rewritten at every pause and holds the current
state. The history is `journal.md`.

## 1. Who you are and where you work

- You are the pcrec-memory-functions kit manager (`pcrecdev3`). The pcrec
  manager is "main" (`pcrecdev1`; run ListAgents). Stale sessions can share a
  name; if two rows do, address by `name [ref]`.
- Main files requests in `requests.md`. You answer in `responses.md` and are
  its only writer.
- **Box:** the Linux dev box, repo `/home/pcrec/projects/pcrec`. Use
  `gnutimeout` (bare `timeout` is uutils). There is no git identity, so commit
  with `git -c user.name="Frank DiCostanzo" -c user.email=frank@dicostanzo.com`.
- **The kit worktree is `worktrees/memfn-r17`, on lane/memfn-r17.**
- Never merge to main, never push, and never `cd`: use `git -C` and absolute
  paths. A `cd` moves the session; it happened twice in the last session.
- **Scratch:** `worktrees/memfn-slot/` (one dir per slot).

## 2. Read, in this order

1. `memfn/CLAUDE.md`.
2. `requests.md` / `responses.md` (newest).
3. The tail of `journal.md` (the 2026-10-13 entries).
4. `docs/dev/lanes/r17loss_report.md` (on lane/r17loss), then
   `vecspike_report.md` (lane/vecspike) and `vecspike2_report.md`
   (lane/vecspike2).
5. `memfn/docs/ideas.md`, the 2026-10-12/13 entries (Frank's span, vector,
   batch and live-range ideas).
6. BOILERPLATE before briefing.

## 3. Box, slot and cron rules

- One heavy suite at a time across BOTH sessions. ASK main for the GO before
  each slot, and ping main with the verdict when it ends.
- Light work (make -j4, strict, single sections pinned `taskset -c 12-15`)
  needs no slot.
- A red stage gets a triage lane BEFORE you read its log.
- Running lanes miss mid-run messages. Put scope changes into a FRESH lane,
  and tell lanes to report ONLY to you (two lanes messaged main directly).
- **Discuss before launch** (Frank). Spikes Frank asks for are fine.
- Heartbeat cron `17,47 * * * *`. Recreate it at wake, delete it at close.
- Reading pcrec-bench: `git -C /home/pcrec/projects/pcrec-bench show <sha>:<path>`.

## 4. Current state

**NEXT ACTION: read the vecspike timing slot.** It is ARMED and starts by
itself.
- Main granted it by artifact (main closed too): the box is the kit's once
  `worktrees/b3tri/build/v/chain.log` shows `ALL_DONE` (expected around
  13:30-14:00 on 2026-10-13).
- `worktrees/memfn-slot/spike1/arm.sh` (detached, armed 13:25) waits for
  that line, then runs slot.sh. Its state is in `spike1/arm.status`:
  ARMED -> TRIGGER -> SLOT_EXIT.
- If arm.sh died (no TRIGGER after ALL_DONE), launch the slot by hand:
  `setsid nohup bash /home/pcrec/projects/pcrec/worktrees/memfn-slot/spike1/slot.sh >/dev/null 2>&1 </dev/null & disown`
- The NEW main session starts nothing heavy before the slot's end note. Post
  that note in responses.md (or message the new main) when SLOT_DONE appears.
  It runs vecspike's `time.sh` (1,549 rows, about 90 min), then vecspike2's
  `time2.sh` (288 rows, about 17 min), on CPU 14 with LAUNCHES=5.
- Progress goes to `spike1/slot.status`; it is finished at `SLOT_DONE`. Logs
  are `spike1/time.log` and `spike1/v2/time2.log`. Each time script ends with
  `time.sh: COMPLETE rows=N wall=...`.
- Read it against each report's predictions (vecspike §6, vecspike2's
  prediction list). Frank's ruling requires the kept vector's VALUE PER CELL
  at 8 B / SSE2 / AVX2, against the walk AND against the same width without
  it. Message main when the slot ends, then report to Frank.

**R-17 / R17-b: back with the kit.** Correct, but not a uniform win.
- slot25 (full chain) + slot25b (front half vs KREF2 = lane/kref2 2c597c35f):
  every red is explained and none is R17-b's. Unmerged fixes:
  - lane/s25alpha: alpha cell fix 365752ee0. It sits on lane/s25btip
    c62220fbe = s25tri's fallback-table fix b66529602 + s25b's
    `emit_sweep --movers-out` and r17b_movers changes.
  - lane/s25mech: S689 flip d6f24fc4b + the report.
  - lane/s25bv: the corrected variants judge dca28769c.
  - Main changed run_fallback_table.sh (now 146/0), so merging b66529602
    WILL conflict there; resolve to 146 plus the three rescued witnesses.
- ALPHA (slot25c/time.log): 62 WIN / 87 REGRESSION / 11 NULL.
  - Losses are 2-5 ns per use on near hits and dense subjects (up to +599 us
    per 1 MiB find-all pass on `[a-z]+\b`).
  - Find-all restarts cold: the state lives per rx_search call.
- **Frank's ruling, via main:** preserving the find vector across a find-all
  sequence is REQUIRED for SIMD find forms. pcrec owes the seam; the mechanism
  is under discussion (main leans to an artifact-owned find-all entry). Design
  against neither mechanism until it is settled.
- Frank's other points: try the serial head up to load alignment; `[a-z]+\b`
  should scan for `\W` (passed to main); the subjects are contrived; the
  multi-position class span is R-18's first non-literal client (no special
  case).
- Nothing is briefed for the R17-b redesign. Wait for the slot reading plus
  Frank and main.

**Delivered this session (main merges):** lane/memfn-g2pin @ 5ce6ea692 (the
G2 SIMD taskset pin) and lane/memfn-g2isa @ b09f95330 (the per-level CPU gate,
loud skips). Both are off main and posted in responses.md.

**Queued:** R-18 (the window search, D161; contract window_contract.md),
behind R-17; S871-S880 are reserved for it. The idea notes for R-18 and
[VM-CLSMASK] are in ideas.md 2026-10-12/13: one class-vector producer, batched
class requests (a multi-output cover), per-class live ranges, shift-or
alignment.

**Worktrees:**
- Keep: memfn-r17 (the kit), kref2, s25btip, s25alpha, s25mech, s25main,
  s25bv, vecspike, vecspike2, r17loss, g2pinm (lane/memfn-g2pin),
  g2isa (lane/memfn-g2isa), plus the r17* lane worktrees until R17-b lands.
- Prunable by main via wtprune once merged or abandoned: s25tri, s25trim,
  g2pin (lane/g2pin, superseded by lane/memfn-g2pin), and the stale ones
  named in earlier wakes.

## 5. Next actions on wake

1. Recreate the heartbeat cron and run ListAgents.
2. Check the slot: `cat worktrees/memfn-slot/spike1/arm.status spike1/slot.status`.
   - Still running: wait for SLOT_DONE, using a background waiter, not sleeps.
   - Never triggered: check chain.log for ALL_DONE, then launch slot.sh.
   - Done: read both logs against the predictions, report the kept vector's
     value per cell, and post the end note (responses.md + the new main).
3. With the reading in hand, discuss R17-b's redesign with Frank and main
   before briefing anything. Then merge the slot25 fix branches into the kit
   branch (git merge ALONE per branch; expect the fallback-table conflict).
