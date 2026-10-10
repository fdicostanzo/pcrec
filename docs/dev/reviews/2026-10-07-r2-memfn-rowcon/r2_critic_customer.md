# ROWCON r2 critic: the pcrec table owner (customer lens)

Reviewer: D6 adversarial critic, read-only. Subject:
`worktrees/memfn/docs/design/memfn/row_contracts.md` rev 2.1 (lane/memfn-rowcon
a165e69d), §1-§3 and Appendix A. The real code was read from `lane/stc2`
(`git show lane/stc2:src/gen/emit_dfa.c`, shown below as "stc2 :N") and from main
(`src/gen/emit_dfa.c`, `src/gen/emit_vm.c`, `src/core/compile.c`,
`src/opt/select_engine.c`, `docs/spec/match_api.md`, D152).

Counts: **2 BLOCKER, 7 MAJOR, 10 MINOR**. Verdict: **hostable without contortion:
YES-WITH-CHANGES.** B1 and B2 are design fixes, and neither one argues against the engine.

What holds, and needs no change:
- The deny test `row.deny & q.flags` matches both walks exactly (stc2 :8136, main
  :5094). That includes multi-bit rows (`run-pinned*`: `NO_OFFSET_SKIP |
  NO_RUN_PREFILTER`) and N12's flags=0 site (stc2 :8285-8288).
- First-match is preserved, and the filters are side-effect free, so they commute.
- `cand_nodes[]` is correctly left outside the engine.
- I agree that `analyses[]` (an AND-reduction) and [POSS-CTX-TABLE] (a dispatch on `AKind`
  that relies on `-Wswitch`) are not hosted.

---------------------------------------------------------------------------
## BLOCKER

### B1. The head's `applies` signature and polarity break pcrec's by-pointer predicates

- **Evidence.**
  - The doc's head (§2.1, row_contracts.md:62) declares
    `int (*applies)(const void *ctx, const struct mf_row *self)`, returning **0 = holds,
    >0 = reason (1 = "false")**.
  - pcrec's head declares `bool (*applies)(const DfaSel *s)`, returning **true = holds**
    (main :3391-3395, stc2 :3445-3449).
  - Appendix A row 1 claims "the returned bool maps to 0/1". It does not, for three
    reasons:
    1. The stc2 table's foundation is that "a walked row's predicate IS the old row's
       function, by pointer, so the oracle tests the FILTER" (stc2 :7776-7783). That
       covers 26 of the 37 rows (`pf_*_applies`, `req_*_applies`,
       `start_pinned_applies`) and every predicate on the ten main lists. A
       `bool(const DfaSel*)` cannot be stored in an `int(const void*, const mf_row*)`
       slot:
       - gcc 14 rejects `.c = { "window", 0, cand_window_applies }` as
         `-Wincompatible-pointer-types`, which is an error by default;
       - with a cast, calling through it is UB (C11 6.3.2.3p8).
    2. If the cast were made anyway, the polarity inverts silently: `true` (1) reads as
       "reason 1 = false", and `false` (0) reads as HOLDS. Every row would flip, and the
       totality fallback `cand_always` would become "never".
    3. The only legal route is one thunk per predicate. That is about 70 wrappers across
       `cand_rows` and the ten lists. It is exactly the contortion Frank asked to avoid,
       and it breaks the oracle's by-pointer premise, because `was` rows would no longer
       share the function.
  - Two other customers do not have a per-row function at all:
    - `pcrec_reseed_rows[]` uses a predicate TAG plus `switch` (emit_vm.c:11133-11150);
    - `fit_rungs[]` has `applies == NULL` rows (compile.c:725).
- **Fix.** Move predicate invocation into the TABLE, not the head:
  - add `int (*test)(const void *ctx, const void *row)` to `mf_table`;
  - have `MF_TABLE_TYPED(prefix, RowT, CtxT, …)` generate that ONE thunk per table, e.g.
    `return ((const RowT *)row)->c.applies((const CtxT *)ctx) ? 0 : 1;`.
  - The head keeps `name/deny/scope/routes/doc` and no predicate. Customers keep their
    typed predicates, by pointer, unchanged.
  - Tag tables and NULL-predicate tables write their own `test`, and the reason-code
    channel is still available to tables that want it.
  - Rewrite Appendix A row 1 accordingly.

