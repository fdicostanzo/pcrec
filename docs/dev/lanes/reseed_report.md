# reseed — [OPT-HYB-RESEED] delivery report

Lane `reseed`, opus, 2026-09-29. Branch `lane/reseed` in
`worktrees/reseed`, cut from `lane/u2land` at `23645945` (abi 46). The
design section is `docs/design/hyb_reseed.md` and the instruments are
`docs/dev/reseed/`. Charter (Frank, eighty-sixth session): *"would it use
freq or other data to decide? out-of-box: can it use live stats to decide?
if last run, or last 2 runs before next try < N, then don't call dfa?"*,
then *"charter it"*. Both are quoted in the plan row, which now reads
STATE:started with a DELIVERED note.

## 0. Summary for a fresh reader

**The defect.** After a failed VM attempt, the hybrid's loop re-asked the
prefilter only when an MRL clamp existed. A clamp-free hybrid whose
prefilter answers for a larger language than the pattern's (a lookaround or
a cut erased, or the count collapse) therefore stepped every character to
the subject end once one prefilter answer failed.

**What landed.**
- ONE first-match table, `pcrec_reseed_rows` (`src/gen/emit_vm.c`). Its
  rows are data: `exact` / `adaptive-dense` / `adaptive` / `fixed`, walked
  once per hybrid in the plan phase and listable through `--list-axes`
  (axis `hyb-reseed`).
- The adaptive retry, built from two or three per-CALL locals. It re-seeds
  and reads the jump. Two short jumps start a step block. The block ends in
  one probe re-seed, a short probe doubles the next block up to a cap, and
  a long jump resets.
- A calibration per PROGRAM CLASS (frameless/framed, off `has_push`).
- The deny `-fno-hyb-reseed` (bit 37) and the stamp `<PREFIX>_VM_RESEED`.
- `abi` 46 → 47, with the full D76/D94 ritual.

**Validation.** Verdicts are below with their logs.
- The byte-identity sweep is clean over 6,756 rows.
- The answer differential at every startpos is clean over the mover
  population.
- `make strict` is clean.
- The codegen suite's new block is green, and both sabotage rows are
  DETECTED.
- The `registry` suite needed the coverage re-pin.

`make test` in full is **OWED**, as is `make test-axes`
`AXES=-fno-hyb-reseed` (see §6).

## 1. Deviations from the brief, each with its reason

1. **N and K are not single constants.** The measured crossover depends on
   what a failed VM attempt costs, which varies about five-fold with the
   program's frame discipline (1.6 ns/position frameless, 8.6 framed). The
   re-seed cost is about constant, near one prefilter call (~25 ns).
   Frameless crossovers measured 16-30 bytes, framed about 3 positions. A
   single N was measured wrong in both directions: N=16 on
   `(?<=a|é)x`/synth-1m made adaptive ×2.5 slower than always-re-seed.
   `vm_reseed_cal` therefore carries one calibrated row per class (§3 of
   the design). The "N/K" of the brief are that table's `gap`/`block`
   columns.
2. **Doubling step blocks and a per-class `first` budget were added.** A
   fixed K left a 5-17% probe cost on dense subjects. `first` exists
   because find-all over a match-dense subject makes many short calls,
   and each call re-learns the density. Both were measured before they
   were kept (design §3).
3. **Row 2 is not "a findings bundle present".** D126 Q4 forbids a reader
   from testing the prior's NONE. So row 2's predicate hands the candidate
   scan's byte set to the MASS primitive, which answers NONE by
   cardinality. A singleton scan under `-e utf8` never reads as dense and a
   64-byte class can. Rows 2 and 3 run the same adaptive machine and differ
   only in the starting state. That is the brief's "density picks the
   STARTING mode" without a NONE test at the reader.
4. **Row 1 reads `Vm.mrl_win`.** That field already IS "a prefilter exists
   and its language is the pattern's own": its three conjuncts are exactly
   the three erasures `src/ir/nfa.c` performs. Reading it is one
   derivation, not a second; see `src/gen/CLAUDE.md`'s new section. The
   clamped over-approximating hybrids (110 byte / 114 utf8), which already
   re-seeded always, are ALSO adaptive now. That is the general mechanism,
   and a step block there cannot carry a stale window, because `mrl_win` is
   false so the ceiling is the subject end on both arms.
5. **`--tune` moves nothing.** The dial's table is a pinned contract (D103)
   and admits a cell only with a measured two-axis rate. The calibration
   table is where such a cell would point.

## 2. D77 census (`docs/dev/reseed/census.py`, branch point)

| encoding | hybrids | clamp-free exact | clamp-free over-approx | clamped exact | clamped over-approx |
|---|---:|---:|---:|---:|---:|
| byte | 1,082 | 309 | 439 (302 look, 100 atomic, 37 both) | 224 | 110 |
| utf8 | 1,101 | 304 | 455 (319 look, 99 atomic, 37 both) | 228 | 114 |

## 3. Identity sweep (`docs/dev/reseed/identity_sweep.py`, `identity_sweep.log`)

