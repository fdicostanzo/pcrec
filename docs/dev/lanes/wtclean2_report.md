# wtclean2 report

## Summary

Premise: `git worktree list | wc -l` printed 80 (brief ~79, holds). Applied Frank's 2026-10-29 "Yes" to removing commit-only worktrees: 54 worktrees removed by `scripts/wtprune --apply --force NAME..` (named, 3 batches: 20 / 20 / 17 attempted, dry run between; 18 + 20 + 16 removed), worktrees 80 -> 26 registered. 3 of the 57 named were kept by wtprune's own gates (p48 and primesurv modified <120 min, s3m has a process cwd). Branches: 494 local before and after (no branch deleted or renamed; stop rule never fired, nothing removed that was not named). Nothing left that is commit-only except the trees named under "Left for the manager". Size-log dirt: tracked by design (tests/size/CLAUDE.md); options below. Branch census: 494 local, 433 merged, 61 unmerged (26 kit, 35 non-kit); origin 98, 95 merged, 3 unmerged.

## Removed

Dirt in every removed tree was only: artifact_size_log.tsv rewrite, untracked NAME_rulings.md / *_deliver.txt, logs (s25tri build/strict/fbt logs), p48.done-style markers, maskbench's untracked raw perf/ + waiter.pid (its perf.tar.gz is committed). Each escalation's diff is saved in worktrees/.wtprune.force/NAME-TS.diff (audit in worktrees/.wtprune.log). "ahead" = commits on the branch not in main; the branch is KEPT, find the commits there.

| worktree | branch | tip sha | ahead of main |
|---|---|---|---|
| l9look | lane/l9look | 4deec7fc9 | 0 |
| revwalk | lane/revwalk | 7d1b32485 | 0 |
| wtclean | lane/wtclean | 00abb619c | 0 |
| costmodel | lane/memfn-costmodel | 7fa573bf5 | 138 |
| expectpre | lane/expectpre | 2e34e3c14 | 1 |
| fdb0 | lane/fdb0 | 668aa1b12 | 1 |
| g2pin | lane/g2pin | a9645193c | 128 |
| grid1 | lane/memfn-grid1 | f160c8f22 | 147 |
| gridread | lane/memfn-gridread | 540649453 | 151 |
| ideas2 | lane/memfn-ideas2 | 47669cc01 | 1 |
| kref2 | lane/kref2 | 2c597c35f | 87 |
| langmisc | langmisc | c01e15fa2 | 1 |
| lflaxtri | lane/lflaxtri | 884a0d71b | 1 |
| maskbench | lane/maskbench | f862f6ba3 | 5 |
| pcscope | lane/memfn-pcscope | 1cfce03c5 | 183 |
| r17a | lane/r17a | 9cc286ef7 | 74 |
| r17b | lane/r17b | 174f3e320 | 87 |
| r17b2 | lane/r17b2 | 60f6a25f4 | 89 |
| r17bp | lane/memfn-r17bp | 830bbce39 | 156 |
| r17bp3 | lane/memfn-r17bp3 | 34f46199f | 200 |
| r17c | lane/r17c | 95788bda1 | 98 |
| r17d | lane/r17d | 9aca4c2fc | 120 |
| r17dry | lane/r17dry | 541dd2ddc | 21 |
| r17e | lane/r17e | 2ead0d59d | 126 |
| r17loss | lane/r17loss | 46e23be1f | 130 |
| r17r | lane/r17r | 32268464e | 61 |
| r17rd | lane/r17rd | 5d067c0f1 | 41 |
| r17s | lane/r17s | 41205da76 | 5 |
| r17upa | lane/r17upa | 49bc596de | 69 |
| r27c | lane/memfn-r27c | b9dc32e3f | 5 |
| r28m | lane/memfn-r28m | c8409a9da | 1 |
| regeval | lane/memfn-regeval | b79a9eff9 | 157 |
| regeval2 | lane/memfn-regeval2 | 08dad8eec | 161 |
| regeval3 | lane/memfn-regeval3 | 393112b7d | 170 |
| regeval4 | lane/memfn-regeval4 | 93bfd6e18 | 173 |
| regeval5 | lane/memfn-regeval5 | 23afdd92e | 177 |
| regeval6 | lane/memfn-regeval6 | 1af3bb3c5 | 193 |
| regeval7 | lane/memfn-regeval7 | eda3adc8d | 194 |
| rewtwin-scratch | lane/rewtwin-scratch | 71ebfc5bb | 2 |
| s25alpha | lane/s25alpha | 8a02504f9 | 129 |
| s25btip | lane/s25btip | c62220fbe | 127 |
| s25bv | lane/s25bv | dca28769c | 128 |
| s25mech | lane/s25mech | 2a4023e27 | 130 |
| s25tri | lane/s25tri | b66529602 | 125 |
| s3 | lane/memfn-s3w | ae83da9d4 | 16 |
| s3fix | lane/memfn-s3fix | e5362a59c | 40 |
| s3pair | lane/memfn-s3pair | cc4f54eb2 | 29 |
| sbscope | lane/memfn-sbscope | 6e3ea9656 | 183 |
| setdig | lane/memfn-setdig | 219f52123 | 2 |
| stopstudy | lane/memfn-stopstudy | fc6735cdf | 4 |
| substuc | lane/substuc | 2ff5940ab | 2 |
| vecspike | lane/vecspike | c2e7a6e54 | 129 |
| vecspike2 | lane/vecspike2 | 19b3151b4 | 131 |
| winreq | lane/memfn-winreq | 49971f3d0 | 189 |

