# The vector span: building job 710's block span at the SIMD layer (R-47, D201)

Status: DESIGN, rev 3 (lane bspan3, 2026-11-21, opus). Design only: no
code. Request R-47 (`memfn/docs/requests.md`); ruling D201 (slug
block-build). Order: this note, a critic round (r67, done), this revision,
then the build. **The build waits on ONE owner answer: `wrap-differs`
(§2.2).** Read §18 (the r67 dispositions) first.

Revision history:
- rev 1 (2026-11-21, lane bspan): first design, gated on `scalar-wrap`.
- rev 2 (2026-11-21, lane bspan2): scalar-wrap read as option A, option B
  retired, U2b and T-keep added, population record replaced by the final
  census, manager calls recorded, §17 ship-size.
- **rev 3 (2026-11-21): review r67 applied** (lane bspan3; review
  `docs/dev/reviews/2026-11-21-r67-memfn-bspan.md` on the kit branch, with
  the kit manager's ruling). The population corrected to 3 bench sites and
  0 corpus sites; seeded witness lists for every population-read check;
  T-keep, §2.1 (c), the scalar timing, the G1 timing window and C6's
  outside-bound cells cut; U2b a machine-code census on the built text
  over the population plus a probe grid; the `wrap-differs` fork (§2.2);
  the C18 amendment, the table's evaluation point, the `skip` fact, one
  selector writer, T-vscan keyed on R7w; the owner quoted verbatim. Text
  changed in rev 3 is marked `[rev3]` where a section kept rev 2's body.

Inputs read: D201 and its addenda 1-2, D146, D147, D155 and its addenda
1-3, D76/D94, D80, D144; integration.md §14, §15, §17.2, §18; the 710
run's `decision.md` (TABLE, ARMS, THE CLAIM, CONTROL), `confirm.py`,
`spike708.py` (`span_fn`, `nib_blk`, `span_body`); the 708 reports; the
reviews 2026-11-20-memfn-blockconfirm and -bcfix-recheck (MEASUREMENT-3);
review r67 and its five critic files; `tests/memfn/simd_floor_check.py`;
`memfn/src/window.c`, `ofsskip.c`, `vany.c`, `runcmp.c`;
`docs/dev/guide/README.md` + `coding.md`.

## FREEZE NOTE: the rulings this note rests on, restated here [rev3]

Review r67 found that four of the rulings below lived only in lane
rulings files (gitignored) and the kit journal. They are restated here so
that this note is their record for the build and the code round.

| ruling | words (whose) | what it means for this design |
|---|---|---|
| D201 | Frank, verbatim: "build with simd layer" | the build go for 710's table at the SIMD-on layer. "The scalar layer stays H64" is D201's "Read as" line (main's reading), not his words |
| D201 add. 1 | Frank, verbatim: "We're here and there's no downside so let's build it." | the population count is **information only**; it does not gate the build or its scope |
| D201 add. 2 (`scalar-wrap`) | Frank, verbatim (the record): "the function goes inline so it's just code organization? If that's true I don't have a problem with that." | the kit's and main's READING, not his words: option A, the wrapper at every layer, with its SIMD-off machine code checked. His answer is CONDITIONAL on "if that's true"; §2.2's owner question exists because it is not true on every set |
| D155 (Frank, recalled this round through the manager) | the selector shape is the SIMD organization agreed when the kit used `#if` code | the shape option A applies. D155 add. 3 made Q-R9-10's single-call shape a GUIDELINE; the design rests on the contract, not on that guideline (§2) |
| R-4, smallest form (manager, from main, 2026-11-21) | "design the SMALLEST form that serves the 710 table. Add no generality beyond what 710 confirmed" | no widths, site kinds or knobs beyond 710's table, the deny row and the card |
| `scan-scope` (manager, 2026-11-21) | WALK only, not LIBC/PAIR: nothing else was measured (D77) | T-vscan holds on finder row **R7w** only. D1w (a walk, but an unmeasured default) is EXCLUDED ON PURPOSE (F-4; §3.3) |
| `wrap-deny` (manager, 2026-11-21) | the deny `span-vector` is LIVE at both layers | `--memfn=no-span-vector` un-wraps the stretch too, restoring main's bytes at every layer and target |

## CONSTRAINT (above the goals; a ruling, not a quality goal) [rev3]

**SIMD-off is the H64 form, and the wrapper is code organization only:
on the population (§0.1) `rxa_search`'s SIMD-off machine code is
identical to today's, padding normalized (U2b, §2.1).** Where the probe
grid shows a set whose SIMD-off machine code differs, the owner's answer
to `wrap-differs` (§2.2) decides what renders there. No goal below can
trade against this line.

## 0. Goals (ranked; a conflict goes to the higher one)

| # | goal | who benefits | checkable form |
|---|---|---|---|
| G-1 | **Answer identity.** Every artifact answers exactly as today, at every layer, width and target. | every caller | G2 (§10): 0 differences against python `re` and against the family's own reference, on guard-page subjects; the answer-identity sweep's `span-vector` deny arm agrees with the default over the corpus AND the seeded witness list SPAN-SEED (§10.1), whose V-site count is printed and floored |
| G-2 | **The shipped text is the timed text.** Where the table routes a stretch, the machine code gcc makes for `rxa_search` is identical to 710's `avx2-loop` arm. Where a difference remains, it is named and measured. | the 710 verdict's validity (MEASUREMENT-3) | F2 (§6): `objdump` of `rxa_search` identical to 710's `avx2-loop` arm source, addresses normalized, on each of the 82 routed cells of 710's grid. A DIFFERS is listed with its diff, enters C6's population, and blocks the landing until the code round rules it |
| G-3 | **No repeated LOSS where it ships.** The SIMD-on movers keep 710's claim: no repeated LOSS against `--memfn=no-span-vector`. | `-fmemfn-simd` users with long one-class spans | the post-build card C6 run (§8) under the clauses of 710's rule named there before data: 0 repeated LOSS. Wins are reported, not gated [rev3: the "S-pick" clause dropped, F-15] |
| G-4 | **Nothing else moves.** At SIMD-off, and at every target that does not admit `w32`, the only bytes that move are the ones §11 lists. The deny restores today's bytes exactly. | default-build users | the identity gate (§10): the `no-span-vector` artifact equals the merge base's artifact over the corpus and SPAN-SEED, both layers, after the DECLARED mask (the abi-number lines only, a literal list) |
| G-5 | **One table, no parallel mechanism.** The span-form choice is one declared first-match table, and these are its rows. | maintainers (Frank's table rule) | `wf_span_head` is retired. One row array exists. A grep for a second span-form decision finds none. The selector is written by the one writer ofsskip already uses (§5) |

Non-goals: the scalar layer's own block form (D201: "Revisit when the
scalar layer is measured"); a 16-byte (`w16`) rung; the SWAR rung of 708's
cascade (no table row reaches it, §4.4); a periodic span; the LIBC, PAIR,
D1w and floor sites (unmeasured, §3.3); aarch64 (K-4; D147 addendum 8); a
scalar timing of the wrapper (cut by r67, F-14).

### 0.1 Population record (information only, D201 add. 1) [rev3: corrected, F-2]

Rev 2 said 4 sites (corpus 1, bench 3). **The real population is 3 bench
sites, and the corpus holds 0 V sites at any width.** The corpus row
`tests/counterk/counterk.rxt` line 1919, `(?:ab|ba|aa|bb){24}c`, is a
finder-row D1 site (`FF_LIBC`, a memchr find), which `scan-scope`
excludes; it has no window site at width 32. The census script's "scan"
was any site without `rxa_mf1_sh[` (a text proxy), not the table's
predicate (r67 lesson 1: count a site's KIND by the table's own predicate
on the trace record).

| pattern (bench) | finder row (MFTRACE FDROUTE) | k | at width 32 and 4095 |
|---|---|---|---|
| `[0-9a-f]{32}` (bounded/hex32, loglines/hex32-id) | D-hors (HORS), frame E-find | 31 | same |
| `\b[0-9a-f]{32}\b` | D-hors (HORS), frame E-find | 31 | same |
| `\d{32}` (bounded/dig-exact-32) | R7w (WALK), frame E-find | 31 | same |

Command (§16 item 5). Every real site has k = 31: none reaches the B = 32
rung or either upper bound. At the default window width (32) only k 16-31
(window) / 24-31 (scan) is eligible; main's owed cover-width timing
(`cover_cap.md` §11.4 B) decides whether that default rises. D201 add. 2's
population line ("corpus 1 of 6,403") is main's record to correct.

Consequence for the checks: a check that reads its population from the
corpus meets 0 V sites and cannot fail. Every population-read check in
this note reads the SEEDED witness list SPAN-SEED (§10.1) as well, with a
printed count and a literal floor > 0.

## 1. Site map: where it lives today (found by grep)

| what | where (command) | today |
|---|---|---|
| the option row | `grep -n 'span-loop' memfn/src/options.def` → 122 | `MF_OPT("span-loop", MF_OPT_PAIR, MF_B_ANY, MF_L_SCALAR, ...)`. Deny = I, force = L |
| the decision | `grep -n WF_SPAN_HEAD memfn/src/window.c` → 1470, 1476, 1483 | `wf_span_head()` (window.c:1477): an IF CHAIN (deny → I, force → L, lever `span-head=N` → H(N), else H(64)), returned as one head `h` per SITE (`plan_of`, :1491) |
| the segmenter | `grep -n 'wf_loop_len\|static int wf_loop\|wf_test_to' memfn/src/window.c` | `wf_test_to` (:3536) walks the plan in offset order. `wf_loop_len` (:3498) finds a ONE-CLASS STRETCH: consecutive core `KIT_POS_WIDE` entries with one set and one table offer, at offsets ≥ h, never crossing entry `skip`. `wf_loop` (:3517) renders it as one loop |
| who renders it | `wf_test_to`'s callers (`grep -n 'wf_test_to(' memfn/src/window.c` → 3576, 3584): `c_find_test` (E-find) and `wf_test` (E-generic, the floor) | the only two renderers of a candidate test |
| `skip` [rev3] | `grep -n '\*skip =' memfn/src/window.c` → 3977, 3988 | an OUTPUT of the head renderers: `d_hors_head` (HORS: the probed entry, where it is a lone position) and `find_head` (find rows: the stop, where `stop_alone`). Not a plan field today |
| 710's "site kind" | `struct wf_plan` fields `pick` (:1401) and `brow` (:1402); `grep -n 'R7w\|D1w' memfn/src/window.c` | "window" = E-find with pick `FF_HORS` (row D-hors, renderer B-hors). "scan" = E-find with pick `FF_WALK`, whose finder row `w->brow` is **R7w** (710's four scan classes) or D1w (`FB_UNMEASURED_DEFAULT`, reached when an unrelated finder deny refuses D1) |
| the level fact | `grep -n 'art->levels = ' memfn/src/compose.c` → 1102; `memfn/src/levels.def` | `art->levels` = the levels the target admits: `LV_X86_W16` (sse2, x86-64) and `LV_X86_W32` (avx2, x86-64-v3). 0 at `-fno-memfn-simd` |
| the SIMD seam idiom [rev3: ofsskip is the routed precedent] | `ofsskip.c` `fn_level_block` (:707) and `fn_selector` (:727) (D155); `vany.c` `vany_level` (:155), `vany_selector` (:189) (not routed) | `<fn>__body`, one bracketed helper per admitted level, and a selector `<fn>` with ONE call to the top helper. `simd_open`/`simd_close` bracket WHOLE LINES (`src/core/sb.c` `pcrec_sb_simd_open`: "a bracket opened mid-line" aborts). ofsskip sets the level's include bit on the ART at define (`art->includes |= kit_level(...)->includes`, ofsskip.c:712) |
| a table asked at define and at use [rev3] | `memfn/src/runcmp.c` `rc_row_of` (:214), asked by the define's helper declaration and by the compare (:358, :404) | one selection, two askers, one trace phase (MF_PH_RUN): the precedent for §3's evaluation point |
| the header fact | `memfn/src/includes_c.def` | `MF_INC_LEVEL_W32` = `#include <immintrin.h>`, placed by pcrec at file scope, ahead of the region |

**Premise test (the brief's).** The 710 TABLE's "site = window / scan" maps
to facts the kit already has: the plan's frame (`w->skel` is E-find), its
pick (`w->pick` = `FF_HORS`) and its finder row (`w->brow` = R7w). k is
the stretch's length, which `wf_loop_len` computes from `skip` (§3.1). The
SIMD-on layer is `art->levels & (1u << LV_X86_W32)`. No pcrec-side fact
is needed. All of these are the kit's own picks, so facts-only (D157)
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
not Frank's words).** An eligible stretch (§3: HORS with 16 ≤ k ≤ 1000, or
R7w with 24 ≤ k ≤ 64; layer-independent facts) renders **at every layer**
as a call `<p>_mf<h>_vs<j>(S, C)` to a selector, in ofsskip's shape (the
routed precedent; vany has the same shape but is not routed):
- `__body` is today's H64 text of that stretch;
- at a target admitting `w32`, a bracketed helper `__w32` is added (the
  710 form) and the selector's one call names it.

[rev3, F-23] The reason this is not a new cost rests on the CONTRACT:
C18 (c) admits exactly one replaced call per SIMD FUNC, and `limits.md`
§8.3¶1 with D155 add. 2 keeps every size decision on the SIMD-off length.
Frank recalled (this round, through the manager) that the selector shape
is the SIMD organization agreed when the kit used `#if` code (D155, add. 1
Q-R9-10: a working function holds no `#if`; a selector picks the level,
one call per arm). D155 add. 3 then made that single-call shape a
GUIDELINE ("They were more guidelines or goals than hard rules"); what
stands is "no `#if` in the code the kit emits into a function body". The
`#if` is gone today (`limits.md` §8.3¶1: the host's region supplies the
ISA).

OFF and ON then differ only as C18 admits, and the lengths stay those of
SIMD-off. **The cost: SIMD-off bytes move** on eligible stretches. The FORM
is still H64, but its text sits inside a function.

**The wrapper is code organization in source; gcc's machine code can
differ on some sets.** Frank's words (D201 add. 2, verbatim): "the
function goes inline so it's just code organization? If that's true I
don't have a problem with that." The function is `always_inline`, so in
source it is only code organization. What gcc makes of `rxa_search` is a
separate fact [rev3, F-13: corrected; numbers from r67's probes, V8/V12]:
- **On the real population** (the 3 bench sites, §0.1) the shipped
  two-level shape (selector → `__body`) gives SIMD-off `rxa_search`
  machine code that differs in NO instruction from today's (one site
  differs in padding only).
- **On `\w`-like sets it differs**: `\w{17}`, `\w{20}`, `\w{32}` (20-26
  lines). None of these is in the corpus or the bench.
- **On `[+.0-9]{65}`** (num k = 64) the two-level shape is identical to
  today; rev 2's "differs by 440 lines" came from a one-level probe and is
  withdrawn.
- **The inline depth matters.** 710's control arm Hspk is a ONE-level
  wrapper; on num k = 64 it differs from H64@on by 47 lines while the
  shipped two-level shape differs by 0. Hspk's results are therefore NOT
  evidence for the shipped wrapper, and this note no longer cites them.
- At `-fmemfn-simd=x86-64` (w16 only) the machine code equals
  `-fno-memfn-simd`'s for wrapped and unwrapped `\w{20}`/`\w{32}` on gcc
  15.2 (r67 NOTED, MEAS's probe): the SIMD-off reading covers w16 on this
  compiler (not shown for clang).

**Why option B was not taken.** B admitted "a replaced inline expression"
as a third diff kind, keeping SIMD-off bytes and 710's exact text, but it
changes C18 (c)/(b), `tuning.md` §2.43¶4 and pcrec's length accounting (a
kit-to-pcrec fact, or a second OFF render): a seam change outside this
design's remit, with its own architecture note. The reading of D201 add. 2
makes it unnecessary.

### 2.1 The scalar no-loss check: a machine-code census on the BUILT text (§14 U2b) [rev3, F-14]

Rev 2's three parts become one. **Dropped:** the scalar timing (its cell
rule reads a uniform 14 % slowdown as TIE, so it could not return LOSS on
a small wrapper effect: r67 MEAS-5) and T-keep with §2.1 (c) (no
compile-time fact keys a "keep list": §2.2).

**U2b, the census.** On the BUILT U2 text (never a probe: the inline depth
changes the answer, §2), for each pattern below, `objdump -d
--no-show-raw-insn` of `rxa_search` at `-fno-memfn-simd`, the default
(wrapped) artifact against the `--memfn=no-span-vector` artifact (today's
text), both from the U2 binary, gcc -O2:
- **normalization, declared before data:** addresses and symbol offsets
  stripped; padding lines (`nop`, `xchg %ax,%ax`, `data16 ... nopw`,
  `cs nopw`) removed. A diff that survives is DIFFERS with its line count.
- **population:** (1) the real population: the 3 bench patterns (§0.1),
  at widths 32 and 4095; (2) the PROBE GRID: 710's ten classes (`confirm.py`
  `CLASSES`: hex, dig, word, vowel, nonl, hi, af, ident, upper, num) x
  k 16..31 at width 32, i.e. `cls{17}` .. `cls{32}`, 160 patterns, of
  which 128 hold an eligible stretch (6 window classes x 16 k, 4 scan
  classes x k 24..31; §16 item 5) and 32 are non-movers whose diff is 0 by
  construction (the normalizer's own control);
- **floor witness:** `\w{20}` is a KNOWN POSITIVE and must be reported
  DIFFERS; if it is not, the census is red (it cannot see what it is
  for). Each count (patterns compiled, eligible, IDENTICAL, DIFFERS) is
  printed.
- **output:** the DIFFERS list, by class and k, in the build lane's report.
  The census answers "on which sets does the wrapper move SIMD-off
  machine code", which is the fact §2.2's fork turns on.
- **command:** the build lane states it in its report; it is a delivery
  step, not a committed test.

The census is the CONSTRAINT's checkable form on the population (identical
there, or the build stops), and the record the owner's answer reads on
the grid.

