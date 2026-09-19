# src/dump — the REGISTRY DUMP TIER

The CLI's read-only table surfaces: `pcrec --list-syntax`,
`--list-families`, `--list-definitions`, `--list-axes`, `--list-limits`,
`--list-schema` and their query siblings. One file per table family;
every one of them renders a table somebody else OWNS, and none of them is
on a compile path.

**Why this is its own tier, at the TOP of the layer order beside the
pipeline driver** ([REVW.3] wave 3, lens 6's L4; `docs/dev/reviews/
lens_reports/lens6_dependency_rxt_cut.md` §2.4). These four files used to
live in `src/parse/` and are not parser code: they READ the parse tier
(`registry.c`'s rows, `rxt_schema.c`'s table), the core tier
(`limits.def`) and the GEN tier (`emit_dfa.c`'s own candidate arrays,
through the `pcrec_dfa_axis_*_cands` accessors) — so filed under `parse`
they produced the single largest `parse -> gen` cell in the call-level
back-edge census while being, by layer, above all of it. They are also
already LINK-CLEAN in a way no other `src/` object is: the four
`*_dump.o` are the ONLY archive members a matcher-only consumer does not
pull in, because no `src/` object names their symbols and only
`cli/main.c` does (lens 6 §1.2's four-arm link experiment). The tier
records that property rather than leaving it a coincidence.

**The rule this tier keeps.** A dump renders; it does not decide. Every
row it prints is derived from the owning table's own data — a
hand-restatement of a fact another file holds is the defect each of these
files' headers warns about, and `tests/registry/` is the independent side
that proves the two agree. `src/dump` must stay a leaf: nothing under
`src/` may `#include` from here or name one of its symbols, which is what
keeps the link-cleanness above a structural fact rather than a measured
one.

## Files

- **syntax_dump.c** — rendering the registry as text (SR-3) AND, since
  MOD-0.7, querying the live parse front: `--list-syntax`
  (TSV — 12 columns at SR-4, 15 since MOD-0.1 appended `roadmap`,
  `quantifiable` and `class_expect`, all on 2026-08-11, 16 at D65's `built`
  and 17 at [M6.6.2] wave F's `family`; columns are APPENDED,
  never reordered, so consumers' positional reads survive),
  `--list-families` (TSV, 7 columns — D71 item 3's INDEX LAYER: one line per
  family, where a family is the rows sharing a key and a row's key is its
  `family` column if set and its own `syntax` otherwise, with `built` ANDed
  over the members. A SECOND dump for `--list-verbs`' reason: `--list-syntax`
  is per-ROW and its consumers depend on that — tests/reject/ probes every
  non-base row's own `syntax`, and a collapsed dump would have silently
  dropped twelve probes), `--list-verbs`
  (TSV, 6 columns — the Q1 name tables, which are not RegRows and so cannot
  appear in the row dump whose format SR-4 froze), `--explain`, and since
  MOD-0.1's slice 8 `pcrec_probe_ask` (`--probe-ask` — ONE doorway call at a
  chosen want level with the real cursor reported before/after, routed by a
  bytewise scan to the first doorway opener in full-text coordinates, `(?:`
  excluded exactly as parse.c excludes it; the check06 cursor-rule channel,
  10 TSV fields appended-never-reordered).
  **MOD-0.7 made this file a CALLER of the doorways, not only a renderer.**
  The bytewise scan is now `doorway_route`/`doorway_call`, file-statics with
  TWO callers — `--probe-ask` and the rewritten `--explain` — because a second
  router would drift and the drift would be invisible, each surface staying
  self-consistent with itself (extraction evidence: 1089 `--probe-ask` cells
  byte-identical, check06's floors unmoved). `--explain` was a mutual-prefix
  match on the `syntax` column with no `ext_`/`arbitrate` reference at all,
  which R10/C4-2 refuted as a control and which made D29's own worked example
  (`--explain '(?i-m:'`) fail; it now prints the ROW's declared attribution
  beside the LIVE doorway's answer and compares them per row (election,
  promise, attribution — `docs/design/design_notes_mod07.md` §5.2), selecting rows by
  prefix UNION bucket-candidates with each row tagged which rule found it, and
  exiting 3 when a row DISSENTS.
  **THE CLAUSES ARE SCOPED TO THE CLOSED GATE since R20/MOD07-2+3**, and the
  scope is the correction: §5.2's census was taken at the closed gate while
  the implementation asked its clauses at whatever `--features` said, so the
  enabled set was an axis the predicate had never been established over. Two
  defects lived there — `--features modifiers --explain '(?J)'` DISSENTED on
  attribution about a tree tests/reject:664 pins as CORRECT (an enabled
  option-run port refuses per LETTER, and a letter's module is not the
  dispatching row's), and a producing answer short-circuited promise and
  attribution away, so opening a gate SHRANK the coverage of the rows it
  turned on. Now TWO calls per displayed row: the `own *` fields show the
  REQUESTED-gate answer as DATA, and a second `WANT_VERDICT` call is what the
  clauses judge. `WANT_VERDICT` is how "the default enabled set" is reached
  without a process-global being rewritten — `pcrec_ext_gate` only demotes and
  floors at VERDICT, so no enabled set can promote it, and a BASE port answers
  at the level asked (measured equivalent to a default-set RESULT ask on all
  100 rows, every `--probe-ask` field compared). A FOURTH clause, `gate`, is
  the one thing an open gate is good for here: a row that PRODUCES must have
  its declared module in the enabled set — the cross-check the short-circuit
  walked past. Total over the table at every gate state, measured as a
  100-row × 5-gate-state census: 0 dissents everywhere, against 2 at
  `modifiers` and 2 at `all` before.
  **The honest limit, measured and repeated
  here because it is the thing a reader will assume wrongly: the attribution
  clause CANNOT dissent on a module-name swap** — ext.c renders "requires
  module '%s'" from the same `r->module` this file prints, so the two agree by
  construction (100 rows, zero census difference under C4-1's sabotage).
  Module-name truth is `tests/reject`'s hand pins; what the live call adds is
  ELECTION, which no existing check has, because 13 rows share their rendered
  diagnostic with a bucket sibling. MOD-0.7 also fixed K14 HERE: the `status`
  line promised module `callouts` for the ROADMAP_NEVER row while ext.c and
  `put_expect` in this same file had both been roadmap-aware since MOD-0.1.
  **BOTH QUERY SURFACES `setjmp` THEIR OWN Ctx since R20/MOD07-1**, and
  `doorway_call`'s comment — which had named "the first enabled,
  result-producing module port" as the event that must revisit the zeroed Ctx,
  two milestones after that port landed — is rewritten as a discharged
  obligation. A raising port used to SIGSEGV both surfaces; it now abandons
  the answer and returns NULL with a `pcrec_error` filled, which the CLI
  renders in the compile path's own shape. Both surfaces `arena_free` too
  (`--probe-ask` never did). **`--explain`'s value renderings escape control
  bytes** (R20/MOD07-8, `put_text`: bytes below 0x20 and 0x7f as `\xHH`, `\`
  deliberately not doubled) — the format grammar had no escaping, so a query
  containing a newline injected a synthetic header line that the test
  suite's own `explain_field` parser read as real. Internal, not public API — the CLI and the
  test suite are the only consumers, and promoting a function into lib/pcrec.h
  later is easier than un-promoting it. SR-4 makes this dump load-bearing, so
  its FORMAT is an interface: no field may contain a tab or a newline, which
  tests/cli case 10 asserts by counting fields

  **[D65] (2026-08-21, docs/design/registry_built_status_memo.md, ratified
  wholesale) — `--list-syntax` gains a 16th column, `built`.** A THIRD
  question beside `status`/`roadmap`'s two ("is this base grammar" /
  "will a module ever implement it"): has the owning module's producer
  actually LANDED, per construct. `pcrec_construct_built_status` (the
  exported entry both this dump and `tests/registry/registry_check.c`'s
  defect assertion call — one derivation, two callers) reuses
  `doorway_route`/`doorway_call` exactly as `--probe-ask`/`--explain` do,
  with EVERY module forced open (`src/parse/enabled.c`'s process-global
  set, saved via `pcrec_enabled_set_modules()` and restored exactly after —
  the same shape `pcre2_check.c`'s "gated pass" already uses), and
  classifies on `res.what` + `res.answered_at` rather than on refusal TEXT
  — see its own comment in this file for the three real rows (module
  `verbs`, module `unicode-props`, and the cross-module `(?m)` case) a
  narrower text-matching first draft measured wrong on before landing on
  this shape. `PCREC_BUILT_NA` ("—") for `RS_BASE`/`RS_REJECTED` rows,
  where the question does not arise; `PCREC_BUILT_DEFECT` for a row whose
  own well-formed `syntax` answers neither way — never rendered as a
  status, always a `registry_check` hard failure. Measured on the shipped
  registry: 33 of the 34 rows belonging to SHIPPED modules read `built`;
  `(?J)` reads `unbuilt` (module `modifiers`' own permanent, unconditional
  DUPNAMES decline) — the precise distinction a per-module summary always
  blurred, and the reason D65 ruled per-CONSTRUCT granularity.

  **[DD-11.2] `pcrec_definitions_tsv` — `--list-definitions`, the FIFTH
  registry surface (D85, docs/design/definitions_table.md §5).** Lives
  here rather than in a new file, deliberately: it reuses `kind_name`/
  `put_selector`/`put_str` DIRECTLY (private statics in this same TU), so
  `kind`/`selector`/`syntax` cannot render differently from
  `pcrec_syntax_tsv`'s own copy — the two dumps join on those columns by
  construction, not by two independent renderings that happen to agree.
  Walks the same `all_kinds` sweep, but PER `RegDef` ENTRY rather than
  per row (a row with `definitions == NULL` contributes nothing); `order`
  is the entry's own array position, never a stored field (`family`'s own
  "one derivation" precedent). `predicate` reads `pcrec_def_tag_name`
  (src/parse/definitions.c) — the tag's OWN name, never hand-authored
  prose. `applies` prints `active` unconditionally today: every row the
  table carries substitutes something, and `identity` (the row already IS
  its own primitive form) is a reserved value with no row using it yet —
  `^`/`$`/the `(?n)`-scoped capturing-group row each need it and are held
  pending a `RegDef` field this design has not settled (see the lane's own
  report to main, and registry.md §9's matching note). Takes `--flavour`
  like `pcrec_syntax_tsv` (r43 K6): it walks the SAME rows, filtered
  identically, so an unfiltered dump would print a definition for a
  construct `--list-syntax --flavour=X` says does not exist.
- **axes_dump.c** — [CHK-2] piece 1: `pcrec --list-axes`, the optimization-
  axis registry's FOURTH TSV surface (`docs/spec/registry.md` §6; NOT the
  syntax registry syntax_dump.c below renders — a different table
  entirely). One row per (axis, candidate): the six DFA layer-1 axes
  (table representation, prefilter, view, seed, accept, direction) are
  walked live off `src/gen/emit_dfa.c`'s own `DfaCand`-headed candidate
  arrays through six read-only accessors that file exports
  (`pcrec_dfa_axis_*_cands`, declared in `core/internal.h`) — never a
  hand-copied restatement of their names/deny bits, so a candidate landed
  in one of those arrays appears in the dump with no edit here. The
  eleven VM/engine-selection axes have no candidate-list-as-data anywhere
  in the tree yet ([ENG-FORM] relayered `emit_dfa.c` only), so those rows
  are hand-stated from `lib/pcrec.h`'s own enum symbols (via a
  stringifying `V()` macro, so a bit's numeric position can move with no
  edit here) and `docs/spec/tuning.md` §2's prose. This file's own header
  comment states in full what the dump proves (what the compiler THINKS
  its axes are) and what it does not (independent evidence that a stamp
  or flag behaves as described — `tests/registry/axes_registry_check.sh`
  and the emitted-artifact checks are that independent side)
- **limits_dump.c** — [LIM-1] `pcrec --list-limits`, the numeric-limits
  registry's SIXTH TSV surface (`docs/spec/registry.md`; D90). It
  `#include`s `src/core/limits.def` DIRECTLY, defining the full
  `PCREC_LIMIT(...)` macro itself rather than going through any site's
  per-HOME dispatch layer, so a row's `value` is spliced into a numeric
  cast at this call site and evaluates to the REAL compiled-in number —
  including a row that references an earlier row's own symbol
  (`PCREC_MAX_EMIT_NAME_LEN`'s `PCREC_MAX_PREFIX_LEN + 96`), never a
  second computation of it. Its own header states what that proves (the
  table's numbers agree with what the compiler built) and what it does
  not (that a value is documented correctly elsewhere —
  `tests/registry/limits_check.sh` is the independent side).
  `schema_dump.c` below is deliberately shaped after it, with the one
  difference that file's entry names.
- **schema_dump.c** — `pcrec --list-schema`, the SEVENTH registry dump and
  the eighth conforming table producer (`docs/spec/table_contract.md`).
  `limits_dump.c`'s shape with one deliberate difference: it `#include`s
  the `.def` NOWHERE and walks the table through `pcrec_rxt_schema_rows()`
  instead, the same entry the parser uses — one derivation, two readers.
  TWO NAMED SECTIONS (`schema`, `surface`), the second being the DECLARED
  NON-COVERAGE; the main table is named rather than anonymous because
  `tests/lib/table.sh`'s Sections rule 4 makes an anonymous section in a
  multi-section stream the one table no conforming consumer can address.
  Three trailing comments carry what a consumer cannot get from the rows:
  `# wave-built:` and `# wave-reserved:` are the `wave` column's two
  boundaries (W23-S3 partitions its arm-4/4b populations on them rather
  than copying internal.h's constants), and
  `# schema-rows:` carries the COMPILE-TIME row total,
  which is the denominator a check iterating the dump's rows cannot get
  from the rows themselves.

## Conventions

- A new `--list-*` table surface is a new file HERE, not in the tier that
  owns the data. Its entry goes in the list above in the same change
  (root `CLAUDE.md`'s directory rule), and `docs/spec/table_contract.md`
  is the contract it conforms to.
- These files are compiled into `libpcrec.a` like every other `src/`
  object (`Makefile`'s `LIBSRCS` carries `$(wildcard src/dump/*.c)`);
  the tier is a LAYER, not a separate library. `cli/` is their only
  caller and the layer model in `tools/review/include_graph.py` places
  them accordingly.

Maintenance: update this file when files are added/removed or their roles
change.
