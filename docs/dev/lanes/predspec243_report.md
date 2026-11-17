# predspec243 — predicates_draft.md revision 24.3 (review r42's fixes)

Lane predspec243 (2026-11-17, opus; DESIGN ONLY, no build go). Review: `docs/dev/reviews/2026-11-17-r42-predspec242.md`
(filed by another lane); the manager's dispositions were the instructions, id by id.

## STATE AT HANDOFF

STATE: done. `docs/design/predicates_draft.md` is at rev 24.3; evidence in `docs/dev/lanes/predspec243_evidence/`.
OWED: none
RULINGS FILE: R1, R2, R3 applied (R3 the last). R2 corrects R1: empty-pass stays THE MANAGER'S READING, told, with
the owner's observation quoted ("makes sense as the entire rx is optional"; "not so much a ruling as an
observation"); R3: his "this is how i expected" quoted beside A2's reading. Both also added as §R.11 rows 42, 43.
STOP RULE: nothing stopped. No answer the owner was shown on 2026-11-17 moved (PART 0: 0 changed lines of rev 24.2's
answer file, PART S's `3qxx`, `m = 00`, `late` / `10:15` and `9:45,10,` lines included).
Premise test (before any change): predspec242b's engine re-ran byte-identical (123 s); the critics' scripts
reproduced A1 30 / 80 / 116 of 121 (NL2 80 / 80 / 80), A2 13 / 353 / 973 of 1,365, A4 301 of 364, A5 9 / 33 / 33.

Head line BEFORE: `**rev 24.2: a loop pass has its own labels; a bare condition after the pattern reads the last
pass's own (the owner, 2026-11-17 evening); NOT STABLE pending the owner's answers** (§R.8).`
Head line AFTER: `**rev 24.3: review r42's fixes; NOT STABLE pending the owner's answers** (§R.8).`
Changelog: a new top entry for rev 24.3 (earlier entries kept, as every revision has done).
Size: 7,230 lines (869,913 bytes) before, 7,391 lines (893,310 bytes) after.

## FIX TABLE

| id | disposition | done | witness / where |
|---|---|---|---|
| A1 | FIX-NOW + told (empty-pass) | engine: the empty iteration kept as the last pass in the literal loop, the hole loop and `occurrences`; R.1.7 (4a); §R.8 (a) | NL `& NOT (h: <5)` vs libpcre2 model U 30 / 80 / 116 -> 0 / 0 / 0 of 121; NL2 80 / 80 / 80 -> 0; literal = hole loop 0 on five conditions; `occurrences(/(?<h>\d)?/)` = model U 0 of 63 (PART X1) |
| A2 | FIX-NOW, manager's reading, told | engine: the pass forms keyed on the outermost loop; R.1.7 (4b); §R.8 (a) | literal vs holes: `some` 6 / 11 / 11, `occurs.none(NOT ..)` 13 / 353 / 973, `h[2]` 7 / 17 / 17 -> all 0 of 1,365; = an independent direct evaluator 0 (PART X2) |
| A3 | FIX-NOW (text) | R.1.7 (4b): joint across depths runs; sibling-loop pass forms UNSPECIFIED, NOT RUN | PART X3: two depths `some(J)` on `37;,51;,` HOLDS; siblings REJECTED by the engine |
| A4 | FIX-NOW | R.1.2 states PCRE2's global loop; engine + every libpcre2 model run it; §R.6 row | lazy `& NOT (h: <5)` engine vs PCRE2's loop 301 -> 0 of 364; the three others 0 -> 0 (PART X4) |
| A5 | FIX-NOW | model U the control (PART U, 15 of 15); R.0, §R.6, §R.10; helper-group kept for G1, G2, G9e | LB / LA helper vs engine 9 / 33 / 33 each (kept as the limit's witnesses) |
| A6 | DOC | §R.6 (label vs capture rows, per-pass label paragraph), §4.3 mark, pass-list-read row | `/(?J)(?:(?<x>a)\|(?<x>b))+\k<x>/` matches `abba`, not `abbb` (PART Z) |
| B1 | DOC; answer claim rejected | R.1's numeral sentence QUOTES §2.4; S4 gets model U (0 of 85); reach of "unless the literal has them" stated as THE DRAFT'S READING | PART U S4 |
| B2 | DOC | §2.2 -> §2.4 at the four cites | grep |
| B3 | DOC | R.1.4 cites the record's CORRECTION (1): the fragments were a toy rule's; re-run under the draft's `late` | R.1.4 |
| C1 | FIX-NOW | value-point, hits-pass, some-own, same-results -> §R.8 (a), each with its entailing ruling quoted; "(the end of each pass)" SUPERSEDED (row 41) | §R.8 (a) |
| C2 | FIX-NOW | looped-warning: costs listed (fires on the ruled meaning; splits SAME-1; strict-all makes errors); name `label.looped`; §7.1 mark; still asked | §R.8 (b) |
| C3 | FIX-NOW | §R.2: example with a defined name `@options.strict(/test\.never/)`, his `no-fail` shown as his example; `predicates_future.md` item 23 | §R.2 |
| C4 | FIX-NOW, told | §R.2 UNSETTABLE-LABEL IS `test.never`; §7.1 mark; removed from the R5 table; §R.8 (a) | §R.2 DEFINE witness (derived) |
| C5 | FIX-NOW, manager rules neither | §R.6 row moved to "allowed by the owner, 2026-11-15" with his words and RECORD (3); the DIFFERENCE listed (rev 24.2's stretch reading vs §11's error; the entry wins); edge-assertion left the R5 list; operand-context narrowed | PART K, one example per construct, both ways |
| C6 | DOC | R.1.4 and §R.11 row 39: (*SKIP) labelled THE MANAGER'S READING of "(*prune) or similar" | R.1.4 |
| C7 | FIX-NOW (doc) | RULING-1 heading name; RULING-10 §R.11 rows 11, 20, 27, 32, 35; RULING-11 §R.9 marks (§5.2, §7.1, rev 24.3's); RULING-12 §2.6 example HOLDS g = `a`; RULING-14 R.1.7 (1) attribution; RULING-15 the MINE carried into the every-pass-spelling and rx-module rows as the manager's input | PART Z |
| D1 | DOC | zero-place row: 738 with hit lists, 660 holds and stretch, hit-list part engine-only; both printed in PART Z | PART Z |
| D2 | NOTED; reach as DOC | §R.10 and the evidence CLAUDE.md state both sabotages' reach | §R.10 |

## WHAT MOVED

No printed number of rev 24.2 moved: predspec242b's whole output re-runs under rev 24.3 with 0 changed lines (PART
0), because no pool of PARTS 0-Q has a nullable loop body, a pass form two loops deep in a literal, or a lazy loop
whose FIND-ALL depends on PCRE2's retry. Numbers that are NEW in rev 24.3 (before = rev 24.2's engine, after = rev
24.3's):
- NL `/(?:(?<h>\d)?)*/ & NOT (h: <5)` vs libpcre2: 30 / 80 / 116 -> 0 / 0 / 0 of 121; witness on `3`: FAILS / ``@0 /
  [``@0, ``@1] -> HOLDS h unset / `3`@0 / [`3`@0, ``@1].
- NL2 `/(?:(?<h>\d)|;?)*/ & NOT (h: <5)`: 80 / 80 / 80 -> 0.
- NEST pass forms, literal vs holes: 6 / 11 / 11, 13 / 353 / 973, 7 / 17 / 17 -> 0; `NEST & (h[2]: <5)` on `,3;,`
  FAILS -> HOLDS h = `3`; `occurs.none(NOT ..)` on `,` HOLDS -> FAILS.
- lazy `/(?:(?<h>\d)?;)*?/ & NOT (h: <5)` FIND-ALL vs PCRE2's loop: 301 -> 0 of 364; on `;` [``@0, ``@1] -> [``@0,
  `;`@0, ``@1].
- §2.6's kept example `(m: occurrences(/(?<g>a)?b/) & (g: "a"))` on `abb`: text said REJECTS -> HOLDS g = `a` (the
  engine already gave HOLDS under rev 24.2; a text fix).
