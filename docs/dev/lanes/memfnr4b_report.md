# Lane memfnr4b — R4b: the fused scan+verify on the post-handoff build (memfn R-1)

Lane of the memfn kit session; branch `lane/memfnr4b` off `lane/memfn-r4b`
(766d08eb, cut from main d4d9ed90). MEASUREMENT ONLY: nothing under
`memfn/src`, `src/`, `cli/`, `lib/`; no pcrec byte moves, no abi event.
Charter: `memfn/docs/requests.md` R-1. The Linux verdict is **OWED** to
main's executor (script below); everything in §4 is Mac, DIRECTIONAL.

## 1. What was copied (the `emit` comparator)

- **Pin d4d9ed90, abi 61.** `git diff d4d9ed90 HEAD -- src cli lib` is empty
  on the lane branch, and main has not touched those trees since f116cff5
  (the T3 handoff), so the artifacts are the pin's. Emitted with this
  worktree's `build/pcrec --features all -p rx` (alpha_k82.sh's flags) from
  the bench pattern files.
- **The text:** `docs/design/memfn/probes/twins/gates_d4d9ed90/`.
  - `<cell>_def.inc`: the artifact's `rx_reqrun` definition, plus the
    `rx_wN` helper line directly in front of it when there is one. It is
    byte for byte, cut by line range, and tb_r4b.c `#include`s it under
    `#define` renames.
  - `<cell>_use.txt`: the entry's pre-check lines.
- **Provenance check:** `twins/gates_sync.sh` re-emits with any pcrec
  binary and checks four things:
  - each artifact's first line says abi 61;
  - the definition, extracted by pattern (not by the line numbers it was
    cut at), equals the `.inc`;
  - the use lines equal the `.txt`;
  - cls-n-uc's `-fno-req-set-lead` artifact differs from the default by
    exactly the three set-leads lines.

  Results:
  - `GATES-SYNC ok` against this worktree's build.
  - `GATES-SYNC ok` against a `git archive d4d9ed90 | make` build (the
    Linux script's own step 2, smoke-run on the Mac).
  - Sabotage: one changed byte in `cn_def.inc` plus one in `up_use.txt`
    gave `GATES-SYNC FAIL 2`, naming both.
- **What changed since twins.md's 8a41efd2 copy:**
  - The three `rx_reqrun` bodies are IDENTICAL to tb_run.c's (diffed
    modulo the function name).
  - userpass's SITE gained the set-leads `memchr('=')` pre-check (K82
    (A), abi 60). On the capability text `=` never occurs, so userpass's
    gate is now one `memchr('=')` that rejects.
  - mod-i and cls-n-uc use the handoff (`handoff_position`).
  - union-select stays on the no-handoff route: the call is compared with
    n and its position is discarded.
  - tb_run.c is labelled STALE as a comparator in its header and in
    twins/CLAUDE.md. It is kept as R1d's record.
- **The wrappers** (tb_r4b.c `emit_<cell>`) are the use lines with one
  substitution: `return 0;` becomes `return subject_length;` (the gate's
  miss value). union-select's wrapper returns the call's value.
- **The function computed** (tb_r4b.c header): `n` if there is a lead and
  no lead byte in `[pos, n)`; otherwise the first `c >= pos` with
  `c + L <= n` and `(s[c+j] & M[j]) == V[j]` for all `j < L`; otherwise
  `n`.

| cell | pattern | run (scan @KA, 2nd @KB) | lead (set-leads) | route |
|---|---|---|---|---|
| us union-select | `(?i)union.*?select.*?from` | SELECT (C/c @4, T @5), 0xDF | none | no-DFA, no handoff |
| up userpass | `(?:username\|USERNAME\|user\|USER)…` | USER (U/u @0, R @3), 0xDF | `=` | handoff |
| mi mod-i | `(?i)cat` | CAT (C/c @0, T @2), 0xDF | none | handoff |
| cn cls-n-uc (K85) | `it\Nm` | it (i @0, t @1), exact | `m` | handoff, K = 0 |

cls-n-uc's pattern was read from the Mac bench copy
(`/Users/fdicostanzo/pcrec-bench/bench/syntax/patterns/cls-n-uc.rx`). It was
NOT copied into the probe directory: `gates_sync.sh` and the Linux script
read it from `$BENCH/bench/...` like every other cell, so no second copy can
drift. The probe dir carries the EMITTED text, which is the comparator. No
ssh to ubuntubudu was needed.

