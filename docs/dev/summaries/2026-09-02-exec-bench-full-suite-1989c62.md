# Executive summary: pcrec-bench full-suite night, pin 1989c62

Overnight window 2026-09-01 22:45 to 2026-09-02 10:48 EDT (the two
window-script-capped clang cells re-run by hand to 10:48). Four sets
measured at pcrec pin `1989c62` (abi 15): `bounded@0.3` (first sample,
the [OPT-5] STEP 2 BEFORE), `loglines@0.1` and `email-specimen@0.2`
(after), `altwide@0.1` (first sample), plus the cc axis's first
production firing (gcc vs clang) on bounded and loglines. Baselines
differ by set (bounded/altwide against a7e0bdf, loglines against
263b013/96e44c2, email against 96e44c2) and are named per finding
below. 29 of 29 scheduled cells landed at attempt 1; two bounded clang
cells were killed by the window script's 3000 s cap and re-run by hand
the same morning, counted as first-class, no second-tier flag. Store
grew to 111 records. Source: pcrec-bench's ledger
`docs/dev/ledgers/2026-09-02-full-suite-1989c62.md` (1,136 lines),
confirmed by their outbox message O-14, which existed at the time of
this summary and reads as a faithful compression of the ledger with no
disagreement found between the two.

## 1. Findings

- **The [OPT-5] STEP 2 BEFORE is now pinned, not scratch.** The
  search-filter entry form costs ×1.985 the unwrapped rate on matching
  calls and ×37.1 on failing anchored calls, confirming O-13's
  scratch-tier reading (1.97-2.04, ×37.4) within 3% (ledger §3.2,
  §8.1).
- **The night's one unpredicted finding: the forced-VM route got
  ~×9 faster on `resume_frames == 1` artifacts, gcc-only.** `floor` on
  `t-letters-064k` went 174,404.8 to 19,382.5 ns/call (2.661 to 0.296
  ns/B); the population is exactly pure-VM artifacts with one resume
  frame, a −402 B split with no exception in 118 shared artifacts
  (ledger §2.2-§2.3).
- **The frameless win has a cost.** On the same population, an
  empty-match-and-advance loop (`[a-z]{0,n}` on digits) got ×1.07-1.09
  SLOWER; failing scans and whole-subject matches got faster (ledger
  §2.6).
- **loglines carries one exact regression family.** Three patterns
  that stamp a non-`none` `dfa_scan_edge` are slower (`iso-ts`
  ×1.06/×1.09, `http-5xx` ×1.03/×1.04, `ipv6` ×1.03); every pattern
  that stamps `none` is flat at a +234 B constant (ledger §7.2).
- **The scan-edge boundary is a spelling, not a count.** `\d{2}` takes
  the edge and `\d{1,2}` declines it on the plain form; the whole
  fixed family declines it at every k on the whole-subject form. On
  the match axis the edge is worth ≤ 0.2 ns at every k from 2 to 32
  while costing +2,037 B (ledger §4.1-§4.4).
- **`auto` picks the slower engine on the bounded match axis at every
  rung from 1024 up.** The forced VM does the 1,024 B whole-subject
  match in 633 ns; the selected DFA takes 1,906 ns unwrapped (×3.01)
  or 3,785 ns search-filter (×5.98) (ledger §3.3).
- **The clang refusal set is EMPTY.** The a7e0bdf-era 50/264 clang
  refusals are gone at 1989c62 on both measured sets, all three arms;
  the prediction held (ledger §5.1).
- **altwide's DFA refusal cost is severe.** 12 of 20 patterns are
  refused on every pcrec config (26 auto refusals at the 1,000,000 B
  source cap, 24 VM refusals at the 500,000 B code cap); the DFA route
  pays 8.7-36.0 s per refusal against the VM route's 0.01-0.07 s
  (ledger §6.1-§6.3).
- **`pcrec-auto` is flat under width growth where every other testee
  is not.** Over `w-8`/`w-64`/`w-256`, `auto` runs 2.24 to 3.43 to
  2.93 ms while pcre2-interp and pcre2-jit rise ×74-90×; at `w-256`
  `auto` is ×83.2 faster than jit and ×797 faster than the
  interpreter (ledger §6.4).
- **`level-context` is flat across the pin** (faster ×1.01) but stays
  ×3.68 behind pcre2-jit on throughput and ×2.91 on search; it is the
  corpus's only collapsed-prefilter VM hybrid (ledger §7.3).
- **The [OPT-5] search-band bonus persists** on 7 of 11 loglines
  patterns, unchanged (within spread) or faster; only the four
  edge-taking patterns moved (ledger §7.3).

## 2. Surprises

