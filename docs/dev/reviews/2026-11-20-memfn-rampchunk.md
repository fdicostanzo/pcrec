# Review 2026-11-20 memfn-rampchunk (both: timing-spike harness + its decision rule) -- DRAFT, PROPOSED dispositions

## Subject
- Branch lane/memfn-rampchunk = 73fcd5bfe89118c8d0c5dbb2d5da256f666f6a53 (merge-base main 9798d196e), harness
  docs/dev/lanes/rampchunk_bench/; scratch harness scratch/memfn/rampchunk/ (h/, gen/, check/, counts.tsv, decision_rule.md);
  queue job scratch/memfn/fcards/jobs/712-kit-rampchunk + common.sh. Branch files byte-identical to the scratch at freeze.
- RULE_SHA bb841580a3de83f6 = sha256(decision_rule.md)[:16]: verified at freeze and at hand-back.
- BUILD tree worktrees/bconf-night (main f8789cd2e), read-only; no review worktree built.
- Rulings freeze main 24a83ff7e; at hand-back main f55b3bdc6 (plan.md +18 lines, none on REQ-PAST-LAST/ramp/chunk; decisions.md
  unchanged): no FREEZE DRIFT affecting the subject.
- The question (owner, 2026-11-20): "Test the ramp up vs chunk. A max ramp may solve my streaming concerns."

## Lenses as run
| lens | model | question | why chosen |
|---|---|---|---|
| MEAS (measurement + simulate drills) | opus | (a) per-arm axis table, one axis per named comparison? (b) do the verdict form, NO-LOSS and noise handling decide what the owner asked; decide.py drilled on constructed outcomes vs a from-text implementation | launcher's lenses 1-2; a comparison + a declared verdict table |
| FID (harness fidelity + control independence) | opus | (a) is the timed exe the gated, keyed, recorded one? (b) do the answer checks and count model share a source with what they check; do the RC_BUG plants go red | launcher's lens 4; a measurement harness with sabotage rows; the only planting lens |
| GATES (job gates) | sonnet | (a) stop time, wait keys, cap/est, expect lines, CPU pin; (b) does the dry run do no real work | launcher's lens 3 |
Standing questions (sibling / general form + unlocks) carried by FID: FID-6 is the unlock.
Verification: inline by the coordinator (quotes of the cited lines, objcopy .text compares, driver/arm_edit premise of MEAS-6); no REFUTED.

## Overall
NOT READY TO TIME as frozen. Two independent reasons, either sufficient:
1. The headline pair cannot discriminate in this cell design (MEAS-6): every timed cell is ONE rx_search from 0 over 1 MiB, and RAMPCLIP's
   window equals ALIGN's exactly once the search is B bytes in, so 32 of 36 cells are structurally identical and the verdict turns on the
   two `early` row-cells (x2 modes) plus noise. The owner's "streaming concern" is outside every verdict (MEAS-7).
2. At the TIMED B (4096/16384/65536) no control can see a window-rule defect (FID-2/3/5/7): answers are window-neutral by construction,
   the model runs only at B 8/64 and on subjects <= 2000 bytes, and the planted bugs are built only at B 8/64. Re-planted at B=4096,
   bug3 ("no re-ask after an empty window") is SILENT and degenerates to the plain loop, so it would read NO-LOSS and PREFERRED.
Plus verdict-printing holes in decide.py (MEAS-2/3/4/5, GATES-1). The job's gates themselves hold (GATES PROBED-AND-HELD).

## Findings (consolidated)

### Answer / verdict level
- **MEAS-6** (MEAS) -- RAMPCLIP vs ALIGN, "the owner's question", is identical by construction after the first B bytes of each search;
  only `early` differs materially (counts.tsv: unb/early 510 vs 1363 finds); one noise WIN/LOSS in the 32 null cells flips EQUAL to
  PREFERRED/MIXED. VERIFIED (rc_window.h end = min(c+w, blockend(c+1)) and blockend(c+1) <= c+B; driver.c timed modes call rx_search(s, n,
  0) once; arm_edit.diff passes search_from). PROPOSED **FIX-NOW** (design): add a cell family where searches restart (find-all over
  matches every k bytes, or a per-chunk search sequence, k and the chunk independent of B), and/or report pairs per cell class with
  "structurally identical" cells excluded and named.
