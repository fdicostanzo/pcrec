# Lane tupleval report: the tuple as a value, the full account (design only)

Deliverable: `docs/design/joint_condition.md` §4A (new section after §4; earlier sentences it corrects are marked
"[§4A.10]" in place and listed in §4A.10). Evidence: `docs/dev/lanes/tupleval_check.py` / `tupleval_check.out`. No
edit to `predicates_draft.md`, `plan.md`, `src/`, `cli/`, `lib/`, `memfn/` or `tests/`. Spellings are placeholders
(D193 add. 4). Citations: `predicates_draft.md` rev 19 by line; `CF:n` = `docs/design/plan_row_bodies/COND-FAMILY.md`.

## STATE AT HANDOFF

STATE: complete. Branch lane/tupleval, cut from main 993ff6873. Rulings file `tupleval_rulings.md`: ONE entry, R-1
(the owner's 09:47 clarification: "In my mind (x, y) is different than (x,y): because the colon ..."), read before
the first commit and before this report; APPLIED (the colon is the stated discriminator in §4A.1, §4A.4 and the
census §4A.7; the manager's three readings of it are tested in §4A.8). Last entry applied: R-1. Evidence run:
`timeout 120 python3 -I docs/dev/lanes/tupleval_check.py` (from the worktree root) -> `TOTAL cases 47357 differ 0
engine-disagreements 0` (libpcre2-8 10.46, Python 3.14.4). OWED RUNS: none. UNTESTED, labelled in the note: the
`$`-bound pair `> ($sh, $sm)` (as in §5 problem 5), the version-policy ARRAY as one set, closure of the class under
`!`.

## THE DEFINITION

§4A.4, one paragraph. In brief: a TUPLE SET of arity k >= 2 is a set of k-tuples of strings, the value of a
tuple-valued expression; arity is static, every other value is arity 1. Producers: the tuple bracket `( e1, ..., ek
)` in value position (no colon after it; the PRODUCT of arity-1 entries), `|`/`&` of one arity, arrays of one arity,
comparison sets with a tuple atom (dictionary order, each component by its literal, each a one-string set), macros
and bindings of these, and filter modifiers under **modifier-lift**. Equality is string equality per component
(table (E): the literal `(9, 0)` admits 0 of 11,000 `t` subjects, `padded(== (9, 0))` admits 2). Accepted: right of
`:` against k references, call arguments, right of `:=`, array entries, `&`/`|` operands, comparison atoms. Errors:
arity mismatch; a tuple where an arity-1 set is required (hole, final pattern, `P & t`, single-reference condition,
`join`, index brackets, arithmetic); nesting; `()`, `(e,)`; labelled entries (L43); component reads by `[n]`/`.`; a
`$`-tuple over repeated labels (table (Q): 5 of 11 subjects differ from per-iteration pairing). LANE'S
CONSEQUENCE: with constant entries the class is the finite unions of products of regular sets, so every joint
condition on a constant tuple set is a finite `|` of single-label condition records, default level.

## RELATION TO CONDITIONS AND THE RECORD

§4A.1. The owner's colon (R-1) separates a TUPLE OF REFERENCES (`(h, m):`, the left of a condition entry) from a
TUPLE OF VALUES (`(9, 0)`); a condition entry `h: S` is the one-reference case. The brackets keep their ruled
meanings (CF:863): in value position `[ ]` (any one) is the union and `( )` (all together) is the product, so no
bracket gains a meaning. The record ruling (his words CF:851-852; the recorded rule CF:866) is UNTOUCHED: a record is
defined by what it is laid against; a value tuple is laid against nothing and has no names. What moves are three
LEAN sentences of the draft that inferred an error from it: L45 (`predicates_draft.md:543`, `f((1, 2))`), the §5.4
`( e1, e2, ... )` row (`:2013`) and the condition row's "any other record in value position" (`:2014`). L43
(labelled entries in value position) stays an error. The one-way rule (CF:853-854) extends in its own direction: the
joint condition views a regex as a record and tests it against a tuple set; a tuple set is never read as a regex.
A tuple set has the ARRAY interface over its entries and NO map interface.

## THE ONE-ENTRY CASE

§4A.2. `x`, `(x)`, `((x))` are one thing; `((h): S)` is `(h: S)`; `((9, 0))` is `(9, 0)`; `[9, 0]` is the arity-1
set "9 or 0"; `()`, `(9,)` and nested entries `((9, 0), 1)` are errors (LANE'S lean; flattening is the recorded
alternative, trigger: a library set only writable by composition). No separate one-tuple: a set of 1-tuples and a
set of strings carry the same information. Holds under either **set-arity** answer.

## REACHING THE PARTS

§4A.3, six options weighed. LANE'S LEAN: a tuple VALUE is used whole; its parts are reached by NAMING them left of
the colon (the match's parts as `$h`, `$m`). Index `t[i]` REJECTED (`[n]` reads entries, §3.2 tool 1); map interface
`t.1` REJECTED (`.name` never digits; named components = the record as value); a projection built-in REJECTED.
Destructuring `(a, b) := t` is the one collision-free route but is NOT PROPOSED: no example needs a component of a
tuple value (rev 19's `lo[1]` was the only use, inside the replaced `lex_` bodies), and on a non-product set it is a
projection whose round trip silently widens the set (table (D): `month_days` 365 pairs -> 372, 7 extra subjects
`02-29` .. `11-31`; `[(9, 0), (17, 30)]` -> 4 pairs). If a case appears: products only. Question **tuple-parts**.

## GENERAL USE

§4A.5 table. Of the twelve §12 cases: E-CAL SIMPLER (a declared table, (C4) of §2), E-IPV4 NEW GROUND (ranges and
CIDR block lists; table (R): 6 blocks, 5 not on an octet boundary, 2,422 cases vs `ipaddress`); 10 the SAME; none
worse. Beyond §12: library sets over unnamed fields (`office_hours`, `valid_ymd`, version-policy arrays), group
questions over pairs, `> ($sh, $sm)` (UNTESTED). A multi-field allowlist is a real use with no §12 case. A match
viewed as a tuple is `($h, $m)` already (set-once labels): no new form. Results as tuples, file-loaded combination
lists: NOT PROPOSED (no example; triggers named).

## WHAT IT CANNOT DO

§4A.6 table: the final pattern, an rx hole, `&` with a pattern, `join`, a single-reference condition, mixed arity,
component reads, `$`-tuples over repeated labels, arithmetic and index brackets, labelled value tuples, and a
reference tuple used without its colon (the bare-reference ruling, CF:1268-1282). Each error names its fix.

## THE MANAGER'S FIRST ANSWERS, TESTED

§4A.8. (m1) HOLDS, INCOMPLETE (static arity, arity-1 entries, one-string comparison components, `$` pairs only on
set-once labels, string equality). (m2) HOLDS, INCOMPLETE (three draft LEAN sentences move; "is" is the open
record-is-product, only the answers are equal). (m3) HOLDS (plus `()`, `(e,)`, nesting errors). (m4) PARTLY WRONG:
the index rejection and projection loss hold, but destructuring is not THE way; parts are named left of the colon,
destructuring held for products only. (m5) HOLDS, INCOMPLETE (allowlist has no §12 case; `($sh, $sm)` untested and
refused over repeated labels; CIDR lists and version arrays missed). (m6) HOLDS, INCOMPLETE (more error positions;
`t & u` of one arity is legal). R-1 readings: (i) INCOMPLETE (computed labels are bindings by spelling and stand left
of the colon, §4.4); (ii) HOLDS under §13 C13's lean; (iii) HOLDS with the arity-1 exception list.

## CONSEQUENCES DERIVED BY THE LANE

Each is the lane's, not a ruling.
1. The tuple bracket in value position is the ruled `( )` "all together" applied to values: the product; `[ ]` stays
   the union. No mark gains a second meaning in a position it had; two `( )` positions are new (§4A.7).
2. L45 flips from an error to "one argument, a pair"; G4 holds because positional arguments are exactly the
   required parameters, so `f(1, 2)` and `f((1, 2))` are never both legal for one macro.
3. A tuple set has the array interface (entries) and no map interface; `[n]` never reads components.
4. No one-tuple, no empty tuple, no nested tuple (errors, D77).
5. Parts of a tuple value: no compile-time access; parts are named left of the colon.
6. `($h, $m)` over repeated labels is an error at every level (unpaired product, table (Q)).
7. Comparison atoms of a tuple: each component a one-string set.
8. A CIDR block of ANY prefix length is one dictionary range over the octets (table (R)).
9. `>= (9, 30)` and `(>= 9, >= 30)` are both legal and differ on 2,700 of 11,000 subjects (table (O)): the one
   census pair that is neither the same answer nor an error.
10. Constant tuple sets are finite unions of products of regular sets: default level.

## QUESTIONS FOR THE OWNER

Ranked. Each: reply either way.

1. **tuple-parts**: may a tuple VALUE's parts stay unreachable at compile time, the parts being reached by naming
   them left of the colon (`t & ((h, m): office_hours)`, then `$h`)? Example: with `lo := (9, 0)`, `lo[1]` is an
   error ("`[n]` reads entries"), and `(lo_h, lo_m) := lo` is not proposed. Forces: no example needs a part of a
   tuple value, and every access form either collides (`[n]` already reads an array's entries; `.` names fields) or,
   on a set that is not a product, silently widens it (`month_days` splits into 12 months x 31 days and admits
   `04-31`); against: a future macro that wants one bound's component. Leaning: YES, no access; destructuring kept in
   the design for products only, waiting for a case.
2. **colon-scope**: is the scope of a name fixed by the colon, as your 09:47 words say, with one refinement: left of
   the colon a name is looked up among the operand's LABELS, COMPUTED labels included (`isodate & (weekday: 6)`,
   where `weekday` is written as a binding); right of the colon (and in any value tuple) a bare name is a BINDING,
   and a label's value is read with `$`? Example: `span & ((eh, em): padded(> ($sh, $sm)))`: `eh, em` are labels,
   `$sh, $sm` their values. Forces: one rule per side, no shadowing (your "it wouldn't be clear where it was coming
   from"); the draft's bare `<=dim` in E-CAL is the one place it would change (open item C13, which already leans
   `<=$dim`). Leaning: YES.
3. **two-orders**: keep both `>= (9, 30)` (dictionary order: 10:00 is after 9:30) and `(>= 9, >= 30)` (each part on
   its own: 10:00 is OUT because 00 < 30) as legal spellings with different answers? Example: on 11,000 times they
   disagree on 2,700. Forces: both are natural (the second is just a tuple of comparison sets, and forbidding it
   would also forbid `(padded(1 | 3), padded(between(1, 31)))` in the calendar table); against: your look-alike rule
   asks that a look-alike be the same answer or an error. Leaning: KEEP both; the operator outside the bracket
   compares the whole tuple, inside it compares one part; a library may add a warning if confusion shows.
