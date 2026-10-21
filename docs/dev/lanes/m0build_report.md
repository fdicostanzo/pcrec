# Lane m0build — [MEASURE-SET] M0 (2026-10-21, opus)

Branch `lane/m0build` from main `f2dae53f9`. Builds step M0 of
`docs/design/measure_sets.md` rev 3 (§R3, §R2, §10.1's M0 row, §3.4-§3.6,
§4, §9, §10.5) under Frank's build go of 2026-10-21, with the K112 rider.
ONE abi event, 81 -> 82 (the brief's ruling: "If M0 builds first, M0 is the
bump"). Rulings file `m0build_rulings.md`: no entries at any checkpoint.

## 1. Commits

| commit | what |
|---|---|
| `82082ab48` | WIP 1: section-TSV reader (ksrc part 1), the measures kind row (`src/core/ks_measures.{c,h}`), the store and loading (`src/core/measures.c`, `measures_{store,table}.inc`, `make gen-measures`, ksgen's `measures` arm, `embed_text.sh` `EMBED_KIND`), `--measures` / the `measures` config line / fill-only, `<PREFIX>_MEASURES` + `rx_info.measures`, `--list-measurements` (`src/dump/measures_dump.c`), abi 82 with its readers, K112's two role strings, `measure_store/` with `zen4-grid1@1` |
| `9e4b87e90` | WIP 2: `docs/spec/measures.md` (new, numbered) + hunks in cli.md, rxt_format.md, match_api.md; `tests/knowledge/run_measures_tests.sh` (70 checks), `ks_ref.py`, `mfixtures.py`, `meas_store_check.c`; the deps check (a')/(b'); sabotage S1227-S1246 |
| `9dcc0617c` | WIP 3: the mover census tool, K112 FIXED, directory CLAUDE.md entries, plan status, FILEPIN self-pin |
| (this commit) | the report, src/gen/CLAUDE.md, the lanes index line |

The lane's last `src/` commit is `9e4b87e90`; `run_recursion_identity.sh`'s
FILEPIN is self-pinned to it. The manager re-pins to the merge.

## 2. What M0 delivers, against the brief

| brief item | state |
|---|---|
| MEASURES kind row: validator, canonical + decoded writers, store, R1-R5 | built; R1-R5 in `run_measures_tests.sh` (R3/R5 against `ks_ref.py`, written from the spec alone) |
| `measure_store/` with ONE set (zen4-grid1 scratch) | built; `zen4-grid1@1`, 68 rows, digest `13a6536315af1520`, sha256 `d332967c…` |
| loading: `--measures`, `measures` config line, fill-only | built (fill-only through `pcrec_ks_pick`; a `pcrec` raw line carrying `--measures` is refused) |
| ABI event: `<PREFIX>_MEASURES` ("" when nothing asked) + `rx_info.measures`, abi 81 -> 82, readers by grep | built; §3 |
| suites that count (registry, codegen, rxtsource) | NOT run yet; they run inside the queued `make test` (§7) |
| bare compile reads the LATEST set | built: `measure_store/DEFAULTS` `idk -> zen4-grid1@1`; a bare compile resolves the `idk` default |
| mover census per the MOVERS rule | tool built, smoke 0/80; full run QUEUED (§4) |
| K112 rider | fixed; `known_issues.md` K112 FIXED; S1243 |

The envelope default is M2, as the brief says; not built.

## 3. abi readers (grep, at 9dcc0617c)

Moved to 82 (hits of `\b82\b` per file):

| file | hits | reader |
|---|---|---|
| `src/gen/emit_dfa.c` | 1 | `#define PCREC_ARTIFACT_ABI 82` |
| `tests/codegen/run_codegen_tests.sh` | 2 | `ABI_EXPECT=82` + its message |
| `tests/mech/sabotages/S693_abi_not_bumped.sh` | 2 | BEFORE 82 / AFTER 81 |
| `docs/spec/match_api.md` | 5 | §1¶7 (it read `!= 80`, stale since 81; fixed), the §6 table's abi row, ¶17, the §8.2 struct quotation, the §6.3.2 inventory |
| `docs/dev/history/abi_changelog.md` | 1 | new top entry (82); the prior entry now says "was 81" |
| `tests/codegen/run_recursion_identity.sh` | 2 | the FILEPIN self-pin and its comment |

Byte-count reader (cites no abi digit, moves anyway): `tests/codegen/manifests/m5_stage1_stamps.tsv`, `EMITTED_BYTES` +193 per row (the member's two comment lines + declaration, the `#define`, the initializer), re-recorded with a comment in `run_cpset_structure.sh`.

Left at 81 (records of past events, grep `abi[ =:]*81\b|abi 80 -> 81`): `docs/design/CLAUDE.md` 1, `docs/design/ctx_span.md` 1, `docs/design/memfn/r17b_prime.md` 1, `docs/dev/plan.md` 2 (one is this row's "81 -> 82"), `src/gen/CLAUDE.md` 2 (the P2c section), `tests/mech/CLAUDE.md` 1, `tests/startset/CLAUDE.md` 1, `memfn/docs/journal.md` 1, `memfn/docs/responses.md` 1. `memfn/docs/wake.md` is the kit's file; the kit should know main is at 82 after the merge.

## 4. Mover census

`docs/dev/lanes/m0build/census.py`: the branch point's compiler
(`build/m0ref/base`, built from `f2dae53f9`) against the lane's, over every
distinct corpus pattern (4,636, from 5,811 corpus rows by
`scripts/emit_sweep.py`'s enumeration) on five arms (the `.c` at default,
`-e utf8`, `--engine=vm`; `--emit-ir --engine=vm`; `--emit-facts=byte,utf8`),
46,360 compiles. The new side loses exactly the declared scaffolding (the
member's three lines, `#define RX_MEASURES ""`, `.measures = "",`, a
`""`-valued facts row for the stamp, the abi digits in four places, K112's
two strings); a `MEASURES` line with any other value is NOT removed, so a
consulted set is a mover. rc and stderr are compared (the size warning's
byte counts masked).

Smoke: 8 patterns x 5 arms = 80 compiles, 0 movers. The full run is queued
(§7); it also writes `measure_store/movers/0001.tsv`, DEFAULTS transition 1
(`none -> zen4-grid1@1:13a6536315af1520`, class `idk`), which
`DEFAULTS.log` row 1 already names. **That file is OWED**: a fresh agent
commits it after reading the census verdict (expected header-only, movers
0). Expected 0 movers: no kit row reads a set key before B4, so no
selection can read the set, and the stamp is `""` everywhere.

Earlier light evidence: the registry dumps differ only in `--list-schema`
(+1 `measures` row, 75 -> 76 schema rows; rxtsource reads the count
dynamically); one artifact diffed by hand moves only the abi digits, the
three member lines, the `#define` and the initializer.

## 5. Sabotage rows (S1227-S1246)

The design's §8.5 proposed ids, renumbered into the brief's range; new rows
fill the rest. Suites: `knowledge` unless noted.

| new | design id | plants |
|---|---|---|
| S1227 | S943 | the values digest skips row 0 |
| S1228 | S946 | a config's `measures` beats `--measures` (fill-only broken) |
| S1229 | S947 | the default table names the wrong class |
| S1230 | S958 | the probe ignores the header id |
| S1231 | S985 | the S2 mismatch falls through instead of refusing |
| S1232 | S961 | the canonical writer drops `cells` |
| S1233 | S962 | the loader accepts a derived view |
| S1234 | S983 | a symmetric column swap in BOTH writers (`SAB_FILE2`); only R5 sees it (hand-planted: 5 failures, 3 of them R5) |
| S1235 | new | two unit codes collide |
| S1236 | new | the section-TSV field count goes unchecked (`src/core/ksrc.c`) |
| S1237 | S988 | the store's shadow rule keyed on id alone |
| S1238 | new | a shadowing set with other values loads |
| S1239 | new | rows left unsorted |
| S1240 | new | `rx_info.measures` differs from the stamp (`emit_dfa.c`) |
| S1241 | new | the embedded text short by one byte (`measures_store.inc`) |
| S1242 | new | `ks_measures.c` includes an internal header (suite `core`, `ksrc_deps_check.sh`; the plant hand-verified as detected) |
| S1243 | new | K112's stale role string put back (suite `irlisting`) |
| S1244 | new | the digest domain without its NUL |
| S1245 | new | `--measures` reaches a registry query |
| S1246 | new | a `pcrec` raw line carries `--measures` |

S693 (`codegen`) re-pinned BEFORE 82 / AFTER 81. Field validation: 31 of 31
valid (the 21 above + 10 re-run rows). Every solo verdict is OWED (§7).

Not built, with the reason:
- design S945 (the stamp's consulted-OR dropped): UNREACHED by construction
  until a kit row consults a set key (B4); a plant has nothing to drop.
- design S944, S948-S951, S953-S957, S959, S960, S987: they need
  `make test-measures`' recompute, the answers / staleness / envelope views
  or `pcrec-measure`, all after M0 (M1/M2).

Re-run rows queued with the new ones (their detectors or files moved):
S961, S962, S984 (knowledge arm, now also running the measures section),
S986, S989, S1049, S1050, S963 (`src/core/ksrc.c`), S313 (fill-only in
`cli/main.c`), S258 (the `--emit-ir` role text, K112). The file-level set
`tests/mech/rows_for.sh` gives for every changed file is ~300 rows
(`emit_dfa.c`, `cli/main.c`, `internal.h` are touched); the anchor
tripwire resolves all 867 rows (898 sites), so per D69 the rest are not
re-run here. The manager may add them as one more job.

## 6. Deviations and open points

1. **Loading built at M0.** The design puts `--measures` and the config
   line at M1; the brief asked for them at M0, so they are here.
2. **Not built**: `make test-measures` (recompute), the `answers`,
   `staleness` and `readers` views, `emit_sweep.py --data measures`. The
   transition-1 movers file comes from `census.py` (base vs lane), because a
   same-binary "no set" side does not exist at M0. M1 builds the data mode
   and `make test-measures-census`.
3. **`ratio-complement`** is added to the derivation registry (the store
   set's rows needed it); `measures.md` §3.2 lists it.
4. **No byte cap on a set FILE read** (`-I` / FILE references): unbounded
   like the analysis kind's. Worth a limits.def row if a hostile file ever
   matters.
5. **Failed attempts**: the kit's `consulted` is ORed only from attempts
   that reached `mf_art_end`; an attempt that refuses before it contributes
   nothing. Today nothing consults, so this is unobservable.
6. **The decoded view's field names** are a separate table from the
   reader's (`row_fields[]`), so R5's independent reader is not checking a
   copy of the reader's own names.
7. **Wording edits outside the lane's files**: the design's §R-MS5 line and
   `memfn/docs/requests.md` line 471 were reworded to "(§8.2, by
   `make test-measures`)" because the citation check read the old text as a
   dangling `measures.md` citation. The kit owns requests.md; please tell
   the kit.
8. **The `members` section's columns** (`member unit_key unit_abs_ns_e6
   box`) are this lane's; the design names the section only.
9. **`-` vs empty** in a cell are kept as TEXT; only `value_e6` treats
   empty as null.
10. **The non-empty stamp path is UNREACHED**: no consulting reader exists
    until the kit's B4. The stamp is `""` on every artifact; S1240 holds the
    mirror, and the consulted path is covered only by the harness override.
11. **The kit's interim/synthetic sets** (status `synthetic`, first-letter
    digests) are not valid under the spec. `measure_store/from_interim.py`
    re-derived `zen4-grid1@1` under the spec's code table. For the kit.
12. **No `--help` lines** for `--measures` / `--list-measurements`:
    `usage()` has none for `--analysis` either; [IFACE-PUSH] is the place.
13. **make test shape**: the job uses `scripts/perfrun --shape 4,2` (the
    brief's 8-core cap), not the rotation's pick.
14. **Job priority 300**: ahead of the kit's pending 521 (M0 gates the kit's
    B4). Rename to reorder.

## 7. STATE AT HANDOFF

Light, during the build (all green): `make`, `make strict`,
`make test-knowledge` (282 checks, 0 failed), `make test-spec-history`
(0 failed), `make test-plan-lint` (184 rows, 0 violations), the deps check
with its plant, `scripts/m6read_check_sab_anchors.py` (867 rows, all
anchors resolve) and census smoke 0/80. The registry, codegen and
rxtsource suites were NOT run on their own; they run inside the queued
`make test`.

Queued (`scripts/boxqueue`, owner m0build, no lift gate; job scripts in
`worktrees/m0build/build/m0scratch/jobs/`; read each with
`scripts/verdict LOG` and `scripts/boxqueue status`):

| job | log | completion line | expect |
|---|---|---|---|
| `300-m0build-test` | `worktrees/m0build/build/m0scratch/test.log` (+ `.perfrun`) | `sections ran: 73/73` | sections=73 |
| `301-m0build-census` | the job's BQ log; table `build/m0scratch/census_full.tsv`; `measure_store/movers/0001.tsv` | `== m0 census COMPLETE: patterns=4636 compiles=46360 movers=0` | patterns=4636 |
| `302-m0build-mech` | the job's BQ log (`run_sabotage_matrix.sh`) | `== mech run COMPLETE: 31 ...` | rows=31 |

OWED to a fresh agent once they end: read the three verdicts; if the census
reads 0 movers, commit `measure_store/movers/0001.tsv`; fill §4's and §5's
verdicts here; triage any red. Last rulings entry applied: none (the file
holds no entries).
