# Round absfold (review r28): the manager's dispositions (2026-11-16, session 136, box clock 15:2x)

Every PROPOSED disposition in review.md is ACCEPTED as proposed, with the rulings and readings below. All "manager's
readings" are labelled as the manager's in the note (never as the owner's) and are told to the owner. Three of the
manager's 14:50 readings (COND-FAMILY.md tail) FALL or MOVE here and are named so in the note and to the owner:
(c) WITHDRAWN, (d) WITHDRAWN, (a) RESTATED.

- A, MARK-DOMAIN: OWNER QUESTION **mark-domain**; NOT decided by the manager. The manager's 14:50 reading (c) "any
  text" is WITHDRAWN (its stated reason is false, and it lets a marked label beside a complement set hold on every
  absence). The fix lane states the domain ONCE as an open parameter with the three candidates (ANY text; the texts
  the label's GROUP can match, read from the group's own text; the VALUES THE LABEL CAN TAKE in some match of the
  pattern, i.e. the label's value language in its context), RUNS all three over the same populations (at least (AR),
  (TM2), (ZJ), (ZE), (RZ), the complement drill and the two-spellings drill), and drafts the question. The manager's
  LEAN, labelled as a lean that rests on those runs: the third candidate (it keeps a text the label can never hold
  from witnessing an answer, and it cannot split two spellings of one pattern); it is retracted if the runs show a
  population where it splits equal spellings or equal sets. Until answered, (AR), F1's sentence, row 55, §4G.6 (8),
  row 64 and the 2092 line cite the one open parameter, never a domain.
- B, (AR) RECORD CELL: FIX-NOW as proposed (one cell for one label, record and joint alike: F1).
- C, `all(...)`: FIX-NOW, the manager's reading, RESTATING 14:50 (a): `all(c)` := c with every label marked, read
  F1. Hence `all((x: S))` = `(x?: S)`; (6)'s parenthesis, the (LI) count and row 58's boundary sentence are corrected;
  absfold_check.py's vacuous `al0` is replaced by the definition and the counts re-run. If the re-run shows the
  definition breaks record = `&` or brings back a `?`/`*` spelling split, STOP and report (do not repair).
- D, `?` AS A LOOP: OWNER QUESTION **optional-as-loop** (it touches his own remark, CF:1599). The manager's lean: a
  quantifier with upper bound 1 is NOT a loop for the pairing rule (it can pair nothing: at most one value), so a
  record over two optional fields answers and `x?` = `(?:x|)`. The fix lane drafts the question with both readings
  run over the same subjects ((OP)-style, the 36 / 11 of 259 counts) and marks every sentence that depends on it.
- E, THE MARK INSIDE `some`/`count`: FIX-NOW, the manager's reading: 14:50 (d) (a compile error) is WITHDRAWN; a
  marked absence is COUNTED by the mark's one meaning (F1), in `some`, `count`, `occurs.*` and inside `all` alike,
  and through expansion (a macro or a record expands first, then the same rule). This also supersedes the 14:31
  sub-choice "not counted" (row 56, row 65 (g), §8 item 4, §4G.6 (4)). 14:50 (f) is restated: the all-looped record
  with an optional field per item HAS a one-condition spelling, `occurs.none(((h, m?): !R))`; re-run its 0 of 259.
  Its answer depends on the domain (A): state that dependence in one line. No new diagnostic row.
- F, THE 14:50 READINGS IN THE NOTE: FIX-NOW as proposed (the hand mappings RULING-3..7, CHANGETAB-5), with (a), (c),
  (d), (f) as moved above. RULING-4: zero-pass-empty closed by (b) is stated as the manager's reading "told 14:50" and
  stays on the owner's list until he assents.
- G, NEGATION OVER A MARKED LABEL: FIX-NOW (doc). "Unmarked" at the four sites; the look-alike row for the marked pair
  is DIFFERENT: BY DESIGN (the manager's call: the mark is on the label, so `!` outside and `!R` inside are two
  conditions; state the answer under each domain candidate if it differs); row 61 scoped to zero passes.
- H, UNTAGGED SUPERSEDED SENTENCES: FIX-NOW for §9 rows 14 and 28; the light tag pass on the note IS done by the fix
  lane (the sites listed in H only; no rewrite).
- I, §9 GAPS AND CITES: FIX-NOW as proposed.
- J, SMALL TEXT ERRORS: fixed in the note now by the fix lane (cheap), not left to rev 20.
- K, THE GENERAL FORM (an absent label reads as a candidate set D: unmarked ∅, default {v}, mark = the domain):
  ACCEPTED as the way the rule is STATED, on one condition: the fix lane first re-runs (AR)/(TM2)/(ZJ)/(ZE) under the
  form and gets 0 differ; otherwise report and leave the present statement. No new spelling is exposed
  (predicates_future.md item 3 keeps its own trigger). One merged warning for the never-absent mark and
  `default.unused` (a) is NOTED for rev 20, not decided here.
- L, GOALS: DOC. The note lists "simplifying semantics", "saving people from themselves" and the 13:52 principle as
  the OWNER'S STATED CRITERIA with their measurable forms, UNRANKED; their rank against G1-G4 is the owner's and is
  NOT asked now (no finding in this round turns on the rank once A and E are decided on their drills).
- D27 recommendation: NOTED for the day the joint condition gets a build go.

Process changes (.coord/process.md): ALL THREE ACCEPTED (skill §4 simulate lens: the DOMAIN drill; skill §4 ruling
check: "readings written after the subject's commit" as an explicit sub-part with hand mapping; COMMON template:
pre-create findings files always). The two "Lessons for the guide" go to docs/dev/guide/critics.md. The framework
note goes to docs/dev/meta/coordinator_framework.md.
