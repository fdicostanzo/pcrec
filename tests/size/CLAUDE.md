# tests/size — the artifact-size metrics log + corpus-level tripwire

[ART-SIZE.1b] (docs/dev/plan.md): the zero-cost size ratchet riding
`test-corpus`'s existing compile pass. The wrapper and the check measure a
population that is the whole tree's rather than one of their own, discovered by
`tests/harness/run.sh` exactly as `test-corpus` always has.

## Files

- **run_size_log.sh** — drop-in replacement for `test-corpus`'s own `bash tests/harness/run.sh` recipe line (see the Makefile's `test-corpus:` target): threads `SIZELOG` ...
- **check_size_tripwire.sh** — THE ONE RED THIS ROW PRODUCES: the corpus-level max size and max gcc-CPU time seen in `docs/dev/artifact_size_log.tsv` (or `$ARTSIZE_LOG`), ...
- `docs/dev/artifact_size_log.tsv` — section "Format of `docs/dev/artifact_size_log.tsv`" (history file)

## Why `docs/dev/artifact_size_log.tsv` stays TRACKED (admin88, 2026-09-30)

The log shows dirty in `git status` after every full `test-corpus` run
because `run_size_log.sh` rewrites it (new commit/date/load1 header, fresh
timings). That is by design, not a leak, and the verdict is KEEP IT TRACKED
(untracking it was considered and rejected). Evidence:

- **A check reads the committed copy.** `check_size_tripwire.sh` (and so
  `make test-size`, the standalone post-test step) reads it and FAILS with
  "size log not found" when it is absent; on a fresh clone the tracked file
  is what `make test-size` has before any corpus run, and it is the
  baseline `scripts/size_diff OLD NEW` and `docs/dev/optdial_size_sweep.md`-
  style comparisons diff against. (Inside one `make test` the corpus
  rewrites it first, so the tripwire reads the fresh copy there.)
- **The log IS the deliverable** (Frank's [ART-SIZE.1b] ruling: per-pattern
  movement is "a `git diff` a reviewer reads"). `git log` holds 44 commits
  on it, committed deliberately at gates ("size log re-archived at the
  <gate> (0 movers)"), which is the ratchet's whole history.

Working rule: a dirty copy after an ordinary run is noise — leave it out of
your commit (`git restore docs/dev/artifact_size_log.tsv`). Commit it only
as a deliberate gate re-archive from a CLEAN, FULL, DEFAULT-axes run (never a
`HARNESS_BATCH` run: batch-mode SIZELOG CPU/wall are compile-only,
`docs/dev/tt4m_time.md`), after reading `scripts/size_diff` for movers.

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

(Rest of this section: see the history file.)

History (long narrative moved verbatim, not auto-injected): `docs/dev/history/claude_md/tests__size.md`.
