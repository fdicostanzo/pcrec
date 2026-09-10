# oraiface — oracle interface + answer store design note lane report

2026-09-10, lane oraiface, Sonnet, Mac-local, read-only + doc-writing (no
`make`, no suite runs). Charter: Frank's two 2026-09-09-late directives
carried in `docs/dev/wake.md`'s lane-3 spec. Deliverable:
`docs/design/oracle_interface.md`.

## What shipped

A PROPOSED, unpaneled design note for the oracle interface and answer
store, per D77 — note + fixture-shaped examples only, no store
implementation, nothing under `src/`/`tests/`. Structure:

- **§1 survey** of every oracle consumer in the tree as it stands at this
  worktree's branch point (`9e436d31`): `tests/harness/verify_rxt.py` (C3,
  python `re`, in-process); `tests/registry/pcre2_check.c` (PC-3,
  direct-linked, compile-accept only, 8 sweeps sharing one primitive,
  149,804-probe POSIX population measured live from the file);
  `tests/registry/pc4_check.c`/`definitions_oracle_check.c` (PC-4-family,
  compile-accept + match-at, 62,872-cell measured population);
  `tests/uprops/uprops_oracle.c` (the chartered first customer — the
  distinct **membership** kind, whole-code-point-space sweep, 91
  properties measured on the byte arm, ~387 derived — not independently
  re-measured this lane — for utf8); the shared `pcre2_ctypes.py` →
  `br_oracle.py` → `la_oracle.py`/`u8_oracle.py` borrowing chain behind
  backrefs/lookaround/atomic-groups/recursion's diff drivers (already
  batched, stdin-protocol); `tests/fuzz/pcre2_oracle` (the one UNBATCHED,
  one-process-per-call shape — named as the anti-pattern, not a
  precedent); the fuzzer (poor caching fit, random population); and
  `docs/design/utf8_measurements/probes/bundle.py`/`archive.sh` — the
  ssh-stdin-payload remote transport the charter names directly as the
  adapter's native batch shape (verbatim-embedded borrowed source,
  nothing written on the far end). `docs/pcre2_compliance.md`'s
  independent survey is named and explicitly ruled OUT of scope
  (`[DOC-DRV]`'s checked-tension architecture would be defeated by
  folding it in).
- **§2** a five-member closed `Question` kind-set — `compile-accept`,
  `match-at`, `captures`, `name-accept`, `membership` — aligned with but
  not equal to the `.rxt` directive vocabulary (`name-accept` and
  `membership` answer questions no `.rxt` cell asks; three reasons given
  for keeping `name-accept` its own kind rather than a synthesized-pattern
  `compile-accept`).
- **§3** `OracleId = (name, version, config)`, with `config` scoped to
  answer-affecting fields only (UTF/CASELESS in; `PCRE2_NO_UTF_CHECK`
  measured inert for every question these kinds ask and excluded;
  `PCRE2_UCP` has no producer anywhere in the tree and is excluded per
  D77/build-under-measurement).
- **§4** canonical tab-separated serialization per kind, reusing `.rxt`'s
  OWN subject-escape vocabulary (no second escape scheme invented) and a
  16-hex-char sha256 question hash — `bundle.py`'s own truncation, reused
  rather than re-decided.
- **§5** byte-stable per-kind answer shapes, including a `giveup` third
  state on `match-at` for a real PCRE2 match-limit/depth-limit answer
  (not in any surveyed population today, but `.rxt`'s own `gu` directive
  already has the shape).
- **§6** the `capabilities()` + `answer(batch)` adapter contract, two
  concrete shapes (local direct-link, in-process, `max_batch: none`;
  remote ssh, generalizing `bundle.py` from one probe to one Question
  batch, `max_batch` a real caller-respected knob per BOILERPLATE's
  light-probes-only rule).
- **§7** store format: TSV-ish, one file per `(OracleId, kind)`, on the
  `third_party/`/`docs/dev/artifact_size_log.tsv`/`table_contract.md`
  house precedent; reference store committed (with a `PROVENANCE.md`-
  equivalent per `OracleId` directory), local caches gitignored under a
  `build/`-shaped separate tree; size table from measured populations,
  honestly flagging the utf8 membership table's real size as unmeasured
  rather than estimating further.
- **§8** the staleness-impossibility argument in three claims (same key ⇒
  same answer, structurally; a version bump is a clean miss by
  construction, no TTL/invalidation needed; only the oracle side caches,
  so a stale pcrec-side answer can never hide behind a fresh oracle one —
  `docs/dev/learnings.md` §3's shared-source lesson applied to cache
  design).
