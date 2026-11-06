# Review 2026-11-06 r4 — span_cards rev 0 (design, first round: span_pick stage 2)

**Subject.** docs/design/memfn/span_cards.md REVISION 0 at 6f93716f6 (branch lane/memfn-s2design, tip
2948ac356 at freeze and at hand-back). Parent: span_pick.md rev 5.2 and R-35 (both identical at the subject
and at main). Build tree: main fb22c62a6, review tree built there (`nice make -j2`, unlocked, rc 0). All
cited code is identical between the subject's base c03c2d711 and main fb22c62a6 (no cited-code drift).
Rulings frozen at 80341284e.

**FREEZE DRIFT (rulings).** main moved 80341284e -> 013af687c during the round. decisions.md gained
**D188** (Frank via the kit, 08:54): "per SIMD level a measurement set records (a) CPU has it (cpuid),
(b) the build compiled it, read off MEMFN_FORMS, a level missing from the stamp recorded absent and never
timed, (c) its cost only when both hold; a set never grants a level", **Home: span_cards.md rev 1**.
plan.md gained [ISL-PRICE] and [XARCH-DEV] (unrelated). No critic saw D188. It lands squarely on J6 (the
SIMD job) and on PREMISE-2/MEAS-1 (what code a fixture actually times): rev 1 must carry it (listed below
as DRIFT-1).

**Verdict (proposed): NOT READY — a rev 1 and a re-check.** No emitted-byte or answer-of-a-match
finding: the "stage 2 moves nothing" core holds (72 compiles, every `<PREFIX>_MEASURES` `""`; no consulting
row; MF_SITE_ABI reaches no text; the zero-init forcing argument for `noise_state` works; format 1 /
grid1's digest and sha untouched; the format-2 digest layout is unambiguous; no-shadowing holds for all
three id-reuse classes). The findings are in four places:
1. **The producer cannot render what it promises** (PREMISE-2/3/5): the one G2 window-site builder is
   SIMD-off by construction, vany is unrouted, vrun needs a RUN term, formhash cannot hash SIMD/PAIR/rc-*
   texts, and no existing deny forces the walk on a two-member stop.
2. **The estimator/gates are not an executable spec and would refuse good runs** (MEAS-1..10): the A/A
   arm is byte-identical to its base, the gate is ill-scaled and sign-blind, delta rows skip §7.4's NULL
   rule, an absolute walk floor refuses memchr in the unit group, the drift check false-refuses 25-57 % of
   clean groups, J1's rule files a spurious D186 unit change ~50 % of the time under no effect.
3. **Rulings and slots** (PREMISE-4/SLOT-3/CONTRACT-4, SLOT-1/2/4/11, PREMISE-1/SLOT-5): the DEFAULTS
   (B) recommendation contradicts R-35 and the design's own Goal 1; raw.tsv/cells.tsv duplicate the spec's
   `cells` section; the producer's home is measure_sets §7.1's rejected alternative, cited through a
   misquote of D176 Q3; check C would read green with nothing resolved; the vrun cards are row-1 keys at
   SIMD-on (or row 1 must be stated scalar-only).
4. **Readers missing from the package** (CONTRACT-1/3/5/9, COST-6): finder_check.py's format-1 digest
   over the format-2 interim, ksgen.c's positional pre-parse, the S1229 anchor, the mfixtures `format 2`
   refusal row, measure_sets.md:490-494, and an existing loader gap (a value past MF_MEASURE_MAX is
   accepted, then every compile is an "internal error") the design copies for noise.

