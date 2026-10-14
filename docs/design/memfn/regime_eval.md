# [REGIME-EVAL] — the replay evaluator for the knowledge-filtered regime table (rev 1)

Status: **REV 1, PROPOSED, design only** (rev 0 lane `regeval`, 2026-10-13, branch
`lane/memfn-regeval` cut from `lane/memfn-r17` at efcc3cd20; rev 1 lane `regeval2`,
2026-10-14, branch `lane/memfn-regeval2`, applies main's review). Nothing under `src/`,
`memfn/src/`, `tests/` or `lib/` changed, nothing was timed, and no `make` ran. A cheap
prototype of the replay runs on the grid1 slot's EXISTING logs:
`regime_eval/replay_proto.py` (§8). A D6 panel follows.

**Change log, rev 0 -> rev 1** (main's review, 2026-10-14):

1. **Judge cells are STREAMED** (§2.4, §3.4 `prereg.tsv`, §2.6). F2 measured the walk at
   0.4-22 branch misses/KiB on repeated 64 KiB buffers and 150-250 on fresh 1 MiB, so a
   repeated judge flatters the walk exactly where the table picks forms. Repeated 64 KiB
   survives only as a labelled, UNGATED column that reports the predictor-training effect
   (P-PRED). Wall re-estimated: gating slots 150 -> ~235 min (§2.4); J-c dropped from the
   gating plan. X2 and the fit-condition label updated (§3.2, §2.1).
2. **Consumer-bound cells are a COUNTED class** (§2.7): a pre-registered measured
   criterion (equal branch misses across forms AND walk-vs-best inside NULL), its own rows
   in `cells.tsv`/`summary.txt`, and every denominator quoted with and without the class
   (G2 and G3 gate on the without-class form).
3. **New reported quantity P-MOVE** (§3.2): the share of RT cells whose best form differs
   from the walk beyond NULL, plus how concentrated the table's saving is.
4. **§9 is now "Questions — resolved"** (main, 2026-10-14), each with its ruling and rider.
5. **§8** notes that regime_tables corrections 1-4 were accepted and applied by main.
6. §10's charter-vs-committed checklist is extended with the five items above.

Owner (Frank, 2026-10-13): the kit owns the rows, this evaluator and the twin
([REGIME-TWIN]). pcrec owns the knowledge plumbing ([REGIME-LANDINGS]), the iterator
([FINDALL-NEXT], D165), the measurement sets ([MEASURE-SET], D166), the engine arms,
and comments on the kit's work.

Inputs read: main's `docs/design/regime_tables.md` rev 0.2; D27, D144 (+ add. 1, 4),
D147, D161 add. 11-12, D162 (+ add. 1-4), D165 (+ add. 1), D166; plan rows [REGIME]
and children; `costmodel_report.md`, `gridread_report.md` (+ `gridread/`),
`grid1_report.md` + `grid1/README.md`, `vecspike_reading.md`; `memfn/docs/responses.md`
through the D161 add. 11 notice. lane/rwcorpus has no commits yet (its cache
`worktrees/.corpus/` holds prose, non-English and one CSV so far); lane/memfn-r17bp has
no committed note, so this design reads regime_tables' rows as the table under test.

Vocabulary: a **cell** is one (pattern/site, subject slice, mode, call shape). A
**form** is a kit search form (WALK, V1 = SWAR W=8, S1/A1 = SSE2/AVX2 W=64, V3/S3/A3 =
the same with state kept across calls). **Regret** = measured ns of the table's pick −
measured ns of the fastest form the layer offers on that cell. **The walk** is the
scalar table walk, the D147 floor every percentage is quoted against.

## 0. Summary

1. **Replay, not modelling.** The evaluator asks the BUILT table what it picks for each
   cell's knowledge record and looks up that form's measured ns. The best form is the
   fastest TIMED arm, never a prediction. It cannot see dispatch cost; [REGIME-TWIN]
   owns that term (§1.4).
2. **Fit on grids, judge on held-out text, judged STREAMED.** Thresholds come only from
   synthetic grids (grid1 F1/F3 today, F4/F5/F7 later), published as a measurement set
   (D166). The judge populations are the [REGIME-CORPUS] subjects × the blinded user
   patterns, the bench's population, and later Zen 1. Every judge cell is timed on
   streamed (distinct, several-MiB) or whole ≥ 1 MiB subjects, never on a repeated
   64 KiB buffer (§2.4). ALPHA and spike cells are reported but do not gate, because
   costmodel read them (§2).
3. **Pre-registered, loose acceptance** (§3): four gate bars per layer and shipped
   filter (aggregate dominance over every fixed form, per-regime caps, an outlier
   budget, evaluator validity), plus named predictions and reported quantities that
   never gate (including P-MOVE, P-PRED and the consumer-bound class, §2.7). The bars file is committed and hashed before any judge timing exists. The
   evaluator refuses to judge if the bars moved or the slot started first.
4. **Failing-direction controls** (§4): each row deleted, swapped thresholds, the old
   R3 error, R0 removed, per-site g* replaced by the PF figure, the wrong box's set, and
   an A/A control. Each control must score VISIBLY worse under a pre-declared rule that
   counts noise only on the cells the control moved. Every control is expressed through
   the build's own knobs (a measurement-set file and a row deny), never a second table
   (§5).
5. **The prototype already pays.** Replaying rev 0.2 on the grid it was fitted from
   reproduces §3's S0 row exactly (11.1/1.2/0.0 SIMD-on, 18.8/16.6/0.1 SIMD-off). It
   also finds that the S1-SIMD-off and S3 figures in regime_tables §3 are the cost
   model's, not the rows'; that S2 SIMD-off loses to always-walk because R3's SIMD-off
   arm is missing; and that R0/R1 are unreachable on the grid (§8, F-1..F-8).

## 1. The replay: inputs and output

### 1.1 The cell and its knowledge record

A cell is `(site, subject, mode, call)`:

| field | values | source |
|---|---|---|
| site | pattern id + kit site index (an artifact may hold several; D165 add. 1 says one stateful FIND per search entry today) | the compile; the kit's MF_TRACE site list |
| subject | corpus file id + slice (offset, length) + sha256 of the slice bytes | the [REGIME-CORPUS] manifest; slices at fixed offsets |
| mode | `first` (one call from 0), `all` (find-all through `_search`, match_api.md §3.1), `iter` (find-all through the iterator; emulated by grid1's keep arm until D165 builds, §2.8) | the timing row |
| call | `whole` (the slice is the subject) or `lines` (one call per line, the grep shape; a new harness mode, §2.4) | the timing row |

Each cell has one KNOWLEDGE record, keyed as in regime_tables §2. A filter S0-S3 masks
it:

| key | value in a cell | where it comes from | filters |
|---|---|---|---|
| P | site kind (PF scan / DFA hat / VM hat / MLINE), term count, RANGE-term count, layer (SIMD on/off) | the compile: the kit's site description in the MF_TRACE build (the same dump `n2_census.py` reads) | all |
| N | `n − startpos` at call entry | the call shape: whole → slice length; lines → each line's length (the replay uses the per-call distribution, §1.3) | all |
| M | one-shot or iterator | the mode | all |
| E | landing gap g per candidate stop | **before [REGIME-LANDINGS]**: the evaluator derives g from an EXEMPLAR file of the same class, never the timed slice, using pcrec-analyze's unigram and bigram counts (the kit's own derivation, labelled `E=exemplar-bigram(kit)`). **After**: the analysis object's landings kind (`E=analysis(landings)`, D162 provenance). An ORACLE arm (`E=oracle`, counted on the timed slice) is reported as an upper bound and never gates. | S1, S3 |
| H | the previous step's span; candidates per block | the counting twin (`cnt`, never timed): activation span ADV/A per call; per-block popcounts from the `blocks`/`uses` counters | S2, S3 |
| A | WHICH MEASUREMENT SET (D166 item 3) | a set file: id, box, run, method version, values relative to the walk's per-byte cost, with absolute ns as provenance only. Until [MEASURE-SET] exists the kit writes the set in its own TSV; the evaluator reads the set by id and records its sha256. | all |

### 1.2 The measured ns of every candidate form

The measured ns come from the grid1 harness, the kit's standing instrument
(`docs/dev/lanes/grid1/README.md` is the arm contract):

- **Base arm (`walk`).** The kit-branch compile of the pattern with
  `--memfn=no-pf-terms-mask`.
- **V1 arm.** The default compile (R17-b's `pf_terms_mask`).
- **S1/A1, S3/A3/V3, Sn/An arms.** `mkvar.py` builds these from the V1 artifact. It
  edits only the site's struct and its `next_candidate`. `build.sh` proves that
  `gen(w8,0,0)` assembles identically to V1. Once the SIMD rows are BUILT (R17-b″),
  real kit renderings replace the hand edits for those forms, and the hand edits
  stay only as twins.
- **Both layers in every cell (Frank, 2026-10-13: "this entire effort is BECAUSE of
  simd").** The SIMD-off layer offers {walk, V1}; the SIMD-on layer adds {S1, A1}.
  The iterator variants add the kept forms. Each layer's best is taken over its own
  arms.
- **pcrec's engine arms (grid1's EXT arms, lane slotarms).** They hold the CONSUMER
  fixed. A cell's base is the pattern's own route, so a form's delta is the search
  form's alone. The evaluator reads EXT rows only to report the consumer's share of
  a cell's time (the TUG regime's ~34%, costmodel §0). It does NOT judge pcrec's own
  route table (`cand_rows[]`), which is pcrec's.
- **Correctness gate first** (`check.sh`, legs R, L and C). Every arm's answer line
  and match list equals the base's. The base equals the reference oracle (libpcre2
  10.46 through `tests/oracle/`'s local adapter; python `re` cannot read user
  patterns). A cell that fails the gate is EXCLUDED and listed, never timed.
- **Measurement.** As grid1: `taskset` CPU 14, governor `performance`, the quiet gate
  (load1 < 1.5), an A/A pair per group (`walk`, `walk#b`), rotated interleaving,
  LAUNCHES rounds, and the median of 7-round medians. **The subject condition is part of
  the measurement (§2.4):** judge groups run STREAMED or on a whole subject ≥ 1 MiB.
- **Branch-miss pass (perf).** Where `perf_event_paranoid` ≤ 2 (it is 2 on this box,
  so user-space events work), the judge slots run F2's pass (`grid1/f2perf.sh`:
  `cycles:u,instructions:u,branches:u,branch-misses:u`, 3 launches) on every judge group.
  It classifies the consumer-bound cells (§2.7) and reports P-PRED (§3.2).

