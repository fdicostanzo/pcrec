# Session Journal — SIMD fixed-pattern matcher project

Written 2026-08-16 as a handoff. A new session should read this, then skim
`precompiled-simd-matchers.md` (the learning doc — the detailed findings live there,
published at https://claude.ai/code/artifact/23cd466f-5e79-474b-b69e-b64a1faf3a1a;
republish that same file path to update the same URL).

## The project

Frank is building **precompiled AVX2 substring/pattern matchers in C**: the pattern is
known at build time, so each matcher is a generated function
`const char *find(const char *hay, size_t n)` (leftmost match or NULL, exact `memmem`
semantics, never reads outside `[hay, hay+n)`). The long-term goal is a **generator
("engine")** that takes a pattern spec + hints and emits the C we have so far written by
hand — that generator is **step 2 and has NOT been started**. Everything to date is step 1:
the test harness plus a library of hand/template-written candidates that measure every
design choice the generator will need to make. A newer use case (Frank's words): the
matchers as an exact **pre-searcher** feeding a regex engine anchor positions, including
factored patterns like `A.*B` and run atoms like `[a-zA-Z.]+@`.

## Working conventions (Frank's explicit preferences)

- **Use subagents (sonnet/opus) for defined work**; orchestrate + integrate in the main
  session. One agent per file to avoid conflicts; registry/Makefile edits done by the main
  session when multiple agents run.
- **Everything runs through `make`**. `make WERROR=1` is the warning gate.
- **Red-team before trusting**: every new harness capability gets a deliberately broken
  candidate registered temporarily to prove the detector fires (overread → guard-page
  crash; fake-CI → mixed-case plant; blind `|0x20` → binary fuzz; dropped alternation
  branch → plant).
- **The learning doc is living**: after each substantive finding, update
  `precompiled-simd-matchers.md` + its Changelog and republish the artifact.
- Persistent memory (auto-loaded) tracks project state; this journal is the fuller
  narrative.

## What was built, in order (details: learning doc §§ cited)

1. **Harness** (`harness.c`): fork-isolated correctness per matcher vs a universal oracle,
   every haystack tested twice flush against PROT_NONE guard pages (over/under-read),
   deterministic fuzz, failing-case dumps, benchmark with calibrated best-of-5 timing.
   Oracle = bitmap pattern compiler (`pattern.h/.c`): k positions × 256-bit member sets,
   `[ab]` classes, ci twins, top-level `|` alternation, `{N}`, `+` (§1, §9).
2. **Candidate axes** (all in `cand_*.c`, registry in `candidates.c`, 43 matchers, all
   passing ~9–11k cases each): needle length 2..32; CI via OR-of-twins vs fold-block;
   classes via OR-chain vs saturating-subtract range vs pshufb shufti; alternation with
   shared loads + trie prefix sharing; union-class prefilters; Teddy; rare-position
   filters; software prefetch variants; 8 SSE (128-bit) ports.
3. **Standalone drivers**: `coldmap.c` (cold mmap study), `findall.c` + `cand_findall.c`
   (find-all mode, own guard+oracle suite), `runext.c` (self-contained run-extension
   microbench — designed to be copied to an Intel box).

## Findings summary (the generator's rulebook)

- Per-position broadcast AND-chain: confirmed matches with no verify step; loop bound
  `i + 32 + (k-1) <= n`; vptest early exit for k>4 (§2). Wins vs memmem up to k≈16;
  periodic-prefix content is its pathology — long needles want rare-pair filter+verify
  (§5).
- Encoder menu by class shape, measured: cmpeq(1 op) / OR 2–3 members / saturating-sub
  range (3 ops, any [lo,hi]) / shufti (~7 ops flat, arbitrary ASCII set) (§3).
- CI: OR-of-twins beats fold-block everywhere; blind `|0x20` is a bug (caught by binary
  fuzz) (§4).
- **Codegen lesson that shaped everything**: GCC would not specialize a generic loop
  through a pointer table — flatten data (`char[ ][8]`) + `#pragma GCC unroll`, or emit
  per-position code explicitly; verify with objdump (the generator should emit explicit
  code) (§8).
- Alternation: `X+` collapses to one position under leftmost-start semantics (no
  backtracking exists in this model); branches share loads; `fred`⊂`frederick` shares
  masks (§6). Union-class prefilter depth ≈ min_k, needs per-lane pass rate ≲1–2%
  (`(1-p)^lanes`) (§7). Teddy beats union filters from ~4–8 branches (bucket bits →
  targeted verify) (§12-C).
- Rare-position filter selection (Frank's suggestion, biggest single win): pick filter
  bytes by background frequency — 6–33× over first/last on realistic corpora; needed the
  frequency-weighted `english` bench kind to even see it (§12-A). Blockwise shift-and:
  rejected (movemask-bound), niche worst-case floor only (§12-B).
- SSE/width: AVX2 wins on Zen 1 via instruction density (double-pumped 256-bit = half the
  front-end work), 0.43–0.85× for SSE; no ranking flips (§11). BUT for short run
  extension, xmm wins when the run distribution fits 16 bytes; **width rule: cover p99 of
  the run distribution — width buys branch predictability** (§15). SSE/AVX mixing is an
  encoding (VEX vs legacy) issue only; single `-mavx2` TU has none; AMD unaffected (§15).
- Memory system: software prefetch hurts ~9% below L3, gains 9–15% above; size-gated
  ~+1024 only (§12-D). Cold mmap: NO userspace warming helps at scan time (prefetcht0
  can't fault pages; kernel readahead saturates the SATA disk; 28× cold/warm gap) — page
  warming is scheduling (`MADV_WILLNEED` ahead of need), not codegen (§12-E).
- Haystack-size tiering is a second dispatch axis: tiny=loop-free, small=few-constant +
  overlapped final block, medium=as-measured, huge=prefetch + robustness-is-free,
  exact-n=fully unrolled (§13).
- Find-all / pre-searcher mode (`findall.h`: all ascending starts incl overlaps,
  count-past-cap): emission floor ~3.3 ns/hit at ≥1% density; ctz bit-walk <1% density,
  mask-store two-pass above; **filter-vs-chain flips at ~0.5–1% filter fire rate** (decoy
  sweep — find-all pays verify per candidate bit); fused vs two-pass factor pairing is a
  tie → prefer simple merge; `A.*B` is fully decided by anchor pairing, `[^\n]*` is
  stream algebra with a newline stream (§14).
- Run extension (`[class]+@` email shape): branchless classify+clz beats scalar table
  loop 2–3× on honest mixed lengths (~50-cycle run-end mispredict); per-anchor 4–7 ns =
  free at real anchor densities (§15).
- Exemplar statistics: §16 is the profiler spec — nine statistics, how gathered, which
  measured knob each drives; fire-rate model validated against decoy sweep; user
  rare-string hints as rank-0 overrides; runtime demotion + trap-content acceptance gates
  as defenses.

## How to run

- `make check` — build + correctness (43 matchers, exits nonzero on failure).
- `make bench` / `./harness --bench-only --matcher NAME` — benchmarks (7 content kinds ×
  5 sizes incl 32 MiB; full run is slow, filter by matcher).
- `./harness --list`, `--seed N`, `--no-bench`.
- `make findall && ./findall` — find-all correctness + density/decoy/pair benches.
- `make runext && ./runext` — run-extension microbench (self-contained file).
- `make coldmap && ./coldmap` — cold-mmap study (creates 1 GiB `coldmap.dat`).
- Bench outputs saved: `bench_results.txt` (+`_before_fix`), `alt_bench.txt`,
  `pf_bench.txt`, `opt_bench.txt`, `sse_bench.txt`, `pf_dist_bench.txt`.
- `make clean` removes binaries/objects/failure dumps; `make distclean` additionally
  removes the 1 GiB `coldmap.dat` and the saved bench outputs.

## Where we left off / open items

Just finished: §16 exemplar-statistics section (Frank asked for it explicitly). All 43
harness matchers + 7 find-all candidates green. Nothing in flight.

Open, roughly in priority order:
1. **The generator itself (step 2)** — not started. §10 has the seven-step spec; the
   dispatch space is pattern × ISA × size tier × mode (first/all/masks/factor-streams) ×
   density model. The codegen lesson says: emit explicit per-position C, never generic
   loops. `bcast_gen.h` is the proto-template; the real engine should generate source.
2. **Intel runs** — `runext.c` (and optionally the harness) on an Intel box; §15 leaves
   the Intel column open (expect ymm to never lose there; SSE-vs-AVX2 ratios §11 are
   Zen-1-specific).
3. Cheap catalogued optimizations, unmeasured: overlapped final block (kills the scalar
   tail; matters most in the small tier), 64/128B unrolling, memchr-jump hybrid for very
   sparse rare bytes (§12 catalog).
4. Small-tier honesty: harness bench mode cycling many distinct small buffers (predictor/
   cache realism) before trusting §13's small-size choices.
5. Huge pages (THP/madvise) for the >L3 tier; NVMe rerun of `coldmap`.
6. Possible harness upgrade: fold find-all mode into the main harness registry (currently
   a separate driver with its own mini-harness).

Hardware context for all numbers: AMD Ryzen 5 1600 (Zen 1), GCC 15.2, `-O3 -mavx2`,
single-threaded; 16 MB L3 (8 per CCX); SATA SSD. Zen 1 double-pumps 256-bit ops — newer
cores will widen SIMD-vs-libc gaps and shift the §15 width crossover.
