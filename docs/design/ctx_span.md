# ctx_span — [DD-11.5] re-scoped: the span-context producer (D168) and `A_BOL`/`A_EOL` into `A_CTX` (D168 addendum 1); DESIGN NOTE, PROPOSED, nothing built

Lane `ctxspan` (opus, design only), 2026-10-18, main `2ce4a1124`, abi 80. The charter is
D168 and D168 addendum 1 (`docs/dev/decisions.md`) and plan row [DD-11.5]. Inputs:
`docs/dev/dd11_family_2026-10-18.md` (the family survey), `kit_proof.md`,
`memfn/window_contract.md`, `ucp_design.md` (UD-2), `definitions_table.md`,
`docs/dev/kvcensus.md`, `docs/dev/eng_look_census.md` and the [ENG-LOOK] row.

Every `file:line` below is by grep at `2ce4a1124`; re-grep at the build commit. Every
equivalence claimed between two spellings was run against libpcre2 10.46 on this box
(`build/probe/eqv.c` in the lane worktree, not committed: anchored match at every start, all
547 (subject, start) cells over `{a, \n, x}` up to length 4). Nothing under `src/` was
changed.

---

## 0. Answers first

| question | answer |
|---|---|
| what part 1 is | ONE producer in `span_facts` (`src/facts/spans.c`, kit_proof's UL-0 slice) that states, per offset BEFORE span 0 and AFTER its end, a context record `{set, absent, exact}`, and that refines span 0's own `S_d` with the same rule where a context item stands INSIDE the span (§3) |
| its one rule | every zero-width item contributes a per-offset set list relative to its own position. Outside the span the list is a context record; inside, it intersects `S_d`. `\b`/`\B` contribute only once the neighbouring side is known (the FOLD). A first-match INPUT TABLE (§3.3) maps each zero-width kind to its contribution; no kind has a private arm |
| what it is not | a tree rewrite: no engine's bytes move, the producer READS `A_CTX` nodes and `A_LOOK` bodies (D168) |
| where the record lives | `MkLang` (`src/facts/known.h`, kit_proof's pattern-fact record) gains `ctx[]`; the producer is the slice's own walk (§3.2) |
| what it sends the kit | nothing new: R-26's `mf_site.ctx[]` CONTEXT predicates with `absent`, plus the EXISTING `byte_form` (EXACT / SUPERSET) for exactness (§3.9). Facts only (D157) |
| relation to kit_proof | one design. Stage 1's source stays the machine reading (Q3, RULED). The producer ships at Z2 beside UL-0 as a listed fact and as the C8-ctx control; it becomes THE source at UL-8's trigger (§3.10) |
| a finding against kit_proof §5.2 | "every zero-width node passes through" is wrong for `A_CTX` and lookaheads INSIDE span 0: they constrain WHICH byte, so passing them through overstates `exact_len` (`a(?=b)[a-z]`). The in-span half of the rule fixes it (§3.8) |
| what part 2 is | the multiline forms `(?m)^` and `(?m)$` leave `A_BOL`/`A_EOL` and become `A_CTX` over the newline set, with an ABSENT-AWARE truth function (9 cells, each side `absent` / `in` / `out`). The `multiline` field, `N_BOT_M` and `N_EOL_M` are deleted (§4) |
| the surprising fact | `(?m)$` needs NO extension: it is `(?![^\n])` today (libpcre2: 547/547 cells agree), already an `A_CTX`. Only `(?m)^` needs "the next character exists" (`(?m)^` vs `(?<![^\n])`: 40 of 547 cells differ, all after a final newline). Both take the absent-aware form anyway, for byte identity (§4.2) |
| what does not fold | `^`/`\A` (`A_BOL`, a position test that anchoring reads), `$`/`\Z` (`A_EOL`: "before a FINAL newline" reads two positions ahead, which is the DFA's eol view), `\z` (`A_END`), `\G`. They stay kinds by D62's own principle (§4.3) |
| census headline | 16 `multiline` code reads: **14 deleted, 2 become the generic node choice**. `N_BOT_M`/`N_EOL_M`: 12 further code lines, **9 deleted, 2 sites become fn-derived predicates**, plus the newline contributor row, its `nl_bit` plumbing and its knob (deleted). **84 code lines naming `A_BOL`/`A_EOL` stay** (the kinds survive). The survey's "38 `A_EOL` references under `src/opt/`" mostly SURVIVE; the deletion is the D62 control-3 hazard class, not those labels (§4.4) |
| cost | an abi event (80 → 81). Six readers of the number by grep (§4.5.1). Byte identity is reachable for every artifact except DFA machines whose context-set list ORDER changes (a `(?m)` node before another `A_CTX` set in NFA order); those are answer-identical movers, counted by emit_sweep. One check retires (`run_mlinectx_identity.sh`), four sabotage rows re-aim (§4.5) |
| contradicts D168? | No. Two precisions (§3.5, §11): D168's "width-1 negative lookbehind" means width 1 in BYTES on the lowered tree (`(?<!é)` under utf8 is a 2-byte disjunction and declines), and part 2's census shows the deletion is smaller than add. 1's survey figure suggested |

---

## 1. Problem

Two things carry the same fact today in separate places.

1. **Context around a search span.** The kit's find-window contract (window_contract §2.2,
   "Context predicates"; kit_proof §3, §4.1) can use what is known about the subject before
   span 0's offset 0 and after its end. Today that knowledge exists as: MLINE's `{\n}`
   CONTEXT predicate at −1; the 23 `scan-restart/ctx` sites, which send a width-1
   lookbehind as a shifted origin (kvcensus §6); the DFA's seed table and class-indexed
   accept, which encode `\b` by position; and kit_proof's stage-1 machine reading (§3.2),
   which reads the context off the anchored DFA. Each reads a different object. A VM-only
   pattern gets none of it. D168 rules ONE producer of per-offset sets in `span_facts`.

2. **The assertion family's special cases.** `\b`, `\B` and every one-character lookaround
   are one node, `A_CTX` (UD-2), with the truth function as DATA. `(?m)^` and `(?m)$` are
   not: they are `A_BOL`/`A_EOL` with a parse-resolved `multiline` field (D62), lowered to
   two dedicated NFA kinds `N_BOT_M`/`N_EOL_M`, each with its own closure arm, its own
   contributor row on the DFA's class axis, its own VM arm, and a field every analysis must
   remember to read. D62 accepted that last cost in so many words: "the compile alarm that
   would cover unimagined [consumers] is forgone" (D62, residual). Frank (add. 1):
   simplification alone qualifies.

The two problems meet. Without part 2, part 1's producer needs an arm for "`A_BOL` with
`multiline` set" to state MLINE's context, which is the special case part 2 deletes. With
part 2, `(?m)^` before a consuming item is an `A_CTX` the fold already reads.

## 2. Forces

- **One mechanism per fact** (memory `pcrec-general-mechanisms-not-special-cases`; D122). The
  context fact must have one producer; a per-spelling arm in that producer re-creates the
  dispersal D168 removes.
- **Read, do not rewrite** (D168; kit_proof §3.2). A tree rewrite moves every engine's bytes
  for no answer change.
- **Facts, never methods** (D157). The record says what is true of every match. Which kit
  row tests it is the kit's.
- **No silent defaults** (memory `pcrec-no-silent-defaults`; window_contract §2.3). Every
  enum in the record has an UNSTATED zero, refused where read.
- **Proof vs filter** (D168; kit_proof C8). An inexact record may filter (a necessary
  condition) and may never prove. `cover` reads exact records only.
- **D62's principle**: kinds encode STRUCTURE, fields encode PARSE-RESOLVED MODIFIER STATE.
  Part 2 must not add a kind per modifier (D62 rejected `A_EOL_M`), and it does not: it
  maps a modifier choice onto an existing GENERAL kind with data (D168 add. 1: "the parser
  resolves modifier state onto the node at parse time and picks the set or kind").
- **The [ENG-LOOK] ruling**: "NO one-character fold ships anywhere — it is the duplicate
  path." That ruling is about ENGINE code (a second DFA path for one-class bodies). The
  producer is a READING in the facts layer, ruled by D168. Part 2 moves `(?m)` ONTO the
  one class-axis mechanism [ENG-LOOK] would generalize, so it reduces the number of
  instances [ENG-LOOK] must later replace. Neither part is the fold that ruling forbids.
- **Abi pre-release** (memory `pcrec-abi-changes-pre-release`): an abi event is ritual, not
  avoidance.
- **Build under measurement** (D77): part 2 is filed FOR THE REVIEW; nothing is built ahead of
  Frank's word.

---

## 3. Part 1: the span-context producer

### 3.1 What exists

- `A_CTX` (`src/core/internal.h:776`, its comment block above): a code-point set
  `u.ctx.iv`/`n` and a 4-bit truth function `u.ctx.fn`, bit `(p << 1) | q` being the answer
  when the previous character's membership is `p` and the next one's is `q`. "Absent" (start
  or end of subject) reads as NOT in the set. Six functions (`CTXFN_*`,
  `src/core/internal.h:1157-1163`): `\b` 0x6, `\B` 0x9, `(?<=C)` 0xC, `(?<!C)` 0x3,
  `(?=C)` 0xA, `(?!C)` 0x5.
- The recognizer (`src/parse/ctxnode.c`, NOT `src/opt/ctxnode.c` as the brief and two code
  comments say, §11): a lookaround whose body's LANGUAGE is a set of single characters, and
  whose set is byte-expressible under the encoding (`pcrec_enc_set_bytes`), becomes one
  `A_CTX`. Everything else stays `A_LOOK`, which the NFA erases to `N_EPS` (`src/ir/nfa.c`,
  the `A_LOOK` arm) and the VM executes.
- `span_facts` is NOT BUILT. `src/facts/spans.c` does not exist; kit_proof §5.2 designs its
  first slice (UL-0: `S_d`, `exact_len`, the hull at the match-start origin, priority-free,
  on the lowered tree) and builds it at Z2. window_contract §5.2 designs the whole producer
  (segments, hull spans, prefix sums).
- kit_proof's stage-1 context is the machine reading `MkEnd.ctx_before`/`ctx_after` with
  `absent_before`/`absent_after` (kit_proof §3.2, §5.1), DFA-only.

### 3.2 The record and where it lives

The record extends kit_proof's pattern-fact record `MkLang` (`src/facts/known.h`, kit_proof
§5.1), because a context set is a property of the same language, at the same origin, on the
same lowered tree. A separate record would be a second home for one walk's output.

```c
/* src/facts/known.h -- span_facts' context half (ctx_span.md §3). One record per offset
   outside span 0 that some context item constrains. Byte sets (mf_term.set's layout),
   on the lowered tree. Every enum has an UNSTATED zero, refused where read. */
typedef enum { MK_ABS_UNSTATED = 0, MK_ABS_SATISFIES, MK_ABS_FAILS } MkAbsent;
typedef enum { MK_CTX_UNSTATED = 0, MK_CTX_EXACT, MK_CTX_SUPERSET } MkCtxForm;
typedef struct {
    int8_t    off;        /* < 0: before span 0; >= exact width W: after the end */
    uint8_t   set[32];    /* the byte at `off` lies in `set` ...                  */
    MkAbsent  absent;     /* ... or `off` is outside the subject and this says    */
    MkCtxForm form;       /* EXACT: the records together are EQUIVALENT to the     */
} MkCtx;                  /* context items; SUPERSET: a necessary condition only   */

typedef struct {
    uint8_t  stated;                    /* MK_LANG_UNSTATED 0, MK_LANG_STATED       */
    uint8_t  exact_len;                 /* 0..MF_MAX_SPAN_POS                       */
    uint8_t  set[MF_MAX_SPAN_POS][32];  /* S_d, d < exact_len                       */
    uint8_t  nctx;                      /* 0 = no context fact (not "none holds")   */
    MkCtx    ctx[MF_MAX_CTX];           /* sorted by `off`, one per offset          */
} MkLang;
```

- **`exact` is one bit per RECORD SET, not per record.** The records of one artifact are
  EXACT together or not at all: the context condition equals the conjunction of the
  records, or it does not. `form` is stated per record so the carrier maps one-to-one
  (§3.9); the producer writes the same value on every record of one artifact, and the
  listing check (§6, CK-3) asserts it.
- **The bounds are the carrier's** (`MF_MAX_BACK` 8, `MF_MAX_AHEAD` 1, `MF_MAX_CTX` derived,
  kit_proof §4.2), not a producer tuning constant (memory `pcrec-suspect-tuning-constants`):
  a fact past the carrier has no reader (D77). A context item that would need an offset
  outside them contributes nothing beyond the bound, and the producer records that it
  truncated (a SUPERSET record, or no record), never a silent drop.
- **`nctx` 0 is "no context fact"**, which every reader treats as "the context is
  unconstrained". It is never read as "a context that always holds".

### 3.3 The input table (first match, one row per zero-width kind)

The producer walks span 0's item sequence as the slice does. Each ZERO-WIDTH item it meets
contributes through this table. No row names a spelling. A kind not in the table is a
compile error (no `default:`; mrl.c's rule).

| row | kind and predicate | contribution (offsets relative to the item's position `p`) | form |
|---|---|---|---|
| `ctx-onesided` | `A_CTX` whose fn reads ONE side (`PREV`/`NOT_PREV`/`NEXT`/`NOT_NEXT`, and part 2's two) | the side's set, or its complement for a `NOT_` fn, at `p − 1` (prev) or `p` (next). `absent` from the fn's absent cell (§4.2; today: absent reads as `out`) | EXACT |
| `ctx-fold` | `A_CTX` whose fn reads BOTH sides (`\b`, `\B`), and the OTHER side's set at this position is KNOWN and lies wholly inside or wholly outside `C` | the fn restricted by the known side becomes a one-sided test on the remaining side (§3.4) | EXACT |
| `ctx-unfold` | `A_CTX`, both sides, the other side unknown or straddling `C` | none (D168 "Revisit when": a two-offset relation is not a per-offset set). Inside span 0 it ENDS `exact_len` before the item | — |
| `look-fixed` | `A_LOOK` positive, every branch of fixed BYTE width | per offset, the union over branches of the branch's byte set, right-aligned at `p` (behind) or left-aligned (ahead); an offset beyond a branch's width takes ALL bytes and absent SATISFIES for that branch. `absent` FAILS within every branch's width | EXACT iff one branch whose language is the product of its per-offset sets; else SUPERSET |
| `look-neg-1` | `A_LOOK` negative, body of fixed width ONE BYTE | the complement of the body's byte set; absent SATISFIES | EXACT |
| `look-neg-wide` | `A_LOOK` negative, wider than one byte | none (a disjunction, not a product; D168). Inside span 0 it ends `exact_len` | — |
| `look-other` | `A_LOOK` of variable width, or with a capture, reference or call in its body | none | — |
| `pos-start` | `A_BOL` (`\A`, non-multiline `^`) | at `p − 1`: the empty set, absent SATISFIES | EXACT |
| `pos-end` | `A_END` (`\z`) | at `p`: the empty set, absent SATISFIES | EXACT |
| `pos-eol` | `A_EOL` (`$`, `\Z`) | none: "before a FINAL newline" is a two-offset fact. Inside span 0 it PASSES THROUGH to the hull, kit_proof §5.2's `[r3rc K1]` rule, and C9 keeps the position constraint on A | — |
| `pos-other` | `A_GSTART`, `A_KRESET`, `A_EMPTY` | none (`\G` is a runtime value, `\K` constrains nothing) | — |

Before part 2, `A_BOL`/`A_EOL` with `multiline` set would each need a further row
(`(?m)^` → `{\n}` at −1 when the next side is consuming; `(?m)$` → `{\n}` at `p` with absent
SATISFIES). Part 2 deletes those two rows: the items arrive as `A_CTX` and take
`ctx-onesided` (`(?m)$`) or `ctx-fold` (`(?m)^`, §4.2). That is the cost the producer pays
without part 2, and it is a special case by the definition this repo uses.

`pos-start`/`pos-end` produce a record no stage-1 consumer reads: an anchored pattern takes
T-CUT's `anchored` row and has no window site (window_contract §5.4), and `\z` is U-z's
(kit_proof §8.3). They are rows because the fact is the same fact, and the table would
otherwise need an exception for them.

### 3.4 The fold: previous set × next set

`\b` at position `p` holds iff `W(prev) ≠ W(next)`, absent reading as not-`W`. Once the
next side's set `N` is known (span 0's `S_0` when `p` is the origin; `S_d` inside the span;
the context record at `p` when one is already stated):

| `N` vs `W` | `\b` becomes | `\B` becomes | absent |
|---|---|---|---|
| `N ⊆ W` | `prev ∉ W` (`(?<!\w)`) | `prev ∈ W` | `\b` SATISFIES, `\B` FAILS |
| `N ∩ W = ∅` | `prev ∈ W` (`(?<=\w)`) | `prev ∉ W` | `\b` FAILS, `\B` SATISFIES |
| straddles | no per-offset fact (`ctx-unfold`) | the same | — |

The mirror holds at the end: with the previous side known (`S_{W−1}`), a trailing `\b`
becomes a test of the byte at `W`. libpcre2 confirms the two directions measured:
`\bx` ≡ `(?<!\w)x` and `\b\n` ≡ `(?<=\w)\n` (547/547 each).

**The next side must EXIST.** If span 0 can be empty at the origin (the body is nullable
there), the byte after `p` may be absent or anything, and the fold declines. The same
condition is what makes `(?m)^` foldable (§4.2): `(?m)^x` ≡ `(?<![^\n])x` (547/547), and
`(?m)^a?` ≢ `(?<![^\n])a?` (40 differ, all with no byte after the position).

**One fold, three placements.** Before span 0 the result is a context record at −1. Inside
span 0 (an `A_CTX` between offsets `d − 1` and `d`), a one-sided result intersects `S_{d−1}`
or `S_d`; a two-sided item folds against `S_{d−1}` or `S_d` (whichever is wholly inside or
outside `C`) and intersects the other; a straddle on both ends `exact_len` at `d − 1`,
because the language from the origin is no longer the product (`[a-z0-9_ ]\b[a-z ]` admits
`a ` and ` a` and not `ab`). After the end it is a record at `W`. kvcensus's context
reading (method, "Context") used exactly the first and third placements and measured them
as an equivalence (C4, 0 of 6,510 disagreements).

### 3.5 Lookbehind and lookahead bodies

- **Width is BYTES on the lowered tree.** The producer runs after `lower_enc`, as the slice
  does, so `(?<=é)` under `-e utf8` is two offsets `{C3} {A9}`, EXACT. D168's "width-1
  negative lookbehind" therefore means one BYTE: `(?<!é)` under utf8 is "not (C3 then A9)",
  a disjunction over two offsets, and DECLINES under `look-neg-wide`. Under `-e byte` it is
  one byte and takes `look-neg-1`. This is a precision of D168, not a contradiction: the
  per-offset sets are byte sets everywhere in this design.
- **Alternation inside a lookbehind** (D168): `(?<=ab|cd)` gives `{a,c} {b,d}`, SUPERSET
  (`ad` passes the records and not the body). `(?<=a|bc)`, which PCRE2 accepts (each branch
  fixed), right-aligns: −1 `{a,c}`; −2 is constrained by branch 2 only, so its union is all
  bytes with absent SATISFIES, which is no fact and is not recorded.
- **Lookahead after the end** mirrors lookbehind before the start, left-aligned at `W`. The
  carrier's `MF_MAX_AHEAD` 1 bounds what is sent (kit_proof §4.2, its trigger stated
  there); the producer states what the item gives and the carrier truncates, marking the
  truncation (§3.2).
- **A lookbehind's body is never a span.** The producer reads its per-offset byte sets with
  the slice's own position walk applied to the body. It does not descend for any other
  purpose, which keeps window_contract §5.2's decline "a lookaround's body is never
  descended" true for the HULL and its segments.

### 3.6 Combining items

- **Stacking at one offset** (`(?<=[a-z])\b\w`): intersect the sets; `absent` SATISFIES only
  if every item's does; the form is EXACT only if every item's is.
- **Top-level alternation** (`\bfoo|\bbar`): per offset, the union of the branches' records;
  EXACT only if every branch states the same record at that offset (then the language is
  that context times the alternation of bodies). An offset one branch does not constrain is
  not recorded. This is §3.5's lookbehind-alternation rule, reused.
- **Repeats** contribute their body's items only at `rmin ≥ 1` on the first (leading) or
  last (trailing) iteration, the slice's own rule for `S_d`.

### 3.7 Encoding

- `A_CTX` sets are CODE POINTS (`u.ctx.iv`). An `A_CTX` exists only where its set is
  byte-expressible (the recognizer's conjunct; `\b`'s port asks the same). The producer
  converts with `pcrec_enc_set_bytes` (`src/enc/enc.c:403`) and DECLINES the item if the
  call fails, never samples. That is the precondition the `A_CTX` comment calls
  `pcrec_ctx_set_bytes`, a function that does not exist (§11).
- Under the precondition, "the previous CHARACTER is in `C`" equals "the previous BYTE is in
  `C`": every member of `C` is one byte, and a multi-byte character ends in a continuation
  byte, which is not in `C`. So an `A_CTX` record at −1 is exact byte-wise under utf8, which
  is kit_proof §3.3's "utf8 and `\w`" argument in general form.
- `A_LOOK` bodies are read lowered, so their sets are bytes by construction.
- UCP `\b` under utf8 is refused by the parser today (`[UCP]` U3/U4), so the producer never
  sees a non-byte-expressible word set.

### 3.8 How it joins the slice (`S_d`, `exact_len`, hull), and a finding against kit_proof §5.2

The context half and the slice are ONE walk. The slice computes `S_d` position by position;
when it meets a zero-width item it consults §3.3. A contribution at an offset inside the span
intersects `S_d`; one outside the span becomes a record; a decline inside the span ends
`exact_len`.

kit_proof §5.2 states that "a zero-width assertion constrains WHERE a byte may stand, and
not WHICH byte", so every zero-width node passes through to the hull. That is true of
`$`/`\Z` (the case it was written for, `[r3rc K1]`) and false of `A_CTX` and of lookaheads.
On `a(?=b)[a-z]` the pass-through slice states `S_0 = {a}`, `S_1 = [a-z]`, `exact_len` 2,
while the language is `{ab}`. The HULL is still sound (every match's bytes lie in the sets),
so nothing ships wrong today, but `exact_len` is overstated. C8 would catch it against A's
`S_1 = {b}` and report `exact/producers-disagree`, which kit_proof calls a defect the trace
build asserts 0 of. So the trace build would go red on the first admitted artifact with a
mid-span `A_CTX`. The in-span half of §3.3 is the fix, and it belongs in UL-0 at Z2 rather
than after it. Filed as F-1 (§11) for kit_proof's next revision.

### 3.9 How the find-window contract carries it (facts only, D157)

No new kit field is needed. Each `MkCtx` maps to one R-26 `mf_site.ctx[]` CONTEXT
predicate (kit_proof §4.1):

| `MkCtx` | `mf_pred` field | note |
|---|---|---|
| `off`, `set` | one term at `off` (in `[−MF_MAX_BACK, 0)` or `[k, k + MF_MAX_AHEAD)`) | `k` is the span's end, `W` here |
| `absent` | `absent` (`SATISFIES` / `FAILS`) | the same enum, UNSTATED refused there |
| `form` | `byte_form` (`EXACT` / `SUPERSET`), window_contract §2.2 | the existing field; a SUPERSET context predicate is a filter only and never takes a proof (window_contract §4.3 direction (2)) |
| — | `consumable`, `need`, `span_class` CONTEXT | pcrec's consumer decides `consumable`; `need` is T-NEED's |
| — | site `read_floor` `MF_FLOOR_SUBJECT` | kit_proof §3.5; a below-origin record is refused under `MF_FLOOR_LO` |

Which records are SENT is pcrec's consumer's choice (T-NEED, T-PROOF), not the producer's:
the producer states every record; a `cover` site sends EXACT records only (C8's rule applied
to context, D168). Nothing in the record or its mapping names a kit method.

### 3.10 Relation to kit_proof: one design, not two

| kit_proof item | what this note does with it |
|---|---|
| §3.2 (READ, stage 1 DFA-only) and §8.4 Q3 (RULED: "the reading for stage 1 … the general form is a previous-set × next-set fold over `A_CTX`") | unchanged for stage 1: `MkEnd`'s machine reading is what `cover` sends at B1. The fold of §3.4 IS Q3's general form |
| §5.2 UL-0 (the slice, built at Z2) | the context half is the same walk (§3.8) and should land in the same Z2 change: it is listed in `--emit-facts`, sent nowhere, and it is the C8-ctx control (§6 CK-1). The in-span refinement is needed by UL-0 itself (F-1) |
| §5.1 `MkEnd.ctx_before/ctx_after/absent_*` | stays as the machine reading. On every DFA artifact where both exist, C8-ctx requires the producer's EXACT records to equal it, with the producer allowed to be SILENT (no record) where the machine states one and never the reverse; a machine-silent, producer-exact case is reported, not failed (the machine declines more shapes, e.g. a seed table whose live entries disagree) |
| §8.3 UL-8 (the facts-layer context fact at U1b) | this producer IS UL-8's object, designed now. It becomes THE context source at UL-8's trigger (U1b / [CAPS-KNOWN], the first VM-side consumer), with the machine reading demoted to its control |
| §8.3 UL-6 (a true lowering of `\b`, BOONIES) | unchanged and still BOONIES: this note lowers nothing |
| §8.3 U-mline | part 2 makes MLINE's context a `ctx-fold` record (`{\n}` at −1). U-mline's change (`absent` SATISFIES, the edge retires) then reads the producer's `absent` rather than a restated predicate |
| §8.3 U-ctxorigin, U4 | the 23 shifted-origin sites and the seeded-DFA filters read the same records (§10) |
| §3.3's table | every "yes" row is a §3.3 row; the "NO" rows are `look-fixed` with width > 1 (the producer CAN state it; the machine reading cannot, so it is producer-only and enters as a filter at U4) and `pos-eol` (never) |

---

## 4. Part 2: retire the multiline forms into `A_CTX`

### 4.1 What exists

- The parser builds `A_BOL` for `^` and `A_EOL` for `$`, writing `u.anch.multiline` from the
  scoped `(?m)` state (`src/parse/parse.c:1681`, `:1696`). `\A`/`\Z` build the same kinds and
  pin the field false (`src/parse/mod_assertions.c:224-225`).
- Lowering consumes the field once: `A_BOL` → `N_BOT_M` or `N_BOT`, `A_EOL` → `N_EOL_M` or
  `N_EOL` (`src/ir/nfa.c:620`, `:636`).
- The DFA closure (`src/ir/dfa.c:1071-1078`): `N_BOT_M` passes iff `bot_ok || (left ∈ \n &&
  !end_ok)`; `N_EOL_M` iff `end_ok || right ∈ \n`. The newline set reaches the class axis
  through its own contributor row `CTXROW_NEWLINE` (`src/ir/dfa.c:190-191`), after every
  `A_CTX` set, and its list index travels as `nl_bit`.
- The VM has two dedicated arms (`src/gen/emit_vm.c:8893`, `:8931`) beside `vm_ctx`'s
  fn-keyed form table (`src/gen/emit_vm.c:8354-8361`).
- `pcrec_nfa_has_bot` (`src/ir/nfa.c:1313-1319`) routes any `N_BOT`/`N_BOT_M`/`N_GSTART`
  machine to `ENG_ATTEMPT`; the `has_end` hoist (`src/ir/dfa.c:1589-1590`) makes the
  `pos == n` view live for both multiline kinds.

### 4.2 The absent-aware truth function

**What `(?m)^` needs.** Its truth (libpcre2: `(?m)^` ≡ `\A|(?<=\n)(?=[\s\S])`, 547/547):

| prev \ next | absent | in `{\n}` | out |
|---|---|---|---|
| **absent** | 1 | 1 | 1 |
| **in `{\n}`** | 0 | 1 | 1 |
| **out** | 0 | 0 | 0 |

No 4-cell function over one set, with absent read as `out`, gives this: the (absent, absent)
cell (`""` at 0) is 1 and the (in, absent) cell (after a final newline) is 0. No choice of
two sets helps either: "prev absent" and "prev is `\n`" must differ, so absent must be its
own value. The extension is therefore: each side is three-valued, `{out, in, absent}`, and
the function is a 9-cell table, bit `3p + q`.

**What `(?m)$` needs: nothing.** `(?m)$` ≡ `(?![^\n])` (547/547), which the recognizer
already turns into `A_CTX(¬{\n}, NOT_NEXT)`; pcrec's two spellings (`x(?m)$`,
`x(?![^\n])`) also agree with each other on both engines over the five subjects probed with
generated matchers. `$` itself is not: `$` ≢ `(?![^\n])` (102 of 547 differ).

**Why both take the absent-aware form over `{\n}`.** Spelling `(?m)$` as
`A_CTX(¬{\n}, NOT_NEXT)` changes the class axis: its set is the complement, so the newline
byte and the absent side share atom 0 where today the newline byte has its own atom, every
`(?m)$` DFA artifact's atoms renumber, and the `pos == n` view it uses today goes dead. The
answers are identical and the bytes all move. Keeping the set `{\n}` and putting the absent
cell in the function keeps today's atoms and today's `end_ok` reading, which is what makes
byte identity reachable (§4.5.3). The two new functions, named by what they compute:

| function | cells set (`3p + q`; `p`,`q` ∈ {0 out, 1 in, 2 absent}) | is |
|---|---|---|
| `CTXFN_PREV_ABSENT_OR_IN_NEXT_PRESENT` | (2,0) (2,1) (2,2) (1,0) (1,1) | `(?m)^` over `{\n}` |
| `CTXFN_NEXT_ABSENT_OR_IN` | (0,1) (0,2) (1,1) (1,2) (2,1) (2,2) | `(?m)$` over `{\n}` |

(The spellings are this note's PROPOSAL; answer-free, the manager's.)

**Re-encoding the six.** Each existing 4-cell function `f` becomes the 9-cell function with
the absent row and column COPIED from `out` (`g(p, q) = f(p', q')`, absent mapped to out).
That is today's semantics by construction ("absent reads as NOT in `C`"), so the six move no
answer, and `u.ctx.fn`/`NState.ctxfn` widen from `uint8_t` to `uint16_t`. The values are
never emitted (`vm_ctx_forms` keys on them, `dfamemo.c:67` compares them), so the widening
moves no byte.

**How each engine reads absent.**
- DFA forward closure: `p = bot_ok ? absent : bit(left)`, `q = end_ok ? absent : bit(right)`.
  These are exactly the inputs `N_BOT_M`/`N_EOL_M` read today, so the closure is the same
  predicate over the same bits.
- Two fn-derived predicates replace the two kind tests: `ctxfn_reads_absent_prev(fn)` (the
  absent row differs from the out row) makes the machine BOT-family in `pcrec_nfa_has_bot`,
  and `ctxfn_reads_absent_next(fn)` (the absent column differs from the out column) makes
  `has_end` live. For the six re-encoded functions both are false, so no shipped `\b` or
  lookaround machine changes route or views. Both are DATA reads, the K96 shape, not kinds.
- Reverse machine: `(?m)$` stays on `ENG_UNANCH` today because its truth at `pp` is a fact
  about the byte already consumed (`src/ir/nfa.c` comment above `pcrec_nfa_has_bot`). The
  `A_CTX` form must read the same `end_ok` through `sides_of`'s direction mapping. That is
  the one engine-side point that must be shown, not argued: CK-5 (§6) is byte identity of
  the reverse tables for every `(?m)$` artifact.
- VM: two rows in `vm_ctx_forms`, each emitting today's expression text for its function
  (`scan_position == 0 || (scan_position < subject_length && (…))` and
  `scan_position == subject_length || (…)`), the set interned from the same newline bitmap.
- possessify's arm A: `pcrec_poss_ctx_admits` takes a left-polarity mask over two values; it
  gains the third (absent). Arm A then VALUES `(?m)` gates instead of widening them, which
  can possessify more quantifiers: an answer-identical VM mover, and a small capability gain
  (§10, UL-c).

### 4.3 What does not fold, and why it stays a kind

- **`^` and `\A` (`A_BOL`).** `\A` ≡ `(?<![\s\S])` (547/547), so it is EXPRESSIBLE as an
  `A_CTX`. It stays a kind: it is an ABSOLUTE POSITION test, and anchoring reads it
  structurally (`startanch.c` SA_BOT, `derive.c`'s killed-`^` route optimization, the
  attempt loop's one-pass stop, `pcrec_nfa_has_bot`). Folding it would turn each of those
  into a recognizer of "`A_CTX` whose fn is prev-absent-only over the full set", a special
  case read off data. That is D62's principle working as intended: structure is a kind.
- **`$` and `\Z` (`A_EOL`).** "Before a FINAL newline" is the byte at `p` being `\n` AND the
  position `p + 1` being absent: two offsets ahead. An `A_CTX` reads one character each
  side. The extension it would need is a multi-offset context node (a set or absent bit at
  `p + 1`), which in the DFA IS the eol view (`DState.eolvar`, the `eol_ok` closure input).
  A multi-offset context is [ENG-LOOK]'s bounded-lookahead object ("bounded lookahead in
  the forward pass as a k-byte delayed acceptance"); building a second one here would be
  the duplicate path that row's ruling forbids. Stays `A_EOL`, with `N_EOL`, `eol_ok` and
  `eolvar` unchanged. D164's end-mark lowering keeps reading it (its `!multiline` clause at
  `src/ir/nfa.c:627` simply goes).
- **`\z` (`A_END`).** Expressible (`\z` ≡ `(?![\s\S])`, 547/547) and kept for `^`'s reason:
  `endwin.c`'s `EW_Z`, possessify's upward-closure exemption and `rev-end` read it as
  structure. `endvar` stays.
- **`\G`, `\K`.** Not context: a runtime value and a side effect.
- **D62 itself.** D62 rejected `A_EOL_M` (a kind per modifier) and put the modifier on a
  field. This design puts the modifier on NEITHER: the parser resolves `(?m)` into which
  NODE it builds, an existing general kind with data. D62's principle stands; its specific
  ruling ("multiline-`$` is a FLAG on the node") is superseded and needs an addendum (Q4).
  `N_BOT_M`'s own comment argued that after lowering the modifier is "a DIFFERENT
  ASSERTION … a different expression over different inputs"; under `N_CTX` that difference
  is the fn, which is data, the same argument `\b`'s retirement into `A_CTX` already won.

### 4.4 The census (by grep, `2ce4a1124`)

Search: `command grep -rn '\bA_BOL\b\|\bA_EOL\b\|anch\.multiline\|N_BOT_M\|N_EOL_M' src
--include=*.c --include=*.h`, plus `nl_bit`, `CTXROW_NEWLINE`, `PCREC_NO_MLINECTX` and
`CTXFN_`/`ctxfn`/`u.ctx.fn`. Comment-only lines are counted separately at the end.

**A. The `multiline` field's 16 code reads: 14 DELETED, 2 become the GENERIC node choice.**

| site | today | after |
|---|---|---|
| `src/parse/parse.c:1681` | `^` → `A_BOL` + field | GENERIC: `(?m)` ? `A_CTX({\n}, PREV_ABSENT_OR_IN_NEXT_PRESENT, anchor)` : `A_BOL` |
| `src/parse/parse.c:1696` | `$` → `A_EOL` + field | GENERIC: `(?m)` ? `A_CTX({\n}, NEXT_ABSENT_OR_IN, anchor)` : `A_EOL` |
| `src/parse/mod_assertions.c:224-225` | `\A`/`\Z` pin false | DELETED |
| `src/ir/nfa.c:620` | `? N_BOT_M : N_BOT` | DELETED (`A_BOL` → `N_BOT`) |
| `src/ir/nfa.c:627` | end-mark tail `!multiline` | DELETED clause |
| `src/ir/nfa.c:636` | `? N_EOL_M : N_EOL` | DELETED |
| `src/opt/possessify.c:649` | multiline `$` widens | DELETED (the `A_CTX` arm widens, or arm A values it) |
| `src/opt/derive.c:226` | `lb \|\| multiline` keeps `^` | DELETED clause (`(?m)^` reaches the `A_CTX` arm at `:231`, same result) |
| `src/opt/derive.c:291` | `!multiline` counts `bol_out` | DELETED clause |
| `src/facts/startanch.c:117` | multiline → 0 | DELETED (the `A_CTX` arm at `:130` returns `acc`, the same) |
| `src/facts/endwin.c:138` | multiline → `EW_NONE` | DELETED (`A_CTX` at `:150` returns `EW_NONE`) |
| `src/facts/endwin.c:296` | `!multiline` pushes the tail | DELETED clause |
| `src/facts/widths.c:129` | multiline → `EM_ANY` | DELETED (`A_CTX` at `:123` returns `acc`, the same) |
| `src/facts/widths.c:131` | the same for `$` | DELETED |
| `src/gen/emit_vm.c:8893` | the `(?m)^` arm (27 lines) | DELETED → a `vm_ctx_forms` row |
| `src/gen/emit_vm.c:8931` | the `(?m)$` arm (13 lines) | DELETED → a `vm_ctx_forms` row |

Also DELETED: the field itself and its 73-line control-3 comment
(`src/core/internal.h:1381-1454`). With it the `anch` payload has no member left, so the
union arm goes; `mod_assertions.c`'s pin on the other kinds (which "aliases nothing and is
read back nowhere", its own comment) goes with it.

Every row's "after" was checked by reading the `A_CTX` arm of the same switch: in all 14
deleted cases it already returns what the multiline branch returns. That is the
simplification stated precisely: **each multiline branch was a hand-copy of the `A_CTX`
answer.**

**B. `N_BOT_M`/`N_EOL_M` and the newline row: 12 further code lines, 9 DELETED, 2 sites
GENERIC, plus the row's plumbing.**

| site | after |
|---|---|
| `src/core/internal.h:2014-2015` (the enum members) | DELETED |
| `src/ir/dfa.c:696-697` (`eps_edge` labels) | DELETED |
| `src/ir/dfa.c:1071-1078` (two closure arms) | DELETED; the `N_CTX` arm (`:1083-1088`) reads three-valued sides |
| `src/facts/kset.c:139-140` (labels) | DELETED |
| `src/ir/dfa.c:171-174` (`cr_nl_reads`/`cr_nl_set`), `:190-191` (`ctx_rows[CTXROW_NEWLINE]`) and `:156` (the row id) | DELETED: the newline set enters through the `ctx` row like every `A_CTX` set |
| `nl_bit`: `src/ir/dfa.c:769`, `:832`, `:1147`, `:1643`, `:1648` | DELETED |
| `PCREC_NO_MLINECTX`: `src/ir/dfa.c:262-264` | DELETED (its check retires, §4.5.4) |
| `src/ir/nfa.c:1316` (`pcrec_nfa_has_bot`) | GENERIC: `N_CTX` with `ctxfn_reads_absent_prev` |
| `src/ir/dfa.c:1589-1590` (`has_end` hoist) | GENERIC: `N_CTX` with `ctxfn_reads_absent_next` |

**C. Truth-function readers that EXTEND (8 sites, become wider, not special).**
`src/core/internal.h:1157-1163` (two functions added, six re-encoded), `Ast.u.ctx.fn` and
`NState.ctxfn` (`:2064`) widen; `src/ir/dfa.c:1086` (index `3p + q`);
`src/opt/possessify.c:266` and `pcrec_poss_ctx_admits` (a third polarity; its exhaustive model
check `tests/possessify/ctx_admits_check.c` extends); `src/gen/emit_vm.c:8354-8361` (two
rows); `src/opt/dfamemo.c:67`, `src/ir/nfa.c:664`, `:1110` (copies, width only);
`src/parse/ctxnode.c:109-110` and `src/parse/mod_assertions.c:134` (re-encoded constants,
same names).

**D. STILL SPECIAL, and why: 84 code lines naming `A_BOL`/`A_EOL`.** A comment-excluding
grep finds 87 code lines in `src/` that name `A_BOL` or `A_EOL` (internal.h 3, endwin.c 4,
req.c 2, startanch.c 2, startset.c 2, widths.c 2, emit_vm.c 11, nfa.c 2, altcls.c 2,
atomic.c 10, derive.c 5, lower_enc.c 3, mrl.c 7, possessify.c 9, revdet.c 5,
select_engine.c 1, ctxnode.c 1, definitions.c 3, mod_assertions.c 3, mod_backrefs.c 1,
mod_lookaround.c 1, mod_vars.c 1, parse.c 3, registry.c 2, rxt_compose.c 2). Three of them
change: `parse.c:1681`/`:1696` become the node choice and `mod_assertions.c:224` is deleted.
The other 84 STAY, every case label and switch arm included, because the kinds survive for
`^`/`\A` and `$`/`\Z`. Where one of those arms holds a table-A branch, only the branch goes;
every other arm already shares its label list with `A_CTX` or answers the same way.
**The survey's "38 `A_EOL` references under `src/opt/`" (add. 1) is therefore not the
deletion count**: those references are these labels, and they survive. The deletion is
tables A-B, and its real content is the hazard class it removes (below).

Also STILL SPECIAL: `N_BOT`, `N_EOL`, `N_END`; the DFA's eol/end views (`eol_ok`, `end_ok`,
`DState.eolvar`/`endvar`, `emit_view_select`), which `$`/`\Z`/`\z` need and which
`(?m)$` keeps reading through its fn; `CTXROW_NOSTART` (K50's gate, not an `A_CTX`); and the
registry's `^`/`$` rows (`src/parse/registry.c:1549-1600`), whose `bol_def`/`eol_def` text
stays as documentation and oracle (add. 1) while their description strings ("D62's
field+fold lowering") are rewritten (a `--list-syntax` text change, §4.5.2).

**What the deletion buys, stated as special cases removed.**
1. D62's accepted residual disappears: no analysis can match `case A_EOL:` and forget a
   field, because the field does not exist, and `(?m)` forms arrive at every exhaustive
   switch as `A_CTX`, which `-Wswitch` already forces each analysis to classify. D62
   control 3's obligation comment (73 lines) and its K63 census-in-a-comment go.
2. Three of the four sabotage rows that exist only to keep a field reader honest (S77,
   S762, S900) lose their subject (§4.5.4).
3. The DFA's class axis has ONE contributor for every assertion set (`ctx`), plus K50's gate.
4. The VM has one context emitter (`vm_ctx`) for eight functions instead of one for six
   plus two hand arms.
5. Part 1's producer needs no `(?m)` rows (§3.3).

### 4.5 Cost

#### 4.5.1 The abi event and its readers (D76/D94, by grep)

Any moved byte makes it an abi event: 80 → 81. Readers of the number at `2ce4a1124`:

| reader | site |
|---|---|
| the define | `src/gen/emit_dfa.c:54` `#define PCREC_ARTIFACT_ABI 80` |
| the codegen pin | `tests/codegen/run_codegen_tests.sh:3149` `ABI_EXPECT=80` |
| the identity gate's (B) pin | `tests/codegen/run_recursion_identity.sh:1262` `FILEPIN` (re-pinned to the landing commit) |
| the not-bumped plant | `tests/mech/sabotages/S693_abi_not_bumped.sh:57-58` (`SAB_BEFORE`/`SAB_AFTER` name 80/79) |
| the spec's number sentence | `docs/spec/match_api.md` §6¶17 ("It is `80` on every artifact") |
| the log | `docs/dev/history/abi_changelog.md` (new entry) |

`src/gen/CLAUDE.md` names the define by line (`emit_dfa.c:51`, stale: it is `:54`); no
number. Per D94's addendum, the suites that count run too even where they never cite the
number: registry, codegen, rxtsource.

#### 4.5.2 Spec hunks (D80)

`--emit-ir`'s VM `assert` rows' role text for the two forms changes to the `vm_ctx_forms`
rows' (a DEBUG listing, D106; `docs/spec/ir_listing.md` gets a hunk only if it quotes the
two strings, to check at build). `--list-syntax` descriptions of `^`/`$` change (the
`registry.c` strings). `--emit-facts`' `start_anchor`/`end_pin`/widths rows do not change
(table A's "after" column is answer-identical by reading).

#### 4.5.3 Is byte identity reachable?

- **VM: reachable by construction, to be measured.** The two `vm_ctx_forms` rows can emit
  today's expressions character for character, and the class pool interns the same newline
  bitmap. One unexplained difference was seen while probing, and the build must account for
  it: `x(?m)$` and its `A_CTX` twin `x(?![^\n])` differ by an extra `goto rx_L3; rx_L3:`
  hop in the former (besides the expected bitmap). It is not yet known which arm adds it.
- **DFA: reachable except where the context-set list's ORDER changes.** The closure is the
  same predicate over the same bits (§4.2), and the alphabet is unchanged: class numbering
  is by lowest member byte whatever the refinement order (`eqclasses`'s comment). What can
  move is the list order. Today the newline set is listed AFTER every `A_CTX` set; after the
  change it is listed in NFA order with them. A machine with ONE context set, or whose
  `(?m)` nodes come after every other `A_CTX` set in NFA order, or whose newline set is
  shared with a `(?=\n)`/`(?<=\n)` already in the list, keeps its order and its bytes. A
  machine with a `(?m)` node BEFORE a different `A_CTX` set (`(?m)^\bfoo`) gets its atom
  vectors' bits in another order, so its atoms renumber and every per-atom table permutes.
  Those artifacts are ANSWER-IDENTICAL MOVERS. Preserving their bytes would need a
  contributor rule that sorts "absent-aware sets last", which is a rule invented to keep
  bytes, the ghost add. 1 tells us not to keep. Leaning: accept and count them (CK-4).
- **Listing and stamps:** no stamp names a multiline kind; `RX_*` stamps read engine and
  route facts, which do not change (`has_bot`/`has_end` are preserved by §4.2's
  predicates).

So the event is "abi bump, measured movers", not "byte-identical": the identity gate pins
(B) at the landing commit, and the mover population is a measured, answer-identical set.

#### 4.5.4 Checks that move

| check | effect |
|---|---|
| `tests/codegen/run_mlinectx_identity.sh` (wave C's gate: a `(?m)`-free pattern pays nothing for the newline axis) and its knob | RETIRES: the axis it guards is the general `ctx` row, which `run_wordctx_identity.sh` already guards with `PCREC_NO_WORDCTX` |
| `tests/lib/mlscan.py` (`multiline_anchor`/`multiline_caret` classifiers for three scripts) | KEPT: it classifies PATTERN TEXT, not kinds; its comment naming `N_BOT_M`/`N_EOL_M` is reworded |
| S76 (mlinectx alphabet unconditional, `src/ir/dfa.c`) | RE-AIM: the plant becomes "the `ctx` row adds a set no `N_CTX` reads" |
| S77 (possessify ignores multiline, anchor `possessify.c:649`) | RE-AIM: "the `A_CTX` arm takes `A_EOL`'s upward-closure exemption" (the failure D62 control 2 protected against, in its new form) |
| S762 (end pin reads `(?m)$`, anchor `endwin.c:138`) | RE-AIM: "`endwin.c`'s `A_CTX` arm returns `EW_EOL`" |
| S900 (derive kills a multiline `^`, anchor `derive.c:226`) | RE-AIM: "`derive.c`'s `A_CTX` arm kills it as `^`" |
| S343 (a shared context set records only the first row) | REACH CHECK: its witness relied on `(?=\n)` and `(?m)^` sharing an entry from two ROWS; after the change both are the `ctx` row, so the witness may stop reaching ([MECH-REACH]) |
| `tests/possessify/ctx_admits_check.c` | EXTENDS to the third polarity (exhaustive) |
| emit_sweep, startset manifests, `run_form_census.sh` floors | re-pinned for the measured DFA movers (CK-4) |

#### 4.5.5 What it costs in code, roughly

Deleted: ≈ 160 lines (the field and its comment ≈ 75, the two VM arms ≈ 40, the closure
arms, the contributor row, `nl_bit`, the knob, the labels ≈ 45). Added: two `CTXFN_*` rows
and their VM form rows, two fn predicates, the three-valued closure index, the possessify
polarity ≈ 40 lines. The net is small in lines; the gain is in kinds of thing a reader must
know about.

---

## 5. Open questions (discussion, each with a leaning)

**Q1. Does part 1's context half land at Z2 with UL-0, or later?** The forces: kit_proof
stages UL-0 at Z2 and keeps the machine reading as stage 1's context source (Q3 ruled);
UL-8 puts a facts-layer context source at U1b. F-1 (§3.8) shows the slice needs the in-span
half of §3.3 at Z2 anyway, or the trace build's C8 goes red on a mid-span `A_CTX`. Once the
in-span half exists, the out-of-span records are the same rule at offsets outside the span,
and listing them costs nothing in bytes. *Leaning:* the whole producer lands at Z2, listed
and used only as the C8-ctx control; the SOURCE switch waits for UL-8's trigger. That keeps
Q3's ruling and gives the control two producers from day one.

**Q2. Should part 2 happen at all before part 1 needs it?** Part 1 can be built without part
2 by giving the input table two `(?m)` rows (§3.3), and deleting them later. Memory
`pcrec-general-mechanisms-not-special-cases` allows implement-then-replace, but this replace
would be the abi event either way, and the rows would be written to be deleted. Frank has
said simplification alone qualifies. *Leaning:* part 2 FIRST, as its own abi event (P2a-P2c,
§7), then part 1 has no `(?m)` rows to write. If Frank prefers part 1 first (it moves no
bytes and is the kit's critical path), the two rows are the honest cost, labelled as such.

**Q3. Accept the DFA list-order movers, or keep bytes?** §4.5.3. A rule "absent-aware sets
last" keeps every byte and is a rule with no meaning except byte keeping. Ordering by NFA
position is today's rule for `A_CTX` sets and is the rule a reader would guess. *Leaning:*
accept the movers, count them at build (CK-4), state the population in the abi log. If the
count is surprising (more than the `(?m)`-plus-other-context population the corpus has),
that is a finding about the list, not a reason for the rule.

**Q4. D62's addendum.** D62's principle survives and its specific ruling (the flag) is
superseded. The addendum would say: the modifier is resolved into the CHOICE OF NODE at
parse time; a kind is still never doubled per modifier; `$`/`\Z`/`^`/`\A` keep their kinds as
structure. *Leaning:* Frank rules it at the same time as Q2, because the addendum is what
makes the deletions of table A legitimate rather than a reversal.

**Q5. Is `$`/`\Z`'s two-offset fact worth a multi-offset `A_CTX`?** It would let `A_EOL`
retire too and let the producer state "the byte at `W` is `\n` and `W + 1` is absent". In
the DFA it is the eol view under a new name, so it buys no engine simplification; in the
producer it is a record pair with a JOINT absent condition, which the per-offset carrier
cannot say. *Leaning:* no. It is [ENG-LOOK]'s bounded-lookahead object; file it as that
row's instance (UL-e, §10) and leave `A_EOL` a kind.

**Q6. Should the producer state `pos-start`/`pos-end` records with no consumer?** They cost a
table row each and are true. A record no one reads is a latent default by memory
`pcrec-no-silent-defaults`'s definition only if something USES it unchecked; here nothing
reads it. *Leaning:* keep the rows (the table needs no exception for two kinds) but do not
SEND them anywhere until U-z or a T-CUT change asks.

---

## 6. Checks (each against a source the subject does not share; sabotage ids PROPOSED, not allocated)

Ids `SP-1`.. are this note's placeholders. The manager allocates real S-ids from
`worktrees/.mgr/sabotage_ids.txt`, outside the kit's reserved ranges.

| id | check | expectation from | sabotage (PROPOSED) |
|---|---|---|---|
| CK-1 | C8-ctx: on every DFA artifact where `MkEnd` states a context set, the producer's EXACT record equals it, or the producer is silent; a producer-EXACT record the machine contradicts fails | the anchored machine's seed table (a different object, built by a different walk) | SP-1: the fold uses `S_0`'s complement (`\b` before a word byte states `prev ∈ W`); must fail CK-1 and CK-2 |
| CK-2 | soundness and exactness against libpcre2 10.46: for every corpus `m` cell, every match's context bytes lie in each record (absent per its bit); for EXACT records, a full-alphabet subject family at the context offsets finds no subject that satisfies the records and the body and that libpcre2 rejects (kvcensus's C4 method generalized) | libpcre2 | SP-2: `look-fixed` marks an alternation EXACT (`(?<=ab\|cd)`); must fail CK-2's exactness half |
| CK-3 | the listing invariant: one artifact's records carry ONE `form`; `nctx` 0 when no item contributed; no UNSTATED enum in a listed record | the listing, read by a python reader that shares no code with `spans.c` | SP-3: a record with `absent` left UNSTATED; refused at the reader |
| CK-4 | part 2's movers: emit_sweep over every arm, answer-identical by the three-way self-oracle; the byte movers are exactly the DFA artifacts with a `(?m)` node before another `A_CTX` set in NFA order (predicted from pattern text by `mlscan.py` plus a python NFA-order read), and the VM movers are zero or explained | libpcre2 (answers) and a text-side prediction (population) | SP-4: the parser builds `A_BOL` for `(?m)^` (the D62 failure in its new form); must go red in `test-assertions` |
| CK-5 | reverse-machine identity for every `(?m)$` artifact on `ENG_UNANCH` (the `sides_of` point, §4.2) | the pre-change build's reverse tables | SP-5: the absent-aware `N_CTX` arm reads `bot_ok` for the right side in reverse; must break CK-5 and a `(?m)$` corpus cell at `startpos > 0` |
| CK-6 | F-1's in-span rule: `exact_len` stops at a straddling two-sided `A_CTX` and refines `S_d` at a one-sided one, on witnesses `a(?=b)[a-z]`, `[a-z0-9_ ]\b[a-z ]`, `\w(?=\d)\w` | libpcre2 prefix languages (X0's method, kit_proof §6.4) | SP-6: the slice passes every zero-width node through (kit_proof §5.2's sentence as written); must fail CK-6 |
| CK-7 | K35: the population of artifacts with ≥ 1 context record, counted by a stamp-free text census (kvctx.py's shape), floors as measured literals | python over pattern text | — (a count, not a plant) |

Each plant needs a REACH witness ([MECH-REACH]): SP-1/SP-2/SP-6 by name above; SP-4 any
`(?m)^` cell after a final newline (`(?m)^$` on `"a\n"`); SP-5 a `(?m)$` artifact routed
`ENG_UNANCH` with a match ending before an internal newline.

## 7. Staging

| step | what | movers |
|---|---|---|
| P2a | re-encode `CTXFN_*` to 9 cells (absent copied from out); widen `fn`/`ctxfn` | 0 (CK-4 asserts zero) |
| P2b | the two new functions, their `vm_ctx_forms` rows, the three-valued closure, the two fn predicates, possessify's third polarity; nothing builds them yet | 0 |
| P2c | the parser builds `A_CTX` for `(?m)^`/`(?m)$`; delete tables A-B; retire `run_mlinectx_identity.sh`; re-aim S76/S77/S762/S900; D62 addendum; abi 81 | the measured DFA list-order movers (CK-4), answer-identical |
| P1a (= kit_proof Z2) | `span_facts`' slice WITH §3.3's table (in-span and out-of-span), listed in `--emit-facts` (`facts_listing.md` hunk), CK-1..CK-3, CK-6, CK-7 | 0 bytes; listing only |
| P1b (= UL-8's trigger) | the producer's EXACT records become the context source for the first VM-side consumer; the machine reading becomes the control | per that consumer's own event |

P2a-P2b are the dangerous part only in that they touch the closure; they move nothing and
can land early. If Frank orders part 1 first (Q2), P1a lands with the two `(?m)` table rows
and P2c deletes them.

## 8. The three standing questions (`docs/design/CLAUDE.md`)

1. **The measurement regime: NOT RELEVANT to a decision here.** No timing is read or
   produced. The only measurements are compile-only probes and libpcre2 equivalence runs
   (547 cells per pair, method in the header). Part 2's mover count is a compile-only census
   at build. Any speed effect of part 2 (possessify's arm A on `(?m)` gates) is a VM mover to
   be read by the bench later, not a premise of this design.
2. **The independent control: RELEVANT.** §6: CK-1 compares two producers that share no code
   (the facts walk and the DFA's seed table); CK-2 and CK-6 read libpcre2; CK-3's reader is
   python; CK-4's population is predicted from pattern text, not from the compiler; CK-7 is
   K35's text census. Each plant names its reach witness.
3. **What moves when data is regenerated: RELEVANT, narrowly.** The producer reads no table,
   prior or measurement set; regenerating any of them moves none of its records. Part 2 is
   an abi event once, at P2c, with the readers of §4.5.1, and re-pins emit_sweep, the startset
   manifests and the form-census floors for its measured movers. The `bol_def`/`eol_def`
   definitions stay oracle input only; regenerating the oracle store moves nothing here.

## 9. SIBLING-OF-A-FAMILY

- **The position-pin family** (window_contract §5.6: `start_set`, the k-set, `run_pin`,
  `end_pin`/`end_window`, compound's split facts, landmark K, `span_facts`). The context
  producer is NOT a new member: it is `span_facts`' own walk extended to offsets outside the
  span, so the family's count does not grow. The unified position-pin record that §5.6
  proposes (each member a projection) gains the context records as a projection too. Its
  trigger is unchanged (U3's, or S4's offset-k move).
- **The context family** (kit_proof §8.2 "Context as a per-position fact"): MLINE's `{\n}`
  predicate, the 23 shifted origins, the seed table, the VM's `A_CTX`, the `-bounded` view
  family, D164's end set, and kvctx.py's reading. This note gives the family its ONE
  producer. The members are now: one producer (this), one machine reading (`MkEnd`, the
  control), and consumers (MLINE, shifted origins, `cover`). A unified TABLE is due and is
  §3.3's input table: it is the declared row table that decides, per zero-width kind, what
  context it contributes (memory `pcrec-decisions-as-first-match-tables`).
- **The absent rule** (kit_proof §8.2): `\A`/`^`, `\z`, MLINE's edge, `\G`'s `search_from`.
  Part 2 adds the engine side of the same rule: the absent cell in `A_CTX`'s truth function.
  One meaning of "absent" now runs from the node (the fn's absent cells) through the producer
  (`MkAbsent`) to the carrier (`mf_pred.absent`). They are three spellings of one enum's
  meaning across three layers, which is a layering, not a dispersal; no unification is due.
- **The assertion family** (`A_BOL`, `A_EOL`, `A_END`, `A_CTX`, `A_GSTART`, `A_KRESET`). Part
  2 is this family's consolidation: assertions that read a CHARACTER become `A_CTX`, and
  assertions that test a POSITION (`\A`, `\z`, `\G`) or a two-position fact (`$`/`\Z`) stay
  kinds. That is a rule a reader can state in one line, which today's split is not.
- **The `\b` rewrite family** (kit_proof UL-6, the definitions table's `\b` row, possessify's
  arm A valuation, kvctx's positional rewrite): the fold of §3.4 is the one READING; arm A is
  the one OPTIMIZER use; UL-6 is the BOONIES lowering. Arm A and the fold both compute "which
  bytes does this gate admit on one side given the other", so arm A's `pcrec_poss_ctx_admits`
  is a candidate shared helper for §3.4's `ctx-fold` row. *Leaning:* share it at P1a if its
  signature fits (it works on code-point intervals and byte bitmaps already), rather than
  writing a second fold.

## 10. UNLOCKS, each with its trigger (filed, not designed beyond it)

| id | unlock | trigger (D77) |
|---|---|---|
| UL-a | the facts-layer context source for VM-only patterns (kit_proof UL-8) | U1b / [CAPS-KNOWN]'s first VM-side consumer |
| UL-b | wider lookbehind context (`(?<=ab)z`) sent as a FILTER on seeded DFA sites, which the machine reading cannot state (kit_proof §3.3, "NO" row) | kit_proof U4's trigger: a measured seeded `\b…` or lookbehind cell |
| UL-c | possessify arm A values `(?m)^`/`(?m)$` gates (part 2's side effect) | lands with P2c as a measured VM mover; no separate trigger |
| UL-d | MLINE's `absent` SATISFIES and pcrec's edge attempt retires (kit_proof U-mline), read off the producer's `ctx-fold` record | U-mline's own: a `(?m)^` cell whose edge attempt is measured |
| UL-e | `$`/`\Z` as an instance of [ENG-LOOK]'s bounded lookahead (a multi-offset context), retiring `A_EOL` | [ENG-LOOK]'s design gate |
| UL-f | the 23 shifted-origin sites restated from the producer's records, origin = the match start (kit_proof U-ctxorigin) | its own: one such site in a losing bench cell |
| UL-g | the producer as the prefilter's context oracle: a SUPERSET record is a necessary condition any search filter may test | a filter consumer asking for it (none today) |

## 11. Findings filed (doc findings, not fixed here)

- **F-1 (kit_proof §5.2):** "every zero-width node passes through" overstates `exact_len` on
  a mid-span `A_CTX` or lookahead (§3.8); C8 would report `producers-disagree` and the trace
  build would go red. Fix: the in-span half of §3.3, at Z2.
- **F-2 (stale path):** `src/opt/ctxnode.c` is named in `src/core/internal.h:759`,
  `src/ir/nfa.c:654` and this lane's brief; the file is `src/parse/ctxnode.c`.
- **F-3 (stale name):** `pcrec_ctx_set_bytes` is named in `src/core/internal.h:774`, `:2017`
  and `src/enc/enc.h:505`; the function is `pcrec_enc_set_bytes`.
- **F-4 (stale line cite):** `src/gen/CLAUDE.md` cites `emit_dfa.c:51` for
  `PCREC_ARTIFACT_ABI`; it is `:54`.
- **F-5 (add. 1's measure):** the "38 `A_EOL` references under `src/opt/`" are case labels that
  survive the fold (§4.4 D); the deletion is the 14 + 9 sites of tables A-B.

## 12. What a review should attack

(a) §4.2's claim that the DFA closure is the same predicate: is `bot_ok` exactly "left
absent" on every forward closure, including `s1u[]`/`s1g[]` interior starts and `\G`'s family?
(b) The reverse machine on `(?m)$` (CK-5). (c) §3.4's "next side must exist" on a span 0
whose offset 0 is reached through an `A_ALT` with a nullable branch. (d) §3.6's alternation
rule when one branch has a record and the other has none (the note says: no record; is
"union with all bytes" ever exact?). (e) Whether any reader of `pcrec_nfa_has_bot` relies on
the KIND `N_BOT_M` beyond routing (emit_dfa's P0 assertion reads `s0` vs `s1u[PLAIN]`). (f)
The DFA mover prediction (CK-4): is NFA order the only thing that moves? (g) The VM `rx_L3`
hop (§4.5.3).
