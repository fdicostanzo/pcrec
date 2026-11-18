# predspec26 report: predicates_draft.md rev 26 (the owner's 2026-11-18 rulings; ONE PLACE TABLE)

Lane predspec26 (2026-11-18, opus; DESIGN ONLY, no build go). Branch `lane/predspec26`, cut from main @ 3c40ba007.
Subject: `docs/design/predicates_draft.md` rev 25.1 -> rev 26, head line "rev 26: the owner's 2026-11-18 rulings
folded; §R rebuilt on ONE PLACE TABLE (R.1.0); NOT STABLE pending the owner's answers". Also `predicates_future.md`
item 24 (entries 21-29 appended, nothing else) and `docs/dev/lanes/predspec26_evidence/`.

## STATE AT HANDOFF

- STATE: done. STAGE A (the fold, all 32 entries from "2026-11-18 MANAGER CORRECTION" to the end of COND-FAMILY.md)
  and STAGE B (§R rebuilt on R.1.0 THE PLACE TABLE + THE HOLE POSITIONS table; the operator table, already complete in
  rev 25.1, gains two rows) both delivered, so the id is rev 26.
- Rulings file `predspec26_rulings.md`: EMPTY at every re-read (before each commit, at the end of Stage A, before this
  report). Last R-n applied: empty.
- NOT FOLDED: none. `git -C /home/pcrec/projects/pcrec log --oneline -5 -- docs/design/plan_row_bodies/COND-FAMILY.md`
  at the end of Stage A: newest e325810db (lone-complement-match), the branch point's own last entry; main has no
  COND-FAMILY, predicates_draft or predicates_future change since 3c40ba007.
- STOPS: none. Every table shown to the owner in the 11-18 entries reproduced except the manager's lazy-`any` clause
  (CX3), which is a manager's reading, not a shown ruling's table: recorded as NOT SUPPORTED, not a STOP.
- RUNS NOT RUN: none; all single-process python scripts of seconds, before the 20:00 hold.
- Draft size: 8,256 lines (1,009,611 bytes) before, 8,750 lines (1,073,336 bytes) after (`wc -lc`).

## RULINGS APPLIED

One row per 2026-11-18 entry (32). The owner's words are quoted in the draft at the place named; §R.11 rows 76-107
carry the per-entry state.

