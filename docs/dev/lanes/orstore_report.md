# orstore — the oracle interface + answer store, implementation

2026-09-10, lane `orstore`. Builds `docs/design/oracle_interface.md` (r56-
paneled, revised by lane `oraiface2`, verify-passed) as its charter states:
implement, do not redesign. Delivers `tests/oracle/` (the code) and
`oracle_store/` (the committed reference store the code produced for real).
Branch `lane/orstore`, parked for the manager to merge post-battery.

## What was built, section by section against the design

**§2 the six question kinds** — `tests/oracle/oracle_store.py`'s
`KIND_QUESTION_FIELDS`/`KIND_ANSWER_COLUMNS`, all six, field lists exactly as
the design's §4 diagram states them.

**§3 `OracleId`** — `OracleId(name, version, utf, caseless, match_limit,
depth_limit, heap_limit)`, defaults at the design's own measured PCRE2
compiled-in values (10,000,000 / 10,000,000 / 20,000,000). `dirname()`
implements §7.1's `<name>-<version>[-<config-tag>]` layout.

**§4 canonical serialization** — `escape_field`/`unescape_field` implement
the five-escape TSV-framing subset, backslash escaped first. Verified against
the design's own two named test vectors: the raw-TAB-vs-`\t` collision
example (distinct serializations, confirmed) and the trailing-backslash
vector (`a\` → `a\\` — three characters, confirmed). `serialize_question` +
`question_hash` (sha256[:16]) complete the section.

**§5 answer shapes** — one function pair or inline tuple per kind in the two
adapters; `captures`' unset pair is the literal `-1`/`-1` convention §5.3
names, reused from `rx_info`/`match_api.md` rather than re-invented.

**§6 the adapter contract** — `capabilities()` + `answer(batch)` on both
adapters, positional correspondence preserved even where the underlying
transport groups questions by encoding (membership) or answers most kinds
individually (everything else). `local_adapter.py` is the "Local
direct-link adapter"; `remote_adapter.py` is the "Remote reference adapter",
generalizing `bundle.py`'s own mechanism per the design's literal words.

**§7 the store** — `store_path`, `write_store`, `read_store`, `lookup` in
`oracle_store.py`. §7.1's two-line `#` header (provenance + column names),
sorted-by-hash rows, `store_format_version` as a clean-miss gate (§8 Claim
4). §7.1a's write-time duplicate-hash detector and "regenerate the whole
file, never append" discipline (`build_uprops_store.py`'s `local`/`remote`
both call `write_store` with the FULL population every run). §7.2's
committed-vs-gitignored split: `oracle_store/libpcre2-10.46/` is committed;
`build/oracle_cache/` (the local Homebrew 10.48 answers) is not, riding
`build/`'s existing gitignore rule rather than a new one.

**§8 the staleness-impossibility argument** — Claims 1-2 are structural
(the key IS the oracle version + config; a version bump is a directory that
does not exist yet). Claim 3 (only the oracle side caches) holds by
construction: nothing in this lane defines or touches a pcrec-side cache.
Claim 4 (a format-version mismatch is a clean miss) is `read_store`'s
`store_format_version` check, returning `(None, None)` rather than raising
or partially parsing.

**§9 migration ladder, Step 1** — `build_uprops_store.py`. Read the R56-6
correction before assuming this discharges S-U6/S-U9: it discharges the
STAGE-5 script-namespace `membership` differential's own 10.46-exactness
debt (`S-U12`'s neighborhood), not the ill-formed-subject `match-at`
questions those two rows actually name.

**§10 what does not change** — confirmed by construction: nothing under
`src/`, no `.rxt` file touched, no existing check's verdict logic touched.

**§12 fixture-shaped examples** — the `pattern-info` fixture
(`(?<zeta>a)(?<alpha>b)(?<mu>c)` → `alpha:2 mu:3 zeta:1`) is reproduced
verbatim by `local_adapter.py`'s own validation run (see below) — the design
called it illustrative and not actually computed by its own read-only lane;
this lane computed it for real and it matches.

## Choices made where the design left something open (§13's own two + two
more found while building)

1. **Store location: top-level `oracle_store/`.** r56 already ratified this
   ("Ratified as-is... top-level oracle_store/"), so this was not open by
   the time this lane started — named here only so a reader of §13 knows
   it is settled, not still a question.

2. **`answer` columns for a variable-width kind** (`captures`'s pairs,
   `membership`'s intervals, `pattern-info`'s nametable): kept as ONE
   space-joined column per kind rather than spread across a query-dependent
   TAB-column count. The design's own diagrams (§4, §5) use tabs for
   `captures`' wire form but never say what a STORE ROW does when the
   column count would otherwise vary per query (`nslots` is part of the
   question, not the kind) — simplest conforming choice: a store file's
   column width is a fixed function of its kind alone, never of a
   particular row's own question. Recorded, not silently decided.

