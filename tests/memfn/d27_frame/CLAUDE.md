# tests/memfn/d27_frame — D27 spec-first tests of 3.0b's seam contract

Tests of `mf_wdecide`'s framed phase-1 ask (MF_SITE_ABI 28) written from the
PROMISE only: `docs/design/memfn/plan_frame.md` §2.1-§2.3 (the contract lines
of §2.2, its Purity paragraph, §2.3's tables and observable-meaning column),
`window_site.md`'s facts and `memfn/include/memfn.h`. The author (D27, lane
s1owed-d27) had no access to `memfn/src`, `src/` or `tests/`; the sites come
from the driver's own generator. Findings, ambiguities, populations and the
control result: REPORT.md (its text is in the lane's reply: the harness
refused the author writing it; the manager places it).

## Files

| file | role |
|---|---|
| `run.sh` | entry point: builds the driver against `build/libpcrec.a` and `build/libpcrec_mftrace.a`, runs seeds 1-3 (plain) and seed 1 (traced) per compiler variant, sums the verdicts |
| `d27_frame.c` | the driver: generator, the five fixed witnesses, every check (each cites its contract sentence), populations and floors, the control switch |
| `cases/floors.tsv` | population floors (K35): measured least count over seeds 1-3 x 20000 cases, less ~10%; `traced:` rows apply to the traced kit only |
| `cases/witnesses.tsv` | the minimal witness of each finding, in plain words (the driver's `fixed_case`) |
| `REPORT.md` | (placed by the manager from the lane's reply) which sentence each check holds, populations, control result, findings, ambiguities, disclosure |

## Running

    bash tests/memfn/d27_frame/run.sh                    # gcc, clang, gcc ASan+UBSan
    D27_QUICK=1 bash tests/memfn/d27_frame/run.sh        # gcc -O2 only
    D27_CONTROL=1 D27_QUICK=1 bash tests/memfn/d27_frame/run.sh   # MUST exit nonzero
    D27_EMPTY=1 D27_QUICK=1 bash tests/memfn/d27_frame/run.sh     # MUST exit nonzero

Outputs go to `$D27_OUT`, else a fresh `d27frame.XXXXXX` under `$TMPDIR`
(the pcrec temp root when TMPDIR is unset or under /tmp). Every step runs
under GNU timeout (`$TIMEOUT_BIN`, else `gnutimeout`, else `timeout`,
checked to be GNU). Last lines `checks passed: N` / `checks failed: M`;
exit 0 iff M == 0 and every floor held. A default run takes ~3 minutes.

Driver alone: `d27_frame SEED NCASES FLOORS OUTDIR [traced]`;
`D27_DUMP=<case>` prints that case's replies, text and trace;
`D27_VERBOSE=1` prints every EMIT-parity and use refusal.
The floors were measured at 20000 cases; `D27_CASES` changes the count
for development only (run.sh warns).
