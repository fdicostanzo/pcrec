# Lane unsetdef: a default for an absent label (design only)

Lane unsetdef, 2026-11-16, opus. Branch `lane/unsetdef` (cut from main c69929e4a). Design only: no edit under
`src/`, `cli/`, `lib/`, `memfn/`, `tests/`, `predicates_draft.md`, `plan.md`, `COND-FAMILY.md`. Deliverables: the
revised `docs/design/joint_condition.md` (§4B new; owner rulings applied; §8 rewritten),
`docs/dev/lanes/unsetdef_check.py` / `.out`, this report. Spellings are placeholders (D193 add. 4). The owner's words
are quoted; every other conclusion is the lane's.

## STATE AT HANDOFF

COMPLETE. Rulings file `docs/dev/lanes/unsetdef_rulings.md` last read 10:49 (box clock); last entry applied: R-2
(10:43: a several-string default is a compile error for now; the `some(...)` idea weighed, NOT PROPOSED NOW, with
R-2's trigger). R-1 (10:40, the owner's question on what `m = x` means when x is an rx) answered in §4B.0 and §4B.6.
Evidence: `timeout 120 python3 -I docs/dev/lanes/unsetdef_check.py` (libpcre2-8 10.46, Python 3.14.4 `re`, both on
every case): `TOTAL cases 233720 differ 0 engine-disagreements 0` (`.out`, last line). SABOTAGE run once
(`UNSETDEF_SABOTAGE=1`, the slice built at m = 30 instead of the default 0): `TOTAL cases 233720 differ 168` (output
kept in scratch, `$PCREC_TMPDIR/scratch/unsetdef/sabotage.out`), so the check goes red. No owed runs. Box: light only
(seconds-long Python).

## THE DEFAULT IN ONE PAGE

    t2 := /(?<h>\d{1,2})(?::(?<m>\d\d))?/
    t2 & ((h, m = 0): padded(between((9, 30), (11, 0))))     # 10 IN, 11 IN, 9 out (table (DF))

- WHAT: an opt-in default, written by the author at a label LEFT of the colon (`(m = v: S)`, `((h, m = v): R)`,
  `(h: S, m = v: T)`). In a match where the label is UNSET, the condition reads the default's TEXT in its place; where
  the label is set, the default is never read. The base rule stays the owner's LEAN: without a default, a condition
  naming an unset label FAILS (`predicates_draft.md:1590-1592`, §4.2).
- THE VALUE: ONE string (a literal, a binding of one, a `$` value of an always-set label or a computed label). A
  several-string default is a COMPILE ERROR (RULED for now, R-2: "We can punt, as you say, and throw an error").
  Plain reading (R-1): `m = 0` is "as if the minutes text were `0`".
- UNDER THE HOOD: the rows over (h, m) on the branch where m is set, plus the SLICE of R at the default on the branch
  where m is unset: a finite union of products again, so the DEFAULT level for a constant set (§4.6 relation for a
  `$` default). The "m unset" guard is ESSENTIAL (without it, 99 of 11,110 subjects differ, `11:45` accepted) and is
  not a user form today except via `!(m: /[\s\S]*/)`, which rests on §4.2's LEAN half and open O28.
- ONE CONCEPT with head defaults: "in a list of names, `name = v` supplies the value when none is given"; what v may
  be follows from what fills the name (a parameter: any value; a label: one string).
- DIAGNOSTICS: `default.unused` (warning; label never unset, or the default outside the set); `label.unset`'s text
  names both fixes (a default; an alternative without the label).
- PROBLEMS: §5 problem 7 (the one WORSE) becomes SIMPLER; optional minutes and a version without a patch SIMPLER; a
  date without a day ("does not matter") SAME: no default reproduces it, the alternative stays. §12 has no optional
  field.

## THE DEFINITION

`joint_condition.md` §4B.0 (examples), §4B.1 (definition). Points:

- FORM: `= v` only on a name (or a path) left of `:` in a condition entry. Inside an entry `&`/`|` bind tighter than
  `=`, so `(m = 0 | 5: S)` is a two-string default: an error. Errors: on the right (`((h, m): R = 0)`), inside `$`.
