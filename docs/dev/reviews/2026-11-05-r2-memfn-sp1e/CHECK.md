# crit-memfn-sp1e / CHECK findings (lens: check adequacy)

Method: plants built from `git archive 9de5b5638` copies (kit objects re-built at -O2, ar-swapped into a copy of the
review tree's libpcrec.a, cli/main.c relinked); plant0 (unplanted rebuild) was SAME on 12/12 patterns vs the review
build (control for the method). Row-map plants are edited copies of tests/memfn/row_map.tsv fed to the readers
(reach_equal --map; rows_check via ROW_MAP_TSV on a copy of rows_check.py whose section C is cut to 2 fd rows, section M
untouched). Nothing under either repo was written.

## FINDINGS

### CHECK-1  row-map readers: the map is checked for existence, not for correctness (CONFIRMED; maintenance; XS-S)
Drill (a). reach_equal --map (patterns file of 4, arm default, tr-base vs tr-subject):
| plant of row_map.tsv | reach_equal --map | rows_check M |
|---|---|---|
| mis-targeted D-hors -> fd/D1 | RED (rc1: fd/D-hors new, fd/D1 base 1 head 0) | GREEN 162/0 |
| D-hors line deleted (D-one only) | RED (fd/D-hors new vs base None) | not run (same code path as below) |
| D-hors declared dissolved (`- -`) | RED | not run |
| D-one declared mapped to fd/D1 | RED (fd/D1 base 4 head 2) | not run |
| D-one line deleted (D-hors only) | GREEN rc0 | GREEN 161/0 |
| fabricated line `zzT zzR fd D1` appended | GREEN rc0 (prints "mapped zzT/zzR -> fd/D1: chosen BASE 2 HEAD 2") | GREEN 164/0 (zzT joins the "mapped-away tables") |
| live row declared dissolved (`fd D1c - -`) | n/a | RED (still a row) |
| target `fd D-zzz` | n/a | RED (missing) |
| empty map | n/a | RED (blind) |
So: rows_check M cannot see a mis-aimed target (any existing row passes) nor a missing or invented line;
reach_equal catches mis-aim of the D-hors line (its count is compared) but the DISSOLVED line is print-only
("dissolved wfD/D-one arm '': BASE chosen 5") and an invented from-row that never occurs at BASE is accepted and
echoed as "mapped". Effect is small today (2 lines; D-one's absence is covered indirectly by whole-key equality, since
its selections reappear as other fd rows' counts) but the map is the declared artifact for 1e and the next unit that
moves a row will copy its shape. Fix: reach_equal red when a map line's from-row has zero BASE END records over the
whole population ("unexercised map line", the K35 shape reach_equal already applies to the target), and when a
BASE table with END records and no HEAD table is missing from the map's from-tables (derive, then compare to the
declaration, as the gone-set already is).
Refs: tests/memfn/rows_check.py:674-706; tests/memfn/reach_equal.py (dissolved print, map target branch).

### CHECK-2  the merged walk's single-decider property: bypass plants are invisible to every static/row check (CONFIRMED; design; S)
Drill (b). Three plants with NONE of the conforming call's tokens (no fd_find/renders_pair/SF_ASKER_PAIR/kit_walk/
`< best`/TIE_/pick_takes):
- B (window.c wf_find_decide, one line after the fd_find call): `if (fx->pick == FF_PAIR) fx->pick = FF_WALK;`
  (a renderer-choice that ignores the asker fact). 16 patterns: SILENT-MOVE 3 (`x[Q%]y`, `(?i)cat`, `(?i)ab`), SAME 13,
  LOUD 0; plant compiler rc 0 everywhere.
  decider_census (--root plant): 67/0 GREEN. rows_check (PAIR + D-hors rows, witnesses and controls): 162/0 GREEN
  (its fd signature is read from the trace record FDROUTE/WPATH, whose row/arm is unchanged). reach_equal subject-tr vs
  plant-tr (5 patterns): RED on `(?i)cat`, `(?i)ab` (fn/fn-pair chosen 1 -> 0) but NOT on `x[Q%]y`, which moved
  bytes with an identical reach map.
- C (compose.c fd_renderer, hard-coded early return for FF_LIBC duplicating the fd_renderers[] rows): 16 patterns SAME 16
  (equal bytes by construction); census GREEN; undetectable by any byte or trace check, and it also MASKS a later drop of
  those fd_renderers rows (the renderer table could be deleted for LIBC with no effect).
