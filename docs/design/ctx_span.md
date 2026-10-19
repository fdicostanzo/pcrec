# ctx_span — [DD-11.5] re-scoped: the span-context producer (D168) and `A_BOL`/`A_EOL` into `A_CTX` (D168 addendum 1); DESIGN NOTE, PROPOSED, nothing built

**Revision 2.1** (lane `ctxspan21`, opus, design only, 2026-10-19, main `fd1d1fc98`, abi 80).
It applies the re-check of revision 2 (the section "Re-check of revision 2 (critR ...)" at
the end of `docs/dev/reviews/2026-10-18-r4-ctx-span.md`): R1-R4 ACCEPTED, unlocks U1/U2
filed. Changed text is marked `[r4rc <id>]`. Read §R2.1 first; §13 maps every re-check id to
its discharge. Nothing was built, run or measured for 2.1: the box was in a bench timing
window, so every new claim is read off the source or the note, and what needs a run is
marked OWED with its command.

**Revision 2** (lane `ctxspan2`, opus, design only, 2026-10-18, main `3b0f87b55`, abi 80).
It applies review r4 (`docs/dev/reviews/2026-10-18-r4-ctx-span.md`): every finding is
ACCEPTED except C3, which ruling Q-r4-1 REJECTED; the rulings Q-r4-1..Q-r4-3 are applied.
Changed text is marked `[r4 <id>]`. Read §R2 first. Every r4 id is mapped to the place that
discharges it in §13. Revision 1 was lane `ctxspan` (main `2ce4a1124`).

`src/`, `tests/`, `lib/` and `docs/spec/` are byte-identical between `2ce4a1124` and
`3b0f87b55`, so every `file:line` below holds at both. Re-grep at the build commit. Every
list that revision 1 made by hand is now DERIVED, and the recipe and the derived list are
both given (§4.4, §4.5.1, §4.5.4). Evidence: `ctx_span/` (own CLAUDE.md). It holds the edit
set, the derived sabotage population, the reader greps and the `\A`/`\z` census aid.

Revision 1 ran every equivalence it claims between two spellings against libpcre2 10.46 on
this box. The method: an anchored match at every start, over all 547 (subject, start) cells
of `{a, \n, x}` up to length 4 (`build/probe/eqv.c` in that lane's worktree, not committed).
Revision 2 adds three compile-only probes with this tree's `build/pcrec`. Nothing under `src/`
changed.

The charter is D168, D168 addendum 1 and plan row [DD-11.5]. Inputs:
`docs/dev/dd11_family_2026-10-18.md`, `kit_proof.md` (revision 2.1 plus the r4 edits this
lane made, each marked `[r4 <id>]` there), `memfn/window_contract.md`, `ucp_design.md`
(UD-2), `definitions_table.md`, `docs/dev/kvcensus.md`, `docs/dev/eng_look_census.md` and
the [ENG-LOOK] row.

---

## §R2.1. What revision 2.1 changed (finding → section)

- **R1 (MAJOR): the absent index is gated on the ROW** (§4.2.3). Revision 2 applied
  `right_abs = end_ok` (and the mirror) to every row. When `has_end` holds, the `V_END` view
  is closed under every context atom, so a copied row (`\b`, `(?=C)`) would read the next
  byte as absent where today it reads the atom's bit. On `\bfoo\b` that interns an `endvar`
  where today there is none. The index is now `q = (right_abs && ctxfn_reads_absent_next(fn))
  ? 2 : bit(right)`, and the mirror for `p`. That is today's six functions and today's
  `N_BOT_M`/`N_EOL_M` arms exactly, so P2a's zero-mover argument is restored on that basis.
  P2d's zero movers rest on the same gate. A consequence: no reverse machine ever meets an
  absent-prev-reading row, so A1's per-direction read cannot be reached by any witness, and
  S341's re-aim moves to R1's plant (§4.5.4, §6 CK-5).
- **R2 (BLOCKER if built): in-span narrowing is PER THREAD** (§3.4, §3.6, §3.8, kit_proof
  §5.2). Narrowing the whole per-offset UNION is unsound under alternation: `a(?=b)[a-z]|ac`
  would drop `c` from `S_1`, and `[ab](?<=a)c|bc` would drop `b` from `S_0`. On the next side
  the walk restricts only the classes of frontier states reached THROUGH the item. On the
  previous side it narrows only when every thread at `d − 1` passes the item, and otherwise
  ends `exact_len` at `d − 1`. The narrowed sets live in the SLICE'S OWN RECORD (`MkLang`).
  `KsetWalk.k[]` stays the pass-through hull, so the k-set consumers (offset-k selection, the
  run pin, the OFS rows, the listing) are unmoved by construction (§3.8). Both witnesses join
  CK-6, `conj.txt` D and X0's list as text. The union-narrowing plant is PROPOSED (SP-6 here,
  S1150 in kit_proof §6.3). `conj.py` does not model the in-span rule; that is OWED (§3.8).
- **R3 (MINOR): a multi-byte newline convention is REFUSED BY NAME until UL-e** (§3.3). After
  P2c no fallback kind exists, since `N_BOT_M`/`N_EOL_M` are deleted.
- **R4 (MINOR): the edit set is checked against the real diff** (§4.5.4, §7). At build the
  lane regenerates the edit set from the actual P2a-P2c diff and compares it with
  `ctx_span/edit_set.tsv`. The derived sabotage list is taken from the regenerated set.
- **Unlocks U1 and U2 are filed** (§10). U1 makes absent its own context atom (the ⊥
  pseudo-character). U2 is R2's fix written once, in the shared frontier iterator `wclose`.

## §R2. What revision 2 changed

- **Part 2 is ONE declared truth table** (Q-r4-1, §4.2). A context function is a 3×3 grid,
  with "no character" (absent) as a visible third value on each side. The six existing
  `CTXFN_*` functions are rows of that grid, and so are `(?m)^` and `(?m)$`. The table shows
  each row's three derived predicates and its VM form. C3's composition alternative is
  REJECTED; §4.2 says why in a paragraph.
- **The reverse machine's absent reading is fixed** (A1, §4.2.3). `Sides` carries
  `left_abs`/`right_abs`, and `sides_of` sets them per direction. The forward machine takes
  `bot_ok`/`end_ok`. The reverse machine takes `end_ok` on the right and never on the left.
  `[a-z]+\b` at `n` joins CK-5.
- **A second census, for `\A` and `\z` as rows** (§4.6). The outcome splits by layer. In the
  ENGINE layer (NFA kinds, closure arms, VM arms) everything deletes. In the ANALYSIS layer
  eight sites read the two kinds as structure, and none deletes. The leaning is an NFA-level
  fold, its own step P2d after the multiline fold. `$`/`\Z` and `\G` stay kinds (ruled).
- **The kit carrier claim is corrected** (B1, §3.9). `byte_form` is not a `memfn.h` field.
  Stage 1 sends EXACT items only, one `ctx[]` entry per context ITEM (U-B4, §3.6). The
  exactness fact is filed as R-26.7, with UL-b/UL-g as its trigger. kit_proof §4.1/§4.3 were
  edited to match.
- **F-1 is wider than revision 1 stated, and kit_proof is edited** (B9, §3.8). The
  pass-through rule is limited to position-only kinds, and the in-span half of §3.3 joins
  UL-0 at Z2. The three witnesses go into `conj.txt` D and into X0's family. X0's set
  equality runs on every site stating `exact_len > 0`. Plant S1149 is PROPOSED.
- **The producer EXTENDS `pcrec_kset_walk`** (C4, Q-r4-3, §3.1, §3.10). There is no new
  `spans.c` walker, and kit_proof's naming is updated.
- **Possessify's arm A keeps WIDENING absent-reading functions at P2c** (B3, §4.2.5).
  Valuing them is UL-c, its own event with its own mover prediction. Every `nullable` reader
  sees today's value (A4).
- **Every list is derived** (B2, B5, B6, C1, §4.4, §4.5.1, §4.5.4). The abi readers come from
  a grep recipe. The sabotage re-aims and retirements come from an edit set plus the anchor
  map. The knob's test readers come from a grep. One identity gate's population is re-defined
  (A2/B4).
- **Staging is free** (Q-r4-2, §7). Part 2 lands at its build go. If that falls between the
  kit's Z1 and B1, the affected kit evidence is re-run (§7 lists it), with the `conj.py` re-run
  at P2c as the independent control (U-B3).
- **The checks are rebuilt** (B7, §6). CK-1 gets a non-silence floor. CK-2 generates
  absent-edge subjects. CK-4 confines each mover's diff to tables. CK-5 is taken modulo the
  predicted permutation. Per-row populations are counted. SP-4 gets a reaching witness, and
  SP-4b and SP-4c are added.

---

## 0. Answers first

| question | answer |
|---|---|
| what part 1 is | ONE producer, `span_facts`' first slice (kit_proof UL-0), computed by EXTENDING `pcrec_kset_walk` (`src/facts/kset.c`) `[r4 C4, Q-r4-3]`. It states one context record per context ITEM `[r4 U-B4]` before span 0 and after its end. It refines span 0's own `S_d` with the same rule where an item stands INSIDE the span (§3) |
| its one rule | every zero-width item contributes, relative to its own position, a per-offset set list with an `absent` cell. Outside the span the list is a context record; inside, it intersects `S_d` or ends `exact_len`. `\b`/`\B` contribute only once the neighbouring side is known (the FOLD). A first-match INPUT TABLE (§3.3) maps each zero-width kind to its contribution. Its lookaround rows CALL the recognizer instead of restating it `[r4 C5]`. No kind has a private arm |
| what it is not | a tree rewrite: no engine's bytes move, and the producer READS `A_CTX` nodes and `A_LOOK` bodies (D168) |
| what it sends the kit | stage 1 sends EXACT items only, one R-26 `mf_site.ctx[]` predicate per item with `absent`. There is no exactness field, because none exists: `byte_form` is not in `memfn.h` `[r4 B1]`. The exactness fact is filed as R-26.7, triggered at UL-b/UL-g. Facts only (D157) (§3.9) |
| relation to kit_proof | one design. Stage 1's source stays the machine reading (Q3, RULED). The producer's in-span half is UL-0's own at Z2 (F-1). Its out-of-span half lands with it as the C8-ctx control. It becomes THE source at UL-8's trigger (§3.10) |
| F-1 against kit_proof §5.2 | CONFIRMED and WIDER `[r4 B9]`. The false `exact_len` is stated on EVERY start-origin FIND site, and the k-set walk the sent sets come from passes `N_CTX`. So a false claim is on the wire wherever a site sends a k-set across an in-span item, latent while `consumable_len` is 0. kit_proof is edited (§3.8) |
| what part 2 is | `(?m)^` and `(?m)$` leave `A_BOL`/`A_EOL` and become `A_CTX` over the newline set, as rows of ONE declared 9-cell truth table. Each side is `out` / `in` / `absent`, and the six existing functions are rows of the same table `[r4 Q-r4-1]` (§4.2). The `multiline` field, `N_BOT_M`, `N_EOL_M`, the newline contributor row and its knob are deleted (§4.4) |
| the surprising fact | `(?m)$` ≡ `(?![^\n])` (libpcre2, 547/547), but that spelling is an `A_CTX` only under `byte`. Under utf8 `[^\n]` is not byte-expressible and forces the VM, so the `{\n}`-plus-absent row is REQUIRED for utf8, not merely chosen for byte identity `[r4 A5]`. `(?m)^` needs "the next character exists" (40 of 547 cells differ from `(?<![^\n])`, all after a final newline) |
| what does not fold | `$`/`\Z` (two offsets) and `\G` (a runtime value) stay kinds, as RULED. `\A` (prev absent) and `\z` (next absent) are rows of the table on paper. A second census (§4.6) finds that their ENGINE readers delete and eight ANALYSIS readers do not. *Leaning:* fold them at the NFA layer only, as step P2d after the multiline fold `[r4 Q-r4-1]` |
| census headline | 16 `multiline` code reads: **14 deleted, 2 become the generic node choice**. `N_BOT_M`/`N_EOL_M` and the newline row: **27 further code lines by grep, 24 deleted, 3 generic**, `dfa.c:345` included `[r4 C1]`; plus the `rows` sharing logic P2c leaves dead (two lines and the reads in two functions) `[r4 B5]`. 31 comment lines in `src/` name them and are reworded `[r4 C1]`. **84 code lines naming `A_BOL`/`A_EOL` stay** (§4.4) |
| cost | an abi event (80 → 81) with its readers found by a grep recipe `[r4 B2]` (§4.5.1). The byte movers are ONLY DFA machines whose context-set list ORDER changes. There are zero VM movers, zero route flips and zero possessify movers at P2c `[r4 B3, C6]`. Each mover's diff is confined to tables (CK-4). Five sabotage rows retire, one re-aims, 24 re-run, all derived (§4.5.4). One identity gate retires and one changes population `[r4 A2]` |
| contradicts D168? | No. Two precisions (§3.5, §11). D168's "width-1 negative lookbehind" means one BYTE on the lowered tree, and a TYPED `(?<!é)` is two bytes under `byte` too `[r4 A6]`. Part 2's census shows the deletion is smaller than add. 1's survey figure suggested |

---

## 1. Problem

Two things carry the same fact today in separate places.

1. **Context around a search span.** The kit's find-window contract (window_contract §2.2,
   "Context predicates"; kit_proof §3, §4.1) can use what is known about the subject before
   span 0's offset 0 and after its end. Today that knowledge exists in four forms:
   - MLINE's `{\n}` CONTEXT predicate at −1;
   - the 23 `scan-restart/ctx` sites, which send a width-1 lookbehind as a shifted origin
     (kvcensus §6);
   - the DFA's seed table and class-indexed accept, which encode `\b` by position;
   - kit_proof's stage-1 machine reading (§3.2), which reads the context off the anchored
     DFA.

   Each reads a different object, and a VM-only pattern gets none of it. D168 rules ONE
   producer of per-offset sets in `span_facts`.

2. **The assertion family's special cases.** `\b`, `\B` and every one-character lookaround
   are one node, `A_CTX` (UD-2), with the truth function as DATA. `(?m)^` and `(?m)$` are
   not. They are `A_BOL`/`A_EOL` with a parse-resolved `multiline` field (D62), lowered to
   two dedicated NFA kinds `N_BOT_M`/`N_EOL_M`. Each has its own closure arm, its own
   contributor row on the DFA's class axis, its own VM arm, and a field every analysis must
   remember to read. D62 accepted that last cost in so many words: "the compile alarm that
   would cover unimagined [consumers] is forgone" (D62, residual). Frank (add. 1):
   simplification alone qualifies.

The two problems meet. Without part 2, part 1's producer needs an arm for "`A_BOL` with
`multiline` set" to state MLINE's context, which is the special case part 2 deletes. With
part 2, `(?m)^` before a consuming item is an `A_CTX` the fold already reads.

## 2. Forces

- **One mechanism per fact** (memory `pcrec-general-mechanisms-not-special-cases`; D122). The
  context fact must have one producer. A per-spelling arm in that producer re-creates the
  dispersal D168 removes. The same force applies to the WALK: one per-offset walker, not a
  fourth `[r4 C4]`.
- **One declared table** (memory `pcrec-decisions-as-first-match-tables`; Q-r4-1). A truth
  function is a row of one visible table, not a hex constant beside five others. Its derived
  properties are computed from the row, never written beside it.