### B2. Customer 2's "optional `routes` → `routes = 0` (= all)" inverts pcrec's meaning, and the query's route encoding is unspecified

- **Evidence.**
  - On main, a row mask of 0, and a list without a mask, both mean **DFA-only**:
    `cand_routed` reads `(m ? m : CAND_ON(CAND_ROUTE_DFA))` (main :5073-5077, stc2
    :5132-5136).
  - Ten of `dfa_pfs`' twelve rows carry no `.routes` (main :6623-6658).
  - `vm_start_row` selects `dfa_pfs` on `CAND_ROUTE_VM` with `.d = NULL, .us = NULL`
    (main :6693-6697).
  - Under the doc's "0 = all routes" (row_contracts.md:61, §3 row 2), that VM walk reaches
    `pf_run_bounded_applies` → `pf_run_applies_common`, and `pf_memchr_applies`, both of
    which dereference `s->us` (main :5735-5736, :5985-5987). The result is a NULL
    dereference on every prefilter-less VM compile.
  - stc2 forbids 0 outright: the self-check rejects `!r->routes` as "routed nowhere"
    (stc2 :8204-8205). The engine's wildcard would turn a forgotten mask into "every
    route", silently. That is the Q-ROW-1 "no silent defaults" ruling, violated in the
    engine's own head.
  - Separately, §2.1 never says whether `mf_query.route` is an INDEX or a MASK.
    `CAND_ROUTE_DFA == 0`. If the query route were a mask, or if 0 meant "unfiltered",
    every DFA query would admit VM-only rows. `ceiling`'s predicate reads `s->vm->…`, and
    `s->vm` is NULL off the VM route (stc2 :7909-7911), so that query crashes.
- **Fix.**
  - `routes == 0` is a table-definition ERROR (`mf_table_check` refuses it), never a
    wildcard.
  - Hosting the ten main lists means writing `CAND_ON(CAND_ROUTE_DFA)` on every row that
    has no mask today, which is the stc2 convention.
  - `mf_query.route` is an INDEX, and the test is `row.routes & (1u << q.route)`, which is
    pcrec's `CAND_ON`.
  - Correct §3 row 2 and §2.1's comment.

---------------------------------------------------------------------------
## MAJOR

### M1. Scope "0 = one" collides with `CAND_SLOT_WINDOW == 0`

- **Evidence.**
  - row_contracts.md:60 reads `scope; /* … 0 = one */`, beside a `routes` whose 0 IS a
    wildcard.
  - `CAND_SLOT_WINDOW` is enumerator 0 (stc2 internal.h `CandSlot`).
  - If 0 is read as "any scope", then rows 1-2 of `cand_rows` match every slot query.
    Row 2, `window-none`, is `cand_always` (stc2 :7963-7965), so it would WIN every
    query, for every slot.
- **Fix.** State that the scope filter is EXACT equality and has no wildcard; a
  single-scope table puts 0 on rows and queries alike.

### M2. The route is carried twice again (`mf_query.route` plus `ctx->route`)

- **Evidence.**
  - stc2 deliberately dropped the separate route parameter "because the route would be
    carried twice" (customers §1.2; stc2 :8124-8127, "never a second parameter that could
    disagree with it").
  - Appendix A row 3 has the caller writing `mf_query.route = sel->route`, which
    re-creates the two carriers.
  - The oracle's `every` loop mutates only `o.route` on a copy (stc2 :8270-8278). After
    migration it would also have to update `q.route`; if it forgot, it would check one
    route with another route's filter.
- **Fix.** Make it `MF_TABLE_TYPED(prefix, RowT, CtxT, route_member)`: the wrapper fills
  `q.route` from `ctx->route_member`, so no caller writes the route. Alternatively, give
  `mf_table` a `route_of(const void *ctx)` hook. Either way the ONE route derivation
  (`cand_route_of`) stays pcrec's.

### M3. `MF_NONE_ABORT` codifies `abort()` on the compile path, and the oracle needs NULL from the same table

