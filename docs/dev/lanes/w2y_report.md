# LANE w2y — [REVW.2] WAVE 2 SLICE E: EP2 sequence steps 12-15

Branch `lane/w2y`, branched from `main` at `ac21aaaf`. Everything wave 2 had
left: lens 11's F7 at two dispatchers, F14 at `vm_look_behind`, F8 at
`vm_render_listing`. Four steps, four commits, one re-aim batch, this report.

---

## 0. THE HEADLINE: EP2's anchor table is EXACT for all four steps, and that is a fact about the SHAPE of these steps rather than about the table

w2a measured 7 anchors where EP2 predicted 9; w2b measured 6 where the charter
predicted 4. The brief carried that forward as "EP2's counts are approximate —
find anchors BY GREP". They were found by grep here, over the whole
`tests/mech/sabotages/` tree on this lane's own source, and **all four
predictions are exactly right**: 8 for step 12 (S75 / S103 / S118 / S105 /
S106 / S109 / S114 / S115), 2 for step 13 (S98, S217 site 2), 4 records over 3
rows for step 14 (S133, S134, S135 ×2), and 0 for step 15.

The reason is worth more than the score, because it says when the table can be
trusted and when it cannot. **EP2's table counts anchors whose whole text lies
inside one CONTIGUOUS SPAN**, and steps 12-15 are exactly the moves for which
that is the right resolution — a `switch` arm's body, a loop's body, a whole
function. The two earlier misses are the two cases where it is not:

- **w2a's miss was a span that bundled two candidates.** EP2's `P4 +
  vm_plan_capacities` row gave one span for two extractions, so the capacity
  policy inherited the anchors of the emission block that follows it.
- **w2b's miss was not a span at all.** Retiring a buffer replaces a NAME with
  an EXPRESSION at every reader, and a reader can sit anywhere in the file —
  which is why two of its six broken rows quote an argument line and a
  consumer rather than the declaration.

So: **a span-resolution anchor count is exact for a relocation and a floor for
a data-flow change.** Steps 12-15 are all relocations.

---

## 1. The commits

| commit | step | what |
|---|---|---|
| `e051baa8` | **13** | F7 `vm_count_slots` — `vm_count_slots_look`, `vm_count_slots_rep`; S98 + S217 site 2 re-aimed |
| `dbcb8dc1` | **12** | F7 `vm_emit` — `vm_wordb`, `vm_cap`, `vm_bref`, `vm_cat`; 8 anchors re-aimed |
| `310eae96` | **14** | F14 `vm_look_behind_branch`; S133/S134/S135(×2) re-aimed, 3 `SAB_DESC` re-pointed |
| `c8771806` | **15** | F8 `vm_listing_events` + `vm_listing_slot_row`/`vm_listing_slots`; 0 anchors |

