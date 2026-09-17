# LENS 1 — SEMANTIC DUPLICATION / MISSING LIBRARIES

Lane `lens1dup` (opus, read-only review; nothing under `src/`, `cli/`,
`lib/`, `tests/` was written or run). Charter:
`docs/dev/reviews/code_review_criteria_draft.md`, lens 1 (Frank #1), under
the ratification addenda.

Scope: **PRIMARY tier only** — `src/`, `cli/`, `lib/`. Emitted C, the
`.rxt` corpus, `tests/`, `studies/` and `docs/` are out by the charter's
own exclusion; `tests/lib/`+`tests/harness/` are the secondary tier, next
round.

Metric artifacts cited per A5 (post-merge paths):
`tools/review/out/clone_candidates.tsv` (70 groups, 258 members) and
`tools/review/out/function_census.tsv` (860 functions, length-ranked).

---

## 0. THE HEADLINE, AND WHAT THE DETECTOR COULD NOT SAY

The clone detector's biggest group — group 1, 36 members — is not one
duplication. It is **every function in the tree that CONTAINS an AST
spine walk**, and `group_frac` is the giveaway: members run from 1.000
(`pcrec_has_atomic`, `pcrec_has_call`, `cg_walk`, `pcrec_minw` — functions
that are *nothing but* the idiom) down to 0.052 (`vm_cost`, 98 code-lines)
and 0.015 (`emit_attempt`, 201 code-lines), which merely have one instance
of it inside them. Winnowing groups on shared fingerprints, so a big
function that uses an idiom once joins the same group as a small function
that is the idiom.

That matters because the detector's 36 **under-counts the real
population**. Counted directly: `grep -c 'k == A_CAT'` over `src/ cli/
lib/` finds **75 hand-written spine-walk sites in 9 files**, and
`grep -c 'case A_CLASS:'` finds **48 exhaustive `AKind` switches across 16
files**. The duplication lens 1 is pointed at is the largest single
structure in this tree, and the detector saw roughly half of it.

The second headline is the one the detector cannot express at all: the
duplicated thing is not text, it is a **safety discipline**. Every one of
those 75 spine sites exists because a walk that recurses on an `A_CAT`
spine segfaults the compiler on a 20,000-character pattern (D10/DD-10/R1
R-2, and K20 — `src/opt/atomic.c:22-26` records that this has been learned
three times). Today that discipline is a copied idiom with a copied
comment. It is correct at all 75 sites as far as this review can see; it
is correct because 75 authors each remembered, not because anything makes
forgetting impossible.

---

## 1. RANKED EXTRACTS

Ranked by value per unit of risk, with A4's vocabulary stated per row.
X2, X3, X4, X7, X10, X12 are the MECHANICAL+safe band the synthesis wants
first; X1 and X9 are the DESIGN-EVENTs at the other end.

---

### X1 — the whole-tree AST walk: extract the TRAVERSAL, keep the VERDICT

**Severity: CORRECTNESS-RISK. Effort: CROSS-CUTTING (stageable). Blast
radius: 6 files, 6 sabotage rows, 3 codegen checks.**

**Evidence (A5):** `clone_candidates.tsv` group 1 (36 members, the 1.000
`group_frac` core listed below); `function_census.tsv` rows for each.
Direct census: 75 spine sites, 48 `AKind` switches.

**The shared operation.** Nine functions in `src/opt/atomic.c` alone, plus
`cg_walk`, `pr_walk`, `subtree_is_identity`, `lower_walk` and `dis_walk`,
are the same three-part program:

1. a per-kind classification — *hit / prune / descend* — which is the only
   thing that genuinely varies;
2. a fixed descent for the single-child kinds (`A_CAP`/`A_REP`/`A_ATOMIC`/
   `A_LOOK`) through `a->l`;
3. an **iterative** left-nested spine loop for `A_CAT`/`A_ALT` that
   recurses only into `->r`, plus a categorical refusal to follow
   `Ast.u.call.body` (the AST's only back edge — following it is a
   non-terminating compile on `(a(?1))`).

Parts 2 and 3 are identical at every site. Part 3 is the K20 discipline
and the `subroutines_design.md` §4.4 back-edge rule, and it is re-argued
in a fresh comment block at nearly every one of them.

**The tabulated variation** (this is what the abstraction has to carry):

| function | `A_LOOK` | `A_REP` | `A_ATOMIC` | `A_CAP` | `A_CALL` | `A_BREF` |
|---|---|---|---|---|---|---|
| `pcrec_has_atomic` | descend | descend | **HIT** | descend | stop | stop |
| `pcrec_has_lookaround` | **HIT** | descend | descend | descend | stop | stop |
| `pcrec_has_collapsible_rep` | **PRUNE** | test, descend | descend | descend | stop | stop |
| `pcrec_ast_stamped_by` | descend | descend | descend | descend | stop | stop |
| `pcrec_has_bref` | descend | descend | descend | descend | stop | **HIT** |
| `pcrec_bref_mark` | descend | descend | descend | descend | **mark** | **mark** |
| `pcrec_has_live_capture` | descend | **PRUNE if {0,0}** | descend | **HIT** | **cond** | stop |
| `pcrec_has_linked_call` | descend | descend | descend | descend | **cond** | stop |
| `pcrec_has_call` | descend | descend | descend | descend | **HIT** | stop |
| `cg_walk` | descend | descend | descend | descend | stop | stop |
| `pr_walk` | descend | descend | descend | descend | stop | stop |

The nine leaf kinds (`A_CLASS`, `A_EMPTY`, `A_BOL`, `A_EOL`, `A_END`,
`A_WORDB`, `A_NWORDB`, `A_GSTART`, `A_KRESET`) are **stop** in all eleven,
without exception.

**Proposed signature.**

```c
/* One traversal, in src/opt/astwalk.c (new), declared in core/internal.h. */
typedef enum { AW_STOP, AW_DESCEND, AW_HIT } AwVerdict;
typedef AwVerdict (*AwClassify)(const Ast *a, void *ud);

/* Pre-order whole-tree walk. Spines ITERATIVELY (D10/DD-10/K20), recursion
 * only into a spine element's `->r` and the spine head. NEVER follows
 * `u.call.body` (subroutines_design.md §4.4) — structurally, not by each
 * caller remembering. Returns true iff `classify` returned AW_HIT. */
bool pcrec_ast_walk(const Ast *root, AwClassify classify, void *ud);
```

**The A1 obstacle, and why the extraction survives it.**
`src/opt/atomic.c:28-36` states a rule this finding must answer: *"NONE OF
THE SEVEN SWITCHES IN THIS FILE CARRIES A `default:` — mrl.c:18-24's rule.
A node kind added after this file is written must be a COMPILE ERROR at
each of them, because 'can this construct contain a cut' ... are questions
only the author of the new kind can answer."* `src/parse/CLAUDE.md`,
`src/opt/mrl.c` and `src/opt/prefix_k.c` (citing R26 V7) all carry the
same rule. It is load-bearing and it is right.

**It is preserved exactly, and that is the whole reason for the
hit/prune/descend split.** The naive extraction — one generic walk taking
a `void visit(const Ast*)` callback — destroys the alarm: the callback
handles only the kinds it cares about, so a new `AKind` inherits silence
at every one of the eleven sites at once. The proposed shape does the
opposite: each predicate keeps **its own exhaustive `switch (a->k)` with
no `default:`**, returning an `AwVerdict` instead of performing the
descent. Eleven switches stay eleven switches, `-Wswitch` still fires at
every one of them under `make strict`, and what moves is only the part
that never varied. The obligation to *answer per kind per predicate* is
untouched; what is removed is the obligation to *re-implement K20 per
predicate*.

**A3 — check coupling.** Sabotage rows bind by `SAB_BEFORE`, an **exact
source-text snippet** with a pinned `SAB_COUNT`. Six rows have
`SAB_FILE="src/opt/atomic.c"`: **S91, S97, S104, S158, S159, S174**. Each
plants inside one of these walks, and at least one (S158) deliberately
includes the *following* `case A_CAT:` line in its `SAB_BEFORE` purely to
stay unique among the nine near-identical walks — so every one of the six
stales on this change and needs a re-aim with its intent re-verified
(BOILERPLATE's rule). Three `tests/codegen/` scripts reference `atomic.c`;
`tests/mech/sabotages/` additionally carries 5 rows on `callgraph.c` and 2
on `postresolve.c` whose walks this touches. **Worth noting in the
refactor's favour:** because each predicate keeps its own per-kind arm,
every one of the six rows remains *addressable* — the re-aims are
mechanical text updates, not row redesigns. Under the naive callback shape
they would not be: nine `A_CALL` arms collapsing into one would leave S158
with no distinct line to plant on.

**Staging.** Do not do this in one wave. X2 below is the zero-risk slice;
then the four pure existential predicates (`has_atomic`, `has_lookaround`,
`has_bref`, `has_call`, all `group_frac` 1.000, none of them carrying a
sabotage row); then the conditional ones; `pcrec_bref_mark` (void
accumulator) and `dis_walk` (a rewriting walk that returns a node) are
**different shapes** and should be judged separately rather than forced
into `pcrec_ast_walk`.

**Census join keys (for ADDENDUM 1 / lens 11):**
`src/opt/atomic.c` `pcrec_has_atomic` 49-107 (32L),
`pcrec_has_lookaround` 132-174 (31L), `pcrec_has_collapsible_rep` 203-246
(35L), `pcrec_ast_stamped_by` 267-312 (31L), `dis_walk` 402-490 (29L),
`pcrec_has_bref` 530-579 (31L), `pcrec_bref_mark` 596-667 (35L),
`pcrec_has_live_capture` 743-820 (36L), `pcrec_has_linked_call` 849-879
(30L), `pcrec_has_call` 881-912 (30L); `src/opt/callgraph.c` `cg_walk`
121-147 (24L); `src/opt/postresolve.c` `pr_walk` 92-122 (24L);
`src/opt/lower_enc.c` `subtree_is_identity` 463-496 (33L), `lower_walk`
503-566 (39L).

---

### X2 — `cg_walk` and `pr_walk` are edge-policy identical

**Severity: MAINTAINABILITY. Effort: MECHANICAL. Blast radius: 2 files, **2
sabotage rows re-aimed** (see below), 0 codegen checks, 0 emitted bytes.**

**Evidence (A5):** `clone_candidates.tsv` group 1, members
`src/opt/callgraph.c:cg_walk` (121-147, `group_frac` **1.000**) and
`src/opt/postresolve.c:pr_walk` (92-122, `group_frac` **1.000**) —
the only two members of that 36-function group that are *both* 1.000 *and*
generic visitors.

These two are the same function. Same kinds stop, same kinds descend
through `->l`, same `const AKind k = a->k; for (; t->k == k; t = t->l)
walk(t->r, f, ud);` spine loop, same `f(ud, a)` pre-order visit, same
`(void *ud, const Ast *)` callback signature. The differences are the
typedef name (`CgVisit` vs `PrVisit`), the recursive call's own name, and
the comment wording.

```c
/* In core/internal.h, replacing both: */
typedef void (*AstVisit)(void *ud, const Ast *a);
void pcrec_ast_visit(const Ast *root, AstVisit f, void *ud);
```

**A1 — this contradicts a ruled sentence, and here is the argument.**
`src/opt/CLAUDE.md`'s `postresolve.c` entry states: *"Its walk is its own
(the house style — `revdet.c`, `possessify.c`, `select_engine.c`,
`altcls.c` and `callgraph.c` each carry one, because what varies is which
edges they follow)."* The justification is a claim about variation, and it
is **true of the five files it names and false of the pair it was written
to justify**: `cg_walk` and `pr_walk` follow *the same edges*. The house
style is right wherever the edges differ — `altcls_walk` rebuilds,
`pss_walk` threads FOLLOW, `rd_walk` reverses — and those stay. The
sentence should be narrowed to say so rather than deleted, and the two
generic pre-order visitors merged. This is the cheapest true finding in
the report and it is also the pilot that de-risks X1.

**A3 — and this row is its own worked example of why the annex exists.**
My first reading of the blast radius was "zero checks": no sabotage row
plants *inside* `cg_walk`'s or `pr_walk`'s body. That reading was wrong.
Checking the seven rows that name these two files, **S-U10** and **S171**
(the `cwmin` and `cwmax` one-round fixpoint rows) each carry
`SAB_BEFORE='            cg_walk(root, cg_cwmin_publish, &m); ...'` — the
literal **call text**, function name included. So renaming `cg_walk` to a
shared `pcrec_ast_visit` stales both rows even though neither touches the
walk itself. Two mechanical re-aims, intent unchanged and trivially
re-verifiable. The transferable form for the whole refactor programme:
*a sabotage row binds to source TEXT, so a rename reaches every row that
happens to quote the caller, not only the rows that plant on the callee* —
and the population of those is found by grepping the identifier across
`tests/mech/sabotages/`, never by reasoning about which rows "are about"
the function.

---

### X3 — saturating arithmetic: one operation, three copies, two of them exactly identical

**Severity: CORRECTNESS-RISK. Effort: MECHANICAL. Blast radius: 3 files,
0 emitted bytes, **3 sabotage rows re-aimed** — S58, S59 and S-U4 each
quote `mrl_sat_add`/`mrl_sat_mul` by name in their `SAB_BEFORE` text
(found by identifier grep over `tests/mech/sabotages/`, per X2's own
lesson, not by reasoning about which rows are "about" the arithmetic).**

**Evidence (A5):** `clone_candidates.tsv` group 32 (`vm_fmul`,
`cg_sat_mul`, `mrl_sat_mul`; `vm_fmul` and `mrl_sat_mul` both
`group_frac` **1.000**).

Six functions, three files:

| | add | mul | ceiling |
|---|---|---|---|
| `src/opt/mrl.c` | `mrl_sat_add` 93-97 | `mrl_sat_mul` 99-104 | `MRL_MINW_MAX` |
| `src/gen/emit_vm.c` | `vm_fadd` 3136-3140 | `vm_fmul` 3143-3148 | `PCREC_MINW_MAX` |
| `src/opt/callgraph.c` | `cg_sat_add` 458-463 | `cg_sat_mul` 465-471 | `CG_EXP_INF` |

`src/opt/mrl.c:91` is `#define MRL_MINW_MAX PCREC_MINW_MAX`. **So
`mrl_sat_add` and `vm_fadd` are the same function after macro expansion,
and so are `mrl_sat_mul` and `vm_fmul`** — not "similar", identical.

This is filed as CORRECTNESS-RISK rather than MAINTAINABILITY on the
tree's own argument. `src/opt/CLAUDE.md`'s `mrl.c` entry: *"Arithmetic
saturates at `PCREC_MINW_MAX` (core/internal.h, **shared with the
emitter's accumulator so a long concatenation of saturated subtrees cannot
overflow past the ceiling that exists to prevent it**). A wrapped product
is not merely wrong, it is wrong in the UNSOUND direction whenever it
lands on a small positive value."* The tree states that the analysis and
the emitter must agree about this arithmetic, and then implements the
arithmetic twice. Nothing checks the agreement; today it holds by the two
bodies happening to be typed the same.

```c
/* In core/internal.h (header-inline, so no call-site cost changes): */
static inline long long pcrec_sat_add(long long a, long long b, long long cap);
static inline long long pcrec_sat_mul(long long a, long long b, long long cap);
```

**What varies per site:** the ceiling only — `PCREC_MINW_MAX` at four
sites, `CG_EXP_INF` at two. **One precondition a reviewer must discharge
before merging all six:** `cg_sat_add` carries an extra leading
`if (a >= CG_EXP_INF || b >= CG_EXP_INF) return CG_EXP_INF;` that the
`mrl`/`vm` pair does not. It *appears* redundant — both operands are
already clamped at 2^40, so the sum cannot approach `LLONG_MAX` and the
trailing clamp catches it — but "appears redundant" is how this project
loses things, and confirming it is the unification's precondition. If it
is not redundant, the shared helper takes the absorbing form and the
`mrl`/`vm` sites are *strengthened* by adopting it.

**A rider, for lens 3 rather than for this wave.** `CG_EXP_INF` is
`((long long)1 << 40)`, a file-local macro in `callgraph.c:456`.
`src/core/limits.def:358` declares `PCREC_MINW_MAX` as `(1LL << 40)`.
**Same value, two independent sources**, one of which is the ruled central
config. `callgraph.c`'s own comment justifies the constant as "above
`PCREC_MAX_SPLICE_NODES` so it is never mistaken for a passing size" — a
reason that does not require 2^40 specifically, which is what makes the
coincidence a drift hazard rather than a deliberate alias. Flagged here
because it surfaced from this family; the finding belongs to lens 3.

---

### X4 — arena string duplication: three private `strndup`s and no arena string library

**Severity: MAINTAINABILITY. Effort: MECHANICAL. Blast radius: 4 files, 0
checks (verified by identifier grep over `tests/mech/sabotages/` and
`tests/codegen/`: zero hits for all six function names), 0 emitted
bytes.**

**Evidence (A5):** `clone_candidates.tsv` group 33, all three members
`group_frac` **1.000**.

```
src/parse/mod_backrefs.c      br_strndup        141-147  (7L)
src/parse/mod_named_groups.c  ng_arena_strndup   76-82   (7L)
src/parse/mod_recursion.c     rc_strndup         99-105  (7L)
```

Three byte-identical bodies (`arena_alloc(len+1)`, `memcpy`, NUL). This is
lens 1's own title — *missing libraries* — in its purest form: the arena's
entire public API is `arena_alloc` and `arena_free`
(`src/core/internal.h:41-42`), so every module that needs an arena-owned
copy of a pattern substring writes its own. A pattern substring is the
single most common thing modules copy.

```c
/* In core/internal.h, beside arena_alloc: */
const char *arena_strndup(Arena *a, const char *s, size_t len);
```

Nothing varies per site except the `Ctx *` unwrapping, which the call
sites already do. Group 33's siblings `br_decimal`/`rc_decimal`
(`clone_candidates.tsv` group 63, both `group_frac` **1.000**,
`mod_backrefs.c:70-78` / `mod_recursion.c:89-97`) are the same story one
operation over — byte-identical saturating decimal parse, differing only
in a `BR_NUMBER_MAX`/`RC_NUMBER_MAX` ceiling macro; `mod_recursion.c:78`'s
own comment says *"Saturation, `mod_backrefs.c`'s `BR_NUMBER_MAX` for its
reason"*, i.e. the author copied it knowingly. Fold both into X6 or ship
them here; they are one commit either way.

---

### X5 — the growable arena array, invented ten times

**Severity: MAINTAINABILITY. Effort: LOCAL. Blast radius: 5 files, **1
sabotage row re-aimed** (S201 quotes `row_push`), 0 emitted bytes.**

**Evidence (A5):** `clone_candidates.tsv` groups 3 and 10. Group 10's
four members `prov_push`, `variant_push`, `case_push`, `aux_push` are all
`group_frac` **1.000**.

```
src/parse/rxt_source.c   row_push      615-631   (17L)
src/parse/rxt_source.c   prov_push    1370-1382  (13L)
src/parse/rxt_source.c   variant_push 1384-1396  (13L)
src/parse/rxt_source.c   case_push    1398-1410  (13L)
src/parse/rxt_source.c   aux_push     1412-1424  (13L)
src/parse/rxt_source.c   seen_add     3209-3220  (12L)
src/core/cpset.c         cpset_grow     72-81    (10L)
src/opt/atomic.c         ds_add        376-387   (12L)
src/opt/lower_enc.c      u8_push_branch 202-212   (11L)
cli/main.c               libdir_push   362-373   (12L)
```

Every one is: at capacity, double (from a per-site seed of 8/16/32),
`arena_alloc` the new block, `memcpy` the old contents, swap, then
`memset` the new element to zero and return it. The arena never frees, so
the copy is the whole growth strategy and it is the same strategy ten
times.

```c
/* In core/internal.h. Returns the zeroed new element; the caller owns
 * the (ptr, n, cap) triple and the element type. */
void *pcrec_arena_vec_push(Arena *a, void **v, size_t *n, size_t *cap,
                           size_t elem, size_t seed);
```

**A1 — an author already saw this and chose the other way.**
`src/parse/rxt_source.c:1364-1368` says of the four section pushes:
*"Each mirrors `row_push`'s own growable-array shape exactly (arena-owned,
doubling capacity), so there is one pattern for 'a section array that
grows' rather than four independently-invented ones."* That is a
deliberate, recorded choice for *consistency of shape* — and it is not an
argument against a helper, it is an argument for one that was not
available. The commentary and the four copies both disappear if the shape
is a function. I file it as an extraction the ruled record supports rather
than one it blocks. Note `cli/main.c`'s `libdir_push` is the one member
that is **not** arena-owned (it `realloc`s and is the CLI's only
allocating option — `cli/main.c:1231-1246` builds a whole invariant on
that fact) and should be left alone.

---

### X6 — the group-reference kit: `mod_backrefs.c` and `mod_recursion.c`'s unfinished sharing

**Severity: MAINTAINABILITY. Effort: LOCAL. Blast radius: 3 files, 5
sabotage rows name `mod_backrefs.c` + 1 names `mod_recursion.c`, 2 codegen
checks reference `mod_recursion.c`.**

**Evidence (A5):** `clone_candidates.tsv` flags this file pair in **six
separate groups** — 9, 22, 33, 42, 48, 63 — more than any other pair in
the tree.

Both modules answer the same question in the same four spellings: a group
named by number, by name, by relative offset, and the diagnostic `what`
text for each. The residual copies:

| operation | backrefs | recursion |
|---|---|---|
| arena substring copy | `br_strndup` 141-147 | `rc_strndup` 99-105 |
| saturating decimal | `br_decimal` 70-78 | `rc_decimal` 89-97 |
| relative offset arithmetic | `br_relative` 254-261 | **inlined** in `pcrec_rcport_rel` 234-274, lines 260-264 |
| name-reference preamble | `br_name_ref` 270-291 | `rc_name_call` 286-371 |
| node constructor | `br_node` 102-127 | `rc_node` 126-159 |
| result wrapper | `br_result_node` 129-136 | `rc_result_node` 107-114 |

The relative-offset row is the sharpest: `mod_backrefs.c` *factored* the
four-line saturating `base ± v` computation into `br_relative`, and
`mod_recursion.c` re-typed it inline rather than calling it. The
name-reference row is the second: both open with the identical
`FEAT_NAMED_GROUPS` gate emitting the identical sentence, and
`mod_recursion.c:277-279` says so out loud — *"`br_name_ref`'s rule and
its reason"*.

**A1 — the ruled record is on the extraction's side here, which is what
makes this admissible rather than a re-litigation.**
`src/parse/CLAUDE.md:1062-1067` states *"the two share a resolution PASS
and share nothing else"* — but that sentence is about the **resolved
data** (`A_BREF.u.bref.refs` is a match-time SET, `A_CALL.u.call.target`
is one parse-time number), which is a real and permanent difference that
no extraction here touches. The same file, 70 lines later
(`:1132-1141`), records the project *already applying this finding's own
principle to this exact file pair*: `pcrec_call_by_name` exists *"so
`\g<name>`/`\g'name'` share §3.4(c)'s rule with `(?&name)`/`(?P>name)`
**rather than growing a second copy of it in `mod_backrefs.c`**"*, and the
resolver *"EXTENDS `mod_backrefs.c`'s RESOLVER RATHER THAN COPYING IT"*.
The discipline was applied to the two large things and not to the six
small ones. These copies are a leftover, not a decision.

```c
/* In core/internal.h — the pattern-text primitives both ports need. */
long        pcrec_pat_decimal(const char *p, size_t from, size_t to,
                              long cap);           /* saturating */
long        pcrec_group_relative(int ncap, int sign, long v, long cap);
/* And in parse/: one gate+grammar preamble both name spellings call. */
```

**What varies per site:** the ceiling macro, the `what` spelling, and the
node kind built afterwards. **Checked, so the extraction is
unconditional:** `BR_NUMBER_MAX` and `RC_NUMBER_MAX` are adjacent rows in
`src/core/limits.def:369-370` and both are `1000000L`. They are already
centralized and I do **not** file the pair as a defect — two
independently-movable limits that presently coincide is a defensible
shape, and collapsing them would remove a module's ability to move its
own ceiling. The consequence for X6 is only that the shared
`pcrec_pat_decimal` takes the cap as a parameter and both callers pass
their own row, which is what the signature above already does. `pcrec_group_name_scan`
(`mod_named_groups.c:98-110`) is the precedent: a cross-module parse-tier
primitive already exists and both modules already call it.

---

### X7 — the DFA table emitter, written six times

**Severity: MAINTAINABILITY. Effort: MECHANICAL. Blast radius: 1 file,
`tests/codegen/run_premul_table.sh` (plus `tests/codegen/CLAUDE.md`)
names `emit_tr_table`, 0 sabotage rows, and the emitted text must be
byte-identical — which the identity gate proves rather than a reviewer
asserting it.**

**Evidence (A5):** `clone_candidates.tsv` group 11 (5 members, `group_frac`
0.478-0.750) plus `emit_stay_table` from group 29.

```
src/gen/emit_dfa.c  emit_tr_table       2610-2623 (14L)
src/gen/emit_dfa.c  emit_eol_table      2727-2737 (11L)
src/gen/emit_dfa.c  emit_end_table      2742-2752 (11L)
src/gen/emit_dfa.c  emit_acc_cls_table  2906-2919 (14L)
src/gen/emit_dfa.c  emit_seed_table     2946-2959 (11L)
src/gen/emit_dfa.c  emit_stay_table     3516-3530 (10L)
```

Each emits `    static const TYPE PREFIX_TAG[N] = {`, then N cells wrapped
**16 per line** behind a **7-space** continuation indent, then
`\n    };\n`. The wrapping constant, the indent string and the trailing
brace are re-typed six times.

```c
/* The emitted "static const T NAME[N] = { ... };" array: header, 16-per-
 * line wrapping, indentation, trailing brace — one home. */
typedef int (*DfaCellFn)(const Dfa *d, const DfaRepr *r, int idx);
static void emit_cell_table(StrBuf *c, const char *p, const char *tag,
                            const char *cell_type, int n,
                            const Dfa *d, const DfaRepr *r, DfaCellFn cell);
```

What varies is exactly three things: the cell type string
(`r->cell_type` at four sites, the literal `"unsigned char"` at one), the
length (`d->n`, `d->n * d->ncls`, `d->ncls`), and a one-line cell
expression. `emit_seed_table` additionally closes over `fam[]`, so the
cell function needs a `void *ud` — or that one stays as it is.

**A3 / D76 note.** This is an emitter change, so D76/D94's reflex is
"abi bump". It is **not** one if the extraction is faithful: the emitted
bytes do not move, and `tests/codegen`'s identity gate is the instrument
that proves it rather than a reviewer's reading. That makes this the
*safest* emitter refactor available and a good first emitter wave. If a
byte does move, the identity gate goes red and the change becomes an abi
event by the ordinary ritual — which is the correct outcome, not a
surprise.

---

### X8 — stamp emission: 73 hand-typed `#define <PREFIX>_NAME` sites

**Severity: MAINTAINABILITY (with a real D94 benefit). Effort: LOCAL.
Blast radius: 2 files, every codegen/abi check that greps a stamp name.**

**Evidence (A5):** direct census —
`grep -c 'sb_printf(.*"#define %s'`: **52 sites in `src/gen/emit_vm.c`,
21 in `src/gen/emit_dfa.c`**. Below the clone detector's `k=20` shingle
floor, which is why no group names it: each site is one line.

Every artifact stamp is emitted by a bespoke `sb_printf(sb, "#define
%s_THING <fmt>\n", upper, value)`. There is no `emit_stamp_str(sb, upper,
"ENGINE", engine)` / `emit_stamp_int(...)` / `emit_stamp_bool(...)`.

```c
static void emit_stamp_str (StrBuf *c, const char *upper, const char *name,
                            const char *value);
static void emit_stamp_int (StrBuf *c, const char *upper, const char *name,
                            long long value);
```

**Why this is worth more than the line count suggests.** D94 rules that
the abi re-pin site list is *"EVERY READER OF THE NUMBER, FOUND BY
GREP"*, and `battriage_report.md` (2026-09-15) already recorded that the
grep ritual has a **second reader class it structurally cannot find** — a
manifest whose rows never cite an abi digit but whose byte-count values
move anyway. A stamp-emission helper does not fix that class, but it does
make the *stamp name set* a greppable list of literal arguments to two
functions instead of 73 format strings, which is the half of the ritual
that a table can serve. Low risk, and it pays into a known ritual gap.

---

### X9 — the optimization-axis table has THREE hand-maintained sources and two awk scrapers holding them together

**Severity: MAINTAINABILITY, trending CORRECTNESS-RISK. Effort:
DESIGN-EVENT. Blast radius: `cli/main.c`, `src/parse/axes_dump.c`,
`lib/pcrec.h`, and it DELETES rather than re-aims two checks.**

**Evidence (A5):** `clone_candidates.tsv` group 6 and group 62; census
rows `cli/main.c:cli_parse` 379-809 (**247L**) and
`src/parse/axes_dump.c:emit_predicate_axes` 375-668 (**178L**) — the 6th
and 10th longest functions in the tree. Direct census: `cli_parse`
contains **59 arms each repeating `!no_more_opts &&`**, of which **20 are
`-fno-X` arms whose entire body is `opt.flags |= PCREC_NO_X;`**.

One fact — *"axis A is denied by bit `PCREC_NO_A`, spelled `-fno-a` on the
command line, reported as stamp `RX_...`"* — is written down in three
independent places:

1. `lib/pcrec.h` declares the bit;
2. `cli/main.c`'s ladder maps the flag text to the bit, one hand-written
   `else if` per axis;
3. `src/parse/axes_dump.c` emits a row carrying `deny_macro`, `deny_bit`,
   `cli_flag` and the stamp, hand-written per candidate.

**And two test scripts textually parse `cli/main.c`'s C source with awk to
reconcile (2) against (3)**: `tests/registry/axes_registry_check.sh`
(`CLIMAIN`, `CLI_MACRO`, `check_cli_flag`) and `tests/axes/run_axes.sh:244`
(*"macro -> CLI flag spelling, from `cli/main.c`'s own `!strcmp(a, "...")`
... sites"*). Both scripts carry their own comment warning that *the awk
pairing can miss a site if `cli/main.c`'s loop shape changes*, and
`run_axes.sh:271` has a guard for exactly that.

**Proposed abstraction: `src/core/axes.def`**, an X-macro table on
`limits.def`'s and `rxt_schema.def`'s own shipped precedent:

```c
/* PCREC_AXIS(axis, candidate, order, stamp_macro, stamp_value,
 *            deny_macro, deny_bit, force_macro, force_bit, cli_flag, applies) */
```

read by `cli_parse` (the 20 deny arms become one loop over the table), by
`axes_dump.c` (the rows become a table walk), and by `lib/pcrec.h`'s bit
declarations. **The 178-line `emit_predicate_axes` and ~60 lines of
`cli_parse` disappear, and — the part that makes this worth a DESIGN-EVENT
— the two awk source-scrapers become unnecessary**: A3's usual cost
direction inverts, because a fact with one source needs no reconciliation
check.

**A1.** Nothing in `decisions.md` rules on this. `limits.def` is the ruled
central-config home (charter, lens 3) and this is the same shape applied
to the axes registry. The `[REG-SV]` work already established that a
hand-typed axes row whose `stamp_value` the emitter cannot produce *"is
worse than an empty one, because it reads as covered"*
(`axes_dump.c:415-421`) — which is the drift this extraction removes at
the source. **Overlaps lens 3** (config centralization): the synthesis
should merge, not double-count.

---

### X10 — the CLI integer-valued option arm, written five times

**Severity: POLISH. Effort: MECHANICAL. Blast radius: `cli/main.c` only;
13 `tests/codegen/` scripts reference `cli/main.c` but none plants inside
these arms; the diagnostic text is user-visible, so `docs/spec/cli.md`
must be checked for exact-wording pins (D80).**

**Evidence (A5):** census row `cli/main.c:cli_parse` 379-809 (247L);
direct census — 5 `strtol`/`strtoll` sites at `cli/main.c:568, 585, 647,
660, 701`.

Each is: `strtol` from a fixed prefix offset, reject on `!end || *end` or
an out-of-range value, `fprintf(stderr, "pcrec: --x wants an integer in
LO..HI (got '%s')\n", ...)`, `return 1`, else assign. The prefix length is
a magic number repeated at the `strncmp` and the `a + N` (`"--unroll="`/9,
`"--vm-entry-shape="`/17, `"--step-budget="`/14).

```c
/* Returns 0 on success, 1 having already printed the diagnostic. */
static int cli_int_opt(const char *arg, const char *prefix,
                       long long lo, long long hi, const char *range_text,
                       long long *out);
```

What varies: the bounds, the range prose (`--vm-entry-shape`'s enumerates
its four rung names, so it stays a parameter rather than being derived),
and the destination field. The `a + N` magic numbers vanish with
`strlen(prefix)`.

---

### X11 — the enum-to-string family: 14 switches, and one enum rendered three ways

**Severity: MAINTAINABILITY. Effort: LOCAL. Blast radius: 4 files, **1
sabotage row re-aimed** — S241 (`schema_dump_handwritten`) quotes four of
these functions by name, and it is the row that asserts `--list-schema` is
generated from the table rather than hand-written, so its intent
re-verification is not a formality here — 0 emitted bytes.**

**Evidence (A5):** `clone_candidates.tsv` group 2 — **14 members, every
one `group_frac` 1.000**, the only group in the file where that is true of
the whole group.

All 14 are the same program: `switch (e) { case E_A: return "a"; ... }
return "?";`, no `default:`. The members span
`src/parse/rxt_schema.c` (7), `src/parse/syntax_dump.c` (4),
`src/parse/rxt_source.c` (2), `src/parse/definitions.c` (1).

The sharpest sub-case is `RxtSchemaScope`, which has **three** renderings
in one file — `pcrec_rxt_scope_name` (135-147), `pcrec_rxt_scope_context`
(306-318), `pcrec_rxt_scope_noun` (323-335) — and
`rxt_schema.c:320-322`'s own comment already names the situation: *"Third
rendering, same enum, same file — never a literal at the refusal site."*
Three switches over six enumerators is eighteen hand-maintained cells
where one table row per enumerator is four.

```c
/* rxt_scope.def, beside the existing rxt_schema.def: */
/* X(RXT_SCOPE_BLOCK, "block", "pattern-block", "pattern block") */
```
declaring the enum *and* generating all three renderings from one row.

**A1 and the honest severity.** This is **not** a correctness finding
today, and the reason is worth stating because it is the same
`no default:` discipline X1 has to preserve: adding an enumerator is a
`-Wswitch` compile error at all three sites under `make strict`, so the
three cannot silently disagree about *membership*. What they can disagree
about is *content* — and a fourth rendering means a fourth switch. So the
value here is size and edit-cost, not a bug. Rank it accordingly.

---

### X12 — `strcmp` ladders that are lookups

**Severity: POLISH. Effort: MECHANICAL. Blast radius: per-site, tiny.**

**Evidence (A5):** `clone_candidates.tsv` group 61 (`stamp_macro_of`
`axes_dump.c:150-169` and `override_name` `limits_dump.c:38-44`,
`group_frac` **1.000** / 0.857). Direct census: `if (!strcmp(` ladders
concentrate in `src/parse/rxt_source.c` (11), `src/parse/axes_dump.c`
(11), `cli/main.c` (6), `src/parse/limits_dump.c` (3),
`src/gen/emit_dfa.c` (3).

`stamp_macro_of` maps an axis name string to a stamp macro string through
a `strcmp` chain; `override_name` maps a token string to a rendered string
the same way. Both are two-column tables written as control flow — lens
11's question 3 (*"code-driven vs DATA-driven"*) meeting lens 1's
*missing library* from the other side.

The extraction is a two-column `static const struct { const char *k, *v; }`
plus one shared lookup helper. Most of these are individually trivial; the
reason to file them as one X is that they are the natural **second-order
cleanup once X9's table exists** — `stamp_macro_of` in particular is
answering from prose a question `axes.def` would answer from data.

---

## 2. DETECTOR GROUPS EXAMINED AND REJECTED

Per the brief, a rejected group is a finding.

**Group 7 — the `pf_emit_*` bounded/unbounded prefilter pairs**
(`emit_dfa.c:4511-4576`, `4808-4854`; `group_frac` up to 1.000).
**Rejected as a duplication.** The six functions are three pairs that
differ in a real, load-bearing way: the unbounded form has an early
`return 0`, the bounded form must fall through to the stepped loop because
under a view the machine may still accept at `n-1` or `n`. The site says
so and says *why it is a form rather than a flag*
(`emit_dfa.c:4545-4548`: *"That lost early-out is exactly what
`<PREFIX>_DFA_PREFILTER`'s `-bounded` half tells a consumer, and it is why
this is its own form rather than a flag inside one"*) — i.e. the split is
**caller-observable through a stamp**. Collapsing them would make the
artifact's own report of its prefilter form derive from a runtime branch
rather than from which form was selected. The residual duplication in
these six is the `sb_printf` + `f->dir->bind` indentation threading, which
is **lens 10's emission kit**, not a lens 1 abstraction.

**Group 4 — the module ports** (`pcrec_agport_atomic`, `pcrec_laport_group`,
`pcrec_modport_optrun`, `pcrec_ngport_declare`, `pcrec_rcport_define`,
`uprops_produce`). **Rejected.** These share a *signature*
(`ExtResult (Ctx*, const RegRow*, ExtWant, size_t, ...)`), which is the
doorway contract doing its job, not duplication. Their bodies parse
different grammars. The two genuine members — `br_result_node` and
`rc_result_node`, both `group_frac` 1.000 — are absorbed into X6.

**Group 26 — `axis_row` / `limit_row` / `emit_in_entry_defs`.**
**Rejected.** `axis_row` and `limit_row` are already the correct shape:
one TSV-row printer per dump, each with its own column count and types. A
TSV printer resembles a TSV printer; there is no operation to share
beyond `sb_printf` itself. `emit_in_entry_defs` is in the group only
because it is a long format string. The real dump-tier finding is X9
(the *content* has three sources), not the row printers.

**Group 1's low-`group_frac` members** — `vm_cost` (0.052), `pss_walk`
(0.095), `rd_reverse` (0.120), `emit_attempt` (0.015), `p_class` (0.022),
`compile_driver` (0.017). **Rejected as members.** These are long
functions that *contain* the walk idiom once. They belong to lens 11 by
length; their idiom instance is covered by X1. Reporting them as clones
would mis-rank the extraction's population.

**Groups 5, 21, 35, 38 (`rxt_source.c` internals) — NOT REJECTED, NOT
REVIEWED.** See §4.

---

## 3. WHAT LENS 11 SHOULD JOIN (ADDENDUM 1)

Every over-N function below has a lens 1 extract that applies, so lens 11
should price the extract *before* proposing any function-specific split:

| census row | lines | extract that applies |
|---|---|---|
| `cli/main.c:cli_parse` 379-809 | 247 | **X9** (≈60 lines), **X10** (5 arms) |
| `src/parse/axes_dump.c:emit_predicate_axes` 375-668 | 178 | **X9** (the whole function) |
| `src/gen/emit_dfa.c:emit_attempt` 6373-6881 | 201 | **X7** partially; otherwise none |
| `src/gen/emit_vm.c:pcrec_emit_vm` 8539-11575 | 778 | **X8** (stamp sites); X1 for its walk instance |
| `src/gen/emit_vm.c:vm_render_listing` 7777-8277 | 288 | **X8** |
| `src/core/compile.c:compile_driver` 556-1789 | 402 | X1 for its walk instance; otherwise **none** |
| `src/parse/mod_recursion.c:pcrec_rcport_rel` 234-274 | 29 | **X6** (the inlined `br_relative`) |
| `src/parse/mod_recursion.c:rc_name_call` 286-371 | 53 | **X6** (the `br_name_ref` preamble) |

The two rows where I found **no** lens 1 extract that materially shortens
the function — `compile_driver` and `emit_attempt` — are the ones where
lens 11's five questions have to stand on their own, and lens 11 should
say so rather than assume an extraction is coming.

---

## 4. WHERE I STOPPED (ADDENDUM 2) — the unreviewed remainder, named

I worked the length-ranked census top-down and, in parallel, the clone
candidates by group size. **Reviewed in full:** `src/opt/` (all 11 files),
`src/core/` (arena, cpset, sb, limits, tune, and `compile.c`'s duplication
surface but not its body), `src/parse/mod_backrefs.c`,
`mod_recursion.c`, `mod_named_groups.c`, `definitions.c`, `rxt_schema.c`,
`axes_dump.c`, `limits_dump.c`, `enabled.c`, `cli/main.c`'s option layer,
and the table/stamp/prefilter emission surfaces of `src/gen/emit_dfa.c`.

**Named remainder, not reviewed:**

1. **`src/gen/emit_vm.c` below the stamp and slot layers.** 11,575 lines;
   it holds the tree's longest function (`pcrec_emit_vm`, 778 code-lines)
   and **85 of the 261 sabotage rows** — a third of the tree's whole
   failing-direction net. `clone_candidates.tsv` puts 11 of its functions
   in group 1 and gives it groups 16, 17, 24, 32, 39, 41, 49, 57, 60 of
   its own. I examined its stamp emission (X8), its saturating arithmetic
   (X3) and its walk instances (X1) and **did not review its rung/slot/
   frame emission at all**. This is the single largest unreviewed surface
   in the primary tier and I judge it needs its own pass, not a tail-end
   skim — which is the trigger the charter's own budget note names
   (*"lens 1 and lens 4 may charter a second pass over the emitters if
   their first pass names the need"*). **I am naming the need.**

2. **`src/parse/rxt_source.c`.** 4,000+ lines; census row
   `pcrec_rxt_source_parse` 2095-3069 is **548 code-lines**, the second
   longest function in the tree. `clone_candidates.tsv` groups 3, 5, 10,
   13, 14, 21, 35, 38 all live here. I took X5 (the five `*_push`
   functions) and X12 (its 11 `strcmp` ladders) and went no further —
   in particular groups 13/14 (value trimming and identifier validation:
   `value_trimmed`, `rtrim_ws`, `prose_value`, `read_wrapped_value`,
   `ident_ok`, `defname_ok`, `oracle_ref_ok`) look like a real
   **text-handling** family, which is one of the four Frank named in the
   lens charter, and I did not judge it.

3. **`src/ir/nfa.c` and `src/ir/dfa.c`.** Touched only through group 20
   (`trie_*`), 31, 36, 37, 45. `compile_ast` (395 span-lines, 121 code)
   and `intern` (165/84) were not read.

4. **`lib/pcrec.h`.** 1,072 lines. Read only where X9 needed the deny-bit
   declarations. Its own duplication surface is lens 9's charter, but a
   lens 1 pass over its macro families was not done.

5. **The tail of the census below ~65 code-lines**, except where a clone
   group pulled a specific function in. Roughly 780 of the 860 census rows
   were not individually examined; the extracts above reach them by
   family rather than by enumeration.

---

## 5. ONE THING THAT IS NOT A FINDING, RECORDED SO IT IS NOT RE-FOUND

The nine `atomic.c` walks look, to a detector and to a first reading, like
nine copies of one function that should become one function. **They should
not become one function.** Every one of the nine differs in at least one
per-kind arm, and every one of those arms carries a measured
justification — `pcrec_has_collapsible_rep` prunes `A_LOOK` because the
NFA builder erases lookaround bodies to epsilon;
`pcrec_has_live_capture` prunes `A_REP{0,0}` with a spelling deliberately
matched to `vm_count_slots`' guard *"because these two are ONE predicate
... asked by two passes, and two spellings of one question are two chances
to disagree"*; `pcrec_bref_mark`'s `A_CALL` arm is the one arm in the file
that is not a decline, and S158/S159 exist to defend it.

The extractable part is **strictly** the traversal. A reviewer who reads
X1 as "merge the nine predicates" has read it wrong, and the wrong version
of this refactor would delete two sabotage rows' plant sites and the
`-Wswitch` alarm in the same commit. That is why X1's proposed shape puts
the verdict enum between the classifier and the driver instead of handing
the driver a callback.
