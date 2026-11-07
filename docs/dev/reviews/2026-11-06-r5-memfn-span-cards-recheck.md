# Review 2026-11-06 r5 — span_cards rev 1 (design RE-CHECK: span_pick stage 2)

**Subject.** docs/design/memfn/span_cards.md REVISION 1 at b06c7447f2b1150e3aed423987ce83fcd22ac873 (branch
lane/memfn-s2rev1 tip, unchanged at hand-back), with its evidence scripts docs/design/memfn/span_cards/
(drill.py, j1_drill.py, coverage_drill.py). It revises rev 0 after review 2026-11-06 r4 (memfn-span-cards). Critics
read only r4's findings table and its "## Rulings" section, extracted, as the claimed fixes.
**Build tree:** main 9f5f082de. Main was 592ed6da3 at launch, and 9f5f082de adds only known_issues K139. The review
tree was built there (`nice make -j2`, unlocked, rc 0). No cited code moved between rev 0's cite base fb22c62a6 and
9f5f082de (src cli lib memfn scripts tests docs/spec: empty diff). The client docs (span_pick.md, measure_sets.md,
docs/spec/measures.md) are identical at the subject and at main.
**Rulings frozen at 592ed6da3.** They were re-diffed when the critics returned and again at hand-back. main moved
plan.md once (ad4ead990, an [ISL-PRICE] note after K139), which is unrelated. **No FREEZE DRIFT** on any ruling in
scope.
**Freeze note for the launcher:** the subject's §8.3 says "main RULED (B)" (DEFAULTS flips at S2e). No record of that
ruling exists in main's tree at 592ed6da3 or 9f5f082de (searched requests.md R-35, responses.md, decisions.md,
plan.md, owner.md, wake.md). The only record is the kit's ASK at responses.md:3202-3205 on the subject branch. R-35
item 1 on main still reads "leaves DEFAULTS unchanged". The critics took the ruling as in force, per the launcher.
Main should record it where R-35 lives.

**Verdict (proposed): NOT READY as a whole. S2a and S2b are READY WITH TEXT FIXES; S2c-S2e need a rev 1.1.** Rev 1
closes most of r4. The DEFAULTS framing, D188's three facts, the derived-noise drop, the §7.1 seam, the per-launch
normalization, the MEAS-2/3/7/10 gate repairs and the drilled estimator all hold. MEAS-7's false drift refusal is
gone: 0/4000 at s 0.2-1 %. The design's own drills reproduce byte-for-figure, and an independent integer
implementation from the text agrees with drill.py on every shared case. No finding moves an emitted byte or a match
answer. The fixes did introduce new defects, in five places:
1. **The `cells` home cannot carry the exact recompute Goal 3 promises.** `length` holds both E and LEN. `round` has no
   value. Group/job/launch identity is unstated. "base in the same group" contradicts §3.7's shared bases. The
   recompute domain for refused groups, FRG and J1 is unstated.
2. **Three S2c checks cannot go red as written.** Check C's new guard reads a directory zen4-grid3 never enters
   (population zero). The twin's "objects `cmp` DIFFERENT" is true with no pad at all (STT_FILE). The cell-text hash
   check compares a window-site rendering with formhash's composer canon.
3. **Placement now enters the gates as a fixed offset.** The perturbed twin puts placement into `aa`, so a walk
   placement offset can refuse the unit group deterministically: re-running the frozen text refuses again. J1 has no
   placement term, and the per-job control is linked into a different driver per job. Magnitudes are unmeasured: a
   dry-run probe at S2c settles it before the window.
4. **S2e's census tool does not exist.** emit_sweep has no `measures` data kind, and movers/0001.tsv was written by a
   lane script.
5. **Some rulings were applied in one section only.** D188 add. 1 is applied only in §2.7: six sentences still wait
   on an "unruled model", and §2.5's scalar-pick-plus-`#if`-rungs reading is not marked interim. D176 Q3's narrowing
   moved into [KIT-POLICY-TABLE] rather than being withdrawn. Two R-35 drops are not put to main.

## Lenses as run

