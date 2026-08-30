# lane w11f — r46 fix lane report

Branch `lane/w11f`, from main `8bee078` (the r46 review commit), merged
forward with `main` at `eda66d5` (Stage B). Written 2026-08-30.

Fixes the r46 panel's triage on the [DD-13b.W1.1] merge
(`docs/dev/reviews/2026-08-30-r46-w11-impl.md`): r46sem (1 BLOCKER + 8
must-fix + 14 shoulds/notes), r46chk (2 must-fix + several notes), plus
sem24 and sem32 from the notes tier, plus the manager's own ruling on
sem10 (blank line ends a config body).

**Headline results — measured on the merged tree**

| | |
|---|---|
| `make -j4`, `make strict` | **clean** (-Werror -Wshadow, whole tree) |
| `make test-rxtsource` | **78 passed / 0 failed** (up from the pre-existing 43 — the r46 fixtures add ~35 new checks) |
| `make test-codegen` | **run_group: 5/5 scripts passed**, every section 0 failed |
| `make test-cli` | **287 passed / 0 failed** |
| `make test-corpus` PROCS=4 | **26,680 passed / 0 failed**, 0 pattern-compile failures (distinct), 0 pending-vm, **178 of 178 file workers**, size-log 2,878 rows |
| sabotage row `S205` | **DETECTED** — `reach:ok(1/1), rxtsource:1fail/77pass, corpus:0fail/26680pass` (exactly the one new `ctrl_bytes` check goes red; nothing else moves) |
| control row `S203` (pre-existing) | **DETECTED**, unchanged — `rxtsource:1fail/77pass, corpus:0fail/26680pass` (confirms the r46 fixtures/checks did not blunt an existing row) |
| `make test-rxtsource` (merged tree, final) | **78 passed / 0 failed** |

---

## (a) Commits

| commit | what |
|---|---|
| `19fe528` | Phase 1 (code-only): all must-fixes (sem1-9, chk1-2, sem24, sem32) + shoulds 11-17, 19-21, 23; 14 new `.rxtin` fixtures; ~25 new checks; new sabotage row S205; CLAUDE.md updates in every touched directory |
| `34e52cc` | sem10 ruled by the manager: a blank line ends a `config` body exactly as it ends a block scalar (`parse_prose` fixed to match `parse_config`'s pre-existing rule); spec sentence; fixture `blank_ends_config_body.rxtin` |
| `b827cb7` | Stage A: the two failures `make test-rxtsource` found on its first real run — `run.sh`'s block-level `description` arm still did an exact `\|` compare (sem14's leg B half was missed in the Phase 1 commit); a wrong expected value in my own sem21 check (code was already correct) |
| `eda66d5` | `git merge main` (Stage B) — docs/journal/plan only, no file overlap, clean auto-merge |

---

## (b) Per-finding table

Legend: **A**/**B**/**C** = leg A (`src/parse/rxt_source.c`), leg B
(`tests/harness/run.sh`), leg C (`tests/harness/verify_rxt.py`).
"Fixture" names are under `tests/rxtsource/fixtures/*.rxtin` unless noted.

### r46sem must-fix / BLOCKER

