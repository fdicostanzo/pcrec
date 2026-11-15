# mcfixd: round r5-memfn-mfindcomb, groups D-E (kit checks, row wording, review commit)

Lane mcfixd (sonnet), 2026-11-15. Branch `lane/memfn-mcfixd`, cut from 9cb091199.
Build go: Frank 2026-11-15 via main. No abi event, no emitted byte moved, no flag, no D/K/R id.

## Summary

The ruled code round is committed (review and its lens directory, indexed in
docs/dev/reviews/CLAUDE.md; the plan-line-cite grep over both found nothing).
Every group (D) item and the group (E) items that are mine are fixed, each check
fix shown RED on the unfixed tree and GREEN after. Two items were not applicable
or not mine, stated below.

## Fixes by id

- **EMITTED-3**: `memfn/src/window.c` `wf_wsearch` is sized `FF_MFIND + 1`, declares `[FF_MFIND] = MF_WSEARCH_NONE`, carries a `_Static_assert` on its size (as finder.c's ff_name does), and `wsearch_of` bounds on the table's own size. Same answers; no emitted byte.
- **CHECKS-1**: `memfn/tests/g2/g2_mfind_gen.c` `check_site` now requires the selector function (`g2m_N`) to `return g2m_N__w32(` at x86-64-v3 and `__w16(` at x86-64. RED: the plant `names[0]` -> `names[nr > 1 ? 1 : 0]` at memfn/src/ofsskip.c fn_selector (selector calls w16 at v3) was GREEN under the old generator (rc 0) and is RED under the new one (rc 1, "the selector does not call its top rung", every v3 site). Plant reverted.
- **CHECKS-3**: `tests/memfn/simd_guarded_check.py` counts `lever-capped` only when MEMFN_FORMS is none AND the artifact holds the fn-mfind body (`memcpy(&w, subject`). RED: S3170's shape (lever flag dropped from LEVER_ARMS) gave lever-capped 6 before; now 0 < floor 4 (and simd-form-lever 0 < 2). GREEN on the clean tree (floor met, run_simd_guarded.sh 19/19).
- **CHECKS-5**: new mech row **S3198** (`tests/mech/sabotages/S3198_simdguarded_mfind_fit_cap_dropped.sh`, suite simdguarded): `return ofs_fn_fits(x, d);` in vrun.c mfind_applies becomes `return 1;`. RED by hand (same edit in this worktree, rebuilt, run_simd_guarded.sh): four lever witnesses "plain stamp 4089/7831/2335/4323 exceeds the sum of its rows' bounds" and lever-capped 0 < 4. Plant reverted. Row passes VALIDATE_ONLY=1 field validation and scripts/m6read_check_sab_anchors.py (1301 sabotages, all anchors resolve). The full matrix run is the re-gate's.
- **CHECKS-7**: `memfn/tests/run_g2_mfind.py` scales the population floors on `(sites - 40) / 40`, capped at 1 (the first 40 sites are a fixed head). RED: old script at `--sites 48 --quick`: checks failed 6 (population multi/caseless/nterm3/nterm4/inloop/size). GREEN: new script at `--sites 48 --quick`: passed 202, failed 0.
- **DRAFTSETS-5 / contract-1** (code and rows half): rows.tsv `pending-site:span_pick-row-1` is now `instrument:mfind` on the three mfind rows, with the reason defined in rows.tsv's header and comment, accepted by rows_check.py (REASONS, section B, the error text; needs a non-empty unit), and listed in docs/design/memfn/row_contracts.md. The "picks yet / until a selection table picks / replaces this predicate" wording at kit.h (FF_MFIND), ofsskip.c (mfind_holds and both fn_rows comments), compose.c, src/core/internal.h, cli/CLAUDE.md and tests/axes/run_axes.sh, and memfn.h mf_lever, now says "unpicked measuring instrument, D197". Comments only; no emitted byte.
- **contract-3 (memfn.h half)**: the pointer to a review file is gone from the public header (mf_lever now states the stale-reply caveat itself); the same review pointer is also gone from kit.h and the two fn_rows comments.
- **SABROWS-2**: NOT APPLICABLE on this base. The `--reach` comment and gate of memfn/tests/run_g2_win.sh here (cut at 9cb091199) are the plain `n=` form and carry no plant-sensitivity claim; the `decisive`/`agree` wording the finding reads arrived with fixposts2b (28686de00), not in this tree. Fix it where that wording lives (main's tree) when this branch merges.

NOT DONE (mcfixa's files, per the brief): the card's "owed" wording in memfn/data/cards/kit-grid.tsv (DRAFTSETS-5's card half) and the kit-grid half of contract-3. They need the same D197 wording; mcfixa owns that file.

## Validation

All in worktrees/mcfixd, tip after this report's commit:
- make -j6 ok; `make strict` ok; `make test-codegen` ok (21/21 scripts).
- `python3 -I memfn/tests/run_g2_mfind.py --root WT --quick`: passed 202, failed 0 (57 plants in class). Same at `--sites 48`: 202/0.
- `bash tests/memfn/run_rows.sh`: 264 passed, 0 failed.
- `bash tests/memfn/run_simd_guarded.sh`: 19/19, lever-capped and simd-form-lever floors met.
- `VALIDATE_ONLY=1 bash tests/mech/run_sabotage_matrix.sh S3198`: FIELDS OK. `scripts/m6read_check_sab_anchors.py`: all anchors resolve. `bash tests/compound/run_lever_fence.sh`: PASS.
- Not run (re-gate's): make test, test-axes, full mech. NEW MECH ROW FOR THE RE-GATE: S3198 (suite simdguarded). tests/mech row count and any mech roster pin counting rows moves by one; lane found no pin by grep that names the count (re-gate confirms).

## STATE AT HANDOFF

Rulings file read: no entries (empty); last entry applied: none. OWED: none.
