# memfn wake — kit session hand-off (rewritten 2026-10-16 ~16:40, session close)

This is the kit session's orientation file. Run it as `/pcrec-memfn-manager`;
its §1 is the wake order. It is rewritten at every pause and holds the current
state. The history is `journal.md`.

## 1. Who you are and where you work

- You are the pcrec-memory-functions kit manager (`pcrecdev3`). The pcrec
  manager is "main" (`pcrecdev1`; run ListAgents).
- Main files requests in `requests.md` and is its only writer. You answer in
  `responses.md` and are its only writer.
- **Box:** the Linux dev box, repo `/home/pcrec/projects/pcrec`.
  - Use `gnutimeout` (bare `timeout` is uutils).
  - Commit with `git -c user.name="Frank DiCostanzo" -c user.email=frank@dicostanzo.com`.
- **THE KIT BRANCH IS `lane/memfn-fd`** (worktree `worktrees/memfn-fd`). It was cut
  from main 063b4a4b4 and has main @ 353249282 merged in. Builds and lanes are
  cut from it. `lane/memfn-r17` is the RECORD branch: old R17-b code at abi 77,
  never merged. Its compiler is what grid2 times the V1 arms with.
- Never merge to main, never push, never `cd` (use `git -C` and absolute paths).
- **Scratch:** `worktrees/memfn-slot/` (one dir per slot).

## 2. Read, in this order

1. `memfn/CLAUDE.md`.
2. `requests.md` on main (newest is R-21) and `responses.md` on lane/memfn-fd.
3. The tail of `journal.md` (the 2026-10-16 entries).
4. `docs/design/memfn/r17b_prime.md` REV 3 (THE design; §3.1 is the step plan)
   and the panel record `docs/dev/reviews/2026-10-16-r1-memfn-r17bp.md`.
5. On main: decisions D167 + addendum 1, D163 addendum 8 (layout switches),
   D165 + addenda.
6. Reports: `docs/dev/lanes/fdb0_report.md`, `fdb1_report.md`,
   `runaxes_report.md`, `grid2r3_report.md`, `comppin_report.md`.
7. BOILERPLATE before briefing.

## 3. Rules in force

- **The build hold is LIFTED (D167).** The R17-b′ build is GO (B0-B3b first,
  LOCKDOWN at B4) and the grid2 timing slot is GO.
- **Main's answers to Q-R17P-15..25 bind** (journal 2026-10-16). In particular:
  - Q-19: PCREC_NO_REQ_SET_LEAD is a WORKING ALIAS or a refusal, never a silent no-op.
  - Q-21: helpers follow D163 add. 8's RESOLVED layout controls.
  - S1017-S1025 = SN-1..SN-9; S1026 = runaxes.
- **/close (Frank, 2026-10-16):** never interrupt in-flight work. Wait for the
  lanes to finish, then close.
- One heavy suite at a time across both sessions. Agree each heavy slot with main.
  Lanes may run light work pinned `taskset -c 12-15 -j4`.
- A lane's rulings file only works if its brief says "re-read before EVERY heavy
  command" (grid2r3 missed a HOLD).
- Running lanes miss mid-run messages: settle scope before briefing.
- Heartbeat cron `17,47 * * * *`. Recreate it at wake, delete it at close.

## 4. Current state (2026-10-16 close)

**Delivered to main:**
- **B0** @ 10d9f43f4: the R17-a seam on main, MF_SITE_ABI 11, no pcrec abi event.
- Validation: make test 70/70, mech 57 rows clean, floored simd/comments sweeps 0
  movers, G2 full 199,850,927/0.
- Main is reviewing it. Its merge waits for main's evening chains, and main runs
  ONE integration make test on e0c + ksrc + B0.

**On lane/memfn-fd, NOT yet delivered:**
- **B1** (fdb1, merged @ 6800f833b): the finder table in shadow, mf_ask, the
  mf_analysis slot, R-MS1..5 seams; MF_SITE_ABI 12.
  - Light checks green: strict, spec-history, registry 79/0, G2 quick 52,987,691/0,
    finder 868/0.
  - OWED (heavy slot): full make test, mech derived rows, G2 full, N2 census.
  - Findings to act on:
    - (a) R0/R7's floor token: fdb1 picked `kit.eps.findall.l64k`. CHECK it
      against rev 3 §2.5 / C4 (regime-matched floors).
    - (b) fields.def class space is full at 64.
    - (c) the record branch's R17-b also claims MF_SITE_ABI 12: renumber at B4.
    - (d) F-B1-3, an MLINE ATTEMPT reader disagreement, goes to B2.
    - (e) an emit_sweep one-sided ASSERT_ZERO mode for new denies is owed.
- **runaxes** (merged @ 8c549afea): run_axes.sh `--memfn=` arm, S1026 DETECTED,
  AXES=--memfn answer-identical. It is MAIN's file, for main's review with the
  next delivery.
- **comppin**: COMPOSITION_EXTRA_PINS for -fmemfn-simd/-fcomments (37/106).
- The close-skill edit (9175611a3).

**IN FLIGHT: grid2 ARMED.**
- `worktrees/memfn-slot/grid2/arm.sh` (detached, armed 15:52) waits for `grid2/.go`.
  Main touches it ~18:00 on a quiet box.
- The run: `worktrees/grid2r3/docs/dev/lanes/grid2/slot.sh`, CPU 14, ~75-80 min,
  compiler worktrees/memfn-r17/build/pcrec (c90d65e53, abi 77).
- Status: `grid2/arm.status` (ARMED → TRIGGER → SLOT_EXIT) and `grid2/slot.status`
  (ends COMPLETE or FAILED).
- If arm.sh died before TRIGGER, re-run it detached:
  `setsid nohup bash /home/pcrec/projects/pcrec/worktrees/memfn-slot/grid2/arm.sh >/dev/null 2>&1 </dev/null & disown`.
- A red stage gets a TRIAGE lane before you read its log.

**Waiting on main / Frank:**
- B0's review and merge.
- Heavy slots for B1's owed runs.
- The I-152 bench answer.
- D163 add. 8's layout controls (compound_entries rev 4, lane cmprev4) before B4's helpers.

**Worktrees:**
- Keep:
  - memfn-fd (the kit branch);
  - memfn-r17 (the record branch + grid2's compiler);
  - memfn-slot (scratch);
  - grid2r3 (slot.sh runs from it);
  - fdb0 (its ref063 reference binary);
  - fdmech and fdb0-mt (logs, prunable after B0 merges);
  - fdb1 (logs).
- Prunable via wtprune once merged: fddocs, sweeparm, grid2p, r17bp4, comppin,
  runaxes, and the 10-14 list (costmodel, regeval*, sbscope, pcscope, winreq,
  r17bp, r17bp3, gridread).

## 5. Next actions on wake

1. Recreate the heartbeat cron, run ListAgents, read requests.md for new items.
2. Read grid2's result (arm.status / slot.status). If COMPLETE, a READING lane
   (sonnet) works against rev 3 §5.4/§9.3, both layers, and reports constants and
   predictions to main.
3. Ask main for the heavy slot for B1's owed runs, then deliver B1 (+ runaxes).
4. Brief B2 (ST2: one-byte FIND routed; rev 3 §3.1 row B2), with F-B1-3 and the
   Q-19 alias rule in the brief. B2 waits on nothing else; E-1 (main) follows B2.
5. Before E5: the evaluator-params digest work (rename the domain to
   `pcrec-evaluator-params-1`, recompute independently).
