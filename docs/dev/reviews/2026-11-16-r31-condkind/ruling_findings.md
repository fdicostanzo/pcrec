# Critic RULING — round crit-condkind (design)

## Findings


### RULING-1  The 22:30 per-entry reading reverses more than "default-reaches-dollar": rev 22 (e2.1), L101, II.3.2's LOCAL row and the owner's own 16:23 unification
STATUS: CONFIRMED. `defscope_options.out` line 16 (1b'): under (a2) the record `(a = 0: <10, b: >$a)` = its `&` spelling, holds 45 (`-1` FAILS); the joint `((a = 0, b): a < 10 & b > a)` holds 54 (`-1` HOLDS). Rev 22 L101 (draft line 776) says the record and that joint spelling are SAME; (e2.1) (draft line 2343) says the default fills `$a`.
SEVERITY: answer (9 of 110 subjects of AB, `-1`, flip HOLDS -> FAILS for the record).
EFFORT: small. BLAST RADIUS: rev 23 §4.2 (e2.1), §0.1 L101, the record-is-product statement, the ruling list.
WHERE: COND-FAMILY 22:30 ("the manager's earlier reading default-reaches-dollar (16:23) REVERSES"); condition_kind.md II.5 rows "default-reaches-dollar ... STANDS inside one condition" and "(e2.1), (e2.2), (e1) | STAND"; Part I §3 row "(rev 22 (e2.1), the 16:23 derivation: FOLLOWS)"; III.6 "Per test (either form): ... II.3.2's LOCAL row stands".
BODY: (a2) makes `$a` read the row inside the writing record too, so (i) (e2.1) and L101 reverse with default-reaches-dollar (same derivation, separate rev 22 sites); (ii) II.5's "(e2.1) STAND" and Part I's FOLLOWS are no longer true; (iii) III.6's "II.3.2's LOCAL row stands" is true only of (a1): II.3.2's LOCAL record cell says HOLDS (54), (a2) gives 45. (iv) The 16:23 derivation answered the OWNER's question "Isn't that form a rewrite of the (a,b): form ? We unified those correct?" from record-is-product (11:35: "every rule of the joint condition (unset labels and defaults, ...) holds for the record by definition"). Under (a2) the answer to his question becomes NO for a record whose entry reads another entry's label: the record is the AND of its entries, NOT the joint condition. III.2.1/III.5 call the reversal "not an owner ruling", which is true of the derivation but hides that the owner's own stated understanding of record-is-product is narrowed. 22:30's question did name "`$a` reading the real label", so the ruling stands; the record must spell the consequence.
FOR REV 23: list (e2.1), L101 and default-reaches-dollar as REVERSED by default-scope (22:30), and state record-is-product as covering PRODUCT records only: a record with a cross-entry `$` is the AND of its entries and differs from its joint spelling (`-1`: record FAILS, joint `((a = 0, b): ...)` HOLDS).

### RULING-2  "all = every pass passes, there may be none" (A2) is the "empty list only" reading the 14:50 (a) reading rejected: it answers the two causes of absence oppositely
STATUS: CONFIRMED (by the note's own words and a 2-subject run). III.3: A2 "changes rev 22's `all` on a pass with an absent label (A2 FAILS ...) and on zero passes (A2 always HOLDS ...)"; `defscope_options.out` PART 3: RZ `(h = 9: <5)` vs A2 `all((h = 9: <5))` differ on the 10 zero-pass subjects. Run (`RULING/bin/a2split.py`, python `re`): `/(?<g>a)?b/` and `/(?:(?<g>a)(?=b))*b/` match the same subjects over {a,b} up to length 5 (`b`, `ab`) with the same labelling; A2 `all((g: "a"))` on `b`: FAILS on the first (one row, g NULL -> UNKNOWN), HOLDS on the second (zero passes, vacuous).
SEVERITY: answer.
EFFORT: medium (a ruling-shaped choice, not a rewording). BLAST RADIUS: rev 23 §4.3 (`all`), L93, L36, the ruling list's `all` row.
WHERE: COND-FAMILY 22:30 ("MINE, restated without his word ... 'all' = every pass passes the condition, and there may be none (Part III.3, A2)"); 21:49 ("MINE, to restate and have checked: the 'all' group question"); condition_kind.md III.3; COND-FAMILY 14:31 (absent-rule (1)), 14:50 (a).
BODY: absent-rule (1) (owner, LOCKED 14:31): "ONE KIND OF ABSENCE ... whatever the cause (an optional skipped, a loop that ran zero times, an alternative not taken, a pass that did not set it)". The manager's 14:50 (a), told to him: "`all(...)` over no values holds for EVERY absence alike (the lane's A2m), never 'an empty list only': the other readings bring the `?`/`*` spelling split back (5 of 11 groups)". A2 is exactly "an empty list only": zero passes HOLD, a present pass with the label absent FAILS. So (i) the claim "no owner word needed: the meaning being replaced was the manager's reading" (III.3) misses that A2 reads two of absent-rule (1)'s causes differently, which is the locked rule's territory; (ii) under R1 (set-once optional = a column, a loop = a nested table, optional-as-loop's manager's reading) A2 splits two patterns with the same subjects and labelling, against the spelling principle (*); (iii) the A2 intent test in III.3 is on `occurrences` hits, where "a hit without g fails, no hit holds" is the AUTHOR's intent; that shows A2 names a useful question, not that `all` should be it. A1 (`all(c)` = c; `all` retires) keeps "every absence alike". A2 may still be right, but it is a question for the owner by name (A1 vs A2, with `b` above), not a manager's restatement.
FOR REV 23: do not state A2 as settled; carry `all` as OPEN (A1 retire vs A2) with the `?`/`*` example, or get the owner's word; if A2, state that it reads zero passes and an absent label in a pass differently and say why absent-rule (1) allows it.

### RULING-3  "STATE OF THE MODEL" is not complete: it omits four answer-moving facts the rulings and the note fix
STATUS: CONFIRMED (each omission quoted against the note's counts).
SEVERITY: answer.
EFFORT: small. BLAST RADIUS: whatever rev 23 takes as its summary of the ruled model (§0 / §2 / §4).
WHERE: COND-FAMILY 22:30, the STATE paragraph; condition_kind.md §1.2, §3 dictionary-order row, III.2, III.5.
BODY: the STATE says "a default is per test and may be any text". Missing:
(i) THE `$` CLAUSE, the one thing that separates the ruled (a2) from (a1): "a `$a` always reads the real label (absent stays absent)" (22:30 body). "Per test" alone is (a1) or (a2); they differ on 9 of 110 (AB, `-1`). The STATE must carry it.
(ii) THE RESULT ROW (R1): a result row is ONE MATCH, the pairing loop's passes a nested table; a plain condition = every pass and at least one (LEFT JOIN row on zero passes), a group question counts real passes. "A three-valued test of one result row" presupposes R1, which was never put to the owner (**source-row** asked S1 vs S2 only; §7's question and 21:49's record say nothing of R1). R2 (a pass is a row) differs on 500 of 1,110 (`0;0;5`, §1.2). Rev 23 needs R1 stated (it is the sequence rule CF:583 restated, so it may need no new word, but it must be written).
(iii) ABSENT-RULE (2)'s STRICTNESS: "any NULL in the tuple makes the test UNKNOWN", stricter than SQL's row comparison (§3 dictionary-order row: `((h, m): padded(>= (9, 30)))` on `10`, ruled FAILS, SQL TRUE). A STATE that says "three-valued test" in a SQL model invites SQL's row comparison; it must name the exception.
(iv) TWO DIFFERENT DEFAULTS FOR ONE LABEL ARE LEGAL and hold where no single value fits (`(h = 0: <5) & (h = 9: >7)`, 11 of 21 on pool A, `c`): stated in 22:30's body "as put to him", absent from the STATE.
Also absent (design, not answer): the complement carries NO labels out (Part I §2, III.1 b1); the spelling principle (*) stands; `all` open (RULING-2); the §5.2 empty-intersection error survives (RULING-5); condition-not open (RULING-6).
FOR REV 23: write the model from a full list (the above plus the STATE's seven clauses), not from the STATE paragraph alone.

### RULING-4  20:41's "both nots ... differ exactly on unmatched and absent-label rows" drops the third row of the note's own table: several result rows per subject
STATUS: CONFIRMED (condition_kind.md §2, "WHERE THE TWO NOTS PART" table, row "a source row with SEVERAL result rows (searched) | per result row | per SOURCE row: kept only where no row has c TRUE | per result row"). Hand case under the ruled source-row (21:49: "a searched pattern gives several result rows per subject; the complement is per subject"): t2 searched, c = `((h, m): late)`, subject `9:30 8:00`: the span `8:00` has c FALSE, so `t2 & NOT c` (and `t2 & ((h, m): !late)`) find a row and HOLD; `t2 & !(t2 & c)` FAILS (the subject has a late row). h and m present, the subject matched: neither "unmatched" nor "absent".
SEVERITY: answer (the not-is-complement error hands the author the set-complement rewrite and the complemented-pattern rewrite as the two spellings; in searched mode they answer differently on subjects with present labels).
EFFORT: small. BLAST RADIUS: rev 23 §2.2 (the two nots), the error text and its hint table (review r30 G).
WHERE: COND-FAMILY 20:41, THE MANAGER'S JUDGMENT ("it defines both nots and they differ exactly on unmatched and absent-label rows"); the rest of that judgment holds (EXCEPT reading, no labels, the open source-row question), see PROBED-AND-HELD. Also a second omission: the repeated-label row (`0;0;5`, 500 of 1,110) separates NOT c from the SET complement `(h: !S)`, the other rewrite the error names.
FOR REV 23: state the two rewrites' difference fully: per source row vs per result row (searched), unknown kept vs dropped (absent labels, zero passes), and "every pass outside S" vs "not every pass in S" (repeated labels).

### RULING-5  21:49's retirement list and its "MINE" item disagree with Part II.5: the empty-intersection error is dropped, "all" is misnamed as the value set's other reader, five II.5 rows are missing
STATUS: CONFIRMED (quoted).
SEVERITY: design (answer-adjacent: a rev 23 that retires zero-pass-empty "whole" could drop the §5.2 compile error).
EFFORT: small. BLAST RADIUS: rev 23's ruling list, §5.2, §7.1.
WHERE: COND-FAMILY 21:49 drop-mark bullet; 21:16 MANAGER'S JUDGMENT; condition_kind.md II.5 (prose and table), Part I §5 row "its corner".
BODY: (a) ZERO-PASS-EMPTY'S "CORNER" names two different things. 19:44 and 21:16 use it for the MARK's empty-set case ("a marked absent label against an empty set would HOLD"; 21:16 "Dropping the mark retires ... zero-pass-empty's corner"); Part I §5 and II.5 use it for "the set empty as written -> the empty-intersection error", which II.5 says STANDS ("its corner (a set empty AS WRITTEN is the §5.2 error) STANDS as part of §5.2"). 21:49 retires "zero-pass-empty" with no carve-out. Read together, the record retires what the note keeps. (b) 21:49: "MINE, to restate and have checked: the 'all' group question, the other reader of the per-program value set (Part II.5)". II.5 says the opposite: the per-program value set "is read by the mark and by nothing else", `all(c)` is listed among "the mark's derived uses", and "ONE OTHER READER" of "the values h can hold" is the §5.2 EMPTY-INTERSECTION ERROR, which "stays and needs only a per-LABEL value set (the regex's)". The record names the wrong reader and drops the right one. (c) II.5 rows with no counterpart in 21:49 or the STATE: the never-absent-mark warning RETIRED; mark-domain's use for a value set RETIRED (principle stands); the "if it is possible" tier SHRINKS to per-label regex values; absent-rule (3)'s "not both" has no subject; FIXIND-5 (`label.unset`'s first fix `h?`) CHANGES to a default (II.1.3 G).
FOR REV 23: keep the §5.2 empty-intersection error and its per-LABEL value set (regex values) explicitly; carry every II.5 row into the ruling list (table below).

### RULING-6  "`!` on a condition stays an error" is stated as settled; condition-not was never asked and the error's ruled reason is contradicted by the model and by the owner's 19:49 words
STATUS: CONFIRMED (quoted).
SEVERITY: design (the error stands as ruled, so no answer moves; the reason and the hint text do).
EFFORT: small. BLAST RADIUS: rev 23 §2.2 / the not-is-complement error text, owner.md's question list.
WHERE: COND-FAMILY 22:30 STATE ("`!` on a condition stays an error"); 21:49 (four slugs: drop-mark, default-scope, default-value, source-row; no condition-not); condition_kind.md §7 **condition-not**, §5 row "second half ... CHANGES IN ITS REASON", II.5 "Part I's **condition-not** unchanged".
BODY: not-is-complement (17:29) rests on his words "! takes an rx and gives the complement set of strings. That has no meaning on a condition." At 19:49 he wrote "Not on the condition there is well defined", and Part I §2 defines NOT c (three-valued). Part I asked **condition-not** (keep the error, reason "one spelling per question"); no record entry answers it; 19:49's own entry says the second half "is to be RE-ASKED by the definition lane, by name". The STATE presents the error with no open question attached.
FOR REV 23: keep the compile error as ruled, do NOT restate the reason "no meaning on a condition", and carry **condition-not** (the reason) as an open owner question.

### RULING-7  "one-witness RETIRES" (21:49) is undone by "per test" (22:30): the oddity returns with two defaults, and Part II's dissolve claims that rested on one default per label lapse
STATUS: CONFIRMED. III.2 row "two conditions, DIFFERENT defaults": (a2) 11 HOLD on pool A (`c`) though no one value is both below 5 and above 7; II.1.2: `(h = 0: <$k) & (h = 9: >$j)` holds on 81 h-absent subjects of J, 45 with no single fitting value (`01`).
SEVERITY: answer (11 of 21; 45 of 81).
EFFORT: small. BLAST RADIUS: rev 23's ruling list (one-witness, L104), §7.1 (a warning, if any), the label-twice hint (review r30 RULING-9).
WHERE: COND-FAMILY 21:49 ("The manager's readings one-witness and not-of-marked retire"); 22:30 ("two different defaults on one label stay legal"); condition_kind.md II.5 ("RETIRED with one default per label; under LOCAL it returns"), II.1.3 group G ("RULING-9's split DISSOLVES with one default per label"), II.1.3 closing paragraph and II.6 drop-mark LEANING ("one-witness dissolve"), III.5 cost (1).
BODY: one-witness the READING (a stand-in per marked condition) retires with the mark; the PHENOMENON (one label tested against two values in one statement) is legal and live under the ruled per-test default. Part II's claims "one-witness dissolves" and "RULING-9's split dissolves" were conditional on one default per label, i.e. on the whole-statement leaning 22:30 rejected; they were part of the drop-mark leaning the owner said yes to at 21:49. Rev 22's label-twice hint offering `(h: A & B)` and `(h: A) & (h: B)` as alternatives is still false when the two carry different defaults.
FOR REV 23: state that two different defaults for one label are legal and give the oddity (the example and count), mark one-witness RETIRED as a reading only, and scope the label-twice hint to "same default or none".

### RULING-8  The per-entry reading's remedy cites "labels that go together are written together" (16:13): a record gloss, not his words, from match-context, which 21:49 retires
STATUS: CONFIRMED. COND-FAMILY 16:13: his words are "So in that pattern, you might (k,h?): ((\"a\", <5) | etc" and "match-context: anywhere. This does need some sort of debugger for writing these."; "labels that go together are written together, in a joint condition" is in the RECORD sentence after "RULED:". condition_kind.md III.4 ends: the cross-label relation goes to "the joint condition, which already exists for exactly that ('labels that go together are written together', 16:13)".
SEVERITY: design.
EFFORT: small. BLAST RADIUS: rev 23 §4.2's statement of why a `$` reads the row; rev 22 line 2364, which quotes the same gloss.
WHERE: condition_kind.md III.4; COND-FAMILY 16:13, 21:49 ("RETIRES ... match-context").
BODY: the cost argument for (a2) leans on a sentence quoted as if ruled, which (i) is the manager's record wording, not the owner's, and (ii) belongs to a ruling now retired. The remedy itself needs no such support: record-is-product (11:35) and the joint condition give the author the joint `((a = 0, b): b > a)`.
FOR REV 23: ground "write the joint condition when one label's test reads another's default" on record-is-product / the joint condition, never on match-context's gloss; do not quote the gloss as the owner's.

### RULING-9  Quote and cite residue: three quotations not found as quoted, two cites that misplace their source
STATUS: CONFIRMED (grep of COND-FAMILY.md, predicates_draft_rev22.md, predicates_future.md; script `RULING/bin/quotes.py`).
SEVERITY: doc.
EFFORT: small. BLAST RADIUS: the note's text and any rev 23 sentence copied from it.
WHERE / BODY:
- II.1.1: "What the draft does NOT define is how FAR a default reaches (only 'in the condition where it is written' is stated)": the phrase is in neither the draft nor the record. The draft's words are "at a LABEL left of `:` in a condition" (line 2934).
- III.1 and III.5 quote that phrase as "at a label left of `:` in a condition" and cite §4.2; it is in the §5.4 mark table (line 2934), with "LABEL" in capitals.
- II.5: "an empty intersection from PURE PARTS": rev 22 line 2854 reads "pure parts" (capitals added inside quotation marks).
- §4 ("the manager's 14:50 (c), withdrawn at the time") and §4.2 ("the ground on which the manager withdrew 'any text' at 14:50 (c)"): 14:50 (c) is where "any text" was ASSERTED ("'Some value' ranges over ANY text"); its withdrawal is recorded later (15:27 reading (3): "stays withdrawn"; rev 22 line 2395).
- Minor: §1.2 quotes the sequence rule as "every pass", CF:583 (the cited 2026-11-14 entry's Q4 says "`x:` = all iterations"); §4 puts "unknown counts as true" in quotes (record 19:44: "UNKNOWN counts as TRUE"). In the RECORD itself, 20:36's consequence (2) cites "domain-scope, 16:32" (the entry is 16:31).
- 21:49's cost sentence "`(h?: <5) & (k: <5)` on `b3`: rev 22 FAILS, without the mark HOLDS unless the author picks another default": with the mark merely deleted the program FAILS on `b3` (h absent); it HOLDS only with the default `h = 0` (II.2.1). The sentence presumes the rewrite.
FOR REV 23: copy wording from the record and the draft, never from the note's paraphrases in quotation marks.

### RULING-10  Under (a2) a `$a` reads NULL even inside the joint condition that defaults a; only the tuple's own part sees the default
STATUS: SUSPECTED (follows from 22:30's "a `$a` always reads the real label" and III.1's "(a2) ... a `$h` always reads the row"; not run: III.2 says the battery has one condition whose `$` reads its own label, the record (1b'), and the rewrite set has none). Would confirm: AB, `((a = 0, b): (<10, >$a))` vs `((a = 0, b): a < 10 & b > a)` on `-1` (expected under (a2): FAILS vs HOLDS).
SEVERITY: answer (the remedy the 22:30 entry hands the author, "writes one joint condition", works only through tuple-part names, not `$`).
EFFORT: small. BLAST RADIUS: rev 23 §4.2 (defaults), §4.1's `$x`-default legality, worked examples using `$` on a defaulted label.
WHERE: COND-FAMILY 22:30; condition_kind.md III.1 (a2) row, III.4, III.5 cost (2).
FOR REV 23: say in one sentence that `$a` never sees a default, in any condition, including the one that writes it; the joint condition's tuple part is the only reader of a default.

## REV 23 RULING LIST (every ruling or reading named KEPT / FOLLOWS / CHANGES / STANDS / RETIRED in Part I §5, II.5, III.6, status after 21:49 and 22:30)

| ruling or reading | status now | by | note |
|---|---|---|---|
| absent-rule (1) one kind of absence, (2) a condition needs a text, (4) a set never contains absence | STAND | 14:31 | (2)'s "any NULL in the tuple -> UNKNOWN" is stricter than SQL: state it (RULING-3 iii); `all` A2 strains (1) (RULING-2) |
| absent-rule (3) the two controls / "not both" | CHANGED: the mark clause REMOVED; the default is the one control; "not both" moot | 21:49 drop-mark | |
| optional-as-loop | STANDS | 15:23 | |
| mark-domain / spelling principle (*) | principle STANDS (provisional wording); its value-set use RETIRED | 15:27, 15:29; II.5 | holds by construction for one-row tests |
| match-context | RETIRED | 21:49 | its gloss "labels that go together ..." must not be quoted as standing (RULING-8) |
| zero-pass-empty (F1) | RETIRED | 21:49 | |
| its "corner" = §5.2 empty-intersection error (constant empty set) | STANDS (II.5); needs per-LABEL regex values | II.5; record silent | RULING-5 (a) |
| domain-scope, mark-narrows | RETIRED | 21:49 | "P & c is a new statement" survives as the model's definition, not as these rulings |
| mark-range | WITHDRAWN | 21:49 | |
| mark-in-none | RETIRED | 21:49 | |
| not-is-complement, first half (`!` on a pattern = complement) | STANDS; complement = source rows (subjects) with no result row, no labels out | 17:29, 20:41 guess, 21:49 source-row | |
| not-is-complement, second half (error on a condition) | error STANDS; its REASON OPEN (**condition-not** never asked) | 17:29; I §7 | RULING-6 |
| label-twice | STANDS | 13:16 | |
| record-is-product | STANDS for product records; a record with a cross-entry `$` is the AND of entries, NOT its joint | 11:35; 22:30 | RULING-1 |
| zero-pass-record | STANDS (LEFT JOIN row; (a2) 155, `9` FAILS) | 12:45 | |
| default-set, colon-scope, unset-component, default-unused | STAND | 10:43, 11:32, 11:05 | default-unused = the "warning only on a default that can never be used" of default-value |
| default-value | RULED: any text, no restriction | 21:49 | item 11 answered |
| source-row | RULED: S1, whole subject; several result rows per subject when searched | 21:49 | R1 (one match, nested passes) UNRULED, must be stated (RULING-3 ii) |
| default-scope / dollar-across-and (r30 I) | RULED: per test, per-ENTRY (a2), `$` reads the row | 22:30 | 0 record/`&` split |
| default-reaches-dollar (16:23), rev 22 (e2.1), L101 | REVERSED | 22:30 | II.5's "(e2.1) STAND" and III.6's "II.3.2 LOCAL row stands" are void under (a2) (RULING-1) |
| (e2.2), (e1) | STAND (lane proposals, unruled as before) | II.5 | |
| one-witness (manager's, L104) | RETIRED as a reading; the oddity RETURNS with two defaults (legal) | 21:49; 22:30 | RULING-7 |
| not-of-marked; never-absent-mark warning | RETIRED | 21:49; II.5 (warning not in the record) | |
| "if it is possible" tier (15:27 (4)) | SHRINKS to per-label regex values (the §5.2 error's) | II.5; record silent | |
| `all(c)` (r28 C, "c with every label marked") | OPEN: A2 is the manager's "MINE, to be checked"; A1 (retire) the alternative | 21:49, 22:30 | RULING-2 |
| FIXIND-5 (`label.unset`'s `h?` fix) | CHANGES to a default | II.1.3 G | |
| predicates_future item 3 (several-value default) | parked; adopting it brings the mark back | II.5 | |
| Part II one-row properties (monotone 0 of 11,388; order-free; RULING-2/-7 0; `S & q`/`S & !q` never both) | STAND (run with a local default; per test ruled) | III.6 | |

## PROBED-AND-HELD

- OWNER QUOTES, word for word against COND-FAMILY: 19:31 ("History: ... whatever that means"), 19:44, 19:49, 20:36, 20:41 (the note drops only the slug prefix "condition-kind: "), 20:44 "Go. Purely exploration", 21:16 (whole), 21:19, 21:49 (III's partial quote), 22:30 "default-scope: yes per test", 17:29 "That has no meaning on a condition", 16:23 his question (rev 22 line 604 and the record agree), 17:02 item 11 (record = predicates_future line 155). All match. The 22:30 record's quoted question ("default-scope: per test, with `$a` reading the real label") names (a2) itself, so the manager's per-ENTRY reading of "yes per test" is the reading the question invited, not an inference.
- CITES: every "(hh:mm)" / "CF hh:mm" in the note (11:35, 12:45, 13:16, 14:31, 14:50, 15:23, 15:27, 15:29, 16:13, 16:20, 16:23, 16:31, 16:44, 17:02, 17:29, 17:42, 19:31-22:30) resolves to a record entry of that time and says what the note says, except RULING-9's items. CF:583 and CF:858 resolve to the 11-14 sequence-rule entry and the 11-15 "a condition is a macro" entry. Draft line cites 1204, 1232, 2333, 2459, 2779, 2842, 2854, 3091, 4381, 1036, 1325 checked: say what the note says.
- 20:41 judgment: "the guess is SQL's EXCEPT" (Part I §2 calls it EXCEPT on the source and spells it as an anti-join; held, EXCEPT being the reading aid); "a complemented pattern carries NO labels" (Part I §2, III.1 b1, `P & !q` 5 of 21 under every scope option): held; "leaves undefined WHAT A ROW OF THE SOURCE IS": held, answered by source-row at 21:49.
- 22:30 "two different defaults on one label stay legal ... holds on the h-absent subjects; coalesce(h,0) < 5 and coalesce(h,9) > 7": III.2, (a2) 11 of 21, `c`; the SQL rendering is right.
- 21:49 drop-mark costs: 45 of 680 pairs (II.2.1) and "none is reversed" (II.6: rulings "lose their subject") held, the `b3` wording aside (RULING-9).
- default-value "any text" vs the withdrawn "any text" range of the mark: no conflict (the mark's range was withdrawn because an unseen value witnessed an answer; a default's value is written by the author).
- colon-scope (11:32: a default after `=` is in value position) does not conflict with (a2).
- STATE clauses checked one by one: "a pattern is a statement" (20:41), "source row is the whole subject" (21:49), "absent is null and never matches", "no optional mark" (21:49), "per test and may be any text" (22:30, 21:49), "the complement ... source rows it did not match" (20:41 guess + 21:49 source-row): each supported by the record; the gaps are RULING-3 and RULING-6.
CRITIC COMPLETE
