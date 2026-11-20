# Critic compB findings (round r59 preddoc3)

## Findings


### COMPB-1  CONFIRMED   severity: doc   effort: M
where: missing piece (expected lib/counting or a core group-question piece); library_details.md lib/counting/occurs (line 397); core.md core/model/table/group-truth. Draft §4.3, §8 ("THE GROUP QUESTIONS ... `some(c)`, `count(c)`"; "`count(...)` FIRST, `occurs` AS THE FALLBACK"), §5.1 line 6322-6323; record CF:977-978, CF:832.
what: the two group questions `some(c)` and `count(c)` (provided names: §8 lists them beside the `occurs` module; §5.1 says "`some`, `all` and `count` are library (prelude) names too") have NO piece in any document. They are used by core pieces (group-truth, outermost-view, labels), by `lib/modifiers/length`'s helper (`nchars := count(...)`) and named as candidates of default-set, yet no piece defines them. The details file admits it: library_details.md:397 "the core's group questions, which have no core piece yet". `count(c)`'s ruled facts (a canonical numeral, RULED CF:977-978 "Allows "even()" or other checks for count"; refused only on budget, `occurs` recommended, RULED CF:832; the [COUNT-TO-OCCURS] rewrite a LATER plan item, RULED CF:840) are reachable only as `readings:` lines of the occurs entry, not as a piece with `rulings:`.
evidence: `grep -nE '\bsome\(|`some`|\bcount\(|`count`' R/subject/predicates/*.md` (17 lines; no heading); piece list (213 headings, compB/pieces.txt) has no `some`/`count` heading.
proposed fix: add a piece per name (or one piece `some, count` like the occurs piece) — library if a body exists (`some(c)` = `occurs.at_least(1, c)`?), else core; status `ruled` for count's numeral/budget facts with the CF:977/832/840 rulings; `some` LEAN (prelude name, review RUL-13). Retire `all` there (`rejected:` all-question 23:18).

### COMPB-2  CONFIRMED   severity: doc   effort: M
where: missing piece (the assert module: `assert.some`, `assert.none`, `assert.same`); only parked/ideas/assert exists (a different thing: an `@assert` INSIDE a definition). Draft §5.6 (line 6560-6612), §5.1 line 6320 ("`@assert` comes from a module (`assert := import("assert")`, §5.6)"), §8 line 7083 ("`assert` (§5.6): `some`, `none`, `same`"); record CF:595-604, CF:608.
what: the assertion library is a ruled provided module and has no library piece, no core piece and no stated reason. Draft §5.6 STATUS: "Concept (compile-time assertions): RULED (CF:595, Q9). Library form `assert.some` etc.: RULED (CF:608, Frank's own `assert := import("assert")`, `assert.some("2024" & leap)`)"; "Validation of an ambiguous label's reading by an assertion: RULED (CF:950-951; the assertion library as its home: the record, CF:958)". None of `assert.some` / `assert.none` / `assert.same` / `@assert.each` occurs in any of the six documents (0 hits each). A session reading the base files whole does not learn that compile-time assertions exist, that their argument is a set position (RULED CF:713), or the label-ambiguity validation idiom ruled at CF:950-951.
evidence: name census (appendix A) rows assert.some/none/same/each: 0/0/0/0/0/0 in lib/core/parked base+details. `grep -n assert R/subject/predicates/*.md` hits only parked/ideas/assert and unrelated "edge assertion" text.
proposed fix: a library section (e.g. `lib/assert/…`, `module: assert`) with one piece for the module members (some/none/same), status `ruled` with CF:595/608/950-951 rulings, the set-position rule, the `@` effect-call spelling (LEAN), and `rejected:` lines for `assert_some(...)` built-ins and `check A == B` (SUPERSEDED, draft §5.6 STATUS), the searched-mode "search assertion" (not adopted, §13 O36), and `@each(...)` (spelling OPEN, §13 O22; lean `@assert.each`).

