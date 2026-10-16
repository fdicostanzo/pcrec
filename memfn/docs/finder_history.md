# The kit's candidate-finder table: edit history (D161 addenda 11 and 13)

The kit owns the rows of the knowledge-filtered candidate-finder table
(D161 add. 11). Until LOCKDOWN (the table that passes [REGIME-EVAL]'s judge
and ships with R17-b′'s routing), the kit edits rows on evidence without a
per-row proposal to Frank (D161 add. 13). Each edit is logged here: the row,
what changed, the evidence, and the commit. Main mirrors it in
docs/design/regime_tables.md. After lockdown, an edit is a formal ruled diff
with evidence, its replay delta and a mover census. The table's source of
truth becomes `fd_rows[]` (docs/design/memfn/r17b_prime.md §1) when E3 lands;
until then the rows are those of regime_tables.md as the kit has corrected them.

| date | row | edit | evidence | commit |
|---|---|---|---|---|
| 2026-10-13 | R3 | split into R3a (span < ~14 B → WALK) and R3b (14-32 B → A3) | gridread §4.2 (A3's L* 14-19 B; A3 loses to the walk at L ~ 8) | 7b54791db (applied on main a3c861852) |
| 2026-10-13 | R0 | added (SIMD off, ≥ 2 RANGE terms → WALK) | gridread §2.1, L3 (3-term V1 β 0.214 > walk 0.189) | 7b54791db |
| 2026-10-13 | R4-R6 | g* keyed per site kind, not the PF figure | gridread §4.1 | 7b54791db |
| 2026-10-14 | R3a/R3b | marked PROVISIONAL (replay cannot score per-step rows) | regime_eval §8 F-5/F-7 | e8db7c810 |
| 2026-10-14 | R8 | added (the amended-D2 DINGHY row: L ≥ ~16-32 B AND g ≥ ~4 B → W=64) | gridread §6.3 D2; regime_eval §8 F-2 | e8db7c810 (id assigned by main, rev 0.4) |
| 2026-10-14 | R8 | `needs` corrected from {P,N,M,A} to {P,N,M,E,A}: its condition reads g, an E fact (or H under the iterator). Its L bound, once declared, is a set value that the `lines` buckets derive their edges from (regime_eval T19) | regeval4 finding | this commit |
| 2026-10-14 | F0, F1 | designed (rev 2): F0 `none` (NONE where span 0 is OPTIONAL and E measured, M22), F1 `libc-m` (a measured libc-free form dominating libc, M19-M21); built at B5 as formal additions (r17b_prime F21) | r17b_prime.md rev 2 §1.3; D161 add. 14, 15 | c90d65e53 (logged late, 2026-10-16, panel r1 B9) |
| 2026-10-14 | D1, D2 | added (rev 2): D1 `default-1b` (Q-WR-1's UNMEASURED-DEFAULT, today's count rule), D2 `run` (handoff landmarks, the nested `fn_rows[]` walk) | D161 add. 15 Q-WR-1; KW-1 | c90d65e53 (logged late, B9) |
| 2026-10-14 | PRES slot | added (rev 2): P0 required, P1 priced, P2-P4 pcrec's ported picks, P9 default (not regime rows; not mirrored) | D161 add. 14 clarification; KW-8; Q-WR-9 | c90d65e53 (logged late, B9) |
| 2026-10-14 | R1 | keyed against the TERMINAL pick (`xover(t, WALK)`), not V1 regardless | r17b_prime F13 | c90d65e53 (logged late, B9) |
| 2026-10-16 | R1, R2 | apply only above a FAST terminal (V1, W64), as row data: key absence no longer keeps one-byte sites zero-mover | panel r1 B14, C1 | lane r17bp4 (r17b_prime rev 3) |
| 2026-10-16 | D1c | added: MLINE's stop is a one-byte CONTEXT predicate with no span 0 → LIBC back (UNMEASURED-DEFAULT) | panel r1 A5; window_contract §2.5; D161 add. 7 | lane r17bp4 |
| 2026-10-16 | D1w | added: one member → WALK (the VM hat's \|S\| = 1 seek, today's Q-R5 rule; `fd-d1`'s OFF arm elsewhere) | D167 add. 1 A7; panel r1 A17, B7 | lane r17bp4 |
| 2026-10-16 | F2 | designed: the VM hat at \|S\| = 1 → V1 where grid2's VM_ATTEMPT one-byte cells show the saving; built at B5 | D167 add. 1 A7 | lane r17bp4 |
| 2026-10-16 | R7, R7w | R7 gated on its shape's measured saving key (an unmeasured shape does not hold); R7w (always → WALK, main's form) added as the OFF fallback | panel r1 C3 | lane r17bp4 |
| 2026-10-16 | R5 ∪ R6, R7 ∪ R7s | merged: one row each over "the layer's LINER form" (V1 at OFF, W64 at W16/W32) | panel r1 D8 | lane r17bp4 |
| 2026-10-16 | all | conditions re-expressed as ONE comparator (lhs, op, key) plus boolean site facts, every threshold a set key; PRES picks as chain-link attributes; mandatory `basis` and `refuted_by` columns; applicability moved into the gate (`fd_rows[]` is a `kit_table`) | panel r1 D1, D2, D3, C2, D11 | lane r17bp4 |
