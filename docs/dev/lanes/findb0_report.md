# findb0 — [FINDINGS] B0, the `.rxt` FORMAT rows

Lane `findb0`, 2026-09-26, branch `lane/findb0` from main `27a63314`.
Design: `lane/findr3:docs/design/findings/design.md` §3.1 and §13 B0 (r3
text, unmerged), review `docs/dev/reviews/2026-09-25-r2-findings-design.md`.
Parse + `--list-schema` + `--list-source` only; nothing is consumed and no
emitted byte moves (no abi event).

## What landed

| item | where |
|---|---|
| FILE `analysis <name>` opens a BUNDLE (TOKEN, REPEAT, `unique-by value`); lowercase `[a-z][a-z0-9_-]*` by name | `rxt_schema.def`, `rxt_source.c` (`analysis_name_check`) |
| FILE `freq <name>` WITHDRAWN (no row; refuses as unknown token) | `rxt_schema.def` |
| new scope `bundle`: `include <name>` (AT_MOST_ONE, search spelling, lowercase), `description` (prose), `freq` (NONE → DATA, AT_MOST_ONE) | `rxt_schema.def`, `internal.h` (`RXT_SCOPE_BUNDLE`, `RXT_CH_BUNDLE`), `rxt_schema.c` renderings |
| DATA `encoding` (ONE, required, `closed data-encoding ascii utf8 latin1 bytes`) | `rxt_schema.def` |
| DATA `serves <query> when <enc,…> via <derivation>` (REPEAT, required, `unique-by first-word`); closed query/derivation vocabulary as one data table; derivation must match the block's kind and answer the query; encodings from the ONE encoding registry (`pcrec_enc_by_name`) | `serves_check`, `rxt_find_derivations` |
| bundle-level (query, enc) collision = parse error naming the first line (r2 M-B1); claim table on the BUNDLE frame | `serves_check` |
| DATA `row` key grammar per kind (`freq`: `row HH N`), lowercase hex, strictly ascending, canonical nonzero count | `row_check`, `rxt_find_row_keys` |
| CONFIG `analysis` → TOKEN, AT_MOST_ONE, lowercase name | `rxt_schema.def`, CONFIG arm |
| `--analysis`/`--analysis=` in a config's `pcrec` line refused (r2 M-B2) | `pcrec_raw_analysis_check` (splits like the CLI's `raw_split`) |
| format_design §2.5's GENERAL fragment rule (manager ruling, round 2): a fragment holds pattern blocks + `include` only; ANY other file-level line in a fragment (any depth) — `analysis` included (r2 M-B3) — refused at the ENTRY naming the fragment's file:line; only this refusal propagates | `fragment_check` + `parse_file(…, chain, …)`, one predicate at the wave-check site |
| PROVENANCE: `bytes`/`sha256` required-if `parent == data and source != authored`; `url`/`ref` required-if `parent == block and source != authored` (§0.10); conjunctive condition clause ` and ` | `rxt_schema.def`, `cond_holds` |
| `--list-source`: new main-table kind `analysis` (name = bundle, value = its `include <x>` as written); a bundle's include is never a head `include` row; a kind block's provenance reports its bundle as block_line/block_name | `RXT_DECL_ANALYSIS`, `kind_name` |
| cardinality `one` now refused at the line (pre-existing gap: a 2nd `question` was silently dropped) | the cardinality site |

Structure layer: file → bundle → freq → provenance (third nesting level)
works with no frame-stack change — asserted by the accept fixture.

## Spec (D80)

