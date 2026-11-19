# Lane preddoc2 — the predicate documents moved, macros to the library, the lint for the post-pilot format

Lane preddoc2 (opus), 2026-11-19. Branch `lane/preddoc2`, cut from `lane/pred-rev28`. Documents, their lint and
its tests only; nothing under src/ cli/ lib/ memfn/ tests/. DESIGN ONLY; rules nothing.

## STATE AT HANDOFF

STATE: done. Commits, one per part: `adc141b00` (PART 1, lint and reader, and the move of the six files),
`931ce6ad8` (PART 2, pointers and CLAUDE.md files), `aa23f1f49` (PART 3, principle statuses, zero-values split),
`53c0a4a85` (PART 4, macros to the library), then this report's commit. Rulings file
`docs/dev/lanes/preddoc2_rulings.md`: re-read before each commit and before this report: **empty** (no R-n applied).
OWED: none.

Premise test (before any edit): `python3 -I scripts/pred_doc_lint.py` printed "checks passed 1828, failed 0";
both .test files passed. Held.

Acceptance, after each part (the lint on the real documents; both .test files; `make -s test-plan-lint`):

| after | lint checks passed / failed | .test files | plan-lint | `?` core / lib | skeleton core / lib |
|---|---|---|---|---|---|
| pilot (before) | 1828 / 0 | pass | failed 0 | 24 / 25 | 22 / 2 (old marker) |
| PART 1 | 1990 / 0 | pass | failed 0 | 24 / 25 | 22 / 2 |
| PART 2 | 1990 / 0 | pass | failed 0 | 24 / 25 | 22 / 2 |
| PART 3 | 2057 / 0 | pass | failed 0 | 24 / 25 | 22 / 2 |
| PART 4 | 2168 / 0 | pass | failed 0 | 21 / 24 | 21 / 2 |

The ratchet did not grow: `?` 49 -> 45, skeleton 24 -> 23 (parked 0 / 0 throughout). The skeleton rows were created
in PART 1 equal to the pilot's count of `modes: n/a (skeleton ...)` pieces (22 core, 2 library), the same population
re-spelt. Slugs: 124 of 124 homed, counted as preddoc1 counted (R.8's 120 bold kebab slugs plus group-truth,
negated-class-hole, inner-label-read, bare-condition-labels; preddoc1's one-word `removal` is outside the count
as there); model PART SL.

## LINT AND READER CHANGES

`scripts/pred_doc_lint.py` (now L1-L12), `scripts/doc_profiles.py`, `scripts/entry`, the sample root moved to
`scripts/tests/pred_doc/root/docs/design/predicates/`, `scripts/tests/pred_doc_lint.py.test`,
`scripts/tests/entry_pieces.test`, `scripts/tests/pred_doc/mut.py`, `scripts/INDEX.md`. The form is written into
`docs/dev/pred/doc_format.md`, new sub-section "How the lint checks the changes above".

- (a) PAIRS: `docs/design/predicates/{core,core_details,library,library_details,parked,parked_details}.md`.
- (b) status `principle` (L4): legal only under `core/principles/`; a `principle` piece needs a `rulings:` item, as
  a `ruled` one does.
- (c) `skeleton: yes` (L8): exempts the piece from L8; the only value is `yes`, never on a `?` piece; the old line
  `modes: n/a (skeleton ...)` now FAILS L8. The ratchet gains a row `<word>-skeleton` per file beside the `?` row;
  both only shrink; `--write-ratchet` lowers both.
- (d) `see:` (L5): every tag exists in any file (forward allowed), never the piece itself; pilot mode skips a
  `see:` into a skipped pair as it skips a `needs:`.
- (e) details `was: <tag> (<date>, <why>)` and `formerly: <module.name> (<date>, <why>)`: grammar, a real date and a
  non-empty why (L2); a `was:` tag equals no live tag and is retired under one entry across all three files (L1); a
  `was:` line in a BASE file fails L6. The L2 escape is gone: a tag's path equals its file and section, always. The
  separate "tag in its file" check was REMOVED: its mutant survived because the section check already implies it
  (a section tag must carry its file word), so it was dead code.
- (f) a new rule L12, library fields: exactly one `module: <dotted lower-case name>` or `module: ?` on every
  non-`?` library piece; `module:` and `default:` only in the library file; `default:`'s one value is `yes`.
