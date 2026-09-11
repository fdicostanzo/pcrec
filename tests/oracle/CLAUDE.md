# tests/oracle/ — the oracle interface + answer store: implementation

`docs/design/oracle_interface.md`'s ORACLE STORE and ADAPTER CONTRACT, built
by lane `orstore` against the r56-paneled, revised, verify-passed design (see
that document's own header and `docs/dev/reviews/
2026-09-10-r56-oracle-interface.md`) — implement, do not redesign. The
UPROPS INSTANCE (§9 Step 1, R56-6 corrected) is the first concrete store
customer. `oracle_store/` (top-level, its own CLAUDE.md) is the committed
DATA this code produces and reads; this directory is the CODE.

## Files

- **oracle_store.py** — the core: the six `Question` kinds and their
  canonical serialization (§4's five-escape TSV-framing subset, backslash
  escaped first — R56-1's fix, verified here against the design's own
  trailing-backslash test vector and the raw-TAB-vs-`\t` collision example),
  the question hash (sha256[:16]), `OracleId` (§3, R56-2's widened limit
  triple), and the self-checking TSV store format (§7): `write_store`
  (sorted by hash, a write-time duplicate-hash detector per R56-5),
  `read_store` (verifies the header's stamped `rows` count against what the
  file actually holds, R56-4), and `lookup` (recomputes the canonical
  serialization from the caller's own question fields and verifies the
  stored `question` text matches before trusting the answer — the
  collision/corruption tripwire; a `StoreCorruption` on mismatch, never a
  silently wrong answer). A `store_format_version` the reader does not
  implement is a CLEAN MISS (§8 Claim 4), not a raise. No adapter code here
  — this module knows nothing about libpcre2 or ssh.

  **ONE IMPLEMENTATION CHOICE the design left open, recorded rather than
  silently decided**: the per-kind ANSWER columns that are naturally
  variable-width (`captures`' pairs, `membership`'s intervals,
  `pattern-info`'s nametable) are each kept as ONE space-joined column
  rather than spread across a query-dependent TAB-column count, so a store
  file's own column width is a fixed function of its KIND alone. A second,
  load-bearing subtlety this file's own docstring on `read_store` explains:
  a serialized `question` is ITSELF tab-joined internally (§4's own
  diagram), so a row's total tab-field count is `1 + len(question fields) +
  len(answer columns)`, both fixed by the KIND (read off the file's own
  BASENAME, one file per kind by construction) — a naive
  `line.split("\t")` assuming `question` is one token corrupts every
  multi-field kind the moment its answer has more than zero columns (caught
  by this lane's own store round-trip test before any real data was
  written, not by a panel).

- **local_adapter.py** — the LOCAL DIRECT-LINK adapter (§6). Answers
  `membership` by BUILDING AND SHELLING OUT TO the already-proven
  `tests/uprops/uprops_oracle.c` (whose own stdout format IS §5.5's wire
  format verbatim), and the other five kinds via ctypes, BORROWING (not
  copying) `docs/design/backrefs_measurements/probes/br_oracle.py` →
  `pcre2_ctypes.py` — the tree's own two-level borrowing chain, reused
  rather than re-derived. **[ORACLE-LINK]/D98's resolution is applied to
  BOTH transports**: `PCREC_PCRE2_PATH` is resolved via `tests/lib/
  resolve_pcre2.sh` and exported into the process environment BEFORE the
  ctypes binding's own module-level `CDLL` load runs, so this adapter sees
  the same Homebrew 10.48 every C oracle in this tree resolves rather than
  the darwin dyld-shared-cache skew (U13/U15b) landing on the system copy
  (10.42) — MEASURED live at this lane's build (`OracleId('libpcre2-10.42')`
  before the fix, `OracleId('libpcre2-10.48')` after). `OracleId.version`
  takes only the first whitespace-delimited token of
  `pcre2_config(PCRE2_CONFIG_VERSION)`'s raw string (which carries a release
  DATE too, e.g. `"10.48 2024-06-06"`) — every other citation of a library
  version in this tree is the bare number, a recorded implementation
  choice. **Scope limitation, not silently narrowed**: only the DEFAULT
  `OracleId.config` (no `utf`/`caseless`/non-default limits) is implemented
  — `answer()` raises on anything else, since neither borrowed binding
  exposes a match context today and nothing this lane's own customer asks
  for one.

- **remote_adapter.py** — the REMOTE REFERENCE adapter (§6), GENERALIZING
  `docs/design/utf8_measurements/probes/bundle.py`'s ssh-stdin-payload
  mechanism from one probe script to one `Question`-batch payload — the
  design's own words for this adapter. Borrows `pcre2_ctypes.py` verbatim
  (embedded as `repr()` of its source, an `importlib` shim resolving the
  borrowed basename out of an in-memory dict — bundle.py's own mechanism,
  reused); the SHIM ITSELF is a small reusable function here rather than an
  import of `bundle.py`, because that file's borrowed-file list is
  hardcoded to a different, larger three-file chain this module's `membership`
  -only scope does not need — see the module's own header for the full
  borrowed-vs-generalized argument. `membership` kind ONLY (a general
  six-kind remote adapter is a straightforward extension — embed
  `br_oracle.py` too — not built here, D77: nothing in this lane's scope
  asks the reference box a `compile-accept` or `match-at` question).
  `MAX_BATCH` is a real, stated-conservative knob (§6: "the adapter's job is
  to make [the light-probe] constraint visible... not to hide it"); a batch
  larger than it is split into multiple ssh round trips by `answer()`
  itself.

  **A real bug this lane's own light validation caught**: the first
  `_build_subject` built `cp_at` (the ovector-offset → code-point map)
  indexed by CODE-POINT ORDER, not by the BYTE OFFSET `pcre2_match`'s
  ovector actually reports — silently correct for `byte` encoding (1
  byte = 1 code point) and an `IndexError` the moment a real `utf8`
  sweep's ovector offset exceeded the code-point count. Fixed by indexing
  on byte offset (a dict, matching `uprops_oracle.c`'s own `cp_at[subjlen]
  = c` construction exactly) and re-validated over a 34-property utf8 batch
  before the real capture ran.

- **build_uprops_store.py** — the UPROPS INSTANCE (§9 Step 1). Reuses
  `tests/uprops/run_uprops_tests.sh`'s OWN two population sources —
  `CATEGORIES` (transcribed, 45 names) and a python transcription of its
  `script_values()` awk one-liner (verified to reproduce its own documented
  count, 171, over the vendored UCD) — rather than a third hand-kept
  population list. `local` sweeps the BYTE-encoding population (the same 91
  properties `run_uprops_tests.sh`'s own byte arm names —
  `CATEGORIES` + `BYTE_SCRIPTS`/`BYTE_SCRIPT_CONTROLS`, both namespaces) via
  `LocalAdapter`, writing to `build/oracle_cache/<local-version>/
  membership.tsv` (gitignored, `build/`-shaped, per §7.2). `remote` sweeps
  the FULL utf8-encoding population (387 = 45 categories + 171 scripts × 2
  namespaces, matching `tests/uprops/CLAUDE.md`'s own measured count) via
  `RemoteAdapter` against the true 10.46 reference, committed to
  `oracle_store/libpcre2-10.46/membership.tsv` — see that directory's own
  CLAUDE.md for what this discharges. Both runs REGENERATE the whole file
  (§7.1a: never an unsorted append).

## Validation run at landing (2026-09-10, lane `orstore`)

- `local_adapter.py` run as `__main__`: all six kinds answered against the
  real resolved libpcre2 (10.48), spot-checked against known facts already
  in this tree — the `pattern-info` D59 witness reproduces `alpha:2 mu:3
  zeta:1` exactly (`docs/design/oracle_interface.md` §12's own fixture), the
  `membership` byte-arm Greek answer is `B7-B7` (the uprops CLAUDE.md's own
  cited MIDDLE DOT scx fact).
- `oracle_store.py`: a scripted round trip — escape/unescape over the raw-TAB-
  vs-`\t` collision vector and the trailing-backslash vector (both from §4,
  both distinct/round-tripping correctly), `OracleId.dirname()` for a
  default and a widened config, a `write_store`/`lookup` round trip, and
  THREE self-check failure modes exercised directly: a tampered `rows=`
  header count, a tampered stored `question` text (the collision/corruption
  tripwire), and a forced write-time duplicate-hash collision — all three
  raise `StoreCorruption` as designed.
- `build_uprops_store.py local`: 91 rows written (matches the documented
  byte-arm population exactly).
- `build_uprops_store.py remote --chunk 60`: 387 rows written to the
  COMMITTED reference store — self-checked on read (header `rows=387`
  agrees with the file), `Greek != sc=Greek` (the required non-vacuity
  control from `tests/uprops/CLAUDE.md` §4), a missing-property lookup
  returns `None` rather than raising. Total wall time for the real capture:
  under two minutes across seven ssh round trips, well inside a light-probe
  budget.

## [ORWIRE] (2026-09-10): the wiring this lane left owed is DONE

`tests/uprops/uprops_compare.py`'s utf8 arm now consults
`oracle_store/libpcre2-10.46/membership.tsv` as a SECOND, EXACT-tier
comparison beside the existing live-oracle one (never a replacement — the
live comparison, and `build_uprops_store.py` as the CAPTURE tool, are both
unchanged and still run). See `tests/uprops/CLAUDE.md` and
`docs/dev/lanes/orwire_report.md` for the mechanism, the provenance output
and the validation transcript. `tests/utf8/axis12_scripts.rxt` itself is a
static `.rxt` corpus (baked-in expectations, not a runtime oracle
consultation) and is unchanged — it was never a store *consumer* in the
sense this ladder step wires; its population is the same `membership`
differential this wiring now checks exact.

## Second consumer, 2026-09-10/11 (lane `pyrole`)

`tests/rxtsource/build_c3_store.py` is a SECOND `LocalAdapter` consumer,
outside this directory (`docs/design/c3_three_way.md`): the C3 python-tier
redesign's own store-capture script, populating `oracle_store/
libpcre2-10.48/{match-at,captures}.tsv` with seven hand-enumerated
questions (not a sweep — see that script's own header). Uses this
directory's `LocalAdapter`/`oracle_store` code unmodified, imported the
same way `local_adapter.py` itself imports `oracle_store` (a `sys.path`
insert to this directory). `tests/harness/verify_rxt.py` is the consumer
of the resulting store data, via `oracle_store.lookup()` directly (not
through `LocalAdapter` — check time never touches a live library).

## Validation OWED (not run by this lane; see the lane report for the exact
commands)

- A general six-kind `RemoteAdapter` (embedding `br_oracle.py` too) if a
  future customer needs a reference `compile-accept`/`match-at` answer.
- `LocalAdapter` support for a non-default `OracleId.config` (utf/caseless/
  non-default limits) — needs a `pcre2_match_context`, not built here.
- `make test` / `make strict` were NOT run (a battery was in flight on this
  box for this lane's whole working period, per `docs/dev/lanes/
  BOILERPLATE.md`'s box-concurrency rule) — this code touches nothing
  under `src/` or existing `tests/` suites, so nothing here should move an
  existing suite's result, but that is a claim, not a measurement, until a
  real run confirms it.

Maintenance: update this file when files are added/removed or their roles
change.
