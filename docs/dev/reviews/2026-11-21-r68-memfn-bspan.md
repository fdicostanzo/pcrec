# Review r68 — memfn-bspan (design): the kit's block-span design note, block_span.md rev 2 (R-47, D201)

- **Subject:** `docs/design/memfn/block_span.md` rev 2 at `aaa1b3227fe28c9480f1e3c914f5b9d8ee648bc1` (lane/bspan2; branch
  HEAD `814a44106` adds only the lane report's OWED line). Design only; nothing is built.
- **Build tree:** the kit branch `lane/memfn-k1108` = `03ce1ee3bd6d1e732d01c11e7d37bd269fef392b`, built once (nice -j2, unlocked)
  in `worktrees/crit-memfn-bspan`, plus an MF_TRACE harness for the round kit. Its `memfn/src`, `src`, `docs/spec`, `tests`
  are byte-identical to main HEAD `5c1ccef7e` and to the subject's base `10cdf0654` (empty `git diff --stat`), so no cited
  code moved between the note's numbers (taken at `051e78af2`) and the build tree. Only line-number nits (PREMISE probed:
  `wf_test_to` is defined at window.c:3536, not :3542; `pick` at :1401, not :1400).
- **Freeze:** 2026-11-21 00:43. Rulings frozen at main `5c1ccef7e` (decisions.md/plan.md last touched `cbbb41ecd`, D201 add. 2).
- **FREEZE DRIFT:** main moved to `047c5195f` during the round (r66 PL14 cites, K153 filed, [K153-QUANT-REGISTRY] plan row).
  No D-row, plan row or spec this subject cites changed. None.
- **FREEZE NOTE:** the subject relies on "rulings R-1..R-4" (R-4 = smallest form) and two "manager 2026-11-21" calls
  (`scan-scope`, `wrap-deny`). Their only records are in files denied to this round (bspan*_rulings.md, the kit journal);
  the critics treated the subject's statement of them as the claim. D201 add. 2 is the record for `scalar-wrap`.
- **Budget:** about 600 pcrec compiles (SOUND ~145, PREMISE ~40, SIM ~335, MEAS ~75, SIZE ~25, coordinator ~15) and about
  600 gcc/clang compiles; SOUND overran its 300 own-C cap by ~38 (process.md). No make, no suite, no timing.
- **Verification:** inline by the coordinator (review/verify.md, 17 items, all HOLD; no contradictions).

## Lenses as run