- **§9** a four-step migration ladder: uprops byte+utf8 first (discharges
  the wake.md-owed STAGE-5 10.46 EXACT arm without darwin owning the
  reference — the S-U6/S-U9 closing witnesses ride it); then C3 (python
  `re`, uniformity dividend); then PC-3/PC-4 (dissolves the U13/U15b
  divergence class for cached questions, live-calls for new ones); the
  shared-binding family named but unscheduled.
- **§10** what does NOT change: `.rxt` files, the driver protocol, every
  existing check's verdict logic, `pcre2_compliance.md`'s independence,
  no pcrec-side cache.
- **§11** the `.rxt` provenance dividend, sketched (not designed — needs
  its own D77 trigger).
- **§12** fixture-shaped examples, one per kind, using real corpus
  material (the backrefs re-entry family for match-at/captures, a uprops
  script for name-accept/membership, a PC-3-style verb probe for
  compile-accept).
- **§13** five open questions for the panel: store location (top-level
  `oracle_store/` vs `tests/oracle_store/`), hash truncation length,
  whether `name-accept` earns its own kind, whether `OracleId.config`
  needs a non-answer-affecting provenance field, and the untested real
  size of the utf8 membership table.

`docs/design/CLAUDE.md` gained the file's entry in the same change.

## Validation