### 2.2 OWNER QUESTION `wrap-differs` (OPEN; the build waits on it) [rev3, F-14]

**The fact.** The wrapper changes gcc's SIMD-off machine code on `\w`-like
sets (`\w{17}`, `\w{20}`, `\w{32}`), and on none of the 3 real sites.
That is outside his words as he said them ("If that's true ..."). No
measurement of that change is planned (the timing was cut: it cannot see
the effect). U2b's census will name the full differing set on the grid.

**The question:** is that acceptable as code organization, or should
`\w`-like sets keep today's text?

**The two outcomes, as a stated fork:**

1. **Wrap everything.** Every eligible stretch renders the selector at
   every layer, as §3/§5 say. The differing machine code on `\w`-like sets
   is accepted as code organization, recorded by U2b's census (the list,
   by class and k) and not timed. Nothing else in this note changes.

2. **Do not wrap the sets whose machine code differs.** This needs a
   compile-time fact that says "gcc will make different machine code for
   this stretch". **None exists.** Whether gcc's machine code differs is
   an output of gcc's inliner and register allocator at one version and
   flag set; the kit sees the set, k and the frame, never that outcome.
   The nearest kit fact is a correlate: the number of terms
   `kit_set_test` renders for the set (`\w` renders 4 terms: three ranges
   and one equality; hex and `[0-9]` render 2 and 1; `[+.0-9]` renders 3
   and does not differ). What that implies:
   - a row keyed on a term count would be a per-shape exception chosen to
     fit one gcc's behaviour on the probes known, not a fact about the
     code: a special case (Frank's general-mechanisms rule) that a gcc
     upgrade can silently invalidate. U2b's census would have to become a
     committed check that the keyed set equals the differing set, red on
     any compiler that moves it;
   - the vector helper needs the selector (C18 (c)), so an unwrapped
     stretch also loses V at SIMD-on. `\w`-like sets would forfeit 710's
     measured wins at SIMD-on (710's word and ident classes are among the
     routed window classes);
   - the only way to keep `\w`-like SIMD-off text AND their SIMD-on V is
     option B's seam (§2), which needs its own architecture note.

   So outcome 2 is either a proxy row with a committed census check and
   the SIMD-on win forfeited on those sets, or option B.

**Manager's leaning (for the question's framing, not a ruling):** outcome
1; it is the only one with no proxy and no forfeited win. The owner
decides.

