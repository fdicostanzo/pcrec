# The compound and callouts: seam-by-seam alignment (D163 addendum 5)

**Status: PROPOSED, design only** (lane `cpcall`, 2026-10-12, from main `ca4a5f22`, abi 76).
Nothing under `src/`, `tests/` or `docs/spec/` changes in this lane. The note is written
before the compound's B4 (driver) brief, as D163 addendum 5 requires.

Read: D163 with addenda 1-5, D88 addendum 1, D36, D38, D41, D42.5, D49, D71, D133 Q11, D158
and its addendum; `compound.md` rev 2.1 (§A-§D, §F); `design_callout_abi.md`;
`../spec/match_api.md` §1-§5 and §10; plan rows [M4-CALLOUTS], [IFACE-PUSH], [FINDALL-NEXT],
[EMIT-ENTRIES], [EFFORT-BUDGET].

## 0. Answers first

1. **There is no B0 conflict.** B0-B2 (lane `cpb02`) can proceed as briefed. Three items
   are soft and cheap if taken now (§9.2): `CompPart` is born with a group-map field;
   `PB_ONE_ATTEMPT` is built as a general emission option, not as a part-mode-only one;
   and the B2 registry column is worded as "observes the attempt sequence".
2. **One item MUST change before B4.** `match_api.md` §4¶10 binds "a generated call site
   that invokes another `rx_matchfn` (a callout, a composed submatcher)". It also says pcrec
   emits no such call site today, so the obligation binds the first one that does. B4's
   controller IS that first site. `compound.md` §B.2's `if (r != 0) return r;` returns
   `PCREC_ERR_STARTPOS` and `PCREC_ERR_INTERNAL` where §4¶10 requires a trap. §5 proposes
   ONE call-site code table for parts and callouts alike. The §4¶10 spec hunk lands in
   B4's commit.
3. **One more change before B4, on the compound side.** D163 addendum 3 says each part
   DECLARES the groups it writes and reads. `compound.md` §A.1's `CompPart` has no field
   for this. The split's pad loop is that declaration, left implicit. Add the field
   (identity for derived parts) so the one-captures-array rule is a column, not prose (§6).
