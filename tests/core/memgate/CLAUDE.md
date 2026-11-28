# tests/core/memgate — the per-compile memory and cost gate ([ARENA-SCOPES] T1)

Opt-in (`make memgate`), NEVER in `make test`. Compares two BUILT SIDES compile by compile over one population (every
distinct corpus argv pattern, `--features all`, plus every non-red growth cell; read from side A's tree). Design of
record: `docs/design/arena_scopes.md` (G2, G5, standing question 1; unit T1). Made reproducible from lane k155fix's
scratch tool.

## Files

- `memgate.py` — `prep SIDE (--ref REF | --tree TREE)` builds a side outside any tree (`git archive` for a ref); `peak
  A B OUT [--bound N]`, `rungs A B OUT`, `instr A B OUT [--band --p95]` compare. The noise read is a side against a
  SECOND directory of the same binaries (the same directory twice is refused). Its docstring is the usage.
- RECORDED COST (F4 lent count, lane f4flag; owner f4-instr, 2026-11-27: "try but not very hard. I accept the marginal slowdown."): `instr` reads p50 1.00048, p95 1.00467, max 1.02533 with 25 deep-nesting, allocation-heavy cells over the 1.020 max band (+4.0 instr per `pcrec_arena_alloc` call); those 25 are an accepted, recorded cost, not a regression.
- `test_verdicts.py` — the control for the verdict lines and exit status (fake sides, <1 s; run first by `make memgate`).
- `mg_drv.c` — the per-compile driver: `-DMG_PEAK` (alloc_inject.h library; peak live heap in REQUESTED bytes, kept
  per pointer, with the `malloc_usable_size` peak as an informational column (lane arenabuild2, R-2); arena BLOCK
  bytes (requested block size) split by ARENA IDENTITY through `--wrap=pcrec_arena_alloc`/`pcrec_arena_free`: attempt arena =
  `&cx->arena`), `-DMG_INSTR` (plain library; user-mode instructions by `perf_event_open`).

## Population levers (env, SCOPE-4)

The default population is byte mode with the auto engine; it cannot reach the VM whole-set class matchers (the
`pcrec_clskit_emit_whole` site). `MG_ENC=N` sets `pcrec_options.encoding` for every compile (mg_drv.c; 1 = utf8) and
`MG_ENG=N` the engine of the CORPUS items (cells keep their own; 2 = VM). Unset reads 0. memgate.py `levers()` refuses a
non-integer, every mode (`peak`, `rungs`, `instr`) prints a `<mode>: levers MG_ENC=.. MG_ENG=..` line, and `test_verdicts.py` covers the reads: `population()` must carry MG_ENG, and the built mg_peak driver must change under MG_ENC (builds the inject library, incrementally). A bound is needed for a verdict: `peak ... --bound 0` (`make memgate` passes MEMGATE_BOUND; the levers pass through its environment). Run with both sides under the
same values: `MG_ENC=1 MG_ENG=2 python3 -I tests/core/memgate/memgate.py peak A B OUT --bound 0`. Nothing more: no per-cell lever.

## Rules

- THE RUNG RULE (the owner, 2026-11-25, "rung-edge: agree with lean"; design D-9): `rungs` judges a rung on REQUESTED
  bytes. A compile/refuse move on a cell whose uncapped requested peak is unchanged prints `LAYOUT` (both thresholds,
  the heap-extent delta) and passes as `VERDICT LAYOUT`; any other move prints `MOVE-FAILS` and reads `VERDICT MOVED`.
- `instr` runs `mg_instr` under `setarch $(uname -m) -R` (ASLR off; `drv_argv`), and `mg_drv.c -DMG_INSTR` exits 3 if
  ADDR_NO_RANDOMIZE is not set: the instruction count is layout-dependent (a ~2,000-instruction spread on a 91k compile
  with ASLR on; A/A max ratio 1.022 on, 1.00001 off over 4,500). `test_verdicts.py` asserts the wrapper. `peak` counts
  requested bytes, so it needs none. Not `perf_event_open`'s fault: do not "fix" by taking a min of N runs.
- Deterministic by construction: no wall clock is read. Nonzero noise (a side against itself) is a STOP for the gate
  that relies on it (design T1).
- The arena split sees only calls that cross an object boundary (GNU ld wraps undefined references): a child arena
  released inside arena.c stays counted in the OTHER column, which is informational; the ATTEMPT column is the gate.
- A side's build dirs, drivers and pattern files live under the OUT/side directories given (the temp root), never in a
  tree.
