# predspec19: predicates_draft.md rev 18 -> rev 19, the other-side sigil (lane predspec19, opus, 2026-11-16)

Design only, no build go. Branch `lane/predspec19`, cut from main dfb9d5659. Inputs: the draft at rev 18,
COND-FAMILY.md to its end (CF:1284-1316, the 23:46 pointer, the 23:56 sigil idea, the 00:06 sigil ruling),
`predspec18_report.md`, review r17. Two owner answers reached the lane through its rulings file during the work
(R-1 00:08 **macro-arguments**, R-2 00:09 **looped-compare**). Both are applied.

## STATE AT HANDOFF

- STATE: done. Commits on `lane/predspec19`: the evidence script and output (one WIP commit). Rev 19 of
  `docs/design/predicates_draft.md` in three WIP commits: the field reference in §§0-5; the §8 rewrite; §13, the
  changelog and §15. Then this report, the history index line and the output re-run.
- Rulings file `docs/dev/lanes/predspec19_rulings.md`: the last entry applied is **R-2** ("looped-compare: warn",
  folded as RULED, with the warning `compare.looped` and worked rows). **R-1** ("macro-arguments": NO, the owner's
  test) is applied too. I re-read the file before each commit and before this report. It has no entry after R-2.
- Premise test passed. The draft showed rev 18, and COND-FAMILY.md ended with the 2026-11-16 sigil ruling.
  `timeout 300 python3 -I docs/dev/lanes/predspec18_check.py`, run from `$PCREC_TMPDIR/scratch/predspec19`,
  reproduced `predspec18_check.out` byte for byte, rc 0.
- Validation (docs only):
  - `make test-spec-history test-doc-lint`: GREEN (make exit 0, no `*** [test-` line). `plan.md` is unchanged, so
    `test-plan-lint` was not needed.
  - Evidence: `timeout 300 python3 -I docs/dev/lanes/predspec19_check.py`, run from the scratch dir before 00:40
    box clock (1.3 s, light). It wrote `predspec19_check.out`, rc 0. libpcre2-8 10.46 and Python 3.14 `re`,
    0 engine disagreements.
  - Comparison with rev 18's output: once rev 18's `(x:)` spellings are mapped to `^x`, every rev 18 table line has
    the same counts. Only titles and column alignment changed. New lines: table (B), table (X) and seven worked
    rows.
