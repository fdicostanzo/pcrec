# span_cards — span_pick STAGE 2: the cards, their producer, the noise channel (design, rev 1.3)

**Status: PROPOSED, rev 1.3 (lane s2c, 2026-11-06: the readiness review's text fixes, §R1.3; lane s2cfix, 2026-11-06: the
code review r9's FIX-NOW/DOC text, §R1.3's second table, marked `[rev1.3 r9-<id>]`), over rev 1.2 (lane
s2rev12, 2026-11-06), rev 1.1 (lane s2rev11), rev 1 (lane s2rev1) and
rev 0 (lane s2design). DESIGN ONLY: no code, no make, no timing, no box job. The design of record for span_pick
stage 2** (`span_pick.md` rev 5.2 §Staging "Stage 2", §Cost cards, §The pick; kit request R-35,
`memfn/docs/requests.md` "R-35"; Frank's GO 2026-11-06, plan 80341284e). **Rev 1.2** applies the second
RE-CHECK `docs/dev/reviews/2026-11-06-r6-memfn-span-cards-recheck2.md` as ruled by the kit manager (its "##
Rulings" section: every FIX-NOW and DOC disposition, with the decisions READY-1, READY-6 + MEAS-7, READY-8,
MEAS-4, MEAS-6, MEAS-1 and the movers.py PLAN). Text changed in rev 1.2 is marked `[rev1.2 <id>]`; it
replaces any `[rev1.1]`, `[rev1]` or unmarked text it contradicts. **Rev 1.2 changes nothing S2a builds**
(the format-2 grammar, the digest, the seam fields, the loader's refusals stay rev 1.1's §4/§5, which S2a is
building now); §R1.2's "How rev 1.2 stays clear of S2a" says how each decision avoids it. **Read §R1.2 first**, then §R1.1, §R1,
§0. Rev 1.1 applied the RE-CHECK
`docs/dev/reviews/2026-11-06-r5-memfn-span-cards-recheck.md` as ruled by the kit manager (its "## Rulings"
section) and main's R-35 rulings (c) DEFAULTS, (d) EMBED, (e) POLICY (`memfn/docs/requests.md` R-35, "Ruled
later", main 78e7da573). Rev 1 applied review `2026-11-06-r4-memfn-span-cards.md`, main's DEFAULTS ruling (B),
D188 and D188 add. 1. Text changed in rev 1.1 is marked `[rev1.1 <id>]`; `[rev1 <id>]` and unmarked text
stand unless a later mark replaces them. Cites are to the kit branch at the r6 review's build tree (main
6f1b40f75 + the kit branch; the r6 review found every code/data cite of S2c-S2e identical to the r5 tree's)
unless a commit is named; spec files by section number. Every figure the note quotes comes from a committed
drill under `span_cards/` that prints its inputs (§R1.2, last paragraph).

## R1.3 What revision 1.3 changed, by readiness finding (review 2026-11-06 r7)

Review `docs/dev/reviews/2026-11-06-r7-memfn-span-cards-ready.md` (one readiness critic on the rev 1.2 diff)
found S2c, S2d and S2e READY WITH TEXT FIXES; the kit manager's ruling ("## Rulings") ACCEPTED every finding
as a text fix, applied here by the S2c build lane in its first commit, and NOTED READY-7 (stated, not
removed). Text changed is marked `[rev1.3 <id>]`. No design decision moves; nothing S2a builds changes.

| id | ruled | answered in |
|---|---|---|
| READY-1 the strip's output layout and Makefile hook unstated | text fix | §3.8 "Who strips" (stripped copies at `$(BUILD_DIR)/gen/meas/<id>/<rev>/set.tsv`, a `KS_TEXTSRCS_measures` row, the three wording readers); §8.2 built-in sets row |
| READY-2 the run record is written twice; J2p's file and the finalizer unnamed | text fix + an S2c dry-run line | §3.5 "The run record" (J1's write at its end into the window's working copy; J2p's `--ready` reads it; a `finalize` step, job J9, writes `jobs`, `plan`, `floor`, the transcript sha); §3.6 (b); §9 S2c witness |
| READY-3 the S2c row lists the withdrawn §2.2¶3 hunk | text fix | §9 S2c content |
| READY-4 contradictory separability sentences | text fix | §9 Separability |
| READY-5 three copies without a compare | text fix | §3.4 step 1 ((a) id fields vs columns, (c) base vs §2.4's family rule); §3.5 run record ((b) the header `run` sha and run id vs PROVENANCE.md vs the record); §9 S2e plants (x2)-(x4) |
| READY-6 the 0-cells assertion has no mechanism | text fix | §3.8 (the runner counts the `.pre` decoded view's `cell` lines) |
| READY-7 the cost-row PARTIAL path is unreachable | NOTED | §3.5 Outcomes (stated as unreachable today; kept) |
| READY-8 the dry-run run id and the cross-launch re-draw order | text fix | §3.2 (`s2c-dry`; launches drawn in order, the cross-launch constraint re-drawing from launch 7 down, each bounded) |
| READY-9 arm_fixtures/check_hash missing from S2c's package | text fix | §9 S2c content; §8.2 form-hash entries row |

**Code review r9 (S2c's build, `docs/dev/reviews/2026-11-06-r9-memfn-s2c.md`), applied by fix lane s2cfix.** The
kit manager's rulings: every disposition ACCEPTED; G4 FOLD; EMIT-3 by majority lowering shape; SLOT-17 ruled
(the gate default is POLICY, R-35 (e)); G1 the gate of the fix. Text changed is marked `[rev1.3 r9-<id>]`.
Sabotage ids S2933 (mech row) and S2934-S2936 (slot-local rows) are the fix's.

| id | ruled | answered in |
|---|---|---|
| r9-G1 the gate never ran the TIMED entry; population unasserted; launch 1 only; `run` unbound to the dry run; caches by existence | FIX-NOW | §3.2 "The answer gate" (`_time` and `_gate` over every subject and a sentinel subject; arms, pools, subjects, timed calls asserted against the plan; every launch; the job's manifest; caches keyed by their inputs); slot sabotage (l3) S2934 |
| r9-G2 the cell-text check read the Arm, not the key | FIX-NOW | §3.2 cell-text check (the key's tokens name the instance; KEY-ARM MISMATCH); slot sabotage (g2) S2935 |
| r9-G3 the estimator took "ran" from cells files and a live plan | FIX-NOW | §3.5 "The run record" (the dry run's frozen plan; est reads the record's jobs, plan and floor; cells under a `#run_id` line; the cross-checks); slot sabotage (g3) S2936 |
| r9-G4 a verify row's dep named the canonical instance only | FIX-NOW, decision: **FOLD** | §2.4 READY-8 (the dep is `mf_form_hash(id)`, ONE hash over every instance's site text in table order); §3.2 entry table; mech row S2933 |
| r9-G5 the draft's form hashes from an unbuilt binary; box facts never written; draft on REFUSED | FIX-NOW | §3.5 run record (`box`, `isa`, `libc`, `gcc`, `rules`); §3.8 step 1 (deps from the dry run's `cell_text.tsv`; no draft on REFUSED) |
| r9-G6 window facts on J1's success path only; `declined-j1b` by default; unknown states fall to `failed` | FIX-NOW | §3.5 run record (window facts at every job's start and at finalize; the cause table) |
| r9-G7 card facts with a second home; the null base's bytes copied; `G//2` | FIX-NOW | §2.4 (the slot reads the ver-3 cards and the policy table); §3.2 (the null base's run/mask/members are its class instance's facts); §3.5 gates compared doubled |
| r9-G8 an unknown landing planted nothing; git's rc ignored | FIX-NOW | §3.2 (an unknown landing refuses) |
| r9-W1 the job scripts were absent | FIX-NOW | §3.3 (committed under `span_cards/slot/jobs/`); §9 S2c content |
| r9-W2 `after` waits forever on a failed upstream; J3-J5 chained after J2p | FIX-NOW | §3.3 readiness ("ended", not green; J3 after J2 and J2p ended); §3.5 run record (J2p 77 on a non-green J1) |
| r9-W3 the quiet wait bounded from the job's start | FIX-NOW | §3.3 (the job's total waiting time) |
| r9-EMIT-3 settest c2's instance is its cheapest shape | FIX-NOW, decision: **majority shape** | §3.2 entry table (vcls's lowering shapes; the instance must be the majority shape, else the row is a lower bound; today case pairs are 156 of 292 c2 sites) |
| r9-EMIT-4 the RUNCMP guard re-derived; settest's guard a no-op | FIX-NOW | §3.2 entry table (settest a leaf render, no selection) |
| r9-EMIT-5 PAIR's second production text | PLAN | §3.2 entry table (a `pair` cls `fn` instance; trigger: row 1 prices a B-fn PAIR site, or J1's verdict moves ofsskip) |
| r9-SLOT-9 vcls.out unstamped, a second census | FIX-NOW (stamp) + PLAN (fold) | §3.2 entry table (vcls.out names the sweep's sha-256 and commit; the fold into census0 with S2f's re-run) |
| r9-SLOT-10 §2.5 named walk's `alt` rows | DOC | §2.5 (the walk plans `one` only) |
| r9-SLOT-11 the enter card's `die1` vs kind 6 | DOC | §2.4 enter card note |
| r9-SLOT-13 the MAXDRAW trigger's unit | DOC + ruling | §3.2 (per (launch, arm)) |
| r9-SLOT-14 gen.c's subject sentence | DOC | (code comment only) |
| r9-SLOT-17 `gate_e6`: policy or card | RULED: POLICY | §2.4 (ver-3 cards state `-`; the slot reads `memfn/data/policy.tsv`'s `gate_default_e6`); §6 "Where it lives" |
| r9-CONTRACT-1/3/4/6 | DOC (spec) | `measures.md` §2.1¶1 `partial`, §3.4¶1, §3.4¶2a, §3.4¶14a, §3.5¶8a, §3.5¶12 row 1; CONTRACT-1's data form (a generic `unless:<run-key>=<value>` token and a base column) PLANNED, trigger: the next producer (S2g) |
| r9-CHECKS-3/4/6 | FIX-NOW | §2.4 (check C resolves every named dep; the count EXACT 17); R-MS3 fixtures per instance |

**Fix check of r9 (`docs/dev/reviews/2026-11-06-r9-memfn-s2c.md` "Fix check", `fixcheck.md`), applied by fix lane
s2cfix2.** Eight leftovers, all RULED FIX-NOW. Text changed is marked `[rev1.3 r9fc-<id>]`. Slot-local sabotage
ids S2937-S2939.

| id | ruled | answered in |
|---|---|---|
| r9fc-FIX-1 est read the cards and the policy live: a policy edit flipped a byte-identical record's verdict | FIX-NOW | §2.4 (the frozen plan pins the rows' values); §3.5 "The run record" (sections `cards`, `policy`, `cards_sha256`, `policy_sha256`; est reads only them); slot sabotage (f1) S2937 |
| r9fc-FIX-2 the key's landing, split, gap and pass were never compared with the Arm | FIX-NOW | §3.2 cell-text check (every key token through its card's dims, ONE table `plan.DIM_FIELD`); slot sabotage (f2) S2938 |
| r9fc-FIX-3 a ref-name FROZEN passed every dry run, then failed every job | FIX-NOW | (job scripts only: `jobs/common.sh` resolves FROZEN to its full sha; a non-hex value refuses at the dry run) |
| r9fc-FIX-4 S2934 reached the control's gate only; the control's dry-run evidence overwritten | FIX-NOW | §9 S2c ((l3) plants the arms' TUs only); `slot/sabotage.sh` (the control's est output keeps its own names) |
| r9fc-FIX-5 vcls's shapes were the spelling, not gcc's lowering | FIX-NOW | §3.2 entry table (`alu1`: one ALU op + one compare, a single-bit pair or an inner range; `cmp2`: two compares; c2 is alu1 217, cmp2 75 of 292: the `{X,x}` instance is the majority's) |
| r9fc-FIX-6 the round's call loop was unchecked (ACC never read) | FIX-NOW | §3.2 "The answer gate" (ACC against the planted counts every round; `drv check` in the dry run); slot sabotage (f6) S2939 |
| r9fc-FIX-7 the placement screen was no job; nothing held J1 on its verdict | FIX-NOW | §3.2 the placement screen and §3.3 (queue job `480-kit-s2d-screen`; every timing job's readiness waits on its verdict, 77 when non-green); §9 S2d |
| r9fc-FIX-8 the draft's resolved gate broke check C's cards equality | FIX-NOW | §2.4 (the set's cards as declared, `-`; the value in the run record's `policy`); `measures.md` §3.5¶2 (a `-` gate takes the run record's pinned value) |

## R1.2 What revision 1.2 changed, by r6 finding and by ruling

Every id of review 2026-11-06 r6 is answered here. "Ruled" is the kit manager's disposition (FIX-NOW and DOC
all ACCEPTED, with the named decisions).

| id | ruled | answered in |
|---|---|---|
| READY-1 measured delta rows name an arm in `inputs`, which the loader refuses | FIX-NOW, decision: **the base leaves `inputs`** | §3.4 step 1 (the cell id grammar: a delta arm's cells carry its base arm as the id's fifth field) and step 2 (the base is read from the row's cells); §2.4 (rows' `inputs` `-`; no placeholder still holds); §3.8 step 1; §4.4 (S2c's §2.2¶3 hunk WITHDRAWN: today's "only a derived or fitted row names inputs" stays true; new §3.4 says a measured row's derivation lives in its cells); §8.2 |
| READY-2 check C's card-guard population is 17, not 12 | FIX-NOW (text) | §2.4 (14 at the tree over the three card tables, 17 after kit-grid@3, floored at 17); §9 S2c; `tree_drill.py` C reads every card table |
| READY-3 the cell-less embed reds three STORE compares and moves two S-row detectors | FIX-NOW (text) | §3.8 "The embed" (the three compares re-aimed, S1241 and S1232 detectors re-verified, `tests/knowledge/CLAUDE.md` and `measures.md` §6¶2's last sentence); §8.2; §10.2 (measure_sets §8.3 "Embedded = committed") |
| READY-4 the embedded TEXT is `scripts/embed_text.sh`'s, not ksgen's; (v) names no check | FIX-NOW (text) | §3.8 "The embed" (a strip step before `embed_text.sh`, whose "unmodified" contract stays; ksgen pre-parses the stripped text and counts `file_cells` from the file); §9 S2e sabotage (v1)/(v2) |
| READY-5 slot sabotages have no runner; unbounded re-draw; (l) count-only; `--list-measurements=` | FIX-NOW (text) | §3.2 (re-draw bound; the answer gate on positions); §9 S2c ((j)-(l) are slot-local rows run by `slot/sabotage.sh`, not S-rows; (l)'s plant named); §3.1, §3.8 step 2 (`--list-measurements=draft.tsv`); (o)'s crash: NOTED in §9 |
| READY-6 the recompute's floor and `partial` need inputs outside the set | FIX-NOW, decision: **a kit-side RUN RECORD** | §3.5 "The run record" (`span_cards/slot/run_record.tsv`: never-ran groups with their keys, J1's verdict and cells, the floor's clause list; its sha in PROVENANCE.md and the set header's `run` key); §3.4 (the recompute reads set.tsv PLUS the record); §1 Goals 2-3; the floor's key list is the kit's, `measures.md`'s new section 3.5 states only the generic rule (§4.4) |
| READY-7 S2d's committed outputs have no unit | FIX-NOW (text) | §9 S2d (its commit: the run record, the `ofsskip.c` comment, the transcript's sha, the (b) filing request); §8.2 |
| READY-8 rows carry no deps | FIX-NOW, decision: **record the deps** | §2.4 (rows carry `kit:form.<id>=<hash>`, measure_sets §2.4/§7.2); check C's measure_store pass reads the RECORDED hash; grid1's `-` NOTED, not copied; §3.8 step 1; §11 Q3 |
| READY-9 S2a is not independent until S2e | FIX-NOW (text) | §9 Separability (S2a -> S2c's spec; S2b -> S2c -> S2d -> S2e) |
| READY-10 artifact_size_log.tsv holds no libpcrec figure | FIX-NOW (text) | §9 S2e (`size -t build/libpcrec.a`, `size -A build/obj/core/measures.o`, base vs head, in its report) |
| MEAS-1 placement seeded without a run id | FIX-NOW, decision: **a run id in the seed** | §3.2 (seed (run id, job, l, arm), the run id the window's, recorded in PROVENANCE.md and the run record); §3.5 HELD (re-run independence by construction; `place_drill.py` A2) |
| MEAS-2 the outcome table has two floor readings and no precedence | FIX-NOW | §3.5 "Outcomes" (ONE first-match table: UNIT, FLOOR over every ACTIVE clause, PARTIAL, FULL; HELD on a shared TEXT-class cause); `outcome_drill.py`; §1 Goal 2 |
| MEAS-3 a sibling cost row's gate refuses its whole group | FIX-NOW (small) | §3.5 (a cost row passes or fails ALONE; group verdicts kept for the unit and drift only) |
| MEAS-4 drift threshold on the per-launch scale | DOC + launcher's option TAKEN: **the s.e. in the threshold** | §3.5 Drift (3 standard errors of the statistic, `K_MED_E6` derived; power and false rate from `place_drill.py` B) |
| MEAS-5 the NULL rule's sign test has no outlier tolerance | FIX-NOW (small) | §3.5 (the sign test over the trimmed six); §2.3 (figures re-drilled, `floor_drill.py` both rules and the spike model) |
| MEAS-6 J1's margin not chosen by its stated reason | FIX-NOW, decision: **re-choose from the drill** | §3.6 (m 0.5, k 5, chosen by a stated rule over `j1_drill.py` Part 2's sweep; the false tolerance labelled) |
| MEAS-7 J1's verdict has no independent control | FIX-NOW (with READY-6) | §3.5 "What the recompute covers", §3.6 (the recompute re-derives J1's verdict from the run record's J1 cells) |
| MEAS-8 walk-set's floor quoted as walk's | DOC | §2.3 (one figure per pair, the larger, rounded up to the drill's 0.5-wb resolution) |
| S2c-1 PLACEMENT: the "3 of 4 phases per arm" rule cannot hold under gcc 15.2's alignment | ACCEPTED (kit manager's ruling on S2c's deviation 1) | §3.2 (each arm needs min(3, 64/A) distinct phases, A the object's own `.text` alignment; no alignment flag); §3.2 "The constraints" and "Re-draw order"; §R1.2 TWIN row; §9 S2c (j); §9 S2d (the placement screen) |
| S2c-2 walk-set is the walk | ACCEPTED (kit manager's ruling on S2c's deviation 2) | §2.3 (floor quote), §2.4 (one card key), §2.5 key and row lists, §3.5 tables, §3.3 job shapes, §9 S2c |
| MEAS-9 the bimodal test's own catch is ~3 % | DOC | §3.5 bimodal test (`place_drill.py` A rev 1.2 breakdown) |
| MEAS-10 a delta row's noise is estimator error | DOC | §3.4 step 7, §6 |
| MEAS-11 z 3.0's tolerance holds for normal launches | DOC | §6 (`coverage_drill.py` (3): t10, t5, two-class) |
| MEAS-12 "every time from tau ~1 %" | DOC | §3.2 (`place_drill.py` A's finer tau row) |
| MEAS-13 "every group boundary re-checks load" undefined under interleaving | DOC | §3.3 (the check is per LAUNCH; its waits are outside §3.7's estimate) |
| standing: movers.py is the 3rd mover census | PLAN | §5, §10 item 12 (main files the row: emit_sweep `--data measures` replaces movers.py at M1's first set) |
| standing: the slot harness is the 4th-5th | PLAN | §12 row 5 (FAM-B's trigger widened to "the next slot harness written") |
| standing: the recompute is a 4th python set reader | FIX-NOW (text) | §3.8 step 4 (it imports `tests/knowledge/ks_ref.py`'s parser; independence is owed to the slot harness) |
| general form 5: §12.1's trigger | DOC | §12 row 1 |
| text-vs-script gaps 2-4 (r6 meas.md) | DOC | §3.4 step 2 (E over arm AND twin; the base's group checked), step 3 (the control's slope over its own cells' lengths), §3.5 drift (the UNIT card's gate); `drill.py` now implements each |
| process change (loader refusal paths; embed/copy compares) | the launcher's | not this note's |

**How rev 1.2 stays clear of S2a.** READY-1: the base is named in the cell ID, a column whose content the
format leaves to the producer (`measures.md` §2.2¶4: an id appears at most once, nothing more), and rows keep
`inputs` `-`, which today's loader accepts; no loader, `ks_ref.py`, §7 or mfixtures change. READY-6: the run
record is a kit file outside the set; the set's `run` header key is existing provenance text. READY-8: a row's
`deps` is provenance text the loader carries and never parses. MEAS-1/2/3/4/5/6: the estimator's and the
slot's rules (S2c spec text, the slot harness). **Needs S2a: none.**

**Drills** (`span_cards/`, `python3 -I`, each prints its inputs; rev 1.2 re-ran every one): `drill.py` (§3.4-
§3.5 from the text, rev 1.2's NULL and drift rules, the base read from cell ids), `outcome_drill.py` (NEW: the
first-match outcome table and HELD on constructed runs), `place_drill.py` (adds A2: HELD with and without a run
id in the seed; the finer tau row; the two-class breakdown; B: K_MED and both drift thresholds),
`coverage_drill.py` (adds (3): non-normal launches), `floor_drill.py` (both NULL rules, N 2,000, the spike
model), `j1_drill.py` (adds Part 2: the (m, k) sweep and its choice rule), `tree_drill.py REPO` (C over every
card table; D's cell id with its base field).

## R1.1 What revision 1.1 changed, by r5 finding and by ruling

Every id of review 2026-11-06 r5 is answered here, by section or as PLAN/NOTED with its home.

| id | ruled | answered in |
|---|---|---|
| CELLS-1 (a) `length` holds E and LEN | FIX-NOW | §3.4 step 1 (format 2's `events` cell column; `length` is always the subject length), §4.4 (S2a hunk) |
| CELLS-1 (b) `round` has no value | FIX-NOW | §3.4 step 1 (`round` is the literal `med`; the per-round transcript is evidence outside the set, its sha-256 in PROVENANCE.md); Goal 3 starts at the cells (§1) |
| CELLS-1 (c) no group/job identity | FIX-NOW | §3.4 step 1 (group = `J<j>.<name>`, the job its prefix; arm names; the control arm `ctl` in `J<j>.ctl`) |
| CELLS-1 (d) "base in the same group" vs shared bases | FIX-NOW | §3.4 step 2 (ONE rule: a delta row's base is in its JOB's base group `J<j>.base`, same launch, named by the row's `inputs`); §3.7 counts redone (`tree_drill.py` B) |
| CELLS-1 (e) launch identity | FIX-NOW | §3.3, §3.4 step 1 (a launch is (job, l): one invocation of the job's launch script; every group of the job is timed in it) |
| CELLS-2 the recompute's domain | FIX-NOW | §3.5 "What the recompute covers" (refused groups' cells stay; J1's evidence is NOT in the set, its home `span_cards/slot/j1/`; the control is not a row; the one non-recomputable input named); §3.5 outcomes (delta-only groups and Goal 2's floor) |
| CELLS-3 `lengths`/`aa_rule` repurposed, placeholders | FIX-NOW | §2.4 (estimator grammar `slope X1,X2,X3` / `delta LEN`, no placeholder: the base is the row's `inputs`; `aa_rule` keeps `bimodal-test`, adds `twin-per-arm`), §4.4 (measures.md §2.2¶3, §2.3¶2 hunks), §10.2 (measure_sets §7.2, kit-grid.tsv column comment); the recompute parses format-2 sets' cards only, counted (§3.8) |
| CHECKC check C sees no grid3 key | FIX-NOW | §2.4 (the deps guard on CARD rows; rows' `deps` are `-`, only cards carry deps; a new counted measure_store pass at S2e, population 40 by `tree_drill.py` C) |
| HASH cell text vs canon site | FIX-NOW | §3.2 (every hashed arm is rendered AT its entry-table row's site shape and stated facts by the entry table's one renderer; the cell hash covers the kit's site text, never the driver's wrapper) |
| TWIN vacuous `cmp` | FIX-NOW | §3.2 (assert on LINKED addresses: arm vs twin function address mod 64 differ in every launch; at least min(3, 64/A) phases per arm over the 7 launches (`[rev1.3 S2c-1]`: A the object's `.text` alignment, was a flat 3); the loop phase recorded per arm per launch) |
| PLACE placement as a fixed offset | FIX-NOW (decide) | §3.2 "Placement is NOISE" (drawn per launch for every arm and twin; the control one fixed executable), §3.5 outcomes (HELD after a second refusal on one cause), §9 S2c (the placement screen in the dry run); `place_drill.py` A |
| DRIFT the statistic normalization cancels | FIX-NOW (text) | §3.5 Drift (what it proxies: a box-state change between jobs, whose non-proportional part no control sees; the threshold's power from `place_drill.py` B) |
| Z the drill without `aa`, two events | FIX-NOW (text) | §6 (re-drilled with the estimator as written over the within-launch share f; ONE event, the new draw; span_pick's sentence amended, §10.2); `coverage_drill.py` |
| FLOOR FRG x base | FIX-NOW (text) | §3.5 (the delta floor is the row's own paired A/A; FRG is dropped, its only reader gone), §2.3 (the per-hit resolution per key, `floor_drill.py`) |
| CENSUS no data-mover tool | FIX-NOW | §5 (S2a-S2d: emit_sweep's two-build sweep; S2e: `span_cards/slot/movers.py`, m0build's census method with nothing normalized; `movers/0002.tsv` in 0001's section shape) |
| KSGEN omission invisible | FIX-NOW (S2a) | §4.5 (`meas_store_check.c` gains a raw-row compare, noise included), §9 S2a sabotage (r) |
| BOUND copied literal, squared noise | FIX-NOW (text) | §4.1 (two literals, one compile-time equality in a test; K138's form amended for main, §10), §10.3 (row 1's band arithmetic) |
| MFMEAS filter, positional reader | FIX-NOW (text) | §4.2 (the handed population: `kit.` rows with a value; the two fields appended after the `%p` columns; `run_part_measures.sh` listed) |
| EMBED cells in libpcrec | MAIN -> R-35 (d) | §3.8 "The embed" (cell-less embed, the listing's column, no embed reader needs cells; `tree_drill.py` D: 260 KB avoided), §10.2 (measure_sets sizing sentence replaced) |
| GOAL2 cannot fail | FIX-NOW (text) | §1 Goal 2 (a floor on PRICED row-1 keys), §3.5 outcomes |
| D188A1 leftovers | DOC | §0 row 8, §2.5, §2.7, §9 S2g, §10, STATE: "HELD until [XARCH-DEV]'s go"; facts per declared target; fact (b) in the `class` header INSIDE the format-2 digest (§2.7, §5) |
| SIMD-READ | FIX-NOW (text) | §2.5 (the INTERIM stated, the kit manager's ruling; its consequences: C9 under variants, SIMD-off-by-default a per-target question at [XARCH-DEV]) |
| TARGET | FIX-NOW (text) | §2.7, §3.8 (`class x86_64/zen4`; fixtures compiled `-march=x86-64 -mtune=generic`, stated in `compiler`) |
| POLICY | MAIN -> R-35 (e) | §6 "Where it lives" (policy table outside the sets: z, the gate default, MATERIAL, each labelled; HORS_MIN and MAX_SET out), §10 item 7 |
| R35 drops | DOC | §10 items 8-10 (derived noise dropped; `verify_cmp` scoped by the census; C9's "SIMD-form cards join stage 2" moved by S2g's hold) |
| D149 labels | DOC | §3.2 (placement draw), §3.5 (drift factor 3), §3.6 (margin 2, "5 of 8"): each labelled with its trigger |
| J1-WIN | FIX-NOW (text) | §3.6, §3.7 (the PAIR arms leave J2/J3 for job J2p, whose `--ready` reads J1's verdict and answers never under (b); the set is then PARTIAL naming the pair keys) |
| LOCK | DOC | §9 Separability |
| ANCHORS | DOC | §8.2, §9 S2a (S1234 re-verified on a format-2 fixture; S1230-S1233, S1235, S1239 re-read) |
| SMP20 | DOC | §7, §10.2 (span_pick.md's two smp20.py cites, span_pick/CLAUDE.md, witness.sh; the golden is smp20.out plus one line) |
| J3 | DOC | §3.7 (counts from `tree_drill.py` B), §3.5 table (inputs printed by `drill.py`) |
| XREF | DOC | §4.4, §4.6 (§10 item numbers), §0 row 9 |
| INDEX | DOC | §3.8 step 3 (`supersedes` empty, both rows `current`) |
| CITE | DOC | §2.1, §10.2 (span_pick :267-268) |
| FAM-A, FAM-B, FAM-C | PLAN | §12 rows 4-6, with triggers |
| FAM-D | DOC | §7 (the census as the priced-forecast tool is this note's decision, moved out of §12) |
| FREEZE NOTE (DEFAULTS (B) unrecorded) | main recorded it | §8.3 cites R-35 (c) |

Main's R-35 rulings, each with its home: (c) DEFAULTS §8.3; (d) EMBED §3.8; (e) POLICY §6; the narrowings for
main to acknowledge §10 items 8-10. The kit manager's SIMD interim §2.5.

**Drills** (`span_cards/`, `python3 -I`, each prints its inputs): `drill.py` (the estimator, gates, NULL rule
and drift from the text, on §3.5's constructed outcomes and on one end-to-end example from cells),
`place_drill.py` (the unit gate under placement; drift power), `coverage_drill.py` (K_TRIM; z),
`floor_drill.py` (per-hit resolution), `j1_drill.py` (J1's rule under placement), `tree_drill.py REPO` (key
population, job points and box time, check C's population at the tree, the embed's bytes).

## R1. What revision 1 changed, by finding (review r4)

Every id of the review is answered here, in a section of this note or as PLAN/NOTED with its home.

| id | ruled | answered in |
|---|---|---|
| DRIFT-1 (D188) | FIX-NOW | §2.7 (the three facts, model-neutral), §3.2 (fact (b) is what a fixture's built code contains), §9 S2g |
| PREMISE-1 + SLOT-5 | FIX-NOW | §2.5 (row 1 prices the SCALAR layer only, SIMD forms ride as rungs; the cost stated), §2.7 |
| PREMISE-2 | FIX-NOW | §3.2 (cell builders named per family and site shape; vrun's RUN-term regime goes with J6, HELD) |
| PREMISE-3 | FIX-NOW | §3.2 (formhash gains a declared entry table: id, site shape, stated facts, policy), §9 S2c (re-costed) |
| PREMISE-4 + SLOT-3 + CONTRACT-4 | main RULED (B) | §8.3 (the flip at S2e and the three texts it amends), §1 Goal 1 (restated), §9 S2e (S1229 re-aim) |
| PREMISE-5 | FIX-NOW | §3.2 (the two-member walk is a site FACT on the composer's FIND site; a kit.h-only test entry if not) |
| PREMISE-6 | DOC | §10.2 (span_pick amendment: `kit-grid@2` -> `kit-grid@3`) |
| PREMISE-7 | FIX-NOW (text) | §2.7 (vany dropped; `kit-kernels@1` keeps governing vany, kit-kernels.tsv unchanged) |
| PREMISE-8 + CONTRACT-2 + SLOT-6 | FIX-NOW | §4.2 (the claim restated "on the shipped loader path"; both test levers hand UNMEASURED always) |
| PREMISE-9 + SLOT-12 + CONTRACT-9 | DOC | §4.1, §8.2 (three constructors), §4.3, §2.1 (7 rounds vs grid2's slot), §8.2 (kit-grid.tsv's per-version unit sentence) |
| PREMISE-10 | DOC (+ FIX-NOW with COST-5 (8)) | §7 (cite span_pick; census0 commits the P-blind count as a golden line) |
| PREMISE-11 | DOC | §3.7 (fixed 7 launches, no rerun allowance; 0.95 s cited as regime_eval's upper-bound figure) |
| PREMISE-12 | DOC | §3.7 (`docs/dev/lanes/r33_report.md` Sources line) |
| PREMISE-13 | DOC | §3.6 (`<h>wa = 128, <h>wb = 128`) |
| MEAS-1 | FIX-NOW | §3.2 (the A/A twin is a PERTURBED build of identical text), §9 row (j) |
| MEAS-2 | FIX-NOW | §3.5 (`noise_e6 x 10^6 <= gate_e6 x value_e6`, value > 0 required; cost rows only) |
| MEAS-3 | FIX-NOW | §3.5 (delta rows take `measure_sets.md` §7.4's NULL rule, never refuse a group) |
| MEAS-4 | FIX-NOW | §3.4 (A/A per arm, on the value), §3.5 (unit group = walk + walk#b only) |
| MEAS-5 | FIX-NOW | §3.4 (the literal integer recipe: cells, slope, event delta, normalization, medians, spread, root) |
| MEAS-6 | FIX-NOW | §2.3 (`find_hit` is per density, one group each, at row 1's mass range), §3.4 (event delta in one group) |
| MEAS-7 | FIX-NOW | §3.5 (one walk control per JOB, threshold from the between-launch spread, a stated size that matters) |
| MEAS-8 | FIX-NOW | §3.6 (paired per-launch sign + margin, a family majority rule; drilled) |
| MEAS-9 | FIX-NOW (text) | §6 (the error the band covers, z re-derived: 3.0, drilled) |
| MEAS-10 | FIX-NOW | §3.4 (the spread drops the one launch farthest from the median), §3.5 drill table |
| MEAS-11 + SLOT-9 | NOTED -> folds into MEAS-5 | §3.4 (every row is a per-launch ratio to that launch's own unit control) |
| MEAS-12 | FIX-NOW (text) | §2.3 (the buffer pool pinned on the card's `subject`); confirm later, trigger in §2.6 |
| MEAS-13 + CONTRACT-6 + COST-1 + SLOT-10 | ACCEPTED, strong form | §4.3 (derived rows carry `-` noise; no engine, no §3.2 column, sabotage (6) dropped), §12 (the general form as an unlock) |
| MEAS-14 | DOC | §3.7 (one window figure: 35 minutes; J3 counted from §2.5's keys) |
| SLOT-1 | FIX-NOW | §3.8 (per-launch cells in the set's `cells` section; no `raw.tsv`, no `cells.tsv`), §4.4 |
| SLOT-2 | FIX-NOW | §3.1 (split along `measure_sets.md` §7.1's seam; the D176 Q3 misquote fixed) |
| SLOT-4 | FIX-NOW | §2.4 (one dim name `form`, key token = canon id, check C's guard keyed on the deps column) |
| SLOT-7 | PLAN + DOC | §6 (z's home is [KIT-POLICY-TABLE], filed by main, trigger row 1; rev 0's narrowing withdrawn) |
| SLOT-8 | FIX-NOW (text) | §7 (census0 REPLACES smp20; `smp20.out` its one-site golden) |
| SLOT-11 | DOC | §9 (ids are the kit's, from the top of the free range at build time, R-35) |
| CONTRACT-1 | FIX-NOW | §3.8 (no format-2 file under `memfn/data/sets/`), §5, §9 row (o) |
| CONTRACT-3 | FIX-NOW (text) | §4.5 (`scripts/ksgen.c`, the regenerated `measures_table.inc`, the KsKind digest role), §8.2 |
| CONTRACT-5 | FIX-NOW (noise half) + PLAN (value half) | §4.1, §4.4 (the loader refuses noise past 10^15, S2a); the value half is pcrec's **K138** (main), not this note's |
| CONTRACT-7 | DOC | §4.5 (format 1: no parsed-noise field; grid1's decoded view byte-identical) |
| CONTRACT-8 | FIX-NOW (text) | §4.2 (MFMEAS prints a text digest of the handed triples), §9 rows (e), (f) |
| COST-2 | DOC | §7 (census0's output lives in `span_pick/`), §9 S2b |
| COST-3 | NOTED, for main | §2.7 (vany cards dropped; C9-scope context for main) |
| COST-4 | FIX-NOW (text) | §4.1 ("the next free MF_SITE_ABI at landing"), §8.1, §9 (each unit names its base and re-baselines), §2.6 (`enter` staleness) |
| COST-5 | FIX-NOW (text) | §9 (every sabotage row states why it can go red) |
| COST-6 | DOC | §8.2 (the `--list-measurements` readers by name; mfixtures `format 2` row; memfn CLAUDE.md gate) |
| COST-7 | NOTED | §9 (separability) |

Main's and the kit manager's rulings beyond the table, each with its home: DEFAULTS (B) §8.3; D188 §2.7; the
SIMD model ruled (D188 add. 1) §2.5, §2.7, §9 S2g; derived noise dropped §4.3, §12; `cells` and the §7.1 seam §3.1, §3.8;
the executable estimator §3.4, §3.5; MF_SITE_ABI at landing §4.1, §9; sabotage ids and why-red §9; K138 §4.1.

## 0. The decisions, one line each

| # | question (brief item) | decision | where |
|---|---|---|---|
| 1 | the cards | four quantities under a NEW method version `kit-grid@3`: `find_byte`, `find_hit` `[rev1 MEAS-6]` (per density), `verify_cmp`, `enter`; the UNIT row is `kit.find_byte.walk`; every key read by row 1; `[rev1 PREMISE-1]` scalar forms only: row 1 prices the scalar layer and SIMD forms ride as rungs, `[rev1.1 SIMD-READ]` the INTERIM until [XARCH-DEV]'s build; `memchr-back` DEFERRED (no reader); `hors.probe`/`find_hit(hors)` out (R14c) | §2 |
| 2 | the producer | `[rev1 SLOT-2]` split along `measure_sets.md` §7.1's seam: the KIT contributes probes (`[rev1.1 HASH]` cell texts rendered by formhash's entry table, the text the hash covers) and card rows; the estimator, gates and NULL rule are SPEC text (`measures.md`'s new sections 3.4-3.5) that M3 later implements; this one run's harness is a slot harness (§7.1 (d)), evidence, never built by make; the writer is pcrec's canonical writer. `[rev1 SLOT-1]` Per-launch cells go in the set's own `cells` section; `[rev1.1 EMBED]` the libpcrec embed omits them (R-35 (d)). `[rev1.1 PLACE]` Placement is NOISE: drawn per launch for every arm and twin, `[rev1.2 MEAS-1]` seeded with the run id. `[rev1.2 READY-1]` A delta row's base is named on its CELLS (the cell id), never in `inputs`. `[rev1.2 READY-6]` What the verdict reads outside the set (never-ran groups and their keys, J1's verdict and cells, the floor's clauses) is one kit-side RUN RECORD, `span_cards/slot/run_record.tsv` | §3 |
| 3 | the noise channel | `mf_measure` gains `noise_state` + `noise_e6` appended LAST (`[rev1 COST-4]` the next free MF_SITE_ABI at landing; an UNSTATED state is REFUSED); noise reaches the kit only from a set whose digest covers it, `[rev1 PREMISE-8]` on the shipped loader path; `[rev1 MEAS-13]` derived rows carry `-` noise (UNMEASURED): no derived-noise rule | §4 |
| 4 | noise in the digest | set FORMAT 2: `noise_e6` is a parsed value and the digest domain is `pcrec-meas-2`; `[rev1.1 D188A1, TARGET]` the format-2 digest also folds the `class` header (the priced target, D188's fact (b)); format 1 stays legal and unchanged, so zen4-grid1@1, its digest `13a6536315af1520` and its file sha stay byte for byte | §5 |
| 5 | the coverage factor | `[rev1.1 Z]` z = 3.0 (`COVER_Z_E3 3000`): at most 2.25 % one-sided false departure of a NEW draw on an equal-price one-card comparison, at every within-launch share, for the noise §3.4 writes (`coverage_drill.py`); UNMEASURED DEFAULT (D149); `[rev1.1 POLICY]` its home is the kit policy table outside the sets (R-35 (e)), written WITH its reader at row 1 | §6 |
| 6 | the step-0 gate | CONFIRMED: D176 Q3's "step-0 census" = SRS §7 step 0. Its trigger is met in advance; it runs FIRST anyway, compile-only, because its population SCOPES the card grid (D77); `[rev1 SLOT-8]` census0 REPLACES smp20; `[rev1.1 FAM-D]` census0 is the priced-forecast tool for every later row | §7 |
| 7 | what stage 2 moves | NO emitted byte, NO pcrec abi, NO stamp value. Moves: MF_SITE_ABI (next free); set format 2 + digest domain 2 (+ the `events` cell column); a new built-in set zen4-grid3@1, embedded cell-less; `kit-grid@3` card rows; form-hash entries; `[rev1 PREMISE-4]` DEFAULTS `idk` -> zen4-grid3@1 at S2e (R-35 (c)), zero movers; `[rev1.1 EMBED]` the `--list-measurements` listing's new column at S2e | §8 |
| 8 | build plan | SIX scalar units S2a-S2f; one timing window (S2d, 35 min, six jobs); `[rev1 D188]` J6 (SIMD, vrun only) is unit S2g, SEPARABLE and `[rev1.1 D188A1]` HELD until [XARCH-DEV]'s go; `[rev1 SLOT-11]` sabotage ids the kit's, each row with why it can go red | §9 |
| 9 | questions | none for Frank from this note (the SIMD model is ruled, D188 add. 1); `[rev1.1 XREF]` eleven items for main, items 8-10 the R-35 narrowings to acknowledge | §10 |

## 1. Goals

Ranked; a higher goal wins a conflict (`docs/dev/guide/architecture.md`).

| # | goal (who benefits) | measurable form |
|---|---|---|
| 1 | **Stage 2 moves nothing a caller sees** (every user; span_pick Goal 2's stage-2 cell; R-35 "adds no reader, moves no emitted byte") | `scripts/emit_sweep.py` byte-identical on EVERY arm (default, each deny, `--engine=vm`, both SIMD layers) at each unit's HEAD against `[rev1 COST-4]` its NAMED base commit, stamps included; every `<PREFIX>_MEASURES` is `""`; zen4-grid1@1's file sha and digest unchanged; `[rev1 PREMISE-4, rev1.1 EMBED]` `--list-measurements` (no value) changes ONLY at S2e: zen4-grid3's new row (`default_for` `idk`), zen4-grid1's `default_for` `idk` -> empty, and the new `file_cells` column on both rows (R-35 (d), §3.8); `[rev1.1 EMBED]` libpcrec grows by the cell-less embed only (`tree_drill.py` D: ~16 KB projected, S2e reports the measured figure) |
| 2 | **Every card row row 1 prices is measured with its noise** (row 1's lane; span_pick §The pick 4: a card without noise cannot qualify) | `[rev1.1 GOAL2]` a FLOOR on PRICED keys (value and noise set, not `null`) in zen4-grid3@1: every `find_byte` key; for each find form (libc, walk, and pair unless J1 (b) holds pair out), at least one `random`-landing `find_hit` row; for each census (form, cls), at least one `verify_cmp` row; every `enter.<kind>.NONE` row. A run that passes its gates but misses the floor is REFUSED, not PARTIAL (§3.5); the unit group passes its half gate and bimodal test. `floor_drill.py` gives the per-hit cost each key resolves (§2.3). `[rev1.2 MEAS-2, READY-6]` The floor is a list of CLAUSES (each met by one priced key of its list), written in the run record from census0's population and these rules, and checked over EVERY clause the run's J1 verdict leaves active, by §3.5's first-match table (`outcome_drill.py`) |
| 3 | **The set is self-checking from kept data** (the next editor; K35) | `[rev1 SLOT-1, MEAS-5]` a pcrec-side check recomputes every measured row's `value_e6`, `noise_e6` and NULL status, every group's verdict, Goal 2's floor and the `partial` verdict, from the set's own `cells` section EXACTLY by the spec's integer recipe (`measures.md`'s new sections 3.4-3.5), and the format-2 digest from the rows, each by code that shares no source with the producer. `[rev1.1 CELLS-1 (b), CELLS-2]` The recompute STARTS at the cells (each a median over rounds, the producer's); the per-round transcript is evidence (its sha-256 in PROVENANCE.md). `[rev1.2 READY-6, MEAS-7]` It reads the set file AND the kit's run record (its sha cited by PROVENANCE.md, checked first), and re-derives J1's verdict from the record's J1 cells; the record's never-ran list is the one input it takes as given (§3.5) |
| 4 | **The least producer that gives a trustworthy set** (Frank 2026-10-21, pcrec-test-harness-minimal) | `[rev1 SLOT-1, SLOT-2]` no second home for raw data (the `cells` section), no second set writer (the canonical writer), `[rev1.1 HASH]` formhash's entry table as the only cell renderer (the hashed text IS the timed text); no card without a named reader (D77) |

**Non-goals.** Any priced reader (row 1's). Unit 3.0. Retuning `PAIR_LOOKAHEAD` (a later unit change if the
sweep says so, §3.6). The SIMD official verdict (D144 add. 4: pcrec-bench). `[rev1 D188]` Any SIMD card
(J6, HELD: §2.7). Horspool's cards (R14c). The bundle-side sampling noise (§4.6). Derived-row noise (§4.3).
A between-window drift term (§3.5, a known gap with its trigger).

## 2. The cards

### 2.1 The method version: `kit-grid@3`

The set's `method` header is one `owner-name@ver` (`measures.md` §2.1¶1) and a set's `cards` must equal the
owner's committed rows at that ver (`measure_sets.md` §7.2). The span cards are quantities of the grid's
successor method (span_pick.md:267-268, `[rev1.1 CITE]`), but **`kit-grid@2` is TAKEN**: it is the method grid2's slot ran
under (`r17b_prime.md:2040`, "Method `kit-grid@2`"; :2059), never written to `memfn/data/cards/kit-grid.tsv`
(its header: "`ver 2` ... is grid2's prep lane's, NOT written here") and never committed to the store. D186
add. 2 refused to reuse `zen4-grid2` for the same reason (a name its readers already mean). So the new
method is **`kit-grid@3`**, appended to `kit-grid.tsv` (append-only by version). `[rev1 PREMISE-6]`
span_pick.md's own `(kit-grid@2)` is amended (§10.2).

**Relation to `r17b_prime.md` §5.4** (grid2's one slot spec): kit-grid@3 KEEPS its run rules (one box, one
method version, gcc 15.2 `-O2`, `taskset`-pinned, rotated interleaving, the per-launch median, the quiet gate
at every group boundary, the correctness gate before any clock, perf optional per D166 add. 1) and CHANGES
what is timed: §5.4 timed whole pcrec artifacts (grid1's harness, `docs/dev/lanes/grid1/README.md`);
kit-grid@3 times the kit's rendered FORM TEXT in a fixed find-all loop (§3.2), whole artifacts only where
the quantity is the consumer's (`enter`, §2.3) or the charter names a pattern (the PAIR sweep, §3.6).
Cross-set comparison is only within one `method@ver` (`measure_sets.md` §1.4), so zen4-grid3's ratios are
not compared with grid1's. `[rev1 SLOT-12]` Rounds: 7, as grid2's §5.4 slot ran (kit-grid@1's cards say 5;
a new version may differ). `[rev1 MEAS-9, MEAS-10, MEAS-14]` Launches: **7, fixed, with no rerun rule**
(rev 0: 5, +2 by rev3 C7's cross-launch trigger). grid2's trigger fired in 28 of its 32 F1 reruns, so a
"+2 when spread exceeds the floor" rule is close to "+2 always"; a fixed 7 gives the spread estimate about
five degrees of freedom after the trim (§3.4), an odd launch count (a true median), and a box time that is a
number, not a range.

### 2.2 What carries over from kit-grid@1: only the unit's regime

D77: a grid quantity no reader reads is not re-measured. At this branch no kit row reads a set key
(`measures.md` §4¶4; R1/R2/R8 retired at span_pick 1f; `kit.h3a`/`kit.gstar.*` "stay in zen4-grid1,
unread", span_pick.md:372), so none of grid1's ten quantities (`beta saving eps f xover block delta ccold
wuse gstar`) is re-measured. The UNIT is: its regime is pinned by the card ("streamed, fresh, long,
member-free", `measure_sets.md` §1.4), and that is exactly `find_byte`'s regime, so **the unit row is
`kit.find_byte.walk`** (value 1,000,000 by construction; `unit_key` may name any row, `measures.md`
§3.1¶2). byte(walk) in span_pick's price IS the unit: one row, not a unit row plus a walk row that
measure the same text twice. The unit group keeps §1.4's half gate and bimodal test. `[rev1 MEAS-4]` The
unit group holds the walk and its A/A twin ONLY; every other arm is in another group.

### 2.3 The four quantities

Key grammar (`measures.md` §2.3): a quantity is `[a-z][a-z0-9_]*`, so span_pick's `find.byte` is spelled
`find_byte`. Units (`measures.md` §3.1): `ratio` = per subject byte relative to the unit; `walkbytes` =
a per-event cost in u.B. Tokens are the kit's own (the format reads no owner's vocabulary, §2.3¶2).
`[rev1 SLOT-4]` The first dim of every quantity a kit form renders is `form`, and its token is the form's
canon id (§2.4).

`[rev1 MEAS-12]` **The subject pool is pinned.** "Streamed-fresh" is a POOL of distinct seeded buffers the
loop cycles through, never one buffer re-read: the pool is **16 MiB** (beyond the 7700X's 1 MiB L2, inside
its 32 MiB L3), stated on every card's `subject` token as `pool16Mi`. memchr's and PAIR's rates move with
the cache level and the walk's do not, so the RATIO is a property of the pool; 16 MiB is the bench's
throughput regime (1 MiB subjects re-scanned, L3-resident), an UNMEASURED choice (D149) with its trigger in
§2.6.

| quantity | dims | unit | subject (the card's regime) | points | estimator (§3.4) | per |
|---|---|---|---|---|---|---|
| `find_byte` | `form` | ratio | streamed-fresh `pool16Mi`, MISS-ONLY (no member in the subject) | lengths 64 Ki, 256 Ki, 1 Mi | `slope` over the three lengths | subject byte, all the method's streams (span_pick.md:216) |
| `find_hit` | `form;landing;split;gap` `[rev1 MEAS-6]` | walkbytes | streamed-fresh `pool16Mi` 1 Mi subjects, hits planted `periodic` (every g bytes) or `random` (seeded uniform, mean gap g); `split` `one` (one member occurs) or `alt` (both members, alternating) | `[rev1 MEAS-6]` g in {256, 1024}, each its OWN row and group | `delta` against the same form on the miss-only 1 Mi subject, per hit | candidate returned and restarted |
| `verify_cmp` | `form;cls;pass` | walkbytes | a fixed candidate array (positions spread over a 1 Mi fresh buffer), compared bytes seeded so the test passes with probability 0 (`p0`) or 1/2 (`p50`); a failing run differs at a uniformly seeded position | one point | `delta` against the `null` arm (same loop, compare replaced by a constant), per compare | one compare: cmp0, cmp½ (span_pick.md:220) |
| `enter` | `kind;entry` | walkbytes | a WHOLE ARTIFACT (`build/pcrec`) of a fixture pattern whose site states `kind` and an alternative of `entry`; candidates every 256 bytes that pass every verify position and die in the consumer one byte past the window (`die1`) | one point (g = 256) | `delta` of the pass subject against the fail subject (candidates fail the last verify position), per candidate | candidate passed on (span_pick.md:222) |

`[rev1 MEAS-6]` **Why per density.** Rev 0's one `find_hit` slope over g in {4096, 256, 32} plus the
miss-only point spanned four groups and two jobs, and its least-squares weights put 74 % of the slope on
g = 32 (31,250 ppm), far denser than row 1's masses (1,097 ppm for `{x,X}`, 4,154 ppm for '/': g ~ 912 and
~241, span_pick.md §Robustness). Periodic hits at g = 32 are branch-predictable where g ~ 900 random hits are
not. g in {256, 1024} brackets row 1's range; each density is one row measured inside ONE group against a
miss-only base in the same launch, so its A/A, gate and NULL rule have one group to refer to. WHICH density
(or both, as regimes) the price reads is row 1's design item (§10.3), with the landing pair.

`[rev1.1 CELLS-1, meas-5 (f)]` **A subject's event count is exact.** Every subject in a `find_hit` pool holds
EXACTLY E = 1 Mi / g hits: `periodic` at every g-th byte, `random` at E distinct positions drawn uniformly
(seeded) per subject. So E per call is one integer for every subject of the pool and every N, written in the
cells' `events` column (§3.4); a `verify_cmp` array has a fixed candidate count, an `enter` subject a fixed
candidate count, likewise.

`[rev1.1 FLOOR]` **What a `delta` row can resolve.** A per-event cost is the difference of two 1 Mi calls
divided by E, so its resolution falls with the call's noise and rises with E. `[rev1.2 MEAS-5, MEAS-8]`
`floor_drill.py` (§3.5's paired NULL rule as rev 1.2 writes it, the sign test over the trimmed six; per-call
arm-specific noise s; inputs: byte ratios walk 1.0, libc 0.06, pair 0.12 from smp20's stand-ins; N 2,000 runs
per point) gives the least per-hit cost priced in 90 % of runs, quoted ONE figure for the walk and walk-set
pair (the larger; `[rev1.3 S2c-2]` walk-set is the walk, so this was one figure already and stays the walk's) and rounded UP to 0.5 wb, the drill's resolution: walk and walk-set **3.5 wb at g 256 and
13.0 wb at g 1024 for s 0.5 %** (2.0 / 6.5 at s 0.25 %; 7.0 / 26.0 at s 1 %); pair 0.5 / 2.0 and libc 0.5 /
1.0 at s 0.5 %. (Rev 1.1's every-launch sign test needed 4.5 / 16.5 at s 0.5 % by the same rounding.) Row 1's
stand-in range is h1 5-40 wb (span_pick's smp20 grid): the g 256 rows resolve it at s <= 0.5 %, the g 1024
rows its part above about 13 wb. Rev 1's floor (`FRG x base`, FRG grid1's 3.09 %) was
31.6 wb at g 1024 for the walk whatever the run's noise; it is dropped (§3.5). Goal 2's floor asks one
priced `random` row per form, either density.

`[rev1 MEAS-6]` **`enter` at one density.** The pass-minus-fail difference at one candidate count cancels the
per-byte and per-candidate find costs (both subjects run the same find on the same positions), so rev 0's
second density bought nothing the difference does not already remove.

`[C10]` (span_pick.md:258): `enter` BAKES IN its fixture's survival (the consumer dies one byte past the
window); the alternative (a pcrec-stated survival x a per-byte card) waits for a reader that states survival.

`[rev1 PREMISE-1, D188]` **No SIMD form is a stage-2 card** (rev 0 carried vrun and vany as method tokens
here). §2.5 states row 1's position; §2.7 carries D188 and the held SIMD job.

### 2.4 The card rows (`kit-grid@3`, appended to `memfn/data/cards/kit-grid.tsv`)

`gate_e6` 30000 is grid1's UNMEASURED DEFAULT (D149) carried; the unit group gates at half (§1.4). `[rev1.3
r9-SLOT-17, r9-G7]` The ver-3 cards state `gate_e6` `-`: their gate is the POLICY table's `gate_default_e6`
(`memfn/data/policy.tsv`, R-35 (e), §6), the one home. `[rev1.3 r9fc-FIX-8]` The set's cards are the card
table's rows AS DECLARED (`-`; check C requires a set's cards equal to its card table), and the value a `-`
took is pinned in the run record's `policy` section (§3.5 "The run record"), which the recompute reads. The slot
harness reads lengths, launches, rounds, unit and gate from the ver-3 card rows and that table at the dry run,
never from its own constants; `[rev1.3 r9fc-FIX-1]` the frozen plan pins those rows' values and its estimator
reads them from the run record, never from the live tables. `[rev1.3 r9-SLOT-11]` The `enter` card's subject `die1` holds for kinds 1-5;
kind 6 (REPORT) has no die (its window IS the match, `slot/art.py`): its rows' regime is the pass-every-candidate
one, stated in `slot/enter/fixtures.tsv`.
`[rev1 SLOT-4]` `deps` are R-MS3 form ids; a card whose `deps` names `kit:form.<form>` has `form` as a dim,
and the key's `form` token IS the canon id (`libc`, never `memchr`: canon's `libc` id is the libc forward
one-byte find, memchr; `formhash.c:240`). The ids marked NEW gain `formhash.c` entries in unit S2c (§3.2).
`[rev1 MEAS-1, MEAS-4]` `aa_rule` `twin-per-arm`: every timed arm has its own A/A twin (§3.2);
`[rev1.1 CELLS-3]` the unit's card adds `bimodal-test`, the token `measure_sets.md` §7.2 already defines (rev 1's
`bimodal-unit` was a silent rename). `[rev1 MEAS-5, rev1.1 CELLS-3]` `lengths` names the row's ESTIMATOR in
the spec's grammar, `slope X1,X2,X3` or `delta LEN` (integers only), so a card says how its rows are
computed. **No placeholder** (`measures.md` §2.3¶2 "The format defines no placeholder token and reads no
owner's vocabulary" holds): rev 1's `delta base.<form> ... per-hit` substituted key tokens by dim name.
`[rev1.2 READY-1]` Each delta row's base ARM is named on the row's own CELLS (the cell id's fifth field, §3.4
step 1), never in its `inputs` (rev 1.1 put it there; the loader refuses inputs on a `measured` row,
`ks_measures.c:466-481`, and an arm is not a cell id): rows keep `inputs` `-`, and the event count is the
cells' `events` column, so the format reads only its own grammar. The recompute
parses `lengths` on the cards of FORMAT-2 sets only (a format-1 set's cards are never parsed, so grid1's
`slope 64Ki-1Mi member-free single calls` needs no exception by name); its population is every committed
format-2 set, counted and floored (§3.8). The §7.2 definitions of `lengths` and `aa_rule` and
`kit-grid.tsv`'s column comment are amended at S2c (§10.2).

| owner | quantity | ver | dims | unit | subject | lengths | launches | rounds | aa_rule | gate_e6 | env | deps |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| kit | find_byte | 3 | form | ratio | streamed-fresh pool16Mi miss-only | slope 65536,262144,1048576 | 7 | 7 | twin-per-arm;bimodal-test | 30000 | - | kit:form.\<form\> (walk, libc; pair NEW; `[rev1.3 S2c-2]` walk-set is the walk, no key) |
| kit | find_hit | 3 | form;landing;split;gap | walkbytes | streamed-fresh pool16Mi landed:periodic\|random | delta 1048576 | 7 | 7 | twin-per-arm | 30000 | - | as find_byte |
| kit | verify_cmp | 3 | form;cls;pass | walkbytes | candidate-array pass:0\|1/2 | delta 1048576 | 7 | 7 | twin-per-arm | 30000 | - | kit:form.\<form\> (settest, rc-words, rc-overlap, rc-bytes, rc-memcmp NEW; the census's (form, cls) pairs only) |
| kit | enter | 3 | kind;entry | walkbytes | artifact die1 g256 | delta 1048576 | 7 | 7 | twin-per-arm | 30000 | - | `-` (kit side: the pass-minus-fail difference cancels the find form, §2.3); pcrec: OWED (§2.6) |

`[rev1.2 READY-1]` The bases (each named on its row's cells, one arm in its job's base group `J<j>.base`): `find_hit` rows name
`base.<form>` (the same form's text on a miss-only 1 Mi subject); `verify_cmp` rows `base.null.<cls>` (the
loop with the compare replaced by a constant); `enter` rows `base.fail.<kind>.<entry>` (the fail subject).
The names are the producer's spelling, written into each delta cell's id; the format never builds them.

`walk-set` is the walk over a two-member stop (T-FIND's R7w). If S2c finds its text hashes as canon's
`walk` (one renderer row, the set test inlined identically), the id is `walk` and the `walk-set` keys fold
into it; the hash decides, never the name (§3.2). `[rev1.3 S2c-2]` **It does** (the kit manager's ruling on
S2c's deviation 2): the composer's FIND over `{X,x}` renders the walk's site text byte for byte (one form
hash, `bc7b2e02f06fe955`), so walk-set is NOT a card key. A second key with the same form hash would be a
duplicate card. Every `walk-set` below is rev 1.2's history, read as `walk`; the plan carries no walk-set key.

`[rev1 SLOT-4, rev1.1 CHECKC]` **check C** (`tests/memfn/finder_check.py` `check_sets`). At the tree it reads
`memfn/data/sets/*.tsv` only (5 sets; it resolves 65 form tokens, all in `kit-interim-grid1.tsv`) and
**0 of measure_store's sets** (`tree_drill.py` C). zen4-grid3 lives in `measure_store/` and §3.8 keeps format 2
out of `memfn/data/sets/`, so rev 1's guard "in the key loop" (:393-399) would have run over ZERO zen4-grid3
keys. Rev 1.1 puts the two halves where their populations are:
- **The deps guard on CARD rows**, in the card-table walk (:337-343), over every card table and every `ver`: a
  card whose `deps` names `kit:form.` must have `form` as its FIRST dim, else red. `[rev1.2 READY-2]`
  Population at the tree, over the three card tables the walk reads (`tree_drill.py` C): **14** cards with a
  `kit:form.` dep (`kit-grid.tsv` 9, `kit-kernels.tsv` 5, `kit-synthetic.tsv` 0), 0 of them without `form`
  first; kit-grid@3 adds 3 (find_byte, find_hit, verify_cmp), so **17**, the guard's count printed and floored
  at 17 by S2c (`[rev1.3 r9-CHECKS-3]` now pinned EXACTLY at 17, bumped by each new card, and every named
  `kit:form.<id>` dep resolved through `--hash`); `enter` has `-` and is outside it by its deps.
- `[rev1.2 READY-8]` **Rows record their deps.** Every form-bearing zen4-grid3 row's `deps` column holds
  `kit:form.<id>=<hash>` (the 16-hex `mf_form_hash` of its form token, measure_sets §2.4: "written by the
  producer from the card's `deps` declaration"). `[rev1.3 r9-G4]` **FOLD**: `mf_form_hash(id)` is ONE hash over
  the site texts of EVERY instance the id's entry-table rows hold, in table order, joined by a newline; a change
  to any instance stales every row of the id (over-staling costs a re-measure, a per-instance dep could miss
  one). walk, libc, pair and rc-memcmp have one instance, so their hashes are unchanged; settest and rc-words
  fold three each. The cell-text check (§3.2) compares each cell's site text with its INSTANCE's hash; the row
  records the fold, read from the dry run's `cell_text.tsv`; `enter` rows carry `-` (the kit side cancels, §2.3; pcrec's dep OWED, §2.6). So measure_sets
  §2.4's staleness (a recorded hash differing from the current one) and §7.2's "a row whose `deps` lacks a
  card dep" both hold for zen4-grid3, and a PAIR retune (§3.6 (b)) stales the PAIR rows through their
  RECORDED hash. grid1's rows carry `-`: a precedent the spec never sanctioned, NOTED, not copied (a
  committed revision never changes, `measures.md` §8¶1). Rev 1.1's "rows carry no deps" is withdrawn.
- **A new counted pass over `measure_store/`** (S2e, with the first set it can read): for every committed set
  whose method is a `kit-grid` version, every row whose card has `form` first resolves its form token through
  the R-MS3 entry table to an id with a hash (red, never "later", for `kit-grid@3`), and `[rev1.2 READY-8]`
  its recorded `kit:form.<id>=<hash>` names that same id with a well-formed hash (red otherwise); a recorded
  hash that differs from today's `mf_form_hash` is STALE, counted and printed, never red (staleness is a
  state, measure_sets §2.4), and S2e's witness asserts 0 stale at landing. The count is printed and floored,
  the floor pinned at S2e as zen4-grid3's form-bearing row count (40 by `tree_drill.py` A at the census
  stand-ins; S2e pins the real count). grid1's rows keep today's "later" treatment.
`enter`'s `-` kit dep is explicit, not silently skipped.

`libc` deps also record `libc:glibc@<ver>` as provenance, never row staleness (`r17b_prime.md` §5.3).

### 2.5 Keys, and the reader of each (D77)

The population of keys is the step-0 census's (§7): a token below is measured only if the census finds a
row-1-class site that reads it.

| keys | reader | why that reader reads it |
|---|---|---|
| `find_byte.walk` (UNIT), `.libc`, `.pair` (`[rev1.3 S2c-2]` no `.walk-set`) | row 1 | byte(m) of the methods row 1's candidates use: a one-member stop by memchr (`libc`) or walk, `{X,x}` by PAIR or walk (finder.c rows D1, D1w, PAIR, R7w) |
| `find_hit.{libc,walk}.{periodic,random}.one.{256,1024}`, `find_hit.pair.{periodic,random}.{one,alt}.{256,1024}` (`[rev1.3 S2c-2]` the `walk-set` `alt` rows fold into `walk`; `[rev1.3 r9-SLOT-10]` and the walk plans `one` ONLY: the table walk's control flow never sees which member hit, so its `alt` is its `one`, and no `find_hit.walk.*.alt.*` key exists) | row 1 | hit(m); the landing pair is the robustness regime span_pick requires (a random-like regime, §Robustness); WHICH landing and density the price reads is row 1's design item (§10.3) |
| `verify_cmp.<form>.<cls>.{p0,p50}` for the (form, cls) the census finds on row-1 sites | row 1 | cmp(f, p) at its two points (span_pick.md:220) |
| `enter.<kind>.NONE` for the kinds the census finds | row 1 | passes_r x enter on its NONE alternatives |
| `enter.<kind>.PARKED`, `enter.<kind>.RESEED`, same kinds | row 1's E2 family unification | span_pick.md:157-160: the "beat the incumbent by a margin" family unifies AT row 1, trigger the `enter` cards; MARGIN stays until the PARKED and RESEED cards exist (:257-258) |
| **HELD: `find_byte`/`find_hit` for `vrun-w16/w32`** | the C9 SIMD T-PICK row (D186 add. 2; span_pick §The pick 6) | `[rev1 D188, rev1.1 D188A1]` J6, unit S2g, HELD until [XARCH-DEV]'s go (§2.7) |
| **DROPPED: vany2/vany3 cards** | none | `[rev1 COST-3, PREMISE-7]` unrouted forms (`vany.c:16`), no reader (D77); §2.7 |
| **DEFERRED: `memchr-back`** | none | finder row D1c serves MLINE (`finder.c:270-275`); no priced row admits MLINE; D1c's own revisit trigger needs a libc-free back-find card that does not exist. R-35 and [MEASURE-SET]'s `next:` list it: For main (§10.1). Trigger: the first priced row admitting MLINE sites |
| **OUT: `hors.probe`, `find_hit.hors`** | the Horspool priced row (later) | R14c (span_pick.md:254-256): D-hors incumbents stay unpriced |

`[rev1 PREMISE-1, SLOT-5]` **Row 1 prices the SCALAR layer only; SIMD forms ride as rungs.** Rev 0 said "row
1's SIMD-on arm needs no SIMD card", and that is false on row 1's own witness: `(?i)x/1234` stamps
`RX_MEMFN_FORMS "none"` by default and `"vrun@w32+w16"` under `-fmemfn-simd` (the incumbent `{X,x}`'s fn-pair
body gains vrun rungs; the challenger '/' calls memchr on both layers, which is what D186 add. 2 C9's "NOT
smp20" speaks of). span_pick §The pick 6 offers two readings, and this note states one:

- **CHOSEN, as the INTERIM (the kit manager's ruling, review r5 SIMD-READ): row 1 is a scalar-layer row.**
  `[rev1.1 SIMD-READ]` Until [XARCH-DEV]'s build, `-fmemfn-simd` keeps today's `#if` arms UNCHANGED (the
  selector arms over `__AVX2__`/`__SSE2__`, `vrun.c:428-429`, `levels.def`): that is the interim, NOT the end
  state. **Row 1 departs on the generic (scalar) target only**: its prices read scalar cards, and its
  SIMD-on arm is judged as today's arms are judged, no slower beyond noise than the incumbent's arms (the
  layers rule's acceptance reading at both layers). D188 add. 1 abolishes exactly this shape in the end state
  ("an `#if` fall-through would run a plan chosen for another target"), which is why it is interim.
- (other) vrun keys are row-1 keys (measured by J2/J3, not J6). Refused here: it needs the SIMD cards whose
  build waits for [XARCH-DEV] (D188 add. 1), and it would make the scalar units depend on the held job.

**What the choice costs.** On a site whose scalar incumbent carries a SIMD rung (smp20's `{X,x}` ->
`vrun@w32+w16`), a scalar-priced departure to a span with no rung (memchr '/') can be SLOWER on the SIMD
layer than the incumbent was, because the price never saw the rung. Bounded TODAY: the SIMD layer is OFF by
default (D147); row 1's acceptance reading reports BOTH layers (memfn/CLAUDE.md, the layers rule), so a
SIMD-on loss is SEEN at row 1's landing verdict and refused beyond noise, not silent. The alternative's cost
is the hold itself: no row-1 key could be measured until [XARCH-DEV]'s build.

`[rev1.1 SIMD-READ]` **The consequences D188 add. 1 names** (drawn here, amendments for main in §10 item 4):
- **C9 under variants.** Under per-target variants every variant is planned and priced for its own declared
  target, so the SIMD variant's span pick is that variant's ORDINARY pick over its own target's cards. D186
  add. 2 C9's opt-in "SIMD T-PICK row" stops being "the only way a SIMD layer picks its own span" and becomes
  the per-target pick itself; span_pick §The pick 6's two readings collapse to one at [XARCH-DEV].
- **SIMD-off-by-default is a per-target question at [XARCH-DEV].** The bound above ("OFF by default") is a
  today-only bound: under a stamped default target LIST (D188 add. 1), whether a SIMD variant is in the
  default list is decided per target there, not by D147's switch.

### 2.6 Known gaps of the card set

- **`enter`'s consumer is pcrec's.** Its staleness cannot be a kit form hash; the set header's
  `code_commit` is the only record. A `pcrec:` dep id for the consumer's entry text is OWED, trigger: a
  re-measure showing `enter` moved beyond noise on a consumer-only change. `[rev1 COST-4]` Two byte-moving
  pcrec lanes land on main around stage 2 (variable lookbehind stage 1; the alternation normal form stages
  1/2p/2b, R-35 Concurrency). The window's frozen commit is main's tip when S2d is enqueued, recorded as
  `code_commit`; an entry-text change landing after it stales the `enter` rows, recorded in
  PROVENANCE.md as the known staleness with the trigger above. The window is NOT held for the landers.
- **Isolation.** A form timed in the fixture's loop is not the form inside a DFA's register pressure: that
  is model error, which span_pick puts OUTSIDE the band and in row 1's predicted-vs-measured print
  (span_pick.md:283-284). The cards make no in-situ claim. `[rev1 MEAS-1]` The perturbed A/A twin (§3.2)
  measures the fixture side of the placement effect; the in-DFA side stays outside the band.
- `[rev1 MEAS-12]` **The pool level.** The ratio of memchr/PAIR to the walk is a property of the pinned
  16 MiB pool. Trigger to re-pin: a find_byte(libc) re-measure at a 256 MiB pool moving the ratio beyond
  the row's noise, or row 1's predicted-vs-measured spread (R5.3) on long subjects.

### 2.7 `[rev1 DRIFT-1]` SIMD: D188's facts, and J6 (HELD)

**D188** (Frank, 2026-11-06, homed in this rev). `[rev1.1 D188A1]` Read PER DECLARED TARGET (D188 add. 1,
"read per variant's target"; rev 1 read them per `levels.def` level, which add. 1 replaced), a measurement set
records three facts:

- **(a)** the CPU has the target's features (cpuid), else "absent (CPU)", never run;
- **(b)** the BUILT fixture contains that target's variant, else "absent (build)", never timed;
- **(c)** the variant's cost, only when (a) and (b) both hold.

A set never grants availability; it only prices. Availability on a target stays with the target's compile
(D147, D144 add. 4); letting measured cards enable a level is the C9 row plus the separately ruled
SIMD-default event.

**The SIMD model is RULED (D188 add. 1, Frank 2026-11-06; manager's edit after delivery, `[rev1 D188a1]`).** There are
no `#if` arms in the end state. A code path is a per-target VARIANT, planned and priced for its DECLARED target.
One artifact may hold several variants (generic plus 1-2 SIMD) as target-attributed functions behind a
once-per-process CPU dispatch, each variant's entry exposed. The target set is an explicit caller-given LIST
with a declared, stamped default, never assumed. D188's three facts are therefore read PER DECLARED TARGET:
(a) the CPU has the target's features; (b) the built fixture contains that target's variant; (c) the
variant's cost, only when (a) and (b) hold. A set prices a variant; it never grants a target. The build of
variants waits for [XARCH-DEV]'s go, and the details are settled there. This note never builds on `#if`
fall-through. One observation for main (§10 item 5) stands for TODAY's tree only: `MEMFN_FORMS` names the
levels the emitted TEXT carries (`match_api.md` §6.3.10¶4: "`ID@LEVEL+LEVEL`"), so under today's `#if` arms
a stamp can name a level the fixture's own compile excluded. Under variants, fact (b) is read off the
artifact's declared-target list, and its spelling is J6's design item at [XARCH-DEV].

`[rev1.1 TARGET, D188A1]` **What zen4-grid3@1 records under D188: ONE declared target, the generic one.**
Every fixture (kit arm, driver, `enter` artifact, J1 width) is compiled `gcc 15.2.0 -O2 -march=x86-64
-mtune=generic`, stated, never assumed from the compiler's default; the flags are in the header's
`compiler` key. The set prices that target's (scalar) variant only:
- **`class x86_64/zen4`**: the ISA level the fixtures were compiled FOR (`x86_64`, the baseline, no `-avx2`
  suffix) `/` the box's tuning class (`measures.md` §2.1: "the ISA level and tuning class it was measured
  for"). grid1's `x86_64-avx2/zen4` is NOT copied: a copied class would read as the AVX2 variant's prices
  under [XARCH-DEV] while every cell is generic-target text. The card keys carry no target dim, because a
  set is one target.
- **(a)** the box has the target's features: the header's `isa` key (the box's cpuid list, provenance, as
  today) includes the baseline's; the slot harness's dry run refuses otherwise.
- **(b)** the built fixtures contain exactly the declared target's variant: **the `class` header, and it is
  INSIDE the set's identity**: the format-2 digest folds `class` after the domain (§5), so `id@rev:digest`
  names the priced target, and a FILE set re-using the id with another class is refused by no-shadowing
  (which compares digests, `measures.c`'s shadow rule). Every other target: absent (build), by the
  one-target rule, with nothing to record per target. Rev 1 homed (b) in PROVENANCE.md prose, outside the
  digest and outside `index.tsv`'s file sha; D188 says the SET records it.
- **(c)** the rows.
The spelling of (b) and (c) for a set holding SEVERAL targets' variants (rows per target, a section, header
keys) is the format event J6's design makes at [XARCH-DEV].

**J6 = unit S2g, SEPARABLE and HELD until [XARCH-DEV]'s go (D188 add. 1).** Content once released: vrun only (`vrun-w16`, `vrun-w32`; the kit
manager's ruling drops vany, §2.5). Its cells cannot come from the scalar builders: vrun renders only through
window row B-fn on ONE RUN term with REACH >= VW + T (`vrun.c:19-25`), and its G2 family is
`g2_simd_gen.c` (a policy word without `MF_P_PORTABLE_ONLY`), so its `subject` is a RUN-term regime of its
own (run length, mask hit rate, verify), designed at [XARCH-DEV]. Its form hashes need `formhash.c`
entries under a SIMD policy (today hard-wired PORTABLE, `formhash.c:291`). It records D188's facts per
declared target and times only targets where (a) and (b) hold. **Nothing in S2a-S2f depends on it**: no scalar card, gate,
estimator line or witness reads a SIMD cell. A set is one run (D166), so J6's rows join the NEXT set id,
measured with the scalar cards it is compared against (scalar the bar, D147), never appended to
zen4-grid3@1.

## 3. The producer

### 3.1 `[rev1 SLOT-2]` Where it lives: along `measure_sets.md` §7.1's seam

`measure_sets.md` §7.1 designs ONE install-time driver (`pcrec-measure`, M3) that owns run control, the card
interpreter, the NULL rule and the set writer, while **"Owners supply METHOD CARDS (§7.2) and PROBES. A kit
quantity is measured by the kit's harness mode: the forms and their timing arms are the kit's"**; it priced
and REJECTED "(b) a mode of the kit's harness only" (inverts ownership) and "(c) one python script" (install
time must not need python). Rev 0's `memfn/measure/` (a kit-owned driver, estimator, gates and interim-set
writer) was (b). **Rev 1 splits along the seam:**

| part | owner and home | built by make |
|---|---|---|
| PROBES: the rendered text of every kit arm, and its form hash | the kit: G2's generators gain a `--cards` mode (§3.2), `memfn/tests/g2/` | as G2 is today (the kit's own checks) |
| METHOD CARDS | the kit: `memfn/data/cards/kit-grid.tsv` `ver 3` rows (§2.4) | no (data) |
| the ESTIMATOR, the GATES, the NULL rule | SPEC text: `docs/spec/measures.md`'s new sections 3.4-3.5 (the format's own rule for a set that publishes cells), written so M3's C driver implements the same text | no (text) |
| the WRITER | pcrec's canonical writer, `pcrec --list-measurements=FILE` (`measures.md` §6¶2; `[rev1.2 READY-5]` the `=` form: the bare flag prints the index); the format-2 digest by `tests/knowledge/ks_ref.py`, verified by the C loader on load (two independent implementations) | yes (existing) |
| THIS RUN's harness: driver, subject generator, the slot's implementation of the spec's estimator, the job scripts, `[rev1.2 READY-6]` the RUN RECORD it writes (§3.5) and `[rev1.2 READY-5]` its sabotage runner | a SLOT HARNESS (`measure_sets.md` §7.1 (d), "slots only", for this one run): `docs/design/memfn/span_cards/slot/`, evidence like `docs/design/kit_proof/measure/` (the 650 template) and grid1's `docs/dev/lanes/grid1/` | no, never |
| the RECOMPUTE CHECK (Goal 3) | pcrec: `tests/knowledge/`, written from the spec's text, sharing no source with the slot harness | yes (`make test`'s measures section) |

**Why a slot harness, and why that is not (b) or (c).** M3 is unbuilt and unscheduled (D77: no measured need
for an install-time tool yet). Stage 2 is ONE run on ONE box, which is what a slot is; (b) and (c) are
rejected as the INSTALL-TIME tool, and nothing here becomes one. The harness owns no format text: the
estimator and gates it runs are the spec's, so when M3 is built it implements `measures.md`'s new sections 3.4-3.5 and
the slot harness stays behind as evidence. Python is fine for a slot (§7.1 (c)'s objection is install
time). The kit owns no writer: the set is written by pcrec's canonical writer.

`[rev1 SLOT-2]` **The D176 Q3 misquote, fixed.** Rev 0 quoted D176 Q3 as "the kit contributes its method cards
to that script"; that phrase is in neither decisions.md nor plan.md. D176 Q3 says: the kit measures this box
"as a new revision of the box's set, in a night window cleared with Frank, gated on the step-0 census. The
library (a canned self-contained pcrec measuring script, closest-match selection over declared fallback rows,
targeting another machine, the generic envelope) is [MEASURE-SET], already filed; `plan_cost.def` rows migrate
into the sets." The owner-supplies-cards-and-probes division is `measure_sets.md` §7.1's, quoted above.

### 3.2 The timed text, the cell renderer, and placement

`[rev1 PREMISE-2, PREMISE-3; rev1.1 HASH]` **One renderer: formhash's declared entry table.** Rev 1 rendered
the cells with G2's window generators while keeping `walk` and `libc` hashed at canon's composer site. The two
texts differ in constants and statements, and formhash's normalization folds identifiers only
(`formhash.c:19-31`), so the cell-text check was red in the correct build; and `g2_win_gen.c` renders no
composer FIND site (it sets no `pred.nterm`, so rev 1's `walk-set` cite of :1048 did not hold) (review r5 HASH).
Rev 1.1: S2c replaces `canon()`'s two-way branch (`mf_form_hash` hard-wires `mf_art_begin(...,
MF_P_PORTABLE_ONLY, ...)` + `mf_emit` on one STMT/FIND site, `formhash.c:291`) with a declared ENTRY TABLE,
one row per id, `id | site shape | stated facts | policy word | deny string`, read by ONE renderer path. That
path renders the text `mf_form_hash` folds AND the text the cell times: every hashed arm is timed AT its row's
site shape and stated facts (the canonical instance), so the timed text IS the hashed text.

| id | site shape | stated facts (the canonical instance) | how the form is reached |
|---|---|---|---|
| `walk` (the unit), `libc` | composer STMT/FIND, ASSIGN handoff (today's canon site) | today's, byte for byte: the set `[0-9]` via table (`walk`), the byte `x` (`libc`), `on_miss "return 0;"` (`formhash.c:237-277`); their hash values do not move, so grid1's and the interim sets' `kit:form.walk`/`libc` readers do not move | today's facts and deny string |
| `pair` | window FIND stop at offset 0, the window asker | the stop `{X,x}`, a two-member case pair | its facts: the window asker renders PAIR (`kit.h` `fd_stop.renders_pair`) |
| `walk-set` (`[rev1.3 S2c-2]` FOLDED into `walk`: same text, same hash, no entry) | composer STMT/FIND | the set `{X,x}` | `[rev1 PREMISE-5]` a FACT: the composer's renderers do not render PAIR (`kit.h:546-555`, `finder.c:656`), so T-FIND's first match is R7w; if its text hashes as `walk`'s, the row folds into `walk` (§2.4) |
| `settest`, `rc-words`, `rc-overlap`, `rc-bytes`, `rc-memcmp` (the census's set) | window verify step (`[rev1.3 r9-EMIT-4]` `rc-*`: the RUNCMP row the window verify step selects, its guard reading the arm that rendered; `settest`: a LEAF render of `kit_set_test`, no site and no selection) | per census (form, cls): the facts that make T-VERIFY pick it (run length and alignment for `rc-*`, a set position for `settest`) | its facts; a pair no fact set reaches is reported by S2c, never forced |

- `[rev1.3 r9-EMIT-3]` **A class is priced by its MAJORITY lowering shape.** A set-test class with one compare
  count still lowers differently. `[rev1.3 r9fc-FIX-5]` The shape is gcc's LOWERING on the declared target
  (§2.7), never the set's spelling: a two-compare `c2` set is `alu1` (one ALU op and one compare: any pair of
  singletons one bit apart, `{X,x}` and `{@,`}` alike, or an inner range, `[0-9]` as `sub; cmp`) or `cmp2`
  (anything else: two compares). `slot/vcls.py`
  counts each class's sites by shape (`shape` lines in `vcls.out`); the timed instance must be the majority
  shape (more than half the class's sites; `link.py` refuses otherwise), and with no majority shape the row is
  tagged `lower-bound`. Today c2 is alu1 217, cmp2 75 of 292 sites (by spelling it was case 156, pair 79,
  range 53, other 4): the `{X,x}` instance is `alu1`, the majority, and stays. `[rev1.3 r9-SLOT-9]` vcls.out's header names the sweep's sha-256 and the commit census0 swept it at;
  PLAN: fold its classes into census0 (§7 FAM-D, with HOUSE-16's `class_measure`), trigger S2f's census0 re-run.
- `[rev1.3 r9-EMIT-5]` PLAN: PAIR has a second production text (B-fn's `ofsskip` body, the `[Xx]abc` shape);
  a second `pair` instance, cls `fn`, joins the fold when row 1 prices a B-fn PAIR site or J1's verdict moves
  ofsskip.

- **Subjects use the instance's own bytes.** The subject generator draws miss bytes from outside the arm's
  stated stop set and plants hits from inside it, per row; so the constants timed are the hashed ones.
- **What the cell hash covers.** The kit's SITE TEXT exactly as `mf_form_hash` folds it (the site's emitted
  text and its sink tables, identifiers normalized), never the driver's wrapper. A cell's translation unit is
  `<the wrapper prologue for the row's site shape> <the site text> <the epilogue>`; the wrapper is ONE text
  per site shape, identical for every arm of that shape, a `static` function the driver's loop calls from
  `pos` to `n`, counting candidates, over the pool (§2.3).
- **The renderer entry** is a `kit.h` TEST entry beside `mf_form_hash` returning the site text of a table
  row (no `memfn.h` change; `mf_form_hash`'s signature stays). G2's generators are not the cell renderer; G2
  keeps checking these forms over its generated predicate space, as today.
- **The `null` verify base** is the driver's (the candidate loop with the compare replaced by a constant;
  `[rev1.3 r9-G7]` its subjects are its class instance's, the run, mask or members read from the instance's
  facts, never copied bytes);
  `enter` arms and J1's widths are whole artifacts (`build/pcrec`, `--emit-main`-free, linked by the driver),
  reached by the fixture patterns' own sites.

All texts are `MF_P_PORTABLE_ONLY` (the scalar layer, which is all stage 2 times), compiled for the ONE
declared target (§2.7). **The answer gate**: the driver's find-all count (verify: pass count) on every
subject against the subject generator's planted count, before any clock; the generator's positions, not the
form, are the expectation. `[rev1.2 READY-5]` It compares POSITIONS, not only the count: the driver also
returns the sum and the FNV-1a-64 of the found positions (verify: of the passing candidates' indices),
compared with the generator's, so a form that finds every hit one byte late keeps the count and is still
refused; the two figures cost nothing in the loop the gate runs outside the clock. `[rev1.3 r9-G1]` **The
gate runs the TIMED entry**: every subject is passed to the arm's `_time` (the loop the clock times) as well as
its `_gate`, and `_time`'s count must equal the planted count; each subject also has a SENTINEL twin (a hit at
its last byte, or its last candidate passing), so a timed loop that stops short misses even on a miss-only or
p0 subject (slot sabotage (l3), S2934). The gate prints its POPULATION (arms, pools, subjects, timed calls),
which the dry run asserts against the plan's (an arm with no length or a missing pool is a miss), and it runs
on EVERY launch executable and on `ctl`. `[rev1.3 r9fc-FIX-6]` **The round's call loop is checked too**:
every round sums its timed calls' counts (ACC) per point and compares it with the counts the generator planted
in the subjects those calls read (a miss is `ROUND MISS`, the round exits 3 and the job fails), and the dry run
runs the round's code once with each point's call count set to its pool size (`drv check`, no clock, its
population asserted) on `ctl` and every launch, so a loop that skips calls is refused before the window (slot
sabotage S2939; the ACC sees a skipped call only where the subjects' planted counts differ, p50 verify and
landed find, not on a p0 or miss-only pool). The dry run then writes the job's MANIFEST (the run id; the sha-256 of
the frozen plan, the fixture binary, `libpcrec.a`, `ctl`, `placement.tsv`, `cell_text.tsv` and the seven
launch executables); the work verifies it first and refuses on any mismatch, so it times only what was gated.
The fixture binary, the artifacts and the subjects are cached by their INPUTS' sha-256, never by existence;
`ctl` is built once per run directory and refuses inputs other than its own. `[rev1.3 r9-G8]` An unknown
landing refuses (it would plant nothing and pass 0 = 0). **The cell-text check** (COST-5 (10)): for every cell TU, the hash of its site-text
span by `mf_form_hash`'s fold equals `mf_form_hash(<the key's form token>)`. `[rev1.3 r9-G2, r9-G4]` The
(form, cls) is read off the KEY's tokens (`kit.<quantity>.<form>[.<cls>]`; `ctl` is the walk), the render uses
it, and an Arm whose own form or class disagrees refuses KEY-ARM MISMATCH (slot sabotage (g2), S2935);
`[rev1.3 r9fc-FIX-2]` so does an Arm disagreeing with ANY token of its key: the key is parsed by its card's `dims`
and each dim is compared with the Arm field ONE table (`plan.DIM_FIELD`) maps it to (form, landing, split, gap,
cls, pass, kind, entry), so the subject an arm is planted and timed with is the one its key prices (slot
sabotage S2938); the
compare is with the hash of the INSTANCE the key names (its cls; the canonical one when the key names none),
and the row's dep is the id's FOLD (§2.4), both written to the job's `cell_text.tsv`. With one renderer it guards the
KEY-to-ROW mapping (sabotage (k)); whether the stated facts reach the row through the kit's router is FAM-A's
independent control (§12 row 4).

`[rev1.1 PLACE, TWIN]` **Placement is NOISE, drawn per launch.** Rev 1's twin was ONE perturbed build, so
placement entered each arm's noise as one draw, a fixed offset that a re-run of the frozen text reproduces:
a placement-sensitive unit refused deterministically, and each J1 width carried a fixed offset into its rule.
The artifact a pick serves sits at a placement nobody chose, so placement IS part of the error a price
carries (span_pick's band). Rev 1.1 samples it L = 7 times per arm:
- **Each launch is its own executable.** For job j and launch l the dry run links `J<j>.L<l>` from one object
  per arm and one per twin (identical text, a separate translation unit), each preceded by a PAD object (a
  `.text` of P bytes, P a multiple of 16 in [16, 4096), drawn by a seeded generator from `[rev1.2 MEAS-1]`
  (RUN ID, job, l, arm)). Every arm and every twin takes a fresh, independent placement in every launch; the
  launch's R rounds run in it. `[rev1.2 MEAS-1]` **The run id** is the window's, fixed when S2d's jobs are
  enqueued (the enqueue time, `s2d-YYYYMMDDTHHMM`), passed to every job of the window and recorded in the
  run record, PROVENANCE.md and the set header's `run` key. A re-run in a later window has another id, so it
  re-links fresh placements: §3.5's HELD figures assume exactly that independence (rev 1.1's seed (job, l,
  arm) re-linked the SAME executables on a re-run; `place_drill.py` A2 at s 0.5 %, tau 0.5 %, 20,000 run
  pairs: re-refusal given a refusal 10.8 % with the same layout vs 6.8 % with a fresh one). `[rev1.3 READY-8]`
  **S2c's dry runs and its placement screen use the run id `s2c-dry`**, a fixed id that is never a window's
  (every window id starts `s2d-`): their placements are NOT the window's, and the window's own `--dry-run`
  (run at its enqueue, with its `s2d-` id) re-links and re-asserts every launch under the real id.
- **The constraints, asserted on the LINKED executables** (`nm`): in every launch each arm's timed
  function's address mod 64 differs from its twin's, and over the 7 launches each arm's function takes at
  least min(3, 64/A) distinct values mod 64, A being the object's own `.text` alignment (`[rev1.3 S2c-1]`
  the kit manager's ruling: revs 1 to 1.2 said "3 of the 4 values a 16-aligned function can take",
  which gcc 15.2's generic tuning makes unreachable, because it aligns tight loops to 32 and some objects'
  `.text` to 64; at A = 32 an arm can take 2 phases, at A = 64 one. At A = 64 the phase within a cache
  line is fixed by the compiler, so it is not a noise source the placement can vary: the constraint is
  recorded, not re-drawn, and the per-launch arm-vs-twin difference likewise binds only where A < 64. The
  seed still varies the object order and the offset at A granularity, which is the page and 4K-aliasing
  placement. No alignment flag is added: the cells time the declared target's default-compiled code. Today
  J2p's objects are all 64-aligned (S2c's report: phases 1); the other jobs' objects are 32-aligned, or
  16-aligned for some, and the draws report the phases they reach); a draw failing either is re-drawn (seeded,
  deterministic). `[rev1.2 READY-5]` The re-draw is BOUNDED: at most 64 draws per launch executable, and
  exhausting them REFUSES the dry run naming the launch and the failed constraint (a plant that makes every
  draw fail, sabotage (j)/(j2), refuses, never hangs); 64 is an UNMEASURED DEFAULT (D149), trigger: a dry run
  that needs more than 8 draws for any launch. `[rev1.3 r9-SLOT-13]` Both the bound and the trigger are per
  (launch, ARM): a launch's draws summed over its arms reach 8-17 in S2c's own dry runs, while one arm's
  never exceeded 5; the trigger has not fired. `[rev1.3 READY-8]` **Re-draw order.** Launches are drawn in
  order l = 1..7, draw index d = 0.. per launch (the seed is (run id, job, l, arm, d); d = 0 is the plain
  (run id, job, l, arm) draw). The per-launch constraint (arm and twin differ mod 64) is checked on launch l's
  link and re-draws launch l. The CROSS-launch constraint (min(3, 64/A) values over the 7 launches, `[rev1.3 S2c-1]`) is checked once
  all 7 are linked; on its failure the LAST launch whose re-draw can still repair it is re-drawn: launch 7
  first, then 6, ..., each with its own bound of 64 draws, an arm's cross-launch failure re-drawing that
  launch's whole executable (every arm and twin, so the per-launch check is re-run on it). Exhausting launch
  1's draws refuses, naming the arm and the constraint. Never asserted on object bytes: STT_FILE makes two differently named objects differ with no
  pad at all (review r5 TWIN). Text equality is asserted on the sources (`cmp`) and on the linked `.text` of
  the two functions (objdump ranges, relocations masked). The hot loop's address (objdump: the function's
  first backward-branch target) is RECORDED per arm per launch in the transcript, not asserted: a loop
  aligned inside the function can share a phase across two function phases. UNMEASURED DEFAULT (D149): the
  pad range and the phase count min(3, 64/A); trigger: the placement screen below showing the walk's placement spread above half
  the unit's half gate.
- **The twin** is the same arm at an independent placement in the same launch: its within-launch difference
  holds run noise AND placement in every launch (§3.4 step 5's aa), and `sp2` holds the between-launch
  placement spread. The A/A no longer rests on one lucky or unlucky pad.
- **The control is ONE fixed executable** `ctl`: the canonical walk's text at the three `find_byte` lengths,
  at one placement, built once by the window's first dry run and shared by every job, its sha-256 asserted at
  each job's start. It is a launch-state probe, not a row (§3.4 step 3). Each round of a launch runs `ctl`
  once beside the launch executable's round (both pinned to the same CPU), so its cells share the launch's
  state, and no normalization or drift comparison ever compares two placements of it (review r5 PLACE (iii)).
- **The placement screen** (S2c's dry run; light, not a timing window, the box need not be quiet): the
  dry run times `kit.find_byte.walk` and its twin at their 7 drawn placements once and prints the unit's §3.4
  noise. If it already exceeds the unit's half gate, the window is NOT requested: the kit manager rules first
  (§3.5 HELD), with the figure in hand. A noisy box only inflates the figure (the safe side); re-run the screen. `[rev1.3 S2c-3]` S2c's own screen ran on a loaded box (load ~7.8, a queue job running): unit noise 8.56 %, over the 1.5 % half gate. It is NO READING; it shows only that the screen computes and prints. The screen that counts runs quiet, at the window's start before J1, as S2d's first step. `[rev1.3 r9fc-FIX-7]` It is a QUEUE JOB, `480-kit-s2d-screen` (after the prep, whose J2 manifest it reads; quiet-gated as a launch is): every timing job's readiness waits for its verdict, and a non-green screen (over the half gate, exit 3) makes J1-J5 answer 77, so the window is HELD with no timing done.
- **What it does to the unit gate** (`place_drill.py` A; L 7, run noise s, placement s.d. τ per build). Like
  for like at s 0.5 %, a refusal of the frozen text on its re-run ("held"): τ 0.5 %: rev 1 refused 7.7 %,
  held 3.8 %; rev 1.1 refused 5.7 %, held 0.3 %. τ 1 %: 34 % / 28 % vs 52 % / 27 %. τ 2 %: 63 % / 59 % vs
  97 % / 94 %. Below τ ~ 0.5 % rev 1.1's refusals are run noise and a re-run (fresh placements, `[rev1.2
  MEAS-1]`) clears them; from τ ~ 1 % the walk's per-byte cost moves with placement by about its own half
  gate, and the per-launch draw reports it instead of leaving it to the luck of one pad: `[rev1.2 MEAS-12]`
  refused 52 % at τ 1 % (s 0.5 %), 87 % at τ 1.5 %, 97 % at τ 2 % (`place_drill.py` A, the finer row), so
  "every time" holds from τ ~ 1.5-2 %, not from 1 %. A twice-refused unit is HELD, not re-run (§3.5).

D188's fact (b) is the same class of question (what code a fixture actually contains), answered in §2.7.

### 3.3 The job shape

Template: `docs/design/kit_proof/measure/650-covertime-slot`. Each job: `--dry-run` builds every arm, links
the job's seven launch executables (§3.2) and asserts the placement constraints and `ctl`'s sha, and runs the
answer gate (no clock); it prints `boxqueue: cap`, `patience none`, `idle-ok`, `est`, and `expect groups=N
lines=^== s2 GROUP done` (a population the work prints per group, so a short job is POPULATION-SHORT, not
green); `--ready` is 650's quiet gate (no running queue job, no box-lock holder, load1 < 2.0 on two samples
>= 55 s apart); the work is the slot harness's `run`. Pinned `taskset` to CPU 7, sibling CPU 15 idle (650's
pair; grid1 used 14, which only names a different core: the set's `box` records it). Jobs chain with `after`
and declare `not-before`/the window's times; `[rev1.3 r9-W1, r9-W2]` the job scripts are COMMITTED under
`span_cards/slot/jobs/` (prep 480, `[rev1.3 r9fc-FIX-7]` the placement screen 480 after it, J1-J5 and J2p 481-486, J9 489; a `window.env` beside the queued copies
carries the run id, the frozen commit and the tree; every `--dry-run` compares its copy with the tree's). The
prep job runs every job's dry run; a timing job's `--dry-run` checks its inputs only and prints `expect
groups=N` from `plan.py groups`. "Chain" is END, not green: a job is ready once its upstream ENDED (green,
failed or cancelled), since boxqueue's `after` waits forever on a failed upstream and would leave J9 pending
and the record never finalized; every timing job answers 77 once the prep ended non-green, and (`[rev1.3
r9fc-FIX-7]`) waits for the screen's verdict, answering 77 once it ended non-green; J2 follows J1, J2p
follows J2 and answers 77 when J1 ended non-green (no verdict will come) or under (b); J3 follows J2 AND J2p
(so J2p's 77 never cancels J3-J5); J4 follows J3, J5 J4; one stage per job, each under an hour (BOILERPLATE, Frank
2026-10-30). The quiet gate checks only the START (BOILERPLATE:236). `[rev1.2 MEAS-13]` Groups are interleaved
within a launch, so a "group boundary" has no single place; the re-check is per LAUNCH instead (replacing rev
1.1's per-group wording): before each of a job's 7 launches the harness takes ONE load sample and reads the
queue and the box lock (instant), records them in the transcript, and only if they are not quiet WAITS for the
start gate's two-sample quiet (bounded at 5 minutes per job, an UNMEASURED DEFAULT, D149, trigger: a wait
timing out in the window; `[rev1.3 r9-W3]` the bound is the job's TOTAL WAITING time, never wall time from the
job's start, which a job's own timing would exhaust); a job whose wait times out FAILS, its launches so far discarded, so it has no cells
(its groups are never-ran, §3.5). Every group of a job shares its launches, so a group present in the set's
cells was timed in launches that each started quiet. §3.7's 35 minutes counts NO wait: a wait extends its job
within the job's cap, and the window's slack absorbs about one. `[rev1.1 CELLS-1 (e)]` **A launch** is (job, l): one invocation of the
job's launch script, running every group of the job in rotated, interleaved rounds; launches of different jobs
are unrelated. `[rev1 MEAS-7, rev1.1 PLACE]` Every launch's round runs the control `ctl` (§3.2); §3.4
normalizes each launch by it and §3.5 checks drift with it.

### 3.4 `[rev1 MEAS-5, rev1.1 CELLS-1]` The estimator, literally (the spec text of `measures.md` new §3.4)

Notation: `rhafz(n, d)` and canonical order are `measure_sets.md` §1.7's (round half away from zero,
truncating division, int128 intermediates in C, integer `divmod` in python); `isqrt_rn(N)` = r + (1 if N - r^2
> r else 0) with r = floor(sqrt(N)) exact (no ties for integer N); `med(v)` = the LOWER median, element
`(n - 1) / 2` (truncating) of v sorted ascending, never an average. L = the card's `launches` (7), R = its
`rounds` (7). `[rev1.2 READY-6]` The recompute reads the set file (header, cards, rows, cells) and the kit's
RUN RECORD (§3.5), and nothing else; rev 1.1's "ONLY the set file" was false (its floor and `partial` read
inputs outside it).

**1. Cells (format 2's `cells` section, §3.8).** For arm `a`, length `x` and launch `l`, a round times N calls
of the arm over the pool (N calibrated by doubling to >= 50 ms per timed loop, D144 add. 1) and gives T ns;
its per-call figure is `rhafz(T x 10^6, N)` (ns x 10^6 per call). The cell `c(a, x, l)` = `med` over the R
rounds: the producer's step, recorded, not recomputed (the per-round transcript is evidence, its sha-256 in
PROVENANCE.md). A cell row's columns (format 2, `[rev1.1 CELLS-1]`):
- `cell`: a unique id. `[rev1.2 READY-1]` Its spelling is the estimator's, `/`-joined: `<group>/<arm>/<length>/
  <launch>`, and on the cells of a `delta` row's arm and its twin a FIFTH field, the row's BASE arm:
  `J3.hit.random.1024/kit.find_hit.walk.random.one.1024/1048576/4/base.walk`. **A measured row's derivation
  lives in its cells**: the estimator is the card's `lengths`, the base is on the cells, the row's `inputs`
  stays `-`. The format reads the id only for uniqueness (§2.2¶4); this section gives it its meaning, and the
  recompute refuses a set whose ids do not parse this way. `[rev1.3 READY-5 (a), (c)]` The recompute also
  COMPARES the copies: (a) the id's first four fields equal the cell's own `group`, `arm`, `length` and
  `launch` columns (a mismatch refuses the set; the estimator reads the COLUMNS, the id only for its fifth
  field), and (c) the fifth field equals the base the row's quantity declares by the family rule of §2.4:
  `find_hit.<form>...` -> `base.<form>`, `verify_cmp.<form>.<cls>...` -> `base.null.<cls>`,
  `enter.<kind>.<entry>` -> `base.fail.<kind>.<entry>` (a producer that computes AND names a wrong base is
  refused). Each gets a plant beside (w)/(x) at S2e (§9). `group`: `J<j>.<name>`, the job being the text before the
  first `.` (groups: `J<j>.ctl` the control, `J<j>.base` the job's delta bases, and one group per row
  family, e.g. `J2.unit`, `J3.hit.random.1024`);
- `arm`: a row's KEY as written in `rows` (`kit.find_byte.walk`), its twin `KEY#b`, a base `base.<name>`
  (`[rev1.2 READY-1]` the name in its delta rows' cell ids), or `ctl`;
- `length`: the subject's length in bytes, ALWAYS (for a `delta` row, the card's LEN);
- `launch`: 1..L, the launch within the job; `round`: the literal `med` (the cell is a median over rounds);
- `events` (NEW in format 2): the event count E per call of the cell's subject (hits, compares or
  candidates), an integer, `0` on a miss-only or fail base, `-` on a `slope` arm or `ctl`;
- `ns_e6`: the cell.

**2. Per-launch absolute, by the card's estimator** (`lengths`, parsed on format-2 sets only, §2.4).
- `slope X1,X2,X3` (find_byte; `[rev1.2]` the control `ctl`, which has no card, is a slope over its own cells'
  `length` values, which must be exactly three distinct lengths in `J<j>.ctl`): with x_i the lengths and y_i = c(a, x_i, l), S = n·Σx_i·y_i
  − Σx_i·Σy_i and D = n·Σx_i^2 − (Σx_i)^2 (n = 3, exact integers), `abs_l = rhafz(S, D)` (ns x 10^6 per byte).
- `delta LEN` (find_hit, verify_cmp, enter): `[rev1.2 READY-1]` the base B is the ONE arm named in the fifth
  id field of the row's cells (the same B on every cell of a and a#b, else the set is refused); `D_l = c(a,
  LEN, l) − c(B, LEN, l)`; E = the `events` of a's cells (one value over all of a's AND a#b's cells together,
  else the set is refused); `abs_l = rhafz(D_l, E)` (ns x 10^6 per event). `[rev1.1 CELLS-1 (d)]` **One base
  rule:** B's cells are in the row's JOB's base group `J<j>.base` (the recompute checks the group, not only
  the job prefix), in the same launch; a base may serve several rows of its job (J3's `base.walk` serves
  four), never a row of another job. The twin uses the same base:
  `D#b_l = c(a#b, LEN, l) − c(B, LEN, l)`.

**3. `[rev1 MEAS-11; rev1.1 PLACE]` Per-launch, by the launch's control.** `u_l` = the `slope` of arm `ctl`
in the row's job's group `J<j>.ctl`, launch l. `v_l = rhafz(abs_l x 10^6, u_l)`. A launch-wide shift
(frequency, page colouring) moves the arm and the control together and cancels in v_l.

**4. `[rev1.1 PLACE]` Anchored to the unit.** `W = med(v_l)` of the unit row (the header's `unit_key`, in
J2). Every row's anchored per-launch value is `x_l = rhafz(v_l x 10^6, W)` (ratio: x 10^6; walkbytes: u.B x
10^6), its twin's `x#b_l` likewise. `value_e6 = med(x_l)`; the unit's is exactly 10^6 (rhafz is monotone and
L odd, so its median maps to `rhafz(W x 10^6, W)`). `abs_ns_e6` (provenance) = `med(abs_l)`. The control is
one fixed placement (§3.2) and the unit is the walk over seven drawn placements, so the anchor makes the unit
the walk's placement-median cost, not the control's one placement.

**5. `[rev1 MEAS-4]` A/A, per arm, on the value.** `aa = med(|x#b_l − x_l|)`.

**6. `[rev1 MEAS-10]` Spread: trimmed, scaled.** Drop the ONE launch farthest from `med(x_l)` (ties: the later
launch); with the remaining n = L − 1 values w, `Q = n·Σw^2 − (Σw)^2` (exact), and
`sp2 = rhafz(K_TRIM_E6 x Q, 10^6 x n x (n − 1))`, `K_TRIM_E6 = 1723000`. K_TRIM is DERIVED, not tuned: the
trimmed variance of 7 normal launches is low by 1/1.723 (`coverage_drill.py` (1): 200,000 draws, rms of the
trimmed s.d. 0.7618, 1/0.7618^2 = 1.723).

**7. noise.** `noise_e6 = isqrt_rn(aa^2 + sp2)`, in the row's unit x 10^6. `[rev1.1 Z]` Its scale: with
placement drawn per launch both terms see the arm-specific variance, so for a within-launch share f of a
launch's variance it is about 0.95 (f 0) to 1.40 (f 1) one-launch sigmas (`coverage_drill.py` (2), mean
noise); a CONSERVATIVE 1-sigma, and §6's z is derived for it as written. `[rev1.2 MEAS-10]` On a `delta`
row the spread is mostly the ESTIMATOR's error (two 1 MiB calls' noise over E, plus the base's placement), not
the per-hit cost's own launch distribution (`drill.py` (2): the walk's random hit row carries noise 3.27 wb on
19.49 from 0.2 % cell noise), and rows sharing a base (J3's `base.walk` serves four), W and their job's `ctl`
share part of it per launch, while §6's band sums cards as independent: it errs WIDE (wins forgone, the safe
side). The only roundings are the cell
medians', steps 2-4 and 6's `rhafz`, and the root: the recompute agrees EXACTLY or fails (`measure_sets.md`
§1.7).

**8.** `n` (provenance) = L x R.

### 3.5 `[rev1 MEAS-2, MEAS-3, MEAS-7; rev1.1; rev1.2]` Gates, the NULL rule, drift, the run record, outcomes (the spec text of `measures.md` new §3.5)

`[rev1.2 READY-6]` **What is spec and what is the kit's.** `measures.md`'s new section 3.5 carries the GENERIC rules
below: the gates, the NULL rule, the bimodal test, drift, and the outcome table over "the producer's declared
floor, a list of clauses kept in a run record outside the set, cited by sha-256 from the set's PROVENANCE.md".
The floor's clauses, J1's rule and the never-ran list are the KIT's (this note and the run record), never
measures.md's text (its format "reads no owner's vocabulary", §2.3¶2).

- **Cost rows** (the `slope` rows, the unit included) pass iff `value_e6 > 0` and
  `noise_e6 x 10^6 <= gate_e6 x value_e6` (`gate_e6` the card's; the unit's at HALF). A non-positive cost is
  a failed measurement. `[rev1.2 MEAS-3]` **A cost row passes or fails ALONE**: a failing row is absent from
  the set (its cells stay) and its key is named in the run summary; its group's other rows are unaffected
  (rev 1.1 refused the whole group, so `find_byte.walk-set` (now `walk`, S2c-2) over its gate removed `find_byte.libc`). Group
  verdicts remain only where they mean something: the UNIT group (the unit row's gate and bimodal test) and a
  JOB's drift.
- `[rev1.1 FLOOR; rev1.2 MEAS-5]` **Delta rows** (`find_hit`, `verify_cmp`, `enter`) are `null` (EMPTY value,
  `-` noise) UNLESS `D_l > 0` on each of the SIX launches left after dropping the one farthest from `med(D_l)`
  (ties: the later launch; §3.4 step 6's trim), and `med(D_l) > aa_D` over all seven, with `aa_D = med(|D#b_l −
  D_l|)` = `med(|c(KEY#b, LEN, l) − c(KEY, LEN, l)|)`: the row's OWN paired A/A, which holds run noise and
  placement (§3.2). The trim is the spread's own: rev 1.1's every-launch sign test let one base-cell spike
  null every row that base serves in that launch (J3's `base.walk` serves four) while the cost rows' trim
  absorbed the same spike; `floor_drill.py` Part 2 (walk g 1024, h 20 wb, s 0.5 %, an ILLUSTRATIVE spike
  model): priced 97.9 % / 86.8 % / 70.1 % under rev 1.1 with no spike / a +3 % spike at 2 % of cells / +8 % at
  5 %, against 99.7 % / 97.7 % / 90.9 % under rev 1.2. This is `measure_sets.md` §7.4's rule (item 2's sign
  rule, one-sided because these deltas are COSTS, here over the trimmed six, and item 1's group floor)
  WITHOUT item 1's `FRG x base` term: FRG is a run-wide p90 of A/A FRACTIONS of the whole 1 MiB call, so
  `FRG x base / E` charged a per-hit row with the base call's worst-decile A/A (31.6 wb per hit at g 1024 for
  the walk at grid1's FRG 3.09 %, whatever this run's own noise); with it gone FRG has no reader and is not
  computed (D77), which also closes review r5's FRG-population question (CELLS-2). A §7.4 line records the
  format-2 exception (§10.2). The per-hit costs this resolves are §2.3's (`floor_drill.py`). A consistently
  negative per-event cost (an arm faster than its base) is a fixture artifact, `null`, named in the row's
  `source`, never priced. **A delta row never refuses anything by itself**: a `null` row is unpriced, and an
  unpriced candidate cannot qualify (span_pick §The pick 4: safe); Goal 2's floor (below) is what a run of
  unpriced keys fails.
- **The unit's bimodal test**: with the unit's `x_l` sorted ascending (s_0..s_6), bimodal iff for some k in
  2..5 (both clusters >= 2 launches) `s_k − s_(k−1) > gate_e6/2`: a split as large as the unit's own gate.
  `[rev1.2 MEAS-9]` Under per-launch placement a two-phase-class walk is caught by the half gate and this test
  TOGETHER, mostly by the gate (`place_drill.py` A, rev 1.2 breakdown, classes 0/2 %, s 0.5 %: half gate
  63.1 %, bimodal 18.8 %, either 65.9 %, the bimodal test ALONE 2.8 %; at 0/1.5 %: 0.6 % alone). Its own
  contribution is a few percent; it stays because it names the cause (two clusters) where the gate names
  only a size.
- `[rev1 MEAS-7; rev1.1 DRIFT; rev1.2 MEAS-4]` **Drift, per JOB.** With `C_j` = `med` of job j's control
  slopes `u_l` and `C_2` the unit's job's, `drift_j = rhafz(|C_j − C_2| x 10^6, C_2)`; job j's groups are
  REFUSED iff `drift_j > max(G/2, 3 x isqrt_rn(rhafz(K_MED_E6 x (sp2_2 + sp2_j), 10^6)))`, G the UNIT card's
  `gate_e6` (`[rev1.2]` named: J4 and J5 hold other cards; equal today, all 30000), each `sp2` on that job's
  relative control values `rhafz(u x 10^6, med(u))`. **The scale** (review r6 MEAS-4): `|C_j − C_2|` is a
  difference of two 7-launch medians, whose variance is `K_MED` times one launch's per median; `K_MED_E6 =
  210300` is DERIVED (`place_drill.py` B: the lower median of 7 normal launches, 400,000 draws, 0.2103), so the
  second term is 3 STANDARD ERRORS of the statistic. Rev 1.1's `3 x isqrt(sp2_2 + sp2_j)` was on the
  per-launch scale, about 6.4 s.e., and its sentence "smaller drifts are unresolvable by a 7-launch median
  comparison" was false. The factor 3 was rev 1.1's UNMEASURED DEFAULT; rev 1.2's basis is the measured false
  rate: the s.e. term alone refuses a no-drift job 1.1-1.2 % of the time at every s_L (`place_drill.py` B,
  20,000 runs each; the estimated spread's tails put it above a normal 3-sigma's 0.3 %), and with the size
  floor G/2 0.0 % at s_L <= 0.5 % and 0.5 % at 1 %. **Power** (`place_drill.py` B, 4,000 runs each, launch-state
  s.d. s_L): a 3 % drift is refused 100 % at s_L <= 0.5 % and 92 % at 1 % (rev 1.1: 17 %); 2 %: 100 %, 98 %,
  93 %, 56 % at s_L 0.2, 0.35, 0.5, 1 %; 1.5 % (at the floor): about 50 % at s_L <= 0.5 %, 30 % at 1 %. The
  floor G/2 stays the SIZE that matters (below it a drift is read as too small for its non-proportional part
  to matter); the s.e. term keeps a noisy job from being refused for noise. **What it proxies** (review r5
  DRIFT: the common component it measures is the one step 3 cancels): it is a BOX-STATE-CHANGE detector
  between jobs, not a correction. A change between jobs that moves every arm in proportion (frequency)
  cancels in every row; a change that is NOT proportional (memory clock or thermal state, bandwidth-bound
  memchr against the compute-bound walk) moves rows and no control can see it. The control's own move is the
  only observable of the box having changed, and the job is re-measured. Arm-specific drift within a job stays
  in each row's spread. Trigger to revisit the floor or the 3: a drift refusal in the window, or row 1's
  predicted-vs-measured spread (R5.3) correlating with the job a row was timed in.
- `[rev1.2 READY-6, MEAS-7]` **The run record** (`docs/design/memfn/span_cards/slot/run_record.tsv`, the kit's,
  written by the slot harness at the window's end and committed by S2d, §9). `[rev1.3 READY-2]` **It is written
  in two steps, by one writer** (`slot/record.py`): (1) at J1's END, J1 writes the record's `run` section's
  `run_id`, `set`, `code_commit`, `j1_verdict` and `j1_widths` lines and its `j1_cells` section into the
  window's working copy of the record (the run directory's `run_record.tsv`, the window's scratch), and J2p's
  `--ready` reads `j1_verdict` FROM THAT FILE (absent or without a `j1_verdict` line: 75, not yet; `b`: 77,
  never; `a`/`c`: 0); (2) a FINALIZE step (`slot/record.py finalize`, run by the window's last queue job
  `J9` (not a timing job, no clock): its `--ready` reads every other window job's state by `scripts/boxqueue
  state` and answers 0 once none is pending or running, whatever each ended as: green, failed, wait-timeout or
  cancelled by its own 77) writes the `jobs` section (each
  job's end state read from the queue's records, a job with no green end being `never-ran` with its cause),
  `plan`, `floor` and `transcript_sha256`, then the file's final bytes, which S2d commits. So the record has
  exactly one writer, J2p's gate reads a defined file, and a failed or declined job still gets its `jobs` row.
  S2c's witness dry-runs both steps (J1's write on a dry-run record, J2p's `--ready` on each of the four
  states, `finalize` on a dry-run window). `[rev1.3 r9-G6, r9-G3]` **The window facts** (`set`, `rules`,
  `run_id`, `code_commit`, `box`, `isa`, `libc`, `gcc`) are written idempotently at EVERY job's start
  (`record.py window`, from `run.py run`) and again at finalize, so a run whose J1 failed still names its run;
  a record naming another run id, commit or box refuses. finalize maps each job's queue end state by ONE
  declared CAUSE table (first match: green -> `ran`; failed -> `failed`; wait-timeout -> `wait-timeout`;
  cancelled -> `declined-j1b` for J2p when the record's `j1_verdict` is `b`, else `cancelled`; none ->
  `never-queued`; any other state REFUSES), and writes `plan` and `floor` from the DRY RUN's frozen plan
  (`RUNDIR/plan.tsv`, written by the first dry run and required equal by every later one), never a live
  rebuild. `[rev1.3 r9fc-FIX-1]` It also writes the CARD AND POLICY VALUES the run was planned under (sections
  `cards` and `policy`, the frozen plan's verbatim copies of the ver-3 card rows and the policy table's rows,
  with `cards_sha256` and `policy_sha256`, the two tables' sha-256 from the frozen plan's inputs), and the
  estimator reads its estimators, lengths, launches, rounds, units and gates from them alone: two equal records
  with equal cells give one verdict, whatever the live tables say later (est.py's self-test plants a live edit;
  slot sabotage S2937). The slot's estimator reads the record's `jobs`, `plan` and `floor` (never "a cells file exists"):
  it refuses the cells of a never-ran job, a ran job missing a planned cell, a cells file whose `#run_id` line
  names another run, an id disagreeing with its columns and a base other than the family rule's (est.py's
  self-test plants each; slot sabotage (g3), S2936). Everything the verdict reads
  that is not in the set, in ONE machine-readable file in `table_contract.md`'s section shape (TAB fields,
  `#section NAME`, a header line per section):

  | section | columns | content |
  |---|---|---|
  | `run` | `key value` | `set` (`zen4-grid3@1`), `rules` (`kit-grid@3`, the owner of the producer's rules, `measures.md` §3.5¶8a; `[rev1.3 r9-CONTRACT-1]`), `run_id` (§3.2), `code_commit`, `box`, `isa`, `libc`, `gcc` (`[rev1.3 r9-G5]` the draft header's provenance), `transcript_sha256` (the per-round transcript's), `j1_verdict` (`a`, `b` or `c`), `j1_widths` (the widths meeting (b), `;`-joined, else `-`) |
  | `jobs` | `job state cause` | every job J1-J5 and J2p: `ran`, or `never-ran` with `declined-j1b`, `failed`, `wait-timeout`, `[rev1.3 r9-G6]` `cancelled` or `never-queued` |
  | `plan` | `key group job` | every row key the run planned (§2.5's keys as census0 scoped them), its group and job |
  | `floor` | `clause key when` | Goal 2's floor: one line per (clause, key); a clause is met by ONE priced key of its lines; `when` is `always` or `unless-j1-b` (the pair clauses) |
  | `cards` | the card table's columns | `[rev1.3 r9fc-FIX-1]` the ver-3 card rows the run was planned under, verbatim (`run`'s `cards_sha256` is the table's sha-256) |
  | `policy` | `name value reason` | `[rev1.3 r9fc-FIX-1]` the kit policy rows the run was planned under, verbatim (`run`'s `policy_sha256`): the value a card's `-` gate took |
  | `j1_cells` | `cell pattern subject regime width launch ns_e6` | J1's cells, each a median over rounds as §3.4 step 1 (widths 32-512 and `128#b`) |

  Its sha-256 is cited in the set's PROVENANCE.md and in the set header's `run` value (`<run id>
  record:<sha256>`, a provenance key the digest does not cover), and the recompute checks the file against
  that sha before reading it. `[rev1.3 READY-5 (b)]` The three copies are compared: the header `run` value's
  sha equals PROVENANCE.md's equals sha-256 of the record file, and the header's run id equals PROVENANCE.md's
  equals the record's `run_id`; any mismatch refuses (a plant at S2e, §9). The record names its set by `id@rev`, never by digest (the set is written after
  it, at S2e). It replaces rev 1.1's "never-ran groups in PROVENANCE.md prose" and the `slot/j1/` files
  (`verdict`, `j1_cells.tsv`): `slot/j1_rule.py` stays the slot's own derivation of J1's verdict. The floor's
  clauses are written from census0's population (§7) and §1 Goal 2's rules: `byte.<form>` (each `find_byte`
  key its own clause), `hit.<form>` (that form's `random` `find_hit` keys, either density or split),
  `verify.<form>.<cls>` (its `p0` and `p50` keys), `enter.<kind>` (its `NONE` key); 19 clauses at the census
  stand-ins (`outcome_drill.py`).
- `[rev1.1 CELLS-2; rev1.2 READY-6, MEAS-7]` **What the recompute covers** (Goal 3). From the committed set and
  the run record: every row's value, noise and NULL status; every cost row's gate; the unit's gate and bimodal
  test; each job's drift; the set's row list (exactly the plan's keys minus those the rules make absent); J1's
  verdict, RE-DERIVED from the record's `j1_cells` by §3.6's rule (independent of `slot/j1_rule.py`, so a
  slot bug that writes a false (b) is caught); Goal 2's floor over the record's clauses; and the outcome and
  `partial`. Hence **a refused job's CELLS STAY in the set** (the verdict reads them: they are read cells,
  `measure_sets.md` §1.5's sense, amended §10.2) while its ROWS are absent; the control's cells stay (every
  row reads them). **The one input the recompute takes as given** is the record's `jobs` section (which jobs
  never ran), and it is cross-checked: a `never-ran` job has no cell in the set and a `ran` job has every
  cell its plan keys need. Quiet is implied by a cell's presence (§3.3). The control is not a row and has no
  gate of its own: a noisy control shows up in every row's spread, and its drift is gated.
- `[rev1.1 GOAL2; rev1.2 MEAS-2]` **Outcomes: ONE first-match table** (pcrec-decisions-as-first-match-tables;
  rev 1.1's prose let PARTIAL and REFUSED both match and read the floor two ways). A clause is ACTIVE unless
  J1's verdict is (b) and its `when` is `unless-j1-b`. A key is UNPRICED by `text` (its cost row over its
  gate, or its delta row `null`), by `drift:J<j>` (its job drift-refused) or by `never-ran:J<j>`.

  | # | condition (first match wins) | outcome | causes recorded |
  |---|---|---|---|
  | 1 | the unit row fails its half gate or its bimodal test | **REFUSED** (exit 3), no set | `unit` |
  | 2 | some ACTIVE floor clause has no priced key | **REFUSED** (exit 3), no set | `floor:<clause>` per failed clause, with its keys' reasons |
  | 3 | some planned key is absent (its job never ran or was drift-refused, or its cost row failed its gate) | **PARTIAL** (exit 4), `partial 1` | the absent keys, named in the run summary |
  | 4 | otherwise | **FULL** (exit 0), `partial 0` | — |

  The floor is read over EVERY active clause (r6 MEAS-2's reading A): a run missing a priced row-1 key is
  not a set row 1 can price from. Row 3 is therefore reached only when the absent keys meet every active
  clause another way; with today's jobs every job holds a clause, so PARTIAL is in practice J1 (b) holding
  J2p out (`outcome_drill.py`: of 14 constructed runs, row 1 by S4/S4g, row 2 by S3, S5-S8, S10-S12, row 3 by
  S2 only, row 4 by S1, S9, S13; the r5 GOAL2 scenario S6 is REFUSED). `[rev1.3 READY-7]` NOTED: row 3's
  branch "or its cost row failed its gate" is UNREACHABLE today, because every `find_byte` key is its own
  floor clause (`byte.<form>`), so a cost row over its gate always reaches row 2 (`outcome_drill.py` S7:
  REFUSED on `floor:byte.walk-set`, read `walk` under `[rev1.3 S2c-2]`). The branch stays: MEAS-3 keeps the cause list exact for HELD and for a
  later card set with a cost row outside the floor; no PARTIAL set with a failed byte row is expected from
  this run. Rev 1.1's "or nothing but the unit
  passes" is absorbed by row 2 and dropped. A REFUSED run is re-run whole in a later window.
  `[rev1.1 PLACE; rev1.2 MEAS-1, MEAS-2]` **HELD**: a second REFUSED run sharing a TEXT-class cause with the
  first: `unit` (the gate and the bimodal test are ONE class: a two-phase walk trips either, `place_drill.py`
  A's breakdown), or one `floor:<clause>` whose keys are unpriced by `text` in both runs. A `drift` or
  `never-ran` cause is box state or a job failure, never a property of the frozen text, and is never HELD
  (`outcome_drill.py`: S4 then S4g HELD on `unit`; S10 twice HELD on `floor:hit.walk`; S3 twice, S11 twice and
  S7 then S10 re-run). A held cause is a property of the frozen text and the box, not of a run: two runs with
  fresh placements (the run id, §3.2) both refuse a clean unit 0.4 % at τ 0.5 % (`place_drill.py` A2, 20,000
  pairs; 0.6 % had the re-run re-linked the same layout), so no third window is asked; the kit manager rules
  (the unit gate, a D149 constant; the placement scheme; or the card's shape: a denser g, more rounds) with
  the two runs' figures. The placement screen (§3.2) can reach HELD before any window.
- **The run** is the six jobs of one window at one frozen commit (D166: one box, one run, one method
  version), with ONE run id; the id `zen4-grid3` is TAKEN AT COMMIT, so a REFUSED run is re-run whole in a
  later window (a new run id) and nothing is mixed across windows. **Known gap**: noise is WITHIN-window;
  between-window drift (review 2026-10-31-r3 MEAS-7, the bake-off's `s_bw`) is unmeasured. Trigger: row 1's
  predicted-vs-measured spread (R5.3) exceeding the band on its movers.

**`[rev1.1 J3; rev1.2]` The rules on constructed outcomes** (`drill.py` (1), an implementation of §3.4-§3.5
from this text, rev 1.2's NULL and drift rules; each input series is printed beside its result; L = 7,
anchored values with the unit at 10^6; the last rows are `outcome_drill.py`'s):

| outcome | constructed input (`drill.py`) | rule | result |
|---|---|---|---|
| clean | x = 59900, 59950, 60000, 60000, 60050, 60100, 60020; twin x + 60 | cost gate | value 60000, noise 92 (0.15 %): PASS |
| one outlier | the same, launch 6 at 64800 (+8 %) | cost gate | value 60000, noise 92: PASS (the trimmed launch) |
| bimodal (non-unit row) | 60000 x4, 63000 x3 | cost gate | value 60000, noise 2034 (3.39 %): that ROW fails (rev 1.2: alone), the split kept in the spread |
| bimodal unit | 10^6 x4, about 1.03 x 10^6 x3 | bimodal test | REFUSED |
| unit, one outlier | clean x6, one at 1.08 x 10^6 | bimodal test | PASS (a cluster of 1) |
| A/A above spread | clean; twin x + 600 (1 %) | cost gate | noise 604 (1.01 %): PASS |
| A/A above the gate | clean; twin x + 2000 (3.3 %) | cost gate | noise 2001 (3.34 %): the row fails |
| delta, signs mixed | D_l = 1500, −2000, 3000, 500, −500, 2500, 1000 | NULL rule | `null` (−500 survives the trim) |
| delta negative | D_l about −30000, all seven | NULL rule | `null` (a negative cost), named |
| delta clean | D_l about 40 us per call; twin's D about ±4 us apart | NULL rule | med 40.0 us > aa_D 4.0 us: priced |
| `[rev1.2 MEAS-5]` delta, one spike | the clean series with launch 3 at −2 us | NULL rule | priced (the spike is the trimmed launch; rev 1.1: `null`) |
| no drift | control = reference + 50 | drift | 0.03 % vs threshold 1.5 %: kept |
| drift, tight launches | control x 1.03 | drift | 3.0 % > 1.5 %: job REFUSED |
| drift inside a wide spread | reference 189200, 191000, 187500, 190500, 188000, 192000, 186800 (−1.27 %..+1.48 %); control x 1.02 | drift | `[rev1.2 MEAS-4]` 2.0 % < 2.28 % (3 s.e.; rev 1.1's per-launch threshold was 4.96 %): kept |
| end to end from cells | `drill.py` (2): two jobs, 147 cells, events column, `base.walk` named in the delta cells' ids, `ctl` (its slope over its own cells' lengths), the anchor | steps 1-8 | unit value exactly 10^6; libc 63298; the walk's random hit row priced |
| equal-effect sweep | J1, all five widths truly equal, 8 cells | §3.6 rule (m 0.5, k 5) | (b) 0.00-0.01 % over τ 0-4 (`j1_drill.py` Part 2, 20,000 each) |
| `[rev1.2 MEAS-2]` J3 drift-refused | `outcome_drill.py` S3 | outcome table | row 2: REFUSED, `floor:hit.{walk,libc}` (drift:J3; `[rev1.3 S2c-2]` walk-set folded into walk) |
| `[rev1.2 MEAS-3]` walk byte over its gate (`[rev1.3 S2c-2]`: was walk-set) | S7 | outcome table | `find_byte.libc` stays priced; row 2: REFUSED on `floor:byte.walk-set` (text) |
| `[rev1.2 MEAS-2]` J1 (b) | S2 | outcome table | row 3: PARTIAL, the 9 pair keys absent, `partial 1` |
| `[rev1.2 MEAS-2]` every periodic hit row `null` | S9 | outcome table | row 4: FULL (the nulls are published; the floor reads `random` rows) |

### 3.6 [PAIR-LOOKAHEAD-TIME]: job J1, first

The charter (plan.md [PAIR-LOOKAHEAD-TIME]): sweep w in {32, 64, 128, 256, 512} on union-select and the
query-string pair on the two bench subjects' shapes, ONE bounded effort (pcrec-one-pass-loss-chasing), after
R-30's abi 94 (DONE). It is the trigger's "measurement-set revision for the pair card".

- **What is timed.** The kit's PAIR text with the declaration's width literal substituted (`ofs_pair_decl`,
  `ofsskip.c:275-279`; `[rev1 PREMISE-13]` the generator asserts the `<h>wa = 128, <h>wb = 128` declaration,
  `<h>` the site's handle prefix: fn-pair writes `wa = 128, wb = 128`, a window B-pair writes
  `rx_mf1_wa = 128, rx_mf1_wb = 128`, and an unmatched declaration refuses the dry run), so neither the kit
  nor pcrec gains a lever (pcrec-test-harness-minimal). Subjects: the bench's two subject files, read-only
  from the sibling checkout's published data (never its ledgers; pcrec-ask-bench-dev), regimes throughput
  (1 MiB find-all) and short (1,024 records); `[rev1 MEAS-1]` one twin, `128#b`, per cell.
  `[rev1.1 PLACE]` Every width's artifact and the twin take a fresh placement per launch (§3.2).
- `[rev1 MEAS-8; rev1.1 meas-5 (g, h)]` **What it decides, by a pre-registered rule.** Per cell c and width
  w != 128, the paired per-launch relative difference `r_l = rhafz((t_l(w) − t_l(128)) x 10^6, t_l(128))`
  (same launch, so the launch cancels). `aa = med_l(rhafz(|t_l(128#b) − t_l(128)| x 10^6, t_l(128)))` (a
  per-launch fraction, then the median); `sp2(r)` is §3.4 step 6 on the r_l. `[rev1.2 MEAS-6]` w **beats**
  128 on c iff every r_l < 0 and `2 x |med(r_l)| > isqrt_rn(aa^2 + sp2(r))` (a margin m = 0.5, integers
  only); **loses** symmetrically. Then: **(b)** some w beats
  128 on at least 5 of the 8 cells and loses on none: a D186 UNIT change is filed (its own deny, abi event, G1
  at both layers), naming every w that meets it (several: the unit change's design picks; the sweep only shows
  a retune is worth filing); it is NOT stage 2. **(a)** no w beats 128 on any cell: the comment in `ofsskip.c`
  changes from "its TIME is an UNMEASURED DEFAULT" to MEASURED with this job named (a kit source comment that
  reaches no artifact: no byte moves). **(c)** otherwise: accept 128, MEASURED, and record the cells where a
  width beat it. `[rev1.2 MEAS-6]` **How m and k were chosen** (replacing rev 1.1's margin 2 and "5 of 8",
  whose stated reason, (b)'s false rate, could not have selected them: it is ~0 at every (m, k)). The choice
  rule, stated in `j1_drill.py` before its run: among m in {0.5, 1, 1.5, 2} and k in {4, 5, 6}, keep those
  whose false (b) with no effect is at most 0.1 % at EVERY τ in {0, 1, 2, 4} (20,000 trials each), then take
  the highest power at a true effect of 4 within-launch s.d. at τ 1 (4,000 trials). Result (Part 2):
  **m 0.5, k 5**: false (b) 0.00 % at τ 0 and 1, 0.01 % at τ 2 and 4; power at effect 4: 100 % (τ 0),
  95.1 % (τ 1), 33.0 % (τ 2); at effect 3: 99.1 %, 60.0 %, 10.1 %. Rev 1.1's m 2 / k 5: 9.9 % at effect 4,
  τ 1; the r6 critic's starting point m 1 / k 5: 90.5 %; m 0.5 / k 4 fails the false bound (0.95 % at τ 4).
  The all-seven-signs test carries the false rate, so the margin can be small. The 0.1 % false tolerance is
  the one CHOSEN constant: UNMEASURED DEFAULT (D149), a risk choice (a false (b) files a unit change whose
  own G1 then refuses it); m and k are DERIVED from it by the stated rule. Trigger: a (c) outcome whose beating
  cells concentrate on one subject regime, or a (b) whose unit change G1 refuses.
- `[rev1.1 J1-WIN; rev1.2 READY-6, MEAS-7]` **(b) inside the window.** J1 writes its verdict as one line in
  its log and into the run record's `run` section (`j1_verdict`, `j1_widths`), its cells into the record's
  `j1_cells` (§3.5; rev 1.1's `slot/j1/verdict` and `j1_cells.tsv` fold into the record), the rule derived from
  them by `slot/j1_rule.py` and RE-DERIVED independently by the recompute (MEAS-7). The PAIR arms are NOT in J2 or J3: they are job **J2p**
  (`after` J1), whose `--ready` reads that verdict and answers 77 (never) under (b) (`[rev1.3 READY-2]` from
the window's working copy of the run record, written at J1's end; the finalize step writes the rest, §3.5). The set is then PARTIAL
  (§3.5: J2p never ran) naming `find_byte.pair` and every `find_hit.pair.*` key, which join the NEXT set id
  after the unit change lands (their form hash moves with the literal). Goal 2's floor then reads "pair
  unless J1 (b)" (the record's `unless-j1-b` clauses). Nobody reads J1's verdict by hand between jobs.
- **Drilled** (`j1_drill.py` Part 1, rev 1.1's m 2 / k 5, kept as the record of the placement reading; the
  launch effect and each arm's within-launch noise unit normal; placement s.d. τ in the same unit, a width's
  placement shared by its pattern's 4 cells within a launch; the drill's r_l are ABSOLUTE differences, the
  text's relative, equal to first order at small relative noise). No true effect, τ 0: (b) 0 of 20,000. One width truly better by 2, 3, 4, 6 within-launch s.d. on every cell, τ 0:
  (b) 0 %, 12 %, 81 %, 100 % (5,000 each). With placement (4,000 each): rev 1's reading (one draw per width
  for the run) gives a FALSE (b) of 0.03 %, 1.15 %, 4.53 % at τ 1, 2, 4; rev 1.1's per-launch draw gives
  0 % at every τ. The price was power: under m 2 / k 5 a true effect of 4 was filed 9.7 % at τ 1 and 0.1 % at
  τ 2 (rev 1: 39 %, 19 %). `[rev1.2 MEAS-6]` Rev 1.1's "an effect smaller than a width's own placement
  spread is not one an artifact would see" did not cover that loss (at τ 1 the effect 4 is about 2.8x the
  per-launch placement s.d. of r) and is withdrawn; rev 1.2's m 0.5 / k 5 files it 95.1 % at the same false
  bound (above).

### 3.7 `[rev1 MEAS-14, PREMISE-11; rev1.1 J3, CELLS-1 (d), J1-WIN]` Box time

Per point-launch 0.95 s: regime_eval's per-launch figure for a streamed or >= 1 MiB grid1 group
(`regime_eval.md`, "0.95 s per launch", used by `r17b_prime.md:2063`), a whole-artifact figure that
overshot grid2's estimate (`r17b_prime.md:2061`), so an upper-bound-style estimate here. 7 launches, fixed
(§2.1): no rerun allowance. A point is one (arm, length) timed per launch; the control's three lengths are
three points of every job. Builds, links and answer gates run in `--dry-run`, OUTSIDE the clock. Counts by
`tree_drill.py` B (its inputs: 8 census verify pairs over 2 cls, 3 consumer kinds, rev 1's stand-ins until
S2b's census fixes them).

| job | content | points | timed (min) |
|---|---|---|---|
| J0 census | compile-only (§7); NOT a timing job, no window | `[rev1 PREMISE-12]` (R-33's job 240-kit-r33-sweep: 5,492 compiles, `docs/dev/lanes/r33_report.md` "Sources"; 14 s by the queue log) | ~1 |
| J1 sweep | ctl 3 + 8 cells x (5 widths + `128#b`) | 51 | 5.7 |
| J2 unit + byte | ctl 3; unit group walk, walk#b x 3 lengths (6); byte group libc, walk-set and twins x 3 lengths (12; `[rev1.3 S2c-2]` rev 1.2's shape: walk-set is the walk, S2c's plan is the record) | 21 | 2.3 |
| J2p pair | ctl 3; pair, pair#b x 3 lengths (6); `base.pair` (1); hit groups pair x 2 landings x {one, alt} x 2 gaps, with twins (16) | 26 | 2.9 |
| J3 hit | ctl 3; `J3.base`: base.libc, base.walk, base.walk-set (3); 4 groups (2 landings x 2 gaps) x (libc one, walk one, walk-set alt, with twins: 6) (`[rev1.3 S2c-2]` rev 1.2's shape: walk-set is the walk, S2c's plan is the record) | 30 | 3.3 |
| J4 verify | ctl 3; 8 census (form, cls) pairs x 2 passes x (arm + twin) (32); 2 `base.null.<cls>` | 37 | 4.1 |
| J5 enter | ctl 3; 3 kinds x 3 entries x (pass, pass#b) (18); 9 `base.fail.<kind>.<entry>` | 30 | 3.3 |
| | **timed total** (J1-J5, J2p) | 195 | **21.6** |

**The window to ask for: 35 minutes** (21.6 timed; six job starts, each behind the >= 55 s two-sample quiet
gate, about 6; slack). The set's cells: (195 − 51) x 7 = 1,008 (J1's are not in the set; `[rev1.2 READY-6]` they are in the run record, §3.5). `verify` and
`enter` counts are the census's to fix (§7); the total moves by minutes. J6 (S2g, HELD) is not in this window.

### 3.8 `[rev1 SLOT-1, CONTRACT-1]` How the set is assembled

1. The slot harness writes ONE draft set (format 2, §5; id `zen4-grid3`, rev 1; method `kit-grid@3`; tier
   `scratch`; `[rev1.1 TARGET]` class `x86_64/zen4`, `compiler` `gcc 15.2.0 -O2 -march=x86-64
   -mtune=generic`, §2.7) under the lane's scratch directory, never under `memfn/data/sets/`
   (`tests/memfn/finder_check.py` digests every `.tsv` there with the format-1 rule; it stays format-1 only,
   guarded by sabotage (o)). Its `rows` are §3.4's values, noise and NULLs (`[rev1.2 READY-8]` `deps`
   `kit:form.<id>=<hash>` on every form-bearing row, `-` on `enter` rows, §2.4; `[rev1.3 r9-G5]` the hash is
   the FOLD the dry run read from the very fixture binary that rendered the timed texts, kept in each job's
   `cell_text.tsv`, never a separately built binary; a class with no majority shape is tagged `lower-bound`;
   the header's `box`, `isa`, `libc` and `compiler` come from the run record's window facts, never literals;
   a REFUSED outcome writes NO draft; `[rev1.2 READY-1]` `inputs`
   `-` on every row, each `delta` row's base named in its cells' ids, §3.4 step 1); its **`cells` section**
   holds every cell §3.4 step 1 defines for J2-J5, refused jobs' and gate-failed rows' included (§3.5); its
   header's `run` key is `<run id> record:<sha-256 of the run record>` (`[rev1.2 READY-6, MEAS-1]`); its
   `values_digest` comes from `tests/knowledge/ks_ref.py digest`. The draft is written at the window's end
   (S2d), and S2d's report names its scratch path and sha-256, which S2e checks before step 2.
2. `pcrec --list-measurements=draft.tsv > set.tsv` (`[rev1.2 READY-5]` the `=` form; the bare flag prints the
   index and leaves `draft.tsv` a stray argument, `cli/main.c:1567-1573`): the C loader re-derives the digest (a mismatch refuses)
   and the canonical writer writes the file (canonical by construction, `measures.md` §6¶2), as grid1's
   PROVENANCE.md records. `measure_store/from_interim.py` is NOT used (its one-time grid1 path stays
   unchanged).
3. `measure_store/zen4-grid3/1/{set.tsv, PROVENANCE.md}` (PROVENANCE: the run, the method card version, the
   slot harness's commit, D188's facts as §2.7 records them, `[rev1.2 READY-6, MEAS-1]` the run id and the
   run record's path and sha-256 (the record holds the never-ran jobs, J1's verdict and cells and the floor,
   §3.5), the per-round transcript's location and sha-256: rounds no row reads are not committed,
   `measure_sets.md` §1.5); `[rev1.1 INDEX]` the `index.tsv` row with `supersedes` EMPTY (zen4-grid1 is another method@ver,
   "not compared", §2.1) and `status` `current`, zen4-grid1's row staying `current` (no code reads either
   column; `measure_sets.md`'s "Supersession is recorded in `index.tsv`" applies within one method);
   DEFAULTS per §8.3; `make gen-measures`; the drift gate `make gen-tables && git diff --exit-code`.
4. **The recompute check** (Goal 3): `tests/knowledge/` gains a python check, written from `measures.md`'s new
   sections 3.4-3.5 and this note's §3.6 (J1's rule) and importing nothing from the slot harness, that
   re-derives from each committed set's file `[rev1.2 READY-6]` and its run record (located and sha-checked
   through PROVENANCE.md) what §3.5 "What the recompute covers" lists, exactly. `[rev1.2 standing question]`
   It reads the set through `tests/knowledge/ks_ref.py`'s parser (imported): independence is owed to the
   SLOT harness, which shares nothing with ks_ref.py, not to pcrec's one python spec reader, so the tree
   gains no fifth set parser. `[rev1.1 CELLS-3]` Its population is every committed FORMAT-2 set (keyed on
   `format`, not a name list), counted and floored at S2e (1: zen4-grid3); format-1 sets are counted as
   skipped by that rule.

`[rev1.1 EMBED]` **The embed: cell-less (R-35 (d)).** Main ruled that the libpcrec embed OMITS the per-launch
`cells` section; the committed `set.tsv` keeps it for the recompute and `--measures=FILE`. Rev 1.1's reading,
for main's S2e review (§10 item 6):
- **The rule is general**: every embedded set is built (`make gen-measures`) from its file WITHOUT the rows of
  section `cells` (its `#section cells` line and column header kept, so the text is a loadable set), text and
  pre-parse alike (`measures.md` §8¶2 amended, S2e). No per-set flag. `[rev1.2 READY-4]` **Who strips.** The
  embedded TEXT is written by `scripts/embed_text.sh` (`Makefile` `gen-%`, the text step), whose contract
  "embeds each FILE's bytes, unmodified" is shared with the findings store and STAYS: `gen-measures` gains a
  STRIP step before it (an awk over each set file, dropping the `cells` section's data rows, into the build's
  generated-text directory), and `embed_text.sh` embeds the stripped files unmodified. `[rev1.3 READY-1]`
  **Layout and hook.** `embed_text.sh` takes each set's NAME from its PATH (`<id>/<rev>/set.tsv`), so the
  stripped copies keep that shape: `$(BUILD_DIR)/gen/meas/<id>/<rev>/set.tsv`, and the names (`zen4-grid1@1`)
  do not move. `gen-%` is ONE static-pattern rule shared by `findings` and `measures` (K2), so the strip is a
  per-store row: `KS_TEXTSRCS_measures` names the stripped copies, produced by their own rule from
  `measure_store/*/*/set.tsv`, while `findings` keeps its committed files. Three texts say the embed is the
  committed file's bytes and are amended at S2e (D80 where caller-facing, else wording): the `Makefile`'s
  K2/B1 comment block, `scripts/embed_text.sh`'s header ("a mechanical ENCODING of committed text ... compares
  it with its source byte for byte": now the stripped copy for `measures`), and
  `tests/knowledge/meas_store_check.c`'s header ("the runner compares it with the committed file, byte for
  byte": now with the runner's stripped copy). The PRE-PARSE is
  `scripts/ksgen.c`'s: it reads the committed file, records its cell count as the set's `file_cells`, and
  pre-parses it without its `cells` rows, so the pre-parse equals a fresh parse of the stripped text.
- **Identity.** `values_digest` never covered the cells (`measures.md` §3.3¶1), so the embedded copy and the
  committed file share one identity `id@rev:digest`, by construction; `index.tsv`'s file sha-256 covers the
  cells. The spec says so in §3.3 (a sentence, S2e).
- **The listing says it.** `--list-measurements` (no value) gains a column `file_cells`, `[rev1.2]` APPENDED
  after `source` (`run_measures_tests.sh:84` reads `default_for` positionally, `$8`): the committed file's
  cell count as ksgen recorded it, which the embed does not hold (0 for grid1). `--list-measurements=NAME` resolved from the embed
  prints its canonical view with an EMPTY `cells` section (still a loadable set with the same digest, §6¶2);
  the full view is `--list-measurements=FILE` on the committed file. Both are caller-visible: §6¶1/¶2 hunks
  at S2e (D80), and Goal 1 counts the column.
- **No embed reader needs the cells.** Readers of the embedded store by grep at S2e: `memfn_measures` (rows
  only, §4.2), the listing, `meas_store_check.c` (pre vs fresh, both cell-less), `--measures=NAME` stamps
  (rows' digest). The recompute (Goal 3) and `--measures=FILE` read the FILE. S2e re-greps and lists them.
- `[rev1.2 READY-3]` **The checks that compare the embed with its file**, each red in the CORRECT build under
  the cell-less rule as written today, re-aimed at S2e in `tests/knowledge/run_measures_tests.sh`'s STORE
  section (for every `measure_store/*/*/set.tsv`):
  (i) R4 (:52-57, today `--list-measurements=<id>@<rev>` `cmp` the file): runs on the FILE path
  (`--list-measurements=<the set.tsv path>` `cmp` the file: every committed file is its own canonical view),
  plus the NAME's view `cmp` the file with its `cells` rows dropped by the runner's OWN awk;
  (ii) R5 (:58-64, the NAME's `--view=decoded` against `ks_ref.py decode` of the FILE): the FILE's decoded
  view against `ks_ref.py decode` of the file, and the NAME's against `ks_ref.py decode` of the runner's
  stripped copy;
  (iii) the embedded-text compare (:104, `meas_store_check.c`'s `<name>.text` `cmp` the file): against the
  runner's stripped copy (its own awk, sharing no source with the strip step);
  and two new named assertions: every embedded set's pre-parse holds 0 cells, and the listing's `file_cells`
  equals the file's cell count counted by awk. `[rev1.3 READY-6]` **The 0-cells assertion's mechanism:** the
  runner counts the `cell` lines of the `.pre` DECODED view `meas_store_check.c` already writes per embedded
  set (`ks_measures.c`'s decoded writer emits one `cell` line per cell) and asserts 0; `meas_store_check.c`'s
  three-field output and its runner's reader do not change. **Detectors that move**: S1241 (the embedded text one byte
  short; detected by (iii)) and S1232 (the canonical writer drops cells; detected by R4) keep their plants;
  their DETECTORS change, so each is re-verified for intent at S2e (S1232 is now caught by R4 on the FILE
  path, where a dropped cell section differs from the committed file), not only its anchor re-read.
  **Wording**: `tests/knowledge/CLAUDE.md`'s STORE description, and `measures.md` §6¶2's last sentence
  ("Every committed set file equals its own canonical view") gains "loaded as a FILE; a NAME resolved from the
  embed prints it without its `cells` rows" (S2e, D80).
- **Bytes** (`tree_drill.py` D; inputs: grid1's file and .inc sizes from the tree, `size -A
  build/obj/core/measures.o` and `size -t build/libpcrec.a` on main's build). grid1's embed is 23,788 B of
  libpcrec (305 B per row or card). zen4-grid3 projected: 49 rows + 4 cards, about 16 KB cell-less; its 1,008
  cells would have added about 274 KB (`[rev1.2]` with the base field in delta cells' ids), 15.3 % of
  libpcrec.a's 1,834,467 B. `measure_sets.md`'s sizing
  sentence ("47 rows is about 6 KB of text per set and 15 KB with the pre-parse; the cells and cards add about
  4 KB. Ten committed sets stay below one `fold_tables.inc`") is replaced at S2e (§10.2): ten grid1-size
  embeds are about 232 KB against fold.o's 24 KB of tables, so its last sentence was already false by ten
  times.

## 4. The noise channel (an MF abi event)

### 4.1 The seam

`mf_measure` (`memfn/include/memfn.h:1226-1231`) is {key, value_e6, unit, source}. It gains, APPENDED LAST:

```c
typedef enum { MF_NOISE_UNSTATED = 0, MF_NOISE_MEASURED, MF_NOISE_UNMEASURED } mf_noise_state;
    uint8_t     noise_state;  /* mf_noise_state; UNSTATED is refused              */
    int64_t     noise_e6;     /* 1-sigma, the row's unit x 1e6; 0 unless MEASURED */
```

- **A state, not a sentinel.** A missing noise is UNMEASURED, never 0 (span_pick.md:182), and a measured
  noise may round to 0; the house rule "an UNSTATED zero is refused" (memfn/CLAUDE.md) then FORCES every
  constructor to state it: `[rev1 PREMISE-9]` the THREE positional constructors found by grep
  (`cli/main.c:160`, the `--harness=measures=FILE` reader; `src/gen/memfn_sites.c:89`;
  `tests/memfn/arm_fixtures.c:1562`) zero-initialize the new fields, so an unedited one is refused at
  `mf_art_begin`, not silently "measured 0".
- **No `n`.** No reader would read it (D77); it stays a listed provenance column.
- **The kit's check** (`compose.c` `measures_check`, :892-905) adds: state in {MEASURED, UNMEASURED};
  MEASURED: 0 <= noise_e6 <= MF_MEASURE_MAX; UNMEASURED: noise_e6 == 0. Refused, never clamped.
  `[rev1 CONTRACT-5]` That refusal is unreachable from a LOADED set: pcrec's loader refuses a noise past
  10^15 first (§4.4), so a bad file is a load error naming the file, never a kit "internal error" on every
  compile. The VALUE half of the same shape (a `value_e6` past MF_MEASURE_MAX loads, then every compile is
  an internal error) is pcrec's **K138** (`docs/dev/known_issues.md`, main's); this note does not fix it.
  `[rev1.1 BOUND]` **The bound's homes.** `ks_measures.c` may include only libc, `core/ksrc.h` and
  `core/ks_measures.h` (its DEPENDENCY RULE, enforced by `tests/core/ksrc_deps_check.sh`, S1242), and the kit
  links nothing of pcrec's, so neither side can READ the other's literal: there are TWO homes, `memfn.h`'s
  `MF_MEASURE_MAX` and a new `ks_measures.h` constant `KS_MEAS_MAX` (10^15, S2a), and ONE check: a test
  translation unit that includes both headers and `_Static_assert`s them equal (built by `make test`'s
  measures section, so a drifted copy fails the build of the check). The loader's noise refusal and, when it
  lands, K138's value refusal both read `KS_MEAS_MAX`. K138's prescribed form "read from the seam, not
  copied" cannot be met under the dependency rule; its amended form ("one equality check over the two
  homes") is for main (§10 item 11). **The square.** `MF_MEASURE_MAX` is a SHAPE bound for SUMS ("the
  finder's comparisons add at most four values", memfn.h); noise is used SQUARED in the band's quadrature
  (span_pick's "quadrature sum ... `(coef_a - coef_b) x noise`"), and (10^15)^2 is past int64 and the
  products `coef x noise` past int128 at the bound. No noise bound is derived here for the square: stage 2
  has no reader (D77). Row 1's band arithmetic is its design item (§10.3): every intermediate bounded from
  the stated bounds, never an int64 square of a raw noise (for scale: with coefficients <= 10^6 and <= 100
  cards per comparison, int128 sums of squares hold iff `noise_e6 <= 10^12`).
- `[rev1 COST-4]` MF_SITE_ABI takes **the next free number at landing** (23 at rev 0's base; another lane may
  take 24 first, `alt_normal_form.md` names a future crossing): a layout move, no MF_VOCAB, no MF_CLASS_V;
  the history comment at memfn.h:39ff gains its entry. MF_SITE_ABI reaches no text (its only src use is
  `s->abi =`, `memfn_sites.c:406`), so no pcrec byte moves. Kit readers of `mf_measure` by grep:
  `compose.c:895` (the check) and `finder.c:440-451` (value lookup, unchanged); no kit row reads noise until
  row 1. `[rev1 CONTRACT-9]` Seam layout: `measures_check` walks `rows[]` at `mf_art_begin` with the new
  stride BEFORE the only abi field (`mf_site.abi`) is checked at `mf_define`; with pcrec and the kit built
  from one tree that is unreachable, and this note does not claim MF_SITE_ABI guards it.

### 4.2 pcrec's fill (`src/gen/memfn_sites.c` `memfn_measures`)

`[rev1 PREMISE-8, CONTRACT-2]` **On the shipped loader path, noise reaches the kit only from a set whose
digest covers it** (format 2, §5): the path is `memfn_measures` over a set `ks_measures.c` accepted, which
recomputes the digest. A format-2 row with a parsed noise is MEASURED; `-` is UNMEASURED; EVERY row of a
format-1 set is UNMEASURED, whatever its text column says, because a format-1 file with invented noise and
the committed values has the committed digest and is not refused by no-shadowing (`measures.md` §5¶4), so
its noise is not identity-bearing.

`[rev1 SLOT-6]` **The two test levers hand UNMEASURED always.** The harness reader (`cli/main.c:93-175`,
`--harness=measures=FILE`) copies `values_digest` verbatim and reads no `format`; `arm_fixtures.c`'s
`fd_load_set` reads key and value only, with no digest at all. Neither can enforce the rule, so neither
hands noise: both state `MF_NOISE_UNMEASURED` on every row. The MEASURED path's witness is `--measures=FILE`
(§9 S2a), which goes through the loader. The harness reader's own comment retires it "until [MEASURE-SET]
M0's loader", and M0 is on main: retiring it is NOT done here (its readers are tests outside this unit),
noted for main (§10 item 6).

`[rev1 CONTRACT-8]` **The MFMEAS trace record** (`meas_record`, :123; built only with `PCREC_CAND_TRACE`)
gains (i) the count of MEASURED rows and (ii) a TEXT digest of the handed triples: FNV-1a-64 over the lines
`key TAB state TAB value_e6 TAB noise_e6 LF` in canonical key order, 16 lowercase hex (`[r8 SEAM-1]` the handed
VALUE joins the line: a record scoped to the noise alone left a wrong handed value unwitnessed). `[rev1.1 MFMEAS]` **The handed
population** is the fill's, stated: `memfn_measures` hands only rows whose key starts `kit.` AND whose value is
not empty (`memfn_sites.c:86-87` skips non-`kit.` keys and `null` rows), so the digest covers exactly those
rows, and `tests/knowledge/ks_ref.py` computes the same digest from the FILE with the same filter written
from this sentence (and the spec's §4 hand rule, which gains it, §4.4); S2a's witness compares the two. The
two new fields are APPENDED after the record's existing `%p` columns, so `tests/compound/run_part_measures.sh`
(:64-90, which reads MFMEAS positionally: `$2` role, `$3` stamp, `$4`/`$5` the addresses) keeps its columns;
it is listed as a reader (§5, §8.2) and re-run at S2a. Unlike the
record's two `%p` addresses, the digest survives a write/read across processes. It is what sees a wrong
column, scale or sign that a state count cannot (the S983 column-swap class, `measure_sets.md:1551`).

### 4.3 `[rev1 MEAS-13, CONTRACT-6, COST-1, SLOT-10]` Derived rows: `-` noise, no rule

Rev 0 added a per-derivation noise column to `measures.md` §3.2 (quadrature rules) as a STORED, RECOMPUTED
field. That was a new recompute engine (no derived-value evaluator exists in C or python today; §3.2¶2 forbids
reader recompute) with population zero in zen4-grid3 and no reader, while §4.6 deferred a seam field on the
same D77 ground. **Ruled, strong form: derived and fitted rows carry `-` noise (UNMEASURED) in format 2**
until a format-2 derived row has a producer AND a reader (D77). No §3.2 noise column, no C or python
evaluator, no fixture for it; rev 0's sabotage (6) is dropped. The loader enforces the rule structurally:
format 2 refuses a numeric noise on a `derived`, `fitted` or `null` row (§4.4, a §7 row), so a FILE set
cannot hand a noise the format does not define. The general form this points at is filed as an unlock
(§12.1). R-35's "derived noise by quadrature" is answered as: not until a derived row has a reader; R-35's
"Not asked" leaves the shape to the kit.

### 4.4 Spec and design hunks (same commit as the seam, S2a, unless named)

- `docs/spec/measures.md` (D80; numbers by letter, never renumbered, docs/spec/CLAUDE.md): §2.1¶1's `format`
  row (`1` or `2`) and a new ¶1a (what format 2 changes); §2.2¶3a (format 2: `noise_e6` is `-` or a
  non-negative integer in value_e6's one spelling, at most 10^15 `[rev1 CONTRACT-5]`; `-` on a `null`,
  `derived` or `fitted` row `[rev1 MEAS-13]`); §3.3¶1a (the format-2 digest, §5); §6¶3a (the decoded view,
  §4.5); §7 table rows (a misspelled or negative noise; a noise past 10^15; a numeric noise on a null,
  derived or fitted row; `format` outside {1, 2}). `[rev1 SLOT-1]` NO `raw.tsv` paragraph: §8¶1 unchanged.
- `[rev1.1 CELLS-1, TARGET, MFMEAS]` also at S2a (the format's own text): §2.2¶1a (format 2's `cells` adds
  the column `events` after `round`: an integer or `-`; `round` may be the literal `med`); §3.3¶1a also
  folds `class` (§5); §4's hand rule gains "only `kit.` rows with a value are handed" (the filter the MFMEAS
  digest states).
- `[rev1 MEAS-5, SLOT-1; rev1.1 CELLS-1, CELLS-3]` at **S2c**: `measures.md` new §3.4 (the estimator, §3.4
  here: the `lengths` grammar `slope X1,X2,X3` / `delta LEN`, parsed on format-2 sets' cards only; the cell
  columns' meanings, group and arm naming, launch identity, `[rev1.2 READY-1]` the cell id grammar and "a
  measured row's derivation lives in its cells" (the base on the delta cells' ids), steps 1-8) and §3.5 (§3.5
  here: gates per row, the paired NULL rule over the trimmed six, bimodal, drift in standard errors, what the
  recompute covers, the first-match outcome table over "the producer's declared floor ... in a run record
  cited by sha-256 from PROVENANCE.md", generic: no kit clause, key or J1 text); new paragraph 2.2¶5: a
  format-2 set carries in `cells` the cells its rows and its verdict read (refused groups' included);
  `[rev1.2 READY-1]` **§2.2¶3 is NOT amended** (rev 1.1's hunk "inputs names its ONE base arm" is withdrawn:
  "only a `derived` or `fitted` row names inputs" stays true, so the loader, `ks_ref.py`, §7 and mfixtures are
  untouched); §2.3¶2 unchanged and still true (no placeholder, §2.4).
- at **S2e**: `measures.md` §5¶6 and §8¶3 (the default and sets today, §8.3); `[rev1.1 EMBED]` §8¶2 (the
  embed omits `cells`), §3.3 (the identity covers rows, so the cell-less embed and the file share it),
  §6¶1 (the `file_cells` column, appended after `source`), §6¶2 (a NAME's canonical view from the embed has
  an empty `cells`; `[rev1.2 READY-3]` its last sentence: a committed file equals its own canonical view
  loaded as a FILE).
- `docs/design/measure_sets.md` (each with a `[s2]` revision line): §4.1 "No provenance columns" amended:
  `noise_e6` is handed from format-2 sets (R-35), `n` and the rest are not (S2a); `[rev1 CONTRACT-9]`
  :490-494 "What the digest excludes ... `noise_e6`" made format-1-only (S2a); §1.4's "the checker's
  recompute" and §1.5's "Cells no row reads are not committed": a method whose estimator normalizes per
  launch recomputes `value_e6` from its cells, not from `abs_ns_e6`, and its read cells include those its
  VERDICT reads (S2c); §7.2 `lengths`/`aa_rule` (S2c, §2.4); §7.3/§7.4: the M3 driver implements
  `measures.md`'s new sections 3.4-3.5, and §7.4 notes format 2's paired floor (S2c, §3.5); §3.6 (S2e, §8.3);
  the sizing sentence (S2e, §3.8); `[rev1.2 READY-3]` §8.3 "Embedded = committed" (S2e: embedded = committed
  minus its `cells` rows).
- `match_api.md`: **NO hunk.** Its measures sentences (§6¶14a, §6.3.10¶12-¶13) state the stamp's grammar
  `id@rev:digest` and that no kit row reads a set: both stay true through stage 2, and the digest's
  definition is `measures.md`'s (§3.3), which carries the change. R-35 names a match_api hunk: For main
(`[rev1.1 XREF]` §10 item 3).

### 4.5 The pcrec-side code (main reviews; the same commit)

`src/core/ks_measures.{c,h}`: `format` 1 or 2 (today refused unless 1, `ks_measures.c:305`); on format 2
`noise_e6` parsed into a new `KsMeasRow.noise_e6` (KS_MEAS_EMPTY for `-`) with the spelling, bound and
row-status refusals; a second digest role beside the first (§5); the canonical writer writes noise back in
its one spelling. `[rev1 CONTRACT-7]` **Format 1**: `KsMeasRow.noise_e6` is KS_MEAS_EMPTY on every row (the
column stays free provenance text, never parsed), and the decoded view gains NO field for it, so grid1's
decoded view is byte-identical; format 2's decoded view gains one field per row, the parsed noise.
`[rev1 CONTRACT-3]` `scripts/ksgen.c` writes the new field POSITIONALLY into the committed pre-parse
`src/core/measures_table.inc` (`:347-358`), so it is in the package: without it the pre-parse holds 0 where a
fresh parse holds KS_MEAS_EMPTY. `[rev1.1 KSGEN]` `tests/knowledge/meas_store_check.c` compares DECODED
views (pre vs fresh, :72-80), and format 1's decoded view has no noise field (CONTRACT-7), so at S2a, with
grid1 the only committed set, a ksgen that leaves the field out was INVISIBLE. S2a adds to it a RAW-ROW
compare: for every embedded set, every `KsMeasRow` field of the pre-parse (the noise included, as an
integer) against a fresh parse of the same text, so KS_MEAS_EMPTY vs 0 on grid1's rows is a red (sabotage
(r)); and one format-2 fixture store (`tests/knowledge/`, a two-row set) run through ksgen, so the
format-2 path is exercised before S2e.
The `.inc` regenerates for grid1 too (its `-` noise as KS_MEAS_EMPTY): a committed derived file that moves
(§8.2), its source `set.tsv` untouched. The measures KsKind row names ONE digest role
(`ks_measures.c:724-725`, the role's domain hashed first by `ksrc.c:533`); format 2's role is chosen by the
set's `format`, and the kind row's `.item`/`.stamp` role stays format 1's (no generic reader of `.item`
exists today; the choice is recorded so a future one reads the right role). `src/gen/memfn_sites.c` (§4.2),
`cli/main.c` harness reader (UNMEASURED, §4.2), `src/dump/measures_dump.c` (the decoded view).
`tests/knowledge/ks_ref.py` (the independent python digest, parser, decoded view and §4.2's triple digest)
and `mfixtures.py` (`[rev1 CONTRACT-9, COST-6]` its refused-format row `("format", hdr("format", "2"), ...)`,
:177, moves to `3`; new format-2 fixtures, §9).

### 4.6 Not here: the bundle's sampling noise

span_pick.md:234-238 puts B's sampling noise (block bootstrap, "pcrec STATES it with the rates") on "stage
2's MF_SITE_ABI event". **Decision: deferred to its producer.** No producer exists (`pcrec-analyze` writes
no noise; the bundle format has no field), a blind compile's P is an authored prior with no sample, and
row 1's witness compiles with data use the scratch `prose` bundle only. A seam field nobody writes and
nobody reads is built ahead of need (D77). Trigger: [BENCH-WITHDATA]'s held-out bundles or
row 1's with-data band, whichever first; then one MF_SITE_ABI event with its pcrec producer. For main
(`[rev1.1 XREF]` §10 item 2): it amends span_pick.md:237-238's "stage 2's".

## 5. Noise in `values_digest`: set FORMAT 2

- **The event.** `measures.md` §3.3¶1 hashes no provenance column, so noise is outside today's digest;
  span_pick.md:265 offers two exits: noise in the digest, or "a FILE set may not share a committed id".
  CHOSEN: noise in the digest, as a FORMAT version, not a domain swap for every set: **format 2** sets hash
  under domain `pcrec-meas-2` (13 bytes with its NUL, the same length), `[rev1.1 D188A1, TARGET]` then the
  header's `class` value and a NUL (the priced target, D188's fact (b), §2.7: so `id@rev:digest` names it,
  and no-shadowing, which compares digests, refuses a same-id file of another class), then per row the key, a
  NUL, the unit byte, the status byte, `value_e6` LE int64 and `noise_e6` LE int64 (`INT64_MIN` for `-`, as
  for an empty value). Format 1 keeps `pcrec-meas-1` and its rule, byte for byte. The `cells` section stays
  outside the digest in both formats (§3.3¶1); the file sha-256 covers it, and the cell-less embed shares the
  file's identity by that rule (§3.8).
- **Why a format, not a re-digest.** A committed revision never changes (`measures.md` §8¶1). Re-digesting
  zen4-grid1@1 would rewrite its header, its file sha (`index.tsv`), DEFAULTS.log row 1 (`zen4-grid1@1:
  13a6536315af1520`) and its movers file's identity, all for noise it does not carry (68 rows, all `-`).
  Under the format rule **zen4-grid1@1 stays format 1, unchanged: its digest `13a6536315af1520`, its
  sha `d332967c...` and DEFAULTS.log row 1**. The format-1 noise rule (§4.2: never handed) closes the
  no-shadowing hole for it.
- **Every reader of the digest, by grep** (`git grep 'pcrec-meas-1'`, values_digest in code), and what each
  does: `src/core/ks_measures.c:245` and `.h:114` (a second `KsDigest` role; the first's line kept byte for
  byte so `S1244`'s anchor holds); `tests/knowledge/ks_ref.py:91` (format dispatch); `measure_store/
  from_interim.py:31` (`[rev1]` UNCHANGED: grid1's one-time path, unused by stage 2, §3.8);
  `memfn/data/sets/generate.py:79` and `[rev1 CONTRACT-1]` `tests/memfn/finder_check.py:313-324,343-374`
  (format-1 only, over EVERY `.tsv` in `memfn/data/sets/`: UNCHANGED because no format-2 file is placed
  there, §3.8, sabotage (o)); `S1244`, `S1227` (format-1 plants: still valid; format-2 plants, §9);
  `cli/main.c:78,143` and `measures_dump.c:29` (the header key only: unchanged); `memfn_sites.c:95,128`,
  `memfn_stamps.c:290` (the hex: unchanged); `tests/compound/run_part_measures.sh` (a synthetic header's
  text: unchanged; `[rev1.1 MFMEAS]` and the positional reader of the MFMEAS record, whose new fields are
  appended after its columns, §4.2); `docs/spec/measures.md` §3.3, `docs/design/measure_sets.md:476,:490-494,:1594,:1923`
  (text). Every committed digest: one, grid1's, unchanged.
- **No emitted byte or stamp moves, and how that is PROVEN.** The stamp is `id@rev:digest` of the loaded
  set iff a reader consulted it (`measures.md` §4¶2) and no kit row reads a set at stage 2 (§4¶4): every
  artifact's `<PREFIX>_MEASURES` is `""` before and after. `[rev1.1 CENSUS]` Proof: **S2a-S2d**:
  `emit_sweep.py`'s ordinary two-build sweep, byte-identical on every arm (stamps included) against the
  unit's named base; no set changes there, so there is no data-mover census to run. **S2e** (the set and the
  DEFAULTS flip): the DATA-MOVER census. `emit_sweep.py` has no `measures` data kind (`DATA_KINDS =
  ("analysis", "limits")`, its `measures` row "joins at [MEASURE-SET] M1") and `movers/0001.tsv` was written
  by `docs/dev/lanes/m0build/census.py`, not by emit_sweep (`measure_store/CLAUDE.md` and
  `measure_sets.md` say otherwise; both corrected, §10.2). `[rev1.2 standing question]` `movers.py` is the
  THIRD mover census (after m0build's `census.py` and `emit_sweep.py --data`), and S2e IS a DEFAULTS
  transition, the use measure_sets §8.4/§9.3 homes in emit_sweep's `measures` kind, so rev 1.1's "its first
  use is M1's" did not hold. Ruled PLAN (kit manager, r6): stage 2 keeps the copy; emit_sweep's `--data
  measures` REPLACES `movers.py` when the next data-mover census is needed (M1's first set), and main files
  the row (§10 item 12). **The tool: `span_cards/slot/movers.py`**, a copy of m0build's
  census method (the base unit's `build/pcrec` against S2e's head, over emit_sweep's own corpus enumeration
  read through `--list-source`, the five arms c-default, c-utf8, c-vm, ir, facts; rc and stderr compared)
  with its normalization list EMPTY: S2e declares no scaffolding, so EVERY difference, an `RX_MEASURES`
  line included, is a mover. With DEFAULTS flipped in the head, the base compiles under zen4-grid1 and the
  head under zen4-grid3 by default; the census also runs the head with `--measures=zen4-grid1` against
  itself with `--measures=zen4-grid3`. **`movers/0002.tsv` takes 0001's shape**: a `#section header` (`seq
  2`, `class idk`, `old zen4-grid1@1:13a6536315af1520`, `new zen4-grid3@1:<digest>`, `code_commit`,
  `population` with the corpus row and pattern counts and the arms, `movers 0`) and a `#section movers`
  (`artifact moved first_difference`, empty), its header comment naming `span_cards/slot/movers.py`. A
  non-empty stamp anywhere is a red, not a finding to explain.

## 6. The coverage factor

- **What it is.** The band of a comparison (span_pick.md:231) is z x sqrt(sum over cards of ((coef_a -
  coef_b) x noise)^2) [+ the bundle's term, §4.6]; z is the coverage factor.
- `[rev1 MEAS-9; rev1.1 Z]` **Which error the band covers: ONE event.** The stored value is the median of 7
  launches over 7 drawn placements (§3.2); the artifact later runs at ONE placement nobody chose, in one
  launch-like condition. The error a departure risks is therefore a **NEW draw** (one launch at a new
  placement) of a card against its stored value, with the noise estimated as §3.4 writes it. span_pick rev
  5.2's sentence ("1 sigma departs ~16 % of equal-price comparisons per side") describes a different event,
  a departure decided on STORED values against true ones (that is ~0 % at z 3: `coverage_drill.py`, 0.005 %
  at f 0); it is amended to this one (§10.2, S2c). Rev 0 quoted Phi(-z) (a known sigma), which is neither.
- **Value: z = 3.0, `COVER_Z_E3 3000`, UNMEASURED DEFAULT (D149).** The tolerance rev 0 chose: at most 2.3 %
  one-sided false departure of a new draw on an equal-price one-card comparison. Drilled on the estimator AS
  WRITTEN (`coverage_drill.py` (2), noise = sqrt(aa^2 + sp2), 100,000 draws per row), for the share f of a
  launch's variance the arm's twin does NOT share (within-launch, arm-specific):

  | f | mean noise (sigmas) | z 2.0 | z 2.5 | **z 3.0** | z 3.5 |
  |---|---|---|---|---|---|
  | 0 | 0.95 | 6.69 % | 3.85 % | **2.25 %** | 1.35 % |
  | 0.5 | 1.21 | 2.70 % | 1.14 % | **0.47 %** | 0.20 % |
  | 1 | 1.40 | 1.68 % | 0.65 % | **0.26 %** | 0.10 % |

  The rate falls as f rises (aa grows with the arm-specific part), so **z 3.0 holds the tolerance at every
  f**, with f = 0 the bound, `[rev1.2 MEAS-11]` **for NORMAL launches**. At f 0 with heavier-tailed launches
  it does not (`coverage_drill.py` (3), 300,000 draws each: normal 2.25 %, Student t10 2.53 %, t5 3.07 %, a
  two-class launch 3.15 %): the tolerance is a normal-launch statement, met in practice because f is near 1
  (below), and the trigger below (row 1's predicted-vs-measured spread) is what would show tails mattering.
  `[rev1.2 MEAS-10]` A `delta` row's noise is mostly estimator error shared across rows of one base, W and
  `ctl` (§3.4 step 7); summing such cards as independent errs WIDE. f is not known before the window and is not assumed: per-launch placement and
  normalization by the launch's control make the residual mostly arm-specific (f near 1, where z 3.0 errs
  wide: wins forgone, the safe direction). rev 1's drill omitted the aa term and so drilled only f = 0. A
  comparison over several cards sums more estimated variances, so its effective degrees of freedom rise and
  3.0 errs WIDE there too. 2.58 (family-wise over smp20's ~10 candidates) was weighed in rev 0 and not
  taken: candidates share cards, so the comparisons are positively correlated and Bonferroni over-corrects.
- `[rev1 SLOT-7; rev1.1 POLICY]` **Where it lives: ONE kit policy table, outside the sets** (R-35 (e), main
  2026-11-06; [KIT-POLICY-TABLE], trigger row 1). Main reads D176 Q3's "`plan_cost.def` rows migrate into the
  sets" as covering MEASURED COSTS only; policy constants are not measurements of a box (D166), and a stamped
  per-set policy value would let a re-measure move a policy. The table's members, each labelled as POLICY with
  its reason (pcrec-suspect-tuning-constants):
  - **z** (`COVER_Z_E3 3000`): the false-departure tolerance of a pick, a risk choice; derived from a chosen
    tolerance above, UNMEASURED DEFAULT.
  - **the gate default** (`gate_e6` 30000 for a card that states none): the noise a cost row may carry and
    still be priced, a quality choice; UNMEASURED DEFAULT carried from grid1 (§2.4). `[rev1.3 r9-SLOT-17]`
    Its home is built: `memfn/data/policy.tsv` (`name value reason`), row `gate_default_e6`; the ver-3 cards
    state `-` and the slot's plan reads the row. z and MATERIAL join the table with row 1.
  - **MATERIAL** (`MATERIAL_NUM`/`MATERIAL_DEN`, `plan_cost.def` today): the margin a departure must clear to
    be worth a plan change, a choice about churn, not a cost.
  - **Not members**: **HORS_MIN** (D176 Q2 deletes it when Horspool is priced) and **MAX_SET** (pcrec's
    `PCREC_OFSK_MAX_SET`, a pcrec FACT transcribed into `plan_cost.def`, D157 direction). Rev 1's member list
    named both; rev 1's "withdraws the narrowing" sentence is replaced by main's reading, which this note
    adopts (R-35 (e)); whether that reading of Frank's Q3 needs Frank is main's call (§10 item 7).
  **Written WITH its reader, row 1** (D77: stage 2 adds no reader); stage 2 fixes z's value and derivation
  here. Visible in row 1's trace (the band per comparison, span_pick.md:60-61); the pcrec-side re-pricer
  pins the literal and diffs it against the trace's.
- **Trigger to re-derive:** row 1's predicted-vs-measured spread (R5.3), which adds model error to the band.

## 7. The step-0 gate

- **The manager's reading is CONFIRMED.** span_pick.md:396 says only "the step-0 gate". D176 Q3
  (`decisions.md:9920`): the cards are measured "in a night window cleared with Frank, gated on the step-0
  census". That census is the stop-ranking study's §7 step 0 (SRS = `docs/design/memfn/stop_ranking_study.md`
  rev 2 on the unmerged `lane/memfn-stopstudy` fc6735cdf, the doc `pricesurvey_report.md:5-7` names SRS):
  "CENSUS, after C1 merges: per window site ... A-mass's pick vs the argmin's at both bracket ends of
  c_probe; count by kind (set to byte, set to PAIR, SKIP declined/admitted, two-byte non-case-pair stops,
  ... the fold)", compile-only, a heavy sweep, no clock; step 1 (THIS box's cards) has the trigger "step 0
  shows a population (any non-zero count of set-to-byte movers or SKIP flips)"; SRS §8 item 2: it "shares
  the price formula with the build, so it LOCALIZES movers and is never the acceptance". The pricesurvey
  cites agree: `:251` (NOT run), `:275` (the census row), `:366` (localize only), `:392` (prerequisite of
  D176's build). **Refinements under span_pick:** the incumbent is today's whole plan (KEY, M, TIE), not
  A-mass alone (span_pick §The pick 2); SKIP (Horspool) counts are out (R14c); "after C1" is met (C1 is S3's,
  landed).
- **What it is now.** J0: the R-33 sweep (job 240's MFTRACE build, re-made at the stage-2 base) plus a
  pricing pass, `docs/design/memfn/span_pick/census0.py`. `[rev1 SLOT-8]` **census0 REPLACES smp20.py**:
  smp20 is census0 on one site, so `smp20.py` is deleted in S2b and `smp20.out` becomes census0's golden on
  that site (one kit-side pricer of the formula, so a formula fix lands once; row 1's C pricer and
  span_pick's pcrec-side re-pricer stay deliberately independent). `[rev1.1 SMP20]` **Its readers move in
  S2b's package** (`git grep smp20.py` at the r5 build tree): `span_pick.md` :286 and :289 (":289 ... BAND-0
  ARGMINS (smp20.py :98)", a line cite) re-cite census0 and `smp20.out`; `span_pick/CLAUDE.md` (:12, :21,
  :34) and `span_pick/witness.sh` (:4, :6) re-point to census0 (§10.2). Per site, each candidate (alternative x
  core position x the methods T-FIND admits on its facts) is priced under P (the default prior) with
  smp20's STAND-INS at the corners of its grid (k 1.00 and 12.00; h1 5 and 40; hit(PAIR) 1x and 8x h1); the
  BAND-0 argmin vs the incumbent read from the trace. Outputs: (1) movers by class (row 1's class: a NONE
  alternative whose core position 0 is a two-member set; others) at any corner; (2) **the card population**:
  for row-1-class sites, the methods, verify (form, cls) pairs and consumer kinds x entry facts their
  candidates read. `[rev1 COST-2]` Output (2) is `docs/design/memfn/span_pick/census0.out` (span_pick's
  instruments directory, own CLAUDE.md), written by S2b and read by S2c's slot harness when it lists the
  cells; there is no separate cell manifest (SLOT-1). Who runs it: a kit lane (the instrument is the kit's).
- **What it must show.** A non-zero row-1-class population: that is the trigger, and it is ALREADY MET by
  smp20 alone (`[rev1 PREMISE-10]` span_pick.md:306-307: "(3,536 points) P's argmin is '/' at 3,381"; the
  figure is span_pick's, `smp20.out` has no P-blind grid line), so as a GATE it cannot stop stage 2. It
  runs first anyway because its output (2) is the D77 reader list that scopes J4/J5's arms (§2.5), and
  Frank's ruling names it. **Control** `[rev1 COST-5 (8), PREMISE-10]`: on smp20's site census0 reproduces
  `smp20.out`'s lines byte for byte, INCLUDING the `incumbent @...` lines (the band-0 argmin is computed
  without the incumbent, so a control on the argmin alone cannot see a wrong incumbent field), and it
  commits its own P-blind grid count as ONE NEW golden line (`[rev1.1 SMP20]` the golden is `smp20.out`
  byte for byte PLUS that line, appended), cross-checked once against span_pick's 3,381 of
  3,536 (a mismatch is a finding about span_pick's figure or census0, resolved before S2b lands).
- **Does stage 2's landing wait on it?** Its TIMING waits (J4/J5's arms come from it); it is unit S2b,
  before the window. Row 1 waits on stage 2, so on it too. It is **re-run after the cards** (S2f) with the
  measured values in place of the stand-ins: still compile-only and readerless, it becomes row 1's
  forecast mover list and the watched witness's stage-2 reading ("is the measured card point above or
  below k*?", span_pick.md:336).
- `[rev1.1 FAM-D]` **A decision of this note, not an unlock** (rev 1's §12.3): census0 is THE priced-forecast
  tool, for row 1 and every later priced row's mover forecast; a later row extends census0 (its pricing
  pass, its classes), never writes a second pricer of the formula.

## 8. What stage 2 moves

### 8.1 Nothing emitted

No pcrec abi event (`[rev1 COST-4]` `PCREC_ARTIFACT_ABI` does not move in any stage-2 unit, whatever its value
at the unit's base: other landers move it, stage 2 does not), no stamp value, no `--list-axes` row (no new
deny: no kit text changes), no `--memfn=` option. Proof per unit: §5's last item, against the unit's named
base.

### 8.2 The numbers that change, and their same-commit packages (readers by grep, D76/D94)

| number / artifact | change | package (same commit) |
|---|---|---|
| MF_SITE_ABI | `[rev1 COST-4]` +1, the next free number at landing (S2a) | memfn.h history entry; `[rev1 PREMISE-9]` the THREE constructors (§4.1); compose.c check; memfn/include/CLAUDE.md; `memfn/docs/journal.md` + responses ledger; `grep -rn 'MF_SITE_ABI'` re-run at landing (no test pins the number today: g2_gen.c uses `MF_SITE_ABI + 1` symbolically) |
| set `format` | `1` -> `1` or `2` (S2a) | `measures.md` hunks §4.4; `ks_measures.c` refusal text; ks_ref.py; mfixtures.py (the `format 2` refusal row -> `3`; a format-2 fixture pair differing only in noise must digest apart; `[rev1.1 TARGET]` a pair differing only in `class` must digest apart; a `-` noise row; a noise-past-10^15 row; a numeric noise on a derived row; a format-1 file with numeric noise text; `[rev1.1 CELLS-1]` a format-2 `cells` row with `events` and `round med`) |
| digest domain | + `pcrec-meas-2`, folding `class` (S2a) | the readers of §5; grid1 untouched |
| `KsMeasRow` layout | + `noise_e6` (S2a); `[rev1.1 CELLS-1]` + the `events` cell column (format 2) | `[rev1 CONTRACT-3]` `scripts/ksgen.c`; the regenerated `src/core/measures_table.inc` (grid1's rows included, noise KS_MEAS_EMPTY); `[rev1.1 KSGEN]` `meas_store_check.c`'s raw-row compare + a format-2 fixture store; `[rev1.1 ANCHORS]` the S-rows anchored in `ks_measures.c`: **S1234** (the noise/abs column swap, anchored on the row-column resolve loop and `put_row`, the exact column S2a starts parsing; its detector re-verified on a format-2 fixture) and S1230, S1231, S1232 (`put_tab(... "cells" ...)`), S1233, S1235, S1239 (anchors re-read; each re-aimed only if its anchor text moves, intent re-verified), with S1244 and S1227 (§5) |
| `KS_MEAS_MAX` | new `ks_measures.h` constant, 10^15 (S2a) | `[rev1.1 BOUND]` the test TU asserting it equal to `MF_MEASURE_MAX` (§4.1) |
| MFMEAS record | + MEASURED count, triple digest, appended (S2a) | `[rev1.1 MFMEAS]` `tests/compound/run_part_measures.sh` (positional reader, re-run); tests/compound/CLAUDE.md's description of the record |
| form-hash entries | `[rev1 PREMISE-3]` formhash.c's declared entry table: + pair, settest, rc-* (S2c; `[rev1.3 S2c-2]` walk-set folded into walk, no entry); `[rev1.1 HASH]` its renderer is the cell renderer (a `kit.h` test entry) | `formhash.c`; `[rev1.3 READY-9]` `tests/memfn/arm_fixtures.c` (`hash_mode`'s `ids[]` gains every new id; `--hash` rc 0 for each) and `finder_check.py` `check_hash` (resolves every new id; LATER_FORMS keep asserting the not-yet ids do not); `[rev1.1 CHECKC]` `finder_check.py` check C's deps guard on CARD rows (§2.4; `[rev1.2 READY-2]` its count printed, floored at 17 over every card table); R-MS3's two fixtures per new id; memfn/data/cards/CLAUDE.md |
| card table | + `kit-grid@3` rows (S2c) | `kit-grid.tsv` (`[rev1 SLOT-12]` its header's unit sentence becomes per-version: ver 1 `u = beta_walk(DFA_SCAN, r1e0c0)`, ver 3 `u = find_byte.walk`; `[rev1.1 CELLS-3]` its column comment for `lengths` and `aa_rule`); its CLAUDE.md |
| spec estimator text | + `measures.md`'s new sections 3.4-3.5 (`[rev1.2 READY-1]` with the cell id grammar), new paragraph 2.2¶5 (S2c); `[rev1.2 READY-1]` NO §2.2¶3 hunk | the recompute check's source text (written in S2e); measure_sets §1.4/§1.5/§7.2/§7.3/§7.4 lines |
| built-in sets | + `zen4-grid3@1` (S2e), embedded cell-less | `measure_store/` files + `index.tsv`; `make gen-measures` (`measures_store.inc`, `measures_table.inc`, `[rev1.1 EMBED]` `scripts/ksgen.c` omitting `cells` and recording `file_cells`; `[rev1.2 READY-4]` the strip step before `scripts/embed_text.sh`, which stays unmodified; `[rev1.3 READY-1]` its layout `$(BUILD_DIR)/gen/meas/<id>/<rev>/set.tsv`, the `KS_TEXTSRCS_measures` row, and the three wording readers (the Makefile K2/B1 comment block, `embed_text.sh`'s header, `meas_store_check.c`'s header); `[rev1.2 READY-3]` `run_measures_tests.sh`'s STORE R4, R5 and embedded-text compares re-aimed and the two new assertions, S1241's and S1232's detectors re-verified for intent, `tests/knowledge/CLAUDE.md`; `[rev1.2 READY-8]` rows' recorded deps and check C's stale count 0 at landing); `measures.md` §8¶2, §8¶3, §3.3, §6¶1-¶2; measure_store/CLAUDE.md ("Sets today", and its line saying emit_sweep writes the movers file, §5); `[rev1.1 CHECKC]` check C's measure_store pass and its floor; the recompute check's format-2 population floor |
| `--list-measurements` listing | `[rev1.1 EMBED]` + column `file_cells` (S2e) | every reader of the listing's columns by grep at S2e (the S-rows below, `run_measures_tests.sh`, `run_code_tests.sh`) |
| `DEFAULTS` | `idk` zen4-grid1@1 -> zen4-grid3@1 (S2e, §8.3) | DEFAULTS, DEFAULTS.log row 2, `movers/0002.tsv` (EMPTY by §5's proof); `measures.md` §5¶6; `measure_sets.md` §3.6 hunk; `[rev1 CONTRACT-4, COST-6]` the `--list-measurements` readers BY NAME: `S1229` (its `SAB_BEFORE` `{ "idk", "zen4-grid1", 1u },` re-aimed to `zen4-grid3`, intent re-verified: the plant still breaks the class's default row), `S1228`, `S1237`, `S1241`, `S1245`, `S1246` (anchors re-read; each re-aimed only if its anchor text moves), `tests/knowledge/run_measures_tests.sh`'s DEFAULTS vs `default_for` vs DEFAULTS.log check (:77-94, a reader of the flip), `run_code_tests.sh`, `c4_allowlist.tsv`, `arch_blind_check.py` (grep hits to re-read). There is NO count pin (`run_measures_tests.sh:75` is a floor `>= 1`) |
| `ofsskip.c` PAIR_LOOKAHEAD comment | UNMEASURED -> MEASURED, iff §3.6 (a) or (c) | none (a source comment; no artifact text); `[rev1.2 READY-7]` committed by S2d |
| `[rev1.2 READY-6]` the run record | new `span_cards/slot/run_record.tsv` (S2d) | its sha-256 in zen4-grid3's PROVENANCE.md and header `run` key (S2e); the recompute reads it; `span_cards/CLAUDE.md` (S2c names the file, S2d writes it) |
| new directories | `docs/design/memfn/span_cards/` (drills now; `slot/` at S2c) | its CLAUDE.md (`[rev1 COST-6]` under the 12 KB gate); docs/design/memfn/CLAUDE.md |

### 8.3 `[rev1 PREMISE-4, SLOT-3, CONTRACT-4]` DEFAULTS: main RULED (B) (R-35 (c)), and what it amends

Rev 0 found a real conflict and mis-framed it ("No ruling is amended"). R-35 item 1 says stage 2 "leaves
DEFAULTS unchanged" and item 3 that row 1 "flips DEFAULTS to zen4-grid3 ... Its flip needs its own landing
verdict from main"; span_pick says the same (Stage 2: "stamps and `DEFAULTS` unchanged"; Row 1 `[rev3 C6]`
"It flips `DEFAULTS` to the new set"). Frank's D166 addendum 2 (Q-MS-1) and `measures.md` §5¶6 say a bare
compile reads the LATEST committed set. Either reading amends something; both give byte-identical artifacts
(nothing consults: every stamp `""`).

**Ruled (main, 2026-11-06): (B). S2e flips `DEFAULTS` `idk` to zen4-grid3@1, with zero movers.**
`[rev1.1 FREEZE NOTE]` The record is R-35 (c) (`memfn/docs/requests.md`, R-35 "Ruled later", main
78e7da573): "DEFAULTS at stage 2 is (B): it flips to zen4-grid3 when the set lands (unit S2e) ... It amends
item 1's 'DEFAULTS unchanged'; the kit's C6 and the measure_sets §3.6 hunk travel with S2e. D166 add. 2 ...
stands." So the R-35 row of the table below is already done by main's record. S2e's commit
writes DEFAULTS, DEFAULTS.log row 2 (`2 idk zen4-grid1@1:13a6536315af1520 zen4-grid3@1:<digest>
movers/0002.tsv`) and `movers/0002.tsv` from the data-mover census (`span_cards/slot/movers.py`, 0001's
shape, §5), EMPTY by §5's proof. It amends three
texts, each in the same commit:

| amended text | owner | amendment |
|---|---|---|
| R-35 item 1 ("leaves DEFAULTS unchanged") and item 3 (row 1 flips, its own landing verdict) | main's request text | DONE by main: R-35 (c). The flip is stage 2's S2e, judged in S2e's landing verdict; row 1 becomes the first READER of an already-default set (its consulting compiles' stamps move then, an abi event that is row 1's) |
| span_pick rev 5.2: Stage 2 "stamps and `DEFAULTS` unchanged"; Row 1 `[rev3 C6]` "It flips `DEFAULTS`"; §Defaults "until row 1 flips it" | the kit's design | `[s2]` lines: stage 2 flips DEFAULTS at zero movers; row 1 reads the default set |
| `measure_sets.md` §3.6 "Every default-set change is therefore an abi event" | the [MEASURE-SET] design | the "therefore" rests on consulting artifacts: a default-set change MOVES the stamp of every consulting artifact, so it is an abi event exactly when a consulting reader exists; a change with no consulting reader (every stamp `""`, the data-mover census empty) is a DEFAULTS.log transition with its census and no abi bump. A `[s2]` revision line (S2e) |

`measures.md` §5¶6 then reads "its default is the latest committed set: `zen4-grid3@1`" (S2e). Goal 1's
measure is restated for it (§1): the `--list-measurements` rows move at S2e (zen4-grid3's new row, grid1's
`default_for`, and `[rev1.1 EMBED]` the `file_cells` column), no other unit moves any.

## 9. Build plan

Stage 2 is SIX scalar units on the kit branch, in this order, plus the HELD SIMD unit S2g; each is a delivered
commit set with its witness. No unit moves an emitted byte (§8.1). The pcrec-side hunks (S2a, S2e) ride the
kit's same-commit package, reviewed by main, as R-35 (a) rules for unit 3.0. Heavy runs are boxqueue jobs;
ONLY S2d needs the timing window main clears with Frank (R-35 (b); never 20:00-01:00, never beside another
timing run).

`[rev1 COST-4]` **Bases.** Each unit names its BASE commit (main's tip it branches from) in its first commit,
and every identity witness (emit_sweep, the data-mover census) compares against that base. Two byte-moving
pcrec lanes land on main alongside (R-35 Concurrency): after any lander, an unlanded unit re-merges main,
re-baselines (a new named base) and re-runs its identity witness before delivery. MF_SITE_ABI is read at
landing (§4.1).

`[rev1 SLOT-11]` **Sabotage ids are the kit's**, taken at BUILD time from the top of the free range and
recorded in the unit's first commit (R-35: three lanes allocate). Below, rows are lettered; `[rev1 COST-5]`
each states the check that turns it red and why that check can see it.

| unit | content | witness | heavy runs | sabotage rows (why each goes red) |
|---|---|---|---|---|
| **S2a** noise channel + format 2 | §4.1-§4.5, §5: the seam field and check (kit); format 2 (noise, `class` in the digest, the `events` cell column, `round med`), the digest role, parse/write, bound and status refusals, `KS_MEAS_MAX` and its equality check, fill (format rule; the handed filter; test levers UNMEASURED), ksgen and the raw-row compare, dump, the MFMEAS fields appended, spec and design hunks (pcrec) | emit_sweep byte-identical every arm vs base; grid1's canonical and decoded views and digest byte-identical; a format-2 synthetic set round-trips canonically; ks_ref.py's digest equals C's on format-2 fixtures; in the `PCREC_CAND_TRACE` build, a compile under a format-2 `--measures=FILE` shows the MEASURED count and a triple digest equal to ks_ref.py's (same filter), a format-1 file with numeric noise text shows 0 and the all-UNMEASURED digest; `run_part_measures.sh` green on the extended record; a kit test hands a zero-initialized row and is refused; `[rev1.1 ANCHORS]` S1234 red on a format-2 fixture, S1230-S1233/S1235/S1239 anchors re-read | `make test` (normal, boxqueue), emit_sweep | (a) format-2 digest skips noise: ks_ref.py (written from the spec) digests the noise-only fixture pair apart, C does not -> mfixtures golden red. (b) format-2 domain spelled `pcrec-meas-1`: ks_ref.py's digest differs from C's on every format-2 fixture. (c) the fill hands format-1 noise as MEASURED: the format-1 fixture carries numeric noise text on every row, so the MFMEAS count is non-zero (expected 0). (d) the kit accepts UNSTATED: the named kit test builds a zero-initialized `mf_measure` and expects the refusal. (e) the fill drops a format-2 noise (UNMEASURED): the handed-triple digest differs from ks_ref.py's. (f) the fill hands `abs_ns_e6` as noise (S983's column swap): the triple digest differs (the fixture's abs and noise columns differ on every row). (g) the canonical writer writes `-` noise as `0`: the fixture holds a `-` row, so the round trip's bytes and digest (INT64_MIN vs 0) differ. (h) the loader admits noise past 10^15: mfixtures' bound row expects a refusal. `[rev1.1 KSGEN]` (r) ksgen omits the appended noise field (C zero in the pre-parse): the raw-row compare reads 0 against a fresh parse's KS_MEAS_EMPTY on grid1's 68 rows. `[rev1.1 TARGET]` (s) the format-2 digest skips `class`: the class-only fixture pair digests apart in ks_ref.py, not in C. `[rev1.1 BOUND]` (t) `KS_MEAS_MAX` edited to 10^16: the equality TU fails to build |
| **S2b** step-0 census | `census0.py` (smp20.py deleted, its readers re-pointed, §7), its run (J0) and `census0.out` | reproduces `smp20.out` byte for byte incl. the incumbent lines, plus the one appended P-blind line; the P-blind count cross-checked (§7); counts non-zero | J0 (compile-only boxqueue job, ~1 min; not timing) | (i) incumbent read from the wrong trace field: the control diffs `smp20.out`'s `incumbent @` lines, which carry that field |
| **S2c** producer | formhash's entry table and its renderer entry (§3.2), `kit-grid@3` cards, check C's deps guard on card rows, `measures.md`'s new sections 3.4-3.5 + 2.2¶5 (`[rev1.3 READY-3]` NO §2.2¶3 hunk: withdrawn by rev 1.2, §4.4), the measure_sets lines, `[rev1.3 READY-9]` `tests/memfn/arm_fixtures.c` hash_mode's `ids[]` and `finder_check.py` `check_hash`'s resolve list gaining every new id (the measure_store pass of S2e resolves tokens through them), the slot harness `span_cards/slot/` (driver, subject generator, per-launch linking and placement with the run id in the seed and the bounded re-draw, `ctl`, the slot's estimator, `j1_rule.py`, the run record's writer, `[rev1.2 READY-5]` `sabotage.sh`, `movers.py`; `[rev1.3 r9-W1]` the S2d job scripts `span_cards/slot/jobs/`) with dry runs of every job and the placement screen | every job's `--dry-run` green (builds, links, placement constraints, `ctl` sha, answer gate on counts AND positions); check C's card guard over every card table (`[rev1.2 READY-2]` 17 with a `kit:form.` dep after kit-grid@3: kit-grid 12, kit-kernels 5; count floored at 17; `[rev1.3 r9-CHECKS-3]` pinned EXACTLY, every named dep resolved); `slot/sabotage.sh` scores every slot-local row below DETECTED; R-MS3's two fixtures per new id (rename: hash kept; one-instruction edit: hash moves); ids pairwise distinct; every cell's site-text hash equals its key's form hash; the placement screen's unit noise printed, under the half gate; `[rev1.3 READY-2]` the run record's two writes dry-run (J1's on a dry-run record, J2p's `--ready` on absent / `a` / `b` / `c`, `finalize` on a dry-run window); `[rev1.3 READY-8]` all under the run id `s2c-dry` | dry runs only (each job's `--dry-run`, light) | `[rev1.2 READY-5]` **(j), (j2), (k), (l) are SLOT-LOCAL rows, not S-rows**: their detectors run only in the slot harness's `--dry-run`, which no make suite runs (`run_sabotage_matrix.sh`'s SAB_SUITES is closed), so `span_cards/slot/sabotage.sh` plants each (a patch to the slot's own source in a scratch copy), runs the job's `--dry-run` and expects the named refusal (precedent `r17b_prime/b3a/sabotage/run_skb3a.sh`); (m), (n), (o) are S-rows (ids the kit's, at build time). `[rev1.1 TWIN, PLACE]` (j) the placement draw ignores the launch (every launch links the same pads): the min(3, 64/A) phases-per-arm assertion on `nm` of the seven linked executables refuses, `[rev1.2 READY-5]` after the bounded re-draw (64) is exhausted, never a hang; (j2) a twin linked at its arm's phase: the per-launch "arm and twin differ mod 64" assertion refuses, likewise bounded. (k) an arm rendered from another entry row than its key's token: its site-text hash differs from `mf_form_hash(<form token>)`. (l) `[rev1.2 READY-5]` two plants: `libc` searching another byte (count 0 vs E: the count gate) and the walk returning each hit one byte late (count kept: the POSITION sum and FNV-1a-64 against the generator's). (m) two form ids hashing one text: the pairwise-distinct check. `[rev1.1 CHECKC]` (n) a kit-grid@3 card with a `kit:form.` dep and no `form` first dim: check C's guard, now in the CARD walk, which reads every card row. `[rev1.3 r9]` (l3) S2934 the timed loop alone halved: the answer gate's `_time` count on the sentinel subject; (g2) S2935 a plan Arm whose form is not its key's: KEY-ARM MISMATCH; (g3) S2936 est's never-ran cross-check removed: est.py's self-test; `[rev1.3 r9fc]` (f1) S2937 est's gate read
from the live cards: est.py's self-test (a live edit after the run); (f2) S2938 a J3 Arm whose landing is not its
key's: the per-dim KEY-ARM MISMATCH; (f6) S2939 the driver's call loop halved for compare arms: the dry run's
round check (ROUND MISS); (l3) plants the arms' TUs only, so a LAUNCH gate refuses; S2933 (mech, `memfnfinder`) `mf_form_hash` folding the canonical instance only: check B's fold compare. (o) a format-2 draft placed in `memfn/data/sets/`: finder_check's format-1 digest of it mismatches (`[rev1.2 READY-5]` NOTED: on a draft with a `null` row it is red earlier, by a ValueError at `int(r["value_e6"])`, `finder_check.py:313-324`: red, not by the stated reason; acceptable, the row's point is red) |
| **S2d** the window | `[rev1.3 S2c-3]` FIRST STEP: the placement screen, run quiet at the window's start before J1 (S2c's screen ran loaded, 8.56 %, and is no reading); over the half gate -> HELD, no J1 (`[rev1.3 r9fc-FIX-7]` the queue job `480-kit-s2d-screen`; a non-green screen makes every timing job's `--ready` answer 77). J1 sweep, then J2, J2p (J1-gated), J3-J5 chained by END (§3.3), one window, one run id. `[rev1.3 r9-W1, r9-W2]` The jobs are S2c's committed `span_cards/slot/jobs/` (prep 480 first: every dry run, the manifests the timing jobs verify and the screen reads; the screen 480 next; J9 489 last), chained by END, not green (§3.3). `[rev1.2 READY-7]` **Its commit** (on the kit branch, after the window): `span_cards/slot/run_record.tsv` (the never-ran jobs, J1's verdict, widths and cells, the plan and floor, the run id, the transcript's sha-256); the `ofsskip.c` comment UNMEASURED -> MEASURED iff (a) or (c) (no byte moves); its report naming the draft set's scratch path and sha-256 and the transcript's location, and under (b) the request that main file the D186 unit-change row | each job's declared population met (POPULATION-SHORT otherwise; J2p's never under (b) recorded as never-ran); the outcome FULL or an accepted PARTIAL (§3.5's table, run by the slot); J1's reading (a)/(b)/(c) | J1-J5 + J2p: quiet-gated `idle-ok` timing jobs, **the window main clears with Frank: 35 minutes** | — (a measurement; its control is S2e's recompute and the per-job drift check) |
| **S2e** the set | §3.8: draft (its sha checked against S2d's report), canonical writer, store files, `index.tsv`, gen-measures with the cell-less embed (`[rev1.2 READY-4]` the strip step, ksgen's `file_cells`) and the listing's `file_cells` column (R-35 (d)); `[rev1.2 READY-3]` the STORE compares re-aimed, S1241/S1232 re-verified; DEFAULTS (B) and its amendments (§8.3); the recompute check (format-2 population, floored; `[rev1.2 READY-6, MEAS-7]` reading the run record and re-deriving J1's verdict); check C's measure_store pass (floored; `[rev1.2 READY-8]` recorded deps, stale count 0); `span_cards/slot/movers.py` and `movers/0002.tsv`; S1229 re-aim | the recompute check exact on every row, every group verdict, Goal 2's floor and `partial`; the drift gate; `tests/knowledge/` green; the data-mover census: zero movers; emit_sweep byte-identical; `--list-measurements` moves by exactly §1's rows and column; `[rev1.2 READY-10]` libpcrec's growth reported in S2e's report as `size -t build/libpcrec.a` and `size -A build/obj/core/measures.o`, base vs head (`tree_drill.py` D's own method; `artifact_size_log.tsv` is a per-pattern log and holds no libpcrec figure), against D's ~16 KB | `make test` (normal), the data-mover census (boxqueue) | (p) the producer's noise off by one unit on one row: the recompute (an implementation of the spec text sharing no source with the slot harness) differs by one, and one unit is a failure (§1.7). (q) a cell edited after the set was written, `[rev1.2]` named: the unit's median-launch 1 Mi `kit.find_byte.walk` cell, which moves W and so every row: the recompute no longer reproduces the rows AND the file sha in PROVENANCE.md/`index.tsv` mismatches (an edit to a cell no median or trim reads is caught by the sha only). `[rev1.1 CHECKC]` (u) a zen4-grid3 row's form token renamed to an id with no hash: the measure_store pass refuses it (red, never "later"); `[rev1.2]` the pass resolves tokens through `arm_fixtures --hash`, so S2c adds the new ids to `arm_fixtures.c` hash_mode's `ids[]` and to `check_hash`'s resolve list (R-MS3's fixtures imply it; stated). `[rev1.2 READY-8]` (u2) a row's recorded dep naming another form's id: the pass compares the recorded id with the row's form token and refuses. `[rev1.2 READY-4]` (v1) the strip step keeps the `cells` rows: the re-aimed embedded-text compare (against the runner's own stripped copy) is red. (v2) ksgen's pre-parse keeps the cells: `meas_store_check.c`'s pre vs fresh parse of the (stripped) text differs, and the named "every pre-parse holds 0 cells" assertion is red. `[rev1.2 READY-6]` (w) the run record edited after the set (a `never-ran` flipped): its sha no longer matches PROVENANCE.md's, refused before it is read. `[rev1.2 MEAS-7]` (x) the slot writes `j1_verdict b` over cells that give (c): the recompute's own re-derivation from `j1_cells` disagrees. `[rev1.3 READY-5]` (x2) a cell's id names launch 4 on launch 5's row: the id-vs-columns compare refuses. (x3) a `find_hit` row's cells name `base.walk` for a `libc` row (computed AND named wrong): the family-rule compare refuses. (x4) the header `run` value's sha edited (PROVENANCE.md and the record untouched): the three-copy compare refuses |
| **S2f** the forecast | census0.py re-run with the measured cards; the watched-witness reading; the report | the smp20 reading stated (above/below k*); row 1's mover forecast listed | J0 again (compile-only) | — |
| **S2g** SIMD (J6) **HELD** | vrun-w16/w32 cards under D188 (§2.7), `[rev1.1 D188A1]` once [XARCH-DEV]'s go is given; its own window and the NEXT set id | designed then | — | designed then |

`[rev1 COST-7; rev1.1 LOCK; rev1.2 READY-9]` **Separability.** The order is **S2a -> S2c (its spec hunks)
and S2b -> S2c -> S2d -> S2e**. S2a is NOT independent until S2e (rev 1.1 said it was): S2c's `measures.md`
hunks (new section 3.4's `events` column and cell grammar, new paragraph 2.2¶5) describe format 2, which S2a's §2.1¶1a/§2.2¶1a
define, and S2c's plant (o) needs a format-2 file; so S2c lands after S2a, and reverting S2a after S2c takes
S2c's spec hunks with it. **S2b -> S2c -> S2d -> S2e are order-locked**: S2c's slot
harness reads `census0.out` when it lists the cells, formhash's new rows are the census's set, and
`verify_cmp`'s deps are the census's pairs (§2.4, §3.2, §7), so S2c cannot land before S2b and S2b cannot
revert alone once S2c lands; S2d times S2c's harness; S2e writes S2d's set. `[rev1.3 READY-4]` (Rev 1.1's
sentence "S2a is independent until S2e" is deleted: it contradicted the first sentence.) Reverting S2a after S2c leaves S2c's spec §3.4-3.5 text describing a format that is
absent, so it is reverted with S2c's spec hunks or not at all (`[rev1.2 READY-9]` the edge above). **S2f after S2e.** S2g depends on nothing here
and nothing here depends on it.

## 10. Questions and amendments

**For Frank: none from this note.** The SIMD model is ruled (D188 add. 1, §2.7); its build waits for
[XARCH-DEV]'s go; the window request goes through main (35 minutes, §3.7).

**For main** (each with the kit's recommendation; `[rev1.1 XREF]` numbered so §4 and §8 cite them):

1. **memchr-back DEFERRED** (§2.5): R-35 and [MEASURE-SET]'s `next:` list it; no priced row reads it (D77).
   Recommend: defer with its trigger; ~1 minute of window if main wants it anyway.
2. **The bundle's sampling-noise field** (§4.6): deferred to its producer; it amends span_pick.md:237-238.
3. **No match_api hunk** (§4.4): R-35 names one; nothing there moves.
4. **Row 1 is a scalar-layer row, as the INTERIM** (§2.5, `[rev1.1 SIMD-READ]` the kit manager's ruling): until
   [XARCH-DEV]'s build `-fmemfn-simd` keeps today's `#if` arms; row 1 departs on the generic target only, its
   SIMD-on arm judged as today's arms (no slower beyond noise). Amendment candidates it draws, for main to
   carry to their owners: span_pick §The pick 6 (its two readings collapse to the per-target pick at
   [XARCH-DEV]) and D186 add. 2 C9 (its "SIMD T-PICK row" becomes the SIMD variant's ordinary pick); and
   SIMD-off-by-default becomes a per-target question at [XARCH-DEV].
5. **D188 fact (b) and today's stamp** (§2.7): `MEMFN_FORMS` names the levels the TEXT carries, so under
   today's `#if` arms a stamp can name a level a fixture's compile excluded. An observation for TODAY's tree
   only; `[rev1.1 D188A1]` there is no model question to relay (D188 add. 1 ruled it), and (b)'s read-back
   under variants is J6's design item at [XARCH-DEV].
6. **The harness set reader's retirement** (§4.2, SLOT-6): its own "until M0" condition is met; noted, not
   done here. `[rev1.1 EMBED]` And **the embed's spelling for S2e's review** (§3.8, R-35 (d)): the general
   cell-less rule, the identity sentence, the `file_cells` listing column and the NAME view's empty `cells`
   are rev 1.1's reading of "must state"; main owns the spelling (the listing is pcrec's contract).
7. `[rev1.1 POLICY]` **The policy table** (§6, R-35 (e)): adopted as ruled (z, the gate default, MATERIAL;
   HORS_MIN and MAX_SET out). [KIT-POLICY-TABLE]'s plan row says "COVER_Z_E3 in plan_cost.def" as TODAY's
   state; `git grep COVER_Z` finds it in no code (it was rev 0's proposal): main's row text to fix. Whether
   main's cost-only reading of D176 Q3 needs Frank is main's call.

**R-35 narrowings, for main to ACKNOWLEDGE** (`[rev1.1 R35]`; each changes main's request text, so each is an
amendment, not a silent drop):

8. **Derived noise by quadrature: DROPPED** until a format-2 derived row has a producer and a reader (§4.3,
   the kit manager's MEAS-13 ruling, strong form). R-35 item 1 asked for it.
9. **`verify_cmp` scoped by the census**: R-35 item 1's "each form the kit offers" becomes the (form, cls)
   pairs the step-0 census finds on row-1 sites (§2.4, §2.5; D77), and vany2/vany3 are dropped (no reader,
   unrouted; already relayed as NOTED).
10. **S2g HELD behind [XARCH-DEV]**: R-35 item 1's "scalar and SIMD" cards become scalar now and SIMD at S2g,
    which waits for [XARCH-DEV]'s go. This MOVES D186 add. 2 C9's ruled sentence "SIMD-form cards join stage
    2" (rev 1's "amends nothing ruled" was wrong): it is an amendment of C9, a consequence of D188 add. 1.

**Also for main:**

11. `[rev1.1 BOUND]` **K138's form**: "read from the seam, not copied" cannot be met under `ks_measures.c`'s
    dependency rule; S2a lands `KS_MEAS_MAX` with a compile-time equality check against `MF_MEASURE_MAX`
    (§4.1), which K138's value refusal can then read. Recommend: amend K138's text to that form.
12. `[rev1.2 standing question]` **The mover census, PLAN** (the kit manager's r6 ruling): file a plan row
    "emit_sweep `--data measures` replaces `span_cards/slot/movers.py` when the next data-mover census is
    needed (trigger: M1's first set)"; main files it (§5).
13. `[rev1.2 READY-6]` **The run record's sha, where cited.** The ruling names PROVENANCE.md "and index notes";
    `measure_store/index.tsv` has no notes column (its columns end `values_digest file_sha256 status`), so
    rev 1.2 cites the sha in PROVENANCE.md and in the set header's `run` provenance key (in the file, under
    the file sha, outside the digest). An `index.tsv` column would be an index-format change of its own (its
    readers by grep at S2e); recommend: not needed.

### 10.2 Amendments this design makes to other documents (each lands with the named unit)

| document | text | amendment | unit |
|---|---|---|---|
| span_pick.md | :267-268 `[rev1.1 CITE]` "(`kit-grid@2`)" | `[s2]` `kit-grid@3` (`@2` is grid2's, TAKEN) `[rev1 PREMISE-6]` | S2c |
| span_pick.md | Stage 2 "`DEFAULTS` unchanged"; Row 1 `[rev3 C6]`; §Defaults | §8.3 | S2e |
| span_pick.md | :237-238 "stage 2's MF_SITE_ABI event" (bundle noise) | deferred to its producer (§4.6) | S2a |
| span_pick.md | `[rev1.1 Z]` §Cost cards "(1 sigma departs ~16 % of equal-price comparisons per side)" | the coverage factor covers a NEW draw of each card against its stored value; z 3.0 at most 2.25 % one-sided on an equal-price one-card comparison (span_cards §6) | S2c |
| span_pick.md | `[rev1.1 SMP20]` :286 and :289 ("smp20.py :98", a line cite) | re-cite census0 (`span_pick/census0.py`) and `smp20.out` | S2b |
| span_pick/CLAUDE.md, span_pick/witness.sh | `[rev1.1 SMP20]` CLAUDE.md :12, :21, :34; witness.sh :4, :6 (smp20.py) | census0.py; the golden is smp20.out plus one line | S2b |
| R-35 (requests.md) | items 1 and 3 (DEFAULTS) | DONE by main: R-35 (c) | — |
| measure_sets.md | §1.4, §1.5 (read cells include the verdict's), :490-494, §3.6, §4.1, §7.2 (`lengths`, `aa_rule`), §7.3, §7.4 (format 2's paired floor) | §4.4, §8.3, §2.4, §3.5 | S2a/S2c/S2e |
| measure_sets.md | `[rev1.1 EMBED]` the sizing sentence ("47 rows is about 6 KB ... Ten committed sets stay below one `fold_tables.inc`") | "Every embed omits its set's `cells` (R-35 (d)); a set embeds as its text plus a pre-parse, about 305 B of libpcrec per row or card (grid1: 23,788 B, `size -A` of `measures.o`). Ten such sets are a few hundred KB, about a tenth of libpcrec.a today; embedding cells would cost about 0.27 KB per cell (`span_cards/tree_drill.py` D)." | S2e |
| measure_sets.md | `[rev1.2 READY-3]` §8.3 "Embedded = committed" ("compares each embedded text with `set.tsv` byte for byte") | embedded = committed minus its `cells` rows; the compare is against the file with those rows dropped (§3.8) | S2e |
| tests/knowledge/CLAUDE.md | `[rev1.2 READY-3]` the STORE description | R4/R5 on the FILE path, the NAME's view = the file minus `cells` rows, the two new assertions (§3.8) | S2e |
| span_cards/CLAUDE.md | `[rev1.2 READY-6]` the `slot/j1/` line | the run record replaces `slot/j1/verdict` and `j1_cells.tsv`; `slot/sabotage.sh` added | done in rev 1.2 (§8.2) |
| measure_sets.md, measure_store/CLAUDE.md | `[rev1.1 CENSUS]` "emit_sweep's data mode writes the movers file" | the movers files are written by a census tool named in their own header (0001: `docs/dev/lanes/m0build/census.py`; 0002: `span_cards/slot/movers.py`); emit_sweep's `measures` data kind is M1's | S2e |
| kit-grid.tsv header | the unit sentence; `[rev1.1 CELLS-3]` the `lengths` and `aa_rule` column comment | per-version (§8.2); the estimator grammar for ver 3 | S2c |
| docs/dev/known_issues.md K138 | `[rev1.1 BOUND]` "read from the seam, not copied" | main's text (§10 item 11) | (main) |

### 10.3 Row 1's design items this note hands on (not decided here)

Which `find_hit` landing and density the price reads (or both, as regimes; §2.3's resolution table bears on
it); verify priced over T-VERIFY's step list (span_pick R21) using `verify_cmp`'s (form, cls) keys; the
`COVER_Z_E3` row in the kit policy table and its trace line; the E2 family unification reading the three
`enter` cards; the band's bundle term (§4.6); its SIMD-on acceptance reading (§2.5, the interim);
`[rev1.1 BOUND]` the band's arithmetic: every intermediate bounded from the stated bounds (value and noise
<= 10^15, its coefficients' bound), never an int64 square of a raw noise (§4.1); `[rev1.1 FAM-C]` its one
qualifier test over three provenance vocabularies (§12 row 6).

## 11. The three standing questions (docs/design/CLAUDE.md)

1. **The measurement regime: RELEVANT.** Every card names it (§2.3): Linux dev box (Zen 4 7700X), gcc 15.2
   `-O2 -march=x86-64 -mtune=generic` `[rev1.1 TARGET]` (the declared target, class `x86_64/zen4`, §2.7),
   glibc's memchr, CPU 7 pinned, sibling idle; each arm at seven drawn placements `[rev1.1 PLACE]`; `[rev1 MEAS-12]` a 16 MiB pool of fresh streamed
   buffers (in L3, beyond L2); throughput on long subjects (byte, hit at g 256 and 1024), a candidate array
   (verify), whole-artifact find-all (enter); hits periodic AND random (a regime flip between them is
   exactly what the robustness rule wants seen); the SCALAR layer only (§2.5); per-call (short-subject)
   regimes are NOT carded ([SPAN-PICK-PERCALL]'s, span_pick.md:198-199), so a priced row's per-call cells
   fall outside the cards' claim. A different box flips picks; that is a new set id, never this one.
2. **The independent control: RELEVANT.** Answers: G2's reference check and the expected-count gate on every
   arm before any clock (`[rev1.2 READY-5]` on positions, not only counts). Values, noise, NULLs, the gates, Goal 2's floor, `partial` and `[rev1.2 MEAS-7]` J1's verdict: the pcrec-side recompute from the set's
   `cells` and `[rev1.2 READY-6]` the kit's run record, sha-checked through PROVENANCE.md (an implementation of `measures.md`'s new sections 3.4-3.5 and §3.6's rule, not importing the slot harness; it reads sets through ks_ref.py's parser); the digest
   by ks_ref.py (python, from the spec's table, not the C), verified again by the C loader. Placement: drawn
   per launch for every arm and twin, the constraints asserted on the LINKED executables (`nm`), never on
   object bytes (§3.2); `[rev1.2 MEAS-1]` the run id in the seed makes a re-run's placements independent of
   the first run's. Drift: the fixed control executable per job against the unit's job, `[rev1.2 MEAS-4]`
   with a threshold in standard errors of the statistic, its false rate drilled. The cell text: its site-text hash against `mf_form_hash` of the key's token
   (one renderer; FAM-A is the router's independent control, §12 row 4). Check C: its card guard reads
   every card row and its measure_store pass every format-2 set's form tokens, each counted and floored. "Stage 2 moves nothing": emit_sweep and the data-mover census,
   counted pcrec-side from artifact diffs (K35) by `slot/movers.py` (§5), never the kit's `moved`. The seam's noise values: the
   MFMEAS triple digest against ks_ref.py's. The census (§7) shares the price formula with row 1, so it
   LOCALIZES only (SRS §8 item 2), never accepts. Populations: every job declares its group count and the
   queue counts it (POPULATION-SHORT); the recompute check counts the sets it skips.
3. **What moves when the data is regenerated: RELEVANT.** Re-measuring makes a NEW id (`measures.md` §8¶1);
   a re-reading of the same `cells` a new rev. With no reader (stage 2), nothing emitted moves under any set
   (§5's proof), and the DEFAULTS flip moves no stamp (§8.3). From row 1, a new default set moves the picks
   of consulting artifacts and their `<PREFIX>_MEASURES` stamps: then a default-set change is an abi event
   with its census (`measure_sets.md` §3.6 as amended, D162). A PAIR width retune (§3.6 (b)) stales the
   PAIR rows through `[rev1.2 READY-8]` the form hash RECORDED in each row's `deps` (rev 1.1's rows carried
   none, so no staleness check could ever have seen it); a consumer entry-text change stales `enter` (§2.6). The embed is
   cell-less (§3.8): a re-measure moves the embed by its rows only, about 305 B each.

## 12. Unlocks (filed, not built)

1. `[rev1 MEAS-13, SLOT-1 general form]` **A measured row as a DERIVATION over `cells`.** The estimators of
   §3.4 (`slope`, `delta`) become registry derivations (`launch-median-slope`, `arm-minus-base`) whose
   `inputs` are cell ids, recomputed by the existing §3.2 checker path; a noise rule becomes one column of
   that registry, and derived-row noise follows from it. Unlocks: Goal 3 without a special-purpose check;
   M3's install tool implementing ONE registry; derived noise with a reader. Trigger: the first format-2
   derived row with a producer and a reader, or M3's driver build, `[rev1.2 r6 general form 5]` or a
   measured row whose value is a derivation over cells needing its own noise (§4.3's `-` noise on derived
   rows collides with it), whichever first. It would also absorb rev 1.2's cell-id base (READY-1).
2. **One kit policy table** ([KIT-POLICY-TABLE], filed by main; `[rev1.1 POLICY]` members per R-35 (e),
   §6). Unlocks row 1's E2 unification. Trigger: row 1.
3. `[rev1.1 FAM-D]` (rev 1's "census as THE priced-forecast tool" is now a decision, §7.)
4. `[rev1.1 FAM-A]` **A router control for the form hash.** The cell-text check proves key-to-row; that the
   stated facts reach the row THROUGH the kit's router (T-FIND / T-VERIFY's first match) is a separate
   fact. General form: every formhash entry row carries its expected router answer and a check routes the
   row's facts and compares. Unlocks: a form-hash row that can never drift from what the router picks.
   Trigger: the first formhash row whose facts route to another row in a router change (a red the cell
   check cannot see), or row 1's build, whichever first.
5. `[rev1.1 FAM-B]` **Placement as a declared fixture property.** Every kit timing fixture (G2's probes,
   the bake-off, stage 2) draws placement per launch by one shared helper (the pad objects and the `nm`
   assertions of §3.2). Unlocks: every timing in the tree carries placement in its noise the same way.
   `[rev1.2 standing question, PLAN]` Trigger: the NEXT slot harness written (the family is already past
   three: 650, grid1, grid2, b3a/e8min, stage 2's), not "a second harness that needs placement".
7. `[rev1.2 READY-6 general form]` **A `run` section inside the set** (review r6 unlock 2): the run record's
   content (never-ran jobs with their keys, the declared floor, gate verdicts like J1's) as a format section
   hashed by the file sha, so "the recompute reads only the set" becomes true and M3 writes the same section.
   Not taken now: it is a format change S2a would have to build (the ruling chose the kit-side record).
   Trigger: M3's driver build, or a second producer whose verdict needs a record.
6. `[rev1.1 FAM-C]` **One qualifier test over the three provenance vocabularies** (the set's `status`, the
   seam's noise state, the card's `aa_rule`): one table that says whether a value may price. Unlocks: row
   1's qualifier written once. Trigger: row 1's build (§10.3).

## STATE AT HANDOFF

`[rev1.3]` Rev 1.3, lane s2c (the S2c build lane's first commit): review 2026-11-06-r7's READY-1..9 applied as
text fixes (§R1.3); the S2c build follows this text. Below, rev 1.2's handoff, kept.

Rev 1.2, lane s2rev12 (over rev 1.1, lane s2rev11), from review 2026-11-06-r6 as ruled (every FIX-NOW and DOC
disposition, the decisions READY-1, READY-6 + MEAS-7, READY-8, MEAS-4, MEAS-6, MEAS-1; the movers.py PLAN).
Nothing S2a builds changed (§R1.2: needs S2a, none). OWED: nothing of the design; every unit of §9 is
unbuilt; S2g HELD until [XARCH-DEV]'s go. Next: the kit manager's diff-check of every r6 id and ONE readiness
critic on the rev 1.2 diff (the ruling). Main's acknowledgements owed: §10 items 8-10 (R-35 narrowings), 7
(policy), 6 (embed spelling), 11 (K138), 12 (the mover-census row to file), 13 (where the run record's sha is
cited). The drills behind §2.3, §3.2, §3.5, §3.6, §3.7, §3.8 and §6 are committed under
`docs/design/memfn/span_cards/` (python only, no timing; each prints its inputs; rev 1.2 re-ran all seven).
No make, no timing, no box job. Not a build go.
