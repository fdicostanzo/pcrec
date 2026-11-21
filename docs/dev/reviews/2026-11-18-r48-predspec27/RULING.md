# RULING findings — critic round predspec27 (rev 27 of predicates_draft.md)

(Pre-created by the coordinator. This is YOUR OUTPUT file: append findings as you go.)

## Findings

Lens question: is rev 27's fold faithful to the owner's words in the five entries of
`R/subject/record_2026-11-18_afternoon.md`, quote by quote? Does it keep every earlier locked ruling that it does not
reverse? Line numbers are lines of `R/subject/predicates_draft_rev27.md`. MINIMUM WITNESS LENGTH: this lens is a
text diff. I re-ran no pattern pool. The answer claims below rest on the draft's own printed answers (R.1.14 AL2,
R.1.15 (8), §R.8 rows), cited by line. Quotes were compared by a whitespace-folded exact search
(`ruling/q.py`) against the record and against COND-FAMILY at b22285a36 (`ruling/cf.md`).

### RULING-1. The array-lift fallout: under T8's reading, R.1.14's ruled worked example now gives an error, and nothing marks it. CONFIRMED. Severity: answer.
- WHERE: R.1.16 T8 (line 2175), STATUS cell "and by m1 an array the user writes: UNDER CONSTRUCTION". A6 (line 2201).
  §R.8 **construction-line** (a) (line 2772). R.1.14 (lines 1910-1915), with no REV 27 mark. §R.7's rev 27 paragraph
  (line 2517), which says "THE VALUE HOLE: no printed answer moves" and lists nothing for array-lift.
- WHAT: T8 is first-match and is presented as the type table. It gives arithmetic over a user-written array the status
  UNDER CONSTRUCTION, the error in every mode, as §R.8 (a) shows. R.1.14 still prints the RULED example
  `rx.repeat(rx.digit, n + 1)` with n := [2, 4] as `(?|\d{3}|\d{5})`, with WHOLE/SEARCHED/FIND-ALL answers (AL2). It
  also prints `[2, 4] + 1` = `[3, 5]` (AL1), "the hand-worked arrays he was shown" and RULED by array-lift. Under T8's
  cell these programs no longer compile, so the draft's own table gives a different verdict from the draft's own
  printed answers. This is G24-1's "no live sentence contradicting it unmarked", and §R.7 does not list the move.
- AGAINST HIS WORDS: no entry of the afternoon names arrays.
  - read-is-constant: "you could also go the other way and apply "single value" functions like x + 1 and left() to
    normal regex AS WELL". The words "as well" mark this as a NEW direction. Array arithmetic was already ruled that
    morning, so it is not the new direction.
  - match-is-rx: "Change my answers to match" asks for answers to follow the unification. It does not ask to demote
    a form he ruled that morning.
  - The hard part he names ("build the dfa graph then put the match state at the second character", "this is hard")
    is graph manipulation of a general rx. A user-written array is a finite compile-time enumeration, already folded
    by R.1.12/AL2.
  - One line cuts the other way and the draft does not cite it: the 2026-11-17 entry (about 12:15) says "a constant
    is an rx where the count of the enumeration is 1". Read literally, an array is not a "constant", so it falls
    outside "restrict them to constants now".
  The record therefore supports both readings. The draft should present (a) as a real fork with both of his lines,
  not as a default that silently breaks ruled examples.
- FIX: in T8, make the array cell "OPEN, **construction-line** (a)" rather than UNDER CONSTRUCTION. Alternatively,
  keep the reading but mark R.1.14 AL1/AL2 "[REV 27: UNDER CONSTRUCTION by m1's reading, asked]" and list them in
  §R.7. Put the 12:15 line beside "as well" in §R.8 (a).
- Effort: small. Blast radius: R.1.14, §R.7, T8, A6, §R.8 (a).

### RULING-2. R.1.15 drops a clause from the RULED form ("under the options in force at the hole") and then presents that clause as the manager's answer. CONFIRMED. Severity: doc (a ruling is labelled as a reading).
- RECORD ("OWNER on value-hole — "yes but""): ASKED AS A RULING (slug value-hole): "a hole may hold an expression over
  label reads and constants; it matches any string the expression yields, as literal text, UNDER THE OPTIONS IN FORCE
  AT THE HOLE; an expression that yields nothing fails". RECORD: "RULED yes to the form".
