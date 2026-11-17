# CRITIC ruling — round predspec242 (rev 24.2 of predicates_draft.md)

## Findings

<!-- appended below, one per finding -->

### RULING-1 — the preamble cites an entry name the record does not have (CONFIRMED; doc; effort trivial; blast: §R preamble only)
§R preamble lines 467-468: "COND-FAMILY, the entries from "OWNER LEAN — pass-own-labels" to the end of the file". No
such heading exists. The record's entry (CF 2385) is headed "OWNER LEAN — a loop pass has its own labels", and the
HIS WORDS in it were said under the slug joint-last-pass ("joint-last-pass: I think the expectation is that each loop
has its own..."). Grep: `OWNER LEAN` matches only CF 1256, 1638, 2101, 2385. Fix: cite the real heading.

### RULING-2 — value-point is asked, but a RULED rule already decides it (CONFIRMED by hand derivation; design; effort small; blast: R.1.7 INSIDE THE BODY, §R.8 value-point row, R.11)
§R.8 line 1102 asks **value-point** (does a label count as the pass's own from its group's close, or only once the pass
ends?). It also labels "group close" THE DRAFT'S READING (R.1.7 lines 750-751). But after-loop-read RECORD (1) (CF
2461-2462) RULED "a condition written INSIDE a loop, on the item, is judged in every pass: that is how "all" is
written", and the worked example he accepted is `late := time & ((h, m): >= (9, 30))`, `/(?:${late},)*/` (CF 2456),
where the condition comes BEFORE the pass's `,`. Under "pass end" that condition can read no label of its own pass, so
"a loop of (times after 9:30)" fails on every non-empty text. The row's own cost column says so: "pass end: ... every
§R.4 item spelling FAILS". So the "pass end" candidate contradicts a ruling, and group close follows from RECORD (1) and
from R.1's own regex model ("reads the labels set so far"). That makes it a reading CLOSED by a ruling, not an owner
question (G24-5 asks only where no model decides). Missed too: the record's MINE for lane predspec241 (CF 2405) reads
"where a label takes its value from the capture (the end of each pass)", which is the opposite parenthetical. The
draft never mentions it. The next revision should say the record's "(the end of each pass)" is superseded by RECORD
(1)'s example.