3. **`OracleId._config_tag()`'s exact spelling** when more than one config
   axis is active (§7.1 says a tag exists "only when more than one config
   is exercised" but not what it looks like): one hyphen-joined token per
   active axis in a fixed order (`utf`, `caseless`, then the limit triple
   as ONE token only if any of the three differs from default, since §3's
   own rule is that a non-default config names all three explicitly).
   `libpcre2-10.46-utf-caseless`, `libpcre2-10.46-lim1000-1000-2000`, etc.

4. **`OracleId.version`'s exact string, beyond what §3 says.** §3 says
   "exactly as `pcre2_abi_version()` reports it", and that function (read
   from `tests/fuzz/pcre2_abi.h`) passes PCRE2's raw `PCRE2_CONFIG_VERSION`
   string through unmodified — which carries a release DATE too
   (`"10.48 2024-06-06"`), not just the number. Every other citation of a
   library version anywhere in this tree (`oracle_store/libpcre2-10.46/`,
   the design's own fixture `libpcre2@10.46(...)`, `tests/uprops/CLAUDE.md`'s
   prose) is the bare number. `OracleId` takes only the first
   whitespace-delimited token. Recorded rather than silently decided,
   because a reader comparing "what `pcre2_abi_version()` reports" against
   "what ended up in the directory name" would otherwise find a real gap.

5. **The local adapter's transport for `membership`.** The design's own
   text names the C `pcre2_abi.h` binding as the local adapter's mechanism
   in general; this lane's `membership` implementation shells out to the
   ALREADY-BUILT, already-tested `tests/uprops/uprops_oracle.c` binary
   rather than re-deriving the whole-code-point sweep through ctypes — the
   simplest conforming choice available, since that binary's own printed
   format IS §5.5's wire format verbatim. The other five kinds go through
   ctypes (borrowing `br_oracle.py`), so the adapter is genuinely two
   transports behind one `answer()` — stated in the module's own header,
   not hidden.

## Judgment calls that are genuine ambiguity, not silently resolved

- **`captures`' padding when the underlying match is `nomatch`.** §5.3 says
  a `captures` question "is only meaningful attached to a `match` answer"
  and that "the adapter reports the pair together rather than the caller
  reconstructing it from two calls" — but does not say what the adapter
  reports when the match-at half comes back `nomatch`. `local_adapter.py`
  reports the unset pair (`-1 -1`) for every requested slot rather than
  raising, on the argument that a batch answer must stay positional and the
  caller asked for this exact tuple regardless of outcome. A store customer
  that instead wants `captures` to be UNASKABLE over a `nomatch` subject
  (raise, or omit the row from a batch answer) would need a ruling; this
  lane's own customer (uprops) never asks a `captures` question, so nothing
  here depends on the choice, and it is flagged rather than assumed settled.

- **`RemoteAdapter.MAX_BATCH`'s value (8, later overridden to 60 for the
  real capture).** §6 states plainly that this knob exists and that "the
  adapter's job is to make [the light-probe] constraint visible... not to
  hide it" — it does not say what the number should BE, and this lane never
  ran a timing sweep across batch sizes. 60 was picked because it produced
  seven round trips for the real 387-property capture, each comfortably
  under a minute; whether a larger N is still "light" is unmeasured, and a
  future caller with a bigger population should re-derive rather than
  assume 60 scales.

## What was found while building (not in the design, found by running it)

