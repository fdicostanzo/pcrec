# The joint condition: a condition over several labels at once (RULED)

STATUS: RULED, design only, no build go. The owner has answered every question put to him through 13:16, in the
COND-FAMILY entries of 2026-11-16 from 00:31 to 13:16 (CF:1336-1592; `grep -c '^\*\*2026-11-16'
docs/design/plan_row_bodies/COND-FAMILY.md` = 28, the first three, 00:06-00:09, the paused field-reference direction)
[§4F: was "has answered every question this note posed ... to 12:51 (CF:1336-1583; ... = 27"; §4E: was "to 11:35
(CF:1336-1542; ... = 24"]. The three contradictions lane jcfold reported (§8) are ANSWERED (CF 12:45, 12:48, 12:51)
[§4E]; **label-twice** is ANSWERED (CF 13:16: an error) [§4F]. STILL OPEN (§8): **tuple-parts** (§4A.3, no user;
item 4 of `docs/design/predicates_future.md`), **pairing-loop** (re-drafted by round jointcond, three parts) and
**zero-pass-empty** (NEW, round jointcond) [§4F].
Lanes: jointexp (the exploration), tupleval (§4A, the tuple as a value), tupleval2 (09:49-09:58; §4A.11), unsetdef
(§4B, the default; 10:18-10:43), jcfold (the entries of 11:05-11:35; every ruled point stated ONCE, as ruled, in §2;
the record DERIVED as the product case and checked rule by rule, §4D; what rev 20 of the draft must change, §9),
jcfold2 (the entries of 12:45-12:51; the manager's zero-pass wording tested, §4E) [§4E], jcfix (critic round
jointcond's fixes as the manager ruled them, 2026-11-16, and the owner's label-twice, CF 13:16; §4F) [§4F].
Changed sentences: §4A.10 (tupleval, tupleval2, unsetdef), §4C (jcfold), §4E (jcfold2) and §4F (jcfix). A sentence
marked "the manager's reading (round jointcond)" is the manager's ruling of a critic finding, told to the owner, not
his words [§4F]. NOT a revision of
`predicates_draft.md`: rev 19 stands as the record of the field-reference direction, which the owner PAUSED (CF
00:31: "i want to pause this direction and consider a different one that is more inline with existing concepts");
since CF 12:51 its `lex_` names, argument order and first-library slot are RETIRED and its sigil PAUSED INDEFINITELY
[§4E]. Spellings are placeholders (the owner's `(h,m): blah` is illustrative; D193 add. 4).
Section numbers `§n.m` are `predicates_draft.md` rev 19's; this note's own parts are named `§4A`, `§4B`, `§4C`, `§4D`,
"item n" (of §4) and "this note's §n"; `CF hh:mm` is the COND-FAMILY entry of 2026-11-16 at that box-clock time,
`CF:n` a line of that file. Every sentence that is a LANE'S own consequence says so; the owner's words are quoted;
a MANAGER'S reading is labelled as the manager's.

Evidence: `docs/dev/lanes/jointexp_check.py` / `.out` (run 2026-11-16 00:40; RE-RUN unchanged by lane jcfold,
`timeout 120 python3 -I`, output identical): 27,752 cases, 0 differ from the independent expectation, 0 engine
disagreements (libpcre2-8 10.46, Python 3.14.4 `re`). Tables cited as (X), (U), (L), (C), (C4), (S), (P) below.
Lane jcfold's `docs/dev/lanes/jcfold_check.py` / `.out` (same engines; `timeout 120 python3 -I
docs/dev/lanes/jcfold_check.py`): 2,019,088 cases, 0 differ, 0 engine disagreements (1,924,375 of them table (RC),
220,750 of those engine-run, the rest the rows' union checked in Python); tables (RD), (RZ), (SE), (MN), (RC), (NL);
SABOTAGED (`JCFOLD_SABOTAGE=1`: (RD) without the "m unset" guard, (SE) with `>=` for `>`): 3,825 differ, so it can
fail. Lane jcfold2's `docs/dev/lanes/jcfold2_check.py` / `.out` (same method and engines; `timeout 120 python3 -I
docs/dev/lanes/jcfold2_check.py`): 14,937 cases, 0 differ, 0 engine disagreements; tables (RZ) re-run, (ZN), (ZJ),
(ZD), (Z1); SABOTAGED (`JCFOLD2_SABOTAGE=1`: every zero-pass piece of the unfolds made vacuous): 2,444 differ [§4E];
its (ZJ-E) rows are the wording's answers COMPUTED in Python, not engine-run and not among the 14,937 [§4F].
Lane jcfix's `docs/dev/lanes/jcfix_check.py` / `.out` (same method and engines; `timeout 120 python3 -I
docs/dev/lanes/jcfix_check.py`): 164,527 cases, 0 differ, 0 engine disagreements; tables (ZE), (UP), (OP), (DM)
(the brief's letter (DD) is unsetdef's date table, so the dictionary-domain table is (DM)); every row it calls
COMPUTED is a Python comparison, not engine-run; SABOTAGED (`JCFIX_SABOTAGE=1`: every zero-pass or unreached piece of
the unfolds made vacuous): 497 differ [§4F].

## Goals

The owner's criteria (CF 2026-11-16 00:31), in his order; a conflict is won by the higher one.

| goal | who benefits | measurable form |
|---|---|---|
| G1 IN LINE WITH EXISTING CONCEPTS | every reader of a program; the owner's "few types and few operators" | the count of NEW concepts (a rule, a form, a value shape, a mark position, an error, a warning, an open item) the idea needs, against rev 19's count for the same problems, counted alike on both sides, with the existing rules each side ABSORBS (reuse): fewer new, and each named with its price (the two-sided table, §3) [§4F] |
| G2 HELPS THE LARGER LANGUAGE | authors of problems other than the tuple compare | of the NON-COMPARE problems tried (the compare is the TEST, G3; his words CF 00:31), how many get simpler, the same, worse; at least as many simpler as worse. Today: one tested non-compare problem simpler (calendar validity, E-CAL, table (C4)), one untested (multi-field allowlists, §4A.5), the rest of §12 the same, none worse; the mechanism's general gain is the label-free library SET (§2) [§4F: was "of the problems tried (§5 here)", a tally of compare instances that counted problem 4 twice (as 9)] |
| G3 THE TUPLE COMPARE AS A TEST | the language's credibility on a hard case | (a) what the language needed ONLY for the compare: J4's dictionary-order sentence, J5's two-orders pair, J8's lift (needed because `padded` gives canonical numerals; it exposed B3); (b) what the compare EXPOSED that is general: the default (J6, used by versions and optional minutes, §4B.5); with the compare's answers equal to integer dictionary order on every evidence population (0 differ) kept as the evidence [§4F: was the 0-differ bar alone] |
| G4 ONE MEANING PER MARK | readers (the owner's look-alike criterion, §0.1) | the mark census (§4 item 8 here): every new position has one meaning; every look-alike is either the same answer or a compile error |

Non-goals: the symbol choices (the spelling step's, D193 add. 4); a build; relations that need a FUNCTION of the
fields (weekday, day differences: computed labels keep them, §4.4); any-arity recursion (the built-in order serves
any number of fields, J4; first/rest is PARKED, CF 10:22, `predicates_future.md` item 1) [§4C].

Standing questions (docs/design/CLAUDE.md). (1) MEASUREMENT REGIME: not relevant; the note measures nothing (the
automaton size of a joint condition is unmeasured, like every condition's, and would be read under §13 O57's
regime). (2) INDEPENDENT CONTROL: relevant for the evidence: every expectation in `jointexp_check.py` is computed
from the subject's digits as Python integer tuples (Python's own tuple order) or by `datetime.date`, never from the
rectangle expansion under test; the script prints each population's count; the same holds for `tupleval_check.py`,
`tupleval2_check.py`, `unsetdef_check.py` and `jcfold_check.py` (expectations from the subject split by Python
string code, integer tuples, `datetime.date`, `ipaddress`), and the last three were sabotaged to show they can
fail [§4C]. (3) WHAT MOVES ON REGENERATION: not
relevant (no data file, table or stamp).

## 1. Examples first

    t := /(?<h>\d{1,2}):(?<m>\d\d)/
    t & ((h, m): padded(between((9, 0), (10, 0))))           # a time from 9:00 to 10:00
    t & ((h, m): padded(> (9, 30)))                           # strictly after 9:30: just `>`
    semver & ((major, minor, patch): >= (1, 4, 0))            # a version at least 1.4.0
    ip & ((a, b, c, d): between((10, 1, 128, 0), (10, 1, 131, 255)))
    list := /(?:(?<h>\d{1,2}):(?<m>\d\d),)*/
    list & ((h, m): padded(>= (9, 0)))                        # every time in the list: per item, no warning
    t2 := /(?<h>\d{1,2})(?::(?<m>\d\d))?/                        # minutes optional
    t2 & ((h, m = 0): padded(between((9, 30), (11, 0))))      # an absent m read as 0 (J6): 10 and 11 in, 9 out
    t & (h: padded(between(9, 17)), m: padded(<30))           # a record: the product case, ((h, m): (..., ...)) (J9)
    screen & ((w, h): (>= 640, >= 480))                       # each part on its own: the per-part form (J5)

    month_days := (padded(1 | 3 | 5 | 7 | 8 | 10 | 12), padded(between(1, 31)))
                | (padded(4 | 6 | 9 | 11),              padded(between(1, 30)))
                | (padded(2),                           padded(between(1, 28)))
    isodate & (((month, day): month_days) | (year: leap, month: padded(2), day: 29))   # a valid calendar date

Read `((h, m): R)` as "the pair (h's text, m's text) is in R". The left of `:` is a list of the operand's labels,
written where a label is always written; the right is a SET OF PAIRS. `(9, 0)` is the pair; `>= (9, 0)` the pairs
at or after it in dictionary order (first field first); `between` is the existing library macro, unchanged.

## 2. The idea in one page: ONE mechanism, as RULED

The joint condition is the ONE condition mechanism; the single-label entry is its one-label case and the record its
product case (RULED, **record-is-product**, CF 11:35: "record-is-product: absolutely. This is precisely the sort of
simplifying semantics I'm looking for."). Each rule is stated ONCE, here, with the owner's words; the sections after
it work it out and cite it as J1-J9.

- J1 THE FORM. A condition entry is `(p1, ..., pk): R`: the whole matches whose labels p1..pk have texts
  (t1, ..., tk), the TUPLE, in R, a set of k-tuples of strings. k = 1 is today's `p: S` (one-entry parentheses are
  grouping, `((h): S)` = `(h: S)`, §4A.2). It stands where a condition entry stands, inside a record:
  `P & ((h, m): R)`. The owner's idea (CF 00:31): "what if we could define a syntax that applied multiple labels in
  conditionals at the same time. like (h,m): blah". A MIXED RECORD, a joint entry beside other entries
  (`isodate & (year: leap, (month, day): month_days)`), is LEGAL and is the `&` of its entries, the draft's "all of
  several conditions = one record" (§4.1 :1546, D3); a label named in two of its entries is the label-twice ERROR
  (RULED, **label-twice**, CF 13:16, his words: "label-twice: agree an error. And that means it's also unofficially
  parked in case some other meaning becomes valuable"; the record: "a label named twice in one condition is a
  COMPILE ERROR in both forms (the record being the product case)"). Legal-and-`&` is the manager's reading (round
  jointcond, MIXED-RECORD), told to the owner [§4F].
- J2 THE COLON'S SCOPE (RULED, **colon-scope**, CF 11:32: "colon-scope: yes with refinement: (a, b = c): ... the 'c'
  is a binding et al"; his statement, CF 09:47: "In my mind (x, y) is different than (x,y): because the colon").
  LEFT of the colon a name is always a LABEL of the intersected pattern, computed labels included (§4.4), found by
  §4.1's chain lookup with its ambiguity and unknown-label errors; never a plain binding. On the VALUE side (right of
  the colon, inside any colon-less tuple, an argument, the right of `:=`) a bare name is always a BINDING (or a
  literal: his "et al"), and a label's value is read `$x`. THE REFINEMENT: a default written after `=` left of the
  colon (`c` in `(a, b = c): ...`) is on the VALUE side although it stands left of the colon.
- J3 THE VALUE (**tuple-value**, CF 09:42: "I am ok with the tuple as a value"; **tuple-anywhere**, CF 09:49: "You
  could use them as you say"; **set-arity**, CF 10:26: "Set arity: yes. It's clean. I like it"). A colon-less
  `( e1, ..., ek )`, k >= 2, in value position is a TUPLE SET, the product of its entries, used wherever a value is
  used. Every SET (every rx-kind value) carries an ARITY fixed at compile time; macros are values as today (CF:858)
  [§4F: was "Every value is a SET of tuples", RULING-5]; today's rx are the arity-1 sets; `|`,
  `&` and array entries need equal arity; the labels left of the colon number the set's arity; only an arity-1 set
  has text. The definition: §4A.4.
- J4 THE ORDER (**first-rest** PARKED, CF 10:22: "Let's park first/rest but keep it in the wings in case we find a
  problem that needs a different way of composing"; after CF 10:18: "I think the tuple mechanism as otherwise
  described handled the problem more simply which I like"). A comparison set takes a tuple atom: `>= (9, 0)` is the
  k-tuples at or after (9, 0) in DICTIONARY order (first part first), each part read by its own literal (§2.4 per
  part). EVERY component of the tuple is read through its literal's domain (canonical numerals for a numeral), the
  components after the deciding one included: `t & ((h, m): >= (9, 0))` REJECTS `10:00` (m = `00` is no canonical
  numeral), which `padded(...)` admits (the manager's reading (round jointcond, DICT-DOMAIN): the DOM reading, the one
  every evidence script checks, keeping §2.4's per-literal reading and C9; SQL and Python tuples read the other way,
  later components unconstrained; table (DM): 900 of 11,000 `t` subjects differ unpadded, 0 padded) [§4F]. A `$`
  component (`> ($sh, $sm)`) has no literal: it is read by its VALUE, leading zeros ignored (`09` is 9), rev 18's LEAN
  (`predicates_draft.md:2554-2563`, "LEAN until O27 is ruled"), which rev 20 carries into the comparison-set text
  (§9 row 10) [§4F, DOLLAR-COMPONENT]. `between(lo, hi) := >=lo & <=hi` serves any k, unchanged. First/rest:
  `predicates_future.md` item 1.
- J5 BOTH ORDERS ARE LEGAL (RULED, **two-orders**, CF 11:20: "I agree. They look sufficiently different to me and I
  like the control."). An operator OUTSIDE the bracket compares the whole tuple (`>= (9, 30)`, dictionary order);
  INSIDE, each part on its own (`(>= 9, >= 30)`, a product). NO WARNING: THE MANAGER'S reading of "sufficiently
  different" (CF 11:20, told to him; not his words), tested in item 4.
- J6 UNSET LABELS AND DEFAULTS (RULED, **unset-component**, CF 11:05: "unset-component: yes"; **default-unused**,
  CF 11:05: "default-unused: agree"; the mark, CF 10:37: "Seeing = in examples I prefer it"; **default-set**, CF
  10:43: "We can punt, as you say, and throw an error"). A condition, single or joint, naming a label that is UNSET
  in a match FAILS for that match, unless the author wrote a DEFAULT for that label, `(h, m = 0): R`: then the
  default's text is read in the label's place. A default is ONE string; a default of several strings is a compile
  ERROR, for now. A default that can never change an answer draws a WARNING, `default.unused` (WARNING is THE
  MANAGER'S reading of "agree", CF 11:05: he agreed with the question's lean). Rev 18's decided-prefix reading is
  WITHDRAWN (CF 11:05, the record). Worked: §4B.
- J7 LOOPS (RULED, **joint-loops**, CF 11:17: "I agree. Makes sense."). The tuples are paired per PASS of the
  innermost loop enclosing the named labels, a label outside that loop having its one value on every pass; the
  condition holds when every pass's tuple is in R. ZERO PASSES (RULED, **zero-pass-record**, CF 12:45:
  "zero-pass-record: I agree but save the notes in the future file. The issue falls into the 'saving people from
  themselves' category that tools need to realistically consider"): a label outside the pairing loop is tested once
  even when the loop runs zero passes; `/(?<k>\d)(?:;(?<h>\d))*/ & (h: <5, k: 3 | 4 | 5 | 6 | 7)` on `9` FAILS; the
  draft's `(a: S, b: T)` = `(a: S) & (b: T)` holds at every depth. THE MANAGER'S WORDING (CF 12:45 record,
  CF:1553-1557, VERBATIM; not the owner's words; tested in §4E): "a reached loop that runs zero times gives ONE tuple
  whose looped parts are EMPTY; empty satisfies any set (for a joint set R: the outside labels' values must be
  possible under R for some value of the looped parts); a default is NOT read there (§4B.1 unchanged); a plain
  single-label condition still HOLDS on zero passes (CF:997-1000 unchanged); "unset" (never reached) keeps its
  meaning." [§4F: was quoted with "for a joint set R THAT IS NOT A PRODUCT" as a separate clause and without
  "(CF:997-1000 unchanged)", RULING-1; §4E: was "(zero passes of a reached loop: holds, §4.2)"] LANE jcfold2's
  REPAIR (not the manager's words): the product clause ("empty satisfies any set", the outside parts tested on their
  own) for a product, the projection for any other set; it keeps the `&` equality and makes the answer on an EMPTY
  set depend on its spelling (§4E corner 1); the record's own unsplit wording makes both spellings FAIL and breaks the
  `&` equality there. With the draft's narrowing-site error (`predicates_draft.md:1941-1942`, §5.2, LEAN) the CONSTANT
  empty spellings are compile errors; what remains (an R empty only through a match value) and the DOMAIN of "some
  value" are the open owner question **zero-pass-empty** (§8) [§4F]. THE ZERO-PASS TUPLE AND THE GROUP QUESTIONS:
  it is tested by the plain condition and by `all`; it is never counted by `some`, `count` or `occurs` (the manager's
  reading (round jointcond, GROUP-ZERO); it keeps `predicates_draft.md:1600-1602` and :1659-1661) [§4F]. "NEVER
  REACHED" is §4.2's: the deepest construct the match entered on the way to the label is not a loop that ran zero
  times (`predicates_draft.md:1598-1605`); a label in an inner loop whose OUTER loop ran zero passes has ZERO passes,
  not unset [§4F, SIM-2]. A pass of an enclosing loop that never reaches the pairing loop is not stated by any
  ruling: open, **pairing-loop** part (3), §8 [§4F]. Labels in SIBLING loops: a COMPILE ERROR naming the fix. The looped warning (CF 00:09: "looped-compare: warn") MOVES onto a
  hand-written `|` of conditions whose labels can repeat; the joint condition draws none. The ruled words read
  literally leave the nested case unstated; the lane's precise statement and both texts: item 5.
- J8 MODIFIERS (RULED, **modifier-lift**, CF 11:27: "modifier-lift: yes. ... However the form is 'do everything to
  both' so the logic makes sense"). A modifier around a set of tuples (`padded(...)`) acts on EVERY part. A per-part
  modifier is not designed: `predicates_future.md` item 2. WHICH MACROS LIFT: a macro whose result DISTRIBUTES over
  `|` in its argument (f(A | B) = f(A) | f(B), checkable from its body: every body that only lays its argument in an
  rx hole, as `padded(rx) := /0*${rx}/` does, CF:1113) applied to a k-ary set R is the union over R's tuples of
  f(t1) x ... x f(tk); a user's `zp(x) := /0*${x}/` lifts exactly as `padded` does; a macro that does not distribute
  (a body with `!x`, or `x` used twice) stays the arity error "a tuple where an arity-1 set is required". The law is
  "an array of X is an X" applied to a macro's argument (the manager's reading (round jointcond, OWNER-5) of "do
  everything to both", CF 11:27; told to the owner; it replaces the word "modifier", a glossary word the compiler
  cannot see) [§4F].
- J9 THE RECORD IS THE PRODUCT CASE (RULED, CF 11:35). `(h: S, m: T)` is DEFINED as `((h, m): (S, T))`; with a
  default, `(h: S, m = 0: T)` as `((h, m = 0): (S, T))` (the record-with-default SPELLING is §4B.1's, lane unsetdef's,
  ruled by reference at 11:05, whose unset-component question pointed at §4B; the 11:35 record shows only
  `(h: S, m: T)`; the equation follows from J9 by definition) [§4F: was cited to 11:35 alone, RULING-6]. A record
  holding a joint entry: J1 (MIXED-RECORD) [§4F]. Every rule above holds for the record by definition. §4D
  checks the draft's record rules one by one: with J7's zero-pass sentence (CF 12:45) all follow [§4E: was "all but
  one follow; the one that does not (labels at different depths, zero passes) is a CONTRADICTION (§8), table
  (RZ)"]; table (RZ) re-run under the ruled rule: 0 of 1,110 differ from the `&` reading.

LEVEL (the lane's, engine-checked). With constant bounds the SET of every joint condition is a FINITE UNION OF
PRODUCTS of per-label constant sets (each component in its literal's domain, J4); for set-once labels the CONDITION
is the `|` of the rows as single-label condition records; for looped labels the union is taken per pass INSIDE the
pairing loop's item, not as a `|` of records over the whole match (that `|` is the moved-warning look-alike: 56 of
1,100 differ with passes, `3;5;6`, jcfold2's (ZJ)): default level, automaton code (§6.1) [§4F: was "i.e. a `|` of
single-label condition records", SIM-4]. `>= (b1, ..., bk)` is k products (table (X): 24,420 cases). `between(lo, hi)` is at most 2k - 1 products after
merging the shared prefix (table (RC): k = 2, 3, 4 over 5,491 bound pairs, the maximum 2k - 1 reached and never
exceeded, answers 0 differ). Bounds from the same match (`> ($sh, $sm)`) are a §4.6 relation, priced by class count
(table (SE): 168 classes, 13,328 cases, 0 differ). A default slices the set at its text (§4B.2).

What it costs, each NEW: (N1) the tuple set as a value (J3); (N2) an arity on sets (J3); (N3) a tuple of label
references left of `:` (J1); (N4) a modifier on a tuple set acts on every part (J8); (N5) a default at a label,
`name = v` left of `:` (J6); and one sentence of §2.4, the dictionary order for a tuple atom (J4). What it gains: the
field-reference machinery of rev 19 has no job left (item 9); a LIBRARY can provide a constraint over several fields
WITHOUT knowing their names (`office_hours := padded(between((9, 0), (17, 0)))`, then `P & ((h, m): office_hours)`):
the author names the labels in the one place labels are always named; and the record carries no rules of its own.

## 3. What is new and what is reused

| concept | existing rule it reuses | what is new (ruling) | what of rev 19 it replaces |
|---|---|---|---|
| left `(p1, ..., pk)` | the left of `:` is a label path (§4.1); the chain lookup and its errors (§4.1) | a TUPLE OF REFERENCES left of `:` (N3; J1, J2 colon-scope 11:32). Errors: a label twice on the left (RULED, label-twice, CF 13:16 [§4F]), a nested tuple | the other-side sigil `^h` (§5.4 `^` row), arrays of references `[^h, ^m]`, §4.1's ONE EXCEPTION (a parameter on the left of `:`) |
| the tuple `(9, 0)` | literals are one-string rx (§2.1); "a record is never a value" untouched (§4A.1) | the TUPLE SET as a value (N1; J3, tuple-value 09:42, tuple-anywhere 09:49) | bounds as arrays read by index (`lo[1]`, §3.2 tool 1); the wrong-length gap (§13 O72) becomes an arity error |
| a set of tuples | rx kind and `& \| !` extensional (§2.1, §2.2); "an array of X is an X" (CF 2026-11-14 00:10, 11-16 00:08) | an ARITY on sets (N2; J3, set-arity 10:26): arity 1 is today's rx; mixing arities is an error | nothing in rev 19 (it had no set of tuples) |
| tuple comparison sets `>= (9, 0)` | unary comparison sets, one atom, the literal decides (§2.4) | dictionary order for a tuple atom (J4, first-rest parked 10:22); the per-part form `(>= 9, >= 0)` stays legal (J5, two-orders 11:20) | the six names `lex_ge2` .. `lex_between3` and their bodies (§8); the any-n recursion `lg` (§8, O69 (3)); the strict spelling `lex_ge2 & !lex_le2` (just `>`) |
| `between`, `\|`, `&` on tuple sets | `between(lo, hi)` inclusive (§2.4); macro bodies over parameters as atoms (§2.4 LEAN) | nothing (arity follows the arguments) | `lex_between2`, `lex_between3` |
| `padded` on a set of tuples | `padded(rx) := /0*${rx}/` (CF:1113) | every part padded (N4; J8, modifier-lift 11:27) | rev 19's per-entry `padded(...)` in the bodies |
| unset fields | §4.2: a condition naming an unset label fails | the same rule for k labels; an author-written DEFAULT at the label (N5; J6, unset-component 11:05, `=` 10:37, one string 10:43, `default.unused` 11:05) | the DECIDED-PREFIX order (§8 caveat (5)), WITHDRAWN (CF 11:05): answers CHANGE (item 6) |
| looped fields | §4.3 sequence rule; SAME ITERATION BY RECORD; §13 O56 | per-pass pairing; sibling loops an ERROR; the looped warning moved onto a `\|` of conditions (J7, joint-loops 11:17) | `compare.looped` as rev 19 defined it (a compare's field can repeat): its subject is gone; the warning keeps its ruling on a new subject (item 5) |
| relations `(b: >$a)` | §4.6 (class-count pricing), `$x` values (§5.4) | nothing: a tuple of `$` values is a product of one-string sets, `> ($sh, $sm)` (table (SE)) | `lex_ge2([^b1, ^b2], [$a1, $a2])` |
| computed labels on the left | §4.4 (a computed label is constrained like a label) | nothing (J2: "computed labels included") | `[^year, ^mnum]` |
| the record `(h: S, m: T)` | ruled (CF:255, CF 2026-11-14 01:00) | DEFINED as the product case (J9, record-is-product 11:35) | — |
| group questions `some`, `count` over tuples | §4.3 (a record = one iteration) | nothing: `count(((h, m): R))` counts the passes whose pair is in R | — |

Counted: rev 19 needed, for the same problems, the sigil (a new mark), arrays of references (a new kind of entry),
§4.1's exception (a rule change), the index on reference arrays (open O75), the bound-call binding (open O76), the
wrong-length mechanism (open O72), six library names, a recursion form waiting on two features, two warnings. The
joint condition needs N1-N5 and one sentence of §2.4, each now ruled.

COUNTED ALIKE (G1's measurable form; [§4F, OWNER-1]: the paragraph above charges rev 19 with its warnings and open
items and the joint condition with N1-N5 only). Each side, for the same problems, by the same columns; the lane's
count, every entry cited in this note:

| column | rev 19 (the field-reference direction) | the joint condition |
|---|---|---|
| new value shape | none (arrays of references are entries, not a shape) | the tuple set (N1) and arity on sets (N2) |
| new form or mark position | the sigil `^h` (a new mark), arrays of references, the bound call | the reference tuple left of `:` (N3), the default `name = v` (N5), the tuple atom of a comparison (one sentence of §2.4) |
| new rule | §4.1's ONE EXCEPTION; the decided-prefix order; the index on reference arrays | the lift by distribution (J8, N4); per-pass pairing at different depths (J7, item 5); the zero-pass EMPTY part, a third absence state beside "unset" and "a value" (J7); a default read when a loop is never reached, not on zero passes (§4B.1) |
| new compile errors | the wrong length (open O72, unbuilt) | arity mismatch, sibling loops, label twice, nested tuple, `(h, m: 0)`, `(h: 10, m = 0)`, a `$x` default that can be absent, a several-string default, a bare label as a default, a `$` tuple over repeated labels, a bound match-dependent tuple (4A.4): 11 |
| new warnings | `compare.looped`, `compare.repeated` (proposed) | `default.unused`; the moved looped warning (no new count); the proposed `label.both_sides` (not ruled, §4B.4) |
| open items | O72, O75, O76 (and O71's spelling) | **tuple-parts**, **pairing-loop**, **zero-pass-empty** |
| library names | six `lex_` names and a recursion form waiting on two features | none |
| existing rules ABSORBED (reuse) | none: the record keeps its own rules | the record's 25 rules follow from J1-J8 (§4D, D1-D25), stated once; `between`, `\|`, `&`, `[ ]`, `!`, `$`, `padded`, the group questions unchanged (§3 table) |

Read: the joint condition adds more ERRORS (each a slip caught at compile time, the "saving people from themselves"
of CF 12:45) and three absence rules; rev 19 adds a mark, an exception and six names, and leaves its record rules
separate. Fewer NEW CONCEPTS of the value/form/mark/rule kinds on the joint side once the record's 25 absorbed rules
count; more errors. The owner weighs errors; the table does not decide G1 for him (the lane's).

## 4. The hand-waving, item by item

### Item 1. What IS the left side `(h, m)`?

The existing condition grammar, extended in ONE place: an entry's left was "a label path"; it becomes "a label path,
or a parenthesised list of two or more label paths", in the owner's terms a TUPLE OF REFERENCES to the intersected
pattern's labels, the colon its mark (CF 09:47: "tuples need a left hand side with colon which mean the symbols are
scoped references to the intersected labels"). Its scope is RULED (J2, colon-scope, CF 11:32): every name in it is a
LABEL of the intersected pattern, computed labels included, never a plain binding; only a default after `=` is on
the value side. Nothing on it is a value and nothing is passed. The nearest existing sibling is the record on the
LEFT of `:=` (`(x, y) := ...`, design only): there names are laid against a result's groups; here paths are laid
against the operand's labels (lane's observation) [§4C].

- Paths nest: `((d.year, d.month): ...)` reads two fields of the label `d` (§5.4 `.` row, unchanged).
- Computed labels: `((year, mnum): ...)` with `mnum := $mname.index` (§4.4); the lookup is §4.4's (and its open
  O19 when the computed label's labels occur in several operands), unchanged.
- Labels from both sides of a chain: `P & Q & ((h, k): R)` with h in P and k in Q is allowed, as `(h: S, k: T)` is
  today (§4.1: the chain is flattened, both operands match the same stretch whole, each label read in its operand's
  parse). A label in both: the ambiguity error, as today.
- A label twice, `((h, h): R)`: a compile error at the condition ("h named twice"), no library insight needed (rev
  18-19's `compare.repeated` gap, §0.1 L75, closes; lane's). LANE'S CONSEQUENCE of J9 [§4C]: the record `(h: <5, h:
  >2)` is by definition `((h, h): (<5, >2))`, so the same rule makes it an error, where the draft's "all of several
  conditions = one record" (§4.1, `predicates_draft.md:1546`) reads it as `(h: <5) & (h: >2)`. The draft has no
  sentence on a label twice in one record (`grep -n 'label twice\|named twice' predicates_draft.md`: only the
  projection's L75 and DECIDED (58)), so this is not a contradiction; the alternative that keeps both forms legal is
  the DIAGONAL reading, `((h, h): R)` = {t : (t, t) in R}, which for a product is t in S & T. RULED (**label-twice**,
  CF 13:16, his words: "label-twice: agree an error. And that means it's also unofficially parked in case some other
  meaning becomes valuable"): a COMPILE ERROR in both forms, the message naming the fix ("h is named twice; for two
  tests on one label write `(h: <5 & >2)`", illustrative, D26); the diagonal is not adopted; the spelling stays FREE
  for a later meaning (`predicates_future.md` item 9) [§4F: was "Open item **label-twice** (§8)"].
- A nested tuple `((h, (m, s)): R)`: an error (no case needs it; D77).
- The shadowing ruling (CF:1268-1282: "it might shadow a binding and it wouldn't be clear where it was coming
  from"): it was about a compared field in an ARGUMENT position. On the left of `:` a name is always the operand's
  label (RULED, J2), so a binding of the same name is not in play and the reader sees where the field comes from:
  the condition's operand, as for `(h: S)`. On the value side the ruling's other half holds: a bare `h` is a
  binding, the label's value is `$h` [§4C].
- SPELLING NOTE: as an entry of a record it is written `P & ((h, m): R)`; `P & (h, m): R` is §4.1's "`:` outside a
  record" error, and `(h, m: R)` is a record whose first entry `h` has no `:` (an error naming the double
  parentheses). Heavy but each form has one reading.

### Item 2. What IS a tuple of values?

Options weighed, least new first:

(a) A RECORD OF BOUNDS BY LABEL, `between((h: 9, m: 0), (h: 10, m: 0))`: REJECTED. A labelled record in value
position already MEANS something: a condition, a macro (§5.4 `( label: S, ... )` row, CF:858). So the argument
would be "the matches whose h is 9 and m is 0", and `between` of two conditions has no meaning. It also repeats the
labels three times. It looks like reuse and is a look-alike (G4).

(b) THE BOUND AS TEXT, PARSED BY THE AUTHOR'S PATTERN, `((h, m): between("9:00", "10:00"))`: POSSIBLE BUT NOT
RECOMMENDED. It reuses literals and the author's pattern, and needs no tuple value, but the meaning of a string on
the right of `:` then depends on the OPERAND (the bound is parsed by the other side of the `&`), which no set has
today (sets are context-free, §11); the bound's own parse can be ambiguous or leave a label unset; and the set
cannot be bound or provided by a library apart from a pattern, which loses G2's main gain.

(c) AN ARRAY `[9, 0]`: IMPOSSIBLE under the owner's rulings. An array is a labelled ALTERNATION (CF 2026-11-14
00:10) and an array of X is an X (CF 2026-11-16 00:08): `[9, 0]` is "9 or 0". Reading it in order inside a
comparison would give `>=` two meanings by context. Under the arity rule (N2) the slip `((h, m): >= [9, 0])` is a
compile ERROR (a set of arity 1 on a 2-ary left), with the hint "write `(9, 0)`" (lane's).

(d) THE TUPLE, `(9, 0)`: ADOPTED (J3; tuple-value, CF 09:42: "I am ok with the tuple as a value"; the value is a SET
of tuples, §4A.4) [§4C]. The exploration's text follows, kept as the record of the reasoning. A positional `( e1, ..., ek )` in value position, k >= 2, denotes the
product of its entries; with one-string entries that is ONE tuple. This needs nothing beyond sets: a "tuple of
values" is not a new value shape, it is a product of one-string sets, and products are what records already do to
labels (the record `(h: S, m: T)` admits exactly the product S x T on (h, m), table (P)). NOTE on table (U): its
rectangle regex is laid over the full `h:m:s` layout, so it checks the expansion's answers on present seconds; the
"absent seconds -> no tuple" answers in its listing are the lift rule's expectation, computed in Python, not an
engine run. Its price is the
ruling it meets: "A RECORD is NOT a value: it cannot be bound, stored or returned" (CF:851-852, RULED). Two readings:
the product IS a record in value position (then the ruling must move), or a product is a different thing that
shares the bracket (a SET, made by `( , )` the way `[ , ]` makes an alternation; a record is a shape laid against
fields, a product is laid against nothing). The lane leans to the second: it is the owner's own record-vs-value line
(CF:846 (4): "a record is a third view on a regex but an abstract one") kept intact, and the reason the earlier
"record of rx = sequence" closure was NOT adopted ("it reverses the no-concatenation lean and loses boundaries,
`(1, 40)` vs `(14, 0)`", CF:846 (4)) does not apply: a product keeps its components apart. SETTLED by the owner's
acceptance (CF 09:42) and §4A.1 (the second reading: the ruling untouched) [§4C].

### Item 3. What IS a set of tuples, and which set-forming things extend to it?

A set of k-tuples of strings. Two framings with one answer set: an ARITY on the existing rx kind (arity 1 = today's
rx; the kind count stays two, §2.1) or a third value kind. RULED, ARITY (J3; CF 10:26: "Set arity: yes. It's clean. I
like it"): every
operator keeps its one meaning, and every existing error shape covers the new misuse ("a set of pairs has no target;
write `P & ((h, m): ...)`" for `P & (9, 0)`, `${(9, 0)}`; mixed arity in an array as §3.5's mixed-kind error).

| set-former | on a set of k-tuples | status |
|---|---|---|
| `\|`, `&` | union, intersection (same arity) | reused, extensional |
| `[e1, e2]` | any one entry: `[(9, 0), (17, 30)]` = the two pairs | reused ("an array of X is an X") |
| `<` `<=` `>` `>=` `==` with a tuple atom | dictionary order, each component by its literal (item 4) | NEW order on a new atom; one sentence |
| `between(lo, hi)` | `>=lo & <=hi` | reused, unchanged |
| `padded(S)` | every component padded (N4) | RULED, J8 (modifier-lift, CF 11:27); a per-part modifier is parked, §6 B3 |
| `any_case`, `quoted` and other modifiers | the same: every component | RULED, J8 ("do everything to both") |
| a macro returning a set | returns a set of tuples (`office_hours := ...`, `shift(n) := ...`) | reused (a binding names whatever its expression is, §2.1) |
| `enumerate` | not extended (no case) | — |
| prefix `!` | complement in the filter role, as for a single label | reused; inherits §13 O28 |

`!` AND UNSET OR NON-NUMERIC FIELDS: exactly the single-label rules, one level up. `!((h, m): R)` is a macro (§2.2)
that is TRUE on a match whose pair does not exist (a label unset) or is not in R; `((h, m): !R)` names the labels, so
an unset label makes it FAIL (§4.2's "a condition naming an unset label fails"). Those two disagree on an unset label
exactly as `!(x: S)` and `(x: !S)` do today (§0.1 L30, §13 O28, OPEN): nothing new, and nothing settled. What
CHANGES is that no common question needs `!` any more: STRICT is `>` (table (S): with the minutes optional, the
joint `> (9, 30)` rejects `9` and `10`, where rev 16-17's `P & !lex_le2` accepted `9` as "strictly above" and below at
once; review r17 F1's bug class has no spelling left in the compare). A non-numeric component (`ab` where a numeral
is compared) makes the tuple exist but lie outside every numeric comparison set, so `(h, m): >= (9, 0)` fails, and
`!` of it holds: §2.2's `!<200` vs `>=200` note, lifted, unchanged.

### Item 4. Dictionary order and the per-part form

THE order of a tuple comparison set is DICTIONARY order, built into the comparison set (J4: the owner preferred the
built-in mechanism, CF 10:18, and parked first/rest, CF 10:22); it is what the time, version, IP and date problems
all mean, and the SQL row-value comparison `(a, b) > (1, 2)` means the same. The other natural order, the PRODUCT
order (every component at least its bound), is the product `(>= 9, >= 0)`. BOTH ARE LEGAL (RULED, J5, two-orders,
CF 11:20: "I agree. They look sufficiently different to me and I like the control."): the operator OUTSIDE the
bracket compares the whole tuple, INSIDE it compares one part. On the `t` population, PADDED (`padded(>= (9, 30))`
vs `padded((>= 9, >= 30))`), they differ on 2,700 of 11,000 subjects (table (O); `10:00` is at or after 9:30 but its
minutes are not at least 30) [§4C]; unpadded they differ on 1,800 under the DOM reading (J4), where `10:00` is in
neither set (table (DM)) [§4F: was cited for the unpadded spellings, SIM-3].

USES OF THE PER-PART FORM (his question, CF 11:20: "Can you think of a use for the second form?"; the manager's
answer in the session reply, worked here by the lane):

    screen & ((w, h): (>= 640, >= 480))                          # a minimum width AND a minimum height
    point & ((x, y): (between(0, 1919), between(0, 1079)))      # inside a bounding box
    rgb & ((r, g, b): (>= 200, <= 60, <= 60))                   # a colour threshold: "reddish"
    slot & ((day, hour): (between(1, 5), between(9, 16)))       # a schedule slot: a weekday AND office hours
    md & ((month, day): (2, >= 4))                              # February, from the 4th on: one part fixed

In each, the parts are INDEPENDENT measurements, so dictionary order would be wrong: `between((1, 9), (5, 16))`
admits Monday 20:00 ((1, 20) is at or after (1, 9) and before (5, 16)), which the slot excludes. The last row is the one place the two forms meet: with the first part pinned to one value,
`(2, >= 4)` and `>= (2, 4) & <= (2, 99)` hold the same pairs.

THE MANAGER'S READING "no warning" (CF 11:20, not his words), TESTED: HOLDS. The withdrawn lean (warn when every
part is a same-direction comparison) fires on the first row above, a legitimate use, and the compiler cannot tell
hierarchical fields (hours and minutes) from independent ones (width and height): the pattern carries no such fact.
INCOMPLETE in one respect: the slip it would have caught, `(>= 9, >= 30)` written for "at or after 9:30", stays
silent; the draft's look-alike table carries it as a BY DESIGN row, told once by the bracket's meaning (§9 here,
the §0.1 rows) [§4C].

- Mixed component kinds: each component's comparison is read by ITS literal (§2.4 per component): `>= (2024, "M")`
  compares the first as an integer and the second as a string. A month NAME is not ordered by its string ("Apr" <
  "Jan"); the route is a computed label (`mnum := $mname.index`, §4.4) on the left, `((year, mnum): ...)`, as rev
  18-19's caveat (4) already said.
- Leading zeros: the comparison set holds CANONICAL numerals per component (§2.4, C9 RULED and confirmed CF:774), so
  `t & ((h, m): >= (9, 0))` REJECTS `9:00` (m = "00" is not canonical) exactly as `/\d\d/ & between(1, 12)` rejects
  `01`, and REJECTS `10:00` too, every component being read through its domain (J4, DOM) [§4F]. `padded(...)` around
  the set is the fix, per component (N4). Evidence (X) uses the padded reading in every component: 0 differ.
- A bound literal with a leading zero, `(09, 00)`: §2.4's "unless the literal has them" per component, the question
  rev 18 answered by a LEAN (bound read by value) and §13 O27 holds open: inherited, not settled here.

### Item 5. Loops and repetition

RULED (J7, joint-loops, CF 11:17: "I agree. Makes sense."), all three parts as asked: per-pass pairing; sibling
loops a compile error; the looped warning moved onto a hand-written `|` [§4C].

- SAME LOOP ITEM: `list & ((h, m): padded(>= (9, 0)))` pairs h and m per pass and holds when every pass's pair is in
  the set: table (L), at bound (9, 30): the joint condition accepts `10:00,9:30,`, `10:15,9:45,`, `10:45,9:35,`,
  which rev 19's per-label reading (the sequence rule over an alternation of records) rejects; 3 of 10 subjects
  differ; the joint answer is "every time is at least 9:30". §4.3's SAME ITERATION BY RECORD is this rule's product
  case (J9).
- THE PAIRING LOOP, stated precisely (the lane's, [§4C]). The ruled words are "the innermost loop enclosing every named
  label, a label outside that loop having its one value on every pass" (CF 11:17, the record). Read literally the two
  halves pull apart: with h in a loop and k outside every loop, no loop encloses both, yet "a label outside that
  loop" is exactly k; and with k in an inner loop nested inside h's loop's item, the loop enclosing both is h's, in
  whose pass k has several values. The statement both cases need: the pairing loop is the DEEPEST loop that encloses
  any named label; every other named label must lie either inside the same pass of it or outside it, and then has
  ONE value per pass (it is set once per pass of the pairing loop); otherwise (the labels' loops do not nest in one
  chain) it is the sibling-loop error. This matches §13 O56's lean (g inside the loop, k outside) and every case the
  ruling names; table (NL) runs the nested case (h in the outer item, k in an inner loop, `((h, k): >= (5, 3))`): 73
  subjects, 0 differ [§4E: "an outer pass with no k pairs nothing and holds" is WITHDRAWN by the zero-pass ruling:
  the inner loop reached in that pass and run zero times gives one tuple (h, EMPTY), and h must be possible under R;
  10 of (NL)'s 73 answers move (table (ZN), `4:;` held, now FAILS: no k makes (4, k) >= (5, 3))]. Open item
  **pairing-loop** (§8), RE-DRAFTED by round jointcond in three parts: (1) the wording above; (2) zero passes read
  PER REACH, which moves 10 of (NL)'s 73 answers (so "no answer changes" no longer holds); (3) a pass of an
  enclosing loop that never REACHES the pairing loop, which no ruling states (table (UP)) [§4F: was "a wording
  confirmation, no answer changes on any case the owner was shown"].
- ZERO PASSES (RULED, J7, CF 12:45, "zero-pass-record: I agree ..."; the wording the MANAGER'S, quoted verbatim in J7)
  [§4E]. A reached loop that runs zero times gives ONE tuple whose looped parts are EMPTY; empty satisfies any set
  (for a joint set R: the outside labels' values must be possible under R for some value of the looped parts) [§4F:
  was split into a product clause and a "not a product" clause, which is lane jcfold2's repair, J7; the domain of
  "some value" and an R empty through a match value are **zero-pass-empty**, §8]. So a label outside the pairing loop
  is tested once on zero passes: `/(?<k>\d)(?:;(?<h>\d))*/ & (h: <5, k: 3 | 4
  | 5 | 6 | 7)` on `9` FAILS, as `(h: <5) & (k: 3 | 4 | 5 | 6 | 7)` does (table (RZ) re-run: 0 of 1,110 differ). The
  rule applies to EVERY reach of a loop, so in the nested case it applies per outer pass to the inner loop too
  (table (ZN): 2,526 subjects, 0 differ from the `&` reading). Tested and the corners it leaves: §4E.
- SIBLING LOOPS: a COMPILE ERROR (RULED). Text (wording illustrative, D26): "h and k sit in different loops
  (`(?:(?<h>\d),)*` and `(?:(?<k>\d),)*`): no pass pairs one h with one k. Write one condition per loop,
  `P & (h: S) & (k: T)`, or ask a group question, `some((h: ...))`, `count(...)`." Smallest example: `/(?:(?<h>\d),)*;
  (?:(?<k>\d),)*/ & ((h, k): R)` (§6 B4). The cross product (every h with every k) is not offered.
- THE LOOPED WARNING, MOVED (RULED). Its subject is now a `|` of conditions written by hand whose labels can repeat:
  `list & ((h: >9) | (h: 9, m: >=30))` over looped h, m. Each alternative is checked over every pass (the sequence
  rule), so the `|` picks ONE alternative for the whole list, not one per item. Text (illustrative): "h and m can
  repeat (the loop `(?:...,)*`): each alternative of this `|` must hold on EVERY pass, so it is not a per-item test;
  for one, write the joint condition `((h, m): R)`." It keys off the SHAPE (a `|` of conditions naming labels that
  can repeat), never a library name, like the anchor warning (CF:1103). The joint condition itself draws no such
  warning (CF 11:17, the record). The warning's name: rev 19's `compare.looped` names the gone subject; the name is
  the spelling step's (the lane's suggestion: `alt.looped`).
- THE SINGLE-LABEL SEQUENCE RULE (§4.2, §4.3) is the k = 1 case, so nothing it says is contradicted: `(x: S)` =
  "every pass's 1-tuple in S".
- A REFERENCE MODEL (critic OWNER-7, round jointcond; NOTED, framing only, no answer changes) [§4F]. A match is a
  TABLE of passes: the passes of the pairing loop are its ROWS; a label set once outside the loop is a column constant
  over the rows (the parent row, as in a join); `((p1, ..., pk): R)` selects the rows whose tuple is in R; the plain
  condition asks that ALL rows qualify, `some`/`count` are the other quantifiers (§4.3). The record is a product
  predicate (J9); sibling loops are two tables with no join key (the error); zero passes are a parent row with no
  child rows, SQL's LEFT JOIN with NULL, where `ALL` over zero rows is true and the parent's columns are still tested
  (J7, CF 12:45). Rev 20's §4.3 may use it. Two unlocks it names are NOT filed as future items (the manager's
  disposition): sibling loops paired by position, and a predicate over successive rows.

### Item 6. Optional and non-numeric fields

- A label UNSET in a match (an optional group skipped, an alternative not taken): no tuple exists, the condition
  FAILS, unless the author wrote a default for that label (RULED, J6, unset-component, CF 11:05: "unset-component:
  yes") [§4C]. Table (U), seconds optional, `((h, m, s): padded(>= (9, 0, 30)))`: `9:00:30`, `10:00:00` in;
  `10:00` OUT (no seconds, no triple), `9:00`, `9:01` out.
- THIS CHANGES rev 18-19's answers. Rev 18's DECIDED-PREFIX order read a later field only when the earlier ones
  equalled the bound, so `10` (minutes unset) WAS in 9:30..11:00 (§8 table (W)). Under the joint condition `10` is
  out; table (S) shows both columns. Which is right? The decided-prefix answer is what the prefix EXPANSION happened
  to do; "the pair is in the range" has no pair to test. An author who means "10 o'clock, minutes optional, counts"
  writes it. Two ways, two meanings (§4B.4): "the missing field MEANS a value", the default,
  `t2 & ((h, m = 0): padded(between((9, 30), (11, 0))))` (`10` and `11` in, `9` out); "it DOES NOT MATTER", an
  explicit alternative, `t2 & (((h, m): padded(between((9, 30), (11, 0)))) | (h: 10))`. Rev 18's decided-prefix
  reading is WITHDRAWN (CF 11:05, the record) [§4C].
- A label unset in SOME alternatives of the pattern: per match, as above; `label.unset` warns at compile time as
  for any condition naming a label that can be unset (§4.2), its text naming both fixes (§4B.1).
- NON-NUMERIC text in a compared component: the tuple exists and lies outside the numeric comparison set (item 3).

### Item 7. Relations between fields

| relation | joint form | existing form | level |
|---|---|---|---|
| `b > a` (`\d+`) | `((a, b): increasing)` needs a NEW 2-ary primitive (a bare `<` as a relation, or a set comprehension); NOT PROPOSED | `(b: >$a)` (§4.6) | unbounded: `functions` only (§4.6), either way |
| start time before end time | `((eh, em): padded(> ($sh, $sm)))`: a product of two one-string `$` sets as the atom | `(eh: >$sh) \| (eh: ==$sh, em: >$sm)` by hand | a §4.6 relation, ~1,440 classes (borderline), same as today; table (SE) runs it on 168 classes [§4C] |
| equality between fields | `(b: ==$a)` | the same | §4.6 |
| a valid calendar date | `((month, day): month_days) \| (year: leap, month: padded(2), day: 29)`: a constant 4-row table (examples, §1) | E-CAL: `dim := days_in($year, $month)`, `(day: padded(<=$dim))` (`$dim` by J2; rev 19 wrote `<=dim`, §13 C13) [§4C] | joint: a constant union of products, DEFAULT level with no relation at all; E-CAL: a 24-class relation |

EXPANSION, shown for the default level (constant bounds). `(f1, ..., fk): >= (b1, ..., bk)` is the union of k
PRODUCTS, row j = `f1 == b1, ..., f(j-1) == b(j-1), fj > bj` (row k: `fk >= bk`), the remaining fields in their
literals' domains (canonical numerals for a numeral; J4, the DOM reading) [§4F: was "the remaining fields
unconstrained", SIM-1/3: every evidence script builds DOM]; each row is an existing condition record of single-label
comparison sets, so for set-once labels the union is §4.1's `|` of records, an automaton (§6.1); for looped labels
the union is taken per pass inside the pairing loop's item (LEVEL, §2) [§4F, SIM-4]. `between` intersects two such unions (products are closed under
intersection, so the result is again a finite union of products; at most 2k - 1 rows after
merging the shared prefix: TESTED by lane jcfold, table (RC), k = 2, 3, 4 over 5,491 bound pairs, maximum 2k - 1
reached and never exceeded [§4C]; 9:00..10:00 is `(h: 9) | (h: 10, m: 0)` padded). Table (X): time (all five operators at five bounds,
plus three between ranges, 22,484 cases), version a.b.c (1,734), IPv4 range (202): 0 differ, 0 engine
disagreements. The calendar: 13 per-month rows (C), 432 cases, and the 4-row table (C4), 468 cases, 0 differ from
`datetime.date`. With `$` bounds each row's comparison has a `$` atom: the §4.6 relation, class-count priced, the
same price rev 19's `[$a1, $a2]` bounds had.

The lane does NOT propose relation sets (`increasing`, `<` standing alone): `(b: >$a)` already says it with no new
form, and its level is the relation's, whatever the spelling.

### Item 8. The look-alikes

| look-alike pair | meaning | verdict |
|---|---|---|
| `((h, m): (S, T))` vs `(h: S, m: T)` | SAME by definition (J9, record-is-product, CF 11:35); table (P), 2,409 cases; with a default, table (RD), 76,860 cases | one meaning, the second the product case's spelling [§4C] |
| `((h, m): R)` vs `(h: R1) \| (h: R2, m: R3)` (R = R1 x any \| R2 x R3) | same on set-once labels; DIFFERENT on looped labels (table (L)) | a real look-alike: the moved looped WARNING (J7, item 5) fires on the second [§4C] |
| `>= (9, 30)` vs `(>= 9, >= 30)` | DIFFERENT: 2,700 of 11,000 padded (table (O)); 1,800 unpadded under DOM (table (DM)) [§4F] | BOTH LEGAL, BY DESIGN (J5, two-orders, CF 11:20), no warning [§4C] |
| `[(9, 0), (10, 30)]` (a union of tuples) vs `([9, 10], [0, 30])` / `(9 \| 10, 0 \| 30)` (a tuple of unions) [§4F, CENSUS-4] | DIFFERENT: padded, 3 vs 6 of 11,000 `t` subjects admitted, differ on 3 (`9:30`, `09:30`, `10:00`; table (DM), computed) | BOTH LEGAL, BY DESIGN like two-orders (the bracket's place says which: the owner's own 09:58 "9,10 and 30, 00" example), no diagnostic unless the owner wants one |
| `(h, m = 0): R` vs `(h, m: 0): R` | a default vs an error | the second is a COMPILE ERROR ("a reference list holds label names; a default is `m = 0`", §4B.4) [§4C] |
| `(9, 0)` (a pair) vs `[9, 0]` ("9 or 0") | different | `((h, m): >= [9, 0])` is an ARITY ERROR ("write `(9, 0)`"), never a silent answer |
| `(9, 0)` (a pair, value position) vs `f(9, 0)` (a call's record) vs `(h: 9, m: 0)` (a condition) vs `((h, m): ...)` (a left) | four uses of `( , )`, told apart by POSITION and by the `:`/`=` marks inside | one meaning per position (§5.4's rule for brackets); the table grows from four `( )` rows to six (N1, N3) [§4A.10: full census §4A.7] |
| `((h, m): R)` vs `(h, m: R)` | the second is an error (an entry without `:`) | error, names the double parentheses |
| `!((h, m): R)` vs `((h, m): !R)` | differ on an unset label | inherited §13 O28 (L30), no new case |
| `t & ((h, m): >= (9, 0))` vs `t & ((h, m): padded(>= (9, 0)))` | the first rejects `9:00`, and `10:00` too (m = `00` is not canonical; every component is read through its domain, J4) [§4F] | the existing C9 behaviour; `label.padding`-style hints are the existing story |

CENSUS (the draft's rule: every mark, one meaning per position, over this note's examples): `( , )` in value
position (product), `( , )` on the left of `:` (a record of paths), `( label: S )` (condition), `f( , )` (call),
`[ , ]` (alternation), `:` (narrows the left, now one path or a tuple of references), `|` `&` (extensional, any
arity), `>=` (comparison set, atom may be a tuple), `$` (a value), `padded(...)` (a modifier, on every part), `=` (a
name's value; NEW position: a default at a label left of `:`, §4B.3). No mark gains a second meaning in a position it
already had; three positions are new (N1, N3, N5) [§4C]. The full census: §4A.7.

### Item 9. What it removes from rev 19, and what it cannot replace

NO JOB LEFT (each is rev 19 text the joint condition does not need; "removed" in the exploration's word, but the
direction is PAUSED, not reversed, CF 00:31; RULED, **retire-paused**, CF 12:51: "retire-paused: agree to split. But
the pause on ^ is indefinite and requires real value other than 'override a users own *'": the `lex_` names, the
argument order and the first-library slot are RETIRED to a superseded-direction record, the joint condition taking
that slot; the sigil is PAUSED INDEFINITELY, out of rev 20's language, with **reference-index** and
**bound-reference** suspended with it [§4E: was "whether rev 20 RETIRES the ruled items among them is the owner's:
open item **retire-paused**, §8 [§4C]"]): the other-side sigil `^` and its §5.4 row;
arrays of field references and the question whether indexing them is an existing tool (§13 O75
**reference-index**); §4.1's ONE EXCEPTION (a parameter on the left of `:`); the binding of a bound call (§13 O76
**bound-reference**); the wrong-length mechanism (§13 O72: a k-ary left with a j-ary set is an arity error, so it
cannot be written); the six `lex_` names and their bodies; the any-n recursion and its two waiting features (O21,
arithmetic in an index); the strict spelling caveat; the DECIDED-PREFIX order (WITHDRAWN by ruling, CF 11:05);
`compare.repeated` (a repeated label on the left is an error at the condition); `compare.looped`'s subject (the
warning MOVED by ruling, CF 11:17, item 5). The owner's "tuple-compare: agree" (CF:1166) is met by the comparison
sets themselves; `lex_ge` and friends are NOT kept as library macros over the joint condition (THE MANAGER'S
reading of "agree", **library-not-syntax**, CF 12:48; left out of the first library until someone asks) [§4E: was
"a library still MAY name `lex`-style helpers, but none is needed"].

CANNOT REPLACE: anything that needs a FIELD as a thing passed to a macro, rather than a field constrained by a set.
A library macro cannot write a condition on a caller's label it is not told about; it can only return a SET the
caller lays against labels the caller writes. Every rev 19 use the lane found (the tuple compares, bounds from the
match, computed-label fields) is a set laid against written labels, so nothing in rev 19's examples is lost. What
the paused direction could ALSO have grown into (a macro taking `^h` and using it in several conditions, or in a
structural tool) has no example; D77 says wait. Relations that need a function of fields (weekday, day
differences) were never the reference's job: computed labels keep them (§4.4).

## 4A. The tuple as a value: the full account

Lane tupleval, 2026-11-16, design only. It answers the owner's request at CF:1362-1372 (2026-11-16 09:42), in his
words: "A pair as a value: I am ok with the tuple as a value. My request is that it's fleshed out and not the slice of
an idea. How is it related to conditions as we'd defined them(sounds like there was thinking there), is x a single
tuple (x), how can I access parts or can I, what is the definition, how can I use it generally". It applies his
clarification of 09:47 (relayed in the lane's rulings file, R-1), his words: "In my mind (x, y) is different than
(x,y): because the colon. So tuples need a left hand side with colon which mean the symbols are scoped references to
the intersected labels, and a right hand side which says the are bindings et al". [§4A.10, tupleval2] His 09:49
clarification: "I meant left right in the expression sense around =  You could use them as you say": the LEFT and
RIGHT of that statement are the two sides of the BINDING sign, not of the colon, and a colon-less tuple is used as a
value wherever values are used (tuple-anywhere: YES). At 09:50, shown the reading "the colon form `(h, m):` holds
scoped references to the intersected pattern's labels; a colon-less tuple is usable on either side of a binding: on
the right its entries are values, `lo := (9, 0)`; on the left its entries are names being bound, `(a, b) := lo` takes
it apart; that answers 'how can I access parts': by taking the tuple apart in a binding, with no index and no new
operator", his word: "Yes". At 09:58, told of lane tupleval's lean (no access), his words: "Nothing is set in stone.
I'd like to hear it out. So It's the set that makes it an item so you can't break it apart without changing its
meaning. Like 9:30, 10:00 broken apart is 9,10 and 30, 00 which is gibberish. Makes sense": reaching the parts is
OPEN, both positions laid out in §4A.3 (question **tuple-parts**). At 09:52 an IDEA, not a ruling: "I don't know if this helps but an idea
I had last night was functional style first/ rest binding with recursion" (worked in §4A.11). The answers follow his order; each
part opens with examples. Every sentence not quoted from him or cited to a ruling is the LANE'S. Evidence:
`docs/dev/lanes/tupleval_check.py` / `.out` (libpcre2-8 10.46 and Python 3.14.4 `re`, both engines on every case;
expectations from Python integer tuples, `datetime.date`, `ipaddress`, plain string equality, never from the regex
under test): 47,357 cases, 0 differ, 0 engine disagreements; tables (D), (R), (Q), (E), (O) below. Lane tupleval2's
evidence: `docs/dev/lanes/tupleval2_check.py` / `.out` (`timeout 120 python3 -I docs/dev/lanes/tupleval2_check.py`,
same engines and versions): 42,079 cases, 0 differ, 0 engine disagreements; tables (F), (FS), (A); sabotaged twice
(an expectation `>=` read as `>`: 18 differ, exactly the subjects equal to a bound; a clause's `==` row written `>=`:
5,535 differ), so it can fail. Placeholder spellings throughout (D193 add. 4).

### 4A.0 Examples first

    t := /(?<h>\d{1,2}):(?<m>\d\d)/
    office_hours := padded(between((9, 0), (17, 0)))      # a colon-less tuple: values. Bound, then passed
    t & ((h, m): office_hours)                            # a tuple WITH a colon: references to t's labels h, m
    open_at := [(9, 0), (13, 30)]                         # an array of pairs IS a set of pairs (two entries)
    t & ((h, m): padded(open_at))                         # 9:00 or 13:30, padded per component
    t & (h: 9, m: 0)                                      # the record ...
    t & ((h, m): (9, 0))                                  # ... and the joint form: same answers (table (P))
    supported := [between((1, 4, 0), (1, 9, 99)), >= (2, 0, 0)]
    semver & ((major, minor, patch): supported)           # a version policy, a library value over unnamed fields
    private := [between((10, 0, 0, 0), (10, 255, 255, 255)), between((172, 16, 0, 0), (172, 31, 255, 255))]
    ip & ((a, b, c, d): private)                          # a CIDR list is an array of tuple ranges (table (R))
    span & ((eh, em): padded(> ($sh, $sm)))               # a tuple of this match's values: one pair per match
    x,  (x),  ((x))                                       # one thing: one entry in parentheses is grouping
    (h: S),  ((h): S)                                     # one thing: one reference left of ':' is the plain condition
    f((1, 2))                                             # ONE argument, a pair (was an error: L45, see 4A.1)
    t & (9, 0)          # ERROR: a set of pairs has no text; write t & ((h, m): (9, 0))
    /${(9, 0)}/         # ERROR: the same
    (lo_h, lo_m) := (9, 0)                                # OPEN (**tuple-parts**, 4A.3): (A) an error; (B) new names 9, 0
    (y, md...) := (2024, 2, 29)                           # first and rest (IDEA, 4A.11; needs (B)): y = 2024, md = (2, 29)
    (m, d) := month_days                                  # ERROR under (A) and under the lane's lean (B1): a set is one item
    (9, 0)[1]           # ERROR: `[n]` reads ENTRIES; (9, 0) has one entry, the pair (parts: 4A.3)

### 4A.1 How the tuple relates to conditions as defined (the record)

THE OWNER'S COLON IS THE DISCRIMINATOR. `(h, m):` and `(9, 0)` share a bracket and differ by the colon after it. A
bracket FOLLOWED BY `:` holds SCOPED REFERENCES to the intersected operand's labels (the left of a condition entry,
§4.1: "a label PATH ... never an expression", `predicates_draft.md:1526`); a bracket NOT followed by `:` in value
position holds VALUES (bindings, literals, `$` values, calls). [§4A.10, tupleval2] Both are tuples in his words; the
colon-less one is the VALUE: on the right of a BINDING sign its entries are values (`lo := (9, 0)`; his sides are the
binding sign's, 09:49); whether it may also stand on the LEFT as names being bound (`(a, b) := lo`) is the open
**tuple-parts** (4A.3). So a condition entry `h: S` is the ONE-REFERENCE case of `(h, m): R`, and a condition entry relates a
tuple of references to a set of value tuples: "the labels' texts, read together, are one of these tuples".

THE BRACKETS KEEP THEIR RULED MEANINGS (CF:863: `[ ]` any one entry, `( )` all entries together; the comma only
"next entry"). In value position over sets, "any one entry" is the union (today's alternation) and "all entries
together" is the PRODUCT: `(S, T)` is every pair (s, t). No bracket gains a second meaning; the colon-less `( , )`
in value position, an ERROR in rev 19, becomes "all together" applied to values. A literal is a one-string set (§2.1,
`predicates_draft.md:853-854`), so `(9, 0)` is the product of {"9"} and {"0"}: the one pair. A value is a SET, as an
rx is a set of strings: a tuple-valued expression denotes a SET OF k-TUPLES, never a lone tuple, and one tuple is
the one-element case, as one string is the one-string set.

THE RECORD RULING STANDS UNTOUCHED, and the tuple is not a record. The owner's words: "I'm ok with a purely
structural type if it can't be bound directly ie not first class type" (CF:851-852); the record of his acceptance
(CF:866): "A RECORD is NOT a value: it cannot be bound, stored or returned. It appears only laid against something
with fields". A record is defined by what it is LAID AGAINST (a macro's parameters, a pattern's labels, a result's
groups); a colon-less tuple in value position is laid against nothing, its components have no names, and it is
bound, passed and returned like any value. Nothing that was a record becomes a value. What moves are the draft's
LEAN inferences that "any colon-less `( , )` in value position would be a record used as a value, hence an error"
(none is the owner's text): §0.1 L45 (`predicates_draft.md:543`: `f((1, 2))` an ERROR) becomes "one argument, a
pair"; the §5.4 `( e1, e2, ... )` row ("ONLY laid against something with fields", `predicates_draft.md:2013`) and
the condition row's "Any other record in value position is an error" (`:2014`) gain the tuple row beside them (4A.7).
UNCHANGED: L43 (`:541`), `(x = /a/, y = /b/)` in value position is still an error, because labelled entries in value
position would be the withdrawn map literal (§3.1, `:1401`; §13 O42), a record used as a value; a tuple's
components are positional only.

THE ONE-WAY RULE, extended in its own direction. His words: "You can view a regex as a record but not vice versa as
what does that even mean?" (CF:853-854). The joint condition IS a regex viewed as a record (its labels, named left of
the colon) tested against a tuple set; a tuple set is never read as a regex (it has no text: 4A.6). The closure the
owner's record declined, "a record of rx = their sequence" ("loses boundaries, `(1, 40)` vs `(14, 0)`", CF:866 (4)),
does not return: a tuple keeps its components apart, and `(1, 40)` and `(14, 0)` are different pairs.

THE TWO INTERFACES (CF:890-891: "Array and map are interfaces that can be applied to regex"). A tuple set has the
ARRAY interface over its spelled entries (`[(9, 0), (13, 30)]` has two entries, each a pair; "an array of something
is that something", CF 2026-11-14 00:10, 11-16 00:08) and NO map interface: its components have no names, and giving
them names would be the record as a value. So `.` never applies to a tuple set and `[n]` reads entries, never
components (4A.3).

THE RECORD CONDITION `(h: S, m: T)` gives the same answers as `((h, m): (S, T))` on every population tried (table (P)
of §2, 2,409 cases), and the record is DEFINED as that product case (RULED, J9, record-is-product, CF 11:35);
§4D derives it and checks the draft's record rules against it [§4C].

### 4A.2 Is a plain value x the one-entry tuple (x)?

    x,  (x),  ((x))                 # one thing: grouping, as today (§0.1 L44, §13 O41 lean)
    ((h): S),  (h: S)               # one thing: one reference left of ':' (grouping on the reference side too)
    ((9, 0)),  (9, 0)               # one thing: grouping of a pair; NOT a one-tuple holding a pair
    [9, 0]                          # "9 or 0": an arity-1 set with two entries
    (9, 0)                          # one pair: an arity-2 set with one entry
    ()                              # ERROR: an empty tuple has no use (no example; D77)
    (9,)                            # ERROR: no one-tuple distinct from its entry
    ((9, 0), 1)                     # ERROR: a tuple entry must be arity 1 (no nesting; see below)

YES: `x` and `(x)` are the same thing, and there is no separate one-tuple. Every existing set (every rx, every
literal, every condition's right side) is a set of 1-tuples, and a set of 1-tuples and a set of strings carry the
same information: no operator, position or tool could tell them apart, so keeping two would be a distinction with no
consequence. One-entry parentheses are therefore GROUPING on both sides of the colon: `((h): S)` is `(h: S)`. The
draft's existing lean already says this for values (`predicates_draft.md:542`, L44; `:3935`, O41), and nothing here
changes it. Under the ruled ARITY (J3, set-arity, CF 10:26) today's rx are the arity-1 sets [§4C].

ARITY 0. `()` would be the set of 0-tuples: either {()} (holds always) or {} (holds never). No example needs either
(D77): an error in every position. (A call with no arguments is not affected: phase 1 has no zero-parameter macro;
a binding without a head is a name.) [§4A.10, tupleval2] The first/rest idea (4A.11) does not need it either: because
`(x)` is `x`, the rest of a pair is its plain second entry, so a recursion on the rest ends at a plain value, never
at `()` (table (F) runs the definitions with that base case).

NESTING. `((9, 0), 1)` could mean the flattened triple `(9, 0, 1)` or a pair whose first part is a pair. Flattening
would let a library compose a k-ary set from a smaller one (`(years, month_days)`), but every such set in the
examples is writable with arity-1 entries row by row (§5 problem 4's `valid_ymd`: the four rows of §1, each entry
arity 1), so the lane leans ERROR ("a tuple entry is one field; write the components out") and names the trigger: a
library set that can only be written by composing tuple sets.

### 4A.3 Can the parts be reached, and how?

[§4A.10, tupleval2: REWRITTEN on the owner's entries of 09:49, 09:50 and 09:58. OPEN: both positions are laid out;
neither is ruled. Lane tupleval's option table (a)-(f) is folded into them.]

THE OWNER'S WORDS, in order. 09:49: "I meant left right in the expression sense around =  You could use them as you
say". 09:50, shown "on the left its entries are names being bound, `(a, b) := lo` takes it apart; that answers 'how
can I access parts': by taking the tuple apart in a binding, with no index and no new operator", his word: "Yes".
09:58, told of lane tupleval's lean (no access): "Nothing is set in stone. I'd like to hear it out. So It's the set
that makes it an item so you can't break it apart without changing its meaning. Like 9:30, 10:00 broken apart is
9,10 and 30, 00 which is gibberish. Makes sense".

    lo := (9, 0)
    t & ((h, m): office_hours)  then  $h, $m      # BOTH: a MATCH's parts, named left of the colon, read with `$`
    (lo_h, lo_m) := lo                            # (A) ERROR, used whole;   (B) lo_h = 9, lo_m = 0
    (sh2, sm2) := ($sh, $sm)                      # (A) ERROR;               (B) one pair per match: exact
    (a, b) := [(9, 30), (10, 0)]                  # (A) ERROR;               (B) his "gibberish": a = 9|10, b = 30|0
    (m, d) := month_days                          # (A) ERROR;               (B) 365 pairs come back as 372
    lo[1],  lo.1,  part(lo, 1)                    # BOTH: ERRORS (no index, no map interface, no projection built-in)

POSITION (A): NO ACCESS. A tuple VALUE is used whole: compared, combined, bound, passed, laid against labels. A
MATCH's parts are named left of the colon and read as `$h`, `$m`. (Lane tupleval's lean.) Its strongest case is the
owner's reason: "It's the set that makes it an item so you can't break it apart without changing its meaning". A
tuple value is a SET of tuples (4A.4), and the parts of a set are its PROJECTIONS, which lose the pairing: his
`9:30, 10:00` gives `9, 10` and `30, 00`, and those put back together are four times, two of them (9:00, 10:30)
never in the set (table (A)); `month_days` 365 pairs -> 372 (tables (D), (A): 7 subjects the table refuses, `02-29`,
`02-30`, `04-31`, ...); `>= (9, 30)` over a day's times 870 -> 900 (table (A)). Price: nothing new, and nothing in
the account needs a part: the only component use in the draft was rev 19's `lo[1]` inside the replaced `lex_`
bodies (§4 item 9), and no §12 case takes a tuple apart. What it gives up: a part of a tuple is never usable alone
(one bound's hour as a single-label bound), and the first/rest idea (4A.11) CANNOT BE WRITTEN: it needs taking
apart.

POSITION (B): TAKING APART ON THE LEFT OF A BINDING. A colon-less tuple on the LEFT of `:=` is a tuple of NEW NAMES
laid positionally against the value on the right, each name bound to its position's component. Its strongest case:
it is the owner's own reading (09:49, 09:50); it is the position the draft already holds in its DESIGN, the record on
the left of `:=` (`predicates_draft.md:726-730`: RULED in the design, CF:852, "We might use it to bind values from a
search (x,y) := rx ~ /.../"; out of phase 1 unless an example needs it), so it costs no new mark, no index and no
new operator; on ONE tuple it cannot change meaning (`(9, 0)` gives `9` and `0`, and they put back `(9, 0)`); and
it gives first/rest its step. Price: the left of `:=` enters the language (§13 O51's statement-start parse); and on
a SET it meets the owner's objection head on, so it needs one of three sub-choices:

| sub-choice | `(a, b) := [(9, 30), (10, 0)]` | `(a, b) := (padded(between(1, 12)), padded(between(1, 28)))` | for | against |
|---|---|---|---|---|
| (B1) ONE TUPLE ONLY: every component one string (a literal, a binding of one, a `$` value of a set-once label: one tuple per match) | ERROR: "a set of 2 pairs is one item: taking it apart changes its meaning; lay it against labels" | ERROR | his objection is the error case, word for word; the test is read off the expression (each component one string); enough for first/rest and the library order (every bound there is one tuple, 4A.11) | refuses a product, whose round trip is exact |
| (B2) ONE TUPLE OR A PRODUCT, decided on the SET (the set equals the product of its parts) | ERROR, as (B1) | `a`, `b` the two sets, exact (336 of 336 pairs, table (A)); `[(1, 2), (1, 3)]`, spelled as an array, IS a product and passes | the widest form whose round trip is always exact | the compiler decides product-ness on a set (decidable for 4A.4's finite unions of products of regular sets, by comparing the set with the product of its parts; cost UNMEASURED); no case takes a product apart |
| (B3) ANY SET, the names holding projections (with or without a warning) | `a` = 9 or 10, `b` = 30 or 0: his "gibberish" | as (B2) | the simplest rule text | the round trip silently widens (his 2 pairs -> 4; 365 -> 372); a warning is one ignored line from that |

UNDER (B), the lane's further consequences: the left holds plain names only (no nesting, 4A.2; they are new
bindings, so CF:1268-1282's shadowing has nothing to shadow); a count mismatch is a compile error (arity is static);
a search result's groups (§13 O54) and a tuple's components would be one meaning of the left of `:=`, "take the
right apart by position", if a result is read as the tuple of its groups (O54 stays open); phase-1 entry still
follows the draft's "out unless an example needs it" (no §12 case; the first/rest library would be one).

WHAT THE REJECTION OF `[n]` AND `.` RESTS ON, under either position: (1) `[n]` already reads ENTRIES of the array
interface (§3.2 tool 1): `[(9, 0), (17, 30)][1]` is `(9, 0)`, so reading components with it would give one mark two
meanings; `(9, 0)[1]` is `(9, 0)` (its one entry), `(9, 0)[2]` the out-of-range absent entry (§3.2); (2) `.` is the
map interface, which needs component NAMES: named components are a record used as a value (CF:866), and `.name` is
never digits (§3.2 tool 4); (3) under (A) parts are not reached at all, and under (B) the binding reaches them (the
reading he said "Yes" to named "no index and no new operator"). A projection built-in `part(t, i)` is rejected
under both: under (A) it is the projection he calls gibberish; under (B) it is a second route to what the binding
does, plus a name on the closed built-in list (§5.1).

LEAN (the lane's): (B1). The two positions differ only on ONE tuple once (B) is held to (B1): a SET of tuples is
never broken apart under either, which is the owner's 09:58 reason kept in full; one tuple, whose parts put back
give the same tuple, can be taken apart, which is his 09:50 "Yes" kept where it cannot change meaning. Like the
draft's other left-of-`:=` uses it stays out of phase 1 until an example needs it; the only candidate is the
first/rest library (4A.11), whose own lean is "not now", so in practice the account runs as (A) until then. [§4A.10, unsetdef] With first/rest PARKED (10:22), **tuple-parts**
has NO USER: it stays open, nothing is built, and the account runs as (A). (B2) and
(B3) are not leaned: (B2) buys an exact round trip on products that no case takes apart, at an UNMEASURED
compile-time test; (B3) is the gibberish. Owner question **tuple-parts**, with both sides.

### 4A.4 THE DEFINITION

A TUPLE SET of arity k (k >= 2) is a set of k-tuples of strings; it is the value of a TUPLE-VALUED expression, whose
arity is fixed at compile time (after macro expansion), and every other SET is arity 1 (a set of strings; **set-arity** RULED, 10:26: one set kind, today's sets being arity 1
[§4A.10, unsetdef]); macros are values as today (CF:858) [§4F: was "every other value", RULING-5].
PRODUCERS: (1) the TUPLE BRACKET `( e1, ..., ek )`, k >= 2, in VALUE position (no `:` after the closing bracket, no
`:` or `=` inside), each ei an arity-1 expression: the product e1 x ... x ek (one-string entries give one tuple; a
`$` entry of a set-once label gives one string per match); (2) `A | B` and `A & B` with A, B of the same arity:
union, intersection; (3) an array `[t1, ..., tn]` of entries of one arity: any one entry (the union), entries kept in
order for the structural tools; (4) a COMPARISON SET with a tuple atom, `op (b1, ..., bk)` with op in `<` `<=` `>`
`>=` `==`: the k-tuples in DICTIONARY order (first component first) relative to the atom, component i compared by
bi's literal reading under §2.4 (a numeral: canonical integers; a quoted string: string order), each bi a one-string
set (a literal, a `$` value of a set-once label, a binding of one; a many-string component is an error, §2.4 being
silent on a many-string atom); EVERY component of a tuple tested, the ones after the deciding component included,
must lie in its literal's domain (the DOM reading; the manager's reading (round jointcond, DICT-DOMAIN), J4; table
(DM)) [§4F]; a `$` component has no literal and is read by its VALUE, leading zeros ignored (rev 18's LEAN,
`predicates_draft.md:2554-2563`, pending O27) [§4F, DOLLAR-COMPONENT]; `between(lo, hi)` is `>=lo & <=hi` unchanged [§4A.10, tupleval2: the owner's
first/rest idea would instead DEFINE this order in a library, the comparison set keeping its one-value atom; worked
and tested in 4A.11, PARKED by the owner (10:22) [§4A.10, unsetdef]: this producer is the design]; (5) a macro whose body yields one, and a
binding of any of these with CONSTANT entries (a binding names whatever its expression is, §2.1); a binding that
reads match labels is a COMPUTED LABEL (§4.4, `predicates_draft.md:1724-1725`), and a computed label is ARITY 1, so a
match-dependent tuple (`($sh, $sm)`) is written inline or passed as an argument, never bound: `start := ($sh, $sm)`
is an ERROR naming the inline form ("a computed label holds one string; write `> ($sh, $sm)` where it is used")
(the manager's reading (round jointcond, TUPLE-BINDING)) [§4F]; (6) a FILTER MODIFIER applied to one
(`padded(t)`), acting on every component (RULED, J8, modifier-lift, CF 11:27) [§4C]; which macros lift: those whose
result distributes over `|` (J8; the manager's reading (round jointcond, OWNER-5)) [§4F]. EQUALITY: two tuple sets are
equal when they hold the same tuples; two tuples are equal when their components are equal STRINGS, so the literal
`(9, 0)` is the text pair ("9", "0") and admits no `t` subject (table (E): 0 of 11,000; minutes are two digits),
while `padded(== (9, 0))` admits `9:00` and `09:00` (2), as `(m: 0)` and `(m: padded(==0))` differ today. ACCEPTED
POSITIONS: the right of `:` in a condition entry whose left names k references (`((h, m): R)`; one reference is the
plain `h: S`); an ARGUMENT of a call (a parameter takes any value); the right of `:=`, and there [§4A.10, tupleval2],
under position (B) of the open **tuple-parts** (4A.3), a colon-less tuple of k NEW NAMES on the left of `:=` takes
it apart, each name bound to its position's component (the lane's lean (B1): one tuple only); an entry of `[ ]` beside
entries of its arity; an operand of `&`, `|` beside one of its arity; the atom of a comparison; the argument of a
filter modifier (J8); `!R` on the right of `:` (the complement over all k-tuples of strings in the
filter role, §2.2; `!((h, m): R)` vs `((h, m): !R)` inherits §13 O28 unchanged). ERRORS, each naming its fix: an
ARITY MISMATCH (between the two sides of `:`, the operands of `&`/`|`, an array's entries: `[(9, 0), 5]`); a tuple
where an arity-1 set is required: an rx HOLE (`/${t}/`), the program's final pattern, an `&` with a pattern operand
(`P & t`: "write `P & ((h, m): t)`"), a single-reference condition (`(h: (9, 0))`), a `join` entry, an index bracket
(`X[(1, 2)]`), arithmetic (`t + 1`), a nested tuple entry (`((9, 0), 1)`); the empty `()` and a one-entry `(e,)`;
labelled entries (`(x = 1, y = 2)`, L43 unchanged) and a mix of `:` and plain entries (`(h: 9, 0)`); a component
read by `[n]` or `.` (4A.3, under either position); under (B), on the left of `:=` a count of names other than the
arity, and (lean (B1)) a value that is not one tuple (4A.3); a BOUND match-dependent tuple (producer (5)) [§4F]; a `$` tuple over a REPEATED label (`($h, $m)` with h, m in a loop: at the default level
the bare `$h` is already the repeated-label error, `predicates_draft.md:1632-1634`; at `captures` it would be the
product of every h with every m, which loses the iterations' pairing, table (Q): 5 of 11 subjects differ from the
per-iteration pairs, so it stays an error naming the joint condition).

The class this produces, with constant entries, is the finite unions of products of regular sets: closed under `|`,
`&` and the filter-role `!`, and each one a finite `|` of condition records over single labels, so every joint
condition on a constant tuple set compiles at the DEFAULT level (§6.1); with `$` components it is a §4.6 relation,
priced by class count (the lane's consequence; the expansions are engine-checked in §2's (X), (C4) and here in (R);
the closure under `!` is UNTESTED).

### 4A.5 General use beyond the compare

| problem (draft or this note) | use of the tuple value | vs today | evidence |
|---|---|---|---|
| E-CAL (§12.5) | `month_days`, a declared 3-row table of products; `isodate & (((month, day): month_days) \| (year: leap, month: padded(2), day: 29))` | SIMPLER: no `days_in`, no relation (§5 problem 4) | (C4) 468 cases |
| E-IPV4 (§12.3) and its `cidrs` (§3.5: "`ipv4 & cidrs` reports which entry admitted the match") | a CIDR block is ONE dictionary range `between(network, broadcast)` over the four octets, whether or not its prefix falls on an octet boundary; a list of blocks is an array of them | NEW GROUND: E-IPV4 checks octet validity only; ranges and block lists need labels on the octets (an existing `=`). Whether `.index` reports the admitting entry of an array on the RIGHT of `:` is not stated by the draft for single labels either: not claimed | (R) 6 blocks, 1 on an octet boundary, 5 not, 2,422 cases, expectation by `ipaddress` |
| version policies (§8's tuple rows, §5 problem 2) | `supported := [between((1, 4, 0), (1, 9, 99)), >= (2, 0, 0)]`, laid against any version pattern's labels | SIMPLER than six `lex_` names | (X) of §2 for single ranges; the array is `\|` (UNTESTED as an array) |
| time windows (§5 problems 1, 6, 7) | `office_hours`, `open_at` bound once, passed, reused | SIMPLER | (X), (L), (U) of §2 |
| a library constraint over unnamed fields | `dates.valid_ymd`, `office_hours`: the library names no label; the caller names them left of the colon | NEW: the mechanism's main gain (§2) | as above |
| bounds from the same match (§5 problem 5) | `> ($sh, $sm)`: a tuple of this match's values, one pair per match (set-once labels only) | SAME level as any spelling (§4.6) | table (SE), 13,328 cases, 0 differ [§4C] |
| a multi-field allowlist (`((level, service): [("error", "db"), ("warn", "auth")])`) | a finite set of pairs | NO §12 CASE has one (E-JSONL tests each key alone); a real use, recorded, not an example | none |
| group questions (§4.3) | `count(((h, m): R))`, `some(((h, m): R))`: the iterations whose pair is in R | SAME machinery, one more condition shape | (L) of §2 |
| E-WEEKDAY, E-RFC, E-NEAR (c) | a function of the fields (weekday, day difference) | SAME: computed labels (§4.4); a tuple set defined by a function is not proposed (B5) | — |
| E-JSONL, E-LUHN, E-FILE, E-HTTP, E-SEP, E-DEPTH, E-CTX | no several-field value | SAME | — |
| results / outputs (§6.2) | a match reported as a tuple of its labels | NOT PROPOSED: the report already carries the labels; no example asks for a tuple | — |
| a MATCH viewed as a tuple (its labels read out as one) | `($h, $m)` already is that, per match, with existing marks | NOT PROPOSED as a separate form (`$(h, m)` or the like): §5 problem 5 is the one use and `($sh, $sm)` covers it | — |
| a FILE of combinations (an allowlist CSV as a tuple set) | `records(...)` yields an rx with labels; reading it as a k-ary set would view an rx's labels as tuple components | NOT PROPOSED: a new form (an rx's labels projected to a tuple set); no example; trigger: a case loading a combination list | — |

Tally (the lane's): 2 of the twelve §12 cases gain (E-CAL simpler, E-IPV4 new ground with ranges and block lists);
10 are the same; none worse. The gains beyond §12 are the library-set uses (a constraint shipped without naming
fields), which is what the owner's criterion asks of the mechanism (CF:1336-1352: "how it would help the larger
language against other problems").

### 4A.6 What it cannot do

| position | example | error (wording illustrative, D26) |
|---|---|---|
| a pattern or the program's final expression | `(9, 0)` as the last line | "a set of pairs has no text; lay it against labels: `P & ((h, m): ...)`" |
| an rx hole | `/${(9, 0)}/`, `/${office_hours}/` | the same |
| `&` with a pattern | `t & (9, 0)`, `t & office_hours` | "`&` fills an operand of strings; write `t & ((h, m): office_hours)`" |
| concatenation | none exists (§2.5); `join([(9, 0), ...])` | "a join entry is a string set" |
| a single-reference condition | `(h: (9, 0))` | "h is one label; the set holds pairs" |
| mixed arity | `[(9, 0), 5]`, `(9, 0) \| 5`, `((h, m): >= [9, 0])` | "arity 2 beside arity 1"; for the last, "write `(9, 0)`: `[9, 0]` is 9 or 0" |
| a component read | `lo[1]`, `lo.1` | "`[n]` reads entries" (under (B) adding "take it apart: `(lo_h, lo_m) := lo`") [§4A.10, tupleval2] |
| taking a tuple apart: under (A) every one; under the lane's lean (B1) a value that is not ONE tuple (**tuple-parts**) | `(m, d) := month_days`, `(a, b) := [(9, 30), (10, 0)]` | "a set of 2 pairs is one item: taking it apart changes its meaning (its parts would also give 9:00, 10:30); lay it against labels: `P & ((h, m): ...)`" [§4A.10, tupleval2] |
| a count mismatch left of `:=` (under (B)) | `(a, b) := (1, 4, 0)` | "3 entries on the right, 2 names on the left" [§4A.10, tupleval2] |
| a `$` tuple over repeated labels | `($h, $m)` with h, m in a loop | "h and m repeat; their values do not pair; write the joint condition" |
| arithmetic, index brackets | `(9, 0) + 1`, `X[(1, 2)]` | "a number is a string set" |
| labels in a value tuple | `(h = 9, m = 0)` | L43's error, unchanged |
| a reference tuple without its colon used as references | `between((h, m), ...)` with h, m labels | the bare-reference ruling (CF:1268-1282: "it might shadow a binding"): right of a colon or in an argument, `h` is a binding; "for the label's value write `$h`" |

### 4A.7 The mark census for `( )` and `,` after the addition

Every position, one meaning; a `( )`'s position is decided by what PRECEDES it (an expression: a call), what FOLLOWS
it (`:` or `:=`), and what is INSIDE it (`:` entries, `=` entries, a leading `&`, a comma). Inside `/.../` neither mark
is the language's (PCRE's own, §5.4).

| form | position | meaning | told apart by |
|---|---|---|---|
| `f( e1, ... )` | after an expression | a CALL: one record against the parameters (§5.2) | the preceding expression |
| `m( p1, ... ) :=` | statement head | a DEFINITION head | followed by `:=` after a name |
| `( p1, ..., pk ) :` | left of `:` inside a condition | a TUPLE OF REFERENCES to the operand's labels (the owner's colon, R-1); k = 1 is grouping, so `((h): S)` = `(h: S)`; each entry a path, or a path `= v` (a default, §4B.1) [§4F] | followed by `:` |
| `( label: S, ... )` | value position | a CONDITION (a macro, §4.1); its record is laid against the operand's labels | entries `p: S` or `p = v: S` inside [§4F: was "`:` entries inside", CENSUS-1] |
| `( x, y ) :=` | statement start (left of the binding sign) | NEW NAMES laid positionally against the value on the right: in the design a result's groups (§13 O54); and a TUPLE TAKEN APART under position (B) of the open **tuple-parts** (4A.3; one meaning if a result is read as the tuple of its groups) [§4A.10, tupleval2] | followed by `:=` (not `:`) |
| `(& f)` | value position | a SECTION (§5.2) | leading `&` |
| `( e )` | value position | GROUPING (§0.1 L44) | one entry, no `:`, `=`, `&` |
| `( e1, ..., ek )`, k >= 2 | value position | NEW: a TUPLE SET (the product of its entries) | comma, no `:` after it, no `:`/`=` inside |
| `( x = e, ... )` | value position | ERROR (L43, unchanged) | an `=` entry with no `:` [§4F: was "`=` entries", CENSUS-1] |
| `()`, `( e, )`, `( a: S, e )` | anywhere | ERROR | — |
| `,` | between entries of any of the above or of `[ ]` | "next entry", never logic (CF:863), unchanged | — |

THE LOOK-ALIKES the addition creates or touches:

| pair | answer | verdict |
|---|---|---|
| `((h, m): R)` vs `((h, m))` | the first: references, a condition; the second: grouping of a tuple of the BINDINGS h, m | one-token difference (the colon), the owner's discriminator; the second is an error if h, m are labels and no bindings (bare names are bindings there, CF:1268-1282) |
| `f(1, 2)` vs `f((1, 2))` | two arguments vs one pair | NEVER BOTH LEGAL for one macro: positional arguments are exactly the required parameters (§5.2), so one of the two is always the wrong-count error. G4 holds (§1 Goals) |
| `(9, 0)` vs `[9, 0]` | one pair vs "9 or 0" | different arities; the slip is an arity error (§4 item 2 (c)) |
| `(h: 9, m: 0)` vs `((h, m): (9, 0))` | the same answers (table (P)) | the same by definition (J9, record-is-product, CF 11:35) [§4C] |
| `(a, b) := t` vs `((a, b): t)` | NEW NAMES taking t apart vs references to labels a, b laid against t | `:=` vs `:`, the owner's two marks; under (B) both legal, meanings stated by the mark (on a t that is not one tuple the first is an error under the lean (B1)); under (A) the first is an error (**tuple-parts**) [§4A.10, tupleval2] |
| `((h, m): (9, 0))` vs `((h, m): padded(== (9, 0)))` | text pair vs numeric pair: 0 vs 2 of 11,000 `t` subjects (table (E)) | the existing `(m: 0)` vs `(m: padded(==0))` story; the first is the empty-intersection error at a narrowing site (§5.2) |
| `>= (9, 30)` vs `(>= 9, >= 30)` | dictionary order vs product order: PADDED they differ on 2,700 of 11,000 `t` subjects (table (O); `10:00` is in the first only); unpadded 1,800 under DOM (table (DM)) [§4F] | BOTH LEGAL, DIFFERENT. The operator's place (outside or inside the bracket) says which; RULED both legal, no warning (J5, two-orders, CF 11:20) [§4C] [§4F: was "the one pair in this census that is neither the same answer nor an error"; the next row is a second] |
| `[(9, 0), (10, 30)]` vs `([9, 10], [0, 30])` | a union of two pairs vs the product of two alternations (four pairs): padded, 3 vs 6 of 11,000 admitted, differ on 3 (table (DM), computed) | BOTH LEGAL, DIFFERENT, BY DESIGN like two-orders: the bracket's place says which (CENSUS-4) [§4F] |

Count (the lane's): `( )` has nine value-or-statement rows (rev 19's §5.4 has four `( )` rows plus the head and the
left of `:=` folded into them); the addition is TWO rows (the reference tuple before `:`, the value tuple), and no
existing row changes MEANING; two rows change their DISCRIMINATOR for the default (the condition row now admits
`p = v: S` entries, the L43 error row is "an `=` entry with no `:`") [§4F: was "no existing row changes meaning",
CENSUS-1]; `,` is unchanged. THE NUMBER rev 20 prints (CENSUS-6) [§4F]: on rev 19 §5.4's basis (its "`( )` has four
rows", `predicates_draft.md:1998`) the count becomes SIX: the four plus the reference tuple and the value tuple;
heads, the left of `:=` and the error shapes stay folded, and the default adds no row (it rides the reference-tuple
and condition rows). This table's own basis unfolds them: ten `( )` rows (eight meanings, two error rows). [§4A.10, tupleval2] Taking a tuple apart, under (B), adds no row: it is the
existing left-of-`:=` row (design only). The first/rest idea (4A.11; PARKED, [§4A.10, unsetdef]) would add a REST MARK (one mark,
one meaning, "the remaining entries", in two positions: a name on the left of a binding or in a head, a value on
the right) and a tuple of names inside a definition head.

### 4A.8 The manager's first answers, tested

| answer | verdict | reason |
|---|---|---|
| (m1) every tuple-valued expression denotes a SET of tuples, as an rx denotes a set of strings; `(9, 0)` the one-pair set, `(S, T)` the product | HOLDS, INCOMPLETE | the reading is the brackets' ruled "all together" in value position (4A.1); missing: the arity is static and every entry arity 1 (no nesting), a comparison atom's components must be one-string sets, a `$` component gives one pair per match only on set-once labels (table (Q)), equality is string equality per component (table (E)) |
| (m2) the record is not a value still holds; a tuple set has no names; the joint condition is where the two meet; `(h: S, m: T)` is `((h, m): (S, T))` | HOLDS, INCOMPLETE | the ruling is untouched (4A.1), but three LEAN sentences of the draft that inferred an error from it move (L45, the §5.4 `( e1, ... )` row, the condition row's "any other record"); and "is" is now RULED (J9, record-is-product, CF 11:35) [§4C] |
| (m3) `x` and `(x)` are the same; one-entry parentheses are grouping; every existing set has arity 1; `((h): S)` is `(h: S)` | HOLDS | 4A.2; set-arity RULED, ARITY [§4C]. Added: `()`, `(e,)` and nested entries are errors |
| (m4) parts are reached by destructuring `(a, b) := t`, NOT by an index; on a non-product set a part is a projection and loses the pairing | OPEN (**tuple-parts**, 4A.3). Lane tupleval judged it PARTLY WRONG (parts named left of the colon, a tuple value used whole); the owner then said "Yes" to taking apart (09:50) and "Nothing is set in stone. I'd like to hear it out" with his reason for no access (09:58) [§4A.10, tupleval2] | the index rejection and the projection loss HOLD under both positions (tables (D), (A); his own example `9:30, 10:00` gives back 4 pairs) |
| (m5) general uses: lookup tables, multi-field allowlists, library constraints over unnamed fields, bounds `($sh, $sm)` | HOLDS, INCOMPLETE | lookup tables and library sets hold (E-CAL, (C4)); the multi-field allowlist has no §12 case; `($sh, $sm)` (tested since: table (SE) [§4C]) must be refused over repeated labels (table (Q)); missed: CIDR block lists (§3.5's `cidrs`, table (R)) and version-policy arrays |
| (m6) a tuple set is never a pattern: no text of its own, so `${t}`, `P & t` and concatenation are errors | HOLDS, INCOMPLETE | missed: the final expression, a single-reference condition, `join` entries, index brackets, arithmetic, mixed arity; and `&` is an error only with a PATTERN: `t & u` of one arity is legal (intersection) |
| R-1 manager's reading (i): a name left of the colon is never looked up as a binding | INCOMPLETE | a COMPUTED label is a binding by spelling and a label of its pattern (§4.4, `predicates_draft.md:1722-1737`; the owner's pointer, CF 2026-11-15 23:46), and it stands left of the colon today (`isodate & (weekday: 6)`); the scope left of the colon is the operand's labels, computed labels included; a PURE binding is never looked up there; RULED as so restated (J2, colon-scope, CF 11:32), with his refinement: a default after `=` there is on the value side [§4C] |
| R-1 (ii): a name in a right-hand tuple is never looked up as a label [§4A.10, tupleval2: "right-hand" read here as right of the COLON; R-2 says his sides are the binding sign's. Restated: a name in a colon-less VALUE tuple (right of `:`, right of `:=`, an argument) is never looked up as a label; a name in a tuple LEFT of `:=` (under (B) of **tuple-parts**) is a new binding, never a lookup at all] | HOLDS (J2, colon-scope, CF 11:32) [§4C] | labels are read by `$` there (§4.1); the draft's bare `<=dim`, `==wd` (§13 C13) become `<=$dim`, `==$wd` (THE MANAGER'S consequence, CF 11:32, tested in §4C) |
| R-1 (iii): a colon-less tuple may stand wherever a value may (bound, passed, returned) | HOLDS, ANSWERED YES by the owner (R-2, **tuple-anywhere**) [§4A.10, tupleval2] | wherever an arity-k value may: not where an arity-1 set is required (4A.6); and, under (B) of the open **tuple-parts**, on the left of a binding as new names |

### 4A.9 What the account depends on

[§4C: REWRITTEN; every question it listed is answered except **tuple-parts**.] RULED and applied above: set-arity
(J3), modifier-lift (J8), unset-component and default-unused (J6), joint-loops (J7), record-is-product (J9),
colon-scope (J2, which also settles §13 C13 on the value side: `$dim`), first-rest PARKED (J4). The `$`-tuple refusal
over repeated labels (4A.4) is unaffected by any of them. STILL OPEN, with no user: **tuple-parts** (4A.3): no access
(A) or taking ONE tuple apart on the left of a binding (B1); nothing in the account depends on it, and first/rest
(4A.11), the only use found, is parked (`predicates_future.md` items 1 and 4).

### 4A.10 Corrections to this note's earlier text

- §2 (THE LEFT): "a positional record of label PATHS ... the record bracket ... in a fourth position" is restated in
  the owner's terms (R-1): a TUPLE OF REFERENCES, the colon its mark (4A.7). The meaning is unchanged.
- §2 (THE RIGHT) and §4 item 2 (d): "a 'tuple of values' is not a new value shape, it is a product of one-string
  sets": the VALUE is a set of tuples (4A.4); products are one producer among six, and `[(9, 0), (17, 30)]` or
  `>= (9, 0)` are not products. Item 2's two readings of the ruling are settled by 4A.1 (the second: a different
  thing that shares the bracket).
- §3 table, row "the tuple `(9, 0)`" ("Collides with 'a record is never a value' ... unless a product is ruled not to
  be a record") and §6 B1: the owner accepted the tuple as a value (CF:1362); 4A.1 gives why the ruling is untouched,
  and names the three draft LEAN sentences that move.
- §4 item 8 CENSUS ("the table grows from four `( )` rows to six"): the full census is 4A.7 (two new rows; the count
  of rows depends on whether heads and the left of `:=` are counted apart).
- §8 question 1 **tuple-value**: ANSWERED by the owner (CF:1362-1372); kept for the record, not re-asked.

Lane tupleval2 (2026-11-16), applying the owner's entries of 09:49 (sides of the binding sign; tuple-anywhere YES),
09:50 ("Yes" to taking apart), 09:52 (the first/rest idea) and 09:58 ("Nothing is set in stone", reaching the parts
reopened). Every changed sentence, marked "[§4A.10, tupleval2]" in place:

- HEADER: one sentence added naming this lane.
- §4A opening: the 09:49, 09:50, 09:52 and 09:58 entries quoted; the evidence paragraph names `tupleval2_check.py`.
- §4A.0: `(9, 0)[1]`'s comment now points to 4A.3 for parts; three example lines added (taking one tuple apart,
  marked OPEN; first and rest; taking a set apart, an error under (A) and under the lean (B1)).
- §4A.1, first paragraph: "Both are tuples in his words; only the right-hand one is a value" (it read his "right
  hand side" as right of the colon) becomes: the colon-less one is the value, on the right of a BINDING sign; its
  use on the left is the open **tuple-parts**.
- §4A.2, ARITY 0: one sentence added: first/rest does not need `()`.
- §4A.3: REWRITTEN. Lane tupleval's option table (a)-(f) and its LEAN ("a tuple VALUE is used whole ... (b) held as
  the route if a case needs it") are folded into two positions laid out fairly, (A) no access and (B) taking apart
  on the left of a binding with sub-choices (B1)-(B3); what the `[n]`/`.` rejection rests on; the lean (B1).
- §4A.4: ACCEPTED POSITIONS gain the left of `:=` under (B); ERRORS gain, under (B), the count mismatch and (lean
  (B1)) a value that is not one tuple; producer (4) gains a pointer to the first/rest alternative.
- §4A.6: the "component read" row's fix gains the (B) form; two rows added (taking apart, count mismatch).
- §4A.7: the `( x, y ) :=` row's meaning gains "a tuple taken apart under (B)"; the look-alike row `(a, b) := t` vs
  `((a, b): t)` no longer says "the first is not proposed" but gives both positions; the count paragraph gains two
  sentences (no new row for taking apart; what first/rest would add).
- §4A.8: (m4) "PARTLY WRONG" becomes OPEN (**tuple-parts**) with the owner's two entries; R-1 (ii) restated on the
  binding sign's sides; R-1 (iii) marked ANSWERED (tuple-anywhere).
- §4A.9: **tuple-parts** (reopened) and **first-rest** added.
- §4A.11: NEW, the first/rest idea worked; it depends on **tuple-parts** (B), and (B1) is enough.
- Goals (non-goals), §2 (COMPARISON SETS), §7 item 10: "no recursion" / "any-arity recursion (not needed)" each
  gain a pointer to 4A.11 (true of the built-in order; the idea is the alternative).
- §8: a current ranked list added (the older list kept for the record); **tuple-anywhere** answered;
  **tuple-parts** restated with both sides; **first-rest** added.

Lane unsetdef (2026-11-16), applying the owner's entries of 10:18 and 10:22 (first-rest: "Let's park first/rest but keep
it in the wings in case we find a problem that needs a different way of composing"), 10:26 (set-arity: "Set arity:
yes. It's clean. I like it"), 10:35 (unset-component, a LEAN: "I'm leaning to agree with you but want to work out the
middle ground. How could we do a 'default value'?"), 10:37 (the default's spelling: "Seeing = in examples I prefer
it") and the lane's rulings file R-1 (10:40, a question) and R-2 (10:43: a several-string default an error for now).
Tuple-anywhere (09:49, YES) was already applied by tupleval2. Every changed sentence, marked "[§4A.10, unsetdef]" in
place:

- HEADER: one sentence added naming this lane and §4B.
- Goals (non-goals), §2 (COMPARISON SETS), §4A.7 (count paragraph), §7 item 10: each first/rest pointer gains
  "PARKED".
- §2 (MEANING PER MATCH): "a joint condition on a match with an unset label FAILS" gains: the owner's LEAN, not
  closed; an author-written default at the label, §4B.
- §2 (what it costs, N2) and §3 ("Counted", "one decision ... **tuple-value**"): marked settled (tuple-value answered,
  set-arity RULED).
- §3 table, row "unset fields": gains "an opt-in default at the label, §4B".
- §4 item 3: "The lane leans ARITY (owner question **set-arity**)" becomes "The lane leaned ARITY; RULED by the owner".
- §4 item 6: the owner's 10:35 lean quoted and the default (§4B) given as the middle ground.
- §4A.2: "The rule holds under either answer to **set-arity**" gains: RULED, ARITY.
- §4A.3 (LEAN paragraph): gains "with first/rest PARKED, **tuple-parts** has NO USER: open, nothing built, (A) in
  practice".
- §4A.4: "under **set-arity** either ... the answers below are the same" becomes "**set-arity** RULED: one set kind";
  producer (4)'s "question **first-rest**; this producer stands until he answers" becomes "PARKED: this producer is
  the design".
- §4A.9: **set-arity** RULED; **unset-component** the owner's lean plus §4B; **tuple-parts** no user; **first-rest**
  ANSWERED, PARKED.
- §4A.11: title "NOT a ruling" becomes "PARKED"; a paragraph added quoting 10:18 and 10:22 with the trigger; the
  verdict's "Owner question **first-rest**" marked answered. The worked account below it is unchanged.
- §4B: NEW, the default for an absent label (examples, definition, the unfold, one concept with head defaults, the
  `=` census, look-alikes, problems tried, the several-string record and the owner's `some(...)` idea).
- §5 problem 7 and the tally: with the default, 7 is SIMPLER (simpler 7, same 6, worse 0).
- §6 B2: the default as the author's route to `10` in; rev 18's answer is the EVERY reading (§4B.6).
- §7 item 8: "unless the author gives the label a default".
- §8: REWRITTEN to what is still open (the answered questions listed with his words; the earlier lists are in git at
  c69929e4a and in `docs/dev/lanes/tupleval2_report.md`).

### 4A.11 First and rest with recursion (the owner's idea, worked; PARKED)

[§4A.10, unsetdef] PARKED by the owner (10:22), his words: "Let's park first/rest but keep it in the wings in case we
find a problem that needs a different way of composing" (after 10:18: "I think the tuple mechanism as otherwise
described handled the problem more simply which I like"). TRIGGER, in his terms: a problem that needs a different way
of composing over a tuple's parts than the language gives. Kept on record below, unchanged.

It DEPENDS on **tuple-parts** (4A.3): it needs position (B), and (B1) is enough. His words (09:52): "I don't know if this helps but an idea I had last night was functional style first/ rest binding
with recursion". Everything in this subsection is the LANE'S working of an idea; nothing is ruled. Spellings
(`r...`, the names) are placeholders.

    (y, md...) := (2024, 2, 29)              # y = 2024; md = (2, 29): the REST, the remaining entries
    (m, d...) := (2, 29)                     # d = 29: the rest of a pair is its plain second entry ((x) is x, 4A.2)
    (2023, md...)                            # the value side: a tuple from a first and a rest, (2023, 2, 29)

    anything := /[\s\S]*/                    # an existing rx: every string
    all((b, r...)) := (anything, all(r)...)  # every tuple of the argument's arity; clauses tried in order,
    all(b)         := anything               #   the first whose HEAD fits the argument
    ge((b, r...))  := (> b, all(r)...) | (== b, ge(r)...)
    ge(b)          := >= b                   # base case: a plain value (arity 1)
    gt((b, r...))  := (> b, all(r)...) | (== b, gt(r)...)
    gt(b)          := > b
    le, lt                                   # the same with `<` and `<=`
    between(lo, hi) := ge(lo) & le(hi)       # the existing macro, unchanged

    t & ((h, m): padded_ge((9, 30)))         # a time at or after 9:30 (a variant writing padded(...) per component)
    ip & ((a, b, c, d): between((10, 1, 128, 0), (10, 1, 131, 255)))   # four fields: no size literal, no index
    span & ((eh, em): gt(($sh, $sm)))        # a per-match pair taken apart: one tuple per match
    t & ((h, m): >= (9, 30))                 # ERROR in this design: a comparison takes ONE value; "write ge((9, 30))"

THE EXPANSION, by hand, of `ge((1, 4, 0))`: the tuple clause gives `(> 1, all((4, 0))...) | (== 1, ge((4, 0))...)`;
`all((4, 0))` is `(anything, anything)`; `ge((4, 0))` is `(> 4, anything) | (== 4, >= 0)` (its rest `0` is plain, so
`ge(0)` is the base clause). Result: `(> 1, anything, anything) | (== 1, > 4, anything) | (== 1, == 4, >= 0)`: the
three rows of §4 item 7's expansion, from no rule about tuples at all.

EVIDENCE, table (F): the clauses above run by a small interpreter that follows them as written (first-match by head
shape, the rest of a pair plain, the value-side rest a product), each result turned into a regex and laid over a
dotted-numeral operand; expectation: Python's integer tuple order on the parsed fields. k = 2 (225 subjects), 3 (512),
4 (1,296); at-least, strictly-greater, at-most, strictly-less at 4-5 bounds each and between at 2-3 ranges: 40,279
cases; plus `padded` written per component at k = 2 (two-digit subjects), 1,800 cases. 0 differ, 0 engine
disagreements. Rows per order: exactly k (the built-in expansion's count).

WHAT THE IDEA NEEDS (the price, each NEW unless marked):

| # | piece | why | relation to the draft |
|---|---|---|---|
| P1 | a REST MARK on the left of a binding, `(b, r...)`: `r` is the remaining entries (one or more), a tuple when two or more, the plain value when one | the recursion's step | new mark; position (B) of **tuple-parts** (4A.3), held to (B1), plus one mark |
| P2 | the same mark on the value side, `(x, r...)`: the product of x with r's components | building the result | the same mark, one meaning ("the remaining entries"), the binding sign's side saying names or values, as for the tuple itself (R-2) |
| P3 | a tuple of names in a DEFINITION HEAD | §5.2 heads declare names and defaults; a body has no local bindings, so a definition can take its argument apart nowhere else | (B)'s form (a head is the left of `:=`) in a new place |
| P4 | SEVERAL CLAUSES for one name, chosen by the head's SHAPE, first match: a tuple head fits arity >= 2, a plain head fits anything | the base case | the open §13 O21 (`predicates_draft.md:3817`: "several definitions of one name by literal argument") generalised; the lane's: one first-match form would serve E-DEPTH's literal heads AND first/rest's shape heads |
| P5 | TERMINATION by arity: a recursive call takes the REST its head bound | G4 (`predicates_draft.md:477`): structural evaluation total and terminating | §7 admits recursion only by "ONE integer parameter ... a literal at every call ... STRICTLY DECREASES" (`predicates_draft.md:2192-2195`, RULED CF:583). The arity is a compile-time natural fixed after expansion and drops by one per call: the same kind of syntactic check with another measure; the rule gains one clause |

NOT NEEDED: an empty tuple (the base case is the plain clause; 4A.2's `()` stays an error); a size literal; an
index; arithmetic in an index. Rev 18's any-n form `lg(j, n, s, lo)` waits on O21 AND "compile-time ARITHMETIC ON A
LITERAL PARAMETER INSIDE AN INDEX (`s[n-j+1]`)" (`predicates_draft.md:2620-2634`; §13 O69 (3)); first/rest needs
O21's several-clauses half only, by shape. "Any value" for the remaining fields is the existing `anything` and the
library's own `all`, no new concept. O69 (3)'s trigger names "a real use with four or more fields": the CIDR block
list of table (R) is one (the lane's observation).

THE SLIPS, table (FS) (the three ways to write the library wrong, each run): the plain clause listed first (it then
catches tuples and builds `>= (1, 2)`): REFUSED at k = 2, 3, 4 (a comparison takes one value); the rest used without
the mark (`(== b, ge(r))`): REFUSED at k = 3, 4 (a nested tuple entry, 4A.2), and at k = 2 ACCEPTED with the same
answer (the rest of a pair is plain, so the mark changes nothing); a recursive call on the whole instead of the rest:
REFUSED at k = 2, 3, 4 (P5). No slip gives a silent different answer.

COMPARED with the built-in order (4A.4 producer (4); §2 COMPARISON SETS):

| | built-in: `>= (9, 30)` | first/rest library: `ge((9, 30))` |
|---|---|---|
| new concepts | ONE: a tuple atom in a comparison set, read in dictionary order (§2.4's ONE ATOM read per component) | FIVE (P1-P5; P4, P5 widen an open and a ruled draft item), minus the built-in's one |
| any number of fields | native | native |
| names | none | six library names (`all`, `ge`, `gt`, `le`, `lt`, `between`, the last existing) |
| the two-orders look-alike: `>= (9, 30)` vs `(>= 9, >= 30)`, 2,700 of 11,000 `t` subjects differ padded (table (O)) [§4F] | both legal, different, told apart by the operator's place (RULED, J5, CF 11:20) [§4C] | GONE: `>= (9, 30)` is an error naming `ge`; dictionary order is a NAME, the product order the bracket |
| `padded` components | modifier-lift (RULED, J8) [§4C] | the library writes `padded` into each component it builds (table (F), 1,800 cases); modifier-lift still needed for `padded(open_at)` |
| reader slips | the two-orders slip is silent; `>= [9, 0]` an arity error | a user's `>= (9, 30)` is an error; an author's slips are refused (FS) |
| G4 | nothing to check | P5 |
| taking a set apart | not involved | first/rest NEEDS taking apart: under (A) of **tuple-parts** it cannot be written; (B1), one tuple only, is ENOUGH (every bound is one tuple: a literal tuple, or `($sh, $sm)`, one per match); a head given a set (`ge(month_days)`) is refused under (B1) exactly as a statement is: one rule |

WHAT ELSE IN THE §12 PROGRAMS IT SERVES (the lane's survey): the tuple compares at any arity (times, versions, dates,
IP ranges and CIDR lists: problems 1-3, 5-8 of §5) and small any-arity library helpers (`all`, an equality `eq`, a
padded variant). NOT served: E-DEPTH (it recurses on a depth number, not a tuple; it shares P4 only); E-LUHN (its
digits are a repeated label's ITERATIONS, per match, outside G4's compile-time structure: first/rest walks spelled
tuples, never a match's iterations); E-CAL (a declared table, no recursion); E-IPV4's octet validity (`join` over an
array already); E-WEEKDAY, E-RFC, E-NEAR (functions of fields: computed labels, §4.4); E-JSONL, E-FILE, E-HTTP,
E-SEP, E-CTX (no several-field value). First/rest over an ARRAY's entries would be a second structural route beside
`each` and `[n]`: not proposed (trigger: a recursion over entries `each` cannot write).

VERDICT (the lane's): HELPS AT A NAMED PRICE. It is the general form the draft's any-arity item was waiting for,
with fewer prerequisites (no index arithmetic, no size literal, no empty tuple), it turns dictionary order from a
language rule into a library definition, and it removes the one census pair that is neither the same answer nor
an error (two-orders). The price is five pieces against the built-in's one, for ONE family (the orders) that the
built-in already covers at any arity; no second any-arity tuple family appears in the §12 programs. Under the
owner's criteria in order (in line with existing concepts first; then the larger language), the built-in wins the
first and first/rest the second only through the two-orders look-alike. LEAN: keep the built-in order now; record
first/rest as worked and tested, TRIGGER: a second any-arity tuple family the built-in cannot express (a tuple
relation other than order, or per-component modifiers a library must choose). If the owner weighs the two-orders
look-alike above the concept count, first/rest is the clean way to remove it. Owner question **first-rest**
[§4A.10, unsetdef: answered, PARKED].

## 4B. A default for an absent label

Lane unsetdef, 2026-11-16, design only. The owner's words, in order: on **unset-component** (10:35), "I'm leaning to
agree with you but want to work out the middle ground. How could we do a 'default value'?"; shown a sketch, "If we
had the operator |= 'or equals' we could use it as for default macro arguments"; on the spelling (10:37), "I was
thinking = but had your concerns. Seeing = in examples I prefer it"; on what the value is (10:40, rulings R-1, a
question), "Also, the m = x there means the x is an rx. I don't have an intuitive sense of what that means"; and
(10:43, rulings R-2, a ruling for now) "We can punt, as you say, and throw an error. Perhaps a reason will open to
reconsider. Then there is a = some(between(...))". Then (11:05) RULED, J6: "unset-component: yes" (a condition
naming an unset label FAILS unless the author wrote a default; `predicates_draft.md:1590-1592`, §4.2, for any number
of labels) and "default-unused: agree" (a never-used default is a WARNING: the manager's reading of "agree"); and
(11:32) the default's scope, J2: "(a, b = c): ... the 'c' is a binding et al" [§4C].
The default is OPT-IN, written by the author at the label; the language never presumes one. Spellings are
placeholders (D193 add. 4). Every sentence not quoted or cited is the LANE'S. Evidence:
`docs/dev/lanes/unsetdef_check.py` / `.out` (`timeout 120 python3 -I docs/dev/lanes/unsetdef_check.py`; libpcre2-8
10.46 and Python 3.14.4 `re` on every case; expectations from the subject split by Python string code, an absent
field given the default's TEXT, Python integer tuple order, never from the unfolded regex under test): 233,720
cases, 0 differ, 0 engine disagreements; tables (DF), (DG), (DN), (D1), (DS), (DV), (DD), (DL), (DA), (DC), (DK),
(DE). SABOTAGED once (`UNSETDEF_SABOTAGE=1`: the slice built at m = 30 instead of the default 0): 168 differ, so the
check can fail.

### 4B.0 Examples first

    t2 := /(?<h>\d{1,2})(?::(?<m>\d\d))?/                     # minutes optional
    t2 & ((h, m = 0): padded(between((9, 30), (11, 0))))      # absent minutes read as 0: 10 IN, 11 IN, 9 out
    t2 & (m = 0: <30)                                         # one label: an absent m passes ("0" is < 30)
    t3 := /(?<h>\d{1,2})(?::(?<m>\d\d)(?::(?<s>\d\d))?)?/
    t3 & ((h, m = 0, s = 0): padded(>= (9, 0, 30)))           # several defaults in one bracket
    semver2 := /(?<major>\d+)\.(?<minor>\d+)(?:\.(?<patch>\d+))?/
    semver2 & ((major, minor, patch = 0): >= (1, 4, 2))       # 1.4 read as 1.4.0: out; 1.5 in
    noon := 12
    t2 & ((h = noon, m): ...)                                 # a binding of ONE string: legal
    span & ((eh, em = $sm): ...)                              # a `$` value of an always-set label: legal
    t2 & ((h, m = between(0, 59)): R)                         # ERROR (R-2): a default is ONE string
    t2 & ((h, m = $x): R)          with x optional            # ERROR: the default could itself be absent
    t2 & ((h, m): R = 0)                                      # ERROR: a default is written at the label
    t  & ((h, m = 0): R)           with m required            # WARNING default.unused: m is never absent

READ `m = 0` AS "as if the minutes text were `0`" (the plain reading R-1 asks for). Every value in the language is a
set of strings (an rx, §2.1), and a literal is the one-string set (`predicates_draft.md:853-854`). A label's value in
ONE match is ONE string. So a label's default stands in for one string, and must be a one-string set: the literal
`0` is the set {"0"}, and the default is its one member, laid where the missing text would have been.

### 4B.1 The definition

FORM. In a condition entry, a name on the LEFT of `:` may carry `= v`: `(m = v: S)`, `((h, m = v): R)`, and in a
record `(h: S, m = v: T)`. Inside the entry `&` and `|` bind tighter than `=` and `:` (§4.1's entry extent), so
`(m = 0 | 5: S)` reads `m = (0 | 5)`: a two-string default, an error (below).

MEANING (one sentence). In a match where the label is UNSET (§4.2: its group or loop never reached), the condition
reads the default's text in its place; where the label is set, the default is never read. Everything else (the set
it is tested against, `padded`, the comparison rules, the lift to tuples) is unchanged: the default is compared
exactly as a captured text would be.

WHAT v MAY BE (RULED for now, R-2: "We can punt, as you say, and throw an error"): ONE STRING, i.e. a one-string set:

| v | verdict | why |
|---|---|---|
| a literal `0`, `"M"` | legal | the one-string set |
| a binding of one string (`noon := 12`, `m = noon`) | legal | a binding names whatever its expression is (§2.1) |
| a `$` value of a SET-ONCE label that is SET IN EVERY MATCH (`em = $sm`), or of a computed label (`$d`) | legal; the condition is then a §4.6 relation, priced by class count | one string per match (§5.4 `$` row) |
| a `$` value of a label that CAN be unset | ERROR: "the default `$x` can itself be absent; give a literal" | no chains of defaults (no case; D77) |
| a `$` value of a REPEATED label | ERROR (the existing bare-`$` error, `predicates_draft.md:1632-1634`) | many strings |
| a set of several strings (`between(0, 59)`, `0 \| 30`, `/\d\d/`) | ERROR (R-2); text below | a label holds one string; "any of these" has two readings (4B.6) |
| a tuple, a condition, a macro | ERROR: "a label's default is one string" | arity, kind |
| a bare LABEL name (`(h, m = h): R`, h a label, no binding h) | ERROR: "`h` here is a binding (a default is on the value side); for the label's value write `$h`" | J2's refinement (CF 11:32): the default is on the value side, where a bare name is a binding [§4C] |
| a bare name that is BOTH a binding and a label (a binding `h := 7` and a label h) | the BINDING (7) | J2: on the value side a bare name is always a binding; no shadowing question arises, the position decides [§4C] |

THE ERROR for a several-string default (wording illustrative, D26): "`m = between(0, 59)`: a default stands in for
ONE missing text, and this set holds 60. Give one value (`m = 0`); or, if an absent m should not matter, add an
alternative that leaves m out: `... | (h: S)`."

WHERE `= v` MAY STAND: only on a name left of `:` in a condition entry. Elsewhere an error with its fix: on the right
(`((h, m): R = 0)`: "a default is written at the label: `(h, m = 0)`"), inside `$` (`$m = 0`: "`$` reads a value; a
default is written at the label"). A PATH may carry one (`(d.year = 0: S)`: the path names one label).

COMPILE-TIME DIAGNOSTICS (texts illustrative; the names are the spelling step's):
- `default.unused`, a WARNING (RULED, J6, CF 11:05: "default-unused: agree", WARNING the manager's reading of
  "agree"; as `dead.branch` is a warning: the answers do not change) [§4C]: (a) the label is set in every
  match of its pattern (`t & ((h, m = 0): R)`, m required: identical answers to no default on 11,000 of 11,000
  subjects, table (D1)); (b) the default never admits: the slice at the default is EMPTY (`(m = 45: <30)`: identical
  on 11,110 of 11,110, table (D1); `(m = 00: <30)`: `00` is not a canonical numeral, so it lies outside `<30`, the same
  11,110 of 11,110). With a tuple set the slice is taken through every component's domain (J4, DOM): `((h, m = 00):
  >= (9, 0))` slices to EMPTY and draws the warning (table (DM): 0 h texts in the slice; the other reading would give
  90 and no warning) [§4F, DICT-DOMAIN]. Decidable for a constant set and a literal default; not issued for a `$` default.
- `label.unset` (EXISTING, §4.2, its text extended for conditions that can take a default): "m can be unset in a
  match of t2 (the optional group `(?::(?<m>\d\d))?`); the condition `((h, m): ...)` then FAILS. To read an absent m
  as a value, write `((h, m = 0): ...)`; to accept whatever m would be, add an alternative without m: `... | (h:
  S)`." It names BOTH fixes; with a default on m it is not issued for m.

THE CASES THE BRIEF NAMES, each:

| case | answer | evidence |
|---|---|---|
| single label `(m = 0: <30)` | holds on a match with m unset exactly when "0" is in the set; so a single-label default is a compile-time choice between "an absent m passes" and "fails" (the latter draws `default.unused`) | (D1): `(m = 0: <30)` differs from no default on the 110 minutes-absent subjects only |
| a label that can never be unset | WARNING `default.unused` (a); an error would refuse a library condition laid over several patterns, some with the field optional | (D1) 11,000 of 11,000 identical |
| a LOOPED label | per ITERATION: an iteration whose item skipped the label reads the default (`list & ((h, m = 0): R)` with `(?::(?<m>\d\d))?` in the item). ZERO ITERATIONS of a reached loop are NOT unset (`predicates_draft.md:554`, L56; `:563`, L65): the looped part is EMPTY, which satisfies any set (J7, CF 12:45), and the default is never read [§4E: was "there is no tuple, the plain condition HOLDS over none"]; a label OUTSIDE the loop is still tested (J7). A loop NEVER REACHED leaves its labels unset: the default is read as for a set-once label (the lane's reading: one tuple with the default; TESTED by lane jcfold2, table (ZD) b [§4E: was UNTESTED]). "Never reached" is §4.2's (`predicates_draft.md:1598-1605`): the deepest construct the match entered on the way to the label is not a loop that ran zero times; so a label in an inner loop whose OUTER loop ran zero passes has zero passes, not unset, and its default is NOT read: `/(?<c>\d)(?:;(?<h>\d)(?::(?<k>\d))*)*/ & (c: 3..7, k = 9: <5)` on `5` HOLDS (by §4.2 and J7, derived, not run; read literally, "the inner loop was never reached" would read 9 and FAIL) [§4F, SIM-2]. A pass of an enclosing loop that skips the label's loop: open, **pairing-loop** (3), §8 [§4F] | (DL) 585 lists, 0 differ; the empty list HOLDS; (ZD) a, c: a looped default on zero passes unread, the empty list HOLDS [§4E] |
| a COMPUTED label (`mnum := $mname.index`) | the lane's reading of §4.4 (which is silent): a computed label is UNSET in a match where a label it reads is unset; its default then stands in (`((year, mnum = 1): >= (2024, 3))`: `2024` out, `2025` in) | (DC) 65 subjects, 0 differ |
| unset because another ALTERNATIVE was taken (`/(?<h>\d{1,2})(?::(?<m>\d\d)\| o'clock)/`) | the same as an optional skipped (§4.2: never reached) | (DA) 11,110, 0 differ |
| SEVERAL defaults in one bracket | each absent label reads its own default; the unfold has one branch per REACHABLE combination of absent labels (3 of 4 for `t3`: s cannot be present without m) | (DS) 4,206 subjects, 0 differ |
| `padded` and modifier-lift | the default is compared AS WRITTEN, through the same set as a captured text: under `padded(...)` `m = 0` and `m = 00` both read as zero; without it `00` is not canonical and fails (`(m = 00: <30)`, table (D1)). No rule of its own; **modifier-lift** is unchanged | (DF), (D1) |

### 4B.2 Under the hood: the unfold

THE CLAIM (the manager's sketch, s2): `P & ((h, m = v): R)` unfolds statically to
`P & (((h, m): R) | (m unset & (h: R at m = v)))`, the SLICE of R at the default.

- THE SLICE IS A REGULAR SET AT THE DEFAULT LEVEL. A constant tuple set is a finite union of products (§4A.4); its
  slice at a constant text is the union of the first components of the rows whose m-component holds the text: again
  a finite union of products of regular sets. For `padded(between((9, 30), (11, 0)))`: 3 rows; at m = "0" the slice
  has 2 rows, {10} and {11} (table (DF)). Several defaults slice in turn (3 / 2 / 1 rows in (DS)). With a `$`
  default the slice reads a value of the match: a §4.6 relation, priced by class count, as any `$` bound.
- "m unset" IS NO NEW MACHINERY: §4.2 already decides per match whether m's group was reached (a condition naming an
  unset label fails), so the automaton already splits the pattern at the optional group; the default gives the
  unset branch a condition instead of failure.
- THE GUARD IS ESSENTIAL, and it is not a user form today. Without "m unset" the slice also admits a PRESENT m:
  `((h, m): R) | (h: 10 | 11)` accepts `11:45` (11:45 is past 11:00, but h = 11 is in the slice): 99 of 11,110
  subjects differ from the default (table (DG)); `between((1, 4, 0), (1, 9, 9))` on versions: 3 of 728 (`1.9.10` ...,
  table (DV)). An author can write the guard only as `!(m: /[\s\S]*/)` (true exactly when m is unset), which rests on
  §4.2's LEAN half "its `!` true" (`predicates_draft.md:1590`) and the open §13 O28 (`:1618-1619`). The default needs neither:
  the compiler makes the split. This is the strongest case FOR the default (the lane's): its hand spelling is either
  wrong (no guard) or rests on an open question.
- WHEN THE GUARD IS NOT NEEDED (the lane's derivation, checked): if the default is the field's MINIMUM and R is
  closed upward in that field (every `>=`/`>` bound), the unguarded slice is exact (table (DV): `>= (1, 4, 2)`,
  `>= (1, 4, 0)`, 0 of 728 differ); an upper bound breaks it.

### 4B.3 One concept with macro-head defaults

THE SINGLE RULE: **in a list of names, `name = v` supplies the value when none is given.** A definition head lists a
macro's parameters; a call may give none for `min`, and `min = 0` supplies it (`occurrences(x, min = 0) :=`,
`predicates_draft.md:1936-1938`, §5.2; the `=` row of §5.4, `:2017`). The left of a condition's colon lists the operand's labels; a match may give
none for `m`, and `m = 0` supplies it. WHAT v MAY BE follows from what normally fills the name, with no second rule:
a parameter takes ANY value (§5.2), so a head default is any value (an rx, a macro, a tuple); a label holds ONE STRING
per match, so a label default is one string (R-2). This is the owner's 10:35 idea ("we could use it as for default
macro arguments") in the spelling he preferred at 10:37.

THE `=` CENSUS after the addition (every position; one meaning, "this name, with this value"; the list it stands in
says whether the value is GIVEN or a FALLBACK):

| position | example | the name | the value is | status |
|---|---|---|---|---|
| an entry of `[ ]` | `[year = /\d{4}/, ...]` | a LABEL the entry gets | the entry (given) | existing (§5.4 `=` row) |
| an argument of a call | `join(a, sep = ".")` | a PARAMETER | its argument (given) | existing |
| a definition head | `occurrences(x, min = 0) :=` | a PARAMETER | the fallback when a call gives none | existing |
| a name left of `:` in a condition | `((h, m = 0): R)`, `(m = 0: S)`, `(h: S, m = 0: T)` | a LABEL of the operand | the fallback when a match gives none | NEW |
| a record in value position | `(x = 1, y = 2)` | — | ERROR (L43, `predicates_draft.md:541`, unchanged) | existing |
| `:=` | `lo := (9, 0)` | (a different mark: binding) | — | existing |

The two lists that take a fallback are the two that DECLARE or NAME what something else will fill (a head, the left
of a colon); the two that take a given value SUPPLY it (an array, a call). No `=` position changes meaning; one is
added. `|=` is not adopted (10:37).

### 4B.4 Look-alikes and errors

Counts over the `t2` population (11,110 subjects: h in 110 one- and two-digit texts, minutes absent or `00`..`99`),
R = `padded(between((9, 30), (11, 0)))`:

| look-alike of `t2 & ((h, m = 0): R)` | answer | diagnostic |
|---|---|---|
| `t2 & ((h, m: 0): R)` | COMPILE ERROR, every program of the shape | NEW text: "a reference list holds label names; a default is `m = 0`" |
| `t2 & (h, m: 0)` | COMPILE ERROR (an entry `h` without `:`, item 1's spelling note) | existing |
| `t2 & (h, m = 0): R` (no outer brackets) | COMPILE ERROR (`:` outside a record, §4.1) | existing |
| `t2 & (h: 10, m = 0)` | COMPILE ERROR | NEW text: "the entry `m = 0` has no set; a default is written left of `:` (`m = 0: S`); to constrain m write `m: 0`" |
| `t2 & [m = 0]` (an array) | LEGAL, DIFFERENT: an alternation of ONE entry, `0` labelled m, intersected with t2: admits only `0`; differs on 244 of 11,110 (table (DK)) | lane's proposal (NOT RULED): WARNING `label.both_sides` ("both operands of `&` define m; the array's entry `m = 0` NAMES a label, it is not a default"), keyed off two operands of one `&` defining one label name, which no case needs [§4F: was named `label.twice`, which collides with the owner's **label-twice** ruling (CF 13:16, an ERROR, a different concept)] |
| `((h, f(m = 0)): R)` (a call on the left) | COMPILE ERROR (the left holds label paths, never an expression, §4.1) | existing |
| `t2 & ((h, m): office_hours(m = 0))` | COMPILE ERROR ("office_hours has no parameter m"; a binding without a head takes no arguments); with a macro that HAS a parameter m, legal and unrelated (a parameter, not the label) | existing |
| `t2 & ((h, m): R) \| ...(h: 10 \| 11)` by hand, no guard | LEGAL, DIFFERENT on 99 of 11,110 (table (DG)) | none possible (two legal programs); `label.unset`'s text names the default as the fix |
| `t2 & ((h, m): R)` (no default) | LEGAL, DIFFERENT on 2 (`10`, `11`: table (DN)) | `label.unset` (existing), naming both fixes |
| `t2 & (((h, m): R) \| (h: 10))` ("don't care", below) | LEGAL, DIFFERENT on 1 (`11`: table (DN)) | none: a different meaning, on purpose |

TWO MEANINGS OF A MISSING FIELD. (1) "It MEANS a specific value": a version `1.4` is `1.4.0`, an hour `10` is
`10:00`: the default. (2) "It DOES NOT MATTER": the author's explicit alternative that leaves the field out,
`| (h: 10)`, or for a date without a day, a month-level condition. They give different answers, and the default
cannot replace the alternative: on `2024-MM` against 2024-02-15..2024-04-01, "does not matter" (the month overlaps
the range) admits `02`, `03`, `04`, and EVERY default day 1..31 misses one of them (the best differs on 1 of 12
months, table (DD): `d = 1` misses `02`, `d = 31` misses `04`). On the time example the alternative `| (h: 10)`
says `11` is out (an hour of 11, minutes unknown, is mostly past 11:00); the default `m = 0` says `11` is in.

### 4B.5 Problems tried

| problem | with the default | vs without | verdict |
|---|---|---|---|
| §5 problem 7, OPTIONAL SECONDS (the one that got WORSE) | `((h, m, s = 0): padded(>= (9, 0, 30)))`: one condition | §5's `((h, m): padded(> (9, 0))) \| ((h, m, s): padded(>= (9, 0, 30)))` gives the same answers WHEN MINUTES ARE REQUIRED (it is the slice written by hand, and `>=` needs no guard, 4B.2); with minutes optional too (`t3`, `m = 0, s = 0`) it differs on 2 (`10`, `11`), the default on 0 (table (DS)) | WORSE -> SIMPLER |
| OPTIONAL MINUTES | `((h, m = 0): padded(between((9, 30), (11, 0))))` | needs a hand slice plus a guard (4B.2); the alternative `\| (h: 10)` means "does not matter", a different answer on `11` | SIMPLER |
| A VERSION WITHOUT A PATCH, `1.4` as `1.4.0` | `((major, minor, patch = 0): >= (1, 4, 2))` | for `>=` bounds a hand alternative `\| ((major, minor): > (1, 4))` is exact (no guard needed) but is the slice computed by the author; for `between` the hand form without a guard is wrong on 3 of 728 (table (DV)) | SIMPLER |
| A DATE WITHOUT A DAY ("does not matter") | not the tool: no default day gives the month-overlap answer (table (DD)) | the author splits the pattern (`ymd & (...) \| ym & ((year, month): between((2024, 2), (2024, 4)))`), as today | SAME |
| §12 cases with an optional field | none: the twelve programs' one `)?` is E-DEPTH's JSON array body, which holds no label (`predicates_draft.md:3545`; `sed -n '3214,3600p' docs/design/predicates_draft.md \| grep -c ')?'` = 2, the other a prose `)?`) | — | none to try |

Tally: simpler 3, same 1, worse 0. §5's tally moves from "worse 1 (7)" to simpler (§5 updated, [§4A.10, unsetdef]).

### 4B.6 A several-string default: the record of why it is an error (R-1, R-2)

The owner asked what `m = x` means when x is an rx (R-1). A label default of SEVERAL strings has two readings, both
regular (the intersection or the union of the slices at each member), worked on the time example with
`m = any \d\d` (table (DE), 110 minutes-absent subjects per range):

| range | EVERY member fits (the intersection) | SOME member fits (the union) | EVERY vs rev 18's decided-prefix order (table (W), §8 caveat (5)) |
|---|---|---|---|
| `between((9, 30), (11, 0))` | `10` | `9`, `10`, `11` | SAME (0 differ): rev 18's `10` in, `9` and `11` out |
| `between((9, 0), (10, 0))` | `9` | `9`, `10` | differs on 2 (`9`, `09`): the lower bound's minutes are 0, so every minute fits; decided-prefix reads the absent field and rejects |
| `>= (9, 30)` | `10`, `11`, `12` | `9` .. `12` | SAME |

So EVERY reproduces table (W) on the owner's example, but not in general (it differs where a bound's later field is
the field's floor). Two findings decide nothing but record why the error is safe (the lane's): (1) EVERY's hand
spelling needs NO guard (if every m fits, a present m fits too: 0 differ on all five ranges tried, table (DE)), so
"does not matter, strictly" is already writable as the alternative `| (h: 10)`; (2) SOME's hand spelling DOES need the
guard (40 to 159 differ without it, table (DE)), and SOME over every day is exactly the date's "does not matter"
(table (DE): `02`, `03`, `04`). RULED for now (R-2): a several-string default is a COMPILE ERROR (text in 4B.1).

HIS IDEA `m = some(between(...))` (R-2, NOT ruled): the author names the reading with the quantifier word. The words
exist: `some(...)` and `all(...)` are the GROUP QUESTIONS (§4.3; `predicates_draft.md:534`, L36: `all(...)` the
default; `:552`, L54), and they take a CONDITION and quantify over the ITERATIONS of a repeated label. L54 withdrew
rev 7's `some(s)` on a SET ("Rev 7's three spellings of 'some result' (`x & s`, `some(s)`, `occurs.some`) become one",
`:552`): membership in a set is already "any one member" under `&`. So `some(between(...))` would be the same word
with a new argument KIND (a set, not a condition), quantifying over a new domain (a set's members, not a label's
iterations), in a new position (a default). The meanings rhyme ("some one of several") and the owner's "an array of X
is an X" makes a set's members and a label's iterations both entries of an array interface (the lane's), but it
reopens L54's withdrawal. NOT PROPOSED NOW. TRIGGER (R-2's): a problem where a missing field means "any of these" or "does
not matter" and the pattern cannot be split by hand (the date case CAN be split). With it, the error text would add: "for 'some value
of m', write `m = some(...)`".

### 4B.7 What the default does NOT change

- The base rule: without a default, a condition naming an unset label FAILS (RULED, J6, CF 11:05) [§4C].
- No value-level "or else" (s5): every case tried puts the fallback at a condition's label; a computed label that
  READS an unset label is itself unset and takes ITS default (table (DC)). A value-level `$m else 0` INSIDE a computed
  label's formula (`total := $h * 60 + ($m else 0)`) has no §12 or §5 example: NOT PROPOSED (D77); trigger: a
  computed label that must read one absent input while the others are present.
- §13 O28 (`!(x: S)` vs `(x: !S)` on an unset label): untouched; a default makes the label "present" for that
  condition only, so `((h, m = 0): !R)` reads `(h, 0)` against `!R`.
- Group questions: `count(((h, m = 0): R))` counts the iterations whose tuple, with the default read, is in R.

## 4C. Corrections by lane jcfold (the entries of 11:05-11:35)

Lane jcfold (2026-11-16), applying the owner's entries of 11:05 (unset-component: "unset-component: yes";
default-unused: "default-unused: agree"), 11:17 (joint-loops: "I agree. Makes sense."), 11:20 (two-orders: "I agree.
They look sufficiently different to me and I like the control."), 11:27 (modifier-lift: "modifier-lift: yes. Add this
as another item like first/last to a 'predicate future consideration' document to consider finer grain transforms.
However the form is 'do everything to both' so the logic makes sense"), 11:32 (colon-scope: "colon-scope: yes with
refinement: (a, b = c): ... the 'c' is a binding et al") and 11:35 (record-is-product: "record-is-product:
absolutely. This is precisely the sort of simplifying semantics I'm looking for."). Rulings file
`jcfold_rulings.md`: empty at every read. Every changed sentence, marked "[§4C]" in place:

- TITLE and HEADER: "(EXPLORATION)" becomes "(RULED)"; the STATUS paragraph REWRITTEN (all questions answered,
  tuple-parts open with no user, the lane list, the §4C/§4D/§9 pointers, the three contradictions in §8, the
  `CF hh:mm` convention); the evidence paragraph gains the re-run of `jointexp_check.py` and `jcfold_check.py`.
- Goals: the non-goal "any-arity recursion (not needed ...) [two bracketed notes]" becomes one sentence (the built-in
  order serves any k; first/rest parked, `predicates_future.md` item 1). Standing question (2) names the later
  scripts and their sabotage runs.
- §1: four example lines added (the default, a record as the product case, the per-part form).
- §2: REWRITTEN as J1-J9, each ruled point stated ONCE with the owner's words and its CF time; the exploration's
  bullets ("THE LEFT ... a fourth position", "THE RIGHT ... NEW", "COMPARISON SETS", "MEANING PER MATCH ... (§4.2
  lifted) [unset: the owner's LEAN]", "THE RECORD IS THE PRODUCT CASE ... (lane's)", "LEVEL ... at most 2k - 1"
  UNTESTED) are replaced by J1 (form), J2 (colon scope), J3 (value, arity), J4 (order), J5 (two orders), J6 (unset,
  default), J7 (loops), J8 (modifiers), J9 (record), LEVEL (now tested, (RC), (SE)); "What it costs (N1)-(N4)" gains
  (N5), the default, and the order sentence, and loses "meets the RULED 'a record is never a value' head on" (settled,
  §4A.1).
- §3: the table REWRITTEN with a "ruling" column entry per row (colon-scope, tuple-value/tuple-anywhere, set-arity,
  first-rest, two-orders, modifier-lift, unset-component/default-unused, joint-loops, record-is-product); "Collides
  with 'a record is never a value' ... unless" removed (settled); "the lift: ... labels in SIBLING loops have no
  pairing (a break, §6)" becomes the ruled error; "the `compare.looped` warning ... its subject goes" becomes "MOVED";
  "Counted: ... N1 and N2 are the expensive ones; they are one decision (question **tuple-value**) [settled]" becomes
  "N1-N5 and one sentence of §2.4, each now ruled".
- Item 1: the opening "It is the RECORD bracket ... in a new position" restated in the owner's terms (a tuple of
  references) with J2 ruled; the label-twice bullet gains the record consequence and open item **label-twice**; the
  shadowing bullet cites J2 instead of §4.1 and adds the value side.
- Item 2 (d): "RECOMMENDED" becomes "ADOPTED"; "Owner question **tuple-value**" becomes "SETTLED".
- Item 3: "The lane leaned ARITY; RULED by the owner" restated as RULED (J3); the `padded` and modifier rows'
  "NEW lift rule" / "follows N4" become RULED (J8).
- Item 4: REWRITTEN: title; the order as RULED (J4); the two orders both legal, RULED (J5); the per-part form's uses
  (his question); the manager's "no warning" reading tested (HOLDS, INCOMPLETE).
- Item 5: REWRITTEN: per-pass pairing RULED; the pairing loop stated precisely (the lane's; open item
  **pairing-loop**; table (NL)); the sibling-loop ERROR with its text ("The lane leans ERROR" removed); the looped
  WARNING moved with its text ("Not a new ruling; a reading to confirm (question **joint-loops**)" removed).
- Item 6: the unset bullet RULED (J6); "The lane leans TUPLE-EXISTS ... Owner question **unset-component**. [the
  owner LEANS ... not closed]" replaced by the two meanings (default vs alternative) and "decided-prefix WITHDRAWN";
  the `label.unset` bullet names both fixes.