## 2. `swar` — the portable fused form, and its boundary argument

`tb_r4b.c` `f_swar` is plain gcc-dialect C. It uses 64-bit words,
`memcpy` loads, `__builtin_ctzll`, and on big-endian targets only
`__builtin_bswap64`. There are no intrinsics and no ISA text. One word holds
eight candidate positions:

- **Pair filter.** Mask and XOR the word at `i+KA` against the scan byte
  and the word at `i+KB` against the second byte. EXACT zero-byte detection
  (`~(((x & 0x7F…) + 0x7F…) | x | 0x7F…)`, no inter-byte borrow) marks the
  matching bytes, and the two marks are ANDed.
- **Verify.** Surviving lanes are verified lowest-first with the masked run
  compare (`run_eq`, the emitted overlapping-word shape). For a 2-byte run
  whose filter covers both bytes, the filter IS the verify.
- **Loop shape.** Two words per iteration, then one, then ONE overlapped
  final block ending at `n`, with its lanes before `i` masked off.
- **Lead.** The lead is OR-accumulated in the same pass, from the word at
  `i`. When a run verifies at `c`, the bytes `[pos, cov)` have been looked
  at. If the lead was seen, the answer is `c`. Otherwise the rest
  `[cov, n)` gets one libc `memchr` (a scalar-layer call, Q50), and the
  answer is `c` or `n`.

**Over-read argument: the kernel never reads outside `[pos, n)`.** No
page-safety or alignment assumption is needed, and the ASan exact-size and
guard-page checks pass. The full argument is in the source comment above
`ld64`; in short:

- Spans with `n - pos < 8 + T` (`T = L - 1`) take the byte loop.
- Loop loads are at `i + {0, KA, KB}` with `KA, KB <= T`. The loop guards
  are `i + 16 + T <= n` and `i + 8 + T <= n`, so the highest byte read is
  at most `n - 1`.
- The final block is at `f = n - T - 8 >= pos`, and its highest byte is
  `n - 1`. On exit `f < i <= f + 8`, and `i - f = 8` is impossible while
  `i + L <= n`, so the lane-mask shift is 8..56. The lead coverage stays
  contiguous.
- A candidate `c <= base + 7` has `base + 7 + T <= n - 1`, so the verify
  stays in bounds.

**Two other variants:**
- **`ffl`** (vector) is T-B's form with per-byte masks and the same lead
  accumulation. One change: a span shorter than `VW + T` now takes `f_swar`
  rather than a byte loop, so the SIMD layer is the scalar layer plus what
  it adds (D147). Without this change ffl LOST to swar at 16 B (it ran a
  byte loop there; first Mac run, not archived).
- **`swlf` / `ffllf`** were added after the first Mac run showed the
  run-first order losing on userpass. They keep pcrec's order: the emitted
  one-shot lead `memchr`, then swar or ffl over the run alone. This is the
  kit replacing `rx_reqrun` only and honouring §15.5's order hint.

## 3. Correctness (before any timing)

`tb_r4b --check --subjects=DIR` checks every variant's whole sweep against
`ref()`. `ref()` is the definition read literally: a backward byte loop for
the lead, a per-position, per-byte loop for the run. It shares no code with
any variant: no `run_eq`, no word loads, no memchr. The cell constants are a
separate table. `emit` derives from pcrec's text, not from that table, so a
wrong row in the table would show up as `emit` != ref.

**Populations checked:**
- **Generated set:**
  - n from 0 to 129, alignments 0..15 in EXACT-size allocations;
  - the run planted at every offset, plus no run;
  - for lead cells, four lead modes: absent, only at n-1, only at 0,
    random;
  - near-miss filler: run bytes in both cases, `^0x20`, `^0x80`, noise;
  - sweeps from 0 and from h/2.
- **Guard pages** at both ends, with 16 start offsets.
- **Fuzz:** 3,000 spans per cell, up to 700 B, several runs each.
- **Real subjects:** every throughput subject of the cell plus the 75
  short subjects.

