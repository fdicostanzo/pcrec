# LANE dd8 — [DD-8] `--emit-ir` adopts `docs/spec/table_contract.md`

Branch `lane/dd8`, branched from `main` at `7ee40500`. D106 and its three
addenda, D108. Four commits, one new spec document, eleven test scripts
converted, sixteen baselines deliberately recaptured, six sabotage rows
re-driven solo.

---

## 0. THE HEADLINE: the scope question this row carried for a month answered
itself in the format, and the answer is that there was never a second contract

D106 left open whether the adoption was (a) the tabular sections only or (b)
that PLUS a new sibling line-oriented contract for the PROGRAM body, and the
manager's own lean was to decide (b) separately after seeing whether (a)
quieted `run_ir_listing.sh`. Frank's addendum item 1 settled it by ruling
machine-first output, and building it confirms the ruling's premise
concretely: **the program body needed five columns and nothing else.**
`label|op|args|target|note` carries every one of the twelve instruction kinds
the `VEvent` walk emits, including the two — `call` and `cut` — whose operands
looked least like a table. No construct in the listing had to be bent to fit,
and no flat-schema contortion was needed anywhere.

The second thing the build says, and it is the one a later customer should
take: **adopting the contract was not mainly a formatting change, it was a
change in what the listing can be ASKED.** Three of its facts were previously
recoverable only by knowing a sentence's shape — which rung kinds this
artifact used, why it has no prefilter, whether its MRL ceiling is the
prefilter window — and all three are now a column value with a fixed
vocabulary. The `prefilter` reason in particular went from "one of eight
prose paragraphs, matched by needle" to one of nine tokens matched by
equality, which is the difference between a check that passes when a word
appears anywhere in a long sentence and a check that passes when the compiler
made the decision it claims.

---

## 1. The commits

| commit | what |
|---|---|
| `1ae7e774` | `tests/lib/table.sh` gains the sections mechanism's ROW-reading half (`table_section_rows`, `table_field`, `table_lookup`) |
| `b8573925` | the adoption: `vm_render_listing` renders nine `#section` TSV blocks through the kit; every reader re-pinned; the spec hunks |
| `8e7c960f` | re-pins: the directory `CLAUDE.md`s and `plan.md`'s `[DD-8]` row |
| (this) | the report |

The order is forced by one fact: **the listing text moves WHOLESALE**, so a
section-by-section adoption across commits would leave every consumer red in
between. `b8573925` is therefore large and coherent rather than small and
broken — the renderer, all eleven consumers, the recaptured baselines and the
spec hunks are one change because a reader and the thing it reads cannot be
separated by a commit boundary. The one piece that COULD land first did:
`table.sh`'s new functions change no existing behaviour and were committed
alone so the diff of the big commit contains no library design.

---

## 2. The format, and the design calls inside it

Nine named sections, no anonymous table:

| section | columns |
|---|---|
| `summary` | `fact` `value` `note` |
| `slots` | `family` `slot` `holds` `note` |
| `rungs` / `strategies` / `pruning` | `label` `kind` `detail` |
| `program` | `label` `op` `args` `target` `note` |
| `choicepoints` | `label` `resume` `note` |
| `islands` | `label` `width` `note` |
| `callouts` | `label` `note` |

`docs/spec/ir_listing.md` is the contract; what follows is only what was
DECIDED here and why.

### 2.1 A `#` line may never follow a section's data, and that rule decided the shape of every empty population

Contract rule 3 makes the LAST `#` line before a section's first data row
that section's HEADER. So a trailing `#` remark inside an EMPTY section would
silently BECOME its column list, and every conforming consumer would then
read a comment as a header. The old listing's empty populations were exactly
such remarks (`  (none: no cursor rung in this program)`).

They are therefore **rows**: cells empty, sentence in the `note`. Two things
follow that are worth more than the rule. First, it costs nothing — an empty
field already means "none" (rule 5), so a row with an empty `slot` is a
conforming way to say "this family reserves none". Second, **it is what lets
the reach census count an empty arm at all.** w2y §3.3 had to re-walk 3,518
listings and classify them by section to prove the empty-population sentences
still rendered; here that is a projection of a declared column.

