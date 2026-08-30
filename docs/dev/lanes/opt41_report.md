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
with its opposite. Implemented as `&& !force_on` on
`fit.prefilter_declined_nullable`. `-fprefilter-collapse` does NOT override it:
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

| row | plant | detectors | corpus |
|---|---|---|---|
| **S205** predicate REMOVED (`= false`) | the rescue is built again on nullable languages — the bench's 1.2-9.9x | `pfcollapse` §6b, §7b's `declined-nullable` witness, §2's two `exact-nullable` rows; `resource`'s nullable cell ALONE (its twin stays green, which is what says a PREDICATE was removed rather than the rung) | EXPECTED `0fail` |
| **S206** predicate INVERTED (`!= 0`) | the rescue is declined on the 2.2-4.6x winners and kept on the losers | `pfcollapse` §6, §2's six `count-collapsed` rows, §7b's `collapsed-prefilter` witness; `resource`'s BOTH cells | EXPECTED `0fail` |

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
here.

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
7. S205 and S206 one at a time through the matrix's ONLY filter, with
   `VALIDATE_ONLY=1` first; their `SAB_DOC_FIGURE`s carry `PENDING PHASE 2` and
   are to be filled from the canonical runs.
8. The eleven bench points compiled and their stamps checked against §6.
9. `--list-axes | grep engine-route` to confirm the new row, and
   `docs/spec/registry.md` §203's stale `axis` value list (it names 19 values
   and omits `engine-route`, `prefilter-lang` and the rest — the bench flagged
   the count as stale in O-10 item 8) re-derived from a live dump. **NOT DONE
   in Phase 1** because it needs a run; flagged rather than guessed.

## 9. Open questions for the manager

1. **The two `nest*` whole forms** (§6 rows 10-11) keep their rescue under this
   predicate and buy nothing measurable in the bench's regimes. Worth an
   [OPT-4.2]-shaped row, or left as a named residual under D77?
2. **A nullable EXACT prefilter is equally useless**, by exactly the argument
   in §1 — a nullable language's filter can never dismiss, whether or not it
   was collapsed. This row deliberately does not touch the default exact
   prefilter: the bench measured only the rescue, the blast radius over the
   corpus is much larger (every nullable VM artifact would lose its prefilter),
   and D77 says wait for the measurement. The population is countable in Phase
   2 (`pcrec_minw(root) == 0` over the corpus's hybrids) and I can report it as
   the number that would trigger the row.
3. **The size rung's decline stamps `RX_ENGINE_SEL "selected"`** — unchanged
   from what that rung already does when it collapses (the bench's finding
   8(b)), so the decline there is visible only as `RX_VM_PREFILTER "none"`.
   Making it a route value would mean reordering the ESEL ladder past
   `!dfa_disabled`, which changes what `"selected"` means for the size rung
   generally. Left alone; flagged.
