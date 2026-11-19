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
- 2026-11-18 "In general, I did not anticipate these ideas and took the conservative route that eg repeat took a single decimal." (record: "2026-11-18 OWNER on value-is-pattern: one ruling, two leans, one idea")
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
- 2026-11-19 padded-order "i agree with your lean", the lean naming "the body's stated behaviour, not an error" (record: "2026-11-19 OWNER RULING — padded-order")
rejected:
- an error for a shorter string listed before a longer one — by owner ruling — padded-order.
readings:
evidence: lib/modifiers/padded's details; PART PO of predspec291.
history:
- 2026-11-19: the phrase was the manager's (padded-order's lean); the owner used it himself in padded-lazy-sparse ("stated behavior"). The census found no owner quote only because it searched the British spelling.

## core/principles/nothing-outside-domain — Nothing, not an error
slugs:
rulings:
- 2026-11-19 "number-edge: nothing" (record: "2026-11-19 OWNER RULING — number-edges")
- 2026-11-19 "literal "a" + "b" is an error because there is no compatible type defined and they are not in the default type (if that works). for now, as you say, we are restricting arithmetic to digits and anything else is nothing (for runtime compatibility) and a warning if known" (record: "2026-11-19 OWNER RULING — plus-operands")
rejected:
readings:
evidence: PARTS NE, PL of predspec291.
history:
- 2026-11-18/19: number-domain's "does not fit yields nothing", then number-edges and plus-operands; his first plus-operands sentence is a later direction (operand types), not in force.

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

