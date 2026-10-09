# memfn wake — kit session hand-off (rewritten 2026-10-09 ~16:50, reset at 53% context)

This is the orientation file for the kit session. Run it as
`/pcrec-memfn-manager` (`.claude/skills/pcrec-memfn-manager/SKILL.md`;
its §1 is the wake order). It is rewritten at every pause and holds the
current state. The history is `journal.md`.

**This copy lives on lane/memfn-vmlazy** (newer than main's). Main's
`memfn/docs/wake.md` is the R-11 copy.

---

## 1. Who you are and where you work

- You are the pcrec-memory-functions kit manager. The pcrec manager
  ("main", session name `pcrecdev1`) files requests in `requests.md`. You
  answer in `responses.md` and are its only writer. This session's name is
  `pcrecdev3`.
- **Box:** the Linux dev box `pcrec@192.168.1.17`. The repo is
  `/home/pcrec/projects/pcrec`. It has 16 threads, gcc 15.2, libpcre2
  10.46 and no clang.
  - Bare `timeout` is uutils; use `gnutimeout`.
  - Commit with
    `git -c user.name="Frank DiCostanzo" -c user.email=frank@dicostanzo.com`.
- **Unit branches.** There is one worktree and branch per unit, cut from
  main. Never merge to main, never push, never `cd`. Use `git -C` and
  absolute paths.
- **Scratch:** `worktrees/memfn-slot/` (gitignored).
- **Pruning:** `scripts/wtprune --apply NAME`. It refuses a worktree with
  untracked `.scratch/` lane logs or a live cwd.

## 2. Read, in this order

1. `memfn/CLAUDE.md`.
2. `memfn/docs/requests.md`, then `responses.md` (the newest notices).
3. The journal tail (this branch).
4. `docs/dev/lanes/vmlazy_report.md` (§8 is its slot chain) and
   `r12scope_report.md`.
5. integration.md §R4.9.7 before R-13.

## 3. Box, slot and cron rules

- **Reset rule:** above **35% context**, look for a reset point (Frank,
  2026-10-09; memory `pcrec-keep-lanes-full`).
- One heavy suite at a time across both sessions.
  - **ASK main for the GO before every slot.** Ping at DONE with the FULL
    `== mech run COMPLETE` trailer.
- **Light work needs no slot:** `make -j4`, strict, `test-memfn-*` and
  codegen pinned to `taskset -c 12-15`, G2 `--quick`, and single mech rows.
- **Slot template:** `worktrees/memfn-slot/slot16/run.sh`.
  - It writes DONE only after the LAST stage completes, FAILED otherwise.
    Main's sequencer keys on DONE.
  - Mech is ONE `PROCS=4` invocation.
  - A verdict reads EVERY column of the COMPLETE trailer.
  - Build row lists from ids, never paths.
- **Heartbeat cron:** `17,47 * * * *`, which doubles as the DEADLOCK CHECK.
  Message a peer ONLY while you wait on that peer for a specific thing, and
  never otherwise. Recreate it at wake.

## 4. Current state (2026-10-09 ~16:50)

- **R-9, R-10, R-11 and R-12 step 1: done and merged.**
- **R-12 VMLAZY: BUILT, awaiting its slot** (lane/memfn-vmlazy @ 36f05045).
  - Commits: normalize 7106b370 (pcrec abi 70 -> 72; main's number, with
    RQ-3 = 71 landing first), zero-mover REPLACE 08bda492, VALID pending
    row + vocab re-sweep df808ef8.
  - G1: movers = exactly the lazy artifacts; 0 OTHER / ASYMMETRIC / entry
    shape; timing null over 222 patterns. Light suites green; S706-S710 and
    S712 DETECTED.
  - **In flight at pause:** the lane's chain2, DETACHED and reparented, so
    it survives the reset. G2 quick passed; 6 zero-mover sweep arms
    remain. Done when `CHAIN2 COMPLETE` appears in
    `worktrees/vmlazy/.scratch/logs/c2/summary.txt`. Judge
    `.scratch/logs/sweep/<arm>.log` by `movers=0 asymmetric=0` on every
    stream.
  - **TODO on wake, in order:**
    1. Read chain2's verdict.
    2. TaskStop lane `vmlazy` if it is still listed. Its chain is
       reparented, so stopping it is safe.
    3. Commit **N7U's retirement** on this branch: delete the N7U manifest
       row (C17 floor literal and its readers by grep, S512's POP), and
       write D147 addendum 14's rule into integration.md §R4.3.4 beside
       Q-R10-11. The rule: a walk whose unit is the encoding's character (a
       decode on either operand) belongs to the encoding; its byte-domain
       sub-loops are kit sites. The kit is encoding-blind. A sabotage id is
       available from S711 if one is needed. Then run light checks.
    4. When RQ-3 has landed (abi 71), merge main ALONE. S693's AFTER
       becomes 71 and the other readers get re-derived (whichever lands
       second re-pins). Re-pin FILEPIN.
    5. Write slot17 from vmlazy_report §8 (template slot16), then ASK main
       for the GO.
- **R-13 (batch 1: vrun-w32/w16 CANDIDATE, S716-S730): ACKED, waiting on
  RQ-3.** Main's NEXT session pings when RQ-3 merges. Build from main after
  that:
  - the `mf_sink` `simd_open`/`simd_close` members, wired in
    `pcrec_memfn_sink` (pcrec's half is `pcrec_memfn_sink_simd_open/_close`);
  - per-row bounds in `tests/memfn/simd_bounds.tsv`
    (`make test-memfn-guarded`);
  - each row's `--memfn=no-NAME` deny plus a pcrec cli case;
  - C18's four legs;
  - the identity gate on every arm, with both layers read.

  RQ-2 is needed for the sweeps, not the build.
- **Kit follow-ups, unscheduled:** Q-G2M6-1..9 and [MEMFN-CI-ASCII] (main's
  filed row).

**Worktrees:** vmlazy (active), g2u + g2u-cell (keep; main re-created g2u at
2dc64da6), memfn (lane/memfn-skill, merged), memfn-slot (scratch), r4h, m4.
r4e0, r4e0b, w5fix and r12 hold only `.scratch/` lane logs; delete those
logs and prune when convenient.

## 5. Next actions on wake

1. Recreate the heartbeat cron and run ListAgents. Read requests.md for new
   items.
2. Work §4's VMLAZY TODO list.
3. When main pings that RQ-3 has merged, start R-13 (opus lane, light runs
   only), in 2:1 shape alongside the migration thread.
