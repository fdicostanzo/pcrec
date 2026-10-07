# memfn wake — kit session hand-off (rewritten 2026-10-07, R4c merged, R4c′ queued, clean reset)

This is the orientation file for the kit session, run as
`/pcrec-memfn-manager` (`.claude/skills/pcrec-memfn-manager/SKILL.md`;
its §1 is the wake order). It is rewritten from scratch at every pause:
the current state, never a history (the history is `journal.md`).

---

## 1. Who you are and where you work

- You are the pcrec-memory-functions session, the kit's manager, working
  `memfn/` inside the pcrec repository. The pcrec manager ("main",
  session pcrecdev1) files requests in `requests.md`. You answer in
  `responses.md` (you are its only writer; never edit `requests.md`).
- Your worktree: `worktrees/memfn`. One branch per delivered unit, cut
  from a main that contains the request. The current branch is
  `lane/memfn-r4c2` (see §4). FIRST command: `git -C /Users/fdicostanzo/pcrec/worktrees/memfn
  rev-parse --show-toplevel`. Never merge to main, never push, never
  `cd` into another tree.
- Scope mandate: write only inside your worktree, your lanes' worktrees
  and the session scratchpad. pcrec-bench is read-only. Main owns
  plan.md, decisions.md, known_issues.md, the site manifest and
  `DELEG_SITES`.

## 2. Read, in this order

1. `memfn/CLAUDE.md`: the layers (D147), the option namespace, the
   boundary, the same-commit abi rule, D149's line.
2. `memfn/docs/requests.md`, then `responses.md` (open = no `done:`).
3. The tail of `memfn/docs/journal.md`.
4. `docs/design/memfn/integration.md`: §R4.7 first, then §R4.6, §R4.5, §R4.4,
   §R4.3, §L. Then the sections the request names (§14 contract, §15
   site shapes, §17 guards, §18 stamps, §22 build order, §23 Q53-Q55).
5. `docs/dev/lanes/BOILERPLATE.md`; `docs/dev/coding_guide.md` before C;
   `docs/dev/learnings.md` §3 before a check.
6. Decisions on demand: D144, D145, D146, D147 (+ addenda 1-9), D149
   (constants: measured, derived, compiler-chosen, or labelled
   `UNMEASURED DEFAULT:`), D76/D94, D80.

## 3. Box and suite rules (summary; BOILERPLATE wins on conflict)

- One heavy suite per box across BOTH sessions; agree slots with main.
  The Mac suite lock `worktrees/.mac-suite.lock` is main's lanes'. Do
  not take it without main's agreement.
- Verdicts are Linux (ubuntubudu), via MAIN's executor channel only:
  commit a pinned script on your branch and send main the path, the
  expected wall time and the completion line. Mac runs are directional.
- macOS ASan has no LeakSanitizer. A probe that passes Mac ASan can
  still fail Linux LSan (R-1's first run did).
- Every acceptance reading reports SIMD-off AND SIMD-on (D147).
- A change that moves a pcrec byte carries the abi bump, re-pins found
  by grep, the stamp values, the spec hunk and G1 at both layers, all in
  the SAME commit.

## 4. Current state (2026-10-07, early morning)

- **Branch:** `lane/memfn-r4c2` in `worktrees/memfn`, cut from main 81bc13de
  (R4c merged). Its commits so far are ledger, journal and wake only.
- **On main:** R-1, R-2, R-3 (R4a, R4a′) and **R-4's R4c** (merge 81bc13de,
  abi 65). The kit renders the composite PRE site and the offset-skip trio
  (`memfn/src/ofsskip.c`, `precheck.c`), with ZERO MOVERS. MF_SITE_ABI is 3
  (Q-G2-18 `on_miss_leaves`). The `-fno-memfn-simd`/`-fmemfn-simd` pair
  exists and is inert. Edits to the migrated emitters are kit work.
