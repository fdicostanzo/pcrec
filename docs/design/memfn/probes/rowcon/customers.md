# Reference customers of a generic first-match row engine: facts only

Read-only survey, 2026-10-07. Paths are relative to the repo root. "main" is the
checkout at /Users/fdicostanzo/pcrec (HEAD 31bf6d00); "stc2" is branch `lane/stc2`
(read via `git show`). Line numbers are from those trees, not from a rebuilt tree.

---------------------------------------------------------------------------
## 1. [START-TABLE] C2: `cand_rows[]` (branch lane/stc2)

Sources: `docs/dev/lanes/stc2_report.md` (stc2), `docs/design/start_table.md`
rev 2.1 §1-§3 (main, 1851 lines), `src/gen/emit_dfa.c` and `src/core/internal.h`
on stc2. No reader is switched yet (`cand_select`, `cand_route_of`, `cand_nodes[]`
carry `__attribute__((unused))` until C3); the table is exercised only by the
trace-build both-walks oracle.

### 1.1 Exact types (stc2)

`src/core/internal.h:7020` (route), `:7022-7032` (slots), `:7041-7047` (VM facts):

    typedef enum { CAND_ROUTE_DFA = 0, CAND_ROUTE_VM, CAND_ROUTE_ATTEMPT } CandRoute;

    typedef enum {
        CAND_SLOT_WINDOW,   /* can a match begin before n - W? (entry, once) */
        CAND_SLOT_PRESENCE, /* does the window hold every necessary landmark? */
        CAND_SLOT_WIDTH,    /* can the rest of the subject hold a match at all? */
        CAND_SLOT_FIRST,    /* where does the first scan begin? */
        CAND_SLOT_NEXT,     /* how is the next candidate start found? */
        CAND_SLOT_RETRY,    /* after a failed VM attempt: step or re-seed? */
        CAND_SLOT_BOUND,    /* how many start positions can match at all? */
        CAND_SLOT_RECOVER,  /* given a match END, where does it start? */
        CAND_NSLOTS
    } CandSlot;

    typedef struct CandVmFacts {          /* filled by the VM emitter only; else NULL */
        long long root_minw; bool mrl_win; long long nclamp;
        bool has_push; unsigned reseed_gap;
    } CandVmFacts;

`src/gen/emit_dfa.c:3398-3429` (per-call context; `DfaSel` was renamed, `typedef
CandSel DfaSel` at `:3432` keeps all old spellings):

    typedef struct CandSel {
        Ctx *cx; const Dfa *d; const void *us; bool forward;
        int st;                  /* per-state axes only, else -1 */
        int route;               /* CandRoute; every initializer names it */
        const StartSet *ss;      /* start_set fact or NULL */
        const CandVmFacts *vm;   /* VM-route rows' inputs or NULL */
    } CandSel;

`src/gen/emit_dfa.c:3391-3395` (common head, also main):

    typedef struct DfaCand { const char *name; uint64_t deny; bool (*applies)(const DfaSel *s); } DfaCand;

`src/gen/emit_dfa.c:7791-7826` (handoff types, mapping, give-up posture, nodes):

    enum { CT_LOWER=1<<0, CT_UPPER=1<<1, CT_CAND=1<<2, CT_WINDOW=1<<3,
           CT_VERDICT=1<<4, CT_HIT=1<<5, CT_START=1<<6 };
    enum { CM_NONE=0, CM_EXACT0, CM_EXACTK, CM_EXACTPRED, CM_WINDOWLO, CM_WINDOWHI,
           CM_LOWERBOUND, CM_PRESENCE, CM_ONE, CM_RECOVER, CM_STEP, CM_RESEED, CM_ADAPT };
    enum { CG_NEUTRAL=0, CG_ONE_WAY, CG_FIXED };
    enum { CAND_NODE_VERIFIER = CAND_NSLOTS, CAND_NODE_LOOP, CAND_NODE_CALLER, CAND_NNODES };
    #define CAND_ON(r) (1u << (r))        /* emit_dfa.c:3438 */
    #define CN(n)      (1u << (n))
    #define CAND_ALL_ROUTES (CAND_ON(DFA) | CAND_ON(ATTEMPT) | CAND_ON(VM))

`:7831-7836` (one per slot plus the 3 non-slot successors; table `cand_nodes[CAND_NNODES]` at `:7843-7867`):

    typedef struct CandNode {
        const char *name;    /* a slot's trace `slot` field */
        unsigned accepts;    /* CT_* it takes from a predecessor */
        unsigned asks;       /* CAND_ON(route) for each route a body asks it on */
        unsigned succ;       /* CN(node) for each node its rows hand to */
    } CandNode;

`:7873-7898`:

    typedef struct CandList { const char *axis; int order; const char *name; } CandList;
    typedef struct CandRow {
        DfaCand       c;          /* identity (unique), deny bits, predicate */
        CandSlot      slot;
        unsigned      routes;     /* CAND_ON(route) mask, written on every row */
        const char   *tok;        /* today's spelling (trace/stamp/old table) */
        unsigned char map;        /* CM_*  (data only; no emitter branches on it) */
        unsigned char giveup;     /* CG_*  (data only) */
        unsigned      hands;      /* CT_* handed to the slot's successors */
        CandList      list[3];    /* indexed by CandRoute: --list-axes projection */
        const void   *was;        /* oracle-only link to the old-table row, by pointer; NULL for inline decisions; deleted C3-C5 */
    } CandRow;

Table: `static const CandRow cand_rows[]` at `:7958-8121`, 37 rows, contiguous block per
slot in `CandSlot` order; `CAND_NROWS` at `:8122`.

### 1.2 The walk

`:8131-8141`: ONE array walked linearly; a row is eligible iff
`row->slot == slot`, `!(c.deny & flags)`, `routes & CAND_ON(s->route)`, then
`c.applies(s)`. First eligible wins. Order of tests: slot, deny, route, predicate.

    const CandRow *cand_select(CandSlot slot, const DfaSel *s, uint64_t flags)

The design note (`start_table.md` §1.3) wrote a 4-arg form with `route` separate;
stc2 dropped it because the route would be carried twice (`s->route`; report §4
item 4). Route is therefore a field of the per-call context, not a parameter.
`cand_route_of(Ctx *)` (`:8149`) is the ONE route derivation: `job->engine ==
PCREC_ENG_ATTEMPT ? CAND_ROUTE_ATTEMPT : CAND_ROUTE_DFA`. Never `fit.chosen`. (VM
route is chosen explicitly by the VM emitter. The route class also cannot express
HYBRID vs VM-ONLY or EMPTY; those distinctions stay inside predicates, design §2.3.)

