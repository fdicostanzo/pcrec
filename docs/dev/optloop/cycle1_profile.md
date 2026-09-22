# [OPTLOOP.1.profile] — the I-85 profile pass read against its own EXPECT lines

Lane `profread`, 2026-09-22, branch `lane/profread` from `main`. Docs-only,
read-only against the tree: nothing under `src/`, `cli/`, `lib/` or
`tests/`. Reads the 12 transcripts in
`docs/dev/optloop/runs/2026-09-22-i85-405668e9/` against the EXPECT lines
in `cycle1_analysis.md` §3, one block at a time. Every number below is
quoted from a transcript file with its line number; the bench executor's
own reading, outbox O-44 in `pcrec-bench/docs/dev/outbox_to_pcrec.md`
(§3209), is used only as a cross-check on transcription — where the two
disagree, the transcript wins and the disagreement is named.

**Provenance note, found while reading the setup log, not asked for.** The
run's own directory name and README cite pin `405668e9` (the
`lane/optrev` merge commit), but `00_setup.log:5,11,13` shows the worktree
built at `69172a00` — one commit LATER, `git log` confirms
(`git merge-base --is-ancestor 405668e9 69172a00` succeeds; the reverse
fails). `git show --stat 69172a00` touches only `docs/dev/dev_journal.md`
and `docs/dev/plan.md` — nothing under `src/`, `cli/`, `lib/` or `tests/` —
so every measurement below is unaffected by the one-commit drift, but the
run's own stated pin is off by one commit from what was actually built.

**Setup (0.1-0.5).** `03_subjects.log:14-16`'s three computed sha256 sums
are byte-for-byte identical to §3's EXPECT block (`cycle1_analysis.md:532-534`)
and to the manifest rows the failed first attempt printed
(`03_subjects.log:10-12`) — 3/3 exact, confirmed independently of O-44's
own claim of the same. `00_setup.log:18`, `make rc=0`. Clock calibration
(`04_clock_driver.log:2-6`) lands at 0.2253-0.2257 GHz across five runs,
no EXPECT stated for this figure (it is a calibration, not a prediction).

---

## M1 — `[OPT-REQBYTE]`

### M1.a — baseline

| quantity | EXPECTED (`cycle1_analysis.md:670-674`) | MEASURED (`10_M1a.log`) | verdict |
|---|---|---|---|
| tag-depth3-bound ns/byte, flat | 3.26 | 7.3078 / 7.3912 / 3.7831 (64k/256k/1m, lines 14-16) | **deviates**: not flat (+124%/+127%/+16% vs 3.26) |
| dup-param-detect ns/byte, flat | 9.74 | 9.7051 / 9.8809 / 9.8336 (lines 17-19) | matches within 1.5%, flat |
| tag-pair-match ns/byte, flat | 3.37 | 3.2378 / 3.2370 / 3.2536 (lines 20-22) | matches within 4% (systematic, low), flat (0.5% spread) |
| username-password-pair ns/byte, flat | 0.93 | 0.9457 / 0.9337 / 0.9338 (lines 23-25) | matches within 1.7%, flat |
| winpath-grok ns/byte, flat | 2.52 | 2.5029 / 2.5184 / 2.5184 (lines 26-28) | matches within 0.7%, flat |
| matches=0 everywhere | yes | matches=0 on all 15 lines (14-28) | matches |

### M1.b — hand-twin

| quantity | EXPECTED (`:686-688`) | MEASURED (`11_M1b.log`) | verdict |
|---|---|---|---|
| tag-depth3-bound floor | ~0.017, "ANY twin that does NOT reach ~0.017 ns/byte refutes the diagnosis" | 0.0374 / 0.0365 / 0.0367 (lines 13-15) | **by the letter of the stated criterion, refutes** (2.2x the target) |
| dup-param-detect floor | ~0.017 | 0.0372 / 0.0365 / 0.0367 (lines 16-18) | same, 2.2x |
| tag-pair-match floor | ~0.017 | 0.0371 / 0.0365 / 0.0367 (lines 19-21) | same, 2.2x |
| username-password-pair floor | ~0.017 | 0.0371 / 0.0367 / 0.0366 (lines 22-24) | same, 2.2x |
| winpath-grok floor | ~0.017 | 0.0368 / 0.0365 / 0.0366 (lines 25-27) | same, 2.2x |
| collapse ratios (stated: 192x/576x/199x/55x/149x) | — | recomputed at 1 MiB (M1.a/M1.b): 103.1x / 267.9x / 88.9x / 25.5x / 68.8x | **deviates ~2x low on all five, uniformly** |
| matches=0 preserved | yes | matches=0 on all 15 lines | matches |

