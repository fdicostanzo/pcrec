# r1 — [OPT-HYB-RESEED] critic: checks and claimed numbers

Read-only critic, lane `reseed` (worktree `worktrees/reseed`, HEAD `8f6007b8`).
Lens: the new checks and the numbers the report claims. Probes ran in
`/tmp/critic_r1` and against the lane's scratch (`/tmp/reseed_scratch`); no
tracked file was touched and no suite was run. The worktree's `build/pcrec` is
the stale bit-36 build (`--list-axes` prints bit 36). Every emitted-text probe
below is unaffected by that.

## Verdict table

| # | severity | finding |
|---|---|---|
| F1 | HIGH | The change breaks `run_size_term.sh`'s cap-rescue pin (K=4 no longer fits under 31,500). The lane's own owed chain already shows it, and the report's "codegen 125/0" hides it. |
| F2 | MEDIUM | Row 2's "NONE answers by cardinality" is false in a default build. A shipped default byte-rate prior is in force, and the spec sentence contradicts the lane's own witness. |
| F3 | MEDIUM | Timing claims: "×2.4-×28" is unsupported and false as stated. The noise floor is about 4%, so several "wins" and "losses" are noise. The ×0.81 twin comparison ignores the plan's own caveat. |
| F4 | MEDIUM | The calibration (16/64/1024/64, 4/16/64/2) is pinned by no check and not reproducible from the repo. The budget arm cannot see a swapped or altered row. |
| F5 | LOW-MED | S370 has exactly one real detector, and its description overstates what the plant does. |
| F6 | LOW | Check-count and scope nits: "15 checks" reads as 13. The clamped-witness awk is unbounded. `RX_VM_RESEED` has no spec-vs-dump value-set check. `registry.md` §6 counts are stale and unlisted. |
| F7 | INFO | Confirmed sound: 141→147, the identity-sweep deny leg, and census equals movers. |

## F1 (HIGH). The adaptive text moves a size pin the report does not mention

**Evidence.**
- `/tmp/reseed_scratch/chain.status` reads `codegen rc=2`.
  `v_codegen.log:242` reads: `FAIL: the rescue took K=2; under this reference
  build the ladder's rung 6 does NOT fit (36,149 B against the 31,500 cap) and
  rung 4 does (31,068 B)`. `make: *** [test-codegen] Error 1`.
