# covs2gtri — triage of the red cloud test run covs2g-test (2026-11-16, opus)

## STATE AT HANDOFF

STATE: done. One red, class (b), fixed in d60241110 on lane/covs2gtri
(cut from lane/covs2b @ d5016fdc8). Rulings file: empty (no R-n applied).
OWED: none (box queue). Cloud runs dispatched on the tip are listed below;
their verdicts are the manager's to read.

## THE FAILURE

GitHub Actions run 43995673790, branch cloud/main/test/covs2g-test, sha
d5016fdc88e3, conclusion failure (premise confirmed via `gh run view
--json conclusion,headSha`). `--json jobs`: every job ran (no log-less
dead runner); 17 of 18 shards green, shard 5/18 red ("Run the shard"),
`gather` red on it. The verdict lines (`gather` job, the only failed-log
source; the per-job shard log came back empty from `gh`):

    RED:   shard 5/18: FAIL: [K37] 1 site(s) invoke the compiler with NO bound (no pcrec_run/$TIMEOUT_BIN/gen_run/gen_cc on the line) and match no allowlist reason ...
    RED:   shard 5/18: make[1]: *** [Makefile:737: test-codegen] Error 1
    RED:   shard 5/18: make: *** [Makefile:557: test-shard] Error 1

No other `*** [... test-X] Error` line in the run.

## CAUSE

Class (b), a defect in covs2g's new test material. The K37 sweep in
`tests/codegen/run_codegen_tests.sh` (the bare-compiler-call check) was
reproduced locally with its own regexes and allowlist copied verbatim out
of the file; it names exactly one site:

    tests/axes/run_axes.sh:1952:    _wsw_ceil="$("$PCREC" --list-limits 2>/dev/null | awk ...)"

That line is covs2g's new test-axes width arm (f0e88611b), which reads
PCREC_ANCHORED_MAX_STATES from `--list-limits` with an unbounded compiler
call. Every other compiler call in run_axes.sh carries `"$TIMEOUT_BIN" 60`
(lines 336, 1295, 1304, 1982). Not a product defect, not infrastructure, and
not the COVER-SIZE-LADDER finding.

## FIX

d60241110: the line now reads `"$TIMEOUT_BIN" 60 "$PCREC" --list-limits`,
the file's own idiom (`TIMEOUT_BIN` comes from `tests/lib/gen_timeout.sh`,
sourced at run_axes.sh:209). No allowlist row was added, no check was
changed, no product file was touched, no emitted byte moved.

## VALIDATION

- K37 sweep reproduction (the block's regexes + allowlist extracted from
  run_codegen_tests.sh by line range): 1 bad site before the fix, 0 after.
- `bash -n tests/axes/run_axes.sh`: clean.
- The fixed line run against this tip's `build/pcrec` (plain `make`, rc 0)
  with gen_timeout.sh sourced: TIMEOUT_BIN=/usr/bin/gnutimeout, ceiling read
  as 4096 (so the arm's width is still 4095).
- The file the suite runs, `tests/codegen/run_codegen_tests.sh`, alone under
  `scripts/watchdog -s 900 -m 8g -c 1800 -S covs2gtri -- nice -n 19 env
  PROCS=4 ...`: rc 0, checks passed 347, failed 0; `PASS: [K37] every
  compiler invocation in tests/**/*.sh (1598 site(s) across 666 script(s))
  is bounded (873 guarded directly) or is a reasoned allowlist exception
  (594, across 13 categories, all non-vacuous)`. (The other two
  test-codegen scripts, run_dfa_stamps.sh and run_trie_identity.sh, were not
  run; nothing they read changed.)
- No suite, no make test, no mech/sanitizer/axes locally (evening hold).

## CLOUD RUNS DISPATCHED

- `covs2gtri-test` (kind test, ref lane/covs2gtri): the owed re-run of the
  red kind.
- `covs2gtri-axes` (kind axes, ref lane/covs2gtri): the fix edits
  tests/axes/run_axes.sh, which the axes kind runs; the in-flight
  covs2g-axes ran the pre-fix file (behaviourally the same line, so its
  verdict still stands for answers, but the tip deserves its own run).
- Not re-dispatched: mechrows and asan (no sabotage row, san_scripts list
  or shard table changed).

## LEFT OPEN

- The width arm runs at width 4095 with `lost_ok` 0, and its own comment
  says the r27 READ-3 code-size refusal at 4095 "is not allowed for". If
  any corpus pattern reaches that cap, covs2g-axes / covs2gtri-axes go red
  as LOST: that would be the known COVER-SIZE-LADDER finding surfacing
  through the arm, not a defect of this fix. Not touched here.
- `gh run view --job <id> --log` for shard 5 returned an empty log; the
  diagnosis rests on the gather job's quoted lines plus the local
  reproduction.
