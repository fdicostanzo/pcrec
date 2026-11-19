# RULING findings — round predspec29 (r54)

## Findings

### RULING-1 — a value hole `${$y & <5}` is put under the dollar-diagnostic warning, but the ruling was checked only where the suggestion is harmless (SUSPECTED, design)
- Location: §R.2 dollar-condition row, line 2661 ("a value hole `${$y & <5}` is the same form and draws it"); model PART DD line 123. The record is "2026-11-19 OWNER RULING — dollar-diagnostic", reading (a).
- His words: "the form $x & .. should just get a warning". The manager's reading (a), "for the next lane to test", says the warning "fires wherever the form is written, including where it is right", and justifies that with ONE witness, an `&` OPERAND (`/(?<x>\d+)/ & ($x & <5)` equals `(x: <5)`, "so the suggestion is harmless there"). The warning "points at `(x: S)`".
- What rev 29 does: it extends the warning to a VALUE HOLE. R.1.15 (12) prints `/(?<y>\d)-${$y & <5}/` as a meaningful form ("the read or NOTHING"). There, swapping in the suggestion `(y: <5)` changes the answer: a condition consumes nothing.
- Repro (`RULING/dh.py`, python, alphabet `37-`, length <= 5, 363 texts): `/(?<y>\d+)-${$y & <5}/` and `/(?<y>\d+)-${(y: <5)}/` differ on 2 WHOLE texts (`3-`, `3-3`; minimum witness length 2). The model's check only tests the trigger; it never compares the hole form with its suggestion.
- What to do: either state this as THE DRAFT'S READING (where the form fires; the record gives the manager only the wording and silencing, not the scope), or narrow the warning to the `&`-operand place. Either way the warning's pointer must not offer a rewrite that changes the meaning.
- Effort: small. Blast radius: §R.2, R.1.15 (12), A32.

### RULING-2 — §2.5 decides on its own which expressions count as the warned form (CONFIRMED, doc/scope)
- Location: §2.5 RULE, the [REV 29] bracket (line ~5050): "`($x + $y) & <50` is that form only where a read is filtered directly".
- Neither his words ("the form $x & ..") nor the record's readings say whether a computed expression over reads, filtered by a set, is "the form". The sentence settles that question but is not marked THE DRAFT'S READING or the manager's call. The model's trigger (`\$\w+\s*&`) does not test it either.
- What to do: label it as a reading, or list it under §R.8 as a scope detail for the manager. Effort: trivial.

### RULING-3 — plus-operands: the manager's call is written into the RULED sentence (CONFIRMED, doc/scope)
- Location: R.1.14 line 2042 ("RULED (the second sentence): ... where the compiler KNOWS the whole result is nothing ... a WARNING") and R.1.16 T8 line 2561 ("a WARNING only where the whole result is known nothing ... silent on `\w + 1`").
- His words: "a warning if known". The record, "2026-11-19 OWNER RULING — plus-operands", reading (b), says that whether the warning speaks when only SOME members are outside the domain "is the manager's call: no, only when the whole result is known to be nothing". Per-member filtering of a class or array operand is also "NOT his words" (the entry "asked plus-operands", reading (d)).
- Rev 29 prints "the WHOLE result" and per-member filtering inside the RULED bracket, with no "THE MANAGER'S CALL" or "reading" mark. Its sabotage t21 tests that call, not the ruling.
- Smaller cases of the same kind: "`+` never joins (joining is the sequence operator)" (R.1.14), and T10's "it is the sequence operator's spelling". "Joining stays the sequence operator's" is the record's reading (c), for the lane to test. Only "`+` does not join" is his.
- What to do: split each sentence into RULED, then THE MANAGER'S CALL or reading. Effort: small. Blast radius: R.1.14, T8, T10, A36.

### RULING-4 — `J` and numbered references across a hole are stated as consequences of same-name-count, but they are the manager's readings (CONFIRMED, doc)
- Location: R.1.14 HOLE-READING (1), line 1926 ("'its own group numbering' STANDS, `\k<h>` and `\1` included (**same-name-count** RULED, R.1.15)"); R.1.15 line 2211 ("`J`: closed by same-name-count (below)"); §11 line 7093 ("`J` has no effect across a hole (same-name-count)"); the §R.8 flags-scope row, line 3360 ("`J` closed by same-name-count").
- The record ("OWNER RULING — same-name-count") lists "(a) `J` has no effect across a hole ... closed by consequence" and "(b) an inserted literal's NUMBERED references are its own too" under "The manager's readings, for the next lane to test". The "backreferences, not labels?" entry says the ruling covers what the OUTER `\k<h>` counts and reads. Only A30 labels these as READING (12 and 13, SUPPORTED). The other four places present them as ruled.
- Also, line 2211's "(below)" points at nothing: R.1.15 has no later same-name-count passage. Line 1926's "R.1.15" pointer is circular the same way. The `J` result lives in R.1.16 A30.
- What to do: mark these as the manager's readings 12 and 13, SUPPORTED, and point at A30. Effort: trivial.

