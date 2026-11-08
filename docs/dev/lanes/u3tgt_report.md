# u3tgt — [XARCH-DEV] target seam unit U3 (pcrec half)

STATE: delivered on lane/u3tgt (tip at handoff: see `git -C worktrees/u3tgt log -1`). It lands
WITH the kit's U2 as ONE merge and ONE abi event (97 -> 98). Built against the U3 interface sheet
(`git show 6418080b2:docs/dev/lanes/u2_report.md`, items 1-10). Rulings applied: R1, the only
entry in u3tgt_rulings.md.

## Summary

- **The art's CPU target crosses the seam.** pcrec states it on every art with
  `mf_art_target(art, pcrec_memfn_target(cx))`, right after `mf_art_begin`. The target is the one
  member of the compile's target set; at the default it is the kit's portable `generic`. A -1 is
  a compile refusal: an internal error naming the kit's `mf_art_error`.
- **`pcrec_memfn_policy` is gone, along with every pcrec reader of `MF_P_PORTABLE_ONLY`.** Sites
  carry `MF_P_INLOOP` alone.
- **pcrec places the kit's text in the artifact.**
  - the family guard, at file scope ahead of every `#include`;
  - the target region: open before the first function (before the kit's helpers and their
    intrinsic `#include` lines), close after `rx_info` and before any `main`.
  - Both count as guarded bytes. A compound part writes neither, nor TARGETS.
- **`<PREFIX>_TARGETS "FAMILY:TARGET"` is on every artifact** (`none:generic` at the default).
- **The kit fix landed, and v3 is pinned per the sheet.** R1's v3 defect was fixed on lane/memfn-u2
  (9d59d96a3, "x86-64-v3 supplies sse2"). I merged the kit's tip ALONE (c6d73f302; conflicts in
  S722 and proof_check.c, resolved as described under Retired readers), then pinned v3 as the
  sheet says. Measured on the merged build with `(?i)cat`:
  - `-fmemfn-simd=x86-64` gives `vrun@w16`;
  - `-fmemfn-simd=x86-64-v3` gives `vrun@w32+w16`;
  - bare `-fmemfn-simd` gives `vrun@w16` on this host.
- **Run here (green):**
  - `make strict`, after the merge;
  - `tests/memfn/run_targets.sh`: 33 passed, 0 failed, 24 cells ran;
  - the movers proof on 1,200 patterns: 0 unpredicted;
  - `VALIDATE_ONLY` mech fields for 13 rows.
- **Not yet run:** the whole-tree runs (make test, the targeted sections, the full movers proof,
  the SIMD sweep, mech, the axes memfn arm). They are QUEUED (STATE AT HANDOFF) and have not run.

## What crosses the seam

