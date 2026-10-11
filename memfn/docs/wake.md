# memfn wake — kit session hand-off (rewritten 2026-10-11, R-16 staged)

This is the kit session's orientation file. Run it as `/pcrec-memfn-manager`;
its §1 is the wake order. It is rewritten at every pause and holds the
current state. The history is `journal.md`.

## 1. Who you are and where you work

- You are the pcrec-memory-functions kit manager, session `pcrecdev3`. The
  pcrec manager is "main" (`pcrecdev1`, and probably a FRESH session; run
  ListAgents). Old closed sessions can share a name. If ListAgents shows
  two rows with one name, address by `name [ref]` and say so to main.
- Main files requests in `requests.md`. You answer in `responses.md` and
  are its only writer.
- **Box:** the Linux dev box, repo `/home/pcrec/projects/pcrec`. Use
  `gnutimeout` (bare `timeout` is uutils). There is no git identity, so
  commit with `git -c user.name="Frank DiCostanzo" -c user.email=frank@dicostanzo.com`.
- Work one branch per unit, each in its own worktree. The kit worktree is
  `worktrees/memfn` (now on lane/memfn-r16). Never merge to main, never
  push, never `cd` (use `git -C` and absolute paths; a `cd` moves the
  session cwd).
- **Scratch:** `worktrees/memfn-slot/` (one dir per slot, plus kept reports).

## 2. Read, in this order

`memfn/CLAUDE.md`; `requests.md` / `responses.md` (newest); the tail of
`journal.md`; `docs/dev/lanes/r16b_report.md`; BOILERPLATE before briefing.

## 3. Box, slot and cron rules

- One heavy suite at a time across BOTH sessions. ASK main for the GO
  before each slot, and ping main at the end with the verdict.
- Light work (make -j4, strict, single sections pinned `taskset -c 12-15`)
  needs no slot.
- A red stage gets a triage lane BEFORE you read the log.
- Running lanes miss mid-run messages. Put changes in a FRESH lane.
- Heartbeat cron `17,47 * * * *`. Recreate it at wake, delete it at close.
- Restore `docs/dev/artifact_size_log.tsv` after make test (run.sh does it).

## 4. Current state (2026-10-11 evening)

- **On main (merged):** everything through R-15 and lane/memfn-ideas3.
- **R-16 (KB at w32 only, D147 add. 16): BUILT, light-green, WAITING ON
  THE SLOT.** lane/memfn-r16 @ f758c035 (plus this wake commit).
  - Lane r16b (closed): ops_of[] `npos` (1 at w16, 2 at w32). vrun_kb()
    returns no KB below 2. The deny is unchanged.
  - Re-pins: VRUN_W16_GUARDED_MAX 2400 (limits.md §8.3), G2 VSHAPE_FLOOR
    none 8, and simd_accept loses vrun-kb's w16 lines.
  - S815-S819 are all detected. SIMD-off has 0 movers, so no abi.
  - The slot21 D-F triage (dftri_report) is committed and folded into the
    ack. It is not R-16's rows, and nothing is built for it.
- **slot23 is staged:** `worktrees/memfn-slot/slot23/run.sh`.
  - Main's GO comes from the NEXT main session, after the rlhbuild chain,
    the rlhtri fix and the L1 merge (that session's first item).
  - BEFORE launching: `git -C worktrees/memfn merge main` ALONE, read it,
    `make strict`, commit. The script's ref is merge-base(HEAD, main),
    built in slot23/refsrc for the classifier.
  - Launch detached (setsid nohup ... > slot23/run.log). It ends with DONE
    or FAILED; verdict.txt is the summary.
  - Judges:
    - plain / start / variants sweeps: 0 artifact movers;
    - simd sweep: only vrun artifacts move (the classifier over EVERY
      pattern reports bad 0);
    - nokbsimd sweep: 0 movers;
    - G2 quick + full: 0 failed;
    - make test: no `*** [Makefile:N: test-` lines;
    - mech S815-S819 + S753: COMPLETE.
  - Hand main `slot23/variant_pins.py` (its thin-tag pins `(\p{Xwd})` and
    `((a)+)+`).
  - My calls (answer-free): no test-axes, no N2, no re-timing (journal).
- **After a green slot:** add the slot23 evidence to the report and a
  `done: R-16` with the tip, then SendMessage main.
- **Unscheduled / filed:** the span thread under [SPAN-ISEL] (a designed
  spike, opportunistic only); KB at w16 when KA is dense; the KB rare-KA
  hypothesis; pc16 nested checks; pcrec workload facts; memcasecmp;
  [VM-CLSMASK]; Q-G2M6-1..9; [MEMFN-CI-ASCII]; a D27 G2 pass for the SIMD
  contract.

**Worktrees:**
- Keep r16b until R-16 merges: slot23's notes cite it, though the
  classifier no longer needs its ref build.
- Keep g2u + g2u-cell.
- Merged, for main to prune via wtprune: r13, r14, r14b, r14p, r15, r15b,
  ideas2, ideas3.

## 5. Next actions on wake

1. Recreate the heartbeat cron, run ListAgents, and read requests.md for
   new items.
2. If main's GO has arrived (or the L1 merge is on main), merge main, run
   strict, and launch slot23 detached. Then watch it with a script, not with
   turns.
3. Otherwise idle on the heartbeat. The deadlock ping goes only to the
   CURRENT main, and only once its chain should be done.
