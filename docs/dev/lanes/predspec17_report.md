# predspec17: predicates_draft.md rev 16 -> rev 17 (lane predspec17, opus, 2026-11-15)

Design only, no build go. Branch `lane/predspec17`, cut from main 4456e9127. Sources: COND-FAMILY.md CF:1214-1248
(the 22:03 pointer, the 23:06 names ruling, the 23:07 direction and its 23:10 addition) and the owner's 23:25 order
ruling, which arrived as rulings R-1 and lives on main only (cited by date and words, not copied).

## STATE AT HANDOFF

- STATE: done. Rev 17 of `docs/design/predicates_draft.md` committed on `lane/predspec17`; one line added to the
  plan row [PRED-REREAD] in `docs/dev/plan.md`; the evidence script `docs/dev/lanes/predspec17_check.py` and its
  output `predspec17_check.out`; this report; one index line in `docs/dev/history/claude_md/docs__dev__lanes.md`.
- Rulings file `docs/dev/lanes/predspec17_rulings.md`: last entry applied **R-1** ("tuple-arg-order: subject low
  high", RULED: the order is (compared fields, low, high); the OPEN mark was never written, and tuple-arg-order is
  not in the questions below). Re-read before each commit and before this report; nothing after R-1.
- Premise test passed: `grep -n "rev 16" docs/design/predicates_draft.md | head` showed rev 16 as the newest
  changelog entry; `tail -n 45 docs/design/plan_row_bodies/COND-FAMILY.md` ended with the 22:03, 23:06 and
  23:07/23:10 entries.
- STOP RULE: the three entries do not contradict each other or an earlier ruling. The decomposition IS expressible
  under the draft's rules without a new concept (today's form uses one accessor macro per label, with two readings
  of existing rules, below). The shorter spelling (a section of the condition, `(h:)`) is a new form, so it goes to the
  owner as a question and is not adopted.
- Validation (docs only): `make test-plan-lint` GREEN (checks passed 2, failed 0; plan_lint 360 rows, 0 violations);
  `make test-spec-history` GREEN (11 passed, 0 failed). Evidence: `timeout 300 python3 -I
  docs/dev/lanes/predspec17_check.py`, run from `$PCREC_TMPDIR/scratch/predspec17`, gives `predspec17_check.out`
  with rc 0: table (D) 25,848 cases, 0 differ; table (R) 7,528 cases, 0 differ; table (W) 35 worked rows, 0 not as
  stated; 0 engine disagreements (libpcre2-8 10.46, Python 3.14.4 `re`).
- Owed: none.

## WHAT CHANGED

Draft (rev 17):
- §8 TUPLE COMPARISONS rewritten. The names are now RULED (`lex_ge2`, `lex_le2`, `lex_between2`, plus the `3` forms) and
  the order is RULED as (compared fields, low, high). The bodies are generic over a projection `s`:
  `lex_ge2(s, lo) := [s[1](padded(>lo[1])), s[1](padded(==lo[1])) & s[2](padded(>=lo[2]))]`, and
  `lex_between2 := lex_ge2 & lex_le2`. Today's projection is one accessor per label (`h_is(S) := (h: S)`); the
  examples use the candidate `(h:)`. The worked rows are: the time range (including the labels in the other text order,
  `30 past 9`), h:m:s, versions, and semver at least 1.4.0 (the 2026-11-14 shape). §8 also gains a per-example rule
  check, two new subsections (BOUNDS AND LEVELS, THE PROJECTION) and the caveats as they now stand: the helper labels
  are gone, the separator caveat is gone, and a new unset-label caveat is added. Rev 16's NAMING CANDIDATES are
  removed, and the §8 STATUS is updated.
- §0: the header's CF range; a new rev 17 rulings table (four rows). §0.1: re-applied, no row moves. §0.3: the
  `section` and `subject` rows are glossed. §1, §2.7: one pointer each. §12: re-applied, no case moves, and the census
  row is updated.
- §13: C25 RESOLVED for the fixed sizes; O47 still (C); the O69 sketch is marked SUPERSEDED (kept as history); O70
  route (a) gets the exposed-options shape and the manager's question, recorded as a QUESTION; O71 NEW
  (label-section); owner question (12) ANSWERED, (13) NEW; DECIDED (49)-(53). §14 and §15 are updated, and the
  changelog has a rev 17 entry.
- Plan: [PRED-REREAD] gains one line with the owner's 22:03 words, the COND-FAMILY entry heading, O70 and the
  through-a-hole question.

Sites where rev 16 still showed the bundled form or the old names, and what was done (found with `grep -n "f, sep\|tuple_between2\|\bt1\b\|NAMING CANDIDATES\|tuple-names\*\*"`):
- §8 bodies, examples, caveats and NAMING CANDIDATES (former lines 2246-2323): replaced.
- §8 STATUS: names, order and decomposition statuses rewritten.
- §2.7's `compare.width` pointer: now gives the decomposed call.
- §12 census row: renamed.
- §14 Tuples: rewritten.
- C25: a REV 17 resolution paragraph added.
- O69 head: the sketch is marked SUPERSEDED. Its `tuple_between2`/`t1` text stays as history, like every rev's
  "the item as it stood".
