# Lane absfold: the owner's LOCKED absent-label rule folded into joint_condition.md

Lane absfold, 2026-11-16, opus, DESIGN ONLY (no build go; nothing under `src/`, `cli/`, `lib/`, `memfn/`, `tests/`;
no edit to `predicates_draft.md`, the rulings record, `predicates_future.md`, any skill or guide). Branch
`lane/absfold` (cut from `lane/absimpact` with main merged). The ruling: COND-FAMILY's last entry, "2026-11-16 OWNER
RULING — absent-rule: LOCKED" (box clock 14:31, CF:1655-1680); the owner's words: "? Or = but not both. Both meanings
of absence are the same?" then "absent-rule: lock". Every sentence not quoted or cited is the lane's; the manager's
sub-choices of 14:31 are labelled "the manager's reading (14:31)" wherever used.

## STATE AT HANDOFF

- STATE: done. Commits on `lane/absfold`: the evidence script and its output, the note's §4G and its in-place
  corrections, the §9 rows, this report and the history-index line.
- OWED: none.
- Rulings file `docs/dev/lanes/absfold_rulings.md`: EMPTY at every read (before each commit and before this report);
  last R-n applied: none.
- Premise test: `tail -40 docs/design/plan_row_bodies/COND-FAMILY.md | grep -c "absent-rule: LOCKED"` = 1;
  `absimpact_report.md` has SUB-CHOICES THE RULE LEAVES (line 187).
- STOP RULE check: no ruled point (1)-(4) contradicts an owner ruling still in force that the 14:31 REVERSES list
  does not name. Checked: every 2026-11-16 entry (`grep -c '^\*\*2026-11-16' docs/design/plan_row_bodies/COND-FAMILY.md`
  = 35), CF:933, CF:997-1000, the ruled L-rows of the draft's §0.1 that read an absent label (L6, L16, L23, L30, L36,
  L52, L55, L56, L64, L65): the ones that move are named by REVERSES (CF:997-1000, L36's zero clause, §4.2's
  boundary, the 12:45 wording, §4B.1's zero-pass sentence, CF:933) or are LEAN / BY DESIGN rows whose verdict holds.
- Files: `docs/design/joint_condition.md` (§4G NEW; [§4G] corrections in the header, J6, J7, J9, §3, items 3, 5, 6, 8,
  §4B, §4D, §4E, §4F, §6, §7, §8, §9); `docs/dev/lanes/absfold_check.py` and `.out`; this report;
  `docs/dev/history/claude_md/docs__dev__lanes.md` (one line). `docs/design/CLAUDE.md` NOT touched (at its limit).
- The mark's spelling `m?` is a PLACEHOLDER (D193 add. 4), said once in §4G.1 and used consistently.
- Standing questions (docs/design/CLAUDE.md), for the note's §4G: (1) measurement regime: not relevant (no timing or
  size); (2) independent control: relevant to the evidence only: the ruled answers are checked against regexes built
  from the rule stated over sets (never from the evaluator), set-once tables against the earlier lanes' committed
  `.out` columns, and a sabotage flips the zero-pass entry (160 differ); (3) what moves on regeneration: not
  relevant (no data file, table or stamp).

## WHAT WAS FOLDED

The rule, stated ONCE as §4G.1 with table (AR) (absence x what the author wrote x shape -> answer), the four ruled
points quoted verbatim, the manager's four sub-choices labelled, the not-both error with its text, the mark's
placeholder status. Table (TM2) (the time example) and (TM2-L) (the same in a list). §4G.2: every table the note
quotes re-run. §4G.3: the place-by-place correction list. §4G.4: every §4E/§4F corner marked CLOSED / MOVED / STILL
OPEN. §4G.5: the ruling's UNDEFINED list. §4G.6: contradictions and unexpected answers.

In-place corrections (each marked "[§4G]"; superseded text kept and marked "SUPERSEDED 14:31"):