- DRAFT, line 2043-2045 (R.1.15 head): "RULED: a hole may hold an EXPRESSION over label reads and constants; it
  matches the strings the expression yields, as LITERAL TEXT, at the hole; an expression that yields nothing FAILS
  there (the form as asked him ...)". The options clause is dropped. Line 2103 (R.1.15 (10)(b)): "CASE: THE OPTIONS IN
  FORCE AT THE HOLE DECIDE (the manager's answer in the discussion; SUPPORTED ...)". This states a RULED clause as a
  manager's reading that the draft supports. Elsewhere the draft gets it right: T12 (line 2179, "under the options at
  the hole ... BUILT NOW, both forms (value-hole RULED)") and the R.1.0 row (line 834). So the draft also disagrees
  with itself.
- FIX: restore the clause in the RULED sentence. Re-label (10)(b) "RULED (value-hole, the form as asked); the
  discussion's case table (the manager's) SUPPORTS it". §R.11 row 121 ("case at the hole SUPPORTED") should cite row 122
  as the ruling. Effort: trivial. Blast radius: R.1.15 head, (10)(b), §R.11 row 121.

### RULING-3. §R.8's quote of read-is-constant cuts out his "other way" sentence, so his "under construction" remark seems to refer to the two forms. CONFIRMED. Severity: doc (the cut changes the meaning).
- DRAFT, §R.8 RULED rev 27 list, line 2714-2717: "Yes $y is a single value read at run time. ... Semantically, $y is a
  regex of a single string. So operations that work on regex should work on it. That means, in practice, that there
  are two forms for each of them ... The "under construction" remark is that this is hard and we shouldn't get bogged
  down with it now but acknowledge the direction."
- RECORD: between "two forms for each of them" and "The "under construction" remark" stand "the compile time version
  ... at run time. So $y + 1 and \d + 1 look the same ... My point was that we were applying & to $y but you could
  also go the other way and apply "single value" functions like x + 1 and left() to normal regex as well." The "this"
  in "this is hard" points to THAT sentence (the other direction). With the cut, "this" points to "two forms for each
  of them". A reader of §R.8 alone would conclude that the two forms are what is under construction, which contradicts
  RULED (1) ("BUILT NOW") of the same entry.
- FIX: keep the "My point was ... as well." sentence in the excerpt. Effort: trivial. Blast radius: §R.8 list only.

### RULING-4. R.1.16 says his words are "quoted in §R.11 rows 123-124", but they are quoted nowhere in full. CONFIRMED. Severity: doc.
- DRAFT, line 2126-2127: "HIS WORDS, in full, are COND-FAMILY's two entries (quoted in §R.11 rows 123-124); the
  load-bearing sentences: ...". §R.11 rows 123-124 (lines 3265-3266) quote NONE of his words. They give the entry
  title and RULED summaries. Row 120 does quote him, and row 62 shows the table's convention of quoting.
