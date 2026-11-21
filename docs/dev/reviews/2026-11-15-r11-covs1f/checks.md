# checks findings

## Findings

### CHECKS-1 (CONFIRMED, doc, effort trivial, blast radius: one row's DOC_FIGURE) — S3226's "3 FAILs" is 2 failing checks
tests/mech/sabotages/S3226_cover_set_compare_low_half.sh SAB_DOC_FIGURE: "measured locally ... on the review plant V16 (3 FAILs)".
Repro: `PCREC=plants/P1_s3226/build/pcrec PCREC_HARNESS=plants/P1_s3226/build/pcrec-harness bash tests/kitproof/run_cover.sh $SUBJECT`
-> rc 1, `checks failed: 2` (verdict u aé|bè, facts u aé|bè); `grep -c FAIL` on that log is 3 because the trailer
`test-kitproof: FAIL` also matches. The figure is a FAIL-line grep count, not the check count (learnings §3: the
verdict is the trailer). P1 is S3226's plant modulo the trailing comment text (`/* PLANT P1 */` vs `/* SABOTAGE S3226 */`;
python replace of SAB_BEFORE->SAB_AFTER on SUBJECT known.c differs from P1 only in that comment).
Fix: "2 checks failed" (or cite the trailer).

### CHECKS-2 (CONFIRMED, maintenance, effort small: 2 lines, blast radius: the TRADES-1 WEIGHTS arm) — the WEIGHTS arm's population is uncounted: an empty or missing measured file makes it vacuous and green
tests/ci/cloud_mech_check.sh:28-31. The arm builds its set `m` from tests/ci/measured_mech.tsv rows with `$6 == "measured"`
and never counts it. Plants (copies of tests/ci under checks/ciroot, tests/mech symlinked to SUBJECT):
- one row unweighted (S1131 weight_source -> ESTIMATE): `UNWEIGHTED ... S1131`, rc 1 — LOUD, held.
- measured_mech.tsv with every row's col 6 = `apportioned` (the file's own other basis word) + the ALL-ESTIMATE table: `PASS: 90 shards ...`, rc 0 — SAME (green).
- measured_mech.tsv with its rows removed (header only) + the ALL-ESTIMATE table: PASS, rc 0.
- measured_mech.tsv MISSING: `awk: cannot open ...` on stderr, then `PASS`, rc 0 (the awk error lands in $T/d? no: stderr, and $T/d is empty).
The arm's own `--selftest` plant DOES go red in the vacuous case (`FAIL: selftest: a table without its measured weights not seen`,
rc 1), but nothing runs `--selftest`: the gate is cloud_kinds.tsv's population column (`bash tests/ci/cloud_mech_check.sh {selector}`,
no --selftest) via cloud_check.sh; grep finds no other caller. Same shape as learnings §3 K35 (a population nobody counts).
Fix: `END { if (!length(m)) print "  NO MEASURED ROWS in measured_mech.tsv (a weights check over nothing)" }` plus a `[ -r ]` test
(or a floor on the measured count), and run `--selftest` from the population column or cloud_check.sh.
Note (not a finding): the arm checks the SOURCE word only, not the number: S1131 weight 3 -> 9999 with source kept is green (a stale
re-weigh is out of its stated claim).

