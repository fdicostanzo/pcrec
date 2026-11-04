# axtri report: red make test-axes (job 758-fsfix-axes), six form-census floors

Verdict: **a stale-floor / intended-movement case, not a regression, and main is affected identically.**
The kit S3 merge (0f425c2d0, lane memfn-s3m, abi 92) added the scan form `cover`, which takes 884
corpus patterns off `RX_DFA_SCAN "unanchored"`. Its plan listed "CHECK-3 test-axes floors" as OWED and
the form census never ran on main afterwards (journal 2026-10-25: the previous axes job's census did not
run, `&&` chain), so the floors were never re-derived. No answer moved (all 758 axis groups OK, 0 AXIS FAIL).

## Counts (same 5,108-pattern `pattern ` corpus, default engine)

| form | floor | fsfix (758) | main a3cc4de82 | pre-S3 (f3a3d2b7b) | SL2 build (bfe30c75f) |
|---|---|---|---|---|---|
| PREFILTER memchr | 750 | 696 | 696 | 853 | 910 |
| PREFILTER offset-set | 290 | 270 | 270 | 377 | 377 |
| PREFILTER offset-set-bounded | 30 | 20 | 20 | 57 | 57 |
| PREFILTER run-pinned | 100 | 55 | 55 | 134 | 133 |
| PREFILTER run-pinned-bounded | 7 | 3 | 3 | 9 | 9 |
| START end-minus-width | 1200 | 667 | 667 | 1509 | 1437 |
| SCAN cover (no floor today) | - | 884 | 884 | 0 | 0 |

Main reproduces 758 exactly (also attempt-start 1447, reverse-pass 1296, landing 206, pinned 214), so main
fails the same six floors; fsfix's red is not branch staleness.

## Cause (evidence)

- Bisect over main's first-parent history (849 commits since SL2, a probe compiling the corpus per commit):
  end-minus-width is 1509 through f3a3d2b7b and 667 from the merge **0f425c2d0 "Merge lane/memfn-s3m: kit S3
  (abi 92)"**. (Bisect steps: 635/741/767/780/781 good, 782/783/787/794 bad.)
- Per-pattern A/B f3a3d2b7b vs 0f425c2d0: 884 patterns change, every one to `cover / none / attempt-start`
  (from unanchored with memchr 141, byte-class 306, offset-set 102, run-pinned 74, handoff 63,
  memchr-bounded 64, offset-set-bounded 37, ...; start end-minus-width 833, reverse-pass 21, landing 16).
  Nothing else moves. Hence PREFILTER none 1117 -> 2001 (floor 500, unaffected) and attempt-start up 884.
- Mechanism: `locate_cover_applies` row (`src/gen/emit_dfa.c` ~10208, tok "cover", `.scan = "cover"`).
- Not a measurement artifact: no timeouts in the 758 log (grep timed out/killed/watchdog: none), REFUSED stays
  499 before and after, and an independent probe on main's binary gives 758's numbers to the pattern.
- s3_report.md line 117 says the census population "stays the pre-S3 default build's, so main's floors hold"
  but that is about run_scan_edge_census.sh only, not this census; line 543 lists the test-axes floors as OWED.

## Fix (prepared on lane/axtri, tests/codegen/run_form_census.sh)

Re-pin at ~85% of the measured counts (the file's convention), reason in a new comment block:
memchr 750 -> 590, offset-set 290 -> 230, offset-set-bounded 30 -> 16, run-pinned 100 -> 46,
run-pinned-bounded 7 -> 2, end-minus-width 1200 -> 560, and a NEW floor `RX_DFA_SCAN=cover` 750 (K35:
every reached value gets a floor; today it has none, so a silent loss of the form would pass).
Every new floor is below the measured count by arithmetic (696/270/20/55/3/667/884); `bash -n` clean.

## STATE AT HANDOFF
- Commit on lane/axtri only; main untouched (still a3cc4de82); no rulings file entries read (none existed).
- OWED (not run: the box was held by 697-kit-r30b-heavy and my boxlock'd census sat yielding to queue jobs
  759/760/762; I killed that waiter by safekill rather than leave a stray run): the census itself on the fix.
  Run: `bash scripts/boxlock run --label axtri -- env PROCS=16 bash tests/codegen/run_form_census.sh`
  (~2-3 min of compile, expect `checks failed: 0`). My probe (`$PCREC_TMPDIR/scratch/axtri/probe.sh`) used
  the census's own stamp reads but is not the census; the census run is the authority.
- Manager rules whether to merge the re-pin; also consider that the test-axes `&&` chain skipped the census
  when run_axes fails, so the census can go unrun for weeks (it did here).
