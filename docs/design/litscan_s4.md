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
7. **S4(a) can stay out of `dfa_pfs[]` entirely (§2.3.5).**
   - `prefix_k.c` publishes a run PIN only for an exact run. So no prefilter
     row ever sees a masked run.
   - The table's shape, its predicates and every existing selection are
     unchanged.
   - The one shared decision that does change is `req_admit` (P7). It learns
     that a masked run is something to admit (Q4).
8. **The NONE answer for the caseless run pick is the cardinality model, and
   it picks `select`, not `from` (§2.3.3).**
   - For a cube, `popcount(K)` is exactly `log2(256/|set|)`. So "bits of
     information" `Σ popcount(K_i)` is `findings/design.md` §6.2's
     per-position cardinality NONE answer, spelled once (D126 Q4).
   - It ranks `select` (42) > `union` (35) > `from` (28).
   - The bench would prefer `from` (0.3441 against `select`'s 0.4389), and
     deployment traffic is wrong for `from` (WAF §3.2). The rule that is
     deployment-sane wins (Q6).
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

#### 2.3.1 The fact: `src/facts/req.c` widened to cube runs, additively

- The walk is the core fact. Each subtree's `RbRuns` gains a second triple:
  `cbest`/`chead`/`ctail`, the best cube run with per-position (T, K).
- Cube runs join across a concatenation exactly as exact runs do. They obey
  the same declines, each with its own reason (`req.c` header; reqpos_2b
  §2.4):
  - no join across a repeat;
  - an alternation's common prefix and suffix only;
  - no lookaround descent.
- A position joins a cube run if its set is one cube. An exact position is
  the `K = 0xFF` case: there is no separate path.

**The ranking is information, not length.**
- Cube runs rank by `Σ popcount(K_i)`. Ties go to the longer run, then the
  leftmost: today's tie order.
- For exact runs this is `8 × len`. So the exact triple's ordering is
  unchanged, and the exact triple keeps its own `best`.
- A don't-care position (`K = 0`) can lengthen a run without making it win.
  That is the reason length cannot be the ranking.

**Additive admission (Q5).** The derived `req_run` fact takes the EXACT run
whenever one of length >= 2 exists: today's answer, today's stamp, today's
bytes. It falls to the cube run only where the exact run declines, and then
only if three conditions hold:
- the cube run has at least three positions (Q8);
- it has at least one member scannable by `memchr`, i.e. `|set| <= 2`;
- `-fno-req-run-fold` (bit 44) is not set.

So the movers are exactly the patterns with no exact run and an admissible
cube run. That is a biconditional manifest, S2a's shape (§5.1). The ranking
between an exact 2-byte run and a 42-bit caseless run is C6's question
(Q7), not S4's.

#### 2.3.2 The record

`ReqRun` (`src/facts/facts.h:64`) gains:

```c
    unsigned char mask[PCREC_MAX_REQ_RUN_EMIT];        /* K per position; all 0xFF when exact */
    unsigned char mask_whole[PCREC_MAX_REQ_RUN_SCAN];  /* [K66]'s whole run's K */
    int pair;        /* -1, or the second byte when the scan member is a pair */
    bool masked;     /* any mask byte != 0xFF */
```

- `bytes` holds T.
- For an exact run every new field is inert (`mask` `0xFF`, `pair -1`,
  `masked false`). Every existing reader can therefore keep reading `bytes`
  and `len` unchanged.
- The readers that cannot take a mask test `masked`. There are two:
  `prefix_k.c`'s pin (§2.3.5) and G1's identity conjunct.

#### 2.3.3 The pick: the NONE answer, spelled once (D126 Q4)

- **Which cube run:** the information ranking above. That is the per-position
  cardinality model `findings/design.md` §6.2 names as `run-rarity`'s
  obvious NONE answer, since `popcount(K) = log2(256/|set|)` for a cube.
- On `union-select` it picks **`select`** (42 bits), over `union` (35) and
  `from` (28).
- When `[FINDINGS.B4]` lands, `pcrec_find_run_rarity` replaces this
  ordering as the C6 reader, and the cardinality order stays its tiebreak
  (findings design §2.6's tie rule).
- **Which member to scan.** The candidates are the window's positions with
  `|set| <= 2`. Cost is the prior's mass: one byte's ppm, or a pair's two
  ppm summed. Lowest wins. Ties go to an exact member (one stream), then
  the rightmost (the LASTCODEUNIT tradition, `rb_pick`'s tiebreak).
- **The encoding gate.** The prior reads only under `byte`, behind the
  accessor's own gate (D122 addendum 2 (3)). Under any other encoding the
  scan member is the rightmost scannable one: `rb_pick`'s fallback, the
  rule `reqrunenc_census.md` recommended for exact runs.
- **The window.** A run longer than `PCREC_MAX_REQ_RUN_EMIT` (8) is cut to
  the 8-position window containing the scan member with the most
  information. That is today's "lowest-frequency window containing the scan
  byte", read in bits.
- **On `union-select` the pick is `select` on `c`.** That is O-55's
  `ci_selectc` twin: **0.4389 ns/B against base 0.7178 (×1.64)**, still
  behind re2's 0.319.
- The bench-optimal `from`/`m` (0.2348) needs a subject-aware rate. That is
  findings territory, and `from` is the deployment-wrong pick (WAF §3.2,
  §5 Q2). Q6 asks the manager to accept the trade.

#### 2.3.4 The scan: a two-stream form in the run block

`OfsTest` (`emit_dfa.c:331`) gains `run_mask` (NULL when exact) and
`scan_pair` (-1 when the scan is one byte). `ofs_test_emit_fn`'s
unreachable `else` arm (`emit_dfa.c:6032`) becomes the PAIR arm. It is
reachable only through `req_run_tests`: `ofs_test_of`, which serves the
prefilter rows, never builds a pair.

The pair arm is the leapfrog O-55 measured. It is restated against the
block's own loop:
- One pending hit per stream is held as an OFFSET.
- Both streams are searched once before the loop.
- A stream is re-searched only when its hit falls behind the cursor.
- An exhausted stream parks at the end offset. The end offset is one past
  the last hit at which the run still fits: `n - (maxk - k*)`.
- The candidate is the smaller hit minus `k*`. The verify is the run
  compare (row 1, masked).
- [K27]'s `memchr(NULL, c, 0)` is closed by the loop guard, as in the
  memchr arm.
- Offsets are used rather than pointers, so no NULL pointer is ever compared
  relationally.

An exact scan member keeps today's `memchr` arm, with a masked verify. So a
cube run that has a case-invariant member, such as `(?i)foo-bar`'s `-`, is
one stream. That is the selection preference the `[WORD-FOLD]` row named.

#### 2.3.5 Admission and the consumers: where the masked run reaches, and where it does not

**`req_admit` (P7, `emit_dfa.c:6374`).** Its first conjunct becomes "no
necessary byte AND no masked run" → `NONE`.
- **G2** (one attempt) applies unchanged.
- **G1** (dominated) can elide a masked run only through an EXACT scan
  member equal to `dfa_cand_scan_byte`'s byte. A pair scan is never
  dominated: no prefilter row scans a pair.
- This is the one shared-decision change in S4. D124 item 3 asks what it
  guarantees to each consumer:
  - **DFA:** a pre-check is a check that does not run, or a proof of absence
    in one pass. It changes no answer.
  - **VM hybrid, and VM with no DFA scan:** the same. On the VM it can only
    turn a step-budget give-up into a NOMATCH, by running fewer attempts,
    and never the reverse. That is the K64/K65/K66 family's direction, and
    the differential must classify these transitions (§5.1).
- `pcrec_emit_req_byte_check` (`emit_dfa.c:810`), with `req_byte < 0` and a
  masked run admitted, emits the run block's call and no byte `memchr`.

**`prefix_k.c`'s pin.** It publishes `run_pinned` only when
`!req_run.masked`. So the `run-pinned[-bounded]` rows of `dfa_pfs[]`
(S1, bit 32) never see a masked run.
- **The table's shape, its predicates, its emitters and every existing
  selection are untouched.** That is the argument (Q4) that S4 does not
  take D122 addendum 4 item 3's full panel.
- A later step that lets a pinned masked run with an exact scan member
  enter the prefilter, the offset preference, does take that panel. It is
  named, not built.

**[K66]'s whole run** on a VM route with no DFA scan carries `mask_whole`.
The no-match proof stays a fact about the pattern.

**[K65]'s set** is unchanged. It is empty exactly when `req_byte` is -1,
which is the case on every S4(a) mover.

**Stamps.**
- `<PREFIX>_REQ_RUN` gains a `/`-suffixed hex mask ONLY when masked, for
  example `"53454c454354@4/dfdfdfdfdfdf"`. Exact runs' stamp text is
  unchanged.
- `<PREFIX>_REQ_BYTE` stays the `req_byte` fact (`"none"` on every mover).
- `<PREFIX>_REQ_WHY` reads `emitted`/`dominated`/`one-attempt`. A mover
  that reads `none` is a defect, and §5.4 checks for it.

### 2.4 Sites that keep their own form, with the reason (compare_stack §5's record, updated in the same change)

| site | why it keeps its form | what would move it |
|---|---|---|
| the island (`vm_isl_*`) | its words are singleton byte strings by its predicate (`vm_isl_single`), and its trie needs disjoint single-byte edges. A caseless island would need a trie over cubes; folding a node is unsound when its edges include a non-letter (`0x40 \| 0x20 == 0x60`). Its exact chains do take the run compare (§2.1) | a measured caseless keyword-alternation cell on the VM route. The only candidates are `altwide/ci-*`, which route DFA |
| the cursor rung's fixed-length `&&` chain (`vm_cursor_rep`) and the backward walk (`vm_rev_emit`) | S2a left both exact sites alone, and S4 keeps parity. A masked arm there needs the same emitter plus a cursor base. That is a small change with no measured population | a census of cursor/backward caseless bodies of length >= 3, plus a cell |
| the offset-set verify chain over cube offsets (`ofsk_emit_verify`'s `ofs_k<k>[...]` probes) | under `(?i)` the offset-k skip is mostly not selected at all (73.8% of producible walks have no invariant offset, `wordfold_census.md` §6). Where it is selected, contiguous cube offsets could be one masked word, but the population is uncounted | a census of offset-set artifacts with >= 3 contiguous cube offsets, plus a cell |
| `DFA_PF_MEMCHR`, `emit_attempt`'s `\n` | one byte, no verify (compare_stack §5) | — |
| `dfa_pfs[]` rows | §2.3.5: the pin is exact-only by construction | the offset-preference step, with a full panel |
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
| 44 | `-fno-req-run-fold` | `PCREC_NO_REQ_RUN_FOLD` | the cube run in the necessary-run fact (§2.3). A fact-level deny (D126 Q3): `req_run` has nothing masked to find, for every consumer | `<PREFIX>_REQ_RUN`'s `/mask` suffix |

**Why three bits and not one (Q2).** D144 item 4 has batch-gate triage flip
flags rather than bisect. The three mechanisms have disjoint witness cells:
- bit 42: slack `://`, router `/user`, litrun;
- bit 43: forced-VM WAF;
- bit 44: `union-select` auto.

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

**Spec hunks (D80), in the commit that changes the behaviour:**
- `tuning.md` §2.37-2.39, plus §2.31's lit-run text ("single-cube byte
  classes");
- `limits.md` §3.1's charge sentence;
- `match_api.md` §6.3's stamp catalogue (`RUN_WORDS`, `VM_LIT_MASKED`, and
  `REQ_RUN`'s suffix grammar);
- `ir_listing.md` (the masked `compare` op);
- `table_contract.md`, if `--emit-facts`' `req_run` row's columns change;
- `compare_stack.md` §2/§5 (the D122 keep-it-true rule).

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
   - **C3:** moved ⇔ `req_run` is masked.

   Each has 0 off-diagonal, as S2a's 1,081 / 4,891 did.
2. **The answer differential** (`tests/findings/b1_mover_answers.py`,
   reused) over every mover covers the span, every capture and the give-up
   surface, at every startpos, BASE vs NEW. C3 classifies give-up → NOMATCH
   transitions as allowed and lists them (§2.3.5). Any other transition is
   a failure.
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
| S446 | `pair-scan-one-stream` (`emit_dfa.c`, the pair arm) | drop the upper-case stream | `reqcube.rxt` "present only in the other case" cells |
| S447 | `req-pin-takes-masked` (`prefix_k.c`) | publish the pin for a masked run | the §5.4 `--emit-facts` check, plus axes on bit 44 |

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
| `slack-webhook-url` auto **caps** (VM hybrid), `syslogbase-expanded` auto | the default-route population. The compare runs once per prefilter candidate | null (the control) |

**C3, the caseless necessary run:**

| cell | why | expect |
|---|---|---|
| `union-select` thr, nocaps and caps | the one measured customer | ≈ **0.43 ns/B** from base 0.718. PREDICTED from O-55's `ci_selectc` 0.4389, whose verify was a byte loop; the word verify is not slower |
| controls, byte-identical under C3: `sleep-benchmark`, `dbnames`, `concat-sqli` (no necessary cube run), `slack` (exact run exists) | — | noise |
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
{auto, vm}) for all three commits, and the C3 cube-run census (which
patterns gain a masked `req_run`). `wordfold_census.md` §2 bounds the C3
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
| **C3** | `req.c` cube triple + ranking; `ReqRun` fields; the derived pick; `prefix_k.c` pin gate; `req_admit` widening; the pair arm in `ofs_test_emit_fn`; `REQ_RUN` suffix; bit 44; tuning §2.39; `reqcube.rxt`; S445-S447 | +330 / −25 | +1 |
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
| specific vs general | General. Any one-cube class joins a run, with no caseless special case. One compare function serves every run site of both engines. The exact arm is the `K = 0xFF` case of the same rows |
| core vs derived | P2 and the cube runs are core facts with no prior read. The run pick and the scan member are derived, and read the prior through the accessor (D126 Q4 NONE answer) |
| applicable vs assumption-changing | Applicable. Exact runs keep their facts, bytes and stamps. The masked run fills only today's declines (additive admission). `dfa_pfs[]` is untouched |
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
4. **Does C3 need D122 addendum 4 item 3's FULL panel?** `dfa_pfs[]`'s shape
   and every existing selection are unchanged by construction: the pin is
   exact-only. But P7 (`req_admit`) gains a conjunct, and the VM give-up
   surface moves in the safe direction. **Recommendation: a light D6 panel
   on C3 only.** Use two lenses: answer soundness (the cube-run walk and its
   declines), and the consumer contract (K64's class, D124 item 3). C0-C2
   take no panel.
5. **Additive admission:** a cube run is consulted only where no exact run
   of length >= 2 exists. **Recommendation: accept.** It makes C3's movers
   an exact biconditional and leaves every exact-run artifact
   byte-identical. Ranking an exact 2-byte run against a 42-bit caseless run
   is C6/B4's job, with a rate.
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
8. **The cube-run floor in C3:** three positions, mirroring D127, or
   today's exact run floor of two. **Recommendation: three.** Every measured
   customer is 4-6 positions. A two-letter caseless run doubles the scan's
   hit density for a two-byte verify, with no cell. Lowering it is a census
   plus a cell (D77).
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