- Grep of the draft: 0 hits each for "Here's the thought" (match-is-rx's graph passage), "I see the issue"
  (read-is-constant's opening) and "I was thinking about this". So the full text of the two entries R.1.16 rests on is
  not in the draft. R.1.16, §R.8 and the R preamble carry only excerpts joined by "...".
- FIX: quote both entries in full in §R.11 rows 123-124, as rows 120 and 62 do, or point R.1.16 at the record. Effort:
  trivial. Blast radius: R.1.16 head, §R.11.

### RULING-5. The value-hole discussion's own words are absent, and his restatement "$y is ... a backreference" conflicts with the draft's settled "the label". SUSPECTED as an owner fork; CONFIRMED absent. Severity: design (decides an answer).
- RECORD ("OWNER, discussing value-hole"), HIS WORDS (4): "To restate, $y is a regex but of an anchored plain string
  THAT IS A BACKREFERENCE." (5): "given that most of our operations reduce the string set and $y is only the one, you
  are limited. No conditions. No &."
- DRAFT: none of his discussion words (1)-(5) appears, apart from "Can i use @y there and what does that mean?" and the
  `if(...)` text. Grep: 0 hits for "anchored plain string", "that is a backreference", "you could use the label",
  "manipulate it like a regex". §R.11 row 121 (line 3263) gives only "the manager's answers".
- WHY IT MATTERS:
  - Words (4) are the owner's own picture of `$y`: a backreference. Under backref-label (RULED, the same afternoon) a
    backreference reads PCRE's CAPTURE. R.1.15 (8) (line 2083) and (11) (line 2108) settle `${$y}` as the LABEL, and
    print answers that differ from `\k<y>`: `/(?:(?<y>\d)?-${$y};)*/` WHOLE `3-3;-3;` FAILS, while `\k<y>` HOLDS
    (2 / 2 / 2 of 21,845; R.1.15 (10)(a)). The record withdrew the manager's "`${$y}` equals `\k<y>`" because it
    contradicted pass-list-read's "an unqualified `$x` reads the label". That ruling was made about `$x` on the
    EXPRESSION side, before holes held values. The owner's own (4) and his "Plain rx in particular should work like pcre
    when we can" point the other way.
  - Two of his lines therefore meet at one printed answer, and the draft resolves it by the manager's reading without
    putting the meeting to him. G24-5 says a reading that a ruling's words contradict is a QUESTION.
  - The draft also does not say that his (5) "No &." is superseded by read-is-constant's "we were applying & to $y"
    before it calls value-filter legal (A5).
- FIX: quote (1)-(5) in §R.11 row 121. Add a §R.8 row (say **hole-reads-capture**): is a read in a hole the label
  (pass-list-read extended) or the backreference (his (4); backref-label's "like pcre")? Use the 2 / 2 / 2 and
  1 / 1 / 1 witnesses as the partition. Note (5)'s "No &" as overtaken in A5. Effort: small. Blast radius: R.1.15
  (8), (11), §R.8, §R.11 row 121, A5.

### RULING-6. **construction-line** (b) asks something his words already rule: regex operations on a read are not "under construction". CONFIRMED (a ruling presented as a reading). Severity: doc/design (an owner question that is not needed).
- DRAFT: T1-T6 (lines 2168-2173) mark the regex operations on a read "BUILT NOW, THE MANAGER'S READING (m2), asked
  **construction-line**". §R.11 row 124 (line 3266): "m2 NOT SUPPORTED by a record line (asked)". §R.8
  construction-line (b) (line 2772).
- RECORD, read-is-constant, HIS WORDS: "Semantically, $y is a regex of a single string. So operations that work on
  regex should work on it." And: "My point was that we were applying & to $y but you could also go the other way ...
  The "under construction" remark is that this is hard ...". He limits his "under construction" remark to the OTHER
  direction, and calls `&` on `$y` the direction "we were applying". RULED (2) and (4) of the entry say the same. The
  only build restriction left is match-is-rx (4), "functions like left() ... restrict them to constants now", and
  read-is-constant answered that a read is inside it ("Yes"). `|`, `&`, `!`, SEQ and quantifiers are not "functions like
  left()". Nothing leaves them under construction on a read, so m2 FOLLOWS. The draft's "no record line" misses that
  the "under construction" remark is explicitly scoped.
- FIX: T1-T6 on a read: "BUILT NOW (read-is-constant (2), (4): only the other direction is under construction)". Drop
  (b) from construction-line, or keep it as a confirmation only. §R.11 row 124: m2 SUPPORTED. Effort: trivial. Blast
  radius: T1-T6, §R.8, §R.11 row 124.

### RULING-7. T4 decides "a new error class, never 'requires module'". That is beyond his words and is not labelled as a reading. CONFIRMED (unlabelled). Severity: design (owner-level / general-mechanisms lens).
- DRAFT, line 2149-2154 (T4): "UNDER CONSTRUCTION IS ITS OWN ERROR CLASS: ... the compiler says so with an "under
  construction" error, never "illegal", never "requires module" (D26's module error refuses a construct pcrec does not
  implement; this one names a meaning the language HAS) ...". The changelog repeats "a named error class distinct from
  "illegal"".
- RECORD, his words: "the error is an "under construction" sign". RULED (4): "an "under construction" sign (not a
  refusal of the meaning)". He rules the MESSAGE'S SENSE: not illegal, the meaning acknowledged. He does not rule a NEW
  class beside D26's module error. The house's existing unbuilt-construct error, "requires module 'X'", ALSO names a
  real construct that pcrec does not build (CLAUDE.md: "unsupported constructs must fail with a clean "requires module
  'X'" error, never miscompile"). The draft's distinction ("refuses" against "names a meaning") is the lane's. Whether
  "under construction" is a second mechanism or a wording of the first is a choice for the owner. The memory rule
  "general mechanisms, not special cases" bears on it.
- FIX: label T4's class sentence "THE DRAFT'S READING". Name the alternative ("requires module '<x>'" worded as under
  construction) beside spellings 28 (line 2828), or ask it. Effort: trivial. Blast radius: T4, spellings 28.