- §R.6's operand-context row: rev 24.2's draft reading (stretch, `a1` SEARCHED `1`@1) -> the edge-assertion ERROR
  (the 2026-11-15 ruling; §11 already said so).
- unsettable-label: a compile error -> the `test.never` warning.

## OWNER QUESTIONS LEFT

§R.8 (b), each with the text on which its candidates differ:
- before-and-inside: `/(?<h>\d)?(?:;(?<h>\d)?)*/ & (h: <5)` on `3;`: last pass's own FAILS, keep-outside HOLDS.
- looped-warning (`label.looped`): no answer moves; it warns on bare `/(?:(?<h>\d);)*/ & (h: <5)` and not on SAME-1's twin.
- hits-text: `x300 12` SEARCHED, stretch hits [`30`] vs subject [].
- hits-committed: `hits(/a(?<g>x)?/) & (g: "x")` on `axa` FAILS (committed) vs the one-pattern hits.
- join-order: `G & L` on `11` SEARCHED `11`@0 (left) vs `1`@0 (right).
- pass-list-read: `/(?:(?<h>\d);)*(?<k>\d)/ & (k: == $h)` REJECTED (list) vs `3;7;7` HOLDS (last).
- zero-place: `occurrences(/\d+/ & (0: /1\d*/), min = 1)` on ` 1` HOLDS (innermost) vs FAILS (group 0).
- operand-context (narrowed): `/\d+/ & /\B\d+/` (and lookbehind, lookahead, `\G`, `\K`) REJECTED (covered) vs run on
  the stretch, e.g. `/\d+/ & /\d+(?![a-z])/` on `1a` -> `1`@0.
