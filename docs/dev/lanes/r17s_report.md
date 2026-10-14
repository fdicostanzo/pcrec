# r17s — R-17 scoping and twin design (small / one-cube / one-range FIND sets)

Lane r17s, 2026-10-11, for the memfn kit manager. Branch `lane/r17s`, cut from
`lane/memfn-r17` at `4aa14637` (pcrec code = main `fdc2f2af`, abi 75, with
`[REQ-HANDOFF-L1]` merged). Read-only on `src/`, `memfn/` and pcrec-bench (bench
checkout at `d359564f`, the commit the loss-review lanes regenerated subjects from).
The box was held by kit slot23: **no timing was taken.** Every count here is from
emitted C or from a compile. Every twin is answer-checked only.

Instruments and twins: `docs/design/memfn/probes/r17/` (own CLAUDE.md).

## 0. Answers first

1. **No new pcrec fact is needed to render any R-17 shape with SIMD off.** Every
   PF/VM-hat FIND already carries the whole set in `mf_term.set` (pcrec's
   `find_site`, `src/gen/emit_dfa.c`). Integration rule 7 says a row may ignore
   `table_ref`. Two things keep today's rows from taking these shapes. The memchr
   rows require `table_ref == 0` and `empty == EXCLUDED`. The only other PF row is
   `pf_walk`, so a set of 2 or more falls to it whatever its shape. That is **kit
   row work**. The VM hat's |S| = 1 (C2) is the same: pcrec passes a one-member
   SET through `start_set` with an empty range of NOP, and `pf_memchr_applies`
   declines it on both counts.
2. **pcrec owes two things (§5).** (N1) The density facts R-17 already promises.
   A |S| = 1 memchr form at the VM hat is exactly the form Q-R5 measured at x0.6
   on a dense set, so a row serving it must decline on density. Until then the
   VM hat's robust candidate is the inline SWAR form, not memchr. (N2) A
   file-scope sink at the PF/MLINE door, needed only for the SIMD layer. D155
   forbids `#if` inside a function that does work, and the door passes
   `file_scope = NULL` today (`pcrec_memfn_emit`). Two pcrec-side findings go to
   main as information, not requests (§5, F-1/F-2).
3. **Population** (emitted C, every distinct corpus pattern, default stream).
   Of 772 DFA-prefilter walks:
   - pairs: 236 (49 one-cube, 93 adjacent, 94 other);
   - one range of more than 2 bytes: 135; one cube of more than 2 bytes: 4;
   - 3-8 members: 73;
   - total reachable by "at most 4 cube terms": 420; by "at most 2 ranges": 522.

   The DFA hat has 39 walks, 37 of them within 4 cubes. The VM hat has 225: 97 at
   |S| = 1 and 56 pairs. Under `--engine=vm`: 1,571 at |S| = 1 and 2,472 of 2,974
   within 4 cubes. The bench (367 patterns) has 102 DFA-prefilter walks (the
   losing cells plus 22 `[0-9]` and 12 `[a-z]` sites) and 17 VM-hat walks.
   **OFS/PRE never scans a multi-member SET**: 0 of 757 offset-skip/pre-check
   bodies lack a memchr. pcrec's `prefix_k.c` rule (b) admits only a single-byte
   scan offset past 0. R-17's "the OFS BODY and PRE sites present the same FIND
   description" therefore has population 0 today (§1.4).
4. **The cells (§2).** Of the 3.85 ms set-skip loss, `ci-strasse` (0.55 ms) no
   longer renders a set walk at this tip: `[REQ-HANDOFF-L1]` made its prefilter
   `handoff`, so it needs a bench re-measure. `alt-distinct-lead` (2.40 ms, the
   biggest cell) is a 3-member set `{63,D0,E6}`, not a pair, cube or range. Its
   skip is only 43% of its time; the rest is 635 DFA steps per match against
   rust's Teddy, so a free scan still leaves at least 1.2 ms lost. Its set is
   three one-byte cubes, which is the case for a general row over terms rather
   than one row per shape.
