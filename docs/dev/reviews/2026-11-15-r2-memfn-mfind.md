# Review 2026-11-15 r2 memfn-mfind: the inline one-member finder (code, light)

DRAFT by the round coordinator, PROPOSED dispositions; the kit manager rules them.

## Subject
- SUBJECT lane/memfn-mfind = a2b2b2a08aa11f5297698aefd18de17a12dcd64b; BASE (merge-base main) = 4e435603b.
- Rulings frozen at main 77a8743e1 (decisions.md/plan.md 41b65ea00). FREEZE DRIFT at hand-back: none
  (main moved to 0361f7ce0; decisions.md, plan.md, plan_frame.md untouched since the freeze). Subject unchanged.
- The unit: fn-mfind (SWAR BODY row) and mfind-w16/-w32 (PREFIX rows) in ofsskip.c fn_rows[], one
  renderer vrun.c mfind_text, UNPICKED (test-only lever `mfind`, `pcrec-harness --harness=mfind`), kit-grid
  ver-6 cards, G2 family run_g2_mfind.py (plants S3150-S3159), S3170 lever witness in simd_guarded_check.py,
  G7 fence allowlist. Claimed: 0 movers under default flags, no abi event.
- Ruling in force for the shape: docs/design/memfn/plan_frame.md "RULED (Frank, 2026-11-07): row 1 waits for
  an inline one-member finder and its measurement card" (at 77a8743e1, ~:1425) + its comparisons table; D190.

## Lenses as run
| lens | model | question | why chosen |
|---|---|---|---|
| emitted vs replaced | opus | (a) the lever arm's C vs fn-memchr: answers and over-read at the buffer ends, and is the guarded-bytes bound a bound; (b) default byte identity BASE vs SUBJECT | emitted C, a zero-mover claim |
| check adequacy | opus | (a) can each plant S3150-S3159, S3170 (+ re-aimed S686, S2930) fail, does a witness reach it, is its class right; (b) G2 control independence, does the row tally reach the unpicked rows | >5 new plants (opus per skill) |
| contract + ruling check | opus | (a) lever unreachable from shipped paths, stamps/replies/docs say what the code does; (b) built shape vs the 2026-11-07 ruling, D190; + standing questions (family sibling, general form + unlocks) | caller-facing lever plumbing; rulings relied on |
Verifier: sonnet, over every CONFIRMED finding that would change code or a design.

## Which lens caught what
- emitted: the guarded bound overrun (with checks), the chain written twice, the SIMD-off speed question.
- checks: the guarded bound overrun (independently), every plant/population finding.
- contract: RUN_WORDS sibling rule, frame reply misdescription, the ruled-shape deviation, the card's
  comparator, the family/general form, a wording slip.

## Findings and PROPOSED dispositions

### F1 = EMITTED-1 + CHECKS-1 (both lenses; verify HOLDS): MFIND_W16/W32_GUARDED_MAX is not a bound
Size-contract/check design. The 1400/1500 are G2's seed-sweep maximum (vrun.c says "not a bound on the
space") but simd_bounds.tsv and kit.h/vrun.c define guarded_max as THE per-row bound that
simd_guarded_check.py holds artifacts to. Verified: `a.*\x7f[acegikmoqsuwy]{12}` under the lever,
RX_SIMD_GUARDED_BYTES 4089 at x86-64 (bound sum 2100) and 7831 at x86-64-v3 (sum 3600);
`b` + 28 x `[0-35-7]`: 2335 / 4323. Green today because the only lever witness is `foo.*bar` and G2's
generator draws at most 4 terms, offsets <= 16. Also: mf_formdecl.guarded_max is read by nothing (grep), and
"the kit's guarded_max is pinned equal to it" names no check.
**PROPOSED: FIX-NOW** (before landing): derive the bound from MF_MAX_TERM x the widest term's text, or cap
the helper's chain, or relabel it as non-bound; add a long-chain LEVER_NAMED witness (either pattern above);
pin guarded_max == simd_bounds row or drop the claim. Reason: a declared bound that a real pattern breaks turns
red the day a table picks the row; the fix is small now and owed anyway.