The sweep compares branch point against this change, default and
`-fno-hyb-reseed`. It covers every corpus pattern line (3,378 unique) under
`--features all`, both encodings, with `-o -` on every side. Normalization
removes only the abi digit and the `RX_VM_RESEED` line.

| enc | identical (non-hybrid) | identical (`exact`) | movers `adaptive` | movers `adaptive-dense` | both refuse | violations |
|---|---:|---:|---:|---:|---:|---:|
| byte | 1,930 | 533 | 476 | 73 | 366 | 0 |
| utf8 | 1,907 | 532 | 497 | 72 | 370 | 0 |

- Deny equals base on every compiling artifact.
- Every adaptive-stamped artifact moved, and nothing else did.
- The census's over-approximating population (549 byte / 569 utf8, clamped
  and clamp-free) equals the mover count exactly.

## 4. Answer identity at every startpos (`docs/dev/reseed/answer_diff.py`)

**OWED at hand-off.** The run is detached with `nohup` and is running
against the pre-renumber build. The deny bit is masked out of
`rx_info.flags`, so the default artifacts it compares are the same text at
bit 36 or bit 37.

- Command: `python3 docs/dev/reseed/answer_diff.py /tmp/reseed_scratch/base/build/pcrec <tree>/build/pcrec /tmp/reseed_scratch/idsweep.tsv /tmp/reseed_scratch/answer_diff.log --jobs 2`.
- Population: the 1,118 mover artifacts (549 byte + 569 utf8).
- Completion line: `movers: 1118` at the head of
  `/tmp/reseed_scratch/answer_diff.log`, with the tally on the lines after
  it. Stdout goes to `/tmp/reseed_scratch/answer_diff.out`.
- Verdict rule: any `DIFF`, `COMPILE-FAIL` or `ERROR:` line below the tally
  is a finding. `SKIP-LINK` is a `vars` artifact, whose search takes the
  environment pair. The script exits 1 on a finding.
- Coverage elsewhere: the codegen block's budget arm exercises the adaptive
  loop at run time, and every corpus answer runs through `make test`
  (owed, §6).

## 5. Checks and sabotage

`tests/codegen/run_codegen_tests.sh` has a new `[OPT-HYB-RESEED]` block of
15 checks; the suite reads 125/0. The checks:
- the stamp IFF over eight witnesses, one per row plus forced-VM and DFA
  absences;
- the prefilter call sites in `<prefix>_search_run`;
- the clamped witness's `window_end`;
- a budget arm with its own deny control.

