# ic3tri report: triage of the red job 680-ic3-test ([INLINE-C] stage 3)

## Summary
Job 680-ic3-test ended RED (rc=1, wall 1501 s) on lane/ic3 eac952671. Build,
`make strict` (DONE rc=0) and the mover census vs main 89831df9a (DONE
cells=41900 unexpected=0, so NO emitted-byte movers, abi stays 91) were green.
Four `make test` sections were red; every one was a stage-3 consequence, none a
miscompile: three stale pins/fixtures (class a) and one CLI diagnostic-order
defect found by a census (class b, trivial). No flakes (class c). All four
fixed and re-run green; the full job is re-queued.

## Red items
Verdict read from `*** [Makefile:N: test-X] Error` lines (4) in job.log.make.

1. test-resource, `[census]` raw-allocation file set moved. (a) Stage 3's
   `src/dump/callouts_dump.c` has one `malloc(1)` (the empty result string of
   `pcrec_list_callouts`, caller-freed like every dump entry's text). A real,
   legitimate new site the pinned manifest exists to name.
2. test-cpset-structure, `[2d]` scratch witness compiler did not build. (a)
   The check copies src/lib/cli/memfn into a scratch tree; stage 3 moved
   sha256 to `shared/` and `src/parse/rxt_source.c` now includes
   `../shared/sha256.h`. `tests/lib/lib_srcs.sh` already knew `shared/`; this
   script's own `cp -R` did not.
3. test-startset, `[vm-movers] vm`: 1 mover not in `manifest_s2_vm_forced.tsv`:
   `tests/code/frag/pin3_mid.rxt:7`. (a) A new fixture block (patterns-only
   fragment, pattern `mi+d`), a correct forced-VM mover, the manifest's own
   documented "fixtures join the corpus" case; no existing row moved.
4. test-subst, option census: `--include-block` and `--list-callouts` are
   documented in `--help` but the census could not spell them. (a) for
   `--list-callouts`/the VALUES rows. Once spelled, `--include-block` showed
   (b): `main` resolved it (`cli_include_block`) before `cli_run`, so
   `--include-block X --subst T` answered with the include-block operand
   diagnostic instead of `--subst`'s "option for a pattern compile" refusal
   that every other pattern-compile option gets (subst_api.md section 5 para 1).

## Fixes
- 3ecae66a3 cpset-structure: scratch tree also copies `shared/`.
- da125a127 resource census: `src/dump/callouts_dump.c` added to the pinned
  file set, with the why beside the list.
- d832c69a4 `manifest_s2_vm_forced.tsv`: +1 row and a dated comment line.
- d096be51c cli/main.c: skip `cli_include_block` when `--subst`,
  `--subst-file` or `--emit-support` is set so their option refusal speaks
  (still a rc 1 refusal; only the wording and its owner move); census VALUES
  gains `--list-callouts` and `--include-block` (class query); cli.md 1.23
  gets one sentence (D80).

No design deviation touched; no emitted byte changed; abi unchanged.

## Re-validation
- cli_option_census.py alone: 257 passed, 0 failed.
- tests/codegen/run_cpset_structure.sh: 29 passed, 0 failed ([2d] fires).
- tests/startset/run_vmhat_checks.sh (JOBS=4, niced): 22 passed, 0 failed;
  both `[vm-movers]` rows green (auto 489, forced 3726).
- tests/resource/run_resource_tests.sh: `[census]` PASS (11 files); the rest
  ran PASS until my 115 s cap (the section was green outside the census in 680).
- tests/subst/run_subst_tests.sh: 8929 passed, 0 failed.
- The heavy `make test` was not re-run here (box queue was full); the full job
  was re-queued with `scripts/boxqueue retry ic3-test`.

## STATE AT HANDOFF
lane/ic3 carries four ic3tri commits on top of eac952671. Worktree clean apart
from the untracked deliver files and `docs/dev/artifact_size_log.tsv` (a test
side-effect, deliberately not committed). Rulings file ic3tri_rulings.md did not
exist (no entries applied). Owed: ic3-test (retried job).