**The floor gap, recomputed, not asserted.** All five twins land in a tight
0.0365-0.0374 ns/byte band (2.4% spread) regardless of pattern or REQ byte
— a pattern-independent floor, exactly the shape the mechanism predicts —
but at ~2.17x the §2.2 floor (~0.0168 ns/byte) rather than at it. The
ratio of predicted to measured collapse (192/103.1=1.86, 576/267.9=2.15,
199/88.9=2.24, 55/25.5=2.16, 149/68.8=2.17) is uniform at ~2.1-2.2x across
all five rows, which is exactly the floor's own 2.17x gap — the whole miss
in every predicted collapse ratio is explained by the floor being 2x high,
not by five independent baseline errors.

**Is the 0.017 a set-grain artefact? No — recomputed both ways.**
`floor-byte`'s own per-1-MiB rate (17,611.4 ns / 1,048,576 B = 0.01680
ns/byte) and its set-grain SUM rate (1,107.8+4,387.1+17,611.4 = 23,106.3 ns
over 65,536+262,144+1,048,576 = 1,376,256 B = 0.01679 ns/byte) agree to
four significant figures. The same recompute on M1.b's own twins agrees
just as tightly (tag-depth3-bound sum: 2.45+9.58+38.49 = 50.52 µs over
1,376,256 B = 0.03671 ns/byte, against its per-1-MiB 0.0367). Set-grain
vs. per-size makes no material difference on either side of the
comparison — the ~2.2x gap is real, not a computation-method artefact. It
most plausibly reflects the twin's raw `memchr()` call at the top of
`rx_search_run` costing more than `floor-byte`'s own engine-native
`RX_DFA_PREFILTER "memchr"` path, but this transcript does not measure
that difference directly and no further diagnosis is drawn.

### M1.c — carve-out

| quantity | EXPECTED (`:696-698`) | MEASURED (`12_M1c.log`) | verdict |
|---|---|---|---|
| twin overhead where the byte is present (bar: <~2%) | within noise | base 3.2516, twin 3.2685 ns/byte (lines 4-5): +0.52% | **matches**, well under the bar |

### VERDICT M1 — PARTIALLY CONFIRMED

Four of five M1.a baseline rows are flat and within a few percent of the
matrix; `tag-depth3-bound` is not flat (R6, below). All five M1.b twins
collapse to a tight, pattern-independent floor and preserve matches=0 —
the mechanism's direction and shape are real — but by the EXPECT block's
own stated refutation clause every twin technically refutes the diagnosis,
since none reaches ~0.017; the entire shortfall traces to one uniform
2.17x floor-level gap rather than to five separate misses. M1.c's
carve-out holds cleanly. **Landing-bar implication**: this is a
single-sample profile, not a repeated-trial sweep, so no median/IQR is
computable here. The direction supports landing (25-268x measured
collapse across the five rows, no carve-out regression), but
`tag-depth3-bound`'s own unstable baseline means that ONE of M1's five
target cells cannot be scored against a stable reference without a
repeated-trial re-measurement first.

---

## M2 — `[OPT-ANCHOR-VM]`

### M2.a — baseline + anchored-DFA control

| quantity | EXPECTED (`:767-771`) | MEASURED (`20_M2a.log`) | verdict |
|---|---|---|---|
| bracket-array-define ns/byte, ~3.5, identical both sizes | ~3.5, flat | 7.7448 (64k) / 3.6029 (1m), lines 19-20 | **deviates**: 1m close (+2.9%), 64k far off (+121%) — NOT identical |
| evil-alt-nested ns/byte, ~4.1, identical both sizes | ~4.1, flat | 3.2536 / 3.1037 (lines 21-22) | undershoots (-20.6%/-24.3%) but IS near-identical between sizes (4.6% apart) |
| trim-nested-star ns/byte, ~3.1, identical both sizes | ~3.1, flat | 2.3538 / 2.3616 (lines 23-24) | undershoots (-24.1%/-23.8%) but near-identical (0.3% apart) |
| ipv4-near-miss (DFA control), ~6 ns TOTAL both sizes | ~6 ns, constant | 30 ns / 30 ns (lines 25-26, `0.000000030 s` both) | constant (matches direction), absolute value 5x the stated ~6 ns |

