# src/dump — the REGISTRY DUMP TIER

The CLI's read-only table surfaces: `pcrec --list-syntax`, `--list-families`,
`--list-definitions`, `--list-axes`, `--list-limits`, `--list-schema` and
their query siblings. One file per table family; each renders a table
somebody else OWNS; none is on a compile path.

## Standing rules

- A dump renders; it does not decide. Every printed row is derived from the
  owning table's own data; a hand-restatement of another file's fact is the
  defect. `tests/registry/` is the independent side proving agreement.
- `src/dump` stays a LEAF: nothing under `src/` may `#include` from here or
  name one of its symbols (keeps the `*_dump.o` members out of a
  matcher-only link; [REVW.3] wave 3, lens6 L4,
  `docs/dev/reviews/lens_reports/lens6_dependency_rxt_cut.md` §2.4).
- A new `--list-*` table surface is a new file HERE, not in the tier that
  owns the data. Add its entry below in the same change;
  `docs/spec/table_contract.md` is the contract it conforms to.
- Files compile into `libpcrec.a` (`Makefile` `LIBSRCS` wildcard
  `src/dump/*.c`); the tier is a layer, not a library. `cli/` is the only
  caller; `tools/review/include_graph.py` places the layer.
- `--list-syntax` FORMAT is an interface (SR-4): no field may contain a tab
  or newline (tests/cli case 10 counts fields); columns are APPENDED, never
  reordered (positional consumers).
