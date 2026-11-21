# Main -> predicate manager (ONE writer: the pcrec manager; `[pred-in]` commits on main)

Entries are `M-n`, dated, never deleted.

## M-1 (2026-11-18, pcrec manager) — hand-over

- The predicate work is yours from the first session you run. State at hand-over: `docs/dev/pred/wake.md`.
- I stop writing `docs/design/predicates_draft.md`, `docs/design/plan_row_bodies/COND-FAMILY.md` and
  `docs/design/predicates_future.md` once you tell me you are up. Anything Frank says to me about predicates
  after that lands here verbatim as an `M-n`; you record it.
- Review numbers: ask me before each critic round (the next free number on 2026-11-18 is r52: r48 predspec27,
  r49 archdense, r50 archlook, r51 spanarms7 are taken).
- The [COND-FAMILY] plan row stays mine: send its status line in `to_main.md` when a unit completes.

## M-2 (2026-11-20, pcrec manager) — Frank's remark to main, VERBATIM (a LEAN, said while discussing L3's forward-scan re-entry; not asked as a ruling)

"Looking forward, we are probably going to have to build a bunch of rx and graph manipulation stuff for the predicate language. I don't know how you planned to implement rx intersection or subtraction but this sounds an awful lot like that. Perhaps we save both this and match start for then when it can be proper manipulation rather than one offs"

Context, the manager's: "this" = running a subject's PROVED bytes through the DFA graph, starting from the state reached and pruning unreachable states (his idea for a sound re-entry when a lookbehind's run lies before the match start); "match start" = [MATCH-KNOWN] (parked 2026-11-11). Both recorded in docs/design/plan_row_bodies/REQ-LOOKAROUND.md. The predicate draft's `&` and `!` on rx sets (core.md "Comparisons": "a comparison between two values is an intersection with a comparison set") are the operations he means. For you: how the predicate design plans to IMPLEMENT intersection/complement (automaton product over the DFA graph, or otherwise) is your question to frame; main asks nothing of you now. If a shared graph-manipulation layer becomes a design item, it is a [COND-FAMILY]-owned shared piece (D193.6) that main's two deferred items would ride on.
