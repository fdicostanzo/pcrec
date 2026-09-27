# docs/dev/memcmp_lowering_study/ — [OPT-LITSCAN] P4's memcmp-lowering probes

Reproduction pieces for `docs/dev/memcmp_lowering_study.md` (2026-09-27,
lane `memcmpstudy`): does gcc/clang's constant-length `!memcmp(base,
"lit", n)` lowering (P4, `emit_exact_compare`, `src/gen/emit_dfa.c:766`)
need a length bound or a form split. Read the memo first; this directory
is its evidence, not a second explanation of it.

## Files

- `gen_probe.py` — generates `probe.c`: one `cmp_memcmp_L` function per
  tested length (P4's own shape), plus `cmp_mask_L` (the `[WORD-FOLD]`
  load-and-AND-mask shape) and `cmp_overlap_L` (the two-overlapping-load
  shape, `L ∈ {5,6,7}`) for comparison. Deterministic, non-repeating
  per-length literals so no two functions' constants can be folded
  together by the compiler.
- `probe.c` — the generated probe source, self-contained (no pcrec
  dependency), toolchain-agnostic. Regenerate with `python3 gen_probe.py >
  probe.c`.
- `probe_extra.c` — a hand-written extension sweeping `L ∈ {25..30}` (not
  in the main brief's list), built to locate the exact edge of gcc's
  `L=31` cliff (§4 of the memo) rather than assume it starts earlier.
- `analyze_asm.py` — splits a gcc/clang Mach-O `.s` file (arm64 or
  cross-compiled x86_64 AT&T) into per-function bodies and reports
  call-out/load/compare/branch counts per function, by name
  (`cmp_(memcmp|mask|overlap)_<N>`). See its own header for the ONE known
  limitation (ARM condition-code branches like `bne`/`beq`/`bhi`
  under-count in the branch column) — every branch-count-dependent claim
  in the memo is corroborated by reading the raw assembly, not by
  trusting that column alone.
- `bench.c` — the scratch microbenchmark (§8 of the memo): `memcmp` vs a
  per-byte `if`-chain vs the load-and-mask form, per `L`, three subject
  regimes (match / first-byte mismatch / last-byte mismatch), best-of-5
  rounds, arms rotated within a regime. Build per length:
  `gcc-16 -O2 bench.c -o bench -DL=<n>`. Never run by `make test` or any
  other pcrec suite — a throwaway per the brief, kept here only because
  the memo cites its exact output.
- `bench_results.txt` — the committed run this lane's memo cites (§8);
  regenerate with `timeout 25 ./bench` per length if the toolchain or box
  changes and the memo needs re-verifying.
- `asm/` — the committed `.s` outputs the memo's tables and code excerpts
  are read from: `probe_gcc16_{O1,O2,O3,Os}.s` (this box's `gcc-16`,
  Homebrew 16.2.0), `probe_clang_O2.s` (Apple clang 21.0.0, native arm64),
  `probe_clang_x86_O2.s` (the same clang, `-target x86_64-apple-darwin`
  cross-compile — a secondary column only, never run, per the box mandate
  against ssh-ing to the Linux reference box for this), `probe_extra_O2.s`
  (the `L=25..30` sweep, gcc-16 only). `gcc-15`/x86 is OWED — the memo §6
  carries the exact commands for whoever holds that channel next.

## Regenerating

```sh
python3 gen_probe.py > probe.c
gcc-16 -O1 -S probe.c -o asm/probe_gcc16_O1.s
gcc-16 -O2 -S probe.c -o asm/probe_gcc16_O2.s
gcc-16 -O3 -S probe.c -o asm/probe_gcc16_O3.s
gcc-16 -Os -S probe.c -o asm/probe_gcc16_Os.s
clang -O2 -S probe.c -o asm/probe_clang_O2.s
clang -target x86_64-apple-darwin -O2 -S probe.c -o asm/probe_clang_x86_O2.s
python3 analyze_asm.py asm/probe_gcc16_O2.s | grep memcmp   # etc, per file
```

Maintenance: update this file when files are added/removed or their roles
change.
