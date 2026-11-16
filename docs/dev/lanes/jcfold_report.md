# Lane jcfold: the 2026-11-16 owner rulings folded into the joint-condition note (design only)

Branch `lane/jcfold`, cut from main 4ae1f9bdc. Tier opus. Design only: no edit under `src/`, `cli/`, `lib/`,
`memfn/`, `tests/`; `predicates_draft.md`, `COND-FAMILY.md`, `predicates_future.md` and `plan.md` untouched.

## STATE AT HANDOFF

- DONE. `docs/design/joint_condition.md` is at the RULED state: every ruled point stated once (§2, J1-J9, his words
  and the CF time), the record derived as the product case and checked rule by rule (§4D), every changed sentence
  listed (§4C), the contradictions and open items in §8, what rev 20 must change in §9 (44 rows).
- Rulings file `docs/dev/lanes/jcfold_rulings.md`: EMPTY at every read (last read before the final commit; times
  11:40, 11:45, 11:48 and at the report). No entry applied.
- Validation: COMPLETE, nothing owed. Commands and totals in WHAT CHANGED IN THE NOTE (evidence).
- Premise test: `grep -c '^\*\*2026-11-16' docs/design/plan_row_bodies/COND-FAMILY.md` = 24; `grep -n '^## 4B\|^## 8'
  docs/design/joint_condition.md` showed both sections at launch.

## RULINGS FOLDED

All 24 entries of 2026-11-16 are now reflected in the note; the ones newly folded by this lane (the earlier ones were
folded by jointexp, tupleval, tupleval2, unsetdef and are restated once in §2):

