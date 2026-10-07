# [MEMFN-ROWCON] Row contracts: one table mechanism (light design, rev 1)

Status: DRAFT for a D6 panel (2026-10-07). It is the kit manager's design,
opened by Frank after K96. Evidence: `probes/rowcon/audit_kit_rows.md`
(the kit's rows, a field × row matrix, visibility and reach) and
`probes/rowcon/audit_pcrec_tables.md` (pcrec's tables, prior designs, the boundary). Both are
committed under `probes/rowcon/`; the design restates the facts it relies
on.

## 0. The problem, in one paragraph

A first-match row table is only sound if every row's applicability test
covers every input its action does not honour. K96 broke that rule: R4c's
ofsskip arm returned `n` on a miss and never read `floor`, yet it
accepted any FIND/FUNC/RETURN site. pcrec never sends a stated `miss` or
`floor`, so the bug lay latent until G2 reached the arm. The audit found
**8 more K96-class cells**, most of them in the pre-check arm:
- it ignores a stated `miss`;
- it pastes `s`/`n`/`lo` unparenthesized;
- it emits `on_miss` unbraced;
- runcmp pastes `s`/`lo` unparenthesized;
- the generic row drops a define/use `floor` mismatch.

It also found **13 rows-disagree cells**, e.g. `miss` NULL is refused by
the generic row and read as `n` by ofsskip. All are unreachable from
pcrec today. The root cause is structural: **a row states what it
DECLINES, so a row that forgets declines nothing.** Frank's three
concerns are the acceptance criteria: (V) visibility into decisions, (R)
every row reachable, (S) sound logic.

## 1. The mechanism: four parts, one table type

### 1.1 Field vocabulary: `fields.def` (one definition per field)

A table's inputs are named once, in an X-macro:
`MF_FIELD(name, default_test, doc)`. `default_test` is ONE predicate,
"this field is at its contract default". For example, `miss` is at
default iff NULL; `floor` iff NULL or `"0"`; `denies` iff 0. The
predicate is written from the contract text (memfn.h + integration.md
§14/§15), and the 13 disagreements are settled HERE, one row per field,
by ruling (§5, Q-ROW-1). `mf_nondefault(site, hooks)` computes the
site's NON-DEFAULT MASK from the table. It is the only place a field's
default is spelled.

### 1.2 Row contract: an ALLOWLIST of honoured fields

Every row declares `honours`, the mask of fields whose non-default values
its action handles correctly. **The shared gate admits a row only if
`nondefault ⊆ honours`.** That check runs BEFORE the row's own
predicate, which keeps its current shape-specific job (term kinds,
counts, plan hints).

Consequences:
- **A field added to the contract later is declined by EVERY row** until
  someone writes that the row honours it. Forgetting fails toward the
  generic row, or a loud refusal, never toward a wrong answer. This is
  the allowlist-not-denylist rule `mk_d27_cell.sh` already uses for the
  same reason.
- **The last row (generic) must honour ALL fields.** A build-time check
  (`_Static_assert` or a startup assert over the table) makes it true by
  construction. Where generic honestly cannot honour a value, that value
  is a CONTRACT refusal, written in `fields.def` as `refuse_test`. It is
  not a silent decline.
- **The define and use checks are the same gate.** It runs on the define
  hooks AND on the use hooks. A use whose non-default mask differs from
  its define's is refused. That is K96's use-side check, made general,
  and it covers S8 (generic's floor mismatch).

### 1.3 Decision record: why this row (V)

`mf_select(table, ctx, rec)` walks the rows and, when `rec` is non-NULL,
fills a fixed-size record:
- the table id;
- per row evaluated: `{row id, verdict}`, where the verdict is one of
  DENIED (opts/deny bit), GATED (with the FIRST failing field's id),
  PRED_FALSE or CHOSEN;
- the site's non-default mask.

The record is plain data. `mf_explain(rec, sink)` prints one line per
row. **The record shape is the migration target for pcrec's
PCREC_CAND_TRACE records** (Frank: decisions move into memfn later; C1's
slot/route/row/site key maps onto table id + context + verdict + caller
site key). Nothing pcrec-side changes now (§4).

### 1.4 Reach: every row is witnessed (R)

The kit keeps per-table per-row hit counters, keyed by verdict CHOSEN,
in the `mf_art`, and exposes them through an accessor. Three consumers:
1. **G2** reports per-row CHOSEN counts and FAILS if a row has 0. That is
   the K35 floor. Lane g2x's shape families are its population; they are
   written blind, which makes it the independent half.
2. **The corpus census** tells which rows ANY pcrec pattern reaches. For
   each row it commits ONE witness pattern as an `.rxt` cell, and the
   check compiles it and asserts the record names the row. A row that no
   pattern can reach is DECLARED (for example, generic is unreached from
   pcrec today) together with a reason, and its witness is a G2 site or
   a C5 fixture instead.
3. **The independent control** is a literal floor in `docs/spec/`: the
   count of rows per table and of witnessed rows. It shares no source
   with the table (memfn/CLAUDE.md's floor convention).

### 1.5 One table type

```c
typedef struct mf_row {
    const char *name;           /* listing/stamp/explain name            */
    uint64_t    deny;           /* MF_D_* bit and/or options.def row     */
    uint64_t    honours;        /* fields.def mask (§1.2)                */
    int       (*applies)(const void *ctx);  /* shape predicate          */
    const char *doc;
} mf_row;
const mf_row *mf_select(const mf_table *t, uint64_t nondefault,
                        uint64_t denies, const void *ctx, mf_decision *rec);
```

This is pcrec's `DfaCand {name, deny, applies}` (emit_dfa.c:3391) plus
`honours` and `doc`. runcmp's `rc_row` already has this shape. The
composer's `arm` struct (kit.h:96) moves onto it and gains a name, deny,
doc and an accessor. That also fixes the audit's visibility gap: the four
composer arms appear in no listing, and `select_arm` never reads `opts`,
so the first byte-moving row's `--memfn=no-NAME` would deny nothing.
**The 12 untabled form branches inside rows** (audit §1.3; e.g.
precheck's gate/run/set-rest, ofsskip's pair/single) become sub-tables
of the same type wherever they choose between forms. A branch that only
spells one form stays code (D152's test).

## 2. Where it lives: generality across the boundary (Frank's point)

Frank asked for a mechanism pcrec's other tables can use too, partially
generalized if need be, not a kit one-off. The facts (audit7):
- pcrec has about 13 first-match tables, all predicate-function rows with
  a `uint64` deny;
- START-TABLE (start_table.md rev 2.1) is folding about 37 start rows into
  one pcrec-internal `CandRow`/`cand_select` at C2-C7, and plans a hit
  counter (§3.4) that is not built yet;
- libpcrec already links the kit, and pcrec already CALLS kit accessors
  (`mf_options`, `mf_run_rows`) through memfn.h;
- the kit links nothing from pcrec and stays extractable (MF_NS, 0BSD,
  C15/C16).

**Decision (proposed): the mechanism is a kit export.** That means
`mf_row`/`mf_table`/`mf_select`/`mf_decision`/`mf_explain` plus the hit
counters, in a new kit file `memfn/src/table.c` with a header section in
memfn.h.
- It is generic: it knows nothing about search sites. `fields.def` is
  the KIT'S vocabulary, and another table passes its own field table, or
  none. Then `honours` = ALL and the gate is a no-op, the "partially
  generalized" fallback.
- pcrec may adopt it table by table through memfn.h, which is the same
  crossing as `mf_options` and needs no new boundary.
- It is the natural home for decisions that move into the kit (M5).

**What is NOT proposed now (D153 remodel-first, D77):** migrating pcrec's
tables. START-TABLE C2-C7 owns the start rows and is mid-flight.
`CandRow`'s fields are a superset of `mf_row`'s (it adds slot, route and
hands/accepts), so the path is that after C7, `cand_select` becomes a
thin wrapper over `mf_select` with CandRow embedding an `mf_row`. pcrec's
side then decides that, as a separate [START-TABLE]/[DEC-FALLBACK]
follow-up, and gets the record, counters and explain for free. ROWCON
ships the mechanism with the KIT's tables as its first users. Nothing in
pcrec moves.

Rejected alternatives:
- **A header-only idiom copied into both trees.** Two spellings drift,
  which is exactly D152's complaint and the reason DfaCand and rc_row are
  already independent copies.
- **A pcrec-internal mechanism the kit cannot use.** That breaks the
  boundary, and decisions moving INTO the kit would have to be rewritten.

## 3. Soundness argument (S)

1. **Gate.** For any site, a chosen row R satisfies `nondefault ⊆
   R.honours` and `R.applies(ctx)`. The row's own correctness argument
   need only cover (a) the fields it honours and (b) the shapes its
   predicate admits. Every other field is at its default, by
   construction.
2. **Totality.** Generic honours ALL fields (asserted), and its predicate
   is `always`. So for every site either a row is chosen, or a
   `refuse_test` in `fields.def` refuses loudly. There is no silent
   third outcome.
3. **One default.** Each field's default is one predicate (`fields.def`)
   read by the gate and by every row, so rows cannot disagree on what
   "unstated" means. That settles the 13 disagreements.
4. **Define/use agreement.** The same gate runs on both hook sets, and a
   mismatch refuses.
5. **What the gate cannot see.** A row may still be wrong on a field it
   CLAIMS to honour (S2-S7's parenthesization is that: generic does it,
   the pre-check arm claims the field but doesn't). That is caught only
   by tests. So (R) is part of the soundness argument: G2's per-row floor
   puts every honoured field in front of the independent reference. The
   fix for S2-S7 is in the row's text (parenthesize like generic), and
   G2 gains a hook-style axis per honoured field.
6. **Order.** Overlapping predicates make order significant (D152's
   cost). Each table states its order rationale in a comment per row,
   and the explain output shows the order at every decision.

## 4. Plan (zero-mover throughout; each step its own commit, gate vs main)

| step | content | pcrec bytes |
|---|---|---|
| T0 | `fields.def` with the Q-ROW-1 rulings; `mf_row`/`mf_table`/`mf_select`/`mf_decision`/`mf_explain`/counters; `table.c`; unit tests | none (unused) |
| T1 | runcmp's `rc_row` onto `mf_row` (honours declared); `mf_run_rows` projects it | none (listing byte-identical) |
| T2 | the composer's `arm` onto `mf_row`: names, denies (opts now READ), honours from the audit matrix. ofsskip/precheck/runcmp declare exactly what they honour; generic is ALL (asserted) | none: pcrec states no non-default field these rows don't honour (proved by the gate vs main) |
| T3 | fix S1-S8 in row text (precheck honours `miss`, parenthesization in pre-check/runcmp, braced `on_miss`) OR drop the field from `honours`, per cell, recorded | none (cells unreachable from pcrec; gate) |
| T4 | the untabled sub-choices become sub-tables where they choose between forms | none |
| T5 | reach: G2 per-row floor (with g2x's families); the corpus witness census (one `.rxt` per row reached from pcrec; declared unreachables); the `docs/spec/` literal floors | none |
| T6 | visibility in pcrec, OPTIONAL and migrating: under `PCREC_CAND_TRACE` only (C1's convention, so the default build is byte-identical), pcrec passes `res`/`rec` and prints `mf_explain` per site. This is an R-6 request only if T5's corpus census needs it, and it is marked "migrates at M5" | none (trace build only) |

Every step: `make strict`, G2, `test-memfn-*`, and the emit_sweep gate
vs main (0 movers, all streams). A row deny added in T2 is the row's
`--memfn=no-NAME`, but since no byte moves its alpha is N/A. It is a
listing change only, so the `--list-axes` memfn section floor goes up in
`docs/spec/` (D80).

## 5. Open questions (for Frank, via the panel)

- **Q-ROW-1, the field defaults.** The 13 disagreements need one ruling
  each in `fields.def`. Recommendation: the default is the contract's
  stated default where it has one (`floor` NULL ≡ `"0"`). `miss` NULL ≡
  "the function's `n`" for FUNC/RETURN and a REFUSAL elsewhere (the
  contract gives no default value). The kit lane drafts the full list
  from audit §3, and the panel checks it against the contract text.
- **Q-ROW-2, T6.** Is pcrec-side visibility needed now (the corpus census
  needs SOME channel to learn which row a pattern reached), or can T5's
  census run through a kit-only route? Recommendation: T6 under the trace
  build only, marked migrating. It is the least code that answers "which
  row did this pattern take", and C1 already built the convention.
- **Q-ROW-3, generality.** Is "kit exports the mechanism; pcrec adopts it
  per table after its remodel" the right partial generalization, or
  should ROWCON also migrate one pcrec table now as a proof?
  Recommendation: not now (D153). Offer it to [START-TABLE] after C7.