- **NEXT JOB: R4c′**, the pcrec manager's review fixes. The full list is the
  responses.md R-4 note of 2026-10-07: items (a)-(g) + nits. None moves a
  byte. **(a)+(b) gate main's C1 (the start-table fold): do them first.**
  - (a) re-pin docs/dev/lanes/r4ccore_report.md §3's B1-B18 to line numbers
    on current main;
  - (b) add the two missing decision reads (emit_dfa.c:1517 req_run
    len>=2; ofs_pred_of's need classification :1095-1104);
  - (c) fail the compile in pcrec_emit_req_byte_check (:1503) when
    `job->mf_pre` is NULL and the admission says a pre-check is emitted;
  - (d) an inert-branch plant in `memfn_r4c_i2.py --selftest`;
  - (e) C11: compile -fmemfn-simd too, or fix libc_census.py's docstring;
  - (f) replace the EMPTY `tests/memfn/c4_populations/gcc15.2-x86_64-ubuntubudu/m_lahf-lm.txt`
    with the re-probed `m_sahf.txt` (ready at
    `worktrees/r4c-lx-results/gccmacros2/m_sahf.txt`, 15.5 KB), and make
    population loading FAIL on an empty dump;
  - (g) S524/S525 get the `checks failed: 0` reach line;
  - nits: S511's header prose; `strategy_denials` naming at lib/pcrec.h:1128
    and tuning.md §2.43.
  - Validation: make strict, the touched sections, the solo mech rows (ONE
    id per matrix call), and the zero-mover gate `python3
    scripts/emit_sweep.py --ref 81bc13de` judged by
    `docs/design/memfn/probes/lxrun/memfn_r4c_gate.py`. Then post R4c's
    `done:`; the draft is `worktrees/r4cscope-scratch/r4c_done_draft.md`
    (fill in the TIP; add R4c′). Then deliver the branch to main.
  - Plan: one opus lane. Its worktree `worktrees/r4c2fix` (branch
    lane/r4c2fix) is already cut from lane/memfn-r4c2 and is EMPTY.
- **Linux re-runs:** `memfn_r4c.sh` supports STEPS / TESTSECTIONS / MECHROWS /
  I2ARMS (lxrun/CLAUDE.md). Linux runs go through main's executor.
- **Sabotage ids:** S510-S529 are USED; the next block is S530-S549
  (main, 2026-10-06).
- **Main's backlog from R4c** (main's admin lane, not ours): (a) the
  matrix should refuse ids after the first; (b) an expected-build-failure
  verdict; (c) trailer counters on the verdict column only; (d) an
  emit_sweep default-arm-only composition floor (it would retire the 3
  I2 declarations).
- **Owed (kit):** G2 (blinded) coverage of the newly refused shapes and of
  `on_miss_leaves` at both values; Q-G2-5 (M3).
- **Leftover worktrees:** `r4clx`, `r4clx2` (merged; prune with
  scripts/wtprune once >120 min idle); `r4c2fix` (R4c′'s, empty);
  `r4cscope-scratch` and `r4c-lx-results` (scratch, gitignored; keep until
  R4c′ delivers). Also the nested memfng2 + cell (Frank's raw-removal
  list) and `memfnk0r3` (pre-kit, unmerged; ask Frank).
- **Box rules this session taught:**
  - run_sabotage_matrix.sh takes ONE id per call;
  - each mech row is ~10 min of full harness, so many rows go to Linux;
  - ask main for the Mac suite lock;
  - a busy in-process lane does not read messages; put rulings in the
    brief.

## 5. Next actions

1. Wake: create the heartbeat cron (17,47). Read requests.md /
   responses.md (the R-4 note of 2026-10-07 is the R4c′ list). Check
   whether main has filed R-5.
2. Brief the R4c′ opus lane in `worktrees/r4c2fix`, with (a)+(b) FIRST.
   Merge it into lane/memfn-r4c2 (alone, then make strict). Run the gate
   vs 81bc13de, post R4c's done:, and deliver.
3. Then R-5 as main files it. The likely candidate is R4d (the first
   movers: SWAR fused composite; trigger MET) or M1b/R4g (zero-mover
   migrations).
