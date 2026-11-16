# Lane jcfix: round jointcond's fixes applied to the joint-condition note, and two owner-question drafts

Lane jcfix, 2026-11-16, opus, design only (no build go; nothing under `src/`, `cli/`, `lib/`, `memfn/`, `tests/`).
Branch `lane/jcfix`, cut from `lane/jcfold2` with main merged in. Subject: `docs/design/joint_condition.md` (new
section §4F; every changed sentence marked "[§4F]"). Inputs: the review draft and the manager's dispositions of round
jointcond (the round's scratch directory, `crit-jointcond/review.md` and `dispositions.md`); the rulings record
`docs/design/plan_row_bodies/COND-FAMILY.md` through the label-twice entry (13:16); `predicates_draft.md` rev 19.

Evidence: `docs/dev/lanes/jcfix_check.py` / `.out`, run with `timeout 120 python3 -I docs/dev/lanes/jcfix_check.py`
(libpcre2-8 10.46, Python 3.14.4): 186,727 cases, 0 differ, 0 engine disagreements. Sabotaged with
`JCFIX_SABOTAGE=1 timeout 120 python3 -I docs/dev/lanes/jcfix_check.py` (every zero-pass or unreached piece of the
unfolds made vacuous): 578 differ, so the check can fail. Every count below comes from that script's output unless it
names another command. A row called COMPUTED is a Python comparison between readings, not an engine run.

## STATE AT HANDOFF

- STATE: done. Commits on `lane/jcfix`: the note, the evidence script and its output, this report, and the
  history-index line.
- Rulings file `docs/dev/lanes/jcfix_rulings.md`: EMPTY at every read (before each commit and before this report);
  the last entry applied: none.
- OWED: none.
- Open with the owner (not answered here): **tuple-parts**, **pairing-loop** (re-drafted below), **zero-pass-empty**
  (new, drafted below).
- A deviation from the brief, named: the brief gave the letter (DD) for a dictionary-domain table, but (DD) is already
  lane unsetdef's date-without-a-day table in §4B.4 of the same note. Two tables named (DD) in one note would be
  ambiguous, so the dictionary-domain table is named (DM) in the script and the note.
- `docs/design/CLAUDE.md` was not touched (it is close to its size limit; no file was added under `docs/design/`).

## FIXES APPLIED BY ID

Every disposition in `dispositions.md` was applied. §4F of the note has the full table, one row per finding id, each
with what changed and where. The fixes by id:

- ZERO-EMPTY (RULING-1, RULING-2, OWNER-2, SIM-6):
  - The manager's zero-pass wording is now quoted VERBATIM from CF:1553-1557 in J7, and item 5 is restated to match.
  - The product/non-product split is labelled as lane jcfold2's repair.
  - §4E corner 1 is restated as a clash among three ruled points.
  - The (ZJ-E) rows are labelled computed, not engine-run.
  - **zero-pass-empty** is added to §8.
  - §9 row 45 now holds the verbatim wording and says what waits on the owner.
- GROUP-ZERO (RULING-3): the J7 sentence is in place, labelled the manager's reading. D9, D11 and D14 are marked
  "FOLLOWS under that sentence". Rows 16 and 45 are updated.
- UNREACHED-PAIRING (SIM-2, SIM-5):
  - SIM-2: the "never reached in §4.2's sense" clause is in J7 and in the §4B.1 LOOPED row, with the nested witness
    (derived, not run).
  - SIM-5: the case is folded into **pairing-loop**, re-drafted whole in three parts (in the note's §8, and in full
    below).
  - §4D D3 gains a fact note, not a repair.
- DICT-DOMAIN (SIM-1, SIM-3):
  - The DOM reading is stated in J4 and 4A.4 (4), labelled the manager's reading.
  - Item 7's expansion and LEVEL are restated, and the `m = 00` `default.unused` consequence is in 4B.1 (b).
  - Table (O) is cited as the PADDED count at all five sites. Unpadded it is 1,800 under DOM, and `10:00` is in
    neither set.
- TUPLE-BINDING (CENSUS-2): one sentence in 4A.4 (5), labelled the manager's reading, plus the error. Also in rows 17
  and 21.
- MIXED-RECORD (CENSUS-3): one sentence in J1, labelled the manager's reading, plus the label-twice ruling. Also in J9
  and row 14.
- DOLLAR-COMPONENT (SIM-7): the value LEAN goes into J4 and 4A.4 (4). Row 10 carries it, and row 28 no longer retires
  it.
- SIM-4: LEVEL, item 7 and row 26 now say that the SET is a finite union of products, taken per pass inside the loop
  for looped labels.
- RULING-4: CF:648 is cited, and the rest of the entry stands (§8; rows 31, 36, 46).
- RULING-5: "every SET carries an arity; macros as today" (J3, 4A.4, row 9).
- RULING-6 (DOC): the record-with-default spelling is cited to 11:05 + §4B.1, not to 11:35 (J9).
- RULING-7: the header is restated: answered through 13:16, three items open.
- The label-twice ruling (freeze drift) is folded into the header, item 1, §3, §4D D26 and its tally (26 of 26
  follow), §7 item 3, §8 ANSWERED, and §9 rows 27, 42, 43, 44. The lane's proposed warning is renamed `label.both_sides`.
- CENSUS-1: the three discriminator phrases in 4A.7. The "no existing row changes meaning" claim is restated, and the
  extent sentence goes in row 22.
- CENSUS-4 (BY DESIGN, listed): item 8, 4A.7 (the "the one pair" sentence is corrected), and row 6. It admits 3 vs 6
  of 11,000 and differs on 3.
- CENSUS-5: row 6 gains the two LEGAL-DIFFERENT pairs. Row 27 gains the proposed warning, marked as a proposal, not
  ruled.
- CENSUS-6 (DOC): row 21 says six on §5.4's basis and ten on 4A.7's.
- OWNER-1: G1's measurable form now counts both sides alike, and the two-sided COUNTED ALIKE table with a REUSE
  column is in §3.
- OWNER-3: G2 is restated by his criterion, and §5's tally is read by it (one non-compare problem simpler, four the
  same, none worse).
