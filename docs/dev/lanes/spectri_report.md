# spectri — triage of lane specnum's red `test-spec-history` (2026-10-09, sonnet)

Worktree `worktrees/specnum`, branch `lane/specnum`, from `5a2a134a`. Evidence:
`build/land/trailer.log` (make test rc=2, one red section) and `build/land/test.log`.

## Diagnosis

`test-spec-history` ran 64 checks: 62 passed, 2 failed. Both failures are in the
`[cites]` group and both name ONE file, `docs/dev/lanes/specnum_report.md`
(`build/land/test.log:6786-6787`):

- dangling citation(s) at report lines 87, 110, 111, 123 (a section 11.9, a section 9.9
  twice, a paragraph 77 of section 3.1.3);
- a line-number citation at report line 111.

Cause: the report DESCRIBES the check's failing-direction plants and the sabotage row,
and it wrote those plants as literal citations (the doc name, `.md`, a space, then
`§9.9` and so on; and the doc name followed by a colon and a line number). The
citation scan reads every tracked file in the tree, so it read the report's examples as
real, dangling citations. Line 87 was a real `match_api` section citation of a DESIGN
note's section, spelled without the note's name in the same words. The checker did what
it is chartered to do: every flagged hit is text that would mislead a reader the same
way a real dangling citation does.

The failure is not load-related and not a moved pin: nothing the renumbering touched
is out of date (numbering, toc and the 1,060-citation scan all pass; the 62 other
checks include every history-marker row and every baseline row).

## Fix-by-fix

| check | class | evidence | fix | commit |
|---|---|---|---|---|
| `[cites]` dangling (4 lines) | none of (a)/(b)/(c) exactly; nearest (a): offending TEXT in a tracked non-spec file, a self-trigger of the checker by a lane report | `build/land/test.log:6786`; `docs/dev/lanes/specnum_report.md` lines 87, 110, 111, 123 quoted planted/old citations as literals | reworded the four spots to describe the plants in words (a citation past the last heading, a paragraph number past a section's last, a nonexistent section of that doc); no allowance added | e26258b8 |
| `[cites]` line-number (1 line) | same | `build/land/test.log:6787`; report line 111 | same hunk (the line-number plant is now described as "a colon and a digit after the doc's name") | e26258b8 |

Not done, deliberately: no row in `tests/spec_history/cite_exclude.tsv` (each row is a
hole in the check; the report is prose that can simply avoid the pattern), no change
to `spec_cites.py`, `docs/spec/`, any pin or the baseline. The checker, the
allowlist, the baseline and the specclean/specnum anchors were all correct.

Class note for the manager: this is a hazard for ANY lane report that documents a
citation check by quoting a bad citation. `tests/spec_history/CLAUDE.md` could grow a
one-line warning; not done here (outside the triage brief; say if you want it).

## Light re-validation (at the commit above, `build/triage/` logs, gitignored)

| command | result |
|---|---|
| `gnutimeout 600 make -C worktrees/specnum test-spec-history` (`build/triage/sh.log`) | rc 0; checks passed: 64, checks failed: 0; `[cites] match_api: 1060 citations scanned, floor 500` |
| `gnutimeout 300 bash scripts/tests/spec_toc.py.test` (`build/triage/toc.log`) | rc 0; checks passed: 17, checks failed: 0 |

(The citation count moved 1,064 -> 1,060: the four flagged report lines no longer
parse as citations. Floor is 500.)

## What the manager owes before merge

The only file changed besides this report is `docs/dev/lanes/specnum_report.md`
(plus the index line in `docs/dev/lanes/CLAUDE.md`). Which sections read those files:
`test-spec-history`'s cite scan reads every tracked file and is the section that was
red and is now green. No other section reads lane reports' prose (the registry and
memfn readers that name `_report.md` files name other, specific reports). So a full
`make test` re-run is NOT needed for these fixes by themselves.

Still owed from lane specnum's own chain, independent of this triage: the verdict on
the rest of the red run was one section only, and the run was load-contaminated by
another session's sweep, so the other 58 sections' greens are valid but a clean full
`make test` on the merged tree is the manager's normal merge gate. If the manager
treats the load-contaminated run as sufficient for the 58 greens (nothing in them can
be a false green from load), the owed validation is: this triage's two light runs
(done) and nothing more. Recommendation: no extra run for these fixes; the usual
post-merge full `make test`.
