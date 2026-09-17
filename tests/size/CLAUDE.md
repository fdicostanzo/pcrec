# tests/size — the artifact-size metrics log + corpus-level tripwire

[ART-SIZE.1b] (docs/dev/plan.md): the zero-cost size ratchet riding
`test-corpus`'s existing compile pass. The wrapper and the check measure a
population that is the whole tree's rather than one of their own, discovered by
`tests/harness/run.sh` exactly as `test-corpus` always has.

## Files

- **run_size_log.sh** — drop-in replacement for `test-corpus`'s own
  `bash tests/harness/run.sh` recipe line (see the Makefile's `test-corpus:`
  target): threads `SIZELOG` through the SAME compile pass (no second gcc
  invocation anywhere — "riding the existing corpus" is the whole charter),
  then — ONLY on a full-corpus invocation (no file/dir arguments, matching
  `run.sh`'s own "no args = every `*.rxt` under `tests/`" rule) — assembles
  the raw rows into the stable, diffable `docs/dev/artifact_size_log.tsv`
  (D35's shape: stable filename, `git diff` shows what moved; deliberately
  NOT under `docs/measurements/` itself — see that file's own CLAUDE.md
  entry for why). A partial/targeted run (explicit files given) still gets
  raw rows at whatever `SIZELOG` path the caller sets directly, but this
  wrapper's own stable-file assembly is skipped — a developer's five-file
  spot-check must never silently overwrite the whole corpus's baseline.
  Exit code is `run.sh`'s own; an assembly problem is reported to stderr
  but never turns a passing corpus run red on its own — `check_size_tripwire.sh`
  is the separate step that can fail the build.
- **check_size_tripwire.sh** — THE ONE RED THIS ROW PRODUCES: the corpus-level
  max size and max gcc-CPU time seen in `docs/dev/artifact_size_log.tsv`
  (or `$ARTSIZE_LOG`), each pinned with headroom over the [ART-SIZE] census's
  own measured numbers (docs/dev/artifact_size_census.md) — see the script's
  own header for why the pins are NOT the census's raw numbers (a different
  compile shape: `-O1` compile+link with `driver.c`, not an isolated
  `-O2 -c`). PLUS the UNPINNED-MAX GUARD: a log that is empty, truncated
  after its own header was written, or below a hardcoded population floor
  fails LOUD rather than reading as "no blowup found" — the check-design
  lesson (memory `pcrec-check-design-lessons`) that a floor without a
  vacuity check measures nothing. A failure names the offending pattern,
  its number, the ratio over the pin, and the load at measurement. NO
  per-pattern gate exists anywhere in this directory — Frank's ruling on
  docs/dev/plan.md's [ART-SIZE.1b] row is explicit that per-pattern
  movement is examined post-test (`scripts/size_diff`), never gated.
  `make test-size` is the STANDALONE post-test check; in `make test` the tripwire runs as the tail of test-corpus's own recipe (a `test-size: test-corpus` prerequisite was skipped by `make -k` whenever the corpus's load cell went red — see the
  Makefile's own comment on why this is a deliberate, narrow exception to
  "no suite reads another's output": it runs strictly after test-corpus,
  reads a stable file-scoped artifact test-corpus produces as a byproduct,
  never a shared mutable workdir).

## Format of `docs/dev/artifact_size_log.tsv`

```
# artifact_size_log.tsv (docs/dev/plan.md [ART-SIZE.1b]) commit=<sha> date=<ISO8601 UTC> load1_at_start=<float> rows=<N> harness_args=(full corpus)
# pattern	engine	rungs	prefilter	size_bytes	gcc_cpu_s	gcc_wall_s	load1
<file>:<pattern-line>	dfa|vm	0x..|	hybrid|none|	<int>	<float>	<float>	<float>
...
```

`pattern` is `file:line` (the `.rxt` block's own coordinates), not the
regex text — stable across an emitter change, greppable straight back to
the corpus. `size_bytes` is the SELF-CONTAINED artifact's size (`.c`+`.h`
combined — the census's own correction, docs/dev/artifact_size_census.md
§6) with COMMENTS EXCLUDED, per `tests/lib/size_count.sh`'s definition
(verified byte-exact against the census's own Python classifier — see that
file's header and docs/testing.md's transcript).

**THE LOG'S POPULATION IS THE `.rxt` CORPUS, AND THE TREE IS BIGGER THAN
IT.** One row per corpus compile — so a pattern that lives anywhere ELSE gets
no row, and the tripwire's "worst size" is worst of THIS population, not of
everything pcrec compiles in this tree. MEASURED at r41 (2026-08-29):
`tests/resource/run_resource_tests.sh`'s giant-repeat shapes live in a BASH
ARRAY, and one of them — `[a-z]{0,30000}` — is the largest artifact the tree
produces at **1,336,143 B**, larger than any of the log's 2,875 rows and
within 5 % of `MAX_SIZE_BYTES`. An [ENG-ABS] draft briefly took it to
1,984,382 B, **over the pin**, and the tripwire could not have said so. If a
change can grow an artifact, ask which artifacts it can grow before reading
this log's worst row as the tree's worst.