### RULING-5 — "LESS the six RULED" undercounts: plus-operands is also on the list being subtracted from (CONFIRMED, doc)
- Location: §R.8, REV 29, line 3298: "STILL ASKED after rev 29: as after rev 28.1, LESS the six RULED, PLUS the new rows."
- The list it builds on (line 3232, "STILL ASKED after rev 28": **plus-operands**, ...) holds plus-operands, and rev 29 RULES it (the seventh, by rulings file R1). Read literally, plus-operands stays asked.
- Also, dollar-diagnostic was on rev 28's GAPS list and rev 28.1's ASKED NEW list. It is one of the six, so it is fine.
- What to do: write "LESS the seven RULED (the six and plus-operands)". Effort: trivial.

### RULING-6 — class-order: the record REPLACES the codepoint lean outright; rev 29 keeps it for the array interface, and two live sentences still call it the LEAN (CONFIRMED, design/doc)
- Location: changelog line 14 ("REPLACED for lifts"); §5.5 RULE line 6429; §5.5 STATUS line 6442, whose live tail after the brackets reads "Codepoint order for class members: LEAN (review OWN-10)"; §0.1 L26 line 4377; E-SEP line 7795; §R.8 class-index line 3365.
- The record ("OWNER RULING — class-order", "The rule as asked"): "a character class's members ... have NO order, as in PCRE; ... The draft's CODEPOINT lean (§5.5) is replaced." It does not say "for lifts". Rev 29 narrows "replaced" to lifts and keeps codepoint for `.index`/`each` as THE DRAFT'S READING, which it asks as class-index.
- Asking class-index is legitimate. The record's reading (a), "the order among equal lengths is never observable", is wrong for the array interface, and rev 29 found that. The faults:
  - (i) Rev 29 does not say that the narrowing is the lane's own, against the record's wording.
  - (ii) The class-index row's DRAFT'S READING cell cites "§5.5's sentence, kept for the array only". That sentence is the lean the record says is replaced.
  - (iii) §5.5 STATUS still ends "Codepoint order for class members: LEAN" unmarked, and the rev 28 bracket's "stays a LEAN" survives as a reader.
- What to do: label the array-interface codepoint as a reading kept despite "replaced", pending class-index. Mark STATUS's tail. Effort: small.

### RULING-7 — class-order: two of the manager's readings sit inside the RULED paragraph without a mark (CONFIRMED, doc)
- Location: §5.5 STATUS [REV 29] bracket, line 6442: "NESTING: `(1|9) + \d` keeps the alternation's order and sorts each choice's class results ...; equal strings from different members are ONE result (`\d * 0` = `0`)."
- The record lists these as the manager's readings (b) and (d), "for the next lane to test". Row 164 says readings 8, 9 and 11 are SUPPORTED, and the same paragraph labels reading 8 ("the manager's reading 8, SUPPORTED"). Nesting and merging are not labelled, so they read as ruled.
- Nesting follows closely from "Alternations ... keep their own order", which was part of the rule as asked. Merging equal results is not in the asked text.
- What to do: add "(the manager's readings 9 and 11, SUPPORTED)". Effort: trivial.

### RULING-8 — the declared fold range does not match the §R.11 rows it names (CONFIRMED, doc)
- Location: changelog line 14 and the header note at lines 748-751: the fold runs "from '2026-11-18 OWNER, discussing padded-order (not a ruling)' ... §R.11 rows 155-171".
- Rows 155 ("a question on padded-order", "padded-order: whats the exact width rx") and 156 ("MANAGER — after lane predspec281") are the two record entries BEFORE that start (COND-FAMILY lines 4450, 4461). They are folded but outside the declared range. Their quotes and classes are correct: QUESTION; no owner words.
- Row 171 is not a record entry: it is "(the lane's rulings file)".
- What to do: say "rows 155-156 fold the two earlier entries rev 28.1 did not reach". Effort: trivial.