5. **Leaning (§3.4): ONE general row family in `pffind.c`.** The kit analyses the
   set into at most K TERMS (eq / cube / range), and a first-match form table
   picks the rendering:
   1. `memchr` for one term of one byte (`pf_memchr`, widened to NOP and to a
      present `table_ref`);
   2. the SWAR term-OR loop for at most K terms (SIMD-off), plus per-level helpers
      (SIMD-on, behind N2);
   3. today's walk otherwise.

   The same term renderer is the kernel an ofsskip `fn_rows[]` BODY row or an
   in-loop exit-set skip would reuse (D122). K is set by step 2's timing,
   labelled `UNMEASURED DEFAULT` until then (D149).
6. **Twins (§4): 65 functions, 14 cells.** The forms are `table`, `memchr`,
   `mc2`/`mc3` (a bounded memchr cascade), `swar`, `sse2` and `avx2`. The cells
   are 10 losing cells, 2 alternative spellings and 2 dense controls.
   - Exhaustive check: **1,874,741,290 calls, 0 mismatches**. That covers all 256
     bytes at every position and lane phase, near-members, n 0..80, every lo,
     hi = n and n - 1, and guard pages on both sides.
   - Planted reference: caught in **14 of 14** cells.
   - ASan+UBSan at n <= 40: 300,215,353 calls, 0 mismatches.
   - The timing harness is written and dry-run (169 pinned invocations), but
     **NOT RUN**.

## 1. Sites, descriptions, rows (question 1)

### 1.1 The one site shape

Every R-17 site is `pcrec_emit_find` → `find_site` → `pcrec_memfn_emit` under
DELEG_SITES row PF, MLINE being the `(?m)^` memchr only. The description is:

| field | DFA prefilter `byte-class[-bounded]` | DFA hat `first-*-bounded` | VM hat seek (entry + retry) |
|---|---|---|---|
| form/op/handoff | STMT / FIND / ASSIGN | same | same |
| term | one REQUIRED SET at offset 0, `set` = the whole set | same | same |
| `table_ref` | `can_begin_match` (1) | `start_bytes` (2) | `start_set` (3), even at \|S\| = 1 |
| `empty` | NOP (the walk tests its own range) | NOP | NOP |
| `end_back` | 0, or 1 bounded (miss `n - 1`) | 1 (the hat is bounded-only) | 0 |
| `on_miss` / leaves | none / 0 | none / 0 | none / 0 (the caller tests `attempt_position >= subject_length` after) |
| `result` | `lo` (in place) | `lo` | `lo` |
| row today | `pf_walk` / `pf_walk_bounded` | `pf_walk_bounded` | `pf_walk` |
| density | `cand_ppm_*` / `ppm_*` unknown | unknown | unknown |

`|S| = 1` at the DFA prefilter is a different description: pcrec's `memchr` row
passes a byte, no table and EXCLUDED, and `pf_memchr` takes it. That is 1,009
corpus sites, which R-17 does not touch.

### 1.2 Why the existing rows do not take the shapes

- **`pf_memchr` / `pf_memchr_bounded`** (`memchr_shape`) require
  `table_ref == 0`, `empty == MF_EMPTY_EXCLUDED` and |S| = 1. The VM hat's
  one-member `start_set` fails the first two. It is a ROW APPLICABILITY limit, not
  a missing fact: the set bits are there, and rule 7 lets a row ignore the table.
  What the memchr row's text lacks for a NOP site is its own `lo < hi` guard,
  because pcrec's text proves the range non-empty only at the EXCLUDED sites.
- **`pf_walk[_bounded]`** takes any set pcrec names by table. It is the only row
  for |S| >= 2, whatever its shape.
