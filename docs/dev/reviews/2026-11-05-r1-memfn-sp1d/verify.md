# VERIFY crit-memfn-sp1d

Compile count (pcrec compiles) is tallied at the end. Env: TMPDIR/PCREC_TMPDIR = VERIFY/.

## CHECK-1 (+SLOT-11): HOLDS
- Dead shapes: `git -C <review tree> grep -nF -e SHAPE -- memfn/src/*.c *.h *.def` counts: `< bm` 0, `< lo` 0, `< b.mass` 0, `< after->mass` 0, `< wl` 0, `< inc` 0; `< best` 2 (window.c:96 a comment, window.c:607 `i < best_n`); `pick_takes(` 8.
- Bypass plant: copy memfn/src to VERIFY/cs/src, append to window.c an unlisted function with `kit_pick b = KIT_PICK_NONE; ... if (b.pos < 0 || v[j] <= b.v) {...}`.
  `python3 -I tests/memfn/decider_census.py --root <review tree> --src VERIFY/cs/src --no-plants`: rc 0, "hits 37, outside a member: 0, checks failed: 0" -- identical to the unplanted run (rc 0, 37 hits, failed 0). SILENT (green).
- Control (conforming twin, same appended function using `kit_pick_takes(&b, ...)`, VERIFY/cs2/src): RED, "outside a member: 1", failed 1. So only the spelling `pick_takes(` trips the backstop; a `.v`/`<=` bypass does not. Plants share the backstop's own shape (pick_takes) as CHECK says.

## CHECK-2: HOLDS (all four rows)
Built per run_finder.sh (one gcc -std=gnu11 -O1 line per memfn/src file, then arm_fixtures.c + objs), against the review tree's memfn/include. Base: `--purity` rc 0, failed 0, passed 287. Plants (diff vs review tree window.c: exactly 1 line each), purity rc, control vs base control.log:
- m_parked_holds (window.c:757) `return x->d->na == 2 && !x->d->art->nsites;` -> rc 0, failed 0, passed 287; CONTROL same (plant not reached). Verdict: SAME (GREEN).
- c_model_holds (window.c:896) `... == &ct_a_model && !d->art->nsites` -> rc 0, failed 0, 287; CONTROL same. SAME.
- c_floor_holds (window.c:892) `!chosen(d)->has_stop && !d->art->nsites` -> rc 0, failed 0, 287; CONTROL same. SAME.
- run_member verify-NO (window.c:869) `int exact = r->verify == MF_VERIFY_NO && !d->art->nsites;` -> rc 0, failed 0, 287; CONTROL same. SAME.
(Plant "compiler" here is gcc, rc 0 for every build.) The control not moving shows the plants are not reached by any harness reply.

