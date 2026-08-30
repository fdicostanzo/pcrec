# [OPT-4.1] — gate the count-collapsed prefilter rescue on non-nullability

Lane `opt41` (opus, worktree `worktrees/opt41`, branch `lane/opt41`).
PHASE 1 (read + code only, under the `.lift` execution hold) COMPLETE.
Phase 2 (build, checks, corpus, axes, the ten stamps) PENDING `.lift`.

Every claim below is marked MEASURED (with the command and the number) or
INFERRED (derived from source read under the hold). Under Phase 1 nothing was
compiled or run, so **every claim about the compiler's behaviour is INFERRED**
and says so; what is MEASURED in Phase 1 is text — greps, counts, extractor
dry-runs.

---

## 1. The predicate, and where it lives

**ONE derivation.** `src/opt/select_engine.c`, in the prefilter block that
already computes `fit.prefilter`:

    fit.prefilter_lang_nullable = pcrec_minw(root) == 0;

`pcrec_minw` is `src/opt/mrl.c`'s existing width analysis ([M4.6d], D51 ruling
1). No new walk was written — memory `pcrec-general-mechanisms-not-special-
cases`, and the helper is the standard structural recursion the brief asked
for.

**THREE readers, each doing a different thing with it:**

| site | reads | does |
|---|---|---|
| `src/opt/select_engine.c`, the `fit.prefilter` clause | `prefilter_declined_nullable` | on a ladder RUNG, drops the prefilter ENTIRELY |
| `src/core/compile.c`, the build gate | `prefilter_lang_nullable` | under `-fprefilter-collapse`, declines the collapse and keeps the EXACT prefilter |
| `src/gen/emit_vm.c`, the `--emit-ir` `; prefilter` line | `prefilter_declined_nullable` (copied onto `VmStamp`) | reports the decline instead of naming a flag the caller did not pass |

**WHY THE RUNG'S DECLINE IS IN `select_engine.c` AND NOT AT THE BUILD GATE.**
On a rung the alternative to the collapsed machine is NOT the exact one — the
exact one is what failed. Declining at the gate would leave `fit.prefilter`
true, send the compile back through the construction that already overflowed,
and cost a THIRD attempt (INFERRED from `compile_driver`'s retry ladder,
`src/core/compile.c` ~line 726-790: `retry_drop` would fire on the second
overflow, so the compile would still succeed — it would just pay for the
wasted build the design's cost bound forbids). Declining the PREFILTER in
selection costs nothing and lands exactly on the artifact the ladder produced
before [OPT-4] existed.

**WHY `pcrec_minw` IS THE RIGHT WALK** (INFERRED, from `src/opt/mrl.c`'s arms
read line by line):

- it already answers for the PREFILTER's lowering, not the pattern's
  semantics: `A_CAP`/`A_ATOMIC` transparent (as `src/ir/nfa.c` lowers them),
  `A_LOOK` 0 (as the prefilter lowers it — to epsilon), `A_CALL` off the
  callgraph fixpoint;
- the fixpoint is populated in time: `compile.c` runs `pcrec_callgraph_build`
  at line 925 and `pcrec_select_engine` at line 952 (MEASURED, `grep -n`);
- its documented direction is UNDER-estimation, so `minw == 0` may claim
  nullable where the true language is not. That direction is the SAFE one:
  declining a rescue costs a filter, never an answer.

**AND THE COLLAPSED LANGUAGE'S NULLABILITY IS THE EXACT PATTERN'S.** The
collapse rewrites `X{m,n}` as `X{min(m,1),}`, and `min(m,1) == 0` iff `m == 0`,
so an `A_REP` is nullable on exactly the same condition before and after;
concatenation and alternation combine 0-ness identically. One walk answers for
both languages, which is why the field is `prefilter_lang_nullable` and not
`collapsed_lang_nullable`.

## 2. What the decline does, per rung

| rung | before [OPT-4.1] | after, when the collapsed language is nullable |
|---|---|---|
| [SEL-1] (a DFA STATE cap overflowed) | collapsed prefilter, `RX_ENGINE_SEL "collapsed-prefilter"` | NO prefilter — the pre-[OPT-4] artifact — and `RX_ENGINE_SEL "declined-nullable"` |
| [OPT-4] size (a size cap refused the exact artifact) | collapsed prefilter, `_LANG_WHY "size cap retry, …"` | NO prefilter, which is SMALLER still, so the rung still rescues the compile. `RX_ENGINE_SEL` stays `"selected"`, as it already does when that rung collapses |
| `-fprefilter-collapse`, no rung | collapsed prefilter, `_LANG_WHY "forced"` | the EXACT prefilter is kept, `_LANG "exact"` / `_LANG_WHY "nullable collapsed language"` |

**THE SIZE RUNG IS GATED TOO, AND THAT IS A DELIBERATE CALL BEYOND THE
MEASURED CASE.** The bench's loss is on the [SEL-1] rung. Gating only that rung
would have been the special case; gating both is the general form, and it costs
no pattern its compile because dropping the prefilter is strictly smaller than
collapsing it. `tests/resource/run_resource_tests.sh`'s `(a|b){0,30000}` cell
is the live witness and its expectation is flipped accordingly (§5).

**`-fprefilter` OVERRIDES THE DECLINE AND IS THE ONLY THING THAT DOES**
(brief item 7). It is do-or-die (D46/D47.3): the decline's alternative is NO
prefilter, which is exactly what an explicit `-fprefilter` forbids, so a
request this pass cannot honour must REFUSE rather than be silently answered
with its opposite. Implemented at BOTH sites: `&& !force_on` on
`fit.prefilter_declined_nullable` in `select_engine.c`, and
`(pfc_prefilter_forced || !nullable)` on the build gate's `collapse`.

**THE SECOND SITE WAS A CORRECTNESS GAP FOUND ON REVIEW, not symmetry.**
Without it, `-fprefilter` on a pattern the SIZE rung is rescuing would decline
the collapse, keep the exact prefilter the cap already refused, and REFUSE a
pattern that compiles today — falsifying the sentence this row's own
`limits.md` hunk adds. INFERRED from the driver's `size_eligible` conjuncts
(`collapse_reason != CR_SIZECAP` makes the third attempt unreachable); no test
in the tree covers `-fprefilter` with an oversize nullable pattern, which is
why it was a review finding rather than a red run. `-fprefilter-collapse` does NOT override it:
that flag chooses a LANGUAGE for a prefilter, not whether one exists, and a
caller who wants existence has `-fprefilter`. Both are specified in
`docs/spec/tuning.md` §2.17.

## 3. The stamps

Two existing macros gain one VALUE each — no new macro, no scaffolding change,
so **no `abi` bump** (D76; `.abi` is untouched and `make test-codegen`'s
[DD-14.FB] §10.4 expectation is unmoved).

- **`RX_ENGINE_SEL "declined-nullable"`** — the [SEL-1] rung was offered and
  declined; no prefilter survives. It exists because without it the declined
  artifact is byte-indistinguishable in its stamps from one whose COLLAPSED
  machine also overflowed (`overflowed-dfa`), and those two cost a consumer
  quite different things: one is a rescue that was not available, the other a
  rescue that was refused as useless. It is reachable ONLY from the [SEL-1]
  rung, which keeps `>= ESEL_OVERFLOWED_DFA` still meaning "a DFA build
  overflowed" (`src/core/internal.h`'s own ordering claim).
- **`RX_VM_PREFILTER_LANG_WHY "nullable collapsed language"`** — a prefilter
  EXISTS and its language is exact BECAUSE the collapse was declined. Reachable
  only under `-fprefilter-collapse`: on a rung the same decline leaves no
  prefilter, and `match_api.md` §6.3's iff makes the LANG pair conditional on
  there being a machine to name.

**THE BRIEF ASKED FOR THE `_LANG_WHY` VALUE ALONE, AND THAT IS NOT ENOUGH —
this is a finding, not a deviation of convenience.** `_VM_PREFILTER_LANG` and
its `_WHY` are emitted iff `fit.prefilter` (`src/gen/emit_vm.c:8297`, gated;
`match_api.md` §6.3 rules the iff; `tests/codegen/run_dfa_stamps.sh` asserts it
both ways). The measured case — the [SEL-1] rung's decline — has NO prefilter,
so it cannot carry a `_LANG_WHY` without breaking that iff, which WOULD be a
scaffolding change and an `abi` bump. `RX_ENGINE_SEL` is the stamp whose whole
job is naming the ladder outcome, and it is unconditional on every artifact.

`--list-axes`' `engine-route` row was added with it (order 3, the ladder's own
position); `prefilter-lang`'s axis lists LANG values, not `_WHY` values, so it
needs no row for the second value.