- shared-label: a label in both `&` operands, error vs `(?J)` reading (not run).
- label-twice-warn: `(h: >2, h: <5)` on `3` REJECTED vs HOLDS.
- empty-search-error: `/(?<h>\d*)/ & NOT (h: <5)` on `a7` REJECTED vs ``@0.
- min-values: `occurrences(/\d/, min = 2)` on `1a2` REJECTED vs HOLDS.
- dollar-condition: `/(?<x>\d+)/ & ($x & <5)` on `3` REJECTED vs HOLDS.
Told, not asked (§R.8 (a)): empty-pass, outer-pass-forms, value-point, hits-pass, some-own, same-results,
unsettable-label.

## EVIDENCE AND COMMANDS

All from `$PCREC_TMPDIR/scratch/predspec243` (= `/var/tmp/pcrec-pcrec/scratch/predspec243`), one process at a time,
each under `timeout 1800`:
- forward: `(cd run && timeout 1800 python3 -I -B <wt>/docs/dev/lanes/predspec243_evidence/predspec243_model.py > fwd.out)`
  (about 140 s): PART 0 0 changed hunks; checks 37 of 37 OK; model U 15 of 15. Committed as `predspec243_model.out`.
- sabotage: `PREDSPEC243_SABOTAGE=1` the same: checks 27 of 37 OK (X1 NL / NL2 NOT, six X2, X4 lazy NOT, U NL
  FAILED); model U 14 of 15: caught. Reach limits in the evidence CLAUDE.md and §R.10.
- the critics' scripts against rev 24.3's engine (`drills/`: copies of the modeclosure critic's drillA, drillN,
  drillF, helper and um, with `eng.py` re-pointed to load predspec242b's source through predspec243's patches):
  drillA 40 EQUAL lines (NL, NL2 now EQUAL; premise: 2 DIFFER); its two remaining DIFFER lines (Q6 lazy, N2 outer
  lazy, under NOT) are the critic's model U using the step-one FIND-ALL: `drillA_glob.py` runs the same four rows
  with model U under PCRE2's global loop, 0 of 364 / 0 of 1,365 each; drillN 21 EQUAL, 0 DIFFER (the three PF rows
  0 of 1,365; premise: 3 DIFFER); drillF engine vs PCRE2's loop 0 on all four (premise: the lazy NOT 301 was the
  engine's too); helper LB / LA unchanged (9 / 33 / 33: the helper model's limit, by design), NL equal.
- doc checks: `scripts/check_claudemd_size.sh` on the new CLAUDE.md; `scripts/lanecheck`.
