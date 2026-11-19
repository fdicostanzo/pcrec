# The predicate language: details (core)

One entry per tag of `core.md`, in the same order: the question slugs asked about the piece, the owner's
rulings verbatim with their record entry, the candidates not taken and why, the readings with their state, the
evidence, and the history. The record is `docs/design/plan_row_bodies/COND-FAMILY.md` (the only source of
rulings); the frozen source of every skeleton piece is `docs/design/predicates_draft.md` revision 29.1 (cited "the
draft", by its section). Evidence directories are under `docs/dev/lanes/`; "PART X of predspecNN" is a block of
that lane's committed `predspecNN_model.out`. The pilot's own runs are `preddoc1_evidence/` (PART EX, R1-R12, LT).

shared: when-peek

## core/principles/regex-default — Regex behaviour wins
slugs: branch-scope branch-order sql-picture
rulings:
- 2026-11-17 "Notably: this is a break from the SQL model we were using. A encapsulating where clause in sql does not cause the inner sql to reconsider. However, it is in line with regex behavior so I do like it and think it should be the general behavior" (record: "2026-11-17 OWNER, on the model after branch-scope")
- 2026-11-17 "regex-settles: yes settled" (record: "2026-11-17 OWNER RULINGS — regex-settles; absent-under-not")
rejected:
- the SQL picture (an enclosing condition does not make the inner pattern reconsider) — by owner ruling — "it is in line with regex behavior" (record above).
readings:
- the SQL picture survives if the table holds EVERY path in PCRE's order (the manager's framing, 11:50) — UNTESTED here (the draft R.1.2; lane pathimpact).
evidence: lanes pathimpact, rxmodel (the regex models of the open choices, 2026-11-17).
history:
- 2026-11-17: stated in the branch-scope discussion; the draft's §R heading "under regex behaviour" carries it since revision 24.

## core/principles/explicit-exceptions — Exceptions are asked for by name
slugs: exception-rule
rulings:
- 2026-11-17 "exception-rule: everything that looks like regex should behave like regex unless we explicitly allow. This is the prove itself portion in that an exception has to be either so useful or the "expected understanding" whereas the actual regex behavior is obscure so as to be useless. Exceptions should be requested by using those features explicitly. If requested (and optioned in if needed), they don't have to be regular regex or even legal regex." (record: "2026-11-17 OWNER RULING — exception-rule")
rejected:
- the manager's lean "both: by name decides visibility, prove-itself decides the level" — by owner ruling — his words fold proving-itself into the request by name.
readings:
evidence: the draft §R.6 (EXCEPTIONS).
history:
- 2026-11-17: settles the two alternatives of the entry "an exception proves itself, or is asked for by name" (review r40 B2). Precedents decided by it: empty-pass, hits-pass (the draft §R.8, "exception-rule, the default"); quantified-condition is an explicit exception requested by him.
- 2026-11-19 (lane preddoc4): the base's "His words in full" block left the base; the rulings item above carries the same words (review r59 READ-18 stage 1).