Order: 13 before 12 (cheapest first, the brief's order); 14 and 15 after,
neither depending on the others. No dependency reason to reorder was found.

**NOT an `abi` event, measured rather than assumed** — no emitted byte moves on
any of the four streams at any step (§3). Nothing under `docs/spec/` changes:
no entry, flag, stamp, limit, diagnostic tier or module behaviour is
caller-observable here.

### What the four steps did to the file

| function | code span before | after |
|---|---:|---:|
| `vm_count_slots` | 349 | **180** |
| `vm_emit` | 515 | **238** |
| `vm_look_behind` | 196 | **68** |
| `vm_render_listing` | 498 | **457** |

Ten new functions: `vm_count_slots_look`, `vm_count_slots_rep`, `vm_wordb`,
`vm_cap`, `vm_bref`, `vm_cat`, `vm_look_behind_branch`, `vm_listing_slot_row`,
`vm_listing_slots`, `vm_listing_events`. File 11,823 → 11,915 lines (the
growth is the ten headers and ten signatures; no statement was added).

---

## 2. What was built, per step

### Step 13 — `vm_count_slots`'s two fat arms

`case A_LOOK:` and `case A_REP:` become one-line delegations, on the precedent
the file already ratified three functions up (`vm_cost`'s `A_REP` arm delegates
to `vm_cost_rep`). Verbatim relocation, dedented four columns.

**The three scratch locals moved with the A_REP arm.** `uint8_t
seq[VM_MAX_STRIDE][32]`, `CapOff caps[VM_MAX_BODY_CAPS]` and `int stride, nc`
sat at the top of the dispatcher and are `vm_cursor_fits`'s out-parameters; the
A_REP arm was their only reader (measured by grep over the function before
moving them), so nine arms that never touch them stopped carrying them.
`vm_cost_rep` declares the same three at its own top, which is the shape this
now matches.

**A finding about EP2's own unit, and it is w2x §0's finding a second time.**
EP2 calls these "two fat arms" and its table gives the A_LOOK arm the span
`:2609-2709` — a hundred lines. The arm's CODE is six statements; the span is
fat because a 15-line comment block sits above it and a 7-line one inside it.
The A_REP arm is genuinely fat (about 90 code lines). *EP2's cost model prices
a candidate by SPAN, and a span includes comments, so "fat arm" at span
resolution and "fat arm" at code resolution are different sets.* Both were
extracted anyway — the A_LOOK arm's six statements plus its own 22 lines of
justification are a unit, and giving that unit a name is the point of F7 — but
a brief sizing work from the span table is sizing comments.

### Step 12 — `vm_emit`'s four fat arms

`vm_emit` dispatched ten kinds: six one-line delegations and four whole
programs, so reading it told you six of the ten things it does. The four become
`vm_wordb` / `vm_cap` / `vm_bref` / `vm_cat`, all on the existing
`(Vm *v, int entry, const Ast *a, int next)` signature the other six use.

`A_WORDB` and `A_NWORDB` stay in ONE arm and one function: `neg` is the whole
difference between them and it is a single comparison operator, so splitting
them would be the violence §4's rubric warns about rather than an altitude
gain. `vm_wordb` takes the dispatcher's `StrBuf *b = v->b;` (the only one of
the four that emits through `b` directly); `vm_bref` already declared its own
`bb` and keeps it (coding guide §1.7 — the emitters' short locals are the house
convention and do not get renamed in a relocation).

### Step 14 — `vm_look_behind_branch`

`vm_look_behind` was a preamble plus one `for` loop whose body was **126 of the
function's 196 lines** — F14's shape exactly. The body becomes
`vm_look_behind_branch(v, a, i, m, okl, pslot, br, bl, bodl, endl)` and the
caller is two lines.

**The extraction is NOT purely additive in the caller, and the compiler is what
says so.** Two of `vm_look_behind`'s locals had no reader outside the loop —
`StrBuf *b = v->b;` and `const bool neg = a->u.look.neg;` — so both moved down
with the body and `make strict`'s `-Wunused-variable` would have caught leaving
them behind. The four label arrays and `br` stay the caller's: they are sized
and filled by the preamble, indexed by the branch function, never written by
it. `(void)mslot;` stays with the caller, where the unused parameter is.

### Step 15 — `vm_render_listing`'s two repetition families

*Family one.* RUNGS, STRATEGIES and PRUNING were the same twelve-line program
three times, differing in four values: event kind, name table, one column
width, empty-population sentence. One `vm_listing_events(o, v, KIND, kindname,
namew, none_msg)`, three calls.

*Family two.* Six slot families rendered `"  %-12d %-22s %s\n"` independently —
six places for one column width to drift. Two helpers, because they are two
altitudes: `vm_listing_slot_row` is the row and the one home for the format;
`vm_listing_slots` is a whole single-index family on top of it, including the
empty-population sentence two of the six carry and four do not (`NULL` says so).

**Lens 11's "a three-column table over the six families, walked once" is not
buildable byte-neutrally, and the obstacle is output ORDER.** Five of the six
are single-index families. The revdet family is not: its three rows come from
ONE loop index, so the section reads *entry, low-water, ceiling, entry,
low-water, ceiling* for two revdet loops, and any per-family walk would emit
*entry, entry, low-water, low-water, ceiling, ceiling*. It loops a three-row
descriptor table onto the row helper instead, and the helper's header records
why it is the one family that cannot join.

