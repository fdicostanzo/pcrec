# s3012tri report: why G2 presence plant S3012 is NOT DETECTED (TRIAGE, no fix)

Lane s3012tri (opus), 2026-11-24. Branch lane/s3012tri, cut from lane/memfn-plantcheck @ 6399dfd86.
D203 triage: I edited no code. The evidence scripts are under `docs/dev/lanes/s3012tri_evidence/`.
Scratch outputs are under `/var/tmp/pcrec-claude/scratch/s3012tri/` and are not committed.

## Summary

- **Cause.** The plant's witness stopped reaching its site. The cause is not the target, the
  applier or the detector. Kit commit **d5f9da41b** (lane partd, 2026-11-13, "kit D1/D2 core ...
  direct translation"; it landed on main as 9cecc3caa, [RUN-POS-SET] S2, 2026-11-14) made the
  derived run part a direct translation of the reply (part_d.md §2.1). Since then the presence
  family's sites never walk window.c's Table A, so `a_mass_choose` (the function the plant edits)
  is called **0 times** in the presence generator's passes. With and without the plant, the
  rendered text is byte-identical on every target and both lever states.
- **The twin was re-aimed but the runner was not.** On 2026-11-14, lane mechund (812637dd5)
  re-aimed the mech twin `tests/mech/sabotages/S3012_in_run_stop_filter_deleted.sh` to g2win and
  recorded "g2pres no longer reaches the filter ... Former detector (g2pres) retired". The same
  plant in `memfn/tests/run_g2_pres.sh` kept detector `mf_define`. `run_g2_win.sh` never got an
  S3012 row.
- **Not x86-specific.** The pres runner's S3012 reads GREEN on every host. The dev box is just
  the first place the full `--plants` list ran after 11-13.
- **Not plantfix/plantfix2.** The old heredoc applier and `tests/lib/plants.py` produce identical
  planted trees.
- **Real defect, but EQUIVALENT for this family.** The filter is live kit code. On the window
  family's in-run sites the plant moves the stop: 43 filter-decisive sites, and 157 of 200 agree
  with the reference instead of 200 of 200. So the plant is a real defect that some check must
  catch. For the presence family's population it is EQUIVALENT by construction, because the
  planted function is never called there.
- **Class.** A runner-embedded plant whose witness stopped reaching after a later kit change.
  Nothing re-runs runner plants for DETECTION (the [SABANCHOR] plant pass checks only that they
  APPLY), and the plant-twin check compares edit TEXT, not DETECTOR. R-2: GF-1 missed it
  through a hole in the check. `read_row()` never reads SAB_SUITES, and
  `PLANT_TWINS="$PLANTS"` declares every pres plant a twin.
- **Siblings.**
  - Twin-detector divergence: **1 of 41** twins across the 4 runners (S3012 itself).
  - Generator-unreached pres plants: **0 besides S3012** (33 of 35 reach their site; S3127 is
    census-only by design).
- **Fix shape.**
  1. Move S3012's runner row from run_g2_pres.sh to run_g2_win.sh. Its detector there is the
     DECIDE check plus the in-run agreement count.
  2. Make the twin check compare the detector arm. A twin's runner must be among its mech row's
     SAB_SUITES.
  3. Give each runner plant a reach measure on its own site, or schedule the `--plants` modes.

## Reproduction

All on the Mac with gcc-16. The plant was applied by `tests/lib/plants.py apply pres` (script
`$S/apply.sh`). The kit objects and `g2_pres_gen` were built exactly as the runner's `kit_objs`
and `build_gen` do. Seed 20261110, 400 sites + 300 wide.

1. PREMISE: `memfn/tests/run_g2_pres.sh --plant-check` prints `plant-check: 35 plants, 41 edits,
   0 bad`. S3012 applies: 1/1 edits, file window.c. The resulting diff removes exactly the two
   lines `if (r && p->stretch && o >= r->start && o < r->start + r->len && o != rs) continue;`
   and puts `(void)o; (void)rs;` in their place.
2. Which pass and which target it was meant to fire on:
   - The spec and the expected-reason pattern `mf_define` mean the LEVER pass (`run-tie-left`,
     lever 1). There, the window's stop and the run decision would disagree, and `mf_define`
     refuses the layout ("its run part is not the WINDOW its presence link verifies"; this is
     the mech row's Former-detector text).
   - The plant is **target-independent**. At the commit that added it (ff8db295a), it red on
     both x86-64.1 and generic.1, with 286 `mf_define` failures each, and changed no lever-0
     text.
3. Today (6399dfd86), clean vs planted generator:

   | pass (target.lever) | clean FAIL / mf_define | planted FAIL / mf_define | g2p_sites.c |
   |---|---|---|---|
   | x86-64-v3.0 / .1 | 0/0, 0/0 | 0/0, 0/0 | identical, identical |
   | x86-64.0 / .1 | 0/0, 0/0 | 0/0, 0/0 | identical, identical |
   | generic.0 / .1 | 0/0, 0/0 | 0/0, 0/0 | identical, identical |

   The generator logs are byte-identical too. Every check in the family consumes either the
   text or the generator log: the driver, the oracle, the cells, the floors, the hashes and the
   lever's moved-witness count. So no check of this runner can red. That matches the dev box's
   `PLANT S3012 GREEN (NOT DETECTED; oracle green, rows=84780 violations=0)`.
4. Instrumented kit (scratch copy only): I added an `fprintf` at the end of `a_mass_choose` that
   counts filter hits and whether the stop moves. Over x86-64 and generic × lever 0/1 it printed
   **zero** lines, so the function is never called by the presence family's sites.

## Cause

Bisected by `$S/hist.sh` (scratch). For each commit it runs `git archive` of `memfn/`, builds the
clean and planted kit + generator, and runs lever passes, with the generator's arguments adapted
to each commit's usage line:

| commit | what | planted lever pass | text clean vs plant |
|---|---|---|---|
| ff8db295a (k382afix, plant added) | K38-2a form | **286 mf_define** on x86-64.1 and generic.1 | lever 1 differs, lever 0 same |
| d5f9da41b^ (partd's parent) | K38-2 seam form | **289 mf_define** (292 failures) on both | lever 1 differs, lever 0 same |
| d5f9da41b (partd kit D1/D2) | direct translation | **0** | identical on all four passes |
| 6399dfd86 (today) | | **0** | identical on all six passes |

So the witness's reach died at **d5f9da41b**. Since Part D, the derived run part is a direct
translation of the reply (`run_part_terms`, part_d.md §2.1), not a layout of the window decision.
The presence sites therefore no longer go through `decide()`'s Table A walk
(`memfn/src/window.c:1300`). The in-run filter at `memfn/src/window.c:736` is still live for
WINDOW sites (`run_g2_win.sh`'s in-run stream).

- **The detector did not change.** The expected reason `mf_define` and the generator's refusal
  path are as before. The plant simply produces no difference for them to see.
- **The filter is not redundant.** On the window family's generator (`g2_win_gen.c` +
  `g2_win_ref.c`, seed 20261022, built against my scratch clean and planted kits), the clean kit
  reads `in-run rendered 200, filter-decisive 43, stop agreeing with the reference 200`. The
  planted kit reads `... 200, 43, 157`. These are the same numbers lane fixposts2b recorded on
  2026-11-15. The defect is real and visible to the window family.
- **Not plantfix/plantfix2 (question 3).** `run_g2_pres.sh` from 9d086e8e6^ (before plantfix) has
  the same S3012 spec text. I applied it with that version's heredoc applier (`$S/apply_old.sh`,
  the `un()` decoder copied verbatim) and with today's `plants.py apply pres`. `diff -r` of the
  two planted trees is empty.
- **Why nobody saw it for 11 days.**
  - The mech row was re-aimed on 2026-11-14 (812637dd5, lane mechund). Its header now says
    "since [RUN-POS-SET] stage 3 ... g2pres no longer reaches the filter; the detector is G2's
    WINDOW family". But the runner's own copy is the same plant in run_g2_pres.sh's `plant_spec`,
    and it kept `plant_expect S3012 = mf_define`.
  - The partd/partd2/partdfix lanes ran `--plant ID` only for the plants they added (S3113,
    S3125-S3127; partd2_report.md, partdfix_report.md). Nothing ran `--plants`.
    `scripts/m6read_check_sab_anchors.py:157` says so outright: the runners' plant modes are
    ones "which nothing runs automatically".
  - The runner's own `--reach` token for S3012 ("C (and S3012's in-run stop):
    REACH-G2P-LEVER-PASS rendered>=300", `memfn/tests/run_g2_pres.sh:624`) counts rendered lever
    sites. That count is not the filter's site, so it stayed green the whole time.
  - plantfix2's `PLANT_TWINS="$PLANTS"` (`memfn/tests/run_g2_pres.sh` near the C0 lines)
    declared S3012 a twin of the mech row. The twin check holds the edit TEXT equal, and the text
    is still equal. It never asks whether the twin's DETECTOR is the runner.

## Class and siblings

**CLASS: a runner-embedded plant whose witness stopped reaching its site after a later kit
change, kept alive by checks that confirm the plant APPLIES and its twin's TEXT matches, but
never that the runner still DETECTS it** ([MECH-REACH]'s population, learnings.md §3: "witnesses
that stopped reaching their site"). Rule broken: a plant row's detector must be re-confirmed when
the mechanism under it changes. In the mech half this is enforced by SAB_REACH probes and the
matrix. In the runner half, nothing re-runs `--plants`, and the twin's re-aim (a detector change)
was not propagated. That is FUW-12's class (plantri) at the DETECTOR level rather than the ANCHOR
level.

**R-2: why GF-1 (plantfix2's twin check) did not catch S3012.** The cause is **a hole in the
check**. It is not a different mech id, a missing mech file or an exemption.

- **Same id, file present.** `tests/mech/sabotages/S3012_in_run_stop_filter_deleted.sh` exists,
  and it is the only row with that id.
- **Declared, not exempt.** run_g2_pres.sh declares `PLANT_TWINS="$PLANTS"` (line 413), so all
  35 of its plants are declared twins by construction. S3012 is one of the 39 compared twins:
  pres 35 + proof 4. That matches `runner plant twins checked: 39` in the plant pass I re-ran on
  this tree (`scripts/m6read_check_sab_anchors.py`, rc 0, "every shared id is an equal declared
  twin").
- **The hole.** `twin_check()` (scripts/m6read_check_sab_anchors.py:298) compares only each
  edit's FILE, FROM and TO. `read_row()` sources the row for exactly SAB_ID, SAB_FILE,
  SAB_BEFORE, SAB_AFTER, SAB_COUNT and their site-2 fields, and never reads **SAB_SUITES**. The
  runner's plant text and the mech row's BEFORE/AFTER are still equal (mechund re-aimed the
  DETECTOR, not the text), so GF-1 is green by construction. "Same plant" was defined as "same
  edit". A twin is the same plant with the same detector, and the detector half of that identity
  is unchecked.
- **A second weakness.** `PLANT_TWINS="$PLANTS"` makes the DECLARATION itself unfalsifiable for
  the pres runner. Every new pres plant is a declared twin automatically, so the
  collision/declaration half of GF-1 can never red there.

Fix shape for the hole:
- GF-1 reads SAB_SUITES too, and holds the runner among the arms that run it: an arm→runner map
  read from `run_sabotage_matrix.sh`'s arm table, not hand-copied. The map needs g2pres and
  g2pres-asan → run_g2_pres.sh, g2win → run_g2_win.sh, and memfnfinder → run_proof.sh via
  run_finder.sh.
- A twin whose row's suites do not name its runner reds as `TWIN DETECTOR MOVED`.
- Replace `PLANT_TWINS="$PLANTS"` with an explicit id list.

Drills:
- (a) The live instance: on today's tree the fixed check must red S3012 and nothing else. The
  census above shows 1 of 41.
- (b) A `--selftest` mutant in a tree copy: set S3044's SAB_SUITES from g2pres to g2win. Today's
  check stays green on that mutant, as it does on S3012; the fixed check reds it, naming S3044.
- (c) The control: S3100's `g2pres-asan` stays green, as the same runner.

**Sibling count 1: twin-detector divergence** (`s3012tri_evidence/twin_detector_census.py`, all 4
runners). For each runner plant id with a `tests/mech/sabotages` row, the census checks whether
the row's SAB_SUITES still names the runner's own arm:

| runner | plants | twins with a mech row | twin's detector is another runner |
|---|---|---|---|
| memfn/tests/run_g2_pres.sh (arms g2pres, g2pres-asan) | 35 | 35 | **1: S3012 (suites=g2win, re-aimed text)** |
| memfn/tests/run_g2_win.sh | 38 | 0 | 0 |
| tests/memfn/run_proof.sh (arm memfnfinder, which runs run_proof.sh) | 6 | 4 | 0 |
| tests/memfn/run_wreply.sh | 2 | 0 | 0 |

So **1 of 41** twinned plants has S3012's exact shape.

- The other re-aimed twins carried their re-aim into the runner. S1224 was re-aimed in both places
  by plantfix FUW-12.
- S3044 contains the word "retired", but its suite is still g2pres.
- S3100 and S3101 are g2pres-asan, which is the same runner.
- run_g2_win.sh's 38 and run_wreply.sh's 2 have no mech twin at all, so this census cannot see
  them. Measure 2 covers that gap for the pres runner.

**Sibling count 2: generator-unreached pres plants**
(`s3012tri_evidence/pres_reach_census.sh`). For each of the 35 PLANTS, the census applies the
plant, builds the plain and trace kits, and runs the runner's full pass list through the
generator. That is 3 targets × lever 0/1 at on_miss_leaves 1 with NWIDE 300 and 0, generic
on_miss_leaves 0, the deny pass, and the trace kit's default passes with their MFTRACE stream. A
plant that leaves every file byte-identical is unreached by anything downstream of the text.

Result (`pres_reach_census.out`; the raw log is `pres_reach_census.raw.log`), 25 artifacts per
plant (the rendered files, generator logs and trace streams of 8 passes + 3 trace passes):

- **33 of 35 plants move at least one artifact.** For those, the generator reaches the site.
  The census does not confirm that their detectors fire; that is the dev box's `--plants`
  verdicts.
- **S3012 moves 0 of 25. It is UNREACHED.**
- **S3127 moves 0 of 25, as expected.** It edits only the `@c0` census copy (`census0.py`), which
  the D3 check reads, not the kit.

So within the presence runner, S3012 is the **only** generator-unreached plant: 0 siblings.

Caveat on the census: the first version of the script never created its NWIDE-0 pass
directories, so all 7 `*.n0` runs failed and carry no data. They are excluded by
`retab.sh`, and the script now has the `mkdir`. Those passes are the site-hash stream, the same
sites without the wide tail, so excluding them hides no population the other passes lack.

**"Expected only on a target this box cannot run".** S3012 does not have this shape. It is
target-independent and was never x86-only. Its expected-pass set is not a host restriction, so
none of the counts above depend on the host. Plants whose detection does depend on a target are
S3098-S3103 (x86-64-v3/x86-64 levels, `host_has`) and the ASan pair S3100/S3101. Their reach on
the dev box is what job 200's DETECTED lines confirm for S3106/S3110/S3112/S3125/S3126/S3047; the
rest is outside what this box can confirm.

## Fix shape

D203 fields:
- Class: as above.
- Rule broken: a detector re-confirmed on mechanism change, and twin equality covering the
  detector.
- Sibling count: 1 of 41 twin-detector divergences (S3012 itself), and 0 other
  generator-unreached plants among the pres runner's 35. The window, proof and wreply runners'
  48 plants without a mech twin are outside both measures; a per-runner reach census is the way
  to count them.
- Fix shape: three parts, below.

1. **S3012 itself (the row).** Retire S3012 from run_g2_pres.sh's PLANTS, `plant_spec`,
   `plant_expect` and its `--reach` comment, and add it to run_g2_win.sh's PLANTS with the window
   family's DECIDE check and in-run agreement as its detector. That is the mech twin's own
   detector, 86 fails per mechund, and agree 157 < rendered 200 here. The PLANT_TWINS of each
   runner then follow the move. This is a test-side move with zero kit bytes. Equivalence for
   g2pres is not an argument to drop the plant: the defect is real, and only its detector moved.
2. **The twin check (the class).** `m6read_check_sab_anchors.py`'s twin check (GF-1) should hold
   a declared twin's RUNNER among its mech row's SAB_SUITES (via an arm→runner map, the one
   `twin_detector_census.py` hand-writes here). A mech re-aim to another arm then reds the runner's
   twin until the runner row moves too. This census shows the check would be green today except
   for S3012, so it adds no other work.
3. **Runner detection (the population).** Runner plants are verified to APPLY, never to DETECT.
   Either:
   - give each runner plant a per-site reach measure (the mech half's SAB_REACH discipline: a
     count of the planted site's population that the clean tree reaches, gated on a floor), or
   - schedule the runners' `--plants` modes as an arm of the full battery so a GREEN plant is a
     red gate.

   The pres runner's S3012 reach token shows why the measure must read the plant's own site: it
   counts rendered lever sites, which says nothing about the filter. I recommend the scheduled
   `--plants` arm (D77: the measurement that triggers it exists now, this GREEN) plus the
   site-specific reach tokens for the plants the census flags.

## STATE AT HANDOFF

- STATE: complete (triage; no code edited).
- Rulings file: R-1 and R-2 applied (R-2 is answered in "Class and siblings"); the last applied is R-2. Base run job 100-main-s3012base is main's. By this analysis it
  should read GREEN at any base after d5f9da41b, which is consistent with "file as a kit K row
  with this class and sibling count".
- Evidence (committed): `docs/dev/lanes/s3012tri_evidence/twin_detector_census.py`,
  `docs/dev/lanes/s3012tri_evidence/pres_reach_census.sh`, and their outputs
  `twin_census.out`, `pres_reach_census.out` and `pres_reach_census.raw.log`, plus `retab.sh`.
  The Mac suite lock was taken for the census and released.
  `pres_reach_census.sh` spells the applier's path in two parts. The first draft named it, and
  [SABANCHOR]'s discovery then listed the script as an UNREADABLE RUNNER. After the change the
  plant pass on this tree reads clean (81 plants, 39 twins, rc 0). Scratch-only helpers in
  `/var/tmp/pcrec-claude/scratch/s3012tri/`: `apply.sh`, `apply_old.sh`, `build.sh`, `hist.sh`,
  and the instrumented kit `inst/`.
- x86 runs: no x86 run is needed for the cause; it reproduces identically on the Mac. Optional
  confirmations main may run:
  - On any box, to check that the plant still reds the window family through the mech twin:
    `bash tests/mech/run_sabotage_matrix.sh S3012` (expect DETECTED, arm g2win).
  - On the dev box, to confirm the GREEN is the base's too:
    `bash memfn/tests/run_g2_pres.sh --plant S3012` at b9f81ef80 (expect `PLANT S3012 GREEN`,
    rc 1). This is already job 100-main-s3012base.
- owed: none.