- **The biggest performance movement of the pin came from a
  portability fix, not a performance change.** The ×9 forced-VM win
  traces to [CC-CLANG] step 1's `has_push` gate, which omits the
  computed-goto resume dispatcher on frameless bodies; nobody measured
  it for speed, and the clang toolchain that forced the gate to exist
  does not reap the benefit (clang is ×2.00 SLOWER on the same cell,
  ledger §2.4-§2.5, I-31's mechanism).
- **P3 was refuted in both directions.** At the same class-run length
  k, the fixed and bounded spellings carry different scan-edge values,
  and the direction flips by entry form: `\d{2}` takes the edge on
  plain while `\d{1,2}` declines it, but on the whole-subject form the
  entire fixed family declines while the bounded family takes it
  (ledger §4.2).
- **The re-pin size census's "+202/+105 B flat" sentence was a
  summary error**, not a measurement error: its own 22 rows already
  split into three buckets (+202 DFA-carrying, +105 pure-VM frames≥2,
  −402 pure-VM frames==1) and the summary sentence collapsed them into
  one (ledger §2.3).
- **`cls-atleast-4096` turned out to be an accidental third case and
  its own control.** It is the only bounded whole-subject DFA artifact
  that stamps both `search-filter` and `edge=range`, yet it never
  doubles in cost because it can never match this set's subjects, so
  every cell is a failing scan (ledger §3.4).
- **`auto` selecting the slower engine at rungs ≥ 1024 is new
  information this window produced**, not a known gap being
  re-measured: even after STEP 2 removes the ×2 penalty, the unwrapped
  DFA stays ×3 behind the forced VM on this regime (ledger §3.3,
  §8 candidate 4).
- **Two altwide predictions inverted.** P5 predicted a size cap only
  on the VM route; the DFA route refuses MORE patterns, at a LOWER
  width, for a different reason. P8 predicted `RX_DFA_SCAN_EDGE = none`
  except possibly on `cnt-64`; it reads `range` on every compiled
  altwide DFA artifact except `floor`, including `cnt-64` (ledger
  §6.2).

## 3. Impact

What was scratch-tier is now pinned. The STEP 2 BEFORE numbers that
governed last session's design-note revision were `inconclusive-load`
smoke readings; they now stand on a quiet-box, five-trial, `agree`
record and reproduced within 3%. The frameless-VM shape, previously
invisible, is now sized and its mechanism traced to source
(`emit_vm.c:9482-9560`) rather than only observed externally.

Priorities move. The bench's ranked candidate list (ledger §8) keeps
[OPT-5] STEP 2's two-pass elision at #1, but adds the frameless-VM
shape as a NEW #2 worth up to ×9 and currently unowned by any charter.
The scan-edge entry cost drops from a sizing question to a candidate
with a measured population and no measured win anywhere in the window
(re-scoped, was #2). A NEW #4 asks whether `auto`'s engine selection
should change on the bounded match axis at high rungs, independent of
STEP 2. The DFA route's late size check is a NEW #5, chartered by
altwide's 8.7-36 s refusal cost.

What is fragile: the ×9 win is a gcc heuristic (whole-function
optimization once a computed goto is removed), not a code-size or
instruction-count effect, and it belongs to nobody's charter. If a
future compiler change or gcc version stops performing that
optimization, the win disappears silently, since no charter or test
currently pins it as a deliberate property.

What the bench instrument itself proved: all three control arms
(interp, jit, `pcrec-auto`) stayed flat to four significant figures
across a 1.55× change in iteration count, which is what let the ×9 be
attributed to the code rather than the measurement. The pre-flight
gate widened its observed quiet band from 5.21% to 7.41% with no
refusal, trial agreement held `agree` on all 30 records (8 disagreeing
rows of 59,076 judged, 0 disagreeing groups), and one genuine
interference event (a 91.63% other-core spike during one bounded clang
cell) was caught, recorded, and shown not to have corrupted that
record's trial agreement (ledger §1.2-§1.4, §2.2).

## 4. Next steps

**(a) The bench's seven asks (ledger §9), answer owed in I-32:**

- (i) Is the frameless-VM ×9 intended to stay, or an unowned side
  effect a later change could silently take back? Does
  `resume_frames == 1` match `has_push == false` exactly? Is
  gcc-only expected? Answered by: pcrec manager, Frank ruling.
- (ii) Carry the size-book correction (−402/+105/+202 B by frame
  count and DFA presence) into both projects' documents. Answered by:
  pcrec manager (already corrected on pcrec's side per the journal,
  confirm to the bench).
- (iii) Is `cls-atleast-4096`'s `search-filter` entry form
  deliberate? It is the natural control for the STEP 2 AFTER. Answered
  by: pcrec manager.
- (iv) The scan-edge boundary keys on spelling and form, not a count.
  What does the decision key on, and is there a cell expected to win
  that the bench should measure? Answered by: pcrec manager.
- (v) `level-context` is the one corpus pattern clang builds
  1.4-1.7× slower; worth a look at that code shape. Answered by: a
  measurement lane.
- (vi) The DFA route's late size check costs 36 s to learn a pattern
  is too big against the VM route's 0.02 s. Answered by: pcrec
  manager, a measurement lane (candidate 5).
- (vii) `pfx3-512` (pcre2-jit ×147 over the interpreter) is refused by
  pcrec's source cap on every config; build altwide@0.2 around it?
  Answered by: Frank ruling (scope decision).

**(b) pcrec's own queue, as the journal states it:**

- [OPT-5] STEP 2 implementation waits for Frank's go; rev 2 of the
  design note is merged (66da68c) and verified.
- [OPT-VEDGE]'s first measurement (opt5d §7 item 3's one-command
  measurement) is not yet started.
- The frameless-VM shape question is a candidate row, not yet
  chartered: does it extend to frames ≥ 2, and should a gcc-only win
  be pinned deliberately.
- The DFA late-size-check candidate (ledger §8 #5) has no owner yet.
- Frank's open rulings, unchanged since the journal's last note: the
  o42 witness-gap (deferred to a future session), K43/K44 fix
  directions (unruled), and the reflection-surface note.
