# predspec251 report: predicates_draft.md rev 25.1 (review r43's fixes)

Lane predspec251 (2026-11-18, opus; DESIGN ONLY, no build go). Branch `lane/predspec251`, cut from main @ 59372876c.
Subject: `docs/design/predicates_draft.md` rev 25 -> rev 25.1, head line "rev 25.1: review r43's fixes; NOT STABLE
pending the owner's answers". Also `docs/design/rx_module.md` (a superseded banner, nothing else) and the evidence
directory `docs/dev/lanes/predspec251_evidence/`.

## STATE AT HANDOFF

- STATE: done. Every FIX-NOW group A-J of the manager's dispositions applied; group K and RULING-5 listed as PLAN
  (§R.0 non-goals), not done.
- Rulings file `docs/dev/lanes/predspec251_rulings.md`: empty at every re-read (before each commit and this report).
  Last R-n applied: empty.
- STOPS: none. Every verifier-confirmed witness reproduced (EVIDENCE AND COMMANDS); the premise held; no fix needed a
  choice between two readings the dispositions did not settle (each new reading is marked THE DRAFT'S READING and, where
  it decides an answer, listed under an owner question).
- RUNS NOT RUN: none. All runs were small single-process scripts done before the 01:00 timing window
  (`scripts/boxqueue status`: box free, the kit's jobs not before 01:00).
- Draft size: 8,020 lines (967,407 bytes) before, 8,256 lines (1,009,611 bytes) after (`wc -lc`).

## FINDINGS APPLIED

One row per id of review r43's by-id completeness list (48). "§" = the draft's section; "PART" = rev 25.1's evidence.

| id | group | applied where |
|---|---|---|
| RULING-1 | A | R.1.13 "WHAT A NUMBER NAMES IN A CHAIN: HIS POSITION, NOT A RULING"; §R.8's RULED list item moved; §R.9 row; §R preamble mark; §R.11 row 64 |
| RULING-2 | A | R.1.13: the manager's consequence marked A READING IN CONFLICT, witness (2); **number-names** |
| RULING-3 | B | R.1.4 and R.1.14 (4): "an `&` operand (EITHER side)"; §R.9 row; §R.11 row 76 (the correction entry) |
| RULING-4 | G | R.1.14 COUNTS: the sentence separating compile-time rx alternations from match-time arrays; **value-is-pattern** |
| RULING-5 | G | PLAN: §R.0 non-goals and the COUNTS mark list the single-value places for rev 26 |
| RULING-6 | I | §R.5 F2's reason replaced (reference, not existence) |
| RULING-7 | I | §2.7 mark; §R.9's marked list now includes §2.7 |
| RULING-8 | I | §R.11 header ("status in rev 25.1"); rows 14, 28, 29, 57 (row 69 revises it), 64 |
| RULING-9 | I | §R.0 heading and the G24-1 term list extended; §0 status "rev 25.1" |
| RULING-10 | F | §5.4 THE ONE OPERATOR TABLE (every operator has a level) |
| SIMULATE-1 | D | R.1.14: the old witness withdrawn (PART D D2), the discriminating witness (D1); **product-order**; sabotage s1 |
| SIMULATE-2 | D | position table GROUP NAME row: plain alternation, renumbered (THE DRAFT'S READING); PART D D3, D5; sabotage s2 |
| SIMULATE-3 | D | R.1.14: the removal unit (PART D D4); the ZERO-members row |
| SIMULATE-4 | I | R.1.7: the backreference sentence corrected; **backref-across-parts** (PART I I1) |
| SIMULATE-5 | A | R.1.13 witness (4) (PART A A1); **number-names** |
| SIMULATE-6 | B | R.1.4: a hole in a filter operand classified after expansion, THE DRAFT'S READING; **hole-in-filter** (PART B B2, three readings) |
| SIMULATE-7 | I | R.1.9 PART H's first-try list [`0`, `12`] (PART I I2); §R.8 STOP RULE note |
| SIMULATE-8 | J | evidence: sabotage rows s1 (product order), s2 (joined copies), s3 (parse clause), s4 (order on the parser); D5 and J9 checks; `x + y` labelled a reading |
| MODECLOSURE-1 | C | R.1.7: "at ONE depth only" mark with the two-depth witness (PART C C1) |
| MODECLOSURE-2 | C | R.1.9 (two places), §2.6 "exactly two ways" and THE ITERATION'S OWN VALUES, §R.8 hits-pass and some-own rows marked; **hit-carry** |
| MODECLOSURE-3 | A | R.1.13 witness (3) (PART A A2) |
| MODECLOSURE-4 | H | R.1.13 PATHS reading (d); **path-and-ambiguity** |
| MODECLOSURE-5 | H | R.1.13 PATHS reading (b), the reading point |
| MODECLOSURE-6 | I | R.1.7 ARRAY-SLOT: setting order, not text order |
| FIXINDUCED-1 | E | §R.2 selectors `/pcrec\.test\.never/`, `/pcrec\.test\..*/`; §7.1 `/compare\.width\..*/`, `startsWith("pcrec.dead.")`, `"pcrec.label.unset"` |
| FIXINDUCED-2 | E | §7.1 table: `pcrec.` head row, `empty.search` trigger, `compare.width` MOVED, `compare.looped` note, new rows `label.numbered` and `match.never` (the can-never-match warning named) |
| FIXINDUCED-3 | I | §0.1 L57 (SAME), §8 `min`, §13 O58 (item and the RESOLVED list), the ruling-table row `min` is 0 or 1 |
| FIXINDUCED-4 | I | §12.12 E-CTX-2 (no error, the warning, three modes hand-worked) and its four readers (§12 head paragraphs, §12.12 header) |
| FIXINDUCED-5 | B | §0.1 L71 and §11 re-derived (both operands filter roles; PART B B1); R.1.14 (4) |
| FIXINDUCED-6 | G | **value-is-pattern** (folds plus-operands and hole-member-kind; the verifier's PARTLY: a member KIND, not "no row") |
| FIXINDUCED-7 | I | R.1.7: `[k]` indexes settings (THE DRAFT'S READING); §5.4 `$` row marked; spellings item 16 |
| FIXINDUCED-8 | C | R.1.7 INSIDE THE BODY mark with the 84 / 134 counts (PART C C2, C3); **hit-carry** |
| FIXINDUCED-9 | F | R.1.14 readings (b) statement end, (c) call/index after an operand; §5.1 mark; spellings item 19 |
| FIXINDUCED-10 | F | §5.4 THE ONE OPERATOR TABLE; §2.2 mark |
| FIXINDUCED-11 | A | R.1.13 witness (2) (PART A A3) |
| FIXINDUCED-12 | B | R.1.4 (as RULING-3) |
| FIXINDUCED-13 | H | R.1.13 PATHS readings (a) last-mention uniqueness, (e) unreferenced read-out |
| FIXINDUCED-14 | D | R.1.14 LEGAL (THE DRAFT'S READING); duplicate-name copy legal; PART D D3 |
| FIXINDUCED-15 | C | §2.6 ground marked stale; §0.1 L18; the nullable-argument refusal as a fifth error-or-warning candidate inside **hit-carry** |
| FIXINDUCED-16 | K | PLAN: §R.0 non-goals (the place table, rev 26's skeleton; the three other forms NOTED with triggers) |
| CENSUS-1 | E | as FIXINDUCED-1, all 7 spans (§R.2 two, §7.1 three, §0.1 L15, §12 one) |
| CENSUS-2 | H | R.1.13 PATHS reading (c); §0.1 L64 mark |
| CENSUS-3 | F | §5.4: `+ - * %`, `${ }`, `$` rows marked; the operator table |
| CENSUS-4 | F | R.1.14: the record's clause restored as a constraint on the spellings review; spellings item 17; PART J J9, sabotage s3 |
| CENSUS-5 | D | position table PATTERN row (false "any pattern is legal" replaced); rows for `\k<${n}>`, `\Q..\E`, zero members, part of a name; value in a pattern position under **value-is-pattern** |
| CENSUS-6 | I | R.1.14: the two senses of "value position" stated |
| CENSUS-7 | I | §4.3 SEQUENCE RULE mark |
| CENSUS-8 | F | `rx_module.md` superseded banner (its `€` line's parse stated); R.1.11 note on `J & C ? J & M : fail` |

## WHAT MOVED

Answers the draft printed that change: PART H's first-try hit list on `x300 12` ([`00`, `12`] -> [`0`, `12`], verdict
unchanged); §0.1 L57 (DIFFERENT: ERROR -> SAME, rev 25's min-values already decided it); §12.12 E-CTX-2 (compile error
-> no error, no match on `a12`, the can-never-match warning; rev 25's hole-reading already decided it); `/\b\d+/ &
/\d+/` (rev 25's text made it compile; rev 25.1: the operand-context error again, "an `&` operand"). Statuses that
move: "numbers name the nearest pattern's groups" from RULED to his position + a reading in conflict; the product's
order from "answer-free" to an answer-deciding reading; the PATTERN row's removal column. Questions: rev 25's
**numbered-duplicate**, **sequence-numbers** -> **number-names**; **plus-operands**, **hole-member-kind** ->
**value-is-pattern**; new **hole-in-filter**, **hit-carry**, **product-order**, **path-and-ambiguity**,
**backref-across-parts**.

## DRAFT READINGS ADDED

21 readings added (each marked THE DRAFT'S READING in the text); 14 decide answers and 4 decide parses; each of
those 18 is listed under an owner question (the parse readings under the spellings list, which the owner reviews):

| # | reading | where | decides answers? | asked as |
|---|---|---|---|---|
| 1 | a hole inside a filter operand is classified after expansion (the operand-context error) | R.1.4 | yes | **hole-in-filter** |
| 2 | an `&` inside a hole keeps both operands filter roles (L71 kept) | R.1.14 (4) | no: follows from the correction (verifier V2) | — |
| 3 | inside an `occurrences` argument, before its group, the previous hit's value (R.1.7's text, now labelled) | R.1.7, R.1.9 | yes | **hit-carry** |
| 4 | copies differing in a group name: plain alternation, renumbered | position table | yes (compiles or not) | **product-order** |
| 5 | part of a group name is the GROUP NAME row | position table | no | — |
| 6 | `\k<${n}>` is a compile error | position table | yes | **backref-across-parts** |
| 7 | inside `\Q..\E` `${` is text | position table | yes | spellings (§11's `$\{` rule) — answer only on a literal `${` |
| 8 | zero members remove the literal | position table | yes | **product-order** |
| 9 | an illegal member in a PATTERN position is a compile error of the whole | position table | yes | **product-order** |
| 10 | a pattern-valued member list in its alternation's order | R.1.14 | yes | **product-order** |
| 11 | legal = the language's syntax; a module refusal is not a removal cause; a duplicate-name copy legal | R.1.14 | yes | **product-order** |
| 12 | the removal unit is the whole literal's copy | R.1.14 | yes | **product-order** |
| 13 | postfix operators stack | R.1.14 (a) | parse | spellings item 19 |
| 14 | a statement ends before `NAME :=` | R.1.14 (b), §5.1 | parse | spellings item 19 |
| 15 | `(`/`[` is a call or index only after an operand | R.1.14 (c), §5.1 | parse | spellings item 19 |
| 16 | the operator table's unruled levels (call/field/index; prefix; `* %`; `+ -`) | §5.4 | parse | spellings item 19 |
| 17 | `[k]` on the array form indexes settings | R.1.7 | yes | spellings item 16 |
| 18 | "ambiguous" = the last mention is not unique; judged at the reading point | R.1.13 (a), (b) | yes | **path-and-ambiguity** |
| 19 | a binding's `.` legal in a value position (`alt.x[1]`) | R.1.13 (c), §0.1 L64 | no (keeps the existing row) | listed in **path-and-ambiguity**'s readings |
| 20 | `aa.h` with two mentions is the last mention's | R.1.13 (d) | yes | **path-and-ambiguity** |
| 21 | an unreferenced shared name reports the left side's value | R.1.13 (e) | yes | **path-and-ambiguity** |

## OWNER QUESTIONS LEFT

New or re-cut in rev 25.1 (§R.8 (b)):
- **number-names**: what a label number names on a composed pattern (sequence, hole, `|`, atomic, `occurrences`, a
  postfix operand, a labelled part) and on a group whose name is shared.
- **hole-in-filter**: a hole carrying an edge assertion inside a filter operand: the filter's error, or does the
  assertion cross the border there too?
- **hit-carry**: does a condition inside an `occurrences`/`hits` argument, before its group, read the previous hit's
  value? (Also: is the nullable-argument refusal a fifth error-or-warning candidate?)
- **product-order**: the cartesian product first slowest or first fastest; with what "legal" means and what is removed.
- **value-is-pattern**: is a match value a one-member pattern (in a hole, as `&`'s left operand, as `+`'s operand), and
  what a wrong-kind member does in a value position.
- **path-and-ambiguity**: what `aa.h` names with two mentions or a branching inside, and what an unreferenced shared
  name reports.
- **backref-across-parts**: what a part's backreference reads once the parts are spliced.
Kept from rev 25's §R.8:
- **quantified-condition**: what a postfix quantifier does to a condition.
- **label-mark**: which single form sets a label in the rx module.
- **lookahead-labels**: whether a lookahead's labels are visible after it.
- **complement-place**: where `!B` may stand; is a lone `!B` an error.
- **nested-complement**: a `contains` argument filtering paths like a program.
- **group-truth / pass-table**: group questions over the pass table.
- **atomic-spelling**, **options-spelling**, **conditional-spelling**, **every-pass-spelling**: spellings to the review.
- **sql-picture**: the manager's restatement, flagged.
- **repeated-means**: the manager's ruling, owner told.
- the spellings list (items 1-19; 16-19 new in rev 25.1).

## EVIDENCE AND COMMANDS

All from `$PCREC_TMPDIR/scratch/predspec251` (= `/var/tmp/pcrec-pcrec/scratch/predspec251`), W = the worktree.

PREMISE (byte-identical; held):

    timeout 900 python3 -I -B W/docs/dev/lanes/predspec25_evidence/predspec25_model.py > fwd25.out
    cmp fwd25.out W/docs/dev/lanes/predspec25_evidence/predspec25_model.out      # IDENTICAL; CHECKS: 42 of 42 OK
    PREDSPEC25_SABOTAGE=1 timeout 900 python3 -I -B .../predspec25_model.py       # CHECKS: 29 of 42 OK (13 FAILED, as the review lists)

THE NEW EVIDENCE (`predspec251_evidence/`, committed output `predspec251_model.out`, all-sabotage output
`predspec251_sabotage.out`):

    timeout 900 python3 -I -B W/docs/dev/lanes/predspec251_evidence/predspec251_model.py > fwd.out   # 25 of 25 OK
    PREDSPEC251_SABOTAGE=s1 ...   # 24 of 25: D1 product order FAILED
    PREDSPEC251_SABOTAGE=s2 ...   # 24 of 25: D5 joined copies compile FAILED
    PREDSPEC251_SABOTAGE=s3 ...   # 24 of 25: J9 (item SEQ ",")* SEQ item FAILED
    PREDSPEC251_SABOTAGE=s4 ...   # 22 of 25: J9 x+ | y, x + y, x * y FAILED
    PREDSPEC251_SABOTAGE=1  ...   # 20 of 25 (s4's order parser replaces the one s3 sabotages)

Witnesses reproduced (verifier's numbers; each matches): A1 SIMULATE-5 (distributed `3x`, `3y` HOLD; 1 = A's `3y`
FAILS; 1 = B's `3x` FAILS); A2 MODECLOSURE-3 (literal `3,7` HOLDS / `7,3` FAILS; hole the reverse); A3 FIXINDUCED-11
(consequence `21` HOLDS; name = number: error); B1 FIXINDUCED-5 (filter reading `xa` HOLDS, FIND-ALL `xa xa xb`
[`xa`@0, `xa`@3]; spliced `x(?:^a)` FAILS / FAILS / []); B2 SIMULATE-6 (three readings; crossing `34`@4 vs
stretch-alone `12`@1 on `a12 34`); C1 MODECLOSURE-1 (`7;,3;,` engine HOLDS, libpcre2 FAILS, SEARCHED `7;,`@0); C2
FIXINDUCED-8 (WHOLE 84; SEARCHED 84 by stretch, 134 with labels; FIND-ALL 84 / 134; engine = libpcre2 0 rows); D1
SIMULATE-1 (slowest x = `1`, y = `23`; fastest x = `12`, y = `3`; 8 / 0 / 0 of 364); D2 (tried lengths slowest [2, 3,
2, 4, 3, 2, 3, 4, 3, 4], fastest [2, 3, 2, 3, 4, 3, 2, 4, 3, 4]); D3 SIMULATE-2 / FIXINDUCED-14 / CENSUS-5 (libpcre2
refusals: the `(?|` name join, also under `(?J)`; `(?<h>\d)(?<h>\d)`; `(?<=(?:\d+))x`; `(?<=(?:\d|\d+))x`;
`a|\d{5,2}`); D4 SIMULATE-3 (`(?!)` vs `a|(?:(?!))`); I1 SIMULATE-4 (`abba` HOLDS, `abbb` FAILS; splice `733` FAILS,
`737` HOLDS; B alone `33` HOLDS; without `(?J)` refused); I2 SIMULATE-7 ([`0`, `12`] vs [`00`, `12`]).

LESSON 1 (parser predicates beside sentences): the table is in `predspec251_evidence/CLAUDE.md`; every predicate of the
expander's tokenizer/parser (longest first; the binary-after-`+`/`*` rule; `starts_operand` excluding `SEQ`; postfix
stacking; statement end; `&`'s condition-only right operand; dotted names) has its draft sentence or is labelled an
engine LIMIT/shortcut that decides nothing.

WITHDRAWN-TERM SWEEP (review lesson 3). Command, over the whole draft, after the edits:

    grep -c -- TERM docs/design/predicates_draft.md
    grep -n -- TERM docs/design/predicates_draft.md | awk -F: '$1>40 && $1<S16'   # S16 = the line of "## 16."

| term | total hits | outside the head/§16 | disposition of every live hit |
|---|---|---|---|
| right side of `&` | 6 | 6 | all inside the rev 25.1 correction text or R.0's term list |
| nearest pattern | 6 | 5 | all marked (preamble, R.1.13, §R.8, §R.9, R.0 list) |
| answer-free where run | 3 | 3 | R.1.14 mark, §R.9 row, R.0 list |
| already reads it | 3 | 3 | R.1.7 mark, §R.9 row, R.0 list |
| one entry per iteration | 2 | 2 | §5.4 row marked; §4.3's reference marked |
| edge-assertion error (lower) | 18 | 18 | hole readers marked (§2.7, ruling-table row, §12 x4, §13 decision (34), §R.9); the rest are set positions (enumerate, `@assert`, libraries, the role table, §12.12 head), still live; §13's rev 7 entry is dated history |
| EDGE-ASSERTION ERROR | 13 | 13 | set-position rows (L9, L10, L12, L14, §11 (3), (4)) live; hole readers marked (L8, R.1.14, §R.9, §11 REV 25 head) |
| E-CTX-2 | 9 | 8 | every reader marked; the remaining are the case's code line and R.0/§R.9 lists |
| is 0 or 1 | 6 | 6 | L57, ruling-table row, §8, §13 O58 (item head and RESOLVED list) marked; one in an old changelog entry |
| one-literal program | 7 | 7 | `empty.search` row marked; the other six are G3 (PCRE compatibility), a different rule, live |
| SEQUENCE RULE | 5 | 4 | §4.3 marked; §16.1 copy is the record |
| no concatenation operator | 3 | 3 | §2.2 marked; §2.5 under its REV 25 heading mark |
| exactly two ways | 2 | 2 | §2.6 marked |
| plain search | 4 | 4 | R.1.9 marked (two), §R.8 |
| empty-match rule's kind | 3 | 3 | §2.6 marked (two), §R.8 |
| any pattern is legal | 2 | 2 | the table row's replacement text, R.0 list |
| `test\.never/` unprefixed | 2 | 2 | inside the §R.2 mark |
| `"compare.width"` | 1 | 1 | inside the §7.1 mark |
| `startsWith("dead.")` | 2 | 2 | §0.1 L15 and §12 marked |
| `"label.unset"` | 0 | 0 | re-spelled |
| ERROR in a predicate program | 1 | 1 | §0.1 L18 marked |
| **numbered-duplicate** / **sequence-numbers** | 4 / 5 | 3 / 4 | each in a "replaced by number-names" mark or the rev 25 changelog |
| **plus-operands** / **hole-member-kind** | 7 / 4 | 6 / 3 | each in a "folded into value-is-pattern" mark or the rev 25 changelog |

Files: `docs/design/predicates_draft.md`, `docs/design/rx_module.md`, `docs/dev/lanes/predspec251_evidence/`
(`CLAUDE.md`, `predspec251_model.py`, `predspec251_model.out`, `predspec251_sabotage.out`), this report, and the lanes
history index line in `docs/dev/history/claude_md/docs__dev__lanes.md`. Review subject: COND-FAMILY's last entry
(the manager's correction, 2026-11-18) read, not edited.
