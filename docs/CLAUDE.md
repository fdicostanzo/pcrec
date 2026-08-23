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
  **[DOC-DRV] (2026-08-21) RESTRUCTURED THE PAGE INTO THREE COMPONENTS OF
  DIFFERENT PROVENANCE, held in checked tension** — chartered by the wave-E
  confusion below, carried by the `compliance-refresh` skill:
  (1) **generated facts**, the "Registry construct index" at the file's end,
  printed by `pcrec --list-syntax` (unchanged from SR-4/D65, below);
  (2) **the independent survey**, every section's hand-written `syntax |
  status | becomes` table — deliberately never generated from the registry,
  since its value is answering "what does PCRE2 have that the registry
  doesn't even list"; (3) **keyed annotations**,
  `docs/pcre2_compliance_annotations.txt` — the measurements and judgment
  that used to sit inline in each row's notes column, now construct-KEYED
  (90 records, migrated from ~90 prose rows plus three section-level
  analysis blocks) and rendered back per section by
  `tests/registry/compliance_section.py --write-annotations`, checked for
  staleness by `--check-annotations` (a key naming a construct that no
  longer exists, or a page render that has drifted from the store, fails
  `make test` naming it) — the mechanism that retires the recurring failure
  the wave-E incident below is one instance of. `--tension` reports the
  checked-tension between components 1 and 2 (informational). See the
  page's own intro section and `.claude/skills/compliance-refresh/SKILL.md`.
  **TWO SURFACES CONFUSED A LANE ONCE** ([M6.2] wave E, 2026-08-19), the
  incident [DOC-DRV] exists to retire the recurrence of: the hand-written
  PROSE rows carried the shipped status (`OK`, `OK-GATED`, `OK-LIMITED`)
  and the GENERATED index at the bottom's `status`/`roadmap` columns are
  the registry's own two fields, where `REJECTED | planned` means "not
  BASE grammar; the `module` column names the owner" — true identically
  for a shipped construct (`\d`) and an unbuilt one, which is what 34 rows
  of SHIPPED modules read (`classes` 12, `modifiers` 12, `assertions` 7,
  `named-groups` 3, measured 2026-08-19) and what the wave-E lane misread
  as module-specific staleness.
  **[D65] (2026-08-21) THE GENERATED INDEX ANSWERS THE QUESTION
  DIRECTLY**: a `built` column (`built`/`unbuilt`/`—`), derived live per row
  by `pcrec_construct_built_status` (docs/design/registry_built_status_memo.md,
  ratified wholesale) — never a hand-declared field. Of the 34 "shipped"
  rows above, 33 read `built` and one, `(?J)`, reads `unbuilt` (module
  `modifiers`' own permanent DUPNAMES decline), a distinction the old
  per-module count could not express. The file's "How to read the
  generated index below" section explains the column; docs/design/CLAUDE.md's
  own entry on the memo carries the design record and rulings.
- `pcre2_compliance_annotations.txt` — [DOC-DRV]'s KEYED ANNOTATION STORE,
  component 3 of `pcre2_compliance.md`'s three-component model above: one
  record per construct (or bundled group of related spellings), format
  documented in the file's own header. Data, not prose — never read as a
  reference document on its own; edit it and run
  `tests/registry/compliance_section.py --write-annotations` to render the
  edit into `pcre2_compliance.md`.
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
  oracle tier that checks both identically. Also (added [TT-3], 2026-08-21)
  "Compile caching (`CCACHE=1`)": the opt-in ccache toggle, its two
  diagnosed-and-fixed blockers (compile+link shape, then a per-case
  `-I<tmpdir>` flag plus `hash_dir` under `-g`), and the MEASURED verdict —
  a clear NO for `make test` (real 64.59% hit rate, still 4x+ plain's wall
  time — the workload is thousands of sub-millisecond compiles, the wrong
  shape for caching's own overhead), a qualified YES for `make mech`'s
  per-sabotage tree rebuild (25-29% faster warm, single-row samples). Also
  (added [TT-7], 2026-08-23) "[TT-7] combined axis": `make san`, ONE
  combined `-fsanitize=address,undefined,leak` axis proposed in place of
  running `ubsan` then `asan` (75m00s measured for the two separate passes
  at m65, `docs/dev/chain_profile.md` candidate (a)) — diagnosis
  distinctness verified small-scale, D45's budgets confirmed
  byte-identical to either single axis, `ubsan`/`asan` left untouched.
  ADOPTED 2026-08-23 (manager timing run: `make san` 45:50 vs
  ubsan+asan 63:43, identical PASS population, zero reports) — the
  battery's sanitizer stage is `san`; ubsan/asan stay as opt-in singles.
  (added [TT-6], 2026-08-23) "The `timeout` binary itself (`TIMEOUT_BIN`)":
  this box's default `timeout` is uutils coreutils 0.8.0 (~108.7ms pure
  wall per call, ~0 CPU) against GNU coreutils' ~4.2ms; `tests/lib/
  timeout_bin.sh` resolves and announces a faster binary once per process
  and every suite's bare `timeout` call was swapped to `"$TIMEOUT_BIN"` —
  MEASURED 6.31x wall on an isolated `make test-corpus` run (identical
  case counts before/after), a wash on the full `-j12 -Otarget make test`
  total (concurrent sections hide a sleeping worker's wall time), and a
  named finding that two `tests/bench/run_bench.sh` budgets (COMPILE-SPEED,
  GCC-TIME) measured the wrapper's own launch cost inside their number and
  now read lower and more honestly.
- `measurements/` — archived probe OUTPUT reports (D35, 2026-08-12):
  stable-named (`<probe>.txt`, diffable across re-runs) verbatim probe
  output with a source-information header (date, repo commit, libpcre2 and
  gcc versions), written by `scripts/measure.sh`. Evidence for reviews,
  never an oracle — no check reads them. See the directory's own CLAUDE.md.

Maintenance: update this file when files/subdirectories are added/removed or
their roles change.