### RULING-8. ANSWERS CHANGED's "his earlier words" column quotes the DRAFT's text (A11) and a RULED summary (A16) as if they were his words. CONFIRMED. Severity: doc.
- A11 (line 2206) quotes "is a value of the match that is not a substring" and "a VALUE, not a pattern" under the
  heading "his earlier words (the entry)". Neither string occurs in COND-FAMILY at b22285a36 (whitespace-folded exact
  search: 0 hits each). They are the draft's own §4.4 RULE ("A COMPUTED LABEL is a value of the match that is not a
  substring") and §2.x STRING SETS sentence. A3 and A8 do label their sources ("rev 26's text, the draft's"; "the
  record, the manager's"); A11 does not. A11's change also leaves §2.1's KIND TABLE (line 4116 on) saying a computed
  label is "as a macro" (LEAN P6-8 (a)), unmarked.
- A16 (line 2211) quotes "an unqualified $x reads the label" as his words. His words in pass-list-read are "I do want
  that. It makes sense and frankly pcre is wrong on this ...". The quoted phrase is the RECORD's RULED line ("an
  unqualified `$x` reads the LABEL"). It binds, but it is not his words. The value-hole discussion entry calls it "his
  ruling", which is accurate.
- FIX: A11: "(the draft's §4.4 RULE and §2 sentence; no owner words)". A16: "(pass-list-read, RULED line)". Mark the
  KIND TABLE's computed-label row. Effort: trivial. Blast radius: A11, A16, §2.1.