`docs/spec/rxt_format.md`: head table (`analysis` row replaces `freq`; the
STALE `lib` row rewritten — contents read since W1.3), config-keys
paragraph (`analysis <name>` names ONE bundle; `pcrec`-line refusal), the
provenance table/per-parent text, new section "`analysis` — the bundle"
(replacing "`freq` — the data block"), `--list-schema` scope list +
`and` clause, `--list-source` kind/name/value rows + the bundle-include
sentence. `cli.md`/`table_contract.md` untouched (B2's hunks); no other
spec reader of the changed rows found by grep.

## Tests

`tests/rxtsource/run_rxtsource_tests.sh` section `[FINDINGS] B0`: accept
fixture asserted on dump rows; 34 refusal cases (class tag + rule needle,
floor 34); controls (exemplar with bytes/sha256, non-`--analysis` pcrec
word, a fragment broken for another reason must NOT fail the entry);
fragment refusal two links deep, and the general class (`fragment_head_line.rxtin`, a `description` in a fragment). Fixtures: `analysis_bundle_accept.rxtin`,
`analysis_in_fragment.rxtin`, `analysis_frag_{mid,leaf}.rxtfrag`.
`verify_rxt.py`'s head-word list: `freq` → `analysis`. W23-S4 kind list
gains `analysis`.

Sabotage: S290 (the ` and ` conjunction reads only its first conjunct),
S291 (the fragment refusal swallowed). S292 unused. S248 RE-ANCHORED (its
anchor row, CONFIG `analysis`, changed; intent re-verified: still inserts
a `testee` row after it). The design names no B0 sabotage row.

## Validation (this box, darwin, gcc-16)

- `make strict`: EXIT 0.
- `make test-rxtsource`: EXIT 0 — 254 passed, 0 failed (40 `findings/B0` passes).
- `make test-parse`: EXIT 0.
- `make test-registry`: EXIT 0 (sections 226/210/123/29/54 passed, 0 failed).
- mech (`run_sabotage_matrix.sh`, one row each, at 963f5047): S248
  DETECTED (reach ok, rxtsource 1 fail/253), S290 DETECTED (reach ok, 8
  fail/245), S291 DETECTED (reach ok, 1 fail/253); unexpected/undetected/
  unreached/anomalies all 0. Logs: `/tmp/fb0/mech_S2{48,90,91}.log`.
- ROUND 2 (after the general fragment rule, at 6c55725a): `make strict`
  EXIT 0; `make test-rxtsource` EXIT 0, 255 passed / 0 failed; mech S291
  DETECTED (reach ok, rxtsource 2 fail/253 — both fragment cells), S290
  DETECTED (8 fail/246); 0 anomalies. test-parse/test-registry not re-run
  (no parse or registry surface moved in round 2).
- **`make test` (full) is OWED and QUEUED — NOT run** (heavy slot booked).

## Findings / choices for the manager

1. **Fragment mechanism (round 2, per the manager's ruling).** pcrec
   never opened a fragment before, and format_design §2.5's "a fragment
   holds pattern blocks and `include` lines only" was enforced by NO leg.
   The sub-parse now enforces the GENERAL rule (one predicate: in fragment
   mode, any FILE-scope line other than `include` is a schema-constraint
   refusal) and propagates only that refusal; other fragment failures stay
   leg B's `[resolution]` (spec rule 3 unchanged). The predicate replaced
   the analysis-only arm at equal size. IN-TREE POPULATION, counted first
   (every `include "` line under tests/, examples/, docs/): 7 distinct
   targets in tests/ (5 fixture fragments, 2 scratch in
   run_rxtsource_tests.sh, plus `common.rxt`); ONE violator —
   `include_head.rxtin` included the LIBRARY `common.rxt` (file-level
   `description`), re-pointed at `include_basic_frag.rxtfrag`. examples/:
   none. docs/: four illustrative `include` lines in
   `docs/design/dd13_format/format_design.md` (:6750-6751, :6933) and
   `usecases_and_outline.md` (:452), whose targets do not exist in the tree;
   two of them (:6933, :452) describe including an analyzer-emitted
   `freq` exemplar file, which §2.5 itself already forbade and the findings
   design supersedes (a bundle, found by `-I`). Design history, not a
   user-copyable file — flagged, not edited. The broken-fragment control's
   fragment now fails on an unknown block directive (a `lib` line would
   now be the rule's own refusal).
2. **Collision population is empty at B0** (one kind ⇒ one block per
   bundle). Reachable input: a duplicated encoding on one `serves` line.
   B5 owes the two-block fixture.
3. **Buffer/no-filesystem parse mode** is B1's (§13), not built here.
4. **Not checked at B0 (B1's, with its limit rows):** count ≤
   `PCREC_MAX_FIND_COUNT`, all-zero/empty block, bundle size.
5. **Spelling choices (manager's, DD-13b memory):** `wave` 23 on all new
   rows (a new wave 24 would bump `PCREC_RXT_WAVE_BUILT`); `include` value
   shape TOKEN (no new `angle-name` shape — grammar is the production's, as
   `lib`'s is); row keys LOWERCASE hex only; explicit `0` count and leading
   zeros refused; scope name `bundle`, diagnostic noun "bundle"; the
   fragment/pcrec-line refusals tagged `[schema-constraint]`, name/grammar
   ones `[value-shape]`; no length cap on analysis names (B2's `-I` probe
   may want one).
6. `docs/dev/plan.md`'s [FINDINGS] row not edited (manager's).

## Rebase onto main (2026-09-26)

`lane/findb0` (tip `6ef8c7f5`) rebased onto main `0bb87eda` ([OPT-LITSCAN]
S1 steps 1-5, abi 36) at the team lead's request. New tip `2b29b150`.

**One conflict, in `docs/dev/lanes/CLAUDE.md`**: an adjacent-bullet
collision between this row's own "findb0: lane report" commit and two
bullets s1build/findb3 had appended to the same list (main tip's
`findb3_report.md`/`s1build_report.md` entries). Resolved by keeping both
— the findb0 bullet appended after them, content unchanged from either
side.

**Every other area the brief flagged as an expected conflict site turned
out disjoint, not merely auto-mergeable**: findb0 never touches
`tests/mech/CLAUDE.md` (S290/S291 are catalogued in
`tests/rxtsource/CLAUDE.md`'s own "[FINDINGS] B0" section instead, which
main's S279-S289 section did not touch), and its `tests/rxtsource/
run_rxtsource_tests.sh` hunks are two self-contained additions (one kinds-
string edit at the pre-existing W23-S4 arm, one new `[FINDINGS] B0`
section appended at the file's end) — B0's fixtures are all `.rxtin`/head-
scoped, so **none of them move `CENSUS_FILES`/`CENSUS_BLOCKS`/`CENSUS_LINES`
or `RUNSH_*`**, and nothing needed re-deriving there. No conflict in
`docs/spec/rxt_format.md`, `docs/dev/plan.md`, or any mech/cpset/resource
manifest.

**`docs/dev/plan.md`'s [FINDINGS] row was missing B0's delivery note**
(item 6 above deliberately left it for the manager) — added here, a
bolded sentence parallel to the existing B3 one, naming the lane, the
mechanism, the tests and the validation, and pointing back at this report.

### Validation (this box, darwin, gcc-16, tree `2b29b150`)

- `make -j4 CC=gcc-16`: clean build, no warnings.
- `make strict CC=gcc-16`: `strict: whole tree compiles clean with -Werror -Wshadow`.
- `bash tests/rxtsource/run_rxtsource_tests.sh`: **255 passed / 0 failed** (1 recorded), census re-derived at run time and holds: `rxtsource: INV-COMPAT holds over 220 files / 4016 blocks / 29224 expectation lines`.
- `make test-parse CC=gcc-16`: **9 passed / 0 failed**.
- `make test-registry CC=gcc-16`: **0 failed** across all five sub-checks (226/210/123/29/54-shaped sections; `[DD-11.3]` option-matrix self-oracle PASS, `definitions-oracle` 354 cells / 101,244+101,244 comparisons / 0 disagreements).
- mech, each row run SOLO via `bash tests/mech/run_sabotage_matrix.sh S<id>` at tree `2b29b150`:
  - **S248**: `reach:ok(1/1),rxtsource:1fail/254pass` — **DETECTED**.
  - **S290**: `reach:ok(1/1),rxtsource:8fail/246pass` — **DETECTED**.
  - **S291**: `reach:ok(1/1),rxtsource:2fail/253pass` — **DETECTED**.
  - All three: unexpected/undetected/unreached/anomalies all 0. Matches the lane's own round-2 figures exactly (S290 8fail/246, S291 2fail/253) — the rebase moved no answer.
- `make test`, `test-codegen`, `test-mrl`, `test-axes`, etc.: **NOT run** per the brief (another lane using the box; the manager schedules the full battery).

Not merged; `git -C /Users/fdicostanzo/pcrec worktree` still shows
`worktrees/findb0` on `lane/findb0` at `2b29b150`.