- OWNER-4 (DOC): G3's measurable form names the compare's price and what it exposed.
- OWNER-5: J8 gains the distributes-over-`|` rule, labelled the manager's reading. 4A.4 (6) and the new row 53 are
  updated. `predicates_future.md` item 2 is NOT edited.
- OWNER-6 (PLAN): new §9 row 54, one declared absence table in §4.2, with no answer change.
- OWNER-7 (NOTED): one paragraph in item 5. U1 and U2 are not filed.
- REV20-1..10: explicit rows. Cites are widened in rows 2, 5, 8, 11, 12, 17, 34, 36, 38, 41, 42 and 43. Rows 47-52
  are NEW. Row 43 uses the "ANSWERED records stay as history with a superseded-by pointer" phrase for §13 records
  only, as allowed.
- §9 is brought fully up to date: rows 47-54 are new and the intro is marked.

## QUESTION DRAFT zero-pass-empty

**The question in one sentence.** If a loop runs zero times and the set of allowed pairs is EMPTY only because of a
value read from this match, should the condition still check the label that sits outside the loop (and so fail), or
should it hold, as the two one-label conditions joined by `&` would?

**Background.** Three of your rulings meet at this one corner, and on it they cannot all hold:

1. **set-arity** (10:26, "Set arity: yes. It's clean. I like it"). There is one kind of set, so two ways of writing
   the SAME set must give the same answer.
2. **record-is-product** (11:35, "record-is-product: absolutely. ..."). `(h: S, k: T)` IS `((h, k): (S, T))`.
3. **zero-pass-record** (12:45, "zero-pass-record: I agree ..."). The record says "the draft's equality
   `(a: S, b: T)` = `(a: S) & (b: T)` holds at every depth".

