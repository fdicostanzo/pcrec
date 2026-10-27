# sanred2: san coverage and one CLI cleanup path

## Summary

All three parts done; nothing changes a message, an exit code or what is
accepted (the stop rule did not fire). Commit 16dc3272e on lane/sanred:
`tests/callouts/run_callouts_tests.sh` joins `tests/lib/san_scripts.txt` and
ran clean under the san env; [TT-9] now counts every `tests/**/run_*.sh`
against the manifest plus a new reasoned exclusion file; `main` has one
cleanup path. `make strict` clean; `tests/codegen/run_codegen_tests.sh`
331 passed / 0 failed; `tests/cli/run_cli_tests.sh` green plain and under san.

## San coverage

- `run_callouts_tests.sh` already built everything with `$GENCFLAGS`, so it
  needed no change. Run once in the worktree's `build-san` (address,
  undefined, leak; PROCS=4, 1500 s timeout) with the `SAN_ENV` values: rc 0,
  101 checks and 120 advice checks passed, zero `runtime error`, zero
  AddressSanitizer or LeakSanitizer lines. No findings. It is slow under san
  (the generated differential alone is several minutes); `make san` carries
  that.
- [TT-9] (`tests/codegen/run_codegen_tests.sh`): the population widens from
  `run_*_diff.sh` (9) to every `tests/**/run_*.sh` (157). New
  `tests/lib/san_excluded.txt` is `PATH<TAB>REASON`, one line per script. The
  check fails on a script in neither file, in both, an exclusion with no
  reason, or one naming no script; floor 100. Negative control: the same audit
  function runs over a synthetic tree in the WORKDIR with five planted defects
  and the check goes red unless all five are flagged.
- The population gap, recorded not fixed: 117 scripts are excluded. 22 are
  `TODO-WIRE` (take `$GENCFLAGS` but are absent from the manifest, e.g.
  `tests/clskit`, `tests/codegen/run_clspack.sh`, `run_search_pinned.sh`,
  `tests/counterk/run_counterkdiff.sh`, `tests/mrl/run_mrldiff.sh`,
  `tests/prefilter`, `tests/subst/run_subst_tests.sh`,
  `tests/thread/run_stackdepth_tests.sh`, `tests/registry/run_pc4.sh`; the
  full list is `grep TODO-WIRE tests/lib/san_excluded.txt`). 48 are
  `DEFER-PLAIN` (plain `$CC`, compiler axis only), 20 NO-C-RUN, 24 OWN-TIER,
  3 NOT-A-SUITE. The prefix assignment is MECHANICAL (a grep for
  `GENCFLAGS` and compiler tokens; memfn and a few named tiers by name), not a
  per-script review: treat the reasons as a first classification for the
  manager to triage. The `TODO-WIRE` list is the open item.

## Cleanup path

`cli/main.c`: `main` parses, calls the new `static cli_run` (the old body of
`main`, taking the parsed state by value) and frees `st.libdirs`,
`st.callouts`, `st.files` and the `--pattern-esc` arena once after it returns.
Every other `free(st.libdirs|callouts|files)` in `main` and in `cli_dispatch`
is gone (about 40 sites), so `--help`, `--version`, refusals, queries and
compiles share one path. `apply_target`'s frees of its own local state `ts`
are unchanged. Control: the pre-change `main.c`, built with the same
sanitizers, leaks on `--callout 13:consume --help` (LeakSanitizer, rc 1); the
new one is rc 0 and clean, as is `-I x --help`.

## Tests

`tests/cli/run_cli_tests.sh`: `--callout 13:consume --help`, `-I x --help`,
`--callout 13:consume -I x --version` (rc 0, stderr empty) and `--version`'s
exact line; the whole script ran green under the san env. Docs:
`docs/testing.md` ([TT-9] paragraph) and `tests/lib/CLAUDE.md` updated. The
manager owes the `make san` re-run.

## STATE AT HANDOFF

Branch lane/sanred, commit 16dc3272e plus this report. Not pushed. Scratch
files are in the worktree's gitignored `build/`. Only single scripts were
run (callouts under san, cli plain and under san, codegen); no box lock taken.

OWED: none
