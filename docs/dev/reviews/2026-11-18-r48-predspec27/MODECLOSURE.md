# MODECLOSURE findings — critic round predspec27 (rev 27 of predicates_draft.md)

(Pre-created by the coordinator. This is YOUR OUTPUT file: append findings as you go.)

## Findings

### MODECLOSURE-1 — R.1.15 (8)'s narrowed control states where label and capture agree without saying which mode; inside an `occurrences` argument the "agree" class parts
CONFIRMED. Severity: design/doc. If it is not fixed, a reader takes "no optional, one depth agree" into a find-all
place and gets the wrong verdict. Effort: small (one sentence plus two counted rows). Blast radius: R.1.15 (8),
R.1.0's `occurrences` ARGUMENT row (REFERENCE cell), §R.8 **hit-carry-depth** (the same mechanism seen from the other
side). Location: draft line 2083-2093, R.1.15 (8) "THE CONTROL, NARROWED"; the record entry "2026-11-18 OWNER, discussing
value-hole" (the manager's answer "the draft's control ... must be narrowed").
The draft says: they part "where the label is UNSET at the hole while the capture is set: an optional group in a loop
... a group two loops deep ...; no optional and one depth 0 / 0 / 0 ... VH0 (no optional, one depth) stands as the
control where they agree". Every pool there is a TOP-LEVEL program. The FIND-ALL column in those counts is PCRE2's
global loop, where every match starts with no captures set. In an `occurrences`/`contains` argument the place table
makes the argument a REWRITE into a loop (each hit is a pass). Under hit-carry, `\k` carries the capture across hits
(L62, line 4435). So a hit adds one pass, and the argument adds one loop depth:
- (i) A LITERAL WITH NO LOOP, with an optional group: `occurrences(/(?<y>\d)?-\k<y>;/, min = 2)` against the same
  literal with `${$y}` in place of `\k<y>`. Result: WHOLE `3-3;-3;`: `\k` HOLDS, label FAILS. SEARCHED: `\k` gives
  `3-3;-3;`@0, the label gives no match. FIND-ALL: `\k` gives [`3-3;-3;`@0], the label gives []. The two part on
  2 / 2 / 2 of 21,845 texts (`37-;`, length <= 7). The same literal at the TOP LEVEL parts on 0 / 0 / 0 of 5,461.
- (ii) "NO OPTIONAL, ONE DEPTH", the draft's agree class: `occurrences(/(?:(?<y>\d);)*=\k<y>/, min = 2)`. Result:
  WHOLE `3;=3=3`: `\k` HOLDS (hit 2 `=3` reads hit 1's capture), label FAILS (hit 2 enters the inner loop, which
  resets y). The two part on 1 / 1 / 1 of 1,093 texts (`3;=`, length <= 6). At the top level: 0 / 0 / 0 of 1,365.
- With `min = 1` both cases are 0 / 0 / 0, because the trailing lazy gap absorbs the second hit. A witness needs
  `min >= 2`.
- In all four, the model "the label where it is set, else the capture" equals `\k<y>` 0 / 0 / 0. The draft's
  direction ("label unset, capture set") holds. The CLASS it names does not.
Fix: state the control per place. In an `occurrences`/`contains` argument, count the hit as a pass and the argument
as one loop depth, so "no optional, one depth" means written depth 0 there. Add one counted row per place.
Repro: `modeclosure/p3.py` and `modeclosure/p4.py`. Model: an empty marker group before each branching that contains
y. The label counts only if y's start is at or after every marker. This is predspec261's marker model generalised.
The lazy-gap template is predspec261's own: `(?:[\s\S]*?(?:R)){k,}[\s\S]*`.
MIN WITNESS: text length 7 for (i) and 6 for (ii). Pattern size: one group, one backreference, plus the template.

### MODECLOSURE-2 — R.1.15 (7) "no answer moves" holds only in WHOLE once a finite label has more than one width
CONFIRMED. Severity: answer. A sentence of the draft says no answer moves, and with the copies in the values' order
SEARCHED and FIND-ALL answers do move. Effort: small (state the order the copies must follow). Blast radius: R.1.15
(7), R.1.12 (pricing a compile-time spelling), T8, and **lift-order** (§R.8 line 2771). Location: line 2078-2082,
R.1.15 (7): "For a FINITE label (`\d{4}`) the same program has a compile-time spelling (an alternation of 10,000
copies, regular, priced by its size, R.1.12); that is a choice of the compiler, no answer moves." This is the owner's
two-forms claim (read-is-constant (3), "look the same") in its run-time-versus-compile-time shape.
- With a fixed width (`\d{4}`), every start has at most one candidate, so any order of the copies gives the same
  answer. The sentence is true for its example.
