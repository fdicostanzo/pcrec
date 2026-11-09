# u3fix — [XARCH-DEV] U3 moved onto the kit's finished U2 (7fb1fa153), joint landing prepared

STATE: delivered on lane/u3tgt (tip at handoff: see `git -C worktrees/u3tgt log -1`). The owed runs are
QUEUED and have not run. Rulings applied: R1, R2, R3 (the last entry in u3tgt_rulings.md).

## Summary

- **The kit's finished U2 is merged** (7fb1fa153, merged ALONE as ccaef16a2). The one conflict was the
  lanes history index, and both lines were kept. `make strict` is green on it.
- **`MF_TARGET_REQUIRED` is now 1** (memfn/src/kit.h, fe34fe1c3; sheet item 11). This is the only memfn/
  edit in this lane.
  - Both suites are green with the switch at 1: `test-memfn-finder` 3316 passed / 0 failed, and
    `test-memfn-arms` 374 / 0.
  - No fixture needed moving. U3 had already made every pcrec art state a target (see Fixtures moved).
  - Control: compose.c built at `-DMF_TARGET_REQUIRED=0` has no refusal text, and at 1 it has it. The
    lane's build/pcrec carries it, so the switch is live in what the suites ran.
- **`#define MF_P_PORTABLE_ONLY` is LEFT in memfn/include/memfn.h.** The kit's own switch now reads it:
  compose.c `define_sel` refuses a site carrying the bit with `s->policy & MF_P_PORTABLE_ONLY`.
  Deleting the define breaks the kit's build. Removing it means first editing compose.c (spell the bit as
  `1u << 0`, or retire refusal (b)). That is a third memfn/ edit, so it is the kit's call or the
  manager's, not this lane's.
- **R3: main 550e23364 is merged ALONE** (2567ce447). run_targets.sh merged cleanly and keeps both sides:
  U3's cells, plus the avx512f run guard with the RAN floor's minus one.
- **The movers re-checked on the merged tip** (`(?i)cat`):
  - default: `none:generic`, `none`;
  - `-fmemfn-simd=x86-64`: `vrun@w16`;
  - `-fmemfn-simd=x86-64-v3`: `vrun@w32+w16`, and it compiles at plain `-march=x86-64` with 15 ymm uses;
  - `-fmemfn-simd=generic`: `none`.
- **No emitted byte moved since 59846b211.** abi stays 98: the merges add no reader of the number.
  FILEPIN is self-pinned to 2567ce447.
- **FINDING: `test-memfn-simdfloor` is red** on this tip, and was red at 59846b211 too. See Checks.

## Merge

| step | commit | result |
|---|---|---|
| merge lane/memfn-u2 7fb1fa153 (alone) | ccaef16a2 | conflict in docs/dev/history/claude_md/docs__dev__lanes.md only (two appended index lines, both kept); 26 files from the kit |
| `make strict` | — | GREEN |
| switch flip | fe34fe1c3 | `#define MF_TARGET_REQUIRED 1` |
| merge main 550e23364 (alone, R3) | 2567ce447 | the same index-file conflict, all lines kept; tests/memfn/run_targets.sh auto-merged with both sides |
| FILEPIN | df28a9527 | `c6d73f302` -> `2567ce447`, with a SELF-PIN comment line; the manager re-pins to the landing merge |

- **Sheet item 1 rev 1.1** says the kit refuses a FIRST statement after a define and accepts a restatement.
  U3's placement fits it:
  - `pcrec_memfn_art` calls `mf_art_target` right after `mf_art_begin`, before any define
    (src/gen/memfn_sites.c);
  - the tests/memfn helpers do the same (arm_fixtures.c `art_begin`, proven_check.c, proof_check.c).
- **The guard/region placement** is unaffected by rev 1.1, which constrains only the call order.
  run_targets.sh is green on the merged tip.
- **abi readers.** `git diff 59846b211 HEAD` adds no line naming an abi number, and
  `PCREC_ARTIFACT_ABI` stays 98. No commit since 59846b211 touches src/, cli/ or lib/.

## Fixtures moved

None needed a move. With the switch at 1, the kit refuses an art that states no target, and a site that
carries bit 0. Every pcrec art was checked against both:

| art | target stated | bit 0 |
|---|---|---|
| src/gen/memfn_sites.c `pcrec_memfn_art` | `mf_art_target(job->mf, pcrec_memfn_target(cx))`, refusal on -1 | sites carry `MF_P_INLOOP` or 0 |
| tests/memfn/arm_fixtures.c `art_begin` | `mf_portable_target()` | none |
| tests/memfn/proven_check.c | `mf_portable_target()` | none |
| tests/memfn/proof_check.c | the loop's target (portable / x86-64-v3) | none |
| tests/memfn/run_proof.sh | states the target (U3) | none |

The other `mf_art_begin` mentions in pcrec are comments: ks_measures.c, cli/main.c,
run_part_measures.sh, and the sabotage rows S1031/S571/S2912/S2903, which plant kit or pcrec code. The
kit measured 2310 and 343 failures with the fixtures unmoved. That was against U2's view of the
fixtures; U3 had already moved them. Measured here at 1: finder 0 failed, arms 0 failed.

## Checks

