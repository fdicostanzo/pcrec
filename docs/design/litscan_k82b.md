# K82 cause (B): an expected-cost admission for the run pre-check, as `[FINDINGS.B4]`'s first reader

**Status: PROPOSED (design only, lane `k82cost`, 2026-10-04, from main
`940fa06e`).** Nothing under `src/`, `tests/` or `docs/spec/` moves here.
Frank's ruling (`known_issues.md` K82, "PLAN RULED"): cause (B) gets no
compile-time cutoff (the 16-bit `run-common` row of
`../dev/lanes/k82diag_report.md` §4.2 was declined as a knob). Instead, the
admission is an EXPECTED-COST COMPARISON of the candidate guards. The RATES
come from the analysis bundle, and the COST TERMS are measured machine
quantities. Lane `k82fix` builds causes (A) and (C) in parallel. This note
assumes its rows exist: `set-leads` and PICK's NONE argmin, as in the
`lane/k82fix` worktree's `req_admits[]`.

Instruments and transcripts: `../dev/optloop/s4/k82cost/` (its own
`CLAUDE.md`). Linux numbers are r1alpha's (`../dev/lanes/r1read_report.md`
§3) and k82diag's. Mac numbers are DIRECTIONAL (D144 addendum 1).

## 0. Findings first

1. **The rule is right when the rates are right.** The model in §1 uses the
   bench subject itself as the exemplar (the oracle arm). With those rates
   it makes the correct call on every K82 cell. It declines the run block on
   `mod-i`, `mod-r`, `cls-fold-pair`, `cls-pair-ctl` and `ci-strasse`. It
   moves `userpass` to the byte guard, which is twin T1. It keeps
   `union-select`, `ci-ascii-ctl` and `slack`. It also gets the measured
   deltas to within about 2x (§2.3).
2. **With NO exemplar it declines none of the five cause-(B) movers.** This
   is the bench's case: it compiles with no `--analysis`. With no bigram
   block, run-rarity's NONE answer is cardinality (findb4 §2.3), and every
   three-letter caseless run then scores 21 bits. On the syntax subject,
   `(?i)cat` actually occurs once per 164 B, which is 7.4 bits. The no-data
   estimate is off by a factor of about 12,000, and no rate-free rule can
   see that. That is the density residual, stated in §3.
3. **The subject length W is decisive, and the declined 16-bit knee was W
   in disguise.** A pre-check that DISCARDS its candidate pays only by
   rejecting, so whether it pays depends on `x = ρ·W`, the expected number
   of run occurrences in the span one call scans. Under the `log` bundle,
   `mod-i`'s gate pays for any W from 9 B to 11 KiB and loses above that.
   At a log line (127-232 B) every gate in the table pays. At the bench's
   64 KiB-1 MiB find-all, the dense-run gates lose. "16 bits" is
   `log2(64 KiB)`. It was a statement about the bench's subject size.
4. **The cure that removes W is an emission, not an admission.** Twin T3
   hands the gate's candidate to the engine as its scan start instead of
   discarding it. On the Mac it recovers the cause-(B) regressions:

   | cell | NEW (C3) | T3 | DENY (abi 58) |
   |---|---|---|---|
   | `mod-i` | 1.39 | 0.81 | 0.76 |
   | `cls-fold-pair` | 0.99 | 0.55 | 0.55 |
   | `ci-strasse` | 0.65 | **0.49** (beats DENY) | 0.53 |
   | `ci-ascii-ctl` (a customer) | 0.209 | 0.208 (the win is kept) | 0.521 |

   No exemplar is needed and W plays no part (§5 Q1). This is the "masked
   run term in the prefilter" step that litscan_s4.md §2.3.5 already named
   as "the cure, not a second admission rule".
5. **The cost terms are not knobs, but one of them is weak.**
   - Scaling all four terms by 2x, or by 0.5x, changes 0 of the 44
     (cell, rate source) verdicts.
   - The Mac and Linux cost rows give identical verdicts on all 44.
   - The decision reads RATIOS of measured quantities. The weak term is E,
     the engine's own cost per byte. It varies by scan form and by pattern,
     and it has no calibration yet. Mixed 2x errors flip 2-6 of the 44
     verdicts, almost all on cells where the gate is worth at most 0.1 ns/B
     either way. It takes a 4x adverse error in the gate/engine ratio to
     lose a customer (§1.4).
