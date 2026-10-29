# Lane simdset — a standalone SIMD kernel: find any of 2-3 arbitrary bytes

Lane `simdset` for the memfn kit manager, branch `lane/memfn-simdset`, cut
from local main 02a054851 (D172 S3, abi 92). Authority: Frank's go to the kit,
2026-10-29 (memfn/docs/responses.md, the notice "Frank's go to the kit
(direct): expand the SIMD layer", step 2). It generalizes plan row
[MEMFN-PAIRSIMD]: that row's arbitrary-pair kernel (two compares and an OR) is
the K = 2 case.

## Summary

- **The kernel** is `memfn/src/vany.c`. Its one entry is
  `mf_kernel_find_any(sink, fn, bytes, k, levels, err, errn)` in a new
  STANDALONE KERNELS section of `memfn/include/memfn.h`. It writes a
  self-contained family of
  `static inline size_t f(const unsigned char *subject, size_t n, size_t pos)`
  functions that return the least i in [pos, n) with subject[i] one of the K
  bytes, else n. The family is laid out in the seam's shape (ofsskip.c, D155):
  - `<fn>__body`, the portable byte loop;
  - one guarded helper per requested level (`<fn>__w16`, SSE2; `<fn>__w32`,
    AVX2), each falling through to the next lower rendered helper on a span
    shorter than one vector;
  - the selector `<fn>`, whose whole body is the `#if` chain.

  K is 2..3. Duplicate bytes are compared once. A refusal (bad sink, name, K or
  level) is loud: -1 with its text in `err`.
- **NOT ROUTED.** There is no `mf_site` row, no `fn_rows[]`/`fd_rows[]` entry
  and no `options.def` row, so there is no deny and no abi event. `vany.o` sits
  in libpcrec.a, but no pcrec object references it, so the linker never pulls
  it into `build/pcrec`. The zero-mover sweep (below) is OWED as a queued job.
- **G2** is the new FIND-ANY family, `memfn/tests/run_g2_any.py`, hooked into
  `run_g2.sh` as section 4y and therefore part of `make test-memfn-g2`. It
  checks every answer against its own scalar byte loop over a generated space:
  - 40 byte sets × 4 level choices = 160 kernels;
  - 20,292,480 answer checks per build, at 4 builds;
  - guard pages at both ends;
  - 13 plants (each red where its level is live, green where compiled out, and
    3 must fault).

  Wall time about 23 s alone.
- **The method card** is `memfn/data/cards/kit-kernels.tsv`, `kit-kernels@1`.
  It is UNMEASURED (no set holds a `kit.*.vany*` row). `finder_check.py` now
  reads every card table in the directory, so the new table is held.
- **NEON is OWED.** This box has no aarch64 cross-compiler, so no untested
  NEON was written.

## The form, and the over-read argument

Per level of register width VW:
1. broadcast each distinct member once;
2. per block, one unaligned load, one compare-equal per member, ORed, one
   movemask; the lowest set lane is the answer.

Blocks ascend from pos. Past the last whole block, ONE overlapped final block
at n − VW. The final block needs NO lane mask, which is DERIVED: its lanes
below the first unscanned position lie inside the last whole block, and that
block held no member. vrun needs its mask; this form does not.

**Reads only [pos, n), on every path** (stated in vany.c's header):
- The body reads s[i] only for pos ≤ i < n.
- The entry test sends `pos >= n` and `n - pos < VW` to the fall-through. Past
  that test at least one whole block runs.
- A whole block runs while `n - i >= VW`, and i ≤ n throughout, so the
  subtraction never wraps. It reads [i, i + VW) ⊂ [pos, n).
- The final block reads [n − VW, n), and n − VW ≥ pos by the entry test.
- No partial vector load is ever made. There is no scalar tail at a level:
  spans shorter than VW go to the next level down.

**What holds this argument:**
- G2's guard pages, at s + n (layout U) and immediately below s + pos
  (layout L);
- the three bound plants (`final-late`, `loop-past`, `entry-short`), which
  move a bound by one byte and must FAULT. They do, at every build where
  their level is live.

## D149 — every constant

| constant | status |
|---|---|
| VW | DERIVED (levels.def's register width) |
| the entry cut-over `n - pos < VW` | DERIVED as a correctness bound (the smallest span one block reads); whether the next level down is faster somewhat above VW is UNMEASURED DEFAULT, and no other cut-over is written |
| loop unroll 1x, unaligned loads from pos, no alignment prologue | UNMEASURED DEFAULT, labelled in place; 2x/4x unrolls (Rust memchr reads 4 vectors per iteration on long spans) and an aligned main loop are variants for the card's first run, not built |
| K ≤ 3 (`VANY_MAX_K`) | CHOSEN shape bound (the charter's 2..3; past 3 is the set-find's territory) |
| duplicate members compared once | DERIVED (OR is idempotent) |

## Licence and provenance

- vany.c is original kit text, 0BSD. The block loop and overlapped final block
  follow vrun.c's (pcrec's own text).
- The compare-each-byte-and-OR idea is the textbook one (Rust memchr's
  memchr2/memchr3 among others). Only the idea was used; no Rust text was
  translated, so the Unlicense arm was not needed.
- The SPDX line and provenance header are present. There is a
  `memfn/PROVENANCE.md` row, and C16 passes (`make test-memfn-link`).

## G2: the find-any family

The family is written by the kernel's author (not D27-blinded). Its
independent controls are:
- the driver's own byte loop (`ref_find`, over the table's bytes as given,
  duplicates kept);
- the generated space;
- the guard pages.

It never compares against another output of the kit's generator.

**The space** (`g2/g2_any_gen.c`, seed 20261029, 40 sets):
- **Fixed head, 16 sets:** {0x00, 0xFF} both orders; {0x00, 0x80, 0xFF};
  0x7F/0x80; 0x80/0x81; {0xFE, 0xFF, 0x01}; the duplicates {a,a}, {x,x,x},
  {a,b,a}, {0,0,1}; a case pair; CR/LF; quote/backslash; 0x10/0x11; a UTF-8
  pair; whitespace.
- **24 random sets** draw high-bit bytes, one-bit neighbours and duplicates.
- **Four level choices per set:** none, w16 alone, w32 alone, both.
- **Measured populations:** dup 11, ff 4, high 25, k2 21, k3 19, kernels 160,
  each level choice 40, zero 4. Floors are about 80% of these, as literals.
- **Refusals:** K 1, K 4, two bad names, a level bit past mf_levels(), and a
  sink without vprintf. Each must be refused with text.

**The subjects** (`g2/g2_any_driver.c`):
- every length 0..73 (2 × 32 + 9);
- starts {0, 1, 2, 3, 15, 16, 17, 31, 32, 33, n − 1, n};
- a member at EVERY position in [pos, n), each member in turn, and the no-hit
  subject;
- a later member (it must never win), and members below pos (layouts U and A);
- non-member filler, half of it one bit away from a member.

**The layouts:**
- U: guard page at s + n;
- L: guard page below s + pos;
- A: every alignment 0..31 from a 64-byte-aligned base, for the hit at pos, at
  n − 1, at a random position, and none.

A 10 s alarm stops a kernel that never returns.

**Builds:**

| build | levels live |
|---|---|
| x86-64 | w16 |
| x86-64-v3 | w32, plus w16 via its own arm and the ladder's fall-through |
| -mgeneral-regs-only | neither; the body |
| ASan+UBSan at x86-64-v3 | as x86-64-v3 |

Every build compiles with -Wall -Wextra -Werror.

**Plants:**
- **The 13 plants:** six per level plus one in the body:
  - `final-late`, `loop-past`, `entry-short` (must FAULT);
  - `no-final`, `high-lane` (lanes highest first), `member-dropped` (must go
    red);
  - `body-last` (the byte loop misses the last byte).
- **How they are applied:** each edit is applied inside every helper of its
  kind and must match its count in each, or the run is red.
- **Matrix, measured (39 runs):** every level plant is FAULT or RED where its
  level is live and GREEN where it is compiled out (w32 at x86-64 and at
  gpr-only; w16 at gpr-only). `body-last` is RED at all three builds.

**Instruction classes:** objdump of the v3 driver shows no pdep, pext or
gather.

**Host gate:**
- A level the host cannot run is built, not run, and printed
  `SKIPPED ARM <build>: <why>; N checks NOT run`.
- `G2A_SKIP_ARMS=x86-64-v3` forces the skip. Exercised: two arms skipped with
  their 20,292,480 checks each named.
- A non-x86-64 host runs the portable build alone, with every level SKIPPED.

## The method card

`memfn/data/cards/kit-kernels.tsv`, `kit-kernels@1`:

| | |
|---|---|
| quantities | kit-grid@1's beta, f, saving, xover and gstar, with the same dims, so a set measured under the card uses the keys the readers already spell |
| forms | `vany2-w16`, `vany2-w32`, `vany3-w16`, `vany3-w32`, `vany2-body`, `vany3-body` |
| comparators (`vs`) | those forms, WALK and LIBC |
| status | UNMEASURED, said in its header: no committed set holds a row, and every reader skips an absent key (measures.md §0¶2) |
| `gate_e6` | kit-grid@1's 30000, an UNMEASURED DEFAULT |

**Which file reads the cards.** No canned measurement script exists today:
item (a) of [MEASURE-SET]'s FORMAL LIBRARY is filed and unscheduled
(plan.md). The only readers are:
- `memfn/data/sets/generate.py`, which writes a set's cards section from the
  table its method names;
- `tests/memfn/finder_check.py` check C.

Check C used a hand list ("kit-grid", "kit-synthetic"), so a new table would
have been read by nothing. It now lists the directory, with a floor of 3
tables, and holds each card row's shape (13 columns, owner `kit`, a §3.1
unit).

