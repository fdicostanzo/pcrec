# covs2a — [COVER-CAP] stage 2, unit A (items A1-A7), build report

Lane covs2a (opus), branch `lane/covs2a`, cut from main `4456e9127`. Design of
record: `docs/design/cover_cap.md` §11 (rev 5.2). Build go: "Go on all stages"
(Frank, 2026-11-15). No abi bump (the joint landing's one event, §11.1).

## STATE AT HANDOFF

- STATE: done (A1-A7 built and committed; the cloud runs below are OWED).
- Head: the commit carrying this report (code head `fa1a4447b`; the report and
  evidence commit sits on top of it). Rulings file `covs2a_rulings.md`: empty
  at every checkpoint (last read 23:40 box clock, before this report); no
  ruling applied.
- Done: A1, A2, A3, A4, A5, A6, A7 (one WIP commit each, named by item), plus
  the pins they move (registry coverage 42 -> 44, cloud mech shard table) and
  the directory CLAUDE.md lines.
- Not done (by design, list B): every check past 32 (the `W` twins at
  n >= 33, the end-at-k answer rows, the proof-range rows, the test-axes arm,
  the compile-cost record), the seam assertion, the span writers' bounds,
  `limits.md` §3.12's lower-only `-D` sentence (B2's), the abi changelog
  entry (the joint landing's).
- Not run locally: the mech matrix for the changed rows. A local
  `run_sabotage_matrix.sh S1131 S3220 S3223 S3234` was refused by the
  session's permission classifier; the rows go to the cloud mech run (OWED
  RUNS). The REACH-only matrix over every kitproof-arm row did run (below).

Premise test (before any edit), all held: `make` on the fresh worktree rc 0;
`build/pcrec --features all --emit-facts --pattern 'a{600}(?:b|cc)'` cover row
`statement-fits|601|601|...`; `--list-limits` 81 data rows; `cc_fits` at
`src/gen/known.c:332-337` (exact); `run_cover.sh` `flags()` at `:40-46`
(exact).

## ITEMS A1-A7

- **A1** (`ff3fc028e`). `src/gen/known.h`: `MkEnd.k` is `uint16_t`, `MkEnd.set`
  is `const uint8_t (*)[32]` pointing at the cover record's arena sets
  (`PcrecCover.sets`). `src/gen/known.c` `cc_exact`: the copy and its READY-3
  internal error are deleted (two lines of fill remain). `req_run_in_cover`
  and `cover_window` read the pointer unchanged (same `e->set[d]` spelling).
  `tests/mech/sabotages/S1131_cover_c8_skipped.sh`: plant rewritten to the
  pointer fill. Check: route identity (below) and `test-kitproof` green;
  S1131 REACH reached.