- E (finder.c: SF_ASKER_PAIR set for every asker, composer included): SILENT-MOVE 1 (`foo|bar` composer site loses
  pf_walk), SAME 15, LOUD 0. rows_check (PAIR, D-hors) 162/0 GREEN; census GREEN; reach_equal RED (arms/pf_walk
  chosen 1 -> 0).
Net: after 1e the decision "which pick" and "which renderer" has exactly one writer in the DESIGN, but nothing in the
suite asserts it. The census's own header says it only sees argmin shapes; rows_check's fd signature is the trace
record, so a renderer layer move after the walk (B) is unobserved by it even for the PAIR row whose artifact text
differs (B-pair vs walk). Only the byte-identity corpus (and, partly, reach_equal) sees B/E. Suggest (S): add a
text signature to the PAIR and D-hors rows.tsv lines (a fragment B-pair / D-hors' shift table prints, as fn rows
already do) so check C's text-vs-selection agreement bites on window rows, and an anchor line in the census for
`fx->pick =` / `->pick =` writers (one allowed writer: fd_find's out-parameter).
Refs: tests/memfn/decider_census.py header ("What it cannot see"); rows.tsv:126,130; window.c:1846.

### CHECK-3  the asker fact is constant at its only construction, so its FALSE branch has no witness (CONFIRMED by read; design; XS)
fd_stop.renders_pair is initialised with the literal 1 (window.c:1844, `fd_stop st = { ..., &f, 1 }`), the only
constructor in the tree (grep), so `if (st->renders_pair)` (finder.c:665) never takes its false arm; rewriting it as
"st != NULL" is SAME everywhere. The part that matters (the composer must NOT get the fact) is separated by `st`
NULL-ness, witnessed only by plant E above (SILENT-MOVE, caught by reach_equal/byte identity, not by rows_check or
finder_check). If renders_pair is meant to be a real input (a second window-family renderer that cannot render PAIR),
no fixture asks that question.

### CHECK-4  per-row reach table for the merged walk (drill c): three of six rows are text-invisible (CONFIRMED; design; XS)
Plant A: DROPROW env var in fd_holds (row dropped = predicate false), subject build as reference, 12 patterns
(each row's rows.tsv witness plus 6 others), default arm; D1c, D1w, R7w also under `--engine=vm` and `-fno-offset-skip`
(R7w's witness arm), 3 patterns each:
| row dropped | emitted C moves | patterns |
|---|---|---|
| D-hors | SILENT-MOVE 1/12 | `[0-9a-f]{8}` |
| D1 | 5/12 | `x+y`, `[a-z]{3}q`, `\d{3}-\d{4}`, `q[a-z]x`, `[a-z]+@[a-z]+\.com` |
| PAIR | 2/12 | `x[Q%]y`, `(?i)cat` |
| D1c | 0 of 18 (12 default + 3 vm + 3 -fno-offset-skip) | - |
| D1w | 0 of 18 | - |
| R7w | 0 of 18 | - |
Every drop: rc 0 (no LOUD). D1c/D1w/R7w are decided rows whose drop falls to the walk with the SAME text (the stage-1
zero-mover bar), so their only observation is the kit's own FDROUTE/REACH record; reach equality compares two builds'
counters, one of which is the new code, and rows.tsv carries no "text-invisible: reach is trace-only" declaration for
them. Not wrong at this stage (it is the point of zero movers) but the invariance check for these rows is one
heavy opt-in corpus run (reach_equal has no make target), and rows_check's single witness per row. Suggest declaring
them in rows.tsv/row_floors (reason class) so a later unit that makes one of them mover or unreached is a visible edit.

### CHECK-5  S1079 re-anchored plant: applies, is SAME on bytes, DETECTED by run_finder; the recorded figure does not match (CONFIRMED; doc; XS)
Apply SAB_BEFORE/AFTER to a copy of finder.c: COUNT 1; kit builds; plant compiler `build/pcrec` rc 0 on 16/16 patterns:
SAME 16, SILENT-MOVE 0, LOUD 0 (a pure trace mover, as the header says). tests/memfn/run_finder.sh against the plant
(own tree, own libpcrec.a): rc 1, `checks passed: 3160 / failed: 3`: `byte1t: decided by -`, `hat1: decided by -`,
`2 of 4 routed sites checked`; unplanted control 3163/0 rc 0. (A first plant run without build/pcrec-harness in the
copy read 3100/6, the extra 3 being "pcrec-harness not built" and two presence-part lines, not plant effects.)
SAB_DOC_FIGURE says `6fail/3155pass ... the routed census and the lever cases under their floors`; I could not
reproduce either number at 9de5b5638 (3 fails, no lever-case failure). Likely the lane's run had the harness missing
(the doc says hand-measured at 7d5d6711c). The mech run's own figure (job 427) is deferred, so the committed number is
unverified. Detection itself holds; 2 witnesses (byte1t, hat1) carry the plant.

### CHECK-6  run_g2_win.sh plant table: two plants do not apply, and nothing reads the table's anchors (CONFIRMED; maintenance; S; pre-existing)
Applied every plant_spec of the file as the --plant code does (count == 1 in the named memfn/src file): 19 of 21 resolve
at SUBJECT; S1405 (window.c `if (m->p[k].present && m->p[k].core && !count(...)) return 1;`) and S1410 (window.c
`... m->p[k].yes && !full(m->p[k].yset))`) find 0 occurrences, and the same two fail identically at BASE (not 1e's
doing). `run_g2_win.sh --plants` would therefore stop at S1405 with `fail_setup "S1405: the plant does not apply"` before
reaching S1542. 1e re-aimed S1542 correctly: `--plant S1542` on the review tree = `PLANT S1542 RED (driver passed
failed: 5200 0): FAIL: site 2501: D-hors scope: a skip table over a window wholly below the candidate` (1 run).
(d) `python3 -I scripts/m6read_check_sab_anchors.py` on the review tree: `sabotages checked: 1102 (1143 anchor sites)`,
`all anchors resolve`, rc 0 (S1079 included). It reads mech sabotages only, not this file's plant_spec, which is
why S1405/S1410 rotted unseen. Suggest extending the anchor script (or a 20-line check in run_g2_win.sh) to resolve
the plant table without running the generator.

### CHECK-7  D-hors enters with PLACEHOLDER floors in both columns (CONFIRMED; maintenance/doc; none to fix now)
row_floors.tsv: `fd D-hors PLACEHOLDER PLACEHOLDER`; rows_check prints `UNREACHED: 13 floor cells ... PLACEHOLDER`.
The row that gained the new decider code (hors_facts, finder.c:638) therefore has no population floor in the N2 census
until a later census run; its reach is held by one rows.tsv witness and the opt-in reach_equal run (which also
needs --map to see it). Stated as owed in the file (no number invented, matching the house rule), so recorded only so
the owner can see D-hors' floor is the one open reach cell of the unit. The reach_equal window drill above shows
dropping D-hors moves 1 of 12 patterns, so a floor on it would be a sensitive one.

## PROBED-AND-HELD
- Method control: plant0 (unplanted rebuild) vs review build: 12 patterns SAME 12/12.
- (d) m6read_check_sab_anchors.py: rc 0, 1102 sabotages, all anchors resolve.
- (e) S1079 plant: SAME 16/16 bytes, plant compiler rc 0; run_finder DETECTED 3 fails vs control 0 (3 runs of run_finder
  total: plant w/o harness, control, plant with harness).
- rows_check section M: green on the committed map (162/0 on a section-C-cut copy; M itself untouched); red on live row
  declared dissolved, missing target, empty map (each one run).
- reach_equal --map on the committed map: mapped wfD/D-hors -> fd/D-hors BASE 1 HEAD 1, utf8 arm included, 8 patterns x 2
  arms: 0 differing keys; mis-target / missing-D-hors / dissolved-D-hors / D-one-mapped all RED (see CHECK-1).
- S1542 re-aimed plant: RED (one run_g2_win.sh --plant). 19/21 plant_specs resolve (CHECK-6).
- decider_census on the subject: 67/0; its own bypass plants fire (`.v <`: 1 stray hit; prototype plant fires).
  HITS 36 / MEMBER_COUNT 52 consistent with the member swaps in the census.tsv diff (fd_route -1, hors_facts +1,
  d_hors_holds -1, fd_renderer +1).
- finder_check FIND_ROWS includes D-hors (run_finder control 3163/0).
- Not exercised (budget/hold): reach_equal over the full corpus and the 4 arms; rows_check full (all 31 rows);
  `--analysis`/all-tie regimes; the make-side sabotage matrix.
- Pcrec compiles: about 395 (exploration 13, reach_equal drills ~101 incl. smoke, runset-based plants/drops 200,
  rows_check M drills 56, traced reach_equal on plants B/E 20, rows_check PAIR/D-hors on plants 16 less
  overlap); run_finder.sh 3 runs; run_g2_win.sh --plant 1 run. No `make`, no box lock.