6. **Only the run block is ever declined, and only against its fallback.**
   The fallback is the set pick's byte check, or nothing, which is the
   pre-C3 program.
   - A byte-only pre-check is not this row's question. Under the builtin
     prior the model would decline every byte guard whose byte is common,
     and that is exactly the "required byte absent" insurance whose loss
     gave cycle 1 its ×256 floor-entry cells.
   - A route whose pre-check is the no-match proof is excluded by
     construction: a VM with no DFA in front (K65/K66, findings design
     §6.2a).

## 1. The cost model

### 1.1 What a discard gate costs and saves

Each emitted run pre-check is `if (rx_reqrun(s, n, pos) >= n) return 0;`.
The candidate it finds is thrown away (k82diag §1.B). So a call over a span
of W bytes pays the gate's own scan, and then, if the gate passed, the
engine's scan over the same bytes. The gate saves the engine's scan only
when it REJECTS. Model the run's occurrences as Poisson with rate ρ per
position. For a guard G, the expected cost per subject relative to no gate
is

```
Δ_G(W) = k_G·f + (k_G·β + σ_G·s)·(1 − e^{−ρ_G·W})/ρ_G + over_G  −  E·W·e^{−ρ_G·W}
         \_entry_/ \_______________gate's scan to first hit______/   \__rescan saved on reject__/
```

| symbol | meaning | from |
|---|---|---|
| `ρ_G` | occurrences per position of what G proves necessary: the run's markov1 rarity, `2^-rarity`; for a byte guard, the byte's rate | **the bundle** (run-rarity, byte-rate) |
| `σ_G` | the guard's STOP rate: the summed rate of its scan stream(s) | **the bundle** (byte-rate over the PICKed scan member's cube) |
| `k_G` | the number of `memchr` streams: 1 for an exact scan member, 2 for the pair arm | the fact (`REQ_RUN`'s mask at `@idx`) |
| `f` | ns per `memchr` call entry | **measured** (§1.3) |
| `β` | ns per byte `memchr` reads | **measured** |
| `s` | ns per stop: the re-search entry plus the masked compare that fails | **measured** |
| `E` | ns/B of the engine that runs when the gate passes (or when there is no gate) | **per scan form**, §1.3 (the weak term) |
| `over_G` | the pair arm's overshoot: each stream re-searches fresh per call and reads about `1/σ_j` past the candidate (k82diag §1.B's 4.8x) | derived from `σ_j`, `β` |
| `W`, `M` | the call span and the matches in it | **the workload**, §3 |

- **The byte-then-run guard.** This is k82fix's `set-leads`. It rejects if
  either is absent, and it pays the byte's pass plus, if the byte is
  present, the run block.
- **Find-all with M matches.** Every call but the last passes, so the gate
  reads the whole subject once and pays the entry plus the overshoot per
  call. `M = 0` is the gate's BEST case, and `M > 0` only adds passing
  calls.
- **Reading the formula.**
  - A guard pays on a window of W: `W_lo < W < W_hi`.
  - **`W_lo ≈ k·f/E`** is the short-call entry term. It comes out at 9-22 B
    on the cells, which matches union-srch's measured 6-10 B break-even
    (k82diag §2).
  - **`W_hi`** is set by `x = ρW`. Once the run is expected to be present,
    the gate stops rejecting and its scan is pure added cost.

### 1.2 The admission is an argmin over the candidate guards

The candidates are the four the ruling names:
- none;
- the set pick's one-byte check;
- the run block;
- byte-then-run.

Each is restricted to what the fact offers (no byte guard when `req_set` is
empty). The row emits the argmin of `Δ_G`. On a tie it keeps the shape the
structural rows chose, so a tie never moves an artifact ([r3 F4]'s rule: a
data tie lands where NONE would). §4.2 places it as one first-match row.

### 1.3 Where each cost term comes from