- **A2** (`37f1dbacb`). `src/core/limits.def`: the row
  `PCREC_DEFAULT_WINDOW_SEARCH_WIDTH` = 32, `positions`, `selection knee`,
  `FLAG_D`, anchor `3.12`, desc as §11.2 (UNMEASURED label; one clause added:
  the legal range). Placed after `PCREC_ANCHORED_MAX_STATES`. Home header
  count `LIMITS_H (30)` corrected to 41 (it was 40 at main, stale).
  `src/core/limits.h`: the `#ifndef` wiring block and the range
  `_Static_assert` (§11.2's exact text); the "six rows below" comment now
  reads eight (three BUILD_D, five FLAG_D). `tests/registry/limits_check.sh`:
  manifest + count 81 -> 82, part 4(b)'s second bespoke lever with its own
  ok/bad pair (the header comment says "two"). Its failing direction was
  recorded before A3: with the row and no CLI flag, part 4 read two FAILs
  (`--window-search-width= is gone` and `... a stale claim`).
  `tests/codegen/run_anchored_match.sh` §4b passes
  `-DPCREC_DEFAULT_WINDOW_SEARCH_WIDTH=5` beside its ceiling 6 (no warning:
  §4b green, 22 checks); `tests/endmark/run_b3_checks.sh` `refbuild` passes
  `"${@:2}"` and §5's anchored build adds `=2` beside ceiling 3
  (`test-endmark` green, 46). `git grep -n -- '-DPCREC_ANCHORED_MAX_STATES='`
  finds no third reference build.
- **A3** (`8107a5389`). `lib/pcrec.h`: `int window_search_width;` after
  `vm_entry_shape` (0 = built-in default). `cli/main.c`: `--window-search-width=N`
  beside `--vm-entry-shape=`, `cli_int_value(a + 22, 1, PCREC_ANCHORED_MAX_STATES - 1)`,
  refusal text per §11.2.1. `src/core/compile.c`: range check after the
  part-layout check, `invalid window_search_width %d (1..%d, or 0 for the
  built-in default)`, returns -1. `src/gen/known.c`: `cover_width_limit()`
  (the option, else the default; one read) and `cc_fits` adds
  `k <= cover_width_limit(st->cx)` first. NOT stamped (manager ruling). Checks:
  CLI `=0`/`=4096` refused rc 1, `=4095` compiles; `[0-9a-f]{20}` reads
  `cover` by default, `statement-fits` (now `width-limit`) at `=16`, `cover`
  at `=20`; library: `tests/kitproof/width_opt.c` (8 checks, wired into
  `run_cover.sh` in A5): -1, 4096, 4097 refused with the message; 0, 1, 4095
  compile; `[0-9a-f]{24}` covers at 24 and not at 23.
- **A4** (`f288f4fb8`). `cover_conj[]`: C15 `width-limit`, kind `limit`; the
  table's header comment and the `kind` field comment updated ("retires like
  C2" removed). Readers: `docs/spec/facts_listing.md` §4.5¶2 (one word),
  `docs/design/kit_proof.md` C15 row, `tests/kitproof/cases.tsv` facts rows
  (`a{40}(?:b|cc)` MOVED to `a{600}(?:b|cc)` reading `width-limit|601|601|...`;
  `a{4095}` `width-limit|4095|4095|...`), S3220 REACH moved to
  `a{600}(?:b|cc)` / `[width-limit]`, S3223's `SAB_BEFORE`/`SAB_AFTER`
  re-anchored on the new return line. `known.c:349`'s error text went with
  A1. `predict.py`'s reading is A6's. `abi_changelog.md` keeps its spelling.
- **A5** (`62a228e5a`). `tests/kitproof/loader.sh` (new): the ONE reading of
  FLAGS/PATTERN, sourced by BOTH `run_cover.sh` and `reach.sh` (deviation:
  §11.6.2 has each reader carry its own map; one sourced file removes the
  copy that could drift, and the two readers can no longer disagree). `W` =
  `--window-search-width=<ceiling - 1>`; `@LD1`/`@LD`/`@D1`/`@D`; verdict
  `width=N`; fail-loud `--list-limits` read (missing/non-decimal row, or a
  width outside 1..ceiling-1 -> FAIL / `REACH-LIMITS-UNREAD`, never an empty
  substitution). Control recorded: a fake `pcrec` that drops the width row
  makes `run_cover.sh` print `FAIL: --list-limits:
  PCREC_DEFAULT_WINDOW_SEARCH_WIDTH is '', not a decimal` and
  `test-kitproof: FAIL`. `reach.sh` matches the RAW cases.tsv spelling in
  `--facts` mode and compiles the expanded one. `cases.tsv`: rows 32/33
  respelled `@LD`, `@LD1`, `[0-9a-f]{@D}`, `[0-9a-f]{@D1}`; the other
  literal-width verdict rows (24, 25, 40, 100, 1000 literal and class;
  `\b[0-9a-f]{32,40,100}\b`; `u \d{32}`) carry `width=N`; one `W` row
  (`[0-9a-f]{24}`, cover) shows the letter on this branch. The ten n >= 33
  `W` twins are B7 (they expect `cover` past the kit's 32). Floor 48 -> 49
  (net: +1 `W` row; the four @-rows replace four literal rows). Result:
  `kitproof: 49 verdicts, 19 facts, 105 answers (2160 cells)`, 185 passed,
  0 failed.
- **A6** (`93443fa6b`). `docs/dev/lanes/covs2a_evidence/predict.py`, a COPY
  (covs1's is untouched), with the three edits: (1) INTO = baseline why
  `statement-fits` and baseline `k <= D`; (2) expected-OUT = baseline `cover`
  with `k > D`, excluded from LOST unless the candidate's why is not C15; (3)
  both sides read from the two `--emit-facts` listings' `cover` sections (no
  trace builds). Usage `predict.py TREE REF_PCREC MOVERS OUT [--width D] [-j N]`;
  D read fail-loud from the candidate's `--list-limits`. Not handled: the
  lowered-cap sweep variants' `size-cap-retry` rows (said in its docstring;
  a combined-branch item).
- **A7** (`c610c8229`). S3223 re-aimed as the BYPASS row: header, DESC,
  `SAB_DOC_FIGURE`, REACH `[0-9a-f]{@D1}` expecting `REACH-DECLINE` /
  `[width-limit]`. New S3234 OFF BY ONE (`k <= cover_width_limit` ->
  `k <`), witness `[0-9a-f]{@D}` (REACH `REACH-COVER` / `[cover]`).
  `tests/ci/cloud_mech_shards.tsv`: S3234 added to shard 9 (ESTIMATE weight,
  like its neighbours). Also added: S3170 (shard 10) and S3198 (shard 11),
  which main `4456e9127` already DROPS (`cloud_mech_check.sh` reads them
  "DROPPED (in no shard)" on main's own tree), so the mech dispatch's
  population check passes; a full regeneration
  (`cloud_units_plan.py mech --measured ... --slots 30 --waves 3`) reshuffles
  ~1,800 lines and was reverted as out of scope. Check: `cloud_mech_check.sh
  tests/ci/cloud_mech_shards.tsv` PASS (90 shards, 1,308 ids once).
  REACH-only matrix over all 22 kitproof-arm rows: `mech-reach-only: DONE
  rc=0 rows=22 reached=22 unreached=0` at `c610c8229`.
- Also: `tests/registry/run_registry_tests.sh` limits coverage pin 42 -> 44
  (read from a run: the §3.12 [doc] check and the second [override-src]
  check), `test-registry` rc 0 after; `cli/CLAUDE.md`, `lib/CLAUDE.md`,
  `tests/kitproof/CLAUDE.md` lines; `cover_cap.md` §11.2.1 stamp row
  "MANAGER DECISION CLOSED 2026-11-15: not stamped".

## ROUTE IDENTITY

Command (box lock `covs2a-sweep`, main built from `git archive 4456e9127` in
lane scratch):

    python3 scripts/emit_sweep.py --ref 4456e9127 --ref-bin $S/main/build/pcrec \
      --tree worktrees/covs2a --bin worktrees/covs2a/build/pcrec --jobs 14 \
      --movers-out $S/movers.tsv \
      --dumps-declared-new=--list-limits:PCREC_DEFAULT_WINDOW_SEARCH_WIDTH

at code head `c610c8229` (A1-A7; the later commits touch no `src/`, `cli/`,
`lib/`). Self-check passed (all identical at full reach). REAL RUN, movers
per stream (population 7,071 corpus argv rows, 465 composition files):

| stream | reach (both ok) | movers |
|---|---:|---:|
| `.c` default engine | 6,497 | 0 |
| `.c` `--engine=vm` | 6,498 | 0 |
| `--emit-ir --engine=vm` | 6,522 | 0 |
| emit-ir-auto (4 arms) | 7,071 each | 0 |
| stderr + rc | 7,071 | 0 |
| composition | 38 (88 artifacts) | 0 |
| dumps | 7 | the one declared new `--list-limits` row |
| facts | 6,513 | 10 rows, 7 distinct patterns |

Every generated artifact is byte-identical to main's. The 10 facts movers
(`a{500}`, `a{200,500}`, `a{200,500}?`, `[ab]{1000}`, `a{50,60}` x3 rows,
`(?:ab|ba|aa|bb){24}c`, `(?:abc){20}` x2) differ ONLY by the A4 rename:
for each pattern, main's listing with `statement-fits` replaced by
`width-limit` equals the candidate's byte for byte (checked one by one). The
sweep's rc 1 is these declared-in-design listing moves (the `why` vocabulary
is advisory, facts_listing.md §4.5¶2, no abi). Evidence:
`covs2a_evidence/sweep_real_run.txt`, `sweep_movers.tsv`.

The prediction (A6's copy, artifact-stream movers only: the facts rows above
are the rename and are not route moves), `predict.py ... --width` from
`--list-limits` (D = 32): population 5,516 distinct patterns x 2 encodings;
census `statement-fits -> width-limit` 7 per encoding, 11,018 unchanged;
`predicted INTO=0 OUT=0 observed=0`; `lost=0 unexplained=0`; rc 0 — "no
artifact moves", as §11.1 predicts at 32. Controls on the same population:
`--width 64` gives INTO=3 (`(?:abc){20}`, `(?:ab|ba|aa|bb){24}c`,
`a{50,60}`) listed predicted-unmoved; `--width 24` gives OUT=2 (the 31- and
32-letter literals) and LOST=4 (rc 1: the candidate is built at 32, so they
stay covers), showing both new predicates reach their populations. Logs:
`covs2a_evidence/predict_D32.log`, `predict_D24_control.log`,
`predict_D64_control.log`.

## SPEC HUNKS

- `docs/spec/limits.md`: §3.12 (new) "The window search's width", ¶1-¶4
  (default, cliff with `[0-9a-f]{32}`/`{33}`, option and `-D`, legal range
  and both refusal texts, a lowered ceiling needs a lowered width, the
  size-cap cliff); its contents line; [0¶1] "§3.1-§3.12 and §8"; [8b¶1] "a
  knee with its own caller option is anchored where that option is
  documented (§3.12)".
- `docs/spec/tuning.md`: §2.56 (new) `--window-search-width=N`, ¶1-¶4
  (answer-identical, cliff, settable both ways and the deny, dial rule, no
  stamp of its own); its contents line; §2¶4 table row (bit —, default the
  row, answer-identical, `rx_info.flags` —, stamp `<PREFIX>_DFA_SCAN`); §4
  field table row; §2.43¶3d one clause pointing at §2.56.
- `docs/spec/match_api.md`: §8.2's `pcrec_options` listing gains the field;
  §6.3.4¶2's `"cover"` row gains "up to the window search's width
  (`tuning.md` §2.56)".
- `docs/spec/facts_listing.md` §4.5¶2: `statement-fits` -> `width-limit`.
- Not written here: `cli.md` (no hunk, §11.2.1); the abi changelog entry
  (the joint landing's).

## OWED RUNS

Dispatched as the lane's last act (owner `main`, `--ref lane/covs2a` at the
report commit), each verdict reaching main as CLOUD-DONE via queuewatch:

- `covs2a-test` — kind `test` (make test, sharded). Branch
  `cloud/main/test/covs2a-test`.
- `covs2a-recidentity` — kind `recidentity` (`make test-recursion-identity`).
  Branch `cloud/main/recidentity/covs2a-recidentity`.
- `covs2a-axes` — kind `axes` (test-axes; dispatched beside test per the
  brief, not after it).
- `covs2a-mech` — kind `mech` (the full matrix, the kitproof arm's S1131,
  S3220, S3223, S3234 included; the local run was refused, see STATE).

Read each with `scripts/cloudrun --verdict cloud/main/KIND/covs2a-KIND SHA`
or `scripts/cloudrun --list`; a mech red names its rows (re-check fixed rows
with `--kind mechrows --rows ...`). Local, green at `c610c8229`/`84acc096b`:
`make strict` (rc 0), `test-kitproof`, `test-registry`, `test-cli`,
`test-endmark`, `test-compound`, `test-doc-lint`, `test-spec-history`,
`tests/codegen/run_anchored_match.sh`, the REACH-only matrix (22/22).

## OPEN FOR THE COMBINED BRANCH

- B needs from this branch: `cover_width_limit()` and C15's first conjunct
  (`known.c`), `MkEnd` as a pointer (`known.h`; B3 writes the counted span
  from `e->set`, no copy bound left), the loader's `W` letter (B7's `W`
  twins and end-at-k rows go into `cases.tsv` as `W` rows), `predict.py`
  (covs2a_evidence) for the stage's sweep, S3223/S3234 as the bypass and
  off-by-one rows.