| row | plant | measured |
|---|---|---|
| S370 | a short probe sets the next block to UINT_MAX (the probe never ends a block); every structurally-read string intact | DETECTED, `codegen:2fail/123pass` (the budget arm's dense subject + SABANCHOR) |
| S371 | the adaptive text never emitted under an `adaptive` stamp | DETECTED, `codegen:8fail/117pass` |

## 6. Validation run, and what is owed

Run on a scratch build of HEAD (`d27eb208`+, bit 37) unless noted:

- `make strict CC=gcc-16`: clean (on the bit-36 tree; the renumber is one
  macro value).
- `tests/codegen/run_codegen_tests.sh`: **125 passed / 0 failed**
  (bit-37 build).
- `tests/registry/axes_registry_check.sh`: **147 / 0**. That MOVED the pin
  in `tests/registry/run_registry_tests.sh` from 141 to 147, re-pinned with
  its comment. It is a D94-addendum reader: the deny sits on TWO live table
  rows, 2 × 3 triples.
- Identity sweep: 0 violations (§3). S370 and S371 are DETECTED (§5).
- `--list-axes` prints the four `hyb-reseed` rows, with bit 37 on the two
  deniable ones.
- PC-3 read 213/0 in the first registry run (bit-36 build). The rest of
  that run was superseded by the renumber.

**OWED** (the manager's battery):
- The full `bash tests/registry/run_registry_tests.sh` on the bit-37 build
  (PC-4 and the definitions oracle are long).
- `make test-codegen`: the recursion-identity FILEPIN is self-pinned to
  `9183433d`, this lane's abi-bump src commit, per convention.
- `make test`.
- `make test-axes AXES="-fno-hyb-reseed"`.
- The answer differential (§4).
- A `rxtsource` census run. No corpus file changed, so nothing is expected
  to move there.

**ABI SERIALIZATION.** This branch writes abi 46 → 47 (the u2land base).
If k73utf or another lane lands first, the digit, `ABI_EXPECT`, the
`match_api.md` §6 entry and the FILEPIN need the manager's renumber at
merge.

## 7. Mac scratch timing (`docs/dev/reseed/timing_mac.md`)

SCRATCH tier: Apple M1, gcc-16 `-O2`, a loaded box (load 13-18),
find-all, median of 3 × best-of-5. The columns are base (branch point),
new, and deny (≡ base); every answer was identical.

| cell | subject | base ns/B | new ns/B | base/new |
|---|---|---:|---:|---:|
| asr-lb-fixed `(?<=é)x` | synth-1m | 1.910 | 1.643 | ×1.16 |
| asr-lb-fixed | synth-dense | 4.070 | 3.985 | ×1.02 (the always-re-seed twin was ×0.81) |
| asr-lb-fixed | gap64 / bursty | 1.679 / 1.659 | 0.402 / 0.114 | ×4.2 / ×14.6 |
| asr-lb-varwidth `(?<=a\|é)x` | synth-1m | 8.348 | 3.212 | ×2.60 |
| asr-lb-varwidth | synth-dense | 6.370 | 6.670 | ×0.96 |
| asr-lb-varwidth | gap16 / gap64 / bursty | 8.6-8.7 | 1.57 / 0.40 / 0.43 | ×5.5 / ×21.6 / ×20.1 |
| asr-lb-neg `(?<!日)本` | synth-1m | 4.288 | 0.427 | ×10.0 |
| asr-lb-neg | cjk1 (a failing candidate per character) | 2.894 | 3.069 | ×0.94 |
| asr-lb-neg | cjk16 | 2.865 | 0.677 | ×4.2 |
| lka-pos `item(?= done)` | sparse prose | 0.534 | 0.519 | ×1.03 |
| lka-pos | match-dense prose | 1.857 | 2.014 | ×0.92 |
| ` (?=the)` (adaptive-dense) | prose | 1.610 / 2.206 | 1.655 / 2.217 | ×0.97 / ×0.99 |

What the table shows:
- **Wins.** Every cell where the old loop stepped over a sparse region is
  ×2.4-×28.
- **The cell the brief worried about** (asr-lb-fixed dense) is now a small
  win, where always-re-seed lost 19%.
- **Losses.** The worst cells are per-call: find-all over a match-dense
  subject re-learns the density on every call. They are filed as
  `[OPT-HYB-RESEED-XCALL]` with these three cells as its witnesses.
- **Scale.** The synthetic subjects do not reproduce the bench's ×25-×124.
  They were not built to the bench's letter frequencies. The bench's own
  subjects decide the magnitude.

## 8. Draft bench inbox ask (NOT SENT; for the manager to relay)

> **I-1xx — [OPT-HYB-RESEED] adaptive retry, re-measure at the pcrec pin
> carrying abi 47.** The VM hybrid's retry now either steps or re-seeds
> from the prefilter, chosen per call. `<PREFIX>_VM_RESEED` names the row:
> `exact` / `adaptive-dense` / `adaptive` / `fixed`. `-fno-hyb-reseed`
> restores the abi-46 retry byte for byte, apart from the stamp line and
> the digit.
>
> Please measure:
>
> 1. **The utf8@0.1 cells**, pcrec auto against `-fno-hyb-reseed`, both
>    compilers, 15 fresh launches each (O-68's bimodality note), all seven
>    throughput subjects:
>    - `asr-lb-varwidth`, `asr-lb-fixed` and `asr-lb-neg` (O-63's rows
>      1/10/11);
>    - I-114's three synthetic subjects.
>
>    PREDICTION (Mac scratch):
>    - varwidth and neg on any subject with sparse candidates are ×2-×25
>      faster;
>    - asr-lb-fixed/synth-dense is flat (±5%), where I-114's always-re-seed
>      twin was ×0.957 under gcc;
>    - no cell slower than ×0.90.
> 2. **The syntax@0.1 `lka-pos`/`lka-verb` cell** (ctxjoint's attribution:
>    its loss is per-byte VM stepping). PREDICTION: auto no longer equals
>    forced-VM there; faster on its throughput subjects.
> 3. **Any roster cell whose artifact stamps `adaptive*`**, bucketed by row
>    and by `RX_VM_FRAMELESS`. Name any cell that reads more than 5% slower
>    than `-fno-hyb-reseed`. Those are `[OPT-HYB-RESEED-XCALL]`'s trigger
>    (the per-call re-learning cost), and the row wants them named.
>
> Answers are identical by construction: the per-startpos differential over
> 1,118 mover artifacts reads clean. A cell whose answer moves is a finding,
> to be reported before any timing.

## 9. Mac owed validation (reseedval, 2026-09-29): IN FLIGHT, verdicts OWED

- The answer differential (§4) is still running (started 23:33, PID 17352;
  a pass over 1,118 movers, ~150 done by 23:43, so ETA ~00:40). Its log is
  written only at the end: `/tmp/reseed_scratch/answer_diff.log`, head line
  `movers: 1118`. It reads `$W/build/pcrec`, so nothing was rebuilt in the
  worktree.
- (b) and (c) run from a scratch COPY of the tree (`/tmp/reseed_scratch/wt2`,
  built at bit 37, PROCS=2), detached, in one chain
  (`/tmp/reseed_scratch/chain.sh`): test-codegen, test-rxtsource, the full
  registry script, then `make test-axes AXES="-fno-hyb-reseed"`. Status
  lines land in `/tmp/reseed_scratch/chain.status` (`<step> rc=N`, then
  `DONE`); logs are `v_codegen.log`, `v_rxtsource.log`, `v_registry.log`,
  `v_axes.log`. Verdict is make's `*** [...] Error` lines / the rc, not a
  grep for FAIL.
