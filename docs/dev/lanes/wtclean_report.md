# wtclean report

## Summary

Dry run before any action: 0 removable, 128 kept (premise 126 +-2 holds), 8 unmanaged. Classified: 60 (a) merged + build/test dirt only, 5 (b) tracked changes, 53 (b) unmerged commits, 3 (b) uncommitted job scripts, 2 fullsuite-run-* and 5 kit/self trees untouched. Removal results are in Removed (filled after each batch).

## Classification table

Basis: `git rev-list --count main..HEAD`, `git status --porcelain` per tree. (a) dirt = rewrite of tracked docs/dev/artifact_size_log.tsv and/or untracked lane process files (NAME_rulings.md, *_deliver.txt), logs, scratch/, a reference binary under ref/.

| worktree | class | note |
|---|---|---|
| adatwin | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| attrtab | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| b3b | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| b4p | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| b4prep | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| cired2 | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| cired4 | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| cired | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| clibundle | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| corefix | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| costmodel | B-unmerged | 138 commits not in main; tip: costmodel: the search-form cost model by regime (report, scripts, analysis) |
| ctxp2e | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| dd10b | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| e1 | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| e8min | B-untracked-job | uncommitted job script not in main |
| emitbidi | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| expectpre | B-unmerged | 1 commits not in main; tip: boxqueue: add/retry/batch warn when an expect differs from the shape's last green population [EXPECT-PREFLIGHT |
| fdb0 | B-unmerged | 1 commits not in main; tip: Merge lane/memfn-fd (sweeparm: -fmemfn-simd/-fcomments DIFFER_PINS, S981/S982) into lane/fdb0 |
| fdb0-mt | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| fdb2 | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| fdb2drop | B-tracked |  M cli/CLAUDE.md; M cli/main.c; M src/core/internal.h; |
| findbench | B-unmerged | 13 commits not in main; tip: Merge branch 'lane/iteropt2' into lane/findbench |
| flat | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| fullsuite-run-20261023_5596c3207 | FULLSUITE | manager decides |
| fullsuite-run-20261027_7d3be7ec7 | FULLSUITE | manager decides |
| g2pin | B-unmerged | 128 commits not in main; tip: g2 simd: derive the driver pin from the affinity set (CI has no CPUs 12-15) |
| grid1 | B-unmerged | 147 commits not in main; tip: grid1: the joint timing slot for costmodel §F F1/F2/F3, built and checked (not run): report, README contract,  |
| grid2r3 | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| gridread | B-unmerged | 151 commits not in main; tip: gridread: the reading of the grid1 joint timing slot — report, scripts, SHA256SUMS, analysis.txt, CLAUDE.md en |
| i1build | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| i2build | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| ic0 | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| ic1a | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| ic1b | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| ic3 | NEVER | kit/self/other-lane |
| ideas2 | B-unmerged | 1 commits not in main; tip: memfn ideas: why the verify is scalar; vector verify alternative |
| iterland | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| iteropt2 | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| iteropt | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| k100 | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| k113 | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| kref2 | B-unmerged | 87 commits not in main; tip: Merge commit '828755101' into lane/kref2 |
| langfix2 | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| langmisc | B-unmerged | 1 commits not in main; tip: langmisc: D27 adversary report + probe evidence (author: lane langmisc, blinded cell; committed by the manager |
| lflaxtri | B-unmerged | 1 commits not in main; tip: lflaxtri: triage of lfl0 test-axes give-ups (report + proposed GIVEUP1_ALLOWANCE Group H diff) |
| lockwait | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| m0build | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| m4 | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| maskbench | B-unmerged | 5 commits not in main; tip: maskbench: timing-1 results, perf tarball, section 6 verdict |
| memfn-r17 | NEVER | kit/self/other-lane |
| memfn-r27 | NEVER | kit/self/other-lane |
| memfn-slot/b3b/reach/wt | NEVER | kit/self/other-lane |
| mptime | B-tracked |  M tests/mech/run_sabotage_matrix.sh; |
| mscomp2 | B-tracked |  D mscomp2_rulings.md; |
| pathreads | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| pathtri | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| pcscope | B-unmerged | 183 commits not in main; tip: pcscope: D161 add. 14 presence/handoff scoping report + census instruments |
| r17a | B-unmerged | 74 commits not in main; tip: r17a: report, lanes index, rank_check CLAUDE.md note |
| r17b2 | B-unmerged | 89 commits not in main; tip: WIP r17b2: MF_SET_BUDGET derived (4 x 787 = 3148), census re-run, §6.2 resolution |
| r17b | B-unmerged | 87 commits not in main; tip: [MEMFN] R17-b: the stateful set find pf_terms_mask, abi 76 -> 77, MF_SITE_ABI 11 -> 12 |
| r17bp3 | B-unmerged | 200 commits not in main; tip: r17bp3: R17-b′ design note REVISION 2 (one window request, 21-row table with slots, step plan B0-B9 with a zer |
| r17bp | B-unmerged | 156 commits not in main; tip: r17bp: R17-b′ design note (D166): the candidate-finder table, the emitted N dispatch, the measurement table, c |
| r17c | B-unmerged | 98 commits not in main; tip: r17c: sabotage rows renumbered S855-S858 -> S867-S870 (main's allocation; S855-S866 are endmark's) |
| r17d | B-unmerged | 120 commits not in main; tip: r17d: report box line |
| r17dry | B-unmerged | 21 commits not in main; tip: r17dry: R-17 rev-2 harness compiled, checked (0 mismatches, planted 152/152, ASan/UBSan clean), dry-run; repor |
| r17e | B-unmerged | 126 commits not in main; tip: memfn: session close — journal, responses notice (R17-b status), wake.md rewritten (slot25 running; make-test  |
| r17loss | B-unmerged | 130 commits not in main; tip: r17loss: R17-b ALPHA loss facts (sets, densities, site counts, fit, predicates) |
| r17r | B-unmerged | 61 commits not in main; tip: r17r23: mark the single-guard name superseded in §3.4a |
| r17rd | B-unmerged | 41 commits not in main; tip: memfn R-17 reading: wording fix |
| r17s | B-unmerged | 5 commits not in main; tip: r17s: R-17 scoping + twin design report, census K35 body count, CLAUDE.md index entries |
| r17upa | B-unmerged | 69 commits not in main; tip: r17upa: uses per activation of R-17's set-FIND sites on the bench's own subjects (counts, reading, report) |
| r26z1 | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| r26zk | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| r27c | B-unmerged | 5 commits not in main; tip: r27c report: 7.8 table/rows/populations now committed (aa388977b) |
| r28 | B-untracked-job | uncommitted job script not in main |
| r28m | B-unmerged | 1 commits not in main; tip: measurement-only merge: lane/dd10 + lane/memfn-r28 (doc conflicts: dd10's side; never merged) |
| r4h | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| regeval2 | B-unmerged | 161 commits not in main; tip: [REGIME-EVAL] rev 1: judge cells streamed, consumer-bound class, P-MOVE, questions resolved |
| regeval3 | B-unmerged | 170 commits not in main; tip: regime_eval rev 2: apply D6 panel r1 (33 ids, all marked [r1 <id>], by-id map in §R) |
| regeval4 | B-unmerged | 173 commits not in main; tip: regime_eval rev 2.1: D166 add. 1 (timing-only CB, perf optional), add. 1.1 (suggest, never act), regime_tables |
| regeval5 | B-unmerged | 177 commits not in main; tip: regime_eval rev 2.2: real J1 population (est 54 RT of 177), corpus caveats, lean two-window plan with power ta |
| regeval6 | B-unmerged | 193 commits not in main; tip: regime_eval rev 2.3: fix a table cell |
| regeval7 | B-unmerged | 194 commits not in main; tip: regime_eval rev 2.4: the evaluator parameter table is a KNOW-SRC kind (evaluator-params); canonical #section f |
| regeval | B-unmerged | 157 commits not in main; tip: [REGIME-EVAL] design note: replay evaluator, fit/judge split, pre-registered loose bars, failing-direction con |
| reqvm0 | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| revbuild | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| revtri | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| rewtwin-scratch | B-unmerged | 2 commits not in main; tip: SCRATCH: twin declines encodings with non-boundary positions (n-W mid-character -> PCREC_ERR_STARTPOS) |
| rq2 | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| rq3 | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| s25alpha | B-unmerged | 129 commits not in main; tip: lanes: s25alpha_report (slot25 alpha check red: hex-dash is an offset-set site, not a mover) |
| s25btip | B-unmerged | 127 commits not in main; tip: s25b: report (KREF2, the 86-pattern equality, the amended judges and their controls, slot25b/run.sh's stages,  |
| s25bv | B-unmerged | 128 commits not in main; tip: [s25bv] slot25b VJUDGE RED triaged: engine-resolution + deny-attribution judge amendments, offline re-judge GR |
| s25mech | B-unmerged | 130 commits not in main; tip: s25mech: report gains main's full-mech baseline and the on-main@657d4fd0f column; reruns re-armed |
| s25tri | B-unmerged | 125 commits not in main; tip: s25tri: fallback-table expectations take R17-c's drop-kit-bytes tail (slot25 red) |
| s25trim | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| s3 | B-unmerged | 16 commits not in main; tip: s3: report part 7 (the code review r1 C1 build: S3 commit b5b85aeac); history index |
| s3fix | B-unmerged | 40 commits not in main; tip: s3fix: s3_report.md Part 11 (the final review fixes: inventory, EMIT-1 design and instruction counts, the rena |
| s3pair | B-unmerged | 29 commits not in main; tip: s3pair: report part 10 (merge main 0d3765c87, abi 85, light suites, job 620) |
| sanred | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| sbscope | B-unmerged | 183 commits not in main; tip: sbscope: D161 add. 14 scoping report + census (single-byte FIND into the kit) |
| scandog | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| scanset | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| setdig | B-unmerged | 2 commits not in main; tip: memfn journal: Frank's E8 go, minimal scope |
| stopstudy | B-unmerged | 4 commits not in main; tip: stop_ranking_study: §5.1 pricing acceptance witnesses (Frank 2026-10-24: set-stop wart + dense hex), desk read |
| streamdes | B-unmerged | 8 commits not in main; tip: streamr2: report round 2 (STATE AT HANDOFF, probe (3) verdict) + lanes index |
| subst | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| substcase | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| substext | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| substland | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| substuc | B-unmerged | 2 commits not in main; tip: substfit: review r3, subst design rev 4b (f18336ee1) against the 29 blind use cases: 10 FITS / 15 FWF / 4 GAP  |
| subtri | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| suitetri | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| sweeppins | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| vb-9950aa672 | B-untracked-job | uncommitted job script not in main |
| vecspike2 | B-unmerged | 131 commits not in main; tip: vecspike2: multi-position class filter for dfa-hat (P2/P3/P4/P3W x w8/SSE2/AVX2): checks green, 8/8 plants det |
| vecspike | B-unmerged | 129 commits not in main; tip: vecspike: checker, plants, time.sh (dry-run), counters, report |
| wingame2 | B-tracked | M  docs/design/memfn/CLAUDE.md;AA docs/design/memfn/window_search_game.md;AA docs/design/memfn/window_search_g |
| winreq | B-unmerged | 189 commits not in main; tip: winreq: Q-WR-7 recorded as ruled (libc-free sites are future-deny work, not a blocker) |
| wsc1 | B-tracked |  M docs/dev/history/claude_md/docs__dev__lanes.md; M docs/dev/lanes/wsc1_report.md; M memfn/docs/journal.md; |
| wsc2 | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| wsc3 | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| wsc4 | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| wsc6 | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| wsc7 | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| wsmain | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |
| wtclean | NEVER | kit/self/other-lane |
| z2build | A | merged; dirt = artifact_size_log.tsv rewrite and/or untracked rulings/deliver/log/scratch |

Unmanaged dirs (c): iterd27-cell, substd27-cell (branches iterd27, substd27 merged into main), mechpar-scratch, revpred-scratch (lane/mechpar, lane/revpred merged, reports exist): REMOVE by name. Left: g2u-cell (lane is kit-side, merged into lane/memfn-g2floor not main), langmisc-cell (worktree langmisc has 1 unmerged commit), streamcrit1-scratch (no lane branch or report found), memfn-slot (kit's).
