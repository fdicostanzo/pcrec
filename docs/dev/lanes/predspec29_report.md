# Lane predspec29 — report (2026-11-19, opus; DESIGN ONLY)

Deliverables: `docs/design/predicates_draft.md` REVISION 29 (head line "rev 29: the owner's six rulings of 2026-11-19
folded (padded-order, flags-scope, class-order, dollar-diagnostic, number-edges, same-name-count); NOT STABLE pending
the owner's answers"); evidence `docs/dev/lanes/predspec29_evidence/` (model, output, sabotage output, CLAUDE.md); an
index line in `docs/dev/history/claude_md/docs__dev__lanes.md`. Branch lane/predspec29, cut from lane/pred-rev28 @
340117775; not merged, not pushed. Draft size (`wc -lc`): 9,973 lines / 1,324,481 bytes before, 10,146 / 1,359,069
after . A FOLD revision: no restructuring. Nothing under `src/`, `cli/`,
`lib/`, `memfn/`, `tests/`, `scripts/`; COND-FAMILY.md, plan.md, decisions.md, `predicates_future.md`, `docs/dev/pred/`
NOT edited; no `make` other than `make -s test-plan-lint` (PASS, "checks failed: 0"); no box job.

## STATE AT HANDOFF

STATE: complete.
OWED: none

- PREMISE TEST: (1) draft line 3 said "rev 28.1": HELD; (2) `predspec281_model.py` and `predspec28_model.py` re-ran
  BYTE-IDENTICAL to their committed `.out` (`cmp`, rc 0 each): HELD; (3) the record's last entry at the cut was "2026-11-19
  OWNER, on building rx from many bindings": HELD. STOP RULE: nothing stopped; no record line contradicted the brief.
  NOTE: lane/pred-rev28 has since gained a commit (9cc933e2c, "owner on numbers as strings over an ordered symbol
  set") after this lane's cut; it is outside the fold range and was not read into the draft.
- RULINGS FILE `docs/dev/lanes/predspec29_rulings.md`: EMPTY at every check (before each commit and before this
  report; last check 2026-11-19 12:52). No entry applied.
- Evidence: CHECKS 25 of 25 OK (6 are the helper's selfchecks); t1-t19 each alone CAUGHT, no traceback; all at once
  7 of 25.

## RULINGS FOLDED

Each quoted verbatim from the record; every changed passage marked "[REV 29 ...]".

- **padded-order** "i agree with your lean": §2.7 (the body, the CONDITION confirmed, rev 28.1's lazy statement
  withdrawn, the body's stated behaviour), A28, A35, §R.8 row ANSWERED, §R.9, §R.7, §R.11 row 158.
- **flags-scope** "i agree with your inherit table excepting that U should also not be inherited. one could make a
  case that only i should be inherited" (the second sentence an observation): R.1.15 header (runs per inline flag),
  R.1.14 (1), R.1.0 MATCH VALUE row, T12, §11, §0.1 L32, A29, A30, §R.8 row ANSWERED, §R.9, §R.11 row 161.
- **class-order** "class-order: longest": §5.5 RULE and STATUS, R.1.16's lift paragraph, T8, §0.1 L26, the §12.10
  example comment, A31, §R.8 row ANSWERED, §R.9, §R.11 row 164.
- **dollar-diagnostic** "i don't want to spend too much time on the warning. the form $x & .. should just get a
  warning": §R.2 dollar-condition row (the warning; the read-stands-for-its-group proposal DROPPED, §5.2 unchanged),
  §0.1 L28, §4.1 and §2.5 marks, A1, A21, A32, the hit-list GAP sentence, §R.8 rows (dollar-diagnostic ANSWERED,
  dollar-warning reopened-and-closed), §R.9, §R.11 row 165. Name, wording and silencing: left as THE MANAGER'S CALL,
  with the placeholder `pcrec.dollar.filter`, selected like every warning (§7.1).
- **number-edges** "number-edge: nothing": R.1.16 THE NUMBER DOMAIN (the reading becomes the ruling), R.1.15 (2)'s
  pointer, A33, §R.8 row ANSWERED, §R.11 row 166.
- **same-name-count** "same-name-count: scoped" (backreferences only; the "(and `$h`)" withdrawn): R.1.13 REFERENCES
  (2) narrowed, R.1.15, A30, A34, §R.8 row ANSWERED, §R.9, §R.11 rows 167-168.

## MANAGER READINGS TESTED

| # | reading | verdict | run or record line |
|---|---|---|---|
| 1 | any-length-first = fill-each-string for every argument ordered by length | NOT SUPPORTED as worded: every longest-first argument (5, n = 2, 3) and the dense shortest-first ones 0 / 0 / 0; a SPARSE shortest-first one parts: `1\|0119` n = 2 0 / 10 / 10 of 1,365 x 2; `/${padded(/1\|0123/, 2)}/` SEARCHED `x0123` body `0123`@1, fill `01`@1 | PART PO; t1 |
| 2 | unbounded lazy `\d+?` under any-length-first (the CONDITION) | SUPPORTED: 0 / 0 / 0 (n = 2, 3; `\d+` too). Rev 28.1's 0 / 160 / 160 came from its hand reduction `(?:[01]{2,}\|[01]{2})` whose `{2,}` is greedy; with `?` kept 0 / 0 / 0; the body run as written 0 / 0 / 0 of 364. The ruling holds | PART PO; t2 |
| 3 | flags reach both sides of an `&` inside a hole; program-level `&` sides keep their own | SUPPORTED (as a reading; folded as THE DRAFT'S READING, still a confirm): REACH = plain hole 0 / 0 / 0 of 1,555, own flags 4 / 52 / 52; `m`, `s` flip, `x`, `n`, `U` agree either way; `/(?i)ab/ & /a./` WHOLE `AB` FAILS | PART FF; t5 |
| 4 | the same for a condition's set and a filter-role argument in a hole | SUPPORTED: `/(?i)x${/(?<w>\w\w)/ & (w: /ab/)}/` `XAB` HOLDS; `/(?i)x${quoted(/ab/)}/` `x"AB"` HOLDS (own flags FAIL) | PART FF; t6 |
| 5 | inheritance is transitive | SUPPORTED: B := /ab/, A := /x${B}/ at `/(?i)${A}/` WHOLE `XAB` HOLDS | PART FF; t7 |
| 6 | a binding computed ALONE reads its own flags | SUPPORTED (a reading): `enumerate(/ab/)` = [`ab`], at `(?i)` four strings | PART FF; t8 |
| 7 | not-inherited flags are the inserted rx's defaults at any depth; the three flips | SUPPORTED: `(?n)` `xaa` HOLDS; `(?U)` SEARCHED `xaaa` `xaaa`@0; `/a b/` keeps its space at `(?x)` (depth one and two); `xx` `x ` HOLDS | PART FF; t4 |
| 8 | class-order needs no tie rule | SUPPORTED for match answers (20 shuffles 0 / 0 / 0, two lifts); the ARRAY interface still sees an order (`.index`): new question **class-index** | PART CO; t9 |
| 9 | `(3\|9) + \d` nests | SUPPORTED by the ruled words; `(3\|9)` cannot show it (0 / 0 / 0); `(1\|9) + \d` does: nested `x11` `1`@1, across `11`@1, 0 / 750 / 1,404 | PART CO; t10 |
| 10 | two classes in one lift; a class under a quantifier | candidates PART: `\d + \d` C1 vs C2 0 / 776 / 1,816 (C3 = C1); lazy `\d{1,2}? + 1` Q1 vs Q2 0 / 2,797 / 3,230; agree on `\d\d + 1` and greedy `\d{1,2} + 1`: OWNER QUESTION **class-positions** | PART CO; t11 |
| 11 | equal strings from different members are one result | SUPPORTED: `\d * 0` = [`0`], = `/0/` 0 / 0 / 0 | PART CO; t12 |
| 12 | `J` has no effect across a hole; the inner `\k<h>` | SUPPORTED: WHOLE `a-bb` HOLDS, `a-ba` FAILS (rev 28.1 the reverse) | PART FF; t19 |
| 13 | an inserted literal's numbered references are its own | SUPPORTED: `/(a)-${/(b)\1/}/` WHOLE `a-bb` HOLDS (text paste: `a-ba`) | PART FF; t19 (one check with 12) |
| 14 | a literal `% 0` meets the "can never match" diagnostics | NOT SUPPORTED by their WORDING: `match.never` (§7.1) names an edge assertion and a product with every combination removed; neither reaches `${$y % 0}`; the constant lift `${\d % 0}` has zero values, R.1.0's `(?!)` cell, no warning. A GAP; no rule made | PART NE; §7.1 row text |
| 15 | `$h` the last mention beside `\k<h>` the outer | SUPPORTED: `/(?<h>a)-${q};${$h}\k<h>/` WHOLE `a-b;ba` HOLDS / `a-b;ba`@9 / [`a-b;ba`@0, `a-b;ba`@14] | PART SC; t15 |
| 16 | the dollar warning fires wherever `$x & S` is written | SUPPORTED: fires on both forms, silent on `(x: S)`; the right one equals its suggestion 0 / 0 / 0 of 364 | PART DD; t14 |
| T-a | isodate x3, two part labels | inside: bare `year` = the third use (last mention) `2023` / `2023` / [`2023`, `2026`]; paths read their parts. SURPRISES: (i) unlabelled use first -> bare `year` reads END_DATE's; (ii) outside a binding, an unlabelled SEQ part exports nothing while the same pattern through a hole does | PART TA; t16 |
| T-b | private labels doing work | three: one separator per date (`_s`), a condition's subject (`_v`), matched quotes (`_q`); none reaches the caller; every mode run | PART TB; t17 |
| T-c | `any_case` vs `/(?i:${rx})/` | EQUAL in every mode for plain and filter-role arguments under REACH (0 / 0 / 0 of 781 each); differs for a written `(?-i)` 3 / 246 / 249. Not closed here | PART AC; t18 |

## ANSWERS CHANGED

| earlier (his words or the draft's) | where | becomes | follows / reading |
|---|---|---|---|
| two-case `padded` body exact-first; rev 28.1 "the argument's order" | §2.7, A20 | any-length first; `x000` on the mixed argument `00`@1 -> `000`@1 | FOLLOWS padded-order |
| rev 28.1 "a lazy infinite argument needs exact-first" | §2.7 | WITHDRAWN (hand-reduction error) | READING corrected by run |
| "`n`, `U`, `xx`, `J` propagate like `i`"; m1 `x` | R.1.15, R.1.14, §11, L32 | not inherited: `(?n)` no error, `(?U)` `xaaa`@0, `(?x)` space kept, `(?xx)` ` ` HOLDS | FOLLOWS flags-scope |
| rev 28.1's `J` run (outer group) | R.1.15 | inner group, `a-bb` HOLDS | READING (12, 13) |
| an `&` operand / condition set / filter argument keep own flags (m2, 2026-11-18) | R.1.15, §R.8 | REACH (still a confirm) | READING (3, 4) |
| codepoint class order | §5.5, T8 | longest first per class position: `\d + 1` `x10` `1`@1 -> `10`@1 | FOLLOWS class-order |
| dedicated warning withdrawn; call 4 (read = group's rx) | §R.2, L28, A21 | a form-keyed warning; call 4 dropped | FOLLOWS dollar-diagnostic |
| number-edges THE DRAFT'S READING | R.1.16 | RULED; no answer moves | FOLLOWS |
| same-name-count THE DRAFT'S READING; REFERENCES (2) for `\k` | §R.8, R.1.13 | RULED for `\k<h>`; no answer moves | FOLLOWS |

## WHAT MOVED

RULED: the six. REVERSED / REPLACED / DROPPED (§R.9 rows): the exact-first body and "the argument's order"; the
propagate-like-`i` reading and m1's `x`; codepoint order for lifts; the dedicated warning's withdrawal and call 4;
m2 as flags-in-filter's reading; REFERENCES (2) for `\k` across a hole. WITHDRAWN: rev 28.1's lazy-infinite statement.

GREP COMMANDS (run over the draft before and after; every live site fixed or marked):

    for t in 'flags-scope' 'flags-in-filter' 'class-order' 'codepoint\|CODEPOINT' 'padded-order' 'two-case' \
             'dollar-diagnostic' 'dollar-warning' 'number-edges' 'same-name-count' 'propagate like'; do
      grep -n -- "$t" docs/design/predicates_draft.md | grep -v 'REV 29'; done

The remaining unmarked hits are history: the changelog entries of earlier revisions, §R.7's REV 28.1 block (preceded
by the new REV 29 block), §R.8's REV 28 / 28.1 lists and closed rows ("this row is the record"), §R.9's earlier rows,
§R.10's evidence lines, §R.11's earlier rows, and paragraphs whose own [REV 29] mark closes the same paragraph
(R.1.15 header, §2.7 THE ORDER, §11).

## DRAFT READINGS ADDED

- flags-in-filter: REACH (the inherited flags reach an `&`'s sides, a condition's set and a filter-role argument
  inside a hole; program level keeps its own), the manager's reading 3/4 SUPPORTED, still asked as a confirm.
- class-index: codepoint order kept for `enumerate`'s ARRAY interface only.
- T-a: an unlabelled pattern inserted through a HOLE exports its labels as the binding's own (from R.1.0's PATTERN HOLE
  row; used only to state surprise (ii)).

## OWNER QUESTIONS LEFT

- **class-positions** (new): two class positions in one lift (`\d + \d`: C1 longest overall vs C2 nested, 0 / 776 /
  1,816) and a class under a lazy quantifier (`\d{1,2}? + 1`: Q1 quantifier order kept vs Q2 one position, 0 / 2,797
  / 3,230); every mode in the §R.8 row.
- **class-index** (new): the order of a class's members in `enumerate`'s array (`.index`); codepoint vs undefined.
- **flags-in-filter** (confirm, reading now REACH).
- Still asked from before: plus-operands, construction-line (b) (and its finite half), other-holes, anything-text,
  zero-in-sequence, group-truth / pass-table, number-in-loop, hit-carry-depth, caller-ambiguous, not-test,
  condition-group, the conditional's spelling, the spellings review.
- For the manager (GAPS, not asked): a literal `% 0` draws no diagnostic (reading 14); T-a's two surprises; T-c's
  result for **any-case-body**; the dollar warning's name and silencing (placeholder `pcrec.dollar.filter`).

## EVIDENCE AND COMMANDS

- Premise: `(cd $PCREC_TMPDIR/scratch/predspec29 && timeout 900 python3 -I -B
  <worktree>/docs/dev/lanes/predspec281_evidence/predspec281_model.py > p281.out)` then `cmp` with the committed
  `.out`: rc 0; the same for `predspec28_evidence/predspec28_model.py`: rc 0.
- Forward: `(cd $PCREC_TMPDIR/scratch/predspec29 && timeout 900 python3 -I -B
  <worktree>/docs/dev/lanes/predspec29_evidence/predspec29_model.py > fwd.out)`; committed as `predspec29_model.out`;
  "CHECKS: 25 of 25 OK". Seconds.
- Sabotage: `PREDSPEC29_SABOTAGE=tN` for N = 1..19 each alone, then `=1`; `predspec29_sabotage.out`: every tN
  CAUGHT, tracebacks 0; all at once 7 of 25.
- Controls: libpcre2-8 10.46 via `../rxmodel_evidence/pcre2h.py` (run, never read; D181), python `re`. No PCRE2
  SOURCE fact was needed (every PCRE2 fact used is behaviour, run, including the `(?^)` / `(?-U:)` mechanics).
- Checks: `make -s test-plan-lint` PASS ("checks failed: 0"); pre-commit staged checks 52 passed.
- LIMITS (the evidence CLAUDE.md): an infinite argument's fill reference truncated to the subject's digits and length
  (hand-worked); an `&` in a hole spelt as capture + callout; the `any_case` primitive's SEARCHED/FIND-ALL order is
  the model's (§2.7 defines a set); the T-a visibility classifier is rule-as-code.
