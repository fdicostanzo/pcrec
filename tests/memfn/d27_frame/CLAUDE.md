# tests/memfn/d27_frame — D27 spec-first tests of 3.0b's seam contract

Tests of `mf_wdecide`'s framed phase-1 ask (MF_SITE_ABI 28) written from the
PROMISE only: `docs/design/memfn/plan_frame.md` §2.1-§2.3 (the contract lines
of §2.2, its Purity paragraph, §2.3's tables and observable-meaning column),
`window_site.md`'s facts and `memfn/include/memfn.h`. The author (D27, lane
s1owed-d27) had no access to `memfn/src`, `src/` or `tests/`; the sites come
from the driver's own generator. Adopted into the tree by lane d27fix
(2026-11-13), which fixed the kit for the author's findings F1-F4 and wrote
the spec text for F5 and A1-A7 as the kit manager ruled them; findings,
rulings and populations: `docs/dev/lanes/d27fix_report.md` (the author's own
report never reached the tree).

## Files

| file | role |
|---|---|
| `run.sh` | entry point: builds the driver against `build/libpcrec.a` and `build/libpcrec_mftrace.a`, runs seeds 1-3 (plain) and seed 1 (traced) per compiler variant, sums the verdicts |
| `d27_frame.c` | the driver: generator, the five fixed witnesses, every check (each cites its contract sentence), populations and floors, the control switch |
| `cases/floors.tsv` | population floors (K35): measured least count over seeds 1-3 x 20000 cases, less ~10%; `traced:` rows apply to the traced kit only |
| `cases/witnesses.tsv` | the minimal witness of each finding, in plain words (the driver's `fixed_case`); since d27fix every witness holds |

## Running

    make test-memfn-d27frame                             # quick tier + control + empty (make test section)
    make test-memfn-d27frame-full                        # gcc, clang, gcc ASan+UBSan (opt-in)
    bash tests/memfn/d27_frame/run.sh                    # the full tier alone
    D27_QUICK=1 bash tests/memfn/d27_frame/run.sh        # gcc -O2 only
    D27_CONTROL=1 D27_QUICK=1 bash tests/memfn/d27_frame/run.sh   # MUST exit nonzero
    D27_EMPTY=1 D27_QUICK=1 bash tests/memfn/d27_frame/run.sh     # MUST exit nonzero

`tests/memfn/run_d27_frame.sh` is the make section: the suite's verdict and a
passes floor, then the control (every family red in all four runs, none
silent) and the empty run (floors broken in all four). Runtimes on the dev box
(7700X): quick tier ~15 s of driver time, the section ~1 min with its two
controls; full tier ~1m40s. Serial: one driver process at a time.

Outputs go to `$D27_OUT`, else a fresh `d27frame.XXXXXX` under `$TMPDIR`
(the pcrec temp root when TMPDIR is unset or under /tmp). Every step runs
under GNU timeout. Last lines `checks passed: N` / `checks failed: M`;
exit 0 iff M == 0 and every floor held.
Driver alone: `d27_frame SEED NCASES FLOORS OUTDIR [traced]`;
`D27_DUMP=<case>` prints that case's replies, text and trace (`-N`: the
fixed witnesses 1..N); `D27_VERBOSE=1` prints every EMIT-parity and use
refusal. The floors were measured at 20000 cases.

## Driver changes since adoption (each a ruling's reading; lane d27fix)

| change | ruling |
|---|---|
| `rule_plan_test`: on E-find a shared-`plan_term` position may answer OWN (a run compare); the text checks hold which | F4 |
| `obs_plan_test_own_text`: an OWN stop offset whose offer the find reads (that read is `stop_test`'s), and one D-hors probe offset, are not OWN-but-read | F4 (and A4) |
| populations: `plan_test_TABLE_in_run_compare` renamed `_shared_term`; `plan_test_OWN_offered_in_run_compare` new; floors re-measured (floors.tsv header) | F4 |
| `no_fenced_defect_refusal`: no define or emit refuses through the run ranking's invariant | F1 |
| `facts_at`: on a PARKED alternative the reply did not re-seed, the tested set is the verify-YES spans' meet | none: N1, the adopting lane's reading, for the kit manager to rule |
