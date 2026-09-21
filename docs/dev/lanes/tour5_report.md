# tour5 — [TOUR-5] select_engine.c: `esel_of`, `prefilter_decision`, and the dead discharge fixpoint

Lane `tour5` (opus), branch `lane/tour5`, branch point `6bc0a5bf` (tree
identical to the code branch point `82dd396a`). Three commits, one per part
of the brief, each self-consistent:

| commit | part |
|---|---|
| `5d5784f0` | (c) the zero-hook `discharge` fixpoint DELETED (D77) |
| `8a6f35e1` | (a) `esel_of`, the non-overlap table, the premise made a check |
| `374da665` | (b) `prefilter_decision` extracted |

Design record: `docs/dev/reviews/2026-09-20-frank-tour.md` [TOUR-5]; the
finding is `docs/dev/reviews/2026-09-20-r61-fable-personal-review.md` F2.
r61 F6 (`vm_counter_fits`' flag read, `emit_vm.c`) was NOT touched — it
belongs to lane tour2.

`pcrec_select_engine` goes from 117 code lines to **52**, and its body now
reads at one level: compute the mask over `analyses[]`, apply the
`--engine=` override, decide the prefilter, stamp `engine_sel`, publish
the fit, run the bounded-repeat ladder.

---

## 1. (a) The non-overlap table as landed, and the one thing the prose did not say

`esel_of(Ctx *cx, const EngineFit *fit)` returns `unsigned char` (the type
of `EngineFit.engine_sel`). The pair is the narrowest signature that carries
what the nine arms read: the fit's four prefilter fields, and the attempt
record `compile_driver` seeds on `cx` (`dfa_disabled`, `collapse_reason`,
`size_drop_rung`, `dfa_was_engine`). `Ctx *` is non-const because the
premise check refuses through `pcrec_ctx_fail`.

The header's table replaces the five stacked blocks the review named
([OPT-4], [OPT-4.1], [OPT-4.2], [LIM-1], [K53-SELRETRY]), each of which
amended the previous one. Every INVARIANT and why-not-the-alternative is
kept — as a table cell, or as one of the four notes (A)-(D) beside it. The
HISTORY went to the rows the tags already name and to `core/internal.h`'s
own `ESEL_*` value comments, which is where the value set's meaning, its
range invariants and its change log already live; nothing in
`decisions.md` or `plan.md` was rewritten for it.

The nine arms, in ladder order (the table itself is in the code):

| # | arm (`ESEL_`) | fires on |
|---|---|---|
| 1 | `FORCED` | `opt->engine != AUTO` |
| 2 | `DECLINED_NULLABLE_DEFAULT` | `fit->prefilter_declined_nullable_default` |
| 3 | `DECLINED_NULLABLE` | `collapse_reason != CR_NONE && fit->prefilter_declined_nullable` |
| 4 | `SIZE_CAP_RETRY` (a) | `collapse_reason == CR_SIZECAP && fit->prefilter` |
| 5 | `SIZE_CAP_RETRY` (b) | `size_drop_rung != SDR_NONE` |
| 6 | `SELECTED` | `!dfa_disabled` |
| 7 | `COLLAPSED_PREFILTER` | `collapse_reason == CR_SEL1 && fit->prefilter` |
| 8 | `OVERFLOWED_DFA` | `dfa_was_engine` |
| 9 | `OVERFLOWED_PREFILTER` | otherwise |

**THE TABLE DISTINGUISHES `excludes` FROM `outranks`, AND THE PROSE DID
NOT.** Writing one row per arm forced the question "is this disjointness or
priority?" to be asked of every arm, and arm 1 answers *priority*:
`compile_driver`'s two drop-ladder rungs carry no `engine == AUTO`
conjunct (`drop_eligible` at `compile.c:1141`, `premul_eligible` at
`:1197`, unlike `ovf_eligible` at `:1012` which does), so `size_drop_rung`
CAN be set under `--engine=dfa` and arm 5 would otherwise fire. First-wins
is the intended answer — a named engine means `auto` selected nothing, so
no selection OUTCOME is the honest token, and the rung stays legible from
the artifact's own axis stamps — but it is a co-occurrence resolved by
ORDER, not an exclusion, and the five blocks nowhere said so.

A second, smaller one: arm 2's own stated non-overlap argument (the
[OPT-4.2] block: "requires `collapse_reason == CR_NONE && !dfa_disabled`,
which is precisely the condition every arm below it is testing the
NEGATION or a further refinement of") **predates arm 5 and does not cover
it** — `size_drop_rung` is neither `collapse_reason` nor `dfa_disabled`.
What actually keeps them apart is that the drop rungs are DFA-engine while
arm 2 requires a VM-chosen artifact. The table says that; the prose did
not.

## 2. (a) The premise check, and how it fails

r61 F2's unasserted premise: *"the size-drop rung and the overflow rung are
mutually exclusive by engine — plausible (drops are DFA-engine, overflow
makes the engine VM) but asserted nowhere; if both ever held,
`ESEL_SIZE_CAP_RETRY` would hide the overflow."* Landed as the first
statement of `esel_of`:

```c
    if (cx->size_drop_rung != SDR_NONE && cx->dfa_disabled)
        pcrec_ctx_fail(cx, fit->why_pos,
                 "internal error: an emitted-size drop-ladder rung and a DFA "
                 "overflow fired on the same compile");
```

**A REFUSAL, NEVER AN `abort()`** — pcrec is a library and
`docs/spec/match_api.md` promises the compile path does not abort the
caller; `pcrec_ctx_fail` unwinds to `compile_driver`'s one `setjmp` and
returns a diagnostic, which is how every other impossible state in this
file already reports itself. (This is [TOUR-4]'s rule applied at a site
that never had the defect, not a second instance of it.)

**FAILING-DIRECTION VERIFIED, not argued.** The conjunction was
temporarily widened to a disjunction on a scratch build and
`\p{L}` under `-e utf8` — a real drop-rung taker, the same witness
`S238`'s own `SAB_REACH` probe uses — was compiled:

```
pcrec: internal error: an emitted-size drop-ladder rung and a DFA overflow
fired on the same compile (pattern offset 0)
exit=1
```

No abort, no signal, exit 1. Reverted; on the delivered build the same
pattern stamps `size-cap-retry` as it did at the branch point.

**WHY THE CHECK IS NARROW ON PURPOSE.** The stronger and also-true premise
is `size_drop_rung != SDR_NONE` ⟹ `fit->chosen == ENGM_DFA` — rung 1 needs
`Job.anchored_ok` (set only when `fit.chosen == ENGM_DFA`) and rung 2 tests
`fit.chosen == ENGM_DFA` outright — which would additionally close arm 2's
gap in §1. It was NOT asserted, because it holds only through an argument
about pipeline determinism ACROSS attempts: the rungs record the PREVIOUS
attempt's `fit`, and the retry re-runs selection from scratch. Nothing the
rungs change (`size_drop_rung` itself, `PCREC_NO_PREMUL_TABLE`) is read by
engine selection, so `chosen` is recomputed identically — verified by grep,
but it is a property of what selection reads rather than a local fact, and
an internal-error refusal that can fire spuriously turns a working compile
into a failure. The narrow form is the one r61 named and the one whose
violation causes the silent loss. The wider fact is stated in note (D) of
the table as the reason, not asserted as a check.

## 3. (b) `prefilter_decision`'s seam, per local

```c
static void prefilter_decision(Ctx *cx, const Ast *root, EngineFit *fit,
                               size_t why_pos);
```

**THE SEAM ANSWERED ITSELF, AND THAT IS THE RESULT.** The brief calls the
inputs and outputs "the design question you ANSWER, not assume". The
answer the code gives is that there is no question: the block was already
a braced `{ }` inside `pcrec_select_engine` precisely because none of its
locals is read outside it. Per local:

Counted by a comment-stripped word count over the landed file, not by
reading:

| local | where it went | reads inside (incl. declaration) | reads outside |
|---|---|---|---|
| `force_on` | stays inside | 6 | 0 |
| `force_off` | stays inside | 3 | 0 |
| `has_bref` | stays inside | 6 | 0 |
| `has_call` | stays inside | 4 | 0 |
| `lang_nullable_declinable` | stays inside | 3 | 0 |
| `would_prefilter` | stays inside | 3 | 0 |

So no local crossed the seam and no returned struct was needed. What
crosses is what always crossed: the function writes the same five
`EngineFit` fields the block wrote in place — `prefilter`, the two
derivations `lang_nullable` and `prefilter_has_collapsible_rep` that
`src/core/compile.c`'s build gate and the `--emit-ir` listing read off the
fit (D81), and the two `prefilter_declined_nullable*` attributions. It
keeps its four refusals, which is the whole reason it takes `why_pos`:
that offset is only the position its diagnostics report, never an input to
a decision.

`root` is `const Ast *` because all four predicates it calls
(`pcrec_minw`, `pcrec_has_collapsible_rep`, `pcrec_has_bref`,
`pcrec_has_linked_call`) already take one.

It is a VERBATIM relocation: the body lost exactly four columns of indent
and `fit.` became `fit->`. Nothing else in it was touched — deliberately,
because its prose carries the [M6.5.2] backref-erasure measurements and the
[DD-14] call-erasure counterexample, which are the contract (D26) and not
this lane's to edit.

## 4. (c) What the discharge deletion removed, and the grep proof it was dead

Removed from `src/opt/select_engine.c`:

1. `EngineAnalysis.discharge` — the `Ast *(*)(Ctx *, Ast *)` member — and
   the three `NULL` initializers in `analyses[]`.
2. The `rewrote` loop: it walked `analyses[]`, `continue`d on every NULL
   hook, and set `rewrote = true` for a non-NULL one **without publishing a
   new root**.
3. The `for (int round = 0; round < SELECT_MAX_ROUNDS; round++)` wrapper
   around the analysis pass.

**Byte-neutral by construction.** With no hook registered the round loop
always left on its first iteration — either at `if (mask & ENGM_DFA) break`
or at `if (!rewrote) break` — so one pass is exactly what ran. Every local
the loop re-initialized (`mask`, `why`, `why_pos`, `node_why`,
`node_why_pos`) is already initialized at its declaration.

`SELECT_MAX_ROUNDS` **STAYS**: the brief's "and the bound" is the round
loop, not the constant. The constant's one remaining reader is
`run_possessify`'s own fixpoint, and `src/core/compile.c:394` cites it by
name; its comment now says so.

**THE GREP PROOF.**

| claim | evidence |
|---|---|
| zero hooks registered | `grep -n discharge src/opt/select_engine.c` at the branch point: the only `analyses[]` occurrences are the three `NULL` initializers |
| no `EngineAnalysis` outside this file | `grep -rn EngineAnalysis src/ cli/ lib/ tests/` → one typedef + one array + comments; the only `tests/` hits are prose in `run_atomic_identity.sh`, `registry_check.c` and `S96`, all naming `node_derived`, never `discharge` |
| the one customer moved | `pcrec_discharge_atomic` is called from `src/core/compile.c:1304` and nowhere else; `select_engine.c` has not called it since [DD-14] wave G |
| the ANALYSIS half is live and kept | all three rows' `forces` are called every compile; `forces_captures` / `forces_registry` / `forces_dfa_overflow` are the pass |

**The rewrite arm could not have served a customer anyway**, which is the
D77 point rather than a historical footnote: `rewrote = true` published no
root, so the first registered hook would have spun `SELECT_MAX_ROUNDS`
against a verdict it could not move. `docs/design/atomic_groups_design.md`
§5.4 had already recorded that as one of its three reasons for declining
to register, and `src/opt/CLAUDE.md` called it *"a live defect in unused
code"*.

### 4.1 Doc readers, found by grep, updated in the same change (D80)

`grep -rn discharge docs/ src/ cli/ lib/ tests/`, filtered to sentences
about the SOCKET rather than about `pcrec_discharge_atomic` the pass. The
change is internal, so no `docs/spec/` hunk is owed — and none of the four
`docs/spec/` files mentions it (verified by grep, not by memory).

- `src/opt/select_engine.c` — the file header paragraph, the
  `EngineAnalysis` struct comment, `SELECT_MAX_ROUNDS`' comment,
  `run_possessify`'s header, the wave-G pass-order note, and
  `pcrec_select_engine`'s own header.
- `src/core/internal.h` — `pcrec_altcls`' "the same shape
  select_engine.c's `discharge` hook uses", and `pcrec_discharge_atomic`'s
  socket paragraph.
- `src/opt/CLAUDE.md` — six entries.
- `docs/dev/plan.md` [ENG-CUT] — its text made the socket a thing the row
  PLUGS INTO. It now owns building the plumbing from scratch (the fixpoint,
  the round bound and the root-publishing path), with the deleted
  scaffolding's defect recorded so nobody rebuilds the same shape.
- The design documents (`engine_m4.md` §5.2, `eng_brep_design.md` §2.8,
  `backrefs_design.md`, `atomic_groups_design.md` §5.4) were **left
  alone**: they are the design RECORD of a socket that was designed and
  shipped, and D80's obligation is on the contract, not on history. The
  plan row and the code now both point at §5.2 as the record.

**A PRE-EXISTING STALENESS FOUND WHILE DOING IT, and fixed in the same
commit.** `internal.h`'s `pcrec_discharge_atomic` declaration said *"RUN
FROM THE TOP OF `pcrec_select_engine`, BEFORE the analysis loop"* and
`src/opt/CLAUDE.md` said *"The FREE DISCHARGE runs from the top of
`pcrec_select_engine`"* — both false since [DD-14] wave G hoisted the call
into `src/core/compile.c`, three weeks before this lane. Neither is about
the socket, which is why neither was caught by the wave's own sweep: the
wave moved a CALL and these two sentences describe WHERE IT RUNS, a fact
that moves with the call while citing neither the function it moved to nor
any symbol the move touched.

## 5. Sabotage anchors: 8 re-aimed, 285/285 resolving

`scripts/m6read_check_sab_anchors.py` reads **285/285 sabotage anchor sites
resolving, 269 rows** — the same figure as at the branch point.

Eight rows anchor inside the moved code. Every one was re-aimed, and every
one had its INTENT re-verified rather than its text substituted: each plant
was re-applied through `tests/mech/lib/replace.py` against a scratch copy of
the landed file (1 occurrence each, AFTER-text presence verified by the tool
itself) and the result compiled with
`gcc-16 -O2 -Wall -Wextra -Werror -std=gnu11 -fsyntax-only`. **8 of 8 apply
and compile.**

| row | move | what the plant still does |
|---|---|---|
| `S238` | into `esel_of`: `fit.`→`fit->`, the arm gained a `: ` continuation column | deletes exactly the `size_drop_rung` disjunct, so a drop-rung-rescued artifact falls to `!cx->dfa_disabled ? ESEL_SELECTED` |
| `S64` | dedent 4, `fit.`→`fit->` | deletes exactly the `-fprefilter` do-or-die refusal, leaving the other three refusals in the same function live |
| `S102` | dedent 4, `fit.`→`fit->` | deletes exactly the `has_bref` disjunct of `fit->prefilter`'s force-false clause |
| `S165` | dedent 4, `fit.`→`fit->` | deletes exactly the `has_call` disjunct of the same clause |
| `S176` | dedent 4 | pins `has_call` false at its one definition, `has_bref` left live |
| `S206` | dedent 4, `fit.`→`fit->` | pins `lang_nullable` false at its one derivation |
| `S207` | dedent 4, `fit.`→`fit->` | INVERTS `lang_nullable` at its one derivation |
| `S216` | dedent 4, `fit.`→`fit->` | pins `prefilter_declined_nullable_default` false, rung-scoped sibling untouched |

Each row carries the re-aim note in its own file, naming what the plant
still does and what it leaves live — so the population claim is checkable
without re-deriving it, which is what `S206`/`S207`'s paired
1-cell-vs-2-cell asymmetry depends on.

The count was **predicted before the edit and matched exactly**: seven rows
quote 8-space-indented lines inside the prefilter block, one quotes the
ladder. `coding_guide.md` §3.4's rule — a verbatim relocation costs zero
re-aims, a RE-INDENTATION breaks every anchor — priced this move correctly
and is the reason the extraction was done as a pure dedent with no other
reformatting.


## 6. Findings the brief did not anticipate

**F1 — the ladder's own non-overlap prose was incomplete, and writing it as
a table is what showed it.** Two gaps, both in §1: arm 1 OUTRANKS rather
than excludes (the drop-ladder rungs run under `--engine=dfa` too), and
arm 2's [OPT-4.2] argument enumerates `collapse_reason` and `dfa_disabled`
but predates arm 5's `size_drop_rung` disjunct and so does not cover it.
Neither is a defect — the stamps that come out are right in both cases —
but both are claims the file MADE and did not support, which is exactly
what r61 F2 said the risk was. *A non-overlap argument written as prose per
amendment cannot be checked for completeness; written as one row per arm,
the empty cell is visible.*

**F2 — a stale sentence survived its own wave because it described a
CALL SITE rather than a symbol.** [DD-14] wave G moved
`pcrec_discharge_atomic`'s call from `pcrec_select_engine` to
`src/core/compile.c` and updated everything that names the socket; three
weeks later both `core/internal.h`'s declaration comment and
`src/opt/CLAUDE.md` still said the pass *"runs from the top of
`pcrec_select_engine`"*. A grep for the moved symbol finds the declaration
— but the sentence that is wrong cites neither the destination file nor
any token the move touched, so a reviewer checking the symbol's sites reads
right past it. Fixed here. It is the same class as
`battriage_report.md`'s SECOND READER CLASS one level up: *a reader whose
text never cites the thing that moved still moves with it.*

**F3 — the deleted mechanism's own design record had already recorded that
it could not work.** `docs/design/atomic_groups_design.md` §5.4 gives three
reasons for not registering the free discharge, the third being that the
fixpoint never calls a hook; `src/opt/CLAUDE.md` called the same line *"a
live defect in unused code"*; `docs/dev/plan.md` [ENG-CUT] cited it by
`file:line`. So the argument for deleting it had been written down three
times, in three files, by three different waves, and the scaffolding stayed
because each of them was a note ON something rather than a row TO do
something. D77's value is in making that a disposition.

## 7. What was NOT done, and why

- **r61 F6** (`vm_counter_fits` reading `PCREC_NO_COUNTER` inside the
  predicate while `vm_cursor_fits`/`vm_revdet_fits` have theirs read by
  callers) is in `emit_vm.c` and belongs to lane tour2. `emit_vm.c` is
  untouched by this branch (`git diff --stat` confirms).
- **The wider premise** (`size_drop_rung != SDR_NONE` ⟹
  `fit->chosen == ENGM_DFA`) is stated as note (D)'s reasoning and not
  asserted — §2 has the argument.
- **The design documents** keep their socket text: they are the record of
  a design that shipped, not a contract that changed (§4.1).
- **The [DD-14] wave-G pass-order note** inside `pcrec_select_engine` was
  left at its full length. It looks like history, but its last clause states
  a LIVE ordering invariant (selection must run after the call graph, the
  discharge before the analysis), and the brief's history-move was scoped to
  the ladder's five blocks.

## 8. Validation

Every log path below is relative to `worktrees/tour5/`.

### 8.1 Complete

| what | result | log |
|---|---|---|
| `make -j4 CC=gcc-16` | clean after every commit | — |
| `make strict CC=gcc-16` | "whole tree compiles clean with -Werror -Wshadow", after every commit | — |
| `scripts/m6read_check_sab_anchors.py` | **285/285 anchor sites resolving, 269 rows** — same as the branch point | — |
| sabotage plants re-applied | **8 of 8** apply through `tests/mech/lib/replace.py` (1 occurrence each) and compile under `-Wall -Wextra -Werror -std=gnu11` | — |
| `make test-registry` | **631 PASS / 0 FAIL, rc=0.** PC-3 green on this box; PC-4 62,872 cells / 0 disagreements; definitions-oracle 354 cells / 101,244 A==B and 101,244 A==C comparisons / 0 disagreements | `build/tour5/registry.log` |
| `make test-codegen` | **9/10 scripts**, 65/0 checks in the script that owns the anchor gate. Sole red: the standing darwin `FAIL: nm could not read arm_a.o` probe (`docs/dev/wake.md`), unrelated to this branch | `build/tour5/test-codegen.log` |
| `make test-prefilter` | **34 / 0** — including all four [OPT-4.2] `declined-nullable-default` stamp checks, which read exactly the field `prefilter_decision` now writes | `build/tour5/test-prefilter.log` |
| `bash tests/codegen/run_anchored_match.sh` | **20 / 0, rc=0** — S238's own suite. Its §5 census is the reach evidence for arm 5: **the size-cap drop arm's corpus population is 11** (floor 6), so the `size_drop_rung` arm is genuinely exercised and the premise check sits on a live path, not a dead one | `build/tour5/anchored_match.log` |
| `make test-vm` | **48 / 0**, 3/3 scripts | `build/tour5/test-vm.log` |
| premise check, failing direction | forced and observed (§2): a scratch build with the conjunction widened refuses `\p{L}` under `-e utf8` at exit 1 with the internal-error text, no abort; reverted | — |

`tests/anchored/run_anchored_diff.sh` was **deliberately not run to
completion**. It is the second script in `make test-anchored-match`'s group,
it is slow, and `docs/dev/tt4m_time.md` records it as FAILING on this tree
pre-existing (26 patterns whose emitted C does not compile under the
harness's own `-Werror` flags). The group was killed with `scripts/safekill`
after `run_anchored_match.sh` — the half that owns S238's detector — had
already finished, and that script was then re-run alone for a clean verdict.

### 8.2 OWED at hand-off

Both are long, so they are the last things launched (BOILERPLATE's
DO-THEN-FINISH), in this order, one at a time:

| what | command | log | completion line |
|---|---|---|---|
| emitter byte-neutrality, five streams | `python3 scripts/emit_sweep.py --ref 82dd396a` | `build/tour5/emit_sweep.log` | `EMIT_SWEEP rc=` (appended). **Bar: `movers=0 asymmetric=0` on every stream, rc 0.** Each stream prints its own `... movers=N asymmetric=N` line; `population:` and `elapsed:` print just above the rc |
| the optimization-axis deny/force matrix | `make test-axes` | `build/tour5/test-axes.log` | `TEST_AXES rc=` (appended). This target is `tests/axes/run_axes.sh` plus `tests/codegen/run_form_census.sh` — the deny/force matrix IS this function's contract, so a red here is this lane's until shown otherwise |

**The prediction, stated before they ran:** 0 movers on all five streams
and a clean axes matrix. All three parts are byte-neutral by construction —
(c) deletes a loop that provably iterated once, (a) and (b) are relocations
of unchanged expressions — and nothing in this branch touches emitted text,
so this is NOT an `abi` event and no `docs/spec/` hunk is owed (verified by
grep: no `docs/spec/` file mentions the `discharge` socket).

## 9. Manager's rulings consumed

Received mid-flight, after the interim report, and implemented in
`b81cdf93`:

1. **Record both findings, and make the header table say OUTRANKS where
   that is the true relation.** Arm 1's cell already read `OUTRANKS`; note
   (B) now states outright that [OPT-4.2]'s prose argued non-overlap from
   `collapse_reason` and `dfa_disabled` alone and so does not cover arm 5's
   `size_drop_rung` disjunct, and that what separates arms 2 and 5 is the
   drop ladder being DFA-engine while the field requires a VM-chosen
   artifact. Both are §1 and §6 F1 here.
2. **Leave `tools/review/out/function_census.tsv` at the branch-point
   copy** — one regeneration after wave 2 merges is the manager's admin
   item. Reverted; §7 has the reasoning.