### RULING-9 — §R.11 row classes drop part of the entry's class (CONFIRMED, doc, minor)
- Row 157: the record says "Class: OBSERVATION / IDEA"; the row says "IDEA".
- Row 160: the record says "DISCUSSION with a LEAN ...; a PRINCIPLE stated: an rx that cares about a flag sets it itself and does not assume"; the row says "LEAN" only. The PRINCIPLE is not cited anywhere in the draft (0 hits for "responsibility").
- Row 172: the record says "RECOLLECTION ..., an OBSERVATION ..., and an IDEA / PROPOSAL"; the row says "RECOLLECTION + IDEA".
- Row 173 states no class. The record classes it sentence by sentence: QUESTION; the join answer; OBSERVATION; IDEA.
- None of these misfolds a rule. Effort: trivial.

### RULING-10 — paraphrases printed in quotation marks as if they were record text (CONFIRMED, doc, minor)
- §2.7, line ~5445: the manager's reading is quoted as "equal for EVERY argument ordered by length". The record's words are "any-length-first equals fill-each-string for every argument whose order is by length (longest first or shortest first)". The paraphrase also drops the "(longest first or shortest first)" that the NOT-SUPPORTED verdict turns on.
- §R.8 class-positions, line 3364: "quantifiers ... their own order" and "quantifiers ... keep their own order" quote the MANAGER's "rule as asked" ("Alternations, quantifiers and arrays the user writes keep their own order") and attribute it to "the ruling". That is acceptable, because the rule as asked is what "longest" answered. Still, a reader may take it for his words.
- Every OWNER quote I checked is verbatim (PROBED-AND-HELD).

## RULED STATE AFTER REV 29

| fold-range entry (COND-FAMILY) | class (record) | state after rev 29 | where the draft carries it |
|---|---|---|---|
| 11-18 a question on padded-order (before the range) | QUESTION | stands (answered) | §R.11 row 155 (line 3991) |
| 11-18 MANAGER after lane predspec281 (before the range) | no owner words | lazy-infinite fact WITHDRAWN by rev 29 | §R.11 row 156; §2.7 line 5433; A35 line 2619 |
| 11-18 discussing padded-order | OBSERVATION / IDEA | cited, not ruled | row 157; §2.7 line 5433 |
| 11-19 RULING padded-order | RULING + CONDITION | FOLDED; condition confirmed (reading (b)); reading (a) NOT SUPPORTED as worded | §2.7 line 5433; §R.8 line 3357; A28 line 2611; R.6 line 3590 |
| 11-19 flags-in-filter: what "flags propagate" meant | RECOLLECTION | not ruled; REACH = THE DRAFT'S READING; OPEN (confirm) | R.1.15 line 2198; §R.8 line 3359; row 159 |
| 11-19 flags and a binding in a hole | DISCUSSION + LEAN + PRINCIPLE | lean = the draft already; readings 5, 6 SUPPORTED; principle uncited | R.1.15 line 2198; row 160 |
| 11-19 RULING flags-scope | RULING (s1) + OBSERVATION (s2) | FOLDED (i m s inherited; U x xx n not); s2 kept as an observation | R.1.15 line 2198; R.1.14 line 1926; §11 line 7093; T12 line 2565; §R.8 line 3360; A29; L32 line 4383 |
| 11-19 class-order: longest first | QUESTION / IDEA | cited | row 162 |
| 11-19 class-order: "class only" | QUESTION | answered | row 163 |
| 11-19 RULING class-order | RULING | FOLDED for lifts; class-positions OPEN (new); class-index OPEN (new; see RULING-6) | §5.5 line 6442; T8 line 2561; R.1.15 (7) line 2351; §R.8 lines 3358, 3364, 3365; A31 |
| 11-19 RULING dollar-diagnostic | RULING | FOLDED (form-keyed warning; group-rx reading dropped); scope at holes and expressions see RULING-1, RULING-2 | §R.2 line 2661; §0.1 L28 line 4379; §4.1 line 5684; A32; §R.8 line 3345 + dollar-diagnostic row |
| 11-19 RULING number-edges | RULING | FOLDED; `% 0` diagnostic = GAP | R.1.16 line 2532; R.1.15 (2) line 2281; §R.8 row; A33 |
| 11-19 RULING same-name-count | RULING | FOLDED for `\k<h>`; `$h` withdrawn; J and `\1` = readings (see RULING-4) | R.1.13 line 1780; R.1.14 line 1926; §R.8 row; A34, A30 |
| 11-19 same-name-count: backreferences, not labels? + MANAGER CORRECTION | QUESTION | "(and `$h`)" withdrawn; no surviving reader found | R.1.13 line 1780; row 168 |
| 11-19 exported and private labels | RECOLLECTION + LEAN | already ruled (export-rule); inner-label-read not asked | R.1.13 T-b line 1757; row 169 |
| 11-19 building rx from many bindings | OBSERVATION + DIRECTION | no rule changed; T-a worked, surprises reported | R.1.13 T-a line 1738; row 170 |
| 11-19 asked plus-operands (`m(g & /\d+/)`) | RECOLLECTION + OBSERVATION + IDEA | cited, not folded | §R.8 REV 29 line ~3280; row 172 |
| 11-19 `+` numbers only; class as base | QUESTION; join answer; OBSERVATION; IDEA | join CLOSED (folded); base idea cited | R.1.14 line 2042; T10 line 2563; row 173 |
| 11-19 base idea: ordered symbol sets | DISCUSSION / IDEA | cited, not folded | row 174; R.1.14 (as "ordered symbol sets" in the direction) |
| 11-19 RULING plus-operands | RULING (s2) + DIRECTION (s1) | FOLDED (nothing; warning if known); direction not in force; partial-warning = manager's call (see RULING-3) | R.1.14 line 2042; T8 line 2561; T10; §R.8 line 3332; A8, A36; §5.1 rows 4-5 lines 6371-6372 |

