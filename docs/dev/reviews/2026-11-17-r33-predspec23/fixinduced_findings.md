# CRITIC fixinduced: predspec23

## Findings

### FIXINDUCED-1  `default.unused` (b) now fires on defaults that DO change answers (condition-not breaks its premise)  CONFIRMED  severity: design (a warning promised on the wrong set)
§7.1 (rev23:3447-3450) keeps `default.unused` (b): "a label's default that can never change an answer: ... (b) the
default's text is outside every set it meets". That premise (record 11:05, asked as "a default that can never change an
answer, the label never unset OR THE DEFAULT OUTSIDE THE SET") held only while UNKNOWN and FALSE dropped the same rows
(§R.1.5 MODEL-7: "observable only through NOT"). With condition-not (23:48) a default outside its set turns UNKNOWN
into FALSE, and NOT turns that into TRUE: the row is KEPT. Rev 23's own §R.3 table (rev23:562-564) shows it:
`NOT (h = 9: <5)` on `x` HOLDS / HOLDS where `NOT (h: <5)` FAILS / FAILS; 9 is outside `<5`, so (b) fires on the very
column the definition block uses as its worked default.
Repro (probe/p2.py, imports predspec23_model read-only): SV pool (341): `NOT (h: <5)` vs `NOT (h = 9: <5)` differ
WHOLE 1 (`x`) / SEARCHED 164; REP pool (364): `NOT (h: <5)` vs `NOT (h = "x": <5)` differ 18 / 232 (first `''`);
`occurs.none(NOT (h: <5))` vs `occurs.none(NOT (h = "x": <5))` differ WHOLE 17 (first `;`). The NOT spelling of
§R.1.7's NARROWER question, `occurs.none(NOT (h = "x": <5))`, equals the sentinel form `occurs.none((h = "x": !<5))`
(0 differ both modes) yet draws (b), while the `!S` spelling does not. Chain: `label.unset`'s named fix "`h = v`"
(rev23:3440) applied to `NOT (h: S)` by an author who wants absent rows kept needs v outside S, which (b) then
flags as unused. (b) is still right for un-negated tests and inside two-valued group questions
(`some((h = "x": <5))` vs `some((h: <5))` 0 differ). Expected: (b) restated as "outside every set it meets AND
under no NOT" (or polarity-aware), with the 11:05 premise noted as narrowed by 23:48. Effort: small text. Blast
radius: §7.1, §R.1.6's "warning only on a default that can never be USED" (stays right; (b) no longer matches it),
§13 warning-family PLAN row.

### FIXINDUCED-2  §2.1's typing rule still makes a condition a MACRO with pointwise `!M` = "neither", which gives `!c` the pattern-difference meaning condition-not rejects  CONFIRMED (text)  severity: design (two definitions of `!` on a condition in normative text)
§2.1 RULE (rev23:1795-1797) still says "There is no third value kind: a CONDITION is a macro", and TYPING OF
`& | !` (rev23:1824-1826): "operators on macros are POINTWISE (`M & N`, `M | N`, `!M` filter as both, either,
neither; rev 22: `!M` only where M is not a CONDITION, **not-is-complement**, §2.2)"; §2.2 (rev23:1897) "Macros in
the filter role combine pointwise by `& | !`"; §4.1 (rev23:~2629) "A condition is a MACRO (§2.1)". §R.9 S056 marks the
kind table "STANDS with §R.1.11's `!` row", and §R.1.11 says a condition is "no longer 'a macro (CF:858)'". With the
rev 22 qualifier lifted by condition-not, the pointwise "neither" reading of `!(h: <5)` keeps every row the
condition does not keep, absent rows included: that is §R.3's THIRD column (difference), not Kleene NOT. On `x`
(`/(?<h>\d)?x/`, h absent): pointwise `!` HOLDS / HOLDS, condition-not FAILS / FAILS (§R.3 table row `x`; PART 2).
The SV pool parts on 1 WHOLE / 164 SEARCHED texts (§R.3 counts). §R's precedence clause decides it, but the body
was declared complete ("every live sentence ... rewritten", rev23:373-376) and S056 says STANDS. Expected: §2.1/§4.1
rewritten to three kinds (or the condition carved out of "pointwise `!M`"), S056 REWRITTEN. Effort: small. Blast:
§2.1, §2.2 line 1897, §4.1, §5.4's macro rows, and any macro body whose parameter can receive either a condition or a
pattern (`m(f) := x & !f` now means NOT for `m((h: <5))` and difference for `m(x & (h: <5))`; rev 22 made the first
an error, so one body had one meaning).

### FIXINDUCED-3  The kept "label no match can set" error (r31 H) dropped rev 22's "the program's regex (its `&` operands)" qualifier  CONFIRMED (text + run)  severity: answer (a constant test passes silently, the hazard H was kept for)
Rev 22 (rev22:2301-2307): "Where no match of the PROGRAM'S REGEX (ITS `&` OPERANDS, conditions not applied) sets a
label ... a COMPILE ERROR". Rev 23 restates it as "a condition or a default on a label NO MATCH OF ITS REGEX CAN SET"
(§R.5 H rev23:727; §4.1 rev23:2611; §4.2 rev23:2672), reason "the per-label regex value set is empty"; §R.2
(rev23:544) "read from the values the label's own regex can give"; R.1.8 makes "its regex" the DEFINING OPERAND. A
label its own operand can set but no match of the `&` of operands can is no longer covered. Repro (probe/p3.py):
`/(?<o>\d)x|y/ & /y/ & (o = "1": <5)`: o is set by the operand, by no match of the program; the default makes the
test constant TRUE: vs the program without it, differ 0 of 341 WHOLE and 0 SEARCHED (holds 1 / 220), exactly H's
"would hold on every subject silently". `(o: <5)` drops every row (0 of 341), `NOT (o = "9": <5)` also constant.
Rev 22 errored on the default/mark here; rev 23's words do not. Expected: keep "the program's regex (its `&`
operands, conditions not applied)" (patterns joined by `&` are statements, not WHEREs, so R.1.8's "a WHERE never
changes columns" does not cover them), or state the narrowing as a choice. Effort: one clause. Blast: §R.5 H, §4.1,
§4.2, §R.2, §0.3 DOM row (rev23:1723).