- VALUE table (§4B.1): literal, one-string binding, `$` of an always-set set-once label or of a computed label:
  legal; `$` of a label that can be unset: ERROR (no chains of defaults, D77); `$` of a repeated label: the existing
  bare-`$` error (`predicates_draft.md:1632-1634`); several strings: ERROR (R-2), text "a default stands in for ONE
  missing text, and this set holds 60. Give one value (`m = 0`); or, if an absent m should not matter, add an
  alternative that leaves m out"; a tuple, condition or macro: ERROR.
- CASES (§4B.1 table): single label `(m = 0: <30)` = "an absent m passes" iff "0" is in the set (differs from no
  default on the 110 minutes-absent subjects of 11,110, table (D1)); never-unset label: `default.unused` warning
  (11,000 of 11,000 identical); looped label: per item, zero iterations of a reached loop are NOT unset (L56, L65:
  `predicates_draft.md:554`, `:563`), so the default is not read and the plain condition holds (table (DL), 585 lists,
  0 differ); a never-reached loop: the default is read (lane's reading, UNTESTED); computed label: unset when a label
  it reads is unset (lane's reading; §4.4 is silent), table (DC) 65 subjects, 0 differ; another alternative taken:
  as an optional skipped, table (DA) 11,110, 0 differ; several defaults: one branch per reachable combination (3 of
  4 for `t3`), table (DS) 4,206, 0 differ; `padded`: the default is compared AS WRITTEN through the same set (under
  `padded` `0` and `00` are zero; without it `00` is not canonical: `(m = 00: <30)` never admits, table (D1)).

## UNDER THE HOOD

§4B.2. Checked by building the unfold as a regex (rows over the present fields + slice rows on the absent-field
branch) and comparing with the independent expectation (fields split by Python string code, absent field = the
default's text, Python integer tuple order):

| table | population | differ |
|---|---|---|
| (DF) optional minutes, `between((9, 30), (11, 0))`, `m = 0` | 11,110 | 0; rows 3, slice rows 2 ({10}, {11}) |
| (DS) optional minutes and seconds, `m = 0, s = 0`, `>= (9, 0, 30)` | 4,206 | 0; branches 3, rows 3/2/1 |
| (DV) `semver2`, `patch = 0`, three ranges | 728 each | 0 |
| (DL) looped items with optional minutes | 585 lists | 0 |
| (DA) other alternative taken | 11,110 | 0 |
| (DC) computed label `mnum = 1` | 65 | 0 |

THE GUARD: the hand unfold without "m unset", `((h, m): R) | (h: 10 | 11)`, differs from the default on 99 of 11,110
(table (DG), e.g. `11:45` accepted); on versions `between((1, 4, 0), (1, 9, 9))` on 3 of 728. When the default is the
field's minimum and R is closed upward (`>=`, `>`) the unguarded form is exact (table (DV): 0 of 728 for both `>=`
bounds): the lane's derivation, checked.

## ONE CONCEPT WITH MACRO-HEAD DEFAULTS

§4B.3. The rule: **in a list of names, `name = v` supplies the value when none is given.** A head names parameters a
call fills (`occurrences(x, min = 0) :=`, `predicates_draft.md:1936-1938`, §5.2; §5.4's `=` row, `:2017`); the left of
a colon names labels a match fills. What v may be follows from what fills the name: a parameter takes any value, a
label one string. The `=` census after the addition (§4B.3 table): array entry (names a LABEL, value given), call
argument (names a PARAMETER, value given), head (PARAMETER, fallback), condition left (LABEL, fallback: NEW), a
value-position record `(x = 1, y = 2)` (ERROR, L43 unchanged). One meaning ("this name, with this value"); the lists
that DECLARE or NAME what something else fills take a fallback, the lists that SUPPLY take the value. No position
changes meaning; one is added. This is the owner's 10:35 idea ("we could use it as for default macro arguments") in
his 10:37 spelling ("Seeing = in examples I prefer it").

## LOOK-ALIKES AND ERRORS

§4B.4, over the `t2` population (11,110 subjects), R = `padded(between((9, 30), (11, 0)))`:

| vs `t2 & ((h, m = 0): R)` | answer | diagnostic |
|---|---|---|
| `t2 & ((h, m: 0): R)` | compile error | NEW text: "a reference list holds label names; a default is `m = 0`" |
| `t2 & (h, m: 0)` | compile error | existing (entry without `:`) |
| `t2 & (h, m = 0): R` | compile error | existing (`:` outside a record) |
| `t2 & (h: 10, m = 0)` | compile error | NEW text: "the entry `m = 0` has no set; a default is written left of `:`" |
| `t2 & [m = 0]` | LEGAL, DIFFERENT: admits only `0`; 244 of 11,110 differ (table (DK)) | lane's proposed warning `label.twice` (two operands of one `&` define m) |
| `((h, f(m = 0)): R)` / `office_hours(m = 0)` | compile error | existing (a left is never an expression; no parameter m) |
| hand unfold without guard | LEGAL, DIFFERENT: 99 | none possible; `label.unset` names the default |
| no default | LEGAL, DIFFERENT: 2 (`10`, `11`) | `label.unset`, both fixes |
| "does not matter" `\| (h: 10)` | LEGAL, DIFFERENT: 1 (`11`) | none: a different meaning on purpose |

THE TWO MEANINGS OF A MISSING FIELD: "means a value" (the default) vs "does not matter" (the alternative). The default
cannot replace the alternative: on a date without a day (2024-MM against 2024-02-15..2024-04-01) "does not matter"
admits `02`, `03`, `04`, and every default day 1..31 misses one (best: 1 of 12 months differ, table (DD)).

THE WARNING `label.unset`, extended text: "m can be unset in a match of t2 (the optional group `(?::(?<m>\d\d))?`);
the condition `((h, m): ...)` then FAILS. To read an absent m as a value, write `((h, m = 0): ...)`; to accept
whatever m would be, add an alternative without m: `... | (h: S)`."

## PROBLEMS TRIED

§4B.5:

| problem | verdict | evidence |
|---|---|---|
| §5 problem 7, optional seconds (the one WORSE) | SIMPLER: `((h, m, s = 0): padded(>= (9, 0, 30)))`; §5's two-alternative form is exact only with minutes required, and with minutes optional differs on 2 (`10`, `11`) | (DS) |
| optional minutes | SIMPLER | (DF), (DG), (DN) |
| a version without a patch, `1.4` as `1.4.0` | SIMPLER (for `between` the hand form without a guard is wrong on 3 of 728) | (DV) |
| a date without a day ("does not matter") | SAME: not the default's job; the pattern is split by hand as today | (DD) |
| §12 with an optional field | none: the one `)?` in §12's programs is E-DEPTH's JSON array body, no label (`predicates_draft.md:3545`; `sed -n '3214,3600p' docs/design/predicates_draft.md \| grep -c ')?'` = 2, the other prose) | — |

Tally: simpler 3, same 1, worse 0; §5's tally becomes simpler 7, same 6, worse 0.

## THE MANAGER'S SKETCH, TESTED

| sketch | verdict | reason |
|---|---|---|
| (s1) the default sits at the label left of the colon, not in the pattern, not on the set | HOLDS | a regex cannot capture absent text; a set is context-free (§11) and does not know presence; the left of the colon is where a label is named (colon-scope) |
| (s2) it unfolds to `((h, m): R) \| (m unset & (h: slice of R at m = 0))`; the slice of a constant tuple set at a constant is regular; default level | HOLDS, INCOMPLETE | 0 differ over (DF), (DS), (DV), (DL), (DA), (DC). Missing: the guard is ESSENTIAL (99 differ without it, (DG)) and not a user form today except through O28's open half; "at m = 0" means the TEXT `0`, compared as written (canonical rule); several defaults give one branch per reachable combination; a `$` default makes it a §4.6 relation; zero iterations are not unset |
| (s3) `10` in, `9` out, `11` in for 9:30..11:00 | HOLDS | (DF): `10` IN, `11` IN, `9` out, `09` out |
| (s4) one label is the one-field case | HOLDS | `(m = 0: <30)`; it reduces to a compile-time "absent passes / fails" choice (the second draws `default.unused`), table (D1) |
| (s5) no separate value-level "or else" | HOLDS (for the cases tried) | every fallback in the problems sits at a condition's label; a computed label reading an unset label is itself unset and takes ITS default (DC). Trigger for a value-level form: a computed label that must read one absent input while the others are present; no example (D77) |
| R-1 manager's answer: one-string default; several strings an error unless EVERY or SOME is chosen; EVERY reproduces rev 18 | HOLDS, INCOMPLETE | EVERY reproduces table (W) on the owner's example (0 of 110 differ) but NOT in general: `between((9, 0), (10, 0))` differs on 2 (`9`, `09`), as does `between((9, 0), (11, 59))`: where a bound's later field is the field's floor, EVERY admits and decided-prefix rejects (table (DE)). Added: EVERY's hand spelling needs no guard (0 differ on 5 ranges), SOME's does (40 to 159 differ); SOME over every day IS the date's "does not matter" |

## WHAT CHANGED IN THE NOTE

Listed in full in `joint_condition.md` §4A.10 ("Lane unsetdef" block), each marked "[§4A.10, unsetdef]" in place:
header sentence; first/rest pointers marked PARKED (Goals, §2, §4A.7, §7 item 10); §2 MEANING PER MATCH (the owner's
lean, the default); §2 N2 and §3 "Counted" (settled); §3 "unset fields" row; §4 item 3 (set-arity RULED); §4 item 6
(the 10:35 lean quoted, §4B the middle ground); §4A.2, §4A.4 (set-arity RULED; producer (4) the design); §4A.3 (no
user for tuple-parts); §4A.9; §4A.11 (PARKED, 10:18 and 10:22 quoted, trigger); §4B NEW; §5 problem 7 and tally; §6
B2; §7 item 8; §8 REWRITTEN (answered list with his words; eight open questions). Tuple-anywhere was already applied
by tupleval2.

## CONSEQUENCES DERIVED BY THE LANE

1. The default's strongest case is the guard: its hand spelling is either wrong (no guard: 99 of 11,110 differ) or
   rests on O28's open half (`!(m: anything)`); the default needs neither.
2. A several-string default has two regular readings (EVERY, SOME); EVERY's hand form needs no guard, so "does not
   matter, strictly" is already writable as `| (h: S)`; SOME's needs the guard. The R-2 error is therefore safe for
   EVERY and leaves SOME to a pattern split.
3. EVERY is rev 18's decided-prefix order on the owner's example but not in general (table (DE)).
4. A default on a label inside a `*` loop is never read on zero iterations (L56): an author who expects "no items =
   the default item" gets "holds". No warning proposed (no case).
5. `t2 & [m = 0]` is a legal, different program (an array entry NAMES a label); a `label.twice` warning (two operands
   of one `&` define one label) would catch it; proposed, no case.
6. The owner's `some(between(...))` idea: same word as the group question `some(...)` with a new argument kind (a
   set), a new domain (a set's members) and a new position; it reopens L54's withdrawal of `some(s)` on a set
   (`predicates_draft.md:552`). NOT PROPOSED NOW; trigger (R-2's): a problem where a missing field means "any of
   these" or "does not matter" and the pattern cannot be split by hand.
7. The single-label default is a compile-time choice between "an absent label passes" and "fails"; no new runtime
   concept.

## QUESTIONS FOR THE OWNER

Ranked; each with its example, forces and leaning. Reply either way.

1. **unset-component** (to close). Close it as "a condition naming an unset label FAILS, unless the author gives
   the label a default"? Example: `t2 & ((h, m = 0): padded(between((9, 30), (11, 0))))`: `10` and `11` in, `9` out;
   without `= 0`, all three out. Forces: one rule lifted from §4.2; "means a value" is the opt-in default, "does not
   matter" the explicit alternative; an author who writes neither gets FAIL, and the `label.unset` warning names both
   fixes. Leaning: close it so. Reply either way.
2. **default-unused**. A default that can never change an answer (the label is never unset, or the default lies
   outside the set, e.g. `(m = 45: <30)`) is a WARNING, as `dead.branch` is, not an error? Example: `t & ((h, m = 0):
   R)` with minutes required: 11,000 of 11,000 answers unchanged. Forces: an error would refuse one library condition
   laid over patterns where the field is sometimes required; a warning is one line the author can silence. Leaning:
   warning. Reply either way.

The rest of the open list (joint-loops, two-orders, modifier-lift, colon-scope, record-is-product, tuple-parts) is in
`joint_condition.md` §8, each with its leaning; nothing new for them from this lane beyond noting that two-orders is
LIVE while first/rest is parked and that tuple-parts has no user.