- With a variable width, `/(?<y>\d{1,2})${$y + 1}/`, two copies can match at the same start.
- The run-time form (a callout model, y read, `v == y + 1`) against a compile-time alternation of one copy per y text
  (`00`..`99`, `0`..`9`):
  - in the VALUES' ORDER (array-lift's order, the order **lift-order** recommends for `\d + 1`): 0 / 53 / 56 of 1,365
    texts (`0123`, length <= 5), first SEARCHED `012`. SEARCHED `1213`: the run-time form gives `1213`@0, the
    values-order spelling gives `12`@0 (the y = 1 copy comes before the y = 12 copy).
  - in PATH ORDER (the label's own backtracking order: the longest y first): 0 / 0 / 0.
- So the compile-time spelling keeps the answers only if its copies follow the label's PATH order. That order is not
  the values' order T8 gives the compile-time form of `+`.
Fix: in (7), "no answer moves PROVIDED the copies follow the label's path order (for a greedy label, the longest
first)". Name the clash with lift-order's recommendation in that question's row: the order that keeps run time and
compile time "the same" is the path order. Repro: `modeclosure/p4.py` part (B).
MIN WITNESS: text length 3 (`012`). Pattern: one group `\d{1,2}` and one value hole.

### MODECLOSURE-3 — R.1.15 (5)'s find-all-place example holds only under the unset reading the draft rejects; under the draft's own reading the form matches nothing in any mode
CONFIRMED. Severity: doc/design. The verdicts shown are not the draft's own. A reader also cannot see that, under the
draft's reading, a value hole written before its group in a hit-list argument matches nothing. Effort: small. Blast
radius: R.1.15 (5), §R.8 **unset-in-hole** (line 2766; its EMPTY cell already notes "rev 26's VH6 needed it").
Location: line 2072-2075, R.1.15 (5), against (3) at 2063-2067 ("THE DRAFT'S READING: FAIL").
- The draft says: (5) `occurrences(/${$y + 1}-(?<y>\d{4})/, min = 2)` "(the unset value read as EMPTY for this run
  only) WHOLE `-2025 2026-2030` HOLDS, `-2025 2027-2030` FAILS".
- Under (3)'s FAIL the first hit's hole always reads an unset label. Hit-carry gives no previous hit to read, so the
  hole fails and no first hit exists, in any mode.
- Run with libpcre2, the template as in MODECLOSURE-1:
  - unset as FAIL: both of (5)'s texts FAIL.
  - unset as EMPTY: HOLDS and FAILS, as the draft shows.
  - Over 5,461 texts (`12- `, length <= 6), `occurrences(/${$y + 1}-(?<y>\d)/, min = 1)`: WHOLE holds on 0 texts
    under FAIL (SEARCHED 0) and on 2,758 under EMPTY. With `min = 2`: 0 against 26.
- So "hit-carry applies ... BEFORE it, the PREVIOUS HIT's" never takes effect in a value hole under the draft's
  reading. This is the plain-PCRE behaviour (`\k` before its group fails in the first hit).
Fix: in (5), show the FAIL answers as the draft's ("both FAIL; under FAIL a hole before its group in a hit-list
argument matches no text"). Keep the EMPTY run as the unset-in-hole candidate's answer. Add "hit-carry in a value hole
is reachable only under EMPTY (or a default)" to the unset-in-hole row's consequence cell.
Repro: `modeclosure/p5.py` part (C).
MIN WITNESS: the pool reaches length 6. The EMPTY side holds from length 2 (`-1`). The FAIL side holds on 0 of
5,461 texts, in WHOLE and in SEARCHED.

### MODECLOSURE-4 — R.1.15 (8) leaves out the two-groups-of-one-name literal, where the label and the capture are both set and still differ
CONFIRMED. Severity: doc. Effort: trivial (a scope clause). Blast radius: R.1.15 (8), **same-name-twice**.
Location: line 2085-2093, R.1.15 (8): "they part where the label is UNSET at the hole while the capture is set" and
"the model 'the label where it is set, else the capture' equals `\k<y>`". The sentence carries no one-name condition.
- `(?J)(?:(?'x'a)|(?'x'b))+-\k<x>`: PCRE's `\k` reads the FIRST SET group. The label is the last pass's own
  (entering the alternation resets x).
- WHOLE `ab-a`: `\k` HOLDS, label FAILS. `ab-b`: the reverse. Here x is SET for the label and the capture is set, and
  they differ.
