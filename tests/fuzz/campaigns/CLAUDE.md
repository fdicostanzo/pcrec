# tests/fuzz/campaigns — at-scale differential campaign logs

Committed logs from many-seed, many-thousand-pattern `fuzz.py` runs
(`tests/fuzz/`'s manual/checkpoint instrument — see the parent directory's
README.md "Two-tier posture" section). One file per campaign, D35-style
provenance header (date, HEAD commit at run time, libpcre2 version, gcc
version, host, seed list) plus per-seed and aggregate statistics tables.

**Evidence, never an oracle** — same rule as `docs/measurements/`: no check
reads these files. `tests/fuzz/run_capturediff_gate.sh` (`make
test-capturediff`) is the live, re-measured regression instrument; a
campaign log here only records that a specific, larger sweep was run once
and found what it found. A stale campaign log does not fail any build.

**Raw per-pattern logs are not committed** (regenerable byte-for-byte from
the file's own recorded seed list and parameters — `fuzz.py`'s generation
is fully deterministic per seed) — only the extracted tables and any
finding worth keeping. If a campaign DOES turn up a real divergence, its
repro bundle belongs in `tests/fuzz/failures/` (see the parent README's
"Triaging a divergence"), not here; this directory is for the aggregate
record of a clean (or triaged) sweep.

## Files

- **2026-08-17_m47e_capture_diff.md** — [M4.7e]'s at-scale capture-span
  differential: 25 seeds (101-125), 3,000 patterns x 20 subjects each,
  75,000 patterns total, 0 accept/reject and 0 content divergences.
  Includes the measured finding that the differential gate, though open
  (`PCREC_DEFAULT_FEATURES="std1"`), is currently vacuous for this
  generator — no classes-module or modifiers-module syntax is ever
  generated (a generator coverage gap, not a gate failure).

Maintenance: add a file per campaign; update this list when one is added.
