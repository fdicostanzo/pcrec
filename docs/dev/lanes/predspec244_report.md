# predspec244 — predicates_draft.md revision 24.4 (the owner's rulings since rev 24.3)

Lane predspec244 (2026-11-17, opus; DESIGN ONLY, no build go). Inputs: COND-FAMILY's entries from "OWNER RULING —
operand-context" to the end of the file; rev 24.3 of the draft; predspec243's report and engine; the rulings file.

## STATE AT HANDOFF

STATE: done. `docs/design/predicates_draft.md` is at rev 24.4; evidence in `docs/dev/lanes/predspec244_evidence/`;
`docs/design/predicates_future.md` item 24 updated (entry 12's answers RUN, entries 13-15 added).
OWED: none
RULINGS FILE: R1 and R2 applied (R2 the last): the separated list written three ways, run on `7`, `7,3,5` and with a
conditioned item, label and array (rev 24.4's PART L); it is R.1.7's worked example, before the derivations; the
draft proposes `list_of(X, sep = S)` as form (a), items-then-last; item 24 entry 12's hand answers are CONFIRMED by
the run (none differs).
STOP RULE: nothing stopped. Every line the owner was shown on 2026-11-17 that reads a label (the `3qxx` table, the
`m = 00` tables, `late` on the `10:00` and `10:15` texts, the nested `3;,` lines, the hit-list run) comes out as shown
under the one rule (PART A, 0 of 82 printed lines differ; PART H). The two answers the record names as CHANGED come
out changed as named (the one-item separated list unset; "`3` -> h = 3" now unset).
PREMISE: predspec243's engine re-ran byte-identical to its committed `.out` (its checks 37 of 37).
Head line BEFORE: `**rev 24.3: review r42's fixes; NOT STABLE pending the owner's answers** (§R.8).`
Head line AFTER: `**rev 24.4: one label rule (branchings reset), the hit list atomic and anchored, the filter
sentence, join order (the owner, 2026-11-17 evening); NOT STABLE pending the owner's answers** (§R.8).`
Size: 7,391 lines (893,310 bytes) before, 7,638 lines (919,410 bytes) after. Changelog: a new top entry.

## RULINGS APPLIED

| ruling (COND-FAMILY entry) | his words quoted at | where |
|---|---|---|
| branchings reset the labels inside them ("Yes. Let's keep it"; the declarative account; "the labels bubble up. Last pass and last mention") | R.1.7 THE RULE | R.1.7 rewritten; R.1 plain words; §R.6 label row; §R.8 before-and-inside dissolved; §4.3 mark |
| what an unqualified `$x` reads ("I do want that. It makes sense and frankly pcre is wrong on this. I agree but! We need a way to get the pcre behavior even if ugly") with pass-list-read (2), (3) ("Eg Perl uses @x. An array of such values is its own type") | R.1.7 THE THREE READS | the label, the carried-capture form, the array form and its type rule; §R.4 sentences; spellings list 2, 3 |
| the hit list atomic and anchored ("hits-text: yes but spelling to be reviewed with all other spellings") | R.1.9 | R.1.9 rewritten; §R.6 rows; spellings list 1 |
| join-order ("left side decides. That's always how I thought of it") + the autocorrect NOTE | R.1.4 | R.1.4 join order and distribution; §R.8 |
| operand-context and its ADDENDUM ("any piece that might look outside is a compiler error"; "yes to that interpretation. Also, then the start of subject and end of subject need the same interpretation") | R.1.4 | the filter sentence; the refused set as THE DRAFT'S READING; §R.6 rows; §R.2 sentence; §11 mark |
| zero-place ("That's its whole world. So all numbers are labels of groups in that world. Also, not recommended to use group numbers") | R.1.4 | THE LAW in every place; numbered-label-warning asked |
| before-and-inside (four discussion entries) | R.1.7 | DISSOLVED by the one rule; joint-last-pass stays dissolved |

## WHAT MOVED

Answers that MOVED from rev 24.3's text (each from `predspec244_model.out`):
- `hits(/(?<n>\d+)/) & occurs.none(NOT (n: <100))` on `x300 12` SEARCHED: `x30`@0 with the hit [`30`] (rev 24.3, the
  stretch reading) -> FAILS (the hit list standing alone is the whole subject's, [`300`, `12`]; PART H).
- `hits(/a(?<g>x)?/) & (g: "x")` on `axa` SEARCHED: `ax`@0 -> FAILS (PART H); WHOLE stays FAILS.
- Two groups of one name (no rule in rev 24.3; PART N): `/(?<h>\d)?;(?<h>\d)?/` on `3;` h UNSET; the two-copy list
  on `7` h UNSET; an alternation's untaken branch `3;x` h UNSET in either order (rev 24.3's rules as implemented
  here give `3` for the first and the last two).
- The filter's refused set: rev 24.3 refused `\b` and edge lookarounds and asked about `\B`, `\G`, `\K`, inner
  lookarounds; rev 24.4 refuses every piece that might look outside (THE DRAFT'S READING of which; PART F).
Rules that moved without moving a printed answer: the per-pass label rules (replaced by one rule; PART A 0 of 82,
PART B 0 on 16 programs); join order, hits-text, hits-committed, zero-place, pass-list-read, operand-context from
asked to RULED.
Lines before and after (head line and size): STATE AT HANDOFF above.

## WHAT NOW FOLLOWS FROM ONE RULE

RUN, not assumed (the brief's evidence-first test of the manager's claim):
- PART A: 82 answer-lines rev 24.3 printed that read a label (S1-S5 and `late`, NEST and both inner views, the pass
  forms two loops deep, the joints across depths and siblings, the empty pass, LAST-PASS-DEFAULT, §R.7's REP lines,
  value-point, some-own, pass-list-read, U1, the duplicate name in a loop, the exported `occurrences` label): 0 differ
  under the one rule; 0 under rev 24.3's rules (the switch back).
- PART B: the one rule vs rev 24.3's rules over 16 programs on their pools, reported row with labels, every mode:
  0 / 0 / 0 each; the capture-vs-rule counts rev 24.3 printed are reproduced by this new engine under both rules
  (28 / 40 / 40, 8 / 33 / 33, 5 / 34 / 34, 4 / 7 / 11, 10 / 20 / 20).
- So the per-pass label, the empty last pass, the outermost view for nested loops and for pass tests, the `3qxx`
  table, the `m = 00` table and the `late` loop FOLLOW, as the manager claimed.
- EXCEPT ONE PLACE (PART C, new; no printed or shown line sits there): a condition inside a loop body written BEFORE
  its label's group, with no branching around the group. Under the one rule as worded the loop resets only when
  entered, so the pass reads the PREVIOUS pass's value; rev 24.3's "a pass has its own labels" read unset.
  `/(?:${c}(?<h>\d);)*/`, c := NOT (h: >= 5): `7;3;` FAILS (rev 24.3 HOLDS); 2 / 8 / 14 of 364 differ; 15 / 29 / 47
  with the group optional; 0 inside an alternation in the body. Asked as **pass-start-read**.
- NEW ANSWERS (PART N, WHOLE): `/(?<h>\d)?;(?<h>\d)?/` on `3;` h UNSET; `/(?<h>\d)?(?:;(?<h>\d)?)*/` on `3;` UNSET,
  `7;3;` UNSET, `7;3` `3`, `3` UNSET; `/(?<h>\d)(?:,(?<h>\d))*/` on `7` UNSET (accepted), `7,3` `3`; an alternation's
  untaken branch UNSET in either order. libpcre2 refuses each without `(?J)` ("two named subpatterns have the same
  name (PCRE2_DUPNAMES not set)"), and under `(?J)` reads the lowest-numbered set group (`3;4` -> `3`).
- CONTROL: the MARKER MODEL on libpcre2 equals the one rule on 10 programs (0 differ each); without markers 9 of 10
  differ (the order check).

## OWNER QUESTIONS LEFT

§R.8 (b), each with WHOLE / SEARCHED / several-match answers per candidate:
- pass-start-read (new): a condition before its group in a pass reads the previous pass's value (the rule as worded) or unset (each pass resets): `7;3;` FAILS vs HOLDS.
- array-slot (new): a reset after a setting leaves an empty slot in the array or not: `7;;3;` [`7`, `3`] vs [`7`, -, `3`, -].
- numbered-label-warning (new, the manager's proposal): warn on a numbered label read on a bound pattern.
- shared-label (re-examined, still asked: "last mention" needs an order of mentions `&` does not give): ERROR vs LEFT vs LAST MENTION, `/(?<h>\d)\d/ & /\d(?<h>\d)/ & (h: <2)` on `12` HOLDS (left) vs FAILS (last); 4 / 134 / 150 of 341.
- looped-warning (unchanged numbers; widened: optionals and alternations now reset by the same rule).
- label-twice-warn, empty-search-error, min-values, dollar-condition (the four "is this error a warning"; dollar-condition's reading now gives `(x: S)`'s answers exactly).
The SPELLINGS list (§R.8): 11 entries (hit list, array form, carried-capture form, atomic, no-re-entry sequence,
skip-past verb, conditional, every-pass shorthand, options and strictness, warning names, rx-module operators).

## EVIDENCE AND COMMANDS

All from `$PCREC_TMPDIR/scratch/predspec244` (= /var/tmp/pcrec-pcrec/scratch/predspec244), one process at a time:
- premise: `timeout 1800 python3 -I -B <wt>/docs/dev/lanes/predspec243_evidence/predspec243_model.py > premise.out`;
  `diff premise.out <wt>/docs/dev/lanes/predspec243_evidence/predspec243_model.out`: identical.
- forward: `timeout 1800 python3 -I -B <wt>/docs/dev/lanes/predspec244_evidence/predspec244_model.py > fwd.out`
  (committed as `predspec244_model.out`): CHECKS 129 of 129 OK.
- sabotage: `PREDSPEC244_SABOTAGE=1 ...`: 68 of 129 OK, PART A 32 of 82 lines differ: caught.
- switch: `PREDSPEC244_RULES=243 ...`: 129 of 129; the output differs from the forward run only in its header line.
- counts name their rules (244 = the one rule; 243 = rev 24.3's; carry = PCRE's capture), metric (reported row:
  holds, stretch and labels, WHOLE / SEARCHED / FIND-ALL) and pool (strings over `37qx`, `37;`, `37;,`, `37;x`,
  `37,`, `129 `, `012 ` up to length 4 or 5; lists of up to three time items), as the .out names them.
- libpcre2-8 10.46 through `docs/dev/lanes/rxmodel_evidence/pcre2h.py`; the review drills are PART D (optional label
  in a looped place; two loop depths; a place inside a place; a nullable body; a duplicate name across a loop) and
  PART F (anchored, `\b`, lookahead operands: refused or allowed).
- LIMITS: the marker model is positional (exact with no empty label group); PART F's classifier is a reading for the
  operands listed; W8 (a §R.4 row) is not re-run under the ruled hit list (said in §R.4).
