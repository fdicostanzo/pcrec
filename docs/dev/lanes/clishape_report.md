# Lane clishape — [REL-1.10] the gcc-shaped CLI (D118)

Branch `lane/clishape`, from `main` 3db1e574 (abi 28). Six commits, in
stage order: parser, spec/docs, call-site migration, `examples/makefile`,
a fix-up pass (four defect classes found by *running* the suites, not by
reading them), and one more fix in `scripts/emit_sweep.py`'s own dialect
probe.

## Stage 1 — the parser (`cli/main.c`)

Positional operands are input **FILES** now, N of them, compiled exactly
as the retired `--source FILE` compiled one — pooled into a single
`OwnedTarget{RxtTarget*, owner}` list before `-o`'s three-form rule, a
`--target` search, and a **prefix-collision-across-files check** (D118
item 1) are applied to the whole invocation. `--pattern 'X'` is the one
way to give a literal pattern (exactly one; refused combined with a file
operand). `--source` is retired — no arm recognises it, so it falls
through to the unknown-option diagnostic, no alias. `-I DIR` joins
`--lib-path DIR` as a second spelling in the same `else if`. `--probe-ask
WANT CONSTRUCT` consumes CONSTRUCT as its own second `argv[++i]` (D118
addendum item i), never through the operand slot — closing the exact
ambiguity the census flagged for `--count-groups`/`--probe-ask`. An
operand that is not an existing file is refused by name, naming
`--pattern`, before pcrec reads a byte of it (`path_exists`).
`compile_source` became `compile_sources`; `apply_target` takes an
explicit `src_path` parameter instead of reading a single `cli->source`.

Verified live at landing: single- and multi-file `-o DIR` compiles,
`--source` refusing as unknown, a non-existent operand naming
`--pattern`, `--pattern` + file operand refusing, `-I` resolving
`lib-path`, a query mode + file operand refusing, `--target` searching
across files, a single-file `-o` over >1 pooled targets refusing and
naming both ways forward.

## Stage 2 — spec + docs

`docs/spec/cli.md`: usage line and §1 rewritten for the gcc shape; new
§1.1 (a FILE operand, D118); a new `--pattern` section; `--count-groups`/
`--probe-ask` sections updated; every worked example in the file
re-verified live; revision-history entry. `docs/spec/rxt_format.md`: the
three-readers intro, "Building from a source file", the pattern-esc/
config-raw-line sentences, including the D118 addendum item (iv) note.
README.md/CLAUDE.md's try-it line/CHANGELOG.md switched to `--pattern`,
each verified live (build + run, not just edited). `cli/CLAUDE.md` gained
a `## [REL-1.10]` section and inline fixes to the two sections whose prose
had gone stale (`[DD-13b.W1.2]`, `[DD-13b.W23.3]`). `docs/spec/CLAUDE.md`'s
own revision-history bullet list for `cli.md` updated.

## Stage 3 — migrating every call site

