# CRITIC check — round r55 l1feat

## Findings

### CHECK-1 — CONFIRMED — S1927 (a design §14.4 L1 feature-commit anchor) no longer COMPILES at SUBJECT: undeclared compile failure = matrix ANOMALY (anomaly ceiling 0 -> mech run exits 1)
- Severity: maintenance (check lost: the E2 "consuming kind takes the zero unit" plant measures nothing). Effort: one-line re-anchor. Blast: S1927 only; the whole mech run goes red on the anomaly ceiling.
- Site: tests/mech/sabotages/S1927_consuming_kind_takes_zero_unit.sh SAB_AFTER `rb_zero_into(w, acc, a);` vs src/facts/req.c:1400 at SUBJECT `static void rb_zero_into(RbWalk *w, RbVal *acc, const Ast *a, RbVal *t)` (the feature 1e2a4f5db added the 4th arg; BASE req.c:1091 had 3). The row is NOT in the subject diff (git diff 07c840368 40e2e8626 -- tests/mech/sabotages lists S1925 + S3365-S3383 only), so "each re-checked for reach after the feature" (§14.4 L1) was not done for S1927's PLANT, only its probe.
- Repro: $R/plants/S1927/build.log: `src/facts/req.c:1427:22: error: too few arguments to function 'rb_zero_into'; expected 4, have 3` / `make: *** [Makefile:238: build/obj/facts/req.o] Error 1`. Row declares SAB_EXPECT=DETECTED (not COMPILE-CATCH) -> tests/mech/CLAUDE.md: "An undeclared compile failure stays ANOMALY, and run_sabotage_matrix.sh exits 1 when anomalies exceed ANOMALY_CEILING_PIN (pinned 0)". Its SAB_REACH still prints REACH-SG2-RUN-ABX on the subject (the probe runs on the CLEAN tree), and `m6read_check_sab_anchors.py` passes it (BEFORE text still present) — neither instrument sees an AFTER that no longer compiles.
- Note for anyone re-using the kit: $R/plants/S1927/tree/build/pcrec EXISTS but is the copied SUBJECT binary (mkplant copies build/ before make); any run "on plant S1927" measures the unplanted compiler.
- Fix: SAB_AFTER `case KTEXT_ANY:  rb_zero_into(w, acc, a, t); return;` (re-validate the row's detection on the harness).

### CHECK-2 — CONFIRMED — the feature makes S1915's anchor STALE; `m6read_check_sab_anchors.py` is red at SUBJECT, green at BASE
- Severity: maintenance (the R1 "variable repeat sets all" plant cannot apply -> APPLY-FAILED in the matrix; the static anchor check goes red). Effort: one-line re-anchor. Blast: S1915 + the anchor gate.
- Site: src/facts/req.c:1002-1004 at SUBJECT (`RbRuns o = rr_cat(w, p, gap), tl = rr_cat(w, gap, p); o.tail = tl.tail; o.rg = tl.rg;`) replaced BASE req.c:790 `o.tail = rr_cat(w, gap, p).tail;`, which is S1915's SAB_BEFORE. S1915 is not in the subject diff; src/facts/CLAUDE.md lists S1915-S1919 among the anchors to "keep reaching their site when editing".
- Repro: `( cd /home/pcrec/projects/pcrec/worktrees/crit-l1feat && python3 -I scripts/m6read_check_sab_anchors.py )` -> `sabotages checked: 1329 (1384 anchor sites)` / `STALE ANCHORS: 1` / `S1915_rep_split_sets_all.sh  src/facts/req.c  ANCHOR NOT FOUND`. BASE with its own script (`( cd $R/base && python3 -I scripts/m6read_check_sab_anchors.py )`) -> `sabotages checked: 1310 (1364 anchor sites)` / `all anchors resolve`. (Running the SUBJECT's script from inside $R/base reads the subject tree — it resolves paths from its own location — and prints the same stale line, so that comparison is not a base reading.) S1915's SAB_REACH still prints REACH-WR1-RUN on the subject.
- Fix: SAB_BEFORE `    o.tail = tl.tail;` SAB_AFTER `    o.tail = tl.tail; o.all = true;   /* SABOTAGE S1915 */` (same planted error), then re-validate on the harness.

### CHECK-3 — CONFIRMED — S3368 (W-L6, CAT-EDGE across a non-`all` neighbour) is an INERT plant: it moves no fact and no answer on its own witness, so its detector stays green (UNDETECTED in the matrix)
- Severity: maintenance (W-L6's planted error is unguarded: the row exists, reaches on the clean tree, and catches nothing). Effort: re-plant at the site the carried leftover actually takes (or re-derive the witness), then re-validate. Blast: S3368; W-L6's rows in tests/litscan/spanarms.rxt:988-1002 are guarded by no plant that goes red.
- Plant: $R/plants/S3368 (build OK, replace OK; src/facts/req.c:779 at the plant: `o.rg = r.all && rleft.n ? ... : rleft.n && r.maxw - r.head.n >= 0 && r.maxw - r.head.n < rleft.n ? rn_slice(&rleft, ...) : r.rg;`).
- Reach: SAB_REACH on the SUBJECT prints REACH-WL6 (req_set_maxoff 97:0,99:3) — but the PLANT prints the SAME value, so the probe proves the clean value only, not that the plant changes it.
- Detector: `PCREC=$R/plants/S3368/tree/build/pcrec CC=gcc PROCS=2 ... tests/harness/run.sh $R/plants/S3368/tree/tests/litscan/spanarms.rxt` -> `cases passed: 466 cases failed: 0` (subject control: 466/0) = SAME.
- Facts, subject vs plant (`--features all --emit-facts`, req_set_maxoff / req_whole_run / req_pieces): IDENTICAL on all 7 of `(?:(?=abc)a.?)[bc]c`, `(?=abc)a.?[bc]c`, `x(?=abcd)a.?[bc][cd]e`, `(?=abc)a[xy]?[bc]c`, `q(?=abcd)ab.?[cd]d`, `(?=abc)(?:a|ab)[bc]c`, `x(?=abc)(?:a.?)[bc]c`.
- Answers: `python3 -I $K/fuzz.py --tree plant:S3368 --alpha abcx --subjects 300 --maxlen 8` on 4 W-L6 variants -> OK 1489 / 1507 / 1459 / 1511 (every start offset of 300 subjects, length 0..8; the witness `abc`/`xabcc` is length 3-5, reached).
- So the plant does not implement §5.7 W-L6's error ("the leftover crosses a variable-width neighbour, shifted by its maximum width"): the guarded expression is not where the walk carries this witness's leftover (inference: the CAT-EDGE branch with `!r.all` is not taken for `a.?` at this spine shape, or the slice lands on positions no later meet reads). A plant that DOES move `[bc]` to `c` should delete `abc` (expected `m "abc" 0 3`).

### CHECK-4 — CONFIRMED — S3366 (W-L2) is DETECTED only through OTHER rows: its own witness `(?:(?=abcd)ab)cd` does not move on the plant, so SAB_DESC's claim ("claims `abcdcd`") is false and W-L2's spanarms rows guard nothing
- Severity: maintenance/doc (detection is borrowed from W-L5/W-S1/W-N1/W-RG/... rows; if those rows or their sites change, S3366 goes UNDETECTED with its named witness never having been the detector — learnings §3 "witnesses that stopped reaching their site"). Effort: pick a witness whose `rg` leftover is actually materialized past an `all` right factor and re-validate. Blast: S3366; tests/litscan/spanarms.rxt W-L2 rows.
- Repro: facts, subject vs plant: `build/pcrec --features all --emit-facts --pattern '(?:(?=abcd)ab)cd'` -> req_whole_run `61626364` / req_set_maxoff `97:0,98:1,99:2,100:3` on BOTH (the row's SAB_REACH therefore also prints REACH-WL2 on the PLANT: `check/reach.sh $R/plants/S3366/tree S3366` -> rc=0 missing=0).
- Detector: harness on $R/plants/S3366/tree spanarms.rxt -> 440 passed / 26 failed (LOUD on the detector), failing patterns: `a(?=b)[bc]`, `ab(?=c)cd`, `(?:abc(?=ab)){2}`, `ab[xy][xy](?=(?<=xx)y)[xy]`, `x(?=ab|ac)a.`, `x(?=qr)[pq]r`, `xy(?=ab)abzw`, `xy(?=bc)[bc]c` — NOT `(?:(?=abcd)ab)cd` (0 of its rows fail).
- (S3377 checked the same way: its own witness `x(?!ab)a[bc]` DOES fail, 2 rows, spanarms.rxt:1125/1132 — not this shape.)

### CHECK-5 — CONFIRMED (low) — S3382 (DEAD as one walk flag) catches W-D3/W-D4/W-D6 but NOT W-D7: its SAB_DESC and §5.7's W-D1..W-D7 row claim W-T1 is listed dead under this plant; it is not
- Severity: doc/maintenance (the W-D7 member of the [facts-look] dead cells has no plant that turns it red; the row overclaims). Effort: drop W-T1 from SAB_DESC and from span_arms §5.7 row W-D1..W-D7's "W-D7 under the flag sabotage" clause, or find a W-D7 shape whose correct walk contains an empty meet that is then dropped. Blast: S3382's text, §5.7 (design, ~line 914 at SUBJECT).
- Repro: my own full plant of BOTH S3382 edits (`check/plants/S3382full`, both BEFORE/AFTER pairs applied, build OK — note the kit's $R/plants/S3382 applied only the FIRST edit: mkplant.sh ignores SAB_FILE2/BEFORE2, so that kit plant is a no-op: identical facts on all four witnesses). `check/flook.sh check/plants/S3382full/tree` -> BAD on `x(?:foo(?=bar)baz)?y`, `(?:foo(?=bar)baz|q)`, `(?:foo(?=bar)baz){0}x` (why [dead], want []) — W-T1's cell stays green; directly: `--emit-facts --pattern '[ac]{17}[bc]{17}(?<=(?<=ca{16})b{17}).'` -> req_whole_run why `rate:builtin-prior` on both subject and full plant.
- Design text: span_arms §5.7 W-D1..W-D7 row: "W-D3, W-D4, W-D6, W-D7 under the flag sabotage: listed dead, the listing check is red". The correct walk of W-T1 has no empty meet, so a walk-level flag cannot fire there.
- The same kit limitation affects S1653 (two-file row): the kit plant has only its req.c half (startset.c half missing), so no S1653 verdict below uses the kit plant as the full row.

### CHECK-6 — CONFIRMED — the W-T1 rows were HAND-APPENDED to a GENERATED file: tests/litscan/presence_deny.rxt is written whole by tests/litscan/gen_presence_deny.py (header: "Written by gen_presence_deny.py"; the generator `open(...presence_deny.rxt, "w")`s the full text), which the subject did not change — the next regeneration silently deletes W-T1's answer check
- Severity: maintenance (a check that vanishes on the file's own documented refresh path; the design names this row as W-T1's answer check under `--memfn=no-fd-pres-pick`, span_arms §5.7 W-T1 / §14.4 L1 [r3 READY-1/8]). Effort: add W-T1 to the generator's CASES (precedent: 27928b1b2 changed gen_presence_deny.py and presence_deny.rxt together) or move the rows to a hand-written file (spanarms.rxt already carries W-T1 at default flags). Blast: the two W-T1 blocks at presence_deny.rxt:721-735 (subject).
- Evidence: `git diff --stat 07c840368 40e2e8626 -- tests/litscan/gen_presence_deny.py` -> empty; `grep -n 'ac]{17}\|W-T1' tests/litscan/gen_presence_deny.py` -> no hit. The appended rows also use a different cell form (`m "..." 0 35` from start 0 only) from the generator's per-start-position `ms P` / `ns P` cells.
- The rows themselves WORK: harness on presence_deny.rxt — subject 655/0 at default and under RXTFLAGS=--memfn=no-fd-pres-pick; plant S3378 653/2 (default) and 651/4 (deny flag), all failures on W-T1's pattern. So today the check is live; the defect is its home.

## PROBED-AND-HELD


Method. Build = `$R/plants/<ROW>/build.log`. Reach = the row's SAB_REACH run as run_sabotage_matrix.sh runs it (cwd = REACH_TMP, TREE/PCREC/REACH_TMP/CC exported, timeout 120, every SAB_REACH_EXPECT line must appear), on the SUBJECT (`check/reach.sh`); "plant-probe" = the same probe on the row's PLANT (MISSING means the plant moves the witness's value). Harness = one-`.rxt` run on the plant's own tree, PROCS=2. Subject controls: spanarms.rxt 466/0, startpos.rxt 41/0, handoff.rxt 4908/0, presence_deny.rxt 655/0 (default and --memfn=no-fd-pres-pick). own = failing harness cells on the row's OWN witness pattern. facts = the [facts-look] block lifted verbatim from tests/codegen/run_facts_checks.sh (`check/flook.sh`, 20 cells; subject OK, BASE red as it should be). codegen = tests/codegen/reqcube_check.py run alone (subject 105 passed / 0 failed). Witnesses: every S3365-S3383 witness is the one span_arms §5.7 names (checked for W-L2, W-L5, W-L6, W-L7, W-L8, W-S4, W-L4); the lane wrote the plants. Witness lengths reached: the harness cells are the rows' own (3-37 bytes); fuzz on S3368 reached length 8 (witness 3-5).

| row | build | reach (subject) | plant-probe | detector on the plant | class |
|---|---|---|---|---|---|
| S3365 W-L5 | OK | OK | moved | harness 430/36, own 4; facts red too | LOUD |
| S3366 W-L2 | OK | OK | NOT moved | harness 440/26, own 0 (CHECK-4) | LOUD (borrowed) |
| S3367 W-L7 | OK | OK | moved | harness 442/24, own 2 | LOUD |
| S3368 W-L6 | OK | OK | NOT moved | harness 466/0; facts identical on 7 shapes; fuzz 4 pats x 300 subj OK (CHECK-3) | SAME |
| S3369 W-L8 | OK | OK | moved | harness 463/3, own 3 | LOUD |
| S3370 W-A1 | OK | OK | moved | harness 464/2, own 2 | LOUD |
| S3371 W-S1 | OK | OK | moved | harness 460/6, own 6 | LOUD |
| S3372 W-N1 | OK | OK | moved | harness 462/4, own 4 | LOUD |
| S3373 W-N2 | OK | OK | moved | harness 464/2, own 2 | LOUD |
| S3374 W-F4 | OK | OK | moved | harness 464/2, own 2 | LOUD |
| S3375 W-RG | OK | OK | moved | harness 464/2, own 2 | LOUD |
| S3376 W-C1 | OK | OK | moved | harness 464/2, own 2; facts -fno-ctx-node cell red | LOUD |
| S3377 W-E1 | OK | OK | moved | harness 464/2, own 2 | LOUD |
| S3378 W-T1 | OK | OK | moved | harness 464/2, own 2; facts W-T1 cell red; presence_deny 653/2 default, 651/4 deny flag | LOUD |
| S3379 W-S4 | OK | OK | moved | reqcube 104/1: `'x(?=qr)[pq]r': RX_REQ_BYTE 113 is not a member of req_set [114, 120]` | LOUD |
| S3380 W-D1 | OK | OK | moved | facts red: `foo(?=bar)baz` why [rate:builtin-prior] want [dead] | LOUD |
| S3381 W-D2 | OK | OK | moved | facts red: `(?<=ab)(?<=cb)c` why [] want [dead] | LOUD |
| S3382 W-D3/4/6/7 | OK (kit plant = 1st edit only, a no-op) | OK | kit: not moved; own full plant: moved | own full plant: facts red on W-D3, W-D4, W-D6; W-T1 (W-D7) green (CHECK-5) | LOUD (3 of 4) |
| S3383 W-L4 | OK | OK | moved | facts red: `bar(?=baz)` value [62617262617a] want [626172] | LOUD |
| S1925 S-L (re-aimed) | OK | OK | moved | harness 403/63, own 6 | LOUD |
| S1926 W-E3 | OK | OK | moved | harness 450/16, own 4 | LOUD |
| S1927 S-g | FAILS (`too few arguments to rb_zero_into`), undeclared (CHECK-1) | OK | n/a (kit binary = subject's, cmp identical) | not runnable | LOUD-build -> matrix ANOMALY |
| S1653 | OK (kit plant = req.c half only; startset.c half missing) | OK | probe not moved (it checks only that the callout call is emitted) | facts move: req_set_maxoff 98:unbounded -> 98:2 on `xa(?C"two,consume")bc`; callouts suite not run (not allowed) | SILENT-MOVE at facts (detector unrun) |
| S1928 zero arm | OK | OK | moved (restore=zero no longer restores) | facts section not lifted; probe is that section's cell shape | moved |
| S1929 empty arm | OK | OK | moved | as S1928 | moved |
| S1887 | OK | OK (`run=none`) | moved | startpos.rxt 30/11 (subject 41/0), own 2 | LOUD |
| S1907 all arms | OK | OK | moved | facts red on every `restore=look` cell | LOUD |
| S465 | OK | OK | moved | handoff.rxt 4858/50 (subject 4908/0), own 10; prechecks not run | LOUD |
| S474 | OK | OK | moved (78797a77 absent) | prechecks not run (run_prechecks.sh:1845 holds the same cell) | moved |
| S1930 tie arm | OK | OK (probe writes `-o /dev/stdout`; prints `/dev/stdout.h.pcrec-tmp.*: Permission denied` — noise, the grep still reads stdout) | moved | facts section not lifted | moved |
| S1915 (not asked) | — | OK | — | anchor STALE at SUBJECT (CHECK-2) | APPLY-FAILED |

Own plants (6): (1) S3382full — both S3382 edits (results above). (2) `lookarm`: drop `PCREC_WALK_ARM(LOOK)` from the E-5i row (req.c:1310) -> [facts-look] red on 4 `restore=look` cells: the look arm has no sabotage row of its own (zero/empty/tie have S1928/S1929/S1930) but S1907 and [facts-look] cover it — held. (3) DELETED [facts-look] cell `foo(?=bar)baz ... dead`, run on plant S3380 -> `19 cells ... OK`: silent (no cell-count floor; the backstop is S3380 going UNDETECTED in the matrix) — held, as designed. (4) INVENTED cell `qux(?=quux) req_whole_run 717578 dead` on the subject -> red (`why [rate:builtin-prior], want [dead]`). (5) DELETED WIT `ws4` from a copy of reqcube_check.py, run on plant S3379 -> the ws4 FAIL disappears (silent; backstop S3379 in the matrix) — held. (Its only other FAIL, the corpus floor `0 masked rows over 0 corpus patterns`, is an artifact of running the copy outside the tree: ROOT is resolved from `__file__`.) (6) INVENTED WIT `("inv", "x(?=qr)[pq]r(?<=zz)", ())` on the subject -> no new FAIL: WIT entries carry no expectation, so an invented entry cannot go red unless its stamps break check 4 — held. walk_arms.def DELETED LOOK row: not planted; req.c:1310 names `PCREC_WALK_ARM(LOOK)`, so the build fails (LOUD); run_axes.sh derives its arms from the .def, so an INVENTED row is swept with nothing to check (its comment already says this).

Anchor check: `( cd <review tree> && python3 -I scripts/m6read_check_sab_anchors.py )` -> 1329 rows, 1 STALE (S1915); BASE's own copy in BASE -> 1310 rows, all resolve. The subject's script run from inside BASE reads the SUBJECT tree (paths come from `__file__`), so it is not a BASE reading. The anchor check does not see S1927 (its BEFORE text is still present; only its AFTER no longer compiles).

Oracle spot-checks (libpcre2-8, $K/oracle.sh) of 8 spanarms/W-T1 cells: all as the .rxt holds (e.g. `(?:(?=abc)a.?)[bc]c` on `abc` M 0 3, `abbc` N; W-T1 M 0 35).
Budget: 22 harness runs, ~400 compiles (reach 60, facts-look 31 x ~24, fuzz 4 patterns, probes), 2 compiler plants of my own.

CRITIC COMPLETE
