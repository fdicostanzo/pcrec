# CRITIC RULING: predspec26 (review r47, 2026-11-18)

## Findings

### RULING-1 — CONFIRMED — answer — the "entailed" nullable-argument meaning ("at most one hit, the first") is false on libpcre2
- Subject: R.1.9 l.1278-1282 ("the one-pattern LOOP, the rewrite he ruled on, gives ONE, the empty hit at 0 ... the
  ruled premise (a rewrite) ENTAILS the loop's one hit, so that is the meaning kept (told, not asked)"); §R.8 (a)
  **nullable-meaning** l.2283 ("keeps the LOOP's meaning: at most one hit, the first, possibly empty"); §2.6 l.3845
  ("the LOOP's meaning kept (at most one hit, the first, possibly empty: entailed by the rewrite"); rev 25.1 text kept
  at l.3856-3857; R.11 row 80 ("the loop's one hit"). Record: the ruling is only "hit-carry: warning on nullable"
  (CF 3155-3156); the meaning is the manager's. The after-subject correction (CF 3636-3637, "the LOOP's one empty hit")
  repeats the over-generalization.
- Repro (ruling/nul.py; the model's own H5 pattern and callout, libpcre2 via pcre2h, WHOLE):
  `\A(?:[\s\S]*?(?<hit>\d*)(?C"r"))*[\s\S]*\z` — `a1b`: [``@0] (the subject's H5, one hit); `1a`: [`1`@0, ``@1];
  `11a`: [`11`@0, ``@2]; `1a1`: [`1`@0, ``@1]. Expected under the subject's sentence: one hit. Observed: TWO hits
  whenever the first hit is non-empty: the loop keeps every non-empty hit up to and INCLUDING the first empty one,
  which ends it (and then misses the later `1`@2 on `1a1` that find-all finds).
- Correct statement (what the run supports): "hits as find-all would give them until the first EMPTY hit, which is
  itself a hit and ends the list". The single witness `/\d*/` on `a1b` (H5) cannot tell the two statements apart:
  its first hit is empty. Effect: `occurrences(/\d*/, min = 2)` on `1a` is decided by this (two hits vs one), and
  the documentation line for the warning would describe the wrong loss.
- Effort: small (one sentence in three places + one witness row with a non-empty first hit + a CHECK). Blast radius:
  R.1.9, §2.6, §R.8 nullable-meaning, R.11 row 80, §0.1 L53's note; the record's correction entry (manager's) should
  be amended too (it is not the owner's).

### RULING-2 — CONFIRMED — design — product-order's "asked again" instruction dropped: its draft readings stay unasked
- Record CF 3186-3188 (product-order entry): "NOT TAKEN AS ANSWERED (the manager's caution on a bare "agree"): the
  rider (...) and the three draft readings listed with it. They stay the draft's readings, to be asked again in the
  next revision's question list." The rider was answered (removal, CF 3228) and one reading ("legal", CF 3202-3203);
  the join reading was withdrawn (name-hole). The rest were NOT re-asked.
- Subject: §R.8 (b) (l.2287-2296) has no row for them: grep of l.2171-2400 for product-order hits only the RULED list
  and other-holes. R.1.14 l.1624 says the opposite of the record: the member-list order "stays THE DRAFT'S, unasked:
  no witness found where it decides an answer the ruled order does not". Still THE DRAFT'S READING and unasked:
  copies share group numbers (branch reset, l.1601); a module refusal is not a removal cause (l.1630); ZERO values =
  `(?!)` (R.1.0 HOLE POSITIONS l.770); an illegal member in a PATTERN position a compile error of the whole (l.764).
- Fix: either a §R.8 (b) row carrying the readings the record says were listed, or a sentence in R.1.14 citing why
  the record's "asked again" is discharged (the "no witness" argument is the manager's to make to him, not the
  lane's to settle). Which three were "listed unless you object" is not in the record: say so.
- Effort: small. Blast radius: §R.8 (b), R.1.14, R.11 row 81.

### RULING-3 — CONFIRMED — design — the owner's "RULED BY THE OWNER, rev 26" list carries three manager entailments
- Subject §R.8 (a) l.2236-2262, headed "RULED BY THE OWNER, rev 26", lists: "**label-mark** closed by entailment"
  (l.2258); "**filter-captures** NOT adopted as a rule" (l.2253); "the read-out closed by **export-rule** (statement
  (5))" (l.2252-2253). Record: label-mark is "ALSO CLOSED THE SAME MORNING, by entailment, told to him and not objected
  to" (CF 3566-3569); filter-captures not carried is "NOT CARRIED (the manager's reading, said to him and not objected
  to)" (CF 3495-3497); the read-out closure is in "WHAT THIS CLOSES (the manager's statement of the state, to be checked
  by the next revision)" (CF 3489-3491). None is his words.
- Same promotion in prose: R.1.13 l.1394-1396 states the read-out closure with no marker ("is closed by
  **export-rule** (5) (below): the caller's captures follow the visibility rules, so a name two parts both make public
  is an AMBIGUOUS REFERENCE for the caller as for the program"); l.1421-1422 puts "filter-captures" inside the ruling's
  own "it closes ..." clause (the record's heading, CF 3474, names only export-scope and path-and-ambiguity). (l.1397
  does mark filter-captures as the manager's reading: the two passages disagree on its status.)
- Fix: move them under a "CLOSED BY THE MANAGER'S ENTAILMENT (told, not objected to)" sub-list, as R.11 row 103 and
  row 93 already label them. Effort: trivial. Blast radius: §R.8 (a), R.1.13.

### RULING-4 — SUSPECTED — design — the read-out reading ("an ambiguous reference for the caller") leaves the caller's answer undefined
- Subject l.1395-1396 and R.1.0 `&` OPERAND row (l.744: "a name two operands both surface is an AMBIGUOUS REFERENCE
  where it is referenced (label-flow (4)), for the caller too (export-rule (5))"); R.9 l.2440 withdraws rev 25.1's
  reading (e) by it. Record: the owner agreed only to the visibility statement "the caller sees the public labels of
  the top-level program plus paths through its part labels, never a private one" (CF 3467-3469, "The caller's
  captures: agree"); "an ambiguous reference for the caller as for the program" is the record's gloss (CF 3469-3470)
  and the manager's WHAT THIS CLOSES (CF 3490-3491).
- The gap: an ambiguous reference is an error "where it is referenced"; the caller does not reference at compile time.
  For `A & B` (A := `/(?<h>\d)\d/`, B := `/\d(?<h>\d)/`, rev 25.1's (e) witness), nothing in the subject says whether
  the PROGRAM is a compile error, `h` is absent from the captures, or reading `h` fails at run time; and the subject's
  own l.1388-1389 ("a collision nobody references is harmless") reads, where its premise applies, as "not an error".
  Rev 25.1's (e) had a printed answer (WHOLE `12` h = `1`); rev 26 withdraws it without printing a replacement.
- Confirm: state the caller-facing outcome for the (e) witness and check it against l.1388-1389; it is a question for
  him (it was never put), not a derivation. Effort: small. Blast radius: R.1.13 PATHS, R.1.0, R.9, the API spec later.

### RULING-5 — SUSPECTED — design — R.1.0's `0` column for a sequence operand and a pattern hole is an unmarked reading that the zero addendum's reading (2) and free-name point the other way
- Subject R.1.0 l.745 (SEQUENCE OPERAND: `0` names "the entire match of the composed rx") and l.752 (PATTERN HOLE:
  "the entire match of the composed rx (the outer rx's `0`)"), neither marked as a reading, no run cited. The same
  hole row's namespace column says "inside X, X's own namespace (free-name)".
- Record: his words "It is always the entire match of the rx however it is composed" (CF 3124-3125) do not say WHICH
  rx for a condition written inside a part; the manager's reading (2) (CF 3130-3132) reads "the rx" as "the rx the
  condition is attached to" (a loop body's or hit's own match), and R.1.0 adopts that for loop bodies and arguments
  (l.747-748) but the opposite for parts and holes.
- Where they decide answers (hand-worked, not run): X := `/\d+/ & (0: <5)` used as `/a${X}b/` or `X SEQ "b"`: "the
  rx it is attached to" tests X's own digits; "the composed rx" tests `a..b` / `..b`, which is not yet known at X's
  point (the very gap **zero-in-sequence** l.2296 raises for a condition AS a sequence operand). Possibly the column
  means only a `0` written at the composition's own level; then the cells must say so.
- Confirm: one PART N-style run of the X example under both readings. Effort: small. Blast radius: R.1.0 two cells,
  zero-in-sequence's scope.

### RULING-6 — CONFIRMED — doc — after-subject correction (2)/(3): rev 26 half-says it, and says the owner was not shown what he was told
- Correction CF 3638-3645: "as a whole value every spelling of 'anything' agrees" is FALSE; "The owner WAS TOLD the
  false sentence as the reason a lone complement could be legal when matching"; "his own example `any := /.*/` would
  not accept a multi-line value".
- Subject: R.1.4 l.931-933 and §R.8 l.2387-2388 soften it to "holds only for spellings that match a newline" (a true
  qualified sentence; does not name his `/.*/` as a failing spelling). §R.8 l.2384-2386 says the simulation "is not a
  table he was shown as an answer"; the correction says the whole-value clause WAS put to him as the lean's reason.
  His DISCUSSION example (`any := /.*/`, `any & not seven`, CF 3596-3599) and "I mean in the context of a match"
  appear only as R.11 row 105/106 titles; the body never states his example.
- Fix: R.1.4 and the **anything-text** row (l.2294) name his `/.*/` as one candidate and give its 90-of-121 WHOLE
  difference; l.2384-2386 say the clause was told to him as a reason (no ruling rests on it: lone-complement-match
  ruled against the lean). Effort: trivial. Blast radius: R.1.4, §R.8.

### RULING-7 — CONFIRMED — doc — value-hole: the record's "eleven uses" vs the subject's "7 live uses MARKED"
- Record CF 3265: "The eleven uses in the draft are marked as resting on an unruled form until then." Subject l.2119:
  "12 lines with `${$`; 7 live uses MARKED". `grep -n '\${\$'` gives 22 lines; 8 carry the `[REV 26: **value-hole**`
  mark. Unmarked and not history: §5.4's mark table l.4998 (the paused `^` sigil's error text advises "write
  `${$h}`"). The count gap is unexplained either way. Fix: reconcile the count in l.2119 against the record's eleven
  and mark or exempt l.4998. Effort: trivial. Blast radius: one line.

## RULING TABLE FOR THE NEXT REVISION (one row per CF 2026-11-18 entry; diffed against §R.11 rows 76-107)

| row | CF line | entry | label (record) | state | §R.11 agrees? |
|---|---|---|---|---|---|
| 76 | 3091 | correction "right side of `&`" | MANAGER | stands; hole-in-filter answered (row 87) | yes |
| 77 | 3102 | number-names | RULED | stands | yes |
| 78 | 3123 | zero addendum | RULED (+MINE 1,2) | stands; MINE (2)'s scope vs R.1.0 parts open (RULING-5) | yes |
| 79 | 3134 | hit-carry | RULED | stands | yes |
| 80 | 3153 | nullable: warning | RULED (+MINE) | warning stands; MINE meaning RETIRED; its replacement wrong (RULING-1) | partly |
| 81 | 3161 | product-order | RULED (2); scope CORRECTION; IDEA (3) | stands; rider answered (84); draft readings still owed to him (RULING-2) | partly |
| 82 | 3194 | cartesian / legal | OBSERVATION, IDEA, RULED YES (legal) | stands | yes |
| 83 | 3210 | name-hole | RULED; PRINCIPLE; IDEA | stands; rev 25.1 join retired | yes |
| 84 | 3228 | removal | RULED (+MINE) | stands | yes |
| 85 | 3238 | value-is-pattern | (2) RULED; (1),(3) LEAN; IDEA | (1) closed by 86; (3) open (value-hole) | yes |
| 86 | 3267 | array-lift | RULED | stands; plus-operands open | yes |
| 87 | 3287 | hole-in-filter | RULED (1),(2); description (3) | stands | yes |
| 88 | 3311 | backref-across-parts | RULED (+MINE a-d) | stands; MINE (a),(d) retired by 89 | yes |
| 89 | 3327 | clarification: last mention | RULED | stands; its hand cases REVERSED by 91 | yes |
| 90 | 3344 | reopened | DISCUSSION | closed by 91 | yes |
| 91 | 3354 | free-name | RULED (1),(2); MINE (3); OBSERVATION (4) | stands; parameter idea open | yes |
| 92 | 3380 | path-and-ambiguity | (1) RULED; (2) open | (2) closed only by MANAGER entailment (RULING-3/4) | partly |
| 93 | 3401 | filter-captures lean | LEAN | not adopted (manager's, not objected) | yes |
| 94 | 3415 | export proposal | PROPOSAL | became export-rule (1),(3) | yes |
| 95-97 | 3428/3438/3458 | export-scope discussion | DISCUSSION | closed by 98 | yes |
| 98 | 3473 | export-rule | RULED (6 statements) | stands; WHAT IT CLOSES = MINE | partly (RULING-3) |
| 99 | 3501 | `_a` clarification, `[_ = A]` | RULED | stands | yes |
| 100 | 3513 | `[_ = A]` confirmed | RULED | stands | yes |
| 101 | 3522 | condition-in-sequence | RULED | stands | yes |
| 102 | 3539 | quantified-condition | RULED (exception) | stands | yes |
| 103 | 3554 | lookahead-labels | RULED; label-mark ENTAILED | stands; label-mark is manager's | yes (row), no (§R.8 list) |
| 104 | 3571 | complement-place | RULED; PRINCIPLE | stands | yes |
| 105 | 3595 | complement as filter on anything | DISCUSSION | closed by 107; MINE whole-value clause FALSE (CF 3632) | partly (RULING-6) |
| 106 | 3609 | "in the context of a match" | DISCUSSION | closed by 107 | yes |
| 107 | 3618 | lone-complement-match | RULED | stands; anything-text open | yes |
| 108 (new) | 3632 | MANAGER CORRECTION, three readings | MANAGER | (1) applied in rev 26 but mis-stated (RULING-1); (2)(3) half-applied (RULING-6); asks **anything-text** (already in §R.8 b) | n/a (after subject) |

## HAND MAPPING of CF 3632-3645 (after the subject commit)
- (1) nullable "keeps PCRE's meaning ... as the empty search does": subject ALREADY SAYS the corrected thing (l.1278-1282,
  2283, 3845, R.11 row 80: "NOT SUPPORTED as worded"); but both subject and correction then state "one hit", false when
  the first hit is non-empty (RULING-1). Reopens: the stated meaning of a nullable argument (and the warning's text).
- (2) "every spelling of anything agrees" (whole value): subject l.931-933, 2387-2388 say "holds only for spellings that
  match a newline" — corrected in substance, not in word; silent that he was told it (l.2384-2386 says the opposite).
- (3) the lazy clause: subject ALREADY SAYS it (l.2294, 2387: "NOT reproduced"; R.11 row 105). `any :=` / `/.*/` as
  his example: SILENT (RULING-6). Reopens **anything-text**: already asked at l.2294 with `/[\s\S]*/` as the manager's
  reading; the nullable-warning text (`pcrec.` name) is untouched by the correction (l.1282).

## PROBED-AND-HELD
- Entry coverage: 32 CF entries (3091-3618) map one-to-one, in order, onto §R.11 rows 76-107 by title; 0 missing,
  0 extra. Labels: 29 of 32 rows carry the record's label (RULED / LEAN / PROPOSAL / DISCUSSION / OBSERVATION / IDEA)
  exactly; the 3 partial rows are RULING-1/-3/-6, not mislabels of owner words.
- Owner quotes verified word for word against CF (whitespace-normalized; leading slug or "In practice," trims and
  marked "..." elisions accepted): 46 quotes in R.1.0 (22), R.1.4 (7), R.1.7/R.1.9 (3), R.1.13 (8), R.1.14/R.1.15 (6)
  and the §R.8 RULED list (12, overlapping). 0 inserted or dropped clauses. Script: ruling/quotes.py (86 unmatched
  spans, all quote-parity artefacts or non-owner text, each inspected).
- No DISCUSSION/LEAN/PROPOSAL/IDEA carried as RULED among owner words (value-hole LEAN, filter-captures LEAN, the
  export proposal, cartesian / interim product / modulus IDEAs, `x.0` and zero-in-sequence left open); no RULED carried
  as open. number-names' shared-name sub-point: in the leaning he said "exactly" to (CF 3106-3107), so not a reading.
- Manager readings marked as readings: zero addendum (1),(2) at R.1.0 l.744/747; removal's never-matches; count
  non-count error ("THE MANAGER'S READING of 'must'"); "sql" autocorrection; quantified-condition scope; lookbehind;
  free-name state; `[_ = A]` reading (then confirmed, row 100). Held, 9 of 9 (the exceptions are RULING-3/-5).
- Withdrawn premises: the r43-withdrawn "nearest pattern to its left" and "numbers not subject to ambiguity" do not
  survive in rev 26 R.1.13 (l.1510-1515 mark them withdrawn); backref MINE (a),(d) withdrawn and the two hand cases
  reversed (REF1, REF3) as CF 3373-3375 says. Held.
- Drill: ruling/nul.py, 4 texts on libpcre2 (RULING-1).
CRITIC COMPLETE