| term | Mac M1, gcc-16, libSystem | Linux ubuntubudu, gcc 15.2, glibc | how measured |
|---|---|---|---|
| `f` | 3.7 ns | 3.4 ns | Mac: `memchr_cal.c` (a hit at distance 0). Linux: k82diag §2, two fresh `memchr` on a 6-11 B subject = 6.8 ns |
| `β` | 0.020 ns/B | 0.020 assumed (**OWED**) | Mac: `memchr_cal.c`'s slope over distances 64 B .. 64 KiB (`memchr_cal.mac.out`) |
| `s` | 7.5 ns | 8.0 ns | Mac: `memchr_cal.c`'s stop loop at spacing 8-128 B. Linux: k82diag §1.B, "8-11 ns per scan hit" on the throughput cells. The short-call +4.4 ns is a warm-cache low |
| `E` | per cell, the DENY ns/B | per cell, r1read §3's base column | **no calibration exists**: see below |

**The proposed provenance is reference-box constants, not a build-time
calibration** (§5 Q4).
- A build-time probe would make the emitted program depend on the machine
  that ran `make`. Today the identity holds across boxes: [XARCH] measured
  0 `size_bytes` movers over 2,925 rows on two machines.
- The precedent is [CLS-TREE] S0: per-probe costs fitted on ubuntubudu,
  committed with their provenance and the probe that regenerates them, and
  re-proposed after recalibration as one ruled diff (D103).
