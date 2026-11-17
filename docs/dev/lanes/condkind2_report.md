# condkind2 — the condition model WITHOUT the optional mark (lane report)

EXPLORATION, rules nothing (owner, COND-FAMILY 2026-11-16 21:19: "drop-mark: another exploration on these ideas").
Deliverable: `docs/design/condition_kind.md` Part II (the note's own revision; Part I kept as delivered, the header
marks the two parts). Evidence: `docs/dev/lanes/condkind2_evidence/` (`condkind2_nomark.py`, `condkind2_nomark.out`,
CLAUDE.md). No edit to `predicates_draft.md` (rev 22) or to any ruling.

## STATE AT HANDOFF

- Branch `lane/condkind2`, cut from main @ 86df3797e; the tip is the last commit on the branch.
- Delivered: Part II of `docs/design/condition_kind.md` (sections II.0-II.8); `condkind2_evidence/` (script, forward
  output, CLAUDE.md); this report and its history-index line in `docs/dev/history/claude_md/docs__dev__lanes.md`.
  `docs/design/CLAUDE.md` unchanged (the note's role is unchanged; that file sits 4 bytes under its limit).
- PREMISE TEST passed: from `$PCREC_TMPDIR/scratch/condkind2/`, lane condkind's commands (`rev22_ref.py`, then
  `condkind_model.py`) reproduced the committed `condkind_model.out` byte for byte, ORDER line aside (`diff` empty;
  `rev22_ref.py` printed "TOTAL engine-run cases 75530 differ 0 ... 346 programs").
- Rulings file `docs/dev/lanes/condkind2_rulings.md`: re-read before each commit and before this report: EMPTY (no
  R-n applied).
- Nothing built; `make` not run. Every run under `timeout`, from the scratch dir; each under 10 s.

OWED: none.

## THE MODEL WITHOUT THE MARK

A label control is nothing (absent = NULL; a test holding a NULL is unknown; the row is dropped) or a default
(COALESCE). Every construct of Part I section 3 restated (Part II.1.1); `all(c)`, defined in rev 22 as "c with every
label marked", loses its definition. By run (`condkind2_nomark.out` PART 1; each count unchanged by the swap run):
adding a condition never admits a subject, 0 of 11,388 pairs over 1,278 programs (rev 22's engine: 3 of 845);
record = `&` 0 differ (RZ, 14 controls) EXCEPT a cross-entry `$` (review r30 I: 9 of 110 under a local default);
equal behaviour: RULING-2 54 -> 0, RULING-7 30 -> 0, SIMULATE-9 order-free; `some(c)` and `none(c)` both hold 14 ->
0; one witness: 0 differ with one default, back (45 of 81 J subjects) when one label gets two defaults.
Review r30: A, B, C (RULING-6), D's mark half, E, H's marked pair and one-witness DISSOLVE; C/J (FIXIND-1,
relative-complement), D's classical half (inside `!q`), F, G (except FIXIND-5, which changes), H's default half, I,
L, M SURVIVE; K is Part I's **source-row**.

## THE REWRITE RUN

Target: rev 22's answers on every subject of the program's pool (rev 22's own engine for its pools; Part I's M2c,
equal to it on all 346 programs, for the worked pools). Tiers: T0 one constant per label; T1 per occurrence; T2 + a
`$x` default with x never absent (legal today); T3 + `$x`/`$x ± 1` for any x (not legal today); T4 a free value per
row (no default); NONE.

| set | programs | T0 | (of which: mark deleted, nothing) | T1 | T2 | T3 | T4 | NONE |
|---|---|---|---|---|---|---|---|---|
| rev 22's pools A, B, P, LST | 314 | 314 | 219 | 0 | 0 | 0 | 0 | 0 |
| worked examples + r30 witnesses | 21 | 19 | 5 | 1 | 0 | 1 | 0 | 0 |
| the lane's probes | 4 | 0 | 0 | 1 | 1 | 0 | 2 | 0 |

- Constant rewrites are the obvious stand-ins (`((h, m?): late)` -> `m = 30`; `(h?: <$k)` -> `h = 0`; mark-in-none ->
  `m = 2`). 0 of 335 need a value the label never holds.
- The brief's expected "cannot" shapes, tested: `(h?: <$k)` T0 (`h = 0`: a one-sided comparison has an extreme
  witness); a joint condition with a missing part T0; a mark under a group question T0 (per program); a zero-pass
  loop T0; two marked conditions on one label T1 (`h = 1` | `h = 8`: one default per OCCURRENCE). Only the TWO-sided
  `(h?: >$j & <$k)` needs an expression (`h = $j + 1`, T3).
