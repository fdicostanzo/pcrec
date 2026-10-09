# memfn wake — kit session hand-off (rewritten 2026-10-09 ~19:20, reset by Frank's ask)

This is the orientation file for the kit session. Run it as
`/pcrec-memfn-manager` (`.claude/skills/pcrec-memfn-manager/SKILL.md`;
its §1 is the wake order). It is rewritten at every pause and holds the
current state. The history is `journal.md`.

**This copy lives on lane/memfn-r13** (the newest). lane/memfn-vmlazy's copy
is older; main's copy is older still. It was written here because slot17 was
validating lane/memfn-vmlazy's tip, and mech archives HEAD, so no commit
could go there.

---

## 1. Who you are and where you work

- You are the pcrec-memory-functions kit manager. This session is `pcrecdev3`.
  The pcrec manager ("main") is `pcrecdev1`. It files requests in
  `requests.md`; you answer in `responses.md`, and you are that file's only
  writer.
- **Box:** the Linux dev box `pcrec@192.168.1.17`, repo
  `/home/pcrec/projects/pcrec`. It has 16 threads, gcc 15.2 and libpcre2
  10.46. Use `gnutimeout`, not bare `timeout`.
- **Commits:** use
  `git -c user.name="Frank DiCostanzo" -c user.email=frank@dicostanzo.com`.
- **Branches:** one worktree per unit. Never merge to main, never push, never
  `cd` (use `git -C` and absolute paths). Scratch lives in
  `worktrees/memfn-slot/`. Prune with `scripts/wtprune --apply NAME`.

## 2. Read, in this order

1. `memfn/CLAUDE.md`.
2. `requests.md`, then `responses.md` (the newest notices, on both kit
   branches).
3. The journal tail (this branch).
4. `docs/dev/lanes/r13_report.md` (§3 deviations, §8 OWED) and
   `docs/dev/lanes/vmlmerge_report.md` (with its vmlrid section).
5. integration.md §R4.9, including the `[D157]` marks.

## 3. Box, slot and cron rules

- Reset above **35% context**.
- **One heavy suite at a time** across both sessions. ASK main for the GO
  before every slot, and ping at DONE with the full `== mech run COMPLETE`
  trailer.
- **Light work needs no slot:** `make -j`, strict, `test-memfn-*` and
  codegen pinned to `taskset -c 12-15`, G2 `--quick`, and single mech rows.
- **Slot template:** `worktrees/memfn-slot/slot17/run.sh`. It writes DONE
  only after mech completes, FAILED otherwise.
- **Heartbeat cron** `17,47 * * * *`, recreated at wake. It doubles as the
  DEADLOCK CHECK: only while you wait on a peer for a specific thing, NAME
  that thing and ASK its status (Frank's format). A check you receive gets a
  one-line ack plus status.
- **Lanes miss addenda while they run.** Send a ruling as a file
  (`worktrees/<lane>/docs/dev/lanes/<lane>_rulings.md`) plus a message, and
  verify it in the diff.

## 4. Current state (2026-10-09 19:20)

- **R-12 VMLAZY: slot17 RUNNING (detached, setsid).**
  - Branch lane/memfn-vmlazy @ 1bb49dee: main 631771b7 (RQ-3, abi 71)
    merged in, VMLAZY at abi 72, N7U retired. The recursion-identity gate
    is 18/0 with the 8th exception, `lazy_prefix_rewrite` (kit ruling R1).
  - Log: `worktrees/memfn-slot/slot17/run.log`; verdict lines in
    `verdict.txt`; `DONE` or `FAILED` beside them.
  - Stages: build, strict, sabanchor (all green at 19:14), recid, the lazy
    G1 census at 71:72, emit_sweep `--variant all` vs 631771b7, N2, G2 full,
    make test (perfrun), and mech (26 rows, PROCS=4).
  - **On DONE:**
    1. Read every column of verdict.txt and the COMPLETE trailer.
    2. VARIANTS: main says the base already carries its re-pin, so it should
       read clean. If a lowsize floor moved, re-pin by measurement.
       `(a{2,3}?){2,3}` drops its prefilter at the lowered cap; that is
       expected.
    3. If the census mover set differs from
       `docs/design/memfn/probes/vmlazy/out/movers.tsv`, re-run
       lazy_timing.py.
    4. Post `[responses] done: R-12` (branch, report, slot17 log + verdict)
       on lane/memfn-vmlazy, then SendMessage main: "DONE + trailer, please
       review/merge".
  - **On FAILED:** start a TRIAGE lane before you read the logs yourself.
- **R-13 batch 1: BUILT, CANDIDATE**, lane/memfn-r13 @ ae7b6a22 (this
  branch).
  - `vrun-w16`/`vrun-w32` filter on KA only. SIMD-off has 0 movers, so there
    is no abi event.
  - Light suites green; solo mech S716-S730 plus 5 re-aims, 20/20 clean.
  - Q-R13-1..7 ruled with the lane's leanings (responses notice 056545df).
  - D157 is recorded: RQ-2 is a ranked rarity ARRAY (`rank_n`/`rank_pos`/
    `rank_ppm`), and the distance rule is the KIT's. Do NOT presume a rule:
    the choice is owed, D149-labelled.
  - **NEXT, when main pings that RQ-2 merged:**
    1. Merge main into lane/memfn-r13, ALONE. The MF_SITE_ABI number goes to
       whichever lands first; renumber otherwise.
    2. Brief an opus lane to design and build the kit's use of `rank_pos`
       in `vrun.c:cmask`. The distance rule is measured, derived, or
       labelled UNMEASURED DEFAULT, and only `-fmemfn-simd` bytes move.
    3. Run the heavy slot from r13_report §8: identity gate on every arm, N2,
       G2 full, make test, the remaining mech rows.
    4. Then the RQ-4 tier-U timing slot, which main grants, and RQ-5.
  - **Frank asked for the first SIMD-on vs SIMD-off directional reading**
    when it exists. It comes from the RQ-4 timing run, after the `rank_pos`
    lane. Report it to him plainly.
- **Waiting on main:** RQ-2 (lane rq2 is building it; main pings on merge),
  and main's review/merge of R-12 after slot17.
- **Owed to main (posted):** decisions.md D58 add. 2's revisit close (N7U).
- **Unscheduled kit follow-ups:** Q-G2M6-1..9, [MEMFN-CI-ASCII], and a
  D27-blinded G2 lane for the SIMD contract after RQ-2 (Q-R13-4).

**Worktrees:**
- vmlazy (slot17 running; do not commit there until DONE)
- r13 (SIMD branch)
- vmlmerge, n7uret and r13doc (merged into kit branches; prune after main
  merges)
- g2u + g2u-cell (keep), memfn (lane/memfn-skill), memfn-slot (scratch),
  r4h, m4

## 5. Next actions on wake

1. Recreate the heartbeat cron and run ListAgents. Read requests.md for new
   items.
2. Check slot17: `ls worktrees/memfn-slot/slot17/{DONE,FAILED}` and
   `cat verdict.txt`. If it is still running, arm a script watcher on DONE
   or FAILED.
3. Work §4 in order.
