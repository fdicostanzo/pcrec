# memfn kit — wake-up brief

Updated 2026-11-23 14:46 by the kit session IN FLIGHT. Main (pcrec-main) is up.

## Who you are
The kit manager (`/pcrec-memfn-manager`). The ledger and journal branch is worktrees/memfn on lane/memfn-k1108.
- Heartbeat cron: 17,47 (4b59ad8c).
- Waiting list: worktrees/.mgr/waiting_on.kit.
- Queue verdicts: only via `scripts/monread kit --wait` (run_in_background).
- Lanes: `scripts/lanewatch --follow NAME`, one name per call.
- Review numbers: ASK MAIN before launching a round (r86 collided, 11-23).

## Read in order
1. This file.
2. memfn/docs/journal.md, the 2026-11-23 entries.
3. docs/dev/reviews/2026-11-23-r80-memfn-bsu6.md and r87-memfn-bsu6par.md (MANAGER RULING at the top).
4. docs/design/memfn/block_span.md §14, c6_rule.md (frozen).

## CURRENT STATE: R-47 / D201, the block span at the SIMD layer
- **U1-U5 are LANDED on main.**
- **U6 is DELIVERED minus timing**:
  - [responses] 866235918;
  - kit merge 7e9df99e3 of lane/bsu6fix3 c8116f8cb;
  - 757 full selftest 222/0; 752 test-axes GREEN; 753 reach ok except S1761 ([PIN-MSG-DEPTH], fixed on main 91cc16215).
  - Main merged U6 locally (4a989690c), cloud test running, pushes after green.
- **TIMING owed**:
  - Main asked Frank (u6-timing-window) for the dev box, leaning 01:00-01:30 tonight.
  - ubuntubudu is UNREACHABLE; main asked Frank if it is off.
  - The job is BUILT and rehearsed (lane u6time; journal 11-23 has the queue command). ON CLEARANCE: write worktrees/.mgr/u6time.cleared "start=YYYY-MM-DDTHH:MM stop=YYYY-MM-DDTHH:MM [evening=ok]" from the window, then queue 760-kit-u6time. Keep worktrees/u6time (do not prune).
  - Read the verdict with `cards.py c6decide`. V stays CANDIDATE until then.
- **Parallel selftest (owner ruling 11-23, verbatim in the journal)**:
  - lane/bsu6par 2061e7e98 adds memfn/tests/parpool.py and 218 selftest units; 758 -j16 GREEN in 780 s vs 5615 s serial, identical to 757 apart from the masked line.
  - r87 ruled FIX FIRST: dead worker, --units closure, subset label, maxtasksperchild=1, longest-first from 758's profile.
  - Lane **bsu6par2** (sonnet, worktrees/bsu6par2) is applying them; it owes one selftest job. GREEN -> merge lane/bsu6par2 into the kit branch, then deliver to main as an R-47 U6 addendum.
- **Filed, not built** (bsu6par survey): mutb.py per-mutant parpool units (27 min serial); split run_g2_win.sh by head (288 s critical path).
- **After R-47 completes** (timing verdict in): tell main, so [KIT-ARCH-STEP] stage 2 can be chartered (Frank's ruling is verbatim in the 11-22 journal).
- **Sabotage ids:** the next free id is S3570 (worktrees/.mgr/sabotage_ids.txt).
- **Prunable** (scripts/wtprune, after main pushes U6): bsu3*, bsu4*, u4tip, bsu5*, u5tip, bsu6, bsu6t, bsu6fix, bsu6fix2, bsu6fix3; bsu6par/bsu6par2 after their merge.
- **Merge main** into the kit branch at the next quiet point: it picks up pinmsg.
- **OWED (older)**: the g2 win-family triage; the rampfix 712 harness re-sync; cards.py not-warm chunking; gatebudget/mfcal/mfind decisions; r46 PLAN/DOC, r24 SR-1..4, ADQ-3-3, the mfind witness; r78 PLAN (PINS-7, G2V-4); r80 PLAN FIDELITY-6/7 (in ideas.md).

## Lessons (2026-11-22/23)
- A lock bypass (PCREC_BOXLOCK=0) is never mine to grant.
- Settle scope before briefing; addenda to running lanes get missed (the bsu6 probe breach).
- Lanes idle on background runs: tell them to poll in the foreground.
- A check that runs only in the slow suite hides drift: put drills in the quick self-test (J2, bsu6fix3).
- Ask main for review numbers.
- Long or repeated test runners get a parallelism review (owner, 11-23).
- Owner words go into the journal VERBATIM.