## 4. Spec hunks (D80), all in the same commits as the code

| file | hunk |
|---|---|
| `docs/spec/tuning.md` §2.17 | a new "[OPT-4.1] A RUNG IS DECLINED WHEN THE COLLAPSED LANGUAGE IS NULLABLE" block: the rule, the per-rung outcome, both stamps, the flag interactions, the measured need |
| `docs/spec/tuning.md` §2.17 | the `-fprefilter-collapse` bullet gains the non-nullability conjunct; the "TWO CONJUNCTS ARE CORRECTNESS" paragraph gains the third, overridable one |
| `docs/spec/tuning.md` §2.17 | the `_LANG_WHY` value table gains `"nullable collapsed language"` |
| `docs/spec/tuning.md` §2.17 | **the NAMED RESIDUAL** (manager's ruling on §9 item 1): nullability is not the only reason a rescue can fail to pay — the four whole-subject-only cells the bench measured FLAT are named, two of them non-nullable and deliberately left alone, with "a measured flat is not a loss" stated so the bench can cite it |
| `docs/spec/registry.md` line 203 | PENDING PHASE 2 — the stale `axis` value list, re-derived from a live `--list-axes` (§8 item 9) |
| `docs/spec/limits.md` §3.3 | the retry does not apply where the collapsed language is nullable; the "nothing that compiles today stops compiling" statement |
| `docs/spec/match_api.md` §6.3 | the `RX_ENGINE_SEL` table gains `"declined-nullable"`; "THE LAST THREE" becomes FOUR; a paragraph on why it is not the same outcome as `"overflowed-dfa"` |

**TWO PRE-EXISTING SPEC DEFECTS FIXED IN PASSING** (both in the `_LANG_WHY`
table I was editing; MEASURED by reading `src/gen/emit_vm.c`'s switch against
the table):

1. the table carried `"exact nfa N > B"` — the PRE-ruling-B knee's value. The
   emitter has not written it since ruling B (its switch emits `no counted
   repeat` / `forced` / `dfa overflow retry` / `size cap retry` / `exact`), so
   the row was a stale contract entry. Removed, with a note saying so.
2. the prose said "FIVE values" over a table of six. Now "SIX values" over six,
   with the removed row accounted for.

## 5. Checks — both directions asserted, each the other's control

**THE BRIEF'S ITEM 3 IS FACTUALLY WRONG ABOUT THE EXISTING WITNESSES, and this
is worth stating because it changed the work.** The brief says the K39/[OPT-4]
check witnesses are "`[a-z]{0,4000}`-shaped pairs" that "now DECLINE". They are
not. MEASURED (`grep`, then `pcrec_minw` computed by hand per arm):

| witness | file | minw | verdict |
|---|---|---|---|
| `a(b\|c)+d` | `run_prefilter_collapse.sh` §2 | 3 | unaffected (no counted repeat) |
| `((a)\|b){0,3}c` | §2 | 1 | still collapses |
| `((a)\|b){0,4000}c` | §1, §2, `run_ir_listing.sh` K39 | 1 | still collapses |
| `foo((a)\|b){0,1000}bar` | §2 | 6 | still collapses |
| `((a)\|ab){4000}c` | §2 | 4001 | still collapses |
| `((a)\|b){0,4000}?c` | §2 | 1 | still collapses |
| `((a{10,20}){10,50})z` | §2 | 101 | still collapses |
| the [SEL-1] witness (level-context) | §6, §7b | 10 | still collapses |

Every one is NON-nullable — they all carry a trailing literal or a positive
`rmin`. So **no existing expectation flips in `run_prefilter_collapse.sh` or
`run_ir_listing.sh`**, and the nullable direction had no witness at all. The
work was therefore to ADD the nullable half rather than to re-derive the
existing rows, with the existing rows serving as the controls the brief asked
for.

### What was added

- **§2 `lang_witness exact-nullable`** — a third expectation folded into the
  existing function rather than a second one: it shares `exact`'s LANGUAGE and
  its byte-identity leg (a flag that changed nothing moved no byte) and differs
  only in requiring `_LANG_WHY "nullable collapsed language"`. Two witnesses,
  `((a)|b){0,4000}` and `((a)|b){0,3}` — the `count-collapsed` rows above them
  MINUS ONE CHARACTER, so a decline that fired on the STRUCTURE rather than on
  nullability turns the pair red from both ends.
- **§6b, the nullable rung** — its witness is §6's own pattern wrapped in
  `(?:...)?`: one epsilon in the NFA, the same DFA overflow, opposite sides of
  the predicate. Asserts `RX_ENGINE_SEL "declined-nullable"` beside
  `RX_VM_PREFILTER "none"`, the ABSENCE of `RX_VM_PREFILTER_LANG` (the §6.3 iff
  on the artifact kind this row creates), and `-fprefilter`'s override.
- **§7 / §7b** — the closed value set gains `declined-nullable`, the
  route-agrees-with-the-prefilter-stamps cross-check puts it in the
  "no prefilter survived" arm, and a `sel_witness` row makes it REACHABLE
  (K35). The three rows are now a three-way control on ONE overflow: rescue
  TAKEN, rescue DENIED by a flag, rescue DECLINED by the language — and only
  the third cannot be produced by a flag at all.
- **`tests/resource/run_resource_tests.sh`** — the size-rung cell became a
  pair, `(a|b){0,30000}` (nullable, expects no prefilter) and `(a|b){1,30000}`
  (non-nullable, expects `size cap retry`). The twin is ALSO the tree's only
  witness for that stamp value: no corpus pattern reaches either rung at the
  default and the bench reaches neither across 74 forms (its O-10 ask (v)), so
  without it the bucket would be tested only by `make check`.
- **`tests/registry/axes_registry_check.sh`** — `RX_ENGINE_SEL` had **NO
  value-set leg at all**; it was checked only by a hardcoded `case` list in
  `run_prefilter_collapse.sh` §7, which shares no source with the dump OR the
  spec. Two legs added: dump-vs-DOCS (`match_api.md`'s table, anchored on a
  phrase carrying no COUNT) and dump-vs-CODE (`pcrec_engine_sel_name`'s own
  `return` statements). **MEASURED in Phase 1** by running both extractors by
  hand against the real files: each yields exactly the six values.

### Sabotage rows (`tests/mech`)

A new `pfcollapse` arm (`run_prefilter_collapse.sh`; its scrape reads that
script's own `prefilter-collapse: N passed, M failed` trailer, not the
`^checks passed:` shape), registered BEFORE the rows that name it (R31 C11).

**THE ROWS WERE RENUMBERED S205/S206 -> S206/S207** (manager, 2026-08-30):
lane w11f, merging ahead of this one, had already minted `S205` on a branch
this worktree could not see. The lane HAD run the directory's own
highest-id command and got 204 — a worktree's `sabotages/` is the id space as
of its branch point, not the id space — so the lesson is recorded in
`tests/mech/sabotages/CLAUDE.md`'s Numbering section rather than left as a
one-off: in a multi-lane session the id range is the manager's to arbitrate.
The renumber was one SIMULTANEOUS substitution (two sequential passes would
have carried the first row to `S207` and merged the pair), and the mention of
`S205` in `docs/dev/dev_journal.md` was left alone — it is w11f's row, not
this lane's.

| row | plant | detectors | corpus |
|---|---|---|---|
| **S206** predicate REMOVED (`= false`) | the rescue is built again on nullable languages — the bench's 1.2-9.9x | `pfcollapse` §6b, §7b's `declined-nullable` witness, §2's two `exact-nullable` rows; `resource`'s nullable cell ALONE (its twin stays green, which is what says a PREDICATE was removed rather than the rung) | EXPECTED `0fail` |
| **S207** predicate INVERTED (`!= 0`) | the rescue is declined on the 2.2-4.6x winners and kept on the losers | `pfcollapse` §6, §2's six `count-collapsed` rows, §7b's `collapsed-prefilter` witness; `resource`'s BOTH cells | EXPECTED `0fail` |

Both plants are ONE TOKEN at the predicate's single derivation, deliberately —
a plant at either READER would leave the other working and report a partial
removal as a whole one. Both declare `SAB_REACH` (a probe on the clean tree
that must produce the stamp the row is about) and `SAB_REACH_POP` floors on the
witness populations, per [MECH-REACH]. `SAB_REACH_POP` counts MEASURED in Phase
1: `^lang_witness exact-nullable` = 2, `\[sel1n\]` = 10, `^lang_witness
count-collapsed` = 6, `\[sel1\]` = 8, `^size_rung_cell ` = 2.

**`corpus:0fail` IS THE EXPECTED READING ON BOTH, and here the argument is a
proof rather than a measurement**: the prefilter is a FILTER whose contract is
soundness of REJECTION and a lower bound on the match start (`match_api.md`
§6.3 H1/H2/H3), so its presence, its absence and its LANGUAGE are all
answer-identical. That is the whole reason `pfcollapse` had to be its own arm.

## 6. PREDICTIONS for the bench's labelled points — stated BEFORE measuring

Derived from the pattern TEXT (read from
`/home/duxevents/pcrec-bench/bench/{bounded,loglines}/patterns/*.rx`, read-only)
and `pcrec_minw`'s arms, by hand. The whole-subject form is
`(?:PAT)\z` (MEASURED: `pcrecbench/record.py`'s `whole_subject_text`), which
adds 0 to `minw`, so a form's verdict is its plain form's.

| # | point | pattern | minw | PREDICTION | expected stamps |
|---|---|---|---|---|---|
| 1 | `ctx-lazy-64` | `\b(?:fail\|abort\|panic)\b.{0,64}?\b(?:disk\|memory\|socket\|quota)\b` | 8 | **KEEP** the rescue | `ENGINE_SEL "collapsed-prefilter"`, `VM_PREFILTER "hybrid"`, `LANG "count-collapsed"`, `LANG_WHY "dfa overflow retry, exact nfa 174"` |
| 2 | `ctx-lazy-256` | same, `{0,256}?` | 8 | **KEEP** | same, `exact nfa 558` |
| 3 | `ctx-lazy-1024` | same, `{0,1024}?` | 8 | **KEEP** | same, `exact nfa 2094` |
| 4 | `ctx-greedy-256` | same, `{0,256}` greedy | 8 | **KEEP** | same, `exact nfa 558` |
| 5 | `level-context` | `\b(?:ERROR\|FATAL\|CRIT)\b.{0,200}?\b(?:timeout\|timed out\|refused\|denied\|unreachable)\b` | 10 | **KEEP** | same, `exact nfa 462` |
| 6 | `cls-upto-32768` plain | `[a-z]{0,32768}` | **0** | **DECLINE** | `ENGINE_SEL "declined-nullable"`, `VM_PREFILTER "none"`, NO `LANG` macro |
| 7 | `cls-upto-32768` whole | `(?:[a-z]{0,32768})\z` | **0** | **DECLINE** | same |
| 8 | `cls-upto-16384` whole | `(?:[a-z]{0,16384})\z` | **0** | **DECLINE** | same |
| 9 | `cls-lazy-16384` whole | `(?:[a-z]{0,16384}?)\z` | **0** | **DECLINE** | same |
| 10 | `nest2-64` whole | `(?:(?:\d{1,64}){1,64})\z` | **1** | **KEEP** | `collapsed-prefilter` / `hybrid` / `count-collapsed`, `exact nfa 8258` |
| 11 | `nest3-16` whole | `(?:(?:(?:\d{1,16}){1,16}){1,16})\z` | **1** | **KEEP** | same, `exact nfa 8466` |

The four `ctx` rungs' and level-context's `exact nfa` numbers are the bench's
own (O-10 item 1); they are quoted as the expected stamp text, not re-derived.

**ROWS 10 AND 11 DISAGREE WITH THE BRIEF, and the disagreement is a finding
rather than an error to fix.** The brief groups `nest2-64 whole` and `nest3-16
whole` with the DECLINE set. Their minimum width is 1 — `(?:\d{1,64}){1,64}`
has `rmin = 1` at both levels over a `\d` of width 1 — so they are NOT nullable
and this predicate keeps their rescue. The bench's own text supports that
reading: O-10 item 3 puts those four `\z`-only rescues in a separate sentence
from the losses, describing them as *"reached only by the anchored regime: flat
numbers, +376…+4,560 B of .so — a rescue with no benefit on those four
cells"*, while item 7 (1) counts the losses as *"three … (the `cls-*`
hybrids)"*. FLAT is not a loss, and nullability is not the reason those four
buy nothing.

**SO [OPT-4.1] LEAVES A RESIDUAL, and it is named rather than absorbed:** a
whole-subject-anchored form's rescue helps only the anchored regime, which the
bench does not measure for those cells, so it costs .so bytes for nothing. That
is a DIFFERENT question from nullability — the filter there can dismiss, it
just never runs in the regime the bench times — and it has no measured loss
attached, so under D77 it waits for one rather than getting a second predicate
here. **RULED a NAMED RESIDUAL** (manager, 2026-08-30) and landed as one in
`docs/spec/tuning.md` §2.17, so the bench can cite it rather than re-deriving
it from this report.

**THE MANAGER ACCEPTED BOTH CORRECTIONS AND IS CORRECTING I-21 WITH THE
BENCH** (2026-08-30): the two `nest*` whole cells keep their rescue AND their
bytes, and only the nullable `cls-*` cells decline. So the AFTER measurement
should expect movement on FOUR forms, not six — worth stating because a
prediction the bench cannot falsify is not a prediction.

**HOW THE PREDICTIONS ARE CONFIRMED IN PHASE 2:** compile each of the eleven
with `build/pcrec --features all -p rx -o -` (plain and, where listed, wrapped
as `(?:PAT)\z`) and read `RX_ENGINE_SEL` / `RX_VM_PREFILTER` /
`RX_VM_PREFILTER_LANG` / `RX_VM_PREFILTER_LANG_WHY`. A mismatch is reported as
a finding.

## 7. Bench ask (iv): `RX_DFA_PREFILTER "none"` beside `vm_prefilter=hybrid`

**INTENDED AND POPULATED — not unpopulated, and not "the axis does not apply
to a VM artifact".** The code line is `src/gen/emit_dfa.c:2414`:

    if (!start_acc && o->cand.usable)
        o->kind = o->cand.use_memchr ? DFA_PF_MEMCHR : DFA_PF_BYTE_CLASS;

Three facts make the answer:

1. **The axis DOES apply to a VM hybrid.** A hybrid inlines a full
   ENG_UNANCH/ENG_ATTEMPT scan and stamps the DFA scan's own two macros through
   `pcrec_emit_dfa_scan_stamps` — the SAME function the DFA-only artifact calls
   ([DD-13c]; `src/gen/emit_vm.c`'s comment at the call site says so, and
   `run_dfa_stamps.sh` asserts the iff both ways). So `RX_DFA_PREFILTER` on a
   hybrid describes the scan that hybrid contains.
2. **`"none"` is the CORRECT value there, for the same reason the pattern is a
   loss.** `unanch_start` selects a candidate-byte skip only when the start
   state cannot ACCEPT (`!start_acc`) — the skip must not pass a position at
   which the machine could report a match. A nullable language's start state
   accepts, so `start_acc` is true and the axis is `DFA_PF_NONE`. The dump's
   own row for that value already says it: *"always (fallback) — … and every
   case where the start state itself accepts (no skip is sound there)"*
   (`src/parse/axes_dump.c:102`).
3. **So it is a SECOND, INDEPENDENT derivation of this row's predicate**, from
   the built DFA rather than from the AST — which is exactly why the bench
   could read it as *"the one structured signal that separates the losing shape
   from the winning one BEFORE the run"*. It is not usable AS the predicate
   (it is available only after the machine the predicate exists to avoid
   building has been built), but it is a genuine cross-check: a pattern
   [OPT-4.1] declines should, if FORCED to collapse, produce a hybrid whose
   `RX_DFA_PREFILTER` reads `"none"`.

INFERRED (source read); to be confirmed in Phase 2 by compiling
`[a-z]{0,32768}` under `-fprefilter -fprefilter-collapse` and reading the two
macros together.

## 8. What waits on execution (Phase 2)

**TWO OF THESE ARE PRE-WRITTEN AND SYNTAX-CHECKED UNDER THE HOLD**, in the
session scratchpad (`.../scratchpad/opt41/`, never committed), so the lift
buys a RUN rather than an authoring session:

- `predict_check.sh` — items 8's eleven forms. The prediction is a LITERAL in
  its table, not prose, and a mismatch prints `MISMATCH` rather than being
  accommodated. It reproduces the bench's `(?:PAT)\z` whole-form spelling
  rather than assuming it, bounds every compile at 180 s (`cls-upto-32768`
  pays the wasted exact DFA build first — 7.0 s on the smaller `cls-upto-16384`
  at pin 96e44c2), and belongs in the background with a log.
- `nullable_census.py` — item 10. Its oracle and its cross-check are as
  specified below, with COVERAGE reported beside the count and disagreements
  NAMED. It compiles the whole corpus sequentially, so it is the LAST thing to
  run and never runs beside `test-corpus`.

Order for the box: build/strict, then the cheap check scripts, then the corpus
run, then axes, then mech one row at a time, then the two sweeps above.

1. `make -j4`, `make strict`.
2. `PROCS=4 make test-codegen` — the new §2/§6b/§7/§7b rows, and
   `run_dfa_stamps.sh`'s iff on the artifact kind §6b creates.
3. `make test-cli`; `PROCS=4 make test-corpus` once, async, expecting
   26,680/0, then `git checkout docs/dev/artifact_size_log.tsv`.
4. `make test-axes` if its runtime fits, else the
   `-fno-prefilter-collapse`/`-fprefilter-collapse` pair over the whole corpus
   by hand — the acceptance floor for any selection change (D-test-axes).
5. `tests/resource/run_resource_tests.sh` (the size-rung pair; it is not in
   `test-codegen`).
6. `tests/registry/axes_registry_check.sh` — the two new `RX_ENGINE_SEL` legs
   against the LIVE dump (the extractors were dry-run in Phase 1; the dump side
   needs a binary).
7. S206 and S207 one at a time through the matrix's ONLY filter, with
   `VALIDATE_ONLY=1` first; their `SAB_DOC_FIGURE`s carry `PENDING PHASE 2` and
   are to be filled from the canonical runs.
8. The eleven bench points compiled and their stamps checked against §6.
9. `--list-axes | grep engine-route` to confirm the new row, and
   `docs/spec/registry.md` line 203's stale `axis` value list (it names 19
   values and omits `engine-route`, `prefilter-lang` and the rest — the bench
   flagged the count as stale in O-10 item 8) re-derived from a live dump and
   FIXED in this row's spec pass. **NOT DONE in Phase 1** because it needs a
   run; flagged rather than guessed. **TAKEN BY THIS LANE** (manager,
   2026-08-30).
10. **THE D77 TRIGGER NUMBER** (manager, 2026-08-30, answering §9 item 2):
   count the corpus patterns whose EXACT prefilter language is nullable — i.e.
   hybrid artifacts with `pcrec_minw(root) == 0` — and record it here. No code
   change this row; the number is what a future row would be chartered on.
   Method: sweep every `pattern` line under `tests/`, compile at the default,
   keep the artifacts stamping `RX_VM_PREFILTER "hybrid"`, and split them on a
   nullability oracle **DERIVED SEPARATELY FROM `pcrec_minw`** — counting with
   the predicate under test would make the population agree with any defect in
   it (learnings §3). The oracle is **python3 `re`**: `re.compile(pat).match("")`
   IS nullability, external to pcrec entirely, and the corpus's own default
   tier already uses it. It is PARTIAL (python refuses possessive quantifiers,
   atomic groups and subroutine calls), so the report must carry the COVERAGE
   as well as the count — an oracle that silently skipped a third of the
   population would be a number nobody can read.

   `RX_DFA_PREFILTER "none"` (§7's second derivation) is a useful STRUCTURAL
   cross-check beside it but is NOT the oracle, and the difference is worth
   stating rather than discovering: `unanch_start` selects `DFA_PF_NONE` on
   `!cand.usable` as well as on `start_acc`, so it is a strict SUPERSET of
   nullable — a pattern beginning with `.` has an unusable candidate set and
   stamps `"none"` while being perfectly non-nullable. Report both counts and
   every disagreement, with the disagreements NAMED rather than summed.

## 9. Open questions — ANSWERED (manager, 2026-08-30)

All three were ruled the same day this report was filed; the rulings are
recorded inline below, against the question that asked them, rather than
replacing it — the question is what makes the ruling readable.

1. **The two `nest*` whole forms** (§6 rows 10-11) keep their rescue under this
   predicate and buy nothing measurable in the bench's regimes. Worth an
   [OPT-4.2]-shaped row, or left as a named residual under D77?

   **RULED: NAMED RESIDUAL under D77, no [OPT-4.2].** A measured FLAT is not a
   loss, and a rescue that buys nothing but bytes is revisited only if a loss
   appears. The residual sentence is LANDED in `docs/spec/tuning.md` §2.17 —
   in the spec rather than only here, so pcrec-bench can cite it.
2. **A nullable EXACT prefilter is equally useless**, by exactly the argument
   in §1 — a nullable language's filter can never dismiss, whether or not it
   was collapsed. This row deliberately does not touch the default exact
   prefilter: the bench measured only the rescue, the blast radius over the
   corpus is much larger (every nullable VM artifact would lose its prefilter),
   and D77 says wait for the measurement. The population is countable in Phase
   2 (`pcrec_minw(root) == 0` over the corpus's hybrids) and I can report it as
   the number that would trigger the row.

   **RULED: NO code change on the exact prefilter this row, but COUNT THE
   POPULATION in Phase 2 and record the number here** — it is the D77 trigger
   for a future row. Carried as §8 item 10, with the independent-oracle
   requirement stated there rather than left to the sweep's author.
3. **The size rung's decline stamps `RX_ENGINE_SEL "selected"`** — unchanged
   from what that rung already does when it collapses (the bench's finding
   8(b)), so the decline there is visible only as `RX_VM_PREFILTER "none"`.
   Making it a route value would mean reordering the ESEL ladder past
   `!dfa_disabled`, which changes what `"selected"` means for the size rung
   generally. Left alone; flagged.

   **RULED: LEAVE IT — and `[LIM-1]` OWNS THE DEFECT** (the bench's I-19 item
   3 folded it in already). Recorded here so nobody counts it twice: the size
   rung stamping `"selected"` is not an [OPT-4.1] residual and must not be
   re-opened as one. This row's only interaction with it is that a DECLINED
   size rung is likewise `"selected"`, visible as `RX_VM_PREFILTER "none"`.

---

# PHASE 2 — MEASURED

Everything below is MEASURED on the merged tree (lane/opt41 after
`Merge branch 'main' into lane/opt41`, w11f included) unless it says otherwise.

## 10. The merge, the build, and the first readings

| item | result |
|---|---|
| `git merge main` | ONE conflict, `docs/dev/lanes/CLAUDE.md` — both lanes appended an entry to the same list. Resolved keeping BOTH, w11f's first (it merged to main first). `docs/spec/limits.md`, `tests/mech/run_sabotage_matrix.sh` and `tests/mech/sabotages/CLAUDE.md` auto-merged and were each READ afterwards rather than trusted: my `[OPT-4.1]` block, my `pfcollapse` arm and w11f's `rxtsource` arm are all intact and no conflict marker survives anywhere in the tree |
| `make strict` (on the resolution, before committing it) | **rc 0** — "whole tree compiles clean with -Werror -Wshadow" |
| `make -j4` | rc 0 |
| `--list-axes` | 21 axes; `engine-route` carries `declined-nullable` at order 3 |

## 11. THREE CORRECTIONS THE RUN FORCED, all mine rather than the compiler's

### 11.1 §6b's witness was unusable twice over

`(?:SEL1)?` — §6's pattern made nullable, which Phase 1 chose because the two
would then differ by four characters — is not a witness at all:

| probe | result |
|---|---|
| `(?:SEL1)?` default | REFUSED, 2,487,847 emitted bytes > 1,000,000 |
| `(?:SEL1)?` `-fno-prefilter-collapse` | REFUSED, **2,487,847** — identical |
| `(?:SEL1)?` `-fno-prefilter` | REFUSED, **2,487,847** — identical |
| `(?:SEL1)?` `--max-emit-bytes=9000000` | compiles, and is a **DFA-ENGINE** artifact: `RX_ENGINE "dfa"`, `RX_ENGINE_SEL "selected"`, 2,500,874 B |

The identical refusal with the prefilter denied AND with it off entirely says
the size is the ENGINE BODY, not the prefilter — so no flag on this axis moves
it — and the raised-cap probe says the artifact takes **no VM prefilter
decision at all**. Neither is a defect in the predicate. **The lesson, recorded
in the check's own header: a witness for this row must be chosen for its
OUTCOME (a VM hybrid whose DFA overflowed), never by transforming a pattern
that has that outcome — nullability is not a property you can bolt on and keep
everything else fixed.**

The replacement is a pair MEASURED at 0.04 s each:

| pattern | SEL | PREFILTER | LANG | WHY | bytes |
|---|---|---|---|---|---|
| `(a\|b)*a(a\|b){15}` | `collapsed-prefilter` | `hybrid` | `count-collapsed` | `dfa overflow retry, exact nfa 20` | 47,152 |
| `(?:(a\|b)*a(a\|b){15})?` | **`declined-nullable`** | `none` | *(absent)* | *(absent)* | 34,723 |

One `?` apart, opposite sides of the predicate, and the declined artifact is
12,429 bytes smaller. `(a|b)*a(a|b){15}` is the classic exponential-DFA shape:
a 20-state NFA whose subset construction needs ~2^16 states, so it overflows
the cap without a large count and without a slow build.

### 11.2 §6b(3) was over-claiming, and the override lives elsewhere

The arm asserted that `-fprefilter` overrides the nullability decline. MEASURED,
it does not exercise that at all: `-fprefilter` makes `compile_driver`'s
`ovf_eligible` false, so on the **[SEL-1] rung the decline is never REACHED** —
the witness refuses with *"pattern too complex for the DFA engine (>32000
states)"*, which is pre-existing [SEL-1] behaviour and would refuse identically
with [OPT-4.1] reverted. The arm now asserts what it does show (a do-or-die
request is honoured or refused, never silently dropped — S64's failure mode)
and names where the override really lives.

**The override is only reachable on the SIZE rung, and it is now asserted
there** (`tests/resource/run_resource_tests.sh`), which is also the direct test
of the correctness gap §2 records me fixing on review:

| `(a\|b){0,30000}` | SEL | PREFILTER | LANG_WHY | bytes |
|---|---|---|---|---|
| default | `selected` | **`none`** | *(absent)* | 32,076 |
| `-fprefilter` | `selected` | **`hybrid`** | `size cap retry, exact 1333437 > 1000000` | 43,773 |
| `(a\|b){1,30000}` default (non-nullable twin) | `selected` | `hybrid` | `size cap retry, exact 1335175 > 1000000` | 46,006 |

The first two rows are the same pattern, so they also measure `limits.md`
§3.3's "dropping the prefilter is strictly smaller than collapsing it" on ONE
pattern rather than across two: 32,076 against 43,773.

### 11.3 `lang_witness`'s byte-identity leg was wrong for `exact-nullable`

It asserted the `-fprefilter-collapse` build is byte-IDENTICAL to the default,
on the reasoning that a flag which changed no language moved no byte. **A
DECLINE is a policy the artifact REPORTS**, so `_LANG_WHY` goes from `"exact"`
to `"nullable collapsed language"` and the builds differ by exactly 22 bytes.
Both rows went red on a correct compiler (`((a)|b){0,4000}` 298,389 vs 298,367;
`((a)|b){0,3}` 49,363 vs 49,341). The replacement is SHARPER than what it
replaces: the artifacts must differ in the `_LANG_WHY` line **and in nothing
else** — the flag reached a policy, said so, and moved no machine. Byte
identity could not have expressed the second half.

### 11.4 An operational trap, recorded because it cost a run

The first `run_prefilter_collapse.sh` run died mid-sweep with
`line 552: syntax error near unexpected token '('` on a line that had just
executed successfully. **The script was not broken** (`bash -n` clean before
and after): I EDITED IT WHILE IT WAS RUNNING, and bash reads a script lazily by
BYTE OFFSET, so the edit shifted the file under the running interpreter. The
`[sel]` results it had already produced are valid; everything after the edit is
noise. Never edit a shell script while a run of it is in flight — re-run
instead.

## 12. Checks — measured

### 12.1 `tests/registry/axes_registry_check.sh` — **83 passed, 0 failed**

The four new `RX_ENGINE_SEL` legs all pass, in both directions:

    PASS [RX_ENGINE_SEL] every dumped stamp_value (forced collapsed-prefilter
         declined-nullable overflowed-dfa overflowed-prefilter selected) is in
         docs/spec/match_api.md §6.3's own value-set table
    PASS [RX_ENGINE_SEL] every table value appears in --list-axes' output
    PASS [RX_ENGINE_SEL (pcrec_engine_sel_name)] both directions

So the dump, the spec table and the emitter's own `return` statements agree on
the six-value set — the leg that did not exist before this row.

### 12.2 The mech field validation — both rows `FIELDS OK`

`VALIDATE_ONLY=1 … S206` and `… S207` each print `FIELDS OK (definition parses
and every field validation passes; NO tree built, NO suite run, NOTHING
measured)`. Run before the rows themselves, as Phase 1 planned, because a
renumbered row is exactly where a malformed field surfaces.

### 12.3 The anchor tripwire — RED on arrival, and the cause is this row

`python3 scripts/m6read_check_sab_anchors.py` reported **2 STALE ANCHORS**,
`S102_prefilter_on_backref.sh` and `S165_prefilter_on_call.sh`, both against
`src/opt/select_engine.c`: adding the nullability conjunct moved the multi-line
`fit.prefilter` expression those two rows span in full.

**This is the THIRD time those two rows have moved for this exact cause** —
`tests/mech/sabotages/CLAUDE.md` already recorded [OPT-4] doing it twice — so
it is promoted there from an anecdote to a standing rule with the action
attached: if you add a conjunct to that clause, re-anchor S102 and S165 in the
same change and run the tripwire before believing anything else.

Re-derived from the text THIS change leaves behind (not `git show HEAD:` — the
lane's own edit is what invalidated them, which is the case that file
distinguishes). **Verified beyond the tripwire**, which only proves an anchor
is FINDABLE: S102, S165, S206 and S207 were each applied to a scratch copy
through `tests/mech/lib/replace.py` — the driver's own mechanism — and the
result `gcc -fsyntax-only`'d. All four apply at exactly `SAB_COUNT` sites and
produce compilable C. Tripwire now: **all anchors resolve, 203 sabotages / 214
anchor sites**.

### 12.4 The answer-identity floor: the PAIR, not the full sweep

`make test-axes` is ~14 full corpus passes plus the form census
(`docs/testing.md`, "Answer-identity sweep"). This row changes ONE axis, so the
delivered acceptance is the deny/force pair that axis owns, run through the
tree's own instrument rather than by hand:

    AXES="-fno-prefilter-collapse -fprefilter-collapse" bash tests/axes/run_axes.sh

three corpus passes (baseline + two axes) with `run_axes.sh`'s own RXTDUMP
answer comparison, which compares span AND every capture slot per case. **This
is deliberately NOT the full `make test-axes`** — that script's own header
calls an `AXES`-scoped run "a QUICK check, not the delivered run" — and the
report says so rather than letting a scoped run be read as the delivered one.

**RULED (manager, 2026-08-30): the scoped pair IS this row's delivered
answer-identity evidence, and the reason is recorded here so it does not
become precedent by silence.** The predicate is read on exactly one axis's
path (the collapse rescue); that axis's own deny/force pair IS swept over the
whole corpus with span and every capture slot compared; and the other axes'
interactions with this path were swept in full when [OPT-4] landed. A 14-pass
sweep would re-prove axes this change cannot reach. **The standing condition:
if the battery or the bench's AFTER ever contradicts answer-identity on ANY
axis, the full sweep runs BEFORE diagnosis** — the scoped run is evidence for
this change, never a substitute for the instrument.

### 12.5 `tests/codegen/run_prefilter_collapse.sh` — **58 passed, 0 failed**

Every `[OPT-4.1]` row green, and the two the row was built for read:

    PASS [sel1n] the NON-nullable twin is rescued: SEL 'collapsed-prefilter'
         / PREFILTER "hybrid" / LANG "count-collapsed"
    PASS [sel1n] the NULLABLE overflow witness declines the rescue:
         RX_ENGINE_WHY 'dfa overflowed: >32000 states at pattern offset 0'
         beside RX_VM_PREFILTER "none" / RX_ENGINE_SEL "declined-nullable"
    PASS [sel1n] ...and carries no RX_VM_PREFILTER_LANG (§6.3's iff)
    PASS [sel1n] ...and -fno-prefilter-collapse on the SAME pattern reads
         'overflowed-dfa' / "none"
    PASS [sel1n] -fprefilter on the nullable witness is REFUSED
    PASS [why]  '((a)|b){0,4000}' … DECLINED under -fprefilter-collapse
                ('nullable collapsed language')
    PASS [why]  '((a)|b){0,3}' … same
    PASS [sel]  route 'declined-nullable' is reachable (vm/none)

The `-fprefilter` refusal is now the GENUINE do-or-die one — *"-fprefilter
requires the VM engine; this pattern compiles to the DFA engine"* — because the
capture-free witness is DFA-selected before the overflow. On the capturing
spelling it was the DFA state cap instead. Either way a refusal, never a silent
drop; §6b's comment records that neither is the [OPT-4.1] override.

**IT TOOK THREE RUNS AND EACH RED WAS MINE**, which is worth listing because
none of them was the compiler:

| run | result | cause |
|---|---|---|
| 1 | died mid-sweep, `line 552: syntax error` | I edited the script while bash was executing it (§11.4) |
| 2 | 56 passed, **1 failed** | my `[sel1n]` case arm demanded `RX_ENGINE_WHY` name the overflow; the capturing witness reads *"capture group at pattern offset 3"* — correct, and about a different route (a capture forces the VM on its own, so only the PREFILTER's DFA overflowed) |
| 3 | **58 passed, 0 failed** | witness made capture-free, which is the [SEL-1] rung in its documented shape |

Run 2's failure also bought the (2b) arm: the capture-free pair let the SAME
pattern be read at the default (`declined-nullable`) and denied
(`overflowed-dfa`), which is the sharpest statement of why the value exists.

### 12.6 `make test-cli` — **287 cases passed, 0 failed**

Unmoved by this row, which is the expected result: nothing here changes a CLI
surface. Recorded because the brief asks for it and because `run_cli_tests.sh`
is where the D37 feature-stamp and `--list-*` field counts are pinned, and this
row touched `--list-axes`' row set.

### 12.7 Rebuild after the `--emit-ir` wording fix — `make -j4` + `make strict` rc 0

The listing's prefilter line carried the SAME over-claim §11.2 records in the
check ("-fprefilter overrides (do-or-die)"), which is true on the size rung and
false on the [SEL-1] rung. It now states both, so an artifact from either rung
reads a line that agrees with `tuning.md` §2.17. Verified live on the declined
witness:

    ; prefilter    NO (nullable collapsed language) -- a ladder rung offered
                   the count-collapsed prefilter ([OPT-4]) and it was DECLINED
                   … -fprefilter is do-or-die and is never silently dropped: on
                   the size rung it OVERRIDES this decline, on the [SEL-1] rung
                   it suppresses the rung itself and the compile refuses.
                   -fprefilter-collapse does not override it

That is the predicate's THIRD reader working, and it is the one that would
otherwise have named a flag the caller did not pass.

### 12.8 `make test-codegen` — **5/5 scripts, 198 checks, 0 failed**

`run_codegen_tests.sh` 106/0, `run_dfa_stamps.sh` 31/0, `run_offset_skip.sh`
22/0, `run_size_term.sh` 32/0, `run_trie_identity.sh` 7/0. Zero `FAIL`/
`MISMATCH` lines anywhere in the group.

The row to read is the tree's own verdict on §12.3's re-anchors:

    PASS [SABANCHOR] scripts/m6read_check_sab_anchors.py: all 203 sabotage
         rows' anchors resolve

`run_prefilter_collapse.sh` is NOT in this group — it is its own section,
`make test-prefilter-collapse` (its header records the corpus sweep at a
MEASURED 151 s, which is why it is kept out of `smoke`'s budget). Its result is
§12.5.

### 12.9 A fifth copy of the flag over-claim, and where it was

The sweep for `overrides the decline` found the sentence in FIVE places, not
one. Four were docs; the fifth was `src/parse/axes_dump.c`'s `engine-route` row
description — **which reaches a user, through `pcrec --list-axes`**. All five
now state the rule per rung. The `axes_dump.c` edit was deliberately HELD until
`test-codegen` finished, because `run_trie_identity.sh` in that group builds a
reference compiler from `src/` and a half-written file would have failed it for
a reason unrelated to anything — the same class of hazard as §11.4's, avoided
this time rather than learned again.

Its neighbouring illustrative claim was corrected in the same edit and is now
MEASURED rather than approximate: `RX_ENGINE "vm"` is reachable by EVERY one of
the six routes (`forced` via `--engine=vm`, `selected` via any capture-bearing
pattern, and the four fallback routes always), which is a stronger statement of
the two axes' independence than the "four of the five" it inherited.


### 12.10 `make test-corpus` — **26,680 cases passed, 0 failed**

`PROCS=4`, one run, the number the brief predicted exactly. The size log's
tripwire passed inside it (`2878 rows … worst size 651,646 B … worst gcc CPU
2.397 s`, both inside their pins), and `docs/dev/artifact_size_log.tsv` was
restored with `git checkout` afterwards, so the tree is clean and the log is
still the pinned one.

**This is the answer-identity floor doing its job at its widest**: every one of
those 26,680 cases would pass whether the collapse fires, does not fire, or
fires where the bench measured it costing 1.2-9.9x. That it is green says the
change is answer-preserving; it says nothing about whether the predicate is
right, which is what §12.5's structural rows and the mech pair are for.

### 12.11 The scoped answer-identity pair — **both axes OK, 0 mismatches**

    -fno-prefilter-collapse (bit 19) | OK | keys_base=22114 keys_axis=22114
        agree=22114 budget=0 refused=0 lost=0 gained=0 mismatches=0 | 176s
    -fprefilter-collapse    (bit 20) | OK | keys_base=22114 keys_axis=22114
        agree=22112 budget=2 refused=0 lost=0 gained=0 mismatches=0 | 181s
    oracle cross-check: OK — both PC-4 runs 0-failure against live libpcre2
    total wall 553s

22,114 keys per axis, each key a case's span AND every capture slot. **Zero
mismatches, zero lost, zero gained** in both directions — the acceptance floor
this row owes.

**THE `budget=2` IS NAMED RATHER THAN WAVED AT.** Both are
`tests/base/d27_k23_ambiguous_decomposition.rxt:90` and `:98`, and they are
RULING B'S OWN REVERSAL WITNESS: `docs/design/prefilter_count_independence.md`
§10a records `(a{1,3}){65}` going from answering in 0.00 s to exhausting the
step budget under a forced collapse, because a superset prefilter cannot supply
the `prefilter-window` ceiling those cells depend on. `run_axes.sh` classifies a
give-up on one side as `budget-bound`, "not an answer disagreement, never a
failure", which is why the axis reads OK.

**AND MY PREDICATE DOES NOT TOUCH THEM**, which is worth stating because it
would be an easy thing to claim credit for: `(a{1,3}){65}` has `minw` 65, so it
is NOT nullable, the decline never fires on it, and it is budget-bound under
`-fprefilter-collapse` exactly as it was before this row. Those two cells are
ruling B's territory, not [OPT-4.1]'s.

### 12.12 A bug in my own Phase-2 instrument, found by a cross-check

`predict_check.sh`'s table used `|` as its field separator — and FIVE of the
eleven patterns CONTAIN `|` (every `ctx` row's `(?:fail|abort|panic)`, and
`level-context`). `IFS='|' read` split those patterns mid-alternation and
shifted every later field, so the script would have compiled `\b(?:fail` and
compared its stamps against the string `panic)\b.{0,64}?\b(?:disk`. It would
have reported eleven MISMATCHes against a compiler that was right.

**It was found by cross-checking the SCRIPT's expectations against the
REPORT's §6 table** — two artifacts written separately, hours apart, which is
the only reason the mismatch was visible at all. A single source would have
been self-consistent and wrong. The separator is now `0x1f`, which no regex can
contain; all eleven rows re-verified to parse into six fields with their
patterns intact and their expectations identical to §6.

This is the second delimiter collision in this lane (the first cost only a
throwaway probe, where `IFS=':'` met `(?:`) and the third instrument bug found
before it ran, after the misleading `$?` and the addendum placed below the
verdict. All four were mine; none reached a measurement.
