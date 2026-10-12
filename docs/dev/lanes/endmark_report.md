# endmark — D164 design note (lane report)

Lane `endmark`, 2026-10-12, opus. Branch `lane/endmark` from main `885eccff`
(abi 76). Design only: nothing under `src/`, `cli/`, `lib/`, `tests/` or
`docs/spec/` changed.

## Delivered

- `docs/design/endmark.md`, the design note (registered in
  `docs/design/CLAUDE.md`).
- `docs/design/endmark/` holds the instruments and transcripts (own CLAUDE.md):
  - the libpcre2 lowering differential;
  - the B3 twin;
  - the census probe and driver;
  - `results/`.

## Validation (all complete; no clock read, no `make test`; `make -j8` built
the worktree's compiler for the probe)

| what | result |
|---|---|
| lowering vs libpcre2 10.46 (`diff_lowering.py --set all --len 5`) | 3,527 patterns, 28,237,887 cells, **0 differences** |
| its six plants (`results/diff_plants.txt`) | 296 to 54,054 differences each (all red) |
| twin part A, forward accept-distance vs libpcre2 | 120,304 cells, 0 differences; the plant gives 3,811 |
| twin part B, rev-end today / tagged+`mark_prio` / untagged+forward vs libpcre2 | 10 patterns × 4,005 subjects, 0 wrong in each strategy; three plants red |
| B3 counted loads (k = 16,000) | `\s+$`, `\s*?$`: 3.00× today → 1.00× (tagged + fact) / 2.00× (untagged); state-dependent shape 3.00× → 2.00× |
| census probe vs shipped engine stamp, VM → DFA set | 0 disagreements |

## Findings (the note's §9)

- **F1.** D164's "no tags, no tie special case" over-claims. A reverse walk cannot
  see priority. One seed holds. The tie becomes the general multi-distance case,
  decided by the static fact `mark_prio` (constant on every common shape) or else
  by FINISH.
- **F2.** A capture that encloses the mark must close at the mark. This is a
  report-time rule; planted, it costs 2,858 cells.
- **F3.** The VM hybrid's window ceiling must stay the CONSUMED end.
- **F4 (live on main, worth a K entry).** `RX_ENGINE_WHY`'s offset goes stale
  after the free atomic discharge. `--features all 'a++b(?<=ab)'` stamps
  "(?<=...) at pattern offset 2", while the lookbehind is at 4.
- **F5.** The unlock is narrow: 2 bench (`syntax/lka-pos`, `lka-verb`) and 22
  corpus patterns go VM → DFA. One-character tails have been `A_CTX` since U2.
- **F6.** Zero-width tails (`z(?=)`) drop out with no mark.

## Owed / not done

- Sabotage ids are NOT taken. The note's §5.6 needs 12 new ids, plus re-aims of
  S758-S760 and S765-S767 derived at build.
- The forward `$` state-count census (E3's gate under Q1's uniform form) needs a
  build of the lowering. It is not measured here.
- The bench pair's timing is a direction only, owed to a bench window.

## Questions for Frank (the note's §7, discussion form)

- **Q1:** should `$` lower on every consumer? I lean uniform, gated on a forward
  state-count census.
- **Q2:** should D164's consequence sentence be amended (tags and ties)?
- **Q3:** should unbounded Y stay a lookahead (L4)?
- **Q4:** should visibility be limited to facts and IR, with no stamp?