- Owner question (12): ANSWERED. Its quoted original question keeps the bundled call as history.
- DECIDED (45)/(46): kept as rev 16's list; (53) withdraws (46)'s `label =` setting.
- The rev 16 changelog entry and the rev 16 rulings table: history, unchanged.

## THE PROJECTION

The owner asked for "a macro that takes a map and produces an array given labels". Each candidate was checked
against the draft's own rules:
- (i) A plain macro from label NAMES is NOT expressible, and nothing in the draft allows it. A label name passed as
  an argument would be a value (C13 is open, and the draft leans against it: values are `$x`). The body would also
  need a label path built from a parameter. The left of `:` is a path written in the program, never an expression
  (§4.1, RULED CF:595). The only place the draft builds a name from a value is a group-name hole in rx text, and that
  defines a group; it does not read one. It would also buy nothing, because the author writes the labels anyway.
- (ii) A small structural primitive that reads the operand's map interface is NOT needed for labels the author
  names. It is needed only if the label list must be COMPUTED from a pattern (for example "all of v's labels in group
  order", C25 reading (B)). That is a later need, with that trigger.
- (iii) Writing it directly works, but only in the FIELD form, and today's rules already allow it. The map is never
  passed: an interface is never a value (CF:890-891) and the operand is never an argument (CF:749). So the map
  arrives through `&` when the composed condition meets the author's pattern. The projection is then just the array of
  the compared labels, each entry being that label's condition with its set left open. Today that is one accessor per
  label, `h_is(S) := (h: S)`, which is a plain macro of the same shape as `date_in(years) := isodate & (year: years)`.
  The VALUES form `[$h, $m]` is writable but cannot be the compared side, because a value is never constrained
  (`$x & ...` as a condition is an error, §4.1). It is the right form for BOUNDS taken from the same match.
- Recommendation: (iii) in the field form. If the owner agrees (label-section), spell it with the condition section
  `(h:)`; otherwise use today's accessors. (ii) waits for a computed label list.
- Level: the compare is decided PER MATCH. With constant bounds, every entry is a condition on a label against a
  fixed set, so it compiles to automaton states at the DEFAULT level. No captured text is read and no callout runs. The
  projection expands away at compile time. Rev 16's DFA/VM claims therefore stand unchanged: table (R) shows the
  expansion equals rev 16's conditions, renamed. `param` bounds compile to parametric automata (default level, §6.1).
  Bounds from the same match are a value-vs-value relation priced by class count (§4.6): small ones stay at the default
  level, large ones are an error naming `functions`, and unbounded fields need `functions` only.

## CONSEQUENCES DERIVED BY THE LANE

None of these are the owner's words. Each is labelled LEAN in the draft.
- The owner's "produces an array" is read as an array of label CONDITIONS, not VALUES. This follows from §4.1's split
  (`x:` constrains, `$x` reads): a compare must constrain what it compares (DECIDED (50)).
- The projection is spelled directly; it is neither a macro nor a primitive (DECIDED (49)).
- The bodies need two readings of existing rules. First, `s[k]` on an array of MACROS gives its k-th entry: §3.2 tool
  1 states the result for arrays of rx, and §3.5 makes an array of macros a macro. Second, a parameter bound to a macro
  may be called in the body: `each` already applies a passed macro, and macros expand at compile time (DECIDED (51)).
- Levels per bound kind (DECIDED (52)). Withdrawn: rev 16's per-call `label =` setting for the helper labels, because
  the compare adds no label (DECIDED (53)). Kept: the wrong-length compile error.
- The halves `lex_ge2`/`lex_le2` take (compared fields, bound). This extends the ruled three-argument order.
- The decomposition gives a gain, and table (W) shows it: the projection's order, not the pattern's group order, is
  the compare order. So `/(?<m>\d\d) past (?<h>\d{1,2})/` compares hours first.
- The label section `(h:)` is presented as C33's "other operators ... then we'll see" case. The owner has not ruled
  that this is such a case.

## QUESTIONS FOR THE OWNER

- **label-section**: should the language write the per-label accessor for you, as "the condition on h, its set to
  come", spelled (placeholder) `(h:)`?
  Example: `/(?<h>\d{1,2}):(?<m>\d\d)/ & lex_between2([(h:), (m:)], [9, 0], [10, 0])`. Without it the same thing
  needs two extra bindings: `h_is(S) := (h: S)`, `m_is(S) := (m: S)`, `lex_between2([h_is, m_is], [9, 0], [10, 0])`.
  Leaning: yes. It is a section like `(& f)`, so it adds no new kind and `:` still only narrows, and every tuple call
  would otherwise carry one accessor per field. Against: one more bracket form, and a `:` with nothing after it looks
  unfinished. Reply either way.
- (Not asked now; it belongs to the [PRED-REREAD] follow-up, recorded in O70.) Does an option set as a value, like
  `/(?i=${case})fred/`, apply THROUGH a hole, given that a hole keeps its own flags?
