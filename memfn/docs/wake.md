# memfn wake — kit session hand-off (rewritten 2026-10-07 evening; pcrec dev moving boxes)

This is the orientation file for the kit session, run as
`/pcrec-memfn-manager` (`.claude/skills/pcrec-memfn-manager/SKILL.md`;
its §1 is the wake order). It is rewritten at every pause and holds the
current state; the history is `journal.md`.

---

## 1. Who you are and where you work

- You are the pcrec-memory-functions kit manager. The pcrec manager
  ("main") files requests in `requests.md`; you answer in `responses.md`
  (you are its only writer).
- **THE BOX CHANGED (2026-10-07).** Frank moved pcrec development to a new
  Linux box, `pcrec@192.168.1.17`, with the repo at `~pcrec/projects/pcrec`,
  cloned from GitHub. ubuntubudu stays the bench's box, and the Mac stays
  for hardware runs. The kit branches were PUSHED to origin at wind-down
  (§4). On the new box: create your kit worktree under `worktrees/` from
  the branch you continue, and re-check the box rules (lock path, timeout
  binary, whether there is a suite lock at all) in the root CLAUDE.md and
  docs/testing.md "The boxes". Old Mac paths in this file are history.
- One branch per delivered unit. Never merge to main yourself. Push only
  when Frank or main says so; he authorised the wind-down push.

## 2. Read, in this order

1. `memfn/CLAUDE.md`.
2. `memfn/docs/requests.md`, then `responses.md`. The newest entries there
   are the ROWCON notices, the R-5 `done:`, and the N2 R-6 list (if posted
   before wind-down).
3. The tail of `memfn/docs/journal.md`.
4. `docs/design/memfn/row_contracts.md` **rev 4.1**: [MEMFN-ROWCON],
   narrowed by Frank to the K96 generalization. Its §6 HOLDS (engine,
   snapshot, listing) and their triggers.
5. Memory notes from today:
   - `pcrec-kit-row-contracts`;
   - `pcrec-no-silent-defaults` (refined: a USED default is the bug,
     unused fields are wildcards);
   - `pcrec-no-addenda-to-running-lanes`;
   - `pcrec-taskstop-kills-detached-runs`;
   - `pcrec-box-concurrency` item 12 (numeric caps on sweeps; lanes
     still overran them "for timing").

## 3. Rulings today (Frank)

- **ROWCON scope:** build ONLY the K96 generalization:
  - per-row `uses`/`serves`;
  - one gate (define AND use phases);
  - decline reasons in the kit's `MF_TRACE`;
  - reach floors;
  - R1 (a row uses only STATED values; unstated fields are wildcards);
  - R2 (a stated value the row does not serve → decline).
- **HELD, with triggers:** the general table engine (Q-ROW-4's charter
  widening is ruled, but it is built only when a real table adopts it);
  the hook SNAPSHOT (Q-ROW-1(c)/Q-ROW-6 ruled; the trigger is a measured
  risky hook). The hook census found NONE
  (`probes/rowcon/hook_census.md`). Re-run it at every migration step
  that adds or changes a hook.
- Proposed decision entries for all of these are in `responses.md`; main
  files them in decisions.md.

## 4. Current state

**Branches pushed to origin at wind-down:**
- `lane/memfn-rowcon`: ROWCON design rev 4.1, reviews r1-r4, the audits,
  hook_census; **N1 merged** (fields.def, uses/serves on all 8 rows, the
  WARN gate at define/use/run, MF_TRACE, trace_format.md, the written
  exemptions); the N2 driver (`probes/rowcon/n2_census.sh`, `.py`,
  `n2_report.py`); main merged in at 5fc4b0e5. NOT yet delivered to
  main: it waits for N2 → R-6 → G2u → N3.
- `lane/memfn-g2x`: R-5 (M1b) `done:` + journal (M1b is on main as
  1c037dce).
- `g2x`: lane g2x's BLINDED G2 reach extension, INTERIM and unreviewed
  (5be6fe58).
  - Run 1: 42.76M passed, 138 failed, 0 faults, 0 sites failed.
  - Report: memfn/tests/G2X_REPORT.md.
  - Findings, owed to triage:
    - **F1:** runcmp/precheck paste hook text raw, so batches 077/079
      fail to compile. G2 uses ternary hook text, which is legal
      contract input today. ROWCON N3's IDENT class would route it to
      generic. Confirm F1 is exactly that cell.
    - **F2:** `MEMFN_LIBC` reads "none" although the kit renders
      memchr/memcmp (§R4.3.3). It may be G2-path-only, since pcrec's
      C11 is green. Verify against pcrec artifacts before calling it a
      pcrec stamp defect.
    - **G1:** W2 mutation-7's kill rate fell to 53% (G2-side; remedy
      owed).
    - **Notes:** N1 (`miss` NULL handled differently per arm: ROWCON's
      R1 covers it) and N2 (`mf_art_begin` prefix pointer lifetime
      unstated).

**N2 (the census):** launched 15:11 on the Mac, holding the lock. Its
results are in `worktrees/memfn/build/scratch/n2_main_5fc4b0e5/n2_results.md`
on the MAC (build/ is not in git). The R-6 list from it is posted in
`responses.md` if N2 finished before wind-down; otherwise re-run N2 on
the new box, which needs the trace-build path checked there.

**ROWCON next steps:**
1. R-6 (main files it): pcrec states `MF_MISS_N` where the chosen row
   uses `miss`. Expected: the ofsskip site (define + call) and precheck's
   ASSIGN use, and whatever else N2 lists.
2. G2u: the blinded G2 update. Fold g2x's interim work in, plus the
   explicit values, the poison and SEMANTIC differentials, and per-row
   floors.
3. N3: enforce. ENTRY: N2 re-run after R-6 shows zero would-decline at
   both phases, plus the identity gate.
4. N4: rows.tsv, signatures, floors.

**Owed elsewhere:** M7 scope +1 (K94's defs_bref_ci_ucp, N7-pending).

## 5. Next actions on wake

1. Make the kit worktree on the new box from `lane/memfn-rowcon`. Read
   requests/responses: has main filed R-6?
2. Triage g2x's F1/F2 with ONE read-only agent (F2 first: is any pcrec
   artifact's MEMFN_LIBC wrong?).
3. Continue ROWCON from §4. Every brief carries every ruling, with
   NUMERIC caps and no timing runs outside the lock.