## 3. The selection: THE SPAN FORM TABLE (rows added to the existing choice)

`wf_span_head`'s if chain becomes a declared first-match table. Its rows
are evaluated **per one-class stretch**. The facts:

| fact | where it comes from |
|---|---|
| `opt(span-loop)`, `opt(span-vector)` | the site's opts (`kit_opt_state`) |
| `lever` | the art's `KIT_LEVER_SPAN_HEAD`, test-only |
| `frame` | `w->skel` |
| `brow` [rev3] | `w->brow`, the finder row (D-hors for HORS; R7w / D1w for WALK) |
| `k` | the stretch's length (§3.1), read off `w->skip` |
| `w32` | `art->levels & (1u << LV_X86_W32)` |

Compile-time facts only; no class name.

| row | holds when (first match) | form | origin |
|---|---|---|---|
| T-deny | `no-span-loop` given | I (every position inline) | today, row 1 of the chain |
| T-force | `span-loop` forced | L (h = 0) | today, row 2 |
| T-lever | test-only `span-head=N` | H(N) | today, row 3 (the cards' instrument) |
| T-vwin | frame E-find, brow D-hors, 16 ≤ k ≤ 1000, `span-vector` not denied | V | **NEW**, 710 row 1, MEASURED |
| T-vscan | frame E-find, **brow R7w**, 24 ≤ k ≤ 64, `span-vector` not denied | V | **NEW**, 710 row 2, MEASURED [rev3, F-4: was "pick WALK", which admitted D1w] |
| T-head | always | H(64) | today, the default (`WF_SPAN_HEAD`, MEASURED by cards run fcards-zen4-1) |

[rev3] T-keep is gone (F-14). Under `wrap-differs` outcome 1 the table is
exactly this. Under outcome 2 a proxy row would sit between T-lever and
T-vwin (§2.2); this note does not draw it, because it would be the owner's
call to build.

**V** is the selector call (§5). Its text is layer-dependent; its
selection is not. That is what keeps C18's diff to one replaced call.

The deny `span-vector` is the V rows' option column, in the
`wf_erows[].opt` idiom (`e_opt`): a row whose option is denied does not
hold. The table rides `kit_table` (`{ "wfS", ..., s_holds, s_opt }`), so
MFTRACE names the deciding row, as Table E's do. T-deny, T-force and
T-lever stay ahead of V, for three reasons (and a sabotage plant now
guards the order: §10, plant (e)):
- the escape hatch still means "the text before the forms";
- the sweep's force arm still exercises L at SIMD-on;
- cards C1-C5 re-run unchanged. Their h-arms would silently become V at
  layer "on" if V came first.

**Where the table is evaluated [rev3, F-10].** The E-find DEFINE writes
`__body`, the selector and the bracket (§5), so it needs each V stretch's
LO, K and j BEFORE the use renders in `wf_test_to`. The table is therefore
ONE selection asked twice, at define and at use, as runcmp's `rc_row_of`
is (asked by the define's helper declaration and by the compare); its
trace phase follows runcmp's. Both asks read the same plan facts, so they
agree by construction; the trace build's record of both asks is the check.

**`skip` becomes a plan fact [rev3, F-10].** k needs `skip` (§3.1), which
today is an OUTPUT of the head renderers (`d_hors_head`, `find_head`).
U1 lifts it into the plan: `plan_of` computes `w->skip` from the pick
(HORS: the probed entry where it is a lone position; find rows: the stop
where `stop_alone`), and both head renderers READ it instead of computing
it. One fact, two readers (the renderers and the table): the general
form. U1's identity gate proves the lift moves no byte.

### 3.1 What k is

k is the number of entries one loop would test if L (h = 0) segmented the
plan: `wf_loop_len(w, i, w->skip)` evaluated with head 0. That is the
maximal run of consecutive core `KIT_POS_WIDE` entries from entry i, all
with one set and one table offer, starting at an offset ≥ 0, never
crossing the search-proven entry `skip` or a C-run compare. This is
exactly 710's k: `parse_span` checked that the span covers k consecutive
positions with one test (the probed position excluded). Measured: at the
default width, `[0-9a-f]{17}` has 16 tested positions plus the probe, and
`[0-9]{25}` has the stop plus 24 (§16 item 5).

`wf_loop_len` gains the head as a parameter (k is read with head 0, the
H rows render with their own h); `w->head` retires into the H rows. Where
T-head (or T-lever, T-force, T-deny) decides, the stretch renders exactly
as today: lone tests below h, a loop from h on. So the per-stretch
evaluation reproduces today's bytes for every non-V stretch. The build
proves the refactor with an identity gate (unit U1, §14).

### 3.2 Where 710's rows generalize, and how far this note lets them

- **Several stretches in one site.** 710's patterns hold one stretch each,
  and so does every real site (§0.1). SMALLEST FORM (R-4): V renders for
  the site's FIRST eligible stretch only, and any later one falls to
  T-head (answer-identical). A second eligible stretch needs a width above
  32 (`[0-9a-f]{20}[g-z]{20}` at width 4095: two eligible stretches, k 20
  and 19; at width 32 it is E-stmt), and a pin cell guards the rule (§10).
- **Default width.** 710 ran at `--window-search-width=4095`. At pcrec's
  default width (32) a window site holds at most 32 positions, so k ≤ 31.
  `[0-9a-f]{17}` and `[0-9]{25}` are byte-identical at both widths (§16
  item 5), so 710's k = 16..31 cells ARE the default-width text.

### 3.3 What the rows deliberately exclude

710's harness called every non-HORS site "scan". Every scan cell it timed
was a walk on finder row R7w. The declared table's words ("skips to a
member byte") also cover memchr finds (LIBC, LIBC_BACK), PAIR and D1w.
Those were not measured.

T-vscan therefore keys on R7w alone (`scan-scope`, FREEZE NOTE).
[rev3, F-4] D1w is a walk too, but an unmeasured default
(`FB_UNMEASURED_DEFAULT`), reached when a finder deny refuses D1:
`x[0-9]{26}` is D1 by default and D1w under `--memfn=no-fd-d1`, k 26 (§16
item 5). Keying on the pick would let an unrelated finder deny move a
site into an unmeasured V cell. Excluded on purpose (D77).

The floor (E-generic) and the legacy rows (E-func, E-stmt) never reach
`wf_test_to`'s span path with a pick, so T-head holds there.

A target admitting only `w16` (`-fmemfn-simd=x86-64`) gets the selector
calling `__body`. SSE2 has no `pshufb` for the 16-byte rung, and no `w16`
form was measured.

## 4. The form's emitted C text (708's avx2-loop, as 710 timed it)

### 4.1 Per stretch, inside the `w32` bracket

Names follow the family's `<prefix>_mf<handle>_*` rule. `j` is the
stretch's index within the site. `B` = 32 where K ≥ 32, else 16.

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

- **[rev3, F-5] Lane order.** `_mm256_set_epi8` takes the HIGHEST lane
  first. Each 16-byte half of a table is written `t[15], t[14], ..., t[0]`
  (spike708's reading), as the `bit` table already is (`-128` is lane 7's
  `1 << 7`). Written in index order, 14 of 16 test sets answer wrong (r67
  SOUND-1). A table value > 127 is written as its signed char value
  (`-128` for 0x80).
- At B = 16 the block helper is `nib_blk`'s `sse` text: `__m128i`, `_mm_`
  names, one table copy each (`_mm_set_epi8`, highest lane first).
- `lo_t[l]` = the bits `1 << h`, for the high nibbles h in 0..7 such that
  `(h << 4 | l)` is in the set. `hi_t` is the same for h in 8..15, bit
  `1 << (h - 8)` (`spike708.py` `nibble_tables`).
- The kit computes both tables in C from the stretch's 32-byte set
  (`w->set[i]`). It never reads a class name or the C-table offer: an
  offered table's set equals `w->set` (`offer_at` requires it), so the
  answers agree.
- **[rev3, F-8] The renderer asserts K ≥ 16** (a `kit_fail` abort, not a
  decline): §4.2's bound argument has no B below 16 (§12).

**What differs from the timed text, and why it is harmless:**
- the identifiers: renamed;
- the 710 harness's `/* blockconfirm ... */` comment: dropped;
- the `target("avx2")` and `target("ssse3")` attributes: dropped. The
  region supplies the ISA (unit U2, ofsskip's idiom). Dropping them was
  machine-code identical on 6 of 6 probes (§16 item 6);
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
  (the largest of 32, 16 that is ≤ K). **This needs K ≥ 16** [rev3, F-8]:
  below 16 there is no B, and a B = 16 block would read below p (r67's
  plant at k 15: a fault at a start guard page). T-vwin's lower bound is
  therefore a safety precondition as well as a measured bound, and the
  renderer asserts it.

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
any set, the empty set and the 255-byte `[^\n]` included; r67 SOUND
hand-executed it on 16 sets x 14 K with 0 differences). `pshufb` zeroes a
lane whose index has bit 7 set. b0 covers high nibbles 0..7, and b1 covers
8..15 through the XOR. `bit` = `1 << (hn & 7)`. A byte is a member iff
`bm & bit` ≠ 0.

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
  inside the region, after the `_sh` table. It knows each V stretch from
  the table's define-time ask (§3).

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

- **[rev3, F-6] `unused` on `__body`'s header at EVERY layer.** At w32 the
  selector calls `__w32`, which never falls back, so `__body` is an
  unreferenced static: clang `-Wall -Wextra -Werror` (the house GENCFLAGS
  under CLANGGEN=1) errors on it; gcc is silent. The attribute is on the
  OFF line too, so the OFF and ON header lines stay identical (C18 (c)).
- **`always_inline` is load-bearing** (G-2): F2 was machine-identical 9 of
  9 with it (r67 MEAS). It is why C18 needs an amendment (§10, F-1).

**At a target admitting `w32`:**
- §4.1's two functions are written between `simd_open(LV_X86_W32)` and
  `simd_close`, ahead of the selector;
- the selector's one line becomes the bracketed
  `    return rxa_mf1_vs0__w32(rxa_mf1_s, rxa_mf1_c);`, which is C18 (c)'s
  replaced call verbatim;
- **[rev3, F-10] the include:** the level block sets the level's include
  bit on the ART at define, `art->includes |= kit_level(LV_X86_W32)->includes`,
  exactly as ofsskip's `fn_level_block` does; pcrec writes
  `<immintrin.h>` at file scope ahead of the region. The window PLAN's
  `includes` does not gain a level bit (no class carries one today);
- the site's `MEMFN_FORMS` token is `span-vector@w32`;
- `<PREFIX>_SIMD_GUARDED_BYTES` counts the bracket.

**One writer [rev3, F-11].** `vs<j>`'s selector and level block are the
third member of a family written twice already (`fn_selector` /
`fn_level_block` in ofsskip.c, `vany_selector` / `vany_level` in vany.c).
Decided: V does NOT add a third writer. U2 lifts ofsskip's two writers
into one shared kit helper taking the function's head (return type,
attributes, parameters) as an input, and both ofsskip and V call it.
ofsskip's bytes do not move (U2's identity gate over the corpus covers its
sites). That one writer is also the one place F-1's spelling question is
decided (the head is an input, C18 reads the same family). vany (not
routed, its own helper shapes) joins at its next touch, filed as a
ride-along, not built here (R-4).