### F2 = EMITTED-2 (verify PARTLY): the verify chain is written twice in the body (+ once per helper)
Size. Verified: SIMD-off artifact 28581 -> 32218 bytes, x86-64-v3 29198 -> 40015 on the F1 pattern. The
RX_RUN_WORDS part of the claim did not reproduce on that pattern (see F3).
**PROPOSED: PLAN** (one text copy: the short span falls into the final-block path, or one shared chain).
Reason: lever-only, no answer effect; it feeds F1's size and belongs with the card's measurement.

### F3 = CONTRACT-1 (verify HOLDS): RX_RUN_WORDS counts the mfind helpers' compares; vrun's are excluded
Doc/maintenance (stamp). `foo.*bar` under the lever: 2 at SIMD-off, 4 at x86-64-v3; vrun's `(?i)hello` 1 at
both. compose.c:1543's rule ("a SIMD helper's own compare is not counted") is kept by vrun_verify's
save/restore of art->words and not by mfind_text.
**PROPOSED: FIX-NOW** (save/restore art->words around the helper path's chain). Reason: tiny, and two
siblings must not keep two rules for one stamp.

### F4 = CONTRACT-2 (verify HOLDS by trace): under the lever the frame reply says search NONE, stream RESTART
Doc (kit public contract). window.c:2517 maps FF_MFIND (> FF_HORS) to MF_WSEARCH_NONE; :2616 takes stream
from ren_fused[RF_FN] = RESTART; the rendered text is a MASK stream (MF_WSTREAM_MASK exists). memfn.h's
search/stream paragraph and the mf_lever doc are silent; only kit.h admits search NONE.
**PROPOSED: FIX-NOW (doc)**: memfn.h mf_lever doc states the reply under the lever is not updated (search
NONE, stream RESTART), or the reply reports MASK. Reason: the D190 triple is what the reply exists to state;
pcrec's src/ reads neither field, so doc now, values when a table picks the form.

### F5 = CONTRACT-3 (verify HOLDS as a reading): the built shape is not the ruled shape
Design. Ruled: "a T-FIND row, a search renderer row and its card ... that unit builds the first MASK stream
renderer row, and it must bring the evidence row ST-many needs". Built: a fused E-func BODY row of fn_rows
(search, MASK stream and check in one renderer), no T-FIND row, no window.c search or stream renderer row, no
RESTART variant (so no ST-many evidence). The subject states this itself (kit.h FF_MFIND comment). Not a
parallel mechanism strictly (fn_rows is an existing table, the row is unpicked), but plan rows triggered by
"the first MASK stream RENDERER ROW lands" ([RUNG-LIST], [PIECE-ACCEPT-RULE]) neither fire nor say they don't.
**PROPOSED: needs a RULING (owner/kit manager)**. Coordinator leaning: accept as STAGE 1 (the form exists,
is exact, measurable, lever-only, zero movers) and record it in plan_frame.md / the finder unit's row as stage
1 of N, naming stage 2 (search renderer row over mfind_mask, an S-mask stream row, a T-FIND row, a RESTART
variant) as owed BEFORE row 1, so the row-1 gate does not read as discharged. DOC now, PLAN for stage 2.

### F6 = CONTRACT-4 (verify PARTLY): the ver-6 card's comparator is the libc bundle, and its wording overclaims
Design/doc. The card compares fn-mfind with fn-memchr and calls it "like-for-like ... names only the search
and stream pieces"; the ruled table says libc memchr vs the finder is "a BUNDLE of three, named as one" (call
boundary, own code vs library, search) and also differs in stream. Verifier: the wording overclaim holds; that
row 1's card must be the SEARCH cell is an interpretation, not shown by the text.
**PROPOSED: DOC (fix-now wording)**: the card comment names itself the bundle comparison; the ruled SEARCH
(vs walk) and STREAM (RESTART vs MASK) cells are listed as owed with F5's stage 2. Ruling on whether the bundle
card satisfies "its measurement card" goes with F5.

