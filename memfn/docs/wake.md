# memfn wake — kit session hand-off (rewritten 2026-10-14, session close)

This is the kit session's orientation file. Run it as `/pcrec-memfn-manager`;
its §1 is the wake order. It is rewritten at every pause and holds the current
state. The history is `journal.md`.

## 1. Who you are and where you work

- You are the pcrec-memory-functions kit manager (`pcrecdev3`). The pcrec
  manager is "main" (`pcrecdev1`; run ListAgents). Stale sessions can share a
  name.
- Main files requests in `requests.md` (it is the ONLY writer). You answer in
  `responses.md` and are its only writer.
- **Box:** the Linux dev box, repo `/home/pcrec/projects/pcrec`.
  - Use `gnutimeout` (bare `timeout` is uutils).
  - Commit with `git -c user.name="Frank DiCostanzo" -c user.email=frank@dicostanzo.com`.
- **The kit's RECORD branch is lane/memfn-r17 (worktree `worktrees/memfn-r17`).**
  It carries the kit's docs, ledger and reports, plus OLD R17-b code at abi 77.
  - It does NOT merge cleanly with main (17 conflicts, aborted). Do NOT
    merge main into it.
  - Ship docs to main via a docs-only branch cut FROM main (like
    lane/memfn-docs, already merged).
  - BUILDS go on FRESH branches cut from main.
- Never merge to main, never push, never `cd` (use `git -C` and absolute
  paths; `cd` moved the session cwd twice this session).
- **Scratch:** `worktrees/memfn-slot/` (one dir per slot).

## 2. Read, in this order

1. `memfn/CLAUDE.md` (boundary table now includes the regime table, evaluator
   and measurement sets).
2. `requests.md` on MAIN (R-19, R-20, R-21 are newest) and `responses.md` on
   lane/memfn-r17 (the last notices: R17-b′ rev 2, the pause notice).
3. The tail of `journal.md` (2026-10-13/14).
4. `docs/design/memfn/r17b_prime.md` rev 2 (THE design; §9 questions) and
   `docs/design/memfn/regime_eval.md` rev 2.4 (the evaluator; §3.0a parameter
   table = `regime_eval/regime-eval.evaluator-params.tsv`).
5. Main: `docs/design/regime_tables.md` (rev 0.4+), `docs/design/measure_sets.md`
   (rev 2.1), decisions D161 add. 11-15, D165, D166 (+ add. 1/1.1/2), [KNOW-SRC].
6. `memfn/docs/finder_history.md` (row edits until LOCKDOWN, D161 add. 13).
7. BOILERPLATE before briefing.

## 3. Rules in force

- **BUILD HOLD (Frank, 2026-10-14):** design notes and D6 panels only. No
  build lane, no E3, no timing/slot run (grid2 included) without Frank's
  explicit go for that item, relayed by main. An agreed order is NOT a go.
- **D166:** measurements are SETS (one box, one run, one method), relative
  units, versioned; A = the set id, I = ISA. **D166 add. 1:** perf counters are
  NEVER required (an optional diagnostic that skips loudly; scripts print the
  paranoid suggestion and never act on it).
- **D161 add. 13:** until LOCKDOWN (the table passing the judge plus R17-b′'s
  routing commit = B4) the kit edits rows freely. Log every edit in
  finder_history.md and tell main.
- One heavy suite at a time across both sessions; ask main for the GO before
  any slot. Light work needs no slot.
- Running lanes MISS mid-run messages (it happened four times this
  session). Settle scope before briefing; apply new rulings with a short
  follow-up lane and VERIFY them in the delivery.
- Heartbeat cron `17,47 * * * *`. Recreate it at wake, delete it at close.

## 4. Current state (2026-10-14 close)

- **Nothing is running.** Main is closed.
- **R17-b′ design rev 2** (`docs/design/memfn/r17b_prime.md`, @ 158b83a85):
  - 21 rows (15 FIND, 6 PRES), with D1 + R7 = Q-WR-1's UNMEASURED-DEFAULT;
  - steps B0-B3b are a ZERO-MOVER first delivery (MF_SITE_ABI 10→14, no pcrec
    abi event);
  - B4 is the one censused mover = LOCKDOWN;
  - B5-B9 come later;
  - 8 ABSENT measurement families (M16-M23).
  - **Its D6 panel is the NEXT kit work** (allowed under the hold). Use 3
    critics: contract-vs-main-emitters/opus, zero-mover+checks/sonnet,
    measurement+sets/sonnet, plus an unlock lens.
- **regime_eval rev 2.4:**
  - Frank's rulings are applied: the lean plan, the constants plus both
    loosenings, k = 3 as a visible lever.
  - The parameters are the [KNOW-SRC] kind `evaluator-params`.
  - OWED before E5: declare the value vs provenance columns, rename the
    domain to `pcrec-evaluator-params-1`, recompute the digest with an
    INDEPENDENT script, and record the domain in the header.
- **Waiting on Frank (via main):**
  - the zen4-grid2 go (≈88 min required / 96 with optional items; it needs a
    grid1 harness extension first, also held);
  - Q-R17P-9..14;
  - the build go for B0-B3b.
- **Waiting on the bench:** I-152 (can the kit import the bench's text libs
  with kit seeds?). The default path is a byte transfer arranged by main.
- **Population facts (sbscope, compiled):** 170/172 rwquest questions have a
  start-search site. J1b is SEALED (sha f41abc63…, 165 rows; unseal only at the
  J1b judge step).
- **Sabotage ids:** S911-S922 and S964-S980 are mapped per step; B6 needs new ids.

**Worktrees:**
- Keep: memfn-r17 (the record branch); memfn-slot (scratch: spike1, grid1 logs
  that gridread reads); grid1 (its harness, docs/dev/lanes/grid1/, is merged
  but slot.sh is run from that worktree).
- Prunable via wtprune (merged into lane/memfn-r17): costmodel, regeval,
  regeval2-7, sbscope, pcscope, winreq, r17bp, r17bp3, gridread, memfn-docs
  (merged into main).
- slotpc: a detached main build at 3182dddf5, used for slotarms. Prunable.
- Older ones are as listed in the previous wakes.

## 5. Next actions on wake

1. Recreate the heartbeat cron, run ListAgents, and read requests.md on main
   for new items (ack them).
2. Run R17-b′ rev 2's D6 panel (read-only critics). Consolidate in
   docs/dev/reviews/YYYY-MM-DD-rN-memfn-r17bp.md; a revision lane follows.
3. If main relays a grid2 go: brief the grid1 extension for grid2's spec
   (r17b_prime rev 2 §4), check it, then run the slot detached.
4. Before E5: the evaluator-params digest work.
