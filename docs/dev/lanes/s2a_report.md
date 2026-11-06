# s2a — span_pick stage 2, unit S2a: the noise channel and set FORMAT 2

Lane s2a (opus), kit manager's brief of 2026-11-06, kit request R-35. Branch `lane/memfn-s2a`, cut from
the design branch `lane/memfn-s2rev11` at e52cd716a. Design of record: `docs/design/memfn/span_cards.md`
rev 1.1, §4.1-§4.5, §5, §8.2 and §9's S2a row. Rulings read: reviews 2026-11-06 r4 and r5, R-35 in
`memfn/docs/requests.md`.

**BASE = 8f43f4f27**: main 6f1b40f75 merged into `lane/memfn-s2a` at e52cd716a, the lane's first act. Main
then moved by two plan.md-only commits (a601992cc, adb2d44b7), merged in at 988d6026a. No code moved, so
the identity base stays 8f43f4f27.

**ABI number taken: MF_SITE_ABI 23 -> 24.** `mf_measure` gains `noise_state` (`mf_noise_state`:
UNSTATED 0 refused, MEASURED, UNMEASURED) and `noise_e6`, each appended last. This is a layout move:
- MF_VOCAB and MF_CLASS_V do not move.
- PCREC_ARTIFACT_ABI does not move (no line naming it changed).
- No pcrec byte moves.

| Item | Outcome |
|---|---|
| Emitted bytes | none moved (identity spots below; full-corpus ident jobs 462-464 prepared) |
| pcrec abi / PCREC_ARTIFACT_ABI | unchanged |
| MF_SITE_ABI | 23 -> 24, with its history entry in `memfn/include/memfn.h` |
| docs/spec | `measures.md` hunks (format 2): §2.1¶1 `1` or `2`, ¶1a; §2.2¶1a, ¶3a; §3.3¶1 (format 1), ¶1a; §4¶2a; §6¶3a; §7 rows |
| grid1 (format 1) | digest 13a6536315af1520; listing, canonical and decoded views byte-identical to base |
| Sabotage | S2900-S2910, each planted red for §9's reason and reverted; S1232 re-aimed; S1234 red on a format-2 fixture |

## What changed, by file

Kit side:
- `memfn/include/memfn.h`
  - MF_SITE_ABI 24 and its history entry.
  - `mf_noise_state` and the two appended fields, with their comment.
- `memfn/src/compose.c`, `measures_check`
  - A MEASURED noise outside 0..MF_MEASURE_MAX is refused, never clamped.
  - An UNMEASURED row must carry noise 0.
  - UNSTATED or an unknown state is refused at `mf_art_begin`.
- `memfn/tests/g2/g2_gen.c`
  - An api block inside `refusal_table`, so it also runs under `--gate-only`.
  - 8 noise cases: 5 refused (zero-initialized/UNSTATED, state 3, MEASURED -1, MEASURED 10^15+1, UNMEASURED with noise 7) and 3 accepted.

pcrec side:
- `src/core/ks_measures.h`
  - The cells columns per format (7 for format 1; 8 for format 2, `events` after `round`).
  - `KS_MEAS_MAX` = 10^15.
  - `KsMeasRow.noise_e6` (appended) and `KsMeasSet.format`.
  - `pcrec_ks_meas_cell_w` and `pcrec_ks_meas_values2_role`.
- `src/core/ks_measures.c`
  - Format 1 and 2 accepted.
  - Format 2 parses `noise_e6`: `-`, or a non-negative integer in one spelling, at most 10^15, on measured rows only. Each refusal names its rule.
  - The `events` cell check.
  - The format-2 digest role, domain `pcrec-meas-2`: class+NUL, then per row key NUL unit status value LE noise LE (INT64_MIN for `-`). The format-1 role and its lines are byte-unchanged (the S1227/S1244 anchors hold).
  - The decoded view prints `noise_parsed` (format 2).
  - The canonical writer writes the noise text verbatim.
- `scripts/ksgen.c` and `src/core/measures_table.inc` (regenerated)
  - `noise_e6` is written positionally (`KS_MEAS_EMPTY` on every grid1 row).
  - `.format` is written.
  - The cells width is per format.
- `src/gen/memfn_sites.c`
  - The fill rule: measured iff `r->noise_e6 != KS_MEAS_EMPTY`. The loader holds EMPTY on every format-1 row, so the format rule lives in ONE place, the loader.
  - The MFMEAS trace record (`PCREC_CAND_TRACE` builds only) appends two columns: the MEASURED count, and an FNV-1a-64 over `key\tstate\tnoise_e6\n` in key order.
- `cli/main.c` (the harness reader) and `tests/memfn/arm_fixtures.c` state `MF_NOISE_UNMEASURED, 0`: the test levers hand UNMEASURED.

