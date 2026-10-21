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

- **pcrec abi is 80.** `MF_SITE_ABI` 17, `MF_VOCAB` 4, `MF_CLASS_V` 4 (unchanged by R-25; kit ruling: no bump).
- **R-25 is built and light-validated** at `lane/memfn-r25` @ f39a2eb3a. The branch tip has the [responses] and wake commits on top.
  - Its parts: `arm.tests` (EVERY/REQUIRED/UNSTATED), `kit_class` reading only tested terms, UNSTATED refused on a FIND, and the fixture tests/memfn/proven_check.c (floor 31).
  - emit_sweep showed 0 movers on six arms.
  - **Main has queued its heavy slot FIRST after the bench sentinel and will message when it's ours.** Run make test plus mech S1018/S1083 (one PROCS=4 matrix call) at the branch tip, then post `done: R-25` and SendMessage main.
  - The variant/trace/rwquest sweep arms were not run (outside the brief). Decide whether the slot should include them.
- **pinfix** is at `lane/memfn-pinfix` @ 1d797ab3a and was delivered to main (notice in responses.md on lane/memfn-r25). It fixes emit_sweep's start-arm orphan pin by adding `a.{1,5}z` to presence_deny.rxt. Its make test is owed: main may fold it into R-25's slot or rely on CI.

**Next work, in order:**
1. R-25's heavy slot, then `done:`.
2. **B4** (r17b_prime rev 3 §3.1, ONE pcrec abi event). It waits on:
   - Frank's rev 4 direction (unknown predictability: default to V1 or the walk?);
   - D163 add. 8's layout controls (E1 has landed, so check that gate);
   - E8 PASS and M0.
3. Comment on main's U1 design (`docs/design/kit_proof.md`) in responses.md once it lands.

**OWED (carried):**
- The five PRES rows' g2 floors stay PLACEHOLDER (they need G2 REACH per row).
- D2 stays `pending-site:R-18`.
- candoracle's reach gap is on main's check-design list.

**In flight (2026-10-21 ~02:00, idle wait):** nothing is running. No lanes, chains, watchers or crons.
- **Kit branch `lane/memfn-b4` @ f5f1e3c05** (worktree `worktrees/memfn-b4`) is for main to merge, as listed in main's wake. It carries:
  - D169's notice (V1 default; main has FILED D169);
  - Frank's 2026-10-21 answers (set sites route by term count, `kit.terms.V1max` = 2; F2 to V1 at B5) as notices with proposed D text for main to file;
  - r17b_prime **rev 4 + 4.1** (B4's table §1.3a, default §1.9, gates §3.1a; every §7.3 question ANSWERED).
- **B4 gates:** D163 add. 8 MET; E8 and M0 NOT MET. OWED before the B4 brief: grid2read §8's quiet re-time (about 2 min, heavy slot), the V1-text attribution against grid1's arm, a byte compare of the slot's walk against main's walk, the mover manifest regenerated (including the 54 no-key sites' term-count split), and the expected-loss list filled.
- **Heavy runs:** `scripts/boxlock run --label kit -- CMD`, or main's `scripts/boxqueue` (kit band 500-699). Run emit_sweep WITHOUT `python3 -I` until main's fix is confirmed.
- **Prune when quiet:** `rev4`, `rev41` (both merged into b4).

**Worktrees:** KEEP `memfn-r25`, `memfn-pinfix` (until merged), `rowfix` (merged; prunable once quiet), `memfn-slot` (scratch). 22 merged kit trees were pruned on 2026-10-18.

## 5. Next actions on wake

1. Create the heartbeat cron (`17,47 * * * *`), run ListAgents, read requests.md for new items.
2. Check whether the bench sentinel has been announced and whether main has given the R-25 slot.
3. Check whether main merged pinfix; if so, prune it and rowfix with wtprune.