- **Evidence.**
  - `docs/spec/match_api.md §8.1` (was `:4990`; §8.1, D56) promises: "It never `abort()`s the caller on
    the compile path". It adds that every "cannot happen" site now refuses through
    `pcrec_ctx_fail`, and since 2026-09-18 the promise "has none" exceptions.
  - `esel_of` quotes that rule for its premise check (select_engine.c:945-960).
  - Today's NULL dereference is no better, but a new mechanism should not add a sanctioned
    `abort()` to the library.
  - The stc2 oracle REQUIRES a NULL return. `cand_oracle_post` prints the
    `CANDORACLE no-row` line on `!nw` (stc2 :8265-8266), and the mech control S598
    (non-total fallback) rides on that diagnostic.
  - In the `-DPCREC_CAND_NEW_FIRST` build, `cand_oracle_pre` walks BEFORE `cand_rows_selfcheck`
    runs (stc2 :8243-8247), so a table-level ABORT would fire before `table-not-total`
    could print.
  - The result is one table needing two policies.
- **Fix.**
  - Replace `on_none` with a hook: `void (*on_none)(const void *ctx, const mf_decision *)`.
    pcrec sets it to a thunk that calls `pcrec_ctx_fail` with the printed record.
  - Allow a per-query override `MF_NONE_NULL` for oracle and quiet walks.
  - Drop `MF_NONE_ABORT`.

### M4. C1's trace is not "absorbed", and a migrated line would NOT be the same line

- **Evidence.**
  - (a) **Identity versus spelling.** stc2's trace and oracle print `tok`, not the
    identity (stc2 :7884-7890; customers §6.2: on stc2 "identity != spelling").
    Examples: `window-none`→`none`, `retry-anchored`→`anchored`,
    `attempt-gstart`→`gstart`, `next-none`→`none`. §2.2 maps `row` to "the CHOSEN
    verdict's row name", i.e. `mf_row.name`, which is the identity. Every such record
    becomes a SET-compare mover.
  - (b) **The route field is not the query route.** WINDOW, `ofs-need`, `req-site`,
    `req-handoff` and FIRST print route `"-"` (main emit_dfa.c:940, 1085, 1432-1455,
    1564). Two PRESENCE records print the route class `dfa-scan`/`no-dfa-scan`
    (:1451, :1455). The engine has a scope-name list and no route-name list at all.
  - (c) **Not every record is a row choice.**
    - `PCREC_CAND_TRACE_RECF` prints a formatted value (`nsel=%d`, :4243).
    - `ofs-need` prints a computed `sig` (:1085).
    - The `ROUTE` pseudo-slot prints `empty`/`live`/`entry`/`inlined` (:4279, :4284,
      :8632, :10058).
  - (d) **The macro cannot "pass that literal into `mf_query.site`".** The record is a
    `fprintf` at the walk's RETURN (customers §6.2); the query is built BEFORE the walk.
- **Fix.**
  - Say that the trace STAYS pcrec's, and do not claim absorption. Alternatively, give the
    head a separate `label` (the projection spelling) next to the unique `name`, as
    customers §1.5 item 7 asks, and add a route-name list to `mf_table`.
  - Add a pcrec-side selection macro, `CAND_SELECT(slot, sel, flags, site)`, that does the
    `"" site` paste and fills `q.site`.
  - Restrict the claim "the same line" to walked sites that print `label`.

### M5. Deriving `--list-axes` from `mf_table_rows` is not byte-identical for `cand_rows`, and the force-bit sentence is wrong

- **Evidence: `cand_rows`.**
  - Its listing is `list[route] = {axis, order, name}` (stc2 :7871-7877, :7895).
  - The listed name is a projection: `all` lists as `unanchored` (stc2 :8111-8113).
  - Rows with no listing must not print: `pred-memchr`, `ceiling`/`width-none`,
    `bot`/`attempt-gstart`.
  - `order` is explicit. Position within the scope would list `next-none` as 13, because
    `pred-memchr` sits before it, but it is listed as 12 (stc2 :8058-8062).
  - `mf_table_rows` yields `{name, deny, scope, routes, doc}` and can produce none of
    this.
  - Appendix A row 4 itself concedes that `list[route]` "keeps feeding --list-axes", which
    contradicts §2.4's "single source".
- **Evidence: the ten main lists.** There the listing is byte-identical only if three
  things stay the caller's:
  - `order` is the index within the list;
  - the `RX_VM_START_SCAN` stamp patch for VM-only rows stays (main :7736-7741);
  - the `applies` prose stays `axes_dump.c`'s `AXIS_DESC`. Moving it to `doc` changes the
    bytes unless the text is copied verbatim, and `AXIS_DESC` has drifted (D-3).
