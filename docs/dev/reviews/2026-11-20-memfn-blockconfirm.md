# Critic round memfn-blockconfirm (mode: both) -- DRAFT with PROPOSED dispositions

Coordinator draft, 2026-11-20. The manager rules each disposition.

## Subject (frozen by sha256 2026-11-20T17:11, re-checked at hand-back: HOLDS)
- /var/tmp/pcrec-pcrec/scratch/memfn/blockconfirm/{confirm.py b5ae56e8, synth.py 5613ed65, decision_rule.md 2a8b2911,
  spike708.py af5bda9b, work/check.pass 97431cc9, proto/*}; job fcards/jobs/710-kit-blockconfirm 503c6989 + common.sh 4f4e5a39;
  build tree worktrees/bconf-night @ f8789cd2e (build/pcrec ae446f32, cards.py 05f2ae4d). Full list: .coord/freeze.sha256.
- RULE_SHA d32a1474107714e2 verified: the sha of decision_rule.md's rule block = its header = confirm.py's DECISION_RULE.
- Rulings: decisions.md/plan.md last commit adea38104 at the freeze and at hand-back (no FREEZE DRIFT); main moved to
  d694f57d2 (not in scope).
- FREEZE NOTE: the owner's go and the manager's 2026-11-20 rulings (five arms, cell-by-cell control, inlined-arm verdict)
  have no record outside the denied journal; critics took them from the subject's own header and rule text, and
  cpuquiet/spec.md.
- No timing run directory exists (the rule is still amendable before data).

## Lenses as run
| lens | model | question | why |
|---|---|---|---|
| MEASUREMENT (+ sibling/general-form) | opus | per-arm axes; does Hspk isolate inlining; does the verdict decide "the table holds" and nothing else | launcher lens 1; a comparison with five arms and a post-data table |
| HARNESS FIDELITY (all plants) | opus | timed = gated = keyed = recorded; can check fail on a wrong arm at the timed values | launcher lens 2; timing harness |
| GATES + DECIDE DRILLS | opus | job gates, NOT-RUN/TRUNCATED, quiet-control port; decide on constructed outcomes | launcher lens 3; simulate lens on a verdict table |
All three finished in 5-10 min, all files complete (CRITIC COMPLETE). Verification was done INLINE by the coordinator
(every CONFIRMED finding is a code quote or a critic-recorded repro): quotes checked for GATES-1 (both WAIT_KEYS lines),
GATES-2 (synth rows lack need/voids; synth/decision.*.md header sha 60ca03823c8eeb26), GATES-5 (write_tsv "%.4f"),
MEASUREMENT-1/2 (confirm.py:1155-1170), MEASUREMENT-4 (cards.py:190-194 ALIGN_VARIANTS[v % 2]), FIDELITY-1 (confirm.py:481
unit via S.run_unit/spike708.py:510 name rxs_span_0 vs body_of name rxs_blkspan), FIDELITY-4 (guard only in cmd_build,
written before `return 1`). Plant repros (FIDELITY) were NOT re-run (each ~15 min of compiles); their outputs are in
fidelity/out_*.txt.

## Overall: NOT READY TO TIME
GATES-1 alone stops the night (710 and 712 wait on each other). Beyond it, five answer-level items bias or blind the
verdict and are cheap to fix before data (the rule may still be amended: no run dir exists): MEASUREMENT-1, -5, GATES-7,
GATES-9, FIDELITY-1 (+ FIDELITY-4). Everything else is DOC or PLAN. After the fixes: re-stamp the rule, re-run build (only
if VARIANTS_RE moves) / check / dry, and a short re-check by one critic on the diff.

## Findings (consolidated) with PROPOSED dispositions

### Blocking the run
- **GATES-1** (answer: no run) 710 WAIT_KEYS includes kit-rampchunk; 712 WAIT_KEYS includes kit-blockconfirm -> mutual 75
  until both refuse 77. 710's own header says 712 waits on it. PROPOSED **FIX-NOW**: drop kit-rampchunk from 710's WAIT_KEYS.
- **GATES-9** (answer, SUSPECTED by arithmetic) the boxqueue cap 2*est+1800 = 16,666 s can kill the run before STOP_AT on a
  noisy box (3 pass-A attempts per void repeat + an unbounded control re-time: ~17,100 s worst case); results.tsv is
  written only after the main pass and decision.md after the re-time, so a cap kill leaves NO verdict while the declared
  TRUNCATED path is never reached. PROPOSED **FIX-NOW**: hand measure deadline = min(STOP_AT, start + cap - margin); PLAN:
  write results.tsv incrementally.

### Verdict bias / scope (rule amendments before any timing)
- **MEASUREMENT-1** (answer) LOSSes must repeat on v9-11 to stand; WINs are never re-timed. For a POSITIVE claim every
  layout-luck error moves toward CONFIRMED (blockanalysis shows layout levels ~20-35 %, above the 15 % floor).
  PROPOSED **FIX-NOW**: re-time the S-pick WINs too and count only repeated WINs (est. +~750 s), and print the control's A/A
  false-non-TIE rate (83 identical-walk patterns, MEASUREMENT-3) as the expected false-WIN count.
- **MEASUREMENT-5** (answer) the table was fitted on 708's grid; the OLD class x OLD k cells (116 of the 260 S-pick cells)
  re-time 708's exact subject bytes and code text. If all OLD cells WIN, 15 of 144 NEW cells (10 %) suffice for CONFIRMED.
  The old/new split is report-only. PROPOSED **FIX-NOW**: CONFIRMED requires a WIN majority in the NEW population (or in
  OLD and NEW separately); OLD stays the replication line.
- **MEASUREMENT-2** (answer; argues against the manager's 2026-11-20 cell-by-cell ruling's FORM, not its purpose) the
  control voids TBL symmetrically, so a TBL LOSS in a cell where Hspk WINS (a LOSS a fortiori) leaves the LOSS check; no cap
  on the void share. PROPOSED **FIX-NOW (manager's ruling)**: void only where the control's direction agrees with TBL's,
  or at least list "TBL LOSS in a void cell" beside the verdict and banner a void share above a declared threshold.
- **GATES-7** (design) first match puts INCONCLUSIVE-HARNESS above LOSS, so a repeated TBL LOSS outside S is not the
  verdict when every S-pick cell is void/noise. PROPOSED **FIX-NOW**: LOSS first (it needs no S cell).
- **MEASUREMENT-4** (answer) main variants 6,7,8 = 2 default-align : 1 no-align (v % 2); re-time 9,10,11 = 1 : 2, so a LOSS
  (or control non-TIE) that lives at default alignment, the shipped build, tends not to repeat. PROPOSED **FIX-NOW** if
  the build cost is accepted (re-time variants with the main pass's parity, e.g. 10,11,12: POOL_N 13, ~650 new exes + a
  re-check); otherwise **DOC** the bias beside the verdict.
- **GATES-3** (answer; argues against cpuquiet spec item 2's formula with the spec's own purpose sentence) CPU7_MAX = max(5 %,
  2 x max 1-s busy) has no ceiling: one busy second in the 60-s sample disarms the CPU-7 test for the whole run, unflagged.
  PROPOSED **FIX-NOW (manager's ruling; the spec is shared with 711)**: a fixed ceiling (e.g. 20 %) with refuse-or-banner
  above it, or a quantile instead of the max.
- **MEASUREMENT-7** (doc) CLAIM ("never slower ... wins where the span is busy") says more than the VERDICT decides (no
  REPEATED LOSS among readable cells; WIN majority among busy cells routed to the block form). PROPOSED **FIX-NOW** (text,
  folded into the same amendment).
- **MEASUREMENT-6** (answer-scope) S is call density (708's definition): 33 byte-heavy pick cells (k=1000 hit-dense at 100 %
  of bytes in the span; word16/ident16 miss-heavy) are outside the WIN denominator. PROPOSED **DOC**: CLAIM says S is 708's
  call-density set (keeping 708's S keeps the comparison); report the 33 byte-heavy cells as their own line.
- **GATES-6** (doc) INCONCLUSIVE-HARNESS is the headline for all-noise, truncated-no-S, zero rows. PROPOSED **FIX-NOW**
  (text): the word names the cause (INCONCLUSIVE-NOISE / NOT-RUN when no S-pick cell is HARNESS-void).

### Harness fidelity
- **FIDELITY-1** (answer, latent) the unit test exercises span_fn's SIBLING text (rxs_span_0, standalone TU, no v3
  region), not the timed rxs_blkspan inlined in rxa_search; the whole-search gate cannot reach position k-1 at window sites
  with k >= 256 (near-miss-in stops at k+1 <= 255). Plant tailm1t (timed text only): MISSED 5/5 at hex1000, af500, word256,
  nonl1000, ident500 by every part of check. Today's texts differ only by names, so no present miscompile.
  PROPOSED **FIX-NOW** (small): unit-test the timed TU's own rxs_span, and/or a near-miss staircase (runs of k-1, k) past 255.
- **FIDELITY-4** (answer, fail-safe toward TIE) nothing in check/dry/measure proves the avx2 exe carries the block form;
  the vector-register guard runs only in build, only on v6, and its failure does not block (manifests written first).
  Plant isspk (avx2 key -> Hspk body): passes check 4/4. PROPOSED **FIX-NOW** (trivial): move the guard into check, all
  variants, rc 1.
- **FIDELITY-2** (answer on a later `decide`) profile.json (N/A and S) is outside src_hash; decide reads live profile, live
  TABLE and live rule and never compares the run's recorded rule_sha. Drill: zeroing hex's calls in profile.json keeps dry
  PASS (91 hex cells would go N/A). PROPOSED **FIX-NOW** (small): profile.json into src_hash; measure snapshots profile +
  marker into the run dir; decide refuses on a rule_sha/src_hash mismatch.
- **GATES-5** (answer on `decide`) results.tsv at "%.4f" makes decide's verdict differ from measure's at a floor boundary
  (drill: CONFIRMED in memory, NO LOSS from the TSV). PROPOSED **FIX-NOW** (one format: repr).
- **GATES-2** (maintenance) synth.py crashes on the amended confirm.py (KeyError 'need'); synth/decision.*.md are the
  previous rule's output, so the lane never exercised the amended decide path. The round's 29 drills (gates/d/drill.py)
  did, code == text in 29/29. PROPOSED **FIX-NOW** (small): refresh synth (or adopt the drills) and re-run after the
  amendment above.
- **FIDELITY-3** (answer, low likelihood) the cards' DRIVER answer-checks only the first find-all pass; timed repeats are
  not checked (plant stateful: MISSED 3/3). No real arm has pass-dependent state. PROPOSED **PLAN** (a cards.py change =
  kit event; one compare per 1 MiB pass).

### Information / doc
- **MEASUREMENT-3** (doc) the control is an A/A layout test on the 83 identical-walk patterns and a rewrite-perturbation
  test on the 47 others; in neither does it isolate avx2-loop's own inlining (avx2-loop's walk is a different program).
  Acceptable under the manager's ruling only if rxs_span always_inline + immintrin.h IS the shippable shape (SUSPECTED,
  unchecked). PROPOSED **DOC**: decision.md splits the void count by the two populations and states the premise.
- **GATES-4** (SUSPECTED) the CPU-7 max over 1-s windows is applied to ~0.3-0.6 s repeats with no time scaling (one tick ~2-3
  %), and our own unpinned harness may land on CPU 7. PROPOSED **NOTED**: read voids.tsv's cpu7 distribution after the run;
  fold into GATES-3's fix if the ceiling is set.
- **GATES-8** (doc) a TRUNCATED run ends RED (rc 4 misses the done expect line) yet may headline CONFIRMED; "re-time MISSING"
  vs the rule's "re-time noisy". PROPOSED **DOC** (+ a TRUNCATED expect line for the monitor).
- **MEASUREMENT-8** (doc) walkdiff.md column 3 counts jump-target renumbering, not walk change. PROPOSED **DOC**.
- **MEASUREMENT-9** per-arm axis inventory (reference; a note that the row-2 scan k=24..31 and row-1 window k=16..31 cells
  measure the SSE-16 cascade, not AVX2). PROPOSED **DOC** in decision.md.
- **MEASUREMENT-10** (maintenance/design, family) the CPU-quiet/decide machinery is in three diverging copies (710
  confirm.py, 711 checkorder/spike.py, 712 rampchunk.py; 712's signatures already differ). PROPOSED **PLAN**: one timing-rule
  module that each spike passes arms, comparisons and a declared verdict table to (unlocks: MEASUREMENT-1/2/4 fixed once;
  a standard A/A false-WIN line; a "fitted on" field forcing held-out verdicts). Trigger: the next spike chartered.
- OUT OF LANE, NOTED: the job runs measure under `nice -n 5`, so the timed exes inherit nice 5 on an un-isolated CPU
  (ask whether 708 ran the same way; if not, it is an axis vs 708); a cards.cpython-314.pyc exists in bconf-night's
  memfn/tests/span_forms/__pycache__ (10:05 today, before this round) and the subject dir has its own __pycache__ (15:50).

## PROBED-AND-HELD (summary; full lists in review/*.md)
- Timed exe = checked exe (all 3900, v6-11 incl. the calibration exe); the content key reproduces byte for byte (2/2).
- Manifest identity: arm swap, re-stamped swap and variant swap all refused by dry (4 drills).
- Plants CAUGHT at timed values: avx2drop 5/5, ssedrop 3/3, swarrange 2/2 (random subjects only), tailm1 at k < 256,
  lo1, far, farfp, skiphead, skipmid (13 plant kinds, 60 planted exes in total).
- Gate independence: answers are python re; the unit's reference is the artifact-parsed byte set, asserted = CLASSES.
- Decide: 29 constructed-outcome drills, code verdict = text reading in 29/29 (clean, zero rows, all-noise, all-void, LOSS
  cleared / stands / not-run / noisy re-time, exactly half vs half+1, floor boundaries, N/A cells, TRUNCATED).
- Gates: STOP_AT refusals at --ready, body start, after the quiet wait and in measure; wait keys proceed on none / failed /
  cancelled; dry writes nothing in steady state and refuses every input it claims; the estimate (7,433 s) recomputes from
  708's measured 1.43 s per cell-arm; the quiet-control port matches spec items 1-5 apart from GATES-3/4 and two minor
  divergences (calibration exe = H64@on, per-arm not per-cell void totals in decision.md).
- TBL's TIE-by-construction cells enter neither CONFIRMED's numerator nor its denominator; S admits no idle cell (0 of 260
  below 2 % span bytes); the table reads site + k only.

## By-id completeness
MEASUREMENT-1..10, FIDELITY-1..4, GATES-1..9: every id above has a disposition.

## Which lens caught what
The answer-level items split cleanly by lens, with no overlap: MEASUREMENT found the verdict biases (re-time asymmetry,
fitted population, symmetric void, parity); GATES found the scheduling deadlock, the cap and the unflagged control;
FIDELITY found the gate's k >= 256 tail blindness and the unenforced arm guard. Two OUT-OF-LANE notes crossed lanes
(GATES -> FIDELITY on src_hash's scope, which FIDELITY-2 had already filed; MEASUREMENT -> GATES on noise-before-TIE).

## Lessons for the guide (proposed)
- A positive-claim timing rule must re-time WINs as it re-times LOSSes (asymmetric re-time favours the claim). Candidate
  text for the measurement lens: "for a positive claim, check the re-time is symmetric in direction".
- A queue job's WAIT_KEYS must be checked against every sibling job's WAIT_KEYS for cycles (GATES-1).
- A table derived post-data must be decided on held-out cells (MEASUREMENT-5).

## RULING (kit manager, 2026-11-20 17:30)
Before ruling, the manager CANCELLED 711 and 712 from the queue: their hold would have expired at 20:00 with GATES-3, and for 711 MEASUREMENT-1, unfixed. All three are re-queued after their fixes and a re-check.
- GATES-1: FIX-NOW, done the other way round. 712 drops kit-blockconfirm from its wait keys; 710 keeps waiting on kit-checkorder and kit-rampchunk. Order: 711, 712, 710.
- GATES-3 (spec): FIX-NOW for ALL THREE jobs: cpuquiet/spec.md amendment 2' (cap 20 %, banner). GATES-4 is folded into it.
- MEASUREMENT-1: FIX-NOW in 710: the S-pick WINs are re-timed like LOSSes and count only if repeated; the A/A false-non-TIE line is printed. ALSO in 711, which re-times only LOSSes for its positive claim. 712 re-times neither direction (symmetric), so it needs no change.
- MEASUREMENT-5: FIX-NOW. CONFIRMED needs a WIN majority in the NEW population; OLD is printed as the replication line.
- MEASUREMENT-2: FIX-NOW; this amends the manager's own cell-by-cell ruling in form, not purpose. A TBL reading in the SAME direction as the control's non-TIE is voided (it may be the inlining artifact). A reading OPPOSITE to it stands (a fortiori). The void share is printed, with a banner above 25 %.
- GATES-7, GATES-9, GATES-6, MEASUREMENT-7: FIX-NOW.
- MEASUREMENT-4: FIX-NOW. The build cost is accepted: re-time variants take the main pass's parity.
- FIDELITY-1, FIDELITY-4, FIDELITY-2, GATES-5, GATES-2: FIX-NOW.
- DOC: MEASUREMENT-3, -6, -8, -9; GATES-8, plus a TRUNCATED expect line. NOTED: GATES-4 (folded into 2'). PLAN: FIDELITY-3, MEASUREMENT-10 (one shared timing-rule module; trigger: the next spike).
- OUT OF LANE, nice -n 5: the fix lane checks how 708 ran and matches it; any difference is named as an axis.
- FREEZE NOTE: accepted. The rulings are now recorded here, on the kit branch.
- Lanes: bcfix (opus) takes 710; cofix (sonnet) takes the 711 MEASUREMENT-1 change and the GATES-3 change in 711 and 712, plus 712's GATES-1. Then one critic re-checks all three before re-queueing.
