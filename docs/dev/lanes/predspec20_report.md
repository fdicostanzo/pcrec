# Lane predspec20 — rev 20 of `docs/design/predicates_draft.md` (design text only)

## STATE AT HANDOFF

OWED: none

- Branch `lane/predspec20`, cut from main aef673e62. Commits: 85cee1967 (evidence), a09f4514d, 655aa0c4c,
  69993e798 (WIP draft), and the final commit carrying this report.
- Deliverable: `docs/design/predicates_draft.md` rev 20; evidence `docs/dev/lanes/predspec20_check.py`/`.out`.
- Validation: `make test-spec-history test-doc-lint` green (no `*** [... test-...]` line, rc 0).
- No file under `src/`, `cli/`, `lib/`, `memfn/`, `tests/`; `docs/design/predicates_future.md` and
  `docs/design/joint_condition.md` NOT edited. No D/K/abi/sabotage ids. Rulings file
  `predspec20_rulings.md`: EMPTY throughout (last read 15:54).

## WHAT REV 20 CHANGES

The draft now states the predicate design alone. A reader new to `joint_condition.md` reads §4.1 (the joint
condition, the record as its product), §4.2 (the absent-label rule, examples first: `t2` with optional minutes and
the list; table (AR); the general form; DOM once; the principles; THE UNDEFINED ITEMS), §4.3 (the pairing rule) and
§2.4 (tuple atoms). The field-reference direction of rev 16-19 is RETIRED (names, order, slot) or PAUSED (the sigil,
§4.1's exception, the projection, O75/O76); rev 19's §8 text and §4.1 exception moved verbatim to the new §16, and
the in-place sites (§5.4 `^` row, §3.2 tool 1, §3.5, §0.1 L72-L81) are marked PAUSED, not deleted. Changelog: rev 20
entry (A)-(F).

## SECTION 9 ROWS APPLIED

All 73 rows of joint_condition.md §9 applied or answered; NA: none; stopped: none.

| rows | site in rev 20 | state |
|---|---|---|
| 1 | Changelog rev 20 entry | done |
| 2, 70 | §0 new table THE ENTRIES AFTER REV 19 (00:06-15:29, his words, the manager's readings labelled, 14:50 readings, r26/r28 dispositions); rows on `some`, the "+ or *" control and the per-match rule marked OVERTAKEN 14:31 | done |
| 3, 4, 5, 6, 58 | §0.1 L37 ERROR, L45 BY DESIGN, L72-L81 PAUSED, L16/L23/L30/L36/L52/L55/L56/L65 restated, new L82-L97; prose (rev 16/18 paragraphs, new REV 20 re-apply paragraph naming the overtaken STATUS clauses) | done |
| 7 | §0.2 REV 20 bullet (joint condition in the slot) | done |
| 8 | §0.3 field reference PAUSED; new words tuple/tuple set/arity, joint condition, absent, optional mark/default, pass, DOM(h); `set once` and `record` rows | done |
| 9, 10 | §2.1 SETS CARRY AN ARITY; §2.4 TUPLE ATOMS, dictionary order, DICT-DOMAIN, `$` component, both orders | done |
| 11, 53 | §2.7 `compare.width` pointer to the joint condition; MODIFIERS ON TUPLE SETS (which macros lift) | done |
| 12, 48 | §3.5 and §3.2 tool 1 reference text marked PAUSED in place (CENSUS-4 tag) | done |
| 13, 14, 68 | §4.1 REV 20: NO EXCEPTION; THE JOINT CONDITION (form, product, mixed record, label-twice, controls, colon scope, loops); STATUS; exception moved to §16.2 | done |
| 15, 45, 54, 55, 60, 62, 73 | §4.2 REPLACED whole | done |
| 16, 56, 67 | §4.3 table rows (plain, `all`, `some`), zero-iteration examples, SAME ITERATION as product case, THE PAIRING RULE (optional-as-loop), out-of-range note, STATUS | done |
| 17 | §4.4 `==$wd`, `$` sentence, absent inputs (e1); §4.6 `==$wd` | done, with the TUPLE-BINDING sentence (a computed label is arity 1; a match-dependent tuple inline or passed, never bound; the manager's reading) |
| 18 | §5.2 label default = head default | done |
| 19-25, 59 | §5.4 head count six, record row, value-in-position row narrowed, new value-tuple / joint-condition / label-controls rows, `=` row, entry extent, `:` row, comparison row, `^` row PAUSED, STATUS | done |
| 26 | §6.1 THE JOINT CONDITION AT THE DEFAULT LEVEL | done |
| 27, 60 | §7.1 `label.unset`, `default.unused`, never-absent-mark warning, `compare.looped` moved, `compare.repeated` gone, `label.both_sides` PROPOSED | done |
| 28-31, 46 | §8 new bullet (comparison sets in the first-library slot, (1)-(6)); rev 19 TUPLE COMPARISONS..FIELD REFERENCE moved to §16.1; §8 STATUS; §16 table of retired/paused items | done |
| 32-34 | §12.5 `<=$dim` + declared-table second spelling; §12.6 `==$wd`; census rows; REV 20 RE-APPLIED note | done |
| 35, 36, 51 | §13 C13 RESOLVED; C25 RESOLVED; C13 premises at O55, O47-area, O68 | done |
| 37-44 | §13 O56, O69, O72, O73/O74, O75/O76/O71, DECIDED, owner questions, new items | done (pre-compaction part of this lane) |
| 47 | §14 Tuples | done |
| 49 | §9 cut list `compare.width` text | done |
| 50 | O47 CLOSED moot; O68 restated | done |
| 52 | §1 libraries list | done |
| 57 | §2.6 ZERO HITS, `xyz` hand check, STATUS, SUPERSEDES; rev 10 changelog O28 note | done |
| 61 | §8 `when` (scoped, §4H.8); §12 census row untouched (no case uses `when`) | done |
| 63 | every old-answer site restated (§0 table rows, L36/L55/L56/L65, §2.6, §4.2, §4.3, §12 E-HTTP sentence, C28, O28) | done |
| 64 | `predicates_future.md` items 3, 5, 6, 7: the manager's edit (this lane does not touch that file) | NA here by brief; listed for the manager |
| 65, 66, 72 | §4.2 THE UNDEFINED ITEMS (a)-(f); §13 OPEN ITEMS NEW IN REV 20 | done |
| 69 | §8 `occurs` entry, C28, O50 (e), §0 row | done |
| 71 | §13 FIXB-9 GENERAL FORM overtaken in part | done |

## CARRIED REVIEW ITEMS (review r19)

- CENSUS-5 + SIMULATE-1: §16.1 (rev 19's §8 evidence sentence and BINDING paragraph) and §5.4 `^` row: the B-rows
  and "828 of 828 refused" restated as THE MODEL OF THE STATED RULE, not independent evidence.
- CENSUS-4: §3.5's "an array of field references is a field reference" tagged as the manager's consequence.
- CENSUS-8: §16.1 THE PROJECTION (iv): the standalone other side DEFERRED with a trigger (a use wanting the other side
  of `&` as a thing in its own right, met only if the sigil returns), not "does not arise".

## UNDEFINED ITEMS DECIDED OR LEFT

| item | stated as | answer (run) |
|---|---|---|
| (a) DOM not exactly computable | the manager's reading, to be attacked | under/over-approximation; same answer answers, could differ is a compile error naming the construct (`(h?: "aaba")` on `/(?<h>(?<a>a+)b\k<a>)?x/`); 0 silent changes |
| (b) context of "some match" | the manager's reading; OPEN WITH OWNER, **match-context** | pattern reading; branch reset on `b`: pattern HOLDS, context FAILS (1 of 142) |
| (c) default inside `all` | the manager's reading | the default stands (`''`: `all` HOLDS, plain FAILS; 1 of 259) |
| (d) zero-pass-empty | the manager's 14:50 (b); awaiting assent | closes under F1 |
| (e1) computed label on an absent input | the lane's proposal | absent itself, its own controls (`-5`: `(mnum?: <3)` HOLDS) |
| (e2) `$a` of an absent a | the lane's proposal | the condition FAILS; whether a default for a reaches `$a`: OPEN |
| (e3) a mark through a macro | the lane's proposal | `all(c)` marks a passed condition; per-label mark on a passed condition: OPEN |
| (f) one warning "D is never consulted" | the lane's proposal | fires for m in `t`; not in `t2` or the list |

## EVIDENCE

`docs/dev/lanes/predspec20_check.py`/`.out` (libpcre2-8 10.46, Python 3.14 `re`; run from scratch with `python3 -I`):
PART A, twelve prior lane scripts re-run, 12 of 12 byte-for-byte SAME (premise: absfix reproduced at aef673e62);
PART B, 821 engine-run cases, 0 differ, 0 engine disagreements, 56,564 whole-match probes; sabotage
(`PREDSPEC20_SABOTAGE=1`) produces 1 silent change in (RA) and 10 differences in (E1). Control caveat: (GF)-style
agreement between the general form and the ruled engine is close to definitional (shared subjects); the independent
controls are the engine-run regexes.

## LEFT OPEN

- **match-context** (new owner question), **zero-pass-empty** (assent), **tuple-parts** (no user).
- (e2) default reaching `$a`; (e3) per-label mark on a passed condition; `list_of`'s minimum.
- Row 64 (`predicates_future.md` items 3, 5, 6, 7): the manager's edit.

Plain-words drafts for the owner (each: reply either way):

- **match-context**: "When a label is marked optional and is missing, we read it as 'some value it could have had'.
  Could have had in ANY match of the pattern, or only in a match that agrees with the other labels of THIS match? Example:
  a pattern where `a` lines allow any digit after them and `b` lines only 5-9; on a bare `b`, 'some digit below 5'
  holds under the first reading, fails under the second. My leaning: any match of the pattern (fixed when compiled,
  cheaper, one table per label)."
- **zero-pass-empty**: "With the mark meaning 'some value would do' everywhere, a marked label tested against a set
  that turns out empty fails, on an empty list as anywhere else. Agree that this closes the question?"
- **default-reaches-dollar** (from (e2)): "If a condition gives `a` a default and also reads `$a` on the value side,
  does the default fill `$a` too? On `-5` with `(a = 0: <10, b: >$a)`: yes means it holds, no means it fails. My
  leaning: yes (one value per label per condition), but not decided."
