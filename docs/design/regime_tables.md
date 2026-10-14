# Search-form selection by regime — ONE first-match table, filtered by knowledge (rev 0)

Status: DRAFT rev 0.5 (rev 0.5: R8 needs E, its g fact; kit finder_history.md 3759b02c5). Was rev 0.4 (rev 0.4: kit panel r1 B-5/B-6: A = the measurement SET id, ISA a separate fact; the amended-D2 row is R8). Was rev 0.3 (rev 0.3: the kit's replay corrections, regime_eval.md §8 @ e8db7c810). Was rev 0.2 (rev 0.2: role, owner column and arch key A per D161 addendum 11). Was rev 0.1 (Frank + manager, 2026-10-13, session 112; rev 0.1 applies the kit's
row check, memfn/docs/responses.md on lane/memfn-r17 7b54791db). Not built, not ruled
beyond its shape. Evidence: docs/dev/lanes/regimefacts_report.md,
docs/dev/lanes/armread_report.md, the kit's costmodel_report.md (lane/memfn-r17
abfece617) and gridread_report.md (lane/memfn-r17 137499324). All constants are
Zen 4 (the Linux dev box); the official verdict on any row is a run on the targeted
hardware (D144 add. 4). Form ids V1/A1/A3 are the kit's (D157: pcrec sends facts;
the kit owns its forms and checks these rows).

## 0. Role (D161 addendum 11)

This document is the JOINT CONTRACT between pcrec and the kit, not a pcrec selection.
The knowledge keys (§2) are the interface: pcrec PRODUCES them. The pick rows (§3) are
the KIT's decision (D157: pcrec sends facts, never the method), the seed of the kit's one
candidate-finder table over (stop, form); the kit's own copy is the source of truth and
this one mirrors it. pcrec's own decisions over the same knowledge (the origin, engine and
route, the iterator/batch API) live in pcrec's tables (`cand_rows[]`), not here.

## 1. Shape

