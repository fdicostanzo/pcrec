---
name: idle
description: Carry out the 2026-10-20 idle rule - write the durable in-flight note and delete the heartbeat cron so the session can go idle. Use when Frank types /idle.
---

# /idle — go idle safely

The rule is `pcrec-manager` §1 step 0, "ONLY WHILE MONITORING". This skill
carries it out; it adds no procedure of its own.

## Refuse first

If lanes, watcher scripts or a peer mid-handoff are in flight, refuse in one
line saying which, and keep the heartbeat. Frank's argument after `/idle`
overrides this.

## Otherwise

1. Write a SHORT durable in-flight note into `docs/dev/owner.md` "Now" and
   `docs/dev/wake.md`, as the manager skill directs: what you wait for, who
   messages you, peer socket addresses, the next action per trigger. Nothing
   compaction could lose.
2. `CronList`, then `CronDelete` the heartbeat (the 30-minute off-minute
   cron). Load the tools with ToolSearch if they are deferred.
3. Confirm in one line: note written, heartbeat deleted, now idle.