### FIXINDUCED-4  `x & when(c, p)` and its stated expansion `(x & c & p) | (x & !q)` report different rows SEARCHED once `|` is PCRE's one parse (r31 B)  CONFIRMED  severity: answer (searched report; holds-counts unaffected)
§8 (rev23:3572-3584) keeps "`x & when(c, p)` = `(x & c & p) | (x & !q)`" and §R.5 A3 cites agreement in COUNTS only.
r31 B's fix (§R.1.4 rev23:436-438) makes `|` "PCRE's ONE parse ... the labels of the branch it took". PCRE's
alternation is BRANCH-MAJOR (branch 1 at each of its ends, then branch 2); `x & when(...)` is END-MAJOR (D196: the
left operand x picks ends, the filter only accepts). The evidence engine (predspec23b P2 `alt`) implements end-major
for the expansion too ("branch 1 first, the next branch when its filters reject", per stretch), a reading R.1.4 does
not state (§R.8/§R.11 list no reading for `|` over FILTERED branches; only "`|` on conditions = Kleene OR").
Repro (probe/p1.py, imports predspec23b_model read-only; KH pool 1,110, p = `(k: between(3, 7))`): reported row
end-major vs branch-major differ on 125 texts for c = `(h: <5)` (first `3;0;5`) and 400 for c = `(h = 0: <5)` (first
`3;5`); `5;1;9`: `x & when` reports `5;1;9`@0, the expansion `5;1`@0; `5;9` with the default: `5;9`@0 vs `5`@0. Find-all
and labels read downstream move with it. Expected: R.1.4 states what a filtered branch does under one parse (fall
through at the same stretch? branch-major ends?), and §8's "=" is qualified to WHOLE / holds-only, or the expansion
is not offered as the definition. Effort: one clause + a run. Blast: §8, §R.5 A3, §R.1.4/§R.1.9, any library body
written as a `|` of filtered branches.

### FIXINDUCED-5  §5.2's empty-intersection error now rejects a non-constant program (`NOT (n: <0)`), the r31 C(iii) objection reopened by condition-not  CONFIRMED  severity: doc (low; a spelling exists)
§R.2 (rev23:543-544) keeps "`(n: <0)` on a digit label is still the error", reason "from pure parts" (§5.2 rev23:3090).
r31 C(iii)/SIMULATE-6 objected that the error rejects a meaningful program once a construct makes the empty test
non-constant; `all` retired, but condition-not is a second such construct: `NOT (n: <0)` on a looped n is "some
pass sets n". Repro (probe/p3.py, `/(?:(?<n>\d),)*/`, 121 texts over {3,7,comma} to length 4): holds WHOLE 6 /
SEARCHED 64, `''` FAILS / FAILS, `3,` HOLDS / HOLDS; 0 differ from `some((n: any text))`. Expected: the error's
statement names the NOT case (still an error, hint "for presence write `some(...)`"), or the text says why it stays.
Effort: one sentence. Blast: §5.2, §R.2.

## PROBED-AND-HELD

- r31 dispositions vs rev 23 text: A2/A4/A5 (R.1.2, R.1.4, R.5 A), C (R.1.7), D (R.1.8), E (R.1.6, R.5 E: (e2.1)/L101
  reversed, label-twice hint scoped, the match-context gloss not quoted), F (one block, R.11, condition-not ruled),
  G (R.5 G), I (R.6), J (R.1.2 keeps O35 an error), K (R.1.1 vocabulary, legend): each present as ruled. H present
  but narrowed (FIXINDUCED-3).
- `NOT some(c)` = `occurs.none(c)` with a non-conforming default: `NOT some((h = "x": <5))` vs `NOT some((h: <5))`
  20 / 20 WHOLE, 364 / 364 SEARCHED over REP (364): holds (group-truth reading).
- `occurs.none(NOT (h = "x": <5))` vs §R.1.7's sentinel `occurs.none((h = "x": !<5))`: 0 differ WHOLE and SEARCHED
  (REP 364). `occurs.none(NOT ((h, m): R))` = I2a (committed PART 4, 85 holds, I2a differ 0) as R.7 row 2 says.
- `when` body vs the NOT-c body: 10 / 110 differ for `(h: <5)`, 0 / 0 for `(h = 0: <5)` (committed PART 5) as
  §R.7b b4 and §8 state; body counts 960 / 1,110 and 955 / 1,045 match the out file.
- §R.3 on a set-once label with defaults: `NOT (h = v: S)` and `(h = v: !S)` agree (definitional: a default makes
  h present); H's error under NOT stays constant (`NOT (o = "9": <5)` constant, probe/p3.py), so H still applies.
- `label.unset` under NOT: an absent h under `NOT (h: S)` is still dropped, so the warning's subject is unchanged;
  its "does not fire on zero passes inside a group question" clause holds for `occurs.none(NOT c)` (zero passes are
  no pass).
- Kleene De Morgan over a record under NOT (`NOT (a: S, b: T)` = `NOT (a: S) | NOT (b: T)`): identity, no answer moves.
Probes: probe/p1.py, p2.py, p3.py (read-only imports of the evidence engines).

CRITIC COMPLETE