Also removed in batch 1 (merged, ahead=0): l9look (lane/l9look 4deec7fc9), revwalk (lane/revwalk 7d1b32485), wtclean (lane/wtclean 00abb619c) — these three are in the table above too.

Kept by wtprune's own gates among the named: p48 and primesurv (modified within 120 min; both merged, ahead=0, dirt = p48.done marker / size log), s3m (a process has its cwd there; 47 commits ahead on lane/memfn-s3m, dirt = size log only). Re-run later, they qualify.

## Left for the manager

Tracked modifications beyond the size log (not removed):
- fdb2drop (detached 8804bd78c): edits to cli/main.c, src/core/internal.h, src/gen/memfn_sites.c, memfn_stamps.c, CLAUDE.md files, deleted S1080/S1081/S1084 sabotage scripts.
- mptime (detached 5554d668d): edit to tests/mech/run_sabotage_matrix.sh.
- mscomp2 (lane/mscomp2 4dcb77d5b): tracked mscomp2_rulings.md deleted.
- wingame2 (lane/wingame2 8038f53bb): mid-merge, unresolved AA conflicts under docs/design/memfn/window_search_game*.
- wsc1 (lane/memfn-wsc1 3cd809da1): edits to wsc1_report.md, memfn/docs/journal.md, memfn/tests/*.sh/CLAUDE.md, docs/dev/history/claude_md/docs__dev__lanes.md.

Uncommitted job scripts / evidence (not removed):
- e8min: jobs/560-kit-e8-window-r2 (docs/design/memfn/r17b_prime/e8min/jobs/) plus e8min_rulings.md.
- r28: docs/dev/lanes/r28/570-kit-r28-heavy.
- vb-9950aa672 (detached 9950aa672): vbisect-job.
- findbench (13 ahead): docs/dev/lanes/findbench_jobs/580-findbench-parity-quiet (queue job, parity bench run).
- streamdes (8 ahead): untracked docs/dev/lanes/streamdes_evidence/ (584K evidence directory).

Live process cwd: s3m (see above). Not touched by rule: memfn (kit home, lane/memfn-r30), memfn-r17, memfn-r27 (untracked r27_rulings.md), memfn-slot and its nested worktree memfn-slot/b3b/reach/wt; fullsuite-run-20261023_5596c3207 and fullsuite-run-20261027_7d3be7ec7 (detached, size-log dirt only; manager decides); live/owed lanes ic3, trailgc, p910, vmbc, p1dsg, wtclean2. Unmanaged dirs untouched: g2u-cell, langmisc-cell, memfn-slot, streamcrit1-scratch.

## Size-log dirt

Writer: tests/size/run_size_log.sh line 37, `STABLE_LOG="${ARTSIZE_LOG:-$ROOT_DIR/docs/dev/artifact_size_log.tsv}"`, rewritten after every full-corpus run (the test-corpus recipe in the Makefile). Readers (code, not prose): tests/size/check_size_tripwire.sh line 74 (same `ARTSIZE_LOG` default; FAILS "size log not found" if absent), scripts/size_diff (baseline compare), docs/dev/optdial_size_sweep.md style diffs; plus docs/ mentions and comments in src/core/limits.h, src/core/sb.c. tests/size/CLAUDE.md "Why ... stays TRACKED" (admin88, 2026-09-30) already considered and rejected untracking: the committed copy is the baseline on a fresh clone and `git log` on it is the ratchet history.

What would stop it dirtying every tested worktree, without losing that:
1. Write the working copy elsewhere, keep the committed one as the baseline: default `STABLE_LOG` to `$ROOT_DIR/build/artifact_size_log.tsv` (ignored) in run_size_log.sh, and have check_size_tripwire.sh read the build copy when it exists, else the tracked one. A gate re-archive then becomes an explicit `cp` (or `ARTSIZE_LOG=docs/dev/artifact_size_log.tsv`). Touches 2 scripts, tests/size/CLAUDE.md and the docs that say the log is rewritten in place; the sabotage rows that plant a log via ARTSIZE_LOG are unaffected.
2. `git update-index --assume-unchanged` per worktree: hides the dirt but also hides a deliberate re-archive; fragile, not recommended.
3. Untrack it (rejected by admin88; needs a seed copy for the tripwire on a fresh clone).
Report only; no change made. Option 1 is the smallest consistent with the standing verdict.

## Branch census

Read-only, taken after the removals (worktree removal does not change branches).
- Local branches: 494 (before and after the removals). Merged into main: 433. Unmerged: 61.
- Kit's lane/memfn-*: 93 total, 67 merged, 26 unmerged. (No bare `memfn*` branches.)
- Unmerged non-kit: 35 (listed below). Branches attached to a registered worktree now: 20 (git branch %(worktreepath)).
- origin (git branch -r, excluding HEAD): 98; merged into main 95; unmerged 3: origin/g2x, origin/lane/opt5m2, origin/lane/srG.

Unmerged non-kit local branches (tip date, name, commits ahead, last subject):

- 2026-10-10 lane/lflaxtri (1 ahead): lflaxtri: triage of lfl0 test-axes give-ups (report + proposed GIVEUP1_ALLOWANCE Group H diff)
- 2026-10-11 lane/r17s (5 ahead): r17s: R-17 scoping + twin design report, census K35 body count, CLAUDE.md index entries
- 2026-10-11 lane/rewtwin-scratch (2 ahead): SCRATCH: twin declines encodings with non-boundary positions (n-W mid-character -> PCREC_ERR_STARTPOS)
- 2026-10-11 lane/rlhtwin-scratch (1 ahead): rlhtwin SCRATCH (NOT FOR MERGE): one-byte K82 handoff — per-member set offsets, landmark K = run window's or t
- 2026-10-12 lane/kref2 (87 ahead): Merge commit '828755101' into lane/kref2
- 2026-10-12 lane/r17a (74 ahead): r17a: report, lanes index, rank_check CLAUDE.md note
- 2026-10-12 lane/r17b2 (89 ahead): WIP r17b2: MF_SET_BUDGET derived (4 x 787 = 3148), census re-run, §6.2 resolution
- 2026-10-12 lane/r17b (87 ahead): [MEMFN] R17-b: the stateful set find pf_terms_mask, abi 76 -> 77, MF_SITE_ABI 11 -> 12
- 2026-10-12 lane/r17c (98 ahead): r17c: sabotage rows renumbered S855-S858 -> S867-S870 (main's allocation; S855-S866 are endmark's)
- 2026-10-12 lane/r17d (120 ahead): r17d: report box line
- 2026-10-12 lane/r17dry (21 ahead): r17dry: R-17 rev-2 harness compiled, checked (0 mismatches, planted 152/152, ASan/UBSan clean), dry-run; repor
- 2026-10-12 lane/r17e (126 ahead): memfn: session close — journal, responses notice (R17-b status), wake.md rewritten (slot25 running; make-test 
- 2026-10-12 lane/r17r (61 ahead): r17r23: mark the single-guard name superseded in §3.4a
- 2026-10-12 lane/r17rd (41 ahead): memfn R-17 reading: wording fix
- 2026-10-12 lane/r17upa (69 ahead): r17upa: uses per activation of R-17's set-FIND sites on the bench's own subjects (counts, reading, report)
- 2026-10-12 lane/s25btip (127 ahead): s25b: report (KREF2, the 86-pattern equality, the amended judges and their controls, slot25b/run.sh's stages, 
- 2026-10-12 lane/s25tri (125 ahead): s25tri: fallback-table expectations take R17-c's drop-kit-bytes tail (slot25 red)
- 2026-10-13 lane/g2pin (128 ahead): g2 simd: derive the driver pin from the affinity set (CI has no CPUs 12-15)
- 2026-10-13 lane/r17loss (130 ahead): r17loss: R17-b ALPHA loss facts (sets, densities, site counts, fit, predicates)
- 2026-10-13 lane/s25alpha (129 ahead): lanes: s25alpha_report (slot25 alpha check red: hex-dash is an offset-set site, not a mover)
- 2026-10-13 lane/s25bv (128 ahead): [s25bv] slot25b VJUDGE RED triaged: engine-resolution + deny-attribution judge amendments, offline re-judge GR
- 2026-10-13 lane/s25mech (130 ahead): s25mech: report gains main's full-mech baseline and the on-main@657d4fd0f column; reruns re-armed
- 2026-10-13 lane/vecspike (129 ahead): vecspike: checker, plants, time.sh (dry-run), counters, report
- 2026-10-13 lane/vecspike2 (131 ahead): vecspike2: multi-position class filter for dfa-hat (P2/P3/P4/P3W x w8/SSE2/AVX2): checks green, 8/8 plants det
- 2026-10-16 lane/fdb0 (1 ahead): Merge lane/memfn-fd (sweeparm: -fmemfn-simd/-fcomments DIFFER_PINS, S981/S982) into lane/fdb0
- 2026-10-16 lane/maskbench (5 ahead): maskbench: timing-1 results, perf tarball, section 6 verdict
- 2026-10-22 lane/findbench (13 ahead): Merge branch 'lane/iteropt2' into lane/findbench
- 2026-10-22 lane/streamdes (8 ahead): streamr2: report round 2 (STATE AT HANDOFF, probe (3) verdict) + lanes index
- 2026-10-22 lane/substuc (2 ahead): substfit: review r3, subst design rev 4b (f18336ee1) against the 29 blind use cases: 10 FITS / 15 FWF / 4 GAP 
- 2026-10-22 langmisc (1 ahead): langmisc: D27 adversary report + probe evidence (author: lane langmisc, blinded cell; committed by the manager
- 2026-10-25 lane/expectpre (1 ahead): boxqueue: add/retry/batch warn when an expect differs from the shape's last green population [EXPECT-PREFLIGHT
- 2026-10-29 lane/ic3 (13 ahead): ic3tri: deliver dirty-ok (ic3's own deliver file)
- 2026-10-29 lane/p1dsg (1 ahead): p1dsg WIP: twins (5b reverse-DFA + scan edge, dup-param VM) with results
- 2026-10-29 lane/p910 (2 ahead): p910 WIP: report draft (census pending), evidence refresh
- 2026-10-29 lane/trailgc (12 ahead): trailgc2: report records the helper's re-aim validation

## STATE AT HANDOFF

Complete. Rulings file wtclean2_rulings.md did not exist in the worktree (no entries applied). No build, no make, owed: none. wtprune dry run at the end: 0 removable, 25 kept, 4 unmanaged. Scratch (dry-run output, lists, dirt table) in /var/tmp/pcrec-pcrec/scratch/wtclean2/. Untracked files in the main tree (ic3_deliver.txt, revwalk_deliver.txt, wtclean_deliver.txt) were removed with their worktrees only where they lived in those trees; the main-tree copies were not touched.
