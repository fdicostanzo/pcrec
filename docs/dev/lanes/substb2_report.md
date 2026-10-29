# substb2 — [M4-SUBST] the R4 interface BUILD (opus)

Branch `lane/subst`, from f18336ee1. Design of record:
`docs/design/replace_design.md` §R4 through REVISION 4c (§R4.17, ruling R13).
Contract: `docs/spec/subst_api.md`, generated from
`docs/design/subst_api_r4_draft.md` and replacing the R3 spec. Build go: Frank,
2026-10-22, "Subst is a go".

## STATE AT HANDOFF (2026-10-22)

- **Commits:** 933c15f1d (step 0, revision 4c), 0c157573a (product and spec),
  872311fd1 (test-subst), f7dfff7d2 (examples/subst), 0aa57ee08 (sabotage
  rows), 552cf1eaf (match_api hunk), f3b758fba (test-subst-d27), then this
  report.
- **Last ruling applied:** R14, the d27 case `include.case.prefixes`, re-tagged
  as an expected refusal. The rulings file holds no "I1+I2 landed at <sha>"
  line.
- **Queued** (boxqueue batch b202610221355422645190, owner `substb2`, each
  waits for the one before it to go green):
  - `330-substb2-…build` (`make -j16`)
  - `331-…strict` (`make strict`)
  - `332-…test` (perfrun `make test`, log `job.log.make`)
  - `333-…mech` (`run_sabotage_matrix.sh`, 40 rows: S1346-S1348, S1350-S1363,
    S1365-S1382, S1500-S1504, all `SAB_EXPECT=DETECTED`)

  Logs are under `worktrees/.boxqueue/{done,failed}/<ts>-33N-substb2-*`. Read
  the verdict with `scripts/verdict` and make's
  `\*\*\* \[(Makefile:[0-9]+: )?test-` lines.
- **Expected red in 332, not this lane's:** `test-spec-history` has one
  `[cites]` FAIL. `tests/compound/CLAUDE.md:125` cites a measures.md paragraph (section 5, paragraph 8)
  which exists on main but not on this branch's base. substb's report
  recorded the same fail, and merging main resolves it. Any other red line is
  real.
- **Run here (light, single runs):**
  - `run_subst_tests.sh`: 3,109 passed, 0 failed, with ASan. That is 1,577
    cells checks plus the ASan pass and the section's own checks. The cells
    are 67 cells, 31 rx and 40 subst artifacts, 55 compared with libpcre2
    10.46. Every REACH_NEED token was reached.
  - `run_examples_tests.sh`: 4 passed, 0 failed.
  - d27: all eleven families have FAIL=0 (1,473 cases), the eight API
    drivers exit 0, and the CLI suite passes 89 with 0 fails after R14. The
    d27 sub-lane ran the full section under the box lock. I re-ran the CLI
    suite alone after the R14 edit.
  - `make test-spec-history`: only the fail above.
- **OWED:**
  1. **Merge main after I1+I2 land.** replace-all and the iterator recipes
     are built and tested here, against the I2 rx block this branch already
     carries (abi 84). The rulings file has no "I1+I2 landed" line yet, so
     main is not merged. When it lands: merge main, renumber the abi with
     the landing (see the ABI section below), then re-run 330-333.
  2. **The queued run's verdicts** (332, 333).
  3. **A witness for the no-map refusal of a composed rx** (§3¶8). No cell
     uses a composed rx, so the clause has no sabotage row. File it with
     the compound work, or as a candidate.

## What was built

- **Pieces.** `rx_subst_piece` is `{const unsigned char *p; size_t len}`. The
  element `<prefix>_render(ctx, map, caps, k, flags, o)` writes pieces into
  `rx_subst_out`, which carries `pc`, `cap`, `n`, `prev` and `need`, plus
  the scratch hooks `scratch`, `scap`, `sn` and `sneed`. Nothing calls
  malloc. The room test runs before anything is written, and NOSPACE sets
  `need`. A failing match commits the matches before it.
- **The reference list.** `<p>_subst_refs` lists the references in
  first-appearance order, group 0 excluded. The record gained `nrefs`,
  `refs`, `maxnum`, `npieces`, `nvrefs`, `vrefs`, `encoding`, `uses`,
  `support_id` and `support`. The header stamps are `<UP>_NREFS`,
  `_PIECES`, `_MAXNUM` and `_NVREFS`, opened by `#ifdef <UP>_PIECES
  #error`: two subst headers whose prefixes differ only in case refuse to
  share a translation unit (R14).
- **The map.** An optional `{slot, nslot, run, nrun}`. NULL means identity.
  `RX_SUBST_NOGROUP` is an intentional entry that renders empty, even under
  STRICT (R5 item 1).
- **The check.** `pcrec_subst_check` and `rx_subst_ctx_init` are `static
  inline` in the subst types block. The setup takes the rx record and the
  map, compares encodings, and refuses a composed rx when there is no map.
