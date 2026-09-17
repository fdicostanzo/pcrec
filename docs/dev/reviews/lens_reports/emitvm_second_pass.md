# `src/gen/emit_vm.c` — THE SECOND PASS: THE INTERIOR MAP

Lane `emitpass2` (opus, read-only; nothing under `src/`, `cli/`, `lib/`,
`tests/`). Chartered by `code_review_criteria_draft.md`'s budget note (*"lens 1
and lens 4 may charter a second pass over the emitters if their first pass
names the need"*) after lens 1 §4 item 1 named it: *"the single largest
unreviewed surface in the primary tier … **I am naming the need.**"* Lens 10
§4.3 then put it on wave 1's critical path, because stage 3 works exactly
where lens 1 stopped.

Everything numeric below was re-derived by this lane at `7d444f9e` from the
file itself and from `tests/mech/sabotages/`, never copied from another lens
report; the six scripts that produce it are archived at
`emitvm_evidence/` (own CLAUDE.md) so every table here regenerates at a later
commit. Where a number disagrees with a prior report, the disagreement is
stated and the instrument difference named — lens 10 §2.4's warning that
"every buffer count differs by instrument" turned out to apply to the anchor
counts too.

---

## 0. THE HEADLINE — five things, in descending order of what they change

1. **All 94 anchors are located, and the re-aim cost model is the opposite of
   what the wave plans assume.** `tests/mech/lib/replace.py` matches
   `SAB_BEFORE` with a **whole-file, line-agnostic `content.count(before)`** —
   so a VERBATIM same-file relocation costs **zero** re-aims, and only a text
   CHANGE breaks an anchor. But **92 of the 94 anchors carry leading
   whitespace**, so any extraction that RE-INDENTS its moved block breaks every
   anchor inside it. Extraction cost is therefore not "how much code moves"
   but "does the moved text keep its column." §3.4 gives the per-candidate
   count; the three cheapest extracts have **zero anchors inside them**.

2. **The buffer population is 58, not 40, and the missing 18 are in a THIRD
   sizing category no instrument has counted.** Five buffers are sized
   `DERIVED_CONSTANT + literal margin` (`PCREC_MAX_EMIT_NAME_LEN + 64`,
   `PCREC_DFA_OVERFLOW_WHY_LEN + 160`) and thirteen by the bare
   `PCREC_MAX_EMIT_NAME_LEN`. Lens 10's stage-3 acceptance criterion — *"zero
   literal-sized `char NAME[…]` scratch buffers remain"* — would be **satisfied
   with category (c) untouched**, which is the K35 shape the criterion was
   written to avoid. §4.

3. **`vm_slot_expr` already IS the extract for the densest buffer cluster, and
   its own header comment says the sites that ignore it are the defect.** The
   helper at `:940` says it exists *"so every site that names a slot inside an
   emitted expression spells it the same way … the alternative is each site
   re-deriving `<PREFIX>_` + `vm_slot_name`, which is three spellings of one
   convention."* Four sites in `vm_call`/`vm_splice` do exactly that, by hand,
   and one more helper (`slot_values[…]` around it) retires **8 of the 40**
   literal-sized buffers with zero anchors touched. This is an A2-clean
   abstraction the file has already named. §2.1, E1.

