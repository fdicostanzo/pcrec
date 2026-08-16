# studies/simd1 — precompiled SIMD fixed-pattern matchers

Adopted 2026-08-16 from Frank's exploration (~/simd/test1, built with a
separate Claude session). Self-contained: own Makefile (`make check`,
`make bench`), own harness, NOT part of pcrec's build or test suite.
Everything compiles with `-O3 -mavx2` on x86-64 Linux; `coldmap.dat`
(1 GiB test file) and all binaries are gitignored and regenerated locally.

## Read first

- `precompiled-simd-matchers.md` — THE FINDINGS DOCUMENT (§1–§16): the
  matcher contract, the position-encoder menu with measured throughputs,
  case-insensitivity verdicts, length crossovers, alternation without
  backtracking, union prefilters and Teddy, rare-position filter selection,
  haystack-size tiering, find-all/pre-searcher mode, run extension +
  vector-width rule, and §16's exemplar-statistics (profile-guided
  generation) design. All numbers: Zen 1, GCC 15.2 — re-measure elsewhere.
- `JOURNAL.md` — the exploration's own session handoff (working
  conventions, state, next steps as of adoption).
- `README.md` — harness usage.

## Layout

- `harness.c`, `pattern.h/c`, `matcher.h`, `candidates.c` — the validation
  harness: universal bitmap oracle, guard pages both ends, fork+alarm
  isolation, red-teamed detectors, adversarial content kinds (fl-trap,
  periodic prefix, pf-trap), deterministic PRNG. §9 of the findings doc is
  its methodology.
- `cand_*.c` — the candidate matchers (scalar baseline, AVX2 broadcast
  chains, first+last and rare-pair filters, range idiom, shufti,
  alternation ± prefilters, SSE ports, shift-and, Teddy, prefetch).
- `bcast_gen.h`, `cand_gen.c` — the template-specialization experiment
  (§8's GCC const-prop failure and fixes).
- `findall.h/c` — find-all / pre-searcher mode (§14) with its own suite.
- `runext.c` — run-extension study (§15), self-contained binary.
- `coldmap.c` — cold-page-cache study (§12-E), generates/evicts its 1 GiB
  file locally.
- `*_bench*.txt` — archived benchmark transcripts backing the doc's tables.

## Relevance to pcrec (why it was adopted)

- [BENCH-1]/DD-9 case (f): engine_m4.md's worklist names bit-parallel
  shift-and as the algorithmic candidate — §12 Study B MEASURED blockwise
  shift-and losing 2–6× to AND-chains on Zen 1 (movemask-bound), content-
  independent floor only. That worklist row should read this before
  building anything.
- M4.6 hybrid/prefilter and V-C (grep CLI): §14's find-all pre-searcher
  contract, fire-rate strategy flip, and §7/§12-C prefilter selectivity
  math are directly the DFA-prefilter/anchor territory.
- D18 speed mandate: the §3 encoder menu and §11's width/ISA-layer
  findings are the specialized-emission playbook for a future SIMD tier.
- §16 exemplar statistics: the profile-guided-generation design (Frank's
  idea) — see the [ENG-PGO] discussion in docs/dev/plan.md if/when a row
  lands.

Maintenance: update this file when files are added/removed or change roles.
