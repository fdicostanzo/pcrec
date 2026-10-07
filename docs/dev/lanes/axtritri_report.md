# axtritri — triage of the axtri Linux `make test` red

Lane `axtritri` (TRIAGE) on `lane/axtri` (9c2891f0). Input: the Linux full
`make test` in `/home/duxevents/pcrec/worktrees/axtri-lx` (`test.log`):
rc=2, `make[1]: *** [Makefile:474: test-rxtsource] Error 1` and
`[Makefile:1290: test-clskit] Error 1`.

Verdict: both reds are TRANSIENT BOX-STATE FAILURES, not axtri's. No code
change was needed; none was made.

## test-rxtsource (Makefile:474), `checks failed: 1`

- Check: `W23-S7 corpus control: entry files: ? (wanted 272), fragments
  spliced: ? (wanted 0)`. Cause line: `pcrec --list-source failed on this
  head-bearing file` for the five `tests/findings/golden/*.rxt`, e.g.
  `'bigram' is not a analysis-bundle directive` (line 41) and
  `[schema-constraint] ... a provenance reco...`.
- Cause: the `build/pcrec` the section ran did not know the findings
  vocabulary the tree's `src/core/findings.c` carries (`bigram`). The file
  `build/pcrec` in that worktree is stamped 00:52, 26 min after the
  worktree's HEAD commit (00:26), i.e. it was rebuilt during/after the
  run window; the load average was 21-25 (the 15-min figure) while the
  suite ran. The binary the check saw was not the tree's. Not related to
  `outcome_word.h` or `GIVEUP1_ALLOWANCE` (neither touches findings
  parsing).
- Class: transient (stale/concurrent binary), not a regression, not a
  pin.
- Re-validation: `make test-rxtsource` alone on the Linux worktree,
  gnutimeout, load ~1.5: `checks passed: 280, checks failed: 0`, INV-COMPAT
  over 272 files / 4606 blocks. rc=0 (no `*** [test-` line).

## test-clskit (Makefile:1290), `checks failed: 2`

- Checks: `FAIL: differential: chunk(s) failed to build or run:
  chunk_051.log chunk_075.log` and `FAIL: differential: 520 sets checked of
  591 in the population` (the second is the first's consequence).
- Cause: `watchdog: clskit chunk_051.c: wall timeout after 10s`, same for
  chunk_075, with `RUNFAIL ... rc=0` and peak rss ~1.9 MB: the two
  chunks hit the 10 s per-chunk wall under the box's load (load average
  ~21-25 during the run), not a wrong answer. The same section's other
  329 chunks, the composition law, the crosscheck and compile-CPU budget
  (max 1.38 s/unit) were green.
- Class: transient load flake, not a regression, not a pin. (The 10 s
  wall is a tight constant on a loaded box; worth a separate look only if
  it recurs on an idle box. No row filed.)
- Re-validation: `make test-clskit` alone on the Linux worktree, load
  ~1.5: all 331 chunks built and ran, `0 mismatches` over 8,451,676,390
  code-point checks, `checks passed: 5, checks failed: 0`. rc=0.

## Evidence summary

| section | full run (loaded) | targeted re-run (idle) |
|---|---|---|
| test-rxtsource | red (1) | green (280/0) |
| test-clskit | red (2) | green (5/0) |

Not done, by design: no Mac re-run (no fix was made, so there is nothing
to re-validate there); no main-at-81bc13de comparison (the identical tree
passes both sections, which settles it). Linux scratch files `rxs.log`,
`cls.log` are in the `axtri-lx` worktree (untracked, not committed).