**"COMMENTS EXCLUDED" IS LINE-BASED, AND AN EMITTER AUTHOR HAS TO KNOW
WHICH LINE.** The classifier recognises a line that STARTS a block (`/*`, or
`//`) and tracks the block to its end. A comment placed ABOVE a declaration
therefore costs zero counted bytes; the CONTINUATION lines of a comment that
begins after code on the same line — the `int x;   /* first line` … shape —
do not start a block and are counted as CODE. MEASURED at [ENG-ABS]
(2026-08-29): one new `rx_info` member whose comment used the trailing shape
put **+691 B into every one of the corpus's 2,875 artifacts** and moved the
corpus total 7.82 %; moving the same comment above the member took the
per-artifact cost to 38 B. Nothing is wrong with the classifier — a trailing
comment's continuation lines genuinely are not a block opener — but "the
emitted comments are free" is true only of the first shape, and the emitted
`struct rx_info` still carries two members (`scan`, `prefilter`) in the
second. `engine`/`rungs`/
`prefilter` are the D46 stamps (`RX_ENGINE`/`RX_VM_RUNGS`/
`RX_VM_PREFILTER`) read straight off the artifact; empty when the artifact
has no such stamp (a DFA artifact carries no rungs/prefilter at all).
`gcc_cpu_s` is user+sys CPU time (NOT wall) for the exact compile
`test-corpus` already performs (compile+link `gen.c`+`driver.c`, `-O1`);
`gcc_wall_s` rides along for comparison. `load1` is `/proc/loadavg`'s
1-minute figure at the moment that row's compile finished, so a
CPU-time reading taken under real contention is distinguishable from a
genuine blowup (the same load-context discipline `tests/lib/load_guard.sh`
uses one layer up).

## Measured overhead

The naive first cut (2x `awk` for size, 3x `sed` for stamps, 1x `awk` for
a CPU sum, 1x `cut` for load, 1x `grep` to parse `time`'s own output — 8
subprocess spawns per compile) cost **20.4%** of `test-corpus`'s own wall
time (75.6s -> 91.1s over 712 artifacts, `tests/base/*.rxt` at `PROCS=2`).
Consolidated into ONE subprocess per compile (`tests/lib/size_count.sh`'s
`size_count_row`, folding the size scan and the D46 stamp grep into a
single `awk` call) plus pure-bash arithmetic for the CPU-time sum and the
load reading (no `awk`/`cut`/`grep` at the call site at all): **1.79%**
(76.75s -> 78.13s, same 712-artifact sample). See
`tests/harness/run.sh`'s SIZELOG call site for the mechanism and
docs/testing.md "The artifact-size log" for the full transcript.

## Conventions

Nothing here writes into `tests/` (the harness's own compile output stays
under its own `mktemp -d` workdir, as always) — the log lands under
`docs/dev/`, never here. `run_size_log.sh` and `check_size_tripwire.sh` are
both read-only against `build/pcrec`/`build/libpcrec.a`, same as every
other section.

Maintenance: update this file when files are added/removed or the log
format changes.

- **size_term.rxt** — [ART-SIZE] STEP 2's ANSWER cells (added 2026-08-29).
  The only `.rxt` in this directory, and it is here because it belongs to the
  size row rather than to any construct's module. Everything structural about
  the size term — its stamps, its two caps, `cap-rescue` — lives in
  `tests/codegen/run_size_term.sh`; this file holds only what a MATCH would
  notice. Its first block is r40 finding R1's witness, the pattern that
  compiles at K=8 and refuses at K=6: a ladder that let a trial's refusal
  escape would break it, so a cell that merely matches is the regression test
  for the blocker. `engine vm` on that block is REQUIRED — on the default axis
  the pattern refuses earlier at NFA construction, and the cell would then
  pass for a reason unrelated to what it tests.

