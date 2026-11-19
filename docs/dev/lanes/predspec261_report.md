# Lane predspec261 — report (2026-11-18, opus; DESIGN ONLY)

Deliverable: `docs/design/predicates_draft.md` rev 26.1, head line "rev 26.1: review r47's fixes and the conditional;
NOT STABLE pending the owner's answers". 8,750 lines (1,073,336 bytes) before, 9,094 lines (1,134,743 bytes) after.
Evidence: `docs/dev/lanes/predspec261_evidence/` (CLAUDE.md, model, forward/sabotage outputs). Branch lane/predspec261,
cut from main @ b230287c2; not merged, not pushed.

## STATE AT HANDOFF

OWED: none

- Draft rev 26.1 complete: every r47 finding A1..E1 handled per the dispositions; every COND-FAMILY entry from "2026-11-18
  MANAGER CORRECTION — three of the manager's readings of this morning were NOT supported by the runs" to the end of the
  branch's file folded, plus main's three later entries named by the rulings file (R1-R3).
- `git -C /home/pcrec/projects/pcrec log --oneline -8 -- docs/design/plan_row_bodies/COND-FAMILY.md` on main: newest
  173ac0934 ("then is required"), e5ca99e05 (single argument), fa87119b0 (when-alone); all three FOLDED (R.1.10 (8),
  §R.11 rows 116-118). NOT FOLDED: none (nothing on main after 173ac0934).
- STOPS: none. The shown when-test table reproduced (python `re` and libpcre2); every r47 verifier-confirmed witness
  reproduced; the premise (predspec26 re-run byte-identical, forward and sabotage) held.