## core/principles/meaning-not-spelling — Meaning, not spelling
slugs: mark-domain spelling-phrasing same-results
rulings:
- 2026-11-16 "mark-domain: if it is possible, the semantic rules should not not depend on the spelling of the regex but on the resulting (graph, behavior, semantics, string set)? Not sure the exact phrasing." (record: "2026-11-16 OWNER RULING — mark-domain, as a PRINCIPLE")
- 2026-11-16 "spelling-phrasing: that sounds good. I agree. Put an asterisk next to it in case it needs adjustment" (record: "2026-11-16 OWNER RULING — spelling-phrasing")
rejected:
- the group-text domain for the mark (read from the label's own text) — by run — it reads the spelling: 5 of 10 vs 0 of 10 on two spellings of one pattern (record, mark-domain entry).
readings:
- same-results: closed by entailment (the draft §R.8 TOLD table) — UNTESTED here.
evidence: `predicates_future.md` item 15 keeps its check (repeatedness).
history:
- 2026-11-16: ruled as a principle with his qualifier "if it is possible"; the sentence (*) is provisional wording, the principle is ruled.

## core/principles/no-absence — A set never contains absence
slugs: absent-rule
rulings:
- 2026-11-16 (class: PRINCIPLE) "In my mind <100 is defined as the set of all positive integer strings less than 100. Absence is not part of that set" (record: "2026-11-16 OWNER PRINCIPLE — a set never contains absence")
- 2026-11-16 the absent-rule LOCKED on this principle (record: "2026-11-16 OWNER RULING — absent-rule: LOCKED")
rejected:
readings:
evidence:
history:
- 2026-11-16: stated while the absent-label options were worked out; constrains every option for absent labels.

## core/principles/conservative-first — Conservative now, relax later
slugs:
rulings:
- 2026-11-17 "operand-context: ^ $ should be redundant as the filter is anchored. Does that mean that interpretation is unnecessary? I would say at this point that any piece that might look outside is a compiler error. Then if we discover later we can relax it we can review." (record: "2026-11-17 OWNER RULING — operand-context")
- 2026-11-18 "It's not that filter rx would never have outward looking elements, it's that it's difficult to figure out now what that means so the conservative route is to ban it." (record: "2026-11-18 OWNER RULING — hole-in-filter: the filter error; fill the holes first")
- 2026-11-18 (class: OBSERVATION) "In general, I did not anticipate these ideas and took the conservative route that eg repeat took a single decimal." (record: "2026-11-18 OWNER on value-is-pattern: one ruling, two leans, one idea")
- 2026-11-18 "When: start with required then. Use NOT to get else behavior" (record: "2026-11-18 OWNER RULING — `then` is required; NOT gives the else-only behaviour")
- 2026-11-18 "quantified-condition: an error. This is a formal punt because we may find a better meaning for it in the future and this keeps that from breaking current code" (record: "2026-11-18 OWNER RULING — quantified-condition: an error, as a formal punt")
rejected:
readings:
- relaxing any refused form later changes no existing answer (the manager's, stated with number-names) — UNTESTED (a property of refusals).
evidence:
history:
- 2026-11-17 to 11-18: five rulings in this shape (census B5 P5); decided by it: operand-context, hole-in-filter, value-is-pattern, `then` required, quantified-condition, the option hole's several values (core/holes/option).

## core/principles/general-rules — One consistent, general rule
slugs:
rulings:
- 2026-11-18 (class: LEAN, with its condition) "1. I like these sort of things. What is needed is a consistent, general rule about it and not something specific to adding to arrays for example. What happens to array + array ?" (record: "2026-11-18 OWNER on value-is-pattern: one ruling, two leans, one idea")
- 2026-11-18 "array-lift: I meant, alternations as you suggested. It's consistent that alternations combine on the product and multiply the rx and produce more alternations" (record: "2026-11-18 OWNER RULING — array-lift: operations on arrays combine on the product")
rejected:
readings:
- class: a principle drawn from the CONDITION of a LEAN ("What is needed is a consistent, general rule"), applied by his array-lift ruling; not itself a slug ruling (review r59 RULING-6; asked only if the manager doubts it).
evidence:
history:
- 2026-11-18: the ground of array-lift (core/arrays/lift); the house rule "general mechanisms, not special cases" is its kin on the compiler side.

## core/principles/rx-owns-flags — An rx sets the flags it needs
slugs:
rulings:
- 2026-11-19 (class: a PRINCIPLE stated, in a DISCUSSION) "lets talk about the flags issue and make sure we understand it. if i write a binding A with a bunch of rx. then i use A like /(?i)${A}/ does A inherit or only direct // literals. i'd say it does. if the flag status is important to an rx, its that rx's responsibility to set them the way it wants and not assume. so if one builds up an rx, they inherit the flags of the surrounding. we might consider that on a flag by flag basis but that would be my expectation" (record: "2026-11-19 OWNER, discussing flags and a binding used in a hole")
rejected:
readings:
evidence: PART FF of predspec29 (flags-scope), PART TX of predspec291.
history:
- 2026-11-19: the record classes it a DISCUSSION with a LEAN and "a PRINCIPLE stated"; "flag by flag" became flags-scope (core/holes/flags).

## core/principles/composed-at-point — Composed at the point of use
was: core/principles/exact-wording (2026-11-19, a remark on the manager's method in the same entry, not a language principle: review r59 RULING-2)
slugs:
rulings:
- 2026-11-19 "zero-in-sequence: you are a lawyer in your exact wording. this is what is needed now. the condition is always sees the regex composed at the point it is used. so the 0: is the match so far" (record: "2026-11-19 OWNER RULING — zero-in-sequence")
rejected:
readings:
- number-names' "0 ... is always the entire match of the rx however it is composed" and zero-in-sequence are ONE rule under this principle (the manager's reading 8) — SUPPORTED (preddoc1 PART R8: 0 / 0 of 363 WHOLE / SEARCHED, a condition last in a sequence against an independent filter model).
- pass-start-read and label-flow are the same principle for labels (the manager's, "NOT his words today") — UNTESTED.
evidence: preddoc1 PARTS R8, R9, R11; EX-bare-condition.
history:
- 2026-11-19: stated with zero-in-sequence; applied the same day to a bare condition in a hole (core/holes/bare-condition).
- 2026-11-19 (lane preddoc4): the piece core/principles/exact-wording retired into this entry: his "you are a lawyer in your exact wording. this is what is needed now." (the same zero-in-sequence entry) is a remark on the manager's method, "no change asked" (the record); it belongs to the manager's skill, not to the language (review r59 RULING-2).

## core/principles/namespace-at-reference — The namespace at the point of reference
slugs:
rulings:
- 2026-11-18 "backref-across-parts: I agree but also, a reference should use the namespace as it is defined at the point of reference" (record: "2026-11-18 OWNER RULING — backref-across-parts: the part's own group; a reference uses the namespace at its point")
rejected:
readings:
evidence:
history:
- 2026-11-18: decided by it (census B5 P8): backref-across-parts, free-name, label-flow, same-name-twice.

## core/principles/operand-world — An operand's whole world
slugs:
rulings:
- 2026-11-17 "zero-place: oh boy, that was illustrative to use 0. But it might be useful so we can add it. It opens the can of worms of other numbers. For A & B: from the perspective of B, the subject is now whatever A matched. There is no outside subject (unless we allow context, etc). That's its whole world. So all numbers are labels of groups in that world. Also, not recommended to use group numbers as it's confusing on bound values you can't see" (record: "2026-11-17 OWNER RULING — zero-place: a pattern's numbers are labels in its own world")
rejected:
readings:
- the law `A & B` = `A & (0: B)` (the manager's, 2026-11-17) — SUPPORTED for the nested set of reading 12 (preddoc1 PART R12, 0 / 0 / 0 of 364).
evidence: preddoc1 PART R12; EX-bare-and.
history:
- 2026-11-17: decided zero-place; 2026-11-19 it gives `${A & (0: digit)}` its `0` = A only.

## core/principles/positions-own-rules — Each hole position has its own rules
slugs:
rulings:
- 2026-11-18 "Name-hole: this is why each target area of the hole is a different thing with its own rules. I agree that arrays in names are a compiler error." (record: "2026-11-18 OWNER RULING — name-hole: an array in a group-name hole is a compile error")
- 2026-11-17 "and its more than two kinds. the kinds are all the various places it can be inserted" (record: "2026-11-17 OWNER RULING — two kinds of hole; illegal combinations are removed")
rejected:
- one product column for every position (the draft's revision 25.1 table) — by owner ruling — "the ruling was for counting holes which duplicate the pattern. It doesn't apply for rx holes. Idk for others" (product-order).
readings:
evidence:
history:
- 2026-11-17/18: the insert's kinds are its positions; decided by it: name-hole, product-order (1), other-holes, the option hole.

## core/principles/structural-warnings — Warnings are structural or library-defined
slugs:
rulings:
- 2026-11-17 (class: PRINCIPLE) "What are all the warning items? Warnings should be structural or definable by a library option." (record: "2026-11-17 OWNER — a principle for warnings")
rejected:
readings:
evidence:
history:
- 2026-11-17: decided by it: polarity-rule, the warnings list; the `$x & S` warning is keyed on the form (core/diagnostics/dollar-form).

## core/principles/match-and-filter — Rx that can match, rx that can filter
slugs:
rulings:
- 2026-11-18 "That means for rx: There is rx that can match. There is rx that can filter. Neither is wholly a subset of the other" (record: "2026-11-18 OWNER RULING — complement-place: the error is at the USE; two kinds of rx")
rejected:
readings:
- the illustration: filter-only a complement, match-only an outward-looking edge assertion, both `/\d+/` (the manager's) — UNTESTED here (the draft R.1.0 head).
evidence: PART CX of predspec26 (the KIND rule as code).
history:
- 2026-11-18: stated as what follows from complement-place; core/filters/kinds is its rule.

## core/principles/matching-language — A matching language
slugs:
rulings:
- 2026-11-17 (class: reflections, principles for the draft's framing) "I like this language because it's in terms no normal imperative language is." Then: "It's a bit deceptive in that it looks like functions and predicates and loops but it's not. Also, I and try to keep this in mind, it's a matching language not a finding language. That's where the SQL analogy breaks down because I expect the filter over times loop to return a set but it's not" (record: "2026-11-17 OWNER, on what kind of language this is")
rejected:
readings:
evidence:
history:
- 2026-11-17: the record classes these "reflections, recorded as principles for the draft's framing, not rulings on any answer". The pilot gave it `ruled` for want of a status (its FORMAT PROBLEMS); status `principle` since 2026-11-19.

## core/principles/left-decides — The left side decides
slugs: join-order
rulings:
- 2026-11-17 "join-order: left side decides. That's always how I thought of it. In concedes the logical purity that you seemed to be going for for the reality that regex is not pure." (record: "2026-11-17 OWNER RULING — join-order: the left side decides")
rejected:
readings:
evidence:
history:
- 2026-11-17: join-order.

## core/principles/stated-behaviour — Stated behaviour
slugs:
rulings:
- 2026-11-19 "padded-lazy-sparse: stated behavior." (record: "2026-11-19 OWNER RULING — padded-lazy-sparse; with remarks on `padded`'s width, a `limited` macro, and a direction on macros")
- 2026-11-19 "i agree with your lean" (record: "2026-11-19 OWNER RULING — padded-order")
rejected:
- an error for a shorter string listed before a longer one — by owner ruling — padded-order.
readings:
- the general statement over every macro body, and the words "the body's stated behaviour, not an error" (the lean padded-order agreed to), are the manager's; the owner ruled padded's case only — the status is `reading` (review r59 RULING-1).
evidence: lib/modifiers/padded's details; PART PO of predspec291.
history:
- 2026-11-19: the phrase was the manager's (padded-order's lean); the owner used it himself in padded-lazy-sparse ("stated behavior"). The census found no owner quote only because it searched the British spelling.
- 2026-11-19 (lane preddoc4): `ruled` to `reading`; the manager's words left the second rulings item; lib/modifiers/padded no longer names this piece in `by:` (review r59 RULING-1).

## core/principles/nothing-outside-domain — Nothing, not an error
slugs:
rulings:
- 2026-11-19 "number-edge: nothing" (record: "2026-11-19 OWNER RULING — number-edges")
- 2026-11-19 "literal "a" + "b" is an error because there is no compatible type defined and they are not in the default type (if that works). for now, as you say, we are restricting arithmetic to digits and anything else is nothing (for runtime compatibility) and a warning if known" (record: "2026-11-19 OWNER RULING — plus-operands")
rejected:
readings:
- the reach of the rule beyond arithmetic (every operation outside its domain yields nothing) — the manager's widening of his arithmetic-only words; a reading (review r59 RULING-7).
evidence: PARTS NE, PL of predspec291.
history:
- 2026-11-18/19: number-domain's "does not fit yields nothing", then number-edges and plus-operands; his first plus-operands sentence is a later direction (operand types), not in force.
- 2026-11-19 (lane preddoc4): the statement restated as arithmetic's, the wider reach marked a reading (review r59 RULING-7).

## core/principles/build-later — Build later: the under-construction sign
slugs:
rulings:
- 2026-11-18 "value-hole: let's use the unifying idea for it. Change my answers to match. The following can be delayed in build. That means both directions: \d + 1 matches the digits 1 through 10. left(2) is the leftmost two digits of an rx. ... We can create functions like left() and restrict them to constants now. I'd like to consider that unbuilt territory however and the error is an "under construction" sign." (record: "2026-11-18 OWNER RULING — match-is-rx: the unifying idea; "Change my answers to match"")
- 2026-11-18 "construction-line: enumerate" (record: "2026-11-18 OWNER RULING — construction-line: enumerate")
rejected:
readings:
evidence: the draft R.1.16 (ONE TYPE).
history:
- 2026-11-18: match-is-rx (4), then his clarification "so the "under construction" was not about arrays but about regexes used on macros that you would think expect a constant" and construction-line placed the line.

## core/principles/check-his-regex — Check his regex
slugs:
rulings:
- 2026-11-19 (class: STANDING INSTRUCTION) "in general: be suspicious of my regex and confirm contemporaneously if you see inconsistencies." (record: "2026-11-19 OWNER RULING — anything-text; and a standing instruction on his regex")
rejected:
readings:
evidence: applied the same day: `/${(0: digit)}/` never holds (zerohole.py); `limited(padded(digits), 5)` = `limited(digits, 5)` (limited.py).
history:
- 2026-11-19: a STANDING INSTRUCTION (the record's class), sent to main as a proposed skill edit.

## core/principles/language-over-macros — The language, not one macro
slugs:
rulings:
- 2026-11-19 (class: DIRECTION) "ALSO: i don't at this junction want to go too deeply into any one macro UNLESS it raises interesting points about the language. padded does to some degree because i had not thought as much about order." (record: "2026-11-19 OWNER RULING — padded-lazy-sparse; with remarks on `padded`'s width, a `limited` macro, and a direction on macros")
rejected:
readings:
evidence:
history:
- 2026-11-19: a DIRECTION for the work (the record's class); it parks `limited` (parked/ideas/limited).

## core/principles/labels-as-defined — Use the rules as defined
slugs:
rulings:
- 2026-11-19 (class: DIRECTION) "i think it will be common to build up rx using multiple bindings. what will happen is that as the exported space will get more filled. ... i say the strategy is to use labels as they are defined and see if there is a problem." (record: "2026-11-19 OWNER, on building rx from many bindings: use the label rules as defined, watch for a problem")
rejected:
readings:
evidence: PART TA of predspec291 (isodate three times).
history:
- 2026-11-19: a DIRECTION: no change to the label rules now.

## core/model/match — What a match is
slugs:
rulings:
- 2026-11-17 "branch-scope: yes. I like that. Also, that makes me like 9:30 choice from yesterday more as well because if we have atomic, you can get the alternative I mentioned." (record: "2026-11-17 OWNER RULING — branch-scope: reading")
- 2026-11-17 "However, it is in line with regex behavior so I do like it and think it should be the general behavior" (record: "2026-11-17 OWNER, on the model after branch-scope")
- 2026-11-16 "row-is-match: yes I agree." (record: "2026-11-16 OWNER RULING — row-is-match")
- 2026-11-17 "regex-settles: yes settled" (record: "2026-11-17 OWNER RULINGS — regex-settles; absent-under-not")
- 2026-11-17 "Then from the perspective of the condition, an rx is a black box that exposes labels" (record: "2026-11-17 OWNER RULING — nested-pass: the outermost view")
rejected:
- the SQL model, an enclosing condition that does not make the inner pattern reconsider — by owner — "this is a break from the SQL model we were using ... However, it is in line with regex behavior so I do like it" (record: "2026-11-17 OWNER, on the model after branch-scope").
- three-valued tests (an absent label UNKNOWN) — by owner ruling — regex-settles (1), a test on an absent label fails.
readings:
- a loop's passes include PCRE's trailing empty pass (by the default of exception-rule; his observation "makes sense as the entire rx is optional", not a ruling) — SUPPORTED (the draft R.1.7 (4a): the literal loop, the hole loop and `occurrences` agree with libpcre2).
evidence: preddoc3a_model.py MATCH (the record's own example: WHOLE `123` a = `1`, b = `23`; the python `re` lowering `1\d+` gives the same spans in all three modes).
history:
- 2026-11-16: row-is-match; a row was a row of the pass table before it.
- 2026-11-17: branch-scope (reading (ii)) made a condition a piece of the pattern; the SQL reading went; regex-settles closed the five points; the nested-pass addendum gave the black-box principle.
- the slugs pass-and and joint-last-pass moved to core/labels/labels-vs-captures, empty-pass to core/labels/one-rule, outer-pass-forms to core/model/places/outermost-view (lane preddoc3a): each is answered there.

## core/model/modes — The three modes
slugs: whole-text empty-search-error
rulings:
- 2026-11-17 "exception-rule: everything that looks like regex should behave like regex unless we explicitly allow." (record: "2026-11-17 OWNER RULING — exception-rule")
- 2026-11-17 "empty-search-error: warning" (record: "2026-11-17 OWNER RULING — empty-search-error: a warning")
- 2026-11-17 "Whole text: adopt it if it's legal. Not sure about the "fail" part" (record: "2026-11-17 OWNER RULING — whole-text: adopted if legal")
rejected:
- a compile error for a searched pattern that can match the empty text (the draft's) — by owner ruling — empty-search-error, "warning".
- a `fail` branch for the whole-text check — by owner — "Not sure about the "fail" part"; the check needs none.
readings:
- FIND-ALL is PCRE2's global loop, the non-empty retry after an empty report included (the draft's R.1.11, by the default of exception-rule) — SUPPORTED (preddoc3a_model.py: every FIND-ALL line of the five sections agrees with python `re.finditer` where a lowering exists; PSR shows the empty reports).
- whole-text is legal with the ruled pieces (`J & C & occurrences(M)`; the condition "adopt it if it's legal") — the draft's R.1.11 writes it with ruled pieces only — UNTESTED here (no run of `occurrences`; see lib/search/occurrences).
evidence: preddoc3a_model.py AND (the example line).
history:
- 2026-11-17: whole-text UN-PARKED and adopted if legal; empty-search-error ruled a warning.
- the slug atomic-search moved to core/patterns/atomic, caller-ambiguous to core/labels/export/caller-ambiguous (lane preddoc3a).
- 2026-11-19 (lane preddoc4): the whole-text idiom `J & C & occurrences(M)` moved to lib/search/occurrences; this piece keeps "a check of the whole text is a WHOLE match" (review r59 PLACE-2 (b)).

## core/model/table — The table of paths and its order
slugs: pass-table hit-list value-point
rulings:
rejected:
- the pass table as the meaning of a bare condition (pass-table) — by owner ruling — last-pass-default and after-loop-read; a pass's own labels survive only inside the group questions (core/model/table/group-truth).
readings:
- the table, its order and a row per labelling (the manager's restatement of branch-scope and row-is-match) — SUPPORTED (preddoc3a_model.py TABLE: the second branch is reached when the first one's label is rejected; the lowering `3\d|\d3` agrees).
- a label takes its value at its group's close, a condition placed after the group reads it (value-point, the manager's reading, closed by entailment) — SUPPORTED (pass-start-read's run, preddoc3a_model.py PSR).
- an atomic part takes its first row before an outside condition filters (regex-settles (5)) — SUPPORTED (preddoc3a_model.py ATOM).
- a filtered argument's hits are its own rows (hit-list; regex-settles (4), the one-pattern model) — UNTESTED here (lib/search/hits).
evidence: preddoc3a_model.py TABLE; the example is invented (no printed answer).
history:
- the draft R.1.2; the pass table was the model's centre before last-pass-default (2026-11-17).

## core/model/table/group-truth — Group questions over the pass table
slugs: group-truth
rulings:
rejected:
readings:
- (a) `NOT some(c)` = `occurs.none(c)` — SUPPORTED by the draft's E12 (0 / 0 / 0), not re-run here.
- (b) `occurs.none(NOT c)` differs from both (21 / 201 / 301 of 364, E12) — not re-run here.
evidence: the draft §R.8 row group-truth / pass-table (E12).
history:
- new piece (lane preddoc3a): the slug was on core/model/table, whose statement does not answer it; the draft keeps it asked ("the 11-18 rulings do not entail an answer").

## core/model/places — The place table
slugs:
rulings:
rejected:
readings:
- the table (the draft R.1.0's, restated by the manager): each row follows from the piece it names — UNTESTED as a table; each place's piece carries its own run.
- a place with no row is not a place a part can stand in — UNTESTED (a statement of scope).
evidence:
history:
- the draft R.1.0 (the place table). `predicates_future.md` items 16 and 22 are this piece (in the documents, not parked).
- the outermost view split off as core/model/places/outermost-view (lane preddoc3a): it is ruled, the table is not.

## core/model/places/outermost-view — The outermost view
slugs: nested-pass outer-pass-forms
rulings:
- 2026-11-17 "The view of the labels on an rx is the outermost view. To get inner views you nest the labels and condition" (record: "2026-11-17 OWNER RULING — nested-pass: the outermost view")
rejected:
- the innermost or per-inner-pass view for a bare condition — by owner ruling — nested-pass.
readings:
- pass tests on a label two loops deep range over the outermost loop's passes (outer-pass-forms; told, his confirmation "this is how i expected", not asked as a ruling) — SUPPORTED by the draft R.1.7 (4b), not re-run here.
evidence: the draft R.1.7 (4b): `/(?:(?:(?<h>\d)?;)*,)*/ & (h: <5)` on `3;,,` and `3;;,` FAIL.
history:
- new piece (lane preddoc3a), split from core/model/places.

## core/patterns/literals — Literals and regex text
slugs:
rulings:
- 2026-11-14 "I agree... I was mostly thinking about multi line predicate syntax" (record: "2026-11-14 RULINGS on predicates_draft.md §13")
- 2026-11-15 "agree. Limited to where | is used to mean alternation. Also, \& should work as escape. Why not?" (record: "2026-11-15 RULINGS — `anchored` has exact ends; which `&` is the operator in rx text")
rejected:
- implicit extended mode under the predicate opt-in — by owner ruling — C2.
- `&` an operator in rx text only right before a `${` hole — by owner — "5. no. I thought we were going to add & to pcre but conditionally with a module or option? Also, fully yes or no." (the record's 2026-11-15 entry "the five open items", a bold opener inside a paragraph, so not a citable title; ruled there: `&` in rx text is all or nothing, by a module or option).
readings:
- a one-literal program is today's PCRE pattern, no strict subset (a lean of review OWN-14, the draft §11) — UNTESTED.
- the strict subset inside a larger program (`\K`, `(*ACCEPT)`, `\G`, verbs, callouts refused) — the draft §11 STATUS: "Literal leanings incl. the strict subset: RULED" on an informal 2026-11-13 entry ("I like your suggestions") that has no title of its own — UNTESTED.
- `&` OFF by default (the manager's lean, the draft §13 O60) — UNTESTED.
- `${` opens a hole in every position, `$\{` is a literal (the draft §11) — UNTESTED.
evidence: preddoc3a_model.py LIT (`/a b|c/` keeps its space; python `re` agrees).
history:
- 2026-11-14: C2 superseded "the predicate opt-in implies x-mode".
- 2026-11-15: `&` in rx text all or nothing; which `&` under ON.

## core/patterns/flags — Flags in a literal
slugs:
rulings:
- 2026-11-14 "I agree... I was mostly thinking about multi line predicate syntax" (record: "2026-11-14 RULINGS on predicates_draft.md §13")
- 2026-11-18 "a hole takes the flags in force at the hole. each regex literal has its own flags." (record: "2026-11-18 OWNER RULING — hole-flags: a hole takes the flags in force at the hole; each regex literal has its own flags; and his question, do flags propagate down")
- 2026-11-18 "flags-propagate: yes" (record: "2026-11-18 OWNER RULING — flags-propagate: yes")
rejected:
readings:
- an `&` written at program level keeps each side's own flags; flags-in-filter as "reach" (the manager's reading after "by "flags propagate" i thought we decided that rx inherits the flags of the surrounding rx", a recollection) — UNTESTED here (core/holes/flags carries the hole case).
- a sequence operand at program level has no surrounding rx and starts from its own flags (the same reading) — UNTESTED.
evidence: preddoc3a_model.py FLAGS (`/a(?i)b/`: the flag applies from where it is written; python `re` `a(?i:b)` agrees).
history:
- 2026-11-18: hole-flags and flags-propagate; 2026-11-19: flags-scope (which flags an inserted rx inherits) is core/holes/flags.

## core/patterns/sequence — The sequence operator
slugs: sequence-operator sequence-precedence sequence-reading rx-module
rulings:
- 2026-11-17 "sequence-reading: splice." (record: "2026-11-17 OWNER RULING — sequence-reading: splice; and the hole reopened")
- 2026-11-17 "sequence-precedence: binds tighter than & and | / sequence-operator: is there a reason why not? I expect rx construction and concatenation is common enough there." (record: "2026-11-17 OWNER RULINGS — the rx module: sequence-precedence and sequence-operator")
rejected:
- juxtaposition as the sequence (`A B`) — by owner — "A B isn't legal so its the addition form" (core/patterns/quantifiers).
- a string paste of the operands — by owner ruling — sequence-reading, splice.
readings:
- the sequence mark cannot begin an operand (the draft R.1.14) — UNTESTED.
evidence: preddoc3a_model.py SEQ (the draft's PART RX1 line; `\b\d+\b` agrees; the printed answers reproduced). PART RX of predspec25.
history:
- the draft R.1.14. `predicates_future.md` item 21 (the rx module) is this section's (in the language, not parked).

## core/patterns/alternation — Alternation
slugs:
rulings:
- 2026-11-17 "branch-scope: yes. I like that." (record: "2026-11-17 OWNER RULING — branch-scope: reading")
- 2026-11-17 "join-order: left side decides. That's always how I thought of it." (record: "2026-11-17 OWNER RULING — join-order: the left side decides")
rejected:
- reading (i) of branch-scope: a condition after a `|` judges only the branch the pattern chose first — by owner ruling — branch-scope (ii).
readings:
- `c | d` between conditions is the one `|` (the draft R.1.5; condition-or deleted as a separate construct) — SUPPORTED by the regex model (an alternation of two zero-width tests).
evidence: preddoc3a_model.py ALT (the draft's PART A B1 line; printed answers reproduced; `\d\d` agrees).
history:
- 2026-11-17: branch-scope (ii); join-order gave the distribution over a `|` on the left.

## core/patterns/quantifiers — Postfix quantifier operators
slugs:
rulings:
- 2026-11-17 "so the two argument form of + is addition, and the single postfix version is 1 or more. if we're going there, lets just do it. + +? * *? ? ??" (record: "2026-11-17 OWNER RULING — quantifier operators")
- 2026-11-17 "lets include the possessive forms but the brace counts are repeat. "did you mean A+ followed by B" A B isn't legal so its the addition form." (record: "2026-11-17 OWNER RULING — quantifier operators")
- 2026-11-17 "also, operator precedence. i'm thinking fairly tight with parenthesis otherwise. right?" (record: "2026-11-17 OWNER RULING — quantifier operators")
rejected:
- a "did you mean" message for `A+ B` — by owner ruling — "A B isn't legal so its the addition form".
- brace counts as postfix operators — by owner ruling — "the brace counts are repeat".
readings:
- the longest-first token reading, binary after `+`/`*` when an operand follows, stacking (the draft R.1.14) — UNTESTED.
evidence: preddoc3a_model.py QUANT (the draft's PART RX8 line; printed answers reproduced; `(?:ab)+` agrees); sabotage s8 (a text paste) caught. PARTS RX7-RX9 of predspec25.
history:
- the draft R.1.14 (THE POSTFIX QUANTIFIER OPERATORS).

## core/patterns/atomic — Atomic parts
slugs: atomic-search
rulings:
- 2026-11-17 "regex-settles: yes settled" (record: "2026-11-17 OWNER RULINGS — regex-settles; absent-under-not")
- 2026-11-17 "Atomic as used by say atomic() would provide pcre behavior." (record: "2026-11-17 OWNER on atomic-search")
rejected:
- an atomic pattern stopping the search at later starts (his item-14 reading "returns nothing") — by owner — atomic-search: "what I was looking for was more akin to (*prune) or similar".
readings:
evidence: preddoc3a_model.py ATOM (the draft's B8 / V17 line; printed answers reproduced; `1\d` agrees); sabotage s7 caught.
history:
- 2026-11-17: regex-settles (5); atomic-search moved the other reading to the backtracking verbs (parked/ideas/atomic). The slug came from core/model/modes (lane preddoc3a).
- 2026-11-19 (lane preddoc4): the name `atomic(X)` is the library body lib/control/atomic; this piece keeps the rule (review r59 PLACE-2 (a)).

## core/patterns/lookaround — Lookaround
slugs: lookahead-labels
rulings:
- 2026-11-18 "lookahead-labels: agree" (record: "2026-11-18 OWNER RULING — lookahead-labels: visible, as in PCRE")
- 2026-11-17 "regex-settles: yes settled" (record: "2026-11-17 OWNER RULINGS — regex-settles; absent-under-not")
rejected:
readings:
- a lookbehind's labels are visible the same way (the manager's) — UNTESTED.
evidence: preddoc3a_model.py LOOK (the draft's PART LA line; printed answers reproduced; no plain-`re` lowering: the condition compares two labels); sabotage s6 caught. PART LA of predspec26.
history:
- the draft R.1.0 lookaround row.

## core/labels/labels-vs-captures — Labels and captures
slugs: pass-own-labels pass-and joint-last-pass
rulings:
- 2026-11-17 "after-loop-read: ok I see it. Last pass own label makes sense" (record: "2026-11-17 OWNER RULING — after-loop-read: the last pass's own label")
- 2026-11-17 "I do want that. It makes sense and frankly pcre is wrong on this. I agree but! We need a way to get the pcre behavior even if ugly" (record: "2026-11-17 OWNER RULING — what an unqualified `$x` reads")
- 2026-11-18 "backref-label: capture" (record: "2026-11-18 OWNER RULING — backref-label: capture")
rejected:
- "labels match every pass, captures match the last" for a bare condition — by owner — reconsidered within minutes: "what you should do is assign the condition inside the loop to get the all behavior" (record: "2026-11-17 OWNER, reconsidering the entry above within minutes"); closed by after-loop-read.
- regex's carried value for a bare looped label (last-pass-default: regex) — by owner ruling — after-loop-read and the `$x` ruling ("frankly pcre is wrong on this"); the carried value stays reachable as the capture.
- a compile error for a bare condition after a loop (the manager's lean) — by owner ruling — after-loop-read.
- pass-and (a Kleene AND over passes) and joint-last-pass — dissolved by the two-valued model and after-loop-read (a joint reads the last pass's own tuple).
readings:
- the array form's index counts settings (the draft R.1.7) — UNTESTED.
evidence: preddoc3a_model.py CAPT, CAPT2 (the draft's PART L: `\k<m>` reads the capture `45` while the label m is unset; python `re` agrees on the regex half); sabotage s9 caught.
history:
- 2026-11-17: last-pass-default (regex), then "labels match every pass", reconsidered within minutes, then after-loop-read and the `$x` ruling (the settled state of the evening).
- 2026-11-18: backref-label (capture).
- the skeleton's statement "A label matches every pass; a capture is PCRE's last value" (the superseded entry) replaced by the after-loop-read statement (lane preddoc3a).

## core/labels/one-rule — One label rule: branchings reset
slugs: bare-loop-label before-and-inside array-slot shared-label repeated-means unsettable-label empty-pass
rulings:
- 2026-11-17 "Yes. Let's keep it" (record: "2026-11-17 OWNER RULING — branchings reset the labels inside them")
- 2026-11-17 "array-slot: only what was set. As you say, someone could get the empty values." (record: "2026-11-17 OWNER RULING — array-slot: only what was set")
- 2026-11-17 "polarity-rule: warning for both. Warnings are errors given some strictness setting eg @config.strict()" (record: "2026-11-17 OWNER RULING — polarity-rule")
rejected:
- one label name on both sides of `&` an error for existing (shared-label: "keep the compiler error") — by owner — revised by label-flow: an ambiguous REFERENCE is the error (core/labels/flow).
- empty places for resets in the array form — by owner ruling — array-slot.
- before-and-inside as its own rule — dissolved by the one rule.
- bare-loop-label "labels match every pass" — by owner — reconsidered (core/labels/labels-vs-captures).
readings:
- a counted repeat `{n}` with n >= 2 is a loop, `{1}` no branching (the manager's) — UNTESTED.
- repeated means set in a loop by its operand regex (the manager's ruling, owner told) — SUPPORTED by the draft's E11 (0 / 0 / 0 of 364 against set-once).
- the empty last pass is a pass (empty-pass; told, his observation) — SUPPORTED by the draft R.1.7 (4a).
evidence: preddoc3a_model.py ONE (the table he was shown with after-loop-read: `3qxx` FAILS, `q3xx` and `7q3xx` HOLD a = `3`; printed answers reproduced); sabotage s2 caught.
history:
- 2026-11-17: the one label rule ("branchings reset"), array-slot, shared-label (then revised by label-flow); polarity-rule made the unsettable label a warning.
- the slug empty-pass came from core/model/match (lane preddoc3a).

## core/labels/flow — Labels across composed parts
slugs: label-flow label-mark
rulings:
- 2026-11-17 "a. yes. a label from an rx is whatever label is surfaced by that rx. b. thats a good point but list here is one rx so exposes one h. i adjust my rules to be such that a compose and a literal rx have the same label behavior" (record: "2026-11-17 OWNER RULING — label-flow")
- 2026-11-17 "label-flow: 1. propose: it is an error to ambigously reference a label. so if A & B & (h: blah) and A and B both use label h, it is an error. this is different than "its an error for labels of the same name to exist at all in A & B"" (record: "2026-11-17 OWNER PROPOSAL — label-flow: an ambiguous REFERENCE is the error")
rejected:
- across the sequence operator a name both parts set is ambiguous (point 2 of his proposal) — by owner — withdrawn by his adjustment ("a compose and a literal rx have the same label behavior").
readings:
- a chain `A & B` with h on both sides, used as a part, still surfaces h ambiguously (the manager's) — UNTESTED.
- label-mark (the single labelling form the rx module offers) is closed by entailment; its spelling stays in core/spellings — not a run question.
evidence: preddoc3a_model.py FLOW (the draft R.1.13 (3)(i) line; printed answers reproduced; `\d(?:,\d)?` agrees on the spans).
history:
- 2026-11-17: the proposal, then the ruling with his adjustment; shared-label's error revised to the reference.

## core/labels/export — Export and private labels
slugs: export-rule export-scope free-name
rulings:
- 2026-11-18 "export-rule: Agee and add [_a = A] is a private reference that wouldn't export at all" (record: "2026-11-18 OWNER RULING — export-rule: public unless `_`; a binding shows its own public labels and its public part labels")
- 2026-11-18 "I meant it wouldn't export outside the binding. To close all exports use [_ = A]" (record: "2026-11-18 OWNER, clarifying export-rule's sixth statement, and adding a form: `[_ = A]` closes all exports")
- 2026-11-18 "backref-across-parts: I agree with error. It is like if a function in C were defined then references a variable it doesn't have defined so it looks up the call stack to the previous definition. Catastrophic. The rx should export the group." (record: "2026-11-18 OWNER RULING — free-name: a reference to a name the rx does not define is an error")
rejected:
- "a filter can never produce captures" (his lean, filter-captures) — closed by export-rule: visibility goes by export, not by the operand's role.
- an explicit export spelling — by owner ruling — export-rule: the `_` prefix decides.
readings:
- a filter operand's labels are visible like any others (the draft R.1.13, filter-captures not adopted) — UNTESTED.
- his remark of 2026-11-19 ("it might be more that private labels are only visible in a binding scope") — already ruled as statement 1 (recorded as a recollection, nothing new).
evidence: preddoc3a_model.py EXP (the draft's PART TB (2) line; printed answers reproduced; `[2-9]\d{3}` agrees). PARTS TA, TB of predspec291.
history:
- 2026-11-18: the proposal (labels seen only if exported), the export-scope discussion, the ruling, the clarification of statement 6 and `[_ = A]`.

## core/labels/export/caller-ambiguous — What the caller gets for an unreferenced shared label
slugs: caller-ambiguous read-out
rulings:
- 2026-11-18 "The caller's captures: agree" (record: "2026-11-18 OWNER, export-scope discussion, third exchange")
- 2026-11-18 "export-rule: Agee and add [_a = A] is a private reference that wouldn't export at all" (record: "2026-11-18 OWNER RULING — export-rule: public unless `_`; a binding shows its own public labels and its public part labels")
rejected:
- (b) h absent from the captures; (c) the last mention's value (the right side's); (d) the left side's value — by owner ruling — export-rule statement 5 (the caller's captures follow the program's rules, where a shared public name is an ambiguous reference).
readings:
- the record's export-rule discussion: "a name two parts both make public is an ambiguous reference for the caller as for the program", pending a ruling (the manager's reading of "The caller's captures: agree") — favours (a) or (e); not ruled.
evidence: preddoc3a_model.py CALL (the spans; the draft's PART R47 B13 printed the same spans under every candidate, reproduced).
history:
- new piece (lane preddoc3a): the slug was on core/model/modes; the draft R.1.13 leaves it "NOT DEFINED".
- 2026-11-19 (lane preddoc4): narrowed to (a) against (e); (b)-(d) to `rejected:` by export-rule statement 5; the record's slug read-out (path-and-ambiguity's second corner) homed here (review r59 RULING-3). The base's slug stays caller-ambiguous.

## core/labels/paths — Part labels and paths
slugs: path-and-ambiguity
rulings:
- 2026-11-18 "so I agree the last reference" (record: "2026-11-18 OWNER on path-and-ambiguity: the part label used twice is RULED; the read-out is open")
- 2026-11-18 "Naming [x = A] only disambiguates scope, it doesn't give additional access" (record: "2026-11-18 OWNER, export-scope discussion, third exchange")
- 2026-11-17 "label-flow: 1. propose: it is an error to ambigously reference a label." (record: "2026-11-17 OWNER PROPOSAL — label-flow: an ambiguous REFERENCE is the error")
rejected:
- a part label used twice is an error — by owner — "I mean, harmless I guess ... so I agree the last reference".
readings:
- `x.h` follows the one label rule inside A; an ambiguity judged where the reference is written; `alt.x[1]` legal (the draft R.1.13) — UNTESTED.
- the read-out corner (what a caller gets) — core/labels/export/caller-ambiguous.
evidence: preddoc3a_model.py PATH (the draft's PART LF line; printed answers reproduced; `[01]\d` agrees) and PATH2 (his corner 1: the last mention); sabotage s18 caught.
history:
- 2026-11-18: corner 1 ruled; corner 2 (the read-out) went to filter-captures, export-scope, export-rule.

## core/labels/backreferences — Backreferences
slugs: backref-label backref-across-parts same-name-twice
rulings:
- 2026-11-18 "backref-label: capture" (record: "2026-11-18 OWNER RULING — backref-label: capture")
- 2026-11-18 "same-name-twice: i agree with your lean." (record: "2026-11-18 OWNER RULING — same-name-twice: an error at the backreference unless `(?J)`")
- 2026-11-18 "backref-across-parts: I agree but also, a reference should use the namespace as it is defined at the point of reference" (record: "2026-11-18 OWNER RULING — backref-across-parts: the part's own group; a reference uses the namespace at its point")
- 2026-11-18 "backref-across-parts: which is to say, it should be the last reference as labels" (record: "2026-11-18 OWNER, clarifying backref-across-parts — a backreference reads as labels do: the last mention at its point")
- 2026-11-18 "backref-across-parts: I agree with error." (record: "2026-11-18 OWNER RULING — free-name: a reference to a name the rx does not define is an error")
rejected:
- a backreference that reads the label (reset on entry) — by owner ruling — backref-label: capture.
- the written-out regex's reading (one namespace for the whole composition) — by owner ruling — backref-across-parts.
readings:
- a reference to a name unset at its point fails, as regex's does (the manager's) — UNTESTED.
evidence: preddoc3a_model.py BREF (the draft's PART REF REF2 line; printed answers reproduced; `\d(\d)\1` agrees); sabotage s10 caught.
history:
- 2026-11-18: backref-across-parts, its clarification, free-name, backref-label, same-name-twice.

## core/labels/numbers — Numbers name groups only without ambiguity
slugs: number-names zero-place numbered-label-warning
rulings:
- 2026-11-18 "number-names: exactly. Only when there is no ambiguity." (record: "2026-11-18 OWNER RULING — number-names")
- 2026-11-18 "number-names: the exception to our rule is 0. It is always the entire match of the rx however it is composed." (record: "2026-11-18 OWNER RULING, addendum to number-names — zero is the exception")
- 2026-11-17 "For A & B: from the perspective of B, the subject is now whatever A matched. There is no outside subject (unless we allow context, etc). That's its whole world. So all numbers are labels of groups in that world." (record: "2026-11-17 OWNER RULING — zero-place: a pattern's numbers are labels in its own world")
- 2026-11-17 "Also, not recommended to use group numbers as it's confusing on bound values you can't see" (record: "2026-11-17 OWNER RULING — zero-place: a pattern's numbers are labels in its own world")
rejected:
readings:
- a number on a group whose name is shared inside one literal is refused (the draft R.1.13) — UNTESTED.
- the numbered-label warning (the manager's proposal from his "not recommended", accepted: record "2026-11-17 OWNER — the numbered-label warning accepted") — the wording is core/diagnostics'.
evidence: preddoc3a_model.py NUM (the draft's PART NUM (2) line; printed answers reproduced).
history:
- 2026-11-17: zero-place, label numbers tried, the warning accepted; 2026-11-18: number-names and its addendum.
- 2026-11-19 (lane preddoc4): the statement's "`0` is always the entire match" now points at the deciding piece core/conditions/match-so-far (his addendum's words stay in the rulings items; after a complete pattern the match so far IS the entire match); the bullet "inside a loop body, the pass's" removed (the loop case is core/conditions/match-so-far/in-loop); the warning's trigger stated once, as the record's accepted proposal words it (review r59 ZERO, READ-10).

## core/labels/numbers/in-loop — A number on a group optional in a loop
slugs: number-in-loop
rulings:
rejected:
readings:
- (a) the label (the draft R.1.13's reading) — the run: preddoc3a_model.py NUML, the printed LABEL answers reproduced.
- (b) the capture — NUML2: WHOLE `3;;` HOLDS under python `re`; label vs capture 8 / 33 / 33 of 364 (the draft's PART R47 A3, not re-run).
evidence: preddoc3a_model.py NUML, NUML2.
history:
- new piece (lane preddoc3a): the slug was on core/conditions/match-so-far, whose ruled statement does not answer it.

## core/conditions/form — The condition form
slugs: condition-not condition-or dollar-condition label-twice-warn
rulings:
- 2026-11-16 "record-is-product: absolutely. This is precisely the sort of simplifying semantics I'm looking for." (record: "2026-11-16 OWNER RULING — record-is-product: yes")
- 2026-11-16 "label-twice: agree an error. And that means it's also unofficially parked in case some other meaning becomes valuable" (record: "2026-11-16 OWNER RULING — label-twice: an error")
- 2026-11-17 "Agree with all three." (record: "2026-11-17 OWNER RULING — the three remaining error-or-warning candidates")
- 2026-11-16 "colon-scope: yes with refinement: (a, b = c): ... the 'c' is a binding et al" (record: "2026-11-16 OWNER RULING — colon-scope: yes, with a refinement for a default")
- 2026-11-16 "condition-not : yes allow not" (record: "2026-11-16 OWNER RULING — condition-not: allowed")
- 2026-11-14 "is somewhat structural because it's combined with the comma. & binds tighter" (record: "2026-11-14 RULING — C22, condition binding")
rejected:
- the diagonal reading of a label named twice — by owner ruling — label-twice ("unofficially parked").
- `|` between conditions as a Kleene OR (condition-or) — deleted with the three-valued model (regex-settles).
readings:
- a condition is a value of its own kind (bound, passed, put in an array) (the draft §4.1) — UNTESTED.
- `P & x: S` and `[x: S]` are errors; parentheses kept (the manager's call on "a condition without its parentheses") — see core/spellings/condition-parentheses.
evidence: preddoc3a_model.py FORM (invented; the lowering `[1-9]\d:[1-2]\d` agrees).
history:
- 2026-11-14 C22; 2026-11-16 colon-scope, record-is-product, label-twice, condition-not; 2026-11-17 the three candidates (label-twice-warn kept the error).
- 2026-11-19: dollar-diagnostic answered dollar-condition (the form `$x & S` stays legal and gets a warning); the warning's wording is core/diagnostics/dollar-form's.

## core/conditions/two-valued — Conditions are two-valued
slugs: three-valued polarity-rule record-under-not
rulings:
- 2026-11-17 "regex-settles: yes settled" (record: "2026-11-17 OWNER RULINGS — regex-settles; absent-under-not")
- 2026-11-17 "Absent under not: use regex rules." (record: "2026-11-17 OWNER RULINGS — regex-settles; absent-under-not")
- 2026-11-17 "polarity-rule: warning for both. Warnings are errors given some strictness setting eg @config.strict()" (record: "2026-11-17 OWNER RULING — polarity-rule")
- 2026-11-16 "not-is-complement: yes agree" (record: "2026-11-16 OWNER RULINGS — not-is-complement and mark-in-none")
rejected:
- "absence never matches, negated or not" (condition-not's absence clause) — by owner ruling — absent-under-not.
- three-valued logic (three-valued) — retired: the regex model entails it (the manager's reading, closed by regex-settles).
- record-under-not as a question — dissolved (a record is the `&` of its entries with or without NOT).
- a never-pass test as an error (the draft §5.2) — by owner ruling — polarity-rule.
readings:
evidence: preddoc3a_model.py TV (the draft's PART A U1 line; printed answers reproduced; the lowering agrees), TV2 (U2: `NOT (a: <5)` on `1` HOLDS); the three-spellings table is the draft §R.3's (N1-N4), reproduced by DEF for `(h = "x": !<5)`; sabotage s5 caught.
history:
- 2026-11-16: condition-not with "absence never matches"; 2026-11-17: regex-settles and absent-under-not reversed the absence clause; polarity-rule.

## core/conditions/in-sequence — A condition as a sequence operand
slugs: condition-in-sequence
rulings:
- 2026-11-18 "condition-in-sequence: yes and it's probably more natural than & but allow both." (record: "2026-11-18 OWNER RULING — condition-in-sequence: yes, and `&` stays")
- 2026-11-17 "pass-start-read: yes keep it" (record: "2026-11-17 OWNER RULING — pass-start-read")
rejected:
readings:
evidence: preddoc3a_model.py INSEQ (the condition tested each pass; `(?:[0-4];)+` agrees; the draft's CS1 `7;3;` FAILS reproduced); sabotage s15 caught. PART CS of predspec26 and predspec261.
history:
- the draft R.1.14 (A CONDITION IN SEQUENCE).

## core/conditions/quantified — A quantifier on a condition
slugs: quantified-condition
rulings:
- 2026-11-18 "quantified-condition: an error. This is a formal punt because we may find a better meaning for it in the future and this keeps that from breaking current code" (record: "2026-11-18 OWNER RULING — quantified-condition: an error, as a formal punt")
rejected:
- regex's meaning with a warning (the manager's leaning) — by owner ruling — the formal punt.
readings:
evidence: PART CS CS4 of predspec26.
history:
- skeleton; condition-group (a group holding only conditions) is open in the draft §R.8.
- 2026-11-19 (lane preddoc4): the slug condition-group moved to its own open sub-piece core/conditions/quantified/group (review r59, the manager's known residual).

## core/conditions/quantified/group — A group holding only conditions
slugs: condition-group
rulings:
rejected:
readings:
- open in the draft §R.8 ("condition-group"); never put to the owner — the manager's brief of lane preddoc4 makes it an open piece; the candidates are the lane's statement of the two ways the ruled quantified-condition can extend.
evidence:
history:
- 2026-11-19 (lane preddoc4): a new open sub-piece; the slug came from core/conditions/quantified, where it sat on a ruled piece.

## core/conditions/match-so-far — The match so far
slugs: zero-in-sequence
rulings:
- 2026-11-19 "zero-in-sequence: you are a lawyer in your exact wording. this is what is needed now. the condition is always sees the regex composed at the point it is used. so the 0: is the match so far" (record: "2026-11-19 OWNER RULING — zero-in-sequence")
- 2026-11-19 ""Inside an inserted part": for a condition bare, yes. like /${(0: digit)}/ but not /${A & (0: digit)}/ where it is only the A" (record: "2026-11-19 OWNER, on `0` inside an inserted part: a bare condition sees the surroundings; `A & (0: ..)` sees only A")
- 2026-11-19 "yes, thanks: /\d${(&(0:digit))}/ and /\d/ & (0: digit) are the same thing" (record: "2026-11-19 OWNER, confirming: a bare condition last in an rx equals the condition on the whole")
rejected:
- the error for now (the manager's leaning) — by owner ruling — zero-in-sequence.
- a bare condition's `0` in a hole as the inserted part's own (the draft's reading, PART N NZ) — by owner — "for a condition bare, yes".
readings:
evidence: preddoc3a_model.py ZERO (the record's zeroseq.py answers reproduced; `7\d` agrees); sabotage s11 caught. preddoc1 PARTS R8, R9.
history:
- 2026-11-19: zero-in-sequence; the bare condition in a hole; the confirmation. The slug number-in-loop moved to core/labels/numbers/in-loop (lane preddoc3a).
- 2026-11-19 (lane preddoc4): the deciding piece for `0` (core/labels/numbers points here); the bare-condition-in-a-hole facts are core/holes/bare-condition's alone (review r59 RULING-8); the loop case moved to the open sub-piece core/conditions/match-so-far/in-loop (review r59 ZERO).

## core/conditions/match-so-far/in-loop — The match so far inside a loop
slugs: zero-in-loop
rulings:
rejected:
readings:
- the reading today, (b), from the rx's start: the manager's reading (c) of the zero-in-sequence entry ("inside a loop the match so far includes the earlier passes (from the rx's start, not the pass's): to run") — SUPPORTED as a model by preddoc1 PART R9 (the callout model: the match's start, not the pass's; the two differ on 4 / 16 / 28 of 364, first `3;3;`); not his words.
- (a), the pass's: the base said it before (core/labels/numbers, "inside a loop body, the pass's"), the draft's reading; his "the 0: is the match so far" and "composed at the point it is used" do not say which start a pass has — the two readings stood in two pieces (review r59 ZERO); asked as zero-in-loop.
- the witness `(/\d/ SEQ (0: /\d/) SEQ ";")+` on `3;4;`: (a) WHOLE HOLDS, (b) WHOLE FAILS — SUPPORTED (preddoc4 PART ZL; sabotage s7, (b) in both lines, caught).
evidence: docs/dev/lanes/preddoc4_evidence/ PART ZL; preddoc1 PART R9.
history:
- 2026-11-19 (lane preddoc4): a new open sub-piece: the two readings of `0` in a loop stated once, as a question (review r59 ZERO).

## core/conditions/pass-start-read — Labels as they stand
slugs: pass-start-read pass-list-read looped-warning
rulings:
- 2026-11-17 "pass-start-read: yes keep it" (record: "2026-11-17 OWNER RULING — pass-start-read")
- 2026-11-17 "I do want that. It makes sense and frankly pcre is wrong on this." (record: "2026-11-17 OWNER RULING — what an unqualified `$x` reads")
rejected:
- a "pass begins" reset rule — by owner ruling — pass-start-read (keep the previous pass's value before the group).
- `$x` "as standard pcre" (pass-list-read's literal reading) — by owner ruling — the `$x` ruling: `$x` reads the label.
- a warning on a bare condition over a looped label (looped-warning) — withdrawn by the manager (the draft §R.2, with `compare.looped`).
readings:
evidence: preddoc3a_model.py PSR (the draft's PART PS line; printed answers reproduced) and PSR2 (WHOLE equals "the items are non-decreasing" on 1,365 texts over `139;`); sabotage s12 caught.
history:
- the draft R.1.7; 2026-11-17 pass-start-read and the `$x` ruling.

## core/conditions/defaults — Defaults and absent labels
slugs: nullable-meaning
rulings:
- 2026-11-16 "default-scope: yes per test" (record: "2026-11-16 OWNER RULING — default-scope: per test")
- 2026-11-16 "colon-scope: yes with refinement: (a, b = c): ... the 'c' is a binding et al" (record: "2026-11-16 OWNER RULING — colon-scope: yes, with a refinement for a default")
rejected:
- a default reaching past its own test (per program) — by owner ruling — default-scope.
readings:
- a default outside the test's set reads as no default at every polarity (the draft R.1.6) — SUPPORTED (preddoc3a_model.py DEF: `x` HOLDS as with no default).
- nullable-meaning (a nullable `occurrences` argument) is lib/search/occurrences' fact, not this piece's — the slug stays here (see the report).
evidence: preddoc3a_model.py DEF (the draft §R.3 N4 line; printed answers reproduced; `[5-9]?x` agrees); sabotage s13 caught.
history:
- 2026-11-16: default-scope (a lane considered both), then ruled per test.

## core/filters/and — The `&` operator
slugs:
rulings:
- 2026-11-15 "That's a good clarification" (record: "2026-11-15 RULING — the sides of `&` "match the same stretch whole"; the word "anchored" is kept for the macro")
- 2026-11-17 "operand-context: yes to that interpretation. Also, then the start of subject and end of subject need the same interpretation" (record: "2026-11-17 OWNER RULING — operand-context")
- 2026-11-17 "join-order: left side decides. That's always how I thought of it. In concedes the logical purity that you seemed to be going for for the reality that regex is not pure." (record: "2026-11-17 OWNER RULING — join-order: the left side decides")
- 2026-11-17 "For A & B: from the perspective of B, the subject is now whatever A matched." (record: "2026-11-17 OWNER RULING — zero-place: a pattern's numbers are labels in its own world")
rejected:
- the right side deciding — by owner ruling — join-order.
- a separate anchor rule for filters — by owner ruling — operand-context (one sentence: the stretch as the whole text).
readings:
- a condition in an `&` chain stands after every pattern operand (the draft R.1.4) — UNTESTED here.
evidence: preddoc3a_model.py AND (the draft's PART F line; printed answer reproduced; `\d` agrees), AND2 (join order: `G & L` vs `L & G` on `11`); sabotages s3, s4 caught.
history:
- 2026-11-15: "match the same stretch whole"; 2026-11-17: operand-context's one sentence, join-order, zero-place.

## core/filters/operand-context — What a filter operand may contain
slugs: operand-context
rulings:
- 2026-11-17 "operand-context: ^ $ should be redundant as the filter is anchored. Does that mean that interpretation is unnecessary? I would say at this point that any piece that might look outside is a compiler error. Then if we discover later we can relax it we can review." (record: "2026-11-17 OWNER RULING — operand-context")
rejected:
readings:
evidence:
history: skeleton; the draft R.1.4.

## core/filters/complement — Complement
slugs: nested-complement
rulings:
- 2026-11-17 "regex-settles: yes settled" (record: "2026-11-17 OWNER RULINGS — regex-settles; absent-under-not")
- 2026-11-16 "not-is-complement: yes agree" (record: "2026-11-16 OWNER RULINGS — not-is-complement and mark-in-none")
- 2026-11-18 "complement-place: is this legal? not_seven := not seven It stands alone. I think it's the use that is the problem" (record: "2026-11-18 OWNER RULING — complement-place: the error is at the USE; two kinds of rx")
rejected:
- `!` on a condition — by owner ruling — not-is-complement (a compile error naming the two rewrites).
readings:
- a complement inside an `occurrences` argument rejects a path (nested-complement, entailed by hit-carry's premise) — SUPPORTED by the draft's PART RS RS1 (81 of 364 differ from the committed reading), not re-run here.
- `!` in rx text keeps PCRE's meaning (the 2026-11-15 correction: `!` inside a normal rx is parked) — UNTESTED.
evidence: preddoc3a_model.py COMP (`(?!7)\d+` agrees; the draft's `712` FAILS reproduced); sabotage s14 caught.
history:
- 2026-11-16 not-is-complement; 2026-11-17 regex-settles (2); 2026-11-18 complement-place.

## core/filters/kinds — Can match, can filter
slugs: complement-place lone-complement-match filter-captures
rulings:
- 2026-11-18 "That means for rx: There is rx that can match. There is rx that can filter. Neither is wholly a subset of the other" (record: "2026-11-18 OWNER RULING — complement-place: the error is at the USE; two kinds of rx")
- 2026-11-18 "lone-complement-match: let's keep it an error and provide "anything"" (record: "2026-11-18 OWNER RULING — lone-complement-match: it stays an error; provide "anything"")
rejected:
- the error at the binding (`not_seven := not seven`) — by owner — "It stands alone. I think it's the use that is the problem".
- a lone complement matching `anything & !B` implicitly — by owner ruling — lone-complement-match.
readings:
- filter-captures is not adopted as a rule: visibility goes by export (core/labels/export) — the draft R.1.13.
evidence: preddoc3a_model.py KINDS (`(?![78])\d+` agrees); sabotage s14 caught. PART CX of predspec26.
history:
- the draft R.1.0 head (THE TWO KINDS OF RX); 2026-11-19 anything-text ruled `anything` (lib/sets/anything).
- 2026-11-19 (lane preddoc4): the example's `not /7\d*/ & not /8\d*/` (lower-case `not`, no spelling) rewritten `!/7\d*/ & !/8\d*/`; answers unchanged (preddoc4 PART KI; sabotage s3 caught) (review r59 NEGATION).

## core/filters/negation — Negation
slugs: not-is-complement
rulings:
- 2026-11-16 "not-is-complement: yes agree" (record: "2026-11-16 OWNER RULINGS — not-is-complement and mark-in-none")
- 2026-11-16 "condition-not : yes allow not" (record: "2026-11-16 OWNER RULING — condition-not: allowed")
- 2026-11-17 "Absent under not: use regex rules." (record: "2026-11-17 OWNER RULINGS — regex-settles; absent-under-not")
- 2026-11-17 "when-meaning: agree" (record: "2026-11-17 OWNER RULING — when-meaning")
- 2026-11-18 "When: start with required then. Use NOT to get else behavior" (record: "2026-11-18 OWNER RULING — `then` is required; NOT gives the else-only behaviour")
rejected:
- lower-case `not` (the kinds example's `not /7\d*/`) — by the record — no-alpha-operators (the 2026-11-14 Q6 + Q9 entry: "a word is always a NAME"); the example now writes `!`.
- `NOT` on a condition as three-valued (the where-clause NOT of condition-not) — by owner ruling — absent-under-not ("use regex rules"): two-valued, a negative lookahead (core/conditions/two-valued).
readings:
- "NOT is a negative lookahead" is the manager's wording when-meaning agreed to; that it covers a zero-width PATTERN (`peek(A)`) and not only a condition is the reading the ruled `when` body needs (`NOT peek(test)`) — SUPPORTED as a lowering (preddoc4 PART NE: `\d(?!x)`; sabotage s6 caught).
- `NOT` as an exception to the no-alphabetic-operators rule: the record uses `NOT` in the owner's own ruled words ("Use NOT to get else behavior") — a reading that the rule's exception list holds it; spellings are placeholders (D193 addendum 4).
evidence: docs/dev/lanes/preddoc4_evidence/ PARTS NE, KI.
history:
- 2026-11-19 (lane preddoc4): a new piece: the one home of the negation spellings (review r59 NEGATION); the kinds example's undefined `not` replaced by `!`; the `when` body's `NOT peek(...)` stated legal here.

## core/values/reads — Reading a label
slugs: value-filter
rulings:
- 2026-11-18 "what i want is that $y works like label. however, there is a way to get the pcre capture value" (record: "2026-11-18 OWNER RULING — hole-reads-capture: the label; and a way to get the PCRE capture value")
- 2026-11-18 "Yes $y is a single value read at run time. At runtime, it is manipulated by left() et al using string manipulation built for simple strings. Semantically, $y is a regex of a single string. So operations that work on regex should work on it." (record: "2026-11-18 OWNER RULING — read-is-constant: yes; two forms of each operation")
- 2026-11-18 "unset-in-hole: i meant what you describe "no string" as. its a regex that matches nothing. that would be a good constant to provide" (record: "2026-11-18 OWNER RULING — unset-in-hole: no string, a regex that matches nothing; and an idea, a constant for it")
rejected:
- a read is PCRE's capture (`${$y}` = `\k<y>`) — by owner ruling — hole-reads-capture; run: the capture gives `3-3;-3;` HOLDS / `3-3;-3;`@0 / [`3-3;-3;`@0, ``@7, `7-7;`@8, ``@12] against the label's FAILS / `3-3;`@0 (preddoc3b EXreads; the draft's PART HR of rev 28, 2 / 2 / 2 of 21,845; sabotage s1 caught).
- "No conditions. No &." on a read (his own discussion, part (5)) — by owner ruling — read-is-constant ("we were applying & to $y"): value-filter answered legal (the draft's A5).
readings:
- a `$y` in an rx that does not define y is free-name's compile error (the draft R.1.15 (11), the manager's, SUPPORTED by the marks, not by a ruling) — UNTESTED (a refusal).
- a read in a hole needs the group's TEXT kept during the match whether or not the group is returned (the manager's m3, hand-worked) — UNTESTED.
evidence: preddoc3b EXreads; PART HR of predspec28.
history:
- 2026-11-18: hole-reads-capture and read-is-constant; the draft R.1.15 (3), (11), R.1.16 T20, A2, A5, A23. His recollection of the label-only group (parked/ideas/label-only-group) is not folded.
- 2026-11-19 (lane preddoc3b): converted from the skeleton; the example is the ruled witness.
- 2026-11-19 (lane preddoc4): "a read of a name the rx it is written in does not define is a compile error" restated as the one scope rule for `$` (a reading, tied to open bare-condition-labels): read literally it made the core's own examples (`$x` in an `&` operand, `${$y + 1}`) errors (review r59 READ-7).

## core/values/one-type — One type: a match is an rx
slugs: match-is-rx read-is-constant value-is-pattern
rulings:
- 2026-11-18 "value-hole: let's use the unifying idea for it. Change my answers to match." (record: "2026-11-18 OWNER RULING — match-is-rx: the unifying idea; "Change my answers to match"")
- 2026-11-18 "That means, in practice, that there are two forms for each of them: the compile time version that works on general regex, and the runtime version that,while compiled, works on single value strings at run time. So $y + 1 and \d + 1 look the same, the first one happens at run time, and the second at compile time." (record: "2026-11-18 OWNER RULING — read-is-constant: yes; two forms of each operation")
- 2026-11-18 "We can create functions like left() and restrict them to constants now. I'd like to consider that unbuilt territory however and the error is an "under construction" sign." (record: "2026-11-18 OWNER RULING — match-is-rx: the unifying idea; "Change my answers to match"")
rejected:
- "$x is not a pattern but a match" (his ground for keeping `$x & <5` an error, 2026-11-17) — by owner ruling — match-is-rx ("Change my answers to match"): `$x & <5` is legal (the draft's A1, A2); run: equal to `(x: <5)` on the digit run (preddoc3b EXonetype; sabotage s2, the chain not re-entering `\d+`, caught).
- a value in a pattern position is a STRING, not a one-member pattern (the draft rev 26's text) — by owner ruling — match-is-rx (A3); no answer moves.
- "adding two patterns is an ordinary type error" (the manager's) — by owner ruling — match-is-rx removes the type ground; plus-operands rules nothing (core/values/arithmetic).
readings:
- the condition and the macro stay their own kinds (the lane predspec27's reading; no line of the rulings names them) — UNTESTED.
- the composition rule, the stricter status wins (the draft's reading, review r48 FIXIND-10) — SUPPORTED as rule-as-code (PART TT of predspec28, sabotage s14).
- a computed value is a one-string rx known at run time, like a read (the draft's A11) — UNTESTED.
evidence: preddoc3b EXonetype; PARTS UT, TT of predspec27, predspec28.
history:
- 2026-11-18: value-is-pattern (one ruling, two leans, one idea), then value-hole "yes but", then match-is-rx and read-is-constant; the draft R.1.16 ONE TYPE, THE TYPE TABLE, ANSWERS CHANGED A1-A36.
- 2026-11-19 (lane preddoc3b): converted from the skeleton; the type table's rows are homed by position and operation (core/holes/*, core/values/*, core/arrays/*), not copied.

## core/values/number-domain — The number domain
slugs: number-domain domain-components numeral-width
rulings:
- 2026-11-18 "number-domain: canonical" (record: "2026-11-18 OWNER RULING — number-domain: canonical")
- 2026-11-18 "numeral-width: canonical" (record: "2026-11-18 OWNER RULING — numeral-width: canonical")
rejected:
- two domains (`+` reading `0099` as 99 while `<` excludes it; the draft rev 27) — by owner ruling — number-domain; run: `0099-100` HOLDS under it (preddoc3b sabotage s3 caught; PART H of predspec271).
- WIDTH KEPT (a result as wide as what was read) — by owner ruling — numeral-width: canonical; the composition `padded($y - 1, strlen($y))` gives it (not built).
readings:
- "removed at compile time, nothing at match time" was in the definition quoted to him and is ruled with it (the manager's m3; confirmed review r52 H) — SUPPORTED by the record.
- canonical at every step of an intermediate result (`($y - 1) + 1`) and for two reads (the manager's m1 of numeral-width) — UNTESTED.
evidence: preddoc3b EXdomain (against the 10,000-copy lowering, 0 differing); PART NW of predspec28, PART H of predspec271.
history:
- 2026-11-18: his question on number-domain, then number-domain and numeral-width; the draft R.1.16 THE NUMBER DOMAIN, R.1.15 (2), A27.
- 2026-11-19: the base-class idea (parked/ideas/class-base) generalizes the domain; not in force.

## core/values/comparisons — Comparisons
slugs:
rulings:
- 2026-11-14 "number makes sense actually. Integers should be \d+ to be variable width. Unpad would be the right approach" (record: "2026-11-14 RULINGS on predicates_draft.md §13")
- 2026-11-15 "for numbers there was a critic complaining that \d\d & between(1,12) would only match 10-12 and i said yes, that is correct because the \d\d means two digits. if the intention was the numeric range 1-12 then either use \d{1,2} or similar or use a transform like padded(between(1,12)) to get between to ignore leading 0" (record: "2026-11-14 RULINGS on rev 3's contradictions"); under its bold line "2026-11-15 CONFIRMATION — numeric ranges are string sets; padding is an explicit transform"
- 2026-11-18 "number-domain: canonical" (record: "2026-11-18 OWNER RULING — number-domain: canonical")
rejected:
- a comparison that compares by VALUE (leading zeros ignored) — by owner ruling — the confirmation ("the "compares by value" reading is NOT adopted", the record); preddoc4 PART CM, sabotage s4 caught.
- `unpad` as the transform — by owner ruling — renamed `padded` (lib/modifiers/padded).
readings:
- unary only, and ONE atom binding tighter than `&`: the record's 2026-11-14 00:10 notes ("does `<` et al ever need to be binary? If not, unary only"; "does it need the parentheses: `x & <256`?") are the manager's summary of his questions, not quoted words; the draft §2.4 calls unary RULED (CF:250, his proposal) — kept as ruled by the draft's status, his words not on record verbatim.
- his "the < types must be primitive because the generator is primitive" (2026-11-12 informal discussion): the comparison set is native to the language (a generated pattern), not a library body.
- `>`/`>=` infinite, never enumerated; strings, decimals and radixes decided by the literal — the draft §2.4's text (LEAN for decimal) — not run here.
- `/\d+/ & <20`: WHOLE `19` HOLDS, `020` FAILS, `20` FAILS / SEARCHED `x25` `2`@1 / FIND-ALL [`2`@0, `5`@1, `7`@3, `0`@5, `19`@6] — SUPPORTED (preddoc4 PART CM, against the plain regex of the numerals below 20).
evidence: docs/dev/lanes/preddoc4_evidence/ PART CM; the draft §2.4.
history:
- 2026-11-19 (lane preddoc4): a new piece: the comparison sets had no piece though ruled pieces use them throughout (review r59 PRIMITIVES-MISSING, READ-1).

## core/values/tuples — Tuples
slugs: tuple-value tuple-anywhere set-arity two-orders record-is-product
rulings:
- 2026-11-16 "A pair as a value: I am ok with the tuple as a value. My request is that it's fleshed out and not the slice of an idea." (record: "2026-11-16 OWNER RULING + REQUEST — the tuple as a value: OK, to be fleshed out")
- 2026-11-16 "I meant left right in the expression sense around = You could use them as you say" (record: "2026-11-16 OWNER CLARIFICATION + ANSWER — "left/right" was about the binding sign; tuple-anywhere: yes")
- 2026-11-16 "I think the tuple mechanism as otherwise described handled the problem more simply which I like." (record: "2026-11-16 OWNER — on first-rest: the built-in tuple mechanism is simpler, "which I like"; and a question")
- 2026-11-16 "Set arity: yes. It's clean. I like it" (record: "2026-11-16 OWNER RULING — set-arity: a set carries an arity")
- 2026-11-16 "I agree. They look sufficiently different to me and I like the control." (record: "2026-11-16 OWNER RULING — two-orders: keep both")
- 2026-11-16 "record-is-product: absolutely. This is precisely the sort of simplifying semantics I'm looking for." (record: "2026-11-16 OWNER RULING — record-is-product: yes")
rejected:
- a third value kind for a set of tuples — by owner ruling — set-arity ("No third value kind", the record).
- first/rest binding with recursion as the order's definition — by owner ruling — first-rest PARKED (parked/ideas/tuple-apart).
- a warning between the two orders (the manager's lean) — by owner ruling — two-orders ("I like the control"; the record keeps both with no warning).
readings:
- each component read by its literal and in its literal's domain (`((h, m): >= (9, 0))` rejects `9:00`, `00` not canonical) — the manager's reading DICT-DOMAIN (the draft §2.4), not run here.
- how a tuple parses apart from a record (a parenthesised comma list standing as a value) — the reading the base states; the spelling is a placeholder.
- `time & ((h, m): >= (9, 30))`: WHOLE `9:45` HOLDS, `9:15` FAILS, `10:15` HOLDS / SEARCHED `10:30`@5 / FIND-ALL [`9:30`@0, `12:45`@10] — SUPPORTED (preddoc4 PART TU; sabotage s5, the per-part form, caught on `10:15`).
- tuple-parts (taking ONE tuple apart) is OPEN: core/modules/positional.
evidence: docs/dev/lanes/preddoc4_evidence/ PART TU; the draft §2.4 (TUPLE ATOMS), joint_condition.md item 4.
history:
- 2026-11-19 (lane preddoc4): a new piece: the tuple had no piece and its spelling read as a record (review r59 PRIMITIVES-MISSING, READ-15).

## core/values/computed-labels — Computed labels
slugs:
rulings:
- 2026-11-14 "I agree with both excepting the spelling ... no alpha operators ... with, check, in ... check is not `x := ...` ... don't want to go into new grammar lightly" (record: "2026-11-14 RULINGS on docs/dev/lanes/predx_report.md §11")
rejected:
readings:
- "a match-dependent binding is a computed label of the pattern whose labels it reads" — the manager's spelling LEAN in the same entry, the concept (compile-time checks and match-dependent bindings, no new grammar) agreed; the base's statement is that lean — a reading.
- an unset input gives an unset computed label — the lane's reading (preddoc3c's proposal), UNTESTED.
- `sum := $a + $b`, `/(?<a>\d)\+(?<b>\d)/ & (sum: <10)`: WHOLE `3+4` HOLDS, `7+8` FAILS / SEARCHED `2+2`@4 / FIND-ALL [`1+1`@0, `5+4`@8] — SUPPORTED (preddoc4 PART CL; sabotage s11, the concatenation, caught).
evidence: docs/dev/lanes/preddoc4_evidence/ PART CL; the draft §4.4.
history:
- 2026-11-19 (lane preddoc4): a new piece: length and month_numbered name bindings left of `:` with no core rule allowing it (review r59 PRIMITIVES-MISSING, READ-8).

## core/values/metadata — Metadata of a member
slugs:
rulings:
- 2026-11-14 "I agree with your leans excepting explain 6, and show 9 examples" (record: "2026-11-14 RULINGS on docs/dev/lanes/predx_report.md §11")
rejected:
- `/a|b|c/[1]` = `/b/` and an ordinal from 0 — by owner ruling — the leans agreed (Q7, 1-based).
readings:
- `.index` the original position and `.label` the original name: the record's "2026-11-14 — each's bindings" (a LEAN), with his "So d[1][1] is "a"" (record "2026-11-14 — index base") — a reading.
- a user label named `index` or `label` an error — the draft's LEAN, UNTESTED.
- `/${days}/ & (w.index: >= 2)`: WHOLE `Tue` HOLDS, `Mon` FAILS / SEARCHED `Wed`@4 / FIND-ALL [`Tue`@0, `Wed`@8] — SUPPORTED (preddoc4 PART ME; sabotage s10, 0-based, caught).
evidence: docs/dev/lanes/preddoc4_evidence/ PART ME.
history:
- 2026-11-19 (lane preddoc4): a new piece: `.index` and `.label` were used with no definition (review r59 PRIMITIVES-MISSING, READ-5).

## core/values/arithmetic — Arithmetic
slugs: plus-operands number-edges
rulings:
- 2026-11-19 "literal "a" + "b" is an error because there is no compatible type defined and they are not in the default type (if that works). for now, as you say, we are restricting arithmetic to digits and anything else is nothing (for runtime compatibility) and a warning if known" (record: "2026-11-19 OWNER RULING — plus-operands")
- 2026-11-19 "number-edge: nothing" (record: "2026-11-19 OWNER RULING — number-edges")
- 2026-11-19 "i don't think + should be used for anything that isn't numbers in one form or another." (record: "2026-11-19 OWNER, on plus-operands: `+` is for numbers only; a class as the base")
rejected:
- a TYPE ERROR for a non-number operand (the manager's lean) — by owner ruling — plus-operands.
- `+` joins strings or patterns (`"7" + 1` is `71`) — by owner ruling — "i don't think + should be used for anything that isn't numbers"; run: preddoc3b sabotage s5 caught (EXplus).
- a signed numeral for a negative result — by owner ruling — number-edges; run: `5--5` HOLDS under it (preddoc3b sabotage s4; PART NE of predspec281).
- `% 0` a compile error of its own (a constant divisor) — by owner ruling — number-edges.
readings:
- a member list (array, class) is filtered member by member: `\w + 1` = `\d + 1` (the manager's (d)) — SUPPORTED (PART PL of predspec29: 0 / 0 / 0 of 3,906; preddoc3b EXplus).
- "(joining is the sequence operator)" (the manager's (c) of plus-operands) — NOT SUPPORTED as complete: negated-class-hole's `join(c)` is a joining that is not the sequence operator; the piece names both.
- his first sentence (a literal `"a" + "b"` an ERROR once operand types exist) is a DIRECTION, "if that works", not in force (the draft's reading) — UNTESTED; ideas parked/ideas/restricted-parameter, parked/ideas/class-base.
evidence: preddoc3b EXplus, EXedges; PARTS PL, NE of predspec29, predspec291.
history:
- 2026-11-18: array-lift's arrays; value-is-pattern part 1.
- 2026-11-19: his restriction idea `m(g & /\d+/)`, "`+` is for numbers only", the base idea, plus-operands, number-edges; the warning's one trigger is the manager's call (core/diagnostics/warnings).

## core/values/functions — Single-value functions
slugs: construction-line
rulings:
- 2026-11-18 "construction-line: enumerate" (record: "2026-11-18 OWNER RULING — construction-line: enumerate")
- 2026-11-18 "so the "under construction" was not about arrays but about regexes used on macros that you would think expect a constant." (record: "2026-11-18 OWNER, what "under construction" was about")
rejected:
- one string only (`enumerate = 1`) — by owner ruling — construction-line (his first option, not taken).
- "may hold more than one string" as the line (the draft rev 27, 27.1) — by owner ruling — construction-line: a finite rx of many strings is built.
- §2.7's preimage filter called `left(n, S)` — by the manager's spelling call (A17): renamed `prefix_in(n, S)`; `left` is his image function.
- `left` taking the last characters — by run — preddoc3b sabotage s6 caught (EXleft).
readings:
- the three clauses in order (the assertion error first) (THE MANAGER'S CALL 1, review r52 B, answer-free) — SUPPORTED as rule-as-code (PART TT of predspec281).
- read compounds applied per member (the draft's reading, review r52 K) — SUPPORTED (PART RC of predspec281: equal to the compile-time copies in libpcre2, 0 / 0 / 0).
- characters or bytes for `left` (his "(Byte ideally)") — UNTESTED; parked/ideas/string-level-rx.
evidence: preddoc3b EXleft; PARTS CN, TT, RC of predspec28, predspec281.
history:
- 2026-11-18: match-is-rx (4), read-is-constant (4), the clarification, construction-line; `length($y)` written `strlen($y)` (THE MANAGER'S CALL 6, A26).

## core/arrays/lift — Arrays are alternations; operations lift
slugs: array-lift lift-order
rulings:
- 2026-11-18 "array-lift: I meant, alternations as you suggested. It's consistent that alternations combine on the product and multiply the rx and produce more alternations" (record: "2026-11-18 OWNER RULING — array-lift: operations on arrays combine on the product")
- 2026-11-18 "What is needed is a consistent, general rule about it and not something specific to adding to arrays for example. What happens to array + array ?" (record: "2026-11-18 OWNER on value-is-pattern: one ruling, two leans, one idea"); a LEAN, settled by array-lift
rejected:
- pairwise as default — by owner ruling — his own first message, replaced at once by him; run: `[2, 4] + [1, 10]` pairwise is `[3, 14]`, `12` FAILS (preddoc3b sabotage s7 caught).
readings:
- a repeated result is harmless (stated with the question, not objected to) — SUPPORTED (AL3 of predspec26: 0 / 0 / 0 of 364).
- the rule is about arrays the user writes, not a label's settings — UNTESTED (a scope statement).
- one array mentioned twice is independent per mention (the draft, review r47 D1) — SUPPORTED (preddoc2 PART RB).
- lift-order is enumerate's order (the manager's m2 of construction-line) — SUPPORTED (PART CN of predspec28); for a class, class-order.
evidence: preddoc3b EXlift; PART AL of predspec26.
history:
- 2026-11-18: array-lift; the draft R.1.14 (ARRAYS UNDER OPERATIONS), AL1/AL2.

## core/arrays/class-order — The order of a class's results
slugs: class-order
rulings:
- 2026-11-19 "class-order: longest" (record: "2026-11-19 OWNER RULING — class-order")
- 2026-11-19 "can we sort by length, longest first?" (record: "2026-11-19 OWNER, discussing class-order: longest first"); a question carrying the idea
rejected:
- codepoint order (the draft's lean, §5.5) — by owner ruling — class-order; run: SEARCHED `x10` `1`@1 against `10`@1 (0 / 250 / 570 of 3,906, PART CO of predspec291; preddoc3b sabotage s9 caught).
- "longest everywhere" (sorting alternations and arrays too) — by owner ruling — the class-only version was the one he took.
readings:
- no tie rule (the manager's 8) — SUPPORTED (20 shuffles, 0 differing; PART CO of predspec29).
- nesting with the alternation first (the manager's 9) — SUPPORTED (0 / 750 / 1,404 against sorting across).
- equal strings are one result (the manager's 11) — SUPPORTED (PART CO of predspec29).
evidence: preddoc3b EXclassorder; PART CO of predspec29, predspec291.
history:
- 2026-11-19: his question, "what do you mean class only?", then the ruling.

## core/arrays/class-positions — Two class positions in one lift
slugs: class-positions
rulings:
rejected:
readings:
- C1 vs C2 0 / 776 / 1,816, C1 vs C3 0 of 3,906; Q1 vs Q2 0 / 2,797 / 3,230; A vs B 0 / 750 / 1,404 (PART CO of predspec29, predspec291) — the candidates part, so asked.
evidence: preddoc3b EXclasspos (C1, C2 re-run); PART CO of predspec291 (P29-9).
history:
- 2026-11-19: the manager's reading (c) of class-order; widened by review r54 P29-9 with the class first.
- 2026-11-19 (lane preddoc4): the long candidate runs left the base for this entry, the base keeping the question and the candidates' names (review r59 READ-18 stage 1). As they stood: "Two classes, `\d + \d`: C1, the lift as one position, its results longest first; C2, the first class slowest in ascending order, the second's results longest first within each; C3, the first descending (= C1's answers). A lazy quantifier, `\d{1,2}? + 1`: Q1, the quantifier's order kept, each count's results longest first (SEARCHED `x100` `10`@1); Q2, the quantified class as one position (`100`@1). The greedy `\d{1,2} + 1` agrees. The class first, `\d + (1|9)`: A, the alternation's order outermost, each choice's class results longest first (SEARCHED `x11` `1`@1); B, the class position's results longest first across the lift (`11`@1)."

## core/holes/insert — One insert, its meaning by position
slugs:
rulings:
- 2026-11-17 "if thats what it is then ok. i visualize ${} as a string insert but in this case it is not, it is a context aware rx insert. then the solution to the illegal version is to remove illegal versions from the cartesion product." (record: "2026-11-17 OWNER RULING — two kinds of hole; illegal combinations are removed")
- 2026-11-17 "and its more than two kinds. the kinds are all the various places it can be inserted" (record: "2026-11-17 OWNER RULING — two kinds of hole; illegal combinations are removed")
- 2026-11-18 "Name-hole: this is why each target area of the hole is a different thing with its own rules." (record: "2026-11-18 OWNER RULING — name-hole: an array in a group-name hole is a compile error")
rejected:
- `${}` as a string insert — by owner ruling — "it is a context aware rx insert".
- "two kinds of hole" (pattern / value) — by owner ruling — the addendum: as many kinds as positions.
readings:
- a position with no row is a compile error (the manager's, revision 25.1, "MINE") — UNTESTED (a statement of scope).
evidence:
history:
- 2026-11-17: two kinds, then "more than two kinds"; the draft revision 25.1 had one table with one product column for every position; revision 26 split it (R.1.0 HOLE POSITIONS).

## core/holes/pattern — The pattern hole
slugs: hole-reading product-order
rulings:
- 2026-11-17 "hole-reading: agree and explicitly then, assertions become ok to cross the border" (record: "2026-11-17 OWNER RULING — hole-reading")
- 2026-11-18 "product-order: first, the ruling was for counting holes which duplicate the pattern. It doesn't apply for rx holes. Idk for others" (record: "2026-11-18 OWNER RULING — product-order: first slowest; and a correction of the product's scope")
- 2026-11-17 "sequence-reading: splice. But opening up the hole again, what was our rationale? I'm wondering if it would be ok if we declared that /xxx${/foo/}yyy/ was /xxx(?:foo)yyy/." (record: "2026-11-17 OWNER RULING — sequence-reading: splice; and the hole reopened")
- 2026-11-15 "anchored-in-hole: agree" (record: "2026-11-15 RULINGS — no anchored-specific error in a hole; the anchor warning covers every whole-match place")
rejected:
- the edge-assertion error for holes (the draft's L8) — by owner ruling — hole-reading ("assertions become ok to cross the border").
- one copy of the literal per value — by owner ruling — product-order (1), "It doesn't apply for rx holes".
- a string insert (`ab?c` for `/${/ab/}?c/`) — by owner ruling — hole-reading; the run: HOLDS / FAILS / [`abc`@2, `ac`@6] against the group's FAILS / `c`@1 / [`c`@0, `abc`@2, `c`@7] (PART RX3 of predspec25; preddoc1 EX-pattern, its rival xEX-pattern caught).
readings:
- a member that is not a legal pattern makes the whole a compile error (the draft's, revision 25.1) — UNTESTED.
- the can-never-match warning for an edge that cannot hold beside its neighbour (the manager's proposal inside the question he agreed to) — UNTESTED here (PART RX3 of predspec25: 0 of 364 texts match `/x${num}/`).
evidence: preddoc1 EX-pattern, EX-pattern-array; PART RX of predspec25.
history:
- 2026-11-17: hole-reading; the draft before it put "a hole's set" among the set positions with an edge-assertion error (the 2026-11-14 Q1 ruling, narrowed).
- 2026-11-18: product-order (1) took the copy rule off pattern holes; the "keeping its own flags" clause went with hole-flags (core/holes/flags).
- 2026-11-19 (lane preddoc4): the bullet on `anchored` in a hole left this piece; lib/search/anchored states it (review r59 PLACE-2 (d)).

## core/holes/count — The count hole
slugs: removal
rulings:
- 2026-11-17 "then the solution to the illegal version is to remove illegal versions from the cartesion product." (record: "2026-11-17 OWNER RULING — two kinds of hole; illegal combinations are removed")
- 2026-11-18 "Otherwise I agree with lean. It's predictable and the user can order the values themselves to get different results (eg longest first)" (record: "2026-11-18 OWNER RULING — product-order: first slowest; and a correction of the product's scope")
- 2026-11-18 "removal: whole copy" (record: "2026-11-18 OWNER RULING — removal: the whole copy")
- 2026-11-18 "2. for sanity sake, a count whole must have values that produce counts (and not convert to rx)" (record: "2026-11-18 OWNER on value-is-pattern: one ruling, two leans, one idea")
- 2026-11-17 "i agree with the count proposal." (record: "2026-11-17 OWNER RULING — the count proposal")
- 2026-11-19 "for counts, no iterations, iterated object disappears. useful semantic" (record: "2026-11-19 OWNER, after other-holes: a zero count, and the option hole's values"); an OBSERVATION, not a ruling
rejected:
- remove only the piece holding the hole — by owner ruling — removal: the run he was shown, `/a|\d{${m},${M}}/`, m := [5], M := [2]: whole copy, nothing matches, not even `a`; the piece, `a` matches (PART P P4 of predspec26).
- first hole fastest — by owner ruling — product-order (2) (PART D D1 of predspec251: 8 / 0 / 0 of 364 on labels x, y).
- a non-count member kept as PCRE's literal text (PCRE reads `\d{x}` as text) — by owner ruling — value-is-pattern (2).
- an illegal copy kept as text — by run — preddoc1 sabotage s13 (EX-count fails).
readings:
- a member that is not a count is a COMPILE ERROR (the manager's reading of "must") — UNTESTED (a refusal).
- a count too large for PCRE (70000) is a count whose copy is removed (the draft's, review r47 B3) — UNTESTED here (PART P P6b of predspec261).
- every copy removed: that literal never matches, with the can-never-match warning (the manager's) — UNTESTED (warning).
- lowering count holes as a sequence of per-hole alternations is NOT the copy rule once anything stands between the holes — SUPPORTED as a limit (PART R47 B1 of predspec261: 351 / 0 / 0 of 364).
evidence: preddoc1 EX-count, EX-count-zero; PART P of predspec26; PARTS RX4-RX5 of predspec25.
history:
- 2026-11-17: the count proposal and two kinds of hole; 2026-11-18 product-order scoped the product to COUNT holes, removal fixed the unit; revision 26.1 replaced "the pattern" by "the literal" (review r47 B9).
- 2026-11-19 (lane preddoc4): the bullet on the copies' group kind: branch reset `(?|...)`, the draft's reading (its count-hole copies, R.1.14 / PART RX4-RX5); the library example now writes the same expansion (review r59 READ-16).

## core/holes/name — The group-name hole
slugs: name-hole
rulings:
- 2026-11-18 "Name-hole: this is why each target area of the hole is a different thing with its own rules. I agree that arrays in names are a compiler error. I could also see them in the future being alternation as an interim product that is then further manipulated like Cartesian or join-per-element" (record: "2026-11-18 OWNER RULING — name-hole: an array in a group-name hole is a compile error")
rejected:
- copies that differ only in a group name joined as plain alternatives (the draft revision 25.1) — by owner ruling — name-hole; python `re` on `7`: a = `7`, b unset, the second copy dead (the record's run).
readings:
evidence: preddoc1 EX-name (its rival: an array accepted, sabotage xEX-name caught).
history:
- 2026-11-18: name-hole; the future possibility (an array of names as an interim product) is parked/ideas/cartesian.

## core/holes/class — The class-member hole
slugs: other-holes
rulings:
- 2026-11-19 "other holes: 1. classes should be alternations on the class like [x] | [y] like patterns. in practice, that means [xy]" (record: "2026-11-19 OWNER RULING — other-holes")
rejected:
- one copy of the LITERAL per value (the count-hole product) — by owner ruling — "alternations on the class ... like patterns"; by run — the copy reading differs from one class on 0 / 53 / 55 of 341 (preddoc1 PART R1, first `xy`).
- "more characters of the class" as the DEFINITION (the draft's reading, never put to him) — by owner ruling — kept only as the collapse of a NON-negated class; for a negated class it differs (core/holes/negated-class).
readings:
- the alternation is of the CLASS, no copies, never reorders the rest; non-negated it collapses to one class exactly, capture before it included (the manager's reading 1) — SUPPORTED (preddoc1 PART R1: 0 / 0 / 0 of 341, span and group; `[${c}q]` 0 / 0 / 0 of 341).
- one value of several characters, each a member; `^` first, `-`, `]`, `\` literal (the manager's reading 5) — SUPPORTED (preddoc1 PART R5: every character a member; the text paste differs: `[a-c]` holds on `b`, `[\d]` on `7`).
- a count-hole detail filed under other-holes (a member that is not a count: a kind error; a count PCRE refuses: its copy removed) is untouched by his words (the manager's (g)) — UNTESTED (core/holes/count).
evidence: preddoc1 EX-class, PARTS R1, R5; otherholes.py, otherholes2.py (the record's runs).
history:
- 2026-11-18: the draft R.1.0 cell "OPEN ("Idk for others")" with the draft's reading "more characters"; revision 26.1 showed the two readings part for a member in a literal with a capture before (0 / 32 / 32 of 121, PART R47 B6 of predspec261).
- 2026-11-19: other-holes ruled; predspec291 report sentence 4 lists the draft cells this replaces.

## core/holes/class/two-holes — Two holes in one class
slugs:
rulings:
rejected:
readings:
- two holes in one class: the alternation over every combination, product-order's order, unobservable for a non-negated class (the manager's reading 2, other-holes (d)) — SUPPORTED (preddoc1 PART R2: `[${a}${b}]` against `[xypq]` 0 / 0 / 0 of 781; first-slowest against first-fastest 0 / 0 / 0; `[${lo}-${hi}]`, the member `c-b` removed, against `[a-e]` 0 / 0 / 0 of 400).
evidence: preddoc1 EX-two-holes, PART R2.
history:
- 2026-11-19: the manager's reading (d) of the other-holes entry; not his words.

## core/holes/negated-class — The negated class hole
slugs: negated-class-hole
rulings:
- 2026-11-19 "negated-class-hole: [^${join(c)}]" (record: "2026-11-19 OWNER RULING — negated-class-hole")
rejected:
- one class built from all the values (`[^${c}]` as `[^xy]`; the manager's leaning) — by owner ruling — negated-class-hole: "none of these" is written with `join`; run: `a[^xy]` `ax` FAILS where `a(?:[^x]|[^y])` HOLDS (otherholes2.py; preddoc1 sabotage s6 caught).
readings:
- `[${join(c)}]` = `[${c}]` for a non-negated class; `[^${c}]` with two different values accepts every character (the manager's reading 6) — SUPPORTED (preddoc1 PART R6: 0 / 0 / 0 of 341; 592 of 592 characters U+0000..U+024F).
- a warning pointing at `join` for `[^${c}]` with two or more different values (the manager's call) — UNTESTED (a warning).
- `join` is a string function on arrays, the only joining that is not the sequence operator; its name to the spellings review (the manager's (d)) — UNTESTED.
- a negated range end with several values is the alternation (the manager's (e)) — UNTESTED by run (the same expansion as core/holes/range-end).
evidence: preddoc1 EX-negated-join, EX-negated-array, PART R6.
history:
- 2026-11-19: other-holes' reading (b) asked it; his answer was outside the two offered.
- 2026-11-19 (lane preddoc4): the definition of `join` left this piece for lib/strings/join (review r59 PLACE-2 (c)).

## core/holes/range-end — The range-end hole
slugs:
rulings:
- 2026-11-19 "2.  range end: again, alternation [a-z]|[x-z] which collapses to [a-z]. remove range errors from alternations" (record: "2026-11-19 OWNER RULING — other-holes")
rejected:
- one value only; an array a compile error (the manager's leaning) — by owner ruling — other-holes place 2.
- a member out of order a compile error of the whole — by owner ruling — "remove range errors from alternations"; the rival kept reversed (`[m-x]`) is caught (preddoc1 sabotage xEX-range).
readings:
- a range WRITTEN with single values out of order stays a compile error; removal is for alternation members only (the manager's reading 4, other-holes (e)) — SUPPORTED (preddoc1 PART R4: libpcre2 refuses `[z-a]`, "range out of order in character class").
- every member removed: the never-matching rx (the manager's reading 3) — SUPPORTED (preddoc1 PART R3: `[${lo}-a]`, lo := [x, z], is `(?!)`).
evidence: preddoc1 EX-range, PARTS R3, R4.
history:
- 2026-11-18: the draft had no reading for a range end (review r47 B6) and "a range whose ends are out of order: a compile error" (THE DRAFT'S READING, revision 25.1 had removal).

## core/holes/option — The option hole
slugs:
rulings:
- 2026-11-19 "3. options: error. no clear semantics" (record: "2026-11-19 OWNER RULING — other-holes")
- 2026-11-19 "for options: the empty {?${""}} would simply be no options are added. also, options restricted to legal set or error" (record: "2026-11-19 OWNER, after other-holes: a zero count, and the option hole's values")
- 2026-11-19 "a nothing in an option would have to be an error. i can think of no useful semantic" (record: "2026-11-19 OWNER, on the option hole: nothing there is an error")
rejected:
- one copy per combination (the draft revision 25.1) — by owner ruling — other-holes place 3.
- the empty value written as `(?)` text — by run — PCRE accepts `(?)` (libpcre2 10.46) and answers as no group; the rule does not depend on it (preddoc1 PART R7).
readings:
- "the legal set" = the inline option letters this language admits: `i m s x xx n U J r a aD aS aW aP aT` (from flags-scope's table and the draft's reading of P29-2), each accepted by libpcre2; `B u X q` refused (the manager's reading 7) — SUPPORTED (preddoc1 PART R7). `(?^)` is accepted by PCRE and not listed by the draft: not in the set (a reading).
- PCRE itself accepts a written `(?)` — RUN: yes (preddoc1 PART R7).
- a value known only at run time cannot stand in an option hole (options are fixed at compile time) (the manager's) — UNTESTED (a refusal).
- an option hole with ONE value is unchanged (the manager's (f)) — SUPPORTED (preddoc1 EX-option).
evidence: preddoc1 EX-option, EX-option-empty, PART R7.
history:
- 2026-11-18: the draft R.1.0 cell "OPEN ("Idk for others")"; its §11 shows a boolean option value `(?i=${ci})` (a typed-position example, not an option-letter hole).
- 2026-11-19: other-holes, then the empty value, then "a nothing": the manager's call "zero values an error" became his ruling.

## core/holes/zero-values — Zero values in a hole
slugs:
rulings:
rejected:
- "every copy removed, `(?!)`" for every position (the draft revision 26) — by review r47 B7 — one cell per position.
readings:
- his "for counts, no iterations, iterated object disappears" is the count VALUE zero, not zero values (the manager's reading, told to him, no objection recorded) — UNTESTED as to his intent; `x{0}` RUN (EX-count-zero).
evidence: preddoc1 EX-zero-values, PART R3; preddoc2 PART ZV (one example per sub-piece).
history:
- 2026-11-19: the other-holes entry's reading (c); "I miss-read the statement" (his) and the count observation.
- 2026-11-19 (lane preddoc2): split into one sub-piece per position (one piece, one status: the option cell is ruled, the rest are readings); the pilot's one table and its class-member example went to the sub-pieces.

## core/holes/zero-values/pattern — Zero values in a pattern hole
slugs:
rulings:
rejected:
- the empty string (an alternation of no members read as matching empty) — by run — it differs from `(?!)` on WHOLE `a` (preddoc2 PART ZV, rival plant xZV-pattern caught).
readings:
- pattern: an alternation of no members, `(?!)` (the draft's, revision 25.1) — RUN, consistent (preddoc2 PART ZV; a run of the reading's lowering, not an independent control of the reading).
evidence: preddoc2 PART ZV.
history:
- 2026-11-19: the pattern cell of the pilot's zero-values table.

## core/holes/zero-values/count — Zero values in a count hole
slugs:
rulings:
rejected:
- zero values read as the count value zero (`a{0}`, the object absent) — by run — it differs on WHOLE `` (preddoc2 PART ZV, rival plant xZV-count caught); the count value zero is the parent's last line.
readings:
- count: every copy removed, that literal never matches, with the can-never-match warning (the draft's, the count row) — RUN, consistent (preddoc2 PART ZV); the warning NOT RUNNABLE (a diagnostic).
evidence: preddoc2 PART ZV.
history:
- 2026-11-19: the count cell of the pilot's zero-values table.

## core/holes/zero-values/name — Zero values in a group-name hole
slugs:
rulings:
rejected:
readings:
- name: a compile error, not exactly one name (the manager's call) — UNTESTED (a refusal).
evidence:
history:
- 2026-11-19: the group-name cell of the pilot's zero-values table.

## core/holes/zero-values/class — Zero values in a class hole
slugs:
rulings:
rejected:
- the class cell `[${[]}x]` = `[x]` (the draft's reading) — by the manager's reading 3 (other-holes (c)), run — it differs from the alternation of no members on 1 / 6 / 7 of 40 (preddoc1 PART R3, first `ax`; sabotage s3 caught).
readings:
- class or range end with zero values or every member removed: the never-matching rx (the manager's reading 3) — SUPPORTED (preddoc1 PART R3).
evidence: preddoc1 EX-zero-values, PART R3; preddoc2 PART ZV.
history:
- 2026-11-19: the class-member and range-end cell of the pilot's zero-values table, with the pilot's example.

## core/holes/zero-values/option — Zero values in an option hole
slugs:
rulings:
- 2026-11-19 "a nothing in an option would have to be an error. i can think of no useful semantic" (record: "2026-11-19 OWNER, on the option hole: nothing there is an error")
rejected:
readings:
evidence:
history:
- 2026-11-19: the option cell of the pilot's zero-values table (the one ruled cell).

## core/holes/value — The value hole
slugs: value-hole unset-in-hole hole-reads-capture value-test
rulings:
- 2026-11-18 "value-hole: yes but. This is either different than regex logic and the separation should be clear OR the types unified. Eg A match is a regex" (record: "2026-11-18 OWNER on value-hole — "yes but": legal, on condition the type question is settled")
- 2026-11-18 "value-hole: let's use the unifying idea for it. Change my answers to match." (record: "2026-11-18 OWNER RULING — match-is-rx: the unifying idea; "Change my answers to match"")
- 2026-11-18 "what i want is that $y works like label. however, there is a way to get the pcre capture value" (record: "2026-11-18 OWNER RULING — hole-reads-capture: the label; and a way to get the PCRE capture value")
- 2026-11-18 "unset-in-hole: i meant what you describe "no string" as. its a regex that matches nothing. that would be a good constant to provide" (record: "2026-11-18 OWNER RULING — unset-in-hole: no string, a regex that matches nothing; and an idea, a constant for it")
- 2026-11-18 "${@y} stays as a future direction item and is not built or defined now" (record: "2026-11-18 OWNER RULING — `${@y}` is a future direction: not built, not defined now")
- 2026-11-18 "numeral-width: canonical" (record: "2026-11-18 OWNER RULING — numeral-width: canonical")
rejected:
- the plain hole reads PCRE's capture (`${$y}` = `\k<y>`) — by owner ruling — hole-reads-capture.
- an unset read as the EMPTY string; "auto fail to anything that touches it" (WHOLE-HOLE); a compile error — by owner ruling — unset-in-hole; the EMPTY rival makes `/(?<y>\d)?-${$y | "x"}/` hold on `-` (preddoc1 sabotage xEX-value-unset caught).
- the read pasted as regex SYNTAX — by the draft's run VH3 (`/(?<y>[\d.]+)-${$y}/` on `1.5-1x5` FAILS) under read-is-constant.
- `${@y}` as "any earlier setting, as an alternation" (the manager's sketch) — by owner ruling — not defined now (parked/ideas/array-in-hole).
readings:
- written today `${@y}` is a plain compile error (the manager's call 2, answer-free) — UNTESTED (a refusal).
- a read in a count, class or option position: the draft R.1.16 T13-T16 — UNTESTED here (to be converted).
evidence: preddoc1 EX-value, EX-value-unset; the draft R.1.15 (12) (PART UT UT4 of predspec27: 0 / 0 / 0 of 3,906 against plain PCRE).
history:
- 2026-11-18: a LEAN ("I love it if it works"), then "yes but", then match-is-rx; hole-reads-capture, unset-in-hole, numeral-width the same evening; the draft R.1.15 is the full account.

## core/holes/value/other-positions — A read in another hole position
slugs:
rulings:
rejected:
readings:
- the draft R.1.16 T13-T16 (THE DRAFT'S READINGS): T13 a read in a count position UNDER CONSTRUCTION; T14 a name read a COMPILE ERROR; T15, T16 class and option reads NOT STATED (construction-line (b)). The option read is a compile error by core/holes/option (other-holes: a value there is one of the option letters, known at compile time) — the lane's reading of T16 under the later ruling, UNTESTED.
evidence: the draft R.1.16.
history:
- 2026-11-19 (lane preddoc4): a new sub-piece: the base pointed a reader at the frozen draft for the current rule (review r59 READ-9).

## core/holes/flags — Flags at a hole
slugs: hole-flags flags-propagate flags-scope
rulings:
- 2026-11-18 "hole-flags: i have heard you say both that the ${} gets the flags in force and also that a hole has its own flags. i agree with your interpretation of flags and holes. a hole takes the flags in force at the hole. each regex literal has its own flags. do the flags propagate down though? /(?i)${/blah/}/ is blah case insensitive?" (record: "2026-11-18 OWNER RULING — hole-flags: a hole takes the flags in force at the hole; each regex literal has its own flags; and his question, do flags propagate down")
- 2026-11-18 "flags-propagate: yes" (record: "2026-11-18 OWNER RULING — flags-propagate: yes")
- 2026-11-19 "i agree with your inherit table excepting that U should also not be inherited. one could make a case that only i should be inherited" (record: "2026-11-19 OWNER RULING — flags-scope")
- 2026-11-19 "by "flags propagate" i thought we decided that rx inherits the flags of the surrounding rx" (record: "2026-11-19 OWNER, on flags-in-filter: what "flags propagate" meant")
rejected:
- NO INHERITED FLAGS ("a hole keeps its own flags"; the draft's own rule, never his) — by owner ruling — flags-propagate.
- every flag propagates (`n`, `U`, `xx`, `J`; the draft revision 28.1's reading) — by owner ruling — flags-scope; `/(?U)x${/a+/}/` SEARCHED `xaaa` gives `xaaa`@0, the text paste `xa`@0 (preddoc1 EX-flags-U, sabotage xEX-flags-U caught).
- the inserted literal spelt `(?^ims:...)` as "the" text — by review r54 P29-1 — `(?^)` does not reset `U`, a paste is no parse of its own (PART TX of predspec291).
- the hole's flags over a flag the literal writes — by owner ruling — flags-propagate, the override as asked (preddoc1 EX-flags-written, sabotage xEX-flags-written caught).
readings:
- "only i" inherited: his OBSERVATION, a possible narrowing, not ruled — UNTESTED.
- the not-inherited flags are the inserted rx's own defaults at any depth; `m`, `s` stay inherited until he rules the narrowing (the manager's) — UNTESTED here.
- the `r` and `a`-family flags inherited (the draft's reading, P29-2) — UNTESTED here (PART FA of predspec291).
evidence: preddoc1 EX-flags, EX-flags-written, EX-flags-U; PARTS FF, FA, TX, SQ of predspec291; PART FL of predspec28.
history:
- 2026-11-18: hole-flags and flags-propagate reversed the draft's NO INHERITED FLAGS (§11, §13 O32).
- 2026-11-19: flags-scope (`U` moved out); the r54 round made "parsed alone" the model (revision 29.1).
- 2026-11-19 (lane preddoc4): flags-in-filter (an open question in a bullet) became the open sub-piece core/holes/flags/in-filter (review r59 READ-9).

## core/holes/flags/in-filter — Flags of an `&` inside a hole
slugs: flags-in-filter
rulings:
rejected:
readings:
- the two sides of an `&` inside a hole start with the hole's flags (THE DRAFT'S READING REACH, 0 / 0 / 0 of 1,555 against the plain hole) — open in the draft §R.8; the record's "2026-11-19 OWNER, on flags-in-filter: what "flags propagate" meant" is his remark on it, not a ruling.
evidence: the draft's PART FF of predspec29 (REACH).
history:
- 2026-11-19 (lane preddoc4): a new open sub-piece, from a bullet of core/holes/flags (review r59 READ-9). The candidate (b) is the lane's statement of the rival the draft names (a filter operand's own world).

## core/holes/labels — Labels through a hole
slugs: inner-label-read
rulings:
- 2026-11-18 "export-rule: Agee and add [_a = A] is a private reference that wouldn't export at all" (record: "2026-11-18 OWNER RULING — export-rule: public unless `_`; a binding shows its own public labels and its public part labels")
- 2026-11-18 "Inserting through a hole." "Agree" (record: "2026-11-18 OWNER, continuing the export-scope discussion")
rejected:
- his lean "a filter can never produce captures" as a rule — by owner ruling — export-rule ("NOT CARRIED": visibility goes by export, not by an operand's role); the form he wanted is `[_ = A]`.
readings:
- inner-label-read (does the outer program see a label defined inside an inserted pattern) is answered by export-rule (2), (3) and the hole row (the manager's, 2026-11-19) — UNTESTED here (PART TA of predspec291 shows `/${isodate}!/` exporting).
evidence: preddoc1 EX-labels; PART TA of predspec291.
history:
- 2026-11-18: the export-scope discussion and export-rule; 2026-11-19 same-name-count's "(and `$h`)" withdrawn, leaving inner-label-read, then answered by this piece.

## core/holes/labels/hole-export — Does a hole re-export a part's labels
slugs: hole-export
rulings:
rejected:
readings:
- today an unlabelled sequence part exports nothing outside its binding while the same pattern through a hole does (the T-a surprise, told to him) — SUPPORTED as a fact of the rules as defined (PART TA of predspec291, P29-13).
evidence: PART TA of predspec291.
history:
- 2026-11-19: review r54 P29-13 asked it; open.
- 2026-11-19 (lane preddoc4): the statement says "outside a binding" (export rule 3 is the premise) and `needs: core/labels/export` (review r59 READ-14).

## core/holes/same-name — Same-name groups through a hole
slugs: same-name-count
rulings:
- 2026-11-19 "same-name-count: scoped" (record: "2026-11-19 OWNER RULING — same-name-count")
- 2026-11-19 "same-name-count: this is only about backreferences, not labels ?" (record: "2026-11-19 OWNER, on same-name-count: backreferences, not labels? — and a MANAGER CORRECTION"); a QUESTION, answered by a correction
rejected:
- a group through a hole counts as a second group of its name — by owner ruling — same-name-count; the rival (the outer `\k<h>` reading the inner group) holds on `a-bb` (preddoc1 sabotage xEX-same-name caught).
- "(and `$h`) mean the outer group" — by the manager's correction the same day — the manager's extension, not asked.
readings:
- `J` has no effect across a hole; the inner `\k<h>` and numbered references are the inner literal's own (the manager's readings 12, 13 of that entry) — SUPPORTED (PART FF of predspec29; A30, A34).
evidence: preddoc1 EX-same-name; PART SN of predspec281; PART SC of predspec291.
history:
- 2026-11-18: same-name-twice's reading (m1) left the hole case unstated; 2026-11-19 ruled.

## core/holes/bare-condition — A bare condition in a hole
slugs:
rulings:
- 2026-11-19 ""Inside an inserted part": for a condition bare, yes. like /${(0: digit)}/ but not /${A & (0: digit)}/ where it is only the A" (record: "2026-11-19 OWNER, on `0` inside an inserted part: a bare condition sees the surroundings; `A & (0: ..)` sees only A")
- 2026-11-19 "yes, thanks: /\d${(&(0:digit))}/ and /\d/ & (0: digit) are the same thing" (record: "2026-11-19 OWNER, confirming: a bare condition last in an rx equals the condition on the whole")
- 2026-11-19 "zero-in-sequence: you are a lawyer in your exact wording. this is what is needed now. the condition is always sees the regex composed at the point it is used. so the 0: is the match so far" (record: "2026-11-19 OWNER RULING — zero-in-sequence")
rejected:
- a `0` inside a part inserted through a hole stays that part's own (the draft's reading, PART N NZ of predspec261) — by owner ruling — for a BARE condition; CONFIRMED for `A & (0: ..)` (EX-bare-and: the surrounding reading never holds there, `x3` is not a digit; sabotage xEX-bare-and caught).
- a macro in a hole is the unapplied-macro error (`${(x: digit)}`; the draft §2.3, §5.1) — by owner ruling — a bare condition in a hole is legal (predspec291 report sentence 1).
- `${0: digit}` without parentheses — by the manager's call — a spellings item (core/spellings/condition-parentheses).
readings:
- a binding whose whole body is a bare condition behaves as the bare condition (the manager's reading 11) — SUPPORTED (preddoc1 PART R11: the record's printed answers for `/\d${(0: digit)}x/` reproduced; the rival, the binding as its own rx, never holds; sabotage s15 caught).
- at the very START of an rx it tests the empty match so far, a candidate for the can-never-match diagnostics (the manager's (c)) — UNTESTED (a warning); `/${(0: digit)}/` never holds (zerohole.py, CHECKED CONTEMPORANEOUSLY in the record).
- `A & (0: digit & (b: blah))` = `A & (0: digit) & (b: blah)` (the manager's reading 12) — SUPPORTED for `0` (preddoc1 PART R12: 0 / 0 / 0 of 364, span and b; sabotage s11 caught); after a NAMED label the draft's existing error — UNTESTABLE by run (a refusal).
evidence: preddoc1 EX-bare-condition, EX-bare-and, PARTS R11, R12; zerohole.py, zeroseq.py (the record's runs).
history:
- 2026-11-19: zero-in-sequence, then his "yes ... but not", his confirmation, his spelling correction `${0: digit}`, his "${} implies (?:${})" (SUPPORTED by hole-reading), then the parentheses remarks; rev 29.1 only marked §2.3.
- 2026-11-19 (lane preddoc4): this piece owns the facts on `0` and a bare condition in a hole; core/conditions/match-so-far points here; the parentheses bullet (a spelling call) is core/spellings/condition-parentheses's (review r59 RULING-8).

## core/holes/bare-condition/labels — Labels a bare condition reads
slugs: bare-condition-labels
rulings:
rejected:
readings:
- the surrounding rx's labels as they stand at the hole (the manager's reading 10; NOT his words) — PARTS from the place table's hole row ("inside X, X's own namespace"): an answer against a compile error (preddoc1 PART R10; sabotage s10 caught). A precedent for the manager's side: hit-carry's ruled witness `occurrences(/${c}(?<h>\d)/, min = 2)`, c := NOT (h: >= 5), read h from the surrounding literal. Asked, never picked.
evidence: preddoc1 PART R10.
history:
- 2026-11-19: listed by the manager in the "`0` inside an inserted part" entry ((a): "if the draft's rows part, ASK"); NEW owner question.

## core/holes/in-filter — A hole inside a filter operand
slugs: hole-in-filter
rulings:
- 2026-11-18 "hole-in-filter: I agree filter error. Also, your assessment that they are compatible if the holes are filled first is my understanding" (record: "2026-11-18 OWNER RULING — hole-in-filter: the filter error; fill the holes first")
rejected:
- the hole's assertion crosses the border inside a filter operand too — by owner ruling — hole-in-filter.
- the operand judged on a prefix of the stretch — by run — the rival holds on `1239` (preddoc1 sabotage xEX-in-filter caught).
readings:
evidence: preddoc1 EX-in-filter; PART HF of predspec261 (the reach classifier).
history:
- 2026-11-18: "the right side of `&`" was the manager's slip (record correction), read as "an `&` operand"; then hole-in-filter.

## core/holes/and-in-hole — An `&` inside a hole
slugs:
rulings:
- 2026-11-15 "so the match span that the & expression creates anchors for is the ${} hole. 999${/\d+/ & <100}999 matches 99945999" (record: "2026-11-15 RULINGS — a per-call hit name; no count warning; the hole is the scope an `&` in it anchors to")
- 2026-11-15 "That's a good clarification" (the sides of `&` "match the same stretch whole") (record: "2026-11-15 RULING — the sides of `&` "match the same stretch whole"; the word "anchored" is kept for the macro")
rejected:
- the sides judged on a prefix of the hole's text — by run — the rival holds on `999450999` (preddoc1 sabotage xEX-and-in-hole caught).
readings:
evidence: preddoc1 EX-and-in-hole (the record's acceptance row).
history:
- 2026-11-15: part (c) of the entry; the wording "match the same stretch whole" adopted the same evening (the word "anchored" kept for the macro and for `\A`/`\z`).

## core/holes/no-hole — Where a hole is not a hole
slugs:
rulings:
rejected:
readings:
- a backreference's name or number takes no hole: a compile error (the draft's, revision 25.1; RULE-AS-CODE row `backreference`, PART P P6 of predspec261) — UNTESTED (a refusal).
- inside `\Q..\E` the hole is not a hole (the draft's, revision 25.1) — SUPPORTED as PCRE's behaviour (preddoc1 EX-quoted: libpcre2 matches `a${x}b` literally; sabotage xEX-quoted caught).
evidence: preddoc1 EX-quoted.
history:
- revision 25.1: both rows; kept in R.1.0 since.

## core/operators/precedence — Precedence
slugs:
rulings:
- 2026-11-17 "sequence-precedence: binds tighter than & and |" (record: "2026-11-17 OWNER RULINGS — the rx module: sequence-precedence and sequence-operator")
- 2026-11-17 "so the two argument form of + is addition, and the single postfix version is 1 or more. if we're going there, lets just do it. + +? * *? ? ??" (record: "2026-11-17 OWNER RULING — quantifier operators")
rejected:
- `&` right-associative as a pipeline (`x & unpad & between(1, 12)`; the manager's 2026-11-14 lean) — by owner ruling — OWN-1 (record "2026-11-14 RULING — OWN-1, transforms are FILTER MODIFIERS"): a transform is a macro on its filter argument, `&` is pure and grouping-free.
- `|` tighter than the sequence operator (`x(?:1|2)`) — by owner ruling — sequence-precedence; run: `2` FAILS, `x2` HOLDS under it (preddoc3b EXprec; sabotage s12 caught).
- juxtaposition (`A B`) as the sequence operator — by owner ruling — "I don't think it would work in the grammar" (sequence-operator).
readings:
- levels 1, 3, 4, 5, 9, the statement end and the call/index rule (the draft's readings, rev 25.1, review r43 F) — UNTESTED (they decide parses; spellings review item 19).
- the parse rule for `+`/`*` binary or postfix (the manager's, "MINE" in the quantifier-operators entry) — UNTESTED.
evidence: preddoc3b EXprec.
history:
- 2026-11-14: OWN-1 replaced the right-associative lean. 2026-11-17: sequence-precedence, quantifier operators; the draft §5.4 THE ONE OPERATOR TABLE (rev 25.1) replaced the fragmentary statements (§2.2, R.1.14, §5.1, the entry extent).
- 2026-11-19 (lane preddoc3b): converted from `?`; a `reading` piece because the table as a whole is the draft's, its ruled rows pointing at their pieces.

## core/operators/bindings — Bindings and macros
slugs:
rulings:
- 2026-11-13 "Then macro binding is m(x) := /.../ & x" (record: "2026-11-13 evening: macro bindings `m(x) := …`")
- 2026-11-15 "Agree with mapping" (record: "2026-11-14 RULINGS on rev 3's contradictions"); the operand is never an argument; positional, keyword and by-name parameters; sections
- 2026-11-15 "1. start with & and then we'll see. 2. start no, 3. agree" (record: "2026-11-14 RULINGS on rev 3's contradictions"); sections start with `&`; no partial application
- 2026-11-15 "I'm liking your ideas" (record: "2026-11-14 RULINGS on rev 3's contradictions"); under its bold line "2026-11-15 RULING — the type picture"; a call is the macro applied to one record; the record is never a value
- 2026-11-15 "2. yes keep out of phase 1. I like the idea of types but they need more thinking." (record: "2026-11-14 RULINGS on rev 3's contradictions"); under its bold line "2026-11-15 RULINGS — answers to the four questions of review r8"
- 2026-11-14 "I agree with both excepting the spelling ... no alpha operators ... with, check, in ..." (record: "2026-11-14 RULINGS on docs/dev/lanes/predx_report.md §11")
- 2026-11-19 ""Inside an inserted part": for a condition bare, yes. like /${(0: digit)}/" (record: "2026-11-19 OWNER, on `0` inside an inserted part: a bare condition sees the surroundings; `A & (0: ..)` sees only A")
rejected:
- `p(x)` = `x & p` (application as a call, C20/C30) — by owner ruling — "Agree with mapping": application has one spelling, `x & f`.
- calling a pattern with conditions, `isodate(year: S)` — by owner ruling (the same entry): "write `isodate & (year: ...)`".
- typed parameters `m(x: T)` in the first build — by owner ruling — "keep out of phase 1"; the idea stays (parked/ideas/restricted-parameter).
- a macro in a hole is always the unapplied-macro error (`${(x: digit)}`; the draft §2.3, §5.1) — by owner ruling — a bare condition in a hole is legal.
- a hole read as a backreference to its first mention (`(\d),\1` for `pair(/\d/)`) — by run — `1,2` FAILS under it (preddoc3b EXpair; sabotage s13 caught).
readings:
- the nested-record error (`f((x = 1, y = 2))`) and a condition argument passing a macro (the draft's LEAN, §13 O45) — UNTESTED.
- `name = default` in a head, a `:` in a head an error (LEAN, review r10 CENSUS-4) — UNTESTED.
- macros expand per use, cost per use (the manager's, 2026-11-13) — UNTESTED.
evidence: preddoc3b EXpair.
history:
- 2026-11-13: macro bindings; 2026-11-14/15: the C20/C30/C33/C34 rulings, mapping by sections, the type picture; currying DEFERRED, not dropped (record "2026-11-15 CLARIFICATION — currying is DEFERRED from phase 1, not dropped").
- FINDING for the manager (rule 5): the draft §5.3's `capture(x) := /(?<${x.label}>${x})/`, `each`, `each_group`, `where_group` are structural macros with no piece; `capture` is a BODY in the core language (a library piece), the others compile-time tools.
- 2026-11-19 (lane preddoc3b): converted from `?`; the statements part split off as core/operators/statements (a different status).
- 2026-11-19 (lane preddoc4): `NOT` named as the one exception to no-alphabetic-operators; the record bullet points at tuples (review r59 NEGATION, READ-15).

## core/operators/statements — Program shape and statements
slugs:
rulings:
- 2026-11-13 "If a symbol is undeclared it must be an rx label. If a symbol is bound := it becomes that binding. Warn (or error) on hiding label. $x is always label. There is no other way to introduce a label" (record: "2026-11-12 (later): owner discussion, informal, before the formal start (Frank: "continue the discussion now but not begin formally until the current threads are run out")")
rejected:
- reserved scope labels `$&`, `$_` (rev 9) — by review r10 CENSUS-8 — no stated meaning and no case (D77).
readings:
- `@` statements, the unused-pattern error, the bare-statement error (the manager's LEAN, CF:619) — UNTESTED (refusals).
- the closed built-in list and the two effect built-ins (LEAN, review r10 CENSUS-7) — UNTESTED.
- string option values (LEAN, review OWN-7) — UNTESTED.
evidence:
history:
- 2026-11-19 (lane preddoc3b): new piece, split from core/operators/bindings: the draft §5.1's program shape and statements hold rules no other tag homes, and their status (LEAN) differs from the bindings' (RULED).
- 2026-11-19 (lane preddoc4): `@options` (used by core/diagnostics/warnings' strictness setting) and the `assert` module's statements join the effect list; every call-form built-in has its library piece (review r59 COMPB-3, READ-11; the owner's direction of 2026-11-19, R-1).

## core/modules/map — A module is a map
slugs:
rulings:
- 2026-11-15 "3. this leans into the idea of an interface to a type over the type. Array and map are interfaces that can be applied to regex but interfaces aren't themselves values that can be created. So what import is is less important than that its interface is a map. 4. agree." (record: "2026-11-14 RULINGS on rev 3's contradictions"); under its bold line "2026-11-15 RULINGS — answers to the four questions of review r8"
rejected:
- a module as a third value kind, a namespace (the manager's 2026-11-14 lean (1)) — by owner ruling — the follow-up (MODULE = MAP) and "what import is is less important than that its interface is a map".
readings:
- members travel WITH THE TYPE (record "2026-11-14 — namespaces for type members", a LEAN) — UNTESTED; not contradicted by the 2026-11-19 rulings (they bind names into the bare space; dot lookup into a type is untouched).
- a module is never passed, stored, returned or used whole as a pattern (the draft §7's phase-1 lean) — UNTESTED.
evidence:
history:
- 2026-11-14: import/export as functions, its follow-up (module = map); 2026-11-15: the interface ruled; the draft §7 MODULES.
- 2026-11-19 (lane preddoc4): the base bullet "Members of a TYPE travel with the type" removed (a lean inside a ruled piece, and "type" against the one-type ruling; types, interfaces and members were cut from the first spec, Q8 of the 2026-11-14 predx entry); it stays a reading above (review r59 READ-12).

## core/modules/binding-list — The named binding list
slugs: import-symbols
rulings:
- 2026-11-19 "import-symbols: agree with all your statements including macro call. further, special form (=) := ... imports all symbols" (record: "2026-11-19 OWNER RULING — import-symbols: the named binding list, the shorthand in a macro call, `(=) :=` for all symbols")
- 2026-11-19 "it might also be (=left, =right) := ... which looks odd but is a degenerate form of macro parameter binding" (record: "2026-11-19 OWNER, discussing import-symbols: the double name, the binding form, `(=left, =right)`"); the idea he then ruled
rejected:
- `(left,right) := import("blah", /left|right/)` (his first instinct) — by owner ruling — "double name is a weakness".
- `(left, right) := import("blah")`, selection by bare name (the manager's leaning) — by owner ruling — "it has implications for the rest of the language"; bare `(a, b)` stays for a positional form (core/modules/positional).
readings:
- the eight statements he agreed to are the manager's list, "no wider" — SUPPORTED by the record entry.
evidence:
history:
- 2026-11-19: his aside after the pilot, the discussion, his lean "don't confirm yet", the manager's implications (a)-(f), the ruling.

## core/modules/call-shorthand — The shorthand in a call
slugs:
rulings:
- 2026-11-19 "import-symbols: agree with all your statements including macro call." (record: "2026-11-19 OWNER RULING — import-symbols: the named binding list, the shorthand in a macro call, `(=) :=` for all symbols"); statement 6, `f(=x)` means `f(x = x)`
rejected:
readings:
evidence:
history:
- 2026-11-19: the manager's implication (e), agreed.

## core/modules/all-symbols — All symbols
slugs:
rulings:
- 2026-11-19 "further, special form (=) := ... imports all symbols" (record: "2026-11-19 OWNER RULING — import-symbols: the named binding list, the shorthand in a macro call, `(=) :=` for all symbols")
- 2026-11-19 "import-symbol: bare "=" must be first but one can override names after (=,l = left) := ... to handle conflicts" (record: "2026-11-19 OWNER RULING — import-symbols, addition: the bare `=` is first; names after it override")
rejected:
readings:
- an entry after `=` REPLACES the member's default binding (the manager's, told to him) — UNTESTED.
- a bare `=` not first is a compile error (the manager's) — UNTESTED.
- "all symbols" = the public members (the manager's) — UNTESTED.
- a later library name can start a warning in a `(=)` program; the 2026-11-14 lean accepts that shape ("a later library member of the same name breaks the build, never silently rebinds") — UNTESTED.
- the default set is `(=) := import(<the default module>)` (the manager's) — see core/modules/default-set.
evidence:
history:
- 2026-11-19: the ruling's addition, then the addition on `=` first.

## core/modules/leave-out — Leaving a member out
slugs:
rulings:
- 2026-11-19 "import-symbol: yes, that correction is good" (record: "2026-11-19 OWNER RULING — import-symbols: a member is left out with `(=, _ = left)`")
- 2026-11-19 "left could be bound later" (record: "2026-11-19 OWNER, import-symbols: leaving a member out")
rejected:
- `(=,left=)` (his first candidate) and `(=, left=_)` (his second) — by owner ruling — the correction: both put the member on the left, against the ruled direction; read by it `left = _` binds a new name `left` to a member `_`.
readings:
- `_` matches the part label `[_ = A]`, where `_` stands on the left too (the manager's) — UNTESTED.
evidence:
history:
- 2026-11-19: his lean with two spellings, the manager's flagged inconsistency, the correction accepted.

## core/modules/conflicts — Conflicts between files
slugs:
rulings:
- 2026-11-19 "import-symbol: (=) := import("pcrec"|"numbers"). conflicts are a compiler error, import separately." (record: "2026-11-19 OWNER, import-symbols: several modules in one import; a conflict is a compile error")
rejected:
readings:
- the same error in the one-name form (the manager's extension, NOT his words) — UNTESTED.
- `pcrec` and `numbers` as module names are his examples, not rulings.
evidence:
history:
- 2026-11-19: it met the 2026-11-14 "exactly one file", settled by import-several (lib/builtin/import).

## core/modules/default-set — The default-imported set
slugs:
rulings:
- 2026-11-19 "import-symbols: agree with all your statements including macro call." (record: "2026-11-19 OWNER RULING — import-symbols: the named binding list, the shorthand in a macro call, `(=) :=` for all symbols"); statement 5, the set is an ordinary implicit line of the form
rejected:
readings:
- "there can be a special imported by default set which includes peek()" (record "2026-11-19 OWNER, after reading the pilot documents", item 2) is a LEAN, not asked: so the piece is a `reading`.
evidence:
history:
- 2026-11-19: his lean after the pilot; statement 5 of import-symbols.

## core/modules/default-set/members — Which names are in the default set
slugs: default-set
rulings:
rejected:
readings:
- `peek` only, today, by his words (the doc-shape entry's item 2) — the rest NOT STATED.
evidence:
history:
- 2026-11-19: queued by the manager as **default-set**, not asked (the doc-shape entry).

## core/modules/positional — A positional binding
slugs: tuple-parts
rulings:
- 2026-11-16 "Yes" (record: "2026-11-16 OWNER CONFIRMATION — a tuple on the left of a binding takes it apart"); a confirmation REOPENED the same morning, see the next item
- 2026-11-16 "Nothing is set in stone. I'd like to hear it out. So It's the set that makes it an item so you can't break it apart without changing its meaning. Like 9:30, 10:00 broken apart is 9,10 and 30, 00 which is gibberish. Makes sense" (record: "2026-11-16 OWNER — reaching a tuple's parts is REOPENED; he wants the "use it whole" case heard")
rejected:
- "a bare positional `(a, b) := X` is left undefined ... the language does not clearly have an ordered right side" (the manager, told to the owner under import-symbols) — by the record — tuples exist; the question is open, not undefined (record: "2026-11-19 MANAGER — a statement told to the owner under import-symbols is WITHDRAWN (the positional binding list)")
- "a positional list takes a tuple apart: confirmed" (the manager's withdrawal entry) — by review r59 — it missed the reopening eight minutes after the confirmation (record: "2026-11-19 MANAGER — the withdrawal above is itself CORRECTED: taking a tuple apart is OPEN (tuple-parts), not confirmed; and a slip in the padded body")
readings:
- his "agree with all your statements" under import-symbols neither closed nor reopened tuple-parts (he was shown a false premise) — UNTESTED (the manager's reading, told to him)
evidence:
history:
- `(x, y) := rx ~ /.../` kept in the design (the type picture); a tuple taken apart confirmed, then reopened; the lean in the frozen draft: (B1) on record, (A) in practice, asked again when a use appears.

## core/modules/export — Export
slugs:
rulings:
rejected:
- `export([leap])`, an array of names (`[leap, weekday]` is `leap | weekday`, names lost) — by the manager's 2026-11-14 analysis, (3).
- `export(leap, weekday)` receiving names (a macro seeing argument expressions) — by the manager's 2026-11-14 analysis ("a meta feature; avoid").
readings:
- `@export(names)` and the no-export error (the manager's lean on his `export(["leap", !startsWith("_")])`; the draft §7, LEAN; "Export choice PENDING Frank", never answered) — UNTESTED.
- what `.` reaches is decided by the public/private rule (import-symbols statement 3, RULED; export-rule) — SUPPORTED by the record.
evidence:
history:
- 2026-11-14: import/export as functions (options (a)-(c), lean (b): every top-level binding exported unless `_`), its follow-up (lean `@export(names)`); 2026-11-18: export-rule (labels); 2026-11-19: statement 3.

## core/modules/standard-library — The standard library
slugs:
rulings:
rejected:
readings:
- his words: "categories of things that will be popular to users like dates and IP addresses, emails, etc. that's where the library comes in" (record: "2026-11-12 (later): owner discussion, informal, before the formal start", the bullet THE STANDARD LIBRARY) — a direction in an informal discussion, so the piece is a reading; "a FOLLOW-UP initiative after the base (content, not mechanism)" is the record's account.
- blessed callouts: the record's "2026-11-14 — a standard library of blessed callouts (Frank)" (lean ADOPT as a later component; plan row [BLESSED-CALLOUTS]) — a lean.
- the four names the worked examples call (`days`, `weekday_of`, `days_in`, `luhn`) as planned content: the draft calls them library names and binds none (review r59 COMPB-9) — the lane's reading.
evidence:
history:
- 2026-11-19 (lane preddoc4): a new piece (review r59 COMPB-4); library.md's header points here (COMPB-9).

## core/modules/naming — Names of provided transforms
slugs:
rulings:
- 2026-11-15 "We should consider this in the naming of formal transforms that we provide." (record: "2026-11-14 RULINGS on rev 3's contradictions"); under its bold line "2026-11-15 RULING — ONE anchoring rule, `anchored()`, and the naming of provided transforms"
- 2026-11-14 "Docs should be clear the transform is transforming the filter" (record: "2026-11-14 RULING — OWN-1, transforms are FILTER MODIFIERS")
- 2026-11-15 "1 occurances." (record: "2026-11-15 RULING — the provided transform `search` is renamed `occurrences`")
rejected:
- `unpad` (it "sounds like it strips away 0 padding from integers but really it changed a filter to accept them", his words in the anchoring entry) — by owner ruling — renamed `padded`.
- `search` — by owner ruling — renamed `occurrences`.
readings:
- the rule's statement as a NAMING RULE over every provided transform: his "We should consider this in the naming of formal transforms" accepted with the anchoring advice ("Ok I agree"); the base's "never `trim`" is from OWN-1's words ("Trim or unpad imply they are doing something to the subject").
evidence:
history:
- 2026-11-19 (lane preddoc4): a new piece (review r59 COMPB-4).

## core/diagnostics/errors — Compile errors
slugs:
rulings:
- 2026-11-17 "polarity-rule: warning for both. Warnings are errors given some strictness setting eg @config.strict()" (record: "2026-11-17 OWNER RULING — polarity-rule"); a never-passing test is no longer an error
- 2026-11-17 "Agree with all three." (record: "2026-11-17 OWNER RULING — the three remaining error-or-warning candidates"); label-twice stays an error, min-values none
rejected:
- the empty-ENTRY error (`["", "M"]`) — by owner ruling — "2026-11-14 RULING — the empty-match hazard": it rejected legitimate optional parts and missed `/\d*/`.
- the empty-search ERROR in predicate programs — by owner ruling — empty-search-error: a warning (`pcrec.empty.search`).
- the error for a never-passing test, and for a test on an unsettable label (REV 21, a manager disposition) — by owner ruling — polarity-rule: a warning (`pcrec.test.never`).
- `$x & S` an error (dollar-condition) — by owner ruling — match-is-rx, then dollar-diagnostic: legal, with a warning.
- `min = n` an error for n other than 0 or 1 — by owner ruling — the three remaining candidates.
readings:
- the table is the manager's index of the errors each piece rules or reads (the draft §R.2, §5.1, §7, §R.6) — UNTESTED (refusals; no regex model).
- the recursion limit (one integer literal parameter strictly decreasing) — the draft's LEAN, no piece — UNTESTED.
evidence:
history:
- 2026-11-14 to 2026-11-19: errors moved to warnings one by one (empty-match hazard, polarity-rule, empty-search-error, dollar-condition); the edge-assertion error's reach ruled (operand-context) and taken off holes.
- 2026-11-19 (lane preddoc3b): converted from `?`; a `reading` piece because the index as a whole is the manager's.

## core/diagnostics/under-construction — The under-construction error
slugs: under-construction-class
rulings:
rejected:
readings:
- the error keeps its own class, worded as under construction (THE MANAGER'S CALL, answer-free, told to him, "closed unless he objects") — UNTESTED (wording).
evidence:
history: skeleton; record "2026-11-18 OWNER RULING — construction-line: enumerate" (the call).

## core/diagnostics/warnings — Warnings
slugs:
rulings:
- 2026-11-14 "I agree but warnings need names and the user must be able to disable them (wildcard?)" (record: "2026-11-14 RULING — the empty-match hazard")
- 2026-11-14 "use an rx instead of wild card purely for consistency" (record: "2026-11-14 RULING — the empty-match hazard"); its amendment: a selector is a set of names as an rx
- 2026-11-17 "What are all the warning items? Warnings should be structural or definable by a library option." (record: "2026-11-17 OWNER — a principle for warnings")
- 2026-11-17 "Warnings: yes, that is my definition of structural and these warnings are good. Naming: library warnings/errors should be id'd by the library path" (record: "2026-11-17 OWNER RULING — warnings: the list accepted; library warnings are named by the library path")
- 2026-11-17 "2. compiler errors and warnings are prefixed with "pcrec."" (record: "2026-11-17 OWNER RULING — warnings: the list accepted; library warnings are named by the library path"); the ADDENDUM
- 2026-11-17 "polarity-rule: warning for both. Warnings are errors given some strictness setting eg @config.strict()" (record: "2026-11-17 OWNER RULING — polarity-rule")
- 2026-11-17 "empty-search-error: warning" (record: "2026-11-17 OWNER RULING — empty-search-error: a warning")
- 2026-11-17 "Agree. Good warning" (record: "2026-11-17 OWNER — the numbered-label warning accepted")
rejected:
- a `*` wildcard in a selector — by owner ruling — the amendment: `"*"` is the literal name and draws `warn.unused`.
- `compare.width` as a compiler warning — by owner ruling — the list accepted: it is about one library form, so the compare library names it (`compare.width.variable_width`).
- a looped-label warning of its own (the manager's proposal) — by the manager, recorded in the principle's entry: it is `label.unset` under the one label rule; the two triggers are not the same set (the draft R.2, rev 25's PART W).
- `transform.noop` (the 2026-11-14 list) — by the draft (§7.1, after OWN-1 made a transform a macro on its filter): a transform without its argument is the unapplied-macro error (core/operators/bindings).
readings:
- every name is the manager's placeholder (the draft §7.1; his `no-fail` an example) — SUPPORTED by the record ("the names ... to the spellings review").
- `match.never` (an inserted pattern's edge that can never hold; a product with every copy removed) and the `[^${c}]` -> join warning are the draft's, not in the accepted list — UNTESTED.
- the arithmetic warning's one trigger (a result known to be nothing, a member list only when every member's is) is the manager's call — UNTESTED.
- the binding-hides-label warning is the owner's 2026-11-13 "Warn (or error) on hiding label", read as a warning — UNTESTED.
- his observation that a selector can catch a compiler warning and a library's of the same last component ("helpful or dangerous") is NOT ruled.
evidence:
history:
- 2026-11-14: names in dotted families, `@warn.off`; 2026-11-17: the principle, the list, the library path, the `pcrec.` prefix, polarity-rule, empty-search-error, numbered-label; 2026-11-19: dollar-diagnostic, plus-operands.
- 2026-11-19 (lane preddoc3b): converted from `?`; three controls of one fact (`@warn.off`, `@warn.error`, `@options.strict`) stay an idea (parked/ideas/severity-table).

## core/diagnostics/dollar-form — The `$x & S` warning
slugs: dollar-warning dollar-diagnostic
rulings:
- 2026-11-19 "i don't want to spend too much time on the warning. the form $x & .. should just get a warning" (record: "2026-11-19 OWNER RULING — dollar-diagnostic")
rejected:
- the form an ERROR (dollar-condition, 2026-11-17) — by owner ruling — match-is-rx made it legal; dollar-diagnostic gave it a warning.
- no dedicated warning, the emptiness diagnostics with "a read stands for its group's rx" (the manager's, rev 28) — by owner ruling — dollar-diagnostic ("should just get a warning").
readings:
evidence: PART DD of predspec291.
history: skeleton; the hint printed only where it is a drop-in (THE MANAGER'S CALL, review r54 P29-12).

## core/diagnostics/nullable-hit — A nullable hit argument
slugs:
rulings:
- 2026-11-18 "hit-carry: warning on nullable" (record: "2026-11-18 OWNER RULING — nullable argument: a warning")
rejected:
readings:
evidence:
history: skeleton.


## core/diagnostics/consuming-test — A consuming test
slugs: when-peek
rulings:
- 2026-11-18 "When peek: warn. A test pattern does consume and warns that it is." (record: "2026-11-18 OWNER RULING — when-peek: a bare pattern as the test CONSUMES, with a warning; `peek()` makes it a peek")
rejected:
- enforced (a bare pattern test a compile error) — by owner ruling — when-peek ("warn"; the manager had leaned enforced).
- automatic (a bare pattern silently peeked) — by owner ruling — when-peek (a bare pattern "does consume").
readings:
- the warning is the COMPILER's, a `pcrec.` name not yet chosen (the draft R.1.10 (5)(a), spellings 24): a body cannot know that an argument is a bare pattern — NOT RUNNABLE (a diagnostic).
- a condition or a peek as the test draws no warning (the manager's reading stated back with when-peek) — NOT RUNNABLE.
evidence: the draft R.1.10 (4); preddoc2 PART WT (the consumed form itself).
history:
- 2026-11-19 (lane preddoc2): split from the old core/conditional/test when `when`, its test and `peek` moved to the library: the warning is the one part of when-peek a body does not produce, so it stays a core diagnostic, beside core/diagnostics/nullable-hit (a warning on a library name's argument, kept in the core the same way).
## core/spellings/placeholders — Every placeholder spelling
slugs: atomic-spelling options-spelling conditional-spelling
rulings:
- 2026-11-17 "hits-text: yes but spelling to be reviewed with all other spellings." (record: "2026-11-17 OWNER RULING — the hit list: atomic and anchored")
rejected:
- juxtaposition as the sequence operator — by owner ruling — sequence-operator (core/operators/precedence).
- alphabetic operators and statement keywords (`with`, `check`, `in`, `as`) — by owner ruling — "2026-11-14 RULINGS on docs/dev/lanes/predx_report.md §11".
readings:
- every spelling a placeholder (D193 addendum 4, the owner's, 2026-11-10: "syntax is not settled") — SUPPORTED by the decision log; the ruling quoted is the record's own statement of it.
- the table's rows are the draft's R.8 list plus the import spellings of 2026-11-19 — UNTESTED.
evidence:
history:
- 2026-11-10: D193 add. 4; 2026-11-17: hits-text sends every spelling to one review; 2026-11-19 (lane preddoc3b): converted from `?`; the four slugs (atomic, options, conditional, every-pass) are rows of the table.
- 2026-11-19 (lane preddoc4): the slug every-pass-spelling moved to its open piece lib/counting/every-pass (review r59 PRIMITIVES-MISSING).

## core/spellings/condition-parentheses — A condition keeps its parentheses
slugs:
rulings:
rejected:
readings:
- the condition keeps its parentheses everywhere, in a hole too; `A & 0: digit` and `${0: digit}` stay the draft's error with their meaning acknowledged (THE MANAGER'S CALL, record "2026-11-19 OWNER, on a condition without its parentheses") — UNTESTED (a spelling).
evidence:
history: skeleton; his remarks "i believe that ${} implies (?:${})", "parenthesis are better because you can't add more to the chain", "maybe thats the same." (an OBSERVATION; the `0` case run: preddoc1 PART R12).
