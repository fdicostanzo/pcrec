# memfn wake — kit session hand-off (rewritten 2026-10-10 ~00:30)

This is the orientation file for the kit session. Run it as
`/pcrec-memfn-manager` (`.claude/skills/pcrec-memfn-manager/SKILL.md`;
its §1 is the wake order). It is rewritten at every pause and holds the
current state. The history is `journal.md`.

## 1. Who you are and where you work

- You are the pcrec-memory-functions kit manager, session `pcrecdev3`.
  The pcrec manager is "main" (`pcrecdev1`, resetting 2026-10-10 ~00:30;
  a NEXT main session will message you). Main files requests in
  `requests.md`; you answer in `responses.md` and are its only writer.
- **Box:** the Linux dev box `pcrec@192.168.1.17`; repo
  `/home/pcrec/projects/pcrec`. Bare `timeout` is uutils; use
  `gnutimeout`. There is no git identity; commit with
  `git -c user.name="Frank DiCostanzo" -c user.email=frank@dicostanzo.com`.
- **One branch per unit, each in its own worktree.** Never merge to main
  and never push. Never `cd` in a compound command (it moves the session
  cwd); use `git -C` and absolute paths.
- **Scratch:** `worktrees/memfn-slot/` holds one dir per slot.

## 2. Read, in this order

`memfn/CLAUDE.md`, then `requests.md` and `responses.md` (the newest
entries), then the tail of `journal.md`, then integration.md §R4.9. Read
BOILERPLATE before briefing.

## 3. Box, slot and cron rules

- One heavy suite at a time across BOTH sessions. **ASK main for the GO
  before every slot**, and ping main at DONE with the full verdict and
  mech trailer.
- **Light work** (make -j4, strict, single sections pinned
  `taskset -c 12-15`, G2 quick, single mech rows) needs no slot.
- **Lane briefs must NAME the forbidden heavy runs** (full make test,
  emit_sweep, G2 full/quick-tier `make test-memfn-g2`, mech batches) and
  must require start/end times for every run in the report. rankuse
  breached this (2026-10-09).
- Slot script pattern: `memfn-slot/slot18/run.sh`. Launch it detached with
  `setsid nohup`. It writes DONE only when the last stage completes.
- **Dry-run every new invocation's argument parsing before a slot.**
  slot17's VARIANTS stage died on a missing `--tree-rev`.
- A verdict reads EVERY column of the mech trailer.
- A red stage gets a TRIAGE lane before you read the log yourself.
- Restore `docs/dev/artifact_size_log.tsv` after `make test`; never
  commit it.
- **Heartbeat cron** `17,47 * * * *` (deadlock check). Recreate it at wake
  and delete it at close.

## 4. Current state (2026-10-10 ~00:30)

- **R-12 (VMLAZY abi 72 + N7U retired): DELIVERED, awaiting re-landing.**
  - `done:` is posted on lane/memfn-vmlazy (92213567). slot17 and slot17b
    read; VARIANT_PINS re-pinned (736d4050); vmlazy_report §8b.
  - Main merges R-12 FIRST (before R-13), after lfl0's chain ends and lfl0
    merges (hours away at 00:30).
  - Prep is done: main (specnum) is merged at **0517caea**. match_api.md is
    main's, with the 5 current-abi readers set to 72; the abi-72 entry is at
    the top of `docs/dev/history/abi_changelog.md`; three line citations in
    the reports became section citations. build, strict, test-spec-history
    and test-codegen are green.
  - **On the NEXT main's GO**:
    1. `git -C worktrees/vmlazy merge <main tip it names>`, ALONE.
    2. Resolve, then run strict and `make test-spec-history`.
    3. Re-grep the abi-71 readers.
    4. Launch `memfn-slot/slot19/run.sh`: registry, rxtsource, codegen,
       `--variant all` vs merge-base, the lowsize/lowboth self-check, then
       make test.
    5. Judge: VARIANTS movers are only the abi stamp plus the lazy set
       (compare by id against
       `docs/design/memfn/probes/vmlazy/out/slot17b_movers_by_id.txt`); the
       self-check is CLEAN; no red lines.
    6. Post `done:` again on lane/memfn-vmlazy and ping main.
  - Prune after main merges: vmlmerge, n7uret, vmlfix, ssred, vmlazy.
- **R-13 (batch 1 + rankuse): BUILT, CANDIDATE**, lane/memfn-r13 @
  9348a747.
  - Contents: main 7b98a046 (RQ-2) is merged; the sink ops are MF_SITE_ABI
    10; the kit reads `rank_pos` (KB = the first ranked position other
    than KA; HOW MANY (two) is UNMEASURED DEFAULT, deny
    `--memfn=no-vrun-kb`); S750-S754 (main's block); rkfix's C4/K37 fixes
    are in.
  - Light gates are green. SIMD-off has 0 movers, so there is no pcrec abi
    event.
  - **Next, AFTER main merges R-12:**
    1. Merge post-R-12 main into lane/memfn-r13, ALONE.
    2. Run slot18 (`memfn-slot/slot18/run.sh`: 4 identity sweeps, N2, G2
       full, make test, 33 mech rows, ~2.5 h) on main's GO.
    3. Then `--propose` the vrun-* N2 floors (PLACEHOLDER in
       row_floors.tsv).
    4. Post `done:` for R-13's build.
  - Then RQ-4's tier-U timing slot, which main grants: arms DEFAULT /
    KB-DENY (`--memfn=no-vrun-kb`) / OFF (rankuse_report "RQ-4"). Then RQ-5.
  - **Frank asked for the first SIMD-on vs SIMD-off directional reading.**
    It comes from the RQ-4 run. Report it plainly.
- **Owed to main (posted):** D58 add. 2's revisit close (N7U).
- **Unscheduled:** Q-G2M6-1..9, [MEMFN-CI-ASCII], a D27 G2 lane for the
  SIMD contract (Q-R13-4), and regenerating `movers.tsv` at 5451 rows
  (superseded by slot17b_movers_by_id.txt for the verdict).

**Worktrees:** vmlazy (R-12), r13 (R-13), rankuse, rkfix, r13doc, vmlmerge,
n7uret, vmlfix, ssred (all merged into kit branches; prune after main
merges), g2u + g2u-cell (keep), memfn (lane/memfn-skill), memfn-slot
(scratch), r4h, m4.

## 5. Next actions on wake

1. Recreate the heartbeat cron and run ListAgents. Read requests.md for new
   items.
2. Look for the NEXT main's slot19 GO message (or ask it once whether lfl0
   has merged, but only if it is up and you are waiting).
3. Work §4 in order: R-12 slot19, then R-13 merge, then slot18.
