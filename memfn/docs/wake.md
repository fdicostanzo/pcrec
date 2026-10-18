# memfn wake — kit session hand-off (rewritten 2026-10-17 ~22:50, session pause on Frank's request)

This is the kit session's orientation file. Run `/pcrec-memfn-manager` and follow its §1, the wake order. This file is rewritten at every pause and holds the current state. History lives in `journal.md`.

## 1. Who you are and where you work

- You are the pcrec-memory-functions kit manager (`pcrecdev3`). Main is `pcrecdev1`; run ListAgents to find it.
- `requests.md` is main's to write, and only main writes it. `responses.md` is yours to write, and only you write it.
- **Box:** the Linux dev box, repo `/home/pcrec/projects/pcrec`. Use `gnutimeout`. Commit with `-c user.name="Frank DiCostanzo" -c user.email=frank@dicostanzo.com`.
- **MERGES GO THROUGH MAIN** (Frank, 2026-10-17) until he adds the kit's merge permission rule. For each merge, send main the lane branch, its sha, the target branch and the validation. Main merges, runs strict and reports the sha back. Lanes may merge MAIN INTO their own lane branch.
- **Kit branches:** one per delivered unit, cut from main.
  - `lane/memfn-b3` (worktree `worktrees/memfn-b3`) carries the ledger for B3a: the B3a notice, R-24's done, and this file. It merges to main along with B3a.
  - `lane/memfn-r23`, `lane/memfn-fd` and `lane/fdb2land` are delivered.
- Never `cd` into a worktree (I slipped three times this session). Use `git -C` and absolute paths.

## 2. Read, in this order

1. `memfn/CLAUDE.md`.
2. `requests.md` (newest is R-24) and `responses.md`.
3. The tail of `journal.md`.
4. `docs/design/memfn/r17b_prime.md` rev 3: §3.1 is the step plan, and B3b is next after B3a.
5. `docs/dev/lanes/b3a_report.md` §9 (review fixes and rebase); `docs/dev/lanes/grid2read_report.md` (M9/M15 contradicted).

## 3. Current state

**On main:** B0, B1, B2 (+ R-22), R-23, R-24 + E-1. MF_SITE_ABI is 15; pcrec abi is 79.

**B3a is READY BUT NOT DELIVERED.**
- Branch `lane/b3afix` @ **4ecc07d5b** = B3a + review fixes + main e368410e7 + main's three proposed diffs as their own commits.
- MF_SITE_ABI 16, no pcrec abi event.
- Main has ACCEPTED its main-side pieces and will merge it as one unit once its heavy chain is complete.

**B3a's heavy chain was CANCELLED midway** (Frank's request). Pinned worktree `worktrees/b3a-mt` @ 4ecc07d5b; scratch `worktrees/memfn-slot/b3aheavy/` (chain.sh, chain.status, mech/summary.txt, logs/).
- DONE: build, strict, full make test GREEN (perfrun label b3a, 22:14; it is also main's integration test), and 28 solo mech rows.
- S1029 reads BAD only because the copied scorer special-cases S919 alone. S1029 is declared SAB_EXPECT=UNREACHED and its unreached=1 is expected: treat it as OK, and fix the scorer to read SAB_EXPECT.
- **TO RESUME:** a fresh sonnet lane builds `chain2.sh` in the same scratch dir, against the same b3a-mt pin, covering the steps NOT yet run:
  1. mech SOLO S739 S811 S812 S995 S1093 S1094 S1095 S1096 S1097 S1098 S1099 S1100 S1101 S1102;
  2. `make test-memfn-g2-full`;
  3. the N2 census + `n2_report.py --floors tests/memfn/row_floors.tsv --propose`;
  4. `MEMFN_REACH_ONLY=1 AXES=--memfn bash tests/axes/run_axes.sh`;
  5. the form census.

  Use anchored CHAIN COMPLETE / CHAIN FAILED lines, and a scorer that honours SAB_EXPECT. About an hour in total. Agree the slot with main first.
- On green: post `done: R17-b′ B3a` (lane/b3afix @ 4ecc07d5b, with the validation) on lane/memfn-b3 and send it to main.

**Next after B3a:** B3b (route PRES rows and D2; retire bit 45 to `--memfn=no-pres-set-lead`, keeping the PCREC_NO_REQ_SET_LEAD alias working (Q-19); handoff framing (a)). It is covered by D167's GO. B3a's review notes for B3b:
- re-run the KW-8 shadow on the kit-sourced `proven0` (P2);
- the deny arms and a measured bundle must stay at 100%.

**Waiting on Frank:**
- the merge permission rule;
- the rev 4 design direction before B4 (grid2's M9/M15: when predictability is unknown, default to V1 or the walk?).

**Worktrees:**
- KEEP: memfn-b3, b3afix, b3a-mt, memfn-slot.
- Prunable via wtprune once merged: memfn-fd, memfn-r23, fdb2*, fdclass, b1fix, r23*, r24*, fdb1-mt, fdb2-mt, grid2read, fdb2drop, and the older list in the previous wake.

## 4. Next actions on wake

1. Recreate the heartbeat cron (`17,47`), run ListAgents, read requests.md.
2. Ask main for the slot, then resume B3a's chain (§3); on green, deliver.
3. Brief B3b once B3a is on main.
4. Prune merged worktrees (wtprune dry run, then `--apply`).
