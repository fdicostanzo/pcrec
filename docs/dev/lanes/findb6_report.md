# [FINDINGS] B6 — the analyzer in C (2026-09-28, lane findb6, sonnet)

`docs/design/findings/design.md` §13's B6 row: `analyze/` -> `build/
pcrec-analyze`, generators switch to it, python ≡ C agreement, then the
python prototype is DELETED (implement-then-replace). Delivered in FOUR
separate commits on `lane/findb6` so the agreement evidence survives in
history, per the brief's own ordering: (1) build the C analyzer, (2) wire
its acceptance suite + prove agreement while the prototype still existed,
(3) switch the generators, (4) delete the prototype and convert the
agreement check into what §11.8 anticipates it becomes.

## What was built

- `analyze/` (`analyze.h`, `count.c`, `sha256.c`, `main.c`, own CLAUDE.md):
  a SEPARATE, zero-dependency binary — links neither `libpcrec.a` nor
  anything under `src/`/`cli/`/`lib/`. Ported 1:1 from `scripts/
  pcrec_analyze.py` (B3): the same four command forms (`--scan`/`--merge`/
  `--digest-only`/`--check`, design.md §10.2), the shard-bounds arithmetic
  ([r2 A-1]'s k=1 exception, [r2 A-2]'s cpfreq lead-byte seam), strict
  UTF-8 decode (Unicode's well-formed-byte-sequence table — the same rule
  CPython's `errors="strict"` enforces, byte for byte: overlong forms,
  surrogates and code points past U+10FFFF are all refused per lead byte),
  the bundle-text writer and its own bundle-text reader (`--merge`/
  `--check`), `--fidelity`/`--adaptation` (B5), and a one-shot SHA-256.
  `make` builds it as part of `all`; `make strict` covers its three `.c`
  files alongside `scripts/findgen.c` (the tree's other standalone build
  tool) and `cli/main.c`.
- `tests/findings/run_analyzer_agree.py` — the design.md §11.8 "python ≡ C
  (implement-then-replace)" proof, run ONCE while both implementations
  existed: the in-tree fixtures across every `--scan` combination,
  shard/merge round trips (N=1..7), `--check` (positive/negative/missing-
  source), R26, `--fidelity`/`--adaptation`, 800 seeded-random invocations
  (seed 20260928, invalid UTF-8 included), and the two real shipped
  corpora (`log`/`weblog`) at `generate.py`'s own exact flags. **47/47
  PASS, 0 divergences anywhere.** Deleted in commit 4, its job done — see
  below for what replaced it.
- `tests/findings/run_analyzer_tests.py` (B3's own acceptance suite)
  REPOINTED at `build/pcrec-analyze`. Its own `parse_bundle`/
  `shard_bounds`/`is_continuation_byte` are now a SEPARATE, independently
  written reader — it no longer imports the python module (which is
  deleted), and per `learnings.md` §3 ("a reader and its check must not
  share a source") that is the right shape regardless. R27a (analyzer
  output round-trips through `pcrec --list-analysis NAME -I <dir>`) was
  an OWED info line since B3; it is now RUN FOR REAL (B2 landed since):
  live-verified PASS.
- The two shipped generators (`third_party/synth-log-lines-v1/
  generate.py`, `third_party/elastic-examples-apache-logs-bc53b584/
  generate.py`) switched their `ANALYZE` path from `scripts/
  pcrec_analyze.py` (via `sys.executable`) to `build/pcrec-analyze`
  (direct exec), with an `ANALYZE.exists()` guard mirroring the existing
  `CORPUS.exists()` one. `tests/findings/run_findings_tests.sh` had TWO
  MORE call sites the brief's own charter did not name — §6 #21 (R27a)
  and §11.4 (d) (the Latin-1 `encode-utf8` witness) each shell out to the
  analyzer directly to build an ad-hoc fixture bundle, not through a
  generator — found by grepping the whole tree for `pcrec_analyze\.py`
  rather than assuming the two `third_party/` sites were the only
  customers. Both switched to a new `$ANALYZE` variable set beside the
  script's existing `$PCREC`.
- `scripts/pcrec_analyze.py` DELETED. `tests/findings/
  run_analyzer_pinned.py` + `tests/findings/golden/*.rxt` (8 committed
  golden files) is what design.md §11.8's "python ≡ C
  (implement-then-replace)" row becomes with no python left to compare
  against — its own header states the succession. It re-runs the same
  representative case population against committed golden output
  (regenerate with `--write`), plus R26 and the two shipped bundles' own
  `generate.py --check` (S325/S326's own mechanism, re-asserted here at
  zero extra cost since it is exactly this row's population).

## The port: what it found

**Nothing wrong in the prototype — the finding is entirely about the
port's own method.** `run_analyzer_agree.py`'s 47/47 and the real-corpus
byte-identity checks (below) are evidence the port is exact; nothing here
is a correction to B3.

1. **A python `dict`'s insertion order matters for one output byte
   position and C has no such thing for free.** `render_bundle`'s "analyzer
   ... --scan ..." line always lists kinds in CANONICAL order
   (`freq,cpfreq,bigram`) regardless of what order `--scan` was TYPED in —
   confirmed by reading `scripts/pcrec_analyze.py`'s `render_bundle`
   (`scan_list = [k for k in CANONICAL_KINDS if k in blocks]`) rather than
   assumed from the CLI table. `analyze/count.c`'s `render_bundle` builds
   its csv the same way, walking `PCREC_ANALYZE_CANONICAL_KINDS` rather
   than whatever order `main.c`'s arg parser happened to set flags in.
2. **`--merge`'s `nominal_bytes_total` is a max over KINDS, not shards —
   and that makes shard/part ORDER genuinely irrelevant to it**, which
   simplified the C port materially: `cmd_merge` accumulates every part's
   rows and provenance in a single pass with no shard-order dependence
   anywhere (`kind_block_merge_from`'s addition is commutative/
   associative; `combine_encoding`'s lattice-max fold is too), so nothing
   in `main.c` needed to replicate python `dict`'s insertion order at all
   for THIS command — a relief after finding (1) needed exactly that
   for rendering.
3. **Python's `parse_bundle` has a documented-looking branch that is
   actually dead in one direction**: `elif findent > 12 or (findent == 8
   and False):` — the `and False` term is always false, so an indent that
   is neither 8, nor 12-while-in-provenance, nor >12 is silently SKIPPED,
   not refused. The C port (`analyze/count.c`'s `parse_bundle`) mirrors
   this exactly, with a comment naming it, rather than "fixing" it into a
   refusal — this file reads only bundles this tool itself writes (or a
   human's deliberate `--merge`/`--check` input), and changing acceptance
   here was out of this port's scope.
4. **Strict UTF-8 needed the FULL Unicode well-formed-sequence table, not
   a naive "check continuation-byte ranges" decoder** — get it wrong and
   `classify_encoding`/R26/`cpfreq` all silently diverge from CPython on
   overlong 2-byte sequences (`C0`/`C1` lead bytes), the E0/ED per-lead-byte
   second-byte range narrowing (excludes overlong 3-byte forms and the
   D800-DFFF surrogate range respectively), and the F0/F4 equivalent for
   4-byte sequences (excludes overlong forms and code points past
   U+10FFFF). Verified against CPython directly: 800 seeded-random byte
   strings including these exact edge shapes, 0 divergences; a fixed
   fixture (`invalid_utf8.bin`) and the shard-seam fixture
   (`cpfreq_seam.txt`, built to straddle continuation bytes at every cut
   offset for N=1..23) both agree byte for byte.
5. **`--merge`'s own module docstring records a judgment call** (findb3's
   own: `--bytes`/`--sha256` as flags rather than a bare positional, so the
   shard-total integrity check the design text names is actually
   buildable) — the C port keeps that shape unchanged; it is not this
   lane's to re-litigate, and changing it would break `run_analyzer_agree.
   py`'s own shard/merge round trip by construction.

## Validation

- `make strict CC=gcc-16`: clean throughout (analyze/'s three files
  compile warning-free under `-Werror -Wshadow`; one real
  `-Wformat-truncation` finding in `cp_key`'s 6-hex-digit branch, fixed by
  widening the buffer from 10 to 16 bytes before the first commit).
- `run_analyzer_agree.py`: **47/47 PASS**, 0 divergences — in-tree
  fixtures x 4 `--scan` combos, shard/merge N∈{1,2,3,5,7} on two
  fixtures, `--check` positive/negative/missing-source, R26 (all three
  outcomes), `--fidelity`/`--adaptation`, 800 seeded-random invocations
  (invalid UTF-8 included), and the two real shipped corpora at
  `generate.py`'s own exact flags (`log` 4,143 B / `weblog` 5,250 B,
  both byte-identical).
- `run_analyzer_tests.py` (repointed at the C binary): **37 PASS / 1 INFO
  / 0 FAIL** — the 1 INFO is the pointer to `run_analyzer_agree.py` (this
  suite no longer does the python-comparison itself). R27a now runs for
  real and passes.
- `make gen-tables && git diff --exit-code`: **NOT byte-identical before
  the switch — exactly the header-comment lines naming the analyzer path**
  (`scripts/pcrec_analyze.py` -> `build/pcrec-analyze`, two lines each in
  `src/findings/log.rxt`/`weblog.rxt`, mirrored into
  `src/core/findings_store.inc`). This is the ONE population §13's own
  acceptance line ("byte-identical before/after the switch") did not
  anticipate, because the generators' own `HEADER` string NAMES the
  analyzer script by path — a fact the port itself changes. Confirmed
  comment-only, not data: `src/core/findings_table.inc` (the PARSED table
  a compile actually reads) is untouched, and `findings_ref.py`'s digest
  function hashes normalized ppm VALUES, never file text, so no
  `<PREFIX>_FINDINGS` stamp moves. Re-ran `make gen-tables` a second time
  after committing the new header text: clean (`git diff --exit-code`
  passes), confirming the regeneration is now idempotent — this IS the
  design row's real acceptance criterion once its own premise (the header
  never mentions the tool) is corrected.
- Full `make test-findings` (twice, before and after the generator
  switch): GREEN both times — `run_findings_tests.sh` (B1/B2/B5's own
  sections, including the §10 sampled answer-identity slice through
  `tests/axes/run_axes.sh`) + `run_analyzer_tests.py` (37/1/0) +
  `run_analyzer_agree.py` (47/0) on the first run (pre-switch); the
  second run (post-switch, still with the prototype present) reads clean
  in `/tmp/tf2.log` — `run_findings_tests.sh` + `run_analyzer_tests.py`
  (37/1/0) + `run_analyzer_agree.py` (47/0), zero FAIL/Error lines
  anywhere in the log.
- `run_analyzer_pinned.py` (the post-deletion standing check), run
  STANDALONE: **11/11 PASS** — 8 golden-file matches, R26, and both
  shipped bundles' `generate.py --check` (which now runs
  `build/pcrec-analyze` exclusively, since the prototype is gone).
  `python3 tests/findings/run_analyzer_tests.py` also re-run standalone
  post-deletion: 37/1/0 unchanged (it never imported the deleted module).
  `make strict` clean post-deletion.
- **OWED**: the FULL `make test-findings` (all three scripts together,
  `run_findings_tests.sh` + `run_analyzer_tests.py` +
  `run_analyzer_pinned.py`) launched as this lane's last act on the
  fully-deleted tree, detached (`nohup make test-findings CC=gcc-16 >
  /tmp/tf3.log 2>&1 &`, PID 65515) per BOILERPLATE's DO-THEN-FINISH —
  the box was carrying concurrent load from another lane's (`findb4`)
  own FINDINGS-axis `run_axes.sh` sweep for this whole window, so the
  §10 slice was still running at hand-off. Every individual piece it
  would re-run has already been verified standalone above (this run adds
  nothing new except confirming they hold TOGETHER, in one process, on
  the fully-deleted tree). Log path: `/tmp/tf3.log` on the dev Mac
  (**note**: this is outside the session scratchpad the brief named —
  the run was already in flight when that was noticed; nothing here is
  committed, but a future lane should launch OWED background runs inside
  the assigned scratchpad, not bare `/tmp`). Completion line to look for:
  `checks passed: 11` with no `FAIL` above it (the `run_analyzer_pinned.py`
  section) preceded by clean `run_findings_tests.sh`/`run_analyzer_tests.py`
  sections and no `*** [test-findings] Error` line.

## What §11.8's own acceptance line got right and wrong

"`make gen-tables` byte-identical before and after the switch" is the
row's own stated verdict, and it is subtly wrong as written: the switch
is NOT byte-identical, because the generators' committed HEADER text
literally names the analyzer's path, and the port itself is a path
change. The corrected reading — confirmed live, not merely argued — is
"no DATA byte moves; only the two comment lines that name the tool do,
and only in the two generated `.rxt` files whose header states that
tool's identity." Recorded here so the NEXT implement-then-replace row
in this house does not re-derive the same correction: a tool-identity
comment embedded in a generated header is, structurally, part of what
"the switch" touches, and belongs in the acceptance line from the start.

## Coordination note (lane findb4)

findb4 runs concurrently and adds a `bigram` kind to the analyzer's
OUTPUT (per the brief). Per design.md §13 B4's own row, `bigram` is
**already admitted to `--scan`'s CLI surface and the bundle TEXT SHAPE**
in both the prototype and this port (`CANONICAL_KINDS` includes it;
`derive_serves`/`render_kind_block` both have a full `KIND_BIGRAM` arm;
`--scan freq,bigram` works today and is exercised throughout this lane's
own test population). What is genuinely NOT yet admitted is the `.rxt`
**SCHEMA row** for a `bigram` DATA block inside a BUNDLE scope
(`src/parse/rxt_schema.def`'s own comment: "`bigram` is NOT a row yet —
it is admitted with its first reader, R2, B4") — confirmed live: a
`--scan freq,bigram` bundle fed to `pcrec --list-analysis` refuses with
`'bigram' is not a analysis-bundle directive`, while a `freq,cpfreq`
bundle (B5's scope) parses clean. **Surfaces findb4 will need to add in
C, if its own charter is the schema/reader side rather than the analyzer
CLI**: none in `analyze/` itself — the analyzer already emits `bigram`
blocks in their final shape (design.md §2.4's `markov1` derivation, the
"byte,utf8"-or-"byte" `serves` line depending on encoding, ascending
`row AA BB N` keys). If findb4's charter is instead the RESOLUTION/READER
side (`src/parse/rxt_schema.def`'s `BUNDLE "bigram"` row,
`src/core/findings.c`'s run-rarity reader, `markov1`'s `L(x)` algorithm),
that is entirely outside `analyze/` and this lane made no C changes
there. The manager sequences the merges; whichever lands second should
re-run `run_analyzer_pinned.py`/`--write` only if the BUNDLE TEXT SHAPE
itself changes (it should not, from either side).

## Commits (on `lane/findb6`, from main `d604bee9`)

1. `[FINDINGS] B6: the C analyzer, analyze/ -> build/pcrec-analyze` — the
   standalone build, unwired.
2. `[FINDINGS] B6: repoint run_analyzer_tests.py at the C binary; prove
   agreement` — `run_analyzer_agree.py` (47/47 PASS), the acceptance
   suite repointed, wired into `make test-findings`.
3. `[FINDINGS] B6: switch the generators to build/pcrec-analyze` — both
   `third_party/*/generate.py`, `run_findings_tests.sh`'s two internal
   call sites, `make gen-tables` re-run (the header-comment movers above),
   living-doc updates (`tests/CLAUDE.md`, `docs/spec/findings.md`,
   `third_party/CLAUDE.md`, both `PROVENANCE.md` files).
4. `[FINDINGS] B6: delete the python prototype; run_analyzer_pinned.py`
   — `scripts/pcrec_analyze.py` removed, `run_analyzer_agree.py` removed,
   `run_analyzer_pinned.py` + `golden/` added and wired in its place,
   `scripts/CLAUDE.md` updated.

## Owed / open

- **`docs/design/findings/design.md` §13's own B6 acceptance line** ("make
  gen-tables byte-identical before/after the switch") is imprecise per the
  finding above; not edited here (D80: a design document's own revision is
  its own change) — flagged for the manager/Frank.
- The manager's full `make test` battery at merge (BOILERPLATE: the full
  battery is the manager's).
- `make mech`'s `findings` arm was not re-run standalone by this lane
  (no `src/` change touches anything it covers — this lane's only `src/`
  changes are the ones in `analyze/`, which `make mech` does not build or
  sabotage); flagged rather than assumed clean.
