# CHECK lens: check adequacy, memfn-sp1a (SUBJECT c0c73bc20 vs BASE 564db08c5)

Method: ran decider_census.py on the review tree; 20 planted/edited copies under this dir (p1..p20, each a copy of
memfn/src + the census files); drove reach_equal.py with a fake-binary harness (re/) that prints MFTRACE REACH
lines (real traced builds and the lane's job scripts not available to me: the real REACH output of base/HEAD,
whether R3a/R3b/R4 lines appear at base, and whether the traced HEAD library registers the same rows were NOT seen;
by gate.c:884-911 every registry row prints a line each compile, even at chosen=0 asked=0).

## Findings

### CHECK-1 (SUSPECTED->CONFIRMED by harness; contract/design; small effort) reach_equal passes when a SURVIVING row's lines vanish at HEAD, if its counts are zero
reach_equal.py:134-140 compares `b.get(k,0) != h.get(k,0)`; absent == 0. Harness `dropZ` (row fd/Z printed
chosen=0 asked=0 at base, absent at HEAD, NOT named in --gone): rc=0, differ=0. The design says deleted rows' LINES
are the declared difference, so the surviving-row-set should be equal as a set, not just as sums. Real exposure:
R8, R1, R2 (pending-site, zero reach by their own rows.tsv entries, "SUSPECTED" asked) and any zero-reach
surviving row (PAIR? D1c?) could be deleted undeclared (or the 1f delete mistaken for 1a's) with rc=0. Fix: compare
`set(b)` keys-with-lines vs `set(h)` less --gone rows' lines; keep zero-count lines as keys. One line of code.
Blast radius: 1a (3 gone rows) and every later unit using the witness (1f, 1e's row map).

### CHECK-2 (CONFIRMED; design; small) --gone is operator-supplied, not derived, and nothing requires it
Harness `nogone` (no --gone at all, identical sides): rc=0. A typo'd row name does go red (at_base False), and a
gone row still present at HEAD is red; but the script never checks that the declared set equals the rows removed
between the two trees (e.g. finder.c's fd_rows / rows.tsv diff). A unit run without --gone, or declaring a SUBSET
of what it deleted, is not detected on the deleted rows themselves except via CHECK-1's blind spot (nonzero-count
deleted rows do go red as "differ"; zero-count ones pass silently). Effort small: derive gone = rows with lines at
BASE and not at HEAD, and require it == the declared list (both directions); then the declared difference is a
derived-and-checked set, not a hand-typed pass mask.

### CHECK-3 (CONFIRMED; design; small) aggregate sums hide compensating moves
Counts are summed over the whole population per (arm,key). Two patterns swapping rows (A:X->Y, B:Y->X) leave
every sum equal. The design says "chosen and asked per row equal"; sums satisfy the letter. Per-pattern equality
(compare each pattern's Counter, report first differing pattern) costs the same compiles (already one process per
(side,pattern,arm)) and memory ~ keys x patterns. Not harness-probed (evident from reach_equal.py:128-141).

### CHECK-4 (CONFIRMED by reading; speed/K35; trivial) `--limit` disables the population floor entirely
reach_equal.py:104 `if len(pats) < POP_FLOOR and not a.limit`. `--limit 1` or `--limit 100000` both skip K35.
Legit for a smoke run, but the verdict trailer `DONE rc=0` is the same line as a full run's and scripts/verdict
reads that. Make the trailer say `limited` or return rc!=0 when limit truncates below POP_FLOOR.

### CHECK-5 (CONFIRMED by reading; small) compile failures not distinguished from "no REACH output"
reach_of ignores returncode. A HEAD crash (segfault/abort before atexit printing REACH) on pattern P contributes
zero lines, which shows up only as a sum difference IF P reaches a row. Pattern that crashes without reaching any
row: invisible. Compare returncode between sides (same set of failing patterns), and count nonzero rcs per arm.
Timeouts are compared as counts only (reach_equal.py:150): base timing out on P and head on Q is "equal".

### CHECK-6 (CONFIRMED by plants p5,p13,p16,p17; design/maintenance; small) decider census: what the backstop does not reach
All verified by planted copies (rc in parens):
- `if (best > a[i])` new decider loop appended to window.c, unlisted fn: GREEN (0). The backstop list is a NAME-style
  filter (docstring admits, "> c)" only). `< best` spelled `best >` escapes. Expected by design, but not named in the
  design's plants; the census is a ratchet on 10 spellings, not on decider-ness.
- a new loop inserted INSIDE a listed function (a_floor_holds; also would pass in a 5th loop of kit_pres_picks
  because all `part` rows span the WHOLE function, decider_census.py:167-179): GREEN. A part's span is the function,
  so the anchor only proves the function holds the part, not where the hit lies. Design: "plants: byte-identical
  copies in an UNLISTED function" so by design, but a part row licenses every shape in that function.
- hits in `memfn/src/*.inc` or a subdirectory (os.listdir, one level, ext c/h/def): GREEN (0). Matches the design's
  glob; recorded only because a kit file with another extension or a sub-dir is invisible.
- 27 of the 50 map rows carry NO backstop hit (hitmap.py: fd_route, fd_find, fd_pres, vrun_kb, 14 window.c fns,
  tie_over, implied_by, kit_set_test, member_test, pred_test:run-chain). Those rows are protected only by "exists";
  deleting a row is caught only by MEMBER_FLOOR 45 vs 50 rows: p12 (drop 6 zero-hit rows) goes red at the 6th, p4 (drop
  1 zero-hit row, run_group_ok) is GREEN. So the ratchet "a unit that moves a decider edits its row" is not
  enforced for these rows: a unit can delete/rename a row silently up to 5 rows. Hit-carrying rows ARE protected
  (p10 drop tie_takes: 2 stray hits, red; p11 drop kit.h excluded row: red).
- p18: a prototype-only forward declaration `static int ghost_fn(int);` satisfies check A for a `fn` member
  (definitions() returns prototypes as items). A decider deleted but still forward-declared keeps its row green.
- p20: when a plant anchor disappears (run_member's loop respelled) the checker dies with a StopIteration traceback
  (rc!=0 but not a labelled FAIL; census prints no verdict line). Acceptable but ugly; a respell of the anchor line
  is exactly what units 1c/1d will do.
- Comments count as hits (p14: "tie_takes is mentioned" in a comment outside a member is red). Conservative; but the
  36 base hits include comment lines, so HIT_FLOOR 30 slack (6) is partly comment text: a unit that deletes a decider
  AND keeps its comments does not lower hits, and one that edits comments can lower hits under the floor with no
  decider change (false red).

### CHECK-7 (CONFIRMED; doc/maintenance; trivial) KIT_SRC_FLOOR comment says 17 files, floor stays 15
run_rows.sh:16: base had 18 .c, now 17; floor 15 unchanged and the comment string is correct. ROWS_FLOOR 33 equals
12+4+4+13 exactly (no slack; the next added row raises it, as run_rows.sh says). No defect; noting that the new
floor is exact for rows and 2-slack for sources.

### CHECK-8 (SUSPECTED; maintenance) no mech/sabotage arm names the census or reach_equal
grep for decider_census outside Makefile/tests/memfn finds nothing in tests/mech or ci shards; the census's two
plants are internal (good, they run on every `make test-memfn-rows`), but reach_equal has no control that runs in
the suite: its failing direction (moved row, declared gone) is covered only by the lane's one-off run. Its
"independent control" is the --gone row, which CHECK-1/2 show is operator-typed. Confirm by grepping tests/mech for
`reach_equal` / `decider_census` (I saw none in the diff).

## PROBED-AND-HELD
- decider_census.py on the review tree, with plants: 55 passed / 0 failed, 36 hits, 0 stray, plants run_member
  (window.c, 2 stray) and presence.c `c < sm` (1 stray) both red-detected (the "two plants" of the design).
- Planted red cases: p1 add a `< best` decider fn (red, 1 stray); p2 rename member run_group_ok (red, A);
  p3 backstop hit `< lo` in a new .c (red); p9 remove a part anchor (red); p10 drop tie_takes row (red, 2 stray);
  p11 drop the kit.h excluded row (red); p14 comment hit (red); p15 new .def hit (red); p19 malformed 2-column
  map line (red); p8 empty src (red: 51 fails and HIT_FLOOR); p12 six dropped rows (red via MEMBER_FLOOR).
- The census map is hand-written and the backstop is a grep over raw text; neither reads the other (independence
  held: p1/p3 reds come from the grep alone, p2/p9 from the map alone).
- reach_equal.py harness verdicts (1202 patterns x 1 arm, fake binaries): equal -> rc0; one surviving row moved
  (asked 5->6) -> rc1; surviving row deleted with nonzero counts (dropB) -> rc1; extra undeclared row with counts
  (extra); an extra row with ZERO counts only was NOT separately probed (my substring mode made it also print the nonzero line), by the code a zero-count extra row passes like CHECK-1;
  declared row still present at HEAD (keepgone) -> rc1; declared row absent at BASE / typo (badgone) -> rc1;
  empty output both sides -> rc1 (no row chosen + vacuous declared difference); truncated output -> rc1 (vacuous
  declared row); REACH_DROPPED>0 -> rc1. It cannot pass vacuously on zero rows read.
- finder_check.py FIND_ROWS (8 ids), rows.tsv/row_floors.tsv deletions (3 lines each) and run_rows.sh floors are
  consistent with the registry count: ROWS_FLOOR 33 = 12+4+4+13; FIND_ROWS compared against the kit's own table
  (finder_check.py:189-196), so a missed edit would fail there.
- Makefile hook: `python3 tests/memfn/decider_census.py --root .` after run_rows.sh inside test-memfn-rows; a red
  census returns non-zero and fails the make target (rc 1 verified directly).
