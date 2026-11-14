# [RUN-POS-SET] plan row body

Long-form notes moved out of plan.md (PL11 row cap).

## 2026-11-12

- NOTE (2026-11-12, manager): readiness memo docs/design/run_pos_set_stage3_readiness.md (lane s2prep, at K38-2's seam): no new seam field (K38-2 carries runs as sets) but 3 kit sites assume <=2 members, so Part D is a KIT BUILD landing with stage 3 in ONE abi event; 2a's ALT row (1) folds into S2; scope = every encoding (classes 3-128 members, alternation unions), census first, D186 gains byte regimes; memo §6 leanings ACCEPTED. Build brief memo §4, kit request §5.

- NOTE (2026-11-12, joint ruling with the kit, Part D critic round NOT READY -> rev 2): R (the run's pinned verify-NO span) is identified by ROLE, not shape: any multi-position verify-NO span pcrec states IN A WINDOW SITE'S ALTERNATIVE is R (scope fix P14: the run presence span, req_pres_spans, is a second such span and is not R); pcrec decides its reach (pf_window_of over walk-proven positions); the kit never infers it from shape and pcrec never reads the kit's scan capability (D157). An MF_SITE_ABI meaning event inside S2's one landing; no byte moves today.

- NOTE (2026-11-12, kit Part D reviews, for the stage 3 brief): The stage 3 build brief must say so, and also (kit review partd2): P1, req_site_define's head-part gate_need keyed on TESTED run, not stated run (run >= 0), or every declined run with a member fails mf_define; P8, pcrec's pick shadow (req_set_leads_own: leads/rlead) RETIRES as an independent expectation on runs with any non-cube position (precedent: K38-2 retired scan/rwin), successor controls C2 + G2's decline equality; FIX-1 (kit partd3): the same retirement extends to dominated/rdom on non-cube runs (part_d §9's "rdom stays" dropped).

- Rule (1) (2026-11-13, Frank: "Isn't that general to the hull?"): yes: `all` is a hull statement (alt_normal_form §4.2, O1), so no owner ruling is needed; S2 lands it OFF; after S2 the census runs with/without (readiness §4 stage 0) and the manager turns it ON if movers are as expected.
- Post-S2 measurement set (Frank 2026-11-13: "Once this framework is in there are a bunch of items that can be measured"; not injected before landing): first item = inline rarest-byte find + in-place neighbour check vs main vs S2 on IPv4, dot-heavy and number-dense texts (memfn/docs/ideas.md 2026-11-13).

**2026-11-14 manager ruling (rps3 STOP note, §9 item 2).** CONFIRMED as built: the head-vs-`req_byte`
check holds only where NO run is stated; on a decline K is read from the head member itself
(`req_landmark_k`). Reason: on a declined run with an exact position the kit's P3 head pick and pcrec's
`req_byte` pick may legitimately differ, so equality there would be a false internal error; the check's
purpose is the K the handoff subtracts, which the head member supplies.

**2026-11-14 manager ruling (rule (1) default ON), landed by lane r1on (abi 106 -> 107).** `rr_alt`
row 1 (`alt_union`: an alternation whose branches are all `all` and of one untruncated width is
`all`, its run the per-position union) is the DEFAULT. Basis: Frank 2026-11-13 (`all` is a hull
statement, supersets ruled OK, ON/OFF the manager's) and the s2r1b census (lane/s2r1 508bec313,
`docs/dev/lanes/s2r1b_report.md`): 19 byte movers of 5,489 distinct corpus patterns in the default
configuration (22 with altcls denied, 22/27 utf8 facts), every one an equal-width or all-zero-width
alternation extending or newly stating a run, 0 unexpected; answers identical 14,880/0 over the 14
mover files; emitted size +0.005% (`(?:ab|ba|aa|bb){24}c` shrinks 9.9 KB, handoff none -> 17). The
AHEAD lever `--harness=alt-union-run` retires; its restore is the walk arm `alt`
(`--harness=restore=alt`, src/facts/walk_arms.def, an internal arm of `tests/axes/run_axes.sh`), a
test-only lever because the change's risk is a wrong answer and it can never be slower for a caller
(no public deny). Witnesses: [facts-ahead] default cells + `alt` twins, S-c in
`tests/litscan/spanarms.rxt`; sabotage rows S3129-S3132; S-g was already landed as S1927.