- Item 7: the E-CAL row writes `<=$dim` (J2, C13); the start/end row cites table (SE).
- §4 item 7's expansion paragraph: "at most 2k - 1 rows ... is UNTESTED" becomes TESTED (table (RC)).
- Item 8: the record row "(question **record-is-product**)" becomes "the same by definition (J9)"; the looped row
  names the moved warning; rows added (the two orders, the default vs `m: 0`); the CENSUS gains `=` (N5): "two
  positions are new (N1, N3)" becomes three (N1, N3, N5).
- Item 9: "REMOVED" becomes "NO JOB LEFT" with the paused-not-reversed caveat (open item **retire-paused**); the
  decided-prefix order "WITHDRAWN by ruling", `compare.looped` "MOVED by ruling"; CF:1164 corrected to CF:1166.
- §4A.1, last paragraph: "whether the record is DEFINED as that product case is the open **record-is-product**.
  Nothing here depends on the answer" becomes RULED (J9) with a pointer to §4D.
- §4A.2: "The rule holds under either answer to **set-arity** ... [set-arity is RULED]" becomes one sentence (RULED).
- §4A.4: producer (6) "(**modifier-lift**, open; without it an error)" becomes RULED (J8); ACCEPTED POSITIONS "(under
  modifier-lift)" becomes "(J8)".
