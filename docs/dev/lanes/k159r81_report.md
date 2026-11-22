# k159r81 report

## Summary
Review r81's FIX-NOW items applied on lane/k159r81 (from lane/k159k37 8174baa29) and its two PLAN items filed. No emitted byte moves: the only C change is one comment sentence in src/facts/kset.c. `make -s strict` green; `run_facts_checks.sh` rc 0 with the new row; the K37 section green (1629 sites, one more than before: the new bounded-witness loop, guarded by `$TIMEOUT_BIN`); `make -s test-plan-lint` green (398 rows, 0 violations).

## Fixes
- CHECK-1: new check `[facts-width-bounded]` (tests/codegen/run_facts_checks.sh, section 9c, beside `[facts-width-cpu]`): `(?:a|bb)c` [2,3], `a{0,30}b` [1,31], `(?:ab){2,5}c` [5,11]. Values derived by hand and CONFIRMED identical on BASE main 92f5e77b6 (a `git archive` build in scratch) and on this build. A REACH line counts the 3 witnesses.
- CHECK-1 sabotage: tests/mech/sabotages/S3541_width_walk_subset_stop.sh plants the coordinator's V1 (`if (w.ncur == nck)` becomes `if (nck >= 0)`, a subset test). Catchers: `[facts-width-bounded]` only (by the review's plant data, [facts-sl1]'s 15 rows and the unbounded `[facts-width-cpu]` witness both stay green under V1). The mech job is queued and owed (STATE AT HANDOFF). ID NOTE: I used S3541, not S3540: worktrees/.mgr/sabotage_ids.txt grants S3540-S3544 to the kit's bsu4fix AND S3540-S3541 to this lane (overlap, as with S3505 earlier); S3541 is in both grants, S3540 is a collision risk.
- SOUNDNESS-1: src/facts/kset.c comment on `pcrec_width_walk` now says `w.cur` is duplicate-free (`wpush` admits a state once per generation across both closure phases), so equal size plus every member stamped IS set equality.
- CHECK-2: the guard's watchdog call has `-m 1g` (measured RSS 52 MB, about 20x headroom), still ONE line with `"$PCREC"` (K37).
- CHECK-3: guard comment re-measured: the fixed d=14 compile is 0.04 to 0.09 s CPU in 6 runs, 52 MB RSS; the old "0.07 s / 70x" figure is replaced by "18x the worst measured (0.28 s, review r81), 50x the lightest". `scripts/loadshame` never read QUIET (load1 5.8 to 7.2, busy-cores 0.28 to 5.8, part phantom iowait), so the figures are stated as measured under load, not quiet.
- K159 in docs/dev/known_issues.md: one line that acyclic and late-cycle families (`q(?:a|bc){N}`, x4 per doubling, identical on BASE) stay quadratic, pointing at [WIDTH-PATH-BOUND].

## Filings
- [WIDTH-PATH-BOUND] (plan.md Candidates, STATE:not-started): COMPLEXITY-1 general form (BFS for bmin, SCC condensation + longest path for bmax, O(n+edges)), flagged as TIGHTER where a live cycle cannot reach accept (an answer change for the width fact, needs its own design); trigger per D77; r81 COMPLEXITY-3's unlocks in refs.
- K160 (docs/dev/known_issues.md, OPEN) + [K160-ALTNF-CUBIC] (plan.md Candidates): COMPLEXITY-2, `pcrec_altnf` class fold about cubic in single-character alternatives (0.61/3.38/24.2 s at 2000/4000/8000, `-e utf8`), `PCREC_MAX_ALTNF_WORK` does not bind (K35 shape: the budget misses its dominant term); SUSPECTED cause marked (altnf.c:401-403 hash re-read inside the sweep :421-430, `anf_cls_union` over a growing list); waits for the owner's fix go (growth-time-bound); next names the [GROWTH-SWEEP] char-list alternation cell. The [GROWTH-SWEEP] row itself is not edited (the cell is named in K160's `next`).
- plan.md PL10 allows one status and either next or trigger per row, so the extra text sits in refs/status; both rows are under the PL10 300-char field limit, no body file.
- The review file docs/dev/reviews/2026-11-22-r81-k159fix.md is on main, not on this branch (cut earlier); the rows cite it by path.

## STATE AT HANDOFF
Last ruling applied: none (k159r81_rulings.md empty, re-read before commit and report).
Commits: f77aeff78 (fixes + filings), 74bbac84b (comment figures), plus this report.
OWED: mech job key `200-k159r81-mech` (S3541, expect rows=1 `== mech run COMPLETE`; DETECTED expected; verdict via scripts/monread). Cloud test: see below.
Cloud test: ref 8bc950eab58dfef9bdbb05ab37193da8d06dcd30 pushed as cloud/main/test/8bc950eab58dfef9bdbb05ab37193da8d06dcd30-8bc950e (owner=main kind=test; proven by `git ls-remote origin 'refs/heads/cloud/main/test/8bc950eab*'`; the brief's `*/k159r81*` glob cannot match because cloudrun names the ref by sha; verdict via queuewatch as CLOUD-DONE, not awaited).
