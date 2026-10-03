# studies/hyb_reseed_cal/bakeoff/ — [OPT-HYB-RESEED-FORM] A2's form bake-off

Lane `rsform` (2026-10-03). The x86 gcc+clang bake-off that picks A2's
emitted form before any emitter text is written (`docs/design/xcall.md` §4
A2 and §6; manager ruling on §7 Q4). Scratch tier; nothing here is built by
`make` or run by `make test`. Run instructions: `README.md`.

## Files

- `README.md` — the manager's three steps (prep on the Mac, scp, one
  command on the Linux box) and how to read the table.
- `cells.tsv` — the witness cells (xcall.md §6's improve and keep lists,
  plus A1's logparse-atomic cell): pattern, flags, role, regime, subjects.
- `prep.sh` — builds the self-contained PACK: the artifacts, the
  sha256-verified subjects, the driver, this table and `bakeoff.sh`.
- `mkforms.py` — writes the six form variants (ai, f1, f2, f3, f3i, f4) of
  one shipped adaptive artifact, reusing `../shape/mkbound.py` and
  `../shape/mkb3.py`.
- `regen_cap_subjects.py` — regenerates capability@0.1's short subjects
  from the bench's generator, sha256-verified, writing nothing into the
  bench checkout.
- `bakeoff.sh` — the Linux-side run: builds every variant with each
  compiler at -O2, checks answers against the deny, calibrates, times
  pinned round-robin launches with a noise floor (`d2`, `dL`), prints one
  table.