- **`fn-pair` / `fn-memchr`** (ofsskip.c `fn_rows[]`) are BODY rows of the
  offset-skip FUNC. That site's scanned term is a one-byte SET or a RUN position
  (exact, or a two-member cube at `plan_pos`). They are unreachable from a PF
  STMT site, and `fn-pair`'s leapfrog keeps `ha`/`hb` across loop iterations
  INSIDE its function. A PF statement is re-entered by the engine per hit, so a
  copy of that leapfrog there is K101's restart (`fresh = 1` every call). The
  stateless equivalent is the bounded cascade `mcK` (§3.1).
- **`pf_memchr_back`**: the `(?m)^` newline only.
- **The generic row** never serves PF in the corpus (C17/N2's zero would-decline).

So: **PF / DFA hat |S| = 2, cube, range → kit row work, no pcrec fact.**
**VM hat |S| = 1 → kit row work, plus N1 to hold the dense regime.**

### 1.3 Population (`census.py`, `summarize.py`; `out/summary_*.md`)

Corpus (4,542 distinct patterns, 755 of 9,084 compiles refused; one row per site,
so the hat's entry and retry count once):

| stream | role | sites | bounded | \|S\|=1 | pair cube | pair adjacent | pair other | 3-8: ≤2 cubes | 3-8: 3 cubes | 3-8: 4+ | range >2 | cube >2 | wide (>8) | ≤4 cubes | ≤2 ranges |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| default | dfa-pf | 772 | 210 | 0 | 49 | 93 | 94 | 7 | 32 | 34 | 135 | 4 | 324 | 420 | 522 |
| default | dfa-hat | 39 | 39 | 0 | 13 | 6 | 12 | 2 | 1 | 0 | 2 | 0 | 3 | 37 | 37 |
| default | vm-hat | 225 | 0 | 97 | 12 | 21 | 23 | 1 | 3 | 0 | 5 | 2 | 61 | 159 | 167 |
| vm | vm-hat | 2,974 | 0 | 1,571 | 157 | 246 | 176 | 42 | 47 | 45 | 217 | 6 | 467 | 2,472 | 2,626 |

Bench (367 patterns, as the pcrec-auto testee compiles them): dfa-pf 102 (pair
cube 7, pair adjacent 2, range 36, cube 3, 3-8 members 12, wide 42), dfa-hat 16,
vm-hat 17 (|S| = 1: 8, pair 1). The 36 bench ranges are `[0-9]` ×22 and `[a-z]`
×12 plus two others. None of them is a losing cell, and a range row reaches all
of them, so they are the DENSE CONTROL (§4.3).

### 1.4 OFS BODY / PRE

The census counts 757 offset-skip and pre-check `__body` helpers (default stream)
and 511 (VM stream). It finds 0 without a memchr. pcrec never presents a
multi-member scanned SET there. In `prefix_k.c`, rule (b) at `si = 1` admits only
a singleton scan offset past 0, and the offset-0 baseline is priced
`C_BITMAP = 116` against `C_MEMCHR = 6` (the table walk's cost). The 2-member
cube case reaches OFS only as a RUN position, which `fn-pair` serves. So "the
same FIND description at OFS/PRE" is a socket with no population. It becomes
live only if pcrec re-prices once a kit set row exists (F-1, §5).

## 2. The named cells (question 2)

The loss is the bench's own (phase-1 tables). The site, set and shape are from
this tip's emitted C (`build/scratch/r17/cells/*`, compiled as the bench's
testee).

| cause / cell | lost (ms), peer | site at this tip | S | shape | twin cell | is the loss the scan form? |
|---|---|---|---|---|---|---|
| set-skip `utf8/alt-distinct-lead` | 2.398, rust ×7.35 | dfa-pf byte-class | {63,D0,E6} | 3 members, 3 one-byte cubes (not pair/cube/range) | `adl` | **PARTLY.** Skip 43%, steps 57% (405k DFA steps, 635 per match; rust runs Teddy). A free scan still leaves ≥ ~1.2 ms. |
| set-skip `utf8/ci-strasse` | 0.551, rust ×2.37 | **prefilter `handoff`** (no set walk at this tip) | — | — | — | **NOT AT THIS TIP.** Its second scalar pass went with `[REQ-HANDOFF-L1]`. Re-measure on the bench. |
| set-skip `utf8/ci-sigma` | 0.406, rust ×3.43 | dfa-pf | {CE,CF} | one cube (pair) | `sig` | yes (skip 100%) |
| set-skip `utf8/ci-kelvin` | 0.345, rust ×1.95 | dfa-pf | {4B,6B,E2} | cube {4B,6B} + byte E2 | `kel` | yes (skip 94%) |
| set-skip `utf8/ci-turkish-i` | 0.149, rust ×1.13 | dfa-pf | {49,69} | one cube (pair) | `tki` | mostly (skip 66%; 41,538 matches, so the per-call cost matters) |
| PAIR-SKIP `syntax/alt-nested` | 0.756, jit ×1.63 | dfa-pf | {63,64} | pair, adjacent (a 2-range), not a cube | `alt2`, `alt2r` | yes (skip 0.906 of 1.076 loads/B; a hit every ~14 B) |
| PAIR-SKIP `syntax/alt-two` | 0.607, jit ×1.52 | dfa-pf | {63,64} | same | same | same |
| RANGE-SKIP `capability/high-byte-run` | 0.257, jit ×1.19 | dfa-pf | 80..FF | one range = one cube | `hbr`, `hbrc` | yes (1.000 loads/B, 0 matches) |
| RANGE-SKIP `capability/utf8-lead-no-cont` | 0.186, jit ×1.13 | dfa-pf **bounded** | C2..DF | one range (4 cubes) | `u8l` | yes (pure miss scan) |
| C2 `capability/quoted-delim-match` | 1.643, jit ×3.79 | vm-hat | {22,27} | pair, not a cube, not adjacent | `qdm` | yes (4.64M seek iterations, 44k attempts) |
| C2 `syntax/bak-k-named` | 0.528, jit ×2.14 | vm-hat | {3C} | \|S\| = 1 | `bkn` | mostly (1.48M seek iterations; 6,968 attempts; 16k pre-check memchr) |
| C2 `capability/balanced-parens-rec` | 0.412, jit ×1.53 | vm-hat | {28} | \|S\| = 1 | `bpr` | **PARTLY.** 1.32M seek iterations, plus 23,583 recursion frames that no scan form touches. |

Not R-17 at this tip: `ci-moskva` (0.82 ms) renders memchr `D0`. Its cure is
prefix_k re-pricing toward the offset-1 cube `{9C,BC}` (F-1). Ranked by ms, the
twinned cells cover 7.83 of the 7.98 ms named (everything except ci-strasse's
0.55 and the parts of adl/bpr that are not the scan).

## 3. Candidate forms (question 3)

### 3.1 SIMD-off (portable C; Q50: SWAR and libc are scalar layer)

| shape | form | over-read / guard argument | reuses |
|---|---|---|---|
| \|S\| = 1 | `memchr(s+lo, b, hi-lo)`, store hit or `hi` | No subject read by our text. On a NOP site the text needs its own `lo < hi` guard: lo may equal n, and s may be NULL at n = 0 (K27). | `pf_memchr`'s text (the bounded row's store shape, plus a guard) |
| \|S\| = 1 | SWAR eq: `haszero(w ^ b*0x01..)` | Loads only while `i + 8 <= hi`, then a byte tail. No call, so it is the candidate for a DENSE VM-hat set. | new (T2/T6/`hiskip` twin precedent) |
| pair / ≤3 members | bounded cascade `mcK`: `h = memchr(m1,[lo,hi))`, then each next member over `[lo,h)` | Exact (the least hit), stateless across calls (unlike `fn-pair`, so no K101), each byte read at most K times, K libc calls per find. Wins only where hits are sparse. | `pf_memchr`'s call; K101's bounded fix shape |
| pair | SWAR 2×eq OR'd | as SWAR eq | new |
| one cube | SWAR `haszero((w & M) ^ V)`: ONE term for {s,S}, {a,c}, {A,B,a,b}, 80..FF | as SWAR eq | new; the cube fact is the kit's own (it links nothing from `src/`; `pcrec_cube_of`'s idea, re-derived) |
| one range | SWAR exact-lane: `d = w -lane L` (no cross-lane borrow), in iff `d < W` | Per-lane exact, no carries. W ≤ 128 written; a wider range is its complement's narrow modular range. | new |
| few cubes / ranges | OR of the terms above (alt-distinct-lead: 3 eq; ci-kelvin: cube + eq) | `haszero` flags false lanes only ABOVE a true lane of the same term, so the lowest flag of the OR is the least hit (checked exhaustively) | the general row (§3.4) |