- THE SHAPE NO DEFAULT REACHES: a joint relation between the absent label and a present one whose values range
  wider: `/(?<h>[0-4])?-(?<k>\d)/ & ((h?, k): h == k)`: `-3` HOLDS, `-7` FAILS under rev 22; no constant (4 off),
  `h = $k` holds on `-7`. The author writes a sentinel and extends the set by hand: `((h = "x", k): h == k | (h ==
  "x" & k < 5))`, 0 of 60 off (the lane's first hand projection for the second probe was off by one, caught by the
  run). The question the mark asked ("is k a value h can take") appears in none of the 335 programs.
- NOT COMPOSITIONAL: in 45 of 680 (program, program + one condition) pairs the rewrite of the smaller program must
  change in the larger (`(h?: <5)` -> `h = 0`, but `(h?: <5) & (k: <5)` FAILS on `b3` under rev 22 because no match
  of that program has an h): these are exactly the answers **domain-scope** made depend on other conditions.

## THE DEFAULT'S SCOPE

Side by side (Part II.3): per CONDITION (local COALESCE in the where-clause) vs per LABEL (a column of the statement,
`coalesce` in the select list). Local: record vs `&` differ 9 of 110 on a cross-entry `$a` (`-1`); `(h = 0: <5) &
(h = 9: >7)` legal and holding on 11 of 21 pool-A subjects where no one value fits; one-witness back (45). Column:
record = `&` (0), two defaults for one label an error, `$a` reads the default, but the default reaches conditions
that did not name it. Positional (reaches later conditions only) breaks `&`'s order (9). Per label rewrote 333 of the
335 programs. A looped default reads per pass; on zero passes the plain condition reads it (10 of 10 RZ subjects
hold) and a group question sees no pass (0). A default the label never holds: needed by 0 rewrites, but it is the
ONLY route for the shape above and for §5.2's `occurs.none((g = "": !"a"))`; out-of-range vs in-range changes 90 of
11,110 T2 answers. Silent drift (II.4): a dead default (`(h = 4: <3)` = no control, 0 differ) is decidable for
constant sets and is `default.unused` (b) already; a default does not follow an edit of its set (`late` -> `>= (9,
45)`: 2 of 11,110 off, `9`); `$` sets (5 of 60 marked occurrences) are decidable only per match.

## WHAT RETIRES AND WHAT SURVIVES

By grep (II.5, line cites there): the per-PROGRAM value set has no reader but the mark (and `all`, defined through
it); the §5.2 empty-intersection error reads "the values h can hold" from pure parts and keeps a per-LABEL regex
value set. RETIRED: zero-pass-empty, match-context, domain-scope, mark-narrows, mark-in-none (owner rulings);
one-witness, not-of-marked, the never-absent-mark warning (manager readings). CHANGES: absent-rule (3) (owner's word:
one control left); `all(c)` (manager's). STANDS: absent-rule (1), (2), (4), not-is-complement, label-twice,
record-is-product, zero-pass-record, optional-as-loop, default-set, colon-scope, unset-component/default-unused,
default-reaches-dollar inside one condition, (e1), (e2.1), (e2.2); mark-domain's principle stands (by construction).

## QUESTIONS FOR THE OWNER

Three, each with its current definition, example and leaning in Part II.6; a reply either way wanted.
- **drop-mark**: is the mark a construct of the language? 219 of 314 rev 22 programs answer alike with it deleted,
  all 314 with one constant per label. Leaning: drop it.
- **default-scope**: is a default a value for one test, or the label's value in the statement? `(a = 0: <10, b:
  >$a)` vs its `&` spelling on `-1`: differ under the first. Leaning: the label's value in the statement.
- **default-value**: may a default be a value the label never holds? The sentinel route needs it. Leaning: any text,
  no restriction; warn only on a DEAD default.

## LEFT OPEN

- The other review r30 round programs are not ported (r30's three DOM witnesses are).
- Rewrites are per pool; a different regex can need a different constant. Not counted.
- `all(c)` without the mark: the manager's to restate. B and C (RULING-6) dissolve by construction, not by a run.
- The column reading's zero-pass detail and where a statement-level default is written: not designed.
- Searched mode of a default: unchanged, not re-run.
- No critic round run (the manager launches it).
