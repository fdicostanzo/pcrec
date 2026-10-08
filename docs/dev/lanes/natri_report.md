# natri — triage of nullanch2's two `make test` reds (2026-10-08)

Chain verdict: build/land/verdict.txt at tip b88a139e (abi 68). Reds:
`test-registry` (Makefile:455) and `test-rxtsource` (Makefile:481). Both were
stale pins moved by the declared change; no defect, nothing loosened.

## test-registry — stale allowlist, one row

- Failing check: `limits_check.sh` 3a, `src/facts/widths.c:78`
  `#define EM_ANY (1u << EM_NONE)` — "numeric constant outside limits.def and
  on NEITHER allowlist" (36 of 37 checks passed; the other 36 incl.
  definitions tables/oracle were green).
- Class: legitimately moved. 9a0cf78e / the E1 fact `empty_admits` introduced
  the mask-set identity `EM_ANY`; it is a bit-set value forced by the
  representation, the same kind as `SA_BOT`/`SA_GSTART` (not a bound).
- Fix: `EM_ANY` added to NONLIMIT_ALLOWLIST with its reason in the kind-6
  comment. The scan itself is untouched, and the `[code-reach]` check still
  proves the entry is reached. The alternative (rewriting widths.c) would move
  a src commit and the recursion identity gate's (B) FILEPIN for no gain.

## test-rxtsource — stale census pins for the new corpus file

- Failing checks (11): census MOVED (found 276/5423/52022, pinned
  275/5416/51960), file list, C1 legs A/B/C block rows, case-row derivation,
  C3 files/population/invariant pins/reconcile, W23-S7 control.
- Class: legitimately moved by `tests/base/nullable_anch.rxt` (+1 file, +7
  blocks, +62 case lines; 8 `# pcre2-only` blocks per grep, 23 pcre2-only
  cells, 39 python-verified cells). Deltas are the harness's own measured
  numbers (the FAIL lines), not derived from the lane's claim.
- Re-pinned in run_rxtsource_tests.sh: CENSUS_FILES 275->276, CENSUS_BLOCKS
  5416->5423, CENSUS_LINES 51960->52022; RUNSH_FILES 251->252, RUNSH_BLOCKS
  and RUNSH_LINES the SAME delta (the file is neither known_fail nor
  findings); C3_PASS 17235->17274, C3_SKIP 34639->34662, C3_SKIP_PCRE2ONLY
  17563->17586, C3_VERIFIABLE 19365->19404. C3 reconciles:
  17274 + 34662 - 3 + 89 = 52022.
- The five `tests/findings/golden/*.rxt` "HARNESS FAILURE / bigram is not a
  directive" lines in the chain log did NOT recur in the re-run (all 268 ->
  green, INV-COMPAT holds over 276/5423/52022); they were a consequence of
  the W23-S7/C1 leg on the old pins' run and the files are unchanged on the
  branch (`git diff main...HEAD -- tests/findings` empty). Cause of the
  chain-time lines not established beyond that; flagging, not explaining.

## Re-run
`make -j6 test-registry test-rxtsource` in worktrees/nullanch2: rc 0, every
section `checks failed: 0` (registry limits 37/37, rxtsource all green).
`test-codegen` not re-run: nothing it reads was touched (only tests/registry
and tests/rxtsource scripts).