**Results:**
- Real variants: **0 wrong** in every build:
  - gcc-16 NEON;
  - clang NEON;
  - clang ASan+UBSan NEON;
  - clang `-arch x86_64` SSE2, AVX2 and ASan+UBSan AVX2 (Rosetta 2,
    correctness only).

  Calls per variant: 0.40M (us), 1.16M (up), 0.51M (mi), 2.12M (cn).
  Ref-hit calls: 0.19M / 0.33M / 0.30M / 1.30M.
- Real subjects alone: 81 / 78 / 6,510 / 5,580 calls, with 4 / 1 / 6,433 /
  5,502 hits.
- **Planted defects: 10 of 10 CAUGHT in every build.**
  - `Ptail`: swar's final-block guard is off by one, so it misses a hit at
    `n-L` when that is the only lane left. Caught in all four cells, with
    356-762 bad sweeps.
  - `Pffltail`: the same defect in ffl. Caught in all four cells, 165-339
    bad sweeps.
  - `Plead`: the lead's rest search stops one byte short. Caught on up and
    cn, ~190k-205k bad sweeps.

  `--check` exits non-zero if any real variant is wrong OR any planted
  variant is missed.
- **Population caveat:** on userpass the real subjects say little (1 hit),
  because `=` is absent from the capability text. Its correctness evidence
  is the generated set.

Transcripts: `docs/design/memfn/probes/out/twins/r4b/check.*.txt`.

## 4. Mac directional table (gcc-16 -O2, NEON, M1, unpinned; ONE launch)

The full rendering is `docs/design/memfn/probes/out/twins/r4b/tb_r4b.mac.gcc.table.md`
and the raw `R` rows are in `tb_r4b.mac.gcc.txt`.

- **Units:** ns. gate, short and pc* are per call; sweep is per find-all.
- **Floor:** |emit - emit2|, the same gate timed as a second instance in
  the same binary.
- Verdicts mark a delta past that floor. On the Mac they are DIRECTIONAL
  only.

| cell | regime, subject | emit | floor | swar | ffl (NEON) | byte | swlf | nosl |
|---|---|---|---|---|---|---|---|---|
| union-select | gate cap t-64k (no hit) | 17,420 | 297 | **7,657** | 2,380 | 43,551 | | |
| union-select | gate cap t-1m | 473,815 | 11,315 | **122,835** | 38,039 | 690,133 | | |
| union-select | short (75) | 5.60 | 0.04 | **3.81** | 3.11 | 6.99 | | |
| union-select | pc16 / pc64 / pc256 / pc1024 | 6.67 / 13.81 / 57.6 / 263 | ≤17.8 | **3.31 / 8.72 / 31.2 / 121** | 2.98 / 3.39 / 10.1 / 37.9 | 7.1 / 37.9 / 172 / 682 | | |
| userpass | gate cap t-64k (`=` absent: n) | 1,346 | 6.7 | 1,395 (LOSS +49) | 1,341 | 21,020 | 1,328 | |
| userpass | gate cap t-1m | 24,419 | 54 | 23,725 | 24,196 | 331,427 | 24,404 | |
| userpass | short (75) | 3.04 | 0.02 | 4.00 (LOSS) | 3.01 | 7.78 | **2.78** | |
| userpass | pc16 / pc64 / pc256 / pc1024 | 2.00 / 4.25 / 8.09 / 24.1 | ≤0.56 | 3.92 / 10.4 / 30.3 / 68.0 (all LOSS) | 3.92 / 3.83 / 11.3 / 32.7 | | 1.96 / 4.18 / 8.03 / 23.4 | |
| mod-i | gate syn t-64k | 52.55 | 0.47 | **11.87** | 4.81 | 51.25 | | |
| mod-i | sweep syn t-64k (400 hits) | 35,362 | 3,594 | **9,206** | 5,193 | 49,157 | | |
| mod-i | sweep syn t-1m (6,030 hits) | 852,261 | 3,725 | **177,302** | 135,830 | 845,429 | | |
| mod-i | short (75) | 6.48 | 0.04 | **4.20** | 3.19 | 8.21 | | |
| mod-i | pc16 / pc64 / pc256 / pc1024 | 6.63 / 15.0 / 38.4 / 54.3 | ≤1.66 | **4.23 / 7.90 / 16.6 / 19.6** | 3.45 / 3.28 / 6.20 / 7.20 | | | |
| cls-n-uc | gate syn t-64k | 29.59 | 0.44 | 30.01 (NULL) | 8.63 | 79.09 | **23.28** | 29.38 |
| cls-n-uc | sweep syn t-64k (262) | 22,723 | 533 | **10,571** | 4,152 | 36,402 | **8,553** | 19,489 |
| cls-n-uc | sweep syn t-256k (1,064) | 147,582 | 2,535 | **44,400** | 16,926 | 160,003 | **34,883** | 129,766 |
| cls-n-uc | sweep syn t-1m (4,176) | 610,537 | 9,183 | **196,723** | 91,029 | 675,736 | **174,510** | 564,533 |
| cls-n-uc | short (75) | 3.17 | 0.05 | 3.67 (LOSS +0.5) | 2.86 | 6.94 | 3.11 | 4.15 |
| cls-n-uc | pc16 / pc64 / pc256 / pc1024 | 3.55 / 9.90 / 29.5 / 62.4 | ≤10.2 | 3.71 / 9.32 / 25.4 / 43.7 | 3.31 / 3.14 / 7.04 / 11.6 | | 3.21 / 8.53 / 20.4 / 33.5 | 4.36 / 9.35 / 26.8 / 58.5 |

