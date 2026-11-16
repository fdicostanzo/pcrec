# covs2c — [COVER-CAP] stage 2, unit 1: pcrec's remaining statement code and its rows

Lane covs2c (opus), 2026-11-16, for the manager. Branch `lane/covs2c`, cut from
`lane/covs2b` df4d38bdb. Build go: the owner, 2026-11-16 ~17:30 box clock,
"Cover-build-go: go" (quoted in the brief). Ids: W* and C* are
`docs/dev/lanes/r45read_report.md`'s, P* are `r45chk_report.md`'s, r27 is
`docs/dev/reviews/2026-11-16-r27-memfn-span4k.md`.

## STATE AT HANDOFF

- STATE: done for items (1)-(3); item (4) (r27 READ-3) STOPPED by the brief's
  stop rule (the fix is not local; facts and options under LEFT OPEN).
- No default emitted byte moved: `scripts/emit_sweep.py --no-self-check`,
  df4d38bdb's binary vs this branch's (1f13610cf's code), every stream 0
  movers, 0 asymmetric (7,071 argv rows, 465 composition files; log in lane
  scratch `$PCREC_TMPDIR/scratch/covs2c/sweep.txt`). No abi move.
- RULINGS FILE `docs/dev/lanes/covs2c_rulings.md`: EMPTY at every read (last
  read before this report, 18:46 box clock).
- OWED (cloud, dispatched as this lane's last act, verdicts reach main as
  CLOUD-DONE): `covs2c-test` = `scripts/cloudrun --owner main --kind test
  --name covs2c-test --ref lane/covs2c`; `covs2c-rows` = `scripts/cloudrun
  --owner main --kind mechrows --rows S3263,S1418,S3048 --name covs2c-rows
  --ref lane/covs2c`. The deliver file says `owed: none` (lanecheck reads the
  box queue only, brief).
- Commits: 1ef617673 (item 1), 6888166d9 (S3263), e7c258b77 (P1, the
  whole record; its message says WIP), 1f13610cf (shard table), 40e8c83aa (S3263's doc
  text, a K37 fix), then this report.

## WHAT WAS BUILT

1. **W5's remainder, B1's per-position check** (`src/gen/memfn_sites.c`,
   `.h`). The four writers `pcrec_memfn_wpos_table/_bits/_any/_cube` take
   the compile's `Ctx *` first; the one accessor they share, `wpos_set`, now
   refuses `j < 0 || j >= w->len` with "internal error: a window span
   position %d lies outside the span's %d positions
   (src/gen/memfn_sites.c)" before any store (the storage is exactly `len`
   entries since MF_SITE_ABI 30, so a position past it would write past the
   arena block). `wpos_table` needs no check of its own: every caller goes
   through `wpos_set` first or writes the table at the same `j`
   (`pcrec_memfn_wpos_table` calls `wpos_set` before `wpos_table(w)[j]`).
   12 call sites respelled with `cx` (10 in `src/gen/emit_dfa.c`, 2 in
   `src/gen/known.c`); two continuation lines re-indented. Not a
   caller-visible change (an internal error no input reaches), so no spec
   hunk.