- **The support unit.** `pcrec --emit-support [-o FILE]` holds
  `rx_group_run`, `pcrec_subst_map_names`, `rx_subst_flatten` and
  `rx_subst_replace_all`:
  - names are abi-suffixed through macros;
  - `pcrec_support_id` is a 64-bit FNV-1a hash of the unit's own text;
  - definitions are under `PCREC_SUPPORT_IMPLEMENTATION`, or `static`
    under `PCREC_SUPPORT_STATIC`.

  With no other option, `--emit-support` writes identical bytes on every
  run. Any other option, pattern or template is refused.
- **The by-name helper.** A reference the rx lacks is MISSING_REF. Under
  `RX_SUBST_MAP_ABSENT` it becomes NOGROUP instead, counted in `*nabsent`,
  with `*bad_ref` set to the first such reference.
- **Unset groups.** Plain `$n` on an unset group renders empty.
  `RX_SUBST_STRICT` makes it `PCREC_SUBST_UNSET` (R6). `--unset=` is gone,
  so it is now an unknown option on every path.
- **replace-all** (draft §10¶6-¶10 with R13):
  - it returns the match count, capped at INT_MAX;
  - `out == NULL` with `cap == 0` sizes the output only, and `out == NULL`
    with `cap > 0` is MISMATCH;
  - NOSPACE sets `*len` to the total;
  - it refuses an iterator that is neither FRESH nor BOUND;
  - the batch size `k` is the smallest of `PAIRS/ncap`, `cap/P` and 64;
  - on a scratch NOSPACE it retries one match at a time.
- **Prefix families:** `rx_subst`, `rx_group`, `pcrec_subst` and
  `pcrec_support`. `rx_shape` is dropped.
- **Spec (D80):**
  - `subst_api.md`, all of it;
  - `cli.md` §1.19¶1 (no `--unset`; every pattern option is refused,
    `--features` included);
  - the new `cli.md` §1.20 for `--emit-support`, with its TOC row;
  - `cli.md` §1.6¶2 row 4 (the families);
  - `match_api.md` §3.8¶9a.
- **Tests:**
  - `tests/subst/` is rewritten: the driver runs the spec's recipes,
    replace-all in every mode, the map modes and every refusal. The
    `cells.tsv` UNSET column is now STRICT.
  - `examples/subst/` holds the §6¶9 wrapper verbatim plus the §6 recipes,
    built with `-Werror` and compared against `expected.txt` by
    `test-examples`.
  - d27 was adapted by a sonnet sub-lane. Expected outputs are unchanged and
    every retired case is listed with its reason in `d27/CLAUDE.md`. The
    landing reviewer checks each one.
- **Not built** (not this lane's work): the case-forcing forms, the case
  table and the extended forms (`subst-extended`), and the G6 inline ASCII
  case step. The hooks they need are built: scratch in `rx_subst_out`, the
  sizing pass and replace-all's scratch NOSPACE handling. Every record
  carries `uses = 0`, `support_id = 0` and `support = NULL`.

## ABI

There is no rx abi event, so the abi stays 84 (lane/i2build's number). No byte
of the rx shared block or of any rx artifact moved. The subst block and the
support unit are never in an rx artifact. Their `#error` ties them to
`PCREC_RX_ABI_H`, and the support unit's names carry the abi, so they
renumber with the rx abi at landing and need no event of their own.

## Sabotage rows

- **Re-anchored on R4** (same IDs, same promise, new site): S1346, S1347,
  S1348, S1350 (now flatten's saturation), S1351 (a map slot at or past
  ncap), S1353 (replace-all's fit), S1354 (STRICT), S1355, S1363 and S1367
  (replace-all), S1356, S1358 (the no-map check, through the new `nmchk`
  arm), S1361, S1368 (COUNT 2: the check and the helper), S1369, S1370,
  S1371, S1375, and S1378 (the helper; its witness is now number -1, which
  would otherwise read as NOGROUP).
- **Wording refreshed:** S1352, S1357, S1359, S1360, S1362, S1365, S1366,
  S1372-S1374, S1376, S1377, S1379-S1382.
- **RETIRED with the glue:**
  - S1349: the glue's LIMIT cap. The limit is now the caller's loop.
  - S1364: the glue's VLA batch buffer. Its overrun class is now S1500.
- **New:**
  - S1500: replace-all's batch ignores `PAIRS/ncap`;
  - S1501: the element's room test;
  - S1502: MAP_ABSENT maps to slot 0;
  - S1503: replace-all returns 0 instead of the count;
  - S1504: the element takes an unknown flag.

None was hand-planted this time. The anchors were counted against the source
(every row's BEFORE hits exactly SAB_COUNT), and 333 is the measurement.

## Numbers this lane needs (the manager assigns)

- A K-number, if the manager files the composed-rx witness gap (OWED 3) as a
  known issue rather than a candidate row.
- A D-number, if the manager records "no abi event for the R4 subst block or
  the support unit" as a decision. The reasoning is in the ABI section above.
