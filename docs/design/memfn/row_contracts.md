# [MEMFN-ROWCON] Row contracts: one first-match table engine (light design, rev 2.1)

Status: rev 2, 2026-10-07. It answers the r1 D6 panel
(`docs/dev/reviews/2026-10-07-r1-memfn-rowcon.md`, 71 ids, themes T-A..T-J)
and adds pcrec's decision tables as REFERENCE CUSTOMERS. That was
Frank's point, relayed by the pcrec manager: rev 1 was kit-centred.
**Rev 2.1 (same day):** Frank RULED Q-ROW-1 in a different form from the
recommendation. There are NO silent defaults (§4.2), and hooks are
SNAPSHOT once (§4.4, option B). **Still pending:** Q-ROW-4 (charter, §6),
which this revision assumes is ruled as recommended.

Evidence, under `probes/rowcon/`:
- `audit_kit_rows.md`: the kit's rows, the field × row matrix, 8 suspect
  cells, 13 disagreements;
- `audit_pcrec_tables.md`: pcrec's tables and the boundary;
- `customers.md`: six pcrec reference customers in detail, with
  `lane/stc2`'s `cand_rows[]` exact.

## 0. Problem and acceptance

A first-match table is sound only if each row's test covers every input
its action does not honour. K96 broke that (R4c's ofsskip arm assumed
`miss == n` and no `floor`). The audit found 8 more such cells and 13
places where rows disagree on the same field.

Frank's acceptance criteria:
- (V) visibility into every decision;
- (R) every row reachable by at least one pattern;
- (S) sound logic;
- (G) a GENERAL mechanism that pcrec's tables can use, partially
  generalized if need be;
- (M) decisions move into memfn later, so the mechanism is built to be
  the destination.

## 1. Two layers

**Layer 1, the ENGINE (generic, `memfn/src/table.c`, a kit utility under
`MF_NS`).** It knows nothing about search sites. It provides: an ordered
row array with a common head, a filtered first-match walk, deny bits, a
pluggable contract gate, a totality policy, a decision record with a
printer, reach counters, and a listing accessor. This layer is what
pcrec's tables can adopt (§3).

**Layer 2, the KIT PROFILE (`memfn/src/fields.def` + the kit's tables).**
The kit's own field vocabulary, with defaults, binding times, kinds and
value classes; the stated-value check; the `honours`/`requires` gate; and the
kit's tables: the composer arms, and runcmp's rows. A pcrec table uses
Layer 1 with NO profile, so its gate is a no-op (honours = ALL). That is
the "partially generalized" seam. pcrec can grow its own profile later
from the same Layer-1 hook.

## 2. Layer 1, the engine

### 2.1 The row head and the table

```c
typedef struct mf_row {          /* the COMMON HEAD: first member of every row  */
    const char *name;            /* unique within the table; listing/trace name */
    uint64_t    deny;            /* caller's deny bits (pcrec: PCREC_NO_*)      */
    uint32_t    scope;           /* sub-table id (cand_rows: CandSlot); 0 = one */
    uint32_t    routes;          /* route mask; 0 = all routes                  */
    int       (*applies)(const void *ctx, const struct mf_row *self);
                                 /* 0 = holds; >0 = reason code (1 = "false")   */
    uint64_t    honours, requires;  /* profile masks; 0/0 = no profile          */
    const char *doc;
} mf_row;

typedef struct mf_table {
    const char *name;            /* table id in records and listings            */
    const void *rows; size_t stride, n;   /* rows of ANY struct with mf_row first */
    const struct mf_profile *profile;     /* NULL = no gate (pcrec tables)      */
    int         on_none;         /* MF_NONE_NULL | MF_NONE_ABORT (cand_always)  */
    unsigned    nscopes;         /* for listing and reach                       */
} mf_table;

typedef struct mf_query {
    uint32_t scope, route;       /* filters                                     */
    uint64_t flags;              /* deny flags in effect                        */
    const char *site;            /* caller's site key (opaque; pcrec: a literal)*/
    const void *subject;         /* profile input (kit: site+hooks); else NULL  */
} mf_query;

const mf_row *mf_select(const mf_table *, const mf_query *, const void *ctx,
                        mf_decision *rec /* NULL = no record */);
```

- **Stride, not a fixed row type.** A customer's row is any struct whose
  FIRST member is an `mf_row`. That is exactly how pcrec's ten row
  structs share `DfaCand` today (customers §2.9). Payload columns stay
  the customer's (e.g. `cand_rows`' `hands`, `list[route]`, `tok`,
  `map`, `giveup`).