2. **W12, witness row (b)**: mech row S3263 (THE ROWS).
3. **P1, the `MFWSTMT` trace record** (`src/gen/memfn_sites.c`, inside
   `#ifdef PCREC_CAND_TRACE`, under `PCREC_MF_ROUTE_TRACE`, called from
   `pcrec_memfn_define` after `pres_record`). One line per stated span:
   `MFWSTMT<TAB>site<TAB>kind<TAB>owner<TAB>alt<TAB>entry<TAB>reseeds<TAB>span<TAB>start<TAB>len<TAB>verify<TAB>core_lo<TAB>core_len<TAB>sets`;
   `owner` is `site` (the site's own `alts`) or `part<I>` (pre-check part
   I's `pspans[I].alts`); `entry` the `MF_ENTRY_*` name; `reseeds` 1 where
   any of that owner's alternatives enters RESEED; `sets` the span's `len`
   sets, comma-separated, 64 hex digits each. These are R6 §3's fields
   (r45_reply.md rev 6, "The record the prediction reads"), read from the
   `mf_site` pcrec defines, never a kit reply. Exercised on a
   `-DPCREC_CAND_TRACE` build (lane scratch `trace/`): `[0-9a-f]{32}` prints
   one COVER span `0 32` (the after side unstated); `\b\.[0-9]{4}Z` two
   (the stated before side at -1); `foo[0-9]+bar` PF's PARKED + RESEED
   alternatives with `reseeds` 1; `(x?)(?i:abcdefghijkl)\1` a `part0` run of
   12 and the PF site's span. Trace-stream readers that do not filter by
   record name: NONE. Every reader of `PCREC_MF_ROUTE_TRACE` output filters
   by prefix: `tests/memfn/run_deleg_sites.sh` (`grep '^MFROUTED'`, awk
   `$1 == "MFPRES"`), `docs/design/memfn/r17b_prime/fdb2/routed_census.py`
   and `b3b/routed_census_b3b.py` (`startswith`),
   `docs/design/memfn/span_pick/probe/collect.py` and
   `docs/dev/lanes/r33_sim/collect.py` (`startswith` on MFTRACE / MFROUTED /
   MFPRESDROP / R33). `scripts/emit_sweep.py`'s trace mode and
   `tests/codegen/run_cand_oracle.sh` never set `PCREC_MF_ROUTE_TRACE`, so
   their streams carry no `MFWSTMT`. P2 (the predictor reading it) is unit 2's.
4. **r27 READ-3**: reproduced, NOT fixed (LEFT OPEN).

## THE ROWS

| id | plant | expectation | REACH result | probed how |
|---|---|---|---|---|
| S3263 (new, W12 row (b)) | `memfn/src/compose.c`: `long end = last_s + 1;` (S3242's cut) AND `SAB_FILE2` deletes R-short, the two lines carrying "the proof range ends before the statement's following offset" | DETECTED by the `kitproof` arm (the `[0-9a-f]{32}` answer rows' harness compile fails). The matrix has no text field, so B5's text is the hand probe: on a planted tree (both plants applied from the row's own fields) `build/pcrec` on `[0-9a-f]{32}` exits 1 with "internal error: the kit's proof range ends at offset 31, before the cover's after-context at 32 (src/gen/known.c)"; the after-STATED control `\b[0-9a-f]{32}\b` compiles clean under the same plant (rc 0), as C9 predicts (last_s 32, the cut range reaches k + 1) | REACHED 3/3 (`REACH-WIDTH-32-K-32`: `--list-limits` default 32 and the facts cover row `cover 32 32`; `REACH-COVER`; `REACH-WHY=[cover]`) | `REACH_ONLY=1 bash tests/mech/run_sabotage_matrix.sh S3263` at 6888166d9, alone; `VALIDATE_ONLY=1` FIELDS OK |
| S1418 (re-anchored) | `pcrec_memfn_wpos_table(cx, &sp[0], 0, wk->k[0].set, ...)` with the continuation re-indented; plant states `us->cand.set` (same fault) | DETECTED (unchanged: harness `offset_skip.rxt` + offsetskip) | NO-PROBE (the row declares none, as before) | anchor counted 1 in `src/gen/emit_dfa.c` from the row's own `SAB_BEFORE`; `VALIDATE_ONLY=1` FIELDS OK; `REACH_ONLY=1` at 1ef617673 |
| S3048 (re-anchored) | `pcrec_memfn_wpos_bits(cx, sp, j, run->pos[j]);` -> cube with mask 0xFF (same fault) | DETECTED (unchanged: codegen reqcube_check) | REACHED 1/1 (`REACH-K66-MASKED-RUN`) | as S1418, same run |

S448 names `pcrec_memfn_wpos_cube` only in a comment (no anchor); unchanged.
`tests/ci/cloud_mech_shards.tsv` regenerated by its generator
(`tests/ci/cloud_units_plan.py mech --slots 30 --waves 3 --measured
tests/ci/measured_mech.tsv --write`); `tests/ci/cloud_mech_check.sh` PASS, 90
shards, 1,318 ids. Ids used: S3263 only (S3264-S3269 unused).

## VALIDATION

- `nice make -j4` and `make strict` clean after item 1 and after P1
  ("strict: whole tree compiles clean with -Werror -Wshadow"); the
  `-DPCREC_CAND_TRACE` build (lane scratch `trace/`, `-Wall -Wextra`) clean,
  no warning.
- Premise test held: tip df4d38bdb; build clean; `[0-9a-f]{32}` stamps abi 109.
- Byte identity: emit_sweep 0 movers on every stream (STATE AT HANDOFF).
- `make test-codegen` (the one pin section the brief allows, under
  `scripts/boxlock run`): first run at 1f13610cf RED, 20/21 scripts,
  `*** [Makefile:737: test-codegen] Error 1`: `run_codegen_tests.sh`'s [K37]
  check read S3263's `SAB_DOC_FIGURE` text "build/pcrec on [0-9a-f]{32}" as an
  unbounded compiler invocation (lane scratch `codegen1.log`). Reworded
  (40e8c83aa); the [K37] site regex then matches only the row's `SAB_REACH`
  line, which the first run already passed. Re-run at 40e8c83aa: GREEN, 21/21 scripts, no `*** [...test-...] Error` line, rc 0
  (lane scratch `codegen.log`). Inside the same run, [SABANCHOR]
  (`scripts/m6read_check_sab_anchors.py`) passed: all 1,318 rows' anchors
  resolve, S1418/S3048/S3263 included.
- NOT run locally (box rules): `make test`, mech, axes. Owed to the cloud runs
  above.

## LEFT OPEN

- **r27 READ-3, STOPPED: the fix is not local.** Reproduced: `build/pcrec
  --features all -p rx --window-search-width=4095 -o X.c --pattern
  '[0-9a-f]{4095}'` exits 1 with "pattern too large: 612696 bytes of emitted
  code (limit 500000) ...". Facts:
  - the cover's code grows with k: at width 4095 `[0-9a-f]{k}` fits up to
    k = 3,328 and fails from k = 3,329 (500,093 bytes); `a{4095}` (a literal
    cover) fits; at `--window-search-width=4094` the same `{4095}` declines
    the cover and the engine route fits (rc 0, `RX_DFA_SCAN "unanchored"`,
    `RX_ENGINE_SEL "selected"`); `--max-emit-code-bytes=700000` ships the
    4095 cover (612,708 bytes of code).
  - `fit_rungs[]` (`src/core/compile.c`) has no row that declines the
    cover, so the ladder reaches `refuse`. `limits.md` §3.12¶4 promises the
    engine "through the size-cap ladder (§8.4), stamped `size-cap-retry`",
    but §8.4's table has no such rung either: the spec contradicts itself
    as well as the code.
  - Options: (a) a `drop-cover` ladder row: a new `FitAct`, an `applies`
    on "this artifact's scan is the cover", a `Ctx` bit `cc_fits` reads
    (like `end_mark_dropped`), its `fit_seq_legal` pairs, a facts `why`
    for the decline, the §8.4 table row ("all ten" becomes eleven) and its
    order, which is a cost claim nothing has measured (memory: suspect
    constants); plus the rung-table readers (`pcrec_fit_table_row`'s dump,
    S237/S238/S420-shaped rows) and a witness row. General, the table's own
    form, moves no default byte; but it touches the ladder, a dump and two
    spec sections, so it is a unit with its own design round, not a local
    fix. (b) Decline the cover in C15 when its code would pass the cap:
    needs a size estimate that does not exist. (c) Change §3.12¶4 to today's
    behaviour (a width whose cover passes the cap fails the compile; raise
    `--max-emit-code-bytes`): a contract change for the manager/owner.
    Leaning (lane's): (a), as a small unit after this landing; until then
    the spec and the code disagree at widths past ~3,328 positions of a
    16-member class.
- P2 (the predictor reading `MFWSTMT`) is unit 2's; the record's format is
  above for it.
- `scripts/lanecheck` reads owed keys from the box queue only; the two cloud
  runs are named here instead (brief).