`%-18s` / `%-14s` / `%-12s` become `%-*s` with a width argument. **w2x §8's
plant 2 is why that is worth a sentence rather than silence**: at width 0
`%-*s` and `%*s` render identically, so a sign typo in a widened form can be
invisible. It is not invisible here — all three call sites pass a real width —
and the helper's header states the condition so a fourth call site passing 0
does not quietly re-open it.

---

## 3. Byte-neutrality — four streams, every step

Against a **pinned branch-point binary** built from `git archive ac21aaaf` into
the session scratchpad, which does not move as the lane edits. Driver rebuilt
in this lane's scratchpad from w2a §2 / w2b §3 / w2x §5 (w2x's own scratchpad
is gone).

| stream | population | reach | every step |
|---|---|---:|---|
| corpus argv, `.c`, default engine | 3,938 rows | **3,517** | BYTE-IDENTICAL |
| corpus argv, `.c`, `--engine=vm` | 3,938 rows | **3,518** | BYTE-IDENTICAL |
| corpus argv, `--emit-ir` + `--engine=vm` | 3,938 rows | **3,518** | BYTE-IDENTICAL |
| composition, `--source` over every `.rxt`/`.rxtin` | 304 files | **96 artifacts, 32 producing** | BYTE-IDENTICAL |

Zero movers, zero asymmetric rows (one side compiling and the other refusing),
on every stream at every step.

**THE INSTRUMENT WAS VALIDATED BEFORE IT WAS TRUSTED.** Run first against this
lane's own branch-point build — same source as the reference, different build
tree — all four streams came back identical at full reach, so a green means "no
byte moved" rather than "the instrument is blind".

**And validating it is what found the two reach defects below.** Both were
invisible in the pass count and visible only in the REACH figure, which is
w2x §5's lesson met twice more.

### 3.1 The argv streams need `--features all`, or reach is 1,500 of 3,938

The first validation run reached **1,500** rows and read a perfect green.
2,438 of the corpus's pattern lines are module-gated, and at default features
BOTH sides refuse them, which the sweep scores as `both_refuse` — a clean
green over a population that excludes, among other things, **every
backreference and every lookbehind in the tree**. That is the population steps
12 and 14 move. With `--features all` the reach is 3,517 / 3,518, matching the
figures w2a/w2b/w2x recorded and `d105_report.md` §3.2's own
"1,500 at default axes and 3,517 at `--features all`".

### 3.2 THE COMPOSITION ARM DOES NOT REACH THE DELIVER BLOCK WITHOUT `--features all` EITHER, and this contradicts a recorded claim

w2a §4 item 6 established that `vm_splice`'s DELIVER block is witnessed by
NOTHING but the composition route, and the brief carries that forward as
MANDATORY. w2x §5 records both DELIVER fixtures as "confirmed present in this
sweep's producing set".

Measured here: at default features, **`compose_delivers.rxtin` and
`deliver_forms.rxtin` both REFUSE** — `(?&d=piece)` needs module `recursion`,
the file declares no features of its own, and `--source` passes none. The
composition sweep at default features produces 84 artifacts from 29 files and
**not one of them contains a DELIVER block**. With `--features all` it produces
96 from 32, and both fixtures compile (`user.c`; `flatcall` / `plaincall` /
`selfcall` / `sitecall`).

Two things follow. First, every composition figure in this report is the
`--features all` one. Second, **the composition arm's population is pinned
nowhere** — it is rebuilt from prose by each lane, and this lane's
default-features number (29/84) and `--features all` number (32/96) both
disagree with w2x's recorded 30/72, so at least two of the three drivers
differ in a way no artifact records. *A mandatory arm whose reach is a property
of a flag nobody wrote down is an arm that can be silently empty.* The durable
fix is a committed script with a pinned producing-set count, not a fourth
rebuild from prose; not built here (D77 — the measurement that triggers it is
this paragraph).