- The rows go in `limits.def` as integers in picoseconds: `f` 3400 ps, `β`
  20 ps/B, `s` 8000 ps, and `E_form` one row per scan form. Each row's
  `desc` names the box, libc, gcc, date and probe (D141's interim rule).
  This needs a new unit token, `ps`/`ps/B`, beside S4's `bits`.

**E is the weak term, and the note does not pretend otherwise.**
- The cell values used here are the measured DENY arms. A real build cannot
  measure E per artifact.
- The proposal is one calibrated row per scan form:
  - **DFA forms.** A table-walk form (`byte-class`, measured 0.68-0.96
    ns/B Linux) and the `memchr`-family forms (`memchr`, `offset-set`,
    `*-bounded`, `run-pinned`) are priced by THIS SAME MODEL over the
    prefilter's own scan byte. That is `[OPT-FIRSTSET]`'s identity,
    `(L·b + w·a + c)/(L + w)` (`../dev/optloop/firstset_design.md`), which
    predicted its skipped fraction to 0.03%.
  - **The VM hybrid's** E is its DFA prefilter's E, because the VM runs
    only on candidates.
- Its spread is real: `byte-class` ranges 0.68-0.96 ns/B across four cells.
  §1.4 bounds what that spread can move.

**Why this is not a knob (D77 / D119).** A knob is a value chosen so that a
measured cell comes out a desired way. These terms are different:
- Each one is a physical quantity that a pattern-blind, bench-blind probe
  regenerates.
- The decision depends only on their ratios (§1.4: uniform scaling moves
  nothing).
- Every rate comes from data.

The remaining guesses are named in §3: W, M, and E's per-pattern spread.
None of them is hidden in a threshold.

**The arithmetic must be integer and bit-exact.** The rarity is already
Q16 (`L(x)`, findb4 §2.2). The decision needs `e^{−x}`, which should be an
integer `exp2` DEFINED BY ITS ALGORITHM, with test vectors, in the same way
`L(x)` is defined.
- Each side of the comparison is evaluated in the log domain, and only the
  sign is read.
- Where `x > 64` the rejection term is exactly 0 by definition.

### 1.4 Robustness: what the cost terms can and cannot flip

This uses `k82b_sens.py` over the 11 cells × 4 rate sources at W = 64 KiB,
M = 0, giving 44 verdicts. Its transcript is `sens.out`.

| perturbation | verdicts flipped |
|---|---|
| all of `f`, `s`, `β`, E ×2, or all ×0.5 | **0 / 44** |
| Mac cost row instead of Linux | **0 / 44** |
| mixed moves (one of `s`, `β` up and the other down, E either way) | 2-6: `http-5xx`, `stack-frame` and `alt-shared`, plus `slack` (null stakes, −0.003 measured) under two sources and `cls-*`/`ci-strasse` under one, both of those moving toward the decline the subject's own rates call for |
| the gate/E ratio moved 4x FAVOURABLY (`s`, `β` ×0.5, E ×2) | 6, all on cells with \|Δ\| ≤ 0.1 ns/B (`http-5xx`, `stack-frame`, `alt-shared`) |
| the gate/E ratio moved 4x ADVERSELY (`s`, `β` ×2, E ×0.5) | 12, including `union-select` |
| `f` alone ×0.5 or ×2 | 0. At 64 KiB the entry term is negligible; it governs `W_lo` only |

So the cost terms must be right to within about 2x on the RATIO of gate
cost to engine cost. That is a calibration standard the probe meets on both
boxes. A 4x error in E is what it would take to lose a customer.

## 2. Prediction on the K82 cells and C3's customers

### 2.1 The rates

Run rarity is markov1 bits per window, as emitted. The scan member is
re-PICKed under each source's byte-rate. The verdict is at W = 64 KiB, M = 0,
Linux cost row. It reads the same at M = occurrences on every row.

| cell | NONE (no exemplar) | `weblog` | `log` | subject = exemplar | on the subject | Linux measured Δ (NEW − BASE) |
|---|---|---|---|---|---|---|
| `mod-i` / `mod-r` | 21.0 → **run** | 13.5 → **none** | 12.2 → **none** | 9.4 → **none** | 7.4 (400 occ) | +0.59..+0.70 |
| `cls-fold-pair` | 23.0 → run | 13.6 → **none** | 12.2 → **none** | 9.4 → **none** | 7.4 | +0.32..+0.41 |
| `cls-pair-ctl` | 23.0 → run | 13.8 → **none** | 13.1 → **none** | 9.8 → **none** | 7.4 | +0.32..+0.41 |
| `ci-strasse` | 21.0 → run | 17.2 → run | 22.3 → run | 13.5 → **none** | 11.0 (32 occ) | +0.08..+0.10 |
| `userpass` (cause A) | 28.0 → run | 17.6 → run | 18.9 → **byte** | 12.0 → **byte** | 8.3 (212 occ, 0 `=`) | +0.92..+0.95 |
| `alt-shared` (C cured) | 31.0 → run | 42.9 → **byte** | 42.9 → **byte** | 14.9 → **none** | 10.9 | (cause C) |
| **`union-select`** | 42.0 → run | 23.6 → run | 29.5 → run | 27.1 → run | absent | **−0.40..−0.52** |
| **`ci-ascii-ctl`** | 21.0 → run | 23.1 → run | 28.3 → run | 17.8 → run | absent | **−0.45..−0.50** |
| **`slack`** | 57.0 → run | 32.7 → run | 50.4 → run | 52.7 → run | absent | −0.0025..−0.0044 |
| **`http-5xx`** | 63.0 → **none** | 21.8 → **none** | 69.9 → **byte** | 56.1 → **none** | absent | −0.0005..−0.0013 |
| `stack-frame` (control) | 24.0 → **none** | 15.1 → **none** | 13.4 → **byte** | 13.6 → **none** | absent | k82diag: deleting the gate WINS, 0.347 → 0.252 |

Transcripts: `model_linux.out`, `model_mac.out`.

**Answer to the brief's question:**
- **With the shipped bundles at buffer scale**, the rule declines
  `mod-i`/`mod-r`/`cls-*` and keeps every customer. `ci-strasse` stays a
  mover under both, because a log exemplar says nothing about German UTF-8
  text.
- **With no exemplar** it declines none of the movers and keeps every
  customer. Today's C3 program is unchanged on all of them.
- **`http-5xx` is declined (or moved to its byte) under every source.**
  The model predicts +0.002..+0.04 ns/B for keeping its gate, against a
  measured −0.001. These are null stakes in either direction, and the
  engine already rejects by `memchr` (`memchr-bounded`, E ≈ 0.02 ns/B).
  This is a customer mover the build's manifest must name.

### 2.2 W decides. The windows on which the run block pays

The run block pays only for subject lengths inside the window
`W_lo..W_hi` (M = 0, Linux):

| cell | NONE | `weblog` | `log` | subject = exemplar |
|---|---|---|---|---|
| `mod-i` | 9 B .. 4 MiB | 11 B .. 26 KiB | 9 B .. 11 KiB | 13 B .. 1 KiB |
| `cls-fold-pair` | 9 B .. 16 MiB | 9 B .. 22 KiB | 22 B .. 8 KiB | 11 B .. 861 B |
| `ci-strasse` | 13 B .. 5 MiB | 16 B .. 304 KiB | 16 B .. 9 MiB | 19 B .. 19 KiB |
| `union-select` | 13 B .. ∞ | 16 B .. 22 MiB | 13 B .. ∞ | 16 B .. 256 MiB |
| `ci-ascii-ctl` | 13 B .. 5 MiB | 13 B .. 22 MiB | 13 B .. ∞ | 13 B .. 724 KiB |

- **On a line-at-a-time workload every one of these gates pays.** The
  `weblog` line is 232 B and the `log` line is 127 B (`N / count(0x0A)` of
  each bundle).
- **The bench calls find-all over 64 KiB-1 MiB buffers.** There, the
  dense-run gates lose.
- So K82(B) is a WORKLOAD mismatch for a discard gate, not a mis-ranking of
  runs. Line-at-a-time and buffer find-all want opposite verdicts on the
  same artifact.

### 2.3 The model against the measurement (subject rates, M = occurrences, Linux)

| cell | model Δ ns/B | measured | | cell | model | measured |
|---|---|---|---|---|---|---|
| `mod-i` | +0.42 | +0.65 | | `union-select` | −0.54 | −0.50 |
| `cls-*` | +0.30 | +0.37 | | `ci-ascii-ctl` | −0.45 | −0.50 |
| `ci-strasse` | +0.26 | +0.09 | | `slack` | −0.11 | −0.003 |
| `userpass` byte vs run | −1.26 | −0.93 (BASE ≈ T1) | | `http-5xx` | +0.002 | −0.001 |

The model gets the sign right on all 8 rows and the magnitude to within
about 2.5x. The worst miss is `slack`'s win: there the engine's own
`offset-set` prefilter already rejects, so E over-states what the gate
saves. That is the E term again.

### 2.4 The bench census: what the row moves

`k82b_census.py` runs over the 345 bench exports. It counts the run-bearing
emitted pre-checks on proof-free routes: 57 of them, 36 in a byte
encoding. It computes `E*`, the engine cost above which the run beats its
fallback, and applies an illustrative `E_form` row.

| rates | W | byte-encoding declines |
|---|---|---|
| builtin (no exemplar) | 232 B | 2: `cls-n-uc`, `stack-frame` |
| builtin | 64 KiB | 6: + `cls-v`, `mod-s`, `lkb-neg`, `lkb-pos` |
| builtin | 1 MiB | 10: + `comment-obfuscation`, `kv-quoted`, `qnt-plus-ctl`, `qnt-poss-plus` |
| `log` | 232 B | 8, all to the byte fallback (the set pick is unseen in the exemplar) |
| `log` | 64 KiB | 18, the cause-(B) movers among them |
| `weblog` | 64 KiB | 16 |

- **Under the builtin prior, every decline is an EXACT run with a common
  scan byte.** It is driven by σ (the byte-rate, which IS served under
  `-e byte`), not by run-rarity.
- **`stack-frame` is the one measured member, and its decline is a WIN**
  (k82diag §4.2).
- `cls-v`/`mod-s`/`lkb-*` sit at `E* = 0.245` against an illustrative
  `E_form` of 0.24. That is the E term's sensitivity, by name.
- The corpus census is OWED to the build lane, with these instruments.

## 3. No exemplar, and where density still enters

**With no exemplar** (the shipped default, and every bench compile):
- byte-rate is the builtin prior under `-e byte`, and NONE under `-e utf8`;
- run-rarity is NONE, which is markov1 over the all-zero table, which is
  cardinality.

The row then sees runs only through their popcount. It declines a run only
when its scan stream alone costs more than the engine saves. That is the
six exact runs of §2.4. None of the K82 movers is among them.

**Where density enters, plainly:**

1. **The run's rate on the deployment's text (ρ).** This is the dominant
   residual. The exemplar's ρ is a stand-in for the subject's. A synthetic
   text that holds `cat` every 164 B looks like no prior anyone ships.
   - Under NONE the shortfall is 2^13.6.
   - Under `weblog` it is 2^6.
   - Only an exemplar of the deployment's own text closes it (§2.1's
     oracle column).
   - `ci-strasse` is the clean witness: it is present in German UTF-8
     text, absent from every shipped bundle, and identical in shape to
     `ci-ascii-ctl` under NONE. That last point is k82diag §4.4's result,
     now restated with rates.
