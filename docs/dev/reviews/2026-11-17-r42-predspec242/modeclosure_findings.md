# CRITIC modeclosure — round predspec242 (rev 24.2 of predicates_draft.md)

## Findings

### MODECLOSURE-1 — an EMPTY final pass: libpcre2 runs it, the engine drops it; the rule never says whether it is "the last pass" (CONFIRMED)
- Severity: answer (WHOLE, SEARCHED, FIND-ALL) + design (a rule gap). Effort: small (one sentence + engine fix + a nullable case in PART C2). Blast radius: every loop whose body can match empty (a literal loop, a hole loop `/(?:${item})*/` with a nullable item); `occurrences` disagrees with the other two loop kinds inside the engine.
- Draft: R.1.7 (2)/(3) (lines 702-707: "the value the LAST pass itself set ... a group that took no part in a pass is unset in it"); R.1.4 / §R.6 row "FIND-ALL after an empty match" (line 991: "the language follows PCRE2").
- libpcre2 10.46 FACT (my run, `work/selftest.py`): `/(?:(?<p>)(?<h>\d)?)*(?C)/` WHOLE on `3`: at the callout p = (1,1), h = (0,1): PCRE2 RUNS a final EMPTY iteration and keeps it; `/(?:a|(?<e>))*/` on `a` sets e = `` (the empty pass's own group).
- The engine's literal loop (pathimpact `Rx._rep`, line 154: "an empty pass past the minimum ends the loop" = `continue`, the pass is DISCARDED) and the hole loop (predspec241 `Rep.walk` line 148, commented "(PCRE)") drop it; `OccS` (line 184) KEEPS an empty hit as a pass. Three loop kinds, two behaviours, neither stated.
- REPRO (`work/drillA.py`, my model U = structural unrolling, below): `/(?:(?<h>\d)?)*/ & NOT (h: <5)`: engine vs libpcre2 WHOLE 30 / SEARCHED 80 / FIND-ALL 116 of 121 (alphabet `37;`, len <= 4); first `3`: engine FAILS, libpcre2 HOLDS with h absent (the empty last pass set no h). `/(?:(?<h>\d)|;?)*/ & NOT (h: <5)`: 80 / 80 / 80 of 121. The positive `(h: <5)` agrees (backtracking leaves the empty pass), so only NOT, the complement and the REPORTED label move: under the PCRE-faithful reading the plain program `/(?:(?<h>\d)?)*/` on `3` reports h ABSENT on its first path, and BOTH `(h: <5)` and `NOT (h: <5)` hold on `3`.
- ADDENDUM (`work/drillO.py`): the HOLE loop drops it too and the `occurrences` loop keeps it, each against model U, 121 texts (`ab `, len <= 4): `/(?:${x})*/ & NOT (g: "a")`, x := `/(?<g>a)?b?/`, 15 / 40 / 66 differ (first `a`: engine WHOLE FAILS, libpcre2 HOLDS with g absent); `occurrences(/(?<g>a)?b?/) & NOT (g: "a")` 0 / 0 / 0. So the same nullable item answers differently as a hole loop and as an `occurrences` argument inside the engine.
- Expected: the draft states whether a final empty iteration is a pass (regex default by exception-rule: it is, PCRE2 runs it), and the engine's three loops agree with that. If the owner's "expected understanding" (most would expect h = `3` here) wins instead, that is an EXCEPTION to regex behaviour and belongs in §R.6's LOOKS LIKE REGEX table, asked with a slug. None of the evidence pools has a nullable loop body (REP, CLOSE, KH, NEST all end in a mandatory character), so no count in §R covers this.

### MODECLOSURE-2 — the PASS FORMS over a label two loops deep: no rule says WHOSE passes; the literal and the hole spelling of the SAME pattern answer differently (CONFIRMED)
- Severity: answer + design (an unstated rule under the outermost view). Effort: one ruling-shaped sentence (asked, slug) + the engine following it. Blast radius: `some`, `occurs.*`, `h[k]`, `$h[k]` (§R.6 PASS TABLE row, line 970; **some-own**, line 1105; §R.4 W1b/W1d/W4*, W6, W7) on any label with two enclosing loops, in every mode and every place that can hold such a pattern.
- Draft: R.1.7 (4) (lines 707-711) rules the OUTERMOST view for a BARE condition only; NESTED LOOPS (line 760) "the literal loop equals its spelling through holes (0 of 1,365)" is measured for the bare condition only; **some-own** asks only "each pass's own" for a single loop.
- REPRO (`work/drillN.py`, engine of rev 24.2), NEST := `/(?:(?:(?<h>\d)?;)*,)*/` vs its hole spelling `/(?:${inner},)*/`, inner := `/(?:(?<h>\d)?;)*/` (PART N's own pair), alphabet `37;,`, length <= 5, 1,365 texts, labels compared:
  `& some((h: <5))` 6 / 11 / 11 (first `3;7;,`: literal HOLDS h = `7`, holes FAILS); `& occurs.none(NOT (h: <5))` 13 / 353 / 973 (first `,`: literal HOLDS, holes FAILS); `& (h[2]: <5)` 7 / 17 / 17 (first `7;3;,`: literal HOLDS, it reads the SECOND INNER pass; holes FAILS, it reads the second OUTER pass, which does not exist).
- Cause in the engine: a literal pattern's pass table is keyed on the INNERMOST enclosing loop (lastpass `rx_of`, "innermost enclosing LOOP") and flattens every inner pass of every outer pass into one list; a hole loop's pass table is the OUTER loop's passes, each reading the item's outermost view. The draft says neither.
- Expected: the draft states whose passes a pass form ranges over for a nested label (the outermost loop's passes at the outermost view, as nested-pass's principle suggests, or every innermost pass flattened), as an owner question with a slug; and the hole rule's claim that the two spellings are one pattern is either kept (then the engine is wrong for one of them) or narrowed to bare conditions in the text.

### MODECLOSURE-3 — the helper-group "regex model" of the per-pass label is POSITIONAL, the rule is TEMPORAL: it is wrong for a label set by a lookaround inside a pass (CONFIRMED)
- Severity: doc + evidence (a stated regex model that is not one; no printed answer moves). Effort: small (narrow the sentence; add a lookaround case to PART C2, or swap in an order-based model). Blast radius: §R.6's "Its regex model is the helper-group callout model (PART C2: 16 of 16 equal)" (lines 999-1000), §R.10's description (lines 1185-1187), R.0 G24-3 (line 497) where it rests on C2; PART C2's check cannot fail on this class (none of its 16 cases has a group in a lookaround inside a loop).
- The construction: a label is "the pass's own" iff its capture STARTS at or after the latest pass-start helper `(?<ps>)`. The rule (R.1.7 (2)/(3)) is about WHEN the group was set (in the last pass), not WHERE its text lies.
- REPRO (`work/helper.py`, the construction re-implemented only to test it; `work/drillA.py` for my structural model U), alphabet `37a`, length <= 4, 121 texts, labels compared:
  LOOKBEHIND `/(?:\d|(?<=(?<h>\d))[a-z])*/ & (h: <5)` on `3a`: the last pass `a` SETS h = `3` (its lookbehind reads back): engine HOLDS h = `3`, model U HOLDS, the helper construction FAILS (h starts at 0, before the pass's helper at 1): 9 / 33 / 33 differ (NOT: 18 / 30 / 40).
  LOOKAHEAD `/(?:(?=.(?<h>\d))[a-z]|\d)*/ & (h: <5)` on `a3`: pass 1 (`a`) sets h = `3` from its lookahead, the last pass (`3`) sets none: engine and model U FAIL WHOLE; the helper construction HOLDS (h starts at 1 = the last pass's start): 9 / 33 / 33 (NOT: 18 / 26 / 36).
  Engine vs model U on both: 0 / 0 / 0 (and NOT 0), so the ENGINE follows the rule; the helper construction does not.
- Expected: §R.6/§R.10 say the helper-group model equals the rule for labels whose group lies inside its own pass's text (no lookaround reaching outside the pass), or the control is replaced by an order-based one (structural unrolling, model U below, is one: only the last pass's copy carries the named group, so PCRE2's own capture state is the last pass's own).
- Side note: on the nullable body of MODECLOSURE-1 the helper construction SIDES WITH libpcre2 against the engine (`NOT (h: <5)` 30 / 80 / 116 of 121), so the two controls this round has (helper, model U) agree there and the engine is the odd one out.

### MODECLOSURE-4 — a joint whose labels sit at DIFFERENT loop depths (or in sibling loops): the bare joint has an answer, `some(J)` / `occurs.none(NOT J)` are silently REJECTED by the engine and unstated by the draft (CONFIRMED in the engine; the draft gap is a reading)
- Severity: design (an unstated place; the §R.4 every-pass spelling stops working one depth down). Effort: one sentence + an owner-question row, or fold into MODECLOSURE-2's question. Blast radius: §R.4 W4b/W4d's spelling `X & some(J) & occurs.none(NOT J)` (line 895, 897) and **every-pass-spelling**, whenever the joint's labels are not all in ONE loop or set once.
- Draft: R.1.7 A JOINT (lines 764-767): "a bare joint reads the last pass's own tuple ... a per-pass joint is written on the item ... or with `some(J)` (some pass)"; W4d pairs a looped h with a SET-ONCE k only.
- REPRO (`work/drillY.py`, engine of rev 24.2), J := `((h, k): h > k)`:
  two depths, `/(?:(?<k>\d)(?:(?<h>\d);)*,)*/`: bare `& J` on `37;,` HOLDS h = `7`, k = `3` (pairs within the last OUTER pass); `& some(J)` REJECTED by the engine ("group question over ('h', 'k')"), in every mode.
  sibling loops, `/(?:(?<k>\d);)*(?:(?<h>\d),)*/`: bare `& J` on `3;7,` HOLDS (each label's own last pass: a tuple no single pass holds); `& some(J)` REJECTED.
- Expected: the draft says what "the last pass's own TUPLE" means when the labels' last passes are different loops' (the sibling case reads two last passes, which "pairs within the last pass", line 767, does not describe), and whether `some(J)` over labels at two depths ranges over inner passes paired with their outer pass's k (the natural reading of W4d one level down) or is an error; the engine's rejection is not a ruled compile error.

### MODECLOSURE-5 — R.1.1's EXPORTS sentence is not closed over the places: it omits `hits(r)` and the `&` operands, and no sentence says whether a `label:` set's own groups export (doc; SUSPECTED for the `label:` set)
- Severity: doc (the place table is deferred to item 22, but this revision states an EXPORTS list and it is the one a reader finds). Effort: one clause. Blast radius: R.1.1 (lines 568-569) and §R.6's black-box rows.
- Draft line 568-569: "which labels it EXPORTS (a loop, an `occurrences` argument and an atomic part: every label set inside, the last pass's own, at the outermost view, R.1.7)". Elsewhere the draft gives two more exporters: `hits(r)` (R.1.9, lines 803-805: the committed LAST hit's own g) and both `&` operands (R.1.4, line 617, "The row's labels are both sides'"); the complement exports none (line 1504, "the complement carries no labels"); a lookahead is asked (**lookahead-labels**). A `label:` set (`(x: /(?:(?<h>\d)?;)*/)`, a WHOLE place by R.1.1) is in none of them: whether its pattern's h is visible after it, and at which view, is unstated (the engine has no node for it, so nothing ran).
- HELD where it is stated (my runs, model U, labels compared): `hits(/(?:(?<h>\d)?;)+/) & (h: <5)` exports the last committed hit's own h at the outermost view, 0 / 0 / 0 of 341 against a libpcre2 global-search model; the right `&` operand's looped label read from outside: 0 differ for five operand kinds (MODECLOSURE PROBED-AND-HELD, (b)).
- Expected: the EXPORTS clause lists every place with its export (or "none"), and the `label:` set's row says exported / not / asked.

### MODECLOSURE-6 — FIND-ALL is defined twice and the two disagree on a LAZY loop under NOT: R.1.2 "an empty report stepping one character" vs §R.6 "the language follows PCRE2" (CONFIRMED)
- Severity: answer (FIND-ALL) + doc (two definitions of one mode). Effort: small (pick one in R.1.2; the engine/harness `findall` gains PCRE2's NOTEMPTY_ATSTART retry). Blast radius: every FIND-ALL whose first surviving path at a start is EMPTY while a later non-empty path at the same start also survives: a lazy loop under NOT or a default, the pass-own rule's absent labels making such empty paths common (zero passes = every label unset).
- Draft: R.1.2 (lines 574-576) DEFINES FIND-ALL as "the first surviving path at each start, again from the reported end, an empty report stepping one character, as the engine and the libpcre2 harness both do (review r40 C3: PCRE's own empty-match retry is not modelled; no answer here depends on it)"; §R.6 LOOKS LIKE REGEX row (line 991): "the language follows PCRE2 (regex, the default); the evidence's simplification decides no answer here".
- REPRO (`work/drillF.py`, model U run both ways): `/(?:(?<h>\d)?;)*?/ & NOT (h: <5)` (a lazy loop), FIND-ALL over 364 texts (`37;`, len <= 5): step-one vs PCRE2's own global loop (retry at the same offset with PCRE2_NOTEMPTY_ATSTART | PCRE2_ANCHORED, then advance) differ on 301 of 364; the ENGINE vs PCRE2's loop likewise 301. First `;`: step-one [``@0, ``@1]; PCRE2 [``@0, `;`@0, ``@1]. The greedy REP and the positive test: 0 of 364 each (so the draft's printed answers are not affected, as it says).
- Expected: R.1.2's definition is PCRE2's global loop (exception-rule's default), or the step is listed as an exception in §R.6 with its slug; "no answer here depends on it" is scoped to the printed programs, with the lazy-NOT witness beside it.

## PROBED-AND-HELD

Method. My control is MODEL U (`work/um.py`): STRUCTURAL UNROLLING, `B*` -> `(?:B'*B)?` with the label's group made
non-capturing in B', recursively for every enclosing loop (`{0,2}` -> `(?:B'?B)?`, `{2}` -> `B'B`, lazy -> `(?:B'*?B)??`,
possessive -> `(?>(?:B'*B)?)`), so PCRE2's own path-exact capture state IS the last pass's own label at the outermost
view; the test is a plain callout. It shares nothing with the engine's helper-group construction (no pass-start group,
no position comparison). For a condition read INSIDE a pass (item, inner view, occurrences argument) model U' places the
test callout where the pass's own label is decided (`(?:(?<h>\d)(?C"t")|(?C"no"));`), fresh per pass. Path-order caveat:
unrolling moves the pass-count choice before the body's own choices; every body used is effectively deterministic per
text. A first attempt with `(*MARK)` names was DISCARDED: libpcre2 10.46 gives a callout the last mark passed on ANY path,
not the current path's (`work/selftest2.py`: a failed second pass's mark is seen) — worth knowing for later models.
Engine = rev 24.2's definitions (predspec242b's patches P1-P6 on predspec241, cut before its PART A; P7 moot), `work/eng.py`;
it reproduces R13;; and the NESTED LOOPS WHOLE line exactly. Every count: every mode, labels compared unless said.

(a) CAPTURE-STATE DRILL
- Loop-ness edges and a single depth (`work/drillA.py`), engine vs model U, `(h: <5)` and `NOT (h: <5)`: `*`, `{0,1}`,
  `{1}`, `{0,2}`, `{2}`, lazy `*?`, possessive `*+`, `(?:B+)?` (the ? outside the loop), an optional group in the body,
  `{1}` inside `*`: 20 of 20 EQUAL (364 / 1,365 texts). R.1.7 (4)'s "upper bound 1 is not a loop" holds on `{0,1}`,
  `{1}` and `{1}`-inside-`*`.
- Two depths in a literal: plain, outer lazy, inner possessive, outer `{0,1}`, inner `{0,2}` with outer `+`, inner `{2}`:
  12 of 12 EQUAL (1,365). A label set by a LOOKBEHIND or a LOOKAHEAD inside a pass, an atomic body: 6 of 6 EQUAL (the
  engine is temporal; the helper construction is not, MODECLOSURE-3). A loop inside a lookahead inside a loop: 2 of 2.
- Nested places (`work/drillN.py`), 18 of 18 EQUAL: a literal loop inside a hole loop, a hole loop of a two-depth literal
  item, a hole loop inside a hole loop, `atomic(NEST)`, atomic inside a hole loop, an `occurrences` argument holding a
  loop, atomic inside `occurrences`, a hole loop inside `occurrences`, three loops (a two-depth literal inside
  `occurrences`) (1,365 texts each; 781 for the three-loop case).
- Inner views and per-pass conditions (`work/drillX1.py`, holds and stretch): view (i), view (ii), a condition inside an
  `occurrences` argument reading a two-depth label, each under `(h: <5)` and NOT: 6 of 6 EQUAL to model U'.
- Defaults on a last-pass-unset label (`work/drillY.py`): `NEST & (h = 0: <5)`, `NEST & NOT (h = 9: <5)`, the default
  over an `occurrences` export: 3 of 3 EQUAL. R.10's stated limit "a condition inside an atomic part inside a loop item":
  `/(?:${atomic(item & (h: <5))})*/` and `/(?:${atomic(INNER & (h: <5))},)*/`: 2 of 2 EQUAL to model U' (the limit did
  not bite here). `hits(/(?:(?<h>\d)?;)+/) & (h: <5)` (last committed hit's own, outermost view): EQUAL to a libpcre2
  global-search model (341).
- Printed answers re-derived on model U alone (`work/printed.py`): NESTED LOOPS WHOLE x4, SEARCHED `3;,`@0 h = `3`,
  FIND-ALL [`3;,`@0, `3;,`@10]; R13;; and R23;; (WHOLE, SEARCHED, FIND-ALL); EXPORTED LABELS on `abb`, `babb`,
  `abb ab`: all as printed.

(b) OPERAND DRILL (`work/drillB.py`, 1,365 texts, alphabet `37;a`): the right operand of `&` holding a looped label,
anchored `$`, anchored `^`, `\b`, a lookahead holding the loop, a lookbehind; the condition reads it from outside:
`(h: <5)` and NOT, 10 of 10 EQUAL to a libpcre2 model that runs B as ITS OWN pattern (model U) WHOLE on the stretch a
callout extracts; the complement `A & !(B & (h: <5))` 5 of 5; THE LAW `A & (B & (h: <5))` vs `A & (0: B & (h: <5))`
(holds, stretch) 5 of 5 at 0.
BLACK-BOX CLAIMS in nested places (`work/drillX.py`, engine vs engine): SAME-1..SAME-4 each inside a hole loop
(condition after; condition on the item), an `occurrences` argument (after; inside), the right `&` operand, atomic, a
complement, under the five conditions of PART P: 0 texts x modes differ in all 28 place-pair cells (1,365 or 364
texts, labels compared). So same-results holds for LABEL conditions in every place I could build; only the pass forms
split same-shaped spellings (MODECLOSURE-2, a box-opening request).
FIND-ALL (`work/drillF.py`): the step-one simplification equals PCRE2's own global loop for the greedy REP (both
polarities) and the lazy REP under the positive test, 0 of 364 each (the lazy NOT case is MODECLOSURE-6).
NOT TESTABLE on the engine (limits, not findings): a lazy, possessive or `{n,m}` HOLE loop (`Rep` is greedy `{lo,}`
only); a `label:` set holding groups (no node); duplicate names.

## SIBLING OF A FAMILY

Yes: the per-pass label is the third member of "a repetition unit is a fresh scope", with (1) **hits-pass** (a hit of
`occurrences` is a pass, its labels its own, R.1.9) and (2) the pass forms reading each pass's own values (**some-own**,
the PASS TABLE row). All three read ONE flat list of units. MODECLOSURE-2 and -4 are where the family stops being
flat: at two depths the members disagree on WHICH units (bare: the last unit of each enclosing level; pass forms in a
literal: the innermost units flattened; pass forms through holes: the outer units). A fourth, parallel member is "a
place has its own TEXT" (the `&` operand and the `label:` set run on the stretch, **operand-context**): the same
"scope" idea applied to text instead of labels; MODECLOSURE-5 is that family's missing row.

## GENERAL FORM + UNLOCKS

GENERAL FORM: the pass table is a TREE, not a list: a pass node holds the labels its own pass set and, per inner loop,
its list of inner pass nodes (a hit is a pass node of the `occurrences` loop). The bare condition reads the path of
LAST children from the root (the outermost view, R.1.7 (4), as ruled); a pass form names the LEVEL it ranges over
(default: the outermost loop's passes, each read at its own outermost view); a joint pairs its labels within their
LOWEST COMMON pass node (one loop: the pass; two depths: the outer pass with its last inner pass; sibling loops: the
enclosing pass, i.e. the two last passes, as the engine does today).
UNLOCKS: (1) MODECLOSURE-2 and -4 become one ruled sentence each instead of two engine accidents; TRIGGER: the first
program with a pass form or a joint over a nested label (a list of lists, `CLOSE` with sub-items), or the next full
revision's place table (`predicates_future.md` item 22). (2) An empty final pass (MODECLOSURE-1) is just a pass node
with no labels; the tree makes "is it a node" the one question; TRIGGER: the first nullable item in a hole loop. (3)
`$h[2]` / `h[2]` at depth gets a natural path form (`h[2][1]`-like, spelling open) without a new mechanism; TRIGGER:
**pass-list-read** being ruled. (4) A CONTROL that is order-based by construction (model U, structural unrolling, or
any model that renames all but the last unit's groups) checks every "which pass" rule without the positional blind
spot of MODECLOSURE-3; TRIGGER: **value-point** or **before-and-inside** being ruled (both are "which unit" questions).

CRITIC COMPLETE