## core/principles/exact-wording — Exact wording
slugs:
rulings:
- 2026-11-19 (class: a remark on the manager's method) "zero-in-sequence: you are a lawyer in your exact wording. this is what is needed now." (record: "2026-11-19 OWNER RULING — zero-in-sequence")
rejected:
readings:
evidence:
history:
- 2026-11-19: a remark on the manager's method; "no change asked" (the record).

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
slugs: pass-and joint-last-pass empty-pass outer-pass-forms
rulings:
rejected:
readings:
evidence:
history: not converted; the draft §R.1 head and R.1.1.

## core/model/modes — The three modes
slugs: whole-text atomic-search empty-search-error caller-ambiguous
rulings:
rejected:
readings:
evidence:
history: not converted; the draft R.1.1, R.1.11, §R.5.

## core/model/table — The table of paths and its order
slugs: pass-table group-truth hit-list value-point
rulings:
rejected:
readings:
evidence:
history: not converted; the draft R.1.2.

## core/model/places — The place table
slugs: nested-pass
rulings:
rejected:
readings:
evidence:
history: not converted; the draft R.1.0 (the place table). `predicates_future.md` items 16 and 22 are this piece (in the documents, not parked).

## core/patterns/literals — Literals and regex text
slugs:
rulings:
rejected:
readings:
evidence:
history: not converted; the draft §11.

## core/patterns/flags — Flags in a literal
slugs:
rulings:
rejected:
readings:
evidence:
history: not converted; the draft §11 and R.1.15; flags at a hole are core/holes/flags.

## core/patterns/sequence — The sequence operator
slugs: sequence-operator sequence-precedence sequence-reading rx-module
rulings:
- 2026-11-17 "sequence-reading: splice." (record: "2026-11-17 OWNER RULING — sequence-reading: splice; and the hole reopened")
- 2026-11-17 "sequence-precedence: binds tighter than & and | / sequence-operator: is there a reason why not? I expect rx construction and concatenation is common enough there." (record: "2026-11-17 OWNER RULINGS — the rx module: sequence-precedence and sequence-operator")
rejected:
readings:
evidence: PART RX of predspec25.
history: skeleton; the draft R.1.14. `predicates_future.md` item 21 (the rx module) is this section's (in the language, not parked).

## core/patterns/alternation — Alternation
slugs:
rulings:
rejected:
readings:
evidence:
history: not converted; the draft R.1.4.

## core/patterns/quantifiers — Postfix quantifier operators
slugs:
rulings:
- 2026-11-17 "lets include the possessive forms but the brace counts are repeat. "did you mean A+ followed by B" A B isn't legal so its the addition form." (record: "2026-11-17 OWNER RULING — quantifier operators")
rejected:
readings:
evidence: PARTS RX7-RX9 of predspec25.
history: skeleton; the draft R.1.14 (THE POSTFIX QUANTIFIER OPERATORS).

## core/patterns/atomic — Atomic parts
slugs:
rulings:
rejected:
readings:
evidence:
history: not converted; the draft R.1.4; its spelling is parked/ideas/atomic.

## core/patterns/lookaround — Lookaround
slugs: lookahead-labels
rulings:
- 2026-11-18 "lookahead-labels: agree" (record: "2026-11-18 OWNER RULING — lookahead-labels: visible, as in PCRE")
rejected:
readings:
evidence: PART LA of predspec26.
history: skeleton; the draft R.1.0 lookaround row.

## core/labels/labels-vs-captures — Labels and captures
slugs: pass-own-labels
rulings:
- 2026-11-17 the entry "labels match every pass, captures match the last" (record: "2026-11-17 OWNER RULING — labels match every pass, captures match the last")
rejected:
readings:
evidence:
history: skeleton; the draft R.1.7; his words not yet copied here (to be converted).

## core/labels/one-rule — One label rule: branchings reset
slugs: bare-loop-label before-and-inside array-slot shared-label repeated-means unsettable-label
rulings:
rejected:
readings:
evidence:
history: not converted; the draft R.1.7.

## core/labels/flow — Labels across composed parts
slugs: label-flow label-mark
rulings:
- 2026-11-17 "a. yes. a label from an rx is whatever label is surfaced by that rx. b. thats a good point but list here is one rx so exposes one h. i adjust my rules to be such that a compose and a literal rx have the same label behavior" (record: "2026-11-17 OWNER RULING — label-flow")
rejected:
readings:
evidence:
history: skeleton; the draft R.1.13.

## core/labels/export — Export and private labels
slugs: export-rule export-scope free-name
rulings:
- 2026-11-18 "export-rule: Agee and add [_a = A] is a private reference that wouldn't export at all" (record: "2026-11-18 OWNER RULING — export-rule: public unless `_`; a binding shows its own public labels and its public part labels")
rejected:
readings:
evidence: PARTS TA, TB of predspec291.
history: skeleton; the draft R.1.13 (EXPORT AND VISIBILITY).

## core/labels/paths — Part labels and paths
slugs: path-and-ambiguity
rulings:
rejected:
readings:
evidence:
history: not converted; the draft R.1.0 PART LABEL row, R.1.13.

## core/labels/backreferences — Backreferences
slugs: backref-label backref-across-parts same-name-twice
rulings:
- 2026-11-18 "backref-label: capture" (record: "2026-11-18 OWNER RULING — backref-label: capture")
- 2026-11-18 "same-name-twice: i agree with your lean." (record: "2026-11-18 OWNER RULING — same-name-twice: an error at the backreference unless `(?J)`")
rejected:
readings:
evidence:
history: skeleton; the draft R.1.13, R.1.15.

## core/labels/numbers — Numbers name groups only without ambiguity
slugs: number-names zero-place numbered-label-warning
rulings:
- 2026-11-18 "number-names: exactly. Only when there is no ambiguity." (record: "2026-11-18 OWNER RULING — number-names")
- 2026-11-18 "number-names: the exception to our rule is 0. It is always the entire match of the rx however it is composed." (record: "2026-11-18 OWNER RULING, addendum to number-names — zero is the exception")
rejected:
readings:
evidence: PART N of predspec26.
history: skeleton; the draft R.1.13 (NUMBERS).

## core/conditions/form — The condition form
slugs: condition-not condition-or dollar-condition label-twice-warn
rulings:
rejected:
readings:
evidence:
history: not converted; the draft §4.1, R.1.4.

## core/conditions/two-valued — Conditions are two-valued
slugs: three-valued polarity-rule record-under-not
rulings:
rejected:
readings:
evidence:
history: not converted; the draft R.1.5, §R.3.

## core/conditions/in-sequence — A condition as a sequence operand
slugs: condition-in-sequence
rulings:
- 2026-11-18 "condition-in-sequence: yes and it's probably more natural than & but allow both." (record: "2026-11-18 OWNER RULING — condition-in-sequence: yes, and `&` stays")
rejected:
readings:
evidence: PART CS of predspec26 and predspec261.
history: skeleton; the draft R.1.14 (A CONDITION IN SEQUENCE).

## core/conditions/quantified — A quantifier on a condition
slugs: quantified-condition condition-group
rulings:
- 2026-11-18 "quantified-condition: an error. This is a formal punt because we may find a better meaning for it in the future and this keeps that from breaking current code" (record: "2026-11-18 OWNER RULING — quantified-condition: an error, as a formal punt")
rejected:
- regex's meaning with a warning (the manager's leaning) — by owner ruling — the formal punt.
readings:
evidence: PART CS CS4 of predspec26.
history: skeleton; condition-group (a group holding only conditions) is open in the draft §R.8.

