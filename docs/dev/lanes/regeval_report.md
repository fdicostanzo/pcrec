# regeval — the [REGIME-EVAL] design note (delivery record)

Lane regeval, 2026-10-13, branch `lane/memfn-regeval` (cut from `lane/memfn-r17` at
efcc3cd20). This is a design lane. The deliverable is
`docs/design/memfn/regime_eval.md`, which has its own charter-vs-committed checklist in
§10, together with an in-sample replay prototype in `docs/design/memfn/regime_eval/`.

- **No timing, no build, no `make`.** Nothing under `src/`, `memfn/src/`, `tests/` or
  `lib/` was touched. The prototype only reads the grid1 slot's finished logs. Its
  input hashes match `gridread/SHA256SUMS`.
- **Prototype results.**
  - It reproduces regime_tables §3's S0 row exactly.
  - It finds that the S1-SIMD-off, S2 and S3 figures are the cost model's, not what
    the declared rows achieve.
  - It finds that R3 has no SIMD-off arm, so S2 SIMD-off loses to always-walk.
  - R0 and R1 are unreachable on the grid.
  - The R3 correction is not visibly supported at this grid's noise level.
  - These are findings F-1..F-8 in the note's §8.
- **Not read.** lane/rwcorpus has no commit yet, and the kit's R17-b′ note is not
  committed. The design reads regime_tables rev 0.2's rows as the table under test.
- **Scope incident (disclosed).** One early command redirected `git show` output to
  `/home/pcrec/.scratch_dec`, which is outside the mandate. The file was deleted in the
  next command and never read back. All later scratch went into the worktree.
