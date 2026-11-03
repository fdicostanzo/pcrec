# VERIFY: critic round crit-memfn-spanpick (design, round 1)

Verifier (opus), read-only. Review tree worktrees/crit-memfn-spanpick @ 884996ef6 (checked:
`git log -1` = 884996ef6). Subject = frozen subject/span_pick.md ("subj:N" = its line N). Compiles
are counted per section (trace build `tracebuild/pcrec`, outputs under verify/c/). Python with `-I`.

## PREMISE-2
**HOLDS.** precheck's texts are presence tests, not finds: memfn/src/precheck.c:279-288 `gate` emits
`if (n <= lo || !memchr(s + lo, b, n - lo)) on_miss`; :295-307 `landmark` a statement-expression
`<prefix>_mf<handle>_q = ... memchr(...)`; :311-330 `set_rest` a `static const unsigned char rq_set[]`
memchr loop. pffind.c:258-266 `pf_memchr_use` renders a different shape (`const void *q = memchr(...)`
then a store), so "same memchr text" (subj:328, N9) does not hold. As a FIND on the VM route the
answer would not be memchr: finder.c:812 `seek_facts` sets SF_SEEK_ROLE for span 0 of a VM_ATTEMPT
site; the D1 row (finder.c:282) lists SF_SEEK_ROLE as an excluded fact; D1w (contract KD_STOP &
~DFA_ATTEMPT, finder.c:214; row :291) takes it -> FF_WALK. pcrec states the pre-check's kind as
`site_kind_of(cx, SKS_PRE)` (emit_dfa.c:8737), VM_ATTEMPT on the VM route (table row :1424).
Compile 1/30: `tracebuild/pcrec -p rx --engine=vm --pattern '(\w+)\s*=\s*(\w+);'` -> trace
`FD ... slot=PRES ... kind=VM_ATTEMPT need=REQUIRED members=1 ... row=P0`; artifact verify/c/vm1.c:302
`!memchr(subject + search_from, 59, ...)` and :305 `rq_set[] = { 61 }`. Today the pre-check is
asked on slot PRES (Q9), not FIND; routing it through T-FIND first match yields D1w. The critic's
conclusion (N9 belongs under T-PRES's rendering, not T-FIND) follows.

## PREMISE-3
**HOLDS.** generic.c:180-209 renders each RUN byte as its own `&&`-joined test: `S[..] == b`
(m == 0xFF), `(S[..] & m) == b`, or the constant `0` for a byte its mask clears. runcmp's first-match
rows (runcmp.c:108-131, predicates `rc_holds` :170-187): `words` = masked and len >= 2; `overlap` =
exact and len in {3, 5-7, 9-15}; `bytes` = any masked run (reached only by masked len 1, or under
the MF_D_RUN_OVERLAP deny); `memcmp` = every other exact run (len 1, 2, 4, 8, >= 16), "one
constant-length !memcmp". So an exact RUN never gets a per-byte `==` chain from T-CMP, and a masked
run of length >= 2 gets `words`; byte identity holds only for a masked len-1 run. U8's "asks T-CMP if
byte-identical" (subj:317) is empty for essentially every RUN term, so U8 is a unit change, and the
stage-1 count of one decider for T-CMP (Goal 3, subj:27-30) does not hold while generic.c keeps its
own compare. The subject's hedge ("else a separate unit change") is itself correct; the finding is
about the stage-1 accounting.

## PREMISE-4
**HOLDS (facts); consequence holds under a literal build.** Every FIND row's contract USES the
consumer kind or (R2) M/N: finder.c:207-218 (`use_kind` on R4, D1, D1c, D1w, PAIR; R7w :232
`use_kind`; `use_mn_kind` R8/R1; `use_mn` R2). gate.c header rule 1: "the row USES it and it is
UNSTATED: DECLINE"; finder.c:400-403 `kind_cl(MF_SK_UNSTATED)` = -1. R-33 data (verify/py/ofs.py over
sweep.jsonl): window sites by (form, handoff, site_kind) include (2=FUNC, 0, 0=UNSTATED) = 381
(RTE 371, DEF 10), every one ending wfE `E-func`, fn `fn-memchr`, NO fd row walked (381/381), all
stating alternatives (PARKED, RESEED). Today their method comes from ofsskip.c `fn_rows`
(:415-416; `pair_holds` = `x->b >= 0`, the one-bit cube of `ofs_fn_applies` :106-134, else
`fn-memchr`) and A-model's `scan_ok` (window.c:446-449: walked, core, one member), neither of which
asks fd. So the subject's equation "RESEED: candidates whose T-FIND answer is not memchr are
UNPRICED ... today's `scan_ok`" (subj:186) is not true on OFS sites: T-FIND built from today's fd
contracts answers nothing there. The "mass mover" consequence follows only if the build reads
T-FIND literally; restating scan_ok in the KEY row (the critic's own alternative) avoids it, so it
is a design-text defect with a stage-1 byte-identity risk, as the critic states. fn-pair's
condition (a one-bit cube at the scan position inside a RUN term) differs from PAIR's (any two
bytes + SF_WINDOW_STOP): HOLDS by code.