### 3.2 SIMD-on (vrun.c's shape; x86 levels sse2 = v1, avx2 = v3)

- eq: `cmpeq(v, b)`.
- cube: `cmpeq(and(v, M), V)`, which is AND+EQ.
- range: `cmpeq(min_epu8(v - L, H - L), v - L)`, the saturating-compare form.
- pair or few terms: the term masks OR'd, then movemask and ctz.

Blocks ascend while `i + W <= hi`. When `hi - lo >= W`, ONE overlapped final
block ends at `hi`, with lanes below `i` masked off. Otherwise the next narrower
level runs (avx2 → sse2 → SWAR tail). **Every load lies inside `[lo, hi)`**, so
there is no over-read and no page argument (the guard pages prove it). This is
vrun.c's block loop and final block with a different lane test. Per the floor rule
and D155, the SIMD rendering is the SIMD-off rendering plus guarded helpers and a
selector. At a PF STMT site those helpers need N2.

### 3.3 Glibc-inside caveat

`memchr` and `mcK` are SIMD-off forms whose libc body is SIMD (runtime-dispatched
AVX2 in glibc). That is the `[r9fu]` trap: a "SIMD-off" `mc2` may beat SWAR on
sparse sets for exactly that reason. It is still scalar layer (Q50). Step 2
compares SWAR against mcK at each density, and the SIMD rows against the best
SIMD-off row, not against `table` (D147).