- **Typed thin wrapper.** `MF_TABLE_TYPED(prefix, RowT, CtxT)` generates
  `static inline const RowT *prefix_select(const CtxT *, …)`, so a
  customer keeps typed predicates and typed results. The wrapper is
  header-only; the walk itself is one copy in `table.c`.
- **The walk, in this order:**
  1. scope;
  2. route;
  3. deny (`row.deny & q.flags`);
  4. the profile gate (§4), if a profile exists;
  5. `applies`.

  The first row passing all five wins. The order of the first four is
  cand_rows' own order (customers §1.2). Steps 1-2 are FILTERS, recorded
  only as a count. Steps 3-5 are recorded per row.
- **Totality.** If no row is chosen: `MF_NONE_ABORT` aborts with the
  record printed, which is pcrec's deliberate crash-on-missing-fallback,
  kept. `MF_NONE_NULL` returns NULL and the caller decides; the kit
  refuses through `kit_fail`.

### 2.2 The decision record (V, M)

```c
typedef struct mf_verdict { uint16_t row; uint8_t kind; uint8_t reason;
                            uint64_t mask; } mf_verdict;
     /* kind: DENIED (mask = the deny bits that fired) | GATED (mask = ALL
        failing fields) | REQUIRES_MISSING (mask) | PRED_FALSE (reason) |
        CHOSEN */
typedef struct mf_decision {
    const char *table, *site; uint32_t scope, route;
    uint64_t subject_mask;           /* profile: the non-default fields      */
    uint16_t filtered, n; mf_verdict v[MF_DECISION_MAX];  /* bounded; overflow
                                        sets a flag and keeps the CHOSEN entry */
    const struct mf_decision *parent;  /* nesting (a decision made inside a
                                          row's action); depth bounded         */
} mf_decision;
void mf_decision_print(const mf_decision *, mf_sink *);
```

- The record holds **every** failing field, the deny source and a
  predicate reason code (r1 vis majors). The record is computed only from
  values the walk already holds, so an adopter calls NO new fact accessor
  to fill it. That is C1's rule "a record argument is a value the
  decision already computed", kept (customers §6).