| lens | model | question | why chosen |
|---|---|---|---|
| fix-induced (`fixind`) | opus | for each claimed fix: what read, hand, row, field, check or home does it add, and what does that break or leave unstated in today's code | RE-CHECK of a revised design (lens table) |
| readiness (`ready`) | opus | per build unit S2a-S2f (+ S2g separability): do the cites hold, can each witness and sabotage row (a)-(q) go red, is the unit separable, is it complete; overall verdict | the last re-check before a build go (lens table) |
| measurement (`meas`) | opus | implement §3.4-§3.6 and §6 from the TEXT, drill them on constructed outcomes, then diff against the design's drills; recompute the quoted numbers; the standing measurement questions | a measured quantity whose estimator rev 1 rewrote; r4's accepted process change (2) |
| ruling check + slot tracing (`ruling`) | opus | does rev 1 agree with every ruling it rests on (D188 + add. 1, DEFAULTS (B), R-35, D176/§7.1, D157, D77, D149, D186), does each slot have one home; the goals; **both standing questions (sibling of a family; general form + unlocks) were assigned HERE** | rulings relied on + new slots (cells, formhash table, z's home) |
| verifier | sonnet | re-ran 17 consolidated items | skill §6.2 |

Not staffed: simulate (no selection rule over a corpus; J1's rule went to meas), soundness (no answer-identity-by-proof
claim beyond "nothing consults", which held), adversary (no trust boundary is added; the loader's bound refusal is a
contract item, covered by fixind-7), owner criteria (D188 add. 1 is the only owner text new since r4; the ruling lens
covered it).

## Which lens caught what

- **fixind:** the cells-home overload (with ready, meas, ruling), check C population zero (with ready), the cell-hash
  shape (with ready), the partial-recompute domain, the `lengths`/`aa_rule` repurposing, the invisible ksgen omission,
  the copied bound and squared noise, the MFMEAS filter and positional reader (with ready), embed sizing (with
  ruling), the D188a1 leftovers (with ruling), stale §10 cross-refs, and index.tsv supersession.
- **ready:** the missing data-mover census tool (alone), the vacuous twin cmp (with meas), the S2b->S2c lock, J1's
  (b) in a chained window, the S1234 family anchors, the smp20.py readers (with ruling), and the per-unit verdicts.
- **meas:** placement as bias in J1, the unit gate and the drift control (alone); z's drill without the `aa` term and
  on a different event; the per-hit NULL floor; the drift statistic; J3's count; the drill-table inputs.
- **ruling:** reading §2.5 as the abolished fall-through; zen4-grid3's undeclared target; [KIT-POLICY-TABLE] vs D176
  Q2/Q3; the R-35 drops; D149 labels; Goal 2 cannot fail; three families + general forms.

## Findings (consolidated; PROPOSED dispositions)

Dispositions: FIX-NOW = rev 1.1 text/design before the build go of the named unit; PLAN = a filed row; DOC = a text
fix, rides rev 1.1; MAIN = needs main's ruling; NOTED = no action. Class: FI = fix-induced, RES = residual of an r4 id,
PEM = pre-existing, missed by r4.

| id | lens(es) | class | sev | verify | finding | proposed | reason |
|---|---|---|---|---|---|---|---|
| CELLS-1 (fixind-3, READY-10, meas-5 a-d, ruling-7 i-ii) | fixind, ready, meas, ruling | FI (SLOT-1 x MEAS-5/6) | design (Goal 3) | HOLDS | (a) the `length` field holds E (§3.4 step 2) AND is the lookup key `c(a, LEN, l)` with LEN 1048576, and measure_sets.md:1230 refuses off-card lengths. (b) `round` has no value for a per-launch median cell. (c) no column ties a group to its job's `ctl` or to J2's unit arm name. (d) "base in the SAME group" (§2.3, §3.4) vs §3.7 J3/J4's bases counted once for four groups, and "the walk's miss base is the control's 1 Mi point" vs the card's `base.<form>`. (e) launch identity across groups is unstated | FIX-NOW (S2c spec hunk) | Goal 3's EXACT recompute is written from this text by someone sharing no source; four of its inputs are ambiguous. Least form: an event-count cell column (format 2) or E on the row; `round` = a stated literal; a group-naming rule carrying the job; one base rule, same group or named shared, with the J3/J4 counts redone |
| CELLS-2 (fixind-4, meas-5 e, i; ruling-7 iv) | fixind, meas, ruling | FI | design/check | HOLDS (text) | what the recompute covers is unstated: do refused groups' cells stay (FRG, "every twinned arm", needs them; §1.5 forbids unread cells); is J1's evidence in the set (its rule flips a MEASURED comment, ruling-7 iv); is a non-J2 control a gated row; the quiet-gate input is not recomputable; delta-only groups pass vacuously, so REFUSED is near-unreachable | FIX-NOW (text) | name the recompute's domain and FRG's population; name J1's evidence home; state the outcome rules for delta-only groups |
| CELLS-3 (fixind-5, ruling-7 iii) | fixind, ruling | FI (MEAS-5, MEAS-1/4) | maintenance | HOLDS (text) | card `lengths` becomes an estimator grammar and `aa_rule` gains `twin-per-arm;bimodal-unit` (renaming `bimodal-test`), with no amendment of measure_sets §7.2 or kit-grid.tsv's column comment. The grammar substitutes key tokens by dim name, against measures.md §2.3¶2 ("no placeholder token ... reads no owner's vocabulary"). grid1's `lengths` already starts with `slope`, so the recognizer must skip it "by name" | FIX-NOW (text) | add the §7.2 and §2.3¶2 hunks or spell the grammar without placeholders; key the parse on format 2 (counted), not a name list |
| CHECKC (fixind-2, READY-4) | fixind, ready | FI (SLOT-4 x CONTRACT-1) | check | HOLDS | finder_check.py check C reads only memfn/data/sets/*.tsv (:345-399), and §3.8/sabotage (o) keep zen4-grid3 out of it: S2c's witness "check C resolves every new dep" runs over zero grid3 keys. SLOT-4's original defect has moved one directory over. Plant (n) goes red only if the guard sits in the card walk (:340-343), not at the cited :395-399 | FIX-NOW | put the deps guard on card rows; name a counted check that resolves measure_store sets' form tokens, or state that row deps are `-` and only cards carry deps |
| HASH (fixind-1, READY-3) | fixind, ready | FI (PREMISE-2/3/5, COST-5 (10)) | check/design | PARTLY (shape HOLDS; red-in-correct-build not rendered) | §3.2 times walk/libc from `g2_win_gen.c --cards` window sites but keeps their formhash entries "today's, byte for byte": `canon()` (formhash.c:237-277) is a composer STMT/FIND site with `pred.nterm = 1`, `[0-9]` via table, `on_miss "return 0;"`, and constants and statements move the hash. g2_win_gen.c sets no `pred.nterm` (0 hits), so the `walk-set` builder cite (:1048, "the composer's FIND site") does not hold | FIX-NOW | render each hashed arm at its entry-table row's site shape and facts (composer sites from g2_gen.c), or change the walk/libc entries and list their readers; state which text the cell hash covers |
| TWIN (READY-2, meas-1) | ready, meas | FI (MEAS-1) | check/design | HOLDS (no-pad cmp differs, STT_FILE; same name same bytes; .text identical); loop-phase half NOT REPRODUCED (verifier: 24/24 links moved the phase; critic: 6/12 did not) | the "objects `cmp` DIFFERENT" assertion is true with no pad whenever the twin's file name differs, so sabotage (j) stays green. Whether the pad plus reordered link moves the hot loop's 64-B phase depends on the link | FIX-NOW | assert on the LINKED driver: the timed function's or loop's address mod 64 differs (`nm`/`objdump`), or `.text` bytes; record the phase pair per arm |
| PLACE (meas-2, meas-3, meas-7 confound) | meas | FI (MEAS-1 x MEAS-4/8, MEAS-7) | design | mechanisms HOLD (scripts reproduced exactly); magnitudes SUSPECTED (τ, offset unmeasured) | placement is now a FIXED per-build offset inside `aa`, not noise. (i) the unit's half gate refuses deterministically once the walk/walk#b offset exceeds ~1 % (s 0.5 %: o 1 % -> 10.5 %, o 2 % -> 96.4 %), and §3.5's "re-run whole in a later window" refuses again. (ii) J1 compares separately compiled widths against ONE 128#b draw: (b) 1.3-4.8 % with no effect at τ 2-4, and power falls from 82 % to 12-19 %. (iii) each job's control is linked into another driver, so drift compares placements | FIX-NOW (decide) + measure at S2c dry run | state whether placement is NOISE (estimate its scale from more than one perturbation) or BIAS (report it, gate the unit on run noise); give the deterministic refusal its own outcome; one prebuilt control executable shared by every job (sha asserted); time walk vs walk#b once in S2c's dry run |
| DRIFT (meas-7) | meas | FI (MEAS-7) | design/doc | HOLDS (rates reproduced) | the drift check measures the common component that step 3's normalization cancels, and is blind to arm-specific drift. At s 1 % a true 3 % drift is refused 17.5 %, 5 % 76 %; the threshold is not the stated "size that matters" once s > ~0.35 % | FIX-NOW (text) | argue which drift it proxies or drop it as redundant; restate the threshold's power |
| Z (meas-4) | meas | RES (MEAS-9) | speed (safe side) / doc | HOLDS | coverage_drill omits §3.4's `aa` term (noise ≈ 1.38 σ with in-launch noise: 2.31 % -> 0.31-0.48 % at z 3), and drills a new-draw event, while span_pick.md:234-235's departure is decided on STORED values (0.05 % at z 3) | FIX-NOW (text) | re-drill with the estimator as written and a stated within-launch share; state ONE event (amend span_pick's sentence or §6); z stays an UNMEASURED DEFAULT |
| FLOOR (meas-6) | meas | FI (MEAS-3 x MEAS-6) | design (row-1 keys unpriced) | arithmetic HOLDS; this run's FRG unknown | the delta NULL floor `FRG x base` scales with the whole 1 MiB call: at grid1's FRG 3.09 %, walk-form hit rows are NULL below 31.6 wb per hit at g 1024 (7.9 at g 256), inside smp20's 5-40 wb stand-in range; perturbed twins likely raise FRG | FIX-NOW (text) | state the minimum resolvable per-event cost per key against what row 1 must resolve, or floor on the paired D_l only |
| CENSUS (READY-1) | ready | PEM | design (S2e content) | HOLDS | emit_sweep.py has no `measures` data kind (:2766 "joins at M1", DATA_KINDS = analysis, limits; stamp regex strips `_FINDINGS` only). movers/0001.tsv was written by docs/dev/lanes/m0build/census.py in another shape. S2e's "data-mover census under both sets" and §5's per-unit proof have no tool | FIX-NOW | S2e names the tool and 0002.tsv's shape (m0build's re-run, or S2e builds emit_sweep's `measures` kind with its readers); S2a-S2d's proof is the ordinary two-build emit_sweep |
| KSGEN (fixind-6) | fixind | FI (CONTRACT-3 x CONTRACT-7) | check | HOLDS | meas_store_check.c compares DECODED views (:78), and CONTRACT-7 keeps noise out of format 1's decoded view. At S2a only grid1 is committed, so a ksgen omission (positional zero) is invisible, contrary to §4.5's claim | FIX-NOW (S2a) | a format-2 store fixture through ksgen, or a raw-field compare, plus a sabotage row |
| BOUND (fixind-7) | fixind | FI (CONTRACT-5) | maintenance/design | HOLDS | ks_measures.c may not include memfn.h (dependency rule, S1242), so the loader's 10^15 is a COPY, against K138's "read from the seam, not copied". MF_MEASURE_MAX's rationale covers sums of four values; noise is SQUARED in the quadrature (10^30 > int64) | FIX-NOW (text) | name the bound's one home (a ks_measures.h constant the kit's check asserts equal, or the reverse), amend K138's form or say how it is met; derive a noise bound for the square, or state row 1's arithmetic |
| MFMEAS (fixind-8, READY-7) | fixind, ready | FI (CONTRACT-8) | check/maintenance | HOLDS | memfn_sites.c:86-87 hands only `kit.` rows with a value; the triple digest's file-side rule states no such filter, so the witness is red on a correct fill with null rows. run_part_measures.sh:64-90 reads MFMEAS positionally and is not listed | FIX-NOW (text) | state the filter in the spec/§4.2; append the new fields after the `%p` columns; list the script |
| EMBED (fixind-9, ruling-9 b) | fixind, ruling | FI (SLOT-1) | size; Goal 1 vs Goal 3 | HOLDS | ksgen writes every cell into the pre-parse (7 pointers = 56 B per cell, about 77 KB for 1,370 cells, plus strings; .inc text is about 6x). libpcrec.a is 1.83 MB today, so a 10-15 % add is plausible. measure_sets.md:625-628's sizing ("cells and cards add about 4 KB") is not amended. The cells are caller-visible via `--list-measurements=X` | MAIN (FIX-NOW text) | a lower-ranked goal (3) moving a higher one's quantity (1): state the conflict and decide by rank (cells outside the embed as a spec event, or measured growth accepted); amend :625-628 |
| GOAL2 (ruling-9 a) | ruling | PEM | design | HOLDS (text) | Goal 2's measurable form is met by a run whose delta rows are all NULL and whose non-unit groups are refused but one: it cannot fail | FIX-NOW (text) | a floor on PRICED row-1 keys, else re-run |
| D188A1 (fixind-10, ruling-1) | fixind, ruling | FI (manager's D188a1 edit) | doc | HOLDS | six sentences still say "until the SIMD model is ruled" (§0 row 8, §2.5 :217/:240, §9 S2g, §10 item 5's "relay the model question", STATE AT HANDOFF). Facts are read "per level" at :261-266/:289/:297 vs "per declared target" at :277-284. Fact (b) is homed in PROVENANCE.md, outside the set's sha and digest, though D188 says the SET records it | DOC | "HELD until [XARCH-DEV]'s go"; one reading (per variant's target); say where (b) lives relative to the set |
| SIMD-READ (ruling-2) | ruling | FI | design | PARTLY (quotes HOLD; "is the abolished fall-through" is an argument) | §2.5's chosen reading (scalar pick, SIMD rungs via today's `#if` selector arms, vrun.c:428-429) is what D188 add. 1 says runs "a plan chosen for another target". Its consequences are undrawn: interim until [XARCH-DEV]; under variants C9 is no longer "the only way"; "SIMD OFF by default" becomes a today-only bound | DOC + For main | mark the reading interim on today's tree; list (ii) as an amendment candidate (span_pick §The pick 6, D186 add. 2 C9) |
| TARGET (ruling-3) | ruling | PEM (sharpened by D188 add. 1) | design | absence HOLDS; consequence not checkable (no selector exists) | zen4-grid3's `class` and compile target are never stated, while grid1's header says `x86_64-avx2/zen4`, `isa x86-64-v3 avx2`. A copied class reads as the AVX2 variant's prices under [XARCH-DEV] | FIX-NOW (text) | declare the priced target (the fixtures' -march) and `class` in the header |
| POLICY (ruling-4) | ruling | FI (SLOT-7) | design/doc | facts HOLD; "relocated not withdrawn" is a reading | [KIT-POLICY-TABLE]'s members (MATERIAL, MAX_SET, HORS_MIN) are plan_cost.def rows today, so homing them outside the sets IS D176 Q3's narrowing ("rows migrate into the sets"), now carried by a plan row. HORS_MIN is deleted by D176 Q2. MAX_SET is pcrec's PCREC_OFSK_MAX_SET (a pcrec fact). The plan row's "COVER_Z_E3 in plan_cost.def" is false today | MAIN (+ DOC) | present the cost/policy split as a D176 Q3 amendment for main/Frank; drop HORS_MIN and MAX_SET from the member list or mark them; main fixes its plan row's "today" clause |
| R35 (ruling-5) | ruling | FI / RES (MEAS-13, COST-3) | design/doc | PARTLY ((i),(ii) HOLD; (iii) the movement is relayed, the C9 sentence is not named) | R-35 item 1's "derived noise by quadrature" drop (§4.3) and the census-scoped `verify_cmp` narrowing of "each form" are not §10 items. S2g held behind [XARCH-DEV] moves D186 add. 2 C9's "SIMD-form cards join stage 2", and §10 item 4 says "amends nothing ruled" | DOC (§10 items + §10.2 rows) | main sees every drop of its request as an amendment |
| D149 (ruling-6) | ruling | PEM/FI | maintenance | not verified (text) | unlabelled chosen constants: drift factor 3, J1's margin 2 and "5 of 8", the 40-byte pad | DOC | label UNMEASURED DEFAULT or DERIVED, with triggers |
| J1-WIN (READY-6) | ready | PEM | design/process | SUSPECTED | J1's outcome (b) removes PAIR arms from J2/J3, which are chained `after` J1 in one window with declared populations: who reads J1's verdict between jobs, and what is J2/J3's population then? | FIX-NOW (text) | J1 in an earlier window, or its pair arms a separate removable group, recorded PARTIAL |
| LOCK (READY-5) | ready | FI (COST-2) | maintenance | HOLDS | S2c reads census0.out, so S2b -> S2c is order-locked; §9 says "S2b is separable" | DOC | "S2b -> S2c -> S2d -> S2e locked; S2a independent until S2e; S2f after S2e" |
| ANCHORS (READY-8) | ready | PEM | maintenance | listing HOLDS; anchor move needs the edit | S1234 (the noise/abs column swap, the exact column S2a starts parsing) and S1230-S1233/S1235/S1239 anchor ks_measures.c and are not listed | DOC | list them; re-verify S1234's detector on a format-2 fixture |
| SMP20 (READY-9, ruling-8) | ready, ruling | FI (SLOT-8) | doc | HOLDS | deleting smp20.py leaves readers: span_pick.md:286/:289 (a line cite), span_pick/CLAUDE.md:12,21,34, witness.sh:4,6 | DOC | add to §10.2 / S2b's package; say the golden is smp20.out plus one line |
| J3 (meas-8) | meas | RES (MEAS-14) | doc | HOLDS | J3 is 46 points by §3.7's own arm list, not 54; the total is 188 (20.8 min), not 196 (~22). The ±1.1 % and 59900..60100 table inputs are not drill.py's (3.82 % vs 4.96 %; 102 vs 92) | DOC | fix the counts; the table cites the drill's inputs. The 35-minute window stands |
| XREF (fixind-11) | fixind | FI | doc | not verified (text) | §4.6 "§10.3" / §4.4 "§10.4" use rev 0's numbering, and §10.3 is now a heading; §0 row 9 says "five items for main" but §10 lists six | DOC | |
| INDEX (fixind-12) | fixind | FI (PREMISE-4) | doc | not verified (text) | index.tsv's `supersedes`/`status` for zen4-grid3 and grid1 are unstated | DOC | |
| CITE (READY-11) | ready | — | doc | — | span_pick ":266-267" is at :267-268 | DOC | |
| FAM-A (ruling-10 A) | ruling | PEM (standing question) | design | n/a (proposal) | "which facts reach form X" is declared three times at S2c: formhash's new entry table, G2 `--cards` builders, and the router rows they must hit (R-MS3 fixtures a fourth reader). General form: each choice-table row declares a WITNESS fact set, everything renders from it, and the control asks the router with those facts | PLAN (kit manager decides at S2c: unify, or argue the parallel list) | third member created by this design (memory pcrec-general-mechanisms-not-special-cases) |
| FAM-B (ruling-10 B) | ruling | PEM | design | n/a | the fourth hand-built slot harness (650, grid1, grid2, span_cards/slot) | PLAN (§12 unlock: the next slot is written against a shared slot library M3 later wraps) | D77's measured need for M3's run-control half |
| FAM-C (ruling-10 C) | ruling | PEM | design | n/a | three provenance vocabularies (row status, mf_noise_state, D162 add. 4 rate provenance); row 1 reads all three in one qualifier | PLAN (§12 row, trigger row 1) | |
| FAM-D (ruling-10 D) | ruling | — | doc | n/a | §12.3 is a decision of this note (trigger "S2b (taken)"), not an unlock | DOC | |

## PROBED-AND-HELD (summary; full lists in each critic file and verify.md)

- **Cites:** about 45 file:line cites checked by ready and all held, apart from the ones named above. These include
  formhash.c, g2_win_gen.c's PORTABLE-only art_begin (9/9), vany.c, vrun.c, finder.c PAIR/D1c, compose.c's
  measures_check, memfn.h's MF_SITE_ABI and mf_measure, ks_measures.c, ksgen.c, mfixtures.py:177, run_measures_tests.sh,
  and measure_sets §7.1/§7.4/§1.7.
- **Constructors:** exactly three positional `mf_measure` constructors. The new fields zero to UNSTATED, so the
  refusal holds. MF_SITE_ABI is pinned by no test, so "next free at landing" is safe. The `pcrec-meas-1` readers match
  §5's list exactly.
- **Goal 1:** `--list-measurements` today has one row, so "two rows at S2e" holds. No kit row reads a set key today
  (the only fd_value caller is templated), so Goal 1's every-stamp-`""` premise holds. S1229's anchor is as quoted.
- **Sabotage rows:** 15 of 17 (a)-(q) reach their check and stay green in the correct build: (a)-(i), (l), (m), (o),
  (p), (q). The exceptions are (j), see TWIN, and (n) as cited, see CHECKC. (k) is under HASH.
- **Estimator:** independently implemented from the text, it agrees with drill.py on all 14 table lines and
  reproduces j1_drill (5 lines) and coverage_drill (12 lines). Every integer primitive is exact: rhafz, isqrt_rn, the
  lower median at L 7, the FRG nearest-rank index, the gate. One outlier anywhere passes; two refuse. Bimodal false
  positives are 0-3.5 % across s 0.3-1 %. Clean rows are never refused at the 3 % gate with s 0.5 %. **MEAS-7 FIXED:**
  no-drift refusal is 0/4000 at three s levels. **MEAS-2 and MEAS-3 FIXED:** value ≤ 0 fails, and delta rows never
  refuse their group. K_TRIM 1.7231, sqrt(1+π/14) 1.1065 and t_5 x 1.107 = 2.92 recompute.
- **Pool:** 7700X CPU 7 L2 1 MiB, L3 32 MiB: the 16 MiB pool is in L3 and beyond L2, as stated.
- **Rulings:** D188 base text holds (3 facts, 2 clauses). D188 add. 1's core holds in §2.7. DEFAULTS (B) holds
  against D166 item 1, D166 add. 2 Q-MS-1 (grid1 and grid3 are both `scratch`, so no second OFFICIAL set exists) and
  D162 ruling 1. R-35 (a)/(b)/Concurrency/sabotage ids hold 4/4. D157 holds (noise_state/noise_e6 are facts). D77
  holds on 7 deferrals. D176 Q1 (walk unit) and the Q3 step-0 census hold. D186 add. 2 (fresh id, no (?i)x/1234
  special rule) holds. The §7.1 seam holds (b)/(c) rejected and the slot as (d).
- **Slots:** 9 of the slots rev 1 creates or moves have one home each (MF_SITE_ABI, format/domain, KsMeasRow+ksgen,
  card rows, twin, noise states per layer, z, census0, the recompute). The exceptions are CELLS-1/3 and SMP20.
- **Other:** the shadow rule refuses a re-used zen4-grid3@1 id with other noise. The test levers skip `cells`, and
  their line buffers fit format-2 rows.

## By-id completeness

fixind-1..12, READY-1..11, meas-1..8 and ruling-1..10 (with ruling-7 i-iv, ruling-9 a-b and ruling-10 A-D) all
appear in the table above. verify.md items 1-17 cover every CONFIRMED finding that changes a design. The DOC-only
text findings (fixind-11, fixind-12, READY-11, ruling-6, FAM-D) are marked not verified.

## Recommendation (launcher decides)

- **Rev 1.1, scoped.** CELLS-1/2/3, CHECKC, HASH, TWIN, PLACE, DRIFT, Z, FLOOR, CENSUS, GOAL2, TARGET and J1-WIN
  touch §2.3-§3.8, §6 and §9 S2c/S2d/S2e. KSGEN, BOUND and MFMEAS are S2a text. The DOC rows ride along.
- **S2a and S2b may start once their text fixes land.** S2a: KSGEN, BOUND, MFMEAS, ANCHORS. S2b: SMP20, LOCK. Neither
  depends on the cells/estimator rework.
- **Main rulings needed:** EMBED (Goal 1 vs Goal 3 size), POLICY (D176 Q3 cost/policy split), R35 (the drops), and
  the DEFAULTS (B) record (freeze note).
- **The re-check after rev 1.1:** a single readiness critic plus a single measurement critic on the reworked
  §3.2-§3.8, not a full round. The S2c dry-run's walk vs walk#b placement probe (PLACE) is the measurement that
  decides between the noise and bias readings. It is a light dry run, not a timing window.
- **D27 spec-first author for S2a:** still DEFERRED to S2a's build brief (r4 ruling); this round adds no reason to
  revisit.

## Lessons for the guide (proposed; see .coord/process.md)

1. **A fix that MOVES data into an existing home is checked against that home's reader population, not only its
   columns.** SLOT-4's check C fix and CONTRACT-1's directory fix each held alone, and together they left the new
   check with population zero (CHECKC). Proposed lens-table text for fix-induced: "for every pair of fixes that both
   touch one check or one directory, recompute the check's population at the build tree".
2. **A "built objects differ" assertion is vacuous when the two objects come from differently named sources.** The
   file name is in STT_FILE. Assert on the linked addresses or `.text`. A one-line lesson for critics.md.

## Rulings (kit manager, 2026-11-06)

**Verdict: NOT READY as a whole.** S2a and S2b become READY once rev 1.1's text fixes for them land. S2c-S2e need rev 1.1, then a 2-critic re-check (readiness + measurement). S2g stays HELD for [XARCH-DEV].

Every PROPOSED FIX-NOW and DOC disposition is ACCEPTED as written. The rest:
- **FREEZE NOTE (DEFAULTS (B) has no record): CORRECT.** Main ruled (B) by message only (its 74f453e9a filed K138 and [KIT-POLICY-TABLE], not the ruling). The kit asks main to record it in R-35, the ruling's natural home. Rev 1.1 cites that record once it exists.
- **EMBED goes to MAIN.** The kit recommends that the embed omit the `cells` section (measures.md's embed rule may omit it for size). The committed set.tsv carries the cells, so Goal 3's recompute runs off the committed file, and `--measures=FILE` shows them; libpcrec does not grow by about 77 KB of cells. Answer-free. Main rules, since the embed is pcrec's.
- **POLICY goes to MAIN.** The kit's reading: z, the gate default and MATERIAL are policy constants, not measured costs, so homing them in a policy table is not the "rows migrate into the sets" D176 Q3 meant. HORS_MIN is deleted by D176 Q2 and leaves the member list. MAX_SET is pcrec's fact and leaves the member list too. Rev 1.1 states this reading. Whether that reading of Frank's Q3 needs Frank is main's call.
- **R35: DOC.** Rev 1.1 lists every narrowing of R-35 explicitly as an amendment for main to acknowledge: derived noise dropped, `verify_cmp` scoped by the census, and S2g held, which moves D186 add. 2 C9's "SIMD-form cards join stage 2".
- **SIMD-READ: FIX-NOW (text), the interim stated.** Until [XARCH-DEV]'s build, `-fmemfn-simd` keeps today's `#if` arms unchanged; that is the INTERIM, not the end state. Row 1 departs on the generic (scalar) target only, and its SIMD-on arm is judged as today's arms are (no slower beyond noise). Rev 1.1 draws the consequences D188 add. 1 names: C9 under variants, and SIMD-off-by-default as a per-target question at [XARCH-DEV].
- **FAM-A/B/C: PLAN** as proposed, as §12 unlock rows with their triggers; main files any plan row. **FAM-D: DOC.**

**Process changes ACCEPTED** (skill + critics.md):
- (1) The freeze step locates each in-force ruling's RECORD (file:line at the freeze); a ruling with no record becomes a freeze note.
- (2) Fix-induced: for every pair of fixes that touch one check or one directory, recompute the check's population at the build tree.
- (3) A "built objects differ" assertion is vacuous across differently named sources (STT_FILE); assert on linked addresses or `.text`.
