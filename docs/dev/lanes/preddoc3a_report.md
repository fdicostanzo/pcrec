# preddoc3a — core part A converted: model, patterns, labels, conditions, filters

Lane preddoc3a (opus), 2026-11-19. Branch `lane/preddoc3a`. Documents only: `docs/design/predicates/core.md` and
`core_details.md` (the five sections and their entries), the evidence directory `preddoc3a_evidence/`, this report
and its history-index line. No product code, no scripts, no `doc_ratchet.tsv`, no head paragraph touched.

## STATE AT HANDOFF

- Rulings file `docs/dev/lanes/preddoc3a_rulings.md`: empty (0 bytes) at every commit and at this report.
- Acceptance:
  - no `?` and no `skeleton: yes` piece left in the five sections: MEASURED, preddoc3a_model.py DONE: "33 pieces in
    the five sections, by status {'open': 3, 'reading': 2, 'ruled': 28}; `?` left: 0; skeleton left: 0".
  - lint: `python3 -I scripts/pred_doc_lint.py` -> "checks passed 2850, failed 0" (premise was 2278; the count
    grows with the converted pieces' lines and rulings items).
  - `make -s test-plan-lint` -> "checks passed: 2, checks failed: 0".
  - slugs: 124 of 124 homed (R.8's 120 bold kebab slugs plus group-truth, negated-class-hole, inner-label-read,
    bare-condition-labels, preddoc2's method), 58 of them on the five sections' entries; missing: none. HOW
    COUNTED: preddoc3a_model.py SL reads every `slugs:` line of core_details, library_details and parked_details;
    the set of the 124 minus the homed set is empty; the five sections' share is listed in preddoc3a_model.out.
- Evidence: 40 checks, 0 failed; 21 sabotages, 21 caught.
- Commits: one WIP commit for all five sections (e3e148b55), then the report commit. The brief asked for a commit
  per section; the sections were written together from one evidence run and committed together.

## PIECES CONVERTED

27 pieces converted (15 `?`, 12 skeleton) and 4 new; `core/conditions/quantified` and `core/filters/operand-context`
were already converted and are unchanged (their details entries restored byte for byte).

| section | piece | status | example |
|---|---|---|---|
| model | match | ruled | three modes, the record's `123` |
| model | modes | ruled | three modes |
| model | table | reading | three modes (invented) |
| model | table/group-truth (NEW) | open group-truth | n/a (library names) |
| model | places | reading | n/a (a table) |
| model | places/outermost-view (NEW) | ruled | three modes, the record's nested-pass line |
| patterns | literals, flags, sequence, alternation, quantifiers, atomic, lookaround | ruled | three modes each |
| labels | labels-vs-captures, one-rule, flow, export, paths, backreferences, numbers | ruled | three modes each (paths two lines) |
| labels | export/caller-ambiguous (NEW) | open caller-ambiguous | three modes (the spans every candidate shares) |
| labels | numbers/in-loop (NEW) | open number-in-loop | three modes, the label reading |
| conditions | form, two-valued, in-sequence, match-so-far, pass-start-read, defaults | ruled | three modes each |
| filters | and, complement, kinds | ruled | three modes each |

Why the new pieces (rule 6): group-truth, caller-ambiguous and number-in-loop are OPEN slugs that sat on pieces
whose statements are ruled or read and do not answer them (model/table, model/modes, conditions/match-so-far); each
now has its own open piece with the readings and where they part. places/outermost-view: the place table is the
draft's restatement (reading), the outermost view is ruled (nested-pass): one piece, one status.

Slugs moved to the piece that answers them: atomic-search (modes -> patterns/atomic), empty-pass (match ->
labels/one-rule), pass-and and joint-last-pass (match -> labels/labels-vs-captures), outer-pass-forms and
nested-pass (match, places -> places/outermost-view).

Library check (rule 5): no piece of the five sections has a body written in the core language; none moved.

## RULINGS FOLDED

Every `rulings:` item quotes the record word for word (checked by R1: each quote's whitespace-normalised text is a
substring of COND-FAMILY.md, each title a citable title, lint L4). By piece, the record titles:

- match: branch-scope (ii); on the model after branch-scope; row-is-match; regex-settles; nested-pass (addendum).
- modes: exception-rule; empty-search-error; whole-text (adopted if legal).
- outermost-view: nested-pass.
- literals: 2026-11-14 RULINGS on §13 (C2); the 2026-11-15 `anchored`/which-`&` entry.
- flags: C2; hole-flags; flags-propagate.
- sequence (kept): sequence-reading; the rx module.
- alternation: branch-scope; join-order.
- quantifiers: quantifier operators (three items).
- atomic: regex-settles; on atomic-search.
- lookaround: lookahead-labels; regex-settles.
- labels-vs-captures: after-loop-read; what an unqualified `$x` reads; backref-label.
- one-rule: branchings reset; array-slot; polarity-rule.
- flow: label-flow; the label-flow proposal.
- export: export-rule; the clarification (`[_ = A]`); free-name.
- paths: on path-and-ambiguity; export-scope third exchange; the label-flow proposal.
- backreferences: backref-label; same-name-twice; backref-across-parts; its clarification; free-name.
- numbers: number-names; its addendum; zero-place (two items).
- form: record-is-product; label-twice; the three remaining candidates; colon-scope; condition-not; C22.
- two-valued: regex-settles; absent-under-not; polarity-rule; not-is-complement.
- in-sequence: condition-in-sequence; pass-start-read.
- match-so-far: zero-in-sequence; `0` inside an inserted part; the confirmation (bare condition last).
- pass-start-read: pass-start-read; the `$x` ruling.
- defaults: default-scope; colon-scope.
- and: the same-stretch ruling (2026-11-15); operand-context; join-order; zero-place.
- complement: regex-settles; not-is-complement; complement-place.
- kinds: complement-place; lone-complement-match.

Later rulings (rule 2) applied: zero-in-sequence, the bare condition in a hole (match-so-far), anything-text (kinds
points at lib/sets/anything). Superseded entries went to `rejected:` with the ruling that closed them:
"labels match every pass" (reconsidered within minutes), last-pass-default's carried value (after-loop-read and the
`$x` ruling), shared-label's existence error (revised by label-flow), condition-not's absence clause
(absent-under-not), the draft's never-pass error (polarity-rule), the `0`-in-a-hole reading for a bare condition.

## DRAFT SENTENCES CONTRADICTED

By rulings after revision 29's fold (predspec291's list, the items that touch these sections):

