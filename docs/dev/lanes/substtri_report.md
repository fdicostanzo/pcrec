# substtri report: triage of boxqueue job 342-substext (make test RED)

Verdict lines: `test-corpus` and `test-rxtsource` only. Not the 332 cause
(measures.md §5¶8): that is absent from this log.

| section | class | cause | fix | standalone verdict |
|---|---|---|---|---|
| test-corpus | (b) the branch added an unpinned corpus file | `tests/subst/composed.rxt` (added a5402ff80) is a head-bearing `.rxt` that the corpus discovers. It declares `target = user` but has no cases and needs `--features all`, so run.sh failed "declared 1 target(s) but only built 0" (the only failed case) | renamed to `composed.rxtin`, the repo convention for head-bearing fixtures the corpus must not discover (cf. tests/definitions/composed.rxtin). Updated run_subst_tests.py (reader and docstring), the S1538 sabotage comment, tests/subst/CLAUDE.md and substext_report.md | the failing file is no longer discovered; `make test-subst` green (7841 checks, 0 failed); full corpus not re-run |
| test-rxtsource | (b) same file | census 293/5996/72906 vs pin 292/5994/72906; run.sh/verify_rxt C1/C3 leg disagreement, keyword census "COLLISION name=2 target=1" and W23-S7 entry files 293, all from composed.rxt's two blocks and its `name`/`target` lines | same rename; the pin (292/5994/72906) was already right, so no re-pin | `make test-rxtsource` green, census matches the pin |

No class (a) and no class (c) findings. Main is ahead of this branch (merge-base 32036bd39, main bf33d2dab); nothing in the reds depends on that.
