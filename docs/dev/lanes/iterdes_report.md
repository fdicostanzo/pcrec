# iterdes — [FINDALL-NEXT] design lane report

Lane `iterdes` (opus), 2026-10-14, branch `lane/iterdes` from main `ee01f4dbb` (abi 78).
DESIGN ONLY: nothing under `src/`, `cli/`, `lib/` or `tests/` changed. No clock was read.

## Delivered

- `docs/design/findall_iter.md`, the design note (revision 1).
- `docs/design/findall_iter/`, its probes, with their own CLAUDE.md:
  - `sem/`, the semantics probe against libpcre2;
  - `twin/`, the iterator hand twin on real artifacts.
- `docs/design/CLAUDE.md` gains two entries; `docs/dev/lanes/CLAUDE.md` gains one line.

## What the note settles (brief items 1-7)

1. **Layout.** A stable 8-byte prefix (`hdr`, `rc`), then `flags`, `lo`, `s`/`n`/`owner`,
   `vars`/`nvars` and `st[S]`.
   - S = 56 B at alignment 8. It is derived from a storage-row table: kit FIND + H 32,
     pcrec K5 pair hits 16, pcrec reseed hint 8.
   - S has two checks: pcrec's build-time derivation assert, and each artifact's own
     `_Static_assert` on the compiler's layout. The second has an empty population at I1;
     it is declared UNREACHED with trigger I2.
   - `RX_ITER_INIT` costs one store (measured).
2. **Entries.**
   - `<prefix>_next` makes one exported call per match (today 2). The body is one
     parameterized function, inlined.
   - Exception: the DFA attempt route's static-label body (233 corpus artifacts) cannot be
     copied and stays shared.
   - `next_n` is twinned, answer-identical, and HELD for a measured trigger (Q2).
3. **Semantics.** The iterator follows PCRE2's global iteration, with the retry gated by a
   new fact `reports_empty`. The note also covers `\G`, utf8, validate-once under
   `-futf-check`, startpos at bind only, sticky `rc`, per-call budgets (D158), variables in
   the iterator, callouts, and every route including the compound.
4. **Kit seam.**
   - Regions of `st`, zero-fresh, with pcrec zeroing only the row.
   - M is the body's mode PARAMETER, which needs R-20 (`MF_BODY_PARAM`). The alternative,
     two bodies, is priced.
   - N is unchanged; H lives in the kit's region.
5. **Overhead and the parity gate.**
   - 1 exported call per match and 1 init store. Per call: a header compare, one fused
     binding compare and an `rc` test.
   - The gate has 6 cells, arms `L_old`/`L_new`/`I`/`I_shared`/`N64`/`I0` and an A/A
     floor, in two link regimes (static and PLT).
   - The gate is OWED to main on a quiet box. The twin is ready as its pre-build
     instrument.
6. **The abi event.**
   - Its readers were found by grep at `ee01f4dbb`, the byte-count reader class included.
   - Spec hunks: `match_api.md` §1, §2, §3, NEW §3.8, §3.1.3, §3.1.2¶6, §4, §5.3, §9.2,
     §10, §6.3; `rxt_format.md`'s new `mg` line; `vars.md`; `facts_listing.md`.
   - A drivers table, the bench relay draft, and checks each with its independent control.
   - S923-S942: every row has a detector and a reach; S934 is an equivalent mutant with a
     structural detector; S936/S937 are UNREACHED until I2.
   - Stages: I0 (zero-mover), I1 (one abi event), I2 (kit), I3 (K5), I4 (`next_n`).
7. **The rest.** Standing questions, the sibling family (streaming is a sibling type), 13
   unlocks with triggers, and four questions for Frank.

## Measured (all reproducible; commands in `findall_iter/CLAUDE.md`)

- **Semantics, libpcre2 10.46, byte, options 0.** 29,502 corpus (pattern, subject) pairs
  over 3,778 patterns; the loop and the global iteration differ on 1,063 pairs
  (160 patterns).
  - The loop's spans are NOT a subset of the global answer on 374 of those pairs. The
    witness is `a??b?` over `"ab"`: the loop reports `(1,2)`, which no oracle reports.
    This refutes `match_api.md` §3.1.3¶9.
  - Python's `finditer` agrees with libpcre2's global loop on every targeted cell.
- **Gate census.**
  - `reports_empty` is true on 686 of 3,778 patterns (605 nullable, 81 more by `\K`).
    Divergence: 160. Gate false and diverging: 0.
  - Bare nullability fails the soundness control on `ab\K` and `ab\Kc?`.
- **Twin, gcc 15.2 -O2.**
  - 60 case lines over 17 artifacts, ALL OK in both the inline and the shared form.
  - The 25 retry cells (VM guard, `\K` included) equal libpcre2's global loop. The 35
    non-retry cells equal today's loop and libpcre2's L.
  - `_search`'s instructions are identical after the refactor on 5 of 8 non-retry
    artifacts. The other three differ by scheduling or size (563 vs 579 B on `[0-9]+x`).
  - `.text`: +997..+2,587 B (inline, `_next` + `_next_n`) or +832..+989 B (shared). On
    the twins, `_next` is 433-1,079 B inline and 321-666 B shared.
- **Static-label bodies:** 233 of 4,243 compiled byte artifacts and 232 of 4,254 utf8 —
  exactly the DFA `attempt` scan.
- **Init codegen:** one 32-bit store for `RX_ITER_INIT` and for re-init, two for `_AT`.
  The aggregate initializer is a `rep stosq` of the whole struct, and its unnamed form
  trips `-Wmissing-field-initializers` under `-Wextra -Werror`.

## Findings for the manager

F1-F8 are in the note's §11. In brief:
- F1-F3: §3.1.3¶9 and ¶11 are wrong about how the loop diverges (subset; greedy; `\K`).
  The spec fix rides I1's hunk.
- F4: the retry gate must include `\K`.
- F5: an inline-into-two-entries design must handle the static-label body explicitly.
- F6: `{ X }` initializers break `-Wextra -Werror` callers.
- F7: `compound.md` §C's session pointer is superseded by D165.
- F8: `next` makes the var-bearing signature uniform.

## Owed (not this lane's)

- The parity gate run (§5.3), via main on a quiet box.
- R-20 to the kit (`MF_BODY_PARAM`), at R17-b″.
- The bench relay (§6.6), after I1.
- Frank's Q1-Q4. The S-sizing policy (declared rows, 56 B) is an answer-free choice and
  the manager's call.

## Resume notes (for a fresh agent)

- Every probe rebuilds from the tree. Run `make -j16`, then
  `docs/design/findall_iter/twin/run_twin.sh . build/iterdes/twin` (prints `run_twin: ALL OK`).
  The semantics commands are in `findall_iter/CLAUDE.md`.
- The case table lives in `run_twin.sh` and is TAB-separated, with `-` for empty flags.