- **Read, do not rewrite** (D168; kit_proof §3.2). A tree rewrite moves every engine's bytes
  for no answer change.
- **Facts, never methods** (D157). The record says what is true of every match. Which kit
  row tests it is the kit's.
- **No silent defaults** (memory `pcrec-no-silent-defaults`; window_contract §2.3). Every
  enum in the record has an UNSTATED zero, refused where read.
- **Proof vs filter** (D168; kit_proof C8). An inexact record may filter (a necessary
  condition) and may never prove. In stage 1 only EXACT items leave pcrec `[r4 B1]`.
- **D62's principle**: kinds encode STRUCTURE, fields encode PARSE-RESOLVED MODIFIER STATE.
  Part 2 must not add a kind per modifier (D62 rejected `A_EOL_M`), and it does not. It
  maps a modifier choice onto an existing GENERAL kind with data (D168 add. 1).
- **The [ENG-LOOK] ruling**: "NO one-character fold ships anywhere — it is the duplicate
  path." That ruling is about ENGINE code (a second DFA path for one-class bodies). The
  producer is a READING in the facts layer, ruled by D168. Part 2 moves `(?m)` ONTO the
  one class-axis mechanism [ENG-LOOK] would generalize.
- **Abi pre-release** (memory `pcrec-abi-changes-pre-release`): an abi event is ritual, not
  avoidance.
- **Staging is free** (Q-r4-2, Frank: "not worried about interim states"). The order is the
  manager's. The design states what each order costs, not a preferred order.
- **Build under measurement** (D77; memory `pcrec-discuss-before-launch`): nothing is built
  ahead of Frank's build go.

---

## 3. Part 1: the span-context producer

### 3.1 What exists

- `A_CTX` (`src/core/internal.h:776`, its comment block above): a code-point set
  `u.ctx.iv`/`n` and a 4-bit truth function `u.ctx.fn`, bit `(p << 1) | q`. "Absent" (start
  or end of subject) reads as NOT in the set. There are six functions (`CTXFN_*`,
  `src/core/internal.h:1157-1163`). Part 2 re-encodes them (§4.2).
- The recognizer (`src/parse/ctxnode.c`, §11 F-2) turns a lookaround into one `A_CTX` when
  the body's LANGUAGE is a set of single characters and that set is byte-expressible
  (`pcrec_enc_set_bytes`). Everything else stays `A_LOOK`, which the NFA erases to `N_EPS`
  and the VM executes. Under `-fno-ctx-node` (`PCREC_NO_CTX_NODE`, bit 35) the recognizer
  does not run, and every lookaround stays `A_LOOK` `[r4 A6]`.
- **The per-offset walk exists** `[r4 C4, Q-r4-3]`. `pcrec_kset_walk` (`src/facts/kset.c`,
  fact `kset_walk`, E3) walks the lowered NFA from `Nfa.anch_start`. Per offset `j` it keeps
  the frontier (closed over epsilon and over every assertion, which it PASSES) and records
  the union of the frontier's classes. That union is `S_j` for the hull, up to
  `PCREC_PREFIX_K_MAX` (24, `limits.def`). `req.c` and `widths.c` are two more per-offset
  walks. Revision 1's `span_facts` slice in a new `src/facts/spans.c` would have been a
  fourth.
- `span_facts` is NOT BUILT. kit_proof §5.2 designs its first slice (UL-0: `S_d`,
  `exact_len`, the hull at the match-start origin, priority-free) and builds it at Z2,
  now as the extended k-set walk (kit_proof §5.2 `[r4 Q-r4-3]`). window_contract §5.2
  designs the whole producer (segments, hull spans, prefix sums).
- kit_proof's stage-1 context is the machine reading `MkEnd.ctx_before`/`ctx_after` with
  `absent_before`/`absent_after` (kit_proof §3.2, §5.1), DFA-only.

### 3.2 The record and where it lives

The record extends kit_proof's pattern-fact record `MkLang` (`src/facts/known.h`, kit_proof
§5.1). A context set is a property of the same language, at the same origin, on the same
lowered machine, filled by the same walk. A separate record would be a second home for one
walk's output.

```c
/* src/facts/known.h -- span_facts' context half (ctx_span.md §3). ONE RECORD PER CONTEXT
   ITEM [r4 U-B4] (a \b, a lookbehind, a lookahead), its terms at every offset outside
   span 0 it constrains. Byte sets (mf_term.set's layout), on the lowered machine. Every
   enum has an UNSTATED zero, refused where read. */
typedef enum { MK_ABS_UNSTATED = 0, MK_ABS_SATISFIES, MK_ABS_FAILS } MkAbsent;
typedef enum { MK_CTX_UNSTATED = 0, MK_CTX_EXACT, MK_CTX_SUPERSET } MkCtxForm;
typedef struct {
    int8_t    off;        /* < 0: before span 0; >= the end W: after it             */
    uint8_t   set[32];    /* the byte at `off` lies in `set`                        */
} MkCtxTerm;
typedef struct {
    uint8_t   nterm;      /* 1..PCREC_CTX_ITEM_TERMS                                */
    MkCtxTerm term[PCREC_CTX_ITEM_TERMS];
    MkAbsent  absent;     /* when a term's offset is outside the subject             */
    MkCtxForm form;       /* EXACT: the terms are EQUIVALENT to the item; SUPERSET: a
                             necessary condition only. LISTED, never sent in stage 1 */
} MkCtx;

typedef struct {
    uint8_t  stated;                       /* MK_LANG_UNSTATED 0, MK_LANG_STATED    */
    uint8_t  exact_len;                    /* 0..PCREC_PREFIX_K_MAX (the walk's)     */
    uint8_t  set[PCREC_PREFIX_K_MAX][32];  /* S_d, d < exact_len                    */
    uint8_t  nctx;                         /* 0 = no context fact (not "none holds") */
    MkCtx    ctx[PCREC_CTX_ITEMS];         /* one per item, in walk order           */
} MkLang;
```

- **The grain is the ITEM** `[r4 U-B4, B1]`. Revision 1 keyed records by OFFSET and needed
  stacking rules: intersect at a shared offset, `absent` SATISFIES only if every item's does,
  EXACT only if every item's is. Per item, the conjunction of the items IS the context, and
  the kit binds several predicates as a conjunction already. So pcrec states no stacking
  rule (§3.6), and `form` is a property of one item. A whole artifact's context is exact iff
  every item is.
- **The bounds are the producer's own** `[r4 B10]`. Revision 1 sized the record by the
  kit's carrier constants (`MF_MAX_BACK`, `MF_MAX_AHEAD`, `MF_MAX_CTX`). That contradicted
  its own rule that "the producer states what the item gives and the carrier truncates".
  The walk's bound is `PCREC_PREFIX_K_MAX`. `PCREC_CTX_ITEM_TERMS`, the widest item, is
  DERIVED from it: an item's offsets lie within `PCREC_PREFIX_K_MAX` of the span edge on its
  side. `PCREC_CTX_ITEMS` is a compile budget in `limits.def` (D90), labelled UNMEASURED
  until P1a counts items per artifact (memory `pcrec-suspect-tuning-constants`). A walk
  that would exceed one states the item SUPERSET, or drops it and records the drop in the
  listing, never silently. The carrier's bounds are
  applied at SEND (§3.9). A consumer that needs the context COMPLETE (`cover`) declines when
  an item is dropped at send; a filter consumer may send fewer.
- **`nctx` 0 is "no context fact"**, which every reader treats as "the context is
  unconstrained". It is never read as "a context that always holds".

### 3.3 The input table (first match, one row per zero-width kind)

