# Lane predspec281 — report (2026-11-18 night, opus; DESIGN ONLY)

Deliverables: `docs/design/predicates_draft.md` REVISION 28.1 (head line "rev 28.1: review r52's fixes to rev 28, as
the predicate manager ruled them, and the owner's numeral-width ruling; NOT STABLE pending the owner's answers"); the
filed review `docs/dev/reviews/2026-11-18-r52-predspec28.md` (+ `2026-11-18-r52-predspec28/`: the five critics' texts
and `verify.md`, copied unchanged, with a CLAUDE.md; an index line in `docs/dev/reviews/CLAUDE.md`); evidence
`docs/dev/lanes/predspec281_evidence/` (model, output, sabotage output, CLAUDE.md). Branch lane/predspec281, cut from
lane/pred-rev28 @ 9b7503b6c; not merged, not pushed. Draft size (`wc -lc docs/design/predicates_draft.md`): 9,755
lines / 1,273,900 bytes before, 9,973 / 1,324,481 after. A FIX revision: no restructuring. Nothing under `src/`,
`cli/`, `lib/`, `memfn/`, `tests/`, `scripts/`, `.claude/` or `docs/dev/guide/` touched; COND-FAMILY.md and
`predicates_future.md` NOT edited; no `make` other than `make -s test-plan-lint` (PASS, "checks failed: 0"); no box job.

## STATE AT HANDOFF

STATE: complete.
OWED: none

- PREMISE TEST: `(cd $PCREC_TMPDIR/scratch/predspec281 && timeout 900 python3 -I -B
  <worktree>/docs/dev/lanes/predspec28_evidence/predspec28_model.py > fwd28.out)` re-ran BYTE-IDENTICAL to the
  committed `predspec28_model.out` (`cmp`, rc 0). STOP RULE: nothing stopped. No record line or run contradicted a
  RULING of the brief. One manager reading is NOT SUPPORTED by the draft's wording (call 4 against §5.2, below); per
  the brief it is reported with the wording change printed in the question, not applied.
- RULINGS FILE `docs/dev/lanes/predspec281_rulings.md`: re-read before each commit and before this report; LAST ENTRY
  APPLIED: R1 (numeral-width RULED canonical, an owner ruling after the brief; it changes disposition F). Applied in
  R.1.15 (2) (his words, the four-form worked example run in every mode, the scope counts), §R.8 (REV 28.1 RULED
  list; the numeral-width row marked ANSWERED), R.1.16 THE NUMBER DOMAIN, T12, A27, §R.9, §R.11 rows 153-154, the
  seven repeated `${$..}` brackets, the changelog, and the filed review's item F (marked SUPERSEDED IN PART).
  number-edges stays ASKED. His words are quoted from R1 (the record entries are on lane/pred-rev28 after the cut).
- Evidence: CHECKS 28 of 28 OK (6 are the helper's selfchecks); t1-t22 each alone CAUGHT; all at once 6 of 28.
- PROCESS CHANGES ACCEPTED BY THE MANAGER (for the manager to send to main; NOT applied here: `.claude/skills/` and
  `docs/dev/guide/` untouched), VERBATIM from `.coord/process.md` "Proposed changes":
  1. Skill section 3 (freeze), design mode: "When the launcher's fold range ends past the record AT the subject
     commit (a ruling delivered by a rulings file), copy the record from the branch head up to the fold range's last
     entry and record the difference as a FREEZE NOTE; post-commit entries go to the ruling lens only." (r52: three
     ${@y} entries.)
  2. Simulate lens drill: "a macro body proved equal to a definition AS A SET is drilled in SEARCHED and FIND-ALL
     with a prefix pair among the argument's members" (r52 TABLES-3: WHOLE 0 of 137,257, SEARCHED 1,344 of 1,365).
  3. Mode-closure lens drill: "a FLAG rule is run with every PCRE inline flag (i m s x xx n U J), `#` under x, and
     an `&` inside the place" (r52 E).
  4. Simulate lens: "an evidence enumerator's ORDER is checked against PCRE priority order on an alternation under a
     counted repeat" (r52 TABLES-4).
  (review.md's "Lessons for the guide (proposed)" 1-3 are the same as 2-4.)

## DISPOSITIONS APPLIED

Every FIX-NOW of review r52, as ruled; each changed passage carries "[REV 28.1, review r52 X]".

- A (padded): §2.7 THE WIDTH FORM: "equals" limited to WHOLE (the 47,112 / 137,257 counts WHOLE-only); THE ORDER
  paragraph: THE DRAFT'S READING the argument's order (per-member fill, T5's words quoted); a body keeping it: the
  per-member alternation for a FINITE argument; for an INFINITE one NO single body found (greedy needs the two-case
  body reversed, lazy the body as written); asked **padded-order** (§R.8 row). A20, §R.11 rows 132/135, §R.9. Prefix
  pair run (PART PO). GENFORM-6: PLAN (§R.8 REV 28.1 block).
- B (T8/T9): T4 gets the ORDERED clause list (assertion looking outside: the edge-assertion COMPILE ERROR; infinite or
  over budget: UNDER CONSTRUCTION; enumerable: BUILT NOW); the same bracket on T8's and T9's STATUS cells
  (`left(/(?<=x)ab/, 1)` the error only). Non-regular rider re-listed in §R.8 GAPS. GENFORM-7: PLAN.
- C (unmarked readers): T8/T9 NEEDS; T8 STATUS first clauses; §2.5 RULE; §5.4 `+ - * %` row; A6; A4; R.1.15 (3),
  (11), (13), (7); R.1.0 MATCH VALUE `${@y}` cell; §13 (40) and O67; §11 ROLE TABLE row 8; A19.
- D: lift-order marked THE MANAGER'S READING m2, SUPPORTED, told as a reading (§5.5, T8, A24, R.1.15 (7), §R.8,
  §R.11 row 143); §5.5's "the greedy width first" corrected to PCRE PRIORITY ORDER; **class-order** new row; evidence
  enumerator in priority order against libpcre2 with `(?:a|ab){1,2}`; array product through it; BUDGET and interior
  lookaround/backreference REPORTED UNSUPPORTED by §5.5 (it gives no number and names only edge assertions);
  product-order CLOSED BY CONSEQUENCE (row marked; out of the asked list).
- E: §11 Literals sentence marked; "as text" limited (R.1.14 (1), §0.1 L32); `m`/`s`/`x` marked reading m1; THE
  DRAFT'S READING for `n`, `U`, `xx`, `J`, the branch carry (R.1.15 header, run); TABLES-8 wording fixed (§2.7
  `any_case`, A19); caseful-hole witness; **flags-in-filter**, **flags-scope** new rows; neither applied as a rule.
- F (as superseded by R1): numeral-width's true scope restated (counts per operation; two reads; intermediates;
  GENFORM-5 observation); then RULED canonical with his words and the worked example; **number-edges** THE DRAFT'S
  READING "outside the domain: nothing", asked with runs.
