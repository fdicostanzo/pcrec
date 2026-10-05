# memfn wake — kit session hand-off (rewritten 2026-10-05, end of the first kit session)

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
  `lane/memfn-r4a`, cut from main 2ed263a7 for R-3, which is not filed
  yet. FIRST command: `git -C /Users/fdicostanzo/pcrec/worktrees/memfn
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
4. `docs/design/memfn/integration.md`: §R4.6 first, then §R4.5, §R4.4,
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

## 4. Current state

- **Kit code:** none. The next code step is R4a (the skeleton), to be
  filed as R-3 after Frank rules Q53-Q55.
- **Requests:** R-1 DONE (merged 348c0a49). R-2 DONE (merged 2ed263a7).
  No open request.
- **Open questions (Frank, relayed by main 2026-10-05):** Q53 (the libc
  record), Q54 (N7 pending), Q55 (the plan at SIMD-off). The kit's
  recommendations are in `docs/dev/reviews/2026-10-05-r5-memfn-rev45.md`
  (last section) and in `responses.md` R-2 done:.
- **Design of record:** integration.md rev 4.6.
- **Measured facts to carry into R4d:**
  - the R4d trigger is MET at SIMD-off on union-select;
  - the lead order is part of R4d's one form, lead-first;
  - `swar` scans at ~0.18 ns/B and loses on early-hit single gate calls
    on dense text (a Q48 candidate, judged at R4d's G1);
  - its 2x unroll is an `UNMEASURED DEFAULT:`.
  Source: `docs/dev/lanes/memfnr4b_report.md` §9.
- **For R4c/R4d (noted by main):**
  - A4: ~28 mech rows anchored in M1 emitters are re-pointed in R4c's
    REPLACE commit;
  - A3: `@idx`/`REQ_BYTE`/[OPT-REQPOS] are re-specced as pcrec's pick
    in R4d's D80 hunk;
  - A1: the set-leads lead is REQUIRED on no-DFA routes.
- **Defects:** none open.
- **In flight:** nothing. No lane is running and no box run is owed.
  Old lane worktrees (memfnr4b, memfnr45, memfnr46) remain under
  `worktrees/`. Their branches are merged; removing them is main's
  call (worktree rm is not covered by the merge permission).

## 5. Next actions

1. Wait for R-3 (R4a) in `requests.md`. Ack it, and re-cut the branch
   if main has moved (or merge main into `lane/memfn-r4a` ALONE in its
   own command, then `make strict`).
2. R4a is the kit's first CODE: `memfn.h`, the `mf_*` entry points, the
   generic scalar row with G2's generated-space tests, K1 reference
   functions, `PROVENANCE.md`, the Makefile wiring (C15/C16), an EMPTY
   `src/options.def` with `mf_options()`/`mf_opts_check()`, the
   `--list-axes` `memfn` section header, and the site manifest with
   C17 (every row `pending`). Zero byte moves. Plan the lanes:
   - opus for `memfn.h` and the contract;
   - a D27-blinded author for G2 (`scripts/mk_d27_cell.sh`);
   - sonnet for the wiring and docs.
   Read coding_guide.md first.
3. Critic and lane briefs: findings go to a scratchpad file and the
   reply gives the path (two critics' messages truncated). Each lane
   adds its report to `docs/dev/lanes/CLAUDE.md` in the same change.
