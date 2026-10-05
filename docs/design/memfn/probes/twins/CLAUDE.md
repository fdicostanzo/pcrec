# docs/design/memfn/probes/twins/ — R1d's hand twins (lane memftwin)

The measured evidence for `../../twins.md`: does a kernel TAILORED to the
pattern beat a fixed generic kernel? Self-contained C, never built by
pcrec's make, never touching `src/`. Built from the repo root through
`../probes.mk` (`twins-check`, `twins-check-asan`, `twins-check-x86`,
`twins-asm`, `twins-run`) into `build/memfn_probe/twins/`, or by
`twins_run.sh` into `build/memfn_twins/<stamp>/` (both gitignored).

- `vec.h` — the vector layer every twin is written against (NEON, SSE2,
  SSSE3, AVX2 behind one set of `v*` helpers; `vmask`/`vfirst`/`VMASK_ONE`/
  `lane_from`), the shared find-first skeleton `FIND_BODY` and find-all
  skeleton `ITER_BODY`, the calibrated timer (>= 50 ms loops, D144
  addendum 1), the guard-page placement and the fuzz generator.
- `shapes.h` — the HAND-SPECIALIZED set classifiers, one per shape, as
  `X_DECL`/`X_CLS`/`X_PRED` macros plus the `k_X_shape`/`k_X_iter`
  kernels built from them. Shared by T-A and T-C.
- `ta_set.c` — T-A: per-shape classifier vs the generic two-table nibble
  lookup vs a scalar 256-table loop vs k memchr calls, by span and hit
  density, plus the `iter` control (find-all keeping the mask). `--check`,
  `--set=ID`, `--real=FILE` (the syntax t-64k text), `--quick` (smoke only).
- `tb_run.c` — T-B: the K82 caseless-run gate (union-select, userpass,
  mod-i) at 8a41efd2 (pre-handoff; STALE as a comparator since R4b, which
  uses `tb_r4b.c`): the emitted `rx_reqrun` VERBATIM vs a memchr2-style pass plus
  verify vs two fused vector loops. `--check`, `--subjects=DIR`.
- `tc_desc.c` — T-C: one always_inline kernel reading a `static const`
  descriptor vs the hand kernel, plus the writable-external control, the
  hoisted run-time library form and the in-loop-switch form. `--check`.
- `tc_asm.sh` — T-C's disassembly diff (per function, addresses/symbols/
  registers normalized; in-order and multiset line counts).
- `subjects.py` — materializes the bench subjects the twins read
  (capability short subjects + t-64k/t-1m, syntax t-64k/t-1m) from a
  READ-ONLY pcrec-bench checkout, sha256-checked against its manifests.
- `twins_run.sh` — build + check (incl. ASan) + asm + time, per box;
  appended to `../linux_run.sh` as the owed Linux run. Last log line
  `MEMFN-TWINS-RUN COMPLETE <dir> fails=<n>`.
- `tb_r4b.c` — R4b (lane memfnr4b, memfn R-1): the fused scan+verify on
  the POST-HANDOFF build. Cells us/up/mi + K85's cls-n-uc; variants `emit`
  (the abi-61 gate VERBATIM, pin d4d9ed90, from `gates_d4d9ed90/`), `emit2`
  (the floor twin), `nosl` (cls-n-uc's `-fno-req-set-lead`), `swar` (NEW:
  portable 64-bit fused pair filter, its over-read argument in the source),
  `ffl` (T-B's vector form, lead + per-byte masks), `swlf`/`ffllf` (lead
  first), `byte`. `--check [--subjects=DIR]` (generated set + subjects +
  planted defects that must be caught), `--subjects=DIR [--cell=C]
  [--quick]` times gate/sweep/short/pc16..pc1024 as machine-read `R` rows.
- `gates_d4d9ed90/` — the emitted gate text copied from the `-p rx`
  artifacts at d4d9ed90 (abi 61): `<cell>_def.inc` (the rx_reqrun
  definition, byte for byte, `#include`d by tb_r4b.c) and `<cell>_use.txt`
  (the entry's pre-check lines).
- `gates_sync.sh` — re-emits at a given pcrec binary and diffs both against
  `gates_d4d9ed90/` (+ abi 61, + K85's `-fno-req-set-lead` is exactly three
  lines). Last line `GATES-SYNC ok|FAIL <n>`.
- `subjects_r4b.py` — tb_r4b's subjects, resolved as alpha_k82.sh does
  (cap/syn t-64k/t-256k/t-1m via gen_throughput_subjects + the 75 short),
  sha256-checked, bench read-only.
- `tb_r4b_table.py` — renders tb_r4b transcripts (launches per build) as
  the R-1 readings: SIMD-off (swar - emit), SIMD-on (ffl - swar), K85's
  nosl columns, each delta against the emit/emit2 floor.
- `twins_tables.py` — renders a T-A transcript as markdown tables
  (absolute ns, the shape − generic delta).

Transcripts: `../out/twins/` (see `../out/CLAUDE.md`).

Maintenance: update this file when files are added/removed or change roles.
