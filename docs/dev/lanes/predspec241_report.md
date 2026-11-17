# Lane predspec241 report: predicates_draft.md revision 24.1 (review r40's fixes)

Lane predspec241 (opus, 2026-11-17), DESIGN ONLY: no build go, no make. Review cited:
`docs/dev/reviews/2026-11-17-r40-predspec24.md` (filed by another lane). The manager's dispositions win where they
differ from the review. Evidence: `docs/dev/lanes/predspec241_evidence/` (engine, `.out`, CLAUDE.md).

## STATE AT HANDOFF

OWED: none

- `docs/design/predicates_draft.md` is at rev 24.1. Size: 6,762 lines (797,544 bytes) before; 7,083 lines (847,257
  bytes) after.
  - The head line was REPLACED, not appended: "rev 24.1: review r40's fixes; NOT STABLE pending the owner's
    answers".
  - The §0 status line was replaced.
  - The changelog gained a rev 24.1 entry at the top. The rev 24 entry stays as the record.
- `docs/design/predicates_future.md` has a new item 22: the place table as the next revision's skeleton (C6).
- RULINGS FILE: applied R1, R2, R3 and R4. The last applied is **R4**.
  - R1: the owner RULED exception-rule.
  - R2: pass-own-labels is now asked.
  - R3: the owner's lean on it, and the ramifications he asked for.
  - R4: a label is not a capture.
  - I re-read the file before each commit and before this report; it was 6,715 bytes at 15:45.
- STOP RULE: nothing stopped.
  - No engine fix changes a RULED answer the owner was shown: PART A's 68 lines are unchanged by the fixes.
  - pass-own-labels is a candidate, not a fix. It moves 17 catalogue lines only when run as the candidate.
- Not done:
  - `[REV 24.1]` marks were placed per sentence or section head, not per row in §13/§16 (records, unmarked by rule).
  - §2.7's single term hit ("one reading primitive", rev 15's O67) is a different notion and was left unmarked.

## FIX TABLE

