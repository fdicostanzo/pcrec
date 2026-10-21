---
name: idle
description: Carry out the 2026-10-20 idle rule - write the durable in-flight note and delete the heartbeat cron so the session can go idle. Use when Frank types /idle.
---

# /idle — go idle safely

The rule is `pcrec-manager` §1 step 0, "ONLY WHILE MONITORING". This skill
carries it out; it adds no procedure of its own.

## Refuse first

Go idle ONLY when actually idle, or when the one thing in flight is watched
by a VERY RELIABLE monitor (Frank, 2026-10-21): a zero-model script that
exits on completion AND on quiet/died/cap (`scripts/watchrun` on a chain or
queue, `scripts/boxqueue`'s own failure handling) with no lane agent alive.
A live LANE is never reliable (lanes go idle without reporting), nor is a
bare background-command notice, nor a peer mid-handoff. In those cases refuse
in one line saying which, and keep the heartbeat. Frank's argument after
`/idle` overrides this.

## Otherwise

1. MANDATORY before deleting the heartbeat (the post-compaction hook
   `scripts/hooks/post_compact.sh` re-injects these files, so they ARE the
   memory an idle compaction keeps): (a) `docs/dev/owner.md` "Now" current;
   (b) `docs/dev/wake.md`'s STEP 0 rewritten to the present (what you wait
   for, which monitor and its exit line, who messages you, peer addresses,
   the next action per trigger, open rulings); (c) a `docs/dev/dev_journal.md`
   entry for anything done since the last one, committed. Nothing a
   compaction could lose may live only in the conversation.
2. `CronList`, then `CronDelete` the heartbeat (the 30-minute off-minute
   cron). Load the tools with ToolSearch if they are deferred.
3. Confirm in one line: note written, heartbeat deleted, now idle.
