# gestpoll report

## STATE AT HANDOFF
- Premise: `scripts/tests/gestalt.test` 93/0 before the edit. After: 98 pass / 0 fail (TMPDIR under scratch). Rulings file: no entries to apply.
- Not run: a live-box check of the row against the real /proc (the test uses fake proc directories only).

## CHANGES
- scripts/gestalt: new `pollers` row (python3 -I scan of `${GESTALT_PROC:-/proc}`, under `timeout 3`; this user's bash/sh/zsh/dash processes whose cmdline holds `until|while ... sleep`). Identity = the text from the first `until`/`while` on (the `source snapshot` prefix drops out), digit runs >= 3 collapsed, trailing quotes trimmed. A fork whose parent has the same key (a pipeline subshell) is not counted. Prints `pollers: N copies of the same wait loop (oldest Xm, pids a b c): <80 chars>` per group with >= 2 copies; silent otherwise. Added to the ROWS table and the header contract; scripts/CLAUDE.md names no row list, unchanged.
- scripts/tests/gestalt.test: G2 points GESTALT_PROC at an empty dir (existing cases stay deterministic); new cases: 3 identical loops fire (exact line, pids, fork excluded), 2 different loops silent, 1 loop silent, and a plant that drops the grouping (sed on a copy) goes red. 98/0.
- Report added to the lanes history index.
