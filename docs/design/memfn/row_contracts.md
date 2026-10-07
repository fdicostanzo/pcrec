# [MEMFN-ROWCON] Row contracts: one first-match table engine (design, rev 3)

Status: rev 3, 2026-10-07. Every question is RULED (Frank). It answers
both D6 panels:
- r1: `docs/dev/reviews/2026-10-07-r1-memfn-rowcon.md`, 71 ids, themes
  T-A..T-J;
- r2, the re-check with a pcrec-customer lens:
  `docs/dev/reviews/2026-10-07-r2-memfn-rowcon.md`, 47 ids, themes
  U-A..U-O.

Evidence is in `probes/rowcon/` (`audit_kit_rows.md`,
`audit_pcrec_tables.md`, `customers.md`). Theme ids are cited inline as
[T-x]/[U-x].

## 0. Problem, acceptance, rulings

A first-match table is sound only if no row can be chosen for an input
its action does not serve. K96 broke that: R4c's ofsskip arm presumed
`miss == n` and no `floor`. The r1 audit found 8 more such cells and 13
cells where rows disagree.

**Acceptance (Frank):**
- (V) visibility into every decision;
- (R) every row reachable by at least one pattern;
- (S) sound logic;
- (G) a general mechanism that pcrec's tables can use;
- (M) decisions move into memfn later.

**Rulings (2026-10-07):**
- **R1, a row may USE only a value the caller STATED.** It never presumes
  one. Unstated fields are wildcards, not defaults, so the caller does
  not specify everything, only what is used (Q-ROW-1 as clarified by
  Q-ROW-5).
- **R2, SNAPSHOT.** Caller value text is evaluated once into reserved
  locals, plus refusals for text that can change meaning in situ
  (Q-ROW-1(c), option B).
- **R3, no public deny on the snapshot.** G1 compares against the
  pre-snapshot commit (Q-ROW-6; a D144 item-4 exception for a correctness
  change).
- **R4, the kit hosts a general first-match table engine** as an `MF_NS`
  utility; D146's charter widens (Q-ROW-4). pcrec's tables MAY adopt it
  per table, an offer after START-TABLE C7 (D153).

The engine itself obeys R1. No field of its own means "all" or "none" by
being 0 [U-A].

## 1. Two layers

**Layer 1, the ENGINE** (`memfn/src/table.c`, `memfn/include/memfn_table.h`).
It is generic and search-blind. It provides:
- a row array of ANY struct whose first member is the common head;
- a filtered first-match walk;
- deny bits;
- an optional contract gate;
- a totality HOOK;
- a decision record and a printer;
- reach counters;
- row iteration.