4. **What is built for callouts today** (§1): the ABI types (`rx_ctx`, `rx_matchfn`,
   `rx_callout_ref`, `rx_renderfn`) in every artifact's shared block; `<prefix>_match` typed
   `rx_matchfn` on every artifact; the `(?C` registry row (PLANNED, refusing "requires
   module 'callouts'"); a reserved `VE_CALLOUT` event kind with no producer and an empty
   `--emit-ir` `callouts` section. **Design-only**: every call site, the trap line, the
   binding of `rx_callout_ref`, the filling of captures-so-far (`ncap` is always 0), the
   syntax (D38 item 7, still open) and the PCRE2-compat block.
5. **The one design** (§3 has the table): a compound part and a callout are the SAME thing,
   a callee compiled by pcrec's unchanged pipeline, at two binding times. A part is bound
   at compile time inside one artifact (static, by name, guards-off, sequential). A
   callout is bound at link time to another artifact (an `rx_callout_ref`, guards-on,
   nested). Every seam then has one rule, parameterized by binding time. Where the two
   sides differ today, the callout side changes, and only in design text: no callout code
   exists, so none of it moves an artifact until [M4-CALLOUTS] step 2 or [IFACE-PUSH].
6. **Three questions for Frank** (§11): the budget unit across a composition (one meter
   per exported call, leaning yes); callout purity (answers depend only on what `rx_ctx`
   carries, leaning yes); and whether `PCREC_ERR_INTERNAL` from a callee propagates
   instead of trapping (leaning propagate).

## 1. What exists for callouts, built versus designed

Read by grep on main `ca4a5f22` (`grep -rn -i callout src/ tests/`).

| piece | state | where |
|---|---|---|
| `rx_ctx { subject, len, pos, ncap, caps, user, vars, nvars }` | BUILT, emitted in every artifact's shared block | `src/gen/emit_dfa.c` (the `PCREC_RX_ABI_H` block); `match_api.md` §2 |
| `rx_matchfn`, `rx_callout_ref { fn, user }`, `rx_renderfn` | BUILT as typedefs only; nothing calls through them | same |
| `<prefix>_match` typed `rx_matchfn`, exported unconditionally (D38.3) | BUILT | `match_api.md` §3.2 |
| D49's propagate-give-ups rule for an `rx_matchfn` return | BUILT on the callee side (the entries return the codes); no caller side exists | `emit_vm.c` match entry comment |
| §4¶10's call-site trap (`ret < PCREC_ERR_FLOOR && ret != PCREC_ERR_UTF`) | DESIGN only: "pcrec emits no such call site today" | `match_api.md` §4¶10 |
| `(?C`, `(?Cn)`, `(?C"text")` | registry row PLANNED; refuses with "requires module 'callouts'" | `src/parse/registry.c:1019` |
| callout sites in the VM | `VE_CALLOUT` reserved with no producer; `--emit-ir` `callout-sites 0`, `callouts` section empty | `src/gen/emit_vm.c:283`, `ir_listing.md` §3.7 |
| captures-so-far at a site (`ncap`, `caps`) | DESIGN only: every emitted `rx_ctx` sets `ncap = 0, caps = NULL, user = NULL` | `emit_vm.c:13507`; `match_api.md` §2¶6 |
| the binding (`extern const rx_callout_ref rx_callout_<name>`) | DESIGN only | `design_callout_abi.md` §1.1 |
| syntax | OPEN (D38 item 7; R-d) | — |
| PCRE2-compat block mirror | DESIGN only, generation-time (D38) | `design_callout_abi.md` §4 |
| inner captures exported (D38 item 5's v2) | recorded, not scheduled | D38 item 5 |

Tests: the shared-block typedefs are checked by `tests/codegen/run_codegen_tests.sh` (one
block per TU) and by S04 (a duplicate-typedef sabotage). `tests/assertions/kreset_entries.c` and
`tests/atomic_groups/atomic_entries.c` call `<prefix>_match` as an `rx_matchfn`. No test
binds an `rx_callout_ref`.

**So the alignment costs nothing in emitted code on the callout side.** Every callout
change below is a change to design text and to the spec sentences that will govern the
first callout producer.

## 2. The family (SIBLING-OF-A-FAMILY)

A compound and a callout are two of SEVEN mechanisms by which one compiled matcher calls
another. The lens asks whether they are one family. They are: each answers "run a
separately produced machine from here and use its answer".

| member | binding time | callee | call shape | captures | backtracking into it | budget | storage |
|---|---|---|---|---|---|---|---|
| VM hybrid's embedded prefilter (D31) | compile, in-Job | P under erasure | DFA search, hands a window | none | n/a (a locator) | none (DFA) | none |
| subroutine call, LINKED ([DD-14]) | compile, in-program | a group of P | VM call frame, return label | callee writes, return RESTORES the write set | yes (10.46 is backtrackable) | the caller's | the caller's frames |
| lookaround body (M6.6) | compile, in-program | a sub-pattern | sub-match, verdict, position discarded | positive retains, negative discards | no (atomic) | the caller's | the caller's frames |
| `.rxt` definition / `lib` (§5.5, D89) | compile, source | a bound definition | inlined or called | delivered BY NAME into slots above `ngroups` | per the call kind | the caller's | the caller's |
| **compound part** (D163) | compile, in-artifact | P derived or under options | entry call (`search`, bounded search, `next_pos`, `valid_upto`) | ONE array, parent numbering (add. 3) | no (unique end; a part's answer is final) | §A.9: fresh per part | one region, max over parts |
| **callout** (D36/D38) | LINK | any `rx_matchfn` (another artifact, or user code) | `rx_matchfn(const rx_ctx *)`, anchored | sees captures-so-far IN; opaque OUT (v1) | no (atomic, D38) | the callee's own, fresh per call | the callee's own (stack default) |
| substitution template callback (`rx_renderfn`, D38 Q6) | LINK | user code | `rx_renderfn(const rx_ctx *, out, outcap)` | sees the completed match | n/a | none | none |

Two columns already agree across every member: **the callee's answer is final**
(atomicity: a callout is atomic by D38, a compound part needs a unique end, a lookaround is
atomic), and **give-ups propagate** (D49). The other columns are the seams below.

The compound row and the callout row differ in only one ESSENTIAL respect: binding time.
From it follow nesting (a part runs between other parts, a callout runs inside the
caller's match) and knowledge (the compound driver knows its part's code set, guards and
group numbering, while a callout site knows only the `rx_matchfn` type). Every other
difference in the table is accidental, and §4-§10 remove it.

## 3. The one design, in one table

| seam | ONE rule | compound side | callout side | when it lands |
|---|---|---|---|---|
| calling convention (§4) | a callee exposes the `match_api.md` §3 entry set. A part is called directly by name; a callout through `rx_callout_ref`. `rx_matchfn` is the late-bindable member of the set | unchanged | unchanged | — |
| result types (§4) | a call returns `locate_finish.md`'s typed result; `rx_matchfn` hands the `verify-at` type (SPAN at a point, or NOMATCH, or a give-up) | §A.2's type check accepts a callout-typed callee | the callout spec cites the vocabulary | text only |
| return codes at a call site (§5) | ONE first-match table: code class → action, rows emitted only for codes the callee can return | §B.2's `return r` replaced by the table | §4¶10 becomes that table; INTERNAL propagates (Q3) | **B4** (first composed call site) |
| captures (§6) | ONE group map per binding (reads, writes); ONE inbound channel (`rx_ctx.caps`, caller numbering); ONE delivery (the binder copies on success, trailed iff it backtracks) | `CompPart.groups` (identity for derived parts) | D38 item 5's v2 re-specified as a map on the binding unit, not a non-const `rx_ctx` | field **before B4**; the rest at client 7 / callouts step 2 |
| budgets (§7) | one meter per EXPORTED call, charged by every callee in the chain | §A.9's "fresh per part" becomes interim | callees charge the outer meter through the session pointer | **B6** / [IFACE-PUSH] (Q1) |
| storage (§7) | sequential callees share one region; a nested callee gets disjoint storage | as designed (§A.9) | as designed (§5.3¶3, §10.5) | — |
| linkage and naming (§8) | ONE namespace reservation table; callout bindings are external references, never closure nodes | the `__` refusal is row 1 | `rx_callout_<name>` becomes a row | row 1 at **B4** |
| cross-call state (§9) | `rx_ctx` gains ONE `rx_session *`. The session has a shared half and an artifact-owned cache region tagged with its owner | §C's `state_words` live in the owned region | callees see the shared half and never read a foreign cache | [IFACE-PUSH] / B8 |
| stamps and `rx_info` (§10) | three stamp kinds: pattern-level, machine-level, LINK-level (dependencies) | parts never appear in `rx_info` (D88 add. 1) | `rx_info` lists the callout names an artifact needs | callouts step 2, in [IFACE-PUSH]'s bundle |
| guards and validity (§10.2) | a call chain checks once | §A.6's one prologue | a callee may skip a check its caller attests (unlock U2) | trigger |
| match-here on an attempt route (§10.3) | `PB_ONE_ATTEMPT` is the general match-here | §B.3 | a composed callee's `_match` stops being O(n) per fire (unlock U1) | trigger |

## 4. Calling convention, context and result types

**Compound.** The controller calls part entries by name with the per-artifact signatures:
`<p>__f_search(s, n, from, caps)`, `<p>__f_next_pos`, `<p>__f_valid_upto`, `<p>__q_search`.
Parts are static, in one TU, and gcc may inline them (§A.5). Results are typed in
`locate_finish.md`'s vocabulary: a part's search hands SPAN (1 with `caps[0]`), NOMATCH (0)
or a negative code. A bounded part's search is `verify-at` at a point.

**Callout.** A site calls `ref->fn(&ctx)` after copying `ref->user` into `ctx.user`. The
callee is any `rx_matchfn`: it returns a length anchored at `ctx->pos`, `-1`, or a code.

**Where they differ.** The entry shape (search versus match-here) and the binding
(direct versus indirect). Neither difference is a misalignment. A part must be called
through the search shape, because `_match` on a DFA attempt route is `"search-filter"`
and cost-wrong (J-2). Late binding needs a type that does not depend on the prefix, and
only `rx_matchfn` has one.

**The ONE design.** The callee interface is the `match_api.md` §3 entry set. A part binds
any member directly. A callout binds the one member with a fixed-literal type
(`rx_matchfn`), and later `rx_matchcapsfn` (§6.3). Typing: `rx_matchfn`'s return IS the
`verify-at` result (a SPAN `[pos, pos+len)`, NOMATCH, or a code). So `compound.md` §A.2's
combinator type check can accept a callout-typed callee as it accepts a bounded part, and
"an artifact whose part is another artifact" never needs a new type.

**Cost:** text. `compound.md` §A.2 gains one sentence; the callout spec, when written,
cites `locate_finish.md` §1.2.

## 5. Return codes at a call site (MUST before B4)

### 5.1 The conflict

`match_api.md` §4¶10:

```c
if (ret < PCREC_ERR_FLOOR && ret != PCREC_ERR_UTF) __builtin_trap();
```

It binds "a generated call site that invokes another `rx_matchfn` (a callout, a composed
submatcher)", and "pcrec emits no such call site today; the obligation binds the first
that does". `compound.md` §B.2 emits:

```c
int r = <p>__f_search(s, n, from, caps);
if (r != 0) return r;                    /* match, give-up or refusal: final */
```

A compound part is a composed submatcher, and B4's controller is the first generated site
that calls into another compiled machine with a code space. (The VM hybrid calls its
embedded DFA search, but a DFA search returns only `{0, 1}`. §5.2's table covers it with no
rows.) As written, the controller returns `PCREC_ERR_STARTPOS` and `PCREC_ERR_INTERNAL`,
where §4¶10 traps on both. Either the compound obeys §4¶10 or §4¶10 is re-scoped. The
two sides must agree before B4 is briefed.

### 5.2 The proposal: one first-match table, keyed by what the callee can return

A call site's handling of a negative return is a FIRST-MATCH TABLE over code classes. Its
rows are emitted only for the codes the CALLEE CAN RETURN, read from the callee's own
facts: its engine (a DFA never gives up), its guards (a guards-off part never refuses), and
its `-futf-check` arm. Every other code reaches the last row. One table serves parts and
callouts; the binding time selects which facts are known.

| # | code class | action | a compile-time part knows | a link-time callout knows |
|---|---|---|---|---|
| 1 | `>= 0` (SPAN) / `1` | the combinator's success edge | yes | yes |
| 2 | NOMATCH (`-1` / `0`) | the combinator's failure edge (relocate, or the outer path fails) | yes | yes |
| 3 | give-up `[PCREC_ERR_FLOOR, -2]` | **propagate** unchanged (D49; D158: final) | only if the part is VM | always (unknown callee) |
| 4 | `PCREC_ERR_INTERNAL` | **propagate** (Q3; today §4¶10 traps) | only if the part has a producer (`vm_look_behind`'s negative arm) | always |
| 5 | `PCREC_ERR_UTF` | **propagate** (D133 Q11) | never: parts are `-futf-check`-clear (§A.6) | if the callee checks |
| 6 | `PCREC_ERR_STARTPOS` | **trap**: the caller generated the position, so it is a boundary (§9.5) | never: parts are guards-off | always (a callee's guard is on) |
| 7 | `PCREC_ERR_UNSET_VAR` | **propagate** (the caller's data, as UTF) | only on a var-bearing part (VM) | always |
| 8 | anything else below the floor | **trap** (the reserved abort space, D38 item 4) | always | always |

For B4's DFA-only, guards-off, check-clear parts, rows 3-7 have no member, so the
controller emits rows 1, 2 and 8. Rows 1-2 are the combinator's edges, so row 8 is the
only new line: `if (r < 0) __builtin_trap();` under the part's search. That line is dead
code by construction. G2 cannot reach it, and a trace-build assertion records that it is
unreached. **The answer does not change for any admitted pattern**, since no admitted part
can return a negative code.

Should B4 emit a dead trap at all? Yes. It is a one-line cold path that turns a broken
guards-off invariant (a part compiled with its guard on by mistake, CMP-12's plant) into a
crash instead of a silently returned refusal. It is also the line §4¶10 already demands.
CMP-12's detector should gain the trap as its second witness.

### 5.3 What changes

- **`match_api.md` §4¶10** (B4's commit, D80): the one-line rule becomes the table above.
  The sentence "pcrec emits no such call site today" goes, and the compound controller is
  named as its first producer. If Q3 is ruled "trap", row 4 reads trap and nothing else
  moves. Row 7 is also a change: today's line traps on `PCREC_ERR_UNSET_VAR`, but variables
  ride `rx_ctx` from the caller, so an unset one is the caller's data, as UTF is. No
  producer exists either way.
- **`compound.md` §B.2 and §A.2**: the controller sketch shows the table's emitted rows.
  The `first-nonzero` combinator's "a SPAN or give-up is final" is restated as rows 1, 3, 4,
  5 and 7.
- **`design_callout_abi.md`**: an appended alignment block (house style) records that F2's
  trap obligation is now this table's row 8 and that INTERNAL propagates (pending Q3).
- **Cost:** for compounds, no movers beyond B4's own abi event (the controller text is new
  anyway). For callouts, none (no call site exists). One sabotage row: CMP-12 gains the
  trap's witness. A new row, CMP-18 (the table emits row 3 for a DFA part, which is a
  population-0 overreach), is optional.

## 6. The captures array

### 6.1 The two sides

- **Compound (D163 add. 3).** One array, in the PARENT pattern's numbering, through the
  same `rx_ctx` the outer call received. Each part declares what it writes and reads. A
  derived part keeps the parent's numbers; a standalone sub-pattern gets a renumbering map.
  There is no backtracking across a cut (the unique-end condition), so nothing is restored.
  On split, F writes all of P's groups. Q writes P's groups minus the pruned ones, and the
  controller pads the rest ("pad slots Q lacks").
- **Callout (D38 item 5, F5, F9).** A callee READS the outer captures-so-far through the
  const `rx_ctx.caps`, valid for the call only. The outer engine's trail undoes them on
  backtrack. The callee's own captures are OPAQUE. The group form (R-c) captures only the
  consumed span, written by the OUTER engine. D38 item 5's v2 path: "declared-in-syntax
  export (`(?Cc<n>"fn")`), requires a non-const ctx + capacity field, a DD-3 struct
  revision".
- **Source composition (§5.5).** A definition's exported groups are DELIVERED by name into
  slots above `ngroups`. A recursive definition's delivery is refused.

### 6.2 Where they differ, and the finding

The three mechanisms answer one question: in which caller slots does a callee's group
land? Each spells the answer differently: a compound renumbering map, a delivered-by-name
slot table, and a declared export count with a non-const struct.

A second finding is sharper. **The compound's "B reads A's groups" (client 7) needs an
INBOUND channel that no compiled entry has.** `_search` and `_match_caps` take no inbound
captures. `rx_ctx.caps` is the inbound channel callouts designed, but no engine consumes
it: F2 says a matcher never requires inbound capture state, and every emitted site passes
`NULL`. So client 7's VM part B, finishing from A's end with a backreference into A, needs
exactly the callout side's designed-but-unbuilt channel. The compound and callouts need
the SAME new engine capability: seed a declared set of slots from `ctx->caps` before the
attempt.

### 6.3 The ONE design

1. **A group map per binding**: `{ writes: callee group → caller slot, reads: caller slot →
   callee group }`, fixed when the binding is made. It is identity for a part derived from
   the parent. It is an offset or a table for a standalone sub-pattern part (D163 add. 3).
   It is what §5.5's delivery computes for a definition, and what an outer pattern declares
   for a delivering callout.
2. **One inbound channel**: `rx_ctx.caps`, in the CALLER's numbering. A callee that reads
   (client 7's B; a callout predicate such as `(\d+)(?C"gt100")`) indexes it through its
   read map. A callee whose read map is empty ignores it, which is F2 today, unchanged.
3. **One delivery primitive**: on a SUCCESS the binder copies the callee's written slots
   through the write map into the caller's array. The copy is trailed when the binder
   backtracks (a VM site under a callout) and plain when it does not (a compound
   controller, which runs after success only). §3.1¶4's caps-untouched-on-failure rule
   then holds for both with no restore logic: a failing callee writes nothing, which is
   the shipped discipline of every entry.
4. **Callout outbound (re-specifying D38 item 5's v2).** The callee's captures leave
   through the `match_caps` shape, not a writable `rx_ctx`. The binding unit gains the
   capture-delivering function and its map:

   ```c
   typedef ptrdiff_t rx_matchcapsfn(const rx_ctx *ctx, ptrdiff_t (*caps_out)[2]);
   typedef struct rx_callout_ref {
       rx_matchfn     *fn;
       void           *user;
       rx_matchcapsfn *fn_caps;   /* NULL: opaque (v1) */
       size_t          ncaps;     /* the callee's <PREFIX>_NCAPS; 0 when fn_caps is NULL */
   } rx_callout_ref;
   ```

   `<prefix>_match_caps` already has the type `rx_matchcapsfn` names, so a compiled matcher
   still links as a delivering callout with a one-line wrap. `rx_ctx` stays const and
   per-position, and the outer engine writes the slots through its own trailed writer. The
   map comes from the outer pattern's declaration (D38's `(?Cc<n>"fn")` direction), at
   compile time, because group numbering is compile-time (subst C1).

**Restore rules, stated once.** A callee's writes reach the caller only through
delivery-on-success (point 3). Undo is the caller's own mechanism: the trail when it
backtracks, nothing when it does not. [DD-14]'s linked call (writes, then restores the
write set on return) is the in-program member, with a different rule on purpose: PCRE2's
plain subroutine call is capture-transparent. §5.5's `=` delivery is the opt-in that
makes a definition behave like point 3.

### 6.4 What changes, and when

- **`compound.md` §A.1, before B4:** `CompPart` gains `groups`, the part's map, stated by
  every part (no default, house rule). For split both parts state `GROUPS_IDENTITY`. The
  pad loop is then "the slots the identity map names and the part does not write", and
  "pad only when `<P>__Q_NCAPS < <P>_NCAPS`" is read off the map. A table-build check:
  every caller slot `1..ncaps-1` is written by some part on every success path the
  combinator can take. For split, F covers all of them and Q plus padding covers all of
  them. On a DFA-only build `ncaps == 1` and the check is trivial, but the field exists.
- **`compound.md` §D (client 7), at its trigger:** B's read map; the slot-seeding engine
  capability (§6.2), shared with callouts.
- **`design_callout_abi.md`, appended block:** D38 item 5's v2 is re-specified as point 4.
  The non-const `rx_ctx` + capacity field is withdrawn. Ruled direction unchanged:
  declared in syntax, compile-time numbering.
- **`match_api.md`:** nothing now. The `rx_callout_ref` fields are an abi event when
  callouts build (a shared-block change moves every artifact). That is [M4-CALLOUTS] step
  2's, or the [IFACE-PUSH] bundle's if it comes first.

## 7. Budgets, give-ups and storage across a call

### 7.1 The two sides

- **Compound §A.9.** Each part entry initializes its own budget. A compound search makes at
  most one call per part. DFA parts have no budget. A part's give-up is returned at once.
  §G Q3: the compound may answer where the plain artifact gives up, and never the reverse
  (the B6 give-up differential).
- **Callout.** The callee is a separate `rx_matchfn`. Each call initializes the callee's
  own budget, and the outer VM may fire it at every position it tries. The total effort of
  one outer call is therefore unbounded by any budget the caller set (N fires × the
  callee's budget). [FINDALL-NEXT]'s manager lean already names the fix: `rx_ctx` gains one
  pointer to the caller's session, so composed matchers charge ONE shared budget
  ([EFFORT-BUDGET]).

### 7.2 Where they differ

"Fresh per callee" is what both sides do today. It is bounded for the compound (at most
`nparts` × budget per call) and unbounded for callouts. Even the bounded form is a
caller-visible budget multiplier: a compound call can spend up to `nparts` budgets. The
spec already documents one such multiplier and had to say so in words: the tiered
default's ×2, §4¶4. A caller who sets `--step-budget` to bound one call's work would
need a third such sentence for compounds and could get none for callouts.

### 7.3 The ONE design (Q1)

**One meter per EXPORTED call.** Every callee in the chain charges it: parts through an
internal meter pointer (part entries are static, so the parameter is internal text), and
callouts through the session pointer (§9). With no session (an un-suffixed entry, today's
callers), the exported entry allocates the meter on its own frame, which is today's
behaviour for a plain artifact. Consequences:

- **D158 gets one comparison unit.** A compound's charge and the plain artifact's charge
  are in the same unit (one meter, one call). The B6 give-up differential compares like
  with like, and §G Q3's "fresh budget per part" asymmetry is gone. The cost: a compound
  can now give up where the "fresh per part" form would have answered. That is exactly
  the D158 question the differential already asks, so B6's gate decides it, never a
  multiplier.
- **Callouts become bounded.** One outer call's total work is at most the caller's budget,
  however many times a callee fires.
- **[EFFORT-BUDGET] inherits it.** The single weighted counter is one more reason for one
  meter. The meter's unit is that row's; this note fixes only its SCOPE (the exported
  call).
- **The tiered default (§4¶4, ×2) is unaffected.** It re-runs the whole exported call, so
  it is a second exported-call meter, as today.

**Storage.** Already aligned, and stated once. Sequential callees share one region (the
compound's parts run one after another, so `compound.md` §A.9's "one region sized by the
max over parts" is sound). A nested callee needs disjoint storage (a callout runs inside
the outer engine's live frames: §5.3¶3, §10.5). One spec gap belongs to B6: a compound's
public `<p>_buffers` counts frames of ONE frame type (§10.2¶2), and parts can have
different frame sizes (24 versus 40 bytes). The compound's frame unit must be defined as
the largest part frame, with the controller converting counts per part. That is a B6
spec hunk.

### 7.4 What changes, and when

- `compound.md` §A.9: "each part entry initializes its own budget" is marked INTERIM. It
  is harmless at B4 (DFA-only parts have no budget) and is decided at B6 by Q1. §G Q3 is
  restated against the one meter.
- [FINDALL-NEXT] / [IFACE-PUSH]: the session carries the meter (the lean already recorded
  there); callees charge it.
- Callout spec (when written): a callee charges the outer call's meter when the session
  is present; with no session it charges its own, as today's entries do.

## 8. Linkage and naming

### 8.1 The two sides

- **Compound.** [EMIT-ENTRIES]' three categories (EXPORTED / KEPT STATIC / OMITTED). Parts
  are named `<prefix>__<role>` and are static or omitted. The `__` reservation in user
  prefixes is §G Q2 (refuse at B4). One exported interface per file (D88 add. 1).
- **Callout.** The artifact declares `extern const rx_callout_ref rx_callout_<name>;`, an
  UNDEFINED reference the embedder defines, prefixed by neither the artifact's prefix nor
  a part role. A compiled matcher used as a callout needs its `<prefix>_match` EXPORTED,
  which D38.3 guarantees ("unconditionally").

### 8.2 Where they differ, and the findings

1. **Names come from four sources** and nothing states their reservations together:
   per-artifact `<prefix>_*`, parts `<prefix>__<role>_*`, the fixed ABI types `rx_<type>`,
   and callout bindings `rx_callout_<name>`. The harness lever (§A.11) proposes a fifth:
   a reserved unique prefix. A collision class exists today in design: prefix
   `rx_callout` plus a callout named `search` gives `rx_callout_search` twice (population 0,
   since callouts are unbuilt). The `__` refusal is one row of a table nobody has written.
2. **[EMIT-ENTRIES]' public request contradicts D38.3.** Omitting `_match` from a requested
   set breaks "the match-here entry is exported unconditionally on every generated
   matcher" (D38.3, F1). That is the ruling that makes every artifact a valid callout. B0
   is internal, with every entry exported by default, so B0 does not conflict. The PUBLIC
   request (compound.md §H U3) needs D38.3 re-ruled at [IFACE-PUSH]: an embedder that
   composes requests `_match`.
3. **Callout bindings are not closure nodes.** The edge from a VM body to
   `rx_callout_<name>` points at an external symbol, not at an entry of this artifact. B0's
   entry table should not model it (none exist), and B0's closure must never treat an
   undefined reference as OMITTABLE.

### 8.3 The ONE design

A **namespace reservation table**, one first-match row list, owned by `valid_prefix`'s
module (`src/core/compile.c`) and listed in `cli.md` beside `-p`'s grammar:

| row | reserved form | refused user prefix | first enforced |
|---|---|---|---|
| parts | `<prefix>__<role>_*` | any prefix containing `__` | **B4** (§G Q2) |
| callout bindings | `rx_callout_<name>` | a prefix equal to `rx_callout`, or starting with `rx_callout_` | [M4-CALLOUTS] step 2 |
| harness lever | its reserved name prefix (§A.11's manager note) | that prefix | B4, if the narrower fence is chosen |

B4 lands the table with its first row, so the next reservation adds a row rather than a
second refusal. **Cost:** at B4 the same refusal §G Q2 already plans, written as a table.
The callout row moves the refusal set when callouts build (population 0 in the tree,
`grep -E -- '-p rx_callout'`).

## 9. Cross-call state

**The two sides.** Compound §C: `CompRow.state_words` (0 for split) and a cache in the
[FINDALL-NEXT] caller struct, valid while the subject is unchanged; `\K` declines it; a
give-up is never cached. Callouts: per-binding `user` (const, in `rx_callout_ref`) and
per-thread TLS that is the callout's own business. [FINDALL-NEXT]'s lean: `rx_ctx` gains
ONE pointer to the mutable per-session struct, so callouts and composed matchers see what
the outer search was given.

**The finding.** With one session pointer threaded through every call, a COMPOUND USED AS
A CALLOUT receives the OUTER artifact's session. Its controller would read and write its
`state_words` cache inside a struct sized and owned by a different artifact. Two
artifacts' caches would collide in one struct, and the inner one could read a "Q result
still valid" entry the outer wrote for a different machine. This is an answer bug, not
just a cost one.

**The ONE design.** `rx_ctx` gains `rx_session *session` (pointer to mutable; `rx_ctx`
stays const and per-position). The session has two halves:

- a **shared half** (the meter of §7, caller counters, and whatever [IFACE-PUSH] moves in
  from `user`/`vars`). Every callee in a chain reads and charges it;
- an **owned cache region**, tagged with its owner's identity (`&<p>_info`, the one
  per-artifact address that already exists). A controller uses the cache only when the tag
  is its own. A callee seeing a foreign tag runs stateless. Answers are history-independent
  either way ([FINDALL-NEXT]'s constraint), so ignoring a cache is always sound.

`compound.md` §C's `state_words` live in the owned region. **Cost:** none now. It is part
of [IFACE-PUSH]'s `rx_ctx` layout event (already planned there) and of B8.

## 10. Stamps, `rx_info`, and "callout" versus "part"

### 10.1 Stamps and `rx_info`

`compound.md` §A.7 classifies every stamp as pattern-level (P's) or machine-level (a
defined compound value). Callouts add a THIRD kind: **link-level**, what the artifact
NEEDS from its link: the `rx_callout_<name>` symbols it references. A loader ([ART-MGR])
or a composing build needs that list without parsing C. Parts never appear in it, because
parts are inside the file (D88 add. 1). The kind decides the compound value as for the
other two: a compound's link-level set is the union over parts. Today it is always empty,
because A3 declines callouts. **Proposal:** when callouts build, `rx_info` gains the
callout-name list, and `compound.md` §A.7's table gains the link-level row. No B4 change:
`<PREFIX>_COMPOUND` and the sentinels stand as designed.

`_ENGINE` on a compound reads "vm if any part is VM", which §A.7 glosses as "can a call give
up". A callout-bearing artifact is VM by D36's forcing, so the two readings agree. Keep
§A.7's gloss.

### 10.2 Guards and validity: "a call chain checks once" (unlock U2)

A part is compiled guards-off and `-futf-check`-clear. The controller's ONE prologue
checks with P's reach (§A.6, measured: plants 2 and 3 fire without it). A callee bound as a
callout keeps its own guard and check. Under `-futf-check`, a `<prefix>_match` call checks
`[pos − LB, n)` (`match_api.md` §3.2¶2: "over the same checked range `<prefix>_search`
uses"). A callout fired at each position the outer VM tries would then re-validate the
subject's tail on every fire: O(n) per fire, so O(n²) per outer call. This is read from the
spec text and not measured, because no call site exists. The compound's one prologue is
the general rule "a call chain checks once". For callouts it needs an attestation: the
session's shared half records the range the outermost prologue validated, and a callee
whose required range lies inside it skips its own check. The boundary guard costs O(1) and
stays.

### 10.3 Match-here on an attempt route (unlock U1)

J-2 measured that `_match` on a DFA attempt route (`"search-filter"`) runs the whole attempt
loop. As F it reads 128,040,004 loads on K106, against 3 for the bounded attempt. The
compound fixes `_match` for admitted compounds only (§B.3). Any OTHER attempt-route artifact
bound as a callout has a `_match` that skims the rest of the subject on every failing fire
(§3.2¶6 says so). `PB_ONE_ATTEMPT` is the general cure: on an attempt route, match-here IS
one bounded attempt at `ctx->pos`. B1 builds the bound as a part option. **B1 should build
it as an emission option any artifact's `_match` could select**, with part mode as its first
reader and no compound-only coupling. Then U1 is a selection row, not a second mechanism.

### 10.4 An artifact used as a callout versus as a compound part

| property | compound part | callout-bound artifact | aligned by |
|---|---|---|---|
| produced by | the same compile, derived tree or options | a separate compile | — (the binding time) |
| linkage | static or omitted (B0 closure) | exported `<prefix>_match` (D38.3) | §8 |
| called | by name, sequentially, at most once per part | through `rx_callout_ref`, nested, per fire | §4, §7 storage |
| entry shape | any §3 entry (search, bounded search, `next_pos`) | `rx_matchfn` (later `rx_matchcapsfn`) | §4, §6.3 |
| codes | rows for what the part can return | rows for an unknown callee | §5 table |
| guards and check | off; one prologue in the controller | on; attestation skips the check (U2) | §10.2 |
| captures | one array, map (identity when derived) | inbound `ctx->caps`; outbound by map (v2) | §6 |
| budget | the exported call's meter | the exported call's meter (session) | §7 (Q1) |
| state | the owned cache region | shared half only; foreign cache ignored | §9 |
| answer finality | unique end (client 7's admission) | atomic (D38) | the same rule |
| `rx_info`, ABI block | none (the compound has one) | its own | D88 add. 1 |

**A compound used as a callout** works with no extra rule: its `<p>_match` is the
controller's match (prologue plus F's bounded attempt), which is O(attempt) (§B.3). Under
§9 its cache is skipped when the session is foreign. **A callout inside a compound part**
is declined today (A3, below), and becomes possible under Q2.

### 10.5 Callouts and A3 (the decline)

`compound.md` §B.8 declines callouts through `RF_CROSSES_ATTEMPTS`, because they "observe
the attempt order". D36 already rules the fire-point discipline ENGINE-RELATIVE, citing
PCRE2's `PCRE2_NO_START_OPTIMIZE` latitude: every prefilter, re-seed and start skip already
changes which positions fire. So the decline is needed only if a callout's ANSWER may depend
on what it observed at other fires, through state it mutates. With Q2's purity contract
(answers are a function of what `rx_ctx` carries; side effects observe an unspecified fire
sequence), callouts are as safe for split as for every shipped start optimization. Verbs
(`(*COMMIT)` and kin) genuinely cross attempts and stay declined. Population is 0 either
way until module `callouts` builds, so nothing moves at B4. B2 should word the column as
"observes or changes the attempt sequence" so a ruling can relabel callouts without
renaming it.

## 11. Questions for Frank (discussion: problem, forces, leaning)

**Q1. The budget unit across a composition.** *Problem:* today every callee starts a fresh
budget. For a compound that multiplies the caller's budget by up to the number of parts;
for callouts the total is unbounded (fires × budget). *Forces:* one meter per exported call
makes `--step-budget` mean what a caller reads it to mean, and gives D158 one comparison
unit (compound versus plain). But it lets a compound give up where a fresh-per-part
compound would have answered, which B6's give-up differential must then show it never does
on a cell where the plain artifact answers. The fresh form needs a ×k sentence in the spec
beside the tiered default's ×2, and callouts cannot have one. *Leaning:* one meter per
exported call, carried by the session for callouts and by an internal pointer for parts.
It is decided before B6, since B4's parts are DFA-only with no budget. It is
[EFFORT-BUDGET]'s scope question, not its unit question.

**Q2. Callout purity.** *Problem:* the compound declines callouts (A3) because they might
observe attempt order. Every shipped start optimization changes the fire sequence too, and
D36 already calls fire points engine-relative. *Forces:* a contract that a callout's RETURN
depends only on what `rx_ctx` carries (subject, pos, captures-so-far, vars, and the state
`user` points to, read but not mutated in answer-affecting ways) lets every optimization,
the compound included, treat a callout as a predicate. A callout that counts fires still
works, but sees an unspecified sequence (PCRE2's own position under start optimizations).
Without the contract, A3 is right, and so is a decline on every prefilter for callout
patterns, which D36 did not intend. *Leaning:* adopt the purity contract in the callouts
spec when step 2 builds, and leave A3 declining until then (population 0).

**Q3. `PCREC_ERR_INTERNAL` from a callee: propagate or trap?** *Problem:* §4¶10 traps on
it at a composed call site; a top-level entry propagates it. *Forces:* INTERNAL means the
callee caught its own analysis disagreeing. The outer then has no correct answer, but the
VM already carries `R_INTERNAL` outward from its own lookbehind check, so propagating costs
no new plumbing, and the caller gets a code instead of a crash. The trap was chosen when
INTERNAL was "the first producer of the abort space". Since then UTF, STARTPOS and
UNSET_VAR have shown that the space below the floor holds REFUSALS that propagate.
*Leaning:* propagate (row 4 of §5.2), and keep the trap for STARTPOS (the caller's own
invariant broken) and for the unassigned space. No artifact moves today. If Frank prefers
the trap, row 4 flips and nothing else changes.

## 12. The three standing questions (`docs/design/CLAUDE.md`)

1. **Measurement regime — NOT RELEVANT, with one flag.** The note measures nothing. Its two
   cost claims (O(n²) re-validation per callout fire, §10.2; search-filter `_match` per
   fire, §10.3) are DERIVED from the spec's text and J-2's measured K106 cell. They become
   measurements at U1/U2's triggers, in the counted-loads regime `compound.md` §B.5 uses.
2. **Independent control — RELEVANT for the checks proposed.** §5.2's table: its expected
   rows per part come from the part's STAMPS (engine, guard, `-futf-check` arm) read off
   the part's own compile, never from the table-emitter's own decision. A check compares
   the emitted rows against that projection. The plant is CMP-12 (a guarded part makes row
   6 reachable). §6.4's slot-coverage check: its expected set is `1..ncaps-1` from the
   plain artifact's `<PREFIX>_NCAPS`, not from the map it checks. §8.3's table: its
   population is the tree's `-p` uses, counted by grep (K35).
3. **What moves when data is regenerated — NOT RELEVANT here; the events are listed.** No
   table or calibration. The changes land as abi events at their own steps: B4 (already
   the compound's event; the trap line and the namespace table add no other mover), callouts
   step 2 or [IFACE-PUSH] (the `rx_callout_ref` fields and `rx_ctx.session` change the
   shared block, so every artifact moves; readers found by grep per D94). B6 (the meter
   parameter on part entries) moves only admitted compounds.

## 13. Unlocks (each with its trigger)

- **U1. One-attempt match-here on every attempt route** (§10.3). `_match` stops skimming the
  subject on a failing probe, for compounds and plain artifacts alike. *Trigger:* the first
  callout call site that binds a pcrec artifact on an attempt route, or a bench match-here
  cell on a `^`/`\G` pattern. An abi mover on attempt-route artifacts.
- **U2. A call chain validates once** (§10.2). *Trigger:* the first `-futf-check` artifact
  bound as a callout.
- **U3. A callout to a KNOWN pattern lowers to a part.** When a `.rxt` source binds a
  callout to another target in the same source, the compiler can bind it at compile time,
  as a compound part, instead of at link time. The callee is then inlinable, shares the
  captures array by map, needs one prologue and charges one meter. The binding-time
  column of §2 becomes a compiler choice. *Trigger:* a `.rxt` source with such a binding
  and a bench cell that measures the indirect call.
- **U4. Lift A3 for callouts** under Q2's purity contract (§10.5). *Trigger:* callouts
  step 2 and Q2 ruled.
- **U5. Slot seeding from `ctx->caps`** (§6.2): one engine capability that serves client
  7's B-reads-A and a callout predicate on captures-so-far (`(\d+)(?C"gt100")`).
  *Trigger:* client 7's own trigger, or callouts step 2, whichever comes first.
- **U6. The compound type check admits external callees** (§4): a combinator over a part
  and a callout-bound artifact (e.g. `locate-then-finish(Q; external verifier)`).
  *Trigger:* a client whose finisher is not pcrec-compiled.

## 14. Summary for the B4 brief and the cpb02 lane

### 14.1 Must change in `compound.md` before B4

1. **§B.2 / §A.2:** the controller's handling of a part's return follows §5.2's table. B4
   emits rows 1, 2 and 8 (the dead trap under each part call). `first-nonzero`'s "final"
   is restated as the table's propagate rows. The `match_api.md` §4¶10 spec hunk lands in
   B4's commit (first producer), with row 4 per Q3.
2. **§A.1:** `CompPart` gains `groups` (the D163 add. 3 map). Split states identity for F
   and Q. The pad rule and a slot-coverage table check are read off it.
3. **§A.5 / §G Q2:** the `__` refusal is row 1 of the namespace reservation table (§8.3),
   not a standalone check.

Text-only, at the same revision: §A.2 accepts a `verify-at`-typed external callee (§4);
§A.9 marks fresh-per-part INTERIM, decided at B6 by Q1; §B.8 words A3's callout clause as
conservative pending Q2; §C points at §9's owned region; §A.7 notes the link-level kind.

### 14.2 Changes to the callout design and spec

- `design_callout_abi.md`: an appended alignment block (house style). F2's trap becomes
  row 8 of the shared table, and INTERNAL propagates (Q3). D38 item 5's v2 is re-specified
  as a capture-delivering function plus a map on `rx_callout_ref`, withdrawing the
  non-const `rx_ctx` (§6.3). Callees charge the outer meter (Q1). The purity contract (Q2).
  The `rx_callout` namespace row (§8.3). The link-level `rx_info` list (§10.1). U1/U2 as
  its known cost hazards.
- `match_api.md` §4¶10: becomes §5.2's table **in B4's commit**. Nothing else in the spec
  moves until callouts build or [IFACE-PUSH] opens.
- [IFACE-PUSH] gains, in its existing `rx_ctx` event: `session` with the shared/owned split
  (§9), and the D38.3 re-ruling needed by [EMIT-ENTRIES]' public request (§8.2).

### 14.3 B0-B2 (lane `cpb02`, being built now)

- **B0: no conflict.** Keep the default as "every entry exported" (D38.3). Do not model
  callout bindings in the entry table (they are external references). Never classify an
  undefined reference as omittable.
- **B1 (soft, cheap now):** build `CompPart` with the `groups` field (identity for split's
  two parts), so B4 does not re-touch every row. Build `PB_ONE_ATTEMPT` as a general
  emission option (BOUND row `attempt-gstart`'s payload), with part mode as its first
  reader and no part-mode-only coupling (U1).
- **B2 (soft):** word `RF_CROSSES_ATTEMPTS` as "observes or changes the attempt sequence";
  mark the verb rows and the callout rows, and keep the two groups distinguishable so Q2
  can relabel callouts.