### RULING-9. GOALS: after dollar-condition is reversed, L28 carries no G0 class, and the draft treats the warning as optional, which the first-ranked goal does not allow. CONFIRMED. Severity: design (goals).
- §0 G0 (line 3546, the owner's STANDING CRITERION, ranked first): a look-alike pair that cannot do the same thing gets
  "exactly ONE class: ERROR or WARNING ..., BY DESIGN ..., or GAP (no diagnostic yet: an open defect ...); acceptance =
  no GAP row".
- Rev 27's L28 (line 3634): "DIFFERENT, BOTH LEGAL ... the warning **dollar-warning**", with diagnostic "legal, the hint
  UNRULED". None of the four classes is given. The difference is silent on the draft's own witness:
  `/(?<x>\d+)-/ & ($x & <5)` never holds, while `(x: <5)` holds WHOLE `3-` (1 / 132 / 132 of 364). So, unless a warning
  is given, it is a GAP. §R.8 dollar-warning (line 2767) argues "a warning moves no answer". That is true, but G0 makes
  the diagnostic a requirement, not a nicety. It also meets the standing criterion SAVING PEOPLE FROM THEMSELVES (CF
  12:45), which is exactly dollar-condition's original reason ("written where `(x: <5)` is meant").
- The same holds for `${$y}` against `\k<y>`. Rev 27 confirms that they part silently (2 / 2 / 2, 1 / 1 / 1; R.1.15
  (8)). L33 (line 3639) is still marked only for levels and value-hole status, so the new answer difference is not
  classed.
- §0 goals otherwise HOLD after one type:
  - G0b: one type REDUCES the kind count. The KIND TABLE already counted "captured string `$x`" as rx (RULED CF:858).
  - G3: backref-label restores PCRE's answers for `\k`, so it is STRENGTHENED.
  - G2: no change in kind. Value holes were already VM-level.
- DOES REV 27 DECIDE WHAT ONLY THE OWNER CAN? Yes, in four places:
  - the new error class (RULING-7);
  - the label in a hole against his "a backreference" (RULING-5);
  - arrays on the under-construction side, by T8's printed status (RULING-1);
  - the unclassed L28 row, which leaves G0's acceptance unmet without saying so.
- FIX: give L28 a class now, THE DRAFT'S READING "WARNING (dollar-warning), asked", and say G0 requires one. Give L33 a
  row for the label/capture answer difference. Effort: small. Blast radius: §0.1 L28, L33, §R.8 dollar-warning.

### RULING-10. Small verbatim deviations in quotes that rev 27 adds. CONFIRMED. Severity: doc.
- Line 2079 (R.1.15 (7)): "the runtime version that, while compiled, ..." The record has "that,while compiled" (no
  space). The draft adds a space inside a quote of his words. R.1.16 at line 2134 keeps it exact, so the two copies
  differ.
- Line 2208 (A13): "Values that produce counts (and not convert to rx)". His words are "a count whole must have values
  that produce counts (and not convert to rx)". The capital V is an unmarked change.
- Line 2888 (§R.9 STOP RULE): m4 is quoted as "array-lift extends to any FINITE rx". The record reads "(m4) array-lift
  extends from arrays the user writes to any FINITE rx". A clause is dropped without an ellipsis. These are the
  manager's words, not his, but they are presented as a quote.
- FIX: copy the exact text, or mark the cuts with "...". Effort: trivial. Blast radius: three lines.

### NEXT REVISION'S RULING TABLE (the five entries; "carried by" = the rev 27 line that should state it)
| entry / item | status for rev 28 | carried by |
|---|---|---|
| backref-label: `\k<h>` in a literal reads PCRE's capture | STANDS (RULED) | R.1.7 (b) line 1202-1204; R.1.13 line 1683-1701; §R.6 line 2437; §R.8 list line 2704 |
| backref-label: his scope QUESTION ("is the scope still local to the literal?") | the manager's answer "yes, unchanged" STANDS as an answer (his question, not a ruling); not yet confirmed by him | R.1.7 (b), §R.8 line 2704-2706 |
| backref-label m1 (narrows "last reference as labels" to which group) | STANDS (it is the only reading that keeps both rulings) | A9 line 2204 |
| backref-label m2 (an inserted part's group: its capture) | STANDS, a reading | A9, §R.11 row 120 |
| backref-label m3 (two groups of one name) | OPEN, **same-name-twice** | line 2768 |
| value-hole discussion: `$y` = the label read, in scope in its rx | NARROWED to OPEN for the hole: his (4) "a backreference" against pass-list-read (RULING-5) | R.1.15 (8), (11) |
| value-hole discussion: withdrawn "`${$y}` equals `\k<y>`" | STANDS as withdrawn IF the label reading holds; reopened by RULING-5 | R.1.15 (8) |
| value-hole discussion: case = the options at the hole | STANDS, and is RULED (in the form asked), not the manager's (RULING-2) | R.1.15 head, (10)(b), T12 |
| value-hole discussion: `${@y}` | OPEN, **array-in-hole** | line 2769 |
| value-hole "yes but": the form (expression, literal text, options at the hole, nothing = fail) | STANDS (RULED); restore the dropped clause | R.1.15 head line 2043 |
| value-hole: numeral width; unset | OPEN, **numeral-width**, **unset-in-hole** | lines 2765-2766 |
| value-hole: the condition (A or B) | SETTLED by match-is-rx: B | R.1.16 |
| match-is-rx (1) one type; (2) answers changed; (3) both directions in meaning; (4) build delayed, the "under construction" sign | STAND (RULED) | R.1.16 T1-T4, A1-A16 |
| match-is-rx m1 (`$x & <5` legal) | STANDS; its warning OPEN (**dollar-warning**), which G0 requires to be decided (RULING-9) | A1, L28 |
| match-is-rx m2 (superseded type ground) | STANDS | A2 |
| match-is-rx m3 (value-filter legal) | STANDS (his "we were applying & to $y"; his discussion "No &." overtaken, say so) | A5 |
| match-is-rx m4 (array-lift to any FINITE rx) | NARROWED: meaning extends to general regex (his "general regex"); order OPEN **lift-order** | A6, line 2771 |
| match-is-rx m5 (his `if` is the one `when`) | REVERSED as written; OPEN **value-test** | A12, line 2770 |
| match-is-rx m6 (unchanged rulings) | STANDS | A13, A16 |
| read-is-constant (1)-(4) | STAND (RULED) | R.1.16 T3-T5 |
| read-is-constant m1 (the line: single-value function on a non-single rx) | STANDS for general rx; its ARRAY consequence OPEN and not to be printed as the default (RULING-1) | T5, T8, §R.8 (a) |
| read-is-constant m2 (regex ops on a read built now) | STANDS, FOLLOWS from his words (RULING-6); drop construction-line (b) | T1-T6 |
| read-is-constant m3 (compile-time constants folded) | STANDS | T8, T9 |
| read in a count / class / option position | OPEN, **construction-line** (c) | T13-T16 |
| the error CLASS for under construction | OPEN (RULING-7) | T4, spellings 28 |

## PROBED-AND-HELD
- Quotes of HIS WORDS that rev 27 adds, compared character by character against the record or COND-FAMILY at
  b22285a36: 22 quote occurrences. EXACT:
  - R.1.15 head: the lean, "yes but", "let's use the unifying idea ... Change my answers to match.";
  - R.1.15 (1) "Semantically, $y is a regex of a single string";
  - (10)(a) "capture. Plain rx in particular should work like pcre when we can";
  - (11) "The rx should export the group";
  - R.1.16's two excerpts (match-is-rx's two passages, exact; read-is-constant's from "Yes" to "direction.",
    including "that,while", with only the opening "read-is-constant: I see the issue." omitted, under the heading "the
    load-bearing sentences");
  - R.1.13's full backref-label quote, including his question;
  - §R.8's backref-label, value-hole and match-is-rx excerpts;
  - §R.2's "My point was that we were applying & to $y";
  - A1, A4, A9, A10;
  - lift-order's "\d + 1 matches the digits 1 through 10";
  - array-in-hole's "Can i use @y there and what does that mean?";
  - spellings 28's "the error is an "under construction" sign".
  Not exact: RULING-3, -8 and -10 only.
- "CF hh:mm" citations added by rev 27: one, A7 "(12:15)". It resolves uniquely to "2026-11-17 OWNER — a constant is an
  rx whose enumeration has one member ... box clock about 12:15". The date is unstated but unambiguous: one 12:15 in the
  file.
- RULED labels checked against the entries' RULED lines, all MATCH:
  - §R.11 rows 120-124;
  - §R.9's six REV 27 rows;
  - §R.8's RULED rev 27 list;
  - R.1.16 T3 and T4;
  - A2, A4, A5, A7, A14.
  The exceptions are RULING-2 (a ruled clause presented as a reading) and RULING-6 (a reading that the words make a
  ruling).
- READING labels held: T1 cell "THE LANE'S READING" for condition/macro kinds; T13 and T14 "THE DRAFT'S READING"; A8,
  A10, A11, A16 "READING"; m5 and m4 "NOT SUPPORTED".
- read-is-constant (4) against match-is-rx (3)/(4) and R.1.16's line, HELD for general rx:
  - match-is-rx (3) defines the meaning in both directions, and (4) delays the build.
  - read-is-constant (1) puts a read inside "constants", and (4) names the other direction as the under-construction
    part.
  - T4/T5 draw the line at "single-value function on an rx that is not a single string". T8 and T9 put `\d + 1` and
    `left(\d+, 2)` under construction, with constants and reads BUILT NOW.
  - No contradiction, except the array cell (RULING-1) and the regex operations on a read (RULING-6).
- backref-label m1 (narrowing to "which group") follows: it is the only reading under which both "last reference as
  labels" (RULED, morning) and "capture" (RULED) stand. m3 is correctly kept OPEN: "capture" does not choose between
  two groups.
- The withdrawn `${$y}` = `\k<y>` reading: the draft narrows it as the record says (the control holds only where label
  and capture agree). The faithfulness problem is only RULING-5's unasked fork.
- when-peek (RULED: "A test pattern does consume") supports the draft's NOT SUPPORTED on m5. Draft and record agree.
- The count ruling ("values that produce counts (and not convert to rx)") and the count proposal (distribution;
  finite enumeration) are kept by T13's compile column (BUILT NOW). A13 "UNCHANGED" holds.
- free-name / backref-across-parts scope rulings: unchanged by rev 27 (A16; R.1.15 (11)). No sentence moves name lookup.
- §0 goals: G0b, G2 and G3 hold after one type (RULING-9 gives the reasons); G0 does not (RULING-9).

CRITIC COMPLETE
