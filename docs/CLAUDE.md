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
  build history. **[M4.7f], 2026-08-18: first document landed** —
  `match_api.md`, the as-built match-API contract, graduated from
  `docs/design/match_api_m4.md`/`engine_m4.md` per D40. See `spec/CLAUDE.md`
  for the charter and file list.

## Files

- `pcre2_compliance.md` — construct-by-construct compliance against PCRE2's
  syntax reference, with a status vocabulary that separates verified from
  believed and clean-rejection from miscompile. Periodically re-surveyed;
  its `REJECTED` rows are backed by tests/reject/ rather than asserted.
- `pcre2_options.md` — [PC-5]'s option-by-option sibling survey: every
  PCRE2 compile/match/dfa-match/substitute flag, `EXTRA_*` bit and
  BSR/NEWLINE value, each with a PROPOSED pcrec disposition (Frank rules)
  from a fixed vocabulary (DONE-AS/RIDES/GENERATION-AXIS/API-PARAM/
  EMITTED-LOOP/LATER/NEVER) and a `ruling` column left for him to fill in.
  Fiddly semantics are measured against libpcre2 (probe + transcript in the
  Measurement Appendix), never read from documentation alone. Restates the
  standing constraint that the suite's oracle is pinned at options=0, so
  adopting any flag is a deliberate re-measurement event. Points to DD-11
  (NEWLINE/BSR) and DOC-BM (`EXTRA_*` dispatch effects) rather than
  re-deriving their territory. **RULED (D38, 2026-08-14):** the `ruling`
  column is filled wholesale (`RATIFIED 2026-08-14 (D38)`, three rows
  ruled individually — LITERAL, DFA_SHORTEST, COPY_MATCHED_SUBJECT); rows
  stay individually re-openable. Also carries the D38 naming-scheme
  addenda: the native surface is uniformly `PCREC_*`, `PCRE2_*` is
  compat-only.
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
  smoke never). Also (added [M4.5a]) "Capture-group expectations": the
  `g`/`gp` `.rxt` line kinds for per-group capture-slot spans, the
  live-vs-pending-VM population-accounting rule (an out-of-range `g` is a
  hard failure, an out-of-range `gp` is counted separately and
  self-activates once `RX_NCAPS` grows to cover it), and the python-`re`
  oracle tier that checks both identically.
- `measurements/` — archived probe OUTPUT reports (D35, 2026-08-12):
  stable-named (`<probe>.txt`, diffable across re-runs) verbatim probe
  output with a source-information header (date, repo commit, libpcre2 and
  gcc versions), written by `scripts/measure.sh`. Evidence for reviews,
  never an oracle — no check reads them. See the directory's own CLAUDE.md.

Maintenance: update this file when files/subdirectories are added/removed or
their roles change.
