# docs/design/memfn/probes/ — R1's call-cost probe

- `callcost.c` — self-contained probe; header comment states the kernels,
  modes (dep/ind), the 50 ms calibration and the `--check` method.
- `probes.mk` — `make -f docs/design/memfn/probes/probes.mk {check,check-asan,run,asm}`
  from the repo root; `CC_GCC`/`CC_CLANG`/`CFLAGS`/`OUT` overridable.
- `survey_chk.c`, `survey_tim.c`, `survey_pcrejit.c`, `survey_build.sh` —
  R2's (lane memfnsurvey) measured evidence for `../survey.md`: an
  exhaustive + guard-page (+ ASan exact-allocation) correctness check of
  third-party kernels, a timing harness on the R1 method, and PCRE2-JIT's
  own miss-scan cost. Third-party sources are NEVER vendored: the build
  script takes a scratch directory of pinned clones (commits in its header).
- `out/` — archived transcripts; see `../CLAUDE.md`.

Maintenance: update this file when files are added/removed or change roles.
