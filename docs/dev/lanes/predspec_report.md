# Lane predspec report: preliminary predicate spec ([COND-FAMILY] #6)

## STATE AT HANDOFF

STATE: delivered. Documentation only (NO BUILD GO); nothing under `src/ cli/ lib/` touched; no make run.
Deliverable: `docs/design/predicates_draft.md` (DRAFT rev 0, sections 0-15 as briefed) and a one-line index entry
in `docs/design/CLAUDE.md` (merged with the `cond_family_syntax_survey.md` line to stay under the 12 KB limit;
`scripts/check_claudemd_size.sh --all` clean). Rulings file `docs/dev/lanes/predspec_rulings.md`: empty at every
read (start, before commit, before this report); no entry applied.
Premise test: PASSED. COND-FAMILY.md ends with the 2026-11-14 outer-layer note ("the expression language is the
OUTER layer"), preceded by the ERRATUM and the binding-vs-constraining-marks and `[]`-positional notes.
Validation: example behaviours (§12) checked with Python (`datetime.isoweekday`: 2026-11-14 Sat, 2026-11-13 Fri,
2024-02-29 Thu; day differences 13 and 30; 2026-11-14 +-15 = 2026-10-30..2026-11-29; a hand-written Luhn:
4111111111111111 valid, ...1112 invalid, 5500000000000004 valid). No pcrec run: nothing in the draft is built.

Resume summary for a follow-up (the exploration/critic lane): read §13 first (16 contradictions, 18 open items);
every rule in §§1-11 carries RULE / REASONING / STATUS with its note date; §15 maps sections to notes.

## SOURCES

- `docs/design/plan_row_bodies/COND-FAMILY.md`, all 571 lines (2026-11-12 through the 2026-11-14 outer-layer
  note): the source of truth; latest note wins.
- `docs/design/cond_family.md` (survey rev 0, D193): background; still the mechanism map (M1-M12, C3); its
  `rx ## P` where-clause and `_` scope rule are superseded by holes and `x:` conditions (noted in §15).
- `docs/design/cond_family_syntax_survey.md` (synsurv): background; `&!`/`=~` superseded (`!` filter, `~`);
  opt-in and class-contents recommendations stand (noted in §15).
- `docs/dev/decisions.md` D196 + addenda 1-2 (asymmetric `&`, precedence, mechanism untethered from syntax).
- `scripts/entry COND-FAMILY` (row status: not-started, umbrella).

## CONTRADICTIONS FOUND

Full text with both readings in `predicates_draft.md` §13; one line each here.

1. C1 `&` order: D196 (left chooses, order meaningful) vs 2026-11-14 "`&` commutes, order is readability only" and
   "`&` extensional".
2. C2 x-mode default for literals (11-13 evening) vs "every PCRE pattern is a one-literal program" (11-14 outer
   layer); the notes' own E-LUHN literal `( ?\d{4})` breaks under x.
3. C3 DEFINE holds `:=` bindings (11-13 evening) vs DEFINE only as PCRE syntax inside literals (11-14), while API
   callers keep the inner direction.
4. C4 `(\d+)${ <256 }` / `\d{3}&${<256}` read as guards, but `<256` is a full rx by the fractional-rx rule, so the
   hole would match a following numeral.
5. C5 `A[1,3,5]` not adopted, comma kept for `A[i, j]` (00:10) vs `X[1,3,5]` valid (`[]` positional note).
6. C6 binding a test is an error (`!~` note, 11-13) vs tests as bindings (one kind of binding, 11-13 evening).
7. C7 value-valued maps (`=>`, `["US" => ...]`, 11-13) vs maps = labelled groups with only `.index` (11-14).
8. C8 comma = `|` in list literals vs comma = AND in condition records ("records remain as shorthand").
9. C9 canonical-numeral rule makes E-CAL's `month: \d\d & between(1,12)` silently {10,11,12} vs label value types /
   "07 complies via unpad".
10. C10 transform-section spellings (`unpad() == 5`, `length() < 6`, `length(<=20)`) vs unary-only comparisons; an
    expression left of `:` (E-NEAR, E-RFC) vs "the left of `:` is a PATH".
11. C11 `x:` pure one automaton (01:00) vs ambiguous labels need PCRE's parse on the VM (11-13).
12. C12 define-before-use required (BLOCK SHAPE) vs forward references allowed (one kind of binding).
13. C13 bare undeclared name = label (NAME RESOLUTION) vs `$x` always the value (01:00).
14. C14 stamped VM fallback / [PRED-SPLIT] automatic demotion vs default level "too large = compile error, never a
    silent switch".
15. C15 in-context lookaround for pattern-level `&` (ruled leanings 11-13) vs all `&` expression-level after the
    outer layer + ERRATUM.
16. C16 precedence example `x & <256 | >300` = `x & ((<256)|(>300))` (00:10) vs D196 `&` tighter than `|`.

Status discrepancy (O3): several 2026-11-14 notes call leanings "ruled" (unset label false, union type of
duplicates, filtering by indexing) where the original note is a leaning.

## OPEN ITEMS

- The 18 open items of `predicates_draft.md` §13 (O1-O18), headline ones: O1 how a program's final expression meets
  the subject (search vs whole-subject); O6 the `functions` level presupposes [ENG-TDFA] DFA captures (a separate
  initiative); O9 the level of a run-time parameter too large to tabulate; O18 `records` silently drops unmatched
  lines (CRLF).
- The goals in §0 are a MANAGER DRAFT (from the lane brief) and have not been seen by the owner.
- Rewrites this document made to examples (each flagged in place): `=` for keyword arguments; `$` for values in
  E-CAL/E-RFC; explicit `unpad` for padded months/days; `(?:[ ]?\d{4})` in E-LUHN; `weekday_of(...)` as a plain macro
  in E-RFC to keep it out of the organisational layer; `& !""` and `word_of` in E-FILE instead of `skip_empty` and a
  lambda; `/^${q}$/m` as the JSONL top level.
- No owner question raised by this lane beyond §13; nothing filed in plan.md (IDS YOU MAY USE: none).
