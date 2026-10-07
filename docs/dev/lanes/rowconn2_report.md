# Lane rowconn2 -- [MEMFN-ROWCON] N2: the would-decline census (script only)

Branch `lane/rowconn2` from `lane/memfn-rowcon` 529659ac. The full sweep was
NOT run; the kit manager launches it in a slot.

## Files (docs/design/memfn/probes/rowcon/)

- `n2_census.sh`: the lock (poll 60 s for `worktrees/.mac-suite.lock`, mkdir,
  `owner` file, release by trap), the `-DMF_TRACE` build into `$OUT/tb`, the
  driver, the report, the final line.
- `n2_census.py`: arms from `pcrec --list-axes` (cli_flag column, deny and
  force spellings, `a|b` and `a / b` split; the `-fcomments` pair is the tier,
  as in I2) + null + the four `--tune` aliases + any `--memfn=` spelling of the
  memfn section (none yet) = 107 arms: 52 each at base "" and `-fcomments`,
  plus the null arm and the utf8-scoped denies (bits 16/30/31/32/44/45/46,
  -fno-lit-run) at `-e utf8`. Per arm: distinct corpus patterns (3,621) at
  the default engine and `--engine=vm`, and the 370 `.rxt`/`.rxtin`
  composition files. Reuses `scripts/emit_sweep.py` (`enumerate_corpus`,
  `distinct_patterns`, `find_files`, `run`); emit_sweep itself is unchanged.
  emit-ir and facts emit no C, so they are not driven.
- `n2_report.py`: `parse_trace` + `Agg` + `render`; CLI merges `arm_*.json`.

## Launch

    cd /Users/fdicostanzo/pcrec/worktrees/rowconn2
    nohup caffeinate -s bash docs/design/memfn/probes/rowcon/n2_census.sh \
        > build/scratch/n2_full.log 2>&1 & disown

Env: `OUT` (default `build/scratch/n2_<stamp>`; re-running with the same OUT
resumes), `JOBS` (8), `CC` (gcc-16). Completion line, exactly one, last:
`== N2 DONE rc=N would_decline=K ==` (rc 0 ok, 1 driver failed, 2 build failed,
3 report failed). Results: `$OUT/n2_results.md`.

## Wall estimate (Mac)

Measured on a loaded box (load average 60-90): 401 compiles in 2.6 s for the
null arm slice, 370 composition compiles in 14 s. So one arm = 3,621 x 2
pattern compiles (~47 s) + composition (~14 s) = about 1 min; 107 arms =
about 110 min. Quote 2 h, range 1.2-3 h depending on load (the traced compile
is not slower than the plain one in this sample).

## Smoke (14 compiles, no lock, `SMOKE=1`)

    n2_census: arm 000 null                0.0s would_decline=5
    n2_census: arm 002 -fno-offset-skip    0.0s would_decline=1
    == N2 DONE rc=0 would_decline=6 ==

Patterns `abc[0-9]+xyz`, `foo(bar|baz)qux`, `[a-z]+@[a-z]+\.com` + 1 composition
file, 2 arms: 14 attempted / 14 compiled, 94 sites traced. It reproduces the
known would-declines and no others:

| row | phase | site shape | fields | count |
|---|---|---|---|---|
| ofsskip | define | FUNC/FIND/RETURN | miss:R1:UNSTATED | 2 |
| ofsskip | use | FUNC/FIND/RETURN | miss:R1:UNSTATED | 2 |
| precheck | use | STMT/ALL_PRESENT/ASSIGN | miss:R1:UNSTATED | 2 |

The R-6 table renders as `ofsskip FUNC/FIND/RETURN: state miss` and
`precheck STMT/ALL_PRESENT/ASSIGN: state miss`.

Separate timing runs (not the smoke, not counted in the 20): 401 + 370
compiles of the null arm into a scratch dir, to measure the estimate above.

## Notes

- A traced build is a scratch build; the 60 of 370 composition files that
  refuse at the null arm are the corpus's negative fixtures (counted as
  `refused`, not investigated).
- Witnesses are the 3 smallest (arm, stream, source, pattern) tuples, so they
  skew to early arms; the `arms seen` column shows spread.
