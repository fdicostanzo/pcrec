# memfn wake — kit session hand-off (rewritten 2026-10-18 ~19:30, session close on Frank's /close)

This is the kit session's orientation file. Run `/pcrec-memfn-manager` and follow its §1, the wake order. This file is rewritten at every pause and holds the current state. History lives in `journal.md`.

## 1. Who you are and where you work

- You are the pcrec-memory-functions kit manager (`pcrecdev3`). Main is `pcrecdev1`; run ListAgents to find it.
- `requests.md` is main's to write, and only main writes it. `responses.md` is yours to write, and only you write it.
- **Box:** the Linux dev box, repo `/home/pcrec/projects/pcrec`. Use `gnutimeout`. Commit with `-c user.name="Frank DiCostanzo" -c user.email=frank@dicostanzo.com`.
- **Merges go through main.** Send main the branch, sha, target and validation. Main merges for the kit at its discretion.
- **Kit branches:** one per delivered unit, cut from a main that contains the request.
  - `lane/memfn-rowfix` (worktree `worktrees/rowfix`) is the latest and carries this file. It is NOT yet merged.
  - `lane/memfn-b3b` is ON MAIN (d18cee085).
- **Never `cd`**, not even inside one compound command; I slipped twice today. Use `git -C`, `make -C`, `env -C` and absolute paths.
- **Worktree removal:** only `scripts/wtprune`; dirty or nested targets by name via `--apply --force NAME..`. Never `rm -rf`.

## 2. Read, in this order

1. `memfn/CLAUDE.md`.
2. `requests.md` on main (newest is R-25) and `responses.md` on lane/memfn-rowfix.
3. The tail of `journal.md` (the 2026-10-18 entries).
4. `docs/dev/lanes/b3b_report.md` (§8-§14, the heavy-chain rounds) and `docs/dev/lanes/rowfix_report.md`.
5. For R-25: `docs/dev/reviews/2026-10-18-r2-kitverify-proof.md` §5 M4, D161 addendum 16, and `docs/dev/kvcensus.md`.
6. `docs/design/memfn/r17b_prime.md` rev 3 §3.1 (B4 is next after R-25), plus the grid2read findings (M9/M15 contradicted; rev 4 direction owed by Frank).

## 3. Rules in force

- **Box calendar (Frank):** the bench's re-baseline runs from 2026-10-19 01:00 TO COMPLETION (~15 h, ~16:00 Mon).
  - From 00:30 until main announces the bench's closing sentinel, the kit runs NOTHING CPU-bound, pinned or not. Docs and thinking are fine.
  - After that: dev by day, bench at night.
- **Timing runs** (grid slots, re-times, REGIME-EVAL judges) are cleared through main, and main clears them with Frank. If a timing run sees load from a non-pcrec process, send main the name and PID; never kill or renice it.
- **Correctness heavy suites** need one heavy slot from main, one at a time.
- **Mech in a heavy chain:** ONE `PROCS=4 run_sabotage_matrix.sh <ids>` invocation, [TT-MECHPAR] (3.3x, verdicts identical; Frank pushed for it today). Never serial solo loops. Solo runs are for triage only.
  - Score by the matrix's per-row column: accept only `DETECTED` or `(EXPECTED`, never `***UNEXPECTED***`.
  - A known-bad allowlist needs a main-side witness.
  - The scorer lives in `worktrees/memfn-slot/b3bheavy3/chain.sh`.
- **After ANY `src/`/`memfn/src` edit, however small:**
  - run `python3 -I scripts/m6read_check_sab_anchors.py` and `bash tests/codegen/run_codegen_tests.sh` (anchors move);
  - also run test-core (FLAG-ACCESS) when C changes.
- **A delivery's make test and its mech rows run at the SAME tip** (main's rule).
- **A red suite stage gets a TRIAGE lane** before you read its log.

## 4. Current state

**On main (d18cee085):** B0-B3b, R-23, R-24, E-1, E1 (part layout, abi 80).
- pcrec abi is **80**.
- `MF_SITE_ABI` is 17, `MF_VOCAB` 4, `MF_CLASS_V` 4.

**Delivered, awaiting main's merge:** `lane/memfn-rowfix` @ 8dbee7fd2 (done: posted in responses.md).
- S689 and S1085 are restored (DETECTED solo).
- **n2_census.sh's rc-4 defect fix (725abc9e5).** On main today every N2 run ends rc 4 with all counts 0, and n2sample-detected rows read a false DETECTED. The n2_report verdicts themselves are unaffected.
- Light validation only. Make test and a full N2 are not run; main decides whether its landing needs them.

**Next work, in order:**
1. **R-25** (acked; queued first). `kit_class` must fold an offset-0 term into `proven0`/`proven_prev` only when the selected row TESTS it. A term the row may skip (OPTIONAL, untested) contributes nothing.
   - Landing bar: a kit fixture with an OPTIONAL offset-0 term the row skips (proven0 all-ones), the same with the row testing it, and zero artifact movers on every emit_sweep arm.
   - Branch `lane/memfn-r25`, cut from main **d18cee085 or later**. Opus lane; light work until the bench window closes.
   - It must land before any kit row may skip an OPTIONAL term and before [KIT-VERIFY]'s build.
2. **B4** (r17b_prime rev 3 §3.1): the routing commit and lockdown, ONE pcrec abi event. It waits on:
   - Frank's rev 4 direction (grid2's M9/M15: when predictability is unknown, default to V1 or the walk?);
   - D163 add. 8's layout controls (E1 has landed, so check whether that gate is satisfied);
   - E8 PASS and M0 per §3.1.
3. **The U1 design** (`docs/design/kit_proof.md`, drafted R-26: per-offset proven sets). It is main's lane `u1design`. Comment in responses.md once the note lands.

**OWED:**
- The five PRES rows' **g2 floors** stay PLACEHOLDER in `tests/memfn/row_floors.tsv`. G2's log has no per-row reach count: a small kit change (G2 REACH per row) would let them be pinned.
- D2 stays `pending-site:R-18`.
- candoracle's reach gap (it counts CANDROW reads, so an artifact selection move is invisible): main's check-design list.

**In flight:** nothing. No lanes, no chains, no watchers.

**Worktrees:**
- KEEP: `rowfix` (unmerged), `b3b-mt` (detached at c83a0a6d8, the last chain's pin, prunable), `memfn-slot` (scratch: b3bheavy*/, b3b/ logs).
- Prunable via `wtprune` now that B3b is on main: `b3b`, `memfn-b3b`, `b3afix`, `b3a`, `b3a-mt`, `b1fix`, `fdb2land`, `fdclass`, `memfn-fd`, `memfn-r23`, `r23*`, `r24*`, the fdb*-mt trees, `grid2read`, plus the older list in the git history of this file.
- `b3b/reach/wt` is a detached scratch tree; it is nested, so it needs `--force NAME`.

## 5. Next actions on wake

1. Create the heartbeat cron (`17,47 * * * *`), run ListAgents, read requests.md for new items.
2. Check whether the bench window has closed. Main announces the sentinel; until then, nothing CPU-bound.
3. Check whether main merged lane/memfn-rowfix. If not, ask main once.
4. Brief R-25: cut `lane/memfn-r25` from main, opus lane, landing bar as in §4.
5. Prune merged worktrees: `scripts/wtprune` dry run, then `--apply`; `--force NAME` for nested scratch.
