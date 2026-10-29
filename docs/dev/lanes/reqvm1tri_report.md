# reqvm1tri — triage of queue job 630-reqvm1-test's two red sections

## Summary

Job 630 (lane/reqvm1 @c7a821e14) had exactly two red sections, both reproduced
and both class (a): the lane's intended change legitimately moves a pin. No
regression, nothing pre-existing on main (main HEAD 490bc2baf is green on
`test-fallback-table`; `gen_handoff_vm.py` does not exist on main). No src/,
lib/, memfn/ edit and no answer change. Both sections are green now.

## Failure by failure

### 1. test-memfn-arch (Makefile:1396) — class (a), new-file vocabulary hit
- Cause: C4 (arch-blind detector) flagged the NEW lane file
  `tests/litscan/gen_handoff_vm.py` line 6, class 6 (arch-noun): its
  docstring's regeneration command spelled `PCREC_PCRE2_PATH=/usr/lib/x86_64-linux-gnu/libpcre2-8.so.0`.
  `x86_64` is box vocabulary, not a branch on an architecture.
- Main differs: the file is not on main (`git show main:tests/litscan/gen_handoff_vm.py` -> not in 'main');
  its sibling `gen_handoff.py` carries a neutral path.
- Evidence: `make test-memfn-arch` -> `FAIL: NEW architecture vocabulary: tests tests/litscan/gen_handoff_vm.py class 6 ...`; after the fix 17 passed / 0 failed.
- Fix commit: see Fixes (docstring path made neutral, `libpcre2-8.so.0`, as gen_presence_deny.py does; no allowlist row added, so the K35 floor is untouched).

### 2. test-fallback-table (Makefile:854) — class (a), size-cap witness window closed
- Cause: one FAIL of 146: `seq-pfcd2 [trlowsize -e utf8 '(\bcat\b){2,}[a-z]\d']`
  refused (rc 1), expected to compile. The witness lived in a narrow window
  (its own comment: it compiles only if the pre-drop size lies in
  30,000..30,146, the drop saving 146 bytes). The lane's handoff code on the
  VM attempt loop (abi 91) makes the dropped, VM-only artifact LARGER than the
  hybrid: pre-drop record `sc=30089/30000`, after the drop 30,710 bytes of
  code, `refuse@size`. Rows: `prefilter-collapse@size > drop-prefilter@size > refuse@size`.
  The window is empty by construction (a drop that no longer shrinks cannot
  rescue a pattern over the cap). Pre-drop sizes are byte-identical to main
  (30046 / 30089); only the post-drop artifact moved, ~+767 bytes.
- Main: green (146/146) on `git archive main` of 490bc2baf, built and run in scratch;
  the test script is byte-identical on main and lane.
- Brute search: 70 variants of `(\b<w>\b){n,}<tail>` at the lowsize cap found
  none that rows collapse>drop and compiles; the drop-succeeds case remains
  covered by `seq-pfcbcat`.
- Evidence: `make test-fallback-table` (before: 145/1; after: 146/0).
- Behavioural note for the manager (not a test matter): at the real cap,
  patterns whose size-cap drop previously rescued a VM-hybrid compile by a thin
  margin may now refuse at `drop-prefilter`'s result. The lane report records
  the same effect on `(\p{Xwd})x` (hybrid size moves by 952 bytes); a cap-edge
  census of corpus patterns (movers.py, "dropped-hybrid-size") counted 1.

## Fixes
- `tests/litscan/gen_handoff_vm.py:6`: docstring path -> `libpcre2-8.so.0`.
- `tests/codegen/run_fallback_table.sh` seq-pfcd2: RC `ok` -> `refused`, expected
  rows `prefilter-collapse@size > drop-prefilter@size > refuse@size`; comment explains.
  `fstate seq-pfcd2 2 'restart=1'` is kept and passes. No new ids; S1708-S1719 untouched.
  The abi (91), flag bits and spec are unchanged (test-only; no caller-observable change).

## Validation
- `make test-memfn-arch`: 17 passed, 0 failed. `make test-fallback-table`: 146 passed, 0 failed.
- `make strict`: clean. `make test-codegen`: rc 0, no FAIL. `make test-registry`: rc 0, 232 passed / 0 failed.
- Full `make test` not run (manager re-queues 630). The suites rewrote the tracked
  docs/dev/artifact_size_log.tsv; it was restored (`git checkout`) before committing.

## STATE AT HANDOFF
- Branch lane/reqvm1, committed on top of c7a821e14; clean tree apart from the deliver files.
- Rulings file reqvm1tri_rulings.md: empty, no entries applied.
- Owed: none. Scratch: /tmp/claude-1001/reqvm1tri (main archive build; disposable).
