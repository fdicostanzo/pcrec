# CRITIC census: crit-jointcond

## Findings

### CENSUS-1 — §4A.7's `( )` census was never updated for the default (N5): two of its rows claim the same bracket
CONFIRMED (quote+cite). Severity: doc (rev 20's §5.4 rows are written from it, §9 row 21). Effort: small (amend three
rows). Blast radius: §9 rows 20-22, rev 20 §5.4 `( label: S, ... )`, `( p1, ..., pk ) :` and the L43 error row.
`joint_condition.md:763-769` decides a `( )` by "what is INSIDE it (`:` entries, `=` entries ...)":
row 764 `( label: S, ... )` value position = CONDITION, "told apart by `:` entries inside"; row 769 `( x = e, ... )`
value position = ERROR (L43), "told apart by `=` entries"; row 768 tuple "no `:`/`=` inside"; row 763 reference tuple
lists no `=` entries at all. §4B.1 (`:1040-1041`) then makes `(m = v: S)` and the record `(h: S, m = v: T)` LEGAL
conditions in value position (`t2 & (m = 0: <30)`, `:1020`; `(h = 9: <5, k: 3..7)`, `:1404`): each has an entry
with BOTH an `=` and a `:`, so by 4A.7's own discriminators it is BOTH row 764 (condition) and row 769 (error).
Likewise `((h, m = 0): R)`'s inner bracket carries an `=` entry that row 763 does not admit. My script
(census/census.py, `paren.tsv`) finds 22 `( )` occurrences of the record-with-default shape and 35 reference tuples
with a default, none covered by 4A.7's discriminator text. The rule that resolves it exists elsewhere (§4B.1: `= v`
only on a name LEFT of `:`; L43 = an `=` entry WITHOUT a `:`), so the fix is wording: row 764 "entries `p: S` or
`p = v: S`"; row 769 "an `=` entry with no `:`"; row 763 "a path, or a path `= v`". Also 4A.7's closing claim "no
existing row changes meaning" (`:787`) should say rows 764/769 change their discriminator. Note: rev 19's ENTRY
EXTENT (`predicates_draft.md` §5.4, "`&` and `|` bind tighter than `:` and `=`") never had an entry holding both
`=` and `:`; §4B.1 states the order only by example (`m = 0 | 5: S`), worth one sentence in rev 20's §5.4.

