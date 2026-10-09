# memfn wake — kit session hand-off (rewritten 2026-10-09 ~15:45)

This is the orientation file for the kit session. Run it as
`/pcrec-memfn-manager` (`.claude/skills/pcrec-memfn-manager/SKILL.md`;
its §1 is the wake order). It is rewritten at every pause and holds the
current state. The history is `journal.md`.

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
  - No git identity is configured. Commit with
    `git -c user.name="Frank DiCostanzo" -c user.email=frank@dicostanzo.com`.
- **Unit branches.** There is one branch per delivered unit, cut from main
  in its own worktree (e.g. `worktrees/r4e0b` on `lane/memfn-r4e0b`).
  - `worktrees/memfn` is the old kit home, now on `lane/memfn-skill`
    (merged).
  - Never merge to main and never push.
  - Never `cd`. Use `git -C` and absolute paths; a top-level `cd` moves
    the session cwd.
- **Scratch:** `worktrees/memfn-slot/` (gitignored).
- **Pruning:** `scripts/wtprune --apply NAME`.

## 2. Read, in this order

1. `memfn/CLAUDE.md`.
2. `memfn/docs/requests.md`, then `responses.md` (the newest `done:`
   entries and notices).
3. The tail of `memfn/docs/journal.md`.
4. `docs/design/memfn/integration.md` §R4.9, the SIMD layer's design
   (rev 4.9, R-9 done).
5. BOILERPLATE before briefing, coding_guide before C, learnings §3 before
   a check.

## 3. Box, slot and cron rules (this box)

- One heavy suite at a time across BOTH sessions.
  - **ASK main for the GO before every slot** (2026-10-09: slot16 was
    launched without one).
  - Ping main at DONE with the FULL `== mech run COMPLETE` trailer.
- **Light work needs no slot:**
  - `make -j4` and `make strict`;
  - single compiles;
  - `test-memfn-*` and `test-codegen`, pinned to `taskset -c 12-15`;
  - G2 `--quick`;
  - single mech rows.
- **Slot script pattern:** `worktrees/memfn-slot/slot16/run.sh` is the
  current template.
  - Launch it detached with `setsid nohup`.
  - It writes DONE ONLY after the last stage completes, and FAILED
    otherwise. Main's sequencer keys on DONE.
  - Mech is ONE `PROCS=4 run_sabotage_matrix.sh <rows>` ([TT-MECHPAR]).
  - A verdict reads EVERY column of the COMPLETE trailer (unexpected,
    undetected, unreached, anomalies) against the rows' declared
    expectations.
  - Build row lists from `SAB_ID`-style ids, never from raw paths.
- Restore `docs/dev/artifact_size_log.tsv` after `make test`, and never
  commit it.
- **Heartbeat cron:** `17,47 * * * *`. It doubles as the DEADLOCK CHECK
  (Frank, 2026-10-09). A tick messages a peer ONLY while you wait on that
  peer for a specific thing. Never ping a session you aren't waiting on.
  Recreate it at wake and delete it at close.

## 4. Current state (2026-10-09 ~15:45)

- **Done and merged today:** R-9 (SIMD design), R-10/M6 (VMSTRIDE, plus
  the W5 alloc-witness fix and the `memfndeleg` mech arm for S683), and
  R-11 step R4e′.0 (the `fn_rows[]` seam plus one `kit_walk`).
- **R-11 step R4e′.0b: DONE, awaiting main's merge.** It is on
  lane/memfn-r4e0b @ 39ed9cca: the routing, pcrec abi 69 -> 70.
  - slot16 is green: routing census 0 OTHER/ASYMMETRIC, N2 clean, G2 full
    192.65M/0, make test green, mech 80 rows with 0 unexpected and 0
    anomalies.
  - The `done:` is posted in responses.md.
  - R-11 is COMPLETE when main merges. Then prune worktrees r4e0b and
    r4e0.
- **Batch 1** (`vrun-w32`/`vrun-w16`, the first SIMD rows) is NOT filed
  yet. Main files it after RQ-1..3:
  - RQ-1 `--memfn=` carrier: LANDED (clibundle). The first options.def row
    must add a pcrec cli case.
  - RQ-3: lane/rq3, abi 71, main's. The kit must add
    `simd_open`/`simd_close` to `mf_sink`, wire them in
    `pcrec_memfn_sink` (2 lines), bracket every SIMD row's guarded text,
    and declare per-row bounds in `tests/memfn/simd_bounds.tsv`, which
    `make test-memfn-guarded` checks.
  - RQ-2 `pcrec_find_pick2`/`plan_pos2`: main's, status unknown.
- **Kit follow-ups, unscheduled:** Q-G2M6-1..9 (memfn/tests/G2M6_REPORT.md)
  are contract-clarity items, not defects. The leading ones are Q-G2M6-3
  (`peek` required at W > 1 although it is unused) and Q-G2M6-4 (EXCLUDED
  on a strided ADVANCE).
- **Open since last night, discussion only:** Frank asked for SIMD
  priority by site-category frequency × winnable margin. No population
  census exists yet.

**Worktrees:** r4e0b and r4e0 (prune after main merges), g2u + g2u-cell
(keep, the D27 cell), memfn (on lane/memfn-skill), w5fix and m6 (merged;
prune), r4h (untracked r4h_rulings.md: check before pruning), m4, r9d
(merged; prune).

## 5. Next actions on wake

1. Recreate the heartbeat cron and run ListAgents. Read requests.md for
   new items (batch 1 may be filed).
2. Confirm main merged lane/memfn-r4e0b; then prune r4e0b, r4e0, m6, w5fix
   and r9d with wtprune.
3. When batch 1 is filed: ack it, then brief per §R4.9.7. The sink ops
   come first, then the rows, with their deny rows plus cli cases, and
   both layers read.
