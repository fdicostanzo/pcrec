# A2 bake-off round 1 — Linux, 2026-10-03

## Provenance

- **Box.** ubuntubudu (AMD Ryzen 5 1600), pinned `taskset -c 2`. The run
  started 2026-10-03T20:52:52Z at load 0.07 / 2.73 / 4.77 and stopped at
  21:02:58Z. Compilers: gcc 15.2.0 (Ubuntu 15.2.0-16ubuntu1) and clang
  21.1.8 (6ubuntu1), both `-O2`. 15 launches per binary, round-robin, each
  the median of 7 passes, every pass calibrated to at least 50 ms on the
  deny.
- **Pack.** Built 2026-10-03T20:10Z on the Mac by lane rsform's `prep.sh`.
  The new compiler is `bea57c8c` (A1, abi 56) and the base is main
  `1f244692` (abi 55). The pack's `bakeoff.sh` was a working-tree copy
  that differs from the committed one (`fbf6bb2c`) on line 66.
- **Where it ran.** The manager ran it in
  `/home/duxevents/pcrec/scratch_lx/bakeoff/rsform_bakeoff/` on the Linux
  box. Lane a2build fetched `work/` read-only with `scp`.

## What stopped it

The pack's line 66 was:

    label="$id/$mode:$(basename "${files[0]}" .bin)$([ ${#files[@]} -gt 1 ] && echo "+...")"

On a row with ONE subject file, `[ 1 -gt 1 ]` returns 1. That makes the
command substitution return 1, so the assignment returns 1, and `set -e`
ends the script. Every row before `lbvar` has several subjects
(`subj/*.bin` is 42 files, `thr/*.bin` is 3). The first single-subject row
is `lbvar f cal/synth-dense.bin`. So the run timed the 10 cell rows above
it on both compilers, 20 (row, compiler) rows in all, and stopped before
the table step.

These 10 cells x 2 compilers were **never timed**:
- `lbvar` (4 rows);
- `lbfix` (4 rows);
- `lbneg` (1 row);
- `lpatom` (A1's cell, 1 row).

The utf8 calibration witnesses and A1's own cell are therefore
UNMEASURED in round 1. It was not, as first read, a crash after the last
timing.

The committed kit already had `|| true` on that line, so the kit at
`fbf6bb2c` would not have stopped. The defect was the pack carrying an
uncommitted script. Lane a2build's fixes:
- `prep.sh` refuses a dirty kit and records each copied script's sha256 in
  `MANIFEST`.
- The label is computed with no failing substitution.
- An ERR trap names the stopping line.
- An EXIT trap renders whatever `raw.tsv` holds, with a `NOT TIMED` list.

## Files

- `header` — the run's own header lines.
- `raw.tsv` — 3,000 launches: 20 rows x 10 variants x 15. sha256
  `f8acf199b2f29059bebe5a6577f0da30e261e866b18c887eb4d834cbfbeb73f1`.
- `table_manager.txt` — the table the manager rebuilt by running the
  script's embedded table code over `raw.tsv`. Its `floor` column is
  `max(|d2/d-1|, |dL/d-1|)`, and its footer's "worst" is the largest
  form/d.
- `table.txt` — the same raw file rendered by the kit's new `table.py`. It
  shows the launch and layout floors apart, marks the two clang lkapos and
  lkaverb f rows UNMEASURED, and lists the rows NOT TIMED. The ratios are
  identical to `table_manager.txt`.
- `deltas.txt` — `deltas.py`: every row as absolute deltas against the
  deny. Short-search rows are in ns per call (the raw sum divided by 42
  subjects). Find-all rows are in us per pass.

## The 31.5% clang keep floor

On clang lkapos/f and lkaverb/f:
- `d2` reads within 0.15 us of `d`, so the launch floor is 0.0%.
- `dL`, the deny re-linked in the other order, reads 866 us against `d`'s
  1,264 us on every one of its 15 launches. That is a 31.5% DETERMINISTIC
  layout effect, not noise.
- The keep comparison is form against `a` (all near 0.41 of `d`). A
  31.5% allowance makes it vacuous, so those two rows are UNMEASURED.

What settles them is a re-run that measures `a`'s own layout spread. The
`aL` variant (`a` re-linked) does this, and round 2 carries it, so the
keep allowance becomes `max(launch, |aL/a-1|)`. Ideally the chosen form
gets a re-linked copy too. More launches would not help, because the
launch spread is already 0.1%.