### M2.b — hand-twin

| quantity | EXPECTED (`:780-783`) | MEASURED (`21_M2b.log`) | verdict |
|---|---|---|---|
| bracket-array-define, constant 30-120 ns both sizes | 30-120 ns | 110 ns both (lines 9-10) | matches |
| evil-alt-nested, constant 30-120 ns both sizes | 30-120 ns | **22,920 ns @64k vs 2,710 ns @1m** (lines 11-12) | **refutes**: not constant, and inverted (smaller subject 8.46x slower) |
| trim-nested-star, constant 30-120 ns both sizes | 30-120 ns | 80 ns both (lines 13-14) | matches |
| matches=0 preserved | yes | matches=0 on all 6 lines | matches |

### M2.c — carve-out

`22_M2c.log:8-10`: the block's own text states the M2 predicate is false
for `nested-comment-rec` (not every alternative is `^`/`\A`/`\G`-anchored),
so no twin was built and the emitted `.c` is unchanged by construction —
the carve-out is satisfied structurally, not by a comparison. The
baseline `nested-comment-rec` reads 5.6795 ns/byte at 1 MiB (line 7),
recorded as a reference figure, not a delta (no edit was made to diff
against).

### VERDICT M2 — PARTIALLY CONFIRMED, with a target-cell anomaly

Two of three M2.a/M2.b witnesses (`bracket-array-define`,
`trim-nested-star`) collapse cleanly to a small constant matching the O(1)
prediction, though M2.a's own baseline undershoots the stated absolute
ns/byte figures by ~20-24% on two of the three (still self-consistent
across sizes). `evil-alt-nested` is the sharpest deviation in the whole
pass: its M2.b twin is neither constant nor even directionally sane — the
smaller subject runs 8.46x SLOWER than the larger one, backwards from any
per-byte cost model. `bracket-array-define`'s M2.a baseline is separately
non-flat (2.15x higher at 64k than at 1m), the same small-subject
inflation pattern seen in M1's `tag-depth3-bound`. **Landing-bar
implication**: `evil-alt-nested` is one of M2's own named rows (at the
shipped default config, §1.1) even though it scores zero in the ranked
table (rescued by `--no-captures`); its twin's anomalous, non-monotone
behavior is exactly the shape the D119 carve-out clause exists to catch,
and it should be re-measured (repeated trials, and checked for a
build/driver defect) before M2 is counted as landing-bar-clean.

---

## M3 — `[OPT-FIRSTSET]`

### M3.a — minimal witness pair

| quantity | EXPECTED (`:866-869`) | MEASURED (`30_M3a.log`) | verdict |
|---|---|---|---|
| `A[A-Z0-9]{16}` stamp + ns/byte | `RX_DFA_PREFILTER "memchr"` | confirmed, line 4; 0.9173 ns/byte, line 5 | matches |
| `\bA[A-Z0-9]{16}` stamp + ns/byte | `RX_DFA_PREFILTER "byte-class-bounded"` | confirmed, line 8; 3.0793 ns/byte, line 9 | matches |
| ratio, "roughly the candidate-density ratio (0.17% vs 77.21%)" | implies a large multiple | 3.0793/0.9173 = **×3.36** | **deviates far below** a density-scaled prediction; NOT refuted by the block's own "same-timing" refutation test (the two are clearly different) |

### M3.b — three real rows, baseline

| pattern | EXPECTED (`:880`) | MEASURED (`31_M3b.log`) | verdict |
|---|---|---|---|
| wild-secrets-aws-access-key-id | 3.83 | 3.0896 (line 3) | -19.3% |
| wild-codegrammar-json-constant | 3.05 | 3.0931 (line 5) | +1.4%, matches |
| wild-waf-crs-942140-dbnames | 2.97 | 3.0767 (line 7) | +3.6%, matches |