2. **The call span (W).** The rate side gives `x = ρW`, and W is not in
   any bundle. It is how the matcher is CALLED, not what the text holds.
   This is the term the 16-bit knee was hiding (§0 item 3). §5 Q2 puts its
   source to Frank.
3. **Match density (M).** M is one-sided: `M > 0` only adds passing calls,
   so a row priced at `M = 0` never declines a gate that pays on a no-match
   workload. Moving M from 0 to the occurrence count flipped 0 of the 44
   verdicts. It is a second-order term.
4. **E's per-pattern spread** (§1.3). It flips only cells worth ≤
   0.1 ns/B.

**The irreducible guess is W.** The emission in §5 Q1 removes it from
every run at a bounded offset from the match start. That covers all five
cause-(B) movers.

## 4. The landing shape

### 4.1 What of `lane/findb4` lands as-is, and what changes

`lane/findb4` is 9 commits on `ed51481b` (2026-09-28). Main has moved a
week since, through S4 C1-C3 and [FIND-TIE]'s successors.

| part | disposition |
|---|---|
| the `bigram` kind (schema row, parser, chain copy, `findgen.c`, dump, `rows_digest`) | **as-is**, rebased |
| `L(x)`, markov1, `pcrec_find_run_model*`, `pcrec_find_run_rarity`, the NONE answer inside the primitive (cardinality), the run digest | **as-is**. NONE stays cardinality (§5 Q5) |
| the shipped `weblog`/`log` bigram blocks, `PROVENANCE`, `generate.py`, `make gen-findings` | **as-is**; regenerate after the rebase |
| §13 tests (L(x) vectors, the python markov1, RUNEST acceptance, WAF sign), the rxtsource refusals | **as-is** |
| S330/S331 | **renumber**: main's highest is S456 |
| its three pre-existing reds (`w-c2a` `@3`→`@7`, `w-c4`, the limits manifest count) | **re-check at the rebase**: they were [FIND-TIE]/B5 pins and are probably re-pinned on main already |
| findings design §13 `[B4]`, §6.2's C-rows | **changes**: the first reader is the admission row (call it **C12**, `req_admit`'s cost row), not C6. C6 (the necessary-run ranking by popcount, litscan_s4 §2.3.1) stays a natural second reader. Its trigger is a measured run mis-rank, for example waf_attribution §5 Q2's `from`/`union` hazard (D77) |
| the `run-rarity` stamp item | **now renders**: every artifact whose compile reaches C12's predicate gains `run-rarity=none` (or `=<bundle>:<digest>`) in `<P>_FINDINGS`. That is a STAMP-ONLY mover population of every run-bearing artifact on a proof-free route, and the identity census must name it |

