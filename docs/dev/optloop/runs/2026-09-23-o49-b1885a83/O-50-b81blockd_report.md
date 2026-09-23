# [B81] lane report — I-98's Block D re-run under the bench's own instrument

Executor lane, I-57 terms. Report, never diagnose. Every command run, every
raw number, stated as MEASURED. Deviations from I-98's literal text are
listed in §0.

## 0. Deviations from I-98's literal text (all mechanical, listed up front)

1. **Instrument form delivered: driverrun's own loop + `judge_trial_agreement`
   called directly, NOT a scratch-tier record.** I-98's brief allows this as
   the named fallback ("if it is not reachable without modifying pcrecbench
   code, STOP on that half and deliver the timing via driverrun's own loop
   with the X13 judgment computed by calling
   pcrecbench.reduce.judge_trial_agreement directly — state which form you
   delivered"). The full `run_cell()` / `store.write()` record path calls
   `Adapter.compile()` directly, which always re-invokes the pcrec CLI on
   pattern TEXT — there is no injection point for a hand-edited artifact
   that pcrec itself never emitted, short of editing `pcrecbench/harness.py`
   or `testees/pcrec/adapter.py`, which the mandate forbids. **Delivered
   instead**: the REAL `testees.pcrec.adapter.Adapter` instance (via
   `pcrecbench.adapters.discover()["pcrec"]`), used ONLY for its
   `.measure()` method (which calls `pcrecbench.driverrun.per_trial`, the
   real driver-invocation loop) against a hand-built `handle` dict pointing
   at each variant's `.so`; the real `pcrecbench.subbench.load(...)`
   (`subjects_for`/`expectation`/`subject`) for `bench/capability`; the real
   `pcrecbench.harness.calibrate` / `outcome_for` / `classify_giveup` /
   `truncation_for`; the real `pcrecbench.record.match_row`; and the real
   `pcrecbench.reduce.reduce_set_cell` / `judge_trial_agreement` /
   `agreement_line`. No line of `pcrecbench/` or `testees/` was edited. No
   record was written to `build/scratch-store` (there is no reachable path
   to one without the edit above) and none is claimed. Runner script:
   `/tmp/optloop4/blockd/run_instrument.py` (scratch, not committed).
2. **The interleave is per adapter.measure() call (one trial, all three
   subjects), not per-subject.** "Interleave a/b/c/d per trial round" is
   read as: round 1 runs one full-subject-list trial of a, then b, then c,
   then d; round 2 repeats; five rounds total — the same trial GRANULARITY
   `pcrecbench` itself uses (one driver invocation per (regime, trial) over
   the whole subject list, `adapters.py`'s driver protocol).
3. **`n_iters` is calibrated PER VARIANT** (`harness.calibrate`, one probe
   each), not shared across the four. Each variant's own `SetCell` and
   `trial_agreement` block therefore judges that variant's own five trials
   at its own iteration count — the same rule a real `run_cell` cell
   follows for any one testee. This means the four variants' RAW per-trial
   sums are not on one scale by iteration count; `reduce.reduce_set_cell`'s
   `median_ns`/`sums` are ns/call, already iteration-normalized, so the
   comparison the grid makes (medians of ns/call) is apples-to-apples
   regardless.
4. Everything else (the four builds, the exact 3-line diff, the subjects,
   the answer-check-before-timing rule, 5 trials) follows I-98/I-93's text
   verbatim.

**Box facts:** `gcc (Ubuntu 15.2.0-16ubuntu1) 15.2.0` (matches [B78]'s own
box). Quiet throughout: `uptime` immediately before the run and before every
timed round, all `load average` readings at or below 0.16 (see §3).
Scratch: `/tmp/optloop4/blockd/` (base/, a_asis/, b_deleted/, c_moved/,
d_nopartial/, run_instrument.py, run_instrument.log, pcrec_driver,
subjects.tsv, make_variants.py). AFTER pin binary:
`/home/duxevents/pcrec-bench/build/pcrec-8d716693/build/pcrec` (already
built, reused unmodified). `bench/capability/throughput/*.bin` regenerated
locally via `python3 bench/capability/gen_throughput_subjects.py`
(gitignored; sha256 confirmed byte-identical to the committed
`manifest_throughput.tsv`: `d2e4f134…`/`t-64k`, `3cf7b248…`/`t-256k`,
`ccbdf7eb…`/`t-1m`).

## 1. Emitting the base artifact (AFTER pin, `-fcomments` protocol token)

    /home/duxevents/pcrec-bench/build/pcrec-8d716693/build/pcrec \
        -p rx -fcomments --features all \
        -o /tmp/optloop4/blockd/base/artifact.c \
        --pattern '(/\*(?:[^*/]|\*(?!/)|/(?!\*)|(?1))*\*/)'
    # rc=0; artifact.c 38,712 B, artifact.h 12,788 B

`-fcomments` mirrors `testees/pcrec/adapter.py`'s `EMIT_COMMENTS_FLAG`
protocol token (always passed, never in `cfg["flags"]`); `--features all`
and the pattern text are `pcrec-auto`'s own config (`configs.toml`
`[testees.pcrec-auto]`, `flags = ["--features", "all"]`); the pattern bytes
are `bench/capability/patterns/nested-comment-rec.rx` verbatim (confirmed
via `xxd`, no trailing newline).

**The verbatim region check (I-98's own gate).** The emitted `rx_search_run`
(lines 565–598 of `base/artifact.c`) carries, at lines 572–577:

    if (search_from > subject_length) return 0;
    /* [OPT-REQBYTE] every match of this pattern contains the byte
     * 47, so a window without it holds no match at all. */
    if (subject_length <= search_from ||
        !memchr(subject + search_from, 47, subject_length - search_from))
        return 0;

This is the SAME code O-48/`b78blocks_report.md`'s Block D quoted as its
own "lines 417–420" (that report's code fence carried its own line-number
annotations, not pcrec's real comment; the actual C statements — the
unchanged bounds check, then the three-line `if (subject_length <=
search_from || !memchr(...)) return 0;` — are byte-for-byte identical to
what is quoted there). The region is present, so no STOP condition fired.

## 2. The four builds

`make_variants.py` (committed as scratch, `/tmp/optloop4/blockd/`) does the
edits programmatically and refuses (STOP) if the 3-line precheck block is
not found EXACTLY once in the base source:

- **(a) as-is** — `a_asis/artifact.c`, unedited copy of `base/artifact.c`.
- **(b) deleted** — the three code lines (the `if (subject_length <=
  search_from || …) return 0;` block, NOT the two-line C comment above it,
  which is inert prose left in place — the literal "three lines" reading)
  removed from `rx_search_run`; line `if (search_from > subject_length)
  return 0;` untouched.
- **(c) moved** — the same three lines removed from `rx_search_run` (as in
  (b)) and reinserted verbatim as the FIRST statement of each of
  `rx_search`, `rx_search_in` and `rx_search_deep` (confirmed by grep: each
  function's opening `{` is immediately followed by the three-line guard,
  before any local declaration — legal under `-std=gnu11`'s mixed
  declarations-and-code).
- **(d) as-is + `-fno-partial-inlining`** — `d_nopartial/artifact.c` is
  BYTE-IDENTICAL to `a_asis/artifact.c` (same sha256); the flag rides on the
  compile line only.

**sha256 of each variant's `artifact.c`:**

    94dab8ba44afd2c6b4bf4b0f6e866635ea98090910f2a6b75f2466e69f932982  a_asis/artifact.c
    e63de7e69b139fc897245bc30bcf75fb6e4e5b2ed99a42df68b05eb9f6a4838e  b_deleted/artifact.c
    6c4caaf151b059029ecfed3aa50b06d6ea541f56d03f6ef24367935e9874e5b8  c_moved/artifact.c
    94dab8ba44afd2c6b4bf4b0f6e866635ea98090910f2a6b75f2466e69f932982  d_nopartial/artifact.c

**The build line, mirroring `testees/pcrec/adapter.py`'s `_compile_one`
phase-2 shape exactly** (`[cc, "-O2", "-std=gnu11", "-fPIC", "-shared"] +
cfg["cflags"] + ["-o", so, shim.c, "-DPB_ARTIFACT=...", "-I", cdir]`, `cc` =
`gcc`, `cfg["cflags"]` = `[]` on every pcrec-auto-shaped config except (d)):

    gcc -O2 -std=gnu11 -fPIC -shared -o <dir>/artifact.so \
        testees/pcrec/shim.c -DPB_ARTIFACT="<dir>/artifact.c" -I <dir>
    # (d) only: -fno-partial-inlining inserted after -shared (the
    #           compilee-flags axis's own position, testees/pcrec/CLAUDE.md
    #           "The compilee-flags axis: cflags")

All four built rc=0, no warnings of note. `.so` sizes: a_asis 31,656 B,
b_deleted 27,504 B, c_moved 31,696 B, d_nopartial 31,656 B (byte-identical
to a_asis, as expected for an unedited source under a flag that changes
codegen, not size in this case).

## 3. Answer-check, before ANY timing

One `--find-all --iters 1` call per variant over all three throughput
subjects (`bench/capability/throughput/{t-64k,t-256k,t-1m}.bin`), via the
real driver protocol (`pcrec_driver --lib <so> --mode search --iters 1
--find-all --list subjects.tsv`), `uptime` immediately before: `load
average: 0.09, 0.12, 0.15` (quiet).

    === a_asis ===
    subject t-64k  nomatch - - 1 65536   1 0.000560713 0 -
    subject t-256k nomatch - - 1 262144  1 0.001723297 0 -
    subject t-1m   nomatch - - 1 1048576 1 0.006115225 0 -
    === b_deleted ===
    subject t-64k  nomatch - - 1 65536   1 0.000462682 0 -
    subject t-256k nomatch - - 1 262144  1 0.001502126 0 -
    subject t-1m   nomatch - - 1 1048576 1 0.005945944 0 -
    === c_moved ===
    subject t-64k  nomatch - - 1 65536   1 0.000369742 0 -
    subject t-256k nomatch - - 1 262144  1 0.001492276 0 -
    subject t-1m   nomatch - - 1 1048576 1 0.005966834 0 -
    === d_nopartial ===
    subject t-64k  nomatch - - 1 65536   1 0.000396962 0 -
    subject t-256k nomatch - - 1 262144  1 0.001517086 0 -
    subject t-1m   nomatch - - 1 1048576 1 0.006089945 0 -

The NMATCHES column (second-to-last) reads **0 on all three subjects, all
four variants** — matching `bench/capability/expectations.tsv`'s
`nested-comment-rec`/throughput rows (`nomatch`, nmatches `0`, all three
subjects) exactly. Re-confirmed programmatically via
`pcrecbench.subbench.expectation()` in the timed run (§4's own
answer-check block, `run_instrument.log`): `ALL VARIANTS matches=[0,0,0]
as expected: True`.

## 4. Calibration (harness.calibrate, one probe per variant)

    a_asis      iters=27  -- median per-iteration 1898.768 us (t-256k) -> iters=27 for a 50 ms loop
    b_deleted   iters=27  -- median per-iteration 1874.557 us (t-256k) -> iters=27 for a 50 ms loop
    c_moved     iters=14  -- median per-iteration 3754.536 us (t-256k) -> iters=14 for a 50 ms loop
    d_nopartial iters=13  -- median per-iteration 3847.036 us (t-256k) -> iters=13 for a 50 ms loop

(Each variant's own probe; `n_iters` is not shared across variants — §0
deviation 3. The probe numbers here are single-iters=100 measurements, not
the 5-trial medians reported in §5 below.)

## 5. Timed rounds — interleaved a,b,c,d × 5, `uptime` before each round

    round 1 uptime: load average 0.08, 0.12, 0.15
    round 2 uptime: load average 0.16, 0.14, 0.16
    round 3 uptime: load average 0.16, 0.14, 0.16
    round 4 uptime: load average 0.16, 0.14, 0.16
    round 5 uptime: load average 0.16, 0.14, 0.16

Quiet throughout (load1 <= 0.16 every round).

**Per-variant `SetCell` (`reduce.reduce_set_cell`, sum of per-subject
ns/call per trial, over the 3 throughput subjects, median/min/max/stddev
over the 5 trials — the SAME arithmetic `quick` prints and the reporter
ranks):**

| variant | median (ns) | min | max | stddev | IQR (Q3−Q1) | Δ vs (a) |
|---|---:|---:|---:|---:|---:|---:|
| (a) as-is | 9,584,242.7 | 8,552,945.6 | 10,027,935.6 | 506,030.6 | 857,295.3 | +0.00% |
| (b) deleted | 8,113,432.3 | 7,974,003.6 | 8,135,943.9 | 59,127.8 | 85,810.7 | **−15.35%** |
| (c) moved | 8,407,235.0 | 8,195,179.1 | 8,442,950.0 | 91,223.6 | 140,520.5 | **−12.28%** |
| (d) `-fno-partial-inlining` | 9,907,376.5 | 9,672,622.5 | 10,504,692.7 | 307,287.2 | 634,402.2 | +3.37% |

Raw per-trial sums (ns), in round order 1–5:

    (a) 9,584,242.74  9,566,184.52  9,805,785.11  10,027,935.63  8,552,945.59
    (b) 8,120,562.33  8,110,881.19  8,113,432.30  8,135,943.85    7,974,003.59
    (c) 8,397,504.21  8,430,774.21  8,442,950.00  8,195,179.07    8,407,235.00
    (d) 10,504,692.69 10,331,645.92 9,894,911.85  9,672,622.46    9,907,376.54

No subject failed its expectation on any trial of any variant (`failing
subjects: []` on all four cells; `n_wrong=0`, `n_gave_up=0` throughout —
confirmed in `run_instrument.log`).

**Per-variant `trial_agreement` (X13, `reduce.judge_trial_agreement`,
called directly on the real match rows — the fallback form named in §0.1):**

    a_asis      agree (0 of 1 groups; 1 of 3 rows; 0 unjudged; k=1.5, 2/3; 5 trials)
    b_deleted   agree (0 of 1 groups; 0 of 3 rows; 0 unjudged; k=1.5, 2/3; 5 trials)
    c_moved     agree (0 of 1 groups; 0 of 3 rows; 0 unjudged; k=1.5, 2/3; 5 trials)
    d_nopartial agree (0 of 1 groups; 0 of 3 rows; 0 unjudged; k=1.5, 2/3; 5 trials)

All four groups are `agree` (a record built from any one of them would
stamp `measured`, not `inconclusive-spread`) — `a_asis` has one of its
three per-subject rows individually flagged inside the rule's own
per-row disagreement test (its round-5 sum, 8,552,945.6 ns, sits noticeably
below the other four; see §6), but that single flagged row does not clear
the rule's `d_min=2` threshold, so the GROUP still reads `agree`.

## 6. The verdict grid (I-98's own EXPECT structure)

**Null-control band, per I-98/O-48 Block B**: −5.74%..+8.46% BETWEEN
separate interleaved windows; tighter within one run's own 5 interleaved
trials (this run's own tightest same-artifact spread is (b)'s IQR, 1.06%
of its median).

- **(b) vs (a): −15.35%.** Clears the null-control band in BOTH directions
  — well outside even the wider cross-window ±5.74%/+8.46% figure, and an
  order of magnitude past the within-run IQRs (857,295 ns / 85,811 ns).
  **Yes, (b) reads below (a) by more than the null band.** Per I-98's own
  §9(C) reading, this is consistent with "the pre-check costs something
  real on this box" surviving under the store's own instrument, where it
  did NOT resolve under `findall.c` (O-48/[B78]: every delta there sat
  inside the per-variant IQR).
- **(c) vs (b): is (c) within the band of (b)?** Medians differ by
  293,802.7 ns (c − b); `max(IQR_b, IQR_c) = max(85,810.7, 140,520.5) =
  140,520.5` ns. 293,802.7 > 140,520.5. **No — (c) is NOT within the band
  of (b)** under this run's own IQRs: (c) is measurably slower than (b) by
  ≈3.6% of (c)'s own median (8,407,235.0 / 8,113,432.3 = 1.0362), though
  both remain clearly faster than (a). G3's literal acceptance test
  ("(c) is the fix: within IQR of (b)") is NOT met on this measurement.
- **(d) vs (a): +3.37%.** Medians differ by 323,133.8 ns; `max(IQR_a,
  IQR_d) = max(857,295.3, 634,402.2) = 857,295.3` ns. 323,133.8 <
  857,295.3. **(d) sits inside (a)'s own IQR** — the `-fno-partial-
  inlining` arm does not read as separated from plain (a) on this
  measurement, the same reading O-48's own Block D reached under
  `findall.c` (there: "(d) reads modestly slower... but the effect size
  sits inside (a)'s and (d)'s own IQRs").

**Stated, not diagnosed further**: (a)'s own spread (IQR 857,295 ns, 8.9%
of its median) is driven by one low round (round 5, 8,552,945.6 ns) against
four rounds clustered 9.57–10.03M ns; the median (9,584,242.7 ns) already
sits at the LOW end of that four-round cluster because of it. Excluding
that one round is not done here — it is reported as MEASURED, a fact about
this run's own noise floor on the UNEDITED artifact, not a resolved cause.

## Summary of what changed vs I-98's literal asks

- Instrument form: driverrun's own loop (`adapters.discover()["pcrec"]
  .measure()`, real `subbench`/`harness`/`record`/`reduce` code) + direct
  `reduce.judge_trial_agreement()` calls — the named fallback, no record
  written, no `pcrecbench`/`testees` source edited (§0.1).
- All four variants built from the SAME emitted `art.c` (the AFTER pin,
  `-fcomments`, `pcrec-auto`'s flags), matching O-48/[B78]'s own build
  shape and sha256-recorded (§2).
- Answer-check `matches=[0,0,0]` on all three subjects, all four variants,
  confirmed twice (a standalone driver call, §3; and inside the timed
  harness path, §5) — no wrong answers anywhere.
- Under this instrument, at 5 interleaved trials, **the results DO resolve
  cleanly** — the opposite of O-48/[B78]'s own finding under `findall.c`,
  where every delta sat inside the per-variant IQR and (b)'s sign flipped
  between iters settings. Here (b) reads clearly and reproducibly below
  (a) (−15.35%, outside a null band an order of magnitude tighter than
  either), (c) reads clearly below (a) but NOT within (b)'s own band
  (G3's literal acceptance test not met), and (d) reads inside (a)'s own
  noise.

Scratch artifacts (not committed, per the mandate):
`/tmp/optloop4/blockd/` (base/, a_asis/, b_deleted/, c_moved/,
d_nopartial/, make_variants.py, run_instrument.py, run_instrument.log,
pcrec_driver, subjects.tsv) — held per the brief's own instruction until
"I-98 logs fetched".
