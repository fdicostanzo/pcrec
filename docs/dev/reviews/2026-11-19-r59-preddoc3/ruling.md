# Critic ruling findings (round r59 preddoc3)

## Findings


### RULING-1  CONFIRMED   severity: design   effort: S
where: core.md + core_details.md [core/principles/stated-behaviour] (record 4492 padded-order, 5134 padded-lazy-sparse); sibling lib/modifiers/padded
what: a `ruled` PRINCIPLE promoted from two slug answers about ONE macro. The statement "A macro body's documented behaviour on an odd argument is accepted, not made an error" is the manager's generalisation; the owner ruled only padded-lazy-sparse ("stated behavior", the slug candidate's own name) and agreed to the padded-order lean. Neither ruling states a rule over macros in general. The second rulings item is not his words: `padded-order "i agree with your lean", the lean naming "the body's stated behaviour, not an error"`; the second quoted phrase is in the MANAGER's paragraph of record 4492 ("that difference is the body's stated behaviour, not an error"). SIBLING-OF-A-FAMILY: lib/modifiers/padded cites the same two rulings (R11, R12) and carries `by: core/principles/stated-behaviour`, so the piece is "decided by" a principle made out of its own rulings (circular).
evidence: record 4492-4503: His words, verbatim: "i agree with your lean" / the manager's paragraph "...that difference is the body's stated behaviour, not an error". Record 5148: "(1) RULING (a slug answer to padded-lazy-sparse): STATED BEHAVIOUR: the padded-order ruling stands as it is; on a lazy or shortest-first argument ...". The details history concedes "the phrase was the manager's (padded-order's lean)". quotes.py: the item is DRIFT (the quote is not contained in the cited entry as one string).
proposed fix: demote to `reading` (a candidate principle, his to confirm), or fold into lib/modifiers/padded as "padded's stated behaviour" and drop the `by:`. Drop the manager-text half of the second item (keep `"i agree with your lean"` alone).

### RULING-2  CONFIRMED   severity: doc   effort: S
where: core.md + core_details.md [core/principles/exact-wording] (record 4955 zero-in-sequence)
what: a `principle` piece made of a remark on the MANAGER'S METHOD, which the record classes as a remark with "no change asked", not a principle, direction or standing instruction. Its statement "On the manager's method: rules are stated exactly" says nothing about the language, yet it sits in core.md, which a session reads to "know the current language". It also splits one sentence of his zero-in-sequence answer across two principle pieces (the other half is core/principles/composed-at-point).
evidence: record 4961-4963: "Also a remark on the manager's method ("a lawyer in your exact wording. this is what is needed now"): exact wording is wanted; no change asked." Item: `(class: a remark on the manager's method)`; doc_format's `principle` = "a principle, a direction, a standing instruction".
proposed fix: drop the piece (keep the remark in composed-at-point's details history), or move it to the manager's process material (skill / wake), not the language base.

### RULING-3  CONFIRMED   severity: doc   effort: S
where: core_details.md [core/labels/export/caller-ambiguous] (record 3458-3469 "third exchange", 3476-3491 export-rule)
what: the open piece keeps five candidates alive although the owner AGREED to export-rule statement 5 ("The caller's captures are what is visible from the top-level program by these rules"), and the record's export-rule title says the ruling "closes the export-scope discussion and path-and-ambiguity" (the read-out corner = this slug's question). By statement 5 plus label-flow ("it is an error to ambigously reference a label"), candidates (b) absent, (c) last mention and (d) left side are out; only (a) compile error vs (e) error when read remains. The details reading says "pending a ruling (the manager's reading of "The caller's captures: agree")" - the record says the ruling came the same morning. The slug `caller-ambiguous` appears nowhere in the record (the record's names: read-out, filter-captures).
evidence: record 3465: HIS WORDS "...The caller's captures: agree". Record 3468-3470: "That settles the read-out corner of path-and-ambiguity in substance (a name two parts both make public is an ambiguous reference for the caller as for the program), pending the one ruling that closes the discussion." Record 3477: "export-rule ... (closes the export-scope discussion and path-and-ambiguity)", statement 5 in the ruled list. `grep -n caller-ambiguous COND-FAMILY.md` -> 0 lines.
proposed fix: cite the export-rule ruling (statement 5) on the piece; move (b)-(d) to `rejected: ... by owner ruling — export-rule statement 5`; narrow the open question to "an ambiguous caller read: a compile error, or an error when read?"; name the record's slug (read-out) in `slugs:`.