### CHECKS-3 (CONFIRMED, design of the job's verdict; effort small; blast radius: covs1-sweep's green is the stage's "moves only what it declares" evidence) — sweep_verdict.py passes failed floors, a traceback and a failed fixture
docs/dev/lanes/covs1_evidence/sweep_verdict.py; job_sweep's own CONTRACT header says "every tag floor held ... (a failed floor; no
DONE line) is red here". The verdict ignores SWEEP_RC (prints it only) and recognises emit_sweep's failures only by the
lines it greps; emit_sweep's other failure prints (scripts/emit_sweep.py report_tally 2236-2246, report_stream 2199-2201,
main 3893-3926, completion_trailer 4073) never appear among them. Constructed reports built from those print shapes
(11 streams, SELF-CHECK PASSED, REAL RUN, DELIVER OK, valid movers file; checks/sv/*.txt), sweep_verdict rc:
| plant | emit_sweep prints | verdict |
|---|---|---|
| clean, movers in c-default+facts | - | rc 0 (right) |
| no DONE | - | RED (right) |
| mover in c-vm | movers=1 | RED (right, twice: stream + movers file) |
| asymmetric c-default | asymmetric=1 | RED (right) |
| stream missing (10) | - | RED (right) |
| TAG FLOOR failed (stderr tally) | `  TAG FLOOR side a: yes 5 < 9`, and NO `tag floors:` line (report_tally prints "all held" only when ok) | rc 0 — SAME |
| reach floor failed (c-default) | `  REACH FLOOR VIOLATION: 5 < floor 90` | rc 0 — SAME |
| uncaught exception after the streams | `emit_sweep: DONE rc=1 (uncaught exception, traceback follows)` + traceback | rc 0 — SAME ("emit_sweep: DONE" is printed on EVERY ending by design, so it is not a completion witness) |
| named fixture did not produce, DELIVER shape hit | `DELIVER WITNESS FAILURE: fixture(s) ...` AND `DELIVER witness: OK` (main prints both) | rc 0 — SAME |
| ARGV POPULATION / COMPOSITION PRODUCING FLOOR VIOLATION | those lines | rc 0 — SAME |
So "a failed floor is red here" is false for every floor kind: the only floor line read is `tag floors:`, which a failing
tally never prints. Fix: red on any line matching emit_sweep's failure vocabulary (`VIOLATION`, `FAILURE`, `TAG FLOOR side`,
`MANIFEST side`, `NO TAG FLOORS PINNED`, `CENSUS OFF-DIAGONAL`, `INVALID`, `uncaught exception`), require `emit_sweep: DONE rc=0`
or `rc=1` WITHOUT `(uncaught`, and require one `tag floors: ... all held` per tally stream (5) rather than "none failing";
keep these constructed reports as its selftest. Held: the 11-stream count is right (4 argv + 4 emit-ir-auto arms + stderr +
composition + dumps under STREAMS_ALL); the movers-file columns (#stream, class, key) match emit_sweep 3873-3879;
`| tee` + `${PIPESTATUS[0]}` hands emit_sweep's rc (bash test: rc 1 seen through tee).

### CHECKS-4 (CONFIRMED, maintenance, effort trivial, blast radius none today) — predict.py ROUTE_ROWS carries a conjunct name, not a row
docs/dev/lanes/covs1_evidence/predict.py ROUTE_ROWS: 14 of 15 names are listing row names (all seen as f[1] of
`build/pcrec --features all --emit-facts=byte,utf8` over abc, a+b, (a)\1, foo$, x[0-9]+Qz, \bcat\b); `finisher-dfa` is
cover_conj C1's / lmwalk's conjunct name (src/gen/known.c:449, lmwalk.c:277), never a row: a dead allowlist entry
(harmless direction: it admits nothing that exists). Drop it or name the row meant.

### CHECKS-5 (CONFIRMED, doc, effort trivial) — job_z2's --dry-run expect reason still says "exec'd last"
docs/dev/lanes/covs1_evidence/job_z2: `boxqueue: expect none reason=the stated check's rc is the job's rc (exec'd last)`;
the stated check is now `| tee` + PIPESTATUS + `exit "$rc"` (rc still the stated check's, so only the parenthesis is stale).
Also: the DELIVERABLE line says "X0 population = stated rows sampled 1-in-MOD" but prints only the SAMPLE's checked=;
the population (`%d distinct statements` on z2.py's `## stated sets` line) is not repeated in it.

## PROBED-AND-HELD

One row per check. Class: SAME (plant green), SILENT-MOVE, LOUD (red / rc != 0).

| # | check | plant | class | observed |
|---|---|---|---|---|
| 1 | run_cover.sh, new rows + floors | P1 (S3226 plant) as PCREC/PCREC_HARNESS | LOUD | rc 1, 2 checks red: verdict u aé|bè, facts u aé|bè (175 -> 173 passed) |
| 1 | same | P2 (stop swap reverted) | LOUD | rc 1, 1 red: facts - a$\n (`fixed-width|-|2|97,10` vs `|2|2|`) |
| 1 | same | clean SUBJECT | - | rc 0, 175 passed |
| 1 | floors 48/19/105 | count of cases.tsv rows by kind | held | 48 verdict, 19 facts, 105 answer rows = the floors exactly (the run prints `48 verdicts, 19 facts, 105 answers`) |
| 1 | utf8 key path | run_cover.sh COPY with the loader's `enc` forced to byte (checks/rcroot) | LOUD | 2 red: BOTH u facts rows (aé|bè and é{16}) read "" (-e utf8 lists only a utf8 row). So the utf8 key is NOT é{16}'s alone; what only é{16} pins is a utf8 STATED record (why cover, k/exact_len 32 counted in BYTES, continuation byte 169): e.g. a plant that counts a utf8 stretch per character (k 16) or drops a stated utf8 cover record would move only it (reasoned, no compiler plant built). The byte C15 boundary at 32 is already pinned by the 32/33-letter verdict rows. |
| 2 | S3226 SAB_BEFORE | count in SUBJECT src/gen/known.c | held | exactly 1 (line 215) |
| 2 | S3226 plant vs P1 | SAB_BEFORE->SAB_AFTER on SUBJECT known.c vs P1's known.c | held | identical except the trailing comment (`/* SABOTAGE S3226 */` vs `/* PLANT P1 */`); code byte-identical |
| 2 | S3226 reach | SAB_REACH on clean SUBJECT, matrix matcher | held | prints `REACH-DECLINE`, `REACH-WHY=[exact/machine-inexact]` = its 2 expect lines, 0 missing |
| 2 | anchors tripwire | `python3 -I scripts/m6read_check_sab_anchors.py` (SUBJECT tree, root from its own path) | held | `sabotages checked: 1305 (1359 anchor sites)`, `all anchors resolve` (S3225's respelled anchor included) |
| 3 | 10 REACH probes (S1131 S1136 S1139 S3220-S3226) | clean SUBJECT, matrix semantics (grep -qF per line, TREE/PCREC/REACH_TMP as the matrix sets them) | held | 10/10 reach:ok(2/2); whys: S1131/S3221/S3226 [exact/machine-inexact], S1136/S1139/S3225 [no-eol-view], S3220/S3223 [statement-fits], S3222/S3224 [cover] |
| 3 | same | P1 / P2 / P3 as TREE | LOUD for P1 only | P1: S3226 MISSING 2/2 (REACH-COVER, [cover]); P2, P3: all 10 ok -- neither plant moves any witness's why (P2 moves only a$\n's k; P3 only the width-bounded rule) |
| 3 | why pin | reach.sh COPY, every why remapped to ANOTHER conjunct | LOUD | 10/10 rows MISSING 1/2, the first-line verdict still found: the pin alone turns them UNREACHED |
| 3 | bracket exactness | reach.sh COPY printing `[exact]` for exact/machine-inexact | LOUD | S1131/S3221/S3226 MISSING 1/2 (`[exact/machine-inexact]` not a substring of `[exact]`) |
| 3 | brackets needed | reach.sh COPY dropping the brackets | LOUD | MISSING 1/2 (pins carry the brackets) |
| 3 | note | facts rows (S1131 S3220 S3221 S3222 S3224) | - | the why pin is redundant there with REACH-FACTS-EQUAL (the facts VALUE's first column IS the why); it still binds the row file to cases.tsv's why, so harmless |
| 4 | cloud_mech_check.sh | real table + `--selftest` | held | `PASS: 90 shards ... 1305 sabotage ids`; selftest 5/5 PASS, rc 0 |
| 4 | WEIGHTS | ONE row (S1131) -> ESTIMATE | LOUD | `UNWEIGHTED ... S1131`, rc 1 |
| 4 | WEIGHTS | measured_mech.tsv col 6 not "measured" / empty / missing | SAME | see CHECKS-2 |
| 4 | regeneration | `cloud_units_plan.py mech --measured tests/ci/measured_mech.tsv --slots 30 --waves 3` to checks/regen_mech.tsv | held | byte-identical to the committed table |
| 4 | trade audit | old (65ad7d226) vs new header + plan runs | - | old: 20 shards, 1304 rows at the 45 s default, max 2970 s, floor 115 s (meaningless). New: 90 shards (30 slots x 3 waves), total work 124,756 s unchanged, slowest shard 2551 s = S221 ALONE (42.5 min; the next 89 are 1366-1377 s, ~23 min), wall 2621 s = the indivisible floor. Measured alternatives: 20 shards -> wall 6313 s, 30 -> 4376 s. Given up: 4.5x the shard jobs and 90 x 70 s setup (~1.75 runner-h) vs 20 x 70 s; 67 rows still ESTIMATE (mean 95.6 s). Wall is bound by S221; splitting it is the only further gain |
| 5 | DOOR_SB_FLOOR 61 | header rule "~10% below" the measure 68 | held | 68 x 0.9 = 61.2 -> 61 |
| 5 | comparison | COPY of rank_check.py, doors() on constructed stderr (FINDDOOR\tstart_bytes\tok x k), FLOORS compare `got >= floor` | LOUD at 60 | 60 RED, 61 GREEN, 68 GREEN; the tag matches emit_dfa.c:7099's print |
| 6 | emit_sweep.py.test new block | run against COPIES of scripts/emit_sweep.py (checks/es_*) | LOUD x6 | clean rc 0; declared-gone branch off: red (line 17 `== ([], 2)`); its "still in NEW" problem off: red (18); declared-new branch off: red (17); "already in REF" off: red (20); "absent from NEW" off: red (19); facts_declarations ignoring the selfcheck label: red (26) |
| 7 | sweep_verdict.py | constructed reports | mixed | see CHECKS-3 (defects: floors/traceback/fixture green); held: no DONE, c-vm mover, asymmetric, missing stream, no movers file all RED; "11 streams" right; movers-file columns right; PIPESTATUS right |
| 8 | predict.py row names | main's build/pcrec (pre-covs1 stand-in: main lacks 65ad7d226) vs SUBJECT on `[a-c]*\ba` | held | f[0] = encoding, f[1] = row name in facts/decisions; moved: RX_DFA_PREFILTER/SCAN/START, RX_REQ_WHY, end_window (route), span_facts, cover (declared), both encs -> wrong = [] |
| 8 | UNEXPLAINED-ROWS | the judge's code text exec'd on constructed listings: a non-route facts row (`kinds`) changed | LOUD | `row outside the declared route rows moved: byte kinds` |
| 8 | no encoding gains | same listings, res rows with no rw!=cover->nw==cover | LOUD | `mover but no encoding gains a cover` (+ route rows in the non-cover enc flagged) |
| 8 | route row in a non-cover enc | byte gains, utf8 stays fixed-width | LOUD | 5 `route row ... moved in utf8 where the candidate is not a cover` |
| 9 | job_z2 DELIVERABLE | the greps on z2.py `stated`'s print shape (z2.py:385) | held | `checked=97 timed-out-items=2` from a constructed log; `unchecked-parts=` does not match `checked=`; Z2_STATED_ITEM_SECS exported (default 90) so set -u holds; rc via PIPESTATUS |