### What the Mac table says (directional)

- **SIMD-off (swar vs emit).**
  - swar wins far past the floor on union-select and mod-i in every regime.
    union-select's gate on t-64k is 7,657 against 17,420 ns, and mod-i's
    t-1m sweep is 177k against 852k. The emitted gate's cost is its stops,
    one per scan-byte occurrence (twins.md §3.3), and the exact pair filter
    removes them.
  - On cls-n-uc swar wins every sweep: on t-1m, 197k against 611k, which
    is also 368k below `nosl`.
  - swar LOSES on userpass in every per-call cell and on t-64k. Its lead
    `=` is absent, so the emitted gate is one `memchr('=')` that rejects.
    Run-first swar pays a pair scan before it reaches the lead.
  - **R4d's trigger as R-1 states it** ("swar beats emit past the floor on
    at least one K82 cell in its own regime, with no loss past the floor in
    the other") READS MET on union-select and mod-i, directionally.
  - **For userpass, the trigger is met only in the lead-first form.**
    `swlf` is the kit taking the run part only. It is NULL-or-WIN against
    `emit` on every userpass row, because it IS `emit` there (the lead
    rejects first).
- **SIMD-on (ffl vs swar).** With the short path fixed to swar, ffl wins or
  ties swar on every cell except the userpass lead-absent throughput rows,
  where both equal one `memchr`. Linux must read SSE2 and AVX2 separately:
  linux_results.md §6.2 saw AVX2 lose about 2.5 ns per call on short
  subjects.
- **K85 (cls-n-uc).**
  - The set-leads pre-check's own cost (`emit - nosl`) on the Mac is
    +0.2..+2.2 ns per gate call and +3.2k / +17.8k / +46k ns per find-all
    sweep at 64k / 256k / 1m: the dense-text loss, reproduced.
  - **Both fused forms remove it and more.** swar's sweep is 197k against
    `nosl`'s 565k on t-1m, because the exact pair filter also removes the
    `memchr('i')` stops of the run part.
  - **The best scalar on the Mac is `swlf`** (lead first, then swar), at
    175k, not run-first swar. The OR-accumulated lead costs about four ALU
    ops per word, more than one fresh `memchr('m')` that finds an `m`
    within a few bytes.
  - That is the Mac's libc. On Linux, glibc's `memchr` per-call cost is
    about 3.5 ns against about 1 ns here (requirements.md §2.4,
    linux_results.md §6.2), so the run-first vs lead-first order is
    exactly what the Linux run must decide.
  - The short subjects (1..93 B) are the one place `nosl` is slower than
    `emit`: the `m` lead DOES reject short chunks.

## 5. The Linux verdict script — OWED to main's executor

`docs/design/memfn/probes/lxrun/memfn_r4b.sh`, run from the root of a
checkout carrying it (this branch or the kit branch after merge):

    cd <checkout>; CPU=2 gnutimeout 120m bash docs/design/memfn/probes/lxrun/memfn_r4b.sh /home/duxevents/pcrec/scratch_lx/r4b