- `--explain`/`--probe-ask`: one router (`doorway_route`/`doorway_call`,
  file-statics, two callers) -- never a second router (invisible drift).
  Both `setjmp` their own Ctx and `pcrec_arena_free`; a raising port returns
  NULL with `pcrec_error` filled. `--explain` value renderings escape control
  bytes (`put_text`: `\xHH` below 0x20 and 0x7f, `\` not doubled).
  `--explain` clauses (election, promise, attribution, `gate`) are scoped to
  the CLOSED gate: two calls per row, `own *` fields show the requested-gate
  answer as data, a second `WANT_VERDICT` call is what the clauses judge;
  exit 3 when a row DISSENTS. The attribution clause CANNOT dissent on a
  module-name swap (ext.c renders from the same `r->module`); module-name
  truth is `tests/reject`'s hand pins.
- `pcrec_construct_built_status` (D65, one derivation, two callers: this dump
  and `tests/registry/registry_check.c`) classifies on `res.what` +
  `res.answered_at`, not refusal text, with every module forced open and the
  enabled set restored exactly; `PCREC_BUILT_NA` for `RS_BASE`/`RS_REJECTED`;
  `PCREC_BUILT_DEFECT` is never rendered, always a `registry_check` failure.
- `pcrec_definitions_tsv` reuses `kind_name`/`put_selector`/`put_str`
  directly (same TU) so kind/selector/syntax cannot render differently from
  `pcrec_syntax_tsv`; `order` is array position, never stored; `predicate`
  reads `pcrec_def_tag_name`; `applies` is `active` (`identity` reserved);
  takes `--flavour` like `pcrec_syntax_tsv` (r43 K6).
- `limits_dump.c` entry `pcrec_limits_tsv` is declared in `lib/pcrec.h` and
  is PUBLIC SURFACE ([REVW.5]): a column change is a contract change and
  carries its `docs/spec/limits.md` hunk. It `#include`s `limits.def`
  directly (defines `PCREC_LIMIT(...)` itself) so values are the real
  compiled numbers.
- `schema_dump.c` includes the `.def` NOWHERE; walks
  `pcrec_rxt_schema_rows()` (one derivation, two readers). Two NAMED sections
  (`schema`, `surface`; `tests/lib/table.sh` Sections rule 4 forbids an
  anonymous section in a multi-section stream); trailing comments
  `# wave-built:`, `# wave-reserved:`, `# schema-rows:`.
- `axes_dump.c`: DFA layer-1 axes walked live off `emit_dfa.c`'s candidate
  arrays via `pcrec_dfa_axis_*_cands` (`core/internal.h`) -- never a hand copy;
  seven START axes are ONE projection of `cand_rows[]` (`emit_cand_axis` over
  `pcrec_cand_list_row`, start_table.md §3.7); fallback axes via
  `emit_fb_axis`/`emit_fb_table_axis` (declared listing
  `docs/design/dec_fallback/listing_declared_B7.tsv`); the VM/engine axes are
  hand-stated from `lib/pcrec.h` enum symbols (stringifying `V()`) and
  `docs/spec/tuning.md` §2. After the axis table it prints `#section memfn`
  from `mf_options()` (`memfn/include/memfn.h`, included by relative path;
  the ONE pcrec TU that includes the kit header; pcrec names no row).
  Independent side: `tests/registry/axes_registry_check.sh`.
- `facts_dump.c` includes `facts.h` and `facts.def`, NEVER `facts_derive.h`
  (enforced by `tests/codegen/run_facts_checks.sh`, sabotage rows
  S298-S300); the driver reaches it only through `PcrecFactsHook`.
- `findings_dump.c` and `measures_dump.c` are `table_contract.md` producers
  at birth: every table a named `#section`, every cell through
  `pcrec_sb_row`; `--view=canonical|decoded` via `pcrec_ks_view_write`.
  `findings_dump` asks the compile's own resolver/digest; `tests/findings/`
  compares against the independent `findings_ref.py`.
- Maintenance: update this file when files are added/removed or roles change.

## Files

- syntax_dump.c -- `--list-syntax` (TSV, columns appended-only, 17 now),
  `--list-families` (D71 item 3, 7 cols), `--list-verbs` (6 cols),
  `--explain`, `pcrec_probe_ask` (`--probe-ask`), built-status (D65),
  `pcrec_definitions_tsv` (`--list-definitions`, DD-11.2, D85).
- axes_dump.c -- `--list-axes` ([CHK-2]); sections after the axis table:
  `memfn`, `part-layout` (off `src/core/part_layout.def`),
  `part-layout-table` (off `pcrec_part_layout_table_row`) ([ENTRY-TABLE] E1;
  registry.md §6 para 10-11).
- limits_dump.c -- `--list-limits` ([LIM-1], D90), public `pcrec_limits_tsv`.
- schema_dump.c -- `--list-schema`, eighth conforming table producer.
- facts_dump.c -- `--emit-facts` ([PATFACTS] 3.0, D126; sections `facts`,
  `decisions`, plus `part-layout-controls`, `part-layout`; not a `--list-*`
  table: needs a pattern, runs real compiles).
- findings_dump.c -- `--list-analyses`, `--list-analysis NAME|FILE`
  ([FINDINGS] B2; `docs/spec/findings.md` §8; [KNOW-SRC] K3).
- callouts_dump.c -- `--list-callouts FILE` ([INLINE-C] stage 3; cli.md
  §2.15): one row per callout site, a REVIEW compile (refusals recorded,
  not raised); the grant comes from the CLI's mode-class column (F27).
- measures_dump.c -- `--list-measurements[=REF]` ([MEASURE-SET] M0;
  `docs/spec/measures.md` §6, `docs/spec/cli.md` §2.9a).

## Pointers

`docs/spec/registry.md` (§6), `docs/spec/table_contract.md`,
`docs/spec/facts_listing.md` (§4.3-4.4), `docs/spec/findings.md`,
`docs/spec/limits.md`, `docs/design/design_notes_mod07.md` §5.2,
`docs/design/definitions_table.md` §5, `docs/design/registry_built_status_memo.md`,
`docs/design/start_table/`, D29, D65, D85, D90, D126.

History (long narrative, dated notes, measurements, per-lane records; not auto-injected): docs/dev/history/claude_md/src__dump.md