### RULING-3 — some-own and hits-pass are asked, but the evening's rulings entail both (CONFIRMED by derivation; design; effort small; blast: §R.8 two rows, R.1.9, R.11 row 36/37)
§R.8 lines 1104-1105 ask **hits-pass** (is a hit of `occurrences` a pass?) and **some-own** (do `some`, `occurs.*`
and `h[2]` read each pass's own labels?). For both, the draft's reading is "yes".
(i) hits-pass: regex-settles (4) (owner: "yes settled") RULED that `occurrences` is the ONE-PATTERN lazy-gap LOOP, so a
hit is a pass of a loop. after-loop-read RECORD (3) (CF 2465-2466) RULED that a loop pass has its own labels, with no
exemption for any loop. R.1.9 line 786 already states it as fact: "(R.1.7: a hit is a pass)". The only alternative,
"No", is the row's own words: "an exception to R.1.7 nobody asked for". exception-rule (CF 2367-2371) RULED that
exceptions "should be requested by using those features explicitly". So "No" is excluded by a ruling.
(ii) some-own: the pass table lists passes, and RECORD (3) defines each pass's labels as its own. The engine agrees:
0 of 364 move between rev 24.1 and rev 24.2. The row's own last column says "No reading carries a value across passes
inside the pass table".
So both are CLOSED (entailed by the rulings), in the same way three-valued is closed by its regex model. Asking the
owner rulings he has already made costs his attention and makes R.8 look more open than it is.

### RULING-4 — same-results is asked, but the black-box principle, read literally, entails it (CONFIRMED by derivation; design; effort small; blast: R.1.3, §R.8 same-results row)
R.1.3 lines 588-599 keep rev 24.1's "the same PATHS with the same labels" as THE DRAFT'S READING. They ask the owner,
as **same-results** (line 1106), whether the principle is instead "the same RESULTS in the same order with the same
labels". The owner's ADDENDUM (CF 2482-2484, his words): "from the perspective of the condition, an rx is a black box
that exposes labels"; RECORD: "a condition reads nothing else of it". Read literally, two patterns that offer the
same results with the same labels cannot be told apart by any condition, so the "results" form FOLLOWS from his
principle. The only things that open the box are explicit requests (the pass forms, the hit list), which §R.6 already
lists as exceptions. The "paths" form is not a rival answer either: same paths imply same results, so it is strictly
weaker and true under both. The question has a single answer. Only MINE (a), "in the same order", is the manager's
addition; it is branch-scope (ii), RULED. Status should be: the restatement is a derivation of the ruled principle,
CLOSED, with its carve-out (requests). It should not be listed as an owner question with the weaker form as the
draft's reading. Evidence already in the draft: PART P, 0 of 364 on four pairs, every condition form; A6 is not a
counterexample.

### RULING-5 — the looped-warning proposal contradicts the black-box principle and fires on the ruled meaning (CONFIRMED by derivation from the draft's own numbers; design; effort small (reword the R.8 row's cost column); blast: R.1.7 line 773, R.1.8, §R.8 looped-warning row)
The black-box ADDENDUM (owner) says a condition reads only the labels the box exposes. MINE (b), which the draft adopts
as a tested claim (R.1 line 532), puts "passes ... INSIDE the box". The proposed warning (lines 773-774, 1107) fires
when a bare condition reads a label "set inside a loop", which is exactly a fact from inside the box. Consequences:
(1) on SAME-1's same-result pair, `/(?:(?<h>\d);)*/` vs `/(?:(?:\d;)*(?<h>\d);)?/` (0 of 364 differ under every
condition, PART P), `(h: <5)` warns on the first and is silent on the second. The diagnostic separates patterns that
the principle (and same-results, RULING-4) calls interchangeable. (2) It fires on the meaning he RULED and called
right ("Last pass own label makes sense", CF 2460). (3) With polarity-rule's strictness, a selector that matches
every name (§7.1's own `@warn.error(/.*/)`, "a strict build") turns every ruled bare-condition-over-a-loop program
into an ERROR. (4) It has no NAME, although R.2 line 848 says "Every warning the draft defines has one stable name"
and the polarity ADDENDUM's MINE (CF 2545) says every warning needs one. The R.8 row's cost column lists none of
(1)-(3). Status (THE MANAGER'S PROPOSAL, asked) is right. The row should carry these costs, and R.1.8's "it now decides
only the looped-warning" should note that the warning is the one place where repeatedness would leak out of the box.

### RULING-6 — under the draft's own names and selector rule, his strictness example selects nothing (CONFIRMED; design; effort small; blast: R.2, §7.1 warning table, §R.8 (missing row))
The polarity-rule ADDENDUM, HIS WORDS: "@options.strict(/no-fail/)". RECORD (CF 2541-2543): "the warnings whose names
it matches become errors (his example selects a warning named `no-fail`)". The draft names that warning `test.always`
(R.2 line 840; §7.1 line 3816). §7.1's SELECTOR rule (lines 3793-3797) matches a name set WHOLE: "`@warn.off(/^dead\./)`
... is the one name `dead.`". So his example, quoted in R.2 line 845 as the model, selects NOTHING under the draft's
names. Since the addendum, names are no longer spelling only: a selector over names decides which warnings become
errors, so a name choice changes what a strict program does. R.2 says "names not ruled", yet §R.8 has no row asking
for them. At minimum: say that his example names the warning `no-fail`, and either propose that name or put
**warning-names** in §R.8 with the cost (a selector written against one set of names silently selects nothing after a
rename).

### RULING-7 — unsettable-label is a test that can never pass, which polarity-rule already rules (CONFIRMED by reading; design; effort trivial; blast: R.2 table row, §7.1 REV 21)
R.2's table (line 856) lists **unsettable-label** (a label no match can set: an error per §7.1 REV 21) as "a candidate
for the same treatment, asked, not changed here", and its meaning column says "a test on it never passes: the
`test.never` case". polarity-rule was asked about "a test can never pass" (CF 2529-2530; the empty intersection was
the EXAMPLE). His answer, "warning for both", is general. The REV 21 error came from review r29 B (the manager's
disposition), not from a ruling. Read literally, the polarity ruling covers this case: it should become `test.never`
in this revision, or the draft should say why a test on a label that can never be set is not "a test that can never
pass".

### RULING-8 — operand-context: the draft calls its reading an exception that is NOT YET ALLOWED, yet keeps it as the default; exception-rule says the default is regex (CONFIRMED by reading; design; effort small (status/wording) or answer-level if reverted; blast: §R.6 table row, R.1.4, §R.8 operand-context)
§R.6 line 985 files "lookarounds and `\b` in an `&` operand see only the stretch" under "LOOKS LIKE REGEX, BEHAVES
OTHERWISE ... NOT YET ALLOWED: asked". §R.8 line 1113 keeps that same reading as THE DRAFT'S READING (0 / 90 / 132
of 364 differ from regex's). exception-rule (1), RULED: "everything that looks like regex should behave like regex
UNLESS WE EXPLICITLY ALLOW". An exception that is not yet allowed therefore defaults to REGEX behaviour (the
subject-context reading) until he allows it. The draft can't both classify the place as a not-allowed exception and
keep the exception as its reading. It must do one of two things: (a) argue that the place is NOT an exception (for
example, that matching B as its own pattern on the extracted stretch IS regex behaviour, as the LAW `A & (0: B)` and
the ruled "^ $ refer to the scoped match" suggest), and move the row out of the table; or (b) make the subject reading
the current one, pending him. The same check applies to **shared-label** (line 989), more weakly: PCRE without `(?J)`
also rejects duplicate names.