### COMPB-3  CONFIRMED   severity: doc   effort: S
where: core.md core/operators/statements (line 960-961) lists built-ins `pattern` and `eval`; no piece defines either. Draft §10 Eval (line 7171-7179, LEAN, CF:430); §5.2 line 6388/6400 (`pattern()`: LEAN), §12 line 7729 (`pattern()` OUT of phase 1, CF:889); record CF:252-253 (pattern), CF:430-436 (eval).
what: two of the seven closed-list built-ins are named in a list but reached by no piece, no parked entry, and no stated reason: `eval` (draft §10: a match-time filter, only as an explicit module "requires module 'eval'", with a budget; LEAN) and `pattern($x)` (the group's static pattern, pure; LEAN; out of phase 1 per draft line 7729). parked_details mentions `eval` only as a level name (line 492). Contrast `param`, `file_text`, `records`, `enumerate`, `import`, `@export`, `@warn`, which all reach a piece.
evidence: `grep -nE '\beval\b|`pattern`|pattern\(' R/subject/predicates/*.md` -> only core.md:960-961 (the list) and parked_details:492.
proposed fix: a library/records-style or core piece for each (status `reading`, the LEAN), or a parked piece with trigger (eval is an "IDEA, late in #6"; `pattern()` is "OUT of phase 1"); either way give the reason where the base file lists the name.

### COMPB-4  CONFIRMED   severity: doc   effort: M
where: missing pieces/statements for the library AS A WHOLE; library.md has only per-name pieces. Draft §8 RULE + STATUS (lines 6864-6867, 7083-7097); §2.7 NAMING RULE (line 5491-5500); record CF:38, CF:461-470, CF:1020-1022.
what: three library-level provided things, each ruled or leaned in §8, reach no piece and no stated reason:
 (a) THE STANDARD LIBRARY itself: "Standard library = prelude text (macros ...) on the foundation; it grows without compiler changes"; "Standard library: RULED as a follow-up initiative (CF:38)"; candidate content (network, time, identifiers, communication, checksummed numbers) "each tested against the standard's OWN vectors (as `@assert` statements), the callout oracle and the laws; each shows its DFA column". Nothing in core/library/parked says the content is a ruled follow-up.
 (b) BLESSED CALLOUTS: LEAN (CF:461 "Lean ADOPT"), own plan row [BLESSED-CALLOUTS], the owner's 2026-11-15 pointer CF:1191-1192; luhn/weekday/days_in are named there as blessed callouts DECLARING A REGULAR TWIN. In the documents only a passing "or a blessed callout" (library.md:242) and two history mentions; library.md:6-7 dismisses `weekday_of`, `days_in`, `luhn` as "worked-example bindings ... not provided names", which is true for the draft's `:=` bindings but leaves the blessed-callout direction (where the same names are the planned PROVIDED content) with no home, not even parked.
 (c) THE NAMING RULE over every provided transform: RULED BY ACCEPTANCE (CF:1020-1022, accepted at CF:1006; draft §2.7 NAMING RULE, §0 rulings table line 4246: "every PROVIDED transform is named for how it changes the FILTER, never for an action on the subject"). It is the reason `search` was renamed; the documents cite it only as "under his naming rule" (library_details.md:208) and "a filter modifier named for what it reads" (library.md:45); no piece states it, so a session naming a new library piece cannot find it.
evidence: `grep -nE -i 'blessed|follow-up|prelude|grows without|own vectors|naming rule|named for' R/subject/predicates/*.md` -> library.md:45, :242, library_details.md:208, core.md:1043 only.
proposed fix: a section-head paragraph or a `lib/…/standard-library` piece (status ruled, CF:38) naming the follow-up and its test rule; a parked piece `parked/ideas/blessed-callouts` (LEAN, trigger: its plan row) naming luhn/weekday/days_in as its first contents; a principle or library-head piece for the naming rule with the CF:1020-1022 ruling (and `rejected:` the name `search`, already present).

### COMPB-5  CONFIRMED   severity: doc   effort: M
where: no `rejected:` field anywhere; expected on the joint-condition piece (core/conditions/form, whose details carry only two rejected items) and/or a library/parked home. Draft §8 (1)-(2) (lines 7040-7056), §8 STATUS (7093-7113), §16 + §16.1-16.2 (lines 9291-9677); record "2026-11-15 RULINGS — tuple compare in the first library", "2026-11-15 RULING — tuple compare names", "2026-11-15 RULING — tuple compare argument order", "2026-11-16 RULING — a compare names its fields with the other-side sigil", "2026-11-16 OWNER RULING — library-not-syntax", "2026-11-16 OWNER RULING — retire-paused".
what: a whole CLASS of rejected candidates is missing: the retired/paused tuple-compare LIBRARY direction (rev 16-19, moved verbatim to the draft's §16). The draft names each as RETIRED, WITHDRAWN, PAUSED or NOT ADOPTED, and several were RULED before being retired, which is exactly what "what was rejected and why" must carry: (1) the six provided names `lex_ge2` .. `lex_between3` (RULED, "tuple_names: a"; RETIRED, retire-paused); (2) their argument order subject-low-high (RULED, "tuple-arg-order"; RETIRED); (3) the fixed-size compares' first-library slot (RULED "tuple-compare: agree"; RETIRED, the joint condition takes it); (4) the 2026-11-14 TUPLE CONDITIONS "a LIBRARY macro (`lex_ge(...)`), no syntax" (WITHDRAWN BY NAME, library-not-syntax: "we've replaced the idea and I think with something much better"); (5) keeping `lex_ge` and friends as library macros over the joint condition (NOT taken: "left out of the first library until someone asks"); (6) the projection and the field reference / other-side sigil `^h` (RULED rev 19; PAUSED INDEFINITELY: "the pause on ^ is indefinite and requires real value other than 'override a users own *'"); (7) the section `(h:)` (not adopted); (8) rev 18's decided-prefix order (WITHDRAWN, unset-component: "unset-component: yes"); (9) rev 18's readings (a), (b) (NOT ADOPTED, macro-arguments answered NO); (10) the strict spelling `lex_ge2(s, lo) & !lex_le2(s, lo)` (now `>`). Only (6) surfaces, as a SIDE remark inside parked_details' field-count item text (lines 175-185); none of (1)-(10) is a `rejected:` line, and none of the slugs tuple-compare, tuple_names, tuple-arg-order, library-not-syntax, retire-paused, unset-component, macro-arguments, joint-loops appears on any `slugs:` line (grep: 0 slug hits; library-not-syntax 0 hits anywhere).
evidence: `grep -nE 'sigil|lex_|projection|tuple compare|retire-paused|library-not-syntax|first-library|decided-prefix|unset-component' R/subject/predicates/*.md` -> parked_details.md:175-185 only. Rejected census (appendix B) rows T1-T10: 0 of 10 carried.
proposed fix: on the joint-condition's home (a `core/conditions/joint` sub-piece or core/conditions/form) add `rejected:` lines for (1)-(5), (7)-(10) with their rulings and reasons, the slugs on its `slugs:` line, and a `parked/ideas/other-side-sigil` piece for (6) (PAUSED INDEFINITELY, trigger = "real value other than 'override a users own *'").

### COMPB-6  CONFIRMED   severity: doc   effort: S
where: core_details.md core/conditions/defaults (rejected: one item only); record "2026-11-16 OWNER RULINGS — drop-mark, default-value, source-row; default-scope to a lane"; draft §16.4/§4.2, §8 (2), (4) ("rev 20-22's second control `((h, m?): ...)` is out").
what: the optional mark on a label (`h?`, `(h?: <5)`, `((h, m?): R)`), RULED into the language in rev 20-22 and then RULED OUT ("drop-mark: YES. The optional mark is OUT of the language"), is carried by no `rejected:` field; nor are the readings it retired with it (zero-pass-empty, match-context, domain-scope, mark-narrows, mark-in-none, mark-range, absent-rule's mark clause, DOM). `drop-mark` occurs only in parked_details SUPERSEDED-IN-PART notes copied from the ideas file. The defaults piece is where a session would look for "why not a mark?"; its details has neither the drop-mark nor the default-value ruling ("Default-value: yes").
evidence: `grep -cE 'drop-mark' compB/rejected_items.tsv` = 0; `grep -nE 'drop-mark|domain-scope' R/subject/predicates/*.md` -> parked_details only (5 lines, all inside quoted ideas-file text).
proposed fix: core/conditions/defaults (or core/conditions/two-valued): `rejected: - the optional mark `h?` (every value the label could hold, rev 20-22) — by owner ruling — drop-mark ("Drop-mark: yes"): an absent label never matches; the author writes a default`; add the default-value ruling to `rulings:` and `drop-mark default-value` to `slugs:`.

### COMPB-7  CONFIRMED   severity: doc   effort: S
where: draft §R.9 table rows (line 3559-3737; appendix B rows R9-7, -8, -12, -42, -43, -75, -79, -106); expected homes core/conditions/form (joint), core/principles/no-absence or core/conditions/defaults, core/patterns/alternation, core/labels/numbers, core/labels/flow, core/holes/flags, core/labels/backreferences, core/diagnostics/dollar-form.
what: eight §R.9 rows that record a CANDIDATE the language once had (or the draft read) and that a ruling removed have no `rejected:` line:
 - R9-7: per-pass pairing for a BARE joint condition (joint-loops (1), RULED 11:17) — REVERSED rev 24.1 / restated by after-loop-read (a bare joint pairs within the last pass). The joint has no piece of its own; core/conditions/form's rejected field has only label-twice and condition-or.
 - R9-8: absent-rule (LOCKED 14:31) clause (2) "over several values ... every value ... at least one" — NARROWED for bare conditions by last-pass-default. core_details:50-53 cites absent-rule as a ruling on the no-absence principle, with no record of the narrowed clause.
 - R9-12: rev 23.2's reading (iii) of branch-scope and its scope rule — REVERSED by branch-scope (ii) 11:35. core/patterns/alternation rejects only reading (i).
 - R9-42: "numbers name the groups of the nearest pattern to their left" and "numbers are not subject to the ambiguous-reference error" — WITHDRAWN by number-names ("Only when there is no ambiguity"). core/labels/numbers has an EMPTY rejected field.
 - R9-43: names resolved inside a part before the splice / renaming groups apart as the RULE — WITHDRAWN by "it should be the last reference as labels" and free-name. Not in core/labels/flow or backreferences.
 - R9-75: hole-flags' split "plain text with no flags of its own" vs "pattern text written with flags" — WITHDRAWN ("under one type there is no "plain text" kind"). core/holes/flags carries four rejected items, not this one.
 - R9-79: rev 27's three candidates for `\k<h>` after two groups of one name — RULED a compile error unless `(?J)` (same-name-twice); the candidates are not listed.
 - R9-106: rev 29's lexical dollar-warning trigger and place-blind hint — REPLACED by the manager's calls (P29-11/12). core/diagnostics/dollar-form has two rejected items, not this.
evidence: keyword map compB/r9_keys.tsv run against compB/rejected_items.tsv (190 items), then each zero row read by hand in its expected entry (awk extracts printed above in my run; numbers' `rejected:` line is empty).
proposed fix: one `rejected:` line per row in the named entry, citing the R.9 row's "changed by" words.

### COMPB-8  CONFIRMED   severity: doc   effort: S
where: draft §13 O61 THE AUDIT (line 8819-8829: the draft's OWN census "every provided macro whose input and output are filters"), §7 (line 6730-6732), R.1.7 (line 1313), §2.5 (line 5164-5170), §5.3 (line 6417), §9 (line 7129-7136), §R.9 rows 14/24; record 2026-11-13 "NO CONCATENATION OPERATOR IN PREDICATES" (CF:69), CF:415-416, CF:583.
what: further provided names and name-level rejections that reach no piece, parked entry or `rejected:` line:
 - `sort(alts, by = "length", order = "desc")` and `unique` (§7: "exists only as the deliberate leftmost-longest choice"; "`unique` keeps the first occurrence"; the record CF:415-416) and `sorted` / `distinct` ("take the array", R.1.7, from pass-list-read RECORD (3)): 0 pieces; docs mention "sorted" only inside a parked item's quoted text.
 - `json.row` (E-JSONL's module member; PASS in the draft's own provided-macro audit) and `any_order(a, sep = ...)` (§5.3 "candidate sugar"; graded in the audit): 0 hits in all six documents. `json.string` appears only as a sub-bullet of the CUT json.quoted piece.
 - `concat(x, y)` ("Value concatenation is insertion or a library name (`concat(x, y)`)", §2.5) together with the 2026-11-13 lean "no concatenation operator" (R.9 rows 14, 24: REVERSED by sequence-operator, "is there a reason why not?"): core/patterns/sequence rejects juxtaposition and a string paste, not the no-operator position or `concat`.
 - §9 CUT, RULED (CF:583, predx Q8): DECLARED TYPES (`type(...)`, `isodate: date`), TYPE MEMBERS, SCOPE-LIMITED UFCS, `types()` (and the record's `kind()`). Only typed PARAMETERS are rejected (core/operators/bindings); core/modules/map even repeats "members of a TYPE travel with the type (`d.weekday` ...)" as a lean with no pointer to the cut.
 - `@assert.each` / `@each(...)` (OPEN §13 O22) and `@assert.reading(...)` (not proposed, D77): see COMPB-2.
evidence: name census appendix A rows sort/unique/sorted/distinct/json.row/any_order/concat/types(): 0 base pieces, 0 rejected lines; `grep -nE 'sort\b|unique|sorted|distinct|json\.row|any_order|concat|UFCS|types\(' R/subject/predicates/*.md`.
proposed fix: library pieces (status `reading`, the draft's LEAN) for sort/unique and sorted/distinct (or one parked piece if the owner never ruled them), `json.row`/`json.string` as a `module: json` piece; `rejected:` lines: on core/patterns/sequence "no concatenation operator; `concat(x, y)` a library name (the 2026-11-13 lean) — by owner ruling — sequence-operator"; on core/modules/map "declared types, type members, UFCS, `types()` in the first spec — by owner ruling (CF:583, §9 CUT)".

### COMPB-9  SUSPECTED   severity: doc   effort: S
where: library.md lines 6-7 (the header: "Worked-example bindings of the draft (`isodate`, `weekday_of`, `days_in`, `luhn`, `leap`, `tagged`, ...) are examples, not provided names, and have no piece"); draft §5.1 line 6321-6322, §4.6 line 6264-6267, §6.1 line 6631, §8 line 7085, §12.4-12.7.
what: the stated reason misclassifies four names. The draft says the opposite in §5.1: "Every other name in the examples (`between`, `startsWith`, `contains`, `padded`, `days`, `weekday_of`, `within`, `list_of`, `join`, `each`, `occurrences`, ...) is a library name"; §4.6 speaks of "the library's `days_in`"; §6.1 gives them a level rule ("At the default level a REGULAR TWIN (luhn, weekday, days_in) MUST take its automaton form"); §8 names them as blessed callouts' regular twins. Unlike `isodate` (bound `isodate := join(...)` in E-CAL) and `tagged` (bound `tagged(S) := ...` in §11), `weekday_of`, `days_in`, `luhn` and `days` are never bound by `:=` in any example: they are CALLED as provided names whose bodies the draft does not write. The documents treat `within` (same §5.1 list, same status: called, never defined) as a provided name with an under-construction piece, but not `days` (absent from the documents entirely) or `weekday_of`. HOW I TOLD THEM APART: a name is a worked-example binding when an example program binds it with `:=` (isodate, tagged, octet, late, office_hours, t, list, card, dim, wd, d, q, headers ...); it is provided when the draft or record assigns it to the language or library (a library-name list, a module member, "the library's X", a built-in list, "provide") whether or not a body is written.
evidence: `grep -nE 'weekday_of|days_in|\bluhn\b|days\(' predicates_draft.md` -> every occurrence is a call (6141, 6143, 6264-6267, 7771, 7795, 7806, 7837, 7853), no `weekday_of :=`/`days_in :=`/`luhn :=`/`days :=` anywhere (the `:=` census, appendix A method 3).
proposed fix: either under-construction pieces beside `within` (`days`, `weekday_of`, `days_in`, `luhn`; or one `lib/dates/…` piece "named by the worked examples, not defined") or a parked blessed-callouts piece that names them (COMPB-4 (b)); correct the header sentence to list only `:=`-bound names.

### COMPB-10  CONFIRMED   severity: doc   effort: S
where: library.md lib/search/occurrences, lib/records/records; core.md core/modules/map; draft §2.6 line 5248-5252, §0 rulings table line 4259 (CF:1070-1072), §7 line 6704-6705, §3.2 line 5710, §5.3 ordinal paragraph (line 6431-6433).
what: three smaller provided items reach no piece:
 - the hit-label NAMING parameter of `occurrences`/`contains`: "a call may NAME its hit label; two calls exposing the same hit label in one chain are the ambiguity error, the per-call name its fix" (RULED, CF:1070-1072; his words `occurrences(x, label = "foo")`, the spelling a placeholder). The occurrences piece and its details carry no `label =` / naming clause (`grep 'label =' library*.md`: 0).
 - `file_literals(p)`: "library sugar over `records` with a NAMED item rx (no hidden default)" (§7; the record CF:411 `file_literals("w.txt")[!startsWith("#") & length(<=20)]`): 0 hits in all six documents.
 - the reserved METADATA fields `.index`, `.label` ("reserved fields", §3.2 tool 4; §5.3: "`x.index` (original position) and `x.label` (original name)"; the ordinal's `start =`/`ordinal =` settings): used in core.md (enumerate, class-index) and library.md (`capture`, `month_numbered`) but defined by no piece; core/modules/map says only "metadata".
evidence: name census appendix A rows; greps listed.
proposed fix: a clause + `rulings:` item on lib/search/occurrences for the naming parameter; a line under lib/records/records for `file_literals` (reading); a core piece (or a clause on core/modules/map) listing the reserved metadata fields and what each yields.

## GENERAL FORM + UNLOCKS

The two classes that went missing whole (COMPB-2 the assert module, COMPB-5 the retired tuple-compare family, COMPB-6 the optional mark, and the §9 cut list in COMPB-8) share one shape: the converter walked the draft's LIVE sections piece by piece and took `rejected:` lines from the history it met inside each live definition. Candidates whose whole home is a SUPERSEDED section (§16, §9, §R.9 rows whose subject has no live piece, a STATUS paragraph), and provided names whose home is a section that defines no single construct (§5.6, §8's RULE/STATUS paragraphs, §7's bullets, §13 O61's audit), had no live piece to hang on, so they fell through.
GENERAL RULE for the converter (and a lint-able control): (1) every name in the draft's own provided-name censuses (§5.1's built-in list and "library name" list, §8's list, §13 O61's audit, §0's rulings-table rows that say "provided") must resolve to a piece, a `rejected:` line, or a parked piece — the converter cannot drop a census row silently; (2) every row of §R.9 and every §16/§9 item must resolve to a `rejected:` line (or be marked "draft-internal correction, no candidate") — again a row-by-row ledger, not a judgement while reading. TRIGGER: any conversion or revision that retires a section or moves text to a superseded section. UNLOCK: with that ledger kept as a TSV beside the documents, `pred_doc_lint` can run it (a new rule "every census name / every R.9 row lands") and the next critic's control becomes a re-run instead of a re-derivation; the same ledger serves the owner's "what was rejected and why" use (doc_format use 4) for names, which today has no index at all (a `rejected:` line is reachable only by the piece's tag, so a rejected NAME with no live piece is unreachable by construction — a `lib/rejected` or `parked/rejected-names` section of name -> reason would make every rejected name greppable by name).

## Appendix A — PROVIDED NAMES (control built from the draft and the record FIRST)

Method (re-runnable): (1) `grep -oE '`[A-Za-z_][A-Za-z0-9_.]*\('` over predicates_draft.md (104 call-form names, compB/draft_calls.txt); (2) dotted names `grep -oE '\b[a-z_]+\.[a-z_][a-z0-9_]*\b'` (module members; warning names like `anchor.whole` excluded: diagnostics, not provided names); (3) every `NAME(...) :=` binding in the draft (to separate example bindings); (4) reading §5.1 (built-ins, library-name list), §5.3, §5.5, §5.6, §7, §8 whole, §9, §10, §2.5-2.7, §13 O61's audit, R.1.4/R.1.10/R.1.14/R.1.16 T9, §R.8 spellings 22/32; (5) the record grepped for provide|library|built-in|prelude and the 2026-11-19 entries after line 4834 (limited, sys.peek, the library-document entry's list). Rule: a name is PROVIDED if the draft or record assigns it to the language or a library (a list, a module member, "the library's X", "provide"), with or without a body; it is a WORKED-EXAMPLE BINDING if an example binds it with `:=` (isodate, tagged, octet, late, office_hours, t, card, dim, wd, d, q, list, headers, not_seven, ...). Then each name grepped in the six documents (compB/names.txt, compB/name_hits.tsv) and the hits read. Status: F = a piece; R = a stated reason (cut/withdrawn/parked/not provided); R* = a stated reason I dispute (COMPB-9); P = partial; M = missing.
On the earlier census: "72 candidate names" vs 61 listed; my list is 98 rows (the six `lex_` names counted singly, families like `occurs.*` counted per member, plus the built-ins and the record's later names). Counted by family (occurs = 1, lex_ = 1, assert = 1, prefix_in/suffix_in/slice_in = 1, rx.digit/alnum = 1, metadata = 1) it is 80.

| # | name | draft/record source | status | where / finding |
|---|---|---|---|---|
| 1 | `startsWith` | §8 | F | lib/search/starts-with |
| 2 | `endsWith` | §8 | F | lib/search/ends-with |
| 3 | `contains` | §8 §2.6 | F | lib/search/contains |
| 4 | `anchored` | §8 | F | lib/search/anchored |
| 5 | `between` | §8 | F | lib/sets/between |
| 6 | `occurrences` | §8 §2.6 | F | lib/search/occurrences |
| 7 | `hits` | R.1.9 | F | lib/search/hits |
| 8 | `when` | §8 R.1.10 | F | lib/control/when |
| 9 | `peek` | R.1.10, rec doc-shape | F | lib/control/peek |
| 10 | `padded` | §8 §2.7 | F | lib/modifiers/padded |
| 11 | `unpadded` | §9 CUT | R | lib/modifiers/unpadded (cut, rejected) |
| 12 | `any_case` | §8 §2.7 | F | lib/modifiers/any-case |
| 13 | `quoted` | §8 §2.7 | F | lib/modifiers/quoted |
| 14 | `length` | §8 §2.7 | F | lib/modifiers/length |
| 15 | `month_numbered` | §8 §2.7 | F | lib/modifiers/month-numbered |
| 16 | `prefix_in` | §2.7 A17 | F | lib/sets/prefix-in |
| 17 | `suffix_in` | §2.7 | F | lib/sets/prefix-in |
| 18 | `slice_in` | §2.7 | F | lib/sets/prefix-in |
| 19 | `left (image)` | R.1.16 T9 | F | lib/strings/left |
| 20 | `right (image kin)` | rec CF:61, T9 "and kin" | P | only the filter names rejected (lib/sets/prefix-in); the image not stated |
| 21 | `mid (image kin)` | rec CF:61, T9 | P | same |
| 22 | `upperStart` | T9 | F | lib/strings/upper-start |
| 23 | `strlen` | R.9 row 95 | F | lib/strings/strlen |
| 24 | `json.quoted` | §9 CUT | R | lib/modifiers/json-quoted |
| 25 | `json.string` | §9, §12.1 | P | sub-bullet of json-quoted only |
| 26 | `json.row` | §7, §12.1, O61 audit | M | COMPB-8 |
| 27 | `some` | §4.3 §8 §5.1 | M | COMPB-1 |
| 28 | `count` | §4.3 §8 (RULED CF:977) | M | COMPB-1 |
| 29 | `all` | §4.3 (RETIRED) | R | rejected on lib/counting/occurs (in passing) |
| 30 | `occurs.exactly` | §8 | F | lib/counting/occurs |
| 31 | `occurs.at_least` | §8 | F | lib/counting/occurs |
| 32 | `occurs.at_most` | §8 | F | lib/counting/occurs |
| 33 | `occurs.none` | §8 | F | lib/counting/occurs |
| 34 | `occurs.some` | §8 (withdrawn) | R | rejected lib/counting/occurs |
| 35 | `occurs.all` | §8 (withdrawn) | R | rejected lib/counting/occurs |
| 36 | `assert.some` | §5.6 RULED | M | COMPB-2 |
| 37 | `assert.none` | §5.6 RULED | M | COMPB-2 |
| 38 | `assert.same` | §5.6 | M | COMPB-2 |
| 39 | `assert.each / @each` | §5.5 §5.6 O22 | M | COMPB-2 |
| 40 | `each` | §5.3 | F | lib/structural/each |
| 41 | `each_group` | §5.3 | F | lib/structural/each |
| 42 | `where_group` | §5.3 | F | lib/structural/each |
| 43 | `where` | O61 audit | F | lib/structural/each (census row cited) |
| 44 | `join` | §5.3 | F | lib/strings/join |
| 45 | `list_of` | §5.3 | F | lib/records/list-of |
| 46 | `any_order` | §5.3 candidate sugar | M | COMPB-8 |
| 47 | `capture` | §5.3 | F | lib/structural/capture |
| 48 | `enumerate` | §5.5 built-in | F | core/arrays/enumerate |
| 49 | `import` | §5.1 built-in | F | core/modules/import |
| 50 | `pattern()` | §5.1 built-in, §5.2 | M | COMPB-3 |
| 51 | `param` | §5.1 built-in | F | lib/records/param |
| 52 | `file_text` | §5.1 built-in | F | lib/records/file-text |
| 53 | `records` | §5.1 built-in | F | lib/records/records |
| 54 | `eval` | §5.1 built-in, §10 | M | COMPB-3 |
| 55 | `@warn` | §5.1, §7.1 | F | core/diagnostics/warnings |
| 56 | `@export` | §5.1, §7 | F | core/modules/export |
| 57 | `@options.strict` | §7.1 | F | core/diagnostics/warnings, parked/ideas/severity-table |
| 58 | `anything` | R.1.4 (provide "anything") | F | lib/sets/anything |
| 59 | `never-matching constant` | R.8 spellings 32 | F | parked/ideas/never-constant |
| 60 | `rx.digit` | R.1.14 | F | lib/rx/classes |
| 61 | `rx.alnum` | R.1.14 | P | lib/rx/classes, only as "..." |
| 62 | `rx.repeat` | R.1.14 | F | lib/rx/repeat |
| 63 | `digits (plural)` | R.1.14 | F | lib/rx/classes, lib/rx/repeat |
| 64 | `rx.optional` | rx_module note | R | lib/rx/optional-loop (not provided) |
| 65 | `rx.loop` | rx_module note | R | lib/rx/optional-loop (not provided) |
| 66 | `limited` | rec padded-lazy-sparse | F | lib/modifiers/limited, parked/ideas/limited |
| 67 | `within` | §5.1 library name | F | lib/sets? within (under-construction) |
| 68 | `days` | §5.1 library name, §4.4 | M | COMPB-9 |
| 69 | `weekday_of` | §5.1 library name | R* | library.md header (reason disputed, COMPB-9) |
| 70 | `days_in` | §4.6 "the library's days_in", §6.1 | R* | library.md header (disputed) |
| 71 | `luhn` | §6.1 §8 regular twin | R* | library.md header (disputed) |
| 72 | `leap` | rec CF:23 prelude example | R | library.md header |
| 73 | `lex_ge2` | §8 (1), §16 RETIRED | M | COMPB-5 |
| 74 | `lex_le2` | same | M | COMPB-5 |
| 75 | `lex_between2` | same | M | COMPB-5 |
| 76 | `lex_ge3` | same | M | COMPB-5 |
| 77 | `lex_le3` | same | M | COMPB-5 |
| 78 | `lex_between3` | same | M | COMPB-5 |
| 79 | `lex_ge(n, s, lo) any-arity` | §8 (1), first-rest | R | parked/ideas/first-rest |
| 80 | `sort` | §7 | M | COMPB-8 |
| 81 | `unique` | §7 | M | COMPB-8 |
| 82 | `sorted` | R.1.7 | M | COMPB-8 |
| 83 | `distinct` | R.1.7 | M | COMPB-8 |
| 84 | `concat` | §2.5 | M | COMPB-8 |
| 85 | `types()` | §9 CUT | M | COMPB-8 |
| 86 | `search (old name)` | §2.6 renamed | R | formerly: on lib/search/occurrences |
| 87 | `cartesian` | rec, parked | F | parked/ideas/cartesian |
| 88 | `atomic()` | R.1 atomic-search | F | core/patterns/atomic, parked/ideas/atomic |
| 89 | `file_literals` | §7, rec CF:411 | M | COMPB-10 |
| 90 | `unpad` | rec CF:249 | R | rejected lib/modifiers/length |
| 91 | `sys (module, his example)` | rec doc-shape | R | library_details history (not ruled) |
| 92 | `blessed callouts (family)` | §8 LEAN | M | COMPB-4 |
| 93 | `.index (metadata)` | §3.2 §5.3 | P | used, no defining piece (COMPB-10) |
| 94 | `.label (metadata)` | §3.2 §5.3 | P | used, no defining piece (COMPB-10) |
| 95 | `hit (provided label)` | §2.6 | F | lib/search/occurrences |
| 96 | `$& / $_ (reserved)` | §5.1 (dropped) | R | rejected core/operators/statements |
| 97 | `occurrences label= setting` | §2.6 RULED CF:1070 | M | COMPB-10 |
| 98 | `standard library (the initiative)` | §8 RULED CF:38 | M | COMPB-4 |

TOTALS A: expected 98; F 49, R 13, R* 3 (stated, disputed), P 6, M 27. Missing names: json.row, some, count, assert.some, assert.none, assert.same, assert.each, any_order, pattern(), eval, days, lex_ge2, lex_le2, lex_between2, lex_ge3, lex_le3, lex_between3, sort, unique, sorted, distinct, concat, types(), file_literals, blessed callouts, the `occurrences` label= setting, the standard library initiative.

## Appendix B — REJECTED CANDIDATES (control built from the draft FIRST)

Method: (1) the §R.9 table (draft lines 3559-3737), every row (109 rows), parsed with `awk -F'|'`; each row classed as a CANDIDATE (a rule, form or name the language or draft had, removed by a ruling/run/review) or N/A (a draft-internal correction of wording, evidence, filing, or a narrowing that rejects nothing); (2) §16 + §8 (1)-(2) + §8 STATUS + §9 + §5.6 STATUS + §5.1 + name-level rejections found by a scan of the whole draft for WITHDRAWN|withdrawn|REVERSED|RETIRED|retired|SUPERSEDED|CUT|REPLACED|REJECTED|DROPPED|dropped|NOT ADOPTED|not adopted (586 hits, compB/draft_rejwords.txt; read for NAMED candidates, not every hit). (3) the documents' `rejected:` items extracted by compB/rej.py (190 items: core 142, library 48, parked 0 — all 39 parked `rejected:` fields are empty), keyword-matched per row (compB/r9_keys.tsv) and every zero or doubtful match read by hand in the expected entry.

R.9: 109 rows; N/A 37 (rows 15, 21, 24 (= row 14's candidate), 33-36, 54, 55, 56, 57, 58, 63, 64, 67, 70, 71, 72, 76, 77, 80, 84, 85, 86, 88, 89, 90, 91, 92, 94, 95, 103, 104, 107, 108-111 as one group counted 4); CANDIDATES 72.
| R9 row | candidate | verdict | rejected item(s) |
|---|---|---|---|
| 3, 4 | one-parse reject / note (a) | carried | core #16 reading (i) of branch-scope; #1, #6 SQL picture |
| 5 | absence never matches, negated or not | carried | #36 |
| 6 | `x:` = all iterations; plain condition = ALL hits | carried | #20, #27 |
| 7 | per-pass pairing for a bare joint | MISSING | COMPB-7 |
| 8 | absent-rule clause (2) | MISSING | COMPB-7 |
| 9 | a pass that sets nothing keeps the earlier value | carried | #21 |
| 10 | labels match every pass, captures the last | carried | #20, #27 |
| 11 | `all` | carried (in passing) | lib #181 |
| 12 | reading (iii) and its scope rule | MISSING | COMPB-7 |
| 13 | `when` filter form / complement body | carried | #160, #49 |
| 14 (24) | no concatenation operator (the 11-13 lean), `concat(x, y)` | MISSING | COMPB-8 |
| 16 | prove-itself vs by-name | carried | #2 |
| 17 | per-pass label rules | carried | #10, #11 |
| 18 | each pass begins by unsetting | carried | #43, #26 |
| 19 | `$x` as standard pcre | carried | #44 |
| 20 | ^...$ of the filtered condition | carried | #48 |
| 22 | hits of the matched stretch | carried | #170 |
| 25 | edge-assertion error for holes | carried | #74 |
| 26 | a hole denotes a set of strings | carried | #72, #76 |
| 27 | shared-label error of existence | carried | #24 |
| 28 | empty-match hazard error | carried | #8, #129 |
| 29 | `min` 0 or 1 | carried | #164, #132 |
| 30 | `compare.width` compiler warning | carried | #134 |
| 31 | warning names without the `pcrec.` prefix | MISSING (minor) | core/diagnostics/warnings has no such line |
| 32 | union reading C1 | carried | #187 |
| 37 | backreference reads the last-set capture | partial | #33 |
| 38 | single product column | carried | #4, #75 |
| 39 | name copies as plain alternatives | carried | #81 |
| 40 | the two argument refusals | carried | #165, #166 |
| 41 | hits are those of a plain search | partial | #168 |
| 42 | numbers: nearest pattern to the left; exempt from ambiguity | MISSING | COMPB-7 |
| 43 | names resolved in a part before the splice / renaming | MISSING | COMPB-7 |
| 44 | read-out is the left side's value | carried (as an open candidate) | caller-ambiguous readings |
| 45 | a filter can never produce captures | carried | #29, #101 |
| 46 | quantifier on a condition: regex's | carried | #40 |
| 47 | adding two patterns a type error | carried | #56 |
| 48 | value in a pattern position only if one-member | carried | #55 |
| 49 | lone `!B` whole-value reading | carried | #50, #51 |
| 51 | `x & (NOT c | p)` as THE definition | carried | #160 |
| 52 | then/else optional args | carried | #159 |
| 53 | when(x) = x | carried | #158 |
| 59 | dollar-condition error | carried | #54, #131, #137 |
| 60 | `\k<h>` reads the label | carried | #32 |
| 61 | value-is-pattern third part (lean -> ruled) | carried (ruled, no rejection) | — |
| 62 | a value is a STRING | carried | #55 |
| 65 | "No conditions. No &." | carried | #53 |
| 66, 101 | plus-operands TYPE ERROR lean | carried | #59 |
| 68 | computed label a VALUE | partial | #55 |
| 69 | `left(n, S)` | carried | #65, #180 |
| 73 | two number domains | carried | #57 |
| 74 | NO INHERITED FLAGS | carried | #97 |
| 75 | plain text with no flags | MISSING | COMPB-7 |
| 78 | exact for padded-width | carried | #143 |
| 79 | `\k<h>` after two groups: rev 27's candidates | MISSING | COMPB-7 |
| 81 | `any_case` candidate body "not it" | carried | #152 + readings |
| 82 | numeral-width: width kept | carried | #58 |
| 83, 96 | two-case padded body / argument's own order | carried | #144, #145 |
| 87 | widest first enumerator | carried | #68 |
| 93 | `${@y}` | carried | #96 |
| 97 | every flag propagates | carried | #98 |
| 98 | codepoint for lifts | carried | #69, #70 |
| 99 | a read stands for its group's rx | carried | #138 |
| 100 | operands keep their own flags (m2) | partial | #97 |
| 102 | `\k<h>` across a hole = last mention | partial | #102, #103 |
| 105 | `% 0` its own error / constant-operand trigger | carried | #62 |
| 106 | lexical dollar-warning trigger | MISSING | COMPB-7 |
R.9 TOTALS: candidates 72 (rows counted singly, joined rows as listed); carried 57, partial 5, MISSING 10 (7, 8, 12, 14, 31, 42, 43, 75, 79, 106).

Beyond R.9 (§16, §8, §9, §5.x, name level): 30 candidates.
| id | candidate | verdict | where |
|---|---|---|---|
| T1-T6 | the six `lex_` names; argument order; first-library slot | MISSING | COMPB-5 |
| T7 | 2026-11-14 TUPLE CONDITIONS as a library macro (library-not-syntax) | MISSING | COMPB-5 |
| T8 | `lex_` kept as library macros over the joint condition | MISSING | COMPB-5 |
| T9 | projection / field reference / sigil `^h` (PAUSED), section `(h:)` | only inside parked field-count text | COMPB-5 |
| T10 | decided-prefix order; rev 18 readings (a)(b); strict spelling | MISSING | COMPB-5 |
| E1 | `json.quoted` | carried | lib #153 |
| E2 | `unpadded(n, S)` | carried | lib #149 |
| E3 | `search` | carried | lib #163 + formerly: |
| E4 | `occurs.some`, `occurs.all` | carried | lib #181 |
| E5 | `left/right/mid(n, S)` filter names | carried | lib #180 |
| E6 | `$&`, `$_` | carried | core #118 |
| E7 | `export capture(x) :=` keyword form | carried | lib #189 |
| E8 | `transform.noop` | carried | core #136 |
| E9 | `rx.digits(min, max)` | carried | lib #185 |
| E10 | `rx.optional`, `rx.loop` | carried | lib #188 |
| E11 | fold of startsWith/endsWith into occurrences | carried | lib #174 |
| E12 | `anchored(rx) := /^${rx}$/` | carried | lib #175 |
| E13 | `startsWith(rx) := /^${rx}/` | carried | lib #173 |
| E14 | `all(c)` group question | partial (in passing) | lib #181 |
| E15 | the optional mark `h?` (drop-mark) | MISSING | COMPB-6 |
| E16 | declared types, type members, UFCS, `types()` (§9 CUT) | MISSING | COMPB-8 |
| E17 | `assert_some(...)` built-ins; `check A == B` | MISSING | COMPB-2 |
| E18 | the searched-mode "search assertion" (§13 O36, not adopted) | MISSING | COMPB-2 |
| E19 | `@each(...)` spelling (lean `@assert.each`) | MISSING | COMPB-2 |
| E20 | rev 2's `pad(n)` / `jstr` names | MISSING (minor; `unpadded` history names `pad(n)` origin only in the draft) | — |
BEYOND-R.9 TOTALS: 30 (T1-T6 counted as 6); carried 13, partial 2 (T9, E14), MISSING 15.

GRAND TOTALS B: expected 102; carried 70; partial 7; MISSING 25.

CORRECTION TO APPENDIX B's ARITHMETIC (checked by a python tally of the row lists above; supersedes the R.9 and GRAND totals lines): rows 23 ("left side first", carried by core #47 "the right side deciding") and 50 (backref within one literal: RULED capture, the sentence holds again: N/A) were left out of both lists. Correct R.9 counts: 109 rows = 39 N/A + 70 CANDIDATES; carried 55, partial 5 (37, 41, 68, 100, 102), MISSING 10 (7, 8, 12, 14, 31, 42, 43, 75, 79, 106). GRAND TOTALS B: expected 100; carried 68; partial 7; MISSING 25.

## PROBED-AND-HELD

- Population checked, (c): 98 provided-name rows (appendix A), every one grepped in all six documents and the hits read; 104 call-form names and ~90 dotted names in the draft screened to build it; the `:=` census (about 190 bound names) used to set aside worked-example bindings. HELD as fine: 49 names with a piece, 13 with a stated reason (cut, withdrawn, not provided, parked, formerly:). Named warnings (`pcrec.label.unset` etc.) treated as diagnostics, not provided names: the warnings table in core/diagnostics/warnings lists them (not audited name by name here). `labelled(x)` HELD: the draft offers it only "if the owner reads the rule as covering every provided macro", a conditional spelling, not a provided name. `kind()` HELD: the record says "a `kind()` built-in only if an example asks". `sys` HELD: his example module, recorded as such in library_details. `rx.word_char`/`rx.space`/`rx.any`/`rx.letter`/`rx.range`/`rx.none_of`/`rx.any_of` in lib/rx/classes come from `docs/design/rx_module.md`, outside my control's sources (draft + record): neither confirmed nor flagged; the draft itself names only `rx.digit`, `rx.alnum`, `rx.repeat`, the plurals.
- Population checked, (d): 109 §R.9 rows (70 candidates), 30 further named candidates from §8/§9/§16/§5.x, against all 190 `rejected:` items (parked 0: all 39 parked `rejected:` fields are empty, which is consistent with parked items carrying their history inside the quoted ideas-file text). HELD as fine: 68 carried with a reason and, in most, a witness run.
- The 586-hit rejection-word scan of the draft was READ for named candidates only; the many hits that re-state a narrowing, mark a row as "the record", or retire a draft reading of the evidence were not each mapped (stated plainly: not every one of the 586 hits is accounted for).
- Post-draft record (entries from line 4834): `limited` (lib + parked), the import-symbols forms (core/modules pieces with rejected lines #122-#125), `peek` default-set, other-holes/negated-class-hole/zero-in-sequence candidates (#84-#88, #41) — all landed.
- Longest witness used: none run (a census lens; no matcher runs).

CRITIC COMPLETE
