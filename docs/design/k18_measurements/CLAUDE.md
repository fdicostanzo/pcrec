# docs/design/k18_measurements/ — the K18 design lane's instruments

Everything `../k18_memo_design.md` cites. Kept so the note's numbers can be
re-run rather than believed, and so the rewrite lane inherits the harnesses
instead of rebuilding them.

**Nothing here is a proposed patch.** The prototypes rewrite `src/ir/dfa.c`
inside a SCRATCH COPY of the tree (`prototypes/mkproto.sh`), never in the
worktree, so `build/`, `make test` and the known-fail ratchet only ever see
the unmodified compiler. Each prototype is a python script that does anchored
textual surgery on `dfa.c` and asserts on its own anchors, so a source change
that moves them fails loudly instead of silently patching the wrong thing.

## Prototypes

- `prototypes/mkproto.sh NAME [script.py]` — tar the worktree (minus `.git`,
  `build*`, `worktrees`) into `$K18_OUT/NAME`, apply the script, `make`.
  `mkproto.sh base` with no script builds the unmodified control.
- `prototypes/proto_a.py` — **A**: the recorded direction. Open-loop stack
  along the walk's path, interned to context ids; memo keyed on (state, ctx);
  the redirect fires on "this loop is OPEN on my path". Separate global
  per-state dedup for `N_CLASS` emission. `PCREC_K18_STATS=1` prints one
  `K18STATS` line per `pcrec_build_dfa`.
- `prototypes/proto_a2.py` — **A2**, the RECOMMENDED shape: A plus the
  empty-context fast path (ctx 0 uses the shipped per-state stamp array, no
  hash). Answer-identical to A — verified byte-for-byte on 19,413 patterns.
- `prototypes/proto_b.py` — **B**, the rejected cheap alternative: two lines,
  an already-seen `N_EPS` is walked through instead of killing the walk.
  Passes the whole K18 acceptance corpus and is still inexact; that is the
  note's central comparison.
- `prototypes/proto_c.py` — **C**: A with the memo deleted. Exists only to
  price the memo, since A and C give the same answers. Carries a 3e8-visit
  budget so a blowup is a number (exit 97) rather than a hang.
- `prototypes/proto_basestats.py` — the UNMODIFIED closure with A's counters.
  The denominator for every inflation figure. It must emit byte-identical C to
  `base`, which is the check that the instrumentation is inert.
- `prototypes/proto_dump.py`, `prototypes/proto_dumpA.py` — `PCREC_K18_DUMP=1`
  prints the NFA, `PCREC_K18_TRACE=1` traces every closure step with its
  verdict, on the shipped closure and on A respectively. The note's before/after
  traces are their output, so neither is a hand reconstruction.

## Harnesses

- `harvest_patterns.py` — every `pattern` line in `tests/**/*.rxt`, deduped.
- `gen_shapes.py` — the DENSE shape-space sweep (18,858 patterns) built only
  from K17/K18's ingredients. The general fuzzer hits this class at ~1e-4,
  which cannot tell two candidate repairs apart; this can.
- `gen_adversarial.py` — the families that are supposed to make a
  path-sensitive memo blow up: nested nullable stars, sibling nullable loops,
  bounded repeats, wide nullable alternations.
- `k18_stats.py` — run a prototype over a pattern list, collect its counters.
  Sums across the forward and reverse machines, maxes the ceilings, and reports
  refusals rather than silently shrinking the denominator.
- `summarise.py` — distributions of the cost-bearing counters for one run.
- `inflation.py` — per-pattern ratio of one counter run over another.
- `emitdiff.py` — emitted-source blast radius between two binaries. The net
  `tests/codegen/run_trie_identity.sh` argues for over subject sampling,
  because it cannot miss a difference the sampled subjects fail to reach.
- `oracle_cmp.py` — the question a design comparison actually has to answer:
  where two binaries DISAGREE, which one matches python3 `re`. Reports
  both-wrong cells separately, since those are not a difference between
  candidates.
- `timecmp.py` — alternating min-of-N compile timing for two binaries. Note
  its floor: this box spawns a process in ~1 ms, so per-pattern ratios on
  sub-5 ms patterns are noise, and only aggregates and expensive patterns mean
  anything.

- `r23_semantics/` — the R23 panel's semantics-critic toolkit, archived as
  evidence (see its README): the S16 stack-fix prototype, shadow/dup
  counter prototypes, the §1.4 half-prototypes, independent generators and
  sweep harnesses behind docs/dev/reviews/2026-08-15-r23-k18-memo.md.
  Static, like `outputs/`.

Maintenance: update this file when files are added/removed or change roles.
