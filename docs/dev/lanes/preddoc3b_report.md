# Lane preddoc3b — core values, arrays, operators, diagnostics, spellings converted; new section core/modules

2026-11-19, opus, documents only. Branch lane/preddoc3b, worktree worktrees/preddoc3b.

## STATE AT HANDOFF

- Done. The five sections are converted in full and core/modules is new (after core/operators).
  - Commits: dfea8e42b (values, arrays, model), 90f05b554 (operators, modules), ac4748705 (diagnostics, spellings), then the delivery commit.
- Rulings file docs/dev/lanes/preddoc3b_rulings.md: **empty** (re-read before each commit and before this report).
- `python3 -I scripts/pred_doc_lint.py`: **checks passed 2841, failed 2**. Both failures are the ONE allowed case, the retired tag still live in the parked file:
  - `L1 core_details.md: was: parked/import-symbols/import is a live tag`;
  - `L9 parked_details.md: slug 'import-symbols' is on 2 tags (core/modules/binding-list, parked/import-symbols/import)`.
  - Both clear when sibling preddoc3c deletes parked/import-symbols/import.
  - Premise run before any edit: 2278 passed, 0 failed.
- `make -s test-plan-lint`: checks passed 2, failed 0.
- Model: 17 checks, 0 failed. Sabotage: 17 plants, each caught by its target check.
- Acceptance: 0 `?` and 0 skeleton pieces left in my sections (model check NOQ, 33 pieces).
- FOR THE MANAGER: core/modules/import carries `was: parked/import-symbols/import (2026-11-19, ruled by the owner: it is in the language)` and slug `import-several`.
  - Slug `import-symbols` moved to core/modules/binding-list, the piece that ruling actually rules.
  - preddoc3c deletes the parked piece. The record line `tags: parked/import-symbols` will then fail L5 unless the record's tags line is updated (not mine to edit).

## PIECES CONVERTED

33 pieces in my sections: 21 ruled, 7 reading, 3 open, 2 under-construction.

| tag | status | change |
|---|---|---|
| core/values/reads | ruled 11-18 | skeleton -> full; example run |
| core/values/one-type | ruled 11-18 | skeleton -> full; the composition rule marked a reading |
| core/values/number-domain | ruled 11-18 | skeleton -> full |
| core/values/arithmetic | ruled 11-19 | skeleton -> full; plus-operands and number-edges folded; two example lines |
| core/values/functions | ruled 11-18 | skeleton -> full; the clause order marked a reading |
| core/arrays/lift | ruled 11-18 | skeleton -> full |
| core/arrays/enumerate | ruled 11-14 | `?` -> full ("Enumerate go") |
| core/arrays/class-order | ruled 11-19 | skeleton -> full |
| core/arrays/class-positions | open class-positions | skeleton -> full; candidates C1/C2/C3, Q1/Q2, A/B; C1 and C2 run |
| core/arrays/class-index | open class-index | skeleton -> full; (a)/(b)/(c); (a) and (b) run |
| core/operators/precedence | reading | `?` -> the one operator table; its ruled rows point at their pieces |
| core/operators/bindings | ruled 11-15 | `?` -> full |
| core/operators/statements | reading | NEW (split from bindings: the program shape and `@` statements are LEAN, the bindings RULED; rule 6) |
| core/modules/map | ruled 11-15 | NEW section |
| core/modules/import | ruled 11-19 | NEW; was: parked/import-symbols/import |
| core/modules/binding-list | ruled 11-19 | NEW |
| core/modules/call-shorthand | ruled 11-19 | NEW |
| core/modules/all-symbols | ruled 11-19 | NEW |
| core/modules/leave-out | ruled 11-19 | NEW |
| core/modules/conflicts | ruled 11-19 | NEW |
| core/modules/default-set | reading | NEW (his LEAN; the implicit-line form is ruled statement 5) |
| core/modules/default-set/members | open default-set | NEW (split: one piece, one status) |
| core/modules/import-filter | under-construction | NEW (his IDEA) |
| core/modules/positional | under-construction | NEW (statement 7) |
| core/modules/export | reading | NEW (the `@export` lean, pending since 11-14) |
| core/diagnostics/errors | reading | `?` -> an index of errors with their pieces |
| core/diagnostics/warnings | ruled 11-17 | `?` -> full; a fires-on table, names placeholders |
| core/diagnostics/dollar-form | ruled 11-19 | details: two rejected candidates added |
| core/diagnostics/under-construction, nullable-hit, consuming-test | unchanged | already converted |
| core/spellings/placeholders | ruled 11-17 | `?` -> a table of every placeholder (incl. the new import spellings) |
| core/spellings/condition-parentheses | reading | unchanged |

New pieces and why (rule 6):
- core/operators/statements: a status differs from bindings.
- default-set/members: the open question split from the reading.
- the twelve modules pieces: part B of the brief.

Every modules piece carries `modes: n/a (no matching involved)` and its section paragraph says the spellings are placeholders once.

