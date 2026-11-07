# hookrole report: per-session hooks + stricter lanecheck

## For the owner, in plain words

Before: whichever session you typed a prompt in, the queue hook read the pcrec manager's unread queue lines
(so a prompt in the kit session ate main's lines and the kit never saw its own), and after any compaction the
hook pasted main's owner view and wake file into whichever session had compacted.

Now each manager session registers its role once at wake (`scripts/session_role main` or `kit`; one line added
to each skill's wake section). The hooks look the session up by the session id every hook receives. The kit
session now reads `monread kit` and, after compaction, gets `memfn/docs/wake.md` (the kit branch's copy under
worktrees/memfn if it exists; the kit has no owner view, so none is injected). A session with no role gets a
one-line "no session role registered; run ..." notice, consumes no queue lines, and gets neither file after
compaction (it is told both candidate paths and asked to register). Subagents are untouched (silent).
No settings change was needed. Caveat: a resumed session may come back with a new id; the notice then asks
it to register again. Registry files live in worktrees/.mgr/roles/ (gitignored, pruned after 30 days).

lanecheck is stricter: `owed: none` passes only when STATE AT HANDOFF has a line that starts `OWED: none`
(or `- OWED none`), not a sentence quoting the words; and if the lane's rulings file has entries
(R1, R2, ..), STATE AT HANDOFF must name the last entry's id (an empty or "(none yet)" file needs nothing).

## Proof

Premise (before): `monitor_unread.sh` ran `bash "$here/../monread" main`; `post_compact.sh` cat'd
`$root/docs/dev/owner.md` and `$root/docs/dev/wake.md` unconditionally.

Real hook inputs, logged by a headless `claude -p` run in this worktree (project settings fire the worktree's
hooks), both events, top level, no agent_id:
- SessionStart: `session_id, transcript_path, cwd, hook_event_name, source` (source=startup; for the compact
  hook the same shape with source=compact, per the hooks reference, not separately logged).
- UserPromptSubmit: `session_id, transcript_path, cwd, prompt_id, permission_mode, hook_event_name, prompt`.
- Discriminator check: in a second headless run the session's `$CLAUDE_CODE_SESSION_ID` (read from a Bash tool call)
  equalled the logged hook `session_id` (24f08cfd-8a52-47d3-a4ec-15632c0d32a2), so a session can learn its own id
  with no config change. agent_id appears only inside subagents (existing hooks already rely on this).

Self-tests (all run, bounded by timeout):
- scripts/tests/hookrole.test: 17 passed, 0 failed (register/get, role kit sees KITLINE only and leaves main's
  cursor, role main sees MAINLINE only, no role = notice + cursors unchanged, subagent silent, garbage input,
  compact main/kit/kit-branch-copy/no-role/subagent).
- scripts/test_queuemon.sh (its hook cases now register a role): 45 passed, 0 failed.
- scripts/tests/lanecheck.test: 40 passed, 0 failed (new: owed quoted in a sentence fails, bullet `- OWED none`
  passes, rulings empty passes, entries with last id unnamed fails, named passes).

Simulated compaction input `{"session_id":ID,"hook_event_name":"SessionStart","source":"compact"}` (scratch tree):
- role main: owner.md and docs/dev/wake.md injected, kit wake not.
- role kit: only memfn/docs/wake.md injected (header "role KIT").
- no role: neither file; text names `scripts/session_role main` and `kit`.

## STATE AT HANDOFF

OWED: none
Rulings file docs/dev/lanes/hookrole_rulings.md: empty at handoff (no entries to apply).
Branch lane/hookrole, no src/ changes, no settings changes. The roles registry starts empty: the two manager
sessions must each run their `scripts/session_role` line once (or on their next wake) before the hooks serve them;
until then both get the notice. Not exercised for real: a live compaction (simulated only).