- **tune_dial_fixtures.rxtin** — [OPT-DIAL] design section 6.2a's NEAR-CAP
  FIXTURE FAMILY (added 2026-09-17, lane dialimpl), the r53 precedent
  ("synthetic ladders are corpus members") applied to `--tune=N`'s own
  refusal-set acceptance (design section 6.2: "no dial position may select a
  switch value that moves the refusal set, in either direction"). Three
  blocks, F1/F2/F3 in the design's own naming, each with the exact measured
  byte counts at every `--tune` position in its own header comment so a
  reader (or `tests/codegen/run_tune_dial.sh`, being built concurrently by a
  sibling lane at the time this file was written) does not have to re-derive
  them:

  - **F1** sits just under `PCREC_MAX_EMIT_BYTES` (1,000,000) at `balanced`
    (`[^\p{C}\p{M}\p{S}]`, a synthetic property-class DFA artifact,
    967,510 B) and shows the GROWTH direction holds: `+1`/`+2` move it by at
    most 8 bytes (the `RX_TUNE` stamp string's own length, not the
    entry-chain term — this artifact has no VM program at all to raise a
    term on). It ALSO carries a finding that is not F1's own claim: at
    `--tune=min-size` the SAME artifact drops to 578,203 B (a 40% shrink),
    which is `-fno-premul-table`'s own documented savings landing on an
    unusually table-heavy machine — see F3.
  - **F2** sits just under `PCREC_MAX_VM_EMIT_CODE_BYTES` (500,000) at
    `balanced`, VM-compiled (a 272-branch literal alternation,
    python-oracle-verified, 499,092 B of code) and holds under the cap at
    every position (906-916 B of headroom throughout). **The entry-chain
    term itself is NOT exercised here** — this witness's own emitted VM
    program is ~499,000 bytes, five orders of magnitude past even the
    raised 8,192-byte threshold, so `shared` is selected at every position
    and the raise is a structural no-op on it. A witness whose OWN program
    sits inside 4,096-8,192 bytes while its surrounding artifact ALSO
    approaches the code cap would need CODE bytes from something other than
    the VM program itself (a hybrid's code overhead is small and roughly
    constant regardless of its table size, since table bytes are excluded
    from "code" by definition) — none was found in the time this row had;
    stated here rather than silently substituted with a weaker claim.
  - **F3 WAS the OPPOSITE direction and is now the FIXED shape**
    (2026-09-17, lane k59rung). It was authored `perr` at `balanced` — a
    MEASURED violation of design section 6.2's own rule, filed as
    `docs/dev/known_issues.md` K59: `[^\p{C}\p{M}\p{P}]` refused at
    `balanced`/`size`/`speed`/`max-speed` (1,027,196-1,027,206 B, over
    `PCREC_MAX_EMIT_BYTES`) and compiled at `--tune=min-size` (608,196 B),
    because `-fno-premul-table`'s unconditional `-2` denial was rescuing a
    pattern no other position could reach. **The fix generalizes rather
    than narrows**: `[K53-SELRETRY]`'s drop ladder gained a second rung
    (`SDR_NO_PREMUL`) that denies the same flag on a DFA-engine artifact's
    own retry, so the rescue the `-2` cell was reaching alone now fires
    from every position on the patterns that need it. The block is now a
    live `pattern`/`m`/`n` block (not `perr`) asserting the fix directly:
    all five positions compile, and match "A" / refuse "!" / "" / "\x01"
    identically at every one of them — the refusal-set-move claim inverted
    into an answer-identity one. `tests/codegen/run_tune_dial.sh` section 6
    re-derives the same table per position and additionally asserts WHICH
    drop-ladder rung(s) fired (via `RX_ENGINE_SEL`/`RX_DFA_MATCH`/
    `RX_DFA_TABLE`) and that the verbose stderr note (Frank's addendum
    ruling) fires exactly there. `src/core/tune.c`'s `-2` cell is
    UNCHANGED — narrowing it was disposition 1, not taken.

  `.rxtin`, not `.rxt`, and that is a departure from the r53 precedent's
  letter forced by this lane's own scope: `tests/rxtsource/
  run_rxtsource_tests.sh` pins a `CENSUS_FILES`/`_BLOCKS`/`_LINES` count over
  every `*.rxt` file in the tree and that script sits outside `tests/mech/`
  and `tests/size/`, so a plain `.rxt` here would move a pin this lane
  cannot also re-pin in the same commit. Kept off `find tests -name
  '*.rxt'` and off the automatic `make test` sweep by the same convention
  `tests/rxtsource/fixtures/*.rxtin` already uses; invoke it explicitly
  (`bash tests/harness/run.sh tests/size/tune_dial_fixtures.rxtin` — 7/7 at
  authoring, confirmed) or `python3 tests/harness/verify_rxt.py tests/size/
  tune_dial_fixtures.rxtin` (F1's three cells use `\p{...}`, which python
  `re` cannot parse at all — SKIP, not `# pcre2-only`, since there is no
  python EXPRESSION to mark; F2 and F3 verify against python `re` directly).
  Whoever wires `run_tune_dial.sh`'s own acceptance should read the sizes
  from this file's own header comments rather than re-measuring them,
  and re-measure only if `src/core/tune.c`'s table or `SIZE_TERM_BAR_DEFAULT`
  moves under it.

