# mcfixc report — r7 memfn-mcfixb XS fixes (lane/memfn-mcfixb, base 6ab3f485b)

## Summary
Three FIX-NOW items of the ruled r7 review fixed and one DOC line added; review + review/ dir copied unchanged to
docs/dev/reviews/2026-11-15-r7-memfn-mcfixb(.md|/) and indexed. No decision semantics changed, no emitted byte moved.

## Fixes by id
- RULE-1 (S3216): d197_rule.py main() parses `rule RUNDIR AVX2RUNDIR [--second F FA] [--confirm C CA]`; each flag takes
  exactly two rundirs, once; second-ness only when `--second` is given. Bad count / unknown flag: `usage` line, exit 2
  (new UsageError). Drill gains 6 SUBPROCESS cases (51 total): no flag on a first run with the shipped arm bound
  avx2 -> INCONCLUSIVE x3 (was NOT-WIN); `--second` pair -> NOT-WIN x3 (was TypeError); `--second`/`--confirm` with one
  rundir, one positional, unknown flag -> rc 2 + usage. RED on 6ab3f485b: 6 of the new cases WRONG; GREEN: 0 wrong.
- RULE-2 (S3217): est.py read_cells: a cells pin PRESENT and different is refused; absent -> stderr NOTE, read
  unpinned. Selftest (68 cases) gains: absent -> priced + NOTE; present+different (zeros) -> refused. The absent case
  is the review's repro (refused on 6ab3f485b by `pin None != sha`).
- CHECKS-2 (S3218): window.c:1904 `FF__COUNT <= 31`. Compile-time assert only.
- DOC RULE-3 (S3219): d197_rule.tsv header: the window runs on the 7700X (Zen 4) only; the shipped-arm guard refuses an
  AVX2-only box by design (general fix = PLAN, trigger: first off-7700X mfcard window). The timing jobs' own note
  lives in scratch/memfn/mcfixa/jobs (outside this lane's write scope, untouched): the manager may add the same line.

## Validation
make strict: see STATE; make test-codegen: see STATE; tests/memfn/run_arch_blind.sh (run via bash; file not +x): 17 pass 0
fail; d197 drill 51 cases 0 wrong; est selftest 68 cases 0 wrong; jobs 609 and 610 `--dry-run` rc 0 against this
worktree (run from a copy of the jobs dir with scratch paths re-pointed to mcfixc, since window.vars needs a write
there; the jobs call the unchanged `rule RUNDIR RUNDIR.avx2libc [--confirm C CA]` shape; jobs unedited).
Review-index grep `plan\.md:[0-9]` over the review and CLAUDE.md: none.

## STATE AT HANDOFF
Rulings applied: none (file empty). OWED: none
