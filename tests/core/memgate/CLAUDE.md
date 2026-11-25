# tests/core/memgate — the per-compile memory and cost gate ([ARENA-SCOPES] T1)

Opt-in (`make memgate`), NEVER in `make test`. Compares two BUILT SIDES compile by compile over one population (every
distinct corpus argv pattern, `--features all`, plus every non-red growth cell; read from side A's tree). Design of
record: `docs/design/arena_scopes.md` (G2, G5, standing question 1; unit T1). Made reproducible from lane k155fix's
scratch tool.

## Files

- `memgate.py` — `prep SIDE (--ref REF | --tree TREE)` builds a side outside any tree (`git archive` for a ref); `peak
  A B OUT [--bound N]`, `rungs A B OUT`, `instr A B OUT [--band --p95]` compare. A side against itself is the noise
  read. Its docstring is the usage.
- `mg_drv.c` — the per-compile driver: `-DMG_PEAK` (alloc_inject.h library; peak live heap in REQUESTED bytes, kept
  per pointer, with the `malloc_usable_size` peak as an informational column (lane arenabuild2, R-2); arena BLOCK
  bytes (requested block size) split by ARENA IDENTITY through `--wrap=pcrec_arena_alloc`/`pcrec_arena_free`: attempt arena =
  `&cx->arena`), `-DMG_INSTR` (plain library; user-mode instructions by `perf_event_open`).

## Rules

- Deterministic by construction: no wall clock is read. Nonzero noise (a side against itself) is a STOP for the gate
  that relies on it (design T1).
- The arena split sees only calls that cross an object boundary (GNU ld wraps undefined references): a child arena
  released inside arena.c stays counted in the OTHER column, which is informational; the ATTEMPT column is the gate.
- A side's build dirs, drivers and pattern files live under the OUT/side directories given (the temp root), never in a
  tree.