The producer is the k-set walk's frontier advance. When the frontier holds a zero-width
state, the state contributes through this table instead of being passed (kset.c's
`wdrain` passes every assertion today, §3.8). No row names a spelling. A kind not in the
table is a compile error (no `default:`; mrl.c's rule). Each row has a POPULATION FLOOR
measured at P1a (CK-7, U-B2) `[r4 B7]`.

| row | kind and predicate | contribution (offsets relative to the item's position `p`) | form |
|---|---|---|---|
| `ctx-onesided` | `N_CTX` whose truth-table row reads ONE side (§4.2's `reads` columns) | that side's set, or its complement where the row admits `out`, at `p − 1` (prev) or `p` (next). `absent` is the row's absent cell (§4.2) | EXACT |
| `ctx-fold` | `N_CTX` whose row reads BOTH sides (`\b`, `\B`, `(?m)^`), where the OTHER side's set at this position is KNOWN and lies wholly inside or wholly outside `C` | the row restricted by the known side, which is a one-sided test of the remaining side (§3.4) | EXACT |
| `ctx-unfold` | `N_CTX`, both sides, with the other side unknown or straddling `C` | none (D168 "Revisit when": a two-offset relation is not a per-offset set). Inside span 0 it ENDS `exact_len` at the item's offset | — |
| `look-fixed` | an `A_LOOK` the recognizer DECLINED, positive, every branch of fixed BYTE width. The predicate is `ctxnode.c`'s own walk called on the body, not restated `[r4 C5]` | per offset, the union over branches of the branch's byte set, right-aligned at `p` (behind) or left-aligned (ahead). An offset beyond a branch's width takes ALL bytes, and absent SATISFIES for that branch. `absent` FAILS within every branch's width | EXACT iff one branch whose language is the product of its per-offset sets; else SUPERSET |
| `look-neg-1` | `A_LOOK` negative, body of fixed width ONE BYTE | the complement of the body's byte set; absent SATISFIES | EXACT |
| `look-neg-wide` | `A_LOOK` negative, wider than one byte | none (a disjunction, not a product; D168). Inside span 0 it ends `exact_len` | — |
| `look-other` | `A_LOOK` of variable width, or with a capture, reference or call in its body | none | — |
| `pos-start` | `N_BOT` (`\A`, non-multiline `^`) | at `p − 1`: the empty set, absent SATISFIES | EXACT |
| `pos-end` | `N_END` (`\z`) | at `p`: the empty set, absent SATISFIES | EXACT |
| `pos-eol` | `N_EOL` (`$`, `\Z`) | none: "before a FINAL newline" is a two-offset fact. Inside span 0 it PASSES THROUGH to the hull (kit_proof §5.2, position-only), and C9 keeps the position constraint on A | — |
| `pos-other` | `N_GSTART`, `\K`'s slot write, `N_CSTART` | none (`\G` is a runtime value, `\K` constrains nothing, the K50 gate is unreachable from `anch_start`, kset.c) | — |

- **`look-neg-1` is reached only under `-fno-ctx-node`** `[r4 A6]`. A width-1-byte negative
  lookbehind whose set is byte-expressible is recognized into `A_CTX` and takes
  `ctx-onesided`. A TYPED `(?<!é)` is two bytes even under `-e byte`, because the pattern
  text is UTF-8 (`C3 A9`), so it is `look-neg-wide`. The row is kept because the recognizer
  can be denied. Unlock (§10, UL-h): the producer's records with and without
  `-fno-ctx-node` must be IDENTICAL on every artifact. That is a free check of the
  recognizer and the `look-*` rows against each other (CK-10).
- **The newline convention** `[r4 A3]`. `(?m)^`/`(?m)$` are `ctx-*` rows only because
  today's convention is LF, a one-byte newline. The rule is: `(?m)` is an `A_CTX` iff the
  active convention's newline is ONE byte. CRLF is a two-offset fact, and ANY/ANYCRLF are
  cross-set facts (a CR/LF pair, or several newline bytes and sequences). Those conventions
  are UL-e's multi-offset object, not this row. The selection lives where the convention
  does, at `definitions_table.md`'s convention-selector customer ([DD-11]'s newline axis).
  When a convention row is added, the parser's `(?m)` choice reads it, and a multi-byte
  convention keeps `(?m)` off `A_CTX`.
- **`pos-start`/`pos-end`** produce a record no stage-1 consumer reads. An anchored pattern
  takes T-CUT's `anchored` row and has no window site (window_contract §5.4), and `\z` is
  U-z's (kit_proof §8.3). They are rows because the fact is the same fact. If P2d is taken
  (§4.6), they become `ctx-onesided` on the `\A`/`\z` rows of §4.2's table, and these two
  rows delete.

If part 1 lands BEFORE part 2 (staging is free, Q-r4-2), the table carries two more rows,
`A_BOL`/`A_EOL` with `multiline` set: `(?m)^` → `{\n}` at −1 when the next side is
consuming, and `(?m)$` → `{\n}` at `p` with absent SATISFIES. P2c deletes them, because
its items arrive as `N_CTX`. That is the honest cost of that order, labelled as such.

### 3.4 The fold: previous set × next set

`\b` at position `p` holds iff `W(prev) ≠ W(next)`, absent reading as not-`W`. Once the
next side's set `N` is known, the fold applies. `N` is span 0's `S_0` when `p` is the
origin, `S_d` inside the span, or the context record at `p` when one is already stated.

| `N` vs `W` | `\b` becomes | `\B` becomes | absent |
|---|---|---|---|
| `N ⊆ W` | `prev ∉ W` (`(?<!\w)`) | `prev ∈ W` | `\b` SATISFIES, `\B` FAILS |
| `N ∩ W = ∅` | `prev ∈ W` (`(?<=\w)`) | `prev ∉ W` | `\b` FAILS, `\B` SATISFIES |
| straddles | no per-offset fact (`ctx-unfold`) | the same | — |

The mirror holds at the end. With the previous side known (`S_{W−1}`), a trailing `\b`
becomes a test of the byte at `W`. libpcre2 confirms both measured directions:
`\bx` ≡ `(?<!\w)x` and `\b\n` ≡ `(?<=\w)\n` (547/547 each). The fold is the same
computation for every both-sides row of §4.2's table. Restrict the row by the known side's
value and read off the remaining column, absent cell included.

**The next side must EXIST.** The fold declines if span 0 can be empty at the origin (the
body is nullable there), because then the byte after `p` may be absent or anything. The
same condition makes `(?m)^` foldable (§4.2): `(?m)^x` ≡ `(?<![^\n])x` (547/547), and
`(?m)^a?` ≢ `(?<![^\n])a?` (40 differ, all with no byte after the position). The condition
is read off the walk's frontier, not off the tree. An `A_ALT` with a nullable branch at the
origin puts `N_ACCEPT` in the offset-0 frontier, and the walk stops before any fold (kset.c,
stop condition (a)). That answers revision 1's §12 (c).

**One fold, three placements.**
- **Before span 0**, the result is a context record at −1.
- **Inside span 0**, for an item between offsets `d − 1` and `d`, a one-sided result
  intersects `S_{d−1}` or `S_d`. A two-sided item folds against whichever of `S_{d−1}` and
  `S_d` lies wholly inside or wholly outside `C`, and intersects the other. A straddle on
  both ends `exact_len` AT `d`: positions `[0, d)` stay exact, and the length-`(d+1)`
  prefixes are no longer the product `[r4 A9]`. Revision 1 said `d − 1`, which is one short.
  Witness: `[a-z0-9_ ]\b[a-z ]`, where `d` = 1 and `exact_len` = 1. It admits `a ` and ` a`
  and not `ab`.
- **After the end**, the result is a record at `W`.

kvcensus's context reading (method, "Context") used exactly the first and third placements
and measured them as an equivalence (C4, 0 of 6,510 disagreements).

### 3.5 Lookbehind and lookahead bodies

- **Width is BYTES on the lowered machine.** The producer runs after `lower_enc`, as the
  walk does, so `(?<=é)` under `-e utf8` is two offsets `{C3} {A9}`, EXACT. D168's "width-1
  negative lookbehind" therefore means one BYTE. A typed `(?<!é)` is "not (C3 then A9)",
  a disjunction over two offsets, under EITHER encoding, so it DECLINES under
  `look-neg-wide` `[r4 A6]`. Revision 1 said it takes `look-neg-1` under `-e byte`, which is
  wrong for typed text. Only the escape spelling `(?<!\xe9)` is one byte under `byte`, and
  the recognizer turns that into `A_CTX`. This is a precision of D168, not a contradiction.
- **Alternation inside a lookbehind** (D168): `(?<=ab|cd)` gives `{a,c} {b,d}`, SUPERSET
  (`ad` passes the terms and not the body), so it is LISTED and not sent in stage 1
  `[r4 B1]`. `(?<=a|bc)` right-aligns: −1 is `{a,c}`, and −2 is constrained by branch 2 only.
  So −2's union is all bytes with absent SATISFIES, which is no term.
- **Lookahead after the end** mirrors lookbehind before the start, left-aligned at `W`.
- **A lookbehind's body is never a span.** The producer reads its per-offset byte sets with
  the walk's own frontier advance applied to the body. It does not descend for any other
  purpose, which keeps window_contract §5.2's decline "a lookaround's body is never
  descended" true for the HULL and its segments.

### 3.6 Combining items

- **Several items at one offset** (`(?<=[a-z])\b\w`) are SEVERAL records `[r4 U-B4]`. The
  context is their conjunction, and the kit binds several `ctx[]` predicates as one. So
  revision 1's stacking rule (intersect, absent-AND, form-AND) is RETIRED, not moved to the
  kit. Inside span 0 each item still narrows `S_d` in turn, which is a set intersection on
  the walk's own sets and not a record.
- **Top-level alternation** (`\bfoo|\bbar`): an item contributes a record only if every
  branch states the same item at the same position. Then the language is that context times
  the alternation of bodies, and the record is EXACT. Otherwise the branches' records
  are unioned per offset into one SUPERSET record (listed, not sent). A branch that does not
  constrain an offset contributes all bytes there, so that offset is no term. Revision 1
  §12 (d) asked whether "union with all bytes" is ever exact. It is not: it is no fact.
- **Repeats** contribute their body's items only at `rmin ≥ 1`, on the first (leading) or
  last (trailing) iteration. That is the walk's own frontier rule.

### 3.7 Encoding

- `A_CTX` sets are CODE POINTS (`u.ctx.iv`). An `A_CTX` exists only where its set is
  byte-expressible (the recognizer's conjunct; `\b`'s port asks the same). The NFA's
  `N_CTX` carries the byte set already (`NState.cls`, filled through `pcrec_enc_set_bytes`,
  `src/enc/enc.c:403`). The producer reads that and samples nothing.
- Under the precondition, "the previous CHARACTER is in `C`" equals "the previous BYTE is in
  `C`". Every member of `C` is one byte, and a multi-byte character ends in a continuation
  byte, which is not in `C`. So an `A_CTX` record at −1 is exact byte-wise under utf8. That
  is kit_proof §3.3's "utf8 and `\w`" argument in general form.
- `A_LOOK` bodies are read lowered, so their sets are bytes by construction.
- UCP `\b` under utf8 is refused by the parser today (`[UCP]` U3/U4), so the producer never
  sees a non-byte-expressible word set.
- **Side simplification, filed as an idea, not designed** (Q-r4-1; §4.7).
  `pcrec_enc_set_bytes` could admit CO-FINITE sets under utf8 ("some ASCII plus every
  non-ASCII character"). That would un-force the VM for `(?![^\n])` and `(?<![a-z])`. The
  open question is ill-formed utf8.

### 3.8 How it joins the slice, and F-1 against kit_proof §5.2 (CONFIRMED, wider)

The context half and the slice are ONE walk, the extended k-set walk `[r4 C4, Q-r4-3]`.
The walk computes the frontier offset by offset. When the frontier holds a zero-width
state, it consults §3.3 instead of passing the state. A contribution at an offset inside
the span intersects `S_d`. One outside the span becomes a record. A decline inside the span
ends `exact_len`.

revision 2.1's kit_proof §5.2 said that "a zero-width assertion constrains WHERE a byte may
stand, and not WHICH byte", so every zero-width node passes through to the hull. That is
true of POSITION-ONLY kinds (`$`, `\Z`, `\z`, `^`, `\A`, `\G`, `\K`). It is false of `A_CTX`
and of lookarounds. On `a(?=b)[a-z]` the pass-through slice states `S_0 = {a}`,
`S_1 = [a-z]`, `exact_len` 2, while the language is `{ab}`. The HULL is still sound, but
`exact_len` is overstated.

**Wider than revision 1 stated** `[r4 B9]`. kit_proof §5.2 states `exact_len` over the
SENT sets on EVERY start-origin FIND site, not only on `cover` candidates. The sent sets come
from the k-set walk, which PASSES `N_CTX` (`src/facts/kset.c`, `wdrain`'s assertion list,
`:131-141`). So under kit_proof as written, a site whose sent positions straddle an in-span
context item states a false `exact_len` on the wire. It is latent while `consumable_len` is 0
there, and it is a defect the trace build asserts zero of (`exact/producers-disagree`).

**The fix, applied to kit_proof as text** (each edit marked `[r4 B9]` there):
- §5.2's pass-through is limited to position-only kinds;
- the in-span half of §3.3 is UL-0's own at Z2;
- the witnesses `a(?=b)[a-z]`, `\w(?=\d)\w` and `[a-z0-9_ ]\b[a-z ]` are added to
  `conj.txt` D (`witnesses.txt`) and to X0's subject family, with subjects on both sides of
  each item's set edge;
- X0's per-byte set equality runs on EVERY site stating `exact_len > 0`;
- sabotage S1149 (PROPOSED) plants the pass-through.

`conj.py` on the three witnesses (machine half of C8 only, this lane, `3b0f87b55`) reads
`cover` k=2, `cover` k=2 and `exact`. A's `S_1` is `{b}` and `\d`, and the third body's
language is not a product. The extended walk must state the same. The plant's slice states
`[a-z]` and `\w`, and so reads `exact/producers-disagree` (kit_proof §6.3 S1149).

### 3.9 How the find-window contract carries it (facts only, D157) `[r4 B1]`

Revision 1 said "nothing new is asked of the kit: R-26's `ctx[]` plus the EXISTING
`byte_form` for exactness". That was false three ways. `byte_form` is not a field of
`memfn.h`. kit_proof §6.2 had already superseded window_contract §2.2's `byte_form` paragraph
by `exact_len`. And R-26's `ctx[]` has no exactness field. The corrected mapping:

| `MkCtx` | `mf_pred` (one per item, in `mf_site.ctx[]`) | note |
|---|---|---|
| each `term` (`off`, `set`) | one term at `off`, in `[−MF_MAX_BACK, 0)` or `[k, k + MF_MAX_AHEAD)` | `k` is the span's end, `W` here; a term outside the carrier's range drops the ITEM at send (§3.2) |
| `absent` | `absent` (`SATISFIES` / `FAILS`) | the same enum, UNSTATED refused there |
| `form` | — (NOT carried) | stage 1 sends EXACT items only; a SUPERSET item is listed and never sent |
| — | `consumable`, `need`, `span_class` CONTEXT | pcrec's consumer decides `consumable`; `need` is T-NEED's |
| — | site `read_floor` `MF_FLOOR_SUBJECT` | kit_proof §3.5; a below-origin term is refused under `MF_FLOOR_LO` |

- **The entry grain is the item** (§3.2, U-B4). kit_proof §4.1 is edited to one entry per
  ITEM everywhere. Its revision-2.1 derivation of `MF_MAX_CTX` as "one entry per offset"
  contradicted its own table. `MF_MAX_CTX` is now 2, derived from stage 1's one source (the
  machine reading: one item before, one after). Its trigger is UL-8, when the producer
  becomes the source.
- **The exactness fact is a new R-26 item, R-26.7, FILED at UL-b/UL-g's trigger**
  (kit_proof §4.3). It is a per-item `EXACT`/`SUPERSET` with an UNSTATED zero, a SUPERSET item
  being a filter and never a proof. Its customers are UL-b (a wider lookbehind sent as a
  filter on seeded DFA sites) and UL-g (the producer as a prefilter's context oracle).
  Neither exists, so nothing is asked now (D77).
- **Which items are SENT is pcrec's consumer's choice** (T-NEED, T-PROOF), not the
  producer's. The producer states every item. A site sends the EXACT ones, and a `cover`
  site declines when any item it needs is not sent (C8's rule applied to context, D168).
  Nothing in the record or its mapping names a kit method.

### 3.10 Relation to kit_proof: one design, not two

| kit_proof item | what this note does with it |
|---|---|
| §3.2 (READ, stage 1 DFA-only) and §8.4 Q3 (RULED: "the reading for stage 1 … the general form is a previous-set × next-set fold over `A_CTX`") | unchanged for stage 1: `MkEnd`'s machine reading is what `cover` sends at B1. The fold of §3.4 IS Q3's general form |
| §5.2 UL-0 (the slice, built at Z2) | the slice IS the extended k-set walk `[r4 Q-r4-3]`. Its in-span rule is UL-0's own (F-1, `[r4 B9]`). The out-of-span records are the same rule at offsets outside the span. They are listed in `--emit-facts`, sent nowhere in stage 1, and serve as the C8-ctx control (§6 CK-1) |
| §5.1 `MkEnd.ctx_before/ctx_after/absent_*` | stays as the machine reading, the C8-ctx control's other producer (CK-1) |
| §4.1 / §4.3 R-26 | the item grain, EXACT-only, `MF_MAX_CTX` 2 and R-26.7 filed, all edited there `[r4 B1]` |
| §8.3 UL-8 (the facts-layer context fact at U1b) | this producer IS UL-8's object, designed now. It becomes THE context source at UL-8's trigger (U1b / [CAPS-KNOWN]), with the machine reading demoted to its control |
| §8.3 UL-6 (a true lowering of `\b`, BOONIES) | unchanged and still BOONIES: this note lowers nothing |
| §8.3 U-mline | part 2 makes MLINE's context a `ctx-fold` record (`{\n}` at −1). U-mline then reads the producer's `absent` |
| §8.3 U-ctxorigin, U4 | the 23 shifted-origin sites and the seeded-DFA filters read the same records (§10) |
| §3.3's table | every "yes" row is a §3.3 row. The "NO" rows are `look-fixed` with width > 1 (producer-only, a filter at U4, so R-26.7's customer) and `pos-eol` (never) |

---

## 4. Part 2: retire the multiline forms into `A_CTX`

### 4.1 What exists

- The parser builds `A_BOL` for `^` and `A_EOL` for `$`. It writes `u.anch.multiline` from
  the scoped `(?m)` state (`src/parse/parse.c:1681`, `:1696`). `\A`/`\Z` build the same kinds
  and pin the field false (`src/parse/mod_assertions.c:224-225`).
- Lowering consumes the field once: `A_BOL` → `N_BOT_M` or `N_BOT`, and `A_EOL` → `N_EOL_M`
  or `N_EOL` (`src/ir/nfa.c:620`, `:636`).
- The DFA closure (`src/ir/dfa.c:1071-1078`) passes `N_BOT_M` iff `bot_ok || (left ∈ \n &&
  !end_ok)`, and passes `N_EOL_M` iff `end_ok || right ∈ \n`. The newline set reaches the class
  axis through its own contributor row `CTXROW_NEWLINE` (`src/ir/dfa.c:190-191`), after every
  `A_CTX` set (`ctx_collect` walks rows in order). Its list index travels as `nl_bit`.
- The VM has two dedicated arms (`src/gen/emit_vm.c:8893`, `:8931`) beside `vm_ctx`'s
  fn-keyed form table (`src/gen/emit_vm.c:8354-8361`).
- `pcrec_nfa_has_bot` (`src/ir/nfa.c:1313-1319`) routes any `N_BOT`/`N_BOT_M`/`N_GSTART`
  machine to `ENG_ATTEMPT` (its one caller is the route fork, `src/core/compile.c:2870`). The
  `has_end` hoist (`src/ir/dfa.c:1589-1590`) makes the `pos == n` view live for both
  multiline kinds.

### 4.2 The ONE truth table (RULED, Q-r4-1)

#### 4.2.1 The table

A context function answers, for one set `C`, whether the position passes given the
previous character `p` and the next character `q`. Each is `out` (not in `C`), `in` (in `C`)
or `absent` (no character: the subject's start or end). That is nine cells. Bit `3p + q`
holds the answer, with `out` 0, `in` 1 and `absent` 2, so `fn` is 9 bits wide (`uint16_t`).
**Every context function pcrec has is a row of this one table.** The six existing functions
are rows whose `absent` row and column are copies of `out`, because that is today's rule
("absent reads as NOT in `C`"). Part 2 adds two rows that do not copy. P2d (§4.6) would add
two more.

Each cell group below lists `p = out | in | absent`. Inside a group the cells are the
answers for `q = out in absent`.

| row (`CTXFN_*`) | built for | set `C` | `p=out` | `p=in` | `p=absent` | `fn` | reads absent prev | reads absent next | reads membership | VM form (today's text) |
|---|---|---|---|---|---|---|---|---|---|---|
| `BOUNDARY` | `\b` (mod_assertions) | word set | 0 1 0 | 1 0 1 | 0 1 0 | 0x0AA | no | no | yes | both sides, `!=` |
| `NONBOUNDARY` | `\B` | word set | 1 0 1 | 0 1 0 | 1 0 1 | 0x155 | no | no | yes | both sides, `==` |
| `PREV` | `(?<=C)` (recognizer) | `C` | 0 0 0 | 1 1 1 | 0 0 0 | 0x038 | no | no | yes | prev in set |
| `NOT_PREV` | `(?<!C)` | `C` | 1 1 1 | 0 0 0 | 1 1 1 | 0x1C7 | no | no | yes | prev not in set |
| `NEXT` | `(?=C)` | `C` | 0 1 0 | 0 1 0 | 0 1 0 | 0x092 | no | no | yes | next in set |
| `NOT_NEXT` | `(?!C)` | `C` | 1 0 1 | 1 0 1 | 1 0 1 | 0x16D | no | no | yes | next not in set |
| `MLINE_BOL` (new, P2b) | `(?m)^` (parser) | `{\n}` | 0 0 0 | 1 1 0 | 1 1 1 | 0x1D8 | **yes** | **yes** | yes | `scan_position == 0 \|\| (scan_position < subject_length && prev ∈ C)` |
| `MLINE_EOL` (new, P2b) | `(?m)$` (parser) | `{\n}` | 0 1 1 | 0 1 1 | 0 1 1 | 0x1B6 | no | **yes** | yes | `scan_position == subject_length \|\| next ∈ C` |
| `SUBJECT_START` (P2d, §4.6) | `\A`, `^` outside `(?m)` | — (reads none) | 0 0 0 | 0 0 0 | 1 1 1 | 0x1C0 | yes | no | **no** | `scan_position == 0` |
| `SUBJECT_END` (P2d, §4.6) | `\z` | — (reads none) | 0 0 1 | 0 0 1 | 0 0 1 | 0x124 | no | yes | **no** | `scan_position == subject_length` |

`MLINE_BOL` is libpcre2's `(?m)^` ≡ `\A|(?<=\n)(?=[\s\S])` (547/547). Its `in`/`absent`
cell is 0 because `(?m)^` does not hold after a FINAL newline. That is PCRE2's default, and
`PCRE2_ALT_CIRCUMFLEX` is the option that turns it on (`dfa.c`'s comment above `N_BOT_M`,
`docs/pcre2_options.md`). `MLINE_EOL` is `(?m)$` ≡ `(?![^\n])` (547/547), stated over `{\n}`
with the absent column set (§4.2.4 says why the set is `{\n}`).

**How the table is declared.** The table is ONE X-macro file of rows (`src/core/ctxfn.def`).
Each row holds a name, the GRID written as the three cell groups above, the VM form, and the
VM role text. The 9-bit value is DERIVED from the grid by one macro, so a reader sees the
grid, and a `_Static_assert` per row ties the name to it. The three predicates are COMPUTED
from the bits, never written as columns, because a written column would share a source with
the check that reads it (learnings §3):

- `ctxfn_reads_absent_prev(fn)`: the absent row differs from the out row;
- `ctxfn_reads_absent_next(fn)`: the absent column differs from the out column;
- `ctxfn_reads_membership(fn)`: the in row differs from the out row, or the in column from
  the out column.

These are DATA reads, the K96 shape, not kinds. For the six copied rows the first two are
false by construction, so no shipped `\b` or lookaround machine changes route or view.

**The control for the table** is CK-8 (§6). Each row is checked against libpcre2 through
its own canonical lookaround spelling over the 547-cell family (`\b` ≡
`(?<=\w)(?!\w)|(?<!\w)(?=\w)`, `(?m)^` ≡ `\A|(?<=\n)(?=[\s\S])`, ...). The expectation
therefore never comes from the bits.

**Why not C3's composition** (REJECTED, Q-r4-1). C3 spelled `(?m)^` as
`\A|(?<=\n)(?=[\s\S])`, built from existing 4-cell nodes, which deletes the fn widening and
the closure indexing. Its costs are four. It spells one fact as an alternation of nodes. It
adds a zero-width VM choice point. It needs a producer alternation rule. And under utf8
`(?=[\s\S])` is not byte-expressible (A5), so it forces the VM where the 9-cell row does not.
Frank ruled the table.

#### 4.2.2 Re-encoding the six

Each existing 4-cell function `f` becomes the 9-cell row `g(p, q) = f(p', q')`, where `absent`
maps to `out`. That is today's semantics by construction, so the six move no answer. Their
values are listed above. `u.ctx.fn` (`internal.h:1372`), `NState.ctxfn` (`:2064`), the builder
`pcrec_ast_ctx`'s parameter and `vm_ctx_forms`' key widen from `uint8_t` to `uint16_t`. The
values are never emitted: `vm_ctx_forms` keys on them, `dfamemo.c:67` compares them, and
`--emit-ir` prints role text, not the number. So the widening moves no byte. That is P2a.

#### 4.2.3 How the DFA reads absent, and A1's fix `[r4 A1]`

Revision 1 wrote `p = bot_ok ? absent : bit(left)`. That ignores direction. The reverse
machine's `s0` is built with `bot_ok` true (`src/ir/dfa.c`, the `make_state(... true, true,
UPC_PLAIN ...)` call for `d->s0`), but in reverse the MISSING byte is on the RIGHT. So
`[a-z]+\b`, a `reverse-pass` artifact, would read its left (a letter, `in`) as absent. That
gives (`out` by the copy rule, `out`), and the start is lost at `n`, so P2a's zero-mover claim
fails. CK-5 did not cover it.

The general form: the closure's sides are three-valued, and the absent bits are part of
`Sides`. They are set in `sides_of`, the ONE place that knows direction:

```c
typedef struct { uint32_t left, right; bool left_abs, right_abs; } Sides;
/* sides_of(m, cons, up, bot_ok, end_ok): forward -- left_abs = bot_ok,
   right_abs = end_ok; reverse -- right_abs = end_ok, left_abs = false (the
   reverse walk's left edge is its TERMINATION boundary, decided by the
   emitter's boundary accept, assertions_design §3.8.3.1, never by a closure) */
```

**The absent index is gated on the ROW** `[r4rc R1]`. Revision 2 wrote `p = left_abs ? 2 :
bit(left)` and the mirror for `q`, for every row. That is wrong for the copied rows. When
`has_end` holds, the end view (`V_END`, `end_ok` true) is closed under EVERY context atom
(`sides_of`'s `up_atom` ranges over the atoms, and the view is chosen at `pos == n`
afterwards). Today a row there reads the atom's bit on the right. Under revision 2's rule a
copied row would read absent instead, which is `out` by the copy. Take `\bfoo\b` after its
`o`, under `V_END × WORD`. Today the trailing `\b` reads left `in` and right `in` (the WORD
atom), so it FAILS. Under revision 2's rule it reads right absent, which is `out`, so it
PASSES. The end view's closure then differs from the eol view's, and `endvar` interns where
today it is −1. That flips `dfa_has_endvar`, the views flag, the `-bounded` forms and the
stamps. It hits utf8 unanchored forward machines with a copied next-reading row, and `\b` with
`\z` or `(?m)`. The answers do not change, since the end view is read only at `pos == n`, but
P2a's zero-mover claim is false under it. There is no third direction case.

The `N_CTX` arm indexes `3p + q` with the absent value taken ONLY where the row reads it:

```c
p = (left_abs  && ctxfn_reads_absent_prev(fn)) ? 2 : bit(left);
q = (right_abs && ctxfn_reads_absent_next(fn)) ? 2 : bit(right);
```

**This equals today's code exactly**, function by function:
- the six copied rows have both predicates false by construction (§4.2.1), so the index never
  takes 2. The arm computes `f(bit(left), bit(right))` over the same bits as today's `N_CTX`
  arm (`dfa.c`'s `(ctx_bit(cl->left, k) << 1) | ctx_bit(cl->right, k)`). "No byte on this
  side" still arrives as atom 0, the empty vector, as `sides_of`'s comment says;
- `MLINE_BOL` reads both. Its grid with `p = bot_ok ? 2 : bit(left)` and `q = end_ok ? 2 :
  bit(right)` passes iff `bot_ok || (left ∈ \n && !end_ok)`, which is today's `N_BOT_M` arm;
- `MLINE_EOL` reads the next side only. It passes iff `end_ok || right ∈ \n`, today's
  `N_EOL_M` arm;
- after P2d (§4.6), `SUBJECT_START` reads `bot_ok` (today's `N_BOT`) and `SUBJECT_END` reads
  `end_ok` (today's `N_END`).

**P2a's zero-mover argument, restored on that basis.** P2a re-encodes the six functions and
changes the index. Because the copied rows never take index 2, every closure of every view
under every atom computes today's bit, so no state's closure changes, `endvar`/`eolvar` intern
exactly as today, and the emitted bytes are today's. The witness the old rule would have moved
is `\bfoo\b` (an `endvar` interned at `V_END × WORD`). It joins CK-5's population and is the
plant's witness (S341 re-aimed, §4.5.4). **P2d's zero-mover claim rests on the same gate**: a
`\A`/`\z` row reads absent and takes index 2, and every copied row on the same machine keeps
its bit read, so folding `N_BOT`/`N_END` into rows moves no other row's closure.

**Per direction** `[r4 A1]`. `left_abs`/`right_abs` come from `sides_of`, the one place that
knows direction: forward `left_abs = bot_ok`, `right_abs = end_ok`; reverse `right_abs =
end_ok`, `left_abs = false`. This is the same predicate today's arms compute over the same
bits:
- `N_BOT_M` reads `bot_ok` forward. No reverse machine carries it, because `has_bot` routes
  it to `ENG_ATTEMPT`, which has no reverse pass (`nfa.c`'s `\G` comment states the same
  routing fact);
- `N_EOL_M` reads `end_ok` in both directions;
- `N_END` reads `end_ok` in both directions.

**A consequence of R1** `[r4rc R1]`: with the row gate, only absent-PREV-reading rows read
`left_abs`, and every such row (`MLINE_BOL`, and `SUBJECT_START` after P2d) sets `has_bot`.
So no reverse machine ever reads `left_abs`, and A1's bug (`left_abs` from `bot_ok` in
reverse) can no longer be reached by any witness. Revision 2's witness `[a-z]+\b` reads no
absent under the gate. A1's fix stays as the defensive form, backed by an assertion in the
closure: a reverse machine that meets an absent-prev-reading row is an internal error naming
the routing dependency. `[a-z]+\b` at `n` stays a CK-5 corpus cell. S341's re-aim moves to
R1's plant (§4.5.4).

The same mapping is the hook UL-e and [ENG-LOOK] extend, and U1 (§10) replaces it. The
forward absent read keeps `(?<![a-c])\d` at 0 as its corpus cell.

#### 4.2.4 Why both new rows are stated over `{\n}`, and A5 `[r4 A5]`

`(?m)$` ≡ `(?![^\n])` (547/547), and the recognizer turns that spelling into
`A_CTX(¬{\n}, NOT_NEXT)`, but only under `byte`. Under `-e utf8`, `[^\n]` contains every
non-ASCII character and is not byte-expressible, so the recognizer declines it and the
pattern takes the VM. So `(?m)$` "already an A_CTX" holds under `byte` only. Revision 1 called
the `{\n}` spelling a choice made for byte identity. Under utf8 it is REQUIRED, because it is
the only `A_CTX` spelling of `(?m)$` there is. Under `byte` there is a second reason for it.
Spelling `(?m)$` over the complement would put the newline byte and the absent side in one
atom, renumber every `(?m)$` DFA artifact's atoms and kill the `pos == n` view. Keeping `{\n}`
and putting absent in the row keeps today's atoms and today's `end_ok` reading, which is what
makes byte identity reachable (§4.5.3).

#### 4.2.5 The other engines' reads, and what possessify does

- **Routing and views.** `pcrec_nfa_has_bot` reads `N_BOT || (N_CTX &&
  ctxfn_reads_absent_prev) || N_GSTART`. The `has_end` hoist reads `N_END || N_CSTART ||
  (N_CTX && ctxfn_reads_absent_next)`. For `MLINE_BOL` both are true, as both `N_BOT_M` arms
  are today. For `MLINE_EOL` only `has_end` is true, as today. So `(?m)^` stays on
  `ENG_ATTEMPT` and `(?m)$` stays on `ENG_UNANCH`, with zero route flips `[r4 C6]`. Without
  the `has_bot` predicate, `(?m)^` would move to `ENG_UNANCH` at `compile.c:2870`. That is
  C6's engine-selection shift, and it is predicted here as ZERO because the predicate exists.
- **The class axis.** `cr_ctx_reads` stays `st->k == N_CTX`, and the newline set enters
  through the `ctx` row in NFA order. That is the list-order mover class (§4.5.3).
- **VM.** `MLINE_BOL`/`MLINE_EOL` are two `vm_ctx_forms` rows. Each emits today's expression
  text and today's role text verbatim (`"(?m)^ attempt_position of subject or after a
  non-final newline"`, `"(?m)$ end of subject or before a newline"`), and interns the set from
  `pcrec_cls_newline` (C7, §4.4).
- **The lookbehind fact** `[r4 A8]`. The `(?m)` node raises NOTHING. `<prefix>_VALID_LB` is
  not raised, because libpcre2 reports a maximum lookbehind of 0 for `(?m)^a`. The parser's
  builder must not copy `\b`'s `pcrec_lb_raise(cx, 1)` (`mod_assertions.c:102`), and the
  node carries `u.ctx.anchor = true` (spelled as an anchor, so `(?m)^*` keeps its grammar).
  CK-4's diff confinement catches a moved `VALID_LB` (it is not a table), and SP-4c plants it.
- **Possessify's arm A** `[r4 B3, A4]`. At P2c, `pcrec_poss_ctx_admits` returns "no
  narrowing" for every row with `ctxfn_reads_absent_prev` or `ctxfn_reads_absent_next` true.
  So arm A WIDENS `(?m)` gates exactly as `possessify.c:649`'s multiline arm does today
  (`bs_all`, `nullable` false). Revision 1 said arm A would then VALUE them, which would
  move VM bytes and possibly flip routes (poss_arms rev 2: arm A's bit is engine-selecting).
  That contradicted its own "only DFA list-order movers". Valuing is UL-c: its own event,
  with its own mover prediction and its own route census.

  A4 is discharged by VALUE IDENTITY. The `First` record cannot say "passes with no next
  byte", so any arm-A narrowing of an absent-reading row would hand every `nullable` reader a
  false non-nullable. At P2c every such row returns today's multiline value, so every reader
  sees the value it sees today. The readers are `possessify.c:198`, `:1020`, `:1021`, `:1073`,
  `:1311`, `:1407`, `:1413`, `:1555`, `:1623`, `:1653` and `:1984` (grep, `ctx_span/readers.txt`
  §7). The proof is CK-4's zero possessify movers, plus test cells `a{0,3}(?m)$`,
  `(?m)^a+b` and `[a\n]+(?m)$\n` in `tests/possessify/` (possdiff, both oracles). UL-c must
  first give `First` a third component ("admits absent") and re-prove each reader.
  `tests/possessify/ctx_admits_check.c` extends to the 9-cell universe. Its raw literals
  (`:169` `0xA`, `:172` `0x5`) become the `CTXFN_NEXT`/`CTXFN_NOT_NEXT` names, and its
  16-function loop (`:155`) becomes all 512 grids × the 7 non-empty left-polarity masks over
  three values.

### 4.3 What does not fold, and why it stays a kind

- **`$` and `\Z` (`A_EOL`): STAY KINDS (RULED).** "Before a FINAL newline" means the byte at `p`
  is `\n` AND the position `p + 1` is absent: two offsets ahead. In the DFA that is the eol
  view (`DState.eolvar`, the `eol_ok` closure input). A multi-offset context is [ENG-LOOK]'s
  bounded-lookahead object (UL-e), and building a second one here would be the duplicate path
  that row's ruling forbids. `N_EOL`, `eol_ok` and `eolvar` are unchanged. D164's end-mark
  lowering keeps reading `A_EOL`, and only its `!multiline` clause at `src/ir/nfa.c:627` goes.
- **`\G` (`A_GSTART`): STAYS A KIND (RULED).** Its truth is a runtime value (`search_from`),
  not a character. `\K` is a side effect.
- **`\A` and `\z`: rows of the table, decided by a second census** (§4.6). The leaning is an
  NFA-level fold as step P2d after P2c. The AST kinds stay for the analyses that read them
  as structure.
- **D62 itself.** D62 rejected `A_EOL_M` (a kind per modifier) and put the modifier on a
  field. This design puts the modifier on NEITHER: the parser resolves `(?m)` into which
  NODE it builds, an existing general kind with data. D62's principle stands, and its
  specific ruling ("multiline-`$` is a FLAG on the node") is superseded, which needs an
  addendum (Q4). `N_BOT_M`'s own comment argued that after lowering the modifier is "a
  DIFFERENT ASSERTION … a different expression over different inputs". Under `N_CTX` that
  difference is the row, which is data, the same argument `\b`'s retirement into `A_CTX`
  already won.
- **The residual: one choice stated twice** `[r4 C2]`. After part 2 the parser's
  `if (multiline)` choice and the registry's `bol_def`/`eol_def` `DEF_MULTILINE` rows
  (`src/parse/registry.c:1549-1600`) both say what `(?m)^` is. The table is documentation
  and oracle input (D168 add. 1), not a second producer, so this is a named residual, not a
  dispersal. A check ties the two (CK-9). The `DEF_MULTILINE` row's text, parsed by the
  ordinary parser, must be answer-identical to the parser's `(?m)^` node over the 547-cell
  family and libpcre2, so drift in either goes red.

### 4.4 The census (by grep at `2ce4a1124` = `3b0f87b55`; `ctx_span/readers.sh` §2-§6)

Recipe (code lines; comments counted separately):
`command grep -rnE 'anch\.multiline|N_BOT_M|N_EOL_M|nl_bit|CTXROW_NEWLINE|cr_nl_(reads|set)|PCREC_NO_MLINECTX' src --include=*.c --include=*.h`
filtered to non-comment lines. Revision 1 found these by the same search plus reading. The
lists below are that grep's output, classified (`ctx_span/readers.txt` §2).

**A. The `multiline` field's 16 code reads: 14 DELETED, 2 become the GENERIC node choice.**

| site | today | after |
|---|---|---|
| `src/parse/parse.c:1681` | `^` → `A_BOL` + field | GENERIC: `(?m)` ? `A_CTX({\n}, MLINE_BOL, anchor)` : `A_BOL` |
| `src/parse/parse.c:1696` | `$` → `A_EOL` + field | GENERIC: `(?m)` ? `A_CTX({\n}, MLINE_EOL, anchor)` : `A_EOL` |
| `src/parse/mod_assertions.c:224-225` | `\A`/`\Z` pin false | DELETED |
| `src/ir/nfa.c:620` | `? N_BOT_M : N_BOT` | DELETED (`A_BOL` → `N_BOT`) |
| `src/ir/nfa.c:627` | end-mark tail `!multiline` | DELETED clause |
| `src/ir/nfa.c:636` | `? N_EOL_M : N_EOL` | DELETED |
| `src/opt/possessify.c:649` | multiline `$` widens | DELETED (the `A_CTX` arm widens: §4.2.5) |
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
union arm goes, and `mod_assertions.c`'s pin on the other kinds goes with it. In all 14
deleted cases the `A_CTX` arm of the same switch already returns what the multiline branch
returns. **Each multiline branch was a hand-copy of the `A_CTX` answer.**

**B. `N_BOT_M`/`N_EOL_M` and the newline row: 27 code lines, 24 DELETED, 3 GENERIC.**

| site | after |
|---|---|
| `src/core/internal.h:2014-2015` (the enum members) | DELETED |
| `src/ir/dfa.c:696-697` (`eps_edge` labels) | DELETED |
| `src/ir/dfa.c:1071-1076` (two closure arms) | DELETED; the `N_CTX` arm (`:1083-1088`) reads three-valued sides (§4.2.3) |
| `src/facts/kset.c:139-140` (labels) | DELETED |
| `src/ir/dfa.c:156` (`CTXROW_NEWLINE` in the row enum), `:171-174` (`cr_nl_reads`/`cr_nl_set`), `:190-191` (`ctx_rows[CTXROW_NEWLINE]`) | DELETED: the newline set enters through the `ctx` row like every `A_CTX` set. `pcrec_cls_newline` stays the ONE newline bitmap, read by the parser's builder and MLINE `[r4 C7]` |
| `src/ir/dfa.c:262-263` (`PCREC_NO_MLINECTX`) | DELETED (its gate retires, §4.5.4) |
| **`src/ir/dfa.c:345`** (`CTXROW_NEWLINE` in `clsctx`'s mask) `[r4 C1]` | DELETED clause (the mask becomes `1u << CTXROW_CTX`) |
| `nl_bit`: `src/ir/dfa.c:769`, `:832`, `:1147`, `:1643`, `:1648` | DELETED |
| **`src/ir/dfa.c:236`, `:242`** (`cs->rows = 0;`, `rows \|= 1u << r`) and the `rows` reads in `ctx_entry_live`/`ctx_rows_knobbed` `[r4 B5]` | DELETED as dead logic. With the newline row gone, only `ctx` and `nostart` remain, and no byte-expressible `A_CTX` set equals utf8's non-start set. So no entry is ever shared by two rows, the `rows` mask carries one bit, and liveness reads one row id. Revision 1's census missed this deletion |
| `src/ir/nfa.c:1316` (`pcrec_nfa_has_bot`) | GENERIC: `N_CTX && ctxfn_reads_absent_prev` |
| `src/ir/dfa.c:1589-1590` (`has_end` hoist) | GENERIC: `N_CTX && ctxfn_reads_absent_next` |
| `src/ir/dfa.c:1086` (the `N_CTX` index) | GENERIC (table C): `3p + q` |

**C. Truth-function readers that EXTEND (become wider, not special).** Recipe:
`command grep -rnE 'CTXFN_|ctxfn|u\.ctx\.fn' src` (code lines, `ctx_span/readers.txt` §6):
- `src/core/internal.h:1157-1163`: the enum becomes `ctxfn.def`'s rows, with two added at P2b;
- `:1372` and `:2064`: the two fields widen;
- `src/parse/parse.c:70`: the builder's parameter widens;
- `src/ir/dfa.c:1086`: the index;
- `src/opt/possessify.c:235` and `:266`: the model and its caller, with the absent-reading
  decline;
- `src/gen/emit_vm.c:8347` and `:8355-8360`: the key and the rows, with two rows added;
- `:8400`/`:8404`: the lookup and its message, width only;
- `src/opt/dfamemo.c:67`, `src/ir/nfa.c:664` and `:1110`: copies, width only;
- `src/parse/ctxnode.c:109-110` and `src/parse/mod_assertions.c:134`: re-encoded constants,
  same names.

In tests, the raw literals are `tests/possessify/ctx_admits_check.c:169`/`:172` and its
16-function loop (`:155`) `[r4 A4]`.

**D. STILL SPECIAL, and why: 84 code lines naming `A_BOL`/`A_EOL`.** A comment-excluding
grep finds 87 code lines in `src/` that name `A_BOL` or `A_EOL`. Three of them change:
`parse.c:1681`/`:1696` become the node choice, and `mod_assertions.c:224` is deleted. The
other 84 STAY, because the kinds survive for `^`/`\A` and `$`/`\Z`. Where one of those arms
holds a table-A branch, only the branch goes. The survey's "38 `A_EOL` references under
`src/opt/`" (add. 1) are these labels, and they survive.

Also STILL SPECIAL:
- `N_BOT`, `N_EOL` and `N_END` (but see §4.6 for `N_BOT`/`N_END`);
- the DFA's eol/end views (`eol_ok`, `end_ok`, `DState.eolvar`/`endvar`,
  `emit_view_select`), which `(?m)$` keeps reading through its row;
- `CTXROW_NOSTART` (K50's gate, U-B1);
- the registry's `^`/`$` rows, whose `bol_def`/`eol_def` text stays as documentation and oracle
  (C2, CK-9). Their description strings ("D62's field+fold lowering") are rewritten (a
  `--list-syntax` text change, §4.5.2).

**E. Comments, by grep** `[r4 C1]` (`ctx_span/readers.txt` §3). 31 comment lines in `src/`
name the field, the kinds, `nl_bit`, the row or the knob, for example `internal.h:2004-2042`
(the kinds' own block), `dfa.c:58-61`, `:252-255`, `:273`, `:1091`, `:1470`, `:1580`,
`mod_modifiers.c:320`, `parse_mods.h:19-50`, `startanch.c:43`, `emit_dfa.c:4234` and `:8918`.
Each is reworded at P2c, so no comment names a deleted identifier. The build lane's
acceptance grep is the recipe above over comments, expecting zero hits after P2c.

**F. Readers outside `src/`** `[r4 C1]` (`ctx_span/readers.txt` §4-§5), by
`command grep -rnI 'NO_MLINECTX\|mlinectx\|run_mlinectx' tests scripts Makefile docs/testing.md`:
- `Makefile:1273` (the gate's line);
- `tests/codegen/run_mlinectx_identity.sh` (the gate);
- `tests/lib/san_scripts.txt:37`;
- `tests/mech/run_sabotage_matrix.sh` (`:169` and the `mlinectxidentity` arm, `:1927-1939`);
- the four comment mentions in `tests/codegen/run_gstart_identity.sh`;
- `tests/mech/sabotages/S76_*` (`SAB_SUITES`);
- the `CLAUDE.md` entries in `tests/codegen/`, `tests/lib/`, `tests/mech/`, `tests/assertions/`,
  `src/ir/` and `src/gen/`;
- `docs/testing.md`.

`tests/lib/mlscan.py` has three readers: `run_mlinectx_identity.sh` (retires),
`run_endvar_identity.sh` (kept; its population "`\z` or a multiline anchor" is unchanged,
because both `(?m)` rows still make `has_end` live, §4.2.5) and `run_mline_diff.sh` (kept). Its
comment naming `N_BOT_M`/`N_EOL_M` is reworded.

**What the deletion buys, stated as special cases removed.**
1. D62's accepted residual disappears. No analysis can match `case A_EOL:` and forget a
   field, because the field does not exist, and `(?m)` forms arrive at every exhaustive
   switch as `A_CTX`, which `-Wswitch` already forces each analysis to classify. D62
   control 3's 73-line obligation comment and its K63 census-in-a-comment go.
2. Four of the sabotage rows that exist only to keep a field reader or the newline row
   honest retire, with their witnesses kept as corpus cells (§4.5.4).
3. The DFA's class axis has ONE contributor for every assertion set (`ctx`), plus K50's gate
   (U-B1 folds that too, later), and the `rows` sharing logic deletes.
4. The VM has one context emitter (`vm_ctx`) over one table instead of one emitter for six
   functions plus two hand arms.
5. Part 1's producer needs no `(?m)` rows (§3.3).

### 4.5 Cost

#### 4.5.1 The abi event and its readers (D76/D94), found BY GREP `[r4 B2]`

Any moved byte makes it an abi event: 80 → 81. Revision 1 gave a six-reader table, and it
missed five readers. The list is now the output of one recipe
(`ctx_span/readers.sh` §1, the D94 rule: every reader of the NUMBER):

`command grep -rnIE '(abi|ABI_EXPECT|PCREC_ARTIFACT_ABI|PCREC_RX_ABI_H)[^0-9]{0,40}\b80\b|`80`|\b80\b[^0-9]{0,25}\babi\b' --exclude-dir={worktrees,build,.git} .`
excluding journal, lane and review history. The build lane runs it at the build commit and
classifies every hit as a READER (it moves with the number) or a RECORD (history, it does
not move). The hits at `3b0f87b55`:

| reader (moves at P2c) | site |
|---|---|
| the define | `src/gen/emit_dfa.c:54` `#define PCREC_ARTIFACT_ABI 80`, whose value the emitted `PCREC_RX_ABI_H` guard and `rx_info.abi` both carry |
| the codegen pin | `tests/codegen/run_codegen_tests.sh:3149` `ABI_EXPECT=80` |
| the identity gate's (B) pin | `tests/codegen/run_recursion_identity.sh:1262` `FILEPIN` (re-pinned to the landing commit; its comment cites 80) |
| the not-bumped plant | `tests/mech/sabotages/S693_abi_not_bumped.sh` (`SAB_BEFORE`/`SAB_AFTER`) |
| the spec's guard block | `docs/spec/match_api.md` §1¶7 (the `#error` text and `#define PCREC_RX_ABI_H 80`) |
| the spec's `rx_info` member table | `docs/spec/match_api.md` §6¶1, row 1 (`abi` … `80`) |
| the spec's number sentence | `docs/spec/match_api.md` §6¶17 ("It is `80` on every artifact") |
| the log | `docs/dev/history/abi_changelog.md`: the "is `80` on every artifact today" sentence and a new entry |
| a design reader | `docs/design/kit_proof.md` §6.1's B1 row ("pcrec abi 80 → +1"): it becomes "the abi at B1's parent, + 1" |
| the kit's wake | `memfn/docs/wake.md` ("pcrec abi is **80**"): the kit session's file, told at the build (a kit byte reader, D146), not edited by pcrec |

The RECORDS that do not move are `memfn/docs/journal.md`, `src/gen/CLAUDE.md`'s e1/e1fix
history, `docs/dev/plan.md`'s [ENTRY-TABLE] status, kit_proof's header and its `foobar`
paragraph, `docs/design/CLAUDE.md`'s entries, and this note.

Then come the readers that never cite the number. These are the byte-count class: the
identity gates' pins, re-pinned by recompiling their witnesses (coding_guide §3.1). After
them RUN THE SUITES THAT COUNT: registry, codegen and rxtsource (D94 addendum). `src/gen/
CLAUDE.md` cites the define by line `emit_dfa.c:51`, which is stale (F-4).

#### 4.5.2 Spec hunks (D80)

- `--emit-ir`'s VM `assert` rows keep today's role text, because the two forms rows carry it
  verbatim (§4.2.5). No `ir_listing.md` hunk is owed unless the build changes a string. That
  is checked at build by the listing's own pins.
- `--list-syntax`'s descriptions of `^`/`$` change (the `registry.c` strings), which needs a
  `registry.md` hunk if it quotes them.
- `--emit-facts`' `start_anchor`/`end_pin`/widths rows do not change (table A's "after" column
  is answer-identical by reading).
- `match_api.md` §1¶7, §6¶1 and §6¶17 take the new abi number (§4.5.1).
- If P1a lands, `facts_listing.md` gets the context records in the `span_facts` slice
  section (kit_proof §6.2, Z2).

#### 4.5.3 Is byte identity reachable?

- **VM: reachable by construction, ZERO movers predicted** `[r4 B3, A7]`. The two
  `vm_ctx_forms` rows emit today's expressions and role text character for character, and
  the class pool interns the same newline bitmap. Revision 1 saw one unexplained difference:
  `x(?m)$` and its `A_CTX` twin `x(?![^\n])` differ by an extra `goto rx_L3; rx_L3:` hop. That
  hop is the mid-pattern option item's `A_EMPTY`, not the assertion. `x(?m)$` carries an
  inline `(?m)` item that lowers to `A_EMPTY` and emits a label hop, and `x(?![^\n])` has
  none (A7). Today's `x(?m)$` and P2c's `x(?m)$` both carry it, so the comparison that
  matters is identical, and B3's "unexplained" closes. With arm A widening absent-reading
  rows (§4.2.5), possessify moves nothing, so no VM program moves.
- **Routes: zero flips** `[r4 C6]`. `has_bot`/`has_end` are preserved by §4.2.5's predicates,
  and possessify, which can flip a route through atomic discharge, moves nothing at P2c.
- **DFA: reachable except where the context-set list's ORDER changes.** The closure is the
  same predicate over the same bits (§4.2.3), and the alphabet is unchanged, because class
  numbering is by lowest member byte whatever the refinement order (`eqclasses`'s comment).
  What can move is the list order. Today the newline set is listed AFTER every `A_CTX` set
  (`ctx_collect` walks the rows in order). After the change it is listed in NFA order with
  them. Some machines keep their order and their bytes: a machine with ONE context set, one
  whose `(?m)` nodes come after every other `A_CTX` set in NFA order, or one whose newline
  set is shared with a `(?=\n)`/`(?<=\n)` already in the list. A machine with a `(?m)` node
  BEFORE a different `A_CTX` set (`(?m)^\bfoo`) gets its atom vectors' bits in another order.
  Its atoms renumber and every per-atom table permutes. Those artifacts are
  ANSWER-IDENTICAL MOVERS, and their diff is confined to per-atom table initializers
  (CK-4). Preserving their bytes would need a contributor rule that sorts "absent-aware sets
  last", a rule invented to keep bytes. Leaning: accept and count them (Q3).
- **Listing and stamps:** no stamp names a multiline kind. `RX_*` stamps read engine and
  route facts, which do not change. `<prefix>_VALID_LB` does not move (§4.2.5, A8).

So the event is "abi bump, measured DFA movers": the identity gate pins (B) at the landing
commit, and the mover population is a measured, answer-identical, table-confined set.

#### 4.5.4 Checks that move: DERIVED `[r4 B5, B6, C1, A2, B4]`

**The method** is the start_table / dec_fallback / locate_finish precedent:
- the text P2a-P2d change is written once as data (`ctx_span/edit_set.tsv`: `def` / `token` /
  `line` per commit);
- `docs/design/start_table/sabotage_anchors.py` maps every sabotage anchor to its owner
  definition and classes it RE-AIM where its anchor text is in the edit set
  (`ctx_span/sabotage_anchors.tsv`);
- `ctx_span/derive_rows.py` adds two facts. One is an OWNER fact: the anchor's definition
  holds a CODE-line edit occurrence, so the row RE-RUNs in that commit. The other is a WITNESS
  fact: the row's `SAB_*` assignments name `(?m)`, the kinds, the knob or the newline row,
  so its witness or detector sits in the population P2c moves, and it RE-RUNs at P2c with its
  reach re-verified.

The dispositions below (retire / re-aim / re-run) come from reading each selected row's
intent. The script derives the population and nothing else. The build lane re-runs all three
scripts on its own base before the first edit.

**The derived list for P2c at `3b0f87b55`** (`ctx_span/derived_rows.tsv`; P2d's rows are in
§4.6):

| row | derived by | disposition |
|---|---|---|
| S76 (mlinectx alphabet unconditional) | owner `ctx_collect` + witness | **RETIRES** with its gate. Its re-aimed plant ("the `ctx` row adds a set no `N_CTX` reads") IS S71's on the one remaining row `[r4 A2]` |
| S77 (possessify ignores multiline) | anchor `first_of` (`anch.multiline`) | **RETIRES** `[r4 B6]`: a re-aim would plant on the generic `A_CTX` arm, which every `\b`/lookaround suite catches already. Its witness stays as a corpus cell (`tests/possessify/`) |
| S762 (end pin reads `(?m)$`) | anchor `ew_walk_marked` | **RETIRES** `[r4 B6]`, witness kept as a corpus cell (`tests/endwin/` or the rev-end corpus) |
| S900 (derive kills a multiline `^`) | anchor `q_rewrite` | **RETIRES** `[r4 B6]`, witness kept as a corpus cell (`tests/compound/`) |
| S343 (a shared set records only the first row) | anchor `ctx_collect` (`rows \|=`) | **RETIRES** `[r4 B5]`: the sharing logic it guards is deleted (table B), because no byte-expressible set equals utf8's non-start set |
| S341 (absent reads in the set) | owner `pcrec_build_dfa` | **RE-AIMS** `[r4 B5]` to the absent read: the plant is A1's bug, `sides_of` setting `left_abs` from `bot_ok` in BOTH directions. Witness: `[a-z]+\b` on `"ab"` at the reverse `s0` (`reverse-pass`; the plant loses the start). Its old forward witness `(?<![a-c])\d` stays as a corpus cell. It replaces revision 1's SP-5 |
| S71 (wordctx alphabet unconditional) | owner `ctx_collect` | RE-RUN at P2c. Its gate's population changes (A2, below) |
| S1100, S14, S746 | owner `compile_ast` (the NFA lowering) | RE-RUN at P2c |
| S157, S49, S84 | owner `first_of` | RE-RUN at P2c |
| S365, S86 | owner `vm_emit_node` | RE-RUN at P2c |
| S613 | owner `em_set` (widths) | RE-RUN at P2c |
| S761 | owner `ew_walk_marked` | RE-RUN at P2c |
| S893, S904 | owner `q_rewrite` | RE-RUN at P2c |
| S218, S222, S235, S463, S470, S490, S608, S617, S78, S81, S82 | witness (`(?m)` in `SAB_REACH`/`SAB_DESC`) | RE-RUN at P2c with reach re-verified. Their reach greps read stamps and structure (`RX_DFA_SCAN`, `rx_seed_state[`, `start_max`, the handoff text), which do not move. Two witnesses are list-order movers, S490's `(?m)^(?:ab\|\bcd)` and S235's `(?m)^a\|\B`, and their reach greps are unaffected |

Thirteen rows name `(?m)` or the kinds only in comments (S1083, S124, S125, S129, S130, S219,
S220, S480, S513, S618, S69, S70, S83) and carry no obligation. **P2a and P2b select no row**:
no anchor and no owner is touched in `pcrec_poss_ctx_admits`, `sides_of`, `Sides`, or the
closure's `N_CTX` index line. Their gate is CK-4's zero movers plus CK-5.

**Against the panel's hand list.** The derivation reproduces every row the panel named:
- S341's re-aim and S343's retirement (B5);
- the eight witness rows B5 names: S490, S218, S222, S235, S463, S470, S608 and S617;
- S77, S762 and S900 (B6), and S76 (A2).

It adds 16 that no list named outright: S78, S81 and S82 (witness), and the 13 owner rows (S71 among them, which A2 names only as S76's re-aim target).

**Gates and other checks** (from `readers.txt` §4-§7):

| check | effect |
|---|---|
| `tests/codegen/run_mlinectx_identity.sh` and its knob | RETIRES, with every reader in §4.4 F (the `Makefile` line, `san_scripts.txt`, the mech arm `mlinectxidentity`, the CLAUDE.md entries, `docs/testing.md`) |
| `tests/codegen/run_wordctx_identity.sh` `[r4 A2, B4]` | its population split was `\b`/`\B` TEXT, and its knob (`-DPCREC_NO_WORDCTX`) cuts every `CTXROW_CTX` set, `(?m)`'s included after P2c, so a `(?m)`-only pattern in its "`\b`-free" population would DIFFER and go red. The population becomes "no `A_CTX` SOURCE spelling at an atom position": `\b`, `\B`, `(?m)^`, `(?m)$` (the `(?m)` half read by `tests/lib/mlscan.py`'s `multiline_anchor`, the one implementation). The `(?m)` patterns join the MUST-DIFFER control |
| `tests/codegen/run_endvar_identity.sh` | KEPT, population unchanged (§4.4 F) |
| `tests/lib/mlscan.py` | KEPT (it classifies TEXT); its comment is reworded |
| `tests/possessify/ctx_admits_check.c` | EXTENDS to the 9-cell universe (§4.2.5) |
| `tests/possessify/` possdiff | gains A4's three cells |
| emit_sweep, startset manifests, `run_form_census.sh` floors | re-pinned for the measured DFA movers (CK-4) |

#### 4.5.5 What it costs in code, roughly

The deletions come to about 175 lines: the field and its comment (about 75), the two VM arms
(about 40), and the closure arms, contributor row, `nl_bit`, knob, labels and the dead `rows`
logic (about 60). The additions come to about 55 lines: `ctxfn.def` (ten rows), the three
derived predicates, the three-valued `Sides` and index, two VM form rows, and the possessify
decline. The net is small in lines. The gain is in the kinds of thing a reader must know.

### 4.6 The second census: `\A` and `\z` as rows (Q-r4-1's extension) `[r4 Q-r4-1]`

**The question.** `\A` is "prev absent" (`SUBJECT_START`, 0x1C0) and `\z` is "next absent"
(`SUBJECT_END`, 0x124), both rows of §4.2's table that read no membership. Folding them
would delete `A_BOL`/`A_END` (and `N_BOT`/`N_END`) as kinds. The ruling decides by deletion
count, with simplification qualifying.

**The method.** A grep with the arm beside it (`ctx_span/arm_pairs.py`) collects every code
line in `src/` naming `A_BOL`, `A_END`, `N_BOT` or `N_END` (100 sites at `3b0f87b55`). It
prints each beside the `A_CTX`/`N_CTX` label of the same switch. Each site is then
classified by hand, by comparing the two arms:

- **DELETED**: the line goes, and the `N_CTX`/`A_CTX` arm answers the same through the row;
- **LABEL**: the kind's label token leaves a shared label list whose arm already serves
  `A_CTX` identically, and the line stays for its other labels;
- **GENERIC**: the site becomes a node choice or a fn-derived predicate;
- **STILL SPECIAL**: the kind's arm answers DIFFERENTLY from `A_CTX`'s, so after a fold it
  would become a recognizer of "the `A_CTX` whose row is `SUBJECT_START`/`SUBJECT_END`".
  That is a special case read off data, invisible to `-Wswitch`: D62 control 3's hazard
  class again.

| | `\A` (`A_BOL` after P2c, `N_BOT`) | `\z` (`A_END`, `N_END`) |
|---|---|---|
| DELETED | `internal.h:739` (`A_BOL`), `:1993` (`N_BOT`); `nfa.c:620` (the lowering arm); `dfa.c:693` (eps label), `:1019-1021` (closure arm); `kset.c:136`; `emit_vm.c:8892` (the `^`/`\A` arm, its position half after P2c); `possessify.c:621-629` (widen-and-decline = the `A_CTX` arm's non-arm-A answer) | `internal.h:752`, `:1995`; `nfa.c:642`; `dfa.c:695`, `:1027-1029`; `kset.c:138`; `emit_vm.c:8952` (the `\z` arm) |
| LABEL | 54 label tokens: `atomic.c` ×10, `revdet.c` ×5, `emit_vm.c` ×9, `possessify.c` (`:317`, `:386`, `:975`, `:1342`, `:1519`, `:1760`), `lower_enc.c` ×3, `mrl.c` (`:158`, `:327`, `:541`, `:682`), `derive.c:65`, `altcls.c:402`, `select_engine.c:254`, `req.c:608`, `startset.c:123`, `endwin.c:149`, `:302`, `parse.c:141`, `definitions.c:218`, `:431`, `ctxnode.c:92`, `mod_backrefs.c:611`, `mod_lookaround.c:192`, `mod_vars.c:226`, `rxt_compose.c` ×2, `internal.h:5108` | 55 label tokens: the same lists' `A_END` tokens, with `altcls.c:404`, `mrl.c:160`/`:543`/`:684`, `possessify.c:318`/`:977`/`:1343`/`:1520`, `derive.c:231`, `:292`, `startanch.c:129`, `endwin.c:299`, `req.c:610`, `startset.c:125`, `definitions.c:220` in place of the `A_BOL` positions |
| GENERIC | `mod_assertions.c:86` (`\A` builds the row and keeps its `pcrec_lb_raise(cx, 1)`); `parse.c:1681` (`^` outside `(?m)` builds the same row); `nfa.c:1316` (`has_bot`: the `N_BOT` clause folds into P2c's predicate); `cr_ctx_reads` gains `ctxfn_reads_membership` (NEW, shared): an absent-only row contributes no set to the class axis, or every artifact gains an atom | `mod_assertions.c:88` (node choice); `dfa.c:1591` (`has_end`: `case N_END` folds into P2c's predicate); the shared `cr_ctx_reads` predicate |
| STILL SPECIAL | `startanch.c:114-117` (`SA_BOT`, which every anchoring reader keys on); `derive.c:225-227` (the killed-`^` route optimization); `derive.c:291` (`bol_out`); `widths.c:128-129` (`EM_S`) | `endwin.c:134` (`EW_Z`, the end pin `rev-end` and `end_window` read); `possessify.c:657` (`\z`'s UNCONDITIONAL upward-closure transparency, where `A_CTX`'s arm widens); `widths.c:132` (`EM_E`); `definitions.c:429` (`eol_tail_plain` admits `\z` inside `\Z`'s row `(?=\n?\z)` for D164's `tagged` form, and answers false for `A_CTX`) |

**The headline.** 15 sites DELETE. 12 of them are in the ENGINE layer: the two NFA kinds,
the two lowering arms, two eps labels, two closure arms, two kset labels and the two VM arms.
They need one new generic predicate (`ctxfn_reads_membership`), plus the `has_bot`/`has_end`
clauses that fold into P2c's predicates. 3 are in the AST: the two enum members and
possessify's `^` arm. The ANALYSIS layer does not delete: 8 sites read `\A`/`\z` as
STRUCTURE (anchoring, the end pin, possessify's exemption, the widths marks, D164's tail).
Each would become a recognizer of a row on data. The 109 label tokens (54 + 55) are tokens,
not lines.

A recognizer that a future analysis forgets errs in a known direction:
- for `startanch`, `derive`, `endwin` and possessify it is a lost optimization (sound): no
  anchor, no kill, no end pin, a widen where a transparency was;
- for `widths.c`'s marks and `eol_tail_plain` the direction is NOT shown here. The build
  must show it before claiming soundness. At best they are the D164 `tagged`-form movers.

**Leaning: fold `\A`/`\z` at the NFA LAYER ONLY, as step P2d after P2c.** This is the
general form the census suggests: AST kinds are structure for analyses, and the NFA has one
context state over one table.
- `A_BOL`/`A_END` stay AST kinds, and every analysis reads them as today: 0 recognizers.
- The lowering maps `A_BOL` → `N_CTX(SUBJECT_START)` and `A_END` → `N_CTX(SUBJECT_END)` by a
  table lookup.
- The VM emits both from the same rows.
- The NFA kinds `N_BOT`/`N_END` and every engine arm above delete.

The NFA-level fold deletes the 12 engine sites (the two lowering arms become one row
lookup, and the two VM arms become rows) at the cost of one generic predicate, with zero new
special cases. A full AST fold would also delete the 3 AST sites and the 109 label tokens,
add 8 recognizers, and re-open D62's hazard. That trade fails the ruling's own test, because
simplification is counted in kinds a reader must know, and 8 data recognizers are more than
2 kinds.

P2d's movers are predicted as ZERO. The absent-only rows read no membership (no atom), and
`has_bot`/`has_end` are preserved. It lands as its own step after P2c with its own CK-4 run.
If that run finds a moved byte (an emitted legend or listing that names an NFA kind), it is
an abi event like P2c, with §4.5.1's recipe. Its derived sabotage rows (`ctx_span/derived_rows.tsv`,
`owner:P2d`) number 31: the NFA lowering (`compile_ast`), `first_of`, `vm_emit_node`, the
kset and req walks (`rb_walk`, `ss_walk`), `pcrec_minw`, `pcrec_nullable`, `rd_shape`,
`dis_walk`, `pcrec_bref_mark` and others. Under the NFA-only form most of them do not move,
because their owners are AST analyses. The build lane re-derives the population with the
narrower P2d edit set (NFA and VM only) before claiming it. If Frank prefers the full fold
or no fold, the census above is the evidence either way (Q7).

### 4.7 Side simplification, filed as an idea, not designed `[r4 Q-r4-1]`

**The idea.** `pcrec_enc_set_bytes` admits only sets whose every member is one byte. Under
utf8 it could also admit CO-FINITE sets of the form "some ASCII plus EVERY non-ASCII
character". At a character boundary such a set is byte-testable on each side:
- the NEXT character is in it iff the next byte is in the ASCII part or is a lead byte
  (`0xC2..0xF4`);
- the PREVIOUS character is in it iff the previous byte is in the ASCII part or is a
  continuation byte (`0x80..0xBF`), because a multi-byte character ends in one.

That would un-force the VM for `(?![^\n])` and `(?<![a-z])` under utf8 (A5's population),
and their records would become exact.

**The question that blocks it is ill-formed utf8.** The equivalence holds for well-formed
text, but pcrec's subject contract is invalid-tolerant (`utf_valid_design.md`; PCRE2's
`MATCH_INVALID_UTF` semantics, where an ill-formed sequence matches no class, negated ones
included). A truncated lead byte (`0xC3` then `a`, or at the end) reads as "next ∈ set",
while PCRE2 says `[^\n]` matches nothing there. A stray continuation byte after ASCII reads
as "prev ∈ set", while PCRE2 says it is no character. So the byte test is unsound on
ill-formed input unless one of three things holds:
- the artifact validates (`-futf-check`);
- the set excludes the invalid bytes on the correct side (`0xC0`, `0xC1`, `0xF5..0xFF` as
  leads, and continuation bytes not preceded by a lead), which is not a per-byte test;
- the context is decided by the ⊥ pseudo-character rule (`ucp_design.md`).

Filed with that question stated (§10, UL-i). Not designed, and nothing here depends on it.

---

## 5. Open questions (discussion, each with a leaning)

**Q1. Does part 1's context half land at Z2 with UL-0?** Settled in part by B9: the IN-SPAN
half is UL-0's own at Z2, because without it the slice overstates `exact_len` on the wire
(§3.8). The out-of-span records are the same walk at offsets outside the span, listed and
sent nowhere. *Leaning:* the whole producer lands at Z2, used only as the C8-ctx control. The
SOURCE switch waits for UL-8's trigger.

**Q2. Order of parts 1 and 2: RULED (Q-r4-2): free.** Part 2 lands at its build go. If that
falls between the kit's Z1 and B1, §7's re-run list applies. If part 1 lands first it carries
the two `(?m)` rows of §3.3, and P2c deletes them.

**Q3. Accept the DFA list-order movers, or keep bytes?** §4.5.3. Ordering by NFA position is
today's rule for `A_CTX` sets and is the rule a reader would guess. *Leaning:* accept the
movers, confine each diff to tables (CK-4), and state the population in the abi log. A count
above the text-side prediction is a finding about the list, not a reason for a sort rule.

**Q4. D62's addendum.** D62's principle survives, and its specific ruling (the flag) is
superseded. The addendum would say: the modifier is resolved into the CHOICE OF NODE at parse
time, a kind is still never doubled per modifier, and `$`/`\Z`/`^`/`\A` keep their AST kinds
as structure (and, if P2d is taken, `\A`/`\z` lower to table rows at the NFA). *Leaning:*
Frank rules it with P2c's build go.

**Q5. A multi-offset `A_CTX` for `$`/`\Z`: RULED (Q-r4-1): no; `$`/`\Z` stay kinds** (UL-e).

**Q6. Should the producer state `pos-start`/`pos-end` records with no consumer?** *Leaning:*
keep the rows, which makes no exception for two kinds, and SEND them nowhere until U-z or a
T-CUT change asks. If P2d is taken they become `ctx-onesided`.

**Q7. P2d (§4.6): the NFA-level fold, the full fold, or none?** The forces:
- the NFA-level fold deletes the 12 engine sites with zero new special cases;
- the full fold also deletes 3 AST sites and 109 label tokens, and adds 8 recognizers that
  `-Wswitch` cannot see;
- no fold keeps two NFA kinds and their arms beside a table that already expresses them.

*Leaning:* the NFA-level fold, landed after P2c as its own step, with its re-derived
population. This is the one item in the revision that is a real choice for Frank. The census
supports the leaning and does not force it.

---

## 6. Checks (each against a source the subject does not share; sabotage ids PROPOSED, not allocated) `[r4 B7]`

Ids `SP-1`.. are this note's placeholders. The manager allocates real S-ids from
`worktrees/.mgr/sabotage_ids.txt`, outside the kit's reserved ranges. kit_proof's S1149
(F-1's plant) is PROPOSED in kit_proof §6.3.

| id | check | expectation from | sabotage (PROPOSED) |
|---|---|---|---|
| CK-1 | C8-ctx: on every DFA artifact where `MkEnd` states a context set, the producer's EXACT item equals it, or the producer is silent. A producer-EXACT item the machine contradicts fails. **Non-silence floor**: the producer must state an EXACT item on at least N artifacts where the machine states one, with N measured at P1a and written as a literal (K35), so an everywhere-silent producer FAILS. **Per input-table row**, a floor of artifacts where that row fired (U-B2) | the anchored machine's seed table. Revision 1 said the two "share no code", which overstated it: both read the same lowered node (input), and neither shares the other's WALK. The node itself is controlled by CK-2 (libpcre2) | SP-1: the fold uses `S_0`'s complement; must fail CK-1 and CK-2. SP-1b: the producer returns `nctx` 0 everywhere; must fail CK-1's floor |
| CK-2 | soundness and exactness against libpcre2 10.46. For every corpus `m` cell, every match's context bytes lie in each item (absent per its bit). For EXACT items, a full-alphabet subject family at the context offsets finds no subject that satisfies the items and the body and that libpcre2 rejects. **The family GENERATES absent-edge subjects**: `c = 0`; `c + k = n`; a match after a final newline; the empty subject; and each item's offset at the subject edge. A random draw does not reach them (kit_proof §6.4's K1 lesson) | libpcre2 | SP-2: `look-fixed` marks an alternation EXACT (`(?<=ab\|cd)`); must fail CK-2's exactness half |
| CK-3 | the listing invariant: each item carries one `form`; `nctx` is 0 when no item contributed; no UNSTATED enum appears in a listed record; no SUPERSET item appears on a site's sent list | the listing, read by a python reader that shares no code with `kset.c` | SP-3: a record with `absent` left UNSTATED; refused at the reader |
| CK-4 | part 2's movers, over emit_sweep's every arm, answer-identical by the three-way self-oracle. (a) The byte movers are EXACTLY the DFA artifacts with a `(?m)` node before another `A_CTX` set in NFA order. That set is predicted from pattern text by `mlscan.py` plus a python NFA-order read. (b) **Each mover's diff is CONFINED** to the per-atom table initializers and the atom vectors: any other differing line (a stamp, `VALID_LB`, a program line) fails. (c) VM movers, route movers and possessify movers are each ZERO, asserted rather than "zero or explained" `[r4 B3]` | libpcre2 (answers), the text-side prediction (population), and the diff's line classes (confinement) | SP-4: the parser builds `A_BOL` for `(?m)^` (the D62 failure in its new form). Witness `(?m)^b` on `"a\nb"`: PCRE2 (2,3), the plant nomatch `[r4 B6]`. Revision 1's `(?m)^$` on `"a\n"` does not reach (nomatch both ways). SP-4b: `MLINE_BOL`'s `in`/`absent` cell copied from `out` (the 4-cell habit); witness `(?m)^` on `"a\n"` from 2, PCRE2 nomatch, the plant (2,2). SP-4c, the `$` twin: the parser builds `A_EOL` for `(?m)$`; witness `a(?m)$` on `"a\nb"`, PCRE2 (0,1), the plant nomatch. SP-4d: the `(?m)` builder copies `\b`'s lookbehind raise (A8); caught by CK-4(b) |
| CK-5 | reverse-machine identity for every `(?m)$` artifact on `ENG_UNANCH` and every `\b`-ending `reverse-pass` artifact (`[a-z]+\b` at `n`) `[r4 A1]`. A predicted list-order mover is compared under the predicted atom PERMUTATION (tables equal after renumbering), since byte identity fails for it by construction `[r4 B7]` | the pre-change build's reverse tables | S341 RE-AIMED (§4.5.4): `sides_of` sets `left_abs` from `bot_ok` in both directions; must break CK-5 and the `[a-z]+\b` corpus cell at `n` |
| CK-6 | F-1's in-span rule: `exact_len` stops at a straddling two-sided item AT its offset and narrows `S_d` at a one-sided one, on `a(?=b)[a-z]`, `[a-z0-9_ ]\b[a-z ]`, `\w(?=\d)\w` and on every site stating `exact_len > 0` | libpcre2 prefix languages (X0's set equality, kit_proof §6.4) | kit_proof S1149: the walk passes every zero-width node; must fail CK-6 |
| CK-7 | K35: the population of artifacts with ≥ 1 context item, PER INPUT-TABLE ROW, counted by a stamp-free text census (kvctx.py's shape), with floors as measured literals | python over pattern text | — (a count, not a plant) |
| CK-8 | the truth table against libpcre2: each `ctxfn.def` row's canonical lookaround spelling, compiled through libpcre2 over the 547-cell family plus the absent-edge cells, must reproduce the row's nine cells | libpcre2 | SP-8: one cell of one row flipped (`MLINE_EOL`'s `out`/`absent` cell); must fail CK-8 and a corpus cell |
| CK-9 | the C2 tie: `bol_def`/`eol_def`'s `DEF_MULTILINE` text, parsed by the ordinary parser, is answer-identical to the parser's `(?m)^`/`(?m)$` nodes over CK-8's family | libpcre2 plus the registry text (not the parser's node) | SP-9: the registry row edited (`(?!\z)` dropped); must fail CK-9 |
| CK-10 | A6's free check: the producer's records are identical with and without `-fno-ctx-node` on every artifact whose lookarounds are all one character | the producer against itself, through two different rows (`ctx-*` vs `look-*`) | SP-10: `look-neg-1` reads absent FAILS; must fail CK-10 |

Each plant needs a REACH witness ([MECH-REACH]), named per row above. SP-4's revision-1
witness is replaced because it did not reach `[r4 B6]`.

## 7. Staging `[r4 Q-r4-2, B8]`

**Ordering is free** (Q-r4-2, the manager's). Part 2 lands whenever its build go comes, and
before the kit's Z1 is preferred when convenient. Revision 1's B8 finding stands as a COST,
not a constraint. P2a-P2c fit nowhere in kit_proof §7's sequence. If P2c lands between the
kit's Z1 and B1, the affected kit evidence is RE-RUN, and the kit is told at that build:

1. Z1's zero-mover baseline (emit_sweep on every arm), because P2c's DFA movers are
   `(?m)`-plus-`A_CTX` artifacts, some of them with kit sites;
2. X0 and `conj.py`'s census and witnesses, because the machine reading's `C_{−1}` for a
   `(?m)^` body is read through the new row;
3. B4's floors (`row_floors.tsv`, the routed census), if B4 has landed;
4. B1's abi number, which becomes P2c's + 1.

**The independent control at P2c** (U-B3): `conj.py` re-run on P2c's tree must give an
IDENTICAL cover census and an identical `why` for every pattern (`conj.txt` A/B/D unchanged).
Part 2 claims no answer move. `conj.py` reads the EMITTED anchored machine through kvdfa,
which shares nothing with P2c's code, so a moved verdict is a finding about P2c.

| step | what | movers |
|---|---|---|
| P2a | `ctxfn.def` with the six rows re-encoded (absent copied from out); widen `fn`/`ctxfn`; the closure indexes `3p + q` | 0 (CK-4 asserts zero; CK-5 on `[a-z]+\b`) |
| P2b | the two new rows and their `vm_ctx_forms` rows; three-valued `Sides` with A1's per-direction absent read; the three derived predicates; possessify's absent-reading decline. Nothing builds the new rows yet | 0 |
| P2c | the parser builds `A_CTX` for `(?m)^`/`(?m)$`; tables A-B delete (with the dead `rows` logic); retire `run_mlinectx_identity.sh`; re-define `run_wordctx_identity.sh`'s population; the derived sabotage list (§4.5.4); the D62 addendum; abi 81 with §4.5.1's readers | the measured DFA list-order movers (CK-4), answer-identical, table-confined; `conj.py` identical (U-B3) |
| P2d (if Q7 takes it) | `A_BOL`/`A_END` lower to `N_CTX` rows; `N_BOT`/`N_END` and their engine arms delete; `cr_ctx_reads` reads `ctxfn_reads_membership` | 0 predicted (CK-4); its own derived rows |
| P1a (= kit_proof Z2) | the extended k-set walk with §3.3's table (in-span and out-of-span), listed in `--emit-facts` (`facts_listing.md` hunk), CK-1..CK-3, CK-6, CK-7, CK-10 | 0 bytes; listing only |
| P1b (= UL-8's trigger) | the producer's EXACT items become the context source for the first VM-side consumer; the machine reading becomes the control; `MF_MAX_CTX` rises (kit_proof §4.1) | per that consumer's own event |

P2a-P2b touch the closure and move nothing, so they can land early. If part 1 lands first
(Q2), P1a carries the two `(?m)` rows and P2c deletes them.

## 8. The three standing questions (`docs/design/CLAUDE.md`)

1. **The measurement regime: NOT RELEVANT to a decision here.** No timing is read or
   produced. The measurements are compile-only probes, libpcre2 equivalence runs (547 cells
   per pair), and two greps-with-classification (§4.4, §4.6). Part 2's mover count is a
   compile-only census at build. Any speed effect (UL-c's arm A valuation, P2d) is a mover
   for the bench to read later, not a premise.
2. **The independent control: RELEVANT.** §6.
   - CK-1 compares two producers that share an input node but not a walk. Its non-silence
     floor is a literal, and the node itself is CK-2's (libpcre2).
   - CK-2, CK-6 and CK-8 read libpcre2, with generated absent-edge subjects.
   - CK-3's reader is python. CK-4's population is predicted from pattern text, its
     confinement from line classes.
   - CK-7 is K35's text census per row. CK-9 reads the registry text, not the parser's node.
     CK-10 is two rows against each other.
   - `conj.py`'s re-run at P2c is the control on the kit side (§7).
   - Each plant names its reach witness, and the derived sabotage population (§4.5.4) is
     produced by a script, not by a hand.
3. **What moves when data is regenerated: RELEVANT, narrowly.**
   - The producer reads no table, prior or measurement set, so regenerating any of them moves
     none of its records.
   - `ctxfn.def` is not regenerated. It is hand-declared rows checked by CK-8 against
     libpcre2.
   - Part 2 is an abi event once, at P2c, with §4.5.1's readers. It re-pins emit_sweep, the
     startset manifests and the form-census floors for its measured movers.
   - The `bol_def`/`eol_def` definitions stay oracle input (CK-9). Regenerating the oracle
     store moves nothing here.

## 9. SIBLING-OF-A-FAMILY

- **The per-offset walk family** `[r4 C4, Q-r4-3]`. The family is `pcrec_kset_walk` (offsets
  from the match start, NFA frontier), `req.c`'s run walk and `widths.c`'s width walk. The
  slice is NOT a fourth member: it is `kset_walk` extended (an exactness bit per offset, the
  context rows of §3.3, offsets outside the span). With three members, the unified per-offset
  table is due (memory `pcrec-forest-for-trees`, the ~3 rule). It is ONE walk producing one
  per-offset record, with each fact (the k-set, the run pin, the widths, the slice, the
  context items) a projection. *Filed* as a unification candidate with its trigger: the next
  per-offset fact asked of any of the three (§10, UL-j).
- **The position-pin family** (window_contract §5.6: `start_set`, the k-set, `run_pin`,
  `end_pin`/`end_window`, compound's split facts, landmark K, `span_facts`). The context
  producer is a projection of the k-set walk, so the family's count does not grow.
- **The context family** (kit_proof §8.2): MLINE's `{\n}` predicate, the 23 shifted origins,
  the seed table, the VM's `A_CTX`, the `-bounded` view family, D164's end set and kvctx.py's
  reading. This note gives the family its ONE producer and its ONE truth table. The members
  are one producer, one machine reading (the control), and consumers.
- **The absent rule** (kit_proof §8.2): `\A`/`^`, `\z`, MLINE's edge, `\G`'s `search_from`.
  Part 2 adds the engine side of the rule: the absent row and column of the truth table. One
  meaning of "absent" runs from the table through the producer (`MkAbsent`) to the carrier
  (`mf_pred.absent`). That is a layering, not a dispersal.
- **The assertion family** (`A_BOL`, `A_EOL`, `A_END`, `A_CTX`, `A_GSTART`, `A_KRESET`). Part
  2 consolidates it. Assertions that read a CHARACTER become rows of one table. Assertions that
  test a POSITION stay AST kinds for the analyses, and with P2d they too lower to table rows at
  the NFA. Two-position (`$`/`\Z`) and runtime (`\G`) facts stay kinds everywhere.
- **The `\b` rewrite family** (kit_proof UL-6, the definitions table's `\b` row, possessify's
  arm A valuation, kvctx's positional rewrite). The fold of §3.4 is the one READING, arm A is
  the one OPTIMIZER use, and UL-6 is the BOONIES lowering. Arm A's `pcrec_poss_ctx_admits` and
  the fold both compute "which bytes does this row admit on one side given the other".
  *Leaning:* the fold calls the extended `pcrec_poss_ctx_admits` (9-cell, P2a) rather than a
  second fold.

## 10. UNLOCKS, each with its trigger (filed, not designed beyond it)

| id | unlock | trigger (D77) |
|---|---|---|
| UL-a | the facts-layer context source for VM-only patterns (kit_proof UL-8) | U1b / [CAPS-KNOWN]'s first VM-side consumer |
| UL-b | wider lookbehind context (`(?<=ab)z`) sent as a FILTER on seeded DFA sites (kit_proof §3.3's "NO" row); R-26.7's first customer | kit_proof U4's trigger: a measured seeded `\b…` or lookbehind cell |
| UL-c | possessify arm A VALUES absent-reading rows (`First` gains "admits absent"; each `nullable` reader re-proved; its own mover prediction and route census) `[r4 B3]` | its own: a measured `(?m)` quantifier cell, measurable on existing corpus cells (C6) |
| UL-d | MLINE's `absent` SATISFIES and pcrec's edge attempt retires (kit_proof U-mline), read off the producer's `ctx-fold` record | U-mline's own: a `(?m)^` cell whose edge attempt is measured |
| UL-e | `$`/`\Z` and multi-byte newline conventions (A3) as instances of [ENG-LOOK]'s bounded lookahead (a multi-offset context) | [ENG-LOOK]'s design gate, or the first non-LF convention row |
| UL-f | the 23 shifted-origin sites restated from the producer's records (kit_proof U-ctxorigin) | its own: one such site in a losing bench cell |
| UL-g | the producer as the prefilter's context oracle: a SUPERSET item is a necessary condition any search filter may test; R-26.7's second customer | a filter consumer asking for it (none today) |
| UL-h | `-fno-ctx-node` producer-record identity as a standing check (CK-10) `[r4 A6]` | lands with P1a; no separate trigger |
| UL-i | co-finite sets in `pcrec_enc_set_bytes` under utf8 (§4.7), un-forcing the VM for `(?![^\n])`, `(?<![a-z])` | the ill-formed-utf8 soundness question answered (a design note), and a VM-forced utf8 cell in a losing bench row |
| UL-j | the unified per-offset walk (k-set, run pin, widths, the slice) (§9) | the next per-offset fact asked of any of the three walks |
| U-B1 | K50 joins the ctx row: `N_CSTART` is the `NOT_NEXT` row over `¬start_cls` with absent copied from `out` (today's semantics); `CTXROW_NOSTART` joins `ctx`, "one contributor for every assertion set" with no exception. Cost: utf8 list-order movers, an abi event | the next [K50] change or the next contributor row; eligible as a simplification alone (Frank 2026-10-18) |
| U-B2 | the input table as a listable first-match table with per-row floors (K35 per row) | P1a (lands with it: CK-1, CK-7) |
| U-B3 | `conj.py` re-run as P2c's independent control | P2c (§7, lands with it) |
| U-B4 | per-item `ctx[]` predicates retire the stacking rules | R-26 drafting: APPLIED now (§3.2, §3.6, kit_proof §4.1) |
| R-26.7 | the per-item exactness fact (kit_proof §4.3, FILED) | UL-b or UL-g |

## 11. Findings filed (doc findings, not fixed here)

- **F-1 (kit_proof §5.2): CONFIRMED and wider** (B9, §3.8). It is FIXED in kit_proof as text
  by this revision (`[r4 B9]` there).
- **F-2 (stale path):** `src/opt/ctxnode.c` is named in `src/core/internal.h:759`,
  `src/ir/nfa.c:654` and revision 1's brief. The file is `src/parse/ctxnode.c`.
- **F-3 (stale name):** `pcrec_ctx_set_bytes` is named in `src/core/internal.h:774`, `:2017`
  and `src/enc/enc.h:505`. The function is `pcrec_enc_set_bytes`.
- **F-4 (stale line cite):** `src/gen/CLAUDE.md` cites `emit_dfa.c:51` for
  `PCREC_ARTIFACT_ABI`. It is `:54`.
- **F-5 (add. 1's measure):** the "38 `A_EOL` references under `src/opt/`" are case labels
  that survive the fold (§4.4 D).
- **N-1 (new): the walk's bound is below the carrier's.** `PCREC_PREFIX_K_MAX` is 24, while
  kit_proof's `MkLang` and `MF_MAX_SPAN_POS` assume 32. With the slice as the extended k-set
  walk, a whole-cover body with `k` > 24 can state `exact_len` at most 24, and declines C8.
  kvcensus's `whole` column counts such bodies at 1 bench / 2 corpus native and 1 / 1 utf8.
  That is an upper bound, since conj.py's admitted subset is not split by `k`. Either the
  walk's limit is raised to a value derived from `MF_MAX_SPAN_POS` (a compile-budget
  re-measure, D90) or the four decline. That is the build's choice, with the count re-taken
  on the admitted set.
- **N-2 (new): the derived sabotage population is larger than any hand list** (§4.5.4). There
  are 16 rows beyond the panel's, 13 of them owner rows whose definitions P2c edits around
  their anchors. That is the third time the method has added rows a hand list missed
  (start_table, dec_fallback, here).
- **N-3 (new): `definitions.c`'s `eol_tail_plain` reads `A_END` as structure** (§4.6). Any
  `\z` fold that reaches the AST moves D164's `tagged`-form selection. That is one reason the
  leaning keeps the AST kinds.

## 12. What a review should attack

(a) §4.2.3's absent mapping. Is `right_abs = end_ok` exactly "right absent" on every reverse
start state (`s0`, `s1u[]`, the `rev-end` seeds), and is the reverse walk's left edge never
a closure question? (b) The table's three predicates. Is `ctxfn_reads_absent_prev` the only
thing `has_bot` needs, or does any reader of `pcrec_nfa_has_bot` rely on the KIND (emit_dfa's
P0 assertion reads `s0` vs `s1u[PLAIN]`)? (c) CK-4's text-side prediction. Is NFA order the
only thing that moves, and does any `(?m)` artifact share its newline set with a
`(?=\n)` that today sits in a DIFFERENT list slot? (d) §4.6's classification. Is any LABEL
site really a different arm, and is the NFA-level fold's "0 analysis movers" true for
`kset_walk` (an E3 fact that reads NFA kinds)? (e) §3.6's per-item grain against kit_proof's
stage 1. Can the machine reading ever need two items on one side? (f) §4.7's ill-formed
cases beyond the two named.

## 13. Disposition and discharge (every r4 id)

| id | sev | disposition | discharged in |
|---|---|---|---|
| A1 | BLOCKER | ACCEPT: `Sides` carries `left_abs`/`right_abs`, set per direction in `sides_of`; the witness `[a-z]+\b` at `n` joins CK-5; S341 re-aims to the bug | §4.2.3; §6 CK-5; §4.5.4 (S341); §7 P2b |
| A2 | MAJOR | ACCEPT: `run_wordctx_identity.sh`'s population becomes "no `A_CTX` source spelling" with the `(?m)` cells in its must-differ control; S76 retires, its re-aimed plant is S71's | §4.5.4 (gates table, S76 row) |
| A3 | MAJOR | ACCEPT: `(?m)` is `A_CTX` iff the convention's newline is one byte; else UL-e; the selector sits at definitions_table's convention customer | §3.3 (newline convention); §10 UL-e |
| A4 | MAJOR | ACCEPT: every `nullable` reader listed by grep and proved by value identity at P2c; test cells; the raw fn literals in tests into table C | §4.2.5 (possessify); §4.4 C; `ctx_span/readers.txt` §6-§7 |
| A5 | MINOR | ACCEPT: `(?m)$` ≡ `(?![^\n])` is an `A_CTX` under `byte` only; the `{\n}`-plus-absent row is REQUIRED for utf8 | §0; §4.2.4 |
| A6 | MINOR | ACCEPT: a typed `(?<!é)` is two bytes under `byte` too; `look-neg-1` lives only under `-fno-ctx-node`; unlock: record identity with/without it | §3.3; §3.5; §6 CK-10; §10 UL-h |
| A7 | MINOR | ACCEPT: the `rx_L3` hop is the inline option item's `A_EMPTY`; B3's "unexplained" closes | §4.5.3 |
| A8 | MINOR | ACCEPT: the `(?m)` node raises no lookbehind (libpcre2 0 for `(?m)^a`); `u.ctx.anchor = true` | §4.2.5 (lookbehind fact); §6 CK-4(b), SP-4d |
| A9 | MINOR | ACCEPT: a straddle ends `exact_len` AT `d`, not `d − 1` | §3.4 |
| B1 | MAJOR | ACCEPT: no `byte_form`; stage 1 sends EXACT items only; one entry per ITEM; the exactness fact filed as R-26.7 at UL-b/UL-g; kit_proof's grain contradiction fixed | §3.2; §3.9; kit_proof §4.1, §4.3 `[r4 B1]` |
| B2 | MAJOR | ACCEPT: the abi readers are a grep recipe's output, classified reader/record; then the suites that count | §4.5.1; `ctx_span/readers.sh` §1 |
| B3 | MAJOR | ACCEPT: P2c keeps arm A widening absent-reading rows; zero VM, route and possessify movers asserted; valuing is UL-c | §4.2.5; §4.5.3; §6 CK-4(c); §10 UL-c |
| B4 | MAJOR | ACCEPT (with A2) | §4.5.4 (gates table) |
| B5 | MAJOR | ACCEPT: the re-aim list is DERIVED (edit set + anchor map + owner/witness facts); S341 re-aims, S343 retires, the `rows` sharing logic deletes, the eight mover rows re-run | §4.4 B (rows); §4.5.4; `ctx_span/edit_set.tsv`, `derived_rows.tsv` |
| B6 | MAJOR | ACCEPT: SP-4's witness `(?m)^b` on `"a\nb"`; SP-4b and the `$` twin SP-4c; S77/S762/S900 retire with witnesses kept as corpus cells | §6 CK-4; §4.5.4 |
| B7 | MAJOR | ACCEPT all six: CK-1's non-silence floor; "share no code" restated; per-row populations; CK-2 generates absent-edge subjects; CK-5 under the predicted permutation; CK-4 confines each mover's diff | §6 (CK-1, CK-2, CK-4, CK-5, CK-7) |
| B8 | MAJOR | ACCEPT as re-ruled by Q-r4-2: ordering free; the re-run list if P2c lands between Z1 and B1; `conj.py` at P2c as the control | §7 |
| B9 | MAJOR | ACCEPT: kit_proof edited (pass-through limited to position-only kinds; the in-span half into UL-0 at Z2; three witnesses into `conj.txt` D and X0; X0 on every site stating `exact_len > 0`; S1149) | §3.8; kit_proof §5.2, §6.3, §6.4, `conj.txt` D `[r4 B9]` |
| B10 | MINOR | ACCEPT: the record's bounds are the producer's own (`PCREC_PREFIX_K_MAX`, two compile budgets); truncation at send | §3.2; §3.9; §11 N-1 |
| C1 | MINOR | ACCEPT: `dfa.c:345` and the comment census by grep (31 lines); the knob's readers outside `src/` derived | §4.4 B, E, F |
| C2 | MINOR | ACCEPT: the residual named; CK-9 ties the parser's choice to the registry rows | §4.3 (residual); §6 CK-9 |
| C3 | MAJOR | REJECTED by Q-r4-1 (the 9-cell table); priced in one paragraph | §4.2.1 ("Why not C3's composition") |
| C4 | MAJOR | ACCEPT (Q-r4-3): extend `kset_walk`; no `spans.c`; kit_proof renamed; the unified per-offset table filed | §3.1; §3.8; §9; §10 UL-j; kit_proof §0, §1.5, §5.1, §5.2, §7, §8.2, §8.3 `[r4 Q-r4-3]` |
| C5 | MINOR | ACCEPT: the `look-*` rows call the recognizer's walk | §3.3 |
| C7 | MINOR | ACCEPT: `cr_nl_set` deletes and `pcrec_cls_newline` is the one newline bitmap; counted | §4.4 B; §4.2.5 (VM) |
| U-B1 | unlock | FILED with its trigger | §10 |
| U-B2 | unlock | FILED; lands with P1a (CK-1, CK-7 per-row floors) | §10; §6 |
| U-B3 | unlock | APPLIED: `conj.py` re-run at P2c as the independent control | §7; §10 |
| U-B4 | unlock | APPLIED: one predicate per item, the stacking rules retired | §3.2; §3.6; kit_proof §4.1; §10 |
| C6 | (unlock list) | the engine-selection shift is predicted ZERO (the `has_bot` predicate), and UL-c is measurable on existing cells | §4.2.5; §4.5.3; §10 UL-c |
| A6 (unlock) | (unlock list) | as A6 | §10 UL-h |
| Q-r4-1 | ruling | APPLIED: one 9-cell table, the six re-encoded as rows, `(?m)` rows, A1; the `\A`/`\z` census (§4.6, P2d after the fold); the co-finite idea filed | §4.2; §4.6; §4.7; §5 Q5, Q7 |
| Q-r4-2 | ruling | APPLIED | §2; §5 Q2; §7 |
| Q-r4-3 | ruling | APPLIED | §3.1; §3.8; §9; kit_proof `[r4 Q-r4-3]` |

C6 has no finding row in r4's table. It sits in the unlocks list and is discharged above.
Every other r4 id is listed. Nothing in the review is left undischarged.
