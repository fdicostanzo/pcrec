# Lane predspec23d — predicates_draft.md rev 23.2 (review r34's fixes), 2026-11-17

DESIGN ONLY (no build go; no make run). Branch `lane/predspec23d`, cut from main @ f0ff7c5c9. Inputs: the manager's
dispositions of review r34 (round predspec231, `$PCREC_TMPDIR/scratch/crit-predspec231/dispositions.md`), the review
and its verifier/simulate files, COND-FAMILY.md entries 2026-11-17 03:01 and 03:47.

## STATE AT HANDOFF

- STATE: done. `docs/design/predicates_draft.md` is at rev 23.2, header "rev 23.2: review r34's fixes; NOT STABLE
  pending the owner's answers"; `docs/design/predicates_future.md` items 17-18; evidence
  `docs/dev/lanes/predspec23d_evidence/` (model, output, CLAUDE.md).
- OWED: none.
- Rulings file `docs/dev/lanes/predspec23d_rulings.md`: empty at every re-read (last R-n applied: empty).
- No ruling made by this lane: every rule the dispositions touched that decides answers and is not word for word in
  the owner's record is labelled THE DRAFT'S READING (or the manager's) and asked in §R.8.
- PREMISE TEST (passed): the four engines (predspec23, 23b, 23c, searchrow) reproduce their committed .out files byte
  for byte when loaded by my model unpatched; review r34's A1 numbers (281; the closing example) reproduce under the
  canonical patch.
- Evidence check: `timeout 1800 python3 -I W/docs/dev/lanes/predspec23d_evidence/predspec23d_model.py > fwd.out`
  from `$PCREC_TMPDIR/scratch/predspec23d`; `PREDSPEC23D_SWAP=1` run: diff without ORDER lines EMPTY (0 lines);
  `PREDSPEC23D_SABOTAGE=1` forward vs swapped: 732 differing lines. Reach and non-reach stated in the script header
  and §R.10. A re-run at the end was byte-identical to the committed `predspec23d_model.out`.

## FIX TABLE

| finding | disposition | done | where |
|---|---|---|---|
| A1 canonical numerals | FIX-NOW | done: every engine line re-run under §2.2; every quoted count replaced; closing default re-chosen `m = 0` | §0.1 L83, L95; R.1.5; R.1.7; §R.3; §R.4; §R.4.1; §R.5 A3; §R.6; §R.7; R.7c; new R.7d; §4.3; §R.10 |
| A2 branch-order | WITHDRAWN -> ask branch-scope | done: R.1.4 relabelled (reading (iii) the draft's text, OPEN), its costs with `25`/`12`/find-all witnesses, scope rule not derivation; contradicted sentences tagged not rewritten (§3.2 tool 2, §3.5, §4.1); every branch-order site relabelled; §4.2 admitting-positions note; §R.8 item 6 | R.1.4, R.1.9, R.1.11, R.5, R.6, R.7c, R.10, R.11, §3.2, §3.5, §4.1, §4.2, §8, S124 |
| A3 order | FIX-NOW in part | done: R.1.1 place table gains "reads order?" column + three modes; `9:30` hits `9`@0, `30`@2 (R.1.9, nested-complement row); find-all holds-move under branch-scope | R.1.1, R.1.9, R.11, R.1.4 cost (3) |
| A4 record under NOT | label + ask | done: R.1.5 / L83 / R.11 "STANDS without NOT; under NOT: OPEN"; §R.8 item 7 with `10`, the completion alternative and its cost | R.1.5, §0.1 L83, R.11, §R.8 |
| D1 when | label | done: filter form = the draft's choice (when-meaning); R.7c c1/c2 say the standalone expansion moved; §2.6 scoped to unfiltered arguments | §8, R.7c, S124, §2.6, §R.8 item 8 |
| D2 polarity | define, label | done: §R.2 POLARITY (local / overall, the judged unit, constant-always warns); L30 + §R.2 qualified on a set-once label with the repeated edge 30 / 0; default.unused (b) by local polarity, scope attributed to the manager's F7 disposition | §R.2, §5.2, §7.1, L30, R.11, §R.8 item 9 |
| D3 interaction | state | done: THE INTERACTION after §R.8 item 5, pointers from 2(b) and 3 | §R.8 |
| D4 complement place | state | done: R.1.4 rev 23.2 paragraph (WHOLE reading, the 20:41 table, the chain/label collision); §R.8 item 10 | R.1.4, §R.8 |
| F-DOC-1 three kinds | FIX-NOW | done | §2.1 (TYPING, ONE INPUT RULE, kind table, REASONING), §3.5 RULE, §4.1 STATUS, §16 between, S056 |
| F-DOC-2 labels | FIX-NOW | done: condition-or (§2.1, §2.2), polarity, complement-in-chain (L1, L39, §2.2), branch sites, hit-list (R.1.1 row 5, R.1.9), default.unused (b) | as listed |
| F-DOC-3 LEFT JOIN cite | FIX-NOW | done | R.1.2 |
| F-DOC-4 parking cites | FIX-NOW | done: §R.4, §R.8 item 1 cite 03:01 (1); R.11 whole-text PARKED; new R.11 row for 03:01 (2) / future item 14 | §R.4, §R.8, R.11 |
| F-DOC-5 yes/no | FIX-NOW | done (absent -> UNKNOWN; repeated -> per pass) | R.1 plain words, R.1.1 row 3, §R.3 fourth member |
| F-DOC-6 hit repeated; "row" | FIX-NOW | done | R.1.8, R.1.9 |
| F-DOC-7 engine readings | DOC | done: end order, pass rows, sabotage reach (23c and 23d) | §R.10 |
| PLAN notes (a), (c) | PLAN | done | predicates_future.md items 17, 18 |

## COUNTS THAT MOVED

All under §2.2 (rev 23.1's engines compared by value, = `padded(...)`), WHOLE / SEARCHED; full list in the draft's
R.7d:
- L83 differ: 101 / 371 -> 101 / 281.
- `t2 & NOT ((h, m): R)`, `t2 & ((h, m): !R)`: 1,860 / 10,230 -> 2,830 / 10,300.
- `t2 & !q`: 1,970 / 11,110 -> 2,940 / 11,110. `t2 & ((h, m = 0): !R)`: 1,880 -> 2,850 (differ 90 unchanged).
- `t2 & !q` on a text with a late time: 0 / 9,140 -> 70 (first `09:30`) / 8,240.
- `!contains(q)`, `text.none(q)`, routes (i)(a) WHOLE and (i)(b): 1,970 -> 2,870; route (ii) T2 / T2PAIRS
  1,970 / 132 -> 2,870 / 182; today's spellings vs (ii) 9,140 / 468 -> 8,240 / 418; T2PAIRS WHOLE 11 -> 13, (b) 132
  -> 182, differ 121 -> 169; find-all 2+ matches 264 / 121 / 589 -> 312 / 169 / 587.
- `when` on T2: 6,050 / 18 -> 6,105 / 18.
- Closing example (WHOLE holds; differ I1/I2a/I2b): joint 85; 70/0/45 -> 40; 36/0/25; record twin 40; 25/45/0 ->
  15; 11/25/0; `m = 99` 15 -> 4; 0/36/11; `m = 00` (now outside R) 40 -> 4; 0/36/11; `((h = 0, m = 00): R)` 40 -> 3;
  1/37/12, SEARCHED 1,111 -> 526; plain 14 -> 3, SEARCHED 852 -> 526. New default `m = 0`: `occurs.none(((h, m =
  0): !R))` and `((h = 0, m = 0): R)` 15; 11/25/0 (I2b EXACT), `((h, m = 0): R)` 14; 12/26/1.
- New witnesses (PART Y): branch-scope on `25`, `12`, `aa`; distribution 12 / 48 of 85 under (iii), 0 / 0 under
  (i), (ii); find-all `when` 125 / 310 of 1,110; record-under-not completion 0 / 0, its cost on `10` with padded R;
  L30 repeated edge 30 / 0 of 364 (first `3;;`); De Morgan 18 / 232 (EXISTS), 0 / 0 (three-valued, pass table),
  1 / 232 (three-valued, real passes); polarity witnesses 1,588 / 1,588.

AGAINST THE VERIFIERS: review r33's V-16 printed L83 281 (its `lt` was canonical) = mine; its closing 85 and 40 were
the value reading, now 40 and 15. Review r34's V1 matches every canonical number; its `t2 & !q` 2,940 was by hand
and the engine gives 2,940. Review r34's V6 175 is a REPORTED-ROW count where the draft's 164 is a holds-count (no
conflict). Review r34's V8 De Morgan 0 / 0 used the pass table with the null row; over real passes a three-valued
`some` gives 1 / 232 (the empty text); with EXISTS 18 / 232, = V8's. The simulate evaluator's 2,830 / 10,300, 2,850
and 6,105 = mine.

## QUESTIONS FOR THE OWNER

All in §R.8 with definition, example in both modes and leaning; the consolidated table at its end:
**whole-text** (parked), **pass-table**, **pass-and**, **group-truth**, **lookahead-labels**, **condition-or**,
**repeated-means** (told), **nested-complement** (told), and new: **branch-scope** (leaning (i)),
**record-under-not** (leaning: keep the split), **when-meaning** (leaning: its body, kept in x's order),
**polarity-rule** (leaning: adopt), **complement-place** (leaning: lone complement legal in whole-value places),
**hit-list** (leaning: adopt). Each wants a reply either way.

## LEFT OPEN

- Everything in the consolidated table; no text that depends on branch-scope or record-under-not chooses a reading
  (STOP RULE): §3.2, §3.5, §4.1 are tagged, not rewritten; R.1.3's same-table re-derivation and R.1.10's "the mode
  changes only which rows exist" are named narrower outside WHOLE, not rewritten (follow branch-scope; future 17).
- A3's general form (one ordered table) is `predicates_future.md` item 17, not built here.
- The engines' end order (Python's first end, then longest-first) is stated, not changed; a pool with nested
  alternative ends would need it fixed before quoting.
- Not reached by the 23d sabotage: PART Y polarity `t2` witnesses, default-unused rows, unmoved engine parts.
