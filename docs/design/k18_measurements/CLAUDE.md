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
  **AMENDED 2026-08-15 (R23 S3/S16):** `clo_visit` now saves and restores the
  open-loop stack's ENTRIES, not only its depth. The first version restored
  depth alone, which let a redirect crossing a frame boundary overwrite an
  ancestor's entries; that one omission was the whole of the note's original
  cost residual (44 s → 0.35 s at the parser's nesting cap) and the cause of
  `nonstacktop` firing where §2a reported 0. The save is deliberately NAIVE
  (a malloc per frame) so no number taken on this prototype can be accused of
  hiding the fix's cost — every cost figure in the note is an upper bound on
  a bump-allocated equivalent. C and A2 inherit it, since both derive from
  this script.
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
  bounded repeats, wide nullable alternations. 70 patterns, 7 families.
  **FIXED 2026-08-15 (R23 M-B1):** `altnest` and `k18nest` appended the outer
  `*` to a body already ending in `?`, so all 18 of their patterns were
  `?*` — invalid in every engine. The two families named after K18's own
  shape therefore contributed ZERO patterns to every measurement the note
  called "52 adversarial patterns", and nothing disclosed it: `k18_stats.py`
  printed `refused=18` on stderr and the number never reached the prose. Both
  now wrap (`"(?:%s)*"`), all 70 compile, and the note's §2a discloses the
  old denominator.
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
- `timecmp.py` — alternating min-of-N compile timing for two binaries.
  **AMENDED 2026-08-15 (R23):** it now MEASURES the per-invocation floor per
  binary and per run (min over 15 compiles of `a`) and reports the aggregate
  both raw and net of it, because a raw aggregate over cheap patterns compares
  the two arms' `fork`. Its docstring carries the two lessons this cost round
  produced: never time pcrec from a shell loop with `date` (the note's
  original table read 0.12 s for everything, which was the shell's overhead
  and hid a 100x prototype defect by making every cheap compile look
  identical), and subtracting a floor does not create resolution — on the
  555-pattern corpus the net swings through zero between trials, so **the
  corpus is priced with the COUNTERS** (`k18_stats.py` + `inflation.py`), not
  the clock. Use the clock for patterns costing milliseconds or more.

- `r23_semantics/` — the R23 panel's semantics-critic toolkit, archived as
  evidence (see its README): the S16 stack-fix prototype, shadow/dup
  counter prototypes, the §1.4 half-prototypes, independent generators and
  sweep harnesses behind docs/dev/reviews/2026-08-15-r23-k18-memo.md.
  Static, like `outputs/`.
- `capdiff/` — the CAPTURE-OFFSET differential `../k18_memo_design.md` §4.6
  flagged as owed: every measurement above is spans-only. Builds
  capture-bearing patterns on the K18/K17 axes (plus a mandatory-leading-
  atom cross forcing the reverse machine to compute a non-trivial match
  start — the axis R23 found the stack-entry corruption on) against the
  CURRENT (post-K18-fix) `build/pcrec`, comparing the default DFA-
  prefiltered VM build against python `re`, libpcre2 and a prefilter-free
  `--engine=vm` build. Also documents a load-bearing finding about the
  current [M4.5]/[M4.6] wiring: the hybrid search entry consumes only the
  DFA prefilter's computed START, never its END, so a K18-class defect
  (which corrupts the FORWARD machine's computed END) cannot reach a
  capture for the fully-nullable-at-offset-0 shapes this directory's own
  and the original K18 corpus are built from — narrowing where a defect
  could actually propagate to the REVERSE machine's START computation. See
  its own CLAUDE.md for the corpus, the instruments and the positive
  control.

Maintenance: update this file when files are added/removed or change roles.