| id | what was done | where |
|---|---|---|
| A1 | Engine: a body or `occurrences` condition reads the labels set so far. W1c re-spelled to the mandatory item. W1c-carry is a control (5 / 34 / 34). W2a = 0 explained. Under rulings R2 the per-pass scope is a candidate, not retired. | R.1, R.1.7, §R.4, §2.6 mark |
| A2 | Engine: a loop exports every label it sets, the last setting. Grid G1-G9 added. | R.1.7, PART C |
| A3 | Engine: `&` and `!B` run the operand WHOLE on the stretch's own text. D5 now covers anchored, lookahead, `\b` and lookbehind operands. | R.1.4, PART D D5 |
| A4 | The stretch rule for `hits` is THE DRAFT'S READING, asked as **hits-text**. "Never re-split" holds in WHOLE only. | R.1.9, §R.8 |
| A5 | WHOLE keys carry labels. Join order moves labels (117 / 414 / 414) and a lazy operand's stretch (0 / 1,008 / 1,197). `&` distributes over a LEFT `\|` only. The manager's "left side first" is withdrawn and becomes **join-order**. | R.1.4, §R.8 |
| A6 | "Some path survives" and "never admits" are scoped: atomic admits 12 / 156 (D18), lookahead 0. The principle is reworded "the same paths with the same labels" (dead branch 1 / 220 / 220, D19). **atomic-search** asked with item 14's words. | R.1.3, R.1.4, §R.8 |
| A7 | joint-loops (1) is reversed for bare joints. The mixed-pass example is `9:45,10,`. **joint-last-pass** asked together with **pass-own-labels**. | R.1.7, §4.3 mark, §R.8 |
| A8 | Marks placed: §0.1 L1, L25, L30, L39, L58, L61, L83, L95, L100; SAME ROWS RE-CHECKED; §2.6; §3.2; §3.5; §4.1 (twice); §4.2; §4.3 PAIRING RULE; §4.4; §5.2; §6.1 ONE READING; §7.1; §8 when body; `all` in §1/§3.4/§5.1. Found by grep, same kind: Goals' "absent is UNKNOWN"; Standing questions' "one reading's cost"; §3.4's "PCRE's parse". | §0.1-§8 |
| A9 | default.unused fires at every polarity (D15 0 / 0 / 0). The §5.2 asymmetry goes with **polarity-rule**. | R.1.6, R.2, §7.1 mark |
| B1 | §R.8 separates the manager's readings closed by a regex model (three-valued, record-under-not, condition-or) from the asked ones. | §R.8 |
| B2 | exception-rule is RULED (rulings R1). It is removed from the questions and applied in §R.6. | §R.6, §R.8, §R.11 |
| B3 | whole-text was CONDITIONAL; it is now ADOPTED as a requested feature (R1 (b)). The searched shape's missing rule is named. | R.1.11, §R.5 |
| B4 | Exact quotes: 11:50 in full; "each row remembers its branch" is pathimpact's; the when-meaning time is after 14:25; ONE `\|` is the manager's wording; regex-settles (4) at 13:25; item 14's words. | R.1.2, R.1.5, R.1.9, R.1.10, R.1.4 |
| B5 | absent-rule (1) and (2) are narrowed for bare conditions. The "one kind of absence" premise is gone. | R.1.7, §4.2 mark, §R.9 |
| B6 | §R.11 is rebuilt, one row per COND-FAMILY entry (30 rows plus 31 exception-rule and 32 the pass-own lean). | §R.11 |
| B7 | §2.5 is marked REOPENED by item 21. | §2.5 mark, §R.9 |
| B8 | G24-1's form is the term list plus the per-entry table diffed against §R.9. G24-5 is new: every model-less item is a question with a slug. Non-goals are stated honestly. | R.0 |
| B9 | W6d, W6e and W7b were RUN. NOT RUN, with reasons: selecting passes, `sorted`/`distinct`, the list `$x` (→ pass-list-read). | §R.4 |
| C1 | §R.10 rewritten: ORDER CHECK, sabotage and switch numbers. | §R.10 |
| C2 | Records are §7's compile-time find-all (D20 0). No tenth question. | R.1.1, §R.6 |
| C3 | Defined: U3's pattern, TML, CLOSE, W1c's `+`, and the +1 advance. | R.1.2, §R.4, §R.5 |
| C4 | The LAW's places are stated (top level). **zero-place** asked. | R.1.4, §R.8 |
| C5 | Each count names its rules, metric and pool. §7.1, L30, L83 and L95 carry rev 24 counts. | §R, marks |
| C6 | A PLACES paragraph is added. predicates_future item 22 is filed. DEFAULTS leave §R.6 (V26-V29 0 differ; D15). | R.1.1, §R.6, future.md |
| SIMULATE-8 | One sentence: a condition in an `&` chain stands after every pattern operand. | R.1 |

## WHAT MOVED

**Engine fixes**: the critic's number before → after, each re-run against the fixed engine.

| fix | what was measured | before | after |
|---|---|---|---|
| A1 | PCRE2's W1c vs the engine (WHOLE / SEARCHED / FIND-ALL, of 364) | 5 / 34 / 34 | 0 |
| A1 | the occurrences twin G2 (per mode) | 42 | 0 |
| A2 | N1 (per mode, of 1,365) | 300 | 0 |
| A2 | Q8 / G8 (per mode, of 1,365) | 693 | 0 |
| A3 | `A & B` vs `A & (0: B)`, anchored B (of 1,365) | 0 / 1,344 / 1,344 | 0 |
| A5 | E5 WHOLE (labels) | 0 | 117 |
| A5 | E1 WHOLE | 243 | 363 |

