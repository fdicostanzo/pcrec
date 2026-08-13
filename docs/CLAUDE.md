# docs/ — project working documents

Process and status documents for pcrec. The architecture itself lives in
../APPROACH.md; these files track execution against it.

## Subdirectories

- `dev/` — development-process documents: tracking execution, not the
  product (plan, journal, decision log, known/upstream issues, checkpoint
  reviews). See `dev/CLAUDE.md`.
- `design/` — living design documents: describe the design AND the
  process/learning of building it (panel-outcome blocks, refutations
  inline). See `design/CLAUDE.md`.
- `spec/` — spec documents detailing how the tool and its surfaces actually
  work and how to use them; deliverables like code, actively maintained, no
  build history. Empty today — see `spec/CLAUDE.md` for the charter.

## Files

- `pcre2_compliance.md` — construct-by-construct compliance against PCRE2's
  syntax reference, with a status vocabulary that separates verified from
  believed and clean-rejection from miscompile. Periodically re-surveyed;
  its `REJECTED` rows are backed by tests/reject/ rather than asserted.
- `testing.md` — .rxt test-file format, harness usage, env vars, oracle
  exclusions, how to add a per-module test directory, and (added [TT-1])
  "Tiered testing": the measured per-section runtimes behind `make
  test-corpus`/`test-cli`/etc., the touched-path -> sections guidance table,
  `make smoke`'s measured composition and floor check, and the opt-in
  `make hooks` pre-push gate. `make test` itself is unchanged by any of this
  — still the full suite, still the merge/close standard. Also (added
  [SAN-1]) "Sanitizer + lint battery": make ubsan/asan/lint both-axes
  targets, the GENCFLAGS compile-site audit, LINTGEN=1, the findings
  inventory (F1), sabotage validations, quiet-box runtimes, and the
  battery-placement ruling (ubsan+asan+lint join the merge/close battery;
  smoke never).
- `measurements/` — archived probe OUTPUT reports (D35, 2026-08-12):
  stable-named (`<probe>.txt`, diffable across re-runs) verbatim probe
  output with a source-information header (date, repo commit, libpcre2 and
  gcc versions), written by `scripts/measure.sh`. Evidence for reviews,
  never an oracle — no check reads them. See the directory's own CLAUDE.md.

Maintenance: update this file when files/subdirectories are added/removed or
their roles change.