## PROBED-AND-HELD
- QUOTES. I extracted every double-quoted string from the + lines of `rev28.1_to_rev29.diff` (joined, whitespace normalized) and matched each against the record (`RULING/q.py`). Every OWNER quote matches verbatim:
  - the rulings: padded-order, flags-scope (both sentences), class-order, dollar-diagnostic (full), number-edges, same-name-count, plus-operands (full and the elided changelog form);
  - "i don't think + should ...", "rx inherits the flags of the surrounding rx", "one could make a case that only i should be inherited", "i say the strategy is to use labels as they are defined ...", "putting the length in front would help order", "i meant, putting any length", "padded-order: whats the exact width rx", "what do you mean class only? like \d ?", "example(g & /\d+/) := blah", "this logic might be used for the arithmetic", "if that works".
  - The two elisions ("for now ... we are", "... excepting that U") keep the meaning. The quote-like strings that did not match are draft-internal text or paraphrases (RULING-10).
- IDEAS NOT FOLDED: the three entries between "building rx" and the plus-operands ruling (restriction by `&`, class as base, ordered symbol sets) are cited only, never stated as rules (rows 172-174; the REV 29 list at §R.8). Flags-scope's second sentence is kept as an OBSERVATION, with `m` and `s` still inherited. Plus-operands' first sentence is kept as a DIRECTION, not in force.
- The withdrawn "(and `$h`)": grep for `and \`$h\`` finds only R.1.13, which states the withdrawal, and row 168. No surviving reader.
- Withdrawn "`n`, `U`, `xx` and `J` propagate like `i`": each reader (line 2186, record-in-bracket) is followed by a REV 29 reversal; §11's "every flag" (line 7093) is followed by a REV 29 bracket.
- Withdrawn "a read stands for its group's rx": the readers at lines 35 and 2994 are past changelogs (record). §R.2, A21 and L28 carry REV 29 marks.
- Withdrawn lazy-infinite claim: line 5431 is followed by the withdrawal at line 5442; the §R.8 row is marked as the record.
- number-edges: the draft's "no compile error of its own for a written `% 0`" and "everywhere" match the record. Reading (14) is reported NOT SUPPORTED, as a GAP, with no new rule.
- padded-order: "the body's stated behaviour" is applied to the sparse shortest-first `1|0123`. The record's ruling text covers that ("where the argument lists a shorter string before a longer one"), so it is not a stretch.
- class-positions is not answered by the record (reading (c): "NOT covered by his words; if the readings part, it is asked"). Asking it is authorized. class-index is a genuine gap: reading (a) "never observable" misses `.index`.
- flags-in-filter: no ruling answers it. The flags-scope ruling's table names "an rx inserted in a hole (a direct literal or a binding)", not an `&` inside. Keeping it as a confirm is correct.
- §R.11 rows 155-175: each fold-range entry has its row, and the RULING/QUESTION/RECOLLECTION/DIRECTION classes are right except the omissions in RULING-9.
- dollar-diagnostic value-hole witness (RULING-1): 363 texts over `37-`, length <= 5; minimum witness length 2.

CRITIC COMPLETE
