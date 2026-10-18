# Lane u1design: report

Lane `u1design` (opus), 2026-10-18, branch `lane/u1design` from main `a016b3bfa`. This was a
DESIGN-ONLY lane: nothing under `src/`, `memfn/`, `cli/` or `lib/` changed. Inside the box
rule I ran only single-pattern `build/pcrec` compiles from main's tree (no rebuild) and one
size-only `gcc -O2 -c/-S` hand twin under `nice -n 19`. I did not run make, time anything
or sweep anything.

## Delivered

- `docs/design/kit_proof.md` — [KIT-VERIFY] U1 (report without an engine), with D161
  add. 16's context spans. Sections §1-§8 follow the brief, and each ends with a "where to
  attack" note.
- `docs/design/kit_proof/` — `counts.py` and `counts.txt` (the census recount by consumer
  kind, groups, end anchors and context), `cover_twin.py` (the SIZE-ONLY hand twin) and
  its CLAUDE.md.
- The `docs/design/CLAUDE.md` entry.

## Key decisions

1. **U1 is ONE LOCATE row, `cover`**, placed `empty → rev-end → cover → composite`. It hands
   `SPAN`/`NOMATCH` to the existing `FIN2 report`/`FIN1 nomatch`, so FINISH gets no new
   row. T-PROOF stops being a separate table: its rows become `cand_rows[]` members that
   share one deny, `-fno-kit-proof`.
2. **Whole-cover is read off the route's ANCHORED machine** (A or ATT), which is
   priority-aware. The facts layer was not used, because an NFA walk without priority would
   refuse `in|instanceof`.
3. **The `\b` "rewrite" is a reading, not a lowering.** The context set comes from the
   seed table (before the match) and the class-indexed accept (after it). That makes it an
   equivalence by construction, and it moves no bytes off the `cover` path.
4. **The end anchor.** Every census pattern that has a kit site and becomes whole-cover
   only "with an end anchor" is `(?m)…$`, which is a context after-span. The length compare
   therefore belongs to the no-kit-site siblings (U-anch).
5. **Stage 1 is DFA-finisher routes only** (71 bench / 686 corpus native sites, +6 / 84
   with context). Captures on the VM or a hybrid are U1b.
6. **R-26 is drafted with R-25 first.** It covers per-offset `proven[]`, `exact_len`,
   `consumable_len`, CONTEXT spans with `absent`/`consumable`, and `MF_SK_REPORT`. Each
   enum's UNSTATED zero is refused.
7. **Staging.** Z0 → Z1 (zero movers) → Z2 (trace-build routed, zero movers) → a
   directional measurement as the GO/NO-GO → B1, the one byte-moving event (pcrec abi +1
   together with the kit's proving text).

## Open questions for Frank (§8.4)

- Q1: captures in U1.
- Q2: should `cover` be source-neutral?
- Q3: is the machine reading acceptable as his `\b` "rewrite"?
- Q4: one family deny, or one deny per row?

## Numbers (none timed)

- Population: from the committed kvcensus run (`kit_proof/counts.txt`).
- `foobar` hand twin: `.text` 2,047 → 1,425 B and `rx_search` 100 → 61 instructions
  (gcc 15.2 -O2, dev box).

## Validation

None was owed: this is a design note, with no code and no check changed. The note's own
checks (X1-X5, S1130-S1138) are proposals for the build lanes.

## For a fresh agent resuming

Start with the critic panel's findings against §1-§8. The ids S1130-S1138 are PROPOSED and
not entered in the ledger.