### 4.2 The row, in k82fix's `req_admits[]`

| # | row | deny | predicate | verdict / emitted | `REQ_WHY` |
|---|---|---|---|---|---|
| 1 | `none` | — | no byte and no run | nothing | `none` |
| 2 | `one-attempt` | — | G2 | nothing | `one-attempt` |
| 3 | `dominated` | — | G1 | nothing | `dominated` |
| **4** | **`run-cost`** (NEW) | **`-fno-req-run-cost`** | a run shipped, AND the route has a linear machine in front (`pcrec_artifact_has_dfa_scan`, G1's own premise; a no-DFA VM route is never asked), AND the argmin of §1.2 over {the run-bearing guard rows 5-6 would emit, the fallback} is the FALLBACK | the fallback: the set pick's one-byte check (the pre-C3 program), or nothing when the set is empty | `emitted`, or **`cost`** (NEW token) when nothing is emitted |
| 5 | `set-leads` | `-fno-req-set-lead` | k82fix (A) | byte, then run | `emitted` |
| 6 | `emitted` | — | always | run (or byte) | `emitted` |

- **Row 4 prices the shape rows 5-6 would emit.** It calls
  `req_set_leads_applies` to know whether that is byte-then-run, so it does
  not restate (A).
- **(A) stays a structural row and is not replaced.** Under the builtin
  prior, the cost model alone does not reproduce T1 on `userpass`, which
  §2.1 shows as run/run. The prior says `=` is present in 64 KiB, so it
  prices the byte's insurance at 0. The text has none. "The rarer guard
  leads" is the minimax form of that insurance. A guard's extra cost is
  bounded by one partial pass, and its upside on an absent byte is ~57x
  (§5 Q6).
- **Ordering.** Row 4 sits after G1, which is a free identity elision, and
  before the shapes, because a declined run has no shape.
- **Ties keep rows 5-6** (§1.2).
- **The deny restores k82fix's program exactly.** The axis bit is the next
  free one at landing.

**The §6.2a row (written first, R2).** C12 chooses whether the run block or
its fallback is emitted. It cannot move an answer or a give-up:
- Its predicate requires G1's premise, a DFA or VM-hybrid scan in front.
  There every pre-check either is a check that does not run, or is a proof
  of absence in one pass.
- The fallback byte is a member of the necessary set.
- On a VM route with no DFA scan, the pre-check is K65/K66's no-match
  proof, and the predicate is false by construction.

The premise the build must keep is the route conjunct.

### 4.3 abi, spec, sabotage

- **abi.** This is an abi event: k82fix's number + 1, readers found by grep
  (D76/D94). On the movers it changes:
  - the program text;
  - `REQ_WHY` (the new token `cost`);
  - the `<P>_FINDINGS` stamp's `run-rarity` item on every asked artifact.

  Under no exemplar at W = 232 B, the program movers on the bench are 2.
- **Spec (D80).**
  - `findings.md` §4: run-rarity's reader. §6.2/§6.2a: the C12 rows. The
    `exp2` algorithm and its vectors.
  - `tuning.md` §2.29 and `match_api.md` §6.3: `REQ_WHY`'s closed set gains
    `cost`, and the "`none` iff" invariant is unchanged.
  - `limits.md` §3: the `ps`/`ps/B` units and the cost rows.
  - `cli.md`/`registry.md`: `-fno-req-run-cost`.
  - The W source (§5 Q2), wherever it is ruled to live.
- **Sabotage** (numbered at landing, above S456):
  - (i) **Drop the route conjunct.** The detector is the K66 witness on its
    VM route under `fire-C12`, the adversarial bundle that makes every run
    maximally common. The give-up appears.
  - (ii) **The pair arm priced as one stream** (`k_G = 1`). The detector is
    the manifest: `cls-fold-pair`, whose scan is one stream, against
    `mod-i`, whose scan is two.
  - (iii) **The rejection term's sign** (`e^{+x}`). The detector is the
    census manifest, which declines the customers.

  `fire-C12`'s GIVEUP1 must be 0 (findings design §11.1).
- **Owed to the build lane:**
  - the corpus + bench mover manifests under builtin, `weblog` and `log`;
  - the identity census of the stamp-only movers;
  - Linux alpha cells for the movers, plus `stack-frame` and `userpass`
    under `--analysis log` as the reader's own R38 cells (they move at
    W = record, §2.4);
  - `memchr_cal.c` run on ubuntubudu (the Linux `β`).