### 3.3 Step 15's stream has no `.c` gate, so its green was checked for vacuity

`vm_render_listing` writes `&job->irsb` and no byte-identity gate over the
artifact reads it (coding guide §3.3). Its comparators are the `--emit-ir`
stream above and `run_ir_listing.sh`. A byte-identity green over a stream that
never RENDERS a family proves nothing about that family (K35 / [MECH-REACH]),
so the same 3,518 listings were re-walked and classified by section:

| family | listings with ≥1 row | listings showing its none-sentence |
|---|---:|---:|
| slots/guard | 324 | 3,194 |
| slots/low | 463 | 3,055 |
| slots/mark | 250 | — (no sentence) |
| slots/revdet | **58** | — |
| slots/lookmark | 517 | — |
| slots/lookpos | 548 | — |
| events/RUNGS | 1,459 | 2,059 |
| events/STRATEGIES | 1,459 | 2,059 |
| events/PRUNING | 1,459 | 2,059 |

**Zero unreached arms** — every family the step rewrote renders rows on real
corpus patterns, and every empty-population sentence renders too. The revdet
family, the one that could not join the helper, is the thinnest at 58 and is
genuinely exercised.

*The census's own first draft was wrong and is worth one sentence.* It searched
the whole listing text for a per-family marker, and three markers were
substrings of another family's text — the guard and low "row" markers are words
their own none-sentences repeat, so both read 3,518 (every listing) instead of
324 and 463, and the PRUNING "row" marker matched a header clause and read 0.
Rewritten to parse the listing into sections and classify rows within them.
*A reach instrument that reads a family's presence off a substring of the
family's own prose will be defeated by the prose.*

### 3.4 Per step, also

`make strict` clean after every step. `bash tests/codegen/run_ir_listing.sh`
**128 passed / 0 failed** after every step. `make test-codegen` at the end of
step 15: **8 of 9 scripts**, the sole FAIL being `run_inline_capability.sh`'s
`nm could not read arm_a.o (no rx_search symbol)` — the standing darwin red the
brief names, reproduced independently here, not fixed.

---

## 4. Anchors

