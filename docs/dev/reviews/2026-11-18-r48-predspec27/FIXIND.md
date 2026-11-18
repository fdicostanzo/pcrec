# FIXIND findings — critic round predspec27 (rev 27 of predicates_draft.md)

(Pre-created by the coordinator. This is YOUR OUTPUT file: append findings as you go.)

## Findings

Scope: R.1.16 ANSWERS CHANGED (A1-A16) and THE TYPE TABLE (T1-T21) of rev 27, each cell against its cited subsection; then a whole-draft grep for every term of each changed answer. Probes are TEXT probes (grep + diff of the frozen copies); answers are the draft's own printed runs (predspec27_model.out lines cited). MINIMUM WITNESS LENGTH: no new text pool was run (one libpcre2 attempt, the `(?J)` duplicate-name witness, could not run: pcre2h refuses non-unique names, 'non-unique substring name'); every witness below is a pattern/text the draft itself prints, or a 2-character hand witness stated with its derivation.

### FIXIND-1 — a second, different `left` already exists (§2.7, §8); T9 and A-table silent on it
CONFIRMED (quoted lines). Severity: answer. Effort: small (one A-row + T9 ground + a §R.8 question or a rename). Blast radius: §2.7 BODIES table, §8 standard filter modifiers, §13 O14, glossary "filter modifier" (line 3983), T9, spellings 29.
Location: R.1.16 T9 (line 2176); §2.7 line 4673; §8 lines 6058-6060.
- The draft ALREADY defines `left`: §2.7 "`left(n, S)`, `right(n, S)`, `mid(i, n, S)` | `left(n, S) := /${S & /(?s:.){${n}}/}(?s:.*)/` (LEAN; out of range: §13 O14)" — a FILTER MODIFIER (§8: "string positions `left/right/mid` with literal positions"): the texts whose first n characters are a member of S. Defined on GENERAL S, at compile time, today.
- Rev 27's T9: "string functions `left(rx, n)` ... (his placeholders) | rx SINGLE for the BUILT form | 'the leftmost two characters of an rx's strings' | ... a constant or a read: BUILT NOW; any other rx: UNDER CONSTRUCTION". A DIFFERENT operation (the prefix IMAGE of S, not a filter by prefix), the argument order reversed, and a different build status (§2.7's body works on any S now).
- Witness (hand, from the two definitions): `/${left("Columbus", 2)}/` on `Co`: T9 HOLDS (the image is "Co"). §2.7's `left(2, "Columbus")` = `/${"Columbus" & /(?s:.){2}/}(?s:.*)/` = an empty set ("Columbus" has no 2-character member) -> FAILS on every text. Same name, two verdicts. Conversely `X & left(2, /\d+/)` (§2.7, built, general S) would be "UNDER CONSTRUCTION" by T9's first-match row ("any other rx").
- Neither T9's ground cell nor any A-row nor §R.8 spellings 29 names §2.7/§8's `left`; grep `left(n` hits only line 4673. "Change my answers to match" covers an existing LEAN definition of the very function he named. Fix: an A-row (the §2.7 `left` meets T9: rename one, or state that §2.7's filter is `S2 & left(...)`'s composition), and mark §2.7/§8.