## 5. Open questions for Frank, each with a recommendation

**Q1. Build the HANDOFF as K82(B)'s cure?** That is the gate's candidate
becoming the engine's scan start, for a run at a bounded offset from the
match start.
- §2-§3 show that the cost row, under the bench's own compile (no
  exemplar), declines none of the five movers.
- T3 recovers them with no rates and no W:

  | cell | NEW | T3 | DENY |
  |---|---|---|---|
  | `mod-i` 64 KiB / 1 MiB | 1.39 / 1.70 | 0.81 / 1.00 | 0.76 / 0.86 |
  | `cls-fold-pair` | 0.99 / 1.38 | 0.55 / 0.81 | 0.55 / 0.80 |
  | `ci-strasse` | 0.65 / 0.81 | **0.49 / 0.61** | 0.53 / 0.64 |
  | `ci-ascii-ctl` (customer) | 0.209 / 0.342 | **0.208 / 0.341** (the win is kept) | 0.521 / 0.638 |

  These are Mac numbers (`t3_mac.out`). Match counts are equal in every
  arm. The full startpos differential is owed.
- `mod-i`'s residual +0.05..+0.18 over DENY is the pair arm's fresh
  per-call overshoot, which T3 does not touch.
- **What the handoff is.** It is litscan_s4 §2.3.5's "masked run term in
  the prefilter (offset-preference step)", a `dfa_pfs[]` row with
  `pf_emit_ofs_reseed`'s context seed.