| entry title | his words quoted at | where |
|---|---|---|
| 2026-11-18 MANAGER CORRECTION — "the right side of `&`" was the manager's slip (no owner words) | no owner words (the manager's correction) | §R.11 row 76; R.1.4, R.1.14, §R.8, §R.9 |
| 2026-11-18 OWNER RULING — number-names | R.1.13 (HIS WORDS, cited by the entry's title and date) | §R.11 row 77; R.1.13, R.1.0 |
| 2026-11-18 OWNER RULING, addendum to number-names — zero is the exception | R.1.13 (HIS WORDS, cited by the entry's title and date) | §R.11 row 78; R.1.13, R.1.0 |
| 2026-11-18 OWNER RULING — hit-carry: it carries, because `occurrences` is a rewrite | R.1.7 (HIS WORDS, cited by the entry's title and date) | §R.11 row 79; R.1.7, R.1.9, §2.6 |
| 2026-11-18 OWNER RULING — nullable argument: a warning | R.1.9 (HIS WORDS, cited by the entry's title and date) | §R.11 row 80; R.1.9, §2.6, §R.8 (a) |
| 2026-11-18 OWNER RULING — product-order: first slowest; and a correction of the product's scope | R.1.14 (HIS WORDS, cited by the entry's title and date) | §R.11 row 81; R.1.14, R.1.0 HOLE POSITIONS |
| 2026-11-18 OWNER, on the cartesian idea and "legal" | R.1.14 (HIS WORDS, cited by the entry's title and date) | §R.11 row 82; R.1.14 |
| 2026-11-18 OWNER RULING — name-hole: an array in a group-name hole is a compile error | R.1.0 HOLE POSITIONS (HIS WORDS, cited by the entry's title and date) | §R.11 row 83; R.1.0 HOLE POSITIONS, R.1.14 |
| 2026-11-18 OWNER RULING — removal: the whole copy | R.1.0 (HIS WORDS, cited by the entry's title and date) | §R.11 row 84; R.1.0, R.1.14 |
| 2026-11-18 OWNER on value-is-pattern: one ruling, two leans, one idea | R.1.14 (HIS WORDS, cited by the entry's title and date) | §R.11 row 85; R.1.14, R.1.15 |
| 2026-11-18 OWNER RULING — array-lift: operations on arrays combine on the product | R.1.14 (HIS WORDS, cited by the entry's title and date) | §R.11 row 86; R.1.14 |
| 2026-11-18 OWNER RULING — hole-in-filter: the filter error; fill the holes first | R.1.4 (HIS WORDS, cited by the entry's title and date) | §R.11 row 87; R.1.4, R.1.0 |
| 2026-11-18 OWNER RULING — backref-across-parts: the part's own group; a reference uses the namespace at its point | R.1.13 REFERENCES (HIS WORDS, cited by the entry's title and date) | §R.11 row 88; R.1.13 REFERENCES |
| 2026-11-18 OWNER, clarifying backref-across-parts — a backreference reads as labels do: the last mention at its point | R.1.13 REFERENCES (HIS WORDS, cited by the entry's title and date) | §R.11 row 89; R.1.13 REFERENCES |
| 2026-11-18 OWNER, reopening backref-across-parts for DISCUSSION | R.1.13 (HIS WORDS, cited by the entry's title and date) | §R.11 row 90; R.1.13 |
| 2026-11-18 OWNER RULING — free-name: a reference to a name the rx does not define is an error (closes the backref-across-parts discussion) | R.1.13 REFERENCES (HIS WORDS, cited by the entry's title and date) | §R.11 row 91; R.1.13 REFERENCES, R.1.0 |
| 2026-11-18 OWNER on path-and-ambiguity: the part label used twice is RULED; the read-out is open | R.1.13 PATHS (HIS WORDS, cited by the entry's title and date) | §R.11 row 92; R.1.13 PATHS, R.1.0 |
| 2026-11-18 OWNER on the read-out — a lean: a filter never produces captures | R.1.13 (HIS WORDS, cited by the entry's title and date) | §R.11 row 93; R.1.13 |
| 2026-11-18 OWNER PROPOSAL — labels are seen only if exported; a literal's labels are exported in its scope | R.1.13 (HIS WORDS, cited by the entry's title and date) | §R.11 row 94; R.1.13 |
| 2026-11-18 OWNER, discussing export-scope | R.1.13 (HIS WORDS, cited by the entry's title and date) | §R.11 row 95; R.1.13 |
| 2026-11-18 OWNER, continuing the export-scope discussion | R.1.13 (HIS WORDS, cited by the entry's title and date) | §R.11 row 96; R.1.13 |
| 2026-11-18 OWNER, export-scope discussion, third exchange | R.1.13 (HIS WORDS, cited by the entry's title and date) | §R.11 row 97; R.1.13 |
| 2026-11-18 OWNER RULING — export-rule: public unless `_`; a binding shows its own public labels and its public part labels (closes the export-scope discussion and path-and-ambiguity) | R.1.13 EXPORT (HIS WORDS, cited by the entry's title and date) | §R.11 row 98; R.1.13 EXPORT, R.1.0 |
| 2026-11-18 OWNER, clarifying export-rule's sixth statement, and adding a form: `[_ = A]` closes all exports | R.1.13 (HIS WORDS, cited by the entry's title and date) | §R.11 row 99; R.1.13, R.1.0 |
| 2026-11-18 OWNER confirms the reading of `[_ = A]` | R.1.13 (HIS WORDS, cited by the entry's title and date) | §R.11 row 100; R.1.13, R.1.0 |
| 2026-11-18 OWNER RULING — condition-in-sequence: yes, and `&` stays | R.1.14 (HIS WORDS, cited by the entry's title and date) | §R.11 row 101; R.1.14, R.1.0 |
| 2026-11-18 OWNER RULING — quantified-condition: an error, as a formal punt | R.1.14 (HIS WORDS, cited by the entry's title and date) | §R.11 row 102; R.1.14, §R.6, R.1.0 |
| 2026-11-18 OWNER RULING — lookahead-labels: visible, as in PCRE | R.1.4 (HIS WORDS, cited by the entry's title and date) | §R.11 row 103; R.1.4, R.1.0 |
| 2026-11-18 OWNER RULING — complement-place: the error is at the USE; two kinds of rx | R.1.4 (HIS WORDS, cited by the entry's title and date) | §R.11 row 104; R.1.4, R.1.0 |
| 2026-11-18 OWNER, discussing complement-place further | R.1.4 (HIS WORDS, cited by the entry's title and date) | §R.11 row 105; R.1.4, §R.8 **anything-text** |
| 2026-11-18 OWNER, clarifying the entry above | R.1.4 (HIS WORDS, cited by the entry's title and date) | §R.11 row 106; R.1.4 |
| 2026-11-18 OWNER RULING — lone-complement-match: it stays an error; provide "anything" | R.1.4 (HIS WORDS, cited by the entry's title and date) | §R.11 row 107; R.1.4, R.1.0, §R.8 |

## MANAGER READINGS CHECKED

24 readings. SUPPORTED / NOT SUPPORTED / NOT RUNNABLE / RULE-AS-CODE (a consistency check of the ruling as code,
never an independent control). PART ids are `predspec26_evidence/predspec26_model.out` lines.

| reading | verdict | run |
|---|---|---|
| number-names: a number on a group whose name is shared is refused | SUPPORTED | N1: 7 / 277 / 284 of 364 differ between the readings |
| number-names addendum (1): `0` in an `&` chain is the chain's stretch | SUPPORTED | N3: 0 / 0 / 0 |
| number-names addendum (2): `0` inside a loop or hit names that pass's / hit's match | SUPPORTED | N4: own 0 differ, group-0 reading 81 |
| hit-carry consequence: "a plain search" only without a condition before its group | SUPPORTED | H3: 84 of 364 carried vs plain |
| hit-carry consequence: §2.6's second refusal goes | SUPPORTED | H1, H2 (the carried answers exist and are PCRE's) |
| nullable: "PCRE's meaning ... as the empty search does" | NOT SUPPORTED as worded | H4 (find-all `/\d*/` on `a1b`: 4 hits) vs H5 (the loop rewrite: ONE empty hit); the loop's meaning is entailed by the rewrite ruling |
| nullable: the warning's name `pcrec.` and "a fifth candidate" | NOT RUNNABLE | naming |
| product-order: first slowest = a sequence of alternations | SUPPORTED | P2 (Python, the shown run), P3: 0 / 0 / 0 |
| "legal sql" read as an autocorrection of "legal still" | NOT RUNNABLE | wording |
| removal: a removed-to-nothing copy never matches; the can-never-match warning | SUPPORTED (P4); the warning RULE-AS-CODE (P4b) | P4 |
| count kind: "must" read as a compile error | NOT RUNNABLE beyond P7 | P7 shows PCRE reads `\d{x}` as text, so the error is a choice |
| array-lift: repeats are harmless | SUPPORTED | AL3 |
| array-lift: the scope statement; a pairwise form a future idea | NOT RUNNABLE | scope |
| backref-across-parts: the final state (the part's own group; free-name) | SUPPORTED | REF1-REF3 |
| backref readings (a) and (d) as the rule | WITHDRAWN by the owner's clarification | REF2 kept as the model |
| export-rule: what it closes (pass-through, path-and-ambiguity's read-out, filter-captures) | CONSISTENT, RULE-AS-CODE | EX1-EX3 |
| label-mark closed by entailment | SUPPORTED (entailed) | EX table |
| quantified-condition: its scope (nine operators, `repeat`, `${c}*`) | RULE-AS-CODE | CS4, CS5 |
| lookahead-labels: lookbehind the same | SUPPORTED | LA4 |
| complement-place: the illustration of the two kinds | CONSISTENT, RULE-AS-CODE | CX1 |
| `any` simulation: greedy reproduced | SUPPORTED | CX3 |
| `any` simulation: the lazy clause | NOT SUPPORTED | CX3: lazy gives [``@0, ``@1, `1`@1, ``@2, `2`@2, ``@3], not the shown list |
| "every spelling of anything agrees as a whole value" | NOT SUPPORTED for `/.*/` | CX4: `/.*/` differs on 90 of 121 texts with a newline; `(?s).*`, `[\s\S]*` 0 |
| condition-in-sequence: last in a sequence = `&` | SUPPORTED | CS3 |

NOT SUPPORTED by the runs: (1) the nullable argument's "PCRE's meaning as the empty search does" (the rewrite gives the
loop's ONE hit; the draft now says so); (2) the lazy clause of the `any` simulation; (3) "every spelling agrees as a
whole value" for `/.*/` (newlines).

## THE PLACE TABLE

`predicates_draft.md` R.1.0: THE TWO KINDS OF RX (complement-place) and one table, 14 places (the program, an `&`
operand, a sequence operand, a condition as a sequence operand, a loop body / postfix operand, an `occurrences` /
`contains` argument, `hits(r)`, an atomic part, a lookahead / lookbehind, a pattern hole, a `label:` set, a `records`
item, a binding, a part label) x 9 columns (TEXT and MODE, the KIND needed, re-entry, what `0` names, what another
NUMBER names, VISIBLE / EXPORTED, where a REFERENCE resolves, the regex model, the section). Then THE HOLE POSITIONS
table: pattern, count, group name, character class, option, backreference name, `\Q..\E`, zero values, match value,
each with its own rule (count: product, first slowest, whole-copy removal, counts only; name: an array is an error;
class, option: OPEN, **other-holes**; match value: UNRULED, **value-hole**). R.1.1's PLACES paragraph and rev 25.1's
R.1.14 position table are now pointers to it. The ONE OPERATOR TABLE (§5.4, rev 25.1) gains: a condition as a
sequence operand (level 6) and a postfix quantifier on a condition as a compile error (level 2).

## EXAMPLES THAT MOVED

Greps over rev 25.1 (`git show 3c40ba007:docs/design/predicates_draft.md`); the full block is §R.7 "REV 25.1 -> REV 26".

| category | grep | rev 25.1 hits | moved |
|---|---|---|---|
| numbers on composed patterns | `([1-9]: \|\$[1-9]\b` | 12 lines | 5 examples to the error (`A SEQ B & (1: <5)`, `/${A},(\d)/ & (1: ..)`, `(A \| B) & (1: <5)`, `A & B & (1: <2)`, the shared-name one); one-literal examples kept |
| part labels / paths (export-rule) | `\[[a-z_]* = [A-Za-z]`; `[a-z]\.[a-z]: ` | 20; 4 | 0 (no `_` label in any example) |
| quantified conditions | `(h: <5)?` and kin | 1 example | 1, to the compile error |
| lone complement | `Alone (`/`standalone complement` | 5 lines | 0 answers moved; now RULED at the use (§2.2 marked) |
| hit-list argument with a condition before its group | `occurrences(/${c}`; `TWO ARGUMENT REFUSALS`; L53/L62 | 2; 8; 2 | the 2 kept (now RULED); §2.6 + L53 (to a WARNING) + L62 (to the loop's one hit `aca`) |
| products over non-count holes | `copied per member` etc. | 6 lines | the name copies to a compile error; class/option OPEN; count examples kept |
| array arithmetic | `n + 1`, `value-is-pattern` | 14 lines | `repeat(rx.digit, n + 1)` RULED `(?\|\d{3}\|\d{5})` (AL2) |
| value holes | `\${\$` | 12 lines | 7 live uses MARKED unruled (§0.1 L33, §2.5, §4.1, §11, §13 x3); §16's 2 the record; §5.4 `^` row a reader |

WITHDRAWN-TERM SWEEP (whole rev 26 draft; total hits / hits left without a "[REV 26]" mark, each read): "asked as
**hit-carry**" 2/0; "nearest pattern" 8/6 (R.1.13's SUPERSEDED paragraph, §R.9 and §R.11 record rows, rev 26's own
withdrawn-list); "not subject to the ambiguous-reference" 3/2 (the superseded paragraph); "asked as **product-order**"
3/2 (record rows); "value-is-pattern" 18/8 (rev 26's own split text and record rows); "path-and-ambiguity" 13/8,
"quantified-condition" 21/13, "complement-place" 17/7, "lookahead-labels" 12/6, "label-mark" 8/2 (rev 26's own
ruling text, R.1.0, §R.8 RULED list, §R.10); "TWO ARGUMENT REFUSALS" 8/2 (§2.6 item 3 points at the marked head;
§R.9 record); "can never produce captures" 2/1 and "LEFT side's value" 3/2 (R.1.13, stated withdrawn); "plain search"
6/4 (R.1.9 narrowed, marked at its head); "copied per member" 3/2 (count rows, still true); "PLAIN alternation" 0.
Every remaining unmarked hit is the ruling's own new text or a record row.

## THE VALUE HOLE FLESHED OUT

`predicates_draft.md` R.1.15 (UNRULED; **value-hole**), points (1)-(9), on rev 26's PART VH (a libpcre2 callout
model controlled against `\k<y>`: 0 / 0 / 0 of 364): (1) a value is inserted as LITERAL TEXT, not regex (VH3:
`/(?<y>[\d.]+)-${$y}/` on `1.5-1x5` FAILS literally, HOLDS as regex); (2) numeral width: canonical vs width-kept both
run (`0099` + 1), the draft reads canonical; (3) an unset label: FAIL / EMPTY / compile error, the draft reads FAIL;
(4) in a loop the pass's own value (VH5); (5) in a hit-list argument hit-carry applies (VH6); (6) all three modes on a
several-match subject (VH1, the draft's hand answers reproduced); (7) the engine level: a generalized backreference,
enumerable for a finite label; (8) the control; (9) what it meets (dollar-condition). Every live use is marked.

## OWNER QUESTIONS LEFT

- **value-hole** — may a matched value stand in a pattern position, read as literal text, canonical numerals, unset = FAIL?
- **other-holes** — what several values mean in a character-class or option hole (product scope covers count holes only).
- **plus-operands** — what `+` means on non-numbers (two patterns, a pattern and a number).
- **anything-text** — what the provided `anything` matches (newlines; `/.*/` differs from `[\s\S]*` on 90 of 121).
- **backref-label** — inside ONE literal with two groups of one name, does `\k<h>` read PCRE's first set group or the label (last mention)? (REF4: 2/2/2 of 341, 6/6/6, 4/4/4 across the three readings.)
- **zero-in-sequence** — what `0` names for a condition inside a sequence ("so far" vs the whole match).
- **group-truth / pass-table** — re-stated from rev 25.1; not entailed by the 11-18 rulings (RS2).

## EVIDENCE AND COMMANDS

- PREMISE: predspec251's engine re-run, byte-identical to its committed outputs (forward 25 of 25; sabotage 20 of 25).
- `docs/dev/lanes/predspec26_evidence/` (own CLAUDE.md, the RULE-AS-CODE predicate table beside the draft sentences;
  no tokenizer exists, said so): `(cd $PCREC_TMPDIR/scratch/predspec26 && timeout 900 python3 -I -B
  <worktree>/docs/dev/lanes/predspec26_evidence/predspec26_model.py)` -> CHECKS 111 of 111 OK
  (`predspec26_model.out`). Sabotages s1-s13 each alone FAIL at least one check (`predspec26_sabotage_each.out`:
  109, 109, 109, 110, 110, 109, 105, 107, 110, 107, 110, 110, 110 of 111); all together 83 of 111
  (`predspec26_sabotage.out`).
- Controls: libpcre2-8 10.46 via `rxmodel_evidence/pcre2h.py` (run, not read); Python `re` for the shown Python run
  (P2). RS1: nested-complement ENTAILED (one-pattern vs committed, 81 of 364 differ, first `71`).
- Not reached by a sabotage (stated): H5, REF4, OQ1-OQ3, CX4 are witnesses for readings and questions, not rulings.
- Greps: the commands in the EXAMPLES THAT MOVED table, run on rev 25.1 and on rev 26.