- **Mapping onto C1's trace** (customers §6), field for field:
  - `slot` is `scope` (named through the table's scope-name list);
  - `route` is `route`;
  - `row` is the CHOSEN verdict's row name;
  - `site` is `site`.

  pcrec's `PCREC_CAND_TRACE_REC` stays a pcrec macro, because it
  enforces the literal with `"" site` at compile time, which a function
  cannot. It passes that literal into `mf_query.site`. **The SET-compare
  diff gate C1 uses (customers §6.3) reads the same four fields**, so a
  migrated trace line is the same line.
- **Where a human sees it.** The engine prints only when the build
  defines `MF_TRACE`, a compile-time switch, off by default. pcrec's
  traced build (site_census, `PCREC_CAND_TRACE`) defines both. In that
  build every kit decision during a pcrec compile prints one block to
  stderr. G2 and the kit CLI call `mf_decision_print` directly.
  - Nothing reaches an artifact.
  - No `mf_result`/`mf_call` field changes.
  - No `form_id` is compared.
  - There is NO pcrec-side request: rev 1's T6 is DROPPED (r1 T-F).

### 2.3 Reach counters (R)

Under `MF_TRACE` only, each table keeps CHOSEN counts per row, and (with
a profile) per (row, honoured field, value class) cell (§4.1). They are
printed as `REACH` lines at exit. Corpus totals are SUMMED BY THE
CENSUS from the trace output across processes; nothing is kept in
`mf_art` (r1 contract M6). The kit counts at SUCCESSFUL render, so a
row chosen and then refused at use is not "reached" (r1 reach M5).
pcrec tables count at select, because nothing refuses after it.

### 2.4 Listing

`mf_table_rows(t, i)` yields `{name, deny, scope, routes, doc}`.
- It is the single source for a table's `--list-axes` section, so the
  axis registry derives from the rows rather than restating them. That
  is the D152 "one spelling" rule.
- One deny bit may sit on many rows. Fact-level denies are not rows, and
  stay outside the engine.
- The `rx_info.flags` mask (which denies an artifact reports) stays the
  caller's (customers §5.4).

## 3. Reference customers: what the engine hosts, and what it does not

| # | customer | hosted? | how |
|---|---|---|---|
| 1 | `cand_rows[]` (START-TABLE C2, lane/stc2; 37 rows, 8 slots, 3 routes) | **yes**, Appendix A | `CandRow` begins with an `mf_row` in place of its `DfaCand`; `slot`→`scope`, `routes`→`routes`; the payload columns stay. `cand_select(slot, sel)` becomes a typed wrapper over `mf_select`. `cand_nodes[]` (the typed handoff graph: accepts/asks/succ) is NOT a selection table; it stays pcrec's static check data, untouched |
| 2 | `dfa_pfs[]` / `DFA_SELECT` (ten row structs sharing a `DfaCand` head; stride walk; optional `routes` by offsetof; crash on missing fallback) | **yes** | the head becomes `mf_row`; the stride walk is the engine's; the optional `routes` becomes `routes = 0` (= all); `cand_always` + `MF_NONE_ABORT` |
| 3 | engine selection (`select_engine.c`) | **partly** | `analyses[]` is an AND-reduction with a first-excluder `why`, NOT first-match. D152 says it is the wrong tool, so it is not hosted. The `esel_of` ladder and `fit_rungs[]` (compile.c) ARE first-match and hostable |
| 4 | [POSS-CTX-TABLE] (per-AKind context table) | **no** | it is indexed by kind with multi-result folds and a fixpoint: a dispatch table, not a decision table. The record and reach printer could still be reused if it ever selects |
| 5 | deny/force axes (`axes.def`) | **yes**, as the deny column | the engine reads the caller's `uint64` deny bits; `--list-axes` sections derive from `mf_table_rows`; force bits stay the caller's (a force is a deny of the alternatives, expressed in the caller's flags) |
| 6 | C1's trace | **absorbed** | §2.2's mapping; the macro and its literal check stay pcrec's |

**No pcrec adoption is planned** (D153 remodel-first). Customers 1, 2,
3's ladder and 5 are an OFFER to [START-TABLE] after C7 and to
[DEC-FALLBACK]. The proof that this is not just on paper is T0's
fixture: a kit unit test builds a `cand_rows`-SHAPED table (8 scopes, 3
routes, a payload struct with a stride, `MF_NONE_ABORT`, a typed
wrapper) and walks it under the both-walks pattern, i.e. an old
hand-written walk vs `mf_select` over the same rows, as stc2's oracle
does. No pcrec file is touched.

## 4. Layer 2, the kit profile (soundness, S)

### 4.1 `fields.def`, one row per site/hook field

`MF_FIELD(name, kind, binding, default_test, classes, doc)`:
- **kind** (r1 sound M1): OBLIGATION (the caller must state it), PERMISSION
  (the kit may use it), REQUIREMENT (a row needs it present) or RENDERING
  (text shape).
- **binding** (r1 T-A, the blocker): SITE (in `mf_site`), DEFINE_BOUND
  (stated at define, must be value-equal at use, e.g. a FUNC `floor`;
  this fixes S8), USE_ONLY (subset-checked at use, can only refuse) or
  DEFINE_ONLY. Each phase runs its own gate. **Rev 1's "use mask ==
  define mask" rule is withdrawn**, because it refused every PRE/OFS site
  pcrec sends.
- **stated_test** (Q-ROW-1 as ruled): the ONE spelling of "this field is
  STATED". There is NO default column. Unset means "not stated", and a
  row that READS an unstated field is refused loudly (§4.2).
- **classes**: value classes for reach cells. Multi-valued enums such as
  `empty` or `need` get one bit per value.

### 4.2 No silent defaults (Q-ROW-1, ruled 2026-10-07)

Frank: implicit defaults are "bugs waiting to happen … assumptions that
may be forgotten in the moment … not seen until circumstances line up".
So:
- Every field a row's output depends on must be STATED. NULL means "not
  stated", never a value.
- `mf_check_stated(site, hooks, row)` refuses, naming the field, whenever
  the chosen row reads an unstated field. This replaces rev 2's
  normalization, so rows can no longer disagree on what "unset" means,
  because unset means nothing. Disagreements #1-#4 are closed by that
  refusal.
- The common values get NAMED explicit tokens, never NULL:
  - `miss = MF_MISS_N` ("the function's `n`");
  - `floor = "0"`;
  - `indent = ""`;
  - …

  A call site therefore shows what it assumes, and it can be grepped.
- **pcrec states its values** (`MF_MISS_N`, `"0"`, …) in its hook
  builders. The emitted text is identical, so there are zero movers (the
  gate verifies). The hook text is pcrec's (the boundary table), so this
  goes as REQUEST R-6 to the pcrec manager.

### 4.3 The gate, `honours` and `requires`

- A row is admitted iff `nondefault ⊆ honours` AND `requires ⊆
  present`. `requires` carries positive needs, such as precheck's
  `on_miss_leaves` (r1 sound M4) and disagreements #5-#7, the
  "this row needs the hook" cells.
- A row whose honouring depends on the predicate's SHAPE (PRE's `floor`,
  r1 sound M5) is SPLIT into two rows with disjoint predicates, never
  given a shape-dependent mask.
- **The generic row** honours every field it handles. Where it cannot
  honour a value, that is a CONTRACT refusal, written in `fields.def`.
  The rev-1 static assert was vacuous (r1 sound M6). Instead, G2's
  per-field cells on generic (§5) check that generic HONOURS what it
  claims.

### 4.4 Caller text: snapshot once, refuse the rest (option B, ruled 2026-10-07)

Caller text pasted in situ can be legal C that MEANS something other than
intended. The hazards are:
1. casts that look parenthesized;
2. side effects and calls evaluated once per paste;
3. a hook identifier captured by a kit local;
4. comments, backslash-newline or `#` swallowing kit text;
5. a dangling `else` bound to an `if` inside `on_miss`;
6. silent signed/unsigned conversion;
7. a macro identifier expanding to a non-primary expression;
8. caller code (`on_cand`) writing a hook variable mid-site.

A text check alone cannot close 6-8. The ruling is STRUCTURAL:
- **Snapshot.** At the top of each site the kit evaluates each value hook
  EXACTLY ONCE, into its own reserved local, inside parentheses: `const
  size_t mf_lo = (lo);`, and likewise for `s`, `n` and the rest. Every
  later use reads the snapshot. That closes 1, 2 (calls are therefore
  ALLOWED: they run once), 7 and 8 by construction, and turns 6 into one
  explicit conversion.
- **Reserved namespace.** Every kit local takes the `mf_` prefix (the
  exact spelling is decided in T3), and a hook text that names an
  identifier in it is refused. That closes 3.
- **Lexical refusals.** Hook and statement text containing a comment,
  backslash-newline or `#` is refused. That closes 4.
- **`on_miss` / `on_cand`** must be ONE jump statement (`goto`, `return`,
  `break`, `continue`) or a braced block. That closes 5.
- **This MOVES BYTES at every delegated site.** The snapshot locals are a
  pcrec abi event, landing in the SAME commit as:
  - the abi bump, with re-pins found by grep (D76/D94);
  - the stamp values;
  - the D80 spec hunk for the caller-text contract;
  - G1 at BOTH layers, its deny row being `--memfn=no-snapshot`.

  The deny is the alpha OFF arm only: it reinstates the hazard and is
  never a supported mode. The trigger is correctness (the K96 class),
  ruled by Frank. G1 must show no slowdown, since the optimizer should
  erase the locals. A measured slowdown is a finding that goes back to
  Frank, not a reason to drop the rule silently.
- S1 (precheck ignoring a stated `miss`) is fixed by honouring it, i.e.
  writing it, which pcrec's explicit `MF_MISS_N` makes the same text.

### 4.5 The contract package (r1 contract M1)

Q-ROW-1's rulings (§4.2, §4.4) change the kit contract, so they come with:
- integration.md rev 4.9;
- `MF_SITE_ABI` 4→5 (kit-internal; no pcrec byte);
- a responses.md notice;
- G2 expectation updates by a BLINDED author after lane g2x: unstated
  fields become expected refusals or explicit tokens. The ~326 ternary
  hook-text sites STAY valid, because the snapshot makes them safe;
- the snapshot's abi event (§4.4) in its own commit.

## 5. Reach and independent controls (R)

- **Grain** (r1 reach B1). Reach is counted per row AND per (row,
  honoured field, value class). A row reached only at defaults does not
  count as reaching the fields it claims to honour.
- **Independent controls** (r1 reach B2): none shares a source with the
  engine or the profile.
  1. A committed NAME manifest, `tests/memfn/rows.tsv`: one line per
     (table, row) with its reach class and its witness. It is
     hand-maintained, so a row added or removed without a line fails.
  2. A TEXT SIGNATURE per row, checked in the witness artifact: a
     substring the row's form writes, e.g. `!memcmp(` for runcmp
     memcmp. A witness that drifts to another row fails here even when
     the kit's record agrees with itself ([MECH-REACH]).
  3. G2 byte-loop agreement on every reached cell.
  4. start_table §3.4's deny-delta control: denying a row must move
     exactly that row's witness.
- **Rows unreachable from pcrec** use a CLOSED reason vocabulary (r1 reach
  M4): `total-fallback` (generic), `pending-site:<trigger>`, or
  `contract-reach:<G2 family>`. Anything else is deleted (D77).
- **The literal floors** in `docs/spec/` are row counts per table and
  witnessed-row counts. They are kept as the last-resort control.

## 6. Questions (Frank)

- **Q-ROW-1, RULED (Frank, 2026-10-07):** NO silent defaults. Values are
  stated explicitly, with named tokens; an unstated field a row reads is a
  loud refusal (§4.2). Caller text is SNAPSHOT once into reserved locals,
  plus lexical and statement-shape refusals (§4.4, option B). The
  snapshot is an abi event, accepted for correctness.
- **Q-ROW-4, charter (PENDING).** Layer 1 is a generic engine in the kit,
  which widens D146's "search-site text" charter. Recommendation: yes, as
  a kit UTILITY under `MF_NS`, with a charter line in memfn/CLAUDE.md.
  Decisions move into the kit (Frank), and the kit cannot link pcrec. If
  ruled no: Layer 2 stays in the kit, Layer 1 shrinks to a kit-private
  walk, and generality waits.
- Q-ROW-2 (no pcrec hook; §2.2) and Q-ROW-3 (no pcrec adoption now; §3)
  are ANSWERED.

## 7. Plan (each step its own commit; gate vs main; ONE ruled abi event, T3b)

| step | content | movers |
|---|---|---|
| T0 | Layer 1: `table.c`, `mf_row`/`mf_table`/`mf_query`/`mf_select`/`mf_decision`, `MF_TABLE_TYPED`, `MF_TRACE` printer + REACH lines, `mf_table_rows`; unit tests, including the `cand_rows`-SHAPED fixture under both walks (§3); C15/C16 (`MF_NS`, SPDX, PROVENANCE) | none |
| T1 | runcmp's `rc_row` onto Layer 1 (no profile needed: its inputs are run facts) | none; `mf_run_rows` listing byte-identical |
| T2 | Layer 2: `fields.def`, the gate; the composer arms onto Layer 1 with `honours`/`requires` from the audit matrix; ofsskip's `miss`/`floor` decline replaced by the gate | ONE DECLARED listing mover: `--list-axes`' memfn section gains the composer arms (dumps stream, D80 hunk, registry re-pins, the section floor goes from UNREACHED to REACHED), same commit (r1 T-D) |
| T3a | no silent defaults (§4.2): `mf_check_stated`, the named tokens, precheck honours `miss`, the rows split for shape-dependent `floor`; with pcrec's R-6 (state `MF_MISS_N`/`"0"`/…) | none (gate) |
| T3b | snapshot + reserved namespace + lexical/statement refusals (§4.4) | **ABI EVENT**: every delegated site; abi bump + grep re-pins + stamps + D80 hunk + G1 both layers, deny `--memfn=no-snapshot`, in ONE commit |
| T4 | reach: `rows.tsv`, signatures, the census over pcrec's traced build (`MF_TRACE` + `PCREC_CAND_TRACE`), G2 per-cell floors with g2x's families, deny-delta | none |

DROPPED from rev 1: T4-old (the sub-tables: no measured need, D77; they
come back on a K96-class finding inside a row's sub-choice) and T6 (the
pcrec hook). The arm denies move no DEFAULT byte. A deny that sends a
delegated site to generic does move bytes when it is used: it is that
arm's OFF arm, and its alpha is owed only when the arm itself moves a
byte.

## Appendix A: hosting `cand_rows[]` on paper (customers §1, lane/stc2)

| `cand_rows` today | engine | note |
|---|---|---|
| `CandRow.c` (`DfaCand{name, deny, applies}`) | `CandRow.h` (`mf_row`) | `applies(const DfaSel*)` is called via the typed wrapper; the returned bool maps to 0/1 |
| `slot` (CandSlot, 8 values) | `h.scope` | the table's `nscopes = CAND_NSLOTS`; scope names = `cand_nodes[i].name` |
| `routes` (`CAND_ON` mask, on every row) | `h.routes` | the same bits; `mf_query.route = sel->route` |
| `tok`, `map`, `giveup`, `hands`, `list[3]`, `was` | payload (unchanged) | the stride walk skips them; `list[route]` keeps feeding `--list-axes`, or moves to `doc` per route |
| the walk `:8131-8141` (slot, deny, route, predicate) | `mf_select` (scope, route, deny, gate=none, applies) | identical outcome: the filters commute with deny; first-match is preserved |
| `cand_always` + crash on none | `MF_NONE_ABORT` | the record is printed before the abort |
| `cand_route_of(cx)` | the caller's | it builds `mf_query.route` once (the ONE route derivation stays pcrec's) |
| `cand_nodes[]` (accepts/asks/succ) | not the engine's | a static graph check over row payloads (`hands`); `cand_rows_check.py` stays pcrec's |
| both-walks oracle (`PCREC_CAND_TRACE`) | supported | `mf_select` is pure; the oracle runs the old walk and `mf_select` and compares the chosen row |
| `PCREC_CAND_TRACE_REC(slot, route, row, site)` | `mf_decision` (§2.2) | the macro keeps `"" site`; the SET diff reads the same four fields |
| the per-slot payload `u` (C3-C5, not built yet) | payload | future columns ride the stride; the engine never reads them |

Nothing in that mapping needs a special case in the engine. The one
cost is the typed wrapper per table, which is one macro line.