### 2.2 `slots` gains a FAMILY column, and it is the fix for a named failure

Before this, a reader told the six slot families apart by recognising their
`holds` PROSE. w2y §3.3 records a reach census defeated by exactly that:
three families' markers were substrings of another family's own
none-sentence, so two read 3,518 instead of 324 and 463, and one read 0.
`family` is now a declared column with a seven-value vocabulary, and every
family emits at least one row. "Which families does this artifact use" is a
projection, not a guess.

`group` is the one family whose `slot` cell is a PAIR (`2,3`), because a
capture group owns its start and end together and the written verdict is a
property of the pair. `revdet` is the one family with three rows per index
and is the one that still cannot use the shared helper, for w2y's reason
(output order).

### 2.3 The `prefilter` value is nine tokens and the prose moved to `note`

Every arm of that eight-way chain has a load-bearing ORDER — four
construct/analysis routes tested before the two flag routes, so the listing
never names a flag the caller did not pass — and every arm was a paragraph a
consumer matched by needle. The order is unchanged. Each arm now also yields
a token:

`yes` · `yes-collapsed` · `no-backreference` · `no-linked-call` ·
`no-nullable-collapsed` · `no-nullable-exact` · `no-dfa-overflow` ·
`no-fno-prefilter` · `no-engine-vm`

The conversion made `tests/prefilter` STRICTLY stronger and the old form's
weakness is worth recording: `check_ir_line "forced back on" 'yes'` passed
whenever the three-letter substring `yes` appeared anywhere in the reason,
and several of the OFF-route sentences contain it. The one claim a token
cannot carry — the [SEL-1] route's cap NAME, `dfa overflowed: >32000 states`
— is asserted separately against the `note`, by a second helper, because that
is a substring of prose whose wording D26 explicitly does not make a
contract.

### 2.4 `prune-ceiling` deliberately borrows the artifact stamp's vocabulary

The listing is the FOURTH reader of `v.mrl_win` (design §9.3 S-LA13) and R31
E3's whole defect was the stamp disagreeing with the code beside it. Its
value now uses the same three words `<PREFIX>_VM_PRUNE_CEILING` uses —
`none` / `prefilter-window` / `subject-end` — so `run_codegen_tests.sh`'s
rule 1(d) compares the two by EQUALITY instead of counting occurrences of a
prose phrase.

**This is not two sources collapsing into one.** The two remain computed
independently, at different sites, from `v.mrl_win` and `v.nclamp`; what
changed is only that the comparison no longer depends on a sentence's
wording. The one asymmetry is recorded in the spec: the listing's `none`
means `-fno-length-prune` and the stamp's means "no bound site emitted", so
they agree on every artifact that clamps — which is the population the
codegen rules are already scoped to (they assert `stamp != none` first).

### 2.5 Facts that were sentences became rows

`; capacities N resume frames, M trail entries (subject ceiling K bytes)` is
three `summary` rows (`resume-frames`, `trail-entries`, `subject-ceiling`);
the PRUNING section's three-line prose head is three more (`prune-ceiling`,
`prune-bound-sites`, `prune-retreats`); `DFA ISLANDS (N)` / `CALLOUT SITES
(N)` are two more, leaving those sections to carry rows. A consumer that
wants the trail capacity now asks for the trail capacity.

`possessify` is the one value that is a PAIR in a cell (`1/1`,
marked/total) and is EMPTY under `-fno-possessify` — deliberately, because
`0/0` would read as "this program has no quantifiers", which is a different
fact and usually a false one.

### 2.6 Code-side: one general mechanism replaced two special cases, and one primitive retired

`vm_rungs_describe` and `vm_strats_describe` were the same twelve-line
program twice and are now one `vm_mask_names(v, mask, bits, names, n)`.
`vm_listing_events`'s `namew` column-width argument is GONE with the padding
(D106 addendum 3, Q3), which retires w2x §8's `%-*s`-at-width-0 blind spot
rather than documenting it for a third time.