- The two part on 8 / 16 / 16 of 364 texts (`ab-`, length <= 5).
- So "label where set, else capture" is not `\k<x>` here. The language allows the literal ("a deliberate difference
  from PCRE"), and which value `\k` reads is the open **same-name-twice**.
Fix: "(for one group of the name; two groups of one name are **same-name-twice**)". Repro: `modeclosure/p6.py`.
MIN WITNESS: text length 4. Pattern: two groups of one name and one backreference.

### MODECLOSURE-5 — T1's run-time cell, "the read's string, then the others", can be read as the read always first
CONFIRMED (the reading). Severity: doc. Effort: trivial. Location: line 2168, T1: "the read's string, then the
others, in order: `$y | "x"`".
- For `"33" | $y` the order decides SEARCHED and FIND-ALL. `/(?<y>\d)-${"33" | $y}/` SEARCHED `3-33`: in written
  order (compile-time PCRE `(?:33|\k<y>)`) it gives `3-33`@0. With the read first it gives `3-3`@0.
- The two forms are "the same" (read-is-constant (3)) only if the run-time form keeps the WRITTEN order.
- UT4's control (0 / 0 / 0) runs only the read-first spelling, so it cannot tell the two readings apart.
Fix: "the operands' strings in written order (the read's one string where the read stands)". Add a run of the
reversed spelling. Repro: `modeclosure/p5.py` part (D). MIN WITNESS: text length 4.

## PROBED-AND-HELD

Controls: libpcre2-8 10.46 through `rxmodel_evidence/pcre2h.py`, run only. Python `re` was used for the empty-pass
check. Scripts are in `modeclosure/p1.py`-`p6.py`. MINIMUM WITNESS LENGTH reached by the pools: text length 7
(21,845-text pools, `37-;`), 6 (1,093 / 5,461), 5 (364 / 1,365). Pattern size: one or two groups, one reference,
plus at most one lazy-gap template.
- The evidence forward run reproduces 21 of 21 OK (`modeclosure/fwd.out`). The draft's counts in R.1.15 (8) all
  reproduce: 2 / 2 / 2 of 21,845; 1 / 1 / 1 of 5,461; 0 / 0 / 0 of 5,461.
- CAPTURE-STATE DRILL (a):
  - (1) An optional group in a looped place, read inside the loop: parts as stated.
  - (2) A group two loops deep, read from outside the loops: parts as stated.
  - (3) An ATOMIC optional in a loop, `(?:(?>(?<y>\d)?)-\k<y>;)*`: 2 / 2 / 2 of 21,845, first `3-3;-3;`. This is the
    same as the plain optional; the atomic place adds nothing. The label-else-capture model gives 0 / 0 / 0.
  - (4) A NULLABLE loop body read from outside, `(?:(?<y>\d)?)*=\k<y>` and `(?:(?<y>\d)?)+=\k<y>`: 0 / 0 / 0 of 63
    each. PCRE and python `re` both keep a final EMPTY iteration (the marker at (1,1) on `3`), which by the TOLD
    empty-pass rule unsets the label. But the hole's own test backtracks to the path without the empty pass, so the
    label and the capture match the same span. HELD: no answer parts at the top level.
  - (5) A literal against the hole spelling of an inserted part (m2), `/(?:${X}-\k<h>;)*/`: equal to the plain
    literal (evidence BL m2, 0 / 0 / 0 of 21,845, reproduced in the forward run).
  - (6) An inserted part exporting the name, `A SEQ B` (m1): reproduced in the forward run (6 / 66 / 66 against
    `(?J)`; capture and label 0 / 0 / 0).
  - (7) A top-level FIND-ALL of a loop-free optional literal, `(?<y>\d)?-\k<y>;`: 0 / 0 / 0 of 5,461. Each match is
    fresh, so the draft's FIND-ALL column is right for the PROGRAM place. The parting appears only in an
    `occurrences` argument (MODECLOSURE-1).
  - (8) In every probe of this lens, the model "the label where it is set, else the capture" equals `\k<y>` on all
    nine programs (21,845 / 5,461 / 1,093 / 63 texts). The one exception is two groups of one name
    (MODECLOSURE-4).
- A `records` ITEM as a find-all place: R.1.0 makes it "condition-free, DFA-able". Neither `\k` nor `${$y}` can stand
  in one, so the backreference and the read cannot part there. HELD (by the draft's text; no run needed).
- MODE MATRIX (b), T-rows on a read:
  - T1 `$y | "x"`, T2 `$y & <5`, T10 `$y . "E"`: the evidence's UT4 runs reproduce, 0 / 0 / 0 of 3,906 each, against
    the plain PCRE spelling, every mode.
  - In the parting region (an optional in a loop), `${$y | "x"}` against `(?:\k<y>|x)` parts 2 / 2 / 2 of 21,845,
    first `3-3;-3;`. This is exactly (8)'s parting carried through T1. So the run-time and compile-time forms are
    "the same" exactly where (8) says label and capture agree. HELD, with MODECLOSURE-1's place caveat.
  - T8 `\d + 1`: WHOLE equals 1..10 (evidence). SEARCHED depends on order, which is **lift-order**, asked; see
    MODECLOSURE-2 for the run-time twin.
  - T13 a read in a count: UNDER CONSTRUCTION; there are no answers to compare. T14 a read as a name: COMPILE ERROR,
    which is mode-free. T7 / T19 are unchanged.
  - The case at the hole (VD1b, 0 / 0 / 0 of 3,906 for each of the 4 placements) is reproduced in the forward run.
    It is place-independent, since options are lexical.

CRITIC COMPLETE