### FIXIND-2 — R.1.14 carries no REV 27 mark yet A6, A8, A13 cite it; it still states the old answers
CONFIRMED (grep). Severity: answer (AL2's printed answer vs the draft's T8 reading) + doc. Effort: small. Blast radius: R.1.14, §R.7, §R.9 MARKED SECTIONS.
Location: R.1.14 lines 1905-1925, 1979-1990; §R.7 line 2512-2513; `grep -n 'REV 27'` shows no hit between 1686 and 2037.
- Line 1918-1920 (unmarked): "What `+` does on operands that are NOT numbers is not stated by any ruling: THE DRAFT'S READING (the manager's lean in the record) a TYPE ERROR, addition being arithmetic". A8 says "the TYPE ground is gone (one type) ... an error would be of DOMAIN". The live R.1.14 sentence still gives the type-error reading.
- Line 1986-1987 (unmarked): "a matched value in a pattern position a LEAN, fleshed out in R.1.15 and asked as **value-hole**" — A4 RULED it.
- Lines 1913-1914 (unmarked) and §R.7 2512-2513 (rev 26 bullet, unmarked): "`rx.repeat(rx.digit, n + 1)`, n := [2, 4], is `(?|\d{3}|\d{5})` (AL2: WHOLE `123` HOLDS...)" and "now RULED `(?|\d{3}|\d{5})`". Under rev 27's own T8 ("by m1 an array the user writes: UNDER CONSTRUCTION") and **construction-line** (a) ("UNDER CONSTRUCTION: the error in every mode"), THE DRAFT'S READING now gives the compile-time "under construction" error for this program; the R.1.14 sentence gives a compiled pattern and a HOLDS. The §R.7 REV 27 "WHAT MOVED" paragraph (2517-2525) lists dollar-condition, backref-label and the value hole but NOT this move (a printed, RULED answer moving to an error under the draft's reading).
- §R.9's own row "array-lift's reach ... | R.1.14, §2.5, §5.4 | WIDENED" (line 2958) names R.1.14 and §5.4, while §R.9's MARKED SECTIONS list for rev 27 (2989-2992) omits both — and indeed neither carries a mark.

### FIXIND-3 — §5.4's `+ - * %` row (cited by A6) unmarked: "between numbers ... arithmetic on numerals"
CONFIRMED (quoted line). Severity: doc. Effort: trivial. Blast radius: §5.4 THE ONE OPERATOR TABLE (the grammar summary readers consult first).
Location: §5.4 `+` row (line ~5572): "`+` `-` `*` `%` | between numbers [REV 26.1 ... on ARRAYS they combine on the product, **array-lift** ...] | arithmetic on numerals (§2.5)". A6 cites "§5.4's `+` row" and changes its meaning to general regex (`\d + 1` = the numerals 1..10, T8) with a build line; T10 makes `+` a joining candidate. The row has no REV 27 mark and still says "between numbers". Likewise §2.5's RULE "`+ - * %` are arithmetic only, on numbers (§2.1)" (line 4305): its REV 27 marks (4307, 4314) cover dollar-condition and value-hole only, not A6's `\d + 1`.

### FIXIND-4 — A11 cites §4.4 RULE and §11's computed-label sentence; both unmarked, §11 still states the old answer
CONFIRMED (quoted line). Severity: doc (a contradiction a reader meets first). Effort: trivial. Blast radius: §4.4, §11 STRING SETS.
Location: §11 line 6315: "A computed label's value is a VALUE, not a pattern (§4.4)"; §4.4 RULE line 5209. A11 says it "becomes" "a computed value is a one-string rx known at run time, like a read", and §2.1 says an rx IS a pattern ("an **rx** (a set of strings, extensional, §11; a pattern)"). So 6315 now contradicts A11 + §2.1, with no [REV 27] mark or R.1.16 pointer. Also §2.1 (line 4080) calls a match-dependent binding a MACRO whose operand is the pattern — A11's "one-string rx" names a different kind; the A-row does not say which of the two §2.1 kinds a computed label now is (T1 keeps macro its own kind).

### FIXIND-5 — "every row also in §R.9" is false: 8 of 16 A-rows have no §R.9 row
CONFIRMED (grep). Severity: doc. Effort: small. Blast radius: §R.9 (the reversal ledger readers use).
Location: R.1.16 line 2192 ("every row also in §R.9"); §R.9 rev 27 rows lines 2953-2958.
- §R.9 carries six rev 27 rows: dollar-condition (A1/A2/A15), `\k` reads the label (A9/A14), value-is-pattern lean (A4), R.1.15 (1) (A3), the `${$y}`=`\k<y>` control (no A-row), array-lift's reach (A6).
- Missing: A5 (value-filter answered), A7 (constant gains a run-time twin), A8 (plus-operands' TYPE ERROR ground gone — a reversed reading, exactly §R.9's subject), A10 (carried-capture form's reach narrowed), A11 (computed value becomes an rx), A12 (m5 not supported), A13, A16 (UNCHANGED rows; arguably need none, but the sentence says "every row"). A8, A10, A11 are real changes with no ledger row.

### FIXIND-6 — A10 drops rev 27's own "for one name" qualifier: `\k<h>` is NOT the carried-capture form under duplicate names
CONFIRMED (the draft's own printed run). Severity: design (a stated identity that fails on the open case). Effort: trivial (add "for one name; two groups of one name: **same-name-twice**"). Blast radius: A10, spellings 3, R.1.7 (b).
Location: A10 (line 2205): "inside rx text `\k<h>` now IS PCRE's capture (backref-label); the carried-capture form is still REQUIRED where a `$` reads ... only its reach inside literals is now met by `\k`". The carried-capture form is defined (spellings 3, line 2803; R.1.7 (b)) as "the value from the last time a group of the name was SET". R.1.7 (b)'s own REV 25.1 text (lines 1192-1195): under `(?J)` `\k<x>` reads the FIRST SET group: `(?J)(?:(?<x>a)|(?<x>b))+\k<x>` WHOLE `abba` HOLDS, `abbb` FAILS (rev 25.1 PART I I1); the carried-capture form (last set = `b`) gives the reverse. Rev 27's R.1.7 (b) mark says "HOLDS again for ONE name; two groups of one name are **same-name-twice**" and the BL m3 run (model.out line 23) shows first-set vs last-set part on 4 / 4 / 4 of 341. A10 states the identity without the one-name qualifier, so "its reach inside literals is now met by `\k`" is false exactly where same-name-twice is open. (Run attempt: pcre2h raised "non-unique substring name" on the `(?J)` pattern, so the witness is the draft's printed rev 25.1 run, not re-run.)

### FIXIND-7 — T13 drops rev 26.1's "unless the label is finite" exclusion for a read in a COUNT
CONFIRMED (diff). Severity: design. Effort: small. Blast radius: T13, A13, construction-line (c), R.1.15 (9).
Location: T13 (line 2180): "a read, `\d{${$n}}`: UNDER CONSTRUCTION (THE DRAFT'S READING; the count rulings name no run-time count; R.1.15 (9))". Rev 26.1's R.1.15 (9) (diff_rev26.1_to_rev27 line 162-164, removed): "a match value in a COUNT position (`\d{${$n}}`) would make the count known only at match time, which the count ruling's 'finite enumeration' excludes UNLESS THE LABEL IS FINITE: NOT STATED". Rev 27's (9) and T13 drop the finite-label case, while R.1.15 (7) keeps the parallel point for the pattern hole ("For a FINITE label (`\d{4}`) the same program has a compile-time spelling ... a choice of the compiler, no answer moves"). For `(?<n>[23])-\d{${$n}}` the counts {2, 3} are FINITE and compile-time enumerable (T13's own NEEDS), so by T13's compile-time column it is BUILT NOW; by its run-time column UNDER CONSTRUCTION. The row states no rule choosing between them; rev 26.1 named the gap, rev 27 erased it.

### FIXIND-8 — T20 and T12 state as fact what R.1.15 marks UNRULED (unset, width): a dropped qualifier
CONFIRMED (quoted cells). Severity: doc (the type table claims "a cell that rests on a reading says so"). Effort: trivial. Blast radius: T12, T20.
Location: T20 (line 2187): the reads "each yields a SINGLE string at run time, or none when unset | BUILT NOW". R.1.15 (3) (line 2064-2067): unset is UNRULED, asked **unset-in-hole**, "THE DRAFT'S READING: FAIL ... whether an unset read is no string or the empty string is the question"; R.1.15 (5) even reads unset "as EMPTY for this run only". T20 states "none when unset" with no reading mark and no pointer. T12 (line 2179): "the expression's strings as LITERAL TEXT ... nothing = the position fails | BUILT NOW, both forms (value-hole RULED)" — R.1.0's MATCH VALUE row (line 834) keeps "width and unset: **numeral-width**, **unset-in-hole**"; T12 drops both. Same table's header: "a cell that rests on a reading says so".

### FIXIND-9 — T10's NEEDS "as T8" makes JOINING require SINGLE NUMERALS
CONFIRMED (cell text). Severity: doc. Effort: trivial. Blast radius: T10.
Location: T10 (line 2177): JOINING two strings | NEEDS "as T8"; T8's NEEDS (line 2175): "SINGLE numerals for the BUILT form". Joining's own witness, `$y . "End"` / R.1.15 (12) `/(?<y>\d)-${$y . "E"}/`, joins a non-numeral ("E"). The intended NEEDS is presumably "SINGLE strings for the BUILT form"; as written the row refuses its own example.

### FIXIND-10 — "first match by row" in a table that mixes OPERATIONS and POSITIONS: an expression in a hole reaches only one row
SUSPECTED (structure; confirm by asking the table which row decides `\d{${n + 1}}`, n := [2, 4]). Severity: design. Effort: small (state that an operation row and the position row it stands in BOTH apply, the stricter status winning, or split the table). Blast radius: the TYPE TABLE, **construction-line**, PART TT.
Location: line 2162 "one row per operation and per hole position the draft has; first match by row". Every hole value is an expression in a position: `${$y | "x"}` matches T1 first and never reaches T12 (whose "under the options at the hole; nothing = the position fails" is the hole's rule); `\d{${n + 1}}`, n := [2, 4], matches T8 first (a user array: UNDER CONSTRUCTION) and never T13 (FINITE compile-time counts: BUILT NOW). PART TT's rows (model.out 65 "+ on finite -> UNDER CONSTRUCTION", 71 "count-hole on finite -> BUILT") give both statuses for that one program; **construction-line** (a)'s "BUILT `(?|\d{3}|\d{5})`" candidate needs T13 to be read. First-match semantics cannot express a composition.

### FIXIND-11 — new run-time form `$x & <5` as an `&` OPERAND: WHEN the read happens is unstated (the "stands AFTER every pattern operand" rule is for CONDITIONS)
SUSPECTED (sibling field unstated; confirm with `($x & <5) & /(?<x>\d+)/` and with a P whose x is set on several paths). Severity: design. Effort: small (one sentence: a read in an `&` operand reads after every pattern operand, as a condition does; or the reverse). Blast radius: T2, A1, A15, §4.1, §2.5's `($x + $y) & <50`.
Location: A1 / T2 ("as an `&` operand, `$x & <5` holds where the stretch is x's text and x < 5"); R.1 PLAIN WORDS (line 746-747): "A condition written in an `&` chain stands AFTER every pattern operand of that chain (it reads the labels of all of them), wherever it is written in the chain". Rev 27 moved `$x & <5` from a (rejected) condition to an RX operand; the placement rule names conditions only, and R.1.0's `&` OPERAND row says "each operand its own pattern on the stretch". UT1 (model.out 39-43) runs only `P & ($x & <5)`, P written first. Written first, `($x & <5) & P`, the draft states no reading point; and if P reaches its stretch on several paths, whether the read follows the path being tried (backtracking into P) is likewise unstated (a condition's is: "goes back to its most recent choice").

### FIXIND-12 — new run-time arithmetic on a read: a non-numeral read is unstated (A8's "DOMAIN error" cannot be a compile error at run time)
SUSPECTED (sibling field unstated). Severity: design. Effort: small. Blast radius: T8, T9, R.1.15 (2), A8, plus-operands.
Location: T8 (line 2175) "a read: BUILT NOW"; A8 (line 2203): "the error, if kept, is one of DOMAIN, not of type". For a constant the domain is known at compile time; for a read it is not: `/(?<y>\w+)-${$y + 1}/` on `ab-ab1` (the label `ab`). No row, no R.1.15 item and no §R.8 question says whether a run-time domain miss FAILS the position (as "an expression that yields nothing"), is a compile error wherever the label CAN be a non-numeral (as unset-in-hole's third candidate), or something else. The same gap for `left($y, n)` with n past the read's length (T9 BUILT NOW on a read; §13 O14 "CLAMP vs strict false" is §2.7's `left`, see FIXIND-1).

### FIXIND-13 — stale "open" markers the A-rows' sources leave untouched (§R.8)
CONFIRMED (quoted lines). Severity: doc. Effort: trivial. Blast radius: §R.8.
- §R.8 RULED list, **value-is-pattern** (line 2663-2665, unmarked; A4 cites "§R.8 RULED rev 26 (value-is-pattern)"): "a matched value in a pattern position a LEAN, now **value-hole** (asked, below)". Now RULED (A4).
- §R.8 remaining table, **rx-module** row (line 2792, unmarked): "[REV 26: ... open: **value-hole**, **other-holes**, **plus-operands**, **anything-text**, **backref-label**, **zero-in-sequence**]". value-hole and backref-label are ANSWERED in rev 27 (rows 2752, 2756).
- §R.11 row 85 (line 3227, unmarked): "(3) LEAN, fleshed out (R.1.15), asked **value-hole**" (the ruling table's own "what the draft did" column; rows 120-124 were added but 85 not pointed on).

### FIXIND-14 — §4.1 RULE and §5.4 `$` row still call `$x` "the CAPTURED STRING" while rev 27 makes capture and label two different values
CONFIRMED (quoted lines). Severity: doc (term now ambiguous by ruling). Effort: small. Blast radius: §4.1, §5.4 `$` row, glossary "captured string" (line 3969).
Location: §4.1 line 4866: "`$x` = the CAPTURED STRING of this match (a one-string set, context-free, §11) for a set-once label; for a REPEATED label, one captured string per iteration"; §5.4 `$` row (5575): "For a GROUP label the value is its CAPTURED STRING (`$year`)"; glossary 3969: "**captured string** | `$x` for a GROUP label: the text it captured". Under backref-label (RULED) and R.1.15 (8)/(10)(a), "capture" now names PCRE's carried value (`\k<y>`), and `$y` reads the LABEL; they part (2 / 2 / 2 of 21,845, `3-3;-3;`; model.out 35). The REV 27 mark at 4869-4870 covers only the `${$x}` insertion and dollar-condition; the "CAPTURED STRING" definition of `$x` sits unmarked beside it (rev 25.1 marked §5.4's iteration clause stale, not the word). A reader taking §4.1's definition reads `$y` as the capture, the reading rev 27 withdrew (the "WITHDRAWN manager reading" of the discussion entry).

## PROBED-AND-HELD


HELD (each checked, no finding):
- A1/A2/A15 (dollar-condition): every location the rows cite carries a [REV 27] mark (§R.2 row 2253, §4.1 4870, §0.1 L28 3634, §R.8 RULED list 2641, §R.11 row 62 3202, §2.5 4307); A1's numbers match model.out UT1 (lines 39-43: 0 / 0 / 0 and 1 / 132 / 132 of 364, WHOLE `3-`). 4 sites + 6 marks.
- A3 (R.1.15 (1)): diffed against rev 26.1's (1) (diff lines 129-132): the CHANGED sentence is quoted exactly; the VH3 answer (`1.5-1x5` FAILS) kept. 1 of 1.
- A4: R.1.0 MATCH VALUE row (834), §R.8 value-hole (2752), the seven live uses (§0.1 L33, §2.5, §4.1, §11, §13 O27, O34, captures lean): marked (except the §R.8 value-is-pattern RULED bullet, FIXIND-13).
- A9/A14 (backref-label): R.1.7 (b) (1202), R.1.13 REFERENCES (1686), §R.6 (2434, 2437, 2438), §R.8 (2756) marked; A9's 6 / 66 / 66 of 364 equals model.out BL m1 (line 16); R.1.13's (1)-(3) restated without loss against rev 26.1.
- A6/A7/A12/A13/A16 cells vs their subsections: A6's 1,111 equals UT3 (model.out 52); A7's sentence kept verbatim at R.1.12 (1541) and §6.1 (5690), "kept" so unmarked is right; A12 matches §R.8 value-test (2770) and UT2; A13 matches R.1.0 COUNT row + T13 (but FIXIND-7); A16 matches R.1.7 (a).
- "`${$y}` equals `\k<y>`": all hits (16, 2084-2091, 2957) carry the narrowing; VD2 counts equal model.out 35-36.
- "not a pattern but a match": 8 hits, all marked or inside A-rows/§R.9/§R.11 record.
- "type error"/"TYPE ERROR": 9 hits; all marked or record EXCEPT R.1.14's 1918-1920 (FIXIND-2). 1981 and 2855 are rev 25/25.1 history lines inside dated brackets.
- "value-filter": 2 hits, both rev 27.
- "last reference as labels": 1656 (the quote, record), 1693 (rev 27 narrowing), 2204, 2937 (§R.9 rev 26 row: the WITHDRAWAL of readings (a)/(d), still true).
- "reads the label": 21 hits; the ones about `\k` are marked (1202, 2954) or describe the CONDITION/`$x` reading, which A16 keeps; 5026 (§4.3) already says `\k<x>` reads the capture (rev 24.3).
- T1, T2, T5, T6, T7, T11, T14, T17, T18, T19, T21 against their cited subsections: no disagreement found (T3's `!` on a condition is a pre-rev-27 §2.1 vs L30 matter, not rev 27's).
Counts: 16 A-rows x their cited locations (~45 sites), 21 T-rows, 14 term greps over 9,333 lines. No text pool run (see the scope note).

CRITIC COMPLETE
