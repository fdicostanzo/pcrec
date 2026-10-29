# [CAP-SPAN] — placing captures inside a proven span

Filed 2026-10-26 by Frank (idea) and the manager (general form). Not
scheduled; see the row's trigger in docs/dev/plan.md.

## The idea (Frank, 2026-10-26)

For `a+\w+(?:abc|bcd)\w+!(\w+)` pcrec runs three passes: a forward DFA
finds the end, a reverse DFA finds the start, then the VM walks the span
to place group 1. "We know it matches": nothing before the `!` can match
`!`, so the span holds exactly one `!`, and group 1 is (just after it,
proven end). One `memrchr` places it; the VM never runs. Other patterns
might skip the VM's start, start it later, or run some VM, skip, then
restart.

## The general condition (manager)

A capture boundary can be placed WITHOUT the VM when it has exactly ONE
viable position p in the proven span [s, e): the pattern before the
boundary matches [s, p) and the pattern after it matches [p, e). With one
viable p, leftmost-first priority has nothing to choose between. With
several, priority picks one and that still takes the VM.

Two ways to know a boundary is unique:

- **Static:** a separator byte or literal that the pattern before the
  boundary cannot contain (the `!` above). Cost: one memchr/memrchr.
- **Dynamic:** a forward DFA of the prefix from s and a reverse DFA of the
  suffix from e mark their viable positions; exactly one common mark
  places the boundary.

"Skip, then start the VM later" falls out of the same rule: once a
boundary is uniquely placed, everything before it is decided, so the VM
can start there with the remainder program. The VM cannot restart at
merely PROBABLE positions: with several viable cuts, the choice depends on
the prefix's priority, so the VM must begin where things are decided.

## The table it would become (first match, D-table style)

| row | condition | action |
|---|---|---|
| whole | the program is deterministic on the span (`det_all`, [CAPTURES-DFA-MB]'s member, D142) | no VM; positions follow from the span |
| unique-cut | every capture boundary is unique (static separator, or dynamic marks) | place them directly; no VM |
| late-start | a prefix up to a unique cut is decided | VM starts at the cut with the remainder program |
| early-stop | the remainder after the last close fits [p, e) ([CAP-EARLY-STOP]) | VM stops at that close |
| full | none of the above | VM walks the span as today |

late-start and early-stop combine (start late, stop early).

## Members and siblings

- [CAP-EARLY-STOP] (Frank 2026-10-09): the early-stop row; same reverse-DFA tool.
- [CAPTURES-DFA-MB]: its PREFIX / WHOLE-PROGRAM SKIP member (D142) is the whole row.
- start_landing.md U1, FIXED-MARGIN CAPTURES: the degenerate unique-cut (boundaries at fixed offsets from s or e).
- [ENG-TDFA]: the general alternative (tags give capture positions in the DFA pass itself); a big fish, opens only on Frank's word.

## Why it waits (Frank, 2026-10-26)

"The problem vm optimization has is that the vm portion of the match is
small." On find-in-text the locate passes dominate; the VM only walks the
proven span, often a few bytes. Every row above pays only where the VM's
span walk is a measured share of the time: match-dense subjects (whole-
subject match, find-all over hit-dense text) with long spans. Today's
bench ledgers have no such cell ([CAPTURES-DFA-MB]'s trigger, and its M-B
read found match-regime subjects were 5-93 byte literals where per-call
overhead dominates).