### 3.4 One general row (D122), with the standing lenses

**General vs specific.** One row per shape (pair row, cube row, range row,
VM-hat byte row) is four renderers. Three of them would be the same loop with a
different lane test, and none of them would serve the biggest cell
(`alt-distinct-lead`, three one-byte cubes) or `ci-kelvin` (cube + byte). The
general form is a SET FIND over a TERM LIST. The kit derives a minimal list of at
most K terms from `term.set` (eq / cube / range), and the shapes R-17 names are
its K = 1..2 cases. The census sizes it: "at most 4 cube terms" reaches 420 of 772
DFA-prefilter walks and 2,472 of 2,974 VM-stream hat walks, while the pairs and
single cubes alone reach 240.

**Core vs derived.** The core is the term list, a kit-internal analysis of
`set[32]`. Forms are derived from it by a first-match table inside `pffind.c`:

| # | predicate | form (SIMD-off) | SIMD-on | deny |
|---|---|---|---|---|
| 1 | one eq term (\|S\| = 1), any `table_ref`, empty EXCLUDED **or NOP**; and not dense, where density is stated (N1); at the VM hat until N1, measured | `memchr` (+ a `lo < hi` guard on NOP) | none (glibc is inside) | `no-pf-memchr-set` |
| 2 | ≤ K terms (K = `UNMEASURED DEFAULT` until step 2) | SWAR term-OR loop as an inline compound statement (today's door suffices) | per-level helpers + selector (needs N2) | `no-pf-terms` (scalar), plus one SIMD deny per level |
| 3 | otherwise | today's `pf_walk[_bounded]` | — | — |

`mcK` is not a row until step 2 shows it beating SWAR in some regime the row can
detect. Without N1 the row cannot detect density, so `mcK` stays a twin.

**Applicable vs assumption-changing.** Rows 1-3 change no pcrec assumption. The
site, the guards and the miss values are as today (the in-place `lo`, `miss` =
`hi`). Row 1 at the VM hat changes the dense regime (Q-R5); hence N1.

**Fits the architecture vs needs a refactor.** SIMD-off fits as is: STMT rows in
`pffind.c`, with an inline compound statement as text and no file-scope part.
SIMD-on needs the PF/MLINE door to offer a file-scope sink (N2): one argument in
`pcrec_memfn_emit`, and pcrec's PF callers passing the artifact's helper region.
That is a small pcrec refactor and the only one. The VM hat's entry and retry
statements are two sites with one set. With N2 they share one helper (D122); with
the inline form each gets its own copy of identical text.

**Unlocks** (filed with triggers, not built):
- **(a)** The in-loop STAY/EDGE/VMSPAN skips whose EXIT set is small (`[^"]*` exits
  on `{"}`) are the same FIND over the exit set. Trigger: a measured stay-loop
  loss where the exit set has ≤ K terms.
- **(b)** ofsskip `fn_rows[]` gets a BODY row scanning a set offset, the same term
  renderer. Trigger: pcrec re-prices prefix_k's set offsets (F-1), with
  `ci-moskva` as the witness.
- **(c)** The N4 set rest (ALL_PRESENT over SET terms) reads the same lane tests.
  Trigger: a set-rest cell in a loss table.
- **(d)** `[START-DENSE]`'s density admission reads N1's facts, so the row and the
  admission share one fact source.

**Leaning: the general row, built in two halves.** The SIMD-off half needs no
pcrec change, and SIMD-off movers are a pcrec abi event sequenced by main. The
SIMD-on half waits for N2 and the SIMD thread's 2:1 capacity. K is read off step
2's timing as the largest term count where SWAR beats `table` in every regime.
Row 1's VM-hat arm waits for N1, unless step 2 shows memchr holding at 800k ppm,
which this lane expects it will not. In that case the VM hat's |S| = 1 goes to
row 2, SWAR eq.

## 4. Twins (question 4)

### 4.1 What was built

`gen_twins.py` renders the C text a row would render, one function per (cell,
form) with every constant literal. The kernel contract is the PF walk's: the least
`i` in `[lo, hi)` with `s[i]` in S, else `hi`, or `lo` when `lo >= hi`, with
`hi = n - end_back`. The cells:

| cell | S | forms |
|---|---|---|
| `adl` | {63,D0,E6} | table, mc3, swar (3 eq), sse2, avx2 |
| `qdm` | {22,27} | table, mc2, swar (2 eq), sse2, avx2 |
| `alt2` / `alt2r` | {63,64} | as a pair (2 eq) / as a range |
| `bkn`, `bpr` | {3C}, {28} | table, memchr, swar, sse2, avx2 |
| `sig`, `tki` | {CE,CF}, {49,69} | table, mc2, swar (1 cube), sse2, avx2 |
| `kel` | {4B,6B,E2} | table, mc3, swar (cube + eq), sse2, avx2 |
| `hbr` / `hbrc` | 80..FF | as a range / as a cube |
| `u8l` | C2..DF | bounded; as a range |
| `dig`, `lc` | [0-9], [a-z] | DENSE CONTROLS: the bench's non-losing range sites |

They are built with the bench's artifact flags, `gcc -O2 -fPIC` (gcc 15.2.0, this
box).

