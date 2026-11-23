# The predicate language: details (core)

One entry per tag of `core.md`, in the same order: the question slugs asked about the piece, the owner's
rulings verbatim with their record entry, the candidates not taken and why, the readings with their state, the
evidence, and the history. The record is `docs/design/plan_row_bodies/COND-FAMILY.md` (the only source of
rulings); the frozen source of every skeleton piece is `docs/design/predicates_draft.md` revision 29.1 (cited "the
draft", by its section). Evidence directories are under `docs/dev/lanes/`; "PART X of predspecNN" is a block of
that lane's committed `predspecNN_model.out`. The pilot's own runs are `preddoc1_evidence/` (PART EX, R1-R12, LT).

shared: when-peek other-holes

## core/principles/regex-default — Regex behaviour wins
slugs: branch-scope branch-order sql-picture regex-settles
rulings:
- 2026-11-17 "Notably: this is a break from the SQL model we were using. A encapsulating where clause in sql does not cause the inner sql to reconsider. However, it is in line with regex behavior so I do like it and think it should be the general behavior" (record: "2026-11-17 OWNER, on the model after branch-scope")
- 2026-11-17 "regex-settles: yes settled" (record: "2026-11-17 OWNER RULINGS — regex-settles; absent-under-not")
- 2026-11-17 (class: DIRECTION) "Predicates: rather than I make arbitrary decisions on various choices that have difficult to predict ramification, can we come up with a regex model for each and use that to explain it. At least, where it is able to" (record: "2026-11-17 OWNER DIRECTION — decide the open choices by a REGEX MODEL where one exists")
- 2026-11-17 (class: OWNER, a qualification of the DIRECTION: the record's "access to ALL the hits of a search STAYS", a NOTED EXCEPTION) "That said, we are also attempting to make a useful language. In that way, being able to access all the hits of a search is helpful. It's an exception that should be noted but no excluded for purity" (record: "2026-11-17 OWNER — the regex model explains; it does not exclude useful features"); refines the direction above within the half hour: the model explains, it never drops a useful feature
rejected:
- the SQL picture (an enclosing condition does not make the inner pattern reconsider) — by owner ruling — "it is in line with regex behavior" (record above).
readings:
- the SQL picture survives if the table holds EVERY path in PCRE's order (the manager's framing, 11:50) — UNTESTED here (the draft R.1.2; lane pathimpact).
evidence: lanes pathimpact, rxmodel (the regex models of the open choices, 2026-11-17).
history:
- 2026-11-17: stated in the branch-scope discussion; the draft's §R heading "under regex behaviour" carries it since revision 24.
- 2026-11-19 (lane preddoc6, review r60 RULING-6): the `(class: OWNER)` item names the record's own words for what it is (OWNER is the heading's speaker, not a class word).

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
slugs: absent-rule absent-holds
rulings:
- 2026-11-16 (class: PRINCIPLE) "In my mind <100 is defined as the set of all positive integer strings less than 100. Absence is not part of that set" (record: "2026-11-16 OWNER PRINCIPLE — a set never contains absence")
- 2026-11-16 "absent-rule: lock" (record: "2026-11-16 OWNER RULING — absent-rule: LOCKED"); the absent rule rests on this principle (its item (4)); its clause offering the optional mark was removed by drop-mark (core/conditions/defaults)
rejected:
- absent-rule's clause (2), "over several values it holds when every value is in the set and there is at least one", for a bare condition after a loop — by owner ruling — last-pass-default, then after-loop-read: a bare condition reads the last pass's own label; "every value" is written on the item (the draft R.9, R.1.7).
- absent-rule's clause (3), the optional mark as one of the two author controls — by owner ruling — drop-mark (core/conditions/defaults).
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
- 2026-11-22 (class: POSITION) "Options m s really can't be inherited because they change semantics in confusing ways if you don't control them." (record: "2026-11-22 OWNER IDEA — program-scoped options: `@options()` setting flags (m, s, n, ...) for the literals of the bindings that follow"); his point 4, quoted in the principle as the ground of hole-flags part 3.
- 2026-11-22 "hole-flags: yes to all. What i like about the i weak behavior is that it's consistent to the other program level settings that only affect literals in program scope." (record: "2026-11-22 OWNER RULING — hole-flags: yes to all (weak values do not propagate; only an explicit `i` is inherited at a hole; `m` and `s` are no longer inherited)"); his reason, quoted in the principle (class: REASON).
rejected:
readings:
evidence: PART FF of predspec29 (flags-scope), PART TX of predspec291.; docs/dev/lanes/predspot_evidence/ predspot_model.py EXPLICIT, NOTINH, FLAGGRID (lane predspot).
history:
- 2026-11-19: the record classes it a DISCUSSION with a LEAN and "a PRINCIPLE stated"; "flag by flag" became flags-scope (core/holes/flags).
- 2026-11-22 (lane predspot, hole-flags folded; record "2026-11-22 OWNER RULING — hole-flags: yes to all (weak values do not propagate; only an explicit `i` is inherited at a hole; `m` and `s` are no longer inherited)"): principle 2026-11-19 re-dated 2026-11-22: his point 4 and his reason quoted; the sentence "Narrowed by hole-flags ..." added (the inheritance his second sentence states is now an explicit `i` only).
- 2026-11-23 (lane predfix84, review r84 C7, C8; record "2026-11-23 MANAGER — review r84 (predspot1122): the dispositions, ruled with the 2026-11-23 rulings in hand; no owner words"): the class of his point 4 corrected from OBSERVATION to POSITION (the record's word: "a POSITION on inheritance (4: ...)"); the base sentence "Narrowed by hole-flags (core/holes/flags): what an rx built up inside another inherits ..." now "As core/holes/flags rules it: ..." (the base carries no revision marks): his "so if one builds up an rx, they inherit the flags of the surrounding." is NARROWED by hole-flags' "yes to all" (2026-11-22) to an explicit `i`.

## core/principles/composed-at-point — Composed at the point of use
was: core/principles/exact-wording (2026-11-19, deleted, not moved: a remark on the manager's method in the same record entry, not a language principle (review r59 RULING-2); its tag is retired here because this entry quotes the one record entry it came from)
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
- 2026-11-19 (lane preddoc6, review r60 DAMAGE-2): the `was:` line's why now says the previous tag was DELETED, not moved (doc_format's DELETE form): the reader presented the deletion of "rules are stated exactly" as a rename into this principle.
- 2026-11-22 (lane predfix77, review r77 D2; record "2026-11-22 MANAGER — review r77 (predfold1121): dispositions ruled (no owner words)"): a scope note added (one definition: zero-in-definition and bare-nested-scope case 2, both ruled 2026-11-21); status date 2026-11-19 to 2026-11-21. Its quote unchanged. A "sealed definitions" principle (review r77 GENERAL-2) is PLAN: a principle needs his words.

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

## core/principles/label-names-spot — A label names a spot
slugs:
rulings:
- 2026-11-22 (class: PRINCIPLE) "The label is not to the regex abstractly, it's to the spot in the pattern where the regex is being inserted." and "It's not a piece of the pattern. It's a template of the rx that might be placed into the pattern." (record: "2026-11-22 OWNER RULING — argument-default: an error; and his reason: a label is to the SPOT in the pattern, a parameter is a template, not a piece of the pattern"); stated while "trying to articulate why" argument-default is an error; the name the manager's.
rejected:
readings:
evidence: docs/dev/lanes/predspot_evidence/ predspot_model.py ARGNAME, ARGLABEL, INPLACE.
history:
- 2026-11-22 (lane predspot, argument-default folded): a new principle piece, his two sentences quoted, the name the manager's.
- 2026-11-23 (lane predfix84, review r84 C8; record "2026-11-23 MANAGER — review r84 (predspot1122): the dispositions, ruled with the 2026-11-23 rulings in hand; no owner words"): the quote "It's not a piece of the pattern. ..." gains its antecedent, his sentence before it in the same ruling: "A parameter like rx in a call B(rx) cannot be labeled because it's not being placed into the pattern." ("It" is the parameter, not the label).

## core/model/match — What a match is
slugs: row-is-match condition-kind source-row searched-complement
rulings:
- 2026-11-17 "branch-scope: yes. I like that. Also, that makes me like 9:30 choice from yesterday more as well because if we have atomic, you can get the alternative I mentioned." (record: "2026-11-17 OWNER RULING — branch-scope: reading")
- 2026-11-17 "However, it is in line with regex behavior so I do like it and think it should be the general behavior" (record: "2026-11-17 OWNER, on the model after branch-scope")
- 2026-11-16 "row-is-match: yes I agree." (record: "2026-11-16 OWNER RULING — row-is-match")
- 2026-11-17 "regex-settles: yes settled" (record: "2026-11-17 OWNER RULINGS — regex-settles; absent-under-not")
- 2026-11-17 "Then from the perspective of the condition, an rx is a black box that exposes labels" (record: "2026-11-17 OWNER RULING — nested-pass: the outermost view")
- 2026-11-16 (class: ANSWER) "condition-kind: a pattern is a SQL statement. The table is the source of matches. Like the text for a pattern." (record: "2026-11-16 OWNER ANSWER, CORRECTED BY HIM — condition-kind"); it supersedes the wording of his first message (the record's entry before it, 20:36, condition-kind adjusted); his best guess on a complement is not a ruling
rejected:
- the SQL model, an enclosing condition that does not make the inner pattern reconsider — by owner — "this is a break from the SQL model we were using ... However, it is in line with regex behavior so I do like it" (record: "2026-11-17 OWNER, on the model after branch-scope").
- three-valued tests (an absent label UNKNOWN) — by owner ruling — regex-settles (1), a test on an absent label fails.
- "a row of the source is the whole subject; the complement is per subject" (source-row's wording, the manager's framing of the question his "Source-row: yes" answered, record "2026-11-16 OWNER RULINGS — drop-mark, default-value, source-row; default-scope to a lane") — by owner ruling — row-is-match SUPERSEDES it the same night: a row is ONE POTENTIAL MATCH, the subject the search text; it closes searched-complement (review r31 finding A: a per-subject complement contradicted the same-stretch tie, `/\d+/ & !/0+/` on `0 7` reports `7`).
readings:
- a loop's passes include PCRE's trailing empty pass (by the default of exception-rule; his observation "makes sense as the entire rx is optional", not a ruling) — SUPPORTED (the draft R.1.7 (4a): the literal loop, the hole loop and `occurrences` agree with libpcre2).
evidence: preddoc3a_model.py MATCH (the record's own example: WHOLE `123` a = `1`, b = `23`; the python `re` lowering `1\d+` gives the same spans in all three modes).
history:
- 2026-11-16: row-is-match; a row was a row of the pass table before it.
- 2026-11-19 (lane preddoc6, review r60 SOURCE-ROW / RECOUNT-4): the slugs source-row and searched-complement moved here from core/filters/complement: row-is-match, this piece's ruling, superseded source-row's wording and closed searched-complement (record "2026-11-16 OWNER RULING — row-is-match": "Review r31 finding A is closed by this ruling").
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
slugs: pass-table value-point
rulings:
rejected:
- the pass table as the meaning of a bare condition (pass-table) — by owner ruling — last-pass-default and after-loop-read; the group questions read the array of settings, not passes (core/labels/labels-vs-captures/array-vs-passes; re-pointed 2026-11-22, lane predfix77, review r77 FIXIND-1: the reason read before "a pass's own labels survive only inside the group questions (core/model/table/group-truth)").
readings:
- the table, its order and a row per labelling (the manager's restatement of branch-scope and row-is-match) — SUPPORTED (preddoc3a_model.py TABLE: the second branch is reached when the first one's label is rejected; the lowering `3\d|\d3` agrees).
- a label takes its value at its group's close, a condition placed after the group reads it (value-point, the manager's reading, closed by entailment) — SUPPORTED (pass-start-read's run, preddoc3a_model.py PSR).
- an atomic part takes its first row before an outside condition filters (regex-settles (5)) — SUPPORTED (preddoc3a_model.py ATOM).
- a filtered argument's hits are its own rows (hit-list; regex-settles (4), the one-pattern model) — UNTESTED here (lib/search/hits).
evidence: preddoc3a_model.py TABLE; the example is invented (no printed answer).
history:
- the draft R.1.2; the pass table was the model's centre before last-pass-default (2026-11-17).

## core/model/table/group-truth — Group questions over the array
slugs: group-truth
rulings:
rejected:
readings:
- (a) `NOT some(c)` = `occurs.none(c)` — SUPPORTED by the draft's E12 (0 / 0 / 0), not re-run here.
- (b) `occurs.none(NOT c)` differs from both (21 / 201 / 301 of 364, E12) — not re-run here.
- on the array (array-vs-passes (a)), c the condition `(d: "7")` written in place, on `/(?:(?<d>\d)?,)+/`, 364 texts over `17,`: `NOT some(c)` against `occurs.none(c)` 0 / 0 / 0 (one question by definition); against `occurs.none(NOT c)` 28 / 216 / 244; `occurs.none(NOT c)` on the array against on the passes 17 / 237 / 245; `NOT some(c)` on the array against on the passes 0 / 0 / 0 — SUPPORTED (predarr TRUTH; sabotage s10 caught). The manager's reading (d) "now part on settings, not passes" is NOT SUPPORTED as worded: `NOT some(c)` and `occurs.none(NOT c)` part under both readings; what moves is `occurs.none(NOT c)` itself.
- the proposal (the lane's): close the question as answered by array-vs-passes for a condition of one entry, the several-entry case asked as record-in-some and count-several — UNTESTED (a proposal; the choice is the owner's).
evidence: the draft §R.8 row group-truth / pass-table (E12); docs/dev/lanes/predarr_evidence/ TRUTH.
history:
- new piece (lane preddoc3a): the slug was on core/model/table, whose statement does not answer it; the draft keeps it asked ("the 11-18 rulings do not entail an answer").
- 2026-11-19 (lane preddoc6, review r60 COLD-20): the question restated as a choice: before, its candidates "(a) `NOT some(c)` = `occurs.none(c)`" and "(b) `occurs.none(NOT c)` is a different question" were both true at once; the reading (the draft §R.1.7, "Each remaining group question counts the REAL passes on which its condition is TRUE") is now candidate (a); lib/counting/some's sentence is marked as that reading.
- 2026-11-21 (lane predarr, array-vs-passes ruled): re-put over the array; the statement until then, verbatim: "After a loop, is the reading the definition: each group question counts the passes on which its condition is TRUE, each pass judged with its own labels, two-valued?"; the body's bullets "The reading: each pass judged with its own labels, two-valued; a condition before its group inside a pass reads the previous pass (core/conditions/pass-start-read), which does not reach the group questions: they judge the finished passes.", "Under the reading `NOT some(c)` and `occurs.none(c)` are one question (they agree on every text run), and `occurs.none(NOT c)`, "no pass on which c fails", is another (it holds with no pass; on a pass lacking c's label c fails and `NOT c` holds)." and "Candidates: (a) yes, the reading; (b) no: he names which of the three forms he meant to be one question." The heading "Group questions over the pass table" renamed. Status date 2026-11-19 to 2026-11-21, still open.
- 2026-11-22 (lane predfix77, review r77 D6 (RULING-5); record "2026-11-22 MANAGER — review r77 (predfold1121): dispositions ruled (no owner words)"): "The choice is the owner's or the manager's." became "The choice is the owner's.": nothing in force gives the manager the choice.
2026-11-22 (lane predbound, bound-condition ruled): in the readings item on the array, "c := `(d: \"7\")`" (notation for the condition) became "c the condition `(d: \"7\")` written in place": a condition bound alone is a compile error now; nothing re-run.

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
- 2026-11-22 (lane predfix77, review r77 D3; record "2026-11-22 MANAGER — review r77 (predfold1121): dispositions ruled (no owner words)"): the binding row's text column read "none of its own (X where `name` is used)"; it is now scoped to flags and matching, its reads its own (bare-nested-scope case 2). No answer moved.
- 2026-11-23 (lane predfix84, review r84 A2; record "2026-11-23 MANAGER — review r84 (predspot1122): the dispositions, ruled with the 2026-11-23 rulings in hand; no owner words"): the binding row's column until then: "for flags and matching, X where `name` is used; its reads are its own (core/holes/bare-condition/nested-scope)". Now for matching where used, for flags where WRITTEN plus an explicit `i` from the hole: under program options the two part (core/holes/flags/in-filter, the lines "Bound in a library" and "Written in the hole"; docs/dev/lanes/predfix84_evidence/ predfix84_model.py FILTER).

## core/model/places/outermost-view — The outermost view
slugs: nested-pass outer-pass-forms
rulings:
- 2026-11-17 "The view of the labels on an rx is the outermost view. To get inner views you nest the labels and condition" (record: "2026-11-17 OWNER RULING — nested-pass: the outermost view")
rejected:
- the innermost or per-inner-pass view for a bare condition — by owner ruling — nested-pass.
readings:
- pass tests on a label two loops deep range over the outermost loop's passes (outer-pass-forms; told, his confirmation "this is how i expected", not asked as a ruling) — REPLACED by array-vs-passes (a) (record: "2026-11-21 OWNER RULING — array-vs-passes: a"): the group questions and `h[k]` read the array of settings at every depth (the line "Two depths" in core/labels/labels-vs-captures/array-vs-passes: `h[2]` on `3;4;,5;,` is `4`, not the second outer pass's `5`). The bare-condition view (the ruling above) is untouched.
evidence: the draft R.1.7 (4b): `/(?:(?:(?<h>\d)?;)*,)*/ & (h: <5)` on `3;,,` and `3;;,` FAIL.
history:
- new piece (lane preddoc3a), split from core/model/places.
- 2026-11-21 (lane predarr, array-vs-passes ruled): the bullet "Pass tests (`some`, `occurs`, `h[k]`) on a label two loops deep range over the outermost loop's passes (a reading)." replaced by the array-of-settings bullet; the printed line (a bare condition) does not move.
- 2026-11-22 (lane predfix77, review r77 D2 (FIXIND-14); record "2026-11-22 MANAGER — review r77 (predfold1121): dispositions ruled (no owner words)"): status date 2026-11-17 to 2026-11-21 (its group-question bullet was rewritten by array-vs-passes, ruled 2026-11-21). Text unchanged.
## core/patterns/literals — Literals and regex text
slugs:
rulings:
- 2026-11-14 "I agree... I was mostly thinking about multi line predicate syntax" (record: "2026-11-14 RULINGS on predicates_draft.md §13"); its RULING C2, "an rx literal means exactly what PCRE means, NO implicit x-mode ...; extended mode is per literal", is REVISED in part by program-options (2026-11-22, lib/builtin/options): a file's program options (`m`, `s`, `n`, `x`, the weak `i`) are its literals' defaults, so a literal means what PCRE means under them (review r84 A3).
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
- 2026-11-22 (lane predfix82, review r82 DES-2; record "2026-11-22 MANAGER — review r82 (predfold1122): dispositions ruled; two corrections of record entries (no owner words)"): a bullet: a provided body also writes the label-only group (a reading). Status date 2026-11-14 to 2026-11-22.
- 2026-11-23 (lane predfix84, review r84 A3; record "2026-11-23 MANAGER — review r84 (predspot1122): the dispositions, ruled with the 2026-11-23 rulings in hand; no owner words"): statement until then: "An rx literal `/.../` is full PCRE and means exactly what PCRE means; the predicate language adds only two marks inside it, the hole `${` and, under its switch, the operator `&`." Now conditioned on the file's program options ("the language" for "the predicate language", the 200-character cap). The consequence, for the owner (review r84 A3): a library literal's meaning is no longer readable off the literal alone; its file's `@options` statement above it is part of it.

## core/patterns/flags — Flags in a literal
slugs: option-hole-explicit
rulings:
- 2026-11-14 "I agree... I was mostly thinking about multi line predicate syntax" (record: "2026-11-14 RULINGS on predicates_draft.md §13"); RULING C2 there, "NO implicit x-mode ...; extended mode is per literal", is REVISED in part by program-options (2026-11-22): under a file's `@options(x)` a literal is read in extended mode with nothing written in it (review r84 A3).
- 2026-11-18 "a hole takes the flags in force at the hole. each regex literal has its own flags." (record: "2026-11-18 OWNER RULING — hole-flags: a hole takes the flags in force at the hole; each regex literal has its own flags; and his question, do flags propagate down"); NARROWED by hole-flags' "yes to all" (2026-11-22): at a hole only an explicit `i` or `-i` in force there is taken; `m`, `s` and a weak `i` are not (review r84 C1, C6).
- 2026-11-18 "flags-propagate: yes" (record: "2026-11-18 OWNER RULING — flags-propagate: yes"); NARROWED by hole-flags (2026-11-22): what propagates down a hole is an explicit `i` or `-i` only (review r84 C1, C6).
- 2026-11-22 "program-options: yes." (record: "2026-11-22 OWNER RULING — program-options: yes; and a PROPOSAL: `i` keeps inheriting, with a "weak" value the program sets"); a file's program options are its literals' defaults, a literal's own flags win.
- 2026-11-22 "hole-flags: yes to all. What i like about the i weak behavior is that it's consistent to the other program level settings that only affect literals in program scope." (record: "2026-11-22 OWNER RULING — hole-flags: yes to all (weak values do not propagate; only an explicit `i` is inherited at a hole; `m` and `s` are no longer inherited)"); that "explicit" is what a literal writes is the manager's reading (a), below (review r84 C7).
rejected:
readings:
- an `&` written at program level keeps each side's own flags; flags-in-filter as "reach" (the manager's reading after "by "flags propagate" i thought we decided that rx inherits the flags of the surrounding rx", a recollection) — UNTESTED here (core/holes/flags carries the hole case).
- a sequence operand at program level has no surrounding rx and starts from its own flags (the same reading) — UNTESTED.
- (a) "explicit" is a flag written in a literal's text (`(?i)`, `(?-i)`, `(?i:..)`, `/.../i`), PCRE's scope inside it; `any_case`'s body writes one; a program option is never explicit — SUPPORTED as run (docs/dev/lanes/predspot_evidence/ predspot_model.py EXPLICIT: nine settings over a library `w := /ab/` on `AB`).
- (review r84 A6, the manager's, composing core/patterns/flags, core/holes/flags, core/holes/flags/in-filter and lib/builtin/options) ONE statement of the flags at a point of a literal: the literal's own text, then an explicit `i` or `-i` in force at the hole it is inserted in, then its file's program options from the statement on, then the file default — SUPPORTED as run (docs/dev/lanes/predfix84_evidence/ predfix84_model.py FLAGGRID, EXPLICIT, LEXICAL, LIBFILE).
- (review r84 A6 (1), the manager's ruling of the disposition on his hole-flags words "At a hole, only an explicit `i` or `-i` is inherited.") `r` and the `a`-family are not inherited at a hole; the draft's reading P29-2 (core/holes/flags readings) is superseded — UNTESTED (the flag engine does not model `r` or the `a`-family).
- (review r84 A6 (4), a reading: lib/builtin/pattern's own sentence "the flags in force where the group is written come along") `pattern($x)` carries the flags in force where the group is written, over an explicit `i` at the hole it is inserted in — SUPPORTED as run (docs/dev/lanes/predfix84_evidence/ predfix84_model.py PATFLAGS).
- (review r84 A6 (2)) open option-hole-explicit: is an `i` written by an option hole (`/(?${o})${w}/`, o := `"i"`) explicit? Both candidates run (docs/dev/lanes/predfix84_evidence/ predfix84_model.py OPENFLAGS); no answer applied.
evidence: preddoc3a_model.py FLAGS (`/a(?i)b/`: the flag applies from where it is written; python `re` `a(?i:b)` agrees).; docs/dev/lanes/predspot_evidence/ predspot_model.py FCONTROL, EXPLICIT, FSWEEP (lane predspot).
history:
- 2026-11-18: hole-flags and flags-propagate; 2026-11-19: flags-scope (which flags an inserted rx inherits) is core/holes/flags.
- 2026-11-22 (lane predspot, hole-flags folded; record "2026-11-22 OWNER RULING — hole-flags: yes to all (weak values do not propagate; only an explicit `i` is inherited at a hole; `m` and `s` are no longer inherited)"): ruled 2026-11-18 re-dated 2026-11-22. Statement until then: "A literal's flags are the ones it writes (`(?x)`, `(?i)`, `/.../x`), with PCRE's scope; the predicate opt-in implies none, and a literal standing on its own inherits none."; the bullet until then: "Built up inside another rx, an rx inherits the flags of what surrounds it: for a hole, core/holes/flags."; two bullets added (the file's options; explicit). The line `/a(?i)b/` stands (docs/dev/lanes/predspot_evidence/ predspot_model.py FSWEEP).
- 2026-11-23 (lane predfix84, review r84 A3, A6, C1, C6, C7; record "2026-11-23 MANAGER — review r84 (predspot1122): the dispositions, ruled with the 2026-11-23 rulings in hand; no owner words"): the bullet "No implicit extended mode: `/foo bar/` keeps its space and `#` is literal text." conditioned on the file's program options (A3); a bullet: the flags at a point, in order, with the four sources (A6, the manager's reading); a bullet: `r` and the `a`-family not inherited (A6 (1)); a bullet: `pattern($x)` (A6 (4), a reading, its line); the open line option-hole-explicit with both candidates' lines (A6 (2)); the slug option-hole-explicit; the 2026-11-14 C2 item marked revised in part; the two 2026-11-18 items marked narrowed (C1, C6); the "explicit" gloss marked the manager's reading (C7 (iv)); "hole-flags" cited as "yes to all" in the base (C6).

## core/patterns/sequence — The sequence operator
slugs: sequence-operator sequence-precedence sequence-reading
rulings:
- 2026-11-17 "sequence-reading: splice." (record: "2026-11-17 OWNER RULING — sequence-reading: splice; and the hole reopened")
- 2026-11-17 "sequence-precedence: binds tighter than & and | / sequence-operator: is there a reason why not? I expect rx construction and concatenation is common enough there." (record: "2026-11-17 OWNER RULINGS — the rx module: sequence-precedence and sequence-operator")
rejected:
- juxtaposition as the sequence (`A B`) — by owner — "A B isn't legal so its the addition form" (core/patterns/quantifiers).
- a string paste of the operands — by owner ruling — sequence-reading, splice.
- no concatenation operator (the manager's 2026-11-13 lean, the draft §2.5: sequencing only inside a literal or by `join`), with `concat(x, y)` as the library name for value concatenation — by owner ruling — sequence-operator ("is there a reason why not? I expect rx construction and concatenation is common enough there"), after his rx-module proposal reopened it (the draft R.9).
readings:
- the sequence mark cannot begin an operand (the draft R.1.14) — UNTESTED.
evidence: preddoc3a_model.py SEQ (the draft's PART RX1 line; `\b\d+\b` agrees; the printed answers reproduced). PART RX of predspec25.
history:
- the draft R.1.14. `predicates_future.md` item 21 (the rx module) is this section's (in the language, not parked).

## core/patterns/alternation — Alternation
slugs:
rulings:
- 2026-11-22 "label-reference: required. we can relax it later as you say although i'm not inclined to." (record: "2026-11-22 OWNER RULING — label-reference: required"); the example re-spelled: `l` comes from the bindings A and B, so the alternation is labelled
- 2026-11-17 "branch-scope: yes. I like that." (record: "2026-11-17 OWNER RULING — branch-scope: reading")
- 2026-11-17 "join-order: left side decides. That's always how I thought of it." (record: "2026-11-17 OWNER RULING — join-order: the left side decides")
rejected:
- reading (i) of branch-scope: a condition after a `|` judges only the branch the pattern chose first — by owner ruling — branch-scope (ii).
- rev 23.2's reading (iii) of branch-scope and its scope rule — by owner ruling — branch-scope, reading (ii) ("branch-scope: yes. I like that."; the draft R.9).
readings:
- `c | d` between conditions is the one `|` (the draft R.1.5; condition-or deleted as a separate construct) — SUPPORTED by the regex model (an alternation of two zero-width tests).
evidence: preddoc3a_model.py ALT (the draft's PART A B1 line; printed answers reproduced; `\d\d` agrees).
history:
- 2026-11-17: branch-scope (ii); join-order gave the distribution over a `|` on the left.
- 2026-11-22 (lane predref, label-reference sweep and helper-captures fold): the line's program `(B | A) & (l: <20)` re-spelled `[ab = B | A] & (ab.l: <20)` (label-reference: `l` is not written in the program); answers unchanged (docs/dev/lanes/predref_evidence/ predref_model.py RESPELL). Status date 2026-11-17 to 2026-11-22 (a piece whose text a ruling changes takes the ruling's date).

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
- 2026-11-22 "label-reference: required. we can relax it later as you say although i'm not inclined to." (record: "2026-11-22 OWNER RULING — label-reference: required"); the example re-spelled, the atomic part labelled
- 2026-11-17 "regex-settles: yes settled" (record: "2026-11-17 OWNER RULINGS — regex-settles; absent-under-not")
- 2026-11-17 "Atomic as used by say atomic() would provide pcre behavior." (record: "2026-11-17 OWNER on atomic-search")
rejected:
- an atomic pattern stopping the search at later starts (his item-14 reading "returns nothing") — by owner — atomic-search: "what I was looking for was more akin to (*prune) or similar".
readings:
evidence: preddoc3a_model.py ATOM (the draft's B8 / V17 line; printed answers reproduced; `1\d` agrees); sabotage s7 caught; docs/dev/lanes/predspot_evidence/ predspot_model.py SWEEP (lane predspot).
history:
- 2026-11-17: regex-settles (5); atomic-search moved the other reading to the backtracking verbs (parked/ideas/atomic). The slug came from core/model/modes (lane preddoc3a).
- 2026-11-19 (lane preddoc4): the name `atomic(X)` is the library body lib/control/atomic; this piece keeps the rule (review r59 PLACE-2 (a)).
- 2026-11-22 (lane predref, label-reference sweep and helper-captures fold): the line's program `atomic(B | A) & (l: <20)` re-spelled `[ab = atomic(B | A)] & (ab.l: <20)`; answers unchanged (docs/dev/lanes/predref_evidence/ predref_model.py RESPELL). Status date 2026-11-17 to 2026-11-22.
- 2026-11-22 (lane preddef, default-export folded; record "2026-11-22 OWNER RULING — default-export: protected"): the line re-spelled: until then `[ab = atomic(B | A)] & (ab.l: <20)` (A := `/(?<l>\d)\d/`, B := `/(?<l>\d\d)/`), now `atomic([ab = B | A]) & (ab.l: <20)`, answers unchanged under argument-default's candidate (local), a compile error under (error); the old program is a compile error under the manager's reading (e) (atomic's body uses X alone, so the call label `ab` reaches no `l`). A bullet says so. Run: docs/dev/lanes/preddef_evidence/ preddef_model.py AWAITS, SWEEP.
- 2026-11-22 (lane predfix83, review r83 D6; record "2026-11-22 MANAGER — review r83 (preddef1122): dispositions ruled; one correction; idiom-confirm closed on default-export (no owner words)"): the bullet's "(default-export)" marked as the manager's reading (e) of default-export (a reading printed as a rule). Answers unchanged.
- 2026-11-22 (lane predspot, argument-default and wrapper-export folded; record "2026-11-22 OWNER RULING — wrapper-export: agree (a) (the provided wrappers pass their argument's labels on); and a question: do transforms in general"): the bullet until then: "`atomic(X)` uses X alone in its body, so a label on the call (`[ab = atomic(B | A)]`, `ab.l`) reaches none of X's labels (default-export, by the manager's reading (e) of it); the label is written on the argument, the caller's own text (awaits argument-default)."; the line `atomic([ab = B | A]) & (ab.l: <20)` (a compile error by the reading (a)) re-spelled `atomic(/(?<l>\d\d)/ | /(?<l>\d)\d/) & (atomic.l: <20)`, the same answers (docs/dev/lanes/predspot_evidence/ predspot_model.py SWEEP).

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
slugs: pass-own-labels pass-and joint-last-pass after-loop-read last-pass-default joint-loops pairing-loop array-slot array-scope array-in-piece
rulings:
- 2026-11-22 "occurences et al should only set labels not captures unless they are so declared." (record: "2026-11-22 OWNER RULING — helper-captures: the library's helpers set labels, not captures, "unless they are so declared"; a PROPOSAL of the label-only group `(?<:x>...)`; an example to validate"); a provided body's groups are labels only (core/labels/label-only-group)
- 2026-11-21 "they chose to use the same labels and therefore that has to have a meaning. for simplicity, and due to the fact that the other interpretations can be otherwise spelled, i think option "a"" (record: "2026-11-21 OWNER RULING — array-vs-passes: a"); the group questions and the index read this piece's array of settings (core/labels/labels-vs-captures/array-vs-passes)
- 2026-11-21 "i agree that captures are explicitly written either in literal form or using a macro like capture()." (record: "2026-11-21 OWNER RULING — pure-label: captures are written explicitly; a label is made a capture afterwards too; `_` labels never export; three examples of what a definition may name"); answer (a): a group in rx text or a capture form makes a capture; `[x = A]` a label and no capture
- 2026-11-17 (class: STATEMENT) "setting labels is just the label using the group-label-not-capture syntax" (record: "2026-11-17 OWNER, three points on labels"); his supporting words, recalled in the pure-label discussion
- 2026-11-19 "array-scope: the only way to do it is by the scope of the entire rx. As you say, you could limit it by grouping labels. So x.@a. (?spelling?)." (record: "2026-11-19 OWNER RULING — array-scope: the array of a label is by the scope of the entire rx; a part label limits it")
- 2026-11-17 "after-loop-read: ok I see it. Last pass own label makes sense" (record: "2026-11-17 OWNER RULING — after-loop-read: the last pass's own label")
- 2026-11-17 "I do want that. It makes sense and frankly pcre is wrong on this. I agree but! We need a way to get the pcre behavior even if ugly" (record: "2026-11-17 OWNER RULING — what an unqualified `$x` reads")
- 2026-11-18 "backref-label: capture" (record: "2026-11-18 OWNER RULING — backref-label: capture")
- 2026-11-17 "last-pass-default: regex. I want to have the method of achieving the alternative meanings defined and tested so we don't lose that functionality." (record: "2026-11-17 OWNER RULING — last-pass-default: regex"); it STANDS with its edge changed by after-loop-read the same evening ("(5) last-pass-default (14:30) STANDS", that entry): the carried value is the capture's; its second sentence is a standing instruction (lib/counting/every-pass)
- 2026-11-22 "array-in-piece: if it was written A & /B-defintion/ then the some(h) would see the h from A. but because B is bound first, its internal references refer only to what can be seen at that point." (record: "2026-11-22 OWNER RULING — array-in-piece: b (a group question inside a bound piece reads only what that piece can see)")
- 2026-11-22 "or A SEQ /B definition/" (record: "2026-11-22 OWNER, adding to array-in-piece: "or A SEQ /B definition/""); his addition: both in-place compositions
rejected:
- the array limited to settings from one definition or one literal (his own guess: "I guess is no, because we could define they had to be in the "same" rx.") — by owner ruling — array-scope: "the only way to do it is by the scope of the entire rx"; his own worry in the guess: "The problem is with composition, nothing will be in the same rx".
- "labels match every pass, captures match the last" for a bare condition — by owner — reconsidered within minutes: "what you should do is assign the condition inside the loop to get the all behavior" (record: "2026-11-17 OWNER, reconsidering the entry above within minutes"); closed by after-loop-read.
- regex's carried value for a bare looped label (last-pass-default: regex) — by owner ruling — after-loop-read and the `$x` ruling ("frankly pcre is wrong on this"); the carried value stays reachable as the capture.
- a compile error for a bare condition after a loop (the manager's lean) — by owner ruling — after-loop-read.
- pass-and (a Kleene AND over passes) and joint-last-pass — dissolved by the two-valued model and after-loop-read (a joint reads the last pass's own tuple).
- per-pass pairing for a BARE joint condition, by the loop enclosing its labels (joint-loops (1), its wording pairing-loop part 1) — by owner ruling — after-loop-read: a bare joint reads the last pass's own tuple; per-pass pairing is the joint written on the item (the draft R.9, R.1.7).
- the composed array for a group question inside a BOUND piece (array-in-piece (a): the settings made before the piece included) — by owner ruling — array-in-piece: b; its lines, verbatim as run (predfix77 ARRPIECE, sabotage s2 caught; the record's "entire" line), are the in-place answers: the same text bound first gives WHOLE `7` FAILS.
readings:
- the array form's index counts settings (the draft R.1.7) — RULED by array-vs-passes (a): `h[k]` reads the array of settings (core/labels/labels-vs-captures/array-vs-passes).
- the array beside "a reset contributes nothing" (array-slot) and "a name set before a loop and inside it does not survive the loop" (core/labels/one-rule), against "the one outside the loop included" — CONSISTENT: a reset acts on the label, never on the array; `/(?<h>\d);(?:(?<h>\d);)*/` on `7;` leaves the label h unset and the array [`7`], the separated list `/(?<h>\d)(?:,(?<h>\d))*/` on `7` the same (predarr OUTSIDE; sabotage s3, a reset deleting settings, caught).
- (a) of array-scope: "the entire rx" is the rx as composed AT THE POINT the array is referenced (composed-at-point); stated in the base as "the settings of the name where the name is visible, as they stand where it is read" (the manager's reading, "for the next lane to test") — UNTESTED.
- (b) of array-scope: `x.@a` lists the settings of `a` made inside part `x` only, in order (the manager's reading, "for the next lane to test"); for a part label used twice it is routed through core/labels/paths (its last-mention rule) — UNTESTED.
- what the caller receives for a captured label that a loop sets (PCRE's carried value or the label's last-pass value) is not stated (the manager's reading (e) of pure-label) — SUPPORTED: no record line states it; the two part on `/(?:(?<h>\d)?;)+/` on `3;;` (label unset, python `re` capture `3`; predscope_model.py LOOPVAL, sabotage s13 caught). Asked as capture-loop-value (proposed).
- a name two groups carry under `(?J)`: PCRE's capture is its FIRST set group in pattern order (`\k<h>` and the by-name copy), not the last set; the label is the last mention — SUPPORTED by a run (libpcre2-8 10.46: `(?J)(?<h>\d)(?:;(?<h>\d))?\k<h>` WHOLE `7;37` MATCH, `7;33` NOMATCH, `77` MATCH; the by-name copy on `7;3` gives `7`; the label on `7;3` is `3`; predfix77_model.py DUPNAME, sabotage s6 caught).
- the two ruled lines: "Bound first" equals the record's pasted `own` line and "Written in place" (`A SEQ /(?:;(?<h>\d))*${some((h: "7"))}/`, his "or A SEQ /B definition/") its `entire` line, each built from the program text; each against a hand regex, 0 / 0 / 0 of 1,365 texts over `71;x` (predfix77 ARRPIECE).
- (b) of array-in-piece: "what can be seen at that point" includes the public labels of the parts the piece itself uses (a B whose body uses A sees A's settings; core/labels/export statement 2) — SUPPORTED as a run of the reading (predfix77 ARRREAD: `U := A SEQ /..some../` answers as the in-place line, 0 / 0 / 0).
- (e) of array-in-piece: the path form (`x.@a`) and the user's own read of both parts are unchanged — UNTESTED (no line moves; nothing in the documents names them as changed).
evidence: preddoc3a_model.py CAPT, CAPT2 (the draft's PART L: `\k<m>` reads the capture `45` while the label m is unset; python `re` agrees on the regex half); sabotage s9 caught. predfix77_model.py DUPNAME (libpcre2-8), ARRPIECE. predfix77_model.py ARRPIECE, ARRREAD (array-in-piece).
history:
- 2026-11-17: last-pass-default (regex), then "labels match every pass", reconsidered within minutes, then after-loop-read and the `$x` ruling (the settled state of the evening).
- 2026-11-18: backref-label (capture).
- the skeleton's statement "A label matches every pass; a capture is PCRE's last value" (the superseded entry) replaced by the after-loop-read statement (lane preddoc3a).
- 2026-11-16 joint-loops and pairing-loop part 1 (per-pass pairing of a joint condition by the loop enclosing its labels; "I agree. Makes sense.", record "2026-11-16 OWNER RULING — joint-loops: agreed, all three parts"; "pairing-loop: I agree part 1.", record "2026-11-16 OWNER RULING — pairing-loop, part 1: the wording confirmed; his remark on optionals") are REVERSED for a bare joint by after-loop-read (cited above: a bare joint reads the last pass's own tuple); the per-pass form is the condition inside the loop, on the item. The slugs are homed here for that reason (lane preddoc5, review r59 COMPA-11).
- the slug array-slot moved here from core/labels/one-rule: the rule it decided ("a reset contributes nothing" to the array form) is this piece's (lane preddoc5, review r59 PLACE-4).
- 2026-11-19 (lane preddoc6, review r60 COLD-13): "a callout" among the capture's readers qualified "where one is allowed: a one-literal program" (core/patterns/literals refuses callouts inside a larger program).
- 2026-11-19: array-scope ruled after hole-export; the heading date moved from 2026-11-17 with it.
- 2026-11-19 (lane predfix61, review r61 F-F (RULING-12, REACH-3, REACH-4, GENERAL-3, GENERAL-13), F-J (RULING-11)): array-scope's readings (a) and (b) were folded as body; now marked readings in the base and listed above. The bullet until then, verbatim: "The array's scope is the entire rx as composed, not one literal or one definition: `[x = rx.digit]+` and `/(?<x>\d)+/` have one array, and two groups of one name in a sequence give it both settings. A part label limits it: the array of `a` under part `x` (placeholder `x.@a`) lists the settings made inside that part." The rejected item's quote was altered ('same' for "same") and its reason was his hole-export worry, not array-scope's words; both corrected. The array of settings against the loop's passes: core/labels/labels-vs-captures/array-vs-passes.
- 2026-11-21 (lane predscope, pure-label folded): two bullets added (a label is not always a capture; the caller's value for a captured looped label not stated) and the line "Captured in a loop"; the rest unchanged. Status date 2026-11-19 to 2026-11-21. evidence: predscope_model.py CAPT, LOOPVAL.
- 2026-11-21 (lane predarr, array-vs-passes ruled): the array bullet's "its index `h[k]` counts settings (a reading). Settings or the loop's passes: core/labels/labels-vs-captures/array-vs-passes." became "which read this array, as its index `h[k]`, the k-th setting, does (core/labels/labels-vs-captures/array-vs-passes)". No answer moves.
- 2026-11-22 (lane predfix77, review r77 A1, A8; record "2026-11-22 MANAGER — review r77 (predfold1121): dispositions ruled (no owner words)"): the CAPTURE bullet until then, verbatim: "The CAPTURE is regex's: the value from the last time a group of the name was set, read inside rx text (`\k<x>`, a conditional group, and a callout where one is allowed: a one-literal program, core/patterns/literals) and by the carried-capture form, a visibly different spelling." It parted from PCRE for a duplicated name (the line "Two groups of one name" added). The array-scope bullet gains the collision with bare-nested-scope case 2, stated as the open core/labels/labels-vs-captures/array-in-piece; neither answer stated.
- 2026-11-22 (lane predfix77, R-1 and R-2 of its rulings file; array-in-piece RULED (b)): the array-scope bullet gains the ruled reading in the definition the question is written in, his words, and the lines "Bound first", "Written in place"; status date 2026-11-21 to 2026-11-22. The collision of review r77 A1 (array-scope against bare-nested-scope case 2) is settled by it; the open piece the lane had drafted for it was never delivered.
- 2026-11-22 (lane predref, label-reference sweep and helper-captures fold): helper-captures: the second bullet names the label-only group beside `[x = A]` (no capture). No line moves.
- 2026-11-22 (lane predfix82, review r82 FIXIND-7; record "2026-11-22 MANAGER — review r82 (predfold1122): dispositions ruled; two corrections of record entries (no owner words)"): the array-scope bullet: "the entire rx as composed, not one literal or one definition" became "the entire rx as composed in the definition the question is written in, not one literal".

## core/labels/labels-vs-captures/array-vs-passes — The array of settings, not the loop's passes
slugs: array-vs-passes joint-in-some
rulings:
- 2026-11-21 "array-vs-passes: in your example, the user chose to set the labels the same. if they wanted the out-the-loop setting to be separately labeled they could have done so. also, if they wanted the h5,m3 condition to be held at the same time they could have specified (h,m): (5,3) but they did not. they chose to use the same labels and therefore that has to have a meaning. for simplicity, and due to the fact that the other interpretations can be otherwise spelled, i think option "a"" (record: "2026-11-21 OWNER RULING — array-vs-passes: a"); answer (a): `some`, `count`, `occurs` and `h[k]` read the ARRAY OF SETTINGS of a name, every setting in order, the one outside the loop included. His reasons: the user chose one name, "and therefore that has to have a meaning"; a setting outside the loop wanted apart is given its own label, in his words "if they wanted the out-the-loop setting to be separately labeled they could have done so"; "simplicity"; "the other interpretations can be otherwise spelled"; the record says the ruling REVISES lib/counting's statements on passes and the reading under core/model/places/outermost-view
- 2026-11-21 "join-in-some: agree and elegant. that said, no one would know to write it." (record: "2026-11-21 OWNER RULING — joint-in-some: agree"); the reading of "agree" taken and told to him, the manager's leaning (c): a joint entry `(h, m): ...` inside a group question is refused for now (a compile error; pairing by index or by item can be allowed later without changing an answer); "same item" is written on the item, the item labelled only where it meets the condition, then a group question on that label (the base's line "Same item, on the item" runs it). "no one would know to write it" is an OBSERVATION (discoverability), not a ruling: the idiom is on the user-documentation list (parked/ideas/user-doc-traps)
- 2026-11-22 "array-in-piece: if it was written A & /B-defintion/ then the some(h) would see the h from A. but because B is bound first, its internal references refer only to what can be seen at that point." (record: "2026-11-22 OWNER RULING — array-in-piece: b (a group question inside a bound piece reads only what that piece can see)")
rejected:
- (b) the passes of the outermost loop holding the group, each pass judged with its own labels, false where the loop made no pass (lib/counting's wording of 2026-11-15) — by owner ruling — array-vs-passes (a). Its lines, verbatim as run (predarr_model.py AVP, RECORD, EMPTY):
  Two depths: Passes: WHOLE `3;4;,5;,` HOLDS, `3;,5;,` HOLDS / SEARCHED `x3;4;,5;,` `3;4;,5;,`@1 / FIND-ALL `3;4;,5;, 3;,5;,` [`3;4;,5;,`@0, `3;,5;,`@9] (`/(?:(?:(?<h>\d);)+,)+/ & (h[2]: "5")`)
  Two in a pass: Passes: WHOLE `71,` FAILS, `17,` HOLDS / SEARCHED `x71,` FAILS / FIND-ALL `71, 17, 12,` [`17,`@4] (`/(?:(?<d>\d)(?<d>\d),)+/ & some((d: "7"))`)
  Outside the loop: Passes: WHOLE `7;` FAILS, `1;7;` HOLDS / SEARCHED `x7;` FAILS / FIND-ALL `7; 1;7; 1;` [`1;7;`@3] (`/(?<h>\d);(?:(?<h>\d);)*/ & some((h: "7"))`)
  Passes: WHOLE `5:1,2:3,` FAILS, `5:3,` HOLDS, `2:1,` FAILS / SEARCHED `2:1, 5:1,2:3,` FAILS / FIND-ALL `5:1,2:3, 2:1, 5:3,` [`5:3,`@14] (`/(?:(?<h>\d):(?<m>\d),)+/ & some((h: "5", m: "3"))`)
  Passes: WHOLE `,` HOLDS, `7,` FAILS, `1,` HOLDS / SEARCHED `7, ,` `,`@1 / FIND-ALL `, 7, 1,` [`,`@0, `,`@3, `1,`@5] (`/(?:(?<d>\d)?,)+/ & some(NOT (d: "7"))`)
  Passes: WHOLE `,` FAILS, `7,` HOLDS, `1,` FAILS / SEARCHED `1, ,` FAILS / FIND-ALL `1, , 7,` [`7,`@5] (`/(?:(?<d>\d)?,)+/ & (n: ==0)`, n := `count(NOT (d: "7"))`)
- (c) split: a group question over the passes, the array form and its index over the settings (the manager's leaning when asked) — by owner ruling — array-vs-passes (a).
- a joint entry inside a group question paired BY INDEX (joint-in-some (a)) — by owner ruling — joint-in-some: refused for now; it finds (`5`, `3`) in `5,2:3,` though no item holds both:
  By index: WHOLE `5:3,` HOLDS, `5:1,2:3,` FAILS, `5,2:3,` HOLDS, `2:3,5,` FAILS / SEARCHED `x5,2:3,` `5,2:3,`@1 / FIND-ALL `5:3, 5,2:3, 2:3,5, 5:1,2:3,` [`5:3,`@0, `5,2:3,`@5] (`/(?:(?<h>\d)(?::(?<m>\d))?,)+/ & some(((h, m): ("5", "3")))`)
- a joint entry inside a group question paired BY ITEM (joint-in-some (b), the passes again) — by owner ruling — joint-in-some: refused for now; the on-item form gives the same answers (predarr IDIOM):
  By item: WHOLE `5:3,` HOLDS, `5:1,2:3,` FAILS, `5,2:3,` FAILS, `2:3,5,` FAILS / SEARCHED `x5,2:3,` FAILS / FIND-ALL `5:3, 5,2:3, 2:3,5, 5:1,2:3,` [`5:3,`@0] (`/(?:(?<h>\d)(?::(?<m>\d))?,)+/ & some(((h, m): ("5", "3")))`)
readings:
- (a) of array-vs-passes: a record of several plain entries inside a group question is the product of its entries, each a group question over its own array (`some((h: "5", m: "3"))` is "some h is 5 and some m is 3") — SUPPORTED by the record's run ("passes WHOLE `5:1,2:3,` FAILS, settings HOLDS"; predarr RECORD, against a hand regex 0 / 0 / 0 of 5,461 texts) and by his words "if they wanted the h5,m3 condition to be held at the same time they could have specified (h,m): (5,3)"; BUT it parts from record-is-product ("record-is-product: absolutely", 2026-11-16: `(h: A, m: B)` = `((h, m): (A, B))`) inside a group question, where the joint form is refused (joint-in-some): an owner question (record-in-some, proposed).
- (b): `count(c)` and `occurs` on a one-entry condition count SETTINGS — SUPPORTED (it follows from the ruling's words; predarr CHANGED, EMPTY); on several entries what is counted is not stated — SUPPORTED (no record line states it; the model refuses to compute it): an owner question (count-several, proposed).
- (c): the group questions are false / zero on an EMPTY array, replacing "false where the loop made no pass" — SUPPORTED as a reading of the ruling (predarr EMPTY; sabotage s9 caught). It moves answers only for a negated condition: `some(NOT (d: "7"))` on `,` FAILS on the array and HOLDS on the passes.
- (d): group-truth re-put — see core/model/table/group-truth (on the array `NOT some(c)` = `occurs.none(c)` by definition; "now part on settings, not passes" NOT SUPPORTED as worded).
- (e): "same item" without a joint entry is spelled on the item — SUPPORTED (predarr IDIOM: against the by-item reading and against a hand regex, 0 / 0 / 0 of 5,461 texts over `53:,`; the record's four subjects in the line "Same item, on the item").
- joint-in-some (a): the refusal's message names the on-item form (the manager's call on a diagnostic's content) — UNTESTABLE as a rule (a wording); the model's error names `[ok = item & ((h, m): (..))]` (predarr REFUSE).
- joint-in-some (b): the idiom on the user-documentation list — done (parked/ideas/user-doc-traps, item 30).
- joint-in-some (c): no shorthand parked — SUPPORTED (nothing parked beyond the list item).
- `h[k]` is the k-th setting, 1-based as the line "Two depths" reads `h[2]` — the ruling's words; 1-based is core/values/metadata's convention (a reading).
- the array's order is the order the settings are made along the path, a lookahead's setting before the group it precedes (review r77 MODES-7) — SUPPORTED as a run of the reading (predfix77 ARRORDER: on `12` the settings of h are [`2`, `1`]; the text order would give [`1`, `2`] and `(h[2]: "1")` FAILS; sabotage s13 caught).
- `h[k]` past the array's end is an absent value: a test on it fails, NOT of it holds (review r77 MODES-8) — SUPPORTED as a run of the reading (predfix77 ARRORDER: `/(?:(?<h>\d)?;)+/ & NOT (h[2]: "5")` WHOLE against a direct count, 0 of 781 texts differ); the error reading has no line.
- a `$` read inside a group question's set reads the label as it stands where written (core/values/reads), the last pass's (review r77 MODES-10) — SUPPORTED as a run of the reading (predfix77 ARRORDER, the line "A read inside"); the promise "can be allowed later without changing an answer" is narrowed to JOINT entries, since a later pairing by item would change that line (`11,23,` would hold).
- the record inside a group question parting from its joint form: now the open core/conditions/form/record-in-some (review r77 A9).
- (c) of array-in-piece: the ruling covers `some`, `count`, `occurs` and the index `h[k]` alike — SUPPORTED as a run of the reading for `some` and `h[k]` (predfix77 ARRREAD: `(h[1]: "7")` bound first against `\d;7(?:;\d)*`, in place against `7(?:;\d)*`, 0 / 0 / 0); `count` and `occurs` follow by the same array (not run).
- (d) of array-in-piece (review r77 A2): a group question written in an `&` operand inside ONE definition reads the settings visible in that definition at that point; with his "or A SEQ /B definition/", in place in an `&` operand the array holds both sides' settings — SUPPORTED as a run of the reading (predfix77 ARRREAD: the line "In an `&` operand, one definition" against `(?:7|\d(?:;\d)*;7)(?:;\d)*`; the rival, the operand's own stretch only, against `\d(?:;\d)*;7(?:;\d)*`, both 0 / 0 / 0; sabotage s3 caught); not separately ruled. A plain read of a name both sides surface stays the ambiguous reference (core/labels/flow), untouched by his words.
evidence: docs/dev/lanes/predarr_evidence/ predarr_model.py ARRAYS, OUTSIDE, AVP, RECORD, JOINT, REFUSE, IDIOM, EMPTY; sabotages s2-s9 caught. Earlier: predfix61_model.py FF, FF2 (the six lines, then candidates (a) and (b)). predfix77_model.py ARRORDER, RECORD; sabotages s13, s19 caught. predfix77_model.py ARRREAD.
history:
- 2026-11-19 (lane predfix61, review r61 F-F: REACH-3, the tension older than the session, sharpened by array-scope's "two groups of one name in a sequence give it both settings"): a new open sub-piece at the manager's ruling of review r61, with the review's three witnesses.

- 2026-11-21 (lane predarr): RULED (a), joint-in-some folded; the heading "The array of settings or the loop's passes" renamed. The piece until then, verbatim: statement "Do the group questions (`some`, `count`, `occurs`) and the index `h[k]` read the array of a label's settings, or the passes of the loop that sets it?"; body "The rule today tells the group questions to the ARRAY (every setting, in order, the one outside the loop included; `h[k]` counts settings, a reading), while lib/counting defines them on a loop's PASSES, each pass with its own label, false where the loop made no pass. They part on two depths, two settings in one pass, and a setting outside the loop. Candidates: (a) the array of settings; (b) the passes of the outermost loop holding the group." Its six lines were labelled "Two depths, (a): Settings: ...", "Two depths, (b): Passes: ..." and so on; the (a) lines stay as "Two depths: Settings: ..." (the same answers, re-run), the (b) lines are under rejected above. Lines added: the label beside the array, a record of two entries, the record form, same item on the item, an empty array, a count of zero. Status open 2026-11-19 to ruled 2026-11-21.
- 2026-11-22 (lane predfix77, review r77 A9, A11, A3; record "2026-11-22 MANAGER — review r77 (predfold1121): dispositions ruled (no owner words)"): three readings added (order, past the end, a `$` read inside) with their lines; "pairing by index or by item can be allowed later" narrowed to "pairing a joint entry"; the record bullet's "(a reading; inside a group question a record and its joint form then part, core/conditions/form)" re-pointed to record-in-some; the line "A count of zero" names its `n` a bound condition (core/holes/bare-condition/bound-condition). No answer moved.
- 2026-11-22 (lane predfix77, R-1 and R-2): array-in-piece folded (the array is read in the definition the question is written in; readings (c), (d)) with the line "In an `&` operand, one definition (a reading)"; status date 2026-11-21 to 2026-11-22.
2026-11-22 (lane predbound, bound-condition and count-in-set ruled): the line "A count of zero" written in place, `(count(NOT (d: "7")): ==0)`, its binding `n := `count(NOT (d: "7"))`` being a compile error now; the line until then ended "(`/(?:(?<d>\d)?,)+/ & (n: ==0)`, n := `count(NOT (d: "7"))`; `n` (depends on the open bound-condition: core/holes/bare-condition/bound-condition))"; the answers do not move (predbound FIVE).

## core/labels/label-only-group — The label-only group in rx text
was: parked/ideas/label-only-group (2026-11-22, moved: his helper-captures ruling needs the thing, so it leaves the parked list; under construction, his form the placeholder)
slugs: -
rulings:
- 2026-11-22 (class: PROPOSAL) "help-captures: 1. i propose the form (?<:x>...) for a label only group x. i've mentioned it before." (record: "2026-11-22 OWNER RULING — helper-captures: the library's helpers set labels, not captures, "unless they are so declared"; a PROPOSAL of the label-only group `(?<:x>...)`; an example to validate")
- 2026-11-22 "occurences et al should only set labels not captures unless they are so declared." (record: "2026-11-22 OWNER RULING — helper-captures: the library's helpers set labels, not captures, "unless they are so declared"; a PROPOSAL of the label-only group `(?<:x>...)`; an example to validate")
- 2026-11-18 (class: RECOLLECTION of a PROPOSAL; nothing ruled) "for capture group regex: i proposed /(<:x>foo)/ would be regex for a labeled group that is not a" (record: "2026-11-18 OWNER, a RECOLLECTION in the hole-reads-capture discussion: the label-only group")
- 2026-11-18 (class: CORRECTION of the entry above, nothing ruled) "oops. yes, i missed the ?. it should look like the top row" (record: "2026-11-18 OWNER, correcting his spelling of the label-only group"); the spelling quoted above, `(<:x>foo)`, was a slip for `(?<:x>foo)`
rejected:
readings:
- the label-only group is a label under every label rule (reset, last mention, the array) and never a capture (the manager's reading (d) of the helper-captures entry) — SUPPORTED as run (docs/dev/lanes/predref_evidence/ predref_model.py LABELONLY: the bodies of `occurrences` and `hits` with `(?<:hit>...)` set the label `hit` as the old `(?<hit>...)` did, the same answers on the record's four programs and on `hits(/a(?<g>x)?/) & (g: "x")`; `hit` is no capture, the user's `g` and `n` in an argument are; sabotage s4 caught)
- `\k<x>` to a label-only group inside its own literal is a compile error for now — UNTESTED (the manager's reading; nothing stated)
- "occurences et al" is every provided body writing a group for its own use, a user's literal keeping pure-label (the manager's reading (a)) — run as a census (docs/dev/lanes/predref_evidence/ predref_model.py LABELONLY: library.md's provided bodies writing a named group in rx text are `occurrences`, `hits`, `capture`; the first two now write `(?<:hit>...)`; `capture`'s purpose is the capture, left as written)
evidence: docs/dev/lanes/predref_evidence/ predref_model.py LABELONLY, HITS.
history:
- 2026-11-22 (lane predref, label-reference sweep and helper-captures fold): new under-construction piece, moved from parked/ideas/label-only-group (the `was:` line); its details there, whole:
- the ideas file (`docs/design/predicates_future.md`) item 32, "The label-only group: labelled, not a capture (`(?<:x>...)`, his stated form 2026-11-18; a placeholder)", whole:

  - The owner's PROPOSAL of 2026-11-09 (POSTFACT.md, "Label spelling", "Names are labels, numbers are captures"),
    recalled by him 2026-11-18 evening (COND-FAMILY, "a RECOLLECTION ... the label-only group"): a group's name and
    its capture status are orthogonal; the fourth cell, named and non-capturing, sets a label and returns nothing.
  - Checked: libpcre2 rejects `(?<:x>foo)` and `(?':x'foo)` (error 162), so neither changes a valid PCRE pattern.
  - Open with it: what `\k<x>` on a label-only group means; whether `(?<x>...)` then returns without the `captures`
    opt-in (§6.2); the 11-09 "numbers are captures" against number-names (RULED 2026-11-18).
  - TRIGGER: the owner rules it (it is his to raise as a question), or the spellings review reaches group forms.
- 2026-11-19 (lane preddoc3c): its trigger and source written into the base piece; the item's text copied here.
- 2026-11-22 (lane predfix77, review r77 D12 (FIXIND-8); record "2026-11-22 MANAGER — review r77 (predfold1121): dispositions ruled (no owner words)"): a bullet: at the expression level `[x = A]` already makes a label and no capture (pure-label), so the idea is the rx TEXT spelling only; its second open point (does `(?<x>...)` return without the opt-in) is answered by pure-label statement 5.
- 2026-11-22 (lane predfix82, review r82 RULING-8 (b), (c); record "2026-11-22 MANAGER — review r82 (predfold1122): dispositions ruled; two corrections of record entries (no owner words)"): "recorded with his proposal of the earlier day" became "as recorded with his recollection of the proposal"; "for its own use" marked a reading.

## core/labels/one-rule — One label rule: branchings reset
slugs: bare-loop-label before-and-inside shared-label repeated-means unsettable-label empty-pass optional-as-loop
rulings:
- 2026-11-17 "Yes. Let's keep it" (record: "2026-11-17 OWNER RULING — branchings reset the labels inside them")
- 2026-11-17 "array-slot: only what was set. As you say, someone could get the empty values." (record: "2026-11-17 OWNER RULING — array-slot: only what was set")
- 2026-11-17 "polarity-rule: warning for both. Warnings are errors given some strictness setting eg @config.strict()" (record: "2026-11-17 OWNER RULING — polarity-rule")
- 2026-11-16 "optional-as-loop: that comment was for discussion. I agree both spellings should answer alike." (record: "2026-11-16 OWNER RULING — optional-as-loop"); `x?` and `(?:x|)` answer alike; his 13:29 "Even /x?/ is a loop from 0 to 1" is discussion, not a ruling
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
- 2026-11-19 (lane preddoc6, review r60 COLD-14): the bullet on a label no match can set names its warning, `pcrec.test.never` (polarity-rule: "a test on an unsettable label" became that warning; core/diagnostics/warnings' `rejected:`).

## core/labels/flow — Labels across composed parts
slugs: label-flow label-mark
rulings:
- 2026-11-22 "default-export: protected" (record: "2026-11-22 OWNER RULING — default-export: protected"); a user reads what a piece exports; a part used alone is protected
- 2026-11-22 ""binding-prefix" 1. yes. 2. i agree with your lean (a)" (record: "2026-11-22 OWNER RULING — binding-prefix: 1 yes"); part 2 keeps the error of his point 4 for a plain read with the binding used more than once; part 1 and the one-use case REVISE "a binding's name is not a path"
- 2026-11-17 "a. yes. a label from an rx is whatever label is surfaced by that rx. b. thats a good point but list here is one rx so exposes one h. i adjust my rules to be such that a compose and a literal rx have the same label behavior" (record: "2026-11-17 OWNER RULING — label-flow")
- 2026-11-17 "label-flow: 1. propose: it is an error to ambigously reference a label. so if A & B & (h: blah) and A and B both use label h, it is an error. this is different than "its an error for labels of the same name to exist at all in A & B"" (record: "2026-11-17 OWNER PROPOSAL — label-flow: an ambiguous REFERENCE is the error")
rejected:
- across the sequence operator a name both parts set is ambiguous (point 2 of his proposal) — by owner — withdrawn by his adjustment ("a compose and a literal rx have the same label behavior").
- the manager's readings (a) "names inside a part are resolved in that part, before the splice" and (d) "renaming groups apart before splicing" as the RULE — by owner — his clarification "it should be the last reference as labels" and free-name; renaming stays the evidence's model (the draft R.9).
readings:
- under label-reference the flow rules judge a name read bare where the parts are written in place, or through a label over the composition; one part's prefix reads that part's own label (lane predref's reading, from binding-prefix's "One use" line) — SUPPORTED as run for the alternation and the atomic part (docs/dev/lanes/predref_evidence/ predref_model.py RESPELL: `[ab = B | A]`, `ab.l`), UNTESTED as a rule
- a chain `A & B` with h on both sides, used as a part, still surfaces h ambiguously (the manager's) — UNTESTED. [review r83 D9: the old sense; the base now reads it: used alone in another binding the chain exports neither side's h, labelled `ab.h` is still ambiguous, SUPPORTED as run, docs/dev/lanes/predfix83_evidence/ predfix83_model.py AMBOUT]
- label-mark (the single labelling form the rx module offers) is closed by entailment; its spelling stays in core/spellings — not a run question.
- (CORRECTION 1 of the record entry "2026-11-22 MANAGER — review r83 (preddef1122): dispositions ruled; one correction; idiom-confirm closed on default-export (no owner words)") default-export also narrows label-flow (b) of 2026-11-17, "a compose and a literal rx have the same label behavior", for what a piece's USER reads: `D1 := CA SEQ CB` (each used alone) exports no `c` where `D2 := /(?<c>\d)(?<c>\d)/` exports its groups — a consequence, the manager's reading; SUPPORTED as run (docs/dev/lanes/predfix83_evidence/ predfix83_model.py WITNESS: `D2 & (D2.c: "3")` the last mention, `D1 & (D1.c: "3")` refused, not visible; sabotage s25 caught).
- (review r83 A1, A7) the `&` ambiguity holds on a read from outside a binding over a chain, through a part label over a chain, through two export lists across `&`, and for bare `$h` and `h[2]` across `&` — the text's rule, now enforced by the evidence engine; SUPPORTED as run (docs/dev/lanes/predfix83_evidence/ predfix83_model.py AMBOUT, BAREAMB; sabotage s2, s3 caught).
- "surfaces" is a name visible in the definition, protected labels included; what a user reaches is what a piece exports — a reading (review r83 D9), UNTESTED (wording).
evidence: preddoc3a_model.py FLOW (the draft R.1.13 (3)(i) line; printed answers reproduced; `\d(?:,\d)?` agrees on the spans).
history:
- 2026-11-21 (the manager, bare-nested-scope case 2): a bullet for the exception ruled under bare-nested-scope case 2 (what a piece reads inside itself is its own settings; compose-equals-literal is for the piece's user), and a `see:` pointer.
- 2026-11-17: the proposal, then the ruling with his adjustment; shared-label's error revised to the reference.
- 2026-11-22 (lane predfix77, review r77 D2 (FIXIND-14), D8; record "2026-11-22 MANAGER — review r77 (predfold1121): dispositions ruled (no owner words)"): statement until then, verbatim: "A label from a pattern is whatever label it surfaces; a composed pattern and a literal have the same label behaviour (the last mention wins)." It now carries the definition unit (within a definition, and for a piece's user); status date 2026-11-17 to 2026-11-21. In the exception bullet his quoted phrase is spelled as he wrote it, "behavior" (was "behaviour"). No answer moved.
2026-11-22 (lane predbound, R-1, binding-prefix ruled): the bullet until then, verbatim: "A binding's name is not a path (`A.h` is an error where a label is referenced)." (from his label-flow point 4 of 2026-11-17: "A . B & (A.h: blah) error. A is a binding not a label and could be ambigous if its used multiple times in an expression", record "2026-11-17 OWNER PROPOSAL — label-flow: an ambiguous REFERENCE is the error"); now the binding's name is a prefix (core/labels/paths/binding-prefix). Status date 2026-11-21 to 2026-11-22.
- 2026-11-22 (lane predref, label-reference sweep and helper-captures fold): a bullet: what the flow rules judge under label-reference (a reading). No line moves.
- 2026-11-22 (lane predfix82, review r82 ANS-6, GENERAL-7; record "2026-11-22 MANAGER — review r82 (predfold1122): dispositions ruled; two corrections of record entries (no owner words)"): a one-use plain read marked a reading (open idiom-confirm); a bullet and the line "Across `&`": a group question over a name both sides of `&` surface reads both (run, predfix82 AMBIG).
- 2026-11-22 (lane preddef, default-export folded; record "2026-11-22 OWNER RULING — default-export: protected"): statement until then: "A label from a pattern is whatever label it surfaces; within a definition, and for a piece's user, a composed pattern and a literal have the same label behaviour (the last mention wins)." The reading on a chain until then: "A chain `A & B` whose sides both surface h, itself used as a part, still surfaces h ambiguously (a reading)." Now: used alone in another binding it exports neither side's h; labelled, `ab.h` is still ambiguous. The exception bullet gains: the user reads only what the piece exports. The owner's "a compose and a literal rx have the same label behavior" now holds inside a definition and, for the user, where the composition labels its parts (a reading).
- 2026-11-22 (lane predfix83, review r83 D2, D9, D17, A1, A7; record "2026-11-22 MANAGER — review r83 (preddef1122): dispositions ruled; one correction; idiom-confirm closed on default-export (no owner words)"): statement until then: "A label from a pattern is whatever label it surfaces; within a definition a composed pattern and a literal have the same label behaviour (the last mention wins); a user reads what a piece exports." The exception bullet until then: "The exception (ruled): what a separately defined piece reads INSIDE itself is its own settings only; "the same label behavior" is for what the piece's user reads (core/holes/bare-condition/nested-scope), and the user reads only what the piece exports: a part it uses alone is protected (core/labels/export, statement 3)." Now: the narrowing of label-flow (b) for the user (CORRECTION 1) with the lines "One literal" and "Composed"; a bullet saying what "surface" means; the one-use bullet cites one-use-read as ruled by default-export (it said "a reading; open idiom-confirm"); refusal lines for the A1 and A7 shapes.

## core/labels/export — Export and private labels
slugs: export-rule export-scope free-name filter-captures hole-export
was: core/holes/labels/hole-export (2026-11-19, merged: the question is answered here)
rulings:
- 2026-11-22 "default-export: protected" (record: "2026-11-22 OWNER RULING — default-export: protected"); a part used alone in a binding (no part label) is available inside it and NOT exported; it reverses hole-export and statement 3 for an unlabelled part
- 2026-11-22 "label-reference: required. we can relax it later as you say although i'm not inclined to." (record: "2026-11-22 OWNER RULING — label-reference: required"); statement 3's spelling: a passed label is referenced with its source
- 2026-11-22 "occurences et al should only set labels not captures unless they are so declared." (record: "2026-11-22 OWNER RULING — helper-captures: the library's helpers set labels, not captures, "unless they are so declared"; a PROPOSAL of the label-only group `(?<:x>...)`; an example to validate"); statement 5: a provided body's groups are label-only, no caller capture
- 2026-11-21 "i agree that captures are explicitly written either in literal form or using a macro like capture()." (record: "2026-11-21 OWNER RULING — pure-label: captures are written explicitly; a label is made a capture afterwards too; `_` labels never export; three examples of what a definition may name"); NARROWS statement 5, ruled 2026-11-18 as "The caller's captures: agree": the caller gets captures, not every public label
- 2026-11-21 (class: STATEMENT, marked agreed "as we discussed") "1. purely predicate labels and 2. cannot become exported captures (although they might be internal captures)" (record: "2026-11-21 OWNER RULING — pure-label: captures are written explicitly; a label is made a capture afterwards too; `_` labels never export; three examples of what a definition may name"); of the `_t` labels; their use, his words: "they would be used in your examples to define a binding level label like the quote character in a string."
- 2026-11-19 "they have to work the same. Agree both pass through." (record: "2026-11-19 OWNER RULING — hole-export: both pass through; and a question on the array of a label under composition"); it revises statement 3 of export-rule; REVERSED for an unlabelled part by default-export (2026-11-22)
- 2026-11-18 "export-rule: Agee and add [_a = A] is a private reference that wouldn't export at all" (record: "2026-11-18 OWNER RULING — export-rule: public unless `_`; a binding shows its own public labels and its public part labels")
- 2026-11-18 "I meant it wouldn't export outside the binding. To close all exports use [_ = A]" (record: "2026-11-18 OWNER, clarifying export-rule's sixth statement, and adding a form: `[_ = A]` closes all exports")
- 2026-11-18 "backref-across-parts: I agree with error. It is like if a function in C were defined then references a variable it doesn't have defined so it looks up the call stack to the previous definition. Catastrophic. The rx should export the group." (record: "2026-11-18 OWNER RULING — free-name: a reference to a name the rx does not define is an error")
- 2026-11-18 "That's exactly right. It makes its labels invisible so you can use it to filter but not cloud the namespace" (record: "2026-11-18 OWNER confirms the reading of `[_ = A]`"); RULED, the reading confirmed: `[_ = A]` makes A's labels invisible everywhere outside A
rejected:
- statement 3 as first ruled, "Outside a binding, what is visible is the public labels written in its own literals, and its public part labels" (an unlabelled sequence part exporting nothing, a hole exporting) — by owner ruling — hole-export: "they have to work the same". REVIVED by default-export (2026-11-22) for an unlabelled part: a part used alone exports nothing, a hole now alike; the rejection stands for nothing that is ruled today (review r83 D1).
- neither passes through (only a part label re-exports; candidate (b)) — by owner ruling — hole-export. REVIVED by default-export (2026-11-22): it is the rule now for an unlabelled part (review r83 D1).
- "a filter can never produce captures" (his lean, filter-captures) — closed by export-rule: visibility goes by export, not by the operand's role.
- an explicit export spelling — by owner ruling — export-rule: the `_` prefix decides. PARTLY in force since export-list (2026-11-22): a part label's named list selects a part's labels; the `_` prefix still decides a binding's own labels (review r83 D1).
readings:
- [review r83 D9: the general clause is the old sense, false under default-export (inside, a part used alone is seen; outside, not); the `date` example, its parts labelled, stands] outside a binding the view is the inside view less the private names, so a read of `v` outside `date := [y = year] SEQ "-" SEQ [m = month]` reads the last mention where the old statement 3 made it an error (the manager's reading (a) of hole-export, "for the next lane to test"; array-scope's reading (c): "it stays a reading") — RULED 2026-11-21 (core/labels/export/flat-read-outside), no longer a reading; since label-reference (2026-11-22) spelled `date.v`, the bare `v` a compile error; its answers RUN (predfix61 FB).
- a part under a `_` part label, or `[_ = A]`, passes none of its labels outside, so statement 3 agrees with statements 6 and 7 (the manager's reading (b) of hole-export: "`[_ = A]` and a `_` part label still close a part's labels") — SUPPORTED as rule-as-code (predfix61 FA: visible outside `[a = A]` {a, h}, `[_a = A]` none, `[_ = A]` none; sabotage s1 caught); the run line of statement 3 is predfix61's.
- a filter operand's labels are visible like any others (the draft R.1.13, filter-captures not adopted) — UNTESTED.
- his remark of 2026-11-19 ("it might be more that private labels are only visible in a binding scope") — already ruled as statement 1 (recorded as a recollection, nothing new).
- (pure-label) `pub` shows the labels `a`, `h` and the one capture `h`; `year` (`_v`) and `[d = digits] & (d: <100)` show no capture; `capture("d", /\d+/)` shows `d` (python `re` agrees on its groups) — SUPPORTED as rule-as-code (predscope_model.py CAPT; sabotage s2, a label counted a capture, and s3, a `_` label exported, caught).
- (ANS-5, the manager's) a source is a path of names, each step passed by the previous one, metadata by the same rule — SUPPORTED as run (docs/dev/lanes/predfix82_evidence/ predfix82_model.py PATHS, `pub.a.h`, `pair.b.x`, `days.w.index`; sabotage s8 caught); a `_x` part label closes its part (docs/dev/lanes/predfix82_evidence/ predfix82_model.py CLOSEDX; sabotage s2 caught)
- (review r83 D3) ONE statement of the implicit label: an unlabelled use carries the implicit label of the binding's name, protected (statement 2; core/labels/paths and binding-prefix point at it; the three equivalences `[_A = A]`, `[A = A]` exporting nothing and "as if `[=chars]`" retired for it) — a reading; SUPPORTED as run (docs/dev/lanes/predfix83_evidence/ predfix83_model.py OWNUSE, OUTSIDE; sabotage s5, s6 caught).
- (review r83 D7) the definition's OWN names enumerated once in statement 3: a group in its literals, a part label it writes, a label its export list takes — a reading; SUPPORTED as run (docs/dev/lanes/predfix83_evidence/ predfix83_model.py GRID: export-list cells read bare inside, `[(=year) = i1] & (year: ..)`).
- (review r83 D13) `_` by grain: a `_` label private, a `_` part label protected, the bare `_` a leave-out's unusable name — a reading; UNTESTED (wording; the three forms run in preddef ANALOGY).
- (review r83 D15, NOW part) `[=A]`, read `[A = A]`, in the table of the ways a part is used: public under its own name — a reading (core/labels/paths); SUPPORTED as run by preddef_model.py as `[A = A]` (`pub.A.h`).
evidence: preddoc3a_model.py EXP (the draft's PART TB (2) line; printed answers reproduced; `[2-9]\d{3}` agrees). PARTS TA, TB of predspec291. predfix61_model.py FA (statement 3's line and the closing parts).
history:
- 2026-11-18: the proposal (labels seen only if exported), the export-scope discussion, the ruling, the clarification of statement 6 and `[_ = A]`.
- 2026-11-19 (lane preddoc5): the slug filter-captures moved here from core/filters/kinds: it is closed by export-rule, which this piece states (review r59 PLACE-4).
- 2026-11-19 (lane preddoc6, review r60 COLD-15): the example names its program (`year`, the final expression); before it printed only the binding, which by core/operators/statements is not a program. Answers unchanged (preddoc6 PART EX).
- 2026-11-19: hole-export ruled; the statement until then: "A label is public unless its name begins with `_`; outside a binding its public labels and its public part labels are visible." From the merged question piece: review r54 P29-13 asked it; the T-a surprise (PART TA of predspec291) was its ground.
- 2026-11-19 (lane predfix61, review r61 F-A, F-B, F-J (RUNOWN-6)): statement 3 contradicted statements 6 and 7 (a `[_a = A]` part's public `h` was "visible inside" and so outside, less only `_a`) and stated the manager's reading (a) as the ruled body. The statement until then: "A label is public unless its name begins with `_`; outside a binding every public label visible inside it is visible, a part's labels passing through a hole and the sequence operator alike." Statement 3 until then: "Outside a binding, what is visible is what is visible inside it, less the private names: the public labels of everything written or used there, read as labels are, and its public part labels, a part's public labels also reached by path through its part label. `B1 := isodate SEQ "!"` and `B2 := /${isodate}!/` both show `year`." (`isodate` was defined nowhere; the run line printed was the private-label program's). Now: the ruled part ("both pass through"), the closing parts (reading (b)), the flat read marked a reading with its owner question flat-read-outside, a defined binding and a run line.
- 2026-11-21 (lane predscope, pure-label folded): statement 5 until then: "The caller's captures are what is visible from the top-level program by these rules." Now the CAPTURES visible from the top-level program (the groups in rx text and the capture forms); `[x = A]` makes a label and no capture. Bullets added: the `_` labels in his words; `pub` and `year` with their captures. Status date 2026-11-19 to 2026-11-21. Every printed line that shows label values in parentheses shows LABELS and stands.
2026-11-22 (lane predbound, R-3, label-reference ruled): statement 3 gains one sentence, the spelling revised by core/labels/paths/label-reference (hole-export); the lines are left for the next lane's sweep.
- 2026-11-22 (lane predref, label-reference sweep and helper-captures fold): statement 3 until then, its last three sentences, verbatim: "Read flat from outside, they are read as labels are inside (ruled: core/labels/export/flat-read-outside). `pub := [a = A] SEQ "!"` and `/${A}!/`, A := `/(?<h>\d)/`, both show `h`; `[_a = A] SEQ "!"` shows none. Its spelling is revised by core/labels/paths/label-reference (ruled): a passed label is referenced with its source." Now: a passed label is referenced with its source (`pub.h`) and read as labels are inside. Statement 5 gains the label-only group and the provided bodies. The line "Statement 3" re-spelled `pub & (pub.h: <5)`, answers unchanged (docs/dev/lanes/predref_evidence/ predref_model.py RESPELL). Status date 2026-11-21 to 2026-11-22.
- 2026-11-22 (lane predfix82, review r82 ANS-5; record "2026-11-22 MANAGER — review r82 (predfold1122): dispositions ruled; two corrections of record entries (no owner words)"): statement 3's bullet: a source is a path of names, each step passed by the previous one (the manager's reading, run); the lines "Statement 3, a path" and "Statement 6" added (predfix82 PATHS, CLOSEDX).
- 2026-11-22 (lane preddef, default-export folded; record "2026-11-22 OWNER RULING — default-export: protected"): statement until then: "A label is public unless its name begins with `_`; a part's public labels pass out of a binding through a hole and the sequence operator alike, unless a `_` part label closes them." Statement 2 until then: "Inside a binding, the public labels of everything written or used there are visible, read as labels are (last mention; an ambiguous reference is the error)." Statement 3 until then, verbatim: "Outside a binding, the public labels of every part written or used there pass through, a hole and the sequence operator alike, with its public part labels; a part's public labels are also reached by path through its part label (`pub.a.h`: a source is a path of names, each step passed by the previous one, a member's metadata by the same rule; the manager's reading, run: the line "Statement 3, a path"). A part under a `_` part label, or `[_ = A]`, passes none of its labels (statements 6, 7; run: the line "Statement 6"). A passed label is referenced with its source, the binding's name or a part label (`pub.h`: core/labels/paths/label-reference), and read as labels are inside (core/labels/export/flat-read-outside). `pub := [a = A] SEQ "!"` and `/${A}!/`, A := `/(?<h>\d)/`, both show `h`; `[_a = A] SEQ "!"` shows none." (REVERSED for `/${A}!/` by default-export.) Statement 5 is marked "(awaits capture-export)" (new open piece core/labels/export/capture-export). The bullet "`pub` below shows the labels `a` and `h` and the one capture `h`; `year` shows no capture (run)." folded into statement 3 (`a` and `h`); its capture half (predscope CAPT) stands in this entry's readings. The backreference and filter-operand bullets joined, unchanged in content. New: his analogy as a four-row table (record "2026-11-22 OWNER, an analogy to validate: the four ways a part is used, as C++ access levels": "Analogy, c++, please validate: [a = A ] is making the labels from A public to local and later bindings. [_a = A ] is making the labels from A protected and available locally but not exported to later bindings. [A ] (A alone, default) also makes the labels protected but with different access locally. [_ = A] makes the labels private to A and not accessible locally to the binding."); the lines "Used alone, inside" and "Used alone, from outside". Readings tested (preddef_model.py PROTECT, ANALOGY): (a) "used alone" as `[_A = A]` with the local name `A` — SUPPORTED as run; (b) what a binding exports: its own text's labels and, through a public part label, that part's exports by path (`pub.a.h`) — SUPPORTED, with the lane's addition that the same labels are read by name (`pub.h`, statement 3 kept for a labelled part: the ruling reverses it "for an unlabelled part" only) — a reading; (c) a read from outside of a label only a part used alone holds is a compile error — SUPPORTED as run (sabotage s1 caught). (f) array-in-piece unchanged: inside the binding a part used alone has its settings seen (`some((A.h: "7"))`), and from outside only the binding's own `h` is read — SUPPORTED as run (preddef_model.py ARRAY).
- 2026-11-22 (lane preddef, export-list folded; record "2026-11-22 OWNER RULING — export-list: yes"): the analogy table gains the list form's row; a bullet answers his question "some labels but not others" (by part, by `_` on a group, by the list).
- 2026-11-22 (lane predfix83, review r83 D1, D3, D6, D7, D10, D13, D15, A6; record "2026-11-22 MANAGER — review r83 (preddef1122): dispositions ruled; one correction; idiom-confirm closed on default-export (no owner words)"): statement 1 until then: "A private label is visible only inside the binding it is written in." Statement 2 until then: "Inside a binding the public labels of everything written or used there are visible, read as labels are; a part USED ALONE (no part label) is reached by its own name, `A.h`, as under `[_A = A]` (a reading; the line "Used alone, inside")." Statement 3 until then, verbatim: "Outside a binding, what passes out is what it EXPORTS: the public labels its own text writes (a group in its literals, a part label) and, through a public part label, the labels that part exports, by path (`pub.a.h`, each step passed by the previous one, a member's metadata alike) and by name (`pub.h`) (readings; run: the lines "Statement 3"). A part used alone exports none of its labels, through a hole and the sequence operator alike; nor does a part under a `_` part label or `[_ = A]` (statements 6, 7); a read from outside of a label only such a part holds is a compile error (the line "Used alone, from outside"). It is referenced with its source and read as labels are inside (core/labels/paths/label-reference, core/labels/export/flat-read-outside). `pub := [a = A] SEQ "!"` shows `a` and `h`; `/${A}!/`, `A SEQ "!"` and `[_a = A] SEQ "!"` show none." Statement 5 until then ended "`[x = A]` and the label-only group (a provided body's) make none (awaits capture-export)". The filter bullet until then ended "a filter operand's labels are visible as any (a reading)". Now: D3 the one statement of the implicit label (statement 2, the dropped "(last mention; an ambiguous reference is the error)" restored, D10); D7 the own names enumerated; D6 reading (c) marked; A6 "A call exports what its body exports"; D10 statement 5 without "(a provided body's)" and the filter bullet with "visibility goes by export, not by role"; D13 statement 1 names the three `_` grains; D15 the `[=A]` row; the "Some labels but not others" bullet moved to core/labels/export/export-list (it answers his question there); D1 the `rejected:` items marked revived and the hole-export rulings item marked. Answers unchanged (docs/dev/lanes/predfix83_evidence/ predfix83_model.py SWEEP).

## core/labels/export/flat-read-outside — A flat read of a part's label from outside
slugs: flat-read-outside
rulings:
- 2026-11-22 "default-export: protected" (record: "2026-11-22 OWNER RULING — default-export: protected"); a label only a part used alone holds is not exported: outside it is no label
- 2026-11-22 "label-reference: required. we can relax it later as you say although i'm not inclined to." (record: "2026-11-22 OWNER RULING — label-reference: required"); what a flat read meant is what `binding.x` means (the manager's reading, told to him)
- 2026-11-21 "flat-read-outside: a" (record: "2026-11-21 OWNER RULING — flat-read-outside: a (a flat read outside a binding follows the inside rules)"); (a) as put to him: "Flat reads follow the inside rules. Both examples stand as shown; the path is there when you want to say which part."
- 2026-11-19 "they have to work the same. Agree both pass through." (record: "2026-11-19 OWNER RULING — hole-export: both pass through; and a question on the array of a label under composition"); the ruled part of statement 3; it does not say how a flat read from outside resolves; reversed for an unlabelled part by default-export (2026-11-22)
rejected:
- (b) a flat read of a part's labels from outside is a compile error, the path required (his sentence of 2026-11-19: "I can't access x y z flat because it's ambiguous and therefore an error. So it's b.x or a.b.x.") — by owner ruling — flat-read-outside: a; both programs of the piece would be refused (predfix61 FB). Its refusal of the bare read is revived by label-reference (2026-11-22, the path through the binding required); its ambiguity ground stays rejected (the read is the last mention).
- (c) legal across `|`, an error where two parts in a sequence both set the name (the manager's third candidate when asked 2026-11-21) — by owner ruling — flat-read-outside: a.
readings:
- what a flat read MEANT is now what `binding.x` means: `pair.x` and `date.v` give the two printed lines unchanged (the manager's reading of the label-reference entry) — SUPPORTED (docs/dev/lanes/predref_evidence/ predref_model.py RESPELL: each old line, read bare as before, against the re-spelled program, the same answers; the bare spelling now refused, SCAN)
- a part label inside the binding reached through the binding's name (`pair.b.x`) — UNTESTED (lane predref's reading; the model gives a binding's prefix only to the labels a part surfaces)
- (a) reads outside a binding follow the inside rules (the manager's reading (a) of hole-export) — RULED 2026-11-21, no longer a reading; spelled `binding.x` since label-reference (2026-11-22), the bare read a compile error; the answers RUN (predfix61 FB; sabotage s2 caught).
- (review r83 A4, the manager's reading) a read from OUTSIDE a binding sees its EXPORTED settings only; a source the binding keeps protected neither supplies a value nor makes an `&` ambiguity — SUPPORTED as run (docs/dev/lanes/predfix83_evidence/ predfix83_model.py OUTSIDE: `pub.h`, pub := `[a = A] SEQ A`, reads the first digit (the line "The exported setting only"); `B.a`, B := `A & /(?<a>\d)/`, legal from outside while the bare `a` inside B is the ambiguous reference; sabotage s5 caught).
evidence: predfix61_model.py FB (both lines of candidate (a); candidate (b) refuses both programs).
history:
- 2026-11-21 (the manager, one ruling): flat-read-outside RULED (a). Status `open flat-read-outside 2026-11-19` to `ruled 2026-11-21`. Statement before: "Outside a binding, is a part's public label read flat (`x`, not `b.x`) under the inside rules, or is a flat read of a part's label an error, the path required?" Its candidates before: "(a) a flat read outside a binding follows the inside rules (the lines below); (b) a flat read of a part's labels from outside is a compile error; the path (`b.x`, `m.v`) is required (no line: refused)." His question back the same day ("so the read is based on match not group?") and the answer told him are in the record.
- 2026-11-19 (lane predfix61, review r61 F-B, RULING-7): a new open sub-piece at the manager's ruling of review r61. The owner's words in the hole-export message, whole for this point: "Here's the issue: if I have [a = ([ b = rx]|[c = rx])] where rx has labels x y z, this would mean that a b c x y z are all flatly visible. I can't access x y z flat because it's ambiguous and therefore an error. So it's b.x or a.b.x. In practice there may not be ambiguity, but is having all those symbols an issue? I'm saying no." The manager's correction, told to him the same turn (record, that entry): "His "I can't access x y z flat because it's ambiguous and therefore an error" is NOT what the rules as defined say for an alternation: the ruled ambiguity is across `&` only ...; across `|` the branch taken sets the label and a bare read is legal". He did not answer the correction; his later "I can't think of a problem with the existing labeling rules so let's move on." (record: "2026-11-19 OWNER RULING — array-scope: the array of a label is by the scope of the entire rx; a part label limits it") is a direction, not an answer to it (the manager's ruling of review r61).
2026-11-22 (lane predbound, R-3, label-reference ruled): a bullet: its spelling is revised by core/labels/paths/label-reference; the statement and lines are left for the next lane's sweep (the manager's R-3).
- 2026-11-22 (lane predref, label-reference sweep and helper-captures fold): heading "A flat read of a part's label from outside" to "A part's label read from outside through its binding" (the tag kept). Statement until then: "Outside a binding a part's public label is read flat (`x`, not only `b.x`) under the inside rules." Its second and third bullets until then: "A flat read is by NAME: what the path that matched left in it. The path (`b.x`, `m.v`) says which part's group (core/labels/paths)." and "Its spelling is revised: a label not written in the referencing definition is referenced with its source (core/labels/paths/label-reference, ruled); the lines below are re-spelled by the next lane." Lines re-spelled: `pair & (x: <5)` to `pair & (pair.x: <5)`, `date & (v: <5)` to `date & (date.v: <5)` (docs/dev/lanes/predref_evidence/ predref_model.py RESPELL). Status date 2026-11-21 to 2026-11-22.
- 2026-11-22 (lane predfix82, review r82 ANS-5; record "2026-11-22 MANAGER — review r82 (predfold1122): dispositions ruled; two corrections of record entries (no owner words)"): the `pair.b.x` bullet marked the manager's reading; the line "Through a part label inside the binding" added (predfix82 PATHS).
- 2026-11-22 (lane preddef, default-export folded; record "2026-11-22 OWNER RULING — default-export: protected"): statement until then: "Outside a binding a part's public label is read through the binding's name (`pair.x`), by name, under the inside rules: what a flat read `x` meant." New bullet and lines: his example of the day (record "2026-11-22 OWNER, discussing the analogy: `B := A & A`, `C := B & (B.a: 9)`: "here B.a is always an error""): B exports no `a`, so `B.a` is no label, plain read and group question alike (the manager's check in the record entry "2026-11-22 OWNER, discussing the analogy: `B := A & A`, `C := B & (B.a: 9)`: "here B.a is always an error"", no letter; cited as "reading (g)" until review r83 D6; SUPPORTED as run, preddef_model.py EXAMPLE, and by its reason, predfix83 EXAMPLE); before the ruling the plain read was an error as an ambiguous reference across `&` and the group question was legal (that entry's check); now both are errors for one reason. `B := [x = A] & [y = A]`: `B.x.a`, `B.y.a` printed in three modes.
- 2026-11-22 (lane predfix83, review r83 A4, D6; record "2026-11-22 MANAGER — review r83 (preddef1122): dispositions ruled; one correction; idiom-confirm closed on default-export (no owner words)"): a bullet and the line "The exported setting only" (A4); the bullet on a label only a part used alone holds marked the manager's reading (c) (D6); the history's "reading (g)" corrected to the record's check, which has no letter (D6). predfix82's engine answered `pub.h` by the last mention, the protected use's; preddef's by the exported use, with no sentence deciding it and no printed line (review r83 A4).

## core/labels/export/caller-ambiguous — What the caller gets for an unreferenced shared capture
slugs: caller-ambiguous read-out
rulings:
- 2026-11-18 "The caller's captures: agree" (record: "2026-11-18 OWNER, export-scope discussion, third exchange")
- 2026-11-18 "export-rule: Agee and add [_a = A] is a private reference that wouldn't export at all" (record: "2026-11-18 OWNER RULING — export-rule: public unless `_`; a binding shows its own public labels and its public part labels")
- 2026-11-21 "i agree that captures are explicitly written either in literal form or using a macro like capture()." (record: "2026-11-21 OWNER RULING — pure-label: captures are written explicitly; a label is made a capture afterwards too; `_` labels never export; three examples of what a definition may name"); narrows statement 5 from labels to captures
rejected:
- (b) h absent from the captures; (c) the last mention's value (the right side's); (d) the left side's value — by owner ruling — export-rule statement 5 (the caller's captures follow the program's rules, where a shared public name is an ambiguous reference).
readings:
- what label-reference and helper-captures change: the program never reads h bare across A & B; a helper's internal label is no capture, so two helper calls no longer raise the question (lane predref's reading, from the two rulings; the brief's reading (f)) — UNTESTED (a statement about which programs raise the question; the example's h is written in rx text in both parts and is unchanged)
- the record's export-rule discussion: "a name two parts both make public is an ambiguous reference for the caller as for the program", pending a ruling (the manager's reading of "The caller's captures: agree") — favours (a) or (e); not ruled.
- the question narrowed to a CAPTURE two parts both make (a label no capture makes never reaches the caller); the example's h is written in rx text in both parts, so the question and its run are unchanged (the lane's reading of pure-label) — UNTESTED as a rule; the spans are preddoc3a CALL's.
evidence: preddoc3a_model.py CALL (the spans; the draft's PART R47 B13 printed the same spans under every candidate, reproduced).
history:
- new piece (lane preddoc3a): the slug was on core/model/modes; the draft R.1.13 leaves it "NOT DEFINED".
- 2026-11-19 (lane preddoc4): narrowed to (a) against (e); (b)-(d) to `rejected:` by export-rule statement 5; the record's slug read-out (path-and-ambiguity's second corner) homed here (review r59 RULING-3). The base's slug stays caller-ambiguous.
- 2026-11-21 (lane predscope, pure-label folded): heading "What the caller gets for an unreferenced shared label" to "... shared capture"; statement before: "For a public label two parts both set that the program never references, is the caller's ambiguous reference a compile error or an error when the caller reads it?" Body before: "The rule (export-rule, statement 5): the caller sees what is visible from the top-level program, so a name two parts both make public is an ambiguous reference for the caller as for the program. Open: WHEN it is refused." Status date 2026-11-19 to 2026-11-21.
- 2026-11-22 (lane predfix77, review r77 A8; record "2026-11-22 MANAGER — review r77 (predfold1121): dispositions ruled (no owner words)"): a sentence names the duplicate-name case (two groups of one name in ONE literal under `(?J)`, PCRE's capture its first set group: core/labels/labels-vs-captures).
- 2026-11-22 (lane predref, label-reference sweep and helper-captures fold): a paragraph: what the two rulings of the day change for the question (a reading). Status date 2026-11-21 to 2026-11-22. No line moves.

## core/labels/export/capture-export — A capture inside a part used alone
slugs: capture-export
rulings:
readings:
- the question as the manager put it with the ruling (record "2026-11-22 OWNER RULING — default-export: protected (a part used alone is available inside the binding and is not exported)": "export statement 5 gives the caller the CAPTURES visible from the top-level program: does a capture written in rx text inside a bare-used part two bindings down still reach the caller (as in PCRE), or does it follow the labels") — the piece states it; neither answer applied.
- the match is the same under both candidates; (a) gives the caller no capture for `q`, (b) gives `h` — RUN as the model's capture list (preddef_model.py CAPTEXP: the groups written in rx text against the labels visible at the top-level program); the caller's capture output itself is not modelled.
evidence: docs/dev/lanes/preddef_evidence/ preddef_model.py CAPTEXP.
history:
- 2026-11-22 (lane preddef, default-export folded): a new open piece, at the manager's brief (the slug named in the ruling entry above, "NOT STATED by his words, to be asked, neither answer applied").

## core/labels/export/export-list — One label of a part, by a list
slugs: export-list
rulings:
- 2026-11-22 "Export list: yes. I will say that the form is the same but one is bindings and one is labels. We should clarify either they are the same thing but different targets or note their space." (record: "2026-11-22 OWNER RULING — export-list: yes")
- 2026-11-22 (class: AGREEMENT) "Agree caveat bindings used to scope labels (A.a: 8)" (record: "2026-11-22 OWNER, on the two name spaces: "Agree caveat bindings used to scope labels (A.a: 8)"")
readings:
- his question before it, whole: "Question, can I somehow export some labels but not others. Like year only from isodate" (record "2026-11-22 OWNER, a question after default-export: "can I somehow export some labels but not others. Like year only from isodate""); his proposal, whole: "I meant if isodate was defined and I wanted to reexport year only. [d = isodate] exports all. How about this: [(=year) = isodate]" (record "2026-11-22 OWNER PROPOSAL — re-exporting one label of a defined part: `[(=year) = isodate]`").
- (a) one form, the named list, two targets decided by where it stands; bindings and labels two name spaces (stated once in core/modules/binding-list) — a reading, his direction; UNTESTED (wording). Marked in the base as the manager's reading (a) (review r83 D6).
- (b) the ruled list forms carry over: rename, several, all, all but one — SUPPORTED as run for one, renamed, all, all but one (preddef_model.py LIST); several UNTESTED.
- (c) a listed label is an alias, same settings, no new capture — UNTESTED (the model gives the alias the part's group; captures are not modelled).
- (d) a listed name the binding also writes is the same label, last mention — UNTESTED.
- (e) the list gives the part no path name — SUPPORTED as run (`date.isodate.month` refused, LIST).
- (f) only an exported label can be listed — SUPPORTED as run (`[(=hour) = isodate]` refused at the list, LIST; sabotage s6, the list exporting an unlisted label, caught).
- (review r83 D16, the manager's) two lists that name one label give the same label, the last mention — SUPPORTED as run (docs/dev/lanes/predfix83_evidence/ predfix83_model.py LISTCOLL: `d.year`, d := `[(=year) = i1] SEQ [(=year) = i2]`, reads i2's; sabotage s11, the first mention, caught).
- (review r83 D16, the manager's) the cross case `(=year) := isodate`, a binding list over a part's labels, is a compile error for now — UNTESTABLE in the model (it parses no binding list left of `:=`); a reading on the text ("on any map" admits it; the label target is the export list's).
- (review r83 D18) inside a binding that lists a part, the part's own prefix (`isodate.year`) and a listed part label's path (`q.a.h`) are compile errors — a reading; SUPPORTED as run (docs/dev/lanes/predfix83_evidence/ predfix83_model.py LISTCOLL; the reason is binding-prefix's A5 reading: a labelled use, a list included, is reached by its label only).
- (review r83 A2) a list through a call whose body uses its argument alone names a label the call does not export: a compile error at the list (argument-default is ruled since: no candidates; review r84 C2) — SUPPORTED as run (docs/dev/lanes/predfix83_evidence/ predfix83_model.py LISTCALL: `[(=d) = B(A)]`, `[(=l) = atomic(B | A)]` refused (since wrapper-export atomic passes its argument's labels on, so that refusal holds by "a part used alone in it nothing", lib/convention/argument-labels: review r84 D3); the body's own `d` listed legal; sabotage s4 caught); (f) above re-run there.
- (review r84 D3) a list through a call that passes its argument's labels on takes them: `[(=l) = atomic(/(?<l>\d)/)] & (l: <5)` legal, reading the group written in the argument — SUPPORTED as run (docs/dev/lanes/predfix84_evidence/ predfix84_model.py LISTATOM, the line "Through a call that passes its argument's labels on").
evidence: docs/dev/lanes/preddef_evidence/ preddef_model.py LIST.
history:
- 2026-11-22 (lane preddef, R-1 and R-2 of its rulings file): a new ruled piece; the analogy table of core/labels/export gains its row; core/modules/binding-list states the one form with two targets and his caveat; core/conditions/form gains the caveat; core/spellings/placeholders gains its row.
- 2026-11-22 (lane predfix83, review r83 A2, D6, D16, D18; record "2026-11-22 MANAGER — review r83 (preddef1122): dispositions ruled; one correction; idiom-confirm closed on default-export (no owner words)"): bullets: two lists of one label (D16), the cross case (D16), the part's own prefix and a listed part label's path inside the binding (D18), the bullet "Some labels but not others" moved here from core/labels/export; the refusal line "Through a call that uses its argument alone" (A2); his caveat classed AGREEMENT and reading (a) marked (D6).
- 2026-11-23 (lane predfix84, review r84 D3; record "2026-11-23 MANAGER — review r84 (predspot1122): the dispositions, ruled with the 2026-11-23 rulings in hand; no owner words"): the refusal line until then ended "; `[(=l) = atomic(B | A)]` alike: the call exports no such label, so the list cannot take it)." (atomic used its argument alone before wrapper-export); now the B case keeps that reason and the atomic case names its own (a part used alone in the argument exports nothing); the positive line "Through a call that passes its argument's labels on" added.

## core/labels/paths — Part labels and paths
slugs: path-and-ambiguity
rulings:
- 2026-11-22 "default-export: protected" (record: "2026-11-22 OWNER RULING — default-export: protected"); a binding's name used alone is local to the definition that uses it and exports nothing
- 2026-11-22 ""binding-prefix" 1. yes. 2. i agree with your lean (a)" (record: "2026-11-22 OWNER RULING — binding-prefix: 1 yes"); a binding's name is a prefix of its own (core/labels/paths/binding-prefix)
- 2026-11-21 "i agree that captures are explicitly written either in literal form or using a macro like capture()." (record: "2026-11-21 OWNER RULING — pure-label: captures are written explicitly; a label is made a capture afterwards too; `_` labels never export; three examples of what a definition may name"); `[x = A]` makes a label and no capture
- 2026-11-17 (class: STATEMENT) "setting labels is just the label using the group-label-not-capture syntax" (record: "2026-11-17 OWNER, three points on labels")
- 2026-11-18 "so I agree the last reference" (record: "2026-11-18 OWNER on path-and-ambiguity: the part label used twice is RULED; the read-out is open")
- 2026-11-18 "Naming [x = A] only disambiguates scope, it doesn't give additional access" (record: "2026-11-18 OWNER, export-scope discussion, third exchange")
- 2026-11-17 "label-flow: 1. propose: it is an error to ambigously reference a label." (record: "2026-11-17 OWNER PROPOSAL — label-flow: an ambiguous REFERENCE is the error")
- 2026-11-22 (class: STATEMENT) "also: [ c = B(A) ] does not allow c.A" (record: "2026-11-22 OWNER, on closed-argument: "i thought you'd lean to (a). what would A.d mean if d no longer was visible?"; and "[ c = B(A) ] does not allow c.A""); a call's label reaches no argument by the argument's name
rejected:
- a part label used twice is an error — by owner — "I mean, harmless I guess ... so I agree the last reference".
readings:
- `x.h` follows the one label rule inside A; an ambiguity judged where the reference is written; `alt.x[1]` legal (the draft R.1.13) — UNTESTED.
- the read-out corner (what a caller gets) — core/labels/export/caller-ambiguous.
- the ground of "[ c = B(A) ] does not allow c.A": inside B the argument is the parameter, "a binding variable not a label" (2026-11-21, nested-scope example 1), so the call's label holds no part named for the argument (the manager's answer in the record entry) — SUPPORTED as run of the reading (docs/dev/lanes/predcall_evidence/ predcall_model.py CA: `[c = B(A)] & (c.A.d: <5)` refused, `c` passes no label `A.d`; sabotage s6 caught)
- his `[=year]` (a placeholder in "an EXERCISE asked for", 2026-11-21) is `[year = year]`, the part label named for the binding it holds (the manager's reading, the `=x` shorthand of the binding list in a third place, not asked) — UNTESTED (a spelling).
- (ANS-4, the manager's) a path to a label not visible through its source is a compile error, a typo'd path alike — SUPPORTED as run (docs/dev/lanes/predfix82_evidence/ predfix82_model.py PATHS: `c.e`, `c.A.d` refused by the visibility rule)
- (review r83 D4 (i), the manager's) a part label over an EXPRESSION written in a binding reads, inside the definition, the labels visible in it by the inside rules, and exports outward only what the expression's own text exports — SUPPORTED as run (docs/dev/lanes/predfix83_evidence/ predfix83_model.py EXPR: inside X `ab.l` legal; from outside `X.ab.l` refused for X := `[ab = B | A] SEQ "!"`; X := `[ab = A SEQ /;(?<l>\d)/] SEQ "!"` exports the literal's `l` only, the line "Outward, what the expression's text writes"; sabotage s8 caught).
- (review r83 D4 (ii)) a macro's parameter is not a part whose labels the body may name (ruled 2026-11-21, bare-nested-scope; statement 2 of core/labels/export does not license `rx.d`) — SUPPORTED as run (docs/dev/lanes/predfix83_evidence/ predfix83_model.py PARAM: `B(rx) := /${rx}/ & (rx.d: <5)` refused at the binding; sabotage s9 caught).
evidence: preddoc3a_model.py PATH (the draft's PART LF line; printed answers reproduced; `[01]\d` agrees) and PATH2 (his corner 1: the last mention); sabotage s18 caught.
history:
- 2026-11-18: corner 1 ruled; corner 2 (the read-out) went to filter-captures, export-scope, export-rule.
- 2026-11-21 (lane predscope, pure-label folded): the first bullet until then (the draft §3.1's reading): "`[x = A]` is the group form `(?<x>A)` read as a label; inside pattern text a named group is the same thing." It was wrong as to capture. The `[=year]` bullet added. Status date 2026-11-18 to 2026-11-21.
2026-11-22 (lane predbound, R-1, binding-prefix ruled): a pointer bullet to the new sub-piece; status date 2026-11-21 to 2026-11-22; no line moves.
- 2026-11-22 (lane predref, label-reference sweep and helper-captures fold): the ambiguity bullet's program `A & (B & (h: ..))` (a bare h not written in it) re-spelled with the parts written in place, `/(?<h>\d)/ & (/(?<h>\d)/ & (h: ..))`, and the binding form `A & (B & (B.h: ..))` named beside it; the bullet stays a reading, UNTESTED as before.
- 2026-11-22 (lane predcall, call-prefix case 1 folded): the pointer bullet names the macro's name beside the binding's (core/labels/paths/call-prefix); a bullet added for his statement "[ c = B(A) ] does not allow c.A" with its ground (a reading, run); no line moves.
- 2026-11-22 (lane predfix82, review r82 ANS-2b, ANS-4; record "2026-11-22 MANAGER — review r82 (predfold1122): dispositions ruled; two corrections of record entries (no owner words)"): "as if a part label `[A = A]`" gained "for one use"; `c.A.d` "is refused, run" now names its rule; a bullet: a path to a label not visible through its source is a compile error, the never-pass warning for a visible label no path sets (the manager's reading).
- 2026-11-22 (lane preddef, default-export folded; record "2026-11-22 OWNER RULING — default-export: protected"): the prefix bullet gains: used alone in a binding it is local there and exports nothing (core/labels/export). Its line until then ended "core/labels/paths/call-prefix." The shorthand bullet gains the manager's reading (d): `[=A]` is the short way to export a part under its own name, SUPPORTED as run with `[A = A]` (preddef_model.py ANALOGY; the model does not parse `[=A]`).
- 2026-11-22 (lane predfix83, review r83 D3, D4, D9; record "2026-11-22 MANAGER — review r83 (preddef1122): dispositions ruled; one correction; idiom-confirm closed on default-export (no owner words)"): statement until then: "A part label `[x = A]` names part A; `x.h` is the label h as part A surfaces it, and a part label mentioned more than once names its last mention where the reference is written." ("surfaces" to "exports", D9.) The bullet until then: "A binding's name is a prefix of its own, as if a part label `[A = A]` for one use (used twice, a plain read is the compile error): core/labels/paths/binding-prefix; a macro's name at its call likewise: core/labels/paths/call-prefix. Used alone in a binding it is local there and exports nothing (core/labels/export)." Now it points at the one statement of the implicit label (core/labels/export statement 2, D3). Two bullets added (D4 (i), (ii)) with the line "Outward, what the expression's text writes".

## core/labels/paths/binding-prefix — A binding's name as a label prefix
slugs: binding-prefix
rulings:
- 2026-11-22 ""binding-prefix" 1. yes. 2. i agree with your lean (a)" (record: "2026-11-22 OWNER RULING — binding-prefix: 1 yes"); part 1, a group question through a binding's prefix reads the settings of every use; part 2, (a), a plain read through it with the binding used more than once is a compile error that says to label the part
- 2026-11-22 (class: LEAN) "binding in prefix: i like your read on this except that perhaps it does refer to all. chars SEQ ":" SEQ chars & (count(chars.ch): ==5) says all chars must total 5" (record: "2026-11-22 OWNER, on binding-prefix: "i like your read on this except that perhaps it does refer to all""); his example and "all"; the definition "as if written `[=chars]`" accepted, in his words "i like your read"
- 2026-11-17 (class: PROPOSAL) "A . B & (A.h: blah) error. A is a binding not a label and could be ambigous if its used multiple times in an expression" (record: "2026-11-17 OWNER PROPOSAL — label-flow: an ambiguous REFERENCE is the error"); his label-flow point 4, REVISED by the ruling: the error stays for a plain read with several uses
- 2026-11-22 (class: IDEA) "count-in-set: ok, thats fine. i think your value in the left part of condition as a fantastic addition so b. it suggests $h could go there which is also new. aside: perhaps we will need a syntax to declare the ch in chars. i am wonderings not for correctness but clarity. also, it suggests that bindings could be used under certain rules as label prefixes like chars.ch as that is clear here. chars seq ":" seq chars & (chars.ch: blah) would need defining. respond" (record: "2026-11-22 OWNER RULING — count-in-set: b"); part 5, where the idea first came: "bindings could be used under certain rules as label prefixes like chars.ch"
rejected:
- the last use only, for a group question through the prefix — by owner ruling — binding-prefix part 1 ("yes"); its line, run (predbound PREFIX; the record's pasted `last` line reproduced):
  The last use only (not the ruling): WHOLE `ab:cde` FAILS, `:abcde` HOLDS, `ab:cd` FAILS, `abcdef` FAILS / SEARCHED `ab:cde` FAILS / FIND-ALL `ab:cde 1:23456 xyz` [`ab:cde 1:23456`@0] (the same program)
- (b) a plain read through a twice-used prefix reads the last use — by owner ruling — binding-prefix part 2 ("i agree with your lean (a)").
- (c) a binding's name is never a path (the rule until then) — by owner ruling — binding-prefix.
- (e) a macro's name is not a prefix for now (`B(A)` gives no `B.x`), the manager's conservative reading of 2026-11-22 — by owner ruling — call-prefix case 1, "yes use the macro name as shown to qualify the label" (core/labels/paths/call-prefix).
readings:
- the ruling as run: his example `chars SEQ ":" SEQ chars & (count((chars.ch: anything)): ==5)` reproduces the record's pasted `all` line in every mode; a plain read `(chars.ch: "a")` and `$chars.ch` through the twice-used `chars` refused with "label the part" (predbound PREFIX; sabotage s18 caught).
- (a) a binding used as a part carries a part label of its own name; with ONE use `A & B & (A.h: <2)` answers as the printed `[aa = /(?<h>\d)\d/] & /\d(?<h>\d)/ & (aa.h: <2)` line — SUPPORTED (predbound PREFIX, the line "One use").
- (b) "used more than once" is counted in the definition the reference is written in — SUPPORTED as a run of the reading (predbound PREFIXRD: `X SEQ X`, X := `chars & (chars.ch: "a")`, is legal, `chars` used once in X; WHOLE against the direct split, 0 of 31 texts over `ab` differ).
- (c) an explicit part label mentioned twice is unchanged — SUPPORTED (predbound PREFIXRD: the printed line "A part label used twice" rebuilt, the same answers).
- (d) no access to anything private, nothing under `_` or `[_ = A]` — SUPPORTED as a run of the reading (predbound PREFIXRD: `year._v` and `[_ = A] & (A.h: <5)` refused; sabotage s19 caught). That such a reference is a COMPILE ERROR rather than an unset label is the model's choice, not stated.
- (f) a label and a binding of one name: which one `x.h` names is not stated — UNTESTED.
- (g) the error may relax to the last use later without changing an answer — UNTESTABLE (a statement about a later change; a refused program has no answers).
- (ANS-2d, the manager's) uses counted in the referencing definition's TEXT, before macros expand — SUPPORTED as run (docs/dev/lanes/predfix82_evidence/ predfix82_model.py TEXTUSES: `/${A},${A}/ & (A.d: <5)` refused, `pair(A) & (A.d: <5)` legal; sabotage s5, uses counted per lowering, caught)
- (ANS-2c, the manager's) the prefix reaches the uses written in the referencing definition's own text, not a use nested in another used binding — SUPPORTED as run (docs/dev/lanes/predfix82_evidence/ predfix82_model.py NESTED, the line "A use inside another used binding"; sabotage s6 caught)
- (ANS-6, the manager's) the index through sequenced uses in text order; through `&`-joined uses a compile error for now — SUPPORTED as run (docs/dev/lanes/predfix82_evidence/ predfix82_model.py INDEX; sabotage s9 caught)
- (DES-6, the manager's) a part label written in the definition wins over a binding's or macro's name, with the hide-label warning — SUPPORTED as run (docs/dev/lanes/predfix82_evidence/ predfix82_model.py HIDE; sabotage s11 caught)
- the second `&` operand's labels kept (EVID-2) — SUPPORTED as run (docs/dev/lanes/predfix82_evidence/ predfix82_model.py SECOND, `A & B & (B.h: <2)`; sabotage s3 caught)
- (review r83 A5, the manager's) a binding's own name reaches its UNLABELLED uses only; a labelled use is reached by its label and is not counted; where a part label written in the definition has the binding's own name, the label wins, with the hide-label warning — SUPPORTED as run (docs/dev/lanes/predfix83_evidence/ predfix83_model.py OWNUSE: `[a = A] SEQ A & (A.h: <5)` reads the unlabelled use, the line "The unlabelled use"; `[a = A] SEQ "!" & (A.h: <5)` refused; `[A = A] SEQ A`: `A.h` the label's, with the warning; sabotage s6 caught). The old engine refused `[a = A] SEQ A & (A.h: <5)` as "used 2 times" (ANSWERS CHANGED, the report).
evidence: docs/dev/lanes/predbound_evidence/ predbound_model.py PREFIX, PREFIXRD.
history:
- 2026-11-22 (lane predbound, R-1 of its rulings file, binding-prefix ruled): a new ruled piece. The brief's parked piece parked/ideas/binding-prefix, drafted in this lane and never delivered, is not made (the ruling replaced it).
- 2026-11-22 (lane predcall, call-prefix case 1 folded): reading (e) withdrawn by the ruling: the base's words until then, "a MACRO's name is not a prefix for now (`B(A)` gives no `B.x`)", became "a MACRO's name is a prefix too, under the same two rules (core/labels/paths/call-prefix)"; (e) and its run (predbound PREFIXRD) moved to `rejected:`. The status date stays 2026-11-22.
- 2026-11-22 (lane predfix82, review r82 ANS-2a, 2c, 2d, ANS-6, DES-6; record "2026-11-22 MANAGER — review r82 (predfold1122): dispositions ruled; two corrections of record entries (no owner words)"): the one-use read marked a reading (open idiom-confirm); uses counted in the text before macros expand; the prefix reaches the uses written in the referencing definition only; the index through `&`-joined uses a compile error for now; the part label wins with the hide-label warning; five lines added and one refusal line (predfix82 SECOND, CONTRAST, NESTED, INDEX, TEXTUSES). Statement unchanged.
- 2026-11-22 (lane preddef, default-export folded; record "2026-11-22 OWNER RULING — default-export: protected"): the definition bullet gains "local to the definition that uses it (exporting nothing: core/labels/export statement 3)". The nested-use bullet until then: "The prefix reaches the uses written in the referencing definition's own text, not a use nested inside another used binding, which its own path reaches (`X.D.h`) (a reading, run: the line "A use inside another used binding")." `X.D.h` is now a compile error (D used alone in X): the lines "X's use, labelled in X" (`X := [d = D] SEQ "!"`, `X.d.h`) and "X's use, used alone in X" added (preddef_model.py NESTED2). The line "A use inside another used binding" is unchanged.
- 2026-11-22 (lane predfix83, review r83 A5, D3, D17; record "2026-11-22 MANAGER — review r83 (preddef1122): dispositions ruled; one correction; idiom-confirm closed on default-export (no owner words)"): the bullet until then: "The definition he liked (a reading): a binding used as a part carries a part label of its own name, as if `[A = A]`, local to the definition that uses it (exporting nothing: core/labels/export statement 3); with ONE use `A.h` reads as `aa.h` does under `[aa = A]` (the lines "One use"): legal as a reading resting on label-reference ("required": the required form must be legal) and on his one-use examples (`(hits.hit: <5)`, `(h.hit: 3)`); open idiom-confirm (core/labels/paths/one-use-read)." Now: the implicit label points at core/labels/export statement 2 (D3); the one-use read is ruled by default-export (D17); a bullet on the unlabelled uses (A5) with the line "The unlabelled use", and the clause "a part label written in the definition wins over a binding's or a macro's name of one spelling, with the hide-label warning (core/labels/paths/call-prefix)" moved from the readings bullet into it.
- 2026-11-23 (lane predfix84, review r84 D4; record "2026-11-23 MANAGER — review r84 (predspot1122): the dispositions, ruled with the 2026-11-23 rulings in hand; no owner words"): the line "Counted in the text" ended "where `pair(A) & (A.d: <5)` writes it once (core/labels/paths/call-prefix)." — refused under the body `pair(p) := /${p},${p}/` since argument-default; now "where `pair(A) & (pair.d: <5)`, the list body, writes it once", the program printed in call-prefix's line "An argument used twice by the body".

## core/labels/paths/label-reference — A label is referenced with its source
slugs: label-reference
rulings:
- 2026-11-22 "default-export: protected" (record: "2026-11-22 OWNER RULING — default-export: protected"); statement 3, which this piece revised, is limited by default-export to what a binding exports
- 2026-11-22 "label-reference: required. we can relax it later as you say although i'm not inclined to. (i wrote then deleted an idea that if you defined isodate := ... above the binding then later usages of it in the same "program" could refer to isodate labels without qualifications but i'm not so sure of it so i will park it)" (record: "2026-11-22 OWNER RULING — label-reference: required"); RULED "required": a reference to a label not known textually at the reference carries its source; his stance, "we can relax it later ... although i'm not inclined to"; the idea he parks: parked/ideas/unqualified-after-definition
- 2026-11-22 (class: QUESTION) "label references: the remaining question is to whether it should be _required_ that the label is known textually at reference. ie should ch require chars.ch in the above example. i'm inclined to say yes. thoughts? also, value in conditions: why would (x,y): () form not allow values?" (record: "2026-11-22 OWNER, two points after binding-prefix: should a label be REQUIRED to be known textually at its reference"); the question raised with his lean
rejected:
- (b) a label from a used binding referenced bare, as before — by owner ruling — label-reference: required. Its line, the bare spelling read as before the ruling (predbound LABELREF):
  Bare, read as before the ruling: WHOLE `abc` HOLDS, `ab` FAILS / SEARCHED `abcd` `abc`@0 / FIND-ALL `abcdefg` [`abc`@0, `def`@3] (`chars & (count((ch: /(?s:.)/)): ==3)`)
readings:
- (e) no answer of any printed example changes, only spellings — SUPPORTED for every re-spelled printed line (docs/dev/lanes/predref_evidence/ predref_model.py RESPELL: each old line rebuilt from the program text at 915b47e64 read bare as before, against the re-spelled program; the same answers in every mode; DOC: each re-spelled line verbatim in the documents)
- every printed program of the three base files obeys the rule — SUPPORTED as a textual check (docs/dev/lanes/predref_evidence/ predref_model.py SCAN: every backtick program span is checked; each span still holding a bare borrowed label is on the model's LEFT list with its reason (a fragment, a quotation, a printed refusal, his own spelling); a planted bare read is caught, sabotage s1)
- the ruling as run: the bare `ch` in `chars & (count((ch: /(?s:.)/)): ==3)` refused, "reference it with its source"; `chars.ch` gives `length`'s printed line (predbound LABELREF; sabotage s20 caught); the documents' `(w.index: >= 2)` with `days` refused, `days.w.index` the same answers (predbound META).
- (a) "known textually": a group in one of the definition's literals or a part label it writes — the model's rule (predbound LABELREF, META), a reading.
- (b) any other label is reached through a binding's name (binding-prefix) or a part label — a reading; run for a binding (`chars.ch`, `days.w.index`) and for an argument that is a binding (`B(A) & (A.d: <100)` legal, `B(A) & (d: <100)` refused: predbound LABELREF).
- (c) the same for `$x` reads; rx text untouched — a reading; the model applies the rule to every name a condition or a `$` read names (predbound LABELREF).
- (d) the source of a label from a macro call's body, from an argument, from a typed parameter — NOT STATED by his words, to be asked; until then a call is labelled and an argument that is a binding is reached by its name (a reading).
- (e) no answer of any printed example changes, only spellings — SUPPORTED for the programs this lane wrote (predbound LABELREF: required against bare-as-before, 0 / 0 / 0 of 63 texts over `ab`; FIVE: `length` and `month_numbered` re-spelled, their printed lines unchanged; META); the other printed programs: the next lane's sweep.
evidence: docs/dev/lanes/predbound_evidence/ predbound_model.py LABELREF, META, FIVE; docs/dev/lanes/predspot_evidence/ predspot_model.py SWEEP (lane predspot).
history:
- 2026-11-22 (lane predbound, R-2): a new open piece, slug label-reference.
- 2026-11-22 (lane predbound, R-3, label-reference RULED "required"): open to ruled; the statement until then, verbatim: "Must a reference to a label not written in the text of the definition that makes it carry its source (`chars.ch`, not `ch`), (a), or may it stay bare, as today, (b)?"; the line "Bare, as today" moved to `rejected:`; `length`'s and `month_numbered`'s bodies, and every program this lane wrote, use the required form; the other printed programs are left bare for the next lane (the manager's R-3).
- 2026-11-22 (lane predref, label-reference sweep and helper-captures fold): the sweep: the bullets on the unstated sources point at the new open piece core/labels/paths/call-prefix; "the documents' other printed programs still read used bindings' labels bare; they are re-spelled by the next lane" replaced by the sweep's result; the reading on rule-sentence capitals added.
- 2026-11-22 (lane predcall, call-prefix case 1 folded): the bullet "Not stated by his words (open call-prefix: core/labels/paths/call-prefix): the source of a label from a macro call's body, from an argument, from a typed parameter; meanwhile the conservative forms below." became: a call's body through the macro's name or a label on the call (ruled), an argument and a typed parameter not ruled. Reading (d) above stands as asked and since answered for the call's body.
- 2026-11-22 (lane predfix82, review r82 RULING-3, RULING-9; record "2026-11-22 MANAGER — review r82 (predfold1122): dispositions ruled; two corrections of record entries (no owner words)"): the argument's source restated as ruled by closed-argument, only the typed parameter unruled; the plain idiom marked a reading on his silence (open idiom-confirm).
- 2026-11-22 (lane preddef, default-export folded; record "2026-11-22 OWNER RULING — default-export: protected"): two bullets gain a clause: an argument the body uses alone (core/labels/paths/argument-default); statement 3 "which default-export since limits to what a binding exports". Their text until then: "... from an argument that is a binding, through the binding where visible (ruled, core/labels/paths/closed-argument); from a typed parameter ..." and "- It revises core/labels/export/flat-read-outside and hole-export (core/labels/export statement 3), and his".
- 2026-11-22 (lane predfix83, review r83 D7, D17; record "2026-11-22 MANAGER — review r83 (preddef1122): dispositions ruled; one correction; idiom-confirm closed on default-export (no owner words)"): the readings bullet until then began: ""known textually" means a group in one of the definition's literals or a part label `[x = ..]` it writes" and ended "the plain idiom is included (`isodate & (isodate.year: ..)`; a reading taken on his silence; open idiom-confirm, core/labels/paths/one-use-read)". Now "known textually" points at the one enumeration of a definition's own names (core/labels/export statement 3, an export list's labels included, D7) and the plain idiom is ruled by default-export (D17).
- 2026-11-22 (lane predspot, argument-default folded; record "2026-11-22 OWNER RULING — argument-default: an error; and his reason: a label is to the SPOT in the pattern, a parameter is a template, not a piece of the pattern"): the call bullet's "where the body uses it alone, core/labels/paths/argument-default" to "where the body uses it alone, a compile error, core/labels/paths/argument-default".

## core/labels/paths/call-prefix — The source of a label from a call or an argument
slugs: call-prefix
rulings:
- 2026-11-22 "call-prefix. case 1. yes use the macro name as shown to qualify the label. 2. i'd say A.d is legal there. i'm trying to figure out if B(A) would ever remove the d. its possible it changes the answer to go through [ c = B(A) ] as B may defined d" (record: "2026-11-22 OWNER RULING — call-prefix, case 1: the macro's name qualifies a label of its body; case 2: "i'd say A.d is legal there", with a doubt he is working through"); case 1 RULED: the macro's name qualifies the labels its call surfaces (`hits(/\d+/) & (hits.hit: 3)`); case 2 his lean "i'd say A.d is legal there" and two thoughts he is working through, ruled after by closed-argument
- 2026-11-22 "closed-arguments: a" (record: "2026-11-22 OWNER RULING — closed-argument: a (where a macro closes its argument's labels, the caller's `A.d` is a compile error)"); case 2 then settled (revised by argument-default, below): `A.d` legal where `d` is visible through the call (core/labels/paths/closed-argument)
- 2026-11-22 "label-reference: required. we can relax it later as you say although i'm not inclined to." (record: "2026-11-22 OWNER RULING — label-reference: required"); the ruling that raised the question
- 2026-11-22 "argument-default: for me this is an error. I'm just trying to articulate why it's an error other than form. I get that it might not end up in the pattern. I think for me it has to do with whether or not it's definitively part of the pattern being constructed or if it's a parameter to it. B(rx) := you can't take a label against rx directly. You can take a label to the spot that rx gets laid into the regex. The label is not to the regex abstractly, it's to the spot in the pattern where the regex is being inserted. A parameter like rx in a call B(rx) cannot be labeled because it's not being placed into the pattern. It's not a piece of the pattern. It's a template of the rx that might be placed into the pattern." (record: "2026-11-22 OWNER RULING — argument-default: an error; and his reason: a label is to the SPOT in the pattern, a parameter is a template, not a piece of the pattern"); case 2 REVISED by it for a body using its argument alone: his lean "i'd say A.d is legal there" was on `C := B(A) & (d: <100)` with B(rx) := `/${rx}xx/`, now a compile error (review r84 C2; "settled" was the manager's word).
rejected:
- (1) of the conservative forms, "never by the macro's name" (`[h = hits(/\d+/)] & (h.hit: <5)` the only way to a call body's labels) — by owner ruling — case 1, "yes use the macro name as shown to qualify the label"; the labelled call stays legal.
- the manager's sentence for case 2, "They are the same label" (`A.d` and `c.d`) — by run — the record entry's two pasted lines differ when B sets a `d` of its own (A := `/(?<d>\d)/`, B(rx) := `/${rx}-(?<d>\d)/`: `7-3` FAILS through `A.d`, HOLDS through `c.d`); withdrawn by the manager in the record entry, reproduced here (docs/dev/lanes/predcall_evidence/ predcall_model.py RECORD).
readings:
- (a) binding-prefix's two rules carried to a macro's name (called once, a plain read legal; called more than once, a plain read the compile error saying to label the call, a group question reading every call) — SUPPORTED as run of the reading (docs/dev/lanes/predcall_evidence/ predcall_model.py TWICE: `occurrences(/\d/) SEQ ";" SEQ occurrences(/\d/) & (occurrences.hit: "9")` refused, "label the part"; its group question `some((occurrences.hit: "9"))` against the direct "a `;` and a 9 anywhere", 0 of 121 texts over `9;1` differ, `9;1` HOLDS so the first call is read; CASE1: his example legal, against the labelled call 0 / 0 / 0 of 341 texts over `13 a`, WHOLE against the direct "the last number is 3" 0 differ; the four printed library lines, the call labelled, give the same answers by the macro's name; sabotage s2, s3 caught). The macro's name counts as a use of that name in the definition the call is written in, as a binding's does (the model's choice, the same rule).
- [review r83 D9: "surfaces" is the old sense; the base reads "as X exports it"] (b) a prefix `X.d` reads `d` as X surfaces it, so `B(A) & (A.d: <5)` and `[c = B(A)] & (c.d: <5)` differ when the body sets a `d` of its own — SUPPORTED (docs/dev/lanes/predcall_evidence/ predcall_model.py RECORD: both pasted lines of the record entry reproduced from the program text; WHOLE against the direct "first digit" / "second digit under 5", 0 and 0 of 40 texts; sabotage s4 caught)
- (c) `B.d` equals `c.d` for a single call — SUPPORTED (docs/dev/lanes/predcall_evidence/ predcall_model.py BDOT: `B(A) & (B.d: <5)` against `[c = B(A)] & (c.d: <5)`, 0 / 0 / 0 of 121 texts over `37-`; its line equals the record's c.d line)
- (d) an argument the body uses twice (`pair(A) & (A.d: ..)`, pair(p) := `/${p},${p}/`): `A.d` reads `d` as it reaches the caller, the last mention — SUPPORTED as run of the reading (docs/dev/lanes/predcall_evidence/ predcall_model.py PAIR: WHOLE against the direct "the second digit under 5", 0 of 40 texts; against `[c = pair(A)] & (c.d: <5)` 0 / 0 / 0; a group question `some((A.d: "7"))` reads both uses; sabotage s5 caught). It needs "used more than once" counted in the caller's TEXT (A written once): counted per lowering of the parameter the same program is the compile error "A is used 2 times here" (the model's OPT argcount = lowered), so the reading also chooses the count, a reading of binding-prefix's reading (b). SUPERSEDED by argument-default (2026-11-22): `pair(A) & (A.d: <5)` with that body is a compile error (the line "Used twice alone"); the list body reads `pair.d` (review r84 C2).
- case 2: `A.d` legal for an argument that is a binding where `d` is visible through the call, reading A's own `d` — RULED with closed-argument (core/labels/paths/closed-argument); run as the record's A.d line (RECORD) and the printed example 1 of core/holes/bare-condition/nested-scope. REVISED by argument-default (2026-11-22) for a body using its argument alone: both programs (the record's A.d line, example 1) are compile errors; legal only where the body labels the spot or passes the labels on (review r84 C2; no longer awaiting argument-default).
- (3) an argument written in place is the caller's own text, read bare — SUPPORTED as run (docs/dev/lanes/predref_evidence/ predref_model.py LABELONLY: `hits(/a(?<g>x)?/) & (g: "x")`, its printed line) SUPERSEDED by argument-default's reading (b) (2026-11-22): `hits(/a(?<g>x)?/) & (g: "x")` is a compile error, re-spelled `hits.hit.g` (review r84 C2; no longer awaiting argument-default).
- (4) a parameter's label inside the body is not nameable — ruled (nested-scope, 2026-11-21); nothing run here
- a group in a USER macro's body (`(?<d>\d)` in B) is a capture and a label as in any user literal: helper-captures ("occurences et al") is for provided bodies — the manager's reading (a) of that ruling; UNTESTED as to capture (the model reads the labels only).
- (review r83 A6) a call exports what its body exports (core/labels/export statement 3), a label a part label in the body passes included: `B.d` for `B(rx) := /${[p = rx]}xx/` reads p's `d` by name — SUPPORTED as run (docs/dev/lanes/predfix83_evidence/ predfix83_model.py LISTCALL: `B(A) & (B.d: <5)` against p's digit under 5, differing 0; sabotage s4 caught by the same check).
evidence: docs/dev/lanes/predcall_evidence/ predcall_model.py CASE1, TWICE, RECORD, BDOT, PAIR; docs/dev/lanes/predref_evidence/ predref_model.py HITS, RESPELL, LABELONLY; docs/dev/lanes/predspot_evidence/ predspot_model.py SWEEP (lane predspot).
history:
- 2026-11-22 (lane predref, label-reference sweep and helper-captures fold): new open piece (the brief's reading (b), the manager's conservative form, listed as the open question call-prefix with candidates).
- 2026-11-22 (lane predcall, call-prefix case 1 folded): open call-prefix to ruled. The statement until then, verbatim: "Under label-reference, how is a label referenced that comes from a macro call's body, from an argument, or from a parameter inside a macro body?". The conservative form 1 until then: "a label from a call's body is reached by labelling the call, never by the macro's name: `[h = hits(/\d+/)] & (h.hit: <5)` (a macro's name is no prefix: core/labels/paths/binding-prefix)"; form 2 kept as the meanwhile reading of case 2; forms 3 and 4 kept. The candidates until then: "(a) keep the four forms; (b) as (a), and a macro called once in the definition is a prefix of its own, as a binding is (`hits.hit`); (c) as (a), and an argument is also reached through the parameter's name at the call (`B(rx = A)`, `rx.d`)"; the ruling is wider than (b): a macro called more than once is a prefix too, under binding-prefix's two rules (the manager's reading told to him). The line `modes: n/a (a question ...)` replaced by the run lines; programs written with a labelled call are not re-spelled.
- 2026-11-22 (lane predcall, R-1 of its rulings file, closed-argument ruled (a)): the case 2 bullet's words until then, "NOT RULED; the owner's lean, 2026-11-22: "i'd say A.d is legal there". Meanwhile the reading: `A.d` is legal and reads A's own `d`, as printed in core/holes/bare-condition/nested-scope", became ruled with closed-argument; the statement gained "an argument's labels are reached through its binding where visible" in place of "a label on the call stays legal" (that sentence is in a bullet); the line label "(case 2, a reading)" became "(case 2)".
- 2026-11-22 (lane predfix82, review r82 ANS-1, DES-6; record "2026-11-22 MANAGER — review r82 (predfold1122): dispositions ruled; two corrections of record entries (no owner words)"): "`A.d` is A's own `d`" marked a reading on the run lines he was shown, the two-sources question pointed at; a bullet and the line "A part label named like the macro" (predfix82 HIDE).
- 2026-11-22 (lane preddef, default-export folded; record "2026-11-22 OWNER RULING — default-export: protected"): statement until then: "A macro's name qualifies the labels its call surfaces (`hits(/\d+/) & (hits.hit: 3)`), under a binding prefix's two rules; an argument's labels are reached through its binding where visible." Case 1 until then: "Case 1, ruled: the macro's name is a prefix of the labels its call surfaces (its arguments' too: a reading)." The prefix bullet until then: "A prefix `X.d` reads `d` as X surfaces it (a reading, run): `B.d`, and `c.d` under `[c = B(A)]`, are `d` as the call surfaces it, the last mention among the body's and the argument's; `A.d` is A's own `d` (a reading, on the run lines he was shown before closed-argument; a name with two sources is open two-sources, core/labels/paths/two-sources). So the spellings differ when the body sets a `d` of its own." Now (the manager's reading (e), SUPPORTED as run, preddef_model.py MACRO): a call exports what its body's text writes; an argument the body uses alone is not exported (`B.d`, `c.d` compile errors for `B(rx) := /${rx}xx/`: the new line "By the macro's name, the body writing no `d`"). The line "d as the call surfaces it, the last mention (B's)" renamed "d as the call exports it, the body's own", answers unchanged. The lines "A's own d" and "An argument used twice by the body" marked "(awaits argument-default)"; the case 2, used-twice and in-place bullets reflowed (40-line cap) and marked; their content otherwise unchanged.
- 2026-11-22 (lane predfix83, review r83 A6, D6, D10; record "2026-11-22 MANAGER — review r83 (preddef1122): dispositions ruled; one correction; idiom-confirm closed on default-export (no owner words)"): statement until then: "A macro's name qualifies the labels its call exports, those its body's text writes (`hits(/\d+/) & (hits.hit: 3)`), under a binding prefix's two rules; an argument used alone is not exported." (narrower than the export rule, A6; it read as if case 2 were refused, D10). The bullet "A prefix `X.d` reads `d` as X exports it" until then: "`B.d`, and `c.d` under `[c = B(A)]`, are the body's own `d`; where the body writes none (`B(rx) := /${rx}xx/`) both are compile errors." Case 1's "a reading of default-export" marked the manager's reading (e) (D6). Answers unchanged.
- 2026-11-22 (lane predspot, argument-default folded; record "2026-11-22 OWNER RULING — argument-default: an error; and his reason: a label is to the SPOT in the pattern, a parameter is a template, not a piece of the pattern"): the prefix bullet's "`A.d` is the caller's read of its own argument (awaits argument-default; two sources: core/labels/paths/two-sources)." to "`A.d` reads A's `d` only where the body labels the spot or passes the labels on (case 2, below)."; the case 2 bullet shortened, gaining "settled strictly by argument-default"; the twice-used bullet until then: "An argument the body uses twice (`pair(p) := /${p},${p}/`) is written once in the caller, so `A.d` is a plain read of one use, the last mention as it reaches the caller (a reading, run: the line "An argument used twice by the body"; awaits argument-default). An argument written in place is the caller's own text, read bare (`hits(/a(?<g>x)?/) & (g: "x")`; awaits argument-default); ...". The line "A's own d, through the argument (case 2)" (B(rx) := `/${rx}-(?<d>\d)/`, WHOLE `7-3` FAILS, `3-7` HOLDS) is now a compile error ("A's own d, the body using the argument alone") and re-spelled with `[p = rx]` ("A's own d, the body labelling the spot", the same answers); "An argument used twice by the body" re-spelled `pair(A) & (pair.d: <5)` with the list on both spots (the same answers).
- 2026-11-23 (lane predfix84, review r84 C2; record "2026-11-23 MANAGER — review r84 (predspot1122): the dispositions, ruled with the 2026-11-23 rulings in hand; no owner words"): the case 2 bullet until then: "Case 2, an argument that is a binding (`A.d` in `B(A)`), ruled with closed-argument ("i'd say A.d is legal there") and settled strictly by argument-default: legal only where ..." Now "by closed-argument and argument-default: legal only where ..." (C2: case 2 is REVISED by argument-default for a body using its argument alone, not "settled"; C8: the mark is here). Readings (d), case 2 and (3) marked; their "awaits argument-default" tags removed.

## core/labels/paths/closed-argument — When a macro closes its argument's labels
slugs: closed-argument
rulings:
- 2026-11-22 "closed-arguments: a" (record: "2026-11-22 OWNER RULING — closed-argument: a (where a macro closes its argument's labels, the caller's `A.d` is a compile error)"); RULED (a), on the statement as put: for an argument that is a binding, the caller's `A.d` is legal exactly where `d` is visible through the call and reads `d` as it reaches the caller; where the macro closes the argument's labels (`B(rx) := /${[_ = rx]}xx/`) `A.d` is a compile error; it settles call-prefix case 2 under that condition
- 2026-11-22 (class: LEAN) "closed-arguments: i thought you'd lean to (a). what would A.d mean if d no longer was visible? also: [ c = B(A) ] does not allow c.A" (record: "2026-11-22 OWNER, on closed-argument: "i thought you'd lean to (a). what would A.d mean if d no longer was visible?"; and "[ c = B(A) ] does not allow c.A""); his lean to (a), put as a question, and his reason, "what would A.d mean if d no longer was visible?"
- 2026-11-22 "argument-default: for me this is an error. I'm just trying to articulate why it's an error other than form. I get that it might not end up in the pattern. I think for me it has to do with whether or not it's definitively part of the pattern being constructed or if it's a parameter to it. B(rx) := you can't take a label against rx directly. You can take a label to the spot that rx gets laid into the regex. The label is not to the regex abstractly, it's to the spot in the pattern where the regex is being inserted. A parameter like rx in a call B(rx) cannot be labeled because it's not being placed into the pattern. It's not a piece of the pattern. It's a template of the rx that might be placed into the pattern." (record: "2026-11-22 OWNER RULING — argument-default: an error; and his reason: a label is to the SPOT in the pattern, a parameter is a template, not a piece of the pattern"); it settles "visible through the call" in the strict sense.
rejected:
- (b) `A.d` still legal where the macro closes the argument, "a closure only needs to guard what the macro surfaces" (the manager's leaning when the question was put) — by owner ruling — closed-argument: a; his reason "what would A.d mean if d no longer was visible?"; the manager withdrew (b) before the ruling (the record entry before it).
readings:
- the ruling as run: where B closes its argument (`[_ = rx]`), `B(A) & (A.d: <5)` and `[c = B(A)] & (c.d: <5)` refused, the call itself matching as `\dxx` (0 / 0 / 0 of 31 texts over `3x`); through an open B `A.d` legal, its line the record's A.d line — SUPPORTED (docs/dev/lanes/predcall_evidence/ predcall_model.py CLOSED; sabotage s13 caught)
- (a) "visible through the call" is by core/labels/export (a `_` part label or `[_ = rx]` in the macro's body closes it) — SUPPORTED as run for `[_ = rx]` (CLOSED); UNTESTED for a `_x` part label (the loaded model keeps a `_x` part's groups visible by their own names, so it cannot show that closure).
- (b) an argument the body uses twice: `A.d` is the last mention as it reaches the caller — SUPPORTED as run of the reading (docs/dev/lanes/predcall_evidence/ predcall_model.py PAIR, the line in core/labels/paths/call-prefix) SUPERSEDED by argument-default (2026-11-22): a body using its argument twice alone exports nothing, so `A.d` is a compile error (core/labels/paths/call-prefix, the line "Used twice alone"; review r84 D1).
- (c) the compile error is at the reference and names its rule (the base's words since the predspot fold; until then "the macro that closes the label"; review r84 D1) (the message the manager's call) — UNTESTED (the model's message names the missing label, not the macro: "`A.d`: `A` passes no public label `d`").
evidence: docs/dev/lanes/predcall_evidence/ predcall_model.py CLOSED, PAIR; docs/dev/lanes/predspot_evidence/ predspot_model.py SWEEP (lane predspot).
history:
- 2026-11-22 (lane predcall, call-prefix case 1 folded): a new open piece, a sub-piece of core/labels/paths/call-prefix in all but its tag (a fifth tag word is not in the format). The manager's leaning (b) as put to him and its withdrawal are in the record entry.
- 2026-11-22 (lane predcall, R-1 of its rulings file, closed-argument ruled (a)): open closed-argument to ruled (a). The statement until then, verbatim: "When a macro closes its argument's labels (`B(rx) := /${[_ = rx]}xx/`), is the caller's `A.d` in `B(A)` (a) a compile error, or (b) still legal?"; the bullets until then: his lean "put as a question, not worded as a ruling", the manager's earlier leaning (b) "not held now" (now under `rejected:`), "The statement the manager would enter on his confirmation, NOT YET RULED: ..." (now the ruling's own statement), "No printed program applies either answer." (now its two lines: "Visible through the call" and "Closed by the macro"). The line `modes: n/a (a question ...)` replaced.
- 2026-11-22 (lane predfix82, review r82 EVID-1, ANS-4; record "2026-11-22 MANAGER — review r82 (predfold1122): dispositions ruled; two corrections of record entries (no owner words)"): the line "Closed by a `_` part label" added (predfix82 CLOSEDX); the `c.d` half of "Closed by the macro" names its rule.
- 2026-11-22 (lane preddef, default-export folded; record "2026-11-22 OWNER RULING — default-export: protected"): the settling bullet until then: "It settles call-prefix case 2: legal, under this condition." It gains: under default-export a body using the argument alone exports none of its labels, so whether `A.d` is visible is open (argument-default); the line "Visible through the call" marked "(awaits argument-default)". The ruling itself is unchanged.
- 2026-11-22 (lane predfix83, review r83 A8; record "2026-11-22 MANAGER — review r83 (preddef1122): dispositions ruled; one correction; idiom-confirm closed on default-export (no owner words)"): reading (a) until then: ""visible through the call" is by core/labels/export (a `_` part label or `[_ = rx]` in the body closes it)", which decided argument-default as (error) mechanically for a body using its argument alone. Now it holds where the body labels the argument and awaits argument-default where the body uses it alone.
- 2026-11-22 (lane predfix83, review r83 D9; record "2026-11-22 MANAGER — review r83 (preddef1122): dispositions ruled; one correction; idiom-confirm closed on default-export (no owner words)"): the line "Closed by the macro": "no `d` surfaces" to "no `d` is exported" (the verb of reach).
- 2026-11-22 (lane predspot, argument-default folded; record "2026-11-22 OWNER RULING — argument-default: an error; and his reason: a label is to the SPOT in the pattern, a parameter is a template, not a piece of the pattern"): ruled 2026-11-22, date kept. The readings bullet until then: "Readings (each a reading): "visible through the call" is by core/labels/export where the body labels the argument (a `_` part label or `[_ = rx]` closes it); where the body uses it alone it awaits argument-default (below); an argument the body uses twice: `A.d` is the last mention as it reaches the caller (...); the error is at the reference and names the macro that closes the label (its message the manager's call)."; the settling bullet until then ended "so whether `A.d` is then visible is open (awaits argument-default, ...); `[_ = rx]` and a `_` part label close it under either candidate."; the line "Visible through the call" re-spelled with B(rx) := `/${[p = rx]}-(?<d>\d)/` (the same answers) and the body-alone form is the new line "Used alone by the body", a compile error.
- 2026-11-23 (lane predfix84, review r84 D1; record "2026-11-23 MANAGER — review r84 (predspot1122): the dispositions, ruled with the 2026-11-23 rulings in hand; no owner words"): reading (b) marked superseded; reading (c) "names the macro" to "names its rule", as the base says.

## core/labels/paths/argument-default — The caller's read of an argument the body uses alone
slugs: argument-default
rulings:
- 2026-11-22 "argument-default: for me this is an error. I'm just trying to articulate why it's an error other than form. I get that it might not end up in the pattern. I think for me it has to do with whether or not it's definitively part of the pattern being constructed or if it's a parameter to it. B(rx) := you can't take a label against rx directly. You can take a label to the spot that rx gets laid into the regex. The label is not to the regex abstractly, it's to the spot in the pattern where the regex is being inserted. A parameter like rx in a call B(rx) cannot be labeled because it's not being placed into the pattern. It's not a piece of the pattern. It's a template of the rx that might be placed into the pattern." (record: "2026-11-22 OWNER RULING — argument-default: an error; and his reason: a label is to the SPOT in the pattern, a parameter is a template, not a piece of the pattern"); answer (error), and his reason (core/principles/label-names-spot); it revises his example 1 of 2026-11-21.
rejected:
- (local), the caller's own read of the argument, legal — by owner ruling — "for me this is an error".
- the middle (labelled), a read only through a label the caller writes on the argument (`B([a = A])`, `a.d`) — by owner ruling, as the manager read it — "A parameter like rx in a call B(rx) cannot be labeled because it's not being placed into the pattern."
readings:
- (a) a part label written ON an argument at a call labels a template, not a spot: a compile error — SUPPORTED as run (docs/dev/lanes/predspot_evidence/ predspot_model.py ARGLABEL: `C := B([a = A]) & (a.d: <100)`, `atomic([ab = B | A]) & (ab.l: <20)`, `rx.repeat([a = rx.digit], min = 1) & (a: "3")` refused, each naming this rule).
- (b) a group written in an argument passed in place is not the caller's to read bare; the body's `d` is the only one, as `B.d` — SUPPORTED as run (docs/dev/lanes/predspot_evidence/ predspot_model.py INPLACE: `B(/(?<d>\d)/) & (d: <5)` refused; `B(/(?<d>\d)/) & (B.d: <5)` reads the body's `d`, checked against a direct read of the second digit on every text of length 3 over `37-`).
- (c) a condition written INSIDE the argument beside its own group travels with the template and stays legal — SUPPORTED as run (docs/dev/lanes/predspot_evidence/ predspot_model.py ARGOWN: `occurrences(/(?<n>\d+)/ & (n: <100))` legal, its printed answers unchanged).
- (d) a spot the body labels exports the argument's exported labels through that label (`B.dd.d`); `hit` is such a spot (`hits.hit.g`) — SUPPORTED as run (docs/dev/lanes/predspot_evidence/ predspot_model.py SPOT).
- (e) a binding used alone in a definition IS placed: its name stands for its spot there (binding-prefix) — SUPPORTED as run (the one-use plain read `A & B & (A.h: <2)` of core/labels/paths/one-use-read answers as printed: docs/dev/lanes/predspot_evidence/ predspot_model.py SWEEP).
- (A3, kept) a body using its argument both alone and labelled reads the labelled spot's labels — SUPPORTED as run (docs/dev/lanes/predspot_evidence/ predspot_model.py SWEEP, the line "Both uses").
- (the lane's) the refusal is keyed on the template: a read of a name that only a parameter's argument holds — UNTESTED as a rule beyond the grid; run on every cell of docs/dev/lanes/predspot_evidence/ predspot_model.py GRID.
- [withdrawn by the ruling: the question as put, both candidates; "an argument written in place belongs to the same question" (now settled by the reading (b)); "the cost of (error)" (paid by wrapper-export and transform-export: lib/convention/argument-labels); its library face of `hit` (answered by the reading (d))].
evidence: docs/dev/lanes/preddef_evidence/ preddef_model.py AWAITS, MACRO; docs/dev/lanes/predspot_evidence/ predspot_model.py ARGNAME, ARGLABEL, INPLACE, ARGOWN, SPOT, GRID, AWAITS, SWEEP.
history:
- 2026-11-22 (lane preddef, default-export folded): a new open piece, at the manager's brief. Every printed line it names is kept with its answers and marked "(awaits argument-default)".
- 2026-11-22 (lane predfix83, review r83 A3, A8, D4 (iii); record "2026-11-22 MANAGER — review r83 (preddef1122): dispositions ruled; one correction; idiom-confirm closed on default-export (no owner words)"): corrected BEFORE the owner is asked (the record's A3): the candidates bullet until then ended "The match is the same under both."; the list of dependents until then: "call-prefix's "A's own d" and "An argument used twice by the body", closed-argument's "Visible through the call", two-sources' (b) in place, nested-scope's "Example 1", core/patterns/atomic, and in the library peek, hits, endsWith, list_of, rx.repeat's labelled item and occurrences' argument group." Now: the exception for a body using its argument both alone and labelled with the lines "Both uses"; the (error) answer's cost across the provided library; the manager's reading on a read inside the argument; the list gains closed-argument's reading (a), two-sources' (a) in place and when's "Labels the test sets are visible in then" (A8); the library face of the label-only `hit` (D4 (iii)).
- 2026-11-22 (lane predspot, argument-default folded; record "2026-11-22 OWNER RULING — argument-default: an error; and his reason: a label is to the SPOT in the pattern, a parameter is a template, not a piece of the pattern"): open argument-default 2026-11-22 to ruled 2026-11-22. Statement until then: "Where a macro's body uses an argument alone, is the caller's read of that argument's labels (`A.d` in `B(A)`, a group written in place) its own local read, legal, or a compile error?"; the body's candidates, its cost and its dependents' list replaced by the ruling, the manager's readings (a) to (e) and the lines "The caller's own read", "A label written on the argument"; the lines "(local)" (`B(A) & (A.d: <5)`, B(rx) := `/${rx}xx/`, WHOLE `3xx` HOLDS, `7xx` FAILS) and "Both uses, (local)" dropped (the rejected answer); "(error)" kept as "The caller's own read"; "Both uses, (error)" kept as "Both uses". Every "(awaits argument-default)" line of the three base files resolved (docs/dev/lanes/predspot_evidence/ predspot_model.py AWAITS).
- 2026-11-23 (lane predfix84, review r84 C8; record "2026-11-23 MANAGER — review r84 (predspot1122): the dispositions, ruled with the 2026-11-23 rulings in hand; no owner words"): the bullet "It revises his example 1 (core/holes/bare-condition/nested-scope): ..." now "His example 1 (...): ..." (the base carries no revision marks): argument-default REVISES his example 1 of 2026-11-21. The rest of that bullet ("it settles call-prefix case 2 and closed-argument's ... in the strict sense") is review r84 C4's, left for the fold lane.

## core/labels/paths/two-sources — A name with two sources
slugs: two-sources
rulings:
- 2026-11-22 "argument-default: for me this is an error. I'm just trying to articulate why it's an error other than form. I get that it might not end up in the pattern. I think for me it has to do with whether or not it's definitively part of the pattern being constructed or if it's a parameter to it. B(rx) := you can't take a label against rx directly. You can take a label to the spot that rx gets laid into the regex. The label is not to the regex abstractly, it's to the spot in the pattern where the regex is being inserted. A parameter like rx in a call B(rx) cannot be labeled because it's not being placed into the pattern. It's not a piece of the pattern. It's a template of the rx that might be placed into the pattern." (record: "2026-11-22 OWNER RULING — argument-default: an error; and his reason: a label is to the SPOT in the pattern, a parameter is a template, not a piece of the pattern"); it settles the FIRST shape (the manager's reading (b)); the second stays open.
rejected:
readings:
- the four candidate lines RUN, each against a direct read of the first or the second digit on every text of length 3 over `37-,1`; the printed `B(A) & (A.d: <5)` (A's own `d`) answers as candidate (b)'s spelling, 0 / 0 / 0 differ (docs/dev/lanes/predfix82_evidence/ predfix82_model.py TWOSRC).
evidence: docs/dev/lanes/predfix82_evidence/ predfix82_model.py TWOSRC; docs/dev/lanes/predspot_evidence/ predspot_model.py SWEEP (lane predspot).
history:
- 2026-11-22 (lane predfix82, review r82 ANS-1, the manager's disposition): a new open piece under the slug two-sources; the question the review found between label-reference and flow; neither answer applied.
- 2026-11-22 (lane preddef, default-export folded; record "2026-11-22 OWNER RULING — default-export: protected"): a bullet: what default-export changes (the call exports its body's `d`, not the argument's; the in-place shape depends on argument-default; the top-level shape unchanged); the line "(b) the source written here" marked "(awaits argument-default)" (under its candidate "error" that program is refused: preddef_model.py AWAITS).
- 2026-11-22 (lane predfix83, review r83 D9, A8; record "2026-11-22 MANAGER — review r83 (preddef1122): dispositions ruled; one correction; idiom-confirm closed on default-export (no owner words)"): statement until then: "When a name read bare has two sources in its definition, a group written in the definition's own text and a label a part surfaces, does the read reach the last mention or the source written here?"; "surfaced by a used binding" in the first bullet to "held by" (D9). The line (a) in place depends on argument-default by the bullet "What default-export changes" (A8): it is listed under argument-default; its printed answer does not move in the evidence engine (the body's own `d` licenses the bare read), so it carries no "(awaits)" mark.
- 2026-11-22 (lane predspot, argument-default folded; record "2026-11-22 OWNER RULING — argument-default: an error; and his reason: a label is to the SPOT in the pattern, a parameter is a template, not a piece of the pattern"): open two-sources 2026-11-22 kept (the second shape open). The candidates bullet until then: "Candidates: (a) the last mention, as the label reaches the caller (what the in-place forms answer today, the lines (a)); (b) the source written here (the lines (b), spelled with a part label, which answer so under either candidate). Neither answer is applied." and the default-export bullet ("What default-export changes (a reading): ... the second shape, at the top, is unchanged.") replaced by the settled first shape and the open second. The line "(a) the label as it reaches the caller, an argument written in place" (`B(/(?<d>\d)/) & (d: <5)`, WHOLE `7-3` HOLDS, `3-7` FAILS) is now a compile error ("The first shape, read bare"); the line "(b) the source written here, as spelled with a part label" (`B([x = /(?<d>\d)/]) & (x.d: <5)`, WHOLE `7-3` FAILS, `3-7` HOLDS) too, by the reading (a); the line "The first shape, settled" added (`B.d`, the answers the old (a) line gave).

## core/labels/paths/one-use-read — A plain read through a prefix with one use
slugs: idiom-confirm
rulings:
- 2026-11-22 "default-export: protected" (record: "2026-11-22 OWNER RULING — default-export: protected (a part used alone is available inside the binding and is not exported)"); rules it, by the record entry "2026-11-22 MANAGER — review r83 (preddef1122): dispositions ruled; one correction; idiom-confirm closed on default-export (no owner words)": "the statement put to him before he ruled "default-export: protected" was "a part used bare is available locally as `A.h` but exports nothing", and his analogy gives the part used alone local access. That IS the one-use plain read through the binding's name; so `isodate & (isodate.year: < 2100)` at the top, where isodate is used alone, is ruled legal by default-export, and his 2026-11-17 point 4 is revised by it." (no owner words; told to him, not asked again)
- 2026-11-22 (class: ANALOGY) "[A ] (A alone, default) also makes the labels protected but with different access locally" (record: "2026-11-22 OWNER, an analogy to validate: the four ways a part is used, as C++ access levels"); the local access the ruling gives
- 2026-11-17 (class: PROPOSAL) "4. A . B & (A.h: blah) error. A is a binding not a label and could be ambigous if its used multiple times in an expression" (record: "2026-11-17 OWNER PROPOSAL — label-flow: an ambiguous REFERENCE is the error"); a one-use program called an error, several uses his reason; REVISED by default-export (2026-11-22, the record entry above)
- 2026-11-22 (class: LEAN) "binding in prefix: i like your read on this except that perhaps it does refer to all" (record: "2026-11-22 OWNER, on binding-prefix: "i like your read on this except that perhaps it does refer to all""); the group question through the prefix
- 2026-11-22 ""binding-prefix" 1. yes. 2. i agree with your lean (a)" (record: "2026-11-22 OWNER RULING — binding-prefix: 1 yes (a group question through a binding's prefix reads every use); 2 a (a plain read through it, the binding used more than once, is a compile error)"); rules the several-use case only
rejected:
- (b) an error with any use, the part labelled instead (`[aa = A]`, `aa.h`), as in his point 4 — by owner ruling — default-export: protected, as the record entry "2026-11-22 MANAGER — review r83 (preddef1122): dispositions ruled; one correction; idiom-confirm closed on default-export (no owner words)" reads it: a part used alone is available locally as `A.h`.
readings:
- (a) legal with one use, the reading the documents print: the line "One use" RUN (docs/dev/lanes/predfix82_evidence/ predfix82_model.py CONTROL and SECOND).
- the plain idiom `isodate & (isodate.year: < 2100)` at the top, isodate used alone — SUPPORTED as run (docs/dev/lanes/predfix83_evidence/ predfix83_model.py TOPLEVEL, the line "The plain idiom, one use"; sabotage s24, the other candidate, caught; GRID cells binding/one, all four read kinds).
evidence: docs/dev/lanes/predfix82_evidence/ predfix82_model.py SECOND.
history:
- 2026-11-22 (lane predfix82, review r82 ANS-2a and RULING-9, the manager's disposition): a new open piece under the slug idiom-confirm; the one-use plain read and the isodate idiom stay as printed, marked readings pointing here.
- 2026-11-22 (lane predfix83, review r83 D17; record "2026-11-22 MANAGER — review r83 (preddef1122): dispositions ruled; one correction; idiom-confirm closed on default-export (no owner words)"): RULED by default-export, the record entry closing idiom-confirm (no owner words; review r83 RULING-8). Status `open idiom-confirm 2026-11-22` to `ruled 2026-11-22`. Statement until then: "With ONE use, is a plain read through a binding's prefix (`A.h`) legal, and with it the plain idiom `isodate & (isodate.year: < 2100)`?" Its body until then: his point 4 and his words of today on binding-prefix (now in rulings:), "The reading the documents print (the manager's): legal, resting on label-reference ("required": the required form must be legal) and on his own one-use examples (`[ hits = occurences(...) ] & (hits.hit: <5)`, `(h.hit: 3)`); the plain idiom `isodate & (isodate.year: < 2100)` taken as included on his silence. Every program re-spelled under label-reference with a one-use prefix depends on it (the line "One use", core/labels/paths/binding-prefix)." and "Candidates: (a) legal with one use (the reading); (b) an error with any use, as in that proposal, the part labelled instead (`[aa = A]`, `aa.h`)." The line "One use, the reading" renamed "One use", answers unchanged; the line "The plain idiom, one use" added.

## core/labels/backreferences — Backreferences
slugs: backref-label backref-across-parts same-name-twice
rulings:
- 2026-11-18 "backref-label: capture" (record: "2026-11-18 OWNER RULING — backref-label: capture")
- 2026-11-18 "same-name-twice: i agree with your lean." (record: "2026-11-18 OWNER RULING — same-name-twice: an error at the backreference unless `(?J)`")
- 2026-11-18 "backref-across-parts: I agree but also, a reference should use the namespace as it is defined at the point of reference" (record: "2026-11-18 OWNER RULING — backref-across-parts: the part's own group; a reference uses the namespace at its point")
- 2026-11-18 "backref-across-parts: which is to say, it should be the last reference as labels" (record: "2026-11-18 OWNER, clarifying backref-across-parts — a backreference reads as labels do: the last mention at its point")
- 2026-11-18 "backref-across-parts: I agree with error." (record: "2026-11-18 OWNER RULING — free-name: a reference to a name the rx does not define is an error")
rejected:
- "inside rx text a backreference already reads the last-set capture" (rev 25) — by the draft (rev 25.1, R.9 row 37) — WITHDRAWN: false under `(?J)` (a backreference there reads the first set group); backref-across-parts asked, then free-name ruled.
- a backreference that reads the label (reset on entry) — by owner ruling — backref-label: capture.
- the written-out regex's reading (one namespace for the whole composition) — by owner ruling — backref-across-parts.
- rev 27's three candidates for `\k<h>` after two groups of one name — by owner ruling — same-name-twice: a compile error unless `(?J)` (the draft R.9, A25).
readings:
- a reference to a name unset at its point fails, as regex's does (the manager's) — UNTESTED.
evidence: preddoc3a_model.py BREF (the draft's PART REF REF2 line; printed answers reproduced; `\d(\d)\1` agrees); sabotage s10 caught.
history:
- 2026-11-18: backref-across-parts, its clarification, free-name, backref-label, same-name-twice.
- 2026-11-19 (lane preddoc6, review r60 RECOUNT-6): the draft R.9 candidate for this piece, PARTIAL at r59 and left unchanged by preddoc5, now has its own `rejected:` line.

## core/labels/numbers — Numbers name groups only without ambiguity
slugs: number-names zero-place numbered-label-warning numbered-duplicate sequence-numbers
rulings:
- 2026-11-18 "number-names: exactly. Only when there is no ambiguity." (record: "2026-11-18 OWNER RULING — number-names")
- 2026-11-18 "number-names: the exception to our rule is 0. It is always the entire match of the rx however it is composed." (record: "2026-11-18 OWNER RULING, addendum to number-names — zero is the exception"); its "entire match" is the match so far after a complete pattern, by the next item
- 2026-11-19 "zero-in-sequence: you are a lawyer in your exact wording. this is what is needed now. the condition is always sees the regex composed at the point it is used. so the 0: is the match so far" (record: "2026-11-19 OWNER RULING — zero-in-sequence"); the statement's "`0` ... names the match so far" (the deciding piece: core/conditions/match-so-far)
- 2026-11-17 "For A & B: from the perspective of B, the subject is now whatever A matched. There is no outside subject (unless we allow context, etc). That's its whole world. So all numbers are labels of groups in that world." (record: "2026-11-17 OWNER RULING — zero-place: a pattern's numbers are labels in its own world")
- 2026-11-17 "Also, not recommended to use group numbers as it's confusing on bound values you can't see" (record: "2026-11-17 OWNER RULING — zero-place: a pattern's numbers are labels in its own world")
- 2026-11-22 "program-options: yes." (record: "2026-11-22 OWNER RULING — program-options: yes; and a PROPOSAL: `i` keeps inheriting, with a "weak" value the program sets"); `n` among the program options.
- 2026-11-22 (class: OBSERVATION) "Using predicate language it's going to be more likely to use () in a literal to mean no capturing group." (record: "2026-11-22 OWNER IDEA — program-scoped options: `@options()` setting flags (m, s, n, ...) for the literals of the bindings that follow"); his ground for `n`.
rejected:
- "numbers name the groups of the nearest pattern to their left" and "numbers are not subject to the ambiguous-reference error" (the manager's readings, rev 25.1-26) — by owner ruling — number-names ("Only when there is no ambiguity"; the draft R.9).
readings:
- a number on a group whose name is shared inside one literal is refused (the draft R.1.13) — UNTESTED.
- the numbered-label warning (the manager's proposal from his "not recommended", accepted: record "2026-11-17 OWNER — the numbered-label warning accepted") — the wording is core/diagnostics'.
- (the lane's reading, at the manager's brief) under `n` a plain `( )` is no capture and no numbered label; only named groups are numbered — SUPPORTED as run (docs/dev/lanes/predspot_evidence/ predspot_model.py NUMBERS: `/(\d):(\d)/` has 0 numbered groups under a file's `@options(n)`, 2 without). What it does to this piece: a number names fewer groups (under `n`, only named ones); to the name table's "capture only" cell: under `n` an unnamed group is not a capture at all, the cell empties.
evidence: preddoc3a_model.py NUM (the draft's PART NUM (2) line; printed answers reproduced).; docs/dev/lanes/predspot_evidence/ predspot_model.py NUMBERS (lane predspot).
history:
- 2026-11-17: zero-place, label numbers tried, the warning accepted; 2026-11-18: number-names and its addendum.
- 2026-11-19 (lane preddoc4): the statement's "`0` is always the entire match" now points at the deciding piece core/conditions/match-so-far (his addendum's words stay in the rulings items; after a complete pattern the match so far IS the entire match); the bullet "inside a loop body, the pass's" removed (the loop case is core/conditions/match-so-far/in-loop); the warning's trigger stated once, as the record's accepted proposal words it (review r59 ZERO, READ-10).
- 2026-11-19 (lane preddoc6, review r60 DAMAGE-4): the statement carries zero-in-sequence's meaning ("names the match so far"), so that ruling is cited here and the status re-dated 2026-11-19 (doc_format: a later ruling rewrites status and statement together); the 2026-11-18 addendum stays, its "entire match" read as the match so far after a complete pattern.
- 2026-11-19 (lane preddoc6, review r60 RECOUNT-5): slugs numbered-duplicate and sequence-numbers homed here: the draft's rev 25 asked them and rev 25.1 replaced both by number-names (the draft: "rev 25 asked two, **numbered-duplicate** and **sequence-numbers**; review r43 A folds them"); neither was answered under its own name.
- 2026-11-22 (lane predspot, program-options folded; record "2026-11-22 OWNER RULING — program-options: yes; and a PROPOSAL: `i` keeps inheriting, with a "weak" value the program sets"): ruled 2026-11-19 re-dated 2026-11-22: a bullet added (under `n`).
- 2026-11-23 (lane predfix84, review r84 C7; record "2026-11-23 MANAGER — review r84 (predspot1122): the dispositions, ruled with the 2026-11-23 rulings in hand; no owner words"): the class of his point 1 corrected from IDEA to OBSERVATION (the record's word: "two OBSERVATIONS (1: ...)"); the reading's "reading (f)" dropped (the folded entries have no (f) for options).

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
slugs: condition-not condition-or dollar-condition label-twice-warn colon-scope label-twice joint-condition
rulings:
- 2026-11-22 "count-in-set: ok, thats fine. i think your value in the left part of condition as a fantastic addition so b. it suggests $h could go there which is also new. aside: perhaps we will need a syntax to declare the ch in chars. i am wonderings not for correctness but clarity. also, it suggests that bindings could be used under certain rules as label prefixes like chars.ch as that is clear here. chars seq ":" seq chars & (chars.ch: blah) would need defining. respond" (record: "2026-11-22 OWNER RULING — count-in-set: b"); "so b": a value may stand left of `:`, written in place; it REVISES "An entry is `p: S`, p a label path, never an expression" (core/conditions/form/value-left)
- 2026-11-16 "record-is-product: absolutely. This is precisely the sort of simplifying semantics I'm looking for." (record: "2026-11-16 OWNER RULING — record-is-product: yes")
- 2026-11-16 "label-twice: agree an error. And that means it's also unofficially parked in case some other meaning becomes valuable" (record: "2026-11-16 OWNER RULING — label-twice: an error")
- 2026-11-17 "Agree with all three." (record: "2026-11-17 OWNER RULING — the three remaining error-or-warning candidates")
- 2026-11-16 "colon-scope: yes with refinement: (a, b = c): ... the 'c' is a binding et al" (record: "2026-11-16 OWNER RULING — colon-scope: yes, with a refinement for a default")
- 2026-11-16 "condition-not : yes allow not" (record: "2026-11-16 OWNER RULING — condition-not: allowed")
- 2026-11-14 "is somewhat structural because it's combined with the comma. & binds tighter" (record: "2026-11-14 RULING — C22, condition binding")
- 2026-11-16 (class: DIRECTION) "So I think the issue is that conditions are the bastard child of macros and patterns. What they need is to be themselves. Then we define them mathematically, whatever that means." (record: "2026-11-16 OWNER DIRECTION — conditions are their own kind"); a direction, not a detailed ruling: a condition is its OWN KIND, neither macro nor pattern
- 2026-11-22 (class: AGREEMENT) "Agree caveat bindings used to scope labels (A.a: 8)" (record: "2026-11-22 OWNER, on the two name spaces: "Agree caveat bindings used to scope labels (A.a: 8)""); the home of the position rule, the manager's wording a reading
rejected:
- the diagonal reading of a label named twice — by owner ruling — label-twice ("unofficially parked").
- `|` between conditions as a Kleene OR (condition-or) — deleted with the three-valued model (regex-settles).
- compared fields written as bare label names in an argument (`[h, m]`, the tuple compare's array) — by owner ruling — "definitely not a bare reference. it might shadow a binding and it wouldn't be clear where it was coming from" (record: "2026-11-15 RULING + OWNER IDEA — no bare field reference; a mark for the other side of the intersection"); left of `:` a name is a label by this piece's rule, so the joint entry `(h, m): R` is not that form.
readings:
- a condition is a value of its own kind (bound, passed, put in an array) (the draft §4.1) — its own kind is the owner's DIRECTION (rulings above); bound, passed, put in an array is the draft's — UNTESTED.
- inside a group question each plain entry reads its own array and a joint entry is refused, so there a record and its joint form part (the lane's reading of array-vs-passes (a) beside joint-in-some; predarr RECORD, JOINT) — SUPPORTED as runs; whether record-is-product is meant to hold there is an owner question (record-in-some, proposed; core/labels/labels-vs-captures/array-vs-passes).
- `P & x: S` and `[x: S]` are errors; parentheses kept (the manager's call on "a condition without its parentheses") — see core/spellings/condition-parentheses.
- (DES-3, the manager's) a bare name, `&` or `|` inside a value left of `:` and a label named twice (`$h` and `h`) are compile errors for now — SUPPORTED as run (docs/dev/lanes/predfix82_evidence/ predfix82_model.py GAPS)
evidence: preddoc3a_model.py FORM (invented; the lowering `[1-9]\d:[1-2]\d` agrees).
history:
- 2026-11-14 C22; 2026-11-16 colon-scope, record-is-product, label-twice, condition-not; 2026-11-17 the three candidates (label-twice-warn kept the error).
- 2026-11-19: dollar-diagnostic answered dollar-condition (the form `$x & S` stays legal and gets a warning); the warning's wording is core/diagnostics/dollar-form's.
- 2026-11-21 (lane predarr): a bullet added, a record and its joint form inside a group question (a reading).
- 2026-11-22 (lane predfix77, review r77 A9; record "2026-11-22 MANAGER — review r77 (predfold1121): dispositions ruled (no owner words)"): the record-is-product clause qualified "outside a group question (open record-in-some: core/conditions/form/record-in-some)"; status date 2026-11-16 to 2026-11-21 (joint-in-some, ruled 2026-11-21, is what parts the two there). The question proposed by lane predarr is now its own open piece.
2026-11-22 (lane predbound, count-in-set ruled (b); record "2026-11-22 OWNER RULING — count-in-set: b"): the statement until then, verbatim: "A condition is a record `(label: S, ...)` laid against the labels of the pattern it meets; it holds when every entry's label text is in its set."; the first bullet's "p a label path, never an expression" became "p a label path or a value written in place" (the manager found no owner words behind "never an expression", record); "Left of `:` names are labels" became "a bare name or a label path is a label". Status date 2026-11-21 to 2026-11-22. No printed line moves.
- 2026-11-22 (lane predfix82, review r82 DES-3, RULING-5; record "2026-11-22 MANAGER — review r82 (predfold1122): dispositions ruled; two corrections of record entries (no owner words)"): "a bare name or a label path" became "a bare name, a number or a label path"; the three parse gaps compile errors for now (readings, predfix82 GAPS); "it may be bound, passed or put in an array" restated with bound-condition (record CORRECTION 2).
- 2026-11-22 (lane preddef, export-list folded; record "2026-11-22 OWNER RULING — export-list: yes"): the left-of-`:` bullet gains his caveat (a path's last step is the label), a reading.
- 2026-11-22 (lane predfix83, review r83 D14; record "2026-11-22 MANAGER — review r83 (preddef1122): dispositions ruled; one correction; idiom-confirm closed on default-export (no owner words)"): the caveat's sentence until then: "A path's last step is the label; its earlier steps are sources, a binding's, a macro's name or a part label (a reading, his caveat: core/modules/binding-list)." (a noun lost, pointing away). Now its home is here, the full wording (a metadata field as a last step, `w.index`, included); core/modules/binding-list points here.

## core/conditions/form/value-left — A value left of `:`
slugs: count-in-set
rulings:
- 2026-11-22 (class: QUESTION) "label references: the remaining question is to whether it should be _required_ that the label is known textually at reference. ie should ch require chars.ch in the above example. i'm inclined to say yes. thoughts? also, value in conditions: why would (x,y): () form not allow values?" (record: "2026-11-22 OWNER, two points after binding-prefix: should a label be REQUIRED to be known textually at its reference"); his "why would (x,y): () form not allow values?"
- 2026-11-22 "count-in-set: ok, thats fine. i think your value in the left part of condition as a fantastic addition so b. it suggests $h could go there which is also new. aside: perhaps we will need a syntax to declare the ch in chars. i am wonderings not for correctness but clarity. also, it suggests that bindings could be used under certain rules as label prefixes like chars.ch as that is clear here. chars seq ":" seq chars & (chars.ch: blah) would need defining. respond" (record: "2026-11-22 OWNER RULING — count-in-set: b"); part 2 of the entry: "so b", a value may stand in the left part of a condition entry, written in place; part 3, "it suggests $h could go there which is also new", an OBSERVATION (the base states the `$h` form as a reading)
- 2026-11-22 (class: QUESTION) "count-in-set: i don't understand your length(S) example: where do you define label ch?" (record: "2026-11-22 OWNER, on count-in-set: "where do you define label ch?""); answered: `ch` is the group of the helper `chars`, which `length`'s body uses; "ok, thats fine" in the ruling accepts it
rejected:
- (e) as first stated, "a joint entry stays a label form" — withdrawn by the manager on his question "why would (x,y): () form not allow values?" (record "2026-11-22 OWNER, two points after binding-prefix: should a label be REQUIRED to be known textually at its reference").
- (a) of count-in-set, a member of `occurs` taking the set (`occurs.in(S, c)`) — by owner ruling — count-in-set: b.
readings:
- (a) the parse: a bare name or label path left of `:` stays a LABEL, any other expression is a VALUE — the manager's call; run as the model's parse: the metadata line (`(w.index: >= 2)`, a path) and month_numbered's `(months.mname.index: S)` answer as printed before (predbound META, FIVE; sabotage s17 caught).
- (b) the value is SINGLE; several strings there are a compile error for now — UNTESTABLE as a rule (the manager's call); the model refuses `(($h + ["1", "2"]): <5)` and accepts `(($h + ["1"]): <5)` (predbound SEVERAL; sabotage s10 caught).
- (c) a value that yields nothing fails the entry, as an unset label does, and NOT holds on it — SUPPORTED as a run of the reading (predbound NOTHING: `(($a - 5): >= 0)` against `[5-9]`, its NOT against `[0-4]`, 0 / 0 / 0 of 31 texts over `0357x`; an unset input on `x`: the entry fails, NOT holds; sabotage s8 caught).
- (d) `($h: S)` and `(h: S)` answer alike in every mode — SUPPORTED (predbound SAMEREAD: 18 programs, 3 patterns, 3 sets, with and without NOT, 0 / 0 / 0 of 341 texts over `37x;`; sabotage s9 caught).
- (e) each component of a joint entry's left part may be a value, each single (R-2) — SUPPORTED as a run of the reading (predbound JOINTV: `((($a + $b), c): (<10, /\d/))` WHOLE against the direct rule, 0 of 300 texts differ; a joint entry inside a group question still refused); a default (`h = v`) stays a label form — UNTESTED (a parse rule).
- the record's two examples: `P & (count((d: "7")): ==2)` and `(($a + $b): <10)` give the printed lines of `count` and of the sum unchanged (predbound FIVE).
- (ANS-3, the manager's) a value entry inside a group question a compile error for now — SUPPORTED as run (docs/dev/lanes/predfix82_evidence/ predfix82_model.py VALUEGQ; sabotage s10, the value read as the label, caught); the two forms part inside a group question, shown by that plant
evidence: docs/dev/lanes/predbound_evidence/ predbound_model.py NOTHING, SAMEREAD, SEVERAL, META, FIVE, SUMALT.
history:
- 2026-11-22 (lane predbound, count-in-set ruled (b)): a new piece: the ruling, the manager's readings (d) of the brief, the lines "Nothing fails the entry", "NOT holds on nothing", "A read on the left", and the printed lines of `count` and of the sum written in place.
2026-11-22 (lane predbound, R-2): the reading "A default (`h = v`) and a joint entry stay label forms" became "each component of a joint entry's left part may be a value"; the line "A joint entry with a value" added.
- 2026-11-22 (lane predfix82, review r82 ANS-3, RULING-8 (d); record "2026-11-22 MANAGER — review r82 (predfold1122): dispositions ruled; two corrections of record entries (no owner words)"): "answer alike in every mode" restricted to outside a group question; a value entry inside one a compile error for now (a reading; the line "Inside a group question", predfix82 VALUEGQ); the default clause marked a reading.

## core/conditions/form/record-in-some — A record inside a group question
slugs: record-in-some
rulings:
- 2026-11-16 "record-is-product: absolutely. This is precisely the sort of simplifying semantics I'm looking for." (record: "2026-11-16 OWNER RULING — record-is-product: yes"); the rule the reading parts from inside a group question
- 2026-11-21 "join-in-some: agree and elegant. that said, no one would know to write it." (record: "2026-11-21 OWNER RULING — joint-in-some: agree (a joint entry inside a group question is refused for now; "same item" is written on the item)"); the joint spelling refused
rejected:
readings:
- (a) of array-vs-passes, each plain entry over its own array — SUPPORTED as a run (predfix77 RECORD: `some((h: "5", m: "3"))` WHOLE against the direct product, "some h is 5 and some m is 3", 0 of 341 texts over `53:,`; the joint spelling refused; sabotage s19 caught); that this is meant is the owner question.
evidence: docs/dev/lanes/predfix77_evidence/ predfix77_model.py RECORD; earlier predarr_model.py RECORD, JOINT.
history:
- 2026-11-22 (lane predfix77, review r77 A9; record "2026-11-22 MANAGER — review r77 (predfold1121): dispositions ruled (no owner words)"): a new open sub-piece; the slug was proposed by lane predarr ("2026-11-21 MANAGER — after lane predarr: array-vs-passes and joint-in-some folded; readings tested (no owner words)").

## core/conditions/two-valued — Conditions are two-valued
slugs: three-valued polarity-rule record-under-not zero-pass-record
rulings:
- 2026-11-17 "regex-settles: yes settled" (record: "2026-11-17 OWNER RULINGS — regex-settles; absent-under-not")
- 2026-11-17 "Absent under not: use regex rules." (record: "2026-11-17 OWNER RULINGS — regex-settles; absent-under-not")
- 2026-11-17 "polarity-rule: warning for both. Warnings are errors given some strictness setting eg @config.strict()" (record: "2026-11-17 OWNER RULING — polarity-rule")
- 2026-11-16 "not-is-complement: yes agree" (record: "2026-11-16 OWNER RULINGS — not-is-complement and mark-in-none")
- 2026-11-16 "zero-pass-record: I agree but save the notes in the future file. The issue falls into the 'saving people from themselves' category that tools need to realistically consider" (record: "2026-11-16 OWNER RULING — zero-pass-record: the outside label is tested"); a label outside the pairing loop is tested once when the loop runs zero passes, and a record is the `&` of its entries at every depth; the manager's 12:45 WORDING, empty satisfies any set, was reversed the same day by absent-rule 14:31, which keeps this ANSWER (`9` FAILS) and record = `&` (cited as "2026-11-16 OWNER RULING — absent-rule: LOCKED" on core/principles/no-absence)
rejected:
- "absence never matches, negated or not" (condition-not's absence clause) — by owner ruling — absent-under-not.
- three-valued logic (three-valued) — retired: the regex model entails it (the manager's reading, closed by regex-settles).
- record-under-not as a question — dissolved (a record is the `&` of its entries with or without NOT).
- a never-pass test as an error (the draft §5.2) — by owner ruling — polarity-rule.
readings:
evidence: preddoc3a_model.py TV (the draft's PART A U1 line; printed answers reproduced; the lowering agrees), TV2 (U2: `NOT (a: <5)` on `1` HOLDS); the three-spellings table is the draft §R.3's (N1-N4), reproduced by DEF for `(h = "x": !<5)`; sabotage s5 caught.
history:
- 2026-11-16: condition-not with "absence never matches"; 2026-11-17: regex-settles and absent-under-not reversed the absence clause; polarity-rule.
- 2026-11-19 (lane preddoc6, review r60 COLD-12): a column added to the three-meanings table on P = `/(?<h>\d)?\d?x/`, `3x` WHOLE: HOLDS / FAILS / FAILS. On the old column rows 1 and 3 were identical, so the table showed two meanings; the new column parts NOT from the complement form (P has two paths over `3x`, h = `3` and h unset). Run: docs/dev/lanes/preddoc6_evidence/ PART TV.

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
- (a), the same compile error, is THE DRAFT'S READING (rev 26.1, review r47 B4): "a GROUP holding ONLY conditions (`((h: <5))?`, `(c1 SEQ c2)*`) IS a condition for this rule, so a quantifier on it is the same compile error; read as regex it is exactly what the punt keeps out: `[h = rx.digit] SEQ ((h: <5))?` WHOLE `7` HOLDS (the test vanishes), `((h: <5) SEQ (h: <5))*` likewise, unquantified WHOLE `7` FAILS (rev 26.1's PART R47 B4; RULE-AS-CODE PART CS CS4's new row; sabotage s22 caught)" (the draft §R.1.14); the §R.8 row: "a condition: the same COMPILE ERROR", candidate regex with SEARCHED `x7` `7`@1 / FIND-ALL `7 3` [`7`@0, `3`@2] HAND-WORKED from the run there — re-run here (preddoc6 PART CG).
- open in the draft §R.8 ("condition-group"); never put to the owner (`grep -c condition-group` on the record: 0).
evidence:
history:
- 2026-11-19 (lane preddoc4): a new open sub-piece; the slug came from core/conditions/quantified, where it sat on a ruled piece.
- 2026-11-19 (lane preddoc6, review r60 FIXVER-4): restated from the frozen draft's own words for the slug. Before, the piece said "The reading today: not stated" and "modes: n/a (a question; no candidate answer is run)"; the draft has the reading ((a), the same compile error) and the runs (PART R47 B4, CS4), now printed; its example `(?:(a: S)(b: T))` replaced by the draft's `((h: <5))?`, `((h: <5) SEQ (h: <5))*`.

## core/conditions/match-so-far — The match so far
slugs: zero-in-sequence zero-in-definition
rulings:
- 2026-11-21 "zero-in-definition: a" (record: "2026-11-21 OWNER RULING — zero-in-definition: a"); answer (a) as put to him: "`0` is the match so far of the definition it is written in"; "within one definition `0` still spans all its literals and operands, so your ruled example is unchanged"
- 2026-11-19 "zero-in-sequence: you are a lawyer in your exact wording. this is what is needed now. the condition is always sees the regex composed at the point it is used. so the 0: is the match so far" (record: "2026-11-19 OWNER RULING — zero-in-sequence")
rejected:
- the error for now (the manager's leaning) — by owner ruling — zero-in-sequence.
readings:
- (the manager's (a) of zero-in-definition) an expression written in place (an argument, a hole's content) belongs to the definition it is written in — SUPPORTED by the words as put ("the definition it is written in"); run: `/\d/ SEQ B((0: /\d/))`, B(rx) := `/${rx}xx/`, the caller's `0` HOLDS on `5xx`, the macro's would never match (predscope_model.py ZARG; sabotage s11 caught).
- a program's final expression is the outermost definition (the lane's reading) — UNTESTED (no ruling names the program).
- (the manager's (d)) zero-in-loop is untouched and still open — SUPPORTED (the ruling's question and answer name definitions, not passes; core/conditions/match-so-far/in-loop unchanged).
- the ruled example `/\d/ SEQ (0: /7/) SEQ /\d/` unchanged — SUPPORTED (predscope_model.py ZSEQ; sabotage s9, `0` restarting at each operand, caught).
- a definition is a binding or a macro body (the manager's gloss, in the ruled statement until 2026-11-22) — UNTESTED (a reading; his "bindings define scope" (record: "2026-11-21 OWNER, his "issue definition" for bare-nested-scope: bindings define scope; flags are a symptom of PCRE, probably only `i` inherits; the two languages differ by construction; a sketch `list_of_stuff(X, cmp, S)`") supports it, not as a ruling).
- a condition joined by `&` reads its left operand's match as its `0` written as a SEQUENCE OPERAND too, as his confirmed hole example does (`A & B` = `A & (0: B)`, core/filters/and; review r77 A5, MODES-3) — SUPPORTED as a run (predfix77 SEQZERO: `/\d/ SEQ (/\d/ & (0: /\d/))` against `\d\d`, against the hole spelling `/\d${/\d/ & (0: /\d/)}/` and against `/\d/ SEQ (/\d/ & /\d/)`, 0 / 0 / 0 of 121 texts over `12x`; read from the definition's start it would FAIL on `12`; sabotage s4 caught).
- `0` in an `occurrences` argument (review r77 A6, MODES-4): the caller's definition (the reading today, from "an argument is the caller's"), the body of `occurrences`, or the hit's own text part on `/x?/ SEQ occurrences(/\d/ SEQ (0: /\d/), min = 1)`: three different lines (predfix77 OCCZERO: each against a hand regex, `\d(?s:.*)`, `x?\d(?s:.*)`, `x?(?:(?s:.*?)\d){1,}(?s:.*)`, 0 / 0 / 0 of 121; sabotage s5 caught). VERIFIED; the disposition is PLAN: a reading to state beside zero-in-loop, asked with it (the lines are in docs/dev/lanes/predfix77_report.md).
evidence: preddoc3a_model.py ZERO (the record's zeroseq.py answers reproduced; `7\d` agrees); sabotage s11 caught. preddoc1 PARTS R8, R9. predfix77_model.py SEQZERO, ZEROARG, OCCZERO.
history:
- 2026-11-19: zero-in-sequence; the bare condition in a hole; the confirmation. The slug number-in-loop moved to core/labels/numbers/in-loop (lane preddoc3a).
- 2026-11-19 (lane preddoc4): the deciding piece for `0` (core/labels/numbers points here); the bare-condition-in-a-hole facts are core/holes/bare-condition's alone (review r59 RULING-8); the loop case moved to the open sub-piece core/conditions/match-so-far/in-loop (review r59 ZERO).
- 2026-11-19 (lane preddoc6, review r60 FIXVER-2): one owner for the hole facts: the base clause "in `${A & (0: S)}` it is A" and the two hole rulings items (""Inside an inserted part": for a condition bare, yes ..." and "yes, thanks: /\d${(&(0:digit))}/ and /\d/ & (0: digit) are the same thing") and the `rejected:` line "a bare condition's `0` in a hole as the inserted part's own" removed here; core/holes/bare-condition carries all three, word for word.
- 2026-11-21 (lane predscope, zero-in-definition folded): statement until then: "`0` in a condition names the match so far: the text the rx the condition is written in has matched from its start to the condition's point." Bullet until then: ""The rx it is written in" is the rx composed at the point the condition is used; every hole case (a condition alone in a hole, `${A & (0: S)}`) is core/holes/bare-condition's." Now the DEFINITION it is written in; within one definition composed; three readings and the "An argument" line added. Status date 2026-11-19 to 2026-11-21.
- 2026-11-22 (lane predfix77, review r77 D5, A5, A4; record "2026-11-22 MANAGER — review r77 (predfold1121): dispositions ruled (no owner words)"): statement until then, verbatim: "`0` in a condition names the match so far: the text the definition the condition is written in (a binding or a macro body) has matched from its start to the condition's point." The gloss became a marked reading; the `&` operand bullet and the line "As a sequence operand" added. No answer moved.

## core/conditions/match-so-far/in-loop — The match so far inside a loop
slugs: zero-in-loop
rulings:
rejected:
readings:
- the reading today, (b), from the definition's start ("the rx's" until 2026-11-22): the manager's reading (c) of the zero-in-sequence entry ("inside a loop the match so far includes the earlier passes (from the rx's start, not the pass's): to run") — SUPPORTED as a model by preddoc1 PART R9 (the callout model: the match's start, not the pass's; the two differ on 4 / 16 / 28 of 364, first `3;3;`); not his words.
- (a), the pass's: the base said it before (core/labels/numbers, "inside a loop body, the pass's"), the draft's reading; his "the 0: is the match so far" and "composed at the point it is used" do not say which start a pass has — the two readings stood in two pieces (review r59 ZERO); asked as zero-in-loop.
- the witness `(/\d/ SEQ (0: /\d/) SEQ ";")+` on `3;4;`: (a) WHOLE HOLDS, (b) WHOLE FAILS — SUPPORTED (preddoc4 PART ZL; sabotage s7, (b) in both lines, caught).
evidence: docs/dev/lanes/preddoc4_evidence/ PART ZL; preddoc1 PART R9.
history:
- 2026-11-19 (lane preddoc4): a new open sub-piece: the two readings of `0` in a loop stated once, as a question (review r59 ZERO).
- 2026-11-22 (lane predfix77, review r77 D12 (FIXIND-6); record "2026-11-22 MANAGER — review r77 (predfold1121): dispositions ruled (no owner words)"): "the rx" became "the definition it is written in" in the statement, the reading and candidate (b) (zero-in-definition's unit). The printed program is one definition; its lines do not move.

## core/conditions/pass-start-read — Labels as they stand
slugs: pass-start-read
rulings:
- 2026-11-17 "pass-start-read: yes keep it" (record: "2026-11-17 OWNER RULING — pass-start-read")
- 2026-11-17 "I do want that. It makes sense and frankly pcre is wrong on this." (record: "2026-11-17 OWNER RULING — what an unqualified `$x` reads")
rejected:
- a "pass begins" reset rule — by owner ruling — pass-start-read (keep the previous pass's value before the group).
- `$x` "as standard pcre" (pass-list-read's literal reading) — by owner ruling — the `$x` ruling: `$x` reads the label.
- a warning on a bare condition over a looped label (the manager's own proposal, looped-warning) — by owner ruling — looped-warning: "I agree remove warning." (core/diagnostics/looped-compare).
readings:
- the test written in its hole, `${NOT (h: /\d/) | (n: >= $h)}`, gives the printed line of the bound `c` unchanged — SUPPORTED (predbound FIVE: the line rebuilt from the program text equals the line printed at 1e0384941; WHOLE against "the digits are non-decreasing" 0 of 19,531 texts over `3471;` differ; sabotage s2 caught on the sum).
evidence: preddoc3a_model.py PSR (the draft's PART PS line; printed answers reproduced) and PSR2 (WHOLE equals "the items are non-decreasing" on 1,365 texts over `139;`); sabotage s12 caught.
history:
- the draft R.1.7; 2026-11-17 pass-start-read and the `$x` ruling.
- 2026-11-16 looped-compare ("looped-compare: warn", record "2026-11-16 RULING — a compare over looped labels warns"): the warning on a compare over looped labels was MOVED by joint-loops (3) onto a `|` of conditions over labels that can repeat (record "2026-11-16 OWNER RULING — joint-loops: agreed, all three parts"); after after-loop-read (core/labels/labels-vs-captures) a bare condition reads the last pass's own label and the draft withdrew `compare.looped` with looped-warning (§R.2, rejected above). The slug is homed here with that rejected line (lane preddoc5).
- 2026-11-19 (lane preddoc6, review r60 LOOPED / RECOUNT-1): the line above read a MANAGER's withdrawal as the end of an OWNER-ruled warning. The warning stands as joint-loops (3) left it (core/diagnostics/looped-compare, both rulings cited there); whether it is still wanted is open (core/diagnostics/looped-compare/still-wanted). The slugs looped-compare and looped-warning moved to those two pieces.
- 2026-11-19 (lane predfix61, review r61 F-I, RULING-2, STALE-2): the rejected item until then: "a warning on a bare condition over a looped label (the manager's own proposal, looped-warning) — withdrawn by the manager (the draft §R.2); the question is open (core/diagnostics/looped-compare/still-wanted)." The question was answered (looped-warning) and the tag merged.
- 2026-11-22 (lane predfix77, review r77 A3; record "2026-11-22 MANAGER — review r77 (predfold1121): dispositions ruled (no owner words)"): a pointer to the open core/holes/bare-condition/bound-condition: this piece's bound definition is read where it is used (a reading).
2026-11-22 (lane predbound, bound-condition ruled; record "2026-11-22 OWNER RULING — bound-condition: "mostly confirmed"; `c := (0: 5)` left open"): the line's program until then, verbatim: "(`/(?:(?=(?<n>\d))${c}(?<h>\d);)*/`, c := `NOT (h: /\d/) | (n: >= $h)`)", and the bullet "The line's `c` (depends on the open bound-condition: core/holes/bare-condition/bound-condition)."; `c` names `h` and `n`, which no pattern in its binding holds: a compile error now. Status date 2026-11-17 to 2026-11-22. The answers do not move.

## core/conditions/defaults — Defaults and absent labels
slugs: default-set unset-component drop-mark default-value match-context zero-pass-empty domain-scope mark-narrows mark-in-none mark-range mark-under-not one-witness default-reaches-dollar default-scope mark-design
rulings:
- 2026-11-16 "default-scope: yes per test" (record: "2026-11-16 OWNER RULING — default-scope: per test")
- 2026-11-16 "colon-scope: yes with refinement: (a, b = c): ... the 'c' is a binding et al" (record: "2026-11-16 OWNER RULING — colon-scope: yes, with a refinement for a default")
- 2026-11-16 "We can punt, as you say, and throw an error. Perhaps a reason will open to reconsider." (record: "2026-11-16 OWNER RULING — default-set: a default of several strings is an error, for now; idea: `some(...)`"); RULED for now: a default is ONE string; his "Then there is a = some(between(...))" is an idea (parked/ideas/default-set)
- 2026-11-16 "unset-component: yes" (record: "2026-11-16 OWNER RULINGS — unset-component: yes; default-unused: agree"); an unset label fails the condition, single or joint, unless the author wrote a default for it
- 2026-11-16 "Drop-mark: yes" (record: "2026-11-16 OWNER RULINGS — drop-mark, default-value, source-row; default-scope to a lane"); the optional mark is OUT of the language: an absent label never matches, the author gets past it with a default; it RETIRES zero-pass-empty, match-context, domain-scope, mark-narrows and mark-in-none (they lose their subject) and absent-rule's clause offering the mark
- 2026-11-16 "Default-value: yes" (record: "2026-11-16 OWNER RULINGS — drop-mark, default-value, source-row; default-scope to a lane"); a default may be any text, including one the label can never hold; a warning only on a default that can never be used
rejected:
- a default reaching past its own test (per program) — by owner ruling — default-scope.
- the optional mark on a label (`h?`, `(h?: <5)`, `((h, m?): R)`: "some value the label could hold", rev 20-22) — by owner ruling — drop-mark ("Drop-mark: yes"): an absent label never matches; the author writes a default. Cost named to him: `(h?: <5) & (k: <5)` on `b3` FAILS with the mark, HOLDS without it unless the author picks another default (45 of 680 program pairs, the record).
- a default that is a set of several strings, read as "every member fits" or "some member fits" — by owner ruling — default-set: a compile error for now; the author-written `some(...)` is parked (parked/ideas/default-set).
- rev 18's decided-prefix reading of a joint condition with an unset component — by owner ruling — unset-component ("rev 18's decided-prefix reading is withdrawn", the record).
- a default restricted to the values the label could hold — by owner ruling — default-value: any text (parked/ideas/default-range keeps the idea).
- default-reaches-dollar (the manager's derivation, 16:23: a default fills an own-label `$a`) — by owner ruling — default-scope (`$h` reads the real label; the draft §R.5 E).
readings:
- a default outside the test's set reads as no default at every polarity (the draft R.1.6) — SUPPORTED (preddoc3a_model.py DEF: `x` HOLDS as with no default).
evidence: preddoc3a_model.py DEF (the draft §R.3 N4 line; printed answers reproduced; `[5-9]?x` agrees); sabotage s13 caught.
history:
- 2026-11-16: default-scope (a lane considered both), then ruled per test.
- 2026-11-19 (lane preddoc5): the slug nullable-meaning moved to lib/search/occurrences (review r59 COMPA-13).
- 2026-11-16, the optional mark's rulings, each RETIRED by drop-mark (cited above), none reversed: "match-context: anywhere. This does need some sort of debugger for writing these." (record: "2026-11-16 OWNER RULING — match-context"); "zero-pass-empty: agree. If nothing could pass then some absent value of present couldn't either. I agree with your reading." (record: "2026-11-16 OWNER RULING — zero-pass-empty"); "P & (k: \"b\") In my mind this is a different regex than P. It only includes the \"b\" track" (record: "2026-11-16 OWNER RULING — domain-scope"); "I agree with your variant. I'm assuming such logic is possible" (record: "2026-11-16 OWNER RULING — mark-narrows"); "mark-in-none: I'd leave it. It's obscure and there are ways to get the intended question." (record: "2026-11-16 OWNER RULING — mark-in-none: LEFT AS IS"; his 17:29 "yes agree" on it was withdrawn by him minutes later, record "2026-11-16 CORRECTION — mark-in-none is NOT ruled"). With the mark went mark-range (withdrawn in the drop-mark entry), the manager's one-witness and not-of-marked readings, and the draft's question mark-under-not (closed with the mark).
- 2026-11-16: default-set (one string, for now), unset-component, drop-mark and default-value (homed here by lane preddoc5: review r59 COMPA-2, COMPA-3, COMPB-6).

## core/filters/and — The `&` operator
slugs:
rulings:
- 2026-11-15 "That's a good clarification" (record: "2026-11-15 RULING — the sides of `&` "match the same stretch whole"; the word "anchored" is kept for the macro")
- 2026-11-17 "operand-context: yes to that interpretation. Also, then the start of subject and end of subject need the same interpretation" (record: "2026-11-17 OWNER RULING — operand-context")
- 2026-11-17 "join-order: left side decides. That's always how I thought of it. In concedes the logical purity that you seemed to be going for for the reality that regex is not pure." (record: "2026-11-17 OWNER RULING — join-order: the left side decides")
- 2026-11-17 "For A & B: from the perspective of B, the subject is now whatever A matched." (record: "2026-11-17 OWNER RULING — zero-place: a pattern's numbers are labels in its own world")
- 2026-11-15 "&: both sides filter and warn if anchor. Agree but test if it makes sense. Like in a hole, what does it mean that they are anchored?" (record: "2026-11-15 CORRECTION and RULING"); part (b): both operands of `&` are filter roles, the operator stays symmetric, an explicit anchor in an operand draws the warning (core/diagnostics/warnings)
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
- 2026-11-14 "1. agree" (record: "2026-11-14 RULING — Q1 foundation"); on review 2026-11-14-r1-predspec's proposed answer: in a SET POSITION an edge assertion is a compile error naming the fix; NARROWED, not withdrawn: operand-context (above) states the filter operand's case, hole-reading the hole's
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
- 2026-11-16 "row-is-match: yes I agree." (record: "2026-11-16 OWNER RULING — row-is-match"); a complement after `&` filters potential matches, one row each: `t2 & !q` searched on `9:30` HOLDS reporting `9`; it SUPERSEDES the 21:49 source-row wording (history)
rejected:
- `!` on a condition as a compile error (the second half of not-is-complement, "no meaning on a condition") — by owner ruling — REVERSED the same evening by condition-not (record: "2026-11-16 OWNER RULING — condition-not: allowed"); the spelling on a condition is `NOT` (core/filters/negation, a reading). The not-is-complement item above stands for its first half only (`!` on a pattern is a complement).
- a complement per SUBJECT (source-row's wording, "a row of the source is the whole subject; the complement is per subject") — by owner ruling — row-is-match: a row is one potential match, the subject is the search text.
readings:
- a complement inside an `occurrences` argument rejects a path (nested-complement, entailed by hit-carry's premise) — SUPPORTED by the draft's PART RS RS1 (81 of 364 differ from the committed reading), not re-run here.
- `!` in rx text keeps PCRE's meaning (the 2026-11-15 correction: `!` inside a normal rx is parked) — UNTESTED.
evidence: preddoc3a_model.py COMP (`(?!7)\d+` agrees; the draft's `712` FAILS reproduced); sabotage s14 caught.
history:
- 2026-11-16 not-is-complement; 2026-11-17 regex-settles (2); 2026-11-18 complement-place.
- 2026-11-19 (lane preddoc6, review r60 SOURCE-ROW / RULING-2 / RECOUNT-4): the `rulings:` item "2026-11-16 "Source-row: yes" (record: "2026-11-16 OWNER RULINGS — drop-mark, default-value, source-row; default-scope to a lane"); a row of the source is the whole subject; a searched pattern gives several result rows per subject; the complement is per subject" REMOVED: that wording was "the MANAGER's framing of the question" (record "2026-11-16 OWNER REMARKS — what a row is; negating a condition; the value of a complemented pattern") and row-is-match "SUPERSEDES the 21:49 source-row wording" the same night (cited above). The slugs source-row and searched-complement moved to core/model/match, the piece row-is-match decides.
- 2026-11-19 (lane preddoc6, review r60 RULING-4): the `rejected:` line "`!` on a condition — by owner ruling — not-is-complement (a compile error naming the two rewrites)" stated the half of not-is-complement that condition-not reversed the same evening; rewritten.

## core/filters/kinds — Can match, can filter
slugs: complement-place lone-complement-match
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
- 2026-11-19 (lane preddoc6, review r60 DAMAGE-3): the ruled statement narrowed to what the rulings carry; before: "`!X` is the complement of a pattern or set; `NOT T` on a condition or a zero-width pattern is the negative lookahead `(?!T)`; no other spelling of negation exists." Its two readings (NOT on a zero-width pattern; no other spelling) are bullets marked "(a reading)"; the record writes `!` on a condition (condition-not: "`!` on a condition is LEGAL").

## core/values/reads — Reading a label
slugs: value-filter pass-list-read
rulings:
- 2026-11-18 "what i want is that $y works like label. however, there is a way to get the pcre capture value" (record: "2026-11-18 OWNER RULING — hole-reads-capture: the label; and a way to get the PCRE capture value")
- 2026-11-18 "Yes $y is a single value read at run time. At runtime, it is manipulated by left() et al using string manipulation built for simple strings. Semantically, $y is a regex of a single string. So operations that work on regex should work on it." (record: "2026-11-18 OWNER RULING — read-is-constant: yes; two forms of each operation")
- 2026-11-18 "unset-in-hole: i meant what you describe "no string" as. its a regex that matches nothing. that would be a good constant to provide" (record: "2026-11-18 OWNER RULING — unset-in-hole: no string, a regex that matches nothing; and an idea, a constant for it")
- 2026-11-17 "pass-list-read: unqualified it is the last pass as standard pcre. I would like a form that allows other passes but it should be clear that that is what is requested. Specifically, it should have different spelling. Eg Perl uses @x. An array of such values is its own type." (record: "2026-11-17 OWNER RULING — pass-list-read"); point (1), what an unqualified `$x` reads, was REOPENED by him minutes later in the same entry and settled by the `$x` ruling (core/labels/labels-vs-captures); points (2), the other passes by a visibly different spelling (`@x`), and (3), an array is its own type, STAND
rejected:
- a read is PCRE's capture (`${$y}` = `\k<y>`) — by owner ruling — hole-reads-capture; run: the capture gives `3-3;-3;` HOLDS / `3-3;-3;`@0 / [`3-3;-3;`@0, ``@7, `7-7;`@8, ``@12] against the label's FAILS / `3-3;`@0 (preddoc3b EXreads; the draft's PART HR of rev 28, 2 / 2 / 2 of 21,845; sabotage s1 caught).
- "No conditions. No &." on a read (his own discussion, part (5)) — by owner ruling — read-is-constant ("we were applying & to $y"): value-filter answered legal (the draft's A5).
readings:
- a `$y` in an rx that does not define y is free-name's compile error (the draft R.1.15 (11), the manager's, SUPPORTED by the marks, not by a ruling) — UNTESTED (a refusal).
- a read in a hole needs the group's TEXT kept during the match whether or not the group is returned (the manager's m3, hand-worked) — UNTESTED.
- rx text (`\k<y>`, numbers) resolves in its literal, PCRE's own scope, where a language read resolves in its definition: a deliberate difference (review r77 GENERAL-4, NOTED) — UNTESTED (a reading; witness `D := /(?<h>a)/ SEQ /\k<h>/`: a compile error by the literal unit, where `(h: "a")` at the same place is legal).
evidence: preddoc3b EXreads; PART HR of predspec28.
history:
- 2026-11-21 (the manager, bare-nested-scope case 2): the value-hole clause: every label visible in the definition the hole is written in; a separately defined piece reads only its own settings (bare-nested-scope ruled). Before: "in a value hole, every label visible in the surrounding rx (core/labels/export) as it stands at the hole; which labels, when the definition holding the hole is used inside another or is an `&` operand, is core/holes/bare-condition/nested-scope's (his three examples; a label its user sets is open)."
- 2026-11-18: hole-reads-capture and read-is-constant; the draft R.1.15 (3), (11), R.1.16 T20, A2, A5, A23. His recollection of the label-only group (parked/ideas/label-only-group) is not folded.
- 2026-11-19 (lane preddoc3b): converted from the skeleton; the example is the ruled witness.
- 2026-11-19 (lane preddoc4): "a read of a name the rx it is written in does not define is a compile error" restated as the one scope rule for `$` (a reading, tied to open bare-condition-labels): read literally it made the core's own examples (`$x` in an `&` operand, `${$y + 1}`) errors (review r59 READ-7).
- 2026-11-19 (lane preddoc5): the slug pass-list-read moved here from core/conditions/pass-start-read: it asks what `$h` reads after the pattern, which this piece states (review r59 COMPA-13).
- 2026-11-19 (lane predfix61, review r61 F-E, REACH-2): "the surrounding rx's labels as they stand at the hole" reached a private `_v` of an inserted binding and the labels behind `[_ = A]`; now "every label visible in the surrounding rx (core/labels/export)", and which rx, for a hole in an inserted literal or an `&` operand, a reading (core/holes/bare-condition/nested-scope). The sentence until then, verbatim: "A `$` read resolves in the namespace at the point it is written: in an `&` operand, the chain's labels; in a value hole, the surrounding rx's labels as they stand at the hole." Status date 2026-11-18 to 2026-11-19.
- 2026-11-21 (lane predscope): the pointer to nested-scope restated (a definition used inside another, not "the literal is itself inserted"); no answer moves.
- 2026-11-22 (lane predfix77, review r77 D2 (FIXIND-14), A8, A3, GENERAL-4; record "2026-11-22 MANAGER — review r77 (predfold1121): dispositions ruled (no owner words)"): status date 2026-11-19 to 2026-11-21 (its value-hole clause was changed by bare-nested-scope case 2); "PCRE's capture (the last value a group of the name set)" became "PCRE's capture (its value for the name: core/labels/labels-vs-captures)"; the NAMES clause points at bound-condition; the rx-text difference stated once.
2026-11-22 (lane predbound, bound-condition ruled; record "2026-11-22 OWNER RULING — bound-condition: "mostly confirmed"; `c := (0: 5)` left open"): the namespace bullet's "a condition or computed label bound alone is the open core/holes/bare-condition/bound-condition" became the ruled compile error. Status date 2026-11-21 to 2026-11-22.

## core/values/one-type — One type: a match is an rx
slugs: match-is-rx read-is-constant value-is-pattern hole-member-kind
rulings:
- 2026-11-18 "value-hole: let's use the unifying idea for it. Change my answers to match." (record: "2026-11-18 OWNER RULING — match-is-rx: the unifying idea; "Change my answers to match"")
- 2026-11-18 "That means, in practice, that there are two forms for each of them: the compile time version that works on general regex, and the runtime version that,while compiled, works on single value strings at run time. So $y + 1 and \d + 1 look the same, the first one happens at run time, and the second at compile time." (record: "2026-11-18 OWNER RULING — read-is-constant: yes; two forms of each operation")
- 2026-11-18 "We can create functions like left() and restrict them to constants now. I'd like to consider that unbuilt territory however and the error is an "under construction" sign." (record: "2026-11-18 OWNER RULING — match-is-rx: the unifying idea; "Change my answers to match"")
rejected:
- "$x is not a pattern but a match" (his ground for keeping `$x & <5` an error, 2026-11-17) — by owner ruling — match-is-rx ("Change my answers to match"): `$x & <5` is legal (the draft's A1, A2); run: equal to `(x: <5)` on the digit run (preddoc3b EXonetype; sabotage s2, the chain not re-entering `\d+`, caught).
- a value in a pattern position is a STRING, not a one-member pattern (the draft rev 26's text) — by owner ruling — match-is-rx (A3); no answer moves.
- "adding two patterns is an ordinary type error" (the manager's) — by owner ruling — match-is-rx removes the type ground; plus-operands rules nothing (core/values/arithmetic).
readings:
- the condition and the macro stay their own kinds (the lane predspec27's reading) — the CONDITION's own kind is the owner's DIRECTION (record: "2026-11-16 OWNER DIRECTION — conditions are their own kind", cited on core/conditions/form); that it survives the one-type ruling, and the macro's own kind, are UNTESTED.
- the composition rule, the stricter status wins (the draft's reading, review r48 FIXIND-10) — SUPPORTED as rule-as-code (PART TT of predspec28, sabotage s14).
- a computed value is a one-string rx known at run time, like a read (the draft's A11) — UNTESTED.
evidence: preddoc3b EXonetype; PARTS UT, TT of predspec27, predspec28.
history:
- 2026-11-18: value-is-pattern (one ruling, two leans, one idea), then value-hole "yes but", then match-is-rx and read-is-constant; the draft R.1.16 ONE TYPE, THE TYPE TABLE, ANSWERS CHANGED A1-A36.
- 2026-11-19 (lane preddoc3b): converted from the skeleton; the type table's rows are homed by position and operation (core/holes/*, core/values/*, core/arrays/*), not copied.
- 2026-11-19 (lane preddoc6, review r60 RECOUNT-5): slug hole-member-kind homed here: asked at rev 25 (the draft's changelog), folded into value-is-pattern (the draft's R.8 row 74, rev 26); never answered under its own name.

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
slugs: tuple-value tuple-anywhere set-arity two-orders record-is-product modifier-lift library-not-syntax retire-paused tuple-compare tuple-names tuple-arg-order
rulings:
- 2026-11-22 "label-reference: required. we can relax it later as you say although i'm not inclined to." (record: "2026-11-22 OWNER RULING — label-reference: required"); the example's joint entry names `time`'s labels through its name
- 2026-11-21 "join-in-some: agree and elegant. that said, no one would know to write it." (record: "2026-11-21 OWNER RULING — joint-in-some: agree"); a joint entry inside a group question is refused for now; "same item" is written on the item (core/labels/labels-vs-captures/array-vs-passes)
- 2026-11-21 "if they wanted the h5,m3 condition to be held at the same time they could have specified (h,m): (5,3) but they did not." (record: "2026-11-21 OWNER RULING — array-vs-passes: a"); his claim about the joint spelling, checked the same turn: inside a group question a joint entry meets two arrays and no rule paired them; then refused (joint-in-some)
- 2026-11-16 "A pair as a value: I am ok with the tuple as a value. My request is that it's fleshed out and not the slice of an idea." (record: "2026-11-16 OWNER RULING + REQUEST — the tuple as a value: OK, to be fleshed out")
- 2026-11-16 "I meant left right in the expression sense around = You could use them as you say" (record: "2026-11-16 OWNER CLARIFICATION + ANSWER — "left/right" was about the binding sign; tuple-anywhere: yes")
- 2026-11-16 "I think the tuple mechanism as otherwise described handled the problem more simply which I like." (record: "2026-11-16 OWNER — on first-rest: the built-in tuple mechanism is simpler, "which I like"; and a question")
- 2026-11-16 "Set arity: yes. It's clean. I like it" (record: "2026-11-16 OWNER RULING — set-arity: a set carries an arity")
- 2026-11-16 "I agree. They look sufficiently different to me and I like the control." (record: "2026-11-16 OWNER RULING — two-orders: keep both")
- 2026-11-16 "record-is-product: absolutely. This is precisely the sort of simplifying semantics I'm looking for." (record: "2026-11-16 OWNER RULING — record-is-product: yes")
- 2026-11-16 "modifier-lift: yes. Add this as another item like first/last to a 'predicate future consideration' document to consider finer grain transforms. However the form is 'do everything to both' so the logic makes sense" (record: "2026-11-16 OWNER RULING — modifier-lift: yes; a "future consideration" document"); a modifier around a set of tuples acts on EVERY part; a per-part transform is parked (parked/ideas/partial-transforms)
- 2026-11-16 "library-not-syntax: agree. we've replaced the idea and I think with something much better" (record: "2026-11-16 OWNER RULING — library-not-syntax: the 11-14 ruling is withdrawn"); the 2026-11-14 "TUPLE CONDITIONS: a LIBRARY macro, no syntax" is WITHDRAWN BY NAME; a tuple on the left of `:` is syntax
- 2026-11-16 "retire-paused: agree to split. But the pause on ^ is indefinite and requires real value other than 'override a users own *'" (record: "2026-11-16 OWNER RULING — retire-paused: split; the sigil's pause is indefinite"); RETIRED: the `lex_` names, their argument order, the fixed-size compares' first-library slot (the joint condition takes it); the sigil PAUSED (parked/ideas/other-side-sigil)
rejected:
- a third value kind for a set of tuples — by owner ruling — set-arity ("No third value kind", the record).
- first/rest binding with recursion as the order's definition — by owner ruling — first-rest PARKED (parked/ideas/first-rest).
- a warning between the two orders (the manager's lean) — by owner ruling — two-orders ("I like the control"; the record keeps both with no warning).
- the six tuple compares `lex_ge2`, `lex_le2`, `lex_between2`, `lex_ge3`, `lex_le3`, `lex_between3` over arrays (`lex_between2([h, m], [9, 0], [10, 0])`) — by owner ruling — retire-paused (the comparison sets on a tuple atom, `((h, m): >= (9, 0))`, say the same with no library family).
- their argument order subject, low, high — by owner ruling — retire-paused (retired with the names).
- the fixed-size compares (2 and 3 fields) in the first library — by owner ruling — retire-paused: the joint condition takes that slot.
- the 2026-11-14 "TUPLE CONDITIONS: a LIBRARY macro (`lex_ge([major, minor, patch], [1, 4, 0])`), no syntax" — by owner ruling — library-not-syntax ("we've replaced the idea").
- `lex_ge` and friends kept as ordinary library macros over the joint condition (the middle path) — by owner ruling — library-not-syntax, the manager's reading of "agree" (told to him): left out of the first library until someone asks.
- the strict spelling `lex_ge2(s, lo) & !lex_le2(s, lo)` — retired with the names; the strict compare is `> (9, 0)` (core/values/comparisons).
readings:
- each component read by its literal and in its literal's domain (`((h, m): >= (9, 0))` rejects `9:00`, `00` not canonical) — the manager's reading DICT-DOMAIN (the draft §2.4), not run here.
- how a tuple parses apart from a record (a parenthesised comma list standing as a value) — the reading the base states; the spelling is a placeholder.
- `time & ((h, m): >= (9, 30))` (as printed before label-reference; today `time & ((time.h, time.m): >= (9, 30))`, the base line): WHOLE `9:45` HOLDS, `9:15` FAILS, `10:15` HOLDS / SEARCHED `10:30`@5 / FIND-ALL [`9:30`@0, `12:45`@10] — SUPPORTED (preddoc4 PART TU; sabotage s5, the per-part form, caught on `10:15`).
- tuple-parts (taking ONE tuple apart) is OPEN: core/modules/positional.
- WHICH macros lift (the manager's reading of "do everything to both", review r26 OWNER-5, told to him): a macro whose result distributes over `|` in its argument, checkable from its body (`padded`'s `/0*${rx}/` does); one that does not is the arity error — UNTESTED here (the draft §2.7).
evidence: docs/dev/lanes/preddoc4_evidence/ PART TU; the draft §2.4 (TUPLE ATOMS), joint_condition.md item 4.
history:
- 2026-11-19 (lane preddoc4): a new piece: the tuple had no piece and its spelling read as a record (review r59 PRIMITIVES-MISSING, READ-15).
- 2026-11-15/16, the tuple-compare library direction (rev 16-19, the draft §16), RETIRED by retire-paused (cited above): "tuple-compare: agree" (record: "2026-11-15 RULINGS — tuple compare in the first library; `any_case` stays a primitive for now, a more fundamental basis is a FOLLOW-UP", part (a)); "tuple_names: a" (record: "2026-11-15 RULING — tuple compare names"; the slug tuple-names); "tuple-arg-order: subject low high" (record: "2026-11-15 RULING — tuple compare argument order").
- 2026-11-16: modifier-lift (the base bullet added by lane preddoc5, review r59 COMPA-1; the draft §2.7 MODIFIERS ON TUPLE SETS states it); library-not-syntax; retire-paused.
- 2026-11-21 (lane predarr): a bullet added, a joint entry inside a group question is refused for now (joint-in-some). Status date 2026-11-16 to 2026-11-21.
- 2026-11-22 (lane predfix77, review r77 A9; record "2026-11-22 MANAGER — review r77 (predfold1121): dispositions ruled (no owner words)"): "one mechanism" qualified "outside a group question (open record-in-some)".
- 2026-11-22 (lane predref, label-reference sweep and helper-captures fold): the line's program `time & ((h, m): >= (9, 30))` re-spelled `time & ((time.h, time.m): >= (9, 30))`; answers unchanged (docs/dev/lanes/predref_evidence/ predref_model.py RESPELL, the tuple comparison lowered as the dictionary order). Status date 2026-11-21 to 2026-11-22.

## core/values/computed-labels — A computed value in an entry
slugs:
rulings:
- 2026-11-14 "I agree with both excepting the spelling ... no alpha operators ... with, check, in ... check is not `x := ...` ... don't want to go into new grammar lightly" (record: "2026-11-14 RULINGS on docs/dev/lanes/predx_report.md §11")
rejected:
- a computed label BOUND to a name of its own and named left of `:` like a label (`sum := $a + $b`, `(sum: <10)`) — by owner ruling — bound-condition: "a computed label bound alone ... is the same form and is illegal" (the manager's list, confirmed: record "2026-11-22 OWNER RULING — bound-condition: "mostly confirmed"; `c := (0: 5)` left open").
- a computed label's value is "a VALUE, not a pattern" (the draft §4.4, §11) — by the draft (rev 27.1, R.9 row 68), following value-is-pattern — CHANGED: a one-string rx known at run time.
readings:
- "a match-dependent binding is a computed label of the pattern whose labels it reads" — the manager's spelling LEAN in the same entry, the concept (compile-time checks and match-dependent bindings, no new grammar) agreed; the base's statement is that lean — a reading.
- an unset input gives nothing and the comparison against it fails (the base bullet; core/conditions/form/value-left) — a reading, UNTESTED. Withdrawn with the binding form: "an unset input gives an unset computed label" (preddoc3c's proposal).
- `(($a + $b): <10)` written in place gives the line once printed for `sum` unchanged — SUPPORTED (predbound FIVE: 0 of 140 texts differ from the direct sum < 10; sabotage s2 caught); `(a: <(10 - $b))` answers alike on the 100 digit pairs, 0 differ, 55 hold (predbound SUMALT; sabotage s12 caught).
- (f) of the brief: the piece restated as a computed value in an entry, no binding form; `count`'s "it may be bound and read like a label" withdrawn — done (predbound MARKS).
evidence: docs/dev/lanes/preddoc4_evidence/ PART CL; the draft §4.4.
history:
- 2026-11-19 (lane preddoc4): a new piece: length and month_numbered name bindings left of `:` with no core rule allowing it (review r59 PRIMITIVES-MISSING, READ-8).
- 2026-11-19 (lane preddoc6, review r60 RECOUNT-6): the draft R.9 candidate for this piece, PARTIAL at r59 and left unchanged by preddoc5, now has its own `rejected:` line.
- 2026-11-21 (lane predarr, array-vs-passes ruled): the last bullet's "a computed label over a loop's passes is a group question" became "over a name's settings (its array)". No answer moves.
- 2026-11-22 (lane predfix77, review r77 A3; record "2026-11-22 MANAGER — review r77 (predfold1121): dispositions ruled (no owner words)"): a pointer to the open core/holes/bare-condition/bound-condition: this piece's bound definition is read where it is used (a reading).
2026-11-22 (lane predbound, bound-condition and count-in-set ruled): renamed from "Computed labels"; the statement until then, verbatim: "A binding whose expression reads a match label is a computed label of the pattern whose labels it reads: a one-string value per path, read by `$` and named left of `:` like a label."; the readings item until then, verbatim: "`sum := $a + $b`, `/(?<a>\d)\+(?<b>\d)/ & (sum: <10)`: WHOLE `3+4` HOLDS, `7+8` FAILS / SEARCHED `2+2`@4 / FIND-ALL [`1+1`@0, `5+4`@8] — SUPPORTED (preddoc4 PART CL; sabotage s11, the concatenation, caught)."; the line's program `(sum: <10)`, sum := `$a + $b` became `(($a + $b): <10)`. Status date 2026-11-19 to 2026-11-22; still a reading.
- 2026-11-22 (lane predfix82, review r82 GENERAL-8, DES-1; record "2026-11-22 MANAGER — review r82 (predfold1122): dispositions ruled; two corrections of record entries (no owner words)"): reduced to its in-a-set fact: statement until then "A value computed from match labels (`$a + $b`, `count(c)`, `$w.index`) is written in place, left of `:` or in a set; it is never bound alone to a name."; the value-left and bound-condition restatements removed; its line now the set form (predfix82 REPRINT). Not merged into value-left (no restructuring this round).

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
- 2026-11-22 (lane predref, label-reference sweep and helper-captures fold): the line's program `/${days}/ & (w.index: >= 2)` re-spelled `/${days}/ & (days.w.index: >= 2)` (label-reference; predbound META had run it); the bullet "Read like labels" says where the bare form stands. Answers unchanged (docs/dev/lanes/predref_evidence/ predref_model.py RESPELL). Status date 2026-11-19 to 2026-11-22.
- 2026-11-22 (lane predfix82, review r82 GENERAL-8; record "2026-11-22 MANAGER — review r82 (predfold1122): dispositions ruled; two corrections of record entries (no owner words)"): `needs:` core/values/computed-labels retargeted to core/conditions/form/value-left.

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
- a member list (array, class) is filtered member by member: `\w + 1` = `\d + 1` (the manager's (d)) — SUPPORTED (PART PL of predspec29: 0 / 0 / 0 of 3,906; preddoc3b EXplus); re-run under the nested loop, classes descending: both `(?:10|9|8|7|6|5|4|3|2|1)`, 0 / 0 / 0 (predloop EXwplus, sabotage s7 caught). Re-run with classes ascending (quantified-order): both `(?:1|2|3|4|5|6|7|8|9|10)`, 0 / 0 / 0 (predasc EXwplus, sabotage s7 caught).
- "(joining is the sequence operator)" (the manager's (c) of plus-operands) — NOT SUPPORTED as complete: negated-class-hole's `join(c)` is a joining that is not the sequence operator; the piece names both.
- his first sentence (a literal `"a" + "b"` an ERROR once operand types exist) is a DIRECTION, "if that works", not in force (the draft's reading) — UNTESTED; ideas parked/ideas/restricted-parameter, parked/ideas/class-base.
evidence: preddoc3b EXplus, EXedges; PARTS PL, NE of predspec29, predspec291; predloop (superseded by predasc: predloop's model asserts the retired descending order and is red at the tip by design) EXplus, EXwplus; predasc EXplus, EXwplus.
history:
- 2026-11-18: array-lift's arrays; value-is-pattern part 1.
- 2026-11-19 (lane predloop): class-positions; the many-strings bullet said "applies member by member, over the product of the operands (core/arrays/lift)", now "in the nested loop over the operands' `enumerate`".
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
- `\d+? + \d+` (his test case under class-positions) is clause 2, under construction (the manager's answer (1), told to him; record: "2026-11-19 OWNER, discussing class-positions: "What about \d+? + \d+"") — SUPPORTED as rule-as-code (both operands infinite: the evidence model's enumerator refuses an unbounded repeat; predloop).
evidence: preddoc3b EXleft; PARTS CN, TT, RC of predspec28, predspec281.
history:
- 2026-11-18: match-is-rx (4), read-is-constant (4), the clarification, construction-line; `length($y)` written `strlen($y)` (THE MANAGER'S CALL 6, A26).
- 2026-11-19 (lane preddoc6, review r60 COLD-6): the statement said "accepts an rx exactly where `enumerate` accepts it ... any other rx is under construction", against its own clause 1 (an outward-looking assertion is enumerate's compile error, not under construction); rewritten to state the clauses as the rule. Statement before: "A single-value function accepts an rx exactly where `enumerate` accepts it, applied to each enumerated string in its order; any other rx is under construction."
- 2026-11-19 (lane predloop): `\d+? + \d+` added to clause 2's examples (class-positions).
- 2026-11-19 (lane preddoc6, review r60 FIXVER-5): the bullet restating `left`'s definition ("`left(rx, n)` is the IMAGE (the first n characters of each string) ...") replaced by a pointer: the definition is lib/strings/left's (every call-form name is a library piece).

## core/arrays/lift — Arrays are alternations; operations lift
slugs: array-lift lift-order macro-arguments
rulings:
- 2026-11-19 "Only solution is sorting output when needed." (record: "2026-11-19 OWNER RULING — quantified-order: PCRE's priority order; and classes lowest to highest; sorting only when asked"); the loop stands and nothing is sorted unless the user sorts (lib/structural/sort); the class order inside it is core/arrays/class-order
- 2026-11-19 "class-positions: nested loops, classes descending" (record: "2026-11-19 OWNER RULING — class-positions: nested loops, classes descending"); adopting his proposal of the entry below as the lift's rule; its "classes descending" half replaced by quantified-order (core/arrays/class-order)
- 2026-11-19 "I'm looking for the simplest rules as though this was against fn() and not +." (record: "2026-11-19 OWNER, discussing class-positions: the nested-loop rule, as if against `fn()`; a `lengthSorted()` transform"); marked by him "Discussion", a PROPOSAL, with the loop "loop a = enumerate(\d): loop b = enumerate(\d): rx |= fn(a, b)"; ruled by the entry above
- 2026-11-18 "array-lift: I meant, alternations as you suggested. It's consistent that alternations combine on the product and multiply the rx and produce more alternations" (record: "2026-11-18 OWNER RULING — array-lift: operations on arrays combine on the product")
- 2026-11-18 "What is needed is a consistent, general rule about it and not something specific to adding to arrays for example. What happens to array + array ?" (record: "2026-11-18 OWNER on value-is-pattern: one ruling, two leans, one idea"); a LEAN, settled by array-lift
- 2026-11-16 (class: DIRECTION) "macro-arguments: the general path is that an array of something is that something. i feel like this is creating a bunch of mechanism for very specific use. what otherwise is an array of macros?" (record: "2026-11-16 OWNER DIRECTION — arrays of macros: the general path, no special mechanism"); NO to the special mechanism; an array of macros is a macro, nothing more
rejected:
- pairwise as default — by owner ruling — his own first message, replaced at once by him; run: `[2, 4] + [1, 10]` pairwise is `[3, 14]`, `12` FAILS (preddoc3b sabotage s7 caught).
- macros as arguments, an array of them indexed and the entry called (macro-arguments, for the tuple compare) — by owner direction — "the general path is that an array of something is that something".
- rev 18's readings (a) and (b) of the tuple compare's body (a macro passed, indexed and applied in a body) — by owner direction — macro-arguments: not adopted (the draft §16).
readings:
- a repeated result is harmless (stated with the question, not objected to) — SUPPORTED (AL3 of predspec26: 0 / 0 / 0 of 364).
- the rule is about arrays the user writes, not a label's settings — UNTESTED (a scope statement).
- one array mentioned twice is independent per mention (the draft, review r47 D1) — SUPPORTED (preddoc2 PART RB).
- lift-order is enumerate's order (the manager's m2 of construction-line) — SUPPORTED (PART CN of predspec28); for a class, class-order.
- the nested loop over arrays the user writes is array-lift's product, first operand slowest (the record's note on his proposal: "this is array-lift's "first operand slowest", ruled 2026-11-18, stated as a loop") — SUPPORTED (predloop EXlift: `[2, 4] + [1, 10]` is `(?:3|12|5|14)`, the line unchanged; RB 0 / 0 / 0 against array-lift's list; sabotage s8 caught).
evidence: preddoc3b EXlift; PART AL of predspec26; predloop (superseded by predasc: predloop's model asserts the retired descending order and is red at the tip by design) EXlift, RB; predasc EXlift, OLD.
history:
- 2026-11-18: array-lift; the draft R.1.14 (ARRAYS UNDER OPERATIONS), AL1/AL2.
- 2026-11-19 (lane predloop): class-positions restated the rule as the owner's nested loop over each operand's `enumerate`, for every function. Statement before (ruled 2026-11-18): "An array is an alternation of values; an operation on arrays applies to every combination of members, the first operand slowest, values in the order given." The loop and "as though this was against fn()" bullets added; "Nothing is sorted by length" added as a pointer to class-order.
- 2026-11-19 (lane predasc): quantified-order. Bullet before: "Nothing is sorted by length; a class's order is core/arrays/class-order." Now "Nothing is sorted unless the user sorts (lib/structural/sort); ...". The example line unchanged (predasc EXlift, OLD).
- 2026-11-19 (lane predfix61, review r61 F-M, GENERAL-11): the lift "for every function" read literally lifts `join(c)` member by member; the bullet gains the manager's reading that only a parameter needing a SINGLE operand lifts (core/values/one-type's properties). Its words until then: "The same rule for every function, "as though this was against fn() and not +"."

## core/arrays/class-order — The order of a class's results
was: core/arrays/class-positions (2026-11-19, merged: the owner's ruling class-positions answered it; its three shapes are this piece's run examples)
slugs: class-order class-positions quantified-order
rulings:
- 2026-11-19 "quantified-order: keep pcre priority order and classes change to lowest to highest unless pcre priority order disagrees. It was to help the arithmetic common choice but if it doesn't completely then it shouldn't at all. Only solution is sorting output when needed." (record: "2026-11-19 OWNER RULING — quantified-order: PCRE's priority order; and classes lowest to highest; sorting only when asked"); quantified-order RULED (inside a quantified operand, PCRE's priority order; no count-by-count order); the class order turns to lowest to highest, REPLACING the "classes descending" half of class-positions (the nested loop stands); a principle for the corner: no built-in length order
- 2026-11-19 "Also, most numbers will use boundary checks to make sure they match the whole subject number." (record: "2026-11-19 OWNER RULING — quantified-order: PCRE's priority order; and classes lowest to highest; sorting only when asked"); an OBSERVATION, shown as a run line (`/\b${\d + 1}\b/`)
- 2026-11-19 "class-positions: nested loops, classes descending" (record: "2026-11-19 OWNER RULING — class-positions: nested loops, classes descending"); the nested-loop half stands; "classes descending" REPLACED by quantified-order the same evening (history)
- 2026-11-19 "Enumerate() will output in written or for classes descending class value order.  lazy/greedy loops start shortest/ longest respectively" (record: "2026-11-19 OWNER, discussing class-positions: the nested-loop rule, as if against `fn()`; a `lengthSorted()` transform"); "in written or" read as "in written ORDER, or" (phone); the proposal the ruling adopted; its "descending" replaced by quantified-order, "lazy/greedy loops start shortest/ longest respectively" stands
- 2026-11-19 "What it doesn't do, unfortunately, is produce a consistent longest to shortest result on pure digits." (record: "2026-11-19 OWNER, discussing class-positions: the nested-loop rule, as if against `fn()`; a `lengthSorted()` transform"); his own statement of the cost, shown `10 - \d` on `10`
- 2026-11-19 "class-positions: is your lean then: written order, in text order then classes by length, in text order" (record: "2026-11-19 OWNER, discussing class-positions: his restatement of the manager's lean"); a question back, discussion
- 2026-11-19 "What about \d+? + \d+" (record: "2026-11-19 OWNER, discussing class-positions: "What about \d+? + \d+""); a test case, discussion
- 2026-11-19 "class-order: longest" (record: "2026-11-19 OWNER RULING — class-order"); REPLACED the same day by class-positions (history)
- 2026-11-19 "can we sort by length, longest first?" (record: "2026-11-19 OWNER, discussing class-order: longest first"); a question carrying the idea; replaced with it
rejected:
- descending class value order (class-positions as ruled earlier the same evening, "classes descending") — by owner ruling — quantified-order, his reason: "It was to help the arithmetic common choice but if it doesn't completely then it shouldn't at all."; run: `/${\d + 1}/` SEARCHED `x10` descending `10`@1 against ascending `1`@1, 0 / 250 / 570 of 3,906 (predasc EXclassorder, OLD; sabotage s1 caught).
- count by count inside a quantified operand (every string of one count together, greedy from the longest count; the old bounded model classpos_inf.py) — by owner ruling — quantified-order ("keep pcre priority order"); run: under ascending classes the lazy + greedy `\d{1,3}? + \d{1,3}` begins `0|100|101` against `100|101|102` count by count, 0 / 0 / 0 differing over 3,906 texts (predasc EXbounded; sabotage s13 caught).
- longest first (class-order as ruled earlier the same day: "where a lift gives results of different lengths from one class position, the LONGER is tried first") — by owner ruling — class-positions, after he was shown the cost, and quantified-order ("Only solution is sorting output when needed."); run: `/${\d + 1}/` SEARCHED `x10` `1`@1 under the loop against `10`@1 longest first, 0 / 250 / 570 of 3,906 (predasc EXclassorder; sabotage s2 caught).
- "longest everywhere" (sorting alternations and arrays too) — by owner ruling — class-order took the class-only version; class-positions and quantified-order sort nothing by length.
- class-positions' candidates C1 (the lift as one position, longest first), C2 (the first class slowest, ascending, the second's results longest first within), C3 (the first descending, longest first within), Q1 and Q2 (a lazy quantifier), A and B (the class first) — by owner ruling — class-positions: none is the nested loop (each sorts by length somewhere; under quantified-order nothing does).
readings:
- (the manager's (a) of quantified-order) "unless pcre priority order disagrees": PCRE gives a class's members no order of its own (a class is one position), so nothing disagrees and a class is ascending everywhere — SUPPORTED as far as a run reaches: no plain match shows a class's member order (the class written as an alternation of its members in 20 shuffled orders, five shapes `\d`, `\d{1,2}`, `\d{1,2}?`, `x\d\d`, `(?:\d|1){1,3}`: 0 / 0 / 0 each over 3,906 texts; predasc PCREORD, sabotage s17 caught); that PCRE's code holds no class order is UNTESTABLE here (its source is read only by the D181 reader).
- (the manager's (b) of quantified-order) a class that is not digits: lib/builtin/enumerate/class-value (open then; RULED 2026-11-21: ascending codepoint).
- (the manager's (c) of quantified-order) the codepoint order rejected under class-order on 2026-11-19 is the rule again, for digits by his words — SUPPORTED: its recorded line (`/${\d + 1}/` SEARCHED `x10` `1`@1) is the loop's answer (predasc EXclassorder); the record's contemporaneous run (asc.py, bare and between `\b`) is reproduced mechanically (predasc RECASC, EXbound; sabotage s18, s15 caught).
- (the manager's (d) of quantified-order) every lift example printed with a descending class re-run ascending — SUPPORTED: 9 printed lines change, the 5 the class rulings do not govern are unchanged (predasc OLD against the documents at 5a299d40d; sabotage s16 caught); old and new lines in lane predasc's report.
- each position is one loop of the nest, outer to inner in text order (two classes, a quantified class, the class first, the alternation first need no rule of their own) — SUPPORTED, re-run ascending (predasc EXtwo, EXlazy, EXfirst, EXnest; sabotage s20, s4, s3, s26 caught).
- equal strings from different members are one result, the first occurrence standing — SUPPORTED (predasc EXeq, sabotage s6 caught).
- the bounded lazy + greedy lift `\d{1,3}? + \d{1,3}` reports `123` on SEARCHED `x123` again (the value withdrawn under "classes descending"), now by enumerate's priority order with the class ascending: the lazy operand's first canonical string is `0`, and inside the greedy operand `123` comes before `12` and `1` — rule-as-code (predasc EXbounded); lazy + lazy now reports `1`@1 (was `12`@1); greedy + lazy `1`@1, greedy + greedy `123`@1.
- no tie rule (the manager's 8 under longest first) — moot: the order is total.
evidence: predasc EXclassorder, EXbound, RECASC, EXsub, EXtwo, EXlazy, EXfirst, EXnest, EXeq, EXmul, EXbounded, PCREORD, OLD; earlier predloop EXclassorder, EXsub, EXtwo, EXlazy, EXfirst, EXnest, EXeq, EXmul, EXbounded, RB; preddoc3b EXclassorder, EXclasspos; PART CO of predspec29, predspec291 (P29-9).
history:
- 2026-11-19: his question, "what do you mean class only?", then the ruling class-order: longest.
- 2026-11-19 (lane predloop): REPLACED by class-positions the same day. Statement before (ruled): "A class's members have no order; where a lift gives results of different lengths from one class position, the longer is tried first." Bullets before: "Alternations, quantifiers and arrays the user writes keep their own order; nothing else is sorted."; "No tie rule is needed: two different strings of one length cannot both match at one position (a reading, run)."; "Nesting, the alternation first: `(1|9) + \d` keeps the alternation's order and sorts each choice's class results (a reading, run)."; the example's expansion was `(?:10|1|2|3|4|5|6|7|8|9)` (its modes unchanged).
- the piece core/arrays/class-positions (open class-positions, merged here by lane predloop), its history: the manager's reading (c) of class-order; widened by review r54 P29-9 with the class first; lane preddoc4 moved its long candidate runs to the details entry (review r59 READ-18 stage 1). Its statement: "The order of a lift's results with two class positions (`\d + \d`), a class under a lazy quantifier, or a class first beside an alternation is a question for the owner." Its printed lines: C1 `/${\d + \d}/` WHOLE `13` HOLDS / SEARCHED `x13` `13`@1 / FIND-ALL `13 4 18` [`13`@0, `4`@3, `18`@5] (the loop's answers); C2 SEARCHED `x13` `1`@1, FIND-ALL [`1`@0, `3`@1, `4`@3, `1`@5, `8`@6]. Its readings line: C1 vs C2 0 / 776 / 1,816, C1 vs C3 0 of 3,906; Q1 vs Q2 0 / 2,797 / 3,230; A vs B 0 / 750 / 1,404 (PART CO of predspec29, predspec291). The candidates as they stood: "Two classes, `\d + \d`: C1, the lift as one position, its results longest first; C2, the first class slowest in ascending order, the second's results longest first within each; C3, the first descending (= C1's answers). A lazy quantifier, `\d{1,2}? + 1`: Q1, the quantifier's order kept, each count's results longest first (SEARCHED `x100` `10`@1); Q2, the quantified class as one position (`100`@1). The greedy `\d{1,2} + 1` agrees. The class first, `\d + (1|9)`: A, the alternation's order outermost, each choice's class results longest first (SEARCHED `x11` `1`@1); B, the class position's results longest first across the lift (`11`@1)."
- 2026-11-19 (lane predasc): quantified-order REPLACED "classes descending" by lowest to highest and ruled the order inside a quantified operand. Statement before (ruled): "A class enumerates in descending class value order, so a lift over it runs the nested loop in that order; nothing is sorted by length." Bullets before: "A class is one position taking one character from a set (`\d`, `[90]`, `\w`, `.`); `enumerate` gives its members in "descending class value order". For digits the value is the digit; for any other class it is open (lib/builtin/enumerate/class-value)."; "Alternations and arrays keep their written order; "lazy/greedy loops start shortest/ longest respectively"."; "A shorter result may come first: `10 - \d` tries `1` before `10`, the owner's "no consistent longest to shortest result"; a length order is only an idea (lib/structural/sort)."; "Inside a quantifier the order is `enumerate`'s priority order, one more copy (lazy: one fewer) at each choice point, so a lazy + greedy lift need not report the longest (a reading, run, bounded); unbounded operands (`\d+? + \d+`) are under construction (core/values/functions)." Its printed lines under "classes descending" (each re-run in the base, old and new in lane predasc's report): `\d + 1` SEARCHED `x10` `10`@1, expansion `(?:10|9|8|7|6|5|4|3|2|1)`; `10 - \d` SEARCHED `x10` `1`@1, expansion `(?:1|2|3|4|5|6|7|8|9|10)`; `\d + \d` SEARCHED `x13` `13`@1, `(?:18|17|..|1|0)`; `\d{1,2}? + 1` SEARCHED `x100` `10`@1, begins `(?:10|100|99|98|..`; `\d + (1|9)` SEARCHED `x11` `11`@1, begins `(?:10|18|9|17|..`; `(1|9) + \d` begins `(?:10|9|8|7|..` (answers unchanged); `\d{1,3}? + \d{1,3}?` SEARCHED `x123` `12`@1, FIND-ALL `123 7 45` [`12`@0, `3`@2, `7`@4, `45`@6]; `\d{1,3}? + \d{1,3}` the same line. The rejected item it moves out of `rejected:`, verbatim: "ascending codepoint order (the draft's lean, §5.5) — by owner ruling — class-order, then class-positions ("descending"); run: `/${\d + 1}/` SEARCHED `x10` ascending `1`@1 against `10`@1 (PART CO of predspec291; predloop EXclassorder, sabotage s1 caught)." The candidates item before: "class-positions' candidates C1 (the lift as one position, longest first), C2 (the first class slowest, ascending), C3 (the first descending, longest first within), Q1 and Q2 (a lazy quantifier), A and B (the class first) — by owner ruling — class-positions: none is the nested loop. Against the loop (predloop RB, 3,906 texts): C1 on `\d + \d` 0 / 0 / 0; Q1 on `\d{1,2}? + 1` 0 / 2,250 / 2,790; A on `\d + (1|9)` 0 / 750 / 1,404 (the loop gives B's answers, `11`@1 on `x11`, by another rule); C2's ascending first class is the rejected ascending order."
- 2026-11-19 (lane predasc): the longest-first rejected item before (its witness `10 - \d` no longer parts from longest first under ascending), verbatim: "longest first (class-order as ruled earlier the same day: "where a lift gives results of different lengths from one class position, the LONGER is tried first") — by owner ruling — class-positions, after he was shown the cost; run: `/${10 - \d}/` SEARCHED `x10` `1`@1 under the loop against `10`@1 longest first, 0 / 250 / 570 of 3,906 (predloop EXsub, RB; sabotage s2 caught)."
- 2026-11-19 (lane predasc): the readings under "classes descending", verbatim (lane predloop):
  - (the manager's (a)) "class value" for a non-digit class is the codepoint — UNTESTED: not a run question; asked as lib/builtin/enumerate/class-value.
  - (the manager's (b)) every printed example keeps its answers except where a subtraction-like function puts a shorter result first — SUPPORTED for the ruled and readings' examples (predloop RB, 0 / 0 / 0 each: `\d + 1`, `\w + 1`, `enumerate(/\d/) + 1`, `\d * 0`, `(1|9) + \d`, `\d + \d`, `\d * \d`, `[2, 4] + [1, 10]`); `10 - \d` differs (0 / 250 / 570, never printed before); the OPEN candidates A and Q1 differ too (above).
  - (the manager's (c)) the bounded lazy + lazy lift `\d{1,3}? + \d{1,3}?` reports `12` on SEARCHED `x123` — SUPPORTED; lazy + greedy `\d{1,3}? + \d{1,3}` reports `123` — NOT SUPPORTED: it reports `12`@1 (FIND-ALL `123 7 45` [`12`@0, `3`@2, `7`@4, `45`@6]), because inside the greedy operand enumerate's priority order tries `3` (first digit 3) before `114` (first digit 1); `123`@1 comes only from a COUNT-GROUPED order (every 3-digit string before any 2-digit one), which is not enumerate's ruled order (predloop EXbounded, the rival printed; sabotage s13 caught). Greedy + lazy and greedy + greedy report `123`@1.
  - (the manager's (d)) nesting, the alternation first, and equal strings are one result (the first occurrence standing) hold under the loop — SUPPORTED: `(1|9) + \d` 0 / 0 / 0 against the old nested list (predloop EXnest, sabotage s5 caught); `\d * 0` is `0` (EXeq, sabotage s6 caught). `\d + (1|9)` is now `10|18|9|17|..` (SEARCHED `x11` `11`@1); `\d{1,2}? + 1` is `10|100|99|98|..` (SEARCHED `x100` `10`@1).
  - (the manager's (e)) is enumerate's: lib/builtin/enumerate.
  - the order inside a quantifier is enumerate's priority order, depth first (this lane's reading of "lazy/greedy loops start shortest/ longest respectively" with enumerate's ruled PRIORITY ORDER) — SUPPORTED as rule-as-code (predloop EXlazy, EXbounded; sabotage s4 caught); an owner question (lane predloop's report): it decides `\d{1,3}? + \d{1,3}`.
  - no tie rule (the manager's 8 under longest first) — moot: the order is total.
- 2026-11-19 (lane predfix61, review r61 F-J, RUNOWN-7): the boundary bullet named no mode and was false on the first line's subject; until then: "`/\b${\d + 1}\b/` reports `10` (the second line below)." Now SEARCHED on `x10 10` `10`@4, on `x10` none (predfix61 FJB, sabotage s9 caught).
- 2026-11-22 (lane predfix77, review r77 D2 (FIXIND-14), D11 (GENERAL-10); record "2026-11-22 MANAGER — review r77 (predfold1121): dispositions ruled (no owner words)"): status date 2026-11-19 to 2026-11-21 (class-value, class-hole-order); "every class is in ascending codepoint order" became "every written class ...; a class holding a hole is an alternation of classes (core/holes/class), in written order".

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
- 2026-11-21 "zero-in-definition: a" (record: "2026-11-21 OWNER RULING — zero-in-definition: a"); the `0` of the last bullet
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
- 2026-11-19 (lane predfix61, review r61 F-M, GENERAL-4): "in the values' order" points at the lift's loop (core/arrays/lift); no answer moves. Status date 2026-11-18 to 2026-11-19.
- 2026-11-21 (lane predscope, zero-in-definition folded): the last bullet's end until then: "`0` in the outer rx is the outer match so far (core/conditions/match-so-far)." Now a `0` in the outer definition is its match so far, the inserted text included, and a `0` inside an inserted definition is that definition's own. Status date 2026-11-19 to 2026-11-21.

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
- 2026-11-19 (lane predfix61, review r61 F-M, GENERAL-4): "the order given" points at the lift's loop (core/arrays/lift) and a class's order (core/arrays/class-order); no answer moves. Status date 2026-11-18 to 2026-11-19.

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
- 2026-11-19 (lane predfix61, review r61 F-H, GENERAL-6): the bullet until then: "In practice, for a class that is not negated, the alternation collapses to one class: `[${c}]` is `[xy]`, in every mode, a capture before the class included (a reading, run)." Under a lift the collapse is falsified (c := [`9`, `0`], `[${c}] + 1`: the alternation gives `(?:10|1)`, one class `(?:1|10)`; SEARCHED `x10` `10`@1 against `1`@1; predfix61 FH, sabotage s8 caught); unlifted the two agree (0 / 0 / 0 of 1,365 texts). Qualified "for matching"; the order is asked (core/holes/class/lift-order).
- 2026-11-22 (lane predfix77, review r77 D2 (FIXIND-14); record "2026-11-22 MANAGER — review r77 (predfold1121): dispositions ruled (no owner words)"): status date 2026-11-19 to 2026-11-21 (class-hole-order ruled). Text unchanged.

## core/holes/class/two-holes — Two holes in one class
slugs:
rulings:
rejected:
readings:
- two holes in one class: the alternation over every combination, product-order's order, unobservable for a non-negated class (the manager's reading 2, other-holes (d)) — SUPPORTED (preddoc1 PART R2: `[${a}${b}]` against `[xypq]` 0 / 0 / 0 of 781; first-slowest against first-fastest 0 / 0 / 0; `[${lo}-${hi}]`, the member `c-b` removed, against `[a-e]` 0 / 0 / 0 of 400).
evidence: preddoc1 EX-two-holes, PART R2.
history:
- 2026-11-19: the manager's reading (d) of the other-holes entry; not his words.
- 2026-11-19 (lane predfix61, review r61 F-H): the statement until then: "Two holes in one class (`[${a}${b}]`, `[${lo}-${hi}]`) are the alternation over every combination, first hole slowest; for a class that is not negated the order is not observable." The order is observable under a lift (core/holes/class/lift-order).

## core/holes/class/lift-order — The order of a class-member hole's values under a lift
slugs: class-hole-order
rulings:
- 2026-11-21 "class-hole-order: a" (record: "2026-11-21 OWNER RULING — class-hole-order: a (written order under a lift)"); (a) as put to him: written order, the alternation of one class per value
- 2026-11-19 "other holes: 1. classes should be alternations on the class like [x] | [y] like patterns. in practice, that means [xy]" (record: "2026-11-19 OWNER RULING — other-holes"); both halves of his sentence, read under a lift, are the two candidates
rejected:
- (b) one class, lowest to highest (the second half of his sentence, "in practice, that means [xy]", read under a lift) — by owner ruling — class-hole-order: a; run: `(?:1|10)`, SEARCHED `x10` `1`@1 against `10`@1 (predfix61 FH; sabotage s8 caught).
readings:
evidence: predfix61_model.py FH (lane predasc's enumerator and nested loop, copied; the two lines; unlifted 0 / 0 / 0 of 1,365). predfix77_model.py LIFTORDER lowers the two printed programs FROM THEIR TEXT (`/${/[${c}]/ + 1}/` to `(?:10|1)`, `/${/[09]/ + 1}/` to `(?:1|10)`) and its DOC check finds both lines verbatim; sabotage s15 caught. predfix61 FH never parsed the program text, so its re-run after the spelling correction showed nothing, and its DOC check was red on that line (review r77 D9, EXAMPLES-3).
history:
- 2026-11-21 (the manager, one ruling): class-hole-order RULED (a). Status `open class-hole-order 2026-11-19` to `ruled 2026-11-21`. Statement before: "Under a lift, are the values of a class-member hole taken in written order, as the alternation of one class per value, or as one class, lowest to highest?" Its candidates before: "(a) written order, the alternation of classes; (b) one ascending class." Candidate (b)'s line is kept as the hand-written class `[09]`, which it equals.
- 2026-11-21 (the manager, the owner's correction): the example program was printed `/${[${c}] + 1}/`, which is not legal ("[${c}] is not legal predicate language": inside `${...}` the text is the expression language, where `${` is no hole and `[..]` is an array); it is `/${/[${c}]/ + 1}/`, the class written as a literal inside the hole. The answers are unchanged (the model lifted the class with its hole, predfix61 FH; re-run 2026-11-21).
- 2026-11-19 (lane predfix61, review r61 F-H, GENERAL-6): a new open sub-piece at the manager's ruling of review r61.

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
slugs: other-holes
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
slugs: other-holes
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
slugs: hole-flags flags-propagate flags-scope weak-meets-weak
rulings:
- 2026-11-18 "hole-flags: i have heard you say both that the ${} gets the flags in force and also that a hole has its own flags. i agree with your interpretation of flags and holes. a hole takes the flags in force at the hole. each regex literal has its own flags. do the flags propagate down though? /(?i)${/blah/}/ is blah case insensitive?" (record: "2026-11-18 OWNER RULING — hole-flags: a hole takes the flags in force at the hole; each regex literal has its own flags; and his question, do flags propagate down"); NARROWED by hole-flags' "yes to all" (2026-11-22, the item below): a hole takes only an explicit `i` or `-i` in force at it, not `m`, `s` or a weak `i` (review r84 C1, C6: the slug hole-flags names two rulings, told apart by their dates).
- 2026-11-18 "flags-propagate: yes" (record: "2026-11-18 OWNER RULING — flags-propagate: yes"); NARROWED by hole-flags (2026-11-22): what propagates down is an explicit `i` or `-i` only (review r84 C6).
- 2026-11-19 "i agree with your inherit table excepting that U should also not be inherited. one could make a case that only i should be inherited" (record: "2026-11-19 OWNER RULING — flags-scope")
- 2026-11-19 "by "flags propagate" i thought we decided that rx inherits the flags of the surrounding rx" (record: "2026-11-19 OWNER, on flags-in-filter: what "flags propagate" meant")
- 2026-11-22 "hole-flags: yes to all. What i like about the i weak behavior is that it's consistent to the other program level settings that only affect literals in program scope." (record: "2026-11-22 OWNER RULING — hole-flags: yes to all (weak values do not propagate; only an explicit `i` is inherited at a hole; `m` and `s` are no longer inherited)"); all three parts as put to him: "1. Weak values do not propagate; they are the file's default for its own literals. 2. At a hole, only an explicit `i` or `-i` is inherited. It replaces what was in force. 3. `m` and `s` are no longer inherited at a hole." It REVISES flags-scope (2026-11-19: `i`, `m`, `s`) and narrows hole-flags and flags-propagate (both 2026-11-18) (review r84 C6: the date of flags-propagate corrected from 2026-11-19).
- 2026-11-22 (class: PROPOSAL) "Proposal: Keep i inherited for now but this could set the "weak" value for i. By that I mean i has three settings: on, off, weak on, weak off." (record: "2026-11-22 OWNER RULING — program-options: yes; and a PROPOSAL: `i` keeps inheriting, with a "weak" value the program sets"); he writes "three settings" and lists four; ruled in the form of hole-flags (on and off explicit, weak on and weak off the file's default).
- 2026-11-22 (class: PROPOSAL) "Consider this: weak settings do not propagate." (record: "2026-11-22 OWNER, on weak-meets-weak: "Consider this: weak settings do not propagate.""); answer (b) of weak-meets-weak, ruled with hole-flags.
rejected:
- NO INHERITED FLAGS ("a hole keeps its own flags"; the draft's own rule, never his) — by owner ruling — flags-propagate.
- every flag propagates (`n`, `U`, `xx`, `J`; the draft revision 28.1's reading) — by owner ruling — flags-scope; `/(?U)x${/a+/}/` SEARCHED `xaaa` gives `xaaa`@0, the text paste `xa`@0 (preddoc1 EX-flags-U, sabotage xEX-flags-U caught).
- the inserted literal spelt `(?^ims:...)` as "the" text — by review r54 P29-1 — `(?^)` does not reset `U`, a paste is no parse of its own (PART TX of predspec291).
- the hole's flags over a flag the literal writes — by owner ruling — flags-propagate, the override as asked (preddoc1 EX-flags-written, sabotage xEX-flags-written caught).
- hole-flags' split, "plain text with no flags of its own (a read, a string constant, a number)" against "pattern text written with flags" (the manager's, in the question) — by owner — "under one type there is no "plain text" kind" (the draft R.9, R.1.15).
- weak-meets-weak (a), the program's weak value flows into a library's literal — by owner proposal, then ruling — "Consider this: weak settings do not propagate."
- the list `i`, `m`, `s` at a hole (flags-scope, 2026-11-19) — by owner ruling — "hole-flags: yes to all."
readings:
- "only i" inherited: his OBSERVATION, a possible narrowing, not ruled — SUPERSEDED by hole-flags (2026-11-22): the narrowing is ruled, an explicit `i` or `-i` only (review r84 C1).
- the not-inherited flags are the inserted rx's own defaults at any depth; `m`, `s` stay inherited until he rules the narrowing (the manager's) — SUPERSEDED by hole-flags (2026-11-22): `m` and `s` are not inherited; the inserted rx's own defaults are its file's program options (review r84 C1).
- the `r` and `a`-family flags inherited (the draft's reading, P29-2) — SUPERSEDED: not inherited, by hole-flags' "At a hole, only an explicit `i` or `-i` is inherited." (review r84 A6 (1), the manager's ruling of the disposition; core/patterns/flags).
- (c) `x`, `xx`, `n`, `U` stay not inherited (ruled by flags-scope, 2026-11-19; that hole-flags leaves them so is the reading); `J` unchanged — SUPPORTED as run for `x`, `n`, and for `m`, `s` no longer inherited (docs/dev/lanes/predspot_evidence/ predspot_model.py NOTINH); `xx`, `U`, `J` not modelled.
- (e) a binding of the SAME file inserted in a hole of that file has the same defaults, so nothing visible changes there, where no `@options` statement stands between the binding and the hole (scoped by review r84 A1; whether one may stand there is open options-position, lib/builtin/options) — SUPPORTED as run (docs/dev/lanes/predspot_evidence/ predspot_model.py LIBFILE: `/x${w}/` under a weakly insensitive file holds on `XAB`).
- weak meets weak, his pasted (b) line — SUPPORTED as run: the weak example under hole-flags reproduces the record's line (b) verbatim, under the 2026-11-19 rule its line (a) (docs/dev/lanes/predspot_evidence/ predspot_model.py EXAMPLES).
evidence: preddoc1 EX-flags, EX-flags-written, EX-flags-U; PARTS FF, FA, TX, SQ of predspec291; PART FL of predspec28.; docs/dev/lanes/predspot_evidence/ predspot_model.py EXAMPLES, NOTINH, LIBFILE, FLAGGRID, FSWEEP (lane predspot).
history:
- 2026-11-18: hole-flags and flags-propagate reversed the draft's NO INHERITED FLAGS (§11, §13 O32).
- 2026-11-19: flags-scope (`U` moved out); the r54 round made "parsed alone" the model (revision 29.1).
- 2026-11-19 (lane preddoc4): flags-in-filter (an open question in a bullet) became the open sub-piece core/holes/flags/in-filter (review r59 READ-9).
- 2026-11-22 (lane predspot, hole-flags folded; record "2026-11-22 OWNER RULING — hole-flags: yes to all (weak values do not propagate; only an explicit `i` is inherited at a hole; `m` and `s` are no longer inherited)"): ruled 2026-11-19 re-dated 2026-11-22. Statement until then: "What is inserted in a hole starts with the flags in force at the hole for `i`, `m`, `s`, not for `U`, `x`, `xx`, `n`; a flag it writes for itself wins."; the bullet until then: "This holds for a direct literal and for a binding alike, at any depth (a binding in a hole inherits)." and "`J` has no effect across a hole (core/holes/same-name)."; bullets added (own file's defaults; his words on the three parts; a weak value does not propagate; the same-file reading (e); x, xx, n, U and J, the reading (c)). The line `/(?i)id-${/blah/}/` stands (an explicit `i`, docs/dev/lanes/predspot_evidence/ predspot_model.py FSWEEP); four lines added, the weak example and the s example (docs/dev/lanes/predspot_evidence/ predspot_model.py EXAMPLES).
- 2026-11-23 (lane predfix84, review r84 A1, C1, C6, C8, D8 (e); record "2026-11-23 MANAGER — review r84 (predspot1122): the dispositions, ruled with the 2026-11-23 rulings in hand; no owner words"): the reading (e) bullet scoped (A1): "... so nothing visible changes there (the manager's reading (e))." now holds where no `@options` statement stands between the binding and the hole, with the open options-position; the part-2 bullet's "(revising the earlier list `i`, `m`, `s`)" moved here (C8: the base carries no revision marks), "are no longer inherited" to "are not inherited"; the `x` bullet until then: "`x`, `xx`, `n`, `U` stay not inherited; `J` has no effect across a hole (core/holes/same-name) (the manager's reading (c))." now names flags-scope as their ruling and the reading (c) as that hole-flags leaves them so (D8 (e)); three readings marked superseded and the 2026-11-18 items marked narrowed (C1, C6). No answer moved (docs/dev/lanes/predfix84_evidence/ predfix84_model.py FSWEEP).

## core/holes/flags/in-filter — Flags of an `&` inside a hole
slugs: flags-in-filter flags-before-and flags-warning
rulings:
- 2026-11-19 "flags-in-filter: both sides inherit." (record: "2026-11-19 OWNER RULING — flags-in-filter: both sides inherit; and a question on a bound `&` put in a hole")
- 2026-11-19 "flags-in-filter: i cannot think of a different solution. I agree with the ruling that the environment of the hole sets the default options for the expression inside." (record: "2026-11-19 OWNER RULING — flags-in-filter confirmed: the environment of the hole sets the default options for the expression inside; and a request for a warning"); it answers flags-before-and: the sides take the flags before the intersection
- 2026-11-19 "flags-warning: yes when it works. You can't do it if the expression refers to $x a label in the literal" (record: "2026-11-19 OWNER RULING — flags-warning: yes, when it works; not when the expression reads a label of the literal")
- 2026-11-22 "hole-flags: yes to all. What i like about the i weak behavior is that it's consistent to the other program level settings that only affect literals in program scope." (record: "2026-11-22 OWNER RULING — hole-flags: yes to all (weak values do not propagate; only an explicit `i` is inherited at a hole; `m` and `s` are no longer inherited)"); the sides inherit an explicit `i` only (the manager's reading (b)).
rejected:
- a structural trigger for the warning (any `&` or complement in a flagged hole whose operand has a letter and sets no case flag) — by owner ruling — flags-warning: the exact trigger, "when it works"; it would fire on the harmless cases too.
- resolve the expression on its own, then insert the result wrapped by the context options (his own proposal, "after") — by owner — dropped by him ("i cannot think of a different solution"): it collides with "a flag it writes for itself wins" (`A & A` against `A`, A := `/(?-i)ab/`).
- neither side inherits (a filter operand judging its stretch with its own flags; candidate (b)) — by owner ruling — flags-in-filter.
- the manager's m2 (an `&` operand, a condition's set, a filter-role argument keep their own flags) as the draft's flags-in-filter reading (2026-11-18) — by the draft (rev 29, R.9 row 100) — SUPERSEDED as the draft's reading by REACH (the manager's reading 3, not a ruling).
readings:
- a binding of an `&` put in a hole equals the `&` written in the hole; used with no surrounding rx it reads under its own flags (the manager's answer to his question, resting on core/holes/flags and the place table's binding row) — NOT SUPPORTED once program options differ by file (review r84 A2): a library `C := /[a-z]+/ & /b.*/` under a weakly insensitive program fails `/id-${C}/` on `id-BLAH` where the `&` written in the hole holds; now for flags a binding is its expression where it is WRITTEN, plus an explicit `i` from the hole (docs/dev/lanes/predfix84_evidence/ predfix84_model.py FILTER, the lines "Bound in a library" and "Written in the hole"); the second half stands (`blah` HOLDS, `BLAH` FAILS).
- the two sides of an `&` inside a hole start with the hole's flags (THE DRAFT'S READING REACH, 0 / 0 / 0 of 1,555 against the plain hole) — open in the draft §R.8; the record's "2026-11-19 OWNER, on flags-in-filter: what "flags propagate" meant" is his remark on it, not a ruling. SUPERSEDED by hole-flags (2026-11-22): "the hole's flags" a side takes are an explicit `i` or `-i` only (review r84 C1).
- flags-warning (a): "when it works" also covers an operand that is not regular and an over-budget comparison (no warning, no error) — UNTESTED (the manager's, record "2026-11-19 OWNER RULING — flags-warning: yes, when it works; not when the expression reads a label of the literal"); marked a reading in the base.
- flags-warning (b): the name `pcrec.flags.filter` is a placeholder, the manager's — UNTESTABLE (a name).
- flags-warning (c): the message points at writing the flag in the operand — UNTESTABLE (a wording).
- flags-warning (d): the trigger is stated for `i`; `m` and `s` follow the same comparison — SUPERSEDED (review r84 C1): the base sentence it marked is gone (the predspot fold); `m` and `s` no longer reach a side (hole-flags, 2026-11-22), so the trigger is stated for an explicit `i` or `-i` (reading (b) below; `-i`: review r84 A8).
- flags-before-and (a): a compile-time judgement of a binding ALONE reads it under its own flags and can say "nothing" of a binding that matches in a flagged hole, so such warnings belong at the USE — UNTESTED (record "2026-11-19 OWNER, after flags-in-filter: do the sides inherit before or after the intersection ("Tricky")").
- flags-before-and (b): the same before/after split exists for a complement (`A & !B` in a flagged hole) — UNTESTED (the same entry).
- (b) the sides of an `&` inside a hole inherit an explicit `i` only; `pcrec.flags.filter` keeps its trigger — SUPPORTED as run (docs/dev/lanes/predspot_evidence/ predspot_model.py FILTER: the trigger computed at `/(?i)${..}/` warns on `/[a-z]x/ & /[A-Z]x/`, not on `/[a-z]+/ & /b.*/`; under a weakly insensitive program no flag reaches the sides).
- (review r84 A8, a reading; the trigger the manager's call) `pcrec.flags.filter` fires under an inherited `-i` by the same comparison: `/(?-i)${C}/`, C := `/[a-z]x/ & /Ax/` in a weakly insensitive library: the sides first hold on no text, the expression alone on `ax`, `aX`, `Ax`, `AX` — SUPPORTED as run (docs/dev/lanes/predfix84_evidence/ predfix84_model.py FILTER, the trigger computed under `(?-i)`).
evidence: the draft's PART FF of predspec29 (REACH). The warning's trigger: the record's run flagswarn.py (brute force over 1,554 strings; 2 WARN, 4 quiet).; docs/dev/lanes/predspot_evidence/ predspot_model.py FILTER, FSWEEP (lane predspot).
history:
- 2026-11-19: his before/after question ("Tricky"), his resolve-then-wrap proposal, then the confirmation; the second example line is the record's run (flagsorder.py, hand-built). A warning for the case is asked of him (flags-warning), not in the language.
- 2026-11-19 (lane preddoc4): a new open sub-piece, from a bullet of core/holes/flags (review r59 READ-9). The candidate (b) is the lane's statement of the rival the draft names (a filter operand's own world).
- 2026-11-19 (lane preddoc6, review r60 RECOUNT-6): the draft R.9 candidate for this piece, PARTIAL at r59 and left unchanged by preddoc5, now has its own `rejected:` line.
- 2026-11-19: ruled; the statement until then: "Do the two sides of an `&` written inside a hole start with the flags in force at the hole?" with the candidates (a) both sides inherit, (b) neither does; the example line is the record's run (flagsfilter.py, hand-built).
- 2026-11-22 (lane predfix77, review r77 D3, D7 (RULING-8), D11; record "2026-11-22 MANAGER — review r77 (predfold1121): dispositions ruled (no owner words)"): the binding bullet's "a binding is its expression where it is used" scoped to flags and matching (its label reads are its own: bare-nested-scope case 2); the warning bullet marks readings (a) and (d) and is the one owner of the trigger (the warnings row cites it; the row's own trigger text until then, verbatim: "an `&` or a complement in a hole that inherits a flag, where the result differs from the expression alone with the flag on its result; not where the expression reads a label (`$x`) or the comparison cannot be made"); status date 2026-11-19 to 2026-11-21. The 2026-11-19 history line "A warning for the case is asked of him (flags-warning), not in the language" is superseded by the flags-warning ruling (folded).
- 2026-11-22 (lane predspot, hole-flags folded; record "2026-11-22 OWNER RULING — hole-flags: yes to all (weak values do not propagate; only an explicit `i` is inherited at a hole; `m` and `s` are no longer inherited)"): ruled 2026-11-21 re-dated 2026-11-22. Statement until then: "The two sides of an `&` written inside a hole each start with the flags in force at the hole, a flag a side writes for itself winning."; the bullet until then: "The inherited flags are the hole's own list (`i`, `m`, `s`: core/holes/flags)."; the trigger's sentence until then: "The trigger is stated for `i`; `m` and `s` follow the same comparison (a reading)." Both lines stand (an explicit `(?i)`, docs/dev/lanes/predspot_evidence/ predspot_model.py FSWEEP).
- 2026-11-23 (lane predfix84, review r84 A2, A8, C1, C6; record "2026-11-23 MANAGER — review r84 (predspot1122): the dispositions, ruled with the 2026-11-23 rulings in hand; no owner words"): the binding bullet until then: "A binding of an `&` put in a hole behaves the same: for flags and matching a binding is its expression where it is used (its label reads are its own: core/holes/bare-condition/nested-scope), so `C := /[a-z]+/ & /b.*/` at `/(?i)id-${C}/` is the `&` written in the hole (a reading)." Now for matching where used, for flags where WRITTEN plus an explicit `i` from the hole (A2), with two lines ("Bound in a library", "Written in the hole"); the trigger bullet gains the `-i` clause (A8, a reading), and core/diagnostics/warnings' row "an explicit `i`" to "an explicit `i` or `-i`"; "of hole-flags" cited as hole-flags' "yes to all" (C6); "`m` and `s` no longer reach a side" to "do not reach a side"; three readings marked (C1, A2).

## core/holes/labels — Labels through a hole
slugs: inner-label-read
rulings:
- 2026-11-22 "default-export: protected" (record: "2026-11-22 OWNER RULING — default-export: protected"); a hole is a part used alone: its labels flow into the outer definition and no further
- 2026-11-22 "label-reference: required. we can relax it later as you say although i'm not inclined to." (record: "2026-11-22 OWNER RULING — label-reference: required"); his example 1 and the line spelled with the source
- 2026-11-18 "export-rule: Agee and add [_a = A] is a private reference that wouldn't export at all" (record: "2026-11-18 OWNER RULING — export-rule: public unless `_`; a binding shows its own public labels and its public part labels")
- 2026-11-18 "Agree", under the manager's heading "Inserting through a hole." (record: "2026-11-18 OWNER, continuing the export-scope discussion"); his agreement to the manager's lean in a DISCUSSION (the entry says nothing is ruled by it): only the inserted part's exported names flow into the outer pattern
- 2026-11-21 (class: EXAMPLE, given "rather than rules") "C can see d as a flat look into A." (record: "2026-11-21 OWNER RULING — pure-label: captures are written explicitly; a label is made a capture afterwards too; `_` labels never export; three examples of what a definition may name"); of `A := [d = digits]`, `B(rx) := /${rx}xx/`, `C := B(A) & (d: <100)`: a label flows out through a macro's parameter hole
rejected:
- his lean "a filter can never produce captures" as a rule — by owner ruling — export-rule ("NOT CARRIED": visibility goes by export, not by an operand's role); the form he wanted is `[_ = A]`.
readings:
- inner-label-read (does the outer program see a label defined inside an inserted pattern) is answered by export-rule (2), (3) and the hole row (the manager's, 2026-11-19) — UNTESTED here (PART TA of predspec291 shows `/${isodate}!/` exporting).
- (review r83 D8, the manager's) at the top nothing is outside: the program's own text and the parts it uses alone are both visible to it — SUPPORTED as run (docs/dev/lanes/predfix83_evidence/ predfix83_model.py TOPLEVEL and GRID: `isodate & (isodate.year: < 2100)`, `B(/(?<g>\d)/) & (g: <5)` under (local); sabotage s24 caught).
evidence: preddoc1 EX-labels; PART TA of predspec291; docs/dev/lanes/predspot_evidence/ predspot_model.py SWEEP (lane predspot).
history:
- 2026-11-18: the export-scope discussion and export-rule; 2026-11-19 same-name-count's "(and `$h`)" withdrawn, leaving inner-label-read, then answered by this piece.
- 2026-11-21 (lane predscope, pure-label folded): two bullets added (what flows is labels; his example 1 through a parameter hole). Status date 2026-11-18 to 2026-11-21. evidence: predscope_model.py EX1 (and CONTROL: equal to `(?:[1-9]\d?|0)xx` on 1,365 texts).
- 2026-11-22 (lane predfix77, review r77 D11 (GENERAL-6); record "2026-11-22 MANAGER — review r77 (predfold1121): dispositions ruled (no owner words)"): bullet until then, verbatim: "What flows is LABELS: a capture is made only where it is written (core/labels/export, statement 5)." It now says a label carries whether it is a capture. No answer moved.
- 2026-11-22 (lane predref, label-reference sweep and helper-captures fold): bullets until then, verbatim: "The outer program reads an inserted pattern's public label by the label rules as defined (the last mention); a private `_` label never flows out." and "Through a macro's parameter hole as well: in his example `C := B(A) & (d: <100)` (B(rx) := `/${rx}xx/`), \"C can see d as a flat look into A\" (core/holes/bare-condition/nested-scope)." Now through the source (`year.v`, `A.d`). The line's program `/${year}-x/ & (v: >= 2000)` re-spelled `/${year}-x/ & (year.v: >= 2000)`; answers unchanged (docs/dev/lanes/predref_evidence/ predref_model.py RESPELL). Status date 2026-11-21 to 2026-11-22.
- 2026-11-22 (lane preddef, default-export folded; record "2026-11-22 OWNER RULING — default-export: protected"): statement until then: "For labels, only the inserted pattern's public (exported) labels flow into the outer pattern; for matching it behaves like a literal." Its outer-read bullet until then ended "a private `_` label never flows out."; it gains: the definition holding the hole exports none of them; to pass them on it labels the insert. The macro-parameter bullet marked: awaits argument-default.
- 2026-11-22 (lane predfix83, review r83 D8, D9; record "2026-11-22 MANAGER — review r83 (preddef1122): dispositions ruled; one correction; idiom-confirm closed on default-export (no owner words)"): statement until then: "For labels, only the inserted pattern's exported labels flow into the outer pattern, and no further out: a hole is a part used alone; for matching it behaves like a literal." (it dropped the labelled insert, D9). The capture sentence ("travels with its label wherever export lets it") is capture-export's candidate (a), marked "(awaits capture-export)" (D8); the top-level reading added.
- 2026-11-22 (lane predspot, argument-default folded; record "2026-11-22 OWNER RULING — argument-default: an error; and his reason: a label is to the SPOT in the pattern, a parameter is a template, not a piece of the pattern"): the macro bullet's "awaits argument-default, B using the argument alone (core/labels/paths/argument-default)." to "revised by argument-default: B using the argument alone, the read is a compile error; it is legal where B labels the spot (his example 3) or passes the labels on".
- 2026-11-23 (lane predfix84, review r84 C8; record "2026-11-23 MANAGER — review r84 (predspot1122): the dispositions, ruled with the 2026-11-23 rulings in hand; no owner words"): the macro bullet's "revised by argument-default: B using the argument alone, the read is a compile error" now "under argument-default, B using the argument alone, ..." (the base carries no revision marks): his flat look through `B(A)` is REVISED by argument-default where B uses the argument alone.

## core/holes/same-name — Same-name groups through a hole
slugs: same-name-count
rulings:
- 2026-11-19 "same-name-count: scoped" (record: "2026-11-19 OWNER RULING — same-name-count")
- 2026-11-19 "same-name-count: this is only about backreferences, not labels ?" (record: "2026-11-19 OWNER, on same-name-count: backreferences, not labels? — and a MANAGER CORRECTION"); a QUESTION, answered by a correction
rejected:
- R.1.13 REFERENCES (2) read for `\k<h>` across a hole as the last mention — by owner ruling — same-name-count NARROWED it: `\k<h>` reads the outer group; `$h` still the last mention (the draft R.9 row 102).
- a group through a hole counts as a second group of its name — by owner ruling — same-name-count; the rival (the outer `\k<h>` reading the inner group) holds on `a-bb` (preddoc1 sabotage xEX-same-name caught).
- "(and `$h`) mean the outer group" — by the manager's correction the same day — the manager's extension, not asked.
readings:
- `J` has no effect across a hole; the inner `\k<h>` and numbered references are the inner literal's own (the manager's readings 12, 13 of that entry) — SUPPORTED (PART FF of predspec29; A30, A34).
evidence: preddoc1 EX-same-name; PART SN of predspec281; PART SC of predspec291.
history:
- 2026-11-18: same-name-twice's reading (m1) left the hole case unstated; 2026-11-19 ruled.
- 2026-11-19 (lane preddoc6, review r60 RECOUNT-6): the draft R.9 candidate for this piece, PARTIAL at r59 and left unchanged by preddoc5, now has its own `rejected:` line.

## core/holes/bare-condition — A bare condition in a hole
slugs:
rulings:
- 2026-11-21 "zero-in-definition: a" (record: "2026-11-21 OWNER RULING — zero-in-definition: a"); the `0` of a condition alone in a hole is the match so far of the definition the hole is written in
- 2026-11-19 ""Inside an inserted part": for a condition bare, yes. like /${(0: digit)}/ but not /${A & (0: digit)}/ where it is only the A" (record: "2026-11-19 OWNER, on `0` inside an inserted part: a bare condition sees the surroundings; `A & (0: ..)` sees only A")
- 2026-11-19 "yes, thanks: /\d${(&(0:digit))}/ and /\d/ & (0: digit) are the same thing" (record: "2026-11-19 OWNER, confirming: a bare condition last in an rx equals the condition on the whole")
- 2026-11-19 "zero-in-sequence: you are a lawyer in your exact wording. this is what is needed now. the condition is always sees the regex composed at the point it is used. so the 0: is the match so far" (record: "2026-11-19 OWNER RULING — zero-in-sequence")
rejected:
- a `0` inside a part inserted through a hole stays that part's own (the draft's reading, PART N NZ of predspec261) — by owner ruling — for a BARE condition; CONFIRMED for `A & (0: ..)` (EX-bare-and: the surrounding reading never holds there, `x3` is not a digit; sabotage xEX-bare-and caught).
- a macro in a hole is the unapplied-macro error (`${(x: digit)}`; the draft §2.3, §5.1) — by owner ruling — a bare condition in a hole is legal (predspec291 report sentence 1).
- `${0: digit}` without parentheses — by the manager's call — a spellings item (core/spellings/condition-parentheses).
readings:
- a condition in a hole behaves as the bare condition written in place (the manager's reading 11, restricted: bound alone, a condition naming a label is bound-condition's compile error, one naming only `0` is open zero-condition-binding, this reading its candidate (a), core/holes/bare-condition/zero-binding) — SUPPORTED for the hole (preddoc1 PART R11: the record's printed answers for `/\d${(0: digit)}x/` reproduced; the rival, the binding as its own rx, never holds; sabotage s15 caught).
- at the very START of an rx it tests the empty match so far, a candidate for the can-never-match diagnostics (the manager's (c)) — UNTESTED (a warning); `/${(0: digit)}/` never holds (zerohole.py, CHECKED CONTEMPORANEOUSLY in the record).
- `A & (0: digit & (b: blah))` = `A & (0: digit) & (b: blah)` (the manager's reading 12) — SUPPORTED for `0` (preddoc1 PART R12: 0 / 0 / 0 of 364, span and b; sabotage s11 caught); after a NAMED label the draft's existing error — UNTESTABLE by run (a refusal).
- WITHDRAWN by the manager (record: "2026-11-22 OWNER, on bound-condition: "the form A := (x: blah) has to be illegal"; his read, a response asked for; two alternatives"): (the manager's (b) of zero-in-definition) a condition bound ALONE has no rx of its own: its `0` is the match so far of the definition it is USED in — UNTESTED (not settled by the record: the answer as put, "`0` is the match so far of the definition it is written in", read literally makes the binding that definition, its match so far at the condition empty). The two answers RUN on `/\d${c}x/`, c := `(0: rx.digit)`: as if in place WHOLE `7x` HOLDS; the binding's own `0` never matches (predscope_model.py ZCBIND; sabotage s12 caught). The question was asked as bound-condition (record: "2026-11-21 OWNER, after bare-nested-scope was ruled: "please discuss if you see an issue"; a capture of B compared against a capture of A"; again "2026-11-21 OWNER, on bound-condition: two examples of what `0` is bound to"); zero-condition-binding was lane predscope's proposed slug only (review r77 D6, RULING-2). Moved to core/holes/bare-condition/bound-condition with its lines.
- (the manager's (c)) `${A & (0: S)}` is unchanged, that `0` only A — SUPPORTED by the record (operand-world, ruled; the 2026-11-19 "but not /${A & (0: digit)}/ where it is only the A"); not re-run here (preddoc1 EX-bare-and).
evidence: preddoc1 EX-bare-condition, EX-bare-and, PARTS R11, R12; zerohole.py, zeroseq.py (the record's runs).
history:
- 2026-11-19: zero-in-sequence, then his "yes ... but not", his confirmation, his spelling correction `${0: digit}`, his "${} implies (?:${})" (SUPPORTED by hole-reading), then the parentheses remarks; rev 29.1 only marked §2.3.
- 2026-11-19 (lane preddoc4): this piece owns the facts on `0` and a bare condition in a hole; core/conditions/match-so-far points here; the parentheses bullet (a spelling call) is core/spellings/condition-parentheses's (review r59 RULING-8).
- 2026-11-19 (lane preddoc6, review r60 DIGIT / COLD-3 / FIXVER-9): a bare `digit` (the owner's own spelling, "like /${(0: digit)}/") written `rx.digit`, the form lib/rx/classes defines; built mechanically the bare name was an undeclared name, a compile error (core/operators/statements). Answers unchanged (preddoc6 PART DG).
- 2026-11-21 (lane predscope, zero-in-definition folded): statement until then: "A condition alone in a hole sees the regex composed at the point the hole stands: its `0` is the surrounding rx's match so far; in `${A & (0: S)}` the `0` is only A." Bullet until then: "A binding whose whole body is a bare condition, used in a hole or as a sequence operand, behaves as the bare condition does (a reading, run)." Its `0` now stated as unsettled, two run lines added. Status date 2026-11-19 to 2026-11-21.
- 2026-11-22 (lane predfix77, review r77 A4, A3, D6, D2; record "2026-11-22 MANAGER — review r77 (predfold1121): dispositions ruled (no owner words)"): statement until then, verbatim: "A condition alone in a hole is read in the definition the hole is written in: its `0` is that definition's match so far to the hole, holes filled; in `${A & (0: S)}` the `0` is only A." (it made `/\d/ SEQ B((0: /\d/))` FAIL against match-so-far's printed "An argument" line, HOLDS). The bound-condition bullet ("A binding whose whole body is a bare condition ... asked as zero-condition-binding.") and its two lines ("As if in place (the reading)", "Read as the binding's own `0`") moved to the open sub-piece core/holes/bare-condition/bound-condition, where the lines are re-run; "an rx" became "a definition" in two bullets.
2026-11-22 (lane predbound, bound-condition ruled; record "2026-11-22 OWNER RULING — bound-condition: "mostly confirmed"; `c := (0: 5)` left open"): the bullet until then, verbatim: "A condition bound to a name of its own, or returned by a macro, used in a hole or as a sequence operand: open (core/holes/bare-condition/bound-condition)."; now the ruled compile error, and `0` alone open (core/holes/bare-condition/zero-binding). Status date 2026-11-21 to 2026-11-22.

## core/holes/bare-condition/labels — Labels a bare condition reads
slugs: bare-condition-labels
rulings:
- 2026-11-21 "lol. i meant b" (record: "2026-11-21 OWNER RULING — bare-nested-scope, case 2: b (a separately defined piece reads its own value only)"); (b) as put to him, with the witness pair shown first: "Own value only. A definition is sealed for values as well as names, and the compose-equals-literal rule gets an exception: it holds for what the user sees, not for what a piece reads inside itself."; his answer before it, its letter unclear, is the record entry just before this one
- 2026-11-19 (class: GUESS) "it's the scope of the whole rx for visibility" (record: "2026-11-19 OWNER, bare-condition-labels: a GUESS: the whole rx is the scope; the last label to its left, otherwise the next to its right"); his guess, adopted as ruled by the entry below (its item 1)
- 2026-11-19 "The first time through the loop, the reference is unset then the label is set. The second time through, the reference is set to the previous loop value." (record: "2026-11-19 OWNER RULING — bare-condition-labels: the label as it stands at the hole; unset the first time through; no such label is an error")
- 2026-11-19 "If the reference matches not label, it's an error" (record: "2026-11-19 OWNER RULING — bare-condition-labels: the label as it stands at the hole; unset the first time through; no such label is an error")
rejected:
- the inserted part's own namespace, under which `(h: ..)` alone in a hole is a compile error (the place table's hole row applied to a bare condition) — by owner ruling — bare-condition-labels.
- the condition read as if written after the literal, wherever the hole stands (his first sentence taken for every position) — by the owner's own observation ("I notice, it's not the same"; "I was thinking of scope not value") — it holds for a hole written last.
- a forward read where nothing to the left has set the label (one reading of his guess "otherwise the next label to its right") — by owner ruling (in a loop) — "The first time through the loop, the reference is unset"; outside a loop the manager's reading ("he spoke of the loop only"; the record's reading (a)): answer-moving, `/${(c: >= 5)}(?<c>\d)/` WHOLE `7` FAILS today and would hold under the forward read (bcl_guess.py).
- "before its label's group" judged on the rx as composed, so `A SEQ B`, B := `/${(c: >= 5)}(?<c>\d)/`, reads A's c (the manager's ruling of review r61 F-D; listed SUPPORTED until 2026-11-22 from predfix61 FD, which still passes asserting it) — by owner ruling — bare-nested-scope case 2: b; B reads its own value only: `A SEQ B` never matches (predfix77 SEALED, against `(?!)` on 31 texts over `73`; sabotage s8 caught).
- the surrounding rx is the rx as composed where the hole stands, when the literal holding it is inserted or an `&` operand (the manager's reading, listed live and "open" until 2026-11-22) — REPLACED by bare-nested-scope (ruled 2026-11-21): the definition the condition is written in.
readings:
- outside a loop, a hole before its label's group reads it unset and the test's outcome is fixed: `pcrec.test.never` where it then fails, `pcrec.test.always` where it then holds; the warning, not the error (the manager's reading; he spoke of the loop only) — UNTESTED as a diagnostic; the answers RUN at both polarities (predfix61 FC; sabotage s3 caught).
evidence: preddoc1 PART R10 (re-run 2026-11-19, same answers); the record's runs bcl_end_vs_point.py and bcl_guess.py; predfix61_model.py FC, FD, FG (every line but the first; the matcher checked against python `re`, CONTROL). predfix77_model.py SEALED (the lines "Two definitions", "One definition"; the citations of predscope CLOSEDB re-pointed here).
history:
- 2026-11-21 (the manager, bare-nested-scope case 2): the surrounding rx is the definition the hole is written in. Bullet before: "The surrounding rx is the rx as composed where the hole stands; which labels a hole may name when its definition is used inside another, or is an `&` operand, is core/holes/bare-condition/nested-scope's (his three examples ruled; a label of the definition's user open)." and "`A SEQ B`, B := `/${(c: >= 5)}(?<c>\d)/`, reads A's c (B writes a c of its own, so the name is legal; that the value is A's is the composed reading, nested-scope)." The line "Composed: WHOLE `73` HOLDS, `37` FAILS / SEARCHED `37 73` `73`@3 / FIND-ALL `73 37 51` [`73`@0, `51`@6]" for `A SEQ B` became "Two definitions: WHOLE `73` FAILS ..." (predscope CLOSEDB, closed side); its old answers are the one-definition spelling's.
- 2026-11-19: listed by the manager in the "`0` inside an inserted part" entry ((a): "if the draft's rows part, ASK"); NEW owner question.
- 2026-11-19: open until ruled; the statement then: "Which labels does a bare condition in a hole read: the surrounding rx's labels as they stand at the hole, or the inserted part's own namespace, where it has none?" The manager's reading 10 (the surrounding labels at the hole; preddoc1 PART R10, sabotage s10 caught; precedent hit-carry's witness `occurrences(/${c}(?<h>\d)/, min = 2)`) is now his ruling.
- 2026-11-19 (lane predfix61, review r61 F-C, F-D, F-E, F-G, F-J (RULING-4)): the statement until then: "A bare condition in a hole sees the labels of the whole surrounding rx and reads each as it stands where the hole is; a label no group of that rx carries is a compile error." ("the whole surrounding rx" reached private labels the export rule hides.) Its bullets until then, verbatim: "Written last in the rx, the bare condition equals the condition after the literal: `/(?<c>\d)${(c: >= 5)}/` is `/(?<c>\d)/ & (c: >= 5)`." (true at top level only: inside an optional it parts, 1 / 58 / 90 of 121, predfix61 FG); "Outside a loop, a hole before its label's group reads it unset: the test can never pass (the warning `pcrec.test.never`, not the error; a reading)." (true only for a test that fails on unset; the partition "outside a loop" judged on the written literal). The loop bullet gains the first-pass condition (a positive first-pass test: 0 matches of 1,093 texts, predfix61 FD).
- 2026-11-21 (lane predscope): the pointer to nested-scope restated (a definition used inside another, not "the literal holding the hole"); the Composed line's sentence notes that B writes a c of its own (legal by name) and that A's value is the composed reading: closed to its user, `A SEQ B` never matches (predscope_model.py CLOSEDB; sabotage s8 caught; that check needs the removed "Composed:" line and can never pass again, review r77 D9: re-pointed to predfix77 SEALED). Answers unchanged.
- 2026-11-22 (lane predfix77, review r77 D1, D2 (FIXIND-14), A4, D12 (RULING-11); record "2026-11-22 MANAGER — review r77 (predfold1121): dispositions ruled (no owner words)"): statement until then, verbatim: "A bare condition in a hole sees every label visible in the surrounding rx and reads each as it stands where the hole is; a label not visible there is a compile error."; status date 2026-11-19 to 2026-11-21. The bullet "The surrounding rx is the DEFINITION the hole is written in" became "the one the CONDITION is written in (an argument is its caller's: a reading)"; "the rx as composed" became "the definition"; "(nested-scope; the last line below)" pointed at the wrong line: now "the line Two definitions below". Two stale readings moved to `rejected:`. No answer moved.

## core/holes/bare-condition/nested-scope — What a hole in a used definition may name
slugs: bare-nested-scope
rulings:
- 2026-11-22 "default-export: protected" (record: "2026-11-22 OWNER RULING — default-export: protected"); a part used alone is local to the piece that uses it
- 2026-11-21 "lol. i meant b" (record: "2026-11-21 OWNER RULING — bare-nested-scope, case 2: b (a separately defined piece reads its own value only)"); (b) as put to him, with the witness pair shown first: "Own value only. A definition is sealed for values as well as names, and the compose-equals-literal rule gets an exception: it holds for what the user sees, not for what a piece reads inside itself."; his answer before it, its letter unclear, is the record entry just before this one
- 2026-11-21 "bare-nested-scope: case 1: compile error at inner." (record: "2026-11-21 OWNER RULING — bare-nested-scope, case 1: a compile error at inner; and a question on a label variable")
- 2026-11-21 "zero-in-definition: a" (record: "2026-11-21 OWNER RULING — zero-in-definition: a"); it settles the `0` line of this piece (the entry's class, in the manager's words, is in history)
- 2026-11-21 (class: EXAMPLE) "let me give some examples rather than rules: 1.  A := [ d = digits ] B(rx) := /${rx}xx/ C := B(A) & (d: < 100) is legal. C can see d as a flat look into A. C cannot see rx as its a binding variable not a label." (record: "2026-11-21 OWNER RULING — pure-label: captures are written explicitly; a label is made a capture afterwards too; `_` labels never export; three examples of what a definition may name")
- 2026-11-21 (class: EXAMPLE) "2. previous but B(rx) := /${rx}xx/ & (d: <100) is incorrect." (record: "2026-11-21 OWNER RULING — pure-label: captures are written explicitly; a label is made a capture afterwards too; `_` labels never export; three examples of what a definition may name")
- 2026-11-21 (class: EXAMPLE) "3. previous but B(rx) := /${[dd = rx]}xx/ & (dd: < 100) would be correct" (record: "2026-11-21 OWNER RULING — pure-label: captures are written explicitly; a label is made a capture afterwards too; `_` labels never export; three examples of what a definition may name")
- 2026-11-22 "array-in-piece: if it was written A & /B-defintion/ then the some(h) would see the h from A. but because B is bound first, its internal references refer only to what can be seen at that point." (record: "2026-11-22 OWNER RULING — array-in-piece: b (a group question inside a bound piece reads only what that piece can see)")
- 2026-11-22 "or A SEQ /B definition/" (record: "2026-11-22 OWNER, adding to array-in-piece: "or A SEQ /B definition/""); his addition: both in-place compositions
- 2026-11-22 "argument-default: for me this is an error. I'm just trying to articulate why it's an error other than form. I get that it might not end up in the pattern. I think for me it has to do with whether or not it's definitively part of the pattern being constructed or if it's a parameter to it. B(rx) := you can't take a label against rx directly. You can take a label to the spot that rx gets laid into the regex. The label is not to the regex abstractly, it's to the spot in the pattern where the regex is being inserted. A parameter like rx in a call B(rx) cannot be labeled because it's not being placed into the pattern. It's not a piece of the pattern. It's a template of the rx that might be placed into the pattern." (record: "2026-11-22 OWNER RULING — argument-default: an error; and his reason: a label is to the SPOT in the pattern, a parameter is a template, not a piece of the pattern"); it REVISES example 1.
rejected:
- COMPOSED for names (candidate (c) of 2026-11-21: a piece may name a label its user sets, an error only at a use with none) — by owner ruling — case 1: "compile error at inner"; the lines it would give: `/(?<h>\d)${inner}/`, inner := `/x${(h: <5)}/`: WHOLE `3x` HOLDS, `7x` FAILS / SEARCHED `7x 3x` `3x`@3 / FIND-ALL `3x 7x 4x` [`3x`@0, `4x`@6]; inner := `/x${$h}/`: WHOLE `3x3` HOLDS, `3x7` FAILS / SEARCHED `3x7 3x3` `3x3`@4 / FIND-ALL `3x3 7x7 3x7` [`3x3`@0, `7x7`@4] (predfix61 FE).
- SHARED values (candidate (a) of case 2: a public label is one label across the composed rx, so B's test reads A's c; the documents' line until 2026-11-21, WHOLE `73` HOLDS) — by owner ruling — case 2: "i meant b"; his reason ("in a loop around the insides of the B ... the first time through it is unset") was checked: the loop case is the same under both, entering the loop resets the label (record, the "no, c" entry).
- COMPOSED for `0` (candidate (b) of the `0` line) — by owner ruling — zero-in-definition: a.
- COMPOSED for a label only a parameter holds — by owner ruling (example 2, "is incorrect") — composed, `B(A)` would match exactly as example 1 (predscope_model.py EX2).
- the LITERAL as the unit of scope (candidate (a) as first put) — by the owner, "literals are not the way to think about it" (record: "2026-11-21 OWNER, discussing bare-nested-scope: literals are not the way to think about it; construction; which way a hole is filled; descending and horizontal; the kind of hole") and zero-in-definition's unit, the definition.
- (the manager's (c) of case 2) a piece looped by its user reads its own previous pass — withdrawn by the manager ("2026-11-21 OWNER, his "issue definition" ..." entry; review r77 A12) — with (d) it made `(B SEQ ";"){2}` and its written-out form part; under it the loop's line would be WHOLE `7;3;` FAILS (predfix77 LOOPPIECE, the line in the report).
- (b) composed for a label of the definition's USER (listed "open" in `readings:` until 2026-11-22, a residue) — by owner ruling — case 1 refuses that very case ("compile error at inner"); the answers RUN (predfix61 FE; predscope_model.py ZNEST).
- (the manager's (b) of case 2 and of zero-in-definition) a bound condition or computed label has no rx of its own and is laid against the pattern it meets — withdrawn by the manager on his position (record: "2026-11-22 OWNER, on bound-condition: "the form A := (x: blah) has to be illegal"; his read, a response asked for; two alternatives") — it stays the open core/holes/bare-condition/bound-condition, candidate (a).
readings:
- his example 1 spelled `C := B(A) & (A.d: <100)` means what his flat look meant (the manager's reading of the label-reference entry) — SUPPORTED (docs/dev/lanes/predref_evidence/ predref_model.py RESPELL: the line "Example 1" rebuilt, the old bare spelling read as before against the new, the same answers) REVISED by argument-default (2026-11-22): that program is a compile error, B using its argument alone (review r84 C2; the line "Example 1").
- (the manager's (a) of case 2) a piece is a binding or a macro body; what is written inside one definition is one piece — UNTESTED (for the next lane or critic round); his array-in-piece words ("because B is bound first") speak of a BOUND piece; his "bindings define scope" (record: "2026-11-21 OWNER, his "issue definition" for bare-nested-scope: bindings define scope; flags are a symptom of PCRE, probably only `i` inherits; the two languages differ by construction; a sketch `list_of_stuff(X, cmp, S)`") supports it, not as a ruling.
- (the manager's (d) of case 2) two uses of one piece are two pieces, to be confirmed — SUPPORTED as a run of the reading (predfix77 LOOPPIECE: with (c) withdrawn, `rx.repeat(B SEQ ";", min = 2, max = 2)` and `B SEQ ";" SEQ B SEQ ";"`, B := `/${NOT (c: >= 5)}(?<c>\d)/`, agree, 0 / 0 / 0 of 364 texts over `37;`, both equal to `\d;\d;`; one definition looped, `/(?:${NOT (c: >= 5)}(?<c>\d);){2}/`, reads its previous pass, equal to `[0-4];\d;`; sabotage s7 caught).
- (the manager's (e) of case 2) an argument is the caller's text and reads the caller's labels — SUPPORTED for a condition (predscope WHEN, ZARG).
- [review r83 D9: also contrary to the manager's reading (e) of default-export, an argument the body uses alone not exported] (the manager's (a) of pure-label) the rule his three examples fit: a body names the labels it writes and the public labels of the parts it writes in, never a label of a parameter; a parameter's public labels pass through to the user; a parameter's name is never a label — NOT SUPPORTED as stated: run over 17 definitions the documents print, it refuses 7 (pass-start-read's `c`, computed-labels' `sum`, count's `n`, length's `nchars`, month_numbered's `mnum`, and this piece's Condition and Read lines); SUPPORTED with bound conditions and computed labels outside it (they are laid against the labels of the pattern they meet), then only this piece's two lines (predscope_model.py NAMES; sabotage s7 caught). It fits all three examples (EX1-EX3).
- (the manager's (b) of pure-label) this is the CLOSED answer to bare-nested-scope for labels and reads — UNTESTED (untestable by the record: none of his examples names a label of the definition's USER, which is what the Condition and Read lines do; example 2 is a parameter's label).
- a used piece takes the flags at its hole but not the labels around it, by construction (review r77 D3, the asymmetry the manager named "to be stated") — SUPPORTED by runs: core/holes/flags/in-filter's `/(?i)${C}/` line (flags flow in) beside the line "Two definitions" (values do not; predfix77 SEALED).
- a group question inside a piece: ruled by array-in-piece (b) (core/labels/labels-vs-captures); review r77 A1 is settled by it.
evidence: predfix77_model.py SEALED (every line of this piece but the loop lines, lowered from the printed text with the provided names: "Two definitions", "One definition", "Passing the condition", "Match so far", "Example 1", "Example 3"; case 1 and example 2 refused at the definition; sabotage s8 caught), LOOPPIECE (the three loop lines; sabotage s7 caught). The citations of predscope CLOSEDB and innerv.py re-pointed here (review r77 D9: CLOSEDB can never pass again). Earlier: predfix61_model.py FE (three readers, both candidates; under (a) the condition and `$h` are refused, `0` reads the inner literal's `x`); docs/dev/lanes/predspot_evidence/ predspot_model.py SWEEP (lane predspot).
history:
- 2026-11-21 (the manager, two rulings of one question): bare-nested-scope RULED: case 1 a compile error, case 2 own value only. Status `open bare-nested-scope 2026-11-21` to `ruled 2026-11-21`. Statement before: "When a definition holding a hole is used inside another, may the hole's readers (a bare condition, `$y`) name a label its user sets, or only the labels the definition itself holds?" Its open part before: "OPEN: a label the definition's USER sets (the Condition and Read lines); no example of his names one. Candidates: (a) CLOSED: a compile error, as for a parameter's label; (b) COMPOSED: the rx as composed where the definition is used." The Condition and Read lines moved to rejected; the line "Example 2, the composed reading he refused" dropped (a compile error has no line); "Passing the condition" added (the manager's hand-built run, innerv.py, not a lane's evidence); "Two definitions" is predscope CLOSEDB's closed side, "One definition" its composed side.
- 2026-11-19 (lane predfix61, review r61 F-E: REACH-5, REACH-9, RULING-13, GENERAL-14): a new open sub-piece at the manager's ruling of review r61; one question for the three readers at a hole. The free-name ruling quoted in its statement: "It is like if a function in C were defined then references a variable it doesn't have defined so it looks up the call stack to the previous definition. Catastrophic." (record: "2026-11-18 OWNER RULING — free-name: a reference to a name the rx does not define is an error").
- 2026-11-21 (lane predscope, zero-in-definition and the three examples folded): heading "Which rx a hole in an inserted literal reads" to "What a hole in a used definition may name"; statement before: "When the literal holding a hole is itself inserted into another rx, or is an `&` operand, do the hole's readers (a bare condition, `$y`, `0`) read that literal or the rx as composed?" Its candidates before: "(a) LEXICAL: the literal the hole is written in (a label it does not define is a compile error; its `0` starts where that literal starts); (b) COMPOSED: the rx as composed where that literal ends up." The `0` line ruled ("Match so far, (a)" now "Match so far (ruled)"; the "(b)" line moved here: WHOLE `3x` HOLDS, `7x` HOLDS / SEARCHED `a3x` `3x`@1 / FIND-ALL `3x 7x` [`3x`@0, `7x`@3]); his three examples and their run lines added; the question narrowed to a label the definition's user sets. The status stays open (the lane's proposal: the Condition and Read lines are not decided by any ruling). Date 2026-11-19 to 2026-11-21.
- 2026-11-22 (lane predfix77, review r77 A12, A3, A1, D1, D9, D10, D3, D5 (RULING-3); record "2026-11-22 MANAGER — review r77 (predfold1121): dispositions ruled (no owner words)"): reading (c) withdrawn and folded (the loop pair printed agreeing, (d) marked "to be confirmed" in the base); the bound-condition exemption marked "(a reading; open bound-condition)"; the array collision pointed at; the flags/labels asymmetry stated once; the example lines' `[d = digits]` (no `digits` is provided) now `[d = rx.digits]`, his own words kept with "(his spelling)"; the VALUES bullet's "its own previous pass in a loop" narrowed to a loop written inside it. The class sentence of zero-in-definition, under `rulings:` until then: "It settles the `0` line of bare-nested-scope: candidate (a) of that piece, with the unit the DEFINITION (a binding or a macro body), not the literal" (the entry's class, the manager's words). Readings bullet until then, verbatim: "Readings (the manager's): a piece is a binding or a macro body, and what is written inside ONE definition (literals, operands, holes, an `&` operand's hole) is one piece; a bound condition or computed label has no rx of its own and is laid against the pattern it meets (core/conditions/form); an argument is the caller's text and reads the caller's labels; a piece looped by its user reads its own previous pass; two uses of one piece are two pieces." No printed answer moved.
- 2026-11-22 (lane predfix77, R-1, R-2 and the bound-condition position): the VALUES bullet names the group questions and `h[k]` (array-in-piece), his sentence quoted; the NAMES bullet no longer states the withdrawn reading (a) for a bound condition, which is open.
2026-11-22 (lane predbound, bound-condition ruled; record "2026-11-22 OWNER RULING — bound-condition: "mostly confirmed"; `c := (0: 5)` left open"): in the NAMES bullet, "a label variable is an idea (parked/ideas/label-parameter). A condition or computed label bound alone: open (core/holes/bare-condition/bound-condition)." became the under-construction pointer (core/operators/bindings/label-variables) and the ruled compile error; `see:` re-pointed from the parked idea. Status date 2026-11-21 to 2026-11-22. The line "Passing the condition" re-run unchanged (predbound INPLACE).
2026-11-22 (lane predbound, R-3, label-reference ruled): his example 1 marked "its spelling revised: core/labels/paths/label-reference"; the example is his and its lines are left for the next lane's sweep.
- 2026-11-22 (lane predref, label-reference sweep and helper-captures fold): example 1's tail until then: "(its spelling revised: core/labels/paths/label-reference)"; now the spelling under label-reference, his quote kept whole. The line "Example 1" re-spelled `C := B(A) & (A.d: <100)`, answers unchanged (docs/dev/lanes/predref_evidence/ predref_model.py RESPELL). Example 2 stays a printed refusal; example 3 writes its part label `dd` and is unchanged.
- 2026-11-22 (lane predfix82, review r82 GENERAL-5; record "2026-11-22 MANAGER — review r82 (predfold1122): dispositions ruled; two corrections of record entries (no owner words)"): the bound-alone sentence gained its condition (a label the binding does not hold) and the open `0` case.
- 2026-11-22 (lane preddef, default-export folded; record "2026-11-22 OWNER RULING — default-export: protected"): his example 1 (bullet and line "Example 1") marked "(awaits argument-default)": B(rx) := `/${rx}xx/` uses rx alone, so whether the caller's `A.d` is legal is the new open question (core/labels/paths/argument-default); under its candidate "error" the binding C is refused (preddef_model.py AWAITS). His example 3 is unchanged.
- 2026-11-22 (lane predfix83, review r83 D2; record "2026-11-22 MANAGER — review r83 (preddef1122): dispositions ruled; one correction; idiom-confirm closed on default-export (no owner words)"): CORRECTION 1 of the record entry: the VALUES bullet until then ended "the exception to "a compose and a literal rx have the same label behavior" (core/labels/flow), which holds for what a piece's USER reads (the lines "Two definitions", "One definition")." Default-export narrows case 2's "holds for what the user sees" as well: the user reads only what each piece exports (a consequence, the manager's reading; docs/dev/lanes/predfix83_evidence/ predfix83_model.py WITNESS).
- 2026-11-22 (lane predspot, argument-default folded; record "2026-11-22 OWNER RULING — argument-default: an error; and his reason: a label is to the SPOT in the pattern, a parameter is a template, not a piece of the pattern"): example 1's sentence until then: "Spelled under label-reference `C := B(A) & (A.d: <100)`: what his flat look meant is what `A.d` means (core/labels/paths/label-reference, core/labels/paths/call-prefix); under default-export B uses rx alone, so it awaits argument-default (core/labels/paths/argument-default)."; now REVISED, a compile error. The line "Example 1" (WHOLE `42xx` HOLDS, `100xx` FAILS, `042xx` FAILS) is a compile error; the line "Example 1, the spot labelled" (`C := B(A) & (B.dd.d: <100)`, B(rx) := `/${[dd = rx]}xx/`) gives the answers it gave.
- 2026-11-22 (lane predspot, hole-flags folded; record "2026-11-22 OWNER RULING — hole-flags: yes to all (weak values do not propagate; only an explicit `i` is inherited at a hole; `m` and `s` are no longer inherited)"): the bullet until then: "A used piece takes the flags at its hole (core/holes/flags) but not the labels around it: the two differ by construction ("bindings define scope")."
- 2026-11-23 (lane predfix84, review r84 C2, C8; record "2026-11-23 MANAGER — review r84 (predspot1122): the dispositions, ruled with the 2026-11-23 rulings in hand; no owner words"): example 1's "REVISED by argument-default ("for me this is an error"): a compile error" now "under argument-default (...): a compile error" (the base carries no revision marks): his example 1 of 2026-11-21 is REVISED by argument-default; its SUPPORTED reading marked.

## core/holes/bare-condition/bound-condition — A condition bound to a name of its own
slugs: bound-condition
rulings:
- 2026-11-22 "cound-condition: mostly confirmed. i leave the c := (0: 5) open" (record: "2026-11-22 OWNER RULING — bound-condition: "mostly confirmed"; `c := (0: 5)` left open"); RULED (b) by confirmation of the list put to him, every item but the `0` case; his slug typed "cound-condition"
- 2026-11-22 "bound-condition: the form A := (x: blah) has to be illegal. x has no references in the binding. further A := /x/ & (y: blah) is also illegal as y has no target. this is the only read consistent with the earlier binding decisions. this is my read. please respond. alternatives: 1. macro variables A(x:) := (x: < 2100) 2. macro types B(d & isodate) := B(year: < 2100) (spellings tbd)" (record: "2026-11-22 OWNER, on bound-condition: "the form A := (x: blah) has to be illegal"; his read, a response asked for; two alternatives"); the two statements of the ruling, in his words: "the form A := (x: blah) has to be illegal. x has no references in the binding. further A := /x/ & (y: blah) is also illegal as y has no target."
- 2026-11-22 (class: CORRECTION) "bound-condition: correction to rx: B(d & isodate) := (year: < 2100)" (record: "2026-11-22 OWNER, correcting his second alternative: `B(d & isodate) := (year: < 2100)`"); his second alternative corrected (core/operators/bindings/macro-types)
- 2026-11-22 (class: CLARIFICATION) "illegal meaning a compiler error" (record: "2026-11-22 OWNER, on bound-condition: "illegal meaning a compiler error""); the forms he called illegal are compile errors, not the under-construction error
- 2026-11-21 (class: EXAMPLE) "bound-condition: A := /\d${(0: 5)}/ binds the literal to 5. A := /\d/ C := /.${A & (0: 5)}/ the 0: is bound to A only" (record: "2026-11-21 OWNER, on bound-condition: two examples of what `0` is bound to"); now in core/holes/bare-condition/zero-binding
- 2026-11-21 (class: CONFIRMATION) "that settles it. my two examples are correct." (record: "2026-11-21 OWNER, confirming his two examples of `0`: "that settles it. my two examples are correct"")
rejected:
- (a) a condition bound alone laid against the pattern it meets where it is used (the manager's leaning, withdrawn on his position) — by owner ruling — bound-condition: b. Its line under (a), the macro case, verbatim as run (predfix77 BOUND): "A macro returning a condition, (a): WHOLE `3` HOLDS, `7` FAILS / SEARCHED `x7 3` `3`@3 / FIND-ALL `3 7 4` [`3`@0, `4`@4] (`/(?<h>\d)${lt5(<5)}/`, lt5(S) := `(h: S)`)".
readings:
- the ruling as the model runs it: ten bindings refused at the binding, each naming the label it lacks: `late := (h: >5)`, `A := /x/ & (y: >5)`, `sum := $a + $b`, both `n`, `nchars`, `mnum`, pass-start-read's `c`, `lt5(S) := (h: S)`, case 1's `inner` (predbound REFUSE; sabotage s4 caught).
- (a) a condition written in place, an argument included, is unchanged — SUPPORTED for the argument of `inner` and for `0` in `B`'s argument (predbound INPLACE: the lines "Passing the condition" and "An argument" equal those printed at 1e0384941; sabotage s6 caught); `when`'s test UNTESTED here (no `when` lowering in this model; lib/control/when-test's own run).
- (b) a SET bound alone (`late := >5`, used `(h: late)`) is unchanged: it names no label — SUPPORTED (predbound SETBOUND: the same line as written in place and as the record's pasted `[6-9]` line, 0 / 0 / 0 of 85 texts over `37 9`; sabotage s3 caught).
- (c) the five refused definitions written in place, every printed line unchanged — SUPPORTED (predbound FIVE: six lines, each rebuilt from the new program text and equal to the line printed at 1e0384941 in its answers, each WHOLE against a direct rule 0 differ; sabotage s2 caught). For `n` the in-place form is `(count((d: "7")): ==2)`, not the list's `occurs.exactly(2, (d: "7"))`: count-in-set ruled (b) after the list.
- (e) the error is reported AT THE BINDING, used or not, and is an ordinary compile error — the class SUPPORTED by his words ("illegal meaning a compiler error"); the place a reading, from "x has no references in the binding" and "compile error at inner" (record "2026-11-21 OWNER RULING — bare-nested-scope, case 1: a compile error at inner; and a question on a label variable"); the model refuses an unused `late` and `sum` at their bindings (predbound ATBINDING; sabotage s5 caught).
- (g) a binding whose body USES a pattern that holds the label is legal, by core/labels/export statement 2 — SUPPORTED as a run (predbound LEGAL: `chars`, `months`, `length`, `month_numbered`, `year` legal at their bindings; `year` against `>= 2000` 0 of 256 texts differ; sabotage s7 caught).
- a macro whose body is a condition naming a label it does not hold (`lt5(S) := (h: S)`) is the same form — a reading (the ruling's words name `A := (x: blah)`; his alternative 1 is the macro form that would make it legal).
- (h) the sweep: every binding printed in core.md, library.md and parked.md checked at its binding — at 1e0384941 the refused ones were the five definitions (`c`, `sum`, `n` twice in print, `nchars`, `mnum`), `length`'s body through `nchars`, `lt5`, and the two printed as refused already (`inner`, example 2's `B`); none beyond the five; now every refused binding in the base files is printed as refused (predbound SWEEP; sabotage s13 caught).
- (DES-1, the manager's) a SET that reads a label, bound alone, is the same compile error — SUPPORTED as run (docs/dev/lanes/predfix82_evidence/ predfix82_model.py BOUNDSET; sabotage s12 caught)
evidence: docs/dev/lanes/predbound_evidence/ predbound_model.py REFUSE, SETBOUND, ATBINDING, INPLACE, LEGAL, FIVE, SWEEP, QUOTES, MARKS. Earlier: predfix77_model.py BOUND, HISEX; predscope_model.py ZCBIND.
history:
- 2026-11-22 (lane predfix77, review r77 A3, D6 (RULING-2); record "2026-11-22 MANAGER — review r77 (predfold1121): dispositions ruled (no owner words)"): a new open sub-piece carrying the question as asked twice; the bullet and two lines that were in core/holes/bare-condition (under the proposed slug zero-condition-binding) moved here, their texts re-run: "As if in place (the reading)" is now "(a) where it is used", "Read as the binding's own `0`" is "(b) sealed, its own `0`", the same answers.
- 2026-11-22 (lane predfix77, after the merge of the bound-condition position): the piece states his position (b) and his two alternatives (his placeholders), and no longer states (a) as the reading in force; the readers point here without an answer. Still OPEN (the lane's rulings file: "bound-condition is still OPEN").
- 2026-11-22 (lane predbound, bound-condition RULED (b)): open to ruled; the piece until then, verbatim: statement "Does a condition bound or passed on its own, no pattern in it, read its labels and its `0` where it is used, (a), or is it sealed like a piece, (b)?"; its candidate lines (a)/(b) on `c := (0: rx.digit)` and his two examples moved to core/holes/bare-condition/zero-binding (the `0` case he left open); the line "A macro returning a condition, (a)" moved to `rejected:`; the five printed definitions rewritten in place in their own pieces; the lines "Written in place", "A set bound alone", "A binding that holds its label" added.
- 2026-11-22 (lane predfix82, review r82 DES-1; record "2026-11-22 MANAGER — review r82 (predfold1122): dispositions ruled; two corrections of record entries (no owner words)"): the general form (the manager's reading): every label a binding's body names has its target in it; the line "A set that reads a label, bound alone" (predfix82 BOUNDSET).

## core/holes/bare-condition/zero-binding — A condition on `0` bound to a name of its own
slugs: zero-condition-binding
rulings:
- 2026-11-22 "cound-condition: mostly confirmed. i leave the c := (0: 5) open" (record: "2026-11-22 OWNER RULING — bound-condition: "mostly confirmed"; `c := (0: 5)` left open"); the `0` case taken out of the confirmed list by him: neither answer applied
- 2026-11-21 (class: EXAMPLE) "bound-condition: A := /\d${(0: 5)}/ binds the literal to 5. A := /\d/ C := /.${A & (0: 5)}/ the 0: is bound to A only" (record: "2026-11-21 OWNER, on bound-condition: two examples of what `0` is bound to"); `0` written in place; agrees with what is ruled
rejected:
readings:
- the candidates RUN on `/\d${c}x/`, c := `(0: rx.digit)`: (a) where it is used equals `\dx`; read as sealed, its own `0`, it equals the never-matching `(?!)`, 0 / 0 / 0 of 121 texts over `17x` each (predbound ZERO; sabotage s11 caught); under (b) as asked, a compile error at `c` (the model's option `error`).
- his two examples, lowered from his text: `5` and `.5` (predfix77 HISEX; the lines re-run unchanged by predbound ZERO).
evidence: docs/dev/lanes/predbound_evidence/ predbound_model.py ZERO. Earlier: predfix77_model.py BOUND, HISEX; predscope_model.py ZCBIND.
history:
- 2026-11-22 (lane predbound, bound-condition ruled with this case left open): a new open piece under the slug zero-condition-binding (the name the manager had proposed); its lines moved from core/holes/bare-condition/bound-condition, the same text.
- 2026-11-22 (lane predfix82, review r82 RULING-4; record "2026-11-22 MANAGER — review r82 (predfold1122): dispositions ruled; two corrections of record entries (no owner words)"): the candidates re-lettered (a) where used, (b) a compile error, (c) sealed and legal; statement until then "A condition naming only `0`, bound alone (`c := (0: 5)`): is it read where it is used, (a), or sealed at its binding, (b), a compile error like a condition naming a label?".

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
- 2026-11-15 "That's a good clarification", to the manager's proposed wording that the sides of `&` match the same stretch whole (record: "2026-11-15 RULING — the sides of `&` "match the same stretch whole"; the word "anchored" is kept for the macro")
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
- 2026-11-22 "label-reference: required. we can relax it later as you say although i'm not inclined to." (record: "2026-11-22 OWNER RULING — label-reference: required"); the compile error's suggested text and `date_in`'s body spelled with the source
- 2026-11-13 "Then macro binding is m(x) := /.../ & x" (record: "2026-11-13 evening: macro bindings `m(x) := …`")
- 2026-11-15 "Agree with mapping" (record: "2026-11-14 RULINGS on rev 3's contradictions"); the operand is never an argument; positional, keyword and by-name parameters; sections
- 2026-11-15 "1. start with & and then we'll see. 2. start no, 3. agree" (record: "2026-11-14 RULINGS on rev 3's contradictions"); sections start with `&`; no partial application
- 2026-11-15 "I'm liking your ideas" (record: "2026-11-14 RULINGS on rev 3's contradictions"); under its bold line "2026-11-15 RULING — the type picture"; a call is the macro applied to one record; the record is never a value
- 2026-11-15 "2. yes keep out of phase 1. I like the idea of types but they need more thinking." (record: "2026-11-14 RULINGS on rev 3's contradictions"); under its bold line "2026-11-15 RULINGS — answers to the four questions of review r8"
- 2026-11-14 "I agree with both excepting the spelling ... no alpha operators ... with, check, in ..." (record: "2026-11-14 RULINGS on docs/dev/lanes/predx_report.md §11")
- 2026-11-19 ""Inside an inserted part": for a condition bare, yes. like /${(0: digit)}/" (record: "2026-11-19 OWNER, on `0` inside an inserted part: a bare condition sees the surroundings; `A & (0: ..)` sees only A")
- 2026-11-21 (class: EXAMPLE) "C cannot see rx as its a binding variable not a label." (record: "2026-11-21 OWNER RULING — pure-label: captures are written explicitly; a label is made a capture afterwards too; `_` labels never export; three examples of what a definition may name"); a parameter's name is not a label
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
- (the manager's reading of condition-argument) a condition passed as an argument is resolved in the caller's definition, where it is written — SUPPORTED: `tagged := [kind = "n" | "w"] SEQ ":" SEQ when((kind: "n"), rx.digits, else = rx.repeat(rx.word_char, min = 1))` (printed with provided names since 2026-11-22, review r77 D10: the run used `any_of("n", "w")`, `digits`, `word`, which nothing provides; the same sets, hand-worked) with `when`'s body read from library.md reproduces the record's line (WHOLE `n:42` HOLDS, `n:ab` FAILS, `w:ab` HOLDS, `w:42` HOLDS); `when`'s body then named no label, so resolved there `kind` would not be visible (since wrapper-export the body writes three export lists, `[(=) = test]`, `[(=) = then]`, `[(=) = else]`; they face outward, to the caller, so the conclusion stands and the premise is restated: review r84 D7) (predscope_model.py WHEN; sabotage s18 caught); the ruled when-test admits a condition as the test.
evidence: preddoc3b EXpair.
history:
- 2026-11-13: macro bindings; 2026-11-14/15: the C20/C30/C33/C34 rulings, mapping by sections, the type picture; currying DEFERRED, not dropped (record "2026-11-15 CLARIFICATION — currying is DEFERRED from phase 1, not dropped").
- FINDING for the manager (rule 5): the draft §5.3's `capture(x) := /(?<${x.label}>${x})/`, `each`, `each_group`, `where_group` are structural macros with no piece; `capture` is a BODY in the core language (a library piece), the others compile-time tools.
- 2026-11-19 (lane preddoc3b): converted from `?`; the statements part split off as core/operators/statements (a different status).
- 2026-11-19 (lane preddoc4): `NOT` named as the one exception to no-alphabetic-operators; the record bullet points at tuples (review r59 NEGATION, READ-15).
- 2026-11-21 (lane predscope): a bullet added (a parameter's name is not a label, his words; an argument resolved in the caller, a reading). Status date 2026-11-15 to 2026-11-21.
2026-11-22 (lane predbound, bound-condition ruled): `see:` gains the two under-construction sub-pieces of his alternatives. No rule moves.
- 2026-11-22 (lane predref, label-reference sweep and helper-captures fold): the bullet's two programs until then: "write `isodate & (year: ...)`" and `date_in(years) := isodate & (year: years)`; now `isodate & (isodate.year: ...)` and `isodate & (isodate.year: years)` (the plain idiom is included: the label-reference entry). No line moves (no example runs them; isodate has no body here). Status date 2026-11-21 to 2026-11-22.
- 2026-11-23 (lane predfix84, review r84 D7; record "2026-11-23 MANAGER — review r84 (predspot1122): the dispositions, ruled with the 2026-11-23 rulings in hand; no owner words"): the condition-argument reading's premise "`when`'s body names no label" restated: the body writes export lists, which pass labels outward and give a condition written in the caller nothing to resolve against inside the body.

## core/operators/bindings/label-variables — Macro variables: a parameter that is a label
slugs:
rulings:
- 2026-11-22 "bound-condition: the form A := (x: blah) has to be illegal. x has no references in the binding. further A := /x/ & (y: blah) is also illegal as y has no target. this is the only read consistent with the earlier binding decisions. this is my read. please respond. alternatives: 1. macro variables A(x:) := (x: < 2100) 2. macro types B(d & isodate) := B(year: < 2100) (spellings tbd)" (record: "2026-11-22 OWNER, on bound-condition: "the form A := (x: blah) has to be illegal"; his read, a response asked for; two alternatives"); alternative 1, "macro variables", his spelling a placeholder, "spellings tbd"
- 2026-11-22 "cound-condition: mostly confirmed. i leave the c := (0: 5) open" (record: "2026-11-22 OWNER RULING — bound-condition: "mostly confirmed"; `c := (0: 5)` left open"); "Both alternatives are marked under construction: directions acknowledged, spellings open" was on the confirmed list
rejected:
readings:
- the body names the parameter, so the label has its target at the call (the manager's reading of the direction) — UNTESTED (nothing defined).
- his earlier words "we note that l is a label variable" (record "2026-11-21 OWNER RULING — bare-nested-scope, case 1: a compile error at inner; and a question on a label variable") are the same direction — a reading.
evidence: none (under construction).
history:
- 2026-11-22 (lane predbound, bound-condition ruled): a new under-construction piece; the older idea stays parked (parked/ideas/label-parameter), pointing here.

## core/operators/bindings/macro-types — Macro types: a parameter restricted to a pattern
slugs:
rulings:
- 2026-11-22 "bound-condition: the form A := (x: blah) has to be illegal. x has no references in the binding. further A := /x/ & (y: blah) is also illegal as y has no target. this is the only read consistent with the earlier binding decisions. this is my read. please respond. alternatives: 1. macro variables A(x:) := (x: < 2100) 2. macro types B(d & isodate) := B(year: < 2100) (spellings tbd)" (record: "2026-11-22 OWNER, on bound-condition: "the form A := (x: blah) has to be illegal"; his read, a response asked for; two alternatives"); alternative 2, "macro types", as first typed
- 2026-11-22 (class: CORRECTION) "bound-condition: correction to rx: B(d & isodate) := (year: < 2100)" (record: "2026-11-22 OWNER, correcting his second alternative: `B(d & isodate) := (year: < 2100)`"); the body is the condition alone, the head gives `year` its target
- 2026-11-22 "cound-condition: mostly confirmed. i leave the c := (0: 5) open" (record: "2026-11-22 OWNER RULING — bound-condition: "mostly confirmed"; `c := (0: 5)` left open"); under construction, by the confirmed list
rejected:
- the manager's reading of the body as `d & (year: < 2100)` — by owner correction — "correction to rx: B(d & isodate) := (year: < 2100)".
readings:
- meaning (i) under label-reference: `x & isodate & (isodate.year: < 2100)`, the source naming isodate's year so x's own year does not make it ambiguous — UNTESTED (lane predref's reading, from binding-prefix's "One use" line; no isodate body is run)
- under label-reference the head's body would name `year` through the parameter, `d.year` (his example, `B(d & isodate) := (year: < 2100)`, was written before label-reference was ruled) — the manager's reading, not asked; UNTESTED (macro types are not defined).
- B is a named condition whose target is declared in its head; `B(x)` lays `(year: < 2100)` against x — the manager's reading (record "2026-11-22 OWNER, correcting his second alternative: `B(d & isodate) := (year: < 2100)`"), UNTESTED.
- the two meanings of the restriction, (i) the intersection and (ii) a promise checked at the call — both stated in the record entry, neither chosen; UNTESTED.
evidence: none (under construction).
history:
- 2026-11-22 (lane predbound, bound-condition ruled): a new under-construction piece; the older idea stays parked (parked/ideas/restricted-parameter), pointing here.
- 2026-11-22 (lane predref, label-reference sweep and helper-captures fold): meaning (i) until then: "literally the intersection, `B(x)` is `x & isodate & (year: < 2100)` (writable today as `B(d) := d & isodate & (year: < 2100)`, and `year` is then ambiguous where x itself surfaces `year`, core/labels/flow)"; now spelled with the source, the ambiguity remark replaced (a reading); his own spelling `B(d & isodate) := (year: < 2100)` quoted unchanged, its bare `year` pointed at call-prefix.
- 2026-11-22 (lane predcall, call-prefix case 1 folded): the bullet's end until then, verbatim: "(the head's bare `year`: his spelling, what label-reference would make of it is open, core/labels/paths/call-prefix)." became the reading that under label-reference the body would name it through the parameter, `d.year`; his example predates that ruling by an hour; not asked. Lane predref's question on it answered by this reading (the manager's, in the brief). No line moves.
- 2026-11-22 (lane predfix82, review r82 RULING-8 (a); record "2026-11-22 MANAGER — review r82 (predfold1122): dispositions ruled; two corrections of record entries (no owner words)"): "written an hour before label-reference was ruled" became "written before label-reference was ruled".

## core/operators/bindings/call-forms — Several bodies for one name
slugs: call-forms
rulings:
rejected:
readings:
- the rule of core/operators/bindings, ruled ("Agree with mapping", record "2026-11-14 RULINGS on rev 3's contradictions": positional, keyword and by-name parameters), has one head per name; it is NOT corrected here. The several bodies are the library's reading: lib/rx/repeat ("The bodies, one per call form", the draft R.1.14; "no maximum" a second body, the draft's reading) and lib/modifiers/padded (the ruled `padded(rx) := /0*${rx}/` and the width form the owner wrote positionally, "someone could use padded(blah, 4) to get a minimum 4", record "2026-11-18 OWNER, on restricting a minimum-width `padded`").
- the record's repeat is ONE construct, "exact with one argument, a range with min and max, no maximum = unbounded" (record "2026-11-17 OWNER — the rx module: one repeat construct; plurals as conveniences"; "an unbounded repeat is written by giving NO MAXIMUM", record "2026-11-17 OWNER RULING — the count proposal"): it rules what a call means, not how many heads define it.
- the parting run: `rx.repeat(rx.digit, 3)` as `(?:\d){3}` and as `(?:\d){3,}` — SUPPORTED (preddoc6 PART CF, `re` on the written-out patterns).
evidence: docs/dev/lanes/preddoc6_evidence/ PART CF.
history:
- 2026-11-19 (lane preddoc6, review r60 COLD-9): a new open sub-piece, at the predicate manager's ruling (r60's FIX-NOW (status) + PLAN (form)): the collision is a question for the owner; the general form (one head, keyword settings, an "unset" bound) is a PLAN item of review r60. The slug call-forms is the lane's name for the question.

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
- (review r83 D11, record-directed: "2026-11-22 OWNER, an observation: the textually-visible rule solves a label from a used binding hiding another binding", his words "The textually visible rules solves a problem of a label from a binding reference hiding another binding") the hide-label warning's trigger restated: since label-reference only labels the definition itself writes can meet a binding's name, so it fires on a label written in the definition against a binding of the same name, and for binding names on a library adding one under `(=) := import(..)` — a reading, the manager's check told to him; UNTESTED (no warnings beyond the A5 case are modelled; OWNUSE runs that one).
evidence:
history:
- 2026-11-19 (lane preddoc3b): new piece, split from core/operators/bindings: the draft §5.1's program shape and statements hold rules no other tag homes, and their status (LEAN) differs from the bindings' (RULED).
- 2026-11-19 (lane preddoc4): `@options` (used by core/diagnostics/warnings' strictness setting) and the `assert` module's statements join the effect list; every call-form built-in has its library piece (review r59 COMPB-3, READ-11; the owner's direction of 2026-11-19, R-1).
- 2026-11-19 (lane preddoc6, review r60 EFFECTS / COLD-1 / COLD-21): the three effects get their library pieces (lib/builtin/warn, lib/builtin/export, lib/builtin/options; the predicate manager ruled them call-form names, 2026-11-19), so "these included" holds; `eval` stays on the list as the draft wrote it (§5.1), now said to be the name reserved for the module that alone provides it (lib/builtin/eval).
- 2026-11-22 (lane predfix82, review r82 FIXIND-9; record "2026-11-22 MANAGER — review r82 (predfold1122): dispositions ruled; two corrections of record entries (no owner words)"): "A binding that mentions a match label is match-dependent (a computed label)" restated with bound-condition. Status date 2026-11-19 to 2026-11-22.
- 2026-11-22 (lane predfix83, review r83 D11; record "2026-11-22 MANAGER — review r83 (preddef1122): dispositions ruled; one correction; idiom-confirm closed on default-export (no owner words)"): the hide-label sentence until then: "an undeclared name that is not a label is a compile error with a suggestion; a binding that hides a label draws a warning, and `$x` still reaches the label." Now it names `pcrec.label.hidden` and its trigger restated (a reading).

## core/modules/map — A module is a map
slugs:
rulings:
- 2026-11-15 "3. this leans into the idea of an interface to a type over the type. Array and map are interfaces that can be applied to regex but interfaces aren't themselves values that can be created. So what import is is less important than that its interface is a map. 4. agree." (record: "2026-11-14 RULINGS on rev 3's contradictions"); under its bold line "2026-11-15 RULINGS — answers to the four questions of review r8"
rejected:
- a module as a third value kind, a namespace (the manager's 2026-11-14 lean (1)) — by owner ruling — the follow-up (MODULE = MAP) and "what import is is less important than that its interface is a map".
- DECLARED TYPES (`type(...)`, `isodate: date`), TYPE MEMBERS declared with a type, SCOPE-LIMITED UFCS (`d.weekday` resolving to a scoped macro), `types()` (and the record's `kind()`) in the first spec — by owner ruling — the §9 cut (predx Q8, the draft §9 STATUS "RULED (CF:583, predx Q8)"); declared types may return as library packaging after a build.
readings:
- members travel WITH THE TYPE (record "2026-11-14 — namespaces for type members", a LEAN) — UNTESTED; not contradicted by the 2026-11-19 rulings (they bind names into the bare space; dot lookup into a type is untouched).
- a module is never passed, stored, returned or used whole as a pattern (the draft §7's phase-1 lean) — UNTESTED.
evidence:
history:
- 2026-11-14: import/export as functions, its follow-up (module = map); 2026-11-15: the interface ruled; the draft §7 MODULES.
- 2026-11-19 (lane preddoc4): the base bullet "Members of a TYPE travel with the type" removed (a lean inside a ruled piece, and "type" against the one-type ruling; types, interfaces and members were cut from the first spec, Q8 of the 2026-11-14 predx entry); it stays a reading above (review r59 READ-12).
- 2026-11-22 (lane predfix83, review r83 D9; record "2026-11-22 MANAGER — review r83 (preddef1122): dispositions ruled; one correction; idiom-confirm closed on default-export (no owner words)"): the bullet until then: "Only what `.` reaches is reachable from outside: the public names, decided by the `_` rule (core/labels/export);" ("public" read as "reachable from outside", the old sense). Now: the names the thing exports, by the `_` rule and default-export.

## core/modules/binding-list — The named binding list
slugs: import-symbols
rulings:
- 2026-11-19 "import-symbols: agree with all your statements including macro call. further, special form (=) := ... imports all symbols" (record: "2026-11-19 OWNER RULING — import-symbols: the named binding list, the shorthand in a macro call, `(=) :=` for all symbols")
- 2026-11-19 "it might also be (=left, =right) := ... which looks odd but is a degenerate form of macro parameter binding" (record: "2026-11-19 OWNER, discussing import-symbols: the double name, the binding form, `(=left, =right)`"); the idea he then ruled
rejected:
- `(left,right) := import("blah", /left|right/)` (his first instinct) — by owner ruling — "double name is a weakness".
- `(left, right) := import("blah")`, selection by bare name (the manager's leaning) — by owner ruling — import-symbols adopted the `=`-marked form (record: "2026-11-19 OWNER RULING — import-symbols: the named binding list, the shorthand in a macro call, `(=) :=` for all symbols"); the reason is his CAUTION in the discussion before it, "it has implications for the rest of the language" (record "2026-11-19 OWNER, discussing import-symbols: the double name, the binding form, `(=left, =right)`", class DISCUSSION, not a ruling); bare `(a, b)` stays for a positional form (core/modules/positional).
readings:
- the eight statements he agreed to are the manager's list, "no wider" — SUPPORTED by the record entry; statement 7 ("A bare positional `(a, b) := X` is left undefined for now") does not stand as told: the manager WITHDREW it (record "2026-11-19 MANAGER — a statement told to the owner under import-symbols is WITHDRAWN (the positional binding list)") and that withdrawal was itself CORRECTED to "the positional list `(a, b) := X` is OPEN under tuple-parts, for a tuple and for a map alike" (record "2026-11-19 MANAGER — the withdrawal above is itself CORRECTED: taking a tuple apart is OPEN (tuple-parts), not confirmed; and a slip in the padded body"); the positional list is core/modules/positional.
evidence:
history:
- 2026-11-19: his aside after the pilot, the discussion, his lean "don't confirm yet", the manager's implications (a)-(f), the ruling.
- 2026-11-22 (lane preddef, export-list folded; record "2026-11-22 OWNER RULING — export-list: yes"): two bullets: one form with two targets, two name spaces (the manager's reading (a), his direction); his caveat "Agree caveat bindings used to scope labels (A.a: 8)" with the manager's wording, a reading; the caveat is class AGREEMENT (record "2026-11-22 OWNER, on the two name spaces: "Agree caveat bindings used to scope labels (A.a: 8)""), noted by review r83 D6.
- 2026-11-22 (lane predfix83, review r83 D6, D9, D14; record "2026-11-22 MANAGER — review r83 (preddef1122): dispositions ruled; one correction; idiom-confirm closed on default-export (no owner words)"): the bullet until then: "Only what `.` reaches can be bound (public names)." (D9). The one-form bullet until then ended "Bindings and labels are two name spaces; the hide-label warning is where they meet." (the last clause not in the sentence he agreed to, and contradicted by the caveat bullet: D6); now marked the manager's addition. The caveat bullet until then: "His caveat, "Agree caveat bindings used to scope labels (A.a: 8)": left of `:` a path's LAST step is a label; its earlier steps are sources, each a binding's name, a macro's name or a part label; a bare single name there is a label the definition itself writes (a reading)." Now a pointer to its home, core/conditions/form (D14), and to core/modules/names.

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
- with `(=)` a reader cannot tell from the file alone whether a bare name is a label or an import (the manager's, "Told to him as the cost of the form, not an objection") — UNTESTED (no matching involved).
evidence:
history:
- 2026-11-19: the ruling's addition, then the addition on `=` first.
- 2026-11-19 (lane preddoc6, review r60 RULING-8a): the base bullet on a reader not telling a label from an import marked a reading; the record has it among "The manager's readings of the addition, FOR A LANE TO CHECK", "Told to him as the cost of the form, not an objection".

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
- 2026-11-19 (lane preddoc6, review r60 COLD-11): the bullet that examples call provided names bare, as if imported, added: built mechanically most examples otherwise call a `module: ?` name with no import line; the bullet decides nothing of default-imports.

## core/modules/default-set/members — Which names are in the default set
slugs: default-imports
rulings:
rejected:
readings:
- `peek` only, today, by his words (the doc-shape entry's item 2) — the rest NOT STATED.
evidence:
history:
- 2026-11-19: queued by the manager as **default-set**, not asked (the doc-shape entry).
- 2026-11-19 (lane preddoc5): the slug renamed `default-imports` in the documents: the word `default-set` already names the RULED 2026-11-16 question on a label default of several strings (core/conditions/defaults); the record entry of 2026-11-19 keeps its word (review r59 COMPA-12).

## core/modules/positional — A positional binding
was: parked/ideas/tuple-apart (2026-11-19, merged: the parked piece and this open piece were one question with two statuses in two base files; review r60 TUPLE-APART, FIXVER-1)
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
- 2026-11-19 (lane preddoc6, review r60 POSITIONAL-MAP / RULING-1): the question restated as the record's correction states it ("WHAT STANDS NOW: the positional list `(a, b) := X` is OPEN under tuple-parts, for a tuple and for a map alike; statement 7 of import-symbols ("left undefined for now") was nearer the record than its withdrawal, though its stated reason (no ordered right side) remains wrong: tuples exist", record "2026-11-19 MANAGER — the withdrawal above is itself CORRECTED: taking a tuple apart is OPEN (tuple-parts), not confirmed; and a slip in the padded body"). The piece before said "a positional list against a MAP, which has no order, is not stated", the WITHDRAWN entry's wording.
- 2026-11-19 (lane preddoc6, review r60 TUPLE-APART): parked/ideas/tuple-apart retired into this piece (the `was:` line above); its trigger is the base's "Asked again when" line. Its details entry, whole:
  - rulings: 2026-11-16 (class: OWNER, reopening) the reopening quoted above; "nothing ruled on the parked item".
  - the ideas file (`docs/design/predicates_future.md`) item 4, "Taking one tuple apart in a binding", whole:
    WHAT: `(lo_h, lo_m) := lo` for ONE tuple (a set of several tuples is never taken apart: the parts no longer
    pair up; the owner's "9:30, 10:00 broken apart is 9,10 and 30, 00 which is gibberish"). STATUS: OPEN, with no
    user while item 1 is parked (the manager's note, 2026-11-16; not an owner ruling). WORKED OUT IN:
    joint_condition.md §4A.3 (both positions; the lean "one tuple only"). TRIGGER: item 1 taken up, or an example
    that needs one part of a tuple value.
  - 2026-11-19 (lane preddoc3c): its trigger and source written into the base piece; the item's text copied there.

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
- 2026-11-19 (lane preddoc6, review r60 EFFECTS): the call-form name `@export(names)` and its examples moved to lib/builtin/export (`open export-choice`: "Export choice PENDING Frank"); this piece keeps the meaning. Its statement before: "A library file exports with `@export(names)`: every binding whose name is in the rx `names`; a file that exports nothing is a compile error."

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
- 2026-11-19 (lane preddoc6, review r60 COLD-13): the blessed callout said to be compiler-emitted, never a callout written in rx text (core/patterns/literals refuses those inside a larger program).

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

## core/modules/names — The kinds of name
slugs:
rulings:
- 2026-11-22 (class: AGREEMENT) "I agree with your interpretation. I note that captures can have no label." (record: "2026-11-22 OWNER, on the two-kind view: "I agree with your interpretation. I note that captures can have no label.""); agreed framing for the name table, not a ruling; the note read as the four-cell table
- 2026-11-22 (class: ACKNOWLEDGEMENT) "Nothing missed I see. but I do wonder if some of these can be defined. Maybe, same thing from a different perspective. A capture group name produces a label of the same name? A macro arg, typed arg, label arg, are all variations on the same thing. Thoughts?" (record: "2026-11-22 OWNER, on the kinds of reference: "Nothing missed I see"; can some be COMBINED: a capture group name produces a label; macro arg, typed arg, label arg as variations of one thing"); his next message corrects one word: "defined" read as "combined"
- 2026-11-22 (class: QUESTION) "So the types of reference are: binding, label, macro argument, capture group name, ?" (record: "2026-11-22 OWNER, a question: the kinds of reference ("binding, label, macro argument, capture group name, ?")"); the list the table completes
- 2026-11-22 (class: AGREEMENT) "Agree caveat bindings used to scope labels (A.a: 8)" (record: "2026-11-22 OWNER, on the two name spaces: "Agree caveat bindings used to scope labels (A.a: 8)""); the position rule in a path
rejected:
readings:
- the two base kinds, label (match time) and binding (compile time), with properties, and `.` the one operator — the manager's view told to him, agreed (above); every row cites its piece and states nothing new — UNTESTED as a whole (a table; its rows' rules are run in their pieces; the grid of docs/dev/lanes/predfix83_evidence/ predfix83_model.py GRID runs the label spellings and the binding sources against the reads).
- "has a label" and "is a capture" independent (the four cells) — the manager's reading of his note; the cell "has no label, is a capture" is an unnamed group where a number is refused (core/labels/numbers) — UNTESTED (captures are not modelled).
- the one operator is core/modules/map's ruled sentence, quoted, "`.` has one meaning: a field of the map interface of the thing on its left" — stated there, not here.
- not merged: label with binding; a label's value with its capture's value — the manager's view, agreed.
evidence: docs/dev/lanes/predfix83_evidence/ predfix83_model.py GRID; docs/dev/lanes/predspot_evidence/ predspot_model.py SWEEP (lane predspot).
history:
- 2026-11-22 (lane predfix83, review r83 (the brief's NAME TABLE piece, review r82's name table); record "2026-11-22 MANAGER — review r83 (preddef1122): dispositions ruled; one correction; idiom-confirm closed on default-export (no owner words)"): a new piece, status `reading`: the table of name kinds, the four-cell table, the one operator and the position rule, what is not merged, his agreement quoted.
- 2026-11-22 (lane predspot, argument-default folded; record "2026-11-22 OWNER RULING — argument-default: an error; and his reason: a label is to the SPOT in the pattern, a parameter is a template, not a piece of the pattern"): a binding row added: an argument at a call, a template, never labelled.
- 2026-11-22 (lane predspot, program-options folded; record "2026-11-22 OWNER RULING — program-options: yes; and a PROPOSAL: `i` keeps inheriting, with a "weak" value the program sets"): the "capture only" cell gains "(none under `n`)", the "neither" cell "a plain `( )` under `n`" (the lane's reading, at the brief; its letter "(f)" dropped by review r84 C7).

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
- 2026-11-19 (lane preddoc6, review r60 COLD-5): the index said every error below is ruled in its piece and read as complete; at least 12 stated compile errors have no row. It now says it is PARTIAL; a generated index (r59 PLACE-8) is a PLAN item of review r60.
- 2026-11-22 (lane predfix77, review r77 D12 (FIXIND-17); record "2026-11-22 MANAGER — review r77 (predfold1121): dispositions ruled (no owner words)"): two rows added, a joint entry inside a group question (array-vs-passes) and a piece naming a label it does not hold (nested-scope case 1).
2026-11-22 (lane predbound): two rows added, a condition or computed value bound alone naming a label its binding does not hold (bound-condition, ruled) and a value of several strings left of `:` (a reading, count-in-set).
2026-11-22 (lane predbound, R-1): a row added, a plain read through a binding's prefix with the binding used more than once (binding-prefix, ruled).
- 2026-11-22 (lane predcall, R-1 of its rulings file, closed-argument ruled (a)): a row for the closed argument's `A.d` (core/labels/paths/closed-argument). The status stays a reading, its date 2026-11-19.
- 2026-11-22 (lane predfix82, review r82 EXAMPLES-2; record "2026-11-22 MANAGER — review r82 (predfold1122): dispositions ruled; two corrections of record entries (no owner words)"): rows added or widened: label-reference's bare read, a path not visible through its source, the value-left gaps, a value entry in a group question, a set bound alone, the binding-prefix row to macro names and the `&` index. Status date 2026-11-19 to 2026-11-22.
- 2026-11-22 (lane preddef, default-export folded; record "2026-11-22 OWNER RULING — default-export: protected"): a row: a read from outside of a label only a part used alone holds (core/labels/export).
- 2026-11-22 (lane predfix83, review r83 D12, A1, A2, A7; record "2026-11-22 MANAGER — review r83 (preddef1122): dispositions ruled; one correction; idiom-confirm closed on default-export (no owner words)"): the row "a read from outside of a label only a part used alone holds (`p2.h`, p2 := `/${A}!/`; `B.a`, B := `A & A`)" gains a `_` part label and `[_ = A]` (`p6.h`) (D12). New rows: the `&` ambiguity in its shapes (A1, A7; "an ambiguous reference across `&`" removed from the partial list, now a row); an export list naming a label the part does not export, the cross case (A2, D12, D16).
- 2026-11-22 (lane predspot, argument-default folded; record "2026-11-22 OWNER RULING — argument-default: an error; and his reason: a label is to the SPOT in the pattern, a parameter is a template, not a piece of the pattern"): a row added: the caller's read of an argument's label where the body uses the argument alone; a part label written on an argument.

## core/diagnostics/under-construction — The under-construction error
slugs: under-construction-class
rulings:
rejected:
readings:
- the error keeps its own class, worded as under construction (THE MANAGER'S CALL, answer-free, told to him, "closed unless he objects") — UNTESTED (wording).
evidence:
history: skeleton; record "2026-11-18 OWNER RULING — construction-line: enumerate" (the call).

## core/diagnostics/warnings — Warnings
slugs: warn-in-macro-body anchor-warn-scope default-unused
rulings:
- 2026-11-14 "I agree but warnings need names and the user must be able to disable them (wildcard?)" (record: "2026-11-14 RULING — the empty-match hazard")
- 2026-11-14 "use an rx instead of wild card purely for consistency" (record: "2026-11-14 RULING — the empty-match hazard"); its amendment: a selector is a set of names as an rx
- 2026-11-17 "What are all the warning items? Warnings should be structural or definable by a library option." (record: "2026-11-17 OWNER — a principle for warnings")
- 2026-11-17 "Warnings: yes, that is my definition of structural and these warnings are good. Naming: library warnings/errors should be id'd by the library path" (record: "2026-11-17 OWNER RULING — warnings: the list accepted; library warnings are named by the library path")
- 2026-11-17 "2. compiler errors and warnings are prefixed with "pcrec."" (record: "2026-11-17 OWNER RULING — warnings: the list accepted; library warnings are named by the library path"); the ADDENDUM
- 2026-11-17 "polarity-rule: warning for both. Warnings are errors given some strictness setting eg @config.strict()" (record: "2026-11-17 OWNER RULING — polarity-rule")
- 2026-11-17 "empty-search-error: warning" (record: "2026-11-17 OWNER RULING — empty-search-error: a warning")
- 2026-11-17 "Agree. Good warning" (record: "2026-11-17 OWNER — the numbered-label warning accepted")
- 2026-11-15 "&: both sides filter and warn if anchor. Agree but test if it makes sense." (record: "2026-11-15 CORRECTION and RULING"); part (b): the anchor warning `pcrec.anchor.whole` on an explicit anchor in an `&` operand
- 2026-11-15 "anchor-warn-scope: agree" (record: "2026-11-15 RULINGS — no anchored-specific error in a hole; the anchor warning covers every whole-match place"); ONE warning in every place a pattern must match its stretch whole
- 2026-11-15 "But! padded is a simple macro so the warning shouldn't key off of the name" (record: "2026-11-15 RULING — the anchor warning keys off the ROLE, never a transform's name"); the warning is decided by the ROLE the rx ends up in after macros are expanded
- 2026-11-15 "warn-in-macro-body: yes but is that an identity? The anchored and & are not the same" (record: "2026-11-15 RULING — the anchor warning has no exemption for macro-body text"); no exemption by authorship, the criterion applied to the expanded text; his question is the manager's to answer, not a ruling
- 2026-11-16 "default-unused: agree" (record: "2026-11-16 OWNER RULINGS — unset-component: yes; default-unused: agree"); the manager's reading of "agree", told to him: the lean, so a never-used default is a WARNING (`pcrec.default.unused`), not an error
- 2026-11-19 "flags-warning: yes when it works. You can't do it if the expression refers to $x a label in the literal" (record: "2026-11-19 OWNER RULING — flags-warning: yes, when it works; not when the expression reads a label of the literal")
rejected:
- a `*` wildcard in a selector — by owner ruling — the amendment: `"*"` is the literal name and draws `warn.unused`.
- `compare.width` as a compiler warning — by owner ruling — the list accepted: it is about one library form, so the compare library names it (`compare.width.variable_width`).
- a looped-label warning of its own (the manager's proposal) — by the manager, recorded in the principle's entry: it is `label.unset` under the one label rule; the two triggers are not the same set (the draft R.2, rev 25's PART W).
- `transform.noop` (the 2026-11-14 list) — by the draft (§7.1, after OWN-1 made a transform a macro on its filter): a transform without its argument is the unapplied-macro error (core/operators/bindings).
- a "modifier argument" clause or a library name in the anchor warning's rule (`padded(/^5/)` on the manager's list) — by owner ruling — the warning keys off the ROLE ("padded is a simple macro so the warning shouldn't key off of the name").
- an exemption for anchors written inside a macro's own body — by owner ruling — warn-in-macro-body.
- a never-used default as a compile error — by owner ruling — default-unused (a warning).
- warning names without a prefix (`empty.search`, `label.unset`, the 2026-11-14 list) — by owner ruling — the ADDENDUM ("compiler errors and warnings are prefixed with "pcrec."", cited above).
readings:
- every name is the manager's placeholder (the draft §7.1; his `no-fail` an example) — SUPPORTED by the record ("the names ... to the spellings review").
- `match.never` (an inserted pattern's edge that can never hold; a product with every copy removed) and the `[^${c}]` -> join warning are the draft's, not in the accepted list — UNTESTED.
- the arithmetic warning's one trigger (a result known to be nothing, a member list only when every member's is) is the manager's call — UNTESTED.
- the binding-hides-label warning is the owner's 2026-11-13 "Warn (or error) on hiding label", read as a warning — UNTESTED.
- his observation that a selector can catch a compiler warning and a library's of the same last component ("helpful or dangerous") is NOT ruled.
evidence:
history:
- 2026-11-19: the row `pcrec.flags.filter` added (flags-warning; the name the manager's placeholder).
- 2026-11-14: names in dotted families, `@warn.off`; 2026-11-17: the principle, the list, the library path, the `pcrec.` prefix, polarity-rule, empty-search-error, numbered-label; 2026-11-19: dollar-diagnostic, plus-operands.
- 2026-11-19 (lane preddoc3b): converted from `?`; three controls of one fact (`@warn.off`, `@warn.error`, `@options.strict`) stay an idea (parked/ideas/severity-table).
- 2026-11-19 (lane preddoc6, review r60 EFFECTS): the call-form names `@warn.off`/`@warn.error` and `@options.strict` have their library pieces (lib/builtin/warn, lib/builtin/options); this piece keeps the meaning (names, selectors, the table).
- 2026-11-19 (lane preddoc6, review r60 COLD-14): (a) core/labels/one-rule's "A label no match can set draws a warning" pointed at no row: by polarity-rule it is the test that can never pass, so the `pcrec.test.never` row names it and the one-rule bullet says so (no new warning); (b) the five nameless rows given placeholder names like the rest (`pcrec.label.hidden`, `pcrec.arith.nothing`, `pcrec.hit.nullable`, `pcrec.test.consumes`, `pcrec.class.join`: the manager's placeholders, to the spellings review); (c) the selector bullet writes `pcrec.warn.unused`, as the table does.
- 2026-11-22 (lane predfix77, review r77 D11; record "2026-11-22 MANAGER — review r77 (predfold1121): dispositions ruled (no owner words)"): the `pcrec.flags.filter` row cites core/holes/flags/in-filter for its trigger (one owner per fact); its own trigger text is in that entry's history.
- 2026-11-22 (lane predfix83, review r83 D11; record "2026-11-22 MANAGER — review r83 (preddef1122): dispositions ruled; one correction; idiom-confirm closed on default-export (no owner words)"): the row `pcrec.label.hidden` until then: "a binding that hides a label". Now its trigger restated as core/operators/statements reads it (a reading).
- 2026-11-22 (lane predspot, hole-flags folded; record "2026-11-22 OWNER RULING — hole-flags: yes to all (weak values do not propagate; only an explicit `i` is inherited at a hole; `m` and `s` are no longer inherited)"): ruled 2026-11-17 re-dated 2026-11-22: the `pcrec.flags.filter` row's "an `&` or a complement in a hole that inherits a flag" to "... that inherits an explicit `i` (the one flag a hole passes on)".
- 2026-11-23 (lane predfix84, review r84 A8; record "2026-11-23 MANAGER — review r84 (predspot1122): the dispositions, ruled with the 2026-11-23 rulings in hand; no owner words"): the `pcrec.flags.filter` row's "inherits an explicit `i` (the one flag a hole passes on)" to "inherits an explicit `i` or `-i`": the trigger fires under an inherited `-i` by the same comparison (a reading, core/holes/flags/in-filter).

## core/diagnostics/dollar-form — The `$x & S` warning
slugs: dollar-warning dollar-diagnostic
rulings:
- 2026-11-19 "i don't want to spend too much time on the warning. the form $x & .. should just get a warning" (record: "2026-11-19 OWNER RULING — dollar-diagnostic")
rejected:
- the form an ERROR (dollar-condition, 2026-11-17) — by owner ruling — match-is-rx made it legal; dollar-diagnostic gave it a warning.
- no dedicated warning, the emptiness diagnostics with "a read stands for its group's rx" (the manager's, rev 28) — by owner ruling — dollar-diagnostic ("should just get a warning").
- rev 29's lexical trigger for the `$x & S` warning and its place-blind hint — by the manager's calls (review r54 P29-11, P29-12): the form is defined on the PARSE, the hint only at an `&` operand (the draft R.9, §R.2).
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

## core/diagnostics/looped-compare — Labels that can repeat draw no warning
slugs: looped-compare looped-warning
was: core/diagnostics/looped-compare/still-wanted (2026-11-19, merged: the question is answered here)
rulings:
- 2026-11-19 "looped-warning: I agree remove warning." (record: "2026-11-19 OWNER RULING — looped-warning: remove the warning"); it reverses the two rulings below
- 2026-11-16 "looped-compare: warn" (record: "2026-11-16 RULING — a compare over looped labels warns"); reversed by looped-warning (above); it had the compiler warn when a compared field can hold more than one occurrence
- 2026-11-16 "I agree. Makes sense." (record: "2026-11-16 OWNER RULING — joint-loops: agreed, all three parts"); part (3): "the looped warning's subject is now a `|` of conditions whose labels can repeat (each alternative is checked over every pass; the message names the joint condition as the per-item form); the joint condition itself draws no such warning"; it moved the 00:09 warning onto a hand `|` of conditions; part (3) reversed by looped-warning (above)
rejected:
- the warning on a hand-written `|` of conditions whose labels can repeat (`pcrec.compare.looped`; candidate (a)) — by owner ruling — looped-warning: its ground (each alternative checked over every pass) went with after-loop-read.
- a warning on any bare condition reading a label set inside a loop (candidate (b); the manager's 2026-11-17 proposal) — by owner ruling — looped-warning.
- the warning on a compare over the looped fields themselves (the 00:09 shape) — by owner ruling — joint-loops (3) moved its subject onto a hand-written `|` of conditions; the joint condition draws none.
readings:
- the name `compare.looped` (the draft §7.1, its name LEAN), read with the compiler's `pcrec.` prefix (the ADDENDUM of "2026-11-17 OWNER RULING — warnings: the list accepted; library warnings are named by the library path") — the manager's; the draft notes it looks like a compare-library path (review r43 E; the spellings review).
- "`compare.looped` and the manager's withdrawn looped-warning go to the next review as told" (record "2026-11-17 OWNER RULING — warnings: the list accepted; library warnings are named by the library path", in the manager's MINE paragraph) and the draft's "[REV 25.1] WITHDRAWN to the next review with looped-warning" (§7.1, §R.2) — the MANAGER's words: a manager's withdrawal does not undo an owner ruling; the owner's own looped-warning ruling then removed the warning (above).
evidence: the draft §8 caveat (6) and §7.1's rows (`9:30,10:00,` rejected by the per-label meaning; the warning's text LEAN).
history:
- 2026-11-16 00:09: looped-compare asked (keep, error or warn; lean warn), ruled "warn" (the draft rev 19, rulings R-2: `compare.looped`). 11:17: joint-loops (3) moved the warning onto a hand `|` of conditions.
- 2026-11-17: after-loop-read made a bare condition read the last pass's own label; the manager sorted its OWN looped-warning proposal as `label.unset` and sent it and `compare.looped` "to the next review as told"; the draft rev 25 marked `compare.looped` WITHDRAWN with it (a manager's act on an owner-ruled warning).
- 2026-11-19 (lane preddoc6, review r60 LOOPED / RECOUNT-1 / RECOUNT-7): a new piece. The documents before said only "withdrawn by the manager" (core/conditions/pass-start-read) and cited neither ruling as a `rulings:` item; lane preddoc5's claim table row for this entry ("SUPERSEDED by joint-loops (3), then after-loop-read (2323 ...)") was WRONG: record line 2323 is "2026-11-17 OWNER RULING — last-pass-default: regex", and neither entry supersedes the warning. The slug looped-compare moved here from core/conditions/pass-start-read.
- 2026-11-19: the statement until the ruling: "A hand-written `|` of conditions whose labels can repeat draws a warning naming the joint condition as the per-item form; a joint condition itself draws none." The warnings table's row `pcrec.compare.looped` left with it.
- 2026-11-19 (lane predfix61, review r61 F-I, RULING-1, STALE-1): live glosses of the reversed rule, verbatim until then: rulings item 2 "; the meaning stays, the compiler warns when a compared field can hold more than one occurrence, naming the fix (the compare inside the loop's item)"; rulings item 3 ". The owner's LAST word on the warning; it MOVES the 00:09 warning, it does not retire it"; readings item 2 "so the warning stands as joint-loops (3) left it; whether it is still wanted is core/diagnostics/looped-compare/still-wanted (the predicate manager's ruling of 2026-11-19, lane preddoc6)." F-J (RUNOWN-5): the joint-form equality qualified "where both are set" (100 of 100 pairs, predfix61 FJJ; with m unset the two part, 6 of 240 in review r61's count).
- from the merged question piece (its readings and history, kept verbatim):
  - the manager's proposal, a compile WARNING on a bare condition over a looped label: "MINE, not ruled: a compile WARNING when a bare condition reads a looped label (proposed to him twice, not answered ...)" (record "2026-11-17 OWNER RULING — last-pass-default: regex"); "the manager's compile-error lean is withdrawn; a compile WARNING on a bare condition over a looped label remains the manager's proposal" (record "2026-11-17 OWNER RULING — after-loop-read: the last pass's own label") — the MANAGER's words.
  - the manager's withdrawal: "the manager's looped-warning proposal is not a new warning but the existing `label.unset` (a condition reads a label that can be unset where it is read, with no default) seen under the one label rule" (record "2026-11-17 OWNER — a principle for warnings") and "`compare.looped` and the manager's withdrawn looped-warning go to the next review as told" (record "2026-11-17 OWNER RULING — warnings: the list accepted; library warnings are named by the library path") — the MANAGER's words, quoted as the manager's; they withdraw the manager's own proposal and cannot retire the owner-ruled warning (core/diagnostics/looped-compare).
  - the two triggers are not the same set (the draft §R.2, rev 25's PART W, five programs `& (h: <5)`): `/(?:(?<h>\d);)*/` both fire; `/(?:(?<h>\d);)+/` the looped trigger only; `/(?:(?<h>\d)?;)+/` both; `/(?<h>\d)?;/` `label.unset` only; `/(?<h>\d);/` neither — SUPPORTED by the draft's run (the base quotes two of the rows).
  - 2026-11-17: proposed by the manager twice, not answered; review r42 named looped-warning an owner question; rev 25 withdrew it to the next review.
  - 2026-11-19 (lane preddoc6, review r60 LOOPED): a new open sub-piece, at the predicate manager's ruling (2026-11-19): the question "is the warning still wanted, and on which shape" goes to the owner; the slug looped-warning moved here from core/conditions/pass-start-read.
- 2026-11-21 (lane predarr, joint-in-some): the joint-form bullet gains "Inside a group question a joint entry is a compile error for now" (a pointer; this piece's ruling is untouched).
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
- 2026-11-19 (lane preddoc6, review r60 FIXVER-5): the STRING FUNCTIONS row routes each name to its library piece (it named core/values/functions for `left`, `strlen`, `upperStart`, `prefix_in`); the EFFECTS rows name lib/builtin/warn, lib/builtin/options, lib/builtin/export (review r60 EFFECTS).
- 2026-11-19 (lane preddoc6, review r60 DIGIT / COLD-3 / FIXVER-9): a bare `digit` (the owner's own spelling, "like /${(0: digit)}/") written `rx.digit`, the form lib/rx/classes defines; built mechanically the bare name was an undeclared name, a compile error (core/operators/statements). Answers unchanged (preddoc6 PART DG).
- 2026-11-19 (lane predfix61, review r61 F-L, RULING-9): a row for the sort and its shorthand for longest first (`longest_first(X)`, the manager's placeholder; his `lengthSorted()`). Status date 2026-11-17 to 2026-11-19.
- 2026-11-21 (lane predscope): rows added or widened for his placeholders of 2026-11-21: `.` as the sequence operator and `[=year]` (record: "2026-11-21 OWNER, discussing bare-nested-scope: an EXERCISE asked for (construct moderately difficult rx from macros), with his predictions"); the capture forms, a wrapper and after the fact, "no spelling suggested" (pure-label).
- 2026-11-21 (lane predarr, array-vs-passes ruled): the ARRAY FORM row's "its index `h[k]` and the pass index `(h[2]: ..)`" became "its index `h[k]`, the k-th setting (`(h[2]: ..)`)".
- 2026-11-22 (lane preddef, export-list folded; record "2026-11-22 OWNER RULING — export-list: yes"): a row: the export list on a part label.
- 2026-11-22 (lane predspot, program-options folded; record "2026-11-22 OWNER RULING — program-options: yes; and a PROPOSAL: `i` keeps inheriting, with a "weak" value the program sets"): ruled 2026-11-19 re-dated 2026-11-22: a row added, the program options statement `@options(..)`.

## core/spellings/condition-parentheses — A condition keeps its parentheses
slugs:
rulings:
rejected:
readings:
- the condition keeps its parentheses everywhere, in a hole too; `A & 0: digit` and `${0: digit}` stay the draft's error with their meaning acknowledged (THE MANAGER'S CALL, record "2026-11-19 OWNER, on a condition without its parentheses") — UNTESTED (a spelling).
evidence:
history: skeleton; his remarks "i believe that ${} implies (?:${})", "parenthesis are better because you can't add more to the chain", "maybe thats the same." (an OBSERVATION; the `0` case run: preddoc1 PART R12).
- 2026-11-19 (lane preddoc6, review r60 DIGIT / COLD-3 / FIXVER-9): a bare `digit` (the owner's own spelling, "like /${(0: digit)}/") written `rx.digit`, the form lib/rx/classes defines; built mechanically the bare name was an undeclared name, a compile error (core/operators/statements). Answers unchanged (preddoc6 PART DG).
