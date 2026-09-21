# lane adm0921 — [ADMIN-0921]: four owed small items

Branch `lane/adm0921`, tip `70a298f0` (five commits: one per item, plus
one fix-up on item 4 caught by broader validation). Never merged to
main; the manager's darwin gate + full `make test` review is owed there.

## Item 1 — delete the four dead exports (D114)

`pcrec_emit_abi_types` (`src/gen/emit_dfa.c`), `pcrec_nfa_has_asserts`
(`src/ir/nfa.c`), `pcrec_rxt_schema_opens_group` (`src/parse/rxt_schema.c`),
`pcrec_rxt_source_ncols` (`src/parse/rxt_source.c`) — grepped `\b<sym>\b`
over `src cli lib tests tools docs scripts` for each; every hit outside
the definition/declaration/header-comment pair was a historical,
already-past-tense mention (tour4_report.md's own table, decisions.md's
D114, prior lane reports) that needed no edit. Deleted each definition,
its header comment, and its `internal.h` declaration. `emit_dfa.c`'s
`emit_rx_abi_types` (the static function `pcrec_emit_abi_types` wrapped)
is still called directly at two other sites and stays.

Two neighbouring banner comments referenced the deleted
`pcrec_rxt_schema_opens_group` by name and were corrected in place
(`rxt_schema.c`'s "three structure-layer parameters" block and its
`internal.h` mirror) rather than left pointing at nothing.

`nm -g build/libpcrec.a | grep -c ' T '`: **262 -> 258, exactly -4.**

**D104's export count (295) is already stale, and not because of this
lane.** Grepped for "295" and found it cited once, in decisions.md's
D104 STATUS entry from 2026-09-17. The export count at THIS lane's
branch point, before any of these four deletions, was already 262 —
33 short of 295, from unrelated waves in between. Re-pinning a
pre-existing drift is outside this charter's four items; flagged here
rather than silently fixed or silently ignored.

## Item 2 — regenerate tools/review's censuses

Regenerated all five `tools/review/*.py` scripts at this lane's HEAD
(after item 1), not only `function_census.py` — `tools/review/CLAUDE.md`'s
own practice has always regenerated the set together at a wave boundary,
and the drift was real across all of them:

| script | before | after |
|---|---|---|
| function_census | 917 rows | 935 rows |
| clone_candidates | 278 member rows (274 groups... 81 now) | 295 member rows, 81 groups |
| literal_census | 12,652 literals / 5,136 distinct | 12,712 / 5,157 |
| include_graph | 207 includes / 0 back-edges | 208 / 0 |
| churn_hotspots | 55 files | 55 files (scores shift) |

The three files the plan row's own charter named as stale
(`emit_vm.c`/`select_engine.c`/`parse.c`) confirmed real: `emit_vm.c`
124->142 functions, `select_engine.c` 8->10, `parse.c` 43->45 in the
function census alone.

**No "export" column exists in any of the five TSVs' schemas** — none
of the five scripts tracks caller/export status at all. Read the plan
row's "census/export columns stale" phrasing as the same staleness the
row counts and per-file spans already demonstrate.

## Item 3 — S154's live witness (tour2's owed item)

tour2_report.md left this owed: its own live-verification attempt for
S154 (`vm_cost` charging `|W|` trail entries per call instead of `2*|W|`)
used `^(a(?1)?b)$` over a^n b^n, the row's own documented bisection
witness — but that call target reaches itself, so `cost.unbounded` stays
true and `trail_frames` falls back to the fixed `RX_TRAIL_FRAMES` 3072
bring-up default at every `n` tried, before the `2*|W|`-vs-`|W|` sizing
difference could show through. Both the clean and sabotaged builds
answered `frames` at n=200 in tour2's own transcript.