**Every cell is a literal or an ARENA fragment (`vm_rolef`), never a shared
scratch buffer**, and that is forced by the format rather than chosen: a TSV
cell is a `const char *` handed to `sb_row` ALONGSIDE ITS SIBLINGS, so a cell
built into `Job.scr_desc` would be clobbered by the next cell of the same
row. The two sites that do use `scr_desc` (the pattern text, the class
description) each build ONE cell and hand it over immediately; the code says
so at both.

The pattern cell is pre-framed with `sb_textn` because `cx->pat` is
bytes-plus-length, not a C string. Running `sb_text` over that a second time
inside `sb_row` is a no-op BY CONSTRUCTION — its output contains no byte
`sb_text` escapes — and the site records the argument rather than leaving a
reader to re-derive it.

**One deliberate content change, flagged here rather than buried:** a byte in
`0x80..0xff` in the pattern now passes through RAW where the old listing
spelled it `\xNN`. `sb_text` is the vocabulary every registry TSV dump uses
and it protects the FRAME without transcoding content; a raw high byte in a
TSV field is what the six dumps already carry. This is the only place where
what the listing SAYS changed rather than how it is arranged.

---

## 3. Byte-neutrality — THE `.c` DID NOT MOVE, on a validated instrument

Against a pinned branch-point binary built from `git archive 7ee40500` into
the session scratchpad. Population: **3,159 unique corpus argv rows**
(`^pattern ` over `tests/**/*.rxt`) and **305 source files**, all at
`--features all`.

| arm | reach | movers |
|---|---:|---:|
| corpus argv, `.c`, default engine | 2,803 | **0** |
| corpus argv, `.c`, `--engine=vm` | 2,804 | **0** |
| composition, `--source` over every `.rxt`/`.rxtin` | 32 producing files / 96 artifacts | **0** |
| **positive control**: corpus argv, `--emit-ir` | 2,804 | **2,804** |

Zero asymmetric rows (one side compiling, the other refusing) on either
`.c` arm. **NOT an abi event**: no emitted scaffolding byte moves, so no
`abi` bump and no identity-gate re-pin are owed.

The composition arm reproduces w2y §3.2's figures exactly — **32 producing
files / 96 artifacts at `--features all`** — which is the first independent
confirmation of that number since w2y measured it and disagreed with w2x's
recorded 30/72.

### 3.1 THE INSTRUMENT'S FIRST RUN READ 100% MOVERS AND THE COMPILER WAS INNOCENT

The first driver compiled the reference side to `-o a.c` and the new side to
`-o b.c`. Every one of the first several hundred rows came back a MOVER.

The cause is that **the emitted `.c` contains `#include "<basename>.h"`,
derived from `-o`** — so two different output NAMES are two different
artifacts by construction and the instrument was measuring its own argv. The
fix is that both sides write `gen.c` and only the DIRECTORY differs.

It is worth a paragraph rather than a line because the failure is the
INVERSE of the one every prior lane's byte sweep was validated against. w2a,
w2x and w2y all validated against a sweep that reads a FALSE GREEN — too
little reach, an arm that never fires. This one read a false RED, loudly and
immediately, and a lane that had trusted it would have spent a session
hunting a byte move in a change that moves no bytes. *A byte-identity
instrument must vary NOTHING the artifact can observe, and the artifact can
observe its own output filename.*

### 3.2 The positive control is why the two greens mean something

w2y §3.3 records that this change's stream has no `.c` identity gate, so the
brief required the reach to be stated. The stronger form used here is an arm
that MUST be red: the `--emit-ir` stream itself, over the same population.
It reads **2,804 movers of 2,804**, so the instrument demonstrably sees a
difference when one exists, and the `.c` arms' zeros are evidence rather than
blindness.

---

## 4. The listing's own conformance and REACH, measured independently

### 4.1 Conformance: 2,804 listings, ZERO contract violations