**Sabotage, run:** a malformed row appended to kit-kernels.tsv turned
`make test-memfn-finder` red, with the exact FAIL line. The file was then
restored. Clean: 1968 passed, 0 failed.

## Validation

| check | result |
|---|---|
| `make -j16` | clean |
| `make strict` | clean (whole tree, -Werror -Wshadow) |
| `make test-memfn-link` | 11 passed, 0 failed (C15, C16 with vany.c's row, R-28: 342 kit functions, largest frame still 3,600 B) |
| `make test-memfn-finder` | 1968 passed, 0 failed (with the card-table listing); sabotage red as above |
| `python3 memfn/tests/run_g2_any.py` alone | 56 passed, 0 failed, 23 s wall (4 builds × 20,292,480 checks; 39 plant runs) |
| `make test-memfn-g2` | green, rc 0: 70,358,654 checks passed, 0 failed, 9 m 31 s wall (all families; section 4y `find-any family (checks passed: 56)`), run while the queue's 690-trailgc-test held the box (not a timing window) |
| zero-mover sweep vs 02a054851, default and `-fmemfn-simd` arms | OWED: queue job `696-simdset-sweep` (see STATE AT HANDOFF) |

No `make test`, no mech run and no timing were run (brief).

## Open questions (for the kit manager; not decided by building)

1. **How pricing is offered the kernel.**
   - **The question:** D176's priced stop choice picks a (position × method).
     This kernel is a method with no site.
   - **Options:**
     - (a) a Table B renderer row (B-any) beside B-pair/B-memchr/B-walk,
       rendering this text for a stop whose set has 2-3 members, priced off
       `kit.beta.vany*`;
     - (b) a BODY row of `fn_rows[]` under the offset-skip function, with the
       kernel's helpers as PREFIX rows (vrun's pattern);
     - (c) both.
   - **Leaning:** (a). It is the one FIND table (addenda/kit.md "One table
     per slot"), and the window family's E-find already asks it.
   - **Whichever is chosen:** routing it moves bytes. That needs its deny
     row, the abi event, G1 at both layers, and [MEMFN-PAIRSTOP]'s census
     trigger.
2. **Form identity for the card's deps.** `mf_form_hash` hashes a site's
   rendering, and the kernel has none, so `kit:form.vany*` cannot resolve.
   Either hash the kernel's own text (a `mf_form_hash_text` call on the
   rendered family), or resolve the deps when it is routed. Today the deps are
   OWED, as the card's header says.