### M3.c — hand-twins (table overwrite)

| pattern | table change | EXPECTED (`:887-889`) | MEASURED (`33_M3c.log`) | verdict |
|---|---|---|---|---|
| aws-access-key-id | 63→1 bytes (line 2) | approach pcre2-dfa's 0.20 ns/byte (18.93x scalar gap) | 3.0896 → 0.8522 (line 9): **×3.63** | improves, target NOT reached (0.8522 still 4.26x above 0.20) |
| json-constant | 63→3 bytes (line 3) | approach re2's 1.62 ns/byte | 3.0931 → 3.4064 (line 10): **×1.10 SLOWER** | **refutes**, by the block's own stated criterion ("A twin that is answer-identical but NOT faster refutes M3 for that row") |
| dbnames | 63→14 bytes (line 4) | approach re2's 1.62 ns/byte | 3.0767 → 2.7400 (line 11): ×1.12 | improves marginally, target NOT reached (2.74 still 1.69x above 1.62) |
| matches=0 unchanged, all three | required | matches=0 on lines 9-11 | matches |

### M3.d — disassembly read

| quantity | EXPECTED (`:898-902`) | MEASURED (`34_M3d.log`) | verdict |
|---|---|---|---|
| instruction-stream divergence confined to the skip-loop block | only that block may differ | `diff aws_base.s aws_twin.s` rc=0 (line 5) — **zero** instruction-text difference anywhere, both files 132 lines (lines 2-4) | **exceeds**: stronger than predicted (not merely confined — literally identical) |
| binaries differ only in table content | expected if gcc doesn't fold the 1-element set | binaries differ at byte 865 (line 6); disassembly identical | confirms |

### VERDICT M3 — PARTIALLY CONFIRMED, one target row REFUTED

The minimal witness pair moves in the predicted direction but by a small
fraction (×3.36) of what a density-scaled argument would suggest — the
mechanism is real, weaker than the density heuristic implies. Of the
three real rows carried to M3.c: `aws-access-key-id` improves (×3.63) but
falls well short of the stated pcre2-dfa floor; `dbnames` improves
marginally (×1.12) and also falls well short of its stated re2 target;
`json-constant` gets measurably SLOWER (×1.10), which by M3's own written
refutation clause refutes the mechanism for that row. M3.d's disassembly
read is a clean, unambiguous confirmation that the change is confined to
table content, unrelated to the timing verdict. **Landing-bar
implication**: one of three real-row target cells (`json-constant`)
actively regresses under its own hand-twin with answer identity intact —
exactly the shape the D119 landing bar exists to catch. M3 as scoped by
this witness set does not clear the bar; it would need either a different
table representation or explicit scoping away from mixed/high-natural-
frequency candidate sets like `json-constant`'s (`'t','f','n'`) before
landing.

---

## M4 — `[OPT-ENDWIN]`

### M4.a — baseline

| quantity | EXPECTED (`:961`) | MEASURED (`40_M4a.log`) | verdict / ratio |
|---|---|---|---|
| stamps | scan unanchored / prefilter offset-set-bounded / start reverse-pass | confirmed, lines 3-5 | matches |
| ns @ 64k/256k/1m, matches=0, LINEAR | ~3,500 / ~16,700 / ~89,400 | 12,740 / 51,630 / 234,831 (lines 7-9), matches=0 | LINEAR confirmed; absolute ×3.64 / ×3.09 / ×2.63 above stated figures |
| ns/byte | 0.085 (derived) | 0.1944 / 0.1970 / 0.2240 | consistently 2.3-2.6x above |

### M4.b — hand-twin

| quantity | EXPECTED (`:968`) | MEASURED (`41_M4bc.log`) | verdict |
|---|---|---|---|
| ns, all three sizes, O(1) | ~25-150 ns, identical | **30 / 30 / 30 ns** (lines 5-7, `0.000000030 s` all three) | confirmed, exactly flat |

### M4.c — correctness carve-out

