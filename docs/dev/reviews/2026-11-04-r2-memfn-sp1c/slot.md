# SLOT lens — critic round memfn-sp1c (subject 3ecb647c7, base 7b671bc2c)

Lens: every slot the subject touches traced to its ONE table/mechanism; house
rules; standing questions (a) sibling of a family, (b) general form + unlocks.
Compiles used: ~82 (60 emit compares, 22 for one private-copy plant).

## Findings

### SLOT-1 — kit_run_member's ranking silently requires T_MASS_STRETCH to be a strict, translation-invariant order
- CONFIRMED (plant in a private export). Severity: maintenance. Effort: S (a sentence in kit.h + the row's basis, or a refusal). Blast radius: translate's rank_pos/rank_ppm, P3 run_scan, window.c run_member.
- Where: memfn/src/window.c:767-785 (kit_run_member), :1363-1369 (translate's loop casts `r.pos` to uint16), :85-110 (wf_ties / kit_tie_takes).
- The `after` cursor skips "ranked at or before" with `!kit_tie_takes(T_MASS_STRETCH, after->pos, j)`. That is right only when the row answers a strict total order on keys. The TIE table lets a row hold TIE_EXCHANGE/PARKED/RESEED, for which kit_tie_takes answers 0 for every pair: the walk then skips every equal-mass position, returns pos -1, and translate writes rank_pos 65535 with rank_n = n. The old insertion sort produced a full permutation under any tie rule.
- Repro: `git archive 3ecb647c7 memfn tests/memfn/mass_check.c` to slot/tree; window.c:87 TIE_HIGHER -> TIE_EXCHANGE; build memfn/src/*.c + a driver ranking four equal-mass positions (slot/walk.c). Observed: `rank[0] pos=0; rank[1] pos=-1 (uint16 65535); rank[2] pos=0; rank[3] pos=-1`. Expected: a permutation of 0..3 or a refusal. mass_check DOES catch this flip (3 FAIL: the HIGHER expectations), so this is a missing precondition, not a missing test.
- The keys' ORIGIN: kit_run_member keys run-relative j. a_mass_choose (window.c:566-574) reads the SAME row keyed on absolute offsets (k + WF_LO), and run_member keyed r->start + j before 1c. Under HIGHER/LOWER the answer does not depend on origin or sign, so today nothing moves. A rule that depends on origin (for example "nearest the candidate", |offset|) would give different answers for the same row in the two readers.
- Fix: state the precondition (a strict order invariant under translation: HIGHER/LOWER) in kit.h at kit_run_member and in the T_MASS_STRETCH row. Also make translate refuse rather than cast a pos of -1.

### SLOT-2 — T_MASS_STRETCH is now pinned by pcrec parity at two seams, but its basis reads "UNMEASURED DEFAULT"
- CONFIRMED by reading. Severity: doc/design. Effort: S. Blast radius: every presence site with a run, every run pre-check.
- Where: window.c:86-89 (basis "today's; on REPORT literal stretches UNMEASURED DEFAULT"); compose.c:667-675 (pres_layout_check: the part's scan must equal pk.run_scan); src/gen/emit_dfa.c:1071 (req_run_member: internal error when the kit's run_member is not pcrec's r->idx); src/core/findings.c:745 (pcrec_find_run_scan_index's own rightmost tie).
- Before 1c the row was already pinned to pcrec's findings.c tie through req_run_member. 1c adds P3's run_scan as a second pinned reader, through pres_layout_check's part_is_run(scan) compare. A measurement-driven flip of the row (which its basis invites) would make mf_define refuse presence sites with tied runs ("its run part is not the WINDOW ...") and make pcrec stop with an internal error. The row's basis does not record this cross-seam obligation.
- Fix: the basis column names the obligation ("must equal pcrec_find_run_scan_index/_run_rank's tie until pcrec reads the kit's member; a change is a pcrec findings change in the same commit"). Splitting A-mass's stretch tie off is NOT recommended: the ruled fact is one stretch tie.

### SLOT-3 — the run-position-to-set conversion has three semantics across the seam; kit_run_set is the kit's one, and pcrec keeps two more
- CONFIRMED by reading. Severity: design (no answer moves today: the D187 count read 0 non-normal). Effort: M, at the kit split. Blast radius: any non-normal cube that pcrec would ever state.
- kit_run_set (presence.c:87-93): `(b & mask) == run`, so a non-normal position is EMPTY.
- pcrec_memfn_wpos_cube (src/gen/memfn_sites.c:517-522): `(b & mask) == (byte & mask)`, which NORMALISES. This is how pcrec states the run window to the kit for req_run_member.
- findings.c cube_mass (:631-640) and pcrec_find_run_window_start (:795): `t | f`, so a non-normal position counts t's stray bit.
- On a non-normal input these give three different answers for one position. The kit refuses only on the presence seam. The window seam gets pcrec's normalised set, so the refusal does not cover req_run_member's statement.
- span_pick.md's "pcrec-side findings" lists scan_index/window_start but not pcrec_memfn_wpos_cube. D187's "Later" (one detector, pcrec_cube_of) is the home. Recommend filing wpos_cube beside them: it is pcrec's run-position-to-set conversion, a sibling of kit_run_set.

### SLOT-4 — the normal-form predicate ("a run byte outside its mask") is spelled three times in the kit; 1c adds a fourth reader
- CONFIRMED by reading. Severity: maintenance. Effort: S. Blast radius: none today.
- The spellings: gate.c:725-731 (cl_run's CL_UNSAT loop), runcmp.c:342-347 (run_cmp_sat), generic.c:195-201 (the per-position constant false). kit_run_set's empty set is the same fact again, implied.
- 1c's refusal (compose.c:584) correctly REUSES run_cmp_sat (no new spelling). The family is at 3 members, so propose unifying it (forest-for-trees rule): cl_run asks run_cmp_sat for its UNSAT answer.
- Under D187's end state (cubes derived from sets) the whole family becomes dead (see unlock U-c).

### SLOT-5 — comments still say "cube mass" where the kit now prices sets
- CONFIRMED by grep. Severity: doc. Effort: XS.
- window.c:545: A-mass "(PICK's cube mass)". 1c changed the parallel run_member comment at :804 to "position mass" but not this one.
- memfn/include/memfn.h:1440: run_member "the least-mass position of all of R (PICK's cube mass)".
- memfn/include/memfn.h:1600-1601: run_scan is "the rarest position, its cube's mass". The PUBLIC description of P3 now disagrees with presence.c:13-15 ("by its set's mass"), which 1c updated.

### SLOT-6 — translate's comment says "rank_pos[0] IS the run member by construction", which is ambiguous against window.c's own run member
- SUSPECTED (by reading; to confirm, trace a verify-NO R whose plan term's least-mass position is a two-member position, and compare rank_pos[0] with d->member - term offset). Severity: doc. Effort: XS.
- Where: window.c:1356-1360. rank_pos[0] is kit_run_member(exact 0) over the PLAN's sets (after C-meet). window.c's run_member (d->member) is kit_run_member over R's sets, with exact 1 on a verify-NO R. These are two different answers that both carry the name "the run member".
- span_pick.md's 1c row asked for "rank_pos[0] asserted against run_member". The subject derives the ranking instead (the "-2" path), so no assertion exists.
- Fix: write "the plan term's least-mass position (kit_run_member over the plan's sets)".

### SLOT-7 — altitude: the kit-wide position primitives live in two family files
- Observation. Severity: maintenance (low). Effort: S, at 1d.
- kit_mass and kit_run_set are in presence.c. kit_run_member, kit_tie_takes and wf_ties are in window.c. So presence's P3 now depends on window.c for its member, and the census map (decider_census.tsv:54) files the kit-wide member under window.c.
- Not a defect. A shared home (one "positions" file) is the natural landing for 1d's one candidate builder.

### STANDING (a) — SIBLING OF A FAMILY
- 1c does not create a new sibling: it merges three own spellings (P3's `c < sm` loop, translate's insertion sort, run_member's loop) into kit_run_member.
- It does LEAVE an argmin family of five members over (mass, tie row): kit_run_member (window.c:767), a_mass_choose (window.c:563-577, which also reads T_MASS_STRETCH, keyed absolute), a_model_choose (window.c:~486-525, T_MODEL), P3's set pick (presence.c:142-150, T_PRES_MEMBER) and P3's run window (presence.c:170-176, T_WINDOW).
- span_pick 1d (one candidate builder, T-PICK) is the ruled place for these; kit_run_member is the first member with a reusable shape (reader callback + filter + cursor).
- Cross-seam siblings, pcrec side: pcrec_find_run_scan_index / pcrec_find_pick / cube_mass (findings.c:631-764), already filed. Also pcrec_memfn_wpos_cube (memfn_sites.c:517), NOT filed (SLOT-3).

### STANDING (b) — GENERAL FORM + UNLOCKS
General form of what 1c did: every decider reads a position ONLY as a byte set, through one reader (kit_pos_at), with the cube-to-set conversion at one point (kit_run_set) and normal form checked at the input. A ranking is a repeated argmin with a cursor over one tie row.

Unlocks, each with its trigger:
- U-a: the presence seam states RUN positions as sets (D187's end state on pspans). kit_run_set leaves presence, run_at and the kit_pos_at callback collapse to a plain array (sets_at alone), and the 1c normal-form refusal is deleted (there is no cube to be non-normal). Trigger: the next MF_SITE_ABI event that touches pspans, or the kit split.
- U-b: kit_run_member generalised to (reader, candidate filter, tie row) is T-PICK's one argmin. a_mass_choose, the set pick, the run window and a_model_choose become its callers, and the cursor gives any ranking for free (e.g. a ranked set-member list for a future multi-member scan). Trigger: 1d landing; precondition SLOT-1 (the row must be a strict order; T_CMODEL's EXCHANGE cannot use the cursor).
- U-c: once renderers receive sets and derive cubes themselves (D187 "Later": one detector, pcrec_cube_of), a derived cube is normal by construction. CL_UNSAT (gate.c:728), generic.c's constant-false branch, Q-G2-13's clause and run_cmp_sat's role as a check all become dead and are deleted. Trigger: the first renderer moved to derive its cube from the set.
- U-d: pcrec's copies (cube_mass, run_scan_index, run_window_start, wpos_cube) become one conversion (pcrec_cube_of's inverse) and one member (asked of the kit). That retires req_run_member's parity check and SLOT-2's pin. Trigger: the kit split (manifesto 2026-11-04) / span_pick's "pcrec's two and its PICK: findings" row.

## PROBED-AND-HELD
- kit_run_member against the three spellings it replaced, by reading:
  - P3's rightmost-first strict `<` equals the ascending walk with HIGHER.
  - translate's stable insertion (rightmost inserted first, shift on `>`) equals the repeated argmin with the HIGHER cursor.
  - run_member's key r->start+j vs j: invariant under HIGHER.
  - mass_check's MEMBER block (7 checks) pins all three; the plant turned 3 of them red.
- The `after` skip predicate, checked by hand for HIGHER and LOWER: it skips exactly the positions ranked at or before `after`.
- One conversion in memfn/src. Submask loops `(b - 1) & f`: 0 remain. Set-builders from `(x & mask) == run`: kit_run_set only; compose.c's term_prove now uses it. The other mask readers (generic.c, k1_ref.c reference evaluator, runcmp.c, vrun.c, ofsskip.c, finder.c:789, precheck.c, compose.c part_is_run) are compares or renderers, not conversions.
- translate's plan sets equal its RUN term's cube. run_bytes takes shape() (lower member, mask ~(a^b)), which is normal. C-run groups only one-member or cube positions (window.c:998), so switching from the term's cube to w->set[hint_at+j] moves nothing.
- kit_pres_picks callers are all behind kit_presence_check: compose.c:983/989 (after site_check at :971), :1006 (rc 0 only), :1116 (after site_check at :1025; the wplan path skips presence).
- kit_mass callers: 11 call sites, all sets. Capped/uncapped is the same as base at each one. The landmark with no run and q<0 gives 0, the same as base's empty-set mass under rates and under NONE (k=0). set_leads' {q} set mass is the same as base's 0xFF-mask cube of q.
- Cost of the repeated-ask ranking: n <= MF_RANK_MAX 32, at most 32x32x256 bit tests per ranked term. Negligible.
- No-mover spot check: 6 patterns x 5 regimes ("", --engine=vm, -fmemfn-simd, -e utf8, --analysis uniform) = 30 cases, BASE vs SUBJECT emitted C, 0 differences.
- decider_census MEMBER_COUNT 51 -> 50 matches the stated merge (2 out, kit_run_member in). The plant anchor moved to `wm < wl`, which is still present at presence.c:173.

CRITIC COMPLETE
