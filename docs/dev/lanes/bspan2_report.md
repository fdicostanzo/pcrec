# bspan2 report: block_span.md rev 2

## STATE AT HANDOFF
OWED: none. STATE: done (text revision only; no code, no run). Branch lane/bspan2, note `docs/design/memfn/block_span.md` rev 2 (revision-history line marked "rev 2 (2026-11-21)"). Rulings file `bspan2_rulings.md` re-read before the commit and this report; last entry applied: R-1 (D155 add. 1 Q-R9-10 cited in the option-A paragraph, §2). No probe was run; every number quoted is rev 1's, with its command in §16.

## THE JOB
Fold the scalar-wrap ruling, the final census, the manager calls and a ship-size account into rev 1, without redesigning.

## CHANGES IN REV 2
- Header/status: rev 2, GATED banner removed, revision history added.
- §0.1: replaced by the final lane/spancensus2 census (corpus 1 of 6403 pairs / 1 of 5645 texts; bench 3 of 363 / 3 of 356; utf8-only movement at k<=3; 23 callout blocks refused), plus main's default-width line (k 16-31 window / 24-31 scan; cover_cap.md §11.4 B) and "information only" with the D201 add. 1 quote.
- §2: option A taken; B kept as one "why not taken" paragraph; the wrapper stated as code organization in source with the 2 of 10 machine-code differences (`\w{20}`, `\w{32}`) named; new §2.1, the scalar no-loss check (a census with objdump at default width and 4095, reusing spancensus2's method/script and wrapprobe; b short scalar timing of the differing sites in a Frank-cleared window with the rule and floor written before data (710 cards/A-A method); c keep list).
- §3: new first-match row T-keep (the named declared row for losers; empty until U2b fills it; drops the selector at both layers, so the SIMD win on that stretch is forfeited, flagged for the build go). §3.3, §7: scan-scope and wrap-deny recorded.
- §8: C6 loses the scalar-wrapper arms (moved to U2b, timed once) and the size-record bullet (R-4 cut).
- §14: new unit U2b before landing; U2 no longer mentions B.
- §15: all four questions RESOLVED (scalar-wrap: Frank 2026-11-21; scan-scope WALK only and wrap-deny live at both layers: "manager 2026-11-21"; ship-size into §17).
- §17 (new): SHIP-SIZE table, set against the 4-pattern population, with the R-4 check of rev 1.
- `docs/design/memfn/CLAUDE.md` index line updated.

SHIP-SIZE TOTAL: 3 new table rows (T-keep conditional) plus the reshaped if-chain rows; 1 deny row; 1 card + 1 grid row + 1 formhash entry; 2 G2 sections, 8 flip cells, 1 identity gate, 4 sabotage rows; 6 spec hunks; 1 abi event; emitted text about 0.4 KB per eligible site at the scalar layer and about 1.3 KB more at w32 (both UNMEASURED estimates); memfn/src code a few hundred lines, UNMEASURED.

## OPEN QUESTIONS
None from rev 1. Owed to main: the cover-width timing (cover_cap.md §11.4 B) that decides whether the default window width rises. Judgment to flag: the code-line and per-site byte figures in §17 are estimates, not counts.

## OWED RUNS
none (the U2b census and timing are build-lane steps, not owed by this lane).