1. R.1.0 SEQUENCE OPERAND row, "a `0` written in a condition INSIDE the operand: the operand's own match (THE
   DRAFT'S READING, as the PATTERN HOLE row)": reversed for a BARE condition (its `0` is the surrounding rx's match
   so far); stands for `A & (0: ..)`. Folded in core/conditions/match-so-far.
2. R.1.0 "a CONDITION as a sequence operand" row, its `0` cell (NOT STATED / asked): ruled, the match so far;
   §R.8's zero-in-sequence row is answered. Folded in match-so-far.
3. §2.3 "The same error covers a macro in a HOLE: `${(x: digit)}`": a bare condition in a hole is legal and sees
   the surrounding rx (match-so-far points at core/holes/bare-condition).
4. §R.8 anything-text row and the `any := /.*/` remark: ruled `anything := [\s\S]*` (kinds points at
   lib/sets/anything).
5. §R.8's STILL ASKED lists naming zero-in-sequence: stale.

Also contradicted inside the BASE (not the draft): the skeleton statement of core/labels/labels-vs-captures, "A
label matches every pass; a capture is PCRE's last value", stated the superseded entry; replaced by after-loop-read's
statement (history line in its entry; no `was:`, the tag did not change).

## MANAGER READINGS TESTED

1. Every ruled statement traces to one record entry title: SUPPORTED. R1: 28 ruled pieces, every rulings item's
   title found and every quote verbatim; lint L4 clean. Sabotage s21 (a title the record lacks) caught. Note: most
   ruled pieces trace to SEVERAL titles (a statement folds two to six rulings); "one" holds as "at least one, each
   item one". Ruled pieces carry body lines marked "(a reading)" for the draft's or the manager's parts, as the
   pilot's holes do.
2. No piece needs a `needs:` into a later core section: SUPPORTED for `needs:` (R2: none; s20 caught). The `see:`
   lines point forward to core/values, core/arrays, core/diagnostics, core/spellings, core/holes and the library,
   as the format allows. One substantive forward dependence: core/conditions/form's statement uses "set", whose
   meaning (the number domain, strings) is core/values/number-domain, a later section; written as `see:`.
