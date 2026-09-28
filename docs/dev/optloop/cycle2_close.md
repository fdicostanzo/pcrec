# [OPTLOOP.2] — CYCLE 2 CLOSE

Lane `optc2`, 2026-09-28, branch `lane/optc2` from `d604bee9`. Documentation
only: nothing under `src/`, `cli/`, `lib/`, `tests/`; no `make` beyond what
this doc's citations needed to verify (`grep`/`git log` reads only).

**Sources.** `docs/dev/optloop/` (`cycle2_*_reading.md`, `b1ledger/`,
`b2ledger/`, `b108/`, `b108_reading.md` + its two addenda,
`cycle2_admitfix_reading.md`, `cycle2_i103_reading.md`,
`axes_reconciliation_2026-09-23.md`), `docs/dev/summaries/
2026-09-28-b108-exec-summary.md`, `docs/dev/plan.md`'s `[OPTLOOP]` rows,
`docs/dev/decisions.md` D119/D122/D123/D125/D126/D127, `docs/dev/
known_issues.md` K64-K69, and the lane reports cited inline.

Cycle 2 = `[OPTLOOP.2.analysis]`, opened 2026-09-22 evening ("Proceed on
all") as a REPEAT on `capability` at pin `8d716693` (D119 addendum). It
chartered two design notes (`c2design`/`c2prep`) that became four
mechanisms — `[OPT-FREQPICK]`, `[OPT-REQPOS]` tier 2b, `[OPT-PRECHECK-ADMIT]`,
`[OPT-REQRUN-ENC]` — built across what the lane reports call "batch 2" and
"batch 3", plus the residual give-up family (K64/K65/K66) and the deny-bit
mask fix (K68) found while validating them.

## 1. What shipped, per mechanism

### `[OPT-FREQPICK]` — the frequency-informed necessary-byte pick

**Shipped:** `src/opt/reqbyte.c`'s `rb_pick`, argmin over the shipped static
prior `pcrec_byte_freq_ppm` (`src/opt/prefix_k.c`), byte-encoding only;
ties to the rightmost (today's PCRE2-matching rule survives as tiebreak).
Merged `8e4e9c6c` (`lane/optimpl2`, 2026-09-22), `abi` 29 → 30 (one event
shared with `[OPT-REQPOS]` tier 2b below). 475 of 2,814 corpus artifacts
move (69 byte-pick-only, 406 gain a run); `-e utf8` moves 449, all run
gains, zero byte-pick moves (the encoding decline holds).

**Measured against the D119 bar (`cycle2_batch2_reading.md`, O-49 at
`b1885a83`):** target `nested-comment-rec` **MEETS spectacularly** — 9.3 ms
→ 23.1 µs on 4/4 configs, the cost model predicting the absolute after-value
to 0.2%. **One unpriced hazard the design note itself classified as a
gain**: `wild-validator-email-owasp`'s pick moved from `.` (19,436 hits) to
`@` (zero hits) on a one-attempt artifact — a 500× floor-jump regression
`reqbyte_freq_pick.md` §7.1 listed among effects that "are gains", because
the note's acceptance check ("no cell's picked byte goes from absent to
present") has no converse test for the opposite direction.

**Default status: DEFAULT-ON**, ruled 2026-09-25 on the `[B84]` reading
(`cycle2_admitfix_reading.md` §5) once `[OPT-PRECHECK-ADMIT]`'s admission
rule removed the email-owasp hazard by construction (a one-attempt route no
longer emits the pre-check at all).

### `[OPT-REQPOS]` tier 2b — the necessary literal RUN

**Shipped:** a second accumulator on `reqbyte.c`'s walk (`Job.req_run`),
`<PREFIX>_REQ_RUN` stamp, axis bit 31, one emitted scan loop shared by both
engines, `pcrec_sb_cstr` (the emission kit's third vocabulary). Same merge,
`8e4e9c6c`, same `abi` 29 → 30. Tier 2 (the bounded-`dmax` skip loop) was
**DECLINED** — `reqpos_census.md` found it covers only 6-8% of patterns and
two losing cells, and does not clear D77.

**Measured against the D119 bar:** forced-VM targets MEET (`github-pat`
−97.6/−97.9%). **The carve-out clause FAILS**: `router-prefix-order`
(DFA route, large subject) regresses +80.83%, fully counted — the emitted
loop makes one `memchr` **call** per occurrence of its scan byte, not of
the run (315 → 39,098 calls, 124×; the cost model reproduces +322,063 ns at
`c_call` = 7.72 ns). `reqpos_2b.md` §4.3 priced the `memcmp` and was silent
about the `memchr` restarts, which are 97% of the regression.

**Default status: DEFAULT-ON WITH `[OPT-PRECHECK-ADMIT]`'s fix**, ruled
2026-09-25 on the `[B84]` reading. The router/keyword residual (the run
check's own FORM should depend on the picked byte's frequency, not fire
unconditionally) is **explicitly handed to `[OPT-LITSCAN]`** as its
dominated-pre-check elision witness (D122) — see §2 below; it is not this
row's to carry.

### `[OPT-PRECHECK-ADMIT]` — admit and place the pre-checks by cost

**Shipped:** G1 DOMINANCE + G2 ADMISSION as one emit-time predicate
`req_admit` (`src/gen/emit_dfa.c`), `abi` 30 → 31 for the new stamp
`<PREFIX>_REQ_WHY` (emitted/none/one-attempt/dominated — `<PREFIX>_REQ_BYTE`/
`_REQ_RUN` deliberately keep naming the ANALYSIS so `[OPT-FREQPICK]`'s
check surface cannot go vacuous). Merged `6ef76820` (`lane/admitimpl`,
2026-09-23). G3 PLACEMENT (the partial-inlining split hypothesis) was
**DROPPED** 2026-09-23 on O-48: no `.part.0` split exists at either pin on
x86_64/gcc 15.2 (lane `g3rec`, `cycle1_ledger_reading.md` §9) —
`nested-comment-rec`'s earlier +18.8–25.0% regression went unattributed
under this hypothesis and was **fully explained instead by `[OPT-FREQPICK]`**
once it shipped (§9's placement question is therefore moot, not merely
unresolved).

**Three give-ups found and fixed while validating admission — filed as
K64/K65/K66, all FIXED and merged:**
- **K65** (2026-09-25, `lane/k65fix`, folded into `27a63314` with K66): on a
  no-DFA-front VM route, which necessary-set member the pre-check `memchr`'s
  decided NOMATCH-vs-give-up; fixed by testing every set member
  (`emit_req_set_rest`). `abi` 33 → 34, 452/6,642 census movers, S277.
- **K66** (2026-09-25, same merge): K65's fix extended to runs — a run
  longer than its 8-byte window is now also compared whole
  (`emit_req_run_rest`). `abi` 34 → 35, 12/6,642 movers, S278.
- **K64** (2026-09-25, `lane/k64fix`, merged `ce658cb7`): G2 declining the
  pre-check on a step-budgeted, framed, forced-VM one-attempt artifact
  turned NOMATCH into `PCREC_ERR_STEPS` (5/75 bench subjects). Fixed: the
  linearity conjunct in `req_route_one_attempt` narrows to an exact hybrid
  or a frameless program only. `abi` 32 → 33, 176/6,634 census
  artifact-configs move (41 on the AUTO route — backref/linked-call VM
  artifacts with no hybrid to be exact — a population the fix's own author
  found against the brief's prediction).

**Measured against the D119 bar (`cycle2_admitfix_reading.md`, `[B84]`/O-52):**
27 of 29 G2 cells improve, 2 sit in band — MEETS. The one new give-up
(K64, since fixed) was the fix's own defect returning an old outcome, not a
regression of the mechanism itself.

**Default status: DEFAULT-ON**, closed 2026-09-26 (lane `closetails`,
`5803051b`) once K64/K65/K66 were all merged and confirmed ancestors of the
tip.

### `[OPT-REQRUN-ENC]` — the run scan byte's non-byte decline

**Shipped in two stages.** Stage 1 (census, lane `reqrunenc`): under a
non-byte encoding, `rn_scan_index`'s `!bytekey` fallback returned index 0 —
the run's LEFTMOST member, i.e. the UTF-8 lead byte, shared by a whole
script block (`é@` stamped 195, ×39.6 slower than `@é` on é-dense text).
Stage 2 (`lane/reqrunenc2`, merged `43039d4e`, `abi` 37 → 38): the fallback
now returns `r->n - 1` — RIGHTMOST, matching `rb_pick`'s own single-byte
fallback (one rule, not two) — plus a structural codegen check
(`run_prechecks.sh` §4.9) and sabotage S294. **K68**, a second defect found
alongside it (`rx_info.flags` left deny bits 28/29/30 unmasked in
`strategy_denials`), fixed and merged separately (`lane/k68fix`,
`d911def7`, `abi` 38 → 39, S295).

**Validation:** per the manager's morning read of the k68fix chain
(`dev_journal.md`, 2026-09-27 addendum): `make test` green except the
standing darwin `nm arm_a.o` probe, recursion identity 16/0, S295 DETECTED.
**This retires the "Full make test/mech OWED" note still sitting in this
row's own plan.md text** — the validation ran and passed before `d911def7`
merged; the note is stale and is corrected in the STATE update below.

**Default status: DEFAULT-ON** (no deny-axis ruling was needed — the
fallback rule change is a pure correctness/consistency fix, not a
trade-off).

**Not fully closed by this mechanism:** finding F3 (the DFA candidate-start
scan still `memchr`s the UTF-8 lead byte — a THIRD copy of the same
pick-a-byte decision, in the prefilter's own scan-byte selection rather
than the pre-check) is real and unaddressed. It is tracked under
`[OPT-LITSCAN]`, not this row — see §2.

## 2. Residuals

Every open follow-up below is mapped to an EXISTING plan row by grep where
one exists. Two have none; they are listed as PROPOSED ROWS, not filed —
that is the manager's call.

1. **Router/keyword tier-2b dominance and the run-check FORM RULE.**
   `[OPT-REQPOS]`'s own closure text hands this to `[OPT-LITSCAN]` by name
   (D122); `[OPT-LITSCAN]`'s own charter text lists it as one of the row's
   `INPUTS BEFORE DESIGN` and cites the exact witnesses
   (`router-prefix-order`/`keyword-prefix-order`). S1's G1 widening
   (merged `0bb87eda`) already addresses the dominance half; S1's own bench
   findings (O-61, F1) found a NEW regression from the elision itself on
   short non-matching subjects (a per-call constant, +39.6–45.9%), which is
   now `[OPT-LITSCAN]`'s own open tail, not a fresh residual.
   → **Mapped to `[OPT-LITSCAN]`** (open; not closed by this document).

2. **F3 — the DFA prefilter's candidate-start scan still `memchr`s the
   UTF-8 lead byte.** Found by the manager 2026-09-27 while writing I-112's
   predictions; already recorded verbatim inside `[OPT-LITSCAN]`'s own
   plan.md text ("Owner: this row's prefilter selection, under
   `[PATFACTS]`' one-NONE-rule, D126 Q4").
   → **Mapped to `[OPT-LITSCAN]`** (open).

3. **The crossover constant / run-form dominance rule.** `cycle2_i103_reading.md`
   left it NOT ESTABLISHED (two points 0.36 percentage points apart cannot
   solve the two-parameter system) and designed, not built, a synthetic
   `e`/space-run witness to settle it (I-105, drafted). `[OPT-LITSCAN]`'s
   own `INPUTS BEFORE DESIGN` already names `I-105's crossover pair`.
   → **Mapped to `[OPT-LITSCAN]`** (open).

4. **`cycle1_caps_view.md`'s CAPS table was never re-rendered at the
   batch-2 pin under the bench's authoritative I-99/I-100 classification.**
   `[OPTLOOP.2.analysis]`'s own text has carried this as OWED since
   2026-09-23 ("re-rendered by cycle 2's re-rank at the batch-2 pin, both
   views under the frozen table") and it was never done — `nocapsview`
   rendered the NOCAPS half only; `capsview`'s CAPS half still scores
   `rust` as a caps competitor, which I-100 ruling 2 overturned (`rust` is
   a NOCAPS config by its own declared per-call `captures_at` cost).
   `grep -n "capsview\|CAPSVIEW" docs/dev/plan.md` finds no row beyond
   `[OPTLOOP.1.analysis]`'s own completed pointer.
   → **NO EXISTING ROW. Proposed row** (not filed): *re-render
   `cycle1_caps_view.md`'s CAPS table under the frozen I-99/I-100
   classification, at the current pin* — a rendering task over data
   `build_nocaps_view.py`'s sibling script already has the shape for
   (`capsview_data.json`'s own reproduction pieces), not a measurement.

5. **`captures_via_dfa_survey.md` candidate (c)'s M-B match-regime
   measurement is confounded and unfinished.** `onepass_census.md`
   discharged M-A (reach 31.46%/29.41%, clears the ~10% kill threshold);
   M-B (lane `mbread`, reduced from bench O-46) found the match-regime
   capture-cost share at median 32.75% but flagged every match-regime
   subject as a 5-93 byte hand literal, so per-call overhead plausibly
   dominates — "the next measurement is the match arm at LARGER subject
   sizes... before candidate (c) is ranked." `grep -n "captures_via_dfa\|
   candidate (c)" docs/dev/plan.md` finds no dedicated row; the survey and
   census live only in `docs/dev/optloop/`.
   → **NO EXISTING ROW. Proposed row** (not filed): *M-B at realistic
   subject sizes for the 17 capture-forced hybrid patterns — the
   measurement `captures_via_dfa_survey.md` needs to finish ranking the
   one-pass DFA candidate against its two rivals.*

6. **A bench data gap, not a pcrec row:** `date-nested-plus`'s own
   `search_short`/`match` subject lookup returned no row during M-B's
   reduction — flagged back to the bench, not a plan item.

## 3. Lessons

**"Aligned arms agree ≠ alignment is faster."** The `[B108]` O-67 addendum
built `S2a` and `S2a -fno-lit-run` BOTH under `-falign-functions=64
-falign-loops=64` and found the misses (`aws` throughput, `lp-removed`
throughput) fall inside the null band under alignment where they sat
outside it unaligned. That clears `S2a` of causing them — the misses were
PLACEMENT, and forcing a common alignment on both arms removes the
placement lottery from the comparison. **It does not show that alignment
itself makes anything faster in absolute terms** — the twin compared two
ARMS against each other, both aligned, never an aligned arm against an
unaligned one. `[EMIT-ALIGN]`'s own row text states this distinction
explicitly and is the reason the row asks for an absolute
aligned-vs-unaligned reading as its own first step, not a repeat of the
arm-vs-arm comparison.

**"Profile where VM time goes before the next VM optimization"
(the litscan/S2a lesson).** `[OPT-LITSCAN]` S2a's own named "faster"
population (`ctx`, `level-context`, `userpass`, `github-pat`, `slack`) was
chosen by what the emitted PROGRAM contains — a literal run the mechanism
turns into one compare — not by what the bench SUBJECTS actually execute.
`b108_reading.md`'s own surprise: on every one of those cells a prefilter
already answers the call before the VM's literal-run compare ever runs, so
the compare executes at most once per match — the mechanism's real win (the
forced-VM L-sweep, 0.93× → 0.25× as L grows 2→40) never showed on the
population it was measured against. The larger, UNASKED cost the same
reading found — the VM route's whole-window pre-check at ~5.5 ns per
`memchr` pass per `rx_search` call, paid ×2-×9 on dense-match find-all — was
found only because the reading profiled where the calls actually went,
not by inspecting S2a's own instruction count (which shrank 5-35%,
correctly, and shrinking instructions is not the same claim as reducing
wall time on the population that matters). Filed as `[OPT-LITSCAN]` F6.

**O-68/O-69: per-process bimodality was the CPU frequency governor, not
code layout.** The `[B108]` placement twin (O-67) first read as a LAYOUT
question — under alignment, S2a's misses collapsed into the null band —
which chartered `[EMIT-ALIGN]` to ask whether emitting alignment for hot
sites wins broadly. Before that row could open, bench O-68/O-69 (answering
I-116, pcrec-bench `e6dfbf6`) found the SAME bimodal-per-process signature
on `[OPT-HYB-RESEED]`'s own I-114 answer and diagnosed it directly: a
whole process sits in a fast or slow CPU-frequency state at launch,
independent of code; ASLR off does not collapse the split, subject-
alignment offsets show no dose-response, the per-launch clock ratio (1.33
vs 3.32 GHz) equals the measured time ratio exactly, and `taskset` pinning
eliminates it (0/40 slow launches). **`[EMIT-ALIGN]` is filed BOONIES
TIER** ("test when 'all' our optimizations are in") rather than opened now
for exactly this reason — an unpinned harness measuring bimodal launches
would have made a code-layout row chase a governor effect it cannot fix.

## 4. What cycle 3 would need as input

Not chartered here — D125 holds the next cycle; this is an inventory, not a
proposal.

- **`docs/dev/summaries/2026-09-27-utf8-bench-exec-summary.md`** — utf8@0.1
  at `ce658cb7`: 0 wrong answers; 42 win / 5 lose ≤×2 / 22 lose >×2 on
  large-subject throughput, split ATTRIBUTED (10, the UTF-8-lead-byte
  mechanism `[OPT-REQRUN-ENC]` fixes but was measured before) vs
  UNATTRIBUTED (12: caseless, alternation, two assertions, the lookbehind
  trio, `cls-dot-rep`).
- **Bench O-62** — standing `capability` losses at `02902356`
  (`trim-nested-star` ×5,110, `evil-alt-nested` ×138, `aws-access-key-id`
  ×43, …), read against the abi-27-era compiler; needs a re-read at the
  current pin.
- **The I-112 re-measure ([B104]) and `[UTF8-ATTRIB]`'s read** — refresh
  and attribute both of the above; `[UTF8-ATTRIB]` already drafted three
  rows from its own read (`[OPT-HYB-RESEED]`, `[OPT-ENDWIN-ENC]`, plus
  `[OPT-A]`/`[OPT-LITSCAN]` S4 for the caseless/alternation cells), all
  filed and `not-started`.
- **`[OPT-LITSCAN]` itself** — chartered 2026-09-25 explicitly as "the
  cycle-3 run-form row"; S1 and S2a are built and merged, S3-S6 are not.
  Its own open tails (F1 short-subject dominance cost, F2 step-6 extraction
  cost, F3 UTF-8 lead-byte prefilter scan, F4 the 2-byte-memcmp
  slower-path, F5 built — `L>=3` narrowing merged `4666ba54` — F6 the
  dense-match pre-check cost) are ALL still open and are this row's own
  business, not cycle 3's to re-derive.
- **The two proposed residual rows from §2** (the CAPS-view re-render; M-B
  at realistic subject sizes for the one-pass DFA candidate).
- **Cycle 1's own deferred mechanisms, never picked up in any cycle-2
  batch:** `[OPT-FIRSTSET]` (ratified "batch 2 or later"; `firstset_design.md`'s
  own repair — reuse `rx_forward_seed_state` — is designed but unbuilt),
  `[OPT-ATTEMPT-SPLIT]` (ratified "batch 2 or later"; size is the
  row's own stated argument against a default landing), and
  `[OPTLOOP.1.M6]`'s VM per-attempt/per-step cost split (measured by
  `cycle1_profile.md`: a steps-per-attempt effect, not a per-step one —
  the row's own STATE was never flipped to reflect that its measurement
  ran).
- **`[OPT-VMSEED]`, `[OPT-RETRY-REUSE]`, `[OPT-CLOSURE-CTX]`** — all filed,
  `not-started`, explicitly "sequenced after the open queue" (D125); K67
  is the shared witness behind the latter two.
- **K67** (`\p{L}+` under `-e utf8` compile time) — DEFERRED into
  `[CLS-TREE]`, itself a D125 phase-3 (reassess-against-today's-architecture)
  row, not phase-2.

## What this document does NOT do

It does not rule on any of §2's proposed rows or §4's inventory — those are
Frank's/the manager's calls at the D125 phase-4 stock-take. It does not
touch `[OPT-LITSCAN]`, `[OPT-VMSEED]`, `[OPT-RETRY-REUSE]`,
`[OPT-CLOSURE-CTX]`, `[OPT-FIRSTSET]`, `[OPT-ATTEMPT-SPLIT]`,
`[OPTLOOP.1.M6]`, `[OPT-HYB-RESEED]`, or `[OPT-ENDWIN-ENC]` — all open,
listed in the plan.md update below with the reason each stays open.