### RULING-9 — the identification of item 14 with (*SKIP) is the manager's reading, stated as fact (CONFIRMED; doc; effort trivial; blast: R.1.4 ATOMIC, R.11 row 39; no answer moves)
R.1.4 lines 664-665: "Item 14's reading is a BACKTRACKING-CONTROL VERB, and on libpcre2 it is (*SKIP)'s behaviour, not
(*PRUNE)'s ... (*SKIP) ... (the search resumes after the rejected match: his "returns nothing" with later matches
still found)". HIS WORDS (CF 2513): "more akin to (*prune) or similar". His item-14 words (predicates_future.md lines
218-220) speak of ONE text, `9:30`, and say "Now the pattern returns nothing". On that text (*SKIP) and (*COMMIT) both
give nothing (the draft's own run). "With later matches still found" is the manager's addition (CF 2525, inside THE
MANAGER'S RUN), not in his words. So "(*SKIP), not (*PRUNE)" is THE MANAGER'S READING: it contradicts the verb he
named, and his words do not separate SKIP from COMMIT. Label it so, and carry it as a question under item 19
(atomic-spelling row) rather than as a fact. R.11 row 39's "((*SKIP) on the run)" is acceptable.

### RULING-10 — R.11 rows whose status the evening changed but which were not updated (CONFIRMED; doc; effort small; blast: §R.11)
- Row 20 (line 1224) still says "else asked (**polarity-rule**, **join-order**)". polarity-rule is RULED (row 40), so
  the row needs "polarity-rule RULED by row 40".
- Row 27 (line 1231) still says "narrows joint-loops (1) and absent-rule (1), (2) for bare conditions". Under rev 24.2,
  absent-rule (1) HOLDS AGAIN (R.1.7 ABSENCE line 768; §R.9 line 1154) and joint-loops (1) is RESTATED (§R.9 line
  1153). The row also omits that its edge was NARROWED by row 36 (CF 2467-2469, RECORD (5)).
- Row 35 (line 1239) omits the entry's LESSON (CF 2451-2452: "I thought we said" was a recollection, not a ruling; the
  settle-before-launch rule applies). It is a process rule of the same kind row 6 records as "STANDS (process)".
- Row 11 (sql-picture) and the §R.8 sql-picture row: the owner's "That's where the SQL analogy breaks down" (CF 2497,
  row 38) narrows the restatement. §R.8 notes it, but R.11 row 11 does not point to row 38.