- (g) reader: `scripts/entry <previous tag>` resolves to the current piece; its first line is
  `entry: was <old> -> <new>` (`entry core/conditional/peek -l 0` prints `entry: was core/conditional/peek ->
  lib/control/peek` then the piece). `--state principle` lists principle pieces.

Tests: selftest 151 runs, 12 of 12 rules with a detected plant, 0 failures; 37 new plants (was/formerly grammar
and dates, a live or doubly-retired `was:` tag in one file and across files, a base `was:`, principle outside
principles and without rulings, `see:` to nothing / a second tag / itself, skeleton value / on `?` / old marker /
removed, skeleton ratchet rows, every L12 clause) and 4 new controls (a retired tag from another file with
`formerly: ?.pad.inner`, a dotted module and `module: ?` on a `?` piece, `see:` into a skipped pair, a fenced
`was:` line). `entry_pieces.test`: 4 new cases (a previous tag at levels 0 and 2, the current tag prints no was
line, `--state principle`).

MUTATION GATE (`python3 -I scripts/tests/pred_doc/mut.py`, as predlint2 ran it): **total 212, killed 196,
equivalent 16, SURVIVED 0, NOMATCH 0**. The 16 equivalents are predlint2's, unchanged in reason. Mutants re-aimed
at the new text where the old text moved (17); 36 new. Four survived on the first run and each was killed by a new
plant or control, not by listing: `formerly:` date unchecked (plant: impossible date), fenced `was:` parsed
(control), `was:` retired per file (plant: two files), `principle` anywhere (plant on a piece WITH a rulings item,
count 1); a fifth, the file-word check, was removed as above.

`scripts/CLAUDE.md` names no old path (checked); `scripts/INDEX.md`'s pred_doc_lint line updated.

## THE MOVE

`git mv` of the six files (in PART 1's commit, so the lint's new paths and the files moved together and every
commit lints clean): `docs/design/predicates.md` -> `predicates/core.md`, `predicates_details.md` ->
`core_details.md`, `predicates_library.md` -> `library.md`, `predicates_library_details.md` ->
`library_details.md`, `predicates_parked.md` -> `parked.md`, `predicates_parked_details.md` -> `parked_details.md`.
PART 1 also carried the two edits the new rules force on the documents: the 24 `modes: n/a (skeleton ...)` lines
became `skeleton: yes`, and `lib/modifiers/padded`, `lib/sets/anything` gained `module: ?`.

PART 2: `docs/design/predicates/CLAUDE.md` (new, 2,136 bytes); `docs/design/CLAUDE.md` (one line: `predicates/`);
`docs/dev/pred/CLAUDE.md` (doc_format no longer "PROPOSED ... not built"; `doc_ratchet.tsv` listed);
`docs/dev/pred/doc_format.md` (file table, STATUS line, the L2 sentence); the six files' head paragraphs (sibling
names; the draft and the ideas file by full path). No other live pointer: the remaining hits of the old names are
in files not to edit (the record, delivered lane reports and preddoc1's evidence, filed review r56, journal,
`to_main.md`). **`.claude/` lines naming the old paths: none** (grepped).

Not edited, and so now stale: `docs/dev/lanes/preddoc1_evidence/preddoc1_model.py` reads
`predicates_details.md` and its siblings by the old names (its PART LT); it is historical and will not run against
this tree.

## MACROS MOVED TO THE LIBRARY

The test, every core piece: is its definition a BODY written in the core language? Principles (21) are
primitives by definition: no. The rest:

| core tag | body? | reason |
|---|---|---|
| model/match, modes, table, places | no | the semantics the language is defined in |
| patterns/literals, flags | no | literal syntax and regex flags |
| patterns/sequence | no | the splice itself (regex concatenation) |
| patterns/alternation, quantifiers, atomic, lookaround | no | regex's own operators |
| **patterns/repeat** | **YES, moved** | its own ruled statement: "a library definition over count holes"; the draft R.1.14: "`repeat` is NOT a primitive" |
| labels/* (7) | no | label semantics |
| conditions/* (7) | no | the condition construct and its reads |
| filters/and, complement | no | `&` and `!` are operators |
| filters/operand-context, kinds | no | rules on operands |
| values/reads, one-type, number-domain, arithmetic, functions | no | reads, the type rule, `+ - * %`, the function rule |
| arrays/lift, class-order, class-positions, class-index | no | rules of the lift |
| arrays/enumerate | no | compile-time enumeration of an rx's strings: no pattern body expresses it |
| holes/* (19 + the zero-values sub-pieces) | no | the hole construct per position |
| **conditional/peek** | **YES, moved** | `/(?=${A})/` |
| **conditional/when** | **YES, moved** | `(test SEQ then) \| (NOT peek(test) SEQ else)`; the record already says "a LIBRARY DEFINITION ... no primitive" (when-meaning) |
| **conditional/test** | **YES, moved** | it is when's body read per kind of test; its WARNING stays core (below) |
| operators/precedence | no | grammar |
| operators/bindings | no | the binding and macro mechanism itself (see the finding below) |
| diagnostics/* (5) | no | compiler diagnostics |
| spellings/* (2) | no | spellings |

Moved, each converted in full, `module: ?` unless stated:

- `core/conditional/peek` -> **`lib/control/peek`** (ruled), `default: yes` (the only one), body `peek(A) :=
  /(?=${A})/`.
- `core/conditional/when` -> **`lib/control/when`** (ruled), body `when(test, then, else = //) := (test SEQ then) |
  (NOT peek(test) SEQ else)`; the signature makes `then` required.
- `core/conditional/test` -> **`lib/control/when-test`** (ruled), plus its open question split off as
  **`lib/control/when-test/not`** (`open not-test`, one piece one status). The tag is `when-test` (three words), not
  `when/test`, because a four-word piece cannot have the child the open question needs.
- `core/patterns/repeat` (ruled, skeleton) + the library's `?` piece `lib/rx/repeat` -> **`lib/rx/repeat`** (ruled),
  `module: rx` (the record: "the rx module"), three bodies, one per call form.
- New section `lib/control` ("Control"), by kind. The core section `conditional` is REMOVED (empty); the lint
  agrees (L11 is per file). Each moved details entry carries `was: <old tag> (2026-11-19, <why>)`.
- STAYS CORE: the warning that a bare-pattern test consumes, now **`core/diagnostics/consuming-test`** (ruled,
  when-peek "warn", `see: lib/control/when-test`). A body cannot see that an argument is a bare pattern (the draft
  R.1.10 (5)(a): "the WARNING ... is the COMPILER's ... since it must know that an argument is a bare pattern").
  Precedent: `core/diagnostics/nullable-hit`, a warning on a library name's argument, already core. `when-peek` is
  `shared:` between this piece and `lib/control/peek`.
- `see:` lines added: `core/patterns/quantifiers` and `core/holes/count` (its `needs: core/patterns/repeat`
  became `see: lib/rx/repeat`), `core/diagnostics/consuming-test`.

Every body was run against every ruled example of its piece in the frozen draft (MANAGER READINGS TESTED). No piece
had to stay core for a failed example.

FINDING for the manager (not moved; no core tag carries it): the draft §5.3, the source of the `?` piece
`core/operators/bindings`, defines `capture(x) := /(?<${x.label}>${x})/`, a body in the core language that has no
library piece at all (preddoc1 also left `capture` unhomed). `each`, `each_group`, `where_group` there are
structural compile-time tools over spelled arrays, not pattern bodies; `join` is already `lib/strings/join`.
Adding a `lib/...` `?` piece for `capture` would grow the ratchet, so it is left for the conversion of that section.

## MANAGER READINGS TESTED

Model `docs/dev/lanes/preddoc2_evidence/preddoc2_model.py`: 25 checks, 0 failed; 17 sabotages, each alone, 17 of 17
caught. Control: the DRAFT'S PRINTED answers (run by earlier lanes on libpcre2 and against PCRE2's own conditional
group), and for `when` a direct semantic model written from the ruled words with its own find-all loop; every
example line in the documents is checked verbatim against the run.

1. **`peek` has a body reproducing every ruled example: SUPPORTED.** `/(?=${A})/`: the when-test table's peek
   column, lookahead-labels (`37`, d = `3`), R.1.10's peek rows, when-default's hand-worked answers,
   `when(NOT peek(x), z)` (PARTS PE, W1, WT, WD, WN). Sabotages: s1 (peek consumes) fails PE W1 WT WD; s5 (labels
   hidden) fails PE.
2. **`when`, peek form and consumed form, has a body: SUPPORTED** for every MATCH answer: R.1.10's four-row table in
   all three modes against the printed table and the semantic model (W1), the when-test table (WT), when-default
   (WD), the condition test and the else-only by NOT on a condition and on a peek (WC, WCnot, WN), the call forms
   (WS: five legal, `when(x)` and `when(x, else = z)` refused), value-test (WV: the condition test and his test
   consumed), and the 2026-11-17 definition as its special case (W8: WH1 and the else form). Sabotages s2, s3, s4,
   s6, s7, s8, s16 each caught. NOT SUPPORTED by a body: the WARNING on a bare test; it stays core, above.
   Reading inside the body: `NOT peek(test)` is the negative lookahead (the draft's reading, R.1.10 (8)); NOT is
   applied only to a peek, so not-test is untouched.
3. **After the move the core needs no `needs:` into the library: SUPPORTED** (PART M3: zero `needs:` naming
   `lib/` or `parked/` in core.md; three core pieces carry `see:`; sabotage s15 caught). The one that existed,
   `core/holes/count` -> `core/patterns/repeat`, became a `see:`.
4. **No ruled statement changes wording: SUPPORTED** (PART M4, against the pilot `76024ee9e`): `core/patterns/repeat`
   (ruled) is word for word `lib/rx/repeat`'s statement; `when`, `test`, `peek` were `?` pieces with no statement to
   change (their statements are new). Sabotage s14 caught.

Also run: `rx.repeat`'s three bodies against RX5, the one-argument exact count, every copy illegal, AL2, B2 (per
mention), RX6 and the plural (PARTS RX, RXexact, RXnone, RXlift, RB, R6; WHOLE against python's `\d{2,4}`,
`\d{2}|\d{4}`, `\d+` on 63 texts, 0 differing); the zero-values sub-pieces' examples (ZVpattern, ZVcount, ZVclass;
s12, s13 caught).

PART 3, `principle` per piece (the test: the statement's quoted words are the owner's answer to a slug -> `ruled`;
words the record classes otherwise -> `principle`, the class written on the rulings item):

| core/principles/ | status | why |
|---|---|---|
| regex-default | ruled | quoted from a non-ruling entry, but settled by the slug ruling regex-settles ("yes settled") |
| explicit-exceptions | ruled | exception-rule |
| meaning-not-spelling | ruled | mark-domain ("as a PRINCIPLE"), spelling-phrasing |
| no-absence | **principle** | the record: "OWNER PRINCIPLE"; absent-rule was LOCKED on it, not the principle's ruling |
| conservative-first | ruled | operand-context's answer is the quoted sentence |
| general-rules | **principle** | quoted from "(1) LEAN, not a ruling" (his condition); array-lift was decided by it |
| rx-owns-flags | **principle** | "a PRINCIPLE stated", in a DISCUSSION |
| composed-at-point | ruled | zero-in-sequence's answer |
| namespace-at-reference | ruled | backref-across-parts' answer |
| operand-world | ruled | zero-place's answer |
| positions-own-rules | ruled | name-hole's answer |
| structural-warnings | **principle** | the record: PRINCIPLE |
| match-and-filter | ruled | complement-place's answer |
| matching-language | **principle** | "reflections, recorded as principles for the draft's framing, not rulings" |
| left-decides | ruled | join-order |
| stated-behaviour | ruled | padded-lazy-sparse's answer |
| nothing-outside-domain | ruled | number-edges |
| build-later | ruled | match-is-rx's answer |
| exact-wording | **principle** | a remark on the manager's method inside the zero-in-sequence entry, "no change asked" |
| check-his-regex | **principle** | STANDING INSTRUCTION |
| language-over-macros | **principle** | DIRECTION |
| labels-as-defined | **principle** | DIRECTION |

Two applied the brief's parenthesis ("keep ruled where the details entry cites a slug ruling") against its first
clause: no-absence and exact-wording cite a slug-ruling entry but the quoted words are not the slug's answer; I
took `principle` for both. Say if the parenthesis was meant literally.

zero-values: split into `core/holes/zero-values/{pattern,count,name,class,option}`; the parent stays a short
`reading` piece listing them (the grammar already allows a three-word piece with four-word children, as
`core/holes/class` has); option `ruled`, the rest `reading`; the old entry's content divided (nothing dropped:
the class cell's rejected candidate and reading, the option ruling, the count-value reading on the parent); new
examples for the pattern and count positions, run (PART ZV), with their rival readings as rejected candidates.

## FORMAT PROBLEMS FOUND

1. **Turning a `?` piece into a skeleton piece raises the skeleton ratchet row.** The rows only shrink, so that
   step is a hand edit of `doc_ratchet.tsv` (visible in the diff). Fine if conversions go `?` -> full; say so in
   the format if that is the rule.
2. **Warnings keyed on a library name's argument live in the core** (`consuming-test`, `nullable-hit`): "core holds
   primitives only" holds for their mechanism, but their statements must name a library macro. A general core
   piece ("a structural warning may be keyed on a library name's argument form") would let them stop naming the
   macro; not written (not ruled).
3. **A `principle` piece's rulings item carries `(class: ...)` by convention only**; the lint does not check that
   it is present.
4. **The four-word tag cap** forced `lib/control/when-test` (not `when/test`) so that its open question could be a
   child. A deeper tree would need a fifth word.
5. **The format's early text still says "Tags are never renamed"** and gives the L2 `was:` escape in the Tags
   bullet; later sub-sections win by the format's rule and I edited only the L2 sentence. A clean rewrite of
   doc_format's top half is the manager's.
6. **Piece bodies cite `predicates_draft.md` by bare name** (e.g. `core/arrays/class-positions`); from the new
   directory that reads as a sibling file. Only head paragraphs were changed, as briefed.
7. **The default else `//`** (the empty pattern) is my spelling of his `null` in the body; the format has no word
   for "a placeholder value in a signature".

## OWNER QUESTIONS LEFT

- **default-set**: which names, besides `peek`, are in the default-imported set (his lean names only `peek()`).
- **import-symbols** (already queued by the manager): his `(left,right) := import("blah", /left|right/)`. No parked
  piece on import exists, so his words went only into `lib/control/peek`'s details history.
- **not-test** (already open, now `lib/control/when-test/not`): NOT on a bare pattern as the test.
- **conditional-spelling** (already open, on `core/spellings/placeholders`).
- For the manager, not the owner: the `principle` reading of no-absence and exact-wording (above); the `capture`
  macro's missing library home; whether the consuming-test warning should become a general core form.

## EVIDENCE AND COMMANDS

- `(cd $PCREC_TMPDIR/scratch/preddoc2 && timeout 300 python3 -I -B <wt>/docs/dev/lanes/preddoc2_evidence/preddoc2_model.py)`
  -> `preddoc2_model.out`: 25 checks, 0 failed.
- `PREDDOC2_SABOTAGE=sN` for s1-s17, one at a time -> `preddoc2_sabotage.out`: 17 of 17 CAUGHT.
- `(cd <wt> && timeout 60 python3 -I scripts/pred_doc_lint.py)` -> `checks passed 2168, failed 0`
  (`checked: L1=188 L2=188 L3=3 L4=353 L5=80 L6=831 L7=163 L8=60 L9=129 L10=6 L11=4 L12=163`).
- `timeout 300 sh scripts/tests/pred_doc_lint.py.test` -> PASS (selftest 151 runs, 12 of 12 rules, 0 failures);
  `timeout 300 sh scripts/tests/entry_pieces.test` -> PASS (0 failures).
- `timeout 600 python3 -I scripts/tests/pred_doc/mut.py` -> `mut: total 212, killed 196, equivalent 16, SURVIVED 0,
  NOMATCH 0`.
- `timeout 120 make -s test-plan-lint` -> failed 0 (after every part).
- `python3 -I scripts/pred_doc_lint.py --write-ratchet` -> core=21, core-skeleton=21, lib=24, lib-skeleton=2,
  parked=0, parked-skeleton=0.
- `scripts/entry core/conditional/peek -l 0` -> `entry: was core/conditional/peek -> lib/control/peek`, then the
  piece; the same for `core/patterns/repeat`.
- Grep for old paths: `grep -rn 'predicates_library\|predicates_parked\|predicates_details\|design/predicates\.md'`
  over the tree; `.claude/`: no hit.