- **FID-5** (FID) -- RC_BUG plants built only at B 8/64 (rampchunk.py exe_list, `for B in (8, 64)`), exactly where the model runs; at
  B=4096 bugs 2, 3, 4 are SILENT and bug3 times FASTER than the correct arm (indicative single runs). VERIFIED by quote; the plant
  builds are the critic's. PROPOSED **FIX-NOW**: build the plants at one timed B too and require CAUGHT there (needs FID-3 or FID-6).
- **FID-3** (FID) -- no "counts vs model" at the timed B (rampchunk.py check: model only for off/on/zero or B in (8, 64), and only on
  subjects <= model_cap 2000 bytes); a key swap (RAMPCLIP4096 built with ALIGN's rule) passes check and would time ALIGN under RAMPCLIP's
  name, making the owner's pair EQUAL by construction. VERIFIED by quote. PROPOSED **FIX-NOW**: model at the timed B on the B-structured
  corpus subjects (raise the cap there), plus a cross-arm "rules differ on dense" assertion.
- **FID-6** (FID, unlock) -- R-46 B3's own identity (attempt sequence equal to ON's) is a control independent of model() and rc_window.h:
  0 differ on 24 clean arms x the 4490-subject corpus, RED for bug3/4/5 at every B incl. 4096 (OFF differs on 1153/2487 lines, so not
  vacuous). PROPOSED **FIX-NOW**: add the attempt counter to the .c builds and gate on it.
- **FID-1** (FID) -- the timed launch's rc is written to raw.tsv and never read by decide.py; check runs the .t exes on the corpus, never on
  the 1 MiB timed subjects. PROPOSED **FIX-NOW**: one comparison per raw row (rc == (cell == "early")), a wrong rc is a red.
- **MEAS-2** (MEAS) -- a pair with zero counted cells prints "0 wins, 0 ties, 0 losses -> EQUAL" (decide.py h2h `if not W and not Lo`),
  and (a) silently drops every arm; the rule text has the same hole ("EQUAL if W = L = 0"). VERIFIED by quote. PROPOSED **FIX-NOW**
  (rule + script): 0 counted cells = NO-VERDICT. Rule amendment before timing (the rule sha moves).
- **MEAS-4 = GATES-1** (MEAS, GATES) -- NOT-RUN is never produced: measure's `notrun` list reaches only its last stdout line; decide.py has
  no NOT-RUN; a deadline-cut run counts cells on 3-6 launches silently, labels 1-2-launch cells INCONCLUSIVE-NOISE, omits 0-launch cells
  from the list and from the >10% denominator; the job still ends DONE rc=0. VERIFIED by quote. PROPOSED **FIX-NOW**: notrun.tsv (or rows
  in raw.tsv), decide.py takes the planned cell list, prints launches per cell; the job prints a distinct truncated line.
- **MEAS-3** (MEAS) -- the rule says an A/A-inconclusive mode's verdicts are "printed but not counted"; decide.py never computes them (all
  loops run on `cnt`). VERIFIED. PROPOSED **FIX-NOW** (script).
- **MEAS-10** (MEAS) -- medians of 7 with no spread report: a bimodal arm (4/7 slow) flips NO-LOSS <-> LOSES and the pair winner on one
  launch, invisible in decision.md. SUSPECTED as a real-box risk. PROPOSED **FIX-NOW** (cheap): list per verdict the cells whose
  min..max straddles 1 +- thr.

### Measurement / control design
- **MEAS-1** (MEAS) -- AA's .text is byte-identical to ON's (both rows; coordinator re-checked), so the A/A floor measures launch noise of
  ONE binary; every compared pair is two binaries (layout axis uncontrolled). The hand edit is also untimed: zero.t is built, not timed;
  on bnd zero.t differs from on.t (6487 vs 6519 B .text). PROPOSED **FIX-NOW**: time zero (built already) and take a layout A/A (e.g.
  zero vs on on bnd, or one arm at two -falign-functions) into the floor.
