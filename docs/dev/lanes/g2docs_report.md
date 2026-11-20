# g2docs report (2026-11-20)

## Summary
- scripts/perfrun default wall cap 3600 -> 5000 (plus the two stale 2700 readers in docs/dev/ttune_measurement.md).
- docs/testing.md: new current `test-memfn-g2` bullet (1004 s alone, top units, make test j2p8 totals); the 52-62 s Mac figure is kept but marked STALE.
- Growth: facts only. The only per-unit data on 11-20 is one run; the window unit (`win`) is the one that grew out of proportion (54 -> 79 -> 288 s declared/measured at different dates and shapes); every other big unit is ~1.7-2.3x its 11-11 weight.

## perfrun default
- scripts/perfrun lines 9, 16, 74 (`tmo=5000`; header and `--timeout` usage line). `bash -n` ok.
- docs/dev/ttune_measurement.md lines 20 and 55 quoted `gnutimeout 2700` / "2700 s cap": now 5000.
- No other reader quotes 3600/2700 as perfrun's default (grep of scripts, docs/testing.md, RUNS.md, .claude/skills, INDEX.md, scripts/CLAUDE.md). Lane reports passing `--timeout N` explicitly are unaffected.
- Reason: a make test under the j2p8 shape measured 2677-2850 s and a contended run hit 3600 (job 200-main-l3fix-test2, rc 124); test-memfn-g2 grew. A timeout is a crash (owner ruling), so the cap sits above the real runtime with margin.

## testing.md runtime
- Source: job 205-g2tri-g2alone (script /var/tmp/pcrec-pcrec/scratch/g2tri/g2alone.job): `make -j4 all` t0..t1 = 6 s, `make test-memfn-g2` t1..t2 = 1795206026-1795205028 = 998 s by the t files . 29 units, per-unit seconds in units.out sum to 1791 s (concurrent units, so sum > wall).
- Top units (s): win 288, gcc 132, asan 93, w2-3 80, w2-1 77, w1w3 77, mfind 76.
- Section readings in the four .s files: 470.6 (20261109 u2_j2p8), 614.9 (20261112 k382 j8p2), 829.8 (20261119 c4fix j4p3), 960.2 (20261120 k146land j2p8).
- make test total at j2p8: 2677 s (job 202-main-k146land-test2), ~45-48 min quiet box. The existing Mac "~100-105 min" statements were left (Mac).
- Note: the t files give 998 s for the g2 phase and 1004 s including the build; the brief's 1004 s is written as "wall".

## Which kit family grew
Sources: units.out (11-20, g2 alone); memfn/tests/g2_units.tsv (weights, 11-11 job 561 N=4 loaded box; its own history); the .s files give only the section total (no per-unit data), so they cannot say which unit grew.
- Section total 470.6 s (11-09) -> 960.2 s (11-20), x2.04 (different tree states and make shapes: not one variable).
- Window family (`win`, run_g2_win.sh): weight 54 s (11-11, job 561) -> 79 s (fc8d0ef4e, 11-17: "measured 103 s -> 151 s" alone niced) -> 288 s in units.out (11-20). Largest unit and the largest relative growth (x5.3 vs the 11-11 weight). docs/testing.md line ~1075 states the cover-cap line (2026-11-19) grew the window family.
- Others vs 11-11 weights: gcc 81 -> 132, asan 46 -> 93, w1w3 41 -> 77, w2-1 34 -> 77, w2-3 30 -> 80 (x1.6-2.7; conditions differ: job 561 was in a 4-way split on a loaded box, 11-20 is one 4-job run).
- mfind (11-14 commit 9acabc756 says 73 s) -> 76 s: flat.
- Commits since 2026-11-09 touching the G2 driver / window family: fac1dc6b0 (11-12, traced window-family pass, G2W_TRACE), 4a5bd7ee7 (11-13, wide G2 stream), df3aa9db4 and 5e9139be3 (11-13 partd window floors / rows unit), fda73b5c9 (11-14, mfind family, section 4z), c0d03366f / d1a14b676 (11-15 mfindfix2 site shapes), fc8d0ef4e (11-17, win reweigh), 7cc686792 (11-15, mfind lever witness 28 -> 32 sets, COVER-CAP). I did not attribute seconds to individual commits: no per-unit measurement exists between them.

## STATE AT HANDOFF
- Last ruling applied: none (g2docs_rulings.md empty).
- Files: scripts/perfrun, docs/dev/ttune_measurement.md, docs/testing.md, this report.
- Checks run: bash -n scripts/perfrun; see commit for lanecheck.
OWED: none
