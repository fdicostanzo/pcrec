# Search-form selection by regime — ONE first-match table, filtered by knowledge (rev 0)

Status: DRAFT rev 0 (Frank + manager, 2026-10-13, session 112). Not built, not ruled
beyond its shape. Evidence: docs/dev/lanes/regimefacts_report.md,
docs/dev/lanes/armread_report.md, the kit's costmodel_report.md (lane/memfn-r17
abfece617) and gridread_report.md (lane/memfn-r17 137499324). All constants are
Zen 4 (the Linux dev box); the official verdict on any row is a run on the targeted
hardware (D144 add. 4). Form ids V1/A1/A3 are the kit's (D157: pcrec sends facts;
the kit owns its forms and checks these rows).

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

| key | what | when known | cost |
|---|---|---|---|
| P | pattern/site facts: terms, range-term count, site kind, SIMD layer | compile | free |
| N | the call's span `n - startpos` | call entry | free (one compare) |
| M | mode: one-shot `_search` vs the D165 iterator `next`/`next_n` | call entry | free |
| E | exemplar landing gap `g` (bigram landings in the analysis bundle) | compile, optional | bundle field |
| H | iterator history: previous step's span; candidates per block (mask popcount) | run time, iterator only | one compare per call/block (F7 prices it) |

Note: without M = iterator, N in a find-all loop is the REMAINING subject, not the
step span; dense find-all is then invisible at call time.

Knowledge strategies (filters): S0 "idk" = {P, N, M}; S1 = S0 + E; S2 = S0 + H;
S3 = S0 + E + H.

## 3. The table

Regret = measured pick minus the fastest form, % of the walk, DINGHY / TUG / LINER
(gridread §6.2). Forms: WALK (scalar table walk), V1 (SWAR W=8), A1 (W=64: AVX2,
else SSE2), A3 (A1 with state kept across iterator calls).

| id | needs | condition | pick | evidence | refuted by |
|---|---|---|---|---|---|
| R1 | P,N,M | one-shot, n < 32 B | WALK | single call pays from ~18-20 B (gridread §4.3) | a W=64/V1 win at n < 32 on fresh text or Zen 1 |
| R2 | P,N,M | one-shot, 32 <= n < 64 | V1 if emitted, else WALK | W=64 loses +1.3..+15.8 ns below a block; V1 wins at 48/63 (§4.4) | V1 loss at 48/63 out of sample |
| R3 | H | iterator, previous step span < ~16 B | A3 | only kept forms win at L = 8 (§5.6; D3) | F4: the real iterator does not reproduce A3's hand-edit win |
| R4 | H | iterator, block popcount says g < 4 B (SIMD on) / < 11-21 B (SIMD off) | WALK for that block | the g row, learned (§4.1) | F7: observation cost exceeds the regret it removes |
| R5 | E | SIMD on, g < 4 B | WALK | W=64 g* 4.2-4.7 B repeated (§4.1) | fresh/irregular text (g* -> 2-4 B), Zen 1 |
| R6 | E | SIMD off, g < 11-21 B | WALK | V1 g* (§4.1); FRAGILE: 14% regret out of sample | the bench's TUG cells; F2 (walk bimodality) |
| R7 | P | otherwise | LINER: A1 (SIMD on) / V1 (SIMD off) | always-A1 11.1/1.2/0.0; always-V1 18.8/16.6/0.1 (§6.2) | fresh real text tilting the other way (X2) |

Regret by filter (measured, in sample; LOGO/out of sample in brackets):

| filter | SIMD on | SIMD off |
|---|---|---|
| S0 {P,N,M} | 11.1 / 1.2 / 0.0 (find-all; R1/R2 only help one-shot) | 18.8 / 16.6 / 0.1 |
| S1 +E | 6.6 / 0.1 / 0.0 | 2.7 / 0.4 [14.0] / 0.1 |
| S2 +H (hint form) | 5.6 / 1.2 / 0.0 | — (V3 never ranks first) |
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
