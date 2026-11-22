# memfn kit — wake-up brief

Updated 2026-11-22 15:15 by the kit session IN FLIGHT. Main (pcrec-main) is up.

## Who you are
The kit manager (`/pcrec-memfn-manager`). The ledger and journal branch is worktrees/memfn on lane/memfn-k1108.
- Heartbeat cron: 17,47.
- Waiting list: worktrees/.mgr/waiting_on.kit.
- Queue verdicts: only via `scripts/monread kit --wait` (run_in_background).
- Lane watching: `scripts/lanewatch --follow NAME`, ONE name per call. It exits DONE at once if the lane's lanecheck already passed.

## Read in order
1. This file.
2. memfn/docs/journal.md, the 2026-11-22 entries.
3. docs/design/memfn/block_span.md (§8, §10, §14, and §18's r78/r79 dispositions).
4. docs/dev/reviews/2026-11-22-r78-memfn-bsu4.md and r79-memfn-bsu5.md (MANAGER RULING at the top of each).

## CURRENT STATE: R-47 / D201, the block span at the SIMD layer
- **U1, U2, U2b and U3 are LANDED on main.** U3 landed at abi 111. L3 then lands at 112; main is landing it now.
- **U4 (checks only) is DELIVERED:** kit branch 3e62406e2, validated at 0eceaaee1 (742/743 GREEN).
  - Main lands U4 after L3, with a cloud test on the merge, and will tell the kit both landings.
  - After that, merge main into lane/memfn-k1108: `git merge` ALONE, then make strict.
- **U5 is built, reviewed (r79, FIX FIRST) and fixed.**
  - Branch: lane/bsu5fix @ 36548a3a9. It is built on lane/bsu5 28b2da326.
  - What it holds: card C6 plus the clang/gcc -Os card C6c; kit-grid@8 UNMEASURED; formhash span folded into WINDOW with 3 span-vector instances; c6_rule.md committed (sha 9a2875a6bf089837).
  - 746 make test is GREEN, and 747 mech (S2930/S2931/S2933) is GREEN.
  - **748 kit-bsu5fix-selftest is RUNNING** (the full cards.py selftest, ~90 min at the base too, cap 7200). It started 15:12, so expect it around 16:45. Log: /var/tmp/pcrec-pcrec/scratch/bsu5fix/selftest_full.log.
  - When it is GREEN:
    1. `git -C worktrees/memfn merge --no-ff lane/bsu5fix`, ALONE;
    2. make strict;
    3. if main moved, merge main too, then a tip test + mech job on a DETACHED worktree (the U4 pattern: worktrees/u4tip);
    4. a [responses] done (partial) R-47 U5 line;
    5. SendMessage main.
  - Pass along the [BSPAN-CLANG-DIFF] status for main: C6c covers clang -O2 + gcc -Os, SIMD-off, non-PIC. clang -O3 and -fPIC are named gaps.
  - The base's ~90-min selftest is pre-existing; the df-cache speedup is NOT built.
- **Then U6 (review r80):**
  - the abi package at the landing base, if any byte moves (U4/U5 moved none);
  - make test-axes;
  - REACH_ONLY;
  - G1's manifest + dry run;
  - **C6/C6c TIMING in a window main clears with Frank, on every bench box including Zen 1** (ubuntubudu). V stays CANDIDATE until then.
  - Open points for U6's reader are labelled in c6_rule.md.
- **After R-47 completes:** tell main, so [KIT-ARCH-STEP] stage 2 can be chartered. Frank's verbatim ruling is in the journal: one overall arch review of the kit's sections, refactors filed and smaller ones favoured; then arch notes + arch rounds before every new kit feature.
- **Owner rulings of 11-22, verbatim in the journal:**
  - D202 add. 1: the cover width is a table per kind; each site states the proof it needs (range vs candidate); the follow-up on the obligation.
  - D202 add. 2: "the width is your call within the above"; the table and score are IDEAS only.
  - "dense-not-target: close".
  - d3-repin-permission granted; lanes may re-pin; the kit ruled YES on the span_seed rows.
- **Sabotage ids:** S3540 and S3542-S3545 are bsu4fix's (S3541 is main's). S3546-S3549 are bsu5's, S3550-S3554 bsu5fix's; the next free id is S3555. Ledger: worktrees/.mgr/sabotage_ids.txt.
- **Prunable once landed (scripts/wtprune):** bsu3, bsu3fix, bsu4g, bsu4p, bsu4, bsu4fix, u4tip, bsu5, bsu5fix.
- **OWED (older):**
  - the g2 win-family triage lane;
  - re-sync the rampfix 712 harness;
  - the cards.py not-warm chunking defect;
  - gatebudget, mfcal and mfind decisions;
  - r46 PLAN/DOC, r24 SR-1..4, ADQ-3-3, the mfind witness.
  - r78 PLAN: PINS-7's table/TSV and G2V-4. r79 PLAN: F15, intrinsic rename invariance in mf_form_hash; file it to main.

## Lessons (2026-11-22)
Lane briefs carry these, and they are in the skill's §4:
- An in-lane run longer than a few seconds checks boxlock for a TIMING holder first.
- A `--harness=` lever use needs its run_lever_fence.sh ALLOW row in the same commit.
- Cancelling a half-branch's validation hides its reds; the combined tip must run everything.
- Lanes idle on background runs: tell them to poll in the foreground.
- A lane's SendMessage to pcrec-memfn fails: brief "team-lead".
- Owner words go into the journal VERBATIM, and the kit's phrases are never filed as his.
