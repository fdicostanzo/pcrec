# tests/findings/witness/ — the reader WITNESSES ([FINDINGS] B2, design §11.9)

One constructed pattern + one named bundle per rate reader C1-C4 (C2 split
into its scan member C2a and its window C2b), whose choice MOVES against the
default. `C6` is B4's.

## Files

- `witness.tsv` — one row per witness: bundle, reader, the reader's stamp,
  the pattern, the stamp's pinned value under the DEFAULT and its pinned
  value under the bundle. Both are pinned: a witness that stops reaching its
  site is red on the first, a reader that stops reading the rate on the
  second. Run by `../gen_adversarial.py witness` (`run_findings_tests.sh` §8).
- `w-c1.rxt` … `w-c4.rxt` — the witness bundles: every byte 1000 and ONE byte
  1, hand-constructed, each file's header naming the byte and the reader.
  (`w-c3`'s flip is G1's IDENTITY conjunct — the rate moves the scan byte
  onto the necessary byte — because the DENSITY conjunct alone fires only on
  a tie or a scanned byte outside the necessary set, a population this
  design names and `run_prechecks.sh` covers.)

Maintenance: update this file when files are added/removed or their roles
change.