### F7 = CONTRACT-5: standing questions (family sibling; general form + unlocks)
Design. Three block-search members now hand-write one skeleton: vrun_render, vany_level, mfind_text (entry
test with rung fall-through, full/overlapped final block, `while (m) { ctz; check; m &= m - 1; }`); vany keeps
a second ops_of copy; B-memchr is the same one-member search on E-find with RESTART (two homes). General form:
a block SEARCH row (lane producer SWAR | level compare; K = 1..3 members; optional second position), a STREAM
row (MASK | RESTART lowest lane | caller's; final-block masking is a stream fact), a CHECK row, one skeleton.
Unlocks with triggers: the STREAM cell (row 1's first comparison); the finder on E-find beside B-memchr/B-walk
(same); vany as K=2-3 of the skeleton (first 2-3-member non-run cube site); a portable SWAR level for vany/vrun
at SIMD-off (a card showing mfind-swar beats fn-memchr OFF); [RUNG-LIST] per-rung facts (as filed).
**PROPOSED: PLAN** (fold into F5's stage 2 as the unification; at 3 members, per the forest-for-trees rule).

### F8 = CONTRACT-6: "the libc stream" misuses D190's word
Doc. memfn.h:1608, kit-grid.tsv ver-6 comment, data/cards/CLAUDE.md: memchr is the SEARCH (LIBC), its stream
RESTART; the lever swaps both. **PROPOSED: FIX-NOW (doc, trivial)**: "in place of the libc memchr search (and
its restart stream)".

### F9 = CHECKS-2 (verify HOLDS): S3150/S3151 fault by a runaway loop, not by the one-byte bound
Check design. The plants break loop exit (`i += VW` lands at e + 1, `e - i` wraps): verified S3150@body faults
rc 139 with NO guard. No plant shows the s + n guard catching a termination-preserving one-byte over-read.
**PROPOSED: FIX-NOW**: add a termination-preserving top-bound plant (`const size_t e = n - D;` -> `n - D + 1`,
or `pos + maxk >= n` -> `> n`), expected FAULT; note S3150/S3151 as runaway witnesses. Pair with F10.

### F10 = CHECKS-3 (verify HOLDS by repro + reading): G2 never plants the scanned byte past the last valid candidate
Check population (K35). g2_mfind_driver.c filler() never returns `a`, every plant is at c <= hi = n-1-maxk,
so a hit in [e, n) arises only by chance; no census counter names it. Verified: `e = n - 2` -> `n - 1` on
`foo.*bar`, subject `xxfoo`+29 y+`ba`: nomatch rc 0 without a guard, SIGSEGV under GUARD=end.
**PROPOSED: FIX-NOW**: subject() plants the scanned byte (and leading passing terms) in [e, n) about half the
time, a `beyond` counter with a floor, and F9's plant row for the D > 0 spelling (expected FAULT).

### F11 = CHECKS-4: S3153 `no-final-mask` (SAME) is a specificity control + text pin, not a check of its property
Doc. SAME is right (a re-handed lane was already rejected by a pure check); the "must not be handed over
twice" / "no byte compared twice" claim is a cost property no check counts. **PROPOSED: DOC**: say so in
PLANTS and soften vrun.c's "must" to the cost claim.

### F12 = CHECKS-5: G2 holds the site shape constant; the omitted shapes are pcrec's own
Check population. g2_mfind_gen.c fixes op FIND, policy NONE, empty MISS, <= 4 terms, offsets <= 16; pcrec's
lever witness is a pre-check-part site (`rx_reqrun`), never in G2; policy SIZE / the INLOOP decline nowhere.
run_axes.sh's lever arm runs SIMD-off only, so mfind-w16/w32 on pcrec's own sites are answer-checked by
nothing (the emitted and checks critics' own probes found 0 differences: see PROBED-AND-HELD), and a pre-check
consumer reads only `>= n`. **PROPOSED: FIX-NOW (small)**: one pre-check-part site and one INLOOP/SIZE site in
G2's space with census floors; a SIMD x lever arm (`--harness=mfind -fmemfn-simd=x86-64-v3`) in INTERNAL_ARMS
or a corpus sample. (If the manager prefers, the axes arm alone is FIX-NOW and the G2 space PLAN.)

### F13 = CHECKS-6 (verify PARTLY): S3158 `lane-shift` declared LOUD but faults often
Check fragility. Verified 354 FAULT / 22 MOVE in 1,500 random cases; run_g2_mfind.py classes a signal on a
LOUD plant as FAULT != LOUD, a red; green today rests on the fixed seed's first deviating case (inference, not
re-run). **PROPOSED: FIX-NOW (trivial)**: accept {LOUD, FAULT} for LOUD plants (or declare S3158 RED either way).

### F14 = CHECKS-7 (verify HOLDS for ROWS_FLOOR): two K35 literals not raised; the fence allowlist cannot see an invented entry
Maintenance. rows.tsv 33 -> 36 rows, run_rows.sh ROWS_FLOOR=33 unchanged against its own header rule;
run_g2.sh FLOOR_ROWS=20 unchanged (23 by reading, unverified). run_lever_fence.sh: a deleted ALLOW entry goes
red, an invented one is green (pre-existing shape; the subject widens it by a whole file).
**PROPOSED: FIX-NOW** for the two floors (36, 23 after counting); **PLAN** for the fence's "each ALLOW
alternative matches a mention" control.

### F15 = EMITTED-3 (SUSPECTED): SWAR at SIMD-off vs glibc's vector memchr on sparse long subjects
Speed. Not timed (no window). The card is UNMEASURED and nothing picks the row, so no rule is broken.
**PROPOSED: NOTED** (the ver-6 card's sparse-subject cell is the measurement; no selection at SIMD-off before it).

## PROBED-AND-HELD (summary; full texts in review/)
- Answers and memory safety of the lever arm: 438,102 whole-matcher runs vs libpcre2 at -O2 and again at
  -O3 -march=native, 219,051 under ASan+UBSan on exact-size buffers, 0 bad; a direct function differential
  lever vs fn-memchr, 7,979,100 inputs x 2 guard placements, -O0/-O2/-O3 native/sanitizers, 240 binaries,
  0 position differences, 0 faults (emitted). 12 x 6,000 control runs over 4 geometries x 3 levels, 0 moves
  (checks). 54 cases vs p2 (contract).
- SWAR exact-mask formula: exhaustive 33,554,432 lane checks, 0 wrong.
- Default byte identity BASE vs SUBJECT: 390 pairs (130 corpus patterns x 3 layers), 0 moved (emitted);
  16 pairs (contract). The lever moves only one-byte offset-skip scans (2 of 8 patterns).
- Lever unreachable from shipped paths: plain pcrec refuses `--harness=mfind` and -f spellings; the strcmp is
  under #ifdef PCREC_HARNESS; no public API/env/.rxt/--memfn= route.
- D155 (no #if; ordinary if on __BYTE_ORDER__; w32 -> w16 -> body), D149 labels, D174, D80 (spec correctly
  silent), the lever memory rule: held.
- Plants: S3150/S3151 FAULT (12 cells), S3152/S3157 FAULT at k = 0 only (as argued), S3153 SAME, S3154 via
  G2's trap alone, S3155/S3156/S3159 LOUD only, S3170 DETECTED, S686/S2930 re-aims intact,
  m6read_check_sab_anchors.py: 1,300 sabotages, all anchors resolve.
- G2 oracle independent of the kit (ref_find, no kit header); row tally (rows_check.py A/C/D, run_g2.sh 4b)
  reaches the three unpicked rows; deleted/invented rows.tsv and simd_bounds.tsv lines go red.

## By-id completeness
EMITTED-1 F1, EMITTED-2 F2, EMITTED-3 F15; CHECKS-1 F1, CHECKS-2 F9, CHECKS-3 F10, CHECKS-4 F11,
CHECKS-5 F12, CHECKS-6 F13, CHECKS-7 F14; CONTRACT-1 F3, CONTRACT-2 F4, CONTRACT-3 F5, CONTRACT-4 F6,
CONTRACT-5 F7, CONTRACT-6 F8. All 16 critic ids dispositioned; verify covered every CONFIRMED code/design
finding (EMITTED-3, CHECKS-4/5, CONTRACT-5/6 not verified: suspected, doc or standing-question items).

## Summary of PROPOSED dispositions
FIX-NOW: F1, F3, F4 (doc), F6 (wording), F8, F9, F10, F12, F13, F14 (floors). RULING: F5 (with F6's card
question). PLAN: F2, F7, F14 (fence control). DOC: F11. NOTED: F15. No answer-level finding; no default mover.

## Lessons for the guide (proposed)
- A per-row "measured" bound drawn from a generator's own space is a control that shares a source with what it
  controls (learnings §3): the witness population must include the widest text the row can render (pcrec-scale
  predicates), or the number is labelled a sweep maximum, never a bound.
- A bound plant that also breaks loop termination proves "the exit test exists", not the bound: pair every
  runaway plant with a termination-preserving one-byte plant.
- The test-only-lever pattern needs its own reach control at every layer the row renders (an axes arm at
  SIMD-off alone left the SIMD rows answer-unchecked on pcrec's sites).

## RULED (kit manager, 2026-11-15 03:30; fixes HELD by Frank's stop for tonight)

- FIX-NOW, as proposed, for a fix lane once the stop lifts: F1, F3, F4, F6, F8, F9, F10, F12, F13, F14 (floors).
  - F1: derive the bound from MF_MAX_TERM x the widest term's text, or cap the chain. Do NOT relabel it, because simd_guarded_check.py reads it as a bound. Add a long-chain LEVER witness (`a.*\x7f[acegikmoqsuwy]{12}`). Pin guarded_max to its simd_bounds row, or delete the unread field.
  - F9: pair every runaway plant with a one-byte plant that keeps the loop terminating.
- F5 RULING, the kit's leaning: accept as STAGE 1. The form exists, is exact and measurable, lever-only, zero movers. Record stage 2 in plan_frame.md and the finder unit's row: a search renderer row over mfind_mask, an S-mask stream row, a T-FIND row, a RESTART variant (ST-many evidence), and the vrun/vany/mfind skeleton unification (F7). Stage 2 is owed BEFORE row 1, so the row-1 gate does not read as discharged. [RUNG-LIST] and [PIECE-ACCEPT-RULE] are main's plan rows: sent to main to confirm.
- PLAN: F2 (one verify chain), F7, F14's fence control. DOC: F11 (S3153 is a specificity control; say so). NOTED: F15 (the ver-6 card's sparse cell measures it).
- F5 RULED (Frank 2026-11-15, via main): instrument only. The fused mfind row (fn-mfind, mfind-w16, mfind-w32) is an UNPICKED MEASURING INSTRUMENT only: never a pick, never "stage 1". Tonight's timing is a one-sided test: a fused loss to libc settles row 1 against the finder; a fused win triggers the 2026-11-07 ruled split shape (T-FIND row, search renderer + card, S-mask stream row, RESTART variant) under its own build go, then a re-measure.
- Lessons 1-3 and the COMMON change (drive a pre-check site's static function, compare the returned position): relayed to main for the guide.