| subject | EXPECTED matches base/twin (`:979`) | MEASURED (`41_M4bc.log:9-16`) | verdict |
|---|---|---|---|
| e1 (`abc`) | 1 / 1 | base 1 (line 9), twin 1 (line 10) | matches |
| e2 (`abc\n`) | 1 / 1 | base 1 (line 11), twin 1 (line 12) | matches |
| e3 (100000 `x` + `abc`) | 1 / 1 | base 1 (line 13), twin 1 (line 14) | matches |
| e4 (`abc` + 100000 `x`) | 0 / 0 | base 0 (line 15), twin 0 (line 16) | matches |

### VERDICT M4 — CONFIRMED for the mechanism's core claim; baseline absolute numbers deviate

The O(1) collapse (M4.b) and full correctness carve-out (M4.c) are clean,
unambiguous confirmations. The M4.a baseline is LINEAR as predicted but
systematically 2.6-3.6x above the stated absolute figures — the same
small-subject-relative-inflation direction seen in M1/M2, though here it
persists at 1 MiB too (unlike those two). This is the SAME box (Ryzen
1600) building the SAME `abc$` pattern this transcript itself compiled, so
it is not a cross-box artefact; no cause is diagnosed here. **Landing-bar
implication**: no carve-out failure. The mechanism's target-cell speedup
(baseline ~89,400-234,831 ns collapsing to a flat 30 ns) is enormous under
either the stated or the measured baseline, so the baseline dispute does
not put M4's landing at risk the way M1's `tag-depth3-bound` or M2's
`evil-alt-nested` do.

---

## M5 — `[OPT-ATTEMPT-SPLIT]`

### M5.a — baseline

| quantity | EXPECTED (`:1047`) | MEASURED (`50_M5a.log`) | verdict |
|---|---|---|---|
| stamps | dfa / scan-attempt / prefilter-none / table-none / edge-none | confirmed, lines 4-8 | matches |
| `start_max` | `= subject_length` | confirmed, line 9 | matches |
| ns/byte, both sizes | 8.83 | 8.7261 (64k) / 8.4218 (1m), lines 12-13 | close (-1.2% / -4.7%), 3.5% spread between sizes |

### M5.b — upper bound (arm deletion)

| quantity | EXPECTED (`:1061`) | MEASURED (`51_M5b_patternedit.log`, `52_M5b.log`) | verdict |
|---|---|---|---|
| arm split | 5→4 top-level arms | confirmed: "5 -> 4 arms, 1460 -> 291 bytes" (`51_M5b_patternedit.log:3`) | matches |
| stamps after split | unanchored/byte-class-bounded/premultiplied/edge-none | confirmed, `52_M5b.log:3-6` | matches |
| ns/byte, at/below re2-longest's 1.62 | ≤1.62 | **2.3961** (`52_M5b.log:9`) | improves hugely (8.4218→2.3961, ×3.51) but MISSES the 1.62 target by 47.9% |
| size, sum of both artifacts | "the other half of the decision" | 388,428 + 148,650 = **537,078 B** (`52_M5b.log:10-12`) | matches the framing exactly |

### VERDICT M5 — PARTIALLY CONFIRMED