| # | finding | commit | fixture | check | measured |
|---|---|---|---|---|---|
| sem1 (BLOCKER) | leg B's `rxt_escape` awk fallback mapped a byte's table INDEX to its `\xNN` render instead of its VALUE (0x0b→TAB, 0x7f raw) | 19fe528 | `ctrl_bytes.rxtin` | new `run_rxtsource_tests.sh` check (byte-for-byte three-leg compare) + sabotage `S205` | check: PASS (`test-rxtsource-2.log`); S205: field-valid, run owed below |
| sem2 | a tab inside a `with`/`from` config list accepted as a separator | 19fe528 | `tab_in_config_list.rxtin` | `check_refusal` (leg A only — head-only construct) | PASS |
| sem3 | `flags` accepted any letters in leg A; leg C's `--dump` path had no check at all | 19fe528 | `bad_flags.rxtin` | `check_refusal_all3` | PASS all 3 legs |
| sem4 | `engine dfa` accepted in legs A/C, refused in leg B (D80 defect); spec's own column table contradicted its own paragraph | 19fe528 | `bad_engine.rxtin` | `check_refusal_all3` + `rxt_format.md` column-table fix | PASS all 3 legs |
| sem5 = chk1 | leg C's `file_has_name` computed correctly then immediately re-initialized to `False`, shadowing the composed-block skip; dead `cur_name` | 19fe528 | (no population on the corpus; dead-code removal, verified by `python3 -m py_compile` + code inspection) | — | py_compile clean |
| sem6 | an oracle timeout was neither pass/fail/skip and left `verify_rxt.py`'s exit status untouched | 19fe528 | (C3's own pinned timeout file) | `--allow-timeouts N` in `run_rxtsource_tests.sh`'s C3 invocation | PASS (C3 reconciles, exit 0) |
| sem7 | `target ... with` names were never resolved against declared configs (only `from`'s cycle walk did); spec said both were validated | 19fe528 | `with_unknown.rxtin` | `check_refusal` (leg A only) | PASS |
| sem8 | too-long `config` name / `target` prefix / definition name reported "needs a name" (false) instead of naming the cap | 19fe528 | inline `toolong.rxt` in the check + `budget_overflow.rxtin` (sem12) | new checks + `docs/spec/limits.md` §3.5 | PASS |
| sem9 | `--list-source` missing from `table_contract.md`'s Scope table; "Six" vs "three" count mismatch | 19fe528 | — (doc-only) | `table_contract.md` gains 3 rows (list-source + the two others already missing) | — |

### r46chk must-fix

| # | finding | commit | fixture | check | measured |
|---|---|---|---|---|---|
| chk1 | (= sem5 above) | 19fe528 | — | — | — |
| chk2 | the unescaped-backtick sabotage-field check scanned one line per field, blind to 43 existing multi-line fields | 19fe528 | permanent self-test in `run_sabotage_matrix.sh` (planted-good/planted-bad) | `SAB_BT_AWK` rebuilt as a quote-state machine over the joined file text | self-test wired to run at script start; exercised live via the S205 VALIDATE_ONLY run below (script started clean, so the self-test passed silently — no FATAL) |
| chk3 (should, taken with sem6) | the "89" literal in C3's reconciliation had no update procedure | 19fe528 | — | `C3_TIMEOUT_FILE_LINES=89` named constant + comment | PASS (part of sem6's check) |

### notes taken

| # | finding | commit | measured |
|---|---|---|---|
| sem24 | `cli/main.c`'s `pcrec_error serr` uninitialized before a `calloc` that can fail | 19fe528 | zero-initialized at the call site; part of the clean `make -j4`/`make strict` build |
| sem32 | `docs/testing.md` had no hunk for `test-rxtsource` or the 11 mech rows | 19fe528 | new "`test-rxtsource` — INV-COMPAT" section + Section-targets table row |

### shoulds taken with a fixture each (as directed)