- **A real bug in `remote_adapter.py`'s own subject construction**, caught
  by this lane's own validation before the real capture ran: `cp_at` (the
  byte-offset → code-point map an ovector result is looked up against) was
  first built indexed by CODE-POINT ORDER, silently correct under `byte`
  (1 byte = 1 code point) and an `IndexError` the instant a real `utf8`
  sweep's ovector offset exceeded the code-point count. Fixed to index by
  byte offset, matching `uprops_oracle.c`'s own `cp_at[subjlen] = c`
  construction (`tests/oracle/CLAUDE.md`'s own entry has the full story).

- **`read_store`'s row-width subtlety.** A serialized `question` is itself
  tab-joined internally (§4's own diagram — `match-at` is three tab-joined
  sub-fields), so a store ROW's tab-field count is `1 + n_question_fields +
  n_answer_columns`, not `3` as a naive "hash, question, answer..." reading
  of §7.1's prose would suggest. Caught by this lane's own store round-trip
  test (a `membership` row with a two-field question broke the first
  `line.split("\t")`-assumes-one-question-token implementation) before any
  real data was written.

- **[ORACLE-LINK]/D98's darwin-dyld skew reaches this ctypes binding too.**
  `local_adapter.py`'s first run resolved `libpcre2-10.42` (the macOS
  system copy) rather than the Homebrew 10.48 every C oracle in this tree
  resolves via `tests/lib/resolve_pcre2.sh` — because `pcre2_ctypes.py`'s
  own `ctypes.CDLL` candidate search runs before `PCREC_PCRE2_PATH` is set,
  unless a caller sets it first. Fixed by resolving `tests/lib/
  resolve_pcre2.sh`'s env and exporting `PCREC_PCRE2_PATH` before the
  borrowed binding is imported. This is the SAME skew `uprops_oracle.c`'s
  own header documents for the C binding side, now confirmed to apply to
  every future ctypes-based adapter this store gains, not just this one.

## Validation done vs owed

**Done, this lane, bounded/targeted, no battery interference (nothing here
touches `src/` or any existing `tests/` suite):**

- `oracle_store.py`: escape/unescape round trip incl. both named test
  vectors; `serialize_question`/`question_hash` determinism;
  `OracleId.dirname()` default and widened-config; a `write_store`/
  `lookup` round trip; THREE self-check failure modes exercised directly
  (tampered row-count header, tampered stored question text, a forced
  write-time duplicate-hash collision) — all three raise `StoreCorruption`.
- `local_adapter.py` run as `__main__`: all six kinds, spot-checked against
  facts already established elsewhere in this tree (the `pattern-info` D59
  witness reproduces `alpha:2 mu:3 zeta:1` exactly; the byte-arm `Greek`
  membership answer is `B7-B7`, the documented MIDDLE DOT scx fact).
- `remote_adapter.py`: a light two-property byte-arm probe against the true
  10.46 reference (confirms `OracleId('libpcre2-10.46')` resolved live, not
  hand-typed), then a 34-property utf8 timing probe that caught and
  confirmed the fix for the `cp_at` indexing bug above.
- `build_uprops_store.py local`: 91 rows written — matches
  `tests/uprops/CLAUDE.md`'s own documented byte-arm population exactly.
- `build_uprops_store.py remote --chunk 60`: **the real capture, not a
  demonstration** — 387 rows written to the COMMITTED
  `oracle_store/libpcre2-10.46/membership.tsv` (45 categories + 171
  scripts × 2 namespaces, matching the documented count exactly), self-
  checked on read (`rows=387` header agrees with the file), `Greek !=
  sc=Greek` confirmed (the non-vacuity control `tests/uprops/CLAUDE.md` §4
  requires), a missing-property lookup returns `None`. Seven ssh round
  trips, under two minutes total wall time.
- `python3 -m py_compile` clean on all four new modules.

**Owed, named precisely, not run by this lane:**

- `make test` / `make strict` / `make san` / any battery stage — a battery
  was IN FLIGHT on this box for this lane's entire working period
  (`BOILERPLATE.md`'s box-concurrency rule). Nothing this lane touched is
  under `src/` or any existing test suite, so the expectation is zero
  effect on any of them — that is a claim from reading the diff, not a
  measurement, until the manager's post-battery run confirms it. Exact
  command once the battery clears: `make test` (whole suite; nothing here
  has a dedicated section target since it isn't wired into any Makefile
  target).
- **Wiring `oracle_store/libpcre2-10.46/membership.tsv` as an existing
  check's actual oracle** — `tests/uprops/uprops_compare.py`'s drift
  policy, or `tests/utf8/axis12_scripts.rxt`'s own S-U12 population, still
  compare against whichever library the box resolves locally, not against
  this store. The design's own §9 migration-ladder framing scopes this as
  a SEPARATE step; this lane discharges the CAPTURE, not the rewiring.
  Exact next command for whoever takes that step:
  `python3 tests/oracle/build_uprops_store.py remote --chunk 60` to
  refresh the store (idempotent regeneration, per §7.1a) before pointing
  a check at it.
- A general six-kind `RemoteAdapter` (the current one answers `membership`
  only, by design — see the module's own header) — build by embedding
  `br_oracle.py` in the payload alongside `pcre2_ctypes.py`, the moment a
  real customer needs a reference `compile-accept`/`match-at` answer (D77).
- `LocalAdapter` support for a non-default `OracleId.config` — needs a
  `pcre2_match_context` built with `pcre2_set_match_limit`/`_depth_limit`/
  `_heap_limit`; neither borrowed binding exposes one today, and this
  lane's own customer never asks for a non-default config.
- Steps 2-4 of the migration ladder (C3, PC-3/PC-4, the shared-binding
  family) — explicitly out of this lane's scope, named in the design as
  later, unscheduled rungs.

## Handback

Branch `lane/orstore` at commit `01ae6fcf`, parked (per BOILERPLATE, no
merge to main from this lane). Validation is COMPLETE for everything listed
under "Done" above and OWED exactly as listed under "Owed" — the manager or
a fresh agent can run the owed `make test` once the current battery clears
and merge if it stays green (nothing here should move it).
