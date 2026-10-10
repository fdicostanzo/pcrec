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
  R1d appended one call: `twins/twins_run.sh`, whose own trailer
  `MEMFN-TWINS-RUN COMPLETE` then ends the whole run.
- `survey_chk.c`, `survey_tim.c`, `survey_pcrejit.c`, `survey_build.sh` —
  R2's (lane memfnsurvey) measured evidence for `../survey.md`: an
  exhaustive + guard-page (+ ASan exact-allocation) correctness check of
  third-party kernels, a timing harness on the R1 method, and PCRE2-JIT's
  own miss-scan cost. Third-party sources are NEVER vendored: the build
  script takes a scratch directory of pinned clones (commits in its header).
- `twins/` — R1d's (lane memftwin) hand twins for `../twins.md`: T-A set
  classifier per shape, T-B fused run scan+verify, T-C constant-descriptor
  specialization, their run script (`twins_run.sh`, appended to
  `linux_run.sh`) and subject materializer. See its own CLAUDE.md.
  `probes.mk` gains `twins-check`, `twins-check-asan`, `twins-check-x86`,
  `twins-asm`, `twins-run`. R4b (lane memfnr4b, memfn R-1) adds `tb_r4b.c`
  and its helpers there (the post-handoff fused scan+verify).
- `lxrun/` — lane lxrun's Linux hand-off scripts (2026-10-05): L-2, L-4 and
  the x86 survey port; R4b's `memfn_r4b.sh` verdict run; own CLAUDE.md.
- `out/` — archived transcripts; see `../CLAUDE.md`. `out/linux/` is the
  2026-10-05 Linux run (own CLAUDE.md).

Maintenance: update this file when files are added/removed or change roles.
- `rowcon/` — [MEMFN-ROWCON] audits (kit rows; pcrec tables) behind row_contracts.md.
- `r4e0b/` — R4e′.0b's G1 instruments (lane r4e0b, 2026-10-09; integration.md
  §R4.9.2.6): `routing_census.py` (movers by id against the parent's own
  function count, the un-done text diff, the per-function byte delta, and
  `-S` assembly identity per recipe with gcc's local labels renumbered and
  the abi DATA read across; `--nonid-out` lists the non-identical movers),
  `routing_timing.py` (the parent-vs-routed timing pair for those movers
  only). Results in `docs/dev/lanes/r4e0b_report.md` §4.
  `r4e0b/out/` holds the transcripts (the full census, the -Os/-O0 sample,
  both timing tables) and `nonid_full.tsv`, the non-identical movers.
- `vmlazy/` — R-12 VMLAZY NORMALIZE's G1 instrument (lane vmlazy,
  2026-10-09; `docs/dev/lanes/r12scope_report.md` §1.5):
  `lazy_census.py` (movers by id against the parent's own lazy-prefix
  count read by the OLD form's regex, the un-done text diff with
  `RX_VM_PROGRAM_BYTES` read back by the measured block delta, the reach
  test's offset checked as K*W, an `RX_VM_ENTRY_SHAPE` mover class, six
  planted controls run first, a K35 floor per stream, and `-S` assembly
  identity per recipe through `r4e0b/routing_census.py`'s normalizer;
  `--movers-out`/`--nonid-out` list the movers). `vmlazy/out/` holds the
  transcripts. Results in `docs/dev/lanes/vmlazy_report.md`. `movers.tsv` is the
  5431-row census (before `tests/base/vm_lazy_rmin_prefix.rxt`); the slot17b
  by-id read over the full 5451 rows, every cell and stream, is
  `out/slot17b_movers_by_id.txt` (with `out/slot17b_pin_vs_measured.txt`, the
  VARIANT_PINS re-pin's before/after; report §8b).