### 1.3 Columns the three requested

The report/design use `accepts`, "asked routes", "successors" as columns of the
NODE table, not of rows:
- accepts = `cand_nodes[slot].accepts` (bit set of CT_*).
- asked-routes = `cand_nodes[slot].asks` (the route-class table, design §2.3).
- successors (hands edges) = `cand_nodes[slot].succ` (a CN() set over slots plus
  VERIFIER/LOOP/CALLER); a row carries `hands` (set of CT_* types) and the
  structural check requires `row.hands` ⊆ union of `accepts` of the slot's successors
  (not per-edge; report §4 item 2: P1-P3 hand no HIT to FIRST).
- `list[route]` is a per-row, per-route `--list-axes` projection `{axis, order, name}`;
  routeless axes (WINDOW, PRESENCE, FIRST) sit on `list[CAND_ROUTE_DFA]` ("the first
  route the slot is asked on", report §4 item 8). N12, H1/H2, B1/B2 have no listing.
  B5 `all` is listed on the VM route only, as "unanchored" order 3.

### 1.4 Applicability, deny, totality

- Applicability: `c.applies(const DfaSel *)`. Row predicates are the old tables'
  functions BY POINTER (`pf_*_applies`, `req_*_applies`, `start_pinned_applies`),
  plus nine NEW predicates for formerly inline decisions (`:7902-7947`): W1, H1, N12,
  R1-R4, B1-B4 (`cand_window_applies`, `cand_ceiling_applies`,
  `cand_pred_memchr_applies` [calls `attempt_cand`], `cand_rs_*`, `cand_bound_*`).
  Predicates may read other slots only by calling their walk (P3 reads NEXT, F1 reads
  PRESENCE, R4 reads NEXT's scanned set); predicates may `pcrec_ctx_fail` (longjmp);
  predicates have first-ask side effects (`pcrec_find_byte_rate` records its first ask;
  the facts layer's `used` column).
- Deny: `c.deny` uint64 bitmask tested `deny & flags` (flags = `cx->opt->flags`,
  or 0 at N12's site, which has no Ctx). Multi-bit rows exist (N1/N2: `16|32`); either
  bit removes the row. Bits used: 16, 32, 37 (PCREC_NO_HYB_RESEED), 22, 45, 46, 47.
  FACT denies (28 start_anchor, 29 end_window, 30/31/44 req_*) stay on facts, not rows;
  the listing shows bit 28 on the `vm-anchor-bound` rows as a projection (design §3.7).
- Totality: every (slot, asked-route) must end in an undeniable `cand_always` row.
  NULL return is "unreachable"; the walk returns NULL and the callers deref (crash).
  Checked, in the trace build only, by `cand_rows_selfcheck` (`:8199-8240`): slot
  contiguity, route within `asks`, `hands` accepted, unique identities, unique
  (axis,order) listings per route, and totality: for each asked (slot, route) the LAST
  routed row has `applies == cand_always && deny == 0` (`table-not-total`).

### 1.5 Multi-slot, routes, successors, payload

- Eight slots in one array (Q2 ruling: one array with a `slot` field, never per-slot
  arrays). Multi-valued per-row outputs carried today: `routes`, `map`, `giveup`,
  `hands`, `list[3]`, `tok`. The slot PAYLOAD `u` (typed union: `u.pf` = DfaPf emit
  hooks/`reseeds`/`run_term`/`scan_set`/`emit_vm`; `u.admit` = ReqAdmit verdict plus
  route-keyed `noscan`; `u.use`; `u.reseed` = action/start/armed; `u.bound` = none/0/
  `search_from` plus the emitted bound string; `u.recover.pinned`) is NOT in C2. It is
  designed (`start_table.md` §1.1 last row) and arrives piecemeal in C3-C5 as each
  old table is deleted. Also designed but absent: `landmark`, `scan`, `hat`, `stamp`,
  `desc`. So at the end state a row carries typed per-slot data of widely different shape
  (function pointers for emitters, enums, strings, a boolean property, a calibration index).
- Route filter: a row's `routes` bitmask over 3 routes; mask 0 means DFA-only on the
  legacy tables. Rows can serve several routes (`window`: all 3; `reverse-pass`: DFA+ATTEMPT;
  `all` BOUND: ATTEMPT+VM). The same slot is asked on different routes by the same artifact
  (BOUND on ATTEMPT and VM for an ATTEMPT hybrid; NEXT on DFA and VM for the VM_START_SCAN
  stamp).
- Successor chains: `hands`/`accepts`/`succ` form a typed handoff graph E1-E12 with 3
  non-slot nodes and re-entry cycles (E5 inside scan, E7 RETRY->NEXT, E8, E10 find-all).
  Termination (PROGRESS) obligations of re-entering edges are argued in the row's review,
  not checked. Data only for checks and listing; no emitter branches on it.
- Slot-DAG of selection reads (design §1.3): BOUND reads nothing; NEXT reads BOUND;
  PRESENCE reads NEXT and BOUND; FIRST reads PRESENCE; RETRY reads NEXT and BOUND.
  C5b replaces four restatements of BOUND with BOUND reads.
- Identity: `c.name` unique across the array; 8 rows share a spelling in the old code
  (`none` x4, `anchored` x2, `gstart` x2), hence the `tok` column. N12 stamps "memchr"
  but is its own identity `pred-memchr` (so its STAMP projection must be a separate `stamp`
  column, report §4 item 1; P4 `set-leads` also projects `emitted`).
- Inline decisions as rows: seven (W1, H1, B1-B4, plus N12/R1-R4) whose old form was
  if/else; row order within the slot is the chain's order.

### 1.6 Visibility, reach, oracle

- Stamps NOT yet read from the table. Old stamps it must reproduce: `REQ_WHY`,
  `REQ_HANDOFF`, `DFA_PREFILTER`, `VM_START_SCAN`, `DFA_START`, `VM_RESEED`, `VM_START`,
  `END_WINDOW`, `VM_ROOT_MINW`. Closed token sets (D81); some value sets differ from row
  names (P4 -> `emitted`; B5 -> `unanchored`; N12 -> `memchr`; F1's stamp is the decimal K).
- Listing: C6 makes `axes_dump.c` project `list[route]`; C7 is a declared listing-only
  change; the listing's `desc` is a hand table today (`AXIS_DESC`, drifted, design D-3).
- Trace (see §6) and the both-walks oracle (trace build only): at 13 old decision sites
  plus a 14th for the route (`cand_route_of` vs the body dispatch). Runs in both orders
  (old-first default; `-DPCREC_CAND_NEW_FIRST` asks `cand_select` first, so a predicate's
  first-ask side effect lands on the new walk). Compares by POINTER to the old row (`was`)
  and by `tok`. Runs `cand_select_quiet` under a thread-local quiet depth
  (`pcrec_cand_trace_quiet`) so predicates that themselves walk print no extra record.
  Because walked rows share predicates by pointer with the old rows, the oracle tests only
  the FILTER (slot/route/deny order/first-match); for inline decisions it also tests the
  predicate. It `abort()`s with a `CANDORACLE` line.
- Reach counting: each checked decision prints `CANDROW <slot> <route> <identity> <site>`
  to stderr (hit counter, design §3.4). 42-line witness file
  `tests/codegen/cand_oracle_witnesses.tsv` + `run_cand_oracle.sh` (every row identity +
  deny landings); coverage K35-checked against the table's own source; rows with zero hits
  across the corpus are "UNPROVEN-BY-SWEEP" and need a witness. The `CANDROW` counts are
  cross-checked against the default artifact's stamps (`xcheck.py`: 31 relations).
- Failing-direction controls: mech rows S594-S599 (planted predicate difference,
  route mis-key, dropped deny bit, wrong inline restatement, non-total fallback,
  wrong handoff type).

### 1.7 Anything unusual a generic engine must host (customer 1)

1. ONE array, EIGHT slots (a slot is a key, rows are filtered by it, not separate arrays).
2. A second key `route` (3 values, bitmask per row; rows serving several routes; mask 0
   legacy default) passed inside the context, filter tested BEFORE `applies`.
3. Same (slot) asked on several routes in one artifact; the same row identity serving
   different route listings (`list[route]`).
4. Inline if/else chains converted to rows (predicate-per-branch), fallback rows
   undeniable; denies as bits only, no force bits on start rows (D148 Q3: deny only).
5. Per-slot heterogeneous payload (emitter hooks, enums, strings, boolean property),
   typed union planned; plus cross-slot selection reads (predicates call other slots'
   walks; the dependency DAG must be acyclic).
6. Typed handoff graph with `accepts`/`hands`/`succ` sets, re-entry edges and a
   structural check over the set relation (not per edge).
7. Several stamps/listing names per row that are PROJECTIONS (not the identity);
   unique-identity vs repeated spelling.
8. Predicate may longjmp (`pcrec_ctx_fail`) and has memoizing side effects, so
   evaluation SET and (diagnostic) ORDER matter; no eager "resolve all slots" plan allowed.
9. Per-call context type `CandSel` carries optional pointers that some routes lack (NULL
   `d`/`us` on VM; NULL `vm` outside the VM emitter); a route mask is what keeps predicates
   from dereferencing the missing one.
10. A deny at N12's site is 0 because that site has no Ctx.
11. A trace/oracle that must run old and new walks in both orders.

---------------------------------------------------------------------------
## 2. `dfa_pfs[]` / `DFA_SELECT` / `dfa_select` / `DfaCand` (main, `src/gen/emit_dfa.c`)

### 2.1 Types

- `DfaCand` `:3391-3395`: `{ const char *name; uint64_t deny; bool (*applies)(const DfaSel *); }`
  The comment: name is "the stamp value, where this axis has a stamp"; deny: "a set bit
  in cx->opt->flags REMOVES this entry".
- `DfaSel` `:3352-3380`: `{ Ctx *cx; const Dfa *d; const void *us; bool forward; int st;
  int route; const StartSet *ss; }`. "A VALUE and not the Ctx because selection happens
  twice per artifact from the body path and twice more from the stamp path, and the two
  must not be able to answer differently" (comment at `:3394`). `st` is -1 except for the
  per-state scan-edge axes. `route` is 0 (DFA) or 1 (VM) on main (ATTEMPT only on stc2).
  Every initializer is designated; `tests/codegen/run_cand_rows.sh` [cand-route-init]
  fails on one omitting `.route`.
- Every row struct begins with `DfaCand c` ("common initial member", so the address of
  the i-th row is a `DfaCand *` without punning). Ten lists use this:
  `dfa_reprs` `:5433` (axis A), `dfa_views` `:5552` (C), `dfa_seeds` `:5629` (D),
  `dfa_accs` `:5719` (E), `dfa_pfs` `:6623` (B), `req_admits` `:7013`, `req_uses`
  `:7130`, `dfa_matches` `:7448` (G), `dfa_search_starts` `:7664` (J), `dfa_edges` `:7840`
  (H). The two direction objects (axis F) are `DfaCand`-headed but NOT a list (both emitted).
- `DfaPf` `:4831-4909`: `c`; `emit_tables`, `emit_block`, `emit` hooks (and `emit_vm`
  for the VM hat; `OfsTest ofs` etc.); `reseeds`, `run_term` booleans; `PfScan scan`
  (`PF_SCAN_NONE/OFS/BYTE/SET`, replaces strcmp on names; the structural check forbids
  strcmp on a row name); `unsigned routes` (CAND_ON mask; 0 = DFA-only);
  `bool (*scan_set)(const DfaSel *, CandSet *out)` (the row's predicate core, the SET it
  scans). So a DfaPf row carries emitters, flags, a scan-kind enum, a route mask, and a
  second function that must agree with `applies`.
- `ReqAdmitRow` `:7008` = `{ DfaCand c; ReqAdmit verdict; const char *desc; }`.
  `ReqUseRow` `:7125` = `{ DfaCand c; ReqUse use; const char *desc; }`.
  `DfaMatch` `:7436`, `DfaSearchStart` `:7583`, `DfaEdge` `:7829`: bare `DfaCand c`.
- `dfa_pfs[]` has 12 rows (N1-N11 + `none`): `run-pinned-bounded` (deny `PCREC_NO_OFFSET_SKIP |
  PCREC_NO_RUN_PREFILTER`), `run-pinned`, `offset-set-bounded`, `offset-set`
  (`NO_OFFSET_SKIP`), `first-memchr-bounded`, `first-class-bounded`, `first-class` (VM route
  only; `NO_START_SET`), `memchr-bounded`, `memchr`, `byte-class-bounded`, `byte-class`,
  `none` (`cand_always`, routes DFA|VM).

### 2.2 The walk

`dfa_select` `:5089-5100`:

    static const void *dfa_select(const void *list, size_t n, size_t sz,
                                  size_t routes_at, const DfaSel *s, uint64_t flags)
    for i in 0..n: if (cand->deny & flags) continue;
                   if (!cand_routed(row, routes_at, s->route)) continue;
                   if (cand->applies(s)) return row;
    return NULL;

Macros `:5101-5108`: `DFA_SELECT(T, list, sel, flags)` (list has no `routes` field, all rows
DFA-only: `routes_at = CAND_UNROUTED`) and `DFA_SELECT_ROUTED(T, list, sel, flags)` (reads
`offsetof(T, routes)`; `cand_routed` `:5073` memcpy's the mask; 0 -> DFA-only). The walk is
`void*`-typed and stride-based; the macro supplies the element type back. Order of tests:
deny, route, applies. First match; no argmin; no scoring.

### 2.3 Totality, fallback policy

`cand_always` `:5113`. Comment `:5084-5088`, `:5110-5112`: NULL is "UNREACHABLE and
deliberately not defended against: every list's last entry's applies returns true
unconditionally ... A missing fallback would crash here rather than emit a machine with a
hole in it." Callers deref the return directly (`pf->c.name`, `r->verdict`, `ss->c.name`).
No static check on main ties the last row to `cand_always`; stc2's trace-build selfcheck
does that for the unified table only. (Some lists' last row is `cand_always`, e.g. `dfa_pfs`
`none`, `req_admits` `emitted`, `req_uses` `scan-from-startpos`, `dfa_search_starts`
`reverse-pass`, `dfa_reprs` `indexed`.) A single list has a SINGLE shared fallback across
routes (`none` serves DFA|VM), so totality per route is by that one row.

### 2.4 Deny handling

Pure bit mask `deny & flags`; "Nothing branches on the flag": a denied row is removed and the
ordinary walk selects the fallback (D82's shape). Multi-bit rows exist. Deny bits are
`lib/pcrec.h` macros listed in `src/core/axes.def`. The `-fno-start-pinned` comment at
`:7660`: "the flag REMOVES the object". Not every row has a deny (the four offset-0 forms
and the fallbacks carry 0; the dump says they have no CLI spelling).

### 2.5 Selection call sites (per-call contexts built at each)

Each list has a thin selector building a `DfaSel` (designated init) and calling the macro:
`dfa_pf_of` `:6663` (also trace site `pf-of`), `vm_start_row` `:6693` (route VM, d=NULL,
us=NULL), `pf_scan_set_of` `:6677`, `pcrec_dfa_scan_state_written`, `dfa_form_derive`
`:8142` (axes A-E), `req_admit` `:7035`, `req_use` `:7146`, `dfa_search_start_of` `:7672`,
`dfa_repr_of` `:5444`, plus `dfa_match_of` and the edge selectors. The same selection is
called from the body path and from the stamp path; correctness depends on them calling the
same selector (so stamps are derived by re-running the selection with the same inputs).

### 2.6 Stamps (`*_WHY` and friends)

All stamps are `pcrec_sb_stamp_str(c, upper, "NAME", value)` where value is the selected
row's `c.name` (identity == stamp value) except where a name function maps it:
`DFA_PREFILTER` (`dfa_prefilter_name`, `:10296`), `DFA_TABLE` (`dfa_table_name`, `:10308`,
which also yields `none`/`mixed` composite values not names of any single row),
`DFA_START` (`dfa_search_start_name`, `:10330`), `DFA_MATCH`, `DFA_SCAN_EDGE`,
`VM_START_SCAN` (`pcrec_vm_start_scan_name`, `:9993`, the VM-route NEXT row's name),
`REQ_WHY` (`req_why_name(admit)`, `:9977`; CLOSED four-token set `none`/`one-attempt`/
`dominated`/`emitted`, and `set-leads` maps to `emitted`, so verdict -> token is many-to-one),
`REQ_HANDOFF` (`req_handoff_stamp`, `:9986`: decimal K or `none`),
`VM_RESEED` (emit_vm.c `:11384`: `rs->row->name`). Stamps are unconditional on every
artifact of the engine family (Frank Q3, K82: "a stamp varies by engine family, never by
presence within one, and 'does not apply' is a value").

### 2.7 AXIS_LIST exposure

`pcrec_dfa_axis_cands` `:7711-7724` walks any `DfaCand`-headed array by stride and fills
`PcrecAxisCand { const char *name; uint64_t deny; const char *stamp; }`
(`src/core/internal.h:6573-6580`); `applies` is DELIBERATELY NOT CALLED ("a fabricated Sel
could silently answer a different question than a real compile does"). `AXIS_LIST(list)`
macro `:7726` instantiates it; one public accessor per list (`pcrec_dfa_axis_table_cands` ...
`pcrec_dfa_axis_searchstart_cands`, `:7731-7761`); `#undef AXIS_LIST` after. Prefilter's
accessor patches `stamp = "RX_VM_START_SCAN"` on a VM-route-only row (`:7739`).
`axes_dump.c` `emit_dfa_list_axis` (`:322-344`) takes `get`, caps at 16 candidates, prints
one TSV row per candidate (`order = i+1`, kind `list`), and takes the `applies` prose from
`AXIS_DESC[]` hand table (`axes_dump.c:100-147`) keyed `(axis, candidate)`; an unmatched row
gets a placeholder rather than being dropped. `req_admits`/`req_uses` instead expose
`pcrec_req_admit_row(i, &desc)` / `pcrec_req_use_row` (name, deny, why/stamp, desc) and the
dump walks them as `predicate`-kind rows (the `desc` field lives beside the row).
`pcrec_reseed_rows[]` is walked the same way via its own struct.

### 2.8 Reach counting / visibility on main

None on main apart from the C1 trace (§6). No hit counters in the default build.

### 2.9 Unusual things for a generic engine (customer 2)

- Type-erased row stride: the same walk serves 10 differently sized row structs by `void*`
  base + stride + optional `routes` offset (not a template, not a vtable).
- `routes` is an OPTIONAL field of the row struct, located by `offsetof`.
- Deny and route filters before predicate; predicate gets a by-value-ish `DfaSel`.
- `DfaPf` rows carry emit hooks that the SAME selection chooses between at several call
  sites (one selection read by stamp, listing, `reseeds` query, density, G1 dominance...).
  A second function pointer (`scan_set`) restates the predicate core and must agree.
- Candidates with a stamp value different from name (`set-leads`->`emitted`; `first-class`
  stamps through another macro).
- Axes A-E are pure first-match lists; axis F is not a list; axis H (edges) selects PER
  STATE (`DfaSel.st`).
- Missing fallback is a crash by design, not an assertion.

---------------------------------------------------------------------------
## 3. Engine selection, `src/opt/select_engine.c` (main, 1117 lines)

Not one first-match table. It is four different structures in one pass,
`pcrec_select_engine` `:992-1117`:

### 3.1 `analyses[]` (rung "what forces an engine") `:405-430`, type `EngineAnalysis` `:68-95`

    typedef struct { const char *name;
                     unsigned (*forces)(Ctx *cx, const Ast *a, size_t *why_pos, const char **why);
                     bool node_derived; } EngineAnalysis;

Three rows: `captures` (`forces_captures` `:107`, request-derived), `registry`
(`forces_registry` `:330`, node-derived), `dfa_overflow` (`forces_dfa_overflow` `:388`,
retry state). The pass `:1026-1043` runs EVERY row (no early exit) and ANDs the returned
`ENGM_*` masks: `mask &= m`. Order matters ONLY for the diagnostic: `why`/`why_pos` are
taken from the FIRST row that excludes the DFA (`if (!(m & ENGM_DFA) && !why)`), and a second
`node_why` from the first excluder with `node_derived`. So it is a conjunction/reduction, not
first-match; row outputs are multi-valued: mask + why text + why position. `forces` may call
`pcrec_ctx_fail`. Applicability is built into each function (they take Ctx/AST, there is no
separate predicate vs data and no deny-bit field). Denies are not on the row: they enter
indirectly (`-fno-atomic-discharge`, `-fno-splice-calls`, `-fno-ctx-node`, the Poss arms...
leave a DFA-excluding construct in the tree, so the registry row fires). Totality: not
applicable (empty mask means internal error `:1045`). `node_derived` is a row column read
only by the `--engine=dfa` override branch (to choose the refusal wording). `dfa_overflow`
says its `node_derived` is `false` because the override can never see it fire.

### 3.2 The `--engine=` override `:1052-1100`

A `switch (cx->opt->engine)` over DFA / VM / AUTO: DFA is do-or-die (refuses if `!(mask &
ENGM_DFA)` with one of two messages chosen by `node_why`/`want_caps`), VM always allowed
(`why = "--engine=vm"` when none), auto picks DFA when allowed. Not a table; not deny-bit
driven (`--engine=` is a VALUE, listed in axes.def as "not a row").

### 3.3 `prefilter_decision` `:561-870` (static)

A long if-chain over facts (`pcrec_fact_kinds`: collapsible_rep, has_bref, has_call, has_var)
and flags (`PCREC_FORCE_PREFILTER`/`NO_PREFILTER`, collapse pair, `dfa_disabled`,
`collapse_reason`, nullability) writing `fit->prefilter`, `prefilter_collapsed`,
`prefilter_declined_nullable[_default]`. Conflicting forces are refused (`pcrec_ctx_fail`).
No table.

### 3.4 `esel_of` `:943-979` = the `ESEL_*` ladder (the `_ENGINE_SEL` stamp)

A nested ternary of 9 arms, FIRST MATCH in OUTCOME order, documented by a comment table
`:889-899` with columns `# | arm | fires on | against the arms below` and the relation word
`OUTRANKS` or `excludes` (disjoint, order free). Arms (in order): FORCED (`engine != AUTO`),
DECLINED_NULLABLE_DEFAULT, DECLINED_NULLABLE, SIZE_CAP_RETRY ((a)||(b) share one value),
SELECTED, COLLAPSED_PREFILTER, OVERFLOWED_DFA, OVERFLOWED_PREFILTER (last = otherwise).
Predicates are inline conjunctions over `cx` retry state and `fit` (`dfa_disabled`,
`collapse_reason`, `size_drop_rung`, `dfa_was_engine`). No deny bit on arms; no table.
The ESEL value set has ORDERED RANGES that consumers test (`>= ESEL_OVERFLOWED_DFA &&
<= ESEL_DECLINED_NULLABLE` = "fell back"; `ESEL_SIZE_CAP_RETRY` and
`ESEL_DECLINED_NULLABLE_DEFAULT` deliberately placed outside; internal.h `:2274-2386`).
Before the ternary, a premise ASSERT (`size_drop_rung != SDR_NONE && dfa_disabled` ->
`pcrec_ctx_fail` internal error `:959`): a documented arm-disjointness precondition. The
stamp is unconditional.

### 3.5 Adjacent and relevant, not in the file

`fit_rungs[]` (`src/core/compile.c:723`, type `FitRung` `:678`): a genuine first-match table
for the size drop ladder with `fit_select(const FitSel *)` `:750` (walk; deny test via
`fit_rung_denied`, then `fit_*_applies(FitSel*)` predicates, `fit_always` total fallback,
`fit_rung_of(act)` lookup by action `:741`). It is the survey's "already unified" row for
the fallback ladder and a structural sibling of `DfaCand`, with a different context type
(`FitSel`) and a payload (`FitAct`).

### 3.6 What is stamped / listed

- Stamps: `RX_ENGINE` (chosen), `RX_ENGINE_SEL` (the ESEL token; closed set, unconditional),
  `RX_ENGINE_WHY` (PROSE from the first-excluding analysis row, VM stamps only) via
  `pcrec_emit_engine_stamp` `emit_dfa.c:421` and the VM stamp block.
- Listing: `axes_dump.c` `emit_predicate_axes` (`:443-`) lists `engine` (2 rows: vm/dfa,
  with `--engine=` spellings) and `engine-route` (`kind=predicate`, one row per `ESEL_` value
  with `stamp_macro RX_ENGINE_SEL`, no deny/force column) as HAND-STATED `emit_pred_row`
  calls (the dump's header says "the VM/engine-selection axes have no candidate-list-as-data
  anywhere in the tree yet"; "37 of 52 listed axes are `predicate`"). `analyses[]`
  is not listed.
- No trace records or hit counters.

### 3.7 Unusual (customer 3)

Reduction (AND of masks) with side-channel outputs (why, why_pos, node_why) vs first-match;
two rows' `why` priority differs from the reduction; the only data column
(`node_derived`) is read at a downstream switch; stamp value ranges with ORDER semantics;
documented disjointness/outranks relations that are asserted only for one pair.

---------------------------------------------------------------------------
## 4. [POSS-CTX-TABLE]

### 4.1 plan.md row (main, `docs/dev/plan.md:1206`)

STATE:not-started, under [OPTLOOP] candidates per D137, FILED 2026-10-07 by lane possarms2
from the [ART-POSS-ARMS] D6 panel's B-FAM disposition; UNSCHEDULED. Text (condensed, all
shape claims):
- Problem: `src/opt/possessify.c` answers "what does node kind K contribute" in THREE
  per-`AKind` switches, `first_of` (`:175`), `gk_build` (`:563`), `pss_walk` (`:841`), plus the
  `pss_verdict` ladder (`:891`), the K93 `CallCtx` join (`cc_join`/`cc_widen`/`cc_top_visit`,
  `:817-`) and the atomic discharge's survey consumer (`pcrec_poss_survey`, callback `fn`).
  [ART-POSS-ARMS] adds a FOURTH fold (A1's continuation, `first_ctx`/`px_cont_first` in the
  prototype) and [POSS-CALL-COPY] / the `verbs` tripwire would add more.
- Proposed shape (the only specification): "ONE context record {follow, may_end, encl, left}
  (A1's P is `left`) and ONE per-kind rows table indexed by kind with a static count
  assertion, so -Wswitch's exhaustiveness alarm (mrl.c's rule) survives."
- NOT built ahead of the arms; ZERO-MOVER refactor, gated on per-pattern `possessify
  marked/total` over corpus+bench plus `scripts/emit_sweep.py` identity (0 movers).
  TRIGGER: the next per-kind possessify edit after [ART-POSS-ARMS] lands. Cost S-M / risk M
  (refutation history U1, U2, the lazy conjunct, K93). Remodel overlap: possessify.c only.

### 4.2 `decision_families_survey.md` §3.14 (line 521) = family 14

Restates the same; adds "No inconsistency found — D154 already made it one walk and one
verdict" and the memory pcrec-forest-for-trees ~3-member threshold. `poss_arms.md` §7 item 3
(`:734-751`) is the original record. NO column list, no row list, no per-kind enumeration,
no signatures. So a precise mapping must be read off the code:

### 4.3 What the code shows (to make the mapping possible; the table itself is unspecified)

- Keyed by `AKind` (the AST node kind enum), NOT by a predicate: it is a dispatch (`switch
  (a->k)`), not first-match. Totality is the exhaustive-switch property (`-Wswitch`, mrl.c's
  rule), which the plan wants preserved with a static count assertion.
- Three folds with different signatures:
  `First first_of(Ctx *, const Ast *)` (returns a 256-bit set + `nullable`; widens to ALL
  BYTES for unmodellable kinds: wide class, backref; `A_WCLASS` is "loud",
  `pcrec_wcls_misplaced`);
  `GkParts gk_build(Gk *g, const Ast *a)` (Glushkov: interns positions into `g`, returns FIRST/LAST
  position sets; `g->ok` false ends the whole construction);
  `void pss_walk(Pss *P, Ast *a, const uint8_t *follow, bool may_end, const uint8_t *encl)`
  (mutates `Ast.u.rep.possessive` or reports through `P->fn`; recurses with per-child
  `follow`).
- The context record the plan names `{follow, may_end, encl, left}` is `pss_walk`'s three
  parameters (`follow[32]`, `may_end`, `encl[32]`) plus a new `left`; `CallCtx` (`:810-817`)
  has exactly `{follow[32], encl[32], may_end}` and the arena's zero is the join's identity.
- Context-INPUT/output asymmetry: `first_of` and `gk_build` take only a node; `pss_walk`
  takes context and mutates; the call-site fixpoint (`Pss.cc`, `cc_join`, `cc_grew`)
  re-walks until stable. `Pss.collect` runs a context-only walk. The state `Pss` holds
  (marked/seen/possessive counters, survey callback, cc array) is mutable across the walk.
- Verdict ladder `pss_verdict` is a separate ordered set of conjuncts (U1, U2, lazy conjunct,
  exact-count arm) combining `first_of(body)` with `follow`/`may_end`/`encl`; this is a
  first-match-like ladder but over a node, and it is not yet a table.
- Deny bits touching it: `PCREC_NO_POSSESSIFY` (axes.def), the future `-fno-poss-ctx-follow`
  (ENGINE-SELECTING, kept in `rx_info.flags`) and `-fno-poss-bref-first` (poss_arms.md
  `:996-1044`).
- Visibility: stamp `RX_VM_STRATS` (possessive/backtracking per A_REP); `--list-axes`
  `possessify` predicate rows (2 rows) hand-stated; correctness gate = `tests/possessify/
  run_possdiff.sh` exhaustive possdiff and CLAIM-vs-MARK.

### 4.4 Unusual (customer 4)

Rows are indexed by node kind (a finite enum), not scanned; there are 3 to 4 folds per kind
of different result type (set+nullable, parts, mutation); a mutable cross-node context
threaded down plus a fixpoint join across call sites; failures are loud (misplaced kinds)
and "widen to all" is the sound default; the exhaustiveness alarm is a COMPILER feature the
table must not lose.

---------------------------------------------------------------------------
## 5. Deny/force axes: `src/core/axes.def`, `rx_info.flags`, `--list-axes`

### 5.1 `src/core/axes.def` (242 lines, main)

X-macro, ONE ROW PER AXIS (not per candidate):

    PCREC_AXIS(deny_macro, deny_flag, force_macro, force_flag, default_state)

- `deny_macro`: token for a `lib/pcrec.h` bit (stringified with `#deny_macro` where a
  NAME is wanted), or `0`; `deny_flag`: CLI spelling `"-fno-X"` or `""`; `force_macro`:
  token or `0`; `force_flag`: `"-fX"` or `""`; `default_state`:
  `PCREC_AXIS_DEFAULT_ON`/`OFF` (the `default_state` column has no reader yet except
  [EMIT-VERB]'s and [MEMFN] pairs' `-fcomments`/`-fmemfn-simd`).
- It deliberately does NOT hold the bit VALUES (they are the public contract in
  `lib/pcrec.h`). The header names all non-rows: semantic flags (`PCREC_CASELESS`,
  `EMIT_MAIN`, `NO_CAPTURES`, `TRACE`), value parameters (`--engine=`, `--unroll=K`,
  `--vm-entry-shape=N`, `--tune=N`), `--fno-step-budget`.
- Rows are grouped by family not bit order. Force pairs: `prefilter`
  (`FORCE_PREFILTER`), `prefilter-collapse`, `startpos-guard` (`FORCE_STARTPOS_ALIGN`),
  `-futf-check` (force only, `deny_macro 0`, default OFF), comments pair (default OFF),
  memfn-simd pair (default OFF).
- Readers (all derived): `cli/main.c` `cli_axis_apply` (the `-f`/`-fno-` grammar);
  `axes_dump.c` `pcrec_axis_macro_name`/`pcrec_axis_cli_flag`; and through the dump
  `tests/axes/run_axes.sh` (answer-identity sweep) and `tests/registry/
  axes_registry_check.sh`.
- ROW-level deny bits (a candidate's `DfaCand.deny`) are NOT in axes.def as rows of a
  list; they are bits drawn from the SAME `lib/pcrec.h` enum. One bit can be on several rows
  (`PCREC_NO_OFFSET_SKIP` on 4 `dfa_pfs` rows and on the run-pinned pair together with
  `NO_RUN_PREFILTER`). The axis registry gets a row's deny by walking the live arrays; a
  candidate with no deny bit derives no CLI flag. Comment at `axes_dump.c:~190`: the
  `cli_flag` is derived from the candidate's deny BIT through `axes.def`, so "a bit, its
  printed symbol name and its CLI spelling are one row".
- Fact-level denies live on facts (`facts.def`: 28 `start_anchor`, 29 `end_window`, 30/31/44
  `req_*`), not on candidate rows (split from `patfacts/design.md` §7.1; load-bearing,
  `start_table.md` §3.7).

### 5.2 `rx_info.flags` masking

`emit_info_def`, `emit_dfa.c:2985-3015`:

    const uint64_t kept = PCREC_NO_ATOMIC_DISCHARGE | PCREC_NO_SPLICE_CALLS |
                          PCREC_NO_STARTPOS_GUARD | PCREC_FORCE_STARTPOS_ALIGN |
                          PCREC_FORCE_UTF_CHECK;
    const uint64_t axis_bits = 0
    #define PCREC_AXIS(dm,df,fm,ff,defst) | (uint64_t)(dm) | (uint64_t)(fm)
    #include "core/axes.def"
        ;
    const uint64_t strategy_denials = startpos_guard_inert | utf_check_inert |
                                      (axis_bits & ~kept) | PCREC_FAST_OR_FAIL;
    ... "    .flags = %lluULL," cx->opt->flags & ~strategy_denials

Polarity (comment `:2985-3003`): after four incidents (bits 16, 18, 21, ...: each a deny bit
moving `.flags` on every artifact it was passed to) the default is "masked unless in
`kept`". Kept: the two ENGINE-SELECTING denies (they leave a construct in the tree so the
knob is not a no-op) and the CONTRACT bits (masked only where `byte` encoding makes them
inert: `startpos_guard_inert`, `utf_check_inert`). `PCREC_FAST_OR_FAIL` is masked as non-row.
Consequence: an artifact's `rx_info.flags` keeps only knobs that change SEMANTICS or ENGINE,
so a row's deny bit is invisible in the artifact. Design §3.7: none of the 12 start-family
bits enters `strategy_denials` on an artifact it cannot act on; 18 `-fno-size-term` and 21
`-fno-scan-edge` were the two unmasked bits found, now [AXES-DENY-MASK]'s. The table of
which rows a deny removes is a survey family (#3, "mask membership, deny->row maps", live
inconsistency).

### 5.3 How `--list-axes` prints

`pcrec --list-axes` = `src/dump/axes_dump.c`, TSV per `docs/spec/table_contract.md`
(`#` comments, header = last `#` line before data; "columns append-only"; Sections
`#section NAME`, `--list-axes` gained `memfn` at R4a). Main table columns:
`axis order candidate kind stamp_macro stamp_value deny_macro deny_bit force_macro
force_bit cli_flag applies`.
- `kind`: `list` (candidates walked LIVE off a `DfaCand`-headed array via
  `emit_dfa_list_axis` + `pcrec_dfa_axis_*_cands`, order = 1-based array position), `both`
  (axis F), `predicate` (hand-stated rows, `emit_pred_row`; 37 of 52 axes). Predicate rows
  may attach to a list axis (`table`'s `none`/`mixed`, `scan-body` composites, via
  `axis_row`).
- Per row: deny macro NAME and bit NUMBER via `deny_cols`, CLI flag via `axis_cli_flag`;
  `stamp_value` = candidate name if the axis has a stamp macro.
- `desc`: from `AXIS_DESC` hand table for `dfa_pfs` & friends; from the row's own `desc` for
  `req_admits`/`req_uses`/`pcrec_reseed_rows[].applies_desc`. Drift is a known finding
  (design D-3; the `prefilter` AXIS_DESC has drifted).
- The `memfn` section is read from `mf_options()` (kit's OWN registry `options.def`: `MF_OPT(name,
  kind, budget, layer, doc)`, `no-NAME` denies / bare `NAME` forces for PAIR kind; pcrec
  passes `--memfn=` through uninterpreted). Floor on the member count is pinned as a literal
  in docs/spec/ (the independent control).
- Consumers: `tests/axes/run_axes.sh` (`make test-axes`: every deny/force flag answer-
  identical to default over the corpus, with form-census floors), the registry check, and the
  PC-3 check. Arms are enumerated from the listing, not named.

### 5.4 Unusual (customer 5)

A row's deny/force is declared in TWO places that must agree: the candidate's own `deny`
field (`DfaCand`) and the axis registry (`axes.def`); one bit may sit on many rows; a bit
may be on a FACT rather than a row; force bits exist only for axes that are not pure
first-match removal; the artifact reports almost none of them (masking); the CLI flag and
macro name are derived from the bit, so a row with no bit has no flag; the listing's `order`
is array position, `kind` is a property of how the axis is stored.

---------------------------------------------------------------------------
## 6. C1's trace convention: `PCREC_CAND_TRACE_REC`

### 6.1 Macros

Main `src/core/internal.h:6996-7008` (stc2 `:7098-...` adds a quiet depth):

    #ifdef PCREC_CAND_TRACE
    #define PCREC_CAND_TRACE_REC(slot, route, row, site) \
        fprintf(stderr, "CANDTRACE\t%s\t%s\t%s\t%s\n", (slot), (route), (row), "" site)
    #define PCREC_CAND_TRACE_RECF(slot, route, site, fmt, ...) \
        fprintf(stderr, "CANDTRACE\t%s\t%s\t" fmt "\t%s\n", (slot), (route), __VA_ARGS__, "" site)
    #else
    #define PCREC_CAND_TRACE_REC(slot, route, row, site)   ((void)sizeof("" site))
    #define PCREC_CAND_TRACE_RECF(slot, route, site, fmt, ...) ((void)sizeof("" site))
    #endif

stc2 wraps both in `(pcrec_cand_trace_quiet ? (void)0 : (void)fprintf(...))`, with `extern
_Thread_local int pcrec_cand_trace_quiet;` (defined in `emit_dfa.c`).

### 6.2 Format and rules

- Record: `CANDTRACE <TAB> slot <TAB> route <TAB> row <TAB> site`, one stderr line per
  start decision, printed at the walk's RETURN, never at a reader's use (design §3.3 item 5).
- `slot`: the CandSlot spelling as a string literal ("NEXT", "PRESENCE", "FIRST", "RETRY",
  "WINDOW", "WIDTH", "BOUND", "RECOVER"; plus pseudo slots "ROUTE" for dispatches and K-list
  decisions use "PRESENCE"/"FIRST"); `route`: `CAND_ROUTE_NAME(r)` = "dfa"/"vm"
  (stc2 adds "attempt"); for route class dispatches also "entry"/"inlined"/"empty"/"live"/
  "dfa-scan"/"no-dfa-scan"; `row`: the chosen row's stamp/listing NAME, "never a C
  identifier" (not the unique identity: on stc2 identity != spelling, so the trace prints
  `tok`); `site`: a declared SITE KEY (`pf-of`, `vm-start`, `scan-state`, `form-fwd`,
  `form-other`, `search-start`, `req-admit`, `req-use`, `reseed`, `end-window`,
  `attempt-cand`, `attempt-bound`, `vm-bound`, `root-minw`, `dfa-engine`, `entry-gate`,
  `engine-empty`, `run-tests`, `set-rest`, `prefix-k`, `req-site`, `req-gate`,
  `req-handoff`, `req-from`, `ofs-need`) = 25 keys at C1 (stc1_report §2 is the table: site
  key, slot, rows printed, record file:line, decision file:line, class W/I/R/P/L/K, kit B-id,
  commit that moves it).
- THE LITERAL CHECK: `site` is pasted as `"" site`, so a non-literal does not compile in
  BOTH builds (a `d == &cx->job->dfa ? "form-fwd" : "form-other"` argument was caught and
  became two records). No `__func__` (C0's experiment measured a `__func__` site
  false-alarming a selection-neutral rename on 6,443 sequences). Also,
  the default-build expansion `((void)sizeof("" site))` evaluates none of the other arguments.
- Arguments rule: records print only values the decision ALREADY computed (or a pure Job
  read), because an accessor asked for the first time inside a record would mark a fact
  `used` and move the facts listing and emitted bytes (checked by C1's trace-vs-default
  byte sweep, stream 6). Two records re-ask something (`pcrec_artifact_has_dfa_scan`, which
  reads only `fit`; `pcrec_fact_start_anchor` at `vm-bound`).
- Trace build is NEVER the byte-sweep build; C1 byte-sweeps trace build vs default.

### 6.3 How the output is diffed (C0 instrument; `scripts/emit_sweep.py --trace`, `scripts/trace_diff.py`)

- The sweep builds BOTH sides with `-DPCREC_CAND_TRACE` (`build_from_rev` gets a `CFLAGS`
  pass-through; the reference is regenerated from the PARENT every commit via `git archive`,
  never a stored reference), captures stderr per compile (never mixed with stdout), and tags
  each record with the PATTERN INDEX and ARM and `seq` (the ask's ordinal in the compile),
  by the sweep, not the compiler.
- The record as diffed: `pattern-index, arm, seq, slot, route, row, site`.
- Diff compares each pattern's sequence. C1 ruling (Frank's two conditions): the GATE is
  the SET compare (`trace_diff.compare(unordered=True)`); the ORDERED compare prints as a
  non-gating diagnostic; `--trace-ordered` swaps them. (Design §3.3 item 5 as written wanted
  ordered; the set invariant was adopted because no artifact surface records ask order, §1.3.)
- Declared multiplicity: a commit may change a pattern's sequence only by additions it
  declares (C5b: records whose `site` is one of its four BOUND readers); the diff filters
  exactly those and requires the rest identical.
- Records-floor: `TRACE_RECORDS_FLOOR` 256,608 / 62,962 at C1, then 262,901 / 64,776 after
  R4c' (measured, lane/stc1 185a4a8c); and `TRACE_SITES`: every one of the 25 declared site
  keys must print at least once on a full-population run on the working side (c-vm reaches
  13 keys; the other 12 are DFA-body sites) (K35: a site whose record stopped printing would
  hide inside an arm's total). Failing-direction control: planted swap of two records and a
  planted reorder within one pattern (mech S550-S555 on arm `emitsweep`); dropping `ofs-need`'s
  records reads NOT REACHED, trips both floors and gives 1,447 SET movers.
- What the trace proves for INLINE sites (design sound-m5): only that the print agrees
  with the emitted text; the emitted BYTES are the control. It is stronger than bytes only
  at walked sites (a row change between rows whose emitted text coincides).
- `call_graph.py` skips `PCREC_CAND_TRACE_REC*` invocations (multi-line too) when counting
  decision SITES: a record prints a decision and makes none.
- Independent controls (shared nothing with the table or the trace): the parent's byte
  sweep (streams 1-6), the deny-delta census (reads bytes and stamps only), stamp-vs-text
  agreements (H1: `VM_ROOT_MINW` vs emitted test; B1/B2: `start_max` literal; B3/B4:
  `VM_START` vs `attempt_max`).

---------------------------------------------------------------------------
## Hardest-to-host feature, one line per customer

1. `cand_rows[]` (START-TABLE): ONE array holding eight slots, each row filtered by (slot,
   route-bitmask) and carrying a per-slot heterogeneous payload plus a typed handoff
   graph (`hands`/`accepts`/`succ` sets with cross-slot selection reads and re-entry cycles).
2. `dfa_pfs[]` / `DFA_SELECT`: a type-erased stride walk over ten differently shaped row
   structs sharing only a `DfaCand` head, with an OPTIONAL `routes` field found by `offsetof`
   and a deliberately-crashing missing-fallback policy.
3. `select_engine.c`: not first-match at all: an AND-reduction over `analyses[]` with a
   side-channel first-excluder `why`/`node_why`, plus an inline 9-arm ternary ladder whose
   value set is range-tested by consumers and whose disjointness is a documented, one-pair
   asserted premise.
4. `[POSS-CTX-TABLE]`: a table INDEXED BY AST KIND (dispatch, not scan) whose rows must yield
   several folds of different result types (set+nullable, Glushkov parts, in-place mutation)
   under a mutable context with a call-site fixpoint, while keeping the compiler's
   `-Wswitch` exhaustiveness alarm.
5. Deny/force axes: a row's deny bit is declared on the row AND derived-from by the registry
   (one bit on many rows, some denies live on facts, force bits only on some axes), and
   a separate mask decides whether the artifact reports it.
6. C1 trace: the site key must be a compile-time string LITERAL (`"" site` paste) and every
   argument of a record must be a value the decision already computed, because evaluating a
   fact accessor in the record would itself change the compiled output.
