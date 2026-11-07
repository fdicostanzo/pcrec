# Peers: messages between sessions and to lanes

Loaded by both manager skills' trigger tables when you are about to message
the kit, the bench or a running lane, relay a ruling, or wait on a peer.
Applies to main and the kit alike.

## 1. Ask for a reply unconditionally

Frank, 2026-11-07: "If you need a response then always ask each other for a
response unconditionally." A conditional ask ("reply on conflict only",
"no reply needed unless ...") makes silence mean two things: "no conflict"
and "not read yet". It happened 2026-11-07: main asked the kit to reply on a
conflict only; the kit found none and sent nothing (its journal: "no reply
sent (main asked for a reply on conflict only)").

- A message that needs ANY knowledge back ends: `REPLY: one line, either
  way (e.g. CONFLICT <what> / NO CONFLICT).`
- A message that needs nothing back says `NO REPLY NEEDED` and you then act
  as if it was read only when you see its effect.
- RECEIVING: a peer message that asks anything gets a one-line answer even
  when it says no reply is needed (memory pcrec-hourly-peer-checkin, revised
  2026-10-09: "answer in spirit, not minimally").
- Answer in spirit everywhere: a rule's purpose outranks its exact wording.
  When the two diverge, follow the purpose and say so in one line (Frank
  2026-11-07: "too literal with exact wording compliance").

## 2. Waiting on a peer

Add one line to your wait list (main: owner.md "Waiting on"; the kit:
`worktrees/.mgr/waiting_on.kit`; `<since HH:MM> <session> <thing>`)
when the wait starts, delete it when it ends. The heartbeat reads that list
every tick and checks each entry older than 60 min (monitoring.md §1). The
list is the whole condition: nothing else decides whether to ping.

## 3. Channels (durable vs live)

- Live: SendMessage by session name. Durable (must outlive a session): the
  kit ledger (`memfn/docs/requests.md`, main writes; `responses.md`, the kit
  writes), the bench inbox/outbox (`inbox_from_pcrec.md`, main writes, a
  single-file `[inbox]` commit; root CLAUDE.md situation row). One writer
  each way (D78).
- To a RUNNING lane: never by message alone (a busy lane reads its inbox only
  between tool rounds and may deliver from an older state). A clarification
  goes into its rulings file in ITS worktree
  (`worktrees/NAME/docs/dev/lanes/NAME_rulings.md`), numbered R1, R2, ...;
  a scope change goes to a FRESH lane (memory
  pcrec-no-addenda-to-running-lanes). At acceptance, check the report's
  STATE AT HANDOFF names the LAST R-n in that file; if it names an earlier
  one or says "empty" while entries exist, apply the missing ruling yourself
  or send it to a fresh lane (u25, 2026-11-07: report "rulings file was
  empty" 8 minutes after R1 and R2 were written).