BODIES IN THE CORE LANGUAGE (rule 5), not moved:
- the draft §5.3's `capture(x) := /(?<${x.label}>${x})/` is a library body with no piece;
- `each`, `each_group` and `where_group` are compile-time tools with no piece.
- Both are recorded in core/operators/bindings history.

## RULINGS FOLDED

Every `rulings:` item quotes the record word for word, with the entry's exact title (lint L4 passes on all).
- **values**:
  - hole-reads-capture; read-is-constant; unset-in-hole;
  - match-is-rx; number-domain; numeral-width;
  - plus-operands; number-edges; "`+` is for numbers only";
  - construction-line; what "under construction" was about.
- **arrays**:
  - array-lift, and the value-is-pattern lean it settled;
  - "2026-11-14 RULINGS on the predx gaps" ("I love it. Enumerate go.");
  - class-order, and his question that carried it.
- **operators**:
  - sequence-precedence; quantifier operators;
  - macro bindings (11-13);
  - "2026-11-14 RULINGS on rev 3's contradictions": "Agree with mapping", "1. start with &...", the type picture, the review r8 answers;
  - no alpha operators (predx §11);
  - the bare condition in a hole;
  - the undeclared-name rule (11-12 later).
- **modules** (2026-11-19 unless noted):
  - the review r8 answers (map, 11-15);
  - import-several; import/export as functions (11-14 addendum);
  - import-symbols, its addition (bare `=` first), the leave-out correction, the conflicts remark, the double-name discussion;
  - statements 5, 6 and 7 of import-symbols, for default-set, call-shorthand and positional;
  - the filter idea inside import-several.
- **diagnostics**:
  - the empty-match hazard and its rx-selector amendment (11-14);
  - the principle for warnings; the list accepted and its `pcrec.` addendum;
  - polarity-rule; empty-search-error; the numbered-label warning;
  - the three remaining candidates; dollar-diagnostic.
- **spellings**: hits-text ("spelling to be reviewed with all other spellings").

Rulings after rev 29's fold that override the draft (rule 2), all folded:
- plus-operands; number-edges; class-order;
- the bare condition in a hole;
- import-several; import-symbols and its additions.

## DRAFT SENTENCES CONTRADICTED

- Draft §7 MODULES / the 11-14 addendum: "it must resolve to EXACTLY ONE file; several matches are a compile error".
  - The piece now says an import may resolve to several files, and one name bound to it is the combined map (core/modules/import; import-several).
  - The old sentence is in `rejected:`.
- Draft §5.1 and §5.4: "(c) the LEFT of `:=` ... design only".
  - The named binding list is RULED (core/modules/binding-list).
  - A bare positional `(a, b) :=` is under construction (core/modules/positional).
- Draft §5.1 / §2.3: "a macro in a hole is the unapplied-macro error".
  - The piece adds "except a condition: a bare condition in a hole is legal" (core/operators/bindings; 11-19 "for a condition bare, yes").
- Draft R.1.14 / T10, the manager's (c) of plus-operands: "(joining is the sequence operator)".
  - The piece says joining is the sequence operator OR `join` over an array (negated-class-hole's `join(c)`) (core/values/arithmetic).
- Draft T15/T16, "OPEN (other-holes)" where they touch arithmetic on non-numbers.
  - Now ruled: nothing, with a warning where known (plus-operands).
- Draft §7 "import weekday as wd" for a clash (11-14 lean).
  - The piece says the rename is `(wd = weekday) := ...` (core/modules/binding-list).
- Draft §5.5's codepoint order for a class in a lift.
  - Replaced by class-order: longest first (core/arrays/class-order; already noted in rev 29).

## MANAGER READINGS TESTED

1. Every ruled statement traces to one record entry title: **SUPPORTED**.
   - Model check M1: 21 ruled pieces, each with at least one rulings item citing an existing record title; lint L4 passes on all 422 citations.
   - Caveat: inline "(a reading)" sentences inside ruled pieces are the pilot style. They trace to no ruling by design.
   - Two citations had to use the CONTAINING bold entry, because the dated paragraphs inside it are not bold titles: "the type picture" and "answers to the four questions of review r8" both sit under "2026-11-14 RULINGS on rev 3's contradictions".
2. No piece needs a `needs:` into a later core section: **SUPPORTED** (model check M2: none).
   - values and arrays only `see:` core/holes and core/diagnostics.
   - diagnostics/errors `needs:` core/modules/conflicts, which is now EARLIER (modules precedes diagnostics).
3. Each ruled piece's three-mode example gives the draft's printed answer: **SUPPORTED where the draft prints one**.
   - The draft's printed answers are reproduced for reads (the label, against the capture rival), one-type (A2), number-domain, lift (AL1), enumerate (the priority list) and class-order (CO).
   - arithmetic's `5--5` FAILS is the rule-2 case (number-edges overrides the draft's open edge).
   - functions, precedence and bindings examples are new and checked by the direct model and a rival instead of a printed answer.
   - The modules pieces have no regex model (`modes: n/a`).