- **Where it is unsound.** It is not valid where the offset is unbounded.
  `union-select`'s `.*?` puts `SELECT` at an unbounded offset, so its T3
  would miss matches. There the discard gate is the only form, and that
  customer's run is rare at every W up to 22 MiB (§2.2).

**Recommendation: yes, as its own row, with the full panel (S4 already
says so).** With it, the cost row prices the handoff gate W-free (it pays
iff its per-byte cost is below E), and W survives only for unbounded-offset
runs.

**Q2. Where does W come from?** The options:
- (a) a declared `span` row in the analysis, which the analyzer writes when
  told the record separator;
- (b) the bundle's own record length, `N / count(0x0A)`: 232 B for
  `weblog`, 127 B for `log`, ~100 B for the builtin at its 1.0% newline
  rate. This is data, not a constant;
- (c) a stated workload default (64 KiB) in `limits.def`. **That is the
  declined knob in workload units.**

**Recommendation: (b) now, with (a) as the override when a deployment
measures a need (D77). Not (c).**
- (b) errs toward keeping gates. A gate's downside is bounded by its
  per-byte cost (≤ 0.65 ns/B measured), while its upside on an absent run
  reaches 57x.
- With Q1 built, W reaches no measured cell.
- Under (b) the row moves 2 bench programs with no exemplar (§2.4),
  including `stack-frame`'s measured win.
- **The cost of (b): it does not fix K82(B) on the bench by itself.** That
  is Q1's job, and the reason Q1 comes first.

**Q3. E per scan form.**
**Recommendation:** one calibrated row per `dfa_pfs[]` form, measured by
one probe per form on ubuntubudu, in [CLS-TREE] S0's shape:
- table-walk forms get a ns/B row;
- `memchr`-family forms are priced by this same model over their own scan
  byte (§1.3);
- the VM hybrid takes its prefilter's E.

Until that probe exists, the row should not land: E is the term that can
flip a customer (§1.4).

**Q4. Reference-box constants or build-time calibration?**
**Recommendation: reference-box constants** (§1.3). They keep emitted
artifacts identical across build machines, and the decision reads only
ratios, which the two boxes measured agree on (0 of 44 flips).

**Q5. Should the builtin default gain a bigram block, so that no-exemplar
compiles get a run rate?**
**Recommendation: no.**
- It would be a default-path mover with no measured need once Q1 exists.
- The only permissively licensed `log_lines` corpus is the synthesized one
  (`third_party/synth-log-lines-v1`).
- Under `log`'s rates `ci-strasse` would stay a mover anyway.
- NONE stays cardinality, as findb4 built it.

**Q6. Does the cost row replace k82fix's `set-leads`?**
**Recommendation: no.** Keep (A) as the structural minimax row (§4.2). A
prior that underestimates a byte's absence prices insurance at 0, and the
row's job is not to second-guess a guard that costs one partial pass.

**Q7. The short-call entry term (union-srch, +2.4..+4.4 ns).**
- The model reproduces it as `W_lo ≈ k·f/E` (9-22 B).
- Acting on it needs the per-call subject length, which is W again.
- k82diag's net over the 73 short cells is −127 ns.

**Recommendation: do not act (D77).** The trigger is a ruling that −127 ns
is not enough.

**Sequencing recommendation.**
1. k82fix (A)+(C) lands.
2. Q1's handoff row, through the panel. This fixes the bench's K82(B) cells.
3. This cost row + B4, once Q3's E probe exists. Its measured R38 cells
   are `stack-frame` and `userpass` under `--analysis log`.
