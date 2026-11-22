# memfn kit — wake-up brief

Updated 2026-11-21 19:20 by the kit session at CLOSE (Frank /close). Main (pcrec-main) is up.

## Who you are
The kit manager (`/pcrec-memfn-manager`). The ledger and journal branch is worktrees/memfn on lane/memfn-k1108.
- Heartbeat cron: 17,47.
- Waiting list: worktrees/.mgr/waiting_on.kit.
- Queue verdicts: only via `scripts/monread kit --wait` (run_in_background).
- Lane watching: `scripts/lanewatch --follow NAME`.

## Read in order
1. This file.
2. memfn/docs/journal.md, the 2026-11-21 entries.
3. docs/design/memfn/block_span.md rev 4.2 (§14 units, §18 dispositions).

## CURRENT STATE: R-47 / D201, the block span at the SIMD layer
- **Owner rulings:** D201 and addenda 1-5:
  - "build with simd layer";
  - option A;
  - "scalar-check-cut: yes";
  - "wrap-clang: a", with [BSPAN-CLANG-DIFF] filed, which rides U5's C6 card: time the bench's clang arms on the 3 sites.
  - D202: the cover width is the KIT's decision. [COVER-WIDTH-KIT] waits on a build go; a fixed engine-cost assumption is allowed.
- **U1 LANDED** on main (c279e7e26).
- **U2 + U2b LANDED and PUSHED** (68521b3ad, abi 110 on main).
- **U3 is built:** lane/bsu3 ec578d053, abi 111 -> 112 on the kit branch. Code round r76 ruled FIX FIRST. The fixes are on lane/bsu3fix @ 6cf672b6a (bsu3fix + bsu3fix2). The r76 gap critic: r75 SLOT-3/4 DISCHARGED.
- **OWED, gated not-before 2026-11-22T07:00:** 729-kit-bsu3fix2-test, 730-kit-bsu3fix2-mech, 731-kit-bsu3fix2-ids.
  - Arm `scripts/monread kit --wait` at wake.
  - All green -> `git -C worktrees/memfn merge lane/bsu3fix` ALONE, then make strict, a [responses] done line, and SendMessage main.
  - Main lands U3. abi 112 is confirmed; whichever of L3/U3 lands later re-pins.
- **Then:**
  - U4 (G2-V, the T-table pins, the rest of C18, sabotage (a)-(f));
  - U5 (card C6 incl. the clang arms, CANDIDATE);
  - U6 (the abi package, G1 dry run; C6 timing in main's window on every bench box, Zen 1 included).
  - Ask main for review numbers.
- **Box:** Frank held it clear from 19:15 tonight; evening hold 20:00-01:00; main's TIMING window 01:00-07:00. Nothing of the kit's runs before 07:00.
- **Prunable later (scripts/wtprune):** bsu2fix (<120 min guard), bsu3, bsu3fix once U3 lands. Unmerged report-only branches: spancensus, spancensus2, rampchunk, rampfix, bcq, cofix, bcfix. A /tmp/pcrec-mech-sabotage.* dir was left by a lane; Frank was told, and it was left alone.
- **OWED (older):**
  - the g2 win-family triage lane;
  - re-sync the rampfix 712 harness;
  - the cards.py not-warm chunking defect;
  - gatebudget, mfcal and mfind decisions;
  - r46 PLAN/DOC, r24 SR-1..4, ADQ-3-3, the mfind witness.
  - Ideas log: [COVER-NEARMISS-SKIP] backward verify (owner idea, unscheduled).

## Lessons
The kit skill §4 "Brief rules learned 2026-11-21" holds the lane-brief rules. Also:
- A reviewer's cut of a condition the owner was told is an owner question.
- Owner words go into the journal VERBATIM, the same day.
- Journal times come from `date`.
- A quoted heredoc ('EOF') stops backticks from running.