| # | finding | commit | fixture | measured |
|---|---|---|---|---|
| sem13 | `description ` (trailing space, no text): leg A hard-errored, legs B/C accepted empty | 19fe528 | `desc_empty_trailing_space.rxtin` | PASS (three-way accept) |
| sem14 | `description \| ` (trailing space): legs A/B accepted the literal `"\| "`, leg C refused | 19fe528, **b827cb7** (leg B's own half) | `desc_pipe_trailing_space.rxtin` | PASS (three-way refuse) |
| sem15 | a whitespace-only line raised in leg C (`line == ''` exact test) | 19fe528 | `whitespace_only_line.rxtin` | PASS (three-way accept/ignore) |
| sem16 | a directive before any `pattern` in a headless file: legs A/B refused, leg C silently dropped it | 19fe528 | `directive_before_pattern.rxtin` | PASS (three-way refuse) |
| sem17 | invalid UTF-8 crashed leg C (`UnicodeDecodeError`) | 19fe528 | synthesized at runtime in `run_rxtsource_tests.sh` (not committed — see below) | PASS (no crash) |
| sem19 | leg C validated `name`/`encoding` less strictly (no identifier check) | 19fe528 | `bad_name_ident.rxtin`, `bad_encoding_ident.rxtin` | PASS (three-way refuse, both) |
| sem20 | block `name` uniqueness enforced only by leg A, which `run.sh` never calls for a headless file (100% of the corpus) | 19fe528 | `dup_block_name.rxtin` | PASS (three-way refuse) |
| sem21 | `pcrec`/`lib`/`with`/`from`'s rest-of-line-vs-trimmed categorization didn't match the code | 19fe528 | `with_trailing_ws.rxtin` | PASS (leg A dump trims trailing ws, keeps internal spacing — the check's own first-draft expectation was wrong and was fixed in b827cb7) |
| sem23 | `--list-source` on a directory silently read as an empty file (EISDIR unchecked) | 19fe528 | (no fixture file — a directory is the input) | PASS (`stat`/`S_ISREG` refusal) |

### taken at discretion (cheap, low-risk)

| # | finding | commit | fixture | measured |
|---|---|---|---|---|
| sem11 | an indented `#` inside a `config` body got "'#' is not a config-block directive" instead of naming the real rule | 19fe528 | `indented_comment_in_config.rxtin` | PASS |
| sem12 | `budget steps=` accepted a leading `+`/space and silently clamped an overflow to `LONG_MAX` (`errno` never checked) | 19fe528 | `budget_overflow.rxtin` | PASS |

### ruled by the manager

| # | finding | commit | fixture | measured |
|---|---|---|---|---|
| sem10 | a blank line inside a `config` body silently ended it while a block scalar treated an interior blank as part of the value — the spec calls them "the same rule" | 34e52cc | `blank_ends_config_body.rxtin` | PASS (config body's own setting only; description after the blank is a separate FILE row; the seam still fires once) |

### left, with reasons (not fixtured)

| # | finding | why left |
|---|---|---|
| sem10 | *(ruled — see above; not left)* | |
| sem18 | a NUL byte silently truncates leg A's line split; bash cannot hold a NUL in a variable at all | no fix is cheaper than a different line-splitting scheme entirely, for a population the panel itself calls very-low-likelihood; documented as a known limitation, not silently ignored |
| sem22 | the `.rxt` dump's escape vocabulary is a stated SUBSET of the full subject-escape table (`"` unescaped, `\f`/`\v` round-trip via `\xNN`) | this is a documentation gap, not a code defect — nothing is wrong to detect; fixed with a clarifying paragraph in `docs/spec/rxt_format.md` instead of a fixture |

Left entirely at discretion per the brief (sem10/11/12/18/22): 10 was
ruled (above); 11 and 12 were taken anyway (cheap); 18 and 22 are
documentation-only, recorded above.

---

## (c) Stage B measurements

All run on the merged tree (`eda66d5`, `main` folded in — docs/journal/plan
only, no file overlap, clean auto-merge with no conflict markers).

1. **`git merge main`** — clean, `Merge made by the 'ort' strategy`, 3 files
   changed (`docs/dev/dev_journal.md`, `docs/dev/plan.md`,
   `tests/rxtsource/CLAUDE.md` — the last auto-merged with no conflict,
   verified by diff that both sides' additions are intact).
2. **`PROCS=4 make test-corpus`** — `cases passed: 26680`, `cases failed: 0`,
   `pattern-compile failures (distinct): 0`, `group cases pending-vm: 0`,
   `size-log rows: 2878`, `parallel: 178 of 178 file workers reported`.
   Matches the pinned expectation exactly. `docs/dev/artifact_size_log.tsv`
   (rewritten by the run's `SIZELOG` mechanism) reverted with
   `git checkout` per instruction.
3. **Sabotage row `S205`** (the escape index-vs-value re-plant), run
   solo via the matrix's `S205` selector:
   `reach:ok(1/1), rxtsource:1fail/77pass, corpus:0fail/26680pass` →
   **DETECTED**. The reach probe (leg B's clean `--dump` on the
   `ctrl_bytes` fixture) succeeds before the plant; after it, exactly
   ONE of `test-rxtsource`'s 78 checks goes red (the ctrl_bytes
   byte-for-byte check itself) and the whole corpus (`test-corpus`)
   stays fully green — the sabotage is latent on the real corpus by
   construction (0 patterns carry a non-TAB control byte), exactly as
   designed.
   **Control row `S203`** (`S-C12`, a pre-existing rxtsource row, chosen
   per the instruction), run solo the same way:
   `rxtsource:1fail/77pass, corpus:0fail/26680pass` → **DETECTED**,
   unchanged from its pre-lane behaviour — confirms the r46 fixtures and
   the ~35 new checks did not blunt an existing row (still exactly one
   check red, not more, not fewer).
4. **Final `PROCS=4 make test-rxtsource`** on the merged tree: **78
   passed / 0 failed**, exit 0. (`git status` after: clean except this
   report file — the run touches no tracked file.)
5. This report, committed.

### A note on the two real bugs Stage A's `make test-rxtsource` run found

The Phase 1 commit's own new checks caught two genuine gaps in the
Phase 1 code itself before Stage B ever ran make test-corpus or mech:

- `tests/harness/run.sh`'s block-level `description` arm still did an
  EXACT `"|"` string compare — sem14's fix had landed in
  `src/parse/rxt_source.c` and `tests/harness/verify_rxt.py` but was
  missed in `run.sh` itself. Caught by `head/desc-pipe-trailing-ws`'s
  three-way check (`check_refusal_all3`), which is exactly the point of
  checking all three legs rather than trusting a memory of "I fixed
  this".
- The `sem21` check's own first-draft expected value was wrong (`a,b`
  instead of `a, b`) — the CODE was already correct (`with`/`from` are
  AS WRITTEN except for trailing whitespace, so the internal space after
  the comma is kept). A reminder that a new check can be the thing that
  is wrong, not only the code it tests.

Both are recorded here rather than only in the commit log, because the
brief asks for "any NEW finding" — these are new findings about the
Phase 1 delivery's own completeness, not new r46 findings, and both are
fixed and verified green as of Stage A commit `b827cb7`.