### RULING-4  CONFIRMED   severity: doc   effort: S
where: core_details.md [core/modules/import] line 1313 (record 630)
what: a rulings item whose quote is the MANAGER's wording, by its own admission ("the manager's wording of his words"). The record line is "Addendum (Frank): `import(...)`'s argument is a set of names (...)", a third-person paraphrase of the 2026-11-14 era, not his verbatim words; the item is in quotation marks as if his.
evidence: quotes.py: LOOSE (matches only with backticks stripped). Record 630: "Addendum (Frank): `import(...)`'s argument is a set of names (an rx over file names, consistent with export); it must resolve to EXACTLY ONE file". The piece is still `ruled` through R1312 (import-several, verbatim).
proposed fix: drop the item or move it to `readings:`/history ("the 2026-11-14 addendum, as the record paraphrased it; its 'exactly one file' half reversed by import-several").

### RULING-5  CONFIRMED   severity: doc   effort: S
where: core_details.md rulings items without the owner's words: [core/principles/no-absence] line 53 ("the absent-rule LOCKED on this principle", no quote at all); [core/holes/and-in-hole] line 1219 (`"That's a good clarification" (the sides of `&` "match the same stretch whole")`, the second quotation the manager's question text); [core/holes/labels] line 1142 (`"Inserting through a hole." "Agree"`: the first is the manager's question heading he repeated, the entry classed DISCUSSION, "nothing ruled by this entry")
what: format says each item is "<his words, verbatim>". These three carry no words of his, or wrap manager text in quotation marks beside his. holes/labels is `ruled` on export-rule (not about holes) plus this DISCUSSION agreement with a manager's lean; it is better supported than a lean but the record never asked "holes" as a ruling.
evidence: quotes.py NOQUOTE x2, DRIFT x1. Record 3438-3439: "(DISCUSSION, nothing ruled by this entry)"; 3451-3452: "(d) Inserting through a hole: he agrees with the manager's lean".
proposed fix: give line 53 his words from record 1655 (or move it to history); write 1219 as `"That's a good clarification"` with the manager's question named outside the quotation marks; on 1142 quote `"Agree"` and add "(to the manager's lean, in a DISCUSSION)"; consider asking holes/labels as a one-line confirm, or mark its hole sentence "(his agreement to a lean)".

### RULING-6  SUSPECTED   severity: doc   effort: S
where: core.md [core/principles/general-rules] `principle` (record 3238-3260); also [core/principles/conservative-first] line 65
what: general-rules' class item is "(class: LEAN, with its condition)"; the record says "(1) LEAN, not a ruling". A principle "STATED" by him from a lean is a stretch; its second item (array-lift, a ruling) applies the rule to arrays only. The principle text ("What is needed is a consistent, general rule ...") is his, so this is borderline. conservative-first's item 65 cites part (0) of the same entry, which the record classes OBSERVATION, with no class mark in the item (the other four items are rulings, so the piece holds).
evidence: record 3253-3256: "(0) OBSERVATION: he had not anticipated these forms ... (1) LEAN, not a ruling: he likes arithmetic over arrays, ON CONDITION of "a consistent, general rule ..."".
proposed fix: keep general-rules but say in the details that the record classes it a LEAN's condition, adopted as a principle by the manager (or confirm with him); mark item 65 "(class: OBSERVATION)".

