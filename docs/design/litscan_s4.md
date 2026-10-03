# `[OPT-LITSCAN]` S4: the caseless stage — one run compare, a caseless VM run, and a caseless necessary run

Lane `s4des` (opus), 2026-10-03, branch `lane/s4des` from main `c231ffc1`
(abi 55). **Design only.** Nothing under `src/`, `cli/`, `lib/` or `tests/`
changed. This is round 1 of the `[OPTLOOP]` cycle opened under D144 (alpha =
`make test` + targeted timing per optimization; batch gate per round).
`[WORD-FOLD]` is a member of this stage. No darwin clock is cited as
evidence: the only darwin timing taken (§1.6) is scratch-tier, and it is
reported because it CONTRADICTS a prior, not because it supports one. Every
other number is a count taken from emitted artifacts, an instruction listing,
or a Ryzen measurement from the bench's own records.
Instruments: `docs/dev/optloop/s4/` (its `CLAUDE.md` lists them).

Governing rulings:
- D122 and its four addenda. ADDENDUM 1: the kit is an outcome, not a
  mandate, and pay-for-what-you-use. ADDENDUM 2 (2): the cube lives in
  `src/core/`. ADDENDUM 2 (4): every form choice is a table row with its own
  deny. ADDENDUM 3: portable SWAR is admitted. ADDENDUM 4: `dfa_pfs[]`
  changes take the full panel.
- D124 (one table per question, engine hats), D126 Q3/Q4 (fact-level
  denies; the NONE answer is spelled once per question kind), D127 (the
  L >= 3 floor) and D144.
- The manager's disposition on the `[OPT-LITSCAN]` row: S4 builds ONE
  overlapping-load emitter, masked. P4's exact arm moves onto it, with the
  mask elided, carrying the 5.6-7.6% exact win.
- The HARD REQUIREMENT on the row: compile-time masks derive from
  `src/core/fold.c`, and they join `tests/backrefs/fold_agreement_check.c`
  as a third consumer.

---

## 0. Findings first

1. **"One overlapping-load emitter" means one emitter FUNCTION with a row
   table, not one emitted spelling.** `pcrec_emit_run_compare` (§1.3) owns
   every literal-run compare in emitted C. Its four rows are:

   | row | role | deny |
   |---|---|---|
   | `words` | masked | 42 |
   | `overlap` | exact, `L` in {3, 5-7, 9-15} | 42 |
   | `bytes` | masked fallback | none |
   | `memcmp` | exact fallback: today's P4 text, byte for byte | none |

   P4's exact arm "moves onto it" in that sense. `memcmp` stays a row where
   it is already one load (`L` in {1,2,4,8}) or a vector compare
   (`L >= 16`). Pay-for-what-you-use holds at **word** grain: a word whose
   mask is all `0xFF` emits no `&`, and a word whose mask is all `0x00` is
   not loaded.
2. **The exact arm's win is not established, and a scratch probe on this box
   contradicts it in a second loop shape (§1.6).**
   - In a find-all loop over 1 MiB, gcc-16 `memcmp` at `L = 7` ran
     **0.466 ns/pos** against the hand overlap's **0.620**, reproduced three
     times.
   - Both loops execute the same one-load fast path. The difference is
     layout, the F5 class (`b108_reading.md` §1).
   - So the exact row carries its own deny, its own alpha cells, and a
     ship-only-if-measured condition (Q3).
3. **The spelling decides branchiness on BOTH compilers, not gcc alone (§1.5).**
   - The memcmp study's "gcc branchy, clang branchless" was about how each
     lowers `memcmp`.
   - With hand-spelled words, `a && b` is an early-exit branch under gcc-16
     AND clang (arm64, x86_64). `!((a ^ A) | (b ^ B))` is branchless under
     both.
   - The design emits the early-exit `&&`. It is the form §10.2 measured
     17-35% faster than the wide load, and the form the scratch probe
     favours on masked words (0.620 vs 0.684 ns/pos). The fused spelling is
     a one-sed twin in the alpha, not a row (Q10).
4. **The endian-neutral constant spelling costs nothing (§1.4).** A word is
   `<p>_w4(subject + o)`, and its constant is `<p>_w4("SELE")`: the same
   `memcpy` load applied to a string literal. gcc-16 at `-O1` and `-O2`, and
   clang arm64/x86_64 at `-O2`, fold every such constant to an immediate.
   Nothing is loaded at run time and no `.rodata` is used. No integer
   literal of the target's byte order appears in emitted text, so the
   big-endian hazard is closed by construction. No box we own could witness
   it.
5. **The overlap form makes the ASan sweep non-blind by construction (§5.2).**
   gcc-16 `-O2 -fsanitize=address` instruments **each word load** (2 checks
   at `L = 5`). The inlined constant `memcmp` gets **zero** checks. That is
   S2a's blind sweep (`s2afix`), reproduced in isolation. `memcmp` rows
   still need `-fno-builtin-memcmp`.
