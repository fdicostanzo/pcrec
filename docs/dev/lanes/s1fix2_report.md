# s1fix2 report: review 2026-11-12 r2 memfn-s1b's ruled fixes in plan_frame 3.0b/§7 and the K38-3 row

STATE: done. Lane s1fix2 (opus, design text only), branch lane/memfn-s1design, worktree `worktrees/s1design`.

## Summary

Applied every ruled finding of `docs/dev/reviews/2026-11-12-r2-memfn-s1b.md` ("Rulings": all as proposed) as
text marked `[r2s1 ID]`: FIX-NOW R30B-1..6, R30B-8, R30B-9 and PLAN R30B-7 in `docs/design/memfn/plan_frame.md`
(§2.2, §2.3, §4.2, §5 3.0b, §7, STATE AT HANDOFF), and FIX-NOW RK383-1..6 in `docs/design/memfn/span_runs_sheet.md`
§5's K38-3 row. Each document's header carries a `[r2s1]` paragraph. Every new cite was read at main 0f1d54089
(`git diff 522faf600 main` is empty for `src/`, `memfn/`, `tests/`, the Makefile, `docs/dev/lanes/r33_sim/` and
`docs/design/memfn/`). The spec and plan are cited by section or tag only; no docs/spec line cite was added.
No code, no make, no suites, no queue jobs, no runs. `docs/design/memfn/part_d.md` untouched.

Design choices the review left open, as settled in text:
- R30B-3: the plant is "ASK-6 passes `call` 0", asserted by its failure TEXT (as row F does). Its form is left to
  main at the GO: row (AG) (recommended; 20 rows, S3078-S3097 on the same expectation) or a once-run control.
- RK383-1: the vehicle is the RECORDING build: per-width entry counters live only inside entry calls, layout L
  count-only (no records), and a count-only layout-A loop on its own stream (RK383-6).
- RK383-2: the `--plant` path reads `asan.log` with an ASan `plant_expect` pattern, and oracle item 4 is stated as
  each plant's SECOND detector. W-K4b is not re-aimed, and the `g2pres-asan` arm stays, with its cost re-weighed
  in the shard planner after the first cloud mech run.
- RK383-3: the set writer splits by ver (one set per method), and `meas_recompute.py` learns `kit-grid@4`.

## Per-finding fixes

