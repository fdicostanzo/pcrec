# Lane predspot — five owner rulings of 2026-11-22 folded into the predicate documents

Branch lane/predspot, cut from lane/pred-rev28 at 75d2318bd. Opus tier. Design only: nothing is built, and no
`make` target reads the evidence.

## STATE AT HANDOFF

OWED: none

- Group 1 (labels) is commit 17f9cc50f. Group 2 (flags), the evidence and this report are the commits after it on
  lane/predspot. Its tip is given in the reply to main.
- The rulings file `docs/dev/lanes/predspot_rulings.md` stayed empty for the whole run. It was re-read before
  each commit and before this report; no R-n arrived.
- The lint: `(cd W && timeout 120 python3 -I scripts/pred_doc_lint.py)` → `checks passed 7000, failed 0` (W is
  the worktree). It is re-run at the end of this lane; that count is in the reply to main.
- `make -s test-plan-lint` is clean.
- The model: 27 checks, 0 failed (`predspot_model.out`).
- The plants: 29 plants, 0 not caught, each turning its target check FAIL with no traceback (`predspot_sabotage.out`).
- KNOWN LIMIT (EVID-4) is unchanged. It is stated in the model header and in predspot_evidence/CLAUDE.md.

## RULINGS FOLDED

Group 1. Each ruling is quoted word for word in its details entry, with its record title.
- argument-default: "for me this is an error". Record: "2026-11-22 OWNER RULING — argument-default: an error;
  and his reason: a label is to the SPOT in the pattern, a parameter is a template, not a piece of the pattern".
  - core/labels/paths/argument-default is ruled 2026-11-22.
  - New principle: core/principles/label-names-spot.
- wrapper-export: "agree (a)". The provided bodies are restated with an export list on their spot `[(=) = x]`.
  - New piece: lib/convention/argument-labels.
  - peek's "Labels A sets are readable after it" is withdrawn.
- transform-export: "yes". capture, rx.repeat and list_of export through the call. hits and occurrences keep `hit`.

Group 2. The record titles:
- "2026-11-22 OWNER RULING — program-options: yes; and a PROPOSAL: `i` keeps inheriting, with a "weak" value the
  program sets"
- "2026-11-22 OWNER, on weak-meets-weak: "Consider this: weak settings do not propagate.""
- "2026-11-22 OWNER RULING — hole-flags: yes to all (weak values do not propagate; only an explicit `i` is
  inherited at a hole; `m` and `s` are no longer inherited)"

The pieces:
- program-options: "program-options: yes."
  - lib/builtin/options (ruled 2026-11-22) gains `@options(..)`. It is a lexical file scope: `m`, `s`, `n`, `x` and
    the weak `i` apply from the statement on, never across an import, and a literal's own flags win.
  - It quotes "Using predicate language it's going to be more likely to use () in a literal to mean no capturing
    group."
  - core/patterns/flags is restated. core/spellings/placeholders gains a row (the spelling is a placeholder).
- hole-flags: "hole-flags: yes to all." It REVISES flags-scope of 2026-11-19 (`i`, `m`, `s`).
  - core/holes/flags and core/holes/flags/in-filter are restated and re-dated, with the three parts.
  - core/principles/rx-owns-flags quotes his point 4 and his reason, and is re-dated.
- His proposal lists four values (on, off, weak on, weak off) where he writes "three settings". This is recorded
  as written in core/holes/flags's details: on and off are explicit; weak on and weak off are a file's default.

## MANAGER READINGS TESTED

Group 1: argument-default (a)–(e), A3 and the brief's convention readings. All are SUPPORTED as run, by checks
ARGLABEL, INPLACE, ARGOWN, SPOT, SWEEP, GRID and PLACES.

Group 2 (record letters (a)–(e); the brief's (e') and (f)):