- G: §R.7's witness given its `(?J)`; language-level SN model (the error's offset); `\2` run; **same-name-count**
  framed against A9, the 2026-11-13 "inserted patterns' groups stay scoped" line, and E3's `(?J)`. GENFORM-9: PLAN.
- H: §R.11 rows 149-154 (the `${@y}` REQUEST/LEAN entry, the CSV QUESTION, the MANAGER CORRECTION, the r52 manager
  entry, his numeral-width lean and ruling); CSV reading in GAPS; outside-the-domain clause RULED (THE NUMBER DOMAIN,
  row 131); §2.4 LEAN RETIRED (domain-components removed as a gap); `${@y}` today a plain "not defined" compile error,
  THE MANAGER'S CALL 2 (R.1.15 (13), T21, R.1.0).
- I: §R.2 / A21 / §0.1 L28: the dedicated warning stays withdrawn; THE DRAFT'S READING (a read stands for its
  group's rx) run; **dollar-diagnostic** row (a confirm) with the §5.2 wording change PRINTED, not made.
- J: "the never-matching rx" at every unset-rule site (14 replacements + the `(?!)` gloss; owner quotes and the rev
  28 changelog untouched; `when`'s "matches nothing" kept); FIXIND-19 and the lookbehind value hole in GAPS.
  GENFORM-2: PLAN with spellings 22, 32.
- K: FIXIND-5 (`strlen($y)`, A26; §2.7 `length(S)` keeps its name); FIXIND-7 (T5 READ COMPOUNDS sentence, run);
  TABLES-5 (the under-construction-class row's SEARCHED/FIND-ALL marked illustrative); TABLES-6 (§2.7 corrected,
  HAND-WORKED); GENFORM-4 (§R.8 one-line row); GENFORM-8: PLAN; FIXIND-10/14 (separating witnesses: TT's table written
  by hand with t19; PW `0*` vs `0?` with t21; NW every-mode lines with t12; UN's spelling with t20).

## MANAGER READINGS TESTED

| reading | verdict | run or record line |
|---|---|---|
| call (1) T8/T9 ordered clauses | SUPPORTED | PART TT: hand-written table matched, t19 caught; no clause collides with enumerate's rule (§5.5's edge-assertion error) |
| call (2) `${@y}` a plain "not defined" error | SUPPORTED | T4 "UNDER CONSTRUCTION needs a DEFINED meaning" + his "not built or defined now" |
| call (3) product-order closed by consequence | SUPPORTED | PART PR: the first-slowest product = PCRE concatenation, 0 / 0 / 0 of 364 |
| call (4) a read stands for its group's rx (dollar-diagnostic) | RUN: SUPPORTED (sound: fires on 3 never-holding programs, silent on 2 that hold; PART DD). WORDING: NOT SUPPORTED by §5.2 ("an empty intersection from pure parts" at "NARROWING SITES"; a read is no pure part). Change printed in the question: "an empty intersection from pure parts, a read `$x` standing for its group's rx, is the warning" | PART DD; §5.2 |
| call (5) "the never-matching rx" | SUPPORTED | record: the `when` ruling's "It holds and matches nothing" names the empty string; PART UN spelling `(?!)` 0 / 0 / 0 of 1,365 |
| call (6) `strlen` placeholder | SUPPORTED | his padded sketch "strlen($y-1)" (record, 2026-11-18 width clarification) |
| padded-order (argument's order) | SUPPORTED as the reading T5 entails; the two-case body parts 0 / 4,416 / 4,416 of 9,331; infinite arguments: no single body | PART PO |
| class-order (codepoint) | the LEAN decides answers: codepoint vs descending 0 / 47 / 85 of 781 | PART CO |
| flags-in-filter | UNTESTABLE as a reading (no rule states it); both candidates run: (a) 6 / 78 / 78, (b) 0 / 0 / 0 of 1,555 | PART FF |
| flags-scope | the draft's reading (every flag, PCRE's scoping) run per flag; the text paste fails under `x` + `#` | PART FF |
| number-edges (nothing) | consistent with THE NUMBER DOMAIN's RULED clause; signed candidate run | PART NE |
| numeral-width (canonical) | RULED by R1; counts what it decides: `- 1` 3, `- 10` 30, `* 0` 9,990, `% 7` 9,990, `+ 1` 0, `* 3` 0 of 10,000 | PART NW, NC |
| I's reading | as call (4) | PART DD |
| FIXIND-7 sentence (per member) | SUPPORTED: `($y | "9") + 1` equals the compile-time copies in libpcre2, 0 / 0 / 0 | PART RC |
| R1 m1 (canonical at every step: two reads, intermediates) | SUPPORTED: a width rule would have to choose a's or b's (part on 4,995 of 45,150) or leave `($y - 1) + 1` no number; canonical chooses nothing | PART NW |
| R1 m2 (the `strlen` composition waits on construction-line (b)) | SUPPORTED: `padded`'s width lands in a count hole; a read there is T13 (UNDER CONSTRUCTION / OPEN) | R.1.16 T13; PART NC (its meaning if built) |

## ANSWERS CHANGED

- `/${padded(/\d{2,3}/, 2)}/` SEARCHED `x123`: `12`@1 (rev 28's body) -> `123`@1 (THE DRAFT'S READING); FIND-ALL `123
  12345` [`12`@0, `12`@4, `34`@6] -> [`123`@0, `123`@4, `45`@7]; WHOLE unchanged.
- `left(/(?<=x)ab/, 1)`: two classes -> the COMPILE ERROR only.
- `\d+ + 1`'s printed SEARCHED/FIND-ALL: defined -> ILLUSTRATIVE (WHOLE only defined).
- `/(?<x>\d+)-/ & ($x & <5)`: silent -> the empty-intersection warning (THE DRAFT'S READING, asked).
- `${@y}` today: "its class for the manager" -> a plain "not defined" compile error.
- §R.7's `(?J)` witness: as printed a COMPILE ERROR -> with `(?J)` HOLDS `3;x3` (answers as rev 28 printed them).
- numeral-width RULED canonical: NO printed answer moves (canonical was the draft's reading; A27).
- `$y % 0`, a negative result: none printed before; THE DRAFT'S READING nothing (asked).

## WHAT MOVED

RULED (owner): numeral-width. Manager's calls applied: 1-6. Closed: product-order (by consequence). Marked as the
manager's readings: m1 (flags), m2 (lift-order). WITHDRAWN/NARROWED (§R.9 rows): the two-case body's equality (to
WHOLE), "holds for `+` only", "UNTESTABLE beyond that statement", domain-components, "the greedy width first",
lift-order as a call, "PLAIN pattern arguments", "Only the comparison is ORDER-SENSITIVE", the two-class operand,
`${@y}`'s open class, the unset wording, `length($y)`'s name.

## DRAFT READINGS ADDED

padded-order (the argument's order); class-order (codepoint, the LEAN now deciding); flags-scope (every flag
propagates; under `x` the inserted literal parsed on its own, a `#` comment ending at its end); number-edges
(outside the domain: nothing); dollar-diagnostic (a read stands for its group's rx); read compounds (per member,
in the compound's order); same-name-count (scoped).

## OWNER QUESTIONS LEFT

Each is a §R.8 row with its definition and runs in WHOLE / SEARCHED / FIND-ALL per candidate:
- **padded-order**: the order of `padded(rx, n)`'s strings; reading: the argument's (`123`@1) vs the body's (`12`@1).
- **class-order**: the member order of a class under enumerate; reading: codepoint (`\d + 1` SEARCHED `x10` `1`@1
  vs descending `10`@1).
- **flags-in-filter**: do a hole's flags reach an `&` inside it; manager leans yes (`/(?i)x${/ab/ & /a./}/` WHOLE
  `XAB` HOLDS vs FAILS).
- **flags-scope**: which flags propagate (`x` above all; `n`, `U`, `xx`, `J`, branch carry run).
- **number-edges**: `% 0` and a negative result; reading: nothing (vs compile error / signed).
- **dollar-diagnostic** (confirm): a read stands for its group's rx for emptiness diagnostics; §5.2 wording change
  printed in the row.
- **same-name-count**: does a group arriving through a hole count as a second name; reading: scoped.
- **construction-line** (b)'s finite half (one line): does it follow from the enumerate line.
- **any-case-body** (a GAP, listed for the manager): the body equals the primitive only for arguments writing no
  case flag and not in a filter role.
- numeral-width: RULED (R1), no longer asked. Still asked from before: plus-operands, construction-line (b),
  other-holes, anything-text, zero-in-sequence, group-truth / pass-table, number-in-loop, hit-carry-depth,
  caller-ambiguous, not-test, condition-group, the conditional's spelling.

## EVIDENCE AND COMMANDS

- Forward: `(cd $PCREC_TMPDIR/scratch/predspec281 && timeout 900 python3 -I -B
  /home/pcrec/projects/pcrec/worktrees/predspec281/docs/dev/lanes/predspec281_evidence/predspec281_model.py >
  fwd.out)`; `cmp fwd.out <evidence>/predspec281_model.out` rc 0; "CHECKS: 28 of 28 OK". Seconds.
- Sabotage: `PREDSPEC281_SABOTAGE=tN` for N = 1..22 each alone, then `=1`; `predspec281_sabotage.out`: every tN
  CAUGHT, tracebacks 0; all at once 6 of 28.
- Controls: libpcre2-8 10.46 via `../rxmodel_evidence/pcre2h.py` (run, never read; D181), python `re`. No PCRE2
  SOURCE fact was needed (every PCRE2 fact used is behaviour, run).
- Counts stated anew (each a line of `predspec281_model.out`): PO 0 / 4,416 / 4,416 of 9,331; CO 0 / 47 / 85 of 781;
  FF 6 / 78 / 78 and 0 / 0 / 0 of 1,555, `any_case(/(?-i)ho/)` 3 of 85; NW 3, 30, 9,990, 9,990, 0, 0 of 10,000, two
  reads 20,900 / 15,950 / 4,995 of 45,150, composition 0 of 60,000; PR rev 28 order 0 / 11 / 12 of 63, product
  0 / 0 / 0 of 364; DD 0 / 0 / 0 and 3 / 417 / 417 of 485; UN 0 / 0 / 0 of 1,365.
- Checks run: `make -s test-plan-lint` PASS; `grep -rnE 'plan\.md:[0-9]'` over the filed review and its dir: no
  match; `scripts/check_claudemd_size.sh --all`: within limits.
- LIMITS (the evidence CLAUDE.md): the two-case body's `&`s reduced by hand (sets checked); an `&` in a hole spelt as
  capture + callout; an infinite argument truncated to the subject's length; §5.5 has no budget number.