| id | ruling | where (section) | change | control named (new checks only) |
|---|---|---|---|---|
| R30B-1 | FIX-NOW | plan_frame §5 3.0b Content (traced purity pass), Witnesses, row (E) | the traced `fxt --purity` pass is held to the plain pass's rule (rc and `checks passed == PURITY_FLOOR`) and counts its window defines per frame from `MFTRACE END table=wfE ... chosen=` lines. The counts are pinned exact; an E-func count of 0 is a named failure | Table E's E-func row declined (`wf_erows[E_FUNC]` `holds` 0), or a fixture edit stating the purity sites STMT/ASSIGN if that plant refuses: purity stays green, and only the E-func count reds |
| R30B-2 | FIX-NOW | plan_frame §5 3.0b Content, Witnesses | the Makefile builds `libpcrec_mftrace.a` (`run_g2.sh` only reads it, exit 2 if missing). The traced window-family pass is shown green on the base tree first, and a pre-3.0b traced-check red is filed before the carrier is claimed | no new check (a gate step) |
| R30B-3 | FIX-NOW | plan_frame §4.2 ASK-6, re-base ids bullet, Witnesses, new row (AG), Size | plant: ASK-6 passes `call` 0. The row asserts the internal-error text naming ASK-6's refusal. Main picks the form at the GO: row (AG) or a once-run control | the plant itself: with the loud hunk deleted it drops the `@` silently with no failed compile, so the asserted text reds only through the new check |
| R30B-4 | FIX-NOW | plan_frame §4.2 ASK-6 | "a refusal on exactly this call" corrected: 3.0b refuses `call` 0 (UNSTATED); ASK-6 asks NONE (1), which is not refused | n/a (wording) |
| R30B-5 | FIX-NOW | plan_frame §4.2 ASK-6 | the hunk records the refusal in the cover branch and calls `pcrec_ctx_fail` after `done:`'s restore (it longjmps; `pcrec_cand_eval_reset` does not reset `pcrec_cand_trace_quiet`). The pre-existing class and its general fix are noted for main | n/a (placement) |
| R30B-6 | FIX-NOW | plan_frame §5 3.0b probe item | the successor directory holds four files: probe.c, a `build.sh` copy (its `here` names the successor), `collect.py` and `sim.py` (both stdlib only). The jobs keep `\|\| exit 1` | n/a (no check added; a missing file fails the job) |
| R30B-7 | PLAN | plan_frame §7 intro, Q16 (reworded row added after the original, which it supersedes), plan-rows table (ASK-DEFINE-FRAME restated) | Q16 is reworded over the ask KINDS (`mf_ask`, `mf_wdecide`) and cites the 3 built members (ASK-1+ASK-3, `req_pres_ask`, `cand_ask`) plus `window.c`'s "every pcrec caller turns -1 into pcrec_ctx_fail" comment. Trigger: the next new pcrec ask of either kind. The note for main is in the plan row | n/a (plan row) |
| R30B-8 | FIX-NOW | plan_frame §2.2 Purity | the fenced exception: a framed ask reaches `translate`'s `kit_fail` (:1566, :1576) through `e_legacy_holds` and poisons the art as the define would. It is FENCED as breaker (a), and NONE never reaches it | n/a (contract wording) |
| R30B-9 | FIX-NOW | plan_frame §2.3 `stop_test`, row (AF), §7 Q14 | names the path: with the stop kept in `plan[]` (pinned stretch), the candidate test `wf_test_to` or `d_hors_head`. Same by-offset class rule, so AF reds there too. Q14's "only B-walk" is scoped to the find. Stale window.c cites refreshed in place (:3124, :3107, :3137, :3217, :2709, :1054-1056, :1112). The 3 sites' path is recorded at the build's first G2 run | n/a (doc) |
| RK383-1 | FIX-NOW | span_runs_sheet §5 K38-3 content, after the S1-10 cells sentence | the vehicle: the recording build's per-width entry counters (inside entry calls only, not `measure()`), layout L count-only with no records, and a count-only layout-A loop | the w32 entry threshold raised past the longest subject: the text census stays green and the w32 entry cells read 0 and red |
| RK383-2 | FIX-NOW | span_runs_sheet §5 K38-3 plant column | the `--plant` path reads `asan.log` with an ASan `plant_expect` pattern. Oracle item 4 is the second detector of both plants (W-K4a still reds by its L fault, W-K4b by its ASan report) | the W-K4b row: with the read removed it prints `RED BUT NOT BY ITS DETECTOR` |
| RK383-3 | FIX-NOW | span_runs_sheet §5 K38-3 content, after `record.py` | the writer `est.py` writes one set per method (ver), with a per-ver rules owner on its read side. `meas_recompute.py` is added as a reader and learns `kit-grid@4` | no new check: the existing `check_store` and `meas_recompute` refusals |
| RK383-4 | FIX-NOW | span_runs_sheet §5 K38-3 content (dim check) | the dim check is scoped to the cards at the planned vers (ver 1's six cards would be refused otherwise) | the existing card plant (the `DIM_FIELD` line removed) |
| RK383-5 | FIX-NOW | span_runs_sheet §5 K38-3 content, after the S1-14 rule | exact-0 on non-admitting passes and the OFF cell, stated for the load cells (the sibling's `fvec` is not exact-0 checked) | w32 admitted on the x86-64 pass in a plant: that cell is nonzero and reds |
| RK383-6 | FIX-NOW (with RK383-1) | span_runs_sheet §5 K38-3, in RK383-1's text and the plant column | the layout-A loop uses its own stream (as FAM-3's `rnd2`). The `g2pres-asan` arm is re-weighed by `cloud_reweight.sh` after the first cloud mech run | n/a |

All 15 ids are applied: 14 FIX-NOW and 1 PLAN.

## Checks

- Cites: every new cite was re-read with `git show main:<file>` at main 0f1d54089, including: `Makefile`
  (`libpcrec_mftrace.a` rule and the g2 targets); `run_finder.sh` (fxt build, plain purity block); `compile.c`
  `pcrec_ctx_fail`; `emit_dfa.c` `req_run_at` :16050-16101 (save :16062-16066, `done:` :16095), `pcrec_cand_eval_reset`
  :10899, the quiet regions, `cand_asked_hold` :7047-7062, `window_reply_ask` :7614-7617, `req_pres_ask` :8749-8759,
  `cand_ask`'s fail :8356-8357, the `MemfnPre` comment :1267-1278; `window.c` :1275-1278, :1566, :1576, :1623, :1687,
  :1054-1056, :1112, :2709, :2797, :3107, :3124, :3137, :3217; `compose.c` `kit_fail` :77-86 and rule 2 :1221-1241,
  FDROUTE/WPATH :1195-1201; `arm_fixtures.c` :2096-2099; `trace_format.md`'s END record; `r33_sim` 240/241/build.sh
  and the Python imports; `g2_pres_run.c` :106, :182-188, :220, :537, :545, :555-568; `run_g2_pres.sh` :125-130,
  :206-230, :271-284, :392-405, :430, :528-541; `est.py` :583-587, :830, :858-860; `meas_recompute.py` :53-66,
  :273-280; `finder_check.py` `check_store`; `occurrence_oracle.py` item 4; `tests/ci/cloud_units_plan.py`,
  `cloud_reweight.sh`.
- Not re-run (forbidden in the evening hold, and none needed for text): R30B-9's 3 sites' path (a G2 run; the text
  defers it to the build's first G2 run) and RK383-2's oracle item-4 red (a `--plant` run). Both are stated as the
  build's first observations, not as facts.
- The pre-commit hook passed on both commits ("staged checks passed: 52, failed: 0"). No compile, make, suite or
  queue job ran.

## Charter-vs-committed checklist

- [x] Read BOILERPLATE.md and memfn/CLAUDE.md; worked only in `worktrees/s1design`, plus scratch edit scripts under
  `/var/tmp/pcrec-pcrec/scratch/memfn/s1fix2/` (not committed).
- [x] R30B-1..6, R30B-8, R30B-9, RK383-1..6 applied as proposed text, marked `[r2s1 ID]`.
- [x] Every new check names its control (R30B-1, R30B-3, RK383-1, RK383-2, RK383-5). The others add no check, or
  name the existing check that serves as their control.
- [x] R30B-7: §7 Q16 reworded over the ask kinds, plus the plan-row note for main (ASK-DEFINE-FRAME restated).
- [x] Cites verified at main 0f1d54089 (522faf600 or later); spec/plan cited by section or tag, no line cites.
- [x] No code under memfn/src or src/; part_d.md untouched; no merge, no push; named-path commits only.
- [x] Report committed with the deliver file's sections; lanecheck run; the history index
  (`docs/dev/history/claude_md/docs__dev__lanes.md`) has the report's entry.

## STATE AT HANDOFF

Done: three commits on lane/memfn-s1design after 50e586be8 (plan_frame, span_runs_sheet, report). No rulings file
was named. For main at 3.0b's GO: approve ASK-6's hunk (the review's precondition); choose R30B-3's plant form
(row (AG), recommended, or a once-run control); rule Q16 as reworded and file ASK-DEFINE-FRAME over both ask
kinds; optionally, the R30B-5 general fix (reset `pcrec_cand_trace_quiet` in `pcrec_cand_eval_reset`). Per the
kit manager's ruling the design goes to main for the GO without a third round. A fresh agent resumes from the
per-finding table above.

OWED: none.
