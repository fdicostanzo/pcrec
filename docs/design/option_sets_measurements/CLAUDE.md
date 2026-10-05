# docs/design/option_sets_measurements/ — [OPT-SETS] cross-source probes

The measurement behind `../option_sets.md` §2.5a (revision 2, lane optsrev,
2026-10-05): how TODAY's compiler composes one option across the command line
and a `.rxt` target's config/block, per axis KIND, measured on `build/pcrec`
rather than read from `docs/spec/cli.md` (the r1 panel, OS-M1/OS-M2, found the
note's description of this wrong in a way no reader of the note could see).

## Files

- `probe.sh` — one cell: writes a scratch `.rxt` (`config c` + `target rx = p
  with c` + block `p`), compiles it with the given CLI flags, prints exit code,
  stderr and the stamps a composition can move. `SCRATCH` is required and must
  not be `/tmp`; `PCREC` defaults to this tree's `build/pcrec`.
- `cases.sh` — every cell §2.5a cites, in table order (labels A* raw `-f`
  bits, B* `flags` letters, C* `features`, D* engine, E*/T* tune, F* analysis,
  G* encoding, H* value options and budgets, M3* co-firing constraint rows).
- `out/cross_source.txt` — the transcript `cases.sh` wrote (first line names
  the pcrec version and tree commit). Evidence for the note, never an oracle:
  no check reads it.

Reproduce: `SCRATCH=<dir> ./cases.sh > out/cross_source.txt`.