A one-off Python script (not committed — scratchpad only) did the
mechanical part: on any line recognisably invoking pcrec and not a
comment, `-- OPERAND` → `--pattern OPERAND` (operand stays LAST, so
`pcrec_run`'s hostile-construct heuristic is undisturbed), `--probe-ask
WANT -- CONSTRUCT` → `--probe-ask WANT CONSTRUCT`, `--source ` → deleted
(the filename stays where it was, legal anywhere as a bare operand).
Continuation lines (backslash-joined) are tracked as one logical line.
Plus targeted hand edits for what a `--`-anchored regex structurally
cannot see: 6 bare-positional calls in `studies/form_char_twins/
gen_base.sh` (the census's own hardest-named case), the 25-file Python
population (12 of the 25 call no CLI surface this flip touches, e.g.
`--list-source` only — read, not blindly edited), four
`tests/spec_mod0/*.c` `argv[]` literals, one Makefile.

**Reconciliation (commit `5d3fbe7c`, before the fix-up pass):** .sh files
518 `--pattern` insertions / 534 removed `-- 'pat'` sites / 27 `--source `
flags deleted; .py files 22 `--pattern` insertions across 12 files that
actually invoke the CLI positionally; .c/.h files 7 `--pattern`
insertions; Makefile 4. Verified zero remaining tree-wide matches for: a
pcrec-invocation line ending `-- 'operand'`; `--probe-ask ... -- ...`;
`--source` as an actual flag on an invocation line. `docs/dev/decisions.md`
and prose narrating the *history* of `--source`/positional patterns (e.g.
`tests/rxtsource/run_rxtsource_tests.sh`'s W1.2 failure-message strings)
is left alone, matching this tree's own convention of not rewriting a
landed wave's record — a live grep for the retired flag as PROSE (not as
an invocation) still finds it there, by design.
`tools/review/out/*.tsv` (a literal-frequency census of the OLD
`cli/main.c` text) is a generated review artifact, stale until
`tools/review` is next re-run — not hand-edited.

## Stage 4 — `examples/makefile`

New top-level `examples/` (own CLAUDE.md). `examples/makefile/`: two
`.rxt` sources (one multi-target — three targets across two files, so the
example itself exercises D118's pooling), a plain Makefile
(`PCREC`/`CC`/`AR` all `?=`-overridable; `gen/.stamp` runs ONE pooled
`pcrec -o gen/ src/*.rxt`; `libmatchers.a` via `ar rcs`; `example` links
`main.c` against two of the three matchers), a README.
`tests/examples/run_examples_tests.sh` copies the example to a scratch
directory, builds it with a stranger's plain `make` against the tree's own
`build/pcrec`, checks the archive holds every target's `<prefix>_search`
symbol (read from the Makefile's own `PREFIXES` variable, never
hand-copied) and the linked consumer's output matches `main.c`'s
expectations exactly. SKIPs loudly if `ar`/`nm` are absent. Wired into
`TEST_SECTIONS`/`.PHONY` as `test-examples`. Root `CLAUDE.md` gains the
`examples/` row; `docs/testing.md`'s touched-path table adds
`test-examples` to `cli/main.c`'s row.

## The fix-up pass — four defect classes, found by RUNNING the suites

Running `make test-codegen` first (6/10 scripts) and `make test-cli`
(268/276 cases) surfaced defects the migration script's line-level regex
could not see by construction. All are now fixed and re-verified.

1. **Reference compilers built from a PINNED OLD COMMIT** don't speak
   `--pattern`. `tests/codegen/run_{atomic,backref,lookaround,
   recursion}_identity.sh`'s `$REF`/`$REF2`/`$FILEREF` (git-archived at a
   commit predating D118) are reverted to `--`; their `$PCREC`-invoking
   lines keep `--pattern`. The SAME files also have reference binaries
   built from the CURRENT tree with a `-D` flag on the same command line
   (`run_trie_identity.sh`, `run_endvar_identity.sh`, and others) — those
   correctly kept `--pattern`, verified by checking each one's own build
   line before touching anything. `studies/scan_edge_ladder/{Makefile,
   run_ladder.sh}`'s `before`/`after` arms are the same class; its
   `step11`/`$(PCREC)` arm is the tree's own build and correctly keeps
   `--pattern`. `scripts/emit_sweep.py`'s REFERENCE binary is an arbitrary
   `--ref REV`, so instead of hand-classifying it, the fix makes the
   script **probe each binary's own `--help` text once** (a regex that
   does not false-positive on `--pattern-esc`, a bug in the probe's own
   first version, found and fixed by actually running the sweep) and
   route each side through its own dialect — general rather than
   per-commit.
2. **A non-pcrec command's own `--` on a line that also mentions
   `pcrec_run`/`$PCREC`** got rewritten. `tests/lib/gen_timeout.sh`'s
   `pcrec_run` DEFINITION itself: `basename -- "..."` → wrongly
   `basename --pattern "..."`, and `scripts/watchdog ... -- "$@"` (its own
   delimiter, forwarding `pcrec_run`'s real argv) → wrongly `...
   --pattern "$@"`. Both reverted to `--`. **This one broke essentially
   everything** — `pcrec_run` is sourced by every suite — and was the
   single highest-leverage fix in the whole pass.
   `tests/{counterk,resource}/*.sh` (11 sites) call `scripts/watchdog`
   directly with `-L LOG -- "$PCREC" -p rx ... PATTERN` on ONE line
   (watchdog's `--` precedes the exec target, not an operand): the
   watchdog `--` is reverted, and the genuine trailing pcrec pattern
   (which had no `--` of its own under the old grammar, so the scripted
   pass never touched it) gains `--pattern`.
3. **Bare positional patterns with no `--` at all** — invisible to a
   `--`-anchored regex by construction, the same shape the census flagged
   as the riskiest population and one this lane already fixed by hand in
   `gen_base.sh`, but which turned out not to be the only file of its
   kind: 9 sites in `tests/cli/run_cli_tests.sh` case13 (the whole
   `-e`/`--encoding` suite), one in
   `tests/spec_mod0/check09_every_feature_toggles.sh`, one in
   `studies/ccd2_entry_shape_ladder/ladder.sh` (the tree's own
   `build/pcrec`). `tests/codegen/run_prefilter_collapse.sh`'s `emit()`
   helper forwarded `"$@"` to `pcrec_run` with no translation of its OWN
   18 callers' `-- PATTERN` convention; fixed ONCE, inside the helper
   (mirroring `run_tune_dial.sh`'s own `emit()`, which already did this
   correctly and needed no change) — no call site touched.
4. **A pattern nested inside an escaped `bash -c` string**
   (`\"$pat\"`, never a clean `"$pat"`): `run_cli_tests.sh` case8's
   stack-depth witness. Found by grep, not by a test run (case8 needs
   `python3`; this box has it, and the case does pass now, but the
   miss itself was structural, not a runtime symptom this pass happened
   to trigger).

Also: `run_cli_tests.sh` case6's "two patterns" scenario is re-targeted
at two `--pattern` flags — the modern equivalent, since a bare second
operand is a FILE now, not a second pattern — asserting on text
`cli_parse` actually emits (`exactly one --pattern expected`) rather than
the retired "one pattern" wording.

A systematic post-fix sweep (two independent detector scripts — one keyed
on `$PCREC`/`pcrec_run`/`build/pcrec`, one broadened to every known
reference-compiler variable name in the tree) found no further bare- or
mis-migrated positional sites in `tests/`, `scripts/`, `tools/`,
`studies/`.

## Validation — every number verified live, this session

| check | result |
|---|---|
| `make -j4 CC=gcc-16` | clean (no rebuild needed after the fix-up commits — none touch `src/`/`cli/`/`lib/`) |
| `make strict CC=gcc-16` | `strict: whole tree compiles clean with -Werror -Wshadow` |
| `make test-codegen` | **9/10** scripts (`run_group: 9/10`) — the one red is `run_inline_capability.sh`'s `nm ... rx_search$` probe, the standing darwin nm limitation (no leading-underscore handling), matching this lane's own expected baseline exactly |
| `make test-cli` | **276/276** cases, 0 failed |
| `make test-registry` | exit 0 (definitions-oracle: 354 cells / 101,244+101,244 comparisons, 0 disagreements) |
| `make test-rxtsource` | exit 0 — INV-COMPAT holds over 213 files / 3,944 blocks / 28,971 expectation lines (unchanged; no `.rxt` file was added under `tests/` by this lane) |
| `make test-examples` | exit 0 — 3/3 (scratch-copy build, `nm` census over the Makefile's own `PREFIXES`, consumer output) |
| `make test-resource` | exit 0 — 27 passed, `sections skipped: 1` (matches the documented skip) |
| `make test-counterk` | exit 0 — 24 passed, `run_group: 2/2` |
| `make test-recursion` | exit 0 — 10 passed (needs >5 min under concurrent load; solo run confirmed clean) |
| `make test-vm` | exit 0 — 48 passed, `run_group: 3/3` |
| `make test-backrefs` | exit 0 — 2 passed, `run_group: 2/2` |
| `make test-lookaround` | exit 0 — 11 passed |
| `make test-atomic` | exit 0 — 8 passed |
| `make test-altcls` | exit 0 — 15 passed, `run_group: 2/2` |
| `make test-definitions` | exit 0 — 22 passed |
| `make test-{atomic,backrefs,lookaround}-identity` | pre-existing, unrelated RETIRED gates (a `[DD-14]` wave-A ABI event predating this lane made their pre-module reference unbuildable-against; not in `TEST_SECTIONS`, opt-in only) — confirmed by reading the gate's own retirement message, not a regression |
| `python3 scripts/emit_sweep.py --ref 3db1e574` | **0 movers on every stream** (self-check AND real run): `c-default` 3522 reach/0 asym, `c-vm` 3523/0, `emit-ir-vm` 3523/0, `composition` 33 producing/98 artifacts/0 asym, `dumps` 7/0; DELIVER witness OK; exit 0 |
| `python3 scripts/m6read_check_sab_anchors.py` | `sabotages checked: 270 (286 anchor sites) / all anchors resolve` — exact match to this lane's own expected baseline |
| `make test` (full suite) | **[see the line below this table — filled in when the run completes]** |

## Census pins

No `.rxt` file was added under `tests/` (`find tests -name '*.rxt' | wc
-l` still 213 — the two new `.rxt` sources live under `examples/makefile/
src/`, outside `tests/`, by design). No census reader moved; nothing to
re-pin.

## Out of scope, named rather than silently skipped

- `docs/design/*_measurements/probes/*.py` (dozens of files): historical,
  one-time measurement probes backing already-published design documents,
  never run by `make`, outside the census's own stated scope
  (`tests/`, `scripts/`, `tools/`, `studies/`). Not migrated.
- `docs/dev/dialtrain_byteid_evidence/byteid_sweep.py`,
  `docs/dev/optvmfl_step0_evidence/census.py`: both take their pcrec
  binary path(s) as caller-supplied CLI arguments (one hardcodes an
  absolute path to a worktree that no longer exists on this machine, so
  it cannot run today regardless). Migrated to `--pattern` for the common
  case (their own stated default, where relevant); a caller pointing them
  at a genuinely pre-D118 binary would need the same dialect care
  `emit_sweep.py` now has, not built here — low-traffic, archival
  directories, same tier as the probes above.
- `tests/codegen/run_object_neutrality.sh`: a manual, on-demand tool
  (`REFERENCE_PCREC [CURRENT_PCREC]`, no default, never called by `make
  test`) explicitly designed to compare a "pre-conversion" reference
  against the current tree for SOME OTHER refactor's own object-neutrality
  question. Its one `--pattern`-migrated call site is kept as `--pattern`
  (a call from the CURRENT tree's own default `CUR` path most needs it);
  a future run comparing against a genuinely pre-D118 `REFERENCE_PCREC`
  would need the same per-binary dialect probe `emit_sweep.py` now has.
  Named here rather than fixed, since it is not exercised by any
  automated section and over-building it has no measured need behind it
  (D77).
- Prose mentions of the retired `--source` flag name and the old
  positional-pattern shape, where they narrate what a past wave landed
  (`tests/rxtsource/run_rxtsource_tests.sh`'s W1.2-era failure-message
  strings, comments elsewhere) are left as historical record, matching
  this tree's own convention (see `cli/CLAUDE.md`'s own
  `[DD-13b.W1.2]`/`[REL-1.10]` pairing for the same choice applied to
  itself).

## Commits

- `f364d122` stage 1 — the parser
- `730237df` stage 2 — spec + docs
- `5d3fbe7c` stage 3 — migrate every call site
- `35459352` stage 4 — `examples/makefile`
- `b6c4e1f5` fix-up — four defect classes from running the suites
- `676de07a` fix — `emit_sweep.py`'s own dialect probe