3. **The measurement script.** Should a small kernel timing driver (scalar
   body vs WALK vs LIBC vs the w16/w32 helpers, kit-grid@1's subjects) be
   written now under `docs/design/memfn/probes/`, so the card has a runnable
   method? Or does this wait for [MEASURE-SET] (a)? This lane built neither
   (D77; no timing was chartered).
4. **One ops table or two.** vrun.c and vany.c each hold a per-level
   intrinsic-spelling table: vrun's has `and`, this one has `or`. Two members
   is below the unification bar ("propose at ~3"). A third SIMD form should
   move the spellings into levels.def or a shared `ops.def`.
5. **NEON.** OWED: no aarch64 compiler on the dev box. The Mac (arm64) could
   build and run a NEON level. Its levels.def row is "born with its first
   row" and needs addendum 8's acceptance (§R4.9.2.2).

## STATE AT HANDOFF

- Branch `lane/memfn-simdset`, tip in the handback message. No rulings file
  appeared (`simdset_rulings.md` was absent at every poll), so no ruling was
  applied.
- OWED: `696-simdset-sweep` (queued 2026-10-29). It runs `make -j16`, then
  `scripts/emit_sweep.py --ref 02a054851 --bin build/pcrec` twice: plain, and
  with `--extra=-fmemfn-simd`. The job declares `expect sweeps=2
  lines=^emit_sweep: DONE rc=0`.
  - Logs: the queue's job.log under `worktrees/.boxqueue/done/*-696-simdset-sweep/`
    and the sweeps' own `worktrees/simdset/build/simdset/sweep/{plain,simd}/`.
  - Read the verdict with `scripts/verdict` on the job.log. Zero movers are
    expected on every stream, because no pcrec object references vany.o.
- No DELIVER block (`docs/dev/lanes/simdset_deliver.txt`) existed at the
  start, so `scripts/lanecheck` has no block to check against. Its output is
  in the handback.

## Charter vs committed

| charter item | committed |
|---|---|
| standalone kernel "first position in [s, e) whose byte is any of K arbitrary bytes, K = 2..3", compares ORed | `memfn/src/vany.c`, `mf_kernel_find_any` (memfn.h) |
| NOT ROUTED: no mf_site row, no pcrec site, no options.def row, no deny, no byte moves, no abi event | none added; vany.o is unreferenced by pcrec |
| prove "no byte moved" with emit_sweep vs 02a054851, default and -fmemfn-simd, via the box lock, once | OWED: queue job 696-simdset-sweep (yields to the queue) |
| the kit's style: MF_NS, static internals, SPDX/provenance header, PROVENANCE.md row | yes; C15/C16 green |
| levels: 16-byte SSE2 and 32-byte AVX2 as levels.def does | yes, from levels.def's guard/header/vw/stamp |
| NEON only if compilable, else OWED with reason | OWED (no aarch64 compiler on the dev box) |
| D149 labels for every unroll/block/cut-over | yes, in vany.c's header and the table above |
| explicit over-read argument and tail handling | vany.c's header; this report; held by guard pages and fault plants |
| G2 vs the scalar byte loop over a generated space (0x00/0xFF/duplicates/high-bit, lengths 0..>2 VW, every alignment, hit at every position, no hit) | `run_g2_any.py` + `g2_any_gen.c` + `g2_any_driver.c` |
| hooked into make test-memfn-g2 if it fits the time budget | run_g2.sh section 4y (~23 s) |
| guard-page or ASan over-read check at the buffer end | both: guard pages U and L, plus an ASan+UBSan build |
| METHOD CARD added in the same change, visibly UNMEASURED; find which reads cards | `kit-kernels@1`; finder_check now reads every card table (sabotage-validated) |
| no timing | none run |
| CLAUDE.md for every directory touched | memfn/, memfn/src/, memfn/include/, memfn/tests/, memfn/data/cards/, tests/memfn/ |
| report ending in this checklist | this file |
| light checks only: make strict, test-memfn-g2, test-memfn-link, zero-mover sweep | strict, link, g2 and finder run; sweep OWED |
| design questions written, not built | Open questions 1-5 |
