# Lane predspec3 report: predicates_draft.md rev 3

Lane predspec3 (opus), documentation only (NO BUILD GO). Branch `lane/predspec3`. Deliverable:
`docs/design/predicates_draft.md` rev 3. Inputs: the rev 2 draft; review `docs/dev/reviews/2026-11-14-r1-predspec.md`
and its critic files (q1r, q1x, own, rul, verify); the COND-FAMILY.md owner rulings from "Q1 critic framing" to
the end. PREMISE TEST held: COND-FAMILY.md ends with the "transforms are FILTER MODIFIERS" ruling note.

## RULINGS FOLDED

All from `docs/design/plan_row_bodies/COND-FAMILY.md`, 2026-11-14:

1. **Q1 critic framing (look-alike criterion).** Folded as goal G0, ranked first, with the checkable LOOK-ALIKE
   TABLE §0.1 (38 rows L1-L38).
2. **C22 condition binding.** In a condition literal the comma separates conditions; `label:` takes the expression up
   to the next comma or `)`; `&`/`|` tighter than `:`, `:` tighter than `,`. §4.1 rewritten (SUPERSEDES "`name:`
   takes one operand term"); `(major: 1 & minor: >=4)` is a compile error; semver comma form in §8. Consequence I
   stated: at top level `P & x: S` is an error ("write `P & (x: S)`"), since its left would not be a label path.
3. **C22 addendum (labelled arguments = condition literal).** `isodate(year: S, month: 2)` = `isodate & (year: S,
   month: 2)`; `=` sets a parameter; a labelled argument always narrows (answers RUL-10). §4.1, §5.2, §5.4.
4. **Q1 RULED (string sets + edge-assertion error).** §11 rewritten: set positions listed, edge assertion defined
   (reads outside the value; static), error text, interior assertions keep PCRE meaning, values / transform images /
   compile-time sets context-free, D193 add. 3 stands (§2.6), nullability in context (§7), named in-context form only
   on measured need (§11, §14). Context-marked sets removed (no both-versions). The "if A kept" items (Q1X-4 A1
   rule, the `label.context` warning, A's context-stripping rules) are moot and dropped.
5. **OWN-1 RULED (transforms are FILTER MODIFIERS).** §2.7 rewritten: filter -> filter (the pullback), nesting in
   reading order, the naming rule, the docs rule (the transform transforms the FILTER; text says so). `&` pure
   intersection again (§2.2); right-associative `&` and pipeline text removed everywhere. Renames: `unpad` ->
   `padded`, `ci` -> `any_case`, `unquoted` -> `quoted`, `length` (now `length(S)`), month-name table ->
   `month_numbered`, `pad(n)` -> `unpadded(n, S)` (my name), `jstr` -> `json.quoted` (my name). Every example
   rewritten. `transform.noop` dropped (no trigger left).

Rulings file `docs/dev/lanes/predspec3_rulings.md` was empty at every check (start, before each commit, before
this report).

## REVIEW DISPOSITIONS APPLIED

FIX-NOW items (by id; where a FIX-NOW depended on Model A it is noted as moot):

- **OWN-13**: G0 + LOOK-ALIKE TABLE §0.1, seeded from Q1R/Q1X/OWN/RUL pairs, incl. L21 `!<200` vs `>=200`
  (DIFFERENT, documented). GAP rows marked; open item O38.
- **Q1X-9**: §12.12 E-CTX-1..6 with ruled answers (all compile errors, each with its fix and the answer it gives);
  **Q1R-4** added as E-CTX-7 (repeated label); one agreeing interior-assertion case.
- **Q1R-10 / Q1X-7**: E-FILE text fixed (blank line, not trailing newline, gives the empty entry; CRLF untiled range
  `foo\r\n`); E-FILE marked not yet a valid acceptance case until O20; O20 carries the consequence.
- **OWN-10**: §5.5 class members in codepoint order; E-SEP `.index` fixed (`.` = 2, `/` = 3).
- **RUL-1**: D193 add. 3 folded (§2.6, §11; it stands under the Q1 ruling).
- **RUL-5**: `$x !~ rx` = `(x: !contains(rx))` (§2.6); its edge-assertion consequence is new contradiction C32.
- **RUL-6**: §5.2 empty-intersection error scoped to narrowing sites, never inside an `@assert` argument; §5.6.
- **RUL-9**: §3.2 numeric filters / integer sets range over 1..n; only literal `[0]` is the whole rx.
- **RUL-14**: marks 1 (warning names MANAGER LEAN, §4.2, §7.1), 2 (no number type: ruled for counts, global form
  LEAN, §2.1), 4 (layer outline LEAN as amended, §1), 5 (`~` operator LEAN, §2.6) fixed; 6 stated as the reading
  taken (§2.4); 3 NOTED (unchanged).
- **RUL-15**: C16's `x & <256 | >300` example withdrawn; `precedence.section` recorded as PLAN (§7.1, L22).
- **RUL-4**: §13 row; dissolved by OWN-1 (pure `&`), recorded in "RESOLVED in rev 3".
- **RUL-8**: new §13 row C29.
- **OWN-2**: §2.2 false sentence replaced, lint-hint equivalence dropped; the OWNER half is O26.
- **OWN-5**: §2.3 `each` out of the equivalence list; lacking label = drop + `label.unset` (§2.3, §4.2, L6).
- **OWN-7** (FIX-NOW half): string enum values (`gaps = "allow"`, `order = "desc"`), closed built-in list (§5.1);
  OWNER half (metadata spelling, level selection) is O31.
- **OWN-14**: G3 restated (one-literal program = today's pattern; check escapes `/` and transfers flags); strict
  subset only inside larger programs (§11).
- **OWN-15** (DOC): goals text notes G1's check shares its source, G2 checked at build, G1/G2 resolved toward G2 at
  default; the ranking question is part of O38.
- **Q1R-1 / Q1X-2**: the three candidates (A, B1, B2) and where they separate, in §11 REASONING (the 25-row table is
  cited, not copied).
- **Q1R-6**: `$x` context-free; `$x ~ rx` value as whole subject (§2.6, §4.1, §11).
- **Q1R-7 / Q1X-6c**: transform images context-free; a modified filter's argument is a set position (§2.7, §11).
- **Q1R-8 / Q1X-5 / Q1X-6a/b**: no-subject uses are set positions (enumerate, assert, name sets, computed values,
  records entries), §5.5, §5.6, §7, §11.
- **Q1R-9**: nullability in context; only the MODE exempts (§7, L18/L19).
- **Q1R-12 / Q1X-1**: §11 REASONING restated on the real argument.
- **Q1X-8**: §7 prerequisites: the static edge-assertion check added; D196 add. 2's regular-lookaround lowering stated
  NOT a prerequisite under the ruled model (§6.1, §7).
- **OWN-8** (PLAN + DOC): look-alike row L24; `array.hole` recorded as proposed.
- Moot (Model A not kept): Q1X-4 (rule A1), Q1R-7's "OWNER if A kept", the `label.context` warning fallback.
- Not applied (PLAN / NOTED by the review): RUL-F1..F6 (one families note in §13), Q1R-13, OWN-12, the general
  form + unlocks list.

## CHANGED SECTIONS

Changelog (rev 3 entry); §0 (status marks incl. REVIEW FIX, goals with G0, G3 restated, NEW §0.1 table, standing
questions); §1 (names, mark); §2.1; §2.2 (pure `&`, `!<200`); §2.3 (`each`, modifiers); §2.4 (`padded`, mark);
§2.5; §2.6 (D193 add. 3, `!~`); §2.7 (REWRITTEN, filter modifiers); §3.1-3.5 (filters over 1..n, modifiers);
§4.1 (REWRITTEN binding, condition literals, labelled arguments); §4.2-4.6 (marks, spellings, pointers); §5.1
(closed built-ins, string enums); §5.2 (labelled args narrow, RUL-6 scope); §5.3-5.4; §5.5 (codepoint order, set
position); §5.6 (set position); §6.1; §7 (records in context / entries context-free, tiling wording, in-context
nullability, prerequisites); §7.1 (names, `transform.noop` gone); §8 (modifier list, `occurs` argument, semver);
§9 (pointer); §11 (REWRITTEN: string sets + edge-assertion error, G3, reasoning); §12 (all examples renamed,
E-IPV4/E-FILE/E-HTTP/E-SEP texts, NEW §12.12 E-CTX-1..7); §13 (resolved lists, C1/C16/C17/C21/C25/C28 updated,
new C29-C32, new O26-O38, families note); §14 (two rows); §15 (rev 3 rows).

## REMAINING OPEN

New open items for the owner (§13, each with the review's lean, unresolved): O26 label-free `!f` (OWN-2), O27
quoting vs comparison reading (OWN-3), O28 one rule for label shapes (OWN-4), O29 each `some` its own witness
(OWN-6), O30 brackets/commas/tuples (OWN-9; the comma-record part already ruled by C22), O31 metadata members and
level selection (OWN-7, RUL-12), O32 `flag.hole` (Q1R-11), O33 two conditions on an ambiguous pattern (RUL-3), O34
same-text-twice levels (RUL-7), O35 duplicate labels (RUL-16), O36 search assertion (Q1X-5, noted), O37 my two
modifier names (`unpadded`, `json.quoted`), O38 GAP rows of the look-alike table + OWN-15's ranking question.
Still open from before: C13 (OWN-11's `$wd` lean recorded there), C28, and the rest of §13.

Contradictions between rulings found and LISTED, not resolved (STOP RULE):
- **C1**: OWN-1's "`&` order- and grouping-free" vs D196 (RULED) "the left operand chooses the reported span"; C17's
  left-major structure has the same tension.
- **C30**: C22 addendum "the positional argument is the subject" vs OWN-1 (a modifier's positional argument is the
  filter) and constructors (`between(lo, hi)`).
- **C31**: the counting ruling's `occurs.exactly(1, name: ...)` vs the C22 addendum's "a labelled argument always
  narrows the subject". §12.9 uses the positional condition literal, valid under both.
- **C32**: RUL-5's `!~` = `x: !contains(rx)` vs D193 add. 3 + Q1 for an rx with an edge assertion (`$x ~ /^err/`
  legal, `(x: contains(/^err/))` refused).

## STATE AT HANDOFF

STATE: done. Commits on `lane/predspec3`: rev 3 WIP + text fixes + this report. Rulings file empty; last entry
applied: none (no entries). Validation: documentation only; the pre-commit staged checks passed (52/52) on each
commit; `scripts/lanecheck --deliver docs/dev/lanes/predspec3_deliver.txt predspec3` run before handback. owed: none.