- **MEAS-7** (MEAS) -- the streaming concern (look-ahead extent / block crossings) is a "reported fact, not part of any verdict"; for
  RAMPCLIP vs ALIGN crossings are 0 for both by construction, look-ahead waste is 0 on every no-match cell, so the facts discriminate
  only on `early`. Reading risk: "max ramp" may mean R-46's ramp WITH its max (RAMP), and no named pair tests RAMP vs ALIGN; counts.tsv
  already shows ramp4096 crossing a block 255x per dense search. The "chunk" is offset-0 B-aligned, not a caller's stream chunk.
  PROPOSED **owner question via the manager** (which reading of "max ramp"; is a caller-boundary look-ahead predicate the streaming
  concern) then FIX-NOW: make that predicate a verdict row.
- **FID-2** (FID) -- the timed .t and counted .c are separate compiles; the only check on a .t (answers vs OFF) has zero power over the
  window. Plant A (halve the window in the timing build only) passes everything. Twin relation holds today (8 exes rebuilt
  byte-identical). PROPOSED **FIX-NOW**: `gcc -E` diff of each .t/.c pair with RC_COUNT hooks mapped empty.
- **FID-7** (FID) -- (i) the crossing assert shares rc_blockend() with the window it polices (Plant E: SILENT at 4096) -> PROPOSED
  **FIX-NOW**: compute crossings from readmax against an independent block end. (ii) gap 6 is one constant feeding both build and model
  (mitigated: FID-6 shows 6 attempt-identical) -> NOTED. (iii) model() reproduces rc_window.h's shape from the same author's reading
  of B4; catches transcription slips, not misreadings -> NOTED (FID-6 is the independent control).
- **FID-4** (FID) -- check/manifest keyed on CHECK_B, measure on TIMED_B, no subset assertion; dropping 65536 from CHECK_B leaves 16 stale
  timed exes unchecked and dry green (Plant C). PROPOSED **FIX-NOW** (3 lines) + measure re-runs manifest_ok/marker_ok and records them.
- **FID-8** (FID) -- counts.tsv not keyed to the manifest; dry tests only existence. Held today (5 rows re-run). PROPOSED **FIX-NOW**
  (2 lines: manifest sha header, compared in dry).
- **GATES-2** (GATES) -- dry pins tree, exes, subjects, marker and rule sha, but not rampchunk.py/decide.py/driver.c/rc_window.h.
  PROPOSED **FIX-NOW** (add their shas to the pinned set).
- **MEAS-9** (MEAS) -- FIXED is labelled "control" but enters no head-to-head (6 of 27 arms). PROPOSED **FIX-NOW** (rule): name ALIGN vs
  FIXED and RAMP vs FIXED, or drop the label and the arms.
- **MEAS-8** (MEAS) -- axis table: each named head-to-head is single-axis in the code (RAMPCLIP/ALIGN = ramp; RAMP/RAMPCLIP = clip;
  composed/pass = method, information only); X vs OFF is a no-loss bar across emission + edit + rule + method + gap + layout. NOTED
  (held), table kept in the review dir.

### Doc / minor
- **MEAS-5** -- INCONCLUSIVE-NOISE count not printed beside the (b) and VERDICT lines, as the rule requires. **FIX-NOW** (trivial).
- **MEAS-11** -- decision_rule.md amendment stamps "~15:45" (Amendment 1) and "~15:15" (Amendment 2) both post-date the file's 15:08
  mtime and the 15:11 freeze, and are in inverted order; the "before any timing" claim rests on them. **DOC** (correct from the lane's
  own record).
