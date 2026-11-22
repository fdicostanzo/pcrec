# The vector span: building job 710's block span at the SIMD layer (R-47, D201)

Status: DESIGN, rev 4.2 (lane bsu2fix, 2026-11-21, sonnet; over rev 4.1,
lane bsu1). Request R-47 (`memfn/docs/requests.md`); ruling D201 (slug
block-build). Order: this note, critic rounds r68 and r69 (done), rev 4, the
LIGHT re-check r71 (done), rev 4.1, **U1 built (lane bsu1), U2 and U2b built
(lane bsu2), code round r75 (done: FIX FIRST, small), this revision (r75's
doc items, with U2's fixes)**. **`scalar-check-cut` is ANSWERED: Frank
2026-11-21, "scalar-check-cut: yes" (D201 add. 4; §2.2). One owner question
is OPEN: `wrap-clang` (§2.2.1), which the census's compiler scope raises
[rev4.2, r75 CENSUS-3].** Read §18 (the r75, r71, r69 and r68 dispositions)
first.

Revision history:
- rev 1 (2026-11-21, lane bspan): first design, gated on `scalar-wrap`.
- rev 2 (2026-11-21, lane bspan2): scalar-wrap read as option A, option B
  retired, U2b and T-keep added, population record replaced by the final
  census, manager calls recorded, §17 ship-size.
- rev 3 (2026-11-21, lane bspan3): review r68 applied (review
  `docs/dev/reviews/2026-11-21-r68-memfn-bspan.md` on the kit branch, with
  the kit manager's ruling).
- **rev 4 (2026-11-21): review r69 applied** (lane bspan4; review
  `docs/dev/reviews/2026-11-21-r69-memfn-bspan3.md` on the kit branch, its
  MANAGER RULING). The three decisions as ruled: the stretch list is
  STORED ONCE (R-2), U2 lifts `fn_selector` only (R-4), SPAN-SEED is a
  committed `.rxt` with a `MEMFN_CLASS` row and a per-check wiring line
  (R-20). Also: `skip`'s producer is `wf_find_prepare` (R-1), the table's
  contracts and homes (R-3), C-own stretches only (R-5), the C18 rule
  reworded and drilled at B = 16 and B = 32 (R-7..R-11), the identity
  gate's mask drilled on real artifacts (R-12), U2's anchor moves (R-13),
  four lever/force pin cells, a D1w cell and the frame column dropped
  (R-14..R-16), U2b's normalizer declared as one regex with two-sided
  controls and a second known positive (R-17, R-18), the k source named
  (R-19), CANDIDATE until every bench box runs V (R-31), arm 2's nine
  surfaces (R-26), the two sentences for the owner (R-25), §17 recounted
  with the plan rows "to be filed by main" (R-30). Text changed in rev 4
  is marked `[rev4, R-n]`; `[rev3]` marks survive where rev 3's text
  stands.
- **rev 4.1 (2026-11-21): review r71 applied** (lane bsu1, the U1 build
  lane's first commit; review `docs/dev/reviews/2026-11-21-r71-memfn-bspan4.md`
  on the kit branch, its MANAGER RULING): R71-1..R71-7 as text fixes; the
  §15 Q4 ruling (the `span-vector` `MEMFN_CLASS` corpus floor pinned at the
  measure at U2, not 0); R71-3's floor-branch reading CONFIRMED; the owner
  question renamed `scalar-check-cut` (it replaced `wrap-differs`), both
  readings carried. Text changed in rev 4.1 is marked `[rev4.1, R71-n]`.
- **rev 4.2 (2026-11-21): review r75 applied** (lane bsu2fix, the U2 fix
  lane; review `docs/dev/reviews/2026-11-21-r75-memfn-bsu2.md` on the kit
  branch, its MANAGER RULING: FIX FIRST). D201 add. 4 is recorded (FREEZE
  NOTE row, §2.2 ANSWERED, the CONSTRAINT collapsed to arm 1); the U2b
  census record carries the DIFFERS classes by k, GNU-diff counts and the
  census's COMPILER SCOPE (§2.1); the owner question `wrap-clang` is OPEN
  (§2.2.1); the identity gate is a DELIVERY step (§10.1, §14). Text changed
  in rev 4.2 is marked `[rev4.2, r75-ID]`.

Inputs read: D201 and its addenda 1-3 (main at `d255d94a3`), D146, D147,
D155 and its items 2 and 6, addenda 1-3, D144 addendum 4, D76/D94, D80;
integration.md §14, §15, §17.2, §18; the 710 run's `decision.md`,
`confirm.py`, `spike708.py`; review r68 and review r69 with their critic
files; `tests/memfn/simd_floor_check.py`, `tests/memfn/routing_shape.py`,
`tests/axes/memfn_arm.py`; `memfn/src/window.c`, `ofsskip.c`,
`compose.c`, `vany.c`, `runcmp.c`; `memfn/docs/trace_format.md`;
`docs/spec/rxt_format.md` §1.1, §4, §6; `docs/dev/guide/README.md` +
`coding.md`.

## FREEZE NOTE: the rulings this note rests on, restated here [rev4, R-23, R-24, R-32]

Review r68 found rulings that lived only in lane files. Since rev 3, main
has recorded most of them: D201 addendum 3 (main `d255d94a3`, from r69's
relays R-23 and R-24). Each row names its record.

| ruling | words (whose) | record | what it means for this design |
|---|---|---|---|
| D201 | Frank, verbatim: "build with simd layer" | D201 Decision (verbatim words in the kit journal, commit 923ea33d2) | the build go for 710's table at the SIMD-on layer. "The scalar layer stays H64" is D201's "Read as" line, main's reading, and D201 add. 3 (a) says add. 2's READING supersedes it |
| D201 add. 1 | Frank, verbatim: "We're here and there's no downside so let's build it." | D201 add. 1 | the population count is **information only**; it does not gate the build or its scope |
| D201 add. 2 (`scalar-wrap`) | Frank, verbatim: "the function goes inline so it's just code organization? If that's true I don't have a problem with that." He had been told, before the reading was formed, that this "is true in source, but gcc's machine code differs on 2 of 10 probes (`\w{20}`, `\w{32}`)" | D201 add. 2 | **The recorded READING, in full** (the kit's and main's, not his words): "option A, with the SIMD-off machine-code changes checked for no loss: a non-timing census of the corpus and bench sites whose scalar machine code changes, then a short timing of only those in a window he clears; any loser keeps today's text through a selector row." **It moved:** the kit manager's r68 ruling (F-14) CUT the short timing (710's cell rule cannot return LOSS on a uniform small effect, r68 MEAS-5) and the keep-a-loser selector row (no compile-time fact keys it, §2.2). What remains is option A with the census (§2.1). D201 add. 3 (a) restates the uncut reading in main's amended R-47 GO line: relayed to main (§15) |
| D155 item 6, AMENDMENT (Frank) | "The SIMD-off artifact routes through the helper too — a one-time, measured byte move and abi event — so the floor rule stays exact." | decisions.md D155 item 6 | the strongest record for option A's shape. It says MEASURED. Arm 1 of the fork (formerly `wrap-differs`, now inside `scalar-check-cut` [rev4.1]) ships an UNMEASURED SIMD-off machine-code move on the `\w`-like sets. Whether D155 add. 3's relaxation also relaxes "measured" is a READING (this lane's), and the owner is given the word (§2.2) |
| D155 add. 3 (Frank) | "They were more guidelines or goals than hard rules" | D155 add. 3 | main's "What stands" line: "NO `#if`/`#ifdef` in the code the kit emits into a function BODY". The single-call shape is a GUIDELINE; this design rests on the contract (§2) |
| D155 recollection (Frank, relayed by the kit manager) | "We talked about that being the way we'd organize simd stuff anyway back when you used ifdef macro code" | D201 add. 3 (b), recorded as an OBSERVATION, not a ruling; the verbatim words are the manager's relay | context only: the selector shape is the organization D155 add. 1 Q-R9-10 agreed |
| D201 add. 4 (`scalar-check-cut`) [rev4.2, r75 SLOT-5] | Frank, verbatim, to the kit: "scalar-check-cut: yes" | D201 add. 4 (the words are in the kit journal, memfn/docs/journal.md) | the cut is accepted: U2b's census replaces the scalar timing; the real bench sites' SIMD-off code must be identical or the build stops, a differing grid shape is REPORTED, `\w{20}` is the floor witness; no T-keep. Arm 1 (wrap everything) stands, arm 2 is dead. The stop rule names no compiler: the census is gcc 15.2 -O2 (§2.1, `wrap-clang`) |
| R-4, smallest form | "design the SMALLEST form that serves the 710 table. Add no generality beyond what 710 confirmed" (the kit's bspan ruling, main asked for it) | the kit's r69 MANAGER RULING R-4 (docs/dev/reviews/2026-11-21-r69-memfn-bspan3.md, on the kit branch); D201 add. 3 (b) holds a paraphrase ("the smallest form that serves job 710's table, no generality beyond it"), not these words [rev4.2, r75 SLOT-5] | no widths, site kinds or knobs beyond 710's table, the deny row and the card |
| `scan-scope` | WALK only, not LIBC/PAIR: nothing else was measured (D77) | D201 add. 3 (b), KIT MANAGER | T-vscan holds on finder row **R7w** only. D1w is EXCLUDED ON PURPOSE (F-4; §3.3) |
| `wrap-deny` | the deny `span-vector` is LIVE at both layers | D201 add. 3 (b), KIT MANAGER | `--memfn=no-span-vector` un-wraps the stretch too, restoring main's bytes at every layer and target |
| D155 item 2 | "a SIMD level is judged on EVERY bench box that runs it: a loss anywhere blocks the level, and a win somewhere is required. Rows may land first as CANDIDATE behind the OFF switch." | D155 item 2 | [rev4, R-31] V lands CANDIDATE behind the OFF switch until a run on every bench box that runs it (§8, §13) |

## CONSTRAINT (above the goals) [rev4, R-27]

The kit manager's r68 ruling (F-14, F-21) of a reading of the owner's
conditional answer (D201 add. 2):

**SIMD-off renders the H64 form. On the population (§0.1) its machine
code is identical to today's (U2b, §2.1), or the build stops. Elsewhere,
every eligible set is wrapped and accepted as code organization (D201
add. 4, `scalar-check-cut`: yes), its differing machine code REPORTED by
the census and not timed [rev4.2, r75 SLOT-5].**

No goal below can trade against this line. It does not claim that the
wrapper is machine-code neutral everywhere: on three classes of set it is
not (`\w`, `[aeiou]`, `[A-Za-z0-9_-]`; §2.1's record), and `\w{20}` is
eligible in the default build.

## 0. Goals (ranked; a conflict goes to the higher one)

| # | goal | who benefits | checkable form |
|---|---|---|---|
| G-1 | **Answer identity.** Every artifact answers exactly as today, at every layer, width and target. | every caller | G2 (§10): 0 differences against python `re` and against the family's own reference, on guard-page subjects; [rev4, R-20] the committed SPAN-SEED `.rxt` (§10.1) is in the corpus, so `make test-corpus` checks its oracle-verified answers at the default build, and `make test-axes` checks the `span-vector` deny arm answer-identical over the corpus (it included) at both layers |
| G-2 | **The shipped text is the timed text.** Where the table routes a stretch, the machine code gcc makes for `rxa_search` is identical to 710's `avx2-loop` arm. Where a difference remains, it is named and measured. | the 710 verdict's validity (MEASUREMENT-3) | F2 (§6): `objdump` of `rxa_search` identical to 710's `avx2-loop` arm source, addresses normalized, on each of the 82 routed cells of 710's grid. A DIFFERS is listed with its diff, enters C6's population, and blocks the landing until the code round rules it |
| G-3 | **No repeated LOSS where it ships.** The SIMD-on movers keep 710's claim: no repeated LOSS against `--memfn=no-span-vector`. | `-fmemfn-simd` users with long one-class spans | card C6 (§8): 0 repeated LOSS, on EVERY bench box that runs V (D155 item 2); until then V is CANDIDATE. Wins are reported, not gated |
| G-4 | **Nothing else moves.** At SIMD-off, and at every target that does not admit `w32`, the only bytes that move are the ones §11 lists. The deny restores today's bytes exactly. | default-build users | the identity gate (§10.2): the `no-span-vector` artifact equals the merge base's artifact over the corpus (SPAN-SEED's `.rxt` included) at widths 32 and, for SPAN-SEED's patterns, 4095, both layers, after the DECLARED mask (§10.2, nine anchored spellings, drilled on real artifacts) |
| G-5 | **One table, no parallel mechanism.** The span-form choice is one declared first-match table, and these are its rows. | maintainers (Frank's table rule) | `wf_span_head` is retired. One row array exists, walked once per stretch by one enumerator (§3). A grep for a second span-form decision finds none. The selector line is written by the one selector writer ofsskip already uses (§5) |

Non-goals: the scalar layer's own block form (D201: "**Revisit when:** the
scalar layer is measured"); a 16-byte (`w16`) rung; the SWAR rung of
708's cascade (no table row reaches it, §4.4); a periodic span; the LIBC,
PAIR, D1w and floor sites (unmeasured, §3.3); aarch64 (K-4; D147 addendum
8); a scalar timing of the wrapper (cut by r68, F-14).

### 0.1 Population record (information only, D201 add. 1) [rev4, R-21, R-20]

The real population is **3 bench sites, and the real corpus holds 0 V
sites at any width.** This is the population BEFORE this build: the
real-pattern record. The build commits SPAN-SEED's `.rxt` into the corpus
(§10.1, R-20), after which the corpus holds 28 V sites at the default
width; those are seeded witnesses, not real patterns, and every count that
means "real" says which file it excludes (§9.4).

| pattern | bench id | finder row (MFTRACE FDROUTE) | k | at width 32 and 4095 |
|---|---|---|---|---|
| `[0-9a-f]{32}` | bounded/hex32 | D-hors (HORS), frame E-find | 31 | same |
| `\b[0-9a-f]{32}\b` | loglines/hex32-id | D-hors (HORS), frame E-find | 31 | same |
| `\d{32}` | bounded/dig-exact-32 | R7w (WALK), frame E-find | 31 | same |

Command: §16 item 5. Every real site has k = 31: none reaches the B = 32
rung or either upper bound. The corpus row `tests/counterk/counterk.rxt`
line 1919, `(?:ab|ba|aa|bb){24}c`, is a D1 site (a memchr find), which
`scan-scope` excludes. At the default window width (32) only k 16-31
(window) / 24-31 (scan) is eligible; main's owed cover-width timing
(`cover_cap.md` §11.4 B) decides whether that default rises. [rev4, R-29]
D201 add. 2's population line now reads "0 corpus sites ... and 3 bench
sites" at main (checked at `d255d94a3`), citing review r68.

## 1. Site map: where it lives today (found by grep)

| what | where (command) | today |
|---|---|---|
| the option row | `grep -n 'span-loop' memfn/src/options.def` → 122 | `MF_OPT("span-loop", MF_OPT_PAIR, MF_B_ANY, MF_L_SCALAR, ...)`. Deny = I, force = L |
| the decision | `grep -n WF_SPAN_HEAD memfn/src/window.c` → 1470, 1476, 1483 | `wf_span_head()` (window.c:1477): an IF CHAIN (deny → I, force → L, lever `span-head=N` → H(N), else H(64)), returned as one head `h` per SITE (`plan_of`, :1491) |
| the segmenter | `grep -n 'wf_loop_len\|static int wf_loop\|wf_test_to' memfn/src/window.c` | `wf_test_to` (:3536) walks the plan in offset order. `wf_loop_len` (:3498) finds a ONE-CLASS STRETCH: consecutive core `KIT_POS_WIDE` entries with one set and one table offer, at offsets ≥ h, never crossing entry `skip`. `wf_loop` (:3517) renders it as one loop |
| who renders it | `wf_test_to`'s callers (`grep -n 'wf_test_to(' memfn/src/window.c` → 3576, 3584): `c_find_test` (E-find) and `wf_test` (E-generic, the floor) | the only two renderers of a candidate test |
| `skip` | `grep -n '\*skip =' memfn/src/window.c` → 3977, 3988 | an OUTPUT of the head renderers: `d_hors_head` (HORS: `ih >= 0 && grp[ih] < 0 ? ih : -1`, `ih = plan_ix(w, w->hl)`) and `find_head` (find rows: `stop_alone ? stop_ix : -1`). Not a plan field today |
| [rev4, R-1] the plan's order | `wf_plan_site` (window.c:2510): `decide` → `plan_of` (:2516) → `wf_find_decide` → Table E's walk → renderer rows → `wf_find_prepare` (:2578) | `plan_of` memsets `w` and writes off/set/core/table/`stop_ix = -1`. `wf_find_prepare` (:2456) writes `brow` (:2461), `stop_alone` (:2464), `grp` (`find_groups`, :2471), then the search row's `prepare` (B-hors's writes `w->hl`, :1999) |
| 710's "site kind" | `struct wf_plan` fields `pick` and `brow`; `grep -n 'w->brow' memfn/src/window.c` → 2461 (the only writer) | "window" = E-find with pick `FF_HORS` (row D-hors). "scan" = E-find with pick `FF_WALK`, whose finder row `w->brow` is **R7w** (710's four scan classes) or D1w (`FB_UNMEASURED_DEFAULT`) |
| the level fact | `grep -n 'art->levels = ' memfn/src/compose.c` → 1102; `memfn/src/levels.def` | `art->levels` = the levels the target admits: `LV_X86_W16` (sse2, x86-64) and `LV_X86_W32` (avx2, x86-64-v3). 0 at `-fno-memfn-simd` |
| the SIMD seam idiom | `ofsskip.c` `fn_level_block` (:707), `fn_selector` (:727), `fn_head` (:615), `fn_call_line` (:626) (D155); `vany.c` `vany_level` (:155), `vany_selector` (:189) (not routed) | `<fn>__body`, one bracketed helper per admitted level, and a selector `<fn>` with ONE call to the top helper. `simd_open`/`simd_close` are a byte COUNT in pcrec's sink (`src/core/sb.c` `pcrec_sb_simd_open`/`_close`), whole lines only ("a bracket opened mid-line" aborts); the ISA comes from the file-wide REGION pragma pcrec writes |
| the window family's store-once idiom [rev4, R-2] | `wf_plan_site`'s header (window.c:2496-2509): "WHAT THE DEFINE RENDERS ... each stored in `w`, where the define renders from it"; define and use read one stored plan (`r->wplan`, :3006, :3371, :4065) | the precedent for §3's stretch list |
| the header fact | `memfn/src/includes_c.def` | `MF_INC_LEVEL_W32` = `#include <immintrin.h>`, placed by pcrec at file scope, ahead of the region |

**Premise test (the brief's).** The 710 TABLE's "site = window / scan" maps
to facts the kit already has: the plan's pick (`w->pick` = `FF_HORS`) and
its finder row (`w->brow` = D-hors or R7w; `brow` is written only by
`wf_find_prepare`, so a set `brow` already means frame E-find). k is the
stretch's length, which `wf_loop_len` computes from `skip` (§3.1). The
SIMD-on layer is `art->levels & (1u << LV_X86_W32)`. No pcrec-side fact is
needed, and all of these are the kit's own picks, so facts-only (D157)
holds.

**One correction to the brief's framing.** There is no separate "scan site"
span. Both 710 site kinds are window.c E-find sites. They differ only in
T-FIND's pick and finder row.

## 2. THE PREMISE FORK, RESOLVED: the timed text is not a shape the SIMD seam admits

Job 710 timed this replacement: inside the walk's statement expression,
which is ONE line, the span's inline chain is replaced by a call to an
`always_inline` function defined at the top of the region. The SIMD-off
artifact keeps the chain. That diff between OFF and ON is an **inline
expression replaced mid-line**. The contract admits exactly two kinds of
difference:

- **C18 (c)** (`tests/memfn/simd_floor_check.py` docstring): "the raw diff
  OFF -> ON deletes no line but the moved stamps and, per SIMD FUNC, its
  one `return <fn>__body(<args>);`, replaced by the same call to
  `<fn>__w<VW>`".
- **`limits.md` §8.3¶1**: the length every size decision reads is the
  SIMD-off length exactly, so "turning SIMD on cannot rescue or refuse a
  pattern or move a ladder step". `tuning.md` §2.43¶4 states the same
  floor. D155 add. 2 is its ruling (SIMD bytes neutral to size decisions).

A mid-line replacement cannot be bracketed (the sink aborts on a mid-line
bracket). It shortens an unguarded line, so the length decisions would read
a SIMD-dependent length. The 710 shape therefore fails C18 and breaks
§8.3¶1.

**The shape taken (option A: the kit's and main's reading of D201 add. 2,
as cut by r68 F-14; not Frank's words).** An eligible stretch (§3: HORS
with 16 ≤ k ≤ 1000, or R7w with 24 ≤ k ≤ 64, C-own entries;
layer-independent facts) renders **at every layer** as a call
`<p>_mf<h>_vs<j>(S, C)` to a selector, in ofsskip's shape:
- `__body` is today's H64 text of that stretch;
- at a target admitting `w32`, a bracketed level block (`__w32_b`, then
  `__w32`, the 710 form) is added and the selector's one call names
  `__w32`.

The reason this is not a new cost rests on the CONTRACT: C18 (c) admits
exactly one replaced call per SIMD FUNC, and `limits.md` §8.3¶1 with D155
add. 2 keeps every size decision on the SIMD-off length. D155 item 6's
AMENDMENT (FREEZE NOTE) is the record of this shape: "The SIMD-off artifact
routes through the helper too". D155 add. 3 made the single-call shape a
GUIDELINE; what stands is "NO `#if`/`#ifdef` in the code the kit emits
into a function BODY". The `#if` is gone today (`limits.md` §8.3¶1: the
host's region supplies the ISA).

OFF and ON then differ only as C18 admits, and the lengths stay those of
SIMD-off. **The cost: SIMD-off bytes move** on eligible stretches. The FORM
is still H64, but its text sits inside a function.

**The wrapper is code organization in source; gcc's machine code can
differ on some sets.** Frank's words (D201 add. 2, verbatim): "the
function goes inline so it's just code organization? If that's true I
don't have a problem with that." The function is `always_inline`, so in
source it is only code organization. What gcc makes of `rxa_search` is a
separate fact [rev4: re-drilled by this lane, §16 item 12]:
- **On the real population** (the 3 bench sites, §0.1) the two-level shape
  (selector → `__body`) gives SIMD-off `rxa_search` machine code that
  differs in NO instruction from today's at widths 32 and 4095 (one site,
  `\b[0-9a-f]{32}\b`, differs in 3 padding lines, which the declared
  normalizer removes).
- **On `\w`-like sets it differs**: `\w{17}`, `\w{20}`, `\w{32}` (r68: 20-26
  lines one-sided; rev 4's lane: `\w{20}` 42 lines added + removed after
  normalizing, a figure r71 did NOT reproduce: 26/22 by difflib, 24/20 by
  GNU diff [rev4.1, R71-7 (a)]; the verdict DIFFERS holds), and [rev4, R-18] `\w{501}` at width 4095 (2 lines; r68's
  figure reproduced). None of these is in the corpus or the bench.
- **On `[+.0-9]{65}`** (num k = 64) the two-level shape is identical to
  today (r68).
- **The inline depth matters.** 710's control arm Hspk is a ONE-level
  wrapper, so Hspk's results are not evidence for the shipped wrapper.
- At `-fmemfn-simd=x86-64` (w16 only) the machine code equals
  `-fno-memfn-simd`'s for wrapped and unwrapped `\w{20}`/`\w{32}` on gcc
  15.2 (r68 NOTED): the SIMD-off reading covers w16 on this compiler (not
  shown for clang).

**Why option B was not taken.** B admitted "a replaced inline expression"
as a third diff kind, keeping SIMD-off bytes and 710's exact text, but it
changes C18 (c)/(b), `tuning.md` §2.43¶4 and pcrec's length accounting (a
kit-to-pcrec fact, or a second OFF render): a seam change outside this
design's remit, with its own architecture note. The reading of D201 add. 2
makes it unnecessary.

### 2.1 The scalar no-loss check: a machine-code census on the BUILT text (§14 U2b) [rev4, R-17, R-18]

Rev 2's three parts became one in rev 3. **Dropped:** the scalar timing
(its cell rule reads a uniform 14 % slowdown as TIE: r68 MEAS-5) and T-keep
with §2.1 (c) (no compile-time fact keys a "keep list": §2.2).

**U2b, the census.** On the BUILT U2 text (never a probe: the inline depth
changes the answer, §2), for each pattern below, `objdump -d
--no-show-raw-insn` of `rxa_search` at `-fno-memfn-simd`, the default
(wrapped) artifact against the `--memfn=no-span-vector` artifact (today's
text), both from the U2 binary, gcc -O2, **both arms compiled under the
same `-o` basename** (the `#include "<name>.h"` line otherwise differs):
- **normalization, declared before data:** each line's address prefix
  stripped; every `<hex> <symbol+off>` operand replaced by one token;
  whitespace runs collapsed; then every line matching ONE regex is
  removed as padding:
  `^((data16|cs) +)*(nop[wlq]?( .*)?|xchg +%ax,%ax)$`. A diff that
  survives is DIFFERS, with its count of added plus removed lines. Nothing
  else is normalized.
- **population:** (1) the real population: the 3 bench patterns (§0.1), at
  widths 32 and 4095; (2) the PROBE GRID: 710's ten classes (`confirm.py`
  `CLASSES`) x k 16..31 at width 32, i.e. `cls{17}` .. `cls{32}`, 160
  patterns, of which 128 hold an eligible stretch (6 window classes x 16 k,
  4 scan classes x k 24..31); (3) `\w{501}` at width 4095 (710's word500, a
  routed cell), so the census sees one k > 31 shape.
- **the normalizer's two-sided control:** `\b[0-9a-f]{32}\b` is its
  POSITIVE control (raw > 0, normalized 0: drilled 3 → 0, §16 item 12);
  `\w{20}` its NEGATIVE (normalized > 0: drilled DIFFERS; the count
  depends on the diff tool, §16 item 12). If either side
  fails, the census is red (it cannot see what it is for).
- **known positives:** `\w{20}` (k 19) and `\w{501}` at 4095 (k 500) must be
  reported DIFFERS; either reading IDENTICAL makes the census red.
- **the 32 non-movers** (4 scan classes x k 16..23) render byte-identical C
  in both arms (T-head decides in both). They are printed as a BYTE-COMPARE
  count ("32 of 32 identical C"), not as an objdump control: an identical
  pair cannot exercise the normalizer (a control sharing its source).
- **output:** each count (patterns compiled, eligible, IDENTICAL, DIFFERS)
  and the DIFFERS list by class and k, in the build lane's report.
- **command:** the build lane states it in its report; it is a delivery
  step, not a committed test (arm 2 would change this, §14). [rev4.1,
  R71-7 (a)] **It NAMES its diff tool** (difflib or GNU diff: the count of
  added plus removed lines differs between them) and re-derives the
  `\w{20}` figure with it.

The census is the CONSTRAINT's checkable form on the population (identical
there, or the build stops), and the record the owner's answer reads on
the grid.

**The U2b record as built and re-derived [rev4.2, r75 CENSUS-1..5]** (the
lane's census and the code round's independent re-implementation agree;
counts are GNU diff's, equal to python difflib at `autojunk=False`):

| population | compiled | eligible | IDENTICAL | DIFFERS |
|---|---|---|---|---|
| the 3 bench patterns x widths 32, 4095 | 6 | 6 | 6 | 0 |
| the grid: 10 classes x k 16..31 at width 32 (`cls{17}`..`cls{32}`) | 160 | 128 | 80 | 48 (+ 32 non-movers, byte-identical C) |
| `\w{501}` at 4095 | 1 | 1 | 0 | 1 (2 lines) |

The grid's DIFFERS set is THREE classes, each at EVERY k 16..31 (not
"`\w`-like sets"; an earlier summary and the owner-facing list "`\w{17}`,
`\w{20}`, `\w{32}`" were incomplete):
- `\w` (4 terms): 16 of 16; 20 lines at every k (GNU diff; a `cmp`/operand
  change);
- `[aeiou]` (5 terms): 16 of 16; 38 lines at every k (a block reorder, an
  early-exit `ret` tail moved: a different change kind);
- `[A-Za-z0-9_-]`: 16 of 16; 2 lines at every k (one `cmp` operand order).
Identical: `[0-9a-f]` 16, `[a-f]` 16, `[^\n]` 16, `[0-9]` 8, `[\x80-\xbf]` 8,
`[A-Z]` 8, `[+.0-9]` 8. At width 4095 the same three classes differ at every
sampled k 32..1000 (`\w{501}` 2 lines); the other classes, and every
T-vscan shape at k 33/49/65, stay identical. Under `-e utf8` the hex and
`[0-9]` stretches differ at SOME k (`{25}` and `{28}`, 10 to 13 lines; an
early-exit tail moved) while the 3 bench patterns stay identical (4 of 4):
the census is byte-only, and no set property keys the differing set
(§2.2 arm 2's term-count correlate is weaker still). The `\w{20}` figure
is **20** (GNU diff, `autojunk=False`); the 42 / 26-22 / 24-20 spread of
the earlier figures was python difflib's autojunk heuristic
(`rxa_search` is over 200 lines), not the wrapper.

**The census's COMPILER SCOPE [rev4.2, r75 CENSUS-3].** The census as
declared is gcc 15.2 at -O2, and passes there (the stop rule is not
tripped). On the 3 REAL bench sites the SIMD-off code is identical under
gcc -O1, -O2, -O3 (also -O2 -fPIC and -march=native, 24 of 24 cells) and
DIFFERS under **clang 21 -O2 and -O3** (`\d{32}` 264 lines, the two hex
sites 12: a range test re-derived) and **gcc -Os** (all three sites 5
lines: a branch inverted), at both widths (18 of 18). The grid at {17, 20,
25, 32}: clang -O2 differs on 28 of 32 eligible (identical only `[^\n]`),
gcc -Os on 32 of 32, gcc -O3 and -march=native on 12 of 32 (the -O2 set).
D201 add. 4's record names no compiler; the owner's premise (add. 2: "the
function goes inline so it's just code organization?") holds on the real
sites for gcc at -O1..-O3 only, and the bench builds the pcrec arms with
clang as well. That is the open owner question `wrap-clang` (§2.2.1). No
timing is implied: add. 4 cut it.

### 2.2 OWNER QUESTION `scalar-check-cut` (ANSWERED: yes, D201 add. 4; it replaced `wrap-differs`) [rev4.2, r75 SLOT-5; rev4.1, r71 FREEZE DRIFT; rev4, R-25, R-24]

**[rev4.2] THE ANSWER.** Frank, 2026-11-21, to the kit, verbatim:
"scalar-check-cut: yes" (D201 add. 4). **He KEEPS the cut**: the census
(§2.1) is the SIMD-off record, arm 1 (wrap everything) stands and arm 2
(the proxy row) is dead, the short timing and T-keep are dropped, and the
cost is accepted and filed as [BSPAN-SCALAR-RISK] (a user pattern of a
changed shape ships changed, unmeasured SIMD-off code; trigger: a bench or
user pattern of that shape: measure it). The text below is the question as
it was put and the fork as it was framed, kept as the record; its "OPEN"
and "carries both readings" statements are history.

**[rev4.1] The question as put.** Main declined to amend D201 add. 3 (a)
on the kit's ruling alone: option A was put to Frank WITH the short scalar
timing and the keep-a-loser row, and r68 F-14's cut of both narrowed what
he was told, so the cut needs his word (kit journal, 2026-11-21 02:15). One
owner question, `scalar-check-cut`, replaced `wrap-differs`; the kit and
main put it to him with the reasons (no real site differs; 710's cell rule
is blind to a uniform 14 % loss; no compile-time fact keys T-keep) and what
U2b's census proves. **This note carries both readings until he answers:**

- **He KEEPS the cut.** The text below stands with the question renamed:
  the census (§2.1) is the SIMD-off record, and the fork that follows
  (formerly `wrap-differs`: arm 1, wrap everything; arm 2, the proxy row)
  is decided inside it, as written.
- **He RESTORES the short timing and/or the keep-a-loser row.** U2b gains
  a timing step in a window he clears, and T-keep returns, which r68 found
  no compile-time fact keys (arm 2 below): that is new design for U2
  onward, from r71's hand mapping, not a text fix.

U1 is unaffected under either reading: it moves no artifact byte (§14).

The fork, as rev 4 framed it (it applies where he keeps the cut):

**The fact.** The wrapper changes gcc's SIMD-off machine code on `\w`-like
sets (`\w{17}`, `\w{20}`, `\w{32}`, `\w{501}` at width 4095), and on none
of the 3 real sites. That is outside his words as he said them ("If that's
true ..."). U2b's census will name the full differing set on the grid.

**What he was told and what changed since.** Before his answer he was told
that gcc's machine code differs on 2 of 10 probes (`\w{20}`, `\w{32}`).
The reading recorded after it named a short timing of the changed sites
and a keep-a-loser selector row. Both were cut (r68 F-14, the kit
manager): the timing because 710's cell rule cannot return LOSS on a
uniform small effect, the keep row because no compile-time fact keys it.
D155 item 6 calls the SIMD-off routing "a one-time, measured byte move";
whether "measured" still binds after D155 add. 3 is a reading.

**The question:** is that acceptable as code organization, or should
`\w`-like sets keep today's text?

**The two outcomes, as a stated fork:**

1. **Wrap everything.** Every eligible stretch renders the selector at
   every layer, as §3/§5 say. The differing machine code on `\w`-like sets
   is accepted as code organization, recorded by U2b's census (the list,
   by class and k) and not timed. **This arm also waives D147's
   both-layers reading ("Every acceptance reading for a change that
   touches searching reports BOTH layers") and R-47's "G1 alpha at both
   layers" at SIMD-off on the sets whose code differs, where the census
   gives no reading. A measurement of that change is possible (an
   aggregate test, or a stated minimum detectable effect: r68 MEAS-5), but
   it was declined on cost.** [rev4, R-25]

2. **Do not wrap the sets whose machine code differs.** This needs a
   compile-time fact that says "gcc will make different machine code for
   this stretch". **None exists.** Whether gcc's machine code differs is
   an output of gcc's inliner and register allocator at one version and
   flag set; the kit sees the set, k and the frame, never that outcome.
   The nearest kit fact is a correlate: the number of terms
   `kit_set_test` renders for the set (`\w` renders 4; hex and `[0-9]`
   render 2 and 1; `[+.0-9]` renders 3 and does not differ). What that
   implies:
   - a row keyed on a term count would be a per-shape exception chosen to
     fit one gcc's behaviour on the probes known: a special case (Frank's
     general-mechanisms rule) that a gcc upgrade can silently invalidate.
     U2b's census would have to become a committed check;
   - the vector helper needs the selector (C18 (c)), so an unwrapped
     stretch also loses V at SIMD-on: `\w`-like sets would forfeit 710's
     measured wins (710's word and ident classes are routed window
     classes);
   - the only way to keep `\w`-like SIMD-off text AND their SIMD-on V is
     option B's seam (§2), which needs its own architecture note.

   The build plan under arm 2 is §14's list (R-26).

**Leaning (for the question's framing only; no ruling records a leaning,
r69 R-24):** the bspan3 and bspan4 lanes lean to outcome 1, the only one
with no proxy and no forfeited win. The owner decides.

### 2.2.1 OWNER QUESTION `wrap-clang` (OPEN; U2 does not wait on it, it goes to main with the delivery) [rev4.2, r75 CENSUS-3]

Add. 2's premise ("the function goes inline so it's just code
organization?") and add. 4's stop rule ("the real bench sites' SIMD-off
code must be identical or the build stops") were checked at gcc -O2 only
(§2.1's compiler scope). The bench HAS clang arms (pcrec-auto-clang,
pcrec-nocaps-clang, pcrec-vm-clang and the -clang-utf8 siblings), and on
clang -O2/-O3 and gcc -Os every real site's SIMD-off code differs. The
question for him: is the wrapper still acceptable as code organization
where the compiler is clang (or gcc -Os), as he accepted it for gcc, or
should those consumers keep today's text? The build does not stop on it
(the declared census passes); a "no" is a new design (no compile-time fact
names the consumer's compiler: §2.2 arm 2's reasoning applies, with a
compiler for a set). The kit's leaning: carry the cost under
[BSPAN-SCALAR-RISK] like the other changed shapes, and measure a clang
bench arm when the scalar layer is next timed. It is the kit and main's to
relay; this lane does not wait on it.

## 3. The selection: THE SPAN FORM TABLE (rows added to the existing choice)

`wf_span_head`'s if chain becomes a declared first-match table. Its rows
are evaluated **per one-class stretch**, by one enumerator, once per site
(below). The facts:

| fact | where it comes from |
|---|---|
| `opt(span-loop)` | the site's opts (`kit_opt_state`): deny, force or neither |
| `opt(span-vector)` | the V rows' option column (`wf_erows[].opt`'s idiom), applied by `walk_row` |
| `lever` | the art's `KIT_LEVER_SPAN_HEAD`, test-only |
| `brow` | `w->brow`, the finder row (D-hors for HORS; R7w / D1w for WALK); written only on E-find |
| `k` | the stretch's length (§3.1) |
| `own` [rev4, R-5] | every entry of the stretch is C-own (`w->table[i] == 0` across it) |
| `w32` | `art->levels & (1u << LV_X86_W32)` (the TEXT of V, never its selection) |

Compile-time facts only; no class name.

| row | holds when (first match) | form | origin |
|---|---|---|---|
| T-deny | `no-span-loop` given | I (every position inline) | today, row 1 of the chain |
| T-force | `span-loop` forced | L (h = 0) | today, row 2 |
| T-lever | test-only `span-head=N` | H(N) | today, row 3 (the cards' instrument) |
| T-vwin | brow D-hors, 16 ≤ k ≤ 1000, own, `span-vector` not denied | V | **NEW**, 710 row 1, MEASURED |
| T-vscan | brow R7w, 24 ≤ k ≤ 64, own, `span-vector` not denied | V | **NEW**, 710 row 2, MEASURED |
| T-head | always | H(`WF_SPAN_HEAD` = 64) | today, the default (MEASURED by cards run fcards-zen4-1) |

- [rev4, R-15] **The frame column is dropped** (a simplification): `brow`
  is written only by `wf_find_prepare` (window.c:2461), so brow D-hors or
  R7w already means frame E-find. The rev 3 frame pin could not fail.
- [rev4, R-5] **`own`**: V's selector takes `(s, c)` and no table, while
  pcrec emits offered tables as FUNCTION-LOCAL statics (`emit_u8_table`,
  emit_dfa.c; inside `rxa_match`), so a `__body` at file scope cannot name
  one. A stretch whose entries share a C-table offer stays on T-head
  (answer-neutral: today's text). No pcrec site reaches this today: every
  eligible loop in SPAN-SEED's census is C-own (§16 item 5).
- [rev4, R-6] **Admitted on purpose:** the table is class-free by design.
  Two R7w shapes 710 did not time as such are admitted: a dense class that
  reaches R7w because D-hors is denied (`[0-9a-f]{32}
  --memfn=no-window-skip` traces R7w, k 31), and a mixed stretch/stop site
  (`[0-9a-f]{31}[0-9]`, R7w, a hex stretch with a digit stop, k 31). Both
  drilled (§16 item 5). Answers hold by §4.3; C6 does not time them (they
  are not real sites).
- T-keep is gone (r68 F-14). Under `scalar-check-cut` kept and outcome 1 the table is
  exactly this. Under outcome 2 a proxy row sits between T-lever and
  T-vwin (§14's list).
- [SEAM-7, NOTED] T-vscan is window.c's first decision keyed on a finder
  row's id. The build reads it as the finder row's identity, never a
  second spelling of the id string in window.c: `w->brow` is
  `fd_rows[...].id` (finder.c), and the build compares against the
  finder's own row (a pointer or an exported predicate), so one file
  spells "R7w".

**V** is the selector call (§5). Its text is layer-dependent; its
selection is not. That is what keeps C18's diff to one replaced call.

T-deny, T-force and T-lever stay ahead of V, for three reasons (and the
T-table pins' lever/force cells guard the order: §10.2, plant (e)):
- the escape hatch still means "the text before the forms";
- the sweep's force arm still exercises L at SIMD-on;
- cards C1-C5 re-run unchanged. Their h-arms would silently become V at
  layer "on" if V came first.

**The table's spelling [rev4, R-3].** It rides `kit_table`, as Table E
does:

```c
static const kit_table wf_spantable = { "wfS", WF_NSROWS, s_ct, NULL, NULL, s_holds, s_opt };
```

- four `gate_contract`s at U1, one per row (six at U2, with the two V rows), by a `WF_CT_S(name, row)` macro after
  `WF_CT_E`, each `{ "wfS", <row id>, NU(use_nothing), ... }` (U1 reuses the
  existing `use_nothing`, the better form): every field a wildcard (the
  rows read no `FLD_*` contract field), phase DEFINE;
- `s_opt(i)` names `"span-vector"` on T-vwin and T-vscan, NULL elsewhere.
  `walk_row` applies the opt column only when `in->s` is set
  (compose.c:172), so the walk's `gate_in` sets `.s = s` (the site): it is
  built inside `wf_plan_site`, where `s` is in hand;
- `wf_tables_check` (window.c:2388) gains the line "a span form row is a
  hole" (a NULL `ct` or `holds`), refused at `mf_art_begin` as Table E's
  is;
- `memfn/docs/trace_format.md`'s window-family paragraph gains
  `table=wfS` (the span forms, one selection per stretch, at
  `phase=define`, `site=` the define's handle; a query writes none). Like
  wfA/wfM/wfE it is NOT in the reach registry's printed tables: its reach
  is the family's (G2's floors) and the T-table pins (§10.2). "wfS" is free
  as a trace name (Table S, the stream table, is not traced). The build
  confirms `tests/memfn/rows_check.py` and `reach_equal.py` ignore wfS as
  they ignore wfE (U1).

**Where the stretches are computed: STORED ONCE [rev4, R-2, ruled].** Per
site, ONE list of stretches `{i, k, form, j}` is computed ONCE, at plan
time, after `skip` (below), and READ by both the define and the use. This
is the window family's own idiom (`wf_plan_site` stores "what the define
renders" in `w`; define and use read one stored plan, `r->wplan`). It
amends r68 F-10's wording ("the runcmp idiom", asked at define and at use)
and keeps F-10's intent, one selection with two readers that agree: the
agreement is now literal.
- **The enumerator** is today's segmentation, moved out of `wf_test_to`:
  walk the plan in offset order; skip entry `skip` and a C-run group's
  later entries (as `wf_test_to` does); at an entry `i` with `grp[i] < 0`,
  `k = wf_loop_len(w, i, skip)` at head 0 (§3.1); for k ≥ 2, walk the span
  form table once (the facts above) and store the subset `{i, k, h}` at U1 (the row's form is its head h; `form` and `j` arrive with U2's V rows); advance
  by k. Entries outside every stretch keep their lone tests, as today.
- **Where it runs:** at the end of `wf_find_prepare` (E-find), after the
  search row's `prepare` and R-1's `skip`; and, for the floor (E-generic),
  at `wf_plan_site`'s floor branch (window.c:2583, the `r == E_GENERIC`
  block that already finishes the floor's plan), with skip -1. V never
  holds at the floor (`brow` is NULL).
  [rev4.1, R71-7 (d)] The walk needs the walk's phases: `wf_find_prepare(al,
  d, w, fx, build)` gains ONE parameter, `gphases` (its `quiet` is `!build`,
  already a parameter); the floor branch has both in hand.
- **[rev4.1, R71-3, CONFIRMED by the kit manager] Why the floor call is
  NEEDED.** The floor's check row reaches `wf_loop_len`, which reads
  `w->head` at every frame (window.c:3500), and `w->head` retires at U1.
  So the floor needs each stretch's form from the stored list, or a second,
  use-side derivation (the parallel mechanism R-2 forbids). The floor
  renders stretches: T-force and T-lever loops, and T-head's loops past
  offset 64 (G2's long floor rows; at width 32 T-head renders none there).
  In R-2's words, the store-once enumerator's call in `wf_plan_site`'s
  floor branch keeps ONE selection, computed once at plan time and read by
  both the define and the use, at both frames that render stretches; it
  adds no reader and no asks (phase-1 asks are quiet), and no second
  mechanism. It extends the ruling's letter ("computed once in
  `wf_find_prepare`") to the one other frame, and matches its intent.
  `memfn/docs/trace_format.md`'s `table=wfS` hunk names floor sites as
  well as E-find sites. **Reach slots:** the trace's reach registry
  (`gate.c` `REACH_ROWS = 64`) holds 54 of 64 after wfS's six rows (36
  printed + 12 window + 6 wfS, recounted by r71's verifier).
- **`j` counts V stretches only** (ruled). With SMALLEST FORM (§3.2) at
  most one V stretch renders per site, so `j` is 0 today; the field keeps
  the name family (`vs<j>`) stable if that rule is ever lifted.
- **The trace:** the walk is traced only where the plan is built for a
  define (`wf_plan_site`'s `quiet` is 0: the `gate_tctx` takes `quiet`, as
  Table E's does); a phase-1 ask (`mf_wdecide`) writes none. So each
  stretch writes ONE `table=wfS` END at `phase=define`, at E-find and
  floor sites alike, and no use-side record exists.
- **The readers:** the use (`wf_test_to`) reads the stored list instead of
  calling `wf_loop_len` itself: at a stored stretch it renders the form
  (I: lone tests; L/H(h): lone tests below h, then `wf_loop` from h; V: the
  selector call). The define (`wf_find_define`) reads the same list to
  write `__body`, the selector and the level block for the V stretch (§5).
  `w->head` retires (its value lives in each stretch's form).

**`skip` becomes a plan fact; its producer is `wf_find_prepare` [rev4, R-1].**
Every input of `skip` is written after `plan_of`: HORS's needs `w->hl` (the
search row's `prepare`) and `w->grp` (`find_groups`); the find rows' needs
`stop_alone`. So:
- `ren_search_row` gains a column `skip`, the row's own rule (a function
  of the plan): `hors_skip` on RB_HORS (today's `d_hors_head` rule,
  `ih >= 0 && w->grp[ih] < 0 ? ih : -1` with `ih = plan_ix(w, w->hl)`) and
  `stop_skip` on RB_PAIR, RB_MEMCHR and RB_WALK (today's `find_head` rule,
  `stop_alone ? stop_ix : -1`). The column is appended to each E-find row's
  initializer; the E-stmt rows (designated initializers) leave it NULL.
- `wf_find_prepare` writes `w->skip = w->srch->skip(w)` after
  `find_groups` and `w->srch->prepare`, before the enumerator.
- `plan_of` writes `w->skip = -1` beside `w->stop_ix = -1` (its memset
  would otherwise leave 0, a REAL entry index). The floor keeps -1, and so
  does the fused B-fn row (`wf_find_prepare` returns before `find_groups`
  for it, :2466-2470).
- **The readers that move** (each reads `w->skip` instead of an argument):
  `ren_search_row.head`'s `int *skip` parameter goes (`d_hors_head`,
  `find_head`, and the four E-find rows' `head` pointers keep their
  names); `ren_check_row.test`'s `int skip` goes (`c_find_test`,
  `c_floor_test`); `wf_find_expr`'s local `int skip` goes; `wf_test_to`
  and `wf_loop_len` read the stored list and `w->skip`.

One fact, read by the head renderers, the enumerator and the test: the
general form (SEAM-7's "the entry the head proved", one search-row column).
U1's identity gate proves the lift moves no byte.

### 3.1 What k is

k is the number of entries one loop would test if L (h = 0) segmented the
plan: `wf_loop_len(w, i, w->skip)` evaluated with head 0. That is the
maximal run of consecutive core `KIT_POS_WIDE` entries from entry i, all
with one set and one table offer, starting at an offset ≥ 0, never
crossing the search-proven entry `skip` or a C-run compare. This is
exactly 710's k: `parse_span` checked that the span covers k consecutive
positions with one test (the probed position excluded). Measured: at the
default width, `[0-9a-f]{17}` has 16 tested positions plus the probe (loop
0..16), and `[0-9]{25}` has the stop plus 24 (loop 1..25) (§16 item 5).

`wf_loop_len` gains the head as a parameter (k is read with head 0; the H
rows render with their own h). Where T-head (or T-lever, T-force, T-deny)
decides, the stretch renders exactly as today: lone tests below h, a loop
from h on. So the per-stretch evaluation reproduces today's bytes for every
non-V stretch. The build proves the refactor with an identity gate (unit
U1, §14).

### 3.2 Where 710's rows generalize, and how far this note lets them

- **Several stretches in one site.** 710's patterns hold one stretch each,
  and so does every real site (§0.1). SMALLEST FORM (R-4): V renders for
  the site's FIRST eligible stretch only, and any later one falls to
  T-head (answer-identical). A second eligible stretch needs a width above
  32 (`[0-9a-f]{20}[g-z]{20}` at width 4095: two eligible stretches, k 20
  and 19), and a pin cell guards the rule (§10.2).
- **Default width.** 710 ran at `--window-search-width=4095`. At pcrec's
  default width (32) a window site holds at most 32 positions, so k ≤ 31.
  `[0-9a-f]{17}` and `[0-9]{25}` are byte-identical at both widths, so
  710's k = 16..31 cells ARE the default-width text.

### 3.3 What the rows deliberately exclude

710's harness called every non-HORS site "scan". Every scan cell it timed
was a walk on finder row R7w. The declared table's words ("skips to a
member byte") also cover memchr finds (LIBC, LIBC_BACK), PAIR and D1w.
Those were not measured.

T-vscan therefore keys on R7w alone (`scan-scope`). D1w is a walk too, but
an unmeasured default (`FB_UNMEASURED_DEFAULT`), reached when a finder deny
refuses D1: `ab[0-9]{26}` is D1 by default and D1w under
`--memfn=no-fd-d1`, k 26 (§16 item 5). Keying on the pick would let an
unrelated finder deny move a site into an unmeasured V cell. Excluded on
purpose (D77), and [rev4, R-15] a pin cell and a plant now guard the
exclusion (§10.2).

The floor (E-generic) and the legacy rows (E-func, E-stmt) have no `brow`,
so neither V row holds there.

A target admitting only `w16` (`-fmemfn-simd=x86-64`) gets the selector
calling `__body`. SSE2 has no `pshufb` for the 16-byte rung, and no `w16`
form was measured.

## 4. The form's emitted C text (708's avx2-loop, as 710 timed it)

### 4.1 Per stretch, inside the `w32` bracket

Names follow the family's `<prefix>_mf<handle>_*` rule. `j` is the V
stretch's index within the site (V stretches only, §3). `B` = 32 where
K ≥ 32, else 16.

```c
static inline __attribute__((always_inline)) int rxa_mf1_vs0__w32_b(const unsigned char *p)
{
    const __m256i x = _mm256_loadu_si256((const __m256i *)p);
    const __m256i b0 = _mm256_shuffle_epi8(_mm256_set_epi8(<lo_t, highest lane first, x2>), x);
    const __m256i b1 = _mm256_shuffle_epi8(_mm256_set_epi8(<hi_t, highest lane first, x2>), _mm256_xor_si256(x, _mm256_set1_epi8(-128)));
    const __m256i bm = _mm256_or_si256(b0, b1);
    const __m256i hn = _mm256_and_si256(_mm256_srli_epi16(x, 4), _mm256_set1_epi8(15));
    const __m256i bit = _mm256_shuffle_epi8(_mm256_set_epi8(-128, 64, 32, 16, 8, 4, 2, 1, x4), hn);
    return _mm256_movemask_epi8(_mm256_cmpeq_epi8(_mm256_and_si256(bm, bit), _mm256_setzero_si256())) == 0;
}
static inline __attribute__((always_inline)) int rxa_mf1_vs0__w32(const unsigned char *rxa_mf1_s, size_t rxa_mf1_c)
{
    const unsigned char *p = rxa_mf1_s + rxa_mf1_c + LO;
    size_t i = 0;
    for (; i + B < K; i += B) if (!rxa_mf1_vs0__w32_b(p + i)) return 0;
    return rxa_mf1_vs0__w32_b(p + (K - B));
}
```

- **Lane order.** `_mm256_set_epi8` takes the HIGHEST lane first. Each
  16-byte half of a table is written `t[15], t[14], ..., t[0]`, as the
  `bit` table already is. Written in index order, 14 of 16 test sets
  answer wrong (r68 SOUND-1; r69's index-order control: 414 of 1204
  differ). A table value > 127 is written as its signed char value.
- At B = 16 the block helper is `nib_blk`'s `sse` text: `__m128i`, `_mm_`
  names, one table copy each (`_mm_set_epi8`, highest lane first). It is
  an xmm instruction stream: at -O0 and -O2 it holds 0 `ymm` (§16 item 10).
- `lo_t[l]` = the bits `1 << h`, for the high nibbles h in 0..7 such that
  `(h << 4 | l)` is in the set. `hi_t` is the same for h in 8..15, bit
  `1 << (h - 8)` (`spike708.py` `nibble_tables`).
- The kit computes both tables in C from the stretch's 32-byte set
  (`w->set[i]`). It never reads a class name or a C-table offer (V
  stretches are C-own, §3).
- **The renderer asserts K ≥ 16** (a `kit_fail` abort, not a decline):
  §4.2's bound argument has no B below 16 (§12).

**What differs from the timed text, and why it is harmless:**
- the identifiers: renamed;
- the 710 harness's `/* blockconfirm ... */` comment: dropped;
- the `target("avx2")` and `target("ssse3")` attributes: dropped. The
  region supplies the ISA. Dropping them was machine-code identical on 6
  of 6 probes (§16 item 6);
- the base `rxa_mf1_s + rxa_mf1_c + LO` is computed in the `__w32` helper,
  not in the harness's `rxs_span`.

F2 (§6) checks all of this against 710's routed cells.

### 4.2 Over-read and boundary argument

The stretch is core. THE HOISTED BOUND (`wf_bound`: `C + chi < N`, plus
the lower half where an offset is < 0) is tested before the candidate test
on every frame. Therefore every byte `S[C + o]` with o in [LO, LO + K) lies
inside the subject. The same fact lets today's loop (`wf_loop`) read them.

The block form reads exactly [p, p + K):
- each loop trip reads [p + i, p + i + B) with i + B < K;
- the final block reads [p + K - B, p + K), and K ≥ B holds by B's choice
  (the largest of 32, 16 that is ≤ K). **This needs K ≥ 16**: below 16
  there is no B, and a B = 16 block would read below p (r68's plant at
  k 15, re-proved by r69: a fault at the start guard page, 4836 of 8730
  answers differ). T-vwin's lower bound is therefore a safety precondition
  as well as a measured bound, and the renderer asserts it.

There is no partial vector, no read past p + K and none below p, on any
path. Lanes the final block shares with the last trip are re-tested
(idempotent). The proof is the same as vany.c's OVER-READ argument, with
[pos, n) replaced by [p, p + K).

### 4.3 Answer identity

Today's text and V compute the same pure conjunction over the same bytes.
Both are side-effect-free, and every read is in bounds before either runs.
So the order of evaluation (blocks, then the overlapped tail) cannot change
the value.

The nibble test is the universal byte-set test (708's critic: correct for
any set, the empty set and the 255-byte `[^\n]` included; r68 SOUND
hand-executed it on 16 sets x 14 K; r69 EMIT built §4.1 + §5 literally on
13 real sites, 0 differences). `pshufb` zeroes a lane whose index has bit
7 set. b0 covers high nibbles 0..7, and b1 covers 8..15 through the XOR.
`bit` = `1 << (hn & 7)`. A byte is a member iff `bm & bit` ≠ 0.

### 4.4 The cascade below 32 B, restricted to what the table reaches

708's avx2-loop cascade is AVX2 32 at k ≥ 32, SSE 16 at k = 16..31, SWAR
8 at k = 8..15 and SWAR 4 below that.

T-vwin starts at k = 16 and T-vscan at k = 24, so **no row reaches a SWAR
rung**. The build emits the 32 and 16 rungs only. That removes dead text,
and with it 708's `SWAR_MAX_RANGES = 8` (an UNMEASURED DEFAULT) and its
bitmap fallback.

The 16-byte rung inside the `w32` helper is an SSSE3 instruction stream
within the x86-64-v3 region, not a `w16` level. 710's MEASUREMENT-9 notes
that its row-1 cells at k = 16..31 and its row-2 cells at k = 24..31
"measure SSE-16, not AVX2". So they measured exactly this. Every real site
(k = 31) is on this rung.

## 5. The seam shape at both layers (option A)

**At every layer**, for every V stretch:
- the walk's text holds `rxa_mf1_vs0(rxa_mf1_s, rxa_mf1_c)` where the
  stretch's chain stood;
- the E-find define (`wf_find_define`, after the run compares' word loads
  and the stream row's table) writes the functions below at file scope,
  inside the region where the target has one [rev4.1, R71-7 (c): none at
  `-fno-memfn-simd`], after the `_sh` table. It reads the V stretch from
  the stored stretch list (§3).

```c
static inline __attribute__((always_inline, unused)) int rxa_mf1_vs0__body(const unsigned char *rxa_mf1_s, size_t rxa_mf1_c)
{
    return <today's H64 text of the stretch: its lone tests, then its loop>;
}
static inline __attribute__((always_inline)) int rxa_mf1_vs0(const unsigned char *rxa_mf1_s, size_t rxa_mf1_c)
{
    return rxa_mf1_vs0__body(rxa_mf1_s, rxa_mf1_c);
}
```

- **`unused` on `__body`'s header at EVERY layer.** At w32 the selector
  calls `__w32`, which never falls back, so `__body` is an unreferenced
  static: clang `-Wall -Wextra -Werror` errors on it. The attribute is on
  the OFF line too, so the OFF and ON header lines stay identical (C18 (c)).
- **`always_inline` is load-bearing** (G-2): F2 was machine-identical 9 of
  9 with it (r68). It is why C18 needs an amendment (§10.2).

**At a target admitting `w32`:**
- §4.1's two functions are written between `simd_open(LV_X86_W32)` and
  `simd_close`, ahead of the selector, by V's own level-block writer
  (below);
- the selector's one line becomes the bracketed
  `    return rxa_mf1_vs0__w32(rxa_mf1_s, rxa_mf1_c);`, which is C18 (c)'s
  replaced call verbatim;
- **the include:** V's level block sets the level's include bit on the ART
  at define, `art->includes |= kit_level(LV_X86_W32)->includes`, exactly as
  ofsskip's `fn_level_block` does; pcrec writes `<immintrin.h>` at file
  scope ahead of the region. The window PLAN's `includes` does not gain a
  level bit;
- the site's `MEMFN_FORMS` token is `span-vector@w32`;
- `<PREFIX>_SIMD_GUARDED_BYTES` counts the bracket.

**One SELECTOR writer; V's level block stays V's own [rev4, R-4, ruled].**
- **U2 lifts `fn_selector` only.** Its body (the head; with a top rung,
  `simd_open(level)`, the call line to the top helper, `simd_close`; else
  the call line to `__body`; `"}\n\n"`) is V's selector line for line. The
  lifted writer is kit-wide (declared in `kit.h`, defined in ofsskip.c
  beside `ofs_fn_fall`, the existing export for vrun.c) and takes the
  HEAD and the ARGUMENT LIST as inputs, as two writer callbacks with a
  context (`head(ctx, name, o)`, `call(ctx, callee, o)`), plus the top
  helper's name and level (none at a layer with no rung) and `__body`'s
  name. ofsskip passes its existing `fn_head` and `fn_call_line`
  unchanged; V passes its own (the `always_inline` head and
  `(rxa_mf1_s, rxa_mf1_c)`). `fn_selector` keeps its signature as a thin
  call of the lifted writer, so `fn_define` and every reader of it stay as
  they are. ofsskip's bytes do not move (U2's identity gate over the corpus
  covers its sites, and ofsskip's w32/w16 rungs are in its x86-64-v3
  population: r69 SEAM, PROBED-AND-HELD).
- **V's level block stays V's own until vany's touch.** Reason: a
  two-function block (`__w32_b` before `__w32`, with differing heads:
  `__w32_b` takes `(p)`) is a new SHAPE that `fn_level_block` (one
  function per block, one head for every role, `render` typed to
  ofsskip's `fn_in`) cannot hold without a pre-head slot, per-role heads,
  an argument-list input and an opaque body callback, and readers
  (`ofs_fn_fits`, `ofs_fn_fall`, vrun.c) that a lift would move. V's
  writer in window.c brackets both functions (`simd_open` before
  `__w32_b`, `simd_close` after `__w32`) and sets the include bit. When
  vany is next touched, the two-function block and vany's level block are
  the second and third members of one shape, and the lift is filed as
  that ride-along (§17's rows for main).
- R-13's anchor moves for this choice: §10.2 "Re-aims at U2".

The `__body` text is today's renderer, unchanged: `wf_pos_test` and
`wf_loop` with the stretch's offsets. The H64 form at the scalar layer is
kept, moved into a function.

**The guarded bound.** One stretch's bracket is constant per (B, set) apart
from three decimals: about 1.3 KB at B = 32 (r69's hand-built V: the
inserted text, stamps aside, is 1747-1766 bytes at B = 16 and 1966-1994 at
B = 32, block plus `__w32` plus the replaced call: §16 item 10). V renders
at most once per site (§3.2), so this is a fixed bound, not a cap with a
decline path. `guarded_max` is the largest instance plus a small headroom,
CHOSEN and labelled so. It gets a row `span-vector-w32` in
`tests/memfn/simd_bounds.tsv`, and a `limits.md` §8.3¶3 sentence names it.

## 6. MEASUREMENT-3: how the shipped text is matched to the timed text

| step | how | what it closes |
|---|---|---|
| **F2, machine-code fidelity** (a delivery check, run once by the build lane and recorded in its report; not a committed test) | **population: the 82 cells of 710's grid the table routes** (6 window classes x 11 k in 16..1000 = 66, and 4 scan classes x 4 k in 24..64 = 16; `confirm.py` `CLASSES`, `SITE_EXPECT`, `KS_OLD` + `KS_NEW`). The build lane re-counts the routed set from the SHIPPED build by §10.1's k source and reports any cell where the two counts disagree. For each: `objdump -d` of `rxa_search`, addresses normalized, the shipped `-fmemfn-simd=x86-64-v3` artifact at width 4095 against 710's `work/src/<pat>.avx2-loop.c`, same gcc and flags | the inlined machine code is what was timed. r68 matched 9 of 9. **Landing rule, before data:** any DIFFERS on a routed cell is listed with its diff, enters C6's population, and blocks the landing until the code round rules it |
| **F3, timing** | card C6 (§8) times the SHIPPED compile (default vs `no-span-vector`, both from one binary) | what F2 cannot see: layout, I-cache, and the shipped trade at SIMD-on |

## 7. The deny row

Proposal for the build lane to take:

```
MF_OPT("span-vector", MF_OPT_DENY, MF_B_ANY, MF_L_SCALAR,
       "long window spans of one byte set are tested by a function that, under -fmemfn-simd at a "
       "target with 32-byte vectors, tests 32 (or 16) bytes per step; denied, the span is tested "
       "inline as before, at every setting")
```

- **The name.** It says what the caller sees (D174): a span tested by
  vector. The `span-` prefix groups it with `span-loop`.
- **The layer is `scalar`** on purpose, under option A. The deny is LIVE
  at both settings (`wrap-deny`): it un-wraps the stretch too, so
  `--memfn=no-span-vector` restores main's bytes exactly at every layer and
  target. It is the wrapper's escape hatch and its control.
- **What is on by default.** The VECTOR HELPER is off by default, because
  `-fmemfn-simd` is OFF by default and the helper renders only at a `w32`
  target. The WRAPPER and its deny are live in the default build: every
  eligible stretch is wrapped at `-fno-memfn-simd` (D201 add. 3 (a)'s
  amended Consequences line says the same).
- **Spec:** `registry.md` §6¶8a gains the row. §6¶8b's `memfn` section
  floor goes from 14 to 15.
- [rev4, R-20] **`make test-axes`:** `tests/axes/memfn_arm.py` requires
  every `--list-axes` memfn row in `MEMFN_CLASS`, so the row lands with its
  classification in the same unit (§9.3).

## 8. The measurement card (same change; Frank 2026-10-23)

**Card C6 `span_vector`** in `memfn/tests/span_forms/cards.py`, and the
append-only row `kit span_vector 8 form;pat;regime;layer ratio cards.py C6
...` in `memfn/data/cards/kit-grid.tsv` (`kit-grid@8`). The row is visibly
UNMEASURED until a box runs it.

Written before data:
- **What it measures: the SHIPPED trade.** On ONE binary, at
  `-fmemfn-simd=x86-64-v3`: `V` (default) and `H64@on`
  (`--memfn=no-span-vector`). The deny changes the wrapper, the body and
  the TU (`<immintrin.h>`, stamps) together; C6 times that combination on
  purpose, because G-3 is about what the caller gets.
- **Patterns, each with its width stated:**
  - the 3 real sites (§0.1), width 32;
  - window k 16 and 31 at width 32; k 32 and 1000 at width 4095;
  - scan k 24 at width 32; k 64 at width 4095;
  - every F2 DIFFERS pattern, at width 4095.
  The outside-bound cells (window k 15, 1001; scan k 23, 65) are CUT: both
  arms render today's bytes there, so they are A/A by construction (the
  T-table pins check the flip in text, §10.2).
- **Regimes.** The cards' six regimes, plus near-miss-in at the window
  sites.
- **Which clauses of 710's rule apply.** The cell rule (FLOOR = max(0.15,
  spread(A), spread(B)); WIN / LOSS / TIE), the re-time, the N/A rule, the
  CPU-quiet control: apply unchanged. The CONTROL clause (Hspk) does not
  apply (Hspk's one-level wrapper is not the shipped shape, §2). The S
  (busy) clause is dropped; no profile arm is declared.
- **What replaces the A/A line:** an A/A arm, the `no-span-vector` exe
  timed as both arms on each C6 pattern; its repeated-LOSS-or-WIN rate is
  printed beside the verdict.
- **The rule's sha** is recorded with the result.
- **`deps`.** `kit:form.span-vector=<hash>`: a NEW formhash SHAPE (a window
  site with one stretch of a stated set and K), its renderer, and one entry
  (the canonical instance: the hex set, K 40, x86-64-v3), so a later text
  change stales the row.

**What it settles, and the every-box rule [rev4, R-31].** G-3 on the
shipped text, box by box. **V lands behind the OFF switch (as every SIMD
level does) and is labelled CANDIDATE until C6 has run on each bench box
that runs it** (Zen 4 here; Zen 1, ubuntubudu, AVX2 split into 2x128, via
main: D144 addendum 4). **A repeated LOSS on any box blocks the level**
(D155 item 2), not merely a bound. A re-measure may RAISE a lower bound,
never below the safety floor 16 (§12). The SIMD-off wrapper is not timed
anywhere (r68 F-14): U2b's census is its record.

Rows for main to file in plan.md (§17), NOT build scope: a
`--harness=span-vector=force` lever (V outside the bounds) and a
`span-vector-body` lever (the wrapper alone at SIMD-on); trigger: a bound
is questioned by a C6 or Zen 1 run.

## 9. The same-commit abi package (D76/D94, D146/D147)

### 9.1 The bump

"The next number at landing" (`docs/design/CLAUDE.md`): main is at **109**
today (§16 item 1, re-checked at `d255d94a3`). Lane L3 is taking 109 → 110,
so this build is likely **111**. The build lane re-greps at its landing
base.

### 9.2 The re-pins, readers found by grep at the landing base

The command: `git grep -n -w <N> -- src tests docs/spec docs/testing.md
memfn`, and **review every hit by hand, unfiltered** (215 hits at 109 on
lane/bspan4's base, §16 item 1). A filter such as `| grep -i abi` drops a
reader: `match_api.md` §6¶17 ("It is `109` on every artifact pcrec emits
today") does not say "abi" on its line (the D94 failure mode). The readers
among the hits:
- `src/gen/emit_dfa.c` `PCREC_ARTIFACT_ABI`;
- `docs/spec/match_api.md` §1's K80 guard, its three lines (`!= N`, the
  `#error` text, `#define PCREC_RX_ABI_H N`);
- `match_api.md` §6's `abi` table row, and §6¶17's sentence;
- `tests/codegen/run_codegen_tests.sh` `ABI_EXPECT`;
- `tests/mech/sabotages/S693_abi_not_bumped.sh` `SAB_BEFORE`, re-aimed;
- `tests/codegen/run_recursion_identity.sh` FILEPIN/ABASEPIN, the (B) pin,
  self-pinned to the lane's last src commit;
- `docs/dev/history/abi_changelog.md`.

[rev4, R-12 drill] A word grep cannot see the subst support symbols'
`_v<N>` suffix (`pcrec_subst_flatten_v109`: no word boundary before the
digits). No tree reader spells it (`git grep -n 'v109'` over the same
paths finds none), so the reader list stands; the identity gate's mask
covers it (§10.2).

Then run the suites that count: registry, codegen, rxtsource (the D94
addendum).

### 9.3 Stamps, pins and the axes row [rev4, R-20]

- `MEMFN_FORMS` gains the token `span-vector@w32` (opaque to pcrec).
- `SIMD_GUARDED_BYTES` rises on SIMD-on movers.
- `simd_bounds.tsv` gains the row `span-vector-w32`.
- **`MEMFN_CLASS`** (`tests/axes/memfn_arm.py`) gains, as ruled,
  `("span-vector", "default")` and `("span-vector", "simd")`: class
  DIFFER, [rev4.1, R71-2, ruled] corpus floors PINNED AT THE MEASURE at U2
  per (encoding, stream), witnesses the 3
  bench texts (`[0-9a-f]{32}`, `\b[0-9a-f]{32}\b`, `\d{32}`) at byte and
  utf8 on `c-default` (witness-only patterns, as `span-loop=force`'s
  `[0-9a-f]{32}`), both layers, because the deny is live at SIMD-off too
  (the wrapper). ASSERT_ZERO would be false. [rev4.1, R71-2] The REAL
  corpus's count is 0 (§0.1); with SPAN-SEED's `.rxt` in the corpus the
  measured count is about 28 (byte) and 20 (utf8) on `c-default` and 0 on
  `c-vm` (no window walk on the VM engine), and U2 pins each floor at that
  measure (K35; §15 Q4, resolved). U2 can: `memfn_arm.py`'s floor counts
  DIFFER patterns in `enumerate_corpus`, every `.rxt` under `tests/`, so
  the `.rxt` U1 commits is counted at U2. U3 moves no pattern into or out
  of DIFFER, so the U2 pin holds at U3; under any arm that takes sets out
  of V (§2.2), re-measure.
- **The `.rxt` moves existing `MEMFN_CLASS` rows** (it puts V sites into
  the corpus): `("span-loop", *)` is ASSERT_ZERO today and becomes DIFFER
  (at a V site `no-span-loop` is T-deny's I, all inline, while the default
  is the wrapper), and `("span-loop=force", *)`'s floors (14 per encoding)
  rise. The build lane re-measures both at the unit that first holds V and
  the `.rxt` together (U2) and pins at the measure.
- `emit_sweep.py`'s `DIFFER_PINS` gains floors for the deny arm at both
  layers over the corpus (the `.rxt` included).
- The `.rxt` itself, at U1 (§10.1), moves the corpus-population pins the
  BOILERPLATE delivery bar lists: the rxtsource census, the start-set mover
  manifests (`tests/startset/manifests/`), the axes allowances, the size
  tripwires and the corpus case counts. Found by `make test` at U1, not by
  this list. [rev4.1, R71-5] One more, sample-dependent: the `.rxt`'s 41
  patterns shift `simd_guarded_check.py`'s every-10th corpus sample
  (`run_simd_guarded.sh`), which moves its `simd-form` floor (pinned at
  the measure).

`MF_SITE_ABI`: unchanged, since the site carries no new field.
`MF_CLASS_V`: unchanged, because the level include bit rides the ART
(ofsskip's idiom, §5), not the window plan class. The trace build's
asked-vs-defined `includes` comparison is the check that the plan class did
not move.

### 9.4 G1 alpha (integration.md §17.2) [rev4, R-28]

- **Population.** pcrec-side: a script diffs each artifact's default
  compile against its `--memfn=no-span-vector` compile, over the corpus and
  the bench patterns (integration.md §17.2's definition), at
  `-fno-memfn-simd` AND at `-fmemfn-simd`. It never reads the kit's
  `moved`. The manifest is written before any timing, with its count.
- **Bins** (op, length decade), floor 8, count **real movers only**: the
  corpus less `tests/memfn/span_seed.rxt` (excluded by path), plus the
  bench. SPAN-SEED is printed SEPARATELY as G1's floor witness (its 28 V
  sites at width 32 must appear as movers, so the manifest is not
  empty-blind, K35).
- **No timing window is booked.** The real population is 3 movers, so
  every bin is UNREACHED at both layers. The build delivers the manifest
  and the dry run (counts printed, UNREACHED printed). Trigger to time: a
  bin reaches 8 real movers (the default width rises, or real patterns
  land in range): a row for main (§17).
- D147's "both layers" reading is met at SIMD-on by C6 and at SIMD-off by
  U2b's census where the code is identical; where it differs, see §2.2
  arm 1.

### 9.5 The spec hunk, the same change (D80)

| file and section | change |
|---|---|
| `registry.md` §6¶8a, ¶8b | the row; the floor 14 → 15 |
| `tuning.md` §2.43¶3a | "What On renders" gains the vector span |
| `tuning.md` §2.43¶3b | its switch |
| `tuning.md` §2.43¶3d | the window search's denies: the wrapper at both settings, under A |
| `limits.md` §8.3¶3 | the per-form bound |
| `match_api.md` §1 (the K80 guard's three lines), §6 (the `abi` row), §6¶17 | through the abi ritual |

`docs/guide/` points at the spec and does not restate it. The kit's own
doc hunk: `memfn/docs/trace_format.md` (`table=wfS`, §3).

## 10. G2 and the checks (each control independent of the generator)

### 10.1 SPAN-SEED: a committed `.rxt`, and how each check reads it [rev4, R-20, R-19, ruled]

**The file.** `tests/memfn/span_seed.rxt`, with its generator
`tests/memfn/gen_span_seed.py` beside it, committed at **U1** (it moves no
artifact byte before U2, and every later unit's gate then reads the
committed file). `tests/harness/run.sh` runs every `*.rxt` under `tests/`
(`rxt_format.md` §6.1¶1), so `make test-corpus` and `make test-axes` pick
it up with no registration. `tests/memfn/CLAUDE.md` gains its line.

**Its patterns: the SPAN-SEED list, 41 distinct, in three blocks** (one
`#` comment header each):
- the 3 bench patterns (§0.1);
- the 11 T-table pin patterns (§10.2);
- a slice of 710's grid: each of the ten classes at `cls{17}`,
  `cls{25}`, `cls{32}`, 30 patterns;
- less 3 that coincide (`[0-9a-f]{17}`, `[0-9]{25}`, `[0-9a-f]{32}` are in
  two blocks; each is written once, in its first block).

**Its cases, per pattern** (`m`, `n`, `mc` lines, `rxt_format.md` §1.5,
§1.7; byte encoding, no `flags`): with n the pattern's repeat count, M a
member string of the class, X a byte outside it (`\n` for `[^\n]`, `g` or `!`
otherwise (`g` for `[\x80-\xbf]`), written with the `<subject>` escapes,
§1.5.1):
- a match at the subject start, and a match flush against the subject end
  after a non-member prefix;
- **the failing-index staircase** (710's FIDELITY-1) on every pattern of
  at most 33 positions (the default-width V sites): for each position
  i in 0..n-1, the n-member subject with position i replaced by X, as an
  `n` case (or as the `m` of a later window where the subject continues);
  a 1001-position pattern gets the staircase at the positions 0, 15, 16,
  31, 32, 63, 64, 999 and n-1 (the rung edges);
- one subject one byte short (`n`), the empty subject (`n`);
- an `mc` find-all count on two back-to-back matches followed by a
  near-miss;
- for `\b[0-9a-f]{32}\b`, the boundary cases (a word byte before and
  after the 32, as `n`).
That is about 950 cases (28 short V patterns at about 30 each, 13 others
at about 8). Under the harness's utf8 axis (`run_axes.sh`'s encodings) the
`[\x80-\xbf]` block is byte-only: the generator writes that block with the
encoding directive the harness's existing byte-only corpus files use, and
the build lane confirms the convention by grep before writing it.

**The oracle:** python3 `re` at authoring, by the generator (bytes
patterns, `re.ASCII`), and `tests/harness/verify_rxt.py` over the
committed file (`rxt_format.md` §3), as every corpus file. The generator
writes the file; the committed file is the record (a hand edit is a
re-run, not an edit).

**Its counts, derived by the table's predicate (§16 item 5):** at width 32,
**28 V sites** (the slice's 26: 6 window classes x 3 + 4 scan classes x 2,
plus the bench's `\b[0-9a-f]{32}\b` and `\d{32}`; the bench's
`[0-9a-f]{32}` coincides with the slice); at width 4095, **31** (the 28
plus `[0-9a-f]{1001}`, `[0-9]{65}` and `[0-9a-f]{20}[g-z]{20}`'s first
stretch). Under `-e utf8`: 20 and 21 (the hex and `[a-f]`/`[aeiou]` sets
become R7w and leave V below `{25}`; `[^\n]` becomes E-stmt; §11). The
floors **read the committed file and say so** (each check names
`tests/memfn/span_seed.rxt` as the source of its SPAN-SEED patterns, via
`pcrec --list-source`, never a copied list).

**The k source [rev4, R-19].** No trace record carries k. Every check that
counts V sites counts them INDEPENDENTLY of the kit's table: the finder row
from the traced build's `MFTRACE FDROUTE ... row=R frame=F` record
(`tests/memfn/mk_mftrace_lib.sh`'s library, as G2's rows half links), k
from the head-0 lever compile's loop text (`pcrec-harness
--harness=span-head=0`: `rxa_mf1_j = LO; for (; rxa_mf1_j < END`, k = END
- LO), C-own read off the loop's test (no table name), and the predicate
(D-hors 16..1000, R7w 24..64, frame E-find, first eligible stretch per
site) applied IN THE CHECK. Drilled: 28 at width 32 and 31 at 4095,
exactly the floors (§16 item 5). Where the shipped text also shows the
kit's own answer (the count of `vs<j>(` calls), the check prints both and
fails on a disagreement.

**The wiring, per check** (which file, which flag):

| check | how it reads SPAN-SEED |
|---|---|
| answer identity, default build (G-1) | `make test-corpus`: the `.rxt`'s oracle-verified cases, at the default width 32 and `-fno-memfn-simd` (the wrapped V at 28 sites) |
| the deny arm's answer identity, both layers (G-1) | `make test-axes`: `run_axes.sh` runs the corpus (the `.rxt` included, with its subjects) under every memfn arm, the `span-vector` deny included, at its default and simd (x86-64-v3) layers; `memfn_arm.py`'s `MEMFN_CLASS` row classifies the deny (§9.3) |
| the identity gate (G-4) | its corpus enumeration (`emit_sweep.enumerate_corpus`) includes the `.rxt` at width 32; it ALSO compiles the `.rxt`'s 41 patterns (`pcrec --list-source`) at `--window-search-width=4095`; prints its V-site count by the k source above, floored 28 / 31 |
| C18 / simdfloor | its corpus population includes the `.rxt`; its `NAMED` list gains the THREE span witnesses (§10.2) [rev4.1, R71-1: rev 4 said two here] with their floor, NAMED at x86-64-v3 ONLY (a per-target column on `NAMED`: x86-64 renders no V mover, so a span witness there prints "NOT a mover" on correct text); `FLOORS` for x86-64-v3 rise by the `.rxt`'s V sites at the default engine (re-pinned at the measure, U4); x86-64 does not move (the selector calls `__body` there, no mover) |
| `DIFFER_PINS` (`scripts/emit_sweep.py`, a hand-run tier) | floors over the corpus, the `.rxt` included, both layers |
| G1's population (§9.4) | EXCLUDES the `.rxt` from its bins by path; prints its V count separately as the floor witness |
| the T-table pins (§10.2) | do NOT read SPAN-SEED: their own literal cell list |

### 10.2 The checks

| check | subject | control (shares no source with the kit) | population count (K35) |
|---|---|---|---|
| **G2-V unit** (new section of `run_g2_win.sh`, x86-64-v3 arts) | every V rendering over a generated space: sets of 1..8 ranges in both polarities, sets with bytes ≥ 0x80, the empty set, a 255-member set, single-byte-removed sets; k at every rung edge (16, 17, 31, 32, 33, 63, 64, 65, 999, 1000) and random interior k | python: `all(re.fullmatch(cls, bytes([b])) for b in window)` with the class written in the TEST, never the kit's set. Windows flush against a `PROT_NONE` page at both ends | per rung, per row: literal floors |
| **G2-V whole** [rev4, R-14] | `cls{k+1}` and mixed patterns (a literal run plus a stretch, two stretches, a stretch beside a non-core position) compiled at SIMD-on and SIMD-off, find-all, at widths 32 and 4095 | python `re` over the cards' regimes, plus forced near-miss staircases (a failing index at each of 0..k-1, at the first window and after a match), **with every subject flush against a `PROT_NONE` page at BOTH ends** | per site kind: literal floors, counted by §10.1's k source |
| **T-table pins** [rev4, R-14, R-15, R-16] | the row bounds, the brow column, the order (T-lever, T-force ahead of V) and once-per-site | a literal CELL list in the test, each with its width and flags, read off the rendered text: the count of selector calls `<p>_mf<h>_vs<j>(` in the walk and, at x86-64-v3, the count of `__w32(` calls in the selectors; never off window.c. Every cell's finder row and k checked by the trace (§10.1's k source) | **20 cells over 11 patterns** (below), every one reached (drilled, §16 item 5) |
| **Identity gate** (G-4) [rev4, R-12] | `--memfn=no-span-vector` artifact on the U2 binary vs the artifact of the lane's MERGE BASE, built once (never "main", which moves); **both arms compiled with the same `-o` basename** in two directories | byte diff of `.c` AND `.h`, both layers, over the corpus (the `.rxt` included) and SPAN-SEED's patterns at 4095. **Mask, declared before data: nine anchored spellings (below), each replacing ONLY its number group.** Nothing else is masked | count printed; 0 differences expected |
| **C18 / simdfloor, AMENDED** | split across U3 and U4 [rev4.1, R71-4] (below) | its own rules, with their own controls | its per-target SIMD FUNC floor rises, plus the NAMED span witnesses' literal floor |
| **F2** (delivery check) | §6 | 710's arm sources | 82 routed cells |

**The T-table pin cells [rev4]** (20; x86-64-v3 unless the cell says
both layers; [rev4.1, R71-6] "present" = 1 selector CALL SITE and 1
`__w32` CALL, "absent" = 0 of each, counted by these spellings (the
definition heads match a bare `vs0(` / `__w32(`, which reads 2/2 on a
whole-text count): the call `rxa_mf1_vs\d+\(rxa_mf1_s, rxa_mf1_c\)` in the
walk, and `__w32(rxa_mf1_s, rxa_mf1_c)` in the selector):

| # | cell | width | expect | what it guards |
|---|---|---|---|---|
| 1-4 | `[0-9a-f]{16}` / `{17}` | 32, 4095 | absent (k 15) / present (k 16) | T-vwin's lower bound, both widths |
| 5-6 | `[0-9a-f]{1001}` / `{1002}` | 4095 | present (k 1000) / absent (k 1001) | T-vwin's upper bound |
| 7-10 | `[0-9]{24}` / `{25}` | 32, 4095 | absent (k 23) / present (k 24) | T-vscan's lower bound |
| 11-12 | `[0-9]{65}` / `{66}` | 4095 | present (k 64) / absent (k 65) | T-vscan's upper bound |
| 13 | `ab[0-9]{26}` | 32 | absent (D1, k 26) | brow: a memchr find |
| 14 | `[xy][0-9]{26}` | 32 | absent (PAIR, k 26) | brow: PAIR |
| 15 | `ab[0-9]{26}` `--memfn=no-fd-d1` | 32 | absent (D1w, k 26) | [R-15] brow: D1w, F-4's own fix (the only cell that separates "brow R7w" from "pick WALK") |
| 16 | `[0-9a-f]{20}[g-z]{20}` | 4095 | exactly one selector call (stretches k 20 and 19, both eligible) | once per site |
| 17-18 | `[0-9a-f]{17}` `--harness=span-head=8` (pcrec-harness) | 32, both layers | 0 selector calls | [R-14] T-lever ahead of V |
| 19-20 | `[0-9a-f]{17}` `--memfn=span-loop` | 32, both layers | 0 selector calls | [R-14] T-force ahead of V |

The frame cell `[0-9a-f]{20}[g-z]{20}` at width 32 is gone with the frame
column (R-15). The pin floor counts CELLS (20), not patterns (11).

**The identity gate's declared mask [rev4, R-12; drilled, §16 item 11].**
Matched per line over the `.c` and the `.h`; `N` is the group replaced:

| # | spelling (anchored regex) | where |
|---|---|---|
| M1 | `^/\* Generated by pcrec \S+ \(abi (N)\)\. ` | line 1 of the `.c` and the `.h` |
| M2 | `^    \.abi = (N),$` | the `.c`'s `rx_info` initializer (emit_dfa.c:3233; subst: emit_subst.c) |
| M3 | `^#if defined\(PCREC_RX_ABI_H\) && \(PCREC_RX_ABI_H \+ 0\) != (N)$` | the `.h` guard |
| M4 | `^#error "pcrec: this artifact \(abi (N)\) shares a translation unit ` | the `.h` guard |
| M5 | `^#define PCREC_RX_ABI_H (N)$` | the `.h` guard |
| M6 | `^#if !defined\(PCREC_RX_ABI_H\) \|\| \(PCREC_RX_ABI_H \+ 0\) != (N)$` | a subst artifact's `.h` |
| M7 | `^#error "pcrec: this subst code \(abi (N)\) needs the rx shared block of abi (N); ` | a subst artifact's `.h` (two groups) |
| M8 | `^#define PCREC_SUBST_H (N)$` | a subst artifact's `.h` |
| M9 | `^#define (pcrec_subst_\w+) \1_v(N)$` | a subst artifact's `.h` and the support unit (the `_v<N>` symbol suffixes) |

M6-M9 apply only where the gate's population holds subst or support
artifacts; declaring them costs nothing and keeps the mask closed under
the abi ritual. A memfn deny stamps nothing else (r69 CHECK-1, held).

**Out of the mask on purpose: the support unit's id** (drilled, §16 item
11). `--emit-support`'s unit also carries `PCREC_SUPPORT_DEF const
unsigned long long pcrec_subst_support_id = 0x...ull;`, a HASH that moves
with the abi but is not a spelling of N. The gate's population is
per-pattern artifacts (the corpus and SPAN-SEED), which never include the
support unit, so the gate does not compile it, and the mask does not
cover it. A gate that adds the support unit must mask that line as a
tenth, declared row (`^PCREC_SUPPORT_DEF const unsigned long long
pcrec_subst_support_id = (0x[0-9a-f]+)ull;$`); it is not declared here,
because no population reaches it (D77).

**The C18 amendment [rev4, R-7..R-11; drilled at B = 16 and B = 32, §16
item 10].** C18's regexes (`tests/memfn/simd_floor_check.py` `SELECTOR`,
`HELPER`) match only `static inline size_t ...`, while V spells `static
inline __attribute__((always_inline)) int ...` (and `__body` adds
`unused`). Its -O0 leg (C9-x86) requires `<fn>__w<VW>` as a defined
symbol in the -O0 object, and an `always_inline` static is never emitted
there. The amendment, with its controls (learnings §3). [rev4.1, R71-4]
**Which unit:** U3 first emits V movers, and `test-memfn-simdfloor` is in
`TEST_SECTIONS`, so the unamended `text_legs` read U3's correct V text RED
("(c) a deleted line that is no SIMD FUNC's floor call", "a mover with no
SIMD FUNC selector"). So the head family (both regexes), the `_b` name
form and the -O0 rule with control (1) land IN U3; NAMED, the floors, the
routing leg (not red at U3) and controls (2)-(4) stay in U4. (Lesson: a
unit order is a check order; an amendment lands in the first unit whose
output the old check reads wrongly.)
- **the head family:** `SELECTOR` and `HELPER` accept `static inline`,
  then an optional `__attribute__((...))` naming `always_inline` and/or
  `unused`, then `size_t` or `int`;
- **the name form [R-10]:** `HELPER` is `(\w+)__w(\d+)(?:_b)?\(`, so the
  block helper `<fn>__w32_b` IS a helper for the exclusivity lint (drilled:
  both `__w32_b` and `__w32` found on every witness);
- **the -O0 rule for a selector whose own head says `always_inline`
  [R-7, R-8]:** the path is fixed by the SELECTOR's head, never by the
  helper's. On that path, in the -O0 object: (1) NO symbol of the
  selector's family (`<fn>`, `<fn>__*`) is defined (`nm`), and (2) the
  function that calls the selector (`rxa_search`) holds at least one
  `pshufb` (`pshufb` or `vpshufb`, xmm or ymm). No register-width reading:
  the B = 16 rung is xmm only. A selector whose head is ofsskip's (no
  attribute) keeps today's `nm` leg unchanged. Drilled: every correct text
  passes at B = 16 (`[0-9a-f]{17}`, `[0-9]{25}`, `[0-9a-f]{32}`: 0 family
  symbols, 6 `pshufb`, 0 `ymm`) and at B = 32 (`[0-9a-f]{41}` and
  `[0-9a-f]{1001}` at 4095: 0 family symbols, 6 `pshufb`, 188 `ymm`);
- **[R-9] no "compile succeeds" leg with a control.** The bracket writes no
  text (a byte count) and the ISA region is file-wide, which C18's
  PLACEMENT lint already requires of every body. So `__w32` outside the
  bracket is caught by leg (c)'s byte count (inserted bytes ≠
  `SIMD_GUARDED_BYTES`), and a helper outside the region by the placement
  lint (and every compile). The -O0 compile is still run (the rule needs
  its object); it has no plant of its own;
- **[R-11] the routing leg:** `tests/memfn/routing_shape.py` (C18 (d),
  C11) gains V: the FUNC population adds the NAME rule `_mf\d+_vs\d+$`,
  and the head family `static inline __attribute__((always_inline[,
  unused])) int <fn>(const unsigned char *<s>, size_t <c>)`, read with the
  forwarded argument list `<s>, <c>`; the rule itself (routed, one call
  forwarding the parameters, the helper defined above, no `#if` in a work
  body) is today's code. Its `--selftest` gains V shapes: routed (OFF), one
  call to its level (ON), and five that must be red (selector does work,
  drops a parameter, helper below, level not defined above, unrouted).
  Drilled: 7 of 7 controls as expected; on the hand-built OFF and ON texts
  the V leg counts 1 FUNC each and no violation, where today's
  `routing_shape.check` counts 0 (§16 item 10). `run_g2_simd.py`'s HELPER
  (G2's ofsskip family) is out of scope: it reads no V text;
- **NAMED span witnesses** in C18's population: `[0-9a-f]{17}` (HORS,
  k 16, B 16) and `[0-9]{25}` (R7w, k 24, B 16), plus `[0-9a-f]{41}` at
  width 4095 (HORS, k 40, B 32), the one B = 32 witness; each with one
  `vs0` selector at x86-64-v3; literal floor: 3 span SIMD FUNCs, written
  before the build. [rev4.1, R71-1] `simd_floor_check.py` checks every
  NAMED witness on every `FLOORS` target (x86-64 and x86-64-v3), and
  x86-64 renders no V mover (§11), so these three carry a per-target
  column on `NAMED`: x86-64-v3 only;
- **controls**, each a mech row with a REACH witness, each rejected by the
  leg it names: (1) drop `always_inline` from `__w32`: the -O0 rule is red
  (the symbol `<fn>__w32` appears and `rxa_search`'s `pshufb` count falls
  to 0; drilled on all three witnesses); (2) write `__w32` outside the
  bracket: leg (c)'s byte count; (3) name a non-admitted level: the
  exclusivity lint (now that `HELPER` sees the name); (4) a V selector
  that does work: the routing leg.

**Sabotage rows** (mech, each with a REACH witness, [MECH-REACH]):

| plant | what it breaks | caught by |
|---|---|---|
| (a) | a nibble table drops a member (708 `nib_drop`) | G2-V unit |
| (b) [rev4, R-14] | the final block reads 1 B past (708 `past`). Witness: a **WALK** whose stretch ends at the pattern end, subject flush at the end (`[0-9]{25}`; r69: SEGV, 6855 of 13546 answers differ). On HORS the byte past the stretch is the probe, in bounds, so the plant is benign there | **G2-V whole**, its end guard page |
| (c) | T-vwin's lower bound becomes 15 | T-table pins cells 1-2, the renderer's K ≥ 16 assert, G2-V whole's start guard page and staircase |
| (d) | the deny is ignored at SIMD-off | identity gate, over the corpus with the `.rxt` (28 V sites at width 32) |
| (e) [rev4, R-14] | V evaluated before T-lever / T-force | **T-table pin cells 17-20** (lever and force on `[0-9a-f]{17}`, both layers: the plant puts a selector call there). Witness reached: D-hors, k 16 (§16 item 5) |
| (f) [rev4, R-15] | T-vscan keyed on pick `FF_WALK` instead of brow R7w (rev 2's key) | **T-table pin cell 15** (`ab[0-9]{26} --memfn=no-fd-d1`: D1w, k 26, gains a selector call). Witness reached (§16 item 5) |

No plant guards R-5's `own` condition: no pcrec site reaches it (every
eligible loop in the census is C-own, §16 item 5), and G2's generator
declares its tables at file scope, so G2 could not see it either. Its
population (0) is printed by the k-source census (K35).

**Re-aims, by the anchor map over EVERY function each unit moves [rev4,
R-13; lesson r69-2; §16 item 13].** The map: every mech row whose
`SAB_FILE` is under `memfn/src/`, or is a file a unit edits, with its
`SAB_BEFORE` located and attributed to its enclosing function.

- **At U1** (window.c: `wf_span_head` retires; `plan_of`, `wf_loop_len`,
  `wf_test_to`, `d_hors_head`, `find_head`, `wf_find_prepare`,
  `wf_find_expr`, `c_find_test`, `c_floor_test`, `wf_test`,
  `wf_plan_site`, `wf_tables_check`, `ren_search_row` and its table, the
  new enumerator and table): **re-aim** S3278 (force ignored), S3279 and
  S3282 (the lever ignored / read as 0), S3281 (deny ignored), all
  anchored in `wf_span_head`, onto T-force, T-lever and T-deny; **re-aim**
  S3280 (`if (w->off[i] < w->head) return 0;` in `wf_loop_len`; `w->head`
  retires) onto the head parameter; **re-check** S3277 (stays in
  `wf_loop_len`, whose meaning changes: k at head 0). **Re-prove REACH**
  (anchors unchanged, reached by the new path): S3276, S3283, S3284
  (`wf_loop`), S3285 (`enum { WF_SPAN_HEAD = 64 };` stays: T-head's form
  reads it), S2982 (the RB_PAIR initializer's first line; the `skip`
  column is appended to the row's last line). No anchor sits in the other
  functions listed.
- **At U2** (ofsskip.c: `fn_selector` becomes a thin call of the lifted
  writer; window.c: `wf_find_define`, the use; options.def: an appended
  row; `memfn_arm.py`): **re-aim** S730 (its `simd_open` / `fn_call_line`
  / `simd_close` lines move into the lifted writer), its REACH re-proved
  on its ofsskip witness, and a V witness added (the writer is shared, so
  the plant now also reaches V's selector); **re-prove REACH** S690, S694
  (`fn_call_line`, unchanged text, now reached through the writer's call
  callback). NOT moved, by R-4's choice: S724, S2995, S3001, S3002
  (`fn_level_block`, untouched) and S687, S691, S692, S695, S728
  (`fn_define`, untouched; S695's AFTER calls `fn_selector` with its kept
  signature).
- **At U5** (formhash.c: a new shape, renderer and entry): **re-check**
  S2930 (anchored in the entries table) and S2933 (`mf_form_hash`): moved
  only if the entry struct gains a field or the hash's dispatch changes.
  [rev4.1, R71-7 (b)] **Re-check** S2931 (`kit-grid.tsv`, unchanged by an
  append).
- **At U6:** S693 (`#define PCREC_ARTIFACT_ABI`), re-aimed by the abi
  ritual (§9.2).
- **Conditional** (re-check only if the unit edits those lines): G2's
  generator rows S3289, S3300, S3301, S3304, S3310, S3311, S3320
  (`memfn/tests/g2/g2_win_gen.c`, if G2-V edits the head pins or long-row
  counters); S1047, S1048 (`scripts/emit_sweep.py`'s composition floors,
  if the `DIFFER_PINS` edit touches that dict line).

`REACH_ONLY=1 bash tests/mech/run_sabotage_matrix.sh` runs at U1, at U2 and
before delivery, since a new row fires in new places (BOILERPLATE).

## 11. Expected movers (which sites' bytes change) [rev4, R-22]

**The moves follow the finder row**, not the class: a stretch moves where
its site is E-find with brow D-hors and 16 ≤ k, or brow R7w and 24 ≤ k
(and k within the width). The examples below are byte encoding. Under
`-e utf8` the finder row changes for some sets (§16 item 5, utf8 census):
`[0-9a-f]`, `[a-f]` and `[aeiou]` become R7w, so they move only at
`{25}`..`{32}` there; `[^\n]{17}`..`{32}` become E-stmt and never move;
`[A-Za-z0-9_-]` and `\w` stay D-hors and move from `{17}`.

| setting | moves | does not move |
|---|---|---|
| every artifact | the abi number lines | — |
| `-fno-memfn-simd` (the default build), default width | artifacts whose window site is E-find D-hors with a C-own one-class stretch of 16..31 positions, or R7w with one of 24..31 (e.g. `[0-9a-f]{17}`..`{32}`, `\w{17}`..`{32}`, `[^\n]{17}`..`{32}`, `[0-9]{25}`..`{32}`, `[A-Z]{25}`..`{32}`). The walk calls `vs<j>`; file scope gains `__body` and the selector | `[0-9a-f]{16}` (k 15), `[0-9]{24}` (k 23), any 33+ position pattern (no window site at the default width), LIBC finds (`x[0-9]{26}`, `ab[0-9]{26}`), PAIR finds (`[xy][0-9]{26}`), D1w walks, floor and legacy sites, every VM/DFA body text |
| `-fmemfn-simd=x86-64-v3` | the same artifacts, plus the bracketed level block, the selector's replaced call, `<immintrin.h>` ahead of the region, `MEMFN_FORMS` `span-vector@w32`, `SIMD_GUARDED_BYTES` | as above |
| `-fmemfn-simd=x86-64` (w16 only), `generic` | as `-fno-memfn-simd` (wrapper, no helper) | — |
| `--window-search-width=W` > 32 | D-hors with 16 ≤ k ≤ min(1000, W - 1); R7w with 24 ≤ k ≤ min(64, W - 1) (r69 POP: at W = 64, `[0-9]{64}` is R7w k 63 and `[0-9]{65}` E-stmt) | k > 1000 (HORS), k > 64 (WALK): H64 |
| `--memfn=no-span-vector` | nothing: main's bytes, every setting | — |
| `--memfn=no-span-loop` | at V sites, the wrapper is replaced by T-deny's all-inline text (the `.rxt` makes `span-loop`'s axes class DIFFER, §9.3) | — |

Over the real corpus the default build moves no artifact but the abi
lines (0 V sites, §0.1); the bench moves 3; SPAN-SEED's `.rxt` moves 28 at
the default width. This lane runs no sweep.

## 12. Constants register (Frank: unroll widths, block sizes, cut-overs are suspect)

| constant | label | source |
|---|---|---|
| 16 (HORS lower bound) | MEASURED and DERIVED: 710's bound, and the smallest rung (§4.2: below 16 no block fits). A re-measure may RAISE it, never lower it | 710, rule `6351bff3901e3955`; §4.2 |
| 1000 (HORS); 24, 64 (WALK) | MEASURED; CANDIDATE until every bench box runs C6 (§8) | 710, rule `6351bff3901e3955` |
| 64 (H's head, `WF_SPAN_HEAD`) | MEASURED | cards run fcards-zen4-1, unchanged |
| B ∈ {32, 16} | DERIVED: the level's vector width and its half; the largest that fits in k, so no read leaves the span | §4.2 |
| the loop shape (not unrolled) | MEASURED as a form: 710 timed `loop` | 708/710 |
| `guarded_max` (`span-vector-w32`) | CHOSEN, UNMEASURED DEFAULT, a cap by construction | §5 |
| SPAN-SEED floors 28 / 31 (byte), 20 / 21 (utf8) | DERIVED: the table's predicate over the committed `.rxt`'s patterns, by the independent k source | §10.1, §16 item 5 |
| [rev4.1, R71-2] `span-vector`'s `MEMFN_CLASS` corpus floors (about 28 byte / 20 utf8 on `c-default`, 0 on `c-vm`) | MEASURED at U2, pinned at the measure (ruled, §15 Q4) | §9.3 |
| U2b's padding regex | DECLARED before data; drilled two-sided | §2.1, §16 item 12 |
| `SWAR_MAX_RANGES` | not shipped (no row reaches SWAR) | §4.4 |

## 13. The three standing questions

1. **The measurement regime (RELEVANT).**
   - **710's regime:** Zen 4 7700X (the dev box), gcc 15.2, glibc, CPU 15
     pinned with a quiet sample, throughput (ns/B, find-all, 1 MiB
     subjects), six regimes plus near-miss-in, x86-64-v3,
     `--window-search-width=4095`, fresh layout pools, A/A 6/448.
   - **What could flip a row:**
     - Zen 1 (2x128 AVX2) could raise the k at which V wins near the lower
       bounds (never below 16, §12). [rev4, R-31] **V is CANDIDATE until
       C6 runs on each bench box that runs it; a repeated LOSS on Zen 1
       blocks the level** (D155 item 2, D144 addendum 4), it does not
       merely move a bound;
     - another compiler (clang: unmeasured, its region is a different
       pragma);
     - a latency regime (one short call) is not what 710 timed.
   - **SIMD-off is not timed** (r68 F-14): its record is U2b's machine-code
     census, a compile-time reading at one gcc (15.2, -O2). Another gcc
     could move which sets differ. [rev4, R-26] The re-run trigger "the
     house gcc changes" has no committed instrument: it is a row for main
     to file (§17), with U2b's command (in the build lane's report) as its
     method.
   - The default width is not a regime change: the text is identical
     (§3.2).
   - The official verdict is the planned bench run on the targeted
     hardware, via main (D144 addendum 4).
2. **The independent control (RELEVANT).** §10:
   - the answers are checked against python `re` and python per-byte
     membership, never the kit's set; SPAN-SEED's `.rxt` is
     oracle-verified;
   - the row bounds and columns against a literal cell list, read from
     the text;
   - every V-site count uses the independent k source (FDROUTE + the
     head-0 loop text + the predicate in the check), never the kit's
     table record (§10.1);
   - the population comes from pcrec's diff (default vs deny), never
     `moved`;
   - the identity gate's reference is the merge base, built once; its
     mask is declared before data and drilled against real artifacts and
     a real bump (§16 item 11);
   - the C18 rule and the routing leg drilled on correct text and on each
     plant at both rungs (§16 item 10);
   - fidelity against a different generator (spike708) and 710's own arm
     sources;
   - the census has two-sided normalizer controls and two known positives
     (§2.1);
   - every sabotage plant has a reach witness, and the anchor map covers
     every function each unit moves (§10.2).
3. **What moves when the data is regenerated (RELEVANT).**
   - The table's bounds are constants in window.c, not a data file. A
     re-measure that moves them (a C6 run on other hardware, a re-run of
     710's rule) moves emitted bytes: a kit byte move, so a pcrec abi event
     plus a spec check. SPAN-SEED's pin cells and floors move with them;
     the `.rxt`'s answers do not (they are the oracle's).
   - Regenerating `tests/memfn/span_seed.rxt` (its generator) moves the
     corpus-population pins §9.3 lists; its answers are re-verified by
     `verify_rxt.py`.
   - `kit-grid@8` is append-only.
   - The `span-vector` form hash moves with any change to §4.1's text,
     staling the C6 row.
   - No calibration or measure-set row prices V. It is a rule row, not a
     priced choice.

## 14. The build units, in order

**U1 may start after the light re-check** (r69 ruling R-26: U1 moves no
artifact byte and is identical under either arm and either reading of the
owner question). [rev4.1] r71 ran (READY WITH TEXT FIXES); U1 is built by
lane bsu1. [rev4.2] `scalar-check-cut` is ANSWERED (yes, §2.2): U2 and U2b
are built (lane bsu2) and fixed (lane bsu2fix, r75); U3 onward is next.

| unit | what it does | moves bytes? |
|---|---|---|
| **U1** | The table refactor: `wf_span_head` becomes THE SPAN FORM TABLE (T-deny, T-force, T-lever, T-head; the V rows land at U2), its four contracts (six at U2, with the V rows), `wf_tables_check`'s line and the `trace_format.md` hunk (§3); the stretch list stored once by one enumerator (E-find in `wf_find_prepare`, the floor in `wf_plan_site`'s floor branch); `skip` a plan fact by the search rows' `skip` column; `w->head` retired; `wf_loop_len` takes the head. **SPAN-SEED's `.rxt` and generator committed** (§10.1), with the population pins it moves (`make test`). The U1 re-aims and REACH re-proofs (§10.2). An identity gate: every corpus artifact (the `.rxt` included) and SPAN-SEED at 4095 byte-identical to the merge base at both layers, both engines (no mask: no abi event); the 4095 run is the U1 lane's one-off, and its repeatable ratchet lands with U2's identity gate (§10.1). A refactor gets no flag (Frank 2026-10-29). [rev4.1, R-1 of lane bsu1] **The decider census** (a U1 surface this note missed, found red by `make test-memfn-rows`): `tests/memfn/decider_census.tsv` gains `wf_stretches` (fn) and `wf_spanrows` (data), answering the new table name **T-SPAN** (the span form table, `wfS`), added to its header list; `decider_census.py`'s `HITS` 67 to 68 and `MEMBER_COUNT` 70 to 72, re-derived from the map; the retired if-chain had no row | no artifact byte (a corpus file is added) |
| **U2** | The wrapper (option A): T-vwin, T-vscan; `vs<j>` + `__body` + the selector for eligible stretches at every layer, the selector line through the ONE lifted selector writer (§5; ofsskip's bytes unchanged); the deny row `span-vector` (both layers) with its `MEMFN_CLASS` row, its corpus floors measured and pinned at U2 [rev4.1, R71-2], and `span-loop`'s re-measured axes rows (§9.3). The identity gate against the merge base for the deny arm, with its declared mask. The U2 re-aims, `REACH_ONLY` at U2. The first abi event lands here | yes |
| **U2b** | **The scalar no-loss check** (§2.1): the machine-code census on the BUILT U2 text, the declared normalizer with its two-sided controls, over the real population, the 160-pattern grid and `\w{501}` at 4095. Identical on the population, or the build stops; the grid's DIFFERS list goes into the report | no |
| **U3** | The `w32` level block: §4.1's text bracketed by V's own writer (lane order, the K ≥ 16 assert), the selector's replaced call, the include bit on the art, the form token, the guarded bound and `simd_bounds.tsv`, the `limits.md`/`tuning.md`/`registry.md` hunks. [rev4.1, R71-4] **C18's head family (`SELECTOR`, `HELPER`), the `_b` name form and the -O0 rule with control (1)** (§10.2), so `test-memfn-simdfloor` reads U3's text green. [rev4.1, R71-5] A V witness (`[0-9a-f]{17}`) added to `simd_guarded_check.py`'s NAMED, `simd-form-named` re-pinned 8 → 9, so the new `simd_bounds.tsv` row has a reader that is not the every-10th sample. F2 recorded before anything else | yes (SIMD-on) |
| **U4** | G2-V (unit, whole, with guard pages at both ends), the 20 T-table pin cells, SPAN-SEED's per-check wiring and floors (§10.1), sabotage rows (a)-(f) with reach, **the rest of the C18 amendment** (its NAMED three span witnesses, x86-64-v3 only (R71-1), the floors, controls (2)-(4)), the routing leg, `DIFFER_PINS` floors, C18's `FLOORS` re-pin | no |
| **U5** | Card C6 (its patterns, widths, A/A arm and rule clauses as §8 states; CANDIDATE) + `kit-grid@8` + the formhash SHAPE, renderer and entry; `cards.py plan`/`dry` green, with no timing; the U5 re-checks | no |
| **U6** | The abi package at the landing base (§9.2, the unfiltered grep), `make test` async, `make test-axes`, REACH_ONLY. Then G1's manifest and dry run (no timing window, §9.4); C6's timing owed to main's window, on each bench box (§8) | — |

The design rounds (r68, r69) preceded this revision; a light re-check
follows it. The code round precedes the landing (Frank 2026-11-15). U2 and
U3 may share one abi event if they land together; the number is taken
once.

**[rev4.2] He KEPT the cut (`scalar-check-cut`: yes, §2.2): arm 1, the
units above as written.** The re-design paths for a restored timing or
T-keep, and arm 2's list below, are kept as history.

**The identity gate is a DELIVERY step [rev4.2, r75 CHECKS-6].**
`tests/memfn/span_vector_identity.py` is run once per delivery of a unit
that moves bytes (U2, and U3 when it lands), like U2b's census; it is
wired to no make target on purpose: its reference is a build of the lane's
merge base, which cannot exist after the merge, so it cannot ratchet. What
repeats at make tier is `tests/axes/memfn_arm.py`'s `span-vector` DIFFER
rows (28 / 20 floors, §9.3) under `make test-axes`. U1's "repeatable
ratchet lands with U2's identity gate" reads that way. A pinned reference
commit (`run_recursion_identity.sh`'s FILEPIN shape) would make it
repeatable and is a PLAN item, not built.

**Under arm 2 (the proxy row; DEAD since add. 4) [rev4, R-26]** the build
also needs:
1. a NEW §3 fact column, the term count `kit_set_test` renders for the
   set: a renderer OUTPUT, so the same lift R-1 met for `skip` (a plan fact
   written where the set is known);
2. its threshold in §12, CHOSEN (fit to one gcc's probes) and labelled so;
3. pin cells for the row (`\w{20}` absent, `[+.0-9]{25}` present), an
   ordering cell, and a sabotage plant with REACH;
4. SPAN-SEED's floors re-derived: the slice's `word` and `ident` cells (6
   of the 26 at width 32) leave V;
5. G-2's and §6's literal "82 routed cells" (`word` and `ident` are 22 of
   them) and C6's population;
6. §11's movers (`\w{17}`..`{32}` stop moving);
7. a D80 spec hunk: §7's deny doc and `tuning.md` §2.43¶3a become false
   for the excluded sets, which the caller observes at SIMD-on;
8. a home for the committed census: "red on any compiler that moves it"
   inside `make test` conflicts with R5-Q1 (a stranger's `make` must not
   fail on a newer gcc), so it must be opt-in or pinned to the house gcc,
   CHOSEN in that build;
9. §17's counts.

Option B instead of arm 2's proxy row is a separate architecture note.

## 15. Open questions

1. **`scalar-check-cut`: ANSWERED, yes** (Frank 2026-11-21, D201 add. 4;
   §2.2) [rev4.2]. **`wrap-clang`: OPEN, the owner's** (§2.2.1, from the
   census's compiler scope); U2 does not wait on it.
2. Owed to main, not blocking: the cover-width timing (`cover_cap.md`
   §11.4 B) decides whether the default window width (32) rises.
3. **Relays to main [rev4, R-23, R-24, R-29]** (records only; main's to
   act on):
   - D201 add. 3 (a) restates, in its amended R-47 GO line, the READING
     with "a short timing in a window Frank clears" and "a loser keeps
     today's text through a selector row". Both were cut by the kit
     manager's r68 F-14 ruling (FREEZE NOTE); main's line should say the
     reading moved and why;
   - D201 add. 3 (b) now records R-4's words, `scan-scope`, `wrap-deny`
     and the D155 recollection: R-24's (a)-(d) are closed. R-24 (e) (a
     manager's leaning on the fork) has no record because none was ruled:
     §2.2 labels it as the lanes' framing;
   - R-29 is closed at main: D201 add. 2's population line and D201's
     provenance pointer carry the corrections and cite r68 (checked at
     `d255d94a3`).
4. **[rev4.1, R71-2] RESOLVED: the `MEMFN_CLASS` corpus floor for
   `span-vector` is PINNED AT THE MEASURE at U2, not 0** (the kit
   manager's ruling, 2026-11-21, recorded post-freeze in the kit journal
   and in r71's MANAGER RULING; K35). The measure is about 28 (byte) / 20
   (utf8) on `c-default` and 0 on `c-vm` (§9.3).

Resolved earlier, restated in the FREEZE NOTE: `scalar-wrap` (read as
option A, as cut by r68 F-14), `scan-scope`, `wrap-deny`, R-4.

## 16. TODAY NUMBERS (each with the command that produced it)

Rev 4 re-derived items 1, 5 and added items 10-13 at the lane's build of
lane/bspan4 (`nice make -j2`; src, memfn/src, tests identical to main
`d255d94a3`: `git -C worktrees/bspan4 diff --stat $(git merge-base HEAD
main) main -- src memfn/src tests` is empty), plus a traced pcrec-harness
(`tests/memfn/mk_mftrace_lib.sh $S/tr/libtr.a build/libpcrec.a`, linked
with `cli/main.c -DPCREC_HARNESS`) in `$S = $PCREC_TMPDIR/scratch/bspan4/`.
The drill tools are in `$S/tools/`; the hand-built V text is
`$S/tools/build_v.py` (r69 EMIT's builder, copied unchanged: §4.1 + §5
literal, from the build's OFF/ON artifacts).

1. **abi 109.** `grep -n 'define PCREC_ARTIFACT_ABI' src/gen/emit_dfa.c` →
   `55:#define PCREC_ARTIFACT_ABI 109`. Readers: `git grep -n -w 109 --
   src tests docs/spec docs/testing.md memfn/src memfn/tests` → 215 hits,
   reviewed against §9.2's list; `git grep -n 'v109' -- src tests docs/spec
   docs/testing.md memfn scripts` → no reader (one unrelated `v109_71` in a
   recursion corpus subject).
2. **`memfn` section floor 14.** `git grep -n 'memfn. section floor' --
   docs/spec/registry.md` → `[6¶8b] ... floor: 14`.
3. **Head 64, the if chain.** `grep -n WF_SPAN_HEAD memfn/src/window.c` →
   1470 (`enum { WF_SPAN_HEAD = 64 }`), 1476, 1483. The chain is
   `wf_span_head`, window.c:1477-1484.
4. **Levels.** `grep -n '^MF_LEVEL' memfn/src/levels.def` → `LV_X86_W16`
   (sse2, x86-64) and `LV_X86_W32` (avx2, x86-64-v3); no others.
5. **Finder rows, k, the population, SPAN-SEED and the pin cells** [rev4].
   The k source of §10.1: `python3 -I -B $S/tools/seed.py
   $S/tr/pcrec_trace $S/seed` (per pattern and width: `pcrec_trace -p rxa
   --features all --harness=span-head=0 --window-search-width=W -o a.c
   --pattern P`, the FDROUTE record from stderr, the loops from `a.c`, the
   predicate applied in the script). Results:
   - SPAN-SEED: **41 distinct patterns; V sites 28 at width 32, 31 at width
     4095** (`$S/seed_census.txt`); with `-e utf8`: **20 and 21**
     (`$S/seed_census_utf8.txt`). Every eligible loop is C-own;
   - the 3 bench sites: `[0-9a-f]{32}`, `\b[0-9a-f]{32}\b` D-hors k 31
     (loop 0..31), `\d{32}` R7w k 31 (loop 1..32), at widths 32 and 4095;
   - the pin cells (`seed.py ... --cells`, `$S/pin_cells.txt`): `[0-9a-f]{16}`
     D-hors k 15 (absent) and `{17}` k 16 (present) at 32 and 4095;
     `{1001}` k 1000 present, `{1002}` k 1001 absent (4095); `[0-9]{24}` R7w
     k 23 absent, `{25}` k 24 present (32, 4095); `{65}` k 64 present,
     `{66}` k 65 absent (4095); `ab[0-9]{26}` D1 k 26; `[xy][0-9]{26}` PAIR
     k 26; `ab[0-9]{26} --memfn=no-fd-d1` **D1w k 26**;
     `[0-9a-f]{20}[g-z]{20}` at 4095 D-hors, first stretch k 20;
     `[0-9a-f]{33}` at 32 R7w E-stmt (no stretch);
   - R-6's admitted shapes: `[0-9a-f]{32} --memfn=no-window-skip` → R7w k 31;
     `[0-9a-f]{31}[0-9]` → R7w k 31; `\w{501}` at 4095 → D-hors k 500.
6. **Machine-code probes** (gcc 15.2.0, -O2, `objdump -d` of `rxa_search`,
   addresses normalized): (a) rev 1's (`$PCREC_TMPDIR/scratch/bspan/`): on
   710's `avx2-loop` sources with the `target()` attributes dropped,
   IDENTICAL on 6/6. (b) r68's two-level figures (SOUND-5, PREMISE-9,
   MEAS-6): the 3 real sites 0 instruction differences; `\w{17}`,
   `\w{20}`, `\w{32}` 20-26 lines; `[+.0-9]{65}` 0. Re-drilled at item 12.
7. **Job 710's verdict** (`$PCREC_TMPDIR/scratch/memfn/blockconfirm/run-20261120T212920/decision.md`):
   CONFIRMED. 840 cells, 112 N/A; the verdict population 144: 127 WIN, 17
   TIE, 0 LOSS; over all counted cells 295 W, 427 T, 0 L; row 1 255/140/0,
   row 2 40/37/0; replication 104 of 115; A/A 6/448.
8. **The C18 rule (c) and its regexes.** `grep -n 'SELECTOR = \|HELPER = '
   tests/memfn/simd_floor_check.py` → 123 `^static inline size_t
   (\w+)\(...`, 124 `^static inline size_t (\w+)__w(\d+)\(`; its -O0 leg:
   `nm` of the `-O0` object (:375-381). `routing_shape.py`: `FUNC_SUFFIXES`
   (:38) and `HEAD` (:39).
9. **710's grid.** `sed -n 43,60p
   $PCREC_TMPDIR/scratch/memfn/blockconfirm/confirm.py`: ten classes, 13 k;
   routed cells 6 x 11 + 4 x 4 = 82 of 130.
10. **[rev4] The C18 amendment and the routing leg, drilled (lesson r69-1).**
    Texts: `build_v.py OFF.c ON.c SET LO K OUT [--no-ai-w32]` from
    `build/pcrec -p rxa --features all [-fmemfn-simd=x86-64-v3]
    --window-search-width=W`, for `[0-9a-f]{17}` (LO 0, K 16, B 16),
    `[0-9]{25}` (1, 24, B 16), `[0-9a-f]{32}` (0, 31, B 16), `[0-9a-f]{41}`
    @4095 (0, 40, B 32), `[0-9a-f]{1001}` @4095 (0, 1000, B 32), and the
    plant (`--no-ai-w32`: `__w32` without `always_inline`) on the first,
    second and fourth. Rule: `python3 -I -B $S/tools/c18drill.py $S/v
    hx17 dg25 hx32 hx41 hx1001 hx17n dg25n hx41n` (gcc -O0 and -O2,
    `-Wall -Wextra -Werror`; `nm`, `objdump -d` of `rxa_search`;
    `$S/c18drill.txt`):

    | witness | B | -O0: family symbols; `pshufb`; ymm; xmm | -O0 rule | -O2: family symbols; `pshufb`; ymm |
    |---|---|---|---|---|
    | `[0-9a-f]{17}` | 16 | none; 6; 0; 888 | PASS | none; 3; 0 |
    | `[0-9]{25}` | 16 | none; 6; 0; 888 | PASS | none; 6; 0 |
    | `[0-9a-f]{32}` | 16 | none; 6; 0; 888 | PASS | none; 6; 0 |
    | `[0-9a-f]{41}` @4095 | 32 | none; 6; 188; 1460 | PASS | none; 6; 60 |
    | `[0-9a-f]{1001}` @4095 | 32 | none; 6; 188; 1460 | PASS | none; 6; 60 |
    | plant on `[0-9a-f]{17}` | 16 | `rxa_mf1_vs0__w32`; 0; 0; 0 | RED | none; 3; 0 |
    | plant on `[0-9]{25}` | 16 | `rxa_mf1_vs0__w32`; 0; 0; 0 | RED | none; 6; 0 |
    | plant on `[0-9a-f]{41}` @4095 | 32 | `rxa_mf1_vs0__w32`; 0; 0; 0 | RED | none; 6; 60 |

    The amended `SELECTOR` finds `rxa_mf1_vs0` → `w32` and the amended
    `HELPER` finds both `__w32_b` and `__w32` on all eight. At -O2 the
    plant is invisible (gcc inlines the static anyway), so the -O0 leg is
    the only one that sees it. Rev 3's "a `ymm` in the caller" reads ymm 0
    on every B = 16 text: red on correct text (r69 R-7, reproduced).
    Routing leg: `python3 -I -B $S/tools/rs_drill.py <tree> $S/v/hx17.offv.c
    $S/v/hx17.onv.c $S/v/dg25.offv.c $S/v/dg25.onv.c $S/v/hx41.onv.c
    $S/v/hx1001.onv.c` (`$S/rs_drill.txt`): 7 of 7 controls as expected; 1
    V FUNC and no violation on each text; today's `routing_shape.check`
    counts 0 FUNCs on each.
11. **[rev4] The identity gate's mask, drilled on real artifacts (lesson
    r69-3).** `bash $S/tools/abigate.sh build/pcrec $S/abi/pcrec110
    $S/abig` (`$S/abigate.txt`), where `$S/abi/pcrec110` is the lane's
    build with ONE change, `emit_dfa.c` compiled with `PCREC_ARTIFACT_ABI
    110` and swapped into a copy of `libpcrec.a` (a real bump). Each
    pattern compiled by both, same `-o` basename, then the nine spellings:
    - DFA default `[0-9a-f]{32}`: `.c` 2 lines hold 109 (1 M1, 311 M2),
      `.h` 4 (1 M1, 8 M3, 9 M4, 12 M5); masked old vs bumped: IDENTICAL;
    - DFA x86-64-v3, VM engine `(a|b)*c\1`, `--emit-main`: the same five
      spellings (M2 at the `.c`'s `.abi` line); IDENTICAL;
    - `a{109}b` (the number in the pattern): the pattern's own `109` lines
      stay UNMASKED (as they must) and the real bump is IDENTICAL after the
      mask (only the abi lines moved);
    - subst `--subst 'x$1y'`: `.h` holds 7 word hits (M1, M3, M4, M5, M6,
      M7, M8) and **6 more lines no word grep sees**, `#define
      pcrec_subst_<x> pcrec_subst_<x>_v109`: with M1-M8 alone the bumped
      `.h` DIFFERS; with M9 it is IDENTICAL. This is the drill's finding:
      M9 is new in rev 4;
    - the support unit `--emit-support` (one `.c`): M1, M3-M8 and the same
      six M9 lines all mask, but the bumped unit still DIFFERS on ONE line,
      `pcrec_subst_support_id = 0x<hash>ull` (`0xfff43a8eff9db85c` at 109,
      `0x236de9258d2400cc` at 110): a derived hash, not a spelling of N, so
      no word grep finds it. The gate's population never holds the support
      unit, so §10.2 declares it out of the mask, with the row a future gate
      would need. The second finding of the drill.
12. **[rev4] U2b's normalizer, drilled.** `python3 -I -B $S/tools/u2b.py
    $S/u2b hx32_32 bhx32_32 d32_32 hx32_4095 bhx32_4095 d32_4095 w20_32
    w501_4095` (`$S/u2b.txt`; today's `-fno-memfn-simd` artifact against
    `build_v.py`'s wrapped OFF text, same basename, gcc 15.2 -O2; counts
    are added plus removed lines):

    | pattern | width | raw | normalized | verdict |
    |---|---|---|---|---|
    | `[0-9a-f]{32}` | 32, 4095 | 0 | 0 | IDENTICAL |
    | `\b[0-9a-f]{32}\b` | 32, 4095 | 3 | 0 | IDENTICAL (the positive control) |
    | `\d{32}` | 32, 4095 | 0 | 0 | IDENTICAL |
    | `\w{20}` | 32 | 46 | 42 | DIFFERS (the negative control, a known positive) |
    | `\w{501}` | 4095 | 2 | 2 | DIFFERS (the second known positive) |

    The built U2 text is what U2b reads; this drill shows only that the
    declared regex passes and fails as worded on its named witnesses.
    [rev4.1, R71-7 (a)] r71's critic did NOT reproduce `\w{20}`'s 46 / 42:
    on its own hand-built wrapper text it read 26 / 22 by python difflib
    and 24 / 20 by GNU diff (r69 R-17 also read 22). The verdict DIFFERS
    holds under all three; the figure depends on the diff tool and on the
    wrapper text, so U2b names its tool and re-derives it on the BUILT text.
13. **[rev4] The sabotage-anchor map (lesson r69-2).** `bash
    $S/tools/anchors.sh <tree> > $S/anchors.tsv` (229 rows on `memfn/src/`)
    then `python3 -I -B $S/tools/anchor_map.py <tree> $S/anchors.tsv`
    (`$S/anchor_map.tsv`, row → enclosing function); the files the units
    edit outside `memfn/src/` read the same way. Results as §10.2's
    re-aim list: in window.c, `wf_span_head` S3278 S3279 S3281 S3282;
    `wf_loop_len` S3277 S3280; `wf_loop` S3276 S3283 S3284; file scope
    S3285 (the enum), S2982 (the RB_PAIR row); in ofsskip.c,
    `fn_selector` S730; `fn_call_line` S690 S694; `fn_level_block` S724
    S2995 S3001 S3002; `fn_define` S687 S691 S692 S695 S728; formhash.c
    S2930 S2933; no anchor in `plan_of`, `wf_test_to`, `d_hors_head`,
    `find_head`, `wf_find_prepare`, `wf_find_expr`, `c_find_test`,
    `c_floor_test`, `wf_test`, `wf_find_define`, `wf_plan_site`,
    `wf_tables_check`.

## 17. SHIP-SIZE (R-4's lens; information, not a ruling) [rev4, R-30]

What the build adds, under option A, `scalar-check-cut` kept, and outcome 1. Counts
marked UNMEASURED are estimates the build lane replaces with `git diff
--stat` at its landing; nothing here was built.

| surface | added |
|---|---|
| table | 2 rows (T-vwin, T-vscan) plus the 4 I/L/H rows reshaped from the if chain; 1 `kit_table` (`wfS`) with **6 contracts** and 1 `wf_tables_check` line; `wf_span_head` and `w->head` retire; `skip` one plan fact via **1 search-row column** (4 rows); **1 stored stretch list** and its enumerator (2 call sites) |
| code, `memfn/src` | the enumerator, the V level-block writer (§4.1, two widths), the `__body`/selector writing at define, the lifted selector writer (one function, two callbacks) and `fn_selector` as its thin caller: UNMEASURED, expected a few hundred lines in `window.c` and `ofsskip.c`, 1 `kit.h` declaration, no new file |
| emitted text per site | scalar layer (every layer): the `vs<j>` selector and `__body` (one `return` each, about 0.4 KB, UNMEASURED). SIMD layer (`w32`): the bracket, about 1.75 KB at B = 16 and 2.0 KB at B = 32 (hand-built, §16 item 10) |
| deny | 1 row (`span-vector`), live at both layers; 1 `registry.md` row, floor 14 to 15; **2 `MEMFN_CLASS` cells** (default, simd) and **the re-measure of `span-loop`'s 2 + 2 cells** |
| card | 1 (C6: 3 real sites + 6 bound cells + F2 DIFFERS, plus an A/A arm; CANDIDATE), 1 `kit-grid@8` row, 1 formhash SHAPE + its renderer + 1 entry |
| decider census [rev4.1, lane bsu1 R-1] | a surface this note missed (U1): 2 `decider_census.tsv` rows (`wf_stretches` fn, `wf_spanrows` data) answering **T-SPAN**, the header's table list +1, `HITS` +1, `MEMBER_COUNT` +2 |
| SPAN-SEED | **1 committed `.rxt` (41 patterns, about 950 oracle-verified cases) + its generator**, 1 `tests/memfn/CLAUDE.md` line, the corpus-population pins it moves (§9.3), **wiring into 6 checks** (§10.1's table) with 2 floors (byte) |
| checks | 1 G2-V unit section, 1 G2-V whole section (with guard pages), **20 pin cells over 11 patterns**, 1 identity gate with a **9-spelling** declared mask, **the C18 amendment** (2 regexes + the `_b` name form, the -O0 rule, 3 named witnesses, 4 control plants), **the routing leg** (a name rule, a head family, 7 selftest shapes), `DIFFER_PINS` floors, C18 `FLOORS` re-pin, the `simd_bounds.tsv` row, G1's diff script and manifest; F2 and the U2b census are delivery steps, not committed tests |
| mech | **6 new sabotage rows** ((a)-(f)) and 4 C18 control rows; re-aims **U1 5 + 1 re-check + 5 re-proved REACH; U2 1 (+ 1 V witness) + 2 re-proved; U5 2 re-checks; U6 1 (S693)**; 9 conditional re-checks |
| spec | `registry.md` §6¶8a/8b, `tuning.md` §2.43¶3a/3b/3d, `limits.md` §8.3¶3, `match_api.md` §1 (the K80 guard's 3 lines), §6 (the `abi` row) and §6¶17: **7 hunks**; plus `memfn/docs/trace_format.md` (kit doc) |
| stamps | the `MEMFN_FORMS` token, the guarded-bytes count |
| abi | 1 event (the number taken at landing, §9.1) |

**Rows to be filed by main in plan.md** (the kit has no plan file; not
filed by this note): (1) the `--harness=span-vector=force` and
`span-vector-body` levers, trigger: a bound questioned by a C6 or Zen 1
run; (2) G1's timing, trigger: a bin reaches 8 real movers; (3) U2b's
re-run when the house gcc changes, method: U2b's command from the build
lane's report; (4) the Zen 1 C6 run (via main, D144 addendum 4; it
decides CANDIDATE, §8); (5) vany's ride-along: the two-function level block
and vany's level block lifted into one writer at vany's next touch (§5).

**Cut by r68 (each with its trigger):** T-keep and §2.1 (c) (returns only
under arm 2, as a proxy row); U2b's scalar timing; G1's timing window
(trigger row (2)); C6's four outside-bound cells; the force and body levers
(row (1)).

**Changed by r69:** grew by the routing leg, the `.rxt` and its wiring,
the `MEMFN_CLASS` cells, 8 pin cells (D1w, 4 lever/force, the bound cells
counted at both widths), plant (f), a third named C18 witness, M5-M9 in the
mask (counted, not new work: M1-M5 were four spellings plus the missed
`.abi`), the U2 re-aim, a fifth spec hunk family (`match_api.md` §1);
shrank by R-4's choice (one selector writer lifted, not a full writer),
the frame column and its pin, leg (i)'s control, and the use-side asks
(store-once). Net: about rev 3's size plus the `.rxt` (the one larger
item, ruled).

**Against the population:** 3 (text, options) pairs route today, all in
the bench, all k = 31 (§0.1), by information only (D201 add. 1: "We're
here and there's no downside so let's build it."). Kept because the 710
table needs them (R-4): both bounds of both rows, the B = 32 rung, the
deny, the one-stretch-per-site rule, the 32 and 16 rungs only, no SWAR, no
unrolled form, no knob beyond the deny row. Every r69 addition traces to a
ruled finding (§18).

## 18. Dispositions

### 18.0a r75 (review 2026-11-21-r75-memfn-bsu2, the kit manager's MANAGER RULING: FIX FIRST, small) [rev4.2]

| id | ruled | answered in |
|---|---|---|
| CHECKS-1/3 gate floors, empty cells | FIX-NOW | `span_vector_identity.py`: per-cell mover floors (28 byte / 20 utf8 at width 32, 31 at 4095, from the committed `span_seed.rxt`, always in the population), a population-0 cell fails; the independent k-source count of §10.1's wiring row is NOT built (the committed seed's V sites are the floor) |
| CHECKS-2 per-hunk movers | FIX-NOW | the gate diffs default against deny at each mover: one definition insertion and one walk line per site, one call per site |
| CHECKS-4 mask rows | FIX-NOW | rows selected by name, a group replaced only where it equals that side's STATED abi (`--ref-abi`, `--abi`), per-row hit counts printed |
| CHECKS-5 the x86-64 layer | FIX-NOW | `LAYERS` gains `-fmemfn-simd=x86-64` |
| CHECKS-6 the gate is a delivery step | DOC | §14 |
| CHECKS-7 stale comments | FIX-NOW | S3280's SAB_DESC, `memfn_arm.py`'s span-vector comment |
| CHECKS-8 V text readers | PLAN at U3 (the U3 brief) | not here |
| SLOT-1 the tag's place | FIX-NOW | the readers tolerate `key=value` tokens before `chosen=` (`reach_equal.py` and three more), `trace_format.md` |
| SLOT-2 named-id typo | FIX-NOW (the self-check only) | `fd_tables_check` at `mf_art_begin`, sabotage S3510; the general form (a named-row index) is PLAN |
| SLOT-3, SLOT-4 | PLAN at U3 | not here |
| SLOT-5 this note | FIX-NOW | status, FREEZE NOTE (D201 add. 4; R-4's record), CONSTRAINT, §2.1 record, §2.2, §2.2.1 |
| SLOT-6 decider census | FIX-NOW | `decider_census.tsv` (six wfS rows) |
| CENSUS-1/2/4/5 | DOC | §2.1 "The U2b record" |
| CENSUS-3 | DOC + owner question `wrap-clang` | §2.1 "compiler scope", §2.2.1 |
| CONTRACT-1 the cap edge | DOC | registry §6¶8a `span-vector`, tuning §2.43¶3d |
| CONTRACT-2 help text, U3 not built | FIX-NOW | `options.def`'s `span-vector` help, registry, tuning |
| CONTRACT-3 "walks to the stop" | FIX-NOW | registry, tuning: "with the default set walk" |

### 18.0 r71 (review 2026-11-21-r71-memfn-bspan4, the kit manager's MANAGER RULING) [rev4.1]

| R-id | ruled | answered in |
|---|---|---|
| R71-1 C18's NAMED leg at x86-64 | FIX-NOW (text): a per-target column on NAMED, x86-64-v3 only; "two" -> three | §10.1 wiring row, §10.2 NAMED span witnesses, §14 U4 |
| R71-2 the Q4 ruling | FIX-NOW (text): floor pinned at the measure at U2, five places | §9.3, §12, §14 U2, §15 Q4 (resolved), §18.1 R-20 |
| R71-3 the floor-branch call | FIX-NOW (text); the reading CONFIRMED | §3 "Why the floor call is NEEDED" (R-2's words, the trace hunk, the slot budget) |
| R71-4 U3 red until U4's amendment | FIX-NOW (text): the head family, `_b` and the -O0 rule move into U3 | §10.2 C18 row and "Which unit", §14 U3/U4 |
| R71-5 `simd_guarded_check.py`'s sample | FIX-NOW (text): a V witness at U3, `simd-form-named` 8 -> 9; the U1 sample note | §14 U3, §9.3 (the `.rxt`'s pins) |
| R71-6 "present" reads 2/2 | FIX-NOW (text): the counted call spellings | §10.2 pin cells |
| R71-7 (a)-(d) | FIX-NOW (text) | (a) §2, §2.1, §16 item 12; (b) §10.2 U5 re-aims; (c) §5; (d) §3 "Where it runs" |
| FREEZE DRIFT `scalar-check-cut` | accepted as mapped; both readings carried | status, CONSTRAINT, §2.2, §3, §14, §15 Q1, §17 |
| U5/U6 not re-checked | accepted (the code round covers them) | — |

### 18.1 r69 (review 2026-11-21-r69-memfn-bspan3, the kit manager's MANAGER RULING) [rev4]

| R-id | ruled | answered in |
|---|---|---|
| R-1 `skip`'s producer | FIX-NOW | §3 "`skip` becomes a plan fact", §1 (the plan's order), §14 U1 |
| R-2 the define/use enumerator | **store-once** (ruled) | §3 "STORED ONCE", §5 |
| R-3 `kit_table` contracts and homes | FIX-NOW | §3 "The table's spelling", §9.5, §14 U1 |
| R-4 the one writer | **lift `fn_selector` only** (ruled) | §5 "One SELECTOR writer", §10.2 re-aims at U2, §17 row (5) |
| R-5 a function-local C table | FIX-NOW (C-own) | §3 (`own`, T-vwin/T-vscan), §4.1, §10.2 (no plant, population 0) |
| R-6 R7w admits unmeasured cells | DOC (admitted on purpose) | §3 "Admitted on purpose", §16 item 5 |
| R-7 the -O0 ymm rule | FIX-NOW | §10.2 the -O0 rule, §16 item 10 |
| R-8 the -O0 path and its control | FIX-NOW | §10.2 the -O0 rule and control (1), §16 item 10 |
| R-9 leg (i) | FIX-NOW | §10.2 "[R-9]", control (2) |
| R-10 `__w32_b`'s name | FIX-NOW | §10.2 the name form, §16 item 10 |
| R-11 `routing_shape.py` | FIX-NOW | §10.2 the routing leg, control (4), §16 item 10 |
| R-12 the identity gate's mask | FIX-NOW | §10.2 the declared mask (M1-M9), §9.2, §16 item 11 |
| R-13 U2's anchor moves | FIX-NOW | §10.2 "Re-aims" (U1, U2, U5, U6, conditional), §16 item 13, §17 |
| R-14 plants (e), (b) | FIX-NOW | §10.2 pin cells 17-20, G2-V whole's guard pages, plants (b), (e) |
| R-15 the D1w cell; the frame column | FIX-NOW (cell; frame column DROPPED) | §3 (frame column dropped), §10.2 cell 15, plant (f) |
| R-16 cells vs patterns | FIX-NOW (doc) | §10.2 (20 cells over 11 patterns), §17 |
| R-17 U2b's normalizer | FIX-NOW | §2.1 (one regex, two-sided control, non-movers relabelled), §16 item 12 |
| R-18 a k > 31 positive | FIX-NOW (add the cell) | §2.1 (`\w{501}` at 4095), §2, §2.2, §16 item 12 |
| R-19 the k source | FIX-NOW (doc) | §10.1 "The k source", §16 item 5 |
| R-20 `MEMFN_CLASS`; SPAN-SEED's wiring | **the row, the wiring, a committed `.rxt`** (ruled); [rev4.1] AMENDED by the §15 Q4 ruling (the corpus floor pinned at the measure at U2, not 0; R71-2) | §9.3, §10.1 (file, cases, oracle, wiring table), §7, §0.1, §14 U1/U2/U4, §15 Q4 |
| R-21 the bench attribution | FIX-NOW | §0.1 table |
| R-22 §11 under utf8; W > 32 | DOC | §11 |
| R-23 the READING quoted in part | FIX-NOW + relay | FREEZE NOTE (the reading in full, how it moved), §2.2, §15 Q3 |
| R-24 records | FIX-NOW + relay | FREEZE NOTE (record column; D155 item 6 cited), §2.2 (leaning labelled), §15 Q3 |
| R-25 D147 waived by arm 1 | accepted: two sentences | §2.2 arm 1 |
| R-26 arm 2's plan; the gcc trigger; U1 | the list; a row for main; U1 after the re-check (ruled) | §14 (arm 2's nine surfaces; U1), §13 Q1, §17 row (3) |
| R-27 the CONSTRAINT | FIX-NOW (text) | CONSTRAINT |
| R-28 G1's bins | FIX-NOW | §9.4 (real movers; SPAN-SEED separate), §10.1 wiring |
| R-29 §0.1/§15.3 stale | DOC + relay | §0.1, §15 Q3 (closed at main) |
| R-30 §17's recount; "filed" | recount; rows "to be filed by main" (ruled) | §17, §8 |
| R-31 D155 item 2 | CANDIDATE until every bench box runs it (ruled) | FREEZE NOTE, §8, §13 Q1, §12, G-3 |
| R-32 non-verbatim quotations | DOC | §0 Non-goals, §2, FREEZE NOTE |
| NOTED: SEAM-7 (segments, the finder-row identity) | NOTED | §3 (the stored list is R-2's form; the brow read by identity) |
| Lessons 1-3 | accepted, applied by this lane | lesson 1: §16 items 5, 10, 12 (each new rule on its witnesses at B 16 and B 32, -O0 and -O2); lesson 2: §16 item 13, §10.2 re-aims; lesson 3: §16 item 11 (found M9) |

### 18.2 r68 (review 2026-11-21-r68-memfn-bspan, the kit manager's ruling)

| F-id | ruled | answered in |
|---|---|---|
| F-1 C18 not unchanged | FIX-NOW | §10.2 "The C18 amendment" (rev 4: R-7..R-11) |
| F-2 population 3 bench sites, 0 corpus | FIX-NOW (doc) | §0.1, §11, §17, §16 item 5 |
| F-3 empty populations; identity gate mask | FIX-NOW | §10.1 SPAN-SEED (rev 4: a committed `.rxt`), §10.2 identity gate |
| F-4 D1w admitted | FIX-NOW (key on R7w) | §3, §3.3, FREEZE NOTE; guarded by pin cell 15 and plant (f) (rev 4) |
| F-5 `set_epi8` order | FIX-NOW (text) | §4.1 "Lane order" |
| F-6 unused `__body` (clang) | FIX-NOW (text) | §5 |
| F-7 plant (b) cannot fire on HORS | FIX-NOW | §10.2 plant (b) |
| F-8 lower bound 16 is a safety floor | FIX-NOW (label + assert) | §4.1, §4.2, §12 |
| F-9 five sabotage anchors retire | FIX-NOW | §10.2 "Re-aims" |
| F-10 where the table is evaluated; `skip`; include bit | FIX-NOW | §3 (rev 4: stored once, R-2; skip in `wf_find_prepare`, R-1), §5 include |
| F-11 third selector writer | FIX-NOW (decide) | §5 (rev 4: the selector writer only, R-4) |
| F-12 abi grep filters a reader | FIX-NOW (doc) | §9.2, §16 item 1 |
| F-13 wrapper evidence (Hspk one-level) | FIX-NOW (doc) | §2, §16 items 6b, 12 |
| F-14 scalar no-loss check; T-keep | MANAGER RULING | §2.1, §2.2, §3, CONSTRAINT |
| F-15 card C6 | FIX-NOW, no new lever | §8, §0 G-3 |
| F-16 formhash needs a shape | FIX-NOW (doc) | §8 `deps`, §14 U5, §17 |
| F-17 F2's `.H64` reference | FIX-NOW (doc) | §6, §16 item 9 |
| F-18 pins guard only k | FIX-NOW | §10.2 T-table pins (rev 4: 20 cells) |
| F-19 §11 examples, encoding | DOC | §11 (rev 4: R-22) |
| F-20 owner not quoted verbatim | FIX-NOW (doc) | FREEZE NOTE, §2 |
| F-21 owner's ruling ranked as a goal; "off by default" | FIX-NOW (text) | CONSTRAINT, §7 |
| F-22 G1 timing vacuous | FIX-NOW (text) | §9.4 (rev 4: R-28) |
| F-23 D155 add. 3 | DOC | §2, FREEZE NOTE |
| F-24 D201 provenance pointer | main's | closed at main (§15 Q3) |
| NOTED: line nits; w16 = off | NOTED | §1, §2 |
| Lessons 1-3 | accepted | applied in §0.1, §10.1, §10.2, §2, §2.1 |