| place | change |
|---|---|
| header STATUS | entries through 14:31 (35); absent-rule RULED, pairing-loop ANSWERED; open: tuple-parts, zero-pass-empty (marked labels only); lane absfold; evidence paragraph |
| J6 | "unset" reads ABSENT, one kind; the default over every absence; the mark; not both |
| J7 | the 12:45 manager's wording REVERSED except the answer `9` FAILS and the `&` equality, restated on the condition side (13:52); GROUP-ZERO superseded; "never reached" no longer distinct; pairing-loop (3) SETTLED |
| J9 | (RZ) re-run: 0 of 1,110 from `&`, 5 move from 12:45 |
| §2 costs, §3 tables | N6 the mark; the "unset fields" row; COUNTED ALIKE: one absence replaces the boundary and the zero-pass EMPTY state; the not-both error (12 errors); the never-absent-mark warning; open items |
| item 3, item 8 | O28's unset half ANSWERED; the three-meanings and not-both look-alike rows |
| item 5 | pairing-loop ANSWERED and (NL) re-run; the ZERO PASSES bullet superseded with re-run counts; the table-of-passes model: the plain condition is no longer SQL's `ALL` |
| item 6 | the third meaning (the mark); `label.unset` names three fixes |
| §4B | 4B.1 MEANING (every absence), `default.unused` clause (a), the mark's warning (manager's reading), `label.unset`, the LOOPED row; 4B.2 the guard "m absent" and the mark's unfold; 4B.4 the third meaning and the date by the mark; 4B.5 the date row SIMPLER; 4B.6 SOME is the mark; 4B.7 base rule, computed label UNDEFINED, O28, group questions |
| §4D | D3, D7, D8, D9, D11, D13, D23, D25 and the tally |
| §4E | the table's superseded zero-pass HOLDs; corners 1-4 and the RULING-2 paragraph |
| §4F | RULING-1, RULING-2, OWNER-2, SIM-6, RULING-3, SIM-2, SIM-5, OWNER-6 |
| §6, §7 | B2 (the mark), B6 (answer kept, new reason); items 8, 15, 16 restated, item 17 new |
| §8 | pairing-loop and absent-rule ANSWERED with his words and times (and absent-holds 13:38, the principle, the idea, the lean, the variant); PARKED items 3, 5-7 marked closed / the rule / overtaken; STILL OPEN 2 marked answered, 3 restated for marked labels with the manager's lean; 4 NEW (all-over-none, mark-in-count), drafts below |
| §9 | rows 2, 6, 15, 16, 27, 43, 44, 45, 54 restated; rows 55-68 NEW (§4.2, §4.3, §2.6/`min`, the look-alike rows, §5.4 the mark, §7.1 warnings, `when`, O28, the old-answer sentences, future items, REV 20 MUST DECIDE, the open shape, pairing-loop/O56, §4.1's equality) |

## EVERY SENTENCE THAT STATED THE OLD ANSWER

The draft (rev 19; absimpact counted 8 distinct statements by
`grep -nE "(zero (passes|iterations|hits|times)|empty (list|span)|the empty)" docs/design/predicates_draft.md | grep -E "HOLDS|holds|HOLD\b"`,
11 lines; their sites, each now in §9 row 63 with the row that restates it):

| site | words | §9 row |
|---|---|---|
| §0 rev summary `predicates_draft.md:215` | "zero iterations: a plain condition holds" | 63 (with 55) |
| L36 `:534` | "on ZERO iterations both HOLD" | 58 |
| L55 `:553` | "with the default `min = 0` a plain condition over zero hits HOLDS" | 58, 57 |
| L56 `:554` | "the match REACHED n's loop and ran it zero times, so the plain condition holds" | 58, 55 |
| L65 `:563` | "the loop was REACHED and ran zero times, so it HOLDS" | 58, 55 |
| §2.6 ZERO HITS `:1172-1173` | "A plain condition or `all(...)` on the hits HOLDS over zero hits" | 57 |
| §2.6 hand check `:1202` | "a plain `(g: "x")` HOLDS at `min = 0`" | 57 |
| §4.2 THE BOUNDARY `:1600-1602`, witness `:1608` | "a plain condition (every iteration) HOLDS over none"; "on the empty span HOLDS" | 55 |
| §4.2 STATUS `:1614` | "a loop reached and run zero times holds a plain condition" | 55 |
| §4.3 table `:1659-1660` | plain: "HOLDS on zero iterations of a loop the match reached"; `all`: "the same as the plain condition, zero iterations included" | 56 |
| §13 O28 `:3683-3689`, `:3844` | "a plain condition HOLDS over zero iterations of a loop the match reached" | 62 |

The note (absimpact's 7, each now corrected in place): J7's quoted 12:45 wording (superseded, [§4G] after it);
§4B.1's LOOPED row and its nested `5` witness; §4D D9; §4E's (ZD) all-looped list row and (Z1) row; §4E's (ZJ) empty-set
row; §8's zero-pass-empty example `0-3`. Also corrected, not on absimpact's list: item 5's ZERO PASSES bullet,
item 5's table-of-passes model ("`ALL` over zero rows is true"), §6 B6, §7 items 15-16, §4F RULING-3.

## THE RULE TESTED

`timeout 120 python3 -I docs/dev/lanes/absfold_check.py` (0.7 s; libpcre2-8 10.46, Python 3.14.4): **69,441
engine-run cases, 0 differ, 0 engine disagreements, 88,275 probes**. `ABSFOLD_SABOTAGE=1 timeout 120 python3 -I
docs/dev/lanes/absfold_check.py`: **160 differ** (the zero-pass entry flipped back to today's). The script exec's
absimpact's machinery verbatim (`part()`, `tup()`, `plain()`, the engine wrappers); the ruled rule is absimpact's R.

| table | result (all from the `.out`) |
|---|---|
| (AR) | the rule table: the zero-pass, never-reached and missing-in-a-pass rows give identical answers in all 15 cells; today differed in the zero-pass row; `h? = v` an ERROR on every row |
| (TM2) | `9`/`10`/`11`/`9:15`/`9:45`: nothing F F F F H; `m?` H H H F H; `m = 0` F H H F H; `m? = 0` ERROR. ENGINE-RUN on 11,110: nothing vs `m?` 92, nothing vs `m = 0` 90, `m?` vs `m = 0` 2 |
| (TM2-L) | list of times: the empty list FAILS for `((h, m): R)`, `((h, m?): R)`, `((h, m = 0): R)`; HOLDS for `((h?, m = 0): R)` and `((h?, m?): R)` |
| (U), (S) | 0 move (set-once); OLD-OUT 0 of 7, 0 of 6 |
| (RZ) | 5 of 1,110 move (`3`); record = `&` 0; `h?` = old 0; `h = 9` 5 move, = `&` 0; `h = 0` = old 0; `all` A2v vs `all & all` 5 (`0`); A2z, A2m vs old 0 |
| (Z1) | 10 of 1,110 move; `''` of the list FAILS; `x` of `/x\|(?<n>\d)+/` FAILS (as before) |
| (ZN) | 69 of 2,526 move; record = `&` (per pass) 0; pooled 48 |
| (NL) | 19 of 73 vs jcfold, 9 vs jcfold2; `(h?, k?)` = jcfold2 0; `(h, k?)` 1 (`''`) |
| (ZJ) | unmarked: 0 of 10 zero-pass hold, each set; `h?` joint = `h?` hand expansion 0 of 10, each set, either domain; domain corner `("x", 3) \| (0, 5)` |
| (ZJ-E) | unmarked F F F; F1 F F F; F2 H H F |
| (ZE) | record = `&` 0 of 11,100; C2 = its rows 0; a = 0 C1 vs C2: unmarked 0, F1 0, F2 1 (`0-3`) |
| (ZD) | b: `5`/`5-` F F, F F, H H for none / 9 / 2; c: 1 of 91 move (`''`), `(h?, m = 0)` 0 |
| (OP) | 1 of 259 move (`''`); record = `&` per pass 0, pooled 8; `(h?, m?)` 11, `(h?, m = 0)` 11, `(h, m = 0)` 12 from the old; `all` A2v 0, A2z 0, A2m 11 |
| (UP) | 15 of 241 move; record = `&` 0; with `k?` 0 |
| (D1) | 11,000 / 11,110 / 11,110 (OLD-OUT equal); looped `n = 0` used (1 of 1,111), `n = 9` unused |
| (DL) | 1 of 585 move (`''`); `(h?, m = 0)` 0 |
| (DD) | `d?` admits `02`, `03`, `04` |
| (L36) | `(n: <5)` split 0 of 11 groups; `all` A2v 5, A2z 5, A2m 0; plain vs `all` 1 of 1,111; `all` vs `n?` 0; `all((n: <0))` vs `(n?: <0)` 1 |

Record = `&` at every depth: 0 differ on (RZ) 1,110, (ZN) 2,526, (OP) 259, (UP) 241, (ZE) 11,100, each single-label
condition read per pass of its own loop. The not-both error: refused on every absence kind and on a present label.

## CONTRADICTIONS AND CORNERS

Not repaired; both sides each (§4G.6 in the note).

1. **`all` over none, three readings, against one kind of absence.** "`all(...)` over no values HOLDS" (the manager's
   reading) can mean A2m (any absence), A2z (a loop's zero passes only, outside labels tested) or A2v (no pass of
   the pairing loop, outside labels NOT tested). `/(?<n>\d)?x/ & all((n: <5))` vs `/(?<n>\d)*x/ & all((n: <5))` on
   `x`: A2z/A2v FAIL, HOLD (5 of 11 equal-pattern groups split again, against ruled point (1)); A2m HOLDS, HOLDS (0).
   A2v also breaks record = `&` under `all` (`/(?<k>\d)(?:;(?<h>\d))*/ & all((h: <5, k: 3..7))` on `0` HOLDS,
   `all((h: <5)) & all((k: 3..7))` FAILS; 5 of 1,110) and HOLDS on the ruled `9`.
2. **The mark's two sentences.** "absence is acceptable, the condition is satisfied" (F2) vs "some value would put
   the tuple in the set" (F1). `/(?:(?<h>\d),)*/ & (h?: <0)` on `''`: F1 FAILS, F2 HOLDS. With `$a`: `(h?: <$a, k: 3)`
   on `0-3` F2 HOLDS while `((h?, k): < ($a, 0))`, the same empty set, FAILS (1 of 1,110). J1/J9 make the one-label
   and record forms the joint condition's, which reads F1.
3. **The domain of "some value"** (§4E corner 2, moved to the mark): `((h?, k): ("x", 3) | (0, 5))` on `3`: over
   `\d` FAILS, over every string HOLDS; the hand expansion agrees with the joint form under either.
4. **A marked absence in `some`/`count`** (manager's reading: not counted): `occurrences(/ab(?<g>[xy])?/) & (g?:
   "x")` on `ab` HOLDS while `some((g?: "x"))` FAILS (absimpact (OG) 885 of 5,461 between the two readings;
   DERIVED, not re-run).
5. **The shape with no one-mark fix** (its row: §4G.6 (5), §9 row 66, OPEN): `/(?:(?<h>\d+)(?::(?<m>\d\d))?,)*/ &
   (h: <10, m: <30)`, meant "empty passes, an item without minutes fails". No mark or default: 11 / 11 / 12 of 259.
   `all((h: <10, m: <30))`: 0 under A2z/A2v, 11 under A2m. So it has a one-word spelling exactly under the `all`
   readings that break one kind of absence.
6. **`all` and the plain condition (L36 said SAME).** Exactly: they agree wherever x has a value; where x has none,
   `all((x: S))` HOLDS and `(x: S)` FAILS ((LI) 1 of 1,111, `''`); under A2m `all((x: S))` = `(x?: S)` except when no
   value of x's group is in S (`(n?: <0)` FAILS, `all((n: <0))` HOLDS; 1 of 1,111).
7. **Record = `&` needs the per-pass single-label reading** (ruled point (1)'s "a pass that did not set it"); pooled:
   (OP) 8 of 259 (`3,3:15,`), (ZN) 48 of 2,526 (`3;0:2;0`). The draft's `:1694` LEAN becomes required.
8. **Three meanings of a missing field**, not two (§4B.4): `m = 0`, `m?` (SOME over the group, §4B.6), `| (h: 10)`;
   on `11`: HOLDS, HOLDS, FAILS; on `9`: FAILS, HOLDS, FAILS.
9. **`label.unset`** names a state the rule no longer has and fires on every condition over a `*` loop (15 programs
   vs 1, absimpact).
10. **`!` of a marked condition** (manager's reading, plain complement): `!(n?: <5)` FAILS on `''` while `(n?: !<5)`
    HOLDS: the L30 pair still differs on an absent label, now in the other direction from the unmarked pair.

## QUESTION DRAFTS

For the manager to present or rule. Plain words; each with a word slug.

**all-over-none** — When a field has no value, should `all(...)` treat every kind of "no value" alike, or only an
empty list?
- Smallest example: `/(?<n>\d)?x/ & all((n: <5))` and `/(?<n>\d)*x/ & all((n: <5))`, both on the text `x`.
- Answer A (every kind alike: `all(c)` = c with its fields marked optional): both HOLD. Follows: your "one kind of
  absence" holds for `all` too (no pair of equal patterns splits), but a list of times whose items may lack
  minutes cannot say "an empty list is fine, an item without minutes is not" in one word (11 of 259 lists differ
  from that meaning); it needs an extra alternative.
- Answer B (only an empty list): the first FAILS, the second HOLDS. Follows: that list shape becomes one word,
  `all((h: <10, m: <30))` (0 of 259 differ), but `?` vs `*` around the same group give different answers again
  under `all` (5 of 11 groups of equal patterns split).

**zero-pass-empty** (now only for fields marked optional) — When a field marked optional is missing and NO value of
it could satisfy the condition, does the condition hold?
- Smallest example: `/(?<a>\d)-(?<k>\d)(?:;(?<h>\d))*/ & (h?: <$a, k: 3)` on `0-3` (a = 0: nothing is below 0).
- Answer A ("some value would do", the reading your ruling gives for several fields): FAILS, and every way of writing
  the same empty condition FAILS alike. The manager's earlier lean.
- Answer B ("the condition is satisfied", read alone): HOLDS, but `((h?, k): < ($a, 0))`, the same empty set,
  FAILS: two spellings of one set disagree (1 subject in 1,110).
- The lane's note: since a one-field condition is the several-field condition with one field (your
  record-is-product), A already follows; this may be the manager's confirmation, not a question. The residue that
  is a real choice: whether "some value" ranges over the strings the field's pattern can match (`\d`: digits) or
  over every string (`((h?, k): ("x", 3) | (0, 5))` on `3`: FAILS vs HOLDS). The manager's earlier lean: the
  field's own pattern.

**mark-in-count** — When an item lacks a field marked optional, does `some(...)` count it?
- Smallest example: `occurrences(/ab(?<g>[xy])?/) & (g?: "x")` and `... & some((g?: "x"))` on `ab` (one hit, no g).
- Answer A (not counted, the manager's reading): the plain condition HOLDS, `some` FAILS: "some item has x" is false
  on a one-item list where "every item has x (or nothing)" is true.
- Answer B (counted, as the plain condition reads it): both HOLD; `count` then counts items that have no value.

Nothing else from CONTRADICTIONS needs the owner: (4)-(10) are consequences to state in rev 20 or the spelling
step's (`label.unset`'s name), and the UNDEFINED list is the ruling's own LEAVES, for rev 20.

## LEFT OPEN

- The questions above (**all-over-none**, **zero-pass-empty** for marked labels incl. the domain, **mark-in-count**),
  and **tuple-parts** (unchanged).
- The ruling's UNDEFINED list for rev 20 (§4G.5, §9 row 65): a computed label reading an absent label; `$h` / a hole
  / a bound on an absent label; the mark through a macro's label parameter; `list_of`'s minimum.
- The shape with no one-mark fix (§9 row 66), tied to all-over-none.
- `predicates_future.md` items 3, 5-7 are marked closed / the rule / overtaken only in this note's §8 and §9 row 64;
  the file itself is the manager's to edit.
- The mark's spelling (placeholder `m?`), `label.unset`'s name and the never-absent-mark warning's name: the spelling
  step's.
- Not done: a critic round on §4G (the 14:31 record says the manager's readings are "to be checked by the fold and
  its critic round").
