# fdb1 — R17-b′ step B1: the facts, the query and the table, unrouted

Lane fdb1 (opus), 2026-10-16, for the memfn kit manager. Branch `lane/fdb1`
from `lane/memfn-fd` @ 608dc8b44 (abi 78, `MF_SITE_ABI` 11). Design:
`docs/design/memfn/r17b_prime.md` rev 3 §3.1 (row B1), §3.4 (B1 rows), §4.5,
§8.3. Box: Linux dev box, every heavy run `taskset -c 12-15`, `-j4`.

**Verdict: B1 BUILT; ZERO ARTIFACT MOVERS on every arm; NO pcrec abi event;
`MF_SITE_ABI` 11 → 12.** Stream 5 moves by exactly the declared five
`--list-axes` rows. Three light reds found by the chain were fixed after it
(§3); their full sections (registry, G2 quick) are OWED a re-run.

## 1. Built, item → file

| item (§3.1 B1) | where |
|---|---|
| `mf_site.body` (ONESHOT from every builder) + START hook (R-19) | `memfn/include/memfn.h`; `memfn/src/{fields.def,gate.c,compose.c}`; `src/gen/memfn_sites.{c,h}`, `src/gen/emit_dfa.c` (`find_hooks`, `req_site_define`, `PCREC_MF_ORIGIN`) |
| `mf_ask` (pure; class not form) + `mf_class`; define-time re-ask under MF_TRACE | `memfn.h`, `compose.c` (`ask_sel`, `kit_class`, `define_sel`) |
| trace-build READER SHADOW (G1, R4, L4 from row AND from `mf_ask`) | `src/gen/emit_dfa.c` `cand_ask_*`, `cand_shadow_*` (PCREC_CAND_TRACE only) |
| declared read list + undeclared-read / cycle trap (D4) | `CandNode.kask`/`kfields` (inside `reads`), self-check `table-ask-unread`, trap `undeclared-ask` |
| `mf_measures` on `mf_art_begin`, `consulted` from `mf_art_end` (R-MS1/2) | `memfn.h`, `compose.c` (`measures_check`) |
| `mf_analysis` declared, NULL-tolerant, read by no row (E-1) | `memfn.h` (window_contract §3.1 types) |
| `mf_form_hash` (R-MS3) | `memfn/src/formhash.c` |
| reader declarations (R-MS4 keys) / listing | `memfn/src/finder.c` `mf_finder_rows` (caller-owned `mf_finder_listing`) |
| method cards `kit-grid@1` (R-MS5) | `memfn/data/cards/` |
| E3: `fd_rows[]` as `kit_table` (19 rows), `routed` 0, trace-only shadow | `memfn/src/finder.c` (+ `terms.c`, R17-b's cover search ported, search only) |
| `measures=` lever + synthetic sets + COMMITTED predicted-mover manifest | `cli/main.c` (`--harness=measures=`), `memfn/data/sets/` (+`generate.py`), `docs/design/memfn/r17b_prime/fdb1/predicted_movers_B4.tsv` |
| `fd` rows in rows.tsv / row_floors.tsv (`pending-site:<step>`) | `tests/memfn/{rows.tsv,row_floors.tsv,rows_check.py,run_rows.sh}` |
| table self-check (C2) | `tests/memfn/finder_check.py` A (+ B-J), `make test-memfn-finder` |
| five deny rows, floor 6 → 11 | `memfn/src/options.def`; `docs/spec/registry.md` §6¶8a/¶8b; `scripts/emit_sweep.py` DIFFER_PINS/ASSERT_ZERO |
| stream-5 delta DECLARED | `docs/design/memfn/r17b_prime/fdb1/{dumps_declared_B1.tsv,dumps_delta.py}` |
| trace compare (new `fd` records only) | `.../fdb1/trace_delta.py` |
| sabotage S917 S919 S921 S1018 S1019 S1020 S1025; arm `memfnfinder` | `tests/mech/sabotages/`, `tests/mech/run_sabotage_matrix.sh`; S743/S844 re-aimed |

`MF_SITE_ABI` readers by grep: `memfn/include/memfn.h` (value + log),
`memfn/include/CLAUDE.md` (the "carries" sentence), `compose.c`'s `s->abi`
check, G2's `g2_gen.c` (reads the macro). Other `MF_SITE_ABI 11` mentions are
historical ("introduced at 11"). Note: R17-b's record branch also took 12; it
renumbers when B4 ports it (R-13's precedent).

## 2. Evidence (logs under `worktrees/fdb1/build/land/`, verdicts `verdict.txt`)

Chain `build/land/chain.sh` at tip 3190c23aa (later commits docs + three
check fixes, no `src/`/`memfn/src` change).

| run | result |
|---|---|
| make -j4, make strict | rc 0, rc 0 |
| test-memfn-finder / arms / rows / forms / deleg / stamps / guarded / simdfloor / rank / manifest / reach / arch | all rc 0 (868 / 383 / 226 / 5 / 5 / 25 / 10 / 51 / 15 / 11 / 4 / 15 passed) |
| test-rxtsource, test-cand-oracle, test-ci-shards, test-codegen | rc 0 (298, 100, 9, codegen green) |
| test-memfn-link | rc 2 (C16: a PROVENANCE row for `data/`) → FIXED, re-run 8/0 |
| test-registry | rc 2 (limits_check: `CAND_ASKF_*` enum values) → FIXED (NON-LIMIT allowlist), limits_check re-run 37/0; full section OWED |
| test-memfn-g2 (quick) | 52,987,690 passed, 1 failed: (b) "rows never chosen" listed the 19 `fd` rows (shadow, by design) → FIXED (`rows_zero` exempts table `fd`); re-run OWED |
| dumps_delta.py | 7 surfaces, 5 declared rows arrived, 0 failures |
| trace_delta.py (every 2, 3 arms) | 6,936 compiles, 5,401 carry new records (211,144 filtered as declared), 0 differ outside the declaration |
| sweep plain / simd (with floor) / comments / utf8 | rc 0, 0 movers every stream (dumps run separately above) |
| sweep start | rc 1: 0 movers; the only failures are the ten new `--memfn=no-fd-*` cells, which the REFERENCE refuses (it predates the rows: refusal 4244/0, 4257/0); the working side reads differ 0 = the ASSERT_ZERO claim. Instrument property of a new deny, not a mover |
| sweep vm | rc 1: 0 movers; composition floor 86 < 100 both sides (known) |
| sweep variants | rc 1: 0 movers on 85 cell-streams; the 40 identical TAG FLOOR lines (known, main's pins) |
| sweep trace | rc 1: 0 movers on c-default/c-vm, SET gate clean; the one nonzero line is stream 5 (dumps) `movers=1` = the declared `--list-axes` delta (dumps_delta.py above) |
| reader census (`reader_census_B1.tsv`) | 4,624 patterns × 4 arms, 240,967 MFASK, 0 CANDORACLE aborts |
| predicted-mover manifest (interim set) | 2,369 set sites ≥ 2 members, 817 (arm, pattern) movers; byte 285 (r1e0c0) + 15 (r0e1c1) = §3.5's prediction |
| hand sample vs ref608 | 60 compiles, 0 diffs |

Sabotage, each solo (`build/land/mech/*.log`): S917 memfnfinder 4fail,
S919 1fail, S1018 13fail, S1020 1fail, S1025 10fail, S921 memfnarms 73fail,
S1019 candoracle 27fail — all DETECTED.

## 3. Findings

- F-B1-2 the eps `<regime>` token is unspelled; chose `kit.eps.findall.l64k`
  (F1 A/A p90) because F3's floor moves the (2,0,0) cover against §3.5. Logged
  in `memfn/docs/finder_history.md`.
- F-B1-3 ATTEMPT arm: MLINE's context stop — the class proves no offset-0
  byte while G1/R4 read predecessor `\n` (466 records default); recorded, not
  asserted. B2's switch must handle it (D1c).
- F-B1-4 `mf_ask` answers the define phase; `mf_emit` fixtures compare only
  exists/proven0.
- F-B1-6 the `gstar` card's dims differ from R5's template.
- `fields.def` class space is FULL at 64 (next class needs a wider mask).
- derivation `ratio-complement` is not in measure_sets' registry.
- R8 basis corrected MEASURED → DERIVED (logged).
- pcrec's scan is slot NEXT where the design names FIRST (kask on NEXT).
- LINER keys at W16/W32 carry no layer token (S1 vs A1).
- kind-dependent rows cannot hold at B1 (kind unstated), so the manifest covers
  ≥ 2-member set sites only; pay operand keys PROVISIONAL; OFS arms outside the
  class vocabulary; the harness lever is not forwarded to compound parts.
- emit_sweep's start arms cannot compare a NEW deny against a reference that
  lacks it (§2); an ASSERT_ZERO cell for a new row needs a one-sided mode.
- `formhash.c` mallocs its scratch arena (listing entry, never a compile).

## 4. OWED

| item | owner | trigger |
|---|---|---|
| re-run `make test-registry` and `make test-memfn-g2` after the §2 fixes | kit manager's slot | next slot |
| full `make test`, mech derived rows, G2 full, N2 census | kit manager | merge slot |
| emit_sweep one-sided ASSERT_ZERO mode for new denies | main / sweeparm owner | next new deny |
| B2's handling of F-B1-3 | B2 lane | B2 |
| pay-rule operand spellings | grid2 prep (kit-grid@2) | grid2 |

## 5. Charter vs committed (§3.1 B1)

All B1 items in §1's table: COMMITTED. No `--emit-facts` section (per A9).
E3b not built (not this lane's). Zero artifact movers: met. Stream 5:
declared, checked. No PCREC abi event.