**Anchor integrity over the whole tree: 284 records / 268 rows / 0 mismatches**,
re-measured after every step (w2x recorded 282/266; the +2/+2 is
[ALLOC-PINS]'s S259/S260, which merged at `935bd2ff` before this branch point).
"Records" counts a `SAB_FILE2` as a second record; `emit_vm.c` holds **99** of
them, 34.9% of the tree.

Fourteen anchor records over thirteen rows were re-aimed (8 + 2 + 4 records;
8 + 2 + 3 rows), all by DEDENT — the
moved text keeps every column relative to its new enclosing brace, and
`replace.py`'s whole-file line-agnostic match is satisfied by re-spelling the
leading whitespace and nothing else (coding guide §3.4). Every plant is
unchanged: swapped reads stay swapped reads, deleted lines stay deleted, the
inlined loop stays the inlined loop. Intent was re-verified per row against the
row's own header rather than inferred from the substitution.

| row | step | site | re-aim | solo verdict |
|---|---|---|---|---|
| S98 | 13 | `vm_count_slots_rep` head | **not a dedent — see §4.1** | DETECTED |
| S217 (site 2) | 13 | counter-rung `npush` | dedent 4 | DETECTED |
| S75 | 12 | `vm_wordb` | dedent 4 | DETECTED |
| S103 | 12 | `vm_cap` | dedent 4 | DETECTED |
| S118 | 12 | `vm_cap` | dedent 4 | DETECTED |
| S105 | 12 | `vm_bref` | dedent 4 | DETECTED |
| S106 | 12 | `vm_bref` | dedent 4 | DETECTED |
| S109 | 12 | `vm_bref` | dedent 4 | DETECTED |
| S114 | 12 | `vm_bref` | dedent 4 | DETECTED |
| S115 | 12 | `vm_bref` | dedent 4 | DETECTED |
| S133 (site 1 only) | 14 | `vm_look_behind_branch` | dedent 4 | DETECTED |
| S134 | 14 | `vm_look_behind_branch` | dedent 4 | DETECTED |
| S135 (both sites) | 14 | `vm_look_behind_branch` | dedent 4 | DETECTED |

### 4.1 S98 is the one re-aim that needed thought, and the reason is a near-collision

Its `SAB_BEFORE` was the two lines `case A_REP: {` + `const bool cuts =
vm_cuts(a, under_atomic);`. The obvious dedent is `{` + `    const bool cuts =
vm_cuts(a, under_atomic);` — and **that text also matches `vm_cost_rep`**,
whose first statement after its own `{` is character-for-character the same
line. `replace.py` refuses on a count mismatch, so this would have read
APPLY-FAILED rather than mis-planting; but the row would have been dead until
someone diagnosed it. Re-aimed onto the new function's SIGNATURE lines instead,
which is what makes it unique. *The line that made an anchor unique can be the
line the extraction deletes, and the replacement has to be found rather than
derived.*

### 4.2 S133 has two anchors in one file and only ONE of them moved

`SAB_FILE`/`SAB_FILE2` are both `emit_vm.c`: site 1 is the back-step call
inside the branch loop, site 2 is `v->enc_mask |= PCREC_ENCE_BACK_STEP;` in the
preamble, which step 14 did not touch. A whole-row mechanical dedent — the
obvious way to batch twelve re-aims — would have broken the half that was still
correct, and the anchor checker would then have reported S133 red **after** the
re-aim, which reads like the extraction was wrong. Site 1 was dedented and site
2 left alone. *A row with two anchors in one file is not one anchor; a
re-aim tool has to take a key list, not a row.*

### 4.3 Three `SAB_DESC` sentences went stale and nothing in the tree checks them

S133, S134 and S135 each open with "`vm_look_behind` …" describing text that
now lives in `vm_look_behind_branch`. Re-pointed. This is w2x §6's class —
prose is not an anchor, `m6read_check_sab_anchors.py` stays green through it by
construction — and it is worth recording that the OTHER nine rows needed no
prose edit at all, because each of them names the AST KIND it plants against
(`A_CAP`, `A_BREF`, "the VM's `\b` arm") rather than the containing function.
*A sabotage description that names the construct survives a refactor; one that
names the function does not.*

### 4.4 The method constraint w2x paid for, honoured here

`run_sabotage_matrix.sh` takes its SOURCE from `git archive HEAD` and the row
DEFINITION from the working tree, so a re-aim is drivable only once committed.
Every re-aim rides its own step's commit, and the solo drives ran afterwards.

---

## 5. What EP2 and lens 11 got wrong about the tree

`w2a_report.md` §4's shape — short, so a later lane carries it.

1. **EP2's span table prices comments.** Its A_LOOK row is a 100-line span
   around six statements (§2, step 13). The same unit conflation as w2x §0's
   "52 sites"; second instance in one wave.
2. **Lens 11's F8 "six identical slot loops … a three-column table walked
   once" is five, plus one that cannot join**, and the obstacle is output order,
   not signature (§2, step 15).
3. **Lens 11's F8 blast radius says "0 sabotage rows" and that is right**, and
   its second citation is right too and was almost dismissed here.
   `tests/vm/run_vm_tests.sh:803` is a COMMENT, not a check — but the check it
   comments is real and is a SECOND live comparator for this step: it compares
   the RUNGS summary MACRO (emitted by `pcrec_emit_vm`) against all three of
   `--emit-ir`'s per-quantifier RUNGS lines (rendered by `vm_render_listing`),
   off the same `v->rungs` / `VE_RUNG` data. Run here explicitly for that
   reason (§7). *A lens citation that lands on a comment is still a citation to
   the check the comment is about.*
4. **F14's "`vm_look_behind` 3 sabotage rows" is 3 rows over 4 records**, and
   one of the three has a second anchor that must NOT move (§4.2).
5. **The composition arm's reach is a property of `--features all`** and was
   not recorded anywhere (§3.2). This is the finding most likely to bite the
   next lane.
6. **`vm_render_listing`'s own group loop is not one of F8's six.** The
   `for (int k = 0; k <= v->ngroups; k++)` block renders `%2d,%-9d` — two slots
   per row — and shares no format with the six; it was left alone, deliberately.

**HELD:** EP2's step ORDER and its dependency edges (13 has none, 12 depends on
11, 14 has none, 15 depends on 11 — all satisfied); its `abi` verdict for every
step (not an event, verified on four streams per step rather than assumed); its
anchor counts for all four steps, exactly (§0); its cost model's central claim
that re-indentation is what costs and verbatim relocation is free; and lens 11's
F7 remedy naming `vm_cost_rep` as the file's own precedent — it is, and the
extracted functions were written to match it.

