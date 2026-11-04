# VERIFY round memfn-spanpick5

Review tree: worktrees/crit-memfn-spanpick5 (main 7f55a62f9). Design: span_pick.md rev 5 (9c9aadb60), copy VERIFY/design.md.
Compiles run by me: 6 on item 9 (no Horspool site reached), 1 on item 13.

## 1 STAGE1-1 FIX-1 SIM-4
verdict: HOLDS
- D186 add. 2 on 7f55a62f9: "The provenance fields (`mf_prov.source`, the bundle "default" label, memfn.h) leave the seam in span_pick stage 1: the kit never sees the source."
- design.md :442 "whether the field stays is main's call"; :508 "For main: ... `mf_prov.source`'s future". Staging rows (design.md :359-364) 1a-1f: none removes it.
- Readers confirmed: memfn.h :1213-1214 (enum), :1224-1233 (mf_prov), :1238 (`mf_prov prov` in mf_akind); memfn_sites.c :273-276 writes prov.source/bundle/digest, :247-248 reads prov.bytes/fidelity from the built object, `pcrec_memfn_prov_stanza` :599; tests/memfn/prov_check.c :27-31 offsetof asserts on all five fields; finder_check.py :658 KIT_READERS_RE; arm_fixtures.c :1572-1584 fd_an_make sets source MEASURED, bundle "weblog", digest, bytes, fidelity.
- No kit .c reads them (grep, item 11), so the unit would be byte-identical.

## 2 STAGE1-2
verdict: HOLDS
- `grep -nE 'kit_walk\(|< best|< bm|tie_takes|TIE_|< inc' memfn/src/*.c`: hits only in compose.c (2), finder.c (1), ofsskip.c (2), runcmp.c (1), window.c (24); presence.c: 0.
- presence.c :165 `m < lo || (m == lo && tie_over(...))`, :182 `c < sm`, :192 `wm < wl`; window.c :1335 `rank_ppm[j - 1] > c` all exist and none matches a grep shape. design.md :151-157: the census is "a grep ... whose every hit must be mapped", so a decider with no hit never reaches the check. (The committed decider->table map is written by the lane, but the red-on-unmapped check is the grep.)

## 3 STAGE1-3
verdict: HOLDS
- arm_fixtures.c :1685 `printf("%u\n", mf_finder_pay(&in));`; memfn.h :1550-1557 declares mf_pay_operands/mf_finder_pay.
- tests/mech/sabotages/S1025_sn9-pay-tie-pays.sh exists; run_sabotage_matrix.sh :497 mentions S1025.
- finder_check.py :641 `--pay-grid`; rows.tsv :119/:123/:124 (R8, R1, R2 `pending-site`), row_floors.tsv :103/:107/:108 (PLACEHOLDER).
- finder.c fd_rows order from :250: R8 R3a R3b R4 R1 R2 D1 D1c D1w PAIR R7w, then P0 (:330) FD_PRES. design.md :355 "A finder row added or removed ahead of the PRES rows is an MF_CLASS_V event"; design 1f row (:364) names only MF_SITE_ABI.

## 4 STAGE1-4
verdict: HOLDS
- presence.c :222-245 writes `out->landmark`; emit_dfa.c :11256 `int kl = k.landmark < 0 ? 0 : k.landmark;` and :11258 `pick_rec("landmark", ...)`; tests/memfn/run_pres_picks.sh :61 `PICKS="set scan window leads dominated landmark ..."`. memfn.h :788-790 documents the public `landmark` field.
- design.md :361/:414 "retired if no census reads it": two readers exist today.

## 5 STAGE1-5 FIX-4
verdict: HOLDS
- `grep consulted memfn/src`: kit.h :292 (decl), compose.c :1303 (`*consulted = art->consulted`, reader), comments at finder.c :378/:862. No write anywhere.
- window.c :1070 `decide(art, site, 1, d);` (quiet=1); kit.h :906-908 "quiet ... counts no reach"; gate.c :943/:956/:978 `if (t->quiet) return;`.
- memfn_stamps.c :275-286 meas_stamp ORs `job->meas_consulted`, `cx->meas_union` and each compound part's `meas_consulted`.

## 6 STAGE1-6
verdict: HOLDS
- row_floors.tsv header: "written as floor(0.9 x measured)"; floors are lower bounds.
- `grep -i 'MFTRACE|MF_TRACE|memfn_trace' scripts/emit_sweep.py`: 0 hits; its "REACH" is corpus pattern reach (:1938).
- `grep -rF 'zzzzzzz~J' tests memfn scripts`: 0 hits (appears only in design/review docs).

