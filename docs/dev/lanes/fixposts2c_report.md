# fixposts2c report (sonnet, 2026-11-15)

## STATE AT HANDOFF
Branch lane/fixposts2; fix commit e068c0004 (this report's commit sits on top). Rulings file fixposts2c_rulings.md was empty at every checkpoint; no R-n applied. Items 1-3 of the audit done; items 4-5 OWED (below).
Job keys: local box job `702-main-fixposts2c-memarm` (owner main, `MEMFN_REACH_ONLY=1 bash tests/axes/run_axes.sh` in the worktree, --ready exits 75 in 20:00-01:00). Cloud runs: names `fixposts2c-mr` (kind mechrows, rows S3012,S474) and `fixposts2c-axes` (kind axes), owner main, ref = this report's commit.

## FIXES
- Audit item 1 (FIXED): `tests/axes/run_axes.sh` restore-arm derivation used bare `gcc` twice. Both now use the resolved `"$CC"`; the row count no longer uses `-fpreprocessed -dD` (`"$CC" -E -P -x c FILE | grep -o WALK_ARM | grep -c .`: WALK_ARM is left undefined, so the preprocessor strips comments and passes the rows through as text, on gcc and clang alike).
- Audit item 2 (FIXED): `tests/axes/memfn_arm.py` precheck-assign-byte floors (default and simd) 130/185 -> 122/176 (byte/utf8 c-default), the corpus= values in /var/tmp/pcrec-pcrec/scratch/fixposts2b/job701.log lines 27, 29, 31, 33; cause (FLOORS-3 corpus-only counting over old corpus+witness totals) in a RE-PINNED comment line.
- Audit item 3 (FIXED): run-verify-wide floors 58/117/99/181 -> 72/134/113/198 (job701.log lines 43-50, corpus= column, both layers identical); cause (rule (1) alt_union ON, 13f46ea50, added movers) in a RE-PINNED comment line.
- FLOORS-3's corpus-only counting not reverted. Nothing under src/, cli/, lib/, memfn/ touched.

## VALIDATION
- Premise: `grep -n fpreprocessed tests/axes/run_axes.sh` hit line 1789 before the fix; job701.log holds corpus 122/176 and 72/134/113/198 as the audit quotes.
- Derivation block (the lines from `WALK_ARMS_DEF=` through `INTERNAL_ARMS+=("--harness=no-min-width")`, extracted to scratch/fixposts2c/blk.sh and sourced with ROOT_DIR=the worktree): CC=gcc gives read=5 rows=5 INTERNAL_ARMS=7 entries; CC=clang gives read=5 rows=5, 7 entries. Both pass the FATAL check.
- `python3 -I -m py_compile tests/axes/memfn_arm.py` ok; pre-commit staged checks 52 passed, 0 failed.
- Not run locally: the full axes suite and the memarm re-measure (queued).

## OWED
- `702-main-fixposts2c-memarm` (audit item 4): must come green; read its job dir under worktrees/.boxqueue.
- Cloud mechrows S3012 and S474 on the new tip (audit item 5): `fixposts2c-mr`.
- Cloud axes on the new tip: `fixposts2c-axes` (the first gate that runs the INTERNAL_ARMS block under the cloud's compiler).
