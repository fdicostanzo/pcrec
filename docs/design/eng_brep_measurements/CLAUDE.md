# docs/design/eng_brep_measurements/ -- the ENG-BREP design lane's instruments

Everything `../eng_brep_design.md` cites, kept so the note's numbers can be
re-run rather than believed and the implementation lane inherits the
harnesses.

## Standing rules

- Nothing here is a proposed patch. Probes needing a MODIFIED compiler
  (raised replication cap; NFA-state `fprintf`) get one from
  `probes/mkscratch.sh`, which builds in a SCRATCH COPY outside the repo's
  build directory, so `src/`, `build/`, `make test` and the known-fail
  ratchet only see the unmodified compiler. Every scratch patch ASSERTS on
  its own anchor (a moved anchor fails loudly, never silently builds the
  stock compiler under a prototype's name).
- Archived outputs are EVIDENCE, NEVER AN ORACLE: no check reads them.
  Archive with `archive.sh` (D35 source-information header; stable
  filenames so re-measurement lands as a git diff).
- Every compile in a probe runs under `timeout`; a timeout is a recorded
  FINDING (`TIMEOUT>N`), never a reason to re-run longer. Re-measure
  load-affected cells serially before quoting.
- Probe oracle: python3 `re` plus (since the nested-lazy lane) libpcre2 via
  `pcre2_ctypes.py` (live `version()`, not hand-typed). python-possessive is
  not PCRE2-possessive (`docs/dev/upstream_issues.md` U9), so the libpcre2
  probes run TWO self-consistent differentials (all-python, all-libpcre2),
  never one cross-engine comparison.
- Every probe family keeps a failing-direction control (`BREP_NO_LAZY_CONJUNCT`,
  `NO_ENCLOSING_FIRST`); `spellings()` derives greedy AND lazy families from
  one base count so omitting one requires deleting a loop. `subjects()` must
  contain the discriminating bytes (D47.6: `z` in `ALPHA` plus
  repetition-heavy subjects; guard `tests/base/possess_lazy_guard.rxt`).
- Rung-census figures are DERIVED by `census_rungs.py` from the archived
  files (never a shell `sort -u` under a UTF-8 locale, which merges
  punctuation-different strings); a table cell's engine/rung is read from
  `--emit-ir`'s header per row.
- `probe_possess.py` row tuples are APPENDED-to, never reordered
  (index-based consumers); it tests only the OUTERMOST quantifier
  (`info[0]`); quantifier-bearing PREFIXES must not inherit index targeting
  without re-deriving it (use `probe_possess_nested.py`).
- Pattern harvesting reuses `../k18_measurements/harvest_patterns.py`.
- Known limits: the probe's model widens `\d`/`\w`/unmodelled constructs to
  all 256 bytes (census rates are LOWER bounds); `probe_rungs.py` splits on
  tabs (tab-containing patterns shift fields; `census_rungs.py` drops
  non-5-field rows); libpcre2 refuses repeat counts above 65535 (reported
  `compile-error`, not divergence); `regen_body.py` declines inline-flag
  groups; the note's §5.3 three-way sweep with pcrec itself is not run here.
- Maintenance: update this file when probes or outputs are added, removed,
  or change role.

## Files

- `probes/mkscratch.sh NAME [FILE SED-EXPR]...` -- scratch-copy compiler
  builder (`bigcap`, `nfastats`).
- `probe_replication.sh`, `probe_throughput.sh` + `tdriver.c` -- replication
  cost sweep; K-axis speed (K=N vs frames-rung star, min of 3, -O2).
- `probe_rungs.py` -- rung census off `--emit-ir`'s RUNGS section;
  `census_rungs.py [OUTPUTS_DIR]` -- derives the note's census figures.
- `probe_possess.py` -- disjoint-follow possessification analysis vs python
  `re`, both directions, greedy and lazy; `probe_possess_corpus.py PATTERNS`
  -- same analysis over the .rxt corpus and `realistic_patterns.txt`
  (40 hand-written patterns, bias disclosed in its header).
- `probe_cell33.sh` -- §3.3 table from one serial run.
- `probe_termination.sh` -- R21 E-2 no-guard-for-bounded ruling.
- `pcre2_ctypes.py` -- minimal ctypes binding to installed libpcre2-8-0.
- `probe_possess_nested.py` -- nested-lazy differential (§8 item 8).
- `probe_possess_pcre2.py` -- flat family vs libpcre2 (+ `is_u9_shape()`).
- `probe_dollar_multiline_pcre2.py` -- `$` MULTILINE gate (§2.5).
- `probe_corpus_diff_pcre2.py` -- corpus + realistic differential; uses
  `regen_body.py` (unparses a quantifier body; raises counted `Unsupported`).
- `archive.sh SRC NAME DESC` -- archive a probe's raw output.
- `outputs/` -- archived evidence (replication_sweep.tsv, nfa_growth.txt,
  possess_differential*.tsv/.summary, rung_census_*, throughput_sweep.tsv,
  termination.txt, nested/pcre2/dollar/corpus differential files,
  `nestedlazy_findings.txt` = read first for numbers). Output-to-note-section
  mapping is in the history file's Outputs table.

## Pointers

`../eng_brep_design.md` (§1.4, §2.4, §2.5, §2.6, §3, §4.3, §6, §8, §10.2),
`docs/dev/decisions.md` D47.6, D35, `docs/dev/upstream_issues.md` U9,
`docs/dev/reviews/2026-08-15-r24-eng-brep.md`, `../k18_measurements/`.

History (long narrative, dated notes, measurements, per-lane records; not auto-injected): docs/dev/history/claude_md/docs__design__eng_brep_measurements.md
