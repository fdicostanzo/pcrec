# G2ROWS_REPORT — per-ROW floor for G2 ([MEMFN-ROWCON] N4 follow-up)

## Commands

    TMPDIR=<scratch> taskset -c 12-15 gnutimeout 1500 memfn/tests/run_g2.sh --quick --rows
    TMPDIR=<scratch> taskset -c 12-15 gnutimeout 1500 memfn/tests/run_g2.sh --quick --no-rows   # plain, for timing

`--rows` also works without `--quick` (full tier). `--quick` now implies `--rows`; `--no-rows` turns it off.

## What it does

With rows on, `lib` is `build/libpcrec_mftrace.a` for every process that calls the kit
and selects rows: the generator (`g2_gen`, run once for the base space and once per W2
mutation 1-7, 8 processes). Each process's stderr goes to its own file; the
`MFTRACE REACH table=T row=R chosen=N` lines are summed and printed as
`row-chosen T R N`. The driver and reference do not link the kit. K1 (`g2_k1`) calls
only `mf_ref_*`, selects nothing and prints no REACH line at all, so it is not one of the
(d) processes (it is still linked against the trace library, harmlessly).
Checks (all PASS:/FAIL:, counted into `checks passed/failed`):
(a) REACH_DROPPED total 0, one line per process; (b) no row with n == 0, each zero row named;
(c) distinct (table,row) pairs >= literal `FLOOR_ROWS=13` (measured 13); (d) every process printed REACH lines.
Controls run on every invocation: (d) a generator linked against the plain library must print
no REACH line; (b) a copy of the sums with one row zeroed must be named by the zero test.

## Output of `--quick --rows` (rows section)

```
== rows: kit selection-table rows chosen over the whole tier (MFTRACE REACH, summed)
PASS: (d) all 8 G2 kit processes printed REACH lines
PASS: (d) control: a generator linked against the plain library printed no REACH line, so (d) is red for it
row-chosen arms generic 190218
row-chosen arms ofsskip 22434
row-chosen arms pf_memchr 3674
row-chosen arms pf_memchr_bounded 3158
row-chosen arms pf_walk 4088
row-chosen arms pf_walk_bounded 3740
row-chosen arms precheck 2290
row-chosen arms precheck_assign 2490
row-chosen arms runcmp 19810
row-chosen runcmp bytes 16487
row-chosen runcmp memcmp 36299
row-chosen runcmp overlap 8084
row-chosen runcmp words 15412
PASS: (a) every REACH_DROPPED is 0 (8 lines)
PASS: (b) every row chosen >= 1 over the tier
PASS: (b) control: a file with row arms/generic zeroed is red for (b)
PASS: (c) 13 distinct (table,row) pairs >= floor 13
```

## Wall times (taskset -c 12-15, Linux dev box, shared)

- `--quick` plain: 145 s, 157 s
- `--quick --rows` (includes the (d) control generator run): 124 s, 175 s

Run-to-run noise (about 25 s) exceeds any difference; the mean cost is about 0. Under the
20 s bar, so `--quick` runs the rows half (opt out: `--no-rows`).

## Controls shown red (whole-tier runs of sabotaged copies of the script, since deleted)

(d): script copy linked against `libpcrec.a` instead of the trace library:
```
FAIL: (d) G2 kit process(es) printed no REACH line (wrong library linked?): gen-gen.err gen-mut1.err gen-mut2.err gen-mut3.err gen-mut4.err gen-mut5.err gen-mut6.err gen-mut7.err
PASS: (d) control: a generator linked against the plain library printed no REACH line, so (d) is red for it
FAIL: (a) REACH_DROPPED total 0 over 0 lines (8 processes)
FAIL: (b) control: a zeroed row was not named
FAIL: (c) 0 distinct (table,row) pairs < floor 13
```
(b): script copy that zeroes the third row after summing:
```
FAIL: (b) rows never chosen: arms/pf_memchr 
PASS: (b) control: a file with row arms/generic arms/pf_memchr zeroed is red for (b)
```
(Note in the (d)-red run, (a) and (c) go red too; (b) alone stays PASS on an empty
file, which is (c)'s job.)

## Questions

- Q-G2R-1: `--quick` now requires `build/libpcrec_mftrace.a`. The cell has it; does the
  pcrec Makefile build it before `make test-memfn-g2`? If not, `--quick` exits 2 with the
  missing-library message until it does (or run with `--no-rows`).
- Q-G2R-2: `FLOOR_ROWS=13` is the registry as measured today (arms 9, runcmp 4); the
  trace_format note says the registry holds 16 counter slots. A new row raises the
  measured count, not the floor, until someone raises the literal: intended ("raise
  floors when the space grows")?
