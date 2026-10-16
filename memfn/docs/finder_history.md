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
