# CRITIC FIXIND: predspec20 findings

## Findings

### FIXIND-1 — "possibly none" is not what the mark (or `all`) means: the gloss rev 20 attaches to `(g?: S)` / `all` is false on two planted cases
CONFIRMED. Rev 20 glosses the mark and `all` as "every, possibly none" at §2.6 l.1353 ("\"Every hit, possibly none\" is
written with the mark, `(g?: "x")`, or `all((g: "x"))`"), §2.6 STATUS l.1439, §4.3 REASONING l.2111 ("\"every,
possibly none\" is `all`, rev 20"), §0.1 L16 l.624, §13 C-entry l.3899 ("\"possibly none\" is the mark `n?`") and the
r10 FIXB-9 note l.4567. The mark has ONE kind of absence (ruled point (1)): it cannot tell "no hit" from "a hit
without g", and it reads F1 over DOM, so it is neither "every" nor "possibly none":
(a) a hit WITHOUT g passes: `occurrences(/(?<g>a)?b/)` (the §2.6 pattern of l.1327-1329), spans over {a,b} length
0-6: "every hit's g is `a`, possibly no hit" vs `(g?: "a")`: 94 of 127 differ (`b`, `abb`: one hit lacks g; the mark
HOLDS because DOM(g) = {a}); ENGINE-RUN (fixind_drill.py (D2): natural = `(?!b)(?![ab]*bb)[ab]*`, mark = always; 254
cases, 0 differ, 0 engine disagreements). Rev 20's own §4H.4 record says the same (`(g?: "x")` on `ab` HOLDS).
(b) "none" does not make it vacuous: `all((n: <0))` FAILS on `''` (rev 20 l.2039, by F1), where "every n is below 0,
possibly none" holds.
The "0 of 5,461" at l.1354 holds only because (OC)'s `r` has g REQUIRED in the hit (absimpact_check.out l.66); the
sentence is stated generally. The DOM-free spelling of "every hit, possibly none" EXISTS and uses no mark:
`occurs.none(!(g: S))` (unmarked `!` holds on an absent g, so a g-less hit is counted): 0 of 127 differ (D2).
Severity: design (a gloss an author will follow, attached to a new construct; "saving people from themselves").
Effort: small (replace the gloss at six sites by what the mark says: "every pass where the label is present is in S;
a pass without it passes when some value in DOM would do"; name `occurs.none(!(g: S))` as "every, possibly none").
Blast radius: §2.6, §4.3, L16, §13 (C28 neighbourhood, r10 FIXB-9 note); any future reader of `all`.

### FIXIND-2 — the worked "one-condition spelling" `occurs.none(((h, m?): !R))` is ill-formed as written and does not mean its stated intent outside one R
CONFIRMED. §4.3 l.2040-2042: "`occurs.none(((h, m?): !R))`, R = `(h: <10, m: <30)`" for "the empty list passes, an
item without minutes fails".
(a) R is a LABELLED record standing right of `:`. J1 (l.1743): "R names NO label: it is a plain set"; §5.4 l.2436: a
`( label: S, ... )` in value position is a CONDITION (a macro), so `!R` is a negated condition, not a tuple set.
Written as rev 20 states it, the example is the arity/value-position error; meant: `!(<10, <30)` (the J9 product).
(b) The mark makes the answer depend on DOM(m), so "an item without minutes fails" holds only when DOM(m) reaches
outside R. Row 66 of the §9 table asked rev 20 to write that dependence "in one line" (R' = `(h: <10, m:
padded(<100))`); rev 20 does not (grep `padded(<100)`: 0 hits). Run (fixind_drill.py (D5), COMPUTED over 1,111 lists
of `/(?:(?<h>\d+)(?::(?<m>\d\d))?,)*/`, every subject whole-matched in both engines): with R the marked form gives the
wanted answers on all 1,111; with R' it differs on 71 (`3,`, `3,3,`, `3,3:15,`: a minute-less item PASSES).
The intent has a spelling with NO mark and NO DOM dependence: `occurs.none(!((h, m): R))` (unmarked, `!` outside:
an item lacking m makes `((h, m): R)` FAIL, so `!` holds and the item is counted): 0 of 1,111 differ under R AND R'.
So the example that CLOSED §4G.6 (5) / 14:50 (f) is the DOM-sensitive one of two spellings, and the DOM-free one is
the plain `!` the draft already defines (l.1904-1905).
Severity: design (the closing example of a formerly open shape) + doc (ill-formed R). Effort: small. Blast radius:
§4.3 l.2040, joint_condition.md §4H.4 (same text), any acceptance case built from it.

### FIXIND-3 — with the mark, the two spellings the label-twice error offers are not the same condition: `(h?: A) & (h?: B)` != `(h?: A & B)`
CONFIRMED. §0.1 L92 (l.700): "`(h: A, h: B)` vs `(h: A & B)` DIFFERENT: ERROR ... `(h: A) & (h: B)` and `(h: A & B)` are
the spellings". Unmarked they agree (both need a text). Marked, the general form (l.1863-1866) chooses a witness from
DOM(h) PER CONDITION, so two conditions choose two witnesses: A = `<5`, B = `>5`:
`/(?<h>\d)?x/` on `x`: `(h?: <5) & (h?: >5)` HOLDS (3 and 7), `(h?: <5 & >5)` FAILS (empty set): 1 of 11 differ;
`/(?:(?<h>\d),)*/` on `''`: the same split, 1 of 111 (fixind_drill.py (D1), ENGINE-RUN 22 cases, 0 differ; DOM(h)
by running). The same with `all`: `all((g: <5)) & all((g: >5))` HOLDS on zero passes, `all((g: <5 & >5))` FAILS.
So the error's fix hint, applied to a marked label, picks between two different answers silently; the record =
`&` equality the draft relies on (row 68) is stated for DISTINCT labels only and is not touched, but `&` of
conditions on ONE label stopped distributing over `&` of sets the day the mark arrived. No look-alike row states it.
Severity: design (a new look-alike; the hint of a RULED error points at it). Effort: a look-alike row and one
sentence in L92 ("marked: write `(h?: A & B)`; the two-condition form lets each condition pick its own value"), or the
general-form choice in FIXIND-7. Blast radius: L92, §4.2 general form, every library that `&`s two conditions on one
optional label (`office` & `lunch` on `t2`'s m, say).

### FIXIND-4 — the never-absent-mark warning (and §4.2 (f)'s merged warning) fires on the marks `all` inserts, including rev 20's own "one way to mark through a macro"
CONFIRMED (by the text; the never-absent fact is the draft's own). §7.1 l.2714-2716: the warning fires on "a mark `h?`
on a label that can never be absent where the condition reads it". §4.3 l.2033 / L93: `all(c)` IS c with every label
it names MARKED. §4.2 (e3) l.1964-1967 offers `t2 & all(office_c)` as "the one way to mark through a macro" and says
"(h is never absent in `t2`)": by the two definitions the program carries a mark on h, a label that can never be
absent, so it draws the warning (and the (f) merged "the candidate set of h is never consulted"). The same for every
`all(c)` over a condition that names any required label (`isodate & all((year: S))`), i.e. most uses of `all` over a
record of a fixed-shape pattern. Neither §7.1 nor §4.3 exempts marks a macro expansion inserts; the nearest ruled
precedent says the opposite for a sibling warning: `anchor.whole` has "no exemption" for "text a macro body writes"
(l.2724-2725, CF:1154), and `all` is a library/prelude name (lean, l.2130-2131). The warning's message is a semantic
claim about the author's mark ("adds nothing"), planted where the author wrote none.
Severity: design (a diagnostic that fires on the recommended spelling). Effort: one sentence: the warning reads only
marks written at the label (not those `all` adds), or `all` is defined by the general form (D = DOM for each label)
rather than by inserting marks. Blast radius: §7.1, §4.2 (e3)/(f), §4.3, L93.

### FIXIND-5 — the widened `label.unset`: its third named fix does not silence it, its first fix inverts `some`, and (e2) hands it a case none of its fixes can be written for
CONFIRMED (by the text, the answers from the draft's own rows). §7.1 l.2707-2712: fires "wherever a label a condition
names can be ABSENT ... unless the label is marked or defaulted; its text names the THREE fixes, `h?`, `h = v`, an
alternative without h".
(a) THE THIRD FIX STILL WARNS. The draft's own third meaning, `t2 & (((h, m): R) | (h: 10))` (L90 l.693, table (TM2),
§4.2's "three meanings"), is exactly "an alternative without m"; its first alternative still names m unmarked and
undefaulted where m can be absent, so the exemption clause (two controls only) fires the warning on the program
that took the warning's advice. Same for L97's slice, whose row says the warning "names the default as the fix".
(b) THE FIRST FIX INVERTS A GROUP QUESTION. Inside `some(...)` the warning fires on a pass that lacks the label (a hit
of `/ab(?<g>[xy])?/` without g: "where the condition reads it"). Its fix `g?` makes that hit COUNT (r28 E, l.2034):
`some((g?: "x"))` HOLDS on `ab`, a span with no `x` at all (joint_condition.md §4H.4: "`(g?: "x")` and `some((g?:
"x"))` both HOLD"). The unmarked `some((g: "x"))` FAILS there, which is what "some hit is x" means. A warning whose
named fix changes "some hit is x" into "some hit is x or lacks g" is the "saving people from themselves" criterion
(§4H.9) run backwards. Whether it fires on a group question's zero passes is also unsaid (§4.3: "zero passes give no
pass to count").
(c) `$a` (§4.2 (e2) l.1959-1960: "`label.unset` covers it"): the mark is written only at a label LEFT of `:`
(l.1854-1856) and whether a default reaches `$a` is OPEN (l.1961-1963), so for `(b: >$a)` fixes 1 and 2 cannot be
written; only the alternative remains. And the mark's reach to `$a` is a three-way open question, not the
default's alone: FIXIND-6.
Severity: design. Effort: small (exempt a label every alternative of which either controls or omits; scope the
warning out of group questions or name `!`/unmarked as the fix there; give (e2) its own text). Blast radius: §7.1,
§4.2 (e2), §4.3, L90, L97.

### FIXIND-6 — (e2)'s open item names only the default reaching `$a`; the MARK has the same question plus a second one (one witness or two), with three different answers
CONFIRMED. §4.2 (e2) l.1961-1963: "NOT DECIDED: whether a default written for a in the same condition reaches `$a`
... left OPEN (§13)". The mark, written for a in the same record, raises the same question and the general form
(l.1863-1866: "some choice of one text from each absent label's D") does not say whether the entry `a?: S` and the
value-side `$a` share that ONE choice. Three readings, run (fixind_drill.py (D4), `/(?<a>\d)?-(?<b>\d)/`, 110
subjects, captures from both engines, DOM(a) by running):
`(a?: <3, b: >$a)`: no-reach (e2's D = {} for `$a`) holds on 24, shared witness 33, a witness each 33; split on 9
(`-1`..`-9`: F / H / H).
`(a?: >7, b: >$a)`: no-reach 1, shared 2, independent 10; split on 9 (`-1`: F / F / H).
So the three are pairwise distinct over the two conditions, and the "independent" reading is the one the general
form gives by default if `$a` is read as a second use of a.
Severity: design (an undefined item the round was asked to find; (e2) as written lists one of the two controls).
Effort: one line in (e2) and its §13 entry. Blast radius: §4.2 (e2), §13, §4.6 relations (`x: <$y`) on an optional y.

### FIXIND-7 — DOM(h) "of the pattern": a NARROWED operand is a pattern too; read off the rx, DOM breaks the mark-domain principle (*) it was chosen to satisfy
CONFIRMED (the split); SUSPECTED (the circularity). §4.2 l.1874-1876: DOM(h) = "the values h can take in some match of
the pattern ... for a group label, the strings its group can capture in some match"; (b) l.1933-1939 keeps it "a
property of the pattern (one table per label, priced once)". The principle (l.1881-1884): "two patterns that match
the same subjects and set their labels the same way answer every condition alike" (*).
Planted pair: `t2m := t2 & (m?: padded(<60))` (a library "valid minutes, optional" built the ordinary way, a
condition on a pattern) and `t2x := /(?<h>\d{1,2})(?::(?<m>[0-5]\d))?/`. Over all 11,110 `t2` subjects they match the
same subjects with the same labels (11,110 of 11,110, both engines). With `(m?: padded(>=60))`: DOM read from t2's
rx (100 values) vs t2x (60): 110 of 6,710 matching subjects differ (every minute-less one, `9`: HOLDS vs FAILS)
(fixind_drill.py (D3)). So (*) forces DOM over the operand AFTER its conditions, i.e. DOM depends on the other
conditions in the `&` chain, not on "the pattern" alone; "one table per label, priced once" does not survive, and
with marked conditions on the same label in one chain (`X & (h?: <3) & (h?: >7)`) DOM is defined through the very
conditions it decides (a fixed point; on `x` the empty-DOM and the rx-DOM readings give FAILS and HOLDS). The (b)
"match-context" question the draft does raise is the per-MATCH half of this; the per-OPERAND half is not raised.
Severity: design (the domain is a manager's reading under a RULED principle; this is a planted counter-case to it).
Effort: a sentence choosing "the operand the condition meets, with every OTHER condition of the chain applied" and
saying what happens for marks on one label in one chain, or an owner question. Blast radius: §4.2 DOM, (a)'s
approximation procedure, (b), every library pattern built as `rx & (conditions)`.

### FIXIND-8 — phase 1: the slot sentence puts SYNTAX in a LIBRARY slot and is silent on the mark, the default and tuple values, while `all` (IN, ruled) now depends on the mark
CONFIRMED (by the text). §0.2 l.894-897: "REV 20: the joint condition takes the first-library slot in phase 1"; §1
l.983: "the joint condition's COMPARISON SETS in the first-library slot". The two sites say different things fill
the slot (the joint condition, which library-not-syntax 12:48 made RULED SYNTAX, J1; or the library comparison sets
`>= (9, 30)`, `between((9, 0), (10, 0))`). Neither says whether the pieces rev 20 adds with it are phase 1: tuple
values `(9, 30)` (tuple-value 09:42), the label default `h = v` (J6), the OPTIONAL MARK `h?`. But `all(...)` is IN
phase 1 by ruling (l.876-878, CF:922-924), and rev 20 DEFINES `all(c)` as c with every label marked (l.2033, L93),
so the mark's whole semantics (DOM(h) as the values h can take, §4.2 (a)'s under/over-approximation and its
"requires" compile error) is in phase 1 by dependency whatever the list says: `all((h: S))` over a label whose group
holds a backreference (§4.2 (a)'s `/(?<h>(?<a>a+)b\k<a>)?x/`) can now be refused where rev 19's `all` (= the plain
condition) was not. The restated slot sentence dropped the rev 18 sentence's qualifier "those constructs are in phase
1 with them" (l.899-903), which named what the slot's occupant drags in; rev 20 has no counterpart.
Severity: doc (scope), with one design consequence (`all` inherits the mark's refusals). Effort: one bullet listing
the joint condition's pieces as IN/OUT (owner's call where unruled) and the `all` dependency. Blast radius: §0.2, §1,
§4.3, the phase-1 cost statement.

### FIXIND-9 — §4.2 STATUS still lists rev 8's O28 lean as SUPERSEDED, after dropping the quote that showed it IS the rev 20 rule
CONFIRMED (restatement diff). Rev 19 §4.2 STATUS (rev 19 l.1624-1625): "SUPERSEDES rev 9's statement by the label's own
quantifier ..., and rev 8's O28 lean \"zero iterations = unset = fail\"." Rev 20 §4.2 STATUS (l.1995-1998):
"SUPERSEDES rev 10-19's PER-MATCH BOUNDARY ..., rev 9's statement by the label's own quantifier, rev 8's O28 lean, and
CF:173's \"unset fails\" (now the whole rule, for every cause)". The restatement DROPPED the quoted content of rev 8's
lean and kept it on the superseded list; that content ("zero iterations = unset = fail") is ruled point (2) itself.
Rev 20 says the opposite elsewhere: §2.6 l.1355 "Rev 8's lean (a plain condition FAILS on zero hits), withdrawn in rev
9, is the rule again". (CF:173's "unset fails" on the same list is likewise not superseded but generalised; the
parenthesis says so, rev 8's item has no such parenthesis.)
Severity: doc (a status line contradicting the rule it stands under). Effort: trivial (move rev 8's lean to "the
rule again", as §2.6 does). Blast radius: §4.2 STATUS; §13 O28's history pointer.

### FIXIND-10 — "an alternative lacking the label is DROPPED" (kept unchanged) is a second absence mechanism; with the mark it answers differently from the same pattern written as rx, against the principle (*)
CONFIRMED. Rev 20 l.1896-1897: "`[x = /\d/, y = /[a-z]/] & (x: /[0-5]/)` = `[0-5]` (the alternative lacking x drops, §2.3)
is unchanged"; §2.6 STATUS l.1142 "An alternative of x lacking the label is DROPPED (with the `label.unset` warning)";
L6 l.614. Ruled point (1) lists "an alternative not taken" as ONE cause of absence, and the mark makes absence
acceptable. The array `[x = /\d/, y = /[a-z]/]` and the rx `/(?<x>\d)|(?<y>[a-z])/` match the same subjects and set
their labels the same way. With `(x?: /[0-5]/)` over the 36 subjects 0-9, a-z (fixind_drill.py (D6), ENGINE-RUN 36
cases, 0 differ; DOM(x) by running): read as the rx's absent label (a letter: x absent, marked, DOM has 0-5) it HOLDS
on 32; with the y entry DROPPED as l.1897 says, on 6. Unmarked both give 6, which is why the drop was harmless until
the mark existed. Under the principle (*) the drop must become "x is absent there" (unmarked the same answer, marked
the rule's). Also unsaid: whether `each((& (a?: d)), x)` is still L6's ERROR on an entry lacking a, and whether the
never-absent-mark warning reads the dropped entries.
Severity: design (a pre-rule mechanism kept beside the rule: the sibling of FIXIND-7's "which pattern"). Effort: one
sentence at l.1897/l.1142 and L6. Blast radius: §2.3/§2.6 application rule, §4.2, L6, every array of labelled
alternatives under a marked condition.

### FIXIND-11 — STANDING Q (sibling): the never-absent-mark warning is the third member of an "inert written control" family, not a pair with `default.unused` (a)
SUSPECTED (a design proposal; confirms if the family's members share one test). §4.2 (f) l.1969-1974 proposes merging the
never-absent mark with `default.unused` (a) because "both say D is never read". The same test, "removing what the
author wrote cannot change any answer", already backs `default.unused` (b) (the default outside every set), `dead.branch`
(an alternative that can never match), `warn.unused` (an `@warn.off` that suppresses nothing) and `anchor.whole` (an
anchor that always holds at the edge). They are one family: a WRITTEN CONTROL WITH AN EMPTY EFFECT. Unified, the
family answers FIXIND-4 once: `anchor.whole` already has a RULED policy for controls a macro body writes ("no
exemption", CF:1154), and the family must say whether that policy holds for the marks `all` inserts (it would fire on
every `all` over a required label) or whether expansion-inserted controls are exempt across the family. `label.unset`
is the family's dual (a control NOT written whose absence WILL change an answer), and the third-fix gap of FIXIND-5 (a)
is the dual's "is the absence handled?" test, which the family's one test (does any alternative read the absent label
uncontrolled?) answers. Unlocks: one effect test in the compiler instead of five; one naming scheme (the spelling
step's). Trigger: the next proposed member (`label.both_sides`, §7.1 l.2737-2740, is already in the queue) or the
build of any one of them. Severity: maintenance/design. Effort: a paragraph in §7.1.

### FIXIND-12 — STANDING Q (general form): the mark, the default, `all` and future item 3 are one operation, "give a label a candidate set", and the general form leaves open WHO shares a candidate choice
SUSPECTED (proposal; FIXIND-3 and FIXIND-6 are its confirmed symptoms). Rev 20's general form (l.1863-1868) assigns D per
absent label PER CONDITION: {} / {v} / DOM(h); `predicates_future.md` item 3 adds D = S. `all(c)` (l.2033) is "D = DOM for
every label of c without a default"; the per-label mark on a PASSED condition has no spelling (§4.2 (e3), OPEN).
GENERAL FORM: one condition transform, "c with candidate sets", `c` over `{label: D}` (spelling the spelling step's),
of which `h?` is `{h: DOM}`, `h = v` is `{h: {v}}`, `all(c)` is `{every undefaulted label: DOM}`, item 3 is `{m: S}`.
And one decision the per-condition form hides: the SCOPE OF ONE CHOICE. Per condition (today): `(h?: A) & (h?: B)` !=
`(h?: A & B)` (FIXIND-3), and the entry `a?` and a value-side `$a` may pick different values (FIXIND-6, 2 vs 10 of
110). Per label per pass across the `&` chain: both equalities return and (e2)'s mark question has one answer, at the
cost that two conditions on one optional label are no longer independent filters (the chain becomes one existential).
UNLOCKS: (e3)'s per-label mark through a macro (the OPEN item) with no field reference; FIXIND-4 disappears (`all` adds
no written mark); item 3 at no new mechanism; L92's two spellings equal again. TRIGGER: the first acceptance case that
passes a library condition and needs ONE of its labels optional (e3), or that `&`s two library conditions over one
optional label. Severity: design. Effort: a paragraph in §4.2 plus the scope choice (an owner question if the chain
reading is wanted).

## PROBED-AND-HELD


- EVIDENCE RE-RUN: `predspec20_check.py` re-run in place, rc 0, stdout IDENTICAL to the committed `.out`; PART A 12 of 12
  SAME. My drill `fixind/fixind_drill.py` (absimpact's engine prefix exec'd verbatim): 312 ENGINE-RUN cases, 0 differ,
  46,520 whole-match probes, 0 PCRE2/Python disagreements; (D5) is COMPUTED (subjects whole-matched in both engines).
- §4.2's time table (5 subjects x 5 columns) and the list table (5 x 5) = joint_condition.md (TM2)/(TM2-L): held.
- The marked form `occurs.none(((h, m?): !(<10, <30)))` reproduces "the empty list passes, an item without minutes fails"
  on 1,111 lists (wider than the draft's 259), 0 differ, for R as written (FIXIND-2 is about R' and the spelling).
- Unmarked: `(h: A) & (h: B)` = `(h: A & B)` on the two FIXIND-3 populations (both need a text): held (0 differ).
- `when` (l.2832-2838): restated with both directions (zero passes; set-once optional where the mark moves the answer):
  held against §4.2's negation paragraph.
- L30, L56, L65, L93, L94, L95 restatements vs §4.2 (AR) and the negation paragraph: held (6 rows).
- (c) the default inside `all` vs the not-both error "decided from the text" (l.1859-1861): no contradiction (`all` is
  defined to skip defaulted labels).
- (a) the approximation table (6 rows): `aaba` is outside a^n b a^n and inside `a+ba+`; the five agreeing rows likewise:
  held by inspection.
- Negation/composition over an OPTIONAL, a REPEATED and a NEVER-REACHED label: unmarked `!(x: S)` HOLDS and `(x: !S)` FAILS
  on all three (one kind of absence), as L30 and O28 now say; `|` with an alternative not naming the label holds on
  absence (L90's third meaning), as stated; the only unstated turn-overs found are FIXIND-3 (`&` of marked), FIXIND-5 (b)
  (the mark inside `some`), FIXIND-6 (`$a`) and FIXIND-10 (an array alternative).
- Record = `&` for DISTINCT labels with marks, per pass (row 68): not re-run; consistent with the general form (each
  label's choice independent): held by reasoning.
- The 2026-11-16 newest three manager's readings: optional-as-loop's "how" is used consistently in §4.3 l.2072-2079 and
  L94; spelling-phrasing carries its asterisk at l.1883 and §0 (checked l.1881-1884).

CRITIC COMPLETE
