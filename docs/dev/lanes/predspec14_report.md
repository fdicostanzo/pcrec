# predspec14 — predicates_draft.md rev 13 -> rev 14 (lane predspec14, opus, 2026-11-15)

Design only, no build go. Branch `lane/predspec14` (cut from `lane/predspec13`). Rulings: COND-FAMILY.md on main,
CF:1083-1148 (the five entries after rev 13 and the owner's tuple idea), applied with rulings R-1 to R-5.

## STATE AT HANDOFF

- STATE: done. Rev 14 committed on `lane/predspec14`; this report, the evidence script and its output, and the
  census script committed beside it.
- Rulings file `docs/dev/lanes/predspec14_rulings.md`: last entry applied **R-5** (read before each commit and
  before this report; R-1 to R-5 all applied).
- Validation (in the worktree, the box in the owner's evening hold: no suites, no queue jobs):
  `make test-spec-history` 11 passed, 0 failed; `make test-plan-lint` 2 passed, 0 failed (GREEN after the
  housekeeping commit, below). Evidence: `timeout 300 python3 -I docs/dev/lanes/predspec14_anchor.py` (run from the
  lane scratch dir) -> `docs/dev/lanes/predspec14_anchor.out`, rc 0, **engines disagree on 0 rows** (libpcre2-8
  10.46 via ctypes vs Python 3.14 `re`). Its first two tables are rev 13's, re-run, byte-identical to
  `predspec13_anchor.out`.
- Housekeeping (its own commit, f5fafc231): the two inherited PL14 hits fixed:
  `docs/dev/lanes/predspec12_report.md`'s quoted lint message respelled with "(line elided)" in place of the
  `plan.md`/report line numbers; `docs/dev/lanes/land1115c_report.md` taken from main.
- Index: one line added to `docs/dev/history/claude_md/docs__dev__lanes.md` (the per-lane history index the lanes
  CLAUDE.md requires in the same change).
- Owed: none.
- ONE POINT FOR THE MANAGER (not hidden): R-2 relayed the manager's consequence that `padded(/\b5/)` becomes plain
  PCRE `/0*\b5/`. The COND-FAMILY record marks that consequence "to be checked by the next revision". Checked: it
  conflicts with the draft's hole rule (L8, the edge-assertion error at a hole's edge, from CF:713/761), because
  under the ruled body the argument IS in a hole. Rev 14 keeps the error (`padded(/\b5/)` is refused exactly like
  `/x${/\b5/}/`) and lists it as DECIDED (34). If the manager or owner wants plain PCRE there, L8 itself changes for
  every hole; that is a separate decision. Not a STOP: the conflicting sentence is a manager consequence, not a
  ruled statement.

## WHAT REV 14 CHANGES

(A) WORDING (RULED, CF:1083-1091: "That's a good clarification"). §11's rule is renamed **THE ONE WHOLE-MATCH
RULE**: a filter role matches its stretch whole; elsewhere an rx is searched or spliced as in PCRE; an explicit
anchor reads the innermost scoped match. A new §0.3 row reserves "anchored" for the macro and real
`\A`/`\z`/`\Z`/`^`/`$`. §8 states the contrast (`${a & b}` ties a and b to each other on the hole's stretch;
`anchored(x)` pins x to its scope's ends) and that `anchored(rx) := /\A(?:${rx})\z/` is a PLAIN MACRO, with the
group there because rx may have a top-level alternation (`/\Aa|b\z/` vs `/\A(?:a|b)\z/`).

WORDING CENSUS (`docs/dev/lanes/predspec14_census.py OLD NEW`, heuristic classes by context; rev 13 copy kept in
the lane scratch):

| meaning | rev 13 | rev 14 |
|---|---|---|
| whole-match requirement or `&` tie (in the draft's voice, plus history and quotations) | 94 | 62 |
| the macro `anchored` | 88 | 119 |
| real assertions (the noun "anchor(s)") | 75 | 92 |
| the warning's name (`anchor.operand` / `anchor.whole`) | 22 | 45 |
| changelog (history) | 19 | 26 |
| other meanings (E-NEAR's `anchor` date; PCRE2_ANCHORED, the caller's anchored mode, "unanchored search") | 11 | 11 |
| total | 309 | 355 |

Of the 94 whole-match-sense uses in rev 13 (outside the changelog), 49 sat on lines rev 14 rewrote. Every
draft-voice use was respelled ("matches its stretch whole", "matched whole", "the one whole-match rule", "pinned by
`anchored(...)`"); the 62 that remain were each read and are: owner and record QUOTATIONS (e.g. "rx is not
anchored unless...", "what does it mean that they are anchored?"), HISTORY records (the rev 10/11/12/13
re-application paragraphs, the provenance table, closed items' "as asked" text, DECIDED (18)-(29)), the new words
row and ruling text that name the word itself, and the macro sense in E-HTTP ("ANCHORED", "the anchored block").
The rises in the other classes are rev 14's new text (the warning table, the contrast, the rulings).

(B) `anchored` IN A HOLE (RULED, CF:1093-1098, "anchored-in-hole: agree"). No `anchored`-specific error;
`x${anchored(/a/)}` never matches, exactly as `/x\Aa\z/` (table (B): both no match on `xa` and `a`;
`/${anchored(/a/)}b/` and `/\Aa\zb/` both no match on `ab`). O64 CLOSED, rev 13's proposed error removed, the worked
row kept (§8, §11, L68). A general "can never match" warning is §13 **O66**, a possible later item with its trigger
(an unmatchable program shipped unnoticed, or the emptiness test built anyway for the empty-intersection error, L67).

(C) THE WARNING (RULED, CF:1098-1111: one warning in every whole-match place, keyed off the ROLE after macros are
expanded, never a name). Renamed **`anchor.whole`** (LEAN; it no longer fires only in an operand). Where it fires,
each row oracled in `predspec14_anchor.out` table (C) (fires: the pattern with and without its edge anchor agree;
does not fire: they differ):

| place (after expansion) | fires | reason |
|---|---|---|
| a side of `&` (final, under `anchored`, in a hole, nested, rx-text `&`) | yes | the side matches its stretch whole |
| a `label:` condition | yes | matches the label's text whole |
| a parameter the body puts beside `&` or after `label:` (user macro `value_of`; `quoted`, `left`/`right`/`mid`) | yes | it is that role, by the body |
| a compile-time set (warning-name set, import/export names, `enumerate`, `@assert`) | yes | matched whole on each string (LEAN that all compile-time sets count) |
| a parameter the body splices into a hole (`padded`, `contains`, `occurrences`, `startsWith`, `endsWith`; user `my_padded`) | no | the anchor reads the body's stretch at a point that need not be its edge, so it means something (`contains(/^err/)` = starts with; `padded(/^5/)` forbids the zeros) |
| `anchored(...)` | no | no anchor written by the author; pinning is the macro's purpose |
| a final pattern's own anchors | no | searched; the subject's ends, plain PCRE |
| a hole in a final pattern | no | plain PCRE (unmatchable programs: O66) |
| the argument of `any_case`, `length`, `month_numbered`, `json.quoted` | yes (LEAN) | matched whole on the reading; no body exists (O67) |

`padded` (RULED, CF:1113-1124): `padded(rx) := /0*(?:${rx})/` (the group: the manager's call, R-3; without it
`/0*1|2/` rejects `02`, R-2 table). Its parameter is in a HOLE, so `padded(/^5/)` accepts only `5` and draws NO
warning. §2.7's "a modifier's argument is itself a FILTER" is withdrawn; §2.7 now carries BODIES OF THE PROVIDED
TRANSFORMS (transform, body, where the parameter lands). The bodies checked: `padded`, `anchored`, `startsWith`,
`endsWith`, `occurrences`, `contains` (hole); `quoted`, `left`/`right`/`mid` (beside `&` inside a hole: filter role;
LEAN bodies); NOT EXPRESSIBLE: `unpadded` (CUT, below), `any_case`, `length`, `month_numbered`, `json.quoted` (each
tests its argument against text the subject does not contain). Against rev 13's reading, the ruled body moves only
`padded(/^5/)`; `padded("5")`, `padded(between(1, 12))`, `padded(between(0, 255))`, `padded(/0/)` accept the same
strings on the sample (R-2 table). An all-zeros value needs no clause (`000` is `00` then the hole's `0`).

`unpadded` (RULED CUT, CF:1125-1136, R-4): removed from §2.7, §8, the naming lists, §1's list and every example;
listed in §9 with the reason; `compare.width` keeps its warning and now suggests split fields. The time range is
`hm & (h: padded(between(9, 10))) & when((h: padded(==10)), (m: "00"))` with `hm := /(?<h>\d{1,2}):(?<m>\d\d)/`:
`9:00`, `09:30`, `10:00` accept, `10:01`, `8:59` reject (also `9:59` accept, `10:59`, `11:00` reject), the same
answers as the cut form on all eight (R-4 table). The natural-order range is §13 **O68**, later, trigger "a real
example where splitting fields is too clumsy".

Tuple compare (owner IDEA, CF:1139-1148, R-5): §13 **O69**, preferred over O68, a sketch, not in the library. For a
FIXED field count it is a plain macro with nothing missing: `tuple_between2(a, sep, b, lo1, lo2, hi1, hi2) :=
/(?<t1>${a})${sep}(?<t2>${b})/ & [(t1: padded(>lo1)), (t1: padded(==lo1), t2: padded(>=lo2))] & [(t1:
padded(<hi1)), (t1: padded(==hi1), t2: padded(<=hi2))]`; three fields add one entry per bound. The time range with
it gives the split-fields answers on all eight subjects (R-5 table). A variable count needs a structural macro with
a running prefix over array positions (bounded recursion or a primitive); `each` cannot. Caveats (not new): the
labels `t1`/`t2` are visible (the `hit` per-call naming question, O55); a parameter as a comparison atom is read as
a binding (LEAN).

ROWS WHOSE CLASS OR ANSWER MOVED: **L7** BY DESIGN -> WARNING; **L15** BY DESIGN -> WARNING; **L13** ANSWER MOVES
(`padded(/^5/)` accepts only `5`; class stays BY DESIGN, no warning). Diagnostic renamed only: L11, L41, L69, L70,
L71. Reworded only: L66, L68. §12: E-CTX-5's equivalence moves (no error, no warning); E-CTX-1 and E-CTX-7 now draw
`anchor.whole` (answers and no-error verdicts unchanged).

(F) Changelog entry rev 14; §0 rulings table for CF:1083-1136; §11 STATUS; §15 provenance row; §13 O64, O65
CLOSED, O66-O69 NEW; DECIDED (30)-(35).

## QUESTIONS FOR THE OWNER

- **primitive-transforms.** Four library transforms read text that is not in the subject, so no macro body can say
  what they do: `any_case("host")` must accept `HOST`, but the text it tests is `host`, which is not in the subject;
  likewise `length` (the length as a number), `month_numbered` (`Feb` read as `2`) and `json.quoted` (escapes
  decoded). Today their argument is matched whole by a sentence about "modifiers", which is the kind of name-keyed
  rule you ruled out for `padded`. Lean: ONE primitive underneath ("match S whole on a reading of the text"), with S
  counted as a whole-match place like a `label:` condition; each of the four becomes a plain macro over it, and the
  rules talk only about roles. Example: `x & any_case(/^host/)` would then warn, for the same reason
  `(x: /^host/)` does.
- **tuple-compare.** Your array-compare idea works as a plain macro today for a fixed number of fields (2 or 3),
  with nothing new in the language: `t & tuple_between2(/\d{1,2}/, ":", /\d\d/, 9, 0, 10, 0)` is "9:00 to 10:00"
  and gives the right answers on every time tried. Should it go into the first library? Lean: yes, as fixed-size
  macros (no new mechanism; it covers the time range `unpadded` was for, and versions like 1.4 to 1.10); a version
  for any number of fields waits, since it would need a looping macro or a primitive.

## CONSISTENCY SWEEP

Every §0.1 row and §12 case re-applied under the rev 14 rulings (the words; `anchored` a plain macro; one warning
by role; `padded`'s body; `unpadded` cut). Method: each row naming an anchor in a filter role, `padded`,
`anchored`, `unpadded` or the warning was read against the new text; witnesses where answers could move were run
in `predspec14_anchor.out`.

| item | rev 13 | rev 14 | why |
|---|---|---|---|
| L7 | BY DESIGN | WARNING (`anchor.whole`) | anchor in a `label:` condition; every filter role RULED |
| L11 | WARNING (`anchor.operand`) | WARNING (`anchor.whole`) | renamed |
| L13 | BY DESIGN, `padded(/^5/)` = `padded("5")` | BY DESIGN, `padded(/^5/)` accepts only `5`, no warning | ruled body puts the argument in a hole |
| L15 | BY DESIGN | WARNING (`anchor.whole`) | warning-name set is a whole-match place |
| L17, L63 | SAME / BY DESIGN | unchanged | anchors in `contains`'s hole; no warning |
| L20 | GAP | unchanged | `padded(between(1, 12))` accepts the same strings under the body |
| L41 | WARNING (`anchor.operand`) | WARNING (`anchor.whole`) | renamed |
| L66 | BY DESIGN | unchanged, reworded | "the program pinned by `anchored(...)`" |
| L68 | SAME | unchanged, reworded | O64 closed, no hole error |
| L69, L70, L71 | SAME / WARNING / WARNING | unchanged, diagnostic renamed | |
| L8, L10 (edge-assertion error) | ERROR | unchanged | `padded(/\b5/)` stays this error (STATE AT HANDOFF) |
| every other row | | unchanged | no anchor in a filter role, no `padded`/`anchored`/`unpadded` |
| E-CTX-1, E-CTX-7 | no error, no warning | no error, `anchor.whole` | anchor in a `label:` condition |
| E-CTX-5 | no error; `padded(/^5/)` = `padded("5")` | no error, no warning; accepts only `5` | ruled body |
| E-WEEKDAY, E-CAL (`padded(between(...))`, `padded(<=dim)`) | | unchanged | same strings under the body |
| E-HTTP (`anchored(block)`) | | unchanged | final pattern; no warning |
| every other case | | unchanged | |
| §2.7 time-range example | `unpadded(5, between("09:00", "10:00"))` | split fields + `when` | `unpadded` CUT; same answers on 8 subjects |

Cross-references checked: no draft-voice "THE ONE ANCHORING RULE" left (history keeps it); no `anchor.operand`
outside history and rename notes; `unpadded` appears only as CUT; O64/O65 references read CLOSED; the §11 STRING
SETS list, the §0.3 "filter role" and "scoped match" rows and §7.1 name the same three roles.

Manager / this lane's choices (LEAN, listed in §13 DECIDED (30)-(35)): the name `anchor.whole`; every compile-time
set counts as a whole-match place; `padded`'s group (the manager's, R-3); `quoted` and `left`/`right`/`mid` bodies
with their argument beside `&` inside a hole (so `quoted(/^a/)` reads the quoted text's start, and warns); the
`padded(/\b5/)` error kept; the census itself.

Standing questions (docs/design/CLAUDE.md): measurement regime: not relevant (no measured quantity; the oracle is
an answer check). Independent control: the evidence script answers each row with two engines (libpcre2 and
Python `re`) that share no code with the draft's text; the expectations in the draft were written first and
compared. What moves on regeneration: nothing generated; the `.out` is reproducible by the command above.
