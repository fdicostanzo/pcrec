# s2rev12 — span_cards.md revision 1.2 (lane report)

Lane s2rev12, branch `lane/memfn-s2rev12` (base 5e8cec75d: rev 1.1 + the kit branch, reviews r4-r6 present).
Design only: no C, no make, no timing, no box job. Drills run with `python3 -I` in the lane scratch dir.

## Summary

`docs/design/memfn/span_cards.md` is now rev 1.2. It applies review
`docs/dev/reviews/2026-11-06-r6-memfn-span-cards-recheck2.md`: every finding in its table and every bullet of
its "## Rulings". Every changed passage is marked `[rev1.2 <id>]`. The new §R1.2 table maps each r6 id to the
section that answers it. **Rev 1.2 changes nothing S2a builds.** The format-2 grammar, the digest, the seam
fields and the loader refusals all stay as rev 1.1 wrote them.

The decisions, as ruled:
- **READY-1.** A delta row's base arm leaves `inputs`. It is named on the row's CELLS: the cell id is
  `<group>/<arm>/<length>/<launch>`, and a delta arm's cells (its twin's too) add a fifth field, the base arm.
  The format already leaves the cell id's content to the producer (§2.2¶4 says only that each id is unique).
  The new section 3.4 says "a measured row's derivation lives in its cells". Rows keep `inputs` `-`, which
  today's loader accepts. Rev 1.1's S2c hunk for §2.2¶3 is withdrawn.
- **READY-6 + MEAS-7.** A kit-side run record, `span_cards/slot/run_record.tsv`, written at the end of the
  window and committed by S2d. Its sections: `run` (run id, J1's verdict and widths, the transcript's sha),
  `jobs`, `plan`, `floor` (the clauses) and `j1_cells`. Its sha-256 is cited in PROVENANCE.md and in the set
  header's `run` provenance key. The recompute reads set.tsv plus the record and re-derives J1's verdict from
  the record's `j1_cells`. The floor's key list belongs to the kit. `measures.md`'s new section 3.5 states only
  the generic rule.
- **READY-8.** Rows record `kit:form.<id>=<hash>`. Check C's measure_store pass reads the recorded hash. A hash
  that differs from today's is counted as STALE, not red. grid1's `-` is NOTED and not copied.
- **MEAS-4.** The drift threshold is now max(G/2, 3 s.e. of the statistic). `K_MED_E6 = 210300` is derived by
  `place_drill.py` B (0.2103). The s.e. term alone falsely refuses 1.1-1.2 % of no-drift jobs. A 3 % drift at
  s_L 1 % is now refused 92 % of the time (rev 1.1: 17 %).