### 1.3 The output

For every (cell, layer, filter):

- **the pick**: the row that fired and the form it chose;
- **the best**: the fastest timed arm of the layer;
- **regret** = ns(pick) − ns(best), raw. It is in absolute ns per pass and is also
  normalised per call and per MiB, because a DINGHY cell is ~16 ns and a LINER MiB
  is ~0.27 ms (gridread §5.2);
- **the cell's NULL threshold**: gridread's max(A/A floor, 3.09% of the walk), with a
  launch-sign check;
- **the walk's ns**, for the percentages.

Per regime (DINGHY / TUG / LINER, §2.5), each figure is summed:

- the absolute regret;
- regret as a % of the summed walk;
- the same for every fixed-form policy (always walk / V1 / A1 / A3);
- the summed A/A floor.

On `lines` cells N is per call, so the knowledge record, and hence the pick, can
differ per line. The replay prices a per-line pick by the per-call ns of each form.
The counting twin reports the per-call span histogram, and the harness reports ns per
pass = Σ over lines. **The replay therefore needs per-form ns for the lines that fall
in each N band.** These come from separate groups whose subject is the slice's lines
bucketed by length (`<32`, `32-63`, `≥64`; the R1/R2 boundaries come from the set,
not from this note). Each bucket is one streamed subject.

### 1.4 What replay cannot see: the dispatch

The prototype makes the gap concrete: an artifact built from the table carries every
reachable form behind run-time compares. regime_tables §1 says it emits "the union of
the picks over the rows reachable under the knowledge it can ever have", and N, M and
H rows become emitted compares (the kit's D161 add. 11 notice, item 1). Replay prices
the pick as if the artifact held only that form. It misses:

1. the compare per call (N, M) or per block (H, R4);
2. code size and its layout effects (two or more forms per site);
3. R4 altogether. R4 switches form INSIDE a call per block, so no per-pass median of a
   single-form arm prices it. The prototype declares it NOT REPLAYABLE.

These go to [REGIME-TWIN]. Its hand-built table arm (real emitted compares) is timed in
one grid slot against the fixed forms and against the per-row best on the same cells.
It yields a dispatch term per (row set, site kind, A) as a SET VALUE. The evaluator then
re-runs §3's bars with that term added to every pick whose cell can reach more than one
form. R4 is scored only by the twin. Until the twin reads, the bars state that they
exclude dispatch, so no R4 or H-dependent row can pass on replay alone (§3.3).

## 2. Populations, the fit/judge split, and placement

### 2.1 FIT (thresholds come only from here)

- **grid1 F1 and F3** (Zen 4, 2026-10-13): 141 + 8 groups. These give the constants
  regime_tables rev 0.2 reads.
- **Later grids**:
  - F4 and F7, through D165's real iterator (R3, R4, A3);
  - F5, Zen 1, through a bench window (every W=64 row moves);
  - the missing axes regime_tables §5 lists: near-hit depth, bytes against landings,
    multi-position filters, and real text's predictability mix *as a synthetic axis*.
- **Fit subject condition.** Every set row carries the subject condition its constant
  was fit on (`repeated64k`, `streamed`, `whole1m`). grid1 F1/F3 are mostly
  `repeated64k`, which flatters the walk's predictor (F2), so their constants are
  labelled `fit-repeated`. F4/F5/F7 run STREAMED (grid1's streamed mode). A streamed
  re-fit of the F1/F3 rows is FILED with its D77 trigger: P-PRED (§3.2) showing that the
  repeated-to-streamed change moves any row's pick on the judge cells.
- **Output.** A fit produces ONE measurement set (D166): one box, one run, one method
  version. Its id names the grid run (for example `zen4-grid1-v1`). The kit owns its
  values; a fit that changes a row's constant is a ruled row diff (regime_tables §6
  item 3).
- **WITNESS cells** (new, §4.4). These are synthetic cells built so that every row has
  a cell that reaches it: R0 needs a ≥2-RANGE-term site; R1 needs a one-shot call
  with n < 32. They are not FIT data; nothing is fitted on them. They exist so that a
  row-deletion control can fire, which is the [MECH-REACH] requirement.

### 2.2 JUDGE, held out

| id | population | status | gates? |
|---|---|---|---|
| J1 | [REGIME-CORPUS] subjects × the blinded user patterns | collecting (lane/rwcorpus; the user agent follows) | YES |
| J2a | the bench's published patterns and subjects (`pcrec-bench/bench/*/patterns/` and its subject generators, read-only; lane rewtwin's precedent), timed by the grid1 harness at the kit tier. A published subject under 1 MiB is replaced by a STREAMED set generated from the bench's published generator at distinct seeds (§2.4); the generator's id and seeds go in the manifest | available now | YES |
| J2b | the bench's own run of a table build on targeted hardware (D144 add. 4), via main | after the build | the OFFICIAL verdict; not a replay |
| J3 | ALPHA (slot25c) and spike cells | seen by costmodel (its regimes, 3.42 ns/use) | NO: reported as "semi-held-out" |
| J4 | Zen 1: J1 + J2a subset re-timed on ubuntubudu via a bench slot request through main | after F5 | YES for the Zen 1 set; also the wrong-box control (§4.1 C6) |

- **Isolation.** No judge cell's timing is read before the pre-registration (§3.4).
  Judge results never feed a threshold. When a judge reading moves a row, the new
  constant is FIT on a new grid, and the old judge population becomes FIT-contaminated
  for that row. It is listed as such in the next run's manifest.
- **The bench rule.** Bench-only questions go to main for relay (memory: ask the
  bench dev). The evaluator never reads the bench's ledgers. It uses only published
  pattern and subject definitions, and the bench's own reports for J2b.

### 2.3 J1: from blinded questions to cells

- **The user agent.** It is D27-blinded: no `src/`, no `tests/`, no bench patterns,
  no regime documents. It writes questions in natural language and the PCRE pattern
  for each, per corpus class. Main owns that lane and commits the pattern list with
  its sha256.
