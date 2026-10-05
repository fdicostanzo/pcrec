# memory-functions: R1d, THE HAND TWINS — tailored kernels against generic ones

Owner row: `[MEMFN]` (docs/dev/plan.md). Lane `memftwin`, 2026-10-04,
written from main at 8a41efd2. This is the D77 measurement behind the
binding-form question that `requirements.md` §2 and `survey.md` §9 left
open: **does a kernel TAILORED to the pattern beat a fixed generic kernel,
on real bench cells?** Three twins answer three halves of it:

- **T-A**: a set classifier chosen per class SHAPE, against the generic
  two-table nibble lookup and a scalar 256-table loop (requirements.md F4).
- **T-B**: one FUSED scan+verify loop for a caseless run, against what
  pcrec emits today (two libc `memchr` streams, then a masked compare;
  `../../dev/lanes/k82diag_report.md` §1) and a memchr2-style pass plus a
  separate verify.
- **T-C**: one header-only `always_inline` kernel given a compile-time
  `static const` descriptor, against the hand-specialized kernel: same code?
  same speed?

Docs and probes only; nothing under `src/`, `cli/`, `lib/` or `tests/`
changes, and nothing here touches pcrec's emission (D91). Evidence:
`probes/twins/` (the twins, their run script, the subject materializer) and
`probes/out/twins/` (transcripts). Bench patterns and subjects were READ from
`/Users/fdicostanzo/pcrec-bench`, never written (`twins/subjects.py`
regenerates the gitignored subjects into the scratch tree and checks every
sha256 against the bench's committed manifests: 0 mismatches).

**Every number below is Mac, directional only** (M1 Max, gcc-16.2 and Apple
clang 21, `-O2`, not pinned, box load 4-6 from other lanes). D144 addendum 1
applies: timings are absolute ns from calibrated loops of at least 50 ms,
min of 3, with the max-min spread printed next to every cell in the
transcripts as the noise floor. Differences are given as absolute deltas,
never as percentages of a few ns, and a delta inside the spread is NULL. The
verdicts the Mac cannot give are queued for Linux (§5).

---

## 0. Findings first

1. **T-A: the shape-tailored classifier is worth having, but it is a small
   lever, and on the dense side it is the wrong lever.**
   - On a MISS (the scan rejects; the whole span is read) the tailored
     classifier saves **about 1,000 ns per 64 KiB for a range or a one-bit
     cube** (`[0-9]`, `{S,s}`: ~1,100 ns against the generic nibble
     lookup's ~2,100), **~600-700 ns for an eq2, a two-bit cube and a
     nibble-unique set**, nothing for an eq3, and it LOSES ~1,000 ns for
     `\w`, where the shape form needs three tests and the nibble lookup
     needs one. That is 0.010-0.016 ns/B, against an engine scan of
     0.5-0.8 ns/B (k82diag §1.B). It matters only where the scan IS the
     call: a rejecting prefilter on a subject the class is absent from.
   - At 16-64 B every vector form is ~2-3 ns and the deltas are inside the
     spread: NULL.
   - **On dense text the classifier does not matter; the restart does.**
     At one hit per 13 B every vector find-first costs ~7.5 ns per hit
     (~38,000-41,000 ns per 64 KiB, all classifiers within ~3,000 ns of
     each other) and LOSES to the scalar table loop (~26,000 ns). The
     `iter` control (the same classifier, the block mask kept across hits)
     removes the restart (§2.3). The API shape (find-first vs iterate) is
     the bigger lever for F4 than the classifier.
   - The generic nibble lookup does not exist on an SSE2-only x86 build
     (`pshufb` is SSSE3): there, the shape classifiers are the ONLY vector
     form, which makes the shape table a requirement on x86-64-v1, not an
     optimization. **Linux decides the x86 numbers.**
   - One memchr per member (`libc`, today's pair-arm shape) loses to every
     inline vector form at every span, by ~1,300 ns (eq2) and ~2,000 ns
     (eq3) per 64 KiB on a miss, and on the real text with `\h` it goes
     super-linear (7.2 ms per 64 KiB): each restart re-searches every
     stream fresh, k82diag's 4.8x-the-subject pathology.
2. **T-B: the fused scan+verify is worth it, by a wide margin, on all three
   K82 cells.** One loop that tests the run's scan byte AND a second byte at
   its known offset (`ffl`) against today's emitted gate (`emit`):

   | cell, subject | emit | ffl | delta |
   |---|---|---|---|
   | union-select, cap t-64k, one gate call (run absent) | 16,829 ns | 2,408 ns | −14,421 ns |
   | union-select, cap t-1m, one gate call | 478,402 ns | 38,964 ns | −439,438 ns |
   | userpass, cap t-64k, sweep (212 gate hits) | 27,912 ns | 3,907 ns | −24,005 ns |
   | mod-i, syn t-64k, sweep (400 gate hits) | 40,594 ns | 5,331 ns | −35,263 ns |
   | capability short subjects (75), per subject, the three cells | 5.5-6.8 ns | 3.6-3.7 ns | −1.9 to −3.2 ns |

   (gcc-16; clang-21 within the spread of these, §3.2.)

   The cost the fused loop removes is the **per-candidate stop**: the
   emitted gate stops on every `c`/`C` (1,431 of them in the capability
   t-64k; the run `SELECT` never occurs) at ~10 ns a stop, k82cost's `s`.
   Filtering on the PAIR (`C` at offset 4 AND `T` at offset 5) leaves zero
   candidates there, so the fused gate is a pure scan at ~0.036 ns/B. On
   `mod-i`'s sweep the gate goes from ~0.62 ns/B (as much as the DFA it
   guards) to ~0.08 ns/B. It does not remove cause B's double scan
   (litscan_k82b.md's T3 handoff does that); it shrinks the first scan by
   ~35,000 ns per 64 KiB, and the two compose. The all-bytes variant
   (`fall`, no verify) is slower than `ffl` on every cell: the second
   filter byte is enough, and extra loads cost more than the verifies they
   save.
3. **T-C: a `static const` descriptor through one header-only kernel IS the
   hand-specialized kernel, under both compilers.** Disassembly diff
   (§4.1): clang emits the identical instruction multiset for 4 of 6 shapes
   and differs only in the scalar `n < 16` byte loop (a table read through
   a struct offset) for the other two; gcc emits the same vector loop with
   different register allocation and scheduling. Timing (§4.2): hand and
   descriptor are within the spread at every span. The descriptor MUST be
   a compile-time constant: the control with a writable EXTERNAL
   descriptor compiles to the generic switch-in-the-loop kernel (~3x the
   instructions) and costs ~600-700 ns more per 64 KiB under clang (gcc
   unswitches that loop, so its cost there is ~+1 ns a call and up to
   ~250 ns per 64 KiB). The
   run-time library form with the shape switch hoisted once per call
   matches the hand kernel from 4 KiB and costs +0.3-1.6 ns per call at
   16-256 B. **So injected text can be "one shared kernel header + one
   descriptor per site", not per-pattern kernel text**, which is what
   `requirements.md` §2.1's B3 form needs to stay small.
4. **What goes in the Linux queue** (§5): `twins/twins_run.sh`, appended to
   `probes/linux_run.sh`, builds every twin at SSE2 / SSSE3 / AVX2 under gcc
   and clang, `--check`s each (plus ASan+UBSan), diffs T-C's disassembly on
   x86, and times T-A at five builds and T-B/T-C at all six. About 50
   minutes, pinned. It decides: the x86 shape-vs-nibble numbers (and
   whether SSSE3's `pshufb` changes the T-A ranking), T-B against glibc's
   AVX2 `memchr` (whose per-call and per-stop terms differ from the Mac's),
   and T-C's code identity on x86.

Correctness: every twin, every build, exhaustive against an independent
scalar reference (positions × lengths × alignments, every byte value, guard
pages at both ends, fuzz), clean on NEON (gcc, clang, clang ASan+UBSan) and
on x86 SSE2 / SSSE3 / AVX2 plus AVX2 ASan+UBSan under Rosetta 2: 0 bad
across 46.4M (T-A), 24.5M (T-B) and 31.7M (T-C) cases per build
(`probes/out/twins/check.rosetta.txt`, `run.log`). The checks are shown to
fire: §1.3.

---

## 1. Method

### 1.1 The harness

`probes/twins/vec.h` is one vector layer for four ISAs (NEON, SSE2, SSSE3,
AVX2; `VW` = 16 or 32 B), with `callcost.c`'s mask idioms (NEON `shrn #4`,
x86 `movemask`). Every set kernel in T-A and T-C is the SAME skeleton
(`FIND_BODY`): 4×VW blocks tested through one OR (memchr's unroll), then VW
blocks, then one overlapped final block ending at `n`, and a byte loop below
VW. Only the classifier differs from row to row, so a row-to-row difference
is the classifier's. Each timed body is a `noinline` function with the
kernel inlined into it (callcost's TIMER shape), calibrated to >= 50 ms per
loop, run 3 times, min reported with the spread.

### 1.2 Subjects

- T-A: synthetic spans with a non-member background (`none`), a member every
  1,009 B (`sparse`) or every 13 B (`dense`), plus `real`: the syntax
  sub-bench's own t-64k text (`syn-t-64k`, regenerated from its
  `censustext.py` at its seed; sha256 = the bench manifest's), with whatever
  density each class has in it (`\w` is 50,015 of 65,536 bytes).
- T-B: the capability sub-bench's t-64k / t-1m (union-select and userpass
  are capability cells) and the syntax t-64k / t-1m (mod-i is a syntax
  cell), plus the capability set's 75 short subjects (1-512 B) as the
  short-call regime.

### 1.3 Correctness, and that the checks can fail

Each twin's `--check` compares every kernel against a reference built from
the member list (T-A), the run's masked definition (T-B) or a byte loop over
the descriptor predicate plus the hand kernel (T-C) — never from a
classifier under test. Spans end exactly at a heap allocation's end (the
ASan build turns an over-read into a report) and sit flush against
`PROT_NONE` pages at both ends; every alignment 0..31 and every hit
position; all 256 byte values planted alone (the case that catches a
`pshufb` high-bit or a signed-compare slip); and random fuzz of whole
find-all sequences.

The checks fire:
- **A real bug, caught on the first run.** `{A,B,a,b}` (bc019) was first
  spelled as the absolute cube `(c & 0xDE) == 'A'`, following
  `../../dev/cls_tree_study.md` §4.3's line `(c & ~0x21) == 'A'`. It is
  wrong: `'A' ^ 'B'` is 0x03, so the set is a cube only over `x = c − 'A'`
  (`cube_of`'s own form). 1,746,728 bad cases. Fixed to
  `((c − 'A') & 0xDE) == 0`. (The study's table writes the cube in absolute
  form for that row; its `cube_of` computes the offset form, so the study's
  kit is right and its prose shorthand is not.)
- **Two sabotages**: the final overlapped block skipped when exactly one
  byte remains (T-A, `FIND_BODY`: 12,750 bad) and a run ending exactly at
  `n` skipped (T-B, `f_fused`: 6,036 bad).

---

## 2. T-A: set classifier per shape vs generic

### 2.1 The sets

| id | class | members | shape | tailored classifier | provenance |
|---|---|---|---|---|---|
| q2 | `["']` | 2 | eq2 | `c == a \| c == b` | userpass bench cell |
| h3 | `\h` | 3 | eq3 | three compares | corpus bc024 |
| d | `[0-9]` | 10 | range | `(c − '0') <= 9` unsigned | the byte tier of `\d` |
| ss | `{S,s}` | 2 | cube, 1 free bit | `(c & 0xDF) == 'S'` | corpus bc011 |
| ab | `{A,B,a,b}` | 4 | cube, 2 free bits | `((c − 'A') & 0xDE) == 0` | corpus bc019 |
| sp | `\s` | 6 | nibble-unique | `T[c & 15] == c` (one shuffle) | corpus bc016 |
| dm | `[\d-]` | 11 | nibble-unique | `T[c & 15] == c` | corpus bc012 |
| w | `\w` | 63 | general | `(c\|0x20) − 'a' <= 25 \| c − '0' <= 9 \| c == '_'` | corpus bc000 |

The generic kernel (`nib2`) is the two-table nibble lookup
`lo[c & 15] & hi[c >> 4] != 0` with tables read from a descriptor (shufti;
exact for every set here, each high-nibble row taking at most 8 distinct
patterns). It needs a byte shuffle: NEON `tbl`, SSSE3/AVX2 `pshufb`.

### 2.2 Results (gcc-16, NEON; ns per find-all over the span)

TABLES_TA

clang-21 gives the same picture within ~200 ns at 64 KiB
(`probes/out/twins/ta.clang.txt`); its `\h` row is the one exception, with
the shape form ~300 ns ahead of the nibble lookup where gcc ties them.

### 2.3 What the tables say

- **Miss / sparse, 4 KiB and up.** The tailored classifier is ahead for
  every shape except eq3 (tie) and `\w` (behind). The order is by
  instruction count per block: range and one-bit cube are two operations
  (sub+cmp, and+cmp); eq2, a two-bit cube and nib1 are three; nib2 is four
  plus a shift; eq3 is five; `\w`'s three-range form is seven. The
  generic kernel's cost is flat across sets (~2,100 ns per 64 KiB), which is
  its point.
- **Short spans (16-64 B)**: NULL. Every vector form is 2.0-2.8 ns; the
  scalar loop is 7 ns at 16 B and 23 ns at 64 B.
- **Dense**: the find-first restart costs ~7.5 ns a hit in every vector
  form against ~5.2 ns in the scalar loop, so the scalar loop WINS, and the
  classifier rows are within ~3,000 ns of each other at 64 KiB. The `iter`
  rows (the same classifier, one pass, the mask's bits consumed in place)
  are the control: see the `iter` rows of the dense and real tables.
- **Real text** follows each class's own density: `[0-9]`/`[\d-]`/`{A,B,a,b}`
  are moderately dense in the syntax text (4,500-5,100 members per 64 KiB)
  and behave like `dense`; `["']` and `{S,s}` are sparse (390 and 1,729)
  and keep the miss ordering; `\s`, `\h` and `\w` are dense and every
  find-first form loses to the scalar loop.
- **libc** (one `memchr` per member, fresh each call) is behind every
  inline form at every span and density, and on `real` `\h` (9,765 hits)
  it reaches 7.2 ms per 64 KiB: each hit restarts all three streams, the
  rare one (`0xA0`, absent) rescanning to the end every time.

### 2.4 Verdict T-A

**Worth it where the scan rejects, and only there; NOT worth it as the
answer to dense classes; Linux decides x86.** The shape menu that earns its
place on NEON is: range, cube (absolute or offset), eq2, nib1, with nib2 as
the general fallback (and the right choice for `\w`). eq3 is no better than
nib2. On x86 the menu is the only vector form at the SSE2 baseline, so its
existence there is not an optimization question; whether `pshufb`'s nib2 is
as cheap relative to the shape forms as `tbl` is on M1 is what the Linux
run measures. For dense classes the measured lever is the iterate-in-place
API, not the classifier.

---

## 3. T-B: fused scan+verify vs the emitted run gate

### 3.1 The cells and the variants

Every variant computes the emitted gate's function exactly: the first
`c >= pos` with `c + L <= n` and `(s[c+j] & 0xDF) == V[j]` for all `j < L`,
else `n`.

| cell | pattern (bench) | run | emitted scan | ffl's second byte |
|---|---|---|---|---|
| us | `(?i)union.*?select.*?from` (capability) | `SELECT` | `C`/`c` at offset 4 | `T` at 5 |
| up | `(?:username\|USERNAME\|user\|USER)…` (capability) | `USER` | `U`/`u` at 0 | `R` at 3 |
| mi | `(?i)cat` (syntax) | `CAT` | `C`/`c` at 0 | `T` at 2 |

- `emit`: the emitted `rx_reqrun`, copied verbatim from pcrec main 8a41efd2's
  `-p rx` artifact (two `memchr` streams, each re-searched only when passed,
  both fresh on every call; overlapping `rx_w2`/`rx_w4` masked compares).
- `m2v`: one inline two-case vector pass for the scan byte (T-A's eq2
  kernel), then the same masked compare, restarting one past a failed
  candidate.
- `ffl`: FUSED. Per block, the scan byte's masked compare AND the second
  byte's, candidates verified from the mask bits with the masked word
  compare, 2×VW unrolled, the final block overlapped with its done lanes
  masked off.
- `fall`: FUSED, all L offsets' masked compares ANDed; a set bit IS the
  answer.

Regimes: `gate` = one call from 0 (what `rx_search` pays per call);
`sweep` = call, restart at hit + 1, to the end (every candidate the gate
would hand on: litscan_k82b.md's T3 use, and the find-all regime cause B
lives in); `short` = one call on each of the 75 capability short subjects.

### 3.2 Results (gcc-16 NEON; ns)

| cell | variant | gate t-64k | gate t-1m | sweep t-64k (hits) | sweep t-1m (hits) | short, per subject |
|---|---|---|---|---|---|---|
| union-select (cap) | emit | 16,829 | 478,402 | 17,616 (0) | 464,200 (0) | 5.66 |
| union-select (cap) | m2v | 13,397 | 397,579 | 13,349 (0) | 396,816 (0) | 4.43 |
| union-select (cap) | ffl | 2,408 | 38,964 | 2,420 (0) | 38,853 (0) | 3.66 |
| union-select (cap) | fall | 10,202 | 163,586 | 10,051 (0) | 163,228 (0) | 7.25 |
| userpass (cap) | emit | 32.5 | 47.2 | 27,912 (212) | 718,476 (3290) | 5.47 |
| userpass (cap) | m2v | 8.6 | 19.3 | 18,365 (212) | 498,477 (3290) | 4.33 |
| userpass (cap) | ffl | 5.1 | 4.1 | 3,907 (212) | 84,974 (3290) | 3.61 |
| userpass (cap) | fall | 15.3 | 11.8 | 9,792 (212) | 172,094 (3290) | 4.82 |
| mod-i (syn) | emit | 54.2 | 91.4 | 40,594 (400) | 865,757 (6030) | 6.77 |
| mod-i (syn) | m2v | 17.0 | 44.5 | 21,151 (400) | 557,045 (6030) | 5.55 |
| mod-i (syn) | ffl | 4.4 | 15.9 | 5,331 (400) | 137,243 (6030) | 3.62 |
| mod-i (syn) | fall | 5.3 | 21.8 | 6,721 (400) | 148,921 (6030) | 3.76 |

clang-21 (`probes/out/twins/tb.clang.txt`): `emit` 18,169 / `ffl` 2,538 on
the union-select gate, 31,609 / 4,212 on the userpass sweep, 40,343 / 5,688
on the mod-i sweep, short subjects 6.4-7.4 / 3.5-3.8 ns. One noisy cell:
`ffl`'s union-select t-1m gate reads 66,031 ns with a +63% spread, against
39,978 for the identical call in the sweep column. Its `fall` is ~3,400 ns
faster than gcc's on union-select 64 KiB and still behind `ffl`.

### 3.3 What the tables say

- **The emitted gate's cost is its stops, not its scan.** union-select's
  run never occurs in the capability text, but `c`/`C` does, 1,431 times
  per 64 KiB. `emit` pays ~14,400 ns above `ffl` for them: ~10 ns a stop,
  which is k82cost's measured `s` (7.5 ns Mac). `m2v`, one inline pass
  instead of two `memchr` streams, saves only ~3,400 ns of that, because it
  still stops on every `c`. Filtering on the PAIR `C`@4 + `T`@5 leaves 0
  candidates (`ct` does not occur in that text), and `ffl` runs at
  ~0.036 ns/B, ~1.8x the cost of ONE `memchr` stream (0.020 ns/B,
  k82cost's `β`).
- **userpass**: a single gate call from 0 is 32.5 ns (`emit`) against
  5.1 ns (`ffl`); the gate passes at offset 113. Over the sweep (212 hits),
  27,912 against 3,907 ns.
- **mod-i**: 400 runs per 64 KiB. Its emitted sweep is 40,594 ns
  (0.62 ns/B, as much as the DFA it guards) and `ffl` is 5,331 ns.
  k82diag counted the gate's `memchr`s reading 4.8x the subject per
  find-all; the fused gate reads it once.
- **Short subjects**: 5.5-6.8 ns (`emit`) against 3.6-3.7 ns (`ffl`) per
  subject, 2-3 ns absolute, above the Mac spread (~0.1-0.3 ns) but a
  ns-scale figure, so
  D144 addendum 1 sends it to the Linux loop before it counts.
- **`fall` loses to `ffl` everywhere** (union-select 64 KiB: 10,202 against
  2,408 ns): L loads per block cost more than the rare verify. Two filter
  bytes is the fused design; more is not better.

### 3.4 Verdict T-B

**Worth it.** A fused pair-filter gate removes the per-candidate stop that
makes today's pair arm cost ~10 ns per scan-byte occurrence, and it is the
kernel `requirements.md` F9 (anchored find_literal with a caller-named
anchor) and survey.md's packed-pair recommendation describe. It composes
with, and does not replace, litscan_k82b.md's handoff (T3): the handoff
removes the second scan, this shrinks the first. The choice of the second
byte (here: the run's last, or first) is the ranker's (survey.md: Rust
`memchr`'s replaceable byte ranker, fed by pcrec's frequency prior). Linux
measures it against glibc's AVX2 `memchr`, whose per-call term is ~3.4 ns
there against ~0.3-1 ns here (requirements.md §2.4), which should widen the
gap rather than narrow it.

---

## 4. T-C: constant-descriptor specialization

### 4.1 Disassembly (`tc_asm.sh`)

One header kernel, `mf_find(s, n, d)`: `FIND_BODY` with a classifier that
switches on `d->kind` (eq2, range, absolute cube, offset cube, nib1, nib2)
and reads the constants and tables from `d`. `desc_X` calls it with
`&D_X`, a `static const struct mf_set`; `hand_X` is shapes.h's hand kernel;
`mut_X` is the control, a writable EXTERNAL `struct mf_set` (another TU may
write it). Each is `noinline`, so each is one symbol. "diff" counts
differing lines in order; "bag" counts differing lines of the instruction
multiset after renaming registers and branch targets (0 = the same
instructions, allocated or scheduled differently).

| set | compiler | hand insns | desc insns | desc diff | desc bag | mut insns | mut bag |
|---|---|---|---|---|---|---|---|
| q2 | gcc-16 | 107 | 112 | 47 | 13 | 321 | 228 |
| d | gcc-16 | 101 | 103 | 30 | 2 | 321 | 246 |
| ss | gcc-16 | 103 | 103 | 28 | 0 | 321 | 228 |
| ab | gcc-16 | 107 | 107 | 30 | 0 | 324 | 243 |
| sp | gcc-16 | 112 | 113 | 73 | 3 | 320 | 220 |
| w | gcc-16 | 135 | 135 | 88 | 10 | 321 | 216 |
| q2 | clang-21 | 106 | 106 | 0 | 0 | 330 | 230 |
| d | clang-21 | 99 | 99 | 4 | 4 | 330 | 263 |
| ss | clang-21 | 99 | 99 | 0 | 0 | 330 | 237 |
| ab | clang-21 | 106 | 106 | 0 | 0 | 330 | 244 |
| sp | clang-21 | 108 | 109 | 27 | 3 | 330 | 226 |
| w | clang-21 | 131 | 130 | 41 | 9 | 330 | 209 |

- **clang**: `desc` is `hand` instruction for instruction on q2/ss/ab
  (in-order diff 0) and the same multiset on d up to the bound check's
  spelling (`sub #0x30; cmp #0xa` against `sub #0x3a; cmn #0xb`, the same
  test). The residual on sp and w (3 and 9 multiset lines) is the scalar
  `n < 16` byte loop reading `T[c & 15]` through the struct offset; the
  vector loop is identical.
- **gcc**: the vector loop is the same instructions with a different
  register allocation and schedule (in-order diff 28-88 lines, multiset
  0-13); the residual multiset lines are the same byte-loop spelling, and on
  q2 a branchy two-compare byte loop where the hand kernel got a `ccmp`.
- **The control does not fold**: `mut` is ~320-330 instructions under both
  compilers, the six-way switch kept inside the kernel. (A `static`
  writable descriptor that nothing writes is NOT a control: clang proves it
  constant and folds it anyway, which the first version of this twin
  measured before the control was made external.)

### 4.2 Timing (ns per call, miss: the whole span read)

| set | form | gcc 16 B | gcc 256 B | gcc 4 KiB | gcc 64 KiB | clang 16 B | clang 256 B | clang 4 KiB | clang 64 KiB |
|---|---|---|---|---|---|---|---|---|---|
| q2 | hand | 3.03 | 6.58 | 91.20 | 1447.35 | 2.30 | 6.46 | 88.68 | 1444.74 |
| q2 | desc | 2.63 | 6.59 | 91.15 | 1438.24 | 2.30 | 6.50 | 90.89 | 1439.90 |
| q2 | mut | 3.27 | 8.44 | 93.46 | 1479.91 | 3.26 | 9.51 | 138.00 | 2102.96 |
| q2 | hoist | 4.27 | 7.27 | 91.15 | 1444.51 | 2.63 | 7.12 | 88.80 | 1394.60 |
| q2 | rt | 3.96 | 8.87 | 107.28 | 1695.33 | 3.52 | 10.25 | 145.56 | 2217.87 |
| d | hand | 2.60 | 5.62 | 73.83 | 1097.13 | 2.33 | 6.56 | 69.21 | 1095.63 |
| d | desc | 2.62 | 5.61 | 69.71 | 1094.59 | 2.29 | 6.50 | 69.36 | 1100.24 |
| d | mut | 3.96 | 7.55 | 82.76 | 1230.36 | 2.96 | 8.57 | 113.60 | 1805.27 |
| d | hoist | 3.24 | 6.30 | 70.48 | 1095.21 | 2.63 | 6.99 | 70.45 | 1102.22 |
| d | rt | 4.29 | 10.18 | 96.81 | 1442.80 | 3.61 | 9.51 | 124.74 | 1975.17 |
| ss | hand | 2.62 | 5.53 | 69.20 | 1095.29 | 2.28 | 6.56 | 69.15 | 1082.46 |
| ss | desc | 2.62 | 5.58 | 69.23 | 1098.64 | 2.31 | 6.62 | 68.47 | 1089.24 |
| ss | mut | 3.92 | 7.55 | 91.39 | 1350.43 | 3.29 | 8.47 | 118.69 | 1806.74 |
| ss | hoist | 3.29 | 6.28 | 70.18 | 1086.16 | 2.81 | 7.03 | 70.47 | 1095.82 |
| ss | rt | 4.26 | 10.07 | 99.80 | 1530.99 | 3.62 | 9.53 | 129.63 | 1964.97 |
| ab | hand | 2.55 | 6.80 | 88.74 | 1439.07 | 2.28 | 6.50 | 89.67 | 1446.21 |
| ab | desc | 2.61 | 6.73 | 88.67 | 1397.87 | 2.29 | 6.45 | 90.11 | 1431.71 |
| ab | mut | 3.53 | 7.37 | 94.76 | 1390.39 | 3.29 | 9.53 | 137.49 | 2124.03 |
| ab | hoist | 3.21 | 7.63 | 92.00 | 1435.77 | 2.96 | 7.69 | 90.29 | 1403.64 |
| ab | rt | 4.00 | 8.27 | 108.44 | 1625.44 | 3.84 | 10.59 | 146.23 | 2232.26 |
| sp | hand | 2.64 | 6.93 | 91.57 | 1444.82 | 2.24 | 6.81 | 88.07 | 1414.59 |
| sp | desc | 2.64 | 6.95 | 91.37 | 1445.89 | 2.29 | 6.90 | 90.79 | 1432.24 |
| sp | mut | 3.63 | 8.60 | 97.37 | 1448.93 | 3.30 | 9.42 | 134.59 | 2102.20 |
| sp | hoist | 3.64 | 7.65 | 92.16 | 1445.52 | 3.80 | 8.29 | 90.24 | 1450.74 |
| sp | rt | 4.02 | 10.22 | 101.19 | 1504.57 | 3.60 | 9.80 | 137.74 | 2109.66 |
| w | hand | 2.97 | 9.57 | 133.15 | 2115.46 | 2.30 | 9.59 | 138.18 | 2188.25 |
| w | desc | 2.97 | 9.57 | 133.56 | 2121.35 | 2.31 | 9.58 | 137.47 | 2197.66 |
| w | mut | 4.29 | 9.89 | 134.17 | 2139.57 | 3.59 | 12.15 | 180.92 | 2763.41 |
| w | hoist | 3.36 | 9.98 | 134.22 | 2153.04 | 3.73 | 10.51 | 137.12 | 2205.40 |
| w | rt | 4.70 | 10.34 | 136.32 | 2179.19 | 3.94 | 12.52 | 179.75 | 2779.72 |

`hoist` is the run-time library form: the descriptor at run time, the shape
switch hoisted once per call to a per-shape loop. `rt` is one function for
every set with the switch left inside the classifier.

### 4.3 Verdict T-C

**Worth it (and it is the enabling result).** The emitter does not need to
write per-pattern kernel TEXT to get per-pattern kernel CODE: one shared
header kernel plus a `static const` descriptor per site compiles to the
hand kernel under gcc-16 and clang at `-O2`, at the hand kernel's speed.
The rule the emitter must keep: the descriptor is `static const` (or
otherwise provably constant at the call); a writable external one silently
becomes the generic kernel. A run-time library entry with the switch
hoisted (`hoist`) is the right shape for a non-injected (B1/B2) binding: it
equals the hand kernel from 4 KiB and costs +0.3-1.6 ns per call at
16-256 B (a per-call figure for the Linux loop to confirm, D144 add. 1).
Linux confirms the identity on x86 (`tc_asm.*` per build in the run).

---

## 5. The Linux queue

`probes/twins/twins_run.sh` is appended to `probes/linux_run.sh` (one call;
memfnisa's script is otherwise unchanged). Its last log line is
`MEMFN-TWINS-RUN COMPLETE <dir> fails=<n>`, written after linux_run.sh's own
trailer. It needs the pcrec-bench checkout beside the pcrec one (`BENCH=`
overrides) to materialize the subjects.

| item | builds | decides |
|---|---|---|
| `--check` + ASan+UBSan, every twin | gcc, clang × `-march=x86-64` (SSE2), `+-mssse3`, `x86-64-v3` (AVX2); clang ASan at v3 | correctness on real x86 hardware (Rosetta 2 already clean) |
| T-A timing | gcc × SSE2/SSSE3/AVX2, clang × SSSE3/AVX2 | the x86 shape-vs-nib2 deltas; whether `pshufb`'s cost changes the ranking; the SSE2 menu's absolute cost; AVX2's 32-B blocks against the restart cost on dense text |
| T-B timing | all six | `ffl` against the emitted gate with glibc's AVX2 `memchr` (per-call ~3.4 ns, per-stop ~8 ns on that box: k82diag §2, litscan_k82b.md §1.3); the short-subject delta on a pinned loop (the D144 addendum 1 bar) |
| T-C timing + `tc_asm` | all six | code identity of descriptor vs hand on x86 under gcc and clang |

Expected wall time about 50 minutes; the manager schedules it (one heavy
suite at a time; the bench's window).

---

## 6. What this does not settle

- **Absolute x86 numbers.** Everything here is NEON on an M1; the brief's
  x86 variants compile and check (Rosetta) but are not timed.
- **The emitted-gate context.** T-B times the gate alone. The whole-search
  effect on a bench cell also depends on what follows the gate (the DFA's
  own scan, cause B's discard); the handoff twin T3 (litscan_k82b.md) and an
  alpha are where that is read.
- **F5 (skip_in_set).** T-A is find-first. The dense result suggests the
  in-loop skip (a run's end) wants the iterate form or a run-extension
  kernel (studies/simd1 §15), not a find-first; not measured here.
- **Code size.** T-C shows the descriptor form costs nothing at run time; the
  shared header's size per artifact (one copy of each used shape's loop) is
  `[OPT-DIAL]`'s term and not measured.
- **The ranker.** T-B's second byte is the run's last (or first) byte, not a
  frequency-ranked one; a ranked pair can only be as good or better on these
  cells (it already reaches zero candidates on union-select).

## 7. Files

- `probes/twins/` — the twins (`vec.h`, `shapes.h`, `ta_set.c`, `tb_run.c`,
  `tc_desc.c`), `tc_asm.sh`, `subjects.py`, `twins_run.sh`,
  `twins_tables.py`; see its CLAUDE.md. `probes/probes.mk` gains
  `twins-check`, `twins-check-asan`, `twins-check-x86`, `twins-asm`,
  `twins-run`.
- `probes/out/twins/` — the Mac run of `twins_run.sh` verbatim (`run.log`,
  `ta.*`, `tb.*`, `tc.*`, `tc_asm.*`) and `check.rosetta.txt`.