- **GATES-3** -- `wait_quiet || exit 5` and `mkdir || exit 1` print no `kit-rampchunk: DONE rc=` line. **DOC/NOTED** (queue sees red anyway).
- **GATES-4** -- --ready waits only on pending|running; a key never queued, mistyped or re-queued under a new key reads `none` and does not
  wait (keys match today's queue names 710/711). **NOTED**: the manager confirms both keys are queued before 712 is.
- **GATES-6** -- CPU7 hard-coded while CPU_PIN is derived from cards.py; correct today (sysfs siblings 7,15). **PLAN** (derive from sysfs).
- **GATES-5** -- est 1090 s reproduced from the plan (6804 launches); worst case all-void ~2900 s < cap 3980. **NOTED** (held).

## PROBED-AND-HELD (summary; full lists in review/)
- decide.py vs a from-text implementation on 11 constructed outcomes x 6,804 launch rows: floor/thr arithmetic, LOSS test, WIN/LOSS/TIE
  bounds, PREFERRED/EQUAL/MIXED map, INCONCLUSIVE-NOISE exclusion, VOID skip, re-time count agree; divergences only MEAS-2/3/4/5.
- Every timed .t (54) and its .c twin are inside the 174 checked exes; all answer-checked vs OFF over 4,490 subjects; OFF vs python re 0.
- Key = code: 8 exes rebuilt from the frozen sources byte-identical to the live build and manifest.
- Timed site has one caller; .t builds carry no RC_COUNT code; physical reads stay inside lim.
- Attempt identity vs ON: 24 clean arms x whole corpus, 0 differ.
- Job: --ready 77/75 paths, run-path re-checks before/after the quiet wait, expect regexes vs real prints, decl cap > est, CPU pin.
- Dry path writes nothing (find -newer empty), takes no lock, makes no queue call.
- Freeze: live h/, gen/, check/, counts.tsv, manifests, rule and job file identical to the frozen copies (but see the scope incident).

## By-id completeness
MEAS-1..11, FID-1..8, GATES-1..6: every id dispositioned above (MEAS-4 and GATES-1 one item).

## Scope incident
`scratch/memfn/rampchunk/h/__pycache__/rampchunk.cpython-314.pyc` was created at 15:16:28 by a critic's in-process import of the
harness (`python3 -I` does not imply -B). Harmless to the run; not removed by the coordinator (no-edit mandate). The launcher removes it.

## Lessons for the guide (proposed; details in .coord/process.md)
1. Harness-fidelity lens: plant the harness's OWN sabotage rows at the TIMED parameter values, not only where the harness built them
   (FID-5).
2. Measurement lens: per named head-to-head, compute over the planned cells where the two arms can differ at all (MEAS-6).
3. COMMON scope block: run the subject's Python with `-I -B` (scope incident).
4. D27-style note: the count model and the rule text share one author's reading of R-46 B4 (FID-7 iii); an attempt-identity control
   (FID-6) is the independent oracle and should be standard for answer-neutral window/skip remedies.

## RULING (kit manager, 2026-11-20 15:30)
- Every PROPOSED FIX-NOW is ACCEPTED: MEAS-1, 2, 3, 4 (= GATES-1), 5, 6, 9, 10; FID-1, 2, 3, 4, 5, 6, 7(i), 8; GATES-2. They go to the fresh lane rampfix.
- MEAS-6: add restart cells. A find-all sequence of searches, each starting after the previous match, over subjects with matches every k bytes (k independent of B) and dense occurrences between them. Each pair is reported over the cells where its two arms can differ; structurally identical cells are excluded and named.
- MEAS-7: ruled by the manager, not asked. Both readings are covered, so the choice changes no answer: RAMP vs ALIGN becomes a named pair beside RAMPCLIP vs ALIGN. The streaming concern becomes a verdict row, STREAM-SAFE iff the arm has 0 chunk-crossing asks on every cell, counted against an independent block end (FID-7(i)). Caveat kept: the chunk is B-aligned from the subject start, a model of stream offset 0. A real stream clips at the chunk it is given.
- MEAS-9: name ALIGN vs FIXED and RAMP vs FIXED.
- MEAS-11, GATES-3: DOC, fixed by rampfix. FID-7(ii, iii), MEAS-8, GATES-5: NOTED. GATES-4: the manager confirms both keys are queued before 712. GATES-6: PLAN.
- Scope incident: the manager removed the stray `__pycache__` (the file, then rmdir). Lesson 3 (run with `-I -B`) goes into the fix brief.
- The rule is amended before timing and gets a new RULE_SHA. A sized re-check (one critic, on the fixes) runs before 712 is queued.
