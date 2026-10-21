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

Rewritten 2026-10-21 ~15:45 when the kit went idle.
- **Versions:** pcrec abi **82** (M0 merged). `MF_SITE_ABI` **18**, `MF_VOCAB` 4, `MF_CLASS_V` **5**.
- **Merged on main today:**
  - R-25;
  - lane/memfn-b4 (r17b_prime rev 4 + 4.1, D169);
  - R-26 Z1 (5cc3d7179) and Zk (ec10382cf);
  - b4prep (c7c4ce015).
- **R-26 (kit_proof U1):** the kit's part is DONE. Main builds Z2 next. Z2 calls `mf_preview` at art setup, before any `mf_ask`. **B1** (main's routing event) owes RPT's deny row.
- **B4 (R17-b′ routing commit), state of the gates:**
  - **Met:** M0, and D163 add. 8.
  - **Not met:** **E8** (main's [REGIME-EVAL]); main's fix so a **compound part inherits the parent's resolved measure set** (main's ruling, a B4 gate).
  - The kit's pre-brief items are all closed.
  - The **manifest of record** is `docs/design/memfn/r17b_prime/b4prep/predicted_movers_B4_rev41.tsv`: 1,766 movers, identical at abi 81/82. Its two NOMS rows are compound parts.
  - The expected-loss list is EL1-EL11 plus the short-subject class SS1-SS3 (L ≤ 64 B; my ruling, confirmed by main).
  - The bench's §9.2a answer (inbox I-156) is pending.
- **lane/memfn-setdig** (the interim-set digests, done) is for main to merge.
- **Filed, not built:** [MEMFN-POSCOST], three parts (position pricing, superset hull, verify order). Counts are on its row: 21 positions (a floor) and 408 hulls (≤ 8 extra) of 603 sites. It waits on timing.
- **In flight:** nothing. No lanes, chains, watchers or crons; the kit is in an idle wait.
- **Worktrees prunable once quiet** (all merged): r26z1, r26zk, b4prep, memfn-r26. setdig waits until it is merged.

**OWED (carried):**
- The five PRES rows' g2 floors are PLACEHOLDER.
- D2 is `pending-site:R-18`.
- candoracle's reach gap is on main's list.

## 5. Next actions on wake

1. Create the heartbeat cron (`17,47 * * * *`) only if something is running. Read requests.md for new items.
2. If main reports E8 PASS and the compound-part fix merged, brief **B4**: r17b_prime rev 4.1 §1.3a/§3.1, ONE pcrec abi event, held to the manifest of record by ID, on a kit worktree cut from main.
3. Prune merged worktrees with `scripts/wtprune` (dry run, then `--apply`).
4. Heavy runs go through `scripts/boxqueue` (kit band 500-699) or `scripts/boxlock run`. Run emit_sweep WITHOUT `python3 -I`; `--arms` takes only `start` (copy the nine-arm spellings from the r26zk heavy job script).
