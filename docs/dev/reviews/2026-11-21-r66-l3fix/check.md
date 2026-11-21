# CRITIC CHECK: l3fix (review r66)

## Findings


### CHECK-1 — CONFIRMED — maintenance (check adequacy) — effort S — blast: DD12a(i) only
The NEW [l3chk] one-sided-run arm of DD12a(i) (tests/codegen/run_encoding_checks.sh ~1785-1813 in the subject
tree, commit 05ea100ea) has no red witness and no counted floor. Its counter `RUN_ONE_SIDED` is printed by the
python (line ~2098) and READ BY NOTHING (grep: line 2098 is its only occurrence; no shell floor, no sabotage row
names the arm). The arm's effect is to set `gate_ok[rside]`, which drops the one-gate memchr bytes from `scanned`
in the REQ_BYTE rule (~1887). Repro (by hand, the arm's code extracted into $OUT/oneside.py): the only two
reaching pairs, `(?<=a)(b)\1x` (byte RX_REQ_RUN "6162@1"/HANDOFF -1, utf8 "none") and `(?i)(?<=ab)(b)\1x`, are
COVERED (have {120} want {98,120} got {98} -> True), so the mutant "coverage test always passes"
(`if not (...)` -> `if False`) is answer-identical on today's population and nothing goes red: the arm's red
branch (`cov_bad` "one-sided run ... not covered") has no witness. (A non-reach of the arm IS loud: the REQ_BYTE
rule reds the run-bearing side, the pre-l3chk state.) learnings §3 K35-shape: a population nobody counts.
Expected: a floor `RUN_ONE_SIDED >= 2` (the two UNDECLARED rows) and one plant (e.g. drop the run-scan
`got` term, `want - have <= set()`), which turns the covered pair red — or a stated reason none is needed.

### CHECK-2 — CONFIRMED — doc (check comments) — effort XS — blast: 3 comment sites
Three check comments say review r65 A's pick rule "moved `(?<=a)(b)\1x` back to BASE's run-free form on the
default route": S3450's RE-AIMED comment (tests/mech/sabotages/S3450_dd12a_presence_order_lost.sh), and
run_encoding_checks.sh ~1577-1580 and ~2181-2182. True for utf8 ONLY. Repro:
`kit/pc subject --features all --emit-facts --pattern '(?<=a)(b)\1x'` -> byte req_whole_run 6162, req_landmark_maxoff
-1 (identical to reviewed 3f02ca8ab; BASE: none/unbounded); with `-e utf8` -> none/unbounded (reviewed: 6162/-1).
The k50 manifest's new block states it correctly (byte "6162@1" handoff -1, utf8 none). The witness re-aim to
`ab(c)\1x` is RIGHT (the pair no longer states a run on both sides), but the reason given is wrong; a reader
re-aiming later would believe the default byte route has no K<0 run here. Also the observation behind it: the
`displaces` decision reads `root->best`, which the byte-rate prior (byte-only, D123-4) picks, so the pick rule
itself is encoding-keyed on this pattern (byte: best `x` unbounded -> BACK displaces; utf8: kept). Recorded by
l3chk as UNDECLARED; noted here only because no check pins the byte side's -1 for this pattern ([facts-look] has
no row for it).

### CHECK-3 — CONFIRMED — test-coverage — effort XS — blast: one pattern shape (the pick rule's third disjunct)
`(?<=xyz)a+xyz` is the pick rule's DEFAULT-route keep (BACK `xyza` at K -3 over an unbounded consumed `xyz`;
RX_DFA_PREFILTER "memchr", RX_REQ_HANDOFF "-3"), pinned by [facts-look] and [5.12a] and named as S3405's reach,
but its only answer cells are `engine vm` (tests/litscan/handoff_vm.rxt:754 block; `git grep 'pattern (?<=xyz)a+xyz'`
finds only that one). Repro: `printf '1:xyzaxyz\n2:qxyzaxyz\n' | $OUT/ms.sh plant:S3412 '(?<=xyz)a+xyz'` (default
route, rx_search with start offset) -> nomatch / nomatch; subject and oracle (kit/oracle.sh ... 1 / 2) -> (3,7) / (4,8).
S3412 is still DETECTED (its vm cells, and the default `(?<=foo)` block in spanarms.rxt also moves: "foo"@1 nomatch
vs (3,3)), so no row is undetected today; but the one default-route compile shape the third disjunct
(`lo < hi && best->off >= PCREC_W_UNBOUNDED`) keeps on K < 0 has listing pins only and no answer witness on its own
route (DFA hybrid + start-byte prefilter + K < 0 run pre-check). Expected: a default-route copy of the handoff_vm.rxt
block (the generator gen_handoff_vm.py emits only vm).

