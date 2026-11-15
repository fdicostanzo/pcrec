# Lane predspec2 report: post-draft rulings folded into the predicate spec ([COND-FAMILY] #6)

## STATE AT HANDOFF

STATE: delivered. Documentation only (NO BUILD GO); nothing under `src/ cli/ lib/` touched; no make run (none
needed: one design document). Deliverable: `docs/design/predicates_draft.md` rev 2 (changelog at the top),
committed on `lane/predspec2`. Premise test PASSED: COND-FAMILY.md ends with the 2026-11-14 "counting occurrences"
ruling note. Rulings file `docs/dev/lanes/predspec2_rulings.md`: empty at every read (start, before commit, before
this report); no entry applied. Sources folded: COND-FAMILY.md from "2026-11-14 RULINGS on predicates_draft.md §13"
to the end (the earlier 2026-11-14 notes were already in rev 0, written after the outer-layer note), plus
`docs/dev/lanes/predx_report.md` §§3, 7, 8, 10, 11 for the content those rulings adopt.
Validation: the three new examples' expected behaviours are by construction (E-SEP separators, E-DEPTH depths,
E-HTTP counts); rev 0's Python-checked weekday/Luhn/day-difference results are unchanged. No cite of the form
file-colon-line (grep clean); pre-commit staged checks 52/52.

Resume summary: §13 now opens with the RESOLVED list (10 items), then rev 0 items still open, then twelve NEW
contradictions (C17-C28) and seven new open items (O19-O25). Each ruled item's STATUS line carries "OWNER RULED
2026-11-14" or "MANAGER LEAN" as the note says.

## RULINGS FOLDED

Each ruling or lean -> the section that now states it.

| ruling / lean (COND-FAMILY 2026-11-14 note) | status used | section |
|---|---|---|
| C9: string-set comparisons, integers `\d+` variable width, explicit `unpad` | OWNER RULED | §2.4; E-CAL §12.5; C9 RESOLVED |
| C4: guard hole `(\d+)&${ <256 }`; without `&` a following item | OWNER RULED | §11; C4 RESOLVED |
| C2: no implicit x-mode, per-literal `(?x)`; multi-line belongs to the expression language | OWNER RULED | §11, §5.1; E-LUHN `( ?\d{4})` restored; C2 RESOLVED |
| predx Q1 context-marked sets (S2), TENTATIVE | OWNER RULED (TENTATIVE) | §11, §2.1; C15 partly resolved; O25 |
| Q2 some-parse at default, PCRE's parse at `vm` | OWNER RULED | §4.5; C11 RESOLVED |
| Q3 = C2 | OWNER RULED | §11 |
| Q4 sequence rule for repeated labels; bare `$x` error; last iteration at `vm` | OWNER RULED | §4.3; O4 RESOLVED |
| Q5 "linear, automaton code only" (automaton split + parameter-only computations at default) | OWNER RULED | §6.1, G2; C14, O9 RESOLVED; E-NEAR (b) |
| Q7 1-based | OWNER RULED | §3.2; O11 RESOLVED |
| Q8 cut interfaces/members/UFCS/types() | OWNER RULED | §1, §9 (rewritten as the cut list), §14 |
| Q10 finite-group backrefs = [BACKREF-FINITE], not #6 | OWNER RULED | §5.5, §11, §14 |
| Q11 reporting axis: span + accept-class values; spans need `captures` (S9) | OWNER RULED | §6.2, §6.1 (`captures` switch) |
| Q12 bounded recursion by a strictly decreasing literal parameter (S6), one example | OWNER RULED | §7, G4; E-DEPTH §12.11 |
| Q13 `records` tiling, `gaps = allow` (S14) | OWNER RULED | §7; O18 RESOLVED; E-FILE §12.8 |
| Q14 prior art answered in predx scratch | OWNER RULED | §15 background (draft cites neither) |
| Q6 one condition form (concept) | OWNER RULED | §4.1; C10 RESOLVED |
| Q6/Q9 spelling: computed values as match-dependent bindings | MANAGER LEAN | §4.4 (`with` removed); E-WEEKDAY, E-CAL, E-RFC, E-NEAR |
| Q9 compile-time assertions (concept) | OWNER RULED | §5.6 |
| NO ALPHABETIC OPERATORS OR KEYWORDS | OWNER RULED | §5.1, §0, §14 |
| import/export as functions; module = map; `@export(names)` filter; no-export error | MANAGER LEAN | §7, §2.1, §5.3 |
| import argument a set of names, resolves to exactly one file | OWNER RULED (Frank addendum) | §7 |
| `@` effect statements; unused-pattern and bare-statement errors | MANAGER LEAN | §5.1, §5.4, §5.6 |
| pullback as pipeline, `&` right-associative (S1) | MANAGER LEAN | §2.7, §2.2; E-JSONL, E-FILE, E-WEEKDAY |
| arrays of filters / transforms | OWNER RULED | §3.5 |
| tuple comparisons as a library macro | OWNER RULED | §8 |
| `enumerate` (budget, PCRE priority order, built-in) | OWNER RULED (design adoption) | §5.5; E-SEP §12.10 |
| `&` at `vm` = DFA candidates + VM verify ([PRED-SPLIT]) | OWNER RULED | §6.1 |
| value-vs-value relations priced by class count (S3) | OWNER RULED | §4.6; E-CAL, E-RFC, E-NEAR (c) |
| empty-match rule (final nullable pattern in search) replacing the empty-entry error | OWNER RULED | §7; E-FILE |
| named warnings, `@warn.off`/`@warn.error`, rx selectors, `warn.unused` | OWNER RULED | §7.1, §4.2, §4.5, §2.7 |
| counting via the `occurs` library | OWNER RULED (name `occurs` MANAGER LEAN) | §8, §4.3; E-HTTP §12.9 |

