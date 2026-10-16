# docs/design/memfn/window_contract_rev31/ — window_contract.md revision 3.1's evidence

Lane `wcfix`, 2026-10-16. Every run used main `2288ad1cb`'s `build/pcrec`
(pcrec abi 78) on the Linux dev box, over emit_sweep's corpus argv stream
(5,790 `pattern` lines, `-p rx --features all -o -`). Compile-only: counts of
stamp values, refusals and byte equality, no clock. Fixtures are written into
a scratch directory given on the command line, never into the tree.

## Files

- `b1_witness.sh`, `b1_witness.out` — panel r4's B1 witness (the `l1none`
  fixture: compiles that refuse when asked and compile with `""` when not) and
  M2's probe (a byte-identical user copy of `default.rxt` resolving at link 0,
  stop `-I`, with the store's digest). `bash b1_witness.sh PCREC SCRATCH`.
- `analysiscount.py`, `analysiscount.out` — the refusal census of §3.7.4a:
  every deny arm × {no analysis, `weblog`, `log`, a measured `-I` bundle
  `mine`, the `l1none` fixture}, per arm the count of `""` compiles, refusals
  by cause, and stamp values. G1-E1's floors are read from it.
  `python3 -I analysiscount.py TREE PCREC SCRATCH [JOBS]` (`LIMIT=` env for a
  slice).
- `perturb_proto.py`, `perturb_proto.out` — the PROTOTYPE of C-PERT (§3.7.7):
  each artifact compiled with the store's `default.rxt` copied verbatim and
  with its byte-rate perturbed (ranks reversed, plus a utf8 `cpfreq` block),
  under the same name and stop; verdicts read from bytes and the stamp only.
  0 null-control failures; power per arm; exactly 2 FAILs, the F-5 witnesses.
  Same usage as `analysiscount.py`.

Maintenance: update this file when files are added/removed or change roles.