- `limits.md` §3.12 states the CURRENT `-D` rule ("a ceiling lowered to 32
  or below must lower this default too"); B2 adds the lower-only ceiling
  sentence (§11.2.1's spec row) when the seam assertion lands.
- The cover row's `desc` in `limits.def` and §3.12¶1 carry "not yet a
  measured choice"; step (6) of §11.6.1 replaces both.
- Stale or wrong in §11, found at this build:
  - `src/core/limits.def:156`'s home count read `LIMITS_H (30)` with 40 rows
    (now 41); §11 does not name it.
  - `tests/ci/cloud_mech_shards.tsv` at main drops S3170 and S3198
    (`cloud_mech_check.sh` red on main's own tree); patched minimally here;
    a measured regeneration is the table owner's.
  - `tests/registry/run_registry_tests.sh`'s limits coverage pin (42) is a
    reader of the registry's check count §11.1's reader list does not name
    (the learnings §3.y shape: a coverage guard on another file's output).
  - §11.6.2 "Each gets a `W` twin ... 10 rows" and the floors' "+10" are B7
    on the A branch (they expect `cover` past the kit's 32); this branch
    adds the one `W` row at 24, so the B floor is 49 + 10.
  - `tests/registry/limits_check.sh:58` still says "the six rows the token
    split concerns" (eight now; left, a comment in another arm's header).
  - `run_cover.sh` links `width_opt.c` against `build/libpcrec.a` even when
    `PCREC`/`PCREC_HARNESS` point at another build (an ASan run); harmless
    today, worth a `LIBPCREC` variable if a sanitizer arm runs kitproof.
- S3223's plant on THIS branch reddens through `cover_window`'s named
  internal error (k = 33 past the kit's 32: a failed harness compile on the
  `[0-9a-f]{@D1}` verdict row), as §11.6.3 says; on the combined branch it
  reddens as a cover past the default. Unmeasured here (cloud mech owed).
