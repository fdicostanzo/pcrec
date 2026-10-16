# iterrev3 — `findall_iter.md` revision 3 (panel r5 discharged)

Lane `iterrev3`, 2026-10-16, opus, from main `37086a1db` (abi 78). Branch `lane/iterrev3`.
DESIGN lane: nothing under `src/`, `cli/`, `lib/` or `tests/` changed. One compile-only
hand-C probe (`docs/design/findall_iter/rev3/`).

## Summary

1. `docs/design/findall_iter.md` is now REVISION 3. It answers panel r5
   (`docs/dev/reviews/2026-10-16-r5-findall-iter-rev2.md`). Every finding is accepted except
   IT4, which D165 add. 3 rejects. §R3 maps each finding to its section.
2. No owner check (D165 add. 3). `owner`, its compare, IT4's setter store, S931 and the
   foreign-owner arm are deleted. Misuse across artifacts is UNDEFINED, stated in the spec's
   new §3.8 next to IT5's rule (subject, vars, descriptor and batch region immutable while
   the iterator is live).
3. Batch region (IT3 + IC3): it comes through a new unprefixed setter
   `rx_iter_batch(&it, ptrdiff_t (*)[2], npairs)`, with the capacity in pairs and K =
   npairs / NCAPS at bind. `<prefix>_buffers`, `emit_buffers_surface`, `<p>_no_buffers` and
   the bench `shim.c` are untouched, and no `<PREFIX>_BATCH_ENTRY_SIZE` is added. F11 is
   withdrawn as this design's cost.
4. One event (IC3). **The batch ABI is in I1 UNCONDITIONALLY. The fill is the `iterate`
   row's `batch` cell (`fill`/`off`), and the parity slot sets it before I1.** A later flip
   is one cell plus a mover census, never a layout event.
5. **S is DEFERRED to I2** (IC2). I1 has no `st`. S, the first held row, check 2 and
   S936/S937 land together inside I2's existing abi event, so nothing ships UNREACHED and no
   plan.md trigger row is needed. Check 1 is `S >= max` (IT7).
6. IT1: bind normalizes every optional field and writes K into `nbatch`. IT2: `__fill`
   ends without searching when a code is pending, and a counted-work cell detects it
   (`loads_drv.c`'s load counter). IT8, IT10-IT15 are applied as the panel proposed. IT12
   cites match_api.md §9.4¶4.
7. Q-I1 is still OPEN. §0.3, §2.1's meter column, §3.4 and §3.4a are CONDITIONAL on it,
   with per-logical-search as the design of record, and §3.4a states what changes under the
   literal reading. Q-I2 and Q-I3 are settled; Q-I4 (stride) is answer-free and left in
   discussion, with a leaning (full captures).
8. IC1: one plant and one population floor per residual twin (`_next_pos`, `_valid_upto`,
   `_var_valid`), checked on a `gcc -O2 -fPIC -c` build in `make test-codegen`
   (`tests/codegen/run_residual_twins.sh`). IC6: every detector names its target, and the
   ASan cells are built inside the new `make test-findall` section.
9. Measured: `sizeof(rx_iter)` is 96 B at I1 and 160 B at I2. Revision 2's layout was
   **152 B**, not the predicted 160 B (F14). The BOUND fast path is one `cmpl $imm32,
   (%rdi)` under `-fPIC`.
10. Validation: `bash tests/spec_history/run_spec_history.sh` (the file `make test`'s
    spec-history section runs) reports 145 passed / 0 failed. The first run caught line
    citations of numbered spec docs in the design and in the panel's text; they are now
    section labels. `layout.c` compiles clean with `-Wall -Wextra`, and §1.1's struct and
    setters text compiles clean under `-fanalyzer`. No suite run is owed: the lane changes
    docs only.

## For the manager

- **Sabotage allocation.** The new rows take S1038..S1046 (findall_iter.md
  §6.8; S1035-S1037 are compound_entries.md revision 4's): S1038 IT2 counted work, S1039 `_valid_upto` twin, S1040
  `_var_valid` twin, S1041 split's meter mirror (IC5), S1042 bind normalization, S1043 setter on
  ENDED, S1044 check order, S1045 NULL-caps local width, S1046 `S >= max`. S931 is withdrawn and
  retired.
- **Two readings to confirm.** (a) Under the IC2 deferral, D167 add. 1 A10's "S re-derived
  at the iterator's abi event" is read as "at the event that first holds a row (I2)". (b)
  Q-I4 is classed as an answer-free manager's call (memory
  `pcrec-answer-free-choices-are-mine`).
- **One claim to check at build.** S1011's DFA (`dfa-root`) cell assumes the DFA scan
  charges no step meter, so the plant reads identical there. The meters' codes are defined
  in the shared block, and a cell that finds otherwise is a finding.
- **Hand-offs** (findall_iter.md §11):
  - F16, the `compound_entries.md` revision 4 list (part rows `__enter`/`__fill`/`__deliver`/
    STEP, `__adv`'s stage label, the stale HELD lines `:54`, `:192`, `:440`, `:664`, `:757`,
    `:776`, `:781`);
  - F13's stale S cites in `r17b_prime.md` (kit manager) and `decisions.md:9707`
    (historical; annotate if wanted).
- **New unlocks** (no plan rows filed by this lane):
  - U16, the newline-aware retry advance (trigger: `DEF_NEWLINE_CONV` gains a producer);
  - U17, a general twin-forwarding check (trigger: `compound_entries.md` I3);
  - U18, debug-only misuse checks (trigger: the first user report).
- **New `make test` section named by the design:** `test-findall` (`tests/findall/`), built
  at I0/I1. It is a name in the design, not a Makefile change.

## Files

- `docs/design/findall_iter.md` — revision 3 (title, header, new §R3, §0-§11 revised).
- `docs/design/findall_iter/rev3/layout.c`, `rev3/out/layout.out` — the layout probe;
  `docs/design/findall_iter/CLAUDE.md` gains a `rev3/` section.
- `docs/dev/reviews/2026-10-16-r5-findall-iter-rev2.md` — the panel (copied from the main
  tree's untracked file) with a header, the manager verdict, and a disposition and
  discharge table at the end. Line citations of numbered spec docs are converted to section
  labels.
- `docs/dev/reviews/CLAUDE.md`, `docs/design/CLAUDE.md`, `docs/dev/lanes/CLAUDE.md` — index
  entries. The revision 1 descriptions are annotated as superseded (F13).