A scratch checker re-implements `docs/spec/table_contract.md`'s rules
directly in python — comment-skip, "the last `#` line before a section's data
is its header", header truthfulness, no TAB inside a field — and
**deliberately does NOT use `tests/lib/table.sh`.** table.sh is the tree's one
CONSUMER implementation and this instrument checks the PRODUCER; sharing the
parser would make the check agree with whatever table.sh happens to tolerate,
which is learnings.md §3's control-shares-a-source-with-what-it-controls
shape.

Over all 2,804 listings the corpus produces under `--engine=vm --features
all`: nine sections present in the declared order on every one, no header
missing, no row whose field count disagrees with its own header, no TAB in
any field, no comment after data, no data row outside a section.

### 4.2 REACH: every section renders rows, and every empty arm renders too

| section | listings | data rows | of which the empty-arm row |
|---|---:|---:|---:|
| `summary` | 2,804 | 56,086 | — |
| `slots` | 2,804 | 23,302 | — |
| `rungs` | 2,804 | 5,422 | 1,588 |
| `strategies` | 2,804 | 5,422 | 1,588 |
| `pruning` | 2,804 | 5,422 | 1,588 |
| `program` | 2,804 | 116,751 | — |
| `choicepoints` | 2,804 | 7,298 | 1,523 |
| `islands` | 2,804 | 2,823 | 2,753 |
| `callouts` | 2,804 | 2,804 | 2,804 |

Slot families, rows / of which the empty-family row: `group` 4,292/0,
`guard` 3,803/2,513, `low` 3,764/2,402, `mark` 2,824/2,579, `revdet`
2,919/2,748, `lookmark` 2,865/2,325, `lookpos` 2,835/2,292. **Every family
renders real rows and every family renders its empty arm** — `revdet`, the
thinnest, on 171 listings.

All **twelve** `program` `op` values render: `label` 42,689, `goto` 25,534,
`set` 12,427, `fail` 9,481, `note` 7,651, `consume` 7,415, `push` 5,775,
`accept` 2,804, `assert` 1,388, `cut` 834, `call` 418, `return` 335.

`callouts` is empty on every artifact, which is correct and is not a gap:
module `callouts` has no producer. The section renders a row per event the
day one lands — the shape `islands` already proved.

### 4.3 The one arm nothing reaches, and it is NOT this change's

`--engine=vm` turns the prefilter off, so pass 1 could reach only three
`prefilter` tokens by construction. A second pass over seven flag axes
(default, `-fno-prefilter`, `-fno-possessify`, `--fno-step-budget`,
`-fprefilter-collapse`, `-fno-prefilter-collapse`, `--backtrack-frames=8`),
**10,640 listings**, reaches seven more:

`yes` 7,011 · `no-fno-prefilter` 1,204 · `no-backreference` 1,127 ·
`no-nullable-exact` 637 · `no-linked-call` 448 · `yes-collapsed` 212 ·
`no-dfa-overflow` 1 — plus pass 1's `no-engine-vm` (2,579). **Eight of nine.**

