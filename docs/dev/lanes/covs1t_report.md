# covs1t report: triage of the red box job covs1-sections

## STATE AT HANDOFF
Rulings file covs1t_rulings.md: empty, last R-n applied: none. Branch lane/covs1, fixes committed (see FIXES). Re-queued: covs1-sections (boxqueue retry); the waiting covs1-cloud keeps its key. NOT triaged (outside the brief): covs1-sweep also FAILED (rc=2, FAILED-FAST in 0s, "an invocation error?"), which blocks covs1-predict.

## CAUSE
Of the 13 sections only test-startset was red (`*** [Makefile:1708: test-startset] Error 1`), one check: `[dfa-movers] 0 not in the manifest, 6 manifest rows not movers`. Class: STALE PIN, not a regression. The six rows (tests/possessify/composition_d27.rxt:1733, 2003, 3083, 3398, 9936, 10135, e.g. `[a-c]*\ba`, `\d{0,}?\B-`, `a*\bA`) were unanchored-DFA hat movers; the exact-stretch cover now admits them (`RX_DFA_SCAN "cover"` in the lane build, `unanchored`/`landmark-walk` before), so they have no scan and no hat. These are among the 18 gained covers. The same shape as the s3fix600 removal of 25 rows. No mover joined.

Stray files: tests/kitproof/reach.sh wrote `${REACH_TMP:-.}/kitproof_reach.c` (the harness also writes the .h beside it), so any run without REACH_TMP set (a hand run of the probe, e.g. for `cat$`) dropped both files into the invoking directory (the main tree root).

## FIXES
- tests/startset/manifests/manifest_s3_dfa.tsv: the six rows removed, one provenance comment added. test-startset re-run on the worktree: 35+3+22+35 checks passed, 0 failed, no `*** [` lines.
- tests/kitproof/reach.sh: without REACH_TMP the probe uses a private mktemp dir under the temp root, removed on exit. Verified: a bare run from another directory leaves nothing behind.
No allowlist row was added to a check (the manifest is a pin; `git log --since=14.days` of it shows no earlier row for this cause). abi stays 108.

## OWED RUNS
covs1-sections re-queued (`boxqueue retry covs1-sections`); covs1-cloud (waits on it) should become ready; the other 12 sections were green in the failed run. The two stray files in the main tree root are for the manager to delete.