Built two scratch trees from `git archive HEAD` (clean, and sabotaged via
`tests/mech/lib/replace.py` applying the row's own `SAB_BEFORE`/`SAB_AFTER`),
then swept subroutine-call patterns for one whose target is **not**
self-recursive, so `cost.unbounded` stays false and `trail_frames` is
COMPUTED from the real charge instead of defaulted. Found a minimal
witness: `(a)(?1)` over subject `"aa"`.

| build | stamped `RX_TRAIL_FRAMES` | result on `"aa"` |
|---|---|---|
| clean | 13 | `match 0 2` (agrees with libpcre2 10.48-Homebrew: `0: aa` / `1: a`) |
| sabotaged | 10 | `PCREC_ERR_FRAMES` ("frames") |

Recorded in the row's own `SAB_DOC_FIGURE` so the next re-verification
does not have to rediscover it. `VALIDATE_ONLY=1` field check passed
before committing; re-ran the row solo through the real driver
afterward (tree `30a4c19172c5a385afcc1dac3ce3511f7f5441a6`, the item-2
commit):

    S154-call-trail-undercharged  harness recursion codegen
    corpus:522fail/1168pass,recdiff:98fail/6pass,codegen:1fail/108pass
    DETECTED
    == mech run COMPLETE: 1 rows (unexpected: 0, undetected: 0,
       unreached: 0, anomalies: 0, oracle-skipped: 0) ==

The row's own automated detector (`run_recursion_diff.sh` SS2's
bisection) is unchanged; this witness is the small, non-bisecting live
match differential tour2 left owed, not a replacement for it.

## Item 4 — close K62

`cls_peek_past_dash` (the dash-vs-literal lookahead inside a character
class) recognised only the four-byte `\Q\E` spelling of an empty quote;
`cls_skip` (which actually consumes it) was already transparent to a
bare `\E` too. So `[0-\E]` saw a live backslash after the dash,
committed to a RANGE, and the class's own closing `]` was consumed as
the high endpoint — "missing terminating ]" on a legal two-member class
`{0,-}`.

Fixed per memory `pcrec-general-mechanisms-not-special-cases`: one
shared helper, `cls_dissolve_len(cx, pos, in_quote)` — "how many bytes
at `pos` are a dissolving quote marker with nothing between its open
and its close" (2 for a bare `\E`, always; 4 for `\Q\E`, only when
`!in_quote`) — called by both `cls_skip` (mutating, passes its live
`cx->in_quote`) and `cls_peek_past_dash` (a non-mutating lookahead,
always passes `false` since its walk never opens a real content-bearing
quote).