The `__body` text is today's renderer, unchanged: `wf_pos_test` and
`wf_loop` with the stretch's offsets. The H64 form at the scalar layer is
kept, moved into a function.

**The guarded bound.** One stretch's bracket is constant per (B, set)
apart from three decimals: about 1.3 KB at B = 32. The 16-B rung is
smaller (UNMEASURED; the build measures the largest instance and records
it).

V renders at most once per site (§3.2), so one site's bracket is one
stretch's text. That makes it constant apart from the decimals in LO and
K, and so it is a fixed bound, not a cap with a decline path.
`guarded_max` is the largest instance plus a small headroom, CHOSEN and
labelled so. It gets a row `span-vector-w32` in
`tests/memfn/simd_bounds.tsv`, and a `limits.md` §8.3¶3 sentence names
it.

## 6. MEASUREMENT-3: how the shipped text is matched to the timed text

The reviews' premise: "rxs_span always_inline + immintrin.h IS the text the
kit would ship". The build closes it in two steps. The first needs no timing.

| step | how | what it closes |
|---|---|---|
| **F2, machine-code fidelity** (a delivery check, run once by the build lane and recorded in its report; not a committed test) [rev3, F-17] | **population: the 82 cells of 710's grid the table routes** (by 710's site kinds: 6 window classes x 11 k in 16..1000 = 66, and 4 scan classes x 4 k in 24..64 = 16; `confirm.py` `CLASSES`, `SITE_EXPECT`, `KS_OLD` + `KS_NEW`). The build lane re-counts the routed set from the SHIPPED trace (FDROUTE row and k) and reports any cell where the two counts disagree. For each: `objdump -d` of `rxa_search`, addresses normalized, the shipped `-fmemfn-simd=x86-64-v3` artifact at width 4095 against 710's `work/src/<pat>.avx2-loop.c`, same gcc and flags. There is no `.H64` source (work/src holds avx2-loop, avx2-ool, Hspk, Hspk-ool, prof); the 48 unrouted cells are not compared | the inlined machine code is what was timed. r67 matched 9 of 9 (B 16 and 32, HORS and WALK, k 16..1000). **Landing rule, before data:** any DIFFERS on a routed cell is listed with its diff, enters C6's population, and blocks the landing until the code round rules it |
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
  at both settings (`wrap-deny`, FREEZE NOTE): it un-wraps the stretch
  too, so `--memfn=no-span-vector` restores main's bytes exactly at every
  layer and target. It is the wrapper's escape hatch and its control.
- **[rev3, F-21] What is on by default.** The VECTOR HELPER is off by
  default, because `-fmemfn-simd` is OFF by default and the helper renders
  only at a `w32` target. The WRAPPER and its deny are live in the default
  build: every eligible stretch is wrapped at `-fno-memfn-simd`.
- **Spec:** `registry.md` §6¶8a gains the row. §6¶8b's `memfn` section
  floor goes from 14 to 15.

## 8. The measurement card (same change; Frank 2026-10-23)

**Card C6 `span_vector`** in `memfn/tests/span_forms/cards.py`, and the
append-only row `kit span_vector 8 form;pat;regime;layer ratio cards.py C6
...` in `memfn/data/cards/kit-grid.tsv` (`kit-grid@8`). The row is visibly
UNMEASURED until a box runs it.

[rev3, F-15] Written before data:
- **What it measures: the SHIPPED trade.** On ONE binary, at
  `-fmemfn-simd=x86-64-v3`: `V` (default) and `H64@on`
  (`--memfn=no-span-vector`). The deny changes the wrapper, the body and
  the TU (`<immintrin.h>`, stamps) together; C6 times that combination on
  purpose, because G-3 is about what the caller gets. It does not isolate
  the wrapper from the body.
- **Patterns, each with its width stated:**
  - the 3 real sites (§0.1), width 32;
  - window k 16 and 31 at width 32; k 32 and 1000 at width 4095;
  - scan k 24 at width 32; k 64 at width 4095;
  - every F2 DIFFERS pattern, at width 4095.
  The outside-bound cells (window k 15, 1001; scan k 23, 65) are CUT: both
  arms render today's bytes there, so they are A/A by construction (the
  T-table pins check the flip in text, §10). 710 already timed the
  interior; the card re-times the shipped text at the bounds and on the
  real population, and adds nothing beyond that (R-4).
- **Regimes.** The cards' six regimes, plus near-miss-in at the window
  sites.
