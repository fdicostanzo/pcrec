# spanarms3 report: docs/design/span_arms.md rev 2 (review 2026-11-08 r2 as ruled)

Lane spanarms3, opus, 2026-11-08. Design and single-pattern measurement only (NO BUILD GO: nothing
under `src/`, `cli/`, `lib/`, `memfn/`, `tests/` touched). Base: main `c054e38e7` (no code drift
since rev 1's `dd2fe2de9`). One `nice make -j2` of the worktree; no suites. Evidence:
`docs/dev/lanes/spanarms3_evidence/` (`oracle1-3.out` through `tests/lib/p2probe.c` against
libpcre2-8 10.46, driver `or.sh`; `facts_w.out`, `facts_w2.out`, `facts_extra.out` from the lane's
`build/pcrec`, driver `facts.sh`).

## Summary

Rev 2 answers all 16 findings of the r2 re-check plus its standing questions. The design choices
the review left open are now made:

- **S2, decided (a):** ITEM reads the producer's item for every positive one-sided context, so an
  `A_LOOK` and the `A_CTX` NEXT/PREV that `ctx-node` makes for one-character bodies give the same
  run. The run no longer differs under `-fno-ctx-node`, and L1's gate checks that (W-C1). Premise
  test held: `a(?=b)c` lists `kinds none`, `RX_DFA_SCAN "empty"`.
- **S8, as ruled:** ONE producer of exact per-offset sets. Its item half is the body's DESCRIPTION
  (`desc.c`, whose positions are exact 256-bit sets, unmoved by bit 44, measured) placed at the
  cursor and united per offset across width groups. That is `look-fixed`'s fact, and it also
  covers bounded variable bodies as SUPERSET. Its in-span half is kset's frontier, already built.
  The guard is a reader that takes the cube hull within `pos_set`. The D168 addendum text is in
  §12. **Flag for the manager:** I read "signed offsets from the attempt start" as fixing the
  FACT and its signed range, with the item's CURSOR as the producer's origin (ctx_span §3.3's own
  coordinate). Under a strict attempt-start origin the guard could read only items at a fixed
  attempt offset, and every mover after a variable-width piece would be lost (§5.3).
- **S9, as ruled:** a declared walk-parameter table (`pos_set`, `max_pieces`, reach, restored
  arms, `lb_bytes`; the sources are public bit 44, harness arms, `limits.def`, `Ctx`), filled at
  the one walk entry `facts.c:208-211`. The deny column keeps its meaning (`pf_enter` empties a
  fact). The table is listed through a new §4.1.3 token, `harness:<arm>`.
- **S4, as ruled:** row CAT-SET puts a narrowed consumed byte into `req_set`. At L2/L3 the scan
  member is picked among consumed positions (`RbRun.cons`, new row A13).
- **S1:** the r2 review's one forced error is fixed in A3's cell: `max(posvar, c − K)`, signed,
  plus the re-ask condition. W-L10 `(?<=ab)ab[a-z]*q` on `abababq` from 3 gives M 4 7; the rev-1
  move would report (2,7).
- **S6:** a DEAD column, carried as a `dead` why on `req_whole_run`. **S5:** guards keep the end
  nearest their edge, and TOP's `++` keeps the first positions. **S7:** the BACK floor is the
  kit's (A2), and the L3 kit request is worded as facts with the origin at the attempt start.
  **S10:** `lb_bytes` is a per-call step-back cost cap, per encoding. The nested-lookbehind
  read-back is libpcre2 NON-UTF behaviour only (UTF: `(?<=c(?<=bc)d)e` from 3 is N, measured).
- Witnesses: the six that could not fail are re-spelled with multi-character bodies, and W-L5 and
  W-RG with non-`cover` shapes. New witnesses: W-C1 (`A_CTX`), W-L10, W-T1..W-T3, W-S4/S4b and
  W-D1..W-D6 (FACT), and W-E3 (E2's own). Every witness has its oracle answer, `kinds`,
  `RX_DFA_SCAN` and the k-set position that keeps the sabotaged run unpinned, all measured. Every
  sabotage spelling lists a run (it clears the floor).

Observation, not probed (outside this note): pcrec's utf8 compile of `(?<=c(?<=bc)d)e` has
`_VALID_LB 2`, and libpcre2 UTF answers N from offset 3. Whether pcrec's utf8 matcher agrees from
offset 3 was not run (the `--emit-main` driver starts at 0). It is a candidate compatibility probe
for the manager.

## Disposition table

| finding | ruling | rev 2 change | where in the note |
|---|---|---|---|
| S1 | FIX-NOW | A3's move is `max(posvar, c − K)`, signed, no `size_t` wrap; the re-ask runs while `c − K < pos`; ¶11's formula is kept for signed K; the two emitters are L3 sites; W-L10 | §5.4 A3, §5.7, §8 L3, §9 |
| S2 | FIX-NOW, (a) | ITEM covers `A_LOOK` positive and `A_CTX` NEXT/PREV (other functions stay E-4); the six witnesses are re-spelled; W-C1 and the `-fno-ctx-node` identity gate; §5.2 (b)-(d) and §5.6 re-derived | §0, §2, §5.1, §5.2, §5.6, §5.7, T1, T3 |
| S3 | FIX-NOW | W-L5 `xy(?=bc)[bc]c` and W-RG `(?:abc(?=ab)){2}`, both VM `unanchored`; the mechanism sentence adds the locator condition, and every row states its scan | §3.6, §5.7 |
| S4 | FIX-NOW (RULED) | CAT-SET at L1; the consumed-only pick (`cons`) at L2/L3; A13; W-S4 and W-S4b | §5.2, §5.4, §8, §9 |
| S5 | FIX-NOW | the §2 sentence (bound, kept end, `trunc` unread, saturation); TOP's `++` is `rn_app`, `t` the stored `lg.n`; W-T1..W-T3 | §2, §5.2, §5.7 |
| S6 | FIX-NOW | the DEAD column, the root's bit, the `dead` why token; W-D1..W-D6 | §5.2 (g), T4, §8, §9, §10 |
| S7 | FIX-NOW | A2 is the kit's two uses; the L3 kit request is worded as facts, with the origin at the attempt start; W-L1 is the kit's witness | §2, §5.4 A1-A2, §5.7, §8 L3 |
| S8 | FIX-NOW (RULED) | the producer = the description placed at the cursor (item half) plus kset's frontier (in-span half); the guard is a reader; the D168 addendum text; the coordinate flag | §5.1, §5.3, §12 |
| S9 | FIX-NOW (RULED) | the walk-parameter table at the one entry; the deny column unchanged; the `harness:` token | §3.7, §5.8, §8, §9 |
| S10 | DOC (RULED) | the cost-cap purpose, per encoding; the UTF fact corrected | §5.5, §13 Q5 |
| S11 | DOC | L3's spec hunks named by paragraph | §8 L3 |
| S12 | DOC | ledger rows; the `req_run_omin` facts.def row | §5.4 A9, §9 |
| S13 | FIX-NOW | L1 depends on E2, E1 (W-F4) and R1 (the REP row, W-RG, W-T1); the table is built by the first of 2a/E1/R1/E2/L1 | §8 |
| S14 | FIX-NOW | W-L4 and W-L8 are in L1's gate | §5.7, §8 |
| S15 | DOC | A1 drops `site_kind_of`; A9 cites `facts.c:236` | §5.4 |
| S16 | FIX-NOW | the T3 sentence (E-5 is the unit under E2) and W-E3 `xy(?<!ab)cd` | §4.1, §4.4, §4.5, §8 E2 |
| standing: walk inputs | in S9 | the table | §3.7 |
| standing: none sentinels | DOC | L3's gate: a stated/none bit on every signed offset | §8 L3, §9 |
| standing: U-exactwidth | PLAN | a §10 row with its trigger | §10 |

## Rev 2 changes by section

- Header: rev 2 status, base `c054e38e7`, readiness as ruled. New §R2 table (the 16 findings plus
  the standing questions).
- §0: two premise bullets: the `A_CTX` lowering, and the description's exact sets being unmoved
  by bit 44.
- §2: the scan floor is the kit's, with the origin at the attempt start (S7). The guard storage
  sentence (S5). The arms table's lookaround row covers both lowerings.
- §3.6: the locator condition in the mechanism sentence (S3). §3.7: the walk-parameter table (S9).
- §4.1: the E-4/E-5 rows by function, plus the S16 sentence. §4.4: the E-5 label. §4.5: W-E3.
- §5.1: the item as the producer's, the guard as a reader, one lowering giving one run.
  §5.2: CAT-SET, the DEAD column, TOP's `++` and `cons`, cases (a)-(g) re-derived, and the
  variable-body paragraph re-homed to the description. §5.3: rewritten (the producer's two
  halves, the coordinate flag, storage and bounds). §5.4: A1-A3, A9, A12 rewritten; A13 added.
  §5.5: the cost cap, per encoding, and the UTF correction. §5.6: attributions corrected and
  the re-spelled rows added. §5.7: the witness table rebuilt with measured scan and k-set
  columns. §5.8: points at the table.
- §6: T1/T3/T4 updated; T7 (walk parameters) added. §8: the staging table (S4, S7, S11, S13, S14,
  S16). §9: the ledger (eight new rows). §10: U-dead scope, U-exactwidth. §11: the controls. §12:
  D-next plus the D168 addendum text. §13: Q3-Q5 updated, none dropped (Q1-Q6 are all still
  Frank's).
- `docs/design/CLAUDE.md`: the span_arms line says rev 2. Index lines: the lanes history and the
  reviews history (r2).

## STATE AT HANDOFF

- STATE: delivered. Branch `lane/spanarms3`, committed. Rulings file
  `docs/dev/lanes/spanarms3_rulings.md` was empty at every re-read (no entry applied).
- Validation: design lane, no suites owed. Measured on the lane's build of `c054e38e7`: about 60
  `--emit-facts` listings and 30 libpcre2 oracle patterns (about 70 cells).
- Open for the manager:
  1. S8's coordinate reading (§5.3 "The coordinate").
  2. The next step as ruled: ONE readiness critic for L1 over §5.7's re-spelled witnesses, and one
     each for L2 and L3 before any go.
  3. The utf8 nested-lookbehind compatibility probe (Summary, observation).
- Not done, by brief: no edits to ctx_span.md (its look-fixed row now reads the item, which is a
  DOC finding for its next revision) or to decisions.md (L1 files the D168 addendum with its build).