| reading | verdict | check |
|---|---|---|
| (a) explicit = written in the literal's text (`(?i)`, `(?-i)`, `(?i:..)`, `/.../i`); any_case's body writes one; a program option is never explicit | SUPPORTED | EXPLICIT (9 settings) |
| (b) the sides of an `&` in a hole inherit an explicit `i` only; `pcrec.flags.filter` keeps its trigger | SUPPORTED | FILTER (trigger computed over a population) |
| (c) `x`, `xx`, `n`, `U` stay not inherited; `J` unchanged | SUPPORTED for `x`, `n` (and `m`, `s` no longer inherited); `xx`, `U`, `J` not modelled | NOTINH |
| (d) the options and the weak `i` are one lexical table, from the statement on | SUPPORTED (weak `i` shown at the top of a file only: not ruled lower) | LEXICAL |
| (e) a same-file binding in a hole has the same defaults: nothing visible changes | SUPPORTED | LIBFILE |
| (e') a file is a program file or a library file; a library keeps its own options | SUPPORTED | LIBFILE, lines "A library keeps its own options", "Never across an import" |
| (f) with `n`, a plain `( )` is no capture and no numbered label | SUPPORTED (0 numbered groups against 2) | NUMBERS |

What (f) does to the documents:
- core/labels/numbers gains a bullet: a number names fewer groups, only the named ones.
- In the name table, the "capture only" cell gains "(none under `n`)" and the "neither" cell gains "a plain `( )`
  under `n`".

READINGS NOT SUPPORTED: none.

## ANSWERS CHANGED

- Group 1: one. `B(A) & (A.d: <5)`, with B(rx) := `/${[p = rx]}-${rx}/` and A := `/(?<d>\d)/`.
  - Under argument-default the use alone exports nothing, so `A.d` reads the labelled spot (the first digit).
  - Candidate (local) read the use alone (the second digit).
  - Its two lines ("Both uses, (local)" and "Both uses, (error)") are now one, with the (error) answers.
- Group 2: none among printed lines. FSWEEP found 4 flag lines at the starting commit, all with an explicit `(?i)`:
  - core.md `/a(?i)b/`
  - `/(?i)id-${/blah/}/`
  - `/(?i)id-${/[a-z]+/ & /b.*/}/`
  - `/(?i)${C}/`

  Each was reproduced under the 2026-11-19 rule and stands under hole-flags. No printed line rested on an
  inherited `m`/`s` or on a non-explicit `i`.
- The new example lines show the change itself. Under 2026-11-19's rule:
  - `/id-${word}/` gave the record's line (a); it now gives the record's line (b), verbatim (EXAMPLES).
  - `/(?s)a${dot}b/` with dot := `/./` held on `a\nb`; it now FAILS.
- FLAGGRID: 18 of its 78 decided cells answer differently under 2026-11-19's rule. They are listed in its summary
  line.

## WHAT MOVED

Group 1:

| piece | change |
|---|---|
| core/labels/paths/argument-default | ruled (an error), readings (a)–(e), four lines |
| core/principles/label-names-spot | new principle |
| call-prefix, closed-argument, two-sources (first shape settled), core/patterns/atomic, label-reference, holes/labels, nested-scope | restated; nested-scope's Example 1 now an error |
| errors table, names table | a row each |
| lib/convention/argument-labels | new piece (ruled) |
| peek, when, atomic, contains, startsWith, endsWith, anchored, padded, quoted, any_case, list_of, rx.repeat, capture | bodies restated with `[(=) = x]` |
| hits, occurrences | keep `hit`; the hits line is re-spelled `hits.hit.g` |
| parked user-doc-traps | a bullet, re-dated |

Lines gone: 9 (SWEEP). Of those, 6 are RESPELLED, 2 are an error now, and 1 is DROPPED. 14 lines were added.

Group 2:

| piece | change |
|---|---|
| core/principles/rx-owns-flags | point 4 and his reason quoted; narrowed by hole-flags; 2026-11-22 |
| core/patterns/flags | restated (file options as defaults; explicit defined); 2026-11-22 |
| core/holes/flags | restated (three parts); weak example and s example, 4 lines; 2026-11-22 |
| core/holes/flags/in-filter | explicit `i` only; trigger sentence; 2026-11-22 |
| core/labels/numbers | the `n` bullet; 2026-11-22 |
| core/diagnostics/warnings | `pcrec.flags.filter` row; 2026-11-22 |
| core/spellings/placeholders | `@options(..)` row; 2026-11-22 |
| nested-scope | flags bullet |
| names table | the two `n` cells |
| lib/builtin/options | `@options(..)`, program options, weak `i`, his `n` sentence, not-ruled list, 2 lines; 2026-11-22 |
| lib/modifiers/any-case | its `(?i:..)` is explicit; the tail re-spelled `/(?i:${[(=) = rx]})/` |

## DRAFT READINGS ADDED

- (the lane's) the argument-default refusal is keyed on the template: a read of a name that only a parameter's
  argument holds. Run on every GRID cell; untested as a rule beyond it.
- (the lane's, at the brief) a file is a program file or a library file, each with its own options (LIBFILE).
- (the lane's, at the brief) under `n` only named groups are numbered (NUMBERS).
- (the lane's) the `pcrec.flags.filter` trigger is stated for an explicit `i`, the one flag a hole passes on.
  This replaces the earlier reading that `m` and `s` follow the same comparison.

## OWNER QUESTIONS LEFT

None of these is ruled, and none was applied.
- capture-export
- two-sources' second shape
- zero-condition-binding
- `(?<:x>...)` as a final spelling
- the `@options(..)` spelling, and whether it may appear more than once
- whether hide and identity are provided names
- macro variables and types
- count-several
- capture-loop-value
- zero-in-loop
- whether `i` may be set weakly insensitive only at the top of a file
- options beyond `m`, `s`, `n`, `x` (`xx`, `J`, `U`)

No printed program awaits a slug: AWAITS found 23 at the start and 0 now.

## EVIDENCE AND COMMANDS

- The model: `timeout 2400 python3 -I -B docs/dev/lanes/predspot_evidence/predspot_model.py` →
  `predspot_model: 27 checks, 0 failed` (predspot_model.out).
- The plants: `PREDSPOT_SABOTAGE=all timeout 9000 python3 -I -B .../predspot_model.py` → `predspot_sabotage: 29 plants, 0 not caught`
  (predspot_sabotage.out).
- The counts, each from that run:
  - GRID: 144 cells, AGREE 144.
  - FLAGGRID: 128 cells, AGREE 78, DISAGREE 0, n/a 50, UNDECIDED 0.
  - SWEEP: 220 lines now, 215 at the start, 0 moved unlisted.
    - CRASH 1, DIFF 6 and unparsed 2 are engine limits that were already there at the start and are unchanged (SWEEP
      fails any that changed).
  - FSWEEP: 4 flag lines then, 9 now, 0 bad.
  - NULLABLE: 366 programs, 0 nullable loops.
  - QUOTES: 15 sentences, 7 titles.
  - DOC: 22 lines.
  - SUCCESSOR: 9 models, every red declared with its FAIL-line digest.
- AWAITS: `git show 75d2318bd:<file> | grep -c "awaits argument-default"` over the three base files → 23.
- The lint: `(cd W && timeout 120 python3 -I scripts/pred_doc_lint.py)` → `checks passed 7000, failed 0`.
- `make -s test-plan-lint`: clean.