- **Which clauses of 710's rule apply.** The cell rule (FLOOR = max(0.15,
  spread(A), spread(B)); WIN / LOSS / TIE), the re-time, the N/A rule, the
  CPU-quiet control: apply unchanged. The CONTROL clause (Hspk) does not
  apply: no shipped lever renders the wrapper alone at SIMD-on, and Hspk's
  one-level wrapper is not the shipped shape (§2). The S (busy) clause is
  dropped with G-3's S-pick line; no profile arm is declared.
- **What replaces the A/A line:** an A/A arm, the `no-span-vector` exe
  timed as both arms on each C6 pattern (one binary, fresh layouts, no new
  lever); its repeated-LOSS-or-WIN rate is printed beside the verdict, as
  710's A/A line was.
- **The rule's sha** is recorded with the result.
- **`deps` [rev3, F-16].** `kit:form.span-vector=<hash>`. formhash
  entries are kit facts over six shapes (FIND .. OFS), and none builds a
  window site with a long one-class stretch; a pcrec pattern spelling has
  no meaning there. So this is a NEW formhash SHAPE (a window site with one
  stretch of a stated set and K), its renderer, and one entry (the
  canonical instance: the hex set, K 40, x86-64-v3), so a later text change
  stales the row. Counted in §17.

**What it settles.** G-3 on the shipped text. The SIMD-off wrapper is not
timed anywhere (F-14): U2b's census is its record. A Zen 1 run of C6
(ubuntubudu: AVX2 split into 2x128) is the D144 addendum 4 reading on
other hardware; it is unmeasured and may move the lower bounds (§12:
never below the safety floor 16).

Filed as PLAN rows with a trigger, NOT build scope (F-15): a
`--harness=span-vector=force` lever (V outside the bounds) and a
`span-vector-body` lever (the wrapper alone at SIMD-on). Trigger: a bound
is questioned by a C6 or Zen 1 run.

## 9. The same-commit abi package (D76/D94, D146/D147)

### 9.1 The bump

"The next number at landing" (`docs/design/CLAUDE.md`): main is at **109**
today (§16 item 1). Lane L3 (`2026-11-20-r65-l3feat`) is taking 109 → 110,
so this build is likely **111**. The build lane re-greps at its landing
base.

### 9.2 The re-pins, readers found by grep at the landing base [rev3, F-12]

The command: `git grep -n -w <N> -- src tests docs/spec docs/testing.md
memfn`, and **review every hit by hand, unfiltered**. A filter such as
`| grep -i abi` drops a reader: `match_api.md` §6¶17 ("It is `109` on
every artifact pcrec emits today") does not say "abi" on its line (the D94
failure mode). At 109 the unfiltered grep returns many unrelated hits
(PCRE2 error 109, timing figures); the readers among them are:
- `src/gen/emit_dfa.c` `PCREC_ARTIFACT_ABI`;
- `docs/spec/match_api.md` §1's K80 guard, its three lines (`!= N`, the
  `#error` text, `#define PCREC_RX_ABI_H N`);
- `match_api.md` §6's `abi` table row, and §6¶17's sentence;
- `tests/codegen/run_codegen_tests.sh` `ABI_EXPECT`;
- `tests/mech/sabotages/S693_abi_not_bumped.sh` `SAB_BEFORE`, re-aimed;
- `tests/codegen/run_recursion_identity.sh` FILEPIN/ABASEPIN, the (B) pin,
  self-pinned to the lane's last src commit (the r65 CONTRACT-1 lesson);
- `docs/dev/history/abi_changelog.md`.

Then run the suites that count: registry, codegen, rxtsource
(the D94 addendum).

### 9.3 Stamps and pins

- `MEMFN_FORMS` gains the token `span-vector@w32` (opaque to pcrec).
- `SIMD_GUARDED_BYTES` rises on SIMD-on movers.
- `simd_bounds.tsv` gains a row.
- `emit_sweep.py`'s `DIFFER_PINS` gains floors for the deny arm at both
  layers, over SPAN-SEED (§10.1): the corpus alone has 0 movers.