| CF time | slug | his words | where in the note |
|---|---|---|---|
| 11:05 | unset-component | "unset-component: yes" | J6; item 6; §4B opening, §4B.7; §6 B2 |
| 11:05 | default-unused | "default-unused: agree" (WARNING: the manager's reading, tested HOLDS) | J6; §4B.1 diagnostics |
| 11:17 | joint-loops | "I agree. Makes sense." | J7; item 5 (pairing, the error text, the moved warning's text); §6 B4 |
| 11:20 | two-orders | "I agree. They look sufficiently different to me and I like the control. Can you think of a use for the second form?" | J5; item 4 (five uses; "no warning" tested) |
| 11:27 | modifier-lift | "modifier-lift: yes. ... However the form is 'do everything to both' so the logic makes sense" | J8; item 3 table; §4A.4; §6 B3 (parked: predicates_future.md item 2) |
| 11:32 | colon-scope | "colon-scope: yes with refinement: (a, b = c): ... the 'c' is a binding et al" | J2; item 1; §4A.8; §4B.1 (two new rows); C13 |
| 11:35 | record-is-product | "record-is-product: absolutely. This is precisely the sort of simplifying semantics I'm looking for." | J9 (the organising rule); §4D |

Standing rulings honoured: "A RECORD is NOT a value" (CF:851-852, untouched: §4A.1, §4D D17); "an array of something
is that something" (CF 00:08); his criteria order; spellings as placeholders (D193 add. 4).

## WHAT CHANGED IN THE NOTE

The full sentence-by-sentence list is the note's §4C. In short:

- HEADER: EXPLORATION -> RULED; STATUS rewritten; evidence paragraph extended.
- §2 REWRITTEN as J1-J9 (form, colon scope, value and arity, order, both orders, unset and defaults, loops, modifiers,
  the record) plus LEVEL (now tested) and the cost list N1-N5.
- §3 table rewritten with the ruling per row.
- §4 items 1-9: ruled wording; item 4 and item 5 rewritten (uses of the per-part form; the precise pairing loop; the
  sibling-loop error text; the moved warning's text).
- §4A: every "open record-is-product / set-arity / modifier-lift / two-orders / colon-scope" marked ruled; §4A.9
  rewritten to the one open point (tuple-parts).
- §4B: the base rule, default-unused and the default's value-side scope ruled; two rows added to WHAT v MAY BE.
- §4C NEW (corrections list and the manager's readings tested), §4D NEW (the record derived, 26 rules checked).
- §5: problems 5 and 8 tested; tally simpler 7, same 6, worse 0.
- §6, §7, §8 rewritten; §9 NEW (rev 20's change table).
- Also: `docs/design/CLAUDE.md` (the note's line: "(exploration)" -> RULED); the lanes history index
  (`docs/dev/history/claude_md/docs__dev__lanes.md`) gains this report's entry.

EVIDENCE (every command `timeout 120 python3 -I`, run from the temp root, libpcre2-8 10.46, Python 3.14.4 `re`):

| script | result | note |
|---|---|---|
| `docs/dev/lanes/jointexp_check.py` (unchanged) | 27,752 cases, 0 differ, 0 engine disagreements | output identical to the committed `jointexp_check.out` (diff without the version line: empty) |
| `docs/dev/lanes/tupleval2_check.py` (unchanged) | 42,079 cases, 0 differ, 0 engine disagreements | identical to `tupleval2_check.out` |
| `docs/dev/lanes/unsetdef_check.py` (unchanged) | 233,720 cases, 0 differ, 0 engine disagreements | identical to `unsetdef_check.out` |
| `docs/dev/lanes/jcfold_check.py` (NEW, `.out` committed) | 2,019,088 cases, 0 differ, 0 engine disagreements | tables (RD) 76,860; (RZ) 2,220 (1,110 subjects x 2 readings; the readings differ on 5, by design of the table); (SE) 13,328; (MN) 2,232; (RC) 1,924,375 of which 220,750 engine-run, the rest the rows' union checked in Python; (NL) 73 |
| `JCFOLD_SABOTAGE=1 ... jcfold_check.py` | 3,825 differ | (RD) without the "m unset" guard and (SE) with `>=` for `>`: the check can fail |

The three claims the first lane left UNTESTED, now TESTED: the `$`-bound start/end pair (table (SE), 168 classes);
the three-field month-name range (table (MN), text order day/name/year, 4 rows); the "at most 2k - 1 rows" count
(table (RC): k = 2, 3, 4, maximum 3, 5, 7 reached, never exceeded over 325 + 2,625 + 2,541 bound pairs). New claims
made testable by the rulings: record = product WITH A DEFAULT (table (RD)); the record at different depths (table
(RZ), the contradiction); nested-loop pairing (table (NL)).

## CONSEQUENCES DERIVED BY THE LANE

1. The record derived (§4D): of 26 record rules of the draft, 23 follow from J1-J8 specialised to a product, 2
   contradict (one corner: labels at different depths, zero passes), 1 is a new consequence (a label twice).
2. The pairing loop of joint-loops, read literally, misses two cases (one label outside every loop; nested loops);
   the precise statement: the DEEPEST loop enclosing any named label, every other label in the same pass or outside
   it, else the sibling error (item 5; table (NL)). Open item **pairing-loop**.
3. A label twice on the left is an error, so by J9 a record `(h: <5, h: >2)` becomes one; the draft is silent; the
   alternative is the diagonal reading. Open item **label-twice**.
4. On the value side a bare computed-label name is the binding, i.e. the computed label's macro: `<=dim` is an ERROR
   naming `<=$dim`, not a second spelling (C13 closes that way).
5. A default is on the value side: a bare label name there is an error naming `$h`; a name that is both a binding
   and a label means the binding.
6. The per-part form has five worked uses (minimum width and height, a bounding box, a colour threshold, a schedule
   slot, `(2, >= 4)`); in the schedule slot dictionary order would be WRONG (`between((1, 9), (5, 16))` admits Monday
   20:00). With one part pinned the two forms agree.
7. The looped warning keys off the shape (a `|` of conditions naming labels that can repeat); rev 19's name
   `compare.looped` names a gone subject (suggestion: `alt.looped`, the spelling step's).

THE MANAGER'S READINGS, TESTED (the note's §4C holds the ones folded here; the earlier ones):

| entry | the manager's reading or consequence | verdict |
|---|---|---|
| CF 00:06 (1) | in a macro body a parameter bound to a field reference may stand left of `:` | HOLDS for rev 19; MOOT under the joint condition (no job), PENDING retire-paused |
| CF 00:06 (2) | macro-arguments WITHDRAWN as unneeded | HOLDS; overtaken by his NO (CF 00:08) |
| CF 00:06 (3) | the accessor bindings `h_is` leave the tuple examples | HOLDS (the joint form has none) |
| CF 00:08 | an array of field references is a field reference; picking an entry must be shown an existing tool | HOLDS for rev 19; MOOT (O75 has no job) |
| CF 09:47 | "left/right" of the colon | WRONG on the sides (he meant the binding sign, CF 09:49); already corrected by tupleval2 |
| CF 09:49 | colon-less tuple on either side of a binding | CONFIRMED (09:50), then reopened (09:58): tuple-parts OPEN, no user |
| CF 10:18 | first-rest = keep the built-in order now | HOLDS (ruled 10:22) |
| CF 10:22 | tuple-parts no user, open; two-orders live | HOLDS; two-orders since ANSWERED (11:20) |
| CF 10:37 | a go to write up and test the default; closed only when he says | HOLDS (closed 11:05) |
| CF 11:05 | "agree" = WARNING | HOLDS |
| CF 11:20 | no warning, unless confusion shows | HOLDS, INCOMPLETE (the slip is silent; a BY DESIGN row needed) |
| CF 11:32 | C13 closes as `$` (`<=$dim`, `==$wd`) | HOLDS, INCOMPLETE (bare is an error, not a synonym; the text missing) |
| CF 11:32 | a default still ONE string | HOLDS |

## CONTRADICTIONS FOUND

Not resolved; both texts in the note's §8.

1. **zero-pass-record**: joint-loops (CF 11:17, per-pass pairing, a label outside the loop "having its one value on
   every pass") + record-is-product (CF 11:35) vs the draft's "`(major: 1, minor: >=4)` = `(major: 1) & (minor:
   >=4)`" (`predicates_draft.md:1546`, the record's AND RULED CF:863/CF:866 (b)) and "For `all`/the plain condition
   the two spellings always agree" (`:1674`). They differ when the labels sit at different depths and the deeper
   loop runs zero passes: `/(?<k>\d)(?:;(?<h>\d))*/ & (h: <5, k: 3|4|5|6|7)` on `9` holds by the rulings, fails by
   the draft (table (RZ): 5 of 1,110).
2. **library-not-syntax**: CF:644-650 (2026-11-14: "TUPLE CONDITIONS: a LIBRARY macro ... no syntax"), carried as
   "Tuples as a library macro: RULED (CF:644), SUPERSEDES predx's tuple-on-the-left-of-`:` syntax (S12)"
   (`predicates_draft.md:2760-2761`), vs record-is-product (CF 11:35: the joint condition, whose left IS a tuple on
   the left of `:`, is "the ONE mechanism"). Closest address: his own idea at 00:31 and the 00:35 GO; no entry
   withdraws CF:644 by name.
3. **retire-paused**: the direction was PAUSED, not reversed (CF 00:31: rev 19 "stands as the record of that
   direction"), and four of its items are RULED (the sigil 00:06, `lex_` names CF:1226, argument order CF:1253, the
   fixed-size compares in the first library CF:1166); the joint condition leaves them no job, and no entry retires
   them. (The fifth, the looped warning, IS addressed: moved at 11:17.) Rev 20 must know whether to retire them and
   whether the joint condition takes CF:1166's first-library slot.

## WHAT REV 20 MUST CHANGE IN THE DRAFT

The note's §9: a 44-row table, one row per draft section or numbered item with its `predicates_draft.md:N` cite (rev
19, main 4ae1f9bdc), the change, and the ruling. Rows that hang on a contradiction are marked PENDING: §4.1's
exception and the record equality (rows 13, 14), §4.3's "always agree" (16), the `^` row (25), §8's names, projection
and field reference (28, 30), §8 STATUS (31), C25 (36), O75/O76 (41), DECIDED field-reference items (42), owner
questions (16)/(17) (43), §0.1 L72-L81 (5), §0.2 phase 1 (7). Not pending: the `$` reads (L37, §4.4, C13, E-CAL
`<=$dim`, E-RFC `==$wd`), L45, the arity (§2.1), the tuple atom (§2.4, §5.4 comparison row), the unset rule with a
default (§4.2), the moved and new warnings (§7.1), the decided-prefix withdrawal (§8 caveat (5), DECIDED (55)), O56,
O69, O72 closed, the new look-alike rows.

## OPEN ITEMS

- **tuple-parts** (owner; unchanged): open with no user (predicates_future.md item 4).
- **zero-pass-record**, **library-not-syntax**, **retire-paused** (owner): the three contradictions above.
- **label-twice** (owner; the lane's lean: error).
- **pairing-loop** (owner; a wording confirmation, no answer changes).
- For the critic round: the §9 table is the lane's reading of what the rulings require; §4D's verdicts and the
  (RZ) table are the ones to attack first.
