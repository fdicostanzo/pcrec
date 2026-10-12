# Lane wingame2: report

Lane `wingame2` (2026-10-11, branch `lane/wingame2` from main `30b8892a`). Brief: add
Frank's P6 `refine` policy (scan the rare span, bound and locally search the tight
span; forward search where the gap is unbounded; presence gate question) to the D161
window-search game. Design study: nothing under `src/`, `memfn/` or `tests/` touched.
COUNTS ONLY. The first lane's files were staged but uncommitted in main's index, so
they were copied read-only from main's working tree into this worktree (first WIP
commit) and extended.

## Deliverables

- `docs/design/memfn/window_search_game.md` section 8 `[wingame2]` (plus a bullet in
  section 0).
- Instruments: `spans.py` (`item0`, `rel_from_items`), `game.py` (P6, `Plan`,
  `simulate_plan`, `simulate_gate`), `run_game.py` (11 two-span witnesses as set `wit2`,
  `refine.tsv`, `relcontrol.tsv`), `summarize.py` section E, `chain.sh` (`PCREC=`
  reuse), `window_search_game/CLAUDE.md`.
- Data: `window_search_game/data/{refine,relcontrol}.tsv` and the P6/wit2 rows in the
  other TSVs; `data/summary.md` sections E0-E5.

## What was run

`run_game.py` over the 327 patterns plus 11 witnesses with main's `build/pcrec` (no
build here, no -j16), about 30 s, no clock read. Controls: (1) sections A-D of the
summary are byte-identical to the first lane's for the original 327 patterns (the
P1-P5/SHIPPED rows in `sim`, `choices`, `spans`, `spaninfo`, `spanforms` diffed
equal); (2) the derived relative distance agrees with a direct item walk on 152 of 152
span pairs. `chain.sh` itself was not re-run end to end; its steps were run by hand
(same commands), and the script only gained the `PCREC=` switch.

Not touched because main's index holds them mid-merge (`docs/dev/lanes/CLAUDE.md` is
`UU`; `docs/design/memfn/CLAUDE.md` is staged there): the index entries for
`wingame2_report.md` and a `window_search_game.md` pointer. The main session should add
them when it resolves that merge.

## Answer

1. Bounded gap: needs NO new contract fact. Relative distance is
   `[omin_B - omin_A, move_back_B - move_back_A]`, uncertainty
   `overshoot_B - overshoot_A` (tighter than the independent `ov_A + ov_B`, which
   costs 1.4x-2x on `.{0,6}\d.{0,3}#`).
2. P6 beats the single-span policies by 3x-6x (VM / per-start consumer) when span 1's
   overshoot is ~0 and span 2's is large: `\d{3}.{0,4}#` 3.1x, `\d{2,4}.{0,12}#`
   4.3x (5.2x merged), semi-rare-A witness 6.2x. Under a DFA (per-byte) consumer it
   ties at best and is 0.5x-0.76x unmerged; merged it is 0.88x-1.07x. It loses when
   A itself has overshoot (0.37x-0.7x).
3. Population: P6 picks a plan on 9 (dfa) / 10 (vm) of 327 patterns, one real
   (`syslogbase-expanded`, 1.40x vm over P5 and SHIPPED) and the rest tiny test
   patterns; it changes nothing on loglines.
4. Unbounded gap: P6 = P5. The forward search for a digit class loses to stepping every
   byte for a DFA consumer (0 of 16 witness cells pay), wins for a VM. A presence gate
   pays only when the rare byte is ABSENT (7 of 45 unbounded cells; then 7.9 K against
   0.7-15.7 M); the continuous gate is a net loss in 13 of 29 population cells, the tail
   form never loses (0 of 158 cells).
5. Contract: the reply must name which span's `(move_back, overshoot)` the window
   carries (scan span != window span). The consumer price is needed more; the survivor
   estimate is the weak term (local A hits per B stop are 7x-900x under the table), so a
   conditional rate or a floor of one window per B hit is needed.