4. The 11-14 `import ... as` lean and "members travel with the type" are not contradicted: **SUPPORTED, with a nuance**.
   - `as` itself is gone (no alphabetic keywords, predx §11). Its NEED, renaming for a clash, is met by `(wd = weekday) :=`, so the lean's intent stands under a new spelling.
   - Members-with-the-type is untouched: today's rulings bind names into the bare space and do not change `.` lookup into a type.
   - The 11-14 "a later library member of the same name breaks the build, never silently rebinds" agrees with the `(=)` hide-label warning and the conflicts error.

## FORMAT PROBLEMS FOUND

- L1/L9 fallout of a ruled-out parked piece, while the parked file still holds it: the `was:` line cannot pass L1 until the sibling deletes the piece. A lane split (convert here, delete there) cannot land clean on its own. Recommendation: land preddoc3b and preddoc3c together, or let L1 accept a `was:` whose target carries `retired-by:`.
- Record `tags: parked/import-symbols` will fail L5 after the deletion; the record is not a lane's to edit.
- L4's title rule: a dated, non-bold paragraph inside a bold entry ("2026-11-15 RULING — the type picture") is not a citable title. The citation has to name the containing entry and the paragraph in a trailing note. A citable sub-entry form would help.
- L7's 40-line cap pushed the operator table and the spellings table into dense rows; both fit, but more rows will force a split (the spellings table has 20 rows).
- The precedence piece is a `reading` holding ruled rows; the "one piece, one status" rule makes a table of mixed grounds a reading with per-row grounds. That shape may want a sanctioned form.

## OWNER QUESTIONS LEFT

- **class-positions**: the order of a lift's results with two class positions.
  - C1: the lift as one position, longest first. C2: the first class slowest, ascending.
  - Witness: `/${\d + \d}/` SEARCHED `x13`: C1 `13`@1, C2 `1`@1.
  - Same question for a lazy quantifier (Q1/Q2, `x100`) and the class first (A/B, `x11`).
- **class-index**: the order of a class in `enumerate`'s array.
  - (a): codepoint for the array, the class order inside a lift.
  - (b): codepoint everywhere.
  - Witness: `/${enumerate(/\d/) + 1}/` SEARCHED `x10`: (a) `10`@1, (b) `1`@1.
- **default-set**: which names besides `peek` are default-imported.
  - Readings: `peek` alone, or every name the core points at (`when`, `occurrences`, ...).
  - Witness: a bare `when(...)` with no import, which compiles or is an undeclared-name error.
- **export-choice** (pending since 11-14, never asked):
  - `@export(names)` with the no-export error;
  - or every top-level binding exported unless `_`-prefixed.
  - Witness: a library file with no `@export`, a compile error or all public.
- **positional-tuple** (a possible STOP-RULE case, kept `under-construction` as briefed):
  - 11-16 OWNER CONFIRMATION ("Yes": `(a, b) := lo` takes a tuple apart);
  - against 11-19 statement 7 (a bare positional `(a, b) := X` "left undefined ... under construction, not illegal", the language "does not clearly have" an ordered right side).
  - Read here as compatible: the meaning is defined for a tuple, the build is not there. The two parts on `(a, b) := lo` with lo a tuple: under the 11-16 words it binds the parts; under the 11-19 words it is the under-construction error.
- Not stated, listed open in their pieces:
  - the import filter before or after the conflict check;
  - an interior lookaround or backreference in `enumerate`'s argument;
  - the enumerate budget's number.

## EVIDENCE AND COMMANDS

- `timeout 300 python3 -I -B docs/dev/lanes/preddoc3b_evidence/preddoc3b_model.py` -> preddoc3b_model.out: 17 checks, 0 failed.
  - EXreads, EXonetype, EXdomain, EXedges, EXplus, EXleft, EXlift, EXenum, EXclassorder, EXclasspos, EXclassindex, EXprec, EXpair, M1, M2, SL, NOQ.
  - Each EX check requires its formatted line verbatim in core.md and a rival that differs.
- `PREDDOC3B_SABOTAGE=sN` for N = 1..17, each alone -> preddoc3b_sabotage.out: every plant caught by its target check.
  - s5 (the `+` rule) and s9 (the class order) also fail the checks that share the rule.
- SLUGS (how counted): the model's SL list holds the 25 slugs found by grepping the frozen draft's question list (rev 29.1) for rows whose subject is in values, arrays, operators, diagnostics or spellings: 22 slugs. To them are added the three slugs of today's import entries (import-symbols, import-several, default-set). SL: 25 of 25 on a `slugs:` line in my sections.
- `timeout 120 python3 -I scripts/pred_doc_lint.py` -> 2841 passed, 2 failed (the allowed case above).
- `timeout 300 make -s test-plan-lint` -> passed 2, failed 0.
- `scripts/lanecheck` -> run at delivery.