`no-nullable-collapsed` ([OPT-4.1], the rung-scoped decline) is reached by
NOTHING, at any flag axis, and three hand-built witnesses could not reach it
either. The structural reason: `prefilter_declined_nullable` requires
`collapse_reason != CR_NONE` (a ladder rung must have OFFERED the collapsed
rescue), but on a nullable pattern [OPT-4.2]'s `prefilter_declined_nullable_
default` fires first, at the ORDINARY hybrid, and declines the prefilter
before any rung can be offered — and the count-collapse rule (`X{m,n}` to
`X{min(m,1),}`) can never make a language nullable that was not nullable
already.

**This is a PRE-EXISTING property of the [OPT-4.1] predicate, not something
this change introduced**, and the argument is structural rather than
measured: the arm's predicate and its position in the chain are unchanged by
this lane, so its reachability is identical before and after by construction.
It is recorded here because it is a live arm of a shipped diagnostic that no
input can print, which is a finding [OPT-4.1]'s own row should own. Not
touched here — a decline's reachability is not a rendering question.

The other conditional arms all render: `root-minw` present on 42 listings,
`subject-ceiling` non-empty on 1,740, `step-budget` empty on 1,520,
`possessify` empty on 1,520, `prune-ceiling` reaching all three values
(`prefilter-window` 2,836, `subject-end` 7,804, and `none` under
`-fno-length-prune`).

---

## 5. Every reader re-pinned, and what each conversion bought

Found by `grep -rl "emit-ir" tests/ docs/ tools/ cli/ src/` on this tree and
narrowed to the files that PARSE the listing (the rest are prose). **Eleven
scripts, all converted to declaration-based parsing; none re-pinned as a
grep.**

| file | what it read | now |
|---|---|---|
| `tests/codegen/run_ir_listing.sh` | 7 fixed-position greps | `program`/`choicepoints`/`summary` by name, + a NEW contract arm |
| `tests/codegen/run_codegen_tests.sh` | `grep -c 'ceiling: min(subject_length, …)'` | `summary` `prune-ceiling` value, by EQUALITY |
| `tests/prefilter/run_prefilter_tests.sh` | 12 needles in the `; prefilter` sentence | `prefilter` VALUE equality + 2 note-needle rows |
| `tests/vm/run_vm_tests.sh` | 4 `grep -cE '^  at L[0-9]+ +kind '` + a padded summary line | `rungs` `kind` counted whole; `summary` `rungs` by equality |
| `tests/mrl/run_mrl_tests.sh` | `grep -q '^PRUNING'` | `pruning` `kind` rows counted |
| `tests/counterk/run_counterk_tests.sh` | `grep -q 'counter'` over the WHOLE listing | `rungs` `kind`, matched whole |
| `tests/possessify/run_possessify_tests.sh` | `sed` line-range + substring | `strategies` `kind`, one compile instead of two |
| `tests/rungselect/run_rungselect_tests.sh` | `sed` line-range + 3 `sed -n 's/^; …/'` | `rungs` `kind`; `summary` rows for replicas/capacity/ceiling |
| `tests/rungselect/run_rungdiff.sh` | `sed -n 's/^; rungs …/'` | hoisted index + one `awk` |
| `tests/counterk/run_counterkdiff.sh` | same | same |
| `tests/possessify/run_possdiff.sh` | `sed -n 's/^; possessify N of …/'` | same, splitting the `marked/total` pair |

Three conversions found a weakness rather than merely surviving:

1. **`tests/counterk` grepped the word `counter` over the ENTIRE listing.**
   The `summary` `rungs` row, a role string and a prose sentence all satisfy
   that. It now matches the `rungs` section's `kind` column WHOLE.
2. **`tests/vm` pinned the listing's COLUMN PADDING** — the pattern
   `'^; rungs        cursor, frames-bounded, frames-unbounded, revdet '`
   carries eight literal spaces and a trailing one. D106 addendum 3 has since
   ruled that width is not a contract; the check now compares the value.
3. **`tests/prefilter`'s `yes` needle** matched a substring of several
   OFF-route sentences (§2.3).

### 5.1 The hot loops keep one `awk`, and that is still declaration-based

The three `--corpus` derivation arms run their read ~3,000 times. Composing
`table_lookup` there would add roughly seven processes per pattern. Instead
the COLUMN INDICES are resolved by name ONCE, from a probe listing at the top
of the arm, and the per-pattern read is a single `awk` using them — the same
process count the old `sed -n` cost. A renamed section or column is a loud
failure at the hoist rather than an empty string every iteration that reads
like "no pattern in the corpus selects this rung". **This is the shape any
future hot consumer of a sectioned dump should copy.**

### 5.2 `tests/lib/table.sh` gained the mechanism's reading half

`table_col_index` resolved a COLUMN; nothing resolved the ROWS, which is why
every consumer still hand-rolled a positional read. `table_section_rows`,
`table_field` and `table_lookup` close that, each failing LOUDLY on an absent
section, column or key — because a silent empty return is indistinguishable
from a population that legitimately has no rows.

### 5.3 `run_ir_listing.sh` gained a CONTRACT arm, and its section list is written down rather than discovered

Nine sections asserted present and header-truthful, per pattern. **The list
is spelled out in the check rather than read from the producer**: discovering
it from the listing would make the arm agree with any producer, which is the
same control-shares-its-source defect §4.1's instrument avoids one level up.
128 checks became 144.

---

## 6. Anchors — NONE MOVED; six rows RE-DRIVEN because what moved is what their CHECKS read

**Anchor integrity over the whole tree: 268 rows / 284 anchor sites / 0
unresolved**, unchanged from the branch point and re-measured after every
commit.

No `SAB_BEFORE` text lies inside `vm_render_listing`. The rows the brief
names are anchored elsewhere — S88 and S141 at the MRL ceiling BUILDERS
(`emit_vm.c:11469`, `:11556`), S216 in `select_engine.c`, S258 in `vm_alt`,
S41 at `vm_lbl`, S42 at `vm_ev` — so **a re-aim would have been wrong; what
this change moves is the TEXT THEIR DETECTING CHECKS READ.** Re-driven solo
at `8e7c960f`, each its own matrix invocation.

S41 and S42 are not on the brief's list and were added by re-running the
grep: both are `irlisting` rows whose detection routes entirely through
extractors this lane converted, so a conversion that had quietly stopped
reading the listing would have left them green.

| row | anchor site | suites moved | verdict |
|---|---|---|---|
| S41 | `vm_lbl` call (accept label) | `irlist:33fail/110pass` | **DETECTED** |
| S42 | `vm_ev(v, VE_PUSH, …)` | `irlist:17fail/127pass` | **DETECTED** |
| S88 | H3 site 1, the search ENTRY builder | `codegen:3fail/106pass, corpus:0fail/53pass, atomicdiff:0fail/8pass` | **DETECTED** |
| S141 | H3 sites 1 and 2, both builders | `codegen:3fail/106pass, irlist:0fail/144pass` | **DETECTED** |
| S216 | `select_engine.c`'s [OPT-4.2] fit site | `prefilter:2fail/32pass` | **DETECTED** |
| S258 | `vm_alt`'s alternation-entry role text | `irlist:5fail/139pass` | **DETECTED** |

Every trailer reads `1 rows (unexpected: 0, undetected: 0, unreached: 0,
anomalies: 0, oracle-skipped: 0)`. **Unexpected: 0. Undetected: 0.
Anomalies: 0.**

**S141's disjointness prediction HOLDS and is now stronger.** Its
`SAB_DOC_FIGURE` predicts `irlisting` GREEN — the `--emit-ir` reader of
`v.mrl_win` is untouched by that row, so a check asserting on it must not
fire. Measured `irlist:0fail/144pass`, against the recorded 80 passes: the
pass count moved because this lane added the contract arm and the reach
widening before it did, and the VERDICT (green) is what the row claims.

**Two observations recorded, neither re-recorded as a doc figure** (w2x's
rule: re-recording a `SAB_DOC_FIGURE` is a claim about a measurement, and
these drives were taken to prove detection survives the conversion):

1. **S88's `atomicdiff` arm reads 0 failures where its recorded text
   PREDICTS red.** That text is explicitly a prediction — it says so, and it
   says "Canonical figure owed from run_sabotage_matrix.sh S88" — so this is
   the row's FIRST measured drive, not a regression against a measurement.
   It is outside this lane's blast radius and the byte-neutrality proof is
   what says so: `atomicdiff` compares ANSWERS, answers come from the `.c`,
   and §3 measures that this change moves no `.c` byte on any corpus row.
   The sabotaged tree's artifact at this commit is therefore byte-identical
   to the sabotaged tree's artifact at the branch point, so the verdict
   cannot be this lane's. Flagged for whoever owns S88's canonical figure.
2. **S88 and S141 both move `codegen` by 3 failures** where S141's recorded
   figure says 2. Same cause as the pass counts: `run_codegen_tests.sh`'s own
   population has grown since those figures were taken. The rows' CLAIMS —
   which arms fire and which stay green — are what held.

---

## 7. Validation — COMPLETE vs OWED

**COMPLETE**

| what | result |
|---|---|
| `make strict` | clean after every commit |
| `tests/codegen/run_ir_listing.sh` | **144 passed / 0 failed** (was 128/0; +16 is the new contract arm) |
| `make test-codegen` | **8 of 9 scripts**, sole FAIL `run_inline_capability.sh`'s `nm could not read arm_a.o (no rx_search symbol)` — the standing darwin red the brief names, reproduced and not fixed |
| `tests/vm/run_vm_tests.sh` | 48 passed / 0 failed |
| `tests/mrl/run_mrl_tests.sh` | 27 passed / 0 failed |
| `tests/prefilter/run_prefilter_tests.sh` | 34 passed / 0 failed |
| `tests/counterk/run_counterk_tests.sh` | 24 passed / 0 failed |
| `tests/possessify/run_possessify_tests.sh` | 18 passed / 0 failed |
| `tests/rungselect/run_rungselect_tests.sh` | 24 passed / 0 failed |
| `tests/rungselect/run_rungdiff.sh --corpus` | **46 rung-positive patterns derived** through the hoisted read, 46 agreed / 0 diverged, 112,038 cells compared, rc=0 — the witness that the three `--corpus` hoists work |
| byte-neutrality, 3 arms + positive control | §3 — 0 movers on both `.c` arms and the composition arm; control fires 2,804/2,804 |
| contract conformance, independent instrument | §4.1 — 2,804 listings, 0 violations |
| REACH census | §4.2/§4.3 — every section and every empty arm renders; 8 of 9 `prefilter` tokens, the ninth unreachable for a pre-existing reason |
| anchor integrity | 268 rows / 284 sites / 0 unresolved, after every commit |
| 6 sabotage rows driven SOLO | §6 — all DETECTED, unexpected 0 |

**OWED AT HAND-OFF: nothing.** The three `--corpus` derivation arms share one
converted read; `run_rungdiff.sh --corpus` is run as its witness, and
`run_counterkdiff.sh --corpus` / `run_possdiff.sh --corpus` are NOT run here
— they are the same hoist against the same section with a different `fact`
value, and each is several thousand compiles. Named so the manager's battery
covers them rather than assumes them.

**NOT RUN, by the brief**: `make test` (the manager's merge gate), the full
`make mech`, `make ubsan`/`asan`/`lint`, `make test-axes`.

---

## 8. What a later listing customer should know

1. **Adding a section is `vm_sec(o, name, cols, ncol)` plus rows.** The
   section NAME set and each section's columns are APPEND-ONLY API
   (`docs/spec/ir_listing.md`); a name, once shipped, keeps its meaning.
2. **Never emit a `#` line after a section's data.** Contract rule 3 would
   make it that section's header on any artifact where the section is empty.
   An empty population is a ROW (§2.1).
