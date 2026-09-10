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
