# memfn wake — kit session hand-off (rewritten 2026-10-06, R4a′ closed, waiting for R-4)

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
  `lane/memfn-ledger` (see §4). FIRST command: `git -C /Users/fdicostanzo/pcrec/worktrees/memfn
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

## 4. Current state (2026-10-06, day)

- **Branch:** `lane/memfn-ledger`, cut from main c9c98e98 (which holds
  everything the kit has delivered), in `worktrees/memfn`. It carries
  only ledger/wake/journal commits; hand it to main for merge.
- **Merged to main:** R-1, R-2, R-3 part 1 (R4a), R-3 part 2 (R4a′, abi
  63, 340d8fef). START-SET stage 3 is abi 64 on top (8148e034). R-3 is
  CLOSED: its `done:` for R4a′ is in responses.md.
- **R4a′ verdict (Linux):** 53/53 ran; one check-side red
  (test-encoding-checks) was fixed on main by lane enctri. The census was
  CLEAN vs 57db5152.
- **NEXT REQUEST: R-4 = R4c, the M1 migration.** Main is sequencing it
  with Frank against main's start-table refactor: both touch
  emit_dfa.c's offset-skip/PRE sites. **Do NOT start R4c code before R-4
  appears in requests.md.** Reading integration.md §22 (R4c) and
  the manifest rows it names is fine meanwhile.
- **Sabotage ids:** they serialize through main. S510-S529 are USED; the next block is S530-S549 (main, 2026-10-06). Old note:
  S510-S529; the next free is S518.
- **Box rule:** a lane's long or multi-section Mac run takes
  worktrees/.mac-suite.lock (directory + owner file, released on exit);
  quick single sections don't need it. Linux verdicts go through main's
  executor.
- **Owed:**
  - G2 coverage of the newly refused shapes. A blinded cell runs from
    the MAIN tree (that code is on main now); never nest a cell;
  - Q-G2-5 (M3);
  - C11's FORMS half, UNREACHED until the first form;
  - main's `--base REF` option for mk_d27_cell.sh, built when a
    kit-branch-only cell is chartered.
- **Leftover worktrees:** `memfnstamp` and `memfnbump` were pruned
  2026-10-06. The nested `worktrees/memfn/worktrees/memfng2` + `-cell`
  is on Frank's list (raw remove only). `memfnk0r3` is pre-kit and
  unmerged (ask Frank).

## 5. Next actions

1. Wait for R-4 in requests.md. Ack it on a fresh branch cut from a
   main that contains it (`git -C worktrees/memfn switch -c
   lane/memfn-r4c main` once this ledger branch is merged).
2. Plan R4c's lanes from the request. Each migration step is ZERO-MOVER
   (pre-migration text is the byte-identity comparator for that step
   only), under the checked manifest (C17: the migrated sites flip
   `pending` → `delegated`). Read coding_guide.md and memfn/CLAUDE.md's
   boundary table first.
3. Critic and lane briefs: findings go to a scratchpad file and the
   reply gives the path. Each lane adds its report to
   `docs/dev/lanes/CLAUDE.md` in the same change.