## 7 STAGE1-9
verdict: HOLDS
- finder.c row starts: D1 :282, D1c :287, D1w :293, PAIR :306, R7w :322. design.md :120: "Horspool FIRST ..., then D1c, PAIR, D1, D1w, R7w". Order differs. (Disjointness not checked; the finding does not depend on it.)

## 8 STAGE1-10
verdict: HOLDS
- roadmap.md on 7f55a62f9 :49-51: "it states its candidates and their prices ... pcrec sees its candidates only as opaque entries with prices" while :386/:400 say prices appear only in the trace (D186 add. 2). A-PLAN row (:107) is amended.
- §5 rows R01-R19 only (:623-641): none for find-method deciders, position enumerators, mass variants, tie/run-member spellings, the landmark shadow or inert finder rows. design.md :93 "no roadmap edit is left to stage 1"; :368 "Ratchet (proposed for main)".

## 9 STAGE1-11 FIX-3
verdict: HOLDS (code); the compile confirmation was NOT obtained
- window.c :1596 `return kit_set_mass(dx->d->rate, dx->w->set[dx->w->stop_ix]) >= COST(HORS_MIN);` plan_cost.def :61 HORS_MIN 145822. presence.c :58-62 `uniform_mass(k) = k*1e6/256`; kit_set_mass (:81-85) = capped kit_set_sum (comment :87-88 "NONE: cardinality"). 37 members = 144,531 < 145,822 <= 148,437 = 38 members.
- m_margin_holds (window.c :669-683) compares `a[].cost * NUM` with `* DEN`, costs built from mass (:421, :470, :552).
- Tried 6 `-e utf8` compiles (`abc[a-zA-Z0-9]`, `abc[a-zA-Z]`, `abc[a-m]`, `[a-zA-Z0-9]{3}=`, `[\w][\w]:[\w]`, `[a-zA-Z0-9_]{4}[a-zA-Z0-9_]x`): no Horspool or shift text in any output, so no site reached D-hors and no 38 vs 37 contrast was shown.

## 10 STAGE1-13
verdict: PARTLY
- 1c needs 1b: HOLDS. window.c run_member (:763-) works on `wf_dec` spans (`kit_set_sum(d->rate, r->set[j])`), presence.c :181 run_scan on `mf_term` run/mask cubes via `cube_mass`. Sharing needs a mass primitive over cubes, which design.md :360 assigns to 1b.
- 1e needs 1d: only as the design words it. d_hors_holds (window.c :1596) reads `dx->w->set[stop_ix]` of `wf_plan`, which exists today. The dependency is real only if 1d changes that structure into the T-VERIFY step list (design.md :120-121), which it does.

## 11 FIX-2
verdict: HOLDS
- memfn.h :1223-1233: mf_prov {source, bundle, digest, bytes, fidelity}.
- grep memfn/src for `(->|\.)digest|mf_akind|->prov|\.prov\b|fidelity`: only `proven`-name false positives. No kit read of prov.
- findings.c :579 `out->bytes = out->source == PCREC_FIND_SRC_MEASURED ? fb->prov_bytes : 0;`.
- finder_check.py :658 regex `mf_prov|mf_akind|MF_FID_|fidelity|->prov\b|\.prov\b`, scan of memfn/src at :720-727: a kit read of `.prov` would be reported.
- design.md :51/:173/:74 hand "its digest" to the kit and put it in the trace; its only home today is mf_prov.digest.

## 12 FIX-5
verdict: HOLDS
- memfn/tests/run_g2.sh :986-1007 (`reach_lines` :998 greps `MFTRACE REACH table=.. chosen= asked=`); run_g2_gate.sh :144 `sed ... MFTRACE REACH table=arms row=precheck_assign_byte chosen=`; memfn/docs/trace_format.md :130 "## Reach (at exit)". design.md :104-105 names only reach_print and rows_check.py.

## 13 FIX-6
verdict: HOLDS
- `build/pcrec -p rx -e utf8 --analysis l1none -I FIX/L1 -o t13.c --pattern 'x/1234'` printed `pcrec: analysis 'l1none': its 'cpfreq' block at line 2 counts nothing via encode-latin1, so it has no byte-rate (pattern offset 0)` and exited rc=1.
- design.md :431-436 table has rows 1-3 only (chain answers / default / none); no refuse row.

