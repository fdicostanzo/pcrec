# partdland — main dd5143e8d (d27fix) merged into lane/memfn-partd

STATE: delivered (validation numbers below; the box gate and the cloud runs OWED)

## Summary

Lane partdland (opus, 2026-11-13) merged main dd5143e8d, which holds d27fix (the window ask's F1-F4
fixes, family `make test-memfn-d27frame`, rows S3120-S3124), into lane/memfn-partd (Part D D0-D3 +
R-41, tip ea1ddd78b + the deliver file b21990615). Merge commit f9528e943. Three files conflicted;
each hunk is listed below. Every d27fix change to `memfn/src/window.c` and `memfn/src/kit.h` is in the
merged tree; the only d27fix code replaced is translate's ranking loop, which Part D moved into
`run_rank`, and `run_rank` holds the same two properties (below). `MF_SITE_ABI` stays 29 (main is 28).
`make strict` was green before the merge commit. d27frame is GREEN on the merged tip (Checks). Validation found
one merge-only G2 red, which was fixed in G2 (fix 1). The kit manager's triage of the pre-merge cloud reds
found two of Part D's own gaps, both fixed here: the axes classification (fix 2) and the arm pins (fix 3). The box
gate is queued as 597-kit-partdland-gate (BASE dd5143e8d, built fresh by the job).

## Merge and conflicts

`git merge main` (run alone): three conflicted files, five hunks. Everything else auto-merged,
including d27fix's `kit.h` (`kit_nop_decl`), `memfn.h` (spec text), `generic.c`, and its new files.

| file | hunk | resolution |
|---|---|---|
| memfn/src/window.c | `member_opts` body | partd's side. d27fix wrote `(kit_run_opts){ KIT_RUN_EXACT_AROUND, T_MASS_STRETCH }` and `kit_run_opts_of(d->art, KIT_RUN_WHOLE)`. Part D's `kit_run_opts` has a third field, and `kit_run_opts_of` takes the site (`kit_run_opts_of(d->art, d->s, KIT_RUN_WHOLE)`). The function and its rule are d27fix's, unchanged: verify NO gives EXACT_AROUND with the stretch row's tie, verify YES gives the art's options. |
| memfn/src/window.c | translate: `kit_run_reply r` declaration | partd's side, which drops it. The loop that read it is now `run_rank`, which declares its own. |
| memfn/src/window.c | translate: the ranking | partd's side: `ro = kit_run_opts_of(d->art, d->s, KIT_RUN_WHOLE)`, `if (d->pinned) ro.tie = member_opts(...).tie` (d27fix F1's two lines, kept), then `run_rank(d->art, ro, ...)`, `n = p->rank_n`. d27fix's inline loop is gone; see "d27fix's fixes kept". |
| tests/mech/sabotages/S3006_rank_asks_member_directly.sh | SAB_BEFORE/SAB_AFTER | partd's side: the anchor is `run_rank`'s call `kit_run_decide(rate, o, ...)`. d27fix's anchor was a line of translate's loop, and that loop no longer exists. |
| tests/mech/sabotages/S3006_rank_asks_member_directly.sh | RE-ANCHORED comments | partd's two comments kept. Instead of d27fix's comment, one line says that its re-anchor of the same date was superseded by partd's. |
| memfn/docs/journal.md | append-only tail | both sides: partd's three lines, then main's. |

Other files from the brief:
- `tests/ci/cloud_mech_shards.tsv` did not conflict. As the brief asks, main's version was taken and
  regenerated: `python3 -I tests/ci/cloud_units_plan.py mech --measured tests/ci/measured_mech.tsv --shards 90 --write`.
  That gave 90 shards of about 22.7 min each; 55 rows are unmeasured and carry 95.5 s.
- `MF_SITE_ABI` stays 29, and its readers were re-checked by grep. Every "28" left in the tree is
  history ("since 28" / "3.0b, 28"): plan_frame.md, span_pick probe, span_runs_sheet.md,
  arm_fixtures.c, and d27_frame's CLAUDE.md and d27_frame.c (the contract dates from 28). One stale
  reader was fixed: `memfn/include/CLAUDE.md` still gave the current values as `MF_SITE_ABI` 28 and
  `MF_CLASS_V` 9. Both parents said so, because Part D never updated it. It now says 29 (R-38 Part D +
  R-41) and 10.

## d27fix's fixes kept

