# docs/design/k24bisect_impl/ — the K24 bisect and fix lanes' instruments

Everything `k24_bisect_note.md` and `k24_fix_note.md` cite. Two lanes share
this directory on purpose: the fix's evidence is only readable against the
diagnosis's, and splitting them would put the causal control experiment and
the lever that reproduces it in different places.

K24 is
`docs/dev/known_issues.md`'s pattern-specific DFA throughput regression on
`(alpha|beta|gamma|delta|epsilon)` (`--no-captures`, pure DFA path):
`tests/bench/compare/compare.sh` case (c) measures ~294-304 MB/s against a
385-390 MB/s floor. This directory holds the bisect that found the culprit
(`1dbb6ce`, the `[M4.4]` API-break commit — **not** K18, the brief's prime
suspect, which is exonerated) and the mechanism (a gcc -O2 partial-inlining
side effect of that commit's refactor, not a DFA algorithm change) — see the
note for the full evidence chain, including a compiler-flag control
experiment that recovers the historical floor with nothing else changed.

**K24 IS CLOSED** (2026-08-17, k24fix lane): `__attribute__((noclone))` on
`<prefix>_search`, emitted by `emit_search_head` in src/gen/emit_dfa.c — the
one site serving both the DFA exported entry and the VM hybrid's `static`
prefilter. `floors.tsv` was never touched; case (c) came back to
391.063 MB/s at its historical 1.02x spread against the untouched 388.615
floor. `k24_fix_note.md` is that lane's evidence.

## Files

- `k24_fix_note.md` — the FIX lane's evidence (2026-08-17): the ten-lever
  head-to-head on case (c) with the pinned protocol, the byte-identical
  assembly comparison against `-fno-partial-inlining`, the VM-artifact audit
  (the VM is NOT split, and the brief's premise for why it might be —
  match/match_caps → search — is wrong: the VM's wrappers call
  `<prefix>_match_impl` directly), the 25-pattern clone sweep that shows 13
  of 14 DFA artifacts were split before the fix and none after, the case (j)
  neutrality check, and the acceptance run. Read this before changing or
  removing the attribute; two of its rows exist specifically to refute the
  two obvious alternative fixes.
- `k24_bisect_note.md` — the findings: culprit commit, per-point
  medians+loads table (10 points, CPU-pinned), the artifact-diff mechanism
  (byte-identical DFA tables/hot-loop instructions before and after, and all
  the way to the current tip — K18 never touches this pattern's output), the
  `-fno-partial-inlining` control experiment that causally confirms the
  mechanism, and a methodology-correction section (the probe's first draft
  ran unpinned, which is what made the initial bad-endpoint reading
  non-reproducible until CPU pinning was added — read this before trusting
  any unpinned rerun of the numbers here).
- `probe.sh` — the standalone bisect probe: builds the checked-out commit,
  compiles `(alpha|beta|gamma|delta|epsilon)` (passing `--no-captures` only
  when that commit's CLI offers it — the flag doesn't predate the whole
  window, see the note's "Brief corrections"), detects which `rx_search` ABI
  era the commit emits (`RX_NCAPS` in `gen.h`; there's a break inside the
  window at the same commit that turns out to be the culprit) and builds a
  matching driver variant, asserts the `ENGM_DFA` engine stamp when that
  mechanism exists, times 3 pinned (`taskset -c 2`) trials against the
  cached subject and reports the median. Exit 0/1/125 (good/bad/skip) for
  `git bisect run`. Lives in the session scratchpad during an actual bisect
  run (historical commits in range predate this directory entirely, so a
  tracked copy would vanish mid-walk); the copy here is for provenance and
  reruns after the fact, not what `git bisect run` itself invoked.
- `gen_subject.py` — regenerates `compare.sh`'s case-(c) subject bit-for-bit
  (same seeded `random.Random(1729)`, same draw order across cases (a)/(b)/
  (c), same `purge_words()` pass), so `probe.sh`'s numbers are directly
  comparable to `compare.sh`'s own floors.tsv reference rather than merely
  similarly-shaped.
- `mk_levers.py` — builds every candidate lever variant from ONE baseline
  `gen.c`, inserting each attribute at the site the emitter would insert it,
  so the head-to-head measures exactly what landing that lever produces
  rather than an approximation of it.
- `lever_probe.sh` — the fix lane's timing harness. Uses `compare.sh`'s build
  line verbatim (`gcc -O2 -std=gnu11 -Wall -Wextra -Werror` + `eng_pcrec.c`)
  rather than `probe.sh`'s hand-built driver, and that is the whole point:
  the split's cost is a code-PLACEMENT cost, so a number is commensurable
  with `floors.tsv` only when it comes from `floors.tsv`'s own link. Pins
  every timed run, refuses above load5 2.0, asserts the match/nomatch
  verdict before timing, reports median + min-max + whether `nm` still shows
  a clone.
- `sweep_clones.sh` — the audit instrument: compiles a pattern set and
  reports every gcc-created `.part`/`.constprop`/`.isra` clone per artifact,
  tagged by engine stamp. Run against a pre-fix and a post-fix compiler, it
  is what turned "is the VM split too?" into a table.
- `h2h_case_c.tsv`, `h2h_case_j.tsv`, `clones_before.tsv`,
  `clones_after.tsv` — the raw output those three instruments produced, as
  measured. The notes quote from these; they are not regenerated by any
  check (D35's posture: archived probe output is evidence, never an oracle).

## Maintenance

Update this file if files are added/removed. BOTH lanes are closed —
diagnosis delivered, fix landed. Anyone revisiting K24 (or finding the
`noclone` attribute in an artifact and wondering about it) should read
`k24_fix_note.md`, then `k24_bisect_note.md`, rather than re-deriving either
the mechanism or the reason the two obvious alternative fixes were rejected.

## Post-lane addendum (manager landing, 2026-08-17)

- **`h2h_case_c.tsv` is HEADER-ONLY** — the lane died on an API 529 before
  the data rows were archived (its numbers survive in the fix note's prose
  and the emit_dfa.c comment). **`h2h_case_c_rerun.tsv`** is the manager's
  independent re-measurement of the LANDED artifact with the committed
  `lever_probe.sh` (one variant dir, the worktree compiler's own emission):
  median 390.740 MB/s, mono (no .part clone in nm), 10 pinned trials,
  384.9-392.5 — confirming the fix against the 388.615 floor from a fresh
  instrument run, which is what an empty archive costs to repair.
- **`lever_probe.sh` takes variant DIRECTORIES as arguments** and produces a
  header-only TSV plus "DONE" when invoked argless — how the empty archive
  read as complete. If you touch it, make the argless case a loud error.
- **THE POISONED-CORE INCIDENT, recorded for every future pinned benchmark:**
  a `timeout`-killed compare.sh leaves its PINNED engine children running;
  a later grid then timeshares core BENCH_CPU with the orphans and measures
  ~exactly HALF throughput on every engine (measured: pcrec 194.8 vs 390.0,
  jit 285 vs 570, python 42 vs 84 — all ~0.5x, tight spreads, so it reads
  as a stable real number). compare.sh's load guard reads GLOBAL loadavg
  and 1.07 passed — a load of ~1.0 IS one competitor sitting on the pinned
  core. Before any pinned measurement: check per-core occupancy
  (`ps -eo pid,psr,comm | awk '$2==CORE'`), not just loadavg.
