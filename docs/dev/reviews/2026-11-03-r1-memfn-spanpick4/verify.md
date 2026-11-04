# VERIFY: crit-memfn-spanpick4

Own computation: VERIFY/v.py (written fresh from the design's price formula and stand-ins; it reads only the
bundle .list rates), VERIFY/d.py. Run with `python3 -I`.

## SIM-1
HOLDS. `v.py sim1` (byte(PAIR) 1.00-10.00x step .05, hit(PAIR) multiples step .25, six candidates, kinds P,F,log,weblog):
least hit(PAIR)/hit(memchr) multiple at which '/' is the minimax pick: hit(memchr) 5 -> 4.75x (design: 8x); 10 -> 3.5x;
20 -> 2.75x; 40 -> 2.25x; 60 -> 2.25x. At exactly 2x, '/' is minimax at hit(memchr) 80 (byte(PAIR) 8.0-8.55x), 120 (10.15-12.35x),
160 (12.3-16.2x), none at 20/40. The design's "at least 4x" / "never at <= 2x" are grid points of smp20's 1,2,4,8 sweep, not boundaries
(second sentence is wrong only at hit(memchr) >= 80, outside the plausible range).

## SIM-2
HOLDS (with PREMISE-7, same claim). `v.py sim2` at hit(memchr) 10, hit(PAIR) 20, byte(PAIR) 2.0x: {X,x},'/' only -> W 2.718 / 2.470, pick '/';
add '4' (never picked, W 3.904) -> W('/') 3.636, pick {X,x}; full six also {X,x}. `v.py p7` (PREMISE-7's case, hit 40): {X,x},'/' -> 3.056 / 2.838
pick '/'; add '4' -> '/' 4.055, pick {X,x}. The loss normaliser min over the candidate set makes the pick depend on non-picked candidates.
Neither §The pick nor §Robustness states it. Grid count (720 flips) not re-run; the two constructed flips suffice for the claim.

## SIM-3
HOLDS. `v.py sim3`: with the PAIR candidate removed (DEF deny; candidates the five one-member stops, default '/'): W('/') 4.055, W('1') 3.789,
W('2') 3.221, W('3') 1.974, W('4') 2.216; c* = '3', gap 2.081 (same at hit(PAIR) 20 and 40). Design §The pick open point (5) (line 115) makes denies
filters on T-FIND/T-PICK rows, and the witness table lists only "'/' on the DEF deny" for today. So under the rule the DEF arm departs '/' -> '3' once the
band is below ~2.08, a mover the table does not forecast. Premise (PAIR filtered by the deny) taken from witness.out (DEF blind stops on '/').

## SIM-4
HOLDS. "With data" text (design lines 192-196) says only "a candidate departs from it only if cheaper beyond the band"; it names no target among
several beating candidates (prose: '4' 63,555, '3' 66,143 per smp20.out). prose.list counts: '4' 11, '3' 19, N 69,462. Own check: price slope ~22.5/ppm
x sqrt(count) x 1e6/N -> 1,074 and 1,412, quadrature 1,774 vs gap 2,588 (1.46 sigma). Exact binomial P(<=11 of 30 | equal) = 0.1002 one-sided (computed).

## PREMISE-2
PARTLY. Code facts HOLD: mf_wdecide (window.c :1058-1063) takes (art, site, out) and its comment says it "reads no frame fact"; finder.c :934
hard-codes `q.ff.layer = CL_L_OFF`; set and bundle are bound by mf_art_begin (compose.c :869-882, `art->ms`, `art->an`). So the property's tuple
(site facts, frame, set, bundle) is not the call's argument list in stage 1, and a different set/bundle needs a new art. The design itself says the
frame joins the plan call at unit 3.0, so the property is stated for the target call; the finding is a precision gap, not a contradiction. art->denies/levers
reads not re-checked.

## PREMISE-3
HOLDS. compose.c :1361-1364 `mf_includes` is a getter; `mf_stamps` (:1404-1418) reads words, forms, libc only. `wused & ~wemitted` read at runcmp.c :515
and written :533 (helper TEXT emitted once, first-use); `simd_inc` read/written at ofsskip.c :565-567 (header `#include` emitted once). So the sentence "read
only by stamps" is false and the emitting face is call-order dependent; the plan path stays pure. (FIX-11's "read only by stamps" part: same evidence,
HOLDS; its other parts not verified.)

## PREMISE-4
HOLDS (ii, iii hard; i is an inference). (ii) witness.out: prose bundle -> KEY default `memchr on: '4'`, blind -> 'X' 'x'; design line 209-210 says KEY's
mass rows read B; the with-data text says "the BLIND pick (steps 1-4) ... is the incumbent" without saying which default step 3 starts from (SIM-7 same). (iii) smp20.py docstring: "No card has a measured noise, so
guard (b) keeps today's pick ... the picks below are what the rule would choose once noise exists". (i) design line 139-140 and 410-411 ("KEY's two rows retire by
census") unchanged while guard (b) needs today's pick as incumbent: the conflict is by reading, not run.