**Layer 2, the KIT PROFILE** (`memfn/src/fields.def`, the kit's tables).
It provides the kit's field vocabulary, value classes, the uses/serves
gate, and the kit's two tables: the composer arms and runcmp's rows. A
pcrec table uses Layer 1 with no profile.

## 2. Layer 1: the engine

### 2.1 Head, table, typed thunk [U-A, U-B, U-C, U-D]

```c
typedef struct mf_row {            /* FIRST member of every row struct          */
    const char *name;              /* unique per table                          */
    uint64_t    deny;              /* caller deny bits; MF_DENY_NONE explicit   */
    uint32_t    scope;             /* MF_SCOPE_ONE, or the caller's slot value  */
    uint32_t    routes;            /* bit per route INDEX; MF_ROUTES_ALL;
                                      0 is a DEFINITION ERROR                    */
    const char *doc;
} mf_row;

typedef struct mf_table {
    const char *name;
    const void *rows; size_t stride, n;
    int  (*test)(const void *row, const void *ctx, uint8_t *reason);
         /* generated per table by MF_TABLE_TYPED: casts and calls the row's
            OWN predicate in its own type and polarity; 1 = holds            */
    unsigned (*route_of)(const void *ctx);  /* the ONE route carrier: ctx    */
    const char *(*tok)(const void *row);    /* the trace spelling (C1: tok)  */
    void (*on_none)(const void *ctx, const struct mf_decision *);  /* never NULL */
    const struct mf_profile *profile;       /* NULL = no gate                 */
    uint32_t nscopes; const char *const *scope_names, *const *route_names;
} mf_table;
```

- **Typed thunk [U-B].** `MF_TABLE_TYPED(pfx, RowT, CtxT, pred_member)`
  emits a `static` `test` that casts `row` to `const RowT *` and calls
  `row->pred_member((const CtxT *)ctx)`. pcrec's `bool (*)(const DfaSel *)`
  predicates are stored UNCHANGED, with no casts of function types and no
  polarity flip.
  - A NULL predicate is a definition error unless the table declares
    `MF_PRED_NULL_HOLDS`. That flag is fit_rungs' encoding, stated, not
    assumed.
  - Tag predicates (pcrec_reseed_rows) supply their own thunk.
- **Explicit tokens [U-A].** Each of the following is a definition error,
  checked once at table registration (`mf_table_check`, run by the
  customer's unit test and at startup in debug builds):
  - `routes == 0` (on main, 0 meant DFA-only in `cand_routed`, so a "0 =
    all" reading would have crashed vm_start_row);
  - a `scope` outside `MF_SCOPE_ONE` ∪ the declared slots;
  - a profiled row whose `uses` is unset (§4).
- **Route [U-D].** `route_of(ctx)` is the only carrier; the query holds
  none.

### 2.2 The walk and the call macro [U-C, U-E]

`MF_SELECT(t, ctx, flags, "site")` calls
`mf_select_(t, ctx, flags, "" "site", rec, opts)`. The `""` paste keeps
C1's compile-time literal check.

For each row in order the walk applies:
1. scope;
2. route (`routes & (1u << route_of(ctx))`);
3. deny (`row.deny & flags`);
4. the profile gate (§4);
5. `test`.

The first row passing all five is returned. Steps 1-2 are filters,
counted. Steps 3-5 are recorded per row.

On NO row: `on_none(ctx, rec)` is called.
- pcrec passes `pcrec_ctx_fail`; match_api §8.1's "never aborts on the
  compile path" holds.
- The kit passes `kit_fail`.
- With `MF_Q_NULL_OK` (the both-walks oracle's per-query option) it
  returns NULL instead.

**The engine never aborts [U-C].**

### 2.3 The decision record [U-E, U-G]

```c
typedef struct mf_verdict { uint16_t row; uint8_t kind, reason; uint64_t mask; } mf_verdict;
  /* DENIED (mask = fired deny bits) | DECLINED (mask = every unstated or
     unserved field, §4) | PRED_FALSE (reason) | CHOSEN                     */
typedef struct mf_decision {
    const char *table, *site; uint32_t scope, route;
    uint16_t filtered, n, depth; uint8_t overflow;
    mf_verdict v[MF_DECISION_MAX];
} mf_decision;
```

- **No parent pointers [U-G].** Nesting is a caller-owned bounded array
  of records plus a depth counter, set on entry, so a predicate that
  longjmps (`pcrec_ctx_fail`) leaves nothing dangling.
- **What it absorbs [U-E], narrowed:** C1's ROW-CHOICE records. The record
  prints `table`, `scope_names[scope]`, `route_names[route]` (or `-` for
  a no-route call), `tok(chosen)` and `site`, which are the same four
  fields C1's SET-compare gate reads.
  - C1's RECF/ROUTE pseudo-records are not decisions; they stay pcrec
    macros.
  - Every record argument is a value the walk already computed, so the
    record calls no new fact accessor (C1's rule).
- **Where a human sees it [T-F, U-M].** The records print under
  `MF_TRACE`, a compile-time switch, with the stderr tag `MFTRACE`. It
  is distinct from pcrec's `CANDTRACE`. The line format is a documented
  contract (`memfn/docs/trace_format.md`), because the census parses it.
  - The census builds through `scripts/emit_sweep.py --trace`, whose
    `KITFLAGS` already inherit `CFLAGS`. No Makefile change.
  - G2 and the kit CLI call `mf_decision_print` directly.
  - Nothing reaches an artifact, and no public struct changes layout.

### 2.4 Reach counters [T-G, U-M]

Under `MF_TRACE` only, kit-private statics count CHOSEN per row, and per
(row, used field, value class) for profiled tables. They are printed as
`MFTRACE REACH` lines at exit, and the census SUMS them across processes.
The kit counts at SUCCESSFUL render; pcrec tables count at select.

### 2.5 Rows, not listings [U-F]

`mf_table_row(t, i)` returns the head. Listings (`--list-axes`
projections such as `list[route]`, their order, unlisted rows) stay the
customer's code. Rev 2's "force = deny of the alternatives" and the
`strategy_denials` remark are RETRACTED.

## 3. Reference customers [U-H]

| # | customer | hosted | encoding |
|---|---|---|---|
| 1 | `cand_rows[]` (lane/stc2; 37 rows, 8 slots, 3 routes) | yes, Appendix A | `CandRow.h` replaces `CandRow.c`'s head; `slot`→`scope` (slot values used as-is; `MF_SCOPE_ONE` is a value outside `CandSlot`); `routes` kept bit-for-bit; `test` thunk over the existing `bool (*)(const DfaSel*)`; `route_of` reads `sel->route`; `tok` reads `row->tok`; `on_none` is `pcrec_ctx_fail`; the oracle uses `MF_Q_NULL_OK` |
| 2 | `dfa_pfs[]` / `DFA_SELECT` (ten structs with a `DfaCand` head) | yes | head per struct; tables WITHOUT a `routes` member write `CAND_ON(DFA)` explicitly. **Today's 0 means DFA-only, and that is preserved by writing it out**; `cand_always` stays a row |
| 3a | `esel_of` ladder; `fit_rungs[]` (compile.c) | yes | fit_rungs: `MF_PRED_NULL_HOLDS`, its degrading/FAST_OR_FAIL class deny as a `deny` bit, its fallback rung as the last row |
| 3b | `analyses[]` | **no** | an AND-reduction with a first-excluder `why`: not first-match (D152) |
| 4 | [POSS-CTX-TABLE] | **no** | indexed dispatch with folds and a fixpoint, not a decision table |
| 5 | deny/force axes | the `deny` column only | listings and force semantics stay the caller's (§2.5) |
| 6 | C1 trace | row-choice records | §2.3 |
| 7 | `pss_verdict` ladder | yes | a first-match ladder; `test` thunk; `on_none` = the caller's |
| 8 | `pcrec_reseed_rows[]` (closed tags + prose) | yes | a custom `test` thunk mapping the tag to the predicate; tags stay data |

The proof beyond paper is T0's fixture: a kit unit test with a
`cand_rows`-SHAPED table (slot values starting at 0, `MF_SCOPE_ONE`
outside them, 3 routes by index, bool predicates via the thunk, an
`on_none` that records, `MF_Q_NULL_OK`) walked against a hand-written
copy of stc2's walk, i.e. the both-walks pattern. It also has a
dfa_pfs-shaped table with a routes-less struct. No pcrec file is touched.

## 4. Layer 2: the kit profile (R1 applied) [T-A, U-I, U-J]

### 4.1 `fields.def`

`MF_FIELD(name, binding, classify, classes, doc)`:
- **binding [T-A]:** SITE | DEFINE_BOUND (value-equal at define and use,
  e.g. a FUNC `floor`) | USE_ONLY | DEFINE_ONLY. Each phase checks its own
  fields.
- **classify:** ONE function per field, mapping a STATED value to a
  class, or `MF_CLS_UNSTATED`.
  - Pointer/text hooks: NULL means UNSTATED.
  - Enums a row uses get an explicit `*_UNSTATED = 0` member, so
    zero-initialisation reads as "not stated", never as a choice. That
    is the enum half of R1, with no blanket stated-bitmask (Q-ROW-5 as
    clarified).
  - Numeric facts a site KIND always carries (terms, offsets,
    `plan_hint`) are per-kind OBLIGATIONS, checked as present by kind,
    not classified.
  - Callbacks: an absent offer is not a value (a WRITTEN exemption).
- **classes:** a closed set per field, always including `OTHER`, e.g.
  `miss` ∈ {`MISS_N`, `OTHER`}, `floor` ∈ {`ZERO`, `OTHER`}, `empty` ∈ one
  class per value. A token added later lands in `OTHER` until classified.

### 4.2 Rows declare USES and SERVES [U-I, U-J]

Each profiled row declares:
- `uses`: the fields its output reads. This is also the snapshot set
  (§5).
- `serves`: per used field, the classes it handles.

The gate, per phase, field by field. A STATED value is a caller
REQUIREMENT, and an unstated field is a wildcard. For each field, as one
first-match rule:
1. **used and unstated:** DECLINE. The row would have to presume a value
   (R1).
2. **stated, class not in `serves`:** DECLINE. The caller asked for
   something this row would ignore or mis-serve. This catches K96's
   half that "uses" alone misses: a stated `floor` the row never reads.
3. **otherwise:** pass. That covers an unstated field the row does not
   use (a wildcard), and a stated field whose class the row serves.

`serves` may list `UNSTATED` and `ANY`:
- `UNSTATED` = "correct when the caller says nothing";
- `ANY` = "correct for every value, because the field is irrelevant to
  this row's output". An irrelevant field must be declared, never
  assumed.

A field absent from a row's `serves` serves NOTHING, so ANY stated value
declines. A field added to the contract later is therefore declined by
every row until someone declares it (fail-safe).

A failing row is DECLINED, with the mask of every failing field. If no
row serves the site, `on_none` (kit_fail) names the fields.
- ofsskip serves `floor` {UNSTATED, ZERO} and `miss` {MISS_N}. pcrec
  states `miss = MF_MISS_N` (its result IS returned) and need not state
  `floor`. **Zero movers.**
- G2's `miss = n + 5` (`OTHER`) or `floor = lo + 2` (`OTHER`): ofsskip
  declines and generic serves.
- A row whose service depends on the predicate's SHAPE (PRE's `floor`) is
  SPLIT into rows with disjoint predicates.
- Generic serves `OTHER` for every field it uses. Where it cannot, the
  value is a contract refusal in `fields.def`, checked by G2.

### 4.3 Who checks the uses lists (the rows' own author can't) [U-J, U-N]

- **G2 POISON differential.** Every field the chosen row declares `ANY`
  (irrelevant), or does not use, is set to a poison value (wild text, an
  out-of-range enum). The render must be byte-identical to the unpoisoned
  one, or, for a non-ANY field, the row must now DECLINE. A row
  that reads an undeclared field fails, which is K96's exact shape.
- **`cells.tsv`,** written by a BLINDED author from the contract: the
  (row, field, class) cells that must be reached. It does not derive
  from `fields.def`.

## 5. The snapshot (R2) [U-K]

Caller value hooks in the chosen row's `uses` are evaluated ONCE, in
declaration order, into `_mf_<site>_<hook>` locals (block scope; the
`_mf_` prefix is not user-choosable via `-p`), each written as `(hook)`:

| site shape | placement |
|---|---|
| STMT | declarations at the top of the site's own block |
| EXPR (VMRUN, guard-conjoined) | a GNU statement expression `({ … })`, as generic already uses |
| FUNC define | none (no caller values at define) |
| FUNC use (a call) | the arguments ARE the snapshot (one evaluation each), but their order is unsequenced; a FUNC use with ≥ 2 hooks is wrapped in `({ })` with sequenced snapshots, then the call |
| ASSIGN with `result_decl` | snapshots precede the declaration in the caller's scope, with names unique per use (`_mf_<site>_<hook>`) |
| ADVANCE `more`/`peek`, ON_CAND per-iteration values | EXCLUDED: per-iteration by design (contract: side-effect-free; G2 checks this by evaluating them twice) |

- **Only `uses` hooks are snapshot.** That keeps `-Wall -Wextra -Werror`
  clean, with no unused locals.
- **Refusals,** applied to the hook text the chosen row uses:
  - a comment, `#` or backslash-newline;
  - an identifier with the `_mf_` prefix;
  - `on_miss`/`on_cand` not a single `goto`/`return` or a braced block;
  - a bare `break` or `continue` inside a kit loop, which would bind to
    the kit's own loop.
- **Abi event (T3b), in ONE commit:**
  - the pcrec abi bump, with readers found by grep (D76/D94);
  - the stamps;
  - the D80 hunk (the caller-text contract);
  - G1 at BOTH layers against the pre-snapshot commit (R3; no deny row).

  It is its own abi event, never combined with [ART-POSS-ARMS]'s (pcrec
  manager's sequencing, for bench attribution).

## 6. Reach and independent controls (R) [T-G, U-N]

- **Cells:** (row, used field, class), as listed in `cells.tsv`.
- **Independent controls,** none derived from the engine or `fields.def`:
  1. `tests/memfn/rows.tsv`: a hand-maintained name manifest, one line
     per row, with its reach reason and witness;
  2. a TEXT SIGNATURE per row, checked in its witness's artifact;
  3. G2 byte-loop agreement on every reached cell;
  4. the poison differential (§4.3);
  5. start_table §3.4's deny-delta control;
  6. the census's own population counts: compiles traced, witnesses
     executed.
- **Rows unreached from pcrec** take a closed reason: `total-fallback`,
  `pending-site:<trigger>` or `contract-reach:<G2 family>`. Anything
  else is deleted (D77).
- **Literal floors** in `docs/spec/`: rows per table and witnessed rows.

## 7. Plan (each step its own commit, gate vs main, always green) [U-L]

| step | content | movers |
|---|---|---|
| T0 | Layer 1 + `mf_table_check` + `MF_SELECT` + record/printer + `MF_TRACE` + `trace_format.md`; the fixture tables (cand_rows-shaped, dfa_pfs-shaped); C15/C16; memfn/CLAUDE.md charter line (R4) | none |
| T1 | runcmp rows onto Layer 1 (no profile) | none (listing byte-identical) |
| T2a | `fields.def`, classify, the gate; composer arms onto Layer 1 with `uses`/`serves` (Appendix B). The gate runs in WARN mode: a recorded verdict, selection unchanged | none (gate vs main) |
| T2b | arm names in `--list-axes`' memfn section | ONE declared listing mover (dumps stream, D80, registry re-pins, the section floor reached) |
| R-6 | pcrec states what its sites' chosen rows USE and cannot be left as a wildcard (inventory from Appendix B: e.g. `MF_MISS_N` on valued handoffs; NOT `floor`) | none (a pcrec lane; nothing refuses yet) |
| G2u | the blinded G2 update: `cells.tsv`, the poison differential, explicit tokens, refusal expectations | none |
| T3a | the gate ENFORCES (declines/refusals on); enum `UNSTATED` members; precheck serves a stated `miss`; the PRE floor row split | none (gate) |
| T3b | the snapshot + refusals (§5) | **ABI EVENT** (§5) |
| T4 | reach: `rows.tsv`, signatures, census via `emit_sweep --trace`, floors | none |

Sub-tables stay DROPPED until a K96-class finding inside a row's
sub-choice (D77) [T-I].

## Appendix A: `cand_rows[]` on the engine (lane/stc2)

| today | engine | identity argument |
|---|---|---|
| `DfaCand c {name, deny, applies}` | `mf_row h {name, deny, scope, routes, doc}` + the row keeps `applies` as its own member | `test` thunk = `row->applies(sel)`; same type, same polarity |
| `slot` | `h.scope` (slot values unchanged) | `MF_SCOPE_ONE` lies outside `CandSlot` |
| `routes` (`CAND_ON` bits) | `h.routes` (same bits; 0 rejected) | every stc2 row already writes its mask |
| walk: slot, deny, route, applies | scope, route, deny, (no gate), test | filters commute with deny; first-match order is unchanged |
| `cand_always` + missing-fallback | `on_none = pcrec_ctx_fail`; the oracle `MF_Q_NULL_OK` | no abort on the compile path |
| `sel->route` / `cand_route_of` | `route_of(ctx)` | one carrier |
| trace `(slot, route, tok, site)` | record → `scope_names`, `route_names`, `tok`, `site` | the SET gate lines are identical; RECF/ROUTE stay macros |
| `tok`, `map`, `giveup`, `hands`, `list[3]`, `was`, `u` | payload | untouched |
| `cand_nodes[]` | not the engine's | stays pcrec's static check |

## Appendix B: kit rows, USES and SERVES (from the audit matrix; T2a fills exact)

| row | uses (beyond the predicate) | serves |
|---|---|---|
| ofsskip | `s`, `n`, `lo`, `miss`, `fn_name`, `comment_tier` | `miss` {MISS_N}; `floor` {UNSTATED, ZERO} (not used, but a stated floor must be honoured) |
| precheck (split by shape) | `s`, `n`, `lo`, `miss`, `result`, `on_miss`, `on_miss_leaves`, `floor` (run-shaped row only) | `miss` {MISS_N, OTHER} after T3a; `floor` {UNSTATED, ZERO} or {UNSTATED, ZERO, OTHER} per split |
| runcmp (VMRUN) | `s`, `lo`, `denies` | all classes of its used fields |
| generic | all used fields | `OTHER` for each, or a contract refusal |

Rev 3 closes the r1 "NOT" ids (sound M3, the per-row list, is this
table) and every r2 theme. A one-critic soundness spot-check on §4-§5
precedes T0.