4. **Lens 11's F1 undercounts its own headline and its three proposed
   signatures are wrong in one load-bearing way.** The true figure is **29
   distinct sabotage rows / 32 anchor records** inside `pcrec_emit_vm`, not 26
   (lens 11's own drift warning, met from inside). And
   `vm_build_region_saves` cannot take `(Vm *, Ast *, int nstate)` — it reads
   `snap_before[]`/`snap_after[]`, produced by the *interleaved* counting pass
   between the two regions lens 11's table treats as contiguous. §3.2, §3.3.

5. **The non-emitting passes cannot go to `src/opt/` and a ruled record says
   so.** `src/core/internal.h:5412-5418` rules the nullability fixpoint into
   the emitter *because its recurrence `vm_nullable` is emitter-`static`*, and
   `vm_nullable` has **10 call sites across four layers** of this file. The
   correct home is file-static helpers in `emit_vm.c` (which is what lens 11
   actually proposed) or a sibling TU behind a private header — never
   `src/opt/`, which would have to export the `Vm` struct. §3.1 (A1).

---

## 1. THE LAYER MAP (deliverable 1)

The file has fifteen layers. The boundaries are the file's OWN banner comments
(`grep -n '^/\* ----' src/gen/emit_vm.c`) joined against the 100 census rows
for `emit_vm.c` in `worktrees/revtools/tools/review/out/function_census.tsv`
(A5). `code` is the census's summed `code_lines`; `anch` counts anchor RECORDS
(not distinct rows — §3.4 separates them); `bufs` counts literal-sized
declaration STATEMENTS (§4's category (a)).

| layer | span | lines | code | fns | anch | bufs | emits text? |
|---|---|---:|---:|---:|---:|---:|---|
| **L0** file header, capacity defaults, encoding-seam ids | 1-233 | 233 | 0 | 0 | 1 | 0 | no |
| **L1** emitter state: `VEvent`, `Cost`, the rung/strat ladders, `Vm` (`:372-735`), `vm_ev`/`vm_rolef`/`vm_label`/`vm_charge` | 234-779 | 546 | 37 | 4 | 0 | 1 | no |
| **L2** slot layout + slot naming (`vm_slot_*`, `vm_look_needs_*`, `vm_marked`) | 780-1078 | 299 | 126 | 14 | 0 | 1 | names only |
| **L3** AST predicates + the class pool (`vm_nullable`, `vm_lifts`, `vm_cuts`, `vm_cls*`) | 1079-1536 | 458 | 123 | 11 | 7 | 0 | `vm_cls_test` only |
| **L4** rung-fitness analysis (`vm_det_seq`, `vm_cap_offsets`, `vm_cursor_fits`, `vm_rev_caps`) | 1537-1842 | 306 | 103 | 5 | 0 | 0 | no |
| **L5** cost + slot counting (`vm_cost_rep`, `vm_cost`, `vm_count_slots`) | 1843-2915 | 1073 | 329 | 3 | 6 | 0 | **no** |
| **L6** the emission primitives + MRL (`vm_lbl`…`vm_cut`, `vm_mrl_*`, `vm_emit_f/fd`) | 2916-3278 | 363 | 159 | 19 | 1 | 2 | **yes — the kit** |
| **L7** the alternation-island rung (`vm_isl_*`) | 3279-3963 | 685 | 312 | 9 | 0 | 1 | build: no; `vm_isl_emit`: yes |
| **L8** the rung emitters (`vm_alt`, `vm_cursor_rep`, `vm_rev_emit`, `vm_revdet_rep`, `vm_counter_*`, `vm_star`, `vm_rep`, `vm_atomic`, the chains) | 3964-6003 | 2040 | **951** | 14 | 14 | 8 | yes |
| **L9** lookaround (`vm_look_behind`, `vm_look`) | 6004-6547 | 544 | 173 | 2 | 14 | 1 | yes |
| **L10** subroutines: the four walks, `W`, `vm_call`, `vm_splice`, `vm_region` | 6548-7128 | 581 | 252 | 9 | 10 | 9 | walks: no; the rest: yes |
| **L11** the dispatcher (`vm_emit`) | 7129-7644 | 516 | 211 | 1 | 9 | 3 | yes |
| **L12** the LISTING (`vm_render_listing` + three describers) | 7645-8278 | 634 | 345 | 4 | 0 | 6 | yes — **a different stream** |
| **L13** frame/trail layout + `vm_emit_default_entry` | 8279-8538 | 260 | 82 | 6 | 0 | 0 | layout: no; entry: yes |
| **L14** `pcrec_emit_vm` | 8539-11575 | 3037 | **778** | 1 | 32 | 8 | mixed — §3 |
| | | **11,575** | **3,981** | **100** | **94** | **40** | |

**Entry points.** The file has exactly one external entry,
`pcrec_emit_vm(Ctx *, Ast *root)` (L14), declared at `src/core/internal.h:5419`.
Everything else is `static`. L14 calls, in order: L3/L4/L5's analyses, L2's
layout, L10's walks, L11's dispatcher (which fans out into L6-L10), L13's
layout helpers, and L12's listing.

**Three facts the table makes visible that prose had not.**

- **`emit_vm.c` is 34.4% code.** 3,981 code lines in 11,575 file lines. That
  is the file-wide form of lens 11's per-function `ratio` column, and it is
  why a line count is a poor proxy for the work in any wave brief here.
- **L5 is the largest non-emitting block in the file and is not
  `pcrec_emit_vm`.** 1,073 lines / 329 code lines of pure analysis, in three
  functions that emit not one byte (verified: zero `sb_*` calls and zero
  L6-primitive calls in `vm_cost_rep`, `vm_cost`, `vm_count_slots`). Lens 11's
  F1 correctly says ~30% of `pcrec_emit_vm` emits nothing; the file's answer to
  "where is the analysis" is L5 first, L14's interior second. **A wave that
  frames the file as "an emitter with some analysis stuck in one function" has
  the proportions wrong.**
- **L12 writes a different output stream.** `vm_render_listing(v, o, st)` is
  called once, at `:11557`, with `&job->irsb` — the `--emit-ir` listing, not
  the C artifact. Every byte-neutrality argument in lens 10's stage 3 is
  stated over the `.c` artifact and the four identity gates that compare it;
  **none of those gates sees `irsb`**, whose comparator is
  `tests/codegen/run_ir_listing.sh`. Any stage touching L12's six buffers owes
  that arm explicitly. §5 carries it.

---

## 2. EXTRACTION VERDICTS (deliverable 2)

### 2.1 Which of lens 1's X1-X12 reach into the interior

| extract | reaches the interior? | sites |
|---|---|---|
| **X1** whole-tree AST walk | **YES, and materially** — §2.2 | 6 iterative spine walks: `vm_nullable` `:1167`, `vm_rev_caps` `:1781`, `vm_grp_set` `:6615`, `vm_w_caps` `:6649`, `vm_publish_nonnull` `:6688`, `vm_publish_saves` `:6719` |
| **X3** saturating arithmetic | **partly** — `vm_fadd` `:3136` / `vm_fmul` `:3143` are this file's copies, and they are NOT identical to the other two (they saturate at `PCREC_MINW_MAX` for a stated follow-min reason). Lens 1 already took them. | 2 |
| **X8** stamp emission | **confirmed EXACT** — 52 `"#define %s_` format literals, **all 52 at line ≥ 8539**, i.e. all inside `pcrec_emit_vm`, 36 of them through `sb_printf(c, …)`. Lens 11's join figure reproduces to the digit. | 52 |
| X2, X4, X5, X6, X7, X9, X10, X11, X12 | **no reach** into L6-L13 | — |

X1 is the only lens 1 extract with real interior reach, and §2.2 narrows it to
two callbacks rather than one.

### 2.2 E0 — X1 at the L10 walk cluster: TWO edge policies, not one

**Severity MAINTAINABILITY. Effort MECHANICAL. Blast radius: 1 file, 1 anchor
re-aim (S149), 0 abi.**

The four walks at `:6613-6748` are, modulo one arm each, the same 28-line
`for(;;) { switch (a->k) }` spine walker. They split into **two pairs with
genuinely different edge policies**, and merging across the pairs would be a
bug:

| | `A_CALL` | `A_CAP` | signature |
|---|---|---|---|
| `vm_grp_set`, `vm_w_caps` | **stop-leaf** (returns) | **act, then descend** | `const Ast *` |
| `vm_publish_nonnull`, `vm_publish_saves` | **act-leaf** (acts, then returns) | plain descend | `Ast *` (mutating) |

```c
/* Two walkers, not one: the A_CALL edge policy differs and the constness does. */
static void vm_walk_caps (Vm *v, const Ast *a, void (*on_cap )(Vm *, int g,     void *), void *u);
static void vm_walk_calls(Vm *v,       Ast *a, void (*on_call)(Vm *, Ast *call, void *), void *u);
```

Each collapses two 28-line bodies into one 20-line walker plus a 4-to-14-line
callback — roughly 30 lines net, which is not the point. **The point is that
the `A_CALL` stop rule is stated once.** `src/opt/callgraph.c`'s header
records that following `.body` from a bare walker *"hangs the COMPILER"* on
`(a(?1))`; today that rule is spelled four times, and the two spellings that
get it right by RETURNING at `A_CALL` and the two that get it right by
ACTING-then-returning look, to a future editor, like the same rule.

**Anti-perversion note carried with it:** `vm_grp_set` and `vm_w_caps` answer
in GROUP indices and SLOT indices respectively, and the file's comment at
`:6603-6612` explains why they are separate (*"a SPLICE has to know the SIZE
of its save block before [the counting] pass runs … Same walk, same stopping
rule, one level earlier"*). **The verdict merges the TRAVERSAL and keeps both
VERDICTS** — exactly lens 1's X1 framing and exactly what its §5 `atomic.c`
warning says not to over-cut.

**A3:** `S149_w_drops_pending` anchors at `:6659`, inside `vm_w_caps`'s
`A_CAP` arm — the text that becomes the callback body. Its four lines would be
re-indented, so **1 re-aim**, intent re-verified per `BOILERPLATE.md`.

### 2.3 NEW extracts that exist ONLY here

#### **E1 — the slot reference: four hand-rolled copies of a helper the file already declares**

**Severity MAINTAINABILITY (the file's own comment calls it a defect class).
Effort MECHANICAL. Blast radius: 1 file, **0 anchors inside**, 2 abutting, 0
abi (byte-neutral by construction).**

`vm_slot_expr` (`:940-951`) renders a slot as `<PREFIX>_SLOT_NAME` or the bare
number, and its header states the rule: *"One helper, so every site that names
a slot inside an emitted expression spells it the same way `vm_set` does — the
alternative is each site re-deriving `<PREFIX>_` + `vm_slot_name`, which is
three spellings of one convention."* It has five callers (`:6423`, `:6535`,
`:7402`, `:7517`, `:7518`).

**Four sites re-derive it by hand anyway**, each six lines, each with its own
pair of buffers, each wrapping the result in `slot_values[…]`:

| site | function | what it saves/restores |
|---|---|---|
| `:6818-6825` | `vm_call` | the call's `W` save block |
| `:6942-6949` | `vm_splice` | the splice's own save block |
| `:7009-7020` | `vm_splice` | the DELIVER copy (both halves of a pair) |
| `:7023-7031` | `vm_splice` | the restore |

All four are byte-identical modulo the slot expression handed in:

```c
char val[160];
char nm[48];
if (vm_slot_name(v, SLOT, nm, sizeof nm))
    snprintf(val, sizeof val, "slot_values[%s_%s]", v->up, nm);
else
    snprintf(val, sizeof val, "slot_values[%d]", SLOT);
```

**The abstraction (A2):**

```c
/* The slot as an emitted LVALUE — `vm_slot_expr`'s sibling, one bracket out.
   Arena-owned so no caller sizes a buffer; `slot_values[%s_%s]` is the only
   spelling. */
static const char *vm_slot_ref(Vm *v, int slot);
```

Returning arena-owned text (`vm_rolef`'s existing mechanism) rather than
filling a caller buffer is what makes this **retire 8 of the 40 category-(a)
buffers in one edit** — `val[160]`/`nm[48]` at `:6818/6819`, `:6942/6943`,
`:7009/7010`, `:7023/7024` — which is 20% of stage 3's whole population for a
change with no anchors inside it.

**A3:** zero anchors lie inside the four blocks (verified by range, §3.4).
`S147_call_zeroes_env` (`:6827`) abuts the first block and
`S173_splice_shares_exit` (`:6969`) abuts the second; per lens 10's stage-3
discipline, an abutting anchor is **re-verified, not assumed**, but neither
quotes a moved line.

**abi: not an event.** The emitted text is identical by construction (same
format, same arguments); the four standing identity gates are the proof.

#### **E2 — the emitted span scan, written twice (lens 11's F12, CONFIRMED with a signature correction)**

**Severity MAINTAINABILITY. Effort MECHANICAL. Blast radius: 1 file, 0 anchors
inside, 0 abi.**

I verified F12 against the source rather than inheriting it. `:4151-4158`
(possessive arm) and `:4295-4303` (greedy arm) emit the same eight-line
fragment. F12's claim holds.

**The correction: F12's proposed signature cannot express the greedy arm.**
The greedy arm emits **one extra line inside the block it opens** —

```c
if (fold)
    sb_printf(b, "        const size_t lim_ = %s_PRUNE_CLAMP_SPAN(scan_position, %s, %d);\n",
              v->up, vm_mrl_amt(v, mrl), stride);
```

— and `lim_` is the very identifier the shared `while` bound then names. A
`(…, const char *test, const char *bound)` helper opens the `{` before the
caller can emit the declaration, so the declaration has to travel with it:

```c
/* Emit the artifact's bounded span scan. `clamp` is the MRL amount when the
   bound is the folded window (which declares `lim_` inside the block), or
   NULL for the unclamped `subject_length` form. */
static void vm_emit_span_scan(Vm *v, const Ast *a, int stride,
                              const char *test, const char *clamp);
```

F12's underlying argument is right and is the reason to take it: two writers
of one emitted fragment, 140 lines apart, **with no agreement check** — where
`k49fix` §2.3's twice-spelled boundary rule was allowed to ship only because
it shipped an extractor that compares the two.

#### **E3 — `{m,n}` rendered four times, three spellings**

**Severity POLISH. Effort MECHANICAL. Blast radius: 1 file, 0 anchors, 0 abi;
retires 3 category-(a) buffers.**

The quantifier's bound text is rendered at four sites:

| site | function | form |
|---|---|---|
| `:4105-4107` | `vm_cursor_rep` | `char bounds[32]`, unbounded arm first |
| `:4862-4864` | `vm_revdet_rep` | `char bounds[32]`, unbounded arm first |
| `:5761-5764` | `vm_rep` | `char fbounds[32]`, **bounded arm first** |
| `:5506`/`:5510` | `vm_counter_rep` | **inline in two `vm_rolef` format strings**, no buffer |

One arena-returning helper (`static const char *vm_bounds_text(Vm *, const
Ast *)`) serves all four and retires `bounds[32]`, `bounds[32]`,
`fbounds[32]`. This is role/listing text only — it reaches the `.c` artifact
solely through `vm_lbl`'s `// %s` line comment and reaches `irsb` through the
listing, so **both byte-streams must be compared**, not just the `.c` one.

### 2.4 THE RUNG QUESTION — is the repetition loopable? (per family, with evidence)

The brief asks whether rung emission is loopable per lens 11 Q4 or whether
each rung is genuinely distinct. **Judged per family, the answer is: the rung
FAMILIES are distinct and must not be unified; the repetition is INSIDE two of
them and is E2/E3's, already taken.**

| family | functions | code | verdict |
|---|---|---:|---|
| cursor (span-loop) | `vm_cursor_rep` | 177 | **distinct.** Emits a bounded byte scan with no frame per iteration. E2 takes its one internal duplication. |
| reverse-deterministic | `vm_rev_emit`, `vm_revdet_rep` | 280 | **distinct.** Emits a forward scan plus a BACKWARD capture-recovery walk — a different emitted program, not a parameterisation. No shared fragment with cursor above four lines. |
| counter-K | `vm_counter_phase`, `vm_counter_poss_opt`, `vm_counter_rep` | 224 | **distinct, and already decomposed** into mandatory phase / possessive optional phase / composition — which is the loop-and-compose shape Q4 asks for, done. |
| frames | `vm_star`, `vm_rep`, `vm_opt_chain`, `vm_poss_chain`, `vm_poss_star` | 259 | **distinct, and already the most factored family in the file**: `vm_star` was extracted out of `vm_rep` (its banner at `:5605` says so), and the three chain emitters are the replication forms. |
| island | `vm_isl_*` (9 fns) | 312 | **distinct**, and it is analysis-heavy (`vm_isl_build` 54 code lines emits nothing; only `vm_isl_emit` writes). |
| lookaround | `vm_look`, `vm_look_behind` | 173 | **distinct.** `vm_look_behind`'s per-branch loop is lens 11's F14 and I concur; see §3.4 for its 4 anchors. |

**Why they cannot be table-driven (Q3).** A rung is not a parameter set over
one emitted skeleton — the rungs differ in *how many labels they mint*, *which
slot families they allocate*, *whether they push a frame at all*, and *what
the fail label restores*. `vm_cursor_rep` mints 2 labels and 1 slot;
`vm_revdet_rep` mints up to 12 labels and 3 slots; `vm_counter_phase` mints
its own set again. A table would have to carry the emitted control-flow graph,
at which point the table IS the code. **This is a case where question 3
answers "code-driven, correctly."**

### 2.5 THE DO-NOT-MERGE LIST (the anti-perversion half)

Five distinctions in the interior that read as duplication and are load-bearing.
Each cites the design note or in-file ruling that makes it so, per A1.

1. **`vm_cost_rep` / `vm_count_slots`'s `A_REP` arm / the rung emitters' own
   rung selection are THREE walks of one decision and must stay three.** The
   file says so at `:4046-4055`: *"vm_cost_rep and vm_count_slots carry the
   same branch; all three must agree or two live loops share one slot."* They
   run at three different times over three different products (a cost, a slot
   index, emitted text). A merged "decide the rung once" pass is a DESIGN-EVENT
   with a real argument behind it, not a cleanup — and it is not this review's
   to propose.

2. **The greedy and lazy arms of `vm_cursor_rep` share a shape and NOT an MRL
   rule.** The greedy arm FOLDS the clamp into the scan's own bound; the lazy
   arm uses the TEST form and *"needs NO LATTICE ROUNDING (§2.7, R26 V7)"*
   (`:4341-4355`). Unifying them would pay for a division the lazy arm does
   not need and would re-open R26 E1's off-lattice cursor.

3. **The possessive arm's MRL is deliberately the TEST form, never the
   clamp.** `:4193-4214`: clamping a possessified loop *"would manufacture a
   match neither the possessive nor the plain greedy semantics produces … MRL's
   soundness must not come to depend on possessify's, so it does not."*
   Ruled; do not unify with the greedy arm's clamp.

4. **`vm_grp_set` and `vm_w_caps` answer in different index spaces at
   different pass times** (`:6603-6612`). E0 merges their traversal and keeps
   both.

5. **`<PREFIX>_MRL_CAP` keeps a rounding the folded bound makes dead**
   (`:4272-4287`), as *"DEFENCE-IN-DEPTH FOR A FUTURE UN-FOLDING"*, and
   `run_mrl_tests.sh` cell 2 greps for the division *"so that this
   deliberately-dead defence cannot be quietly removed by a refactor that read
   'dead' as 'deletable'."* A wave will meet this and must not take it.

---

## 3. THE NON-EMITTING PASSES INSIDE `pcrec_emit_vm` (deliverable 3)

### 3.1 The home question, answered: NOT `src/opt/`, and a ruled record says so (A1)

The brief asks whether the fixpoints and the closure can move to `src/opt/` or
an `ir/`-adjacent home. **No, on two independent grounds:**

**(a) The ruled record.** `src/core/internal.h:5412-5418` reads:

> *"`Ast.u.call.nonnullable` is the graph fixpoint whose RECURRENCE
> (`vm_nullable`) is `static` to the emitter — see src/opt/callgraph.c's
> header for why the two fixpoints split across two files — so the emitter is
> the pass that WRITES it, and `save`/`nsave` are written there too because
> their values are SLOT INDICES that exist nowhere else."*

`src/opt/CLAUDE.md:95-98` states the other half: callgraph.c *"owns the GRAPH
both fixpoints iterate over, exported so the emitter does not re-derive 'which
groups are called and what does each reach'."* **The split is a ruled
decision with a stated reason, and a finding that moves either fixpoint across
it must argue against that reason explicitly or drop (A1).** I do not argue
against it: `vm_nullable` has **10 call sites spanning L3, L5 and L8**
(`:1291`, `:1298`, `:1352`, `:1995`, `:2170`, `:2909`, `:4593`, `:5622`,
`:8800`, plus its own recursion), three of them anchored (S107/S127/S156), so
moving the recurrence is a far larger change than moving the loop that drives it.

**(b) The struct.** All four candidates write into `Vm` — `rgn_emit`,
`rgn_grp`, `spl_nw`, `rgn_w`, `rgn_nw`, `rgn_cost` — and `Vm` is a file-local
`typedef struct {…} Vm;` at `:372-735`, 364 lines of emitter-private state
with no header declaration anywhere. Relocating to `src/opt/` means exporting
`Vm`, which is a much worse outcome than a long function.

**The realistic home is file-static helpers in `emit_vm.c`** — which is what
lens 11's F1 actually proposes (`static void vm_resolve_nonnull(Vm *v, …)`),
and what §5 stages. A sibling TU (`src/gen/emit_vm_plan.c`) behind a private
`emit_vm_priv.h` carrying `Vm` is a legitimate later option and is NOT
recommended for wave 1: it converts a text change into a build-graph change
and buys nothing the statics do not.

### 3.2 The four candidates, corrected — lens 11's region table merges two passes and separates one

Lens 11's F1 table treats `8539-9000` as one region and `9000-9189` as
another. Read at one nesting level, the interior is **four analyses separated
by an interleaved counting pass**, and the interleaving is what constrains the
seams:

| # | candidate | span | emits | what it closes over | seam |
|---|---|---|---|---|---|
| **P1** | the call-target **nullability fixpoint** | `:8792-8810` | nothing | `v.cg`, `v.nregion`, `root`; **mutates the AST** via `vm_publish_nonnull` (`a->u.call.nonnullable`) | `static void vm_resolve_nonnull(Vm *v, Ast *root)` — clean |
| **P2** | the **region-linkage flags + transitive GROUP set + `spl_nw`** | `:8826-8865` | nothing | `v.cg`, `v.ngroups`, `v.pend_of` (through `vm_marked`); writes `rgn_emit`, `has_linked_calls`, `rgn_grp`, `spl_nw` | `static void vm_plan_regions(Vm *v)` — clean, and **lens 11's table folds this into its 8539-9000 row without naming it** |
| — | `vm_count_slots` + the per-region snapshot passes | `:8867-8990` | nothing | — | **already a function**; produces `snap_before[]`/`snap_after[]` |
| **P3** | the **`W` save-set build**: per-region base sets, the seven per-copy family ranges, the transitive closure, the `spl_nw` agreement check, `vm_publish_saves` | `:9000-9150` | nothing | `v.cg`, `nstate`, `rgn_emit`, `spl_nw`, `rgn_grp`, **and `snap_before[]`/`snap_after[]`** | `static void vm_build_region_saves(Vm *v, Ast *root, int nstate, const VmSnap *before, const VmSnap *after)` |
| **P4** | the **region cost fixpoint** (cyclic targets settled first, then a readiness-ordered DAG evaluation) | `:9150-9186` | nothing | `v.cg`, `v.nregion`, `rgn_cost` | `static void vm_memo_region_costs(Vm *v)` — clean |

**The correction that matters.** Lens 11 proposes
`vm_build_region_saves(Vm *v, Ast *root, int nstate)`. That signature cannot
compile: `:9018-9037` reads `snap_before[i].guard`, `.low`, `.mark`, `.rev`,
`.ctr`, `.lookmark`, `.lookpos` and the matching `snap_after[i]` fields —
**seven family ranges per region, taken from the interleaved counting pass**,
which is `VmSnap`-typed local state in `pcrec_emit_vm`. The snapshots must be
parameters (or `Vm` fields, which is a data-flow change and should not ride a
text wave). **P3 is the one candidate whose seam is not free**, and a brief
that copies lens 11's signature will discover this at compile time rather than
at design time.

**Lens 11's `vm_plan_capacities` (its third proposal) is not in this list**
because `:9189-9405` is not an analysis in the same sense — it decides frame
and trail capacity, the step and work budgets and the tiered-entry rung,
consuming `vm_cost`'s result. It is extractable and I concur with extracting
it, but it is a policy block, not a fixpoint, and it carries **2 anchors**
(§3.4) where P1/P2/P4 carry zero.

### 3.3 Byte-neutrality: all four are byte-neutral, and here is the proof obligation

All four candidates move code that writes no text to `v->b` and no event to
`v->ev`. Verified by reading: zero `sb_*` calls and zero L6-primitive calls in
any of the four spans. **So none is an abi event** under D76/D94 — a
relocation that emits identically is not "emitted scaffolding changing."

Two caveats a wave must carry rather than assume:

- **P1 mutates the AST**, and the fixpoint's `nn[]` is iterated `nt+1` times
  with the final round asserted to change nothing (`:8804-8806`). An
  extraction that returns early on the settle round instead of asserting would
  silently delete the assertion. The `ctx_fail` at `:8806` is the assertion;
  it must travel.
- **P3 carries the `spl_nw` agreement `ctx_fail` (`:9138-9143`)**, which the
  file's own comment at `:9118-9137` marks as *"a SAME-SOURCE check [that]
  must not be read as anything more."* It exists because the `(?:(a{2,5}(?1)?b)((?1)c)){0}(?2)`
  bug was invisible to every bar in its own wave. It must travel, with its
  comment, and a reviewer should check that it did.

The proof that neutrality held is the pair lens 10 §3 stage 3 already
specifies — the four standing identity gates plus a full-corpus emit-diff on
`cmtfix_report.md`'s methodology — **plus, for anything touching L12, the
`irsb` arm** (§1's third fact).

### 3.4 THE ANCHOR MAP (the deliverable the wave briefs need)

**Method.** Every `S*.sh` in `tests/mech/sabotages/` was sourced; every
`SAB_FILE`/`SAB_FILE2` naming `emit_vm.c` yielded its `SAB_BEFORE` text; each
was located by exact string search in `src/gen/emit_vm.c` at `7d444f9e` and
mapped to a census function. **94 anchor records found, 0 NOT-FOUND, 0
straddling a candidate boundary.** Reproduction:
`emitvm_evidence/` (own CLAUDE.md) — `extract_anchors.sh` then
`locate_anchors.py`, `anchors_per_candidate.py`, `reindent_sensitivity.py`.

**Reconciling the three numbers in circulation, all of which are right at
their own resolution:**

| figure | value | what it counts |
|---|---:|---|
| this lane / the brief | **94** | anchor RECORDS in `emit_vm.c` (a row with `SAB_FILE2` here contributes 2) |
| lens 1 §4 item 1 | **85** | distinct sabotage ROWS with ≥1 anchor in the file — **reproduces exactly** |
| tree total | 261 files / 277 records | `emit_vm.c` holds **32.6%** of the tree's rows |

**Two rows straddle `pcrec_emit_vm` and another function** —
`S168_return_through_macro` (`:7117` in `vm_region` + `:10534`) and
`S217_has_push_npush_estimate_reverts` (`:2862` in `vm_count_slots` +
`:9689`). These are `SAB_FILE2` defence-in-depth pairs *within one file*, so a
wave touching either site re-aims one row at two places.

**Correction to lens 11 F1:** its *"26 sabotage rows attribute inside this
function — the densest anchor site in the tree, 10% of the whole
failing-direction net"* is an undercount. The measured figure is **29 distinct
rows / 32 anchor records**, i.e. **11.1%** of the 261 rows. Lens 11's own
drift warning ("counts are FLOORS") met from inside.

**Anchors per extraction candidate** (`inside` = the anchor's whole text lies
in the moved span, so a re-indent breaks it):

| candidate | span | anchors inside | which |
|---|---|---:|---|
| **E1a-d** slot-ref, 4 blocks | `:6818-6826`, `:6942-6950`, `:7009-7021`, `:7023-7032` | **0** | — (S147 `:6827`, S173 `:6969` ABUT) |
| **E2a/b** span scan | `:4151-4159`, `:4291-4304` | **0** | — |
| **E3a/b/c** bounds text | `:4105-4107`, `:4862-4864`, `:5761-5764` | **0** | — |
| **E0** the two walkers | `:6613-6748` | **1** | S149 |
| **P1** `vm_resolve_nonnull` | `:8790-8812` | **0** | — |
| **P2** `vm_plan_regions` | `:8824-8866` | **0** | — |
| **P3** `vm_build_region_saves` | `:9000-9188` | **6** | S148, S150, S151, S152 (×2), S153 |
| **P4** + `vm_plan_capacities` | `:9189-9405` | **2** | S41, S184 |
| **F7** `vm_wordb` arm | `:7312-7348` | **1** | S75 |
| **F7** `vm_cap` arm | `:7349-7415` | **2** | S103, S118 |
| **F7** `vm_bref` arm | `:7416-7555` | **5** | S105, S106, S109, S114, S115 |
| **F7** `vm_cat` arm | `:7557-7592` | **0** | — |
| **F7** `vm_count_slots` `A_LOOK` arm | `:2609-2709` | **0** | — |
| **F7** `vm_count_slots` `A_REP` arm | `:2777-2912` | **2** | S98, S217 |
| **F14** `vm_look_behind` branch loop | `:6315-6444` | **4** | S133, S134, S135 (×2) |
| **F8** `vm_render_listing` | `:7777-8277` | **0** | — |

**The `pcrec_emit_vm` emitting regions, for completeness** (nothing proposes
moving these; a brief needs the map anyway): prologue+stamps `:9405-10075` — 4
records (S217, S224, S225, S226, three of them on the one line `:9714`);
run-state+macros `:10075-10400` — 1 (S60); run-function preamble/reset/dispatch
`:10400-10770` — 6 (S89, S155, S168, S181, S182 ×2); trailers `:10770-10970` —
2 (S36, S144); search entry + retry `:10970-11310` — 6 (S63, S85, S88, S141
×2, S169); public entries/info/main `:11310-11575` — 3 (S179, S180, S183).

### 3.5 THE COST MODEL — the finding that should govern every wave brief here

`tests/mech/lib/replace.py` is the only thing that applies a sabotage. Its
match is:

```python
actual = content.count(before)
if actual != expected: … refuse
new_content = content.replace(before, after)
```

**Whole-file, plain-string, line-agnostic.** Three consequences:

1. **A verbatim relocation inside one file costs ZERO re-aims.** Moving a
   `switch` arm's body, a block, or a whole function to a different position
   in `emit_vm.c` does not break a single anchor **provided every byte of the
   moved text is unchanged**.
2. **Re-indentation is what costs.** **92 of the 94 anchors carry leading
   whitespace** (33 of 35 single-line anchors; 59 of 59 multi-line anchors have
   at least one continuation line with leading whitespace). Extracting a
   `case` arm from `switch`-depth to function-body depth dedents every line by
   four, so **every anchor in that arm breaks**. F7's `vm_bref` extraction is
   the worst instance: 5 re-aims for a purely mechanical move.
3. **Therefore the cheap extractions are the ones whose moved text becomes a
   new function BODY at the SAME indentation, or whose moved text has no
   anchors in it.** E1, E2, E3, P1, P2 all have zero anchors inside and are
   the correct wave-1 population on this criterion alone — which is a
   different ordering from "smallest diff first."

This is not a licence to preserve indentation artificially to game the
anchors. It is a costing rule: **price an extraction by the anchors whose TEXT
it changes, which my table gives per candidate, not by the lines it moves.**

---

## 4. THE BUFFERS (deliverable 4) — 58 declarations, in three sizing categories

Joined to the layer map. The population is larger than any prior instrument
reports, and the extra sites are in a category none of them matches.

| category | how it is spelled | statements | declarators |
|---|---|---:|---:|
| **(a)** bare integer literal — `char val[160]` | matched by lens 2, lens 3 F6, lens 10 | **40** | 45 |
| **(b)** bare `PCREC_MAX_EMIT_NAME_LEN` — the K38 family | counted separately by lens 10 (16) | 13 | **16** |
| **(c)** **derived constant + literal margin** | **matched by NO prior instrument** | **5** | 5 |
| | **total** | **58** | **66** |

**Reconciling lens 10 §2.4 exactly.** Lens 10 reports "40 `emit_vm.c`" for
category (a) and "16" for category (b). Both reproduce here — **but they are
counted at different resolutions**: 40 is DECLARATION STATEMENTS (category (a)
has 45 declarators, because `:4857`, `:7401`, `:7516`, `:7676` and `:10770`
declare two or three each) and 16 is DECLARATORS (category (b) has 13
statements). Lens 10 was right to warn that the instruments differ; the
difference turns out to be inside its own two numbers.

**Category (c), the five sites nobody has counted:**

| line | function | declaration |
|---|---|---|
| `:4989` | `vm_revdet_rep` | `char cnt[PCREC_MAX_EMIT_NAME_LEN + 64]` |
| `:5079` | `vm_revdet_rep` | `char pv[PCREC_MAX_EMIT_NAME_LEN + 32]` |
| `:5137` | `vm_revdet_rep` | `char cnt[PCREC_MAX_EMIT_NAME_LEN + 64]` |
| `:7800` | `vm_render_listing` | `char sel1_prefilter_reason[PCREC_DFA_OVERFLOW_WHY_LEN + 160]` |
| `:11381` | `pcrec_emit_vm` | `char mguard[PCREC_STARTPOS_GUARD_TEXT_MAX]` (a pure limits constant, no margin — the ONLY buffer in the file already sized by a governing limit) |

**The consequence for lens 10's stage-3 acceptance criterion.** It reads:
*"zero literal-sized `char NAME[…]` scratch buffers remain in
`src/gen/emit_vm.c` and `src/gen/emit_dfa.c` — a grep, checkable in both
directions, with a floor of 48 declarations at the branch point."* If the
grep behind it is the instrument that produced 40+8, **category (c) passes the
criterion untouched** — four hand-sized buffers with hand-computed margins
survive a stage whose stated deliverable is completeness. That is the K35
shape the criterion was explicitly written to avoid, one category over.
**Recommended repair: state the criterion over `char <ident>[` with ANY size
expression, excluding only `Vm.up` by name** (which lens 10 already scopes
out), and pin the floor at **58 declaration statements / 66 declarators** in
`emit_vm.c` rather than 40.

`:7800` deserves its own note as the file's best-documented buffer and the one
most likely to survive a sloppy migration: its comment computes the static
text at 142 bytes and calls +160 *"this file's own K38-precedent margin over
that worst case rather than a tight fit that reopens the next time either
string grows."* That is a correct answer to lens 3's F6 question — but it is
an answer for one site, which is why `sb_fragf` dissolving the question is
still the better outcome.

### Category (a)'s 40 statements, by layer (stage 3's work list)

| layer | lines |
|---|---|
| L1 | `:758` (`vm_rolef`) |
| L2 | `:946` (`vm_slot_expr`) |
| L6 | `:2984` (`vm_set`), `:3066` (`vm_cut`) |
| L7 | `:3836` (`vm_isl_die`) |
| **L8** | `:4078`, `:4105`, `:4176` (`vm_cursor_rep`); `:4857`, `:4862` (`vm_revdet_rep`); `:5345` (`vm_counter_phase`); `:5460` (`vm_counter_poss_opt`); `:5761` (`vm_rep`) — **8** |
| L9 | `:6379` (`vm_look_behind`) |
| **L10** | `:6818`, `:6819` (`vm_call`); `:6942`, `:6943`, `:7009`, `:7010`, `:7023`, `:7024` (`vm_splice`); `:7088` (`vm_region`) — **9, of which E1 retires 8** |
| L11 | `:7401`, `:7477`, `:7516` (`vm_emit`) |
| **L12** | `:7676` (`vm_cls_describe`); `:8003`, `:8156`, `:8167`, `:8200`, `:8215` (`vm_render_listing`) — **6, and these write `irsb`, not the `.c`** |
| **L14** | `:10033`, `:10377`, `:10383`, `:10594`, `:10770`, `:10870`, `:11118`, `:11127` — **8** |

Lens 10's §4.1 measurement (no fragment provably truncates at a 60-byte
prefix; tightest margin 9 bytes at `:10384`/`gst_param[96]`) is **not
re-derived here** and I take it as given; nothing I read contradicts it, and
the K38 comments at `:4094`, `:4200`, `:4358`, `:4672`, `:5027`, `:5095`
record the family that DID truncate and was fixed by widening rather than by
retiring the buffer.

---

## 5. THE RECOMMENDED SEQUENCE (deliverable 5)

Reconciling lens 11's four-commit order for `pcrec_emit_vm`, lens 10's
five-stage kit plan, and this pass's findings into one sequence for all
`emit_vm.c` work across every wave. Ordered by **anchors-inside ascending**
(§3.5's cost model), then by dependency.

| # | step | span | anchors inside | abi | depends on |
|---:|---|---|---:|---:|---|
| **0** | **lens 10 STAGE 0** — the long-prefix corpus control | no source | 0 | no | — |
| **1** | **E1** `vm_slot_ref`, 4 sites | L10 | **0** | no | 0 |
| **2** | **E2** `vm_emit_span_scan`, 2 sites | L8 | **0** | no | — |
| **3** | **E3** `vm_bounds_text`, 3 sites | L8 | **0** | no | — |
| **4** | **P1** `vm_resolve_nonnull` | L14 | **0** | no | — |
| **5** | **P2** `vm_plan_regions` | L14 | **0** | no | 4 |
| **6** | **E0** the two X1 walkers | L10 | **1** | no | 1 |
| **7** | **P4** `vm_memo_region_costs` | L14 | 0 | no | 5 |
| **8** | **P3** `vm_build_region_saves` (+ the snapshot parameters) | L14 | **6** | no | 5, 7 |
| **9** | **`vm_plan_capacities`** (lens 11's third) | L14 | **2** | no | 8 |
| **10** | **X8** the stamp pair, 52 sites | L14 | 4 abutting | **see below** | 1 (needs `sb_name`/`sb_upper`) |
| **11** | **lens 10 STAGE 3** — `sb_fragf` over the remaining buffers | all | 4 direct + blast | no | 1, 2, 3, 6 |
| **12** | **F7** `vm_wordb` / `vm_cap` / `vm_cat` / `vm_bref` | L11 | **8** (0/2/0/5 + S75) | no | 11 |
| **13** | **F7** `vm_count_slots`'s two fat arms | L5 | **2** | no | — |
| **14** | **F14** `vm_look_behind_branch` | L9 | **4** | no | — |
| **15** | **F8** `vm_render_listing`'s loops | L12 | **0** | no | 11 |

**Verdict on lens 11's four-commit order.** Its order is *(1) X8's stamp
helpers, (2) `vm_resolve_nonnull`, (3) `vm_build_region_saves`, (4)
`vm_plan_capacities`*. **Corrected in three places:**

- **X8 must NOT go first.** It is the only item in the whole sequence with an
  abi question attached (its 52 sites are the emitted `#define` text D94's
  ritual is about), and it depends on lens 10's `sb_name`/`sb_upper`
  substrate, which stage 3 delivers. Lens 10 §4.3 item 4 already flags X8 as
  *"the one item that should ride stage 3 rather than wait"* — that is the
  correct placement and it is step 10, not step 1.
- **P2 (`vm_plan_regions`) is missing from lens 11's order entirely**, folded
  invisibly into its `8539-9000` region row. It is a free, zero-anchor
  extraction and it must precede P3 and P4, which read its outputs.
- **P3 before P4 is wrong.** P4 (`vm_memo_region_costs`) is zero-anchor and
  depends only on P2; P3 is six-anchor and needs the snapshot parameters.
  Doing the cheap one first means a red in P3 bisects to P3 alone.

**Verdict on lens 10's stage plan.** Unchanged in order and in substance.
Steps 1-6 above all *precede* its stage 3 rather than competing with it, which
is exactly what §4.3's sequencing argument asks for (*"the second pass runs
BEFORE stage 3"*). Two additions this pass owes it:

- **Its acceptance criterion needs the category-(c) repair** (§4): the
  measured floor is 58 declarators, not 48 across both emitters.
- **Its byte-neutrality instrument needs the `irsb` arm** for anything
  touching L12 (§1). The four standing identity gates and the full-corpus
  emit-diff both compare the `.c` artifact; `tests/codegen/run_ir_listing.sh`
  is the only comparator for the listing, and six of stage 3's buffers write
  only to it.

**abi verdict, whole sequence: no step is an abi event except possibly step
10.** Every other step relocates code that emits byte-identical text. Step 10
converts 52 hand-typed `#define` format strings into helper calls; if the
helper reproduces each line byte for byte it is also not an event, but **that
is a claim to verify rather than assume**, and D94's own lesson (the
hand-enumerated "four sites" that was five) says the site list is found by
grep. For step 10 the grep is `"#define %s_` — 52 hits, all at line ≥ 8539,
re-derivable in one command.

---

## 6. PROBED AND HELD

Extractions and findings I examined and declined, so a later pass does not
re-find them and assume they were missed.

1. **Unifying the rung emitters into a table-driven emitter.** §2.4. Rungs
   differ in label count, slot families, frame discipline and fail-label
   semantics; the table would have to carry the emitted CFG. Question 3
   answers "correctly code-driven."
2. **Merging `vm_cost_rep` / `vm_count_slots`'s `A_REP` / the rung selection
   into one decision pass.** Real, and a DESIGN-EVENT with its own argument —
   the file's `:4046-4055` comment is aware of the triplication and states the
   invariant instead. Not a review finding.
3. **`vm_fadd`/`vm_fmul` (`:3136`, `:3143`) merging with the tree's other
   saturating helpers.** Lens 1's X3 already covers them, and they saturate at
   `PCREC_MINW_MAX` for the follow-min accumulator's own stated reason. No
   further finding here.
4. **`vm_emit_f` / `vm_emit_fd` (`:3155`, `:3165`) as one function with a
   defaulted argument.** Declined: `vm_emit_f`'s header says it is *"THE ONLY
   MUTATOR of `v->fmin`"* and `vm_emit_fd` additionally sets `v->fdyn` with
   one caller. Collapsing them makes the single-mutator claim harder to check,
   for six lines.
5. **Retiring `Vm.up[80]` (`:376`, ~110 readers).** Lens 10 explicitly scopes
   it out of wave 1 and gives the reason (a data-flow change through the
   central struct, with a different byte-neutrality argument). I concur and
   add: it is the file's 59th declaration (67th declarator), and it belongs in
   the same later wave as any `Vm` field change.
6. **`vm_emit`'s leaf arms (`A_CLASS`, `A_EMPTY`, `A_BOL`, `A_EOL`, `A_END`,
   `A_GSTART`) as extracted functions.** Declined: each is 4-20 lines and
   reads correctly as a dispatcher arm. F7's argument applies to the four FAT
   arms only, and lens 11 scoped it that way.
7. **`vm_isl_build` (`:3609`, 198 span / 54 code) as a candidate for the
   §3 treatment.** It emits nothing, so it looks like P1-P4's family — but it
   is already its own function with its own name, which is the whole remedy.
   No finding.
8. **The `L14` emitting regions as extraction candidates.** `:9405-11575` is
   1,170 span lines of prologue, stamps, macros, trailers and entries in the
   emitted file's own order. Lens 11's F1 says this is the shape
   `emit_attempt` and `emit_info_def` already have and that §5 passes them
   for; I agree and add the measurement: those regions hold **22 of the 32
   anchor records** in the function, so a speculative split there is the
   sequence's most expensive move for its least benefit.

---

## 7. WHERE I STOPPED (ADDENDUM 2)

**Reviewed in full for this pass:** the layer boundaries and census join for
all 100 functions; L2's slot-naming layer; L6's primitive kit; L8's
`vm_cursor_rep` and `vm_revdet_rep` in full and the other rung families at
banner + signature + census resolution; L10's four walks, `vm_call`,
`vm_splice` and `vm_region` in full; L11's dispatch arm inventory; L14's
`:8780-9190` in full; the whole buffer population; all 94 anchors.

**Named remainder, not reviewed at line level:**

1. **L7, the alternation island (`vm_isl_*`, 685 lines / 312 code, 9
   functions).** Zero anchors, which is itself worth a look — it is the only
   substantial layer in the file with no failing-direction coverage at all.
   I read its banners and `vm_isl_emit`'s emission surface and did not read
   `vm_isl_build`, `vm_isl_words` or the trie insert. **A zero-anchor,
   312-code-line layer is a gap somebody should price**, and it is a
   `tests/mech` question rather than a lens question.
2. **L12, `vm_render_listing`'s 288 code lines.** In lens 11's scope (F8) and
   I did not duplicate it; I add only the `irsb` stream fact (§1) and its six
   buffers (§4). F8's three-section/six-slot-loop claim is **not independently
   verified here**.
3. **L5's `vm_cost_rep` and `vm_count_slots` bodies** (241 code lines
   together). Read at arm-boundary resolution for F7's fat-arm list and for
   the do-not-merge finding; not read statement by statement.
4. **L9's `vm_look` (66 code lines).** Read at signature and anchor
   resolution only; `vm_look_behind` was read for F14.
5. **`emit_dfa.c`.** Out of this lane's scope by the brief. Lens 10's 8
   category-(a) buffers there are unverified by me, and **the category-(c)
   finding in §4 has not been run against it** — if `emit_dfa.c` has
   derived-constant-sized buffers too, stage 3's floor moves again.

**The one thing I would want measured before wave 1 starts** and did not
measure (no `make` allowed in this lane): whether the four standing identity
gates plus `run_ir_listing.sh` actually cover every layer a step in §5 touches.
§1's `irsb` finding says the `.c` gates do not reach L12; nobody has checked
the converse — whether `run_ir_listing.sh`'s population reaches L8's rung
emitters, whose `vm_rolef` role text is the listing's own content. That is one
`RXTDUMP`-style census, and it belongs in lens 10's stage 0 beside the
long-prefix control.
