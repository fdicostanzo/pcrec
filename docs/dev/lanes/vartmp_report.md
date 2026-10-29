# vartmp report (lane vartmp, sonnet, 2026-10-28)

## Summary
All pcrec temporary files now go under one per-user root on disk,
`$PCREC_TMPDIR` (default `/var/tmp/pcrec-<user>`), defined once in
`scripts/tmpdir.sh`. The Makefile exports `TMPDIR` to it for every recipe; the
run-control scripts source the helper; the queue runner prunes the root at each
job start. No `src/`, `cli/`, `lib/` file writes a temp file (nothing found;
the STOP RULE did not fire). No abi, no emitted-text change.

## Temp root
- `scripts/tmpdir.sh` (POSIX sh): sourced it sets+exports `PCREC_TMPDIR`
  (default `/var/tmp/pcrec-$(id -un)`, `mkdir` under umask 077 = 0700) and
  forces `TMPDIR` to it; executed with `--print` it prints the root (the
  Makefile uses this: `PCREC_TMPDIR := $(shell sh .../scripts/tmpdir.sh --print)`,
  `TMPDIR := $(PCREC_TMPDIR)`, both exported; a make-file assignment beats the
  environment, so a caller's `TMPDIR=/tmp` does not win; the override is
  `PCREC_TMPDIR`). I put it in scripts/ (not tests/lib/) so its self-test
  `scripts/tests/tmpdir.sh.test` is found by scripts/Makefile's wildcard.

## Writers moved
- Makefile: 2 `mktemp` fallbacks `${TMPDIR:-/tmp}` -> `${TMPDIR}`; 17 recipe
  `TMPDIR=$${TMPDIR:-/var/tmp}` prefixes removed (now redundant: exported).
- scripts/boxqueue, chainrun, battery.sh, fullsuite_job.sh, measure.sh: source
  the helper (measure.sh's hard-coded `/var/tmp` mktemp + `TMPDIR=/var/tmp` gone).
- tests/recursion/gen_corpus.py and tests/lookaround/d27/checker.py: hard-coded
  `/tmp/claude-1001/-home-duxevents-...` scratchpad paths (another box's
  session dirs) -> `$TMPDIR/scratch/{srCorpus,la27}` (python fallback `/var/tmp`).
- Docs: docs/testing.md ("Where temporary files go"), BOILERPLATE.md, both
  skills (critic: `$PCREC_TMPDIR/scratch/crit-<topic>/`; manager), root
  CLAUDE.md MANDATE clause, scripts/CLAUDE.md, scripts/tests/CLAUDE.md.

## Writers left
- ~120 suite scripts/self-tests with the form `mktemp -d "${TMPDIR:-/tmp}/x.XXXXXX"`
  (or `:-/var/tmp`): under make and under every sourcing entry point TMPDIR is
  set, so the fallback never fires; only a hand run with TMPDIR unset reaches
  `/tmp` (export TMPDIR or `. scripts/tmpdir.sh` first; stated in testing.md).
  I did not mass-edit them (a second copy of the default would be needed).
- Comments/usage text mentioning /tmp or /var/tmp (tests/probes/*.c,
  tests/spec_mod0/*.c|h, compile_time_census.py usage, lanecheck, startset,
  rxtsource, axes, resource, codegen/run_object_neutrality.sh, tests/*.md):
  docs only. docs/design/**, studies/: archival, untouched. memfn/: no edit
  needed (its tests use `${TMPDIR:-...}` mktemp).
- Claude Code's own `/tmp/claude-1001` task files: not ours.

Population (`grep -rnE "(^|[^A-Za-z_])/(var/)?tmp/" Makefile scripts tests tools | grep -v ^docs | wc -l`):
before 48 (Makefile 1, compile_time_census.py 3, measure.sh 1, lanecheck 1,
recursion 2, startset 1, probes+spec_mod0+others comments, md files); after 52:
the 4 net-new are the helper's own default/comments and its self-test.
Hard-coded WRITERS in that set: 5 before (measure.sh x2, gen_corpus.py,
checker.py, Makefile mktemp fallbacks counted separately) -> 0 after.

## Prune
`pcrec_tmp_prune` (scripts/tmpdir.sh), called by `boxqueue` `_start` inside the
box lock before the job launches, live queue only (skipped when
PCREC_BOXQUEUE_DIR is set, i.e. self-tests). Candidates: the root's children
and `scratch/`'s children. Kept: anything with a file modified within
`PCREC_TMP_PRUNE_DAYS` (UNMEASURED default 3), any path that is a cwd or open
fd of any readable process (scanned via `find /proc/[0-9]*/cwd /proc/[0-9]*/fd/`;
uutils `readlink` drops multiple operands, so not readlink). The `rm -rf` only
runs on a path under a root that is non-empty, absolute and not `/`.
Self-test (14 checks) covers old/idle, recent, old-with-recent-file, cwd-held,
open-held, outside-root, bad roots; the first run caught the uutils readlink
defect (cwd/open cases failed until switched to find).

## Validation
- `make -j2` ok; `make strict` clean.
- Self-tests: tmpdir.sh 14/14, boxqueue 144/144, chainrun 26/26,
  fullsuite_job.sh 14/14, boxlock 35/35.
- `make test-registry` and `make test-codegen` ran green (no `***` line; codegen
  "run_group: 19/19"; registry definitions-oracle 0 disagreements), with
  TMPDIR=/tmp in the environment. Logs: build/vt_val.log (gitignored).
- Corpus section: there is no `test-base`; ran `TMPDIR=/tmp make test-cli`
  under `strace -f -e openat,mkdir` for 110 s (cut by timeout, all cases shown
  PASSed): 135 creations, all under `/var/tmp/pcrec-pcrec`, 0 under `/tmp/`.
  The `find /tmp -newer` comparison was noisy (other sessions' cc*.o), so the
  strace is the evidence.
- Not run: full make test, battery.sh itself (no self-test; sourcing line only).

## STATE AT HANDOFF
Branch lane/vartmp, all committed. Rulings file vartmp_rulings.md never
existed in the worktree (no entries applied). Owed: none. Manager to queue
make test after merge; note a make test already running from the main tree
still uses `/tmp/pcrec-test-trailer.*` (old Makefile) until it ends.
