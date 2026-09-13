# Lane w23aux — [DD-13b.W23] STEP 1.4, format_design.md REVISION 3.4 (D99)

**2026-09-13, opus, DOCS-ONLY.** Branch `lane/w23aux`. Nothing under
`src/`, `tests/` or `docs/spec/` (verified: `git diff main...HEAD
--name-only` matches none of the three). `docs/dev/reviews/
2026-09-12-r57-w23-format.md` is append-only history and was not
touched. No `make`, no battery, no suite run — this lane had none to
run and none was in its charter.

Three files changed: `docs/design/dd13_format/format_design.md`
(+1,357 / −319 across the whole delivery),
`docs/design/dd13_format/CLAUDE.md`, `docs/dev/plan.md` (one row
annotated, STATE unchanged at `started`).

---

## 1. What the revision does

D99's five consequences, executed. The short version, which is also
what the manager should check first:

1. **§2.20 (`configs describe`) and §2.16 (`provides`) are WITHDRAWN**,
   marked in place with their full reasoning rather than deleted (house
   style — §0.6/§0.7/§0.8's revision records are the pattern). Both
   markers say what the mechanism was, what collision it addressed,
   why it is withdrawn, where the need goes, and what left with it.
2. **`config … testee`/`option` (N-42) leave the wave plan** with them:
   same reason, an engine roster describes engines.
3. **§2.27 is NEW — the AUX production, spelled `ext <consumer>`.**
   File scope and block scope, `cardinality: repeat`, body is ordinary
   S1-attached records, semantically uninterpreted, dumped in a new
   `#section aux`. The **GRADUATION RULE is normative** (§2.27.3) with
   a four-clause falsifiable test for "act on".
4. **§0.9 carries the SECOND-ORDER IMPACT TABLE** — 23 rows, 13 from
   the seed list and 10 found by the sweep, each with a disposition and
   a citation.

## 2. The impact table's four rows worth reading first

Full table is §0.9. These are the ones that changed something beyond
their own line.

**S2 — `cross-scope` loses its only customer, and the constraint
vocabulary goes EIGHT → SEVEN.** The kind was admitted at revision 3.2
(r57 S-BL1, a blocker) specifically for `provides` ⊆ `vocabulary
requires`. Grepped every occurrence in the note and read each: no
production other than `provides` uses it anywhere. §2.25.3's own
membership rule — *"a constraint kind is admitted only when a
production in THIS delivery needs it"* — therefore requires its
removal, or it is not a rule but a ratchet. It goes back to §2.25.4's
deferred row with a sharpened trigger. The count is corrected at every
site that states it. **The general lesson recorded with it**: a
deferral with a trigger has to be re-checked against the delivery it
ends up with, in both directions — a trigger that fires can un-fire.

**F2 — the `lib`-contributes-DEFINITIONS-ONLY clause is the most
load-bearing re-home.** §2.20 rule 4's second half (added at 3.2 as r57
C-S4) answers *"what crosses a `lib` edge?"*, which has an answer
whether or not a mode line exists — `configs` was the occasion for
writing it down, never its subject. Deleting it with its section would
have **silently re-opened a closure question in a different
production**, which is exactly the second-order damage the sweep exists
to prevent. It moves to §2.5's include model (where a reader asks the
question) with a pointer from §4.1 (where [LIB] needs it).

**F1 — a STALE ECHO found rather than inherited.** §8's P-Q9 still
listed *"`pattern` + `pattern-esc` in one block"* among W23's
refuse-by-name productions. Revision 3.2 DROPPED that refusal as an
empty population (r57 S-BL2), rewrote §2.19, §1.3's EBNF comment, §9's
B6 row and the bench correction list — and the r57 ROUND 2 critic
recorded *"every echo of the dropped `pattern`/`pattern-esc` refusal
gone"*. **This one survived, two sections from anywhere the 3.2 sweep
looked.** Fixed. It is §1.6.4's own sixth clause (a sweep bounded by
where the change was made finds what the change touched, not what the
change invalidated) recurring inside the revision that wrote the clause
down, which is why it is in the report rather than only in the diff.

**S12 — the one seed row REFUTED.** The seed asked whether `configs`
appears in §1.6's reserved-keyword / version-break material. **It does
not, anywhere.** §1.6.3 reserves `version` and declines `schema` and
names neither; §1.6.2's break pricing is about indenting case lines.
The only §1.6-adjacent mention is §0.7's 52-candidate freeness census,
a historical measurement that stays true (removing candidates from a
list of tokens measured ABSENT cannot make any of them present). **No
edit was needed and none was made.**