- STOP RULE: one point. The census of the sigil does not pass under the rules as written: `[n]` on the left of `:`
  is an ITERATION index by §3.2's position rule, and the bodies need an ENTRY pick. Under R-1's instruction this
  goes to the owner inside **reference-index**; it is not added quietly. The draft states the lean resolution and
  marks it OPEN (O75). The rule change itself collides with no ruled text (checked: CF:595-597 rules the concept,
  CF:275 is the manager's path proposal). No evidence population differs.
- Owed: none.

## WHAT CHANGED

Section names are the draft's (rev 19). Tables are those of `docs/dev/lanes/predspec19_check.out`.

- **§5.4 new `^` row** (THE FIELD REFERENCE, defined once). It covers:
  - positions: a call's argument, or an entry of a spelled array that is one;
  - errors elsewhere, each with its fix;
  - meaning: neither a value nor a condition;
  - binding: fixed where written; kept when passed; refused against another operand;
  - unset, repeated and computed labels;
  - one meaning per occurrence.

  The `:` row also notes the parameter route, and the STATUS line records the mark's provenance.
- **§4.1 THE ONE EXCEPTION** to "the left of `:` is a path, never an expression". STATUS states why no ruled text
  collides with it.
- **§3.2 tool 1**: a sentence on arrays of field references, marked OPEN (O75); indexing arrays of MACROS stays out
  (R-1).
- **§3.5**: an array of field references is a reference, "h or m" (the owner's general path).
  `(s: S)` = `(h: S) | (m: S)`.
- **§8 TUPLE COMPARISONS**:
  - The bodies are rewritten as `[(s[1]: padded(>lo[1])), (s[1]: padded(==lo[1]), s[2]: padded(>=lo[2]))]`, each
    entry ONE condition record (the record holds its tests together, §4.1). The 3-field form and the any-n `lg`
    sketch are rewritten the same way.
  - The projection text is rewritten. WHAT THE BODIES USE lists 4 items. THE OWNER'S TEST APPLIED.
  - Every worked row and caveat is re-spelled `[^h, ^m]`.
  - THE RULE CHECK is redone over references. Rev 18's readings (a)/(b) are marked NOT ADOPTED.
  - EVIDENCE gains rev 19's numbers. Caveat (6)(i): with references the slip is visible at the call. Caveat (6)(ii):
    RULED warn, plus worked rows.
  - NAMING and THE PROJECTION (iii)/(iv) are rewritten. The section `(h:)` is recorded as not adopted, with his
    reason and his open door. The recommendation is replaced.
  - New subsection THE FIELD REFERENCE: binding written vs passed, no `&` in sight, unset/repeated/computed,
    shadowing, THE CENSUS table.
  - STATUS rewritten.
- **§7.1**: new warning name `compare.looped`.
- **§0**:
  - status line and the CF range line updated; R-1/R-2 citation convention added;
  - new rulings table "entries after rev 18" (5 rows);
  - the rev 16/17 rows' trailing cells corrected (readings, section);
  - §0.2's rev 18 paragraph rewritten;
  - §0.3: `section` row (not adopted) and a new `field reference` row.
- **§0.1**:
  - L72-L75 re-spelled. L73's error is now §4.1's. L74 is re-read through §3.5. L75 notes that the duplicate is
    visible at the call (`compare.repeated` proposed, row stays GAP).
  - New rows L76 (`^h`/`$h`/`h:`, BY DESIGN), L77 (the section and `^.h`, ERROR), L78 (`(^h: S)` written directly,
    ERROR), L79 (nested `&`, BY DESIGN), L80 (passed to another operand, ERROR), L81 (a bound call, OPEN).
- **§12 census**: tuple row re-marked; new `^` row; positional `X[...]` row notes O75.
- **§13**: O71 RESOLVED (ruled). O73 ANSWERED NO (the owner's words). O74 CLOSED (ruled warn). O75
  **reference-index** and O76 **bound-reference** are NEW. DECIDED (61)-(66). Owner questions (13)-(15) are
  answered, and (16), (17) are new.
- **Changelog** rev 19; **§15** provenance row; **§2.7** `compare.width` pointer re-spelled.
- **Evidence** `docs/dev/lanes/predspec19_check.py` is a copy of predspec18's (the original is unedited):
  - The bodies are re-expressed: a `Ref` is a pair (the operand it was resolved against, the label), and the body's
    `(s[k]: S)` raises `RefError` when the reference's operand differs from the body's.
  - Every call also runs rev 18's label-name body verbatim. Table (X), rev 19's form against rev 18's:
    48,797 calls, 0 differ.
  - Table (B), the binding rule: 4,188 cases, 0 differ.
    - B1 nested `&`: 48 cases, 0 differ. The outer-operand reading would differ in 22 of the 48, so the
      population tells the two readings apart.
    - B2 passed to the same operand: 828 cases, 0 differ.
    - B3 written in a library body: 1,656 cases, 0 differ.
    - B4 a bound call against the direct call: 1,656 cases, 0 differ.
    - B5 passed and laid against another operand: 828 of 828 refused.
  - Worked rows: 60, 0 differ (53 from rev 18 plus 7 looped).
  - Every rev 18 table (D, D', R, U, Z, L, N, S, C) keeps its counts. That includes the expected-differ rows that
    measure the defects (rev 17's strict forms: 230; the width reading: 30 and the rest).

STALE SITES, grepped and corrected (`(h:)`, `^.`, `h_is`, `macro-arguments`, `label-section`, `looped-compare`,
`readings (a)`):

| site | what was there | fix |
|---|---|---|
| §2.7 `compare.width` paragraph | rev 17 example with `(h:)` and the accessors `h_is`, `m_is` | re-spelled `[^h, ^m]`, citing the ruling |
| §0 rulings table, tuple-compare row, last cell | "plain macros only under readings (a) and (b) ... **macro-arguments**" | the readings belonged to rev 17-18; rev 19 needs neither (R-1), only §4.1's exception and O75 |
| §0 rulings table, decomposition row, last cell | "the two readings they need ... the label section `(h:)` (OPEN, O71)" | not adopted; sigil RULED |
| §0.2 rev 18 paragraph | a passed macro CALLED in the body, **macro-arguments** | the sigil and the §4.1 exception; called macros gone |
| §0.3 `section` row | `(h:)` OPEN | considered and not adopted |
| §0.1 L72-L75 | `[(h:), (m:)]` spellings; L74 "reading (a)"; L75 "would need the library to see label names" | re-spelled; L74 re-read through §3.5 and O75; L75 updated |
| §8 the body block, projection text, accessor block `h_is`/`m_is`, every worked row, RULE CHECK, TWO READINGS, caveats (2), (4), (6), any-n `lg`, NAMING (`[^.major, ...]` "the other candidate"), THE PROJECTION (i) tail, (iii) "`h_is` ... `(h:)`", (iv) both candidates, RECOMMENDATION "the SECTION", STATUS "OPEN (**label-section**)" | rev 18 text | rewritten (WHAT CHANGED) |
| §12 census rows (tuple compares; positional `X[...]`) | "the section `(h:)` or the other-side mark `^.h` ... OPEN (O71)" | ruled; new `^` row |
| §13 O71 | two candidates, lean the section | RESOLVED |
| §13 O73 | OPEN, lean yes | ANSWERED NO, the owner's words |
| §13 O74 | OPEN, lean warn | CLOSED, RULED warn |
| §13 owner questions (13), (14), (15) | open | ANSWERED, each keeping "the question as asked" |

Left as written on purpose: the rev 17 and rev 18 changelog entries and their §0 rulings tables (history); DECIDED
(51) and (60) (rev 17-18 decisions, superseded by the new O71/O73 text); the `^.`/`^...` hits in §0.1 L7, L69, §11
and E-CTX (PCRE anchors inside rx text, unrelated).

## THE FIELD REFERENCE

The reference has one meaning per occurrence. The census in §8 shows this for every `^` the draft writes, apart
from the row brought to the owner (see the stop rule above).

- **What it is.** `^h` (also `^d.year`, `^mnum`) is a compile-time NAME OF ONE FIELD OF ONE OPERAND. It is neither
  a value (that is `$h`) nor a condition (that is `h:`). Each label then has three spellings with one role each:
  `h:` constrains, `$h` reads, `^h` refers.
- **Where it may appear.** Only as a call's argument (`is_late(^h)`) or as an entry of a spelled `[ ]` that is an
  argument (`lex_ge2([^h, ^m], [9, 0])`). Everywhere else it is an error with a fix:
  - `P & ^h`;
  - `(^h: S)` written directly (fix: write `(h: S)`);
  - a bound `[^a1, ^a2]` (fix: write `$a1`);
  - `${^h}`;
  - `r := ^h`;
  - an array that mixes references with rx or macros.

  Inside `/.../`, `^` is PCRE's anchor; the symbol is the spelling step's to choose.
- **Binding.** The reference is resolved WHERE IT IS WRITTEN, to the field that a condition `(h: S)` written in place
  of the call would read (§4.1's chain lookup at that place):
  - At an `&` operand, that is the other side of THAT `&`.
  - At a nested `&` inside a condition's set, it is the inner one.
  - Written in a library body, it is the body's own `&`.
  - PASSED into a body, it keeps its operand. A body that lays it against another operand is a compile error that
    names both.
  - A call bound by name is resolved where the bound macro's operand is filled. That is OPEN, **bound-reference**.

  This states the manager's lean ("the `&` of the place it is written") precisely. The two agree everywhere except
  the bound call.
- **No `&` in sight.** A call that never meets an operand is the unapplied-macro error (§2.3). A reference outside
  the two positions is the `^` row's error.
- **Labels.**
  - An unset label is legal: its conditions fail per match, and only when the compare reaches the field.
  - A repeated label follows the sequence rule, and `compare.looped` warns (RULED).
  - A computed label (`^mnum`) is found by the same lookup as `(mnum: S)`, because a computed label IS a label of the
    pattern whose labels it reads (§4.4).
  - Shadowing: bare `mnum` names the binding, `^mnum` the field, `$mnum` the value.
- **The rule change** (the manager's consequence, checked). In a macro body, a parameter bound to a field reference,
  or a LITERAL-index entry of one (`s[1]`), may stand on the left of `:`. The path was written at the call and is
  only passed along, and it must name a field of the operand the condition is laid against.

  STILL FORBIDDEN:
  - a label built from a string or any value (`("h": S)`, a name from `$x`, a hole);
  - arithmetic or a computed index (`s[n - 1]`, until O69 (3)'s trigger);
  - extending a passed reference (`(s[1].year: S)`);
  - a parameter bound to anything but a reference;
  - a reference written directly on the left of `:`.

  It collides with no ruled text. CF:595-597 rules the concept "one condition form `label: set`". The PATH is the
  manager's proposal (CF:275). The record itself left "a PARAMETER AS A LABEL NAME" open to check (CF:1239-1240).
- **Indexing an array of field references.** The existing array rules do not cover it. §3.2 tool 1 says the result
  is "always an rx", and the owner's general path (R-1) gives the array's MEANING ("h or m"), not its entries.
  §3.2 tool 1 gains one OPEN sentence, which is owner question **reference-index**.
- **Look-alikes.** §0.1 L72-L81: `^h` vs `$h` vs `h:` (BY DESIGN); bare `h` (ERROR, ruled out); the section `(h:)`
  and the superseded `^.h` (ERROR); `(^h: S)` (ERROR); nested `&` (BY DESIGN); passed to another operand (ERROR);
  a bound call (OPEN).

## CONSEQUENCES DERIVED BY THE LANE

Each of these is the lane's, not the owner's and not the manager's.

1. **The manager's consequence (2) is wrong as worded.** It said: "the bodies no longer need [macros as arguments];
   the current rules (an index gives an rx ...) stand." The first half holds: nothing is called. The second half
   does not: the bodies INDEX AN ARRAY OF REFERENCES (`s[1]`), and that is not "an index gives an rx". So the
   bodies still need one thing beyond the ruled-in change, and it is now owner question **reference-index** (O75).
   The owner's own answer (R-1) also overtakes the withdrawal: **macro-arguments** is recorded as ANSWERED NO, with
   his words, not as withdrawn.
2. **The manager's consequence (1)** (a field-reference parameter on the left of `:`) is right and collides with no
   ruled text. It needs stated LIMITS, listed above as STILL FORBIDDEN; DECIDED (63) records them.
3. **The manager's consequence (3)** (the accessors leave the examples) is done. No example needed them.
4. **Binding rule.** I state the manager's lean as "the field a condition written in place of the call would read".
   That gives the other side of the written `&` in every directly written case. It also keeps §0.1 L2 (a binding is
   its expansion) for a bound call, where a strictly visible `&` would refuse. The difference goes to the owner
   (**bound-reference**).
5. **An array of field references is a field reference ("h or m")**, by the owner's general path (R-1). So
   `(s: S)` with `s` bound to `[^h, ^m]` means `(h: S) | (m: S)`, the same answer as L74's filter-role array. No
   body uses that reading.
6. **The census's one failing occurrence.** `[k]` on the left of `:` after a reference parameter must be the entry
   pick, but §3.2's position rule reads `[n]` there as an iteration. The lean resolution uses an existing rule: a
   passed reference cannot be extended, so an iteration index is written at the call (`^h[2]`). It goes to the owner
   inside **reference-index**.
7. **The repeated-field slip (L75) is now detectable at the call**, because the two references are visible there
   (`compare.repeated` proposed). It is not adopted (D77), so the row stays GAP.
8. **Writing `(^h: S)` directly is an error**, so `:` keeps one spelling. The ruling makes the reference a way to
   NAME a compared field. It does not make it a second way to write a condition.
9. **The looped warning is named `compare.looped`.** It fires on a reference to a REPEATED label (§4.2's boundary).

## QUESTIONS FOR THE OWNER

1. **reference-index**: may a library body pick the k-th field out of `[^h, ^m]` by position?

   Example: `lex_ge2(s, lo) := [(s[1]: padded(>lo[1])), (s[1]: padded(==lo[1]), s[2]: padded(>=lo[2]))]`, called
   as `/(?<h>\d{1,2}):(?<m>\d\d)/ & lex_ge2([^h, ^m], [9, 0])`.

   Forces:
   - By your general path, `[^h, ^m]` is "h or m". A compare needs "h, then m", so without positional access the six
     names have no body.
   - Picking an entry is the index the language already has for `[/a/, /b/][1]`, and nothing is called. That is
     what separates it from the macro mechanism you refused.
   - It does need one stated exception. On the left of `:`, `[n]` normally means "iteration n" (`(x[2]: S)`).
     After a passed reference it would mean "entry n". That is safe only because a passed reference cannot be
     extended, so "iteration 2 of h" is written at the call as `^h[2]`.

   Leaning: yes, with that exception stated. Reply either way.

2. **bound-reference**: may a compare call that holds references be bound by name and applied later?

   Example: `late := lex_ge2([^h, ^m], [9, 30])`, then `/(?<h>\d{1,2}):(?<m>\d\d)/ & late`.

   Forces:
   - Applying it later works the way a bound condition `c := (h: >9)` already does, and keeps "a binding is its
     expansion" (tested: 1,656 cases, 0 differ from the direct call).
   - Refusing it means the `&` the field comes from is always in sight where the reference is written. That is your
     "it wouldn't be clear where it was coming from", at the price of that binding rule.

   Leaning: allow it; the binding's name is then where a reader looks. Reply either way.
