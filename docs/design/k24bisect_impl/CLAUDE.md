# docs/design/k24bisect_impl/ — the K24 bisect lane's instruments

Everything `k24_bisect_note.md` cites. K24 is
`docs/dev/known_issues.md`'s pattern-specific DFA throughput regression on
`(alpha|beta|gamma|delta|epsilon)` (`--no-captures`, pure DFA path):
`tests/bench/compare/compare.sh` case (c) measures ~294-304 MB/s against a
385-390 MB/s floor. This directory holds the bisect that found the culprit
(`1dbb6ce`, the `[M4.4]` API-break commit — **not** K18, the brief's prime
suspect, which is exonerated) and the mechanism (a gcc -O2 partial-inlining
side effect of that commit's refactor, not a DFA algorithm change) — see the
note for the full evidence chain, including a compiler-flag control
experiment that recovers the historical floor with nothing else changed.

**Nothing here is a fix.** Diagnosis only, per the lane's brief.

## Files

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

## Maintenance

Update this file if files are added/removed. This lane is closed
(diagnosis delivered); a fix, if one lands, belongs in its own lane and
should read `k24_bisect_note.md` first rather than re-deriving the mechanism.
