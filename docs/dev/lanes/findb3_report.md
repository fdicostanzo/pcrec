# findb3 — `[FINDINGS]` step B3: the analyzer PROTOTYPE

Lane `findb3`, sonnet, 2026-09-26, branch `lane/findb3` from main
`27a63314`. Scope: `docs/design/findings/design.md` §13's **B3** row only —
the analyzer PROTOTYPE (`scripts/pcrec_analyze.py`, §10) and its own
checks (`tests/findings/`). B0 (the `.rxt` schema's `analysis` bundle), B1
(the accessor + default + gate move) and B2 (resolution + CLI +
`--list-analysis`) have **not landed** — confirmed before writing anything
(`src/core/findings.*` does not exist; `rxt_schema.def` has no `analysis`
row). Nothing under `src/`, `cli/`, `lib/` touched. Delivered
BUILT-AND-VALIDATED (own fixtures + `make strict` only, per the box's
one-heavy-suite hold); `make test`/`test-axes` NOT run (queued on this box
per BOILERPLATE).

## What was built

- `scripts/pcrec_analyze.py` (743 lines) — the four command forms design.md
  §10.2 specifies (`--name`/`--retrieved [--scan]`/`--shard`; `--merge`;
  `--digest-only`; `--check`), grown from `docs/dev/findings_measure/
  scripts/ngram_count.py`'s one-pass counting shape (that module's own
  docstring names itself "the prototype for the one-counter rule" — this
  file is what actually takes on that role; it does not import
  `ngram_count.py`, so the completed measurement lane and this permanent
  tool do not couple — see `scripts/CLAUDE.md`'s new entry for the full
  reasoning).
- `tests/findings/run_analyzer_tests.py` + `tests/findings/fixtures/*` —
  the B3-scoped subset of design.md §11.8's acceptance list, PASS:/FAIL:/
  INFO: lines and a `checks passed`/`checks FAILED` trailer matching house
  convention. `make test-findings` (light, no `all` dependency, NOT in
  `TEST_SECTIONS` — see `tests/findings/CLAUDE.md`).
- `tests/findings/CLAUDE.md`, `scripts/CLAUDE.md` (new entry), `tests/
  CLAUDE.md` (new bullet) — directory charters updated per convention.
