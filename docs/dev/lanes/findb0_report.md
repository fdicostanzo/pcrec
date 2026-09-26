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
| `analysis` in an `include "path"` fragment (any depth) refused at the ENTRY naming the fragment's file:line (r2 M-B3) | `fragment_check` + `parse_file(…, chain, …)` |
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
fragment refusal two links deep. Fixtures: `analysis_bundle_accept.rxtin`,
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
- **`make test` (full) is OWED and QUEUED — NOT run** (heavy slot booked).

## Findings / choices for the manager

1. **Fragment mechanism.** pcrec never opened a fragment before, and
   format_design §2.5's "a fragment holds pattern blocks and `include`
   lines only" is enforced by NO leg (`include_head.rxtin`'s fragment
   `common.rxt` carries a file-level `description`). B0 adds a fragment-mode
   SUB-PARSE per include (cycle-guarded) that propagates ONLY the
   `analysis` refusal; other fragment failures stay leg B's `[resolution]`
   (spec rule 3 unchanged). The general §2.5 rule is a separate row if wanted.
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
