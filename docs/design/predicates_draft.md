# The predicate language ([COND-FAMILY] #6): a preliminary specification for critical analysis

## Changelog

- **rev 13 (lane predspec13, 2026-11-15).** Applies the confirming review r14 on rev 12 (draft
  `$PCREC_TMPDIR/scratch/crit-predspec12/review.md`, filed by another lane) and folds the owner's three entries after
  rev 12 (CF:1026-1062 on main) and the fourth that arrived during it (CF:1068-1081 on main, rulings R-1: a per-call hit
  label name, O55 (i) RESOLVED; NO count warning, O63 CLOSED, L66 GAP -> BY DESIGN; the owner's hole example
  `999${/\d+/ & <100}999` an acceptance row). RULINGS: `search` is renamed `occurrences` everywhere outside quotations and history
  (§2.6, §8, §0.3; O61 CLOSED; the label `hit` kept, its name not ruled); `anchored` has the EXACT ends,
  `anchored(rx) := /\A(?:${rx})\z/` (§8; O62 CLOSED; L68 moves DIFFERENT -> SAME; E-HTTP respelled `anchored(block)`,
  the same text); under the rx-`&` switch ON `&` is the operator exactly where `|` means alternation, a literal is
  `\&` or `[&]` (§11; O60 (d) CLOSED); BOTH operands of `&` are filter roles and an explicit anchor in an operand
  draws the warning `anchor.operand` (§11, §7.1; review r14 F1). THE OWNER'S CONDITION: §11 THE AMPERSAND RULE
  TESTED BY POSITION, eight positions with oracle rows (`docs/dev/lanes/predspec13_anchor.py` / `.out`): sensible in
  every position; `\b` and edge lookarounds stay the edge-assertion ERROR. REVIEW r14 FIXES: F2 (the general form of
  what opens a scoped match, the hole sentences narrowed, STRING SETS' four set positions vs three filter roles),
  CENSUS-1 (rev 11's paragraph marked superseded), CENSUS-3 (the library family lower case, "gap-bodied"),
  CENSUS-4 (`$` without `(?m)`), CENSUS-6 ("or what it reads" marked LEAN; §2.7's heading), CENSUS-7 (the name audit
  in O61, `capture` classed), and DOC CENSUS-2 ("span" in the draft's voice), CENSUS-8 ("searched" for the mode),
  `\Z` in the list of ends. §0.1: L68 SAME; L11, L41 BY DESIGN -> WARNING; NEW L70 (`P` vs `P & /(?s).*/`), L71 (the
  same in a hole). §13: NEW O64 (`anchored` in a hole: the "filter role" wording differs there, so the definition is
  the `\A`/`\z` text), O65 (the warning in every filter role); owner questions (2), (4) ANSWERED; DECIDED BY THIS LANE
  (22)-(29).
- **rev 12 (lane predspec12, 2026-11-15).** Folds the owner's evening ruling ONE ANCHORING RULE, `anchored()`, AND
  THE NAMING OF PROVIDED TRANSFORMS (CF:1001-1024; the manager's advice he agreed to, CF:1009, "Ok I agree"). (A)
  ANCHORING, restated everywhere the draft spoke of it: ONE rule, a FILTER (the filter side of `&`, a `label:`
  condition) matches the WHOLE value, everywhere else an rx is unanchored as in PCRE (a final pattern is searched);
  `^`/`$` are the ends of the SCOPED MATCH, plain PCRE with the value as the subject (§11 THE ONE ANCHORING RULE, §0.3
  "scoped match"). No transform "removes" anchoring any more: `contains`/`search`/`startsWith`/`endsWith` are plain
  GAP bodies (§2.6, §8). `anchored(rx) := /^${rx}$/` ADDED (§8; identity in filter position, L69). The lean to fold
  `startsWith`/`endsWith` into `search` is WITHDRAWN (§8, §13 FIXB-9 (2)); the rejected alternative (an explicit
  anchor switching the implicit one off) recorded (§11, L69). ANSWER MOVED: L63 (`$` is PCRE's, so `contains(/err$/)`
  accepts `err\n`; rev 10's exact-end lean, SIM-5, withdrawn as an extra rule); NEW L68 (`anchored(x)` vs `\A...\z`
  in a final pattern, on a final newline) and L69; every other row and §12 case re-applied, unchanged in answer
  (§0.1, §12 REV 12). (B) NAMING: the naming rule now binds every PROVIDED transform (§2.7); `search` fails it and is
  marked OPEN, name under review, spelling kept (§2.6, §8, §13 O61). (C) §13: owner questions carried (O60 (d), O55,
  O63), question (3) withdrawn by the ruling; new O61 (a name for `search`), O62 (`anchored`'s ends), O63 (the count
  warning, restated under the one rule). Oracle runs: `docs/dev/lanes/predspec12_anchor.py` / `.out`.
- **rev 11 (lane predspec11, 2026-11-15).** Applies review `docs/dev/reviews/2026-11-15-r12-predspec10.md` (critic
  texts in its directory): its 15 FIX-NOW findings with the picks of its DISPOSITIONS RULED (manager); the refuted
  part of CENSUS-6 (a) left as it stood. ANSWER-LEVEL (SIMULATE-1): under the ruled anchoring a directly applied
  `/^foo/` is exactly `foo`, so L7, L11, L13, L15, L41 move from SAME to DIFFERENT: BY DESIGN, §2.7, §7.1, §11 and
  E-CTX-1/5 are respelled, and every SAME row and every §12 case is re-applied under the ruling (§0.1, §12 REV 11).
  DESIGN: the second argument refusal NARROWED to its reason (a reader that can run with its group unset in the
  current hit; `/(.)\1/` admitted; SIMULATE-2, LEAN); one-hit vs every-hit/selection marks split (CENSUS-8) and the
  selection written in the path, `$m.hit[(g: "x")]` (CENSUS-1, LEAN); `$` reads the VALUE(S) of a label path
  (CENSUS-11); `balanced` respelled with its literal's own named group, so rx text has exactly two non-PCRE marks
  (CENSUS-2); under the rx-`&` switch ON PCRE's own constructs (`(?&name)`) keep their meaning and a literal `&` is
  `[&]`, rev 10's `\&` rewrite withdrawn (CENSUS-3: an OWNER QUESTION, §13 O60 (d)); `${` in a class or `\Q...\E`
  (CENSUS-4); an rx-text `&` takes the whole concatenation, new L67 (CENSUS-5); a duplicate label in a loop is a
  repeated label (CENSUS-12). DOC: SIMULATE-3, CENSUS-6 (b)-(d), CENSUS-7 (MARK TABLE case lists, `+`), CENSUS-9 (one
  mark for the per-match rule), CENSUS-10 (transform vs filter modifier; "searched").
- **rev 10 (lane predspec10, 2026-11-15).** Applies review `docs/dev/reviews/2026-11-15-r10-predspec9.md` (critic
  texts in its directory) with its DISPOSITIONS RULED (18 FIX-NOW, 19 DOC, FIXB-8 PLAN, FIXB-9 NOTED), and folds the
  owner's last three COND-FAMILY.md entries (CF:962-1000, the last on main after this lane's base; rulings file R-1): `min` is 0 or 1 and the ambiguity warning is for the
  author's own text (CF:962-971); the five open items (CF:972-988: one-hit access needs captures, ONE measured
  budget, a count is a numeral string, `&` in rx text ALL OR NOTHING by a module or option); filters stay anchored at
  both ends (CF:989-996); a condition on a label that never ran is decided PER MATCH (CF:997-1000). NEW: §2.6 THE TWO ARGUMENT REFUSALS (nullable, and a group read by a backreference or
  conditional inside the argument, SIM-1) and THE ITERATION'S OWN VALUES (SIM-2); §4.2 THE BOUNDARY restated PER
  MATCH (FIXB-2; RULED, CF:997-1000); §4.5 MEMBERSHIP IS EXTENSIONAL, A CONDITION READS THE SPELLING (FIXB-1) and
  the search-mode consequence (FIXB-7 (d)); §11 THE MARKS INSIDE `/.../` (`${` always a hole; `&` by the switch;
  CENSUS-2, CF:981-984); §0.1 L60-L65. Changed: §0 marks (the hedge criterion, FIXB-5), §0.3 (transform vs filter
  modifier, span, search vs searched, run-time input), §2.2, §3.4, §4.3 (`$` on a repeated label, `[n]` by position),
  §5.2/§5.4 (defaults in a head, the `${ }` positions, `#`, one meaning per position), §5.3 (`each` passes the
  ordinal by name), §8 (scoped library bodies), §12 (every case re-checked in its real mode; E-HTTP anchored; E-DEPTH
  marked), §13 (C23, O39, O40, O49, O50, O58, O59 RESOLVED; O28's zero-iteration half RESOLVED by CF:997-1000, not by the record; O53, O55, O57
  restated; O60 new).
- **rev 9 (lane predspec9, 2026-11-15).** Folds the owner's last two COND-FAMILY.md entries (CF:927-961): SEARCH
  FOLLOWS PCRE'S MATCHING, a name bound to a transform's result binds the transformed rx, hit-count control by
  settings (CF:927-947); and ONE READING EVERYWHERE (PCRE's), ambiguity the author's to validate, no `max` on search
  for now (CF:948-961). REWRITTEN: §4.5 (ONE READING: a condition on any label, set once or in a loop, follows PCRE's
  own parse; the 11-14 some-parse rule SUPERSEDED; what the default level computes for free and what it builds at a
  cost; the condition never steers the parse), §2.6 (`search(x, min = 0)`, `contains(x)` = `search(x, min = 1)` in
  what it accepts and ONE definition, zero hits decided by `min`, hand checks re-run for min 0 and 1), §4.2 (the
  boundary between an UNSET label set once and a loop with zero iterations, stated once), §4.3 (no conflict mark;
  zero iterations: a plain condition holds), §5.6 (validating an ambiguous label's reading with the existing
  assertions: no new form needed), §6.1 (the default level and PCRE's reading), §7.1 (`label.ambiguous` text), §8
  (`search` with `min`, `contains` by `search`, lazy `endsWith`). §0.1: L16, L34, L36, L51, L53 restated; L55-L59
  new. §13: C36, O33, O54 (the `d :=` half) RESOLVED; O28 restated; the manager's calls on O53, O31 (`index`/`label`),
  C7 (`=>`) and the library `(?s)` marked LEAN (manager); O57 (the OWED MEASUREMENT of the one reading's cost), O58
  (`min` above 1, `max`), O59 (the library bodies' own reading) new.
- **rev 8 (lane predspec8, 2026-11-15).** Folds the owner's three latest COND-FAMILY.md entries: the search result
  is the ARRAY of all results (CF:880-887); his answers to review r8's four questions (CF:888-901: typed parameters
  OUT of phase 1, `:` narrows only; ARRAY and MAP are INTERFACES applied to a thing, never values that can be
  created; a module is described by its MAP interface; `.` has ONE meaning); and SEARCH IS A TRANSFORM (CF:902-926:
  `search` a library transform of the `contains` family, `~` and `!~` WITHDRAWN, the hit a REPEATED LABEL,
  `some(...)`/`all(...)` the one spelling, `occurs` counts only, same hit by record, the definition requirements, the
  array interface over ANY repeated label's iterations). REWRITTEN: §2.6 (now SEARCH AND CONTAINS ARE TRANSFORMS, with
  both definitions and their hand checks), §3.4 (spelled arrays vs a repeated label's iterations), §4.3 (repeated
  labels: the general home of plain conditions, `some`, `all`, `count`, `occurs`, same iteration by record, the
  array interface over iterations), §8 (`search`, `contains`, `some`, `all`, `count`, `occurs`), G4. "View" becomes
  INTERFACE throughout (one word, §0.3); §9's cut "interfaces" become DECLARED TYPES (the word now names the array and
  map interfaces). §0.1: L16, L17, L31, L36, L50, L51 rewritten, L52-L54 new. Mark table: `~` and `!~` leave; `.`
  RULED one meaning; `:` narrows only in phase 1. §13: O12, O29, O48 (phase 1), C28 RESOLVED; O31, O46, O50, C29,
  O28, O36, O52 restated; C36 (a CONFLICT: the priority parse vs §4.5's some-parse rule) and O53-O56 new.
- **rev 7 (lane predspec7, 2026-11-15).** Applies the RULED dispositions of review
  `docs/dev/reviews/2026-11-15-r8-predspec6.md` (P6-1..P6-18) and folds the owner's note "a search result is the
  ARRAY of all results" (CF:880-887), with his own example as §2.6's illustration. NEW: §0.3 WORDS (one word per
  thing, P6-15); G0b (the 11-15 criterion as a goal, its check the MARK TABLE and the KIND COUNT, P6-9); §2.1 KIND
  TABLE and the typing sentence for `& | !` (P6-8); §3.4 SPELLED vs MATCH-TIME arrays (P6-7); §5.4 rows for `( label:
  S, ... )`, the section `(& f)`, `.` and `$`, and the OTHER MARKS table (P6-3, P6-6, P6-9, P6-12, P6-14); §12 TWO-WAY
  CENSUS (P6-9); §0.1 L48-L51 and a class (ERROR / WARNING / GAP / BY DESIGN) on every DIFFERENT row; §13 O48-O51,
  O31 widened to the whole dot family, and O52 FAMILIES (P6-4, P6-5, P6-7, P6-12, P6-13, P6-16). Changed: the
  hole-as-guard clause deleted (P6-1); the `[ ]` meaning stated once and the false tuple reason dropped, C25 back to
  OPEN, O47 re-argued (P6-2); `^`/`$` of a filter passed as an argument (or in a hole of a filter's body) are the ends
  of the span the enclosing filter role filters, `contains(/^err/)` = `startsWith("err")` (P6-5, LEAN, O49); the
  glossary applied through the text (P6-15: operand, comparison set, entry extent, item rx, effect, captured string); `$a.b.c` = `$(a.b.c)` (P6-6); L16/L17 rewritten (a search result is an rx, a test is a condition) and
  C29's premise corrected (P6-7); RULED marks narrowed to the owner's quoted words (P6-10); ill-formed examples fixed
  (P6-11: L2, L9, L36, L42, C28, §2.5, §7 `balanced` and `records`, E-CAL's bare `dim`).
- **rev 6 (lane predspec6, 2026-11-15).** Folds the owner's "type picture" ruling (CF:846-878): two value kinds (rx,
  macro), a condition is a macro, "filter" is a ROLE (CF:858); one input rule, a call fills parameters and `&` fills
  the one subject slot (CF:860); the COMMA means only "next entry" and the BRACKET says how entries relate, `[ ]` any
  one, `( )` all together, `=` labels an entry, `:` constrains an existing label (CF:863); a RECORD is never a value,
  appears only in a call, a condition or the left of a binding, is the written MAP view, one-way (CF:866); a search
  returns an rx (CF:873). NEW: §5.4 is THE grammar summary for `,` `( )` `[ ]` `=` `:` (every other section points
  at it); §0.1 L43-L47; §0.2 destructuring line; O41-O47. Changed: §2.1, §2.2, §2.3, §2.6, §2.7, §3.1 (the map
  literal `(x = /foo/ | y = /bar/)` withdrawn, LEAN), §3.2, §3.5, §4.1 (the condition binding restated in record
  terms), §4.2 (example respelled), §5.1, §5.2, §7 (what a module is, O46), §8 (tuple example), §12 (all twelve
  re-checked: unchanged), §13 (C19, O30 resolved; C5, C8, C18, C25, C29, O40 restated), §14, §15.
- **rev 5 (lane predspec5, 2026-11-15).** Folds COND-FAMILY.md from the mapping ruling (CF:749) to the end: C33-C35,
  the `!` entries and the ten 2026-11-15 entries (CF:761-845; a later entry wins over the one it corrects), and fixes
  what the rev 4 audit (audpred) found in the spec. Status marks are RULED (record line) / LEAN / OPEN. NEW §0.2
  PHASE 1 SCOPE, §0.1 L41-L42, O39-O40. Changed: §2.1 and §14 (numbers one kind, LEAN; no "no number type"), §2.2
  (`!` not in rx, PARKED), §4.6 (thresholds OPEN; example without a filter called on a subject), §5.2 (sections `&`
  only; no partial application in phase 1, currying kept), §5.4, §6.1 (quote overclaim removed; next-end caveat
  restored), §8 (`count()` first, `occurs` the fallback, refusal by budget), §11 (`^`/`$` = the FILTERED SPAN's ends,
  stated once; `(?m)`), §12.5, §12.9, §13 (C6, C21, C33-C35, O23 resolved; C23 restated).
- **rev 4 (lane predspec4, 2026-11-15).** Folded the rulings after "transforms are FILTER MODIFIERS" through "Agree with
  mapping" (C1, C20, C30-C32; patterns take no arguments; the subject is never an argument; sections).
- **rev 3 (lane predspec3, 2026-11-14).** Folded the rulings from "Q1 critic framing" to "transforms are FILTER
  MODIFIERS" and the FIX-NOW dispositions of review `docs/dev/reviews/2026-11-14-r1-predspec.md` (G0 and the
  LOOK-ALIKE TABLE, pure `&`, filter modifiers, condition binding, string sets, §12.12 E-CTX).
- **rev 2 (lane predspec2, 2026-11-14).** Folded every ruling and lean after rev 0 through the counting-occurrences
  ruling and the adopted parts of `docs/dev/lanes/predx_report.md`.
- **rev 0 (lane predspec, 2026-11-14).** First consolidation of the notes through the outer-layer note.

## 0. Status, goals, standing questions

**Status: DRAFT rev 13 (lane predspec13, 2026-11-15). NOT a ruling, NOT scheduled, NO BUILD GO** (Frank 2026-11-13:
#6 not scheduled; 2026-11-15, relayed in the predspec5 brief: "the predicate work is not a go to build as we are
still in design"). Purpose (Frank 2026-11-14): "create a preliminary predicate spec doc with our latest ideas for the
purpose of critical analysis. Provide reasoning." It consolidates the dated notes in
`docs/design/plan_row_bodies/COND-FAMILY.md` ("CF"; the source of truth; the LATEST note on a topic wins, and the
owner's QUOTED words outrank a manager paraphrase beside them), the parts of `docs/dev/lanes/predx_report.md` that
the rulings adopt, and review 2026-11-14-r1-predspec. Older background, `docs/design/cond_family.md` (survey rev 0,
D193) and `docs/design/cond_family_syntax_survey.md` (lane synsurv), is cited where still live. Every rule traces to
a note, a ruling or a review finding (§15); where they are silent or disagree, §13 lists both readings.

**SYNTAX IS PLACEHOLDER THROUGHOUT.** The owner rules semantics; spelling is a later design step (D193 add. 4).
One spelling RULE is ruled (§5.1): no alphabetic operators or statement keywords; and one NAMING rule (§2.7;
widened in rev 12 by CF:1020-1022): every transform the library PROVIDES is named for how it changes the FILTER,
which values the changed filter accepts (`padded`, `anchored`), never for an action on the subject; rev 12's
`search` failed it and the owner renamed it `occurrences` (rev 13, CF:1028 on main; §13 O61 CLOSED). Examples use the latest spellings: `/.../` rx literals (bare rx
fragments are never admitted in the expression language), `:=` define, `,` "next entry" inside `[ ]` (ARRAY, any
one entry) or `( )` (RECORD, all entries together), `=` labels an entry, `:` constrains a label that exists (THE
grammar summary is §5.4), `==` the equality comparison, `X[...]` positional, `&` (pure intersection) / dot for
filtering and labels, `where` for structural selection, conditions `(x: S, y: T)`, FILTER MODIFIERS, the pullback
kind of transform (`x & padded(between(1, 12))`), operator sections `(& f)`, `@` effects, modules as `m := import("m")`, 1-based indexes,
the library transform `occurrences(rx)` (rev 7's `~`/`!~` are withdrawn, §2.6; spelled `search` through rev 12).
Line numbers "CF:n" up to CF:1024 hold on this branch's copy and on main; "CF:n on main" (n >= 1026) are the rev 13
rulings, on main only.

Status marks (rev 10, unchanged in rev 11; every mark is one of three):
- **RULED (CF:n)**: the owner's own words at line n of COND-FAMILY.md (or a D-number) cover the rule; it reaches only
  as far as his quoted words, not a manager gloss beside them. HEDGED WORDS (rev 10, review r10 FIXB-5): a hedged
  ANSWER to a question the manager put to him ("we could skip it", "I think it will help") RULES what it answers; a
  hedged PROPOSAL of his own ("Perhaps search needs ...") is his LEAN. A manager's lean he answers with "agree" or
  "your examples make me agree" is RULED BY ACCEPTANCE, marked "(CF:n, accepted at CF:m)", and reaches as far as the
  lean's own words. THE TYPE PICTURE (CF:846-879) is a manager's RECORD
  (CF:857-875) that the owner ACCEPTED as a whole at CF:851 ("I'm liking your ideas"); a mark "RULED (CF:858)" (or
  860, 863, 866, 873) means "the record point at that line, accepted at CF:851", and reaches only as far as the table
  below says his own sentences go (review r8 P6-10, RUL-3):

| record point | the owner's own sentence behind it, beyond the acceptance | what rests ONLY on the acceptance |
|---|---|---|
| (1) two kinds, a condition is a macro, "filter" a role (CF:858) | "a condition ... It's more like a macro" (CF:849); `isodate` "is not a macro but an rx" (CF:855) | "filter" as a role; "a binding names whatever its expression is" |
| (2) one input rule (CF:860) | "Then macro application has a specific meaning" (CF:850-851, the criterion, not the rule) | call = parameters, `&` = the operand slot |
| (3) comma and brackets (CF:863) | "a consistent grammar over comma where it has a specific meaning" (CF:850) | `[ ]` any one, `( )` all together, `=` labels, `:` constrains |
| (4) the record (CF:866) | "a purely structural type if it can't be bound directly ie not first class type" (CF:851-852); "We might use it to bind values from a search (x,y) := rx ~ /.../" (CF:852); "You can view a regex as a record but not vice versa" (CF:853-854) | its three positions; "NO third view" (his own words offer "a third view on a regex but an abstract one", CF:853); "phase 1 only if an example needs it" (CF:869-870) |
| (5) the search result (CF:873) | "Ok. I like this view. Let's fold it in" (CF:854); "an array of all of the results ... use count ... treat it as an array ... use the occurs module" (CF:881-883) | "`d.year` = the set of the occurrences' years" (CF:874); rev 8: the RESULT-AS-A-VALUE reading of (5) is overtaken by the transform ruling below (CF:902-926) |

  The 2026-11-15 rulings after the type picture (rev 8). The answers to review r8's four questions (CF:888-892) are
  the owner's own sentences, so a mark citing CF:889-892 is RULED in his words; the manager's RECORD lines beside them
  (CF:893-901) reach only as far as those sentences. The SEARCH IS A TRANSFORM record (CF:906-926) is the manager's
  lean the owner approved with "Do it" (CF:905); a mark resting on it says "(CF:n, accepted at CF:905)":

| ruling point | the owner's own sentence behind it, beyond the acceptance | what rests ONLY on the acceptance ("Do it", CF:905) or is the manager's |
|---|---|---|
| typed parameters out of phase 1 (CF:895) | "yes keep out of phase 1. I like the idea of types but they need more thinking" (CF:889) | "`:` keeps its one meaning (narrows) there" (the manager's record line, CF:895-896: a consequence, not his words) |
| array and map are interfaces (CF:896) | "Array and map are interfaces that can be applied to regex but interfaces aren't themselves values that can be created" (CF:890-891) | |
| a module is described by its map interface (CF:896-898) | "what import is is less important than that its interface is a map" (CF:891-892) | "members reached as fields" |
| `.` has one meaning (CF:898-899) | "agree" (CF:892), to the manager's lean | the whole content of the point (the lean he agreed to) |
| search is a transform (CF:907-909) | "What if search was a transform like search(x) := /.*(?:(${x}.*).*/" (CF:903-904; a sketch, his spelling a placeholder) | "of the `contains` family"; `~` and `!~` WITHDRAWN; "an rx over the WHOLE value in which the occurrence group REPEATS" |
| `some(...)` for some hits (CF:912-914) | "could you use some() to get some hits?" (CF:904-905, a question) | `all(...)` the default; `occurs` keeps counts only; `x & s` re-examined |
| the hit is a repeated label (CF:910-911); same hit by record (CF:915-917); the definition requirements (CF:918-921); group questions phase 1 (CF:922-924) | none | all of it ("Do it") |
| one-iteration access at a higher capability level (CF:924-926) | rev 10: "1. agree" (CF:977), to the manager's item (1) "reading ONE hit needs captures, a higher level with its cost shown, count/some/all in phase 1" (CF:972-973): RULED BY ACCEPTANCE | (rev 9: the manager's lean, LEAN) |

  The two LAST 2026-11-15 entries (rev 9). Both are the owner's answers in his own words (CF:929-934, CF:949-952);
  the RECORD lines beside them (CF:935-940, CF:953-961) reach only as far as those words, and the manager's notes
  (CF:941-947) are LEAN except where his second answer (CF:949-952) takes them up:

| ruling point | the owner's own sentence behind it | what rests only on the record or is the manager's |
|---|---|---|
| search follows PCRE's matching, "always" (CF:935-936) | "it should always follow it if for no other reason than that's what's expected" (CF:932-933) | the count and every question about the hits on that parse (the record's gloss) |
| a bound name holds the transformed rx (CF:936-937) | "the name binds to the transformed regex as for all transformed regex. Am I missing something?" (CF:929) | `hits := search(r)`, applied as `(m: hits)` (the manager's example of it) |
| the quantifier decides zero hits; settings on `search` (CF:937-940) | "What's missing is the + or * control. Perhaps search needs a min max with defaults." (CF:933-934; "perhaps" = a LEAN of his) | "a plain condition on the hits stays all hits and is true over zero hits when zero hits are allowed" (the record's reading of "+ or * control") |
| ONE reading everywhere, the some-parse rule SUPERSEDED (CF:953-955) | "I think it will help if our rx is consistent" (CF:950), answering note (a) (CF:941-944), whose words were "ONE rule (PCRE's reading everywhere)" | "the compiler builds it where it can with the cost shown and refuses on budget naming the higher level" (note (a)'s tail: the MANAGER'S LEAN, not taken up in his answer) |
| the cost is to be known (CF:955-957) | "i'd like to know the cost of this, as you say" (CF:949-950) | the measurement's population and form, and its timing "before any build go" (the record's, CF:955-957; review r10 FIXB-5) |
| ambiguity is the author's to validate (CF:957-959) | "If someone is writing ambiguous rx they need to think about what that means and validate it with @check()" (CF:950-951; `@check()` a placeholder) | the assertion library as its home; `label.ambiguous` kept as the pointer (the record's) |
| `search` gets `min` only; no `max` for now (CF:960-961) | "if "max" is confusing we could skip it for now" (CF:951-952) | `min` default 0, `min = 1` = at least one hit (the manager's note (b), CF:944-945, which his answer leaves standing); `contains(x)` accepts what `search(x, min = 1)` accepts (note (b)) |
  The LAST FOUR 2026-11-15 entries (rev 10; the fourth, CF:997-1000, landed on main after this lane's base). The owner's words are short answers to the manager's numbered lists;
  each point reaches as far as the list item he answered:

| ruling point | the owner's own sentence behind it | what rests only on the record or is the manager's |
|---|---|---|
| `min` is 0 or 1 (CF:965-966) | "1. yes. Keep the wording and we can adjust later. (No argument types so not sure formal way to express limit)" (CF:963-964) | a compile error for other values (the record: "the last clause is the manager's reading", CF:968-969): LEAN |
| `label.ambiguous` fires for the author's OWN text only (CF:969-970) | "2. agree" (CF:964), to rev 9's O59 reading (A) | |
| reading ONE hit needs captures, a higher level with its cost shown; count/some/all in phase 1 (CF:972-973, 980) | "1. agree" (CF:977) | whether a TEST on one iteration by a literal index counts as "reading" one hit (§4.3, O56 (2): LEAN, the default level) |
| ONE measured budget for "too many classes" and the `count()` refusal, no fixed thresholds in the spec (CF:974-975, 980) | "3. agree" (CF:977) | |
| a count is a canonical numeral string, no new value kind; ordinary filters apply (CF:975, 980-981) | "4. agree. Allows "even()" or other checks for count." (CF:977-978) | |
| `&` in rx text ALL OR NOTHING by a module or option; no position-dependent meaning (CF:981-984) | "5. no. I thought we were going to add & to pcre but conditionally with a module or option? Also, fully yes or no. If no put the whole rx in the hole. Like ${// & blah}." (CF:978-979) | the switch OFF by default, `\&` a literal in both modes (the manager's leans, CF:986-987): LEAN; rev 11: the literal spelled `[&]`, and which `&` is the mark under ON (PCRE's own constructs keep their meaning), LEAN, review r12 CENSUS-3, an owner question (§13 O60) |
| filters anchored at both ends; `contains`/`search` remove that; `^`/`$` in their argument are the ends of the span being filtered (his "value", §0.3) (CF:991-996) | "Your examples make me agree. /\d\d/ & between(1, 12) Without anchoring it would match "31"" (CF:990-991): RULED BY ACCEPTANCE of the manager's lean (CF:987-988) | "`startsWith`/`endsWith` are conveniences" (the record, CF:994). REV 12: RESTATED by the later ruling (CF:1011-1019): no transform "removes" anchoring; the filter (the transform's BODY) still matches the whole value and its plain gaps let the argument sit anywhere; same accepted sets except `$`, now PCRE's (L63) |
| a condition on a label that never ran is decided PER MATCH: it FAILS when the match never reached the label's group or loop; a loop REACHED and run zero times satisfies a plain condition (CF:997-1000 on main, after this lane's base; rulings R-1) | "Agree with lean" (CF:1000), to the manager's lean with its two witnesses | the wording of "reached" (§4.2: the deepest construct the match entered) |

  The LAST 2026-11-15 entry (rev 12): ONE ANCHORING RULE, `anchored()`, AND THE NAMING OF PROVIDED TRANSFORMS
  (CF:1001-1024). The owner's own words (CF:1002-1010) are a request ("We need consistent rules around when rx is
  anchored and to what. I don't want to have a bunch of "primitive" functions have special cases"), his own sketch,
  and the naming remark; the RECORD (CF:1011-1022) is the manager's advice he agreed to ("Ok I agree", CF:1006), so
  its points are RULED BY ACCEPTANCE, "(CF:n, accepted at CF:1006)", and reach as far as the record's words:

| ruling point | the owner's own sentence behind it | what rests only on the record or is the manager's |
|---|---|---|
| ONE rule: a FILTER (the filter side of `&`, a `label:` condition) matches the WHOLE value; everywhere else an rx is unanchored as in PCRE (a final pattern is searched) (CF:1011-1012) | "rx is not anchored unless it is in the filter position of & or transformed with anchored()" (CF:1004-1005) | that a COMPILE-TIME SET (an `enumerate` or `@assert` argument, a name set) is read as a filter over whole strings: this document's reading (LEAN, §11) |
| `^`/`$` are the ends of the SCOPED match (the value in a filter, the subject in a final pattern): plain PCRE with the value as the subject, no extra rule (CF:1013-1014) | "^ $ refer to the scoped match" (CF:1005) | that "no extra rule" withdraws rev 10's exact-end `$` (SIM-5), so `$` also holds before a final newline of the value (L63): this document's reading (LEAN) |
| `anchored(rx) := /^${rx}$/` ADDED; identity in filter position; its use is outside one (CF:1014-1015) | "anchored(rx) := /^${rx}$/" (CF:1005) | "`anchored(block)` instead of `\A...\z`" (the record): not exact on a subject ending in a newline (L68, §13 O62) REV 13: the ends are EXACT, `\A`/`\z` (CF:1048-1053 on main), so L68 is SAME |
| the library definitions are plain gaps with no anchors (`startsWith(rx) := /${rx}.*/`, `endsWith(rx) := /.*${rx}/`, `contains(rx) := /.*${rx}.*/`, gaps cross line breaks); no primitive carries an anchoring special case (CF:1016-1019) | "I don't want to have a bunch of "primitive" functions have special cases concerning that" (CF:1003-1004) | the bodies' exact text: rev 9-11's lazy `endsWith` gap and `contains := search(x, min = 1)` are kept (gap-only bodies, the same SETS as the record's; §8) |
| the lean to fold `startsWith`/`endsWith` into `search` WITHDRAWN; the alternative (an explicit anchor switching the implicit one off) REJECTED (CF:1019-1020) | (the record's) | |
| every PROVIDED transform is named for how it changes the FILTER, never for an action on the subject (CF:1020-1022) | "the name transform seemed to imply you were transforming the subject, but of course you're transforming the filter ... We should consider this in the naming of formal transforms that we provide" (CF:1006-1010) | the audit and that `search` needs a new name ("manager's note, not ruled", CF:1022-1024): §2.7, §13 O61 |

  The FOUR entries after rev 12 (rev 13; CF:1026-1062 and CF:1068-1081 on main, the last arriving during this
  revision as rulings R-1). Each is the owner's own short answer to a question
  the manager put; a point reaches as far as the question he answered, and the ~21:20 entry CORRECTS part (a) of the
  ~20:55 one (CF:1048-1053):

| ruling point | the owner's own sentence behind it | what rests only on the record or is the manager's / this document's |
|---|---|---|
| the provided transform `search` is renamed `occurrences` (CF:1026-1029) | "1 occurances." (CF:1028, choosing from the five candidates) | whether the label `hit` is renamed to match: NOT ruled (CF:1029-1030), a spelling-step note |
| `anchored` has EXACT ends (`\A`/`\z`): `anchored(/foo/)` as a final pattern does not match `foo\n` (CF:1050-1052) | "Anchored def: agree" (CF:1037), to the manager's `\A`/`\z` lean, as CORRECTED: "The anchored comment was to a previous statement" (CF:1049-1050) | defining `anchored(P)` as "P in filter role on the enclosing scope": NOT ruled (CF:1052-1053); not used, a reading of it differs in a hole (§11, §13 O64) |
| under the rx-`&` switch ON, `&` is the operator EXACTLY where `\|` means alternation; a literal ampersand is `\&` or `[&]` (CF:1043-1046) | "agree. Limited to where \| is used to mean alternation. Also, \& should work as escape. Why not?" (CF:1041-1042) | the list of positions where PCRE's reading stands (the record's) |
| BOTH operands of `&` are filter roles (the operator stays symmetric); an explicit anchor in an `&` operand draws a WARNING (CF:1059-1060) | "&: both sides filter and warn if anchor. Agree but test if it makes sense. Like in a hole, what does it mean that they are anchored?" (CF:1057-1058) | the CONDITION: test in every position, bring him any without a sensible meaning (CF:1060-1062): §11 THE AMPERSAND RULE TESTED BY POSITION; the warning's name `anchor.operand`, text and reach (LEAN, §13 O65); the general form of what opens a scoped match (LEAN, review r14 F2) |
| a call may NAME its hit label; two calls exposing the same hit label in one chain are the ambiguity error, the per-call name its fix (CF:1070-1072) | `occurrences(x, label = "foo")` (CF:1070) | the spelling `label =` (a placeholder; `label` is reserved metadata, review r10 CENSUS-14): the spelling step |
| NO warning for a count filter in a searched program; the trap and its fix stated where counts are documented (CF:1075-1077) | "Host count warn: agree" (CF:1075); confirmed "Count warning: yes I agree with that interpretation" (CF:1081) | |
| an `&` in a hole: the stretch the hole consumes is the scope both operands match whole; `999${/\d+/ & <100}999` matches `99945999`, an acceptance row (CF:1079-1080) | "so the match span that the & expression creates anchors for is the ${} hole. 999${/\d+/ & <100}999 matches 99945999" (CF:1078-1079) | the near row `99912345999` (no match) and the other positions: §11 THE AMPERSAND RULE TESTED BY POSITION |

- **LEAN**: a manager's reading or proposal, this document's consequence of a ruling, an owner "perhaps", or a
  review fix (the FIX-NOW dispositions of review r1 other than Q1 and OWN-1 carry no owner ruling); the source is
  named in parentheses (review finding id, "manager", "this document").
- **OPEN**: listed in §13.

### Goals (MANAGER DRAFT; G0 is the owner's standing criterion; ranked, highest wins a conflict)

| # | goal | who benefits | checkable form |
|---|---|---|---|
| G0 | LOOK-ALIKE CONSISTENCY / INTUITIVE BEHAVIOUR: forms that look like they should do the same thing DO the same thing; where they cannot, the compiler SAYS so for the program at hand. A rule whose effect a user cannot predict (context silently making a predicate fail) is a defect even when formally sound | every user (Frank: "Rx is already hieroglyphics"); reviewers of predicate programs | the LOOK-ALIKE TABLE (§0.1): every pair of forms that look alike is marked SAME, or DIFFERENT with exactly ONE class: ERROR or WARNING (the named diagnostic the compiler emits for the program at hand), BY DESIGN (the difference IS a mark's stated meaning, §5.4), or GAP (no diagnostic yet: an open defect, §13 O38); acceptance = no GAP row |
| G0b | FEW KINDS, FEW MARKS, ONE MEANING EACH: "few types and few operators that always mean the same thing wherever they are used"; "a consistent grammar over comma where it has a specific meaning. Then macro application has a specific meaning" (CF:847-851) | every user (one meaning to learn per mark); the spelling step (a small fixed inventory to spell) | the MARK TABLE (§5.4: every mark, its ONE meaning, every position it may take) and the KIND COUNT (§2.1 KIND TABLE), each entry naming the §12 case that needs it; acceptance = no mark or kind with two meanings, and every mark and kind either needed by a case or listed in the TWO-WAY CENSUS (§12) as carried without one, with its reason |
| G1 | EXPRESSIVENESS over the string: conditions PCRE cannot state (cross-label arithmetic, checksums, calendar validity, key-order independence, computed properties, occurrence counts) are short programs | users writing validators, filters, log/JSONL searches | every §12 acceptance case is written with no construct outside §§2-8 (the cases are chosen by the rules' own author: a control sharing its source, review OWN-15) |
| G2 | LINEAR, AUTOMATON-CODE-ONLY BY DEFAULT: a program that compiles at the default level runs as automaton code (one pass or an automaton relax-then-verify split; linear time, no backtracking, hostile-input safe, self-contained output) | anyone matching untrusted input; embedders | at design: every §12 case names its level; at build: every default-level §12 case compiles to automaton code only (`RX_ENGINE` stamp); anything else is a compile error naming the construct and the opt-in, never a silent route change |
| G3 | PCRE COMPATIBILITY: a one-literal program IS today's PCRE pattern, with PCRE's meaning (no subset, no level beyond today's engine choice) | existing PCRE users; the corpus | the whole `.rxt` corpus, each pattern wrapped as `/.../` (with `/` escaped as `\/`, each `${` written `$\{`, and the case's flags transferred to the literal), answers identically to today with the rx-`&` switch OFF (a nullable one-literal program gets the `empty.search` WARNING only, §7). The two marks inside `/.../` that are not PCRE's are §11's: `${` always (in PCRE `$` then a literal `{`, an anchor no text can satisfy before a `{`; `$\{` means the same in PCRE; 33 of 7,057 corpus pattern lines contain `${`, all in `tests/vars/`, the [VAR] module's own hole), and `&` only with the switch ON (G3's check runs OFF. Of the 165 corpus pattern lines that contain `&`, 154 hold PCRE's subroutine call `(?&name)`, 7 an `&` inside a callout's text `(?C...)`, 1 the property `\p{bc=L&}`, 2 an `&` only inside a character class, and 1 a bare literal `&`, a URL's query separator: under ON, by the ruling of §11 (CF:1041-1046 on main: the operator exactly where `\|` means alternation) every one of PCRE's own constructs keeps its meaning and only that one bare `&` would be rewritten, to `\&` or `[&]`; review r12 CENSUS-3; the classifying script is recorded in `docs/dev/lanes/predspec11_report.md`). Counts: `grep -rhE '^pattern .*\$\{' --include='*.rxt' tests \| wc -l` and the same with `&` and with `^pattern ` alone |
| G4 | STRUCTURE OF SPELLED THINGS IS COMPILE-TIME ONLY, TOTAL, TERMINATING: every structural evaluation (each, join, records, indexing, imports, enumerate) over a SPELLED array (§3.4) is finite and ends; a repeated label's ITERATIONS (a search's hits included) exist per match and are questions of the automaton (G2), outside this goal (§3.4, §4.3) | the compiler's users (no hang at build), the security story | recursion through parameterized definitions only by a strictly decreasing literal parameter (§7); every structural operator ranges over finite declared things, `enumerate` under a budget; a fuzzer over programs never hangs the compiler (watchdog) |

Constraints on every goal (ruled RULES, not ranked goals): no alphabetic operators or keywords (§5.1); `&`, `|`,
`!` extensional for MEMBERSHIP (§2.2; a condition on a label reads the spelling's parse, §4.5). Non-goals: §14. G0 is the owner's ("STANDING CRITERION ... ranked first for this design",
CF:691); G0b is the owner's 2026-11-15 criterion (CF:847-851; as a goal row: LEAN, review r8 P6-9); G0 and G0b
are not ranked against each other (each is checked by its own table). G1 > G2 > G3 > G4 is the manager's draft
order for DESIGNING a new rule. AS THE RULES OPERATE, at the default level G2 wins every conflict with G1: the
program gets a compile error naming the opt-in (the capability levels, §6; the class-count cost, §4.6), and G1 is
regained only by that opt-in, never by a silent route change (review OWN-15). Whether the table should say G2 > G1 at
the default level is the owner's (§13 O38).

### 0.1 The LOOK-ALIKE TABLE

Each row is a pair (or set) of forms a reader would expect to agree. SAME = one answer on every subject. DIFFERENT
carries exactly ONE class (G0, review r8 P6-9): ERROR / WARNING = the named diagnostic the compiler emits when they
differ for the program at hand; BY DESIGN = the difference is a mark's stated meaning (§5.4), which the reader is
told once; GAP = no diagnostic yet (an open defect against G0, §13 O38). "(proposed)" = a named diagnostic
recommended by a review and not yet adopted, so the row stays GAP. OPEN = the answer itself is undecided (§13).
Sources: review 2026-11-14-r1-predspec finding ids, and r8 (P6-n) for rev 7.

| # | forms | verdict | diagnostic / reason | source |
|---|---|---|---|---|
| L1 | `a & b & c` in any order or grouping, incl. transforms: `alts & !startsWith("#") & length(<=20)` vs `alts & length(<=20) & !startsWith("#")`; `(x & padded(S)) & T` vs `x & (padded(S) & T)` | SAME | `&` is pure intersection (§2.2, OWN-1 ruling) | OWN-1, RUL-11 |
| L2 | a binding vs its expansion: `m := /\d\d/ & padded(between(1, 12))` then `m & T` vs `/\d\d/ & padded(between(1, 12)) & T` | SAME | | OWN-1 (c) |
| L3 | `isodate & (year: S, month: 2)` vs `isodate & (year: S) & (month: 2)` | SAME | the `( )` RECORD holds its entries together; the AND comes from the record, not the comma (§4.1, §5.4) | C22, CF:866 |
| L4 | `(major: 1, minor: >=4)` vs `(major: 1 & minor: >=4)` | DIFFERENT: ERROR | the second is a compile ERROR: a label inside a value (`major: (1 & minor: >=4)`) | C22 |
| L5 | `x & (a: d)` vs `(a: d)(x)` | DIFFERENT: ERROR | the second is a compile ERROR: the operand is never an argument (CF:749's "subject", §0.3; hint: "write `x & (a: d)`"); application has one spelling (§2.3) | 2026-11-15 RULING (supersedes OWN-5's two spellings) |
| L6 | `x & (a: d)` vs `each((& (a: d)), x)` | DIFFERENT: ERROR | `each` is the STRUCTURAL per-entry map (keeps entries, labels, order; the filter is mapped through the section `(& (a: d))`, §5.3); an alternative lacking `a` is dropped by `&` with `label.unset`, an ERROR naming it under `each` | OWN-5, 2026-11-15 RULING (mapping) |
| L7 | `x: /^S\w*/` vs `x: startsWith("S")` | DIFFERENT: BY DESIGN | (rev 13: WARNING `anchor.operand` if the owner extends the warning to every filter role, §13 O65, lean yes; the anchor is not in an `&` operand's own text, so the ruled warning does not reach it) a filter applied directly is ANCHORED AT BOTH ENDS (§11 THE FILTERED SPAN), so `/^S\w*/` is the strings that are ENTIRELY `S\w*` (its `^` adds nothing), while `startsWith("S")` is every string that starts with `S`: on the span `S-1` the first rejects, the second accepts. The two agree only where the span is word characters (E-CTX-1's x is `\w+`). "Starts with" is `startsWith("S")` or `contains(/^S/)` (L17). Rev 10 said SAME (review r12 SIMULATE-1) | CF:732, CF:761, D193 add. 3; the anchoring: CF:991-993 (accepted at CF:990), restated as the ONE rule (CF:1011, accepted at CF:1006; rev 12) |
| L8 | `num := /\b\d+\b/`: `/x${num}/` vs the pasted `/x\b\d+\b/` | DIFFERENT: ERROR | the hole form is the EDGE-ASSERTION ERROR ("put `\b` in the pattern that places num") | Q1X-3 (iv), Q1R-3 |
| L9 | `p := /(?<=\$)\d+/`: the program `p` (searched) vs `[n = /\d+/] & (n: p)` | DIFFERENT: ERROR | the condition is the EDGE-ASSERTION ERROR; the searched final pattern keeps PCRE meaning | Q1X-3 (iii), Q1X-1 |
| L10 | `\w{3} & /\w+\b/` vs `/\w{3}\b/` | DIFFERENT: ERROR | the first is the EDGE-ASSERTION ERROR (no silent move foo -> bar) | Q1X-2 |
| L11 | `alts & !/^#.*/` vs `alts & !startsWith("#")` | DIFFERENT: WARNING | `anchor.operand` fires on the `^` (rev 13: an explicit anchor in an `&` operand, here inside the complement `!/^#.*/`, CF:1054-1062 on main; rev 11-12 class BY DESIGN). The directly applied `/^#.*/` is anchored at both ends and its `.` has no `(?s)`, so it is the entries that are ENTIRELY `#` and non-line-break characters; `startsWith("#")` is every entry starting `#`: the entry `#a\nb` is kept by the first, dropped by the second. They agree on entries without a line break (E-FILE's `alts` are lines). Rev 10 said SAME (review r12 SIMULATE-1) | CF:761; the anchoring: CF:991-993 (accepted at CF:990), restated as the ONE rule (CF:1011, accepted at CF:1006; rev 12) |
| L12 | `"5" & /(?<=\$)\d+/` in `@assert.none(...)` vs `"5" & /\d+/` | DIFFERENT: ERROR | the first is the EDGE-ASSERTION ERROR (an assertion argument is a set position, §5.6) | Q1X-5 |
| L13 | `x & padded(/^5/)` vs `x & padded(startsWith("5"))` | DIFFERENT: BY DESIGN | (rev 13: WARNING `anchor.operand` if the owner extends the warning to every filter role, §13 O65, lean yes; the anchor is not in an `&` operand's own text, so the ruled warning does not reach it) a modifier's argument filters the span AS THE MODIFIER READS IT, and is itself a FILTER, so it matches that whole reading (THE ONE ANCHORING RULE, §2.7, §11): `padded(/^5/)` = `padded("5")` (`5`, `05`, ...), while `padded(startsWith("5"))` also accepts `57` and `057`. `padded(/\b5/)` stays the EDGE-ASSERTION ERROR. Rev 10 said SAME (review r12 SIMULATE-1) | CF:761; the anchoring of a modifier's argument: this document's application of CF:991-994 and of the ONE rule (CF:1011; a modifier's argument is a filter, §2.7) (LEAN, §13 O49) |
| L14 | `enumerate(/(?<=a)[bc]/)` vs `enumerate(/[bc]/)` | DIFFERENT: ERROR | the first is the EDGE-ASSERTION ERROR | Q1R-8, Q1X-6 (b) |
| L15 | `@warn.off(/^dead\./)` vs `@warn.off(startsWith("dead."))` | DIFFERENT: BY DESIGN | (rev 13: WARNING `anchor.operand` if the owner extends the warning to every filter role, §13 O65, lean yes; the anchor is not in an `&` operand's own text, so the ruled warning does not reach it) a name set is a compile-time set of WHOLE strings (§11 STRING SETS; there `^`/`$` are the string's own ends): `/^dead\./` is the ONE name `dead.`, `startsWith("dead.")` every name starting `dead.`. Rev 10 said SAME (review r12 SIMULATE-1) | CF:713 (string sets); `^` in a compile-time set: LEAN (§11; rev 12: a name set read as a filter over whole names under the ONE rule, CF:1011, LEAN) |
| L16 | `(m: occurrences(/^err/))` vs `(m: contains(/^err/))` | DIFFERENT: BY DESIGN | `occurrences` with its default `min = 0` NEVER REJECTS (as a set it is every string; what it adds is the repeated label `hit`, one iteration per hit, here at most one, at m's start); `contains` is the TEST (one hit needed). The search filters nothing until a question is asked of its hits (`some(...)`, `count(...)`, a plain condition; §2.6, §4.3). With `min = 1` the two are SAME (L58) | CF:907-909 (accepted at CF:905); rev 7's `$m ~ /^err/` row withdrawn with `~`; `min`: CF:960 |
| L17 | `(m: contains(/^err/))` vs `(m: startsWith("err"))` | SAME | it "falls out of PCRE" (rev 12): `contains`'s body is plain gaps around its argument, matched against the WHOLE span, so the `^` in its argument is PCRE's `^`, the start of the scoped match (m's span), and only an empty lead gap reaches it: `/.*^err.*/` accepts what `/err.*/` accepts, gaps crossing line breaks (§11 THE ONE ANCHORING RULE; libpcre2 10.46 and Python `re`: `err x` accepted, `x err` rejected by both forms, `predspec12_anchor.out`); `(m: !contains(/^err/))` is the negated test (rev 7's `$m !~ /^err/`, withdrawn, §2.6) | CF:761; CF:991-994 (accepted at CF:990); rev 12: "`contains(/^err/)` = starts with `err` falls out of PCRE" (CF:1018, accepted at CF:1006) |
| L18 | a nullable final search pattern: `/\b/` vs `/a*/` | SAME | both are nullable IN CONTEXT: `empty.search` WARNING for a one-literal program, ERROR in a predicate program (§7) | Q1R-9 |
| L19 | `(?m)^\d*` searched vs the same pattern in whole-subject mode | DIFFERENT: WARNING | by MODE only: `empty.search` in searched mode, none when anchored (a `^` in the pattern does not exempt) | Q1R-9 |
| L20 | `/\d\d/ & padded(between(1, 12))` vs `/\d\d/ & between(1, 12)` | DIFFERENT: GAP | GAP: the second is {10, 11, 12} by the C9 ruling (string sets, canonical numerals); no warning is named for a padded target against an integer comparison set | C9, OWN-2 |
| L21 | `!<200` vs `>=200` | DIFFERENT: GAP | on targets with non-canonical members (`0150`, `abc`: kept by `!<200`, refused by `>=200`): GAP; in where they may stand (`${>=200}` legal, `${!<200}` the unapplied-macro error): the unapplied-macro error. §13 O26 | OWN-2, RUL-2 |
| L22 | `(x: <200 \| >900)` vs top-level `x & <200 \| >900` | DIFFERENT: GAP | inside a condition `\|` binds tighter than `:` (x in either range); at top level D196 parses `(x & <200) \| >900`, a full rx that widens the program; `precedence.section` (proposed, PLAN) | C22, RUL-15 |
| L23 | `(x: <200, y: >55)` vs `[(x: <200), (y: >55)]` | DIFFERENT: BY DESIGN | AND vs OR, said by the BRACKET (`( )` all together, `[ ]` any one; §5.4); the comma means "next entry" in both, so the look-alike the review flagged (one comma, two logics) is gone; whether the bracket difference still needs a diagnostic: LEAN no (§13 O30 RESOLVED, O38) | OWN-9, CF:863 |
| L24 | `x := /a\|b\|c/`: `/${x}\|d/` vs `x \| /d/` vs `/a\|b\|c\|d/` | DIFFERENT: GAP | one language, different entries: `[2]` and the default-level `.index` differ; `array.hole` (proposed, PLAN) | OWN-8 |
| L25 | `/a\|b/` vs `/b\|a/` | DIFFERENT: BY DESIGN | SAME under `& \| !` as MEMBERSHIP (one language); differ under `[]`, `.index`, PCRE priority and a CONDITION on a label of the operand (§3.4 and §4.5: structural tools and conditions read the spelling; L60); whether a documented structural difference also needs a diagnostic: §13 O38 | §3.4 |
| L26 | `enumerate(/[-\/.]/)` vs `enumerate(/[.\/-]/)` | SAME | class members in codepoint order (§5.5) | OWN-10 |
| L27 | `X[<4]` vs `X[1\|2\|3]` | SAME | numeric filters range over positions 1..n (§3.2) | RUL-9 |
| L28 | `$x & S` as a condition vs `(x: S)` | DIFFERENT: ERROR | the first is an ERROR "did you mean `x: ...`?" (§4.1) | §4.1 |
| L29 | `a := 256` vs `b := "256"` under `<a` / `<b` | DIFFERENT: GAP | GAP; OPEN (§13 O27) | OWN-3 |
| L30 | `!(x: S)` vs `(x: !S)` on a repeated, optional or zero-iteration label | DIFFERENT: GAP | GAP; OPEN (§13 O28) | OWN-4 |
| L31 | `some((g: "x", h: 1))` vs `some((g: "x")) & some((h: 1))` over a repeated label (`occurrences` hits included) | DIFFERENT: BY DESIGN | SAME HIT BY RECORD: one record = all its entries on the SAME iteration; two `some` calls may be met by different iterations (§4.3; on hits `x2 y1` of `/(?<g>[xy])(?<h>\d)/`: the first false, the second true). Replaces rev 7's GAP row (two `occurs.some` vs one `some(s)`); §13 O29 RESOLVED | CF:915-917 (accepted at CF:905) |
| L32 | `/${q}/m` vs the inlined text of `q` | DIFFERENT: GAP | GAP; `flag.hole` (proposed); OPEN (§13 O32) | Q1R-11 |
| L33 | `\k<s>` vs `${$s}` vs `each(..., enumerate(...))` on a finite label | DIFFERENT: GAP | different levels today; OPEN (§13 O34) | RUL-7 |
| L34 | `(a: <5) & (b: <5)` on an ambiguous two-label pattern (`/(?<a>\d+)(?<b>\d+)/` on `123`): default level vs `vm` | SAME | ONE READING (§4.5, CF:953-955): both levels read PCRE's one parse (a = `12`, b = `3`), so on the WHOLE SPAN `123` the program is false at both; SEARCHED in the subject `123` it reports `12` at both (a = `1`, b = `2` on that span; D196 tries the shorter end, §4.5); the default level may pay states for it (cost owed, §13 O57). `label.ambiguous` still names the label, as the POINTER to the author's validation (§5.6, CF:959), not as a report of a difference. Rev 8: DIFFERENT: WARNING (some-parse at default) | CF:953-955; rev 8 RUL-3 |
| L35 | `(?J)` duplicate label vs a repeated label, under `x: S` | DIFFERENT: GAP | GAP; OPEN (§13 O35) | RUL-16 |
| L36 | `(x: S)` vs `all((x: S))` on a repeated label | SAME | `all(...)` is the default, "rarely written": a plain condition already means every iteration (§4.3); rev 7's `occurs.all` leaves (`occurs` keeps counts only); on ZERO iterations both HOLD (the loop's own quantifier allowed none; the boundary with an unset label: §4.2) | CF:912-913 (accepted at CF:905); C28 RESOLVED |
| L37 | `(wname.index: ==wd)` vs `(b: >$a)` | OPEN | a computed label read bare vs with `$` (§13 C13; E-RFC's `==wd` and E-CAL's `<=dim` both rest on it) | OWN-11, r8 P6-11 |
| L38 | `isodate(x).year` vs `(x & isodate).year` | DIFFERENT: ERROR | the first is a compile ERROR (a pattern takes no arguments; hint "write `x & isodate`"); whether `.year` of `x & isodate` is a value or a pattern: OPEN (§13 C29) | RUL-8, 2026-11-15 RULING |
| L39 | `A & B` vs `B & A` | SAME | BOTH operands are filter roles, matched whole on the same span (RULED, CF:1054-1062 on main, rev 13; review r14 F1: a one-sided "filter side" would break this row), so the same subjects are accepted; the left operand picks the REPORTED span among overlapping qualifiers (D196), so the report may differ (§2.2) | C1 ruling |
| L40 | `isodate(year: S)` vs `isodate & (year: S)` | DIFFERENT: ERROR | the first is a compile ERROR: a pattern has no parameters; hint "write `isodate & (year: ...)`"; a parameterised pattern is a macro, `date_in(years) := isodate & (year: years)` (§5.2) | CF:744 |
| L41 | `/\w+/ & /^foo/` vs `/\w+/ & startsWith("foo")` | DIFFERENT: WARNING | `anchor.operand` fires on the `^` of `/^foo/` (rev 13, CF:1054-1062 on main; rev 11-12 class BY DESIGN). The directly applied `/^foo/` is anchored at both ends, so the first is the ONE word `foo` (its `^` is the word's start, never the subject's, and adds nothing); the second is every word starting `foo`. Searched in `foobar` the first reports `foo` (D196 tries the shorter end), the second `foobar`. Rev 10 said SAME (review r12 SIMULATE-1) | CF:761; the anchoring: CF:991-993 (accepted at CF:990), restated as the ONE rule (CF:1011, accepted at CF:1006; rev 12) |
| L42 | `n := count((name: S))` then `headers & (n: ==1)` vs `headers & occurs.exactly(1, (name: S))` | SAME | one count, two spellings; `count()` is refused only over the BUDGET, naming the `occurs` form (§8) | CF:823 (LEAN), CF:832 |
| L43 | `[x = /foo/, y = /bar/]` vs `(x = /foo/, y = /bar/)` in value position | DIFFERENT: ERROR | the second is a compile ERROR: "a record is not a value; for any one of the entries write `[ ... ]`" (§3.1, §5.4); the rev 5 map literal `(x = /foo/ \| y = /bar/)` is withdrawn (§13 O42) | CF:863, CF:866 |
| L44 | `(x)` vs `x` in value position | SAME | parentheses with one unlabelled entry are GROUPING; a one-entry record exists only where a record stands (a call `f(x)`, the left of a binding), so no value is ever a one-entry record (§5.4; §13 O41) | CF:866 (LEAN) |
| L45 | `f(1, 2)` vs `f((1, 2))` | DIFFERENT: ERROR | the second is a compile ERROR: a call is the macro applied to ONE record, and an inner record would be a record used as a value (§5.2) | CF:866 (LEAN) |
| L46 | `isodate & (year: 2000)` vs `c := (year: 2000)` then `isodate & c` | SAME | a condition is a MACRO, a value; binding it is L2's case; the record is its written body, never the bound thing (§2.1; §13 O45) | CF:858, CF:866 (LEAN) |
| L47 | `[x: S]` vs `[(x: S)]` | DIFFERENT: ERROR | the first is a compile ERROR: `:` constrains a label of what the record is laid against, and an array entry is laid against nothing; hint "write `[(x: S)]`" (§5.4) | CF:863 (LEAN) |
| L48 | `x := /a\|b\|c/`: `[x, /d/]` vs `x \| /d/` | DIFFERENT: BY DESIGN | SAME under `& \| !` (one language); under structural tools `[x, /d/]` has 2 entries (each entry of `[ ]` is ONE entry, like a group or a hole, §3.3, §5.4) and `x \| /d/` has 4 (`\|` concatenates ENTRIES, §3.3) | r8 P6-14 |
| L49 | `m(x: T) := ...` then `m(A)` vs `A & (x: T)` | DIFFERENT: ERROR (phase 1) | typed parameters are OUT of phase 1 (the owner: "keep out of phase 1", CF:889), so in phase 1 the first form is an ERROR ("a parameter takes no constraint in phase 1; constrain where it is used") and `:` has ONE behaviour, it narrows. In the design (types "need more thinking", CF:889) rev 7's difference (`:` checks in a head, narrows in a condition) stays unruled (§13 O48) | r8 P6-4; CF:889 |
| L50 | a record on the left over `occurrences`, rev 8 spelling `(x, y) := $m & occurrences(/(?<a>\d)(?<b>\d)/)`: laid over the argument's GROUPS vs read as the first two HITS (Python's `x, y = re.findall(...)`) | OPEN | design only, out of phase 1 (§0.2). Rev 8 removes the second reading's footing (hits are iterations of a label, reached by the array interface over iterations, never entries of a value), so the lean is the first: the record is laid against the ARGUMENT's groups in their group order (the library's own `hit` group excluded; review r10 FIXA-4: in the body's own group order x would land on `hit`); x and y are then REPEATED labels, one iteration per hit, paired by iteration. Whether the form survives the withdrawal of `~` at all: §13 O54 | r8 P6-7 (DRIFT-6); CF:852 |
| L51 | `(m: !occurrences(r))` vs `(m: !contains(r))` | DIFFERENT: ERROR | `occurrences(r)` accepts every string, so `!occurrences(r)` is EMPTY: the empty-intersection ERROR at a narrowing site (§5.2), hint "for no hit write `!contains(r)`". Replaces rev 7's `!($m ~ r)` vs `$m !~ r` GAP row (both operators withdrawn). With `min = 1`, `!occurrences(r, min = 1)` = `!contains(r)` (L58) | CF:909 (accepted at CF:905); §5.2 (LEAN) |
| L52 | `(m: occurrences(r) & (g: "x"))` vs `(m: occurrences(r) & some((g: "x")))` | DIFFERENT: BY DESIGN | the LOOK-ALIKE ROW the transform ruling requires: a plain condition on a hit's label means ALL hits (the sequence rule, §4.3); "some hit" is `some(...)`. On `abx aby abx` with `r := /ab(?<g>[xy])/`: the first rejects (hit 2 has g = y), the second accepts. Whether it also gets a named warning: §13 O38 | CF:920-921 (accepted at CF:905) |
| L53 | `(m: occurrences(/a*/))` vs find-all of `/a*/` (Python's `re.findall("a*", "baa")` = 3 results) | DIFFERENT: ERROR (lean) | the lazy-gap definition stops at an EMPTY hit (PCRE ends a loop whose iteration matched empty: 1 hit on `baa`); an `occurrences` argument that can match empty is refused, naming `x & !""` (§2.6, §13 O53) | CF:919-920 (accepted at CF:905); the refusal: LEAN (manager, rev 9) |
| L54 | `x & s` with s an rx vs `some(...)` | DIFFERENT: BY DESIGN | `x & s` is MEMBERSHIP in the rx s (any one entry under `&`, §3.4); `some(...)` asks whether some ITERATION of a repeated label meets a condition (§4.3). Rev 7's three spellings of "some result" (`x & s`, `some(s)`, `occurs.some`) become one: `some(...)` | CF:913-914 (accepted at CF:905) |
| L55 | `(m: occurrences(r) & (g: S))` vs `(m: occurrences(r, min = 1) & (g: S))` on a span with NO hit | DIFFERENT: BY DESIGN | `min` says whether zero hits are allowed (the owner's "+ or * control", CF:933): with the default `min = 0` a plain condition over zero hits HOLDS (every one of none), with `min = 1` the span is rejected. On `xyz` with `r := /ab(?<g>[xy])/`: the first accepts, the second rejects (§2.6 hand checks). Rev 8's lean (a plain condition FAILS on zero hits) is withdrawn | CF:933-934; CF:937-940 (record); the zero-hit answer RULED BY ACCEPTANCE (CF:997-1000 on main, "Agree with lean"; rulings R-1) |
| L56 | `/(?<n>\d)?x/` vs `/(?<n>\d)*x/` under `(n: <5)`, on the span `x` | DIFFERENT: WARNING | PER MATCH (§4.2): with `?` the match skipped n's OPTIONAL group, so n is UNSET and the condition fails (`label.unset` warns on the `?` form); with `*` the match REACHED n's loop and ran it zero times, so the plain condition holds (§4.3). See L65 for a loop the match never reached | the per-match rule (the optional skipped = never reached = FAILS; the loop reached and run zero times HOLDS): RULED BY ACCEPTANCE (CF:997-999, accepted at CF:1000, "Agree with lean"; rulings R-1); the `label.unset` name: LEAN; CF:937-940 (rev 11, review r12 CENSUS-9: rev 10 also marked "unset fails" LEAN, CF:173) |
| L57 | `occurrences(x, min = 2)` vs `occurrences(x) & occurs.at_least(2, (hit: /(?s).*/))` | DIFFERENT: ERROR | under PCRE's reading `{2,}` RE-CUTS the hits to reach two: `x := /aab\|a/` on `aab` gives one hit (`aab`@0) at `min` 0 or 1 but two (`a`@0, `a`@1) at `min = 2` (libpcre2 and Python's `re` agree, §2.6), while the `occurs` form counts the default hits (one: rejects). `min` is 0 or 1; a larger `min` is a compile ERROR naming the `occurs.at_least` form (§13 O58 RESOLVED) | `min` 0 or 1: RULED (CF:963-966); the error for other values: LEAN (the record: the manager's reading, CF:968-969) |
| L58 | `contains(x)` vs `occurrences(x, min = 1)` | SAME | ONE definition (§2.6, §8): `contains(x) := occurrences(x, min = 1)`, so they accept the same values AND read x's labels the same way (leftmost hits, a plain condition = every hit). Rev 8's own body `/(?s).*${x}.*/` accepted the same values but, under the one reading, would read x's labels at the RIGHTMOST occurrence (its greedy lead; `contains(/ab(?<g>[xy])/)` on `abx aby` gives g = `y`, libpcre2), a look-alike the one definition removes. ANSWER MOVE (review r10 FIXB-3): a condition on x's labels after `contains` now reads EVERY hit: `(m: contains(r) & (g: "x"))` on `abx aby` (`r := /ab(?<g>[xy])/`) ACCEPTED under rev 8 (a parse with g = x existed) and REJECTS from rev 9 (hit 2 has g = y); rev 8's meaning is `contains(r & (g: "x"))` or `contains(r) & some((g: "x"))` (L61) | CF:944-945 (note (b)); LEAN (this document) |
| L59 | `/(?<a>\d+)(?<b>\d+)/ & (a: "1")` vs the constraint written into the pattern, `/(?<a>1)(?<b>\d+)/`, on `123` | DIFFERENT: WARNING | a condition READS PCRE's parse of the pattern it is laid against and never steers it (§4.5): that parse gives a = `12`, so on the WHOLE SPAN `123` the first rejects; a constraint written INTO the pattern changes the pattern, whose parse then gives a = `1`, so the second accepts. `label.ambiguous` names a and shows the witness; the author validates the intended reading (§5.6). SEARCHED in the subject `123`, the first reports `12` (the parse of `12` gives a = `1`): the condition never steers the PARSE of a span, but by D196 it selects which SPAN is reported (§4.5; review r10 FIXB-7 (d)) | CF:953-955; the no-steering statement: LEAN (this document) |
| L60 | `/(?<a>\d+)(?<b>\d+)/ & (a: "1")` vs `/(?<a>\d+?)(?<b>\d+)/ & (a: "1")` on the span `123`; `A \| B` vs `B \| A` under `(l: "a")` with `A := /(?<l>a)a/`, `B := /(?<l>aa)/`, on `aa` | DIFFERENT: WARNING | ONE LANGUAGE, TWO SPELLINGS, TWO PARSES (review r10 FIXB-1): membership is extensional (§2.2), but a CONDITION reads the parse of the spelling it is laid against (§4.5), so greedy vs lazy (a = `12` vs `1`: the first rejects, the second accepts) and union order (l = `a` vs `aa`: the first accepts, the second rejects) give different answers. `label.ambiguous` names a (resp. l) in both programs. A CONSEQUENCE of the ruled one reading, told to the owner (not asked). libpcre2 10.46 anchored at both ends | CF:953-955 (the one reading); the statement: LEAN (this document) |
| L61 | `(m: contains(r & (g: "x")))` vs `(m: contains(r) & (g: "x"))`, `r := /ab(?<g>[xy])/`, on `abx aby` | DIFFERENT: BY DESIGN | a condition INSIDE the argument narrows WHAT IS SEARCHED FOR (the hits are the occurrences of `abx`: one hit, accepts); a condition on the OPERAND side reads EVERY hit (hit 2 has g = y: rejects). The same pair for `occurrences`: `occurrences(r & (g: S))` changes the hits, `occurrences(r) & (g: S)` tests every hit. The existential spelling over the hits is `some((g: "x"))` (L52) | review r10 FIXB-3 (manager's pick); LEAN |
| L62 | `occurrences(/(?:(?<c>a)\|b)c(?(<c>)a\|d)/)` vs find-all of the same pattern on `acabcd` | DIFFERENT: ERROR | PCRE's loop carries a group's capture from an EARLIER iteration into a backreference or conditional of a later one (the loop finds ONE hit `aca`; find-all finds `aca`@0 and `bcd`@3), so an `occurrences` argument with a backreference or conditional that can run while its group is UNSET IN THE CURRENT HIT (here `(?(<c>)...)` on the `b` path) is REFUSED, the nullable refusal's sibling (§2.6 THE TWO ARGUMENT REFUSALS); an argument whose group is set before its reader on every path (`/(.)\1/`) is admitted (rev 11, review r12 SIMULATE-2) | review r10 SIM-1 (manager's pick); the narrowing: review r12 SIMULATE-2; LEAN |
| L63 | `contains(/err$/)` vs `endsWith("err")` on the span `err\n` | DIFFERENT: BY DESIGN | `$` is PCRE's `$` with the span as the subject (§11 THE ONE ANCHORING RULE): it holds at the value's end AND before a final newline, so `contains(/err$/)` ACCEPTS `err\n` (the hit `err`, then the tail gap takes the `\n`), while `endsWith("err")` must END with `err` and REJECTS it (libpcre2 10.46 and Python `re`, `predspec12_anchor.out`). The exact end is PCRE's own `\z`: `contains(/err\z/)` = `endsWith("err")` (both reject `err\n`). Rev 10/11 said SAME, by an exact-end reading of `$` (review r10 SIM-5) that rev 12 withdraws as an extra rule; whether a warning should name a `$` that can meet a final newline: §13 O38 | rev 12: "plain PCRE with the value as the subject, no extra rule" (CF:1013-1014, accepted at CF:1006); the withdrawal of the exact end: LEAN (this document) |
| L64 | `alt.x[1]` vs `(x[1]: S)` (and `$x[1]`) on `alt := /(?J)(?:(?<x>a)\|(?<x>b))+/` | DIFFERENT: BY DESIGN | `[n]` reads BY POSITION (§5.4 `[ ]` row): in VALUE position (`alt.x[1]`, the rx of the groups labelled x) it is ENTRY 1 of that rx's array interface, the first group in the PATTERN (`a`); on the left of `:` and under `$` (match positions) it is ITERATION 1 of the label in the MATCH (`b` on `ba`) | review r10 FIXA-2, CENSUS-10; LEAN |
| L65 | `/x\|(?<n>\d)+/` vs `/(?<n>\d)*x/` under `(n: <5)`, on the span `x` | DIFFERENT: WARNING | PER MATCH (§4.2): in the first the match took the other alternative and never REACHED n's loop, so n is UNSET and the condition FAILS (`label.unset`), although the loop's own `+` is never consulted; in the second the loop was REACHED and ran zero times, so it HOLDS. PCRE reports n unset in both: the zero-iteration rule is a condition rule laid over PCRE's parse (where the match stopped short of the label), not a capture state | review r10 FIXB-2; RULED BY ACCEPTANCE (CF:997-1000 on main, "Agree with lean"; rulings R-1) |
| L67 | `/(\d+)&${<256}/` vs `/port=(\d+)&${<256}/` vs `/port=(?:(\d+)&${<256})/`, with the rx-`&` switch ON | DIFFERENT: GAP | D196's precedence (concatenation, then `&`) makes an rx-text `&` cover the WHOLE CONCATENATION on each side within its alternative: the first guards the number; the second is `/port=(\d+)/ & <256`, EMPTY (no string starting `port=` is a numeral); the third guards one atom by grouping it and matches `port=80`. An empty-intersection diagnostic at an rx-text `&` is not stated (§5.2 names narrowing sites only; proposed: the empty-intersection error at every `&` whose result is empty, not adopted) | review r12 CENSUS-5; LEAN (this document) |
| L66 | `headers & occurs.exactly(1, (name: any_case("Host")))` SEARCHED vs the same program on the WHOLE SUBJECT, on `Host: a\r\nhost: b` | DIFFERENT: BY DESIGN | rev 13: the owner ruled NO warning (CF:1073-1081 on main; §13 O63 CLOSED), so the difference is the stated meaning of a searched program, told where counts are documented (rev 10-12: GAP). A count filter is NOT UPWARD-CLOSED: searched, D196 tries shorter ends and the one-header span `Host: a` passes (match), while the whole block has two Host headers (no match). A count over a block means "the whole block" only when the program anchors (§12.9 is anchored in rev 10); a warning for a count filter in a searched program (`count.searched`, proposed) is REFUSED by the owner (rev 13); the fix is `anchored(...)` | review r10 SIM-6; §13 O38, O63; CF:1073-1081 on main |
| L68 | `anchored(x)` as a FINAL pattern vs `/\A${x}\z/`, on a subject ending in a newline (`x := /foo/`, subject `foo\n`) | SAME | rev 13: `anchored` has the EXACT ends (RULED, CF:1048-1053 on main: "`anchored(/foo/)` as a final pattern does not match `foo\n`"), `anchored(rx) := /\A(?:${rx})\z/`, so the two are one text: both find nothing in `foo\n` (`predspec13_anchor.out`). Rev 12 said DIFFERENT: BY DESIGN under the owner's placeholder `/^${rx}$/` (PCRE's `$` held before the final newline; §13 O62 CLOSED). In a HOLE `anchored` reads the enclosing scope like any anchor (`/x${anchored(/a/)}/` never matches `xa`): §13 O64 | CF:1005, CF:1014-1015 (accepted at CF:1006); exact ends: CF:1048-1053 on main |
| L69 | `x & anchored(r)` vs `x & r` vs `x & /^(?:r)$/` (and `x & /\A(?:r)\z/`) (and `/^5/` vs `/5/` in a filter) | SAME | (rev 13: SAME answers; `anchor.operand` fires on the third and fourth forms, written anchors, and not on `anchored(r)`) a filter role matches its WHOLE span, and an anchor at a whole match's own start or end always holds there, so `anchored` in filter position is the identity (the record's "identity in filter position"); an explicit anchor never SWITCHES OFF the implicit whole-value rule (`/^5/` accepts no more than `/5/`: it rejects `57`), the alternative the owner rejected (CF:1019-1020). Hence `startsWith(rx) := /^${rx}/` (the owner's first sketch) would mean exactly rx in a filter, and the library body is the plain gap `/${rx}.*/` (§8). libpcre2 10.46 whole-value: `^(?:foo)$` accepts `foo`, rejects `foo\n`, as `foo` does; `^5` rejects `57` | CF:1011-1020 (accepted at CF:1006) |
| L70 | `P` vs `P & /(?s).*/` as a FINAL program (intersection with every string): `/^foo/` vs `/^foo/ & /(?s).*/` on `xfoo`; `/foo$/` vs `/foo$/ & /(?s).*/` on `foox`; `/^\d+$/` vs `/^\d+$/ & <256` on `x300 12` | DIFFERENT: WARNING | both operands of `&` are filter roles (RULED, CF:1054-1062 on main), so an anchor in an operand reads the span both match, not the subject: `/^foo/` finds nothing in `xfoo`, `/^foo/ & /(?s).*/` finds `foo` at 1-4; `/foo$/` nothing in `foox`, the `&` form `foo` at 0-3; `/^\d+$/` nothing in `x300 12`, `/^\d+$/ & <256` finds `30` at 1-3 (libpcre2 10.46 and Python `re`, `predspec13_anchor.out`). `anchor.operand` fires on the `&` forms (§11 THE AMPERSAND RULE TESTED BY POSITION); to pin the subject: `anchored(/\d+/ & <256)` | review r14 F1; the ruling CF:1054-1062 on main; the warning's name and text: LEAN |
| L71 | `/x${/^a/}/` vs `/x${/^a/ & /(?s).*/}/` (a hole without and with a filter role inside it), on `xa` | DIFFERENT: WARNING | a hole opens no scoped match, so in the first `^` is the SUBJECT's start and the program never matches `xa`; in the second the `&` operands are filter roles over the text the hole takes, `^` is that text's start, and it matches 0-2 (`predspec13_anchor.out`). `anchor.operand` fires on the second | review r14 F2; CF:1054-1062 on main; the general form: LEAN |

**REASONING.** The owner's framing: "complex context could cause predicates to just not work and it's not clear how
the obscure rules impact it ... that's why it was so important to me that things that look like they should do the
same thing actually do." A ranked goal without a checkable table would lose every tie to G1 (review OWN-13); the
table makes G0 testable, and a D27 spec-first author writing acceptance cases from the table alone is its natural
independent control (review "D27 recommendation").

**STATUS.** G0 as the first criterion: RULED (CF:691). G0 as a goal row and the table: LEAN (review OWN-13). Rows
L1-L2: RULED (CF:722); L3-L4: RULED (CF:698); L7-L19: RULED (CF:713 as superseded in part by CF:732 and CF:761: `^`/`$`
in a filter are the filtered span's ends), except L16 and L17: L16 (rewritten in rev 8) states the transform
ruling (CF:907-909, accepted at CF:905); L17 is LEAN (P6-5, the filtered span applied to a filter passed as an
argument; rev 10: RULED BY ACCEPTANCE, CF:991-994 accepted at CF:990); L5, L38, L40: RULED (CF:744, CF:749);
L39: RULED (CF:732); L41: RULED (CF:761); L42: LEAN (CF:823 "perhaps"; the budget rule RULED, CF:832); L23's reason:
RULED (CF:863); L43's error: RULED (CF:866, a record is never a value), the withdrawal of the map literal it names:
LEAN (§13 O42); L44-L47: LEAN (this document's readings of CF:858-866); L48-L51 (rev 7): BY DESIGN and ERROR rows state the
rule of the section cited (L49, L51 are ERROR rows since rev 8), OPEN/GAP rows their §13 item; the class on each DIFFERENT row: LEAN (review r8 P6-9); other
rows state the rule of the section cited. Rev 8: L16, L31, L36, L51, L52, L54 rest on the transform ruling as
accepted ("Do it", CF:905), not on the owner's own words; L51's error class is this document's
LEAN; L49's phase-1 verdict is RULED in his words (CF:889); L50 stays OPEN with a lean (§13 O54). Rev 9: L34's SAME
rests on the one reading (CF:953-955, his "consistent", CF:950); L55's zero-hit answer on the owner's "+ or * control"
(CF:933) as the record reads it (CF:937-940), and L16, L36, L51's rev 9 clauses (`min`, zero iterations hold) on
the same record lines; L56 on §4.2's LEAN (CF:173) and the record (CF:937-940); L58's one definition and L59's
no-steering statement are this document's LEAN; L53's refusal is the manager's call (LEAN). Rev 10: L57's `min` 0 or
1 RULED (CF:963-966), its error LEAN; L17 RULED BY ACCEPTANCE (CF:990); L55, L56 and L36's zero-iteration clause LEAN
RULED BY ACCEPTANCE (CF:997-1000, the per-match rule; rulings R-1); L60-L64, L66 LEAN; L65 RULED with them (review r10 picks, this document). Rev 11 (review r12 CENSUS-9: one mark per
point): the PER-MATCH RULE behind L36's zero-iteration clause, L55, L56 and L65 is RULED BY ACCEPTANCE (CF:997-999,
accepted at CF:1000, "Agree with lean"; rulings R-1); the wording of "reached" (§4.2) is LEAN; L60-L64 and L66 stay
LEAN (review r10 picks, this document). Rev 11 (review r12 SIMULATE-1): L7, L11, L13, L15 and L41 move from SAME to
DIFFERENT: BY DESIGN under the anchoring ruling (RULED BY ACCEPTANCE, CF:991-993, accepted at CF:990, for the
directly applied filters of L7, L11, L41; L13's modifier argument and L15's compile-time set by this document's
application of the same rule, LEAN); the class BY DESIGN on each: LEAN. L67 (review r12 CENSUS-5): LEAN. Rev 12
(CF:1001-1024): L7, L11, L41 keep their verdicts, now under the ONE rule (CF:1011, accepted at CF:1006); L13, L15
by this document's application of it (LEAN); L17's reason "falls out of PCRE" (CF:1018, accepted at CF:1006); L63
moves SAME -> DIFFERENT: BY DESIGN (PCRE's `$`, "no extra rule", CF:1013-1014; the withdrawal of the exact end:
LEAN); L68's difference: this document (LEAN, §13 O62); L69: RULED BY ACCEPTANCE (CF:1014-1020, at CF:1006). Rev 13
(CF:1026-1062 on main): L68 SAME, RULED (CF:1048-1053); L39's reason and L70/L71's answers RULED (CF:1054-1062; L71
also rests on this document's general form, LEAN); the WARNING class of L11, L41, L70, L71: the warning RULED
(CF:1057-1061), its name `anchor.operand`: LEAN.

MODE OF THE ANSWERS (rev 10, review r10 SIM-6, FIXB-7 (d)). A row's answer is on the VALUE a set position filters
(the whole span, as a condition reads it) unless the row says SEARCHED. A searched program may report a SHORTER span
than the value (D196 tries the next end when a filter rejects the preferred one), so a filter that is not
upward-closed (a condition on an ambiguous label, a count) can pass on a shorter span: L34, L59 and L66 give both
answers.

SAME ROWS RE-CHECKED UNDER THE ONE READING (rev 10, review r10 FIXB-1: a condition reads the SPELLING's parse). A SAME
row can break only where its two forms spell a LABELLED operand differently. L1 and L39 reorder an `&` chain (the
operand that defines a label keeps its spelling; its parse does not depend on the other operands), L2 and L46 bind
what the other form writes out (the same text after expansion), L3 and L36 and L42 lay one or two questions on ONE
operand, L58 is one definition: all hold. L7, L11, L13, L15, L17, L41, L63 compare filters no condition reads (the `hit` label of `contains` in L17, L63 is named by neither form), L18, L26, L27,
L44 have no condition: unaffected. The rows whose spellings DO differ under a condition were already DIFFERENT (L24,
L25, L48) or are new (L60). (Rev 11: this re-check asked only the one-reading question; five of the rows it passed
break under the anchoring ruling folded in the same revision, next paragraph.)

SAME ROWS RE-APPLIED UNDER THE ANCHORING RULING (REV 11'S RECORD, SUPERSEDED by the next paragraph (rev 12) and by
the one after it (rev 13); its "remove", "loosening" and its L63 clause are rev 11's meanings, kept as history, review
r14 CENSUS-1; review r12 SIMULATE-1; the ruling: a filter applied
directly is anchored at both ends, `contains`/`search` remove that, `^`/`$` in their argument are the span's ends,
CF:991-996). A SAME row can break only where one form writes `^` or `$` in a filter that no loosening transform wraps
(the ruling changes nothing else: sets were already the strings matched ENTIRELY, CF:713). L7, L11, L13, L15, L41 do
and BREAK: each pits a directly applied `/^.../` against `startsWith(...)`, and the anchored filter is the whole-string
set, not "starts with" (each row now states its witness). L17 puts the anchor INSIDE `contains`: it HOLDS
(`contains(/^err/)` = `startsWith("err")`). (Rev 11 also held L63 here by its exact-end `$`; rev 12 MOVED it, below.) L1, L2, L3,
L18, L26, L27, L34, L36, L39, L42, L44, L46, L58 write no `^`/`$` in a filter (L18's `/\b/` and `/a*/` are FINAL
patterns, searched): they HOLD. Each row in its real mode (searched only where the row says SEARCHED): the per-row
table is in `docs/dev/lanes/predspec11_report.md`, ROWS AND EXAMPLES RE-APPLIED.

EVERY ROW RE-APPLIED UNDER THE ONE ANCHORING RULE (rev 12; CF:1011-1020: a filter matches the whole value, everywhere
else an rx is unanchored as in PCRE, `^`/`$` are PCRE's with the scoped match as the subject, library bodies are plain
gaps). Against rev 11 the rule changes an answer only where (a) rev 11 had an anchoring rule PCRE does not have, or
(b) a form is newly written (`anchored`). (a): rev 11's one extra rule was the EXACT-END `$` (review r10 SIM-5); its
only row is L63, which MOVES to DIFFERENT. Rev 11's other anchoring statements give PCRE's answer with the value as
the subject: a directly applied filter matched whole (L7, L11, L13, L15, L41: verdicts unchanged), `^` inside
`contains`/`occurrences` reached only by an empty lead gap (L16, L17: unchanged), final patterns searched (L8, L9, L18,
L19: unchanged). (b): L68, L69 new. Every other row writes no `^`, `$`, `\A`, `\z` and no anchoring transform, or
writes one only in a final pattern: unchanged. Per-row table: `docs/dev/lanes/predspec12_report.md`, CONSISTENCY
SWEEP.

EVERY ROW RE-APPLIED UNDER REV 13'S RULINGS (CF:1026-1062 on main: `occurrences`; `anchored`'s exact ends; rx-text
`&` where `|` alternates; both `&` operands filter roles with the `anchor.operand` warning). ANSWER MOVES: L68 (SAME:
`anchored` is now the `\A`/`\z` text). CLASS MOVES (no answer moves): L11, L41 BY DESIGN -> WARNING (`anchor.operand`
on an anchor in an `&` operand); L66 GAP -> BY DESIGN (the owner ruled no count warning, CF:1073-1081 on main). NEW: L70, L71 (DIFFERENT: WARNING, the look-alikes the ruling creates). NOTED: L7,
L13, L15 stay BY DESIGN unless the owner extends the warning (§13 O65); L69's answers unchanged, the warning fires on
its written-anchor forms; L39's SAME now rests on the ruling (both operands filter roles). Unchanged in answer: every
row naming `occurrences` (respelled from `search`: L16, L31, L50-L53, L55, L57, L58, L61, L62; the same transform),
L17 (no warning: the anchor sits in `contains`'s hole), L63 (`$` stays PCRE's), L67 (rx-text `&` positions: its `&`
stands where `|` would alternate), every other row (no anchor in an `&` operand, no `anchored`). Per-row table:
`docs/dev/lanes/predspec13_report.md`, CONSISTENCY SWEEP.

### 0.2 Phase 1 scope (what the owner said is in and out of the first build)

Nothing is scheduled and there is no build go (Status above); "phase 1" is the owner's name for the first,
base-level predicate build whenever it is chartered.
- IN: THE PREDICATE PART ITSELF, the primary goal of this design (CF:795: "the primary goal of the predicate design is
  the predicate part itself"). RULED.
- IN, and the ONLY additions to the rx language: the `${}` hole and `&` (CF:795: "extra elements added to rx like ${}
  and & are necessary parts of that"). RULED. Where `&` may stand in rx text: ALL OR NOTHING, by a module or option
  (CF:978-979, CF:981-984, RULED; §11 THE MARKS INSIDE `/.../`); its default OFF: LEAN (§13 O60 (a)); which `&` is the
  mark under ON (exactly where `|` means alternation; `(?&name)` and PCRE's other constructs keep their meaning) and
  the literal `\&` or `[&]`: RULED (CF:1041-1046 on main, rev 13).
- IN: operator sections with `&` only, `(& f)` (CF:753, C33: "start with &"). Other operators' sections on need. RULED.
- IN: a macro call binds every required parameter or is an error naming the missing one (CF:753, C34; CF:804). RULED.
- OUT: `!` inside a normal rx (`/!foo/`): PARKED for a later plan item, because its scope (the whole `foo` or just
  the `f`) is unclear (CF:795). `!` in the predicate language is unaffected. RULED.
- OUT: partial application (currying). DEFERRED from phase 1 as a scope reduction, NOT dropped: the design keeps it
  (CF:804: "we can start out phase 1 without currying and revisit later"). RULED.
- OUT: the automatic `count()` -> `occurs` rewrite: a later optimization plan item, [COUNT-TO-OCCURS] (CF:840). RULED.
- OUT unless a worked example needs it: a record on the left of a binding, rev 7's `(x, y) := rx ~ /.../`. In the
  DESIGN: RULED (CF:852, his words: "We might use it to bind values from a search (x,y) := rx ~ /.../"). Out of phase 1
  unless an example needs it: LEAN (the manager's record, CF:869-870, accepted at CF:851; review r8 RUL-4). No §12 case
  needs it (rev 8 re-check), so it is out. The `~` its spelling used is withdrawn (CF:909); what the form becomes:
  §13 O54.
- OUT: TYPED PARAMETERS (`m(x: T)`, the containment check in a definition head). RULED (CF:889: "yes keep out of
  phase 1. I like the idea of types but they need more thinking"). In phase 1 `:` narrows only (§5.2, §5.4); the
  property mark `m(p: pure)` leaves with them (§13 O48).
- IN: the GROUP QUESTIONS on a repeated label, `occurrences` hits included: a plain condition (all iterations), `some(...)`,
  `all(...)`, `count(...)`, `occurs.exactly/at_least/at_most/none` ("compile to states and are phase 1": CF:922-924,
  accepted at CF:905). NOT the default level: access to ONE iteration (`$m.hit[2]`), which needs captures inside a
  loop (CF:972-973, RULED BY ACCEPTANCE: "1. agree", CF:977; §4.3); reading EVERY iteration (`$m.hit`) or SELECTING
  iterations (`$m.hit[(g: "x")]`, keep iterations 1 and 3) at the same level: LEAN (this document's consequence;
  review r12 CENSUS-8).
- IN (rev 9) as RULES that every phase-1 piece obeys, not as constructs: ONE READING, a condition on any label reads
  PCRE's own parse (§4.5; CF:950, CF:953-955), with its COST OWED as a measurement (§13 O57; "i'd like to know the
  cost of this", CF:949-950, RULED; "before any build go" is the record's timing, CF:956: LEAN); `occurrences`'s `min`
  setting, 0 or 1 (RULED, CF:963-966; other values a compile error, LEAN). OUT for now: a `max` setting on `occurrences`
  (CF:951-952: "we could skip it for now", RULED). ONE measured budget for class counts and the `count()` refusal
  (RULED, CF:977, §13 O39); a count is a canonical numeral string (RULED, CF:977-978).
- Not stated by the owner: which library pieces (§8) and levels beyond the default (§6.1) phase 1 carries; and, of
  the constructs NO §12 case uses (the TWO-WAY CENSUS, §12: operator sections in code, the `occurrences` transform and
  `some`/`all`, positional `X[...]`, `where`/`where_group`/`each_group`, `when`, `eval`, `@export`/`@warn`, `*`/`%`,
  `.label`), which stay in phase 1. Sections are IN by ruling (CF:753); `occurrences` (spelled `search` through rev 12) is ruled as a library transform
  (CF:902-909, accepted at CF:905) and its group questions as phase 1 (above), but no case uses it. Rev 8 invents no
  case for them (review r8, DISPOSITIONS RULED, P6-9): the owner decides which stay.

### 0.3 Words (one word per thing)

G0b read as applying to this document's WORDS as well as to its marks (the review r8 coordinator's reading, P6-15;
LEAN). Each word below names ONE thing throughout; a quoted ruling keeps its own words, glossed where they differ.

| word | names | not used for |
|---|---|---|
| **subject** | the run-time TEXT being matched (a `occurrences` or `contains` filter reads the filtered SPAN of it, §2.6, §11) | the operand of `&` (the type-picture record's "subject slot", CF:860, is the OPERAND slot below; CF:749's ruled phrase "the subject is never an argument" means the operand) |
| **operand** | what `&` puts into a macro's slot: the rx on the other side (`X & M` fills M's operand with X) | the text |
| **kind** | rx or macro, the two VALUE kinds (§2.1) | value-vs-pattern; constraint sets |
| **value** | anything of a kind (an rx or a macro) | a captured substring; the filtered text (that is the SPAN; the owner's "the value being filtered", CF:994, is kept in quotes) |
| **span** | the text a set position filters: an `&` operand's text, a label's text in this match, the text an `occurrences`/`contains` filter reads (§11); the draft's own word for "the value being filtered" (rev 13, review r14 CENSUS-2) | a value |
| **scoped match** | the text an rx is matched against, whose ends `^`/`$` (and `\A`/`\z`/`\Z`) are. Exactly two things OPEN one (rev 13, review r14 F2): the PROGRAM (its subject, searched; or a `records` item rx's file text) and every FILTER ROLE wherever it stands (its span, matched WHOLE: an `&` operand, both sides, a `label:` condition, a modifier's argument); a hole never opens one; an anchor reads the INNERMOST (the owner's word, CF:1005; §11 THE ONE ANCHORING RULE) | a hole (a hole is part of the rx around it and has no scoped match of its own) |
| **captured string** | `$x` for a GROUP label: the text it captured in this match (a one-string rx with no labels) | the value `$` reads from metadata or a computed label (`$mname.index`, `$d`): a VALUE of the path, not captured text (§5.4 `$` row; review r12 CENSUS-11) |
| **constraint set** | the rx after `:` (`x: S`; in the design only, `m(x: T)`, an ERROR in phase 1, §5.2), the set a label must lie in (rev 6 said "type" or "value type") | the kinds |
| **filter role** | what stands on the filtering side of `&` (CF:858); "a filter" = a thing in that role | a kind; structural selection (`where` SELECTS) |
| **condition** | the macro written `( label: S, ... )`, laid against an operand's labels (§4.1) | a single `label: S` entry (an ENTRY of a condition); any filter |
| **section** | `(& B)`, the macro with only its operand open (§5.2) | comparisons (those are COMPARISON SETS) |
| **comparison set** | `<256`, `>=lo`, `==5`, `between(1, 12)`: a full rx (§2.4) | |
| **transform** | ANY macro filter -> filter (the owner's word, CF:903, CF:929): the filter modifiers, and the library's gap-bodied transforms `occurrences`/`contains`/`startsWith`/`endsWith`, whose bodies put plain gaps around the argument, and `anchored`, whose body puts the exact ends `\A`/`\z` around it (rev 13, CF:1048-1053 on main); `occurrences`/`contains` also add the repeated label `hit` (§2.6, §8). Rev 11 said `search`/`contains` "loosen the anchoring"; rev 12: no transform changes anchoring, the one rule does (§11). Every PROVIDED transform obeys the naming rule (§2.7, CF:1020-1022) | |
| **filter modifier** | the PULLBACK kind of transform (§2.7): the filter changed to read the subject through a READING t; the NAMING RULE (a name describes the subjects it accepts) bound modifiers only in rev 10-11 (review r10 FIXA-1); rev 12 (CF:1020-1022) widens it to every provided transform (§2.7) | `occurrences`, `contains` (transforms, not modifiers); the map `t` itself (that is the modifier's READING, and its output is "what the modified filter reads") |
| **`occurrences`** / **searched** | `occurrences(x)`, the library TRANSFORM (§2.6; spelled `search` through rev 12, renamed CF:1028) / the MODE in which a FINAL pattern or a `records` item rx is applied to its subject (leftmost match, D196; §7, §11); `empty.search` names the MODE's hazard (review r10 CENSUS-16); "search" alone is used only in quotations and history (review r14 CENSUS-8) | each other |
| **binding** | `name := expression` (§5.1); "match-dependent binding" is a binding that reads a captured string | the C22 parse rule (that is ENTRY EXTENT, §5.4) |
| **entry extent** | how far an entry of `( )` or `[ ]` reaches: to the next comma or the closing bracket, `&`/`\|` tighter than `:` and `=` (C22) | |
| **label** | a pattern's group name, incl. a computed label (§4.4) | a macro's parameter name (PARAMETER); a module's name (MEMBER); `.index`/`.label` (METADATA) |
| **parameter** / **member** / **metadata** | a macro's named input / a module's exported name / `.index`, `.label`; members and metadata are reached by the one `.`, a field of the map interface (§5.4, CF:898-899) | labels; a run-time input |
| **run-time input** | `limit := param(rx)`: an rx whose string the CALLER fixes per match (§11; rev 9 said "run-time parameter", review r10 CENSUS-12) | a macro's parameter (fixed per call at compile time) |
| **entry** | one item of a written `[ ]` or `( )`, or of an rx's array interface (a top-level alternative) | a module's export (MEMBER); a joined part (PART); one pass of a repeated label (ITERATION) |
| **interface** | the ARRAY interface (entries in order) or the MAP interface (fields by name) APPLIED TO a thing: to an rx (§3.1), to a repeated label's iterations (array, §4.3), to a module (map, §7). The owner's word ("Array and map are interfaces that can be applied to regex but interfaces aren't themselves values that can be created", CF:890-891; rev 7 said "view"). An interface is never a value: nothing creates an array or a map | a declared type (§9: rev 7's cut "interfaces", now DECLARED TYPES) |
| **iteration** | one pass of a repeated label in one match (a HIT of `occurrences` is one iteration of its `hit` label, §2.6) | an entry (spelled) |
| **hit** | one occurrence found by `occurrences`: an iteration of the repeated label `hit` (§2.6) | rev 7's "result"/"occurrence" as an array entry |
| **PCRE's reading** (= **the parse**) | the ONE parse PCRE2 gives a pattern matched against exactly the SPAN a set position filters (anchored at both of its ends): which path the match takes, every label's span, every iteration of a loop; a label read within ITS iteration (§2.6, §4.5) | "some parse" (rev 8's some-parse rule, SUPERSEDED); a parse a condition would steer toward (a condition never steers, §4.5) |
| **set once** / **repeated** | a label whose group can be set at most once in one match (it may be UNSET: an optional group, an untaken alternative) / a label whose group can be set more than once (a loop with an upper bound of 2 or more, or none; the `hit` of `occurrences`); the boundary: §4.2 | |
| **record** | the written `( ... )` laid against fields (§5.4); never a value | what `records()` returns (an rx whose ARRAY interface lists the ITEMS; its pattern is the ITEM RX; the name `records` is a placeholder to rename, §13 O44) |
| **effect** | an `@` form, a compile-time statement (§5.1), not a value and not a macro | |

### Standing questions (docs/design/CLAUDE.md)

1. **Measurement regime.** Mostly not relevant: a language spec introduces no measured quantity. The numbers cited
   (ISO date with leap Feb 29 as a plain regex: 6,848 B object, 5.9 ms compile; CF:40; class counts in §4.6) are
   compile-time sizes or arithmetic, not timings. The budgets of §4.6/§8 (O39) are measured quantities when a build
   sets them, and must name their regime then. RELEVANT in rev 9 for ONE owed measurement (§13 O57: the cost of
   PCRE's reading of a condition on an ambiguous label, CF:955-957). Regime: COMPILE-TIME size, not match speed:
   minimal-DFA states (and build time, reported beside them) of the automaton for PCRE's reading vs the some-parse
   automaton for the same program, one minimiser, one alphabet, one box and compiler named in the result. A
   different regime (match throughput) would not flip the decision it feeds (both are automaton code, linear); a
   different POPULATION could, which is why O57 names two.
2. **The independent control.** Relevant to §12 and G0: expected behaviours were checked against Python's
   `datetime`, a hand-written Luhn function and libpcre2 10.49 (review r1's kit), not against pcrec. At build: the
   PCRE2+callout oracle (studies/andspike, F9), an independent Python reference evaluator, standards' own test
   vectors as `@assert.*` statements (§5.6); for G0 a D27 author working from §0.1 alone. Rev 9: PCRE's reading of
   a label is checked against libpcre2's OWN parse through its public API (the pattern matched against the whole
   value, the label's span read from the match; never a rejecting callout, which would make PCRE backtrack into
   another parse, §4.5), with Python's `re` (same priority rules for these constructs) as a second, separately built
   engine; neither shares a source with a construction pcrec would build. For O57 the ambiguous-pattern population is
   counted by the decidable ambiguity check (§4.5) AND, independently, by libpcre2 itself: a callout at the end of
   the pattern that RECORDS the label's span and returns "fail", so PCRE backtracks through EVERY accepting parse of a
   sampled witness; a label with two recorded spans is ambiguous (K35: who counts the population). The callout
   COUNTS only (on sampled witnesses: a lower bound) and never decides an answer, so it is not the steering callout §4.5 forbids for the reading; its parses
   come from PCRE's own backtracking, sharing no source with pcrec's ambiguity check (review r10 FIXB-6).
3. **What moves when data is regenerated.** Relevant only through `file_text`/`import` pins (§7): a changed file
   under a `sha256` pin is a loud compile error; a re-pinned file changes the emitted automaton. O57's result, when
   measured, moves no emitted byte: it feeds the budget (§13 O39) and the owner's go/no-go on the one reading's cost.

## 1. Layering

**RULE.** Two layers. FOUNDATION: value kinds (§2), operators and filter modifiers (§2), the array and map
interfaces (§3), match values, repeated labels and computed labels (§4), capability levels and the reporting axis
(§6), the compile-time boundary, modules and warnings (§7). LIBRARIES, built on the foundation and changeable without
it: `each`, `join`, `records`, `file_text`, standard filters and filter modifiers (`between`, `startsWith`,
`endsWith`, `contains`, `anchored`, `length`, `padded`, `unpadded`, `any_case`, `quoted`), the transform `occurrences`, the group questions
`some`, `all`, `count` and the `occurs` counts, `assert`, tuple comparisons, blessed callouts (§8). The
ORGANISATIONAL layer (DECLARED TYPES, type members, UFCS, `types()`; rev 7 called the first "interfaces", a word
that now names the array and map interfaces, §0.3) is CUT from the first spec (§9); declared types may return as
library packaging after a build. Modules stay in the foundation (described by their map interface: §7, §13 O46).

**TEST OF THE RANKING.** No worked example needs the cut layer: §12 checks this case by case (E-RFC uses a plain
macro on the three fields, not a declared type's member).

**REASONING.** Frank: the purpose is to probe the fundamental structure; unless foundational, lower priority.
predx §9: none of thirteen further programs needed interfaces, UFCS or `types()`.

**STATUS.** Layer outline: LEAN (the LAYERING note, CF:522, is the manager's outline under Frank's framing; its "no
recursion", namespaces-as-organisational and numeric-value-type items were since changed by Q12, the module-as-map
lean and C9; review RUL-14.4). The cut: RULED (CF:583, predx Q8).

## 2. Values and operators

### 2.1 Two value kinds

**RULE.** Every value is one of TWO KINDS: an **rx** (a set of strings, extensional, §11) or a **macro** (a term
awaiting input). There is no third value kind: a CONDITION is a macro; a record is not a value at all (§5.4); a
binding names whatever its expression is (`isodate := join(...)` names an rx; in `isodate & (year: 2000)` the macro is
the condition, not `isodate`). Numeric and string literals are rx: `5` = {"5"}, `"a.b"` = {"a.b"} (the dot is literal,
unlike `/a.b/`); they differ only in what a comparison means (§2.4).

ONE INPUT RULE. A macro takes input two ways: a CALL fills its PARAMETERS (the call's argument list is ONE record laid
against them, §5.2); `&` fills its one OPERAND slot with the rx on the other side (the record's "subject slot",
CF:860; §0.3). The rx is never the thing applied (the operand is never an argument, §2.3). So: a CONDITION (`(x:
<200)`, `(a: 1, b: 2)`) = a macro with an operand and no parameters; a TRANSFORM (a filter modifier, §2.7, or
`occurrences`/`contains`, §2.6; §0.3) = a macro whose parameter is a filter and whose result is a filter; an operator SECTION `(& B)` = only the operand open; prefix
`!B` = a macro with the operand open (§2.2); an unapplied filter modifier (`padded` alone) = a macro with its
parameter open. A section of something that is already a macro with only its operand open is that macro: `(& M)` =
M (so `each((& (a: d)), x)` and `each((a: d), x)` are one program, §5.3; review r8 P6-8 (f)).

A MATCH-DEPENDENT BINDING (a computed label, §4.4: `weekday := weekday_of($year, $month, $day)`, `n := count((name:
S))`) receives the match by the same rule: it is a MACRO whose operand is the pattern whose labels it reads, filled
by `&` when that pattern is the operand of the condition that names it (`isodate & (weekday: 6)`: `isodate` fills
the operand of the condition, and through it of `weekday`). LEAN (this document, review r8 P6-8 (a)); which pattern
when its labels occur in several: §13 O19.

TYPING OF `& | !` OVER THE TWO KINDS (review r8 P6-8 (b); LEAN, this document's consequence of CF:858-860): an rx R
standing in the filter role acts as its section `(& R)`; operators on macros are POINTWISE (`M & N`, `M | N`, `!M`
filter as both, either, neither); `X & M` with X an rx fills M's operand with X (and `X & R` with R an rx is the
intersection, the same thing as `X & (& R)`). So `rx | macro` mixes kinds and is an error naming the fix (write the rx
as its section, `(& R) | M`), as in a mixed array (§3.5); `macro | macro` is legal.

"FILTER" IS A ROLE, NOT A TYPE: whatever stands on the filtering side of `&` (CF:858). An rx can
take the role (`<200`, `between(3, 6)`, `startsWith("S")` and `padded(between(1, 12))` mention no label, so each is
a full rx, the set that passes), and so can a macro with its operand open (a condition, `!B`, a section). Anything
naming a label it does not define is a macro awaiting the pattern that defines it.

Phase 1 has NO partial application (a macro call binds every required parameter, §5.2); the design keeps currying
for later, when a macro with some parameters bound will be a macro too (§0.2). There is no boolean type (a test is a
filter: `"2024" & leap` is {"2024"} or empty).

NUMBERS are ONE kind for the user: a number read from the subject (text matched by `\d+` and the like, compared and
added, §2.4, §2.5) and a count of matches (`count(...)`, §8) take the same comparisons and arithmetic. Where a number
test is evaluated (compiled into the match as a set, or computed on the result) is the compiler's choice, shown with
its cost (manager's view, CF:813). Under the two kinds a number is an rx, a set of numeral strings: for a COUNT this
is RULED ("4. agree. Allows "even()" or other checks for count", CF:977-978, to "a count is a canonical numeral
string, no new value kind", CF:975), so an ordinary filter applies to a count (`n := count(c)`, `P & (n: even)`);
for a number read from the subject it is C9's string sets (§2.4); §13 O40 RESOLVED.

THE KIND TABLE (G0b's KIND COUNT; review r8 P6-8, a DISCLOSURE of everything a name or a mark can denote: the two
VALUE kinds are unchanged, the other rows are not values):

| thing | what it is | a value? | bound by `:=`? | passed as an argument? | §12 case needing it | status |
|---|---|---|---|---|---|---|
| rx (literal, comparison set, binding of an rx, captured string `$x`, a `occurrences(r)` or `contains(r)` filter) | a set of strings | yes | yes | yes | every case | RULED (CF:858) |
| macro (condition, section, filter modifier, `!B`, parameterised definition) | awaits input: parameters by a call, operand by `&` | yes | yes | yes | E-WEEKDAY (condition), E-JSONL (`json.row`, modifiers), E-HTTP (condition argument), E-SEP (`date_sep`) | RULED (CF:858, CF:860) |
| computed label (match-dependent binding) | a macro whose operand is the pattern whose labels it reads (above) | as a macro | yes (that is its spelling) | no case passes one | E-WEEKDAY, E-CAL, E-RFC, E-NEAR (c); E-HTTP's `count` in prose only | LEAN (P6-8 (a)) |
| record `( ... )` | a shape laid against fields: a call's parameters, a condition's labels, a result's groups (§5.4) | no | no (on the LEFT of `:=` only, design only) | no (it IS the argument list) | every call; every condition | RULED (CF:866) |
| module | `m := import(...)`: described by its MAP INTERFACE, members reached as fields by `.` (CF:891-892: "what import is is less important than that its interface is a map"); what kind of thing it is: not ruled, and matters less | no (lean) | yes, by `:= import(...)` | no (lean) | E-JSONL, E-IPV4, E-HTTP, E-DEPTH | the interface RULED (CF:891-892); the kind not ruled (§13 O46) |
| array / map INTERFACE | applied to a thing (an rx, a repeated label's iterations, a module); never created (CF:890-891) | NO | no | no | every case that indexes, joins or reads a field | RULED (CF:890-891) |
| repeated label's iterations | the passes of one label in one match (`occurrences` hits included), read through the array interface (§4.3) | no (they are parts of a match) | no | no | E-HTTP (`name`) | the group questions: CF:922-924, accepted at CF:905 |
| run-time input | `limit := param(rx)`: an rx whose string the caller fixes per match | as an rx (lean) | yes, by `:= param(...)` | yes, as an rx | E-NEAR (b) | OPEN (§13 O46) |
| effect | an `@` form, a compile-time statement (§5.1) | no | no | no | E-IPV4, E-CAL, E-CTX (`@assert`) | LEAN (CF:619) |

The map-interface tools' results (`where_group`, `each_group`, §3.2, §5.3) are rx whose array interface lists the
selected parts in group order: LEAN (this document; review r8 P6-8 (e): the result kind was unstated). Rev 8 (CF:890-891):
wherever this document says a tool "returns an array", it returns an RX read through the array interface; no tool
creates an array or a map as a value (the list of places checked: `docs/dev/lanes/predspec8_report.md`).

**REASONING.** The closure (a predicate denotes a pattern, 2026-11-12/13) means one algebra serves patterns,
values and tests; a condition is a term with a free variable, the same kind as a macro awaiting its operand (via `&`).
The owner's criterion for the type picture: "few types and few operators that always mean the same thing wherever
they are used" (CF:847-848); on conditions, "It's more like a macro" (CF:849). Two kinds and one input rule are the
smallest picture that covers every §12 case; the kind table shows what else a NAME can denote (a namespace, a
parameter) without making those values, so the owner can rule on them (O46) with the whole list in view.

**STATUS.** Two kinds (rx, macro), a condition is a macro: RULED (CF:858, accepted at CF:851; "It's more like a
macro", CF:849; his correction that `isodate` is an rx, CF:855); SUPERSEDES the rev 5 LEAN (CF:362). "Filter" a role
and a binding naming whatever its expression is: RULED (CF:858, on the acceptance alone, §0 marks table). One input
rule (call = parameters, `&` = the operand slot): RULED (CF:860, on the acceptance alone). `(& M)` = M, the computed
label as a macro, the typing of `& | !`, the kind table and the map-interface tools' result kind: LEAN (this document, review r8
P6-8). Literals as one-string sets: LEAN. Module: its MAP interface RULED (CF:891-892), its kind not ruled (§13
O46). Array and map are interfaces, never created values: RULED (CF:890-891). Numbers ONE kind for the user: LEAN (CF:823,
"perhaps"; the owner's ideal, CF:813); a count a canonical numeral string: RULED (CF:977-978); the 11-14 "no number type" is WITHDRAWN as over-reach (CF:782 (3)); what a
number is: §13 O40. No boolean type: LEAN (manager's Q6/Q9 spelling lean, CF:595). No partial application in phase
1, currying kept by the design: RULED (CF:753, CF:804). The earlier "assertions (their own value kind)": withdrawn by
the two kinds (§13 C19 RESOLVED); `@` forms are effects, not values: LEAN (CF:619).

### 2.2 Operators `&`, `|`, prefix `!`

**RULE.** `&` intersection, `|` union, both EXTENSIONAL over rx operands FOR MEMBERSHIP: which strings an `&`/`|`/`!`
expression admits depends only on the operands' languages, so two spellings of one language admit the same strings.
A CONDITION on a label is not membership: it reads the parse of the SPELLING it is laid against (§4.5, the one
reading), like a structural tool (§3.4), so two spellings of one language can answer differently under a condition
(greedy vs lazy, `A | B` vs `B | A`: §0.1 L60; review r10 FIXB-1, a consequence of the ruled one reading). `&` is PURE INTERSECTION:
associative and commutative, so the ORDER and GROUPING of an `&` chain never change which strings it admits (a
transform, a filter modifier or `occurrences`/`contains`, §2.6, §2.7, is a macro called on a filter, never an operator
with a position in the chain). Prefix `!B` is ALWAYS A MACRO with its
operand open (it takes the filter role, §2.1): `A & !B` = A minus B; `&!` is not a separate operator. A standalone `!B` where an rx
is needed (`${!B}`, `C | !B`) is the unapplied-macro error. Macros in the filter role combine pointwise by `& | !`
(the typing sentence, §2.1). `!` lives in the
expression language only: inside a normal rx literal it keeps PCRE's meaning (`/!foo/` matches the text `!foo`); a
`!` operator in the rx language is PARKED for a later plan item (§0.2).

`!<200` and `>=200` are NOT interchangeable: `!<200` keeps every target string that is not a canonical numeral
below 200, so on a target with non-canonical members they differ (`/\d{4}/ & !<200` keeps `0150`, `/\d{4}/ & >=200`
does not; `"abc" & !<200` = {"abc"}, `"abc" & >=200` is empty); they agree only where every target string is a
canonical numeral. `!<200` is a macro, `>=200` a full rx (§0.1 L21; whether a label-free `!f` is a full rx: §13
O26). There is no "positive form" lint rewrite (it would change answers).

Reported span (D196, RULED for `&` between patterns: the expression `&`, and `&` in rx text when the rx-`&` switch is
ON, §11): the left operand chooses (PCRE priority: first alternative,
greedy longer, lazy shorter), the right only filters which ends are admitted; the span SET is commutative. So
`A & B` and `B & A` ACCEPT THE SAME SUBJECTS; D196's left operand picks the REPORTED span among overlapping
qualifiers, so the report may differ (§0.1 L39; C1 RESOLVED).
Precedence (D196): concatenation, then `&`, then `|`; inside a record entry `&` and `|` bind tighter than `:`
and `=`, and the comma is no operator (it ends an entry; §4.1, §5.4). In the expression language there is no concatenation operator (§2.5).

**REASONING.** Extensional `&` keeps arrays and rx "the same". `!` as a filter: a standalone complement is useless
in a searched program and VM-hostile, while under `&` it is bounded. A pure `&` is what the owner's look-alike criterion (G0)
asks of the most common operator: rev 2's right-associative `&` made reordering or parenthesizing a chain with a
transform in it change the answer silently (review OWN-1, RUL-11).

**STATUS.** `&` extensional, `!` a filter: RULED (CF:328, CF:376); scoped to membership, with conditions reading
the spelling's parse: LEAN (this document's consequence of CF:953-955, review r10 FIXB-1). D196: RULED (D196). `&` pure intersection, order-
and grouping-free: RULED (CF:722, OWN-1), SUPERSEDES the right-associative `&` lean. The `!<200` / `>=200` correction
and the dropped lint: LEAN (review OWN-2, RUL-2). C1: RULED (CF:732): same matches, the report may differ. No `!`
inside a normal rx: RULED (CF:795), PARKED, the spelling question NOT closed (CF:795 corrects CF:758).

### 2.3 The unapplied-macro error

**RULE.** An unapplied macro where an rx is required is a compile error naming the fix: "filter `x: digit` has
no target; write `T & (x: digit)`"; "modifier `padded` has no filter; write `padded(between(1, 12))`". The same
error covers a macro in a HOLE: `${(x: digit)}`, `${!<200}` (the owner: a condition is "not usable as `${x: digit}`",
CF:362); a guard is written with `&` before an rx hole, `(\d+)&${ <256 }` with the rx-`&` switch ON, or with the
whole rx in the hole, `${/(\d+)/ & <256}`, with it OFF (§11, C4, CF:978-979). THE OPERAND IS NEVER AN
ARGUMENT (CF:749's "the subject is never an argument", §0.3): application of a FILTER has ONE spelling, `x & f` (`x &
(a: digit)`, `x & padded(S)`); this is the one input rule of §2.1 (a call fills parameters, `&` fills the operand slot;
CF:860). A call that passes the operand (`(a: digit)(x)`, `p(x)`, `padded(S)(x)`) is a compile error naming the fix
("write `x & p`"). An alternative of x lacking the label is DROPPED (with the `label.unset` warning, §4.2), never an error.
`each(f, A)` is NOT an application spelling: it is the STRUCTURAL per-entry map (§5.3), which keeps entries, labels
and order and is an error on an entry lacking the label (§0.1 L6); a filter is mapped through an operator SECTION,
`each((& f), A)` (§5.3).

**STATUS.** The unapplied-macro error: LEAN (manager, CF:362); in a hole, by the owner's own words: RULED (CF:362,
"not usable as `${x: digit}`"; review r8 P6-1 deleted rev 6's contrary hole-as-guard clause). `each` out of the equivalence, lacking label = drop:
LEAN (review OWN-5). One application spelling, the operand never an argument (withdraws the rev 3 spellings `(a:
d)(x)`, `rx & f` = `f(rx)`, `p(x)` = `x & p`): RULED (CF:749, "Agree with mapping"); C20 RESOLVED by it.

### 2.4 Comparisons are unary COMPARISON SETS on string sets

**RULE.** Comparisons are UNARY ONLY: `<256`, `>=lo`, `==5` are COMPARISON SETS (full rx, §0.3; not sections, which
are `(& B)` only), attached by `&` like everything else. A
prefix comparison takes ONE ATOM (literal, label value, binding, call, field access, parenthesized expression) and
binds tighter than `&`, `|`, `!`. The LITERAL decides the reading: `<256` = integers 0..255, `<"256"` =
lexicographic strings, `2.5` decimal, `0x100` hex. Comparisons are on the STRING SET: an integer comparison set contains
CANONICAL numerals of VARIABLE WIDTH (the `\d+` shape: no leading zeros, sign or decimal point unless the literal
has them). Padded text is compared through the explicit `padded` modifier (§2.7): `/\d\d/ & between(1, 12)` is
{10, 11, 12} ("correct because the \d\d means two digits", CF:774) and is WRONG for months; write `/\d\d/ &
padded(between(1, 12))` or the wider pattern `/\d{1,2}/ & between(1, 12)`. There is no "compares by value" reading. `between(lo, hi)` is INCLUSIVE.
Decimal is exact decimal, never binary floating point.

**REASONING.** Every binary comparison is an intersection with a comparison set. Literal-decides means declared
constraint sets are needed only where no literal fixes the reading (value vs value, §4.6). A comparison never silently reinterprets the
text: padding is a visible modifier on the filter.

**STATUS.** Unary: RULED (CF:250, Frank's proposal). Literals decide: RULED (CF:43). String sets, `\d+` integers, the
explicit padding modifier: RULED (CF:573, C9) and CONFIRMED (CF:774: "\d\d & between(1,12) would only match 10-12
... that is correct because the \d\d means two digits"; the "compares by value" reading is not adopted). CANONICAL
(no leading zeros) is this document's reading of "`\d+`", supported by CF:774's "to get between to ignore leading 0":
LEAN (review RUL-14.6); E-IPV4's `01.2.3.4` out depends on it. The name `padded`: RULED (CF:722; the confirmation's
own spelling, CF:774). Exact decimal: LEAN. Whether the reading belongs to the literal's quoting or to the comparison:
§13 O27.

### 2.5 No concatenation operator; arithmetic

**RULE.** The expression language has no concatenation operator: sequencing is written inside a literal
(`/${a}-${b}/`) or by `join`. `+ - * %` are arithmetic only, on numbers (§2.1): subject numbers can be added and
filtered through a computed label (`s := $x + $y`, then `P & (s: <50)`, §4.4; `$y + 1` in a hole; day differences).
`($x + $y) & <50` used as a condition is the "did you mean `x: ...`?" error (§4.1, §0.1 L28). Value concatenation is insertion or a library name
(`concat(x, y)`).

**REASONING.** Avoids the overload trap (`"12" + "34"` = 46 or "1234"?); with no juxtaposition, a name after an
expression always starts a binding (one-token look-ahead, §5.1).

**STATUS.** No concatenation operator: LEAN (CF:69). Arithmetic on subject numbers: RULED (CF:782 (1): "\d+ numbers can
be added, filtered <256"). Arithmetic result width (`${$y + 1}` on `0099`): §13 O27.

### 2.6 `occurrences` and `contains` are transforms

**RULE.** `occurrences` (spelled `search` through rev 12; renamed by the owner, CF:1026-1031 on main, his words
"1 occurances", CF:1028) IS A LIBRARY TRANSFORM of the `contains` family, not an operator: it takes an rx and returns an rx
over the WHOLE span in which the hit group REPEATS, once per hit, and it is applied like any filter, by `:` or `&`
(`(m: occurrences(/ab(?<g>[xy])/))`, `P & occurrences(r)`). It is a TRANSFORM but not a FILTER MODIFIER (§0.3): its body puts
plain gaps around the argument (rev 12: it removes no anchoring; the body, a filter, matches the whole span, §11) and
adds the label `hit`. Since rev 12 the naming rule binds EVERY provided transform (CF:1020-1022, §2.7); rev 12's
`search`, a verb acting on the subject, failed it, and the owner renamed it `occurrences` (rev 13; §13 O61 CLOSED): a
noun for what the changed filter reads (each occurrence of the argument, one `hit` each). The name of the label `hit`
is NOT ruled (CF:1029-1030): kept, a spelling-step note (§13 O55). Quotations of the owner and of the record keep
their `search`; elsewhere this document writes `occurrences`, and the MODE in which a final pattern is applied is
"searched" (§0.3), never the transform. The
operators `~` and `!~` of rev 7 are WITHDRAWN: rev 7's `$m !~ r` is `(m: !contains(r))`; rev 7's `$m ~ r` has no
one-to-one replacement, because a search result is no longer a value: a TEST is `contains`, a QUESTION about the hits
is `occurrences` with a group question (§4.3). The hit needs no new concept: it is a REPEATED LABEL (§4.3), so a plain
condition on a hit's label means ALL hits, `some(...)` some hit, `count(...)` and `occurs.*` count them, and one
record means one hit (SAME HIT BY RECORD). The hits are those of PCRE's OWN matching of the body, "always" (the
owner, CF:932-933): the ONE READING of §4.5.

    occurrences(x, min = 0) := /(?:(?s:.*?)(?<hit>${x})){${min},}(?s:.*)/   # each hit is one iteration of the label `hit`; NAMED (CF:1028)
    contains(x)                  := occurrences(x, min = 1)                               # a TEST: at least one hit

(Library text, §8; spelling placeholder, D193 add. 4. The owner's sketch `search(x) := /.*(?:(${x}.*).*/`, CF:903-904,
is the idea; the shape is the record's requirement (5), CF:918-919. `min = 0` in the head declares an optional
setting and its default (§5.2, §5.4 `=` row). `${min}` is a hole in a typed syntax position, the quantifier's lower
bound (§11, §5.4 `${ }` row); `{0,}` is `*`, `{1,}` is `+`, the owner's "+ or * control" (CF:933). The gaps are
SCOPED `(?s:...)` so they cross line breaks inside the span (the manager's call, LEAN, rev 9) and nothing leaks into
the hole. The hole `${x}` is one atom with its OWN flags and its OWN group numbering (§3.3, §11, §13 O32): a reader
who splices the text by hand must write `(?:x)` with x's flags kept and its numbered groups renumbered, or `/a.b/`,
`/a|b/` and `/(.)\1/` give other answers spliced raw (review r10 SIM-3; `/(.)\1/` is an argument the second refusal
below ADMITS since rev 11: its group is set before `\1` on every path, review r12 SIMULATE-2). The label name `hit` is a library
placeholder, §13 O55.)

THE `min` SETTING (CF:933-934 "Perhaps search needs a min max with defaults", his LEAN; `min` only, CF:960; `min` is
0 or 1, RULED, CF:963-966). `min` is an optional setting with the default 0 (§5.2): `min = 0` allows zero hits (the
span is never rejected), `min = 1` requires at least one hit (a span with none is rejected). Any other value is a
compile error naming `occurs.at_least(n, ...)` (the manager's reading, CF:968-969: LEAN; with typed parameters out of
phase 1 the limit is a stated rule of the library entry, not part of its signature). The reason the owner kept the
limit: `{2,}` lets PCRE RE-CUT the hits to reach two (`x := /aab|a/` on `aab`: one hit `aab` at `min` 0 or 1, two
hits `a`, `a` at `min = 2`), so it is not "at least two of the hits" (§0.1 L57). THERE IS NO `max` FOR NOW (the owner:
"if "max" is confusing we could skip it for now", CF:951-952): under PCRE's reading `{0,N}` would mean "take the FIRST
N hits" (the rest of the span may hold more), not "at most N hits in the span", which stays a count test,
`occurs.at_most` (§13 O58).

`min = 1` FINDS THE SAME HITS AS `min = 0` whenever there is at least one. Proof (in PCRE's priority order): the rest
of the pattern after any iteration always succeeds (`{0,}` may stop and the tail `(?s:.*)` takes what is left), so
the first iteration's first success is never undone; under `{0,}` the greedy loop tries that iteration before
stopping, and under `{1,}` it must; each later iteration is the same choice in both. Checked below on every row.

`contains` IS `occurrences(x, min = 1)`: ONE definition (the manager's note (b), CF:944-945, "`contains(x)` is then
`occurrences(x, min = 1)` in what it accepts"; ONE definition: LEAN, this document). What it accepts is unchanged from rev
8's own body `/(?s).*${x}.*/`: as SETS both are the spans in which x matches IN PLACE, its `^`/`$` reading the span's
ends (for an argument without `^`/`$`: the spans with a substring in x; `contains(/^err/)` rejects `x err`, which has
the substring `err`; review r10 SIM-4). What differs is x's LABELS under the one reading: rev 8's greedy lead puts x
at its RIGHTMOST occurrence (`contains(/ab(?<g>[xy])/)` on `abx aby`: g = `y`, libpcre2), while the `occurrences` body puts
the hits leftmost, every one an iteration, so `(m: contains(/ab(?<g>[xy])/) & (g: "x"))` means "every hit has g = x"
and `some((g: "x"))` "some hit does", exactly as for `occurrences` (§0.1 L58). THE ANSWER MOVES from rev 8 for such a
program (review r10 FIXB-3, the manager's pick to keep one definition): on `abx aby` it accepted under rev 8 (a parse
with g = x existed) and rejects from rev 9 (hit 2 has g = y). Rev 8's meaning is spelled with the condition INSIDE
the argument, `contains(r & (g: "x"))`, which narrows what is searched for (§0.1 L61), or `contains(r) & some((g:
"x"))`. So every `contains` exposes the repeated label `hit` and makes its argument's labels repeated: two
transforms in one `&` chain then both offer `hit`, and a label set once in the argument (`contains(/(?<k>\d)/)`'s k)
is repeated in the result (a bare `$k` is the §4.3 error at the default level); §13 O55. RULED in rev 13 (CF:1068-1072
on main, his words `occurrences(x, label = "foo")`, CF:1070): a call may NAME its hit label, two calls exposing the
same hit label in one chain are the ambiguity ERROR naming both, and the per-call name is the fix:
`(m: contains("a", label = "ha") & contains("b", label = "hb") & some((ha: ...)))`. The SPELLING `label =` is the
owner's placeholder (his examples' spellings are placeholders, 2026-11-10): rev 9 dropped `label =` because `label`
is a reserved metadata name (§5.4 `.` row; review r10 CENSUS-14), so the setting's name is a spelling-step item, not
ruled; this document writes his spelling, marked placeholder. Cost:
where no question reads x's labels, the compiler may build `contains` as the plain set (an optimisation that changes
no answer and does not change which labels exist).

THE DEFINITION'S REQUIREMENTS (CF:918-921, accepted at CF:905), and how the text above meets each:
1. LAZY GAPS, so the hits are LEFTMOST and NON-OVERLAPPING. In PCRE's priority parse of `(?:.*?(x))*.*` against the
   whole span, the outer `*` (greedy) tries one more hit before stopping, and the lazy gap tries the shortest gap
   first, so each iteration takes the leftmost place where x matches; the rest of the pattern always succeeds (the tail
   `.*` takes what is left), so nothing backtracks into a hit and each hit is x's own PCRE-preferred match at that
   place. That is PCRE2's find-all order (the C find-all iterator's) for every argument that passes THE TWO ARGUMENT
   REFUSALS below; for the arguments they refuse, the loop and find-all differ.
2. A REPEATED LABEL'S COUNT FOLLOWS PCRE'S PRIORITY PARSE (which with lazy gaps is find-all order). As a SET the
   pattern is every string and it has other parses (a gap can swallow a hit); the hits are the iterations of PCRE's
   parse. Rev 8 marked this a CONFLICT with the 11-14 some-parse rule (C36); the ONE READING (§4.5, CF:953-955)
   RESOLVES it: PCRE's parse is the reading of every label, so `occurrences` needs no exception.
3. THE EMPTY-MATCH ADVANCE: the first of THE TWO ARGUMENT REFUSALS below.
4. THE LOOK-ALIKE ROW: "`(g: x)` on a search result means ALL hits" is §0.1 L52 (BY DESIGN).

THE TWO ARGUMENT REFUSALS (stated once; review r10 SIM-1, the two are siblings). PCRE's LOOP over the body agrees
with find-all hit for hit EXCEPT where one iteration can see another, and there are exactly two ways it can:
- A NULLABLE ARGUMENT. PCRE ends a loop whose iteration matched the empty string, so an argument that can match empty
  gives at most ONE hit (the first, possibly empty) where find-all advances and continues (`/a*/` on `baa`: one empty
  hit at 0; Python's `re.findall("a*", "baa")` gives `['', 'aa', '']`, three; §0.1 L53).
- AN ARGUMENT WITH A BACKREFERENCE OR CONDITIONAL THAT CAN RUN WHILE ITS GROUP IS UNSET IN THE CURRENT HIT. PCRE
  keeps a group's capture from an EARLIER iteration of the loop, so a later iteration's `\k<c>` or `(?(<c>)...)` that
  runs before this iteration set c reads the earlier hit, where find-all starts each hit with the group unset: `/(?:(?<c>a)|b)c(?(<c>)a|d)/` on `acabcd` gives ONE hit `aca`
  in the loop and two, `aca`@0 and `bcd`@3, in find-all; `/(?:(?<c>a)|b)\k<c>?c/` on `ac bac` gives the loop's last
  hit `bac`@3 against find-all's `ac`@0, `ac`@4 (libpcre2 10.46 and Python's `re`; §0.1 L62).
Each is a COMPILE ERROR naming its fix: `x & !""` for the first; for the second, an argument in which SOME PATH from
its start reaches a backreference or conditional naming one of its groups WITHOUT having set that group in this hit
(a static property of the argument's own pattern) is refused with "an `occurrences` argument can read its own group across
hits: `\k<c>` can run with c unset in this hit; set c on every path before it, or write the alternatives out"
(finite groups: `enumerate`, §5.5). An argument whose reader always follows its group's capture in the same hit
(`/(.)\1/`; E-SEP's PCRE pattern `\d{4}([-\/.])\d\d\1\d\d`) is NOT refused: the reader sees only this hit's capture,
and the loop equals find-all hit for hit (review r12 SIMULATE-2: `(?<c>.)\k<c>` over all 1,365 subjects of length 0-5
on four letters, 0 differences). REV 11 NARROWS the rev 10 refusal (which refused every backreference to the
argument's own group) to its stated reason (LEAN, this lane's pick on review r12 SIMULATE-2): the refusal and the
reason then coincide, and the G0 look-alike `/(.)\1/` searched vs `contains(/(.)\1/)` (the searched final pattern
legal, the `contains` argument refused) disappears; the price is one static path check on the argument instead of a
syntactic one. The refusal of the first is the MANAGER'S CALL (LEAN, rev 9;
§13 O53); of the second the manager's pick (LEAN, rev 10; §13 O53). Both are the empty-match rule's kind of refusal
(§7): a construct whose PCRE meaning inside the body is not what `occurrences` promises. Elsewhere the hits are
find-all order, as the owner expects of a search.

THE ITERATION'S OWN VALUES (review r10 SIM-2; the manager's pick, LEAN). A hit's labels are read WITHIN ITS OWN
ITERATION: a label of the argument that the iteration did not set is UNSET in that hit (§4.2), even when PCRE's raw
capture state still holds an earlier iteration's value. `occurrences(/(?<g>a)?b/)` on `abb`: hits `ab`@0 (g = `a`) and
`b`@2 (g UNSET); PCRE's capture state after the match reports g = (0,1), hit 1's `a`, lying outside hit 2. So `(m:
occurrences(/(?<g>a)?b/) & (g: "a"))` on `abb` REJECTS (hit 2's g is unset, `label.unset`). This is a stated DEPARTURE from
PCRE's raw capture state, not from PCRE's parse: the parse (which path each iteration took) is PCRE's; what an
iteration did not set, it does not have. The same root as the second refusal above, which is why that one is a
refusal: a backreference INSIDE the body reads the raw state, which no per-iteration reading can change.

ANCHORS IN THE ARGUMENT (rev 12, THE ONE ANCHORING RULE, §11; CF:1011-1019, accepted at CF:1006; rev 10-11's
"`contains` and `occurrences` REMOVE the anchoring", CF:991-994, is RESTATED by it). The body of `occurrences` (and so of
`contains`) is a FILTER: it matches the WHOLE span. Its argument sits in a HOLE inside that body, after a plain gap,
so it is not a filter of its own and carries no anchoring of its own; nothing is removed or put back. A `^` or `$`
written in the argument is PCRE's, with the span as the subject: `^` is the span's start (or, under an explicit
`(?m)`, a line start inside it, C35), so only an empty lead gap reaches it and `occurrences(/^err/)` has AT MOST ONE HIT,
at the span's start; `contains(/^err/)` = `startsWith("err")` "falls out of PCRE" (CF:1018; L17). `$` is PCRE's `$`:
the span's end OR just before a final newline of the span, so `contains(/err$/)` ACCEPTS `err\n` while
`endsWith("err")` rejects it (§0.1 L63; libpcre2 10.46 and Python `re`, `docs/dev/lanes/predspec12_anchor.out`); the
exact end is PCRE's `\z` (`contains(/err\z/)` = `endsWith("err")`). Rev 10-11 read `$` as the exact end (review r10
SIM-5); rev 12 withdraws that as an extra rule ("no extra rule", CF:1014; LEAN, this document). Rev 13: an anchor in the
argument sits in a HOLE of the body, so the `anchor.operand` warning does not fire on it (`x & contains(/^err/)` is the
documented "starts with", §11).

ZERO HITS (CF:933 "What's missing is the + or * control"; the record, CF:937-940; RULED BY ACCEPTANCE (CF:997-1000 on main, "Agree with lean"; rulings R-1), §4.2). The quantifier the user chose decides, as for any loop the match reached (§4.2 states the boundary with an
UNSET label once). `occurrences`'s loop is always reached (it is the body's first construct):
- With `min = 0` zero hits are ALLOWED: `occurrences` never rejects (zero iterations always parse; as a set it is every
  string). A plain condition or `all(...)` on the hits HOLDS over zero hits (every one of none); `some(...)` fails,
  `count(...)` is 0, `occurs.none(...)` holds. Rev 8's lean (a plain condition FAILS on zero hits) is WITHDRAWN; "there
  is a hit and every hit is an x" is written `occurrences(r, min = 1) & (g: "x")` or `some(...) & (g: "x")`.
- With `min = 1` zero hits REJECT the span; otherwise the hits are the `min = 0` hits (above).
`(m: occurrences(r))` alone narrows nothing (§0.1 L16); `!occurrences(r)` is empty, the empty-intersection error (L51), and
`!occurrences(r, min = 1)` = `!contains(r)`.

HAND CHECKS (rev 9: re-run for `min` 0 and 1). Each row was derived by hand from the priority parse, then run on the
system libpcre2-8 10.46 through its public API: the loop `(?:.*?(X)){min,}` UNROLLED into nested optionals with one
capture group per iteration (equal to the loop in priority for an argument that passes THE TWO ARGUMENT REFUSALS;
review r10 SIM-1 found the backreference/conditional exception), matched against the whole span
(PCRE2_ANCHORED|PCRE2_ENDANCHORED), every hit read from the final match, so nothing abandoned is recorded; Python
3.14's `re` ran the same patterns as a second engine and agreed on every row (script and output:
`docs/dev/lanes/predspec9_reading.py`, `predspec9_reading.out`). The argument was spliced RAW. No row has a `.` or a
numbered group; one row has a top-level `|` (`/aab|a/`), which the capture `(?<hit>...)` around the argument already
scopes; so raw splicing and the hole's own scope agree on all eight (review r10 SIM-3; the reason corrected in rev 11,
review r12 SIMULATE-3).

| span | argument X | hits, `min = 0` (PCRE's parse) | `count` | `min = 0` accepts | `min = 1` hits | `min = 1` (= `contains`) accepts |
|---|---|---|---|---|---|---|
| `abx aby abx` | `/ab(?<g>[xy])/` | `abx`@0 g=x, `aby`@4 g=y, `abx`@8 g=x | 3 | yes | the same three | yes |
| `xyz` (no hit) | `/ab(?<g>[xy])/` | none | 0 | yes | none | NO |
| `aaa` | `/aa/` | `aa`@0 (a hit at 1 would need a lower-priority parse) | 1 | yes | `aa`@0 | yes |
| `err x err` | `/^err/` | `err`@0 (`^` is the span's start) | 1 | yes | `err`@0 | yes |
| `x err` | `/^err/` | none | 0 | yes | none | NO |
| `err\nerr x\nok` | `/(?m)^err/` | `err`@0, `err`@4 | 2 | yes | the same two | yes |
| `aab` | `/aab\|a/` | `aab`@0 | 1 | yes | `aab`@0 | yes (`min = 2` would give `a`@0, `a`@1: L57) |
| `baa` | `/a*/` | the empty string @0, then the loop ends (rev 8's loop run) | 1 (find-all: 3) | refused (L53) | refused | refused |

On the first row: a plain `(g: "x")` fails (hit 2), `some((g: "x"))` holds, `occurs.exactly(2, (g: "x"))` holds,
`count((g: "y"))` = 1 (§4.3). On the `xyz` row: a plain `(g: "x")` HOLDS at `min = 0` (no hit to violate it) and the
span is rejected at `min = 1` (§0.1 L55). The unrolled form is NOT the loop for a nullable argument (it does not stop
at an empty iteration: six empty hits on `baa`), which is why the `/a*/` row keeps rev 8's loop run.

THE OWNER'S EXAMPLE (his semantics, CF:880-887 and the predspec7 brief; his own spelling bound `d` to a search of the
subject with the withdrawn `~`; his example stays the INTENDED BEHAVIOUR). A NAME BOUND TO A TRANSFORM'S RESULT BINDS
THE TRANSFORMED RX (the owner: "the name binds to the transformed regex as for all transformed regex", CF:929), so his
`d` is the `occurrences` transform itself, applied to a span like any filter. With `r := /ab(?<g>[xy])/`, `hits := occurrences(r)` and a
pattern P whose label m holds `abx aby abx`:

    P & (m: hits & occurs.exactly(3, (hit: /(?s).*/)))   # his count(d) = 3: a group question, phase 1
    P & (m: hits & some((g: "x")))                        # some hit has g = x: phase 1
    P & (m: hits & occurs.exactly(2, (g: "x")))           # two hits have g = x: phase 1
    $m.hit[2]                                             # his d[2] = aby: ONE iteration, captures level
    $m.hit[2].g                                           # his d[2].g = y: captures level
    $m.hit[(g: "x")]                                      # his d & (g: x): iterations 1 and 3, positions kept

The first three are GROUP QUESTIONS, which compile to states (phase 1; CF:922-924, accepted at CF:905). The last
three need captures inside a loop, a higher capability level with its cost shown: for the two that read ONE
ITERATION that is RULED BY ACCEPTANCE (CF:972-973, "1. agree", CF:977: "reading ONE hit"); for the third, which
SELECTS iterations, it is this document's consequence (LEAN; review r12 CENSUS-8). The selection is written over the
ITERATIONS, in the label path, and `$` reads the strings AFTER it (rev 11, review r12 CENSUS-1; spelling LEAN): in a
match position the index bracket keeps the iterations its filter accepts, a numeral by POSITION (`[2]`), a condition
by the iteration's OWN LABELS (`[(g: "x")]`, the record laid against that iteration, SAME ITERATION BY RECORD, §4.3);
the kept iterations keep their positions (iteration numbers) and their match order. They read through `$`'s ONE
meaning (§5.4 `$` row): the VALUE(S) of a label path, one ENTRY per iteration in match order (a set-once label has one
entry, so its `$x` is a one-string set as before); `$m.hit[2].g` reads the WHOLE PATH `m.hit[2].g`, iteration 2's g
(never a field of the string `$m.hit[2]`, which carries no labels); `$m.hit[(g: "x")]` reads the hits of iterations 1
and 3. Rev 10's `$m.hit & (g: "x")` laid a condition against captured strings, which have no labels (review r12
CENSUS-1). `(hit: /(?s).*/)` is "every hit" spelled as a
condition; a shorter spelling is §13 O55. `hits` is an rx (a binding names whatever its expression is, §5.1), so
`(m: hits)` and `(m: occurrences(r))` are one program (§0.1 L2); no special case for `occurrences` (§13 O54 RESOLVED for `d :=`).

`x & s` with s an rx stays MEMBERSHIP (`x & a`; no `in`): it is not a "some result" spelling (§0.1 L54); over
iterations the one spelling is `some(...)` (CF:913-914).

**REASONING.** The owner's criterion "few types and few operators that always mean the same thing wherever they are
used" (CF:847-848): two operators leave, and the one thing rev 7 had to invent for search, a MATCH-TIME array with
its own rules (rev 7 §3.4, O50), is gone: the hits are the iterations of a repeated label, which the language had
already (§4.3), and the array interface over them is the general one for ANY repeated label (CF:922-923). `occurrences`
is a filter like `contains`, so it composes by `&` and `:` like every other filter, and `^`/`$` in its argument are
PCRE's with the span as the subject, the one anchoring rule (§11). `min` is the loop's own lower bound, so zero hits follow the rule of every loop
(§4.2) and `contains` is no longer a second body with a second reading of its argument's labels. The two refusals
keep "the hits are find-all order" true for every argument that compiles, so one sentence describes what `occurrences`
finds. Search results stay values-not-globals in the owner's sense ("Even Perl had the awkward $1"): a hit is reached
through the label of the match it belongs to, never through a global.

**STATUS.** Search as a library transform of the `contains` family, `~` and `!~` withdrawn, the hit a repeated label,
the definition requirements (lazy gaps, the count along PCRE's priority parse, the empty-match advance stated, the
look-alike row): CF:907-921, accepted at CF:905 ("Do it"; the transform idea is his own, CF:903-904). Search a
transform but not a filter modifier: LEAN (review r10 FIXA-1). The hits follow PCRE's matching, "always": RULED
(CF:932-933, his words); C36 RESOLVED by the one reading (CF:953-955). A bound name holds the transformed rx: RULED
(CF:929, his words). `min` with default 0: the owner's LEAN ("Perhaps", CF:933-934); `min` only and no `max` for now:
RULED (CF:951-952, "we could skip it for now"); `min` 0 or 1: RULED (CF:963-966), the error for other values LEAN
(CF:968-969); zero hits decided by the quantifier and a plain condition true over zero allowed hits: the record's
reading (CF:937-940) of his "+ or * control" (CF:933), now RULED BY ACCEPTANCE (CF:997-1000 on main, "Agree with lean"; rulings R-1). `contains` accepting what
`occurrences(x, min = 1)` accepts: the manager's note (b) (CF:944-945); ONE definition and its answer move, the written
bodies and the hand checks: LEAN (this document; the move: review r10 FIXB-3, the manager's pick). The refusal of a
nullable argument and the scoped `(?s:...)` gaps: LEAN (manager, rev 9; §13 O53); the refusal of an argument reading
its own group (narrowed in rev 11 to a reader that can run with the group unset in this hit, review r12 SIMULATE-2),
and the iteration's own values: LEAN (the manager's picks on review r10 SIM-1, SIM-2; the narrowing: this lane's
pick). `^`/`$` of the
argument = PCRE's, with the span as the subject: RULED BY ACCEPTANCE (CF:991-994, accepted at CF:990; restated by
CF:1011-1019, accepted at CF:1006; D193 add. 3; CF:761); rev 10's exact-end `$` (review r10 SIM-5) WITHDRAWN in rev 12
(LEAN, this document's reading of "no extra rule"). The NAME `occurrences`: RULED (CF:1026-1031 on main, rev 13;
§13 O61 CLOSED); the label name `hit`: not ruled (§13 O55). The group questions phase 1: CF:922-924, accepted at CF:905;
one-iteration access at captures: RULED BY ACCEPTANCE (CF:977). The owner's example: his intended behaviour; its
`$` reading: LEAN (review r10 FIXA-3); the selection spelled in the path, `$m.hit[(g: "x")]`: LEAN (review r12
CENSUS-1). SUPERSEDES rev 8's `contains(x) := /(?s).*${x}.*/` body, rev 8's zero-hit lean
(fails), rev 9's unscoped `(?s)` body, and rev 7 §2.6 (`$x ~ rx` as an operator, the search result as a match-time
ARRAY VALUE, `!~` as sugar) and rev 6's "a search returns an rx (the occurrence set)" (CF:873) as a VALUE reading; its
occurrence order (non-overlapping, leftmost, CF:74) is kept as requirement 1. Binding a test: allowed (§13 C6
RESOLVED).

### 2.7 Filter modifiers: the pullback kind of transform

**RULE.** A TRANSFORM is a macro FILTER -> FILTER (its parameter is a filter and its result is a filter, the one
input rule of §2.1, CF:860). A FILTER MODIFIER is the transform of THIS section (the owner's ruling "transforms are
FILTER MODIFIERS", CF:722, named the kind then known; `occurrences`/`contains` came later, §2.6, §0.3): given a filter S it returns a NEW FILTER that accepts the subjects
S would accept once parts of them are ignored or reinterpreted. THE TRANSFORM TRANSFORMS THE FILTER, NOT THE
SUBJECT: the subject is never modified; the modified filter reads it differently. Mechanically the modified filter
is the pullback of S under the modifier's READING t, a finite transducer or a finite table (the strings whose reading
lies in S): one
construction, regular in, regular out (inverse image under a rational relation); a non-finite t needs `functions`.

    month & padded(between(1, 12))                 # accepts "05", "5", "12": leading zeros ignored by the filter
    t & unpadded(5, between("09:00", "10:00"))      # accepts "9:00": the filter reads it as if zero-padded to width 5
    (msg: quoted(contains("timeout")))              # the filter reads only the text inside the quotes
    (host: any_case("example.com"))                 # the filter ignores letter case
    alts & !startsWith("#") & length(<=20)          # the filter reads the subject's length
    mname & month_numbered(between(1, 6))           # month names whose number is 1..6: "Jan" .. "Jun"
    quoted(any_case("host"))                        # modifiers nest, in reading order

NAMING RULE (rev 12: EVERY TRANSFORM THE LIBRARY PROVIDES, the owner's ruling CF:1020-1022, accepted at CF:1006;
rev 10-11 bound modifiers only, review r10 FIXA-1): a provided transform is named for HOW IT CHANGES THE FILTER, which
values the changed filter accepts, or (LEAN, this document's reading, derived from the owner-ruled name `length`,
CF:722; not part of CF:1020-1022's words) what it reads (an adjective or phrase: `padded`, `unpadded`, `any_case`,
`quoted`, `length`, `month_numbered`, `anchored`, `occurrences`; a predicate on the value: `contains`, `startsWith`,
`endsWith`), never a verb acting on the subject (`unpad`, `trim`, `lowercase`, rev 12's `search`). The owner's words: "the name transform
seemed to imply you were transforming the subject, but of course you're transforming the filter ... What helped was
calling it "padded"" (CF:1006-1008). Rev 12's `search` FAILED the rule; the owner renamed it `occurrences` (CF:1028;
§13 O61 CLOSED), a name that passes through the "what it reads" clause (LEAN above) or as a description of the
accepted values read occurrence by occurrence. The audit of every provided name is in §13 O61. A modifier is applied to a filter by a call and the result is used like any filter: `x &
padded(S)`, `(x: padded(S))` (the operand arrives via `&` or `label:`, never as an argument, §2.3); `&` stays pure intersection (§2.2), so a modified filter may stand
anywhere in a chain. A modifier without its filter argument where a filter is needed is the unapplied-macro error
(§2.3). `!padded(S)` is an ordinary filter (the complement of a filter). A modified filter's argument is a SET
POSITION (§11): `^`/`$` inside it are the ends of the span the modified filter filters, AS THE MODIFIER READS IT (the
argument's "own" start and end in rev 6's words: the argument filters what the reading yields, so its ends are that
span's ends). The argument is a FILTER (the modified filter tests whether the reading lies in it), so under THE ONE
ANCHORING RULE (§11, CF:1011, rev 12) it matches the WHOLE reading, and a `^`
in it adds nothing: `padded(/^5/)` = `padded("5")`, NOT `padded(startsWith("5"))` (§0.1 L13; rev 10 said the
opposite, review r12 SIMULATE-1). This is the one filtered-span rule of §11 applied to an
argument (review r8 P6-5: an argument never opens a span of its own, whether the macro is a modifier, `contains` or a
user macro); `\b` and edge lookarounds are the edge-assertion error (§11). The variable-width lexicographic lint (`compare.width`) suggests `unpadded(n, ...)`.

**REASONING.** One mechanism (the pullback) collapses rev 0's transform sections, pattern -> value mappings, `jstr(p)`
and the binary forms into one closure theorem (predx S1, §8.2). Frank: "The problem is the name. Trim or unpad imply
they are doing something to the subject. But they are not. They are changing the filter to ignore elements of the
subject." A filter -> filter macro needs no operator and no position in an `&` chain, so `&` stays order- and
grouping-free (G0, review OWN-1/RUL-11), and C1/C20/C22's transform cases dissolve.

**STATUS.** RULED (CF:722, OWN-1: filter -> filter, the pullback, nesting in reading order, the naming rule, the
docs rule), SUPERSEDES the right-associative `&` pipeline (`x & unpad & between(1, 12)`), the `->` / `;` stage ideas,
and the earlier function forms `unpad(S)` / `length(<=20)` read as images. Names `padded`, `any_case`, `quoted`,
`length`, `month_numbered`: RULED (CF:722). `unpadded(n, S)` and `json.quoted`: LEAN (this document's names under the
naming rule, §13 O37). The naming rule over every provided transform: RULED BY ACCEPTANCE (CF:1020-1022, accepted at
CF:1006; rev 12); `anchored`: RULED (the owner's own name, CF:1005, CF:1009); `occurrences`: RULED (CF:1028, rev 13);
the "or what it reads" clause: LEAN (this document, from `length`, CF:722; review r14 CENSUS-6).

## 3. The array and map interfaces

### 3.1 Array interface and map interface

**RULE.** ARRAY and MAP are INTERFACES applied to a thing, never values that can be created (the owner: "Array and
map are interfaces that can be applied to regex but interfaces aren't themselves values that can be created",
CF:890-891; rev 7 called them "views"). An rx has both. ARRAY interface = its top-level alternatives (flat): `/a|b|c/`
has 3 entries, `/abc/` has one, `/(?:a|b)|c/` has 2. MAP interface = its labelled groups (a tree; nesting gives paths
`d.year`). Counts differ: `/(?<y>\d{4})-(?<m>\d\d)/` = array 1, map 2; `/(?<a>x)|(?<b>y)|z/` = array 3, map 2.
Map order = PCRE group number. The same two interfaces apply elsewhere: the ARRAY interface to a repeated label's
iterations in a match (§3.4, §4.3), the MAP interface to a module (§7, CF:891-892). A labelled alternation where each
alternative is exactly one named group is the ALIGNED case, written with labelled entries: `[x = /foo/, y = /bar/]`
IS the rx `(?<x>foo)|(?<y>bar)` (`[ ]` = any one entry, `=` labels an entry, §5.4; `[1, 3, 5]` = `1|3|5`): a `[ ]`
literal WRITES AN RX, it creates no array. Unlabelled entries are index-labelled. Reverse lookup (which branch
matched) is reading the accept-state label (`.index`).

THE WRITTEN FORMS OF THE TWO INTERFACES. `[ ... ]` is the written form of the array interface (an rx spelled entry by
entry) and the RECORD `( ... )` is the written form of the map interface (no third interface: the manager's record,
CF:870; the owner's own words offer "a third view on a regex but an abstract one", CF:853, which this reading folds
into the map interface). The record is never a value (§5.4): it appears only laid against something that has fields
(a macro's parameters, a pattern's labels, a result's groups). The relation is ONE-WAY: an rx can be read through
the map interface as a record (its groups are its fields); a record is never read as an rx. The rev 5 map literal `(x
= /foo/ | y = /bar/)` is WITHDRAWN (a `( )` in value position would be a record used as a value, and a map is never
created; the `[ ]` form above says the same thing; §0.1 L43, §13 O42). The closure "a record of rx is their sequence"
was considered and NOT adopted: it would reverse the no-concatenation lean (§2.5) and lose entry boundaries (`(1,
40)` and `(14, 0)` would both be `140`); sequencing stays with `join` and literals.

**REASONING.** Frank: "Maps are the labeled groups. The interpretation between the two is different and can have
different counts"; arrays and maps are perspectives on an rx, not types; 2026-11-15: they are interfaces "applied to"
a thing, which is why one interface serves an rx, a label's iterations and a module.

**STATUS.** RULED (CF:343, two VIEWS, now INTERFACES: CF:890-891, his words; SUPERSEDES ONE TABLE CONSTRUCT and `{Jan:
1}` / `["US" => ...]`; value-valued maps: §13 C7). The array interface over a repeated label's iterations:
CF:922-923, accepted at CF:905; the map interface of a module: RULED (CF:891-892). One-way: RULED (CF:853-854, his
words: "You can view a regex as a record but not vice versa"). The record never a value: RULED (CF:851-852, "it
can't be bound directly ie not first class type"). The record as the written map interface, "no third view", and the
sequence closure not adopted: RULED only by the acceptance (CF:866, accepted at CF:851; review r8 RUL-2: "no third
view" is the manager's word, not his). The labelled array as the one spelling of the aligned case and the map literal
withdrawn: LEAN (this document; CF:542's spelling was itself a lean; §13 O42). The metadata members `.index`/`.label`
vs user labels of those names: a user label so named is an ERROR (the manager's call, LEAN; §13 O31, §5.4 `.` row).

### 3.2 The four tools

**RULE.**
1. `X[...]` = POSITION in the array interface only: integers, integer sets, numeric filters (`X[1]`, `X[<4]`); the
   result is always an rx read through the array interface, keeping the ORIGINAL positions; a string or non-numeric
   filter inside is a compile error suggesting the right tool. Indexing descends (`d[1][1]`). Integer sets and
   numeric filters select among positions 1..n only (`X[<4]` = `X[1|2|3]`); there is no `X[0]` (the whole rx is X
   itself; review r8 P6-2, CENSUS-13: a group-0 index read the map interface's numbering through the array
   interface's bracket). Out of range = entry absent: tests on it are false. 1-based. `[n]` reads BY POSITION
   (review r10 FIXA-2, CENSUS-10; LEAN; §5.4 `[ ]` row, §0.1 L64): in VALUE position it indexes the entries of the rx
   on its left, a SPELLED array read at compile time (§3.4; `alt.x[1]` = the first group labelled x in the PATTERN);
   in a MATCH position (under `$`, or a path on the left of `:`) it indexes the ITERATIONS of the label in the MATCH:
   `$m.hit[2]` reads iteration 2's text (the `captures` level, RULED BY ACCEPTANCE, CF:977; §4.3), `(x[2]: S)` tests
   it (§4.3, O56 (2)). In a match position a CONDITION in the bracket keeps the iterations whose OWN labels meet it
   (`$m.hit[(g: "x")]`, iterations 1 and 3 of the owner's example, positions kept; rev 11, review r12 CENSUS-1: LEAN;
   the `captures` level, LEAN, CENSUS-8).
2. `X & f` = filter by LANGUAGE; `&` distributes over entries and empty products drop:
   `alts & !startsWith("#")` keeps passing literals; `rows & (w: >100)` keeps matching rows.
3. `where(p, X)` = SELECT entries by a compile-time STRUCTURAL property (the selecting twin of `each`; not the filter
   role, §0.3); `where_group(p, X)` for the map interface; both return an rx (§2.1).
4. `X.name` = a FIELD of the MAP INTERFACE of the thing on the left; `.name` is never digits. ONE meaning (the
   manager's lean the owner agreed to, CF:892, CF:898-899): a LABEL (`A.Saturday`, `alt.repeated[1]`, `d.year`), a
   module MEMBER (`json.row`, the module's map interface, §7), METADATA (`.index`, `.label`, reserved fields) and,
   under `$`, a label PATH (`$rest.year`, §5.4) are instances of it. A user label named like a metadata field
   (`index`, `label`) is a compile ERROR naming the reserved field (rev 9: the manager's call, LEAN; §13 O31).

**REASONING.** The output of `[]` is always an rx read through the array interface, so `[]` uses the array
interface. `&` on structural properties
would intersect languages (wrong), hence `where`.

**STATUS.** `[]` positional only: RULED (CF:553). 1-based: RULED (CF:583, predx Q7). Filters over 1..n: LEAN (review
RUL-9). Multi-index `X[1, 3, 5]`: if adopted it is the array reading, any one of the positions = `X[1|3|5]`
(CF:863); whether to adopt: §13 C5. The dot's one meaning: RULED by acceptance ("agree", CF:892, to the lean at
CF:898-899).

### 3.3 Holes and groups are single entries; `|` concatenates entries

**RULE.** Expression `|` CONCATENATES the operands' entries (each operand contributes its top-level alternatives; appended
entries take lowest PCRE priority). An rx GROUP or a `${}` HOLE is ONE entry. With `x := /(a|b|c)/`: `x | /d/`
has 2 entries; with `x := /a|b|c/`: `x | /d/` has 4; `/${x}|d/` has 2 for either (§0.1 L24). A hole is an atom for
correctness (`/${x}d/` = `(?:a|b|c)d`). Expression parentheses are precedence only. `join` of no entries is the
empty string.

**STATUS.** LEAN (manager, CF:385; ADD = `|`). The `array.hole` warning: LEAN (proposed by review OWN-8, PLAN).

### 3.4 Extensional vs structural operations

**RULE.** EXTENSIONAL (`& | !`, comparisons, filter modifiers) depend only on the language: which strings pass.
STRUCTURAL (indexing, `each`, `join`, `where`, `.label`, `enumerate`, entry counts) read the SPELLING: `/a|b/` and
`/b|a/` are equal under `&` but differ under `[1]` (and in PCRE priority). A CONDITION on a label reads the spelling
too, through PCRE's parse of it (§4.5): two spellings of one language admit the same strings under `& | !` and may
answer differently under a condition (§0.1 L25, L60; review r10 FIXB-1). Internal rewrites (altcls, alt_normal_form) never change
user-visible structure. Field-wise narrowing that keeps other entries is structural (`each_group((& (x: d2)), rx)`,
the condition passed as a section, §5.2; rev 6 passed a bare `&`, an operator as an argument, review r8 P6-8 (d)),
never `&`.

SPELLED ARRAYS vs A REPEATED LABEL'S ITERATIONS (stated once; review r8 P6-7, restated by the transform ruling,
CF:922-923). The array interface applies to two kinds of thing. (1) An rx whose entries are known from the program
text (a literal `[ ]`, a binding of an rx, a `join` input, an `enumerate` or `records` result) is a SPELLED array: the
structural tools above read it at compile time, and G4 covers it. (2) The ITERATIONS of a repeated label in one match
(a group inside a loop, the `hit` label of an `occurrences`, §2.6) exist only per match: the array interface over them is
§4.3's, where the GROUP QUESTIONS (a plain condition, `some`, `all`, `count`, `occurs.*`) compile to states (phase 1)
and access to ONE iteration (`$m.hit[2]`) needs captures (RULED BY ACCEPTANCE, CF:977). No structural tool of this section (`each`, `join`,
`where`, `enumerate`, `.label`) reads iterations: on a label that can repeat it is a compile error naming the group
questions. Rev 7's MATCH-TIME ARRAY (a search result as an array value, `d := $m ~ /.../`) is gone with `~`: nothing
in the language is an array value (CF:890-891).

**STATUS.** RULED (CF:328, CF:385). The structural effect of `&`'s distribution over entries is unstated: §13 C17.
The two things the array interface applies to: CF:922-923 (accepted at CF:905), restated here (LEAN); the error for a
structural tool on iterations: LEAN (this document; review r8 DRIFT-2's "two populations", now one population per
kind of thing).

### 3.5 Arrays of filters and filter modifiers

**RULE.** Closure one level up: an array of rx is an rx (alternation); an ARRAY OF MACROS is a macro, so an array
in the filter role filters pointwise (`t & [f, g]` = `(t & f) | (t & g)`) and an ARRAY OF FILTER MODIFIERS is a
filter modifier (`[padded, any_case](S)` = `padded(S) | any_case(S)`). The `[ ]` bracket gives "any one entry" in
every case, and the comma only separates entries (§5.4). A MIXED rx/macro array is an error (fix: write the rx entry
as a section, `(& /x/)`).
Entries must share arity. `.index` keeps the original positions when entries drop, so `ipv4 & cidrs` reports which
entry admitted the match.

**REASONING.** Frank: "an array of rx is an rx. An array of filters|macros is macro?" Classification against a
table (predx §8.3 item 1) becomes `pattern & table` with no new construct.

**STATUS.** RULED (CF:644, ARRAYS OF FILTERS); arrays of modifiers restated under OWN-1 (CF:722); "a list of
filters" as the `[ ]` any-one reading: RULED (CF:863); "filter" read as the role of a macro: CF:858.

## 4. Match values

### 4.1 `x:` constrains, `$x` reads; condition literals

**RULE.** The entry `x: S` of a condition = the set of WHOLE MATCHES whose label x is in S (inside a condition
record, a macro awaiting the pattern that defines x). `$x` = the CAPTURED STRING of this match (a one-string set,
context-free, §11) for a set-once label; for a REPEATED label, one captured string per iteration, read through the
array interface (§5.4 `$` row, §4.3). `x:` is ALWAYS the
constrained side; `$x` is ALWAYS a value used (operand, insertion `${$x}`, output). Capture-vs-capture is `x: <$y`
(§4.6). `$x & ...` used AS A CONDITION is an ERROR: "did you mean `x: ...`?". The left of `:` is a label PATH
(`d.year: <2000`), never an expression: a computed value is constrained through a computed label (§4.4).

CONDITIONS ARE RECORDS LAID AGAINST LABELS. A condition is written as a RECORD `( ... )` (§5.4) whose entries are
`label: S`; it is laid against the labels of the pattern it meets by `&`. The RECORD holds its entries together
(the AND comes from the record, not the comma, CF:866 (b)); the COMMA only ends an entry. An entry runs to the next
comma or the closing paren, and inside an entry `&` and `|` bind tighter than `:` (the C22 rule, restated in
record terms as ENTRY EXTENT, §0.3; every answer is unchanged, §13 O43). So:
- all of several conditions = one record: `(major: 1, minor: >=4)` = `(major: 1) & (minor: >=4)`;
- any one of several = separate records joined by `|`, or an array of them: `(major: 2) | (major: 1, minor: >=4)`
  (= `[(major: 2), (major: 1, minor: >=4)]` in the filter role, §3.5);
- a set after a label needs no parentheses: `(x: <200 | >900)`, `(month: padded(between(1, 12)))`;
- `(major: 1 & minor: >=4)` is ONE entry, `major: (1 & minor: >=4)`, a compile ERROR (a label inside a value), not a
  misreading;
- `:` outside a record has nothing to constrain: at top level `P & x: S` is an ERROR "write `P & (x: S)`", and so is
  `[x: S]` ("write `[(x: S)]`", §0.1 L47).
A condition is a MACRO (§2.1): written in value position (an argument, `occurs.exactly(1, (name: S))`; a binding,
`c := (year: 2000)`; an array entry) the record is its written body and the macro is the value; the record itself is
never bound (§0.1 L46; §13 O45).
Entry extent reads the same at top level and after a label (G0). In a chain `P & Q & (x: ...)`, x is looked up in
the other operands of the chain (`P & Q`; `&` is order- and grouping-free, so the whole flattened chain); a label in
both is AMBIGUOUS (error naming both); an unknown label is an error listing those available.

PATTERNS TAKE NO ARGUMENTS. A pattern has no parameters, so the call form `isodate(year: S, month: 2)` is a compile
error with the hint "write `isodate & (year: ...)`"; the one spelling is `isodate & (year: S, month: 2)`, a condition
literal with the entry extent above, which always NARROWS the operand (§5.2). The labelled-argument form of rev 3 (the C22
addendum's `p(a: s)` = `p & (a: s)`) is WITHDRAWN; the C22 entry-extent rule stays, for condition literals only. A
parameterised pattern is a macro (`date_in(years) := isodate & (year: years)`, §5.2). `:` constrains a label that
exists, `=` names an entry (in a call, the name is a parameter: `sep = "."`); §5.4.

**REASONING.** Frank: "x: represents a fraction of the search object deconstructed": the pattern is the schema, a
match a row, labels its columns, `x:` a WHERE clause. Avoids the trap that `($x & <200) & ($y & >55)` forces x = y.
ONE condition form (`label: set`) for every condition. On entry extent, Frank: `month: unpad & between(1, 12)` "is
somewhat structural because it's combined with the comma. & binds tighter" (the call form he also named is withdrawn,
CF:744; the extent reads the same in `isodate & (year: ...)`).

**STATUS.** Condition records: RULED (CF:255). One condition form, the left of `:` a path: RULED (CF:595, Q6 concept).
Entry extent (comma separates, `label:` up to the comma, `&`/`|` tighter than `:`): RULED (CF:698, C22), SUPERSEDES
"`name:` takes one operand term". `=` sets a parameter: RULED (CF:706). Patterns take no arguments, the call form
withdrawn: RULED (CF:744: "It can't take arguments anymore correct?", answered correct). The top-level `P & x: S` error
and the flattened chain lookup: LEAN (this document's consequences of the ruled entry extent). Comma records `(x: <200, y:
>55)`: RULED (CF:698). The AND from the record, the comma "next entry", `:` constrains an existing label: RULED
(CF:863, CF:866 (b)); the extent restated in record terms and the `[x: S]` error: LEAN (this document, §13 O43); a
condition written in value position denotes the macro: LEAN (§13 O45).

### 4.2 Unset labels

**RULE.** A comparison on an UNSET label is false (its `!` true); a condition naming a label that is unset for a
match fails for that match; WARN (`label.unset`) when a plain reference can be unset. This keeps extensional `&`
consistent: `[x = /\d/, y = /[a-z]/] & (x: /[0-5]/)` = `[0-5]` (the alternative lacking x drops, §2.3; rev 5
spelled the labelled alternation as the withdrawn map literal, §3.1).

THE BOUNDARY, stated once, PER MATCH (rev 10, review r10 FIXB-2; the manager's lean, RULED BY ACCEPTANCE (CF:997-1000 on main, "Agree with lean"; rulings R-1)). A label is SET ONCE when its group can be set at most once in one match (an optional group `(?<x>...)?` or
`{0,1}`, an alternative that may not be taken); it is REPEATED when some LOOP encloses its group (a quantifier with an
upper bound of 2 or more, or none: `*`, `+`, `{n,m}` with m >= 2, a `list_of` part, an `occurrences` hit; §4.3). Whether a
condition on a label with no value in a match holds is decided by WHERE THE MATCH STOPPED SHORT OF THE LABEL: the
deepest construct on the path from the pattern to the label's group that the match ENTERED.
- If that construct is a LOOP that was REACHED and ran ZERO times, the label has zero iterations: a plain condition
  (every iteration) HOLDS over none; `some(...)` fails; `count(...)` is 0 (§4.3). The loop's own quantifier allowed
  none (the owner's "+ or * control", CF:933; for `occurrences`, its `min`, §2.6): `*` and `{0,m}` do, `+` does not.
- Otherwise (an optional skipped, an alternative not taken, or an enclosing construct that skipped the loop) the
  match NEVER REACHED the label's group or loop: the label is UNSET and a condition naming it FAILS (this section's
  rule; `label.unset` warns).
Witnesses (§0.1 L56, L65): `/x|(?<n>\d)+/ & (n: <5)` on `x` FAILS (the other alternative was taken; n's loop was
never reached, although its own `+` is never consulted), like the set-once `/x|(?<n>\d)/`; `/(?:(?<n>\d),)*/ & (n:
<5)` on the empty span HOLDS (the loop was reached and ran zero times); `/(?:(?<n>\d)+)?x/` on `x` FAILS (the
optional skipped the loop); `/(?<n>\d)?x/` FAILS and `/(?<n>\d)*x/` HOLDS on `x` (L56). PCRE reports n UNSET in every
one of these: the zero-iteration rule is a CONDITION rule laid over PCRE's parse (it reads where the parse stopped),
not PCRE's capture state.

**STATUS.** The per-match rule (a condition on a label whose group or loop the match never reached FAILS, set once or
not; a loop reached and run zero times holds a plain condition): RULED BY ACCEPTANCE (CF:997-999, accepted at
CF:1000; rulings R-1), which overtakes CF:173's earlier lean ("unset fails") for every never-reached label (rev 11,
review r12 CENSUS-9: one mark per point). The rest of this section's RULE (a comparison on an unset label false, its
`!` true) stays LEAN (CF:173); cited as "ruled" by a later note (§13 O3). That warnings have names: RULED (CF:666); the name
`label.unset`: LEAN (manager's list, review RUL-14.1). The two sentences disagree on `(x: !<5)` for an unset x: §13
O28. The zero-iteration answer (a plain condition true over zero iterations a reached loop allowed): the record
(CF:937-940) of the owner's "+ or * control" (CF:933), which is a diagnosis plus a hedged proposal ("Perhaps search
needs a min max"), which review r10 FIXB-8 found too thin to rule; the owner then ruled the manager's per-match lean
whole ("Agree with lean", CF:997-1000 on main; rulings R-1): a loop REACHED and run zero times satisfies a plain
condition, a label whose group or loop the match never reached fails. RULED BY ACCEPTANCE. The exact wording of
"reached" here (the deepest construct entered): LEAN (this document's statement of the ruled lean). SUPERSEDES rev 9's statement by the
label's own quantifier, under which `/x|(?<n>\d)+/` on `x` held, and rev 8's O28 lean "zero iterations = unset = fail".

### 4.3 Repeated and duplicate labels: the general home of the group questions

Rev 8's CONFLICT MARK (§13 C36: the priority parse vs the some-parse rule) is GONE: the ONE READING (§4.5, CF:953-955)
makes a repeated label's iterations those of PCRE's parse, as for every label.

**RULE.** At the default level a repeated label follows the SEQUENCE RULE: `x: S` constrains ALL iterations; a bare
`$x` on a repeated label is EVERY iteration's captured string (§5.4 `$` row: one entry per iteration), which needs
captures inside a loop, so at the default level it is an ERROR naming the group questions below and the `captures`
level. At `vm`, PCRE's own `\k<x>` INSIDE rx text sees the last iteration (PCRE's meaning, inside a literal); the
expression's `$x` keeps its one meaning at every level (review r10 FIXA-3, CENSUS-1; rev 9 gave `$x` at `vm` the
last-iteration meaning). Duplicate names (`(?J)`, `(?|`) on a SET-ONCE label (no loop encloses the duplicate
groups): plain `$x` gives the lowest-numbered set group. A duplicate label INSIDE A LOOP is a REPEATED label first:
its iterations in match order, each iteration's value from whichever of the duplicate groups THAT iteration set (the
iteration's own values, §2.6), so `/(?J)(?:(?<x>a)|(?<x>b))+/` on `ba` has iterations `b`, `a` (PCRE's raw state:
group 1 = `a`, group 2 = `b`, libpcre2 10.46), `$x[1]` = `b` and a bare `$x` is the repeated-label error at the
default level (§0.1 L64; rev 11, review r12 CENSUS-12: LEAN; a duplicate label set twice in ONE match outside a loop
stays §13 O35). The static
CONSTRAINT SET of a duplicate label (the strings it can hold) is the UNION of the definitions that can set it.
Structurally, `alt.x` returns EVERY entry labelled x as an rx read through the array interface in group order;
`alt.x[1]` (first in the PATTERN, compile time: `[n]` in value position) differs from `$x[1]` and `(x[1]: S)` (the
MATCH's iteration 1: `[n]` in a match position; §3.2 tool 1, §0.1 L64). A repeated label is
ANY label inside a loop (one that can set it more than once; the boundary with a set-once label is §4.2's): a group
under `*`/`+`/`{n,m}` with m >= 2 or no m, a `list_of` part (E-HTTP's `name`), and the `hit` label of a
`occurrences` with every label of its argument (§2.6). There is no second population: rev 7's "entries of a match-time
array" are these iterations.

THE GROUP QUESTIONS, stated once (CF:910-915, accepted at CF:905). Each is a macro with its operand open, standing in
the filter role like a condition (`P & some((g: "x"))`, `(m: occurrences(r) & some((g: "x")))`); the labels it names are
looked up in its operand as for any condition (§4.1).

| form | means, over the iterations of the labels it names | example on the hits `abx`, `aby`, `abx` of `/ab(?<g>[xy])/` |
|---|---|---|
| plain `(g: S)` | EVERY iteration's g is in S (the sequence rule); HOLDS on zero iterations of a loop the match reached (§4.2, RULED, CF:997-1000) | `(g: "x")` fails |
| `all((g: S))` | the same as the plain condition, zero iterations included: the default, "rarely written" (§0.1 L36) | `all((g: "x"))` fails |
| `some((g: S))` | AT LEAST ONE iteration's g is in S; false on zero iterations | `some((g: "x"))` holds |
| `count(c)` | the NUMBER of iterations meeting the condition c: a number: a canonical numeral string (RULED, CF:977-978; §2.1), tested through a computed label or any ordinary filter (`n := count(c)`, `P & (n: ==2)`) | `count((g: "x"))` = 2 |
| `occurs.exactly(n, c)`, `occurs.at_least(n, c)`, `occurs.at_most(n, c)`, `occurs.none(c)` | `count(c)` compared with a constant n; `none(c)` = `count(c)` is 0 = `!some(c)` | `occurs.exactly(2, (g: "x"))` holds; `occurs.none((g: "y"))` fails |

`occurs` keeps the COUNTS only (CF:913): `occurs.some` and `occurs.all` are withdrawn. The record allows "goes away
or becomes an alias"; rev 8's lean is GONE, not aliased (one spelling for one question, G0b; nothing in §12 uses them).

SAME ITERATION BY RECORD (CF:915-917, accepted at CF:905). A record is ALL its entries together ON THE SAME
ITERATION; two calls are two questions, which different iterations may answer. With `/(?<g>[xy])(?<h>\d)/` searched
in a value (§2.6):
- on `x2 y1` (hits g=x h=2, g=y h=1): `some((g: "x", h: 1))` FAILS (no one hit has both); `some((g: "x")) & some((h:
  1))` HOLDS (hit 1 gives g = x, hit 2 gives h = 1). The two spellings DIFFER (§0.1 L31).
- on `x1 y2` (hits g=x h=1, g=y h=2): both HOLD (hit 1 has both). The two spellings AGREE.
For `all`/the plain condition the two spellings always agree (every iteration has both = every iteration has g and
every iteration has h); `count((g: "x", h: 1))` counts the iterations that have both. This REPLACES rev 2's rule that
every `some(s)` over the same set denotes the same occurrence ("two occurrences need two names"; §13 O29 RESOLVED).
Which iteration a record means when its labels sit at different depths (g inside the loop, k outside it): §13 O56.

THE ARRAY INTERFACE OVER ITERATIONS (CF:922-926). The iterations of any repeated label, in match order, are read
through the array interface (§3.1, §3.4); nothing is created. Two levels:
- GROUP QUESTIONS (the table above) compile to states (a capped counter per question, n+2 states, CF:685):
  the DEFAULT level, phase 1 (CF:922-924, accepted at CF:905). The iterations are those of PCRE's parse (CF:919-920;
  the one reading, §4.5).
- ONE ITERATION read out, `$x[2]` (entry 2 of `$x`, the captured string of iteration 2) and `$m.hit[2].g` (the
  whole path, iteration 2's g; `$` covers the whole path, §5.4), needs captures inside a loop: the `captures` level,
  its cost shown (RULED BY ACCEPTANCE: "1. agree", CF:977, to CF:972-973's "reading ONE hit"). Reading EVERY
  iteration (a bare `$x`, `$m.hit`) and SELECTING iterations by a condition in the index bracket (`$m.hit[(g: "x")]`:
  the iterations whose own g is x, iterations 1 and 3 with their positions, the owner's array example, §2.6) need the
  same level: LEAN (this document's consequence, review r12 CENSUS-8; the selection's spelling: review r12 CENSUS-1,
  LEAN). Out of range = the iteration is absent and a test on it is false (CF:62). A TEST on one iteration by a
  literal index (`(x[2]: S)`) does not read text out; CF:62's countdown makes it regular (~k states for i <= k), so
  this document reads it as a group question at the default level (LEAN; the ruling covers READING one hit, and
  whether a test counts as reading is not in his words; §13 O56).
- Each iteration's labels are read WITHIN that iteration: a label the iteration did not set is unset in it, even when
  PCRE's raw capture state holds an earlier iteration's value (§2.6 THE ITERATION'S OWN VALUES; review r10 SIM-2).
- A COUNT IS NOT UPWARD-CLOSED: in a SEARCHED program a shorter span can have fewer iterations and pass a count that
  the whole block fails (`headers & occurs.exactly(1, ...)` on two Host headers reports the one-header span; §0.1 L66,
  review r10 SIM-6). A count over a whole block is written with the program anchored (§12.9).
- No structural tool (`each`, `join`, `where`, `enumerate`, `.label`) reads iterations (§3.4).

**REASONING.** "All iterations" is substitution into the loop body, the only pure lowering (predx §2.1, O4); the
last-iteration rule would need captures inside a loop. One home for every repeated label means `occurrences` adds no rule
(§2.6), and "some" has one spelling (`some(...)`), "all" the plain condition, "how many" `count` and the `occurs`
counts. The record-as-same-iteration rule is the record's own meaning (all entries together, §5.4) applied to one
iteration, so it needs no extra rule either.

**STATUS.** Sequence rule: RULED (CF:583, predx Q4), SUPERSEDES "plain `$x` = last iteration" at the default level.
Plain condition = all, `some`/`all` the one spelling, `occurs` counts only, same iteration by record, the hit a
repeated label, group questions at the default level and phase 1: CF:910-917, CF:922-924 (accepted at CF:905;
"could you use some() to get some hits?" is his own question, CF:904-905). `occurs.some`/`occurs.all` removed rather
than aliased: LEAN. One-iteration access at `captures`: RULED BY ACCEPTANCE (CF:977, to CF:972-973; rev 9: LEAN); a
literal-index TEST at the default level: LEAN (CF:62). `$x` on a repeated label as every iteration's captured string
(one meaning at every level), the per-iteration reading, and the count-in-search sentence: LEAN (review r10 FIXA-3,
SIM-2, SIM-6). The iterations of PCRE's parse: RULED (CF:932-933 for
the hits of `occurrences`, CF:950/CF:953-955 for every label; C36 RESOLVED). Zero iterations: §4.2. `occurs` as a library:
RULED (CF:682); its role as the FALLBACK to `count()`: LEAN (CF:823) with the budget rule RULED (CF:832); the name
`occurs`: RULED in use (CF:782). Duplicate labels by index: LEAN (CF:400); union type cited "ruled" (CF:350; §13 O3).
A duplicate label set twice in one match under `x: S`: §13 O35. The `occurs` condition argument is a parenthesised
literal: RULED (CF:732, C31). Whether `some`, `all`, `count` are built-ins or library names: lean library (prelude)
names (§8; C28 RESOLVED for `occurs.all`, the rest LEAN).

### 4.4 Computed labels are match-dependent bindings

**RULE.** A COMPUTED LABEL is a value of the match that is not a substring. It is written as a MATCH-DEPENDENT
BINDING: a binding that reads match labels IS a computed label of the pattern whose labels it reads (a macro whose
operand is that pattern, filled by `&`: the one input rule, §2.1):

    d  := days($b) - days($a)                 # a computed label of the pattern defining a and b
    close := pair & (d: between(-15, 15))
    wd := weekday_of($rest.year, $rest.month, $rest.day)
    rfc & (wname.index: ==wd)

A mapping must be a FUNCTION (one value per text it reads), many-to-one allowed, total on its pattern. Under the ONE
READING (§4.5) every label it reads has ONE span per match, so its input is single-valued by construction; the
requirement is on the mapping itself (a table giving two values for one text is refused). Rev 8's guard, "the
per-label ambiguity check", was the some-parse rule's and is gone with it (review r10 FIXB-7 (c)). Tabulated mappings report a constant from the accept state (§6.2); numerals by digit conversion. A computed
label's value is context-free (§11). Read it with `$` like any label (`$d`, `$wd`); the bare spellings in E-CAL and
E-RFC (`<=dim`, `==wd`) are §13 C13. Through a filter modifier a value condition becomes a pattern: `month_numbered(<3)` =
`/Jan(uary)?|Feb(ruary)?/` (§2.7).

**REASONING.** Lets non-numeric layouts (month names) comply with numeric fields; a weekday or a Luhn check is a
property without a capture group. A binding instead of a keyword keeps the grammar keyword-free (§5.1).

**STATUS.** Computed labels: LEAN (foundation per the LAYERING note, CF:522). Match-dependent binding as THE spelling:
LEAN (manager, CF:595; the concept RULED there), SUPERSEDES the `with` placeholder and predx's `with`. Which pattern a
binding attaches to when its labels occur in several: §13 O19.

### 4.5 Ambiguity: ONE READING (PCRE's)

**RULE.** A label is AMBIGUOUS when two accepting parses give it different spans (decidable). ONE READING
EVERYWHERE: a condition on ANY label, set once or in a loop, at every level, reads PCRE'S OWN PARSE: the parse PCRE2
gives the pattern matched against exactly the span the condition filters (anchored at both of its ends, as a set
position reads it; §0.3), each iteration's labels read within that iteration (§2.6).

MEMBERSHIP IS EXTENSIONAL; A CONDITION READS THE SPELLING (review r10 FIXB-1; a CONSEQUENCE of the ruled one
reading, told to the owner, not asked). PCRE's parse depends on how a pattern is WRITTEN (greedy or lazy, the order
of alternatives), not only on its language. So two spellings of one language, which admit the same strings under
`& | !` (§2.2), can answer differently under a condition on a label: `/(?<a>\d+)(?<b>\d+)/` and
`/(?<a>\d+?)(?<b>\d+)/` are one language with one set of labelled spans, yet on `123` PCRE gives a = `12` and a =
`1`, so `& (a: "1")` rejects `123` for the first and accepts it for the second; and with `A := /(?<l>a)a/`, `B :=
/(?<l>aa)/`, `(A | B) & (l: "a")` accepts `aa` while `(B | A) & (l: "a")` rejects it (§0.1 L60; libpcre2 10.46,
anchored at both ends). Under rev 8's some-parse rule a condition depended only on the labelled spans and these
agreed; the one reading trades that for one answer at every level. `label.ambiguous` names the label in every such
program (the label is ambiguous by definition when the spellings can disagree). Several conditions on one pattern read the SAME one parse, and a repeated label's iterations
and the hits of `occurrences` are that parse's (§4.3, §2.6).

THE CONDITION FILTERS THE PARSE; IT NEVER STEERS IT. A condition that fails on PCRE's parse fails, even when another
parse would pass. Worked example (set once): `P := /(?<a>\d+)(?<b>\d+)/` on `123`. PCRE's greedy `\d+` first takes
`123`, b then has nothing, so a gives back one digit: a = `12`, b = `3` (libpcre2 10.46 and Python's `re` agree;
`docs/dev/lanes/predspec9_reading.out`). So `P & (a: "12")` accepts `123` and `P & (a: "1")` does NOT, though the
parse a = `1`, b = `23` exists (rev 8's some-parse rule accepted both). `P & (a: <5) & (b: <5)` is false (both read a =
`12`; O33 RESOLVED). A constraint written INTO the pattern is a different pattern with its own parse
(`/(?<a>1)(?<b>\d+)/` accepts `123`): §0.1 L59. At `vm` the condition is checked on PCRE's match, never as a
rejecting callout that would send PCRE back into another parse (an oracle or a build that used one would compute a
some-parse answer).

IN A SEARCHED PROGRAM THE CONDITION SELECTS THE SPAN (review r10 FIXB-7 (d); "searched", not "search", rev 11,
review r12 CENSUS-10). "Never steers the parse" holds for a given
span. A SEARCHED program tries other spans (D196: the leftmost start, then the left operand's next end when a filter
rejects the preferred one), and each span has its own parse: `P & (a: "1")` searched in the subject `123` rejects the
span `123` (a = `12`) and reports `12` (whose parse gives a = `1`, b = `2`; libpcre2 and Python's `re.fullmatch`
agree), a span plain PCRE would not report. Likewise `P & (a: <5) & (b: <5)` searched in `123` reports `12` (§0.1
L34). The answer ON A VALUE (the whole span) is the rule above; what a searched program REPORTS follows from it span
by span.

WHAT A DEFAULT-LEVEL PROGRAM GETS, AND PAYS.
- An UNAMBIGUOUS label (every accepting parse gives it one span): PCRE's reading is every parse's, so the plain
  automaton (the product of the pattern's automaton and the condition's, as before) computes it, FREE. Every §12 case is here
  (rev 9 re-check, §12), and so is every label of a fixed-width or separator-delimited layout.
- An AMBIGUOUS label: the plain automaton computes "some parse passes", which is NOT PCRE's reading. The compiler
  builds PCRE's reading as AUTOMATON CODE where it can: for a pattern without backreferences, PCRE's choice among
  parses is a finite-state function of the span, so the strings whose PCRE parse puts the label in S form a regular
  set (this document's claim, LEAN, the one the measurement O57 exercises), and the default promise "linear, automaton
  code only" (§6.1) holds. The extra states over the some-parse automaton are its COST, shown by the cost report
  ([COST-EXPLAIN]); over the budget (§13 O39) the program is REFUSED with an error naming the higher level that
  computes the parse at run time (`captures` where its tagged automaton follows PCRE's priority, [ENG-TDFA]; else
  `vm`). This clause is the MANAGER'S LEAN (CF:943-944), not taken up in the owner's answer: LEAN. HOW MANY states:
  unmeasured, the OWED MEASUREMENT §13 O57 (its timing, before any build go: the record's, CF:955-957, LEAN).

AMBIGUITY IS THE AUTHOR'S TO VALIDATE (CF:950-951, CF:957-959). The `label.ambiguous` WARNING stays as the POINTER
to that validation: it names the label, shows a witness and two parses, says which one PCRE takes (the one the
program uses), shows the cost of computing it, and names the fix, an assertion on the witness (§5.6):

    "label `a` is ambiguous: on `123` the parses give a = `12` (PCRE's, used here) or a = `1`; validate the reading
     you intend, e.g. `@assert.some("123" & P & (a: "12"))`; PCRE's reading of `a` costs N states over the plain
     automaton"

LIBRARY PATTERNS. Rev 8's "library patterns are checked unambiguous at their labels" was the some-parse rule's guard
(it kept the two readings equal on library labels). Under one reading it becomes the library author's own validation,
like any author's: an ambiguous library label carries its assertions (the library's test vectors, §5.6, §8). The
`hit` of `occurrences` is ambiguous as a set by construction; its reading (leftmost, non-overlapping hits) IS its
definition, checked by its hand checks (§2.6). `label.ambiguous` fires only for ambiguity in the author's OWN pattern
text (an argument `/(?<a>\d+)(?<b>\d+)/` passed to `occurrences` still warns for a), never for ambiguity a library body
introduces and states (the gap of `occurrences` or `endsWith`): RULED ("2. agree", CF:964, to rev 9's O59 reading (A); §13
O59 RESOLVED).

**REASONING.** The owner: "I think it will help if our rx is consistent" (CF:950). One reading means a condition means
the same at the default level and at `vm`, set once and in a loop, inside `occurrences` and in a plain pattern; and what
a validation assertion checks is what the program does (under some-parse, `@assert.some("123" & P & (a: "1"))` and
the same with `"12"` would BOTH pass, so no assertion could validate a reading). Rev 8's argument ("the default level
is a promise; only some-parse keeps it") is WITHDRAWN: the promise is linear automaton code (§6.1), which PCRE's
reading keeps for backreference-free patterns; what the reading costs is states, measured (O57), and over the budget
the refusal names the level, never a silent route change (G2). For unambiguous labels nothing changes.

**STATUS.** ONE READING (a condition on any label, set once or in a loop, follows PCRE's own reading) and the
some-parse rule SUPERSEDED: RULED (CF:950, his words, answering the manager's note (a), CF:941-944; record
CF:953-955). The cost known: RULED (CF:949-950, "i'd like to know the cost of this"; the measurement: §13 O57); its timing,
"before any build go", is the record's (CF:956): LEAN (review r10 FIXB-5). The warning for the author's own text only:
RULED (CF:964). Membership extensional and conditions reading the spelling, and the search-mode span selection:
LEAN (this document's consequences of CF:953-955; review r10 FIXB-1, FIXB-7 (d)). Ambiguity the author's to validate, with an assertion: RULED (CF:950-951, `@check()` a
placeholder); `label.ambiguous` kept as the pointer: the record (CF:958-959). Built where it can with the cost shown,
refused on budget naming the higher level: LEAN (the manager's, CF:943-944). The no-steering statement, the regularity
claim, the library check restated and the warning's text: LEAN (this document). SUPERSEDES the 11-14 rule (CF:583,
predx Q2: "passes if SOME parse passes", "library patterns are checked unambiguous") and rev 8's §4.5; C36 and O33
RESOLVED; C11 (purity vs ambiguity) re-resolved by CF:953-955.

### 4.6 Value-vs-value relations, priced by class count

**RULE.** A comparison between two match values (`(b: >$a)`, `(day: padded(<=days_in($year, $month)))`,
`(wname.index: ==wd)`) is a RELATION, run the cheapest correct way. The values are passed to value macros as
parameters (`days_in($year, $month)`); an rx is never called with them (`leap` is an rx, which has no parameters:
`leap($year)` is the operand-as-argument error, §2.3; the leap test is `$year & leap`, inside the library's `days_in`). Its cost is the CLASS COUNT of the
earlier label(s): the number of classes the earlier labels enter the relation with (raw = |dom|; through a regular
twin = its class count). The manager's answer to "how practical" (CF:659-663; the owner has not replied, so the
tiers and numbers are LEAN and ILLUSTRATIVE): there is ONE MEASURED BUDGET for "too many classes" and for the
`count()` refusal, with no fixed thresholds in the spec (RULED, "3. agree", CF:977, to CF:974-975; §13 O39 RESOLVED);
the examples below say where today's cases fall: SMALL (calendar 24, state/ZIP ~50, weekday-vs-date 7, check
digits 10/11) = one automaton at the default level; LARGE (times of day 1,440: borderline; dates within 15 days:
~3.65M) = a default-level ERROR printing the count and the fixes, or a linear arithmetic check under `functions`;
UNBOUNDED (`b: >$a` over arbitrary `\d+`) = not regular, `functions` only. The compiler computes the count BEFORE
building; [COST-EXPLAIN] shows it.

**REASONING.** Turns "too large" into an explainable number; predicts E-CAL (24) vs E-NEAR (3.65M). Present it as
"a relation, run the cheapest correct way", never as "always one automaton".

**STATUS.** Value-vs-value comparisons, typed and class-count priced: RULED as a concept (CF:657-659: "VALUE-VS-VALUE
comparisons: AGREED, Frank asked how practical"). The SMALL / LARGE / UNBOUNDED tiers and their numbers are the
manager's ANSWER to that question (CF:659-663), which the owner never replied to: LEAN, illustrative; ONE measured
budget, no thresholds in the spec: RULED (CF:977; §13 O39 RESOLVED). A
count against another label's value is such a relation: LEAN (CF:682).

## 5. Macros, bindings, statements

### 5.1 Program shape, bindings, no keywords

**RULE.** A program = bindings, expressions, calls and `@` STATEMENTS, with ONE final expression (the program's
pattern); newlines are layout (whitespace and newlines are free between expression tokens: long logic goes in `:=`
definitions, literals stay short). A `(` or `[` after an expression is always a call or an index, so a statement
that STARTS with `(` or `[` (a record on the left, a final array) continues the line before it: §13 O51 (review r8
P6-13). A binding starts `name :=`. There is ONE kind of binding: `name := expression`,
and the name names whatever its expression is, an rx or a macro (CF:858); a definition head `m(p1, p2) :=` makes a
macro (§5.2); a record on the left (`(x, y) := ...`, §13 O54) is design only, out of phase 1 (§0.2). The bound kind
decides use in a hole: an rx inserts its set (a one-string set, a captured string or a quoted literal, as its literal
text; any other rx as a sub-pattern); a macro in a hole is the unapplied-macro error (§2.3; CF:362, "not usable as
`${x: digit}`"); a guard is written with `&` (§2.3, §11, C4: in rx text only with the rx-`&` switch ON). A binding
mentioning a match label is MATCH-DEPENDENT (a computed label, §4.4); otherwise PURE (compile time); the cost report
shows which.

NO ALPHABETIC OPERATORS OR STATEMENT KEYWORDS: a word is always a NAME (function, label, binding). There is no
`with`, `check`, `in`, `export`, `import ... as`: imports and exports are function calls (§7), assertions are
library calls (§5.6), computed values are bindings (§4.4). Enumerated option values are STRINGS, not bare words
(`gaps = "allow"`, `order = "desc"`).

BARE STATEMENTS: only `@` forms (compile-time EFFECTS, §0.3, §5.6, §7.1; not values and not macros) may stand alone; a bare rx anywhere but
the final expression is an error ("unused pattern: bind it or make it the result"); a bare statement without `@` is
an error (it catches the unbound pattern). Macros cannot take `@`; effects cannot drop it (purity visible and checked
syntactically). `@` exists only in the expression language.

Names: symbols come only from the pattern (labels), from `:=` (bindings) or from a module (member access). The
BUILT-INS are a CLOSED list, reserved in CALL position only: `import`, `enumerate`, `pattern`, `param`,
`file_text`, `records`, `eval`; and two EFFECT built-ins, reserved after `@` only: `@warn` (§7.1) and `@export` (§7),
which act on the program or file itself and so are not imported (review r10 CENSUS-7; LEAN). `@assert` comes from a
module (`assert := import("assert")`, §5.6); the per-entry assertion spelling `@each(...)` is OPEN (§13 O22). Every other name in the examples (`between`, `startsWith`, `contains`, `padded`,
`days`, `weekday_of`, `within`, `list_of`, `join`, `each`, `occurrences`, ...) is a library name; `some`, `all` and
`count` are library (prelude) names too (LEAN, review RUL-13; §4.3, §8). Rev 9's reserved scope-supplied labels `$&`
and `$_` had no stated meaning and no case: the reservation is DROPPED until a case needs one (D77; review r10
CENSUS-8; LEAN). An undeclared name that is not a label is an error with a suggestion; a binding hiding a label WARNS (`$x` still
reaches the label).

**REASONING.** Frank: "no alpha operators ... with, check, in ... don't want to go into new grammar lightly". The
grammar shrinks to bindings, expressions, calls and `@` statements; the `@` mark makes compile-time effects visible.
A bare enum word (`allow`, `desc`) would be a keyword in argument position (review OWN-7).

**STATUS.** Block shape: RULED (CF:68). One kind of binding, naming whatever its expression is: RULED (CF:858,
accepted at CF:851; rev 6 still said LEAN (CF:115), review r8 RUL-13). The macro-in-a-hole error: RULED (CF:362). No alphabetic keywords: RULED (CF:595). `@` statements,
the unused-pattern and bare-statement errors: LEAN (manager, CF:619, on Frank's prefix suggestion). String enum values
and the closed built-in list: LEAN (review OWN-7); the effect built-ins and the dropped `$&`/`$_`: LEAN (review r10
CENSUS-7, CENSUS-8). Define-before-use: §13 C12. Bare label names as values: §13 C13.
How a program selects `functions`/`captures`/`vm`/`eval` (§6.1): §13 O31.

### 5.2 Macros and parameters

**RULE.** `m(p1, p2) := body` makes a macro. THE OPERAND IS NEVER AN ARGUMENT (it arrives via `&` or `label:`, §2.3).
A CALL IS THE MACRO APPLIED TO ONE RECORD (CF:866 (a)): the parentheses of `f(...)` are a record (§5.4) laid against
the macro's parameters, its positional entries by position, its labelled entries (`=`) by parameter name; a record
inside that record would be a record used as a value, an ERROR (`f((1, 2))`, §0.1 L45). An entry that is itself a
condition (`occurs.exactly(1, (name: S))`) passes a MACRO, not a record (§4.1). Every argument is a PARAMETER:
POSITIONAL arguments are the REQUIRED parameters in declared order (`between(1, 12)`,
`padded(S)`, `occurs.exactly(1, cond)`, `pair(p) := /${p},${p}/`), KEYWORD arguments are OPTIONAL SETTINGS with
defaults (`join(a, sep = ".")`), and ANY parameter may also be passed by name (`between(low = 1, high = 12)`): one
rule for every macro. A pattern is not a macro and has no parameters: calling one is a compile error ("write
`isodate & (year: ...)`", §4.1). A PARAMETERISED pattern is a macro: `date_in(years) := isodate & (year: years)`.
Every labelled pattern keeps its labels as fields, reached by a condition literal (`isodate & (year: 2000)`; fully
constrained = formatting). A SECTION is a macro (rev 6 said "operators are macros", which made the one input rule
circular for `&` itself and licensed an operator as an argument; review r8 P6-8 (d)): `(& B)` is a macro with only
its operand open (the operand on the left; CF:860), `(& M)` = M when M already has only its operand open (§2.1),
sections compose (`(& isodate & (year: 2024))`, `(& !B)`), and a
section is how a filter is passed where a macro is wanted (`each((& isodate), dates)`, §5.3). Sections START with
`&` only; sections of other operators come on need (C33). NO PARTIAL APPLICATION in phase 1: a macro call binds
every required parameter or is a compile error naming the missing one (`between(low = 1)` = "missing `high`"); a
section is the one way to leave a hole. The DESIGN keeps currying (a macro with some parameters bound is a macro)
for after phase 1 (C34; §0.2). Macros expand at compile time, inlined per use; cost is per USE. No lambda until an
example needs one (D77).

TYPED PARAMETERS ARE OUT OF PHASE 1 (the owner: "yes keep out of phase 1. I like the idea of types but they need
more thinking", CF:889). In phase 1 a definition head declares NAMES and DEFAULTS only: a bare name is a REQUIRED
parameter, `name = default` declares an OPTIONAL SETTING and its default (`occurrences(x, min = 0) :=`: x required, `min`
optional with 0; this is where §5.2's "keyword arguments are optional settings with defaults" get their defaults;
review r10 CENSUS-4, LEAN); a `:` in a head is an ERROR ("a parameter takes no constraint in phase 1; constrain where it is used", §0.1 L49), so `:` has ONE behaviour
in phase 1: it NARROWS, in a condition (`isodate & (year: <2000)` silently drops `5`, which `/\d{4}/` cannot hold).
At NARROWING SITES (condition literals, an `&` whose operands come from definitions) an empty intersection from pure
parts is an ERROR; a dead branch WARNS (`dead.branch`); nothing when emptiness is match- or parameter-dependent;
NEVER inside an `@assert.*` argument, whose emptiness is the assertion's own question (§5.6). In the DESIGN (after
phase 1) rev 7's typed parameters stay as text for the owner's "more thinking": `m(x: T)` with a containment CHECK on
the positional argument (an error showing a dropped witness), which would give `:` a second behaviour, and `m(p:
pure)` (a property after `:`, with the fix `pattern($x)`, the built-in giving a label's static pattern); none is
decided (§13 O48).

**STATUS.** Macro bindings: RULED (CF:124). `=` sets a parameter vs `:` filters, a condition literal narrows: RULED
(CF:706). Patterns take no arguments, a parameterised pattern is a macro: RULED (CF:744). The operand (CF:749's
"subject") is never an argument, positional = required parameters, keywords = optional settings, any parameter by name, operator sections,
no lambda: RULED (CF:749; C20/C30 RESOLVED). Sections start with `&` only: RULED (CF:753, C33). No partial application
in phase 1: RULED (CF:753, C34); the design keeps currying for later: RULED (CF:804, which says C34 does not supersede
CF:308). A call = the macro applied to one record: RULED (CF:866 (a)); the nested-record error and a condition
argument passing the macro: LEAN (this document; §13 O45). Typed parameters OUT of phase 1: RULED (CF:889, his
words); the head error that says so: LEAN (this document); typed-parameter containment and `pure` in the design: not
decided ("they need more thinking", CF:889; §13 O48). The empty-intersection error scoped to narrowing sites: LEAN
(review RUL-6). Defaults written `name = default` in a head: LEAN (review r10 CENSUS-4). `pattern()`: LEAN. A section is a macro, `(& M)` = M: LEAN (review r8
P6-8). Overloading: LEAN, NOT phase one (CF:163). `(x & isodate).year`: §13 C29.

### 5.3 Structural macros: `each`, `each_group`, `where`, `join`

**RULE.** Macros are passable values, FENCED: compile-time only, over finite SPELLED arrays (§3.4; never over a
repeated label's iterations, §4.3), structural operators only. `each(f, A)` applies f per entry, keeps labels and
order, returns an rx read through the array interface (the structural per-entry map, not
an application spelling, §2.3). f is a MACRO whose parameters the entry fills (`each(triple, ...)`, `each(capture, a)`),
or a FILTER passed as an operator SECTION: `each((& isodate), dates)` maps the filter over the entries, and sections
compose (`(& isodate & (year: 2024))`, ruled 2026-11-15, §5.2); a condition, already a macro with only its operand
open, may be passed as it is (`each((a: d), x)` = `each((& (a: d)), x)`, §2.1); over several arrays it ZIPS by position (unequal lengths = error naming both counts).
`each_group` zips BY LABEL; `where_group` and `each_group` return an rx (an array in group order, §2.1). `join(a, sep
= s)` concatenates the entries of a SPELLED array in their written order (a structural tool, §3.4); `sep` is a set;
joined PARTS stay navigable by their labels in the map interface (`(c.A: <200)`, `c.A`), free when unread. A join is
ONE alternative, so its array interface has one entry and `c[1]` is c itself (rev 6's `c[1]` "first part" read the array
bracket as a part index; review r8 CENSUS-13); an unlabelled part is reached through the binding it came from. Family: in-order fixed = `join`; in-order repeated =
`list_of(X, sep = ...)`; any-order fixed = `&` of labelled parts (JSONL); candidate sugar `any_order(a, sep = ...)`.
Caller-visible captures are a library macro: `capture(x) := /(?<${x.label}>${x})/` (the hole in a GROUP-NAME
position, a typed syntax position, §11, §5.4 `${ }` row), `join(each(capture, a), sep = ".")`, exported like any
binding (§7).

**Ordinal parameter.** The iteration ORDINAL (dense, starts at `start =`, default 1), `x.index` (original position)
and `x.label` (original name) differ once an array is sliced. The ordinal is passed BY NAME (review r10 CENSUS-15, the
manager's pick; LEAN): the macro declares a parameter for it and the call names that parameter with the setting
`ordinal = "i"` (`capture(x, i) := /(?<f_${i}>${x})/`, `each(capture, a, ordinal = "i")`); without the setting no
ordinal is passed. So a macro's POSITIONAL slots are always filled by the zipped entries (`pair(x, y) :=
/${x}=${y}/`, `each(pair, A, B)` = `pair(A[k], B[k])` for each k), and the call record says which parameter takes
the ordinal; macro application keeps its one meaning (the owner, CF:850-851). Rev 9's "the second argument when the
macro takes one" gave a two-parameter macro's slot 2 two claimants. The setting that was `index =` is `start =`
(review r10 CENSUS-14: `index` is a reserved metadata field, §5.4 `.` row).

**STATUS.** LEAN (CF:278 join, CF:289 compose instead of an option, CF:300 each's bindings). Mapping a filter by a
section: RULED (CF:749). Ordinal default 1: per the 1-based ruling; passed by name, the `start =` and `ordinal =`
settings: LEAN (review r10 CENSUS-14, CENSUS-15). Per-field constraints carrying into joined labels:
§13 O5. The rev 0 `export capture(x) := ...` keyword form is superseded by `@export` (§7).

### 5.4 The marks: THE grammar summary and THE MARK TABLE

This is the ONE place the marks are defined; every other section points here. It is G0b's MARK TABLE: each mark,
its ONE meaning IN EACH POSITION it may take (a bracket's position decides which of its rows applies: `( )` has four
rows, `[ ]` two readings; review r10 CENSUS-17), and the §12 case that needs it ("no case" marks a mark carried
without one; the TWO-WAY CENSUS in §12 gives the reason). Inside `/.../` none of this applies: rx text has PCRE's
meaning (`\d{1,3}`, `(?<y>...)`, `[^,]`), with exactly TWO stated exceptions, §11 THE MARKS INSIDE `/.../`: `${`
always opens a hole (`/${p},${p}/`) in a pattern position (in a class or `\Q...\E` it is written `$\{`), and `&` is
the intersection only when the rx-`&` switch is ON, and then exactly in the positions where `|` means alternation
(PCRE's own constructs, `(?&name)` included, keep their meaning: RULED, CF:1041-1046 on main, rev 13). Self-recursion is plain PCRE inside the literal
(§7), so there is no third (rev 11, review r12 CENSUS-2).

THE BRACKETS AND THEIR MARKS (`,` `( )` `[ ]` `=` `:`):

| mark | where it may appear | what it means | §12 case |
|---|---|---|---|
| `,` | only between ENTRIES inside `[ ]` or `( )` (a call's parentheses are a `( )`) | "next entry"; it never carries logic (no AND, no OR, no dimension) | every case but E-LUHN, E-DEPTH (its commas are inside rx text) and E-CTX (rev 11, review r12 CENSUS-7) |
| `[ e1, e2, ... ]` | value position; and as the index bracket `X[...]` | ARRAY (the written form of the array interface: it WRITES AN RX entry by entry and creates no array value, CF:890-891): ORDERED ENTRIES, each entry ONE entry (like a group or a hole, §3.3: `[x, /d/]` has 2 entries whatever x holds, §0.1 L48). Under `& \| !` and in the filter role (extensional, §3.4): ANY ONE entry (of rx: an alternation; of macros: a macro, a list of filters, §3.5; mixed: error). Under structural tools (indexing, `each`, `join`, the entry count, §3.4): the entries in their written order. One meaning, two readings of it, as for every rx (§3.4). `X[...]` selects positions, any one of those listed (`X[1, 3, 5]` = `X[1\|3\|5]`, if the multi-index is adopted, C5); BY POSITION (§3.2 tool 1, §0.1 L64): in value position the ENTRIES of the rx on the left (`alt.x[1]`), in a match position (under `$`, a path on the left of `:`) the ITERATIONS of the label (`$m.hit[2]`, `(x[2]: S)`), and there a CONDITION in the bracket keeps the iterations whose own labels meet it (`$m.hit[(g: "x")]`; rev 11, review r12 CENSUS-1, LEAN) | E-WEEKDAY, E-IPV4, E-RFC, E-NEAR, E-SEP, E-HTTP (`join` inputs); E-RFC (alternations of names) |
| `( e1, e2, ... )` | ONLY laid against something with fields: (a) a CALL's argument list, against the macro's parameters (also a definition head `m(p1, p2) :=`, which declares them); (b) a CONDITION, against a pattern's labels; (c) the LEFT of `:=`, against a result's groups (design only; out of phase 1, §0.2) | RECORD: ALL entries together, positional or labelled. NEVER A VALUE: it cannot be bound, stored or returned. The written form of the MAP interface (§3.1); one-way | every call; every condition |
| `( label: S, ... )` in VALUE position (an argument, an array entry, the right of `:=`) | where a value may stand | a CONDITION, i.e. a MACRO (CF:858), NOT a record: the record is its written body, laid against the operand's labels when `&` fills it (position (b)); no record is bound or passed (§4.1; §13 O45). Any other record in value position is an error (`(x = /a/, y = /b/)`: "a record is not a value; for any one of the entries write `[ ... ]`", §0.1 L43) | E-HTTP (`occurs.exactly(1, (name: ...))`, `count((name: ...))`) |
| `(& f)` | value position | a SECTION: the macro with only its operand open (§5.2); `(& M)` = M for M with only its operand open (§2.1) | no case (prose only, §5.2, §5.3) |
| `( e )` | value position, no comma, no label mark | GROUPING (precedence only); a one-entry record exists only in positions (a)-(c) (§13 O41) | no case (§12's parentheses are calls and conditions) |
| `=` | `name = e` as an entry of `[ ]`, of a call record, or of a definition head | gives the entry its NAME: a LABEL (group name) in an array (`[year = /\d{4}/, ...]`), a PARAMETER in a call (`sep = "."`), and in a HEAD an OPTIONAL SETTING with its DEFAULT (`occurrences(x, min = 0) :=`, §5.2; review r10 CENSUS-4) | E-WEEKDAY, E-RFC, E-NEAR, E-SEP, E-HTTP; `sep =`, `of =`, `sha256 =`; `occurrences`'s `min =` (an optional setting, §2.6): no case |
| `:` | `path: S` as an entry of a condition record: a FIELD PATH of the operand's map interface, the `.` row's one meaning (a label `d.year`, metadata `wname.index`, an iteration index `x[2]`; review r10 CENSUS-9) | NARROWS a field that EXISTS by a constraint set: ONE behaviour in phase 1. Elsewhere an error (`P & x: S`, `[x: S]`, `f(x: S)` in a call, and in phase 1 `m(x: T) :=` in a definition head: typed parameters are OUT, CF:889; §5.2, §0.1 L49, §13 O48) | E-WEEKDAY, E-CAL, E-RFC, E-NEAR, E-FILE, E-HTTP, E-CTX (conditions) |

ENTRY EXTENT: an entry runs to the next `,` or the closing bracket; inside it `&` and `|` bind tighter than `:` and
`=`, so `(x: <200 | >900)` and `[month = /\d\d/ & padded(between(1, 12)), ...]` each hold ONE entry (§4.1, C22).

THE OTHER MARKS:

| mark | where it may appear | its one meaning | §12 case |
|---|---|---|---|
| `&` | between two expressions; in rx text ONLY with the rx-`&` switch ON, then exactly where `\|` would mean alternation (PCRE's own constructs keep their meaning, `(?&name)` included; a literal `&` is `\&` or `[&]`: RULED, CF:1041-1046 on main, rev 13); BOTH operands are filter roles matched whole on one span, an anchor in an operand drawing `anchor.operand` (RULED, CF:1054-1062 on main) (§11; CF:981-984); in rx text it takes the whole concatenation on each side (§0.1 L67) | fills the operand slot: rx & rx = intersection, rx & macro = the macro applied to the rx, macro & macro = pointwise (§2.1, §2.2) | every case but E-SEP, E-DEPTH |
| `\|` | between two expressions | ANY ONE: union of rx, concatenation of entries (§3.3), pointwise on macros; rx \| macro is an error (§2.1) | E-FILE, E-DEPTH |
| prefix `!` | before an expression (expression language only, §2.2) | the complement in the filter role: a macro with its operand open | E-FILE |
| `<` `<=` `>` `>=` `==` | prefix, before ONE atom | a COMPARISON SET (a full rx, §2.4) | E-CAL (`<=`), E-RFC (`==`), E-FILE (`<=`, `>`) |
| `+` `-` `*` `%` | between numbers | arithmetic on numerals (§2.5) | E-NEAR, E-DEPTH (`-`); `+`, `*`, `%`: no case (the TWO-WAY CENSUS gives the reason; `+` listed in rev 11, review r12 CENSUS-7) |
| `:=` | statement start (a name, a definition head, or a record on the left, design only) | binds a name to an rx or a macro (§5.1) | every case |
| `.` | after an expression or a label path | a FIELD of the MAP INTERFACE of the thing on the left (§3.2 tool 4), its ONE meaning (CF:898-899, agreed CF:892): a label (`d.year`, `rest.year`), a module member (`json.row`, §7), metadata (`.index`, `.label`, reserved fields) and a `$` path are instances. A user label named `index` or `label` is an ERROR naming the reserved field (rev 9: the manager's call, LEAN; §13 O31) | E-RFC (`.index`, `$rest.year`), E-JSONL and others (`json.row`), E-FILE (`r.word`) |
| `$` | before a label PATH | the VALUE(S) of the whole label path in this match, read through the array interface: ONE ENTRY PER ITERATION in match order (a set-once label: one entry, so a one-string set; unset: no entry). For a GROUP label the value is its CAPTURED STRING (`$year`); for METADATA (`$mname.index`) or a COMPUTED LABEL (`$d`, `$wd`, §4.4) it is that value, a numeral string, not captured text (rev 11, review r12 CENSUS-11). An entry is a one-string rx with NO labels: a selection of iterations is written in the path, before `$` (`$m.hit[(g: "x")]`), never as a condition laid against `$`'s entries (review r12 CENSUS-1). The path is read whole: `$a.b.c` reads the path `a.b.c` (the parenthesised `$(a.b.c)` is notation here, not a program), so `$mname.index` is the index of mname's matched entry (11 for `Nov`), never the field `index` of `$mname` (review r8 P6-6). On a repeated label it needs captures, the `captures` level: for ONE iteration (`$m.hit[2]`, `$m.hit[2].g`) RULED BY ACCEPTANCE (CF:977, to CF:972-973's "reading ONE hit"); for every iteration (`$m.hit`) or a selection: LEAN (review r12 CENSUS-8; §4.3); one meaning at every level (review r10 FIXA-3, CENSUS-1; LEAN) | E-WEEKDAY, E-CAL, E-RFC, E-NEAR |
| `${ }` | inside rx text, ALWAYS (in the opt-in, whatever the rx-`&` switch; §11) | a HOLE: the text the expression inside denotes, inserted where it stands. In an ATOM position (the usual one) it inserts an rx's set as ONE entry (§3.3); in a TYPED SYNTAX POSITION it supplies that position's value from a finite compile-time set: a quantifier bound (`{${min},}`, `\d{${n}}`), a class range end (`[${a}-${b}]`), a GROUP NAME (`(?<${x.label}>...)`, `(?<f_${i}>...)`: a one-string set that is a valid name) (§11; review r10 CENSUS-3). A macro in it is the unapplied-macro error (§2.3) | E-JSONL, E-DEPTH, E-HTTP (`/\A${block}\z/`), E-CTX (`/a${num}/`); E-IPV4 (prose); typed positions: §2.6, §5.3 (no case) (rev 11, review r12 CENSUS-7) |
| `/.../` | value position | an rx literal with PCRE's meaning (§11) | every case but E-CAL (its `isodate` is a comment since rev 10; review r12 CENSUS-7) |
| `@` | statement start | marks an EFFECT (§5.1): a module's effect (`@assert.some`) or one of the two effect built-ins `@warn`, `@export` (§5.1) | E-IPV4, E-CAL, E-CTX (`@assert.none`; review r12 CENSUS-7) |
| `#` | outside rx text, to the end of the line | a COMMENT (layout; inside `/.../` `#` is PCRE's: a literal, or a comment only in extended mode, §11; review r10 CENSUS-17) | ten of the twelve §12 blocks |
| `"..."` and numerals | value position | a one-string rx (§2.1); a numeral may carry a sign (`between(-15, 15)`, §2.4) | every case but E-SEP (review r12 CENSUS-7) |

**STATUS.** The comma as "next entry", `[ ]` any one, `( )` all together, `=` labels, `:` constrains an existing label:
RULED (CF:863, on the acceptance alone except the comma, CF:850). The record never a value: RULED (CF:851-852, his
words); its three positions: RULED (CF:866, on the acceptance; the left of `:=` also CF:852). Spellings:
placeholders (D193 add. 4). The table's placement of definition heads under (a), the `( e )` grouping rule, the entry
extent restated for `=`, and the condition row: LEAN (this document; §13 O41, O43, O44, O45). `[ ]`'s one meaning
stated with its two readings, and each entry ONE entry: LEAN (review r8 P6-2, P6-14; §3.4 RULED, CF:328, CF:385).
`$` over a whole path: LEAN (review r8 P6-6). The `.` row's one meaning: RULED by acceptance ("agree", CF:892, to
the lean recorded at CF:898-899); the metadata collision an ERROR: the manager's call (LEAN, §13 O31). The marks
inside `/.../` (`${` always, `&` by the switch): RULED (CF:981-984 for `&`; `${` the stated exception, LEAN, review
r10 CENSUS-2); which `&` is the mark under ON and the literal `\&`/`[&]`: RULED (CF:1041-1046 on main, rev 13). The rev 10 rows and wordings (one meaning per position, `[n]` by position, `$` per iteration, the
`${ }` positions, the head `=`, the `:` field path, `#`): LEAN (review r10). `:` narrows only, the head use out of phase 1:
RULED (CF:889, his words; the record line CF:895-896 states the consequence for `:`). Rev 8 REMOVES two marks: `~`
(search inside a value) and `!~` (its negated test) are WITHDRAWN (CF:909, accepted at CF:905): search is the library
transform `occurrences(rx)` and the negated test `!contains(rx)` (§2.6), so the inventory loses two operators and gains
no mark. The other marks restate the sections cited; `@`: LEAN (manager, CF:619). SUPERSEDES rev 5's "`,` separates conditions in a
condition literal and arguments in a call" and "`=` BINDS a label inside a map/list literal" (the map literal is
withdrawn, §3.1).

### 5.5 `enumerate`

**RULE.** `enumerate(rx)` = an rx whose ARRAY interface lists a FINITE rx's strings one per entry, in PCRE PRIORITY ORDER (leftmost alternative,
greedy before lazy); the members of a CLASS, which has no priority among them, come in CODEPOINT ORDER (so
`enumerate(/[-\/.]/)` = `enumerate(/[.\/-]/)` = `["-", ".", "/"]`); so re-joining preserves which match is reported
(hence a built-in, not a library). Its argument is a compile-time SET POSITION: an edge assertion in it is the
edge-assertion error (§11; `enumerate(/(?<=a)[bc]/)`). A BUDGET bounds it: an infinite or over-budget rx is a
compile error giving the count. Uses: finite backreferences made regular (`each(date_sep, enumerate(/[-\/.]/))`,
`!contains(each(triple, enumerate(/[\x21-\x7E]/)))`), matched delimiters (`each(q, enumerate(/["']/))`), which option
matched via `.index` at the default level, per-entry library assertions (spelling OPEN, §13 O22; rev 9's `@each(...)`
reuses the name of the structural macro `each`, so the lean is a member of the assert module, `@assert.each(...)`;
review r10 CENSUS-16).

**REASONING.** A class is ONE alternative, so no array tool reached its members; finiteness plus a budget keeps G4.
Codepoint order is extensional: two spellings of one class give one array (G0).

**STATUS.** RULED as design (CF:648: "I love it. Enumerate go." = design adoption; #6 unscheduled). Codepoint order for
class members: LEAN (review OWN-10). Edge assertions refused: RULED (CF:713, CF:761 (3)). Finite-group backreferences
as a GENERAL engine rule are not #6: [BACKREF-FINITE] (§11, §14); the levels of the three same-text spellings: §13
O34.

### 5.6 Assertions (compile-time checks)

**RULE.** Compile-time assertions are LIBRARY effect calls over rx, written as `@` statements; no boolean type, no
keyword. Membership is `&` (`"2024" & leap` is {"2024"} or empty); inclusion is `A & !B` empty:

    assert := import("assert")
    @assert.some("2024" & leap)
    @assert.none("1900" & leap)
    @assert.none(octet & !/\d{1,3}/)          # every octet has 1-3 digits
    @assert.same(old, new)                     # library: both differences empty
    @assert.some(slow_errors)                  # not dead

`assert.some(X)` / `assert.none(X)` and the group questions `some(c)` / `occurs.none(c)` (§4.3) share a word and
one sense, "at least one member" / "no member", over different things: the assertion over the STRINGS of a set X at
compile time, the group question over the ITERATIONS of a label in a match; the module prefix tells them apart
(review r10 CENSUS-16; LEAN).

An assertion's argument is a compile-time SET POSITION: it is decided on strings, and an edge assertion in it is
the edge-assertion error (§11; `@assert.none("5" & /(?<=\$)\d+/)` is refused, not existential over contexts). No
assertion states SEARCH behaviour (that `256.1.1.1` is searched as `56.1.1.1`, §12.3). The implicit
empty-intersection error never applies inside an assertion's argument (§5.2). Anonymous assertions report line +
text; NAMED assertions give named failures (§13 C18 for their spelling). An assertion the compiler cannot decide
reports "can't prove: not regular" beyond the default level. Libraries carry their standard's test vectors as
assertions run at import.

VALIDATING AN AMBIGUOUS LABEL'S READING (rev 9; the owner: "If someone is writing ambiguous rx they need to think about
what that means and validate it with @check()", CF:950-951, his `@check()` a placeholder for this library). The
EXISTING forms express "on this witness, label a is `12`", because a condition reads PCRE's parse (§4.5): the witness
narrowed by the pattern and a condition on the label is non-empty exactly when PCRE's parse of the witness gives the
label that value.

    P := /(?<a>\d+)(?<b>\d+)/
    @assert.some("123" & P & (a: "12"))          # the intended reading: a takes all but the last digit
    @assert.none("123" & P & (a: "1"))           # and not the other parse

Both pass (PCRE's parse of `123` is a = `12`, b = `3`, §4.5). If the author meant a = `1`, the first fails at compile
time with its line and text, and the fix is in the pattern (`/(?<a>\d)(?<b>\d+)/` or a lazy `\d+?`), not in the
condition. NO NEW FORM IS NEEDED: under rev 8's some-parse rule both assertions above would pass whatever the author
meant, so no assertion could validate a reading; the one reading is what makes the existing library sufficient. A
shorter spelling for "the parse of this witness" (`@assert.reading(P, "123", (a: "12"))`-shaped) is not proposed
(D77); named assertions for clearer failures are §13 C18.

**REASONING.** Language equality and inclusion are decidable (D196 add. 2's never-match/XOR fact), so the library
test rule ("tested against the standard's own vectors") becomes executable (predx S8, §8.3 item 3).

**STATUS.** Concept (compile-time assertions): RULED (CF:595, Q9). Library form `assert.some` etc.: RULED (CF:608,
Frank's own `assert := import("assert")`, `assert.some("2024" & leap)`); `@` prefix: LEAN (manager, CF:619),
SUPERSEDES `check A == B` and the `assert_some(...)` built-ins. Set position: RULED (CF:713). The empty-intersection
exemption: LEAN (review RUL-6). A library SEARCH assertion (review Q1X-5): not adopted, §13 O36. Validation of an
ambiguous label's reading by an assertion: RULED (CF:950-951; the assertion library as its home: the record,
CF:958); that the existing forms suffice, and the example: LEAN (this document).

## 6. Capability levels and the reporting axis

### 6.1 Levels

**RULE.** Inside the predicate opt-in, the DEFAULT level promises "LINEAR, AUTOMATON CODE ONLY": linear time, no
backtracking, hostile-input safe, self-contained output. It does NOT promise one DFA pass: a relax-then-verify split
whose verify is itself an automaton over the candidate span ([PRED-SPLIT]) is inside it, and so are computations on
run-time INPUTS only (`param(...)`, §0.3; once per match, over a fixed-size value; comparisons against inputs compile to
parametric automata). Anything beyond is a compile error naming the construct and the option that allows it ("the
relation `d` has ~3.65M classes: add `functions`, or make the anchor a constant"), the "requires module 'X'" shape.
Opt-ins are INDEPENDENT switches, not a ladder:
- `functions`: blessed callouts on CAPTURED text (still linear, self-contained);
- `captures`: named-group SPANS in the output (§6.2);
- `vm`: full PCRE semantics (backrefs, recursion, non-DFA lookbehind);
- `eval`: runtime patterns (budgeted; links a runtime).
At the default level a REGULAR TWIN (luhn, weekday, days_in) MUST take its automaton form; too large = compile error
with the size (§4.6), never a silent switch. The planner may choose an automaton split silently (it changes only
speed); it may NOT change level silently. A one-literal program is today's PCRE pattern on today's engines (G3,
§11). The cost tool's first output is the level a program needed and why.

THE ONE READING AT THE DEFAULT LEVEL (rev 9, §4.5). Every level reads PCRE's parse; the levels differ only in what
they compute it WITH. For an unambiguous label the default level computes it free (the plain automaton); for an
ambiguous label it builds PCRE's reading as automaton code (backreference-free patterns: still linear, so inside the
promise) with the extra states shown, and over the budget the program is a compile error naming the level that
computes the parse at run time, never a silent fall-back to "some parse" (rev 8 kept the promise by changing the
answer; rev 9 keeps the answer and prices the promise). The building and the refusal: LEAN (manager, CF:943-944); the
size: OWED (§13 O57).

**`&` AT `vm` WITH A NON-REGULAR OPERAND.** The regular operands build the CANDIDATE automaton; the VM verifies the
non-regular operand on each candidate span; the reported span follows D196 ([PRED-SPLIT]). CAVEAT (CF:63): D196's
left operand chooses the reported end, so when the verify rejects the preferred end the next end must be tried; for
that match the verify falls back to the VM.

**REASONING.** An RE2-class promise with far more expressive power (G2). Independence: a user may want
linear-time callouts without backtracking, or spans without callouts. Under the ruled string-set model (§11) no
set-position use carries context state, so G2 needs no regular-lookaround lowering for conditions (review Q1X-8).

**STATUS.** Levels: LEAN (CF:472, "Lean ADOPT"). The promise "linear, automaton code only" (automaton split and
run-time-input-only computations at default; `functions` = functions over captured text): RULED (CF:583, predx Q5;
resolves C14 and O9). `&` at `vm`: RULED (CF:657, "AGREED"; the note's "the spec must state it" is the manager's
text, not a quote); the next-end caveat: LEAN (CF:63, the [PRED-SPLIT] filing). Performance-trade rules: RULED
2026-11-12. `functions` presupposes DFA captures ([ENG-TDFA]): §13 O6. How a program selects a level: §13 O31.

### 6.2 What a default-level program reports

**RULE.** Three outputs, three costs: (a) the match SPAN: default, free; (b) ACCEPT-CLASS values (`.index`,
computed labels with finite class counts: weekday, region, card brand, per-group classes combined at output):
default, free (a lookup on the accept state); (c) named-group SPANS (`$year` as text): the `captures` opt-in (a
tagged DFA, [ENG-TDFA], or the VM). The default output is span + accept-class values.

**STATUS.** RULED (CF:583, predx Q11).

## 7. The compile-time boundary, modules, traps

**RULE.**
- Structural evaluation is TOTAL over finite things and TERMINATES. Recursion through a PARAMETERIZED definition
  is admitted only when ONE integer parameter is a literal at every call after expansion and STRICTLY DECREASES at
  every recursive call, with a literal base case (`value_depth(0) := json.scalar`, §12.11: a form not yet in the
grammar, a literal in a head and two `:=` for one name, §13 O21; review r10 CENSUS-5); any other cycle is
  refused at load (the error names the cycle). A parameterless pattern binding recurses AS IN PCRE, inside its OWN
  literal through that literal's own named group (`balanced := /(?<p>\((?:[^()]|(?&p))*\))/`, matched at run time,
  needs `vm`; libpcre2 10.46 finds `(a(b))` in `x(a(b))y`): plain PCRE text, no crossing from rx text to the expression
  language (§11; CF:113's lean "a pattern binding may call itself via `(?&name)` inside its own literal" is met by the
  literal's own group). Rev 10 wrote `(?&balanced)`, naming the BINDING, which PCRE rejects as written ("reference to
  non-existent subpattern"): a third non-PCRE reading of rx text (review r12 CENSUS-2; rev 11's respelling is the
  manager's pick, LEAN). Labels inside recursion refused at first (a condition on `p` is refused; the group itself
  is the call's target).
- `file_text(path, sha256 = ...)` = the whole file as one compile-time string; `records(text, rx)` = an rx whose
  ARRAY interface (a spelled array, §3.4) has one ITEM per compile-time match of the ITEM RX over a compile-time string (the names
  `records`/"record rx" are placeholders colliding with RECORD, §0.3, §13 O44). The item rx is SEARCHED in the text
  (in context, like a final pattern: its `^`/`$` read the file text); each ITEM is the item rx narrowed to that one
  match, a one-string rx (context-free, §11) whose labels stay reachable by the map interface (`r.word`, E-FILE; rev 6
  said "named groups make entries maps" and "each ENTRY is a plain string", review r8 RUL-12). The item rx's matches
  must TILE the text (every byte in a record or a declared gap),
  else a compile error naming the untiled byte range ("bytes 0-4 (`foo\r\n`) belong to no record");
  `records(text, rx, gaps = "allow")` opts out. How an item rx declares its separator bytes: §13 O20 (until it is
  settled, a multi-line file fails tiling on its `\n` terminators). `file_literals(p)` is library sugar over
  `records` with a NAMED item rx (no hidden default). Item rx restricted to the DFA-able subset; `records` needs
  an IN-COMPILER matcher (pcrec has none today) built on [AUTOMATON-KIT].
- MODULES. `m := import(names, sha256 = ...)` is a built-in FUNCTION; `names` is a CONSTANT set of names (an rx
  over file names, e.g. `"json"`); it must resolve to EXACTLY ONE file in the CONFIGURED library directories (zero
  or several = compile error listing the candidates; a pattern from an untrusted source must not read files). It
  returns a MODULE of the file's exported bindings, DESCRIBED BY ITS MAP INTERFACE: its members are its fields,
  reached by the one `.` (`json.row`; §3.2 tool 4). The owner: "what import is is less important than that its
  interface is a map" (CF:891-892), so the interface is RULED and what KIND of thing a module is stays unruled and
  matters less (§13 O46; the kind table, §2.1). An interface is never a created value (CF:890-891), so the map
  interface gives no map value to pass around; rev 7's lean (a module is a compile-time NAMESPACE that `:=` names,
  never passed, stored, returned or used whole as a pattern) is consistent with the ruling and kept as the phase-1
  rule (LEAN). A library file exports with `@export(names)`: every module label whose NAME is in the rx
  `names` (`@export("leap")`, `@export(["leap", /[^_].*/])`, `@export(/[^_].*/)`); the filter must be a set of
  strings, not a target-less filter in an alternation. A name set is a compile-time set: an edge assertion in it is
  the edge-assertion error (§11). A library file with no export is an error ("library exports nothing"). Imports and
  file reads are COMPILE TIME ONLY (artifact self-contained), PINNED by `sha256`; the name -> file map and its pin
  live in configuration (the .rxt `include`/`lib` machinery, `docs/spec/rxt_format.md` §1.1.1, and [LIB]).
- THE EMPTY-MATCH HAZARD. When the program's FINAL pattern is NULLABLE and used in SEARCHED mode: an ERROR in a
  predicate program, a WARNING (`empty.search`) for a program that is one plain PCRE literal (`/a*/` is legal
  PCRE). NULLABILITY IS COMPUTED IN CONTEXT: a pattern is nullable when it can report an empty find in some subject,
  so `/\b/`, `/(?=a)/` and `(?m)^\d*` are nullable although as string sets `/\b/` and `/(?=a)/` are empty. Only the
  caller's anchored/whole-string MODE exempts (validation); an anchor or assertion IN the pattern does not (`(?m)^\d*`
  yields an empty find on every line without digits). No diagnostic either when the empty string is excluded (`&
  !""`) or when opted out. The message names the empty source and the fixes. Empty ENTRIES are legal (`["", "M"]`
  is an optional part). File blank lines are covered by `records` tiling.
- SORT IS SEMANTICS: alternation order = PCRE priority (`ab|abc` vs `abc|ab` on `abcd`); `sort(alts, by =
  "length", order = "desc")` exists only as the deliberate leftmost-longest choice; `unique` keeps the first
  occurrence.
- Compile cost is first-order: every kernel row and prelude macro reports compile time, table size and match speed
  beside its DFA column; relation costs as class counts (§4.6); warnings only on a route change, a cap, or an
  interaction blow-up ([COST-EXPLAIN]). Prerequisites named before any build: [DFA-MIN-FAST], an
  in-construction budget, [PRED-SPLIT], and the static EDGE-ASSERTION check (nullable-prefix/suffix reachability of
  an assertion node, §11). NOT a prerequisite: D196 add. 2's regular-lookaround lowering for conditions (the ruled
  model refuses edge lookarounds in set positions; context-free uses cost the same under every model, review
  Q1X-8). A context assertion in a FINAL pattern (a lookahead, a multi-character lookbehind) keeps today's engine
  choice and its level (§6.1).

**REASONING.** G4; compile-time expansion must terminate, and a strictly decreasing literal parameter is a
syntactic termination check that admits the one legitimate default-level recursion (bounded nesting). Tiling is "no
silent defaults" for data files (the CRLF trap becomes an error). Modules add no value kind (O46's lean: a
namespace, not a value; its interface a map, CF:891-892); import and
export as functions over name-sets add no keyword, and one name-selection rule serves import, export and warnings.
The empty-ENTRY error rejected legitimate optional parts and missed `/\d*/`; the real hazard is a final pattern that
reports an empty find, which is a fact about the pattern in context (review Q1R-9).

**STATUS.** Bounded recursion: RULED (CF:583, predx Q12, low priority, one example), REFINES CF:58. file_text +
records: LEAN (CF:419). Tiling: RULED (CF:583, predx Q13). Import/export as functions, `@export` filter,
no-export error: LEAN (manager, CF:608, CF:619, on Frank's proposals); a module described by its MAP interface: RULED
(CF:891-892, his words), its kind not ruled (§13 O46); the namespace rule for phase 1: LEAN; import resolves to exactly one file, argument a set of names: RULED (CF:630). Empty-match rule: RULED (CF:666), SUPERSEDES the empty-ENTRY error and `skip_empty`;
nullability in context: RULED (CF:713); only the MODE exempts: LEAN (review Q1R-9). String option values: LEAN (review
OWN-7). Prerequisite list: LEAN (review Q1X-8). The untiled-range wording: LEAN (review Q1R-10). Cost surfacing: LEAN
(CF:41). The `trim` / `\r` trap of rev 0 is subsumed by tiling (§13 O18 RESOLVED).

### 7.1 Named warnings

**RULE.** Every warning has a STABLE NAME in dotted families (a contract, stated in the spec): `empty.search`,
`dead.branch`, `label.unset`, `compare.width`, `label.ambiguous` (rev 9: the pointer to the author's validation of an
ambiguous label, never a report that the levels differ: they read one parse, §4.5; it fires only for ambiguity in the
author's OWN pattern text, RULED, CF:964), `warn.unused`, `anchor.operand` (rev 13: an explicit `^`, `$`, `\A`, `\z`
or `\Z` written in an `&` operand's own rx text reads the span both operands match, not the subject; the warning is
RULED, CF:1057-1061 on main, its name and text LEAN; text and reach: §11 THE AMPERSAND RULE TESTED BY POSITION;
whether it reaches every filter role: §13 O65); proposed by review 2026-11-14-r1
and not adopted: `precedence.section`, `array.hole`, `flag.hole`. Control is by `@` effects, rest of file:
`@warn.off("compare.width")`, `@warn.off(startsWith("dead."))` (a label-free library rx is a full rx; the look-alike
`@warn.off(/^dead\./)` is NOT the same set: a name set holds whole strings, so it is the one name `dead.`, §0.1 L15), `@warn.off(/.*/)`; the reverse `@warn.error(/.*/)` (a
strict build); a per-binding form (spelling OPEN); and a compiler option for a whole build (like `-Wno-`). A warning name
written in CODE is a STRING (`@warn.off("label.unset")`): bare, `label.unset` would parse as the field `unset` of a
label named `label` (§5.4 `.` row); in prose its code font is only a name (review r10 CENSUS-14). SELECTORS
ARE A SET OF NAMES AS AN RX, the same name-selection rule as import and export: no `*` wildcard (`"*"` is the
literal name `*`, matches nothing). Errors cannot be disabled (the edge-assertion error included). An `@warn.off`
that suppresses nothing raises `warn.unused` (itself suppressible).

**STATUS.** That warnings have names and can be disabled: RULED (CF:666: "warnings need names and the user must be able
to disable them"); selectors as an rx: RULED (CF:677: "use an rx instead of wild card purely for consistency"). The
list of names: LEAN (manager's list, review RUL-14.1). rev 2's `transform.noop` is gone: a modifier without its
filter is the unapplied-macro error (§2.3).

## 8. Libraries

**RULE.** Standard library = prelude text (macros; typed parameters are out of phase 1, §5.2) on the foundation; it
grows without compiler changes. Standard library sets (each call is a full rx, used in the filter role): `between`
(inclusive), and the gap-bodied transforms (lower case: "GAP" is only §0.1's verdict class, review r14 CENSUS-3), plain
bodies with NO ANCHORS of their own (rev 12, the owner's ruling,
CF:1016-1019, accepted at CF:1006: "No primitive carries an anchoring special case"):

    startsWith(s)  := /(?:${s})(?s:.*)/            # the record: /${rx}.*/
    endsWith(s)    := /(?s:.*?)(?:${s})/           # the record: /.*${rx}/ (lazy gap: LEAN, rev 9, below)
    contains(s)    := occurrences(s, min = 1)           # the record: /.*${rx}.*/ (the same SET; one definition: LEAN, §2.6)
    anchored(s)    := /\A(?:${s})\z/               # ADDED (CF:1005, CF:1014); EXACT ends, rev 13 (CF:1048-1053); identity in filter position (L69)

Each body is a FILTER where it is used, so it matches the WHOLE span (THE ONE ANCHORING RULE, §11); the argument
sits in a hole of the body, part of the body's rx, so `^`/`$` in it are PCRE's with the span as the subject:
`contains(/^err/)` = `startsWith("err")` falls out of PCRE (CF:1018), `contains(/err$/)` also accepts a span ending
`err\n` (PCRE's `$`; `\z` for the exact end; §0.1 L63). The gaps are SCOPED `(?s:...)` so they cross a line break inside
the span ("gaps cross line breaks", CF:1017) and nothing leaks into the hole (the manager's call, LEAN, rev 9); the
holes are written `(?:${s})` so the text means what the hole semantics says (review r10 SIM-3). `anchored` is for a
position OUTSIDE a filter: a final pattern, `anchored(block)` (the record's use, CF:1015), where its ends are the
subject's. Its ends are EXACT, `\A`/`\z` (RULED, CF:1048-1053 on main: "`anchored(/foo/)` as a final pattern does not
match `foo\n`"; rev 12 wrote the owner's placeholder `/^${rx}$/`, whose `$` also held before a final newline, L68,
§13 O62 CLOSED), so `anchored(block)` and `/\A${block}\z/` are one text. Read as "P matched WHOLE on the innermost
scoped match" it gives the same answer in every position tested (a final pattern, a filter, a `label:` condition, an
alternation at P's top, `(?m)` inside P); read as "P in filter role on the span it takes" it DIFFERS in a hole
(`/x${anchored(/a/)}/` on `xa`: `\A`/`\z` no match, that reading (0,2); `docs/dev/lanes/predspec13_anchor.out`), so
the definition is the `\A`/`\z` text and the hole case is an owner question (§13 O64). The owner's first sketch
`startsWith(rx) := /^${rx}/` does NOT work in filter position (there it means exactly rx: `/^5/` rejects `57`; L69).
DIFFERENCES FROM THE RECORD'S TEXT, kept and listed (rev 12): the record writes `contains(rx) := /.*${rx}.*/` and
`endsWith(rx) := /.*${rx}/`; this document keeps `contains := occurrences(x, min = 1)` and a LAZY `endsWith` gap
(rev 9-10, LEAN): the same SETS (a gap is a gap; the record's point is "no anchors"), chosen for how the ARGUMENT's
labels read under the one reading (below; L58). The lean to fold `startsWith`/`endsWith` into `occurrences` with an
anchored argument (review r10 FIXB-9 (2), rev 10's "FAMILIES below") is WITHDRAWN (CF:1019): they stay the plain
bodies above, with no `hit` label. Under the ONE READING (§4.5) a library body's gaps decide how the argument's
labels read, so the bodies are written for the reading a user expects (rev 9, LEAN): `endsWith`'s gap is LAZY, so its
argument starts as far LEFT as it can (`endsWith(/(?<n>\d+)/)` on `ab123`: n = `123`; rev 8's greedy `.*` gave n = `3`,
libpcre2), and `contains` is `occurrences` (§2.6: leftmost hits; rev 8's greedy-lead body read the RIGHTMOST occurrence).
As SETS nothing changes (a lazy and a greedy gap admit the same strings). `when(c, p)` (`x & when(c, p)` = `(x & c & p) | (x & !c)`). Standard FILTER MODIFIERS (§2.7; each transforms the
filter, never the subject): `padded(S)` (leading zeros ignored), `unpadded(n, S)` (read as if zero-padded to width
n), `any_case(S)` (letter case ignored), `quoted(S)` (only the text inside the quotes read), `length(S)` (the
subject's length read), `month_numbered(S)` (a month name read as its number), string positions `left/right/mid`
with literal positions (units = characters per the encoding mode; out-of-range: §13 O14); `json.quoted(S)` (a JSON
string literal read as its decoded text) lives in the `json` module.
- THE `occurrences` TRANSFORM (§2.6; CF:907-909, accepted at CF:905; spelled `search` through rev 12, renamed by the
  owner, CF:1028, rev 13): `occurrences(x, min = 0) :=
  /(?:(?s:.*?)(?<hit>${x})){${min},}(?s:.*)/`, of the `contains` family: each hit, leftmost and non-overlapping along PCRE's
  own parse (the one reading, §4.5; "always", CF:932-933), is one iteration of the repeated label `hit` (§4.3), with
  the argument's labels inside it. `min` (0 or 1, RULED, CF:963-966; default 0): with 0 it never rejects, with 1 a span with no
  hit is rejected; another value is a compile error naming `occurs.at_least` (LEAN, CF:968-969; §13 O58); NO `max`
  for now (CF:951-952). THE TWO ARGUMENT REFUSALS (§2.6, stated there once): a nullable argument (LEAN, manager; §13
  O53) and an argument with a backreference or conditional that can run while its group is unset in the current hit
(LEAN, review r10 SIM-1; narrowed in rev 11, review r12 SIMULATE-2).
  Each hit's labels are read within that hit (§2.6). `contains(x) := occurrences(x, min = 1)` is the
  one-hit TEST of the family, ONE definition (§2.6, §0.1 L58; it also equals `occurrences(x) & some((hit: /(?s).*/))`);
  where no question reads x's labels the compiler may build it as the plain set. The negated test is `!contains(x)`
  (rev 7's `!~`, withdrawn).
- THE GROUP QUESTIONS over any repeated label (§4.3, stated there once): `some(c)`, `all(c)` (= the plain condition,
  rarely written), `count(c)`, and the `occurs` module (`occurs := import("occurs")`), which keeps the COUNTS ONLY
  (CF:913): `exactly(n, c)`, `at_least(n, c)`, `at_most(n, c)`, `none(c)`; rev 7's `occurs.some` and `occurs.all` are
  withdrawn (lean: removed, not aliased). `c` is the usual condition, passed as a parenthesised literal
  (`occurs.exactly(1, (name: set))`; C31 RESOLVED); one record = one iteration (SAME ITERATION BY RECORD, §4.3);
  constant (or caller-parameter) n at default; cost = a capped counter (n+2 states) multiplied in, shown by
  [COST-EXPLAIN]; a count against another label's value is a priced relation (§4.6). The module NAME tells the user
  these are counts of matches. The owner's "use count to check the number of results ... use the occurs module"
  (CF:882-883) is this, over the hits of `occurrences`: ONE population (iterations), not rev 7's second one.
- `count(...)` FIRST, `occurs` AS THE FALLBACK: `count(c)` yields the number of iterations meeting `c`, a canonical
  numeral string (RULED, CF:977-978: "Allows "even()" or other checks for count"), used with the ordinary
  comparisons, arithmetic and filters like a subject number (`n := count((name: any_case("Host")))`, `headers
  & (n: ==1)`; §0.1 L42). There is NO positional rule against `count()`: it is accepted wherever it is written, and
  the compiler refuses it only when building it exceeds the BUDGET (its state cost), the refusal naming the `occurs`
  form as the fix. Below the budget the compiler may RECOMMEND the `occurs` form (a named warning) as the way to reduce
  states. A later, separate plan item, [COUNT-TO-OCCURS] (not phase 1): where the compiler can PROVE the answers do not
  change, it rewrites a `count()` test into the `occurs` form itself. What `occurs` saves over `count()` for the same
  test belongs to the lowering section of a later revision; the budget is ONE measured quantity shared with the
  class-count refusal, no thresholds in the spec (RULED, CF:977; §13 O39 RESOLVED). A count over a whole block is
  written with the program anchored: searched, a shorter span can pass it (§4.3, §0.1 L66).
- TUPLE COMPARISONS are a library macro, no syntax. The defect of the rev 5 spelling `lex_ge([major, minor, patch],
  [1, 4, 0])` is its BARE LABEL NAMES used as values (`major`, `minor`, `patch`; §13 C13), not its arrays: a `[ ]` has
  ordered entries that a structural macro reads in order (§3.4, §5.4), exactly as `join([...])` does in six §12
  cases (CF:548: "join takes an ordinary array"). (Rev 6 said the type picture "forbids" it because "a `[ ]` is an
  alternation ... its order is not part of the value"; that reason was false, review r8 P6-2.) How a tuple
  comparison is spelled is OPEN (§13 C25): a structural macro over two arrays, or `version & lex_ge(1, 4, 0)`, a macro
  whose call record is the bound tuple and whose OPERAND, arriving by `&`, supplies the other tuple as its labels in
  group order (needing a call record of variable length, §13 O47). The phase-1 spelling needs no tuple: "version at least 1.4" is `semver &
  ((major: >=2) | (major: 1, minor: >=4))`: the record holds its entries together, `|` gives any one (§4.1).
- `assert` (§5.6): `some`, `none`, `same`.
Candidate content (a follow-up initiative): network, time, identifiers, communication, checksummed numbers; each
tested against the standard's OWN vectors (as `@assert` statements), the callout oracle and the laws; each shows
its DFA column.

BLESSED CALLOUTS: emitted C text, so the artifact stays self-contained. Blessed = PURE, BOUNDED, TOTAL,
ORACLE-TESTED, and DECLARES ITS REGULAR TWIN where one exists (luhn, weekday, days_in), with its class count
(§4.6): the compiler picks automaton vs callout. First contents: numbers, dates, checksums, network, text; Unicode
normalisation deferred. The unblessed escape hatch is PCRE `(?C)`. Home: its own directory/tests/journal like
memfn/. A callout in DFA context returns a DFA-friendly verb; plain FAIL needs the VM.

**STATUS.** Standard library: RULED as a follow-up initiative (CF:38). Blessed callouts: LEAN (CF:461, "Lean ADOPT").
`when`: RULED (CF:184, "Add when"). Filter modifiers and their names: RULED (CF:722; `unpadded`, `json.quoted`: §13
O37). `occurs` family: RULED as a library (CF:682); the name: RULED in use (CF:782). `count()` first, `occurs` the
fallback: LEAN (CF:823, "perhaps the solution is both"). `count()` refused only on BUDGET, `occurs` recommended to
reduce states, no positional rule: RULED (CF:832: "i would refuse count() on budget or as a recommended way to reduce
states rather than rules"); the budget as ONE labelled measured quantity, no thresholds in the spec: RULED (CF:977, to CF:974-975; §13 O39). The
automatic rewrite: RULED as a LATER plan item (CF:840). Tuples as a library macro: RULED (CF:644), SUPERSEDES predx's
tuple-on-the-left-of-`:` syntax (S12); its spelling: OPEN (C25). The comma form of the semver condition: RULED (CF:704).
Rev 8: `occurrences` as a library transform of the `contains` family, `occurs` keeping counts only, `some`/`all` the one
spelling: CF:907-914 (accepted at CF:905); the written bodies, the law, and the removal (not aliasing) of
`occurs.some`/`occurs.all`: LEAN (this document). Rev 9: the hits on PCRE's parse: RULED (CF:932-933); `min`: the
owner's LEAN (CF:933-934), 0 or 1 RULED (CF:963-966), no `max`: RULED (CF:951-952); `contains` by `occurrences` and the lazy `endsWith`: LEAN (this
document); the `(?s)` gaps and the nullable refusal: LEAN (manager). Rev 10: scoped gaps and grouped holes, the second
refusal: LEAN (review r10 SIM-3, SIM-1). SUPERSEDES rev 7's "`occurs`: `all`, `some`, `none`,
..." and its search result as a second population. Rev 12: plain gap bodies with no anchoring special case, `anchored`
added, the fold of `startsWith`/`endsWith` into `occurrences` withdrawn, the naming rule over every provided transform:
RULED BY ACCEPTANCE (CF:1011-1022, accepted at CF:1006); keeping `contains := occurrences(x, min = 1)` and the lazy
`endsWith` against the record's `/.*${rx}.*/` and `/.*${rx}/` (same sets): LEAN (this document). Rev 13: `anchored`
has the exact ends `\A`/`\z`: RULED (CF:1048-1053 on main; §13 O62 CLOSED); the name `occurrences`: RULED (CF:1028;
§13 O61 CLOSED).

## 9. Cut from the first spec

**RULE.** Not in the first spec: DECLARED TYPES (`type(...)`, `isodate: date`; rev 7 called them "interfaces", a
word that now names the array and map interfaces, §0.3, CF:890), TYPE MEMBERS declared with a type, SCOPE-LIMITED
UFCS (`d.weekday` resolving to a scoped macro), `types()`. Declared types may return after a build as LIBRARY
PACKAGING (a set of required labels with value types, checked by inclusion per field, at the module export
boundary); the owner's 11-15 remarks bear on that return ("I like the idea of types but they need more thinking",
CF:889; "this leans into the idea of an interface to a type over the type", CF:890), and typed parameters are out of
phase 1 (§5.2). The NO-SEMANTIC-OVERRIDE rule (two compliant formats holding one date must agree) stays as a rule
for that return. Modules stay (§7, §13 O46; a definition's labels are dotted paths).

**REASONING.** predx §9: none of thirteen programs needed them; UFCS would add a second resolution rule to `.`, whose
ONE meaning is now ruled (a field of the map interface, CF:892, CF:898-899).

**STATUS.** RULED (CF:583, predx Q8). SUPERSEDES rev 0 §9's interface, member, UFCS and `types()` rules.

## 10. Eval

**RULE.** `x & eval($fmt)` is a FILTER (an rx, §2.1) known only at match time, opaque to analysis; the static matcher finds
candidates and eval filters them. DFA-only, the same automaton code as compile-time `records()`. Only as an
explicit MODULE ("requires module 'eval'" otherwise; the artifact declares the runtime dependency), with a BUDGET
(exhaustion is a distinct result) and a cache keyed by pattern string. The workhorse is the caller-PARAMETERISED
matcher (§11); self-describing files are a demonstration, not a driver.

**STATUS.** LEAN (an idea, late in #6; CF:430 runtime eval + addendum).

## 11. The outer layer

**RULE.** The expression language is the OUTER layer: an rx is a LITERAL inside it, so a program that is just
`/(a|b)+c/` is valid and every PCRE pattern is a one-literal program (no separate PCRE mode). A ONE-LITERAL PROGRAM
IS EXACTLY TODAY'S PCRE PATTERN: no strict subset, no level beyond today's engine choice, no set position (G3), with
the two marks below written as PCRE spells them in a literal (`$\{` for PCRE's `${`; with the rx-`&` switch ON, `\&`
or `[&]` for PCRE's bare literal `&`, both plain PCRE, RULED, CF:1041-1046 on main).
Top-level `:=` replaces DEFINE for new code; DEFINE stays only as PCRE syntax inside a literal with PCRE's meaning.
The predicate opt-in selects WHICH LANGUAGE a file or API call is in. Library files are expression-language files
with `@export`. The `.rxt` format is unchanged. Crossings: rx -> expression ONLY by `${...}`; expression -> rx only by
`/.../`. (Rev 10 also listed `(?&name)` naming the pattern binding whose literal it sits in; PCRE rejects such a
literal, so it was a third non-PCRE reading of rx text. Rev 11 writes self-recursion with the literal's OWN named
group, `balanced := /(?<p>\((?:[^()]|(?&p))*\))/`, plain PCRE, §7: nothing crosses and the marks inside `/.../` stay
exactly two; review r12 CENSUS-2, the manager's pick, LEAN.)

Literals: full PCRE inside, `\/` escapes; a literal means EXACTLY what PCRE means: NO implicit extended mode
(`/foo bar/` keeps its space, `#` is literal); extended mode is per literal (`/.../x` or a leading `(?x)`). A literal
is its OWN SCOPE (numbered groups do not leak; named groups are fields of its value); NO INHERITED FLAGS (a hole's
pattern keeps its own flags: §13 O32).

THE MARKS INSIDE `/.../` (stated once; CF:978-984 for `&`; review r10 CENSUS-2 for `${`). A literal means what PCRE
means EXCEPT for exactly two marks, which are the predicate language's two additions to rx text (CF:795: "${} and
&"):
- `${` ALWAYS OPENS A HOLE inside rx text in the opt-in, in every position (an atom, a class, a quantifier, a group
  name; §5.4 `${ }` row), whatever the `&` switch says: the owner's own `${/.../ & blah}` relies on it (CF:979). In
  PCRE `${` is the anchor `$` then a literal `{` (`x${num}` compiles, libpcre2 10.46), which can NEVER match: `$`
  holds only at the end or before a line break, and the next character would have to be `{` (`x${num}` does not
  match `x{num}`); and `${2}` is a PCRE compile error. So IN A PATTERN POSITION the exception takes no matchable PCRE
  meaning away. In a CLASS and inside `\Q...\E` it does: there PCRE's `${` is literal text that matches (`[${]x`
  matches `{x`; `\Q${\E` matches the text `${`, libpcre2 10.46), and the hole reading takes that away; the rewrite
  below restores it, and the G3 transfer applies it, so no transferred answer moves (rev 11, review r12 CENSUS-4). A literal `$` then `{` is written `$\{` (the same PCRE meaning in a pattern position, a class or a comment;
  inside `\Q...\E`, `$\E\{\Q`). The G3 transfer of a corpus pattern does exactly this rewrite (§0 G3: 33 of 7,057
  corpus pattern lines contain `${`, all in `tests/vars/`, where [VAR]'s variable hole already uses the spelling;
  command in §0 G3).
  The stated exception (the manager's pick on CENSUS-2: LEAN).
- `&` is ALL OR NOTHING, by a MODULE or OPTION (RULED, CF:978-979 "fully yes or no", CF:981-984; the switch's name is
  a placeholder). ON: `&` is the INTERSECTION operator everywhere in that rx text, with D196's semantics and
  precedence (concatenation, then `&`, then `|`). OFF: `&` is PCRE's literal everywhere, and an intersection is
  written in the expression language, with the whole rx inside a hole when it must sit in rx text (`${/(\d+)/ &
  <256}`, the owner's `${/.../ & blah}`). There is NO position-dependent reading (rev 9's C23 reading A, `&` an
  operator only right before `${`, is REJECTED, CF:981). The manager's lean: the switch is OFF by default, so pasted
  PCRE keeps its meaning (G3) (CF:986-987): LEAN, §13 O60.
  WHICH `&` IS THE MARK UNDER ON (RULED, CF:1041-1046 on main, rev 13; his words: "agree. Limited to where | is used
  to mean alternation. Also, \& should work as escape. Why not?"; §13 O60 (d) CLOSED; the ruled "fully yes or no" is
  not re-opened). Under ON, `&` is the operator EXACTLY in the positions where `|` means alternation; everywhere else
  PCRE's reading stands: inside a class (`[a&b]`), quoted text (`\Q&\E`), a callout's text (`(?C...)`), a `(?...`
  opener (`(?&name)`, the subroutine call, 154 of the 165 corpus pattern lines with `&`), a property name
  (`\p{L&}`), a comment, and after a backslash. A LITERAL ampersand is `\&` or `[&]`, both plain PCRE meaning `&`
  under both settings (`\&` compiles and matches `&`, libpcre2 10.46 and Python 3.14's `re`, rev 11's check). What
  rev 11 withdrew was only an automatic REWRITE of every `&` to `\&` when a pattern moves across the switch (it turns
  `(?&a)` into `(?\&a)`, a PCRE compile error, "unrecognized character after (? or (?-"); the escape itself was never
  refused (CF:1045-1046). So the reading is decided by PCRE's own tokenizing (the positions where `|` is an
  alternation bar), not by a position the predicate language adds.
- SCOPE OF AN rx-TEXT `&` (rev 11, review r12 CENSUS-5). By D196's precedence the `&` takes the WHOLE CONCATENATION on
  each side within its alternative, not one atom: `/(\d+)&${<256}/` alone guards the number, but `/port=(\d+)&${<256}/`
  is `/port=(\d+)/ & <256`, EMPTY; to guard one atom, group it, `/port=(?:(\d+)&${<256})/` (§0.1 L67).
So C2's "a literal means EXACTLY what PCRE means" (CF:577) holds for every other mark (and, by the ruling above, for
every `&` that is part of a PCRE construct), and G3's check runs with the switch OFF and `${` rewritten.

Inside a LARGER program, literals start from the STRICT PURE SUBSET (refuse
`\K`, `(*ACCEPT)`, `\G`, backtracking verbs, callouts/inline code, each admitted later once its predicate meaning is
defined; unbounded backreferences need `vm`).

STRING SETS. A pattern used as a SET denotes the strings it matches ENTIRELY (keys starting with S are `/S.*/`).
SET POSITIONS are: a side of `&` (either side), a `label:` condition, a compile-time set (an `enumerate` argument,
an `@assert` argument, a name set for `import`/`@export`/`@warn`), and a hole's set. The first three are FILTER ROLES
(§0.3): each matches its stretch WHOLE; a side of `&` and a condition open a scoped match over a stretch of the
subject, a compile-time set over each whole string. A computed label's value is a VALUE, not a pattern (§4.4). A
HOLE'S SET is a set position (the edge-assertion error applies to it, L8) but NOT a filter role: it is a part of the
rx it sits in, opens no scoped match, and its anchors read the enclosing one. A macro's PARAMETER is in whichever of
these its BODY puts it, after expansion (rev 14, RULED 2026-11-15 20:45 on main: the role, never the name): the
argument of `contains`, `startsWith`, `endsWith`, `anchored` and `occurrences` lands in a hole of the body; the
argument of `padded` or `quoted` lands in a `label:` condition of the body, a filter role (§2.7 BODIES OF THE
PROVIDED TRANSFORMS). (Rev 12 called all four "filters"; review r14 CENSUS-5 / F2: the word is reserved for the
filter roles. Rev 13 listed "a filter body (incl. a modified filter's argument)" as a role of its own; rev 14 drops
the clause: the body says where the argument lands.)

THE ONE WHOLE-MATCH RULE (stated once; rev 12, completed in rev 13, re-worded in rev 14; the owner's ruling
CF:1001-1020, the manager's advice he agreed to, CF:1006: "Ok I agree", CF:1048-1062 on main (`anchored`'s exact
ends; both `&` operands filter roles, the warning), and the three 2026-11-15 entries after rev 13 on main (the
wording, "That's a good clarification"; no `anchored`-specific error in a hole; one warning keyed off the ROLE); it
RESTATES CF:761 and CF:991-996 without changing their answers except `$`, below). The owner's request: "We need
consistent rules around when rx is anchored and to what. I don't want to have a bunch of "primitive" functions have
special cases concerning that" (CF:1002-1004). WORDS (rev 14, RULED, "That's a good clarification"): a filter role
"matches its stretch whole"; the two sides of `&` match THE SAME STRETCH WHOLE, tied to each other (where that
stretch sits is decided by what surrounds the `&`); the word "anchored" is kept for the macro `anchored(...)` (§8)
and for the real assertions `\A`, `\z`, `\Z`, `^`, `$`. The rule, in three sentences:
- A FILTER ROLE MATCHES ITS STRETCH WHOLE. A filter role is decided by the ROLE an rx stands in AFTER MACROS ARE
  EXPANDED, never by a macro's name (RULED, 2026-11-15 20:45 on main: "padded is a simple macro so the warning
  shouldn't key off of the name"): BOTH sides of `&` (RULED, CF:1054-1062 on main: "&: both sides filter and warn if
  anchor"; the operator stays symmetric, L39), a `label:` condition, and a compile-time set; an rx passed as a
  macro's PARAMETER is in a filter role exactly when the macro's BODY puts it in one (beside `&`, after `label:`),
  and in a hole when the body splices it into a hole (§2.7 BODIES OF THE PROVIDED TRANSFORMS). Its set is a set of
  WHOLE strings (`m & /^err$/` = `m & /err/`; the owner's reason: `/\d\d/ & between(1, 12)` not matched whole "would
  match "31"", CF:990-991).
- EVERYWHERE ELSE AN RX IS SEARCHED OR SPLICED AS IN PCRE: a program's FINAL pattern is searched in the subject, and
  so is a `records` item rx in its file text (§7); an rx in a HOLE, outside any filter role written inside the hole,
  is part of the rx around it and has no whole-match requirement of its own.
- AN EXPLICIT ANCHOR READS THE INNERMOST SCOPED MATCH. `^` and `$` (and `\A`, `\z`, `\Z`, and `(?m)`'s line ends)
  are the ends of the SCOPED MATCH (§0.3): exactly two things OPEN one (rev 13, review r14 F2), the PROGRAM (its
  subject) and every FILTER ROLE wherever it stands (its stretch), in a final program, under `anchored`, inside a
  hole, inside another filter role; A HOLE NEVER OPENS ONE. This is PLAIN PCRE WITH THE STRETCH AS THE SUBJECT, no
  extra rule (CF:1013-1014). So `$` (and `\Z`) is PCRE's: the stretch's end or just before a final newline of it; the
  exact end is `\z`. Checked against every position an `&` can stand: THE AMPERSAND RULE TESTED BY POSITION, below.
Consequences, each a sentence of the rule, not a further rule:
- NO PRIMITIVE CARRIES A WHOLE-MATCH SPECIAL CASE (CF:1018). The library's gap-bodied transforms are plain bodies (§8):
  `contains`, `occurrences`, `startsWith`, `endsWith` put gaps around a hole holding the argument; `anchored(rx) :=
  /\A(?:${rx})\z/` puts the scoped match's EXACT ends around it (RULED, CF:1048-1053 on main), a PLAIN MACRO (rev 14,
  RULED: no `anchored`-specific error anywhere, §8).
- REJECTED (CF:1019-1020): an explicit anchor that SWITCHES OFF the whole-match requirement (under it `/^5/` would
  accept more than `/5/`). An explicit anchor in a filter role never widens it (L69).
- AN EXPLICIT ANCHOR IN A FILTER ROLE DRAWS ONE WARNING, `anchor.whole` (RULED that it exists, CF:1054-1062 on main;
  RULED that it covers every place a pattern must match its stretch whole and keys off the role, 2026-11-15 20:44 (b)
  and 20:45 on main; its name and text are this document's, LEAN): below.
- A COMPILE-TIME SET (an `enumerate` or `@assert` argument, a name set) is a filter role over whole strings: its
  `^`/`$` are the string's own ends (this document's reading of the one rule, LEAN; rev 11 called it an extension).

What follows, every answer as rev 11 gave it except `$`. Because a filter role matches its stretch whole, a `^` or `$` written
at the edge of a filter role ADDS NOTHING: `/\w+/ & /^foo/` = `/\w+/ & /foo/`, the one word `foo`, NOT the words that start with
`foo` (that is `/\w+/ & startsWith("foo")` = `/\w+/ & contains(/^foo/)`; §0.1 L41); `P & (x: /^S\w*/)` makes x
ENTIRELY `S\w*` (L7); `alts & !/^#.*/` drops the entries that are entirely `#` and non-line-break characters (L11).
"Starts with" is a gap after the argument: `startsWith("foo")`, or `contains(/^foo/)`, where only an empty lead gap
reaches the `^` (L17). The lone program `/^foo/` is different because it is a FINAL pattern, searched in the subject:
there `^` is the subject's start (or a line start under `(?m)`). `$` is PCRE's: `contains(/err$/)` ACCEPTS `err\n`
while `endsWith("err")` rejects it (L63; libpcre2 10.46 and Python `re`, `docs/dev/lanes/predspec12_anchor.out`).
Rev 10-11 read `$` in a filter as the span's end EXACTLY (review r10 SIM-5): an extra rule, WITHDRAWN in rev 12
(LEAN, this document's reading of "no extra rule"). The answer moves only where something after the `$` can consume
the final newline: `/err$/` as a filter rejects `err\n` under both readings (the whole span must be matched), while
`/err$\n/` now accepts it and `contains(/err$/)` (whose tail gap takes the `\n`) now accepts it. This RESTORES the 2026-11-13 understanding ("b was in the span context
of a", CF:56 "in-context stays for pattern-level &") in exactly this sense, and it SUPERSEDES the 2026-11-14 Q1
entry's listing of `^`/`$` among the errors (CF:713-717); the foundation stays STRING SETS (CF:761 (1)).

ONE SPAN PER FILTER ROLE, now a CONSEQUENCE of the one rule (review r8 P6-5; RULED BY ACCEPTANCE for the arguments of
`contains`/`occurrences`, CF:993-994, and as plain PCRE by CF:1013-1014; §13 O49 RESOLVED). The span is fixed where the
FILTER ROLE is: the `&` operand's text, the label's text. A HOLE written inside a filter opens no span of its own,
because a hole has no scoped match of its own (a FILTER ROLE written inside the hole does open one, over the text
the hole takes: rev 13, review r14 F2): an rx in a hole of a filter's body (the argument of `contains`,
`occurrences`, `startsWith`, `endsWith`, a user macro's hole) is matched as part of that body, against the span, so its
`^`/`$` are the span's ends, as PCRE gives them. So `contains(/^err/)` = `startsWith("err")` although `contains`'s body
(`occurrences`'s) puts the argument in a hole inside its loop, after a lazy gap, and `occurrences(/^err/)` has at most one hit,
at the span's start (§2.6, §0.1 L16, L17). A modifier's argument is NOT a separate case (rev 14, RULED 2026-11-15
20:45 on main): `padded`'s body puts its argument in a `label:` condition on the digits after the leading zeros, a
filter role, so it matches that stretch whole (`padded(/^5/)` = `padded("5")`, §0.1 L13); a user macro with the same
body behaves the same (§2.7 BODIES OF THE PROVIDED TRANSFORMS). In a FINAL pattern a hole's `^`/`$` are the subject's (or a line's) ends, as in the pasted text. Rev 6
read `^` in a hole as the HOLE's own start, which made `contains(/^err/)` accept `xerr` while §0.1 L17 said it was the
same as a search for `/^err/` (review r8 SIM-1).

An assertion that would READ BEYOND THE FILTERED SPAN is a COMPILE ERROR naming the fix (CF:761 (3)): `\b` at the
span's start or end, and (LEAN, the manager's reading) a lookaround that can read outside the span, reachable at its
start through a nullable prefix or at its end through a nullable suffix; the property is decided statically on the
pattern. `^`/`$` are NOT in this class. (Rev 12: plain PCRE with the span as the subject would give `\b` at the
span's edge a meaning, the subject edge read as a non-word character; that is not the text's real context, so the
ruled refusal stands, CF:761 (3). The one anchoring rule speaks of anchors, `^`/`$`, only, and an anchor reads no
character, so it is not an anchoring special case.)

    "`\b` in the condition on x reads text outside x: put `\b` in the pattern that places x"

Assertions strictly INSIDE the span keep PCRE meaning (`(x: /\d+\b\.\d+/)`: the `\b` reads only x's own characters).
MULTILINE (C35, CF:753): an explicitly written `(?m)` keeps PCRE's meaning inside the span (`^`/`$` also at line
breaks within it); without it `^` is the span's start and `$` its end or the point just before a final newline of
the span (review r14 CENSUS-4: rev 12 wrote "the span's ends", the exact-end reading it had withdrawn); never does
either read outside the span. CAPTURED STRINGS
(`$x`, a one-string set) and every other value `$` reads (metadata, a computed label; §5.4), what a modified filter reads (its reading's output, §2.7) and compile-time sets are
CONTEXT-FREE. A
SEARCH inside a span (`(m: occurrences(rx))`, §2.6) is a filter like any other: its argument's `^`/`$` are the ends of
the filtered span, PCRE's with the span as the subject (D193 add. 3, which says the same of a predicate's regex test;
CF:993-994; CF:1013-1014). FINAL patterns and a `records` item rx are SEARCHED in their subject and keep full PCRE meaning,
context assertions included. Nullability for the empty-match rule is computed IN CONTEXT (§7). A named in-context form
(a library call, no keyword) is added only on a measured need (D77).

HOLES `${expr}`: in an atom position every hole denotes a SET OF STRINGS and matches one of them (typed syntax
positions, below, take one value from a finite set): a one-string set (a captured string, a
quoted literal) inserts LITERAL TEXT (never re-parsed), any other rx inserts a sub-pattern (`${isodate & (year:
2000)}` = a sub-pattern insertion); a MACRO in a hole is the unapplied-macro error (§2.3; CF:362). A hole's set is a
set position for the edge-assertion rule (a `\b` or edge lookaround at its edge is the error above, L8; write the
assertion in the literal around the hole); its `^`/`$`, outside any filter role written inside the hole, are the
ends of the innermost scoped match around it, the enclosing filter role's span or a final pattern's subject; an `&`
operand or a `label:` condition written INSIDE the hole is a filter role and opens its own over the text the hole
takes (THE ONE ANCHORING RULE, above; review r14 F2: `/x${/^a/}/` never matches `xa`, `/x${/^a/ & /(?s).*/}/` matches
it, §0.1 L71). In the inner direction (an API caller passing a PCRE string) a GUARD is written with an explicit `&`
when the rx-`&` switch is ON: `(\d+)&${ <256 }` (with it OFF, the whole rx in the hole: `${/(\d+)/ & <256}`); a hole
after an atom WITHOUT `&` is a FOLLOWING item (`(\d+)${ <256 }` = digits followed by a numeral below 256). The guard
covers the whole concatenation on each side of its `&` within the alternative (D196 precedence, above): inside a
longer literal group the guarded atom, `/port=(?:(\d+)&${<256})/`, since `/port=(\d+)&${<256}/` is empty (§0.1 L67;
review r12 CENSUS-5). Generalized backreferences (`(?<y>\d{4})-${$y + 1}`); holes are order-free; holes in typed SYNTAX
POSITIONS (`\d{${n}}`, `{${min},}`, `[${a}-${b}]`, a group name `(?<${x.label}>...)`) supply that position's value
from a finite compile-time set; holes never change structure seen outside: an atom hole is one entry, and a
name-position hole names the group the LITERAL writes around it (the literal's own structure; review r10 CENSUS-3). Run-time INPUTS (`limit := param(/\d{1,4}/)`) are read-only per match, validated against their
type, read AS LATE AS POSSIBLE; computations on run-time inputs only are default-level (§6.1).

THE AMPERSAND RULE TESTED BY POSITION (rev 13; the owner's CONDITION on his ruling, CF:1058: "Agree but test if it
makes sense. Like in a hole, what does it mean that they are anchored?"). The rule: both operands of `&` are filter
roles, each matches the WHOLE span the `&` is applied to, and an anchor in an operand reads THAT span. In every
position below the span is the one piece of text both operands must cover; it is the only sensible meaning, because
`&` intersects two SETS of strings and a string must be one stretch of the subject from end to end to be in both. Each
row is emulated on libpcre2-8 10.46 (each operand matched as plain PCRE with the span as the subject) and Python
3.14's `re`, 0 disagreements: `docs/dev/lanes/predspec13_anchor.py` / `.out` (run: `timeout 300 python3 -I
docs/dev/lanes/predspec13_anchor.py`). Searched rows report the leftmost start, then the left operand's preferred end
(D196; the greedy operands here prefer the longest that qualifies). `<256` is the comparison set, canonical numerals
0-255 (C9).

| position | the span the operands match whole (and their anchors read) | example, subject: answer | sensible | `anchor.operand` |
|---|---|---|---|---|
| (i) a final program, searched | each candidate stretch of the subject the search tries, in D196's order; the stretch reported is the one both accept | `/^\d+$/ & <256`, `x300 12`: `30` at 1-3 (`/^\d+$/` alone: no match; `/\d+/ & <256`: `30`, the same) | YES: "a numeral below 256 somewhere"; the anchors add nothing | fires (at `^` and `$`) |
| (ii) a final program under `anchored` | the whole subject, exact ends (`anchored(P) = /\A(?:P)\z/`) | `anchored(/^\d+$/ & <256)`: `x300 12` no match; `200` match 0-3; `200\n` no match (the same without the operand anchors) | YES: the anchors coincide with the subject's ends and add nothing | fires |
| (iii) inside a hole of an rx | the text the hole takes; the rx around the hole reads the enclosing scope (the owner's own reading, CF:1078-1080 on main: "the match span that the & expression creates anchors for is the ${} hole") | ACCEPTANCE ROW (the owner's, CF:1079): `/999${ /\d+/ & <100 }999/`: `99945999` match 0-8 (the hole's text `45`); near row `99912345999`: no match (`12345` is not below 100, and no other `999` pair brackets a numeral). `/port=${ /^\d+$/ & <256 }/`: `port=80` match 0-7; `port=300` match 0-7 (`port=30`: nothing after the hole stops the number); `/port=${ /\d+/ & <256 }\b/`: `port=300` no match | YES: the hole's text is the only stretch both can share; reading `^` as the subject's start would make the hole unmatchable (`/port=^\d+$/`: never) | fires |
| (iv) a filter nested inside a hole | the INNERMOST filter role's span: an inner `&` in a hole of an outer operand reads the inner hole's text; a condition in a hole reads its label's text | `/\w+/ & /a${ /^\d$/ & <5 }b/`, `a3b`: match 0-3 (the inner `^` read as the outer operand's start: no match); `P := /(?<w>\w)-(?<v>\w+)/`, `/k=${ P & (v: /^a\w*/) }/`: `k=x-ab` match 0-6, `k=x-ba` no match | YES: each `&` has its own span; an anchor reads the nearest | fires (inner operands); for the condition: §13 O65 |
| (v) a `label:` condition | the label's text in this match | `P := /(?<w>\w) (?<x>\w+)/`, `P & (x: /^S\w*/)`: `a Sab` match 0-5, `a xSab` no match | YES (E-CTX-1; unchanged since rev 11) | by the ruling's words NO (the anchor is in a condition, not directly in the operand); LEAN yes, §13 O65 |
| (vi) an operand that is itself an `&` chain | the same span for every operand of the chain (`&` is associative, L1) | `(/^\d+/ & /\d+$/) & <256` and `/^\d+/ & (/\d+$/ & <256)`, `x300 12`: both `30` at 1-3 | YES: grouping changes nothing | fires (each anchor) |
| (vii) an operand with an edge assertion that looks OUTSIDE the span (`\b`, a lookaround at the edge) | the span; but the assertion would read the character before or after it, which plain PCRE on the span sees as "no character" | `/\w+/ & /\bfoo/`, `xfoo`: read as plain PCRE on the span it would match `foo` at 1-4, while `/\w*\bfoo/` (where `\b` reads the real text) does not match | NO for `\b`/lookarounds: they have no meaning confined to the span; that is why they are the EDGE-ASSERTION ERROR (CF:761 (3), L10, E-CTX-4), unchanged. Anchors read no character outside the span (`$` reads only a final newline inside it), so they are not in this class | no (the ERROR instead). `(?m)^foo` in an operand: the span's start counts as a line start (`/\w+/ & /(?m)^foo/`, `xfoo`: `foo` at 1-4): fires |
| (viii) rx-text `&`, switch ON | D196 precedence: each side is the WHOLE CONCATENATION of its alternative (L67), so the span is the text that alternative takes; `^`/`$` written OUTSIDE a group around the `&` read the enclosing scope | `/^\d+&${<256}$/`, `x300 12`: `30` at 1-3 (operands `^\d+` and `${<256}$`); `/^(?:\d+&${<256})$/`: `x300 12` no match, `200` match 0-3; `/a\|^b&\w+/`, `xb`: `b` at 1-2 (`^b` is an operand) | YES by the same rule, and the MOST surprising position: an author who writes `^...$` around a whole rx-text pattern means the subject; the warning names the grouped fix | fires; text names `/^(?:...)$/` |

THE LOOK-ALIKE the rule creates (review r14 F1; §0.1 L70, L71): `P` vs `P & /(?s).*/` (intersection with every string)
differ exactly when P writes an anchor: `/^foo/` on `xfoo` no match, `/^foo/ & /(?s).*/` `foo` at 1-4; `/foo$/` on
`foox` no match, `/foo$/ & /(?s).*/` `foo` at 0-3; in a hole, `/x${/^a/}/` on `xa` no match (the hole opens no scope,
`^` is the subject's start), `/x${/^a/ & /(?s).*/}/` match 0-2. The warning fires on the second form of each, so the
rows are DIFFERENT: WARNING.

THE WARNING `anchor.operand` (§7.1's naming; RULED that it exists, CF:1057-1061; name, text and reach LEAN, this
document). IT FIRES on `^`, `$`, `\A`, `\z`, `\Z` (with or without `(?m)`) written in an `&` operand's OWN rx text,
i.e. an anchor whose innermost scoped match is that operand's span: a literal operand, a binding used as one (its
text, L2), either side, at any depth of an `&` chain, in rx-text `&` under ON. IT DOES NOT FIRE on an anchor inside a
HOLE that a macro body puts the argument into (`x & contains(/^err/)`: that `^` follows the body's gap and is the
documented spelling of "starts with", L17), nor on `anchored(...)` (no anchor is written; in filter position it is
the identity, L69). One warning per anchor, at the anchor, naming the `&`:

    "`^` in this operand of `&` is the start of the text both operands must match whole (here: <the reported match |
     the text the hole takes | the text of the enclosing operand>), not of the subject, so it always holds and adds
     nothing; to pin the subject's start, write the final pattern as `anchored(...)` (in rx text: `/^(?:...&...)$/`)"

(`$`, `\z`, `\Z`: "end" for "start"; `(?m)`: "a line start" and the span's start counts as one.) Whether the same
warning fires for an anchor in a `label:` condition, a modifier's argument or a compile-time name set, where the
anchor adds nothing for the same reason (§0.1 L7, L13, L15): §13 O65 (lean: yes, one warning for every filter role).

`anchored(P)` CHECKED THE SAME WAY (CF:1048-1053: the "P in filter role on the enclosing scope" wording may stand only
if no case differs from `\A(?:P)\z`; `predspec13_anchor.out`, second table). Read as "P matched WHOLE on the
INNERMOST scoped match", it agrees with `\A(?:P)\z` in every case tested: a final pattern (`foo\n` no match, `foo`
match), `$` in P (`anchored(/foo$/)` on `foo\n`: no match), an alternation at P's top (`anchored(/a|b/)` on `ab`: no
match; `anchored(/a|ab/)`: 0-2), `(?m)` inside P (`anchored(/(?m)^a$/)` on `a\n`: no match), inside a filter
(`/\w+/ & anchored(/foo/)` on `xfoo`: 1-4), a `label:` condition, and a hole (`/x${anchored(/a/)}/` on `xa`: no match,
the hole opens no scope). Read as "P in filter role ON THE SPAN IT TAKES", it DIFFERS in a hole (`/x${anchored(/a/)}/`
on `xa`: match 0-2; `/${anchored(/a/)}b/` on `ab`: match 0-2). The wording has both readings, so the DEFINITION is the
text `/\A(?:${rx})\z/` and the hole case is an owner question (§13 O64).

**REASONING.** Making PCRE text a literal gives G3 without a mode switch; free-form multi-line layout belongs to the
expression language, not to literals (C2); the strict subset applies only where a literal sits inside a larger
program (review OWN-14). The Q1 foundation: review r1 compared context-marked triples (A), value-scoped string sets
(B1) and string sets composed in context (B2); the rule set is string-set shaped, and rev 2's argument for A did not
discriminate (its cases are FINAL patterns, searched under every model; Q1R-12, Q1X-1). Under A or B2 look-alikes
fail SILENTLY (`\w{3} & /\w+\b/` moves the match; a `^` condition on a repeated label passes one header and fails
two); under B1 others do (`n: p` dead for a lookbehind `p`). With `^`/`$` bound to the filtered span (CF:761) a `^`
never reads the subject's start; under the anchoring (CF:991-993) a `^` in a directly applied filter adds nothing, and
"starts with" is the gap body `startsWith(...)` = `contains(/^.../)` (rev 10 said the `^` look-alikes agree with
`startsWith`; review r12 SIMULATE-1). Rev 12's one anchoring rule (CF:1011-1020) takes the last special case out:
where an rx is anchored is decided by its POSITION (filter or not), and `^`/`$` are PCRE's in the scoped match, so a
reader predicts every anchor from PCRE plus one sentence, and no library primitive needs its own anchoring clause (the
owner's "consistent rules ... no special cases", CF:1002-1004); the price is PCRE's `$` before a final newline (L63),
which `\z` avoids; every remaining divergence needs an assertion that reads outside the span, a
static property, and refusing exactly those leaves no silent failure and no unbuilt lowering at the default level
(G0, G2). Nullability in context is A's one real gain, adopted. What a hole holds (one string or a set) decides its
insertion, never the text's content (no injection); a guard needs `&` so the hole rule has no exception (C4).

**STATUS.** Outer layer: LEAN (CF:564, "Lean ADOPT"). Literal leanings incl. the strict subset: RULED (CF:56, "I like your
suggestions"); the subset scoped to literals inside a larger program and the one-literal program = today's pattern:
LEAN (review OWN-14). No implicit x-mode: RULED (CF:577, C2). STRING SETS: RULED (CF:713, CF:761 (1)). In a filter
`^`/`$` = the ends of the span being filtered: RULED (CF:761 (2), SUPERSEDES the part of CF:713 that listed `^`/`$`
among the errors). THE ONE ANCHORING RULE (a filter role matches its whole span, everywhere else unanchored as in PCRE,
`^`/`$` the scoped match's ends as plain PCRE, no primitive with an anchoring special case, the explicit-anchor
switch rejected): RULED BY ACCEPTANCE (CF:1011-1020, accepted at CF:1006; rev 12); its reading of the compile-time
sets as filters over whole strings: LEAN (this document). Assertions reading beyond the filtered span refused: RULED for `\b` (CF:761 (3)); edge
lookarounds in the same class: LEAN (manager's reading, CF:761). `(?m)` written explicitly: RULED (CF:753, C35).
Context-free captured strings, modifier readings and compile-time sets, nullability in context, a named in-context form only on
measured need: RULED (CF:713). The three candidates and the restated reasoning: LEAN (review Q1R-1, Q1X-2, Q1R-12,
Q1X-1). Guard holes with `&`: RULED (CF:573, C4); a macro in a hole the unapplied-macro error: RULED (CF:362). One
span per filter role (an argument or a hole reads the enclosing filter's span): RULED BY ACCEPTANCE for the
arguments of `contains`/`occurrences` (CF:991-994, accepted at CF:990), and, since rev 12, a consequence of plain PCRE
with the span as the subject (CF:1013-1014) for every hole (§13 O49 RESOLVED); filters anchored at both ends: RULED
BY ACCEPTANCE (same cite; restated by CF:1011); `$` the exact end (review r10 SIM-5): WITHDRAWN in rev 12, `$` is
PCRE's (LEAN, this document's reading of "no extra rule"). The
self-recursion through the literal's own named group, with no crossing (rev 10: `(?&name)` naming the binding, a
crossing): LEAN (CF:113; review r12 CENSUS-2, the manager's pick). Holes: RULED (CF:80, CF:81). Run-time inputs ("parameters" in CF:84): RULED (CF:84); the
interface rides [IFACE-PUSH]. `&` and `${}` as the only rx additions: RULED (CF:795). `&` in rx text all or nothing by a module or option: RULED
(CF:978-979, CF:981-984); OFF by default: LEAN (manager, CF:986-987; §13 O60); which `&` is the mark under ON
(exactly where `|` means alternation) and the literal `\&` or `[&]`: RULED (CF:1041-1046 on main, rev 13; §13 O60 (d)
CLOSED); the guard's stated scope: LEAN (manager; review r12 CENSUS-5). Rev 13: both operands of `&` filter roles
and a warning on an explicit anchor in an operand: RULED (CF:1054-1062 on main), with the owner's condition met by
THE AMPERSAND RULE TESTED BY POSITION (sensible in every position; `\b`/edge lookarounds stay the error); the
general form of what opens a scoped match: LEAN (review r14 F2, this document), checked against every position; the
warning's name, text and reach: LEAN (§13 O65); `anchored` with exact ends: RULED (CF:1048-1053 on main), its
definition as the `\A`/`\z` text: this document (the filter-role wording differs in a hole, §13 O64).
`${`'s matchable meaning in a class or `\Q...\E`, restored by the rewrite: review r12 CENSUS-4. `${`
always a hole and the `$\{` spelling: LEAN (the manager's pick on review r10 CENSUS-2). Finite-group backreferences as
regular: a general engine row, [BACKREF-FINITE] (RULED, CF:583, predx Q10: not #6). `&` in rx text: §13 C23
RESOLVED.

## 12. Worked examples (acceptance cases)

Each case: the program (placeholder spelling), the capability level it needs, and expected behaviour on a few
subjects. Subjects are searched with PCRE semantics (leftmost, then the left operand's priority) unless the program
anchors. Weekdays, day differences and Luhn results were checked with Python (`datetime.date.isoweekday`, a
hand-written Luhn), not with pcrec; PCRE behaviours (E-IPV4, E-DEPTH, E-FILE, E-CTX) were checked with libpcre2 10.49
by review 2026-11-14-r1-predspec. Libraries are modules (`d := import("dates")`, §7). No §12.1-12.11 case puts an
assertion in a set position, so none of them depends on the Q1 model; §12.12 holds the cases that do.

REV 7 RE-CHECK (review r8; per-case record in `docs/dev/lanes/predspec7_report.md`): all twelve cases are UNCHANGED
token for token. Every comma sits in a call record, a condition record, a `[ ]` array or rx text (§5.4); every `[ ]`
is an array of ordered entries, read as any one entry under `&` (an alternation of names or strings) or in order by
`join` (§3.4, §5.4); every `( ... )` is a call or a condition (none is grouping); no case passes a record as a value
or needs a record on the left of a binding (§0.2); no case uses search (`~`: 0 uses), so the owner's search-result
note (CF:880-887) changes none of them. OPEN items that touch cases without changing their spelling: the module
bindings (`json := import("json")`, E-JSONL, E-IPV4, E-HTTP, E-DEPTH; §13 O46); a condition passed as an argument
(E-HTTP; now stated in §5.4's `( label: S, ... )` row, §13 O45); a computed label read BARE as an operand (E-CAL's
`<=dim`, E-RFC's `==wd`; §13 C13, lean `<=$dim`, `==$wd`); the dot family (E-RFC's `.index`, `$rest.year`; §13 O31).
E-RFC's `$mname.index` now has one parse, `$(mname.index)` (§5.4 `$` row; review r8 P6-6).

REV 8 RE-CHECK (per-case record in `docs/dev/lanes/predspec8_report.md`, EXAMPLES RE-CHECKED): all twelve cases are
UNCHANGED token for token (§12's code lines, comments stripped, are byte-identical to rev 7's; command in the
report). No case uses `~` or `!~` (0 uses each), `occurrences(` (0) or a group question `some(`/`all(` (0; the two
`some(` hits are `@assert.some`), and none has a typed definition head, so the transform ruling and the phase-1 typed
parameter ruling change none of them. What rev 8 changes AROUND them: E-JSONL's `contains("timeout")` is now a member
of the search family (§2.6, §8: its body gains `(?s)`, which changes no expected answer: the case's values have no
line break); E-HTTP's `occurs.exactly`, `occurs.at_most`, `occurs.none` are COUNTS, which `occurs` keeps (CF:913), and
its `name` is a repeated label under §4.3's group questions; the module bindings now have a RULED map interface
(CF:891-892; E-JSONL, E-IPV4, E-HTTP, E-DEPTH; §13 O46 restated); E-RFC's `.index`, `$rest.year` and E-FILE's
`r.word` are instances of the one ruled `.` (CF:892, CF:898-899; §13 O31 narrowed to the metadata collision).

REV 9 RE-CHECK against the ONE READING (its "unchanged token for token" for E-DEPTH stands as text; E-DEPTH's form is
not in the grammar, rev 10 above) (§4.5; per-case record in `docs/dev/lanes/predspec9_report.md`, EXAMPLES
RE-CHECKED). The question for each case: does any condition read an AMBIGUOUS label (two accepting parses giving it
different spans)? If none does, PCRE's reading and rev 8's some-parse answer coincide and no expected answer moves.
Result: NO §12 CASE depends on some-parse; every expected answer is unchanged, and the code lines are unchanged token
for token. The labels conditions read are fixed-width or delimited by a character they cannot contain: E-WEEKDAY,
E-CAL (`\d{4}`, `\d\d`, `-`), E-RFC (`\d{1,2}` then a space; names from fixed lists), E-NEAR (c) (two fixed-width
isodates), E-FILE (`[^,]+` then `,`, `\d+` to the line end), E-HTTP (`name = token`, which has no `:`; `fvalue` holds
no CR/LF, so the `list_of` iterations split at each `\r\n` in one way; predx §3.8), E-CTX-1/7 (`\w` then one space;
the whole `name`), and the agreeing look-alike's `v` (the whole span). E-JSONL, E-IPV4, E-LUHN, E-SEP and E-DEPTH
put no condition on a label (their `&` operands are label-free sets), and E-CTX-2..6 are compile errors. What rev 9
changes AROUND them: E-JSONL's `contains("timeout")` is now `occurrences("timeout", min = 1)` (§2.6), the same set; E-HTTP's
`name` iterations would follow PCRE's parse if `fvalue` could hold a line break (it cannot). §0.1: L34 changes verdict
(DIFFERENT: WARNING -> SAME, both levels read PCRE's parse); L16, L36, L51, L53 restated; L55-L59 new; no other row's
answer depended on some-parse.

REV 10 RE-CHECK IN EACH PROGRAM'S REAL MODE (review r10 SIM-6: every case applied as the program actually runs,
SEARCHED unless the program anchors, not only "whole subject"; per-case record in `docs/dev/lanes/predspec10_report.md`,
EXAMPLES RE-CHECKED). UNCHANGED (searched gives the expected answer because every match is fixed-width or delimited,
so a searched subject has no shorter qualifying span): E-WEEKDAY, E-LUHN, E-CAL (its "whole subject" answers hold
searched too: isodate is 10 characters and so are the subjects), E-RFC, E-NEAR (a)-(c), E-SEP, E-JSONL (anchored by
its own `/^${q}$/m`, line by line), E-FILE (already stated searched), E-CTX-1, E-CTX-7 and the agreeing look-alike
(searched, the reported span is the whole subject), E-CTX-2..6 (compile errors). RESPELLED, ANSWER MOVED AS WRITTEN:
E-HTTP (searched, `Host: a\r\nhost: b` MATCHED the one-header span `Host: a`, where the case expects no match: a
count is not upward-closed; rev 10 anchors the program, `/\A${block}\z/`, and the expected answers are unchanged;
§0.1 L66). ADDED: E-IPV4's searched answer for `01.2.3.4` (`1.2.3.4`, beside the stated `256.1.1.1` -> `56.1.1.1`).
MARKED: E-DEPTH needs the unruled multi-clause definition (§13 O21; review r10 CENSUS-5); E-CAL's `isodate := (as in
12.2)` is now a comment, not a code line. Rev 10's other changes touch no case's answer: `contains` (E-JSONL) gets the
scoped body and exposes `hit` (no condition reads it); no case reads a label inside an optional part of a repeated
group (the per-iteration reading, SIM-2), an argument with a backreference or conditional (SIM-1), a `$` before a
final newline in a filter (SIM-5), or two spellings of one labelled operand (FIXB-1); E-HTTP's `name` loop is always
REACHED (the block is the loop), so the per-match zero-iteration rule changes nothing there.

REV 11 RE-APPLIED UNDER THE ANCHORING RULING, EACH CASE IN ITS REAL MODE (review r12 SIMULATE-1; per-case table in
`docs/dev/lanes/predspec11_report.md`, ROWS AND EXAMPLES RE-APPLIED). The ruling (CF:991-996) changes a case only
where a `^` or `$` stands in a filter no loosening transform wraps. CODE LINES: unchanged token for token. ANSWERS:
unchanged in every case; E-JSONL's `^`/`$` sit in the FINAL pattern (searched, the subject's lines), E-HTTP's
`\A`/`\z` likewise, E-LUHN and E-FILE use `startsWith` (a library call), E-CTX-7's `/^[A-Z][\w-]*/` was already read
as a whole-string set. RESPELLED (prose): E-CTX-1's reason (x must be ENTIRELY `S\w*`; equal to `startsWith("S")`
only because x is `\w+`); E-CTX-5's stated equivalence MOVES (`padded(/^5/)` = `padded("5")`, not
`padded(startsWith("5"))`; the program has no subject and its no-error verdict stands); E-NEAR (c) and E-HTTP's
budget outcomes worded as EXPECTED under the unmeasured ONE budget (review r12 CENSUS-6 (d)). Rev 11's other changes
touch no case: the narrowed second argument refusal (no case passes a backreference to `occurrences`/`contains`), the
selection spelling `$m.hit[(g: "x")]` (no case reads iterations out), `balanced`'s respelling (not a case), the
rx-`&` reading under ON (G3 runs OFF; no case uses rx-text `&`), and the duplicate-in-a-loop rule (no case has
`(?J)`).

REV 12 RE-APPLIED UNDER THE ONE ANCHORING RULE, EACH CASE IN ITS REAL MODE (CF:1011-1020; per-case table in
`docs/dev/lanes/predspec12_report.md`, CONSISTENCY SWEEP). The rule moves an answer only where a `$` in a filter or a
filter's hole can meet a final newline that something after it consumes (rev 11's exact-end `$` is withdrawn), or
where a case would use `anchored`. CODE LINES: unchanged token for token. ANSWERS: unchanged in every case. E-JSONL
(`^`/`$` in the FINAL pattern under `m`, searched line by line, as before; its `contains("timeout")` holds no anchor),
E-HTTP (`\A`/`\z` in the final pattern: the exact ends; the record's suggested `anchored(block)` would ALSO accept a
block followed by one final newline, L68, so the case keeps `\A...\z`), E-FILE (the item rx `/^[^\r\n]*$/m` is
searched in the file text, an "everywhere else" position, as before; `!startsWith("#")` is a gap body), E-LUHN
(`startsWith("4")`, a gap body), E-CTX-1, 5, 7 (a `^` in a filter or a modifier's argument adds nothing, the reason
now the one rule), E-CTX-2, 3, 4, 6 (compile errors; the edge-assertion error is not an anchoring rule, §11),
E-WEEKDAY, E-IPV4 (`/\b${ipv4}\b/` a final pattern), E-CAL, E-RFC, E-NEAR, E-SEP, E-DEPTH (no anchor in a filter) and
the agreeing look-alike. Rev 12's other change (the naming rule; `occurrences` OPEN) touches no case: no case writes
`occurrences` (E-JSONL's `contains` passes the rule).

REV 13 RE-APPLIED (CF:1026-1062 on main; per-case table in `docs/dev/lanes/predspec13_report.md`, CONSISTENCY SWEEP).
CODE LINES: one changes, E-HTTP's final pattern `/\A${block}\z/` -> `anchored(block)` (the record's own suggestion,
CF:1015, now exact: one text, the same answers). ANSWERS: unchanged in every case. No case writes an anchor in an `&`
operand's own text (E-HTTP's `&` operands are `headers` and the counts; E-JSONL's and E-IPV4's anchors sit in final
patterns; E-FILE's `^`/`$` in the searched item rx), so `anchor.operand` fires in none; E-CTX-1 and E-CTX-7 (an
anchor in a `label:` condition) and E-CTX-5 (in a modifier's argument) would draw it only if the owner extends it
(§13 O65). No case uses `search`/`occurrences` by name (E-JSONL's `contains` is `occurrences(x, min = 1)`), nor
rx-text `&`.

THE TWO-WAY CENSUS (G0b; review r8 P6-9, OWNER-12). G1's check runs case -> construct (every case uses only §§2-8);
this table runs construct -> case. Counts are uses in §12's code lines, comments stripped (command in
`docs/dev/lanes/predspec7_report.md`; rev 8's re-run: `docs/dev/lanes/predspec8_report.md`). A construct with no case is LISTED, not cut and not given an invented case:
the owner decides which stay in phase 1 (§0.2).

| construct | §12 cases that need it | if none: why it is carried |
|---|---|---|
| `&`, `\|`, prefix `!`, `:=`, `,`, `[ ]`, `( )` call/condition, `=`, `:` in a condition, `.`, `$x`, `${}`, comparison sets, `-`, `/.../` | all twelve between them (§5.4's MARK TABLE names the cases per mark) | |
| `@assert`, `import`, `param`, `enumerate`, `records`/`file_text`, `each`, `join`, `list_of`, `occurs.*` | E-IPV4, E-CAL, E-CTX; E-JSONL, E-IPV4, E-HTTP, E-DEPTH; E-NEAR; E-SEP; E-FILE; E-FILE, E-SEP; six cases; E-HTTP; E-HTTP | |
| `count(...)` | none in code (E-HTTP's prose only) | the first spelling: LEAN (CF:823, "perhaps"); its budget refusal RULED (CF:832); a count is a numeral string RULED (CF:977-978) (review r10 FIXA-6) |
| operator section `(& f)` in code | none (prose only, §5.2, §5.3) | RULED, IN phase 1 (CF:753) |
| the `occurrences` transform (rev 7's `~`, `!~`: withdrawn) and its `min` setting | none (E-JSONL's `contains` is `occurrences(x, min = 1)` by definition, rev 9) | CF:907-909 (accepted at CF:905); its group questions phase 1 (CF:922-924); `min`: CF:933-934, CF:960; whether a case is wanted: the owner's (§0.2) |
| `some(...)`, `all(...)` | none (the two `some(` hits are `@assert.some`) | CF:912-914 (accepted at CF:905; `some()` is his own question, CF:904-905) |
| `contains(...)` | E-JSONL | standard library (§8) |
| `anchored(...)` | E-HTTP (rev 13) | standard library (§8); RULED (CF:1005, exact ends CF:1048-1053 on main) |
| positional `X[...]` | none | RULED (CF:553); the owner's search example reads one iteration by it (`$m.hit[2]`, §2.6), at the `captures` level (LEAN) |
| `where`, `where_group`, `each_group` | none | LEAN (§3.2, §5.3); candidate cut |
| `when(c, p)` | none | RULED (CF:184, "Add when") |
| typed parameters `m(x: T)`, `pure`, `pattern()` | none | OUT of phase 1 (CF:889); in the design for "more thinking"; §13 O48 |
| `eval` | none | LEAN (§10); an opt-in module |
| `@export`, `@warn` | none (library files are not cases) | LEAN (CF:608, CF:619); warnings RULED (CF:666); effect built-ins (§5.1) |
| multi-clause definition (a literal in a head, two `:=` for one name) | E-DEPTH | NOT IN THE GRAMMAR (§5.2 heads declare names and defaults; §13 O21); E-DEPTH is marked as needing it (review r10 CENSUS-5) |
| `+` | none | RULED (CF:782 (1), "\d+ numbers can be added", his words; §2.5); listed in rev 11 (review r12 CENSUS-7: carried without a case and not listed) |
| `*`, `%` | none | LEAN (the manager's reading of CF:782 (1), whose words name addition only; review r10 FIXA-6) |
| `.label` | none | LEAN (§5.3); §13 O31 |
| record on the left of `:=` | none | RULED in the design (CF:852); OUT of phase 1 (§0.2) |

### 12.1 E-JSONL: flat JSONL, date range + string match (key-order independence)

    json  := import("json")    # ws, jchar, quoted, num, value, member_any, member(k, v), row(k, v)
    dates := import("dates")
    q := json.row("ts",    json.quoted(dates.isodate & between("2024-01-01", "2024-03-31")))
       & json.row("level", json.quoted("error"))
       & json.row("msg",   json.quoted(contains("timeout")))
    /^${q}$/m

`row(k, v)` aligns one member to the member grid; `&` of three rows accepts the members in any order. `json.quoted`
is the JSON-string filter modifier (§2.7): `json.quoted(p)` is the filter p changed to read a JSON string literal as
its decoded text (rev 2's `json.jstr & p` pipeline is superseded). Quoted literals compare as strings; fixed-width
ISO dates order correctly that way. `^`/`$` sit in the FINAL pattern and read the subject's lines (§11); `q` holds no
assertion. LEVEL: default (every binding is pure; cost = the product of the `row` automata). Expected:
- `{"ts":"2024-02-10","level":"error","msg":"db timeout"}` -> match;
- `{"msg":"timeout","level":"error","ts":"2024-02-10"}` -> match (order independent);
- `{"ts":"2024-05-01","level":"error","msg":"timeout"}` -> no match (date out of range).
Duplicate keys: `row` holds if ANY member with that key matches. Nesting: §12.11 or `vm`.

### 12.2 E-WEEKDAY: ISO date + weekday as a computed label

    isodate := join([year  = /\d{4}/,
                     month = /\d\d/ & padded(between(1, 12)),
                     day   = /\d\d/ & padded(between(1, 31))], sep = "-")
    weekday := weekday_of($year, $month, $day)     # match-dependent binding: a computed label of isodate
    isodate & (weekday: 6)                         # ISO numbering assumed: Monday = 1

LEVEL: default (regular: ~14 year states after the 4th digit, month as an offset mod 7, day in 7 classes; on the
order of a hundred minimal states, unmeasured); output = span + the weekday class (§6.2). Expected: `2026-11-14` ->
match (Saturday); `2026-11-13` -> no (Friday); `2024-02-29` -> no (Thursday). Weekday value type: §13 O7.

### 12.3 E-IPV4: real octet ranges

    octet := /\d{1,3}/ & between(0, 255)       # canonical numerals only: "01" excluded
    ipv4  := join([octet, octet, octet, octet], sep = ".")
    assert := import("assert")
    @assert.some("192.168.1.17" & ipv4)
    @assert.none("01.2.3.4" & ipv4)
    ipv4

LEVEL: default. Expected (whole-subject test): `192.168.1.17` in; `256.1.1.1` out; `01.2.3.4` out (canonical rule;
`padded(between(0, 255))` admits it, a stated library choice). As a SEARCHED program (its real mode: no anchor),
`256.1.1.1` yields `56.1.1.1` and `01.2.3.4` yields `1.2.3.4` (held under Python's `re` on the octet pattern, rev 10); a boundary is the user's to write, in the final pattern around the hole: `/\b${ipv4}\b/` on
`256.1.1.1 and 10.0.0.1` finds `10.0.0.1` only (the `\b` belong to the final pattern, not to the hole's set, §11).
The assertions run at compile time and are decided on strings (§5.6).

### 12.4 E-LUHN: checksummed card numbers

    card := /\d{4}(?: ?\d{4}){3}/ & luhn & startsWith("4")
    card

`luhn` (weighted digit sum mod 10) is REGULAR (~20 states), a filter declaring its regular twin; IBAN mod 97 and
ISBN-10 mod 11 are the same class. The literal keeps its space (no implicit x-mode, §11). LEVEL: default. Expected:
`4111 1111 1111 1111` -> match; `4111 1111 1111 1112` -> no (Luhn fails); `5500 0000 0000 0004` -> no (Luhn valid,
fails `startsWith("4")`). Whether `luhn` skips the spaces: §13 O8.

### 12.5 E-CAL: calendar validity (a relation between labels)

    # isodate as in 12.2
    dim   := days_in($year, $month)             # computed label: 24 classes (12 months x leap)
    valid := isodate & (day: padded(<=dim))
    @assert.some("2024-02-29" & valid)
    @assert.none("2023-02-29" & valid)
    valid

A value-vs-value relation with class count 24 (§4.6): one automaton. `days_in` is a value macro whose parameters
are the two captured strings; the leap test (`$year & leap`) sits inside it, so no rx is called with an operand
(§2.3; rev 4 wrote `days_in($month, leap($year))`, which called the rx `leap` with the operand and used its result
as a truth value). `<=dim` reads the computed label BARE: §13 C13 (lean `<=$dim`; review r8 SIM-8). LEVEL:
default. Expected (whole subject):
`2024-02-29` in; `2023-02-29` out; `2024-04-31` out; `2024-13-01` out (not an isodate). The notes' `month: \d\d &
between(1,12)` is WRONG (only 10, 11, 12 pass): C9, confirmed CF:774; `padded` is the fix (§0.1 L20).

### 12.6 E-RFC: weekday consistency

    month_abbrevs   := ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    weekday_abbrevs := ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    textdate := join([day = /\d{1,2}/, mname = month_abbrevs, year = /\d{4}/], sep = " ")
    month    := $mname.index                    # computed label of textdate (1-based index = month number)
    rfcdate  := join([wname = weekday_abbrevs, rest = textdate], sep = ", ")
    wd       := weekday_of($rest.year, $rest.month, $rest.day)
    rfcdate & (wname.index: ==wd)

LEVEL: default (a 7-class relation). Expected: `Sat, 14 Nov 2026` -> match; `Fri, 14 Nov 2026` -> no. The note's
`wd := weekday(rest)` assumes a member on a `date` type (cut, §9); the plain macro on the fields is this document's
rewrite. `month := $mname.index` is this document's rewrite of rev 0's `with month = mname.index` under §4.4 (the
same mapping as the `month_numbered` modifier, §2.7; family note, §13). `==wd` vs `==$wd`: §13 C13.

### 12.7 E-NEAR: date within 15 days of another (three anchor cases)

    near_const := isodate & within(15, of = "2026-11-14")            # (a) compile-time constant
    anchor     := param(isodate)                                      # (b) caller-supplied at run time
    near_param := isodate & within(15, of = anchor)
    pair       := join([a = isodate, b = isodate], sep = /\s*,\s*/)   # (c) both dates in the subject
    d          := days($b) - days($a)
    close      := pair & (d: between(-15, 15))

(a) a 31-literal set (2026-10-30 .. 2026-11-29); LEVEL default. `2026-11-29` in, `2026-11-30` out. (b) a
computation on a run-time input only (anchor +- 15 days, once per match) and a parametric comparison: LEVEL default
(§6.1). (c) a relation with ~3.65M classes (§4.6): at the default level REFUSED when the count is over the ONE measured
budget (RULED, CF:977; the budget is unmeasured, so the refusal is the EXPECTED outcome, not a fixed one: review r12
CENSUS-6 (d)), the error printing the count and naming `functions`; under `functions` a linear arithmetic check on DFA-validated candidates. `2026-11-01,
2026-11-14` -> match (13 days); `2026-11-01, 2026-12-01` -> no (30 days).

### 12.8 E-FILE: file literals and CSV records

    lines := /^[^\r\n]*$/m                                        # named item rx; no hidden default  
    alts  := records(file_text("w.txt", sha256 = "<pin>"), lines)
             & !startsWith("#") & !"" & length(<=20)              # any order: & is pure intersection
    rows  := records(file_text("w.csv", sha256 = "<pin>"), /^(?<word>[^,]+),(?<w>\d+)$/m)
    word_of(r) := r.word
    heavy := each(word_of, rows & (w: >100))
    alts | heavy

LEVEL: default; nothing happens at match time. Expected, with `w.txt` = `# words`, `foo`, `foobar` and `w.csv` =
`apple,150`, `pear,90`: `alts` = `foo|foobar` (file order), `heavy` = `apple`. Searching `foobarbaz` reports `foo`
(sort is semantics). The item rx is searched in the file text (its `^`/`$` read the file); the items are one-string
rx. A BLANK LINE inside `w.txt` gives an empty item (without `& !""` the final pattern is nullable and the
searched program is an error, the `empty.search` hazard, §7); a TRAILING newline gives none (PCRE2's multiline `^`
does not match after a final newline; Python's `re` differs). A CRLF line `foo\r\n` is not matched at all by `lines`,
so the tiling error names the whole range `foo\r\n`, not just the `\r`. NOT YET A VALID ACCEPTANCE CASE: the `\n`
terminators belong to no record, so under the tiling rule as written E-FILE is itself a tiling error until O20
says how an item rx declares its separators (§13 O20). A changed `w.txt` under its pin is a compile error.

### 12.9 E-HTTP: header block with occurrence counts

    occurs := import("occurs")
    header := join([name = token, value = fvalue], sep = ":")    # token, fvalue as in predx §3.8
    headers := list_of(header, sep = /\r\n/)
    block := headers & occurs.exactly(1, (name: any_case("Host")))
                     & occurs.at_most(1, (name: any_case("Content-Length")))
                     & occurs.none((name: any_case("Transfer-Encoding")))
    anchored(block)

ANCHORED (rev 10, review r10 SIM-6): the counts are about the WHOLE block, and a count filter is not upward-closed,
so a SEARCHED `headers & occurs...` would report a shorter span that passes (`Host: a\r\nhost: b` -> `Host: a`;
§0.1 L66). `anchored(block)` (rev 13; rev 10-12 wrote `/\A${block}\z/`, the same text since `anchored` has the exact
ends, CF:1048-1053 on main, §0.1 L68) is the FINAL pattern, and its `\A`/`\z` read the subject's ends. `name` is a
repeated label: a bare `$name` would be an error (§4.3). Each `occurs` filter is a capped counter (n+2
states: 3, 3, 2) multiplied into the loop. The condition is passed as a parenthesised literal (a required positional parameter, C31 RESOLVED 2026-11-14); the
labelled-argument spelling `occurs.exactly(1, name: ...)` is not used.
The `count()` spelling (§8) is the same test: `n_host := count((name: any_case("Host")))` and `headers & (n_host:
==1)` inside the anchored block; at these bounds (a capped counter of a few states) it is EXPECTED to fall within the
ONE measured budget and is then accepted (the budget is unmeasured; review r12 CENSUS-6 (d)); the compiler may
recommend the `occurs` form.
LEVEL: default. Expected (the subject is the block): a block with one `Host:` line and no `Transfer-Encoding` ->
match; two `host:` lines -> no (`any_case`); `Host: a\r\nTransfer-Encoding: chunked` -> no.

### 12.10 E-SEP: the same separator twice (a finite backreference, regular)

    date_sep(s) := join([year = /\d{4}/, month = /\d\d/, day = /\d\d/], sep = s)
    dates := each(date_sep, enumerate(/[-\/.]/))      # 3 entries, class members in codepoint order: - . /
    dates

LEVEL: default (PCRE's `\d{4}([-\/.])\d\d\1\d\d` needs `vm` in the strict subset; §13 O34). Expected: `2026-11-14`
-> match, `.index` 1; `2026.11.14` -> match, `.index` 2; `2026/11/14` -> match, `.index` 3; `2026-11/14` -> no. Over
budget (`enumerate(/\w+/)`) is a compile error giving the count.

### 12.11 E-DEPTH: bounded recursion (JSON nested at most k deep)

    json := import("json")
    value_depth(0) := json.scalar
    value_depth(k) := json.scalar | /\[(?:${value_depth(k - 1)}(?:,${value_depth(k - 1)})*)?\]/
    value_depth(3)

`k` is a literal at every call and strictly decreases, with a literal base case (§7); objects elided. LEVEL:
default (a few hundred states for k = 3, unmeasured). `json.value` itself (unbounded recursion) needs `vm`.
Expected: `[[1]]` -> match; `[[[[1]]]]` -> the whole subject is not a `value_depth(3)` (the searched program finds an inner
`[[[1]]]`). NOT YET WELL-FORMED (review r10 CENSUS-5): the two heads hold a literal and bind one name twice, a
MULTI-CLAUSE definition the grammar does not have (§5.2: a head declares names and defaults; §5.1: one binding per
name); the alternative `value_depth(k: 0)` is the phase-1 head error (L49). The case needs the unruled form of §13
O21; no new grammar in rev 10 (the manager's pick).

### 12.12 E-CTX: assertions in set positions (the cases that decide Q1)

Each case puts an assertion where the three candidate models (§11) disagree; the answer is the RULED one (string
sets, `^`/`$` = the filtered span's ends, the edge-assertion error for `\b` and edge lookarounds; CF:761; rev 12:
THE ONE ANCHORING RULE, CF:1011-1020, the same answers). E-CTX-1, 5
and 7 do not error; E-CTX-2, 3, 4, 6 do. The answers under the other models are review Q1X-2's table. LEVEL: none applies
(compile errors).

    P := /(?<w>\w) (?<x>\w+)/
    P & (x: /^S\w*/)                                  # E-CTX-1, subject `a Sab`
    num := /\b\d+\b/
    /a${num}/                                         # E-CTX-2, subject `a12`
    @assert.none("5" & /(?<=\$)\d+/)                  # E-CTX-3
    /\w{3}/ & /\w+\b/                                 # E-CTX-4, subject `foobar`
    x & padded(/^5/)                                  # E-CTX-5
    enumerate(/(?<=a)[bc]/)                           # E-CTX-6
    headers & (name: /^[A-Z][\w-]*/)                  # E-CTX-7 (§12.9's headers), `Host: a` / `Host: a\r\nAccept: b`

- E-CTX-1: NO error; the filter is anchored at both ends of x, so x must be ENTIRELY `S\w*` (its `^` is x's start
  and adds nothing): `a Sab` -> match `a Sab`. Here the answer equals `(x: startsWith("S"))`'s only because x is
  `\w+`; in general the two differ (§0.1 L7; rev 11, review r12 SIMULATE-1). (A/B2: silent no match; B1: match.)
- E-CTX-2: compile ERROR (`\b` at both edges of the hole's set). Fix: write the boundaries in the literal around the
  hole, `/a\b${/\d+/}\b/`, which says what the pasted text says: on `a12` it finds nothing (`a` and `1` are both
  word characters). (B1: match, unlike the pasted text.)
- E-CTX-3: compile ERROR (a lookbehind at the start of an assertion argument). Under A the assertion FAILED although
  the subject `5` never matches. Fix: assert on strings without the lookbehind (`@assert.some("5" & /\d+/)`); what a
  searched program finds is shown by an example subject, not by an assertion (§5.6, §13 O36).
- E-CTX-4: compile ERROR (`\b` at the end of an `&` operand). Fix `/\w{3}\b/`: on `foobar` it reports `bar` visibly,
  from the final pattern. (A/B2: the reported match silently moves from `foo` to `bar`.)
- E-CTX-5: NO error; the modifier's argument is anchored at both ends of the span `padded` reads, so `padded(/^5/)` =
  `padded("5")` (`5`, `05`, ...). It is NOT `x & padded(startsWith("5"))`, which also accepts `57` (§0.1 L13; rev 10
  said "same", review r12 SIMULATE-1: the stated equivalence MOVES, the program and its no-error verdict do not).
- E-CTX-6: compile ERROR (a lookbehind at the start of an `enumerate` argument). Fix `enumerate(/[bc]/)` = `["b",
  "c"]` and put `(?<=a)` in the final pattern.
- E-CTX-7: NO error; `^` is the start of each `name` value: both subjects -> match, same as `(name: /[A-Z][\w-]*/)` (a
  set is matched ENTIRELY). (A/B2: the one-header block matches, the two-header block silently
  fails, and adding `m` to the condition flips it; review Q1R-4.)
Agreeing look-alike (no error): an assertion strictly inside a value, `/(?<v>[\d.]+)/ & (v: /\d+\b\.\d+/)` on
`3.14` -> match (the `\b` reads only characters of v).

## 13. Open questions and contradictions

Contradictions (C) are places where two notes, or a note and a ruling, give different readings; open items (O) are
places the notes leave silent or explicitly open. Each gives both readings; none is resolved here except by a
recorded ruling, cited.

RESOLVED (one line each; the rule now stands in the section named; RULED marks cite the record):
- **C1** `&` order: RULED (CF:732), §2.2, §0.1 L39. **C2** x-mode: RULED (CF:577), §11. **C4** guard holes: RULED
  (CF:573), §11. **C11** purity vs ambiguity: RULED (CF:583, Q2), RE-RESOLVED in rev 9 by the one reading (CF:953-955), §4.5. **C14** size-cap fallback: RULED (CF:583,
  Q5), §6.1. **C20** application: RULED (CF:749), §2.3. **C22** the pipeline under `name:`: RULED (CF:698, CF:706),
  §4.1. **C24** `ci`: RULED (CF:722, `any_case`), §2.7.
- **O4** (CF:583, Q4), **O9** (Q5), **O11** (Q7, 1-based), **O18** (Q13, tiling), **O25** (CF:713, string sets): RULED,
  §4.3, §6.1, §3.2, §7, §11.
- **C6** binding a test (rev 5): the 2026-11-13 "a TEST is an error" was corrected the same day: a test IS a pattern
  and may be bound and inserted (CF:81, Frank's correction; CF:117: one kind of binding, tests sit beside patterns),
  §5.1.
- **C8** comma in records vs lists: RULED (CF:698), RESTATED by the type picture (rev 6, CF:863): the comma means
  only "next entry" in both; the BRACKET says how entries relate (`( )` all together, `[ ]` any one); answers
  unchanged, §5.4, §0.1 L23.
- **C19** the kind of an assertion (rev 6): RULED (CF:858): two value kinds, so an assertion is not a value kind.
  That `@` forms are EFFECTS (statements, §2.1 kind table, §5.6): LEAN (CF:619; CF:858 has no `@`, review r8
  RUL-10). Whether one can be NAMED: C18.
- **O30** brackets and commas with opposite meanings (rev 6): RULED (CF:863): the comma has one meaning and the
  bracket carries the relation, so `(x: <200, y: >55)` vs `[(x: <200), (y: >55)]` differ by the bracket alone (L23);
  `x[[1, 3, 5]]` vs `x & [1, 3, 5]` differ by the TOOL (position vs language, §3.2), both brackets reading any one.
  The review's lean "tuples by name" is overtaken (a record is never a value, CF:866); the tuple question is C25.
- **C9** padded labels: RULED (CF:573), CONFIRMED (CF:774): string sets, `\d+`, explicit `padded`, §2.4.
- **C10** transform sections and the left of `:`: filter modifiers (RULED, CF:722) and computed values via
  match-dependent bindings (concept RULED, CF:595), §2.7, §4.4.
- **C15** in-context vs value-scoped `&`: the model RULED (CF:713, CF:761: string sets; `^`/`$` = the filtered span's
  ends; reading beyond it refused), §11. `&` inside `/.../` text: C23.
- **C21** `count` as a value (rev 5): `count(...)` yields a number used like a subject number, LEAN (CF:823,
  "perhaps"); refused only over the budget with `occurs` named, RULED (CF:832); the 11-14 "NOT a count value (no
  number type)" is withdrawn (CF:782 (3)), §8. `some`/`all`/`count` as built-ins or library names: lean library
  (prelude) names (rev 8, §4.3, §8).
- **C27** context-marked sets vs "matches ENTIRELY": RULED (CF:713): a set is the strings it matches entirely; `^` in
  a filter is the filtered span's start (CF:761), §11.
- **C30** what a positional argument is: RULED (CF:732, CF:749): positional = required parameters, keywords =
  optional settings, any parameter by name, §5.2.
- **C31** `occurs` conditions: RULED (CF:732): a parenthesised literal, `occurs.exactly(1, (name: any_case("Host")))`,
  §8, §12.9.
- **C32** `^`/`$` and edge assertions in a filter: RULED (CF:732), CONFIRMED and stated by the owner (CF:761): `^`/`$`
  mean the start and end of the span being filtered; `\b` that would read beyond it is refused, §11.
- **C33** operator sections (rev 5): RULED (CF:753, "start with &"): sections start with `&` only (`(& f)`, the
  operand on the left; `(& !B)` covered); other operators on need, §5.2.
- **C34** partial application (rev 5): RULED (CF:753, "start no"; CF:804): phase 1 has none (a call binds every
  required parameter or is an error naming the missing one; sections are the one way to leave a hole); the DESIGN
  keeps currying (CF:308) for after phase 1 (Reading A of rev 4 is the later design, Reading B the phase 1 build),
  §5.2, §0.2.
- **C35** `(?m)` inside a value (rev 5): RULED (CF:753, "agree"): an explicit `(?m)` keeps PCRE meaning inside the
  span (line breaks within it); without it `^` is the span's start and `$` its end or the point just before a final
  newline of the span (rev 13, review r14 CENSUS-4); never reads outside, §11.
- **O17** D196's F7 in-context lookaround: RULED for set positions (CF:713, CF:761 (3): an assertion that would read
  beyond the filtered span is refused; final patterns keep PCRE meaning; the 2026-11-13 span-context understanding,
  CF:56, is restored for `^`/`$`), §11. `\K` refused; verbs, cross-operand backrefs (finite: `enumerate`; general:
  [BACKREF-FINITE]), recursion remain as listed in rev 2.
- **O23** the `occurs` namespace name (rev 5): RULED in use (CF:782: "use 'occurs' module like occurs.at_least(3,
  ...)"; "i suggested an 'occurs' type module that would handle structural predicates").
- The call form `isodate(year: S)` and the labelled-argument addendum: WITHDRAWN, RULED (CF:744), §4.1, §5.2.
- Review RUL-4 (right-associative `&` vs the chain label lookup): dissolved by OWN-1 (pure `&`), §4.1. Review RUL-10:
  answered by CF:706 (labelled arguments always narrow), §5.2.

- **C28** `occurs.all` vs the sequence rule (rev 8): RESOLVED by the transform ruling (CF:912-913, accepted at
  CF:905): `occurs` keeps the COUNTS only, so `occurs.all` (and `occurs.some`) leave; `all((x: S))` is the plain
  condition, the default, rarely written (§0.1 L36 SAME). Removed rather than aliased: LEAN. Zero iterations: both hold (rev 9, §4.2).
- **O12** `!~` (rev 8): RESOLVED: WITHDRAWN with `~` (CF:909, accepted at CF:905); the negated test is
  `!contains(rx)` (§2.6). L51 is restated on `!occurrences(r)` vs `!contains(r)`.
- **O29** does each `some` pick its own occurrence (rev 8): RESOLVED by SAME HIT BY RECORD (CF:915-917, accepted at
  CF:905): one record = one iteration (`some((g: x, h: 1))`), two calls = possibly different iterations (`some((g: x))
  & some((h: 1))`); the rev 2 rule "every `some(s)` over the same set denotes the same occurrence" is REPLACED. This is
  the review's OWN-6 lean, now accepted. §4.3, §0.1 L31.
- **O48** for PHASE 1 (rev 8): RESOLVED by the owner's reading (C): typed parameters are OUT of phase 1 (CF:889: "yes
  keep out of phase 1"), so `:` narrows only in phase 1 (§5.2, §5.4, §0.1 L49). In the design, O48 stays open below.
- **C36** the priority parse vs some-parse (rev 9): RESOLVED by the owner (CF:950, "I think it will help if our rx is
  consistent", answering the manager's note (a), CF:941-944; record CF:953-955): ONE READING, PCRE's, for a condition
  on ANY label, set once or in a loop. This is broader than rev 8's three readings ((A) some-parse everywhere, (B)
  PCRE's parse for repeated labels only, (C) for `occurrences` only): the some-parse rule (CF:583, predx Q2) is SUPERSEDED
  for every label. Its cost is the owed measurement O57. §4.5, §2.6, §4.3.
- **O33** two conditions on an ambiguous pattern (rev 9): RESOLVED by the one reading (CF:953-955): both conditions
  read PCRE's one parse, so `/(?<a>\d+)(?<b>\d+)/ & (a: <5) & (b: <5)` on `123` is FALSE (a = `12`) at every level;
  merged narrowing is no longer a separate rule. §4.5, §0.1 L34.
- **O54**, the `d :=` half (rev 9): RESOLVED (CF:929): a name bound to a transform's result binds the transformed rx
  (`hits := occurrences(r)`, applied as `(m: hits)`). The record-on-the-left half stays open below. §2.6.
- **O28**, the zero-iteration half (rev 9; RE-RESOLVED in rev 10): rev 9 listed it RESOLVED on the record's
  reading (CF:937-940) of the owner's hedged "+ or * control" (CF:933), too thin a footing (review r10 FIXB-8), and
  its statement by the label's own quantifier flipped on a `+` in a branch never entered (FIXB-2). Now RULED BY
  ACCEPTANCE (CF:997-1000 on main, "Agree with lean"; rulings R-1): decided PER MATCH, a condition on a label FAILS
  when the match never reached the label's group or loop (`/x|(?<n>\d)+/ & (n: <5)` on `x`), and a loop REACHED and
  run zero times satisfies a plain condition (`/(?:(?<n>\d),)*/` on the empty span); the quantifier (for `occurrences`,
  `min`) decides whether zero is allowed. Rev 8's lean (fail) withdrawn. The rest of O28 stays open below. §4.2,
  §4.3, §2.6, §0.1 L36, L55, L56, L65.
- **C23** `&` in rx text (rev 10): RESOLVED by the owner (CF:978-979: "5. no. I thought we were going to add & to pcre
  but conditionally with a module or option? Also, fully yes or no. If no put the whole rx in the hole. Like ${// &
  blah}"; record CF:981-984): `&` in rx text is ALL OR NOTHING by a module or option; ON, the intersection everywhere
  in the rx text; OFF, PCRE's literal everywhere, the intersection written in the expression language with the whole
  rx in a hole. Rev 9's lean (reading A, `&` an operator only before `${`) REJECTED. Its default, which `&` is the
  mark under ON, and the literal spelling: O60. §11. (Rev 10 also listed C23 under STILL OPEN; rev 11 lists it here
  only, review r12 CENSUS-6 (c).)
- **O39** the budgets (rev 10): RESOLVED (CF:977, "3. agree", to CF:974-975): ONE measured budget for "too many
  classes" and the `count()` refusal, no fixed thresholds in the spec. §4.6, §8.
- **O40** what is a number (rev 10): RESOLVED (CF:977-978, "4. agree. Allows "even()" or other checks for count", to
  CF:975): a count is a canonical numeral string, no new value kind, so ordinary filters apply; inserted in a hole it
  is its canonical numeral; against a padded subject number the explicit `padded` applies (§2.4). §2.1, §4.3, §8.
- **O49** one span per filter role (rev 10): RESOLVED BY ACCEPTANCE (CF:990, "Your examples make me agree", record
  CF:991-996): filters are anchored at both ends; `contains`/`occurrences` remove that; `^`/`$` in their argument are the
  ends of the span being filtered, `contains(/^err/)` = starts with `err`. The alternative (filters unanchored as in
  PCRE) REJECTED by his `31` example. Other macros' arguments and holes follow the same "ONE rule" (LEAN). §11, L17.
  REV 12: RESTATED by THE ONE ANCHORING RULE (CF:1011-1020, accepted at CF:1006): no transform removes anchoring (the
  bodies are plain gaps), a hole's `^`/`$` are the scoped match's as plain PCRE gives them, so one span per filter
  role is a consequence, not a rule; `$` is PCRE's (L63).
- **O50** what a search result is at match time (rev 10): its last open part, the LEVEL of one-iteration access, is
  RULED (CF:977, "1. agree", to CF:972-973): reading ONE hit needs captures, a higher level with its cost shown;
  count/some/all in phase 1. (Rev 9's (c), "a search never rejects", holds for the default `min = 0` only; `min = 1`
  rejects, review r10 FIXA-11 (b).) §4.3.
- **O58** `min` above 1 (rev 10): RESOLVED (CF:963-964, "1. yes. Keep the wording and we can adjust later"; record
  CF:965-969): reading (A), `min` is 0 or 1; the compile error for other values is the manager's reading (LEAN). `max`
  stays out for now (CF:951-952). §2.6, L57.
- **O59** where `label.ambiguous` fires (rev 10): RESOLVED (CF:964, "2. agree"): reading (A), only for ambiguity in the
  author's OWN pattern text; a library body states and tests its own reading. §4.5, §7.1.

STILL OPEN (contradictions):
- **C3. DEFINE bindings in the inner direction.** 2026-11-13 evening: an opted-in DEFINE holds `name := ...` bindings.
  2026-11-14: DEFINE stays ONLY as PCRE syntax inside a literal; API callers keep the inner direction (`(\d+)&${ <256
  }` with the rx-`&` switch ON, §11; inside a longer literal grouped, `(?:(\d+)&${<256})`, §0.1 L67). Reading A: inner-direction patterns have holes but no bindings. Reading B: inner-direction DEFINE keeps `:=`.
- **C5. Multi-index comma.** 2026-11-14 00:10 (a manager lean): `A[1,3,5]` NOT adopted, comma kept for `A[i, j]`;
  the `[]` positional note lists `X[1,3,5]` as valid. Rev 6: NARROWED by CF:863, which names "a multi-index if
  adopted" under the array bracket: IF adopted, `X[1, 3, 5]` = `X[1|3|5]` (any one of those positions, result an
  array keeping the original positions), and the comma can no longer be a dimension separator (`A[i, j]` would make it
  carry logic; write `A[i][j]`, as `d[1][1]` already does). Still open: whether to adopt the multi-index at all.
  Lean: adopt (it costs no new rule; `X[[1, 3, 5]]` then reads the same).
- **C7. Value-valued maps.** 2026-11-13 `["US" => "United States"]`; 2026-11-14 views: labels are names, the value
  per branch shown is `.index`. Reading A: other values are computed labels (now bindings, §4.4) or record arrays
  (predx C7). Reading B: `=>` survives. Rev 8: reading B creates a MAP as a value, which the owner rules out ("Array
  and map are interfaces ... interfaces aren't themselves values that can be created", CF:890-891), unless `=>` only
  WRITES an rx whose entries carry a computed label (then it is reading A's form with a new mark). Lean: A (this
  document's consequence of CF:890-891); the item stays listed because the owner has not seen it in these terms.
  REV 9: reading A is the MANAGER'S CALL (LEAN, manager): the `=>` lookup-table spelling is DROPPED in favour of
  computed labels (§4.4: `country := names_of($code)`-shaped, a mapping that must be a function).
- **C12. Define-before-use.** 2026-11-13 BLOCK SHAPE: required; 2026-11-13 evening: forward references allowed, no
  cycles. Bounded recursion (§7) needs a self-reference at least.
- **C13. Bare label names as values.** 2026-11-13 NAME RESOLUTION: an undeclared bare name is a label; 2026-11-14
  01:00: values always `$x`. `(wname.index: ==wd)` (E-RFC) and `(day: padded(<=dim))` (E-CAL) use a bare computed
  label as an operand while `(b: >$a)` uses `$` (§0.1 L37); rev 5's tuple `lex_ge([major, minor, patch], ...)` did the
  same with plain labels (§8). Review OWN-11's lean: computed labels follow labels, `x:` to constrain, `$x` to read (so `==$wd`).
- **C16. Precedence example.** D196 (`&` tighter than `|`) parses the 00:10 example `x & <256 | >300` (CF:251) as
  `(x & <256) | >300`, silently WIDENING the program; WITHDRAWN (LEAN, review RUL-15): write `(x: <256 | >300)`
  (§4.1); a `precedence.section` warning is PLAN (§0.1 L22).
- **C17. `&`'s structure.** `&` is extensional (§2.2) yet distributes over array entries and drops empty products
  (§3.2), a structural effect (`/a|b/ & /b|a/` gives [a, b] or [b, a] by which side is major). predx C17/S15
  proposes "left-major cross product", which would give the ORDER of an `&` chain a structural effect against the
  ruled "order- and grouping-free" (CF:722). `.index` after `&` with an array of filters (§3.5) depends on it. (Rev 7
  tied the owner's search example here; in rev 8 his `d & (g: x)` is a selection over a repeated label's ITERATIONS,
  at the `captures` level, §4.3, which keeps their match order and positions by definition, so it no longer depends
  on C17. Rev 11 spells it `$m.hit[(g: "x")]`, a selection in the label path, not an `&`, review r12 CENSUS-1.)
- **C18. Named assertions vs the `@` rule.** Named failures via `leap_1900 := assert_none(...)` (CF:595); the `@`
  lean (CF:619): effects cannot drop `@`, only `@` forms are bare statements. A named assertion is then
  `leap_1900 := @assert.none(...)` (an `@` inside an expression), a binding without `@`, or not allowed. Rev 6: a
  binding names an rx or a macro (CF:858) and an assertion is neither (C19), so the binding readings are out. Lean: a
  name is a labelled entry of the assertion's call record, `@assert.none("1900" & leap, name = "leap_1900")`.
- **C25. Tuple comparison arrays.** `lex_ge([major, minor, patch], [1, 4, 0])` (CF:648). RULED from CF:644: "a library
  macro, no syntax". Rev 6 closed the array spelling on a false reason (that a `[ ]` has no order; review r8 P6-2):
  a `[ ]` has ordered entries that structural tools read in order (§3.4, §5.4; `join` does exactly this), and a
  record is never a value only as a RECORD (CF:866), which an array is not. The real defect of the rev 5 spelling is
  its bare label names used as values (C13). BACK TO OPEN between: (A) a STRUCTURAL library macro over two arrays,
  `join`-like, read in order, with the label side spelled without bare names (`$major`, ... or the labels' names as
  strings); (B) `version & lex_ge(1, 4, 0)`: the call record is the bound tuple, the operand (by `&`) gives the other
  side as its labels in group order, with a compile error when the counts differ; it needs a variable-length call
  record (O47). (The `&`-equality of `[1, 4, 0]` and `[0, 1, 4]`, review OWN-9, is the language reading; a structural
  macro reads the order, so it does not decide.) No lean in rev 7: no worked example needs a tuple (rev 7 check of
  §8 and §12), and phase 1 can rely on the condition spelling of §8.
- **C26. The empty-match ERROR "opted out".** §7: in a predicate program the nullable-search case is an ERROR, with
  "no diagnostic ... when opted out"; §7.1: "Errors cannot be disabled". How a predicate program opts out of an
  error (other than `& !""` or anchoring) is not stated.
- **C29. `(x & isodate).year`.** `isodate(x)` is a compile error (CF:744, CF:749). What remains: whether `.year` of
  `x & isodate` is a VALUE (the cut layer's `(X & isodate).weekday`) or the map-interface PATTERN of the part (§3.2).
  Reading A: `.` on any rx is structural and values are only `$`-forms (`$d.year`). Reading B: `.year` of an
  application is a value. Rev 6 leaned A citing the search result's `d.year` (CF:874, the manager's gloss; review r8
  DRIFT-7); rev 7 argued A from §3.1 alone. Rev 8: the owner AGREED that `.` has ONE meaning, a field of the map
  interface of the thing on its left (CF:892, CF:898-899), and `x & isodate` is an rx, so `.year` of it is the field
  of an rx's map interface: the part's PATTERN (narrowed by x), and values remain the `$`-forms. Reading A therefore
  follows from the ruled dot (this document's consequence, LEAN); listed until the owner sees it, no longer argued
  from the search result.

Open items (rev 0, still open):
- **O1.** The meaning of a program's final expression against the subject (search vs whole-subject test). The
  empty-match rule presupposes a SEARCHED MODE chosen by the caller (predx O1 lean: the caller picks); not ruled.
- **O2.** Precedence among `!`, `:`, `.`, `$`, prefix comparisons, arithmetic and `@` is stated only pairwise (C16,
  §4.1's entry extent; and `$` over a dot path, §5.4: `$a.b.c` = `$(a.b.c)`).
- **O3.** Notes call several leanings "ruled" (unset label false, union type of duplicates, filtering by indexing).
- **O5.** Do a map's per-field value constraints carry into joined labels (asked Frank 2026-11-14; lean yes; predx:
  yes by construction).
- **O6.** `functions` presupposes DFA captures ([ENG-TDFA]); Q11 moves span REPORTING to `captures`; whether
  `functions` without TDFA pays a VM re-run per candidate is not ruled.
- **O7.** Weekday value type and numbering (`weekday == "Sat"` vs `weekday: 6`).
- **O8.** Checksum filters over separated digits (does `luhn` skip spaces?).
- **O10.** Resume after a rejecting callout for unanchored search (predx: the next DFA candidate; not ruled).
- **O13.** Library files: bindings + `@export`; whether a library has a final expression (the "one final
  expression" and "unused pattern" rules, §5.1) is not stated.
- **O14.** String position out of range: CLAMP (rev 0 leaning) vs strict false (predx lean).
- **O15.** Mid-sequence placement for joined maps (`before`/`after`): deferred to a real example.
- **O16.** Group 0 find-all resume rule (`\K`-style vs lookbehind-style), cond_family.md §7 (D193 add. 5).

Open items (rev 2, still open):
- **O19.** A match-dependent binding is "a computed label of the pattern whose labels it reads": which pattern, when
  the labels it reads occur in several bindings (`$mname` in `textdate`, reached again through `rfcdate.rest`).
- **O20.** `records` tiling: how an item rx declares its separator/gap bytes (line terminators) so that tiling
  holds without `gaps = "allow"`. CONSEQUENCE (review Q1R-10): until it is settled, E-FILE fails its own tiling rule
  on every `\n` (§12.8); the review suggests a declared separator (`records(text, rx, sep = /\n/)`-shaped).
- **O21.** Bounded recursion's base case: several definitions of one name by literal argument (`value_depth(0) :=`)
  is predx's spelling; not stated as a general feature.
- **O22.** The per-binding `@warn.off` spelling; the `@each(...)` per-entry assertion spelling (both OPEN by ruling).
- **O24.** Export: the Q6/Q9 note's "look later: `export` as a binding attribute, imports as a compilation-unit
  setting" is overtaken by the function forms, which are LEAN (manager); the option (b) `_`-prefix convention is
  expressible as `@export(/[^_].*/)` but not a default (a library with no export is an error).

Open items NEW in rev 3 (review 2026-11-14-r1-predspec items dispositioned OWNER that no ruling covers; each with the
review's proposed lean, in plain words, NOT resolved):
- **O26. Is a negated filter with no label a full pattern?** (OWN-2, RUL-2.) `>=200` may stand alone (`${>=200}`,
  `@warn.off(startsWith("dead."))`) but `!<200` and `!startsWith("dead.")` may not (prefix `!` always makes a macro, §2.2),
  although both are well-defined regular sets. Lean: yes, a label-free `!f` is a full pattern exactly like a
  label-free `f` (the "useless in a searched program" worry is what the empty-match rule already catches); plus a warning when a
  negated numeric comparison meets a target with non-canonical members (`0150`, `abc`).
- **O27. Does quoting a constant decide how it compares?** (OWN-3.) `a := 256` and `b := "256"` are the same set, yet
  `x & <a` compares numbers and `x & <b` compares text (`1000` out vs in), and `@assert.same(a, b)` passes. The same
  question covers arithmetic results (does `${$y + 1}` on `0099` insert `100` or `0100`?) and leading-zero bounds
  (does `between(01, 12)` admit `1`, `05`?). Lean: make numeric vs text a property of the comparison you write, not
  of how the constant is quoted; arithmetic yields canonical numerals; width is set with the padding modifier.
- **O28. One rule for conditions on optional, repeated and never-entered labels?** (OWN-4.) On `1,7,` with a
  repeated n, "not all below 5" (`!(n: <5)`) matches while "each not below 5" (`(n: !<5)`) does not; on an optional
  label that is unset the two sentences of §4.2 disagree; `?` vs `*` around the same group flips `(n: <5)` on `end`.
  (Rev 3's lean, "a condition holds when EVERY occurrence is in the set AND there is at least one", lost its
  zero-iteration clause in rev 9; the zero-iteration rule now stands RULED, CF:997-1000, in the RESOLVED list. What
  rev 3's lean still says:) `!(x: S)` is its plain complement; `(x: !S)` = every occurrence outside S; a warning with a witness when the
  two differ for the pattern at hand; `occurs.all` an alias or removed (C28). Rev 8: `occurs.all` is gone (C28
  RESOLVED) and the question now covers a SEARCH with zero hits. REV 9: the ZERO-ITERATION part is RESOLVED (see
  the RESOLVED list; rev 10: PER MATCH, RULED, CF:997-1000): a plain condition HOLDS over zero iterations of a loop
  the match reached, as the 11-13 leaning said ("`all` is true" over no occurrences, CF:180), and the quantifier the
  user chose decides whether zero is allowed (`*` vs `+`; `occurrences`'s `min`); a label whose group or loop the match
  never reached is UNSET and fails; rev 8's lean (fail) is WITHDRAWN. The boundary is stated once in §4.2, with its
  look-alikes L56, L65. STILL OPEN: `!(x: S)` vs `(x: !S)` on a repeated label (on `1,7,`: "not all below
  5" matches, "each not below 5" does not; L30, GAP), and `(x: !<5)` on an unset set-once x (the two sentences of
  §4.2). Lean for those: `!(x: S)` is the plain complement, `(x: !S)` = every iteration outside S, with a warning and
  a witness where the two differ for the pattern at hand.
- **O31. The dot family, and level selection.** (OWN-7, RUL-12; WIDENED in rev 7 by review r8 P6-12, CENSUS-24.)
  One `.` carries four resolutions: (1) a LABEL of the map interface (`d.year`, `rest.year`); (2) a module MEMBER
  (`json.row`), which is name resolution if a module is a namespace (O46's lean), not navigation on a value;
  (3) METADATA (`.index`, `.label`), which share the dot with user labels: for `/(?<index>\d+),(?<label>\w+)/`, is
  `r.index` the label or the position?; (4) a PATH under `$` (`$rest.year`; `$` covers the whole path, §5.4). §9 cut
  UFCS for being "a second resolution rule to `.`" (rev 8's §9; rev 7's said "third", review r10 FIXA-8); the same
  argument applies here. Readings: (A) one meaning, the
  field of the map interface of the thing on the left, with modules read as maps of members and metadata as reserved
  fields (an error for user labels so named); (B) the dot for labels and members only, metadata as call-position
  built-ins (`index(x)`, `label_of(x)`); (C) a non-alphabetic metadata mark. Lean (rev 7): A for labels and paths,
  B for metadata; members follow O46. REV 8: the DOT PART IS DECIDED: the owner agreed to reading A in full ("agree",
  CF:892, to the manager's lean recorded at CF:898-899: "label, module member, metadata and the `$` path are
  instances"), so metadata are RESERVED FIELDS of the map interface and a module's members are its map interface's
  fields (CF:891-892). What remains, as this document's consequence of A (LEAN): a user label named `index` or `label`
  is a compile ERROR naming the reserved field (reading A's own clause; REV 9: the MANAGER'S CALL, LEAN (manager));
  the metadata name list is closed (`.index`, `.label`). STILL OPEN: how a program selects `functions`/`captures`/`vm`/`eval` (as strings or API options, not
  bare words).
- **O32. Flags of a pattern inserted in a hole.** (Q1R-11.) With no inherited flags, `q := /^\{.*\}$/` inserted in
  `/${q}/m` keeps single-line `^`/`$` and finds nothing on `{a}\n{b}`, while the same text inlined in the `m`
  literal finds both lines. Lean: a `flag.hole` warning naming the fix (`q := /.../m`), or state the flags of a
  binding explicitly.
- **O33. Two conditions on an ambiguous pattern.** (RUL-3.) RESOLVED in rev 9 by the one reading (CF:953-955; see the
  RESOLVED list): both conditions read PCRE's one parse, so the example is false at every level. Rev 8's lean
  (per-condition some-parse) is SUPERSEDED with the some-parse rule.
- **O34. Same text twice: one level for every spelling?** (RUL-7.) `\k<s>` on a 3-valued finite group needs `vm`,
  the value hole `${$s}` on the same label is default-level, and `each(..., enumerate(...))` is a third spelling.
  Lean: one rule keyed by whether the referenced language is finite, for all three spellings (links
  [BACKREF-FINITE]; if Q10 keeps the engine rule out of #6, the predicate front end must still lower `\k` on a finite
  label as it lowers `${$x}`, or refuse both).
- **O35. A label set twice in one match.** (RUL-16.) `(?J)(?<x>\d)-(?<x>\d)` is not "repeated", so `(x: <5)` is
  unspecified and `$x` silently picks the lowest-numbered group, while the look-alike repeat `(?:(?<x>\d)-?){2}` is
  under the sequence rule. Lean: the sequence rule for every label with more than one static occurrence per match.
- **O36. A search assertion.** (Q1X-5, NOTED.) No assertion can state search behaviour (E-IPV4's `256.1.1.1` ->
  `56.1.1.1`). The critic's suggestion: a library search assertion (`@assert.finds(p, "256.1.1.1", ...)`-shaped, a
  name, not a keyword). Not dispositioned by the review; recorded. Rev 8: with `occurrences` a library transform, an
  assertion can state what a search finds INSIDE A VALUE, decided on strings (`@assert.some("256.1.1.1" & occurrences(ipv4)
  & some((hit: "56.1.1.1")))`); the FINAL pattern's searched mode (where in the subject a match is reported) is still
  outside every assertion. Lean: this narrows O36 to that remainder; no new assertion until a measured need (D77).
- **O37. Two modifier names this document chose.** `unpadded(n, S)` (rev 2's `pad(n)`: the filter reads a subject
  as if zero-padded to width n) and `json.quoted(S)` (rev 2's `jstr`) are placeholders under the naming rule; the
  ruling named `padded`, `any_case`, `quoted`, `length`, `month_numbered` only.
- **O38. Look-alike rows with no diagnostic.** §0.1 marks GAP rows (rev 8: L20, L21 on answers, L22, L24, L29, L30,
  L32, L33, L35, unchanged in rev 9, whose new rows L55-L59 carry a class each: L55 BY DESIGN, L56 and L59 WARNING,
  L57 ERROR, L58 SAME, and L34 moves from WARNING to SAME; rev 10's L60-L66: L60, L65 WARNING, L61, L64 BY DESIGN, L62
  ERROR, L63 SAME, and L66 a NEW GAP (a count filter in a searched program, `count.searched` proposed, not adopted);
  rev 11 (review r12): L7, L11, L13, L15, L41 move from SAME to BY DESIGN (a `^` in a directly applied filter adds
  nothing; whether a warning should say so, since the form LOOKS like "starts with", is this item's question), and
  L67 is a NEW GAP (an rx-text `&` whose concatenation makes the result empty; the empty-intersection error at every
  `&`, proposed, not adopted); rev 12: L63 moves from SAME to BY DESIGN (PCRE's `$` before a final newline; whether
  a warning should name a `$` inside `contains`/`occurrences` that a gap can follow is this item's question), L68 was BY
  DESIGN (`anchored` vs `\A...\z`), SAME from rev 13 (exact ends, §13 O62 CLOSED), L69 SAME; rev 13: L11, L41 move
  from BY DESIGN to WARNING (`anchor.operand`), L70, L71 new WARNING rows, L66 from GAP to BY DESIGN (no count
  warning, RULED, CF:1073-1081 on main); rev 8 moved L31 to BY DESIGN and L51 to ERROR; L16, L23, L25, L31, L48, L52, L54 are BY DESIGN, the
  stated meaning of a mark or a library name, §5.4, §4.3; L52, "a plain condition on a hit means ALL hits", is the one
  rev 8 row where a warning could pay, since the owner's own first question was about it, CF:904):
  DIFFERENT with no named diagnostic, so G0's acceptance fails on them today. Some are open items above; L20 (a padded
  target against an integer comparison set) and L25 (`/a|b/` vs `/b|a/` under `[]`/`.index`, by design) have no item:
  whether a documented structural difference (a BY DESIGN row) also needs a diagnostic, and which warning L20 gets,
  are open. Also from OWN-15: whether the goal order G1 > G2 should be stated as G2 > G1 at the default level (what
  the rules do, §0 Goals).

Open items NEW in rev 5 (from the 2026-11-15 entries and the rev 4 audit; plain words, each with a leaning):
- **O39. The budgets: how big is too big?** RESOLVED in rev 10 (CF:977; the RESOLVED list), as its lean said. Two size limits are named but never set by the owner: (a) the
  class-count tiers of a relation between two labels (§4.6: "24 classes = fine, 1,440 = borderline, 3.65M = error"
  is the manager's answer to "how practical", CF:659-663, which the owner did not reply to); (b) the budget over which
  `count()` is refused in favour of `occurs` (CF:832). Lean: ONE budget, a labelled, measured state/size quantity
  that both tests use (the standing preference for measured budgets over structural rules; D77), shown with its
  number by the cost report, with no fixed thresholds written into the spec.
- **O40. What is a number?** RESOLVED in rev 10 (CF:977-978; the RESOLVED list), as its lean said. The owner wants numbers to be one kind (CF:813, CF:823); rev 4 treated numbers as
  numeral strings (`5` = {"5"}). Open: whether a number is still a numeral STRING SET (so `count(...)` is the set of
  its canonical spellings and can be inserted with `${...}`) or a separate value kind; and so how `count(...)` reads
  inside a hole and against a padded subject number. Lean: numeral string sets, canonical form, so no third value
  kind is added and §2.4's comparison rules cover counts unchanged; where a number test is evaluated (inside the match
  as a set, or on the result as a value) is the compiler's choice, with the cost shown (manager's view, CF:813). Rev
  6: the ruled two value kinds (CF:858) leave no room for a number kind, so the lean follows from the ruling; it stays
  listed because the owner has not said "a number is an rx" in so many words, and the hole/padding questions remain.

Open items NEW in rev 6 (the type picture, CF:846-878; items (a)-(e) are the manager's TO CHECK list, CF:876, and
the brief's; each with a lean, none decided here):
- **O41. `(x)`: grouping or a one-entry record?** (a.) Lean: GROUPING wherever a value is expected. A record is
  never a value (CF:866), so a value-position `( e )` cannot be a record and there is nothing to disambiguate; a
  one-entry record exists only in the three record positions, where the position says so: a call `f(x)` (its
  parentheses are the record), a condition `(x: S)` (the `:` says so), and the left of a binding `(x) := r` (design
  only: lays x over r's first group; out of phase 1). §5.4, §0.1 L44.
- **O42. The list form and the map literal under "comma = next entry".** (c.) `[x = /foo/, y = /bar/]` reads
  directly: an array (any one entry) whose entries carry labels (`=`), i.e. `(?<x>foo)|(?<y>bar)`; it STAYS, as the one
  spelling of the aligned case (`join`'s input is the same form). The map literal `(x = /foo/ | y = /bar/)` does not
  survive: a `( )` in value position would be a record used as a value, and its single entry `x = (/foo/ | y = /bar/)`
  puts a label inside a value. Lean: withdraw it (CF:542 was a spelling lean, not a ruling); write the array form.
  §3.1, §0.1 L43.
- **O43. The condition's entry extent in record terms.** (d.) The C22 rule "`&`/`|` tighter than `:`, `:` tighter than `,`"
  becomes: an ENTRY runs to the next comma or the closing bracket (the comma is no operator, so it has no precedence),
  and inside an entry `&` and `|` bind tighter than `:` and `=`. Every rev 5 answer is unchanged (L3, L4, L22; the
  `(major: 1 & minor: >=4)` error). New consequences: `:` outside a record is an error (`P & x: S`, `[x: S]`). Lean:
  adopt the restatement; it is the C22 ruling, not a new rule. §4.1, §5.4.
- **O44. Every other comma in the draft.** (e.) Checked: `occurs.exactly(1, cond)`, `between(1, 12)`, `join(a, sep =
  ".")`, `each((& f), A)`, `weekday_of($y, $m, $d)`: call records (positional, then labelled), unchanged; `[f, g]`
  arrays of filters (§3.5) and `@export(["leap", /[^_].*/])`: arrays, any one entry, unchanged; `(x: <200, y: >55)`:
  a condition record, unchanged; `X[1,3,5]`: C5 (narrowed); commas inside `/.../` (`\d{1,3}`, `/${p},${p}/`,
  `[^,]`): rx text, untouched. Two things the ruling's list of record positions does not name: (1) DEFINITION HEADS
  `m(p1, p2) :=` and typed parameters `m(x: T)`; lean: a head is position (a), the call shape that declares the
  parameters, with `:` constraining the parameter it declares; (2) the library name `records(text, rx)` (§7) now
  collides with the vocabulary word "record"; lean: rename the placeholder when spellings are chosen (it returns an
  ARRAY of items, so a name like `items_of` says what it returns); rev 7 already says "item rx" for its pattern and
  "item" for each entry (§0.3, §7; review r8 CENSUS-23).
- **O45. A condition written where a value is expected.** The ruling says a condition is a macro (a value, CF:858)
  and that a record appears "in a condition, against a pattern's labels" (CF:866 (b)); conditions are also passed
  (`occurs.exactly(1, (name: S))`, `count((name: S))`), put in arrays (`[(x: <200), (y: >55)]`) and could be bound
  (`c := (year: 2000)`). Lean: a record whose entries are all `label: S`, written in value position, DENOTES ITS
  CONDITION (the macro with the operand open that lays the record against the operand's labels); the macro is the
  value, the record is its written body, and no record is ever bound. Any other record in value position is an
  error (L43). §4.1, §0.1 L46; rev 7 states it IN §5.4's table as its own row (review r8 P6-3).
- **O46. What a module is.** Rev 5: a module is a MAP of the file's bindings (LEAN, CF:619), usable whole as a
  pattern when every entry is an rx. Under the two kinds it is neither an rx (it holds macros) nor a record (never a
  value, CF:866), yet `json := import("json")` binds it. Reading A: a module is a compile-time NAMESPACE that `:=`
  names, not a value (no passing, storing or returning; `json.row` is name resolution). Reading B: a module is an rx
  when every export is an rx and a namespace otherwise (two meanings for one form, against G0). Lean: A; the "use a
  module whole as a pattern" sentence goes (name the entries in an array instead). Touches E-JSONL, E-IPV4, E-HTTP,
  E-DEPTH only through their `import` lines, whose spelling does not change. §7. Rev 7 (review r8 P6-8 (c)): the
  same question covers a RUN-TIME INPUT (`anchor := param(isodate)`, E-NEAR (b)), also bound by `:=` and neither
  plainly an rx nor a macro; the KIND TABLE (§2.1) lists both. Readings: (A) both are named by `:=` but are not
  values (a third BINDABLE shape beside the two value kinds, never passed or returned); (B) a parameter is an rx whose
  string the caller fixes per match (a value), a module a namespace (not a value); (C) both become values (a third
  value kind). Lean: B (it keeps two value kinds and needs one non-value shape, the namespace). REV 8, RESTATED by
  the owner (CF:890-892): "this leans into the idea of an interface to a type over the type ... So what import is is
  less important than that its interface is a map". RULED: a module is DESCRIBED BY ITS MAP INTERFACE (members are
  fields, reached by the one `.`); interfaces are never created values (CF:890-891), so the map interface gives no
  module VALUE either. NOT RULED, and by his words of lesser weight: what kind of thing a module is. So the module
  half of this item shrinks to a non-question for phase 1 (reading A's behaviour, no passing/storing/returning, is
  consistent with the ruling and kept, LEAN); the RUN-TIME INPUT half (`param(...)`) is untouched and stays OPEN
  with lean B.
- **O47. A call record of variable length.** (b.) Rev 6's motivation was the tuple: its argument that a `[ ]` cannot
  carry a tuple was false (C25, review r8 P6-2), so O47 is needed ONLY IF C25 takes reading (B) `version & lex_ge(1,
  4, 0)`, or the FAMILIES unlock (O52 (a)) moves `join`'s ordered parts into a call record. §5.2's macros have a fixed
  parameter list. Readings: (A) a library-only variadic form (a declared "rest" parameter), (B) fixed-arity variants
  (`lex_ge3`), (C) none. Lean: C until C25 or O52 (a) needs it (D77); then A.

Open items NEW in rev 7 (review r8 2026-11-15-r8-predspec6, its PLAN items and the owner's search note; each with
its readings and a lean, NONE decided here):
- **O48. What `:` means in a definition head.** (Review r8 P6-4; OWNER-8, CENSUS-4/5, SIM-11.) In a condition `x: S`
  NARROWS silently (`isodate & (year: <2000)` drops what is outside); in a head `m(x: T)` it CHECKS (an argument
  partly outside T is an error showing a dropped witness, §5.2); §0.1 L49. The owner's own word for `:` is "filters"
  (CF:706). No §12 case uses a typed head. Also `m(p: pure)` puts a PROPERTY after `:`, not a constraint set.
  Readings: (A) `:` NARROWS in both, the head check becoming the existing dead-branch / empty-intersection
  diagnostics at a narrowing site (one meaning; the general form of O52 (c)); (B) the containment check gets its own
  spelling, `:` keeps narrowing; (C) typed parameters leave phase 1 (no case needs them). `pure`: a non-`:` spelling
  under any reading. Lean: A (it removes the second behaviour without a new mark), C for phase 1 if the owner prefers
  not to decide now. REV 8: the owner chose (C) for phase 1 ("yes keep out of phase 1. I like the idea of types but
  they need more thinking", CF:889; RESOLVED above for phase 1). In the DESIGN the item stays OPEN with no reading
  chosen: (A) and (B) are the candidates for the "more thinking", together with his remark that an interface to a
  type may matter more than the type (CF:890) and §9's declared types.
- **O49. One span per filter role: confirm.** RESOLVED in rev 10 (CF:990-996; the RESOLVED list), as its lean said. (Review r8 P6-5, ruled FIX-NOW by the manager; LEAN until the owner
  confirms.) Rev 7 states that `^`/`$` in a filter passed as an argument, or in a hole of a filter's body, are the
  ends of the span the enclosing FILTER ROLE filters (§11 ONE SPAN PER FILTER ROLE), so `contains(/^err/)` =
  `startsWith("err")`. The alternative: a hole (and so an argument a library body puts in a hole) opens a span of its
  own, `contains(/^err/)` = `contains("err")`, with a diagnostic for an anchored argument (review r8 P6-5 (b)). The
  consequence the owner should see: under rev 7, `\b` at a hole's edge stays the edge-assertion error (L8, CF:713)
  while `^` in a hole reads the enclosing span: two assertion kinds, two rules, because `^` needs no text outside the
  span and `\b` does. Lean: rev 7's reading (it is the one a user expects, G0, and it is the owner's 11-15 rule,
  CF:761, applied without exception).
- **O50. What a search result IS at match time.** (Review r8 P6-7: OWNER-10, RUL-8/9, CENSUS-11, DRIFT-1..8.)
  RESTATED IN REV 8 by the transform ruling (CF:922-926, accepted at CF:905) as the GENERAL question: the ARRAY
  INTERFACE over the iterations of ANY repeated label (§4.3). Rev 7's parts, each with where rev 8 leaves it:
  (a) THE TOOLS. Rev 7's reading (D), "the search result is a REPEATED LABEL", is ADOPTED (CF:910-911); there is one
  population (iterations), not two. The GROUP QUESTIONS (plain condition = all, `some`, `all`, `count`, `occurs`
  counts) compile to states and are phase 1 (CF:922-924). `each`, `join`, `where`, `enumerate`, `.label` never read
  iterations (§3.4, LEAN). ONE-ITERATION access (`$m.hit[2]`, `$m.hit[2].g`) needs captures inside a loop: the
  `captures` level, its cost shown (RULED BY ACCEPTANCE, CF:977, to CF:972-973's "reading ONE hit"; it was the
  MANAGER'S LEAN, CF:924-926, until rev 10); every iteration and selecting iterations (`$m.hit[(g: "x")]`, rev 11's
  spelling, review r12 CENSUS-1) at the same level: LEAN (review r12 CENSUS-6 (b), CENSUS-8); the owner's example is
  the intended behaviour at that level, §2.6. A literal-index TEST (`(x[2]: S)`) at the
  default level by CF:62's countdown: LEAN (§4.3, O56).
  (b) `d.g` ACROSS ENTRIES: dissolved. There is no `d`; `m.g` is a field of m's map interface (the ruled dot), the
  label g, which repeats, so a condition on it follows the sequence rule (plain = every hit) and the group questions
  (§4.3). Rev 7's readings (A) union set / (B) projection array / (C) per entry only are not needed.
  (c) THE FILTER ROLE: dissolved. `occurrences` IS a filter (`(m: occurrences(r))`), which with the default `min = 0` never
  rejects; the TEST is
  `contains(r)` and its negation `!contains(r)` (§2.6; L16, L51).
  (d) THE RECORD ON THE LEFT: moved to O54 with the binding of a search.
  (e) `some`/`all`: decided: `some(...)` is the one spelling of "some" (CF:912-914), `all(...)` the default, and the
  witness rule is SAME ITERATION BY RECORD (O29 RESOLVED).
  What stayed open here, the level of one-iteration access, is RULED in rev 10 (`captures`, CF:977; the RESOLVED
  list). C36 (the
  priority parse), which the whole restatement rested on, is RESOLVED in rev 9 by the one reading (CF:953-955).
- **O51. Statements that start with `(` or `[`.** (Review r8 P6-13, CENSUS-14.) `(` and `[` after an expression are
  always a call or an index, and newlines are layout (§5.1), so `t := foo` NEWLINE `[a, b]` parses as `foo[a, b]` and
  `d := ...` NEWLINE `(x, y) := ...` as a call. The final-array half is live today; the destructuring half is design
  only. Readings, for the spelling step: (A) a statement never starts with `(` or `[` (a record on the left gets a
  leading mark; a final array is bound first); (B) a newline is significant before `(` and `[`. Lean: A (no layout
  rule; one-token look-ahead stays as §2.5 argues).
- **O52. FAMILIES and the general form behind them.** (Review r8 P6-16, CENSUS-25/26; a unification candidate, not a
  rev 7 rewrite.) ANY ONE is spelled `|`, `[ , ]`, `some`, `X[1|3|5]`; ALL TOGETHER `&`, `( : , : )`, the sequence
  rule (rev 8: `occurs.some` and `occurs.all` are withdrawn, CF:913, so `some` and the plain condition are each one
  spelling over iterations, §4.3); a NAME is introduced by `:=`, `[x = e]`, `(?<x>...)`, a head parameter, a record
  on the left. General form: one ENTRY LIST whose bracket names the combiner and whose entry marks are fill (`=`) vs
  narrow (`:`). Unlocks, each with its TRIGGER: (a) `join`'s ordered parts in a call record (`join(year = ..., month =
  ..., sep = "-")`-shaped), so `[ ]` reads only as any-one; trigger: the variadic record O47 needs, one mechanism for
  C25, O47 and this; (b) piecewise definitions as narrowed heads (`value_depth(k: 0)`), no new form; trigger: O21
  decided, or a second recursive library; (c) one meaning of `:` (O48 (A)); trigger: any typed-parameter build (rev 8:
  typed parameters are out of phase 1, CF:889, so `:` already has one meaning in phase 1);
  (d) mixed rx/macro arrays and `each(isodate, dates)` without a section (§3.5's mixed-array error goes); trigger: a
  worked example with a mixed table, or C33's "other sections on need". Lean: record the family; decide each unlock at
  its trigger (D77).

Items NEW in rev 8 (the owner's three 2026-11-15 entries, CF:880-926; each with its readings and a lean, NONE decided
here):
- **C36** (rev 8's CONFLICT, the priority parse vs some-parse): RESOLVED in rev 9 (CF:953-955); see the RESOLVED list.
- **O53. An `occurrences` argument that can match the empty string.** (Record (5), "the empty-match advance rule stated",
  CF:920.) PCRE ends a loop whose iteration matched empty, so the lazy-gap body gives at most one hit for a nullable
  argument (`/a*/` on `baa`: one empty hit at 0, where find-all gives `''`, `aa`, `''`; §0.1 L53; checked on
  libpcre2 10.46 and Python 3's `re.findall`). Readings: (A) REFUSE: a nullable `occurrences` (or `contains`) argument is a
  compile error naming `x & !""`, as the empty-match rule refuses a nullable final pattern in a predicate program
  (§7); (B) write PCRE2's find-all ADVANCE RULE into the definition (after an empty hit, the next hit may not be empty
  at the same place; one character is skipped), which no lazy-gap regex expresses directly, so `occurrences` would stop
  being library text. REV 9: (A) is the MANAGER'S CALL (LEAN, manager; not an owner ruling): §2.6 and §8 say so; the
  item stays listed until the owner sees it. REV 10 (review r10 SIM-1, the manager's pick): its SIBLING is refused the
  same way, an argument whose own group is read by a backreference or conditional inside it (PCRE's loop carries the
  earlier hit's capture into a later hit: one hit `aca` where find-all finds `aca`, `bcd`; §0.1 L62); both refusals
  are stated once, §2.6 THE TWO ARGUMENT REFUSALS. REV 11 (review r12 SIMULATE-2): the sibling is NARROWED to a
  reader that can run while its group is unset in the current hit, the case its reason describes; `/(.)\1/` is
  admitted (LEAN, this lane's pick). Reading (B) for the sibling would be a per-iteration capture reset,
  which is not PCRE's parse of the written body.
- **O54. What a binding of a search result becomes.** (Brief item (v); review r8 P6-7 (d); §0.1 L50.) REV 9: the
  `d :=` half is RESOLVED by the owner (CF:929: "the name binds to the transformed regex as for all transformed
  regex"): rev 8's reading (A), `hits := occurrences(r)` binds the transformed rx, applied as `(m: hits)`, no special case
  for search (§2.6, §5.1). Reading (B), a match-dependent binding `d := $m & occurrences(r)` (a computed label, §4.4), is
  not a separate rule: §4.4 already admits it, and it is used only if a case wants a name for one label's hits. STILL
  OPEN, unchanged: the RECORD ON THE LEFT, `(x, y) := $m & occurrences(/(?<a>\d)(?<b>\d)/)` (CF:852, his words, "We might
  use it to bind values from a search"); lean (ii): laid against the ARGUMENT's GROUPS in their group order (the map interface;
  the library's own `hit` group excluded, since in the body's group order, hit, a, b, x would land on `hit`; review
  r10 FIXA-4), x and y REPEATED labels, one iteration per hit, paired by iteration; design only, out of phase 1 (§0.2,
  L50).
- **O55. The hit's label, and "every hit" as a condition.** The library body names the hit group `hit`
  (placeholder). A user label `hit` inside the argument would be a duplicate (the `(?J)` question, O35). And
  "count the hits" is spelled `count((hit: /(?s).*/))`, a condition whose set is every string. Readings: (A) a fixed
  library label, a clash an ERROR naming it; (B) the hit label as an optional keyword setting of `occurrences`
  (`occurrences(r, hit_name = "h")`; rev 9 wrote `label =`, a reserved metadata name, review r10 CENSUS-14), with `hit` the
  default; (C) no hit label at all, the group questions reading only the
  argument's own labels (then "count the hits" needs a label in the argument). For "every hit": (a) keep the
  condition spelling; (b) a label-only spelling (`count(hit)`), which C13's bare-label question governs. Lean: (A)
  and (a) for now: no new mark or rule; a shorter spelling when a worked example needs it (D77).
  REV 10, TWO TRANSFORMS IN ONE CHAIN (review r10 FIXB-4, with `contains` = `occurrences(x, min = 1)`, §2.6): every
  `contains` and `occurrences` exposes `hit` and makes its argument's labels repeated. So (i) in `(m: contains("a") &
  contains("b") & some((hit: ...)))` both operands offer `hit`, and §4.1's chain lookup (the whole flattened chain)
  makes it AMBIGUOUS; (ii) a label set once in the argument (`contains(/(?<k>\d)/)`'s k) is repeated in the result, so
  a bare `$k` is the §4.3 error at the default level and a structural tool on it the §3.4 error. Readings for (i):
  (A') the ambiguity ERROR naming both, with the fix "ask about a label of the argument instead (`some((g: ...))` with
  g unique to one argument), or give one `occurrences` call its own hit name"; (B') reading (B) above, a per-call hit name, made
  mandatory when two transforms meet; (C') a condition right after a transform reads only that transform's `hit` (an
  order rule, against the order-free `&`, G0). Lean: (A') for phase 1, which needs no new rule (it is §4.1's), with
  (B') as its named fix when a case needs two hit labels; for (ii) the consequence is stated, not avoided: the
  arguments' labels ARE repeated, and "the compiler may build `contains` as the plain set" changes no label. Not
  decided here (the manager's ruling on FIXB-4). REV 12: put to the owner as question (2) of OWNER QUESTIONS AFTER
  REV 12 (lean: (A'), the ERROR, with (B'), a per-call hit name, as its fix). `startsWith`/`endsWith`/`anchored` add
  no `hit` (plain gap bodies, §8), so only `occurrences` and `contains` meet this. REV 13: `search` is renamed
  `occurrences` (CF:1028); whether the default name `hit` is renamed to match is NOT ruled (CF:1029-1030), a
  spelling-step note. (i) is RESOLVED in rev 13 (RULED, CF:1068-1072 on main; rulings R-1): reading (A') with (B') as
  its fix, (B') OPTIONAL (a call MAY name its hit label, `occurrences(x, label = "foo")`, his placeholder spelling;
  `label` is reserved metadata since rev 9, review r10 CENSUS-14, so the setting's name waits for the spelling step);
  two calls exposing the same hit label in one chain are the ambiguity ERROR naming both. Still open: (A)/(B)/(C) of
  the label's default name and the "every hit" spelling, both spelling-step questions.
- **O56. Which iteration a record or an index means.** (1) Same iteration by record when the labels sit at
  DIFFERENT depths (`some((g: "x", k: 1))`, g inside the loop, k outside it, or two nested loops). Lean: the
  innermost loop that encloses every label of the record; a label outside it has one value for every iteration of
  that loop. (2) A literal index as a TEST (`(x[2]: S)`): by CF:62 (the 11-13 `s.nth(i)` rule: "YES if i is bounded",
  a countdown of ~k states) it is regular and needs no captures, while the transform record puts `d[2]` at a higher
  level (CF:924-926; rev 10: RULED for READING one hit, CF:977, which does not say whether a test reads it). Lean: a TEST on iteration i is a group question at the default level (it
  reads no text out); READING iteration i's text (`$x[2]`, `${$x[2]}`) is the `captures` level. Both leans are this
  document's.

Items NEW in rev 9 (the owner's last two 2026-11-15 entries, CF:927-961; each with its readings and a lean):
- **O57. OWED MEASUREMENT: what does the one reading cost?** (CF:949-950: "i'd like to know the cost of this";
  record CF:955-957: "a measurement owed before any build go".) NOT RUN in rev 9 (design only). WHAT IS MEASURED: for
  a condition on an AMBIGUOUS label, the extra states of the automaton for PCRE's reading (§4.5) over the some-parse
  automaton (the plain product of pattern and condition) for the same program: both absolute minimal-DFA state
  counts and their ratio, with the build time beside them and whether the construction finishes under a stated
  budget. ON WHICH POPULATION: (1) the worked examples: every §12 case (all unambiguous at the labels they read, so
  the expected extra is ZERO: a control that the construction adds nothing where the readings coincide), §4.5's
  `/(?<a>\d+)(?<b>\d+)/` conditions, §2.6's `occurrences` rows (the `hit` label, ambiguous as a set by construction: the
  case every `occurrences` question meets) and the §0.1 rows L34, L59; (2) a CORPUS OF AMBIGUOUS PATTERNS: the `.rxt`
  corpus's patterns with a capture group, kept where the decidable ambiguity check (§4.5) finds an ambiguous label,
  each paired with one fixed condition family per ambiguous label (the label equal to its PCRE value on a
  shortest witness, and its negation), so the conditions are not chosen by the construction's author. THE REGIME:
  compile-time size on one box, compiler and minimiser, named in the result (§0 standing question 1); match speed
  is not measured (both automata are linear). THE INDEPENDENT CONTROL: each constructed automaton's answers are
  checked on sampled strings against libpcre2's own anchored match (the label read from the match, never a
  rejecting callout) and Python's `re`; the ambiguous population is counted twice, by the ambiguity check and by
  libpcre2 itself (K35): a callout at the pattern's end that records the label's span and returns "fail", so PCRE
  backtracks through every accepting parse of a sampled witness; two recorded spans = ambiguous. That callout COUNTS
  only (a lower bound, on samples) and never decides an answer, so it is not the steering callout the reading
  forbids, and its parses come from PCRE's own backtracking, not from pcrec (review r10 FIXB-6). TIMING: "before any
  build go" is the record's (CF:956), LEAN; the owner's words are "i'd like to know the cost" (review r10 FIXB-5). WHAT MOVES: no emitted byte; the result
  feeds the budget (O39) and the owner's go/no-go on the one reading's cost. WHAT WOULD FLIP A DECISION: a small,
  bounded extra on the corpus keeps the manager's lean (build at the default level); frequent blow-ups would make
  the budget refusal common and send the cost back to the owner. Prerequisite: a construction of PCRE's reading as
  an automaton, which pcrec does not have today (an in-compiler automaton kit, [AUTOMATON-KIT], is the natural home).
  Lean: run it as its own measurement lane when the predicate front end nears a build go, not before (D77).
- **O58. `min` above 1, and `max`.** RESOLVED in rev 10 (CF:963-966: reading (A); the RESOLVED list). (CF:951-952, CF:960; §0.1 L57.) Under PCRE's reading the quantifier `{n,}`
  with n >= 2 lets PCRE RE-CUT the hits to reach n (`x := /aab|a/` on `aab`: one hit at `min` 0 or 1, two at `min = 2`;
  libpcre2 and Python's `re`, `docs/dev/lanes/predspec9_reading.out`), so `occurrences(x, min = 2)` is not "at least two of
  the hits" (`occurrences(x) & occurs.at_least(2, (hit: /(?s).*/))`, which rejects `aab`). Readings: (A) `min` is 0 or 1;
  a larger `min` is an ERROR naming the `occurs.at_least` form; (B) `min = n` is SUGAR for the `occurs.at_least` form
  (not the quantifier), so the hits never change with `min`; (C) `min = n` is the quantifier `{n,}`, with a
  look-alike WARNING when the argument can re-cut. Lean: (A) (the owner named only 0 and 1, CF:960; (B) would make
  `min` mean two mechanisms). `max`: LEFT OUT for now, RULED (CF:951-952, "we could skip it for now"); FILED with its
  confusion stated: under PCRE's reading `{0,N}` means "take the FIRST N hits" (the rest of the value may hold more),
  whereas "AT MOST N hits in the value" is a count test that stays `occurs.at_most(N, ...)`. Trigger to revisit: a
  worked example that needs "the first N hits".
- **O59. The library bodies' own reading, and where `label.ambiguous` fires.** RESOLVED in rev 10 (CF:964: reading
  (A); the RESOLVED list). Under the one reading, a library body's
  gaps decide how the ARGUMENT's labels read: rev 8's `endsWith(s) := /(?s).*${s}/` reads `endsWith(/(?<n>\d+)/)` on
  `ab123` as n = `3` (greedy lead), the lazy body as n = `123`; rev 8's `contains` body read its argument's labels at
  the RIGHTMOST occurrence. Rev 9 (LEAN, this document) writes the bodies so the argument starts as far LEFT as it can
  (lazy gaps; `contains` = `occurrences`, §8), each library macro stating its reading and checking it by assertions (§5.6).
  Readings for the warning: (A) `label.ambiguous` fires only for ambiguity in the user's OWN text (the argument
  `/(?<a>\d+)(?<b>\d+)/` passed to `occurrences` still warns for a), not for ambiguity that a library body introduces and
  states (the gap of `occurrences` or `endsWith`); (B) it fires for every ambiguous label a condition reads, library-made
  or not. Lean: (A) (the library author validated the body's reading; warning every `occurrences` user would bury the
  warnings that matter). The LEVEL a budget refusal names (§4.5: `captures` where its tagged automaton follows PCRE's
  priority, else `vm`) waits on [ENG-TDFA] (§13 O6).

DECIDED BY THE MANAGER (rev 10, the picks of review r10's DISPOSITIONS RULED; each LEAN (manager), none an owner
ruling; listed so the owner sees them): (5) an `occurrences` argument whose own group is read by a backreference or
conditional inside it is REFUSED, the nullable refusal's sibling (§2.6, O53; NARROWED in rev 11, below); (6) a hit's labels are read within its
own iteration, a stated departure from PCRE's raw capture state (§2.6); (7) `${` is the one stated exception to "rx
text has PCRE's meaning", a literal `$` then `{` written `$\{` (§11, G3); (8) `contains` stays ONE definition, so a
condition after it reads every hit (§2.6, L58, L61); (9) E-DEPTH is marked as needing the multi-clause form, no new
grammar (§12.11, O21); (10) `each` passes the ordinal BY NAME (§5.3).

DECIDED BY THE MANAGER OR THIS LANE (rev 11, the picks of review r12's DISPOSITIONS RULED; each LEAN, none an owner
ruling; listed so the owner sees them): (11) L7, L11, L13, L15, L41 are DIFFERENT: BY DESIGN, no tail added (the
manager's pick on SIMULATE-1); (12) the second argument refusal is NARROWED to a reader that can run with its group
unset in the current hit (this lane's pick on SIMULATE-2; §2.6); (13) a selection of iterations is written in the
label path, `$m.hit[(g: "x")]`, and `$` reads the value(s) of a path (this lane's spelling on CENSUS-1, CENSUS-11;
§2.6, §5.4); (14) `balanced` uses its literal's own named group (the manager's pick on CENSUS-2; §7); (15) under the
rx-`&` switch ON PCRE's own constructs keep their meaning and a literal `&` is `[&]` (the manager's lean on CENSUS-3,
put to the owner as O60 (d)); (16) an rx-text `&` takes the whole concatenation, a guard of one atom is grouped (the
manager's pick on CENSUS-5; L67); (17) a duplicate label inside a loop is a repeated label (this lane's pick on
CENSUS-12; §4.3).

DECIDED BY THIS LANE (rev 12, readings of the one anchoring rule; each LEAN, none an owner ruling; listed so the
owner sees them): (18) "no extra rule" withdraws rev 10's exact-end `$` (SIM-5): `$` in a filter and its holes is
PCRE's, so `contains(/err$/)` accepts `err\n` (L63; `\z` for the exact end); (19) a compile-time set (an `enumerate`
or `@assert` argument, a name set) is read as a filter over whole strings (§11); (20) the library bodies keep
`contains := occurrences(x, min = 1)` and the lazy `endsWith` gap against the record's `/.*${rx}.*/` and `/.*${rx}/`,
the same sets (§8); (21) E-HTTP keeps `\A...\z` rather than the record's `anchored(block)` (L68, O62; REV 13: moot,
`anchored` has the exact ends and E-HTTP is written `anchored(block)`).

DECIDED BY THIS LANE (rev 13; each LEAN, none an owner ruling; listed so the owner sees them): (22) what opens a scoped
match, stated once in its general form: the program and every filter role, a hole never (review r14 F2; §11, §0.3);
(23) the warning is named `anchor.operand`, fires on an anchor in an `&` operand's OWN rx text (not inside a hole of a
macro body such as `contains(/^err/)`, not on `anchored(...)`), one per anchor, text in §11; (24) `anchored` is
DEFINED as the text `/\A(?:${rx})\z/`, not by the "filter role" wording, because that wording has a reading that
differs in a hole (§11; O64); (25) E-HTTP is respelled `anchored(block)` (the same text); (26) the "or what it
reads" clause of the naming rule is marked LEAN (review r14 CENSUS-6); (27) `capture` is classed a structural tool,
not a transform (O61's audit); (28) the library family is written lower case, "gap-bodied", and GAP is only the
verdict class (review r14 CENSUS-3); (29) the draft's own voice says "span" for the filtered text, "value" only for
a member of a kind and in quotations (review r14 CENSUS-2).

DECIDED BY THE MANAGER (rev 9; the manager's calls, each LEAN (manager), none an owner ruling; listed so the owner
sees them): (1) an `occurrences` argument that can match the empty string is REFUSED with the fix `x & !""` (O53 reading A;
§2.6, §8); (2) a user label named `index` or `label` is a compile ERROR naming the reserved field of the map
interface (O31; §5.4 `.` row); (3) the library transforms' gaps cross line breaks: `(?s)` in `occurrences`, `contains`,
`startsWith`, `endsWith` (§2.6, §8); (4) the `["US" => "United States"]` lookup-table spelling is DROPPED in favour of
computed labels (C7 reading A; §3.1).

FAMILIES noted by the review (PLAN; not folded): value mappings (RUL-F1); quantifiers and emptiness checks, now
incl. `count()` vs `occurs` (RUL-F2); same-text-twice (O34, RUL-F3); name-set selection (RUL-F4); the dot (O31,
RUL-F5); application spellings (C29, RUL-F6; C20/C30 resolved).
REVIEW r10 FIXB-9 (NOTED, a proposal for the owner's discussion, not a defect). (1) RUL-F2 gained four members in rev
9 (unset fails, zero iterations hold, `min` 0/1, the nullable refusal; rev 10 adds the second refusal). The critic's
GENERAL FORM: every label is a sequence of 0..n iterations in PCRE's parse (UNSET = zero iterations), a plain
condition is "every iteration" everywhere, "at least one" is always spelled (`some`, `min = 1`, `+`). Unlocks: one rule
instead of §4.2's boundary paragraph. Cost: it flips "a condition on an unset label fails" (CF:173). Its trigger was
the owner's answer on zero iterations, and that answer (CF:997-1000) took the OTHER side: a label the match never
reached FAILS. So the general form is recorded and not adopted. (2) The four library sets (`startsWith`, `endsWith`,
`contains`, `occurrences`): one body (`occurrences`) plus the argument's own anchors, `startsWith(x)` = `occurrences(/^(?:x)/, min =
1)`, `endsWith(x)` = `occurrences(/(?:x)$/, min = 1)`, same sets AND the same label readings as the written bodies (the
critic's hand trace). Unlocks: one hand-check table and one reading for the family. Cost: each such filter then
carries `hit` (O55 rev 10). Its trigger, the anchored-argument ruling, FIRED in rev 10 (CF:990-996, whose record
calls the two "conveniences", CF:994): the unification is now the manager's to schedule, not done here (lean: adopt
once O55's two-transforms question is answered, since every `startsWith` would add a `hit`). REV 12: WITHDRAWN by the
owner's ruling (CF:1019: "The manager's earlier lean to fold startsWith/endsWith into search with an anchored argument
is WITHDRAWN"): `startsWith`/`endsWith` stay plain gap bodies with no `hit` (§8), and the owner question that rested
on this lean is withdrawn with it.

Items NEW in rev 10:
- **O60. The rx-`&` switch: its default and its spelling.** The owner ruled `&` in rx text ALL OR NOTHING by a module
  or option (CF:978-984). Open: (a) the DEFAULT. Readings: (A) OFF, so a pasted PCRE pattern keeps its meaning (G3) and
  an intersection inside rx text is written with the whole rx in a hole (`${/(\d+)/ & <256}`); (B) ON inside the
  predicate opt-in, so `(\d+)&${ <256 }` works as written (`(?:(\d+)&${<256})` inside a longer literal, §0.1 L67) and
  a literal ampersand is `[&]` (165 of 7,057 corpus pattern lines contain `&`, but only ONE holds a bare literal `&`,
  §0 G3). (b) The literal: REV 11 (review r12 CENSUS-3): `[&]`, valid PCRE meaning `&` under both settings, so text
  written for ON reads the same under OFF wherever it has no intersection. Rev 10's `\&` is withdrawn as the
  rewrite: `\&` alone compiles and matches `&` (libpcre2 10.46, Python 3.14's `re`), but rewriting every `&` turns
  `(?&a)` into `(?\&a)`, a PCRE compile error. (c) The switch's NAME and whether it is a module (`requires module
  'X'`, D26's shape) or an option: a spelling-step question (D193 add. 4). (d) Which `&` is the operator under ON: CLOSED in rev 13 (RULED, CF:1041-1046 on
  main: "agree. Limited to where | is used to mean alternation. Also, \& should work as escape. Why not?"): `&` is the
  operator EXACTLY in the positions where `|` means alternation; PCRE's reading stands everywhere else (a class,
  quoted text, a callout's text, a `(?...` opener such as `(?&name)`, a property name, after a backslash); a literal
  ampersand is `\&` or `[&]`, both plain PCRE; rev 11 withdrew only the automatic rewrite of every `&` to `\&`
  (which breaks `(?&a)`), never the escape. (b) is answered with it (`\&` or `[&]`). Still open: (a) the default
  (lean (A), OFF) and (c) the switch's name, at the spelling step. §11.

Items NEW in rev 12 (the owner's 2026-11-15 evening ruling, CF:1001-1024):
- **O61. A name for `search`.** CLOSED in rev 13: the owner ruled `occurrences` (CF:1026-1031 on main, his words "1
  occurances", CF:1028), the lean of rev 12's five candidates (`occurrences`, `hits`, `marked`, `each_occurrence`,
  `containing`; for and against each: `docs/dev/lanes/predspec12_report.md`, TRANSFORM NAME AUDIT). NOT ruled: whether
  the label `hit` is renamed to match (CF:1029-1030), a spelling-step note (O55). The name passes the naming rule as a
  noun for what the changed filter reads, the clause this document derives from `length` (CF:722), LEAN (§2.7;
  review r14 CENSUS-6), or as a description of the accepted values read occurrence by occurrence. THE AUDIT (review
  r14 CENSUS-7: every provided macro whose input and output are filters, graded here, not by pointer). PASS:
  `padded`, `unpadded`, `any_case`, `quoted`, `json.quoted`, `month_numbered`, `anchored`, `contains`, `startsWith`,
  `endsWith`, `occurrences`, `json.row`; `length`, `left`/`right`/`mid` (through the "what it reads" clause, LEAN);
  `when` (a conjunction), `some`, `all` (quantifiers over iterations), `occurs.exactly`/`at_least`/`at_most`/`none`
  ("c occurs n times" describes values), `list_of`, `any_order` (descriptions of the accepted values). NOT
  TRANSFORMS: `count` (returns a number); `between`, `within` (set builders, no filter parameter); `each`, `join`,
  `where`, `where_group`, `each_group`, `records`, `enumerate`, `sort`, `unique`, `concat` (structural, compile-time);
  `capture(x)` (§5.3), CLASSED a STRUCTURAL TOOL (LEAN, this document): it places an rx under a caller-visible group
  name and its argument is never tested as a filter, like `join` building structure; if the owner reads the rule as
  covering every provided macro, the verb fails and the lean name is `labelled(x)`. No provided transform fails.
- **O62. `anchored`'s ends.** CLOSED in rev 13: EXACT ends, `\A`/`\z` (RULED, CF:1048-1053 on main: "`anchored(/foo/)`
  as a final pattern does not match `foo\n`"; the owner's earlier `/^${rx}$/` was a placeholder). `anchored(rx) :=
  /\A(?:${rx})\z/` (§8); L68 is SAME; E-HTTP is written `anchored(block)`. The "P in filter role on the enclosing
  scope" wording (review r14's general form) is NOT ruled (CF:1050-1053) and is not used as the definition: one of
  its readings differs in a hole (O64).
- **O63. Warn when a count sits in a program whose final pattern is searched?** CLOSED in rev 13: NO warning
  (RULED, CF:1073-1077 and CF:1081 on main, "Host count warn: agree", confirmed "Count warning: yes I agree with that
  interpretation"; rulings R-1); the trap and its fix (`anchored(...)`) stay stated where counts are documented (§4.3,
  §8, §12.9; L66 moves from GAP to BY DESIGN). The item
  as asked (review r10 SIM-6, L66; carried from O38): Under the one rule the wording still makes sense, restated:
  the count FILTER is a filter and matches its whole span, but a SEARCHED final pattern (the one place an rx is
  unanchored) picks the span, and a shorter span can pass a count the whole block fails (`Host: a\r\nhost: b`
  reports `Host: a`). The fix has a library spelling: `anchored(...)` around the final pattern (exact ends since rev
  13, the same as `\A...\z`). Lean: no warning (carried): counting inside the spans a searched program finds is a
  legitimate program, and the fix is stated where counts are documented (§4.3, §8, §12.9).

Items NEW in rev 13 (the owner's three 2026-11-15 entries after rev 12, CF:1026-1062 on main, and his condition on
the `&` ruling; §11 THE AMPERSAND RULE TESTED BY POSITION):
- **O64. `anchored(...)` inside a hole.** The ruled exact ends make `anchored(P)` the text `/\A(?:P)\z/`, and a hole
  opens no scoped match, so inside a hole its `\A`/`\z` are the ends of the scope AROUND the hole (the subject, or the
  enclosing filter role's span): `/x${anchored(/a/)}/` can never match (on `xa`: no match), and `/${anchored(/a/)}b/`
  neither (on `ab`). The other reading of the unruled wording, "P in filter role on the span the hole takes", makes
  both match (0-2; `predspec13_anchor.out`). Readings: (A) the text, as defined (an `anchored` hole that cannot reach
  the scope's ends never matches; proposed: a compile ERROR when it provably cannot, like the empty-intersection
  error); (B) inside a hole `anchored(P)` means P whole on the hole's text (then it is just `P` with its own anchors
  confined, i.e. the `&`-operand reading, `P & /(?s).*/`). Lean: (A), with the error: `anchored` is for a final
  pattern (the record's use, CF:1015); the confined reading already has a spelling (`${P & /(?s).*/}`, L71), so (B)
  would give one meaning two spellings.
- **O65. Does `anchor.operand` fire in every filter role?** The ruling names an explicit anchor in an `&` operand
  (CF:1057-1061). The same anchor ADDS NOTHING, for the same reason, in a `label:` condition (`P & (x: /^S\w*/)`,
  L7, E-CTX-1, E-CTX-7), a modifier's argument (`padded(/^5/)`, L13, E-CTX-5) and a compile-time name set
  (`@warn.off(/^dead\./)`, L15). Readings: (A) only `&` operands (his words); (B) every filter role, one warning,
  one rule. Lean: (B) (one rule for one fact; under (A) `x & /^S\w*/` warns while `(x: /^S\w*/)` is silent though the
  anchor means the same thing in both). Under (B) L7, L13, L15 move from BY DESIGN to WARNING.

OWNER QUESTIONS AFTER REV 13 (the open small ones, each in one line with its lean; the plain-words version with an
example each is in `docs/dev/lanes/predspec13_report.md`, QUESTIONS FOR THE OWNER). Rev 12's (1), (5), (6) are
ANSWERED (CF:1026-1062 on main: rx-text `&` where `|` alternates, `occurrences`, exact ends); (3) was withdrawn;
(2) and (4) were answered on the evening of rev 13 (CF:1068-1081 on main; rulings R-1).
- (2) ANSWERED in rev 13 (CF:1068-1072 on main): the ambiguity ERROR, fixed by a per-call hit label name
  (`occurrences(x, label = "foo")`, spelling a placeholder; O55).
- (4) ANSWERED in rev 13 (CF:1073-1081 on main): NO warning (O63).
- (7) `anchored(...)` inside a hole: reads the scope around the hole and so cannot match after other text; a
  compile error when it provably cannot: lean YES (O64).
- (8) The anchor warning in a `label:` condition, a modifier's argument and a name set too: lean YES (O65).

## 14. Non-goals

- Non-regular nesting (balanced parentheses, unbounded JSON) stays with PCRE recursion on the VM (`vm`) or bounded
  recursion (§7); the predicate language adds no non-regular power of its own.
- No general-purpose language: no unbounded recursion through parameterized definitions, no unbounded loops, no
  lambdas until an example needs one, no side effects beyond compile-time `@` statements, no run-time compilation of
  caller-supplied PATTERNS outside `eval`, no alphabetic keywords, no boolean type (LEAN, CF:595). Numbers are NOT a
  non-goal: they are one kind for the user (§2.1, LEAN).
- No "best match" overload ranking; no interfaces, members, UFCS or `types()` in the first spec (§9).
- No third value kind: no record, boolean or number values (two kinds, rx and macro, RULED CF:858; a record is a
  shape laid against fields, never a value, RULED CF:851-852; no boolean: LEAN, CF:595; numbers: §13 O40). Tuples:
  no tuple VALUE kind, but whether a tuple comparison is spelled over arrays is OPEN (§13 C25; review r8 RUL-6).
  Names that denote non-values (modules, described by their map interface; run-time inputs): the kind table,
  §2.1, §13 O46. No array or map VALUE: array and map are interfaces applied to a thing, never created (RULED,
  CF:890-891). No search-result value: `occurrences` is a filter and its hits are a label's iterations (§2.6, §4.3).
- No change to plain PCRE patterns outside the opt-in; class contents `[...]` keep PCRE2's meaning (synsurv).
- No in-context reading of a pattern in a set position (refused, §11) until a measured need (D77).
- No spelling decision beyond the no-keyword rule and the modifier naming rule (placeholder throughout); no build
  (#6 not scheduled; NO BUILD GO). Not phase 1: `!` in a normal rx (PARKED), partial application (deferred),
  sections of operators other than `&`, the `count()` -> `occurs` rewrite ([COUNT-TO-OCCURS]) (§0.2).
- Not this document: DFA captures ([ENG-TDFA]), finite-group backreferences as an engine rule ([BACKREF-FINITE],
  its own unscheduled row), the Boolean IR mechanism and lookaround lowering (D196 add. 2), the standard library's
  content, a JSON database.

## 15. Provenance

COND-FAMILY.md notes by date/heading; "11-12" = the 2026-11-12 sections, etc. "predx" = `docs/dev/lanes/predx_report.md`.
"r1" = review `docs/dev/reviews/2026-11-14-r1-predspec.md` (finding ids from its critic files).

| section | notes consolidated |
|---|---|
| rev 13 (rulings and review r14 sites) | CF:1026-1031 on main (`occurrences`) -> §2.6, §8, §0.3, §2.7, O61, every row and case naming the transform; CF:1033-1053 on main (`anchored`'s exact ends, as corrected; rx-text `&` where `\|` alternates) -> §8, §11, L68, E-HTTP, O60 (d), O62, O64, §0 G3, §5.4 `&` row; CF:1054-1062 on main (both `&` operands filter roles; the warning; the condition) -> §11 THE ONE ANCHORING RULE and THE AMPERSAND RULE TESTED BY POSITION, §7.1, L11, L39, L41, L70, L71, O65. CF:1068-1081 on main (rulings R-1: per-call hit label; no count warning; the hole example) -> §2.6, O55, O63, L66, §11 table (iii), owner questions. Review r14 (F1, F2, CENSUS-1..8, `\Z`) -> §0.1, §0.3, §2.6, §2.7, §8, §11, §12, §13. Oracle runs: `docs/dev/lanes/predspec13_anchor.py`/`.out` |
| rev 12 (anchoring and naming sites) | CF:1001-1024 (ONE anchoring rule, `anchored()`, the naming of provided transforms): CF:1011-1014 -> §11 THE ONE ANCHORING RULE, §0.3 "scoped match", §0 rulings table, L63, L69, §2.6 ANCHORS IN THE ARGUMENT, §2.7, §12 REV 12, O49; CF:1014-1015 -> §8 `anchored`, L68, L69, O62; CF:1016-1019 -> §8 gap bodies, L17, FIXB-9 (2) withdrawn; CF:1019-1020 -> §11 REJECTED, L69; CF:1020-1024 -> §0 naming rule, §0.3, §2.6, §2.7, §8, O61. The brief's carried owner questions -> §13 OWNER QUESTIONS AFTER REV 12, O63. Oracle runs: `docs/dev/lanes/predspec12_anchor.py`/`.out` |
| rev 9 (all sections touched) | CF:927-947 (search follows PCRE's matching; a bound name holds the transformed rx; min/max settings): CF:929 -> §2.6 owner's example, §5.1, O54; CF:932-936 -> §2.6, §4.3, §8, C36; CF:933-940 -> §2.6 `min` and ZERO HITS, §4.2 boundary, §4.3 table, L36, L55, L56, O28; CF:941-944 (the manager's note (a)) -> §4.5 build-or-refuse (LEAN), §6.1; CF:944-947 (note (b)) -> §2.6 `contains` = `search(x, min = 1)`, L58, O58. CF:948-961 (ONE reading everywhere; ambiguity the author's; no `max`): CF:950, CF:953-955 -> §4.5 rewritten, §0.3 glossary, L34, L59, C36, O33, C11; CF:949-950, CF:955-957 -> O57, §0 standing questions; CF:950-951, CF:957-959 -> §5.6 validation example, §7.1 `label.ambiguous`, §4.5; CF:951-952, CF:960-961 -> §2.6, §8, §0.2, O58. The brief's manager's calls -> O53, O31, C7, §2.6/§8 `(?s)` and the DECIDED BY THE MANAGER list. CF:180 -> O28 |
| rev 10 (all sections touched) | review `docs/dev/reviews/2026-11-15-r10-predspec9.md` (DISPOSITIONS RULED) -> §0.1 L17, L25, L34, L48-L59, L60-L66, §2.6, §3.2, §3.4, §4.2-§4.5, §5.1-§5.6, §7, §7.1, §8, §11, §12, §13. CF:962-971 (`min` 0 or 1; the warning for the author's own text) -> §2.6, §4.5, §7.1, O58, O59; CF:972-988 (captures for one hit; one budget; count a numeral; `&` all or nothing) -> §4.3, §4.6, §8, §2.1, §11, C23, O39, O40, O50, O60; CF:989-996 (filters anchored at both ends) -> §11, §2.6, §8, L17, O49; CF:997-1000 (per match, on main after the lane's base; rulings R-1) -> §4.2, §4.3, §2.6, L55, L56, L65, O28 |
| rev 8 (all sections touched) | CF:880-887 (the search result as the ARRAY of all results) -> §2.6's owner's example, O50; CF:888-901 (the four answers): CF:889 -> §0.2, §5.2, §5.4 `:`, L49, O48, O52 (c); CF:890-891 -> §0.3 interface, §1, §2.1 kind table, §3.1, §3.2, §3.4, §5.4, §9, §14; CF:891-892 -> §7, O46, kind table; CF:892/CF:898-899 -> §3.2 tool 4, §5.4 `.`, O31, C29; CF:902-926 (SEARCH IS A TRANSFORM) -> §0 rulings table, §0.1 L16, L17, L31, L36, L50-L54, §0.2, §2.6, §3.4, §4.3, §4.5, §5.1, §5.3, §5.4, §8, §11, §12, C17, C28, O12, O28, O29, O36, O38, O50, O52, C36, O53-O56; CF:62 -> §4.3, O56 (2); CF:180 -> O28 |
| rev 7 (all sections touched) | review `docs/dev/reviews/2026-11-15-r8-predspec6.md` P6-1..P6-18 (critic texts in its directory) with its DISPOSITIONS RULED; CF:880-887 (the search result is the ARRAY of all results) -> §2.6, §3.4, §8, §0.1 L16/L50/L51, O50, and the owner's example (via the predspec7 brief) -> §2.6, O50; CF:761-768 (the filtered span) -> §11 ONE SPAN PER FILTER ROLE, §2.7, §8, L17, O49 (P6-5); CF:362 -> §2.3, §5.1, §11 (the macro-in-a-hole error, P6-1); CF:847-856 (the owner's own words behind the type picture) -> §0 marks table, §2.1, §3.1, §5.4 (P6-10); CF:113 -> §7, §11 (the `(?&name)` crossing, SIM-9); CF:548 -> §8, C25 (P6-2); CF:75 -> O50 (D) |
| rev 6 (all sections touched) | the type picture, CF:846-878: CF:858 (two kinds, condition = macro, filter a role) -> §2.1, §2.2, §3.5, §14, C19, O40; CF:860 (one input rule) -> §2.1, §2.3, §2.7, §5.2; CF:863 (comma, brackets, `=`, `:`) -> §5.4, §3.1, §3.2, §4.1, L23, C5, C8, O30; CF:866 (record never a value, three positions, map view, one-way, no sequence closure) -> §5.4, §3.1, §4.1, §5.2, §0.2, §7, §8, L43-L47, C25, O41-O47; CF:873 (search returns an rx) -> §2.6, C29; CF:876 (the manager's TO CHECK list) -> O41, O42, C25, O47 |
| 0 | rev 5: §0.2 from CF:753, CF:795, CF:804, CF:840; legend per the audpred findings; 11-12 base requirements; 11-13 COST METRICS; Frank 11-13 (#6 not scheduled), 11-14 (charter); goals are the manager's draft; rev 2: Q5 (G2), C2 + empty-match (G3), Q12 + enumerate (G4); rev 3: 11-14 Q1 critic framing (G0), r1 OWN-13 (table), OWN-14 (G3), OWN-15; the table's rows from r1 Q1R/Q1X/OWN/RUL |
| 1 | 11-14 LAYERING; 11-14 predx Q8; r1 RUL-14.4 |
| 2.1-2.3 | rev 4: 11-15 RULING (subject never an argument), 11-14 RULINGS (C1); 11-14 fractional rx + addendum; 11-14 `!`; 11-14 SUPERSEDES field-wise `&`; D196 + add. 1-2; 11-14 import follow-up (module = map); 11-14 counting; rev 5: CF:753 (C34), CF:782, CF:795, CF:804, CF:813, CF:823 (numbers, `!`, currying); rev 3: 11-14 RULING OWN-1 (pure `&`); r1 OWN-2, RUL-2, OWN-5, RUL-14.2 |
| 2.4 | 11-13 LITERALS DECIDE; 11-14 00:10; 11-14 RULINGS on §13 (C9); 11-14 RULING OWN-1 (`padded`); r1 RUL-14.6 |
| 2.5-2.6 | 11-13 NO CONCATENATION OPERATOR; 11-13 SEARCH notes; 11-14 00:10; D193 add. 3; 11-14 RULING Q1; r1 RUL-1, RUL-5, Q1R-6, RUL-14.5 |
| 2.7 | 11-14 RULING OWN-1 (transforms are FILTER MODIFIERS); predx S1, §8.2 (the pullback) |
| 3 | 11-14 00:10; views; spelling vs logic; index base; `[]` positional; 11-14 predx Q7; 11-14 predx gaps (ARRAYS OF FILTERS); r1 RUL-9, OWN-8 |
| 4 | rev 5: §4.6 thresholds marked LEAN per the audit, example per CF:749; rev 4: 11-14 follow-up (patterns take no arguments); 11-14 01:00; 11-13 late; 11-13 DESTRUCTURING, AMBIGUITY notes, MAPPINGS; 11-14 predx Q2, Q4, Q6/Q9; 11-14 value-vs-value (cont.); predx S3; 11-14 counting; rev 3: 11-14 RULING C22 + addendum; r1 RUL-14.1 |
| 5 | rev 5: CF:753, CF:804 (sections, no partial application in phase 1); rev 4: 11-14 follow-ups + 11-15 RULING (parameters, sections, no lambda); 11-13 BLOCK SHAPE, NAME RESOLUTION; 11-13 evening; 11-14 join, compose, curry, marks; 11-14 Q6/Q9 (no keywords, assertions); 11-14 import/export + follow-up (`@`); 11-14 predx gaps (ENUMERATE); predx S8; rev 3: C22 addendum; 11-14 RULING Q1; r1 OWN-7, RUL-6, OWN-10, Q1X-5 |
| 6 | rev 5: CF:63 (next-end caveat restored); 11-14 capability levels; 11-12 base requirements; 11-14 predx Q5, Q11; 11-14 RULINGS cont. (`&` at `vm`); predx S9, S10, §3.9 F33; r1 Q1X-8 |
| 7, 7.1 | 11-13 RECURSION RULE NARROWED, IMPORT, COST notes; 11-14 file_text + records; 11-14 predx Q12, Q13; predx S6, S14; 11-14 import/export + follow-up + addendum; 11-14 empty-match RULING + amendment; rev 3: 11-14 RULING Q1 (nullability in context); r1 Q1R-9, Q1R-10, Q1X-8, OWN-7, RUL-14.1 |
| 8 | rev 5: CF:782, CF:823, CF:832, CF:840 (`count()`, `occurs`, budget, [COUNT-TO-OCCURS]); 11-12 STANDARD LIBRARY; 11-13 STRING OPERATIONS; 11-13 late; 11-14 blessed callouts; 11-14 counting; 11-14 predx gaps (TUPLE CONDITIONS); 11-14 Q6/Q9 + import (assert); rev 3: 11-14 RULING OWN-1, C22 (semver comma form) |
| 9 | 11-14 predx Q8; predx §9 |
| 10 | 11-14 runtime eval + addendum |
| 11 | rev 5: CF:761 (the filtered span), CF:753 (C35), CF:795 (rx additions); rev 4: 11-14 RULINGS (C32); 11-14 outer layer, ERRATUM; 11-13 literal/hole/parameter notes; 11-14 RULINGS on §13 (C4) and RULING C2; 11-14 predx Q3, Q5, Q10; rev 3: 11-14 RULING Q1 foundation (SUPERSEDES predx Q1 / C15 / S2's context-marked sets); D193 add. 3; r1 Q1R-1, Q1X-2, Q1R-12, Q1X-1, OWN-14 |
| 12 | rev 5: E-CAL per CF:749 (no filter called with a subject), E-HTTP `count()` per CF:823/832; rev 4: E-CTX-1, 5, 7 per the C32 ruling, E-HTTP per C31; rev 0 sources; rev 2 rewrites per §§2.7, 4.4, 5.6, 7; E-HTTP from 11-14 counting; E-SEP from 11-14 ENUMERATE; E-DEPTH from predx §3.9 + Q12; rev 3: renamed per OWN-1; E-SEP index per r1 OWN-10; E-FILE per r1 Q1R-10/Q1X-7; E-CTX-1..6 per r1 Q1X-9, E-CTX-7 per r1 Q1R-4 |
| 13 | rev 5: C6 (CF:81, CF:117), C21, C33-C35, O23 resolved; C23 restated (CF:795); O39-O40 from CF:659-663, CF:813-832; cross-reading of all notes, D196, D193 and the 2026-11-14/15 rulings (lanes predspec, predspec2, predspec3, predspec4); rev 3 open items O26-O38 from r1's OWNER dispositions; rev 4: 11-14 RULINGS on rev 3's contradictions (C1, C30, C31, C32), 11-14/15 follow-ups and RULING "Agree with mapping" (C20, C30), new C33-C35 |
| 14 | 11-12 scoping; 11-13 late JSONL; D196 add. 2; synsurv; 11-14 predx Q10; 11-14 RULING Q1 (named in-context form only on measured need) |

Background documents: `cond_family.md` (members, machinery M1-M12, D193 answers) is still the mechanism map;
`cond_family_syntax_survey.md`'s `&!` and `=~` spellings are superseded (`!` filter; rev 7's `~`, itself withdrawn in rev 8 for the
`search` transform), its "opt-in, not default"
and "do not touch class contents" recommendations stand.
