# memfn kit — wake-up brief

Updated 2026-11-24 01:3x by the kit session at its HAND-OFF. Frank is moving the kit session from the Linux dev box to the Mac (owner 2026-11-23, verbatim in the journal): ONE kit at a time, never two.

## Who you are
The kit manager (`/pcrec-memfn-manager`). The kit branch is lane/memfn-k1108 (on the dev box: worktrees/memfn).
- **On the Mac:**
  - cut your own kit worktree from main once main has merged d716c9d72 (or later);
  - re-register (`scripts/session_role kit`) and create a fresh heartbeat;
  - read the Mac rows in pcrec-cross-platform-verification and docs/testing.md "The boxes" first.
- Timing verdicts stay on the Linux dev box (D144 add. 1); the Mac is directional. A timing run means a window main clears with Frank.
- Review numbers: ASK MAIN before launching a round.
- Long or repeated test runners get a parallelism review (owner 11-23); memfn/tests/parpool.py is the shared pool.

## Read in order
1. This file.
2. memfn/docs/journal.md, the 2026-11-23/24 entries.
3. memfn/docs/responses.md, the last three items (U6 partial, the U6 addendum, R-47 done).
4. docs/design/memfn/block_span.md §14 (the units), c6_rule.md (frozen).

## STATE AT HAND-OFF
- **R-47 / D201 is COMPLETE.** U1-U6 are landed on main, except the final delivery.
  - The final delivery: [responses] done d716c9d72 on lane/memfn-k1108, carrying 760's timing record (docs/dev/lanes/u6time_evidence/run760/) and the job-shape fix. Check that main merged it.
  - **Verdict, Zen 4 dev box, job 760:** C6 NO LOSS (17/10/0, 27 of 32 readable); C6c NO LOSS under off-clang and off-os.
  - ubuntubudu is UNAVAILABLE, and there is no Mac cell.
  - **V stays CANDIDATE:** the official SIMD verdict is a pcrec-BENCH run (D155 item 2, D144 add. 4), and 760 was the kit's own cards (unofficial). Main put it to Frank as question simd-v-candidate (11-24); block_span.md keeps CANDIDATE until he rules. (The kit wrongly proposed a lift in d716c9d72; corrected here.)
- **Nothing open here:** no kit queue jobs, no running lanes, heartbeat deleted.
  - Leftover worktrees on the dev box: bsu3/bsu3fix only (pinned in .wtprune.keep); u6time and its branch were pruned 2026-11-24 03:13.
- **NEXT (on the Mac):** [KIT-ARCH-STEP] stage 2. Frank's ruling, verbatim in the 11-22 journal: "kit-arch-step: yes but after existing effort completed. Then overall arch review of kit sections with suggestions. Possible refactors, favoring smaller items. Then arch reviews going forwards". Wait for main's charter; use the pcrec-architect skill and critic arch mode.
- **Sabotage ids:** the next free id is S3570 (ledger worktrees/.mgr/sabotage_ids.txt on the dev box; it is gitignored and does not travel). Ask main for the ledger, or carry the number.
- **Filed, not built:** mutb.py under parpool (27 min serial); run_g2_win.sh split by head (288 s critical path); r80 FIDELITY-6/7 (ideas.md).
- **OWED (older):**
  - the g2 win-family triage;
  - the rampfix 712 harness re-sync;
  - cards.py not-warm chunking;
  - gatebudget/mfcal/mfind decisions;
  - r46 PLAN/DOC, r24 SR-1..4, ADQ-3-3, the mfind witness;
  - r78 PLAN (PINS-7, G2V-4); r79 PLAN F15 is filed as [FH-INTRIN].
  The arch review may absorb some of these; re-triage them after it.

## Lessons (2026-11-22/24)
- A lock bypass (PCREC_BOXLOCK=0) is never mine to grant.
- Settle scope before briefing; addenda to running lanes get missed.
- Lanes idle on background runs: tell them to poll in the foreground.
- A check that runs only in the slow suite hides drift: put its drill in the quick self-test.
- A window-gated job declares the window start as not-before (or the queue calls it stuck), and keeps a rehearsal's lines out of the log its expects read.
- Verify a lane's "box was quiet" mechanism and its estimates against the log before quoting a wall time.
- Owner words go into the journal VERBATIM.