Checked by grep on the merged `memfn/src/window.c` / `kit.h` (each hunk of d27fix's diff from
c5b3c2c22):
- F1 (the pinned R's tie): `member_opts` is the single home of the member's tie. translate's two lines
  (`ro` from the art, then `ro.tie = member_opts(...).tie` when pinned) are kept verbatim. Part D
  replaced the loop they fed with `run_rank(art, o, ...)`, which calls
  `kit_run_decide(rate, o, sets_at, sets, n, prev)` with the caller's `o` at every rank. That is the
  same property: the ranking's tie is the member's on a pinned R. It also keeps the loop's loud check:
  `kit_fail` "the run ranking lost position" when the tie row is no strict order, with `rank_n` cut
  at k. `make test-memfn-d27frame` is the property's check on the merged tip (Checks).
- F2: `kit_nop_decl` (kit.h), `nop_decl_rows`, `emit_use_refused`, and `wf_frame`'s use of
  `kit_nop_decl`. All present, auto-merged.
- F3: `if (use && site->decl_point) return -1;` in `wdecide_framed`, the `use` parameter, and
  `mf_wdecide` passing `call == MF_WCALL_EMIT`. All present.
- The defect-path refusal: `if (art->err[0]) { memset(out...); rc = -1; }` after `wd_free`. Present.
- F4: `test_of`'s `w->table[k] && w->grp[k] < 0`, `plan_tests`' stop by C-table alone, and
  `wf_agree`'s held `plan_test` using the same rule. All present.
- `wf_agree` asks `wdecide_framed(art, ws, def, gphases, 0, &asked)` (the define half), and
  `fp->ren` is set at both of its sites. Present.

## Checks

Logs are under /var/tmp/pcrec-pcrec/scratch/memfn/partdland/ (val.log is the chain's index).

| check | result |
|---|---|
| nice make -j8 | rc 0 |
| make strict (before the merge commit) | rc 0 |
| make test-codegen | rc 0, run_group 21/21 |
| make test-memfn-d27frame | GREEN: 6,937,301 checks passed, 0 failed (floor 6,500,000); control red in all 4 runs; empty red in all 4 runs |
| make test-memfn-finder | rc 0, 18,058 / 0 |
| make test-memfn-rows / link / targets / arch / forms | rc 0 each |
| make test-memfn-g2 (the quick tier) | first run RED: window family, plain and traced, `site 1452: table_name: plan[3] (offset 1): plan_test TABLE, the marker read`. Fix 1 below. Rerun rc 0: 70,358,671 passed / 0 failed (window traced 5,673; presence 8,051,517) |
| anchors (scripts/m6read_check_sab_anchors.py) | 1,294 sabotages, 1,345 anchor sites, all resolve |
| `CLAUDEMD_ROOT=... check_claudemd_size.sh --all` | rc 0, 370 files |
| make test-memfn-arms (after fix 3) | rc 0: 382 passed, 0 failed; 116 pinned rows over 58 fixtures |
| axes reach, `MEMFN_REACH_ONLY=1 AXES="--memfn=no-run-verify-wide" bash tests/axes/run_axes.sh` (after fix 2) | rc 0: run-verify-wide ASSERT_ZERO, differ=0 refused=0 of 5,491 patterns in all 8 cells (default and simd layers x byte/utf8 x c-default/c-vm); the population check passed |
| make strict (after fixes 1-3) | rc 0 |

**Fix 1: G2's table_name check at a stop that sits inside a run compare (commit d51ff0980).** At site 1452
(seed 20261022), the kit's text is a B-walk find over the stop at offset 1, whose marker
`g2w_t1452_2` is the stop's table, followed by ONE `memcmp` of offsets -2..1. Plan position 3 is
offset 1, which is the stop, inside that compare. The kit answers plan_test OWN there. That is right
under plan_frame §2.3 as d27fix revised it (F4: a position inside a run compare reads no table;
`plan_tests` answers the stop by C-table alone). The stop's own check (stop_test TABLE, marker read)
holds. G2 was wrong: it attributed the stop's marker read to the plan position. The fix exempts that
read only when four things hold: the position is the stop, it is inside a shared compare, it answers
OWN, and B-walk's stop_test TABLE reads that marker. The case is counted as `stop_run` on the classes
line; this seed has 1. No floor is set on it, because one witness is too thin to floor. Neither parent
had such a site. It is the first one Part D's generator produced under d27fix's rule.

**Fix 2 (the kit manager's triage, cloud axes run 43467980369): `tests/axes/memfn_arm.py`'s MEMFN_CLASS
had no row for Part D's new deny `run-verify-wide`.** `--list-axes` lists that deny, so the population
check went red. Added: ASSERT_ZERO cells at both layers (default, simd), the vrun-* shape. The deny is
the identity on every run stated before Part D, so it is inert on today's pcrec. A comment says that
the stage 3 joint landing ([RUN-POS-SET]) re-measures it.

**Fix 3 (the same triage, cloud test run 43467904318 shard 5): `make test-memfn-arms` reported four
parts rendered with no pin.** They are pre-wide-every-pos and pre-wide-findable, each .def and .use
(Part D's fixtures, never pinned). They are now pinned in `tests/memfn/pins/arms.tsv` under an ADDED
header, the way the file's header says pins are made. The digests were recorded from the kit's own
rendering (arm_fixtures.c's output on this tip, through run_arm_pins.sh's sha256 digest), never hand
computed. The arm column is `precheck`, the form id the driver prints for both fixtures. The triage
suggested fn-every-pos / fn-memchr, but check 1 compares against the printed id.

## Owed runs

OWED: kit-partdland-gate (box job 597-kit-partdland-gate: zero-mover proof against BASE dd5143e8d, built
fresh by the job, 71 identity arms plus the skipped new deny; the deny's ASSERT_ZERO cells; G2 plants
S3106-S3114, S3119, S3125-S3127, S3116-S3118, S1409; D3's production path + p14), plus cloud `test` and
`mechrows` on the branch tip (the merge f9528e943 plus the three fixes; tip at handoff named in the handback). The kit manager runs those. The mechrows set is Part D's
24 rows (S3106-S3115, S3119, S3125-S3127 + the re-anchored rows) plus d27fix's S3120-S3124 and S3006,
whose anchor is partd's here.

## STATE AT HANDOFF

Branch lane/memfn-partd at 13cebb40f (the merge is f9528e943; G2 fix d51ff0980; axes + pins 41cb0f4c5; then report
commits). Every check in Checks is green on this tip's code. OWED: kit-partdland-gate (queued as 597-kit-partdland-gate, job
script /var/tmp/pcrec-pcrec/scratch/memfn/partdland/jobs/gate.sh, completion line `partdland-gate: DONE ...`), and
cloud test + mechrows on this tip (the kit manager's).
