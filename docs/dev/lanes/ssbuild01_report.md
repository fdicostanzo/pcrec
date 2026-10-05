# ssbuild01 — START-SET stages 0 and 1 (lane report)

Lane `ssbuild01`, 2026-10-05, opus. Branch `lane/ssbuild01` off main
`35c8ed45`. Builds `docs/design/startset.md` §8 stages 0 and 1 (rev 2 +
§6.4) under D148 + addenda 1-2. **Both stages are ZERO-MOVER and carry no abi
event**; §1-§2 hold the proof. Validation numbers are in §4; the full Mac
`make test` is OWED (§5).

## 0. Summary

| stage | what landed | movers / abi |
|---|---|---|
| 0 | K84 fixed: `DfaPf.scan` (`PfScan`), designated `dfa_pfs[]` rows, both `strcmp` readers test the field; `tests/codegen/run_cand_rows.sh` [cand-no-name-strcmp]; mech arm `candrows`; S495; S284 re-anchored | 0 movers on all five `emit_sweep` streams; no abi event |
| 1 | the `start_set` core fact (`src/facts/startset.c`, `--emit-facts` row, spec hunk); `DfaSel.route`/`.ss`, `DfaPf.routes`/`.emit_vm`, the routed first-match walk, [cand-route-init]/[cand-route-walk]; the FIND primitive `pcrec_emit_find`; `tests/startset/` (C-SS\*, NULLABLE ⇒ start_set.nullable, option witnesses; `make test-startset`, mech arm `startset`); S501/S502; S68 re-anchored; the census re-run with per-block options (`docs/design/startset/s1/`) and the stage-2/3 mover manifests (`tests/startset/manifests/`) | 0 movers (§4); no abi event |

## 1. Stage 0 — K84

- **The field.** `DfaPf` gained `PfScan scan` (`PF_SCAN_NONE`/`_OFS`/`_BYTE`/
  `_SET`), declared beside the emitter, for `reseeds`' own reason. The table
  moved to designated initializers so a later field (stage 1's `routes`,
  `emit_vm`) zero-fills without touching a row; every row names `.scan`.
- **The readers.** `dfa_cand_scan`: `pf->scan == PF_SCAN_BYTE` (was two
  `strcmp`s on `memchr`/`memchr-bounded`); `pcrec_dfa_cand_ppm`:
  `pf->scan != PF_SCAN_SET` (was two on `byte-class`/`-bounded`).
  `ofs_test_of` already read a property (`emit_block`), unchanged.
- **The check.** `tests/codegen/cand_rows_check.py` [cand-no-name-strcmp]:
  no comparison call under `src/ cli/ lib/` takes a `dfa_pfs[]` row name as a
  literal (names read off the table's text; `"none"` excepted as every axis's
  fallback word, with the receiver half covering `strcmp(pf->c.name,
  "none")`) or reads `c.name` through a `pf` receiver. Population: 9 row
  names, 240 comparison calls in 78 files. **Red on the branch point** (the
  four K84 sites, run against a `git archive 35c8ed45`), green on the fix.
- **Sabotage S495** (`pcrec_dfa_cand_ppm` re-reads the name): mech arm
  `candrows` (new word), DETECTED solo — `reach:ok(1/1),candrows:1fail/0pass`.
  Its stage-3 answer-level detector is the design's and does not exist yet.
- **S284 re-anchored** (the run rows' `reseeds` line); intent unchanged
  (`reseeds = false` on both run rows, count 2); expected verdict unchanged
  (UNDETECTED); the anchor tripwire resolves all 430 rows.
- **Gate:** `scripts/emit_sweep.py --ref 35c8ed45` (self-check PASSED, then the
  real run), **0 movers, 0 asymmetric on all five streams**; REACH default
  4,065 / vm 4,066 / `--emit-ir` 4,066 of 4,512 argv rows, composition 35
  producing files / 102 artifacts of 360, registry dumps 7 / 7.
- **Found, NOT fixed (out of the ruled scope):** the same shape on axis C —
  `emit_machine_tables` chooses the view tables by
  `strcmp(f->view->c.name, "end"/"eol")` (src/gen/emit_dfa.c). Latent like
  K84 was (a new `dfa_views` row with another name would emit the wrong
  tables). Recorded in K84's FIXED note for the manager to file or not.

## 2. Stage 1

### 2.1 The fact

`src/facts/startset.c` (`pcrec_start_set`), `facts.def` row `START_SET`
(E2, `PF_CORE`, no deny, owner the new file), the accessor
`pcrec_fact_start_set`, `StartSet { bits[32]; nullable; }` in `facts.h`, its
empty value (every byte, nullable) and its renderer.
- **On the LOWERED tree**, so it reads the compile's own `-i`, `--ucp`,
  encoding and per-block flags by construction (sound-F4); it takes no
  option.
- **Its `nullable` is the walk's own bit** — the ERASED language's
  (sound-F9) — and `nullable` ⇒ `start_set.nullable` is a check.
- The walk is startset.md §3.1's table, spines iterative (`A_CAT` and the
  `A_ALT` chain), `Ast.u.call.body` not followed, no `default:`.