**Steps** (every step under `gnutimeout`; steps 1-4 ABORT the run on
failure):
1. Subjects: `subjects_r4b.py`, alpha_k82.sh's resolution, sha256-checked.
2. pcrec at d4d9ed90: `git -C $PCREC_REPO archive | make`, then
   `gates_sync.sh`.
3. Builds: gcc 15.2 `-O2 -march=x86-64` (SSE2, the SIMD-off build) and
   `-march=x86-64-v3` (AVX2); clang the same (directional); gcc ASan+UBSan.
4. `--check --subjects` on every build.
5. Timing: 3 launches round-robin over gcc-sse2 and gcc-avx2, pinned with
   `taskset -c $CPU`, waiting for load1 < 0.5 (at most 600 s). Each launch
   uses ≥ 50 ms calibrated loops (min of 3); the floor is emit vs emit2 in
   the same binary. clang gets one launch per build.
6. Readings: `readings.gcc.md` / `readings.clang.md` from
   `tb_r4b_table.py`. The SIMD-off reading is swar − emit and swlf − emit in
   the SSE2 build. The SIMD-on reading is ffl-SSE2 and ffl-AVX2 − swar(SSE2).
   cls-n-uc adds the `nosl` columns. All deltas are read against the floor.

**Expected wall: ~20-25 min** on a quiet box (cap 120 min).

**Completion line** (last line of `OUTDIR/run.log` and stdout):
`R4B-DONE status=<n> dir=<OUTDIR>`, where 0 means clean and an abort
prints its step number.

**Mac smoke** (`QUICK=1 LAUNCHES=2 CLANG= BUILDS="gcc-sse2:gcc-16:
gcc-avx2:gcc-16:" ASANFL=`, unpinned and never a verdict) ran every step:
`git archive d4d9ed90 | make`, `GATES-SYNC ok`, three builds, three checks
clean, four timed launches and `readings.gcc.md`, ending
`R4B-DONE status=0`.

- The first smoke found three script defects, all fixed:
  - clang was timed when only gcc builds existed;
  - the table script crashed on an empty group;
  - a `case` pattern skipped the readings.
- The pcrec build step's final form (make output to `pcrec.build.log`) was
  run once as a no-op rebuild. It was not run from scratch in the final
  smoke.

**One caution for the reader of the Linux readings:** the floor is
`emit`-vs-`emit2` only. In the first smoke, on a box at load ~19, `swlf`
on userpass t-1m read `LOSS` by 494 ns against a 310 ns floor. swlf
executes the same `memchr` as emit there, so a third launch or a re-read
should settle any lone verdict that sits near the floor.

## 6. What would change integration.md §15.5's composite-site description

1. **The order hint is load-bearing, not a nicety.** §15.5 says the order
   (lead, then run) "is a hint the baseline honours and a non-baseline arm
   may revise (lead and window fused into one pass…). That is K85's
   general answer." The measurement says otherwise:
   - Fusing the lead INTO the run pass is not uniformly better.
   - When the lead rejects (userpass on the capability text), the
     run-first fused form LOSES per call at every length.
   - When the lead never rejects (cls-n-uc on dense text), the Mac's best
     scalar is still lead-first (`swlf`). The K85 cure there comes from
     the fused RUN filter, not from fusing the lead.

   Suggested rewording: *"K85's general answer is the kit's form for the
   window RUN part (an exact pair-filter scan with the run verify in the
   same pass, which removes the per-scan-byte stops). Whether the lead is
   tested first (one call) or folded into the run's pass is the kit's
   per-site choice, made on the Linux reading in both regimes. The
   baseline's order is the default."*

   This holds pending Linux, where glibc's per-call `memchr` cost may flip
   cls-n-uc toward run-first.
