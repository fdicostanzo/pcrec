# regeval3 — [REGIME-EVAL] regime_eval.md rev 1 -> rev 2 (D6 panel r1 applied)

Lane regeval3, 2026-10-14, branch `lane/memfn-regeval3` cut from `lane/memfn-r17`.
Docs only, plus `docs/design/memfn/regime_eval/rev2_arith.py` (arithmetic over one
finished file). No timing, no make, nothing under `src/`, `memfn/src/`, `tests/`,
`lib/`. pcrec-bench read with `git show` only, at db629a54.

## Delivered

- `docs/design/memfn/regime_eval.md` rev 2: every one of the panel's 33 ids applied and
  marked in place `[r1 <id>]` (each id has at least one mark; 146 marks), §R maps id →
  section, §R.1 the bars before/after, §R.2 the items relayed to main.
- `docs/design/memfn/regime_eval/rev2_arith.py` + `rev2_arith_out.txt`: the CB spread
  over K = {walk, V1, A1} and condition 3b from `gridread/f2_counts.txt`; the judge
  wall formula and the five-slot split.
- `memfn/CLAUDE.md`: three boundary-table rows (the regime table and its knowledge
  keys; the measurement set, owner split per T18; the evaluator, census and verdict).
- `docs/design/memfn/CLAUDE.md` and `regime_eval/CLAUDE.md`: entries updated.

## The bars as now formulated (§3.0-§3.1)

Walk-cost units (÷ the walk's ns on the same cells); noise N(S) = √Σ_groups(Σ_cells
NULL)², linear within a group, quadrature across groups; allowance 2·N; cross-fit
regret; NULL_c = max(A/A, ν·walk), ν re-derived per slot from walk vs walk#c.
G0: ≥ 20 RT cells from ≥ 5 patterns per layer×regime×filter, else UNREACHED; RT-share
weight floor 0.25. G1: R_T − R_P ≤ 2·N over the cells where table and P differ.
G2: R_T/W_exCB − 2N/W_exCB ≤ 1.25·R_in + 2 (DINGHY/TUG), R_in + 1 (LINER), R_in from
grid2's streamed in-sample replay. G3: per pass ns_pick − ns_walk > max(3·w_call,
0.25·walk) (per call too for first/lines); ≤ 5% of non-CB RT cells and excess ≤ 0.25 ·
max(0, saving). G4: scorable controls WORSE per moved cell (Δ > 2·N, m_min 5), C7
split-half, C8 null mutation exactly zero; R3a/R3b/R4/C2 UNSCORABLE (twin-owned).
Power floors give UNDERPOWERED → INCONCLUSIVE, never PASS.

## Owed elsewhere

- zen4-grid2 must carry: streamed re-time of the F1/F3 fit cells (all pickable arms,
  both layers, walk#b, walk#c), perf on K for them, the F2 streamed perf pass (3 cells
  × 4 arms × 3 classes), and the 30-group FIT anchor subset (~61 min). E5 waits.
- E3 owes: the shadow trace call, the row denies with their D80 hunk and the memfn
  floor pin, the pending row's id.
- Relays: Q-REVAL-13/14/15 and §R.2's items to main and the bench dev.

## Open questions

Q-REVAL-12 (wall/slots), Q-REVAL-13 (`RD2`), Q-REVAL-14 (A vs I), Q-REVAL-15 (J2a
subjects, for the bench dev), Q-REVAL-16 (rev 2's chosen constants).