## 3. What D99 did not anticipate — the lane's own findings

Five, beyond the stale echo above.

**(a) `validated_by` has no cell for "the body is never checked", and
the note had already solved this shape once.** The brief specified
`validated_by = nothing`. There is no row to put it on, because
**`validated_by` is a property of a ROW and an aux body has no rows.**
That is r57 S-S3's finding verbatim, one production over — config
RESOLUTION had the identical problem, and the answer built for it was a
declared non-coverage `surface` row in `--list-schema`. Aux takes the
same mechanism unchanged. §2.27.4 spells it, and the honest statement
that falls out is better than the brief's: **the STRUCTURE is validated
by all three legs (`validated_by: all-readers` on the `ext` opener),
the CONTENT by nobody (the surface row)** — two claims that a single
cell would have blurred. A repair that fits its second customer
unchanged is the sign the first one was diagnosed correctly.

**(b) `children` needed a fourth value, and the alternative was a
carve-out consequence 1 forbids.** §1.2.2's rule is that a first token
unknown IN ITS SCOPE is a hard error; every scope today is a closed
set, and an aux scope is open by construction. Expressing that as *"the
unknown-token rule does not apply under `ext`"* is precisely the
per-keyword structural exception Frank's consequence 1 rules out. So it
is **`children: tree`** (§2.25.2) — one enum member, the same price
`prose` cost, in the column that already says what a kind's indented
lines ARE. It deliberately does not touch structure-layer parameter 2:
the pair test is unchanged and `tree` fails it exactly as `none` does.

**(c) §2.26's ownership audit could not have reached D99's answer, and
both of its now-moot rows show why.** Item 4's 3.2 addendum diagnosed a
real symptom — the `requires`/`provides` rename bought a READING
symmetry the GRAMMAR did not have — and treated it with a rename plus a
constraint kind plus a pointer sentence. **The two ends did not fit
together because one of them did not belong in the format at all.** An
audit scoped to spellings (correctly so, for an ownership ruling about
syntax) is structurally unable to reach that. Item 6 is the same shape
with the opposite sign: a CONFIRMED spelling on a mechanism that should
have been questioned. Recorded in both items as the audit's own limit.

**(d) SW13's membership moves for free, and it is the `wave` column's
first real service.** r57 S-S2 challenged the `wave` column as having
an empty consumer population at the delivered pin; it was kept on the
argument that the ROLLOUT's partial builds need it. Its first actual
use turns out to be a **withdrawal**: because the "NOT IN THIS BUILD"
list is derived from the column, `configs`/`testee`/`option`/`provides`
never enter it — a withdrawn production cannot be forgotten in a
hand-kept list when there is no hand-kept list.

**(e) The dump-shape change carries a survey obligation this tree has
already paid for once.** `--list-source` gains a row kind and a
section, which is a change to the table's SHAPE.
`registry_built_status_memo.md`'s own CORRECTION records what that
costs when only CONTENT readers are surveyed: the `built` column's
landing swept every reader of the dump's meaning and missed two readers
of its FORM, both hard-coding **`NF != 15`**, caught by the union
battery rather than by the survey. §2.24 names the obligation
(CONTENT-vs-FORMAT, swept BY GREP) and SW19 carries it as a landing
condition rather than as advice. It matters more at 3.4 than it would
have at 3.3 because `#section aux` is the first section whose presence
is driven by data pcrec does not understand, so "which sections can
appear" stops being derivable from the productions a reader knows.

## 4. The two decisions flagged for the manager

Both are the manager's under the 14:5x delegation; the note argues
rather than assumes, and this report is where the ask is.

**Spelling — `ext <consumer>`. RECOMMENDED.** §2.26 item 14 carries the
argument and prices four alternatives. MEASURED free: 0 occurrences in
first-token position across 210 corpus files and 49 fixtures, indented
or not; `aux`, `extra`, `vendor`, `consumer`, `namespace` and `opaque`
are 0 as well, so availability decides nothing. `ext` reads as
*extension* and puts "not core" and "whose" in eight characters at the
position a first token is read; it is the idiom of every neighbouring
line-oriented format. **Its one genuine objection**: "extension"
suggests EXTENSIBILITY when the point is the opposite. Answered by a
spec sentence (SW18): *an `ext` block extends what a file CARRIES,
never what the format MEANS.*