## CHANGED SECTIONS

- Top: new Changelog (rev 2, rev 0).
- §0: status rev 2; status marks gain OWNER RULED 2026-11-14 / MANAGER LEAN; G2 restated as "linear, automaton
  code only"; G3 checkable form (no x-mode break; `empty.search` warning); G4 (bounded recursion, enumerate budget).
- §1: two layers; organisational layer cut.
- §2.1 (module = map, no number type), §2.2 (right-associative `&`, `!transform` error), §2.3 (transforms only as
  stages), §2.4 (C9 rewritten), §2.6 (`count` moved to C21), NEW §2.7 transforms/pipeline.
- §3.2 (1-based ruled; module members), §3.4 (pullbacks extensional, enumerate structural), NEW §3.5.
- §4.1 (one condition form; left of `:` a path), §4.2 (`label.unset`), §4.3 (sequence rule, `occurs`), §4.4
  (computed labels as bindings), §4.5 (some-parse), NEW §4.6 relations by class count.
- §5.1 (program shape, no keywords, `@`), §5.3 (`export capture` keyword superseded), §5.4 (`@`), NEW §5.5
  `enumerate`, NEW §5.6 assertions.
- §6 split into §6.1 levels (promise, `captures`, `&` at `vm`) and NEW §6.2 reporting axis.
- §7 (bounded recursion, tiling, modules, empty-match), NEW §7.1 named warnings.
- §8 (`occurs`, tuples, `assert`, transforms list).
- §9 replaced by the cut list. §10 trimmed. §11 (no x-mode, context-marked sets, guard `&`, [BACKREF-FINITE]).
- §12: all eight examples rewritten to the newest spellings (pipeline, bindings, `@assert`, `import`); three added
  (E-HTTP `occurs`, E-SEP `enumerate`, E-DEPTH bounded recursion).
- §13: RESOLVED list; open rev 0 items kept with updates; NEW C17-C28, O19-O25. §14, §15 updated.

## REMAINING OPEN

Still open from rev 0: C1, C3, C5, C6, C7, C8, C12, C13, C15 (partly), C16; O1, O2, O3, O5, O6, O7, O8, O10, O12,
O13, O14, O15, O16, O17.

Contradictions found BETWEEN the new rulings (STOP RULE: listed, not resolved; full text in §13):
1. C17 `&`'s structural effect (distribution order) unstated though `.index` after `&` with filter arrays needs it.
2. C18 named assertions (`name := assert.none(...)`) vs "effect macros cannot drop `@`".
3. C19 assertions as "their own value kind" vs two kinds and no boolean type.
4. C20 `p(x)` = `x & p` vs transforms (`x & unpad` is a no-op warning, `unpad(S)` superseded).
5. C21 `count` as a value (§2.6) vs the counting ruling's "NOT a count value".
6. C22 the ruling's `month: unpad & between(1, 12)` vs §4.1 "`name:` takes one operand term, tighter than `&`".
7. C23 `&` inside inner-direction PCRE text (C4 ruling) vs ERRATUM "`&` is not rx syntax" / G3 `R&D`.
8. C24 `ci("Host")` as a function (counting) vs `ci` as a pipeline transform (pullback lean).
9. C25 `lex_ge([major, minor, patch], ...)`: an array literal is an alternation, names lost (the reason `export([leap])` was rejected).
10. C26 empty-match ERROR "opted out" vs "errors cannot be disabled".
11. C27 context-marked sets vs rev 0's "a pattern as a set matches entirely" (`/^S/` = {"S"}) for anchored label conditions.
12. C28 `occurs.all(x: S)` vs `x: S` already meaning all iterations.

New open items: O19 which pattern a match-dependent binding attaches to; O20 how `records` declares separator
bytes for tiling; O21 several literal-argument definitions for a recursive base case; O22 per-binding `@warn.off`
and `@each` spellings; O23 the `occurs` name; O24 export lean status (`_` convention only as an explicit filter);
O25 context-marked sets TENTATIVE, first critic target.