**A fix-up was needed.** The first cut of the helper ignored `in_quote`
entirely and dissolved a `\Q\E` sequence unconditionally. That broke
nested `\Q` inside an already-open quote: `tests/quoting/d27/charclass.rxt`'s
`[\Qa\Q\E]` cells (a quote opened once, `a`, then a SECOND `\Q` that is
really the two literal bytes `\` and `Q` followed by the real closing
`\E`) went from matching `\` and `Q` to `nomatch` on both — caught by
running the FULL `tests/quoting/` + `tests/classes/` harness rather than
trusting the narrow new pin file alone (184/186 passed, not 186/186).
Fixed by gating the four-byte dissolution on `!in_quote`.

Oracle-verified against local libpcre2 10.48-Homebrew (this box's own
copy, not the 10.46 reference) and pinned in
`tests/quoting/k62_class_range_e.rxt` — outside the D27-blinded `d27/`
corpus, since this is an implementation-authored regression pin, not a
blinded-author test:

| pattern | members |
|---|---|
| `[0-\E]` | `{0,-}` |
| `[a-\E]` | `{a,-}` |
| `[0-\E9]` | `0-9` (range) |
| `[0-\Q\E]` | `{0,-}` (the pre-existing spelling, kept as the fix's own control) |
| `[0-\E` | still refuses (unterminated class) |

Grepped `tests/reject/` and the rest of `tests/` for any pin of the OLD
(wrong) refusal of `[0-\E]`-shaped patterns — none found, so nothing
needed re-pinning in the other direction.

K62 closed in `docs/dev/known_issues.md`.

## Validation (whole delivery, at `70a298f0`)

| step | result |
|---|---|
| `make -j4 CC=gcc-16` | clean, throughout (after every commit) |
| `make strict CC=gcc-16` | clean ("whole tree compiles clean with -Werror -Wshadow"), throughout |
| `bash tests/harness/run.sh tests/quoting/ tests/classes/` | **186/186 cases pass** (184/186 before the item-4 fix-up) |
| `python3 tests/harness/verify_rxt.py tests/quoting/` | **PASS=8 FAIL=0**, all quoting-specific cells correctly skipped as no-python-expression |
| `python3 scripts/m6read_check_sab_anchors.py` | **270 rows / 286 anchor sites, all resolve** |
| `python3 scripts/emit_sweep.py --ref 476892de` | self-check PASSED at full reach; real run **0 movers on all 5 streams** — see table below |
| `make test-codegen CC=gcc-16` | **65 checks passed, 0 failed; `run_group` 9/10 scripts passed** — sole red `run_inline_capability.sh` ("nm could not read arm_a.o (no rx_search symbol)"), the standing pre-existing darwin probe multiple prior lanes (tour2, tour4) have confirmed unrelated to their own changes; not re-confirmed against a fresh branch-point scratch build here (already well-documented as pre-existing and structurally unrelated to a parser/census/sabotage-doc lane) |
| `make test-registry CC=gcc-16` | **620/620 checks passed** across its five sub-checks (225+209+108+24+54), 0 failures |

**emit_sweep detail** (`--ref 476892de`, self-check first):

| stream | population | both_ok (reach) | both_refuse | movers | asymmetric |
|---|---|---|---|---|---|
| c-default | 3944 | 3520 | 424→422 (real) | 0 | 0 (self) / 2 (real) |
| c-vm | 3944 | 3521 | 423→421 (real) | 0 | 0 (self) / 2 (real) |
| emit-ir-vm | 3944 | 3521 | 423→421 (real) | 0 | 0 (self) / 2 (real) |
| composition | 306 | 33 | 273 | 0 | 0 |
| dumps | 7 | 7 | 0 | 0 | 0 |

The self-check (ref vs. an independent second rebuild of the same ref)
is all-identical at full reach. The real run's only asymmetry, on all
three argv streams, is the two new K62 test patterns themselves
(`[0-\E]`, `[a-\E]` — refused at the branch point, compile now): the
fix's own intended effect landing on a brand-new test file, not a
corpus regression. `DELIVER witness: OK`. Elapsed 259.9s. Log:
`/private/tmp/claude-501/-Users-fdicostanzo-pcrec/54162df9-163f-49c9-877d-215048b45714/scratchpad/emit_sweep.log`.

`make test-codegen` log:
`/private/tmp/claude-501/-Users-fdicostanzo-pcrec/54162df9-163f-49c9-877d-215048b45714/scratchpad/test_codegen.log`.
`make test-registry` log:
`/private/tmp/claude-501/-Users-fdicostanzo-pcrec/54162df9-163f-49c9-877d-215048b45714/scratchpad/test_registry.log`.

## Files touched

- `src/gen/emit_dfa.c`, `src/ir/nfa.c`, `src/parse/rxt_schema.c`,
  `src/parse/rxt_source.c`, `src/core/internal.h` — item 1 deletions.
- `tools/review/out/*.tsv` (8 files) — item 2 regeneration.
- `tests/mech/sabotages/S154_call_trail_undercharged.sh` — item 3's
  `SAB_DOC_FIGURE` update (the plant itself unchanged).
- `src/parse/parse.c` — item 4: new `cls_dissolve_len`, `cls_skip` and
  `cls_peek_past_dash` rewritten to share it.
- `docs/dev/known_issues.md` — K62 closed.
- `tests/quoting/k62_class_range_e.rxt` (new), `tests/quoting/CLAUDE.md`
  — item 4's regression pin and its directory listing entry.
- `docs/dev/plan.md` — the `[ADMIN-0921]` row, this delivery block.

## What is OWED

- **`make test` — launched in the BACKGROUND as this lane's last act,
  per DO-THEN-FINISH.** Numbers OWED. Log:
  `worktrees/adm0921/build/adm0921_test.log`. Completion line to grep:
  `checks failed:`. A fresh agent or the manager should read that log
  once it completes and fold the numbers into this report or the
  manager's own merge notes.
- The manager's own darwin gate at merge (per every other lane's
  delivery bar in this tree).
- D104's stale "295" export-count citation in decisions.md — flagged
  under item 1 above, not fixed (out of this charter's four items).
