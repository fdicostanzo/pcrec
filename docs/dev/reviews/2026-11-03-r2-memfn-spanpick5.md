# Review 2026-11-03 r2 — memfn-spanpick5 (design RE-CHECK of span_pick rev 5; last re-check before the stage-1 build go)

- **Subject:** docs/design/memfn/span_pick.md rev 5 at 9c9aadb60ba971b5d66a5fa5c04e400d5072b912
  (lane/memfn-spanpick5); rev 4 base 76a7f02e7. A build lands on main 7f55a62f9; the review tree was
  built there. memfn/src, src, lib, cli, tests/memfn and emit_sweep.py did not change between the
  design's cite tree 959c08124 and 7f55a62f9, so every cite was checkable.
- **Rulings frozen:** main 7f55a62f9 (D186 + add. 1-2 as amended 2026-11-03, incl. 7f55a62f9's own
  hunk; reviews r1, r2, 2026-11-03-r1).
- **FREEZE DRIFT: YES, plan.md only.** fa736a260 "[MEASURE-SET]: RULED line after refs" landed on main
  during the round. It RULES M2's order (not ordered against row 1; priced rows go dark on bare compiles,
  INTENDED) and restates stage 2's cards as "memchr, two-stream pair, walk, verify; Horspool-probe later".
  FIX-9 read it (it cited main HEAD), so its items (a) and (c) rest on the post-freeze row. 4f9368e7c
  (journal) also landed; not read. decisions.md and roadmap.md: unchanged since the freeze.
- **The design's own last commit (23:42:50) predates main's 7f55a62f9 (23:43:42).** That hunk is the
  source of finding R1 below: the design could not have carried it.
- **Coordinator:** crit-memfn-spanpick5 (opus). Critics opus x3, verifier sonnet. Draft: PROPOSED
  dispositions only.

## Stage-1 readiness verdict