When the set is empty, rule 3 makes `(h: S, k: 3)` hold on zero passes, because each single-label condition holds.
Rule 2 makes it the empty set of pairs. Rule 1 then makes it answer the same as every other spelling of the empty set.
The manager's wording of 12:45 ("the outside labels' values must be possible under R for some value of the looped
parts") makes every such spelling FAIL.

**Smallest example (run).** The pattern is `/(?<a>\d)-(?<k>\d)(?:;(?<h>\d))*/` and the subject is `0-3`: a = 0, k = 3,
and the loop runs zero times. Both conditions below mean the empty set of pairs at a = 0.

| rule | `(h: <$a, k: 3)` | `((h, k): < ($a, 0))` | keeps set-arity | keeps record-is-product | keeps the `&` equality |
|---|---|---|---|---|---|
| the `&` reading (for the second spelling, its hand expansion `(h: <$a) \| (h: ==$a, k: <0)`) | HOLDS | HOLDS | no (C1 vs C2 at a = 0: 9 of 1,110 differ) | yes | yes |
| lane jcfold2's split (a product: each part on its own; otherwise the projection over every string) | HOLDS | FAILS | no (1 of 1,110 differ: `0-3`) | yes | yes for products |
| the record's wording unsplit (the projection for any set, over every string) | FAILS | FAILS | yes (0 differ) | yes | no (`0-3`) |
| THE LEAN: ONE rule, the projection, with the looped values drawn from their groups' strings | FAILS | FAILS | yes (0 differ) | yes | no, one documented exception |
| a fourth clause "R empty: holds" (the critic's) | HOLDS | HOLDS | yes (0 differ) | yes | no: it also holds `(h: <$a, k: 3)` on `0-5`, where k is untested (9 of 1,110 a = 0 subjects differ from `&`) |

All counts are from table (ZE), 11,100 subjects per condition, with a, k in 0..9 and 0-2 passes. Every rule except
the `&` reading is engine-run as an unfold. Over the whole population, the lean differs from the `&` reading on 1
subject for the first spelling (`0-3`) and 10 for the second (`0-0` .. `0-9`). With one or more passes, every rule
gives the same answer.

**What the draft's empty-intersection error does.** `predicates_draft.md:1941-1942` (§5.2) says: "At NARROWING SITES
(condition literals, an `&` whose operands come from definitions) an empty intersection from pure parts is an ERROR; a
dead branch WARNS (`dead.branch`); nothing when emptiness is match- or parameter-dependent". Its status is LEAN: §5.2
STATUS says "The empty-intersection error scoped to narrowing sites: LEAN (review RUL-6)".

- The CONSTANT spellings `(h: <0, k: 3)` and `((h, k): < (0, 0))` are compile ERRORS under it (computed: R against
  `\d` x `\d` is empty).
- A set row that cannot meet its label's group, such as `("x", 3)` with h `\d`, is a dead branch and draws a warning.
  This was derived by the round, not run here.
- So the question exists only where the emptiness depends on the match, which is the `$a` example above.

**Forces.**

- One rule is simpler than two clauses, and the product/non-product switch is not even a function of the set: the
  empty set factors more than one way. This supports the lean.
- The `&` equality is what you ruled at 12:45, for "saving people from themselves". The lean keeps it everywhere except
  this corner.
- Reading the looped values from their groups' strings is what a reader of the pattern expects. It is also the
  narrowing view the draft already uses.
- Emptiness that depends on the match is rare.

**The manager's lean.** ONE rule: "the outside labels' values must be possible under R for some value of the looped
labels drawn from their groups' strings". The draft's empty-intersection error covers the constant spellings. The `&`
equality then has one documented exception: a part that is empty only through a match value FAILS on zero passes.

**The lean on the existing populations** (table (ZE-L), lean engine-run):

- (RZ), 1,110 subjects: 0 differ from the `&` reading and 0 from jcfold2's split rule.
- (ZN), 2,526 subjects: 0 and 0.
- (ZJ), the 50 zero-pass subjects of five non-product sets:
  - 8 differ from the hand expansion into a `|` of records. Seven are `< (0, 3)` on `0`, `1` .. `9` minus the
    possible k: corner 1, where the expansion's row `(h: <0)` holds vacuously. One is `("x", 3) | (0, 5)` on `3`: the
    domain.
  - 1 differs from jcfold2's split rule (the same `3`: over every string it holds by h = `x`; over `\d` it fails).
- (ZJ) with passes: 0 of 5,500 differ from the split, and 56 differ from the hand expansion. The 56 are the per-pass
  vs whole-match `|` look-alike, not a zero-pass effect.

**What follows under each answer.**

- The lean: rev 20's §4.2 writes one sentence, "possible under R for some value of the looped labels drawn from their
  groups' strings", plus one exception line for the `&` equality. §4E corners 1 and 2 close: constant empty sets are
  errors, and the domain is the group's strings. Nothing on (RZ) or (ZN) moves.
- The split: the `&` equality holds everywhere, but one empty set answers by its spelling. Rev 20 must define "a
  product" for a set (unclear for the empty set) and pick a domain for the non-product clause.
- The fourth clause: spelling-independent, but a condition whose set is empty for this match holds without testing
  the outside label. That goes against the 12:45 answer's direction, and it is a third clause.

## QUESTION DRAFT pairing-loop

**The question in one sentence.** When the labels of one condition sit in loops at different depths, which loop pairs
them, how do the inner loop's zero-run cases read, and what happens in a pass of the outer loop that never gets to the
inner loop at all?

**Background.** You ruled **joint-loops** (11:17, "I agree. Makes sense."). The record: "per-pass pairing by the
innermost loop enclosing every named label, a label outside that loop having its one value on every pass". You then
ruled **zero-pass-record** (12:45): the outside label is still tested when the loop runs zero times, and
`(a: S, b: T)` = `(a: S) & (b: T)` at every depth. Three parts remain open.

**Part 1, the wording.** Please confirm: "the pairing loop is the DEEPEST loop that encloses any named label; every
other named label lies inside the same pass of it or outside it, and then has ONE value per pass; otherwise it is the
sibling-loop error". The ruled words, read literally, miss two cases:

- one label outside every loop, where no loop encloses both labels;
- one label in an inner loop nested in the other's loop, where the loop enclosing both gives the inner label several
  values per pass.

**Part 2, zero passes read per reach.** Each time a pass of the outer loop reaches the inner loop and the inner loop
runs zero times, that reach gives its own tuple with the inner part EMPTY. For records this is exactly the `&`
reading: table (ZN), 0 of 2,526 differ (`jcfold2_check.py`, `timeout 120 python3 -I
docs/dev/lanes/jcfold2_check.py`). It MOVES answers the earlier text gave you. On jcfold's (NL) population,
`/(?:(?<h>\d):(?:(?<k>\d),)*;)*/ & ((h, k): >= (5, 3))`, 10 of 73 answers move. For example, `4:;` used to hold and
now FAILS, because no k makes (4, k) at least (5, 3). The earlier question text said "No answer changes on any case he
was shown (table (NL): 73 subjects, 0 differ)", and that no longer holds.

**Part 3, a pass that never reaches the pairing loop.** The pattern is `/(?:(?<h>\d)(?:-(?:(?<k>\d),)*)?;)*/`: each
item is an h, optionally followed by `-` and a loop of k's. A pass that skips the optional never reaches k's loop.

- Smallest example: `(h: <5, k: <5)` on `3-2,;9;`. Pass 1 pairs (3, 2). Pass 2 has h = 9 and no reach.
  - The text as written pairs nothing in pass 2, so the condition HOLDS (h = 9 is never tested).
  - The ruled `(h: <5) & (k: <5)` FAILS (9 is not < 5).
- The candidate sentences, each with its matching single-label sentence:
  - (W) "a pass that never reaches the pairing loop reads like a zero-pass reach: one tuple (h, EMPTY), h tested".
    The matching single-label sentence comes in two forms:
    - (W'): W, plus "if NO pass reaches k's loop, k is unset in the match (J6 fails it)". This matches TODAY's
      single-label rule, §4.2's per-match boundary (RULED BY ACCEPTANCE, CF:997-1000; the exact wording of "reached",
      LEAN). No new single-label sentence is needed.
    - (W) alone needs "such a pass gives k zero iterations". That departs from §4.2 on `3;`, where no pass reaches k:
      §4.2 says FAILS, (W) says HOLDS.
  - (Y) "k is unset in that pass, so the pass FAILS (J6)". The matching single-label sentence: "a pass that did not
    set k FAILS `(k: T)`". That is the draft's per-iteration reading at :1694 ("a label the iteration did not set is
    unset in it"; §2.6 THE ITERATION'S OWN VALUES, LEAN), read over the outer loop's passes.
- Does `(a: S, b: T)` = `(a: S) & (b: T)` survive? Table (UP) has 241 subjects: 0-2 outer passes, h in 3, 4, 9, and
  k's optional skipped, empty, or 1-2 values. W and Y are engine-run; the rest are computed.

| joint reading | vs `&` with today's per-match k rule | vs `&` with "zero iterations in that pass" | vs `&` with "a pass without k fails `(k: T)`" |
|---|---|---|---|
| the text as written | 8 differ (`3-2,;9;`) | 14 | 24 |
| (W) | 6 (`3;`) | **0** | 22 |
| (W') | **0** | 6 | 16 |
| (Y) | 16 (`3-2,;4;`) | 22 | **0** |

| subject | as written | (W) | (W') | (Y) | `&`, today's k rule |
|---|---|---|---|---|---|
| `3-2,;9;` | HOLDS | FAILS | FAILS | FAILS | FAILS |
| `3-2,;4;` | HOLDS | HOLDS | HOLDS | FAILS | HOLDS |
| `3-2,;3;` | HOLDS | HOLDS | HOLDS | FAILS | HOLDS |
| `3;` | FAILS | HOLDS | FAILS | FAILS | FAILS |
| (empty) | HOLDS | HOLDS | HOLDS | HOLDS | HOLDS |

On a set that is not a product, `((h, k): >= (5, 3))`, the readings split the same way. On `9-5,;4;`, W and W' FAIL
(h = 4 cannot reach (5, 3)), Y FAILS, and the text as written HOLDS.

- What follows:
  - Under (W'), the equality survives with NO change to the single-label rule. Rev 20 adds one sentence to J7 and the
    absence table (§9 row 54) gains one row.
  - Under (Y), the equality survives only if the single-label rule also reads per pass of the outer loop. That changes
    today's per-match answers on 16 of 241 subjects, `3-2,;4;` among them.
  - Under the text as written, the equality fails on 8.
- The same root at one depth is THE OPTIONAL-IN-A-PASS CASE below. Its answer depends on the same choice: per pass
  (Y-like) or per match (W'-like).

**Leaning.** None is offered by the lane. The manager's lean is not in the dispositions file for part 3.

## THE OPTIONAL-IN-A-PASS CASE

Facts only; nothing repaired. The case is `/(?:(?<h>\d+)(?::(?<m>\d\d))?,)*/ & (h: <10, m: <30)` with no default, on a
list where one item has no minutes. Table (OP) has 259 subjects: 0-3 items, h `3` or `12`, minutes absent, `15` or
`45`. The record is engine-run; the `&` readings are computed.

- **What the ruled text answers: FAILS.**
  - J9 (RULED, record-is-product, CF 11:35) makes the record `((h, m): (<10, <30))`.
  - J7 (RULED, joint-loops, CF 11:17) pairs per pass of the item loop.
  - J6 (RULED, unset-component, CF 11:05, his words "unset-component: yes"; the record: "an unset label fails the
    condition (single or joint) unless the author wrote a default") fails the pass whose m is unset.
  - That J6 applies PER PASS is the lanes' reading, not a ruled sentence. It is §4B.1's LOOPED row ("an iteration
    whose item skipped the label reads the default", lane unsetdef), and the draft's :1694 ("a label the iteration
    did not set is unset in it", §2.6, LEAN) agrees.
  - So `3:15,3,` FAILS.
- **What `(h: <10) & (m: <30)` answers: it depends on the single-label reading, and two draft texts point opposite
  ways.**
  - (A) m's iterations are the item loop's passes, and a pass without m leaves m unset in it, so `(m: <30)` FAILS. This
    is :1694 + §4.2's "a condition naming a label that is unset ... fails", per iteration; §2.6 is LEAN.
  - (B) m's iterations are the values m took. The sequence rule ("`x: S` constrains ALL iterations", RULED CF:583)
    holds over [15], and §4.2's per-match boundary (RULED BY ACCEPTANCE) fails m only when m has no value in the whole
    match. Under (B), `3:15,3,` HOLDS.
- **Does the ruled equality `(a: S, b: T)` = `(a: S) & (b: T)` hold there?** It depends on the reading:
  - Under (A): yes, 0 of 259 differ.
  - Under (B): no, 8 of 259 differ. The smallest example is `3:15,3,` (record FAILS, `&` HOLDS), then `3,3:15,`.
  - Neither ruled sentence picks between (A) and (B): the CF 12:45 equality's record speaks of depth, not of an
    optional inside a pass.
- **Does §4D row D3, as worded, cover it?** It covers it in WORDING but not in FACT.
  - D3 says FOLLOWS "when the labels are set once or in the same pass". h and m are in the same pass, so the case
    falls under it.
  - D3 FOLLOWS only under reading (A), which D3 does not state. Round jointcond's ruling lens reached the same verdict
    on `/(?:(?<g>\d)(?<h>\d)?,)*/`: "both fail ... under draft :1694 + :1590 and J6".
  - The note now carries this as a fact note in D3 ([§4F]), not a repair.
- **What it means for pairing-loop part 3.** (OP) is the one-depth form of the same question:
  - per pass, (A), matches (Y);
  - per match, (B), matches (W').
  - The two cases are the same choice, so asking pairing-loop part 3 alone would leave (OP) to follow from the answer
    by analogy.

## NOT DONE

- Nothing in the dispositions was left unapplied. No disposition contradicted an owner ruling in the record. No
  FIX-NOW needed a choice between two readings that the dispositions file left open.
- Not done, by the brief: `predicates_draft.md`, COND-FAMILY.md, `predicates_future.md` (item 2's line for OWNER-5 is
  the manager's), and any skill or guide file. That includes process changes 1-4, the guide lessons, and the framework
  note, which the dispositions assign elsewhere.
- Not run here:
  - the SIM-2 nested-default witness (`(c: 3..7, k = 9: <5)` on `5`), derived by §4.2 + J7 and run by the critic's
    script;
  - the dead-branch claim for `("x", 3)` with h `\d`, derived by the round;
  - the per-reach (ZN)/(NL) numbers, which are cited from `jcfold2_check.py`, not re-run by `jcfix_check.py`.
- Part 3 of pairing-loop has no lean in the dispositions file. The draft above gives none rather than inventing the
  manager's.
- Process gaps to flag:
  - The brief's (DD) letter collided with an existing table, so the table is (DM) (STATE AT HANDOFF).
  - The (W) vs (W') distinction (whether a match where NO pass reaches k's loop leaves k unset) is new in this lane.
    It is what lets (W') keep today's single-label rule unchanged.
