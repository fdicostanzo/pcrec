# covs1g report: r11 fixes on lane/covs1f

## STATE AT HANDOFF

- Branch lane/covs1f. Code commit 0fd00688f (all fixes, the critic texts, the skill sentence, the evidence jobs
  pointed at worktrees/covs1f); this report is a docs-only commit on top of it. No src/ behaviour change, abi stays
  108. One src/ text edit: the `limits.def` description string of PCREC_ANCHORED_MAX_STATES (the facts-listing /
  `--list-limits` cell), because the brief's "four places" for "at most 4095" includes that cell; that cell is
  already a declared dumps move of the sweep (`--list-limits:PCREC_ANCHORED_MAX_STATES`). `tests/registry/limits_check.sh` 42/0 and
  `make` clean after it.
- RULINGS FILE: `docs/dev/lanes/covs1g_rulings.md` did NOT exist in the worktree (the brief says it exists, empty).
  Last R-n applied: none. `covs1g_deliver.txt` was also absent; this report follows the brief's DELIVER text.
- No lost cover, no unexplained mover seen in any output (the lane ran no sweep itself).
- Evidence-tree note: the box jobs and the cloud run use commit 0fd00688f's code; the later commit adds only this report.

## FINDINGS FIXED

Red-before / green-after, each on its planted failure (plants in /var/tmp/pcrec-pcrec/scratch/covs1g/):

| finding | planted input | verdict before | verdict after |
|---|---|---|---|
| ADQ-3 tag floor | a clean 11-stream report with one `TAG FLOOR side a:` line, rc 1 | GREEN (rc 0) | RED (rc 1) |
| ADQ-3 reach floor | `REACH FLOOR VIOLATION` line, rc 0 | GREEN | RED |
| ADQ-3 uncaught exception | `emit_sweep: DONE rc=1 (uncaught exception, traceback follows)`, rc 1 | GREEN | RED |
| ADQ-3 DELIVER witness | `DELIVER WITNESS FAILURE` beside `DELIVER witness: OK`, rc 1 | GREEN | RED |
| ADQ-3 clean report | the same report with none of the plants, rc 0 | GREEN | GREEN (control) |
| ADQ-2 empty measured file | `meas=` an empty file, real shard table | PASS rc 0 | FAIL rc 1 ("WEIGHTS ... no measured row") |
| ADQ-2 missing measured file | `meas=` a nonexistent path | PASS rc 0 (awk error on stderr) | FAIL rc 1 |
| ADQ-4 | `finisher-dfa` in ROUTE_ROWS | dead name | dropped |

- ADQ-3: `docs/dev/lanes/covs1_evidence/sweep_verdict.py` now defaults RED. It is red on emit_sweep's failure
  vocabulary (VIOLATION, FAILURE, TAG FLOOR side, MANIFEST side, NO TAG FLOORS PINNED, CENSUS OFF-DIAGONAL,
  INVALID, uncaught exception, Traceback, "tag floors: NOT APPLIED", SELF-CHECK FAILED), requires one
  `tag floors: N pinned, all held` per tallied stream, requires a clean `emit_sweep: DONE rc=N` equal to the sweep
  rc, rc 0 or (rc 1 with at least one mover), and the old checks. `--selftest` holds 14 constructed reports
  (all 14 right). The earlier covs1-sweep runs (failed, rc 1 at 38 s and 99 s per `boxqueue status`) never reached
  a green verdict, so no log judged green by the old script exists to re-read.
- ADQ-2: `tests/ci/cloud_mech_check.sh` fails when `measured_mech.tsv` is missing or has no `measured` row; its
  `--selftest` plants both (the file is overridable through `meas=`). The real table still passes (90 shards, 1305 ids)
  and the selftest rc is 0.
- ADQ-4: all 14 other ROUTE_ROWS names were checked against a built `--emit-facts` listing (column 2 of the facts
  and decisions sections, `a(b|c)+d` and `ab$`): all are rows. Kept those 14; dropped `finisher-dfa` (a conjunct
  name in known.c / lmwalk.c, not a row). No replacement name was added (none of the listing rows is a finisher).
- DOC: S3226's SAB_DOC_FIGURE says 2 checks fail (verdict u and facts u); job_z2's dry-run reason updated;
  kit_proof.md's four unmarked producers-disagree sentences each carry a dated "history, retired 2026-11-15" mark;
  the facts-listing spec's why-id clause now says the ids may change in any release with no abi event, the listing
  having none (by section, no line cite); "at most 4095" became "the ceiling less one" in limits.def, the
  facts-listing spec's stretch clause, cover_cap.md (two places) and kit_proof.md C7 (the number 4095 stays beside it
  as the default's value).
- Also: the round's five critic texts are in docs/dev/reviews/2026-11-15-r11-covs1f/ (the pre-commit spec-cite check
  passed unchanged); .claude/skills/pcrec-critic/SKILL.md section 3 step 2 gained the one sentence on building BASE
  and SUBJECT trace binaries behind whatever guard a touched trace sits behind.
- `make test-plan-lint` 2/0 before the commit.

## OWED RUNS

- Queue: 200-covs1-sweep and 200-covs1-predict cancelled (200-covs1-asan left running). Added
  `200-covs1f-sweep` (key covs1f-sweep) and `200-covs1f-predict` (key covs1f-predict). The job scripts source
  worktrees/covs1f and scratch /var/tmp/pcrec-pcrec/scratch/covs1f/. job_sweep writes its verdict to
  `$SC/sweep.verdict`; predict's `--ready` waits on that file (75 until it exists, 77 if it reads non-zero) plus the
  20:00-01:00 hold, not on a key. Green = `sweep_verdict: ... instrument ok` in the sweep log, then predict's rc 0.
  Dry runs (as queued):
  - sweep: `would run in .../worktrees/covs1f: ref build of 91bae2d98 (abi 108) + emit_sweep.py --ref-bin, movers to .../scratch/covs1f/sweep.movers.tsv`; `cap 5400`, `est 2400`, `patience none`, expect none (reason: rc is sweep_verdict.py's rc, default RED, also written to sweep.verdict).
  - predict: `would run: predict.py over the corpus, ref .../scratch/covs1f/ref, movers .../scratch/covs1f/sweep.movers.tsv`; `cap 3600`, `est 1500`, `patience none`, expect none (exec'd, predict.py's rc).
- Cloud: pushed lane/covs1f; dispatched `scripts/cloudrun --owner main --kind test --name covs1g-0fd00688f --ref 0fd00688f`,
  branch cloud/main/test/covs1g-0fd00688f, run id 43773092490 (`gh run list` showed it in_progress). Verdict arrives as CLOUD-DONE.
