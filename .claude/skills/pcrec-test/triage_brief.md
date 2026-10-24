# Triage brief (launched by the pcrec-test monitor on a red stage)

TRIAGE (sonnet), read-only. Scope mandate: touch only /home/pcrec/projects/pcrec
and pcrec-bench; scratch only under /tmp/claude-1001/<your name>/; never edit
either repo, never commit, never run make or any suite (the battery may still
be running). `timeout` on uncertain commands; no cd into worktrees.

Input: LOGDIR and the first red stage (your prompt); later red stages appear in
LOGDIR/red_stages.txt (re-read it before you finish). The frozen commit is in
LOGDIR/frozen.txt; its tree is the worktree named there.

Per red stage: the verdict is make's error lines
(grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-' and the stage's own FAIL lines);
for each failing check, classify with evidence:
- STALE PIN: the check compares against a pinned value that a landed change
  legitimately moved (name the commit and the pin file:line);
- REAL REGRESSION: an answer, speed or size change no ruling covers (the
  smallest repro: pattern, subject, command, observed vs expected);
- INFRA: the harness, box or environment (disk, timeout, a missing tool);
- UNKNOWN: what would decide it.
Write /tmp/claude-1001/triage-<NAME>/triage.md, NAME being the job name in your prompt (one table: stage, check, class,
evidence, suggested owner), then your final reply (<= 10 lines) naming that file path; it reaches the manager directly (the monitor may not see it, which is fine: the FILE is the delivery),
then END.
