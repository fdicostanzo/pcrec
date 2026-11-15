# predspec8 report: predicates_draft.md rev 8, the owner's three latest rulings folded (design only)

## STATE AT HANDOFF

STATE: done. Branch `lane/predspec8`, from main a7509b64e. Deliverables: `docs/design/predicates_draft.md` rev 8
(changelog entry first) and this report. Design text only: nothing under `src/`, `cli/`, `lib/`, `memfn/`, `tests/`
or `docs/spec/` touched; COND-FAMILY.md and plan.md not edited. Rulings file `docs/dev/lanes/predspec8_rulings.md`:
empty at every commit and at this report; last R-n applied: none. Validation: `make test-plan-lint` in the worktree
(checks passed: 2, failed: 0); pre-commit staged checks passed on every commit (52 passed, 0 failed).
OWED: none (no suites by brief).

Premise test held: `grep -c 'SEARCH IS A TRANSFORM' docs/design/plan_row_bodies/COND-FAMILY.md` = 1; the draft's
changelog said rev 7. "CF:n" = line n of COND-FAMILY.md at a7509b64e (926 lines, `wc -l`): the owner note CF:880-887,
the four answers CF:888-901 (his words CF:888-892), the transform ruling CF:902-926 (his words CF:903-905).

Size: `wc -lc docs/design/predicates_draft.md` = 2,284 lines / 225.3 KB (rev 7: 1,978 / 189.3 KB). Growth: the §0
rulings table for the 11-15 entries, §2.6 rewritten with definitions and hand checks, §4.3 rewritten as the home of
the group questions, §13 C36 and O53-O56.