- **MEAS-6.** J1's margin and cell count were re-chosen by a rule stated in `j1_drill.py` Part 2 before it
  ran: m 0.5, k 5. False (b) is 0.00-0.01 % over τ 0-4. Power at effect 4, τ 1 is 95.1 % (rev 1.1: 9.9 %; the
  critic's m 1 / k 5: 90.5 %). The 0.1 % false tolerance is the only chosen constant, labelled D149.
- **MEAS-1.** The placement seed is (run id, job, l, arm). The run id is the window's, recorded in the run
  record, PROVENANCE.md and the header. `place_drill.py` A2 (s 0.5 %, τ 0.5 %): given a refusal, a re-run
  refuses again 6.8 % of the time with fresh placements and 10.8 % with the same layout.
- **MEAS-2 / MEAS-3.** One first-match outcome table, checked by `outcome_drill.py` on 14 constructed runs:
  UNIT, then FLOOR over every active clause, then PARTIAL, then FULL. HELD requires a shared text-class
  cause; drift and never-ran causes are never HELD. Cost rows now pass or fail one by one.
- **movers.py.** PLAN. §5 and §10 item 12 ask main to file the row.

Drills: one new (`outcome_drill.py`), six revised. All seven were re-run, and every figure quoted in rev 1.2
comes from their output. `docs/design/memfn/CLAUDE.md` and `span_cards/CLAUDE.md` are updated.

Two items for the manager:
- **The deliver file arrived late.** `docs/dev/lanes/s2rev12_deliver.txt` was missing when I started. It
  appeared in the worktree (untracked) during the lane, and I used it as written.
- **"index notes" was read as the header's `run` key.** The ruling says the record's sha goes in
  "PROVENANCE.md and index notes", but `measure_store/index.tsv` has no notes column. I cited the sha in the
  set header's `run` provenance key instead and flagged it to main as §10 item 13.

## Charter-vs-committed checklist

Commits: 388e59d60 (drills), 973a40a25 and 5f92cd0b3 (WIP doc), 582c610ae (rev 1.2 + CLAUDE.md files), and
the report commit.

| item | committed where | done |
|---|---|---|
| READY-1 (FIX-NOW; ruling: base leaves `inputs`, named on cells) | §3.4 steps 1-2, §2.4, §3.8 step 1, §4.4 (§2.2¶3 hunk withdrawn), §8.2; `drill.py` (2) reads the base from cell ids | yes |
| READY-2 (17, every card table) | §2.4, §8.2, §9 S2c; `tree_drill.py` C (14 at the tree, 17 after) | yes |
| READY-3 (STORE compares, S1241/S1232, wording) | §3.8 "The embed", §4.4 S2e, §8.2, §9 S2e, §10.2 (measure_sets §8.3, tests/knowledge/CLAUDE.md) | yes |
| READY-4 (embed_text.sh, strip step, (v) split, file_cells source) | §3.8, §8.2, §9 S2e (v1)/(v2) | yes |
| READY-5 (slot sabotage runner, bounded re-draw, (l) positions, `=` spelling, (o) noted) | §3.1, §3.2, §3.8 step 2, §9 S2c | yes |
| READY-6 (FIX-NOW; ruling: kit-side run record) | §3.5 "The run record", §3.4 preamble, §1 Goals 2-3, §3.8 steps 1/3/4, §8.2, §12 row 7 (the in-set form as an unlock) | yes |
| READY-7 (S2d's commit) | §9 S2d, §8.2 | yes |
| READY-8 (FIX-NOW; ruling: record the deps) | §2.4, §3.8 step 1, §9 S2e (u2), §11 Q3 | yes |
| READY-9 (separability) | §9 Separability | yes |
| READY-10 (libpcrec size figure) | §9 S2e | yes |
| MEAS-1 (ruling: run id in the seed, in PROVENANCE) | §3.2, §3.5 HELD, §3.8 step 3; `place_drill.py` A2 | yes |
| MEAS-2 (one first-match table + its drill) | §3.5 Outcomes, §1 Goal 2; `outcome_drill.py` | yes |
| MEAS-3 (cost rows per row) | §3.5 | yes |
| MEAS-4 (ruling: s.e. in the threshold) | §3.5 Drift; `place_drill.py` B, `drill.py` | yes |
| MEAS-5 (sign rule over the trimmed six) | §3.5, §2.3; `floor_drill.py` | yes |
| MEAS-6 (ruling: re-choose the margin from the drill) | §3.6; `j1_drill.py` Part 2 | yes |
| MEAS-7 (with READY-6) | §3.5 "What the recompute covers", §3.6, §9 S2e (x) | yes |
| MEAS-8 (DOC) | §2.3 | yes |
| MEAS-9 (DOC) | §3.5 bimodal test; `place_drill.py` A breakdown | yes |
| MEAS-10 (DOC) | §3.4 step 7, §6 | yes |
| MEAS-11 (DOC) | §6; `coverage_drill.py` (3) | yes |
| MEAS-12 (DOC) | §3.2; `place_drill.py` A finer row | yes |
| MEAS-13 (DOC) | §3.3 | yes |
| Ruling: verdict NOT READY; rev 1.2, then diff-check + one readiness critic | STATE AT HANDOFF names the next step | yes (the next step is the manager's) |
| Ruling: every PROPOSED FIX-NOW and DOC accepted | the rows above | yes |
| Ruling: standing question movers.py, PLAN; main files the row | §5, §10 item 12 | yes (filing is main's) |
| Ruling: process change (readiness lens) | not this note's; recorded in §R1.2 as the launcher's | n/a |
| Standing question: FAM-B trigger widened (PLAN) | §12 row 5 | yes |
| Standing question: the recompute imports ks_ref.py's parser (FIX-NOW text) | §3.8 step 4, §11 Q2 | yes |
| General form 5: §12.1's trigger | §12 row 1 | yes |
| r6 meas.md text-vs-script gaps 2-4 | §3.4 steps 2-3, §3.5 Drift; `drill.py` | yes |
| §R1.2 table mapping every r6 id | span_cards.md §R1.2 | yes |
| Every quoted figure from a committed drill with named inputs; constants labelled per D149 | `span_cards/*.py`; D149 labels on the re-draw bound 64, the wait bound 5 min and J1's 0.1 % tolerance; K_MED derived | yes |
| CLAUDE.md lines | `docs/design/memfn/CLAUDE.md`, `docs/design/memfn/span_cards/CLAUDE.md` | yes |

## Needs S2a

None. Each decision is placed where S2a's work does not reach:
- READY-1 uses the cell id, which the format leaves to the producer, and keeps `inputs` `-`.
- READY-6 is a kit file plus an existing provenance header key.
- READY-8 uses a row's `deps`, which is provenance text the loader never parses.
- The MEAS fixes change the estimator and slot rules: spec text that lands at S2c, plus the slot harness.

I checked these against the build tree. `ks_measures.c` checks cell ids for uniqueness only (:495-499),
refuses inputs on measured rows (:466-481, which no longer applies because rows keep `-`), and never parses
`deps`.

## STATE AT HANDOFF

Rev 1.2 is complete and committed on `lane/memfn-s2rev12`. OWED: none. There is no validation run; this is a
design lane. Next is the manager's: a diff-check of every r6 id against §R1.2, then one readiness critic on
the rev 1.2 diff.
