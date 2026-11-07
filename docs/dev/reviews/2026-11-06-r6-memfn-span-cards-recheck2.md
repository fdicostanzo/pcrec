# Review 2026-11-06 r6? — memfn-span-cards-r11 (design RE-CHECK of span_cards.md rev 1.1, units S2c-S2e)

- **Subject:** `docs/design/memfn/span_cards.md` rev 1.1 at ef2f130fc (branch lane/memfn-s2rev11, head
  e52cd716a = ef2f130fc + the lane report and a history index line). Scope: S2c, S2d, S2e and §2, §3, §6,
  §8.3, §9's S2c-S2e rows. S2a/S2b out of scope except where read.
- **Build tree:** main 6f1b40f75 (kit branch lane/memfn-k1102 = main + journal commits). No binary built.
- **Rulings frozen** at main 6f1b40f75 (D188 + add. 1; R-35 (a)-(e)).
- **FREEZE DRIFT:** main moved to adb2d44b7 during the round: plan.md only. a601992cc edits
  [KIT-POLICY-TABLE]'s status (drops the nonexistent `COVER_Z_E3` cite), which is the amendment the design
  itself asks for (§10, line ~1264) — consistent, no finding moves. adb2d44b7 files [ANCH-AT] — unrelated.
  decisions.md and requests.md unchanged.

## Lenses as run

| lens | model | question | why chosen |
|---|---|---|---|
| readiness (+ standing questions: sibling of a family, general form + unlocks) | opus | per unit S2c/S2d/S2e: cites hold at the build tree, witness can fail, separable, complete; per-unit + round verdict | the launcher's ruled lens for the last re-check before the build go |
| measurement (+ simulate drills) | opus | regime / independent control / what moves on regeneration; text-first estimator re-implementation diffed against drill.py; first-match outcome drills; every quoted figure recomputed; never-picked candidate; finer re-sweeps | the launcher's ruled lens; the subject is an estimator with drills |
| verifier | sonnet | re-derive every CONFIRMED finding that would change the design | skill §6 |

## Round verdict (proposed): NOT READY — S2e not ready; S2c and S2d ready with listed text fixes, but READY-1 is a format decision that also reaches S2a (being built NOW)

READY-1 is the gating item: §2.4/§3.4/§3.8 put a delta row's base ARM name in a MEASURED row's `inputs`; the
loader at the build tree refuses any input on a measured row and accepts only row keys or cell ids on a
computed one (`src/core/ks_measures.c:396-415, :466-481`), and no unit (S2a's code list, S2c's spec-only
§2.2¶3 hunk, S2e) carries the loader / ks_ref.py / mfixtures / measures.md §7 change. S2e cannot load its own
set. The natural home is S2a's format-2 parse — which is in flight — so the launcher may want to rule the
shape before S2a lands. Two S2e blockers (READY-1 via CELLS-3, READY-3 via EMBED) and READY-8 (via CHECKC)
are FIX-INDUCED by rev 1.1's own fixes.