- The other failure in that log (`run_inline_capability.sh`, "nm could not
  read arm_a.o") is the known Mac nm-only failure quoted in the u2land merge
  message. The size-term failure is not.
- Mechanism. The witness is `(?:aa|a){8,12}+b`, which is possessive, so its
  prefilter is over-approximating. It now stamps `adaptive`. I compiled it
  with `/tmp/reseed_scratch/base/build/pcrec` and with the lane's build at
  `--unroll=4` and `--unroll=6`:

  | K | base bytes | new bytes | delta |
  |---|---:|---:|---:|
  | 4 | 26,748 | 27,317 | +569 |
  | 6 | 31,830 | 32,399 | +569 |

  These are `.c` file bytes, not the size model's "code bytes", but the delta
  is the same text. The script's own comment records K=4 at 31,068 B against
  the 31,500 cap, a 432 B margin. +569 B (about 570) puts K=4 near 31,640,
  over the cap. The ladder then takes K=2, which is the failure above.
- The report §6 lists `make test-codegen` as OWED only for the FILEPIN. It
  never says the whole target is red. The report cites "codegen suite 125/0",
  which is `run_codegen_tests.sh` alone, not the target.
- The mechanism matches the D94-addendum lesson in the situation index: a
  reader that never cites the number still moves with it. The lane's
  grep-for-readers covered the abi number. It did not cover emitted size.

**Disposition.**
- Re-calibrate the cap the way that script's own comment recipe does
  (31,000→31,500 at B1). Measure K=6, 4, 3 and 2 on a rebuilt reference
  compiler. Choose the cap so that 6 and 3 do not fit, 4 fits, and 2 fits.
  My estimate is a cap near 32,000. K=3 would be about 32,500, K=6 about
  36,700 and K=2 about 30,400, but re-measure rather than trust my delta.
- Add the readers to the "sizes that ride emitted text" list in the report.
- Check the other size-driven pins for the same +569 B on adaptive hybrids:
  `docs/dev/artifact_size_log.tsv` (already dirty in `git status`),
  `RX_MAX_EMIT_*` boundary witnesses, and the size-term materiality pool
  (that pool passed here).
- Not an answer or stamp defect. A 25% sample of the 1,118 movers (280
  artifacts) showed no `UNROLL_K`, `UNROLL_K_WHY`, `VM_ENTRY_SHAPE` or
  `VM_FRAMELESS` change between base and new, so the size shift does not
  visibly re-pick K on the corpus. The sample is not proof for the rest.

## F2 (MEDIUM). "NONE answers by cardinality" is not what a default build does

**Claims.** Report §1 item 3, design §4 and `tuning.md` §2.33 row 2 say: "with
no prior this is the set's cardinality, so a single byte never qualifies and a
wide class can." The code comment on `pcrec_find_set_ppm` says the same for
NONE.

**Evidence.**
- Default compiles stamp `#define RX_FINDINGS "byte-rate=default:1822fb97…"`.
  A prior is in force, not NONE. `--analysis none` is refused as an unknown
  analysis.
- The lane's own row-2 witness is `' (?=the)'`, the single byte `' '`. It
  stamps `adaptive-dense` (codegen `dense` witness; I reproduced it). A
  singleton under cardinality would be 1/256, about 3,900 ppm, far under the
  1e6/16 threshold. So the shipped English-like default prior is what makes
  the space "dense".
- `a(?=the)` stamps `adaptive`, and `[a-z](?=the)` stamps `adaptive-dense`.
  So which 73/72 artifacts are `adaptive-dense` is a fact about the default
  prior's letter frequencies, not about the pattern.

**Consequence.**
- The spec sentence is false in the default configuration. This is a
  caller-visible contract sentence (D80).
- The starting mode on non-prose subjects (logs, binary, CJK) is chosen from
  prose statistics. Cost is bounded (the probe re-seed ends the first block),
  but it is a stated design property the text misdescribes.
- The codegen `dense` witness passes only because of the default prior.
  Nothing pins the NONE-prior arm of the predicate.

**Disposition.** Fix the three sentences to say "under the compile's byte-rate
prior (the built-in default unless `--analysis` names another)". Add a second
row-2 witness under a non-default analysis, or state that row 2 was never
measured under one. The design note's D126-Q4 story is fine; the prose about
what the default is, is not.

## F3 (MEDIUM). Timing claims versus their stated method

Source: `docs/dev/reseed/timing_mac.md`; a loaded Mac (load 13-18); darwin is
directional only, which the report says.

1. **"×2.4-×28" (report §7, plan row, design §5's "Bursty ×15-×28") is not in
   the table.**
   - The maximum is ×21.56 (varwidth gap64). Bursty reads ×14.62 (fixed) and
     ×20.05 (varwidth). ×28 appears in no row.
   - "Every cell where the old loop stepped over a sparse region" is also
     false as a range. The same table has fixed synth-1m at ×1.16, gap1, 4
     and 16 at ×1.15-1.21, adv16 at ×1.20 and cjk4 at ×1.19. The minimum of
     the "wins" is ×2.34.
   - Disposition: restate as "up to ×21.6, from these subjects" and drop
     ×28, or point at the measurement that gave it.
2. **Noise floor.**
   - The `base` and `deny` columns are byte-identical programs, so their
     difference is pure noise: fixed synth-1m 1.910 vs 1.992 (4.3%), neg
     synth-dense 5.520 vs 5.700 (3.3%), varwidth synth-64k 8.286 vs 8.545
     (3.1%).
   - So ×0.97, ×0.96, ×0.99, ×1.02, ×1.03 and ×1.07 are all noise.
   - "asr-lb-fixed dense is now a small win (×1.02)" is a null result. The
     honest claim is "flat within noise", which is what the draft inbox ask
     says (±5%).
   - The real signals are ×0.92 (lka dense) and ×0.94 (cjk1), and they are
     only marginally over the floor.
3. **The "always-re-seed twin ×0.81" comparison.**
   - The plan row's I-114 caveat says the Mac scratch table (×0.81-0.90) "may
     be partly the same lottery; do not cite it without fresh-launch
     medians". Report §7 cites ×0.81 as the foil without that qualifier.
   - The report's own inbox draft cites ×0.957 (x86, gcc) for the same cell.
     The two numbers are different platforms; the report should say so.
   - The driver (`/tmp/reseed_scratch/drv.c`) takes a median of `reps` inside
     ONE process (`./x subj 7`). The stated "median of 3 × best-of-5" cannot
     be reconstructed from it, and it is not a fresh-launch median. The
     per-process bimodality that plan row records is not controlled.
4. **Unexplained ×1.15-1.21 at gap1/gap4/gap16 on asr-lb-fixed.**
   - There the adaptive machine should sit in step mode, or in re-seed mode
     at gap16 (gap ≥ 16 counts as long), and equal the step arm (about 1.65
     ns/B). It reads 1.36-1.40.
   - A 15-20% win where the model predicts parity is either layout or
     alignment luck or something the mechanism does not explain. It should
     not be counted as a mechanism win.
5. `--tune`, "no measured bench scale": the report is honest about the
   synthetic subjects not reproducing ×25-×124. No finding.

## F4 (MEDIUM). The calibration is neither pinned nor reproducible

**Pinning.**
- No check reads any calibration number. The codegen block reads the row
  name, the call-site count, and three strings (`reseed_steps_left > 0`,
  `reseed_steps_left = reseed_block;`, `window_end = subject_length;`).
- The budget arm uses `--step-budget=2000`. Analysis: in the sparse tail the
  first probe re-seed jumps to the end, so the call spends at most one block
  of steps. Any finite block or `first` under about 1,900 passes. Swapping
  the two class rows (framed getting 64/1024/64) therefore still answers
  `nomatch` on both subjects. An `s/16/16000/` on the cap or gap is likewise
  invisible.
- The `frameless` and `framed` witnesses check only the stamp and the call
  sites. They do not check that the class picked the right row.
- So "a calibration row per class" is unguarded. The only defence is that
  `has_push` indexes a two-entry array.

**Reproducibility.**
- `docs/dev/reseed/` holds the census, the sweep, the answer diff and one
  result table. Nothing in it produces the crossover table (§3 of the
  design) or `timing_mac.md`.
- The generators (`gen.py`, `gen114.py`), the driver (`drv.c`), the hand-twin
  transformer (`twin.py`) and the bench scripts (`bench.sh`, `dbl.sh`,
  `modes.sh`) exist only under `/tmp/reseed_scratch`. The subject names
  (`synth-1m`, `gap64`, `bursty`, `adv16`, `dense_sparse`, `cjk16`) are
  defined nowhere in the repo.
- A reader cannot rerun the calibration, and the tree points at the scratch
  as if it were the record.

**Derivation gaps.**
- Frameless gap 16 is the minimum of three measured crossovers (16 / 26 /
  30 B). That is defensible, but the two later crossovers are not used.
- Framed gap 4 comes from `(?<=a|é)x` (~3 B). The other framed witness,
  `(?<!日)本`, crosses at 9-12 B, so at gaps 4-12 B it re-seeds where
  stepping is cheaper (cjk4 ×1.19, cjk1 ×0.94 are the cells).
- Frameless `first = 64` is one pattern (`item(?= done)`, 8 steps ×1.8 vs 64
  steps within 10%). Framed `first = 2`, `block = 16`, `cap = 64`, and
  frameless `block = 64` and `cap = 1024` have no stated measurement.
- The design text says "All four are measured, none derived", but the doc
  gives the measurement for `first` (frameless) and the gaps only.

**Disposition.**
- Commit the twin, generators and driver (or one script that regenerates
  the subjects) under `docs/dev/reseed/`, with the raw output the tables
  were read from.
- Add one check that reads the emitted numbers per class: a frameless and a
  framed witness asserting the literal `reseed_steps_left = 64, ...` /
  `= 2, ...` declaration. Or stamp the calibration. A row swap is then red.
- If the swap is judged not worth a check, say so in the design note (D77:
  name the trigger).

## F5 (LOW-MED). S370: one detector, and the description overstates the plant

- S370 fires two checks in `codegen`: the dense budget subject, and
  `[SABANCHOR]`, which is the plant removing its own anchor and so detects
  nothing about the emitter. There is exactly one real detector, and it is
  the check that leans on the `--step-budget=2000` arithmetic. My analysis
  says it is sound for this plant: after the first short probe, block =
  UINT_MAX steps every remaining position. But it is one check.
- The header says "the probe never ends a block" and the codegen comment
  says "(the probe exit removed)". The plant does neither. The FIRST block
  still ends in a probe; only the SECOND is unbounded. A plant that really
  removes the probe exit (for example a decrement that never reaches zero)
  is caught by the structural string checks. A plant that removes the
  doubling is benign. So the two rows plus the budget arm cover the probe
  exit, but the wording should say "the second block".
- Would S371 fire if the adaptive text were removed? Yes, by design: 8
  detectors (call-site count, step-exit string, clamped `window_end`, both
  budget subjects, anchor). It does not share a source with what it
  controls, because the expected call-site counts and strings are hand-typed
  in the check.
- Both budget-arm subjects have a proper control (the deny arm must give up
  `steps` on both), which is the best-designed part of the block.

## F6 (LOW). Smaller items

1. **Check count.** The report says "15 checks". I count 13 `ok`s in the
   block (9 witness rows, 1 clamped, 1 control, 2 default budget subjects).
   Reconcile against `git diff main...HEAD` on the suite's count. The
   S370/S371 figures 123+2 and 117+8 both sum to 125, so the total is
   consistent. It is the "15" that needs a source.
2. **Clamped `window_end` check** (codegen, `rs_clamped.c`). The awk starts
   at the first `reseed_steps_left > 0` and runs to end of file. A
   `window_end = subject_length;` anywhere later in the file satisfies it,
   and a `window[0][1]` anywhere later fails it. Bound it to the retry's
   block. It is not vacuous today: an artifact lacking the text goes red.
3. **No value-set check for `RX_VM_RESEED`.** The registry check has
   `check_value_set` legs for `RX_DFA_TABLE`, `RX_VM_PREFILTER`, `RX_ENGINE`,
   `RX_UNROLL_K_WHY` and others. `RX_VM_RESEED` has none, so the
   `match_api.md` §6.3 table, the dump (walked live off the same C table) and
   the emitter's actual stamp values are not tied together. The codegen
   witnesses cover all four values once each, so this is a gap in kind, not
   coverage today.
4. **`registry.md` §6 is not updated.** It says "87 rows / 31 axes" and lists
   the axis values, and the file tells the reader to re-derive it. The tree
   already reads 99 rows / 35 axes with the new axis (stale before this lane
   too). The new axis `hyb-reseed` is in neither the count nor the list, and
   the section says "append-only, a new axis is a new value". It is
   pre-existing staleness, but this change is a caller-visible addition.
5. **Other spec hunks.** `lib/pcrec.h`, `tuning.md` §2.33 plus its table row,
   `match_api.md` §6 abi paragraph and §6.3 stamp table, and `cli.md`'s
   `--help`-omitted list are all present. `cli_axis_apply` is driven by
   `axes.def`, so no CLI hunk is missing. The bit-37 mask into
   `strategy_denials` is in `emit_dfa.c:2571`. Deferred to F2 for the row-2
   sentence.
6. **Registry pin merge hazard.** The pin is now 147 on this branch. Every
   other lane adding an axis (s4build holds bit 36) edits the same line. That
   is a serialization point for the manager, as the report already says for
   abi.

## F7 (INFO). Attempted refutations that did not land

- **141→147 by mechanism.** Confirmed. In `axes_registry_check.sh`, a
  one-bit deny row yields exactly 3 `ok` lines (macro-bit, cli flag accepted,
  bit documented in `tuning.md`). `hyb-reseed` has two rows carrying
  `PCREC_NO_HYB_RESEED`, so 6. Rows 1 and 4 have no deny cell and add none.
  This is the same shape as `ctx-node` (138→141, one row). The pin counts a
  duplicated fact (one flag, one bit, one heading checked twice), so it says
  "rows", not "distinct facts", but it is honest.
- **Identity sweep is not vacuous.** The `deny == base` leg runs over 549
  (byte) and 569 (utf8) artifacts that actually stamp `adaptive*`, and the
  "adaptive stamped ⇒ text moved" leg has teeth. The mover count equals the
  census's over-approximating population exactly (476+73 = 439+110 = 549;
  497+72 = 455+114 = 569). The census classification uses the E1 kinds and
  `VM_PREFILTER_LANG`, a partly independent source from `mrl_win`, so that
  equality is a real cross-check.
- **Limits of the sweep (not defects).**
  - It compiles corpus pattern lines at default flags, `--features all`, both
    encodings only. Blocks carrying their own flags (`--engine`,
    `--step-budget`, `--vm-entry-shape`, `-fno-prefilter`) are not swept.
    `make test-axes AXES=-fno-hyb-reseed` (owed) is the only cover.
  - It proves text, not answers. The answer differential is still running
    and OWED. Given F1 it is worth running to completion before merge.
  - A "mover" is any text difference. It does not verify that only the
    retry lines and the abi digit moved. My 280-artifact sample showed no
    stamp shifts, but a whole-diff filter would make the sweep strict.
  - Everything is under the default prior; a non-default `--analysis` is
    never swept (see F2).

## Order of work I suggest

1. F1: recalibrate the size-term cap and re-run `make test-codegen` (needed
   before merge).
2. F2 and F3: fix the false sentences (spec, design, report, plan row).
3. F4: commit the calibration instruments and add the per-class numbers
   check, or record the D77 decision not to.
4. F5 and F6: wording and small scoping fixes.
