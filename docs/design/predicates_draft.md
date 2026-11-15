# The predicate language ([COND-FAMILY] #6): a preliminary specification for critical analysis

## Changelog

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
  O28, O36, O52 restated; C36 (a CONFLICT: the priority parse vs §4.5's some-parse rule) and O53-O57 new.
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

**Status: DRAFT rev 8 (lane predspec8, 2026-11-15). NOT a ruling, NOT scheduled, NO BUILD GO** (Frank 2026-11-13:
#6 not scheduled; 2026-11-15, relayed in the predspec5 brief: "the predicate work is not a go to build as we are
still in design"). Purpose (Frank 2026-11-14): "create a preliminary predicate spec doc with our latest ideas for the
purpose of critical analysis. Provide reasoning." It consolidates the dated notes in
`docs/design/plan_row_bodies/COND-FAMILY.md` ("CF"; the source of truth; the LATEST note on a topic wins, and the
owner's QUOTED words outrank a manager paraphrase beside them), the parts of `docs/dev/lanes/predx_report.md` that
the rulings adopt, and review 2026-11-14-r1-predspec. Older background, `docs/design/cond_family.md` (survey rev 0,
D193) and `docs/design/cond_family_syntax_survey.md` (lane synsurv), is cited where still live. Every rule traces to
a note, a ruling or a review finding (§15); where they are silent or disagree, §13 lists both readings.

**SYNTAX IS PLACEHOLDER THROUGHOUT.** The owner rules semantics; spelling is a later design step (D193 add. 4).
One spelling RULE is ruled (§5.1): no alphabetic operators or statement keywords; and one NAMING rule (§2.7):
a transform's name describes the subjects it accepts. Examples use the latest spellings: `/.../` rx literals (bare rx
fragments are never admitted in the expression language), `:=` define, `,` "next entry" inside `[ ]` (ARRAY, any
one entry) or `( )` (RECORD, all entries together), `=` labels an entry, `:` constrains a label that exists (THE
grammar summary is §5.4), `==` the equality comparison, `X[...]` positional, `&` (pure intersection) / dot for
filtering and labels, `where` for structural selection, conditions `(x: S, y: T)`, transforms as FILTER MODIFIERS
(`x & padded(between(1, 12))`), operator sections `(& f)`, `@` effects, modules as `m := import("m")`, 1-based indexes,
search as the library transform `search(rx)` (rev 7's `~`/`!~` are withdrawn, §2.6).

Status marks (rev 8; every mark is one of three):
- **RULED (CF:n)**: the owner's own words at line n of COND-FAMILY.md (or a D-number) cover the rule; it reaches only
  as far as his quoted words, not a manager gloss beside them. THE TYPE PICTURE (CF:846-879) is a manager's RECORD
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
| one-iteration access at a higher capability level (CF:924-926) | none | the MANAGER'S LEAN, "stated to him twice, not separately ruled" (CF:925-926): LEAN, not RULED |
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
| G3 | PCRE COMPATIBILITY: a one-literal program IS today's PCRE pattern, with PCRE's meaning (no subset, no level beyond today's engine choice) | existing PCRE users; the corpus | the whole `.rxt` corpus, each pattern wrapped as `/.../` (with `/` escaped as `\/` and the case's flags transferred to the literal), answers identically to today (a nullable one-literal program gets the `empty.search` WARNING only, §7) |
| G4 | STRUCTURE OF SPELLED THINGS IS COMPILE-TIME ONLY, TOTAL, TERMINATING: every structural evaluation (each, join, records, indexing, imports, enumerate) over a SPELLED array (§3.4) is finite and ends; a repeated label's ITERATIONS (a search's hits included) exist per match and are questions of the automaton (G2), outside this goal (§3.4, §4.3) | the compiler's users (no hang at build), the security story | recursion through parameterized definitions only by a strictly decreasing literal parameter (§7); every structural operator ranges over finite declared things, `enumerate` under a budget; a fuzzer over programs never hangs the compiler (watchdog) |

Constraints on every goal (ruled RULES, not ranked goals): no alphabetic operators or keywords (§5.1); `&`, `|`,
`!` extensional (§2.2). Non-goals: §14. G0 is the owner's ("STANDING CRITERION ... ranked first for this design",
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
| L7 | `x: /^S\w*/` vs `x: startsWith("S")` | SAME | in a filter `^` is the start of the span being filtered (§11) | CF:732, CF:761, D193 add. 3 |
| L8 | `num := /\b\d+\b/`: `/x${num}/` vs the pasted `/x\b\d+\b/` | DIFFERENT: ERROR | the hole form is the EDGE-ASSERTION ERROR ("put `\b` in the pattern that places num") | Q1X-3 (iv), Q1R-3 |
| L9 | `p := /(?<=\$)\d+/`: the program `p` (searched) vs `[n = /\d+/] & (n: p)` | DIFFERENT: ERROR | the condition is the EDGE-ASSERTION ERROR; the searched final pattern keeps PCRE meaning | Q1X-3 (iii), Q1X-1 |
| L10 | `\w{3} & /\w+\b/` vs `/\w{3}\b/` | DIFFERENT: ERROR | the first is the EDGE-ASSERTION ERROR (no silent move foo -> bar) | Q1X-2 |
| L11 | `alts & !/^#.*/` vs `alts & !startsWith("#")` | SAME | `^` is the filtered span's start (§11) | CF:761 |
| L12 | `"5" & /(?<=\$)\d+/` in `@assert.none(...)` vs `"5" & /\d+/` | DIFFERENT: ERROR | the first is the EDGE-ASSERTION ERROR (an assertion argument is a set position, §5.6) | Q1X-5 |
| L13 | `x & padded(/^5/)` vs `x & padded(startsWith("5"))` | SAME | `^` is the start of the span the modified filter reads (§11); `padded(/\b5/)` stays the EDGE-ASSERTION ERROR | CF:761 |
| L14 | `enumerate(/(?<=a)[bc]/)` vs `enumerate(/[bc]/)` | DIFFERENT: ERROR | the first is the EDGE-ASSERTION ERROR | Q1R-8, Q1X-6 (b) |
| L15 | `@warn.off(/^dead\./)` vs `@warn.off(startsWith("dead."))` | SAME | `^` is the start of the name (§11) | CF:732 (LEAN extension, §11) |
| L16 | `(m: search(/^err/))` vs `(m: contains(/^err/))` | DIFFERENT: BY DESIGN | `search` NEVER REJECTS (as a set it is every string; what it adds is the repeated label `hit`, one iteration per hit, here at most one, at m's start); `contains` is the TEST (one hit needed). The search filters nothing until a question is asked of its hits (`some(...)`, `count(...)`, a plain condition; §2.6, §4.3) | CF:907-909 (accepted at CF:905); rev 7's `$m ~ /^err/` row withdrawn with `~` |
| L17 | `(m: contains(/^err/))` vs `(m: startsWith("err"))` | SAME | a filter passed as an argument filters the span the call's filter role filters, so `^` is m's start in both (§11 THE FILTERED SPAN); `(m: !contains(/^err/))` is the negated test (rev 7's `$m !~ /^err/`, withdrawn, §2.6) | CF:761 (LEAN, r8 P6-5) |
| L18 | a nullable final search pattern: `/\b/` vs `/a*/` | SAME | both are nullable IN CONTEXT: `empty.search` WARNING for a one-literal program, ERROR in a predicate program (§7) | Q1R-9 |
| L19 | `(?m)^\d*` searched vs the same pattern in whole-subject mode | DIFFERENT: WARNING | by MODE only: `empty.search` in search mode, none when anchored (a `^` in the pattern does not exempt) | Q1R-9 |
| L20 | `/\d\d/ & padded(between(1, 12))` vs `/\d\d/ & between(1, 12)` | DIFFERENT: GAP | GAP: the second is {10, 11, 12} by the C9 ruling (string sets, canonical numerals); no warning is named for a padded target against an integer comparison set | C9, OWN-2 |
| L21 | `!<200` vs `>=200` | DIFFERENT: GAP | on targets with non-canonical members (`0150`, `abc`: kept by `!<200`, refused by `>=200`): GAP; in where they may stand (`${>=200}` legal, `${!<200}` the unapplied-macro error): the unapplied-macro error. §13 O26 | OWN-2, RUL-2 |
| L22 | `(x: <200 \| >900)` vs top-level `x & <200 \| >900` | DIFFERENT: GAP | inside a condition `\|` binds tighter than `:` (x in either range); at top level D196 parses `(x & <200) \| >900`, a full rx that widens the program; `precedence.section` (proposed, PLAN) | C22, RUL-15 |
| L23 | `(x: <200, y: >55)` vs `[(x: <200), (y: >55)]` | DIFFERENT: BY DESIGN | AND vs OR, said by the BRACKET (`( )` all together, `[ ]` any one; §5.4); the comma means "next entry" in both, so the look-alike the review flagged (one comma, two logics) is gone; whether the bracket difference still needs a diagnostic: LEAN no (§13 O30 RESOLVED, O38) | OWN-9, CF:863 |
| L24 | `x := /a\|b\|c/`: `/${x}\|d/` vs `x \| /d/` vs `/a\|b\|c\|d/` | DIFFERENT: GAP | one language, different entries: `[2]` and the default-level `.index` differ; `array.hole` (proposed, PLAN) | OWN-8 |
| L25 | `/a\|b/` vs `/b\|a/` | DIFFERENT: BY DESIGN | SAME under `& \| !`; differ under `[]`, `.index` and PCRE priority (§3.4: structural tools read the spelling); whether a documented structural difference also needs a diagnostic: §13 O38 | §3.4 |
| L26 | `enumerate(/[-\/.]/)` vs `enumerate(/[.\/-]/)` | SAME | class members in codepoint order (§5.5) | OWN-10 |
| L27 | `X[<4]` vs `X[1\|2\|3]` | SAME | numeric filters range over positions 1..n (§3.2) | RUL-9 |
| L28 | `$x & S` as a condition vs `(x: S)` | DIFFERENT: ERROR | the first is an ERROR "did you mean `x: ...`?" (§4.1) | §4.1 |
| L29 | `a := 256` vs `b := "256"` under `<a` / `<b` | DIFFERENT: GAP | GAP; OPEN (§13 O27) | OWN-3 |
| L30 | `!(x: S)` vs `(x: !S)` on a repeated, optional or zero-iteration label | DIFFERENT: GAP | GAP; OPEN (§13 O28) | OWN-4 |
| L31 | `some((g: "x", h: 1))` vs `some((g: "x")) & some((h: 1))` over a repeated label (search hits included) | DIFFERENT: BY DESIGN | SAME HIT BY RECORD: one record = all its entries on the SAME iteration; two `some` calls may be met by different iterations (§4.3; on hits `x2 y1` of `/(?<g>[xy])(?<h>\d)/`: the first false, the second true). Replaces rev 7's GAP row (two `occurs.some` vs one `some(s)`); §13 O29 RESOLVED | CF:915-917 (accepted at CF:905) |
| L32 | `/${q}/m` vs the inlined text of `q` | DIFFERENT: GAP | GAP; `flag.hole` (proposed); OPEN (§13 O32) | Q1R-11 |
| L33 | `\k<s>` vs `${$s}` vs `each(..., enumerate(...))` on a finite label | DIFFERENT: GAP | different levels today; OPEN (§13 O34) | RUL-7 |
| L34 | `(a: <5) & (b: <5)` on an ambiguous two-label parse: default level vs `vm` | DIFFERENT: WARNING | `label.ambiguous` WARNING (per label); multi-label reading OPEN (§13 O33) | RUL-3 |
| L35 | `(?J)` duplicate label vs a repeated label, under `x: S` | DIFFERENT: GAP | GAP; OPEN (§13 O35) | RUL-16 |
| L36 | `(x: S)` vs `all((x: S))` on a repeated label | SAME | `all(...)` is the default, "rarely written": a plain condition already means every iteration (§4.3); rev 7's `occurs.all` leaves (`occurs` keeps counts only); on ZERO iterations both follow §13 O28 | CF:912-913 (accepted at CF:905); C28 RESOLVED |
| L37 | `(wname.index: ==wd)` vs `(b: >$a)` | OPEN | a computed label read bare vs with `$` (§13 C13; E-RFC's `==wd` and E-CAL's `<=dim` both rest on it) | OWN-11, r8 P6-11 |
| L38 | `isodate(x).year` vs `(x & isodate).year` | DIFFERENT: ERROR | the first is a compile ERROR (a pattern takes no arguments; hint "write `x & isodate`"); whether `.year` of `x & isodate` is a value or a pattern: OPEN (§13 C29) | RUL-8, 2026-11-15 RULING |
| L39 | `A & B` vs `B & A` | SAME | the same subjects are accepted; the left operand picks the REPORTED span among overlapping qualifiers (D196), so the report may differ (§2.2) | C1 ruling |
| L40 | `isodate(year: S)` vs `isodate & (year: S)` | DIFFERENT: ERROR | the first is a compile ERROR: a pattern has no parameters; hint "write `isodate & (year: ...)`"; a parameterised pattern is a macro, `date_in(years) := isodate & (year: years)` (§5.2) | CF:744 |
| L41 | `/\w+/ & /^foo/` vs `/\w+/ & startsWith("foo")` | SAME | `^` in a filter is the start of the span being filtered (the `\w+` word), not of the subject (§11) | CF:761 |
| L42 | `n := count((name: S))` then `headers & (n: ==1)` vs `headers & occurs.exactly(1, (name: S))` | SAME | one count, two spellings; `count()` is refused only over the BUDGET, naming the `occurs` form (§8) | CF:823 (LEAN), CF:832 |
| L43 | `[x = /foo/, y = /bar/]` vs `(x = /foo/, y = /bar/)` in value position | DIFFERENT: ERROR | the second is a compile ERROR: "a record is not a value; for any one of the entries write `[ ... ]`" (§3.1, §5.4); the rev 5 map literal `(x = /foo/ \| y = /bar/)` is withdrawn (§13 O42) | CF:863, CF:866 |
| L44 | `(x)` vs `x` in value position | SAME | parentheses with one unlabelled entry are GROUPING; a one-entry record exists only where a record stands (a call `f(x)`, the left of a binding), so no value is ever a one-entry record (§5.4; §13 O41) | CF:866 (LEAN) |
| L45 | `f(1, 2)` vs `f((1, 2))` | DIFFERENT: ERROR | the second is a compile ERROR: a call is the macro applied to ONE record, and an inner record would be a record used as a value (§5.2) | CF:866 (LEAN) |
| L46 | `isodate & (year: 2000)` vs `c := (year: 2000)` then `isodate & c` | SAME | a condition is a MACRO, a value; binding it is L2's case; the record is its written body, never the bound thing (§2.1; §13 O45) | CF:858, CF:866 (LEAN) |
| L47 | `[x: S]` vs `[(x: S)]` | DIFFERENT: ERROR | the first is a compile ERROR: `:` constrains a label of what the record is laid against, and an array entry is laid against nothing; hint "write `[(x: S)]`" (§5.4) | CF:863 (LEAN) |
| L48 | `x := /a\|b\|c/`: `[x, /d/]` vs `x \| /d/` | DIFFERENT: BY DESIGN | SAME under `& \| !` (one language); under structural tools `[x, /d/]` has 2 entries (each entry of `[ ]` is ONE entry, like a group or a hole, §3.3, §5.4) and `x \| /d/` has 4 (`\|` concatenates arrays) | r8 P6-14 |
| L49 | `m(x: T) := ...` then `m(A)` vs `A & (x: T)` | DIFFERENT: ERROR (phase 1) | typed parameters are OUT of phase 1 (the owner: "keep out of phase 1", CF:889), so in phase 1 the first form is an ERROR ("a parameter takes no constraint in phase 1; constrain where it is used") and `:` has ONE behaviour, it narrows. In the design (types "need more thinking", CF:889) rev 7's difference (`:` checks in a head, narrows in a condition) stays unruled (§13 O48) | r8 P6-4; CF:889 |
| L50 | a record on the left over a search, rev 8 spelling `(x, y) := $m & search(/(?<a>\d)(?<b>\d)/)`: laid over the search pattern's GROUPS vs read as the first two HITS (Python's `x, y = re.findall(...)`) | OPEN | design only, out of phase 1 (§0.2). Rev 8 removes the second reading's footing (hits are iterations of a label, reached by the array interface over iterations, never entries of a value), so the lean is the first: the record is laid against the map interface (groups); x and y are then REPEATED labels, one iteration per hit, paired by iteration. Whether the form survives the withdrawal of `~` at all: §13 O55 | r8 P6-7 (DRIFT-6); CF:852 |
| L51 | `(m: !search(r))` vs `(m: !contains(r))` | DIFFERENT: ERROR | `search(r)` accepts every string, so `!search(r)` is EMPTY: the empty-intersection ERROR at a narrowing site (§5.2), hint "for no hit write `!contains(r)`". Replaces rev 7's `!($m ~ r)` vs `$m !~ r` GAP row (both operators withdrawn) | CF:909 (accepted at CF:905); §5.2 (LEAN) |
| L52 | `(m: search(r) & (g: "x"))` vs `(m: search(r) & some((g: "x")))` | DIFFERENT: BY DESIGN | the LOOK-ALIKE ROW the transform ruling requires: a plain condition on a hit's label means ALL hits (the sequence rule, §4.3); "some hit" is `some(...)`. On `abx aby abx` with `r = /ab(?<g>[xy])/`: the first rejects (hit 2 has g = y), the second accepts. Whether it also gets a named warning: §13 O38 | CF:920-921 (accepted at CF:905) |
| L53 | `(m: search(/a*/))` vs find-all of `/a*/` (Python's `re.findall("a*", "baa")` = 3 results) | DIFFERENT: ERROR (lean) | the lazy-gap definition stops at an EMPTY hit (PCRE ends a loop whose iteration matched empty: 1 hit on `baa`); rev 8 refuses a search argument that can match empty, naming `x & !""` (§2.6, §13 O53) | CF:919-920 (accepted at CF:905); LEAN |
| L54 | `x & s` with s an rx vs `some(...)` | DIFFERENT: BY DESIGN | `x & s` is MEMBERSHIP in the rx s (any one entry under `&`, §3.4); `some(...)` asks whether some ITERATION of a repeated label meets a condition (§4.3). Rev 7's three spellings of "some result" (`x & s`, `some(s)`, `occurs.some`) become one: `some(...)` | CF:913-914 (accepted at CF:905) |

**REASONING.** The owner's framing: "complex context could cause predicates to just not work and it's not clear how
the obscure rules impact it ... that's why it was so important to me that things that look like they should do the
same thing actually do." A ranked goal without a checkable table would lose every tie to G1 (review OWN-13); the
table makes G0 testable, and a D27 spec-first author writing acceptance cases from the table alone is its natural
independent control (review "D27 recommendation").

**STATUS.** G0 as the first criterion: RULED (CF:691). G0 as a goal row and the table: LEAN (review OWN-13). Rows
L1-L2: RULED (CF:722); L3-L4: RULED (CF:698); L7-L19: RULED (CF:713 as superseded in part by CF:732 and CF:761: `^`/`$`
in a filter are the filtered span's ends), except L16 and L17, which rev 7 rewrote: L16's difference of kinds is
the ruled search result (CF:873, CF:881-883) and its filter-role reading is OPEN; L17 is LEAN (P6-5, the filtered
span applied to a filter passed as an argument, until the owner confirms); L5, L38, L40: RULED (CF:744, CF:749);
L39: RULED (CF:732); L41: RULED (CF:761); L42: LEAN (CF:823 "perhaps"; the budget rule RULED, CF:832); L23's reason:
RULED (CF:863); L43's error: RULED (CF:866, a record is never a value), the withdrawal of the map literal it names:
LEAN (§13 O42); L44-L47: LEAN (this document's readings of CF:858-866); L48-L51 (rev 7): BY DESIGN rows state the
rule of the section cited, OPEN/GAP rows their §13 item; the class on each DIFFERENT row: LEAN (review r8 P6-9); other
rows state the rule of the section cited. Rev 8: L16, L31, L36, L51, L52, L54 rest on the transform ruling as
accepted ("Do it", CF:905), not on the owner's own words; L53's refusal and L51's error class are this document's
LEAN; L49's phase-1 verdict is RULED in his words (CF:889); L50 stays OPEN with a lean (§13 O55).

### 0.2 Phase 1 scope (what the owner said is in and out of the first build)

Nothing is scheduled and there is no build go (Status above); "phase 1" is the owner's name for the first,
base-level predicate build whenever it is chartered.
- IN: THE PREDICATE PART ITSELF, the primary goal of this design (CF:795: "the primary goal of the predicate design is
  the predicate part itself"). RULED.
- IN, and the ONLY additions to the rx language: the `${}` hole and `&` (CF:795: "extra elements added to rx like ${}
  and & are necessary parts of that"). RULED. Where `&` may stand in rx text: §13 C23.
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
  §13 O55.
- OUT: TYPED PARAMETERS (`m(x: T)`, the containment check in a definition head). RULED (CF:889: "yes keep out of
  phase 1. I like the idea of types but they need more thinking"). In phase 1 `:` narrows only (§5.2, §5.4); the
  property mark `m(p: pure)` and `pattern()` leave with them (§13 O48).
- IN: the GROUP QUESTIONS on a repeated label, search hits included: a plain condition (all iterations), `some(...)`,
  `all(...)`, `count(...)`, `occurs.exactly/at_least/at_most/none` ("compile to states and are phase 1": CF:922-924,
  accepted at CF:905). NOT the default level: access to ONE iteration (`$m.hit[2]`, keep iterations 1 and 3), which
  needs captures inside a loop (CF:924-926: the MANAGER'S LEAN, LEAN; §4.3).
- Not stated by the owner: which library pieces (§8) and levels beyond the default (§6.1) phase 1 carries; and, of
  the constructs NO §12 case uses (the TWO-WAY CENSUS, §12: operator sections in code, the `search` transform and
  `some`/`all`, positional `X[...]`, `where`/`where_group`/`each_group`, `when`, `eval`, `@export`/`@warn`, `*`/`%`,
  `.label`), which stay in phase 1. Sections are IN by ruling (CF:753); search is ruled as a library transform
  (CF:902-909, accepted at CF:905) and its group questions as phase 1 (above), but no case uses it. Rev 8 invents no
  case for them (review r8, DISPOSITIONS RULED, P6-9): the owner decides which stay.

### 0.3 Words (one word per thing)

G0b read as applying to this document's WORDS as well as to its marks (the review r8 coordinator's reading, P6-15;
LEAN). Each word below names ONE thing throughout; a quoted ruling keeps its own words, glossed where they differ.

| word | names | not used for |
|---|---|---|
| **subject** | the run-time TEXT being matched (a `search` or `contains` filter reads the filtered SPAN of it, §2.6, §11) | the operand of `&` (the type-picture record's "subject slot", CF:860, is the OPERAND slot below; CF:749's ruled phrase "the subject is never an argument" means the operand) |
| **operand** | what `&` puts into a macro's slot: the rx on the other side (`X & M` fills M's operand with X) | the text |
| **kind** | rx or macro, the two VALUE kinds (§2.1) | value-vs-pattern; constraint sets |
| **value** | anything of a kind (an rx or a macro) | a captured substring |
| **captured string** | `$x`, the text a label captured in this match (a one-string rx) | |
| **constraint set** | the rx after `:` (`x: S`, `m(x: T)`), the set a label must lie in (rev 6 said "type" or "value type") | the kinds |
| **filter role** | what stands on the filtering side of `&` (CF:858); "a filter" = a thing in that role | a kind; structural selection (`where` SELECTS) |
| **condition** | the macro written `( label: S, ... )`, laid against an operand's labels (§4.1) | a single `label: S` entry (an ENTRY of a condition); any filter |
| **section** | `(& B)`, the macro with only its operand open (§5.2) | comparisons (those are COMPARISON SETS) |
| **comparison set** | `<256`, `>=lo`, `==5`, `between(1, 12)`: a full rx (§2.4) | |
| **transform** (= **filter modifier**) | a macro filter -> filter (§2.7) | the map `t` it reads the subject through: that is the modifier's READING, and its output is "what the modified filter reads" |
| **binding** | `name := expression` (§5.1); "match-dependent binding" is a binding that reads a captured string | the C22 parse rule (that is ENTRY EXTENT, §5.4) |
| **entry extent** | how far an entry of `( )` or `[ ]` reaches: to the next comma or the closing bracket, `&`/`\|` tighter than `:` and `=` (C22) | |
| **label** | a pattern's group name, incl. a computed label (§4.4) | a macro's parameter name (PARAMETER); a module's name (MEMBER); `.index`/`.label` (METADATA) |
| **parameter** / **member** / **metadata** | a macro's named input / a module's exported name / `.index`, `.label`; members and metadata are reached by the one `.`, a field of the map interface (§5.4, CF:898-899) | labels |
| **entry** | one item of a written `[ ]` or `( )`, or of an rx's array interface (a top-level alternative) | a module's export (MEMBER); a joined part (PART); one pass of a repeated label (ITERATION) |
| **interface** | the ARRAY interface (entries in order) or the MAP interface (fields by name) APPLIED TO a thing: to an rx (§3.1), to a repeated label's iterations (array, §4.3), to a module (map, §7). The owner's word ("Array and map are interfaces that can be applied to regex but interfaces aren't themselves values that can be created", CF:890-891; rev 7 said "view"). An interface is never a value: nothing creates an array or a map | a declared type (§9: rev 7's cut "interfaces", now DECLARED TYPES) |
| **iteration** | one pass of a repeated label in one match (a search's HIT is one iteration of its `hit` label, §2.6) | an entry (spelled) |
| **hit** | one occurrence found by `search`: an iteration of the repeated label `hit` (§2.6) | rev 7's "result"/"occurrence" as an array entry |
| **record** | the written `( ... )` laid against fields (§5.4); never a value | what `records()` returns (an rx whose ARRAY interface lists the ITEMS; its pattern is the ITEM RX; the name `records` is a placeholder to rename, §13 O44) |
| **effect** | an `@` form, a compile-time statement (§5.1), not a value and not a macro | |

### Standing questions (docs/design/CLAUDE.md)

1. **Measurement regime.** Mostly not relevant: a language spec introduces no measured quantity. The numbers cited
   (ISO date with leap Feb 29 as a plain regex: 6,848 B object, 5.9 ms compile; CF:40; class counts in §4.6) are
   compile-time sizes or arithmetic, not timings. The budgets of §4.6/§8 (O39) are measured quantities when a build
   sets them, and must name their regime then.
2. **The independent control.** Relevant to §12 and G0: expected behaviours were checked against Python's
   `datetime`, a hand-written Luhn function and libpcre2 10.49 (review r1's kit), not against pcrec. At build: the
   PCRE2+callout oracle (studies/andspike, F9), an independent Python reference evaluator, standards' own test
   vectors as `@assert.*` statements (§5.6); for G0 a D27 author working from §0.1 alone.
3. **What moves when data is regenerated.** Relevant only through `file_text`/`import` pins (§7): a changed file
   under a `sha256` pin is a loud compile error; a re-pinned file changes the emitted automaton.

## 1. Layering

**RULE.** Two layers. FOUNDATION: value kinds (§2), operators and filter modifiers (§2), the array and map
interfaces (§3), match values, repeated labels and computed labels (§4), capability levels and the reporting axis
(§6), the compile-time boundary, modules and warnings (§7). LIBRARIES, built on the foundation and changeable without
it: `each`, `join`, `records`, `file_text`, standard filters and filter modifiers (`between`, `startsWith`,
`contains`, `length`, `padded`, `unpadded`, `any_case`, `quoted`), the transform `search`, the group questions
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
<200)`, `(a: 1, b: 2)`) = a macro with an operand and no parameters; a TRANSFORM (filter modifier, §2.7) = a macro
whose parameter is a filter and whose result is a filter; an operator SECTION `(& B)` = only the operand open; prefix
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
its cost (manager's view, CF:813). Under the two kinds a number is an rx, a set of numeral strings (this document's
consequence of CF:858, LEAN; §13 O40).

THE KIND TABLE (G0b's KIND COUNT; review r8 P6-8, a DISCLOSURE of everything a name or a mark can denote: the two
VALUE kinds are unchanged, the other rows are not values):

| thing | what it is | a value? | bound by `:=`? | passed as an argument? | §12 case needing it | status |
|---|---|---|---|---|---|---|
| rx (literal, comparison set, binding of an rx, captured string `$x`, a `search(r)` or `contains(r)` filter) | a set of strings | yes | yes | yes | every case | RULED (CF:858) |
| macro (condition, section, filter modifier, `!B`, parameterised definition) | awaits input: parameters by a call, operand by `&` | yes | yes | yes | E-WEEKDAY (condition), E-JSONL (`json.row`, modifiers), E-HTTP (condition argument), E-SEP (`date_sep`) | RULED (CF:858, CF:860) |
| computed label (match-dependent binding) | a macro whose operand is the pattern whose labels it reads (above) | as a macro | yes (that is its spelling) | no case passes one | E-WEEKDAY, E-CAL, E-RFC, E-NEAR (c), E-HTTP (`count`) | LEAN (P6-8 (a)) |
| record `( ... )` | a shape laid against fields: a call's parameters, a condition's labels, a result's groups (§5.4) | no | no (on the LEFT of `:=` only, design only) | no (it IS the argument list) | every call; every condition | RULED (CF:866) |
| module | `m := import(...)`: described by its MAP INTERFACE, members reached as fields by `.` (CF:891-892: "what import is is less important than that its interface is a map"); what kind of thing it is: not ruled, and matters less | no (lean) | yes, by `:= import(...)` | no (lean) | E-JSONL, E-IPV4, E-HTTP, E-DEPTH | the interface RULED (CF:891-892); the kind not ruled (§13 O46) |
| array / map INTERFACE | applied to a thing (an rx, a repeated label's iterations, a module); never created (CF:890-891) | NO | no | no | every case that indexes, joins or reads a field | RULED (CF:890-891) |
| repeated label's iterations | the passes of one label in one match (search hits included), read through the array interface (§4.3) | no (they are parts of a match) | no | no | E-HTTP (`name`) | the group questions: CF:922-924, accepted at CF:905 |
| run-time parameter | `limit := param(rx)`: an rx whose string the caller fixes per match | as an rx (lean) | yes, by `:= param(...)` | yes, as an rx | E-NEAR (b) | OPEN (§13 O46) |
| effect | an `@` form, a compile-time statement (§5.1) | no | no | no | E-IPV4, E-CAL (`@assert`) | LEAN (CF:619) |

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
label as a macro, the typing of `& | !`, the kind table and the map-view result kind: LEAN (this document, review r8
P6-8). Literals as one-string sets: LEAN. Module: its MAP interface RULED (CF:891-892), its kind not ruled (§13
O46). Array and map are interfaces, never created values: RULED (CF:890-891). Numbers ONE kind for the user: LEAN (CF:823,
"perhaps"; the owner's ideal, CF:813); the 11-14 "no number type" is WITHDRAWN as over-reach (CF:782 (3)); what a
number is: §13 O40. No boolean type: LEAN (manager's Q6/Q9 spelling lean, CF:595). No partial application in phase
1, currying kept by the design: RULED (CF:753, CF:804). The earlier "assertions (their own value kind)": withdrawn by
the two kinds (§13 C19 RESOLVED); `@` forms are effects, not values: LEAN (CF:619).

### 2.2 Operators `&`, `|`, prefix `!`

**RULE.** `&` intersection, `|` union, both EXTENSIONAL over rx operands: membership depends only on the
language, so two spellings of one language behave the same under `&`, `|`, `!`. `&` is PURE INTERSECTION:
associative and commutative, so the ORDER and GROUPING of an `&` chain never change which strings it admits (a
transform is a filter modifier, §2.7, never an `&` operand with a position). Prefix `!B` is ALWAYS A MACRO with its
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

Reported span (D196, RULED for pattern-level `&`): the left operand chooses (PCRE priority: first alternative,
greedy longer, lazy shorter), the right only filters which ends are admitted; the span SET is commutative. So
`A & B` and `B & A` ACCEPT THE SAME SUBJECTS; D196's left operand picks the REPORTED span among overlapping
qualifiers, so the report may differ (§0.1 L39; C1 RESOLVED).
Precedence (D196): concatenation, then `&`, then `|`; inside a record entry `&` and `|` bind tighter than `:`
and `=`, and the comma is no operator (it ends an entry; §4.1, §5.4). In the expression language there is no concatenation operator (§2.5).

**REASONING.** Extensional `&` keeps arrays and rx "the same". `!` as a filter: a standalone complement is useless
in a search and VM-hostile, while under `&` it is bounded. A pure `&` is what the owner's look-alike criterion (G0)
asks of the most common operator: rev 2's right-associative `&` made reordering or parenthesizing a chain with a
transform in it change the answer silently (review OWN-1, RUL-11).

**STATUS.** `&` extensional, `!` a filter: RULED (CF:328, CF:376). D196: RULED (D196). `&` pure intersection, order-
and grouping-free: RULED (CF:722, OWN-1), SUPERSEDES the right-associative `&` lean. The `!<200` / `>=200` correction
and the dropped lint: LEAN (review OWN-2, RUL-2). C1: RULED (CF:732): same matches, the report may differ. No `!`
inside a normal rx: RULED (CF:795), PARKED, the spelling question NOT closed (CF:795 corrects CF:758).

### 2.3 The unapplied-macro error

**RULE.** An unapplied macro where an rx is required is a compile error naming the fix: "filter `x: digit` has
no target; write `T & (x: digit)`"; "modifier `padded` has no filter; write `padded(between(1, 12))`". The same
error covers a macro in a HOLE: `${(x: digit)}`, `${!<200}` (the owner: a condition is "not usable as `${x: digit}`",
CF:362); a guard is written with `&` before an rx hole, `(\d+)&${ <256 }` (§11, C4). THE OPERAND IS NEVER AN
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

### 2.6 Search and contains are transforms

**RULE.** SEARCH IS A LIBRARY TRANSFORM of the `contains` family, not an operator: it takes an rx and returns an rx
over the WHOLE value in which the hit group REPEATS, once per hit, and it is applied like any filter, by `:` or `&`
(`(m: search(/ab(?<g>[xy])/))`, `P & search(r)`). The operators `~` and `!~` of rev 7 are WITHDRAWN: rev 7's
`$m !~ r` is `(m: !contains(r))`; rev 7's `$m ~ r` has no one-to-one replacement, because a search result is no
longer a value: a TEST is `contains`, a QUESTION about the hits is `search` with a group question (§4.3). The hit
needs no new concept: it is a REPEATED LABEL (§4.3), so a plain condition on a hit's label means ALL hits,
`some(...)` some hit, `count(...)` and `occurs.*` count them, and one record means one hit (SAME HIT BY RECORD).

    contains(x) := /(?s).*${x}.*/                   # a TEST: one hit needed
    search(x)   := /(?s)(?:.*?(?<hit>${x}))*.*/     # every value; each hit is one iteration of the label `hit`

(Library text, §8; spelling placeholder, D193 add. 4. The owner's sketch `search(x) := /.*(?:(${x}.*).*/`, CF:903-904,
is the idea; the shape is the record's requirement (5), CF:918-919. `(?s)` makes the gaps cross line breaks; it does
not reach into the hole, a literal's flags are never inherited by a hole's pattern, §11, §13 O32. The label name
`hit` is a library placeholder, §13 O56.)

THE DEFINITION'S REQUIREMENTS (CF:918-921, accepted at CF:905), and how the text above meets each:
1. LAZY GAPS, so the hits are LEFTMOST and NON-OVERLAPPING. In PCRE's priority parse of `(?:.*?(x))*.*` against the
   whole value, the outer `*` (greedy) tries one more hit before stopping, and the lazy gap tries the shortest gap
   first, so each iteration takes the leftmost place where x matches; the rest of the pattern always succeeds (the tail
   `.*` takes what is left), so nothing backtracks into a hit and each hit is x's own PCRE-preferred match at that
   place. That is PCRE2's find-all order (the C find-all iterator's), for an argument that cannot match empty.
2. A REPEATED LABEL'S COUNT FOLLOWS PCRE'S PRIORITY PARSE (which with lazy gaps is find-all order). As a SET the
   pattern is every string and it has other parses (a gap can swallow a hit), so the hits are the iterations of the
   PRIORITY parse, not of "some parse". This is a CONFLICT with §4.5's ruled some-parse rule for ambiguous labels: §13
   C36 gives both readings and does not pick.
3. THE EMPTY-MATCH ADVANCE. PCRE ends a loop whose iteration matched the empty string, so an argument that can match
   empty gives at most ONE hit (the first, possibly empty) where find-all advances and continues (`/a*/` on `baa`: one
   empty hit at 0; Python's `re.findall("a*", "baa")` gives `['', 'aa', '']`, three; §0.1 L53). Rev 8 (LEAN): a
   search argument that can match empty is a compile ERROR naming the fix `x & !""` (the same hazard the empty-match
   rule refuses for a predicate program's final pattern, §7); the alternative, PCRE2's find-all advance rule written
   into the library text, is §13 O53.
4. THE LOOK-ALIKE ROW: "`(g: x)` on a search result means ALL hits" is §0.1 L52 (BY DESIGN).

THE ANCHORED ARGUMENT. `^`/`$` in the argument are the ends of the span the enclosing filter role filters (§11 ONE
SPAN PER FILTER ROLE; §13 O49), not of the hole the body puts the argument in. So `search(/^err/)` can hit only at
the value's start: AT MOST ONE HIT. This is the rev 7 rule unchanged: `contains(/^err/)` = `startsWith("err")` (L17),
and `search(/^err/)` has its one hit exactly when `contains(/^err/)` holds. With an explicit `(?m)` in the argument
`^` also matches after a line break inside the span (C35), one hit per such line.

ZERO HITS. `search` NEVER REJECTS (zero iterations always parse; as a set it is every string); `contains` does.
`(m: search(r))` alone narrows nothing (§0.1 L16); a question narrows: on zero hits `some(...)` fails, `count(...)` is
0, `occurs.none(...)` holds, and a plain condition or `all(...)` follows §13 O28 (lean: fails, zero iterations being
"unset"). `!search(r)` is empty, the empty-intersection error (L51).

HAND CHECKS. Each row was derived by hand from the priority parse and then run on the system libpcre2-8 (10.46): the
pattern `(?s)(?:.*?(X)(?C1))*.*` matched against the whole value (anchored at both ends), a callout recording the
span of each hit (script and output: `docs/dev/lanes/predspec8_report.md`, EXAMPLES RE-CHECKED).

| value | argument X | hits (the priority parse) | `count` | `search` accepts | `contains` accepts |
|---|---|---|---|---|---|
| `abx aby abx` | `/ab(?<g>[xy])/` | `abx`@0 g=x, `aby`@4 g=y, `abx`@8 g=x | 3 | yes | yes |
| `aaa` | `/aa/` | `aa`@0 (the parse with a hit at 1 has lower priority) | 1 | yes | yes |
| `baa` | `/a*/` | the empty string @0, then the loop ends | 1 (find-all: 3) | refused (L53, lean) | refused (lean) |
| `err x err` | `/^err/` | `err`@0 (`^` is the span's start) | 1 | yes | yes |
| `x err` | `/^err/` | none | 0 | yes | no |
| `xyz` | `/ab(?<g>[xy])/` | none | 0 | yes | no |
| `err\nerr x\nok` | `/(?m)^err/` | `err`@0, `err`@4 | 2 | yes | yes |

On the first row: a plain `(g: "x")` fails (hit 2), `some((g: "x"))` holds, `occurs.exactly(2, (g: "x"))` holds,
`count((g: "y"))` = 1 (§4.3).

THE OWNER'S EXAMPLE (his semantics, CF:880-887 and the predspec7 brief; his `d := <subject> ~ ...` spelling used the
withdrawn `~`; his example stays the INTENDED BEHAVIOUR). With `r := /ab(?<g>[xy])/` and a pattern P whose label m
holds `abx aby abx`:

    P & (m: search(r) & occurs.exactly(3, (hit: /(?s).*/)))   # his count(d) = 3: a group question, phase 1
    P & (m: search(r) & some((g: "x")))                        # some hit has g = x: phase 1
    P & (m: search(r) & occurs.exactly(2, (g: "x")))           # two hits have g = x: phase 1
    $m.hit[2]                                                  # his d[2] = aby: ONE iteration, captures level
    $m.hit[2].g                                                # his d[2].g = y: captures level
    $m.hit & (g: "x")                                          # his d & (g: x): iterations 1 and 3, positions kept

The first three are GROUP QUESTIONS, which compile to states (phase 1; CF:922-924, accepted at CF:905). The last
three read ONE ITERATION, which needs captures inside a loop: a higher capability level with its cost shown (the
MANAGER'S LEAN, CF:924-926, LEAN; §4.3). `(hit: /(?s).*/)` is "every hit" spelled as a condition; a shorter spelling
is §13 O56. A search result is no longer BOUND: what `d := ...` becomes is §13 O55.

`x & s` with s an rx stays MEMBERSHIP (`x & a`; no `in`): it is not a "some result" spelling (§0.1 L54); over
iterations the one spelling is `some(...)` (CF:913-914).

**REASONING.** The owner's criterion "few types and few operators that always mean the same thing wherever they are
used" (CF:847-848): two operators leave, and the one thing rev 7 had to invent for search, a MATCH-TIME array with
its own rules (rev 7 §3.4, O50), is gone: the hits are the iterations of a repeated label, which the language had
already (§4.3), and the array interface over them is the general one for ANY repeated label (CF:922-923). A search
is a filter like `contains`, so it composes by `&` and `:` like every other filter, and `^`/`$` in its argument follow
the one filtered-span rule (§11). Search results stay values-not-globals in the owner's sense ("Even Perl had the
awkward $1"): a hit is reached through the label of the match it belongs to, never through a global.

**STATUS.** Search as a library transform of the `contains` family, `~` and `!~` withdrawn, the hit a repeated label,
the definition requirements (lazy gaps, the count along PCRE's priority parse, the empty-match advance stated, the
look-alike row): CF:907-921, accepted at CF:905 ("Do it"; the transform idea is his own, CF:903-904). The written
definitions and the hand checks: this document (LEAN). The refusal of a nullable argument: LEAN (§13 O53). `(?s)` in
the library bodies: LEAN (this document). The priority parse vs §4.5: CONFLICT (§13 C36). `^`/`$` of the argument =
the filtered span's ends: RULED (D193 add. 3; CF:761), applied to an argument: LEAN (§13 O49). The group questions
phase 1: CF:922-924, accepted at CF:905; one-iteration access at captures: LEAN (CF:924-926). The owner's example:
his intended behaviour. SUPERSEDES rev 7 §2.6 (`$x ~ rx` as an operator, the search result as a match-time ARRAY
VALUE, `!~` as sugar) and rev 6's "a search returns an rx (the occurrence set)" (CF:873) as a VALUE reading; its
occurrence order (non-overlapping, leftmost, CF:74) is kept as requirement 1. Binding a test: allowed (§13 C6
RESOLVED).

### 2.7 Transforms are FILTER MODIFIERS

**RULE.** A TRANSFORM is a macro FILTER -> FILTER (its parameter is a filter and its result is a filter, the one
input rule of §2.1, CF:860): given a filter S it returns a NEW FILTER that accepts the subjects
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

NAMING RULE: a modifier's name describes the SUBJECTS IT ACCEPTS (an adjective or phrase: `padded`, `unpadded`,
`any_case`, `quoted`, `length`, `month_numbered`), never a verb acting on the subject (`unpad`, `trim`,
`lowercase`). A modifier is applied to a filter by a call and the result is used like any filter: `x &
padded(S)`, `(x: padded(S))` (the operand arrives via `&` or `label:`, never as an argument, §2.3); `&` stays pure intersection (§2.2), so a modified filter may stand
anywhere in a chain. A modifier without its filter argument where a filter is needed is the unapplied-macro error
(§2.3). `!padded(S)` is an ordinary filter (the complement of a filter). A modified filter's argument is a SET
POSITION (§11): `^`/`$` inside it are the ends of the span the modified filter filters, AS THE MODIFIER READS IT (the
argument's "own" start and end in rev 6's words: the argument filters what the reading yields, so its ends are that
span's ends; `padded(/^5/)` = `padded(startsWith("5"))`). This is the one filtered-span rule of §11 applied to an
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
naming rule, §13 O37).

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
vs user labels of those names: §13 O31.

### 3.2 The four tools

**RULE.**
1. `X[...]` = POSITION in the array interface only: integers, integer sets, numeric filters (`X[1]`, `X[<4]`); the
   result is always an rx read through the array interface, keeping the ORIGINAL positions; a string or non-numeric
   filter inside is a compile error suggesting the right tool. Indexing descends (`d[1][1]`). Integer sets and
   numeric filters select among positions 1..n only (`X[<4]` = `X[1|2|3]`); there is no `X[0]` (the whole rx is X
   itself; review r8 P6-2, CENSUS-13: a group-0 index read the map interface's numbering through the array
   interface's bracket). Out of range = entry absent: tests on it are false. 1-based. Indexing reads a SPELLED array
   at compile time (§3.4); on a repeated label's iterations (`$m.hit[2]`) it reads ONE iteration, the captures level
   (§4.3, LEAN).
2. `X & f` = filter by LANGUAGE; `&` distributes over entries and empty products drop:
   `alts & !startsWith("#")` keeps passing literals; `rows & (w: >100)` keeps matching rows.
3. `where(p, X)` = SELECT entries by a compile-time STRUCTURAL property (the selecting twin of `each`; not the filter
   role, §0.3); `where_group(p, X)` for the map interface; both return an rx (§2.1).
4. `X.name` = a FIELD of the MAP INTERFACE of the thing on the left; `.name` is never digits. ONE meaning (the
   manager's lean the owner agreed to, CF:892, CF:898-899): a LABEL (`A.Saturday`, `alt.repeated[1]`, `d.year`), a
   module MEMBER (`json.row`, the module's map interface, §7), METADATA (`.index`, `.label`, reserved fields) and,
   under `$`, a label PATH (`$rest.year`, §5.4) are instances of it. What remains open is only the collision of a
   metadata name with a user label of that name (§13 O31).

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

**RULE.** EXTENSIONAL (`& | !`, comparisons, filter modifiers) depend only on the language. STRUCTURAL (indexing,
`each`, `join`, `where`, `.label`, `enumerate`, entry counts) read the SPELLING: `/a|b/` and `/b|a/` are equal
under `&` but differ under `[1]` (and in PCRE priority). Internal rewrites (altcls, alt_normal_form) never change
user-visible structure. Field-wise narrowing that keeps other entries is structural (`each_group((& (x: d2)), rx)`,
the condition passed as a section, §5.2; rev 6 passed a bare `&`, an operator as an argument, review r8 P6-8 (d)),
never `&`.

SPELLED ARRAYS vs A REPEATED LABEL'S ITERATIONS (stated once; review r8 P6-7, restated by the transform ruling,
CF:922-923). The array interface applies to two kinds of thing. (1) An rx whose entries are known from the program
text (a literal `[ ]`, a binding of an rx, a `join` input, an `enumerate` or `records` result) is a SPELLED array: the
structural tools above read it at compile time, and G4 covers it. (2) The ITERATIONS of a repeated label in one match
(a group inside a loop, the `hit` label of a `search`, §2.6) exist only per match: the array interface over them is
§4.3's, where the GROUP QUESTIONS (a plain condition, `some`, `all`, `count`, `occurs.*`) compile to states (phase 1)
and access to ONE iteration (`$m.hit[2]`) needs captures (LEAN). No structural tool of this section (`each`, `join`,
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
context-free, §11). `x:` is ALWAYS the
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

**STATUS.** LEAN (CF:173); cited as "ruled" by a later note (§13 O3). That warnings have names: RULED (CF:666); the name
`label.unset`: LEAN (manager's list, review RUL-14.1). The two sentences disagree on `(x: !<5)` for an unset x, and
on zero-iteration repeated labels: §13 O28.

### 4.3 Repeated and duplicate labels: the general home of the group questions

**CONFLICT MARKED (§13 C36).** The transform ruling requires a repeated label's iterations to be those of PCRE's
PRIORITY parse (CF:919-920); §4.5 (RULED, CF:583) lets a condition on an ambiguous label pass on SOME parse. For an
unambiguous loop the two agree; for a search's hits (always ambiguous as a set) they do not. This section is written
under the priority parse because the search definition (§2.6) needs it; it does not decide C36.

**RULE.** At the default level a repeated label follows the SEQUENCE RULE: `x: S` constrains ALL iterations; a bare
`$x` on a repeated label is an ERROR naming the group questions below. At `vm`, `$x` is PCRE's last iteration (what
`\k<x>` sees). Duplicate names (`(?J)`, `(?|`): plain `$x` gives the lowest-numbered set group; the static
CONSTRAINT SET of a duplicate label (the strings it can hold) is the UNION of the definitions that can set it.
Structurally, `alt.x` returns EVERY entry labelled x as an rx read through the array interface in group order;
`alt.x[1]` (first in the PATTERN, compile time) differs from `$x` (the MATCH's captured string). A repeated label is
ANY label inside a loop: a group under `*`/`+`/`{n,m}`, a `list_of` part (E-HTTP's `name`), and the `hit` label of a
`search` with every label of its argument (§2.6). There is no second population: rev 7's "entries of a match-time
array" are these iterations.

THE GROUP QUESTIONS, stated once (CF:910-915, accepted at CF:905). Each is a macro with its operand open, standing in
the filter role like a condition (`P & some((g: "x"))`, `(m: search(r) & some((g: "x")))`); the labels it names are
looked up in its operand as for any condition (§4.1).

| form | means, over the iterations of the labels it names | example on the hits `abx`, `aby`, `abx` of `/ab(?<g>[xy])/` |
|---|---|---|
| plain `(g: S)` | EVERY iteration's g is in S (the sequence rule); on zero iterations: §13 O28 | `(g: "x")` fails |
| `all((g: S))` | the same as the plain condition: the default, "rarely written" (§0.1 L36) | `all((g: "x"))` fails |
| `some((g: S))` | AT LEAST ONE iteration's g is in S; false on zero iterations | `some((g: "x"))` holds |
| `count(c)` | the NUMBER of iterations meeting the condition c: a number (an rx of canonical numerals, §2.1, §13 O40), tested through a computed label (`n := count(c)`, `P & (n: ==2)`) | `count((g: "x"))` = 2 |
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
Which iteration a record means when its labels sit at different depths (g inside the loop, k outside it): §13 O57.

THE ARRAY INTERFACE OVER ITERATIONS (CF:922-926). The iterations of any repeated label, in match order, are read
through the array interface (§3.1, §3.4); nothing is created. Two levels:
- GROUP QUESTIONS (the table above) compile to states (a capped counter per question, n+2 states, CF:62's cost rule):
  the DEFAULT level, phase 1 (CF:922-924, accepted at CF:905). The iterations are those of PCRE's priority parse
  (CF:919-920; C36 above).
- ONE ITERATION read out: `$x[2]` (the captured string of iteration 2), `$m.hit[2].g` (a label inside it; `$` covers
  the whole path, §5.4), and selecting iterations by a condition (`$m.hit & (g: "x")` keeps iterations 1 and 3 with
  their positions, the owner's array example, §2.6) need captures inside a loop: the `captures` level, its cost shown
  (the MANAGER'S LEAN, CF:924-926: LEAN). Out of range = the iteration is absent and a test on it is false (CF:62). A
  TEST on one iteration by a literal index (`(x[2]: S)`) does not read text out; CF:62's countdown makes it regular
  (~k states for i <= k), so this document reads it as a group question at the default level (LEAN, reconciling
  CF:62 with CF:924-926; §13 O57).
- No structural tool (`each`, `join`, `where`, `enumerate`, `.label`) reads iterations (§3.4).

**REASONING.** "All iterations" is substitution into the loop body, the only pure lowering (predx §2.1, O4); the
last-iteration rule would need captures inside a loop. One home for every repeated label means search adds no rule
(§2.6), and "some" has one spelling (`some(...)`), "all" the plain condition, "how many" `count` and the `occurs`
counts. The record-as-same-iteration rule is the record's own meaning (all entries together, §5.4) applied to one
iteration, so it needs no extra rule either.

**STATUS.** Sequence rule: RULED (CF:583, predx Q4), SUPERSEDES "plain `$x` = last iteration" at the default level.
Plain condition = all, `some`/`all` the one spelling, `occurs` counts only, same iteration by record, the hit a
repeated label, group questions at the default level and phase 1: CF:910-917, CF:922-924 (accepted at CF:905;
"could you use some() to get some hits?" is his own question, CF:904-905). `occurs.some`/`occurs.all` removed rather
than aliased: LEAN. One-iteration access at `captures`: LEAN (CF:924-926, the manager's, not separately ruled); a
literal-index TEST at the default level: LEAN (CF:62). The priority parse: C36 (CONFLICT). `occurs` as a library:
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

A mapping must be a FUNCTION (one value per text: the per-label ambiguity check), many-to-one allowed, total on its
pattern. Tabulated mappings report a constant from the accept state (§6.2); numerals by digit conversion. A computed
label's value is context-free (§11). Read it with `$` like any label (`$d`, `$wd`); the bare spellings in E-CAL and
E-RFC (`<=dim`, `==wd`) are §13 C13. Through a filter modifier a value condition becomes a pattern: `month_numbered(<3)` =
`/Jan(uary)?|Feb(ruary)?/` (§2.7).

**REASONING.** Lets non-numeric layouts (month names) comply with numeric fields; a weekday or a Luhn check is a
property without a capture group. A binding instead of a keyword keeps the grammar keyword-free (§5.1).

**STATUS.** Computed labels: LEAN (foundation per the LAYERING note, CF:522). Match-dependent binding as THE spelling:
LEAN (manager, CF:595; the concept RULED there), SUPERSEDES the `with` placeholder and predx's `with`. Which pattern a
binding attaches to when its labels occur in several: §13 O19.

### 4.5 Ambiguity

**RULE.** A label is AMBIGUOUS when two accepting parses give it different spans (decidable). At the default level
a condition on an ambiguous label passes if SOME parse passes (one automaton); a `label.ambiguous` WARNING shows a
witness, the two parses, which one PCRE chooses, the consequence and a fix where one exists. At `vm` the condition
uses PCRE's chosen parse. Library patterns are checked unambiguous at their labels. Every occurrence of the same
application denotes ONE parse (merged narrowing).

**CONFLICT MARKED (§13 C36, rev 8).** The library transform `search` (§2.6) is AMBIGUOUS at its `hit` label by
construction (a lazy gap, as a set, can swallow a hit), so it fails "library patterns are checked unambiguous at their
labels", and its group questions are defined on PCRE's PRIORITY parse (CF:919-920), not on some parse. Both readings
are in C36; this section's rule is unchanged until the owner decides.

**REASONING.** The default level is a promise; only some-parse keeps it; for unambiguous labels the readings
coincide, so the difference is confined to exactly the patterns the warning flags (predx C11).

**STATUS.** RULED (CF:583, predx Q2). Resolves C11. Some-parse per condition vs merged narrowing for two conditions on
one pattern (`(a: <5) & (b: <5)` on `123`): §13 O33.

### 4.6 Value-vs-value relations, priced by class count

**RULE.** A comparison between two match values (`(b: >$a)`, `(day: padded(<=days_in($year, $month)))`,
`(wname.index: ==wd)`) is a RELATION, run the cheapest correct way. The values are passed to value macros as
parameters (`days_in($year, $month)`); an rx is never called with them (`leap` is an rx, which has no parameters:
`leap($year)` is the operand-as-argument error, §2.3; the leap test is `$year & leap`, inside the library's `days_in`). Its cost is the CLASS COUNT of the
earlier label(s): the number of classes the earlier labels enter the relation with (raw = |dom|; through a regular
twin = its class count). The manager's answer to "how practical" (CF:659-663; the owner has not replied, so the
tiers and numbers are LEAN and the thresholds §13 O39): SMALL (calendar 24, state/ZIP ~50, weekday-vs-date 7, check
digits 10/11) = one automaton at the default level; LARGE (times of day 1,440: borderline; dates within 15 days:
~3.65M) = a default-level ERROR printing the count and the fixes, or a linear arithmetic check under `functions`;
UNBOUNDED (`b: >$a` over arbitrary `\d+`) = not regular, `functions` only. The compiler computes the count BEFORE
building; [COST-EXPLAIN] shows it.

**REASONING.** Turns "too large" into an explainable number; predicts E-CAL (24) vs E-NEAR (3.65M). Present it as
"a relation, run the cheapest correct way", never as "always one automaton".

**STATUS.** Value-vs-value comparisons, typed and class-count priced: RULED as a concept (CF:657-659: "VALUE-VS-VALUE
comparisons: AGREED, Frank asked how practical"). The SMALL / LARGE / UNBOUNDED tiers and their numbers are the
manager's ANSWER to that question (CF:659-663), which the owner never replied to: LEAN; the thresholds are §13 O39. A
count against another label's value is such a relation: LEAN (CF:682).

## 5. Macros, bindings, statements

### 5.1 Program shape, bindings, no keywords

**RULE.** A program = bindings, expressions, calls and `@` STATEMENTS, with ONE final expression (the program's
pattern); newlines are layout (whitespace and newlines are free between expression tokens: long logic goes in `:=`
definitions, literals stay short). A `(` or `[` after an expression is always a call or an index, so a statement
that STARTS with `(` or `[` (a record on the left, a final array) continues the line before it: §13 O51 (review r8
P6-13). A binding starts `name :=`. There is ONE kind of binding: `name := expression`,
and the name names whatever its expression is, an rx or a macro (CF:858); a definition head `m(p1, p2) :=` makes a
macro (§5.2); a record on the left (`(x, y) := ...`, §2.6) is design only, out of phase 1 (§0.2). The bound kind
decides use in a hole: an rx inserts its set (a one-string set, a captured string or a quoted literal, as its literal
text; any other rx as a sub-pattern); a macro in a hole is the unapplied-macro error (§2.3; CF:362, "not usable as
`${x: digit}`"); a guard is written with `&` before an rx hole (§11, C4). A binding
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
`file_text`, `records`, `eval`. Every other name in the examples (`between`, `startsWith`, `contains`, `padded`,
`days`, `weekday_of`, `within`, `list_of`, `join`, `each`, ...) is a library name; whether `some`/`all` are
built-ins or library names: §13 C21/C28 (review RUL-13). `$&` and `$_` are reserved scope-supplied labels; an
undeclared name that is not a label is an error with a suggestion; a binding hiding a label WARNS (`$x` still
reaches the label).

**REASONING.** Frank: "no alpha operators ... with, check, in ... don't want to go into new grammar lightly". The
grammar shrinks to bindings, expressions, calls and `@` statements; the `@` mark makes compile-time effects visible.
A bare enum word (`allow`, `desc`) would be a keyword in argument position (review OWN-7).

**STATUS.** Block shape: RULED (CF:68). One kind of binding, naming whatever its expression is: RULED (CF:858,
accepted at CF:851; rev 6 still said LEAN (CF:115), review r8 RUL-13). The macro-in-a-hole error: RULED (CF:362). No alphabetic keywords: RULED (CF:595). `@` statements,
the unused-pattern and bare-statement errors: LEAN (manager, CF:619, on Frank's prefix suggestion). String enum values
and the closed built-in list: LEAN (review OWN-7). Define-before-use: §13 C12. Bare label names as values: §13 C13.
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

Typed parameters: `m(x: T)` narrows x by the constraint set T (in a definition head, `:` constrains the parameter
the head declares, §5.4), and the POSITIONAL argument must lie WITHIN T; a broader or partly overlapping argument is
an error showing a dropped witness and the explicit conversion. A condition literal applied by `&` never gets that
check: it always NARROWS the operand (`isodate & (year: <2000)` silently drops `5`, which `/\d{4}/`
cannot hold). At NARROWING SITES (typed parameters, condition literals, an `&` whose operands come from definitions) an
empty intersection from pure parts is an ERROR; a dead branch WARNS (`dead.branch`); nothing when emptiness is match-
or parameter-dependent; NEVER inside an `@assert.*` argument, whose emptiness is the assertion's own question (§5.6).
So `:` CHECKS in a head and NARROWS in a condition (§0.1 L49): whether it should do one thing in both, or the check
get its own spelling, or typed parameters leave phase 1, is OPEN (§13 O48; review r8 P6-4). `m(p: pure)` (a
match-dependent argument is an error, "pass `pattern($x)`") puts a PROPERTY, not a constraint set, after `:`, a
second use of the mark: its spelling is OPEN (§13 O48). Built-in `pattern($x)` = the label's static pattern.

**STATUS.** Macro bindings: RULED (CF:124). `=` sets a parameter vs `:` filters, a condition literal narrows: RULED
(CF:706). Patterns take no arguments, a parameterised pattern is a macro: RULED (CF:744). The operand (CF:749's
"subject") is never an argument, positional = required parameters, keywords = optional settings, any parameter by name, operator sections,
no lambda: RULED (CF:749; C20/C30 RESOLVED). Sections start with `&` only: RULED (CF:753, C33). No partial application
in phase 1: RULED (CF:753, C34); the design keeps currying for later: RULED (CF:804, which says C34 does not supersede
CF:308). A call = the macro applied to one record: RULED (CF:866 (a)); the nested-record error and a condition
argument passing the macro: LEAN (this document; §13 O45). Typed-parameter containment: LEAN (CF:149). The empty-intersection error scoped to narrowing sites: LEAN
(review RUL-6). `pattern()`: LEAN; `pure`'s spelling: OPEN (O48). A section is a macro, `(& M)` = M: LEAN (review r8
P6-8). Overloading: LEAN, NOT phase one (CF:163). `(x & isodate).year`: §13 C29.

### 5.3 Structural macros: `each`, `each_group`, `where`, `join`

**RULE.** Macros are passable values, FENCED: compile-time only, over finite SPELLED arrays (§3.4; on a search
result, a match-time array: §13 O50), structural operators only. `each(f, A)` applies f per entry, keeps labels and order, returns an array (the structural per-entry map, not
an application spelling, §2.3). f is a MACRO whose parameters the entry fills (`each(triple, ...)`, `each(capture, a)`),
or a FILTER passed as an operator SECTION: `each((& isodate), dates)` maps the filter over the entries, and sections
compose (`(& isodate & (year: 2024))`, ruled 2026-11-15, §5.2); a condition, already a macro with only its operand
open, may be passed as it is (`each((a: d), x)` = `each((& (a: d)), x)`, §2.1); over several arrays it ZIPS by position (unequal lengths = error naming both counts).
`each_group` zips BY LABEL; `where_group` and `each_group` return an rx (an array in group order, §2.1). `join(a, sep
= s)` concatenates the entries of a SPELLED array in their written order (a structural tool, §3.4); `sep` is a set;
joined PARTS stay navigable by their labels in the map view (`(c.A: <200)`, `c.A`), free when unread. A join is ONE
alternative, so its array view has one entry and `c[1]` is c itself (rev 6's `c[1]` "first part" read the array
bracket as a part index; review r8 CENSUS-13); an unlabelled part is reached through the binding it came from. Family: in-order fixed = `join`; in-order repeated =
`list_of(X, sep = ...)`; any-order fixed = `&` of labelled parts (JSONL); candidate sugar `any_order(a, sep = ...)`.
Caller-visible captures are a library macro: `capture(x) := /(?<${x.label}>${x})/`, `join(each(capture, a), sep =
".")`, exported like any binding (§7).

**Ordinal parameter.** The iteration ORDINAL (dense, starts at `index =`, default 1), `x.index` (original position)
and `x.label` (original name) differ once an array is sliced; the ordinal is a PARAMETER the macro declares
(`capture(x, i) := /(?<f_${i}>${x})/`); `each` passes it as the second argument when the macro takes one.

**STATUS.** LEAN (CF:278 join, CF:289 compose instead of an option, CF:300 each's bindings). Mapping a filter by a
section: RULED (CF:749). Ordinal default 1: per the 1-based ruling. Per-field constraints carrying into joined labels:
§13 O5. The rev 0 `export capture(x) := ...` keyword form is superseded by `@export` (§7).

### 5.4 The marks: THE grammar summary and THE MARK TABLE

This is the ONE place the marks are defined; every other section points here. It is G0b's MARK TABLE: each mark,
its ONE meaning, every position it may take, and the §12 case that needs it ("no case" marks a mark carried without
one; the TWO-WAY CENSUS in §12 gives the reason). Inside `/.../` none of this applies: rx text has PCRE's meaning
(`\d{1,3}`, `(?<y>...)`, `[^,]`, `/${p},${p}/`).

THE BRACKETS AND THEIR MARKS (`,` `( )` `[ ]` `=` `:`):

| mark | where it may appear | what it means | §12 case |
|---|---|---|---|
| `,` | only between ENTRIES inside `[ ]` or `( )` (a call's parentheses are a `( )`) | "next entry"; it never carries logic (no AND, no OR, no dimension) | every case |
| `[ e1, e2, ... ]` | value position; and as the index bracket `X[...]` | ARRAY: ORDERED ENTRIES, each entry ONE entry (like a group or a hole, §3.3: `[x, /d/]` has 2 entries whatever x holds, §0.1 L48). Under `& \| !` and in the filter role (extensional, §3.4): ANY ONE entry (of rx: an alternation; of macros: a macro, a list of filters, §3.5; mixed: error). Under structural tools (indexing, `each`, `join`, `count` of entries, §3.4): the entries in their written order. One meaning, two readings of it, as for every rx (§3.4). `X[...]` selects positions, any one of those listed (`X[1, 3, 5]` = `X[1\|3\|5]`, if the multi-index is adopted, C5) | E-WEEKDAY, E-IPV4, E-RFC, E-NEAR, E-SEP (`join` inputs); E-RFC (alternations of names) |
| `( e1, e2, ... )` | ONLY laid against something with fields: (a) a CALL's argument list, against the macro's parameters (also a definition head `m(p1, p2) :=`, which declares them); (b) a CONDITION, against a pattern's labels; (c) the LEFT of `:=`, against a result's groups (design only; out of phase 1, §0.2) | RECORD: ALL entries together, positional or labelled. NEVER A VALUE: it cannot be bound, stored or returned. The written form of the MAP view (§3.1); one-way | every call; every condition |
| `( label: S, ... )` in VALUE position (an argument, an array entry, the right of `:=`) | where a value may stand | a CONDITION, i.e. a MACRO (CF:858), NOT a record: the record is its written body, laid against the operand's labels when `&` fills it (position (b)); no record is bound or passed (§4.1; §13 O45). Any other record in value position is an error (`(x = /a/, y = /b/)`: "a record is not a value; for any one of the entries write `[ ... ]`", §0.1 L43) | E-HTTP (`occurs.exactly(1, (name: ...))`, `count((name: ...))`) |
| `(& f)` | value position | a SECTION: the macro with only its operand open (§5.2); `(& M)` = M for M with only its operand open (§2.1) | no case (prose only, §5.2, §5.3) |
| `( e )` | value position, no comma, no label mark | GROUPING (precedence only); a one-entry record exists only in positions (a)-(c) (§13 O41) | no case (§12's parentheses are calls and conditions) |
| `=` | `name = e` as an entry of `[ ]` or of a call record | gives the entry its NAME: a LABEL (group name) in an array (`[year = /\d{4}/, ...]`), a PARAMETER in a call (`sep = "."`) | E-WEEKDAY, E-RFC, E-NEAR, E-SEP, E-HTTP; `sep =`, `of =`, `sha256 =` |
| `:` | `label: S` as an entry of a condition record (the label may be a path, `d.year: S`); `p: T` in a definition head | CONSTRAINS a label (or, in a head, the parameter the head declares) that EXISTS, by a constraint set. Elsewhere an error (`P & x: S`, `[x: S]`, `f(x: S)` in a call). In a head it CHECKS, in a condition it NARROWS (§5.2, §0.1 L49, §13 O48) | E-WEEKDAY, E-CAL, E-RFC, E-NEAR, E-HTTP, E-CTX (conditions); no case uses a typed head |

ENTRY EXTENT: an entry runs to the next `,` or the closing bracket; inside it `&` and `|` bind tighter than `:` and
`=`, so `(x: <200 | >900)` and `[month = /\d\d/ & padded(between(1, 12)), ...]` each hold ONE entry (§4.1, C22).

THE OTHER MARKS:

| mark | where it may appear | its one meaning | §12 case |
|---|---|---|---|
| `&` | between two expressions; in rx text only as `&${` before a hole (C23) | fills the operand slot: rx & rx = intersection, rx & macro = the macro applied to the rx, macro & macro = pointwise (§2.1, §2.2) | every case but E-SEP, E-DEPTH |
| `\|` | between two expressions | ANY ONE: union of rx, concatenation of arrays (§3.3), pointwise on macros; rx \| macro is an error (§2.1) | E-FILE, E-DEPTH |
| prefix `!` | before an expression (expression language only, §2.2) | the complement in the filter role: a macro with its operand open | E-FILE |
| `<` `<=` `>` `>=` `==` | prefix, before ONE atom | a COMPARISON SET (a full rx, §2.4) | E-CAL (`<=`), E-RFC (`==`), E-FILE (`<=`, `>`) |
| `+` `-` `*` `%` | between numbers | arithmetic on numerals (§2.5) | E-NEAR, E-DEPTH (`-`); `*`, `%`: no case |
| `~` | `$x ~ rx` | search inside a value: the ARRAY of all results (§2.6) | no case |
| `!~` | `$x !~ rx` | the condition `(x: !contains(rx))` (§2.6; O12, O50 (c)) | no case |
| `:=` | statement start (a name, a definition head, or a record on the left, design only) | binds a name to an rx or a macro (§5.1) | every case |
| `.` | after an expression or a label path | FIELD of the MAP VIEW of the thing on the left: a label (`d.year`, `rest.year`) (§3.2 tool 4). Rev 7 lean (P6-12): this is its one meaning; module members (`json.row`) and metadata (`.index`, `.label`) are instances only if a module is read as a map and metadata as fields, which §13 O31 decides | E-RFC (`.index`, `$rest.year`), E-JSONL and others (`json.row`), E-FILE (`r.word`) |
| `$` | before a label PATH | the CAPTURED STRING of the whole path: `$a.b.c` = `$(a.b.c)`, so `$mname.index` is the index of mname's matched entry (11 for `Nov`), never `($mname).index` (review r8 P6-6) | E-WEEKDAY, E-CAL, E-RFC, E-NEAR |
| `${ }` | inside rx text | a HOLE: inserts an rx's set as one entry (§3.3, §11); a macro in it is the unapplied-macro error (§2.3) | E-JSONL, E-DEPTH, E-IPV4 (prose) |
| `/.../` | value position | an rx literal with PCRE's meaning (§11) | every case |
| `@` | statement start | marks an EFFECT (§5.1) | E-IPV4, E-CAL |
| `"..."` and numerals | value position | a one-string rx (§2.1) | every case |

**STATUS.** The comma as "next entry", `[ ]` any one, `( )` all together, `=` labels, `:` constrains an existing label:
RULED (CF:863, on the acceptance alone except the comma, CF:850). The record never a value: RULED (CF:851-852, his
words); its three positions: RULED (CF:866, on the acceptance; the left of `:=` also CF:852). Spellings:
placeholders (D193 add. 4). The table's placement of definition heads under (a), the `( e )` grouping rule, the entry
extent restated for `=`, and the condition row: LEAN (this document; §13 O41, O43, O44, O45). `[ ]`'s one meaning
stated with its two readings, and each entry ONE entry: LEAN (review r8 P6-2, P6-14; §3.4 RULED, CF:328, CF:385).
`$` over a whole path: LEAN (review r8 P6-6). The `.` row's one meaning: LEAN, the dot family OPEN (§13 O31). The
other marks restate the sections cited; `@`: LEAN (manager, CF:619). SUPERSEDES rev 5's "`,` separates conditions in a
condition literal and arguments in a call" and "`=` BINDS a label inside a map/list literal" (the map literal is
withdrawn, §3.1).

### 5.5 `enumerate`

**RULE.** `enumerate(rx)` = the ARRAY of a FINITE rx's strings, in PCRE PRIORITY ORDER (leftmost alternative,
greedy before lazy); the members of a CLASS, which has no priority among them, come in CODEPOINT ORDER (so
`enumerate(/[-\/.]/)` = `enumerate(/[.\/-]/)` = `["-", ".", "/"]`); so re-joining preserves which match is reported
(hence a built-in, not a library). Its argument is a compile-time SET POSITION: an edge assertion in it is the
edge-assertion error (§11; `enumerate(/(?<=a)[bc]/)`). A BUDGET bounds it: an infinite or over-budget rx is a
compile error giving the count. Uses: finite backreferences made regular (`each(date_sep, enumerate(/[-\/.]/))`,
`!contains(each(triple, enumerate(/[\x21-\x7E]/)))`), matched delimiters (`each(q, enumerate(/["']/))`), which option
matched via `.index` at the default level, per-entry library assertions (spelling of `@each(...)` OPEN).

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

An assertion's argument is a compile-time SET POSITION: it is decided on strings, and an edge assertion in it is
the edge-assertion error (§11; `@assert.none("5" & /(?<=\$)\d+/)` is refused, not existential over contexts). No
assertion states SEARCH behaviour (that `256.1.1.1` is searched as `56.1.1.1`, §12.3). The implicit
empty-intersection error never applies inside an assertion's argument (§5.2). Anonymous assertions report line +
text; NAMED assertions give named failures (§13 C18 for their spelling). An assertion the compiler cannot decide
reports "can't prove: not regular" beyond the default level. Libraries carry their standard's test vectors as
assertions run at import.

**REASONING.** Language equality and inclusion are decidable (D196 add. 2's never-match/XOR fact), so the library
test rule ("tested against the standard's own vectors") becomes executable (predx S8, §8.3 item 3).

**STATUS.** Concept (compile-time assertions): RULED (CF:595, Q9). Library form `assert.some` etc.: RULED (CF:608,
Frank's own `assert := import("assert")`, `assert.some("2024" & leap)`); `@` prefix: LEAN (manager, CF:619),
SUPERSEDES `check A == B` and the `assert_some(...)` built-ins. Set position: RULED (CF:713). The empty-intersection
exemption: LEAN (review RUL-6). A library SEARCH assertion (review Q1X-5): not adopted, §13 O36.

## 6. Capability levels and the reporting axis

### 6.1 Levels

**RULE.** Inside the predicate opt-in, the DEFAULT level promises "LINEAR, AUTOMATON CODE ONLY": linear time, no
backtracking, hostile-input safe, self-contained output. It does NOT promise one DFA pass: a relax-then-verify split
whose verify is itself an automaton over the candidate span ([PRED-SPLIT]) is inside it, and so are computations on
run-time PARAMETERS only (once per match, over a fixed-size value; comparisons against parameters compile to
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

**`&` AT `vm` WITH A NON-REGULAR OPERAND.** The regular operands build the CANDIDATE automaton; the VM verifies the
non-regular operand on each candidate span; the reported span follows D196 ([PRED-SPLIT]). CAVEAT (CF:63): D196's
left operand chooses the reported end, so when the verify rejects the preferred end the next end must be tried; for
that match the verify falls back to the VM.

**REASONING.** An RE2-class promise with far more expressive power (G2). Independence: a user may want
linear-time callouts without backtracking, or spans without callouts. Under the ruled string-set model (§11) no
set-position use carries context state, so G2 needs no regular-lookaround lowering for conditions (review Q1X-8).

**STATUS.** Levels: LEAN (CF:472, "Lean ADOPT"). The promise "linear, automaton code only" (automaton split and
parameter-only computations at default; `functions` = functions over captured text): RULED (CF:583, predx Q5;
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
  every recursive call, with a literal base case (`value_depth(0) := json.scalar`, §12.11); any other cycle is
  refused at load (the error names the cycle). A parameterless pattern binding may recurse as in PCRE through its
  OWN NAME inside its OWN literal (`balanced := /\((?:[^()]|(?&balanced))*\)/`, matched at run time, needs `vm`):
  the one crossing from rx text to the expression language other than `${}` (§11; CF:113's lean "a pattern binding
  may call itself via `(?&name)` inside its own literal"; review r8 SIM-9: rev 6 used it without stating it). Labels
  inside recursion refused at first.
- `file_text(path, sha256 = ...)` = the whole file as one compile-time string; `records(text, rx)` = an ARRAY (a
  spelled one, §3.4) with one ITEM per compile-time match of the ITEM RX over a compile-time string (the names
  `records`/"record rx" are placeholders colliding with RECORD, §0.3, §13 O44). The item rx is SEARCHED in the text
  (in context, like a final pattern: its `^`/`$` read the file text); each ITEM is the item rx narrowed to that one
  match, a one-string rx (context-free, §11) whose labels stay reachable by the map view (`r.word`, E-FILE; rev 6
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
  returns a MODULE of the file's exported bindings; member access is navigation by name (`json.row`). WHAT A MODULE
  IS under the two value kinds is OPEN (§13 O46; the kind table, §2.1): rev 5 called it a MAP (the aligned map case), usable whole as a
  pattern when every entry is an rx; but a module holds macros, so it is not an rx, and a record (the written map
  view) is never a value (CF:866), yet `json := import("json")` binds it. Lean: a module is a compile-time NAMESPACE
  that `:=` names, not a value (never passed, stored, returned or used whole as a pattern). A library file exports with `@export(names)`: every module label whose NAME is in the rx
  `names` (`@export("leap")`, `@export(["leap", /[^_].*/])`, `@export(/[^_].*/)`); the filter must be a set of
  strings, not a target-less filter in an alternation. A name set is a compile-time set: an edge assertion in it is
  the edge-assertion error (§11). A library file with no export is an error ("library exports nothing"). Imports and
  file reads are COMPILE TIME ONLY (artifact self-contained), PINNED by `sha256`; the name -> file map and its pin
  live in configuration (the .rxt `include`/`lib` machinery, `docs/spec/rxt_format.md` §1.1.1, and [LIB]).
- THE EMPTY-MATCH HAZARD. When the program's FINAL pattern is NULLABLE and used in SEARCH mode: an ERROR in a
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
namespace, not a value); import and
export as functions over name-sets add no keyword, and one name-selection rule serves import, export and warnings.
The empty-ENTRY error rejected legitimate optional parts and missed `/\d*/`; the real hazard is a final pattern that
reports an empty find, which is a fact about the pattern in context (review Q1R-9).

**STATUS.** Bounded recursion: RULED (CF:583, predx Q12, low priority, one example), REFINES CF:58. file_text +
records: LEAN (CF:419). Tiling: RULED (CF:583, predx Q13). Import/export as functions, `@export` filter,
no-export error: LEAN (manager, CF:608, CF:619, on Frank's proposals); module = map: LEAN, put in question by
CF:858/CF:866 (§13 O46); import resolves to exactly one file, argument a set of names: RULED (CF:630). Empty-match rule: RULED (CF:666), SUPERSEDES the empty-ENTRY error and `skip_empty`;
nullability in context: RULED (CF:713); only the MODE exempts: LEAN (review Q1R-9). String option values: LEAN (review
OWN-7). Prerequisite list: LEAN (review Q1X-8). The untiled-range wording: LEAN (review Q1R-10). Cost surfacing: LEAN
(CF:41). The `trim` / `\r` trap of rev 0 is subsumed by tiling (§13 O18 RESOLVED).

### 7.1 Named warnings

**RULE.** Every warning has a STABLE NAME in dotted families (a contract, stated in the spec): `empty.search`,
`dead.branch`, `label.unset`, `compare.width`, `label.ambiguous`, `warn.unused`; proposed by review 2026-11-14-r1
and not adopted: `precedence.section`, `array.hole`, `flag.hole`. Control is by `@` effects, rest of file:
`@warn.off("compare.width")`, `@warn.off(startsWith("dead."))` (a label-free library rx is a full rx; the look-alike
`@warn.off(/^dead\./)` is the same set, `^` being the name's start, §0.1 L15), `@warn.off(/.*/)`; the reverse `@warn.error(/.*/)` (a
strict build); a per-binding form (spelling OPEN); and a compiler option for a whole build (like `-Wno-`). SELECTORS
ARE A SET OF NAMES AS AN RX, the same name-selection rule as import and export: no `*` wildcard (`"*"` is the
literal name `*`, matches nothing). Errors cannot be disabled (the edge-assertion error included). An `@warn.off`
that suppresses nothing raises `warn.unused` (itself suppressible).

**STATUS.** That warnings have names and can be disabled: RULED (CF:666: "warnings need names and the user must be able
to disable them"); selectors as an rx: RULED (CF:677: "use an rx instead of wild card purely for consistency"). The
list of names: LEAN (manager's list, review RUL-14.1). rev 2's `transform.noop` is gone: a modifier without its
filter is the unapplied-macro error (§2.3).

## 8. Libraries

**RULE.** Standard library = prelude text (macros with typed parameters) on the foundation; it grows without
compiler changes. Standard library sets (each call is a full rx, used in the filter role): `between` (inclusive),
`startsWith(s) := /${s}.*/`, `endsWith`, `contains(s) := /.*${s}.*/` (`^`/`$` in an argument are the ends of the span
the call's filter role filters, §11, so `contains(/^err/)` = `startsWith("err")`; the body's hole does not open a span
of its own),
`when(c, p)` (`x & when(c, p)` = `(x & c & p) | (x & !c)`). Standard FILTER MODIFIERS (§2.7; each transforms the
filter, never the subject): `padded(S)` (leading zeros ignored), `unpadded(n, S)` (read as if zero-padded to width
n), `any_case(S)` (letter case ignored), `quoted(S)` (only the text inside the quotes read), `length(S)` (the
subject's length read), `month_numbered(S)` (a month name read as its number), string positions `left/right/mid`
with literal positions (units = characters per the encoding mode; out-of-range: §13 O14); `json.quoted(S)` (a JSON
string literal read as its decoded text) lives in the `json` module.
- `occurs` (`occurs := import("occurs")`): filters over a repeated label's occurrences: `all`, `some`, `none`,
  `exactly(n, c)`, `at_least(n, c)`, `at_most(n, c)`; `c` is the usual condition, passed as a parenthesised literal
  (`occurs.exactly(1, (name: set))`; C31 RESOLVED); constant (or caller-parameter) n at default; cost = a capped
  counter (n+2 states) multiplied in, shown by [COST-EXPLAIN]; a count against another label's value is a priced
  relation (§4.6). The module NAME tells the user these are counts of matches. The owner applies `occurs` and `count`
  to a SEARCH RESULT too (CF:882-883: "You could use count to check the number of results ... You could use the
  occurs module"): there they count ENTRIES of a match-time array, a second population beside a repeated label's
  iterations; whether the two are one rule (a search result as a repeated label) is §13 O50 (a).
- `count(...)` FIRST, `occurs` AS THE FALLBACK: `count(c)` yields the number of occurrences meeting `c`, a number used
  with the ordinary comparisons and arithmetic like a subject number (`n := count((name: any_case("Host")))`, `headers
  & (n: ==1)`; §0.1 L42). There is NO positional rule against `count()`: it is accepted wherever it is written, and
  the compiler refuses it only when building it exceeds the BUDGET (its state cost), the refusal naming the `occurs`
  form as the fix. Below the budget the compiler may RECOMMEND the `occurs` form (a named warning) as the way to reduce
  states. A later, separate plan item, [COUNT-TO-OCCURS] (not phase 1): where the compiler can PROVE the answers do not
  change, it rewrites a `count()` test into the `occurs` form itself. What `occurs` saves over `count()` for the same
  test belongs to the lowering section of a later revision; the budget: §13 O39.
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
states rather than rules"); the budget as a labelled measured quantity: LEAN (manager's note, CF:832; §13 O39). The
automatic rewrite: RULED as a LATER plan item (CF:840). Tuples as a library macro: RULED (CF:644), SUPERSEDES predx's
tuple-on-the-left-of-`:` syntax (S12); its spelling: OPEN (C25). The comma form of the semver condition: RULED (CF:704).

## 9. Cut from the first spec

**RULE.** Not in the first spec: INTERFACES (`type(...)`, `isodate: date`), TYPE MEMBERS declared with a type,
SCOPE-LIMITED UFCS (`d.weekday` resolving to a scoped macro), `types()`. Interfaces may return after a build as
LIBRARY PACKAGING (a set of required labels with value types, checked by inclusion per field, at the module export
boundary). The NO-SEMANTIC-OVERRIDE rule (two compliant formats holding one date must agree) stays as a rule for
that return. Namespaces stay (§7, §13 O46; a definition's labels are dotted paths).

**REASONING.** predx §9: none of thirteen programs needed them; UFCS adds a third resolution rule to `.` (the
metadata members are already one: §13 O31).

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
IS EXACTLY TODAY'S PCRE PATTERN: no strict subset, no level beyond today's engine choice, no set position (G3).
Top-level `:=` replaces DEFINE for new code; DEFINE stays only as PCRE syntax inside a literal with PCRE's meaning.
The predicate opt-in selects WHICH LANGUAGE a file or API call is in. Library files are expression-language files
with `@export`. The `.rxt` format is unchanged. Crossings: rx -> expression by `${...}`, and by `(?&name)` naming
the pattern binding whose own literal it sits in (self-recursion only, §7; CF:113); expression -> rx only by `/.../`.

Literals: full PCRE inside, `\/` escapes; a literal means EXACTLY what PCRE means: NO implicit extended mode
(`/foo bar/` keeps its space, `#` is literal); extended mode is per literal (`/.../x` or a leading `(?x)`). A literal
is its OWN SCOPE (numbered groups do not leak; named groups are fields of its value); NO INHERITED FLAGS (a hole's
pattern keeps its own flags: §13 O32). Inside a LARGER program, literals start from the STRICT PURE SUBSET (refuse
`\K`, `(*ACCEPT)`, `\G`, backtracking verbs, callouts/inline code, each admitted later once its predicate meaning is
defined; unbounded backreferences need `vm`).

STRING SETS. A pattern used as a SET denotes the strings it matches ENTIRELY (keys starting with S are `/S.*/`).
SET POSITIONS are: an `&` operand, a label condition, a filter body (incl. a modified filter's argument, §2.7, and
a filter passed to any macro), a hole's set (together: FILTERS, the first three each applied to a SPAN of the
subject, the last a part of the filter it sits in), and a compile-time set (an `enumerate` argument, an `@assert`
argument, a name set for `import`/`@export`/`@warn`, a computed label's value, a `records` item).

THE FILTERED SPAN (stated once; CF:761). In a filter, `^` and `$` mean the START and END OF THE SPAN BEING FILTERED,
not of the subject. `/\w+/ & /^foo/` accepts the words that start with `foo`, exactly as `/\w+/ & startsWith("foo")`
(§0.1 L41); `P & (x: /^S\w*/)` constrains x's own start (L7); `alts & !/^#.*/` drops entries starting `#` (L11). The
lone program `/^foo/` is different because it is a FINAL pattern, searched in the subject: there `^` is the subject's
start (or a line start under `(?m)`). This RESTORES the 2026-11-13 understanding ("b was in the span context of a",
CF:56 "in-context stays for pattern-level &") in exactly this sense, and it SUPERSEDES the 2026-11-14 Q1 entry's
listing of `^`/`$` among the errors (CF:713-717); the foundation stays STRING SETS (CF:761 (1)). A compile-time set
has no filtered span; there `^`/`$` are the string's own ends (this document's extension, LEAN).

ONE SPAN PER FILTER ROLE (review r8 P6-5; LEAN until the owner confirms, §13 O49). The span is fixed where the FILTER
ROLE is: the `&` operand's text, the label's value, the value searched by `~`. Nothing written INSIDE a filter opens
a span of its own: a filter passed as an argument to a macro (`contains(/^err/)`, `padded(/^5/)`, a user macro) and
an rx inserted in a hole of the filter's body both read the span of the filter they are part of. So `contains(/^err/)`
= `startsWith("err")` although `contains`'s body puts the argument in a hole after `.*`; `$m !~ /^err/` and `(m:
!contains(/^err/))` agree (§2.6, §0.1 L17). This is the owner's rule ("^...$ meant the start and end of the filtered
condition", CF:761-768) applied to arguments, not a property of `contains`, `startsWith` and `endsWith`. It agrees
with §2.7's "the argument's own start and end" (`padded(/^5/)` = `padded(startsWith("5"))`): a modifier's argument
filters the span AS THE MODIFIER READS IT, which is the same span read through the modifier, so its ends are that
span's ends. In a FINAL pattern a hole's `^`/`$` are the subject's (or a line's) ends, as in the pasted text. Rev 6
read `^` in a hole as the HOLE's own start, which made `contains(/^err/)` accept `xerr` while §0.1 L17 said it was the
same as a search for `/^err/` (review r8 SIM-1).

An assertion that would READ BEYOND THE FILTERED SPAN is a COMPILE ERROR naming the fix (CF:761 (3)): `\b` at the
span's start or end, and (LEAN, the manager's reading) a lookaround that can read outside the span, reachable at its
start through a nullable prefix or at its end through a nullable suffix; the property is decided statically on the
pattern. `^`/`$` are NOT in this class:

    "`\b` in the condition on x reads text outside x: put `\b` in the pattern that places x"

Assertions strictly INSIDE the span keep PCRE meaning (`(x: /\d+\b\.\d+/)`: the `\b` reads only x's own characters).
MULTILINE (C35, CF:753): an explicitly written `(?m)` keeps PCRE's meaning inside the span (`^`/`$` also at line
breaks within it); without it `^`/`$` are the span's ends; never does either read outside the span. CAPTURED STRINGS
(`$x`, a one-string set), what a modified filter reads (its reading's output, §2.7) and compile-time sets are
CONTEXT-FREE. In a
SEARCH inside a value (`$x ~ rx`, §2.6) the value is the whole subject of that search, so `^`/`$` are the value's ends
(D193 add. 3). FINAL patterns and a `records` item rx are SEARCHED in their subject and keep full PCRE meaning,
context assertions included. Nullability for the empty-match rule is computed IN CONTEXT (§7). A named in-context form
(a library call, no keyword) is added only on a measured need (D77).

HOLES `${expr}`: every hole denotes a SET OF STRINGS and matches one of them: a one-string set (a captured string, a
quoted literal) inserts LITERAL TEXT (never re-parsed), any other rx inserts a sub-pattern (`${isodate & (year:
2000)}` = a sub-pattern insertion); a MACRO in a hole is the unapplied-macro error (§2.3; CF:362). A hole's set is a
set position for the edge-assertion rule (a `\b` or edge lookaround at its edge is the error above, L8; write the
assertion in the literal around the hole); its `^`/`$` are the enclosing filter's span ends (above). In the inner direction (an API caller passing a PCRE string) a GUARD is written with an explicit `&`:
`(\d+)&${ <256 }`; a hole after an atom WITHOUT `&` is a FOLLOWING item (`(\d+)${ <256 }` = digits followed by a
numeral below 256). Generalized backreferences (`(?<y>\d{4})-${$y + 1}`); holes are order-free; holes in typed SYNTAX
POSITIONS (`\d{${n}}`, `[${a}-${b}]`) supply that position's type from a finite set; holes never change structure
seen outside. Run-time PARAMETERS (`limit := param(/\d{1,4}/)`) are read-only per match, validated against their
type, read AS LATE AS POSSIBLE; computations on parameters only are default-level (§6.1).

**REASONING.** Making PCRE text a literal gives G3 without a mode switch; free-form multi-line layout belongs to the
expression language, not to literals (C2); the strict subset applies only where a literal sits inside a larger
program (review OWN-14). The Q1 foundation: review r1 compared context-marked triples (A), value-scoped string sets
(B1) and string sets composed in context (B2); the rule set is string-set shaped, and rev 2's argument for A did not
discriminate (its cases are FINAL patterns, searched under every model; Q1R-12, Q1X-1). Under A or B2 look-alikes
fail SILENTLY (`\w{3} & /\w+\b/` moves the match; a `^` condition on a repeated label passes one header and fails
two); under B1 others do (`n: p` dead for a lookbehind `p`). With `^`/`$` bound to the filtered span (CF:761) the `^`
look-alikes agree with `startsWith`; every remaining divergence needs an assertion that reads outside the span, a
static property, and refusing exactly those leaves no silent failure and no unbuilt lowering at the default level
(G0, G2). Nullability in context is A's one real gain, adopted. What a hole holds (one string or a set) decides its
insertion, never the text's content (no injection); a guard needs `&` so the hole rule has no exception (C4).

**STATUS.** Outer layer: LEAN (CF:564, "Lean ADOPT"). Literal leanings incl. the strict subset: RULED (CF:56, "I like your
suggestions"); the subset scoped to literals inside a larger program and the one-literal program = today's pattern:
LEAN (review OWN-14). No implicit x-mode: RULED (CF:577, C2). STRING SETS: RULED (CF:713, CF:761 (1)). In a filter
`^`/`$` = the ends of the span being filtered: RULED (CF:761 (2), SUPERSEDES the part of CF:713 that listed `^`/`$`
among the errors); its extension to the compile-time sets (no span is filtered there; `^`/`$` = the string's ends):
LEAN (this document). Assertions reading beyond the filtered span refused: RULED for `\b` (CF:761 (3)); edge
lookarounds in the same class: LEAN (manager's reading, CF:761). `(?m)` written explicitly: RULED (CF:753, C35).
Context-free captured strings, modifier readings and compile-time sets, nullability in context, a named in-context form only on
measured need: RULED (CF:713). The three candidates and the restated reasoning: LEAN (review Q1R-1, Q1X-2, Q1R-12,
Q1X-1). Guard holes with `&`: RULED (CF:573, C4); a macro in a hole the unapplied-macro error: RULED (CF:362). One
span per filter role (an argument or a hole reads the enclosing filter's span): LEAN (review r8 P6-5; §13 O49). The
`(?&name)` self-recursion crossing: LEAN (CF:113). Holes: RULED (CF:80, CF:81). Parameters: RULED (CF:84); the
interface rides [IFACE-PUSH]. `&` and `${}` as the only rx additions: RULED (CF:795). Finite-group backreferences as
regular: a general engine row, [BACKREF-FINITE] (RULED, CF:583, predx Q10: not #6). `&` in rx text: §13 C23.

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

THE TWO-WAY CENSUS (G0b; review r8 P6-9, OWNER-12). G1's check runs case -> construct (every case uses only §§2-8);
this table runs construct -> case. Counts are uses in §12's code lines, comments stripped (command in
`docs/dev/lanes/predspec7_report.md`). A construct with no case is LISTED, not cut and not given an invented case:
the owner decides which stay in phase 1 (§0.2).

| construct | §12 cases that need it | if none: why it is carried |
|---|---|---|
| `&`, `\|`, prefix `!`, `:=`, `,`, `[ ]`, `( )` call/condition, `=`, `:` in a condition, `.`, `$x`, `${}`, comparison sets, `-`, `/.../` | all twelve between them (§5.4's MARK TABLE names the cases per mark) | |
| `@assert`, `import`, `param`, `enumerate`, `records`/`file_text`, `each`, `join`, `list_of`, `occurs.*` | E-IPV4, E-CAL; E-JSONL, E-IPV4, E-HTTP, E-DEPTH; E-NEAR; E-SEP; E-FILE; E-FILE, E-SEP; six cases; E-HTTP; E-HTTP | |
| `count(...)` | none in code (E-HTTP's prose only) | RULED as the first spelling (CF:823, CF:832) |
| operator section `(& f)` in code | none (prose only, §5.2, §5.3) | RULED, IN phase 1 (CF:753) |
| search `~`, `!~` | none | RULED as a construct (CF:74, CF:873, CF:880-887); phase 1: the owner's |
| positional `X[...]` | none | RULED (CF:553); needed by the owner's search example (§2.6) |
| `where`, `where_group`, `each_group` | none | LEAN (§3.2, §5.3); candidate cut |
| `when(c, p)` | none | RULED (CF:184, "Add when") |
| typed parameters `m(x: T)`, `pure`, `pattern()` | none | LEAN (CF:149); §13 O48 |
| `eval` | none | LEAN (§10); an opt-in module |
| `@export`, `@warn` | none (library files are not cases) | LEAN (CF:608, CF:619); warnings RULED (CF:666) |
| `*`, `%` | none | RULED in kind (arithmetic, CF:782 (1)) |
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
`padded(between(0, 255))` admits it, a stated library choice). As a SEARCH program, `256.1.1.1` yields `56.1.1.1`
(held under libpcre2); a boundary is the user's to write, in the final pattern around the hole: `/\b${ipv4}\b/` on
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

    isodate := (as in 12.2)
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
computation on a parameter only (anchor +- 15 days, once per match) and a parametric comparison: LEVEL default
(§6.1). (c) a relation with ~3.65M classes (§4.6): at the default level a compile error printing the count and
naming `functions`; under `functions` a linear arithmetic check on DFA-validated candidates. `2026-11-01,
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
search program is an error, the `empty.search` hazard, §7); a TRAILING newline gives none (PCRE2's multiline `^`
does not match after a final newline; Python's `re` differs). A CRLF line `foo\r\n` is not matched at all by `lines`,
so the tiling error names the whole range `foo\r\n`, not just the `\r`. NOT YET A VALID ACCEPTANCE CASE: the `\n`
terminators belong to no record, so under the tiling rule as written E-FILE is itself a tiling error until O20
says how an item rx declares its separators (§13 O20). A changed `w.txt` under its pin is a compile error.

### 12.9 E-HTTP: header block with occurrence counts

    occurs := import("occurs")
    header := join([name = token, value = fvalue], sep = ":")    # token, fvalue as in predx §3.8
    headers := list_of(header, sep = /\r\n/)
    headers & occurs.exactly(1, (name: any_case("Host")))
            & occurs.at_most(1, (name: any_case("Content-Length")))
            & occurs.none((name: any_case("Transfer-Encoding")))

`name` is a repeated label: a bare `$name` would be an error (§4.3). Each `occurs` filter is a capped counter (n+2
states: 3, 3, 2) multiplied into the loop. The condition is passed as a parenthesised literal (a required positional parameter, C31 RESOLVED 2026-11-14); the
labelled-argument spelling `occurs.exactly(1, name: ...)` is not used.
The `count()` spelling (§8) is the same test: `n_host := count((name: any_case("Host")))` and `headers & (n_host:
==1)`; at these bounds it is within any budget, so it is accepted, and the compiler may recommend the `occurs` form.
LEVEL: default. Expected: a block with one `Host:` line and no `Transfer-Encoding` -> match; two `host:` lines -> no
(`any_case`).

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
Expected: `[[1]]` -> match; `[[[[1]]]]` -> the whole subject is not a `value_depth(3)` (search finds an inner
`[[[1]]]`). Defining one name by several literal-argument cases is how predx spells the base case; whether that
form is admitted generally is not stated (§13 O21).

### 12.12 E-CTX: assertions in set positions (the cases that decide Q1)

Each case puts an assertion where the three candidate models (§11) disagree; the answer is the RULED one (string
sets, `^`/`$` = the filtered span's ends, the edge-assertion error for `\b` and edge lookarounds; CF:761). E-CTX-1, 5
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

- E-CTX-1: NO error; `^` is x's start: `a Sab` -> match `a Sab`, same as `(x: startsWith("S"))`. (A/B2: silent no
  match; B1: match.)
- E-CTX-2: compile ERROR (`\b` at both edges of the hole's set). Fix: write the boundaries in the literal around the
  hole, `/a\b${/\d+/}\b/`, which says what the pasted text says: on `a12` it finds nothing (`a` and `1` are both
  word characters). (B1: match, unlike the pasted text.)
- E-CTX-3: compile ERROR (a lookbehind at the start of an assertion argument). Under A the assertion FAILED although
  the subject `5` never matches. Fix: assert on strings without the lookbehind (`@assert.some("5" & /\d+/)`); search
  behaviour is shown by an example subject, not by an assertion (§5.6, §13 O36).
- E-CTX-4: compile ERROR (`\b` at the end of an `&` operand). Fix `/\w{3}\b/`: on `foobar` it reports `bar` visibly,
  from the final pattern. (A/B2: the reported match silently moves from `foo` to `bar`.)
- E-CTX-5: NO error; `^` is the start of the modified filter's argument, same as `x & padded(startsWith("5"))`.
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
  (CF:573), §11. **C11** purity vs ambiguity: RULED (CF:583, Q2), §4.5. **C14** size-cap fallback: RULED (CF:583,
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
  number type)" is withdrawn (CF:782 (3)), §8. `some`/`all` as built-ins or library names: C28.
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
  span (line breaks within it); without it `^`/`$` are the span's ends; never reads outside, §11.
- **O17** D196's F7 in-context lookaround: RULED for set positions (CF:713, CF:761 (3): an assertion that would read
  beyond the filtered span is refused; final patterns keep PCRE meaning; the 2026-11-13 span-context understanding,
  CF:56, is restored for `^`/`$`), §11. `\K` refused; verbs, cross-operand backrefs (finite: `enumerate`; general:
  [BACKREF-FINITE]), recursion remain as listed in rev 2.
- **O23** the `occurs` namespace name (rev 5): RULED in use (CF:782: "use 'occurs' module like occurs.at_least(3,
  ...)"; "i suggested an 'occurs' type module that would handle structural predicates").
- The call form `isodate(year: S)` and the labelled-argument addendum: WITHDRAWN, RULED (CF:744), §4.1, §5.2.
- Review RUL-4 (right-associative `&` vs the chain label lookup): dissolved by OWN-1 (pure `&`), §4.1. Review RUL-10:
  answered by CF:706 (labelled arguments always narrow), §5.2.

STILL OPEN (contradictions):
- **C3. DEFINE bindings in the inner direction.** 2026-11-13 evening: an opted-in DEFINE holds `name := ...` bindings.
  2026-11-14: DEFINE stays ONLY as PCRE syntax inside a literal; API callers keep the inner direction (`(\d+)&${ <256
  }`). Reading A: inner-direction patterns have holes but no bindings. Reading B: inner-direction DEFINE keeps `:=`.
- **C5. Multi-index comma.** 2026-11-14 00:10 (a manager lean): `A[1,3,5]` NOT adopted, comma kept for `A[i, j]`;
  the `[]` positional note lists `X[1,3,5]` as valid. Rev 6: NARROWED by CF:863, which names "a multi-index if
  adopted" under the array bracket: IF adopted, `X[1, 3, 5]` = `X[1|3|5]` (any one of those positions, result an
  array keeping the original positions), and the comma can no longer be a dimension separator (`A[i, j]` would make it
  carry logic; write `A[i][j]`, as `d[1][1]` already does). Still open: whether to adopt the multi-index at all.
  Lean: adopt (it costs no new rule; `X[[1, 3, 5]]` then reads the same).
- **C7. Value-valued maps.** 2026-11-13 `["US" => "United States"]`; 2026-11-14 views: labels are names, the value
  per branch shown is `.index`. Reading A: other values are computed labels (now bindings, §4.4) or record arrays
  (predx C7). Reading B: `=>` survives.
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
  ruled "order- and grouping-free" (CF:722). `.index` after `&` with an array of filters (§3.5) depends on it, and
  so does the owner's search example (§2.6: `d & (g: x)` keeps entries 1 and 3 with their original positions).
- **C18. Named assertions vs the `@` rule.** Named failures via `leap_1900 := assert_none(...)` (CF:595); the `@`
  lean (CF:619): effects cannot drop `@`, only `@` forms are bare statements. A named assertion is then
  `leap_1900 := @assert.none(...)` (an `@` inside an expression), a binding without `@`, or not allowed. Rev 6: a
  binding names an rx or a macro (CF:858) and an assertion is neither (C19), so the binding readings are out. Lean: a
  name is a labelled entry of the assertion's call record, `@assert.none("1900" & leap, name = "leap_1900")`.
- **C23. `&` in rx text.** C4 ruling: the guard is `(\d+)&${ <256 }`, an `&` inside PCRE text; the owner lists `&`
  (with `${}`) as the rx additions the predicates need (CF:795); but a literal means EXACTLY what PCRE means (CF:577),
  where `R&D` is three literal characters (G3). Reading A: `&${` is a two-token marker, rx syntax only before a hole.
  Reading B: `&` is an operator throughout rx text in the predicate opt-in (a one-literal program then differs from
  PCRE on `R&D`). Lean: A, which keeps G3 and still gives the owner's `&` in rx.
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
- **C28. `occurs.all` vs the sequence rule.** §4.3: `x: S` on a repeated label already means all iterations; the
  counting ruling adds `occurs.all((x: S))` (rev 6 wrote `occurs.all(x: S)`, a `:` in a call record, an error by
  §5.4; review r8 SIM-3). Either they are synonyms or `x: S` means something else (§0.1 L36; O28).
  Also open here: whether `some`/`all` are built-ins or library names (review RUL-13).
- **C29. `(x & isodate).year`.** `isodate(x)` is a compile error (CF:744, CF:749). What remains: whether `.year` of
  `x & isodate` is a VALUE (the cut layer's `(X & isodate).weekday`) or the map-view PATTERN of the part (§3.2).
  Reading A: `.` on any rx is structural and values are only `$`-forms (`$d.year`). Reading B: `.year` of an
  application is a value. Rev 6 leaned A citing the search result's `d.year` as "the set of the occurrences' years"
  (CF:874), but that sentence is the manager's gloss, and what `d.year` means across several entries is OPEN (O50
  (b); review r8 DRIFT-7). The conclusion survives every O50 reading (each gives an rx or a label, never a third
  thing); the premise does not. Lean A (unchanged), argued from §3.1 alone: the map view of an rx gives an rx.

Open items (rev 0, still open):
- **O1.** The meaning of a program's final expression against the subject (search vs whole-subject test). The
  empty-match rule presupposes a SEARCH MODE chosen by the caller (predx O1 lean: the caller picks); not ruled.
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
- **O12.** `!~` once `!` is a filter: keep (as the sugar of §2.6, review RUL-5), or drop it (no edge-assertion
  special case remains, C32). Rev 7: `$m !~ r` is a condition while `$m ~ r` is an rx (the array of results), so `!~`
  is not the negation of `~` (§0.1 L51); decided with O50 (c).
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
  label-free `f` (the "useless in a search" worry is what the empty-match rule already catches); plus a warning when a
  negated numeric comparison meets a target with non-canonical members (`0150`, `abc`).
- **O27. Does quoting a constant decide how it compares?** (OWN-3.) `a := 256` and `b := "256"` are the same set, yet
  `x & <a` compares numbers and `x & <b` compares text (`1000` out vs in), and `@assert.same(a, b)` passes. The same
  question covers arithmetic results (does `${$y + 1}` on `0099` insert `100` or `0100`?) and leading-zero bounds
  (does `between(01, 12)` admit `1`, `05`?). Lean: make numeric vs text a property of the comparison you write, not
  of how the constant is quoted; arithmetic yields canonical numerals; width is set with the padding modifier.
- **O28. One rule for conditions on optional, repeated and never-entered labels?** (OWN-4.) On `1,7,` with a
  repeated n, "not all below 5" (`!(n: <5)`) matches while "each not below 5" (`(n: !<5)`) does not; on an optional
  label that is unset the two sentences of §4.2 disagree; `?` vs `*` around the same group flips `(n: <5)` on `end`.
  Lean: a condition holds when EVERY occurrence is in the set AND there is at least one (zero iterations = unset =
  fail); `!(x: S)` is its plain complement; `(x: !S)` = every occurrence outside S; a warning with a witness when the
  two differ for the pattern at hand; `occurs.all` an alias or removed (C28).
- **O29. Does each `some` pick its own occurrence?** (OWN-6.) Two `occurs.some` filters may use different
  iterations (filters combine independently), but §2.6 says every `some(s)` over one search set is the SAME
  occurrence. Lean: each `some(...)` picks its own witness; to make one occurrence satisfy two tests, write one `some`
  with both tests conjoined. This deletes the "two occurrences need two names" rule.
- **O31. The dot family, and level selection.** (OWN-7, RUL-12; WIDENED in rev 7 by review r8 P6-12, CENSUS-24.)
  One `.` carries four resolutions: (1) a LABEL of the map view (`d.year`, `rest.year`); (2) a module MEMBER
  (`json.row`), which is name resolution if a module is a namespace (O46's lean), not navigation on a value;
  (3) METADATA (`.index`, `.label`), which share the dot with user labels: for `/(?<index>\d+),(?<label>\w+)/`, is
  `r.index` the label or the position?; (4) a PATH under `$` (`$rest.year`; `$` covers the whole path, §5.4). §9 cut
  UFCS for being "a third resolution rule to `.`"; the same argument applies here. Readings: (A) one meaning, the
  field of the map view of the thing on the left, with modules read as maps of members and metadata as reserved
  fields (an error for user labels so named); (B) the dot for labels and members only, metadata as call-position
  built-ins (`index(x)`, `label_of(x)`); (C) a non-alphabetic metadata mark. Lean: A for labels and paths (§5.4's
  `.` row), B for metadata; members follow O46. Also unstated: how a program selects `functions`/`captures`/`vm`/
  `eval` (as strings or API options, not bare words).
- **O32. Flags of a pattern inserted in a hole.** (Q1R-11.) With no inherited flags, `q := /^\{.*\}$/` inserted in
  `/${q}/m` keeps single-line `^`/`$` and finds nothing on `{a}\n{b}`, while the same text inlined in the `m`
  literal finds both lines. Lean: a `flag.hole` warning naming the fix (`q := /.../m`), or state the flags of a
  binding explicitly.
- **O33. Two conditions on an ambiguous pattern.** (RUL-3.) `/(?<a>\d+)(?<b>\d+)/ & (a: <5) & (b: <5)` on `123`:
  each condition passes on SOME parse (true per condition, the extensional reading), no single parse passes both
  (merged narrowing: false), PCRE's chosen parse gives false. Lean: per-condition some-parse (the extensional
  reading), with the `label.ambiguous` text saying that two conditions may be met by different parses.
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
  name, not a keyword). Not dispositioned by the review; recorded.
- **O37. Two modifier names this document chose.** `unpadded(n, S)` (rev 2's `pad(n)`: the filter reads a subject
  as if zero-padded to width n) and `json.quoted(S)` (rev 2's `jstr`) are placeholders under the naming rule; the
  ruling named `padded`, `any_case`, `quoted`, `length`, `month_numbered` only.
- **O38. Look-alike rows with no diagnostic.** §0.1 marks GAP rows (rev 7: L20, L21 on answers, L22, L24, L29-L33,
  L35, L51; L23, L25 and L48 are BY DESIGN, the stated meaning of a mark, §5.4):
  DIFFERENT with no named diagnostic, so G0's acceptance fails on them today. Some are open items above; L20 (a padded
  target against an integer comparison set) and L25 (`/a|b/` vs `/b|a/` under `[]`/`.index`, by design) have no item:
  whether a documented structural difference (a BY DESIGN row) also needs a diagnostic, and which warning L20 gets,
  are open. Also from OWN-15: whether the goal order G1 > G2 should be stated as G2 > G1 at the default level (what
  the rules do, §0 Goals).

Open items NEW in rev 5 (from the 2026-11-15 entries and the rev 4 audit; plain words, each with a leaning):
- **O39. The budgets: how big is too big?** Two size limits are named but never set by the owner: (a) the
  class-count tiers of a relation between two labels (§4.6: "24 classes = fine, 1,440 = borderline, 3.65M = error"
  is the manager's answer to "how practical", CF:659-663, which the owner did not reply to); (b) the budget over which
  `count()` is refused in favour of `occurs` (CF:832). Lean: ONE budget, a labelled, measured state/size quantity
  that both tests use (the standing preference for measured budgets over structural rules; D77), shown with its
  number by the cost report, with no fixed thresholds written into the spec.
- **O40. What is a number?** The owner wants numbers to be one kind (CF:813, CF:823); rev 4 treated numbers as
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
  same question covers a RUN-TIME PARAMETER (`anchor := param(isodate)`, E-NEAR (b)), also bound by `:=` and neither
  plainly an rx nor a macro; the KIND TABLE (§2.1) lists both. Readings: (A) both are named by `:=` but are not
  values (a third BINDABLE shape beside the two value kinds, never passed or returned); (B) a parameter is an rx whose
  string the caller fixes per match (a value), a module a namespace (not a value); (C) both become values (a third
  value kind). Lean: B (it keeps two value kinds and needs one non-value shape, the namespace).
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
  not to decide now.
- **O49. One span per filter role: confirm.** (Review r8 P6-5, ruled FIX-NOW by the manager; LEAN until the owner
  confirms.) Rev 7 states that `^`/`$` in a filter passed as an argument, or in a hole of a filter's body, are the
  ends of the span the enclosing FILTER ROLE filters (§11 ONE SPAN PER FILTER ROLE), so `contains(/^err/)` =
  `startsWith("err")`. The alternative: a hole (and so an argument a library body puts in a hole) opens a span of its
  own, `contains(/^err/)` = `contains("err")`, with a diagnostic for an anchored argument (review r8 P6-5 (b)). The
  consequence the owner should see: under rev 7, `\b` at a hole's edge stays the edge-assertion error (L8, CF:713)
  while `^` in a hole reads the enclosing span: two assertion kinds, two rules, because `^` needs no text outside the
  span and `\b` does. Lean: rev 7's reading (it is the one a user expects, G0, and it is the owner's 11-15 rule,
  CF:761, applied without exception).
- **O50. What a search result IS at match time.** (Review r8 P6-7: OWNER-10, RUL-8/9, CENSUS-11, DRIFT-1..8; the
  largest open item of the round.) The owner: "an array of all of the results. You could use count to check the
  number of results. You could treat it as an array. You could use the occurs module" (CF:881-883). His EXAMPLE
  (§2.6) is the behaviour every answer must give: on `abx aby abx`, `d := <subject> ~ /ab(?<g>[xy])/` has `count(d)`
  = 3, `d[2].g` = `y`, and `d & (g: x)` keeps entries 1 and 3, positions kept. The array tools were defined over
  SPELLED arrays at compile time (G4, §3.4, §5.3); `d` is a MATCH-TIME array (§3.4). Parts and readings:
  (a) THE TOOLS. (A) Two populations stated once: on a match-time array, `[i]` with a literal or bounded i,
  `count`, `&` per entry and `occurs.*` are match-time tests (regular: counters, CF:62's cost rule), while `each`,
  `join`, `where`, `enumerate`, `.label` are a compile error naming the match-time source (DRIFT-2). (D) The search
  result is a REPEATED LABEL, one iteration per occurrence (`$m ~ P` read as the value matched against
  `(?:.*?(P))*.*`), so §4.3's sequence rule and §8's `count`/`occurs` cover search results with no new rule, the
  owner's own pairing of search results with repeated captures (CF:75); DRIFT's lean. Note: under the sequence rule
  `(g: x)` on a repeated label means ALL iterations, so `d & (g: x)` would TEST every result rather than SELECT
  entries 1 and 3; to give the owner's example, (D) needs `&` on a search result to keep entries (the array
  reading, §3.2 tool 2), i.e. (D)'s counting with (A)'s per-entry `&`.
  (b) `d.g` ACROSS ENTRIES. (A) the union set (rev 6's text; loses multiplicity: `count(d.g)` is not the number of
  results); (B) the projection array, `d.g[i]` = `d[i].g` (keeps order and multiplicity; extensionally equal to A
  under `& | !`); (C) per entry only, `d.g` an error on a multi-entry array; (D) the repeated label: `(d.g: S)` = every
  result, `occurs.some((d.g: S))` = some result.
  (c) THE FILTER ROLE. (a) `~` only produces a value; the test spelling is the condition `(m: contains(r))`, `!~` its
  complement, and a bare `$m ~ r` in the filter role is an error naming it (§0.1 L16, L51); (b) a search result in the
  filter role means "non-empty", an emptiness-to-test coercion seen nowhere else. DRIFT's lean (a).
  (d) THE RECORD ON THE LEFT, `(x, y) := $m ~ P` (design only, out of phase 1): (i) the projection arrays, paired by
  index; (ii) one indexed entry (`[1]` implied, or an error unless at most one result); (iii) the union per field
  (rev 6's text); (iv) the first two RESULTS (entries are index-labelled, §3.1; Python's `x, y = re.findall(...)`),
  which rev 6's rules also admit: the same spelling with two meanings (§0.1 L50). DRIFT's lean: laid against the
  search pattern's GROUPS only, never entry positions, per result via (D).
  (e) `some`/`all` over a search result: `x & s`, `some(s)` and `occurs.some(...)` are three spellings of "some
  result" with two witness rules (O29).
  Lean (this lane's, after the owner's example): (A)'s two populations with `&` selecting entries (the example's
  `d & (g: x)`), counting and `occurs` read as (D)'s repeated label (one population for `count`, CF:75), `d.g` as the
  projection array (b) (B), the filter role (c) (a), the record on the left (d) over groups. Phase 1: the owner's
  call (§0.2); no §12 case uses search.
- **O51. Statements that start with `(` or `[`.** (Review r8 P6-13, CENSUS-14.) `(` and `[` after an expression are
  always a call or an index, and newlines are layout (§5.1), so `t := foo` NEWLINE `[a, b]` parses as `foo[a, b]` and
  `d := ...` NEWLINE `(x, y) := ...` as a call. The final-array half is live today; the destructuring half is design
  only. Readings, for the spelling step: (A) a statement never starts with `(` or `[` (a record on the left gets a
  leading mark; a final array is bound first); (B) a newline is significant before `(` and `[`. Lean: A (no layout
  rule; one-token look-ahead stays as §2.5 argues).
- **O52. FAMILIES and the general form behind them.** (Review r8 P6-16, CENSUS-25/26; a unification candidate, not a
  rev 7 rewrite.) ANY ONE is spelled `|`, `[ , ]`, `some`, `occurs.some`, `X[1|3|5]`; ALL TOGETHER `&`, `( : , : )`,
  the sequence rule, `occurs.all`; a NAME is introduced by `:=`, `[x = e]`, `(?<x>...)`, a head parameter, a record
  on the left. General form: one ENTRY LIST whose bracket names the combiner and whose entry marks are fill (`=`) vs
  narrow (`:`). Unlocks, each with its TRIGGER: (a) `join`'s ordered parts in a call record (`join(year = ..., month =
  ..., sep = "-")`-shaped), so `[ ]` reads only as any-one; trigger: the variadic record O47 needs, one mechanism for
  C25, O47 and this; (b) piecewise definitions as narrowed heads (`value_depth(k: 0)`), no new form; trigger: O21
  decided, or a second recursive library; (c) one meaning of `:` (O48 (A)); trigger: any typed-parameter build;
  (d) mixed rx/macro arrays and `each(isodate, dates)` without a section (§3.5's mixed-array error goes); trigger: a
  worked example with a mixed table, or C33's "other sections on need". Lean: record the family; decide each unlock at
  its trigger (D77).

FAMILIES noted by the review (PLAN; not folded): value mappings (RUL-F1); quantifiers and emptiness checks, now
incl. `count()` vs `occurs` (RUL-F2); same-text-twice (O34, RUL-F3); name-set selection (RUL-F4); the dot (O31,
RUL-F5); application spellings (C29, RUL-F6; C20/C30 resolved).

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
  Names that denote non-values (namespaces, run-time parameters): the kind table, §2.1, §13 O46.
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
`cond_family_syntax_survey.md`'s `&!` and `=~` spellings are superseded (`!` filter, `~`), its "opt-in, not default"
and "do not touch class contents" recommendations stand.