- §4A.5: the bounds row "UNTESTED (as in §5)" becomes table (SE).
- §4A.7: the record look-alike "record-is-product (open)" and the two-orders row "owner question **two-orders**"
  become RULED.
- §4A.8: (m2) "'is' is the open **record-is-product**" becomes RULED; (m3) "holds under either **set-arity**
  answer" becomes RULED; (m5) "`($sh, $sm)` is UNTESTED" now tested; R-1 (i) "owner question **colon-scope**" becomes
  RULED as restated, with the refinement; R-1 (ii) "the one open spot; under C13's lean it holds" becomes HOLDS (J2),
  C13 settled as `$dim` (the manager's consequence, tested below).
- §4A.9: REWRITTEN to the one open point (tuple-parts).
- §4A.11: the comparison table's "(**two-orders**)" and "needs **modifier-lift**" become RULED.
- §4B opening: "The base rule is unchanged and is his LEAN, not closed" becomes RULED (11:05), with default-unused
  (11:05) and the default's scope (11:32) quoted.
- §4B.1: WHAT v MAY BE gains two rows (a bare label name: an error naming `$h`; a name that is both a binding and a
  label: the binding), from J2's refinement; "COMPILE-TIME DIAGNOSTICS (names LEAN, the lane's ...)" becomes the
  ruled warning, the names the spelling step's.