Tests:
- `tests/knowledge/ks_ref.py`: format 2, the format-2 digest, and `handed` (count and digest, MFMEAS's spelling).
- `tests/knowledge/mfixtures.py`
  - fx-f2, and fx-f1noise (format 1, numeric noise text on every row).
  - Six format-2 refusal fixtures, each redigested so its own rule is the only refusal.
  - The pairs fx-f2-noise and fx-f2-class.
  - A format-2 `store/` for ksgen.
- `tests/knowledge/meas_store_check.c`
  - The raw-row compare: every field, pre-parse vs fresh parse, noise included.
  - `-DMSC_TABLE` mode, for a ksgen fixture table.
  - `_Static_assert(KS_MEAS_MAX == MF_MEASURE_MAX)`.
- `tests/knowledge/run_measures_tests.sh`: builds ksgen from the tree over the format-2 fixture store; floors moved; 91 checks.
- `tests/compound/run_part_measures.sh`: new section (C), the MFMEAS noise witness against `ks_ref.py handed`; floor 16.
- `tests/mech/sabotages/`: S2900-S2910 (new) and S1232 (re-aimed).

Docs:
- `docs/spec/measures.md` (above).
- `docs/design/measure_sets.md`: `[s2]` revision line; §1.6's exclusions are format 1's; §4.1 noise handed from format 2.
- `docs/design/memfn/span_pick.md`: `[s2]` the bundle-noise seam field deferred to its producer (span_cards §4.6, §10.2).
- `memfn/docs/journal.md`: one line.
- CLAUDE.md lines: `memfn/include/`, `tests/knowledge/`, `tests/compound/`.

No `measures_dump.c` change was needed: the decoded view is `ks_measures.c`'s writer.

## Grep reader table (MF_SITE_ABI)

`git grep -n MF_SITE_ABI`, excluding history, lanes and reviews. Every code reader takes the SYMBOL, never
the number:
- `s->abi = MF_SITE_ABI` in `src/gen/memfn_sites.c`, `memfn/src/formhash.c`, `tests/memfn/{arm_fixtures,mass_check,proof_check,proven_check}.c` and `memfn/tests/g2/{g2_gen,g2_simd_gen,g2_win_gen}.c`;
- the runtime check in `memfn/src/compose.c`;
- G2's `MF_SITE_ABI ± 1` refusal cases.

Readers of the NUMBER:
- `memfn/include/memfn.h` (the define and the history), moved to 24;
- `memfn/include/CLAUDE.md`, moved to 24;
- the new S2a comments (compose.c, g2_gen.c, run_part_measures.sh, S2903).

Everything else that cites 23 is a dated journal, ledger or response line (records, not readers). No test
pins the number: G2 and the stamps read the symbol. `mf_measure`'s other readers are the two builders
(`memfn_sites.c`, `cli/main.c`) and `arm_fixtures.c`'s `fd_load_set`; all three state the new fields.
`docs/dev/lanes/r33_sim/probe.c` is a lane artifact, never built.

## Sabotage map and results (planted by hand on a `git archive HEAD` copy, reverted, reverts checked by cmp)

| row | id | file | plant | arm | red (planted) | reason seen |
|---|---|---|---|---|---|---|
| (a) | S2900 | ks_measures.c | format-2 fold skips noise (18 -> 10 bytes) | knowledge | 4 FAIL | fx-f2's declared digest (ks_ref.py) does not match C; pairs fx-f2-noise/-class refuse |
| (b) | S2901 | ks_measures.c | role-2 domain `pcrec-meas-1` | knowledge | 4 FAIL | every format-2 fixture's digest differs from ks_ref.py's |
| (c) | S2902 | memfn_sites.c | fill reads noise TEXT whatever the format | compound | 1 FAIL | fx-f1noise (C): handed `3 31a7...`, ks_ref `0 5e21...` |
| (d) | S2903 | compose.c | the kit accepts UNSTATED/unknown | g2gate | 2 FAIL | `api measure noise zero-initialized (UNSTATED)` and `state 3` expected refused |
| (e) | S2904 | memfn_sites.c | fill hands every row UNMEASURED | compound | 1 FAIL | fx-f2 (C): handed `0 a94e...`, ks_ref `2 a905...` |
| (f) | S2905 | memfn_sites.c | fill hands `abs_ns_e6` as noise | compound | 1 FAIL | fx-f2 (C): count equal (2), digest `5c87...` vs `a905...` |
| (g) | S2906 | ks_measures.c | canonical writer writes `-` noise as `0` (format 2) | knowledge | 4 FAIL | fx-f2 R1/R2/R3; its canonical view refuses ("a null row carries noise_e6 0") |
| (h) | S2907 | ks_measures.c | bound check removed | knowledge | 1 FAIL | `refuse f2-noise-bound: the set LOADED` |
| (r) | S2908 | scripts/ksgen.c | ksgen omits the noise field | knowledge | 1 FAIL | raw-row compare: `kit.enter.walk ... noise_e6 0/-9223372036854775808` on the format-2 fixture store |
| (s) | S2909 | ks_measures.c | format-2 digest skips `class` | knowledge | 4 FAIL | every format-2 fixture refuses (ks_ref.py folds class); fx-f2-class pair |
| (t) | S2910 | ks_measures.h | `KS_MEAS_MAX` 10^16 | knowledge (COMPILE-CATCH) | 3 FAIL | `meas_store_check.c:40: static assertion failed: "KS_MEAS_MAX ... MF_MEASURE_MAX"` |
| re-aim | S1232 | ks_measures.c | anchor moved to the per-format cells `put_tab` line | knowledge | 6 FAIL | grid1 R4 (canonical view differs from the committed file) |
| re-verify | S1234 | ks_measures.c | unchanged | knowledge | 16 FAIL | R5 on every format-1 fixture as before; every format-2 fixture refuses to load |

Notes on the table:
- (r) deviates from §9's wording. §9 says the compare reads 0 against EMPTY "on grid1's 68 rows". That holds only after `make gen-measures`, which the mech tree never runs (the committed `.inc` stays). The armed detector is therefore the format-2 FIXTURE store, which `run_measures_tests.sh` runs through a ksgen built from the sabotaged tree. The row header says so.
- (t) is declared `SAB_EXPECT=COMPILE-CATCH`, like S1242.
- The anchor tripwire (`scripts/m6read_check_sab_anchors.py`) reports: 1113 sabotages, all anchors resolve. That covers S1227, S1230, S1231, S1233, S1235, S1239 and S1244, re-read against the S2a code.
- `VALIDATE_ONLY=1` over the 71 mech rows: 71 definitions valid.

## Validation (light only; Linux dev box, 2026-11-06, outside 20:00-01:00)

| check | result |
|---|---|
| `make` | rc 0 |
| `make strict` | rc 0 ("whole tree compiles clean with -Werror -Wshadow") |
| `make test-codegen` | rc 0 (9/0 and 1/0) |
| `make test-knowledge` | rc 0, 303 passed / 0 failed (measures part 91/0) |
| `tests/compound/run_part_measures.sh` | PASS, 16/0 (fx-f2 `2 a9057c4ff546ae73`, fx-f1noise `0 5e21380e8e967a56`, each equal to `ks_ref.py handed`) |
| `make test-memfn-g2` | 70,358,660 checks passed, 0 failed, api fail 0 (run before the sabotage commits) |
| grid1 vs base | `--list-measurements`, `--view=canonical` (9562 B), `--view=decoded` (42457 B): byte-identical |
| emit_sweep identity vs 8f43f4f27 | see below |

The emit_sweep identity spots were bounded (`--limit 50`, under the lock cap), with the base frozen at `scratch/memfn/s2a/ref`. Every stream had movers=0 and asymmetric=0, with self-check clean:

| spot | sample | arms or streams |
|---|---|---|
| 1 | `--every 75` | every default stream (c-default, c-vm, emit-ir, facts, the four emit-ir-auto variants, stderr, composition, dumps) |
| 2 | `--every 37` | the same 22 stream/selfcheck lines |
| 3 | `--every 41` | `--measures=zen4-grid1@1`, C streams |
| 4 | `--every 43` | `--analysis=weblog`, C streams |

Two spots did not count:
- A `-eutf8` spot was mis-spelled: both sides refused all 50.
- A `--skip` spot was a usage error.

The full-corpus default sweep queued behind the box lock (it yielded to queue jobs 200 and 213-218, hours of work), so I stopped my own process with `scripts/safekill`. The full corpus over all 67 declared arms plus the two measures arms is jobs 462-464.

TT-9/K35: no new `tests/**/run_*.sh` was added. Both edited runners (`run_measures_tests.sh`, `run_part_measures.sh`) set `LC_ALL=C` and are listed in `tests/lib/san_excluded.txt`.

## Gate jobs (prepared, NOT queued)

`/var/tmp/pcrec-pcrec/scratch/memfn/s2a/jobs/` holds `common.sh`, `ident.sh`, `mech.sh` and nine jobs. Every `--dry-run` passes.

The chain runs 460 -> 461 -> 462/463/464 -> 465 -> 466/467/468:

| job | key | what it runs |
|---|---|---|
| 460 | kit-s2a-strict | `make strict` |
| 461 | kit-s2a-sections | test-knowledge, test-compound, test-memfn-g2, -arms, -stamps, -link, -manifest, -deleg, -rows, -finder, test-codegen, test-cli, test-findings, test-registry |
| 462-464 | kit-s2a-ident1/2/3 | 69 arms in 3 shards: the 67 `--list-ident-arms 8f43f4f27` arms plus `meas-grid1` and `an-weblog`; full corpus; ref = the frozen base build |
| 465 | kit-s2a-test | `make test` via perfrun |
| 466-468 | kit-s2a-mech/mech2/mech3 | 71 rows in shards of 24/24/23; expected trailer: unexpected 0, undetected 0, unreached 0, anomalies 0 |

The 71 mech rows are the union of four sets:
- `rows_for.sh` over the changed code and test files (56);
- every `knowledge` row;
- every `g2gate` row;
- every row read through `run_part_measures.sh` (S1291-S1295).

## Seam notes (observations only)

- The kit reads no noise yet. "No selection reads noise today" stays true. The channel is checked at `mf_art_begin` and witnessed by the MFMEAS record only.
- The format rule has ONE home, the loader: format-1 rows hold `KS_MEAS_EMPTY`. The fill reads only the parsed integer, never the text, so S2902's plant has to read the text column to go wrong.

## Design deviations

- (r)'s detector is the format-2 fixture store, not grid1's 68 rows (above). The §9 wording holds only after a regeneration that mech never runs.
- Neither is a deviation, but both are for main and the kit session:
  - The responses ledger entry (`memfn/docs/responses.md`, single writer) is the kit session's.
  - §10 items 2 and 3 (`[rev1.1 XREF]`) are main's.

## DELIVER file

`docs/dev/lanes/s2a_deliver.txt` is MISSING, both in this worktree and in the main tree. BOILERPLATE says the manager writes it; I did not create it. `scripts/lanecheck` therefore exits 65 (DELIVER missing), not DONE rc=0.

## Charter vs committed (§9's S2a row, §4, §5)

| charter item | committed |
|---|---|
| seam field and check (kit), §4.1 | yes: memfn.h, compose.c `measures_check` |
| format 2: noise | yes: ks_measures.c `noise_load`, the measures.md §2.2¶3a rules |
| format 2: `class` in the digest | yes: `meas_fold2`, measures.md §3.3¶1a |
| format 2: `events` cell column, `round med` | yes: the cells columns per format, events check, measures.md §2.2¶1a |
| the digest role (`pcrec-meas-2`), §5 | yes; format 1 unchanged (grid1 13a6536315af1520) |
| parse/write | yes; the canonical view writes the noise verbatim; R1-R5 green on fx-f2 |
| bound and status refusals | yes: 6 format-2 refusal fixtures, each held to its substring |
| `KS_MEAS_MAX` and its equality check | yes: ks_measures.h, `_Static_assert` in meas_store_check.c |
| fill (format rule; the handed filter; test levers UNMEASURED) | yes: memfn_sites.c, cli/main.c, arm_fixtures.c; §4¶2a |
| ksgen and the raw-row compare, §4.5 | yes |
| dump (the decoded view, §4.5) | yes: `noise_parsed` on format 2 (ks_measures.c's writer; no measures_dump.c change) |
| MFMEAS fields appended | yes: count + noise digest |
| spec hunks (§4.4) | yes: measures.md, all S2a items |
| design hunks (§4.4, §10.2) | yes: measure_sets.md §1.6 + §4.1 with an `[s2]` line; span_pick.md :237-238 |
| witness: emit_sweep byte-identical every arm vs base | PARTIAL here (bounded spots, 0 movers); full corpus is jobs 462-464, prepared |
| witness: grid1 views + digest identical | yes |
| witness: format-2 synthetic set round-trips canonically | yes (fx-f2 R1/R2/R3) |
| witness: ks_ref digest = C's on format-2 fixtures | yes (fx-f2 loads; pairs digest apart) |
| witness: MFMEAS under `--measures=FILE` format 2 / format-1 numeric noise | yes (run_part_measures (C)) |
| witness: `run_part_measures.sh` green | yes, 16/0 |
| witness: a kit test hands a zero-initialized row, refused | yes (G2 api block, also under `--gate-only`) |
| `[rev1.1 ANCHORS]` S1234 red on format 2; S1230-S1233/S1235/S1239 anchors re-read | yes (S1232 re-aimed) |
| sabotage (a)-(h), (r), (s), (t) | yes, S2900-S2910, all red then reverted |
| `make test` (normal, boxqueue) | prepared (465), not queued, per brief |

## STATE AT HANDOFF

STATE: done. OWED none: this lane queued nothing. Gate jobs 460-468 are prepared in
`/var/tmp/pcrec-pcrec/scratch/memfn/s2a/jobs/` for the kit manager to queue. The DELIVER file is missing
(above), so lanecheck cannot pass. Branch tip: the commit that adds this report.