**Ready for a build go: YES WITH LISTED TEXT FIXES.** No answer-level or speed-level finding. Every
stage-1 cite checked (about 45 across two critics) holds or is off by a line. Every population count
recomputed from raw data holds. emit_sweep.py covers every arm the witness names. The fixes are text,
plus one unit that main has ALREADY ruled (R1). Four items need a decision rather than a sentence;
each has a leaning below: R1 (the unit's shape), R4 (U6 keep or retire), R8 (translate grouping keep),
R2 (the NONE uniform mass's threshold readers). Two pre-build steps are main's, not the lane's: R10
(the ratchet rows with recipes, needed before stage 1's base count) and the roadmap §0a sentence.

Per unit (STAGE1's verdict, verifier-checked): 1a ready with text fixes (R11, R10); 1b ready with
text fixes (R2, R6); 1c ready with text fixes (R4; it depends on 1b); 1d ready with text fixes (R5, R6,
R7, R8); 1e ready with text fixes (R9, R11; it depends on 1d); 1f ready with text fixes (R3). MISSING
unit: R1.

**Re-check need:** none proposed. Every FIX-NOW below is checkable by diff against this list. The
lane that applies them should get a light single-critic diff check, not a full round.

## Lenses as run

| lens | model | question | why chosen |
|---|---|---|---|
| FIX (fix-induced + ruling check + sibling/general form) | opus | does each rev-5 change hold, what does it add untraced (siblings of every new field, every reader of a named home), and does rev 5 agree with D186 add. 1-2 ON MAIN | re-check of a revised design; rulings amended the same night |
| STAGE1 (premise + slot tracing, as readiness) | opus | per unit 1a-1f: cites against the build tree, can the witness fail, separability, completeness (purity grep, census shapes, 1f hunks, ratchet, roadmap, D186 obligations); verdict | the launcher's "last re-check before the build go" |
| SIM (simulate) | opus | implement the priced action from the text first, recompute every quoted number, drills (never-picked candidate, finer re-sweep, band edge cases, the with-data property's c_P outside the candidate set) | new incumbent and tie rule; quoted boundaries |

Not run: adversary (no trust boundary), measurement (stage 2's measurements are unchanged from rev 4,
covered there), cost/overlap (unchanged; ruled). D27: the design's contract is the pure plan face and
the python re-price; rev 5 already assigns the re-price's tests to a D27 author. RECOMMENDED in
addition: the 1d purity harness (R7) is a good D27 target (a promise, "same inputs, same plan").

**Which lens caught what.** All three found R1 independently (a coordinator planted check: main's
7f55a62f9 hunk post-dates the design). STAGE1 alone found the census blindness (R3a), the 1f reader
gaps (R3), U6's public readers (R4), the witness that cannot fail on reach (R6), the translate grouping
(R8), the row order (R9), the roadmap/ratchet pre-steps (R10) and the dependencies (R13). FIX alone
found the provenance siblings (R1's bytes/fidelity/digest), the refuse row (R12), the main-sync items
(R14) and the hysteresis family. SIM alone found the tie-anchor IIA hole (R15), the "no dearer than
c_P" overclaim (R16) and the band-0 labels (R17). STAGE1 and FIX both found the NONE rate-model point
(R2) and the `consulted` writer (R5); FIX and SIM both found the one-candidate-set gap (R18).

## Findings (consolidated) with PROPOSED dispositions

Severity: no answer-level or speed-level finding. One finding is a byte-identity RISK for 1d (R8). It
is avoided by keeping today's grouping.

### Stage-1 blockers-by-text (FIX-NOW before the go)

- **R1 = STAGE1-1 + FIX-1 + SIM-4 (+ FIX-2). VERIFIED HOLDS.** Main's D186 add. 2 (7f55a62f9): "The
  provenance fields (`mf_prov.source`, the bundle "default" label, memfn.h) leave the seam in span_pick
  stage 1". Rev 5 says "whether the field stays is main's call", and no unit 1a-1f does it. It is an
  MF_SITE_ABI event that rev 5 does not count ("1f is stage 1's only"). Readers: memfn.h :1213-1214,
  :1223-1233 (`mf_prov` inside `mf_akind`); memfn_sites.c :186-191 (map), :273-276 (writes), the prov
  stanza, and :233-249 (the KSRCTRACE record reads `prov.bytes`/`fidelity` from the built object, so
  e1_object_check.py's premise moves); tests/memfn/prov_check.c :27-34 (static `offsetof`: a build
  break); finder_check.py section L (:654-740); arm_fixtures.c :1569-1590; window_contract.md §3.1;
  memfn/include/CLAUDE.md. FIX-2's siblings: `digest` is the only home of the digest the kit's trace
  will name (no kit read today; a read trips L(4)'s `.prov` regex); `bytes`/`fidelity` let the kit tell
  a measured bundle from the default (bytes 0 for the default, findings.c :579), against "the kit never
  sees the source". Rev 5's band text keys "no sampling term" on "an authored default, a `fidelity
  synthesized` bundle", which is provenance. **PROPOSED: FIX-NOW.** Add unit 1g (or a declared part of
  1f's seam event): `mf_akind` keeps {tag, version, present, digest, payload}; source, bundle label,
  bytes and fidelity leave, with the reader list above. It is byte-identical (MF_SITE_ABI reaches no
  emitted text, memfn_sites.c :413). Rephrase the band as "pcrec states the sampling noise, or none".
  Strike "main's call" and the "For main" item.
- **R2 = STAGE1-11 + FIX-3. VERIFIED HOLDS (code; the compile contrast was not reached on 6 utf8
  patterns).** Main: with no rates, the rules rank by MEMBER COUNT, "declared as the rules' own
  tie-break, not a rate model". Today the uniform mass (presence.c :58-62) IS read as a density by
  thresholds. One is D-hors admission (window.c :1596 vs HORS_MIN 145,822: 38 or more members admits
  Horspool under NONE). The other is MARGIN's cost ratio (window.c :669-683). Every `-e utf8` compile is
  NONE. **PROPOSED: FIX-NOW (text in 1b).** Add a declared NONE row (member count -> uniform ppm).
  HORS_MIN and MARGIN reading it stay as a NAMED EXCEPTION (today's answers, stage 1 is no-mover), with
  the trigger "[SPAN-PICK-UTF8]'s per-encoding prior, or a priced row on NONE". pcrec's own NONE
  arithmetic (findings.c :606/:814) gets a pointer. If the manager reads main's sentence as "no
  threshold may read it", that is a unit change outside stage 1: a manager line, not an owner
  question.
- **R3 = STAGE1-3 (+ STAGE1-2 as R3a). VERIFIED HOLDS.**
  - 1f misses these readers: arm_fixtures.c :1685 (`mf_finder_pay`: a build break);
    tests/mech/sabotages/S1025_sn9-pay-tie-pays.sh + run_sabotage_matrix.sh :497 (retire);
    finder_check `--pay-grid` H (:641); memfn.h :1550-1557; rows.tsv/row_floors.tsv lines.
  - R8/R1/R2 sit AHEAD of the PRES rows in `fd_rows` (finder.c :249ff), so by the design's own rule 1f
    is also an MF_CLASS_V event.
  - **R3a (STAGE1-2):** the decider census's grep shapes miss presence.c :165/:182/:192 and window.c
    :1335, exactly the spellings 1b/1c delete. They also miss the B-row loop (:1754) and fd_pres's
    chain. A copy of presence.c's loop would pass the sabotage.
  - **PROPOSED: FIX-NOW.** Add the readers and MF_CLASS_V to 1f. Make the census a declared FUNCTION
    list with the grep as a widened backstop (`< lo`, `< sm`, `< wl`, `> c)`). Add a second sabotage
    that copies presence.c :182.
- **R4 = STAGE1-4. VERIFIED HOLDS.** U6's "landmark shadow" (presence.c :222-245) writes the public
  `mf_pres_picks.landmark`. pcrec reads it at emit_dfa.c :11256 (the KW-8 record) and
  run_pres_picks.sh :61 reads it, so "retired if no census reads it" is false at the base and 1c is
  not kit-only. **PROPOSED: FIX-NOW (decision, leaning KEEP):** U6 stays a named member until pcrec
  states the landmark as a candidate (the existing D167 A11 trigger). Drop it from 1c; the ratchet row
  stays.
- **R5 = STAGE1-5 + FIX-4. VERIFIED HOLDS.**
  - `art->consulted` has no writer in memfn/src, so breaker (d) is a FUTURE breaker.
  - (c) is already fenced: `mf_wdecide` decides quiet (window.c :1070), and quiet counts no reach
    (gate.c :943/:956/:978). 1d's (c) is a KEEP. The real risk is serving phase 2 from a stored plan;
    "No cache" covers it. Name it.
  - (b) misses compose.c :982/:988/:1005 and fd_route's `handle`.
  - pcrec ORs `consulted` over every attempt (memfn_stamps.c :275-286). "Taken call" must mean "a
    define", with every attempt's define still counting.
  - **PROPOSED: FIX-NOW (text).**
- **R6 = STAGE1-6 + FIX-5. VERIFIED HOLDS.**
  - Reach floors are `floor(0.9 x measured)`, and emit_sweep compares no reach. A fence that
    double-counts, or drops 10 % or less, passes.
  - Reach readers missed: run_g2.sh :986-1024, run_g2_gate.sh :144, trace_format.md, and rows_check's
    asked == records equation (fence both or neither).
  - `zzzzzzz~J` (the design's own counterexample) is in no corpus.
  - **PROPOSED: FIX-NOW.** The 1d/1e witness adds REACH EQUALITY (chosen/asked per row, base vs HEAD,
    with 1e's declared wfD->fd row map). 1b adds a golden-value test of the one primitive (NONE at k =
    1, 3, 6, 16, 256; a repeated byte; capped vs uncapped) and `zzzzzzz~J` via `--patterns-file`. Name
    the 588 sample's generator and the bench pattern list as `--patterns-file` inputs.
- **R7 = STAGE1-7. HOLDS (not separately verified; absence by grep).** The purity witness has no
  harness and no builder. It passes trivially today, so it needs a plant. **PROPOSED: FIX-NOW:** the 1d
  lane builds it in arm_fixtures (N sites, in order, reversed and repeated, `mf_wreply` compared field
  by field). Its sabotage is a row that reads `art->nsites`; add a sticky-`err` case. A D27 author is
  optional.
- **R8 = STAGE1-8. VERIFIED PARTLY (structural).** T-VERIFY's "`run_group_ok` read by BOTH renderers'
  grouping" would change `translate` (window.c :1278-1300 groups by `pterm`, with no core, cap or
  adjacency clause; a pinned join needs no core). It is not provably byte-identical. **PROPOSED:
  FIX-NOW (decision, leaning KEEP):** translate's grouping stays a named member, until a census shows
  the two agree on every B-fn site.
- **R9 = STAGE1-9. VERIFIED HOLDS.** T-FIND's listed order "D1c, PAIR, D1, D1w, R7w" is not today's
  (D1, D1c, D1w, PAIR, R7w). The answers are disjoint, but the trace and `pres_row` move. **PROPOSED:
  FIX-NOW:** write today's order, "order kept".
- **R10 = STAGE1-10. VERIFIED HOLDS.** The kit's ratchet rows are not in roadmap §5 and have no
  recipes ("position enumerators" names no members), so stage 1's base count cannot be taken.
  Roadmap §0a's first bullet still says "candidates and their prices" and "opaque entries with
  prices", against one plan with prices in the trace (A-PLAN point 1 is amended; §0a is not).
  **PROPOSED: PLAN, as a PRE-BUILD step for main:** add the rows with recipes and the §0a sentence
  before the first lane. The design should say "main adds ... before 1a" instead of "no roadmap edit
  is left".
- **R11 = STAGE1-12 + FIX-11. HOLDS.** Cite drift: findings.h :300 -> :303; memfn.h :1212 ->
  :1213-1214; compose.c :1303 is a reader. 1a's test edits are missing: finder_check.py :109
  FIND_ROWS, rows.tsv :120-122, row_floors.tsv :104-106. 1e's wfD->fd table rename in
  rows/floors/trace names is unlisted. compose.c :882's stale comment sits on a line 1d touches.
  **PROPOSED: FIX-NOW (text).**
- **R13 = STAGE1-13. VERIFIED PARTLY.** 1c depends on 1b (holds). 1e depends on 1d only because 1d
  reshapes `wf_plan` into the step list (holds as worded). The stated order respects both, but no unit
  after 1a can land out of order: say so. Landing 1f right after 1a would stop 1e's merged walk from
  carrying R8/R1/R2 and the pay rule only to delete them. **PROPOSED: FIX-NOW (text; leaning: move 1f
  to follow 1a, or say why it stays last).**

### Stage-3 / pick text (FIX-NOW as text; none blocks stage 1)

- **R12 = FIX-6. VERIFIED HOLDS (repro: `-e utf8 --analysis l1none` is refused on 8 of 8 patterns).**
  The rate-source table lacks the 4th outcome, rule 9's REFUSE: a chain answers but cannot derive, and
  the kind is consulted. Main's D186 text omits it too. **PROPOSED: FIX-NOW (a first row in the table),
  and a one-line note for main's D186 text.** The SUSPECTED part goes to PLAN, triggered by the first
  priced row reading rates. The `_FINDINGS` consult is pcrec's MIRROR asks only. memfn_stamps.c :385
  "no routed kit row consults a kind yet" is stale. known.c's cover site has no mirror ask.
  Unlock (FIX's): the kit reports a per-kind consult mask from `mf_art_end`.
- **R14 = FIX-9. VERIFIED (against main fa736a260, i.e. FREEZE DRIFT for (a), (c)).** Sync to main:
  - (a) M2 order is RULED (PENDING-RECORD stale).
  - (b) The default-prior log is "filed with the first such change".
  - (c) Stage 2's card list vs [MEASURE-SET]'s: Horspool-probe is later. Consequence: D-hors
    incumbents stay unpriced, so §The pick 4 keeps them. State it.
  - (d) Main's "smp20 blind keeps {x,X}" vs rev 5's forecast: a main wording item.
  - (e) "Minimax is PAIRWISE" is still live on main, "within one rate source". Rev 5 should say
    "reduced to §The pick 3's qualifier test", not "SUPERSEDED".
  - **PROPOSED: FIX-NOW (text); (d), (e) DOC for main.**
- **R15 = SIM-1. VERIFIED HOLDS (independent construction).** The tie set is anchored on the
  CHEAPEST qualifier, and the within-band relation does not chain. So a qualifier that is never picked
  can flip the pick (I 100, q1 80, q2 84, band 5, TIE prefers q2 -> q2; add c 78 ranked last -> q1).
  Equal-price cheapest qualifiers leave the anchor undefined. The Growth rule then moves picks at
  sites a new method never wins. The design claims only the never-QUALIFYING property, which holds.
  **PROPOSED: FIX-NOW (text):** state the weaker property. Make the anchor deterministic: the
  incumbent-side band, or TIE's own order among qualifiers. Add "a new method row's movers census
  counts sites it does not win" to the Growth rule and §Staging's per-row census.
- **R16 = SIM-2. VERIFIED HOLDS.** "If c_P qualifies the pick is no dearer than it" is false once TIE
  acts. The bound is price(c_P) + band. **PROPOSED: FIX-NOW (one sentence).**
- **R18 = FIX-7 + SIM-3. VERIFIED HOLDS.** "Built from site facts alone (no rate input) ... ONE
  candidate set" is false where inc_P and inc_B differ outside the row's levels. KEY A-mass, MARGIN and
  C-model read `d->rate` (window.c :421/:470/:552/:669-684/:991). The NOT-covered clause names a
  different population (sites no row admits). Row 1's condition "whose default is a two-member stop"
  reads a rate-dependent kit output, not a stated fact: smp20 is admitted blind and not under `prose`.
  It is harmless there. **PROPOSED: FIX-NOW (text):** scope "one candidate set". Add the
  differing-incumbent sites as a [BENCH-WITHDATA] census line and a fifth cause beside (i)-(iv).
  Phrase row 1's admission on stated facts ("a NONE alternative whose core position 0 is a two-member
  set").
- **R19 = FIX-8. VERIFIED HOLDS.** D176 Q5 says ties are "decided by the EXISTING declared tie rows".
  Rev 5 adds T_BAND -> TIE_DEFAULT. Qualifiers can differ in position AND method (smp20's {X,x} PAIR @0
  vs '/' memchr @1), which no existing row compares. **PROPOSED: FIX-NOW (text):** map each level's
  tie to a named row (position: offset by span kind; alternative: T_MARGIN's PARKED; method: row 1's
  new row) and record a manager line amending Q5's "existing" for the method level (answer-free until
  row 1).
- **R20 = SIM-8.** Rule 4 is silent on an INCUMBENT that reads a noiseless card. **PROPOSED: FIX-NOW
  (one sentence):** any card with a nonzero coefficient difference and no noise means no departure.
- **R17 = SIM-5 + SIM-6 + SIM-9. VERIFIED HOLDS.**
  - SIM-5: the table's pick column and the 3,536-point grid counts are band-0 argmins (smp20.py :98).
    Under rule 4 with noiseless stand-ins every point keeps the incumbent. Label them "band 0, argmin".
  - SIM-6: name P by the stamp digest `1822fb973b95a4da`, not R-33's local hash `a322116b1b87f9f6`.
  - SIM-9: §The shape mixes arms. The RTE split is 733/696 of 1,429; 740/714 are RTE+DEF.
  - Also from SIM's divergence list: 4x/h1 40 k* 0.971 belongs with "under 1"; the blind P argmin
    over the grid is '/' at 3,381 of 3,536 points, so "P keeps {X,x}" is a single-point reading (the
    forecast already hedges; quote the count).
  - **PROPOSED: FIX-NOW (doc).**
- **R21 = SIM-7 (SUSPECTED).** verify_r prices "other positions in ascending mass". T-VERIFY runs
  the run member first and compares the run as one T-CMP stretch: the price prices a plan that is not
  run. It is negligible on smp20. **PROPOSED: PLAN (row 1's design: price verify over T-VERIFY's own
  step list); one sentence now.**
- **R22 = FIX-10 (SUSPECTED).** finder_check L(4) varies rates and provenance together, so it goes
  red at the first priced fd row. **PROPOSED: PLAN (row 1's witness list):** hold the rates fixed and
  vary only provenance. After R1 that becomes "vary the digest only", which is the check that "the kit
  never distinguishes a bundle from the default".

### General form and unlocks (FIX's standing questions)

- **Handed-fact resolution family** (measures set, byte-rate, run-rarity, the chain): one first-match
  per kind, (caller choice -> per-(encoding|target) default -> NONE, refuse when underivable and
  consulted) yields (payload, digest). The kit reports consults. **Unlock:** one consult channel, which
  retires the mirror asks (R12). **NOTED -> PLAN row** (trigger: first priced row reading rates).
- **Hysteresis family** (MARGIN, T_BAND, the qualifier test, `pcrec_landmark_margin`, HORS_MIN; on
  the evaluation side D186's bar and [BENCH-WITHDATA]): depart iff price(ref) - price(ch) > k·σ.
  **Unlock:** the same rule judges predicted vs measured movers, and row 1's spread measures k (the
  UNMEASURED coverage factor). **NOTED** (rev 5's E2 already unifies the compile-time side at row 1).

## PROBED-AND-HELD (consolidated)

- About 45 stage-1 cites (purity breakers 13-15 of 13-15, Table E/T-FIND/T-VERIFY sites, KEY/M/TIE,
  rc_row_of, kit_set_test, req_run_member, landmark admission, findings.c run pin) hold in the build
  tree, apart from R11's line drifts.
- Every population count re-run from R-33's raw sweep.jsonl: 1,742/1,767; 1,429/291/22; 1,454 =
  740+714; A-floor 1,420/1,835 (1,397/1,800 RTE); 371/371 OFS. Identical to counts.out.
- witness.sh was re-run on the review tree: 16 compiles, byte-identical to witness.out (stamps
  included).
- smp20: 28 prices (an independent implementation from the text), 16 exact k* cells, "28.0/103.7",
  the DEF "no move", and the 3,536-point grid counts all reproduce. A finer re-sweep cannot add a
  winner (prices are linear in k).
- The kit sees no source today: zero reads of `prov`/`MF_PROV_`/`fidelity` in memfn/src. There is no
  built-in rate table. pcrec's resolution matches rows 1-3 (`byte-rate=default:1822fb...` byte, `none`
  utf8). A shipped bundle moves no blind compile.
- 1f's registry hunk: 14 memfn denies = IDENT_MEMFN, and 14 -> 12 is right. `mf_set_terms` (1a) is
  internal, so it is no seam event.
- emit_sweep covers default, vm, every `--memfn=no-X`, both SIMD flags, utf8, `--list-*`, facts and
  stderr. A mis-ordered tie IS caught (the utf8 arm is NONE, with ties everywhere).
- The plan face is pure beyond the listed breakers: `const mf_art *`, quiet, no reads of earlier
  sites, no cache. C3's scoping of order-dependence to the emitting face holds.
- The never-QUALIFYING candidate property holds. The incumbent never enters the tie set. "No rates:
  keep" matches the NONE code path.
- The rulings rev 5 carries agree with main: minimax struck, D186 over D144, C9, one plan, pure
  function, witness wording, O3, `zen4-grid3`, flat guard dropped on a required random-like regime.

## By-id completeness

FIX-1..11: R1, R1 (FIX-2), R2, R5, R6, R12, R18, R19, R14, R22, R11. STAGE1-1..13: R1, R3a, R3, R4, R5,
R6, R7, R8, R9, R10, R2, R11, R13. SIM-1..9: R15, R16, R18, R1, R17, R17, R21, R20, R17. Every id
has a disposition.

## Lessons for the guide (proposed)

1. **Freeze-skew between a design's last commit and the rulings' commit.** The owner's/manager's
   ruling hunk landed 52 s after the design's commit, and every critic found the gap. The coordinator
   should record, at the freeze, whether any ruling commit post-dates the subject's last commit, and
   tell critics to read the rulings on main (done here; it worked).
2. **A post-freeze ruling read by a critic.** FIX read plan.md at main HEAD, not at the frozen commit,
   so FREEZE DRIFT reached a finding. COMMON should say "read rulings with `git show <FREEZE>:path`,
   never the working tree", and the verifier should flag any finding that cites a post-freeze line (it
   did here).
3. **Census-by-grep lens drill.** For a decider/ratchet census whose shapes are a grep, run the grep
   and list the deciders it MISSES that the units delete (STAGE1-2). Add it to the slot-tracing lens
   question.

## RULINGS (kit manager, 2026-11-03)

- Verdict ACCEPTED: stage 1 is ready for a build go once the listed text fixes land (rev 5.1).
- All PROPOSED dispositions ACCEPTED. R8: keep the translate/run_group_ok decider as a NAMED MEMBER (not folded in stage 1), since its byte identity is not provable.
- R1: add unit 1g (provenance leaves the seam, an MF_SITE_ABI event), with its full reader list, including prov_check.c; bytes/fidelity/digest decided in the unit text (the digest stays: the kit's trace names it).
- R10 goes to main as a PLAN item before the build.
- Process changes ACCEPTED: a "readiness" lens row for the last re-check before a go; COMMON reads every ruling file via `git show <freeze>:path`.
