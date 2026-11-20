# c4scope report

## Summary
C4 (`make test-memfn-arch`) no longer scans test-corpus DATA. One rule in `tests/memfn/arch_blind_check.py` (`mask_data`), no path list. `make test-memfn-arch` is green on the branch with no new allowlist row (22 checks, 0 failed); the L1 D27 witnesses (`l1d27_witnesses.rxt` 5 hits, `l1d27_listing.tsv` 1 hit) are now out of scope, so no third "adx" patch is needed.

## The scope rule
Applied by file shape before the scan, tests scope only; line numbers preserved.
- `.rxt`: a non-comment line whose first token is a data directive (`pattern`, `pattern-esc`, `m`, `n`, `ms`, `ns`, `mc`, `mg`, `gu`, `var`, `under`) has everything after the keyword blanked; so do the indented lines of a `pattern |` opaque region. `#` lines, `description` lines and every other directive stay in scope. rxt_format.md §1.5¶1: comments are WHOLE-LINE only, so no trailing-comment swallow is possible.
- `.tsv` under tests/: a header row naming a column `pattern` or containing `subject` blanks those columns in later rows; header and other columns stay in scope.
- Every other file type is scanned whole. Spec/design sentence: integration.md C4 row (§ tests table), docs/testing.md, one pointer-free note in tests/memfn/CLAUDE.md (at its size limit, so no sentence there).

## Rows deleted
- tests/altcls/altnf_lookbehind.rxt (class 1, 2)
- tests/lookaround/lookbehind_group_alt.rxt (class 1, 2)
- tests/lookaround/d27/refusals.rxt (class 1, 7)
- lowered: tests/lookaround/lookbehind_variable.rxt 4 -> 2 (the two comment lines naming "adx" stay in scope).
Allowlist total 116 -> 103. C4_ALLOW_FLOOR (26) left unchanged: it is a lower bound far below the total and is not breached. The `.gen.py` generator rows for "adx" stay (a `.py` is in scope by the ruling).

## Self-test and plants
New scratch controls (the word is the first compiler-derived class-1 plant): `.rxt` comment RED, `.rxt` description RED, `.rxt` `oracle` line (non-data directive) RED, a comment after a `pattern |` region RED; pattern line, m/ms lines and the `pattern |` region lines NOT hit; planted in .sh/.py/.c test files RED; listing TSV pattern/subject columns not hit, another column RED. The negative hex-escape control gained a `description` line so it still exercises the rule.

## Validation
`make test-memfn-arch`-equivalent (run_arch_blind.sh): 22 passed, 0 failed. Queued, not awaited: build + `make test` (perfrun) key batch b202611191745283801473 (jobs 205 build, 206 test; OWED key `206-c4scope-b202611191745283801473.test`), and `make strict` as 207-c4scope.

## STATE AT HANDOFF
Branch lane/c4scope, committed. Rulings file empty (no entries). Owed: the queued test and strict jobs.