### 4.2 The exhaustive check (`check.c`; `out/check*.txt`)

The reference is the byte loop over the TABLE derived from the cell's member
list. The SWAR/SIMD terms are a second, independent spelling of S. Every twin is
called at hi = n and hi = n - 1 for every lo in [0, n] and every n in [0, 80]:

| family | what |
|---|---|
| F1 | every byte value at every position and lane phase (`(i*step + seed) & 255`, 256 seeds × 3 steps) |
| F2 | one probe at every (n, p, lo): the probe ranges over every member and near-member (one-bit flips, edges ±1; edges only for sets > 8), the background over three bytes |
| F3 | 4,000 random alphabet subjects |
| F4 | 1,500 subjects ending at a PROT_NONE page and 1,500 starting after one |

Results:

    R17 CHECK: twins=65 calls=1874741290 mismatches=0          (out/check.txt)
    R17 CHECK: ... mismatches=550086450 (PLANTED reference)
    R17 PLANT: cells whose table twin was caught = 14 of 14    (out/check_planted.txt)
    R17 CHECK: twins=65 calls=300215353 mismatches=0           (ASan+UBSan, n <= 40)

Reproduce from the worktree root:

    O=build/scratch/r17/tw; mkdir -p $O
    python3 -I docs/design/memfn/probes/r17/gen_twins.py > $O/twins_gen.h
    taskset -c 12-15 gcc -O2 -fPIC -I$O -o $O/check docs/design/memfn/probes/r17/check.c
    taskset -c 12 $O/check            # ~40 s; PLANT=1 for the control