M5.a matches the diagnosis closely (stamps, `start_max`, ns/byte within
5%). M5.b's arm-deletion twin shows a large, real speedup (×3.51) that is
NOT refuted by the block's own criterion ("If the split artifact is not
materially faster, ENG_ATTEMPT is not the cost and M5 is refuted") — it
IS materially faster — but the resulting rate (2.40 ns/byte) misses the
specific numeric bar the analysis set (re2-longest's 1.62) by ~48%. The
summed artifact size (537,078 B, +38.3% over the original 388,428 B alone)
is real evidence for the risk the analysis's own Architecture-fit section
named ("a two-machine artifact doubles the table budget"). **Landing-bar
implication**: this is exactly the size-vs-speed tradeoff the analysis
anticipated with "may belong at a `--tune` position rather than the
default" — the upper bound this mechanism can reach on its own witness is
materially better than baseline but not competitive with the named
algorithmic target, at a real size cost.

---

## M6 — the ns/attempt vs. ns/step measurement (no mechanism proposed)

| pattern | wall(base) ns/byte (`60_M6a.log`) | attempts | steps | ns/attempt | ns/step | steps/attempt |
|---|---|---|---|---|---|---|
| nested-comment-rec | 5.676 (line 3) | 1,048,577 | 3,175,731 (`61_M6cnt.log:8`) | 5.68 | 1.87 | 3.03 |
| quoted-delim-match | 5.661 (line 6) | 1,017,656 | 3,315,211 (line 11) | 5.83 | 1.79 | 3.26 |
| balanced-parens-rec | 3.650 (line 9) | 1,005,534 | 2,231,728 (line 14) | 3.81 | 1.72 | 2.22 |

(All from `61_M6cnt.log:17-19`. `nested-comment-rec` finds zero matches
and its attempts count is exactly n+1 (1,048,577 for n=1,048,576); the
other two find real matches — 2,975 and 6,061 respectively
(`60_M6a.log:6,9`) — and find-all's advance-past-a-match reduces their
attempt counts below n+1 correspondingly. This is arithmetic already in
the same log, not a new mechanism.)

**Is ns/attempt ≈ steps/attempt × ns/step?** Yes, to within rounding on
all three (3.03×1.87=5.666 vs stated 5.68; 3.26×1.79=5.835 vs 5.83;
2.22×1.72=3.818 vs 3.81) — but this is an algebraic identity
(`ns/attempt = wall/attempts = (wall/steps)·(steps/attempts) = ns/step ·
steps/attempt`) given the same three measured quantities, not an
independent empirical check.

**Which of the two does the per-byte cost decompose into?** `ns/step` is
nearly uniform across all three patterns (1.87/1.79/1.72 — an 8.7% spread
top to bottom), while `steps/attempt` varies far more (3.03/3.26/2.22 — a
46.8% spread) and `attempts` is pinned close to n by find-all's own
advance rule. The overall ns/byte spread across the three rows (5.68 /
5.83 / 3.81, a ratio of 1.530x top to bottom) tracks the `steps/attempt`
ratio (3.26/2.22 = 1.468) far more closely than the `ns/step` ratio
(1.87/1.72 = 1.087). **M6's bucket is a STEPS-PER-ATTEMPT (per-attempt
work) problem, not a per-STEP dispatch-cost problem** — the per-step cost
is close to constant across these three artifacts' emitted code, and what
differs row to row is how much body work each attempt does before it
fails. No mechanism is proposed here, per the block's own instruction;
this is the fact a future M6 candidate must target.

---

## Known headlines, verified against the transcripts

- **Floor collapse rate ~0.037 vs §2.2's ~0.017.** Confirmed real (M1.b
  table above); confirmed NOT a set-grain artefact by direct recompute —
  `floor-byte`'s own per-1-MiB rate and its set-grain sum rate agree to
  four significant figures (0.01680 vs 0.01679), and the same recompute on
  M1.b's own twins likewise agrees with itself (0.03671 sum-based vs
  0.0367 per-1-MiB for `tag-depth3-bound`). The entire gap in every
  predicted collapse ratio (192x/576x/199x/55x/149x vs measured
  103x/268x/89x/26x/69x) is explained by one uniform ~2.17x floor-level
  gap, not by five independent misses.