3. **A cell is a literal or an arena fragment, never a shared scratch**
   (§2.6): `sb_row` reads all of a row's cells at once.
4. **Adding a FACT is a `summary` row**, not a new section — `fact`/`value`/
   `note`, with the machine-readable half in `value`. That is where the
   artifact-wide numbers now live, including the ones that used to be prose
   heads on `pruning` and `islands`.
5. **`--emit-ir` STILL has no `.c` identity gate.** Any change on this path
   owes `run_ir_listing.sh`, the sweep's `--emit-ir` arm, AND a REACH
   statement — plus, now, the contract arm. §3.2's positive-control shape is
   the cheap way to show the sweep is not blind.
6. **The DFA/prefilter listing section (D106 addendum items 3-4) drops
   straight in.** It is a `#section dfa` with its own columns and needs
   nothing from this format that does not already exist; the `summary`
   section is where its artifact-wide facts would go. `--emit-dot` is
   unaffected — a different output entirely.
7. **The walk→event→render seam is intact and is now sharper** (D108 rule
   2): the renderer consumes the `VEvent` stream and `VmStamp`, nothing else,
   and every text primitive it calls takes values. A back-end producing the
   same event stream from a deserialized IR gets this rendering unchanged.

---

## 9. Rulings received

None. No question was escalated; no `dd8_rulings.md` was written for this
lane. Every design call in §2 was made under the brief's "design calls you
make" clause, and none of them changes what the listing CAN say — except
§2.6's high-byte framing, which is recorded there as the one content change.