### 4.3 The timing harness (step 2; WRITTEN, NOT RUN)

`time.c` + `run_time.sh` are modelled on rq4/r14p's shape. They give a
calibrated sample of at least 50 ms per form, R = 7 repeats interleaved across
forms, `taskset` pinning, an answer checksum on every sample (`VOID` on a
mismatch), and absolute ns per call and per byte against a FLOOR row. The floor
answers from a precomputed next-hit array, so it pays the driver and the calls
but reads no subject byte.

Regimes, each named on every row:
- findall (throughput, one FIND per hit, as the prefilter re-enters) at 64 KiB and
  1 MiB, ppm in {0 (hit-sparse), 1000, 20000, 70000 (hit-dense: {c,d} in text)};
- findall at 64 KiB, ppm in {300000, 800000}: the DENSE CONTROL, which the
  `[0-9]`/`[a-z]` sites live in and which Q-R5 measured;
- percall (latency, short spans), L in {16, 64};
- optionally the bench's own subjects (`SUBJ_TSV`, regenerated read-only with the
  lossreview instruments).

Exact command for a QUIET slot (≈ 8 min, 169 invocations; check re-run first; last
line `R17 TIMING COMPLETE rc=0 rows=K void=V`):

    cd <worktree>
    L=build/scratch/r17/slot CORE=<idle core> R=7 MIN_MS=50 \
      nohup bash docs/design/memfn/probes/r17/run_time.sh > build/scratch/r17/slot.log 2>&1 & disown
    # dry run: DRYRUN=1 L=build/scratch/r17/dry CORE=12 bash docs/design/memfn/probes/r17/run_time.sh

Read it per row as `d_floor_ns` of each form against `table`'s. A form is a
candidate only where it beats `table` in EVERY regime its sites can be in (K-1).
SIMD rows are read against the best SIMD-off row. The official verdict is the
bench's on the target box (D144 addendum 4); these are kit-unofficial, and both
boxes matter (Zen 1 ubuntubudu: AVX2 at 2×128).

Expectations to falsify (UNMEASURED; the loss review's fit puts the table walk at
~0.44 ns/B on Zen 1):
- swar beats table by ≥ 3× per byte at ppm 0 on every cell;
- at 800k ppm, swar is within the floor band of table, and memchr/mcK LOSE there
  (the Q-R5 regime);
- `alt2r` (range) ≤ `alt2` (2 eq);
- `hbrc` (cube) ≈ `hbr` (range);
- `mc2` beats swar at ppm 0 on 1 MiB (glibc AVX2 inside), and loses from ~20k ppm.

## 5. pcrec-side needs (question 5) — facts, never methods