## CHECK-4: HOLDS (witness never enters the loop on the default arm; never ties on any arm; plant LOUD where reached)
- Derivation: presence.c:160 `if (n > MF_PRES_WINDOW)` guards the T_WINDOW loop (presence.c:163-170); MF_PRES_WINDOW = 8 (memfn/include/memfn.h:1619).
- Instrumented lib (CHECK/T: presence.c differs from the review tree only by two fprintf lines after the kit_mass at :168, printing WCAND per iteration and WTIE on a tie; diffed). `(?i:x)abcdefg(?i:y)`: default rc 0 WCAND=0 WTIE=0; `-e utf8` 0/0; `-fmemfn-simd` 0/0; `-I tests/findings/adversarial --analysis=uniform` 0/0 (and with -e utf8 0/0); `--engine=vm` WCAND=82 but WTIE=0 (the loop is entered, nothing ties). Control: `x(?i:eeeeeeeeeeeqeeeeeeeeeee)y` default WCAND=344 WTIE=301, vm 656/574, `-e utf8` 43/0 (instrument works).
- Plant (CHECK/S1096/pcrec, S1096's own SAB_AFTER) vs subject build/pcrec, same basename x.c in two dirs, `--features all`: witness default / -e utf8 / --engine=vm / uniform: plant rc 0, subject rc 0, all SAME. Tie-reaching `x(?i:eeeeeeeeeeeqeeeeeeeeeee)y` default: see line below.
  Result: plant rc 1 ("pcrec: internal error: the memfn kit refused a site: mf_define: the pre-check's parts are not its presence links' layout"), subject rc 0 -> LOUD where reached. The named witness itself: SAME on 4 arms (never reaches a tie, so the sabotage is not caught by it; the row text "caught by the (?i:x)abcdefg(?i:y) tie witness" is stale -- candoracle detection, if any, comes from other patterns, which I did not run). Verdict HOLDS (SUSPECTED part of CHECK-4 about SAB_DOC_FIGURE not verified: needs run_cand_oracle.sh, banned).

## SEAM-1: HOLDS
`tr-subject/pcrec -p rx --features all -e utf8 -o VERIFY/s1/x.c --pattern P` (rc 0 both, 2 compiles). Both chosen=A-mass. WCAND lines:
- `[ac][ac]`: `alt=0 off=0 members=2 mass=7812 core=1 stop=1 walked=0 key=0 incumbent=0` / `alt=0 off=1 members=2 mass=7812 core=1 stop=1 walked=0 key=1 incumbent=1`
- `[ab][ab]`: `alt=0 off=0 members=2 mass=7812 core=1 stop=1 walked=0 key=1 incumbent=1` / `alt=0 off=1 ... key=0 incumbent=0`
Input fields (everything but key/incumbent) are identical record-for-record; the pick differs (off 1 vs off 0). Consequence claim (hidden stretch/cube bit) is derivation by the critic from a_mass_choose; the observation itself is reproduced.

## SEAM-2 / SEAM-3: HOLDS (drivers rebuilt in VERIFY/drv: `gcc -std=gnu11 -O1 -I memfn/include -I tests/memfn -I VERIFY/drv X.c tr-subject/libpcrec.a`, rc 0 each)
- seam_drv (A-model, own set / scan eligibility): variant 0 reply `stop=1@1 path=reseed nplan=1`, variant 1 `stop=1@2 path=reseed+pin nplan=3`; chosen=A-model both. WCAND input fields identical across variants in all three rows (`off=0/1/2 members=1 mass=3906 core=1 stop=1 walked=0/1/1`); only key/incumbent differ (off 1 vs off 2).
- seam_o (C-model, list order): variant 0 `stop=1@4 plan=0,1`, variant 1 `stop=1@4 plan=0,3`; the five WCAND rows are byte-identical between the variants (members/mass/walked/key/incumbent all equal, written in offset order). Plan differs: HOLDS.
- seam_m (M-parked vs MARGIN) needs the rated arm: run with an argument (`seam_m 1`; without it, both variants are MARGIN and no gap shows -- the critic's text omits that). With rated: variant 0 `alt=0 stop=1@0 path=parked+pin`, chosen wfM=M-parked; variant 1 `alt=1 stop=1@1 path=reseed`, chosen=MARGIN. WCAND input fields (alt, off, members, mass, core, stop, walked) are identical in all 12 rows; only key/incumbent differ. HOLDS (with the rated-arm qualification).
(Fixture drivers, not pcrec compiles; exit codes 0.)

## SEAM-5: HOLDS, and identical at BASE
`seam_r.c` built twice with one gcc line: against review-tree build/libpcrec.a and against base/build/libpcrec.a (using the subject's arm_fixtures.c helpers; base lib links, mf_wdecide exists). Both print `same art, same site: rc 0/0 stop 4 -> 2 (stop)`; also on tr-subject lib. So a host mutating its table after mf_art_begin moves the reply at BASE exactly as at SUBJECT: KEPT, not introduced by 1d (SAME base vs subject).

## SLOT-1: HOLDS
Recipe quoted at docs/design/stream/roadmap.md:640 (e9e5f035e; untouched by the diff): "enumerators among `^static void a_model_choose(` and `^static void a_mass_choose(` in memfn/src/window.c ... minus 1". `git show REV:memfn/src/window.c | grep -cE '^static void a_model_choose\(|^static void a_mass_choose\('`: daf6f002b -> 2, e9e5f035e -> 2. Reads 1 at both; delta 0. (The recipe's parenthetical still names `mass_domain`, which 1d deleted.)

## SLOT-2: HOLDS (one nuance)
presence.c:183 `out->set_leads = kit_mass(rate, s->pspans[best].term[0].set, 1, KIT_MASS_SUM) < sc.mass;` is a strict-`<` two-candidate compare with no TIE row, not through kit_pick_takes. Census: `grep sc.mass` over decider_census.tsv/py: 0 hits; the tsv lists kit_pres_picks only as :set-pick (l.68), :run-window (l.69), :landmark (l.70); `git grep 'sc\.mass' memfn/src` finds only this line. Nuance against the critic: kit.h:366-370 DOES name the exception ("P2 and P4 compare with no TIE row"), so P4 is a stated exception in the header, though not a census member.

## SLOT-8 / HOUSE-2: HOLDS
ofsskip.c:128-131: `int m = run_mask_at(sc, p->plan_pos); if (m != 0xFF && (__builtin_popcount(~m & 0xFF) != 1 || (sc->run[p->plan_pos] & ~m & 0xFF))) return 0;` where run_mask_at (ofsskip.c:77-80) is `t->mask ? t->mask[j] : 0xFF`. Earlier, ofsskip.c:110-117's loop covers every term including p->term[p->plan_hint] (plan_hint < nterm checked at :106) and for each RUN term does `if (!run_cmp_sat(t)) return 0;` (:116). run_cmp_sat (runcmp.c:346-352) returns 0 unless `!(t->mask && t->run[j] & ~t->mask[j] & 0xFF)` for every j (run_pos_sat, runcmp.c:341-344). So when sc is a RUN and control reaches :128, `run[j] & ~mask[j] & 0xFF == 0` for all j, including plan_pos < run_len (checked at :127); the `&` clause at :131 is always 0: unreachable, a fourth spelling (the others: gate.c:725, generic.c:196, runcmp.c:341). ofsskip.c is not in the SUBJECT diff (pre-existing).

## SLOT-4 / HOUSE-1: HOLDS
window.c:793-797 (review tree): "Three rows are applied elsewhere and listed for the order: C-meet by `merge` (Table A reads the meet), C-bound inside C-floor and C-yes (the bound itself is `plan_of`'s) and C-table/C-own by `plan_of`". Stale against the same file: `c_bound` is its own applied step (window.c:922-931, `wf_crows` row `{ 2, "C-bound", c_always, c_bound, ...}` at :1053); C-meet's row text (:1036-1038 region, `{ 1, "C-meet", c_always, NULL, ... (`merge`, in the candidate builder `cands`, before Table A)`) and `cands` (:347-349 "alternative's C-meet into m") show it is built in `cands`; C-member is row 0 (`run_member`, :1036) and the header omits it.

## SLOT-9: HOLDS
compose.c:884-885: `art->an = an; /* the handed rates: kit_byte_rate reads them (the PRES picks, KEY's A-parked/A-model/A-mass, MARGIN, D-hors) */`. `grep -n 'd->rate\|kit_byte_rate' memfn/src/*.c`: presence.c:136 (PRES picks), window.c:543 (A-parked k0), :870 (`run_member`: `kit_run_member(d->rate, ...)`, T-VERIFY), :1120/:1123 (`cands`, KEY/MARGIN), :1464 (translate: `kit_run_member(d->rate, ...)`), :1731 (D-hors). The comment names five groups and omits run_member (:870) and translate's ranking (:1464).

## HOUSE-6: HOLDS (reading; "would desync" is prediction)
c_bound (window.c:922-931): `full(m->has_stop ? p->yset : rd_set(d, p))` inside an apply whose row has `holds = c_always` (:1053). The two holds it re-derives are `c_floor_holds = !chosen(d)->has_stop` (:892) and `c_stop_holds = chosen(d)->has_stop` (:893); C-floor and C-yes are the rows at step 2 selected by them. So c_bound repeats the has_stop partition inline instead of its own rows / `c_stop_holds(d)`. Sound today (partition).

## HOUSE-7: HOLDS (count exact; the gate is a floor)
run_finder.sh PURITY_FLOOR line(s) quoted above; fixture built from the review tree per run_finder.sh's gcc line (VERIFY/base): `--purity` rc 0, `checks failed: 0`, `checks passed: 287` = floor 287. Gate compares with `-ge` (run_finder.sh:134-135 `... >= floor`).

## EMIT-1: HOLDS
`tr-subject/pcrec -p rx --features all -e utf8 -o VERIFY/e/x.c --pattern '\bfoo\b'` rc 0: single alternative, `ROW ... row=A-parked verdict=DECLINED:PRED_HOLDS ... fields=entry:R2:NOENTRY` (entry NONE), yet `WCAND ... alt=0 off=-1 members=193 mass=753906 core=0 stop=0 walked=1` and `off=3 members=193 ... walked=1`. trace_format.md (e9e5f035e:memfn/docs/trace_format.md:127-128): "`walked`: 1 iff a RESEED walked offset (A-model's domain, ...)". Text vs output disagree.

## EMIT-2: HOLDS
`tr-subject/pcrec -p rx --features all -o VERIFY/e/y.c --pattern '(^)*ab'` rc 0: two `WCAND` records (off=0, off=1), then `END table=wfE ... chosen=E-func`; no `WPATH` line. trace_format.md:118 says WCAND is written "after C-meet, in alternative then offset order, before its `WPATH`" (and :132-134 says a WPATH is the plan's shape). Text claims a WPATH follows; none does.

## EMIT-3: HOLDS (by reading)
window.c:811-815 `plan_drop`: `d->poff[i] = d->poff[--d->np]` (moves the LAST entry into the freed slot), so c_bound (:922-931, walks poff from the end, drops full-set positions) can reorder; BASE (daf6f002b) never added those positions, so its pre-C-asc order was add-order. Rows between C-bound (step 2) and C-asc (step 7, :1072), in wf_crows order: C-model (:934-938, `plan_add` of m->pick[]), C-none (:940 no-op), C-pin (:963-976: reads via `tested_elsewhere` -> `in_plan` (:947-948), then `plan_add` run positions), C-stop (:983-987: `plan_drop` of the stop), C-run (:1000-: `c_asc(d)` is its first act, :1008, "Grouping reads adjacency, so it orders first"). plan_add dedupes via in_plan (:808) and caps by count (`d->np < WF_NPOS`), both order-free; every reader is membership/count based. Only the final order matters and C-asc sorts offsets (unique), so SUBJECT's final plan equals BASE's. Pre-C-asc order does differ from BASE (swap), unobserved.

## PLANT COMPARE SUMMARY
CHECK-2 plants: plant "compiler" gcc rc 0 on all four; verdicts GREEN purity (SAME as base: failed 0 / passed 287), control SAME (not reached).
CHECK-1 plant: census rc 0 SAME as unplanted (SILENT); conforming control rc 1 LOUD (RED).
CHECK-4: S1096 plant pcrec vs subject build/pcrec: witness on 4 arms SAME (rc 0/0); tie-reach pattern LOUD (plant rc 1, subject rc 0).
Not verified: CHECK-4's SAB_DOC_FIGURE "5fail/177pass" (needs run_cand_oracle.sh, banned on this box); CHECK-5 and CHECK-3 (not in my list).

PROBED: pcrec compiles about 27 (of 400): 9 instrumented-lib witness probes, 8 plant-vs-subject compares for the witness, 2 tie-reach, 2 SEAM-1, 2 EMIT, plus a few repeats; the fixture/driver builds (6 purity fixtures, 6 drivers) are gcc builds, not pcrec compiles.

## VERIFY COMPLETE
All 15 items verified: HOLDS (CHECK-1, -2, -4, SEAM-1, -2, -3, -5 [same at BASE], SLOT-1, -2 [nuance: kit.h:366-370 names P4], -4, -8, -9, HOUSE-6, -7, EMIT-1, -2, -3); none REFUTED; SEAM-3 needs the rated arm; CHECK-4's candoracle figure not verified.
