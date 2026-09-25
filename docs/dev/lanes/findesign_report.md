# Lane `findesign` report: [FINDINGS] step 2, the design note

**opus, 2026-09-25, branch `lane/findesign` from main `f94b9dd8`. DESIGN
ONLY.** No `src/`, `cli/`, `lib/`, `tests/` or `docs/spec/` edits and no
`make test`. There was one `make` (the lane's worktree build, used to read
an artifact's stamps) and small read-only probes over RUNEST's committed
data.

## Deliverable

- `docs/design/findings/design.md`: the design note, §0–§17.
- `docs/design/findings/CLAUDE.md` and `docs/design/CLAUDE.md`: index
  entries.

## Summary (a fresh agent can resume from this)

**Data model.**
- A bundle is one file-scope `analysis <name>` block holding at most one
  block per kind (`freq`, `cpfreq`, `bigram`) and an optional
  `include <other>`.
- Blocks store sparse COUNTS as hex-keyed ascending rows.
- Applicability is DECLARED per block as `serves <query> when <enc,…> via
  <derivation>`, drawn from closed vocabularies (queries `byte-rate` and
  `run-rarity`; derivations `unigram`, `encode-utf8`, `encode-latin1`,
  `markov1`). `encoding` only describes the data.
- A query is answered by the first block along the chain that declares it
  for the compile's `-e`, and exactly one block answers each query.

**Resolution (Route I, decided).** Names are looked up in three stops, in
order:
- S1: the compile's own `.rxt` closure (or in-memory library text);
- S2: `-I DIR/<name>.rxt`;
- S3: the embedded store.

Two rules sit on top of that. A self-named `include` uses include_next
semantics. The chain's terminal is the built-in `default`, taken by
identity rather than looked up by name.

**The accessor.** `src/core/findings.c` exposes three calls:
`pcrec_find_byte_rate`, `pcrec_find_set_mass` and `pcrec_find_run_rarity`.
All arithmetic is integer: the normalization and the Q16 `L(x)` are
specified. Every call is recorded for the stamp.

**Stamp.** `<P>_FINDINGS` plus `rx_info.findings` carry a
`query=bundle:fnv64` item for each query consumed. This takes abi from 32
to 33, and the prior-gate move rides the same bump.

**Store.** The shipped `.rxt` text is embedded at build time and parsed by
the same reader as user files.

**Analyzer.** `pcrec-analyze`: a python prototype first, then a C binary.
It reads stdin, takes `--scan` switches, and parallelizes with `--shard`
(seam overlap) and `--merge` (order-independent).

**Build plan.**

| step | content |
|---|---|
| B0 | format |
| B1 | accessor + default + abi 33 |
| B2 | resolution / CLI / library / the findings axis |
| B3 | python analyzer |
| B5 | shipped `log` / `weblog` + `cpfreq`, each gated by its R35 census |
| B4 | `bigram` + its first reader (S4(a)) |
| B6 | C analyzer |

**Findings the design rests on (§0).**
- RUNEST's "128 KB at 2-byte ppm" cannot hold conditional rates: 226–317
  cells per class exceed 65,535 ppm (MEASURED from RUNEST's own
  `data/tables`). The tables are also sparse, at 471–3,288 pairs.
- `-I` is refused without a file operand (`cli/main.c:1600`).
- Per-kind fall-through needs a one-block-per-query rule.
- Self-shadowing needs include_next.
- A sharded bigram merge needs a one-byte seam overlap to stay
  order-independent.
- The terminal default must not be resolved by name.
- The default's byte identity follows from the normalization arithmetic
  itself.
- `prefix_k` needs a declared NONE fallback: cardinality.
- `log` has no licensable source yet.
- Provenance's data-parent conditions do not fit authored or private data.
- Embedding the store as TEXT gives one reader.

**Open to Frank (§16).**
1. The built-in-default terminal is by identity (recommended).
2. `log`'s sourcing: recommended (a) a sourcing lane, falling back to (b)
   synthesized.
3. No path sugar for `--analysis` (recommended).

## Validation

Design-only lane, so no suites are owed. The only measurements are the
read-only RUNEST-data probes cited in §0.1 and §8.3, reproducible from
`docs/dev/findings_measure/data/tables/*.json`. A D6 critique loop
follows.
