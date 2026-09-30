# Clamped over-approximating hybrids: does the adaptive retry pay? (r1 sem F1)

Lane `reseedfix`, 2026-09-30. The r1 panel (`docs/dev/reviews/2026-09-30-r1-hyb-reseed.md`)
asked for a measurement of deviation 4 in `docs/dev/lanes/reseed_report.md` §1:
lane `reseed` had made the CLAMPED over-approximating hybrids (110 byte / 114
utf8 artifacts in the D77 census) adaptive too. The question has two sides.

## The contract side

On a clamped hybrid, today's (abi-46) retry already re-seeds after every
failed attempt (`retry_win`, D51 ruling 2). A step block therefore ADDS
attempts that retry skipped. Each attempt charges the call's shared step and
work budgets, so a call that answered can give up. The sem critic's witness
shows it: `(?<=a|bc)[a-c]{2,4}d`, `--work-budget=100000`, subject
`xabd`×20000 + `aabd` answers `1,80001-80004` at abi 46 and `PCREC_ERR_WORK`
under lane reseed's build.

On a clamp-free hybrid it is the other way round. The abi-46 retry stepped
every position, so an adaptive retry's attempts are a subset of those, in the
same order. A give-up can become an answer and never the reverse.

## The speed side

These are SCRATCH-tier numbers: Apple M1, gcc-16 `-O2`, load1 about 10. The
harness is `studies/hyb_reseed_cal/table.py`, with 5 launches × 5 passes and
the median of the per-launch medians. The subjects are
`studies/hyb_reseed_cal/subjects.py`'s `clamp_*` family: one unit, then G-1
filler bytes, repeated to 1 MiB.

The unit is a failing candidate: the prefilter accepts it and the pattern
does not. `new` was a lane build with the compact adaptive text and WITHOUT
the `clamped` row. To reproduce, delete that one row from
`pcrec_reseed_rows`.

`deny` is byte-identical to `base`, so base/deny is the noise floor. It reads
×0.99-×1.02 here. Every witness stamps `RX_VM_FRAMELESS 0` (framed: gap 4,
block 16, cap 64, first 2). No answer differed in any cell.

| witness | unit | G=1 | G=2 | G=4 | G=8 | G=16 | G=64 |
|---|---|---:|---:|---:|---:|---:|---:|
| `(?:aa\|a)*+ab` | `aab` | ×2.19 | ×1.81 | ×1.30 | ×0.98 | ×0.98 | ×0.97 |
| `(?<=a\|bc)[a-c]{2,4}d` | `xabd` | **×0.46** | ×0.97 | ×0.96 | ×0.98 | ×0.98 | ×1.00 |
| `x*(?>a\|ab)c\|abcd` | `abc` | ×1.75 | ×1.40 | ×1.00 | ×0.97 | ×0.98 | ×1.01 |
| `(?:a\|ab)++c` | `abc` | ×2.04 | ×1.74 | ×1.00 | ×1.01 | ×1.00 | ×1.00 |

(base/new: a value above 1 means the adaptive retry is faster. The raw rows
are in `studies/hyb_reseed_cal/results/clamped_2026-09-30.md`.)

What the table shows:

- **Three witnesses gain ×1.3-×2.2 when candidates are dense** (a candidate
  every 3-5 bytes). On sparser subjects they are flat within noise, because
  the adaptive retry then re-seeds exactly as the old one did.
- **One witness loses ×0.46 on its densest subject.** A step at a
  non-candidate position costs far more than the framed class's calibration
  assumes: a bounded counter and a lookbehind run on every stepped position.
  In the same cell a re-seed is cheap, because the prefilter's DFA is small.
  The per-class calibration prices this program's step wrongly.
- On a clamp-free hybrid that loss cannot happen against the old retry,
  which already stepped everywhere. It can happen only where the old retry
  re-seeded, which means only on a clamped hybrid.

## Decision

The adaptive row is not justified on clamped hybrids.

- The gain is mixed (×2.2 to ×0.46), on a population of synthetic
  test-corpus patterns (`tests/atomic_groups/possessive.rxt`,
  `tests/lookaround/d27/matrix.rxt` and the like).
- Its cost is a contract clause: answer → give-up.
- The general mechanism is the table, so the exclusion is a table row.
  `clamped` sits second, undeniable, with today's retry
  (`src/gen/emit_vm.c`, `tuning.md` §2.35).

Side effects:

- The adaptive text never meets a clamp window. The emitter's `window_end`
  arm for it is gone, and an internal-error guard replaces it.
- `tests/codegen/run_size_term.sh`'s cap-rescue witness
  `(?:aa|a){8,12}+b` is a clamped over-approximating hybrid, so it goes back
  to today's retry plus one stamp line (r1 chk F1; that script's
  2026-09-30 comment has the re-measure).

**What would re-open it:** a per-program step-cost estimate, which is the
×0.46 cell's mechanism. It would also tighten the clamp-free rows'
crossover. The plan row `[OPT-HYB-RESEED-XCALL]` sits next to it: both
replace a per-class constant with a better-informed choice. No trigger is
met today.