- **Freezing.** The evaluator freezes the list by hash at pre-registration (§3.4). A
  pattern added later belongs to the next run.
- **Site mapping, no clock.** Each pattern is compiled with the kit branch at both
  layers (`-fno-memfn-simd` and `-fmemfn-simd`) with the N2 census tooling
  (`tests/memfn/n2_census.py`'s pool, which records row selections per site through
  the MF_TRACE build). Each pattern lands in exactly one class:

| class | meaning | in the replay? |
|---|---|---|
| REFUSE | pcrec refuses the pattern (a module not built, a limit) | no; counted with its diagnostic |
| NOSITE | compiles, no kit FIND site on any search path (anchored whole-match, pure DFA with no set prefilter, ...) | no; counted |
| OTHER | a kit site whose form family the regime table does not cover yet (`pf_memchr`, the `vrun` pre-check, MLINE, ADVANCE) | no; counted per family. D161 add. 11 grows the table over (stop, form), and these become in scope then |
| UNREACHED | a regime-table site that never runs on the class's subjects (counter leg U zero; for example the required-byte pre-check answers first, grid1 §5) | no; counted per subject |
| RT | a regime-table site that runs | YES |

- **Completeness (K35).** The five counts must sum to the frozen pattern total. The
  evaluator fails closed if they do not. Every non-RT pattern is LISTED in the
  results with its class and reason, never dropped silently. The summary leads with
  the RT share. If the blinded population mostly misses the table, that is the first
  finding, before any regret.
- **Subjects per pattern.** Each RT pattern is timed on two timed files of its OWN
  class and on one file of a FOREIGN class (fixed by a rotation declared at
  pre-registration). A third file of its own class is the E exemplar (§1.1) and is
  never timed.

### 2.4 Timing the held-out cells: STREAMED condition, shape, count, slot wall

