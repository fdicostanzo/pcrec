# Review 2026-11-05 r4 — alt_normal_form rev 1 (design, RE-CHECK)

## RULING (manager, 2026-11-05)

Every PROPOSED disposition is ACCEPTED as drafted (FIX-NOW list, DOC, NOTED, PLAN: SIM-5 and the general-form G-1..G-4; REJECTED none). Verdict accepted: stages 1 and 2p ready with the listed text fixes; 2b NOT ready (SND-1 side effects between merged branches; SIM-1 one sibling-merge spec); 2a census-first; 3 waits on [POS-ONE-DETECTOR]. Rev 2 (text only) applies the fixes; the readiness lens re-reads stages 1 and 2p only. Owner questions (flag-bit budget; the hull as a second shape under D187) go to Frank with the rev 1 questions. Process change adopted: COMMON tells critics that a harness-refused findings file is returned as final text and marked 'relayed' in the draft (critic skill §5).

## Subject

- `docs/design/alt_normal_form.md` REV 1 (lane altrev1) at its own commit
  `f7fd1a759241a5c22a090bd4f14603c8130013ee`; build tree main HEAD
  `569c57d3a7f9ad323ad2a56e69508bfbf4ed8309` (merge of lane/altrev1). No file
  under src/ cli/ lib/ memfn/ scripts/ tests/ moved between the two; the
  note's §2.3 ledger says "base 7ffbd4deb", and every cite holds at 569c57d3a
  too (fix, readiness).
- Rulings frozen at 569c57d3a. FREEZE DRIFT at hand-back (main `f15f30f25`):
  decisions.md and the note unchanged; plan.md changed by lane vlbrev1
  ([VLOOKBEHIND] status → rev 1, new HELD row [LB-EXIST]). No row this note
  cites by ruling moved; [VLOOKBEHIND] bears on SND-5 (lookbehind bodies).
- Review tree `worktrees/crit-altnf2` at 569c57d3a, built once unlocked
  (`nice make -j2`, rc 0); removed at hand-back (wtprune).
- Population: altrev1_evidence, altdesign_evidence, altthink_evidence,
  rpsurvey_evidence + the two study reports, copied read-only.