**Printed numbers that moved, rev 24 → rev 24.1:**
- libpcre2 models: 20 of 20 equal → 38 of 38 equal.
- `&` distributes over `|` → over a LEFT `|` only. `X & (B | A)` differs 0 / 1,008 / 1,197.
- join-order "0 / 414 / 414 ... never the stretch" → 117 / 414 / 414, plus the stretch 0 / 1,008 / 1,197.
- W1c (rev 24's spelling): 0 → 5 / 34 / 34. Re-spelled: 0.

**New numbers, all rules rev 24.1:**
- PART D:
  - D12 (L100): 156 of 341 WHOLE.
  - D13 (L61): 0.
  - D14: 0 / 125 / 125.
  - D15: 0.
  - D16 (L30): 1 / 130 / 148; 1 / 220 / 220; REP 6 / 248 / 364.
  - D17 (§4.4): HOLDS.
  - D18: 12 / 156.
  - D19: 1 / 220 / 220.
  - D20: 0.
  - D21 (L95): 6 / 1,482 / 1,908.
- Defaults V26-V29: 0.
- operand-context: 0 / 90 / 132; lookahead 0 / 122 / 132 (of 364).
- pass-own-labels ramifications:
  - PART A: 17 of 68 lines move.
  - PART B: 23 of 23 stay at 0.
  - PART C: 30 of 38 stay equal.
- Unchanged by the fixes: catalogue 68 lines, MOVED 28; printed check 109, mismatches 0; old meanings 23 of 23 at 0.

## OWNER QUESTIONS WRITTEN

Eleven questions are in §R.8: the nine named in the brief (exception-rule was RULED meanwhile and taken out) plus pass-own-labels, operand-context and shared-label. None is chosen.

1. **hits-text**: the stretch's hits or the subject's. `x300 12`: `x30`@0 with hits [`30`] vs hits []. 0 / 56 / 56 of 341.
2. **atomic-search**: PCRE's group vs stopping at the first start. `9:30` SEARCHED: `30`@2 vs FAILS. 0 / 84 / 84 of 3,906.
3. **joint-last-pass**: last settings vs per-pass. `9:45,10,` WHOLE: HOLDS vs FAILS. 14-32 / 18-42 of 85.
4. **pass-own-labels** (asked together with 3): carry vs each pass starting unset (the owner's lean; R4: a label is not a capture).
   - `3;;`: HOLDS vs FAILS.
   - `9:45,10,`: HOLDS vs FAILS.
   - `((h, m = 00): == (10, 00))` on `9:45,10,`: FAILS vs HOLDS.
5. **hits-committed**: the committed list vs one pattern. `1234`: FAILS vs HOLDS. 56 / 56 / 56 of 341.
6. **join-order**: which operand is outer. `G & L` on `11`: `11`@0 vs `1`@0. 0 / 1,008 / 1,197 of 1,365.
7. **polarity-rule**: none / a warning / an error. Widened: is the §5.2 error without NOT itself an exception?
8. **pass-list-read**: a bare looped `$h` is the last setting or the list. `3;7;7` HOLDS vs REJECTED.
9. **zero-place**: innermost stretch vs group 0. ` 1`: HOLDS vs FAILS. 738 / 738 / 738 of 1,365.
10. **operand-context** (new): a lookaround or `\b` in an `&` operand sees the stretch or the subject. `a1`: `1`@1 vs FAILS.
11. **shared-label** (new): a label in both `&` operands is an error vs PCRE's `(?J)` reading. Not run.

## EVIDENCE AND COMMANDS

Every run was one engine process, from `$PCREC_TMPDIR/scratch/predspec241`, about 40 to 60 seconds each.

- Forward run:
  `(cd $PCREC_TMPDIR/scratch/predspec241 && timeout 1800 python3 -I -B <worktree>/docs/dev/lanes/predspec241_evidence/predspec241_model.py > fwd.out)`
  - SUMMARY: catalogue 68, MOVED 28; printed 109, mismatches 0; old meanings 23 of 23 at 0; libpcre2 38 of 38 equal; order check 3 of 3 differ.
  - The output is committed as `predspec241_model.out`.
- `PREDSPEC241_SABOTAGE=1`, same command:
  - MOVED 37; libpcre2 19 of 38; order check 0 of 3.
  - Caught.
- `PREDSPEC241_RULES=23.2`, same command:
  - MOVED 0; mismatches 0; libpcre2 15 of 38.
- Premise checks, from before the fixes:
  - predspec24's engine re-runs byte-identical to its committed `.out`.
  - The critics' scripts for A1, A2, A3 and A5 reproduce review r40's numbers.
- The owner-question lines are in PART Q of the `.out`, grep `^Q <slug>`.
- The RAMIFICATIONS lines are grep `^Q pass-own-labels`.
- Limit, stated: a condition inside an atomic part inside a loop item that reads a carried label is not covered.