## PREMISE-5
**HOLDS (one cite misattributed).** window.c:42-44: "Every table is a `kit_table` on the one walk
(kit_walk; Tables A, M, D, E) or a declared row list read in order (C, TIE, and B's renderers ...)";
kit_walk is called only for A (:1000), M (:1010), D (:1738), E (:1821). `c_plan` (window.c:972-981)
applies EVERY row with `apply && holds`, in step order (step numbers 1-7 in `wf_crows`, :942-969):
cumulative, not first-match. C-table and C-own (step 6) are among Table C's 12 rows (subj:122,
"Table C's 12 rows unchanged") and are also listed as replaced by T-SETTEST (subj:124): double-booked.
`rd_set` (:251-254) reads `d->reseed`, which C-pin sets on a PARKED alternative (:877-878): HOLDS, so
PARKED readability is an output of the verify plan. Correction: the critic's ":819" is in `c_floor`
(:814-825), not C-model; the state-setting rows are C-floor and C-pin. Does not change the finding.

## PREMISE-6
**HOLDS (on the literal reading).** memfn/CLAUDE.md:28: "pcrec's sources reach the kit ONLY through
`memfn/include/memfn.h`; the kit links nothing from `src/`, `cli/`, `lib/`." The kit's only non-local
includes are `../include/memfn.h` (kit.h:14, k1_ref.c:12); grep finds `limits.def`/`src/core` in
memfn/src only as TEXT (plan_cost.def:50-53 provenance string "src/core/limits.def
PCREC_OFSK_MAX_SET ..."; options.def). PCREC_OFSK_MAX_SET = 4 at src/core/limits.def:393 (INTERNAL_H);
plan_cost.def `MAX_SET, 4`. U9's "`plan_cost.def` row reads `limits.def`" (subj:318; subj:201 "read
from `limits.def`'s `PCREC_OFSK_MAX_SET`") is a boundary crossing if "reads" means a build-time read;
if it means "cites", plan_cost.def already does and U9 deletes nothing. Either way the stage-1 line
as written is not a valid deletion; the fix's home (pcrec states it, or the kit owns it) stands.
(SLOT's PROBED-AND-HELD counted this as held; that was the "cites" reading.)

## PREMISE-8, MEAS-3
**PREMISE-8 HOLDS; MEAS-3 HOLDS (premise), extent conditional as the critic says.** memfn.h:1291-1294:
`consulted` is "1 iff some kit row whose decision the art's text CARRIES resolved a key against the
set, found or absent"; src/gen/memfn_stamps.c:280-291 `meas_stamp` returns "" unless consulted, else
`id@rev:digest`. Today no carried decision consults (finder.c:378 "lookups set `consulted` (never at
B1)", :862). Compiles 2-3/30 (review build): `(?i)x/1234` default and `--measures=zen4-grid1` both
carry `#define RX_MEASURES ""` (verify/c/smp20.c:311, smp20m.c:311). So once a stage-3 row's sites
price default and challengers from cards, the stamp moves from "" to `id@rev:digest` on that class
even where `keep` results, and a later card rev moves the digest again: bytes move without a pick
moving, against subj:409-411 ("it moves bytes only where a T-PICK row admits a departure and the new
prices change a dominance verdict"). MEAS-3's wider "every priced site" holds only if pricing runs
before the T-PICK condition (the subject does not order them, subj:142-178), so its extent is the
critic's own SUSPECTED. tests/memfn/finder_check.py:38-41 (check D, "every finder site under NO set
and the FULL synthetic set decides the same rows") and :43-44 (check F, "`consulted` is 0 on every
compile ... the true arms are OWED to the first row that does") exist as quoted: HOLDS.

## PREMISE-9, MEAS-10, OWNER-7
**HOLD.** plan.md `[MEMFN-UNBOUNDED-SPANS] STATE:not-started`, status "filed; nothing built",
trigger "(an MF_SITE_ABI event: pcrec abi bump, identity re-pin and spec hunk in the same change)".
Presence today is the finder's PRES slot: finder.c:836-841 `fd_scope` (ALL_PRESENT with
npspan/pspans -> FD_PRES), P0-P9 rows; compile 1 (vm1) shows `slot=PRES ... row=P0`. So subj:75
("presence states unbounded spans (D176 Q4)") and subj:267-268 ("every scenario routed through the
one call ... Abi: none if bytes are identical") rest on the unbuilt row. MEAS-10's other parts:
plan.md `[MEMFN-PAIRSTOP] STATE:not-started` HOLDS; roadmap.md:388-390 A-PLAN's prerequisites
"The kit's agreement ...; the first stream step that touches search sites (ride-along)" HOLDS (the
subject's "the split and stage 1 are one change", subj:97-98, takes that step). OWNER-7's parts:
`grep -n 'fold\|dropped'` over the subject: no hit, while D176 Q4 (decisions.md:9919) rules "One
general fold: ... the presence pass is dropped" HOLDS; D176 Q3 "as a new revision of the box's set"
and plan.md "as zen4-grid1 rev 2" vs subj:274 "a new set id per box per run" HOLDS; D176 Q3
"gated on the step-0 census" with no step-0 mention in the subject (grep `step.0`: none) HOLDS.

## PREMISE-12
**HOLDS (both parts; U4's reach under NONE unverified, as the critic says).** U5: presence.c:125-134
`tie_over` breaks a mass tie between member spans by `member_order` ("the one last in pattern order
first (a known position above an unknown one)") then the larger byte. `wf_ties` (window.c:79-104)
has six rows (T_MASS_STRETCH, T_MASS_SET, T_MODEL, T_CMODEL, T_MARGIN, T_WINDOW), all over offsets /
model order / MARGIN; none states pattern-order-then-byte. So "presence.c `tie_over` reads it"
(subj:314) needs a new `wf_ties` row. U4: `window_mass` (presence.c:101-114) under NONE (rate NULL)
returns `uniform_mass(k)` over the TOTAL member count k of the MF_PRES_WINDOW = 8 positions
(memfn.h:1620); a sum of per-position `kit_set_sum` (presence.c:89-96, NONE -> `uniform_mass(k)` per
set) is a sum of floors. Recomputed: `16*10**6//256` = 62,500; `8*(2*10**6//256)` = 62,496. The
`cube_mass` == `kit_set_sum` identity holds (both rate and NONE).

## PREMISE-13
**PARTLY.** REFUTED: "R-33's R2 sites are the DFA prefilter OFS sites (FUNC/RETURN, E-func)". R-33's
differ table (docs/dev/lanes/r33_sim/out/differ_keyB.tsv) puts all 95 `differ-alt` units at kind
`PF`, frame `E-stmt`, arows `A-parked/A-floor` (awk count: `95 PF E-stmt A-parked/A-floor`); e.g.
pr01 `(?i)hello.*world` is `PF E-stmt`. The OFS (E-func) units in that table are the 17 R3
`differ-stop` units. In the raw sweep (verify/py/pf.py) every PF site is form STMT, handoff ASSIGN,
wfE `E-stmt`. So the "FUNC-frame renderer" prerequisite and the "OFS units" rename are wrong.
HOLDS in part: item 3 (subj:288-289, "priced with PAIR/walk cards") presumes PAIR on E-stmt sites,
where PAIR has no renderer (PAIR needs SF_WINDOW_STOP, set only by fd_find under E-find,
finder.c:306/938; E-stmt walks via fd_route, R7w). That is the same gap the subject names for
item 4 (subj:290-291) but does not name for item 3; the walk half of item 3 renders today. The
terminology tension also stands, in a different form: the subject's "PF find states one alternative
with one candidate" (subj:74) is contradicted by these same PF sites (see SIM-8).

## PREMISE-14, SLOT-15, MEAS-8
**PREMISE-14 PARTLY; SLOT-15 HOLDS; MEAS-8 PARTLY.** memfn.h:39 `#define MF_SITE_ABI 20 /* layout and
meaning of every struct below.`; `mf_site` ends :820 and `mf_wreply` :1444, both below. The subject
grows the reply ("The plan reply grows from window_site's phase-1 reply ... by the method and
resume", subj:95-98, "the split and stage 1 are one change"), so an MF_SITE_ABI event in stage 1 is
certain, not conditional on `mf_site` (subj:271-272): HOLDS. REFUTED part (PREMISE-14's "house
practice treats an MF_SITE_ABI event as a pcrec abi event" and MEAS-8's "window_site §5.2 pairs
every MF_SITE_ABI event with a pcrec abi bump"): window_site.md:518 "The number reaches no artifact
... Check: S2's emit_sweep is byte-identical across the number change", and §5.2's abi row
(:546) gives S1+S2 "ONE `MF_SITE_ABI` event (+ `MF_CLASS_V`) ...; NO pcrec abi event", the pcrec bump
only in S3 where bytes move. plan.md pairs the two only for [MEMFN-UNBOUNDED-SPANS], a row that
moves statements. So the stage-1 truth is "one MF_SITE_ABI (+ MF_CLASS_V) event, no pcrec abi
event if bytes are identical", which makes Goal 2's "byte-identical to main but for the abi digits"
(subj:23-24) the inconsistent sentence, and SLOT-15's reading (two different numbers; say which moves)
the right one. MEAS-8's other parts HOLD: window_site §5.2's S1+S2 witness is "emit_sweep
byte-identical ... on every arm (default, each deny, `--engine=vm`, both SIMD layers), stamps
included; `tests/findings/manifests/*_movers.txt` unchanged; reach floors" versus the subject's
"main vs branch" over corpus/bench/588 (subj:395-397), with no arms named; plan_cost.def is
"1/100 cycle per subject byte" integers (plan_cost.def:17, :29-44, Zen 1 "ubuntubudu, Ryzen 5 1600")
while stage 3 prices relative to the walk (subj:157), so two cost systems coexist from stage 2 on.

## PREMISE-1, SLOT-6
**PREMISE-1 PARTLY; SLOT-6 HOLDS.** Code: Table E is the kit's (`wf_erows`, window.c:1447-1452, walked
by kit_walk :1821), legacy rows first. E-func/E-stmt hold via `e_legacy_holds` (:1386-1393):
`legacy_ok(...)` then `translate` and `kit_legacy_serves` over the translated PLAN; E-find holds iff
`e->fx->holds` (:1403-1407), i.e. the stop's find was decided and rendered (`wf_find_decide`). So
which renderer serves a site (and hence whether PAIR exists: PAIR needs SF_WINDOW_STOP, finder.c:306,
set only in fd_find :938) is a function of the plan: HOLDS. The PARTLY: window_site.md:92-94 says
"Phase 2, TEXT: pcrec states the frame its NEXT row chose", so the (form, handoff) half of subj:130
("chosen by pcrec's NEXT row from the reply") matches window_site; what pcrec does NOT choose is the
E row, which is what the T-FIND validity column needs. PREMISE-1's "false as written" overstates;
its substance (the validity-relevant frame class is the kit's, plan-dependent by construction) holds.
Data (verify/py/frame.py over the sweep): the E row is a pure function of (form, handoff, site_kind,
wfloor) on every sampled site (14 classes; 15 with `deleg`, each one E row); two-member stops
(verify/py/two.py) are PAIR on site_kind 6 REPORT (73 + 28 = 101) and R7w on kinds 1-4
(105 + 84 + 59 + 31 = 279): HOLDS. SLOT-6's numbers recomputed exactly: STMT form E-stmt 1,887,
E-find 1,021, E-func 200; FUNC form E-func 381; fd PAIR 101, fn-pair 61 (E-func 33, E-find 28),
both on one site 28. window_site.md:94-95 "The decision reads no frame fact" vs the subject's step-1
"frame class" fixed fact (subj:52) HOLDS; the subject says both "declared beside the renderer table
it mirrors" (subj:342) and "the renderer table's declared contract read at plan time" (subj:110):
the two readings SLOT-6 names are both in the text.

## SLOT-1
**HOLDS.** Goal 3 (subj:27-30) promises "exactly ONE per question: six question tables plus the pick's
one admission table". The subject's own stage-1 text keeps further deciders: the KEY table with three
rows (subj:180-187), the alternative default "today's MARGIN row" (subj:151-152; N2 "kept",
subj:321), ONE tie table `wf_ties` "that every level reads" (subj:133-134), Table E as "the emit
face's renderer selector", order kept (subj:131, N11 subj:330), vrun's KA/KB KEPT (U7 subj:316, N10
subj:329), and `run_member` (U2 subj:311; see SLOT-2), which is a least-mass argmin with its own tie
row (window.c:763-797, `tie_takes(T_MASS_STRETCH, ...)`). Whatever the exact tally the critic gives
(ten tables plus a column, a selector and two untabled answers), "six plus one" is not the stage-1
inventory, and the stop position keeps at least two deciders (KEY + `run_member`, plus KB under SIMD).

## SLOT-2
**HOLDS.** `run_member` (window.c:763-797) picks the least-`kit_set_sum` run position with
T_MASS_STRETCH ties; `c_plan` calls it before Table C's rows (:977); its answer leaves in the reply
(:1046 `out->run_member = d->member`). Recount (verify/py/runm.py over the sweep): 483 replies state a
run; in 31 the stop differs from the run member (30 with reseed=1 path `reseed`, 1 path `mass`);
examples reproduced: `\bcat\b` (DEF) stop 1 / member 0, `a{ , }` (smp17 DEF) stop 1 / member 5,
`\b(github_pat_[0-9a-zA-Z_]{82})\b` stop 6 / member 10. The subject's U2 row (subj:311) only unifies
its spelling; no table or pick level in §The tables owns it.

## SLOT-3
**HOLDS.** Table A is five first-match rows (window.c:637-648: A-empty, A-parked, A-model, A-mass,
A-floor); the KEY table names three, keyed on entry (subj:183-187). Recount (verify/py/arow.py; every
window site's wfA ends zipped with its stated alternatives, 0 length mismatches): NONE(1) -> A-mass
1,432; PARKED(2) -> A-parked 1,857; RESEED(3) -> A-model 415 and A-floor 1,420 (77 % of RESEED);
A-empty 0. The KEY table has no row for the RESEED/A-floor case ("no stop") and A-empty has no home
and no population, as stated.

## SLOT-4
**HOLDS (text).** The KEY rows' fate is stated four ways: subj:180 "deleted in stage 3 by the first
choice change" (all three); subj:282-283 item 1 "the no-entry KEY row (mass alone) is replaced by
the priced key"; subj:310 (U1) "stage 3 item 1 replaces both" (A-model's and A-mass's keys);
subj:320 (N1) and :321 (N2 MARGIN) at item 3; subj:327 (N8, the PARKED key) "stage 3: priced by
..." with no item. subj:278-279 says every stage-3 difference is "one `T-PICK` row, its deny"; item 1
instead replaces a KEY row, i.e. the level-(b) DEFAULT (subj:150-151 "the position the stage-1 KEY
row ranks first"). With the default itself replaced, the item's deny returns the new default, so
"RTE vs the row denied" (subj:279-280) no longer compares against today's answer. The consequence
follows from the text.

## SLOT-7
**HOLDS (forward-looking; no stage-1 effect).** subj:121 makes SIMD forms "FORMS of a row ...
applicable only at `-fmemfn-simd`"; subj:195 cards `find.byte` "per method x layer"; subj:142-143
level (a)'s winner feeds (b) and (c). Nothing restricts levels (b)/(c) to scalar prices, so a SIMD-on
compile can price a different stop/alternative. D147 (decisions.md:9002-9004): the scalar layer is
"the algorithm: what is searched, the plan, handoffs, ..."; SIMD "a LAYER on top ... never a
substitute"; window_site.md:274 (B-fn, D155's seam) "the SIMD-on artifact adds only guarded rungs over
the SIMD-off text". In stage 1 the SIMD forms are declined or kept (N12, U7), so the issue starts at
stage 3; the subject does not state the restriction.

## SLOT-8
**HOLDS; and the reach is provably zero, not just unobserved.** finder.c:250-281 rows R8, R3a, R3b,
R4, R1, R2 compare stated facts against keys `kit.lstar.W64.<kind>`, `kit.g8.W64.<kind>`, `kit.h3a`,
`kit.h3b`, `kit.gstar.<liner>.<kind>`, `kit.xover.<t>.WALK.<kind>`, `kit.block.W64`. Recount
(verify/py/fdrows.py): fd FIND rows reached in the sweep: D1 1,510, R7w 1,101, D1w 143, PAIR 101,
D1c 39 (exactly SLOT-8's numbers); none of the six. By code (finder.c:524-541 `cmp_eval`/`fd_holds`):
KN_H rows (R3a, R3b, R4) return 0 ("no iterator before B9"), FL_E_G (R8) returns 0, R1/R2 need
SF_TERMINAL_FAST. R1 (FF_WALK), R3a (FF_WALK), R4 (FF_WALK) pick a renderable walk, so N14's
"declined by the validity column (no renderer)" (subj:333) does not retire them; the two
representations (crossover keys vs `find.*` cards) are both in the design (subj:121, :195-210).

## SLOT-13
**HOLDS.** D153 (decisions.md:9250-9262) rules "don't live in a house we're remodeling": in-flight
refactors take priority over round 3, and "A round-3 row that touches a site under remodel
sequences AFTER the refactor that owns it". It names "memfn's zero-mover migration steps" as
examples of remodel work but nowhere states "refactors are no-movers" (subj:269). The critic's
consequence (stage 1 in flight would sequence smp04's unit change, subj:295-298 "lands independently
of stages 1-3", after it) is D153's principle applied by analogy (D153 itself is about round 3).

## SLOT-14
**HOLDS (a, b, c).** (a) D174 (decisions.md:9906-9908): new caller-facing names name behaviour,
"never ... lane or row ids"; the `--memfn=` namespace is grandfathered, the names inside it are new.
subj:279 spells the stage-3 denies `--memfn=no-<row>`. (b) The existing `--memfn=no-*` denies are
specified in docs/spec/tuning.md (e.g. §2.29¶1, §2.40), registry.md, cli.md and match_api.md (grep
`memfn=no-` over docs/spec); §What moves (subj:413-414) names only measures.md §8 and §5. (c) see the
MEAS-4 section below.

## SIM-1
**HOLDS (numbers recomputed independently).** The subject's formula (subj:161-165): `hits_r(S) =
m_r(S) (ppm; PAIR: m_r(a) + m_r(b))`, i.e. the set's mass, not doubled. R-33's `score()`
(docs/dev/lanes/r33_sim/sim.py:88-98) charges `m * streams * H_HIT` (streams = 2 for pair). My own
script (verify/py/smp20.py; Zen 1 /100 constants C_MEMCHR 0.06, C_BITMAP 1.16, C_VERIFY 2.5,
C_ENTER 20; H_HIT 20; prior x 997 + X 100 = 1,097, '/' 4,154, each digit 7,476; two verify compares
in ascending order) gives under P: {x,X} PAIR 144,693.9 vs '/' memchr 153,476.4 (ratio 1.0607: '/'
LOSES by 6.1 %); with PAIR hits doubled 166,633.9, which is R-33's differ_keyB.tsv:2 `166634.0` vs
`153476.5` = 1.086, the subject's "wins by 8.6 % under KEY B" (subj:251). Hit cost sweep: '/' wins
only below ~17 c (h 17: 141,403 vs 141,014; h 10: 133,724 vs 111,936, the critic's exact pair).
Under F: PAIR 295,857.5 vs '/' 147,966.9 (critic 147,929: a verify-order difference of 0.03 %,
immaterial). `cat|dog`-shape {c,d} 46,603 ppm with every hit entering: PAIR 1,984,120 vs walk
2,092,060 (c_hit(walk) 0) or 3,024,120 (c_hit(walk) 20): PAIR cheaper under P with the design's
formula, against subj:255 "the walk wins under P"; R-33's walk-wins figure is its doubled PAIR
(differ_keyB.tsv:24 `a0@0{c,d} ... pair s2916180` vs walk 2092060).

## SIM-2
**(a) HOLDS; (b) HOLDS as a text defect (the subject's own example disambiguates).** (a) subj:161-162:
scan terms are "streams x c_byte(method) x 1e6; walk: c_byte(walk) x 1e6; Horspool: (c_probe +
m_r(S) x verify) / E_r[shift]". With m in ppm, `m x verify / E[shift]` is per 1e6 bytes but
`c_probe / E[shift]` is per byte: the probe term lacks x 1e6. (b) subj:148 defines F as "`|S|/256`
per position" (a probability) while subj:163/165 use ppm (`pass_r(j) = m_r(set_j)/1e6`) and subj:255
quotes "7,812 under F" (= 2e6/256, ppm). A literal reading breaks the formula; the intended unit is
recoverable from the example, so this is doc severity, not an outcome the design gets wrong. (c)-(e)
(E[shift] undefined; whether Horspool also pays the hit/verify lines; unit vs fixed-point scale) are
absences in the text I confirm by reading subj:157-171: no definition of E_r[shift] or the
fixed-point scale appears.

## SIM-3, MEAS-1
**HOLD.** memfn.h:1189-1194: `mf_measure` = { key, value_e6, unit, source } ("source: display only; no
selection reads it"); no noise field. docs/design/measure_sets.md:948-950: "No provenance columns.
`abs_ns_e6`, `noise_e6`, `n`, ... are pcrec's listing's. A kit row that wants noise asks by REQUEST
... No selection reads noise today." measure_store/zen4-grid1/1/set.tsv rows section (awk count): 68
rows, `noise_e6` set on 0, `n` set on 0; 42 measured, 26 derived (MEAS-1's split exact). So the
subject's band (subj:240-243, "Each card row carries its A/A `noise_e6`") has no channel over the
"existing channel, no new fact" (subj:206-207) and no value in the one committed set. SIM-3's
departure counts are from its own simulator (sim/summary_base.tsv `ALL PF:alt 204` + `PF:pos 2` =
206; summary_noise0.tsv `PF:alt 230` + `PF:method 11` + `PF:pos 3` = 244): read and summed, not
re-simulated.

## SIM-7, PREMISE-15
**HOLD.** Count (verify/py/sim7.py over sim/units_base.tsv): 206 P-and-F departures = 204 PF `alt`
+ 2 COVER `pos`; all 204 are alternative 0 (PARKED) walk -> alternative 1 (RESEED) walk; stop
offsets 181 @1, 13 @2, 4 @3, 4 @9, 1 @4, 1 @8. Reason, checked on pr01 `(?i)hello.*world`: today
PARKED @0 {H,h} walk P = 2,048,200 = 1,160,000 scan + 44,410 ppm x C_ENTER 20 (no verify: every hit
enters); RESEED @2 {L,l} walk P = 1,235,590 = 1,160,000 + 29,333 x 2.5 verify + a small enter term.
Same scan cost both sides, so the gap is the PARKED plan paying C_ENTER on every hit vs the RESEED
plan verifying first; the subject prices `c_enter` per consumer kind only ("every plan of one site
hands to the same consumer, so only `passes_r` differs", subj:169-171), and F leaves the term
unchanged. Today's code does the same: window.c:391-395 `model_cost = scan + m*vc/PPM +
m*vr/PPM*COST(C_ENTER)/PPM`, A-parked calls it with vr = PPM (:420), so every parked hit pays
C_ENTER; MARGIN's 2x (plan_cost.def MATERIAL 2/1, "ARGUED") is what keeps PARKED today, and stage 3
item 3 deletes it (subj:321).

## SIM-5
**HOLDS on the three spot checks** (sim/units_pfpair.tsv, the PF-PAIR run; masses recomputed from
sweep.jsonl.rates.json: {a,b} 64,049, {g,t} 73,436, {c,d} 46,603, {a,o} 104,089 ppm).
- bench bounded/ctx-lazy-64: today PARKED @0 {a,f,p} walk P 2,794,860 / F 1,394,375; 3-level pick
  RESEED @1 {a,b} PAIR P 1,578,074 / F 296,013; the same stop's walk P 1,337,094 / F 1,179,763. PAIR -
  walk under P = 240,980 = (0.12e6 - 1.16e6) + 20 x 64,049: the walk is P-cheaper, PAIR F-cheaper, so
  neither beats the other at level (a) and the default (PAIR, first match) stands; the walk also beats
  today under both models beyond the printed bands (P gap 1.46M vs band 412k; F gap 214,612 vs band
  76.5k). Departs to a P-worse plan: HOLDS.
- bench syntax/alt-two `cat|dog`: pick RESEED @2 {g,t} PAIR P 1,787,990 vs the same stop's walk
  1,359,270 (GLOBAL column): same shape. HOLDS.
- corpus c00011 `cat|car|cap|dog`: 3-level keeps today (PARKED @0 {c,d} walk P 2,092,060 / F 1,316,250);
  GLOBAL RESEED @1 {a,o} walk P 1,444,568 / F 1,179,703 dominates beyond band (P gap 647k vs 240k; F gap
  136,547 vs 62.9k). At @1 the level-(a) default is PAIR, whose P is at least 0.12e6 + 20 x 104,089 =
  2,201,780 > 2,092,060, so it cannot challenge today and the dominating walk is hidden. HOLDS.
These are the critic's simulator outputs checked for internal arithmetic, not an independent re-run of
all 43 units.

## SIM-6
**HOLDS.** sim/units_pfpair.tsv utf8/alt-cyr-64: today @0 {\xd0,\xd1} walk P 1,160,080 / F 1,316,250;
pick PAIR P 120,160 / F 432,500. Recomputed: prior mass {\xd0,\xd1} = 4 ppm (rates.json), so PAIR P =
120,000 + 4 x 20 + 4 x 20 = 120,160 and walk P = 1,160,000 + 80; F mass 7,812.5, PAIR F = 120,000 +
156,250 + 156,250 = 432,500, walk F = 1,160,000 + 156,250 = 1,316,250. PAIR wins under both models.
R-33 lists the row as "utf8/alt-cyr-64: R1, 421x" (r33_report.md:257) and blames the prior ("{\xd0,\xd1}
reads as 4 ppm ... a facts problem", :260-263). In Cyrillic UTF-8 every letter is two bytes led by
D0/D1 (D2-D3 for extended letters), so these leads are about half the bytes: F (uniform 1/128 for the
pair) is far from that too, and the P-and-F rule passes the departure. In today's frames (base run) the
site keeps the walk; the departure appears once PF frames render PAIR (stage 3 item 4).

## SIM-8
**HOLDS.** verify/py/pf.py over the sweep: 1,767 sites with deleg PF (RTE 1,742, DEF 25); stated
alternatives (PARKED=2, RESEED=3) on 1,454, one NONE alternative on 291, one PARKED on 22. subj:74
says "PF find states one alternative with one candidate (span 0, pcrec's start set)" and subj:374-375
"the kit never picks another stop there", while stage 3 item 3 (subj:288-289) admits RESEED
candidates on R-33's R2, which are exactly these PF sites (95 units, all `PF E-stmt`, see
PREMISE-13).

## SIM-10
**HOLDS.** subj:150 makes the level-(a) default "T-FIND's first match", and T-FIND lists PAIR before
R7w (subj:121; finder.c:306-322 likewise, PAIR "above R7w, which it narrows"). With PAIR valid in PF
frames (item 4), the first match on every two-member PF stop becomes PAIR, so the default moves
without any `T-PICK` row. sim/summary_pfpair.tsv: R1 today=walk = 13 + 187 + 3 + 66 = 269 units; dense
no-dominance 187. The subject's own item-4 wording ("then the method level may choose walk over
PAIR", subj:291) confirms PAIR becomes the default; that contradicts the R1 bullet "no dominance, the
default stands" (subj:255-256) read with walk as the default, and it labels the flip a "unit
addition" (subj:290) where D186 would call a which-unit-where move a choice change.

## MEAS-2
**PARTLY.** HOLDS: measure_sets.md:122 "Sets. One box, one run, one method version, never mixed."
(ruled by D166); :409-412 "Cross-set comparison is only within one `method@ver`. A different unit
regime is a different method version"; spec measures.md:63 header `method` = "the method cards'
`owner-name@ver`" (one). memfn/data/cards/ holds kit-grid.tsv (`kit-grid@1`), kit-kernels.tsv,
kit-synthetic.tsv; its CLAUDE.md:8 "`kit-grid@2` (grid2's cards) is grid2's prep lane's". So a new
`kit-span@1` card file (subj:205) cannot share a set with kit-grid@1 grid keys; the subject's own
fallback (subj:209-210, "re-read under one method version") points at the same constraint without
naming its cost. NOT HELD: (1) "Re-read is not available": spec measures.md §8¶1 (:214) says "a second
reading of the same cells is published as a new `rev`", so a re-reading is provided for (whether a
re-read may change the method version is not settled by the text). (2) "a new set without the grid
keys ... moves every finder-pay site": the pay rule (finder.c:742-760, `pay_fill` :616) runs only on
intervals cut by non-terminal rows, which are the inert key-reading rows (see SLOT-8), and
tests/memfn/finder_check.py check D (:38-39) asserts "every finder site under NO set and the FULL
synthetic set decides the same rows" today. So no finder mover follows from dropping the keys on
today's code; that consequence is REFUTED. The reader-closure point (§7.3, no reader of span cards at
stage 2) I did not re-verify.

## MEAS-4, PREMISE-7, SLOT-14(c)
**HOLD.** spec measures.md:176 (5¶6): "Today there is one class, `idk` (a compile that declares
none), and its default is the latest committed set: `zen4-grid1@1`"; measure_store/DEFAULTS is the
one line `idk	zen4-grid1@1`; src/core/measures_table.inc:130 `{ "idk", "zen4-grid1", 1u }`. A compile
names a SET (`--measures X`, `.rxt` `measures`, `pcrec_options.measures`; 5¶1 :166), never a class.
cli/main.c's only `class` token (:144) parses a set FILE's header key; `--target NAME` (:1701) builds
one `.rxt` target by prefix (cli/CLAUDE.md). So subj:212-215 ("The set is the one the compile names ...
or its class's `DEFAULTS` row") and Goal 4's "measured on the target's class" hold only when the
caller names a set; a class-declaring input is unlisted work. Open question 2 (subj:425-429) covers
only the envelope.

## OWNER-1, SLOT-12, PREMISE-11, MEAS-9
**HOLD (the textual tension is real; whether it is a conflict is the owner's question, as all four
say).** D186 Relations (decisions.md:10028): "Pricing ([PRICE-BAKEOFF], deferred) returns only if
hand-written rows start conflicting"; Revisit (:10030): "the row table grows past what hand-written
rows can keep loss-free (pricing's trigger)". plan.md [PRICE-BAKEOFF] `STATE:deferred`,
status 2026-11-02 "DEFERRED, not a priority (Frank, after the pilot): default 0.981 of ideal held-out,
PASS at 0 rules ... is the baseline pricing must beat. Build waits for [STREAM]", next "revisit only
when an unmeasured choice shows headroom". pricing_requirements.md:11-20: "within-engine headroom is
about 2 % ... a pricing build waits for the stream work". The subject: stage 3 item 1, the first
choice change, replaces the no-entry KEY with "the priced key" (subj:282-283) and the pick prices
every level from cards (subj:142-171), while subj:177-178 says "When `T-PICK` rows start conflicting,
that is D186's revisit trigger and pricing's ([PRICE-BAKEOFF])", i.e. it treats pricing's trigger as
still ahead although its own first row already prices. Its authority is the 2026-11-02 direction
quoted in subj:3-8 and D176 Q1/Q3 (2026-10-23, decisions.md:9915/9917), earlier than D186. Mitigating
fact (all four critics note it): architecture.md:20-27 "a priced argmin ... An optimizer may sit
inside one row's action", so a T-PICK row with a priced action is permitted by the guide; no D-row
records that reading. MEAS-9's sizes check: finder 1,162, window 2,788, compose 1,451, presence 247,
runcmp 689, precheck 570, ofsskip 995, pffind 570, generic 871 lines = 9,343 (critic "~9.5k"): HOLDS;
its "about 6 units" for item 1 is the critic's own sign-only estimate, not re-derived.

## OWNER-5, SLOT-5, PREMISE-10
**HOLD.** D176 Q5 (decisions.md:9920): "prices within the measurement-noise band tie, decided by the
existing declared tie rows." Subject step 3 (subj:153-155): a challenger replaces the default only if
cheaper under BOTH models beyond the combined band, "Otherwise the default stands. Among several
qualifying challengers, the least P price wins; ties within a band go to the TIE table." So a
default-vs-challenger near-tie never reaches `wf_ties`; only challenger-vs-challenger ties do. The
subject cites D176 Q5 only for "fixed-point integers" (subj:158). `wf_ties` (window.c:79-104) has six
rows keyed on today's rules (T_MASS_STRETCH, T_MASS_SET, T_MODEL, T_CMODEL, T_MARGIN, T_WINDOW), none
for method/position/alternative ties under a band, and none that returns "the default". SLOT-5's
second point ("least P price wins" lets P alone choose between two P-and-F qualifiers, while
§Robustness says a P-only win keeps the default, subj:237-238) is in the text as quoted.

## OWNER-3
**PARTLY.** HOLDS: the subject's only evidence for the rates is job 588's subjects (subj:229-230,
"job 588's real subjects held x 2,338 against '/' 1,026 candidates (t588tri §a)";
t588tri_report.md:9 "real x 2338 vs / 1026"), and stage 3 item 1's acceptance is job 588 plus the
row's own run (subj:283-284), so no independent rate source is named. Overstated: the "never set
from a validation site" sentence (subj:351-353) is about the CARDS ("the cards are measured in
isolation, never fitted to end-to-end timings, never set from a validation site"), not the prior, and
Open question 3 already asks for "a separate facts change with its own evidence" (subj:431-432). So
the leaning does not break a stated rule; it leaves the independent source unnamed, which is the
fixable part.

## MEAS-7
**HOLDS, and more strongly than stated.** subj:404-405: "a plant that drops model F must flip smp20's
class witness". At smp20 F already favours the challenger '/' by about 2:1 (SIM-1: 147,967 vs
295,858), so with F the departure test is "P-win AND F-win" = "P-win", and without F it is "P-win":
identical. Dropping F can change a verdict only where P admits a challenger and F refuses it; smp20 is
never such a site, whatever the cards say (the critic's "may not reach" is in fact "cannot reach").
A reaching witness must be a site where F refuses a P winner (e.g. the R1 dense pairs, where per the
subject the walk wins under P and PAIR under F, subj:255-256). The other MEAS-7 points (F was
motivated by smp20 and smp20 is item 1's validation site; the "every cost read is a declared row"
check is counted from the kit's own consult recorder) are as the text reads; the second I did not
probe in code.

## Summary
Compiles used: 3 of ~30 (vm1 trace build; smp20 x2 review build). Scripts: verify/py/*.py.
HOLDS: PREMISE-2, -3, -4, -5 (one cite misattributed), -6, -8, -9, -12, -15; SLOT-1, -2, -3, -4, -5, -6,
-7, -8 (reach provably zero), -12, -13, -14, -15; SIM-1, -2, -3, -5 (3 spot checks), -6, -7, -8, -10;
MEAS-1, -3 (extent conditional), -4, -7 (cannot reach, not "may not"), -9 (facts), -10; OWNER-1, -5,
-7; PREMISE-7, -10, -11 (as an owner question).
PARTLY: PREMISE-1 (window_site says pcrec states the frame; the E row is the kit's), PREMISE-13 (R2 is
PF/E-stmt, not OFS/E-func; only PAIR lacks a renderer), PREMISE-14 and MEAS-8 (MF_SITE_ABI certain,
but window_site §5.2 had NO pcrec abi event for a byte-identical seam change), MEAS-2 (one-method rule
holds; "re-read unavailable" and the finder-mover consequence refuted), OWNER-3 (the no-fitting
sentence is about cards; Q3 asks for its own evidence).
REFUTED outright: none; the refuted parts are inside the PARTLY ids above.
VERIFY COMPLETE