- **`tag-depth3-bound`'s baseline is NOT flat across sizes.** 7.3078 /
  7.3912 / 3.7831 ns/byte (64k/256k/1m, `10_M1a.log:14-16`) against a
  stated flat 3.26 — the 1 MiB value is within 16%, the 64k/256k values
  are +124%/+127%. By the bench's own R6 rule (`pcrec-bench/bench/
  capability/NOTES.md:277-284`: "a non-flat throughput sweep, on EVERY
  pattern... read FIRST, for every pattern, as this rule's own positive
  case" for a possible quadratic-backtrack hazard), this is read here
  and tabulated, not diagnosed further.
- **`evil-alt-nested`'s single M2.b attempt is not size-constant.**
  22,920 ns @64k vs 2,710 ns @1m (matches=0 both, `21_M2b.log:11-12`) —
  the smaller subject runs 8.46x SLOWER than the larger one, tabulated
  without explanation per the brief's instruction.
- **M3 splits.** `aws-access-key-id` ×3.63 against the stated 18.93x
  scalar-gap target (reaches 0.8522 ns/byte against a stated 0.20 floor);
  `dbnames` ×1.12 against a stated re2 target of 1.62 (reaches 2.7400);
  `json-constant` ×1.10 SLOWER (3.0931→3.4064), which REFUTES M3 for that
  row by the block's own stated criterion. The minimal witness pair
  (M3.a) reads ×3.36 (0.9173 vs 3.0793 ns/byte). M3.d's disassembly is
  byte-identical instruction text (`diff` rc=0, `34_M3d.log:5`); only
  table content differs (binaries diverge at byte 865, line 6).
- **M4 O(1) at the ~30 ns timer floor.** M4.a's baseline runs ×3.64 /
  ×3.09 / ×2.63 above the matrix's stated absolute ns at 64k/256k/1m
  (12,740/3,500, 51,630/16,700, 234,831/89,400). Separately, M4.b's twin
  and M2.a's DFA control (`ipv4-near-miss`) both bottom out at the
  IDENTICAL 30 ns figure (`41_M4bc.log:5-7`, `20_M2a.log:25-26`) despite
  being different artifacts under different mechanisms — consistent with
  this being this session's shared `findall.c` driver's own per-call
  floor rather than two independently-arrived-at costs. The matrix cited
  in `cycle1_analysis.md` is the bench's own harness; the twin driver
  here is `findall.c` (§0.5) — a different driver, stated plainly, no
  diagnosis drawn between the two.
- **M5's arm deletion.** 2.40 ns/byte (`52_M5b.log:9`) against 8.4218
  baseline (`50_M5a.log:13`) — 2.40/1,048,576-byte-scale collapse of
  ×3.51 — still above re2-longest's 1.62 by 47.9%. Summed artifact size
  537,078 B (`52_M5b.log:10-12`).
- **M6's ns/attempt vs. ns/step.** 5.68/5.83/3.81 ns/attempt vs.
  1.87/1.79/1.72 ns/step, 3.03/3.26/2.22 steps/attempt
  (`61_M6cnt.log:17-19`). Plainly: the per-byte cost spread across these
  three artifacts decomposes into `steps/attempt`, not `ns/step` — see
  the M6 section above for the ratio comparison that decides it.

---

## The executor's five logged mechanical deviations

Per the README and O-44 (`pcrec-bench/docs/dev/outbox_to_pcrec.md:3211-3216`):

1. **Worktree `--detach` substitution** (`00_setup.log:6-11`): `main` was
   already checked out in the primary clone, so the executor retried with
   `--detach` at the same commit. Does not affect any reading — same
   commit either way (modulo the one-commit provenance drift noted above,
   which is docs-only).
2. **Repo-root-on-`sys.path` retry for `captext`** (`03_subjects.log:1-13`):
   the bench's own subject generator needed its sibling package on the
   path. Does not affect any reading — the retry succeeded with
   byte-identical sha256 sums against the EXPECT block.
3. **M4.b's clamp placement** (before `size_t scan_position = search_from;`
   rather than "before the scan loop" as stated): the O-44 text
   (`outbox_to_pcrec.md:3213-3215`) explains the literal instruction would
   have been inert at the stated spot. Affects M4.b's reading only in
   that the exact insertion line is not the one §3 describes verbatim —
   but the measured result (a flat 30 ns, matches=0 preserved) is exactly
   what M4.b's EXPECT block asked for, so this deviation does not change
   the verdict.
4. **One (b)2 rerun** after a display-pipe truncation on the first
   attempt (noted in `70_b2_p2info46.log:1`). Does not affect any
   reading — only one completed run's output exists and is read below.
5. **The p2info bitmap-dump extension** for M3.c
   (`32_p2info_ext.log:2`): M3.c's own block asks for exactly this
   extension ("docs/dev/optloop/p2info.c, extended to dump FIRSTBITMAP").
   Not a deviation from what was asked, and does not affect the reading.

None of the five changes any verdict above; three (1, 2, 4) are pure
process retries with identical end results, and the other two (3, 5) are
the executor doing precisely what the ambiguous or explicit instruction
in §3 required.

---

## The two (b) reads

**(b)1 — evil-alt-nested's "wrong" verdicts vs. dropped expectations.**
Not separately transcribed as its own log file in this run's 12 (it is a
report-side finding, not a Linux command); the executor's own account
(O-44, `outbox_to_pcrec.md:3242-3249`) states the 10 "wrong" trials sit
exactly on `rd-evil-alt-near-miss` (5) and `sd-empty-alt-hit` (5), the two
triples `bench/capability/NOTES.md` records as DROPPED when the oracle
gave up, and `expectations.tsv` carries NO row for either pairing — so the
"wrong" label is emitted for a cell with no derived expectation behind
it, not a genuine oracle disagreement. This rests on no derived
expectation at all, and the bench has opened it as **KB-27**
(`pcrec-bench/docs/dev/known_issues.md:1270`, OPEN, investigation owed on
their side) rather than closing it as a pcrec finding.

**(b)2 — p2info at 10.46 vs 10.48 columns.** `70_b2_p2info46.log` runs
p2info against libpcre2-8-0 10.46-1build1 (line 2) on all 64 patterns,
all `OK` (lines 3-66). `71_b2_diff.log` compares these 10.46 outputs
against `cycle1_rows.tsv`'s 10.48-derived columns: 23 "hard" DIFFs, 0
"soft" (line 27). The reading note the executor appended
(`71_b2_diff.log:29-36`) accounts for all 23: two are this comparison's
OWN char-quoting (`0x93`/`0x94` and a backslash — the raw 10.46 lines
attached show agreement on the underlying fact), and the other 20 are all
on the `.anchored` column, which the note states directly has **no
counterpart in p2info.c's own print** (`firstcodetype`/`firstcodeunit`/
`lastcodetype`/`lastcodeunit`/`minlength`/`bitmapbits` only) — so the
comparison script's own `firstcodetype==2` stand-in is not `pcrec`'s
actual source for that column, and this is not a 10.46-vs-10.48
divergence in anything p2info.c measures. **On the facts p2info.c
actually prints, 10.46 and 10.48 agree for all 63 shared patterns; the
set difference is one pattern (`negation-scope-lookbehind-var`) present
in the 10.46 run but absent from the tsv's 63.** No divergence found.

---

## Closing table

| mechanism | verdict | batch-1 fitness (recommendation only — manager/Frank decide) |
|---|---|---|
| M1 `[OPT-REQBYTE]` | PARTIALLY CONFIRMED — direction/shape real, magnitude off by a uniform ~2.2x floor gap; one target row (`tag-depth3-bound`) has an unstable baseline | Fit for a batch AFTER a repeated-trial re-measurement of `tag-depth3-bound`'s baseline and a resolved read of the 0.017-vs-0.037 floor discrepancy; the carve-out and four of five collapses are otherwise clean |
| M2 `[OPT-ANCHOR-VM]` | PARTIALLY CONFIRMED — two of three witnesses clean, `evil-alt-nested` anomalous (non-constant, inverted with subject size) | NOT yet fit — `evil-alt-nested`'s anomaly needs a design revisit (repeated trials at minimum; possibly a build/driver defect) before this mechanism's own named row set is trusted |
| M3 `[OPT-FIRSTSET]` | PARTIALLY CONFIRMED, one target row (`json-constant`) REFUTED by its own stated criterion | NOT yet fit as scoped — needs either a different table representation or explicit scoping away from mixed/high-frequency candidate sets before a design note is written |
| M4 `[OPT-ENDWIN]` | CONFIRMED for the core O(1)/correctness claim; baseline absolute numbers run high but do not threaten the landing bar | Fit for a batch — the enormous target-cell speedup is robust to the baseline dispute, and all four correctness carve-outs hold |
| M5 `[OPT-ATTEMPT-SPLIT]` | PARTIALLY CONFIRMED — large real speedup, misses its stated numeric target, real size cost measured | Fit only for a `--tune`-position design, not a default landing, per the analysis's own anticipated tradeoff — needs the design pass to weigh the measured +38.3% size cost |
| M6 (no mechanism) | Measurement only — decides the bucket is a steps/attempt (per-attempt work) problem, not a per-step (dispatch) problem | Not a batch candidate yet; the measurement narrows what a future M6 mechanism proposal must target |
