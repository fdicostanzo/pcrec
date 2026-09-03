# studies/alt_dispatch/ — [ENG-ISL.S0], the alternation-dispatch study

Chartered by Frank 2026-09-03 ("I approve the study charter"). Answers one
question for `[ENG-ISL]`'s first named island candidate (VM alternation
dispatch as a trie/switch, docs/dev/plan.md's `[ENG-ISL]` row): of five
dispatch algorithms for a wide literal alternation, which is exact, which is
fast, and at what width does the win justify building it into
`src/gen/emit_vm.c`. Self-contained per `studies/CLAUDE.md`: own Makefile,
`gcc -O2`, never built by pcrec's own `make`, never run by `make test`.
Nothing under this repo's `src/` or `tests/` changes.

Mid-study ruling R1 (Frank, 2026-09-03) added algorithm (e), the VM-native
trie walk, as the PRIMARY candidate — see
`docs/design/alt_dispatch_study.md` §3.2 and §6.

See `docs/design/alt_dispatch_study.md` for the method, the exactness
argument, the measured tables and the recommendation. This file is the
how-to-reproduce.

## Layout

- `src/` — the harness. `common.h`/`.c` (the `ByteSet`/`Branch`/`Subject`
  types — a branch is a sequence of 256-bit class bitmaps, not a raw
  string, so a `(?i)` branch is a first-class input with no special-casing:
  see `common.h`'s header comment for why this mirrors `src/ir/nfa.c`'s
  `TItem`). `algo_serial.*` (a, the oracle), `algo_firstbyte.*` (b),
  `algo_trie.*` (c AND e — the M2.8 trie ported to a query walk, plus
  `trie_dispatch_vm`, the VM-native walk ruling R1 added, sharing the same
  trie), `algo_hash.*` (d, the k-byte block hash). `harness.c` is the
  driver (`main`).
- `gen_inputs.py` — derives `patterns/*.branches` and `subjects/*.bin` from
  pcrec-bench's `bench/altwide/` (read-only input; see its own header for
  exactly what is copied verbatim, what is derived by a stated rule with no
  new pool words, and what could not be built). `make check` re-derives and
  diffs.
- `patterns/*.branches` — one branch per line, a `# MODE literal|ci` header,
  a `# PROVENANCE` header naming the bench source or derivation rule.
- `subjects/*.bin` — copied byte-for-byte from the bench (see
  `subjects/PROVENANCE.md`).
- `tests/unit_trie.c` — adversarial exactness checks for (c) AND (e): both
  of `src/ir/nfa.c:192`'s M2.8 counter-examples (rule 1, rule 2), re-derived
  independently against this study's own oracle (a), plus the rule-2
  decline path (a hand-built genuinely-overlapping-class case the bench's
  literal/ci inputs never produce). The rule-1 case (`abc|a|abd`) is also
  the regression test for (e)'s own correctness subtlety — see
  `docs/design/alt_dispatch_study.md` §3.2.
- `analyze.py` — reads `results/*.tsv` and prints the summary tables the
  design doc's §4 cites, including (e)'s frames-pushed/deferred-mask table.
- `results/*.tsv` — this study's measured output (committed): `identity.tsv`
  (mismatch counts, the exactness bar), `tries.tsv` (tries/verify-bytes per
  subject byte, plus frames/max-deferred for `vm`), `timing.tsv` (median ns
  over 11 rounds, ns/byte, ns/call, `load1` at measurement time),
  `construction.tsv` (build cost + table bytes for (b)/(c)/(d); (e) shares
  (c)'s trie).

## Reproducing

```
make inputs   # derive patterns/ and subjects/ from pcrec-bench (or `make check` to verify committed copies)
make unit     # the two nfa.c hazard counter-examples + the decline case
make run      # the full measurement matrix -> results/*.tsv
```

`make run`'s TIMING numbers are only as good as the box's load at
measurement time — every row in `results/timing.tsv` carries its own
`load1` column; read it before comparing across runs. The answer-identity
and tries-per-byte numbers (`identity.tsv`, `tries.tsv`) are load-
independent and safe to trust regardless.

## What each algorithm is, one line each

- **(a) serial try** — today's `vm_alt` (`src/gen/emit_vm.c`): branches in
  source order, first match wins. The oracle (trivially leftmost-first).
- **(b) first-byte grouping** — stable-group by first byte, try only the
  subject byte's group, original order within it.
- **(c) sorted trie, priority-tagged accepts** — `src/ir/nfa.c:192`'s M2.8
  trie, ported to a walk: descend the subject's own path, collect every
  accept passed, answer the lowest original index. Exact; see the design
  doc for the argument and for what a genuinely overlapping class (this
  study's inputs never produce one) needs instead.
- **(d) k-byte block hash** — `[OPT-ALTHASH]`: hash the next k (2 or 4)
  subject bytes into a table over the branches' distinct k-byte prefixes;
  branches shorter than k take the per-byte (here: serial) path.
- **(e) VM-native trie walk** — ruling R1's PRIMARY candidate: (c)'s SAME
  trie, but the walk COMMITS (pushes one resumable frame, stops) the
  instant a passed end node's index can be proven to beat everything else
  still live, and DEFERS (records into a small ascending list) otherwise.
  Exact — see the design doc §3.2, including a correctness subtlety the
  ruling's own wording does not spell out. Pushes at most one frame per
  dispatch on every input this study measured.