- **Evidence: force bits and `strategy_denials`.**
  - The force and cli columns derive from `axes.def` by bit, so they are unaffected.
  - `strategy_denials` masks `rx_info.flags` in the ARTIFACT (emit_dfa.c:2985-3015). It
    never touches `--list-axes`, so it is unaffected.
  - §3 row 5's "a force is a deny of the alternatives, expressed in the caller's flags" is
    false. `FORCE_PREFILTER` is read inside predicates (compile.c:715; select_engine's
    `prefilter_decision`). `FORCE_STARTPOS_ALIGN` and `FORCE_UTF_CHECK` are contract bits
    kept in `.flags`.
  - Expressing a force as row denies would put a `FORCE_*` macro into `deny_macro`
    columns, which is a listing mover and confuses the registry check.
- **Fix.**
  - State that forces are outside the engine.
  - The engine supplies identity, deny and routes. The customer supplies a projection
    callback, `list_of(row, route) → {axis, order, name}` or NULL.
  - Claim "single source of names and deny bits", not "of the section".

### M6. Nested `parent` records can dangle after a predicate longjmps

- **Evidence.**
  - Predicates may call `pcrec_ctx_fail` (customers §1.4 item 8). stc2 documents that a
    longjmp inside a quiet walk "leaves the depth raised" (stc2 :8169-8172).
  - The `parent` link (row_contracts.md:124-125) implies the engine keeps a
    current-decision pointer. Predicates walk other slots (P3→NEXT, F1→PRESENCE), so
    nesting really happens.
  - A longjmp out of `applies` leaves that pointer aimed at a dead stack frame.
  - pcrec is a library; `pcrec_ctx_fail` is its normal refusal path, and compiles repeat
    in one process. The next compile's first decision would therefore link a dangling
    parent.
- **Fix.**
  - No engine-global nesting state. The caller passes `mf_query.parent` explicitly; a
    predicate that walks has the record in hand through its ctx.
  - If a global is unavoidable, make it `_Thread_local`, keep it under `MF_TRACE` only, and
    reset it from a documented entry hook that pcrec calls in `compile_driver`.

### M7. `fit_rungs` is "hostable" only through encodings the doc does not state

- **Evidence.**
  - `fit_rung_denied` is not `deny & flags`: it also denies every `degrading` row under
    `PCREC_FAST_OR_FAIL` (compile.c:732-736). That is a class deny.
  - `applies == NULL` rows (`unroll-rescue`, :725) are SKIPPED by the walk and chosen only
    by `fit_rung_of(act)`. The engine would call NULL.
  - The fallback on none is `fit_rung_of(FIT_REFUSE)` (:755), not NULL.
- **Fix.**
  - State the encoding: `deny |= PCREC_FAST_OR_FAIL` on degrading rows. If the table is
    ever listed, that bit then prints as a row deny, so say so.
  - "Not walked" becomes the table `test` hook (B1) returning a SKIP code.
  - The fallback becomes the `on_none` hook (M3).

---------------------------------------------------------------------------
## MINOR

- **m1. The walk-order sentence is false.**
  - row_contracts.md:103-104 says "The order of the first four is cand_rows' own order".
    In fact `cand_select` runs slot, DENY, ROUTE, predicate (stc2 :8135-8138), and
    `dfa_select` runs deny, route, applies (main :5094-5096).
  - The OUTCOME is the same, because the filters are side-effect free. The RECORD is not:
    a row that is both denied and off-route records as "filtered" in `mf`, never as
    DENIED.
  - Fix: correct the sentence, and state why the order does not matter.
- **m2. "`mf_select` is pure" (Appendix A, oracle row) is false.**
  - Predicates memoize: `pcrec_find_byte_rate` records the first ask, and facts set their
    `used` column. That is why the oracle runs in both orders.
  - Under `MF_TRACE`, the reach counters would also count the oracle's quiet walks and its
    every-route walks (stc2 :8264-8278), which inflates "pcrec counts at select" (§2.3).
  - Fix: count only on a non-quiet query bit, or leave counting to the customer.
- **m3. The table's `stride`/`n` are hand-set.**
  - `DFA_SELECT` derives both from `sizeof` today (main :5101-5108).
  - Fix: `MF_TABLE_OF(id, array, RowT, …)` sets `.stride = sizeof array[0]` and
    `.n = sizeof array / sizeof array[0]`, and adds two checks:
    `_Static_assert(offsetof(RowT, h) == 0)` and
    `_Static_assert(__builtin_types_compatible_p(__typeof__(array[0]), RowT))`.