### RULING-7  SUSPECTED   severity: design   effort: S
where: core.md [core/principles/nothing-outside-domain] `ruled` vs [core/values/arithmetic] `ruled`; SIBLING-OF-A-FAMILY
what: the principle rests on exactly the two rulings that also make the arithmetic piece (number-edges, plus-operands); his words are about arithmetic only ("we are restricting arithmetic to digits and anything else is nothing"). The statement "An operation outside its domain yields no match" widens it to every operation; that widening is the manager's. One fact, two pieces; the principle adds a scope he did not rule.
evidence: R197/R198 = R786/R787 (same quotes, same titles). Record 4801: "FOR NOW arithmetic (`+ - * %`) is restricted to the decimal numerals".
proposed fix: either keep only the arithmetic piece (with number-domain's "does not fit yields nothing"), or restate the principle as arithmetic's and mark any wider reach "(a reading)".

### RULING-8  SUSPECTED   severity: maintenance   effort: S
where: core.md [core/conditions/match-so-far] and [core/holes/bare-condition] (both `ruled` 2026-11-19); SIBLING-OF-A-FAMILY
what: both rest on the same three entries (zero-in-sequence, "on `0` inside an inserted part", "confirming: a bare condition last in an rx") and both state the `${A & (0: S)}` clause and the "last in an rx = the whole" clause. Also bare-condition's bullet "The condition is written with its parentheses, in a hole too" is the manager's call (record 5104-5106: "The manager's call (syntax; told to him)"), stated without "(a reading)" inside a ruled piece; it is already its own `reading` piece (core/spellings/condition-parentheses).
evidence: R637-R639 vs R1178-R1180 (identical titles). Record 5103-5106.
proposed fix: one owner (bare-condition keeps the hole facts, match-so-far points); replace the parentheses bullet with a `see: core/spellings/condition-parentheses`.

## Appendix A: quote containment census (part a)
Method: `timeout 120 python3 -I /var/tmp/pcrec-pcrec/scratch/crit-preddoc3/ruling/quotes.py` (imports the lint's own parse_details / ruling_items / fence_mask; an entry = from its title line to the next citable title; quote = text between the first `"` after the date/class and the last `"` before ` (record:`). Output items.json.
Population: 255 rulings items in the three details files (core, library, parked).
- EXACT (quote a substring of the cited entry): 115
- whitespace-only differences: 133
- `...`-joined, each segment exact: 2 (build-later 208, labels-as-defined 249)
- LOOSE (only with backticks/markup stripped) - manager's paraphrase: 1 (RULING-4)
- DRIFT: 2 (stated-behaviour 186 = manager text, RULING-1; holes/labels 1142 = re-quoted question, RULING-5)
- no quote: 2 (no-absence 53, and-in-hole 1219's parenthetical; RULING-5)
- cited title not found: 0
Owner-ness: `pre.py` prints the 70 characters before each located quote; all 248 located quotes sit after "HIS WORDS"/"His words, verbatim"/"(Frank: "/"his words:" or inside such a quotation, except the items named in RULING-1/4/5. 10 items whose quote equals a title fragment (e.g. "flags-propagate: yes") checked by hand: each is also inside "HIS WORDS, in full: ..." in the body.
Items citing an entry the record classes as non-ruling (OBSERVATION/QUESTION/LEAN/IDEA/DISCUSSION/disclaimer): all are labelled in the item except conservative-first 65 (RULING-6) and lib/control/when 156 ("that wasn't my ruling but my interpretation", a disclaimer; the piece holds by five other items).

## Appendix B: ruled pieces with no RULING-titled citation
Method: `timeout 60 python3 -I /var/tmp/pcrec-pcrec/scratch/crit-preddoc3/ruling/noruling.py`. 2 hits, both fine on reading the entry body: core/holes/zero-values/option (record 4900: "Class: RULING by his own statement"), core/modules/conflicts (record 5439: "Class: a RULING on the conflict").

## PROBED-AND-HELD
- (b) all 79 `ruled` + 9 `principle` core pieces and 15 `ruled` library pieces read statement-against-items (view.py side by side); besides RULING-1/2/6/7/8 every piece has at least one item that rules its statement, not a neighbour. Checked against the record body: padded (4492, 5134), label-flow PROPOSAL closed by 2026-11-17 label-flow ruling, plus-operands' "error" sentence read correctly as the later state (4801-4806, arithmetic body says nothing+warning), backref-label, number-domain, numeral-width, construction-line, flags-propagate, padded's 2026-11-15 body, option hole entries 4872/4898, same-name-count's MANAGER CORRECTION (holes/same-name speaks of `\k<h>` only, as corrected), rx-owns-flags (class "PRINCIPLE stated, in a DISCUSSION" matches record 4535-4536).
- Post-draft rulings (record 4834 on): other-holes, option hole x2, negated-class-hole, anything-text, zero-in-sequence, bare condition x2, padded-lazy-sparse, import-symbols x3, import-several, conflicts: each is a `ruled` piece citing it; no document follows the draft where these override it (spot-checked holes/class, range-end, option, negated-class, modules/*).
- (b) open pieces, 10 (8 core, 2 library): slugs and topic words grepped in the record. group-truth (last-pass-default 2323/2467 does not decide it; the details say "the 11-18 rulings do not entail an answer"), number-in-loop, class-positions, class-index (record 4828-4829: NEW questions after rev 29), hole-export (P29-13, never asked), bare-condition-labels (never asked), default-set (5303: "not asked now"), any-case-body, not-test: no owner ruling answers them. Only caller-ambiguous is (partly) answered: RULING-3.
- SIBLING-OF-A-FAMILY: rulings cited by 3+ pieces listed (20 entries); principle-piece pairs that only restate a piece's quote but carry his principle-shaped words (match-and-filter/filters/kinds, positions-own-rules/holes/insert, left-decides/filters/and, namespace-at-reference/backreferences, operand-world/labels/numbers) held: the words are general in his own sentence. Only stated-behaviour, nothing-outside-domain and match-so-far/bare-condition reported.
- Not done: parked_details items were in the census (a) but parked pieces' statements were not read against them (status `parked`, outside (b)).

CRITIC COMPLETE