None owed — this is a design-note-only lane (D77), no code, no suite runs.
Every population figure cited as MEASURED was read directly from the named
file (`pcre2_check.c:1666`'s 149,804; `pc4_check.c`'s header's 62,872;
`tests/uprops/CLAUDE.md`'s 91 properties / 1,053 names); the one DERIVED
figure (utf8 arm ~387 membership questions) is flagged as such in both the
note and here, not asserted as measured.

## Handback

Status: COMPLETE for this lane's scope. The design note is committed on
`lane/oraiface`, ready for the manager's D6 panel. No follow-up work is
owed from this lane; the uprops instance is the next lane once the panel
dispositions land, per the charter.

## 2026-09-10 — r56 revision (lane `oraiface2`)

Two critics (r56cons + r56mech) panelled the note above
(`docs/dev/reviews/2026-09-10-r56-oracle-interface.md`). The survey held
exact under re-derivation (every population number reproduced, DOC-DRV's
exclusion structural, no wire-format impedance in the ssh transport); the
mechanism had two deterministic-failure BLOCKERS and one ladder
misattribution. All eight numbered dispositions plus the stale-comment side
fix are applied in this commit, on top of `acde84d5`, directly to
`docs/design/oracle_interface.md` (no store code lands — still D77-scoped).
Disposition-by-disposition checklist:

| id | disposition | hunk |
|---|---|---|
| R56-1 (BLOCKING) | serialization injectivity — canonical form is `rxt_format.md`:458-474's FIVE-escape TSV-framing subset (`\\ \t \n \r \xNN`), backslash escaped FIRST, stated normatively; both vocabularies named, the seven-escape quoted-context one explicitly rejected; trailing-backslash test vector stated | §4, rewritten in full (the injectivity refutation, the two-vocabulary comparison, the producer rule, the test vector) — §12's `(a|b\1)+` fixture corrected to `(a|b\\1)+` and a new real-corpus fixture added (`tests/base/escapes.rxt:34`'s `pattern \\`, the trailing/all-backslash case) |
| R56-2 (BLOCKING) | limit triple (`match_limit`/`depth_limit`/`heap_limit`) joins `OracleId.config` with explicit defaults; §8 Claim 1 restated over the widened key; a giveup answer cacheable ONLY under a fully-keyed config; §3's NO_UTF_CHECK/UCP exclusion argument unchanged | §3's `config` bullet (new limit-triple paragraph, defaults measured via `pcre2_config()` against this box's resolved 10.48 binding: match=10000000, depth=10000000, heap=20000000 KiB, cited to `docs/design/subroutines_measurements/probes/sr_oracle.py`'s own answer-flip cells); §8 Claim 1 rewritten; §7.1's `<config-tag>` paragraph extended |
| R56-3 (MUST-FIX) | store-format/serialization-rule version field per file header, so an encoding change is a clean miss like an oracle version bump; §8 gains Claim 4 | §7.1 new paragraph (`store_format_version` header field); §8 new Claim 4 |
| R56-4 (MUST-FIX) | per-`(OracleId,kind)` file header carries its own row count + provenance (the `artifact_size_log.tsv` precedent's ACTUAL shape); readers verify a fetched row's question text equals the query's serialization before trusting the answer | §7.1 new paragraph (row count + provenance stamped per file; the question-text verification tripwire) |
| R56-5 (MUST-FIX) | store discipline: regeneration sorted-by-hash with a duplicate-hash detector as a check; owning-lane regeneration, never an unsorted append; merge protocol (re-derive on conflict, never hand-merge) | new §7.1a "Store discipline" |
| R56-6 (cons-F1, BLOCKING) | un-conflate the two owed items: S-U6/S-U9's closing witnesses are `match-at`-kind, ill-formed-subject cells riding a LATER ladder rung; what uprops-first (Step 1) discharges is the STAGE-5 drift-zeroing 10.46 arm, S-U12's neighborhood | §0 (the charter summary) and §9 Step 1, both corrected in place with the S-U6/S-U9-vs-S-U12 distinction spelled out and cited to each row's own `sabotages/*.sh` header |
| R56-7 (cons-F2, MUST-FIX) | the sixth kind, `pattern-info` (a compiled pattern's structural properties — the NAMETABLE/NAMECOUNT ordering differential D59/`rx_info.groups` rests on); same rigor as the other kinds (canonical nametable form defined); kind-set gains an extension rule (kind addition = store-format minor bump, existing kinds never re-keyed) | §2 (sixth kind + extension rule), §4 (added to the serialization grammar), §5.6 (new answer-shape subsection), §7.3 (size table row, deferred customer), §12 (new fixture using `tests/probes/probe_named_groups.c:159`'s own zeta/alpha/mu witness, D59's exact population) |
| R56-8 (MECH-8+9, required text) | newline/BSR and JIT-vs-interp named as excluded from `config` BY MEASURED FACT (no adapter varies them today), with the rule that an adapter varying either must widen config first | §3, new paragraph appended to the config bullet |
| stale-comment (D98 residue) | `tests/uprops/uprops_oracle.c`'s header still described the retired dlopen shim | `tests/uprops/uprops_oracle.c` lines 5-31, comment-only (verified `gcc -fsyntax-only` clean against the resolved Homebrew 10.48 headers) — the direct-link binding is named correctly, `--probe`'s mode is flagged DEAD CODE (`pcre2_abi_load()` cannot fail post-[ORACLE-LINK]), and the real loud-skip mechanism (`run_uprops_tests.sh` sourcing `resolve_pcre2.sh` at BUILD time) is stated in its place |

**Ratified-as-is items (16-hex hash, top-level `oracle_store/` lean,
`name-accept` staying its own kind, the membership-table git-posture
"measure before deciding") are UNCHANGED** — the review confirmed these
without requiring a text move, and §13's open-questions list is left as
written so the manager/Frank still see them as live questions rather than
silently pre-answered.

**One self-caught defect during this revision, worth recording**: an
early edit to §5.5→§5.6 accidentally dropped the `## 6. The adapter
contract` heading (the new §5.6 content was inserted immediately before
it and the old heading line was consumed by the edit's own old_string).
Found by a full section-header grep (`grep -n "^## [0-9]"`) before
handback, which is now the check to re-run on any future revision of this
file: 14 numbered sections, `0`..`13`, each exactly once.

**Validation**: prose-only revision — the check is internal consistency,
not a suite run (D77, same as the original lane). Verified: every §12
example round-trips under the §4 rules as revised (the corrected
`(a|b\\1)+` example and the two new backslash fixtures traced by hand
against the backslash-first rule); grepped the note for every remaining
occurrence of `S-U6`/`S-U9`/`S-U12` (two places, both corrected, matching
R56-6's own "fix both places" instruction) and of "five kind"/kind-count
language (all updated to six where the count was asserted, the five-escape
vocabulary's own "five" left untouched since it names the escape
vocabulary, not the kind-set); full `## [0-9]` section-header grep (14/14,
no duplicates, no gaps); `gcc -fsyntax-only` on the touched `.c` file.

**Handback**: COMPLETE. One revision commit on `lane/oraiface` (branch
unchanged, no new worktree), this report appendix in the same commit. A
fresh verify agent runs the B13-contract completion-contract pass against
this delivery before merge, per the charter; nothing else is owed from
this lane. Never merged to main by this lane.