| unit | proposed verdict | blocking items |
|---|---|---|
| S2c | ready with listed text fixes (after READY-1's decision) | READY-1 (where its §2.2¶3 hunk lands), READY-2, READY-5, READY-9 |
| S2d | ready with listed text fixes | READY-7; MEAS-1 (seed), MEAS-2/3/5 (outcome rules it is judged by) |
| S2e | NOT READY | READY-1, READY-3, READY-4, READY-6 (+MEAS-7), READY-8, READY-10; MEAS-2 (the recompute must re-derive `partial` exactly) |

## Which lens caught what

- readiness: READY-1..10 (cites, witnesses, completeness, separability), three of them fix-induced.
- measurement: MEAS-1..13 (re-run statistics, outcome table, drift scale, NULL fragility, J1 constants).
- Overlap: READY-6 and MEAS-7 (the recompute's inputs outside the set; J1's verdict uncontrolled);
  READY-6 and MEAS-2 (Goal 2's floor is neither exactly stated nor recomputable from the set).
- No answer-level findings (nothing emitted moves, §8.1 held). No speed-level findings (all measurement
  statistics; nearest is MEAS-1/3/5: priced rows lost or run held, i.e. wins forgone, safe side).

## Findings with PROPOSED dispositions (verifier verdict in brackets)

| id | lens(es) | severity | proposed | one-line reason |
|---|---|---|---|---|
| READY-1 | readiness | design (blocker S2e) | **FIX-NOW** (rev 1.2 decision; rule before S2a lands) | measured delta rows name an arm in `inputs`; the loader refuses both; no unit owns the change. Options: S2a's loader admits "one arm of this set's cells on a format-2 delta row" (+ks_ref.py, §7 row, mfixtures, S-row), or the base moves out of `inputs` (a cells-side reference, readiness unlock 1). Must also stay parseable under the cell-less embed (READY-3) [HOLDS] |
| READY-3 | readiness | design (blocker S2e `make test`) | **FIX-NOW** (text) | cell-less embed makes run_measures_tests.sh STORE R4, R5 and the embedded-text compare red in the correct build; S1241/S1232 detectors move; measures.md §6¶2 and measure_sets §8.3 "Embedded = committed" need amending [HOLDS; S-row detectors not separately re-run] |
| READY-4 | readiness | completeness / witness | **FIX-NOW** (text) | the embedded TEXT is `scripts/embed_text.sh` ("unmodified"), not ksgen; sabotage (v) names no check and must split text/pre-parse; state where `file_cells` comes from [HOLDS] |
| READY-6 | readiness (+MEAS-7, MEAS-2) | design (Goal 3) | **FIX-NOW** (rev 1.2 decision) | "the recompute reads ONLY the set file" is false: never-ran groups (prose in PROVENANCE), J1's verdict and the census key list are outside it; give each a machine-readable home (readiness unlock 2: a `run` section), and home the floor's key list with the kit, not measures.md [HOLDS] |
| READY-8 | readiness | maintenance (permanent for zen4-grid3@1) | **FIX-NOW** (decision at S2e at the latest) | rows' deps `-` contradicts measure_sets §2.4/§7.2 and the design's own staleness-through-form-hash claims (§3.6, §11); record `kit:form.<id>=<hash>` or amend measure_sets and withdraw the claims. Verifier: grid1 already carries `-` (precedent that already contradicts the text) [HOLDS] |
| READY-2 | readiness | doc / check floor | **FIX-NOW** (text) | check C's guard walks every card table: 14 at the tree, 17 after kit-grid@3, not 12; tree_drill C reads kit-grid only [HOLDS] |
| READY-5 | readiness | witness | **FIX-NOW** (text) | slot sabotages (j)(j2)(k)(l) have no runner (SAB_SUITES closed; name a slot-local runner or say they are not S-rows); bound the re-draw loop; (l) gate on positions not count; spell `--list-measurements=FILE`. (o) is red by a ValueError, not the stated reason: NOTED [PARTLY: (l)'s text is ambiguous count vs positions; the (o) crash not re-run] |
| READY-7 | readiness | separability | **FIX-NOW** (text) | S2d's committed outputs (j1 verdict + cells, ofsskip.c comment flip, transcript sha, (b) plan filing) have no owning unit [not sent to verifier: text-only] |
| READY-9 | readiness | doc | **FIX-NOW** (text) | S2a is not independent until S2e: S2c's spec hunks describe format 2 and plant (o) needs a format-2 file; LOCK becomes S2a -> S2c(spec), S2b -> S2c -> S2d -> S2e [not sent: text] |
| READY-10 | readiness | doc | **FIX-NOW** (text) | artifact_size_log.tsv is a per-pattern log, holds no libpcrec figure; report `size` base vs head instead [coordinator checked the file's header on main: per-pattern columns] |
| MEAS-1 | measurement | design (HELD statistics) | **FIX-NOW** (one word + re-quote) | placement seeded from (job, l, arm) only: a re-run re-links the same layouts, so HELD's "two independent runs, 0.3 %" overstates; add a run id to the seed (recorded in PROVENANCE) or re-derive HELD for a same-layout re-run [HOLDS mechanism; magnitude 1.3-1.8x at 20,000 trials vs the critic's ~2.7x at 4,000] |
| MEAS-2 | measurement (+READY-6) | design (Goal 2/3) | **FIX-NOW** | the outcome table has two floor readings: (A) PARTIAL-by-refusal is dead text, (B) r5 GOAL2's own scenario is ACCEPTED as PARTIAL with 3 priced keys; no precedence when PARTIAL and REFUSED both match; HELD's "same cause" undefined for drift and two-cause refusals. One first-match table + a drill of it [HOLDS] |
| MEAS-3 | measurement | design | **FIX-NOW** (small) | "a group passes iff every cost row passes": a walk-set row over its gate removes find_byte.libc (J2's byte group); pass/fail cost rows per ROW, keep group verdicts for the unit and drift [HOLDS] |
| MEAS-5 | measurement | design (floor fragility) | **FIX-NOW** (small) | NULL rule "every D_l > 0" has no outlier tolerance while the spread trims one launch; one base-cell spike nulls every row that base serves (J3 base.walk: four); apply the sign rule over the trimmed six or say why not [HOLDS; spike model illustrative] |
| MEAS-6 | measurement | design/doc | **FIX-NOW** (text or re-chosen margin with its drill) | J1's margin 2 / 5 of 8 cannot have been chosen by (b)'s false rate (0 % over the whole re-swept grid); power 9.7 % at an effect 2.8x placement s.d.; m 1 / k 5 gives ~90 % at the same 0 % false [HOLDS] |
| MEAS-7 | measurement (+READY-6) | design (low) | **FIX-NOW** (with READY-6) | J1's verdict sets the set's PARTIAL but is re-derived only by the slot harness; the recompute (or a pcrec test from §3.6) re-derives it from j1_cells.tsv, or PROVENANCE cites its sha [HOLDS] |
| MEAS-4 | measurement | doc/design | **DOC** (+ launcher's option: put the s.e. in the threshold) | drift threshold is ~6.4 s.e. of the statistic; "smaller drifts are unresolvable" is false (3 % at s_L 1 %: 18 % vs 90 % at 3 s.e.); factor 3 is D149-labelled, so the trade is the launcher's [HOLDS] |
| MEAS-8 | measurement | doc | DOC | walk-set's floor quoted as walk's (16.0/31.75 vs 15.75/31.25), below the drill's MC resolution |
| MEAS-9 | measurement | doc | DOC | the bimodal test's own catch is ~3 % beyond the half gate (67 % is mostly the gate's) |
| MEAS-10 | measurement | doc | DOC | delta rows' noise is estimator error (shared base, shared W/ctl), not §6's independent per-card launch distribution; errs wide |
| MEAS-11 | measurement | doc | DOC | z 3.0's 2.25 % holds for normal launches; t5 tails 3.07 % |
| MEAS-12 | measurement | doc | DOC | "from tau ~1 % ... every time": drill prints 52 %/42 %; every time from ~1.5-2 % |
| MEAS-13 | measurement | doc (SUSPECTED) | DOC | "every group boundary re-checks load" undefined under interleaved rounds; its cost is not in §3.7's 35 min |

## Standing questions (readiness lens)

- **Sibling of a family:** `span_cards/slot/movers.py` is the THIRD mover census (m0build census.py,
  `emit_sweep.py --data`); measure_sets §9.3/§8.4 homes the DEFAULTS transition census as emit_sweep's
  `measures` data kind, and S2e IS a DEFAULTS transition. Proposed: **PLAN or build at S2e** (launcher's
  call; r5 CENSUS accepted either; the general-mechanism rule favours building `--data measures` now).
  The slot harness is the 4th-5th hand-built harness: widen FAM-B's trigger to "the next slot harness
  written" (**PLAN**). The recompute is a 4th python set reader: import ks_ref.py's parser (independence is
  owed to the slot harness, not to ks_ref.py) (**FIX-NOW text**, rev 1.2).
- **General form + unlocks:** (1) the base as a cells-side reference, not a row input (absorbs READY-1;
  trigger rev 1.2); (2) a machine-readable `run` section in the set (absorbs READY-6/MEAS-7; M3 writes the
  same; trigger rev 1.2); (3) recorded form hashes in row deps (READY-8; trigger: decide at S2e, permanent);
  (4) `emit_sweep --data measures` (trigger S2e or row 1's flip); (5) §12.1's registry-derivation trigger
  should add "a measured row whose value is a derivation over cells needing its own noise".

## PROBED-AND-HELD (summary; full lists in review/ready.md and review/meas.md)

- Every code/data cite of S2c-S2e is identical between ef2f130fc and 6f1b40f75 (empty diff over the cited
  files); ~40 file:line cites quoted and held.
- Text-first re-implementation of §3.4-§3.5 vs drill.py: 6 functions x 200,000 fuzz cases, 0 divergences;
  six text/script gaps listed (meas.md "Text vs script diff"; gap 1 = MEAS-2, gaps 2-6 doc).
- 40+ quoted figures recomputed from all six drills: all reproduce except MEAS-8's attribution.
- K_TRIM 1.7238 at 10^6 draws (derived as stated); z 3.0 crossing at ~2.98; the never-picked-candidate
  drill moves no normaliser (only the group verdict, MEAS-3); gate edges inclusive/strict as written.
- Sabotage rows that can fail as written: (m), (n), (p), (u) (with arm_fixtures `ids[]` named), (q) partly.
- r5 fixes present in text for S2c-S2e: CELLS-1..3, CHECKC, HASH, TWIN, PLACE (within a run), DRIFT, Z,
  FLOOR, CENSUS, EMBED, GOAL2 (NULL half), J1-WIN, LOCK, J3, INDEX — with the fix-induced gaps above.

## By-id completeness

READY-1..10, MEAS-1..13: every id has a proposed disposition. Verified by the verifier: READY-1,2,3,4,5,6,8;
MEAS-1..7 (13 HOLDS, 1 PARTLY, 0 REFUTED). Not sent (text-only/doc): READY-7, 9, 10; MEAS-8..13.

## D27 recommendation

Not recommended for this round: S2c-S2e change no caller contract beyond measures.md's new spec sections,
whose independent reader IS the recompute (Goal 3). Revisit if READY-6's `run` section becomes a format.

## Lessons for the guide (proposed)

See .coord/process.md "Proposed changes".

## Rulings (kit manager, 2026-11-06)

**Verdict: NOT READY.** Rev 1.2, a text revision with the decisions below, then a manager diff-check of every r6 id plus ONE readiness critic on the rev 1.2 diff only (fix-induced focus); no full round. S2c/S2d READY with rev 1.2's text; S2e READY once rev 1.2 lands and the diff-check passes.

Every PROPOSED FIX-NOW and DOC disposition is ACCEPTED, with these decisions:
- **READY-1: the base leaves `inputs`.** A measured delta row carries `inputs` `-`. Its base arm is named on the row's CELLS (the cell rows already carry the group `J<j>.base`), and the recompute reads the relation from set.tsv's `cells`. WHY: no loader, ks_ref.py or §7 change, so S2a (being built) is untouched. Embed readers read value and noise only, never the base, which keeps the cell-less embed (READY-3) sound. The spec text says a measured row's derivation lives in its cells (measures.md new §3.4).
- **READY-6 + MEAS-7: a kit-side RUN RECORD, not a new set section.** Never-ran groups, J1's verdict and inputs, and the census key list the floor reads go into one committed machine-readable file beside the slot harness (`span_cards/slot/run_record.tsv`). Its sha is cited in PROVENANCE.md and index notes. The recompute reads set.tsv plus that file and re-derives J1's verdict from it. No format-2 change, so S2a is untouched. The floor's key list is the kit's, not measures.md's.
- **READY-8: record the deps.** Rows carry `kit:form.<id>=<hash>` as measure_sets §2.4/§7.2 require. grid1's `-` is a precedent the spec never sanctioned; it is NOTED, not copied.
- **MEAS-4: put the s.e. in the drift threshold** (3 s.e. of the statistic). The factor 3 was an UNMEASURED DEFAULT; the measured basis replaces it.
- **MEAS-6: re-choose J1's margin from its drill** (the critic's m 1 / k 5 at about 90 % power and 0 % false is the starting point). Rev 1.2 quotes the drill.
- **MEAS-1: a run id in the placement seed**, recorded in PROVENANCE.
- **Standing question (movers.py is the 3rd mover census): PLAN.** emit_sweep `--data measures` replaces movers.py when the next data-mover census is needed (M1's first set). Main files the row.

**Process change ACCEPTED:** the readiness lens runs the build tree's LOADER refusal paths over every new data-row shape the design writes, and lists every check that compares an embed or copy with its source.