- Rulings file R1-R3 applied (R2 superseding R1's `when(x)` derivation; when-alone off the open slugs).
- `predicates_future.md`: not edited (item 24 optional; item 29 untouched as R2 says).

## FINDINGS APPLIED

| id | where | what |
|---|---|---|
| A1 | R.1.9, §R.8 (a) nullable-meaning, §2.6, §13 O53, §R.7 | "at most one hit" replaced by the verified statement (hits up to and including the first empty one; first `min` taken); 63 of 63 for min 0-3; s14 |
| A2 | R.1.0 place table `0` cells; R.1.13 (b); §R.8 zero-in-sequence | `0` per place; inside a part = its own match, THE DRAFT'S READING, asked under zero-in-sequence; NZ run |
| A3 | R.1.13, §R.6, §R.7, §R.8 | "with the regex meaning" narrowed; **number-in-loop** asked (8/33/33) |
| A4 | R.1.13 (two sites), §R.6, §R.8 backref-label | widened with both one-name witnesses (2/2/2 of 21,845; 1/1/1 of 5,461), plain PCRE patterns change answer |
| A5 | R.1.7, R.1.0 LOOP BODY and occurrences rows, §R.8 | **hit-carry-depth** asked (66/150/206) |
| A6 | R.1.0 PROGRAM row, §R.8 anything-text | advice WHOLE only; vacuity added (364 of 364 searched); `digits & not_seven` |
| B1 | R.1.14 | adjacent count holes only (351/0/0); s25 |
| B2 | R.1.14 | one array independent per mention (`n - n` = [0,-3,3,0]; `1234` via (2,6)); s28 |
| B3 | R.1.0 COUNT row, §R.6, §R.8 other-holes | split as THE DRAFT'S READING (-1 kind error, 70000 removed copy); `hole_ok` fixed |
| B4 | R.1.14, §R.6, CS4 row, §R.8 | group of conditions only = a condition, THE DRAFT'S READING; decides answers, asked as NEW slug **condition-group** |
| B5 | R.1.15 (10), §R.6, §R.8 value-hole | the two-anchor gap and `(?i)` caseless (4/336/336 exact vs 0/0/0 caseless; python literal control 0 of 3,906) |
| B6 | R.1.0 CLASS row, §R.8 other-holes | member reading limited to class-only literals (0/32/32) |
| B7 | R.1.0 ZERO row, §R.8 other-holes | one zero cell per position |
| B8 | R.1.0 | COMPLEMENT OPERAND row |
| B9 | R.1.0 COUNT row | "the literal holding the holes" |
| B10 | R.1.0 HOLE POSITIONS head, R.1.14 | the no-row-is-an-error sentence stated |
| B11 | R.1.14, §R.8 (b) | **product-order** re-listed |
| B12 | §R.8 RULED list, R.1.13 (two sites) | "CLOSED BY THE MANAGER'S ENTAILMENT" sub-list |
| B13 | R.1.13, §4.1, §5.3, §R.8 | **caller-ambiguous** asked (runs both sides) |
| C1 | evidence NZ; R.1.13; §R.11 row 78 | N3 withdrawn; s15 |
| C2 | evidence `rx_reach`, HF2 | reach classifier, soundness vs libpcre2; s16 |
| C3 | evidence CS3; R.1.14 | independent filter model, one level and in a loop; s17 |
| C4 | evidence `hole_ok`, P6 (9 rows) | backreference error, count kind; s18 |
| D1 | §5.4 `${ }` and `+ - * %` rows, §11 `+` row, §R.9 pointer | marked/pointed |
| D2 | §2.6 (four sites) | withdrawn refusals marked |
| D3 | R.0, R.1.1, §R.8 label-mark cite | cites fixed |
| D4 | R.1.4 CX, §R.8 anything-text, STOP RULE | his `any := /.*/` named failing; the clause was told to him |
| D5 | §R.7, §5.4 `^` row, §13 O34 | census corrected (22 lines in rev 26; 26 now), every live use marked |
| E1 | — | PLAN (next full revision, with RULING-5); nothing done |

## RULINGS FOLDED

| entry | kind | where | manager readings: run result |
|---|---|---|---|
| MANAGER CORRECTION — three readings NOT supported | correction | R.1.9, R.1.4, §R.8 | (1) "the LOOP's one empty hit": NOT SUPPORTED (r47 A1; superseded by the 3741 entry); (2)/(3) "every spelling agrees" false: SUPPORTED (90 of 121) |
| OWNER, a question on the conditional form | question | R.1.10 | naive form falls through: SUPPORTED (whole `1`; find-all `1x 12 a`) |
| OWNER, on spelling the conditional | suggestion | R.1.10, spellings 7 | — |
| OWNER RULING — when-default (+ `when` operator) | ruling | R.1.10 (2), R.1.0 | hand-worked answers: SUPPORTED |
| OWNER RULING — the guarded form | ruling | R.1.10 (1) | — |
| OWNER RULING — when-test | ruling | R.1.10 (3) | shown table REPRODUCED; peeked label readable in B: SUPPORTED |
| OWNER RULING — when-peek | ruling | R.1.10 (4), spellings 24 | peek/consumed forms, condition consumes nothing: SUPPORTED every mode; warning NOT RUNNABLE; A evaluated once per branch: NOT RUNNABLE |
| OWNER, spelling LEAN + the check | lean | R.1.10 (7), spellings 25-27 | commas required today: SUPPORTED by reading (NOT RUNNABLE) |
| MANAGER CORRECTION — nullable meaning, again | correction | R.1.9, §R.8 (a) | SUPPORTED (63 of 63, min 0-3) |
| OWNER on when-alone (main, by R1/R2) | history | R.1.10 (8)(i) | derivation `x \| (not x)`: runs as derived, WITHDRAWN by the next ruling |
| OWNER RULING — single argument an error (main, R2) | ruling | R.1.10 (8)(ii) | `then` required by the signature: became the next ruling; legal call list: consistent (RULE-AS-CODE); `null` a placeholder: NOT RUNNABLE |
| OWNER RULING — `then` required; NOT for else (main, R3) | ruling | R.1.10 (8)(iii), §R.8 | bare pattern under NOT collides: CONFIRMED (both readings run), asked **not-test** |

## WHAT MOVED

- `when` with a single argument and `when(x, else = z)`: legal by the lean → COMPILE ERROR. A bare pattern as a test: new
  (consumed, warned). Rev 26's `when(c, p)` answers: none moved (0/0/0 of 5,461; printed answers reproduce).
- The PROGRAM row's `anything & not_seven` advice: every mode → WHOLE only.
- Stated meanings (no printed answer moved): the nullable argument; `0` placement; number on one literal (now marked).
- Withdrawn-term sweep (`grep -cF TERM docs/design/predicates_draft.md`, final; every hit read, each either inside a
  [REV 26.1] mark, the record (§16, changelog, rev 26's R.1.10 text, §R.9/§R.11 history rows) or not a reader):
  "at most one hit" 7 (6144 is `^err`, genuinely one hit); "ONE, the empty hit" 1; "the LOOP's one" 2; "x & (NOT c | p)" 7;
  "when(c, p)" 14 (§8 under its mark, §16, changelog); "LIBRARY DEFINITION" 2; "entire match of the composed" 2;
  "exactly what regex means" 1 (marked); "one model (CS3)" 1; "N3" 6; "ONE COPY OF THE PATTERN" 0; "in every mode);
  write" 0; "with the regex meaning" 4; "same as x" 4; "two optional arg" 4; "when-alone" 5; "R.1.14 table" 2 (§R.9
  record); "find-all order" 5 (marked); "every spelling" 5; "filter-captures" 4; "label-mark" 10 (all "closed by
  entailment"); `${$` 26 lines (D5).

## DRAFT READINGS ADDED

13 added; 10 decide answers, each also asked:
1. `0` inside a part is its own match — decides; zero-in-sequence.
2. a number reads the LABEL in a loop — decides; number-in-loop.
3. `\k<h>` reads the label (one name) — decides; backref-label.
4. count -1 kind error / 70000 removed — decides; other-holes.
5. group of conditions only is a condition — decides; condition-group (NEW slug).
6. a value hole under `(?i)` caseless — decides; value-hole.
7. a range out of order a compile error — decides; other-holes.
8. zero values per position (class `[x]`) — decides; other-holes.
9. parameters by name (`when(x, then = y)`) — decides; conditional-spelling.
10. `NOT` on a bare test as a negative peek vs error — decides; not-test (no reading chosen).
11. `when` a library definition, the warning the compiler's — no answer.
12. A's labels unset in the else branch — no alternative answer under the rulings.
13. §4.1 chain lookup reads exports only — no printed answer.

## OWNER QUESTIONS LEFT

- value-hole: may a matched value stand in a pattern position, and as what text (now also case and the two anchors)?
- anything-text: what the provided `anything` matches (newlines; greedy/lazy); it cannot make searching non-vacuous.
- other-holes: several or zero values in class, range-end and option holes; non-count members of a count hole.
- plus-operands: what `+` does on operands that are not numbers.
- backref-label: does `\k<h>` read the label or PCRE's capture, now shown to change plain PCRE patterns?
- zero-in-sequence: what `0` names in a sequenced condition, and inside a part.
- group-truth / pass-table: do the group questions after a loop agree with the per-pass form?
- number-in-loop: a number on an optional group in a loop: capture, label, or refused?
- hit-carry-depth: does a label carry across outer passes or reset per `occurrences` entry?
- caller-ambiguous: what the caller gets for a label two parts export.
- not-test: `when(NOT x, z)` with a bare pattern: error or negative peek?
- condition-group: is a quantified group of conditions the same error?
- product-order (re-listed): confirm the member-list reading.
- (remaining table) conditional-spelling: the spelling, and parameters by name.
- when-alone: ANSWERED (not open).

## EVIDENCE AND COMMANDS

- Premise: `(cd $PCREC_TMPDIR/scratch/predspec261 && timeout 900 python3 -I -B .../predspec26_evidence/predspec26_model.py)`
  vs the committed .out: byte-identical; `PREDSPEC26_SABOTAGE=1` likewise.
- Forward: `(cd $PCREC_TMPDIR/scratch/predspec261 && timeout 300 python3 -I -B <worktree>/docs/dev/lanes/predspec261_evidence/predspec261_model.py)`
  → CHECKS 156 of 156 OK. All sabotages `PREDSPEC261_SABOTAGE=1` → 100 of 156; each of s1..s29 alone fails at least
  one check (`predspec261_sabotage_each.out`).
- Minimum witness lengths: A1 0-4, A3 3, A4 7 and 6, A5 4, B1 3, B5 3, B6 2, COND 0-3, NZ 3. Pools: A4 `37-;` <= 7
  (21,845), A5 `37x,` <= 6 (5,461), COND `12x` <= 5 (364), KH `15;9` <= 6 (5,461).
- Runs not run: the conditional's warning and the comma check (no parser); the `&`-chain `0` (not independently
  runnable); "A evaluated once per branch" (a cost). No make, no suite; single-process scripts under timeout only.