| check | result |
|---|---|
| `make strict` after the U2 merge, and again on 2567ce447 | GREEN ("whole tree compiles clean with -Werror -Wshadow; the kit's target table check passes") |
| `make test-memfn-finder`, switch at 1 | 3316 passed / 0 failed (scratch/u3fix/finder.log) |
| `make test-memfn-arms`, switch at 1 | 374 passed / 0 failed (scratch/u3fix/arms.log) |
| switch control (compose.c at 0 vs 1) | refusal text absent at 0, present at 1 |
| tests/memfn/run_targets.sh on 2567ce447 | 33 passed / 0 failed, 24 cells ran, 0 skipped |
| pre/post comparison: 59846b211 (git archive, built in scratch) vs the merged tip, emitted text | 1,500 sampled corpus patterns × 6 cells (default, x86-64, x86-64-v3, generic, `-e utf8`, `--engine=vm`): 0 movers. (scratch/u3fix/cmp.py, cmp.log) `(?i)cat` and `((?i:abc))` are byte-identical at x86-64 and x86-64-v3 |
| movers by flag, `(?i)cat` | default none; x86-64 vrun@w16; v3 vrun@w32+w16; generic none; bare `-fmemfn-simd` vrun@w16 (this host) |
| tests/memfn/simd_floor_check.py, `--every 40` | **RED**: 6 passed / 3451 failed (scratch/u3fix/sf/run.log) |

- **FINDING, the simd floor check (C18, `test-memfn-simdfloor`) was never re-aimed for U3 + U2.**
  - The kit's u2_report Deviations item 8 names it U3's to re-aim, and u3tgt did not edit
    tests/memfn/simd_floor_check.py. Its lint expects every inserted line to be one of:
    - a levels.def `#if` guard;
    - a level header;
    - a stamp move.
  - On this tip it fails per mover on:
    - the TARGETS line (`(c)` deleted/inserted, and "guard lint: '#define RX_TARGETS' inserted");
    - the family guard `#if !(defined(__x86_64__) && !defined(__ILP32__))`;
    - the region's `#if defined(__clang__)` and `#pragma` lines;
    - "(c) inserted 1953 bytes, SIMD_GUARDED_BYTES 0x77f" (the TARGETS lines are not guarded bytes);
    - "a mover with no SIMD FUNC selector" (the kit's one-call selector);
    - and finally "population: 245 movers / 0 SIMD FUNCs (K35)".
  - The same text is in 59846b211, so the queued sections job reads this red at either tip. It is not
    caused by the switch.
  - The re-aim is a check-design job, and this lane did not build it: what legs (a)/(b) mean once the
    level blocks carry no `#if`; the guard and region as named kit text; TARGETS as a stamp move. It
    needs a follow-up lane (learnings §3).
- **S726 (declared UNDETECTED by the kit).** No pcrec-side row aims at the same need check: the level's
  `needs` versus the target's features.
  - Every row anchored in memfn/src/levels.def or targets.def is the kit's: S725, S726, S2975, S2976,
    S2978, S2980, S2981, S2994.
  - pcrec's U3 rows are placement and statement only: S1870 target unstated, S1871 guard dropped, S1872
    region close dropped. None of them would see a weaker need.
  - What would close S726 is the kit's own condition: a target row that supplies the weaker feature
    alone.

## STATE AT HANDOFF

- **Rulings:** last entry applied is **R3** (main 550e23364 merged ALONE, both sides of run_targets.sh
  kept).
- **Branch:** lane/u3tgt. This lane's commits are ccaef16a2 (U2 merge), fe34fe1c3 (switch), 2567ce447
  (main merge), df28a9527 (FILEPIN) and the report commit.
- **Owed: the six queued box jobs** (`480-main-u3fix-*`, owner main, prio 480; they run after the
  19:00-01:00 hold). Each dry-ran at enqueue; none has run. Job files are in
  /var/tmp/pcrec-pcrec/scratch/u3fix/jobs/, logs in /var/tmp/pcrec-pcrec/scratch/u3fix/runs/.
  - `main-u3fix-sections`: test-cli, memfn stamps/arms/arch/targets/rows/guarded/simdfloor/forms/reach,
    kitproof, codegen, registry, rxtsource. **Predicted red: test-memfn-simdfloor** (the finding above).
  - `main-u3fix-movers`: u3tgt_movers.py at x86-64 and x86-64-v3, against the abi-97 ref.
  - `main-u3fix-sweepsimd`: emit_sweep's `-fmemfn-simd=x86-64` arm, byte + utf8.
  - `main-u3fix-mech`: S693 S981 S1224 S2930 S1870 S1871 S1872 (expect rows=7).
  - `main-u3fix-axesmemfn`: run_axes.sh `AXES=--memfn`.
  - `main-u3fix-maketest`: make, strict, make test via perfrun.
- **main-u3tgt-sections was left running** (it held the box lock from 18:08). It runs in this same
  worktree, and the merges landed under it. Its verdict reads a mixed tree; trust the u3fix-sections
  run instead.
- **For the landing:**
  - the `MF_P_PORTABLE_ONLY` define stays until compose.c's refusal stops naming it (see Summary);
  - re-pin FILEPIN to the landing merge;
  - the simdfloor re-aim lands first, or the landing waives it with a reason.
