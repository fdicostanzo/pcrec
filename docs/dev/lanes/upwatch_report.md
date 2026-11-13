# Lane upwatch — record PCRE2 issue #1072 and follow upstream issues daily

## STATE AT HANDOFF

STATE: complete. Validation complete, nothing owed. No rulings file existed in the worktree (none applied).
- `scripts/tests/upstream_watch.test`: 11 pass, 0 fail (foreground, TMPDIR under scratch/upwatch).
- `scripts/tests/gestalt.test`: 93 pass, 0 fail (was 87; 6 new upstream-row cases).
- `scripts/plan_lint.sh`: 336 rows, 0 violations; `scripts/entry --lint-scripts`: 66 index lines, 0 failures;
  `tests/doc_lint/run_doc_lint.sh`: 15 pass; `check_claudemd_size.sh --all`: within limits.
- Premise: `gh issue view 1072 -R PCRE2Project/pcre2` returns OPEN with 0 comments; a real `scripts/upstream_watch` run on it is silent and seeds its state.
- Finding: this box's `gh` does not know the JSON field `stateReason`, so the script asks for it in a second, best-effort call only when an issue has just turned CLOSED.
- Not done by design: no `TOOL: DONE` line (a few-second tool whose stdout is the news; stated in its header). Nothing under src/ or memfn/ touched; nothing posted upstream.

## CHANGES

- `docs/dev/upstream_issues.md`: new row U26 (issue URL, filed 2026-11-12, the two bug cells, seen on 10.46 and 10.49, pcrec refuses both, status reported-upstream).
- `docs/dev/plan.md` [PCRE2-DEFLB]: status line "reported upstream #1072 2026-11-12; awaiting maintainers"; trigger "a maintainer reply or a fixing release".
- `docs/dev/upstream_tracked.tsv` (new): the declared list (url, our row id, filed date); one row, #1072.
- `scripts/upstream_watch` (new): per tracked issue reads state, comments (last author, time, text) and labels through read-only `gh` (timeout 60), compares with `$PCREC_TMPDIR/upstream_watch/state.json`, prints one line per issue with news (new comment, CLOSED (reason), REOPENED, labels now), nothing otherwise, one `upstream: unavailable` line when gh fails (state untouched, so the news is kept).
- `scripts/tests/upstream_watch.test` (new): shim `gh`; new comment, several comments, silent on no change, closed once, reopened + labels, gh failing, gh absent, first-seen issue, and a plant (comment branch disabled) that the same check catches.
- `scripts/gestalt`: new `upstream` row. At most one detached `upstream_watch` run per 24 h (stamp `$PCREC_TMPDIR/gestalt/upstream.last`); its output goes to `upstream.news`, which the next gestalt run prints once and consumes; empty otherwise (not shown even under `--all`). Detached so gestalt never waits on gh.
- `scripts/tests/gestalt.test`: a quiet stub watcher is exported for every case (no real gh); new cases: first call runs it and prints nothing, next call shows the news, no second run within 24 h, news shown once, reruns when the stamp is over 24 h old, a quiet watcher leaves the row empty.
- `scripts/INDEX.md`, `scripts/CLAUDE.md`, `docs/dev/history/claude_md/docs__dev__lanes.md` (lanes history index): entries for the new script and report.