| # | need | why | status |
|---|---|---|---|
| N1 | `mf_site.cand_ppm_lo/hi` and `mf_term.ppm_lo/hi` filled at every PF / DFA-hat / VM-hat FIND (the prior's rate of the scanned set) | A row whose form costs a call per hit (memchr, mcK) must decline on a dense set: Q-R5's x0.6 at 80%. Without the fact the kit can serve the VM hat's \|S\| = 1 only with a call-free form. | already promised in R-17 ("a separate no-mover change") |
| N2 | the PF and MLINE FIND sites offer the kit a file-scope sink, the artifact's helper region before the function the statement sits in (`pcrec_memfn_emit` passes `NULL` today) | D155: the SIMD-on helpers and their selector must be file-scope functions; a function that does work holds no `#if`. It also lets the VM hat's two statements share one helper. A row that needs no helper ignores the sink. | NEW request to main; needed only for the SIMD layer |

Findings for main (information, not requests; D157 keeps the pricing pcrec's to
fix):
- **F-1.** `src/opt/prefix_k.c` prices the offset-0 set scan as the table walk
  (`C_BITMAP` 116 against `C_MEMCHR` 6, "MEASURED at 1.16 cycles/byte"). Its rule
  (b) admits only a singleton scan offset past 0 "since a set wide enough to need
  one is never selective enough". Both describe the table form. When a kit set row
  ships, the constant describes a form no longer rendered (integration §19's class
  of pcrec pricing kit search code). `ci-moskva`'s offset-1 cube `{9C,BC}` is the
  witness (0.82 ms).
- **F-2.** `pf_vm_emit_first_class`'s comment ("the `|S| = 1 -> memchr` cut-over is
  an unmeasured default ... not taken") and `pffind.c`'s header ("the
  one-byte/table split is the SITE's") both go stale the day the kit chooses by
  set shape. pcrec's text never chose a method here; it named a table. Doc-only.

## 6. Standing design questions

1. **Measurement regime: relevant.** No number here was taken under timing.
   §4.3 names every regime the harness measures, and the decision rule requires a
   form to win in every regime its sites occupy. The dense control exists because
   Q-R5's dense regime flips the memchr decision.
2. **Independent control: relevant.** The check's reference is the byte loop over
   a table built from the member list. The twins' lane tests are a separate
   spelling of S, and the planted reference (14/14) shows the check can fail. The
   census population is counted (K35): 757/511 bodies counted for the OFS claim,
   1,009 PF memchr sites. A future row's G1 population must come from a pcrec-side
   artifact diff (`census.py` reads emitted C, so it is a candidate), never from
   the kit's `moved`. Proposed sabotage use of S820-S824: S820 the range term's
   upper edge off by one, S821 a cube mask with one bit wrong, S822 the SWAR tail
   dropping the last byte, S823 the overlapped final block's lane mask shifted by
   one, S824 the NOP memchr row's `lo < hi` guard removed. Each is caught by
   `check.c`-style G2 rows.
3. **What moves when data is regenerated: not yet.** No data file. K is a
   measured constant (step 2) that moves bytes; re-measuring it is a pcrec abi
   event.

## 7. Charter vs committed

| question | artifact | status |
|---|---|---|
| 1 sites, rows, why not memchr/pair, fact vs kit, population | §1; `probes/r17/census.py`, `summarize.py`, `out/summary_corpus.md`, `out/summary_bench.md`, `out/census_corpus.log` | DONE |
| 2 named cells → pattern/site/shape; non-scan losses | §2 | DONE (ci-strasse needs a bench re-measure: OWED, bench via main, trigger = the next bench pin) |
| 3 forms per shape and layer, guards, reuse, one general row, lenses, leaning | §3 | DONE |
| 4 twins for the top cells, exhaustive check with counts | `probes/r17/gen_twins.py`, `check.c`, `out/check*.txt`; §4.1-4.2 | DONE (65 twins / 14 cells, 0 mismatches) |
| 4 timing harness, exact commands, not run | `probes/r17/time.c`, `run_time.sh`; §4.3 | WRITTEN; the RUN is OWED to the kit manager's next quiet slot (after R-16's slot23) |
| 5 pcrec-side needs as facts | §5 (N1, N2; F-1, F-2) | DONE; N2 is a new request for main |
| CLAUDE.md updates | `probes/r17/CLAUDE.md` (new), `probes/CLAUDE.md`, `docs/dev/lanes/CLAUDE.md` | DONE |