- **Rendering (a deliberate refinement of §3.1's "`all` when nullable or
  full"):** `nullable` where the erased language can match empty, otherwise
  `<popcount>:<64 hex>` — a FULL non-nullable set renders as `256:ff…ff`, not
  `all`, so a reader can tell "no byte is necessary because nullable" from
  "every byte can start a match". `docs/spec/facts_listing.md` carries the
  spelling (D80).
- No pass reads it at stage 1 (`used no` on every listing).

### 2.2 The selection value and the walk (checks-F6)

- `DfaSel` gained `route` (`CandRoute`, `CAND_ROUTE_DFA = 0`) and
  `const StartSet *ss`; all 9 `DfaSel` initializers are designated and name
  `.route`.
- `DfaPf` gained `routes` (a `CAND_ON` mask; 0 is the legacy DFA-only row)
  and `emit_vm` (NULL on every row).
- `dfa_select` takes the mask's offset and asks `cand_routed` BEFORE
  `applies`; `DFA_SELECT_ROUTED` walks `dfa_pfs[]`, `DFA_SELECT` every other
  (DFA-only) list. No row serves the VM route.
- **Why the mask is on `DfaPf` and not on `DfaCand`:** a trailing `DfaCand`
  field would draw `-Wmissing-field-initializers` (on under `-Wextra`) on
  every positional row of the other nine axis lists, and only `dfa_pfs[]`
  has a second route.
- Checks: [cand-route-init] (every `DfaSel NAME = {…}` names `.route`; 9
  found) and [cand-route-walk] (`cand_routed(` precedes `->applies(` in
  `dfa_select`). **Both validated red** on a scratch copy with one `.route`
  removed and the route test moved after `applies` (2 FAIL).

### 2.3 The FIND primitive

`pcrec_emit_find(StrBuf *, const char *ind, const PcrecFind *)`
(`core/internal.h`): one line, a `memchr` for a BYTE row or a table loop
otherwise, parameterized by prefix, table tag, byte, position variable,
subject, length and holdback (the D11 bound). The four plain prefilter forms
call it through `pf_emit_find`, which takes the form off `DfaPf.scan`.
Byte-identical (§4). **Sabotage S68 re-anchored** onto its table line (intent
unchanged: the hot loop advances through `<prefix>_next_pos`; it now reaches
both byte-class forms, which share the line).

### 2.4 `tests/startset/` (`make test-startset`, in `TEST_SECTIONS`; mech arm `startset`)

Population (`startset_lib.corpus_blocks`): 258 `.rxt` files, 4,512 pattern
rows, 617 (text, options) duplicates, **3,895 blocks**, each compiled with
its own `flags`/`features`/`encoding`/`engine`/`tune`; 3,453 compile.

| check | reads | result at landing |
|---|---|---|
| [ss-ctrl] C-SS\* | the SHIPPED `start_set` row vs `Tdfa` (seeded) / emitted `can_begin_match` (unseeded), read off the emitted tables | **861 machines checked, 129 seeded, 0 violations**; unread counted: 341 no forward table (attempt engine et al.), 1,413 unseeded with no emitted table |
| [ss-null] | `nullable` ⇒ `start_set.nullable` | **3,453 blocks, 419 nullable, 0 violations** |
| [ss-flag] | 13 hand-written witnesses (`-i`, `--ucp` Latin-1 fold and its no-`--ucp` control, utf8 caseless with the KELVIN SIGN lead byte E2, a utf8 lead byte, lookbehind/`\b` erasure, the call/backreference/variable arms, a nullable pattern) | **13/13** |

Floors are half the landing population (D110: 1,700 blocks, 450 C-SS\* rows,
60 seeded, 200 nullable). ~20 s on the Mac. C-SS\*'s header carries ssedge's
correction: it is a WALK check and cannot certify a `T` (`Tdfa` is not a
sound floor, §6.4.3 item 2).

**Sabotage, the walk as the failing direction** (landed early with their
stage-1 detector; the design's stage-2/3 answer detectors join later):

| row | plant | mech verdict |
|---|---|---|
| S501 | `A_LOOK` read as consuming its body's first bytes (non-nullable) | DETECTED — `reach:ok(1/1),startset:2fail/1pass` |
| S502 | `A_CAT` drops `null(l) ? F(r)` | DETECTED — `reach:ok(1/1),startset:2fail/1pass` |

### 2.5 The census re-run with per-block options (sound-F4) and the manifests

`docs/design/startset/s1/census_s1.py` (~30 s), outputs committed
(`census_s1.tsv`, `census_s1_summary.txt`). It reads the BUILT fact, the
checks' own population, and the DFA hat's `T = S ∩ E*` off the emitted tables.

| count | bench | corpus |
|---|---|---|
| population | 345 | 3,895 |
| auto refused | 24 | 442 |
| **V at auto (stage-2 movers)** | **17** | **164** (100 of them blocks that pin `--engine` themselves; 64 do not) |
| **V under `--engine=vm`** | **274** | **2,547** |
| DFA scan, seeded | 30 | 144 |
| **F admitted (stage-3 movers)** | **18** | **32** |
| F admitted with `T == S` (the build assertion) | 18 | 32 |
| F-checked seeded machines with `\|E*\| == 256` | 21 of 21 | 101 of 101 |

Against r3/rev 2 (the design's §1): bench matches exactly (17 / 18; 274
against 273 under forced VM). Corpus moves because the population is now
(text, options) blocks rather than distinct texts at `--features all`: V at
auto 164 (64 without an engine pin, against r3's 59), F 32 against rev 2's
38. `T == S` and `|E*| == 256` hold on every row they are asked of, as §4.1a
measured.

Manifests (`tests/startset/manifests/`, checks-F5): `manifest_s2_vm_auto.tsv`
(181 rows), `manifest_s2_vm_forced.tsv` (2,821), `manifest_s3_dfa.tsv` (50).
Regenerating the census MOVES the check that reads them; each header says so.

### 2.6 ssedge's corrections (§6.4.3)

Nothing built at stage 1 states the old argument. startset.md now carries
build annotations at §4.1's invariant (steps 1-3 superseded by item 2's
argument; the re-seed must be CONDITIONAL, item 1 — both bind stage 3),
§4.1a's "`Tdfa` alone would also be sound" (refuted, item 2) and §6.3's S485
("answer-invisible" withdrawn, item 1).

### 2.7 D149

No tuning constant was introduced. The test floors are DERIVED (half the
landing population, D110) and labelled where they live.

## 3. Files

src: `src/facts/startset.c` (new), `facts.def`, `facts.h`, `facts.c`,
`facts_derive.h`, `src/gen/emit_dfa.c`, `src/core/internal.h`.
tests: `tests/codegen/cand_rows_check.py` + `run_cand_rows.sh` (new),
`tests/startset/` (new: checks, lib, manifests, CLAUDE.md),
`tests/mech/run_sabotage_matrix.sh` (arms `candrows`, `startset`),
`tests/mech/sabotages/S495`, `S501`, `S502` (new), `S68`, `S284`
(re-anchored). Makefile: `run_cand_rows.sh` in `test-codegen`'s group;
`test-startset` section. docs: `docs/spec/facts_listing.md` (D80),
`docs/dev/known_issues.md` (K84 FIXED), `docs/dev/plan.md` (STATE),
`docs/design/startset.md` (build annotations), `docs/design/startset/s1/`
(new), CLAUDE.md in `src/facts`, `src/gen`, `tests`, `tests/codegen`,
`tests/mech`, `tests/startset`, `docs/design/startset`, `docs/dev/lanes`.

## 4. Validation (stage 1)

VALIDATION_PLACEHOLDER

## 5. Owed

- **Full Mac `make test`** — armed detached as this lane's last act;
  OWED_PLACEHOLDER
- Stage 2 (the VM hat) is next; its manifest is `manifest_s2_vm_*.tsv`.

## 6. For the manager

- Axis C's `strcmp` on `dfa_views` row names (§1): file it or not.
- The `start_set` rendering refinement (§2.1): `nullable` / `N:hex`, not
  `all`.
- S495, S501 and S502 landed at stage 0/1 on structural detectors; their
  answer-level detectors are the design's and join at stages 2/3.