2. **A fact the site should carry:** whether the lead can REJECT on the
   site's text class. This is K85's suspected cause ("says nothing about
   whether the one-shot check can REJECT"). With it the kit can pick
   lead-first or folded without a cost model. Without it, the evidence says
   lead-first is the safe default. This is a density hint, which the
   boundary table already gives pcrec.
3. **The part 1 handoff contract is unchanged.** Every fused variant
   returns the exact leftmost run position (ASSIGN, `ret_pred = 1`); the
   check proves equality with the emitted gate's value.

## 7. Charter vs committed

| R-1 promise | artifact / state |
|---|---|
| `emit` re-copied verbatim at the run's pin (us/up/mi) | `twins/gates_d4d9ed90/{us,up,mi}_{def.inc,use.txt}`, pin + abi in tb_r4b.c's header and here; `gates_sync.sh` (sabotage-validated) — DONE |
| 8a41efd2 copy retired | tb_run.c header + twins/CLAUDE.md say STALE — DONE |
| `swar` portable fused pair-filter, over-read argument | tb_r4b.c `f_swar` + comment block (§2) — DONE |
| `ffl` SSE2 + AVX2 builds | tb_r4b.c `f_ffl`; built + checked under Rosetta; Linux timing — **OWED (main's executor, memfn_r4b.sh)** |
| byte loop: reference, timed | `f_byte` timed; the correctness reference is `ref()`, deliberately not the timed variant (learnings §3) — DONE |
| K85 cls-n-uc vs `-fno-req-set-lead` (no `-fno-req-handoff`) | `cn` cell + `nosl` (gates_sync proves exactly three lines); Mac reading §4; Linux **OWED** |
| subjects as alpha_k82.sh resolves them | `subjects_r4b.py` (sha256 OK, all 6 throughput + 75 short) — DONE |
| THROUGHPUT and PER-CALL regimes | gate/sweep at t-64k/t-1m (+t-256k on cn); short (75) + the pc16..pc1024 ladder — DONE (Mac) |
| correctness: generated set, every subject, planted fail | §3 — DONE, 6 builds |
| Mac directional, short, under timeout + caffeinate | `out/twins/r4b/tb_r4b.mac.gcc.{txt,table.md}` — DONE |
| Linux verdict script | `lxrun/memfn_r4b.sh`, smoke-run end to end on the Mac — DONE; **the run is OWED to main's executor** |
| per cell × regime: emit, swar, ffl-SSE2, ffl-AVX2, floor; SIMD-off and SIMD-on readings; K85 | Mac (NEON) §4; x86 readings **OWED** (`readings.gcc.md`) |
| `done:` in responses.md | the kit session's, after the Linux read |
| §15.5 changes | §6 (proposal; integration.md not edited by this lane) |

**Deviations:**
- R-1 says the short subjects are 16 B–1 KiB. They are 1..93 B. The pc16,
  pc64, pc256 and pc1024 ladder (chunks of the cell's t-64k) was added to
  cover the declared range.
- The `swlf`/`ffllf` variants are beyond the brief, added because §4's
  first read made the order question unavoidable.
- The `ffl` short path changed to swar (§2).

## 8. Files

- `docs/design/memfn/probes/twins/`:
  - `tb_r4b.c`, `gates_d4d9ed90/`, `gates_sync.sh`, `subjects_r4b.py`,
    `tb_r4b_table.py` (all new);
  - `tb_run.c` (stale label);
  - `CLAUDE.md`.
- `docs/design/memfn/probes/lxrun/memfn_r4b.sh` (new), `lxrun/CLAUDE.md`.
- `docs/design/memfn/probes/out/twins/r4b/`: Mac transcripts (check × 6,
  timing raw + table); `out/CLAUDE.md`.
- `docs/design/memfn/probes/CLAUDE.md`.
- Scratch, not committed: `build/r4b/` in the worktree (subjects, binaries,
  the smoke run's OUTDIR `build/r4b/lxsmoke/out`).

## 9. The Linux verdict (added by the kit session after main's executor run)

**Run.** `memfn_r4b.sh` at probe 4ecea50b (the first attempt, at
7549a3b8, aborted at step 4 on a LeakSanitizer finding in the harness:
the `short.bin` load buffer was never freed; fixed in 4ecea50b — macOS
ASan has no LSan, so the Mac checks could not see it). ubuntubudu, AMD
Ryzen 5 1600, gcc 15.2.0, `taskset -c 2`, governor schedutil, boost on,
load 2.12 at start (the script waits for load1 < 0.5 before each timed
launch), 0.78 at end; 16:23→16:41 EDT. `R4B-DONE status=0`. Steps 1-4
green: subjects sha256 0 mismatches, pcrec@d4d9ed90 built, GATES-SYNC ok,
5 builds; correctness 0 wrong / 10 of 10 planted caught in gcc-sse2,
gcc-avx2, clang-sse2, clang-avx2 and gcc ASan+UBSan+LSan. Timing: 3
launches per gcc build (median), floor = max |emit − emit2|. Transcripts:
`docs/design/memfn/probes/out/twins/r4b/linux/`; the table is
`readings.gcc.md` there.

**SIMD-off reading (`swar` vs `emit`, gcc SSE2; ns, delta, floor):**

| cell | throughput (gate / sweep, 64k and 1m) | per-call (short75, pc16..pc1024) |
|---|---|---|
| union-select | WIN everywhere: gate 1m 364,078 → 187,022; sweep 64k 16,580 → 11,422 | WIN everywhere: short 11.50 → 5.83; pc1024 272 → 195 |
| mod-i | sweep WIN (1m 724,503 → 267,480; 64k 34,851 → 15,546); gate 64k WIN (46.2 → 20.3); gate 1m LOSS +2.41 (floor 0.52; first hit at 404) | WIN everywhere (short 13.54 → 6.05) |
| userpass | `swar` LOSS everywhere (gate 64k +35.6, pc1024 +86); lead-first `swlf`: NULL on gate/sweep except sweep 1m LOSS +3.07 (floor 2.53) | `swar` LOSS; `swlf` NULL or WIN (short 6.00 → 5.25) |
| cls-n-uc (K85) | sweeps WIN (1m 437,242 → `swar` 286,914, `swlf` 242,662, nosl 403,594); gate 64k/256k LOSS (`swar` 147 vs 76.5 at 256k; `swlf` 108) | `swlf` WIN at pc16..pc1024, short +0.04 = floor (LOSS by the rule) |

**R4d's trigger** ("`swar` beats `emit` past the floor on at least one K82
cell in its own regime, with no loss past the floor in the other"): **MET
on union-select.** It wins every row in both regimes, by 1.4-2.0x on
throughput and 1.4-2.0x per call. mod-i nearly meets it too: one
throughput row loses by 2.4 ns on a single early-hit gate call. userpass
shows that the ORDER is part of the form. Run-first loses wherever the
lead rejects first (`=` is absent from the capability text); lead-first
is null there.

**SIMD-on reading (`ffl` vs `swar`):** `ffl` wins every row on every
cell, at both SSE2 and AVX2, with two exceptions at 16 B: userpass pc16
and cls-n-uc pc16 at AVX2 (+0.64 and +0.36 ns). Short vector spans
belong to the scalar form; that is a cascade/short-path detail for
R4e′, not a verdict against the layer.

**What the numbers say about the scalar form itself:**
- `swar`'s raw scan rate is ~0.18 ns/B (union-select 1m, no stops), and
  `ffl`'s is ~0.04. glibc's AVX2 `memchr` scans faster still, so `swar`
  wins only where `emit` pays per-stop costs (union-select's 1,431 `c`
  stops per 64 KiB; mod-i's and K85's find-all sweeps).
- It loses where a short distance to the first hit gives `emit` few
  stops: mod-i gate 1m, cls-n-uc gates at 64k/256k. That is a regime
  boundary of the portable form, not a defect.
- The raw rate is set by the unmeasured choices: the 2x unroll and the
  exact `zbytes`. Frank, 2026-10-05: tuning constants are suspect, so
  measure them or leave them to the compiler. R4d's form starts from
  the plain loop, under measurement.

**K85:** both fused forms remove the dense-text loss in the find-all
regime and beat the no-gate floor (nosl). At 1m: `swlf` −160,932 ns vs
nosl, `ffl` AVX2 −306,068. The single-call gate on dense text still
loses at SIMD-off. The fused RUN filter with the lead first is the
general answer, as §6 proposed; the lead order is a kit per-site choice.

**§15.5 consequence (for the integration.md revision, a kit design
deliverable after main's review):** the composite site's form takes
the lead order as a kit choice. Lead-first is the default when a lead is
present (userpass, K85), and the fused run filter follows it. A "lead
can reject" density fact from pcrec would let the kit choose run-first
where the lead is dense. The SIMD-off form must not be selected for
early-hit single gate calls on dense text without that fact. Both are
noted for R4d's design, not built now (D77).

**Charter vs committed, updated:** the Linux verdict, OWED in §7, is
DONE: `docs/design/memfn/probes/out/twins/r4b/linux/`, read above.