## Lenses as run
| lens | model | question | why chosen |
|---|---|---|---|
| premise | opus | test every assumption and every "the existing X does Y" at the build tree | new mechanisms (cards, producer, noise field, format 2) resting on many existing-code claims |
| measurement (+ simulate drills) | opus | do values/noise/gates mean what the design says (regime, control, regeneration); recompute every quoted number | the subject IS a measured quantity and its estimator; a rule (gates, J1 decision) to drill on constructed outcomes |
| slot tracing + ruling check + goals (+ the two standing questions) | opus | every new slot to its table; every relied-on ruling and its consequences; goals ranked/served; sibling of a family; general form + unlocks | new tables/fields/constants/dirs; many rulings (R-35, D77, D149, D157, D166, D176, D186) |
| contract + seam round trip | opus | every caller-observable contract moved (format 2, digest, mf_measure, fill, spec hunks), its readers by grep, edge probes; what crosses the pcrec->kit seam | a spec-level format and an MF abi seam event |
| cost and overlap | sonnet | cost vs benefit per unit, D77 triggers, D153/in-flight overlap, separability, can each sabotage row go red | a six-unit build proposal with a timing window |
| verifier | opus | re-check every CONFIRMED design-changing finding | skill §6 (opus: several drills needed a faithfulness judgment) |
Owner-criteria lens not run separately (no owner benefit criteria stated for stage 2 beyond R-35, folded
into the ruling check). No soundness lens (no answer-identity-by-proof claim beyond "no reader", probed by
premise/contract).

## Which lens caught what
premise: the producer gaps (2, 3, 5), vrun at SIMD-on (1), DEFAULTS vs §3.6 abi rule (4), kit-kernels@1
(7), cite gaps. measurement: every estimator/gate finding (MEAS-1..14). slot: `cells` section (1), §7.1
home + D176 misquote (2), check C dims (4), sunset harness lever (6), policy-constant home (7), census0 vs
smp20 (8), sabotage ids (11). contract: finder_check over the interim (1), harness paths (2), ksgen (3),
S1229 (4), the MF_MEASURE_MAX internal error (5), derived-noise unenforced (6), noise-value witness (8).
cost: derived-noise engine ahead of need (1), S2b/S2c order (2), vany cards (3), abi-number race (4),
sabotage rows (8)/(10) cannot go red (5). Coordinator: R-35's sabotage-id and DEFAULTS lines (also found by
slot/premise), D188 freeze drift.

## Findings (consolidated; PROPOSED dispositions)
Dispositions: FIX-NOW = rev 1 text/design before the build go; PLAN = a filed row; DOC = a text fix,
rides rev 1; NOTED = no action.

