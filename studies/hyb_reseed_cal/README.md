# [OPT-HYB-RESEED] calibration harness

SCRATCH TIER. Every number this produces is directional on the machine it
ran on. The bench's x86 runs decide magnitudes.

## Setup

```sh
# 1. The branch-point compiler (abi 46), from git archive, never a checkout:
mkdir -p /tmp/rsbase && git -C "$REPO" archive 23645945 | tar -x -C /tmp/rsbase
make -C /tmp/rsbase -j2 CC=gcc-16
export PCREC_BASE=/tmp/rsbase/build/pcrec
# 2. The compiler under test:
export PCREC_NEW="$REPO/build/pcrec"
# 3. Subjects (about 60 MiB):
python3 subjects.py /tmp/rssubj
```

## The tables

- **Crossover (design §3).** Run
  `xover.sh NAME PATTERN ENC UNIT` in a scratch directory. UNIT is a
  python expression of `g` giving the repeating unit, for example
  `"b'y'*(g-1)+b'x'"`. It prints the step/always-re-seed ns-per-byte ratio
  at g = 1..32; the crossover is where it passes 1. It needs only
  `PCREC_BASE`.
- **base / new / deny (`docs/dev/reseed/timing_mac.md`).** Run
  `table.py NAME PATTERN ENC /tmp/rssubj/<subject>.bin ...`.
  `LAUNCHES` and `REPS` set the sampling (default 5 × 5). Read the
  base/deny column before the base/new one.
- **Clamped (`docs/dev/reseed/clamped.md`).** Use `table.py` on the
  `clamp_*` subjects with a `PCREC_NEW` built with the `clamped` row deleted
  from `pcrec_reseed_rows`. With the row in place, the new and deny columns
  are both today's retry.

## Caveats

- `drv.c` takes its median inside ONE process. `table.py` launches each
  binary `LAUNCHES` times and takes the median of medians. That samples the
  per-process layout lottery (plan row I-114's caveat); it does not control
  it.
- The `lka_*` subjects are seeded word streams. Lane reseed's originals
  came from an earlier seed, so its lka rows are the same recipe in a
  different realization, and they differ materially: ×0.94 there, ×0.62
  here, on the same compiler.