---

## 6. Re-pins

- **Fragment census** (`tools/review/fragment_census.py` over both emitters):
  **6 declarators / 6 statements**, exactly the six named encoding-seam
  exclusions w2b left. Re-run on this tree after step 15; unchanged, because no
  step touched a scratch buffer. Nothing to re-pin.
- **`run_ir_listing.sh`**: 128/0 before and after every step; its fixture set,
  `--features` rows and `irsb` baselines are untouched.
- **`tools/review/out/*.tsv`**: the committed census snapshots are the
  2026-09-17 review's own pin at commit `7d444f9e` and are not regenerated per
  wave (no wave-2 slice has regenerated them; no check reads them). Left alone
  deliberately rather than silently.
- **No `abi` reader moves**, because no emitted byte moves; no `docs/spec/`
  hunk is owed (nothing caller-observable changed).
- Searched by grep for anything pinning `emit_vm.c`'s source text outside
  `tests/mech/sabotages/`: every other mention in `tests/` is a comment.

---

## 7. Validation — COMPLETE vs OWED

**COMPLETE**

- Byte-neutrality, all four streams, every step: BYTE-IDENTICAL (§3), with the
  instrument validated against the branch point first and reach reported per
  stream.
- Listing-family REACH census over the 3,518 `--emit-ir` listings: 0 unreached
  arms (§3.3).
- `make strict` clean after every step.
- `run_ir_listing.sh` 128/0 after every step.
- `make test-codegen` 8/9, the standing darwin `nm could not read arm_a.o`
  FAIL reproduced and recorded (§3.4).
- `tests/vm/run_vm_tests.sh` **48 passed / 0 failed** — run because of §5
  item 3: its `[M4.5e] D46` arm is a SECOND live comparator for step 15,
  cross-checking `--emit-ir`'s per-quantifier RUNGS rows against the
  `RX_VM_RUNGS` summary macro. A/B'd against a build of the branch-point tree,
  which reads 48/0 identically.
  *One methodology note, because it nearly became a false finding*: the first
  reading of this log said 38/0 with the D46 arm ABSENT, which looks exactly
  like an arm silently vanishing on a failed `build` (a K35 shape). It was the
  log being counted while the backgrounded run was still writing it. The same
  witness was A/B'd directly on both binaries first — byte-identical RUNGS
  sections — which is what stopped it being written up.
- Anchor integrity 284/268/0 after every step and after the re-aims (§4).
- S98 driven SOLO at `e051baa8`: **DETECTED** —
  `codegen:1fail/108pass,corpus:52fail/211pass,atomicdiff:96fail/8pass`,
  trailer `1 rows (unexpected: 0, undetected: 0, unreached: 0, anomalies: 0)`.

- **Every re-aimed row driven SOLO and DETECTED — 13 of 13**, each its own
  matrix invocation (`run_sabotage_matrix.sh <id>`, one row per run), twelve of
  them at `c8771806` and S98 at `e051baa8`. Every trailer reads
  `1 rows (unexpected: 0, undetected: 0, unreached: 0, anomalies: 0,
  oracle-skipped: 0)`. **Unexpected: 0. Undetected: 0. Anomalies: 0.**