The STOP RULE fired once: CONFLICTS FOUND (the priority parse vs §4.5's ruled some-parse rule); §2.6, §4.3 and §4.5
carry a CONFLICT mark and §13 C36 gives the readings without a pick.

## RULINGS FOLDED

(A) "a search result is the ARRAY of all results" (CF:880-887). His example (`abx aby abx`: count 3, `d[2].g` = y,
`d & (g: x)` keeps 1 and 3) stays the INTENDED BEHAVIOUR; rev 8 respells it under (C) in §2.6: the counts and
some/exactly questions as phase-1 group questions over the `hit` label, the one-iteration lines (`$m.hit[2]`,
`$m.hit[2].g`, `$m.hit & (g: "x")`) at the `captures` level, marked LEAN (the manager's lean, CF:924-926).

(B) the four answers (CF:888-901), each with where it landed:
1. "show me what this would mean" (the search result at match time): not a ruling; answered by (C).
2. Typed parameters OUT of phase 1 (CF:889, his words, RULED): §0.2 OUT line; §5.2 rewritten (a `:` in a head is a
   phase-1 error, `:` narrows only; rev 7's typed text kept for "more thinking", undecided); §5.4 `:` row; §0.1 L49
   (verdict DIFFERENT: ERROR (phase 1)); §13 O48 RESOLVED for phase 1, open in the design; O52 (c) trigger note;
   two-way census row; §8's "macros with typed parameters" corrected.
3. ARRAY and MAP are INTERFACES, never created values (CF:890-891, his words, RULED); a module is described by its
   MAP interface (CF:891-892, RULED; its kind not ruled): "view" -> "interface" throughout (§0.3 glossary row, §1,
   §3 retitled, §3.1, §3.2, §5.3, §5.4, §7, C29, O31); rev 7's §9 "interfaces" renamed DECLARED TYPES (one word per
   thing); kind table rows for module, interface, iterations; §7 module paragraph; O46 restated; C7 note; §14.
4. `.` has ONE meaning (CF:892 "agree" to the lean at CF:898-899; RULED by acceptance, marked so): §3.2 tool 4, §5.4
   `.` row, O31 (dot part decided; the metadata-name collision a LEAN error; level selection still open), C29 (lean A
   now follows from the ruled dot), §9 reasoning.

(C) SEARCH IS A TRANSFORM (CF:902-926; his own words are the transform idea, CF:903-904, and the question "could you
use some() to get some hits?", CF:904-905; everything else rests on "Do it", CF:905, and is marked "accepted at
CF:905"; the one-iteration level is marked LEAN as the brief says):
- `search` a library transform of the `contains` family; `~`, `!~` WITHDRAWN: §2.6 rewritten (title "Search and
  contains are transforms"), §8 library entry, mark table (two rows removed, STATUS says so), §0 spelling line, §11.
- the hit a REPEATED LABEL; plain condition = ALL hits; `some`/`all` the one spelling; `occurs` counts only (lean:
  `occurs.some`/`occurs.all` removed, not aliased); `x & s` re-examined (stays membership, L54): §4.3 rewritten as
  the general home with a table, §8, L36, L54, C28 RESOLVED, O52.
- SAME HIT BY RECORD: §4.3 with one example each way, L31 rewritten, O29 RESOLVED.
- the definition requirements (lazy gaps, the count along the priority parse, the empty-match advance, the look-alike
  row): §2.6 items 1-4, L52 (the required row), L53, O53, C36.
- the search-result question RESTATED as the array interface over ANY repeated label's iterations; group questions
  phase 1; one-iteration access at a higher level (LEAN): §3.4 rewritten, §4.3, §0.2 IN line, O50 restated, G4.

Required work (i)-(v) of the brief: (i) definitions and hand checks: §2.6 and EXAMPLES RE-CHECKED below; (ii) the
meanings over a repeated label and same-hit-by-record both ways: §4.3; (iii) re-check: below; (iv) mark table,
kind table, glossary, two-way census, changelog: done; (v) binding a search result and the record on the left:
§13 O54 (readings, lean, not decided), L50.

THE INTERFACE CHECK (B3's "nothing creates an array or a map as a free-standing value"). Places in rev 7 that did,
or read as if they did, and what rev 8 did with each:
1. §2.6 "a search result IS the ARRAY of all results", `d := $m ~ ...`, rev 7 §3.4's MATCH-TIME ARRAY: removed with
   `~`; hits are a label's iterations read through the array interface (FIXED).
2. §3.2 tool 1 "the result is always an array": now "an rx read through the array interface" (FIXED).
3. §3.3 "`|` CONCATENATES arrays", "`join` of an empty array": reworded to entries (FIXED).
4. §4.3 "`alt.x` returns every entry ... as an array": now an rx read through the array interface (FIXED).
5. §5.3 "`each` ... returns an array": now an rx (FIXED).
6. §5.5 "`enumerate(rx)` = the ARRAY of a finite rx's strings": now an rx whose array interface lists them (FIXED).
7. §7 "`records(text, rx)` = an ARRAY": now an rx whose array interface lists the items (FIXED); glossary row too.
8. §2.1 "the map-view tools' results ... are rx (arrays ...)": restated, plus a general sentence that every "returns
   an array" means an rx through the array interface (FIXED).
9. §3.1 `[x = /foo/, y = /bar/]`: stated that a `[ ]` literal WRITES AN RX and creates no array (FIXED); §5.4 `[ ]`
   row says the same.
10. §7 module "rev 5 called it a MAP" and the module value: restated as the map interface of a module, no module
    value (FIXED, O46).
11. §13 C7 `["US" => ...]` (a value-valued map): reading B would create a map value; noted, lean A (FILED, C7).
12. §8 tuple comparison "a structural macro over two arrays": the arrays are `[ ]` literals, i.e. rx; no change
    needed (CHECKED).
13. O50 (b) rev 7's "projection array" and (d)'s readings: removed with O50's restatement (FIXED).
Command for the remaining-word check: `awk 'NR>18' docs/design/predicates_draft.md | grep -n 'array view\|map view\|
MAP view\|map-view\|returns an array\|the ARRAY of'` returns only quoted words, history lines, or "the ARRAY of all
results" as his quoted note.

## EXAMPLES RE-CHECKED

THE HAND CHECKS of §2.6, run on the system libpcre2-8 10.46 (2025-08-27) through ctypes: the pattern
`(?s)(?:.*?(X)(?C1))*.*` matched with PCRE2_ANCHORED|PCRE2_ENDANCHORED (the whole value, as a set position
reads it), a callout recording each hit's span. Script: `$PCREC_TMPDIR/scratch/predspec8/hits.py` (not committed;
run with `python3 -I`). Output, verbatim:

    'ab(?<g>[xy])' 'abx aby abx' rc 3 hits ['abx@0', 'aby@4', 'abx@8']
    'aa' 'aaa' rc 2 hits ['aa@0']
    'a*' 'baa' rc 2 hits ['@0']
    '^err' 'err x err' rc 2 hits ['err@0']
    '^err' 'x err' rc 1 hits []
    'ab[xy]' 'xyz' rc 1 hits []
    '(?m)^err' 'err\nerr x\nok' rc 2 hits ['err@0', 'err@4']

Each row matched the hand derivation in §2.6 before it was run. The find-all control for the empty-argument row:
`python3 -c 'import re; print(re.findall("a*","baa"))'` = `['', 'aa', '']` (3), against 1 hit under the lazy-gap
body (§0.1 L53, O53). `rc` is the number of capture pairs set (1 = no hit; a callout fires only on a hit's success
path here, because the rest of the pattern always succeeds, so no abandoned hit was recorded). Caveat: this oracle
reads the PRIORITY parse, which is what record (5) requires; it says nothing about §4.5's some-parse reading (C36).

§12 WORKED EXAMPLES. Command: `awk '/^## 12\./,/^## 13\./' docs/design/predicates_draft.md | grep '^    ' |
sed 's/#.*//' > c12.txt` (67 lines), diffed against the same extraction from a7509b64e: IDENTICAL. Token counts
(`grep -cF -- TOKEN c12.txt`): ` ~ ` 0, `!~` 0, `search(` 0, `contains(` 1, `some(` 2 (both `@assert.some`),
`all(` 0, `occurs.` 3, `count(` 0, `(&` 0; typed heads (`grep -nE '[a-z_]+\([a-z_]+: '`) 0.

| case | verdict | note |
|---|---|---|
| 12.1 E-JSONL | unchanged | `contains("timeout")` is now in the search family; its body gains `(?s)` (LEAN), no expected answer moves (no line break in the values); `json` module: map interface RULED |
| 12.2 E-WEEKDAY | unchanged | |
| 12.3 E-IPV4 | unchanged | `@assert.some` is the assert library, not the group question |
| 12.4 E-LUHN | unchanged | |
| 12.5 E-CAL | unchanged | `@assert.*` as above; C13 unchanged |
| 12.6 E-RFC | unchanged | `.index`, `$rest.year`: instances of the ruled one `.` |
| 12.7 E-NEAR | unchanged | `param` half of O46 still open |
| 12.8 E-FILE | unchanged | `records` now "an rx whose array interface lists the items" (wording); `r.word` the ruled `.`; still not valid until O20 |
| 12.9 E-HTTP | unchanged | `occurs.exactly`, `occurs.at_most`, `occurs.none` are counts, which `occurs` keeps (CF:913); `name` is a repeated label under §4.3 |
| 12.10 E-SEP | unchanged | |
| 12.11 E-DEPTH | unchanged | `value_depth(0) :=` is a literal-argument head, not a typed one |
| 12.12 E-CTX | unchanged | E-CTX-5's `padded(/^5/)` and the anchored search argument share §11's one-span rule |

§0.1 LOOK-ALIKE ROWS (every row; "respelled" = same verdict, new spelling; "rewritten" = new verdict or content):

| rows | verdict |
|---|---|
| L1-L15 | unchanged |
| L16 | rewritten: `$m ~ /^err/` vs `(m: startsWith("err"))` (BY DESIGN, kinds) becomes `(m: search(/^err/))` vs `(m: contains(/^err/))` (BY DESIGN: search never rejects) |
| L17 | respelled: SAME unchanged; its `$m !~ /^err/` aside becomes `(m: !contains(/^err/))` |
| L18-L30 | unchanged |
| L31 | rewritten: GAP (two `occurs.some` vs one `some(s)`) becomes BY DESIGN (same hit by record), O29 RESOLVED |
| L32-L35 | unchanged |
| L36 | rewritten: OPEN (`occurs.all`) becomes SAME (`(x: S)` vs `all((x: S))`), C28 RESOLVED |
| L37-L48 | unchanged (L42's `count`/`occurs.exactly` kept: both are counts) |
| L49 | rewritten: BY DESIGN (head checks, condition narrows) becomes DIFFERENT: ERROR (phase 1), typed parameters out |
| L50 | respelled: still OPEN, `~` removed, lean the group reading (O54) |
| L51 | rewritten: GAP (`!($m ~ r)` vs `$m !~ r`) becomes ERROR (`!search(r)` empty vs `!contains(r)`) |
| L52 | new: the look-alike row record (5) requires (plain condition on a hit = all hits), BY DESIGN |
| L53 | new: nullable search argument vs find-all, ERROR (lean) |
| L54 | new: `x & s` membership vs `some(...)`, BY DESIGN |

Broken: none. O38's GAP list re-counted: L20, L21, L22, L24, L29, L30, L32, L33, L35 (9 rows; rev 7 had 12 with L31,
L51 and the L36 OPEN out of it).

## CONFLICTS FOUND

ONE, under the STOP RULE; not picked. Marked in §2.6 (requirement 2), §4.3 (head of section) and §4.5; written out
as §13 C36.

The priority parse vs some-parse. RULED (CF:583, predx Q2; draft §4.5): at the default level a condition on an
ambiguous label passes if SOME parse passes, and library patterns are checked unambiguous at their labels. Accepted
with "Do it" (CF:905; record (5), CF:919-920): "a repeated label's COUNT follows PCRE's priority parse". The search
body is ambiguous at `hit` for every argument (as a set the lazy gap is `.*` and can swallow a hit), and it is a
library pattern. Under some-parse every count from 0 to the maximum holds on `abx aby abx`, and `some((g: "y"))` and
`!some((g: "y"))` both hold; the owner's own example (count 3) cannot be given. Under the priority parse every
question has the find-all answer (the hand checks above), but outside §4.5's one-automaton/some-parse promise.
Readings: (A) §4.5 everywhere, with an unambiguous `search` body (a negative-lookahead gap; refused today by §11's
edge-assertion rule at the span's end, and the hit's own length stays ambiguous for `/a+/`); (B) record (5) for
REPEATED labels, §4.5 for labels set once per match, the library unambiguity check exempting repeated labels; (C)
record (5) for `search` alone (a special case). The record's own words name (B). The cost of (B) at the default
level (priority-parse counting as automaton code) is unmeasured.

## OPEN ITEMS

Questions for the owner, plain words, each with an example and a lean:

1. When a search could count its hits two ways, which wins? The rule you accepted on 11-14 says a condition on an
   ambiguous label passes if any reading of the match passes; the search you approved today counts hits the way PCRE
   finds them, left to right. Example: in `abx aby abx`, searching for `ab` + x-or-y, "exactly 3 hits" is what you
   want; under the "any reading" rule, "exactly 0 hits" would also pass, because a gap may swallow a hit. Lean (the
   record's own words): for any label inside a loop, PCRE's left-to-right reading decides; the "any reading" rule
   stays for labels set once. Its cost is unmeasured.
2. A search for something that can match nothing at all: refuse it, or copy PCRE2's find-all stepping? Example:
   searching `baa` for `a*` gives one empty hit under the definition, three results under find-all. Lean: refuse,
   with the fix "add `& !""`", the same rule we already apply to a whole program that can match empty.
3. With `~` gone, what does `d := ...` name? Example: your `d := <subject> ~ /ab(?<g>[xy])/`. Lean: bind the search
   itself (`hits := search(r)`, then `(m: hits)`); ask questions of the hits where they live (`some(...)`, counts);
   reading one hit (`$m.hit[2]`) is the captures level. The `(x, y) := ...` form you wanted for searches stays in the
   design, laid against the search pattern's named groups, one pair per hit; out of phase 1.
4. "Every hit" when there are no hits: true or false? Example: `(g: "x")` on a value with no hit at all. Lean:
   false (so "every hit is an x" also says "there is a hit"); the other meaning is written "no hit is not an x".
5. One-hit access level: is reading ONE hit's text (`$m.hit[2]`, keeping hits 1 and 3) the captures level, as I
   leaned to you, while a TEST on hit 2 (`(hit[2]: "aby")`) stays default because the 11-13 nth rule makes it a
   countdown? Lean: yes to both.
6. Two smaller ones from the interface ruling: a user label named `index` or `label` (lean: an error, those are
   the dot's reserved fields); and the 11-13 lookup table `["US" => "United States"]` would make a map as a value
   (lean: drop `=>`, use computed labels).
7. Library bodies gain `(?s)` in `contains`, `startsWith`, `endsWith`, `search` so a gap crosses a line break inside
   the value. Example: `contains("b")` on a value `a\nb`. Lean: yes; no worked example's answer moves.

Not for the owner yet (filed in the draft): the hit label's name and a short "count the hits" spelling (§13 O55;
lean: fixed `hit`, condition spelling, wait for a case); which loop a record means when its labels sit at different
depths (O56 (1); lean: the innermost loop enclosing all of them); typed parameters in the design after phase 1
(O48, no reading chosen); the run-time parameter half of O46; how a program selects a capability level (O31).