**Prose inside an aux body — RECOMMENDED YES**, §2.27.2 decision 3. It
reuses S3 and `prose-value` end to end and costs no code path. **The
one real cost, stated rather than buried**: structure-layer parameter 2
(§1.2.1) becomes "these five rows, PLUS every line in any `ext` scope"
— a row set plus a predicate — and the parameter is specified as a
FETCH from `--list-schema` precisely so a generic reader need not
hard-code it. **Whether the dump can return a predicate in the form the
fetch expects is genuinely open**, is flagged in §3.3 and §5.2a attack
9, and if it cannot, the one-line alternative (no `|` inside aux) wins.

## 5. Where to attack this revision

§5.2a gains items 7, 8 and 9. The sharpest is **item 7, the sweep's own
completeness**: the hunt was a grep for six TOKENS plus the seed list,
and a grep finds SPELLINGS, not DEPENDENCIES. `cross-scope` was caught
only because §2.25.3's table names its customer in the same row; a
mechanism admitted for a withdrawn production whose text never types
either token would have survived. **The inverse method — walk every
mechanism this delivery ADDED since revision 3 and ask what needs it —
was NOT run**, and it is the one that would catch the residue. Stated
as an owed check rather than as a limitation.

Items 8 and 9 are the graduation rule's enforceability (the case its
four clauses may not cover: a `--list-source --ext=bench` FILTER,
arguably the dump repeating itself and arguably pcrec understanding a
namespace — the lane's answer is in a paragraph, not in the clauses)
and the prose decision above.

## 6. Validation status

**COMPLETE for what this lane can validate; nothing is OWED.** This is
a design-note revision with no code, no check and no fixture built —
§9.1's five new aux fixtures are PLANNED, like every other row in that
table, and the implementation lane that lands H12/H16/SW18 builds them.

What was verified, each by a command run in this worktree, read-only:

- **`ext` and six alternatives are 0** in first-token position over 210
  corpus `.rxt` files and 49 `tests/rxtsource/fixtures/` files
  (indented or not). `pcrec-bench` holds **0** `.rxt`/`.rxtin` files.
- **The withdrawals reach no shipped surface**: `docs/spec/` contains
  **0** occurrences of `configs describe`, `configs build`, `provides`,
  `capable` or `cross-scope`; `src/` and `tests/` contain **0** of the
  same. This is the brief's own STOP condition and it is clean — both
  mechanisms are design-note-only at this pin, which is why the
  withdrawal costs a diff and nothing else.
- **`cross-scope` has exactly one customer**; **`unique-by` has three
  and loses one** (so it is unaffected as a kind — checked, because
  losing one of three and losing one of one are the same edit with
  opposite outcomes).
- **Seed items (n) and (o) are clean**: `w1_impl.md`'s four hits for
  the six tokens are all incidental English plus one W3-era "NOT built"
  list that is still true; §2.19, §2.21 and §2.22 carry zero references
  to any withdrawn mechanism (checked by extracting each section body
  and testing per token), which is why W23-F4 stands untouched.
- **The impact table renders**: all 23 rows at 5 cells. The other
  markdown tables' apparent cell-count mismatches are escaped `\|`
  inside cells, the file's existing convention, present identically in
  pre-3.4 rows.

## 7. What the manager owns next

- **Review and panel.** A D6 panel on 3.4 is the natural gate;
  §5.2a items 7-9 are written as the shortest path.
- **The two flagged decisions** (§4 above).
- **Appendix A — the DRAFT outbox message to pcrec-bench.** Drafted in
  the note, **NOT sent and NOT written to the bench repo** (D78: one
  writer each way, `inbox_from_pcrec.md` only, and that is the
  manager's commit to make). Its headline for the bench: no probe
  script needs an edit for the withdrawals (measured — neither
  `capable` nor `provides` is typed by any check in their §3), their
  SET FILE changes shape, F2 is satisfied more completely than before,
  F3's gate gets easier, **their sixteen-config matrix stays theirs**,
  and the key names inside an `ext` block are theirs to choose. The
  draft also owes them the process apology D99 names.
  **Timing is the manager's**: O-26 §7 puts the correction list at the
  implementation delivery, and D99 arguably moves the withdrawal half
  earlier, since the bench is designing set files against mechanisms
  that no longer exist.
- **The Frank queue is now W23-F4 alone** (the non-callable-definition
  loss, manager recommends ACCEPT). F1 and F2 are withdrawn, F3 was
  resolved at 3.1, and D93 is untouched and decoupled.