**The streamed condition (pre-registered; §3.4 puts it in `prereg.tsv`).** Why: F2
(`gridread/f2_counts.txt`; the F2 notice in `memfn/docs/responses.md`) counted the walk's
branch misses at 0.4-22 per KiB on a REPEATED 64 KiB buffer and 150-250 per KiB on fresh
1 MiB text. A judge on repeated buffers lets the walk's predictor learn the subject and
flatters the walk exactly where the table picks forms (gridread's X2 reading). Rev 0 timed most
judge cells that way; rev 1 does not. Every JUDGE cell, including the J2a and WITNESS
cells and the lines buckets, runs on one of:

- **(S) a streamed subject**: a directory of 64 DISTINCT 64 KiB buffers (4 MiB in all)
  cut from the pattern's class corpus at distinct offsets, disjoint from the E exemplar,
  every buffer's sha256 in the manifest. grid1's cursor never resets, so consecutive
  passes see distinct data (`grid1/README.md` item 5; check leg C rejects a driver that
  does not cycle). `ns/pass` is per buffer, and the regret sums are per MiB;
- **(W) a whole subject of at least 1 MiB** (the size F2 counted).

A cell timed ONLY on a repeated subject is `REPEATED-ONLY` and never enters a gate.
Total size is at least 4× the largest fresh size F2 measured. The size is pre-registered
and is not fitted. The class corpus must supply 4 MiB outside the exemplar; a class that
cannot is served by (W) alone and listed.

**Cell shapes per RT pattern (own class), all gated:** `first`/S, `all`/S, `all`/W (1 MiB),
`all`/lines (S, bucketed, §1.3), `iter`/S. That is 5 groups per RT pattern for J-a/J-b.
The foreign-class group and the second own-class file are the optional J-c (below).

**The repeated column (UNGATED, labelled `rep64k`).** One extra group per RT pattern:
`all` on a single REPEATED 64 KiB own-class buffer, all arms. It costs little and
measures a named quantity, the PREDICTOR-TRAINING EFFECT (P-PRED, §3.2): the same
cell's walk ns, and each form's ns, repeated against streamed. It also gives the
like-for-like column against the in-sample (`fit-repeated`) figures of §8. It never
feeds a bar, a control, or a pick.

**Harness extension H1 (kit, small):** a `lines` subject = a manifest of line buffers,
one pass = one call per line through the existing streamed-cursor code (README item 5).
The extension is a manifest generator that splits the slice into per-bucket line
buffers. The driver is unchanged. Check leg C already proves the cursor cycles.

**Estimate** (the formula, so that main can rescale; SEC = 0.65 s per launch on a
repeated 64 KiB subject, 0.95 s on a 1 MiB or streamed one, grid1 §3's measured values;
launches use 3 rounds, with 7 arms on `all`/`iter` groups and 5 on `first`/`lines`, about
7 on average):

```
rev 0 (judge on repeated 64 KiB, 4 of 5 shapes; gating = J-a + J-b)
  J1 gating  350 groups (70 RT patterns x 5) x ~7 x 3 = ~7,350 launches
  J2a        ~40 patterns x 3 groups x 7 x 3          = ~2,500 launches
  9,850 launches x ~0.71 s (4/5 at 0.65, 1/5 at 0.95) = ~117 min, + 2 gate passes
  (~15 min each) = ~147 min     [rev 0 quoted ~150]
rev 1 (every judge cell streamed or >= 1 MiB)
  the same 9,850 launches x 0.95 s                    = ~156 min   (+33% on the timed part;
                                                        +46% if every rev 0 cell had been 64 KiB)
  repeated column  70 groups x 7 x 3 = 1,470 launches x 0.65 s = ~16 min
  perf pass (F2 method)  ~1,750 arm rows x ~0.6 s     = ~18 min   (F2 ran 72 rows in 43 s)
  3 gate passes (check.sh + counting, no clock)  3 x ~12 = ~36 min
  total gating  ~226 min (~3.8 h), +54% on rev 0's ~147
optional J-c (foreign class + second own-class file, 420 groups x ~7 x 3 = ~8,800 launches):
  rev 0 ~104 min; rev 1 at 0.95 s ~140 min
```

**The fit into slots.** J-c is DROPPED from the gating plan (it was already optional,
and J-a/J-b alone gate). It runs only if main asks for the out-of-class read or if the
J-a/J-b result shows class sensitivity. Patterns per class stay at ~20. Gating work is
three slots of about 75 min:

- **Slot J-a1** (~80 min): J1 `first`/S and `all`/S at both layers, no kept arms.
- **Slot J-a2** (~70 min): J1 `all`/W and `lines`/S.
- **Slot J-b** (~76 min): J1 `iter`/S, J2a, the repeated column, the WITNESS cells.
- **Slot J-c** (~140 min, optional, ungated, unscheduled).

Each slot first runs `check.sh` and the counting pass, no clock, ~10-15 min, and runs the
perf pass (§1.2) on its own groups. One heavy run at a time, through main's slot
channel. On Zen 1, the J4 subset is J-a1's cells only: about 2.2× the wall on
ubuntubudu's slower core, so ~3 h. J4 runs no perf pass, and its consumer-bound labels
are inherited from the Zen 4 cell of the same id, flagged `inherited`.

### 2.5 Regime placement

A cell's regime comes from the COUNTED facts of its own counting twin, never from
timings or the table:

- L = bytes advanced per activation (ADV/A);
- g = bytes per use (ADV/U).

Placement uses costmodel's rule: DINGHY if L < 64, else TUG if g < 18.5, else LINER.
This is the rule regime_tables §3's regret table is reported in, so judge figures
compare to the fit's one for one.

The rule is pre-registered as a REPORTING bucket only, and it never decides a pick.
A second column re-buckets with gridread's W=64 boundaries (L ≥ 8-32, g ≥ 4) for
reference and is not gated.

Real text adds one axis the grid controlled: landing PREDICTABILITY (gridread §5.3:
+4-7 ns per unpredictable landing on the walk). The counting twin cannot see it.
F2's branch-miss count could, if Frank lowers `perf_event_paranoid`. The per-cell file
therefore carries a `pred` column: the walk's ns per use on the cell, divided by its
grid value at the same g. It is a derived observation, reported only.

### 2.6 The prototype's population lesson

Requiring every arm timed (gridread §6.2's 101 groups) silently drops grid1's L = 8
groups, because those time only walk/V1/A1/A3. The kit's R3 correction (A3 loses at
L ≈ 8) rests on exactly those groups.

The evaluator's population rule is therefore: **every form the table can PICK in that
layer is timed; the best is the minimum over the arms that were.** Cells missing a
non-pickable arm are kept and flagged `partial`. A population rule is part of the
pre-registration, never chosen after the reading.

The rule has a second clause, **the subject condition**: a cell enters a gate only if
its judge timing is STREAMED or ≥ 1 MiB (§2.4). A `rep64k` cell is reported in its own
labelled column and never gates.

### 2.7 The consumer-bound class: a COUNTED class, with its own rows

F2 showed that on bounded prose every form misses the same as the walk, 145-160 per KiB
at 1 MiB. Those misses belong to the CONSUMER (the `[a-z]+\b` run verify), not to the
scan. No scan form can turn such a cell. It adds the same time under every form, so it
does not move the table's regret, but it inflates the "% of walk" denominators and so
dilutes G2's percentages.

**Definition (measured, pre-registered).** A cell (layer) is CONSUMER-BOUND (`cb = 1`) iff
all three hold:

1. **Material misses:** the walk's branch misses are at least 50 per KiB. Below that
   the equal-miss reading is counter noise.
2. **Equal misses:** (max − min of misses/KiB over the layer's timed arms) ÷ the walk's
   misses/KiB ≤ 20%. This is the F2 criterion itself, "every form misses the SAME as
   the walk".
3. **Nothing to gain:** ns(walk) − ns(best) ≤ NULL_cell (§1.3). A form that wins on
   instructions despite equal misses is not consumer-bound, and the cell stays in.

**Why this criterion and not the timing spread alone.** The spread alone cannot tell a
consumer-owned cell from a scan-owned cell where the forms simply tie (a LINER default,
which is where the table is supposed to be right). Equal misses are the mechanism. A
cell with unequal misses has a scan to improve. perf is available on this box
(`perf_event_paranoid` = 2, user-space events), and F2's pass is the instrument.

**The constants (20%, 50/KiB) are CHOSEN, not fitted**, and labelled so (D149, the
suspect-tuning-constants rule). F2's 12 fresh-1 MiB cells give:

| cell | spread ÷ walk misses | reading |
|---|---|---|
| bounded prose1m | 10.5% | the one member |
| bounded docs1m, code1m | 40%, 40% | not |
| dfa-hat prose / docs / code 1m | 44%, 38%, 38% | not |
| hex-run prose / docs / code 1m | 81%, 77%, 79% | not |

20% sits in the gap [10.5, 38]. The evidence is thin (one member cell). So the report
also prints the CB count at tolerance 10% and 35%, ungated, so a boundary effect shows.
The thresholds are fixed in `prereg.tsv` before the judge slot (§3.4).

**Where perf is unavailable** (Zen 1 box, the Mac): the cell reads `cb = unknown`
(inherited from Zen 4's same-id cell on J4, flagged) and is counted as NOT
consumer-bound in the "without the class" denominators. That choice is conservative: it
cannot make a gate easier to pass.

**Reporting.** CB cells are LISTED, not hidden inside regime sums:

- `cells.tsv` carries `cb` (0, 1, unknown) and `cb_misses_spread`;
- `summary.txt` has a CB block: count and share of RT cells per layer × regime × site
  kind, and the patterns whose cells are ALL consumer-bound;
- every denominator is given both ways:

  | quantity | WITH the class | WITHOUT the class |
  |---|---|---|
  | Σ walk ns per layer × filter × regime | W_all | W_exCB |
  | regret as % of the summed walk | R / W_all | R / W_exCB |
  | outlier share (G3) | outliers / RT cells | outliers / non-CB RT cells |

- **What gates:** G2's caps and G3's rates gate on the WITHOUT-the-class form, because
  CB cells carry about zero regret and dilute the with-class percentages, so the
  stricter form is the honest one. G1 sums nanoseconds and is unaffected: CB cells stay
  in the regret sums, since the table's pick there is still a pick. The with-class
  figures are reported beside every gated one.
- E4 re-derives the in-sample figures of §8 WITHOUT the class (F2's labels cover the
  grid's bounded cells) before `prereg.tsv` fixes the G2 caps, so the proposed caps stay
  only if in-sample WITHOUT-class is within them.

A CB cell's cause is a pcrec/origin matter ([FIND-BOUNDARY-SIDE], origsurvey's
BYTE-ONLY 53%), not a table matter. The report says so beside the count.

## 3. Pre-registered acceptance (loose, per Frank)

Frank (2026-10-13): looser bars are fine. Outliers and some regression are accepted for
a cleaner, clearer design. What is not loose is WHEN the bars are fixed.

### 3.1 Gate bars

Each bar is evaluated per layer (SIMD-off, SIMD-on) × per SHIPPED filter, on J1 ∪ J2a
pooled, over STREAMED or ≥ 1 MiB cells only (§2.4), with raw regret. G2 and G3 gate on
the WITHOUT-the-consumer-bound-class form (§2.7), and both forms are always printed:

- R17-b′ ships S0, and S1 where E arrives.
- R17-b″ ships S2 and S3.

| bar | statement | proposed value |
|---|---|---|
| G1 aggregate dominance | Σ regret(table) ≤ Σ regret(P) + NULL(P) for every fixed-form policy P ∈ {always walk, always V1, always A1, always A3 (iter only)}. NULL(P) = Σ, over the cells where the table and P pick differently, of each cell's NULL threshold. | as stated (no free constant) |
| G2 regime caps | regret as % of the regime's summed walk (non-CB cells, W_exCB) ≤ cap | SIMD-on: DINGHY 15, TUG 5, LINER 2. SIMD-off: DINGHY 25, TUG 20, LINER 2 |
| G3 outlier budget | An OUTLIER is a cell whose pick is slower than the walk by more than 50 ns per call AND by more than 25% of the walk's ns. Outliers are at most 5% of non-CB RT cells, and their summed excess over the walk is at most 25% of the table's summed saving over the walk. | 50 ns, 25%, 5%, 25% |
| G4 evaluator validity | Every control in §4 is WORSE where reached. A control UNREACHED on the judge population must be WORSE on the WITNESS population. The A/A control reads inside its floor. | as stated |

Why these numbers, briefly:

- **G2's caps are the in-sample replay** (§8: SIMD-on S0 DINGHY 11.1-13.7%; SIMD-off
  S0 DINGHY 18.8-20.2%, TUG 16.2-16.6%) **plus headroom.** "Loose" means a held-out
  population a little worse than the fit still passes. The §8 figures are `fit-repeated`
  and include any consumer-bound grid cells. E4 re-derives them without the class
  (§2.7) before the caps are fixed, and the caps below stand only if the new figures are
  within them.
- **LINER is tight on purpose.** It is where the table's default lives, and a 2%
  LINER regret would mean the default is wrong.
- **SIMD-off TUG is wide on purpose.** Frank ruled LINER (V1) as the default with no
  data. gridread §6.2 shows always-V1 regrets 16.6% in TUG in-sample, and the ruling
  rests on X2 ("real text leans LINER"). The cap is not where that bet is judged;
  prediction X2 below judges it.
- **G3's 50 ns per call** is about three DINGHY calls (gridread §5.2: ~16 ns per
  DINGHY call). It catches a per-call disaster. A 1-2 ns per-call nudge is accepted as
  "some regression".

A failed gate sends the TABLE back to the kit. It does not send the forms back. The
failure report names the regime and the row that fired in the cells carrying the
excess.

### 3.2 Predictions (reported, never gating)

Each prediction is written down now and reported CONFIRMED / REFUTED / UNREACHED:

| id | prediction | if refuted |
|---|---|---|
| X2 | On J1 STREAMED, SIMD-off S0's TUG regret (W_exCB) is at most the in-sample 16.6% (real text leans LINER). The in-sample figure is `fit-repeated`, so the like-for-like comparison is the `rep64k` column (reported beside it), and streamed is expected to read lower: streaming costs the walk its trained predictor, so V1 (the SIMD-off default) loses less. A streamed figure ABOVE 16.6% is the strong refutation | re-open the SIMD-off default (D162 totality is unaffected: WALK becomes the SIMD-off default) |
| P-R1 | R1 picks the walk on at least 80% of J1's `lines` cells with N < 32, and the walk is the best there | R1's crossover moves (kit's note: with landings in the call the crossover passes 32 B) |
| P-R5 | on J1 at S1, R5's per-site g* cuts SIMD-on DINGHY regret vs S0 by at least half | the per-site g* is a grid artifact |
| P-E | the gap between E=exemplar and E=oracle regret is at most 2 points of the walk in every regime | the exemplar is a poor proxy; [REGIME-LANDINGS] carries real landings, or E is not worth shipping |
| P-RT | at least 40% of the blinded patterns are RT | the regime table covers too little of real use for its cost; widen it (D161 add. 11) before tuning it |

Reported quantities (no bar, no refutation row; the numbers are printed and read by main):

| id | quantity | why it is reported |
|---|---|---|
| P-MOVE | the share of RT cells whose BEST form differs from the walk at all, i.e. some timed arm beats the walk by more than NULL_cell, per layer × regime × filter, with and without the CB class. Also the CONCENTRATION: the share of Σ(walk − best) carried by the top 5%, 10% and 25% of cells, the same for the table's realised saving Σ(walk − pick), and the number of patterns with at least one mover cell | Frank wants to see whether the table's value lives in few cells. A small P-MOVE with a high concentration says the table is worth building for those cells and little else |
| P-PRED | the predictor-training effect: per cell, ns(walk, rep64k) ÷ ns(walk, streamed), the same for each form, and the walk's misses/KiB in both conditions (the perf pass). Plus the count of picks that CHANGE between the repeated and the streamed condition | names what the repeated column measures; says whether a streamed re-fit of the `fit-repeated` rows is due (§2.1 trigger) |
| P-CB | the consumer-bound cells (§2.7): count, share of RT cells per layer × regime × site kind, and the count at tolerances 10% and 35% | makes the class visible instead of hiding it in sums |

### 3.3 Scope statements that are part of the bars

- Replay bars exclude dispatch until [REGIME-TWIN] reads (§1.4). After the twin, G1-G3
  are re-run with its term added. Passing without the twin is a PROVISIONAL PASS, and
  the status line says so.
- R4 and any H-dependent row is NOT gated by replay. It is gated by the twin, by F4
  and F7, and by D165's dense-tiny-match parity gate (regime_tables §5).
- `iter` cells are emulated by the keep hand-edit until D165 builds. S2 and S3 bars on
  emulated cells are reported but do not gate (Q-REVAL-7).
- Answers are not part of acceptance. Every form is answer-identical. Answer identity
  is the correctness gate (§1.2) and a wrong answer EXCLUDES a cell.

### 3.4 Fixing the bars before the reading

- **The pre-registration file.** `docs/design/memfn/regime_eval/prereg.tsv` holds,
  machine-read by the evaluator:
  - every bar and prediction above, with its value;
  - the population rule (§2.6), including the **STREAMED CONDITION**: judge cell is
    (S) 64 distinct 64 KiB buffers, 4 MiB in all, disjoint from the exemplar, or (W)
    a whole subject ≥ 1 MiB; a repeated 64 KiB cell is `rep64k` and never gates; the
    buffer count, buffer size and the minimum total size are values in the file, so a
    drift in the condition is a bars change;
  - the **consumer-bound definition** (§2.7): the three conditions and their constants
    (20% spread, 50 misses/KiB, NULL_cell), the perf event list and the denominator
    forms that gate (WITHOUT the class);
  - the placement rule (§2.5);
  - the frozen pattern list's sha256, the corpus manifest's sha256 and the slice
    offsets;
  - the foreign-class rotation;
  - the E source per filter;
  - the control list with each control's target regimes;
  - the LAUNCHES count;
  - the measurement set id and its sha256;
  - the table listing's sha256 (§5.3).
- **Commit and announce.** It is committed ALONE as `[regime-eval] pre-registration`,
  and its blob sha256 is posted to main in a responses notice before any judge slot is
  requested. Main's journal records it, so the hash lives in two histories.
- **The evaluator's judge mode refuses to run unless all hold:**
  1. `prereg.tsv` at HEAD has the same blob as at the pre-registration commit;
  2. that commit's committer date precedes the judge slot's `SLOT_START` line;
  3. the slot's `arms.tsv` and subject manifest hash to the values the prereg names,
     and every gated group's subject satisfies the streamed condition (buffer count,
     size, total, no buffer shared with the exemplar);
  4. the table listing and the set it reads match the prereg's hashes.
  Any mismatch is a hard refusal that names the field.
- **Changing a bar after a reading** means a NEW pre-registration, a NEW judge
  population (or the old one marked contaminated) and a new slot. Both results are
  reported side by side.
- **Outliers are LISTED, not excused.** Every G3 outlier appears in the results with
  its cell, regime, the row that fired, pick, best, walk and excess. Any note beside
  one is labelled INTERPRETATION (gridread's convention). An outlier is never removed
  from a sum.

## 4. Failing-direction controls

The evaluator must show it FAILS when the table is wrong. Each control mutates the
table or set through the build's own knobs (§5.2), re-runs the replay on the same cells
and timings (no new timing), and must score VISIBLY WORSE.

### 4.1 The controls

| id | control | how expressed | target regimes |
|---|---|---|---|
| C1 | swapped thresholds: SIMD-on g* ↔ SIMD-off g*; and R1/R2's spans ↔ R3's spans | an alternate set file | all |
| C2 | the old R3 short-span error: A3 for H < 32 (no R3a) | set value `h_r3a = 0` | DINGHY |
| C3 | each row deleted, one at a time (R0 … R6) | a row deny (`--memfn=no-<row>`, the kit's own deny carrier) | the regimes the row fires in |
| C4 | R0 removed: V1 on ≥ 2 RANGE terms (C3's R0 instance, named separately because its evidence is the F3 grid) | deny R0 | all (it is P-keyed) |
| C5 | per-site g* replaced by the PF figure (4.5 SIMD-on, 14 SIMD-off for every site kind) | an alternate set file | DINGHY, TUG |
| C6 | the set from the wrong box: Zen 4's set applied to Zen 1's timings, and Zen 1's set applied to Zen 4's | the other box's set file | all (once J4 exists) |
| C7 | A/A: the same arm twice (`walk` vs `walk#b`) | the policy "always walk#b" scored against "always walk" | must read inside the floor |

### 4.2 "Visibly worse", declared now

For a control, consider only the cells whose pick it MOVED. In at least one target
regime:

  Σ_moved (regret_control − regret_table) > max( 2 × Σ_moved NULL_cell , 1.0 point of the regime's summed walk )

NULL_cell is gridread's: max(that cell's A/A floor, 3.09% of its walk). A control that
moves no cell is UNREACHED, never PASS.

**Why "moved cells only".** The prototype's first rule summed the A/A floor over the
whole regime. In TUG that floor is dominated by the walk's bimodality (38 µs of A/A
over 33 groups, gridread §1.1), so it hid a +56 µs control (C5, SIMD-off). Noise only
matters where the pick changed.

Each control reports one of:

- **WORSE**: the evaluator detects this error;
- **NOT-WORSE where reached**: the evaluator cannot tell this table from the true
  one on this population;
- **UNREACHED**.

A NOT-WORSE is a G4 failure for C1, C2, C5 and C6. For C3 a row deletion that is
NOT-WORSE has a different meaning. Either the row is worth nothing on real use (a
candidate for deletion under Frank's "cleaner, clearer design", Q-REVAL-2), or the
population cannot exercise it. The report says which, by the row's reach count. A row
that fires on fewer than 10 RT cells reads as "unexercised", not "worthless".

### 4.3 The A/A control and the noise rule

- **C7.** The A/A control is the replay of a policy against its own repeat launch. It
  must read within the summed NULL. The prototype reads 54.8 µs = 1.25% of the walk
  summed over 132 groups. That is the evaluator's aggregate resolution: a difference
  between two policies below about 1.3% of the walk is noise at the aggregate.
- **Regret is biased upward.** Best = the minimum over noisy arms (the winner's curse).
  The A/A figure states the size of that bias. The gates use raw regret and accept the
  bias rather than zeroing NULL cells, because zeroing biases toward passing.
- **Per-cell verdicts** (WIN, LOSS or NULL against the walk, listed per cell) use
  gridread's rule verbatim: |Δ| ≤ max(A/A, 3.09%), or the paired launch deltas
  disagree in sign.

### 4.4 Reach of the controls ([MECH-REACH])

Every control's report carries the count of moved cells. The prototype shows the
problem on the fit grid: R0 and R1 are UNREACHED (the grid has no ≥2-range-term site
and no one-shot n < 32 call). The WITNESS population (§2.1) exists for these.

Rule: every row has at least one WITNESS cell that the row fires on and where deleting
the row changes the pick. The evaluator checks this with its own pick harness (§5.2)
before any timing, and it fails closed on a row without a witness. WITNESS cells are
timed in the judge slot but reported apart. They gate only G4.

## 5. Independence

### 5.1 Sources, and what each must not share

Everything below follows docs/dev/learnings.md §3 and memory pcrec-check-design-lessons.

| judged thing | judged against | must not share |
|---|---|---|
| the table's pick | the fastest TIMED arm on the cell | the cost model. The best is never `costmodel.py --price` or gridread's fit. The prototype imports grload's loaders and refuses gridread.py, which holds the fit (§8). |
| the thresholds | judge populations the fit never saw | the fit data: thresholds from FIT only; the judge isolation of §2.2; ALPHA/spike non-gating (§2.2 J3) |
| the patterns | a D27-blinded author | the kit's or pcrec's alphabet: the user agent never sees src/, tests/, the bench patterns or the regime documents |
| E (the exemplar gap) | the timed slice | the timed bytes: the exemplar is a different file of the same class. E=oracle is the only exception and never gates. |
| the regime bucket | counted facts from the counting twin | timings and the table's own conditions |
| the population | a completeness sum over five classes | the evaluator's own filter: K35, every pattern listed |
| the evaluator | its failing-direction controls and witnesses | its own success: §4 |

### 5.2 One declared table, read by both

The table the build compiles is the kit's declared row data. D161 add. 11 makes the
kit's copy the source of truth, and regime_tables §0 mirrors it. The evaluator must
judge THAT table, not a transcription.

Design, which adds no parallel mechanism:

- **The pick harness `regime_pick` (kit, tests only).** A small C program linked
  against the kit's own selection function. It reads knowledge records as TSV (one
  per cell × layer × filter, with the filter masking unknown keys) plus a measurement
  set file and an optional deny list (`--memfn=` syntax). It prints the fired row and
  the form per record.
  - Python never evaluates a row condition. It only joins picks to timings and does
    arithmetic.
  - The harness is the same code path the compiler runs at define time for {P, E, A}
    rows.
  - For {N, M, H} rows it calls the same condition function that the emitted dispatch
    is generated from. The kit table's `needs` column decides which (the kit's D161
    add. 11 notice: "one table, two evaluation times").
- **Controls go through the build's knobs only.** A control is an alternate SET FILE
  (D166 already requires sets to be loadable and rollback-able by name) or a ROW DENY
  (every kit row already has its `--memfn=` deny, D147 addendum 9's namespace). No
  control edits the table.
  - C2 (the old R3) is a set value.
  - C3 and C4 are denies.
  - C1, C5 and C6 are set files.
  - If a control cannot be expressed this way, that is a finding against the table's
    declaredness, not a reason for a second table.
- **The table's identity is recorded.** The evaluator records the sha256 of the kit's
  table LISTING ([LIST-TABLES]: `--list-axes`' `memfn` section, or the kit's own table
  dump), as printed by the binary that built the timed artifacts. The same listing
  hash goes into the pre-registration. A results file whose listing hash differs from
  the artifacts' build is refused.
- **Before R17-b′.** The prototype carries the rows in Python (`replay_proto.py`'s
  `ROWS`), labelled as a mirror of regime_tables rev 0.2. That is exactly the parallel
  mechanism the design forbids. It is allowed only in the prototype, and it expires at
  R17-b′'s first commit.
- **Sequencing.** R17-b′'s first commit is the table data plus its pick function at
  ZERO MOVERS: not routed, no emitted byte. It precedes the evaluator's build, so the
  harness links real rows from day one.

### 5.3 What the harness proves about itself

Each check below is built so that it can fail.

- **Agreement.** On every FIT cell, the harness's pick equals the pick the MF_TRACE
  build records when it compiles that cell's pattern with the cell's P/E/A. This covers
  the define-time rows. For run-time rows the trace records the condition the dispatch
  emits.
- **Plant.** A planted off-by-one in a set value (h_r3a + 1) must move picks on the
  WITNESS cells.

## 6. Outputs and where they live

### 6.1 Results files

Results are committed under `docs/design/memfn/regime_eval/results/<run-id>/`, where
`<run-id>` = `<date>-<box>-<set-id>-<listing-sha8>`:

| file | contents |
|---|---|
| `manifest.tsv` | the run's inputs, one per row: the prereg blob sha, the set id and sha, the listing sha, the corpus manifest sha, the pattern list sha, and the sha256 of every slot log read (time_*.log, raw, counts, subj_facts; gridread's SHA256SUMS shape), plus box, gcc, CPU, LAUNCHES and the SLOT_START line. `--check` re-verifies them. |
| `cells.tsv` | one row per (cell, layer, filter), sorted by a stable cell id (pattern id, subject id@sha8, slice, mode, call), with no timestamps in rows. Columns: `cell layer filter class site_kind terms range_terms regime L g pred E_src rows_fired pick best ns_pick ns_best ns_walk regret_ns regret_per_call null_cell aa_floor launches verdict_vs_walk partial outlier subj_cond cb cb_misses_spread mv_best_vs_walk` |
| `population.tsv` | every frozen pattern with its class (REFUSE / NOSITE / OTHER / UNREACHED / RT), reason and site family. The completeness sum is in the header. |
| `summary.txt` | per layer × filter × regime: table regret, every fixed policy, the A/A floor, the gate bars with PASS/FAIL and their inputs, the predictions with CONFIRMED / REFUTED / UNREACHED, the reported quantities P-MOVE / P-PRED / P-CB, the consumer-bound block, every denominator both WITH and WITHOUT the class, the outlier list in full, and the status line (PASS / PROVISIONAL PASS (no twin) / FAIL) |
| `controls.tsv` | one row per (control, layer, filter, regime): moved cells, Δregret, the threshold, the verdict |

Everything is plain sorted TSV with fixed column order, so `diff` across runs,
measurement sets or boxes shows only what moved. A companion
`regime_eval.py --diff RUN_A RUN_B` joins `cells.tsv` on the cell id and prints pick
changes and regret moves. That is the [MEASURE-SET] mover census for a set change
(D166 item 1).

### 6.2 What stays out of the tree

These stay in scratch, uncommitted:

- the slot directory and every raw log (their sha256s are in the manifest);
- the corpus BYTES. Licensing: only ids and sha256s are committed, and the bytes live
  in `worktrees/.corpus/`.

The prototype's outputs are committed because they are small and in-sample, and they
cite their input hashes.

## 7. The plan

| step | what | owner | gates on | slot? |
|---|---|---|---|---|
| E0 | this note → main's comments → D6 panel → revision | kit | — | no |
| E1 | [REGIME-CORPUS] collection report (manifest, PROVENANCE, sha256s) | main | — | no |
| E2 | blinded user-agent lane: questions + patterns per class, frozen list committed | main | E1 | no |
| E3 | R17-b′ first commit: table data + pick function, zero movers (§5.2). It FIRST retires the Python mirror (Q-REVAL-11) | kit | E0 | no |
| E4 | evaluator build: `regime_pick`, `regime_eval.py` (replay, controls, judge gate, `--diff`, `--check`), harness H1 (`lines`) and the streamed-subject generator (§2.4), the consumer-bound classifier and the P-MOVE/P-PRED/P-CB reports (§2.7, §3.2), WITNESS cells. Validated IN-SAMPLE on grid1 (must reproduce the prototype within the same arithmetic, and re-derive §8 without the consumer-bound class) with every control, the agreement check and the plant | kit | E3 | no |
| E5 | pre-registration commit + hash posted to main | kit | E2, E4 | no |
| E6 | site-mapping census (no clock), counting pass, correctness gate on J1 + J2a + WITNESS; population.tsv | kit | E5 | light (no clock; ~15 min, -j) |
| E7 | judge slots J-a1, J-a2, J-b on Zen 4 (J-c optional, ungated, not scheduled), every cell streamed or ≥ 1 MiB, with the perf pass | kit, scheduled by main | E6 | YES: ~80 + ~70 + ~76 min (~226 min; J-c +~140) |
| E8 | replay → results committed → summary to main | kit | E7 | no |
| E9 | D6 panel on the RESULTS (rows, outliers, controls, predictions) | kit launches, main comments | E8 | no |
| E10 | [REGIME-TWIN]: the hand-built table arm timed against fixed forms and the per-row best on FIT + a J-a1 subset; dispatch term as a set value; bars re-run with dispatch | kit | E8 (design with E0) | YES: one grid slot, ~60 min |
| E11 | F5: J4 on ubuntubudu via a bench request through main; the Zen 1 set; C6 | main schedules the bench box | E8 | bench window |
| E12 | R17-b″ evidence: F4/F7 through D165's iterator; S2/S3 bars become gating | kit + pcrec | D165 build | YES |

The [REGIME] umbrella's official verdict (D144 add. 4) remains the bench run on
targeted hardware (J2b). This evaluator is the kit-tier gate before it.

Slots needed, via main: E6 (light), E7 (three), E10 (one), E11 (a bench window).

What [REGIME-TWIN] adds:

- the dispatch term (per row set and site kind);
- the only score for R4;
- code-size movement per artifact (pcrec's observable, `artifact_size_log`), which
  replay cannot see;
- the conversion of PROVISIONAL PASS into PASS.

## 8. The prototype: what the replay already shows (in sample)

`regime_eval/replay_proto.py` on grid1's slot (inputs sha-matched to
`gridread/SHA256SUMS`). It imports grload's loaders only. Its knowledge records come
from planted facts plus the `site(G1)` counters. Its rows are regime_tables rev 0.2
with the kit's rev 0.1 corrections, held in Python as a labelled mirror (§5.2).

| filter, layer | STRICT population (101 groups) | regime_tables §3 claims | PICKABLE population (132 / 109) |
|---|---|---|---|
| S0 SIMD-on | 11.1 / 1.2 / 0.0 | 11.1 / 1.2 / 0.0 | 13.7 / 1.3 / 0.0 |
| S0 SIMD-off | 18.8 / 16.6 / 0.1 | 18.8 / 16.6 / 0.1 | 20.2 / 16.2 / 0.1 |
| S1 SIMD-on | 5.6 / 0.1 / 0.0 | 6.6 / 0.1 / 0.0 | 8.9 / 0.1 / 0.0 |
| S1 SIMD-off | 3.5 / 2.1 / 0.1 | 2.7 / 0.4 / 0.1 | 6.3 / 2.0 / 0.1 |
| S2 SIMD-on (iter) | 6.0 / 1.2 / 0.0 | 5.6 / 1.2 / 0.0 | 4.9 / 1.3 / 0.0 |
| S2 SIMD-off (iter) | 10.5 / 16.6 / 1.0 | — | 8.3 / 16.2 / 0.9 |
| S3 SIMD-on (iter) | 6.0 / 0.1 / 0.0 | 0.5 / 0.1 / 0.1 | 4.9 / 0.1 / 0.0 |
| S3 SIMD-off (iter) | 3.5 / 2.1 / 1.0 | 1.5 / 0.4 / 0.1 | 2.8 / 2.0 / 0.9 |

All values are DINGHY / TUG / LINER regret as % of the walk.

Controls on STRICT (`proto_out_strict.txt`):

- C1 swapped g*: WORSE in all three configurations.
- C5 PF-only g*: WORSE in both.
- C3: deleting R3a or R6 is WORSE; deleting R5 is WORSE at S1 and NOT-WORSE at S3.
  Deleting R2 is NOT-WORSE (|Δ| ≈ 0 on 2-4 moved cells). Deleting R3b is NOT-WORSE,
  and its Δ is negative: −5.2 µs at S2 and −39.9 µs at S3.
- R0 and R1 are UNREACHED.
- C2, the old R3, is NOT-WORSE: −6.0 µs on STRICT; +35.1 µs on PICKABLE, under the
  moved-cell threshold.
- C7 (A/A): 1.25% of the walk.

Findings (MEASURED replay arithmetic over the slot's timings; interpretations labelled):

- **F-1.** The evaluator's arithmetic reproduces regime_tables §3's S0 row exactly on
  gridread's own population. The replay and the source agree where they should, so
  the instrument starts calibrated.
- **F-2.** The S1-SIMD-off, S2-SIMD-on and S3 figures in regime_tables §3 are not what
  the declared ROWS achieve. They are gridread §6.2's model rows ("gap", "hint",
  "gap+span" with oracle facts). The rows regret S3 SIMD-on DINGHY 6.0% against the
  claimed 0.5%. INTERPRETATION: the rows have no DINGHY row for "L ≥ ~16-32 and
  g ≥ ~4 → W=64" (gridread §6.3 D2's amended rule), and R4 is not replayable. This is
  why the evaluator replays rows and never quotes a model.
- **F-3.** S2 SIMD-off regrets 10.5% in DINGHY against always-walk's 2.4%: the table
  loses to a fixed form, a G1 failure. R3b's condition requires SIMD-on, so a span of
  14-32 B with SIMD off falls through to R7's V1. INTERPRETATION: R3 needs a SIMD-off
  arm (WALK, by rule D1) or a statement that S2 is SIMD-on only.
- **F-4.** With no iterator, SIMD-on DINGHY regret (11.1-13.7%) is worse than
  always-walk (7.2-9.1%). This is regime_tables' own note: find-all through `_search`
  makes N the remaining subject, so DINGHY is invisible at call time. G1 is aggregate
  and the table still dominates overall (LINER), which is why G2 caps DINGHY
  separately and loosely.
- **F-5.** The population rule decides C2. STRICT drops the L = 8 groups the kit's
  R3 correction rests on, and C2 there reads −6.0 µs (the old row looks better).
  PICKABLE keeps them and C2 reads +35.1 µs, but under the moved-cell noise threshold.
  The R3 correction is therefore NOT visibly supported by the replay of this grid.
  INTERPRETATION: H here is the per-pass mean activation span, and R3 is a per-step
  row; per-step H needs the iterator (F4) or [REGIME-TWIN].
- **F-6.** R0 and R1 are unreachable on the fit grid (no ≥2-range-term F1 cell; no
  one-shot n < 32 call), hence the WITNESS population (§2.1, §4.4).
- **F-7.** Deleting R3b IMPROVES in-sample regret (−39.9 µs at S3). INTERPRETATION:
  A3 at activation spans 14-32 B loses to R7's A1 on these cells. This conflicts with
  gridread §4.2's L* 14-19 B, which is a per-call-span crossover at fixed g, again
  the per-step vs per-pass H gap.
- **F-8.** The TUG A/A floor (38 µs) is dominated by the walk's bimodality (gridread
  §1.1). A regime-summed noise rule hides real controls there. §4.2's moved-cell rule
  is the fix.

None of these is a judge result. They are statements about the table against its own
fit data, which is the evaluator's first job (E4 must reproduce them). The §8 figures
are `fit-repeated` (§2.1) and WITH the consumer-bound class; E4 re-derives them
without it (§2.7), and they are the like-for-like reference for the `rep64k` column.

**Disposition of regime_tables corrections 1-4** (the kit's notice of 2026-10-14 asked
for them; each below is the finding behind F-2, F-3, F-5/F-7 and F-6):

1. S1-off / S2 / S3 figures are gridread's model rows, not the declared rows: accepted;
   applied by main on its mirror.
2. R3b has no SIMD-off arm (F-3): accepted; applied by main on its mirror.
3. The R3a/R3b split is not supported by the grid's per-pass H (F-5, F-7): accepted;
   applied by main on its mirror (R3a/R3b PROVISIONAL until per-step H exists).
4. R0 and R1 are unreachable on the fit grid (F-6): accepted; applied by main on its
   mirror (the WITNESS cells of §2.1, §4.4 carry the reach).

## 9. Questions — resolved (main, 2026-10-14)

Main accepted all of Q-REVAL-1..11 as recommended, with the riders below.

- **Q-REVAL-1, the bar values (§3.1): RULED, adopt as proposed, with the streamed
  condition.** The values are loose by design. LINER is the only tight cap, and it is
  tight because the default lives there. The bars apply only to STREAMED or ≥ 1 MiB
  cells (§2.4), and G2/G3 gate without the consumer-bound class (§2.7).
- **Q-REVAL-2, may a held-out row deletion argue for removing the row?: RULED yes, but
  a deletion becomes a PROPOSAL to Frank.** When C3 reads NOT-WORSE on the judge
  population AND the row fires on at least 10 RT cells, the report files a per-row
  proposal to Frank under "cleaner design". It is never automatic and never a kit
  decision. On the fit grid this already names R2 (|Δ| ≈ 0) and R3b (negative Δ) for a
  look.
- **Q-REVAL-3, E before [REGIME-LANDINGS]: RULED as recommended, exemplar-bigram,
  labelled, until [REGIME-LANDINGS].** The evaluator derives g from a same-class
  EXEMPLAR through pcrec-analyze's unigram and bigram counts, labelled
  `E=exemplar-bigram(kit)`, and also reports E=oracle. Every figure that uses it carries
  the label until [REGIME-LANDINGS] delivers the analysis object's landings kind.
- **Q-REVAL-4, harness extension H1 (`lines`): RULED as recommended.** A manifest
  generator in the grid1 harness, no driver change. It is the only shape where N at
  call entry is small on real text, so it is the only place R1 and R2 are judged on use.
- **Q-REVAL-5, ALPHA and spike cells (J3): RULED as recommended.** Reported, never
  gating.
- **Q-REVAL-6, J2a: RULED yes, published definitions only.** The bench's published
  patterns and subjects, timed at the kit tier. The evaluator never reads the ledgers,
  and bench-only questions go to main for relay.
- **Q-REVAL-7, emulated iterator cells: RULED as recommended.** S2 and S3 on keep-edit
  cells are reported and do not gate until F4 measures the real iterator.
- **Q-REVAL-8, LAUNCHES for judge slots: RULED as recommended.** 3 for J-a1, J-a2, J-b
  (and J-c if run), with gridread's paired-sign rule; 5 for WITNESS cells. The estimate
  of §2.4 uses 3.
- **Q-REVAL-9, the reporting buckets: RULED as recommended.** costmodel's (64, 18.5) as
  the gated buckets; gridread's W=64 boundaries as an ungated second column.
- **Q-REVAL-10, the measurement set before [MEASURE-SET]: RULED as recommended.** The
  kit writes its set as a TSV in D166's shape (relative to the walk's per-byte cost,
  absolute ns as provenance, id, box, run, method version and, new in rev 1, the
  subject condition per row, §2.1), replaced by pcrec's format when [MEASURE-SET] lands.
- **Q-REVAL-11, order relative to R17-b′: RULED as recommended, with the E3 zero-mover
  table first, which retires the Python mirror.** E3 (the table data plus its pick
  function at zero movers) comes first and retires `replay_proto.py`'s `ROWS` mirror
  (§5.2); then the evaluator (E4), then the judge (E7), then R17-b′'s ROUTING commit
  only after a PASS or PROVISIONAL PASS.

### 9.1 The standing design questions (docs/design/CLAUDE.md)

1. **Measurement regime: RELEVANT.**
   - Every judge timing is Zen 4 7700X, CPU 14, governor `performance`, gcc 15.2
     -O2, kit tier, unofficial (D144 add. 4), under the quiet gate, with `first`,
     find-all, `lines` and emulated-iterator call patterns.
   - Real text differs from the grid in landing predictability, and that moves g*
     2-4× (gridread §5.3). The judge populations exist to see exactly that.
   - The SUBJECT CONDITION flips the walk's cost: 0.4-22 branch misses/KiB on a
     repeated 64 KiB buffer against 150-250 on fresh 1 MiB (F2). That is why every
     judge cell is streamed or ≥ 1 MiB (§2.4), the repeated column is ungated, and the
     F1/F3 constants are labelled `fit-repeated` (§2.1).
   - Equal branch misses across forms mark a consumer-owned cell (§2.7). It is a counted
     class, because it dilutes % denominators without moving regret.
   - Zen 1 (AVX2 as 2×128) is expected to move every W=64 row. J4 and C6 measure it.
   - Dispatch is unmeasured by replay. [REGIME-TWIN] supplies it, and passes before
     it are PROVISIONAL.
   - A different call pattern (an iterator against `_search` find-all) flips DINGHY
     picks. M is a knowledge key, and the emulated cells do not gate.
2. **Independent control: RELEVANT.** §5.1's table:
   - the best comes from timed arms, never the model;
   - thresholds come from FIT only, and the judge is held out and pre-registered;
   - patterns come from a D27-blinded author;
   - E comes from a different file than the timed one;
   - the population is counted to completeness (K35);
   - every control is failing-direction, with witnesses that reach their rows
     ([MECH-REACH]);
   - the table under test is the built table, through its own pick function and
     knobs, with its listing hash recorded;
   - the consumer-bound criterion is measured (perf misses plus the timed spread), with
     chosen constants labelled and the F2 gap that bounds them shown (§2.7).
3. **What moves when the data is regenerated: RELEVANT, NO pcrec byte.**
   - The evaluator is analysis. A new measurement set or a re-fit grid changes picks
     and therefore regret. The results are versioned by (set id, listing sha,
     population sha), and `--diff` is the mover census D166 asks for.
   - Re-fitting a threshold the judge has already read contaminates that judge
     population for that row (§2.2).
   - Changing `prereg.tsv` after a reading invalidates the judge run (§3.4).
   - No abi event, no stamp, no spec hunk: nothing here is caller-observable.
   - The table itself, when routed (R17-b′), is the kit's abi event, not this
     evaluator's.

## 10. Charter vs committed

| charter item | committed |
|---|---|
| 1. Replay inputs (cell; knowledge P/N/M/E/H/A under S0-S3; measured ns of every form, both layers) and output (pick, regret, absolute + relative per regime); sources named; the dispatch gap handed to [REGIME-TWIN] | §1.1-§1.4 |
| 2. FIT/JUDGE split (grid1 F1/F3 + future grids → a D166 set; J1 corpus × blinded, J2 bench via main, J3 ALPHA/spike, J4 Zen 1); held-out timing via grid1 over corpus subjects with cell and slot estimates; regime placement from counted L/g; pattern→site mapping with every non-reaching pattern counted (K35) | §2.1-§2.6 (estimate §2.4; mapping and completeness §2.3) |
| 3. Pre-registered loose acceptance per layer and regime; total-regret caps, outlier rule, dominance over fixed forms; committed and hashed before the run; outliers listed | §3.1-§3.4 |
| 4. Failing-direction controls (swapped thresholds, old R3, each row deleted, R0 removed, per-site g* → PF, wrong-box set), "visibly" defined beforehand; A/A control; the noise rule | §4.1-§4.4; the prototype runs C1-C5 and C7 (§8) |
| 5. Independence (no shared source; fit vs judge; best from timed arms; one declared table read by both, no parallel mechanism) | §5.1-§5.3 |
| 6. Outputs: per-cell table, per-regime and per-filter summaries, control scores; diffable; committed vs scratch | §6.1-§6.2 |
| 7. The plan: run order, gates, slots via main, what the twin adds | §7 |
| 8. Open questions Q-REVAL-n with recommendations + the standing design questions | §9 (now resolved, with rulings), §9.1 |
| Rev 1, item 1: every judge cell streamed or ≥ 1 MiB; repeated 64 KiB only as a labelled UNGATED column naming the predictor-training effect; wall recomputed and fitted (J-c dropped from gating); the condition in §2.4 AND in `prereg.tsv`; populations rule and X2 updated | §2.1, §2.4, §2.6, §3.2 (X2, P-PRED), §3.4 |
| Rev 1, item 2: consumer-bound cells as a COUNTED class with a measured, pre-registered criterion; denominators with and without the class | §2.7, §3.1, §3.4, §6.1 |
| Rev 1, item 3: P-MOVE, the share of RT cells whose best form differs from the walk (non-gating) | §3.2 |
| Rev 1, item 4: Q-REVAL-1..11 resolved with main's rulings and riders | §9 |
| Rev 1, item 5: regime_tables corrections 1-4 noted as accepted and applied by main | §8 |
| Optional cheap prototype on existing data, no new measurement | `regime_eval/replay_proto.py`, `proto_out.txt`, `proto_out_strict.txt` (§8) |
| CLAUDE.md lines | `docs/design/memfn/CLAUDE.md`; `regime_eval/CLAUDE.md` |
| No timing, no make test, nothing under src/, memfn/src/, tests/, lib/ | held: Python reading of finished slot logs only |
