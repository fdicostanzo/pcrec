# 2026-10-14 r1 — D6 panel on docs/design/memfn/regime_eval.md rev 1 ([REGIME-EVAL])

Subject: lane/memfn-r17 @ 08dad8eec, regime_eval.md rev 1 (main's review applied).
Panel: three read-only sonnet critics, each with its own lens plus one "unlock"
item: crit-meas (measurement validity and pre-registration), crit-indep (check
design and independence; learnings §3, pcrec-check-design-lessons), and
crit-contract (contract, ownership boundary, staleness). The consolidated
disposition is in §D.

## A. crit-meas — ACCEPT-WITH-FIXES (no BLOCKER; M-1..M-8 fixed or ruled before E5)

- **M-1 MAJOR. The G2 caps come from repeated-buffer replays (§8, `fit-repeated`) but gate streamed cells.**
  - A streamed walk is slower, so every "% of walk" shrinks and the caps pass by construction. F-4's SIMD-on DINGHY loss of 11-14% already sits inside the 15% cap.
  - Fix: express the caps in ns/B or ns/call from the set, or re-derive them from a streamed in-sample run before E5. Print a rep64k cap check as well.
- **M-2 MAJOR. The G3 per-call floor loosens with match density.**
  - Example: a 1 MiB pass making 10k calls can be +400 µs (+150%) at 40 ns/call.
  - Fix: test per PASS (excess > max(50 ns, 25% of walk)), and per call only for `first`/`lines`. Define the second clause for Σ(walk − pick) ≤ 0.
- **M-3 MAJOR. G1's tolerance Σ NULL is linear, while noise adds in quadrature.**
  - The allowance is 2-3x the measured aggregate A/A (1.25%), so G1 is vacuous when P-MOVE is small.
  - Fix: sqrt(Σ NULL²) or a cell bootstrap. Add a power floor so a thin bar reads UNDERPOWERED.
- **M-4 MAJOR. CB condition 3 tests best vs walk, not pick vs walk.**
  - F2: bounded prose1m V1 runs +16% cycles with equal misses, yet the cell is CB, leaves G2/G3, and the loss vanishes.
  - The arm spread grows with the number of arms (2 off, up to 7 on).
  - The streamed subject S was never perf-measured.
  - Fix: CB leaves the DENOMINATOR only, and its regret stays in the numerator. Run the F2 pass on one S subject before E5. Compute the spread over the walk plus the common arms.
- **M-5 MAJOR. Winner's curse.**
  - A 7-arm minimum is biased more than the 2-arm A/A.
  - C7 and NULL_cell share the walk/walk#b launches.
  - Fix: cross-fit (pick the best on launches 1-2, score it on launch 3). Add walk#c, or a per-slot anchor re-timing, as an independent A/A plus a drift check.
- **M-6 MAJOR. Held-out contamination.**
  - J2a's bench patterns overlap ALPHA/spike, which costmodel read.
  - FIT's prose1m/docs1m/code1m may share bytes with J1.
  - Re-registering against the same J1 after a FAIL tunes on the judge.
  - Fix: a sha256 disjointness proof of judge buffers against every FIT buffer and the shipped findings corpora; J2a ∩ ALPHA/spike marked contaminated and non-gating; seal ~30% of J1 as a final-only holdout; list every prereg version.
- **M-7 MAJOR. The wall estimates undercount.**
  - Length buckets add ~140 groups (~+46 min).
  - J-b is ≥ 79 min before gates, perf and WITNESS cells.
  - Fix: recompute and re-split the slots. Add a load1-breach abort rule and M-9's adaptive launches.
- **M-8 MAJOR. A wrong-box set is blamed on the table.**
  - Fix: refuse when set.box ≠ the run box unless the run is declared C6. Each judge slot first replays the set's FIT anchor subset on that box (~10 min). An anchor fail reads SET-MISMATCH; otherwise a judge failure goes to the table.
- **M-9 MINOR. LAUNCHES=3 with a bimodal walk;** the sign test passes by chance 25% of the time. Fix: +2 launches for any group whose A/A disagrees by more than NULL (pre-registered).
- **M-10 MINOR. Inherited CB labels in J4 are not conservative.** Report only; never gate on them.
- **M-11 MINOR. The prereg does not pin the evaluator; committer dates are forgeable; a PROVISIONAL PASS authorizes routing.**
  - Fix: blob shas of regime_eval.py, regime_pick and the CB classifier go into prereg.tsv. Main's journal hash is the timestamp authority. Add a rollback trigger tied to [REGIME-TWIN].
- **Also:**
  - print each population, class and pattern-median separately, not only ns-pooled;
  - also report regret against walk minus the EXT consumer ns;
  - state that neither streamed condition is DRAM-bound.
- **Unlock:** a table-agnostic replay harness (table, set, knowledge records, timed arms, then pick/regret/controls/prereg). Trigger: a second table with timed arms up for a ruling (cand_rows[] reseed/handoff, [PRIOR-COST-UNIFY]). Do not generalize earlier.

## B. crit-indep — ACCEPT-WITH-FIXES (I-1, I-2 BLOCKERS before E5)

- **I-1 BLOCKER. The agreement and plant checks compare the kit's one selection function with itself.**
  - A wrong condition (`<` vs `<=`) or a wrong row order agrees with itself, and the plant moves both sides.
  - Fix: an independent oracle. A blinded author, from the prose rows only, writes ~60 (knowledge → expected row) cases covering every row and boundary, plus a second small evaluator of the prose rows. The harness must match all of them, and the plant must make it fail them.
- **I-2 BLOCKER. G4 is unsatisfiable, and C3 passes vacuously.**
  - C2 is already NOT-WORSE in sample (per-step rows, per-pass H).
  - Deleting a rare row can never move 1 point of a regime sum.
  - Fix: declare the UNSCORABLE rows and controls (R3a, R3b, R4, every H-keyed row, C2) as handed to the twin and excluded from G4, never counted as passed. C3 becomes per-moved-cell (> 2×ΣNULL over the moved cells, with a minimum moved count), reported per moved cell.
- **I-3 MAJOR. CB hides pick losses** (the same issue as M-4).
  - Fix: add condition 3b, ns(pick) − ns(best) ≤ NULL. CB-with-pick-loss cells stay in G3. Print the with-class gates too.
- **I-4 MAJOR. C7 A/A is a tautology** (its floor is walk vs walk#b).
  - Fix: a split-half C7 (odd vs even rounds: pick/verdict disagreement and the regret difference). A null-mutation control (deny an alias row: NOT-WORSE, zero moved). Per-arm A/A where it exists.
- **I-5 MAJOR. Uncounted populations (K35):**
  - (a) a GATE-EXCLUDED sixth class with a per-arm count; any exclusion of a pickable arm is a hard FAIL;
  - (b) "partial" cells are counted, capped, and kept out of the G2/G3 numerators;
  - (c) G0: a floor on RT cells per layer × regime × filter, below which the gate reads UNREACHED, not PASS;
  - (d) RT is classified per timed group (counter leg U), with the completeness sum over groups;
  - (e) the RT share becomes a floor on the gate's weight.
- **I-6 MAJOR. Contamination and iteration:**
  - J2a ∩ ALPHA/spike/costmodel inputs is dropped from gating (the same as M-6);
  - the blinded lane writes J1b now and commits its hash unopened, for after a FAIL;
  - (W) subjects are checked for no byte-range overlap with the exemplar;
  - main passes the prereg sha in the slot request (the ordering authority).
- **I-7 MAJOR. A planted evaluator bug would not be caught** (a wrong pick→ns join, E read from the timed slice, the wrong cell's ADV/A).
  - Fix:
    - a second independent parser re-reads 30 random cells from the raw logs;
    - an oracle-policy control (pick = best must give regret 0, an inverted policy the maximum);
    - a planted E-leak control.
- **I-8 MINOR. The `lines` bucket edges come from the table's own constants.** Derive them from the set under test, and check that no edge falls inside a bucket.
- **I-9 MINOR. Label the G2 caps (in-sample plus headroom) and G3's constants as not independent.** Report held-out minus in-sample as the headline figure.
- **Unlock:** a decision-table evaluator for pcrec's first-match tables (cand_rows[], fit_rungs[], reseed rows, req_admits[]; [SEL-COST], [DEC-FALLBACK], D166's second consumer). Trigger: a second table needing a measured-regret verdict. Until then, keep the input side pluggable.

## C. crit-contract — ACCEPT-WITH-FIXES (no BLOCKER; B-1 before anyone runs J2a)

- **B-1 MAJOR. J2a's "streamed set from the bench's published generator at distinct seeds" would write into pcrec-bench.** `gen_throughput_subjects.py` hard-codes `OUT` and its seeds, which is a mandate breach.
  - Fix: import only the bench's text libraries (`boundedtext.py`, `logtext.py`) read-only (`python3 -I -B`), with kit seeds and a kit scratch out-dir. Otherwise use only the bench's existing ≥1 MiB subjects (condition W) and relay the seed question to the bench dev via main.
  - The prereg hashes the bench commit read.
- **B-2 MAJOR. The controls' "build knobs" are unbuilt.**
  - Set files need `--measures` ([MEASURE-SET], not started), so C1/C5/C6 go through `regime_pick` until then.
  - The `--memfn=no-<row>` denies do not exist yet. E3 creates them, so E3 owes the D80 spec hunk plus the registry floor pin (r15b precedent).
  - [MEASURE-SET]'s trigger fires at E3; main should schedule it then.
- **B-3 MAJOR. The agreement check cannot run before routing.** E3 is unrouted, so MF_TRACE records nothing.
  - Fix: E3 includes a trace-only SHADOW call (r4ccore I1's implement-then-replace pattern, zero emitted bytes).
  - The witness rule fails closed on R4 and H rows and on the unnumbered pending row. Exempt H rows (the twin witnesses them) and give the pending row an id.
- **B-4 MAJOR. §6.1 calls `--diff` D166's mover census; it is not.** D166's census is pcrec-owned and emit_sweep-shaped (artifact bytes over corpus + bench, including emitted N/M/H dispatch). `--diff` is an advisory PICK census over judge cells, and may optionally ingest an emit_sweep run.
- **B-5 MINOR. No ISA field.** D166 item 3 keeps ISA availability a separate fact, but regime_eval's A is only the set id, and nothing selects S1 vs A1. Main's regime_tables §2 still defines A as "ISA + tuning class" (pre-D166).
  - Fix: add an ISA field to the knowledge record and flag the regime_tables conflict to main.
  - D157 note: the range-term count is kit-derived from set[32] (no pcrec field); say so.
- **B-6 MINOR. Stale citations against regime_tables rev 0.3** (aad0199d9): R3a/R3b, a pending amended-D2 row, model-vs-declared relabel.
  - C3's "R0..R6", §8's header and §4.4 follow 0.2.
  - Main's pending row cites "replay F-1" for the 6.0% finding; it is F-2.
- **B-7 MINOR. §2.4's F2 quote overgeneralizes.**
  - The walk on repeated 64k reads 0.44-0.9 (dfa-hat), 22/150/4.7 (hex-run prose/docs/code) and 95-168 (bounded).
  - The streamed rationale holds for hex-run prose/code and dfa-hat; P-PRED should expect no change on bounded.
  - The §2.7 spread figures match f2_counts exactly.
- **B-8 MINOR. The interim set and interim E.**
  - The kit-private TSV is labelled as such, with a converter and zero movers through `--diff` when [MEASURE-SET] lands (its hash change forces a new prereg).
  - Ownership: pcrec owns the format, loader, store and stamp; the kit owns the values and the method.
  - E = exemplar-bigram is a surrogate producer. [REGIME-LANDINGS]'s arrival needs an agreement check between the two and a fresh S1/S3 prereg.
- **B-9 MINOR. Box-specific absolutes** (G3's 50 ns, the CB floor of 50/KiB, NULL 3.09%). J4 re-derives NULL from its own A/A; G3 goes into walk-cost units or is marked Zen 4 only.
- **B-10 MINOR. J2a ∩ ALPHA disjointness is unchecked (K35).** Count it and label overlaps contaminated.
- **Held, no finding:**
  - the ownership of rows, evaluator and twin; judge isolation (no ledgers; J2b via main);
  - the controls are set/deny changes, not a second table;
  - answer identity is the correctness gate;
  - Q-11's order (subject to B-3).

  Side note: memfn/CLAUDE.md's boundary table never mentions the regime table, the evaluator or measurement sets.
- **Unlock:** make the CONTRACT table-agnostic now, at the cost of an interface only. `picks.tsv` (cell, layer, filter, row id, form id) plus an arm-timing file are the interface, and `regime_pick` is one producer. pcrec could then judge cand_rows[], the reseed rows or req_admit through the same judge. Trigger for anything more: a second first-match table with a measured threshold needing a judge (forest-for-trees, about 3 members).

## D. Disposition (kit manager, 2026-10-14)

**Verdicts:** ACCEPT-WITH-FIXES ×3. **Blockers:** I-1, I-2. Every id below is ACCEPTED. Duplicates are merged explicitly. Rev 2 (lane regeval3) applies them before the E5 prereg commit.

| theme | ids | disposition |
|---|---|---|
| T1 an independent pick oracle | I-1 | ACCEPT. A D27-blinded author (cell), from regime_tables' PROSE rows only, writes ~60 (knowledge → expected row) cases covering every row and boundary, plus a second small prose-row evaluator. `regime_pick` must match all of them, and the threshold plant must fail them. |
| T2 unscorable rows, per-moved-cell controls | I-2, B-3 (witness part) | ACCEPT. Declare UNSCORABLE (twin-owned, excluded from G4, never counted as passed): R3a, R3b, R4, every H-keyed row, and C2. C3 becomes per-moved-cell (> 2·√ΣNULL² over the moved cells, with a minimum moved count) and is reported per moved cell. H rows are exempt from the witness rule. The pending amended-D2 row gets an id. |
| T3 shadow trace before routing | B-3 | ACCEPT. E3 carries a trace-only shadow call (zero bytes), so the agreement check runs at E4. |
| T4 caps in relative units, from streamed data | M-1, B-9, I-9 | ACCEPT. G2 caps are re-derived from a STREAMED in-sample replay (fit cells in zen4-grid2), expressed in walk-cost units, and labelled not-independent. G3 goes to walk units (or is marked Zen 4). J4 re-derives NULL. The headline figure is held-out minus in-sample. |
| T5 the outlier test per pass | M-2 | ACCEPT. Per pass: excess > max(50 ns, 25% of walk), in walk units per T4. Per call only for first/lines. The Σ ≤ 0 clause is defined. |
| T6 aggregate noise | M-3 | ACCEPT. √ΣNULL² or a cell bootstrap (choose one and pre-register it). A power floor gives UNDERPOWERED. |
| T7 the consumer-bound class | M-4, I-3, B-7 | ACCEPT. CB leaves the DENOMINATOR only, and its regret stays in the numerator. Add condition 3b, pick − best ≤ NULL; CB-with-pick-loss cells stay in G3. The spread is computed over the walk plus the common arms. An F2 perf pass on one streamed subject runs before E5 (in grid2). B-7's corrected F2 quote and the P-PRED expectation on bounded are applied. |
| T8 winner's curse and A/A | M-5, I-4 | ACCEPT. Cross-fit (pick the best on launches 1-2, score it on launch 3). C7 becomes a split-half test. Add a walk#c / per-slot anchor (also the drift check) and a null-mutation alias-row control. Per-arm A/A where it exists. |
| T9 contamination and sealing | M-6, I-6, B-10 | ACCEPT. A sha256 disjointness proof of judge buffers vs FIT buffers vs the exemplar vs the findings corpora, including (W) byte ranges. J2a ∩ ALPHA/spike/costmodel inputs is marked contaminated and non-gating, and counted. Seal ~30% of J1 as a final-only holdout. The blinded lane writes J1b now and commits its hash unopened. Every prereg version is listed. Main passes the prereg sha in the slot request (the ordering authority). |
| T10 populations counted | I-5 | ACCEPT. A sixth class, GATE-EXCLUDED, with a per-arm count (excluding a pickable arm is a hard FAIL). Partial cells are counted and capped. G0: an RT floor per layer × regime × filter, below which the gate reads UNREACHED. RT is classified per timed group with a completeness sum over groups. The RT share is a floor on gate weight. |
| T11 evaluator plants | I-7, M-11 | ACCEPT. A second independent parser over 30 random raw cells; an oracle-policy control (pick = best gives 0, inverted gives max); a planted E-leak control. prereg.tsv carries the blob shas of the evaluator, `regime_pick` and the CB classifier. Main's journal hash is the time authority. A PROVISIONAL PASS gets a rollback trigger tied to [REGIME-TWIN]. |
| T12 slots and launches | M-7, M-9 | ACCEPT. Recompute with the length buckets and WITNESS cells, re-split the slots, add a load1-breach abort rule, and +2 launches when a group's A/A disagrees beyond NULL. |
| T13 wrong-box set | M-8, B-5 | ACCEPT. Refuse when set.box ≠ the run box (except a declared C6). Each slot first replays the set's FIT anchor subset, reading SET-MISMATCH vs a table failure. Add an ISA-level field to the knowledge record. |
| T14 inherited CB on Zen 1 | M-10 | ACCEPT. Report only, never gate. |
| T15 bench boundary | B-1 | ACCEPT. The bench's text libraries are imported read-only with kit seeds and a kit out-dir. Otherwise only the bench's existing ≥ 1 MiB subjects are used. The prereg hashes the bench commit. Seed or out-dir questions go to the bench dev via main. |
| T16 controls through unbuilt knobs; spec | B-2 | ACCEPT. C1/C5/C6 run through `regime_pick` until [MEASURE-SET]. E3 owes the D80 hunk and the registry floor pin for each new deny. Tell main [MEASURE-SET]'s trigger is E3. |
| T17 census naming | B-4 | ACCEPT. `--diff` is an advisory pick census. D166's mover census is pcrec's (emit_sweep-shaped). |
| T18 interim set/E, ownership words | B-8 | ACCEPT. The kit-private TSV is labelled, with a converter and a zero-mover `--diff` at [MEASURE-SET]. Ownership: pcrec owns format/loader/store/stamp; the kit owns values/method. A surrogate-E agreement check and a fresh S1/S3 prereg follow when [REGIME-LANDINGS] lands. |
| T19 staleness | B-6, I-8 | ACCEPT. Re-cite regime_tables rev 0.3 (C3 list, §8 header, §4.4). Tell main F-1 → F-2 in its pending row. `lines` bucket edges come from the set under test, with the no-edge-in-bucket check. |
| T20 unlock (all three critics converged) | M-unlock, I-unlock, B-unlock | ACCEPT THE INTERFACE ONLY: `picks.tsv` + an arm-timing file; `regime_pick` is one producer; the input side is pluggable. No general judge is built (D77). Trigger: a second first-match table with a measured threshold needing a verdict (candidates: reseed rows, [PRIOR-COST-UNIFY], [SEL-COST]). Filed with main. |
| side | memfn/CLAUDE.md boundary table | ACCEPT. Add the regime table, the evaluator and measurement sets (owner split per T18). |

**Completeness by id:** M-1..M-11 (11), I-1..I-9 (9), B-1..B-10 (10), plus 3 unlocks: 33 ids, all dispositioned.

**To main:**
- regime_tables §2's A definition conflicts with D166 item 3 (B-5);
- the pending row's replay citation should read F-2 (B-6);
- [MEASURE-SET]'s trigger is E3 (B-2);
- a table-agnostic judge interface is filed (T20);
- zen4-grid2 will carry the streamed in-sample fit cells and the F2 streamed pass (T4/T7).