### CENSUS-2 — a bare name bound to a `$` tuple has two readings: a tuple binding (§4A.4 producer 5) or a computed label (§4.4)
CONFIRMED (quote+cite; no engine needed: the question is which rule applies). Severity: design (accept vs compile
error on a program the note's producers admit). Effort: one sentence + one error row. Blast radius: §4A.4 producers
(1)/(5), §4C's C13 consequence, §9 rows 17, 21, 24; rev 20 §4.4.
Program: `span := /(?<sh>\d{1,2}):(?<sm>\d\d)-(?<eh>\d{1,2}):(?<em>\d\d)/`, `start := ($sh, $sm)`,
`span & ((eh, em): padded(> start))`.
Reading A (accept, = §5 problem 5): §4A.4 producer (1) admits `($sh, $sm)` ("a `$` entry of a set-once label gives
one string per match", `:674`) and producer (5) "a binding of any of these (a binding names whatever its expression
is, §2.1)" (`:682-683`); a bare name on the value side is a binding (J2, `:97-98`). Reading B (compile error): §4.4
"a binding that reads match labels IS a computed label of the pattern whose labels it reads"
(`predicates_draft.md:1724-1725`); §4C (`:1315`) and §7 item 11 (`:1547`): "a bare `dim` there is a binding, i.e.
the computed label's macro, which no comparison atom takes: an ERROR naming `$dim`". Under B the fix `> $start`
then needs `$` to yield a PAIR, but the `$` row is "one string per match" (`:1055`, §5.4 `$` row) and J3 says "only
an arity-1 set has text". And LEFT of the colon (J2: "computed labels included", `:96`) `(start: >= (9, 0))` is a
one-reference left (arity 1) naming a label whose value is a pair: neither the arity rule nor §4A.6's
"single-reference condition" row (which is about a pair-valued SET, `(h: (9, 0))`) says which. The note's own uses
avoid the question by writing `($sh, $sm)` inline (`:506`, `:1459`) or passing it as an argument (`gt(($sh, $sm))`,
4A.11). Expected: one sentence — e.g. "a computed label is arity 1; a match-dependent tuple is written inline or
passed, never bound" (an error naming the inline form), or "a binding of a `$` tuple is a tuple binding, not a
computed label". Either is cheap; today the note determines neither.

### CENSUS-3 — a record holding a joint entry BESIDE other entries is admitted by J1 but defined by nothing
CONFIRMED (quote+cite). Severity: design (legal/error and, on a shared label, error-vs-accept undetermined). Effort:
one sentence. Blast radius: J1, J9, §4D (D2, D3, D26), §8 **label-twice**, §9 rows 13-14, 21.
J1 (`:89-92`): the joint entry "stands where a condition entry stands, inside a record". A record has several entries
(rev 19 §4.1), so `isodate & (year: leap, (month, day): month_days)` and `P & ((h, m): R, (a, b): Q)` are written
the way J1 says. Their meaning is not determined: (i) J9 (`:141`) and §4D (`:1325-1326`) DEFINE only records of
single-reference entries, `(p1: S1, ..., pk: Sk)` = `((p1, ..., pk): (S1, ..., Sk))`; applied to the mixed record it
gives `((year, month, day): (leap, month_days))`, whose entry `month_days` is arity 2 inside a tuple bracket — a
"nested tuple entry", an ERROR by §4A.2/§4A.4 (`:575`, `:698`). (ii) D2/D3's "all of several conditions = one record"
(`predicates_draft.md:1546`) would read it as `(year: leap) & ((month, day): month_days)`, legal. (iii) Flattening
(the triple `leap x month_days`) is the third reading; the note leans AGAINST flattening only for VALUE tuples
(§4A.2 NESTING). The readings give the same accept set on set-once labels, but split on a SHARED label:
`(h: <12, (h, m): R)` is, by (iii) + item 1, `((h, h, m): ...)` = the label-twice ERROR; by (ii) `(h: <12) &
((h, m): R)`, legal. No code span in the note writes a mixed record (census: 0 of 169 joint-entry records have a
second entry; my scan `paren.tsv`), and §1's calendar line uses `|` of two records instead, so the gap is silent.
Expected: one sentence in J1/J9 — mixed records legal and = the `&` of their entries (with label-twice across
entries stated), or an error naming that `&`.

### CENSUS-4 — unlisted look-alike: a union of tuples vs a tuple of unions (`[(9, 0), (10, 30)]` vs `([9, 10], [0, 30])`), both legal, different
CONFIRMED (repro). Severity: doc (G4 bookkeeping; possibly design if the owner wants a diagnostic). Effort: one row
in item 8, 4A.7 and §9 row 6. Blast radius: §9 row 6, rev 20 §0.1.
The note gives the operator-inside/outside pair (J5) a BY DESIGN row and says in 4A.7 (`:783`) it is "the one pair
in this census that is neither the same answer nor an error". The SAME inside/outside distinction for `|` and
`[ ]` is nowhere listed: `[(9, 0), (10, 30)]` / `(9, 0) | (10, 30)` (two pairs, §4A.4 producers (2),(3)) vs
`([9, 10], [0, 30])` / `(9 | 10, 0 | 30)` (the product of two alternations, four pairs, producer (1)). Every
spelling is legal (arity 2 everywhere). It is exactly the owner's own 09:58 example ("9:30, 10:00 broken apart is
9,10 and 30, 00 which is gibberish", `:480-481`), which the note uses against taking parts apart (§4A.3) but never
as a WRITTEN look-alike. Repro: `census/transpose.py` (`timeout 300 python3 -I`), `t` population 11,000 subjects,
`t & ((h, m): padded([(9, 0), (10, 30)]))` vs `t & ((h, m): (padded(9 | 10), padded(0 | 30)))` (J8 lift), expectation
from Python integer pairs, both forms also run as rx: union admits 3, product 6, differ on 3 (`9:30`, `09:30`,
`10:00`); 0 expectation/regex disagreements. Not the same answer, not an error, no warning proposed. Plausibly
"sufficiently different" by the owner's 11:20 test (bracket order is visible), but under G4 (`:43`) it must be
LISTED either way; item 8 (`:417-427`), 4A.7 (`:775-783`) and §9 row 6 (`:1650`) all omit it, and 4A.7's "the one
pair" sentence is then false.

### CENSUS-5 — §9 row 6 drops the note's own LEGAL-DIFFERENT look-alikes from §4B.4 (and their proposed warning)
CONFIRMED (cross-table count). Severity: doc (rev 20 is written FROM §9; what row 6 omits leaves the draft's §0.1).
Effort: two rows in §9 row 6, one in row 27. Blast radius: §9 rows 6 and 27, rev 20 §0.1 and §7.1.
I took the union of the note's look-alike tables — item 8 (9 rows, `:417-427`), 4A.7 (7, `:775-783`), §4B.4 (10,
`:1150-1161`) — 22 distinct pairs after merging duplicates; §9 row 6 (`:1650`) carries 8. Of the 14 omitted, 12 are
compile ERRORS, design-only (`(a, b) := t`), already-warned (`label.unset`, `:1160`) or existing/inherited stories (O28's `!` pair, C9 padding, `(9, 0)` vs `padded(== (9, 0))`,
`f(1, 2)` vs `f((1, 2))` — never both legal by §5.2's "positional = required parameters", `predicates_draft.md:1950`,
held — and §4B.4's error rows); those can reasonably stay out. The two that cannot are NEW-by-this-note, LEGAL and
DIFFERENT: (1) `t2 & [m = 0]` vs `t2 & (m = 0: S)`-style defaults (`:1156`: "LEGAL, DIFFERENT ... 244 of 11,110",
the `=` before a label NAMES a new label in `[ ]` but READS a label with a fallback left of `:`), with the lane's
proposed WARNING `label.twice`; §9 row 27's warning list (`:1671`) has `compare.looped`-moved and `default.unused`
but not `label.twice`, so the proposal vanishes from rev 20 without a ruling; (2) the unguarded hand slice
`t2 & ((h, m): R) | ...(h: 10 | 11)` vs the default (`:1159`, "LEGAL, DIFFERENT on 99 of 11,110 ... none possible"),
the pair the note calls "the strongest case FOR the default" (`:1113`). Row 6 carries the `| (h: 10)` alternative
(DIFFERENT, on purpose) but not these two. Plus CENSUS-4's pair. Expected: row 6 gains (1) and (2); row 27 gains
`label.twice` marked "the lane's proposal, not ruled" (or the note says why it is dropped).

### CENSUS-6 — the `( )` row count rev 20 must print has three different bases in the note; recomputed
CONFIRMED (count). Severity: doc. Effort: one sentence in §9 row 21. Blast radius: §9 row 21, rev 20 §5.4 `:1998`.
Rev 19 §5.4 (`predicates_draft.md:1998`, "`( )` has four rows"): I count 4 `( )` rows in its table —
`( e1, e2, ... )` (call / condition / left of `:=` folded), `( label: S, ... )`, `(& f)`, `( e )`: the claim holds.
The note: item 8 (`:424`) "from four `( )` rows to six (N1, N3)" — on §5.4's basis 4 + 2 = 6, correct. 4A.7
(`:785`) "nine value-or-statement rows ... the addition is TWO rows": its table has TEN `( )` rows (`:761-770`:
eight meanings + two ERROR rows); nine excludes the reference-tuple row, which is one of the "TWO" added — so on
4A.7's own basis rev 19 is 8 (four + head + left of `:=` + the two ERROR sentences unfolded), not "four plus the head
and the left of `:=`" = 6. §4A.10 (`:826-827`) concedes the basis question but §9 row 21 still says only "updated
(§4A.7)". Recomputed under N5 (CENSUS-1): no NEW row (the default rides rows 763/764), so 6 on §5.4's basis, 10 on
4A.7's. Expected: §9 row 21 names the number and the basis ("six: the four plus the reference tuple and the value
tuple; heads, the left of `:=` and the error shapes stay folded").

## PROBED-AND-HELD

Method: `census/census.py` (`timeout 300 python3 -I census/census.py subject/joint_condition.md census`) extracts
1,475 code spans (1,387 backtick, 88 indented-block lines), strips `/.../` regex text, and classifies every `(` by
what precedes it, what follows the matching close (`:` / `:=`) and what is inside (`:`/`=` entries, comma, leading
`&`): 1,115 `(` occurrences — tuple set 253, call 174, joint-entry record 169, reference tuple 145, condition 127,
comparison tuple atom 72, reference tuple with default 35, destructuring left of `:=` 24, grouping 24, record with a
default entry 22, empty/`()` 16, `:`-mixed 15, head 13, `(e,)` 10, L43 labelled value 7, one-reference grouping 6,
section 1, unbalanced (span cut by prose) 2. Every non-standard class (57 occurrences: mixed, empty, unbalanced,
L43, `(e,)`, section, one-ref grouping) inspected by hand: each is regex text, prose, or an example the note itself
labels ERROR. Other marks over the same spans: `,` 862, `:` 612, `:=` 93, lone `=` 142, `$` 124, comparison
immediately before `(` 72, `[` 72, `padded(` 56. `census/eq.py`: ~70 distinct `=` contexts.

HELD (each determined by J1-J9 / §4A.4 / §4B.1, one meaning per position):
- `=`: every one of the ~70 contexts is one of §4B.3's positions (array label, call parameter, head default, label
  default, L43 error) or prose/env vars; `(m = 0 | 5: S)` extent fixed by §4B.1; `$m = 0`, `((h, m): R = 0)`,
  `((h, f(m = 0)): R)` all errors as stated.
- Comparison before a tuple atom (72): all dictionary-order atoms; `>= [9, 0]` the arity error; `>= (x)` grouping;
  `between` via parameter atoms "unchanged" (J4) — held, though producer (4) spells only the bracket form.
- Bare names on each side of the colon (145 + 35 reference tuples): J2 + the refinement determine every one (left:
  label incl. computed; default: binding; both-binding-and-label -> binding; label-only default -> error). Exception
  filed: CENSUS-2 (a binding of a `$` tuple).
- `$` (124): label value, `${` hole, or a stated error; never on the left of `:`.
- `padded(...)` (56): around a set (lift, J8) or a part of a product; B3's non-numeric case stated.
- `|`/`&` between tuple sets: arity rule; tuple-set `|` condition is rev 19's rx|macro error.
- `[ ]` of tuples: union; `[9, 0]` vs `(9, 0)` arity error.
- Look-alikes checked and holding: `f(1, 2)` vs `f((1, 2))` (never both legal, §5.2 :1950 "positional = required
  parameters"); `((h, m))` vs `((h, m): R)`; `(9, 0)` vs `[9, 0]`; `(h, m = 0): R` vs `(h, m: 0): R`; `>= (9, 30)` vs
  `(>= 9, >= 30)` (ruled BY DESIGN); `between((1, 9), (5, 16))` vs `(between(1, 5), between(9, 16))` (J5's family,
  item 4 covers it); head `m(p, q = 0) :=` vs reference `(p, q = 0):` (told by name + `:=` vs `:`).
- Rev 19 §5.4 rows after the additions: `,` row unchanged; `:` row (a path or a tuple of references) one meaning;
  `=` row gains one position, one meaning per position (the `[m = 0]` reader trap is CENSUS-5); comparison row
  "ONE atom" extends cleanly; `( e1, e2, ... )` row + the new value-tuple row are told apart by position — one
  meaning per position HOLDS except the discriminator wording in CENSUS-1.
- Count recomputations: rev 19 "four `( )` rows" = 4 (holds); item 8 "four to six" holds on §5.4's basis; 4A.7
  "nine"/"TWO" reconciled only on a different basis (CENSUS-6); item 8 "three positions are new (N1, N3, N5)"
  holds (the tuple atom, the lift and `$` in a tuple are extensions of existing positions, counted as §2.4's one
  sentence and J8).
- Repro run: `census/transpose.py`, 11,000 subjects, 0 expectation/regex disagreements.

CRITIC COMPLETE