| id | lens(es) | sev | verify | finding | proposed | reason |
|---|---|---|---|---|---|---|
| DRIFT-1 | coordinator | design | n/a (ruling text) | D188 (landed mid-round, homed in span_cards rev 1): J6 must record per level cpuid presence + MEMFN_FORMS presence of the BUILT fixture, never time a fallen-through level, and the set never grants a level | FIX-NOW | an owner ruling homed in this doc; J6/§2.3/§2.5 do not have it |
| PREMISE-1 + SLOT-5 | premise, slot | design | PARTLY (fact HOLDS: `(?i)x/1234 -fmemfn-simd` -> MEMFN_FORMS `vrun@w32+w16`; the key move is not forced: span_pick §The pick 6 lets SIMD forms ride as rungs) | §2.5 "row 1's SIMD-on arm needs no SIMD card" is false on row 1's own witness; J6 is not "droppable alone" while row 1 claims a SIMD-on arm | FIX-NOW | state one: vrun keys are row-1 keys (J2/J3, not J6), or row 1 prices the scalar layer only with SIMD forms as rungs |
| PREMISE-2 | premise | design | HOLDS | g2_win_gen.c passes MF_P_PORTABLE_ONLY at every mf_art_begin; vany is NOT ROUTED (vany.c:16); vrun needs ONE RUN term with REACH >= VW+T (vrun.c:19-25), not "one stop set at offset 0"; SIMD rows live in g2_simd_gen.c / g2_any_gen.c | FIX-NOW | the "ONE window-site builder" producer cannot render the SIMD arms; name the families/site shapes and a RUN-term subject regime for vrun |
| PREMISE-3 | premise | design | HOLDS | mf_form_hash is hard-wired portable + mf_emit (formhash.c:291); kit-kernels.tsv says vany deps are OWED (renders outside any site); PAIR holds only for SF_ASKER_PAIR askers; rc-* are run-verify compare rows | FIX-NOW | S2c needs a new hashing entry shape (policy, entry, site kind per id), not 12 canon() entries; re-cost S2c |
| PREMISE-5 | premise | design | HOLDS | no existing deny forces the R7w walk on a two-member {X,x} stop (finder.c:282-289 PAIR "No deny"; options.def) | FIX-NOW | `find_hit.walk.*.alt` and walk-vs-pair need a named test-only force (allowed: pcrec-flag-follows-caller-effect); "force rows" names nothing |
| PREMISE-4 + SLOT-3 + CONTRACT-4 | premise, slot, contract (+ coordinator) | design | HOLDS (R-35, Goal 1, S1229 anchor); PARTLY (§3.6's "every default change is an abi event" rests on consulting artifacts, none at stage 2) | §8.3 (B) "No ruling is amended" is false: R-35 item 1 "leaves DEFAULTS unchanged", item 3 "row 1 flips ... its own landing verdict"; under (B) `--list-measurements` changes TWO rows (grid1's `default_for`), failing Goal 1's own measure; S1229's SAB_BEFORE anchor (`{ "idk", "zen4-grid1", 1u }`) disappears; measure_sets §3.6 needs a hunk | FIX-NOW (main rules) | either reading amends something (A: D166 add. 2's literal / §5¶6; B: R-35, span_pick rev3 C6, §3.6); present it so, for main (and Frank if (A)) |
| PREMISE-7 | premise | design | HOLDS | kit-kernels@1 already declares vany cards (beta/f/saving/xover/gstar, UNMEASURED); a set has ONE method header | FIX-NOW (text) | say which card governs vany from stage 2 and what kit-kernels.tsv records (append-only) |
| PREMISE-8 + CONTRACT-2 + SLOT-6 | premise, contract, slot | design | HOLDS | "noise reaches the kit only from a set whose digest covers it" is false on the two test paths §4.2 says "follow the same rule": cli/main.c's harness reader copies values_digest verbatim, reads no `format`, and its own comment retires it "until M0's loader" (M0 is on main); arm_fixtures fd_load_set has no header/digest/status (hands a null row's value) | FIX-NOW | least form: test levers hand UNMEASURED always (or retire the harness lever per its "until"); restate the claim "on the shipped loader path" |
| MEAS-1 | meas | design | HOLDS (two-dir gcc: byte-identical binaries; measure.sh:71-72 cmp-asserts identical sources) | the A/A "separate compile and link" is the same binary, so the floor holds no code-placement term; sabotage (9) detectable only by path | FIX-NOW | perturb the A/A arm (pad/align/link order, stated) or relabel aa as rerun noise and drop the placement claim; D188's fall-through point is the same class |
| MEAS-2 | meas | design | HOLDS | gate `noise_e6/value_e6 <= gate_e6` mixes a fraction with an e6 scale: read literally every case passes (incl. 301 %); value 0 divides by zero; negative values pass/fail by reading | FIX-NOW | `noise_e6 x 10^6 <= gate_e6 x |value_e6|` plus a near-zero rule (MEAS-3) |
| MEAS-3 | meas | design | HOLDS | verify_cmp (arm - null) and enter (pass - fail) are delta rows; measure_sets §7.4's NULL rule (|Δ| <= max(floor, FRG x base) or sign disagreement) is never applied; a sign-unstable or negative cost is priced, or one row refuses the group | FIX-NOW | delta rows take §7.4 (NULL, never refusing the group); the relative gate applies to cost rows |
| MEAS-4 | meas | design | HOLDS (mechanism, arithmetic); box size SUSPECTED | aa is absolute (the walk's floor scaled); in the unit group (half gate 1.5 %) memchr (r~0.06) at grid1's 0.173 % floor is 2.9 %, 1.67 % even at 0.10 % -> the unit group, hence the whole run, is REFUSED because memchr is fast | FIX-NOW | per-arm A/A as a fraction (as §7.3 says), unit group = walk + walk#b only |
| MEAS-5 | meas | maintenance | PARTLY ((a) slope-of-ns/B-over-length HOLDS; the per-hit half REFUTED: the text says "time" for find_hit; (b)-(e) HOLD) | §3.4 is not executable: find_byte's slope is of a per-byte figure (ns/B^2); the miss-only point is another job's launch sequence; the A/A arm per group unnamed (J1/J5/J6); sp's unit/normalization unstated; integer order of operations unstated (one-unit disagreement on 4,793 of 20,000 inputs) | FIX-NOW | Goal 3's EXACT recompute needs a literal integer recipe (as measure_sets §1.7 does for rhafz); consider per-launch normalization to the launch's own unit (also MEAS-11, SLOT-9) |
| MEAS-6 | meas | design | HOLDS | find_hit spans 4 groups (3 densities + J2's miss point); g=32 carries 74 % of the LS information, at 31,250 ppm vs row 1's masses 1,097 / 4,154 ppm; A/A propagation 38.4 d (independent) vs the design's 1 d | FIX-NOW | per-density rows or a density pinned to row 1's mass range; A/A taken on the value (slope of A#b minus slope of A) |
| MEAS-7 | meas | design | HOLDS (model faithful, rates reproduce) | the in-group walk drift check compares a difference of medians (between-launch variance) to a within-launch floor: false REFUSE 0.245-0.572 per clean group, so FULL is unreachable over ~40 groups; undefined for J1/J4/J5 (no walk arm) and wrong for J3 (walk on a hit subject) | FIX-NOW | one miss-only walk control cell per JOB, threshold from the between-launch spread, and a stated drift size that matters |
| MEAS-8 | meas | design | HOLDS (faithful) | J1's (a)/(b)/(c) rule under five truly equal widths picks (b) "file a D186 unit change" 50-55 %: best-of-5 selection, a same-binary floor, 32 comparisons, no multiplicity control | FIX-NOW | a pre-registered margin on the paired per-launch difference and a family rule; (b) only on a stated majority of cells for one w |
| MEAS-9 | meas | doc/design | HOLDS (as a derivation gap) | z=2's "2.3 %" assumes a known sigma; noise is a 5-launch s.d. (4 dof): 0.62 % (iid launches, stored median) or 5.8 % (new-run draw); P(s < sigma/2) = 9 % | FIX-NOW (text) | state which error the band covers; t_{L-1}-adjusted figure or z from its quantile; COVER_Z_E3's derivation is its whole justification |
| MEAS-10 | meas | design | HOLDS (under MEAS-2's scaled gate) | one +8 % launch out of 5 (median unmoved) gives noise 3.58 % > 3 % -> group refused; robust centre, non-robust spread | FIX-NOW | MAD-based spread, or the rerun rule REPLACES an outlier launch |
| MEAS-12 | meas | design | SUSPECTED (not verified) | "streamed-fresh" pins no buffer-pool footprint (L2 1 MiB / L3 32 MiB / DRAM); memchr/SIMD ratios move with cache level, the walk does not | FIX-NOW (text) | pin the pool size on the card's `subject` (cheap); confirm on the box later |
| MEAS-11 + SLOT-9 | meas, slot | speed (safe) | SUSPECTED | launch-wide shifts enter every row's sp and span_pick's band sums cards as independent, widening bands for shifts that cancel; the unit's own noise never enters a measured row | NOTED -> folds into MEAS-5's per-launch normalization | resolved if rows are per-launch ratios to the launch's unit |
| MEAS-13 + CONTRACT-6 + COST-1 + SLOT-10 | meas, contract, cost, slot | design | HOLDS (no derived-value evaluator exists in C or python; the loader checks no derived value; measures.md §3.2¶2 forbids reader recompute) | §4.3's derived-noise table would be a NEW recompute engine (spec + C + ks_ref.py + fixtures + sabotage (6)) with population zero in zen4-grid3 and no reader, while §4.6 defers a field on the same D77 ground; cross-lin ignores fit covariance; unenforced on FILE sets anyway | FIX-NOW | derived rows carry `-` (UNMEASURED) until the first producer of a format-2 derived row (the interp-log2 rule, generalized); or "the producer's rule, unchecked at load"; drop sabotage (6). R-35 "Not asked" leaves the shape to the kit |
| MEAS-14 | meas | doc | HOLDS (J3, window figures); PARTLY (+2/3) | J3 is 42 points by §2.5's keys, not 54; window quoted as ~35-45 / ~35 / ~32-45 / ~45; "+40 %" is every group rerun (a ceiling) | DOC | one window figure for the request to Frank |
| SLOT-1 | slot | design | HOLDS | the spec already has the `cells` section (measures.md §2¶2, §2.2; ks_measures.c:44) and measure_sets §8 says "The `raw/` directory is gone" — raw.tsv (two copies) and cells.tsv re-create it with their own sha/writer/check | FIX-NOW | use `cells` (recomputed by the existing checker; an embed rule may omit it for size) or argue the force that forbids it |
| SLOT-2 | slot | design | HOLDS (the quoted phrase is absent from decisions.md and plan.md at 80341284e) | memfn/measure/ (C driver + python estimator/gates/interim writer, kit-owned) is measure_sets §7.1's REJECTED (b)/(c); §3.1 cites D176 Q3 as "the kit contributes its method cards to that script", which D176 does not say ("a canned, self-contained pcrec script") | FIX-NOW | engage §7.1: split along its seam (kit = probes + card rows; estimator/gates/writer = the format's spec, so M3 implements the same text) or argue why a stage-2 slot may differ; fix the quote |
| SLOT-4 | slot (+ cost) | check | HOLDS | finder_check.py check C resolves deps only when the first dim is `form` (:395-399): find_byte (`method`), find_hit, enter (`kind;entry`) are skipped silently, so S2c's witness reads green with nothing resolved; keys say `memchr`, deps/canon say `libc`; enter's dep names no key dim | FIX-NOW | one dim name for the kit's text id across @1 and @3 (`form`), key token = canon id, check C guard keyed on it |
| SLOT-7 | slot | maintenance | HOLDS (wording); arguable | COVER_Z_E3 goes to plan_cost.def while D176/[MEASURE-SET] RULED say "plan_cost.def rows migrate into the sets" with no cost/policy split; gate_e6 (a noise policy) lives in kit-grid.tsv: two homes for noise policy | PLAN (row 1's E2 unification) + DOC now | name a kit POLICY table home (MATERIAL, MAX_SET, HORS_MIN, z, gate default) when row 1 writes z; rev 1 stops narrowing the ruling silently |
| SLOT-8 | slot | maintenance | SUSPECTED | census0.py "generalizes" smp20.py while smp20.py stays: two kit-side python pricers of one formula | FIX-NOW (text) | census0 replaces smp20 (smp20.out its golden) |
| SLOT-11 | slot (+ coordinator) | doc/process | HOLDS | R-35: "Sabotage ids: the kit takes its own from the top of the free range"; the design says "ids: the manager's" | DOC | follow R-35 |
| CONTRACT-1 | contract | maintenance | HOLDS | finder_check.py digests EVERY .tsv in memfn/data/sets with the format-1 rule; §3.8 puts the format-2 interim there; §5 lists it UNCHANGED | FIX-NOW | format-dispatching digest (or keep the interim elsewhere) + a sabotage row |
| CONTRACT-3 | contract | maintenance | HOLDS | scripts/ksgen.c writes KsMeasRow positionally into measures_table.inc; meas_store_check.c compares pre vs fresh; KsMeasRow.noise_e6 would be 0 (pre) vs EMPTY (fresh); measures_table.inc (grid1 too) regenerates | FIX-NOW (text) | list ksgen.c and the regenerated .inc in §4.5/§8.2; also which KsDigest role the kind row names |
| CONTRACT-5 | contract | answer-adjacent (caller-visible) | HOLDS (re-run: value 2e15, digest fixed, 3 patterns rc 1 "internal error: the memfn kit refused ..."; control rc 0) | a loader-accepted set with value_e6 > MF_MEASURE_MAX makes every compile an internal error TODAY; the design copies the shape for noise (bound only kit-side, no §7 refusal row) | FIX-NOW (noise half, in S2a) + PLAN (the existing value half: a K-row / known_issues) | the loader refuses |value| and noise past the kit's bound, a §7 row each |
| CONTRACT-7 | contract | doc | not verified (text) | format-1 decoded view / KsMeasRow.noise_e6 on format 1 unspecified; grid1's decoded view may move by implementer choice | DOC | state it (format 1: no parsed-noise line) |
| CONTRACT-8 | contract | design | SUSPECTED | no stage-2 witness checks the noise VALUE handed to the kit (MFMEAS counts MEASURED rows; sabotages (3)/(5) are state errors); MFMEAS prints `%p` (not text-portable) | FIX-NOW (text) | a text digest of handed (key, state, noise) triples vs ks_ref.py's, and a column-swap sabotage (the S983 class) |
| CONTRACT-9 + COST-6 | contract, cost | doc/maintenance | HOLDS | unlisted readers: measure_sets.md:490-494 "the digest excludes noise_e6"; mfixtures.py:177's refused `format 2` row (-> `3`); the `--list-measurements` readers are S1228/S1229/S1237/S1241/S1245/S1246 anchors and run_measures_tests.sh's DEFAULTS check, not "a count that grows by one" (no count pin exists); memfn/measure/CLAUDE.md under the 12 KB gate | DOC | add to §4.4/§5/§8.2 |
| COST-2 | cost | design | HOLDS | S2b writes cells.tsv into memfn/measure/, which S2c creates | DOC | name S2b's home or move the write to S2c |
| COST-3 | cost | design | NOTED (ruled) | J6's vany cards (unrouted forms, 4 form ids) have no reader but a C9 row not yet designed; D186 add. 2 C9 rules SIMD cards into stage 2 | NOTED, for main | C9 is Frank's; D188 now also scopes J6; main may ask whether "SIMD cards" covers unrouted vany |
| COST-4 | cost | maintenance | PARTLY (alt_normal_form names a FUTURE MF_SITE_ABI crossing, not a scheduled 24) | the design hard-codes MF_SITE_ABI 23 -> 24 and "PCREC_ARTIFACT_ABI stays 95" while two byte-moving lanes land on main; measure_sets §3.6's house form is "the next number at landing" | FIX-NOW (text) | "next free MF_SITE_ABI at landing"; each unit names its base commit and re-baselines after a lander; `enter` cards stale on the next lander's entry-text change (freeze after, or record) |
| COST-5 | cost | check | HOLDS ((8) reason refined by the verifier) | sabotage (8): smp20's band-0 argmin never reads the incumbent, so the wrong-field plant stays green unless the control diffs the incumbent column; (10): check C never sees rendered cell text (and skips `method` dims) | FIX-NOW (text) | (8) diff the incumbent column; (10) a cell-text-hash vs dep-hash check in G2 `--cards`; also (3) needs a non-`-` format-1 fixture and the PCREC_CAND_TRACE build, (4) needs a named UNSTATED test |
| COST-7 | cost | — | — | separability: S2a reverts alone only before S2e; S2c-S2e order-locked | NOTED | |
| PREMISE-6 | premise | doc | HOLDS (text) | span_pick.md:266-267 names the successor method `kit-grid@2`; rev 0's decision makes it stale and §10 does not list the amendment | DOC | add a span_pick [s2] amendment line |
| PREMISE-9 + SLOT-12 + CONTRACT-9 | premise, slot, contract | doc | HOLDS (three greps agree: three constructors) | §8.2 "the four constructors" vs §4.1's three; §4.3 "§8.2's recompute" (is §3.8 item 4); kit-grid.tsv's header hard-codes grid1's unit sentence; "keeps 7 rounds" relative to grid2's slot | DOC | |
| PREMISE-10 | premise | doc | HOLDS | "3,381 of 3,536" is not in smp20.out (only span_pick.md:306-307); §7's control has no committed P-blind line to reproduce | DOC (+ FIX-NOW with COST-5 (8)) | cite span_pick or commit the count |
| PREMISE-11 | premise | doc | not verified (cite reading) | "28 of 32 F1 reruns" is the trigger's share among reruns, not of groups; it does not support +40 % | DOC | label stands (UNMEASURED); drop the cite as support |
| PREMISE-12 | premise | doc | not verified (source denied to critics) | "R-33 job 240: 5,492 compiles in 14 s" unfindable in the readable tree | DOC | cite the record |
| PREMISE-13 | premise | doc | not verified | B-pair writes `<h>wa = 128, <h>wb = 128`; the J1 generator's exact assertion holds for fn-pair only | DOC | spell the declaration with its handle prefix |

## PROBED-AND-HELD (summary; full lists in each critic file)
- Stage 2 moves no emitted byte as designed: 72 compiles (18 patterns x default, -fmemfn-simd, --engine=vm,
  --measures=zen4-grid1) all `<PREFIX>_MEASURES ""`; `art->consulted` never assigned in memfn/src;
  MF_SITE_ABI's only src use is `s->abi =` (memfn_sites.c:406); default vs --measures=zen4-grid1
  byte-identical but the include line.
- `kit-grid@2` TAKEN (kit-grid.tsv header, r17b_prime.md:2040,:2059); canon() walk/libc only; vrun/vany
  facts, levels, denies, vrun body = fn-pair = ofs_pair_text; exactly three mf_measure constructors, and
  zero-init of appended fields refuses unedited ones; ks_measures.c:305 format refusal; Makefile:330 embeds
  set.tsv only; grid1 digest/sha/DEFAULTS/DEFAULTS.log as quoted; every §5 digest reader at its line.
- Format 1 hole is real (a grid1@1 FILE with invented noise loads with the committed digest) and the
  format-1 rule closes it on the shipped path; format 2 refused today; no-shadowing holds for format-2
  claiming grid1@1, format-1 claiming grid3@1, and format-1 grid1@1 + noise.
- Digest byte layout unambiguous; measured-0 vs `-` digest apart; match_api NO hunk holds.
- Seam round trip: mf_measure carries strings, integers and an enum; facts only (D157).
- Quoted numbers: Phi(-1/-2/-2.58), Bonferroni z, §3.7 minutes (282 points, 31.3 min), J1/J2/J6 point
  counts; value_e6 dimensionally coherent for ratio and walkbytes; absolute noise is what span_pick's band
  needs; §4.3's propagation rules correct first-order for independent inputs; isqrt_rn exact.
- Step-0 census quotes (SRS §7 row 0/1, §8 item 2; pricesurvey_report :5-7,:251,:275,:366,:392; D176 Q3 at
  decisions.md:9920) all match. [PAIR-LOOKAHEAD-TIME] charter, abi 95, PAIR_LOOKAHEAD comment as quoted.
- D77 deferrals (memchr-back, Horspool) consistent; D149 labels on gate_e6, z, +40 %, 5 launches present.
- Sabotage rows (1),(2),(5),(7),(11),(12),(14) go red by the design text.

## By-id completeness
premise 1-13: all dispositioned. meas 1-14: all. slot 1-12 (+ rulings/goals/sibling/unlocks sections): all.
contract 1-9: all. cost 1-7: all. DRIFT-1 (coordinator).

## Standing questions (slot lens)
- Sibling of a family: raw cells (`cells` / raw.tsv / cells.tsv -> one, SLOT-1); measure harness dirs
  (§7.1 measure/, kit_proof/measure, memfn/tests/g2, grid1's harness, now memfn/measure/: SLOT-2); policy
  constants (gate_e6 / z / MATERIAL / HORS_MIN: SLOT-7); pricers (smp20 / census0: SLOT-8); the format
  version + digest domain is the KsDigest roles family's own extension (held); the noise-state enum vs the
  row `status` column (held: the seam needs UNSTATED).
- General form + unlocks: (1) a measured row is a DERIVATION over `cells` (`launch-median-slope`,
  `arm-minus-null` estimator rows, inputs = cell ids, recomputed by the existing checker): unlocks Goal 3
  for free and lets M3's install tool implement a spec, not a python script; trigger S2a. (2) one kit
  noise-POLICY table: unlocks row 1's E2 unification; trigger row 1. (3) the census as THE priced-forecast
  tool (census0 subsumes smp20 and every later row's mover forecast); trigger S2b.

## Recommendation (launcher decides)
A D27 spec-first test author for S2a's format-2 contract (parse, spellings, refusals, digest) from
measures.md's rev-1 hunks alone: ks_ref.py is already an independent twin for the digest, so the author's
value is in the refusal table and the format-1/format-2 noise rule. Moderate value; optional.

## Lessons for the guide (proposed; see .coord/process.md)
- A design that names a measurement ESTIMATOR should be drilled like a selection rule: the measurement
  lens's constructed-outcome drills (clean / outlier / bimodal / A/A > spread / equal-effect sweep) found
  every gate defect in this round (MEAS-2,4,7,8,10). Add to the measurement lens's question.
- "Freeze the rulings" caught D188 only at hand-back; a ruling HOMED IN THE SUBJECT that lands mid-round
  should trigger a fresh critic on its section, not just a drift line.

## Rulings (kit manager, 2026-11-06)

**Verdict: NOT READY.** span_cards.md rev 1 (a fresh design lane briefed from this review), then a short re-check (fix-induced + readiness) before any build.

Every PROPOSED disposition is ACCEPTED as written, except these:
- **PREMISE-4 + SLOT-3 + CONTRACT-4 (DEFAULTS) goes to MAIN.** My recommendation is (B), flip DEFAULTS at S2e, with rev 1 stating plainly what it amends: R-35 item 1 (main's text), span_pick rev3 C6 (the kit's design; amended in rev 1), and measure_sets §3.6 (a spec hunk). It also restates Goal 1's measure, since two `default_for` rows change. Why: both readings move zero bytes at stage 2 (no row consults a set), so this is an answer-free choice. (B) amends only main's and the kit's text, while (A) would amend Frank's D166 add. 2 literal and §5¶6. If main prefers (A), it goes to Frank. Rev 1 carries whichever main rules, plus the S1229 anchor re-aim.
- **MEAS-13 + CONTRACT-6 + COST-1 + SLOT-10: ACCEPTED in the strong form.** Derived rows carry `-` (UNMEASURED) noise until the first format-2 derived row has a producer AND a reader (D77). No derived-noise engine, no §3.2 column; sabotage (6) dropped. The general form (a measured row as a derivation over `cells`) is filed under SLOT-1's resolution, not built.
- **SLOT-1 + SLOT-2: FIX-NOW, rev 1 engages measure_sets §7.1.** Raw medians go in the spec's existing `cells` section (no raw.tsv/cells.tsv twin). The producer splits along §7.1's seam: the kit contributes probes and card rows, while the estimator, gates and writer are the format's spec text that M3's install tool implements. The D176 misquote is fixed.
- **CONTRACT-5: noise half FIX-NOW in S2a. The existing value half is a FINDING ABOUT PCREC**: the loader accepts value_e6 > MF_MEASURE_MAX, and then every compile is an internal error. It goes to main for known_issues by responses notice. The kit will not fix pcrec's loader.
- **COST-3 (vany cards): rev 1 drops J6's vany cards** (unrouted forms, no reader; D77). J6 keeps vrun per D188's three facts. This is NOTED for main as C9-scope context.
- **SLOT-7: PLAN** (one kit noise-policy table at row 1) + DOC now, as proposed. The plan row is filed by main from this review.
- **D27 spec-first author for S2a: DEFERRED** to S2a's build brief; decided there.
- **DRIFT-1 (D188): FIX-NOW.** Rev 1's J6 records per level: CPU has it, build compiled it (MEMFN_FORMS of the BUILT fixture), cost only when both hold. MEAS-1's A/A placement point is the same class and is fixed with it.

**Process changes: both ACCEPTED** (skill + critics.md, same commit):
- (1) Re-diff the frozen rulings at EACH critic return. A ruling HOMED in the subject that lands mid-round gets a fresh critic on its section.
- (2) The measurement lens drills a named ESTIMATOR on constructed outcomes (clean, one outlier, bimodal, A/A above spread, an equal-effect sweep), as the simulate lens drills a selection rule.