## PREMISE-5
HOLDS. src/findings/log.rxt line 5 "SYNTHESIZED, Hadoop-DataNode-shaped log corpus", `fidelity synthesized` at :89/:166;
third_party/synth-log-lines-v1/PROVENANCE.md :7 "SYNTHESIZED. Not vendored from an external source". smp20.out hit 20: the worst cases of '3','4','1','2'
(5.925, 6.654, 8.939, 9.670) are all the `log` column. Design line 174 and 284 call both bundles "real data" (D186 add. 2 says the shipped `log` and `weblog`).

## PREMISE-6
HOLDS. VERIFY/d.py (first 1,000,000 bytes, per-block count var/mean, Poisson would be 1): weblog 20 blocks: x 18.6, X 9.2, '/' 4.4, '3' 19.8, '4' 8.3;
100 blocks: x 14.7, X 5.1, '/' 3.6, '3' 10.9, '4' 7.5 (SD 1.9-4.3x Poisson). log (synthetic) 20 blocks: '/' 2.1, '3' 5.5, '4' 24.6; x/X under-dispersed (0.5/0.0). Identical to the critic's
figures for weblog. Block-size dependent by nature; direction (clustered, understated sqrt(n)) holds.

## PREMISE-9
HOLDS. smp20.out hit(PAIR) 20: P {X,x} 144,694 < '/' 153,476 (P's least is {X,x}); '/' beats {X,x} under P only at hit(PAIR) 40 (153,476 < 166,634).
Design line 309 "'/' wins P and F ... at both" is false at 20 (its own table row says "{X,x} ('/')").

## FIX-1
HOLDS. D186 add. 2 last bullet (decisions.md :10039) says it amends A-PLAN's open point 1 ("a BOUNDED set"); roadmap.md :398 already carries "Amended (owner,
2026-11-02 ...): ONE PLAN, WITH THE TRACE"; design :97-99 says it amends the "agreed next step" and stage 1 edits the roadmap; roadmap :107 (table row
"candidates + price cards"), :384 (end state) and :387 (next step "candidates and cards out") still carry the old text. Source cell design :497 cites "memfn journal 2026-11-03"
(after today) and not D186 add. 2.

## FIX-2
PARTLY. Facts HOLD: gate.c reach_print (:884-900) prints `MFTRACE REACH ... chosen= asked=`, tests/memfn/rows_check.py reads it (:156-169, "asked=N"),
and the counters increment per call (gate.c :1013-1014); `consulted` (kit.h :292, read compose.c :1303) is not listed among the breakers and nothing sets it today (finder.c :862).
So "write-only" is wrong as stated (counters are read by a printer and tests). The consequence (extra scenario calls change reach counts, only in an MFTRACE build) is
conditional, not re-run; `art->nsites + 1` extra sites (compose.c :982,:988,:1005) not re-checked.

## FIX-4
HOLDS. decisions.md :9742-9748 D167 "zen4-grid2 GO"; measure_store/zen4-grid1/1/PROVENANCE.md :26 names zen4-grid2 as the replacing set; memfn journal (pre-11-02) 2026-10-16 line 2371
"grid2 itself ended COMPLETE 20:06:22 required=ok". decisions.md has no text giving `zen4-grid2` to the span-card set (only D167 hits). measure_store/ has no zen4-grid2 directory yet, so
the clash is of the id as already used in records for the Oct-16 run, not an existing set.

## FIX-5
HOLDS. `grep zen4-grid2 docs/dev/decisions.md` hits only D167; the '4'-passes widening has no decisions text, and the r2 review's RULINGS (line 324) says the witness "must switch to '/'".
O3 went to the owner as a question (r2 review :244-246); no answer text found in decisions/plan; "pure function" has no decisions/plan home (roadmap :61/:107 are the emit face). Only the
one-plan row has a home (D186 add. 2).

## FIX-8
HOLDS (text facts; consequences plausible). Design :148 retires the PREFIX / vrun KA/KB exception at "the first SIMD T-PICK row" though rule 6 says PREFIX/KA/KB pick SIMD rungs of the scalar
plan on sites that row will not admit; §The shape step 2 (:55-56) builds candidates from stated core positions, and the C9 witness is a two-byte vector window; the card table (:248-254) has no layer/SIMD-form column or
row even though the intro says "measured per layer". Whether the witness is reachable is an argument, not run.

## FIX-9
HOLDS. plan.md :1541 [COVER-PRICE-WITNESS] (`[\xc2-\xdf](?![\x80-\xbf])` x1.95 slower, charter "BOTH layers", trigger "the kit's D176 priced stop choice build opens") and :1547
[PAIR-LOOKAHEAD-TIME] (trigger "the kit's next timing window ... or the measurement-set revision for the pair card"). grep of the design for both tags: 0 hits; it uses the pattern as C9's witness (:187)
and "O3 = WAIT: smp04 and look-ahead" (:387) with no tag cite. roadmap :392 lists [COVER-PRICE-WITNESS] as a ride-along trigger.

VERIFY COMPLETE
