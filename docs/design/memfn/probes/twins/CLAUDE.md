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
  mod-i): the emitted `rx_reqrun` VERBATIM vs a memchr2-style pass plus
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
- `twins_tables.py` — renders a T-A transcript as markdown tables
  (absolute ns, the shape − generic delta).

Transcripts: `../out/twins/` (see `../out/CLAUDE.md`).

Maintenance: update this file when files are added/removed or change roles.
