# docs/design/memfn/probes/ — R1's call-cost probe

- `callcost.c` — self-contained probe; header comment states the kernels,
  modes (dep/ind), the 50 ms calibration and the `--check` method.
- `probes.mk` — `make -f docs/design/memfn/probes/probes.mk {check,check-asan,run,asm}`
  (R1b: `{check-isa,check-asan-isa,run-isa,asm-isa,compile-x86,isanote,fmvdarwin}`)
  from the repo root; `CC_GCC`/`CC_CLANG`/`CFLAGS`/`OUT` overridable.
- `isacost.c` — R1b's ISA-selection probe (isa_selection.md §1, §3): per-call
  cost of each selection mechanism by span, `--sel=base|wide`,
  `--isa-report` (the declared-ISA stamp-against-CPU verdict), `--check`.
  x86-64 and AArch64 paths; mutable statics in it are LIBRARY stand-ins.
- `isanote.c`, `isanote.sh` — Linux x86 only: what the loader enforces about
  `GNU_PROPERTY_X86_ISA_1_NEEDED` (linker-written, source-written, static,
  `dlopen`, plus a SIGILL control). `make ... isanote`.
- `fmvdarwin.c`, `fmvdarwin.sh` — Mac only: `__builtin_cpu_supports` and
  multiversioning lowering under Apple clang and LLVM clang. `make ... fmvdarwin`.
- `linux_run.sh` — the ONE owed Linux x86 run: `callcost` (R1 §2.6) and all
  of R1b, pinned (`taskset`), bounded (`gnutimeout`), into
  `build/memfn_linux/<stamp>/`; last log line `MEMFN-LINUX-RUN COMPLETE`.
- `survey_chk.c`, `survey_tim.c`, `survey_pcrejit.c`, `survey_build.sh` —
  R2's (lane memfnsurvey) measured evidence for `../survey.md`: an
  exhaustive + guard-page (+ ASan exact-allocation) correctness check of
  third-party kernels, a timing harness on the R1 method, and PCRE2-JIT's
  own miss-scan cost. Third-party sources are NEVER vendored: the build
  script takes a scratch directory of pinned clones (commits in its header).
- `out/` — archived transcripts; see `../CLAUDE.md`.

Maintenance: update this file when files are added/removed or change roles.