| item (sheet) | pcrec side | where |
|---|---|---|
| 1 `mf_art_target` | called on every art; -1 is a compile refusal | src/gen/memfn_sites.c `pcrec_memfn_art` |
| 2 admission | not read (the kit's) | — |
| 3 guard | `mf_family_c_of(t->family)->guard` (none for `generic`) | memfn_targets.c `pcrec_emit_target_guard` |
| 4 region | `mf_target_c_of(t)->region_open/_close` | `pcrec_emit_target_open/_close` |
| 6 TARGETS | `t->family ? t->family->name : "none"` `:` `t->name` | `pcrec_memfn_targets_stamp`, emit_dfa.c prologue |
| 8 bit 0 | `pcrec_memfn_policy` deleted; sites carry `MF_P_INLOOP` alone | memfn_sites.c, internal.h |
| 9 tests/memfn callers | arm_fixtures/proven_check/proof_check state the portable target; C-PROOF loops over every `mf_targets()` row | tests/memfn |

C4 (arch-blind): no target token is spelled in src/, cli/, lib/, tests/cli, tests/axes or
tests/mech. tests/cli and tests/axes read their targets from `--list-cpu-targets`: from the one
family that has two or more targets, they take the target with the fewest features and the one
with the most. `make test-memfn-arch` is in the queued sections job.

## Emitted text

- **Default (`-fno-memfn-simd`):** only the abi digits move (5 sites) and
  `#define RX_TARGETS "none:generic"` is added. Checked by u3tgt_movers.py: ref 9161402da renumbered
  plus that line must EQUAL the lane, at byte/utf8 × default/VM. The 1,200-pattern trial found 0
  other movers.
- **`-fmemfn-simd=TARGET` adds:**
  - the TARGETS line;
  - the guard (3 lines);
  - the region (two 6-line `#if defined(__clang__)` blocks; their pragmas are the kit's text);
  - the moved FORMS and GUARDED stamps.
- **`-fmemfn-simd=TARGET` removes:**
  - every CPU `#if`/`#elif`/`#else`/`#endif`;
  - the blocks of the levels the target does not admit (the w32 helper at x86-64);
  - the selector's other arms.
- **FORMS** is the ref's minus the unadmitted levels (`vrun@w32+w16` -> `vrun@w16` at x86-64). The
  1,200-pattern trial found 0 unpredicted lines. Its kit-SIMD-served patterns were 6 (byte),
  5 (VM) and 1 each at utf8 (among them `((?i:abc))`).
- **The proof's control:** every compiled cell is judged a second time with one planted line,
  which must be rejected.
- **Guarded bytes at `(?i)cat`:** 0x77f (x86-64) and 0xe9a (x86-64-v3). The default reads 0.
- **Answers do not move.** run_targets.sh part 4 compiles real `(?i)cat` artifacts at three targets
  (generic, x86-64, x86-64-v3) × five cells (gcc, `-march=native`, `-march=x86-64-v2`, `-mno-sse2`,
  clang), and every cell equals a naive caseless finder (11,476 checks each).
  - The v3 object carries 15 ymm uses at the default `-march`.
  - With its region pragmas stripped, the v3 artifact refuses to compile (so the region, not the
    consumer's flags, supplies the ISA).
  - The guard refuses `gcc -m32` and `clang --target=aarch64` with its own message.
  - v3 cells are built but not run on a CPU without AVX2.

## Retired readers

- **Bit-0 readers, now gone:**
  - `pcrec_memfn_policy` (memfn_targets.c, internal.h, memfn_sites.h);
  - the site policy in memfn_sites.c;
  - lib/pcrec.h's "one bit … INERT today" comments (2);
  - tests/memfn arm_fixtures.c (12 begins, now one `art_begin` helper), proven_check.c and
    proof_check.c.
- **The `#define MF_P_PORTABLE_ONLY` in memfn/include/memfn.h is LEFT.** I may not edit memfn/.
  Sheet item 8 makes its removal a one-line memfn.h edit in the landing merge. Its only remaining
  mentions are comments: the re-aim notes in S1224 and S1870, and memfn/src/fields.def.
- **Sabotage rows:**

| row | disposition |
|---|---|
| S722 | re-aimed by BOTH lanes. The merge takes the KIT's form: the w16 row's `[FLD_target]` set to `MF_ANY`, suite g2simd. The kit owns vrun.c's plant. |
| S1224 | re-aimed: the plant clears `proven[0]` bit 0 when `kit_target_levels(art->target)` is nonzero (compose.c `mf_ask`). Planted RED, plain run 882/0 (run_proof.sh). |
| S2930 | anchor `MF_P_PORTABLE_ONLY` -> `"generic"` (the kit merged its own S2930 edit cleanly beside it) |
| S693 | BEFORE 98, AFTER 97 |
| S981 | re-aimed: the arm is now `-fmemfn-simd=x86-64`, so the plant drops the flag in either spelling (`str(a).split("=")[0]`) |
| S1864 | RETIRED (file deleted): it planted the derivation of bit 0 off the target set, in `pcrec_memfn_policy`, which U3 deleted. Reason recorded in S1870's header. |
| S1870 (new) | `mf_art_target` skipped -> no SIMD level at any target (cli) |
| S1871 (new) | guard text dropped (cli placement case) |
| S1872 (new) | region close dropped (cli placement case) |

## Pins and abi

- **abi 97 -> 98, one bump.** Readers found by grep:
  - emit_dfa.c `PCREC_ARTIFACT_ABI`;
  - tests/codegen ABI_EXPECT and its narrative;
  - match_api.md §1 (3) and §6 (table row and ¶17);
  - S693;
  - docs/dev/history/abi_changelog.md (new top entry).
- **Identity gate.**
  - (B) is FILEPIN, SELF-PINNED to `c6d73f302`. That is the merge of the kit's tip, the last
    commit that moves memfn/src; the lane's own src commits end at a6f88a689. There is a SELF-PIN
    comment line, and the manager re-pins it to the landing merge.
  - (A) ABASEPIN stays: no call-free program region moves.
- **Spec hunks:**
  - match_api.md:
    - §6.3.2 inventory row `<PREFIX>_TARGETS`;
    - §6.3 MEMFN_FORMS (levels are the target's, no `#if`);
    - §6.3.10¶8/¶9/¶10 (guarded bytes include guard + region, 0 at the portable target);
    - NEW §6.3.10¶14 (TARGETS) and ¶15 (the guard and region text);
    - §6.3.12 compound table (`_TARGETS` pattern-level);
    - NEW §10.7¶4 (a no-vector-register consumer uses the default target);
    - §8.2¶7d.
  - tuning.md §2.43 ¶3, ¶3a, ¶3e and ¶4.
  - cli.md §1.24¶3 (the list is the artifact's target now).
- **Explicit-target pins (the family explicit):**
  - tests/memfn/rows.tsv: `vrun-w16` at `-fmemfn-simd=x86-64`, `vrun-w32` at
    `-fmemfn-simd=x86-64-v3` (tests/memfn is C4-exempt);
  - tests/cli: the vrun cases at the derived fewest/most-features targets (mfs2b expects exactly
    `vrun@w16`), plus the U3 placement and TARGETS cases;
  - tests/axes: the SIMD layer is now `-fmemfn-simd=<most-features target>`, so every floor
    measured with both rungs keeps its meaning. memfn_arm.py's layer check accepts the `=TARGET`
    spelling.
  - scripts/emit_sweep.py:
    - DIFFER_PINS and COMPOSITION_EXTRA_PINS: the SIMD arm is now `-fmemfn-simd=x86-64`, with the
      floors carried (re-measured by the queued job);
    - the arms sweep sets each SIMD arm's fixed target text aside (measured on a control pattern),
      so the floor still counts only kit-served patterns.
  - simd_bounds.tsv: `target-text 700` (measured 615 B at v3).
- **NOT re-pinned:** row_floors.tsv and simd_accept.tsv are counts and bench acceptance per CPU
  class, and nothing moved them. The queued sections job (test-memfn-rows) is their check.
- **CLAUDE.md:** src/gen, tests/memfn and tests/cli rows were updated, with detail in the NOTES.md
  of src/gen and tests/memfn.

## Checks

| check | result |
|---|---|
| `make strict` (merged tree) | GREEN |
| tests/memfn/run_targets.sh (all 4 parts) | 33 passed / 0 failed, 24 cells ran |
| u3tgt_movers.py x86-64, 1,200 patterns × 8 cells | 0 unpredicted (control active) |
| tests/cli at the earlier tip (pre-merge, R1 time) | U3 cases green; the 6 w32 cases red from the kit defect; all 369 green with v3 given sse2 in a scratch copy. NOT re-run after the merge (the queued sections job) |
| run_proof.sh S1224 plant / plain | RED / 882 passed 0 failed |
| mech VALIDATE_ONLY (S689 S693 S722 S723 S981 S1026 S1224 S1852 S1870-S1872 S2930 S2981) | 13 definitions valid |
| memfn batch at the pre-merge tip | stamps/libc 133 agree; K1 411,620/0; G2 SIMD family RED (expected `vrun@w32+w16`, read `none`) on the kit's PRE-fix G2. Killed when the kit tip landed; G2 is the kit's gate. |

## STATE AT HANDOFF

- Last rulings entry applied: **R1** (v3 pinned per the sheet after the kit fix 9d59d96a3 was
  merged ALONE as c6d73f302).
- **Owed:** queued box jobs (`--prio 480 --owner main`), none of which has run yet:
  - `main-u3tgt-sections`: test-cli, memfn stamps/arms/arch/targets/rows/guarded/simdfloor/forms/
    reach, kitproof, codegen, registry, rxtsource;
  - `main-u3tgt-movers`: u3tgt_movers.py, full corpus, at x86-64 and x86-64-v3;
  - `main-u3tgt-sweepsimd`: emit_sweep's `-fmemfn-simd=x86-64` arm, byte + utf8, DIFFER floors
    carried from the bare arm;
  - `main-u3tgt-mech`: S693 S981 S1224 S2930 S1870 S1871 S1872;
  - `main-u3tgt-axesmemfn`: run_axes.sh `AXES=--memfn`;
  - `main-u3tgt-maketest`: make, strict, make test via perfrun.
  - Job files: /var/tmp/pcrec-pcrec/scratch/u3tgt/jobs/; logs: .../u3tgt/runs/. The ref binary for
    the movers proof is .../u3tgt/ref/build/pcrec (git archive 9161402da).
- **Predicted risks for the owed runs:**
  - sweepsimd: the carried DIFFER floors (22/19/15/15) were measured with the bare arm when it
    rendered both rungs. If a pattern served only at w32 existed, it would read lower now; a red is
    a re-pin from that job's measured counts.
  - sections: simd_floor_check.py, libc_census.py, reach_equal.py and run_wreply.sh pass bare
    `-fmemfn-simd` (now x86-64, w16 only). Expected green; any red names its file.
  - S722 is the kit's form now (suite g2simd), so it is in the kit's mech set, not this lane's.
- **For the landing:**
  - remove `#define MF_P_PORTABLE_ONLY` from memfn/include/memfn.h (one line, sheet item 8);
  - re-pin FILEPIN to the landing merge;
  - the kit's own U2 gates are the kit's.