- Prior round: `docs/dev/reviews/2026-11-05-r2-alt-normal-form.md` (critics
  read it; its §14 map was the fix-induced lens's checklist).

## Lenses as run

| lens | model | question | why chosen |
|---|---|---|---|
| fix-induced (+ ruling check O1-O5/D-rows, + standing: sibling of a family, general form + unlocks) | opus | per claimed fix: what read/row/field/check/flag does it add; trace siblings and readers in today's code | a re-check of a revised design |
| soundness | opus | apply the adjacency test, factoring rules, island set-edge reading, piece-set fact, as written, to crafted witnesses vs libpcre2; can each sabotage witness fail in both builds | rev 1's answer-identity-by-proof claims (C2 adjacency rule) |
| readiness (+ goals) | opus | per build unit: cites hold, gates/witnesses runnable and can fail, separable, readers complete; overall verdict | rev 1 is close to a build go for stage 1 |
| simulate (+ measurement) | sonnet | re-implement §6 table and §3.3 strategy from text; recompute every new number; U1 predicate tightness | a rule table + strategy + quoted numbers |

Not run: owner criteria (the owner's criteria in force are rulings O1-O5,
folded into fix-induced's ruling check); premise (ran in r2; fix-induced
traced the additions); cost/overlap (folded into readiness/fix-induced).

Delivery: fix, soundness, readiness ended on lanecheck DONE. **simulate's
findings were RELAYED via the manager; its own findings file was not written**
(a harness rule refused its report-file Write; it did not route around it).
Its text is `review/sim.md`. Verifier (sonnet) ended DONE.

## Which lens caught what

- soundness: SND-1 (answer: side effects in the intervening branch), SND-2,
  SND-3, SND-4, SND-5.
- fix-induced: FIX-1..FIX-10 (no FIX-9 verified: SUSPECTED), ruling check,
  family/general form.
- readiness: RDY-1..RDY-9, per-unit verdict table.
- simulate: SIM-1..SIM-6.
- Overlaps: SND-2 = FIX-2; FIX-1 = RDY-1; FIX-4 = RDY-2; FIX-3 = RDY-7
  (+ RDY-5).
- Verifier: HOLDS 14, PARTLY 6 (FIX-3/RDY-7 counts, RDY-3 consequence,
  RDY-4, RDY-8, SIM-1, SIM-4), REFUTED 0. `review/verify.md`.

## Findings (consolidated) with PROPOSED dispositions

Answer level

| id (lenses) | finding | verified | proposed | reason |
|---|---|---|---|---|
| SND-1 (soundness) | §3.2's adjacency test is about STRINGS only and its shortcut "capture-free branches of EQUAL width always pass" lets j move past an equal-width m that has a SIDE EFFECT. `\K`: `(?:ab\|a\Kd\|ad)` on `ad` = (1,2) in libpcre2 and pcrec; the merge the test allows, `(?:a[bd]\|a\Kd)`, = (0,2). Capture: `(?:ab\|(a)d\|ad)\1?` on `ada` (0,3) → (0,2). Lookahead, atomic, `^` in m held. New with 2b's non-adjacent merge (altcls today merges adjacent only); stage 1 immune. | HOLDS | FIX-NOW (text) | "decidable" = has an EXACT §3.5 description spanning the whole branch (captures excluded, ZERO kinds such as `\K` cut); equal-width shortcut becomes "equal width AND such a description"; add `(?:ab\|a\Kd\|ad)`/`ad` as an S-d witness |

Speed / size / gate level (a correct build would go red, or an unlisted choice mover)

| id (lenses) | finding | verified | proposed | reason |
|---|---|---|---|---|
| SND-2 = FIX-2 (soundness, fix) | PREM-1's fix over-reaches: "read a set position inside an A_WCLASS as its members" also admits TODAY's multi-member boxes (`u8_box` ranges), declined today by `vm_isl_single`. `x(?:[éè]1\|q2\|r3)y` and `x(?:[\x{100}-\x{17f}]1\|q2\|r3)y` islands 0 today, would become 1; Gate U4's "islands equal" is red on a correct build; "today's word list" is false. Answers safe. | HOLDS | FIX-NOW (text) | either list range-box island admission as a predicted (choice) VM mover with U4 = "base ∪ predicted" from the box model, or keep the singleton rule and accept `[éà]` 1 → 0 (S-i then a decline witness); the post-merge tree cannot tell a merged set from a box range without a new field |
| RDY-3 (readiness) | Unlisted stage-1 CHOICE mover: `vm_det_seq` (emit_vm.c:1885-1928) declines A_ALT/A_EMPTY under the seal, so a quantified multi-box class takes the frames rung; merged it becomes a deterministic stride. `(?i)xé+y` utf8 VM `RX_VM_RUNGS 0x4u`, 3319 B; the byte spelling of the merged tree `0x1u` (cursor), 1078 B. | HOLDS (measurement); PARTLY (stage tree not built, byte stand-in) | FIX-NOW (text) | add rung flips to stage 1's predicted movers/choice cells, an `RX_VM_RUNGS` census beside the island census in U4, `vm_det_seq`/`vm_cursor_fits` to §2.1; 2b moves the same reader |
| FIX-4 = RDY-2 (fix, readiness) | Gate B0's instrument cannot give an empty diff for a correct stage 1: `emit_sweep.py --bases` is read only in `--variant`/`--data` modes; the facts stream is hard-wired `--emit-facts=byte,utf8`; the composition stream compiles utf8 `.rxt`s with their own directives. | HOLDS | FIX-NOW (text) | spell B0 as a runnable byte-only population (byte argv streams, facts filtered to `byte` rows, `.rxt`s compiling at byte, or a `--variant` no-op at `--bases byte`), the utf8 halves going to U1; refusals counted |
| FIX-1 = RDY-1 (fix, readiness) | §3.6's "the row is -Wswitch-complete, so a missed reader is a compile error" is false for a new TEXT value: the -Werror=switch pragma covers only `pcrec_kind_row`'s switch over AKind; four TEXT switches only WARN outside `make strict`; `possessify.c:446/501/924` are `== KTEXT_ZERO` tests nothing catches (a miss silently declines possessify / the Glushkov build and moves BYTE artifacts in a stage whose census models only the run). The reader LIST is right. | HOLDS | FIX-NOW (text) | drop the claim; either a `text_is_zero` predicate at the three `==` sites, or keep A_EMPTY at ZERO and put the unit in its own column (KIND_ROW arity makes that a compile error; see FIX-9); stage 2a gate adds a byte emit-diff limited to predicted movers |

Design level

| id (lenses) | finding | verified | proposed | reason |
|---|---|---|---|---|
| FIX-3 = RDY-7, + RDY-5 (fix, readiness) | §11 gives stages 1, 2a, 2b, 3 a public deny each; 58 of 64 flag bits are used (0-54, 56, 57 defined; 55 the kit's), 6 free; [IFACE-PUSH]'s HARD TRIGGER opens at ≤ 4 free: the second new bit trips it. The note never names the budget, [IFACE-PUSH] or [FLAG-ACCESS]. Stage 2b replaces altcls, which already has public bits 10/11 (`-fno-altcls-merge`/`-factor`, tuning.md §2.6/§2.7, whose ¶1 wording becomes false); their stamps, spec text and tests are not in 2b's reader list; §2.6¶2 records the merge deny moves the refusal set (K45), and stage 1's merge can move the utf8 refusal set (unlisted). | HOLDS (conclusion); PARTLY (RDY counted 7 free) | FIX-NOW (text) + QUESTION | decide in the note: 2b re-specifies bits 10/11 (spec hunks, stamps, tests, mech S66/S67), stage 1's lever public, 2a/3 test-only until a loss shows (memory "flag follows caller effect"), or put the bit budget to Frank before the stage-1 go; add the utf8 refusal set to U1 |
| FIX-7 (fix) | Phase contradiction: §3.5 builds the description over the LOWERED tree in req.c's walk and names "altcls/the owner" a reader, but altcls runs before the call graph and lowering (compile.c:2819 → 2854 → 2962), at code-point level. Either a second, code-point description (the parallel mechanism G3 removes) or a two-level description §3.5 does not state. | HOLDS | FIX-NOW (text) | state the description as a pure function over a subtree parameterized by alphabet with two call sites (ledger: ADDED), or drop the owner from §3.5's readers and name its own smaller width/position test |
| FIX-5 + FIX-8 (fix) | Stage 3's `info(S) = 8 − ⌈log2\|S\|⌉` ranks/admits a run while a cube reader tests the HULL (SND-6 fix), worth up to 3 bits less: Kelvin `{4b,6b,e2}` info 6 vs hull 4; ſ `{53,73,c5}` 6 vs 3 (hull has 32 members); three ſ-like positions admitted at 18 "bits" and tested at 9. Which cardinality the member bound counts is unstated. The hull is a second cube derivation disagreeing with the set, against D187's "two shapes of one position cannot disagree". | HOLDS | FIX-NOW (text) for info-per-reader; QUESTION (D187 addendum) for the hull | information per READER (set reader info(S), cube reader popcount(hull)); name the hull as a separate lossy derivation and put it to the owner as a D187 addendum rather than leaving it to the kit split |
| SIM-1 (simulate) | §6's rule table (first match) and §3.3's declared strategy are two specs of sibling merge and disagree: `aaa\|aab\|aba\|bba` → table `a(?:a[ab]\|ba)\|bba` (3 paths) vs strategy `aa[ab]\|[ab]ba` (2); the table has no duplicate rule and no "re-run after factoring" rule, so `ab\|ab`, `aab\|bbb\|bab` are reading-dependent. Critic: 432 of 2,016 equal-width lists worse under the table, 104 better. Soundness not at issue. | PARTLY (list 1 reproduced; others reading-dependent, which confirms under-determination) | FIX-NOW (text) | name one procedure: how table rows and the strategy compose, fixpoint re-run, and duplicates |
| RDY-6 (readiness) | Stage 2p: (a) a new `PF_FACT` row is read by `tests/codegen/run_facts_checks.sh` checks 3 and 4 (tuning.md "Facts emptied" lines for `-fno-req-run`/`-fno-req-run-fold`) and needs a `facts_listing.md` §4.1.2 paragraph (D80); the group bound is a new limits row; (b) 2p's width-12 москва piece needs the equal-width ALT hull merge (`(?i)с` width-2 forms differ at two positions), which §3.5 assigns to 2a, yet "2a waits and 2p goes alone". | (a) HOLDS; (b) arithmetic HOLDS, separability SUSPECTED | FIX-NOW (text) | list 2p's contract readers and spec hunk; state that 2p builds the equal-width hull merge inside the group list itself |
| FIX-6 (fix) | altcls stage 2's key is already the longest common literal prefix (`altcls_extend_prefix`, altcls.c:200-258); only the GROUPING keys on the first byte. `(?:abx\|aby\|abz)q` today is `ab(?:x\|y\|z)q`, `RX_ALTCLS_FACTORED 1`. Stage 2b's real addition there is remainder re-merge and set-valued keys; no stamp counts suffix factoring (FACTORED is defined as prefix). | HOLDS | FIX-NOW (text) | correct §2.1/§2.2(5)/§2.3/stage 2b wording; a remainder-re-merge witness; a suffix-factoring stamp or REACH instrument in 2b's abi/spec steps |
| SND-5 (soundness) | The owner's reach is unstated for lookaround bodies. altcls treats A_LOOK as a leaf (altcls.c:443-455), but if the owner entered a lookbehind, prefix factoring turns accepted patterns into refused ones: `(?<=ab\|a)x`, `(?<=xab\|xc)y`, `(?<=aab\|a(b))x` accepted today; factored forms refused ("variable-length lookbehind"); libpcre2 accepts both. | HOLDS (shape); build consequence SUSPECTED | FIX-NOW (text) | state that the owner does not enter lookaround bodies until [VLOOKBEHIND] lands, or that factoring inside a lookbehind needs equal-width rests; list [VLOOKBEHIND] (rev 1 in flight) in the overlap column |
| RDY-8 (readiness) | Existing mech rows anchored on the text each stage edits are not listed (§5 demands REACH only for new rows): stage 1 S366, S302, S303, S-U7, S-U8; 2a S268, S1653; 2b S66, S67; 3 S451. S1638-S1641 anchor OTHER kinds' rows and move only if the column set changes (FIX-9's option b would move them). | PARTLY (rows and anchors exist; S1638-S1641 corrected) | FIX-NOW (text) | each stage brief lists the rows it re-anchors or retires, with REACH re-run |
| SIM-4 (simulate) | Nothing gates the declared strategy on wide classes (fold classes are confluent under every order): `\p{Lu}` 664 boxes → 67 last-first vs 105 first-first (best of 24 orders); `\p{L}` 827 → 330; Nd 71 → 39; dot 10 → 8. The note's "76 vs 66" does not reproduce (verifier: no order gives 76 or 66). | PARTLY (67/105/39 reproduce, 76/66 not) | FIX-NOW (text) | pin the strategy's box counts on the widest classes as a stage-1 gate; correct "76 vs 66" |
| SIM-2 (simulate) | Gate U1's predicate (">1 box or a merge fires") over-predicts: in a 364-class sample, 223 predicted, 142 observed; 80 predicted do not move (`x(?i)σ` tables equal the unsealed spelling); "merge fires" is subsumed by ">1 box"; "mover" is undefined. Two-sided as written, U1 is red on a correct build. | not re-verified (sample claim) | FIX-NOW (text) | define "mover" per observable (run, table, program bytes) and predict each separately; a predicted non-mover with a reason is not a failure |

Doc level

| id | finding | verified | proposed |
|---|---|---|---|
| SND-3 | S-e cannot fail at bound 2, the bound stage 3 lands with; a bound-2 witness exists: `(?i)xyzłw` (Ł/ł `c5 81`/`c5 82`, one box `c5 [81-82]`, non-cube), today `58595ac5/dfdfdfff`, correct 43 bits, sabotaged 44, answer (0,6). | HOLDS | FIX-NOW (one row) |
| SND-4 | "suffix factoring holds for any A, B, C" needs C identical as a node, capture indices included: `(?:a(x)\|b(x))` → `(?:a\|b)(x)` moves group 2 to group 1. pcrec refuses branch reset, so a shared C is capture-free. | HOLDS | DOC |
| SIM-3 | "20 of 76" bench/utf8 movers wrong both ways: lists cls-neg-allhigh (ASCII-only), prp-ingreek (not implemented), prp-l-anchored (refused); omits cls-d-ucp (71 → 39 boxes), cls-s-ucp, ci-class-range; asr-* need `--features all`. | HOLDS (three mis-listed; omitted cells non-ASCII multi-box) | DOC (the U1 script recomputes the list) |
| FIX-10 | Gate U2 names `foldsweep.py`, which computes no "keeps the run" verdict; the keep rule lives in rpsurvey prose, and 513's decomposition differs between the two sources. | HOLDS | DOC: the stage-1 brief commits one keep-count script, pinned against shapes2.py |
| RDY-4 | §4.7 cites "D168 add. 3" for "the ruled reading keys the abi on emitted text"; add. 3 is the `\A`/`\z` fold (its P2e note is an instance, not the source). | PARTLY | DOC: cite D76/D94 and match_api.md §6¶17-19 |
| RDY-9 | Every unit waits on span_pick 1e (the note's own rule), which rewrites emit_dfa.c where most §4.2 audit rows live. | text | DOC: re-grep §4.2/§2.3 at 1e's landing commit |
| SIM-6 | §7 q3 omits property-derived classes (`\p`, UCP `\d\s\w`) as UCD-bump movers. | text | DOC |

NOTED / PLAN

| id | finding | proposed |
|---|---|---|
| FIX-9 (SUSPECTED) | `UNIT` would be a one-member TEXT value (kindrow.def's per-KIND rule keeps its node-dependent siblings `(?:)*`, `(?:){3}` out forever). Alternative: `rr_unit` read from the description's EMPTY arm, kind row untouched. | DOC (decide with FIX-1's option) |
| SIM-5 | 2b's adjacency scan is O(n) per merge (205k tests for 1,296 words); an equal-width short-circuit fixes it. | PLAN (build lane states the bound) |
| FIX ruling-check: O4 vs D77 | stage 2p builds a fact, limits row, facts row, model and gate ahead of any consumer; O4 ("now") governs, but §13 q1 should say in plain words that O4 overrides D77 for 2p. The kit-side crossing is an `MF_SITE_ABI` event on the kit's side, unstated. | DOC |
| FIX family / general form | Third member of a "canonical set, derived spelling" family ([CLS-TREE] S3 WCLASS set, D187 set/cube, this note). G-1: one anchored position-set description with kset/startset/endwin/D172 spans as readers (trigger: a census showing head positions equal or refine kset's); G-2: the island reads the WCLASS SET, not the byte tree, which removes SND-2's box-shape dependence (trigger: U4 census or A-ISL un-hold); G-3: information per reader (FIX-5); G-4: the piece set stays inert only while out of `fields.def`. | PLAN: G-2 deserves a look as the fix for SND-2; others filed with triggers |

## Per-unit readiness (readiness lens, adjusted for the other lenses)

| unit | verdict |
|---|---|
| stage 1 | ready with listed text fixes: SND-2, RDY-3, FIX-4, SIM-2, SIM-4, SIM-3, FIX-10, RDY-4, RDY-8, FIX-3 (bit budget) |
| stage 2a | census lane only (by design, §13 q3); text fixes FIX-1, FIX-9, RDY-8 before a build |
| stage 2p | ready with listed text fixes: RDY-6 (a, b), O4/D77 sentence |
| stage 2b | NOT ready as written: SND-1 (answer), SIM-1 (one procedure), FIX-7 (phase), FIX-6, SND-5, FIX-3/RDY-5 (existing flags), SND-4 |
| stage 3 | not ready by design (rides [POS-ONE-DETECTOR], O3); FIX-5/FIX-8 and SND-3 for its eventual brief |

**Overall: ready with listed text fixes for stage 1 (and 2p); 2b needs a rev 2
of §3.2/§6/§3.5 before its go (one answer-level hole, SND-1).** No finding
needs a redesign of stage 1's core: the exact byte merge held again (S-a, S-b,
S-i, K123 can fail; the piece set's soundness as a fact held).

## PROBED-AND-HELD (summary; full lists in each critic file)

- Prefix factoring on a fixed-width capture-free key, rests arbitrary: 26
  pairs SAME (libpcre2 and pcrec): empty key branch in its slot, nested rests,
  captures in rests, recursion into a rewritten group, atomic/possessive/lazy,
  `\K` in key and rests, two same-span key ways, backref keys, inline `(?i)`,
  utf8 caseless keys. Suffix factoring with C capture-free: 4 SAME.
- C2 completeness for strings; the empty branch blocks every merge across it.
- §3.4/§3.5 piece set as a FACT: a language identity, no match outside every
  piece (C1).
- Island set-edge reading: answers unchanged (disjoint equal-width members),
  only the count moves (SND-2).
- Every ledger cite holds at 569c57d3a; the ZERO-reader list is complete; the
  abi precedents and match_api.md §6¶18-19 read as §4.7 says; flags, stamps,
  make targets, emit_sweep options exist; seal's VM `L2 label empty` /
  `RX_VM_PROGRAM_BYTES 1502ULL` reproduce; the kit seam already carries
  256-bit sets.
- Numbers: G4 1454 (1417/37), 513/766/898/1403/1416/1417, 253/398 splits,
  0 mismatches vs the compiler on 357 sampled classes; москва widths 12-15 and
  the 12-position run; `xyzkabc` 7/9; о head/tail; all 11 §8 entry figures;
  U3 0 growth in 364 classes; table outputs `ab[xyz]`, `[xy]ing`, `a(?:b||d)`,
  `fr(?:ank|ed)`, β `ce[92 b2]|cf 90`; table soundness ~44k cases vs `re`, 0
  mismatches; strategy input-order independent, ≤ 2 sweeps on 65,535 grids.
- Witnesses: S-a, S-b, S-i, S-d, S-k, S-f CAN FAIL; S-c, S-g PLAUSIBLE (reach
  confirmed; sabotage not built; S-c's REACH line should name
  `RX_DFA_PREFILTER_OFFSETS`, the req pre-check being "dominated"); S-p inert
  as stated; S-e bound-3 only (SND-3).
- Compile totals: fix ~30, soundness ~75, readiness ~15 (+3 gcc), simulate
  (critic's count not relayed), verifier ~60.

## By-id completeness

SND-1..5, FIX-1..10, RDY-1..9, SIM-1..6: every id has a proposed disposition
above (FIX-2 under SND-2, RDY-1 under FIX-1, RDY-2 under FIX-4, RDY-5/RDY-7
under FIX-3, FIX-8 under FIX-5, RDY-9 DOC). FIX-NOW: SND-1, SND-2, RDY-3,
FIX-4, FIX-1, FIX-3 (+question), FIX-7, FIX-5 (+D187 question), SIM-1, RDY-6,
FIX-6, SND-5, RDY-8, SIM-4, SIM-2, SND-3. DOC: SND-4, SIM-3, FIX-10, RDY-4,
RDY-9, SIM-6, FIX-9, O4/D77 sentence. PLAN: SIM-5, general-form G-1..G-4.
REJECTED: none.

Questions for Frank (plain words): (a) four new public "turn this off" flags
would use up the spare flag bits and trigger the interface push; should the
alternation stages reuse altcls's two existing flags and keep the others
test-only until a slowdown is measured? (b) stage 3's "covering cube" for a
set it cannot spell exactly is a second shape of one position, which D187 was
written to prevent; allow it as a named, lossy derivation (an addendum), or
have cube-only readers decline such positions?

## Lessons for the guide (proposed)

1. Soundness lens: an adjacency or commutation test stated over STRINGS must
   also be drilled with SIDE EFFECTS in the intervening branch (`\K`, a
   capture read later by a back-reference): "same span, nothing observable
   differs" fails on them (SND-1).
2. Fix-induced lens: when a fix re-reads an existing node kind in a new way
   ("read X inside Y as members"), test it on today's instances of X that the
   fix's author did not create (SND-2/FIX-2: `u8_box`'s own range boxes).
3. Readiness lens: when a design names a sweep script and option as a gate's
   population, run its argument parser path (which modes read the option)
   before calling the gate runnable (FIX-4/RDY-2, found by two lenses).