## core/conditions/match-so-far — The match so far
slugs: zero-in-sequence number-in-loop
rulings:
- 2026-11-19 "zero-in-sequence: you are a lawyer in your exact wording. this is what is needed now. the condition is always sees the regex composed at the point it is used. so the 0: is the match so far" (record: "2026-11-19 OWNER RULING — zero-in-sequence")
rejected:
- the error for now (the manager's leaning) — by owner ruling — zero-in-sequence.
readings:
- inside a loop the match so far includes the earlier passes (the manager's reading 9) — SUPPORTED by the callout model (preddoc1 PART R9: the match's start, not the pass's; the two differ on 4 / 16 / 28 of 364, first `3;3;`).
evidence: preddoc1 PARTS R8, R9; zeroseq.py (the record's run).
history: skeleton (one ruled statement); the draft's R.1.0 CONDITION row cell is answered by it (predspec291 report, sentence 3).

## core/conditions/pass-start-read — Labels as they stand
slugs: pass-start-read pass-list-read looped-warning
rulings:
- 2026-11-17 the entry pass-start-read (record: "2026-11-17 OWNER RULING — pass-start-read")
rejected:
readings:
evidence:
history: skeleton; the draft R.1.7; his words not yet copied here (to be converted).

## core/conditions/defaults — Defaults and absent labels
slugs: nullable-meaning
rulings:
rejected:
readings:
evidence:
history: not converted; the draft R.1.6, §4.2.

## core/filters/and — The `&` operator
slugs:
rulings:
rejected:
readings:
evidence:
history: not converted; the draft R.1.4, §2.2.

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
rejected:
readings:
evidence:
history: not converted; the draft §R.3, R.1.0 COMPLEMENT row.

## core/filters/kinds — Can match, can filter
slugs: complement-place lone-complement-match filter-captures
rulings:
- 2026-11-18 "That means for rx: There is rx that can match. There is rx that can filter. Neither is wholly a subset of the other" (record: "2026-11-18 OWNER RULING — complement-place: the error is at the USE; two kinds of rx")
rejected:
readings:
evidence: PART CX of predspec26.
history: skeleton; the draft R.1.0 head (THE TWO KINDS OF RX).

## core/values/reads — Reading a label
slugs: value-filter
rulings:
- 2026-11-18 "what i want is that $y works like label. however, there is a way to get the pcre capture value" (record: "2026-11-18 OWNER RULING — hole-reads-capture: the label; and a way to get the PCRE capture value")
rejected:
readings:
evidence:
history: skeleton; the draft R.1.15, R.1.16.

## core/values/one-type — One type: a match is an rx
slugs: match-is-rx read-is-constant value-is-pattern
rulings:
- 2026-11-18 "value-hole: let's use the unifying idea for it. Change my answers to match." (record: "2026-11-18 OWNER RULING — match-is-rx: the unifying idea; "Change my answers to match"")
rejected:
readings:
evidence:
history: skeleton; the draft R.1.16.

## core/values/number-domain — The number domain
slugs: number-domain domain-components numeral-width
rulings:
- 2026-11-18 "number-domain: canonical" (record: "2026-11-18 OWNER RULING — number-domain: canonical")
- 2026-11-18 "numeral-width: canonical" (record: "2026-11-18 OWNER RULING — numeral-width: canonical")
rejected:
readings:
evidence: PART NW of predspec28.
history: skeleton; the draft R.1.16 (THE NUMBER DOMAIN), R.1.15 (2).

## core/values/arithmetic — Arithmetic
slugs: plus-operands number-edges
rulings:
- 2026-11-19 "literal "a" + "b" is an error because there is no compatible type defined and they are not in the default type (if that works). for now, as you say, we are restricting arithmetic to digits and anything else is nothing (for runtime compatibility) and a warning if known" (record: "2026-11-19 OWNER RULING — plus-operands")
- 2026-11-19 "number-edge: nothing" (record: "2026-11-19 OWNER RULING — number-edges")
rejected:
- a TYPE ERROR for a non-number operand (the manager's lean) — by owner ruling — plus-operands.
readings:
evidence: PARTS PL, NE of predspec291.
history: skeleton; the draft R.1.14 (the `+` paragraph), R.1.16 NUMBER EDGES.

## core/values/functions — Single-value functions
slugs: construction-line
rulings:
- 2026-11-18 "construction-line: enumerate" (record: "2026-11-18 OWNER RULING — construction-line: enumerate")
rejected:
readings:
evidence:
history: skeleton; the draft R.1.16 T5.

## core/arrays/lift — Arrays are alternations; operations lift
slugs: array-lift lift-order
rulings:
- 2026-11-18 "array-lift: I meant, alternations as you suggested. It's consistent that alternations combine on the product and multiply the rx and produce more alternations" (record: "2026-11-18 OWNER RULING — array-lift: operations on arrays combine on the product")
rejected:
- pairwise as default — by owner ruling — his own first message, replaced at once by him.
readings:
evidence: PART AL of predspec26.
history: skeleton; the draft R.1.14 (ARRAYS UNDER OPERATIONS).

## core/arrays/enumerate — Enumerate
slugs:
rulings:
rejected:
readings:
evidence:
history: not converted; the draft §5.5.

## core/arrays/class-order — The order of a class's results
slugs: class-order
rulings:
- 2026-11-19 "class-order: longest" (record: "2026-11-19 OWNER RULING — class-order")
rejected:
- codepoint order (the draft's lean, §5.5) — by owner ruling — class-order.
readings:
evidence: PART CO of predspec291.
history: skeleton.

## core/arrays/class-positions — Two class positions in one lift
slugs: class-positions
rulings:
rejected:
readings:
evidence: PART CO of predspec291 (P29-9).
history: open; the draft §R.8.

## core/arrays/class-index — The order of a class in enumerate
slugs: class-index
rulings:
rejected:
readings:
evidence: PART CO of predspec291 (P29-10).
history: open; the draft §R.8.

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

## core/holes/flags — Flags at a hole
slugs: hole-flags flags-propagate flags-scope flags-in-filter
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
- flags-in-filter: the two sides of an `&` inside a hole start with the hole's flags (THE DRAFT'S READING REACH, 0 / 0 / 0 of 1,555 against the plain hole) — open in the draft §R.8; not converted here.
- the `r` and `a`-family flags inherited (the draft's reading, P29-2) — UNTESTED here (PART FA of predspec291).
evidence: preddoc1 EX-flags, EX-flags-written, EX-flags-U; PARTS FF, FA, TX, SQ of predspec291; PART FL of predspec28.
history:
- 2026-11-18: hole-flags and flags-propagate reversed the draft's NO INHERITED FLAGS (§11, §13 O32).
- 2026-11-19: flags-scope (`U` moved out); the r54 round made "parsed alone" the model (revision 29.1).

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
rejected:
readings:
evidence:
history: not converted; the draft §5.4 (THE ONE OPERATOR TABLE).

## core/operators/bindings — Bindings and macros
slugs:
rulings:
rejected:
readings:
evidence:
history: not converted; the draft §5.1-§5.3.

## core/diagnostics/errors — Compile errors
slugs:
rulings:
rejected:
readings:
evidence:
history: not converted; the draft §R.2, §7.

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
rejected:
readings:
evidence:
history: not converted; the draft §7.1. Ideas: parked/ideas/known-nothing, parked/ideas/warning-rows.

## core/diagnostics/dollar-form — The `$x & S` warning
slugs: dollar-warning dollar-diagnostic
rulings:
- 2026-11-19 "i don't want to spend too much time on the warning. the form $x & .. should just get a warning" (record: "2026-11-19 OWNER RULING — dollar-diagnostic")
rejected:
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
slugs: atomic-spelling options-spelling conditional-spelling every-pass-spelling
rulings:
rejected:
readings:
evidence:
history: not converted; the draft §R.8 spellings list (D193 addendum 4: spellings are placeholders).

## core/spellings/condition-parentheses — A condition keeps its parentheses
slugs:
rulings:
rejected:
readings:
- the condition keeps its parentheses everywhere, in a hole too; `A & 0: digit` and `${0: digit}` stay the draft's error with their meaning acknowledged (THE MANAGER'S CALL, record "2026-11-19 OWNER, on a condition without its parentheses") — UNTESTED (a spelling).
evidence:
history: skeleton; his remarks "i believe that ${} implies (?:${})", "parenthesis are better because you can't add more to the chain", "maybe thats the same." (an OBSERVATION; the `0` case run: preddoc1 PART R12).
