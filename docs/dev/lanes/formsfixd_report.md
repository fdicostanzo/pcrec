# formsfixd report — code review r36 G1, G9, G10, G11, G13 (grid assert): G2's hold on the shipped head and four check gaps

Lane formsfixd (sonnet), 2026-11-17, branch `lane/memfn-formsfixd` cut from `lane/memfn-forms` @ 31f98f49b.
Review of record: r36 (`docs/dev/reviews/2026-11-17-r36-memfn-forms2.md` on the kit manager's side) and its RULED section.
Rulings file `docs/dev/lanes/formsfixd_rulings.md`: empty (no entry to apply).

## Summary

- G2's default pass now pins the shipped head from a G2 LITERAL (`G2W_SHIPPED_HEAD` = 64 in `g2_win_gen.c`, never read from
  window.c): the exact loop pin and the below-head test run on it, in the random space and in the long rows. The script
  also compares the default pass's per-family loop counts with the head-64 pass's (equal: parked 5, pair 6, mass 6,
  mline 6, part 7, report 8, random 6, repeated 14, mixed 9).
- The wide REPORT stream is counted and floored (`wide-report rendered=60 past64=36`; floors 54 and 32).
- The lever's strict parse is pinned on the CLI (six refused rows, two accepted) and on `mf_lever` (the same eight, G2's
  generator controls).
- S727 re-anchored to `kit_opt_denied`; it no longer reaches the shared `opt_has`, so it cannot kill the force.
- run_g2_win.sh asserts its head list and the generator's `RC_HEADS` equal cards.py's `GRID`, read from cards.py.
- No compiler or kit source moved: `git diff 31f98f49b HEAD -- src cli lib memfn/src memfn/include` is empty. emit_sweep
  against 31f98f49b over the full population (7071 argv): movers 0, asymmetric 0, `emit_sweep: DONE rc=0`.

## Fixes

| finding | fix | commit |
|---|---|---|
| G1 | default pass pinned at literal 64 (`pin_head()` in loops_check and the long rows); `default==head64` per-family equality in run_g2_win.sh; plant S3285 (`WF_SPAN_HEAD` 64 -> 63) | 2db54e349 |
| G9 | `g2_win_gen: wide-report rendered=N past64=M` printed and both floored (54, 32; measured 60, 36) | 2db54e349, 8886152ce |
| G10 | CLI rows for `-0`, `+8`, `' 8'`, `4096`, empty, `8x` (refused) and `08`, `4095` (accepted) on `--harness=span-head=` (the harness build; `PCREC` is the plain binary, which has no such option); `lever_controls` in g2_win_gen.c, the same eight on `mf_lever`; plants S3286 (CLI empty accepted), S3287 (mf_lever empty accepted), S3288 (mf_lever top + 1); floor on controls 104 -> 112 | 2db54e349, 0a4c82115 |
| G11 | S727 anchored to `return opts && name && opt_has(opts, "no-", name);` in `kit_opt_denied` | 2db54e349 |
| G13 grid assert | run_g2_win.sh `GRID_HEADS` and generator `RC_HEADS` (less 0) asserted equal to cards.py's `GRID`, read from cards.py; plant S3289 (RC_HEADS drops 24) | 2db54e349 |

The mech shard table got the five new rows by hand (shard 45, ESTIMATE weight, after S3284) rather than a regeneration, so
the diff stays five lines; `cloud_mech_check.sh` passes (1325 ids). The sibling lane formsfixc takes S3290-S3299; its rows
will meet mine in that table at merge.

## Validation

Local, `nice`, `gnutimeout`, no queue, no timing, no full make test. Logs in `/var/tmp/pcrec-pcrec/scratch/memfn/formsfixd/`.

- `make strict`: rc 0.
- `make test-codegen` rc 0 (after one fix: the K37 heuristic flagged `$(dirname "$PCREC")/pcrec-harness` in the CLI rows; spelled `${PCREC%/*}/pcrec-harness`); `test-registry`, `test-rxtsource`, `test-memfn-link`, `test-cli` rc 0 (the CLI rows print PASS).
- `bash memfn/tests/run_g2_win.sh` (the file this run used): `checks passed: 27345`, `checks failed: 0`, 152 s.
- HEAD40 by hand (the reviewer's plant, `WF_SPAN_HEAD = 40`, lib rebuilt, then reverted by `git checkout`): RED, `checks failed: 9`,
  `FAIL: site 2801: span loop: a loop from offset 40, below the head 64` (and four more of that shape).
- Sabotage rows through `bash tests/mech/run_sabotage_matrix.sh ID`, every one DETECTED, 0 unexpected, 0 undetected:
  S3285 g2win 10 fail; S3286 cli 1 fail; S3287 g2win 10 fail; S3288 g2win 10 fail (`FAIL: site -1: lever control: span-head=4096`, once per pass);
  S3289 g2win 7 fail; S727 cli 10 fail + g2simd 348 fail; S3276 1331; S3277 263; S3278 axesmemfn 4; S3279 96; S3280 35; S3281 2; S3282 32; S3283 1291; S3284 204 (g2win fails unless named).
- `scripts/m6read_check_sab_anchors.py`: 1325 rows, all anchors resolve. `cloud_mech_check.sh`: PASS.
- emit_sweep zero movers (above).
- Not run (not asked): full `make test`, `make test-axes`, any timing.

## STATE AT HANDOFF

Last rulings entry applied: none (the file is empty). All work committed on `lane/memfn-formsfixd`.
Untouched by design: cards.py, r45_reply.md, memfn.h's mf_lever comment, window.c's label comment, cli/CLAUDE.md, docs/spec (formsfixc's).
Caveat for the merger: `docs/dev/history/claude_md/docs__dev__lanes.md` and `tests/ci/cloud_mech_shards.tsv` are touched by both lanes.
OWED: none
