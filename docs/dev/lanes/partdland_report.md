# partdland — main dd5143e8d (d27fix) merged into lane/memfn-partd

STATE: delivered (validation numbers below; the box gate and the cloud runs OWED)

## Summary

Lane partdland (opus, 2026-11-13) merged main dd5143e8d, which holds d27fix (the window ask's F1-F4
fixes, family `make test-memfn-d27frame`, rows S3120-S3124), into lane/memfn-partd (Part D D0-D3 +
R-41, tip ea1ddd78b + the deliver file b21990615). Merge commit f9528e943. Three files conflicted;
each hunk is listed below. Every d27fix change to `memfn/src/window.c` and `memfn/src/kit.h` is in the
merged tree; the only d27fix code replaced is translate's ranking loop, which Part D moved into
`run_rank`, and `run_rank` holds the same two properties (below). `MF_SITE_ABI` stays 29 (main is 28).
`make strict` was green before the merge commit. d27frame is GREEN on the merged tip (Checks). The box
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

PENDING (filled when the validation chain ends; logs under /var/tmp/pcrec-pcrec/scratch/memfn/partdland/).

| check | result |
|---|---|
| nice make -j8 | rc 0 |
| make strict (before the merge commit) | rc 0 |

## Owed runs

OWED: kit-partdland-gate (box job 597-kit-partdland-gate: zero-mover proof against BASE dd5143e8d, built
fresh by the job, 71 identity arms plus the skipped new deny; the deny's ASSERT_ZERO cells; G2 plants
S3106-S3114, S3119, S3125-S3127, S3116-S3118, S1409; D3's production path + p14), plus cloud `test` and
`mechrows` on the merged tip f9528e943. The kit manager runs those. The mechrows set is Part D's
24 rows (S3106-S3115, S3119, S3125-S3127 + the re-anchored rows) plus d27fix's S3120-S3124 and S3006,
whose anchor is partd's here.