### CHECK-4 — SUSPECTED (held by reasoning; plants requested below) — test-coverage — effort S — blast: the pick rule
Sub-part (b). No sabotage row flips ONE disjunct of `rb_top_back_displaces` (src/facts/req.c ~1708) or one conjunct of
`fwd_reentry` (src/facts/facts.c ~259); S3455 is the all-true mutant (column passed over). Each single mutant, the
witness that separates it, and the check line that would go red (run by hand on SUBJECT green; on plant:S3455 where
the direction matches):
| mutant | witness (route) | subject | mutant value (reasoned) | red line | covered by an existing plant? |
|---|---|---|---|---|---|
| M1 drop `!fwd_reentry` (rule applied everywhere) | `(?<=foo)bar` --engine=vm | 666f6f626172 / -3 | 626172 / 0 (the default route's value, fwd_reentry true) | [facts-look] `p --engine=vm (?<=foo)bar req_whole_run 666f6f626172` (+ every vm L3 row, W-D2 vm row) | NO (S3455 is the opposite direction; vm rows stayed green on plant:S3455) |
| F-a drop `engine != PCREC_ENGINE_VM` | same | same | same (vm no longer forces false; NO_REQ_HANDOFF is not implied by --engine=vm: git grep shows it set only by the axis) | same | NO |
| F-b drop `!NO_REQ_HANDOFF` | `(?<=foo)bar` -fno-req-handoff | 666f6f626172 | 626172 | [facts-look] `p -fno-req-handoff (?<=foo)bar req_whole_run 666f6f626172` (+ the run_pin rows) | NO |
| M2 drop `best->n == 0` | `(?<=foo)` default | 666f6f (lo=hi=3, kept only via n==0) | none | [facts-look] `p - (?<=foo) req_whole_run 666f6f` | NO (opposite direction; that row green on plant:S3455) |
| M3 drop `lo < hi` | `(?<=foobar)\d*x` default | none | 666f6f626172 | [facts-look] `p - (?<=foobar)\d*x req_whole_run none` | YES in effect: plant:S3455 reds exactly this row (observed got 666f6f626172) |
| M4 drop `best->off >= UNBOUNDED` | `(?<=foo)bar` default | 626172 / 0 | 666f6f626172 / -3 | [facts-look] `(?<=foo)bar` default rows; [5.12a] `(?<=foo)bar(\w)\1%-e byte%0%0` | YES in effect: plant:S3455 reds these rows (observed) |
| M5 drop the whole third disjunct | `(?<=xyz)a+xyz` default | 78797a61 / -3 | 78797a / unbounded-or-0 (BASE's consumed best) | [facts-look] `(?<=xyz)a+xyz` both rows; [5.12a] `(?<=xyz)a+xyz%-e byte%-3%-3` | NO (opposite direction) |
So every single mutant has a red check line by reasoning, but the four NARROWING mutants (M1, F-a, F-b, M2, M5) are
held only by reasoning: no plant exercises them, and all answers are sound either way (no harness cell can see them;
only the listing rows can). Confirm with the three plants below.

## PLANT REQUESTS
(For CHECK-4. Each is ONE line of the SUBJECT, SAB_COUNT=1; detector = tests/codegen/run_facts_checks.sh
[facts-look]; expected red line named. Each is the narrowing direction no existing plant takes.)
- P-M2 (src/facts/req.c):
  SAB_BEFORE='    return !w->fwd_reentry || best->n == 0 || (lo < hi && best->off >= PCREC_W_UNBOUNDED);'
  SAB_AFTER='    return !w->fwd_reentry || (lo < hi && best->off >= PCREC_W_UNBOUNDED);   /* PLANT M2 */'
  expect red: `p - (?<=foo) req_whole_run 666f6f` (got none).
- P-M5 (src/facts/req.c):
  SAB_BEFORE='    return !w->fwd_reentry || best->n == 0 || (lo < hi && best->off >= PCREC_W_UNBOUNDED);'
  SAB_AFTER='    return !w->fwd_reentry || best->n == 0;   /* PLANT M5 */'
  expect red: `p - (?<=xyz)a+xyz req_whole_run 78797a61` and `req_landmark_maxoff -3`; also run_prechecks.sh [5.12a]
  row `(?<=xyz)a+xyz%-e byte%-3%-3`.
- P-Fa (src/facts/facts.c):
  SAB_BEFORE='        .fwd_reentry = cx->opt->engine != PCREC_ENGINE_VM &&'
  SAB_AFTER='        .fwd_reentry = /* PLANT Fa */ true &&'
  expect red: every `p --engine=vm` L3 row, e.g. `(?<=foo)bar req_whole_run 666f6f626172` (got 626172), and the
  reqcube ws4c / S3413-reach shape (`(?<=qz)ab` vm would lose RX_REQ_HANDOFF "-2"), and the vm reaches of S3406/
  S3409/S3410/S3411/S3412/S3413 would stop reaching (their witnesses depend on vm keeping BACK).
Lens check verifies by running `$OUT/lk.sh plant:P-xx $OUT/lookrows.tsv` (the [facts-look] p rows, by hand).

## PROBED-AND-HELD
Reach = the row's SAB_REACH run by hand on SUBJECT (all 12 printed their SAB_REACH_EXPECT). Plant class from the
detector's own witness cell(s) run by hand, plant vs subject (answers via a start-offset driver $OUT/ms.sh; listings
via $OUT/lk.sh = the 49 [facts-look] p rows; [5.12a]/reqcube/DD12a(i) lines extracted and run by hand).
| row | reach | plant class (witness) | detector red |
|---|---|---|---|
| S1887 | yes (vm run+K abcx -3) | LOUD answer: startpos.rxt `ms 3 "abcx"` nomatch vs (3,4), default route, features lookaround | yes |
| S3381 | yes | SILENT-MOVE listing: `(?<=ab)(?<=cb)c` why dead lost, default and vm rows | yes (2 [facts-look] rows) |
| S3405 | yes | LOUD: `(?<=xyz)a+xyz` -e byte refused, "internal error: a prefilter keeps a re-entry site at a negative K" | yes ([5.12a] refused) |
| S3406 | yes | LOUD answer: `(?<=a)a(\w)\1` vm "-aaaaaq-b"@3 (2,5) vs (3,6) | yes (spanarms vm cell) |
| S3408 | yes | SILENT-MOVE listing: req_byte 114/111/97 vs 120/none/98 (vm rows) | yes (3 [facts-look] rows) |
| S3409 | yes | LOUD answer: a^20 b^8 z b^11 vm nomatch vs (20,40); default unchanged | yes (vm cell) |
| S3410 | yes | LOUD answer: `(?<=ab)ab[a-z]*q` vm "abababq"@3 (2,7) vs (4,7) | yes (vm cell) |
| S3411 | yes | COMPILE-CATCH: -Wsign-compare error under the harness GENCFLAGS | yes |
| S3412 | yes | LOUD answer: `(?<=foo)bar` vm "foobar"@2/@3 nomatch vs (3,6); also default `(?<=foo)` and `(?<=xyz)a+xyz` | yes (CHECK-3 notes an unwitnessed default shape) |
| S3413 | yes | SILENT-MOVE stamp: RX_REQ_BYTE 122 vs 98 (not in req_set {97,98}) | yes (reqcube check 4) |
| S3450 | yes | test-script plant: unplanted fragment takes the order arm on `ab(c)\1x` (byte gate (120,) / utf8 set (120,), members equal); planted never does -> PRESENCE_ORDER 0 < floor 1 | yes (by the extracted fragment + floor reading) |
| S3455 | yes | SILENT-MOVE listing: 7 default-route [facts-look] rows red | yes |
Re-pins checked against BASE (an independent anchor, not the subject): cpset `(?<=foo)bar` EMITTED_BYTES 38505 = BASE
38505 (reviewed 39608); D27 A22 7374 and C07 none = BASE; FILEPIN f487fbd0f = the delta's last src commit (self-pin
convention, held); d3 census `(?<=ab)ab(\w)\1` default facts = BASE's (a new corpus pattern, not a mover); k50
UNDECLARED rows are an exact-equality list (a wrong re-pin reds). [5.12l]'s deleted K<0 arm: a K<0 forward artifact
would now fail its nd==1 count or the compile's internal error (S3405 shows the latter). Not held: CHECK-1..4.
Compile count: 203 (budget 500). MINIMUM witness `(?<=foo)`; LONGEST `(?<=aaaaaaaaaaaaaaaaaaaa)bbbbbbbbzbbbbbbbbbbb`.

CRITIC COMPLETE