One table. Each row declares the KNOWLEDGE it needs. Selection = the first row, in
order, whose knowledge is available AND whose condition holds. The "knowledge
strategies" (what a given artifact/call can know) are FILTERS on the same table,
never separate tables (Frank: "4 logical tables but it is really one table filtered
on knowledge strategy").

- **Default row last: LINER** (the widest emitted form). The onus is on knowledge to
  move a call off it (Frank, 2026-10-13).
- **Emission is derived:** an artifact emits the union of the picks over the rows
  reachable under the knowledge it can ever have. No separate emission table.

## 2. Knowledge (the filter's vocabulary)

| key | what | when known | cost | producer / channel |
|---|---|---|---|---|
| P | pattern/site facts: spans bounded to the origin, terms, range-term count, site kind, SIMD layer | compile | free | pcrec / the site description |
| N | the call's span `n - startpos` | call entry | free (one compare) | pcrec entry / kit body argument |
| M | mode: one-shot `_search` vs the D165 iterator `next`/`next_n` | call entry | free | pcrec API (D165) |
| E | exemplar landing gap `g` (bigram landings in the analysis bundle) | compile, optional | bundle field | pcrec-analyze / the analysis object (D162) |
| H | iterator history: previous step's span; candidates per block (mask popcount) | run time, iterator only | one compare per call/block (F7 prices it) | storage pcrec (rx_iter S, D165); content kit |
| A | the MEASUREMENT SET id (D166 item 3): the set whose relative constants the rows read; an unmeasured box reads the derived generic envelope set (D161 add. 12), listed with provenance | compile | free | pcrec loads the set (`--measures=`, [MEASURE-SET]); the set's rows are the kit's, measured |
| I | ISA availability (which forms CAN run: SSE2/AVX2/AVX-512/NEON), a separate fact from A | compile | free | pcrec passes the declared target ISA |

Note: without M = iterator, N in a find-all loop is the REMAINING subject, not the
step span; dense find-all is then invisible at call time.

Measured A today: Zen 4 (AVX2, SSE2). Zen 1: F5 (bench window). Mac NEON, Intel, AVX-512: none.

Knowledge strategies (filters): S0 "idk" = {P, N, M}; S1 = S0 + E; S2 = S0 + H;
S3 = S0 + E + H.

## 3. The table

Regret = measured pick minus the fastest form, % of the walk, DINGHY / TUG / LINER
(gridread §6.2). Forms: WALK (scalar table walk), V1 (SWAR W=8), A1 (W=64 AVX2), A3 (A1 with state kept
across iterator calls). S1/S3 (W=64 SSE2) are DISTINCT arms, not A1's fallback spelling: SSE2
regrets more (TUG 2.8% vs 1.2%; a larger sub-block tail) [kit 0.1]; where AVX2 is absent the
rows read S1/S3 with their own thresholds, owed per box (F5).

Every pick row below is KIT-OWNED (owner column omitted: all rows = kit). Thresholds are
per (form, site kind, A); the numbers shown are A = Zen 4.

| id | needs | condition | pick | evidence | refuted by |
|---|---|---|---|---|---|
| R0 | P | SIMD off, site has >= 2 RANGE terms | WALK | SWAR saving ~0 at 2 range terms; 3-term V1 0.214 vs walk 0.189 ns/B (gridread §2.1/§5.8) [kit 0.1] | a 2-term V1 win out of sample |
| R1 | P,N,M | one-shot, n < 32 B | WALK | single MEMBER-FREE call pays from ~18-20 B (gridread §4.3); with landings in the call the crossover moves past 32 B [kit 0.1] | a W=64/V1 win at n < 32 on fresh text or Zen 1 |
| R2 | P,N,M | one-shot, 32 <= n < 64 | V1 if emitted, else WALK | W=64 loses +1.3..+15.8 ns below a block; V1 wins MEMBER-FREE calls at 48/63 (§4.4) but loses dense ones [kit 0.1] | V1 loss at 48/63 out of sample |
| R3a (PROVISIONAL) | H | iterator, previous step span < ~14 B | WALK | A3 still loses to the walk at L ~ 8 in most cells (dig g64 +9.6 us, dfa-hat g4 +17 us); it only beats A1 there [kit 0.1] | F4/F7 |
| R3b (PROVISIONAL; SIMD-on only) | H | iterator, previous step span ~14-32 B | A3 | A3's measured L* 14-19 B (gridread §4.2) | F4: the real iterator does not reproduce A3's hand-edit win |
| R8 | P,N,M,E,A (H under the iterator) | amended D2: L >= ~16-32 B and g >= ~4 B | W=64 | gridread §6.3 D2; the kit proposes the row (replay F-2, regime_eval.md §8: without it S3-on DINGHY is 6.0%, not 0.5%) | replay on J1 |
| R4 | H,P | iterator, block popcount says g < g*(site kind, layer) | WALK for that block | the g row, learned (§4.1) | F7: observation cost exceeds the regret it removes |
| R5 | E,P | SIMD on, g < g*(site kind) | WALK | g* per site kind: PF one-term 4.2-4.7 B; dfa-hat/bounded ~2-3 B; fresh irregular text 2-4 B (§4.1) [kit 0.1] | fresh/irregular text (g* -> 2-4 B), Zen 1 |
| R6 | E,P | SIMD off, g < g*(site kind) | WALK | V1 g* per site kind: PF dig 11-17 B, bounded 21 B, dfa-hat 3.0-3.3 B (§4.1) [kit 0.1]; FRAGILE: 14% regret out of sample | the bench's TUG cells; F2 (walk bimodality) |
| R7 | P | otherwise | LINER: A1 (SIMD on) / V1 (SIMD off) | always-A1 11.1/1.2/0.0; always-V1 18.8/16.6/0.1 (§6.2) | fresh real text tilting the other way (X2) |

R3 is PROVISIONAL (replay F-5/F-7): the split is not supported on per-pass H (the old-R3 control is not worse; deleting R3b improves regret); it waits for per-step H from the iterator or the twin. R0 and R1 are unreachable on the grid; the evaluator adds witness cells.

Regret by filter. CORRECTION (rev 0.3): the S1-SIMD-off, S2 and S3 figures below are gridread's MODEL policies (an. 7.2), NOT what the declared rows do. Replaying the declared rows (regime_eval.md §8): S0 reproduces exactly; S3-on DINGHY is 6.0% (missing the amended-D2 row); S2 SIMD-off loses to always-walk (10.5% vs 2.4%) because R3 has no SIMD-off arm, so S2 is SIMD-on only.

| filter | SIMD on | SIMD off |
|---|---|---|
| S0 {P,N,M} | 11.1 / 1.2 / 0.0 (find-all; R1/R2 only help one-shot) | 18.8 / 16.6 / 0.1 |
| S1 +E | 6.6 / 0.1 / 0.0 | 2.7 / 0.4 / 0.1 (in sample; the [14.0] LOGO belongs to gap+span, row S3) |
| S2 +H (the hint A3/A1/A1; in-sample UPPER BOUND, LOCO 14.6% in DINGHY) | 5.6 / 1.2 / 0.0 | — (V3 never ranks first) |
| S3 +E+H | 0.5 / 0.1 / 0.1 [1.5 / 1.1 / 0.1] | 1.5 / 0.4 / 0.1 [5.1 / 14.0 / 0.1] |

## 4. Answers recorded with the shape (Frank's points, 2026-10-13)

1. **Islands under a LINER pick:** worst case ~3.5 ns extra per island landing
   (c_cold 2.3-2.9 + ~1 ns overscan) against 0.18 ns/B saved elsewhere: LINER wins
   while there are > ~20 sparse bytes per island landing. Irregular islands favour
   the forms further (the walk pays +4-7 ns per unpredictable landing); inside the
   iterator, island landings are served from the kept mask at c_warm 0.4-1.0 ns.
2. **"idk" is S0, not nothing:** P, N and M are free. What it lacks is the gap.
3. **Default LINER:** SIMD on it is the clear minimax; SIMD off it is close on the
   grid, and the grid's repeated buffers flatter the walk (gridread X2), so real
   text leans LINER.
4. **Adaptivity, by grain:** selection on call-known facts (N, M) is not adaptation
   and is always in; observation at call/block grain (H) is ON TRIAL (F7); the
   per-use switch (setfind §9.1, 1.6-3.2x) stays OUT.

## 5. Owed (to prove or refute rows)

- F4, F7 and D165's dense-tiny-match parity gate (R3, R4) — after the iterator builds.
- F5 Zen 1 constants via a bench window (every W=64 row moves).
- Fresh real-text population (X2) and the bench's population re-scored by the table.
- F2 branch-miss counts (needs `kernel.perf_event_paranoid` lowered; Frank's call).
- Not covered by any grid yet: near-hit depth, bytes-vs-landings decoupling, the
  multi-position filters (T3), real text's predictable/unpredictable mix.

## 6. Standing questions (docs/design/CLAUDE.md)

1. **Measurement regime:** every number is Zen 4, gcc 15.2, find-all and single-call
   passes over synthetic 64 KiB subjects (repeated or streamed) plus the kit's real-text
   cells; regret is in-sample unless bracketed. Zen 1 (AVX2 as 2x128) is expected to
   move every W=64 row (F5); fresh irregular landings move every g* down (gridread
   §5.3). Both can flip rows R1, R5, R7.
2. **Independent control:** the regret figures are measured ns of the fastest
   applicable form, not the model's prediction; the out-of-sample checks are LOGO/LOCO
   refits, F5 on other hardware, and the bench population (which no table row was
   fitted on).
3. **What moves when regenerated:** nothing yet — the table is not built. When built,
   its constants (L*, g* thresholds) are declared row data; re-measuring them is a
   ruled row diff, and any change to an emitted selection is an abi event with its
   spec hunk.