6. **S4 has one measured customer, and it is a DFA-route PRE-CHECK, not a VM
   compare.** `waf_attribution.md` and its Linux block (bench O-55, gcc 15.2,
   `t-1m`) give:

   | `union-select` | ns/B |
   |---|---|
   | base | 0.7178 |
   | hand twin, two-stream `memchr` + caseless verify, run `from` scanned on `m` | 0.2348 |
   | twin, `from` on `f` | 0.3441 |
   | twin, `select` on `c` | 0.4389 |
   | twin, `union` on `u` | 0.4701 |
   | re2 | 0.319 |

   That is S4(a), the caseless necessary run. §2.3 designs it. The VM
   caseless run (`[WORD-FOLD]`'s VM half) has **no losing bench cell**:
   - on the default route only two bench artifacts carry a VM fold test,
     `slack-webhook-url` and `syslogbase-expanded`, and both are wins or
     prefilter-answered;
   - its timed witnesses are forced-VM cells and a synthetic per-position
     cell (§6).

   It is built because it is the same emitter with the mask on (one
   primitive, D122), and it shrinks the program. This is recorded honestly
   as a D77 gap, not hidden (Q9).
7. **[r1 S3/C2, revised; r2 R2-C3] S4(a) leaves `dfa_pfs[]`'s SHAPE alone,
   and (r2) every measured selection with it (§2.3.5).**
   - The pin is published by `pcrec_run_pin` (`src/facts/kset.c:240`), not
     by `prefix_k.c`. It is a fact about EXACT positions: [r2] it pins the
     maximal exact stretch of the window around the window's rarest exact
     byte, so a masked run keeps the exact positions today's pin covered.
   - The table's rows, predicates and emitters are unchanged.
   - Under r1's single ranking a masked run can OUTRANK an exact pinned
     run. r1 then dropped the pin on 10 artifacts and moved 2 selections.
     [r2] Of those 10, 9 keep a pin at the SAME offset and 1 (`slack`,
     whose window has no exact stretch of two) loses it on a row that does
     not read it, so 0 selections move and 1 G1 verdict moves
     (`a[bc]de`, §2.3.7).
   - The one shared decision that changes is still `req_admit` (P7). It
     learns that "nothing necessary" means no byte AND no run (Q4).

8. **[r1 C1/C4, revised] One ranking, information, over exact and cube runs
   alike. The scan member comes from the EXISTING readers, generalized
   (§2.3.1, §2.3.3).**
   - A run position is a byte (`K = 0xFF`) or a two-member cube. The walk
     ranks every run by `Σ popcount(K_i)`, which is `8 × len` for an exact
     run, so exact runs keep today's order.
   - One floor, `PCREC_MIN_REQ_RUN_BITS` = 16 (two exact bytes), replaces
     both round 0's exact floor of 2 and its cube floor of 3.
   - The run pick ranks `select` (42) > `union` (35) > `from` (28). The bench
     would prefer `from` (0.3441 against `select`'s 0.4389), and deployment
     traffic is wrong for `from` (WAF §3.2). The deployment-sane rule wins
     (Q6).
   - The scan member is `pcrec_find_run_scan_index` over (T, K): cost is the
     position's member-set mass, ties go to the rightmost, and the NONE
     answer is the rightmost. There is no masked-only rule. [r2 R2-C1] It
     reaches that through ONE extended PICK primitive whose candidates are
     cubes, so the NONE answer stays inside the primitive (D126 Q4).
   - `[FINDINGS.B4]`'s `run-rarity` replaces it as the C6 reader (Q7).

9. **The hard requirement is met through the SET, not by reading the fold
   table at emission (§1.2).**
   - The mask is `cube_of` of the byte set. For a caseless letter, that set
     is `cls_casefold`'s output from `pcrec_ascii_fold`.
   - Reading the table directly at emission would be a fourth spelling of
     the letter range (compare_stack D1). It would also be a special case
     that `{j,k}` and `[0-7]` would not take.
   - The third consumer of `fold_agreement_check.c` sweeps 65,536
     (position, byte) pairs through an EMITTED 256-position masked run,
     against the table (§5.3).

---

## 1. The primitive

### 1.1 What exists today

- **P4** is `pcrec_emit_exact_compare` (`src/gen/emit_dfa.c:963`). It writes
  `!memcmp(<base>, "<bytes>", L)`. It has three callers:
  - the offset-skip block's run term, which is also the run pre-check's
    compare since S1 step 6 (`ofsk_emit_verify`);
  - the VM's literal run (`vm_lit`, `emit_vm.c:8616`);
  - the island's single-child chains (`vm_isl_emit`, `emit_vm.c:4481`).
- **The VM run fact** is `pcrec_lit_run` (`src/core/cpset.c:391`). It returns
  three or more consecutive SINGLETON `A_CLASS` spine elements (D127). A
  caseless letter is a two-member class, so it ends the run.
- **A caseless letter on the VM** is one label per byte. clskit's
  `byte-fold-default` row emits it (`clskit.c:610`):
  `if (scan_position < subject_length && ((subject[scan_position] | 0x20) == 117)) { scan_position++; goto rx_L3; }`
  The forced-VM `union-select` artifact carries 15 of these, `concat-sqli`
  744, and `altwide/ci-256` 1,842 (§7).
- **The cube** exists once in `src/`: `cube_of` in `src/gen/clskit.c:206`.
  It is section-relative (`base = iv[i].lo`), and offsets past the span are
  don't-cares behind the kit's dispatch. compare_stack P2 asked for an
  absolute-byte form in `src/core/`. It does not exist yet.

### 1.2 P2: the byte cube moves to `src/core/` (D122 addendum 2 (2))

**The definition is ONE function, parameterized by the domain the
membership is tested over.**

```c
/* src/core/cpset.c — is iv[i..j] exactly ONE AND-mask cube over [base, base+w)?
 * On success (x & *care) == *val is membership for every x in that domain. */
bool pcrec_cube_of(const PcrecCpRange *iv, int i, int j,
                   unsigned base, unsigned w, unsigned *care, unsigned *val);
/* The byte-domain reader the run facts use: an A_CLASS's byte set as (K, T)
 * over all 256 bytes; false when it is not one cube. A singleton is K = 0xFF. */
bool pcrec_cls_cube(Ctx *cx, const Ast *a, unsigned char *K, unsigned char *T);
```

- clskit's caller passes `base = iv[i].lo`, `w = span`, today's semantics,
  so its selections are byte-identical. That is the zero-movers gate,
  `scripts/cls_identity.py` plus `scripts/emit_sweep.py`.
- The run facts pass `base = 0`, `w = 256`: the absolute cube.
- The exact check over the domain (`cube_of`'s second loop, at most 256
  points) is the one agreement control D2 asked for. With it the three
  copies outside `src/` are retired as checks:
  - `docs/dev/optloop/wf/wf_run_probe.c`;
  - `studies/cls_tree_study/discover.c`;
  - `studies/cls_tree_study/kit.py`.

  They stay as study artifacts.
- `pcrec_cls_single` becomes the `K == 0xFF` reading of the same function.
  It is NOT replaced in S4: it has 6+ readers, and replacing it is
  implement-then-replace work with no customer.

**How the mask derives from `fold.c` (the hard requirement).**
- D23 folds `(?i)s` at parse time. `cls_casefold` widens it to `{S, s}`,
  and it reads `pcrec_ascii_fold` (`fold.c:68`) to do so.
- `pcrec_cls_cube({0x53, 0x73})` then returns `K = 0xDF`, `T = 0x53`.
- So every caseless mask is a pure function of a set that `fold.c`
  produced. No emitter or fact reads the table again.

Two shortcuts were considered and rejected:

| shortcut | why rejected |
|---|---|
| `K = 0xDF where pcrec_ascii_fold[c] != c` | it is a fourth spelling of the letter range, compare_stack D1's failure class, and it would not cover `{j,k}`, `[0-7]` or `(?s).` |
| leave clskit's `is_ascii_fold_pair` recognizer as is | it is D1's unguarded fourth spelling; it becomes a P2 reader when `[CLS-TREE]` next touches it, not in S4, because S4 has no customer for it (§2.4) |

### 1.3 The run compare: `pcrec_emit_run_compare` and its rows

**Home.** A new `src/gen/runcmp.c` plus `runcmp.h`, beside `clskit.c`: the
compare is a question both emitters share (D124). It takes P4's place, and
`pcrec_emit_exact_compare` is retired in the same commit
(implement-then-replace).

```c
typedef struct {
    const unsigned char *t;   /* T, already masked: (t[i] & k[i]) == t[i] */
    const unsigned char *k;   /* K per position, or NULL = every position exact */
    int len;                  /* >= 1 */
} PcrecRun;

/* Writes a C boolean expression, true iff (base[i] & k[i]) == t[i] for every
 * i < len. Reads EXACTLY base[0 .. len): the caller has emitted the P8 guard
 * (`pos + len <= n`, or a loop guard implying it). Returns the chosen row's
 * name for stamps and the listing. */
const char *pcrec_emit_run_compare(Ctx *cx, StrBuf *c, const char *base,
                                   const PcrecRun *r);
extern const PcrecRunRow pcrec_runcmp_rows[];   /* walked live by --list-axes */
```

**The word decomposition `D(L)`.** These are the windows a word row loads.
Every window lies inside `[0, L)`.

| `L` | words (width @ offset) |
|---|---|
| 1, 2, 4, 8 | one: `L@0` |
| 3 | `2@0`, `2@1` |
| 5-7 | `4@0`, `4@(L-4)` |
| 9-15 | `8@0`, `8@(L-8)` |
| 16 | `8@0`, `8@8` |
| > 16 | `8@0`, `8@8`, ..., `8@(L-8)`: ceil(L/8) words, the last overlapping |

**The rows.** They are first-match, in the `dfa_pfs[]`/`ROWS` shape:
`{name, deny, applies, emit}`.

| # | row | applies | emits | deny |
|---|---|---|---|---|
| 1 | `words` | some `k[i] != 0xFF` | `D(L)`, chained by `&&` in offset order. A word whose K is all `0xFF` compares unmasked; a word whose K is all `0x00` is not emitted | `-fno-run-overlap` (bit 42) |
| 2 | `overlap` | exact, `L` in {3, 5, 6, 7, 9 .. 15} (where gcc's `memcmp` decomposes into 2-4 pieces, `memcmp_lowering_study.md` §3) | `D(L)`, two unmasked words, `&&` | `-fno-run-overlap` (bit 42) |
| 3 | `bytes` | masked (domain total fallback) | `(base[i] & K) == T` per position, `&&`. K `0xFF` elides the `&`; K `0x00` skips the position | — |
| 4 | `memcmp` | exact (domain total fallback) | `!memcmp(base, "<t>", L)`: today's P4 text, byte for byte | — |

Two total fallbacks, one per domain, are what keep the deny honest:
- With bit 42 denied, every EXACT compare is abi 55's text. Rows 1-2 are
  the only exact movers.
- A masked run, which abi 55 never had, still compiles, by row 3. So
  `-fno-run-overlap` (the form) and `-fno-lit-run-fold` (the fact, §3)
  are orthogonal. Each flag's triage reads one mechanism.

**Rows not built, with the measurement that would build them (D77).**
- `fused`: the `|`-of-xors spelling of rows 1-2 (§1.5). Trigger: the
  alpha's one-sed twin beats `&&` beyond the base/deny noise floor on a
  witness. It would then replace the `&&` text, not join it as a row,
  unless the two win in different regimes.
- `lead-byte`: one byte test of the rarest position before the words, the
  F4 hedge (§6.3). Trigger: a per-position witness regresses beyond its
  noise floor.
- `run-time` K/T (S6's `span_match`). Trigger: a cell where
  `span_match` time matters, which does not exist yet. The interface
  above takes constant `t`/`k`. S6 would add a sibling entry, not widen
  this one.

### 1.4 Emitted shapes

**The load helper.** These are three `static inline` functions per artifact,
behind the render-prefix placeholder (D143). They are emitted only where the
artifact writes a word row: the same decision, and the same
`pcrec_emit_prologue` parameter, that S2a added for `#include <string.h>`.

```c
static inline uint32_t rx_w4(const void *p) { uint32_t w; memcpy(&w, p, 4); return w; }
/* likewise rx_w2 (uint16_t) and rx_w8 (uint64_t); <stdint.h> already arrives via the .h */
```

The constant goes through the SAME helper applied to a string literal. That
makes it endian-neutral by construction (§0 item 4). `pcrec_sb_cstr` writes
the bytes with octal escapes, so `0xDF` becomes `\337`. The comment
rendering keeps `emit_comment_safe_byte` (coding_guide §3.2).

Each example below follows today's site text up to `&&`:

```c
/* exact, L = 5, ofsskip run term `/user` (router-prefix-order), row `overlap` */
rx_w4(subject + cand) == rx_w4("/use") && rx_w4(subject + cand + 1) == rx_w4("user")

/* exact, L = 3, the reqrun verify `://` (slack-webhook-url), row `overlap` */
rx_w2(subject + cand) == rx_w2(":/") && rx_w2(subject + cand + 1) == rx_w2("//")

/* masked, L = 6, (?i)select on the VM, row `words` */
if (scan_position + 6 <= subject_length
    && (rx_w4(subject + scan_position) & rx_w4("\337\337\337\337")) == rx_w4("SELE")
    && (rx_w4(subject + scan_position + 2) & rx_w4("\337\337\337\337")) == rx_w4("LECT"))
    { scan_position += 6; goto rx_L9; }

/* masked, L = 12, (?i)group_concat, mixed ('_' is K = 0xFF inside the mask) */
(rx_w8(s + p) & rx_w8("\337\337\337\337\337\377\337\337")) == rx_w8("GROUP_CO")
 && (rx_w8(s + p + 4) & rx_w8("\337\377\337\337\337\337\337\337")) == rx_w8("P_CONCAT")

/* masked, L = 20, (?i)information_schema: three words at 0, 8, 12 */
```

**The P8 guard is unchanged at every site.**
- The VM writes `scan_position + L <= subject_length`.
- The island writes `scan_position + depth + L <= subject_length`.
- The `<p>_ofsskip`/`<p>_reqrun` blocks rely on their
  `while (pos + maxk < n)` guard. `maxk >= run_o + L - 1`
  (`ofs_test_model`; S287 defends the widening).

The primitive adds one invariant: **the last word's offset is `L - W`**, so
no word reaches past the run. A structural codegen check asserts it on every
emitted word (§5.4), and sabotage S442 plants the violation (§5.5).

### 1.5 gcc's branchy masked overlap, and how it is handled

The memcmp study §10.1 found gcc-16 rendering `cmp_ovmask_7` with a real
branch where its unmasked overlap used `ccmp`. Re-probed here with the
emitted spelling above (`docs/dev/optloop/s4/spell.c`, `gcc-16 -O1/-O2 -S`,
`clang -O2 -S` for arm64 and `-target x86_64`):

| spelling | gcc-16 arm64 `-O2` | clang arm64 | clang x86_64 |
|---|---|---|---|
| masked `a && b`, L = 6 | 1 early-exit branch (`beq` into the 2nd word) | `b.ne` (same shape) | `jne` (same shape) |
| masked `!((a^A)\|(b^B))`, L = 6 | branchless: 2 loads, `eor`, `orr`, `cset` | branchless | branchless (`xorl`, `orl`, `sete`) |
| exact `a && b`, L = 5 (`ov5`) | branchy | branchy | branchy (`cmpl mem`, `jne`) |
| exact `!memcmp`, L = 5 | 4+1 pieces, branchy | branchless | branchless (`xor`/`or`/`sete`) |

**So the asymmetry was about `memcmp`.**
- clang lowers a constant `memcmp` branchless, and gcc does not.
- With the words spelled by hand, the emitted TEXT decides branchiness, on
  both compilers.
- "Spell it so gcc stays branchless" is therefore available: it is the `|`
  spelling.

**Whether branchless is FASTER is a separate question, and the evidence
points the other way for this population.**
- §10.2 measured the early-exit masked overlap 17-35% faster than the wide
  single load. On a mostly-mismatch scan the first word's branch is
  predictable and the second load is skipped.
- §1.6's scratch probe puts masked `&&` at 0.620 and `|` at 0.684 ns/pos.
- The design therefore emits `&&`, early-exit, in offset order.
- The fused `|` spelling is a twin in the alpha block (§6.2 step 3). It
  needs no deny bit: the alpha either swaps the text or does not.

### 1.6 A scratch probe that contradicts a prior (darwin, directional only)

`docs/dev/optloop/s4/hot.c`, gcc-16 `-O2`, Apple M1, load1 2.2-4.1, best of
9 rounds × 20 passes over 1 MiB, run three times:

| arm (find-all, every position) | random text | near-miss band |
|---|---|---|
| masked L=6 byte chain `(s[i]\|32)==c` (today's VM, minus labels) | 0.635 | 0.664 |
| masked L=6 `words` `&&` | **0.620** | **0.631** |
| masked L=6 `|` (fused) | 0.684 | 0.684 |
| masked L=12 `words` `&&` / `|` | 0.623 / 0.688 | 0.623 / 0.688 |
| exact L=7 `memcmp` | **0.466** | **0.570** |
| exact L=7 `overlap` `&&` | 0.620 | 0.706 |
| exact L=7 `overlap` `|` | 0.529 | 0.529 |

What the listing shows and what it means:
- `memcmp`'s loop body has MORE instructions on its fast path than
  `overlap`'s (`hot.s`).
- Both take one load, one compare and one branch before exiting.
- The 33% gap is therefore placement, the same class F5 recorded on the
  bench for S2a's VM runs (`b108_reading.md` §1).
- It contradicts §11's −5.9% at `L = 7` in a different loop shape.

That is the reason for §0 item 2 and Q3. **No exact-arm number from any box
is trusted until the alpha measures it on real artifacts on x86, against a
noise floor.** The masked rows do not depend on this: their alternative is
the per-byte chain, which they at worst tie.

---

## 2. The sites: which join, which keep their own form

### 2.1 P4's exact callers: they move (row choice only)

The three P4 callers become callers of the run compare with `k = NULL`:
- the offset-skip run term;
- the run pre-check verify;
- the VM run and the island chains.

They move only where row 2 applies (`L` in {3, 5-7, 9-15}). Bench census
(§7) over 339 patterns: **55 of 317 default-route artifacts and 92 of 318
forced-VM artifacts** carry at least one compare at an overlap length.
Every other exact compare is byte-identical (rows 4 and 2 never both apply).

### 2.2 The VM caseless run: `[WORD-FOLD]`'s VM half

**The fact widens, in place.**

```c
int pcrec_lit_run(Ctx *cx, const Ast *const *el, int n, int j,
                  unsigned char *t, unsigned char *k);
```

- With `k == NULL`, a position joins only if it is a singleton: today's
  answer exactly.
- With `k != NULL`, a position joins if its byte set is ONE cube
  (`pcrec_cls_cube`). `t`/`k` receive T and K. An all-singleton run reports
  `k[i] = 0xFF` throughout and goes to row 2 or 4 as today.
- The floor stays three positions (D127), in the fact: one row, one deny,
  as F5 ruled.
- The VM wrapper `vm_lit_run` passes `k = NULL` under `-fno-lit-run-fold`
  (bit 43), and returns 0 under `-fno-lit-run`. So both denies reach
  `vm_cat`, `vm_cost_cat` and `vm_count_slots` at once, the S2a property
  (S305 defends the slot walk's agreement).

**It is general, not caseless-only (the `[WORD-FOLD]` charter, D122
addendum 1).** These all become run positions:
- a caseless letter (`K = 0xDF`);
- `{j,k}` (`K = 0xFE`);
- `[0-7]` (`K = 0xF8`);
- `(?s).` under `byte` (`K = 0x00`, a don't-care that is never loaded).

A three-member class is not a cube, so it ends the run. `[ab]` is not a
cube either: `{0x61, 0x62}` spans two free bits and spills onto 0x60 and
0x63.

**What it charges is what the chain charged** (`limits.md` §3.1; S2a's
argument holds verbatim):
- one node per position, so `PCREC_MAX_VM_NODES` refuses the same
  patterns;
- one fail-label entry per compare, so steps are unchanged;
- the work budget is untouched. Islands do not take cube runs.

`limits.md` §3.1's run sentence widens from "one-byte literals" to
"single-cube byte classes". That is its only spec change.

**Stamps.**
- `<PREFIX>_VM_LIT_RUNS` keeps counting runs.
- A new `<PREFIX>_VM_LIT_MASKED` counts the runs that took row 1 or 3. It
  is the activity stamp `--list-axes` reads for the `lit-run-fold` row,
  as `RX_VM_LIT_RUNS` is for `lit-run`.
- `<PREFIX>_VM_CLS_FOLDS` moves down wherever a run absorbs a fold class.
  That is expected, and the mover census names it.

**The listing.** `--emit-ir`'s `compare` op (S2a) describes a masked run as
`'select' (6 bytes, 6 masked)`. That is a `docs/spec/ir_listing.md` hunk
and an `irsb` re-capture (coding_guide §3.3: the identity gates do not see
the listing).

### 2.3 S4(a): the caseless necessary run (the one measured customer)

**[r1] This section was rewritten against the light D6 panel
(`docs/dev/reviews/2026-10-03-r1-litscan-s4-c3.md`).** Each change carries
its finding's tag; §R1 is the disposition table. The round-0 text is at
`26152329` for comparison. Two changes go beyond the panel's fixes, and §R1
names them as SHAPE changes: the run's position domain (§2.3.1) and the
dfa_pfs[] input population the single ranking moves (§2.3.5).

**[r2] Revision r2 applies the round-2 findings** (the same review file,
section "Round 2"). Each edit carries `[r2 <id>]`, and §R2 is the
disposition table. **The mechanism's shape does not change again**: the
position domain, the hull, the one ranking, the one floor, the pair arm and
P7's conjunct are r1's. r2 fixes how the pair arm is guarded and dispatched,
moves the pair's pick into the PICK primitive, states one invariant, and
gives the pin back its exact positions, which RESTORES the `dfa_pfs[]`
inputs r1 moved (§2.3.5, §2.3.7).

#### 2.3.1 The fact: `src/facts/req.c`, one triple over (T, K) positions

**[r1 C5] One triple, one key.** The round-0 walk carried a second triple
(`cbest`/`chead`/`ctail`) beside the exact one, each with its own declines.
That is gone:
- `RbRun` (`facts_derive.h:70`) gains `mask[PCREC_MAX_REQ_RUN_SCAN]`, the K
  of each stored position. `bytes` holds T. An exact position is
  `K = 0xFF`, and there is no other kind of exact.
- `RbRuns` keeps its one `best`/`head`/`tail`/`all`. Every helper copies
  `mask` beside `bytes` (`rn_app`, `rn_pre`). `rr_byte(b)` becomes
  `rr_pos(T, K)`.
- The declines are unchanged and are stated once (`req.c` header): no join
  across a repeat, no lookaround descent, and the common affixes of an
  alternation (now over (T, K), below).

**[r1, SHAPE] The position domain: a byte or a two-member cube.** A class
joins a run iff it is one cube of at most `PCREC_MAX_REQ_RUN_POS_SET`
members (2, a new `limits.def` row, §2.3.6). So `popcount(K)` is 8 or 7 at
every run position.
- The cube comes from C0's `pcrec_cls_cube` (P2, `src/core/cpset.c`). A
  `K = 0xFF` answer is the singleton, so `pcrec_cls_single`'s set arm reads
  the same call. The set's arm is unchanged: only a singleton is a set
  member.
- **Why the domain is narrower than round 0's "any cube".** Round 0
  admitted any cube, including `K = 0` (`(?s).`) and `[0-7]`. It then
  needed a second predicate at admission ("at least one member with
  `|set| <= 2`"), and a run whose best-ranked form had no scannable member
  would have declined. That decline would have LOST exact runs: an exact
  `ab` beside a 25-bit `[0-7]{5}` run. With the domain at two members,
  every position is a scan candidate. The scannability predicate
  disappears, and no ranking can pick an unscannable run.
- What it costs: non-letter cubes of four or more members and don't-care
  positions do not join a run. `wordfold_census.md` §2 found them rare.
  They remain C2's business (the VM run, `pcrec_lit_run`, any cube), which
  is a different fact with a different consumer.
- **Under `-fno-req-run-fold` (bit 44) the bound is 1.** That is the
  fact-level deny (D126 Q3). The walk is then exactly today's: singletons
  only, and the hull below requires `K' = 0xFF`, which is byte equality.
- **[r2 R2-S3] The canonical form: `T & ~K == 0` at every position.** T is
  the LOWER member, with every free bit clear. The scan's second member is
  `T | ~K` and the masked verify compares `(s & K) == T`; both read T as
  the member with the free bit clear. If a producer ever stored the upper
  member, `T | ~K == T`: the pair arm would scan one member twice and the
  verify would match nothing (`s & K` never has the free bit), so matches
  would be DELETED. Every producer satisfies it today: `pcrec_cls_cube`
  returns `T = member & K`, and the hull writes `T' = Ta & K'`.
  - It is enforced where a position is made. `rr_pos(T, K)` is the walk's
    one constructor of a position, and it refuses a non-canonical pair as an
    internal error (`pcrec_ctx_fail`), as `ofsk_emit_verify` refuses an
    empty chain. A loud stop, never a silent normalization: a silent `T &= K`
    would hide the producer's bug.
  - It is checked from outside on every artifact: §5.4's `--emit-facts`
    check reads `req_run` and `req_whole_run` and requires
    `T[i] & ~K[i] == 0` and `popcount(K[i]) ∈ {7, 8}` at every position.

**[r1 S1] The alternation's common head and tail are the CUBE HULL.** Round
0 compared T and kept the left branch's mask. That is order-dependent and
unsound: `(?:S(?i:ab)|(?i:sab))` claimed an exact `S` at position 0, while
`sab` matches. Position by position, for branches `a` and `b`:

```
K' = Ka & Kb & ~(Ta ^ Tb)        T' = Ta & K'
```

- `cube(T', K')` is the smallest cube holding both positions' member sets,
  so every byte either branch can put there is in it. Each branch's head
  starts where the alternation starts (each tail ends where it ends), so
  position `i` holds a byte of branch `a`'s set or of branch `b`'s set, and
  the hull holds both. The formula is symmetric in `a` and `b`, so the
  branch order cannot change the answer.
- `rn_common_head` and `rn_common_tail` continue while the hull passes the
  position-domain predicate above, and stop at the first position that
  fails. Stopping is a shorter claim, never an unsound one.
- On exact branches the hull is NEW information where they differ in one
  bit: `frank|fred` → `fr[ae]`, `(?:😀|😁)` → `F0 9F 98 [80|81]`. The census (§2.3.7) counts
  these. They are general (no caseless special case), and they are movers.
- `reqcube.rxt` carries both counterexamples in both branch orders, head
  and tail (§5.1).

**[r1 C4/C5] The ranking: one key, information.**
`rn_longer` becomes `rn_better(a, b) = info(b) > info(a) ? b : a`, where
`info = Σ popcount(K_i)`.
- An exact run's information is `8 × len`. So among exact runs the order and
  the tie rule (`a` on a tie: the earlier candidate) are exactly today's.
- **[r2 R2-C2] Exact-only artifacts: the FACTS are identical; the bytes
  are a prediction.** Wherever the winning run is exact, the walk publishes
  today's run, and (r2's census) today's window, scan index, `req_byte` and
  `run_pin`: 0 counter-examples in 603 (corpus 505, bench 98), §2.3.7 class
  B, measured on the auto engine at the fact level. That the emitted C is
  byte-identical too follows from the readers (every one of them reads only
  these facts on an exact run), but no instrument here read emitted C. The
  build's §5.1 mover manifest is the byte evidence, over every corpus
  pattern under auto AND `--engine=vm` and the bench patterns under all
  four configs.
- `info` is `log2(256/|set|)` summed. That is `findings/design.md` §6.2's
  per-position cardinality model, so the walk's key and the pick's NONE
  answer are the same model (D126 Q4).

**[r1 C4] One floor, one constant.** [r2 R2-C5] This is the NECESSARY
run's floor, in bits, read by one consumer: `pf_derive_req_walk`'s
publication. D127's `L >= 3` is a different floor with a different
consumer: the VM literal run (`pcrec_lit_run`, C2), in positions. They are
two floors because they guard two different facts, and neither is derived
from the other. The derived admission at publication
(`facts.c` `pf_derive_req_walk`, today `run.n >= 2`) becomes
`info(run) >= PCREC_MIN_REQ_RUN_BITS` (16, a new `limits.def` row).
- 16 bits is two exact bytes, so every exact run admitted today is admitted
  (`n >= 2` ⇔ `8n >= 16`).
- Three caseless letters (21) pass. Two caseless letters (14) and a
  caseless letter beside an exact byte (15) do not. Round 0's "cube runs need
  three positions" (Q8) was a second floor spelled in positions; it is
  subsumed, since a position is worth 7 or 8 bits.
- A run that passes the floor has at least two positions. So every reader's
  `len >= 2` / `whole_len >= 2` still means "a run shipped". No reader
  re-spells the floor, and `facts.h`'s "len is never 1" stays true.
- **Publication trims nothing.** With no `K = 0` positions in the domain,
  round 0's question of trimming don't-care edges does not arise.

**This OVERTURNS round 0's additive admission (Q5),** as the panel's C4
asked. An exact run no longer shadows a better cube run:
`(?i)select.*from 1=1` publishes `FROM 1=1` (60 bits) rather than today's
` 1=1` (32 bits), and `(?i)union select 1,2` publishes its whole
16-position run, windowed, rather than ` 1,2`.
The price is a mover population among artifacts that carry an exact run
today (§2.3.7 class C), which round 0's biconditional avoided by
construction.

#### 2.3.2 The record

**[r1 C5]** `ReqRun` (`src/facts/facts.h:64`) gains two arrays and no
flags:

```c
    unsigned char mask[PCREC_MAX_REQ_RUN_EMIT];        /* K of each window position; 0xFF exact */
    unsigned char whole_mask[PCREC_MAX_REQ_RUN_SCAN];  /* [K66]'s whole run's K */
```

- `bytes`/`whole` hold T. `mask == whole_mask + at`, the same derivation as
  `bytes == whole + at`.
- Round 0's `pair` and `masked` fields are dropped. They were derived
  values stored beside their source:
  - "the scan is a pair" is `mask[idx] != 0xFF`;
  - "the run is masked" is one `static inline bool
    pcrec_req_run_masked(const ReqRun *)` in `facts.h`, the one spelling
    every reader calls.
- For an exact run both arrays are all `0xFF`. A reader that reads only
  `bytes`/`len` stays correct on every exact run.

#### 2.3.3 The pick: the existing readers, generalized (D126 Q4)

**[r1 C1] There is no masked-only pick and no second window rule.** Round 0
added a member rule with its own tie order ("exact first, then rightmost")
beside `pcrec_find_run_scan_index`. That rule is withdrawn. The existing
readers take (T, K) candidates:

| reader (`src/core/findings.c`) | today | r1 |
|---|---|---|
| `pcrec_find_run_scan_index(rate, T, K, n)` (findings.c:500) | PICK over bytes `[n-1 … 0]`, cost `rate[b]`, ties to the earliest (rightmost); NONE → rightmost | [r2 R2-C1] the same order and tie, through the EXTENDED PICK primitive below: the candidates are the positions as cubes `(T[i], K[i])`, reversed. The reader builds the order and makes one call. It never tests `rate` |
| `pcrec_find_run_window_start(rate, T, K, n, idx)` (findings.c:526) | MASS over each 8-byte window, ties leftmost | MASS over each 8-position window, ties leftmost. [r2 R2-C1] The reader lists the window's MEMBERS (T for an exact position; T and `T \| ~K` for a pair) and makes one `pcrec_find_seq_mass` call per window, so MASS's own NONE answer (cardinality) applies with no reader branch: under NONE a window with more exact positions has fewer members and wins; on an exact run every window ties, as today |
| `pcrec_req_window` (req.c:489) | composes the two; copies `bytes` | the same; it also copies `mask` from `whole_mask + at` |

**[r2 R2-C1] The PICK primitive takes member-set candidates.** r1's table
said the pair's cost was `pcrec_find_seq_mass` and that NONE answered
"rightmost". Both cannot hold through the primitives as they are: under
NONE, `seq_mass` returns cardinality (1 for an exact position, 2 for a
pair), so an argmin over it picks the exact byte, and the rightmost answer
would then need the reader to test `rate == NULL` itself. D126 Q4 forbids
exactly that branch, and `pcrec_find_pick` took bytes, not sets. So the
PICK primitive is extended, and the NONE answer stays inside it:

```c
/* PICK: which of n candidates to scan. Candidate i is the CUBE
 * (cand[i], care[i]): its members are the bytes b with (b & care[i]) ==
 * cand[i] (cand[i] & ~care[i] == 0). care == NULL means every care[i] is
 * 0xFF, i.e. every candidate is the one byte cand[i]. Cost of a candidate:
 * the rate summed over its members. Argmin, ties to the EARLIEST
 * candidate; returns the INDEX. NONE: `rightmost`, the index of the
 * reader's positional rightmost candidate, whatever the candidates' sizes.
 * n >= 1, 0 <= rightmost < n. */
int pcrec_find_pick(const uint32_t *rate, const unsigned char *cand,
                    const unsigned char *care, int n, int rightmost);
```

- **Byte-identity of every existing reader.** `pcrec_find_set_pick` passes
  `care = NULL`. `pcrec_find_run_scan_index` passes the reversed mask, which
  is all `0xFF` on an exact run. A one-member cube costs `rate[cand[i]]`,
  so the argmin and the tie are today's on every exact candidate list. r2's
  census measured it at the fact level (§2.3.7: 0 of 603 exact-run
  artifacts change window, index or `req_byte`).
- **The NONE answer is spelled once, in the primitive** ("`rightmost`",
  before any cost is read). No reader holds a `rate == NULL` branch, so this
  is still one PICK kind with one NONE answer (`findings/design.md` §6.2),
  now over cube candidates. A cube of four or more members would be priced
  the same way; the run's position domain makes every candidate one or two
  members (§2.3.1), but the primitive does not assume it.
- **The member sum is the existing MASS definition** (`pcrec_find_set_mass`
  over the cube's members), so the pick and the window price a pair the
  same way, and no new number enters (§2.3.6).
- **`findings/design.md` §6.1/§6.2 hunk, in C3's commit:** §6.1's PICK
  signature and comment become the block above; §6.2's kind table reads
  "PICK | `pcrec_find_pick` | `cand[rightmost]` | C1, C2a, C8", unchanged
  but for a note that a candidate is a cube and a byte is the cube with care
  `0xFF`; row C2a's candidates become "the run's positions as cubes
  `(T[i], K[i])`, reversed". It is a kind row EXTENDED, not added: no new
  kind, no new NONE answer (§6.1's "a new reader of an existing kind
  inherits that answer").
- **Accepted, stated: `bar(?i:x)` under `-e utf8` (NONE).** The run is
  `bar[xX]` (31 bits). NONE answers the positional rightmost, so the scan is
  the PAIR at `X`, two streams, over the exact `r` next to it, one stream.
  The PICK kind's NONE answer carries no density claim, so it cannot know
  that one stream is cheaper. That is the same no-information answer that
  scans a run's last byte under NONE whatever it is, and a rate (the default
  table under `byte`, or any declared analysis) prices the pair with the
  rest. Under `byte` the default table picks the pair too (x and X sum to
  1,097 ppm, below every other member), so this is not a utf8-only
  outcome. A one-stream preference under NONE would be a reader-side NONE
  rule, which D126 Q4 forbids; its trigger is a measured utf8 cell where the
  pair scan loses to an adjacent exact byte.

- **One tie rule.** Round 0's "ties go to an exact member" is not a rule
  any more. Under a rate it falls out of the cost: one stream's mass against
  two summed. Under NONE the PICK answer is the positional rightmost, for
  exact and masked runs alike. That is [OPT-REQRUN-ENC]'s rule. Under
  `-e utf8` a run ending in a caseless character ends in a pair of
  continuation bytes, so the rightmost rule lands there and never on the
  character's lead byte. Round 0's "exact first" would have scanned the
  lead byte, R13's shape again. Today the walk joins no such run past one
  character (§2.3.7 item 4), so this is the rule's argument, not a counted
  mover.
- **Exact runs are byte-identical through both readers.** Every member has
  mass `rate[b]` (or the NONE uniform constant), so the argmin, the tie and
  the window are today's.
- **The pair's cost model is DENSITY ONLY**, as today's exact cost is. The
  second `memchr` stream's own per-byte cost is not modelled. O-55's twins
  are the only measurement (the run on `c` against `m`), and the model is
  revisited when `[FINDINGS.B4]`'s `run-rarity` replaces this reader as the
  C6 reader (Q7). No new number enters: the pair's cost is the rate summed
  over its members, MASS's own definition, computed inside the PICK
  primitive [r2 R2-C1] (§2.3.6, C7).
- **Which run** is the walk's (§2.3.1). On `union-select`
  (`(?i)union.*?select.*?from`) it is `SELECT` (42 bits) over `UNION` (35)
  and `FROM` (28), and the scan under the builtin prior is `c`'s pair: O-55's
  `ci_selectc` twin, **0.4389 ns/B against base 0.7178 (×1.64)**, still
  behind re2's 0.319. Q6 is unchanged.

**[r1 S2a] `req_byte`: a run byte only from an EXACT scan member.**
`pcrec_req_pick` (req.c:519) becomes:

```c
    if (run->len >= 2 && run->mask[run->idx] == 0xFF) return run->bytes[run->idx];
    if (set->rightmost < 0) *why = PF_WHY_NONE;
    return pcrec_find_set_pick(rate, set->bits, set->rightmost);
```

- Round 0 returned `bytes[idx]` whenever a run shipped. At a pair position
  that is T, a byte not every match contains: `(?i:select)\d+x`'s stamp
  would have read `T` (or `C`) where the analysis's answer is `x` (120).
- **How `REQ_BYTE` relates to the emitted scan:**
  - **(i) The run's scan member is exact, or no run shipped.** `REQ_BYTE` is
    the byte the pre-check's `memchr` tests, as today. With a run, it is
    `bytes[idx]` (§2.28's checkable pair, now conditional on
    `mask[idx] == 0xFF`).
  - **(ii) The run's scan member is a pair.** `REQ_BYTE` is the SET's pick,
    or `"none"` when the set is empty (`union-select`). The run block scans
    the pair (`REQ_RUN`'s `@idx` with its `/mask`).
    - On the no-DFA-scan VM route, K65's whole-set test then memchr's
      `REQ_BYTE` too (§2.3.5).
    - On every other route the artifact tests no single byte, and
      `REQ_BYTE` names the analysis. That is §2.27's existing "names the
      ANALYSIS, not the emission" sentence, gaining this third case.
  - Every `REQ_BYTE` value is a member of `req_set`, or `"none"`. §5.4
    checks it from `--emit-facts`. Round 0 broke this invariant.
- **Not built: a one-byte `memchr` of the set pick in front of the run
  block on DFA routes.** It would make case (ii) emit what `REQ_BYTE`
  names on every route. No cell asks for it (D77). Its trigger is a DFA-route
  pair-scan mover whose set pick is rare and absent on a measured subject.

#### 2.3.4 The scan: the pair arm in the one block emitter

`OfsTest` (`emit_dfa.c:331`) gains `run_mask`: NULL when the run is exact,
otherwise the window's or the whole run's mask. Round 0's `scan_pair` field
is dropped: the second member is `scan_byte | (~run_mask[scan_k] & 0xFF)`,
read where it is emitted.

**[r1 S4] Both `ofs_test_run` sites carry the mask.** `req_run_tests`
(`emit_dfa.c:991`) builds two tests, and each gets its own mask:
- `t[0]`, the window: `ofs_test_run(&t[0], r->bytes, r->mask, r->len, r->idx)`;
- `t[1]`, [K66]'s whole run on the no-DFA-scan route:
  `ofs_test_run(&t[1], r->whole, r->whole_mask, r->whole_len, r->at + r->idx)`.

A whole-run test built without its mask is an EXACT compare of T. It
deletes every match whose letters are not all upper case, on exactly the
route where the pre-check is the only proof. S448 (§5.5) plants that.

**[r2 R2-S2] The dispatch is re-keyed, and the pair arm is tested FIRST.**
r1 wrote that the unreachable `else` arm becomes the pair arm. But
`ofs_test_emit_fn` (`emit_dfa.c:5991`) branches on `t->scan_byte >= 0`, and
`ofs_test_run` sets `scan_byte = run[i]` for every run, so that test is
always true: with only `run_mask` added, the `memchr` arm would still win,
scan `T` alone and verify. `(?i)select` on `"select"` would scan `T`, find
nothing, and answer NOMATCH where python matches (0, 6). The block's
dispatch becomes one ordered test, read where the arm is chosen:

```c
if (t->run_mask && t->run_mask[t->scan_k - t->run_o] != 0xFF)
    /* the PAIR arm: two streams, T[k*] and T[k*] | ~K[k*] */
else if (t->scan_byte >= 0)
    /* the memchr arm: one stream (an exact scan member, masked or not) */
else
    pcrec_ctx_fail(...);   /* unreachable, as today */
```

- `scan_k - run_o` indexes the run, since `scan_k` is an offset from the
  candidate start. Every run test has `run_o == 0` (`ofs_test_run`), so it
  is `run_mask[scan_k]`; the subtraction is spelled so the predicate stays
  true if a run term ever sits at an offset.
- **Sabotage S453** (§5.5) plants the old order (the `scan_byte >= 0` test
  first). Its detector is a LOWERCASE `reqcube.rxt` cell: `(?i)select` on
  `"select"`, `m 0 6`, under both `engine auto` and `engine vm`. An
  all-uppercase subject cannot detect it, because the one stream it keeps
  is `T`.
- **The verify reads the mask in BOTH tests.** `ofsk_emit_verify`'s run term
  (`if (!k)`, today `pcrec_emit_exact_compare(..., t->run_bytes,
  t->run_len)`) becomes C1's `pcrec_emit_run_compare(..., t->run_bytes,
  t->run_mask, t->run_len)`, which writes the masked row when `run_mask` is
  non-NULL. Both `t[0]` (the window, `r->mask`) and `t[1]` (the whole run,
  `r->whole_mask`) reach it through the same `ofs_test_run`, so the mask
  cannot be dropped for one test and kept for the other except at the
  constructor call (S448's site).
- `ofs_test_of`, which builds the prefilter rows' tests, never sets
  `run_mask`: a pin is a fact about EXACT positions (§2.3.5, r2), so every
  run term a prefilter row carries is exact.

**The pair arm** is O-55's leapfrog against the block's own loop. The
streams are `a = T[k*]` and `b = T[k*] | ~K[k*]`, where `k*` is the scan
offset.
- Each stream holds one pending hit, as an OFFSET into the subject (never a
  pointer, so no NULL pointer is ever compared relationally).
- **[r2 R2-S1] Every search runs INSIDE the guarded loop.** r1 said both
  streams were "searched once before the loop", which contradicts its own
  `pos + maxk < n` argument: the K27 guard is the loop's condition, so a
  search above the loop has none. `(?i)select` (k* = 5) on `""` or `"abc"`
  would call `memchr(subject + pos + 5, 'T', n - pos - 5)` with a wrapped
  `size_t` length, a wild over-read; on `n = 0` with `k* = 0` it is
  `memchr(NULL, c, 0)`, K27 itself. So there is no pre-loop search. A
  `fresh` flag makes the first iteration search both streams, and every
  search sits under the same guard as the `memchr` arm's:

  ```c
  static inline size_t <p>_reqrun(const unsigned char *subject, size_t n, size_t pos)
  {
      size_t ha = 0, hb = 0;       /* pending hits; n = the stream is exhausted */
      int fresh = 1;
      while (pos + MAXK < n) {     /* MAXK >= K: the length below is >= 1 */
          size_t cand;
          if (fresh || ha < pos + K) {
              const void *q = memchr(subject + pos + K, A, n - pos - K);
              ha = q ? (size_t)((const unsigned char *)q - subject) : n;
          }
          if (fresh || hb < pos + K) {
              const void *q = memchr(subject + pos + K, B, n - pos - K);
              hb = q ? (size_t)((const unsigned char *)q - subject) : n;
          }
          fresh = 0;
          cand = ha < hb ? ha : hb;
          if (cand >= n) return n;
          cand -= K;
          if (cand + MAXK >= n) return n;
          if (/* the masked run compare */) return cand;
          pos = cand + 1;
      }
      return n;
  }
  ```

  where `A = T[k*]` and `B = T[k*] | ~K[k*]` are emitted as integer
  constants and `K = k*`. A loop that is never entered (`n <= MAXK`, which
  includes `n = 0` with a NULL subject) searches nothing and returns `n`.
  A stream parked at `n` is never re-searched, because the guard keeps
  `pos + K < n`.
- **[r1 S4] The re-search bound is the cursor's scan position.** At the top
  of each iteration a stream is re-searched iff its hit is
  `< pos + k*`. After a failed verify, `pos = cand + 1`, so the bound is
  `cand + 1 + k*`.
  - Round 0 wrote "falls behind the cursor", i.e. `< pos`. With `k* >= 1`
    that keeps the hit that just produced `cand` (it sits at `cand + k*`,
    which is `>= cand + 1`).
  - The next candidate is then the same `cand`, and `pos` never advances: a
    hang. S449 plants it. A watchdog-bounded `reqcube.rxt` cell is its
    detector.
- An exhausted stream parks at `n`. The candidate is `min(ha, hb) - k*`,
  and the block's existing `cand + maxk >= n → return n` exit ends the
  search, exactly as the `memchr` arm's does.
- The verify is the run compare (C1's row table, masked).
- [K27]'s `memchr(NULL, c, 0)` is closed by the loop guard
  `pos + maxk < n`, as in the `memchr` arm: every search's length is
  `n - pos - k* >= 1`. [r2 R2-S1] This now holds for EVERY search the arm
  makes, since none sits outside the loop. The empty- and short-subject
  cells (§5.1, `reqcube.rxt`) and a NULL-subject run of the K66 witness's
  blocks under UBSan/ASan (§5.2, §5.4) are its witnesses.
- **An exact scan member keeps today's `memchr` arm** with a masked verify.
  So `(?i)foo-bar` scans `-` in one stream whenever the rate says `-` is
  rarer than the cheapest pair, which is the selection the `[WORD-FOLD]` row
  named. It is now a consequence of the cost, not a rule.

#### 2.3.5 Admission and the consumers

**`req_admit` (P7, `emit_dfa.c:6374`).** Its first conjunct changes from
"`req_byte < 0`" to "`req_byte < 0` AND no run" → `NONE`, which says
"nothing necessary". Today the two spellings are equivalent, because a
shipped run's bytes are set members. They differ only on a masked run over
an empty set, which is exactly the population that needs the change.
- The two early returns that restate the old conjunct move with it.
  `pcrec_emit_req_byte_check`'s `if (b < 0) return;` (`emit_dfa.c:1194`)
  becomes `b < 0 && run->len < 2`. S265's anchor is re-verified there.
  `req_run_tests`'s `pcrec_fact_req_byte(cx) < 0 ||` (`emit_dfa.c:998`) is
  deleted: admission decides.
- **G2** (one attempt) applies unchanged.
- **G1** (`req_byte_dominated_by`, `emit_dfa.c:6352`) elides a run
  pre-check only behind a scan that verifies the run: its first conjunct
  requires `cs->run_verified`. [r2 R2-C3] With r2's pin a masked run can be
  verified, and then elided, but only where the selected test checks every
  position, the pair positions included, with members inside the
  position's cube (below). That is the same rule as today's, read over
  cubes, not a special case: `(?i)x/1234` is elided (its offset-0 model term
  is exactly `{x, X}`), `a[bc]de` is not (nothing tests offset 1).
- **D124 item 3, what P7's change guarantees to each consumer:**
  - **DFA, and the VM hybrid:** a pre-check is a check that does not run, or
    a proof of absence in one pass. It moves no answer.
  - **VM with no DFA scan:** it can only turn a step-budget give-up into a
    NOMATCH, by running fewer attempts, never the reverse. That holds
    because the run block is a sound necessary condition, and because K65's
    second half still tests every set member the run does not prove
    (`done[]`, below).

**[r1 S2b] K65's `done[]` marks only exact positions.** `emit_req_set_rest`
(`emit_dfa.c:1127`) marks `done[whole[k]]` for every whole-run position
today. It becomes:

```c
    if (r->len >= 2) {
        for (k = 0; k < r->whole_len; k++)
            if (r->whole_mask[k] == 0xFF) done[r->whole[k]] = true;
    } else done[pcrec_fact_req_byte(cx)] = true;
```

- At a pair position, T is not a byte the run check proved present (the
  subject may hold the other member). Round 0 marked it, so a set member
  equal to that T lost its `memchr`, and NOMATCH became a give-up.
- **Witness:** `(x?)([a-z]+)+S\d(?i:select)\1` on `"a"*30 + "1select"`.
  - The set is `{S}`, and `select`'s T is `SELECT`, whose first position's
    T is `S`.
  - Today K65's `memchr('S')` answers NOMATCH in one pass. Under round 0
    the run check passed on `select`, `S` was marked done, and the VM
    backtracked `([a-z]+)+` to its step budget.
  - D124 item 3 forbids that direction. §5.1 classifies it as a DEFECT,
    and the witness is a committed case.

**[r1 S3/C2] The pin's real site is `pcrec_run_pin` (`src/facts/kset.c:240`),
not `prefix_k.c`.** It needs `count == 1` at every offset it pins, so it
already refuses to claim a cube position: a pair has two members.

**[r2 R2-C3] The pin keeps the run's exact positions.** r1 added one
refusing conjunct (`pcrec_req_run_masked(r)` → unpinned). That dropped
sound pins: `a[bc]de` and `(?i)x/1234` keep an exact stretch (`de`,
`/1234`) the NFA walk still pins, so they lost `run-pinned` and gained a
pre-check, with no cell. r2 withdraws the conjunct and pins the exact
positions instead:
- **The rule, in `pcrec_run_pin(walk, r, rate, pin)`.** PICK over the
  window's EXACT positions in reverse order (the one PICK primitive,
  `care = NULL`; ties and NONE go to the rightmost exact position). The pin
  is the maximal stretch of exact positions around the picked one, when it
  has at least two positions (16 bits, the floor) and the walk's singletons
  spell it at some offset (the smallest, as today). `RunPin` gains `at` and
  `len` (the stretch inside the window) and `idx` (the picked position
  inside the stretch); `o` is the stretch's offset from the match start.
- **On an exact run it is today's pin.** The exact positions are the whole
  window, so the pick is the window's own `idx` (the same primitive over the
  same candidates), the stretch is the window, `at = 0`, `len = r->len`.
  r2's census: 603 of 603 exact-run artifacts publish the identical
  `run_pin` (§2.3.7 class B).
- **Where the run's own scan member is exact, the pin scans it too.** An
  argmin over the exact positions contains the window's argmin, in the same
  order, so the pin's `idx` is the run's. Where the scan member is a pair
  (`(?i)x/1234` under the default table, where `x` and `X` sum to 1,097 ppm),
  the pin scans the window's rarest EXACT byte (`/`). Either way the
  prefilter's scan is one exact byte, which is what its `memchr` rows emit.
- **Soundness.** The pin claims bytes at offsets, read from the walk's own
  singletons, exactly as today; the stretch is a sub-run of a necessary run,
  and the masked positions make no pin claim. A later satisfying offset, or
  a shorter stretch, is a lost opportunity, never a wrong answer.
- **What `dfa_pfs[]` sees: only exact bytes.** The run rows' term is the
  stretch (`bytes + at`, `len`, at `o`), compared exactly; their scan is
  `bytes[at + idx]` at `o + idx` (§4 rows 13-14). No masked run enters the
  table. The offset-preference step (a masked run TERM in the prefilter)
  is still named and not built, and still takes the full panel.
- **G1 asks about the WHOLE run, generalized to cubes** (§4 row 15): the
  selected test must test every run position `i` at offset
  `o - at + i` with a byte, or a term whose members all lie in
  `cube(T[i], K[i])`. That is today's question on an exact run.
  - `(?i)x/1234`: its `run-pinned` test checks offset 0 with a model term
    whose members are `{x, X}` (the cube) and offsets 1-5 as the run term.
    It verifies the masked run, so it stays `REQ_WHY "dominated"`.
  - `a[bc]de`: its test checks offsets 0 (`a`, a model term), 2 (the scan,
    `d`) and 3 (`e`), and not offset 1. It does NOT verify `a[bc]de`, so G1
    moves `dominated` → `emitted`: one masked pre-check pass (scan `d`, the
    `memchr` arm) ahead of an unchanged prefilter. That is the ranking's
    intent, not a side effect: the winning run says more (`[bc]` at 1) than
    the prefilter tests. If its cost shows on a measured cell, bit 44 is the
    interim kill switch (D144 item 3), and the cure is the offset-preference
    step, not a second admission rule.
- **The counted inputs (§2.3.7):** of the 10 artifacts pinned today whose
  run becomes masked, 9 keep a pin at the SAME offset (8 of them with a
  stretch byte-equal to today's run; `/abcd[xy]/user` with the shorter `/u`,
  on a `memchr` row that does not read the pin) and 1 loses it
  (`slack-webhook-url`: its 8-position window holds no exact stretch of
  two, and its `offset-set` row does not read the pin). **0 `dfa_pfs[]`
  selections move**: both `run-pinned` artifacts keep the same offset, the
  same scan byte and a stretch equal to today's run, so the row's predicate
  and its program read the same values. **1 G1 verdict moves** (`a[bc]de`).
  The build's manifest confirms these against emitted artifacts (§5.1).

**[K66]'s whole run** carries `whole_mask` (§2.3.4, `t[1]`). The no-match
proof stays a fact about the pattern.

**Stamps.**
- **`<PREFIX>_REQ_RUN`** gains a `/`-suffixed hex mask ONLY when masked:
  `"53454c454354@4/dfdfdfdfdfdf"`. Exact runs' text is unchanged. The
  stamp renders from the facts renderer (`facts.c:445`, D126 Q9), so the
  stamp and `--emit-facts`' `req_run` row change together.
  `req_whole_run` takes the same suffix.
- **`<PREFIX>_REQ_BYTE`** is the `req_byte` fact, per §2.3.3 cases (i) and
  (ii).
- **`<PREFIX>_REQ_WHY`**: round 0's "`none` on a masked mover is a defect"
  stands. The spec's invariant "`REQ_WHY "none"` iff `REQ_BYTE "none"`"
  becomes "iff `REQ_BYTE "none"` AND `REQ_RUN "none"`" (`tuning.md` §2.29,
  `match_api.md` §6.3). `union-select` reads `REQ_BYTE "none"`,
  `REQ_RUN "…/dfdf…"` and `REQ_WHY "emitted"`.

#### 2.3.6 The constants (D141) [r1 C7]

D141 is chartered and unscheduled. Its interim rule is that new estimation
or selection constants go into `PLACE` or carry their provenance inline.
`PLACE` is clskit's own struct. These are fact-layer selection knees, and
`limits.def` already holds that kind (`PCREC_MAX_REQ_RUN_EMIT`, "selection
knee"). So they are rows there, with the provenance in each row's `desc`,
checked by `tests/registry/limits_check.sh` (D107) and listed by
`--list-limits`:

| row | value | unit | kind | provenance (the row's desc) |
|---|---|---|---|---|
| `PCREC_MIN_REQ_RUN_BITS` | 16 | `bits` (a NEW unit token: `limits.def`'s header vocabulary, `limits.md` §3, `limits_check.sh`) | selection knee | RULED, not fitted. Today's exact floor (two bytes) restated in the ranking's own unit, so exact admission is unchanged (§2.3.7 class B: 0 counter-examples). Three caseless letters clear it and two do not, which matches every measured customer (4-6 letters, §7). Moving it takes a census plus a cell (D77). [r2 R2-C5] It is the necessary run's floor only; D127's `L >= 3` (the VM literal run, positions) is a separate floor with a separate consumer |
| `PCREC_MAX_REQ_RUN_POS_SET` | 2 | `count` | selection knee | RULED: the largest member set a run position may have, because every position must be a scan candidate and the emitted scan has two arms, one stream (`memchr`) and two (the pair leapfrog, O-55's measured form). A wider set is a third arm no cell asks for (D77) |
| `PCREC_MAX_REQ_RUN_EMIT` (existing) | 8 | `bytes` → **`positions`** | selection knee | its desc gains "positions: a masked window is 8 positions, compared by C1's row table". A `limits.md` hunk |

- **The pair's cost is not a constant.** It is the rate summed over the
  pair's two members: [r2 R2-C1] inside the extended PICK primitive for the
  scan member (cube candidates), and through `pcrec_find_seq_mass` over the
  window's members for the window. The 1:1 summing is the definition of hit
  density for a two-member scan, and it carries no fitted weight. Each NONE
  answer is its primitive's own (PICK: the rightmost; MASS: cardinality),
  and no reader tests the rate.
- **The `|set| <= 2` cutoff is `PCREC_MAX_REQ_RUN_POS_SET`.** Round 0 had
  it twice, as the admission predicate's `|set| <= 2` and the pick's
  candidate filter. Now it is one row, read in one place: the walk's
  position predicate, which the hull reads too.
- `PCREC_MAX_REQ_RUN_SCAN` is unchanged; it stores positions as it stored
  bytes.
- The `limits_check.sh` manifest count moves by 2. That is a reader found by
  grep (§4).

#### 2.3.7 The census: what the single ranking moves (compile-only, this lane)

**Instrument.** `docs/dev/optloop/s4/c3census/`:
- `proto.patch` is the r1 walk only: (T, K) positions in the two-member
  domain, the hull, the information ranking, `whole_mask` in
  `--emit-facts`. It is applied to a SCRATCH copy of main `92b8bbf0`,
  never committed under `src/`.
- `c3_census.py` compiles every corpus pattern (as written, through
  `--list-source`, with its `flags`/`encoding`) and every bench export at
  `--features all --emit-facts` under BASE (main) and PROTO, Mac,
  compile-only. Every compile is bounded by a 60 s `timeout`, and none
  fired.
- `c3_report.py` applies the floor and writes `c3_summary.txt`.
- PROTO's emitted C is not read. Its emitters still read T as exact.
- **[r2 R2-C3] Re-run for r2** (lane `s4rev2`, from main `af615d01`,
  serial, each compile under a 60 s `timeout`, none fired; BASE is main's
  own `build/pcrec`). `proto.patch` now also carries r2's fact half: the
  extended PICK primitive (cube candidates), the member-mass window,
  `req_byte`'s exact-member clause and the exact-stretch pin, with
  `run_pin` rendered `o` or `o:at+len`. The census now records PROTO's
  `req_run`, `req_byte` and `run_pin` beside its `req_whole_run`, so class B
  is checked on all four facts and classes A1/C report the pin. The bench
  side reads pcrec-bench's live exports, which grew by 4 compiled patterns
  since r1 (all four land in A0); every other count is r1's.

| class | corpus (3,898 compiled) | bench (321 compiled) |
|---|---|---|
| A0: no run before, none after | 3,363 | 212 |
| A0b: a masked run below the floor (not admitted) | 23 | 4 |
| **A1: no run before, masked run after** (round 0's population) | **15** | **8** |
| …of which the set is non-empty (S2's class: `REQ_BYTE` must stay the set pick) | 4 | 3 |
| **B: exact run before, the identical exact run after** [r2: and the identical window + `idx`, `req_byte` and `run_pin`] | **505** | **98** |
| B!: exact before, a DIFFERENT exact run, window, `req_byte` or pin after (would falsify the fact-level identity) | **0** | **0** |
| **C: exact run before, masked run after (the NEW mover population)** | **15** | **3** |
| …caseless (`-i` or `(?i`) | 1 | 1 |
| …the C4 shadow count: caseless AND the shadowing exact run was a 2-run | **0** | **0** |
| …no `K = 0xDF` position (hull or non-letter pair only) | 14 | 2 |
| …pinned today | 8 | 2 |
| …[r2] …a pin at the SAME offset after (the exact stretch) | **8** | **1** |
| …[r2] …the pin lost (no exact stretch of two in the window) | **0** | **1** (`slack`, `offset-set`: does not read the pin) |
| …`run-pinned` `dfa_pfs[]` row selected today | 2 | 0 |
| …[r2] …selection moves | **0** | **0** |
| …G1 verdict moves (`dominated` → `emitted`) [r2: predicted from the BASE artifacts' `RX_DFA_PREFILTER_OFFSETS`, §2.3.5] | **1** (`a[bc]de`) | 0 |
| A1 with a pin after [r2] | 0 | 0 |

**What the counts say.**
1. **The C4 shadowing is real but small in the corpus and the bench.** The
   critic's `(?i)union select 1,2` is not in either population.
   - The one bench case is `slack-webhook-url`: exact `://` (24 bits)
     shadows `COM/SERVICES/T`, 14 positions and 100 bits, cut to an
     8-position window.
   - The one corpus case is `(?i)x/1234`: exact `/1234` shadows
     `X/1234`, 47 bits.
   - **No caseless pattern in either population is shadowed by an exact
     2-run.** Round 0's additive rule cost nothing measured, which is why
     it looked free. The single ranking is still the one-mechanism answer
     (C4), and its cost is class C below.
2. **[r2 R2-C2] Exact-only artifacts keep their FACTS**: B! is 0 of 603.
   Every pattern whose winning run is exact gets today's whole run, and
   (r2) today's window and scan index, `req_byte` and `run_pin`, byte for
   byte. This census reads facts on the auto engine only; it is not a
   reading of emitted C. The C3 mover biconditional, **moved ⇔ `req_run`
   is masked** (§5.1), is therefore a PREDICTION from the facts, and the
   build's mover manifest is its byte evidence (auto and `--engine=vm`,
   the bench's four configs). Its population is A1 ∪ C: 41 here, against
   round 0's 23.
3. **Class C is mostly the S1 hull, not caseless text.** 16 of its 18
   cases have no `K = 0xDF` position:
   - `frank|fred` → `fr[ae]` (`fra/fffffb`);
   - `a[bc]de` → `a[bc]de`;
   - `foo(?:username|password|passphrase)bar` → `[de]bar`;
   - the six `^(a)…(i)(j|k)…$` recursion spellings → `abcdefghi[jk]`;
   - three utf8 emoji pairs (`(?:😀|😁)`).

   These are the general mechanism working: a one-bit alternation hull is
   more information than the exact run beside it. They are also the
   population r1 moved the pin on (10) and the 2 `run-pinned` selections.
   [r2 R2-C3] Under r2's exact-stretch pin, 9 of the 10 keep a pin at the
   same offset, 0 selections move, and 1 G1 verdict moves (§2.3.5).
4. **Utf8: no caseless non-ASCII mover.** A caseless non-ASCII letter is
   a pair at its continuation byte (`(?i)é` → `C3 [89|A9]`, 15 bits). But
   the walk never joins a run ACROSS such a character today. Every bench
   `utf8/ci-*` pattern yields its FIRST character's two positions only:
   - `ci-moskva` → `D0 [9C|BC]`;
   - `ci-greek-run` → `CE [91|B1]`;
   - `[Мм][Оо]` alone does the same.

   That is a pre-existing property of how the encoding lowering shapes a
   multi-byte class for the run walk, not something C3 adds. Every such
   pattern is A0b (below the floor), unchanged. Extending the walk across
   lowered multi-byte classes is a separate row with its own census, named
   here and not built. `ci-strasse` moves on its ASCII `TRA` (A1).
5. **Caveats.**
   - The corpus is read as written (`config`/`with` cascades are not
     applied), `wf_census.py`'s own scope.
   - PROTO is the walk, not the build: the build lane's mover manifest
     (§5.1) is the count of record, and these numbers are its prediction.
     A disagreement between the two is a finding against one of them.

### 2.4 Sites that keep their own form, with the reason (compare_stack §5's record, updated in the same change)

| site | why it keeps its form | what would move it |
|---|---|---|
| the island (`vm_isl_*`) | its words are singleton byte strings by its predicate (`vm_isl_single`), and its trie needs disjoint single-byte edges. A caseless island would need a trie over cubes; folding a node is unsound when its edges include a non-letter (`0x40 \| 0x20 == 0x60`). Its exact chains do take the run compare (§2.1) | a measured caseless keyword-alternation cell on the VM route. The only candidates are `altwide/ci-*`, which route DFA |
| the cursor rung's fixed-length `&&` chain (`vm_cursor_rep`) and the backward walk (`vm_rev_emit`) | S2a left both exact sites alone, and S4 keeps parity. A masked arm there needs the same emitter plus a cursor base. That is a small change with no measured population | a census of cursor/backward caseless bodies of length >= 3, plus a cell |
| the offset-set verify chain over cube offsets (`ofsk_emit_verify`'s `ofs_k<k>[...]` probes) | under `(?i)` the offset-k skip is mostly not selected at all (73.8% of producible walks have no invariant offset, `wordfold_census.md` §6). Where it is selected, contiguous cube offsets could be one masked word, but the population is uncounted | a census of offset-set artifacts with >= 3 contiguous cube offsets, plus a cell |
| `DFA_PF_MEMCHR`, `emit_attempt`'s `\n` | one byte, no verify (compare_stack §5) | — |
| `dfa_pfs[]` rows | §2.3.5: the pin is exact-only (`pcrec_run_pin`'s count-1 test plus r1's explicit conjunct). [r1] No masked run enters the table. The single ranking does move its pin INPUT on 10 artifacts and 2 selections (§2.3.7) | the offset-preference step, with a full panel |
| byte `$_span_match_caseless` | its K/T are run-time (S6) | S6's trigger |
| utf8 `$_span_match_caseless` | length-changing folds; not a byte cube | never (D23) |
| clskit's `is_ascii_fold_pair` | correct for any pair differing in bit 5 (the emitted `(c \| 0x20) == hi` does not need the letter conjunct). Making it a P2 reader is `[CLS-TREE]`'s D1 item, with no S4 customer | `[CLS-TREE]` touching the fold rows |

---

## 3. Deny flags, bits, stamps, the dial

The next free bit on main is **42** (`lib/pcrec.h:1038`, bit 41,
`--fast-or-fail`). All three bits below are `#define`s for bit 32's reason,
and all three are masked out of `rx_info.flags` (`strategy_denials`)
because none changes an answer. Each is one `src/core/axes.def` row, one
`--list-axes` predicate row and one `docs/spec/tuning.md` section (§2.37
onward, renumbered at landing if a round-1 sibling takes a number first,
Q11).

| bit | flag | macro | denies | activity stamp |
|---|---|---|---|---|
| 42 | `-fno-run-overlap` | `PCREC_NO_RUN_OVERLAP` | rows `words` and `overlap`. Exact compares are abi 55's `memcmp`; masked compares take `bytes` | `<PREFIX>_RUN_WORDS` (compares written by rows 1-2, both engines) |
| 43 | `-fno-lit-run-fold` | `PCREC_NO_LIT_RUN_FOLD` | cube positions in the VM run fact (§2.2). Runs are singleton-only, as at abi 55 | `<PREFIX>_VM_LIT_MASKED` |
| 44 | `-fno-req-run-fold` | `PCREC_NO_REQ_RUN_FOLD` | [r1] cube positions in the necessary-run walk (§2.3.1): the position bound drops from `PCREC_MAX_REQ_RUN_POS_SET` to 1, so the walk, its hull and its ranking are exactly abi 55's (byte equality, `8 × len`). A fact-level deny (D126 Q3): `req_run`/`req_whole_run` have nothing masked to find, for every consumer, and [r2] the pin's stretch and `a[bc]de`'s G1 verdict (§2.3.5) revert with it | `<PREFIX>_REQ_RUN`'s `/mask` suffix |

**Why three bits and not one (Q2).** D144 item 4 has batch-gate triage flip
flags rather than bisect. The three mechanisms have disjoint witness cells:
- bit 42: slack `://`, router `/user`, litrun;
- bit 43: forced-VM WAF;
- bit 44: `union-select` auto (and, under r1's single ranking, `slack-webhook-url`, whose `://` run becomes masked: §6.2).

One bit would make a regression on any of them a revert of all three.

**`-fno-lit-run` (bit 33) still denies the whole VM run, masked runs
included.** It is the outer switch and bit 43 the inner one. The recursion
identity gate (A) gains bits 42 and 43 to its excuse set, S2a's precedent
for `-fno-lit-run`.

**Each deny restores the abi-55 program except its stamp lines.** That is
what makes base/deny the noise floor (§6.1). The structural check proves it
per witness (§5.4).

**The dial (`opt_dial_design.md` §3, the PINNED CONTRACT, D103).** The policy
table gains three rows, all ON at every position. That is a ruled diff the
landing lane carries:
- a masked run is smaller than the chain it replaces;
- an overlap compare and `memcmp` are within a word of each other in size.

No row is a size/speed trade.

---

## 4. abi events and every reader (D76/D94)

**Three events, one per optimization commit (D144 item 5; Q1).**
- C1 (the run compare): 55 → 56.
- C2 (the VM masked run): 56 → 57.
- C3 (the caseless necessary run): 57 → 58.

Each number is "the next at landing", never a literal (the findings
precedent). C0 (P2's move) is byte-identical and carries no event.

**The reader recipe, run on the landing tree, not from this list:**

```sh
grep -rnE 'PCREC_ARTIFACT_ABI|ABI_EXPECT|abi[ :=(]*55\b|\(abi 55\)|"pcrec: this artifact \(abi' \
     src tests docs/spec lib cli scripts | grep -v '^docs/dev/'
```

Readers known at `c231ffc1`, a floor and not the list:
- `src/gen/emit_dfa.c:52` (`#define PCREC_ARTIFACT_ABI 55`).
- `tests/codegen/run_codegen_tests.sh` (`ABI_EXPECT=55`, plus the
  `[DD-14.FB]` narrative string's next transition).
- `docs/spec/match_api.md`:
  - §6's changelog: "is 55" → "was 55", plus a new entry stating the
    mechanism, the mover manifest and the invariants;
  - line 302, the shared block's mixed-abi `#error` text (D143);
  - line 2299, `rx_info.abi`'s sentence.
- `tests/codegen/run_recursion_identity.sh`: the (B) `FILEPIN` re-pin to
  the commit's own last `src/` change (the k73utf convention), and (A)'s
  excuse axes.
- `src/gen/CLAUDE.md` and `src/core/CLAUDE.md`, design-record entries.

**The D94 addendum: suites that move without citing the number.** Run them,
do not grep them:
- `make test-registry`: the `axes_registry_check` coverage pin grows by
  three triples.
- `make test-codegen`: `run_ir_listing.sh` `irsb` baselines (masked
  `compare` rows); the cpset-structure manifest (moved VM witnesses);
  `run_size_term.sh` and `run_facts_checks.sh` (`--emit-facts`'
  `req_run` row gains the mask).
- `make test-rxtsource`: `CENSUS_*`/`RUNSH_*` grow by the new corpus files.
- `make test-axes AXES="-fno-run-overlap -fno-lit-run-fold -fno-req-run-fold"`.
- The size log's tripwire, if a pinned witness moves.

**Spec hunks (D80), in the commit that changes the behaviour (C1/C2):**
- `tuning.md` §2.37-2.38, plus §2.31's lit-run text ("single-cube byte
  classes");
- `limits.md` §3.1's charge sentence;
- `match_api.md` §6.3's stamp catalogue (`RUN_WORDS`, `VM_LIT_MASKED`);
- `ir_listing.md` (the masked `compare` op);
- `compare_stack.md` §2/§5 (the D122 keep-it-true rule).

**[r1 C3] C3's readers of the necessary-run family, BY GREP (D94).** The
recipe is to run it on the landing tree. The list below is the floor it
printed at `92b8bbf0`:

```sh
grep -rnE 'pcrec_fact_req_run|pcrec_fact_req_whole_run|pcrec_fact_req_byte|pcrec_fact_run_pin|req_run\.|->whole\b|->whole_len|pcrec_req_window|pcrec_req_pick|pcrec_run_pin|pcrec_find_run_scan_index|pcrec_find_run_window_start|pcrec_emit_req_(byte_check|run_blocks)|req_admit\b' src cli lib
grep -rnE 'REQ_(BYTE|RUN|WHY)|req_(whole_)?run|req_byte' docs/spec tests
```

| # | reader | what it reads | C3 change |
|---|---|---|---|
| 1 | `src/facts/req.c` `rb_walk` and the `rn_*`/`rr_*` helpers | the run triple | (T, K) positions, hull, `rn_better` (§2.3.1) |
| 2 | `src/facts/facts.c:170-177` `pf_derive_req_walk` | `run.n >= 2` (THE FLOOR) | `info >= PCREC_MIN_REQ_RUN_BITS`; copies `whole_mask` |
| 3 | `facts.c:73-80` (the fact deny's empty value) | clears `whole`/`bytes` | clears both masks too |
| 4 | `facts.c:443-447` `pcrec_fact_render` (`req_whole_run`, `req_run`) → `--emit-facts` AND the `REQ_RUN` stamp (`emit_dfa.c:9129`, `pcrec_fact_stamp`) | hex + `@idx` | `/mask` suffix when masked (one renderer, D126 Q9) |
| 5 | `req.c:489` `pcrec_req_window` | `whole` | passes (T, K), copies `mask` (§2.3.3) |
| 6 | `req.c:519` `pcrec_req_pick` → `req_byte` → `REQ_BYTE` | `bytes[idx]` when a run shipped | only when `mask[idx] == 0xFF` [S2a] |
| 7 | `src/core/findings.c:500/526` the two run readers | byte arrays | (T, K) arrays; the scan index through the EXTENDED `pcrec_find_pick` (cube candidates), the window through one `seq_mass` over each window's members [r2 R2-C1] |
| 7a | `src/core/findings.c:413` `pcrec_find_pick` and its other caller `pcrec_find_set_pick` (`:454`) | byte candidates | [r2 R2-C1] a `care` array (NULL = bytes); NONE still `rightmost`, inside; the set pick passes NULL |
| 8 | `src/facts/kset.c:240` `pcrec_run_pin` | `bytes` vs walk singletons | [r2 R2-C3] pins the window's longest maximal EXACT sub-window (ties rightmost); `RunPin` gains `at`, `len`, `idx`; takes the byte-rate for `idx` (§2.3.5). r1's refusing conjunct is withdrawn |
| 9 | `emit_dfa.c:997` `req_run_tests` | `req_byte < 0` gate; two `ofs_test_run` sites | gate deleted; both sites masked [S4] |
| 10 | `emit_dfa.c:1055` `emit_req_run_check` | run bytes into the comment | a masked run's comment names its masked positions (emitted text: inside C3's abi event) |
| 11 | `emit_dfa.c:1123` `emit_req_set_rest` | `done[]` over the whole run | exact positions only [S2b] |
| 12 | `emit_dfa.c:1193/1208` `pcrec_emit_req_byte_check` | `b < 0` early return; run branch | `b < 0 && no run` |
| 13 | `emit_dfa.c:5683/5689` `us_run_pin`, `pf_run_applies_common` | pin, `bytes[idx]` | [r2 R2-C3] the scan is the PIN's: offset `pin.o + pin.idx`, byte `bytes[pin.at + pin.idx]`; the "model already tests it" question asks about the pinned sub-window. On an exact run `at = 0`, `len = r->len`, `idx = r->idx`: unchanged |
| 14 | `emit_dfa.c:5741` `ofs_test_of` | pin, `bytes` | [r2 R2-C3] the run term is the pinned sub-window (`bytes + pin.at`, `pin.len`, at `pin.o`), always exact; never sets `run_mask` |
| 15 | `emit_dfa.c:5812` `ofs_test_verifies_run` | pin, `bytes[i]` | [r2 R2-C3] G1's question stays "does the test refuse every window lacking the WHOLE run": every position `i` tested at offset `pin.o - pin.at + i` (which must be `>= 0`) by a byte or a term whose members all lie in the cube `(T[i], K[i])`. On an exact run that is today's `b == bytes[i]` |
| 16 | `emit_dfa.c:6352` `req_byte_dominated_by` | `len >= 2` | none (reads `run_verified`, row 15) |
| 17 | `emit_dfa.c:6374` `req_admit` | `req_byte < 0` → NONE | AND no run (§2.3.5) |
| 18 | `emit_dfa.c:8969` `<string.h>` decision | `req_admit` | none (reads the one derivation) |
| 19 | `emit_vm.c:13089/13156` the VM entry's two calls | — | none |
| 20 | `src/dump/axes_dump.c:695/709` `--list-axes` rows `req-byte`/`req-run` | stamp names, descriptions | `req-run`'s description ("contiguous literal bytes") gains masked positions; a new `req-run-fold` row |
| 21 | `ofs_test_emit_fn` (`emit_dfa.c:5981`) | `scan_byte >= 0` | [r2 R2-S2] re-keyed: `run_mask && run_mask[scan_k - run_o] != 0xFF` → the pair arm, tested FIRST; then the `memchr` arm. Every search inside the guarded loop [r2 R2-S1] (§2.3.4) |
| 22 | `ofsk_emit_verify` (`emit_dfa.c:5882`), the run term | `run_bytes`, `run_len` | [r2 R2-S2] `pcrec_emit_run_compare` with `run_mask`: masked in `t[0]` and in `t[1]` alike |
| 23 | `facts.c:466` `pcrec_fact_render` (`run_pin`) → `--emit-facts` | `o` | [r2 R2-C3] `o` for a whole-window pin (every exact run: unchanged text); `o:at+len` for a sub-window pin |

The test and spec readers that grep prints are in §5.4 (the stamp
cross-checks) and in the hunks below. The ones a grep at `92b8bbf0` names
that C3 MOVES:
- `tests/codegen/run_prechecks.sh:381`, check `[3.1w]`, asserts
  `REQ_BYTE "none"` ⇔ `REQ_WHY "none"` on every row. r1 makes it
  "⇔ `REQ_BYTE "none"` AND `REQ_RUN "none"`" (`union-select`'s shape).
- Its `[3.1r]`/`[3.6r]` expected-`REQ_RUN` tables are re-read for any
  pattern that becomes masked.
- `run_codegen_tests.sh`, `run_encoding_checks.sh`, `run_cpset_structure.sh`,
  `run_recursion_identity.sh`, `tests/axes/run_axes.sh`,
  `tests/findings/gen_adversarial.py` and
  `tests/findings/manifests/ship_weblog_movers.txt` each read `REQ_RUN`.
  Each is re-run, not re-read (the D94 addendum).
- `tests/registry/limits_check.sh`'s row manifest gains the two
  `limits.def` rows.
- **[r2 R2-C6] Four more, named:**
  - `tests/findings/manifests/ship_log_movers.txt` (746 `REQ_RUN` lines, the
    `log` bundle's mover manifest) is re-generated and re-read, like
    `ship_weblog_movers.txt`: a pattern whose run becomes masked changes its
    `REQ_RUN` text there.
  - `CHANGELOG.md` `[Unreleased]` gains C3's entry (the caseless necessary
    run, bit 44, the `REQ_RUN` suffix), as each optimization commit adds its
    own.
  - `tests/axes/run_axes.sh` gains a bit-44 group beside GROUP F
    (`-fno-req-run`): the cells where `-fno-req-run-fold` takes a masked
    run's no-match proof away and the axis gives up where the default
    answers NOMATCH (K66's shape, one fold narrower). The axes run at
    landing populates it; if it finds none, the group's header says so with
    the run's numbers rather than being absent.
  - `docs/guide/`: **none.** No guide chapter names `REQ_RUN`, `REQ_BYTE`
    or the necessary run (grep at `af615d01`); the guide points at
    `tuning.md` for stamps.

**[r1 C6] C3's spec hunks, each named:**

| file | hunk |
|---|---|
| `tuning.md` §2.27 | `REQ_BYTE`: "where §2.28's run shipped, the run's own scan member" becomes "where the run's scan member is EXACT"; the third "names the analysis" case (§2.3.3 (ii)). Facts emptied: unchanged |
| `tuning.md` §2.28 | the run is a run of POSITIONS (a byte or a two-member cube); the information ranking and `PCREC_MIN_REQ_RUN_BITS`; the hull; the stamp grammar `hex@idx[/mask]`; "`REQ_BYTE` is exactly `bytes[idx]`" made conditional on `mask[idx] == ff` |
| `tuning.md` §2.29 | the admission's first conjunct (no byte AND no run); the `"none"` iff sentence; K65's "what counts as already tested" = the run's EXACT positions; K66's whole run compared masked |
| `tuning.md` §2.30 | the pin is exact-only, stated (it was implicit); `-fno-req-run-fold` reaches the pin the way `-fno-req-byte` does |
| `tuning.md` §2.39 (new) | `-fno-req-run-fold`, bit 44: facts narrowed (not emptied) — `req_whole_run`/`req_run` lose their masked form; consumers listed per D126 Q3 |
| `match_api.md` §6.3 | the `REQ_BYTE`, `REQ_RUN` (suffix grammar, example) and `REQ_WHY` (`"none"` iff) entries |
| `findings.md` §4 (line 128's table) | the scan-member row: PICK over POSITIONS in reverse, cost = the position's member-set mass; the window row: MASS over positions. The rightmost-first rule is restated, not changed. "Every member is necessary" is restated for a pair: the run is compared whole at each hit of either member |
| `facts_listing.md` §`facts`, `value` column (line 95) | "a run as lowercase hex (with `@idx` …)" gains "and `/` + the per-position mask in hex where any position is not exact"; [r2 R2-C3] `run_pin`'s value gains the `o:at+len` form for a sub-window pin |
| `findings/design.md` §6.1/§6.2 (a design record, not `docs/spec/`) | [r2 R2-C1] the extended PICK signature and its cube-candidate note (§2.3.3) |
| `limits.md` §3 | two new rows (`PCREC_MIN_REQ_RUN_BITS`, `PCREC_MAX_REQ_RUN_POS_SET`), the new unit token `bits`, `PCREC_MAX_REQ_RUN_EMIT`'s unit `positions` |
| `table_contract.md` | **no hunk, with the reason.** The `--emit-facts` header and its column set do not change: the mask rides inside the existing `value` cell, by the one renderer the stamp shares (D126 Q9). A new column would be a second spelling of one value. The contract's HEADER TRUTHFULNESS check sees an unchanged header. The panel asked for "mask/pair columns". Round 0's stored `pair` field is dropped (§2.3.2), so there is no pair column to publish |
| `compare_stack.md` §5 | the pre-check's run compare is masked (C1's row table), now with two arms (one stream, the pair) |

---

## 5. Answer identity, ASan, sabotage

### 5.1 Answer identity, per commit

1. **Movers manifest.** Reuse `docs/dev/optloop/s1/s1_identity.py` and
   follow `s2a/s2a_movers.py`'s pattern. BASE is the previous commit, abi
   normalized. The populations are the bench capability patterns × 4 configs
   and every corpus pattern × {auto, `--engine=vm`}. Each commit's
   biconditional:
   - **C1:** moved ⇔ the artifact writes a compare at an overlap length.
   - **C2:** moved ⇔ the VM program writes a masked run.
   - **C3:** moved ⇔ `req_run` is masked. [r1] It is still a biconditional
     under the single ranking, because every artifact whose winning run is
     exact keeps its facts (§2.3.7 class B!, 0 of 603). [r2 R2-C2] That
     census is fact-level and auto-engine only, so it PREDICTS the
     biconditional; THIS manifest is its evidence, in bytes: it diffs the
     emitted artifacts (abi-normalized) over every corpus pattern under auto
     AND `--engine=vm`, and the bench capability patterns under all four
     configs, and its off-diagonal (an exact-`req_run` artifact that moved,
     or a masked one that did not) must be 0. The population is A1 ∪ C, and
     the census predicts 41 (23 + 18) over corpus+bench auto. The manifest
     is the count of record. It also lists, as named sub-populations, each
     matched against §2.3.7's list: [r2 R2-C3] the pins that MOVE or are
     LOST (§2.3.5), the 0 `run-pinned` selections that move, and the G1
     verdicts that move (`a[bc]de`, `dominated` → `emitted`).

   Each has 0 off-diagonal, as S2a's 1,081 / 4,891 did.
2. **The answer differential** (`tests/findings/b1_mover_answers.py`,
   reused) over every mover covers the span, every capture and the give-up
   surface, at every startpos, BASE vs NEW. [r1 S2] C3's classification is
   one table:

   | BASE → NEW | verdict |
   |---|---|
   | identical | pass |
   | give-up → NOMATCH | allowed, listed (the pre-check's only legal direction, D124 item 3) |
   | **NOMATCH → give-up** | **DEFECT**: the `done[]` class (S2b); fails the commit |
   | any change of span, capture, or match ↔ no-match | DEFECT (wrong answer, D144 item 3's disaster) |
   | give-up → match | DEFECT (a pre-check cannot create a match) |

   The NEW side runs at the corpus's own step budgets, so a NOMATCH that
   needed K65's set member to stay linear shows up as a give-up and not as
   a slow pass.
3. **The oracle corpus.** New `tests/litscan/caseless.rxt`, python
   `re`-verified (`verify_rxt.py`'s C3 tier). Gaps that need libpcre2
   marking are flagged. It covers:
   - masked runs at every `L` in 3..20 and at 31, 32 and 64;
   - mixed exact/caseless words, including a `0xFF` mask byte inside a
     masked word;
   - non-caseless cubes (`[jk]`, `[0-7]`, `(?s).`);
   - subjects with every case pattern;
   - near misses at every position;
   - subjects truncated inside the run at every length, which is P8's
     both-directions witness at the subject end.

   C3 adds `tests/litscan/reqcube.rxt`, covering:
   - a necessary caseless run present, absent, and present only in the
     other case;
   - present only across the scan member's upper/lower streams;
   - starting at `startpos`, and inside a lookbehind's span;
   - a run with an exact member (one stream) against all-letters (two
     streams).

   **[r1] The panel's counterexamples, as planned cells.** Each block runs
   under `engine auto` and again under `engine vm`. Python `re`
   (`re.ASCII`) verified every expectation below on 2026-10-03 unless the
   cell says otherwise.

   | block | pattern | cells | guards |
   |---|---|---|---|
   | S1 head, branch order A | `(?:S(?i:ab)\|(?i:sab))` | `m "sab" 0 3`, `m "SAB" 0 3`, `m "Sab" 0 3`, `m "xsAbx" 1 4`, `n "ab"`, `n "zab"` | the hull (S450) |
   | S1 head, order B | `(?:(?i:sab)\|S(?i:ab))` | the same six | order-independence |
   | S1 tail, order A | `(?:(?i:ab)S\|(?i:abs))` | `m "abs" 0 3`, `m "ABS" 0 3`, `m "abS" 0 3`, `m "xaBsx" 1 4`, `n "ab"`, `n "abz"` | the hull, tail arm |
   | S1 tail, order B | `(?:(?i:abs)\|(?i:ab)S)` | the same six | |
   | S1 exact-branch hull | `frank\|fred`; `a[bc]de` | `m "fred" 0 4`, `m "frank" 0 5`, `n "frx"`, `n "fre"`; `m "abde" 0 4`, `m "acde" 0 4`, `n "ade"` | the class-C mover shape (§2.3.7) |
   | S2b give-up witness (`features backrefs`, `budget steps=10000`, `encoding byte` and `utf8`) | `(x?)([a-z]+)+S\d(?i:select)\1` | `n` on `"a"×16 + "1select"`, `×17`, `×18`; `m "abcS1SeLeCt" 0 11`; **`gu steps` on `"a"×18 + "Sx1select"`** (the control: every necessary byte and the run present, so the budget really is reached, the K65 file's shape) | `done[]` (S451) |
   | S2b, the panel's exact witness | the same | `n` on `"a"×30 + "1select"` | **classified**: NOMATCH today (K65's `memchr('S')`); NOMATCH→give-up under round 0, which is the DEFECT. Its `n` expectation follows from absence alone (`S` is necessary and absent). Python backtracks exponentially at L = 30, and libpcre2's own required unit is the caseless `t`, which is present. So the build lane light-probes 10.46 (tailnet, one compile) and records whether it answers NOMATCH or a match-limit error, in the file's header, as `k65_precheck_whole_set.rxt` records its own. pcrec's answer is `n` either way |
   | S2a stamp | `(?i:select)\d+x` | `m "SELECT12x" 0 9`, `n "select12"`, `m "sElEcT1x" 0 8` | the answers; `REQ_BYTE "120"` is §5.4's |
   | S4 re-search | `(?i)select` | `m "selecX select" 7 13`, `m "SELECXSELECT" 6 12`, `m "xSelEcT" 1 7` | each first scan hit fails its verify. Under S449 the block stops advancing and the file's watchdog fires (a hang is the detector) |
   | S4 whole run, K66 site (`features backrefs`: VM, no DFA scan, a 12-position run, so `t[1]` exists) | `(x?)(?i:abcdefghijkl)\1` | `m "abcdefghijkl" 0 12`, `m "ABCDEFGHIJKL" 0 12`, `m "zaBcDeFgHiJkLz" 1 13` | S448: a whole run compared unmasked deletes the first and third |
   | **[r2 R2-S1]** empty and short subjects, pair arm | `(?i)select` (k* = 5); `(x?)(?i:abcdefghijkl)\1` (the K66 site, both blocks) | `n ""`, `n "s"`, `n "abc"`, `n "selec"`, `n "ELECT"`; `m "select" 0 6` (n = 6 = MAXK + 1, the first length that enters the loop); on the K66 witness `n ""`, `n "abcdefghijk"` (11, one short), `m "abcdefghijkl" 0 12` | the guard (S454: a search hoisted above the loop). Every subject shorter than the run never enters the loop, so a pre-loop search is the only way any of them reaches `memchr`; ASan/UBSan over this block is §5.2's |
   | **[r2 R2-S2]** the dispatch, lowercase | `(?i)select` | `m "select" 0 6`, `m "xselectx" 1 7`, `m "seLecT" 0 6` | S453 (the `memchr` arm tested first): it scans `T` only, so every subject whose scan position holds `t` is deleted. The uppercase cells above cannot see it |
   | **[r2 R2-C3]** the kept pins | `a[bc]de`; `(?i)x/1234` | `m "abde" 0 4`, `m "acde" 0 4`, `n "adde"`, `n "abd"`, `m "zzacdezz" 2 6`; `m "x/1234" 0 6`, `m "X/1234" 0 6`, `n "y/1234"`, `n "x/123"`, `m "--X/1234--" 2 8` | the answers through the kept `run-pinned` row; the row itself and G1's verdicts are §5.4's |
4. **The axes.** `make test-axes` on the three new flags. With the deny
   applied, each must be answer-identical over the whole corpus.

### 5.2 ASan/UBSan: the read-safety sweep

- The S1-1/S2a lesson is that a sweep compiled with inlined constant
  `memcmp` sees nothing. §0 item 5 reproduces that in isolation:
  `two.c`, zero `__asan_report_*` at `-O2`.
- The word rows are instrumented by construction: `one.c`, two
  `__asan_report_load_n`, one per word.
- So the sweep compiles every mover with
  `-fsanitize=address,undefined -fno-builtin-memcmp`. `memcmp` rows are then
  intercepted and word rows are checked inline.
- It runs with `-DDIFF_EXACT_SUBJECT` (each subject in a block of exactly
  its length) and `PREFIXES=1` (subjects ending inside a run).
- **[r2 R2-S1] The pair arm's short subjects are in the sweep.**
  `reqcube.rxt`'s empty- and short-subject block (§5.1) runs under it with
  `DIFF_EXACT_SUBJECT`, so a subject of length 0..5 sits in a block of
  exactly that length and any search past it is reported. The NULL-subject
  case (K27's own input, `s == NULL`, `n == 0`) is not a `.rxt` cell (the
  harness never passes NULL); it is §5.4's `[K27]`-shaped driver on the
  pair-arm witness, which runs under `make ubsan`/`make asan` because its
  script is in both suite lists.
- **The control must read RED on a planted over-read** before the sweep is
  believed. S442 (§5.5) is that plant, run once under the sweep. That is
  the "control red on 58/214" discipline `s2afix` restored.
- gcc-15 on x86 folding a constant-size `memcpy` into an instrumented load
  is BELIEVED, from the same GIMPLE folding. It is one line of the Linux
  block to confirm (§6.2 step 0).

### 5.3 The fold-agreement check's third consumer (the hard requirement)

`tests/backrefs/fold_agreement_check.c` gains two parts:

- **(b) in process.** For all 256 bytes `c`, `pcrec_cls_cube({c,
  pcrec_ascii_fold[c]})` must give `K = 0xDF` when `pcrec_ascii_fold[c] !=
  c`, and `K = 0xFF` otherwise, with `T = c & K`. This ties P2 to P1:
  compare_stack P2's "fold pairs must come out K = 0xDF". A sibling arm,
  shaped like `run_cls_fold_agreement.sh` and not in this file, runs P2's
  exact domain check over every class the corpus produces, with a
  population floor of half the measured count (D110).
- **(c) emitted.** `run_backref_diff.sh` §9 compiles a SECOND fixture beside
  `gen.c`: `-p rxk --engine=vm` of `(?i)` followed by all 256 bytes as
  `\xHH`, in order. That is one masked run of 256 positions, 32 words, with
  the last word at offset 248. For every position `p` and byte `j`, the
  check runs `rxk_match` on the run's own bytes with `subject[p] = j`. It
  must match iff `j == run[p]`, or `pcrec_ascii_fold[run[p]] == j`. That is
  65,536 ordered (position, byte) pairs.
  - The emitted mask (fold.c → `cls_casefold` → set → P2 → emitter) is one
    source. The table, read directly, is the other.
  - The fixture asserts `RX_VM_LIT_MASKED 1` and `RX_RUN_WORDS >= 1`, so
    the check cannot pass on a chain it was not meant to see. That is the
    K35 guard, `§9`'s own "carries no `rx_span_match_caseless`" shape.
- What the check cannot see: a sabotage of `fold.c` itself. It moves both
  sides, as today's §9 cannot see one either. The libpcre2 differential and
  the 52-byte shape assertion own that.

### 5.4 Structural checks (`tests/codegen/run_codegen_tests.sh`, `[OPT-LITSCAN S4]` blocks)

- **Every emitted word** (`<p>_w2/4/8(base + o)`) satisfies
  `o + W <= L`, with `L` read from the same compare's guard. Each word's
  constant is a string literal, never an integer literal: the endianness
  guard.
- **Per witness, each deny restores the previous commit's program**, by
  `diff` modulo the stamp lines:
  - `-fno-run-overlap`: `/user`, `://`;
  - `-fno-lit-run-fold`: `(?i)select`;
  - `-fno-req-run-fold`: `union-select`.
- **The pay-for-what-you-use directions:**
  - `xyz` is still `memcmp` (L = 3 exact → `overlap`; L = 4 → `memcmp`);
  - `(?i)select` takes `words`;
  - `[0-7]ab` takes `words` with one masked byte;
  - a word with an all-`0xFF` mask carries no `&`.
- **A masked necessary run reads `REQ_WHY` ≠ `none`,** and its pin reads
  `none` in `--emit-facts`. That is the dfa_pfs exclusion, read from the
  artifact.
- **[r1 S2a] `REQ_BYTE` is a `req_set` member or `"none"`,** on every
  artifact of the C3 mover manifest, read from `--emit-facts`' `req_byte`
  and `req_set` rows. Where `REQ_RUN` carries a mask, `REQ_BYTE ==
  bytes[idx]` holds iff `mask[idx] == ff`. This is the check S452 plants
  against. `(?i:select)\d+x` reads `REQ_BYTE "120"`.
- **[r1 S2b] On the no-DFA-scan route, K65's `rq_set` list contains every
  set member that is not an EXACT position of the whole run.** On
  `(x?)([a-z]+)+S\d(?i:select)\1` that means it contains `83` (`S`).
- **[r1 S4] A pair arm's emitted re-search condition reads
  `< pos + k*`** (a text check on the witness's block). Both
  `<p>_reqrun` and `<p>_reqrun_whole` carry the masked compare on the K66
  witness.
- **[r2 R2-S1] No search outside the loop.** On the pair-arm witness, every
  `memchr(` line of `<p>_reqrun` and `<p>_reqrun_whole` sits between the
  block's `while (pos + ` line and its closing brace (a text check; S454's
  detector). Beside it, the `[K27]` check (`run_codegen_tests.sh`, the
  existing NULL-subject driver) gains the pair-arm witness: `(?i)select`
  and the K66 witness compiled, `<prefix>_search(NULL, 0, 0, NULL)` run,
  `0` expected, under the sanitizer battery as today.
- **[r2 R2-S2] The dispatch, structurally.** On `(?i)select` the block
  carries TWO `memchr` calls with the constants `84` and `116` (`T`, `t`);
  on `a[bc]de`, whose masked pre-check scans the exact `d` (r2 census:
  `req_run` `61626465@2/fffeffff`), ONE `memchr` of `100` and a masked
  verify. A block with one `memchr` on an all-letter run is S453's shape.
- **[r2 R2-S3] The canonical form, on every artifact.** For every
  `req_run` and `req_whole_run` row of `--emit-facts` carrying a mask, over
  the C3 mover manifest and the whole corpus: `T[i] & ~K[i] == 0` and
  `popcount(K[i]) ∈ {7, 8}` at every position. The count of masked rows it
  read is printed and floored (half the manifest's masked count, D110), so
  the check cannot pass on an empty population.
- **[r2 R2-C3] The kept pins, read from the artifact.** `a[bc]de` and
  `(?i)x/1234` both read `RX_DFA_PREFILTER "run-pinned"`, `run_pin` `2:2+2`
  and `1:1+5` in `--emit-facts`, and `REQ_WHY` `"emitted"` and
  `"dominated"` respectively; and each one's `<p>_ofsskip` block equals the
  previous commit's, modulo the stamp lines (the prefilter program does not
  move).
- Each block is validated in the failing direction on a scratch rebuild
  before commit, as litf5 did.

### 5.5 Sabotage rows (the highest on main is S439; renumber at landing)

| id | row (file) | plant | expected detector |
|---|---|---|---|
| S440 | `cube-spill-unchecked` (`src/core/cpset.c`) | drop `pcrec_cube_of`'s exact domain loop (accepts a cube that spills) | P2 agreement arm (b) + corpus. **Re-aims S361** (`clskit_cube_accepts_noncube`), whose anchor moves with the function |
| S441 | `fold-mask-wrong-bit` (`cpset.c`) | the absolute-domain reader returns `care & ~0x10` for one-free-bit cubes | fold-agreement (c) + `caseless.rxt` |
| S442 | `run-word-overreads` (`runcmp.c`) | the last word at `L - W + 1`, with that byte's mask `0x00` (ANSWER-PRESERVING) | the §5.4 word-offset check (cheap). The ASan sweep with `DIFF_EXACT_SUBJECT` is its K27-style both-directions witness, and its control |
| S443 | `run-mask-word-swapped` (`runcmp.c`) | word 2 uses word 1's mask (mixed runs) | `caseless.rxt` mixed-word cells |
| S444 | `lit-run-fold-admits-noncube` (`cpset.c`, `pcrec_lit_run`) | admit any two-member class (`[ab]`) as a cube | `caseless.rxt` `[ab]` cells (answers change) |
| S445 | `req-cube-crosses-repeat` (`req.c`) | join a cube run across a min-0 repeat | `reqcube.rxt` + the C3 differential (deletes matches) |
| S446 | `pair-scan-one-stream` (`emit_dfa.c`, the pair arm) | drop the second stream (`T \| ~K`) | `reqcube.rxt` "present only in the other case" cells, on BOTH blocks (`<p>_reqrun` and `<p>_reqrun_whole`) |
| S447 | `req-pin-takes-masked` (**[r1 S3] `src/facts/kset.c` `pcrec_run_pin`**, not `prefix_k.c`). **[r2 R2-C3] re-aimed**: r1's conjunct is withdrawn ; the row moves to the run row's TERM (`emit_dfa.c` `ofs_test_of`) | the run term takes the whole window (`r->bytes`, `r->len`, at `pin.o - pin.at`) instead of the pinned stretch, so the prefilter compares T exactly at a pair position | `reqcube.rxt`'s kept-pins block (`a[bc]de`: the exact compare of `abde` deletes `acde`, `zzacdezz`) |
| S448 | **[r1 S4]** `whole-run-unmasked` (`emit_dfa.c` `req_run_tests`, the `t[1]` site) | build `t[1]` without `whole_mask` | `reqcube.rxt`'s K66 block (lowercase subject deleted) |
| S449 | **[r1 S4]** `pair-research-behind` (`emit_dfa.c`, the pair arm) | re-search bound `< pos` instead of `< pos + k*` | `reqcube.rxt`'s S4 block hangs and the watchdog fires |
| S450 | **[r1 S1]** `req-hull-keeps-left` (`req.c` `rn_common_head`) | the round-0 rule: compare T and keep `a`'s mask | `reqcube.rxt` S1 head, order A (`sab` deleted) |
| S451 | **[r1 S2b]** `set-rest-marks-masked` (`emit_dfa.c` `emit_req_set_rest`) | mark `done[]` at every whole-run position | `reqcube.rxt` S2b (`n` → `gu`: the DEFECT direction) |
| S452 | **[r1 S2a]** `req-pick-takes-pair` (`req.c` `pcrec_req_pick`) | return `bytes[idx]` whenever a run shipped | §5.4's `REQ_BYTE ∈ req_set` check (answer-preserving: no answer reads `REQ_BYTE` on a run route) |
| S453 | **[r2 R2-S2]** `pair-dispatch-memchr-first` (`emit_dfa.c` `ofs_test_emit_fn`) | test `scan_byte >= 0` before the pair predicate (r1's dispatch) | `reqcube.rxt`'s lowercase dispatch block (`(?i)select` on `"select"` deleted), and §5.4's two-`memchr` text check |
| S454 | **[r2 R2-S1]** `pair-search-above-guard` (`emit_dfa.c`, the pair arm) | search both streams once ABOVE the `while`, as r1 wrote it | §5.4's "no search outside the loop" text check (cheap); the ASan/UBSan sweep over `reqcube.rxt`'s short-subject block and the `[K27]` NULL-subject driver are its run-time witnesses |
| S455 | **[r2 R2-S3]** `cube-stores-upper` (`req.c`, the hull) | `T' = (Ta \| ~K') & 0xFF` (the upper member) | `rr_pos`'s internal error fires on the first hull it meets (the corpus's `frank\|fred`), and §5.4's `--emit-facts` canonical-form check if the constructor's refusal is also removed |

**Anchor population to re-aim, by grep on main, a floor**
(coding_guide §3.5):
- S228, S267, S278, S279, S285, S287, S293, S304, S320, S361 and S392 quote
  code S4 moves: `pcrec_emit_exact_compare`, `lit_byte`, `cube_of`,
  `req_run_tests`, `ofs_test_run`, `ofs_test_emit_fn`, `ofsk_emit_verify`
  and `is_ascii_fold_pair`.
- Each re-aim re-verifies its intent: S267 and S279 must now plant into a
  word row.
- C1 keeps columns at every site it does not rewrite (coding_guide §3.4).

---

## 6. Witness cells and the alpha timing protocol (D144 item 1)

### 6.1 The protocol

- **Box.** ubuntubudu (Ryzen 1600, gcc 15.2). The run goes through the
  executor channel (pcrecdev2) as an exact-command brief; no lane runs on
  the box itself (BOILERPLATE). Record load1, governor and turbo in the run
  header (`tests/bench/README.md`'s discipline). Every timed command runs
  under `taskset -c 2`, with load1 < 0.5 before each phase.
- **Three builds per commit.** BASE is the previous commit. NEW is the
  commit. DENY is NEW with its own flag. DENY's program equals BASE's except
  the stamp lines, verified by `diff` before timing (§5.4).
- **The noise floor is `BASE/DENY` per cell.** It is the same program, so
  the ratio is pure noise for that subject on that box (the
  `docs/dev/reseed/timing_mac.md` precedent). A `BASE/NEW` ratio inside it
  is a NULL.
- **The runner** is `docs/dev/optloop/cycle1_analysis.md` §0.1-0.5's
  `findall.c`/`clock.c`, with the subjects sha256-checked against the
  bench's manifest.
  - 5 launches round-robin across the three binaries, 5 passes each.
  - A cell is the median of the per-launch medians, in ns per subject byte.
- **Every twin is answer-checked first** with `docs/dev/optloop/waf/check.sh`:
  SAME lines, or the block stops.

### 6.2 The cells

**Step 0, x86 instruction evidence.** It owes `[WORD-FOLD]`'s gcc-15/x86 arm:
- `gcc -O1/-O2/-Os -S docs/dev/optloop/s4/spell.c`;
- `gcc -O2 -fsanitize=address -S` on `one.c`/`two.c`.

It records branch count, constant folding and ASan checks per function.
This is §1.4-§1.5's table for x86 gcc.

**C1, the exact `overlap` row:**

| cell | why it moves | expect |
|---|---|---|
| `wild-secrets-slack-webhook-url` thr, nocaps | the reqrun verify is `://`, L = 3, once per `/` hit: 39,095 hits over 1.38 MB, a per-hit-dominated cell (WAF §3.5) | faster, or null. A regression past the floor triggers Q3 |
| `router-prefix-order` thr | the offset-skip run term `/user`, L = 5 | the same |
| litrun `lit-l3`, `lit-l7`, `lit-l10`, forced VM, the match / first-byte-flip / last-byte-flip subjects | the VM run compare | the same |
| **controls, byte-identical:** `lit-l2`/`l4`/`l8`/`l16`/`l31`/`l40`; `keyword-prefix-order` (run `in`, L = 2) | no compare at an overlap length | in-window noise. The L-sweep's non-moving lengths are a free second floor |

Plus one twin: the `|` (fused) spelling of the slack and `lit-l7` artifacts,
made by `sed` on NEW (§1.5).

**C2, the masked VM run:**

| cell | why | expect |
|---|---|---|
| forced-VM `union-select`, `concat-sqli`, `dbnames` thr | per-position caseless chains (15 / 744 / 186 fold tests) become masked words | faster or null |
| synthetic `(?i)(?<=sel)ect` and `(?i)\bselect\b` forced VM, on the WAF `t-1m` subject | **the F4-class witness** (§6.3): a masked run on a per-position path that fails at its first byte almost always | a regression past the floor triggers the `lead-byte` row |
| `slack-webhook-url` auto **caps** (VM hybrid), `syslogbase-expanded` auto | the default-route population. The compare runs once per prefilter candidate | null (the control). [r2 R2-C4] **Read on C2's own commit only** (BASE = C1, NEW = C2, DENY = C2 + bit 43), never across C3: `slack-webhook-url` is a C3 mover (§2.3.7 class C), so after C3 lands its C1 and C2 cells and its C3 cell are three different artifacts. The control that survives C3 is `syslogbase-expanded` (§2.3.7 class A0: no run before or after), and any re-read of C2's control after C3 uses it alone |

**C3, the caseless necessary run:**

| cell | why | expect |
|---|---|---|
| `union-select` thr, nocaps and caps | the one measured customer | ≈ **0.43 ns/B** from base 0.718. PREDICTED from O-55's `ci_selectc` 0.4389, whose verify was a byte loop; the word verify is not slower |
| **[r1] `slack-webhook-url` thr, nocaps and caps** (NO LONGER a control; [r2 R2-C4] it is also no longer C2's control past C3, §6.2's C2 table) | class C: the exact `://` (24 bits) is outranked by `COM/SERVICES/T` (100 bits), windowed to 8 positions; the pin (offset 5) is lost; the selected row (`offset-set`) does not read it | faster or null. A regression past the floor is the single ranking's cost on a real cell: a new issue row, bit 44 the interim kill switch (D144 item 3). This cell is also C1's `://` witness, so C1's alpha is read BEFORE C3 lands, never across it |
| **[r1] `loglines/http-5xx` thr** | class C: exact `" HTTP/1."` (8 bytes) becomes the 12-position `" HTTP/1.[01]\" 5"` (95 bits), one pair; DFA, `memchr-bounded`, no pin today | null expected (the scan member is exact either way); the cell is there because it moves |
| controls, byte-identical under C3: `sleep-benchmark`, `dbnames`, `concat-sqli` (class A0: no run before or after); `loglines/stack-frame`, `kv-quoted` (class B: the same exact run) | — | noise |
| `union-select` srch | a short subject: the F1/F6 per-call-constant risk | within the floor, or a regression row |

### 6.3 The F4-class risk: first-byte-then-rest?

**F4.** S2a's 2-byte `memcmp` on a per-position failing path measured +30%
(`asr-lb-fixed`). F5's floor of 3 is the ruled response.

**What S4 changes on such a path.** A masked run is `bounds + load W + and +
cmp + branch` before it exits. The byte chain it replaces is
`bounds + load 1 + or + cmp + branch`. That is the same instruction count on
the failing path, and §1.6's chain-vs-words scratch row ties (0.635 vs
0.620).

**Why a lead-byte row is not built now.** It would add one test on the
success path and save nothing on the failing one. And F4 itself was not
predicted by instruction counts.

**Its slot is reserved (§1.3), with its trigger:** the C2 F4-class witness
regresses beyond its noise floor. Under D144 item 3, that regression is a
new issue row with bit 43 as the interim kill switch, not a revert.
`asr-lb-fixed` itself is NOT a mover: a 2-byte run is under the floor.

---

## 7. Census (counts, this lane, `build/pcrec` at `c231ffc1`)

`docs/dev/optloop/s4/census.py` compiled every pcrec-bench
`bench/*/patterns/*.rx` export (read-only; `-e utf8` for the utf8 set) under
`--features all -p rx`, at default selection and at `--engine=vm`.

| | auto | `--engine=vm` |
|---|---|---|
| compiled / refused | 317 / 22 | 318 / 21 |
| artifacts with a P4 compare at an overlap length (C1 movers) | **55** | **92** |
| artifacts with a VM fold-pair test `(\| 0x20) ==` (C2 candidates) | **2** (`slack-webhook-url`, `syslogbase-expanded`) | **17** |
| P4 compares by L (auto) | L2 21, L3 73, L4 52, L5 24, L6 8, L7 3, L8 21, L10 1, L11 2 | — |

Forced-VM artifacts with at least 3 fold tests:

| artifact | fold tests |
|---|---|
| `altwide/ci-256` | 1,842 |
| `concat-sqli` | 744 |
| `dbnames` | 186 |
| `slack` | 28 |
| `union-select` | 15 |
| `sleep-benchmark` | 14 |
| `syslogbase-expanded` | 12 |
| `syntax/mod-i` | 3 |
| `syntax/mod-r` | 3 |
| `utf8/ci-ascii-control` | 3 |
| `utf8/ci-strasse` | 4 |

**OWED to the build lane:** the corpus census (every `.rxt` pattern ×
{auto, vm}) for all three commits. [r1] The C3 cube-run census is now
TAKEN, at the fact level, by this revision (§2.3.7, `c3census/`). The
build lane's mover manifest confirms it against real artifacts. `wordfold_census.md` §2 bounds the C3
corpus population: 0 of the corpus's 48 `(?i)` patterns has a run >= 4, and
7 of the bench's 12 do. So C3's corpus movers will be few, and its witnesses
are bench patterns. The build lane must commit them as corpus cells
(`reqcube.rxt`) rather than rely on the bench (the scenario-asymmetry lesson,
`wordfold_census.md` §7).

---

## 8. Change size and the commit plan

| commit | contents | src lines (est.) | abi |
|---|---|---|---|
| **C0** | `pcrec_cube_of`/`pcrec_cls_cube` in `cpset.c`; clskit's `cube_of` becomes a caller; fold-agreement part (b); S440 (S361 re-aimed) | +90 / −40 | none (zero movers by `cls_identity.py` + `emit_sweep.py`) |
| **C1** | `src/gen/runcmp.c`/`.h` (rows, helpers, emitter); P4's three callers re-pointed and `pcrec_emit_exact_compare` retired; the prologue's helper decision; bit 42 + axes row + `--list-axes` + `RUN_WORDS`; tuning §2.37; structural checks; S442/S443; litrun cells at L 3..20; P4 anchor re-aims | +420 / −30 | +1 |
| **C2** | `pcrec_lit_run` cube admission; `vm_lit` takes `PcrecRun`; bit 43 + `VM_LIT_MASKED`; listing op; tuning §2.38 + §2.31 + limits §3.1; `caseless.rxt`; fold-agreement part (c); S441/S444; recursion identity (A) excuse | +160 / −20 | +1 |
| **C3** [r1, r2] | `req.c`: (T, K) positions in the ONE triple, the hull, `rn_better`, `rr_pos`'s canonical-form refusal [r2 R2-S3]; the floor at `pf_derive_req_walk`; `ReqRun`'s two mask arrays + `pcrec_req_run_masked`; [r2 R2-C1] `pcrec_find_pick`'s cube candidates and the two `findings.c` run readers over (T, K); `pcrec_req_pick`'s exact-member clause; [r2 R2-C3] `pcrec_run_pin`'s exact stretch, `RunPin`'s `at`/`len`/`idx` and their emitter readers, `run_pin`'s `o:at+len` render; `req_admit` + its two restating early returns; `done[]`; both `ofs_test_run` sites masked and `ofsk_emit_verify`'s run term masked [r2 R2-S2]; the pair arm with its re-keyed dispatch and every search in the loop [r2 R2-S1/S2]; `REQ_RUN`/`req_whole_run` suffix; two `limits.def` rows + the `bits` unit; bit 44 + its `run_axes.sh` group; the spec hunks of §4, the `findings/design.md` §6.1/§6.2 hunk and CHANGELOG; `reqcube.rxt` (§5.1's planned cells); S445-S455 | +340 / −30 (r2 adds the cube PICK, the stretch pin and its readers, and the in-loop pair arm) | +1 |
| (C4) | `[FINDINGS.B4]`: bigram + `run-rarity` with C6 as its first reader. Its own lane and its own commit (Q7) | — | +1 if the pick moves |

**Totals:**
- ~1,000 `src` lines net;
- ~1,800-2,400 with tests, spec and CLAUDE.md;
- 8 sabotage rows and ~11 re-aims;
- 3 abi events.

C3 is the largest and the riskiest: it touches P7 and a core fact. It is
last, so C1 and C2 can alpha-accept and close on their own (D144) if C3
needs a revision.

**Validation the build lane owes.** Each commit runs:
- `make strict`;
- `make test-codegen`, `test-registry`, `test-rxtsource`, `test-litscan`;
- the movers manifest and the differential;
- the ASan sweep, with its red control first;
- the axes subset;
- mech rows by single-row runs.

Then comes the alpha block (§6), and `make test` once per commit as the
alpha's other half. The full battery is the batch gate's.

---

## 9. The lenses

| lens | reading |
|---|---|
| specific vs general | General. Any one-cube class joins the VM run (C2), and any class of at most two members that is a cube joins the necessary run (C3, r1: every position must be a scan candidate), with no caseless special case. The alternation hull is the same rule on both branch orders and on exact branches. One compare function serves every run site of both engines. The exact arm is the `K = 0xFF` case of the same rows, and the exact run is the `K = 0xFF` case of the one ranking |
| core vs derived | P2 and the cube runs are core facts with no prior read. The run pick and the scan member are derived, and read the prior through the accessor (D126 Q4 NONE answer) |
| applicable vs assumption-changing | [r1, r2] Applicable, with one assumption changed and counted. Every artifact whose winning run is exact keeps its facts (0 of 603 differ at the fact level; the bytes are the manifest's to show, [r2 R2-C2]). Additive admission is withdrawn (C4): a masked run now outranks an exact one when it carries more information, which moves 18 exact-run artifacts. [r2 R2-C3] Their pins keep their offsets (9 of 10; the tenth is on a row that does not read it), 0 `dfa_pfs[]` selections move and 1 G1 verdict does. `dfa_pfs[]`'s shape is untouched |
| fits the architecture vs refactor | Fits. A new shared file in `src/gen/` (clskit's precedent) and widened fields; no restructuring |
| D124: a question both emissions share? | Yes. The compare is one table (`pcrec_runcmp_rows`), used by both emitters; the caseless pre-check is one text on every route. The engine appears only in which sites call |

---

## 10. Questions for the manager

1. **One abi event or three?** The row's disposition says "S4's own abi
   event". D144 item 5 (later) puts the bump with each optimization's own
   commit. **Recommendation: three** (C1, C2, C3), so each alpha cell
   attributes one mechanism and each commit can close its row alone.
2. **Three deny bits (42, 43, 44) or fewer?** **Recommendation: three.** The
   witness cells are disjoint (§3). One shared bit would make batch-gate
   triage a revert of all three. Bits are cheap; the cost is one axes run
   each.
3. **If C1's exact `overlap` row reads null or worse on its cells (§6.2),
   does it ship?** **Recommendation: no.** The row is then not built, or
   built denied-by-default, and exact runs stay `memcmp`. The one-emitter
   property holds either way, because the same function writes both rows.
   §1.6's scratch probe already contradicts §11 in a second loop shape, so
   the 5.6-7.6% should be treated as unproven, not as owed.
4. **Does C3 need D122 addendum 4 item 3's FULL panel?** Round 0 asked for
   a light panel, ruled light, and that panel held C3 (the r1 review).
   - **[r1, revised] The shape question, re-argued at the fact layer.**
     `dfa_pfs[]`'s rows, predicates, emitters and selector are unchanged,
     and the pin's site (`pcrec_run_pin`) gains only a conjunct that
     REFUSES. But the single ranking (Q5, revised) moves the table's INPUT
     on a counted population:
     - 10 pins are lost;
     - 2 corpus artifacts move from `run-pinned` to the next row;
     - the same 2 move from G1 `dominated` to `emitted` (§2.3.5, §2.3.7).
   - Round 0's premise, "every existing selection is unchanged", is
     therefore false for those 2.
   - **Recommendation: a SECOND light round, not the full panel**, with two
     lenses:
     - answer soundness of the hull and the pair arm (the new code paths);
     - selection semantics: are 2 moved selections, with no bench cell, an
       acceptable price for one ranking, against the alternative of keeping
       the exact run wherever it is pinned?
   - The latter would be a second admission rule keyed on a downstream fact,
     which is the C4/C1 class this revision removes. I recommend against it,
     and name the trigger for revisiting: a measured regression on a
     `run-pinned` artifact that C3 moved.
   - The full panel stays reserved for the offset-preference step, where a
     masked run ENTERS `dfa_pfs[]`.
   - **[r2] Ruled: the second light round ran** (s4r2a soundness, s4r2b
     selection) and held the hull. r2 applies its nine findings. With the
     exact-stretch pin (R2-C3) the "2 moved selections" this question
     weighed are 0 (§2.3.7), so the selection-semantics trade it asked about
     no longer arises; what remains is 1 G1 verdict (`a[bc]de`,
     `dominated` → `emitted`), which is the ranking's intent (§2.3.5).
     r2 does not change the shape (§R2), so the review's "no third round
     unless r2 changes the shape again" applies.
5. **Additive admission. [r1] OVERTURNED by the panel (C4), accepted.** Round
   0 recommended consulting a cube run only where no exact run of length
   >= 2 exists. The panel showed it defeats the caseless run
   (`(?i)union select 1,2`, `(?i)select.*from 1=1`) and spells the floor
   twice.
   - r1 has ONE ranking (`Σ popcount(K)`, exact = `K` 0xFF) and ONE floor
     (`PCREC_MIN_REQ_RUN_BITS` = 16).
   - The census (§2.3.7): the shadowing it fixes is 2 artifacts over
     corpus+bench (`slack`, `(?i)x/1234`). No caseless pattern there is
     shadowed by an exact 2-run.
   - The new mover population is 18 exact-run artifacts, 16 of them
     through the alternation hull rather than caseless text.
   - Exact-only artifacts keep their facts (0 of 603; [r2 R2-C2] a
     fact-level census, the manifest is the byte evidence). So C3's movers are
     still an exact biconditional (moved ⇔ masked), just a larger one.
6. **The run pick's NONE answer:** cardinality (`Σ popcount(K)`), which
   picks `select` (×1.64 on `union-select`, still behind re2), against the
   letter argmin, which picks `from` (×2.09 on the bench, and wrong in
   deployment). **Recommendation: cardinality.** It is the NONE answer
   `findings/design.md` §6.2 already names, it is deployment-sane, and it
   is spelled once (D126 Q4).
7. **`[FINDINGS.B4]`'s data half:** in C3's commit, or the next one?
   **Recommendation: the next commit, in the same round.** Then S4(a)'s
   alpha measures the mechanism and not the data, and B4 lands with its
   first reader (R2). Frank's option (c), "lands WITH S4", is honoured at
   round grain.
8. **The cube-run floor in C3. [r1] Subsumed by the one floor (C4).**
   `PCREC_MIN_REQ_RUN_BITS` = 16, in `limits.def` with its provenance
   (§2.3.6), replaces round 0's two floors (exact 2 positions, cube 3).
   - In positions it admits three caseless letters (21 bits) and every exact
     run admitted today, and refuses two caseless letters (14) and a letter
     beside one exact byte (15). That is round 0's recommendation, restated
     in one unit.
   - 27 masked runs over corpus+bench fall below it (§2.3.7 A0b).
   - Lowering it is still a census plus a cell (D77).
9. **The VM masked run (C2) has no losing bench cell.** Its witnesses are
   forced-VM WAF cells and synthetic per-position cells, and the default
   route carries it on two bench artifacts, both already won or
   prefilter-answered. **Recommendation: build it in S4 anyway.** It is the
   same emitter with the mask on (the one-primitive ruling), it shrinks
   programs (forced-VM `concat-sqli`'s 744 per-byte fold labels become a few
   words per run), and
   its regression risk is fenced by bit 43 and the F4 witness. If the
   manager reads D77 strictly, C2 is the one commit to hold until a VM-route
   caseless cell appears.
10. **Spelling:** the early-exit `&&` (measured faster than the wide load,
    §10.2, and faster than `|` in §1.6's scratch). The fused `|` spelling
    is an alpha twin, not a row. **Recommendation: yes.** If the x86 twin
    shows `|` faster beyond the noise floor, the landing swaps the row text,
    with no new axis.
11. **Bit and section numbers:** 42-44 and tuning §2.37-2.39 are the next
    free on main. Round-1 siblings (`[OPT-HYB-RESEED-XCALL]`, `[SEL-COST]`)
    may also claim bits and sections. **Recommendation: assign at landing
    order.** The landing lane takes the next free numbers at its merge and
    re-greps its readers, the findings design's "the next number at
    landing" rule.

---

## R1. Disposition of the light D6 panel (`docs/dev/reviews/2026-10-03-r1-litscan-s4-c3.md`)

Lane `s4rev` (opus), 2026-10-03, from main `92b8bbf0`. Design only, nothing
under `src/`. Each disposition is marked in place as `[r1 <id>]`.

| # | sev | finding | disposition | where |
|---|---|---|---|---|
| S1 | HIGH | alternation head/tail compared T and kept the left mask: order-dependent, unsound | **FIXED** as asked. The cube hull `K' = Ka & Kb & ~(Ta ^ Tb)`, `T' = Ta & K'`, symmetric, stopping at the first position outside the domain. Both counterexamples are planned cells in both branch orders, head and tail; sabotage S450 | §2.3.1, §5.1, §5.5 |
| S2 | HIGH | (a) `req_pick` returned a T byte; (b) `done[]` marked T values: NOMATCH → give-up | **FIXED** as asked. (a) A run byte only from an exact scan member, else the set pick, with `REQ_BYTE`'s two cases stated against the emitted scan. (b) `done[]` marks only `K == 0xFF` positions. The differential's table classifies NOMATCH → give-up as a DEFECT. The witness (and its L = 16..18 python-verifiable twins plus a `gu` control) is a planned cell; S451, S452 | §2.3.3, §2.3.5, §5.1, §5.4, §5.5 |
| S3 | LOW | the pin is `pcrec_run_pin` in `kset.c`, not `prefix_k.c` | **FIXED**: real site named. One explicit refusing conjunct (`pcrec_req_run_masked`), argued sound-and-redundant except for a walk-proves-T edge, where it is a lost opportunity. S447 re-aimed | §2.3.5, §5.5 |
| S4 | LOW | the pair arm's re-search bound; both `ofs_test_run` sites need the mask | **FIXED**: re-search iff hit `< pos + k*`, with the hang mechanism spelled out. `t[0]` and `t[1]` carry `mask`/`whole_mask`; S448 (the unmasked whole run) and S449 (the hang) | §2.3.4, §5.1, §5.5 |
| C1 | HIGH | a second pick-a-byte and window rule | **FIXED** as asked. `pcrec_find_run_scan_index`/`_window_start`/`pcrec_req_window` take (T, K). Cost is the position's member-set MASS. One tie rule (rightmost) and one NONE answer (rightmost), so exact runs are byte-identical. Round 0's "exact first" tie is withdrawn: under a rate it is a consequence of the cost, under NONE it is not applied (it would have re-created R13 under utf8) | §2.3.3 |
| C2 | HIGH | stale "dfa_pfs[] untouched" | **FIXED, and the conclusion CHANGED.** The shape is untouched. Under the single ranking 10 pins are lost and 2 corpus selections move (`run-pinned` → next row). Q4 re-recommends a second LIGHT round with a selection-semantics lens | §0 item 7, §2.3.5, §10 Q4 |
| C3 | HIGH | reader list incomplete | **FIXED**: 21 code readers and the test readers by grep, with the recipe. `req_byte` for a pair scan is defined (§2.3.3 (ii)) | §4 |
| C4 | HIGH | additive admission defeats the caseless run; two floors | **FIXED as asked, overturning Q5.** One ranking (`Σ popcount(K)`), one floor (`PCREC_MIN_REQ_RUN_BITS` = 16, `limits.def`). Census: the shadow count of caseless patterns behind an exact 2-run is **0** over corpus+bench (2 shadowed in all: `slack`, `(?i)x/1234`). The single ranking adds **18** exact-run movers (16 via the hull), and exact-only artifacts stay **byte-identical (0 of 603)** | §2.3.1, §2.3.7, §10 Q5/Q8 |
| C5 | MED | two parallel triples | **FIXED**: one triple, one key. Round 0's `pair`/`masked` stored fields are dropped for a derivation and one accessor | §2.3.1, §2.3.2 |
| C6 | MED | spec hunks not named | **FIXED**: 11 hunks named. `table_contract.md` has **no hunk, with the reason**: the header and column set are unchanged and the mask rides in the `value` cell by the shared renderer; the pair column does not exist because the `pair` field was dropped | §4 |
| C7 | LOW | D141 constants | **FIXED**: two `limits.def` rows with provenance (`PCREC_MIN_REQ_RUN_BITS`, `PCREC_MAX_REQ_RUN_POS_SET`), plus `PCREC_MAX_REQ_RUN_EMIT`'s unit → `positions`. The pair cost is the existing MASS primitive, not a constant | §2.3.6 |

**Shape changes beyond the fixes (they decide a second round):**
1. **The position domain is narrowed** to a byte or a two-member cube
   (`PCREC_MAX_REQ_RUN_POS_SET`), from round 0's any cube. This follows
   from C1 + C4: with one ranking, a run with no scannable member could
   outrank a scannable exact run, and then decline it. With the narrowed
   domain every position is a scan candidate and no second predicate
   exists. `K = 0`/`[0-7]` positions leave the necessary run. They stay in
   C2's VM run.
2. **The single ranking reaches `dfa_pfs[]`'s inputs.** That is 10 lost
   pins, 2 moved selections and 2 G1 verdicts on corpus artifacts. Round 0
   had none by construction.
3. **The S1 hull makes exact-branch alternations masked movers**
   (`frank|fred` → `fr[ae]`). It is general and sound, and it is most of
   class C.

The mechanism's own parts are unchanged from round 0: the walk-level
fact, the pair-leapfrog scan, P7's one conjunct, bit 44, the stamps'
suffix grammar and C3's position as the last commit.

---

## R2. Disposition of round 2 (`docs/dev/reviews/2026-10-03-r1-litscan-s4-c3.md`, "Round 2")

Lane `s4rev2` (opus), 2026-10-03, from main `af615d01`. Design only,
nothing under `src/`. Each disposition is marked in place as `[r2 <id>]`.
The census was re-run (`c3census/`, serial, compile-only, every compile
under a 60 s `timeout`, none fired).

| # | sev | finding | disposition | where |
|---|---|---|---|---|
| R2-S1 | HIGH | pair-arm pre-loop searches outside the K27 guard: wrapped length, `memchr(NULL, c, 0)` | **FIXED** as asked: no search above the loop. A `fresh` flag makes the first iteration search both streams, every search under `pos + maxk < n` (the emitted block is written out). Empty- and short-subject `reqcube.rxt` cells (n = 0..5 on `(?i)select`, 0 and 11 on the K66 witness); the ASan/UBSan sweep runs them at exact subject length; the `[K27]` NULL-subject driver gains the pair-arm witnesses; a text check that every `memchr(` sits inside the loop; S454 plants the hoisted search | §2.3.4, §5.1, §5.2, §5.4, §5.5 |
| R2-S2 | MED | dispatch trap: `scan_byte >= 0` is always true, so the `memchr` arm wins and scans `T` only | **FIXED** as asked: one ordered dispatch, `run_mask && run_mask[scan_k - run_o] != 0xFF` → the pair arm FIRST, then `memchr`, then the unreachable failure. S453 plants the old order; its detector is a lowercase `reqcube.rxt` block plus a two-`memchr` text check. `ofsk_emit_verify`'s run term reads `run_mask` through C1's `pcrec_emit_run_compare`, in `t[0]` and `t[1]` alike | §2.3.4, §4 rows 21-22, §5.1, §5.4, §5.5 |
| R2-S3 | LOW | unstated invariant `T & ~K == 0` | **FIXED**: stated (T is the lower member; what breaks if not). Enforced at the walk's one position constructor `rr_pos` (internal error, never a silent normalization) and checked from outside by an `--emit-facts` pass over the manifest and the corpus with a population floor. S455 plants an upper-member hull | §2.3.1, §5.4, §5.5 |
| R2-C1 | HIGH | the pair pick needed a reader-side `rate == NULL` branch | **FIXED** as asked: `pcrec_find_pick` takes cube candidates (`care`, NULL = bytes), cost = the rate summed over members, NONE = `rightmost` inside the primitive. Existing readers byte-identical (set pick passes NULL; an exact run's mask is all `0xFF`); the window lists members into one `seq_mass` call. `findings/design.md` §6.1/§6.2 hunk named for C3's commit (a kind row EXTENDED, no new kind). `bar(?i:x)` under utf8/NONE (pair at `X` over the exact `r`) stated as accepted, with its trigger | §2.3.3, §2.3.6, §4 rows 7-7a |
| R2-C2 | MED | "0 of 603 byte-identical" verified the run FACT only | **FIXED**: reworded as facts everywhere it appeared (§2.3.1, §2.3.7, §5.1, §9, §10 Q5). r2's census widens the fact check to window + `idx`, `req_byte` and `run_pin` (still 0 of 603). The §5.1 mover manifest is the byte evidence, over corpus auto + `--engine=vm` and the bench's four configs | §2.3.1, §2.3.7, §5.1, §9, §10 |
| R2-C3 | MED | two sound pins dropped (`a[bc]de`, `(?i)x/1234`) | **FIXED: the exact positions are pinned.** r1's refusing conjunct is withdrawn; `pcrec_run_pin` pins the maximal exact stretch around the window's rarest exact byte (one PICK call), `RunPin` gains `at`/`len`/`idx`, and G1's "verifies the run" is read over cubes. **Census:** both witnesses keep `run-pinned` (`run_pin` `2:2+2`, `1:1+5`: the same offsets and stretches as today's runs); of r1's 10 lost pins 9 keep the same offset and 1 (`slack`, `offset-set`, a row that does not read it) is lost; **0 selections move** (r1: 2); **1 G1 verdict moves** (`a[bc]de` → `emitted`, offset 1 untested; `(?i)x/1234` stays `dominated`). Mover counts unchanged: A1 ∪ C = 41. Kept-pin cells in `reqcube.rxt`; S447 re-aimed to the run term; bit 44 the interim kill switch | §0 item 7, §2.3.5, §2.3.7, §4 rows 8, 13-15, 23, §5.1, §5.4, §5.5 |
| R2-C4 | MED | the slack control is inconsistent | **FIXED** with an ordering caveat: C2's slack control is read on C2's own commit only, never across C3 (`slack` is a C3 mover); `syslogbase-expanded` (class A0 under C3) is the control that survives C3 | §6.2 |
| R2-C5 | LOW | two floors, not one | **DOC**: said plainly. `PCREC_MIN_REQ_RUN_BITS` is the necessary run's floor (bits, one consumer); D127's `L >= 3` is the VM literal run's (positions, `pcrec_lit_run`) | §2.3.1, §2.3.6 |
| R2-C6 | LOW | four readers missing from §4 | **FIXED**: `ship_log_movers.txt` (746 `REQ_RUN` lines) re-generated; a CHANGELOG `[Unreleased]` entry; a bit-44 group in `tests/axes/run_axes.sh` (stated empty with numbers if the run finds none); `docs/guide/`: none (grep at `af615d01`) | §4 |

**Did the shape change again? No.** The position domain (a byte or a
two-member cube), the hull, the one ranking and the one floor, the pair
arm's two streams and its re-search bound, P7's conjunct, bit 44, the stamp
grammar and C3's place as the last commit are r1's. What r2 changes:
- **fixes inside the same parts**: where the pair arm searches (R2-S1),
  how its arm is chosen (R2-S2), one stated invariant (R2-S3), the words of
  a claim (R2-C2), a control's reading order (R2-C4);
- **one primitive extended, not added** (R2-C1): PICK takes cube
  candidates, which is how r1's own table was meant to read without a
  reader branch;
- **one input moved BACK toward today** (R2-C3): the pin keeps its exact
  positions, so r1's two moved `dfa_pfs[]` selections return to their
  current rows. r1's third shape note ("the single ranking reaches
  `dfa_pfs[]`'s inputs") shrinks to one G1 verdict on one corpus artifact
  and the stretch representation of nine pins.