| row | suites moved |
|---|---|
| S98 | `codegen:1fail/108pass, corpus:52fail/211pass, atomicdiff:96fail/8pass` |
| S217 | `atomicdiff:1fail/7pass` |
| S75 | `codegen:2fail/107pass, corpus:131fail/733pass` |
| S103 | `brefdiff:23fail/7pass, dupnamesdiff:5fail/1pass, corpus:333fail/329pass` |
| S118 | `brefdiff:20fail/8pass, corpus:11fail/25pass` |
| S105 | `brefdiff:157fail/2pass, corpus:88fail/0pass` |
| S106 | `codegen:7fail/107pass, brefdiff:12fail/4pass, corpus:21fail/14pass` |
| S109 | `codegen:13fail/107pass, corpus:0fail/88pass` |
| S114 | `dupnamesdiff:5fail/1pass, corpus:26fail/62pass` |
| S115 | `dupnamesdiff:5fail/1pass, corpus:8fail/80pass` |
| S133 | `codegen:43fail/107pass, corpus:0fail/113pass` |
| S134 | `codegen:15fail/107pass, corpus:0fail/113pass` |
| S135 | `corpus:119fail/2264pass, laround:1fail/4pass, laexpand:2fail/9pass` |

S109 and S134 move `codegen` alone and leave `corpus` at 0 failures, which is
what their own headers PREDICT — both are seam rows whose plant changes no
answer under the byte backend — so the behavioural suites reading 0fail is the
recorded outcome and not a weak detection.

Recorded `SAB_DOC_FIGURE` values were NOT re-recorded from these runs.
Re-recording a doc figure is a claim about a measurement, and these drives were
taken to prove the re-aims land, not to re-baseline thirteen rows (w2x's rule).

**OWED AT HAND-OFF: nothing.**

**NOT RUN, by the brief**: `make test` (the manager's merge gate), `make mech`
in full, `make san`/`ubsan`/`asan`/`lint`, `make test-axes`.

---

## 8. The NEXT unblocked step, and what the render-path customers should know

Wave 2 is COMPLETE at step 15 — EP2's sequence has no step 16. The queued
customers are **DD-8** and **[EMIT-VERB]**, both on the render path.

What changed under them:

1. **Adding a listing SECTION of the form "every event of kind K, or say why
   there are none" is now one call**, `vm_listing_events(o, v, KIND, kindname,
   namew, none_msg)`. Pass a real `namew`; the helper's header says why 0 is
   the value that re-opens the `%-*s`/`%*s` blind spot.
2. **Adding a slot FAMILY is one call**, `vm_listing_slots(o, v, n, accessor,
   holds, note, none_msg)`, with `NULL` for "this family has no
   empty-population sentence". The accessor signature is
   `int (*)(Vm *, int)` — the existing `vm_slot_*` accessors fit unchanged.
3. **A family with more than one row per index does NOT fit** and must decide
   the ordering question the revdet family answers (§2, step 15). If a customer
   needs a second one, the honest move is to generalise `vm_listing_slots` with
   a stride and a per-row descriptor, not to add a third ad-hoc loop.
4. **The `--emit-ir` stream has no `.c` identity gate.** Any change on this
   path owes `run_ir_listing.sh` AND the sweep's `--emit-ir` arm explicitly, and
   — §3.3 — a REACH statement, because a byte-identity green over a family that
   never renders is not evidence about that family.
5. **`vm_render_listing` is still 457 lines** and is still the largest function
   on the render path. F8's two families are retired; what remains is the header
   block (a long sequence of one-off `sb_printf` lines, each a different fact,
   which is question 4 answering "no variation to loop") and the PROGRAM event
   walk. Neither is a repetition. A customer should add to it, not restructure it.

Also carried forward for whoever rebuilds the sweep next: **§3.2 — the
composition arm needs `--features all`, and building it a committed script with
a pinned producing-set count would close a hole three lanes have now rebuilt
by hand.**

---

## 9. Rulings received

None. No question was escalated; no `<lane>_rulings.md` was written for this
lane.