- §4B.7: "the owner's lean; unset-component stays open until he closes it" becomes RULED.
- §4C (this list) and §4D: NEW.
- §5: problems 5 and 8 "UNTESTED" become TESTED (tables (SE), (MN)); problem 7's "[§4A.10, unsetdef]" folded; the
  tally restated as one sentence (simpler 7, same 6, worse 0).
- §6: REWRITTEN: B1 settled; B2 ruled; B3 ruled and parked; B4 ruled error; B6 NEW (the zero-pass corner).
- §7: REWRITTEN to the ruled state; items 1, 5, 6, 8, 10 restated; items 11-14 NEW.
- §8: REWRITTEN: answered list complete; CONTRADICTIONS FOUND (three); open items (tuple-parts and the lane's
  four); parked ideas point at `predicates_future.md`.
- §9: NEW, what rev 20 of the draft must change.

THE MANAGER'S READINGS AND CONSEQUENCES in the entries folded here, each TESTED (HOLDS / WRONG / INCOMPLETE):

| entry | the manager's reading or consequence (not the owner's words) | verdict | why |
|---|---|---|---|
| CF 10:22 | "tuple-parts has no user while first/rest is parked and stays open, not built" | HOLDS | no case in §5, §4A.5 or the draft's §12 takes one tuple apart (§4A.3) |
| CF 10:22 | "two-orders stays a live question" | HOLDS, then ANSWERED | it was live until CF 11:20 ruled it |
| CF 10:37 | the default is a go to WRITE UP AND TEST (lane unsetdef); unset-component closed only when he says so | HOLDS | he closed it at 11:05 after §4B |
| CF 11:05 | "agree" on default-unused = a WARNING | HOLDS | the question asked was "a WARNING not an error; lean warning"; agreeing with the question's lean is the warning; an error would refuse a library condition laid over patterns where the field is sometimes required (§4B.1, table (D1)) |
| CF 11:20 | "sufficiently different" = NO warning, unless confusion shows in use | HOLDS, INCOMPLETE | item 4: the trigger the withdrawn lean proposed fires on legitimate per-part uses (minimum width and height) and the compiler cannot tell hierarchical fields from independent ones; INCOMPLETE: the slip `(>= 9, >= 30)` for "at or after 9:30" is then silent (2,700 of 11,000 padded, table (O) [§4F]), a BY DESIGN look-alike row the draft must carry (§9) |
| CF 11:32 | C13 closes as "`$` to read a computed label on the value side": `<=dim` becomes `<=$dim`, `==wd` becomes `==$wd` | HOLDS, INCOMPLETE | J2 puts both on the value side, where a bare name is a binding; a computed label IS a binding (§4.4, `predicates_draft.md:1724-1726`, "a match-dependent binding ... a macro whose operand is that pattern"), so bare `dim` there names that macro, and a comparison set's atom must be a one-string set (§2.4): bare `<=dim` becomes an ERROR naming `<=$dim` (the lane's), not a second spelling. Missing from the consequence: that error text, and that `$dim` is already the draft's lean (§4.4 :1737-1738) |
| CF 11:32 | "a default still must be ONE string (ruled earlier today)" | HOLDS | J2's refinement puts the default on the value side, where any value may stand; the one-string limit is CF 10:43's, unchanged; the two new §4B.1 rows (a bare label name; a binding-and-label name) follow from the refinement |
| CF 11:17, 11:27, 11:35 | (none: the record of each states the ruling as asked) | — | the wording of 11:17's pairing loop is INCOMPLETE on its own terms (item 5, **pairing-loop**) |