## 14 FIX-7 SIM-3
verdict: HOLDS
- window.c :421, :470, :552, :774, :1334 read `d->rate` (`d->rate = kit_byte_rate(art)` :991): KEY A-mass, MARGIN costs, run_member.
- design.md :177-179 "built from site facts alone (no rate input) ... ONE candidate set"; :178 candidates are plans "that differ from the incumbent only at the row's levels"; :204-206 the parenthetical "where the two incumbents agree outside the row's levels; elsewhere the NOT-covered census", while :212 NOT-covered = "sites no priced row admits".
- witness.out: default arm blind `memchr on: 'X' 'x'`, prose `'4'`. Row 1 (design.md :389) admits "NONE alternatives whose default is a two-member stop" = reads the incumbent, so smp20 is admitted blind and not with prose.
- A real loss site was not produced (needs a census over 50 compiles).

## 15 FIX-8
verdict: HOLDS
- D176 Q5 (decisions.md :9919): "prices within the measurement-noise band tie, decided by the existing declared tie rows".
- window.c :77-110: wf_ties rows T_MASS_STRETCH/T_MASS_SET/T_MODEL/T_CMODEL/T_MARGIN/T_WINDOW, each "of a mass EQUAL to the best's" at an offset (tie_takes :107-110); no TIE_DEFAULT, no method-level row. design.md :185-186 introduces T_BAND -> TIE_DEFAULT and "the method-level tie row is row 1's design item".

## 16 FIX-9
verdict: HOLDS against main HEAD fa736a260; NOT present at the frozen 7f55a62f9
- plan.md [MEASURE-SET] row at fa736a260 (only that row read): "RULED M2 order ... M2 is NOT ordered against span_pick's row 1 ... priced rows go DARK on bare compiles ... INTENDED"; next: "span_pick stage 2 measures the zen4 span cards (memchr, two-stream pair, walk, verify; Horspool-probe later) as a FRESH set id `zen4-grid3`". At 7f55a62f9 the row has neither (its next: line still reads "memchr, two-stream pair, Horspool-probe cards + verify"). Those hunks came with a later commit (fa736a260 "RULED line after refs").
- design.md :503 "M2-dark: PENDING-RECORD", :497 "log form PENDING-RECORD", :508 "M2's order" as For main; stage-2 cards include hors.probe (:259), memchr-back (:257).
- D186 add. 2 says "its log is filed with the first such change". decisions.md :10042 "Minimax is PAIRWISE against the incumbent" is still live; design.md :504 "A1 SUPERSEDED".
- The consequence "Horspool cards deferred => D-hors incumbent unpriced => rule 4 keeps" follows from design.md :187 "Unpriced incumbent: keep" (not re-derived beyond the text).

## 17 SIM-1 SIM-2
verdict: HOLDS (under uniform band 5, an instance the text allows)
- Own script VERIFY/sim17.py implements step 3 as written (qualifier iff price(inc)-price(c) > band; pick = TIE-ranked member of those within band of the cheapest qualifier). Output: before `q2`; after adding cnew=78 (qualifies, TIE-ranked last) `q1`, and cnew is not picked. SIM-2: inc 100, cs 70, cP 72, c3 74, TIE prefers c3: pick c3 at 74 while cP (72) qualifies.
- Caveat: bands are per-pair quadrature in the design; I used a constant band, a legal case.

## 18 SIM-5 SIM-6 SIM-9
verdict: HOLDS (all three)
- SIM-5: smp20.py :98 `q = [c ... if c != inc and p[c] < p[inc]]` (band 0); docstring of pick: "cheapest candidate cheaper than the incumbent".
- SIM-6: r33_sim/collect.py :126 `hashlib.sha256(tab.encode()).hexdigest()[:16]` is the `a322116b1b87f9f6` source; the kit's digest is `1822fb973b95a4da` (design.md :340, witness.out). design.md :282 names `a322116b1b87f9f6`.
- SIM-9: counts.out columns RTE/DEF/total: PARKED+RESEED 1429/25/1454; 1 core position 733/7/740; >=2 696/18/714. design.md :71-72 quotes 1,429 (RTE) beside 740/714 (total).

## 19 STAGE1-8
verdict: PARTLY (structural: translate's grouping rule is not run_group_ok's; whether any real site differs is not shown)
- translate (window.c :1278-1300) groups by `d->pterm` equality over `in_plan` positions, with no check of `w->core`, shape, adjacency in `w->off` or the MF_MAX_TERM cap.
- find_groups (:1494) additionally requires `key[i] >= 0`, `w->off[j] == w->off[j-1] + 1`, `run_group_ok` (:1467: every position core and `shape`) and `nrun < MF_MAX_TERM`.
- pterm itself (:905-929) already needs adjacency in poff and shape+same stated span for non-pinned joins, but a pinned join (:912-914) needs only `in_pinned` on both, no core. So the two rules can differ at a pinned non-core position or where w drops a position; making translate read run_group_ok is not provably a no-op. Equivalence on real sites needs a census (not run).

VERIFY COMPLETE