- Row 32's addendum MINE (CF 2404-2406: one named group gives both; `\k<m>` against `(m: ...)`; "what the draft's
  existing sentences on `\k<x>`, `capture(x)` and the `captures` level say today") is only partly discharged. PART L
  covers `\k<m>`. No sentence says what `capture(x)` (§5.3 line 3430, a caller-visible group) returns for a looped x
  (the capture, or the pass's own label), and §4.2's `\k<x>` sentence at line 2970 is not marked.

### RULING-11 — §R.9's list of rev 24.2 marked sections is incomplete (CONFIRMED; doc; effort trivial; blast: §R.9 MARKED SECTIONS)
§R.9 lines 1172-1173 list rev 24.2's marks as §2.6, §4.2 and §4.3 only. Grep `REV 24.2` after line 1247 also finds
§5.2 (line 3386: "[REV 24.2: a WARNING, `test.never`, ...]") and §7.1 THE WARNING TABLE (line 3810, "rev 24.2,
rulings R6"; rows 3815-3816), plus the §0 status line (1250). R.11 row 40 itself cites "§R.2, §5.2, §7.1". G24-1 (b)
needs this list to be complete.

### RULING-12 — a [REV 24.2] mark calls a paragraph "the RULE in substance" but keeps that paragraph's wrong example (CONFIRMED by hand derivation and the draft's own engine line; answer (in a kept example); effort trivial; blast: §2.6 line 2412-2416)
The §2.6 mark (line 2412): "[REV 24.2: the RULE in substance (after-loop-read, nested-pass) ... where this paragraph
and R.1.7 differ, R.1.7 wins]". The paragraph keeps `(m: occurrences(/(?<g>a)?b/) & (g: "a"))` on `abb` REJECTS
("hit 2's g is unset, `label.unset`"). Under rev 24.2 (regex-settles (4), the one-pattern lazy-gap loop with re-entry;
a bare condition after it reads the LAST hit's own label, R.1.9), the path with hits [`ab`, `b`] fails (the last hit's
g is unset). The pattern then backs off to hits [`ab`] with `b` as gap, where the last hit's g = `a`, so the program
HOLDS. That is R.1.7's own engine line on the same shape: `occurrences(/(?<x>(?<g>a)?b)/, min = 1) & (g: "a")` on
`abb` HOLDS with x = `ab` (line 753-754, 42 / 42 / 42 of 364). The mark should name this example as superseded rather
than call the paragraph the rule.

### RULING-13 — the pass forms over a label two loops deep are stated nowhere and missing from §R.8 (SUSPECTED; design; effort small (one R.8 row + an engine run); blast: R.1.7 NESTED LOOPS, §R.6 PASS TABLE row, §R.8)
nested-pass RULED: "The view of the labels on an rx is the outermost view. To get inner views you nest the labels and
condition". The draft states the outermost view for a BARE condition (R.1.7 (4)) and for inner views by nesting. It
never says what `some(c)`, `occurs.*(.., c)`, `h[2]` or `$h[2]` list when h is two loops deep. They could list the
OUTER passes, each with h at the outermost view (the last inner pass's own within that outer pass), or EVERY inner
pass. Read literally, the ruling gives the outer passes (a request from outside sees the outermost view), and inner
passes would need nesting. On `/(?:(?:(?<h>\d)?;)*,)*/` with `3;;,7;,`, `some((h: <5))` HOLDS if it lists every inner
pass and FAILS if it lists the outer passes (h unset, then `7`). Every some-own and §R.4 witness is a single loop, so
nothing checks this. Confirm by an engine run of `some((h: <5))` on that pattern. Add **pass-forms-nested** to §R.8,
or state the literal reading as entailed.

### RULING-14 — "Then the rx is ..." is attributed as his reply to being shown `late`; the record has it the other way round, and outside HIS WORDS (CONFIRMED; doc, low; effort trivial; blast: R.1.7 (1) line 700-701)
R.1.7 (1): "and, shown `late := time & ((h, m): >= (9, 30))`, `/(?:${late},)*/` (after-loop-read): "Then the rx is "a
loop of (times after 9:30)""". In the record (CF 2455-2456), the phrase sits in the entry's PREAMBLE: "shown that the
ALL meaning is the condition on the item ("Then the rx is "a loop of (times after 9:30)"", his words, to `late := ...`,
`/(?:${late},)*/`)". The phrase is his, and the `late` program is the manager's rendering of it. The entry's HIS WORDS
are only "after-loop-read: ok I see it. Last pass own label makes sense". The quote itself is verbatim. The draft
should not present it as his answer to the program, and the cite should be "the after-loop-read entry's preamble".

### RULING-15 — the language-kind MINE on names is not carried into the rows it names (CONFIRMED; doc, low; effort trivial; blast: §R.8 every-pass-spelling and rx-module rows)
The kind-of-language entry's MINE (CF 2505-2508) says names should not invite the imperative or set reading, and that
this is "an input to the rx-module naming ("loop") and to the spellings still open". His words: "it looks like
functions and predicates and loops but it's not". §R.8's every-pass-spelling row (line 1129) offers "his `loop`
construct over a conditioned item" as a candidate, and the rx-module row (line 1130) does not mention the naming
hazard. Both rows should carry the MINE as the manager's input. It is not a ruling: the record files the entry as
"principles for the draft's framing, not rulings on any answer".

## PROBED-AND-HELD


QUOTES (part (a)): I checked every owner quote of the evening entries in §R against COND-FAMILY 2364-2546, with
whitespace normalised (script `q2.py` in this dir, plus reading). The following are VERBATIM and attributed to the
right entry: exception-rule (in full, at lines 462-465 and 953-957; also the "Exceptions should be requested..." and
"If requested (and optioned in if needed)..." pieces); "what you should do is assign the condition inside the loop to
get the all behavior"; "after-loop-read: ok I see it. Last pass own label makes sense"; "I think the expectation is
that each loop has its own ... most would expect that a missing group would unset" (the elision is fair; the slug
prefix "joint-last-pass:" is dropped); "that logic might be justified if you differentiate between a label and a
capture"; nested-pass (both sentences); the black-box ADDENDUM; the kind-of-language passage ("It's a bit deceptive
... but it's not"); atomic-search ("atomic: I think ... (*prune) or similar. Atomic as used by say atomic() would
provide pcre behavior"; "match A then B but don't go back into A"); polarity-rule ("polarity-rule: warning for both.
Warnings are errors given some strictness setting eg @config.strict()") and its addendum "@options.strict(/no-fail/)".
Earlier-day quotes reused in §R also check verbatim (11:50, 12:25, 12:55, 13:10, 13:15, 13:20, 13:25, 14:05, 14:20,
14:30, regex-settles, item 14): 21 strings, 0 mismatches. The only exceptions are the entry name (RULING-1) and the
placement noted in RULING-14. Every entry-name cite in §R resolves except RULING-1's: "OWNER RULING — exception-rule",
"— after-loop-read", "— nested-pass", its ADDENDUM, "reconsidering the entry above within minutes", "OWNER, on what
kind of language this is", "OWNER on atomic-search", "polarity-rule", RECORD (4) and RECORD (5) of after-loop-read.
LAST ENTRY APPLIED (part (a)): on each evening subject, the draft applies the LAST entry. Pass labels: CF 2454 + 2474
(not the 2385 lean). Bare condition after a loop: 2454 (not 2423). Nested view: 2474 (not the 2408 lean). Strictness
scope: the 2540 addendum (not the 2537 MINE "every warning"; R.2 and §7.1 select BY NAME; grep finds no surviving
"every warning" in the strictness sense). Atomic: 2510. 2423's restoration of Q4 / "ALL hits" is NOT carried: §R.9
keeps them REVERSED by last-pass-default, which is right because 2467 says last-pass-default STANDS. Nothing in §R
still rests on PCRE's carry as the label's value. Every mention of the carry is marked as rev 24.1's reading, the
CAPTURE, or a switch (R.1.7 (5), §R.6, §R.7, PART L). The [REV 24.2] marks at §4.2 (2932) and §4.3 (3059) agree with
2454 (the §2.6 mark: RULING-12).
MINE LABELS (part (a)): black-box (a)-(d): "THE MANAGER'S READINGS ... CLAIMS ... none ruled" is right as a label
(but (c) is entailed: RULING-4). Language-kind: framing, "no answer changes", right (RULING-15). atomic-search's MINE:
mislabelled as fact (RULING-9). polarity "covers every warning": correctly dropped for the addendum. looped-warning:
"THE MANAGER'S PROPOSAL", right (RULING-5 on its costs). `test.never`/`test.always`: "THE DRAFT'S PROPOSED NAMES",
right but see RULING-6. value-point, same-results, some-own, hits-pass: all labelled "asked", but each is entailed
(RULING-2, -3, -4). joint-last-pass "dissolves" (MINE, CF 2470): HELD as entailed (R.1.5: a record/joint is the `&`
of its entries, each reading the last pass's own, so the tuple is the last pass's own; PART J 0 of 85). Absent-rule
(LOCKED) agrees with R.1.7 ABSENCE. default-scope agrees (a default stands in for the last pass's unset label: CLOSE
hour line). branch-scope (ii) agrees with black-box (a). regex-settles (5) agrees with atomic-search (atomic stays
PCRE's).
R.8 OPEN TABLE (part (b)): closed items absent from the open table: exception-rule, pass-own-labels, nested-pass,
polarity-rule, atomic-search, joint-last-pass and bare-loop-label are each in DISSOLVED/RULED/CLOSED, none in the
open rows. (after-loop-read itself is not named as a slug; it is cited under pass-own-labels. Acceptable.) Open items
of the evening that are present: looped-warning, every-pass-spelling (with his evening words), atomic-spelling (with
the verbs and `A :: B`), options-spelling (item 20; the strictness setting's scope and host cap fit there, but the
row does not mention warnings: minor). Missing: warning-names (RULING-6) and pass-forms-nested (RULING-13). Present
but entailed: RULING-2, -3, -4.

THE RULING TABLE FOR THE NEXT REVISION (evening entries; built from the record, then diffed against R.11 rows 31-40
and §R.9):
| # | entry (CF line) | status | reverses / narrows / settles | R.11 / §R.9 diff |
|---|---|---|---|---|
| 31 | exception-rule (2364) | STANDS (RULED) | settles 13:30's (A)/(B); supersedes the manager's "converted to regular language" reading and the "both" lean; CONSEQUENCES MINE: whole-text and the hit list admitted as requests; every look-alike place listed | matches; but §R.6's operand-context row conflicts with it (RULING-8) |
| 32 | LEAN a pass has its own labels (2385) + ADDENDUM label/capture (2398) | superseded as a lean, ruled by 36 (pass-own) and 37 (outer); the ground (label vs capture) STANDS | its MINE R4 partly open (`capture(x)`) | matches; R4 gap (RULING-10) |
| 33 | pass-own-labels after the ramifications (2408): outer lean; alternation case expected to fail; MANAGER'S NOTE bare-loop-label | lean ruled by 37; "all must pass" expectation superseded by 35/36 (his `3x` expectation still holds: FAILS) | none of its own | matches |
| 34 | "labels match every pass, captures match the last" (2423) | SUPERSEDED (by 35, ruled away by 36 (4)); its restoration of Q4 / ALL hits never takes effect | none (it would have reversed last-pass-default for labels) | matches (R.11 34, §R.9 row, R.8 dissolved) |
| 35 | reconsideration (2442) | STANDS: ALL is written on the item; after-loop-read reopened, then ruled by 36; LESSON (process) STANDS | none | LESSON missing (RULING-10) |
| 36 | after-loop-read RULED (2454) | STANDS | NARROWS last-pass-default's recorded edge to the capture; RESTORES absent-rule (1) for bare conditions; RESTATES joint-loops (1); dissolves joint-last-pass (MINE, entailed); withdraws the compile-error lean; looped-warning stays a proposal | row 27 not updated (RULING-10); value-point entailed by its (1) (RULING-2) |
| 37 | nested-pass RULED (2474) + black-box ADDENDUM | STANDS; innermost candidate retired | rules 33's lean; MINE (a)-(d) claims, (c) entailed (RULING-4); pass forms over nested loops unstated (RULING-13) | matches in status |
| 38 | kind of language (2493) | framing, STANDS as principle; no answer | narrows sql-picture (the analogy "breaks down") | R.11 row 11 lacks the pointer (RULING-10) |
| 39 | atomic-search (2510) | CLOSED: atomic = PCRE's; item 14 = a backtracking verb ("(*prune) or similar"); `A :: B` an idea | reclassifies item 14 (an idea, not a ruling) | the (*SKIP) identification is MINE (RULING-9) |
| 40 | polarity-rule RULED (2529) + ADDENDUM (2540) | STANDS; strictness SELECTIVE by name | §5.2's error becomes a warning; corrects the manager's "every warning"; reaches unsettable-label (RULING-7) | row 20 stale; §R.9 marks miss §5.2, §7.1 (RULING-10, -11); names vs `no-fail` (RULING-6) |
Rows 31-40 of R.11 are all present (10 of 10). Statuses agree with mine except as noted in the diff column.

## SIBLING OF A FAMILY (from the rulings' side)
WARNING CONTROL now has three spellings of one fact, "select warnings by name with an rx; change their severity":
§7.1's `@warn.off(sel)` and `@warn.error(/.*/)` ("a strict build"), and the owner's `@options.strict(/no-fail/)` (the
`@options` family, item 20). R.2 places strictness in `@options` without noting that `@warn.error` already exists.
That is three members, so propose the unified table now: a selector over names maps to a severity (off / warn /
error), with one host-cap rule (item 20). Second family: "a pass" (loop pass, `occurrences` hit, the hit list's
committed hit, a lookahead's single path, an atomic part's committed path) each has its own "what labels does it
export at the outermost view" sentence spread across R.1.4, R.1.7, R.1.9 and §R.6. The PLACES table (item 22) is the
named home. hits-pass and some-own (RULING-3) are symptoms of the missing row.
## GENERAL FORM + UNLOCKS
General form: the BOX contract. A pattern exposes (results in PCRE's order, each with its outermost-view labels), and
everything else (passes, inner views, captures, hit lists, the stretch's surroundings) is reached only by an explicit
request feature, which is an exception under exception-rule. Unlocks: (1) the spelling principle becomes a theorem
(RULING-4), and an optimizer may swap same-result patterns freely. Trigger: the first rewrite pass that changes a
pattern's shape under a condition. (2) Diagnostics must also respect the box, which settles looped-warning (RULING-5).
Trigger: the next warning that is proposed. (3) Every request feature gets one row (feature, what it opens, level),
which is §R.6's table generalised. Trigger: the rx-module design note (item 21), whose `loop`/`digits` constructs will
each need their row.

CRITIC COMPLETE