- The start-set and size tripwires move only if a corpus artifact's size
  moves. The corpus has 0 V sites today, but `make test` is owed in full,
  not one section (BOILERPLATE's delivery bar).

`MF_SITE_ABI`: unchanged, since the site carries no new field.
`MF_CLASS_V` [rev3, F-10]: unchanged, because the level include bit rides
the ART (ofsskip's idiom, §5), not the window plan class. Rev 2's reason
("the plan class already carries a level bit") was false: no class
carries one today. The trace build's asked-vs-defined `includes`
comparison is the check that the plan class did not move.

### 9.4 G1 alpha (integration.md §17.2) [rev3, F-22]

- **Population.** pcrec-side: a script diffs each artifact's default
  compile against its `--memfn=no-span-vector` compile, over the corpus,
  the bench patterns and SPAN-SEED, at `-fno-memfn-simd` AND at
  `-fmemfn-simd`. It never reads the kit's `moved`. The manifest is
  written before any timing, with its count.
- **Bins** (op, length decade), floor 8. The real population is 3 movers,
  so every bin is UNREACHED at both layers by construction.
- **No timing window is booked.** The build delivers the manifest and the
  dry run (count printed, UNREACHED printed). Trigger to time: a bin
  reaches 8 real movers (the default width rises, or patterns land in
  range). D147's "both layers" reading is met at SIMD-off by U2b's
  machine-code census where the code is identical; at SIMD-on by C6.

### 9.5 The spec hunk, the same change (D80)

| file and section | change |
|---|---|
| `registry.md` §6¶8a, ¶8b | the row; the floor |
| `tuning.md` §2.43¶3a | "What On renders" gains the vector span |
| `tuning.md` §2.43¶3b | its switch |
| `tuning.md` §2.43¶3d | the window search's denies: the wrapper at both settings, under A |
| `limits.md` §8.3¶3 | the per-form bound |
| `match_api.md` §6 | through the abi ritual |

`docs/guide/` points at the spec and does not restate it.

## 10. G2 and the checks (each control independent of the generator)

### 10.1 SPAN-SEED, the seeded witness list [rev3, F-3]

Every population-read check (the identity gate, G-1's deny-arm sweep,
C18's floor, G1's population, `DIFFER_PINS`) reads SPAN-SEED as well as
its usual population. The list is literal, committed with the checks, and
written before the build:
- the 3 bench patterns (§0.1);
- the T-table pin cells (below);
- a slice of 710's grid: each of the ten classes at k 16, 24, 31
  (`cls{17}`, `cls{25}`, `cls{32}`), 30 patterns.

Each check runs SPAN-SEED at widths 32 and 4095, prints its count of V
sites (by the trace record's FDROUTE row and k, never a text regex), and
fails below a literal floor. The list holds 41 distinct patterns (3
bench + 11 pin patterns + 30 slice, less 3 that coincide: the slice's
`[0-9a-f]{17}`, `[0-9]{25}` and `[0-9a-f]{32}` are also a pin or a bench
text). **Floors, derived by the table's predicate on the trace build (§16
item 5):** at width 32, 28 V sites (the slice's 26: 6 window classes x 3
+ 4 scan classes x 2, plus the bench's `\b[0-9a-f]{32}\b` and `\d{32}`);
at width 4095, 31 (the 28 plus the pins `[0-9a-f]{1001}`, `[0-9]{65}`,
and `[0-9a-f]{20}[g-z]{20}`'s first stretch).

### 10.2 The checks

| check | subject | control (shares no source with the kit) | population count (K35) |
|---|---|---|---|
| **G2-V unit** (new section of `run_g2_win.sh`, x86-64-v3 arts) | every V rendering over a generated space: sets of 1..8 ranges in both polarities, sets with bytes ≥ 0x80, the empty set, a 255-member set, single-byte-removed sets; k at every rung edge (16, 17, 31, 32, 33, 63, 64, 65, 999, 1000) and random interior k | python: `all(re.fullmatch(cls, bytes([b])) for b in window)` with the class written in the TEST, never the kit's set. Windows flush against a `PROT_NONE` page at both ends (708's `check_tu`), so a read past p + K or below p faults | per rung, per row: literal floors |
| **G2-V whole** | `cls{k+1}` and mixed patterns (a literal run plus a stretch, two stretches, a stretch beside a non-core position) compiled at SIMD-on and SIMD-off, find-all | python `re` over the cards' regimes, plus forced near-miss staircases (a failing index at each of 0..k-1, at the first window and after a match: 710's FIDELITY-1) | per site kind: literal floors |
| **T-table pins** [rev3, F-18] | the row bounds AND the brow, frame and once-per-site columns | a literal cell list in the test, each with its width, read off the rendered text (the count of `__w32` calls), never off window.c: HORS `[0-9a-f]{16}` / `{17}` (k 15 absent / 16 present; widths 32 and 4095), `[0-9a-f]{1001}` / `{1002}` (k 1000 present / 1001 absent; 4095); R7w `[0-9]{24}` / `{25}` (k 23 absent / 24 present; 32 and 4095), `[0-9]{65}` / `{66}` (k 64 present / 65 absent; 4095); **brow:** `ab[0-9]{26}` (D1, k 26: absent; 32), `[xy][0-9]{26}` (PAIR: absent; 32); **frame:** `[0-9a-f]{20}[g-z]{20}` at width 32 (E-stmt: absent); **once per site:** the same pattern at 4095 (two eligible stretches: exactly one `__w32` call) | 12 cells, every one reached (its fd row checked by the trace) |
| **Identity gate** (G-4) [rev3, F-3] | `--memfn=no-span-vector` artifact on the U2 binary vs the artifact of the lane's MERGE BASE, built once (never "main", which moves) | byte diff, both layers, over the corpus and SPAN-SEED. **Mask, declared before data:** exactly the abi-number lines, a literal list of their four spellings (the artifact header's `(abi N)`, `#if ... != N`, the `#error` text's `(abi N)`, `#define PCREC_RX_ABI_H N`; `match_api.md` §1, §6). Nothing else is masked | count printed; 0 differences expected |
| **C18 / simdfloor, AMENDED** [rev3, F-1] | a unit of its own in U4 (below) | its own rule (C18 (c)), with its own controls | its per-target SIMD FUNC floor rises, plus the NAMED span witnesses' literal floor |
| **F2** (delivery check) | §6 | 710's arm sources | 82 routed cells |

**The C18 amendment [rev3, F-1].** C18 is not "unchanged": its regexes
(`tests/memfn/simd_floor_check.py` `SELECTOR`, `HELPER`) match only
`static inline size_t ...`, while V spells `static inline
__attribute__((always_inline)) int ...` (and `__body` adds `unused`). On a
hand-built ON text it found 0 selectors and 0 helpers and reported every
V mover's deleted line as "no SIMD FUNC's floor call" (r67 V1). Its -O0
leg (C9-x86) requires `<fn>__w<VW>` as a defined symbol in the -O0
object, and an `always_inline` static is never emitted there (§16 item
6c). The amendment, as one unit with its controls (learnings §3):
- **spelling:** SELECTOR and HELPER accept the head family the one writer
  (§5) emits: `static inline` with an optional `__attribute__((...))`
  list naming `always_inline` and/or `unused`, returning `size_t` or
  `int`. The `__w32_b` block helper is a HELPER for the exclusivity lint
  (it lives inside the bracket);
- **the -O0 rule for `always_inline` helpers:** the `nm` test does not
  apply (no symbol exists by construction). In its place: (i) the -O0
  compile succeeds (gcc refuses to inline an `always_inline` AVX2 helper
  into a function outside its target: "inlining failed ... target specific
  option mismatch", §16 item 6c), and (ii) `objdump -d` of the -O0 object
  shows a `ymm` register in the function that calls the selector;
- **NAMED span witnesses** in C18's population: `[0-9a-f]{17}` (HORS,
  k 16, B 16) and `[0-9]{25}` (R7w, k 24), each with one `vs0` selector at
  x86-64-v3; literal floor: 2 span SIMD FUNCs, written before the build;
- **controls:** a plant that drops `always_inline` from `__w32` makes leg
  (ii)'s ymm reading change and the -O0 `nm` path find a symbol (the rule
  must not silently pass both shapes); a plant that moves `__w32` outside
  the bracket makes (i) fail; a plant that names a non-admitted level
  makes the guard lint fire. Each is a mech row with a REACH witness.

**Sabotage rows** (mech, each with a REACH witness, [MECH-REACH]):

| plant | what it breaks | caught by |
|---|---|---|
| (a) | a nibble table drops a member (708 `nib_drop`) | G2-V unit |
| (b) [rev3, F-7] | the final block reads 1 B past (708 `past`). Witness: a **WALK** whose stretch ends at the pattern end, subject flush at the end (`[0-9]{25}`). On HORS the byte past the stretch is the probe, in bounds and a member, so the plant is benign there (r67: 0 of 1100 answers differ on `[0-9a-f]{32}`) | the guard page |
| (c) | T-vwin's lower bound becomes 15 | T-table pins, the renderer's K ≥ 16 assert, the start guard page, the staircase (three ways, r67 MEAS-3) |
| (d) | the deny is ignored at SIMD-off | identity gate, over SPAN-SEED (the corpus alone holds no V site, so it could not see the plant: S3281's own header records this lesson) |
| (e) [rev3, F-9] | V evaluated before T-lever / T-force (the order §3 claims) | G2's head-pass loop pins on an eligible stretch (SPAN-SEED's k 16 HORS cell) under `span-head=N`; the build lane names the detecting check with the REACH witness |

**Re-aims at U1 [rev3, F-9].** U1 deletes or changes the anchors of five
existing rows; U1 re-anchors each onto the table's rows and re-proves its
REACH at U1 (not only at U6):
- S3278 (force ignored), S3279 and S3282 (the lever ignored / read as 0),
  S3281 (deny ignored): anchored in `wf_span_head`, which retires; they
  move onto T-force, T-lever and T-deny;
- S3280: anchored on `if (w->off[i] < w->head) return 0;` in
  `wf_loop_len`; `w->head` retires, so it moves onto the H rows' head;
- S3277: stays textually in `wf_loop_len`, but the function's meaning
  changes (k is read with head 0; the head is a parameter), so its plant
  and witness are re-checked.

`REACH_ONLY=1 bash tests/mech/run_sabotage_matrix.sh` runs at U1 and
before delivery, since a new row fires in new places (BOILERPLATE).

## 11. Expected movers (which sites' bytes change) [rev3, F-19]

The classes below are byte-encoding sets. Under `-e utf8` the hex sets are
WALK (R7w), so the hex family moves only at `{25}`..`{32}` there.

| setting | moves | does not move |
|---|---|---|
| every artifact | the abi number lines | — |
| `-fno-memfn-simd` (the default build), default width | artifacts whose window site is E-find D-hors with a one-class stretch of 16..31 positions, or E-find R7w with a stretch of 24..31 (e.g. `[0-9a-f]{17}`..`{32}`, `\w{17}`..`{32}`, `[^\n]{17}`.., `[0-9]{25}`..`{32}`, `[A-Z]{25}`..`{32}`). The walk calls `vs<j>`; file scope gains `__body` and the selector | `[0-9a-f]{16}` (k 15), `[0-9]{24}` (k 23), any 33+ position pattern (no window site at the default width), LIBC finds (`x[0-9]{26}`, `ab[0-9]{26}`), PAIR finds (`[xy][0-9]{26}`), D1w walks, floor and legacy sites, every VM/DFA body text |
| `-fmemfn-simd=x86-64-v3` | the same artifacts, plus the bracketed `__w32` helpers, the selector's replaced call, `<immintrin.h>` ahead of the region, `MEMFN_FORMS` `span-vector@w32`, `SIMD_GUARDED_BYTES` | as above |
| `-fmemfn-simd=x86-64` (w16 only), `generic` | as `-fno-memfn-simd` (wrapper, no helper) | — |
| `--window-search-width=W` > 32 | D-hors with 16 ≤ k ≤ min(1000, W - 1); R7w with 24 ≤ k ≤ 64 | k > 1000 (HORS), k > 64 (WALK): H64 |
| `--memfn=no-span-vector` | nothing: main's bytes, every setting | — |

Over the corpus the default build moves no artifact but the abi lines (0
V sites, §0.1); the bench moves 3. G-4's "G1 population equals §11's
mover classes" is counted over SPAN-SEED. This lane runs no sweep.

## 12. Constants register (Frank: unroll widths, block sizes, cut-overs are suspect)

| constant | label | source |
|---|---|---|
| 16 (HORS lower bound) [rev3, F-8] | MEASURED and DERIVED: 710's bound, and the smallest rung (§4.2: below 16 no block fits). A re-measure may RAISE it, never lower it | 710, rule `6351bff3901e3955`; §4.2 |
| 1000 (HORS); 24, 64 (WALK) | MEASURED | 710, rule `6351bff3901e3955` |
| 64 (H's head) | MEASURED | cards run fcards-zen4-1, unchanged |
| B ∈ {32, 16} | DERIVED: the level's vector width and its half; the largest that fits in k, so no read leaves the span | §4.2 |
| the loop shape (not unrolled) | MEASURED as a form: 710 timed `loop`. 708's `unr` and `loop2` were other arms, not shipped | 708/710 |
| `guarded_max` (`span-vector-w32`) | CHOSEN, UNMEASURED DEFAULT, a cap by construction | §5 |
| SPAN-SEED floors 28 / 31 | DERIVED: the table's predicate on the trace build | §10.1, §16 item 5 |
| `SWAR_MAX_RANGES` | not shipped (no row reaches SWAR) | §4.4 |

## 13. The three standing questions

1. **The measurement regime (RELEVANT).**
   - **710's regime:** Zen 4 7700X (the dev box), gcc 15.2, glibc, CPU 15
     pinned with a quiet sample, throughput (ns/B, find-all, 1 MiB
     subjects), six regimes plus near-miss-in, x86-64-v3,
     `--window-search-width=4095`, fresh layout pools, A/A 6/448.
   - **What could flip a row:**
     - Zen 1 (2x128 AVX2) could raise the k at which V wins, near the
       lower bounds (never below 16, §12);
     - another compiler (clang: unmeasured, its region is a different
       pragma);
     - a latency regime (one short call) is not what 710 timed: its
       not-warm and short-subject regimes are the cards' approximations,
       void by method.
   - **SIMD-off is not timed** (F-14): its record is U2b's machine-code
     census, a compile-time reading at one gcc (15.2, -O2). Another gcc
     could move which sets differ; the census is re-run when the house gcc
     changes (§2.2 outcome 2 would make it a committed check).
   - The default width is not a regime change: the text is identical
     (§3.2).
   - The official verdict is the planned bench run on the targeted
     hardware, via main (D144 addendum 4).
2. **The independent control (RELEVANT).** §10:
   - the answers are checked against python `re` and python per-byte
     membership, never the kit's set;
   - the row bounds and columns against a literal cell list, read from
     the text;
   - the population comes from pcrec's diff (default vs deny), never
     `moved`, over the corpus AND SPAN-SEED, with literal floors (the
     corpus alone is empty, F-3);
   - the identity gate's reference is the merge base, built once; its
     mask is declared before data;
   - fidelity against a different generator (spike708) and 710's own arm
     sources;
   - the census has a known-positive floor witness (`\w{20}`);
   - every sabotage plant has a reach witness.
3. **What moves when the data is regenerated (RELEVANT).**
   - The table's bounds are constants in window.c, not a data file. A
     re-measure that moves them (a C6 run on other hardware, a re-run of
     710's rule) moves emitted bytes. That is a kit byte move, so it is a
     pcrec abi event plus a spec check (the registry row's doc names no
     bound, so it stays). SPAN-SEED's pin cells and floors move with them.
   - `kit-grid@8` is append-only.
   - The `span-vector` form hash moves with any change to §4.1's text,
     staling the C6 row.
   - No calibration or measure-set row prices V. It is a rule row, not a
     priced choice.

## 14. The build units, in order

**The build waits on `wrap-differs` (§2.2).** Outcome 1 is the units
below as written; outcome 2 adds a proxy row and makes U2b a committed
check, or goes to option B (a separate note).

| unit | what it does | moves bytes? |
|---|---|---|
| **U1** | The table refactor: `wf_span_head` becomes THE SPAN FORM TABLE (T-deny, T-force, T-lever, T-head), evaluated per stretch and asked at define and use (§3); `skip` lifted into the plan; `w->head` retired; `wf_loop_len` takes the head. The five sabotage re-aims (S3277-S3282) with REACH at U1. An identity gate: every corpus and SPAN-SEED artifact byte-identical to the merge base at both layers, both engines. A refactor gets no flag (Frank 2026-10-29) | no |
| **U2** | The wrapper (option A): `vs<j>` + `__body` + selector for eligible stretches at every layer through the ONE writer lifted from ofsskip (§5; ofsskip's bytes unchanged), and the deny row `span-vector` (both layers). The identity gate against the merge base for the deny arm, with its declared mask. The first abi event lands here | yes |
| **U2b** | **The scalar no-loss check** (§2.1): the machine-code census on the BUILT U2 text, padding normalized, over the real population and the 160-pattern probe grid, with `\w{20}` as the floor witness. Identical on the population, or the build stops; the grid's DIFFERS list goes into the report | no |
| **U3** | The `w32` helper: §4.1's text bracketed (lane order per F-5, the K ≥ 16 assert), the selector's replaced call, the include bit on the art, the form token, the guarded bound and `simd_bounds.tsv`, the `limits.md`/`tuning.md`/`registry.md` hunks. F2 recorded before anything else | yes (SIMD-on) |
| **U4** | G2-V (unit, whole), the 12 T-table pin cells, SPAN-SEED and its floors, sabotage rows (a)-(e) with reach, **the C18 amendment** with its controls and named span witnesses, `DIFFER_PINS` floors | no |
| **U5** | Card C6 (its patterns, widths, A/A arm and rule clauses as §8 states) + `kit-grid@8` + the formhash SHAPE, renderer and entry; `cards.py plan`/`dry` green, with no timing | no |
| **U6** | The abi package at the landing base (§9.2, the unfiltered grep), `make test` async, `make test-axes`, REACH_ONLY. Then G1's manifest and dry run (no timing window, §9.4); C6's timing owed to main's window | — |

The design round (r67) preceded this revision. The code round precedes
the landing (Frank 2026-11-15). U2 and U3 may share one abi event if they
land together; the number is taken once.

## 15. Open questions

1. **`wrap-differs`: OPEN, the owner's** (§2.2). The build waits on it.
2. Owed to main, not blocking: the cover-width timing (`cover_cap.md`
   §11.4 B) decides whether the default window width (32) rises, which
   widens the eligible range from k 16-31 / 24-31 to the 710 table's
   16-1000 / 24-64.
3. Main's, not this note's: D201's provenance pointer for "build with simd
   layer" (F-24, decisions.md), and D201 add. 2's population line (F-2).

Resolved earlier, restated in the FREEZE NOTE: `scalar-wrap` (read as
option A), `scan-scope`, `wrap-deny`, R-4.

## 16. TODAY NUMBERS (each with the command that produced it)

Rev 3 re-derived items 5, 6c and the finder rows at the lane's build of
lane/bspan3 (`nice make -j2`; memfn/src identical to main's), plus a
traced pcrec (memfn/src/*.c compiled `-DMF_TRACE -O1`, linked as
`tests/memfn/rows_check.py` does) in `$PCREC_TMPDIR/scratch/bspan3/tr/`.
Item 1 re-checked at main `248f3cff6`. Other items are rev 1's (main
051e78af2), unchanged.

1. **abi 109.** `git -C /home/pcrec/projects/pcrec grep -n 'define PCREC_ARTIFACT_ABI' main -- src/gen/emit_dfa.c` → `src/gen/emit_dfa.c:55:#define PCREC_ARTIFACT_ABI 109`. Readers: `git -C /home/pcrec/projects/pcrec grep -n -w 109 main -- src tests docs/spec docs/testing.md memfn/src memfn/tests`, reviewed by hand (§9.2): emit_dfa.c:55; match_api.md §1 (three K80 lines), §6's table row and §6¶17; run_codegen_tests.sh `ABI_EXPECT=109`; S693 `SAB_BEFORE`; the rest are PCRE2 error 109 and unrelated figures.
2. **`memfn` section floor 14.** `git -C /home/pcrec/projects/pcrec grep -n 'memfn. section floor' main -- docs/spec/registry.md` → `[6¶8b] ... floor: 14`.
3. **Head 64, the if chain.** `grep -n WF_SPAN_HEAD memfn/src/window.c` → 1470 (`enum { WF_SPAN_HEAD = 64 }`), 1476, 1483. The chain is `wf_span_head`, window.c:1477-1484.
4. **Levels.** `grep -n '^MF_LEVEL' memfn/src/levels.def` → `LV_X86_W16` (sse2, x86-64) and `LV_X86_W32` (avx2, x86-64-v3); no others.
5. **Finder rows, k and the population** [rev3]. The command, per pattern P and width W: `$PCREC_TMPDIR/scratch/bspan3/tr/pcrec_trace -p rxa --features all -fmemfn-simd=x86-64-v3 --window-search-width=W -o /dev/null --pattern P 2>&1 | grep -o 'MFTRACE FDROUTE[^"]*'`. Results:
   - `[0-9a-f]{32}`, `\b[0-9a-f]{32}\b`: `row=D-hors ... frame=E-find` at W 32 and 4095; `\d{32}`: `row=R7w ... ren=B-walk frame=E-find` at both;
   - `(?:ab|ba|aa|bb){24}c` (counterk.rxt:1919): no record at W 32; `row=D1 ... ren=B-memchr` at 4095;
   - `x[0-9]{26}`, `ab[0-9]{26}`: `row=D1`; with `--memfn=no-fd-d1`: `row=D1w ... ren=B-walk`;
   - `[xy][0-9]{26}`: `row=PAIR ... ren=B-pair` at 32 and 4095;
   - `[0-9a-f]{20}[g-z]{20}`: `frame=E-stmt` at 32; `row=D-hors frame=E-find` at 4095;
   - 710's ten classes at n 17, 25, 32 (W 32): hex, word, vowel, nonl, af, ident are D-hors; dig, hi, upper, num are R7w; all frame E-find.
   - Rev 1's text facts stand: every class has a window site up to n = 32 and none from n = 33; the positions tested = n (k = n - 1); `[0-9a-f]{17}` and `[0-9]{25}` have byte-identical walk lines at widths 32 and 4095.
6. **Machine-code probes** (gcc 15.2.0, -O2, `objdump -d` of `rxa_search`, addresses normalized):
   - **(a)** (rev 1; `$PCREC_TMPDIR/scratch/bspan/`) On 710's timed `avx2-loop` sources, with the `target()` attributes dropped: IDENTICAL on 6/6 (hex16, hex40, hex1000, dig24, num64, word500). With the harness's `rxs_span` wrapper also removed: hex16, hex40, hex1000 and word500 IDENTICAL; dig24 and num64 differ in one `cmp` operand order.
   - **(b)** [rev3, F-13] Rev 1's `wrapprobe.py` measured a ONE-level wrapper; its `[+.0-9]{65}` "440 lines" did not reproduce with the shipped two-level shape (0 lines, two independent r67 lenses) and is withdrawn. The two-level figures this note uses are r67's (SOUND-5, PREMISE-9, MEAS-6; `$PCREC_TMPDIR/scratch/crit-memfn-bspan/meas/`, `kit/objfn.sh`): the 3 real sites 0 instruction differences (one padding only); `\w{17}`, `\w{20}`, `\w{32}` 20-26 lines; `[+.0-9]{65}` 0. U2b re-measures on the built text.
   - **(c)** [rev3] `always_inline` at -O0: `$PCREC_TMPDIR/scratch/bspan3/ai.c` (an AVX2 `always_inline` helper `h` inside a `#pragma GCC target("avx2")` region, called from `inreg` inside it and `outreg` outside it). `gcc -O0 -c` → error "inlining failed in call to 'always_inline' 'h': target specific option mismatch" (from `outreg`). With `outreg` removed: compiles; `nm` lists only `T inreg` (no `h`); `objdump -d | grep -c ymm` → 6.
7. **Job 710's verdict** (`$PCREC_TMPDIR/scratch/memfn/blockconfirm/run-20261120T212920/decision.md`): CONFIRMED.
   - Cells: 840 cells, 112 N/A.
   - The claim: the verdict population is 144, with 127 WIN, 17 TIE and 0 LOSS. Over all counted cells: 295 W, 427 T, 0 L.
   - Per row: row 1 is 255/140/0 (W/T/L) and row 2 is 40/37/0.
   - Replication: 104 of 115.
   - The A/A line: 6/448 repeated.
   - (Hspk, the control, is a one-level wrapper and is not cited for the shipped shape, §2.)
8. **The C18 rule (c) and its regexes.** `grep -n 'SELECTOR = \|HELPER = ' tests/memfn/simd_floor_check.py` → 123 `^static inline size_t (\w+)\(...`, 124 `^static inline size_t (\w+)__w(\d+)\(`; its -O0 leg: `nm` of the `-O0` object (:375-381). The bracket's whole-line rule: `src/core/sb.c` `pcrec_sb_simd_open` / `_close`.
9. **710's grid** [rev3]. `sed -n 43,60p $PCREC_TMPDIR/scratch/memfn/blockconfirm/confirm.py`: ten classes (`SITE_EXPECT`: 6 window, 4 scan), `KS_OLD` (8 values) + `KS_NEW` (5) = 13 k; routed cells: 6 x 11 (k 16..1000) + 4 x 4 (k 24..64) = 82 of 130.

## 17. SHIP-SIZE (R-4's lens; information, not a ruling) [rev3]

What the build adds, under option A and `wrap-differs` outcome 1. Counts
marked UNMEASURED are estimates the build lane replaces with `git diff
--stat` at its landing; nothing here was built.

| surface | added |
|---|---|
| table | 2 rows (T-vwin, T-vscan) plus the 4 H/I/L rows reshaped from the if chain; `wf_span_head` and `w->head` retire; `skip` becomes one plan fact |
| code, `memfn/src` | the block-text renderer (§4.1, two widths), the per-stretch table evaluation at define and use, the ofsskip selector writer lifted to a shared helper (no third writer): UNMEASURED, expected a few hundred lines in `window.c` and `ofsskip.c`, no new file |
| emitted text per site | scalar layer (every layer): the `vs<j>` selector and `__body` (one `return` each, about 0.4 KB, UNMEASURED). SIMD layer (`w32`): the bracket, about 1.3 KB at B = 32 (§5), less at B = 16 (UNMEASURED) |
| deny | 1 row (`span-vector`), live at both layers; 1 `registry.md` row, floor 14 to 15 |
| card | 1 (C6: 3 real sites + 6 bound cells + F2 DIFFERS, plus an A/A arm), 1 `kit-grid@8` row, **1 formhash SHAPE + its renderer + 1 entry** (F-16) |
| checks | 1 G2 unit section, 1 G2 whole section, **12 pin cells** (8 bound + 4 column/once-per-site, F-18), **SPAN-SEED: 1 literal list of 41 patterns with 2 floors** (F-3), 1 identity gate with a declared mask, **the C18 amendment** (2 regexes, the -O0 rule, 2 named witnesses, 3 control plants; F-1), **5 new sabotage rows** ((a)-(e)) and **5 re-aims** (S3277-S3282, F-9); F2 and the U2b census are delivery steps, not committed tests |
| spec | `registry.md` §6¶8a/8b, `tuning.md` §2.43¶3a/3b/3d, `limits.md` §8.3¶3, `match_api.md` §6 (abi): 6 hunks |
| abi | 1 event (the number taken at landing, §9.1) |

**Cut by r67 (each with its trigger):** T-keep and §2.1 (c) (no fact to
key on; returns only under `wrap-differs` outcome 2, as a proxy row);
U2b's scalar timing (cannot detect the effect); G1's timing window
(UNREACHED by construction; trigger: a bin reaches 8 movers); C6's four
outside-bound cells (A/A by construction); the force and body levers
(PLAN rows; trigger: a bound is questioned).

**Grew by r67:** the C18 amendment, the formhash shape and renderer, five
sabotage re-aims plus one ordering plant, SPAN-SEED and its floors, four
pin cells. Net: about rev 2's size, minus T-keep and two timing windows,
plus the C18 and formhash units rev 2 did not count.

**Against the population:** 3 (text, options) pairs route today, all in
the bench, all k = 31 (§0.1), by information only (D201 add. 1: "We're
here and there's no downside so let's build it."). Kept because the 710
table needs them (R-4): both bounds of both rows, the B = 32 rung (no real
site reaches it, but D201's "Read as" names the 710 table), the deny, the
one-stretch-per-site rule, the 32 and 16 rungs only, no SWAR, no unrolled
form, no knob beyond the deny row.

## 18. r67 dispositions (review 2026-11-21-r67-memfn-bspan, the kit manager's ruling)

| F-id | ruled | answered in |
|---|---|---|
| F-1 C18 not unchanged | FIX-NOW | §10.2 "The C18 amendment", §5, §14 U4, §17, §16 items 6c, 8 |
| F-2 population 3 bench sites, 0 corpus | FIX-NOW (doc) | §0.1, §11, §17, §16 item 5; D201 add. 2's line is main's (§15) |
| F-3 empty populations; identity gate mask | FIX-NOW | §10.1 SPAN-SEED, §10.2 identity gate, §0 G-1/G-4, §9.3, §9.4 |
| F-4 D1w admitted | FIX-NOW (key on R7w) | §3 (T-vscan on brow R7w), §3.3, FREEZE NOTE |
| F-5 `set_epi8` order | FIX-NOW (text) | §4.1 "Lane order" |
| F-6 unused `__body` (clang) | FIX-NOW (text) | §5 (`unused` at every layer) |
| F-7 plant (b) cannot fire on HORS | FIX-NOW | §10.2 plant (b) |
| F-8 lower bound 16 is a safety floor | FIX-NOW (label + assert) | §4.1, §4.2, §12 |
| F-9 five sabotage anchors retire | FIX-NOW | §10.2 "Re-aims at U1", plant (e), §14 U1 |
| F-10 where the table is evaluated; `skip`; include bit | FIX-NOW | §3 "Where the table is evaluated", "`skip` becomes a plan fact", §5 include, §9.3 |
| F-11 third selector writer | FIX-NOW (decide) | §5 "One writer" (one writer, lifted from ofsskip; vany at its next touch) |
| F-12 abi grep filters a reader | FIX-NOW (doc) | §9.2, §16 item 1 |
| F-13 wrapper evidence (Hspk one-level) | FIX-NOW (doc) | §2, §16 item 6b, §2.1 (BUILT text only) |
| F-14 scalar no-loss check; T-keep | MANAGER RULING: coordinator's leaning | §2.1 (census only), §2.2 (`wrap-differs` fork), §3 (T-keep gone), CONSTRAINT |
| F-15 card C6 | FIX-NOW, no new lever | §8, §0 G-3 |
| F-16 formhash needs a shape | FIX-NOW (doc) | §8 `deps`, §14 U5, §17 |
| F-17 F2's `.H64` reference | FIX-NOW (doc) | §6 (82 routed cells, landing rule), §16 item 9 |
| F-18 pins guard only k | FIX-NOW | §10.2 T-table pins (12 cells, widths) |
| F-19 §11 examples, encoding | DOC | §11 |
| F-20 owner not quoted verbatim | FIX-NOW (doc) | FREEZE NOTE, §2 (record quoted; readings labelled) |
| F-21 owner's ruling ranked as a goal; "off by default" | FIX-NOW (text) | CONSTRAINT line, §7 |
| F-22 G1 timing vacuous | FIX-NOW (text) | §9.4, §17 |
| F-23 D155 add. 3 | DOC | §2, FREEZE NOTE |
| F-24 D201 provenance pointer | main's (decisions.md) | not edited here (§15) |
| NOTED: line nits; w16 = off | NOTED | §1 (:3536, :1401), §2 |
| Lessons 1-3 | accepted | lesson 1 applied in §0.1, §10.1 (count by trace record); 2 in §10.2; 3 in §2, §2.1 |
