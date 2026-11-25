# arenadesign21 report: [ARENA-SCOPES] design rev 2.1

## Summary
Rev 2.1 of `docs/design/arena_scopes.md` applies review r103's RULED text fixes C1-C20 and the NEW gate. Text only: no
code, no new measurement. Counts re-run at main d4a6c0b74.

## Applied
- C1: D-1 rests on FORM (one list for every memory kind, no second mechanism); (A)'s cost kept as context, "0 to 64 KB by
  where the owned record lives". C2/C3: successful-compile figures, the 146/150 gdb read.
- C20: `uprops_produce`'s `Arena tmp` is client S29, unit F6. CHOICE: L4 narrowed for that one client (scanner allow row),
  not a streaming decode. Reasons: a pure transient that captures nothing in the AST; a streaming decode is a new
  algorithm needing its own measurement (D77); the compile-arena form was refused at +29% peak. D-10's kinds sentence and
  counts updated (463 `pcrec_arena_alloc(`, 34 Arena writers, 6 scanner rows).
- NEW gate (THE SEEN GATE, in F1): W7 gains a hand-kept-arena window, a planted-strand unit test, the filed
  `uprops_produce` known_stranded row required REACHED, and sabotage (10); no unit claims a strand closed before it reads.
- C4-C19: shared `scope_check` in all six calls, drills 3b/3c, forged-handle 4b and sabotage 4c, W6 re-pins, F1 anchors,
  scanner rows (-6 +2), accessors, F3 STOP 256 B, T1 split by arena identity, `PcrecPartFacts.hold`, both alloc_check links,
  bare `free(` regex, C0(d) method, C19 items.
- "r103 disposition" table added at the end.

## STATE AT HANDOFF
Committed on lane/arenadesign. Rulings file empty at every re-read. OWED: none. Not applied: none. Validation:
`make -s test-plan-lint` (result in the handback).