3. Each ruled piece's three-mode example gives the frozen draft's printed answer: SUPPORTED where the draft printed
   one, 21 examples reproduced (MATCH from the record, NEST from the record, SEQ, ALT, QUANT, ATOM, LOOK, CAPT, ONE,
   FLOW, EXP, PATH, BREF, NUM, TV, INSEQ (`7;3;` only), PSR, DEF, AND, COMP (`712` only)); ZERO is rule 2's case,
   its answers the record's zeroseq.py run, which the draft's PART OQ OQ3 printed the same. UNTESTABLE for the
   invented examples with no printed answer: LIT, FLAGS, FORM, KINDS (ruled pieces) and TABLE (a reading); their
   control is the python `re` lowering, same spans in all three modes.

## FORMAT PROBLEMS FOUND

- A bold opener glued to the previous paragraph is not a citable title (lint L4, by design): the 2026-11-15 "the
  five open items" entry (where `&` in rx text became all or nothing) and the 2026-11-13 list item "I like your
  suggestions" (the strict subset) cannot be cited. The first is quoted under `rejected:` with its place named; the
  strict subset is a `readings:` item. A ruling that the format cannot cite is a gap the record format makes.
- `was:` takes a TAG only; a changed STATEMENT under the same tag (labels-vs-captures) has no `was:` form; written
  as a history line.
- Slugs sat on pieces that do not answer them (group-truth, caller-ambiguous, number-in-loop, atomic-search,
  empty-pass, pass-and, joint-last-pass, outer-pass-forms): moved, see above.
- LEFT, not mine to move: `nullable-meaning` on core/conditions/defaults is lib/search/occurrences' fact (sibling
  preddoc3c's file); `condition-group` (open in the draft) sits on the converted ruled piece
  core/conditions/quantified, so that ruled piece carries an open slug.
- The draft itself: "seven" is `/7/` in the R.1.0 cell and `/7\d*/` in R.1.4 / CX2 (the examples here use
  `/7\d*/` written out); R.1.4's lookaround example spells `(l: > f)` where colon-scope requires `(l: > $f)` (written
  `$f` here).
- Sibling tags pointed at (`see:`), all existing today: core/values/number-domain, core/values/arithmetic,
  core/arrays/lift, core/diagnostics/warnings, core/diagnostics/dollar-form, core/spellings/condition-parentheses
  (preddoc3b's sections); lib/sets/anything, lib/search/occurrences, lib/search/hits, lib/counting/occurs,
  lib/control/when-test, lib/records/records, parked/ideas/atomic (preddoc3c's files). No `needs:` into them.

## OWNER QUESTIONS LEFT

- group-truth: after a loop, (a) `NOT some(c)` = `occurs.none(c)` versus (b) `occurs.none(NOT c)` read per pass;
  they part on 21 / 201 / 301 of 364 (the draft's E12), e.g. with no pass (b) holds. Piece
  core/model/table/group-truth.
- caller-ambiguous: what the caller gets for a public label two parts set and nothing references (`A & B`, A :=
  `/(?<h>\d)\d/`, B := `/\d(?<h>\d)/`): a compile error, absent, the right side's (h = `2`), the left's (h = `1`),
  or an error when read; the spans are the same, h parts on `12`. Piece core/labels/export/caller-ambiguous.
- number-in-loop: `/(?:(\d)?;)*/ & (1: <5)` on `3;;`: the label FAILS, the capture HOLDS, refused is a compile
  error. Piece core/labels/numbers/in-loop.
- condition-group (not converted here; on core/conditions/quantified): left open as the draft has it.
- Readings left for the next round, not questions: whole-text's legality (not re-run); the strict subset; `&` OFF
  by default; a lookbehind's labels; `{1}` as no branching.

## EVIDENCE AND COMMANDS

- `docs/dev/lanes/preddoc3a_evidence/preddoc3a_model.py` (python `re` only; its CLAUDE.md has the method):
  `(cd $PCREC_TMPDIR/scratch/preddoc3a && timeout 300 python3 -I -B <W>/docs/dev/lanes/preddoc3a_evidence/preddoc3a_model.py)`
  -> `preddoc3a_model.out`: "preddoc3a_model: 40 checks, 0 failed".
- Sabotages: `PREDDOC3A_SABOTAGE=sN` for N = 1..21 -> `preddoc3a_sabotage.out`: 21 of 21 caught (each run lists
  its failing checks; every wanted check among them).
- `timeout 120 python3 -I scripts/pred_doc_lint.py` -> "checks passed 2850, failed 0".
- `make -s test-plan-lint` -> "checks passed: 2, checks failed: 0".
- `scripts/lanecheck` -> see the reply (run last).