- **m4. `scope` is a `uint32_t` and loses `CandSlot` type checking.** The typed wrapper
  should take the customer's enum (`cand_select(CandSlot, …)` today).
- **m5. The head carries kit-profile masks (`honours`/`requires`) in every pcrec row.**
  - That puts dead kit vocabulary in pcrec's head, and grows it from 24 to 56 bytes.
  - Fix: reach the profile masks through a profile-supplied offset or accessor, not the
    common head.
- **m6. Performance is not a concern.**
  - The hottest selection is `dfa_edge_of`, once per DFA state (main :4367, :8174; :7935),
    with 2 rows walked. One cross-TU call per select is noise against `scan_choice`'s work
    in the predicate.
  - `dfa_edge_taken`'s pointer compare against `&dfa_edges[0]` survives a typed return.
  - Fix: state that the `rec == NULL` path writes no record and takes no `MF_TRACE`
    branch.
- **m7. Missed customers.**
  - (a) `pcrec_reseed_rows[]` (emit_vm.c:11061, walk :11163-11170) is a live first-match
    table on main with TAG predicates and a two-object ctx (`v`, `rs`). It belongs in §3
    until C5 deletes it into RETRY, and B1's `test` hook is what hosts it.
  - (b) `pss_verdict`'s ladder (possessify.c:891; customers §4.3) is the first-match part
    of customer 4. It is hostable on the same terms as `esel_of`, and §3 row 4 should say
    so.
- **m8. D152 is mis-cited.** Its "wrong tool" list is a single yes/no, an argmin, or a
  run-time per-call decision. An AND-reduction is not on it. Reword: "not first-match (a
  reduction), so outside D152's shape".
- **m9. `esel_of`'s hosting needs two things stated.**
  - The premise refusal (select_engine.c:958) stays BEFORE the walk.
  - The ESEL enum, whose ORDERED RANGES consumers test, rides in the payload; it never
    comes from row order.
  - The arms have no deny bits, so the gain is the record only. Say that, so nobody
    expects deny or listing machinery from it.
- **m10. The engine could host one more generalization: totality.**
  - Today `cand_rows_selfcheck`'s totality test compares function pointers
    (`last->c.applies != cand_always`, stc2 :8236).
  - Fix: a generic `mf_table_check_total(t, asks[nscopes])` that verifies "the last row
    routed for each asked (scope, route) is undeniable and always-true", given a
    customer-declared always-predicate. That is a real benefit an adopter would get from
    the engine, and §3 never names it.

---------------------------------------------------------------------------
## Answers to the brief's questions, compressed

| question | answer |
|---|---|
| Is Appendix A exact, row by row? | No, at four rows: predicate (B1), routes (B2), route carrier (M2), trace (M4). The deny row, the `cand_nodes` row and the payload row are exact. |
| Would `mf_select` make the identical choice on every (slot, route, flags, ctx)? | Yes, once B1, B2 and M1 are fixed. As written, `dfa_pfs` VM-route selections crash (B2), and a wildcard reading of scope 0 sends every slot to `window-none` (M1). |
| Type safety | It is lost at the predicate (B1) and at stride/n (m3). The fix keeps typed predicates and makes the compiler check the table. |
| Performance | Not a concern (m6). |
| Is `dfa_pfs`/`DFA_SELECT` hostable as claimed? | Yes, if the absent `routes` is written as DFA-only, never as 0 (B2). Per-state `st` is just a ctx field. |
| Customers 3 and 4 | I agree they are not hosted. Missed: the `pss_verdict` ladder and `pcrec_reseed_rows` (m7). `fit_rungs` needs its encodings stated (M7). |
| Customer 5's listing | Byte-identical for the ten main lists, with caveats. Not for `cand_rows` (M5). `strategy_denials` is irrelevant to the listing, and the force sentence is wrong (M5). |
| Is the C1 trace kept? | The SET-compare lines are not kept (M4). "A record argument is a value already computed" is kept, since the engine evaluates no row beyond the chosen one. |

**Verdict: hostable without contortion: YES-WITH-CHANGES** (B1, B2, M1-M7).
