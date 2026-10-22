# memfn wake — kit session hand-off (rewritten 2026-10-18 ~22:15, paused for the night)

This is the kit session's orientation file. Run `/pcrec-memfn-manager` and follow its §1, the wake order. This file is rewritten at every pause and holds the current state. History lives in `journal.md`.

## 1. Who you are and where you work

- You are the pcrec-memory-functions kit manager (`pcrecdev3`). Main is `pcrecdev1`; run ListAgents to find it.
- `requests.md` is main's to write, and only main writes it. `responses.md` is yours to write, and only you write it.
- **Box:** the Linux dev box, repo `/home/pcrec/projects/pcrec`. Use `gnutimeout`. Commit with `-c user.name="Frank DiCostanzo" -c user.email=frank@dicostanzo.com`.
- **Merges go through main.** Send main the branch, sha, target and validation.
- **Kit branches:** one per delivered unit, cut from a main that contains the request.
  - `lane/memfn-r25` (worktree `worktrees/memfn-r25`) is the latest and carries this file. It is NOT merged.
  - `lane/memfn-pinfix` (worktree `worktrees/memfn-pinfix`) was delivered to main for merging.
- **Never `cd`**, not even inside one compound command. Use `git -C`, `make -C`, `env -C` and absolute paths.
- **Worktree removal:** only `scripts/wtprune`, naming the kit's own trees (`--apply NAME..`); dirty or nested targets via `--apply --force NAME..`. Never `rm -rf`.

## 2. Read, in this order

1. `memfn/CLAUDE.md`.
2. `requests.md` on main (newest R-25) and `responses.md` on lane/memfn-r25.
3. The tail of `journal.md`.
4. `docs/dev/lanes/r25_report.md` and `docs/dev/lanes/pinfix_report.md`.
5. For B4: `docs/design/memfn/r17b_prime.md` rev 3 §3.1, plus the grid2read findings (M9/M15).

## 3. Rules in force

- **Box calendar (Frank):** the bench's re-baseline runs from 2026-10-19 01:00 TO COMPLETION (~16:00 Mon).
  - Until main announces the bench's closing sentinel, the kit runs NOTHING CPU-bound. Docs and thinking are fine.
  - After that: dev by day, bench at night.
- **Timing runs** are cleared through main, and main clears them with Frank. Correctness heavy suites need one heavy slot from main.
- **Mech in a heavy chain:** ONE `PROCS=4 run_sabotage_matrix.sh <ids>` invocation, [TT-MECHPAR]. Score by the per-row column: accept only `DETECTED` or `(EXPECTED`.
- **After ANY `src/`/`memfn/src` edit, run all of these:**
  - `python3 -I scripts/m6read_check_sab_anchors.py`;
  - `bash tests/codegen/run_codegen_tests.sh`;
  - test-core.
- **A delivery's make test and its mech rows run at the SAME tip.**
- **A red suite stage gets a TRIAGE lane** before you read its log.

## 4. Current state

Rewritten 2026-10-21 ~21:40 at Frank's /close.
- **Versions:** pcrec abi 82, `MF_SITE_ABI` 18, `MF_VOCAB` 4, `MF_CLASS_V` 5.
- **R-26's kit part:** DONE and merged (Z1, Zk).
- **The set-FIND form question is CLOSED.** Read `docs/design/memfn/walk_vs_v1_record.md` before proposing any non-walk default. Frank's ruling: the WALK when the subject is unknown; D169's addendum is filed. [MEMFN-SKIPSWITCH] is in Boonies.
- **B4:** RE-SCOPE OWED. Its V1 movers disappear under the walk ruling. Expected shape: route the existing rows, with no default byte move; the measured-regime path stays. Send main the new shape. The minimal-E8 work stays on lane/memfn-e8min (D170).
- **R-27 (REPORT speed on sparse text):** DESIGN ONLY at `lane/memfn-r27` @ b4875f947, report `docs/dev/lanes/r27_report.md`. Design: D161 window search, extensions E1/E2/E4 to existing rows, plants R27-a..f, questions Q1-Q3 in §0.
  - **No build go.** Frank: "lets see what the design returns. after you wake, run the critic pass on it."
  - **Timing job `580-kit-r27-cover` is QUEUED** behind main's i1build jobs, with a quiet gate.
    - Completion line: `== r27 COMPLETE rows=1800 launches=5`.
    - Table: `worktrees/memfn-r27/build/r27/job/r27_table.md`.
    - Job log: `worktrees/.boxqueue/{done,failed}/<TS>-580-kit-r27-cover/job.log`.
    - Paste the table into r27_report.md §5.
- **Unmerged kit branches for main:** lane/memfn-r27 (record, ruling notices, the R-27 design), lane/memfn-e8min, lane/memfn-flat, lane/memfn-adatwin (measurement records). Ask main to merge them as records.
- **Nothing running** except job 580 waiting in the queue. No lanes, crons or watchers.
- **Prunable once merged and quiet:** r26z1, r26zk, b4prep, memfn-r26, setdig, e8min, flat, adatwin.

**OWED (carried):**
- The five PRES rows' g2 floors are PLACEHOLDER.
- D2 is `pending-site:R-18`.
- candoracle's reach gap is on main's list.

## 5. Next actions on wake

1. **Critic pass on R-27's design (Frank's instruction).** Run 2-4 read-only critics on r27_report.md: soundness of the skip/verify/proof equality, the E1/E2/E4 row extensions vs the general mechanism, the measurement regime, and an unlocks lens. Consolidate into `docs/dev/reviews/<date>-r1-memfn-r27.md`, then bring Frank the findings plus a build-go question. Fold in job 580's table if it has run.
2. Send main B4's re-scoped shape.
3. Heavy runs go through `scripts/boxqueue` (kit band 500-699) with a quiet gate and `idle-ok`. Run emit_sweep WITHOUT `python3 -I`.