The earlier entries' manager readings (00:06 consequences (1)-(3), 00:08 notes, 09:47, 09:49, 10:18) were tested by
the lanes that folded them (§4A.8, §4A.10) or belong to the paused direction; their verdicts are in
`docs/dev/lanes/jcfold_report.md` (CONSEQUENCES DERIVED BY THE LANE).

## 4D. The record, derived: each record rule of the draft as the k-label rule specialised

RULED (J9, record-is-product, CF 11:35): the record `(p1: S1, ..., pk: Sk)` IS the joint condition
`((p1, ..., pk): (S1, ..., Sk))`, and with defaults `(p1: S1, p2 = v: S2)` IS `((p1, p2 = v): (S1, S2))`. So every
record rule of `predicates_draft.md` must be what J1-J8 say for a product right side. Checked one by one (the
lane's):

| # | the draft's record rule (rev 19) | J1-J8 specialised to a product | verdict |
|---|---|---|---|
| D1 | `x: S` = the whole matches whose label x is in S (§4.1, `predicates_draft.md:1521-1522`) | J1 with k = 1 | FOLLOWS |
| D2 | a record holds its entries together, "the AND comes from the record, not the comma" (§4.1 :1541-1543, RULED CF:863, CF:866 (b)) | (t1, ..., tk) in S1 x ... x Sk iff each ti in Si: the AND is the product's | FOLLOWS (per pass) |
| D3 | "all of several conditions = one record: `(major: 1, minor: >=4)` = `(major: 1) & (minor: >=4)`" (§4.1 :1546) | FOLLOWS when the labels are set once or in the same pass; at DIFFERENT DEPTHS the product is per pass of the deeper label's loop (J7); on ZERO passes ONE tuple with the looped part EMPTY, so the once-set k is still tested (J7, CF 12:45) | FOLLOWS [§4E: was CONTRADICTION (§8 **zero-pass-record**), 5 of 1,110 differing under the vacuous reading]: table (RZ) re-run under the ruled rule, `/(?<k>\d)(?:;(?<h>\d))*/` with S = 0..4, T = 3..7: 0 of 1,110 differ from `(h: S) & (k: T)` (`9` FAILS by both); nested, table (ZN): 0 of 2,526. [§4F: "set in the same pass" FOLLOWS only under the single-label reading that a pass which did not set the label FAILS `(m: T)` (`predicates_draft.md:1694`, a label the iteration did not set is unset in it; §2.6's THE ITERATION'S OWN VALUES, LEAN); under "m's iterations are the values it took" it does not (table (OP): 8 of 259, `3:15,3,`); and a pass that never reaches the pairing loop is unstated (table (UP), **pairing-loop** (3)); facts, not repaired] |
| D4 | an entry runs to the next comma; `&`, `\|` bind tighter than `:` (§4.1 :1543-1545) | a spelling of the product's parts | FOLLOWS (spelling) |
| D5 | `:` outside a record is an error; a condition in value position is a macro, never the record (§4.1 :1552-1556) | the same for `((h, m): R)` | FOLLOWS |
| D6 | the chain lookup, ambiguity and unknown-label errors (§4.1 :1557-1559) | J2 | FOLLOWS |
| D7 | a condition naming an unset label FAILS (§4.2 :1590-1591, RULED by acceptance :1613-1615) | J6: no tuple exists, the joint condition fails | FOLLOWS; with a default, `(h: S, m = v: T)` = `((h, m = v): (S, T))`: table (RD), 76,860 cases (18 combinations of S, T and the default, both routes engine-run), 0 differ |
| D8 | "a comparison on an UNSET label is false (its `!` true)" (§4.2 :1590, LEAN) | `!((h, m): R)` true on a match with no tuple | FOLLOWS; §13 O28's `!(x: S)` vs `(x: !S)` inherited unchanged |
| D9 | zero iterations of a REACHED loop: a plain condition HOLDS (§4.2 :1600-1602, RULED) | J7: zero passes, one tuple with the looped part empty, which satisfies any set: holds [§4E: was "no tuple, holds"] | FOLLOWS at every depth (table (Z1); at different depths D3's rule tests the outside label) [§4E], under J7's GROUP-ZERO sentence: the zero-pass tuple is tested by the plain condition and `all`, never counted by `some`/`count`/`occurs`, so :1601's "`some(...)` fails; `count(...)` is 0" stands [§4F, GROUP-ZERO] |
| D10 | the sequence rule: `x: S` constrains ALL iterations (§4.3 :1632, RULED CF:583) | J7 with k = 1 | FOLLOWS |
| D11 | the group questions `some`, `all`, `count`, `occurs.*` over a record (§4.3 :1653-1666) | they count PASSES whose tuple is in R | FOLLOWS under J7's GROUP-ZERO sentence (the zero-pass tuple is no pass for `some`/`count`/`occurs`; `all` = the plain condition, zero iterations included, :1660) [§4F: was "FOLLOWS"; either unstated choice broke :1601/:1661 or :1660] |
| D12 | SAME ITERATION BY RECORD (§4.3 :1668-1673, CF:915-917 accepted) | J7's per-pass pairing IS this rule | FOLLOWS (the rule is the product case of J7) |
| D13 | "For `all`/the plain condition the two spellings always agree (every iteration has both = every iteration has g and every iteration has h)" (§4.3 :1674-1675) | true when g and h are in the same pass; at different depths with zero passes the record tests the outside label once, as `(g: S) & (k: T)` does (J7, CF 12:45) | FOLLOWS, as D3 [§4E: was CONTRADICTION, the same corner as D3] |
| D14 | labels at different depths: §13 O56 (:4118-4121, LEAN: "the innermost loop that encloses every label of the record; a label outside it has one value for every iteration of that loop") | J7 (RULED, CF 11:17) | FOLLOWS under J7's GROUP-ZERO sentence (O56's own example is `some((g: "x", k: 1))`) [§4F]; O56 (1) becomes RULED through J7 + J9; the same wording gap (item 5, **pairing-loop**) |
| D15 | a literal-index test `(x[2]: S)` (§4.3 :1690-1693, LEAN) | a path on the left (item 1) | FOLLOWS |
| D16 | each iteration's labels read within that iteration (§4.3 :1694-1695) | per pass | FOLLOWS |
| D17 | §5.4 `( e1, e2, ... )` row: a RECORD, never a value, in positions (a) call, (b) condition, (c) left of `:=` (:2013) | position (b) is the joint condition's product case; the record is still never a value (the tuple set `(S, T)` is a value and not a record, §4A.1) | FOLLOWS; the row's position (b) is restated as J9 (§9) |
| D18 | §5.4 `( label: S, ... )` in value position is a CONDITION, a macro (:2014) | the same for any joint condition | FOLLOWS; "Any other record in value position is an error" narrows to labelled entries (L43), since a colon-less positional tuple is a value (§4A.1) |
| D19 | §5.4 `=` row: `name = e` names an entry; in a head, a default (:2017) | J6 adds a fourth position, a default at a label left of `:`, same meaning (§4B.3) | FOLLOWS (one more position) |
| D20 | §5.4 `:` row: the left is a field path (:2018) | J1: a path or a tuple of references | FOLLOWS (one more form) |
| D21 | §0.1 L23 (:521): `(x: <200, y: >55)` vs `[(x: <200), (y: >55)]`, AND vs OR by the bracket | a product vs a union of two 1-label conditions | FOLLOWS |
| D22 | §0.1 L31 (:529): `some((g: "x", h: 1))` vs `some((g: "x")) & some((h: 1))` differ | one pass with both vs two passes | FOLLOWS |
| D23 | §0.1 L36 (:534): `(x: S)` = `all((x: S))` | k = 1 | FOLLOWS |
| D24 | §0.1 L43-L47 (:541-545): record in value position an error; `(x)` grouping; `f((1, 2))` an error; a bound condition; `[x: S]` an error | L43, L44, L46, L47 unchanged; L45 changes (`f((1, 2))` is one argument, a pair: §4A.1), which is the TUPLE's consequence, not the record's | FOLLOWS (L45 moves for J3, not J9) |
| D25 | §0.1 L56, L65 (:554, :563): per-match unset vs zero iterations | J6, J7 at k = 1 | FOLLOWS |
| D26 | a label written twice in one record (`(h: <5, h: >2)`): the draft has NO sentence (`grep -n 'label twice\|named twice' predicates_draft.md`: only the projection's L75 :573 and DECIDED (58) :4270-4271) | by J9 it is `((h, h): (<5, >2))`, which item 1 makes an error | FOLLOWS: an ERROR, RULED (**label-twice**, CF 13:16) [§4F: was "a NEW CONSEQUENCE: open item **label-twice**"] |

Tally: 26 rules; 26 follow (one of them as a spelling only; D9, D11, D14 under J7's GROUP-ZERO sentence; D26 by the
label-twice ruling) [§4F: was "25 follow ...; 1 new consequence (D26)"]; 0 contradict since CF 12:45 [§4E: was "23
follow ...; 2 contradict, both the same corner (D3, D13: labels at different depths, zero passes)"]. Nothing else in the draft's record rules needs its own
statement once J9 holds: the record is the product case.

## 4E. Corrections by lane jcfold2 (the entries of 12:45-12:51)

Lane jcfold2 (2026-11-16), applying the owner's entries of 12:45 (zero-pass-record: "zero-pass-record: I agree but
save the notes in the future file. The issue falls into the 'saving people from themselves' category that tools need
to realistically consider"), 12:48 (library-not-syntax: "library-not-syntax: agree. we've replaced the idea and I think
with something much better") and 12:51 (retire-paused: "retire-paused: agree to split. But the pause on ^ is
indefinite and requires real value other than 'override a users own *'"). Rulings file `jcfold2_rulings.md`: empty
at every read. Every changed sentence, marked "[§4E]" in place:

- HEADER: the STATUS paragraph (entries through 12:51, `grep -c` = 27; the three contradictions answered; still open
  tuple-parts, label-twice, pairing-loop; lane jcfold2; the retired and paused items); the evidence paragraph gains
  `jcfold2_check.py`.
- J7: the zero-pass sentence, the owner's words and the MANAGER'S wording, replacing "(zero passes of a reached
  loop: holds, §4.2)". J9: "all but one follow ... a CONTRADICTION" becomes "all follow", (RZ) re-run.
- Item 5: (NL)'s "an outer pass with no k pairs nothing and holds" WITHDRAWN (10 of 73 answers move, table (ZN)); a
  ZERO PASSES bullet added.
- Item 9: retire-paused RULED (retired / paused indefinitely); "a library still MAY name `lex`-style helpers" becomes
  "NOT kept" (library-not-syntax, the manager's reading).
- §4B.1, the LOOPED-label row: "there is no tuple" becomes "the looped part is EMPTY"; the never-reached reading
  TESTED (table (ZD)). The rule itself (a default is never read on zero passes) is unchanged, as the ruling says.
- §4D: D3, D13 CONTRADICTION become FOLLOWS; D9 restated; the tally 25 follow, 0 contradict.
- §6 B6: RULED. §7: item 14 restated, item 15 NEW.
- §8: zero-pass-record, library-not-syntax, retire-paused moved to ANSWERED with his words and clock times; the
  CONTRADICTIONS list kept as the record of the questions, each marked ANSWERED; PARKED gains `predicates_future.md`
  items 5-8. The STILL OPEN items (tuple-parts, label-twice, pairing-loop) are untouched.
- §9: the intro (no row hangs on a contradiction); rows 1, 2, 5, 7, 12, 13, 14, 16, 23, 25, 28, 30, 31, 36, 41, 42,
  43, 44 restated; rows 45 (the zero-pass sentence in §4.2/§4.3) and 46 (the superseded-direction record) NEW.
- §4E (this section): NEW.

THE MANAGER'S WORDING TESTED (`jcfold2_check.py`; M = the wording evaluated on the split subject, engine-run against
its unfold into a regex; 14,937 cases, 0 differ, 0 engine disagreements; sabotaged, zero passes made vacuous: 2,444
differ):

| table | case | result | verdict |
|---|---|---|---|
| (RZ) | jcfold's population, `/(?<k>\d)(?:;(?<h>\d))*/ & (h: <5, k: 3..7)` | M vs `(h: <5) & (k: 3..7)`: 0 of 1,110 differ; M vs jcfold's vacuous reading: 5 (`9` FAILS by M) | HOLDS: the ruled answer |
| (ZN) | NESTED, `/(?<c>\d)(?:;(?<h>\d)(?::(?<k>\d))*)*/ & (c: 3..7, h: 0..4, k: 2..6)`: c outside every loop, h in the outer item, k in an inner loop; 6 subjects with a zero-pass OUTER loop, 888 with a zero-pass inner reach | M vs the `&` reading: 0 of 2,526 differ; M vs the vacuous reading: 153. `5` (outer zero) holds; `5;9` (inner zero, h = 9 not in 0..4) FAILS | HOLDS, read PER REACH: the inner loop's zero passes in each outer pass give their own tuple (c, h, EMPTY); only that reading equals `&` at every depth |
| (ZN) | jcfold's (NL) population re-run, non-product `((h, k): >= (5, 3))`, h in the outer item, k in the inner loop | 10 of 73 answers MOVE from (NL): `4:;` held (no k, nothing paired), now FAILS (no k makes (4, k) >= (5, 3)) | an answer CHANGE on a case the owner was not shown; see CONTRADICTIONS (3) |
| (ZJ) | NON-PRODUCT sets, zero passes: `((h, k): >= (5, 3))`, `((k, h): >= (5, 3))`, `((h, k): (0\|1\|2, 3\|4) \| (5, 5))`, `((h, k): ("x", 3) \| (0, 5))`, `((h, k): < (0, 3))` | possible k: all; 5..9; {3, 4, 5}; {3, 5} (any string) or {5} (`\d`'s strings); {0, 1, 2}. On zero passes M equals the hand expansion into a `\|` of records on 43 of 50; the 7 that differ are below | the rule answers R's PROJECTION onto the outside labels. `9` FAILS under `(0\|1\|2, 3\|4) \| (5, 5)`: no h makes 9 possible. No ruled sentence covers a non-product set on zero passes; the nearest, the `&` equality, has no non-product form |
| (ZJ) | the projection vs the hand expansion when an expansion row has an EMPTY part: `((h, k): < (0, 3))` expands to `(h: <0) \| (h: 0, k: <3)` | 7 of 10 zero-pass subjects differ: the row `(h: <0)` holds vacuously on zero passes (single-label rule), M requires k in {0, 1, 2} | CORNER (1) below |
| (ZJ) | the EMPTY set, zero passes, `3`: `(h: <0, k: 3)` and `((h, k): (<0, 3))` (product clause) vs `((h, k): < (0, 0))` (non-product clause) | HOLDS, HOLDS, FAILS: three spellings of the same (empty) set of pairs; COMPUTED in Python (the (ZJ-E) block prints typed-in values), not engine-run and not among the 14,937 [§4F, SIM-6] | CORNER (1) below |
| (ZD) | a looped default on zero passes, `(h = 9: <5, k: 3..7)` on (RZ)'s pattern | default NOT read: 0 of 1,110 differ from `(h = 9: <5) & (k: 3..7)`; reading it would move 5 (the zero-pass subjects with k in 3..7) | HOLDS: §4B.1 unchanged |
| (ZD) | the loop NEVER REACHED, `/(?<k>\d)(?:-(?:;(?<h>\d))*)?/` on `5` vs `5-` | no default: `5` FAILS (unset), `5-` holds; `h = 9`: `5` FAILS (9 read, not <5); `h = 2`: `5` holds (2 read) | HOLDS: "unset" keeps its meaning; §4B.1's never-reached reading now TESTED |
| (ZD) | all-looped list with a default, `/(?:(?<h>\d)(?::(?<m>\d))?,)*/ & ((h, m = 0): >= (5, 3))` | 91 subjects, 0 differ; the empty list HOLDS | HOLDS: (DL) unchanged |
| (Z1) | single label: (RZ)'s pattern `& (h: <5)`; `/(?:(?<n>\d),)*/ & (n: <5)` on the empty span; `/x\|(?<n>\d)+/ & (n: <5)` on `x` | zero passes HOLD (1,110 + 4 subjects); never reached FAILS | HOLDS: CF:997-1000 |

CONTRADICTIONS AND UNEXPECTED ANSWERS (the lane's; NOT repaired; each with both sides):

1. AN EMPTY PART. The wording as this section first read it has two clauses: "empty satisfies any set" (a product)
   and "possible under R for some value of the looped parts" (not a product) [§4F: that split is lane jcfold2's
   repair; the record's wording (CF:1553-1557) is ONE clause, the parenthetical a gloss for any joint set, under which
   both spellings below FAIL, against the `&` equality (RULING-1)]. They agree whenever every part of every product is non-empty, and
   disagree on an EMPTY part. Smallest example, zero passes, subject `3` of `/(?<k>\d)(?:;(?<h>\d))*/`: `(h: <0, k:
   3)` HOLDS (product clause; and the ruled `(h: <0) & (k: 3)` holds too, since a single-label condition holds on
   zero passes), while `((h, k): < (0, 0))`, the same empty set of pairs, FAILS (no h possible). Side A: J3 makes
   every value a SET of tuples, so equal sets should give equal answers. Side B: the ruled answer keeps `(a: S, b: T)`
   = `(a: S) & (b: T)` at every depth, which forces the product clause even when S is empty. The same corner makes
   the projection differ from a hand expansion whose row has an empty part (`< (0, 3)` vs `(h: <0) | (h: 0, k: <3)`:
   7 of 10 zero-pass subjects). Reachable only through an empty set, which `<0` over numerals is.
2. THE DOMAIN OF "SOME VALUE". "Possible ... for some value of the looped parts" does not say over WHICH values: every
   string, or the strings the looped label's group can match. Smallest example: `((h, k): ("x", 3) | (0, 5))` with h
   `\d`, zero passes, subject `3`: over every string it HOLDS (h = `x`), over `\d`'s strings it FAILS. The hand
   expansion `(h: "x", k: 3) | (h: 0, k: 5)` holds, so "every string" is the reading that agrees with the record
   rule; a reader thinking of the pattern would expect FAILS.
3. THE NESTED ANSWERS MOVE. For a product the ruled answer forces the per-reach reading (each zero-pass reach of an
   inner loop gives its own tuple; (ZN) 0 of 2,526 differ from `&`). Carried to the non-product (NL) case, 10 of its 73
   answers move: `/(?:(?<h>\d):(?:(?<k>\d),)*;)*/ & ((h, k): >= (5, 3))` on `4:;` HELD (lane jcfold, item 5) and now
   FAILS. Not against a ruled sentence: (NL)'s answer was the lane's, and §8 **pairing-loop** cites (NL) as "73
   subjects, 0 differ" for its own wording, which is still true; but the open question's text no longer states every
   answer the owner would be confirming. The §8 text is left as it stands (the brief).
4. A DEFAULT THAT IS NOT READ. `(h = 9: <5, k: 3..7)` on `5-` of `/(?<k>\d)(?:-(?:;(?<h>\d))*)?/` (loop reached,
   zero passes) HOLDS while on `5` (loop never reached) it FAILS (9 read, not <5) (table (ZD)). Consistent with §4B.1 and the ruling
   ("a default is NOT read there"); a reader who writes the default to mean "no h means 9" would expect FAILS in both.
   The owner's idea to read it was parked (`predicates_future.md` item 7).

No wording CONTRADICTS a RULED sentence on any case the ruling names: (RZ), (Z1) and the default rows hold exactly.
[§4F, RULING-2: but corner 1 IS a clash among three RULED points, not only a lane corner: set-arity (one set kind,
values compared as sets), record-is-product (J9) and zero-pass-record's `&` equality cannot all hold on an EMPTY
set on zero passes; no set-only rule meets all three without a fourth clause "R empty: holds". The draft's
narrowing-site error (`predicates_draft.md:1941-1942`, LEAN) removes the CONSTANT empty spellings; an R empty only
through a match value remains: owner question **zero-pass-empty** (§8), table (ZE).]

## 4F. Corrections after round jointcond (lane jcfix)

Lane jcfix (2026-11-16), applying critic round jointcond (review draft and the manager's dispositions of 2026-11-16,
session 135: every proposed disposition ACCEPTED, with the manager's rulings and readings) and the owner's entry of
13:16 (label-twice: "label-twice: agree an error. And that means it's also unofficially parked in case some other
meaning becomes valuable"). Rulings file `jcfix_rulings.md`: empty at every read. Every manager's reading enters the
note labelled "the manager's reading (round jointcond)"; lane jcfold2's zero-pass split is labelled as its repair.
Evidence: `jcfix_check.py` (header). Every changed sentence is marked "[§4F]" in place; one row per finding id:

| id | what changed | where |
|---|---|---|
| RULING-1 (ZERO-EMPTY) | the manager's zero-pass wording quoted VERBATIM from CF:1553-1557 (the parenthetical gloss for any joint set; "(CF:997-1000 unchanged)" restored); the product/non-product split labelled lane jcfold2's repair | J7; item 5 ZERO PASSES; §4E corner 1; §9 row 45 |
| RULING-2 (ZERO-EMPTY) | the empty-set corner restated as a clash among three RULED points (set-arity, record-is-product, the `&` equality), not a lane corner; owner question **zero-pass-empty** | §4E (after corner 4); §8 STILL OPEN 3 |
| OWNER-2 (ZERO-EMPTY) | the draft's narrowing-site error (`:1941-1942`, LEAN) named as removing the constant spellings; the match-dependent case and the domain of "some value" put to the owner with the manager's lean; table (ZE) | J7; §4E; §8 STILL OPEN 3; §9 row 45 |
| SIM-6 (ZERO-EMPTY) | the (ZJ-E) rows labelled COMPUTED, not engine-run, not among the 14,937 | header evidence paragraph; §4E (ZJ) EMPTY row |
| RULING-3 (GROUP-ZERO) | the sentence "the zero-pass tuple is tested by the plain condition and by `all`; never counted by `some`/`count`/`occurs`" (the manager's reading); D9, D11, D14 "FOLLOWS under that sentence" | J7; §4D D9, D11, D14, tally; §9 rows 16, 45 |
| SIM-2 (UNREACHED-PAIRING) | "never reached" in §4.2's sense (the deepest construct entered), with the nested witness (derived, not run) | J7; §4B.1 LOOPED row; §9 row 45 |
| SIM-5 (UNREACHED-PAIRING) | folded into **pairing-loop**, re-drafted whole in three parts; table (UP); D3's dependence on an unstated single-label reading stated as a fact | item 5; J7; §4D D3; §8 STILL OPEN 2; §9 rows 45, 54 |
| SIM-1 (DICT-DOMAIN) | the DOM reading stated (every component in its literal's domain; the manager's reading); item 7's expansion and LEVEL restated; the `m = 00` default's `default.unused` consequence; table (DM) | J4; LEVEL; item 4; item 7; §4A.4 (4); §4B.1 (b); §9 row 10 |
| SIM-3 (DICT-DOMAIN) | table (O) cited as the PADDED count; unpadded 1,800 under DOM, `10:00` in neither set | item 4; item 8; §4A.7; §4A.11 table; §4C table; §9 row 6 |
| CENSUS-2 (TUPLE-BINDING) | "a computed label is arity 1; a match-dependent tuple is written inline or passed, never bound" (the manager's reading); the error added to the list | §4A.4 (5) and ERRORS; §3 counted table; §9 row 17 |
| CENSUS-3 (MIXED-RECORD) | a mixed record is legal, the `&` of its entries; a label in two entries the label-twice error (the manager's reading + CF 13:16) | J1; J9; §9 row 14 |
| SIM-7 (DOLLAR-COMPONENT) | the value LEAN for a `$` component carried as a sentence of the comparison-set text; not retired with §8 | J4; §4A.4 (4); §9 rows 10, 28 |
| SIM-4 | "i.e. a `\|` of single-label condition records" restated: the SET is a finite union of products; for looped labels the union is taken per pass inside the loop | LEVEL; item 7; §9 row 26 |
| RULING-4 | CF:648 cited for the withdrawn TUPLE CONDITIONS sentence; the rest of CF:644-650 stands | §8 ANSWERED; §9 rows 31, 36, 46 |
| RULING-5 | "every value is a set of tuples" becomes "every SET carries an arity; macros as today" | J3; §4A.4; §9 row 9 |
| RULING-6 | the record-with-default spelling cited to 11:05 + §4B.1 (lane unsetdef), not to 11:35 | J9 |
| RULING-7 | the header restated: answered through 13:16; open: tuple-parts, pairing-loop, zero-pass-empty | header STATUS |
| label-twice (FREEZE DRIFT) | RULED (CF 13:16): an ERROR in both forms, the spelling free (`predicates_future.md` item 9); folded; the lane's proposed warning `label.twice` RENAMED `label.both_sides` | header; item 1; §3 table; §4B.4; §4D D26 + tally; §7 item 3; §8 ANSWERED; §9 rows 27, 42, 43, 44 |
| CENSUS-1 | §4A.7's discriminators for the default (`p = v: S` entries; L43 = an `=` entry with no `:`; the reference tuple's `p = v`); "no existing row changes meaning" restated; the §5.4 extent sentence | §4A.7 rows and count; §9 rows 21, 22 |
| CENSUS-4 | the look-alike union of tuples vs tuple of unions LISTED, BY DESIGN like two-orders; "the one pair" sentence corrected | item 8; §4A.7; §9 row 6 |
| CENSUS-5 | §9 row 6 gains the two LEGAL-DIFFERENT pairs of §4B.4; row 27 the proposed warning, marked proposal, renamed | §9 rows 6, 27 |
| CENSUS-6 | rev 20's `( )` row number named with its basis: six on §5.4's basis, ten on §4A.7's | §4A.7 count; §9 row 21 |
| OWNER-1 | G1 counted alike on both sides with a REUSE column | Goals G1; §3 COUNTED ALIKE |
| OWNER-3 | G2's evidence and bar restated by his criterion (non-compare problems only) | Goals G2; §5 tally |
| OWNER-4 | G3's measurable form names the compare's price and what it exposed | Goals G3 |
| OWNER-5 | which macros lift: a macro whose result distributes over `\|` (the manager's reading of "do everything to both"); `predicates_future.md` item 2 NOT edited (the manager adds its line) | J8; §4A.4 (6); §9 row 53 |
| OWNER-6 | PLANNED into rev 20: one declared absence table in §4.2, no answer change | §9 row 54 |
| OWNER-7 | NOTED: one paragraph, the table-of-passes model; its two unlocks NOT filed | item 5 |
| REV20-1 | §14 Non-goals row | §9 row 47 |
| REV20-2 | row 12's cite widened; §3.2 `:1435-1438` row | §9 rows 12, 48 |
| REV20-3 | row 11's cite widened; `compare.width` text `:2810` row; §0.1 prose `:693-706` into row 5 | §9 rows 5, 11, 49 |
| REV20-4 | C25 `:3760-3778`, O69 `:4426-4440`; O47 and O68 row | §9 rows 36, 38, 50 |
| REV20-5 | DECIDED (46), (49)-(53), (56), (57), (60) into row 42 | §9 row 42 |
| REV20-6 | O71 and the heading into row 41; owner questions (10), (12), (13), (15) into row 43 | §9 rows 41, 43 |
| REV20-7 | `==wd`/`<=dim` at `:1731`, `:1840`, `:3320` into row 17; C13's other premises row | §9 rows 17, 51 |
| REV20-8 | row 34's cite widened (`:3340-3343`, `:3360-3362`); §1 `:831` row | §9 rows 34, 52 |
| REV20-9 | row 2's cite an insertion point; the §0.1 prose into row 5 | §9 rows 2, 5 |
| REV20-10 | the glossary `record` row into row 8 | §9 row 8 |

NOT CHANGED here (the brief): `predicates_draft.md`, the rulings record, `predicates_future.md`. The D27 recommendation
(a spec-first author when the joint condition gets a build go) is NOTED for that day.

## 5. Problems tried

Each in full; `t`, `semver`, `ip`, `isodate`, `textdate` as defined; what is REUSED and what is NEW per line.

1. TIME-OF-DAY RANGE. `t & ((h, m): padded(between((9, 0), (10, 0))))`. Reused: `t`, `between`, `padded`, the
   condition record. New: the left list (N3), the pairs (N1), tuple order, the lift (N4). Accepts `9:00`, `09:30`,
   `10:00`; rejects `10:01`, `8:59`. Table (X) between rows. Rev 19: `t & lex_between2([^h, ^m], [9, 0], [10, 0])`.
   Other text order (`/(?<m>\d\d) past (?<h>\d{1,2})/`): the same condition, `((h, m): ...)`: the LEFT's order is the
   compare's order, as rev 17's projection gave.
2. VERSION AT LEAST 1.4.0. `semver & ((major, minor, patch): >= (1, 4, 0))` (semver refuses leading zeros, so no
   `padded`). 3 product rows; table (X) version, 1,734 cases (with `padded` per component as the populations carry
   leading-zero subjects), 0 differ. Strict: `> (1, 4, 0)`.
3. IPv4 INSIDE A RANGE. `ip := join([a = octet, b = octet, c = octet, d = octet], sep = ".")`, then
   `ip & ((a, b, c, d): between((10, 1, 128, 0), (10, 1, 131, 255)))`. NEW beside E-IPV4: labels on the octets (an
   existing `=`). Table (X) ipv4, 202 cases (sampled), 0 differ.
4. VALID CALENDAR DATE (leap years). `isodate & (((month, day): month_days) | (year: leap, month: padded(2), day:
   29))` with `month_days` the 3-row set of §1. Reused: `leap` (an rx of years, §4.6), records, `|`. New: the pairs
   as products. A library can ship `month_days` (label-free) or the whole 3-ary set `valid_ymd`, laid against any
   date pattern's labels: `isodate & ((year, month, day): dates.valid_ymd)`. Table (C4): 468 cases, 0 differ from
   `datetime.date` (years 1900, 1996, 2000, 2023, 2024, 2099; 1900 not leap). SIMPLER than E-CAL (item 7).
5. START TIME BEFORE END TIME, ONE LINE. `span := /(?<sh>\d{1,2}):(?<sm>\d\d)-(?<eh>\d{1,2}):(?<em>\d\d)/`, then
   `span & ((eh, em): padded(> ($sh, $sm)))`. Reused: `$` values, §4.6. New: a pair of `$` values as an atom. Level:
   §4.6, ~1,440 classes (borderline), the same as any spelling. TESTED by lane jcfold [§4C], table (SE): the
   relation unfolded as one branch per class of (sh, sm) (24 hours x 7 minute values = 168 classes), each the
   two-row expansion with that class's values as the atom; 13,328 subjects with one- and two-digit hours, 0 differ
   from `(eh, em) > (sh, sm)` as integers.
6. LOOPED LIST OF TIMES ALL AT LEAST 9:00. `list & ((h, m): padded(>= (9, 0)))`: per item; table (L) at 9:30, 10
   cases, 0 differ from "every pair at least 9:30"; rev 19's form differs on 3 and needed a warning plus a rewrite
   into the loop's item.
7. OPTIONAL SECONDS. `/(?<h>\d{1,2}):(?<m>\d\d)(?::(?<s>\d\d))?/ & ((h, m, s): padded(>= (9, 0, 30)))`: table (U); a
   subject without seconds is OUT (no triple). For "seconds optional, absent means :00": `((h, m): padded(> (9, 0)))
   | ((h, m, s): padded(>= (9, 0, 30)))`. The decided-prefix answer differs (item 6). With a default (J6):
   `((h, m, s = 0): padded(>= (9, 0, 30)))`, one condition (§4B.5, table (DS)): SIMPLER [§4C].
8. DATE RANGE WITH A MONTH NAME. `mnum := $mname.index` (§4.4; E-RFC's `textdate`), then `textdate & ((year, mnum,
   day): between((2024, 3, 15), (2025, 2, 1)))` (day `\d{1,2}`, canonical: no `padded`). Reused: the computed label,
   between. TESTED by lane jcfold [§4C], table (MN): text order day, name, year (the left's order is the
   compare's, not the text's); mnum's sets become name alternations; 4 rows; 2,232 subjects (years 2022-2027, 12
   names, days 1-31), 0 differ from the integer triple order.
9. (E-CAL, §12.5) SIMPLER: problem 4; no computed label, no `days_in` value macro with `$` parameters, no relation;
   a declared table of products (memory: selections as declared tables).
10. (E-NEAR (c), §12.7) THE SAME: "within 15 days" is arithmetic on dates; `d := days($b) - days($a)`, `(d:
    between(-15, 15))` stays. A joint condition `((a, b): within15)` would need a 2-ary set defined by a function: a
    new concept, not proposed.
11. (E-RFC, §12.6) THE SAME: the weekday is a function of three fields; `(wname.index: ==$wd)` stays.
12. (E-JSONL, §12.1) THE SAME for its fixed-width ISO dates (string order works); a non-fixed-width date inside
    the quotes would use `((year, month, day): padded(between(...)))` laid against the inner pattern's labels:
    better only for a case §12 does not have.
13. (E-IPV4, §12.3) THE SAME for octet validity; problem 3 is new ground it could not reach without labels.

Tally (of the problems tried): simpler 7 (1, 2, 3, 4, 6, 7, 9 against rev 19 or the existing language; 7 by the
default, J6), same 6 (5, 8, 10, 11, 12, 13), worse 0. BY G2'S CRITERION [§4F, OWNER-3: this tally was cited as G2's;
problems 1, 2, 3, 5, 6, 7 and 8 are tuple-compare instances, which the owner ranks as the TEST (G3), not as "other
problems"; 9 is 4 again]: the non-compare problems are 4 (= 9, E-CAL, SIMPLER, table (C4)), 10-13 (the same), and
the multi-field allowlist (§4A.5, untested): 1 simpler, 4 the same, 0 worse. Before the default (lane jointexp) 7 was worse: an absent optional field needed an
explicit alternative (B2) [§4C].

## 6. Where it breaks

[§4C: REWRITTEN to the ruled state. The exploration's B1-B5 are kept with their outcome.]

- B1 THE TUPLE MET "A RECORD IS NEVER A VALUE" (RULED, CF:851-852). SETTLED: the tuple as a value is accepted (J3,
  CF 09:42), the record ruling stands untouched (§4A.1: a tuple set is laid against nothing and has no names).
  Smallest example: `between((9, 0), (10, 0))`. What moves in the draft are three LEAN sentences that inferred an
  error from the ruling (§0.1 L45, the §5.4 `( e1, ... )` row, the condition row's "any other record"): §9.
- B2 OPTIONAL FIELDS CHANGE ANSWERS. Smallest example: `/(?<h>\d{1,2})(?::(?<m>\d\d))?/` with
  `((h, m): padded(between((9, 30), (11, 0))))` on `10`: rev 18-19 accept, the joint condition rejects. RULED (J6,
  CF 11:05): the unset label fails; rev 18's decided-prefix reading is withdrawn; the author who wants `10` in writes
  a default, `(h, m = 0)` (`10` and `11` in, `9` out, §4B), or the explicit alternative for "does not matter".
- B3 A MODIFIER CANNOT PICK COMPONENTS. Smallest example: `((h, name): padded(>= (9, "M")))` pads the NAME too
  (`0Mary` passes). RULED (J8, CF 11:27: "the form is 'do everything to both'"): a modifier acts on every part; a
  per-part modifier exists only for PRODUCTS (`(padded(S), T)`), not for dictionary-order sets. Workarounds: a
  computed number for the non-numeric field, or the author's pattern refusing leading zeros. A finer-grained transform
  is parked: `predicates_future.md` item 2.
- B4 SIBLING LOOPS HAVE NO PAIRING. Smallest example: `/(?:(?<h>\d),)*;(?:(?<k>\d),)*/ & ((h, k): R)`. RULED (J7, CF
  11:17): a compile ERROR naming the fix (text: item 5).
- B5 RELATIONS DEFINED BY A FUNCTION are out of reach of sets written in the language (E-NEAR, E-RFC); they need
  computed labels (existing) or a NEW set-comprehension concept (not proposed). Not a break of the joint condition,
  a boundary it shares with rev 19.
- B6 (NEW, lane jcfold) THE RECORD AT DIFFERENT DEPTHS, ZERO PASSES. Smallest example: `/(?<k>\d)(?:;(?<h>\d))*/ &
  (h: <5, k: 3 | 4 | 5 | 6 | 7)` on `9`: as the product case (J9 with J7's per-pass pairing) no pass, no tuple, HOLDS;
  as the draft's "`(major: 1, minor: >=4)` = `(major: 1) & (minor: >=4)`" (§4.1 :1546) and "the two spellings always
  agree" (§4.3 :1674) the once-set k is still tested, FAILS. 5 of 1,110 subjects differ (table (RZ)). RULED (J7,
  **zero-pass-record**, CF 12:45): FAILS; the outside label is tested once on zero passes, the draft's equality holds
  at every depth [§4E: was "A CONTRADICTION between the 11:17 + 11:35 rulings and ruled draft text: §8
  **zero-pass-record**, not resolved here"]. The ruled wording's own corners (an EMPTY set, the domain of "some
  value", the nested (NL) answers that move): §4E.

## 7. Consequences derived by the lane

Each is a lane's (jointexp's, updated by jcfold [§4C]), not a ruling; where a ruling has since made one true, it says
so.

1. The record `(h: S, m: T)` is the PRODUCT CASE of the joint condition: now RULED (J9); §4D checks it rule by rule.
2. Dictionary order is THE order of a tuple comparison set (J4); the per-part form is the product, both legal (J5).
3. The wrong-length gap (§13 O72) and the repeated-field gap (`compare.repeated`) become COMPILE ERRORS at the
   condition (an arity mismatch; a label twice on the left), with no library insight. The second reaches the record
   too (D26), now RULED (**label-twice**, CF 13:16) [§4F].
4. Strict compares are comparison sets (`>`), so review r17 F1's bug class (a `!` true where the compare cannot
   read) has no spelling in the compare; `!` keeps its single-label meaning and §13 O28 stays the one open question
   about it.
5. The looped compare means "every pair" per pass (RULED, J7); the looped warning's subject is now a hand-written `|`
   of conditions over labels that can repeat (RULED, J7).
6. Labels at different depths pair per pass of the deepest loop (J7, stated precisely in item 5); sibling loops are an
   error (RULED).
7. A library constraint over several fields is a SET, label-free: `office_hours`, `month_days`, `valid_ymd`,
   version policies, IP blocks; the author writes the labels in the condition. This is the mechanism's account of
   how it helps the larger language (G2): the same thing SQL row values do (`(a, b) IN ((1, 2), (3, 4))` is
   `((a, b): [(1, 2), (3, 4)])`), and a declared TABLE of products is a natural spelling for many-field validity.
8. A tuple whose label is unset does not exist, unless the author gave the label a default (RULED, J6); rev 18's
   decided-prefix order is withdrawn.
9. Arity makes `[9, 0]`-for-a-tuple a compile error instead of a silent "9 or 0".
10. Any number of fields is native (the built-in order; no recursion, no size suffix); first/rest is parked (J4).
11. (jcfold) On the value side a computed label is read `$dim`; a bare `dim` there is a binding, i.e. the computed
    label's macro, which no comparison atom takes: an ERROR naming `$dim` (§4C, the 11:32 consequence tested).
12. (jcfold) A default is on the value side (J2's refinement), so its bare name is a binding, a label's value is
    `$x`, and a name that is both a binding and a label means the binding there (§4B.1).
13. (jcfold) The per-part form has real uses (item 4) and cannot be told from a dictionary-order slip by the compiler;
    the slip is a BY DESIGN look-alike the draft must list (§9).
14. (jcfold) The k-label rule specialised to products reproduces every record rule of the draft (§4D; the one corner,
    zero passes at different depths, closed by J7's ruled sentence, CF 12:45 [§4E: was "but one corner"]): the
    record's semantics shrink to "J9", and the draft's record sentences become pointers.
15. (jcfold2) On zero passes a joint condition over a NON-product set reads as R's PROJECTION onto the labels
    outside the loop, which equals the hand expansion into a `|` of records on every case tried except a row with an
    EMPTY part (table (ZJ); §4E) [§4E].
16. (jcfix) Round jointcond's manager's readings, each labelled where it lands, none the owner's words [§4F]: every
    tuple component in its literal's domain (DOM, J4); a `$` component read by value (rev 18's LEAN); the zero-pass
    tuple tested by the plain condition and `all`, never counted by `some`/`count`/`occurs` (J7); a computed label
    is arity 1, a match-dependent tuple never bound (4A.4 (5)); a mixed record is the `&` of its entries (J1); a
    macro lifts to tuples when its result distributes over `|` (J8).

## 8. Questions for the owner

[§4C: REWRITTEN. The exploration's and tupleval2's lists are in git (c69929e4a) and the lane reports; unsetdef's
list of eight is answered below.]

ANSWERED, not re-asked (his words, CF 2026-11-16): **tuple-value** (09:42, "I am ok with the tuple as a value");
**tuple-anywhere** (09:49, "You could use them as you say"); **first-rest** (10:22, PARKED: "Let's park first/rest
but keep it in the wings in case we find a problem that needs a different way of composing"); **set-arity** (10:26,
"Set arity: yes. It's clean. I like it"); the default's mark (10:37, "Seeing = in examples I prefer it");
**default-set** (10:43, "We can punt, as you say, and throw an error"); **unset-component** (11:05, "unset-component:
yes"); **default-unused** (11:05, "default-unused: agree"); **joint-loops** (11:17, "I agree. Makes sense.");
**two-orders** (11:20, "I agree. They look sufficiently different to me and I like the control."); **modifier-lift**
(11:27, "modifier-lift: yes"); **colon-scope** (11:32, "colon-scope: yes with refinement: (a, b = c): ... the 'c' is a
binding et al"); **record-is-product** (11:35, "record-is-product: absolutely"); and, the three contradictions
below, [§4E] **zero-pass-record** (12:45, "zero-pass-record: I agree but save the notes in the future file. The issue
falls into the 'saving people from themselves' category that tools need to realistically consider": the outside
label is tested; J7, the wording the manager's, tested in §4E); **library-not-syntax** (12:48, "library-not-syntax:
agree. we've replaced the idea and I think with something much better": the 2026-11-14 TUPLE CONDITIONS ruling
(CF:648) WITHDRAWN BY NAME, the rest of that entry (CF:644-650: ARRAYS OF FILTERS, ENUMERATE) STANDING [§4F: was
"CF:644-650 WITHDRAWN BY NAME", the record's own range, RULING-4]; `lex_ge` and friends not kept as library macros, the manager's reading of "agree"); **retire-paused** (12:51,
"retire-paused: agree to split. But the pause on ^ is indefinite and requires real value other than 'override a
users own *'": the `lex_` names, the argument order and the first-library slot RETIRED to the superseded-direction
record, the joint condition taking the slot; the sigil PAUSED INDEFINITELY, out of rev 20's language;
reference-index and bound-reference suspended with it); [§4F] **label-twice** (13:16, "label-twice: agree an error.
And that means it's also unofficially parked in case some other meaning becomes valuable": a label named twice in
one condition is a COMPILE ERROR in both forms; the spelling stays free, `predicates_future.md` item 9).

PARKED (not questions; each with its trigger in `docs/design/predicates_future.md`): first/rest (item 1),
finer-grained transforms (item 2), a several-string default with `some(...)`/`all(...)` (item 3), taking one tuple
apart (item 4, which is **tuple-parts**); and the four ideas raised on the way to **zero-pass-record** (items 5-8)
[§4E].

CONTRADICTIONS FOUND (lane jcfold; each states both texts; [§4E] ALL THREE ANSWERED, CF 12:45-12:51, above; kept as
the record of the question asked):

1. **zero-pass-record** [§4E: ANSWERED, reading (b)]. The rulings: joint-loops (CF 11:17, record: "per-pass pairing by the innermost loop
   enclosing every named label, a label outside that loop having its one value on every pass"; "the condition holding
   when every pass's tuple is in the set") with record-is-product (CF 11:35: "every rule of the joint condition (...
   per-pass pairing in loops ...) holds for the record by definition"). The draft: "all of several conditions = one
   record: `(major: 1, minor: >=4)` = `(major: 1) & (minor: >=4)`" (§4.1, `predicates_draft.md:1546`; its AND RULED,
   CF:863, CF:866 (b)) and "For `all`/the plain condition the two spellings always agree" (§4.3 :1674, under SAME
   ITERATION BY RECORD, CF:915-917 accepted). They disagree only when the record's labels sit at different depths and
   the deeper loop runs zero passes: `/(?<k>\d)(?:;(?<h>\d))*/ & (h: <5, k: 3 | 4 | 5 | 6 | 7)` on `9` HOLDS by the
   rulings, FAILS by the draft (table (RZ): 5 of 1,110). Readings for the owner: (a) per-pass, vacuous on zero passes
   (the rulings as written; the draft's two sentences gain "at one depth"); (b) a label outside the pairing loop is
   tested once even when the loop runs zero times (the draft's equality kept; J7 gains a clause). The lane takes
   neither.
2. **library-not-syntax** [§4E: ANSWERED, withdrawn by name]. The ruling of 2026-11-14 (CF:644-650: "TUPLE CONDITIONS: a LIBRARY macro (`lex_ge([major,
   minor, patch], [1, 4, 0])`), no syntax"), carried in the draft as "Tuples as a library macro: RULED (CF:644),
   SUPERSEDES predx's tuple-on-the-left-of-`:` syntax (S12)" (§8 STATUS, `predicates_draft.md:2760-2761`), against
   record-is-product (CF 11:35: "the joint condition is the ONE mechanism"), whose left side IS a tuple on the left of
   `:` and whose order is built into comparison sets (J4, after CF 10:18, 10:22). The 00:31 entry (his own `(h,m):
   blah`) and the 00:35 GO come closest, but no entry withdraws CF:644 or S12's supersession by name. Not resolved:
   rev 20 needs a sentence from the owner (or the manager's reading of 00:31 + 11:35 as that withdrawal, labelled).
3. **retire-paused** [§4E: ANSWERED, split]. The direction of 00:06-00:09 was PAUSED, not reversed (CF 00:31: "rev 19 of the draft stands
   as the record of that direction"). Its RULED items: the other-side sigil (CF 00:06, "i think the sigil mark is
   better"), the `lex_` names (CF:1226, "tuple_names: a"), the argument order (CF:1253, "tuple-arg-order: subject low
   high"), the fixed-size compares in the first library (CF:1166, "tuple-compare: agree"), and the looped warning on
   compares (CF 00:09; MOVED by 11:17, so this one IS addressed). The joint condition leaves the first four no job
   (item 9), but no entry retires them. Rev 20 cannot both "stand as the record" and drop them. Not resolved: whether
   rev 20 RETIRES them (moved to a superseded-direction record) or keeps them PAUSED beside the joint condition, and
   whether the joint condition takes the tuple compares' place in the FIRST LIBRARY / phase 1 (CF:1166's slot).

STILL OPEN (each: reply either way):

1. **tuple-parts** (§4A.3): unchanged, NO USER while first/rest is parked: (A) a tuple used whole, or (B1) ONE tuple
   taken apart on the left of a binding. Nothing is built either way. Leaning: (B1) on record, (A) in practice; asked
   again when a use appears.
2. [§4F: was **label-twice**, ANSWERED CF 13:16, moved above.] **pairing-loop** (lane jcfold, item 5; RE-DRAFTED by
   round jointcond, the full plain-words draft in `docs/dev/lanes/jcfix_report.md`), three parts:
   (1) WORDING: confirm "the pairing loop is the DEEPEST loop that encloses any named label; every other named label
   lies in the same pass of it or outside it, and then has ONE value per pass; otherwise the sibling-loop error". The
   ruled words ("the innermost loop enclosing every named label, a label outside that loop having its one value on
   every pass", CF 11:17 record) read literally miss one label outside every loop and the nested case.
   (2) ZERO PASSES PER REACH: under zero-pass-record (CF 12:45) each reach of an inner loop that runs zero times gives
   its own tuple; for products this equals the `&` reading (table (ZN): 0 of 2,526 differ), and it MOVES 10 of
   jcfold's (NL) 73 answers (`4:;` held, now FAILS) [§4F: was "No answer changes on any case he was shown (table
   (NL): 73 subjects, 0 differ)"].
   (3) A PASS THAT NEVER REACHES THE PAIRING LOOP (round jointcond, SIM-5): `/(?:(?<h>\d)(?:-(?:(?<k>\d),)*)?;)*/ &
   (h: <5, k: <5)` on `3-2,;9;`: the text as written pairs nothing in the second pass and HOLDS, while the ruled
   `(h: <5) & (k: <5)` FAILS. Two candidate sentences, each with its matching single-label sentence: (W) "as a
   zero-pass reach: (h, EMPTY)", with "such a pass gives k zero iterations"; (Y) "k is unset in that pass: the pass
   FAILS (J6)", with "such a pass FAILS `(k: T)`". Table (UP), 241 subjects: W = `&` under its sentence (0 differ),
   Y = `&` under its sentence (0 differ); W vs Y 22; the text as written vs §4.2's per-match reading 8. `3-2,;4;`:
   W HOLDS, Y FAILS. Leaning: none stated here (the manager's).
3. **zero-pass-empty** (NEW, round jointcond: RULING-1/2, OWNER-2, SIM-6; the full draft in the jcfix report): when
   the joint set is EMPTY only through a value of the match, does a zero-pass match test the outside label? Smallest
   example, `/(?<a>\d)-(?<k>\d)(?:;(?<h>\d))*/`, subject `0-3` (a = 0, zero passes): `(h: <$a, k: 3)` HOLDS by the `&`
   reading and by lane jcfold2's split, FAILS by the record's unsplit wording and by the lean; `((h, k): < ($a, 0))`
   FAILS by the split, the unsplit wording and the lean (table (ZE)). The constant spellings (`(h: <0, k: 3)`,
   `((h, k): < (0, 0))`) are compile errors by the draft's narrowing-site rule (`predicates_draft.md:1941-1942`,
   LEAN). The manager's lean (round jointcond): ONE rule, "the outside labels' values must be possible under R for
   some value of the looped labels drawn from their groups' strings", with the empty-intersection error covering the
   constant spellings; the `&` equality then has one documented exception (a part empty only through a match value,
   on zero passes, FAILS). On jcfold2's populations the lean differs from the `&` reading on 0 of 1,110 (RZ) and 0 of
   2,526 (ZN), and from jcfold2's split on 0, 0 and 1 of (ZJ)'s 50 zero-pass subjects (`("x", 3) | (0, 5)` on `3`:
   the domain).

## 9. What rev 20 must change in predicates_draft.md

One row per draft section or numbered item, cited at rev 19 (`predicates_draft.md:N`, this worktree, cut from main
4ae1f9bdc; rev 19 unchanged since) [§4F: rows 47-54 NEW and cites widened after round jointcond's rev20 lens,
REV20-1..10]. "Ruling" names the CF entry of 2026-11-16 (`CF hh:mm`) or this note's J-rule; rows that hang on a
CONTRADICTION (§8) say so and must not be written until the owner answers [§4E: none is left; the three were answered
CF 12:45-12:51, and every row that hung on one is restated, marked "[§4E]"]. Every row is the lane's reading of what
the rulings require; the manager drafts rev 20.

| # | draft site | what changes | under |
|---|---|---|---|
| 1 | Changelog (`:3`) | a rev 20 entry: the joint condition as the one condition mechanism; the field-reference direction: the `lex_` names, argument order and first-library slot RETIRED, the sigil PAUSED INDEFINITELY (**retire-paused**, CF 12:51) [§4E] | all |
| 2 | §0 ruled-points tables (`:422-461`) | a new table "the entries after rev 19" with the 28 entries of 2026-11-16 (00:06-13:16), his words, what is the manager's, and round jointcond's manager's readings (§7 item 16), each labelled [§4F: was 27, 00:06-12:51; §4E: was 24, 00:06-11:35]; the new table goes after the rev-18 entries' table (an insertion point after `:461`, not a range: REV20-9) | all |
| 3 | §0.1 L37 (`:535`) | OPEN becomes DIFFERENT: ERROR: `(wname.index: ==wd)` is the bare-binding error, write `==$wd` | colon-scope 11:32 (C13) |
| 4 | §0.1 L45 (`:543`) | `f((1, 2))`: ERROR becomes "one argument, a pair" | tuple-value 09:42, tuple-anywhere 09:49 (§4A.1) |
| 5 | §0.1 L72-L81 (`:570-579`) | the ten field-reference rows lose their subject: those on the `lex_` names, the argument order or the first library move to the superseded-direction record; those on the sigil, reference-index and bound-reference are marked PAUSED INDEFINITELY, out of rev 20's language [§4E] ; the §0.1 prose after the table that discusses them, `:685-706` ("tuple compare (now in the library)" :693, "the tuple bodies pad every comparison" :694, the projection's entries :697-704, "C13's lean `$x`" :705), restated with rows 3, 28, 30 and 35 [§4F, REV20-3/9] | 00:31; retire-paused 12:51 |
| 6 | §0.1 new rows | `((h, m): (S, T))` vs `(h: S, m: T)` SAME (J9); `>= (9, 30)` vs `(>= 9, >= 30)` DIFFERENT: BY DESIGN (2,700 of 11,000 PADDED, table (O); 1,800 unpadded under DOM, table (DM)) [§4F]; `(9, 0)` vs `[9, 0]` ERROR (arity); `((h, m): R)` vs `(h, m: R)` ERROR; `(h, m = 0): R` vs `(h, m: 0): R` ERROR; `((h, m): R)` vs a hand `\|` of records over looped labels DIFFERENT: WARNING (the moved warning); `(9, 0)` vs `f(9, 0)` vs `(h: 9, m: 0)` vs `((h, m): ...)` BY DESIGN (position); `t2 & ((h, m = 0): R)` vs `t2 & ((h, m): R) \| (h: 10)` DIFFERENT: BY DESIGN (§4B.4); [§4F, CENSUS-4] `[(9, 0), (10, 30)]` vs `([9, 10], [0, 30])` DIFFERENT: BY DESIGN (a union of tuples vs a tuple of unions: 3 vs 6 of 11,000 padded, table (DM)); [§4F, CENSUS-5] `t2 & [m = 0]` vs `t2 & (m = 0: S)` DIFFERENT (an array's `=` NAMES a label, a default READS one: 244 of 11,110, table (DK)), with the lane's proposed WARNING `label.both_sides` (not ruled, renamed from `label.twice`); the unguarded hand slice `t2 & ((h, m): R) \| (h: 10 \| 11)` vs the default DIFFERENT, no diagnostic possible (99 of 11,110, table (DG)) | J1-J9 |
| 7 | §0.2 phase 1 (`:751-756`) | "the fixed-size tuple compares ARE in the first library ... and their bodies use ... the field reference `^h`": RETIRED (CF:1166's slot); the joint condition takes that first-library slot in phase 1 [§4E: was PENDING **retire-paused**] | retire-paused 12:51 |
| 8 | §0.3 words (`:777`) | the **field reference** word row goes or is marked paused; new words: TUPLE SET, ARITY, JOINT CONDITION, DEFAULT (of a label), PASS ; the glossary `record` row (`:793`, "the written `( ... )` laid against fields (§5.4); never a value") gains "the joint condition's product case" (J9) [§4F, REV20-10] | J1-J7; record-is-product 11:35 |
| 9 | §2.1 two value kinds (`:848-852`) | every SET (every rx-kind value) carries an arity; today's rx are arity 1; macros as today (CF:858); still two kinds [§4F: was "every value is a set of tuples", RULING-5] | set-arity 10:26 |
| 10 | §2.4 comparisons (`:994-1017`) | a tuple atom, dictionary order, each part by its literal; EVERY component in its literal's domain, the ones after the deciding component included (DOM; the manager's reading, round jointcond, DICT-DOMAIN) [§4F]; a `$` component read by its VALUE, leading zeros ignored, rev 18's LEAN pending O27, moved here from §8 `:2554-2563` (row 28) [§4F, DOLLAR-COMPONENT]; the per-part form is the product | first-rest 10:22 (J4), two-orders 11:20 (J5) |
| 11 | §2.7 (`:1356-1360`) [§4F: was `:1358`, REV20-3] | the rev 19 example `lex_between2([^h, ^m], ...)` becomes `((h, m): padded(between((9, 0), (10, 0))))`; "the library's tuple compare (§8 TUPLE COMPARISONS)" and the sigil/O71 clause go | J4 |
| 12 | §3.5 (`:1506-1509`) [§4F: was `:1506-1507`, REV20-2] | "an ARRAY OF FIELD REFERENCES ... is a field reference": goes with the sigil, PAUSED INDEFINITELY, out of rev 20's language [§4E]; an array of tuples IS a tuple set (an array of X is an X) | 00:08 + J3; retire-paused 12:51 |
| 13 | §4.1 THE ONE EXCEPTION (`:1528-1539`) and its STATUS (`:1575-1579`) | REMOVED (no parameter on the left of `:`); the entry form becomes `(p1, ..., pk): R` with the colon's scope (J2) and a default `name = v` (J6) | colon-scope 11:32, unset-component 11:05; retire-paused 12:51 (the exception's only use, a parameter bound to a field reference, goes with the paused sigil) [§4E] |
| 14 | §4.1 records (`:1541-1556`) | the record DEFINED as the product case (J9); "`(major: 1, minor: >=4)` = `(major: 1) & (minor: >=4)`" (`:1546`) KEPT, holding at every depth (J7's zero-pass sentence) [§4E: was PENDING **zero-pass-record**] ; a MIXED record (a joint entry beside others) is legal and the `&` of its entries, a label in two entries the label-twice error (the manager's reading, round jointcond, MIXED-RECORD) [§4F] | record-is-product 11:35; zero-pass-record 12:45; label-twice 13:16 |
| 15 | §4.2 (`:1590-1592`, STATUS `:1613-1625`) | "a condition naming an unset label fails" for any k, "unless the author wrote a default"; `label.unset`'s text names both fixes; `default.unused` added | unset-component, default-unused 11:05 |
| 16 | §4.3 SAME ITERATION BY RECORD (`:1668-1677`) | per-pass pairing (J7) as the rule, the record its product case; `:1674`'s "always agree" KEPT (true at every depth under J7's zero-pass sentence) [§4E: was PENDING **zero-pass-record**]; `:1677`'s pointer to O56 becomes J7; the GROUP-ZERO sentence (the zero-pass tuple is tested by the plain condition and `all`, never counted by `some`/`count`/`occurs`; the manager's reading, round jointcond) [§4F]; optionally the table-of-passes model (item 5, OWNER-7) as §4.3's account of loops [§4F] | joint-loops 11:17; zero-pass-record 12:45 |
| 17 | §4.4 (`:1737-1738`), and the bare spellings at `:1731` (`rfc & (wname.index: ==wd)`), `:1840` (§4.6) and `:3320` (`padded(<=dim)`, §12) [§4F, REV20-7] | "the bare spellings in E-CAL and E-RFC (`<=dim`, `==wd`) are §13 C13" becomes: read with `$`; bare is the binding error; every bare site becomes `$wd`/`$dim`; and one sentence: a computed label is ARITY 1, a match-dependent tuple is written inline or passed, never bound (an error naming the inline form; the manager's reading, round jointcond, TUPLE-BINDING) [§4F] | colon-scope 11:32; set-arity 10:26 |
| 18 | §5.2 heads (`:1937-1938`) | one sentence: a label default is the same `name = v` in a condition's reference list (§4B.3's single rule) | `=` 10:37 |
| 19 | §5.4 `( e1, e2, ... )` row (`:2013`) | position (b) restated: a record in a condition is the joint condition's product case; still never a value | record-is-product 11:35 |
| 20 | §5.4 `( label: S, ... )` row (`:2014`) | "Any other record in value position is an error" narrowed to labelled entries; the joint condition in value position is a macro too | tuple-value 09:42 |
| 21 | §5.4 new rows (after `:2016`) | `( p1, ..., pk ) :` a tuple of references; `( e1, ..., ek )`, k >= 2, in value position, a TUPLE SET; the head count "`( )` has four rows" (`:1998`) becomes SIX on its own basis (the four plus the reference tuple and the value tuple; heads, the left of `:=` and the error shapes stay folded; the default adds no row) [§4F: was "updated (§4A.7)", CENSUS-6]; the condition row's discriminator "entries `p: S` or `p = v: S`" and the L43 row's "an `=` entry with no `:`" [§4F, CENSUS-1] | J1, J3 |
| 22 | §5.4 `=` row (`:2017`) | a fourth position: a default at a label left of `:` (value side, J2's refinement); the ENTRY EXTENT sentence gains: "an entry may hold both, `p = v: S`; `&` and `\|` bind tighter than `=` and `:`, so `(m = 0 \| 5: S)` is a two-string default, an error" [§4F, CENSUS-1] | 10:37, 11:32 |
| 23 | §5.4 `:` row (`:2018`) | the left: a path or a tuple of references; "in a macro body the path may arrive through a parameter bound to a field reference" removed (the sigil PAUSED INDEFINITELY, out of rev 20's language) [§4E] | J1; retire-paused 12:51 |
| 24 | §5.4 comparison row (`:2030`) | "before ONE atom": the atom may be a tuple (dictionary order) | J4 |
| 25 | §5.4 `^` row (`:2035`) and STATUS (`:2048-2052`) | the other-side sigil `^h`: out of rev 20's language, recorded as PAUSED INDEFINITELY, returning only for a use with real value; rejecting the empty case of the author's own `*` loop (`some(^h)`) is not such a use (CF 12:51) [§4E: was "REMOVED or marked PAUSED"] | retire-paused 12:51 |
| 26 | §6.1 levels (`:2139`) | a joint condition on a constant tuple set is default level: its SET is a finite union of products; for set-once labels the condition is the `\|` of the rows as records, for looped labels the union is taken per pass inside the pairing loop's item (NOT "a `\|` of records", the moved-warning look-alike) [§4F, SIM-4]; with `$` parts a §4.6 relation | LEVEL (§2 here; tables (X), (RC), (SE)) |
| 27 | §7.1 warnings (`:2270-2272`) | `compare.looped` (a compare's field can repeat) becomes the warning on a hand-written `\|` of conditions whose labels can repeat (its name the spelling step's); `default.unused` added; `compare.repeated` (proposed) gone (an error at the condition, label-twice RULED 13:16 [§4F]); the lane's proposed `label.both_sides` (§4B.4; renamed from `label.twice`, which names the owner's different ruling) listed as a PROPOSAL, NOT RULED [§4F, CENSUS-5] | joint-loops 11:17, default-unused 11:05 |
| 28 | §8 TUPLE COMPARISONS (`:2415-2620`): the six `lex_` names and bodies (`:2433-2442`), worked rows (`:2480-2487`), the strict spelling (`:2544-2546`), CAVEATS (`:2574-2619`) incl. caveat (5) the DECIDED-PREFIX order (`:2594`) and caveat (6) looped (`:2608-2616`) | the family becomes the comparison sets: `>= (9, 0)`, `between((9, 0), (10, 0))`, `> (9, 30)`; the decided-prefix order WITHDRAWN; the looped caveat restated per pass (zero passes: J7's sentence); the six names and their bodies RETIRED to the superseded-direction record, not kept as library macros; the value LEAN for `$` bounds (`:2554-2563`) is NOT retired with them: it moves to §2.4 (row 10) [§4F, DOLLAR-COMPONENT] [§4E: was PENDING **retire-paused** (a library may still name `lex`-style helpers, none needed)] | J4-J7; 11:05; library-not-syntax 12:48, retire-paused 12:51 |
| 29 | §8 ANY NUMBER OF FIELDS (`:2620-2641`) | the recursion form `lex_ge(n, s, lo)` / `lg` has no job: any k is native (J4); first/rest parked (`predicates_future.md` item 1) | first-rest 10:22 |
| 30 | §8 THE PROJECTION (`:2642-2678`) and THE FIELD REFERENCE (`:2679-2745`, table (B), the census) | no job: the projection and the field reference go with the sigil, PAUSED INDEFINITELY (out of rev 20's language) [§4E: was PENDING **retire-paused**] | 00:31; retire-paused 12:51 |
| 31 | §8 STATUS (`:2757-2771`) | "Tuples as a library macro: RULED (CF:644), SUPERSEDES predx's tuple-on-the-left-of-`:` syntax (S12)" moves to the superseded record: CF:648 (the TUPLE CONDITIONS sentence) WITHDRAWN BY NAME, the rest of the CF:644-650 entry (arrays of filters, enumerate) STANDING [§4F: was "CF:644-650", RULING-4], a tuple left of `:` is ruled syntax (J1-J9) [§4E: was PENDING **library-not-syntax**]; the rest restated to the joint condition | library-not-syntax 12:48 |
| 32 | §12 census and E-CAL (`:3231`, `:3439-3455`) | `<=dim` becomes `<=$dim` (C13 closed); optionally the declared-table form `((month, day): month_days) \| (year: leap, month: padded(2), day: 29)` as a second spelling (table (C4), SIMPLER) | colon-scope 11:32; §5 problem 4 |
| 33 | §12.6 E-RFC (`:3456-3469`) | `==wd` becomes `==$wd` | colon-scope 11:32 |
| 34 | §12 census (`:3340-3343`, `:3360-3362`) [§4F: was `:3360-3361`, REV20-8] | the tuple-compare and field-reference rows restated (no §12 case uses either); `:3340-3343`'s "the tuple family" and its REV 17 census note restated; `:3362`'s positional `X[...]` row loses the compare bodies and O75 | J1-J4 |
| 35 | §13 C13 (`:3741-3744`) | RESOLVED: values with `$` on the value side; bare is the binding error | colon-scope 11:32 |
| 36 | §13 C25 (`:3760-3778`) [§4F: was `:3760`, REV20-4] | RESOLVED by the joint condition; its "a library macro, no syntax" premise (CF:648) WITHDRAWN (CF 12:48), with its REV 16/17 text (`:3770-3778`: the first library, the names, the projection, O71) [§4F] [§4E: was PENDING **library-not-syntax**] | library-not-syntax 12:48 |
| 37 | §13 O56 (`:4118-4125`) | (1) RULED via J7 + J9 (with **pairing-loop**'s wording); (2) unchanged | joint-loops 11:17 |
| 38 | §13 O69 (`:4426-4440`) [§4F: was `:4426`, REV20-4] | the any-number-of-fields item CLOSED: native in the built-in order | J4 |
| 39 | §13 O72 (`:4527-4534`) | CLOSED: a wrong length is an arity error | set-arity 10:26 |
| 40 | §13 O73, O74 (`:4535-4547`) | O73 stays ANSWERED; O74's warning MOVED (J7) | 11:17 |
| 41 | §13 O75, O76 (`:4549-4565`) and O71 (`:4517-4524`) with the heading `:4548` [§4F, REV20-6] | SUSPENDED with the sigil (**reference-index**, **bound-reference**), out of rev 20's language; O71's "RESOLVED in rev 19 ... by a SIGIL" marked overtaken (the sigil PAUSED INDEFINITELY) [§4F] [§4E: was "WITHDRAWN as moot ..., PENDING **retire-paused**"] | retire-paused 12:51 |
| 42 | §13 DECIDED (45), (46), (49)-(55), (57)-(66) (`:4244-4285`) [§4F: was (45), (54), (55), (58), (59), (61)-(66), REV20-5] | each restated or withdrawn: (55) the decided-prefix order withdrawn by ruling (11:05); (46), (57) the wrong-length call: an arity error (O72 closed); (49)-(53) and (60) the projection, the bodies' index, bounds and levels and the section lean: retired with the bodies; (56) a bound read by value SURVIVES in the comparison sets (row 10); (58) a label twice becomes an error at the condition (**label-twice**, RULED CF 13:16 [§4F: was open]); (65) `compare.looped` moved; the field-reference ones: those on the `lex_` names, argument order or first library RETIRED, those on the sigil PAUSED INDEFINITELY [§4E: was PENDING **retire-paused**] | 11:05, 11:17; retire-paused 12:51; label-twice 13:16 |
| 43 | §13 owner questions (10), (12), (13), (15) (`:4576-4602`) and (16), (17) (`:4604-4610`) [§4F: was (16), (17) only, REV20-6] | (10), (12): RETIRED with the names and the first-library slot (retire-paused); (13): overtaken (sigil PAUSED INDEFINITELY); (15): the warning MOVED (J7; O74 is row 40); (16), (17) suspended with O75, O76 (the sigil PAUSED INDEFINITELY); each ANSWERED record stays as history with a superseded-by pointer; new entries for the 2026-11-16 answers (tuple-value through label-twice, 13:16 [§4F]) [§4E: was "moot ... (PENDING **retire-paused**)", "through record-is-product"] | all; 12:45-12:51 |
| 44 | §13 new items | **tuple-parts** (open, no user); **pairing-loop** (re-drafted in three parts by round jointcond); **zero-pass-empty** (NEW, round jointcond) [§4F: **label-twice** was listed open; RULED CF 13:16, an error, now a DECIDED entry] [§4E: "the three CONTRADICTIONS until answered" removed: answered CF 12:45-12:51] | §8 |
| 45 | §4.2 THE BOUNDARY (`:1595-1606`) and §4.3 (`:1659-1660`) [§4E: NEW row] | the zero-pass sentence for several labels, the MANAGER'S wording VERBATIM (CF:1553-1557, J7) [§4F: was restated with a "non-product" clause, which is lane jcfold2's repair, RULING-1]; the GROUP-ZERO sentence (row 16) [§4F]; "never reached" in §4.2's sense, the deepest construct entered (an inner loop under an outer loop that ran zero passes has zero passes, not unset) [§4F, SIM-2]. NOT WRITTEN until the owner answers: an R empty only through a match value and the domain of "some value" (**zero-pass-empty**), a pass that never reaches the pairing loop (**pairing-loop** (3)) [§4F: was "§4E's three corners ... want a sentence each"] | zero-pass-record 12:45; zero-pass-empty, pairing-loop (open) |
| 46 | a superseded-direction record (new appendix or history file) [§4E: NEW row] | the `lex_` names (CF:1226), the argument order (CF:1253), the fixed-size compares in the first library (CF:1166), and the 2026-11-14 "TUPLE CONDITIONS: a LIBRARY macro ..., no syntax" (CF:648; the rest of the CF:644-650 entry stands [§4F, RULING-4]), each with the ruling that retired or withdrew it; the sigil (CF 00:06) listed as PAUSED INDEFINITELY with its bar (CF 12:51) | library-not-syntax 12:48, retire-paused 12:51 |
| 47 | §14 Non-goals (`:4621-4625`) [§4F: NEW row, REV20-1] | "Tuples: no tuple VALUE kind; a tuple comparison is spelled over arrays at fixed sizes: RULED (rev 16-17: library macros ...) ... no tuple value is created" is FALSE under J3 and the CF:648 withdrawal: restated as "a tuple SET is a value of arity k (J3); no third value kind (set-arity)" | tuple-value 09:42, set-arity 10:26; library-not-syntax 12:48 |
| 48 | §3.2 tool 1 (`:1435-1438`) [§4F: NEW row, REV20-2] | the paragraph ON A SPELLED ARRAY OF FIELD REFERENCES (`s[k]` on references, OPEN O75) goes with the sigil, PAUSED INDEFINITELY, out of rev 20's language | retire-paused 12:51 |
| 49 | §7.1 `compare.width` text (`:2810`) [§4F: NEW row, REV20-3] | "or, since rev 16, the tuple compare (§8 TUPLE COMPARISONS ...)" becomes the joint condition's comparison set (`((h, m): padded(...))`) | library-not-syntax 12:48, retire-paused 12:51 |
| 50 | §13 O47 (`:3987-3991`), O68 (`:4420`, `:4442-4457`) [§4F: NEW row, REV20-4] | O47's premise (C25 reading (B), `lex_ge3`) is gone: CLOSED as moot (any k native, J4); O68's "BEHIND the tuple compare, which is in the first library" and its `tuple_between2(...)` sketch restated to the comparison sets | J4; retire-paused 12:51 |
| 51 | C13's other premises: §0.1 `:705`, C25 `:3764`, `:4096`, O68 `:4456` [§4F: NEW row, REV20-7] | each cites C13 as open; C13 is RESOLVED (row 35): the sentence becomes "`$x` reads a label's value on the value side" | colon-scope 11:32 |
| 52 | §1 libraries list (`:831`) [§4F: NEW row, REV20-8] | "the fixed-size tuple compares (2 and 3 fields, rev 16; decomposed into a projection and an array compare, rev 17)" becomes the joint condition in the first-library slot | retire-paused 12:51 |
| 53 | §2.7 filter modifiers (`:1276`) and the §5.4 hole row [§4F: NEW row, OWNER-5] | WHICH MACROS LIFT to tuple sets: a macro whose result distributes over `\|` in its argument (checkable from its body), as `padded` does; a non-distributing body is the arity error (J8; the manager's reading, round jointcond) | modifier-lift 11:27 |
| 54 | §4.2 (after THE BOUNDARY, `:1595-1606`) [§4F: NEW row, OWNER-6, PLAN] | ONE declared ABSENCE TABLE: rows = the absence state (never reached; an alternative not taken; an iteration skipped the label; a reached loop, zero passes; a label outside the loop while the loop has zero passes; a pass that never reaches the pairing loop), columns = the condition shape (single label, record, joint non-product, the `!` forms) x default or none, each cell the answer and its ruling; replaces the scattered sentences, NO answer changes; the parked `predicates_future.md` items 3, 5-7 each become one cell | the absence rulings (CF:997-1000; 11:05; 12:45) |
