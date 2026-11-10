# gquiet report

## STATE AT HANDOFF

Done, committed on lane/gquiet. scripts/tests/gestalt.test: 34 pass, 0 fail. No make test (no C).

**What changed.** scripts/gestalt builds every line silently as `L_<kind>`; one declared `ROWS` table at the end
(kind | condition | line variable) decides what prints. Default output = lines whose row holds, in table order;
nothing at all (no DONE line either) when none holds; rc 0 always. `--all` = the old full output + DONE. log.tsv
is written on every run, as before.

| row | prints when |
|---|---|
| load | load1 > nproc |
| queue | box idle (no running job) and a pending job whose answer is ready |
| session | a role registered in worktrees/.mgr/roles (main/kit) has no live session; line gains `; GONE: role` |
| disk | repo, tmp or /tmp fs >= 85% |
| context | a registered manager's tokens > 70% of autoCompactWindow (else the window) |
| ci | latest main run not completed/success|skipped (failure, cancelled, timed_out ...), or gh unavailable |
| box, lanes, subscription, git, unread | never by default (`--all` only) |
| docidx (docs/design/doc_index_format.md, lane/docfmt) | commented placeholder, not built |

Judgment calls: a cancelled-latest main run prints (`ci: completed/cancelled Nm ago`; push cancels normally
leave a newer run as latest, so a cancelled latest means nothing newer is green). `ci: unavailable` also prints,
since silence would hide a red. Unread is not a row: heartbeat step 1 runs monread itself. The DONE line is
dropped in default mode (Frank's "nothing at all"), so a broken gestalt looks like a healthy one; rc and stderr
are the only tells.

Queue candidates not built: a RED ended job not yet triaged (needs a triage record gestalt does not have); a
pending job waiting on a FAILED dependency (the answer text already says so, easy to add as a row); a job past
its cap (cap is in the running dir, not in `boxqueue status`).

**Tests** (scripts/tests/gestalt.test): existing cases now use `--all` (output unchanged); new: silent when
normal, `--all` + DONE, and one crafted input per row (load, ci failure/cancelled/unavailable, queue idle+ready
and idle+nothing-ready, disk, session gone, context hot and not-hot), log.tsv written on a silent run. New env
test hooks in gestalt: GESTALT_LOADAVG, GESTALT_BOXQUEUE, GESTALT_SOCKS_DIR; autoCompactWindow now read from
GESTALT_CLAUDE_HOME/settings.json (same file by default).

**Callers/docs changed.** scripts/CLAUDE.md, scripts/NOTES.md (new section), .claude/skills/pcrec-manager/monitoring.md
step 0. scripts/statusline.sh does not call gestalt (comment only: it writes snapshots gestalt reads): unchanged.

**Proposed heartbeat text (manager owns the cron; step 0 replaced, rest as is):**

    0. Run `scripts/gestalt --owner main`. It prints ONLY items past their threshold (load > nproc, a session
       gone, disk >= 85%, context > 70% of compaction, CI not green, box idle with a ready job) and nothing
       when all is normal. No output = nothing to report; any line it prints goes in the one-line reply and
       gets acted on.

**Kit's needed change** (.claude/skills/pcrec-memfn-manager/SKILL.md lines ~115-118, not edited): replace "its
'load' and 'sessions' lines go in the one-line reply only when unusual: load > nproc, a session gone, CI red"
with "it prints only items past threshold (nothing when normal); any line it prints goes in the one-line reply".