| lens | model | question | why chosen |
|---|---|---|---|
| SOUND (soundness; owns hand-execution of the pseudo-code) | opus | does §4.1's text, §4.2's bound argument and §5's `__body`/selector seam answer exactly as today, hand-executed with every kept guard, at default flags, -march=native and clang | the design ships emitted-text pseudo-code and an identity proof |
| PREMISE (premise + slot tracing; sibling question; every caller of the emitting functions) | opus | is every "today the tree does X" true at the build tree; is the span-form choice one table per slot; is `vs<j>` a third family member | a new table and mechanism resting on many tree facts |
| SIM (simulate; owns k and the bounds) | sonnet | run the table as written over the population and the bound cells: does it pick what §0.1/§3.2/§11/§17 claim | a selection rule with a population claim |
| MEAS (measurement + check adequacy; owns the plants) | opus | can each measurement/check/plant fail when its property is false; does each comparison move one axis | U2b, F2, C6, G1, G2-V, pins, identity gate, 4 new sabotage rows |
| SIZE (SHIP-SIZE, the launcher's lens; + goals, rulings with the owner-quote check, cost/overlap, general form + unlocks) | opus | the smallest form that serves the confirmed table, against the real population; does the design agree with its rulings | requested by the pcrec manager; a build proposal resting on owner rulings |

## Which lens caught what
- Found by three lenses: the C18 selector/helper mismatch (SOUND-2, PREMISE-1, MEAS-11) and the population error (SIM-1,
  MEAS-1, SIZE-1). Found by two: D1w is a second WALK row (SOUND-4, PREMISE-6); five existing sabotage rows anchored in
  retired code (PREMISE-2, MEAS-7); the wrapper evidence (PREMISE-9, MEAS-6, SOUND-5); C6 widths (SIM-3, MEAS-8).
- SOUND alone: the `set_epi8` order (SOUND-1), clang's unused `__body` (SOUND-3).
- PREMISE alone: where the table can be evaluated (PREMISE-3, -7), the includes bit (PREMISE-4), the abi reader (PREMISE-5),
  the selector family (PREMISE-8), the formhash shape (PREMISE-10).
- MEAS alone: plant (b) cannot fire on HORS (MEAS-2), the lower bound is a safety floor (MEAS-3), C6's axes and control
  (MEAS-4, MEAS-10), U2b's power (MEAS-5), pins (MEAS-8), the identity gate's mask (MEAS-9), F2's reference (MEAS-12).
- SIZE alone: U2b on today's population (SIZE-2, -3), double timing (SIZE-4), the owner quote and the reading (SIZE-5, -6),
  D155 add. 3 (SIZE-7), goals ranking (SIZE-8), D201's provenance pointer (SIZE-9).

## Headline
No answer-level defect in the DESIGN: SOUND hand-executed §4.1 (16 sets x 14 K, guard pages both ends) and the §5 wrapper
on 20 real sites at three compilers with 0 differences, and MEAS matched the V side's machine code to 710's arm sources on
9 of 9. The note is NOT ready for the build as written: (1) the C18 gate it calls "unchanged" cannot parse its selector, and
an `always_inline` helper cannot pass C18's -O0 `nm` leg; (2) the population is 3 bench sites, all k = 31, not 4, and the
corpus holds ZERO V sites at any width, so every corpus-populated check (identity gate, G-1's deny arm, C18's floor, G1)
has an empty population; (3) the scalar no-loss check (U2b) censuses a population that holds none of the shapes known to
differ, and its timing cannot see an effect below ~15 %; (4) the note does not say where the table is evaluated, and `k`
needs `skip`, which only a head renderer computes today. All four are text/design fixes before the build go. SIZE's
ship-size reading: the surface is mostly ruling-bound; T-keep, U2b's timing and G1's timing window serve no site today.

## Findings (PROPOSED dispositions)

### F-1 — design — C18 / simdfloor is not "unchanged": its regexes miss the subject's selector and helpers, and its -O0 `nm` leg cannot see an `always_inline` helper — **FIX-NOW (design text: name the C18 change as a unit)**
SOUND-2, PREMISE-1, MEAS-11. VERIFIED (V1). `tests/memfn/simd_floor_check.py` SELECTOR/HELPER match only
`static inline size_t ...`; §4.1/§5 spell `static inline __attribute__((always_inline)) int`. On a hand-built ON text:
0 selectors, 0 helpers, and leg (c) reports "a deleted line that is no SIMD FUNC's floor call" on every V mover. C9-x86
requires `<fn>__w<VW>` as a defined symbol in the -O0 object; an `always_inline` static is never emitted. The `__w32_b`
block helper is invisible to the exclusivity lint. C18's population (corpus + NAMED) has no span witness (F-3), so even a
fixed C18 meets no `vs<j>`. `always_inline` is load-bearing for G-2 (MEAS PROBED: F2 identical 9/9 with it).
Fix: §10/§14 U4/§17 name a C18 amendment with its own controls (learnings §3): the second selector/helper spelling (or
one spelling shared with ofsskip, see F-11), the -O0 rule for `always_inline` helpers (e.g. read the inlined ymm use, or
`-fno-inline` for the C9 compile), and a NAMED span witness (`[0-9a-f]{17}`, `[0-9]{25}`) with a literal floor written
before the build. Effort small-medium.

### F-2 — doc — the population is 3 bench sites (all k = 31), not 4; the corpus holds 0 V sites — **FIX-NOW (doc)**
SIM-1, MEAS-1, SIZE-1. VERIFIED (V2). The corpus row `tests/counterk/counterk.rxt:1919` `(?:ab|ba|aa|bb){24}c` is
fd D1 = FF_LIBC (k = 48 at width 4095; no window site at width 32), which `scan-scope` excludes. The census script's
"scan" is any non-HORS site. Real population at each pattern's own options: bench `[0-9a-f]{32}` (HORS k 31),
`\b[0-9a-f]{32}\b` (HORS k 31), `\d{32}` (WALK/R7w k 31), identical at widths 32 and 4095. No real site reaches the B = 32
rung or either upper bound. §17's "the 4 are all the default build can show" is wrong twice. Fix §0.1, §8's "four routed
census patterns", §17; the census script's `route()` should read the fd row. D201 add. 2's population line
("corpus 1 of 6,403") is main's record: the manager may want a one-line correction there too (PLAN/DOC for main).

### F-3 — design — every corpus-populated check has an empty population; the identity gate's "byte for byte" cannot hold across U2's own abi bump — **FIX-NOW**
MEAS-1 (consequences), MEAS-9, MEAS-11 (population). Follows from F-2: the identity gate (G-4), G-1's deny-arm sweep,
C18's floor and G1's population all compare 0 V sites from the corpus, so plant (d) survives the identity gate by
construction (S3281's own header already records this lesson: its detector is G2's window family at a width past 64). And
U2 lands the abi event, so the deny artifact differs from main's on every artifact's abi lines: the mask is undeclared.
Fix: every population-read check names a SEEDED witness list (the flip-pin patterns, the 3 bench texts, a slice of 710's
grid) at width 32 and 4095, with a printed count and a floor > 0 (K35); the identity gate declares its mask before data
(exactly the abi-number lines, a literal list) and pins its reference to the lane's merge base, built once. Effort small.

### F-4 — design — T-vscan keyed on "pick WALK" admits D1w, an unmeasured one-member walk — **FIX-NOW (key on the R7w row, or say D1w is admitted on purpose)**
SOUND-4, PREMISE-6. VERIFIED (V3). `FF_WALK` is the pick of two fd rows, R7w (710's four scan classes) and D1w
(FB_UNMEASURED_DEFAULT). `x[0-9]{26}` is D1 (LIBC, excluded) by default but D1w with `--memfn=no-fd-d1`, k = 26: an unrelated
finder deny moves it into an unmeasured V cell, against `scan-scope`'s own reason (D77). Answers held (SOUND: 176
subjects, 3 compilers). Cheapest fix: the predicate reads the fd row (`w->brow`), R7w only. Effort trivial.

### F-5 — doc (answer if built literally) — §4.1 writes the nibble tables in index order inside `_mm256_set_epi8` — **FIX-NOW (text)**
SOUND-1. VERIFIED (V4). `set_epi8` takes the highest lane first; the `bit` table is written that way, `lo_t`/`hi_t` are
defined by index. Read literally, 14 of 16 test sets answer wrong; the reversed reading (spike708's) gives 0 differences.
Also state that table values > 127 are written signed. G2-V unit would catch a literal build. Effort trivial.

### F-6 — build (clang) — the unreferenced `__body` at a w32 target is a clang `-Werror` failure — **FIX-NOW (text)**
SOUND-3. VERIFIED (V5). At w32 the selector calls `__w32`, which never falls back, so `__body` is an unused static function:
clang `-Wall -Wextra -Werror` (the house GENCFLAGS under CLANGGEN=1) errors; gcc is silent. vany's `__body` is always
referenced, so V would be the first unreferenced floor. Fix: `__attribute__((unused))` on `__body`'s header at EVERY layer
(OFF and ON lines must stay identical for C18 (c)), stated in §5. Effort trivial.

### F-7 — design — sabotage (b) ("final block reads 1 B past", caught by the guard page) cannot fire on any HORS site — **FIX-NOW (row (b)'s witness)**
MEAS-2. VERIFIED (V6). On HORS the byte past the stretch is the probe: in bounds and a member. Hand plant: `[0-9a-f]{32}`
(the bench's own hex32, B = 16) -> no fault, 0 of 1100 answers differ. WALK control `[0-9]{25}` (stretch = pattern tail):
SEGV. Fix: row (b)'s witness is a WALK whose stretch ends at the pattern end, subject flush at the end; say that on HORS
the shape is in-bounds and benign. Effort small.

### F-8 — answer (latent) — T-vwin's lower bound 16 is a safety precondition of the block rule, labelled MEASURED only — **FIX-NOW (label + renderer assert)**
MEAS-3. VERIFIED (V7). For K < 16 §4.2's "largest of 32, 16 that is <= K" has no B; built as B = 16 the final block reads
below the stretch (hand plant at k 15: SEGV at a start guard page, 398/700 answers differ). §13 Q3 lets a re-measure
(Zen 1) "move the lower bounds". Fix: §12 labels 16 "MEASURED and DERIVED (the smallest rung)"; the renderer asserts
K >= 16 (an abort, not a decline). Plant (c) is caught three ways (pins, start guard page, staircase). Effort trivial.

### F-9 — maintenance — U1 deletes the anchors of five existing sabotage rows; the note names none — **FIX-NOW (U1 lists the re-aims, REACH at U1)**
PREMISE-2, MEAS-7. VERIFIED (kit/anchors_window.txt). S3278, S3279, S3281, S3282 anchor in `wf_span_head` (retired, G-5);
S3280 on `if (w->off[i] < w->head) return 0;` in `wf_loop_len` (`w->head` retires); S3277 stays textually but its function's
meaning changes (k computed with head 0, so `wf_loop_len` gains a head parameter). §9.2 names only S693. Also no plant
covers §3's own ordering claim (V after T-deny/T-force/T-lever). Fix: U1 re-anchors the five onto the table's rows with
REACH re-proved at U1 (not only U6), and adds one ordering plant. Effort small.

### F-10 — design — where the table is evaluated: the define must know each V stretch before `wf_test_to` runs; `k` needs `skip`, which only the head renderers compute; the includes bit cannot be a class fact — **FIX-NOW (design text)**
PREMISE-3 (as corrected by its author), PREMISE-7, PREMISE-4. VERIFIED (V9, V10). §5 has the DEFINE write `__body`,
the selector and the bracket, so it needs each V stretch's LO, K and j before the use renders; runcmp's `rc_row_of`
(one table, asked by both the define's helper declaration and the compare, phase MF_PH_RUN) is a working precedent for a
double ask. But §3.1's `k` = `wf_loop_len(w, i, skip)` and `skip` is an OUTPUT of `d_hors_head`/`find_head`
(renderers). And §5/§9.3's "the plan's `includes` gains `MF_INC_LEVEL_W32`" would make the window plan the first class
carrying a level bit (pcrec's trace build compares asked vs defined `includes`); ofsskip sets the level bit on the ART at
define. Fix: say the table is one selection asked at define and use (the runcmp idiom, its trace phase), lift `skip`
into the plan (one fact, two readers: the general form), follow ofsskip for the include bit, and drop §9.3's
"`MF_CLASS_V` unchanged since the class already carries a level bit" premise (false today). Effort small.

### F-11 — design (sibling) — `vs<j>`'s selector and level block are the third member of a family written twice already — **FIX-NOW (decide in the note: one writer, or why not)**
PREMISE-8 (SUSPECTED, argued; the two members are by file:line). `vany_selector`/`vany_level` (vany.c) and
`fn_selector`/`fn_level_block` (ofsskip.c) write the same two shapes; §4.1/§5 would be a third. The house rule (notice
siblings, propose unification at three) and G-5 apply; one writer is also the one place F-1's signature question is
decided, and it is the smaller ship. Note: the ROUTED precedent is ofsskip (vany is not routed; PREMISE probed), so §1/§2
"exactly vany's shape" should cite ofsskip. Also cite runcmp's table as the model (PREMISE-8 (b)). Effort small.

### F-12 — doc (the abi ritual) — §9.2's reader grep filters out a reader — **FIX-NOW (doc)**
PREMISE-5. VERIFIED (V11). `git grep -w <N> ... | grep -i abi` drops `match_api.md` [6¶17] ("It is `109` on every artifact
pcrec emits today"). The D94 failure mode. Fix: cite [6¶17]; review the unfiltered `-w N` hits by hand. Effort trivial.

### F-13 — doc/design — the wrapper's machine-code evidence: 710's Hspk is a one-level wrapper, the shipped shape is two-level; §16 item 6b's counts do not reproduce — **FIX-NOW (doc; U2b censuses the BUILT text only)**
PREMISE-9, MEAS-6, SOUND-5. VERIFIED (V8, V12). 710 recorded the wrapper changing the walk on 47 of 130 patterns, which §2
does not cite. But on num k=64 (`[+.0-9]{65}`) Hspk differs from H64@on by 47 lines while the two-level shape (selector ->
`__body`) differs by 0. So §2's "Hspk is exactly this wrapper" and its "0 standing LOSS, 3 standing WIN" read a different
machine code, and §16 6b's "`[+.0-9]{65}` differs by 440 lines" is not reproduced by two independent lenses (0 lines);
the `\w{17..32}` sites do differ (20-26 lines), consistently. Fix: §2 drops the Hspk transfer (or calls it a one-level
wrapper), and U2b (a) runs on the BUILT U2 text only, with its command stated. Effort trivial.

### F-14 — design (the round's main open question) — what the scalar no-loss check (U2b) checks, and whether T-keep can exist — **MANAGER RULING (leaning below)**
MEAS-5, SIZE-2, SIZE-3, SIZE-6, SIZE-8. Facts (agreed by both lenses): on the real population (3 sites) the two-level
wrapper's SIMD-off `rxa_search` differs in no instruction (one site padding only); the shapes known to differ (`\w{17}`,
`\w{20}`, `\w{32}`) are in no corpus or bench pattern, so a census over corpus + bench answers "does the population hold a
differing site" (no), not "does the wrapper move machine code" (it does, on `\w`); U2b (b)'s cell rule reads a uniform
14 % slowdown as 100/100 TIE (MEAS drill), so it cannot return LOSS on a small wrapper effect; T-keep's "declared keep list"
needs a stretch identity no §3 fact carries (a per-pattern exception list); a padding-only diff has no rule.
And the owner's words were CONDITIONAL on identity ("If that's true I don't have a problem with that", D201 add. 2); the
reading substitutes "no measured loss" (SIZE-6).
Two remedies were proposed: SIZE's (record a machine-code census on the built text, padding normalized; drop T-keep and
the scalar timing; triggers bring them back) and MEAS's (widen the census to a class x k grid with `\w{20}` as a floor
witness that must be found; state the timing's minimum detectable effect, or an aggregate test).
Coordinator's leaning: take SIZE's form for the build and MEAS's census population: U2b (a) = a machine-code census on the
BUILT text over the population PLUS a class x k probe grid (710's classes x k 16..31 at width 32), padding normalized, with
`\w{20}` as the known-positive floor witness; drop T-keep and the scalar timing from the design (T-keep has no fact to key
on). The `\w` shapes then differ at the instruction level with no planned measurement, which is outside the owner's words
as he said them: that becomes ONE plain owner question (suggested slug `wrap-differs`: "the wrapper changes gcc's machine
code on `\w`-like sets at SIMD-off; is no-measured-loss enough, or keep `\w`-like sets unwrapped?"), not a reading. Until he
answers, the build may land with the default-build mover set limited to what is machine-identical, or wait; that is the
manager's call. Effort small (text), plus the owner question.

### F-15 — design — card C6: no width stated (half its cells do not exist at width 32), two axes per arm, no control arm, no S set, and the outside-bound cells are A/A by construction — **FIX-NOW (text), no new lever**
SIM-3, MEAS-4, MEAS-10, MEAS-8 (width part). At width 32 the k 32/1000/1001 window cells and 64/65 scan cells do not
exist (n >= 33 is E-stmt), and `[0-9a-f]{41}` (the formhash instance) has no E-find site: C6 would time H64 against H64.
At SIMD-on `--memfn=no-span-vector` changes the wrapper AND the body AND the TU (immintrin, stamps); 710's rule needs its
control (Hspk) and its A/A line, which no shipped lever renders; S needs a profile arm C6 does not declare; at k 15/1001
and 23/65 both arms are today's bytes.
Coordinator's leaning (ship-size): state width 4095 for every cell above k 31; state that C6 measures the SHIPPED trade
(both axes: G-3 is about what the caller gets) and write, before data, which clauses of 710's rule apply and what replaces
the control/A-A (e.g. the identical-machine-code cells as the A/A population, F-13); define S or drop "S-pick" from G-3;
drop the four outside-bound cells from the "both sides" claim (say they are A/A). MEAS-10's `--harness=span-vector=force`
lever and MEAS-4's `span-vector-body` lever are PLAN rows with a trigger (a bound is questioned by a C6/Zen 1 run), not
build scope. Effort small.

### F-16 — maintenance/size — the formhash "entry" needs a new SHAPE and renderer — **FIX-NOW (doc: count it in §8/§17)**
PREMISE-10. VERIFIED (V13). formhash entries are kit facts over six shapes (FIND .. OFS); none builds a window site with a
long one-class stretch, and a pcrec pattern spelling has no meaning there. §17's "1 formhash entry" is a shape + renderer +
entry. First span card staled by a text hash (C1/C3 carry `-`). Effort small.

### F-17 — doc — F2 names an `.H64` reference that does not exist and has no failing outcome before landing — **FIX-NOW (doc)**
MEAS-12. VERIFIED (V15). work/src has avx2-loop, avx2-ool, Hspk, Hspk-ool, prof (130 each); no H64. F2's real population is
the routed cells; say so and count them, and state the landing rule for a DIFFERS on a routed cell. Effort trivial.

### F-18 — design — the T-table pins guard only the k column — **FIX-NOW (3-4 literal cells)**
MEAS-8. The pick column (`ab[0-9]{26}`: D1, k 26, refused only by "pick WALK"), the frame column, and the once-per-site rule
(`[0-9a-f]{20}[g-z]{20}` at width 4095: two eligible stretches, exactly one `__w32` call) have no detector; V is
answer-identical there, so only a text pin can see a plant. State each pin's width. Effort small.

### F-19 — doc — §11's examples and encoding — **DOC**
SIM-2, SIM-4 (VERIFIED V14), PREMISE-6 (second part). `a[0-9a-f]{20}` is E-stmt with no stretch, not a LIBC/PAIR find (use
`x[0-9]{26}` or `[0-9]{30}x`); under `-e utf8` hex sets are WALK (R7w), so the hex family moves only at `{25}`..`{32}`.
§11 and G-4's "equals §11's mover classes" state the byte encoding only. Population unaffected.

### F-20 — doc (owner-facing) — the owner's words are not quoted verbatim, and the reading is labelled his ruling — **FIX-NOW (doc)**
SIZE-5. VERIFIED (V16). §2 ("verbatim") and §15.1 quote "Scalar wrap: the function goes inline ..."; D201 add. 2's record
has no "Scalar wrap:". The header, the revision history, §2 ("option A, RULED") and §15.1 attribute A-with-check to Frank;
the record calls it "READING (the kit's and main's, not his words; he may narrow it)". Fix: quote the record exactly;
label A + check as the kit's and main's reading of his conditional answer everywhere. Ties to F-14.

### F-21 — design — goals: the owner's scalar-layer ruling is ranked fourth among quality goals — **FIX-NOW (text)**
SIZE-8, SIZE-6 (§7 part). D201/R-47's "the scalar layer stays H64" sits inside G-4, below G-2/G-3, under "a conflict goes to
the higher one". A ruling is a constraint above the ranking; and U2b, added for exactly that constraint, is no goal's
checkable form. Also §7 "Off by default" is true of the vector helper only: the wrapper and its deny are live in the default
build. Fix: a CONSTRAINT line above §0's table ("SIMD-off: the H64 form; machine code identical on the population, padding
normalized", per F-14's ruling), and §7's sentence corrected. Effort trivial.

### F-22 — doc — G1 alpha's timing is vacuous on 3 movers (floor 8), and the wrapper/vector forms are timed more than once — **FIX-NOW (text)**
SIZE-4. integration.md §17.2 bins with a floor of 8 movers; the population is 3, so every bin is UNREACHED at both layers.
The SIMD-off G1 pair is U2b (b)'s pair; the SIMD-on G1 pair is C6's. Fix: G1 delivers its manifest + dry run (count 3,
UNREACHED printed) with NO timing window booked; trigger = a bin reaches 8 (the default width rises, or a pattern lands in
range). D147's "both layers" reading is satisfied by the machine-code census (F-14) where the code is identical.

### F-23 — doc — §2 cites D155 add. 1 Q-R9-10 as binding; add. 3 made it a guideline — **DOC**
SIZE-7. The conclusion (A) holds on the contract (C18 (c), limits.md §8.3¶1, D155 add. 2's neutrality); the sentence "the
standing SIMD organization ... not a new cost" should cite add. 3 and rest on the contract.

### F-24 — doc (main's record) — D201's provenance pointer for "build with simd layer" names a commit without the words — **DOC (manager's: decisions.md)**
SIZE-9. VERIFIED (V17). Kit commit 29e893818's responses.md NOTICE holds a proposed D-entry text, not the quote; the words
may be in the denied kit journal. Every copy of the quote itself matches. Fix the pointer in decisions.md.

### NOTED
- Line-number nits in §1 (`wf_test_to` :3536; `pick` :1401). NOTED.
- MEAS PROBED: `-fmemfn-simd=x86-64` (w16) machine code equals `-fno-memfn-simd` for wrapped and unwrapped `\w{20}`/`\w{32}`
  on gcc 15.2: the SIMD-off reading covers w16 on this compiler (not shown for clang). Worth one sentence in §2.1.

## PROBED-AND-HELD (union; counts in the critic files)
- §4.1 hand-executed from the text: 16 classes (empty set, 255-member, >= 0x80 bytes, odd and 8-range sets) x 14 K (16..1000)
  x LO {0, 1, -24}, ~10k windows per class, guard pages at both ends: 0 differences (with set_epi8-order tables); B's choice,
  `i + B < K` + overlapped tail, the 16-B rung inside the v3 region, negative LO all held; K = k (never k + 1). (SOUND)
- §5 wrapper on 20 real sites (HORS/WALK, widths 32/4095, beside literals, `\b`, C-run memcmp) at gcc -O2, -march=native,
  clang: the chain references only `rxa_mf1_s`, `rxa_mf1_c` and its own `_j`; 0 answer differences over 140..3092 subjects
  per site; gcc -Werror clean. (SOUND)
- F2, V side: §4.1/§5 rendered on build-tree artifacts vs 710's avx2-loop sources, 9 of 9 machine-identical (B 16 and 32,
  HORS and WALK, k 16..1000). (MEAS)
- §1 site map, §16 items 1-5, §3 facts (`w->skel`, `w->pick`, `kit_opt_state`, `KIT_LEVER_SPAN_HEAD`, the deny-column idiom,
  `offer_at`'s set equality), §3.3's floor/legacy claim as worded, every caller of `w->chk->test`/`wf_test_to` (three; no
  other), length accounting (`pcrec_sb_len_decide` = uncut minus bracketed), option A as the existing ofsskip SIMD-off shape:
  held. (PREMISE)
- The table run over 210 sweep cells (5 classes x 15 n x 2 widths, + 60 at v3): k = n - 1 everywhere; bounds 16/24/1000/64
  exact; routing layer-independent; §3.2 one eligible stretch per site at width 32; width identity of the walk lines;
  first-match order of T-deny/T-force/T-lever ahead of V. (SIM)
- Plants (a) and (c) caught; plant (b) caught on WALK only (F-7). (MEAS)
- Rulings: D201 decision and add. 1 quotes word for word in every copy; D147, D155 add. 2, D157, D174, D77, D144 add. 4,
  D80/D76/D94 agree with the design. Surfaces kept by ruling: both bound pairs and the B = 32 rung (no real site reaches
  them, but D201's "Read as" names the 710 table), U1, the deny, C6, G2-V, pins, the spec hunks, the abi event, one V per
  site with no SWAR or unroll. (SIZE)

## SHIP-SIZE summary (the launcher's lens)
Ruling-bound and kept: the two V rows with 710's bounds, both rungs, U1, the deny (both layers), C6 + kit-grid row,
G2-V, pins, spec hunks, abi event. Cut or defer (each with its trigger): T-keep and §2.1 (c) (no site, no keying fact:
F-14); U2b (b)'s scalar timing (0 instruction differences on the population: F-14); G1's timing window (UNREACHED by
construction: F-22); C6's outside-bound cells (A/A by construction: F-15); any new force/body lever (PLAN rows: F-15).
Grows (smaller than it looks today, but real): the C18 amendment (F-1), the formhash shape (F-16), five sabotage re-aims
(F-9), seeded witness lists (F-3), 3-4 pin cells (F-18). Net: the build is about the size §17 says, minus T-keep and two
timing windows, plus the C18 and formhash units §17 did not count.

## D27 recommendation
The caller contract is small (one deny row, answer identity) and G2-V's control is already written from the class, not the
kit. A spec-first author is OPTIONAL here; if the manager wants one, its promise is the deny's (`--memfn=no-span-vector`
restores today's bytes at every layer) and answer identity at each bound cell. The launcher decides.

## By-id completeness
SOUND-1 F-5; SOUND-2 F-1; SOUND-3 F-6; SOUND-4 F-4; SOUND-5 F-13.
PREMISE-1 F-1; PREMISE-2 F-9; PREMISE-3 F-10; PREMISE-4 F-10; PREMISE-5 F-12; PREMISE-6 F-4, F-19; PREMISE-7 F-10;
PREMISE-8 F-11; PREMISE-9 F-13; PREMISE-10 F-16.
SIM-1 F-2; SIM-2 F-19; SIM-3 F-15; SIM-4 F-19.
MEAS-1 F-2, F-3; MEAS-2 F-7; MEAS-3 F-8; MEAS-4 F-15; MEAS-5 F-14; MEAS-6 F-13; MEAS-7 F-9; MEAS-8 F-18, F-15; MEAS-9 F-3;
MEAS-10 F-15; MEAS-11 F-1, F-3; MEAS-12 F-17.
SIZE-1 F-2; SIZE-2 F-14; SIZE-3 F-14; SIZE-4 F-22; SIZE-5 F-20; SIZE-6 F-14, F-21; SIZE-7 F-23; SIZE-8 F-21; SIZE-9 F-24.

## Lessons for the guide (proposed; the manager accepts or declines)
1. A census script's site KIND must be the table's own predicate (frame + finder row), never a text proxy: spancensus2's
   "scan = no `_sh[`" counted a LIBC site as routed, and the error travelled into D201 add. 2 and the note's §0.1/§17.
   Proposed critics.md line under the simulate lens: "re-derive each population count with the subject's predicate on the
   trace record (MFTRACE fd row), not the census's text regex".
2. When a design adds a SIMD FUNC in a NEW spelling (return type, attributes), the premise lens greps C18's regexes against
   it; "C18 unchanged" is a claim about a regex, not a docstring (three lenses found it from three sides).
3. A wrapper's machine-code evidence depends on its INLINE DEPTH: a probe or control arm with a different depth from the
   shipped shape is not evidence for it (Hspk one level vs the two-level selector -> `__body`: 47 lines vs 0).

## MANAGER RULING (kit manager, 2026-11-21)
- **FIX-NOW, as proposed:** F-1..F-13, F-15..F-18, F-20..F-22. **DOC:** F-19, F-23. F-24 is main's (decisions.md), relayed.
- **F-2:** accepted. The real population is 3 bench sites (`[0-9a-f]{32}`, `\b[0-9a-f]{32}\b`, `\d{32}`, all k = 31), and the corpus has 0 V sites (counterk:1919 is a LIBC site). The kit's "4 patterns" figure, reported to the owner and to main, was wrong; both are told. D201 add. 2's population line goes to main for correction.
- **F-14: the coordinator's leaning, taken.**
  - U2b (a) becomes a machine-code census on the BUILT text, padding normalized. Its population is the real one PLUS a class x k probe grid (710's classes x k 16..31 at width 32), with `\w{20}` as a known-positive floor witness that must be found.
  - T-keep, §2.1 (c) and U2b (b)'s scalar timing are DROPPED: T-keep has no fact to key on, and the timing cannot detect the effect.
  - The `\w`-like machine-code change at SIMD-off goes to the owner as question `wrap-differs`. The build waits for his answer on that point only; the fix lane writes both outcomes as a stated fork.
- **SHIP-SIZE:** the cuts are accepted (T-keep, the two timing windows, C6's outside-bound cells, no new levers). The growths are accepted and counted in §17: the C18 amendment, the formhash shape, the five sabotage re-aims, the seeded witness lists, the pin cells.
- **D27:** not used. The caller contract is one deny row plus answer identity, and G2-V's control is written from the class.
- **Lessons:** all three accepted. Lesson 1 (census site KIND by the table's own predicate on the trace record, not a text proxy) also becomes a kit rule, journaled.
- **Freeze note:** R-1..R-4 / scan-scope / wrap-deny were recorded only in denied files. Rev 3 restates them in the note.
- The reviews/CLAUDE.md index line is left to main: the file sits at its size limit.
- **Process note (manager):** the coordinator verified the 17 CONFIRMED claims itself and launched no separate verifier, which the skill §1 roles require; it reported this. Accepted for this round, because every finding is a text or design fix that rev 3's own re-check reads. The next round of this subject launches a verifier. Also accepted: the coordinator's top process change. Every run kit for a rule keyed on kit picks ships the MF_TRACE harness plus a per-site fd-row script, never a text-proxy census.
- **Renumbered r67 -> r68** (2026-11-21): main's 2026-11-21-r67-k152 took r67 first. Both launchers share the sequence; main takes r69 and up next.
