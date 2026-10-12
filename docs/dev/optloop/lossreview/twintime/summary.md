# twintime — the quiet-box twin timing slot (2026-10-11)

**Tier: SCRATCH** (D144 add. 4: a twin is a candidate's ceiling on its own cell, never a landing number).
Box: pcrec dev box, Ryzen 7 7700X (Zen 4), Linux 7.0.0-38, `performance` governor, gcc 15.2.0, pcrec at
`aa2ddb1d` (abi 75), pcrec-bench `d359564f` read-only (`git archive` copy, regenerated subjects sha256-checked:
309 + 98 OK). Every artifact built as the bench builds it (`gcc -O2 -fPIC -shared`), driver `fatime` (the
bench's find-all loop, best of 11 per subject), pinned `taskset -c 14` (SMT sibling cpu 6 idle, checked from
`/proc/stat`), ONE timing process at a time, no build or suite beside a timing run. Desktop apps (Frank's
session) were open but idle on cpu 6/14; load1 during a run is the driver itself (~1.0).

**Method.** Per cell, arms interleaved in a per-round shuffled order (seeded by the round), 31 rounds; the
cell total is the sum over the set's throughput subjects of best-of-11 ns; the figure per (cell, arm, layout)
is the median over rounds. Layout control: `.skip PAD` at the top of `rx.c` (every function moves by PAD),
PAD = 0,16,...,112 (8 layouts) for every C1 arm and base. `base_b` is a SECOND compile of today's artifact,
run interleaved with `base`: it is the null band (base vs base re-run). Answer identity: `run_twin.sh`'s
per-subject find-all match count + span checksum over throughput, short and constructed subjects
(ANSWERS IDENTICAL for all five new twins), and `timeit.py` aborts on any per-subject checksum difference
against base on every one of the ~25,000 timed runs. "gain" = (base - arm) / base, so positive = faster.
Replicated: a first full run at 4 layouts (`raw/c1_throughput_run1_4pads.tsv`) agrees with the 8-layout run to
0.1 pp on every cell.

## 1. Candidate 1: seam helpers (fixes.md r2 §2 candidate 1, §3 step 0)

Pad-pooled: median over the 8 layouts [min .. max over layouts]. Raw: `raw/c1_throughput.tsv`, `raw/c1x_throughput.tsv`;
pooled `pooled_c1.tsv`; per layout `by_pad_c1.tsv`.

| cell | arm | gain % | layouts min..max | null band (`base_b`) | panel band | verdict |
|---|---|---|---|---|---|---|
| bak-2 | `bak2-static-seam` (always_inline) | **+9.71** | +8.49 .. +10.38 | -0.09 .. +0.22 | 10-21% | **at the band's low edge**: 0.29 pp under the bar's letter, and the bar (10%) lies inside the layout range; call it borderline, not refuted |
| bak-2 | `bak2-static-noinline` (direct call, `.constprop.0` clone) | +8.45 | +6.89 .. +8.92 | same | (arm splits PLT/specialization) | PLT removal alone = 87% of the seam arm's gain |
| bak-2 | `bak2-static-noinline-noclone` (strict PLT-only; added, see below) | +7.76 | +6.03 .. +8.33 | same | | PLT removal alone = 80% of the seam arm's gain; specialization + inlining adds 1.3-1.95 pp |
| bak-1 | `bak1-static-seam` | **+13.51** | +11.74 .. +15.50 | -0.15 .. +0.25 | 9-18% | **confirmed** (inside the band) |
| mod-j-uc | `modj-static-seam` | **+5.61** | +3.87 .. +6.83 | -0.21 .. +0.08 | 5.7-11.4% | **borderline at the low edge** (0.09 pp under; the layout range straddles 5.7); the effect is real, 3x the null band |
| phone | `phone-static-seam` (an added arm) | -0.02 | -9.94 .. +6.14 | -0.40 .. +1.03 | 5.7-11.3% | **within noise**: layout-dominated (see below), the band is not testable on this cell |
| bak-py | `bakpy-static-seam` (added) | +13.53 | +11.75 .. +15.35 | -0.12 .. +0.19 | bak-1's 9-18% (assumed) | confirmed; matches bak-1's value, so the fixes.md assumption holds |
| bak-g-rel | `bakgrel-static-seam` (added) | +13.47 | +11.70 .. +15.49 | -0.36 .. +0.15 | bak-1's 9-18% (assumed) | confirmed; same |

Implied saving per seam call (gain ns / gcov-counted `span_match_calls`, `vm/gcov_counts.tsv`), Zen 4 ns:
bak-1 1.16, bak-2 0.75 (PLT-only arm 0.60), mod-j-uc 0.84, bak-py/bak-g-rel 1.16 (count assumed at bak-1's).
Scale to the bench box by the cell-speed ratio (bench Zen 1 cell ns / this box's cell ns: bak-1 2.61, bak-2 2.51,
mod-j-uc 2.33): 3.0, 1.9, 1.96 ns per call on Zen 1 (bak-2's PLT-only arm 1.5). That is the lower half of the
panel's assumed 2-4 ns, which is why bak-2 and mod-j-uc sit at the low edge of their bands and bak-1 in the middle.
Because the bands are shares of each cell's own ns, the percentage comparison needs no separate scaling (it is the
same statement as the scaled ns/call). Bench-ns equivalent of the seven-cell result: 13.5% x 16.23 (bak-1) +
13.5% x 16.30 (bak-py) + 13.5% x 16.29 (bak-g-rel) + 9.7% x 15.48 (bak-2) + 5.6% x 25.43 (mod-j-uc)
= **about 9.5 ms** recovered on five cells, against the 7.9-15.8 ms predicted for six; phone (0.5-1.0 ms
predicted) is not measurable here. The prediction lands in the lower half of its range.

Notes that change how fixes.md reads:

- **PLT vs specialization on bak-2 (the noinline arm's question).** A direct, non-inlined call already recovers
  7.8-8.5 of the 9.7 points. The specialization (reflen folded to 1, `rx_search` 192 -> 157 insns) is worth about
  1.3-1.95 pp (about 0.15-0.25 ns per call on this box), not the larger share the "specialization exists only on the
  1-char-capture cells" paragraph implies. And the cell that has NO specialization (bak-1, runtime length) gains
  MORE per call (1.16 ns vs 0.75), so the per-cell band is not ordered by specialization.
- **The `noinline` arm as chartered is not PLT-only**: gcc emits `rx__span_match_in.constprop.0` (the constant
  length folded into a private clone), `nm` shows it. I added the strict arm (`noinline, noclone`, no clone symbol, 2 text
  symbols: the exported one and the static one) and report both. The edit is in `vm/twins/twin.py`
  (`static_noinline`, `static_noinline_noclone`; the existing `static_seam` is unchanged) and `vm/twins/twins.tsv`.
- **phone is a layout lottery.** Its seam arm is bimodal across layouts (3.76-3.85 M ns in four layouts, 4.2-4.36 M
  in four) while base spans 3.87-4.15 M; per-layout gain runs +6.1 .. -9.9. The cell is a 4.68 M-iteration VM-hat
  seek loop. Best layout vs best layout the seam is +3.0% (3.755 M vs 3.87 M), so the band (5.7-11.3%) is neither
  confirmed nor refuted. A bench-box run or a larger layout sample would be needed.
- **The null is clean**: `base_b` vs base is inside +-0.4% on every cell except phone (+1.03 max), so none of the
  C1 gains on bak-1/bak-2/mod-j-uc is a measurement artifact; the layout spread (up to 4 pp) is the larger source of
  uncertainty and is the reason the verdicts at the low edge are called borderline.
- The refute bar was "below the band's low end". On the letter, bak-2 (9.71 < 10) and mod-j-uc (5.61 < 5.7) are
  each marginally below; both are within their own layout spread of the bar and, scaled, equal the low end of the
  2-4 ns assumption. They are reported as borderline, not as a refutation of the attribution: C1's seam helpers
  are a real, replicated 5.6-13.5% on every backreference throughput cell except the layout-dominated phone.
- Not timed: the 5 short-subject C1 cells (the charter asked for the throughput twins); the trail twins
  (`*-trail-free`, `*-both`) and `*-no-start-set` (step 4-5's owed twins, outside this slot's list).

## 2. T5: D160 `fo20` vs today (misc.md §7 T5; acceptance floor = §3.1's stops table)

`t5_build.sh`: all 76 utf8 patterns compiled as the bench's pcrec-auto-caps testee (`misc/mk.py`), today vs
`--analysis fo20 -I DIR` (the SCRATCH prior of `misc/gen_d160f.py ... fo20 o 20`, never a candidate for
`src/findings/`). 72 compile; 4 refuse at this pin (`asr-b-cyr-ucp`, `cls-w-ucp`: UCP wide sets;
`prp-ingreek`: unimplemented property; `prp-l-anchored`: over the emitted-size cap), as for any arm. Of the 72,
**10 emit different C** (everything else differs only in the `RX_FINDINGS` stamp, `raw/t5_class.txt`) and only those are timed.
Of §3.1's 14 cells, 5 are the SAME artifact (`lit-cyr-run`, `lit-1ch-3b`, `alt-nearmiss`, `qnt-counted-3b`,
`ci-moskva`): their stops are equal by construction and nothing moves. Same driver, same 7 utf8 throughput subjects,
4 layouts, 31 rounds (`raw/t5_throughput.tsv`, `pooled_t5.tsv`). Stops = libc memchr calls, counted with
an `LD_PRELOAD` shim (`memcount.c`, `raw/t5_stops.tsv`); "pred." applies the measured gain to the bench's
set-grain auto-caps ns (Zen 1) and compares it with the strongest trailing comparator (`misc/data/cells.tsv`),
a crude transfer because the stop price differs between boxes.

| cell | stops today -> fo20 (§3.1 column: fo20) | gain % (4 layouts) | null | bench ns -> pred. | vs peer | reading against the floor |
|---|---|---|---|---|---|---|
| lit-sharp-s | 83,154 -> 2,089 (2,089) | **+94.00** (x16.7) | +-0.06 | 622 -> 37 µs | x0.63 of rust | floor met; modelled 930 -> 53 µs (x17.5) matches |
| lit-offset-at-head | 16,728 -> 7 (7) | **+85.11** (x6.7) | +-0.14 | 227 -> 34 µs | x1.19 of re2 (28.3) | floor met; just over the peer (the model said 30) |
| lit-1ch-4b | 14,582 -> 2,638 (2,638) | **+67.37** | +-0.08 | 205 -> 67 µs | x0.95 of re2 | met |
| qnt-bounded-4b | 12,027 -> 2,638 (2,638) | **+63.21** | +-0.13 | 193 -> 71 µs | x0.80 of rust | met |
| lit-mixed-ascii | 3,727 -> 7 (7) | **+57.12** | +-0.17 | 72 -> 31 µs | x0.52 of rust | met |
| ci-ascii-control | 25,844 -> 9,463 (9,463) | **+53.32** | +-0.16 | 405 -> 189 µs | x0.78 of rust | met |
| lit-nfc-pair | 16,966 -> 16,700 (16,700) | +1.39 | +-0.11 | 234 -> 231 µs | x2.82 of rust | met, but nothing to gain: the cell stays x2.8 behind (pick half only, as misc.md said) |
| asr-b-ascii | 42,990 -> 42,228 (42,228) | +1.55 | +-0.24 | 502 -> 494 µs | x4.97 of rust | met, nothing to gain (the prefilter does not move) |
| **ci-strasse** | 45,914 -> 56,124 (15,430 -> 19,549) | **-11.61** (11.6% SLOWER; layouts -9.6 .. -13.9) | +-0.18 | 946 -> 1,056 µs | x2.67 -> x2.7 of rust | **the floor says "+6%, the only regression"; the clock says 11.6%** (a pair arm: the prior moves the scan member `@2 -> @1`). Not an acceptance failure by the stops column but a larger loss than the model priced. |
| lit-cyr-run, lit-1ch-3b, alt-nearmiss, qnt-counted-3b, ci-moskva | equal (5,611; 7,666; 5,746; 5,749; 146,633) | same artifact | n/a | unchanged | | met (identical) |
| **cls-s-ucp** (`(*UCP)a\sb`, not in §3.1's table) | 43,572 -> 8,783 | **+66.10** | +-0.13 | | | an UNLISTED MOVER: its DFA prefilter flips `memchr` -> `handoff` (scan 'a' -> landmark 'b'); misc.md says "0 of 62 other cells move >6%", this one moves 66% (a win) |

The 14-cell stops table is reproduced EXACTLY by the artifacts at this pin for 13 of 14 cells (the counts equal the
column digit for digit); `ci-strasse` counts both streams of the pair arm (45,914 / 56,124 against the column's
single-stream 15,430 / 19,549: the ratio x1.22 vs x1.27 agrees). So the acceptance floor is intact as stated, and the
timing finds: the six pick-defect cells improve 53-94% (the modelled gains reproduce within a few points),
the two half-pick cells gain 1.4-1.6%, five cells are untouched, and ONE cell regresses by more than the +6%
the floor allowed for: ci-strasse, -11.6%. Before D160 builds in the `fo` shape, the ci-strasse regression
(or a pair-arm-aware pick) should be priced; the unlisted cls-s-ucp mover is a gain.

## 3. What this does not say

Scratch tier on a bench-class-but-different box (Zen 4; the bench is Zen 1): the figures are ceilings of the
twins on their cells, the landings need the bench's own run. The layout control is 8 (C1) / 4 (T5) function
shifts, not a full alignment sweep; phone shows the layout effect can exceed the band. The short-regime C1 cells,
the trail-free twins and the DENSE-SKIP arms were outside this slot's list.