- `docs/dev/plan.md`'s `[FINDINGS]` row and `docs/dev/lanes/CLAUDE.md` —
  progress recorded (the row was stale: design.md's own STEP 2 — PANELED
  r2, REVISED — had already landed with no plan.md note; both that fact
  and B3's delivery are now recorded in the same edit).

## What each design.md §11.8 acceptance item reads (B3's own row, §13)

The B3 row's gating measurement names: "§11.8 determinism/shard-merge/
shard-1/cpfreq-seam/--check/R26/R27a; its output for RUNEST's web_request
sample normalizes (through B1's function) to RUNEST's unigram."

| item | reads | evidence |
|---|---|---|
| determinism (R27c) | PASS — two runs, same input+flags, byte-identical; no clock read anywhere in the tool (`--retrieved` is a required flag, never `datetime.now()`) | `check_determinism` |
| stdin ≡ file | PASS — explicit `-` and an omitted FILE both equal the FILE form; `--shard` refuses stdin outright (design.md §10.4's last sentence) | `check_stdin_equals_file` |
| shard/merge (F-7, D123-3a) | PASS — N=1..7, full permutations at N≤4, three seeded shuffles above, each byte-identical to the whole-file scan, over THREE scan combinations (`freq,bigram`; `cpfreq` alone; `freq,cpfreq,bigram` together) | `check_shard_merge` |
| shard 1's first byte ([r2 A-1]) | PASS — a byte occurring at offset 0 only counts exactly 1 under every N in {1,2,3,4,5,8} | `check_shard1_first_byte`, fixture `shard1_first_byte.bin` |
| cpfreq seam ([r2 A-2]) | PASS — 2-, 3- and 4-byte code points at varying run lengths; N swept 1..23, every merge byte-identical to the whole-file cpfreq count; the sweep DID land a nominal cut mid-code-point (`seen_straddle=True`, printed) — a straddle-free sweep would have been evidence of nothing | `check_cpfreq_seam`, fixture `cpfreq_seam.txt` |
| python ≡ C (implement-then-replace) | **NOT APPLICABLE** — `analyze/`'s C end state is build step B6, which has not started. Recorded as an INFO line, never silently skipped (design.md §9's "never") | `check_python_equals_c` |
| `--check` | PASS — a matching recount exits 0; a one-byte-changed source is rejected; a **missing** source ([r2 A-5]'s analyzer-level analogue of a manifest-only third_party source) fails CLOSED with a named reason, never a silent skip | `check_check_command` |
| R26 | PASS — `--scan cpfreq` on invalid UTF-8 hard-errors; `--scan freq` on the SAME input succeeds; `--scan freq,cpfreq` on it also hard-errors rather than silently emitting freq alone (D123-3) | `check_r26`, fixture `invalid_utf8.bin` |
| R27a | **NOT YET TESTABLE** — B2 has not landed, so `pcrec --list-analysis` does not exist. INFO line, OWED to whichever lane lands B2 | `check_r27a` |
| §13 B3's own line: web_request normalizes to RUNEST's unigram | PASS, under the reading below | `check_runest_web_request` |
| §10.2's collision-free declarations ([r2 M-B1]) | PASS — scanning `freq,cpfreq` together on both the ascii-only and utf8-mixed observed rows splits `byte`/`utf8` with no overlap; the invalid-utf8 row is covered by R26's own hard-error test above (cpfreq cannot exist there at all) | `check_collision_free_declarations` |

Full run: 35 PASS / 0 FAIL / 2 INFO, `make test-findings` (also runnable
directly: `python3 tests/findings/run_analyzer_tests.py`), ~20s wall.

### The "normalizes to RUNEST's unigram" reading

The design's own sentence names no artifact to compare against (RUNEST's
`data/` directory has no separately-stored per-class unigram ppm table —
only bigram JSONs and the unrelated, hand-authored `byte_freq_ppm.tsv`
static prior dump). Read as: (1) `pcrec-analyze`'s raw `freq` counts over
`docs/dev/findings_measure/corpora/web_request.txt` must be
count-IDENTICAL to what `ngram_count.py`'s own `Counts.build(data).unigram`
computes over the same file (the shared-counting-implementation claim,
R27b, made a check rather than an assertion); (2) applying an INDEPENDENT
python re-implementation of §2.5's normalization algorithm (written from
the design text, not from any future C — `learnings.md` §3's rule) to
those counts must produce a well-formed byte-rate table (Σ=1,000,000,
every entry ≥ the 2 ppm floor). Both hold. **This is the closest check
available before B1's `src/core/findings.c` exists** — B1's own row
(design.md §13) is where "normalizes to `default_ppm.tsv` exactly" gets
its real oracle-verified home for the SHIPPED default; this check is
scoped to what B3 alone can prove about the counting+normalization
pipeline on a real, large (1 MB), out-of-corpus sample.

## Manager-review items (judgment calls where the design was ambiguous at B3's altitude)

1. **`--merge` gains `--bytes N --sha256 HEX` (not in §10.2's literal CLI
   table).** §10.4 says a merge's final `bytes`/`sha256` "come from a
   `--digest-only` run over the whole input ... and `--merge` checks that
   the shards' byte total equals it" — but §10.2's own signature is
   `--merge --name NAME PART.rxt...`, no file operand, and `--merge` can
   never recompute a whole-input sha256 from parts alone (sha256 is
   sequential; a shard PART only ever saw its own nominal byte range).
   Read as: the caller runs `--digest-only` once, hands both values to
   `--merge`, which verifies them against the SUM of the parts' own
   recorded `bytes` fields (this IS F-7's detector — reproduced live:
   `--bytes 999` against a real 1040-byte total refuses loudly) before
   stamping the merged bundle. Both flags optional; omitted, merge sums
   `bytes` with no `sha256` recorded. **Escalate if this reading is
   wrong** — the alternative (a positional FILE after the parts) is a
   two-line change if preferred.
2. **A cpfreq block with no freq sibling always declares `serves byte-rate
   when utf8`** (never `when byte,utf8`), even though §0.9 proves
   `encode-utf8`'s counts equal a hypothetical sibling `freq`'s on any
   decodable input. Design.md §10.2's table only states the split for
   "freq + cpfreq both scanned"; a cpfreq-ALONE bundle is outside that
   table. The conservative reading (never claim `byte` from a `cpfreq`
   block) is never WRONG per [r2 M-B1]'s own collision rule, only
   possibly less rich than allowed. Left as-is; a future lane can widen it
   once a real cpfreq-alone bundle exists to test it against.
3. **Provenance metadata mismatches across `--merge` parts (differing
   `source`/`retrieved`/`url`/`ref`/`license`) are a hard error**, not a
   silent pick-one. Not stated either way by the design; chosen for
   consistency with design.md §9's "never [silent]" ethos and R27c's
   determinism requirement (a silent pick would make the merged output
   depend on part ORDER, which D123-3a explicitly forbids for counts and
   there is no stated exception for metadata).
4. **`question`/`reader` prose fields are boilerplate this tool writes**,
   not derived from anything the design specifies precisely beyond the
   shipped `default.rxt` exhibit (a hand-authored bundle, not analyzer
   output). Free text, not gated by any check; a future lane can improve
   the wording without moving anything a check reads.
5. **`--check` also verifies provenance `bytes`/`sha256` drift**, beyond
   the literal "exit 0 iff a recount reproduces the rows." Cheap, and
   strengthens the manifest-only-source analogy (A-5) — a source whose
   size changed without its rows changing (or vice versa) is now caught
   too. If this over-reaches the design's stated contract, it is a clean
   revert (the `bytes`/`sha256` block in `cmd_check`).
6. **`make test-findings` is deliberately NOT added to `TEST_SECTIONS`.**
   BOILERPLATE says "if you add them to a make target, it must be a light
   one" — this is that, but B1/B2's own rows (§13) are what name `make
   test-findings` as part of THEIR verdict, once there is an accessor and
   a CLI to check answer identity against. Wiring it into the full battery
   now would test nothing beyond what its own 35 checks already cover.
   Flagging for the manager: confirm this reading before B1 lands (B1's
   own acceptance table already lists `test-findings` as one of its
   verdicts, so nothing is lost either way).

## A defect this lane found and fixed while validating, before it shipped

Classifying a sharded scan's `encoding` field from the shard's own NOMINAL
freq byte range (`[start_K, end_K)`) is wrong: that range can end mid-way
through a multi-byte UTF-8 sequence, so a shard that is genuinely the
middle of valid UTF-8 text would read "bytes" (invalid) purely from where
its boundary happened to fall — caught by the cpfreq-seam sweep failing at
N=3+ with an `AssertionError` from `derive_serves`'s own "cpfreq present
with encoding=bytes" guard (the guard did its job: it turned a wrong
declaration into a loud crash rather than a silently-wrong `.rxt` line).
Fixed by classifying encoding from the code-point-ALIGNED window
([r2 A-2]'s own seam adjustment, computed unconditionally now, whether or
not `cpfreq` was requested) instead of the raw nominal range. Re-swept
N=1..23 clean after the fix (see the "cpfreq seam" row above).

## Validation

- `make strict` (gcc-16): clean, no `src/`/`cli/`/`lib/` change to break
  anyway.
- `make test-findings`: 35 passed / 0 failed / 2 INFO (both named OWED
  items above), ~20s.
- Manual smoke (not part of the committed suite, transcript above in the
  session): freq/cpfreq split on ascii-only and utf8-mixed samples;
  kind-disjoint merge (`--scan freq` + `--scan bigram` separately, merged)
  byte-identical to a single `--scan freq,bigram` run except for the
  documented sha256-absent-without-digest case; R5's ASCII identity
  (`freq` counts == `cpfreq` counts on pure-ASCII input) confirmed
  programmatically.
- NOT run: `make test`, `make test-axes` (queued on this box per
  BOILERPLATE's one-heavy-suite rule) — B3 needs neither (no `src/`
  change), so nothing is owed there.

## Delivery

Branch `lane/findb3`, committed incrementally, PARKED — **not merged**.
Files: `scripts/pcrec_analyze.py`, `scripts/CLAUDE.md`, `tests/findings/`
(new directory: `run_analyzer_tests.py`, `CLAUDE.md`, `fixtures/*`),
`tests/CLAUDE.md`, `Makefile` (`test-findings` target),
`docs/dev/plan.md`, `docs/dev/lanes/CLAUDE.md`, this report.
