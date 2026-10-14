# setfind — R-17 revision 2: the small-set FIND as the degenerate window search

**revision 2.3 (2026-10-12, r5 light re-check applied; the revision a build
follows, after the bench relay gate)** — lane r17r23, text only, on
`lane/r17r` at the kit tip `17e09a86`. Nothing was run. It applies every
disposition of `docs/dev/reviews/2026-10-12-r5-memfn-setfind22.md` (K3-1..K3-11),
each checked against the code it cites. **Read §R6 first**: it maps each r5 id
to where it is answered and names the two places this revision did something
other than the disposition's literal text, with the evidence (K3-7: the
reserved prefix rule must also refuse the bare prefix `pcrec_mfk`; K3-8: the
key is K80's own guard, because the kit cannot see pcrec's abi). The bench
gate's change and the one withdrawn claim go to pcrec-bench as a corrigendum to
I-148: `setfind_bench_corrigendum_I148.md`. The settled directions (D155 add.
3/4/4.1, D161 add. 1-3, D162 and add. 1) are not reopened. Where revision 2.2
text below disagrees with a `[rev 2.3]` marker, revision 2.3 wins.

**revision 2.2 (2026-10-12, every direction SETTLED; the revision a build
follows, after the bench relay gate)** — lane r17r22, text only, on
`lane/r17r` at the kit tip `b50d4a80`. Nothing was run; the one number this
revision computed itself (the `reset=call` row across the ppm grid, §9.2) is
python over the committed `probes/r17/out/slot2/times.tsv`. It folds in:
- the follow-up timing, RUN as slot2 and read in `probes/r17/reading_slot2.md`
  (§13);
- D155 addendum 4 and 4.1 (body text over per-width primitives; the stateful
  contract `next_candidate(&state, lo)`; §3.4a, §4, §6, §8);
- D162 and its addendum 1 (one analysis object; ADMIT when density is absent;
  the bench relay gates R17-b; the state-lost dense residual is
  [FINDALL-NEXT]'s; §9.2, §11, §14);
- D161 addendum 3, unchanged (§2).

The forms that survive are ONE stateful row behind `next_candidate`, with
`mask8_swar` at SWAR, `mask64_sse2` at SSE2 and `mask64_avx2` at AVX2. The
ring, the adaptive switch, the stateless term-OR and `pf_memchr_set` are not
built, and their reasons are recorded (§4.1, §8.3, §9.1, §17). The bench
request that gates R17-b is the self-contained draft
`setfind_bench_request.md`. **Read §R5 first**: it maps each settled
direction and each slot2 answer to the section where it lands. Revision 2.1's
header and amendment follow unchanged; where they disagree with revision 2.2,
revision 2.2 wins, and the amendment's "the adaptive switch (§9.1) learns at
run time" is superseded by D162 addendum 1 (the no-data decision is ADMIT,
§9.2).

**revision 2.1 (2026-10-12, r4 light re-check)** — lane r17r21, text only, on

> **Amendment (2026-10-12, Frank, ruled directly to the kit):** workload data
> reaches the kit as ONE ANALYSIS OBJECT per compile, not a `freq` field:
> "option 1 with options to add more data. pcrec should send what it has."
> Compile-wide distributions only (option 1), extensible by kind, with a
> per-site slot reserved. W6 and §14's N1 are restated. The "one density
> carrier" unlock (§17) folds into the object. Where other sections still
> say `freq` or W6 as a byte-rate field, read it as the object's byte-rate
> kind.
> Frank, same day: "that said, be ready to make decisions without data."
> Every row's selection is TOTAL when the object, or a kind in it, is absent.
> The no-data path is a stated decision, not a fallback to refusal. Here the
> adaptive switch (§9.1) learns at run time, and with no density kind the
> static gate keeps today's walk only where the stateful forms lose. Data
> refines a choice; it is never a precondition for one.
`lane/r17r` at the kit tip `b7d086ff`. It applies every disposition of
`docs/dev/reviews/2026-10-12-r4-memfn-setfind.md` (24 ids, r3's C1-2 residual,
and the sabotage renumbering to main's allocation S826-S843). Read **§R4**
first: it maps each r4 id to the section that answers it, and names the four
dispositions this revision corrected against the code (K1-5, K1-6's VM half,
K2-1's flush half, K2-6's include slot). The rulings (Q-R17-1, Q-R17-2, D161
addendum 3) are unchanged. Nothing was run by this revision; the harness runs
cited in §13 are lane r17dry's (`docs/dev/lanes/r17dry_report.md`).

Lane r17r5, 2026-10-11/12, for the memfn kit manager. Branch `lane/r17r`, cut
from the kit branch `lane/memfn-r17` at `e704144c` (pcrec code at abi 75,
`MF_SITE_ABI` 10). DESIGN ONLY: nothing under `src/`, `memfn/` or `tests/`
changes. The box was held by main's validation chain, so **nothing was run**:
no build, no compile of the harness text, no timing. Every run named below is
OWED, with its owner and trigger in `docs/dev/lanes/r17r_report.md`.

Revision 1 is `docs/dev/lanes/r17s_report.md` (the scoping, §3.4 the row
family). Its step-2 timing reading is `probes/r17/reading_slot.md`. The D6
panel that this revision answers is `docs/dev/reviews/2026-10-11-r3-memfn-r17.md`
(36 ids; §R below disposes of each one). The follow-up measurement's source
text is under `probes/r17/` (§13).

## 0. Answers first

1. **R-17 is the window search with one span of one position, move-back 0,
   overshoot 0 (§2).** The kit's existing vocabulary already says most of
   it. An `mf_pred` of REQUIRED terms at fixed offsets IS one span. Its
   classes are the terms' sets, and the "any byte" class fills its gaps.
   Term offsets already carry the span AFTER the window's beginning that
   MLINE needs; `[r4 K2-4]` with D161's origin that is a NEGATIVE move-back
   (-1), so the field is signed. What the general form adds:
   - the window's move-back and overshoot (two fields on `mf_pred`, with a
     stated bit);
   - further spans the kit may choose among;
   - a frequency table;
   - a consumer price;
   - a reply that names the span.

   R-17's routing event carries the first two fields now, along with FIND's
   result meaning ("the window's beginning, never below lo") and the storage
   and file-scope routing. `[r4 K2-4]` The fields have D161's origin (the
   span's beginning), a reserved unbounded value and a checkable STATED bit.
   Every FIND builder states them, and at R-17 each states the neutral value
   (the window begins at the candidate). The others are appended by R-18;
   appending a field moves no byte, and no R-17 row reads them.

   `[r4 K2-2, K2-3]` **What "the sites move once" means, honestly.** It is
   ROUTING-once, and only for the PF sites (the DFA prefilter, the DFA hat,
   the VM hat): how each is defined, where its text goes and what storage it
   has are fixed by R-17's one event, and R-18 does not re-route them. It is
   not BYTES-once. A PF site's bytes move at R17-b, and again at any later
   FORM event, where a row starts reading a new fact behind its own deny.
   The one such event already in view is W6. `[rev 2.2]` §13 RAN: the
   stateful forms lose dense only where the state is lost (§9.2), and D162
   addendum 1 rules ADMIT when density is absent. So R17-b reads NO density
   fact, and the gate's decline arm is a later FORM event on the PF sites,
   landing only when the analysis object carries both of its inputs (§9.2).
   It re-routes nothing. Other sites may re-route at R-18: the K82 handoff (an
   ALL_PRESENT / ASSIGN site whose reply is `preds[ret_pred]`'s hit, with
   pcrec's own `c - K` text after it) and the offset-skip FUNC. Revision 2's
   "R-18 needs no re-routing" is WITHDRAWN for them (§2.1).
2. **The forms centre on STATEFUL variants (§8).** A per-site CACHE holds the
   exact membership of a subject block `[base, top)`. It is spelled either
   as a bitmask (Frank's "truth vector", popped one set bit per candidate)
   or as a ring of candidate positions drained before the next vector or
   SWAR pass.
   - `[rev 2.2]` **The body contract is `next_candidate(&state, lo)`** (D155
     addendum 4.1). The state and its form are per width and chosen by
     measurement, and the body never changes. **Measured and chosen (slot2):**
     the carried mask at every width: `mask8_swar` (W = 8), `mask64_sse2` and
     `mask64_avx2` (W = 64). The ring loses to the mask in every regime and is
     NOT built (§8.3); it stays a filed note behind the same interface.
     `mask64_swar` is admitted only where the state survives the whole call
     AND every span is at least 64, and no R-17 site states both, so it is
     designed and not built (§4.1).
   - `[rev 2.2]` Each width's implementation is readable text over per-width
     PRIMITIVES (a vector type, `load_vector`, the eq/cube/range term masks,
     `first_lane`) defined once per file in a guarded shared block (D155
     addendum 4; §3.4a).
   - **The correctness core is one invariant.** The cache is a pure function
     of bytes that are immutable for the call. That makes every answer equal
     the stateless answer for ANY sequence of `lo` values: backwards, repeated,
     a jump, a reseed, past `n`, at `n = 0`.
   - **The proof (§8.2) needs from pcrec only that `s`, `n` and the subject
     bytes do not change between uses.** It does not need monotonicity.
3. **Adaptive (§9.1).** A two-mode switch observes the skip distance at each
   use. It drops to pcrec's table walk on short gaps, for a doubling block
   with a probe: [OPT-HYB-RESEED]'s shape, carried in the same kit-owned
   locals. Every threshold is `UNMEASURED DEFAULT`. The static
   positive-evidence density gate is a FALLBACK only (§9.2), rendered only if
   the follow-up shows the stateful/adaptive forms still losing dense. Until
   then R-17 needs NO density fact, and N1 stops being the build trigger.
   - `[rev 2.2]` **MEASURED: the adaptive switch does not pay, and is NOT
     built** (slot2 answer 4: it beats the better of `table` and its fast form
     beyond the band on 4-9 of 574 rows and loses on 393-447). §9.1 keeps the
     design as a filed note.
   - `[rev 2.2]` **§9.2 is REWRITTEN under D162 addendum 1.** The rows ADMIT
     when density is absent and decline only on POSITIVE evidence of density
     at or above ~300k ppm TOGETHER with a state-losing call pattern. That
     reverses revision 2.1's "`D_ABSENT` declines". No input can reach the
     decline arm today, so R17-b reads no density fact; the arm lands as a
     form event when the analysis object carries both kinds. The state-lost
     dense residual is [FINDALL-NEXT]'s (main's chunk 5), not R-17's: break-even
     is 2-3 candidates per state lifetime for `mask8_swar`.
4. **Kit-owned local storage: what pcrec provides (§7; main's question).**
   - ONE declaration call, `mf_locals`, at a point in the function that
     dominates every use, before any `goto`/label that can reach a use;
   - automatic storage for one call (never `static`: the matcher stays
     reentrant);
   - initialization in the declaration, by the kit's text;
   - `s`, `n` and the subject bytes invariant across the uses, and nothing
     promised about the cursor;
   - one storage per site, shared by all of that site's uses, so the VM hat's
     entry and retry share one cache;
   - names derived from a pcrec-given stem (`fn_ref`) that pcrec reserves.
     `[r4 K2-9]` The stem is derived from the name of the function holding
     the uses, so no two bodies in one artifact can share one.

   `[r4 K2-5]` pcrec states this as a host CAPABILITY on the site
   (`decl_point`: "pcrec calls `mf_locals` for this site at such a point"),
   never as a request for storage.
5. **One routing event (§11), in two commits.**
   - **R17-a:** a zero-mover seam. Each PF site is DEFINED at a file-scope
     point above its function (define-then-use), gets `mf_locals`, reports
     whether its form reads pcrec's table, and states the new fields, with
     every artifact byte-identical.
   - **R17-b:** the one SIMD-off byte move. The new rows land with their
     denies, the abi bump and the method-blind spec text.
   - **Then:** SIMD arms land as guarded helper DEFINITIONS, at zero SIMD-off
     movers (the floor rule).
   - `[rev 2.2]` **The shared primitive block is emitted only when some site
     uses a primitive.** No R17-a row uses one, so the block is absent there,
     and R17-a stays a true zero-mover. The block first appears in R17-b,
     inside that step's one abi event (D155 addendum 4's manager note; §3.4a,
     §11.1).
   - `[rev 2.3, r5 K3-1, K3-8]` **The block is one sub-block PER WIDTH**
     (W8, V16, V32), each under its own guard and each emitted only where a
     site uses that width (§3.4b). A SIMD-off artifact therefore holds the W8
     sub-block only, with no SIMD text in it, so the SIMD arms land at zero
     SIMD-off movers. No sub-block carries a version or a value of its own:
     K80's abi guard, which every artifact emits before any kit text, is the
     key.
   - `[rev 2.2]` **A bench relay on real subjects GATES R17-b** (D162
     addendum 1). A real cell that loses beyond the regression floor returns
     to the kit before merge. The relay is drafted, self-contained, in
     `setfind_bench_request.md`, for main to carry (the kit never writes to
     pcrec-bench; §11.2a).

   `[r4 K2-1, K2-6]` The panel's N2 shrinks to two DEFINE POINTS that already
   have precedents, and nothing else: the DFA PF site is defined from a new
   `u.pf.emit_block` on its rows (the offset-skip FUNC's precedent), the VM
   hat beside `pcrec_emit_req_run_blocks` above `<searchfn>_run`. Each writes
   its helper straight into the file stream there, so `mf_flush_helpers` is
   UNCHANGED. Revision 2's "the pending-helper flush" was wrong twice: that
   call flushes word loads only, and it runs in the prologue, before
   `_search_run` is written. `mf_plan` is DROPPED: the define reports whether
   the form reads the table, and the new rows are header-free, so no include
   is predicted. No table moves to file scope for any row: a helper that
   reads pcrec's table takes it as a PARAMETER, named at each use (K1-1, the
   `<p>_ofsskip` precedent; C3-6, re-derived).
6. **The follow-up measurement is written, not run (§13).** It adds:
   - stateful twins (mask8/mask64 at SWAR, SSE2 and AVX2, and a ring), with
     adaptive twins;
   - a state-reset axis (within-call, per-call, and every K hits);
   - the grid the panel asked for;
   - an exhaustive candidate-SEQUENCE check with a planted stale-state
     control.

   Estimated wall time is about 1 h 45 min on one pinned core (an upper
   bound). Lane r17dry has since compiled, checked and dry-run it: 0
   mismatches over 4.04 G calls, the planted control caught 152 of 152,
   ASan+UBSan clean, 619 invocations listed, its arithmetic estimate ~80 min.
   `[r4]` The harness measures forms, not the contract, so revision 2.1
   leaves it unchanged (§13).
   `[rev 2.2]` **It has RUN** (slot2, 2026-10-12 03:48-05:37, core 14, quiet
   box; 9,654 rows, void 0; read in `probes/r17/reading_slot2.md`). §13.5
   records what each verdict decided. Real bench subjects were NOT run, so
   that question moves to the bench relay (§11.2a).
7. **Correction to revision 1 (§1.3):** "no pcrec change for SIMD-off" is
   false (C3-2/C3-3). The `findall` regime models only WITHIN-CALL re-entry.
   A true match ends the call, so per-call state cannot survive it (§13.1).

## 1. Inputs and the rulings, verbatim

### 1.1 The rulings (all RULED)

1. **D161 addendum 3** (Frank, `docs/dev/decisions.md`, main tree):
   > "Ideally the idea of having kit handle 'search for window' subsumes other
   > kit requests. It's a more general form of simple search."

   D161 itself, the contract being generalized:
   > "**A list of SPANS.** Each span is an ARRAY OF CLASSES (one byte set per
   > position), with a **move-back** number: how far to move back from the
   > span's beginning to the window's beginning (a prefix is 0; an inner span
   > might be 7). And an **overshoot** number: how far that move-back might
   > overshoot the match beginning. **A frequency table** (the byte-rate prior
   > / findings data). The kit builds the window search from these. Which
   > span, which positions, which form, and when a span is worth using are the
   > kit's."
2. **Q-R17-1**, D161 addendum 2 (Frank):
   > "I like adaptive. But also, this depends on how the fast form is
   > implemented. If it preserves its data between candidates it might be
   > faster. Say we have the truth vector I mentioned and we save it. Or we
   > have a circle queue of potential positions and we exhaust it before the
   > next simd search."
3. **Q-R17-2 = (A)**, D155 addendum 3 (Frank; main renumbered it from 2):
   > "those kit emit restrictions were for when kit simply was choosing one fn
   > or another. I'm not sure they apply. They were more guidelines or goals
   > than hard rules. Also, it might be that kit emits lower level
   > instructions into the body that compose to the result rather than a
   > function that handles the whole effort. Each lower level function
   > definition might have ifdef inside it to guide its implementation. That
   > said, if the code can be neatly put into a function then that works too
   > and I agree with A. Consider that the start position queue idea might
   > need local storage and therefore might need the kit function to access it
   > or even decide if it should be emitted or not. So the kit can emit code
   > into the body but should avoid ifdef code there. One method is to
   > encapsulate a arch-versioned function in the header but there may be
   > others."
4. **Main's question** (kit journal, 2026-10-11, "Q-R17-2 RULED"): "The
   state-slot contract item becomes 'kit-owned local storage in the body'.
   Main asks what pcrec must provide (a declaration site? its lifetime across
   candidates?)." §7 answers it.

`[rev 2.2]` The rulings of 2026-10-12, in the order the kit journal records
them (all SETTLED):

5. **D162** (Frank, to the kit; filed by main): workload data is ONE
   analysis object.
   > "i agree option 1 with options to add more data. pcrec should send what
   > it has."
   > "that said, be ready to make decisions without data."
6. **D155 addendum 4** (Frank, to the kit; filed by main): body text over a
   per-width set of primitives.
   > "i like your idea of a set of primitives to be used in the body. it
   > provides a lot of flexibility to customize the solution."
7. **D155 addendum 4.1** (Frank, to the kit): the stateful contract is
   `next_candidate(&state, lo)`.
   > "i like your hide behind primitives idea. ultimately its a performance
   > issue and avx512 does handle them extremely cleanly."
8. **D162 addendum 1** (Frank, via main, "Yes agree" to the manager's lean):
   ADMIT when density is absent; decline only on positive evidence of density
   at or above 300k with a state-losing call pattern. A bench relay on real
   subjects gates the routing event. The state-lost dense residual is
   [FINDALL-NEXT]'s (chunk 5), not R-17's.

Binding throughout:
- **D157:** pcrec→kit carries facts only.
- **D122:** one implementation per search.
- **D77:** build under measurement.
- **D147:** layers; SIMD must beat the current scalar.
- **D155 addendum 3:** no `#if` in body code.
- **D149:** every unmeasured constant is labelled in place.
- **No silent defaults.**
- `[rev 2.2]` **D155 addendum 4 / 4.1:** forms are composed from per-width
  primitives; a stateful FIND's body is `next_candidate(&state, lo)`, and the
  body never changes with the width or the form.
- `[rev 2.2]` **D162:** every selection is TOTAL without data.

### 1.2 Main's gaming-out, read for this note

`docs/design/memfn/window_search_game.md` (main tree, wingame/wingame2):
- §1 derives spans as `move_back = omax`, `overshoot = omax - omin`.
- §2 lists what D161 cannot say: an unbounded move-back, per-branch spans,
  variable distance between spans, lookbehind as a negative move-back.
- §3 sets out the policies P1-P6.
- §5.5 lists the facts the contract needs: `omin` beside `omax`; a consumer
  price per route (a fixed cost per candidate, a cost per window byte, a cost
  per possible start, and a no-search cost per byte); optionally a joint
  survival rate.
- §8.5 adds that the REPLY must name which span's `(move_back, overshoot)`
  the window has, because P6 scans one span and hands over another's window.

§2 below is consistent with each item and marks what R-17 carries now.

### 1.3 Corrections to revision 1's stale facts (`r17s_report.md`)

| r17s said | now |
|---|---|
| §0.1, §3.4: "No new pcrec fact is needed to render any R-17 shape with SIMD off"; "the SIMD-off half needs no pcrec change" | **False.** The `<string.h>` prediction (`need_string_h`, `emit_dfa.c:12791`), the stamp/spec meaning, and dead tables under `-Werror` all move (C3-2, C3-3). §11 and §14 (N3) carry them. |
| §3.4: build "in two halves", SIMD-off inline first | **Withdrawn** (C3-1). Q-R17-2 = (A) makes it one routing event (§11). |
| §3.4 row 1: "`pf_memchr`, widened to NOP and to a present `table_ref`" | **A new row, `pf_memchr_set`**, with its own deny and its own store form (C1-5, C3-4; §4.3). |
| §1.1, R-17's Facts: the VM hat caller is `emit_dfa.c:7111` | `pf_vm_emit_first_class` is `emit_dfa.c:7200`. Its two call sites are `emit_vm.c:13464` (entry) and `:13559` (retry), through `pcrec_emit_vm_start_seek` (`emit_dfa.c:7299`). |
| §4.3: `findall` is "the DFA prefilter's re-entry", one FIND per hit | **Only WITHIN-CALL re-entry.** The PF block fires while `state == s0 && last == -1` (`pf_open`, `emit_dfa.c:6228`; `[r4 K2-12]` rev 2 cited :6222), so after the first accept it never fires again in that call. A find-all crosses a CALL per true match, and per-call state cannot survive that. The regime now splits on a state-reset axis (§13.1). |
| §4.3 expectations: "at 800k ppm, swar is within the floor band ... memchr/mcK LOSE there" | Measured (`reading_slot.md`): every form WINS at 800k; the loss is at 300k. |
| §3.4: K is "read off step 2's timing" | Not readable: no cell has more than 3 terms (C2-4). K stays `UNMEASURED DEFAULT = 3` until §13's 4/5/6/8-term cells. `[rev 2.2]` Read off slot2's synthetic cells: K = 4 (§3.3). |
| §6.2: S824 = "the NOP memchr row's `lo < hi` guard removed" | Re-aimed to the n = 0 wrap (C1-1; §12.5). |
| §3.1: the SWAR forms' lane test, `haszero` | `haszero` is LOWEST-exact only (§3.4). The stateful forms and the complement form need EXACT lane renderings. |
| §3.4 "Fits the architecture": "SIMD-off fits as is ... no file-scope part" | Superseded by §11's routing: the term rows' text is a file-scope helper plus a one-statement use. |
| `pffind.c` header: "the one-byte/table split is the SITE's" (F-2) | False from R17-b on. The header is rewritten in that commit (C3-10). |

## 2. The window-contract mapping (the degenerate case of D161)

### 2.1 What the existing vocabulary already says

Take a FIND's candidate `c`. A term at offset `d` reads `s[c + d ..]`. So an
`mf_pred` whose terms are all REQUIRED and at fixed offsets is ONE SPAN:
- its positions run from `d_min` to `d_max`;
- each position's class is that term's set, a RUN term's masked bytes, or
  "any byte" at an offset no term covers;
- `[r4 K2-4]` its D161 move-back is measured from the SPAN'S BEGINNING,
  `c + d_min` (D161: "how far to move back from the span's beginning to the
  window's beginning"): the window begins at `c + d_min - move_back`. Today
  the window IS the candidate `c`, so every site's move-back is `d_min`;
- its overshoot is 0, because every offset is fixed.

| existing site | span(s) | D161 move-back | overshoot | the reply today |
|---|---|---|---|---|
| PF / DFA-hat / VM-hat FIND (R-17) | one span: one position, class `S` | 0 | 0 | `result` = the first `c` (the window IS the candidate) |
| MLINE `(?m)^` (`pf_memchr_back`) | one position at offset -1, class `{\n}` | **-1** (the window begins one byte AFTER the span's beginning) | 0 | `result` = the hit + 1 |
| offset-skip FUNC (`ofsskip`, `offset-set`) | one span: the k-set's terms at offsets 0..k | 0 for the span; the SCANNED position (`plan_hint`, the kit's within-span choice) is at move-back k | 0 | the candidate |
| ALL_PRESENT / ON_MISS presence gate (R-15's ASSIGN gate, N4's set rest) | npred spans, each "somewhere in [lo, hi)" | unbounded: the window is anywhere ahead | unbounded | existence (ON_MISS), or `preds[ret_pred]`'s leftmost hit (ASSIGN) |
| K82/L1 handoff | the landmark's span (a run window or one byte) | K (`req_landmark_maxoff`) | K - omin (omin not carried: so up to K) | the gate's hit; **pcrec's own text** computes `hit - K` after the site |

Two findings follow:
- **The negative move-back is already expressible.** wingame §2.2 says D161
  cannot state a span AFTER the window's beginning (lookbehind). The kit's
  offset form already does, at -1, with Q-R7-1's read-bounded range.
  `[r4 K2-4]` With D161's origin that span has move-back **-1**, so W1 is a
  SIGNED field: a negative value says the window begins after the span's
  beginning. (Revision 2 measured from offset 0 to keep W1 unsigned; the r4
  critic found that origin ambiguous against D161, and it is replaced.)
- **The handoff's reply is split today.** The kit finds the hit; pcrec moves
  back K. Under the window contract the kit's reply IS the window's
  beginning, so a handoff site that stated `move_back = K` would retire
  pcrec's `c - K` text. `[r4 K2-2]` **R-17 does not fix that meaning for the
  handoff.** W3 (§2.2) is FIND's result on a STMT / ASSIGN FIND site. The
  handoff is an ALL_PRESENT / ASSIGN site whose reply is `preds[ret_pred]`'s
  leftmost hit (`emit_dfa.c:1576-1582`), and extending W3 to that reply is a
  meaning change with a byte move (pcrec's text after the site goes) that no
  R-17 row needs, so it is not justified now. Revision 2's "so R-18 needs no
  re-routing" is WITHDRAWN: R-18 may re-route the handoff, and the
  offset-skip FUNC, whose scanned position already sits at move-back k inside
  its span. "Move once" holds for the PF sites (§0 item 1).

### 2.2 The proposed fields and reply

Every field here is **proposed; ratified by main's chunk-2 note / R-18**. The
spellings are the kit's (D157: facts, no method).

| # | field / meaning | type | R-17 carries it? | why now / why later |
|---|---|---|---|---|
| W0 | `[r4 K2-4]` `mf_pred.window_stated`: 1 = W1 and W2 are STATED. 0 is the zero-fill, so it means "unstated", never a value | `uint8_t` 0/1 | **YES, 1 on every FIND builder** | No silent defaults: a FIND site with 0 is REFUSED (every FIND row uses W1/W2, R1), so a builder that forgets fails at R17-a rather than reading a zero-fill as "move-back 0". A non-FIND site or a `reverse` site stating 1 is refused: no window meaning is defined there. |
| W1 | `mf_pred.move_back`: bytes from the SPAN'S BEGINNING (`c + d_min`, D161's origin) back to the window's beginning. Negative: the window begins after the span's beginning (MLINE: -1). `MF_MOVE_UNBOUNDED` (`INT32_MAX`) is RESERVED: no bound | `int32_t` | **YES, stated by every FIND builder** as `d_min` (0 on R-17's sites, -1 on MLINE) | Free to state now. If it were appended later, every FIND builder would be edited a second time, and the R-17 rows would read an unstated value (a silent default). R-17's rows SERVE `move_back == d_min` only (the window is the candidate); anything else declines (R2). `[r4 K2-4]` signed, with D161's origin and a reserved unbounded value (the r4 unlock "`MF_MOVE_UNBOUNDED` + a fixed origin", taken now). |
| W2 | `mf_pred.overshoot`: how far the window's beginning may lie before the match's beginning; `MF_OVER_UNBOUNDED` (`UINT32_MAX`) = unbounded | `uint32_t` | **YES, stated 0** | As W1. `omin = move_back - overshoot` is derived (signed arithmetic), so it needs no field (wingame §5.5 item 1 holds through W1 and W2). |
| W3 | FIND's RESULT, on a STMT / ASSIGN FIND site, means the window's beginning, never below `lo`. With `back = move_back - d_min` (a constant of the site) and `c` the first candidate the site's range admits (today's result): `back == 0`: `c`; `back > 0`: `c - lo >= back ? c - back : lo`; `move_back == MF_MOVE_UNBOUNDED`: `lo`. `back < 0` is REFUSED at R-17 (no builder states it; R-18 defines it). A miss is unchanged | (a meaning, no field) | **YES** | `[r4 K2-4]` NON-WRAPPING: the subtraction runs only where `c - lo >= back`, so `c - back` never goes below `lo` or wraps (revision 2's `max(lo, c - move_back)` formed `c - move_back` first). At R-17 every builder has `back == 0`, so the result is today's, byte for byte. It is written into memfn.h's `MF_OP_FIND` comment in R17-a. Soundness for `back > 0`: `c* <= c_m <= m + omax`, so `c* - omax <= m` for every match `m >= lo` (wingame §1.1's definitions). `[r4 K2-2]` It is NOT extended to ALL_PRESENT's `ret_pred` reply (§2.1). |
| W4 | `[r4 K2-5]` `mf_site.decl_point`: a HOST CAPABILITY. 1 = pcrec calls `mf_locals` for this site, once, at a point dominating every use (§7). The kit may use it or not, and may write nothing there | `uint8_t` 0/1, OBLIG | **YES** | It is the fact a row that keeps storage needs at DEFINE time (R1: 0 declines). Revision 2's name, `locals_offered`, and its gloss read as a request from the kit's method; the field states what pcrec provides. |
| W5 | `fn_ref` on a STMT site: the stem of every kit-declared identifier for it (§7.6) | existing field, new reading | **YES** | It makes naming stable (no handle renumbering movers) and hook-safe. `[r4 K2-12]` `fields.def`'s `fn_ref` doc string ("names a FUNC site") gains the STMT reading at landing. |
| W6 | `mf_site.analysis`: the compile's ANALYSIS OBJECT (`const mf_analysis *`, one per compile, `NULL` = none stated): a versioned list of tagged kinds, each present or explicitly absent, carrying every compile-wide distribution pcrec has (byte rates first; see the 2026-10-12 amendment). Was `mf_site.freq` | `const mf_analysis *` | `[rev 2.2]` **no** (D162 addendum 1: the rows ADMIT when it is absent, so no R17-b row reads it) | D161 item 2, D162. A set's marginal rate is derived from it, so pcrec computes no `cand_ppm` for R-17. It is appended when its first reader lands: §9.2's decline arm, once the object carries a byte-rate kind AND a call-pattern kind, or R-18's first density reader, whichever comes first. Appending it moves no byte. |
| W7 | further spans: FIND reads `npred`/`preds` as alternative spans, any of which may locate the window | existing fields, new reading on FIND | no (`npred` 0 is already stated) | R-18. Today FIND never reads `preds`. Reading them is a meaning addition and a `MF_SITE_ABI` bump; no R-17 site is touched. |
| W8 | the reply's span: hook `span_index`, an lvalue written with the index of the span whose window was returned (0 = `pred`) | `const char *` hook | no (unstated = wildcard at one span) | R-18 (wingame §8.5). A use hook no R-17 row reads. |
| W9 | the consumer price per route: per candidate, per window byte, per possible start, and the no-search cost per byte | a small struct on `mf_site` | no | R-18 (wingame §5.5 item 2). pcrec's to state, because pcrec builds the consumer. The fallback gate of §9.2 is P5's decline degenerate, so a gate in force could later read W9 in place of its kit-own threshold. |
| W10 | a joint survival rate per span | optional | no | R-18 (wingame §5.5 item 3), behind a measured loss. |

**What "the sites move once" means here** (`[r4 K2-3]`, restated). A site's
ROUTING is how it is defined, where its text goes and what storage it has.
R-17's event fixes the PF sites' routing (W0-W5, `mf_locals`, the define
points, the table-read report) and their first forms. R-18 appends W6-W10 and
does not re-route the PF sites.

That is routing-once, not bytes-once. A PF site's bytes move again wherever
a row starts READING a new fact: an ordinary kit form event with its own
deny, never a re-routing. A FIELD appended to the struct moves no byte by
itself. Which §13 outcome keeps R-17's own reading set closed is stated in
§0 item 1. `[rev 2.2]` §13 ran and D162 addendum 1 ruled: R-17's reading set
stays closed, and W6 is not part of R-17.

### 2.3 What the degenerate case does NOT need

These are recorded so that R-18 does not inherit a presumption from R-17:
- spans of more than one position (the R-17 sets are one position);
- `omin` (always `d_min - 0`, the candidate);
- the consumer price, because the window is the candidate and there is no
  window cost to rank;
- the reply's span (there is one span);
- an unbounded move-back (wingame §2's biggest miss). `[r4 K2-4]` Its VALUE
  is reserved now (`MF_MOVE_UNBOUNDED`, W1), so R-18 does not re-shape the
  field; what a row does with it is R-18's question.

## 3. The term derivation, `mf_set_terms(set, K)`

ONE kit primitive. Every row and every SIMD level that renders a class as
lane tests calls it, and in R-18 so does every span position's class. That
avoids a fourth copy of cube analysis (the panel's first unlock). It lives in
`memfn/src/terms.c` (new, kit-internal, `static` callers through `kit.h`).

### 3.1 The term kinds

| kind | members | notes |
|---|---|---|
| `CUBE(M, V)`, `V & ~M == 0` | `{x : (x & M) == V}`, `2^(8 - popcount M)` members | `EQ(b)` is `CUBE(0xFF, b)` and the full set is `CUBE(0, 0)`. `{s,S}` is `CUBE(0xDF, 0x53)`. `80..FF` is `CUBE(0x80, 0x80)`. |
| `ARC(L, W)`, `1 <= W <= 128` | the MODULAR run `{(L + j) mod 256 : 0 <= j < W}` | A RANGE that may wrap past 0xFF. One per-lane modular subtraction, `d = x -lane L`, then `d < W`. W ≤ 128 keeps the test one lane compare (r17s's spelling). |
| the COMPLEMENT form | the whole set is `¬C`, for a cover `C` of the complement | One negation over the OR of C's EXACT flags. It covers `[^\n]`, `[^"]`, and every RANGE of width 129-255: `[L, H]` with W > 128 is `¬ARC(H + 1, 256 - W)` (C1-8). |

### 3.2 The candidates

The candidates of a set `S` (256 bits):
- its **prime cubes**: maximal `CUBE`s contained in `S` (Quine-McCluskey over
  8 variables; a member contained in no larger cube is its own prime cube,
  an `EQ`);
- its **maximal arcs**: every maximal modular run of members of length at
  most 128 is one candidate; `[r4 K1-10]` a run longer than 128 contributes
  EVERY 128-long arc inside it (at most 128 of them). Revision 2 took only the
  two END arcs, and then an interior sub-arc (an arc of a 200-long run that
  starts at 60) lay inside no candidate.

Every candidate is a subset of `S` by construction. This is **PURITY**: no term
admits a non-member. The complement form's candidates are the same
construction over `¬S`.

**Dominance** (`[r4 K1-10]`, what makes objective 1 exact). Every pure cube
lies inside a prime cube, and every pure arc of width at most 128 lies inside
a candidate arc (a maximal run of at most 128 is itself a candidate; inside a
longer run, any sub-arc of at most 128 fits in a 128-long one). Widening each
term of any pure cover to a candidate containing it keeps the cover, its size
and its purity. So the fewest-terms answer over candidate covers is the
fewest over ALL pure covers.

### 3.3 The objective and the search

**The objective is lexicographic.** A cover is a list of candidates whose
union is `S` (for the complement form, `¬S`). Overlap is allowed. Covers are
ranked by:
1. the number of terms, fewest first;
2. direct before complement (the complement costs one extra NOT per word);
3. the summed RENDER COST: the ALU operations per 64-bit word of each term's
   cheapest exact SWAR spelling, read off the renderer (`EQ` 6, `CUBE` 7,
   `ARC` 9 in r17s's spellings). DERIVED by counting the spelling's operators,
   not tuned (D149). A term that is both a cube and an arc (`30..37`) is
   spelled as the cheaper kind;
4. the canonical key: terms sorted by `(kind, M, V)` / `(kind, L, W)`, compared
   as a sequence.

**The search is bounded iterative deepening.**

    for k = 1 .. K:
        for target in (S, ¬S):              # [r4 K1-10] both, at every k
            dfs(uncovered = target, chosen = [], depth = k)
        if a cover was recorded at this k: stop (objective 1)

    dfs(uncovered, chosen, depth):          # candidates are target's (§3.2)
        if uncovered is empty: record chosen if better (objectives 2-4); return
        if depth == 0: return
        if ++nodes > BUDGET: abort the whole derivation (a DECLINE, below)
        x = the lowest uncovered member
        for t in the candidates containing x, in canonical order:
            dfs(uncovered \ t, chosen + [t], depth - 1)

- **Branching.** It branches on the lowest uncovered member, so every cover
  is reached by one branch order per term choice. `[r4 K1-10]` Within depth k
  the search is exhaustive over CANDIDATE covers of `S` and of `¬S`, not over
  all covers. By §3.2's dominance that loses nothing for objective 1.
  Objectives 2-4 rank candidate covers of the minimal size only: a cover
  using a non-prime `EQ` (cost 6) where its prime cube is a `CUBE` (cost 7)
  is not searched. That is a stated restriction, not a claim of optimality
  over every cover.
- **Determinism.** The canonical order makes the derivation deterministic:
  same set, same list, every compile, every box.
- **K** is the row's term limit: `UNMEASURED DEFAULT: 3` (C2-4, C3-10) until
  §13's 4/5/6/8-term cells give the measured boundary, i.e. the largest term
  count at which the chosen form beats the table walk in every regime its
  sites can be in. K moves bytes, so re-measuring it is an abi event (§16.3).
  `[r4 K2-10, r3 C3-10]` **K's derivation path:** the follow-up's real cells
  (at most 3 terms, as in step 2) and its synthetic `syn4`/`syn5`/`syn6`/
  `syn8` (exactly k non-mergeable terms) → `summarize_r2.py`'s per-cell
  verdict against `table` under the noise band → K = the largest k such that
  the chosen term row has no loss beyond the band in any regime at every
  cell with at most k terms → written into `terms.c` as `MEASURED-UNOFFICIAL
  (<slot>, dev box zen4, <date>)` in place of the `UNMEASURED DEFAULT`
  label, with G1 and the abi ritual in the same commit. A box on which the
  bench later reads a different boundary is a re-measure event (§16.3).
  `[rev 2.2]` **READ: K = 4**, to be written into `terms.c` as
  `MEASURED-UNOFFICIAL (slot2, dev box Zen 4, gcc 15.2.0 -O2, 2026-10-12)`.
  - **How it was read** (`reading_slot2.md` answer 5): K = 4 is the largest
    term count whose best SIMD-off form wins every SPARSE regime (findall 0,
    20k and 70k ppm; percall at 0 ppm), with margins 0.77-0.86 of `table`. At
    K = 5 the 0-ppm scan ties or loses (1.04; percall L16 1.01); K = 6 loses
    sparse outright (1.25 at 0 ppm).
  - **This is a narrowing of the rule above, stated, not hidden.** No term
    count, K = 4 included and the real 1-3 term cells too, wins in EVERY
    regime: dense percall (300k, spans 16/64) is `table`'s regime (syn4
    1.25/1.31). The rule above ("no loss in any regime") would give K = 0, so
    K is read on the sparse regimes. The dense regimes are governed by §9.2's
    admission rule and the bench relay, not by K.
  - **The syn8 anomaly** (K = 8 runs faster than K = 6 at 0 ppm) is
    unexplained and is not read as "8 terms are fine". The disassembly check
    owed with R17-b (§13.4) is exactly this question.
  - The only reason K > 4 is not dead is the state: syn6 at 300k is `swar`
    1.88, `mask8_swar` 1.23. K = 4 is a SIMD-off reading; the SIMD widths'
    K is the bench's, per box (D144 addendum 4).
- **BUDGET** caps the compile-time search: `UNMEASURED DEFAULT: 4096` nodes per
  derivation. It is a compile-time bound and not a run-time tuning, but it
  decides which sets decline, so it moves bytes, and it is labelled. Its
  control is a census tripwire (§12.1 check T3): no corpus or bench set may use
  more than BUDGET/4 nodes. If one does, the budget has become a visible
  selection constant and must be derived instead.

### 3.4 Exact and lowest-exact renderings (C1-8)

Every term has two SWAR spellings, each with a TAG:
- **LOWEST** (`haszero` on `x ^ rep(b)` or `(x & M) ^ rep(V)`). It flags every
  member lane and may flag a non-member lane only ABOVE a flagged member lane
  of the same term, because the borrow propagates upward only. The lowest flag
  of an OR of LOWEST terms is therefore a member: a false flag at lane `j`
  implies a true flag of that term below `j`. r17s checked this exhaustively
  for its cells.
- **EXACT.** Every lane's flag is its own membership:
  `~(((t & 0x7F..) + 0x7F..) | t) & 0x80..` on the same `t` for `EQ`/`CUBE`,
  and r17s's modular `ARC` spelling (already exact per lane).

**The rule:**
- a stateless find-first row may OR LOWEST terms;
- the stateful rows (§8), the complement form (§3.1) and any count/popcount
  use need EXACT.

The renderer takes the tag as an argument, and `mf_set_terms` returns kinds
and parameters only.

`[rev 2.2]` Every row revision 2.2 builds is stateful, so every rendering it
emits is EXACT. LOWEST stays in the renderer's vocabulary for one filed use:
the "stateless test first" twin (§17) may test a word with an OR of LOWEST
terms (any flag means the word holds a member) before it packs that word's
EXACT mask.

### 3.4a The per-width primitives and the shared helper block (`[rev 2.2]`, D155 addendum 4)

**The vocabulary.** For each width, the kit defines a small set of
primitives, and every form is readable text over them:

| primitive | meaning | SWAR (W 8) | SSE2 (W 16) | AVX2 (W 32) |
|---|---|---|---|---|
| a vector type | one load's worth of subject bytes | `unsigned long long` | a 16-byte vector | a 32-byte vector |
| `load_vector(p)` | the bytes `p[0 .. W)` as a vector, lane `i` = `p[i]`. **It owns byte order** (§6) | `__builtin_memcpy` plus the constant-folded byte-order normalization | the ISA's unaligned load (lane order is memory order) | the same |
| `eq(v, b)`, `cube(v, M, V)`, `range(v, L, W)` | the term masks of §3.1: EXACT lane flags, a flag vector of the width | §3.4's EXACT spelling (the flag in each lane's top bit) | a compare | the same |
| `vor(f, g)` | the union of two flag vectors | `\|` | the vector OR | the same |
| `lane_mask(f)` | the flag vector as an integer mask, bit `i` = lane `i` | the multiply-pack of §8.1 | movemask | the same |
| `first_lane(m)` | the lowest set bit's index | `__builtin_ctzll` | the same | the same |

- D155 addendum 4 names the vector type, `load_vector`, the term masks and
  `first_lane`; `vor` and `lane_mask` are the two connectives a form needs to
  OR several terms and pack ONCE, which is what the measured twins do (§8.1:
  EXACT terms ORed, then one pack per word).
- The integer masks of every width carry lane `i` at bit `i`, so NOT within
  the width (the complement form) and the pop-and-clear `m &= m - 1` are
  plain C operators, and `first_lane` is ctz at every width. The body never
  counts leading zeros (§6).
- The term parameters (`b`, `M`/`V`, `L`/`W`) are constants in the per-site
  helper's text; the primitives are set-independent.
- The spellings above are the kit's, PROPOSED; D157 holds: pcrec's site
  fields never name a primitive.

**The shared helper block.** The primitives are defined ONCE per file, in one
guarded block, on K80's precedent (the shared ABI block's VALUED guard):
- **Keyed to the abi AND a helper-set version.** The guard's value carries
  both. A translation unit that includes two artifacts whose blocks have
  different keys fails to compile with an `#error` naming the cause, as
  `PCREC_RX_ABI_H` does since K80. The same key means the same bytes, so the
  first block wins and later ones are skipped.
- **The block's bytes are a function of the key ONLY.** They never depend on
  the artifact's SIMD layer or on which primitives its sites use. This is
  what makes "first block wins" correct: if a SIMD-off artifact emitted only
  the SWAR width and a SIMD-on artifact came second in the same file, the
  second would find the guard defined and lose its wide primitives. So the
  block holds every width of its helper set. The wide widths' definitions sit
  under `#if` on the target's own macros (`__SSE2__`, `__AVX2__`) INSIDE the
  helper definitions, which D155 addendum 3 allows. They are `static inline`
  and unused in a SIMD-off artifact, so they produce no code there, and under
  C18's `-mgeneral-regs-only` preprocessing they vanish.
- **Emitted only when some site uses a primitive.** Only the block's
  PRESENCE depends on use. At R17-a no row uses a primitive, so no artifact
  carries the block and R17-a moves no byte. The block first appears in
  R17-b, inside that commit's one abi event (§11). Any later change to its
  bytes is a pcrec abi event in the same commit (memfn/CLAUDE.md, D146/D147).
- **Names carry the reserved kit stem.** The block is shared by artifacts of
  different prefixes, so its names cannot carry `<prefix>` or a site stem.
  They carry one fixed reserved stem (PROPOSED: `pcrec_mfk_`, with the guard
  `PCREC_MFK_H`), and pcrec reserves that stem in emitted files as it
  reserves `<stem>__*` (§7.6, §14 N5).
- **What it does NOT replace (yet).** The run compare's word-load helpers
  `<p>_w<W>` (`runcmp.c`, `mf_flush_helpers`) stay per artifact. Folding them
  into the block's SWAR `load_vector` is a filed unlock (§17).

`[rev 2.3]` **The first two bullets above ("keyed to the abi AND a helper-set
version"; "the block holds every width of its helper set") are SUPERSEDED by
§3.4b** (r5 K3-1, K3-8), and so is the single guard `PCREC_MFK_H` in the
names bullet: there is one guard per width (one shared guard is now S838's
plant). The other bullets stand, read per sub-block.

### 3.4b Per-width sub-blocks, keyed by K80 (`[rev 2.3]`, r5 K3-1, K3-8)

**What was wrong with one all-widths block (K3-1).** Revision 2.2 made the
block's bytes independent of the artifact so that "first block wins" stayed
correct in a file mixing SIMD-off and SIMD-on artifacts. The cost was four
defects:
- **Live SSE2 text in every default x86-64 build.** x86-64's baseline defines
  `__SSE2__`, so the SSE2 primitives inside a SIMD-off artifact's block were
  live definitions there, not vanished text. That breaks "SIMD-off is portable
  C" in spirit, even though the definitions are unused.
- **A later width moved every artifact.** Adding AVX-512 or NEON to the block
  changes its bytes, so every SIMD-off artifact moved for a width none of them
  uses.
- **Untested definitions (D77).** The wide primitives in a SIMD-off artifact
  are compiled and never executed by any SIMD-off test.
- **Headers.** A wide width that needs an intrinsics header would put an
  include into every artifact, breaking R17-b's `includes = 0` (§11.1 item 3).

**The design.** The block is split into ONE SUB-BLOCK PER WIDTH, each under
its own guard, each emitted only when some site in the artifact renders a
definition at that width:

| sub-block | guard (PROPOSED spelling) | holds | emitted in |
|---|---|---|---|
| W8 | `PCREC_MFK_W8_H` | the SWAR vector type, `load_vector` with its byte-order ternary and `_Static_assert` (§6), `eq`/`cube`/`range`/`vor`/`lane_mask`/`first_lane` over 64-bit words | every artifact with a `pf_terms_mask` mover, at either layer (the SWAR definition is the floor arm of the SIMD-on selector too) |
| V16 | `PCREC_MFK_V16_H` | the 16-byte primitives, the whole sub-block inside a file-scope `#if defined(__SSE2__)` | SIMD-on artifacts with a mover, once the SSE2 arm exists (§11.4) |
| V32 | `PCREC_MFK_V32_H` | the 32-byte primitives, inside a file-scope `#if defined(__AVX2__)` | SIMD-on artifacts with a mover, once the AVX2 arm exists |

- **Which width's sub-block is in a SIMD-off artifact: W8 only.** A SIMD-off
  mover renders only the SWAR `next_candidate`, which reads only W8's
  primitives. The W8 sub-block contains no `#if` and no SIMD text, so a
  SIMD-off artifact compiles to the same code on every target.
- **First-wins holds per sub-block.** A sub-block's bytes are a function of
  its width alone, within one abi (below). In a translation unit that
  includes a SIMD-off mover and then a SIMD-on mover, the first defines W8,
  the second skips its identical W8 and defines V16/V32, whose guards are
  still undefined. In the opposite order the second skips W8 only. In both
  orders every primitive any site calls is defined once, so the mixed-layer
  TU check (§12.7) holds by construction.
- **Why the SIMD arms stay at zero SIMD-off movers.** The arms add V16/V32
  sub-blocks and per-width `next_candidate` definitions to SIMD-ON artifacts
  only. A SIMD-off artifact's W8 sub-block, its definitions and its body are
  untouched, so the floor rule holds in the strongest form: SIMD-on is
  SIMD-off plus guarded sub-blocks and guarded definitions.
- **A new width is an event only for its users.** AVX-512 or NEON is a new
  sub-block plus a new arm of the selector. It moves the SIMD-on artifacts
  that render it (an abi event for them), and no SIMD-off byte.
- **Within a width, the content does not depend on the sites.** W8 holds all
  of its primitives even where a set uses only `eq`. This keeps first-wins
  correct between two SIMD-off artifacts whose sets use different term kinds.
  The unused `cube`/`range` definitions in an `eq`-only artifact are
  `static inline` and produce no code. They are executed by other movers in
  the corpus and by T5/G2 over the rendered sub-block, so nothing is
  untested (S842 holds this).
- **Headers.** W8 is header-free (`__builtin_memcpy`, `__builtin_bswap64`,
  `__builtin_ctzll`), so R17-b keeps `includes = 0`. V16/V32 are written with
  gcc vector extensions and `__builtin_ia32_*` builtins, which need no header.
  If an arm ever needs an intrinsics header, that is the trigger of the filed
  back-patchable include slot (§17), and it is the arms' question, not
  R17-b's.

**The key (K3-8): K80's guard, no version, no value.** Revision 2.2 keyed the
block to "the abi AND a helper-set version" and never said how the two are
spelled in one guard. Revision 2.3 drops both from the sub-block guards. Each
guard is a plain `#ifndef PCREC_MFK_<W>_H` / `#define PCREC_MFK_<W>_H`. The
reasons:
- **The version is redundant.** Every change to a sub-block's bytes is a pcrec
  abi event in the same commit (memfn/CLAUDE.md, D146/D147; §16.3). Two
  artifacts with one abi therefore have identical sub-blocks per width, and a
  version could only ever agree with the abi.
- **An abi value would be a second copy of K80's check, and the kit cannot see
  the abi.** `memfn.h` carries only `MF_SITE_ABI`, and `mf_art` has no field
  for `PCREC_ARTIFACT_ABI` (`src/gen/emit_dfa.c:54`). Valuing the guard with
  the abi would need a new contract field so that the kit can repeat a test
  pcrec already makes.
- **K80 already makes it, for every TU.** Every artifact emits the valued
  `PCREC_RX_ABI_H` guard, with its `#error` on a mismatch, in its prologue:
  in the `.c` before any engine text (`emit_dfa.c:13027`, inside the
  self-contained branch), or in the header the `.c` includes first
  (`emit_dfa.c:3417`). A TU that mixes two abis therefore fails at K80's
  `#error`, whatever the order of the kit sub-blocks inside it, because the
  second artifact's K80 test runs whether or not its sub-blocks were skipped.
  Inside a TU that compiles, there is one abi, and so one rendering per width.
- **The one gap is K80's own, not new.** An artifact from before K80 (an empty
  guard) included after a new one is the order K80 documents as unreachable by
  any emission (match_api.md §1¶7). Such an artifact predates the kit block
  and carries no sub-block.

So "keyed to the abi" stays true, through K80. What changes is that the kit
renders no number into its guards, and the `#error` a mixed-abi TU sees is
K80's ("shares a translation unit with an artifact of a different abi"),
which names the cause. S838 is re-aimed to match (§12.5): its rev 2.2 plant,
"the guard keyed on the abi only, the version dropped", is now the design.

**Names.** The sub-blocks' identifiers carry the reserved stem plus the width
(`pcrec_mfk_w8_load_vector`, `pcrec_mfk_v16_eq`, …; PROPOSED), so two widths'
primitives never collide. pcrec refuses a `-p` prefix inside the stem (N6,
§14), and reserves the stem in emitted files (N5).

### 3.5 Declines and the edges

- **Uncoverable.** No cover of `S` or of `¬S` within K terms, or BUDGET
  exceeded: `mf_set_terms` returns "none" and the row DECLINES (the next row,
  ultimately today's walk, takes the site). This is a decline, never a
  refusal: a wide, scattered set is a legal site.
- **|S| = 0.** Decline. pcrec builds no such PF site, since an empty start set
  is prefilter `none` (the artifact matches nothing), and the walk over an
  all-zero table would return `hi`.
- **|S| = 256.** Decline. pcrec's predicates exclude it (`pf_vm_start_applies`
  requires fewer than 256 members; a full DFA escape set has no prefilter).
- Both edges are in G2's generated set space (§12.1), so the declines are
  observed rather than assumed.

### 3.6 The cross-check against `pcrec_cube_of` (C3-14, D122)

`src/core/cpset.c:394` `pcrec_cube_of` (with `src/gen/clskit.c:182`'s caller)
is pcrec's own cube test. The kit links nothing from `src/`, so the analysis
exists twice by the boundary's construction. The two must agree.

**The check** (T4, pcrec-side, `tests/memfn/`, linked against `libpcrec.a`,
which contains both): for every byte class the corpus lowers, where
`pcrec_cube_of` says "one cube `(care, val)`", `mf_set_terms(set, 1)` must
return exactly `CUBE(care, val)`. Where it says "not one cube", the kit must
return no single CUBE. The kit may still return an ARC for a run, which is
recorded and is not a disagreement. The population is counted (K35): the
number of corpus classes for which `pcrec_cube_of` holds, with a literal floor
pinned in the test.

## 4. The forms and their row contracts

### 4.1 The rows, in first-match order

New rows sit in `memfn/src/pffind.c` (and `terms.c` for the shared renderer),
inside `arms[]`'s PF block. The order is:

    pf_memchr, pf_memchr_bounded,          (byte sites: unchanged)
    pf_terms_adapt, pf_terms_mask, pf_terms_ring, pf_memchr_set, pf_terms,
    pf_walk, pf_walk_bounded,              (today's walk: the floor, undeniable)
    pf_memchr_back                         (MLINE: unchanged)

The new rows' RELATIVE order (adapt / mask / ring / memchr_set / stateless) is
the follow-up measurement's output. Each row exists only if it wins somewhere
and loses nowhere its sites can be (D77, K-1), so §13's verdict deletes rows
from this list. The order shown is the expected one: stateful first, because
it is the dense fix; memchr_set below it, because Q-R5 measured it losing
dense; the stateless term-OR last before the walk.

`[rev 2.2]` **The order after the measurement (slot2):**

    pf_memchr, pf_memchr_bounded,          (byte sites: unchanged)
    pf_terms_mask,                         (the next_candidate row; W per width)
    pf_walk, pf_walk_bounded,              (today's walk: the floor, undeniable)
    pf_memchr_back                         (MLINE: unchanged)

`pf_terms_mask` is ONE row whose body use is `next_candidate` (§4.3). Its
implementation per width is the measured choice: `mask8_swar` (W = 8) at
SWAR; `mask64_sse2` and `mask64_avx2` (W = 64) as the later SIMD arms
(§11.4), each with its own deny. The rows the measurement deletes, each with
its reason, kept as filed notes behind the same interface (§17):

| row | fate | measured reason (`reading_slot2.md`) |
|---|---|---|
| `pf_terms_adapt` | NOT BUILT | answer 4: beats the better of `table` and its fast form beyond the band on 9/4/4 of 574 rows (best 0.95), loses on 401/393/447; its mode branch mispredicts (0.63 per call against `table`'s 0.038 at 300k) and it gives up sparse wins (`adapt_swar`/`swar` 1.45 at 70k) |
| `pf_terms_ring` | NOT BUILT | answer 3: loses to the mask in every regime (ring/mask 1.02-1.62 at `reset=inf`, 6.6-15x at `k4`/`call`); its one apparent win (SWAR percall L16, 0.56) is `mask64_swar`'s tail-path artifact, and the ring loses there to the AVX2 mask too (2.03) |
| `pf_terms` (stateless term-OR) | NOT BUILT | answer 1: `swar` loses at 150k-400k even when state could carry (1.15-1.31 median, 1.47 worst), and every R-17 site offers storage (W4), so the stateful row always outranks it; no site would fall through to it except where the walk is the right answer |
| `pf_memchr_set` (\|S\| = 1) | NOT BUILT | slot2 did not time it; step 2 measured `memchr` losing dense (+18% at 300k, Q-R5), and `pf_terms_mask` covers \|S\| = 1 with one `eq` term. No measured case keeps it (D77); filed with a trigger (§17) |
| `pf_terms_mask64` (SWAR, W = 64) | DESIGNED, NOT BUILT | answer 7: the best SIMD-off form at 1M (0.37 at 300k, 0.48 at 70k), but 3.98/5.43 at `reset=call` and 2.21/2.73 at percall L16 (the `hi < 64` tail path). Admitted only where the state survives the whole call AND every span is at least 64; no R-17 site states either fact today, so its population is zero (§4.3) |

### 4.2 The contract shared by every new row

In the convention of the existing PF rows (`PF_SERVES`, `PF_AT_ZERO` in
`pffind.c`; R1/R2 of `row_contracts.md`):

| field | serves | why |
|---|---|---|
| form / op / handoff | `STMT` / `FIND` / `ASSIGN` | `pf_shape` |
| reverse, guard_by_caller | `NO` | forward; a STMT is never caller-guarded |
| pred | `NONNEG`: one REQUIRED SET term at offset 0, `nterm` 1 | the degenerate span. Any offset other than 0 declines (C1-7). The MLINE shape at -1 stays `pf_memchr_back`'s. |
| window_stated, move_back, overshoot (W0-W2) | W0 `1` (0 is refused, every FIND row USES it); W1 `== d_min` (0 here); W2 `ZERO` | R-17 is the degenerate window: the window is the candidate. Any other value declines (R2), until R-18 relaxes it. `[r4 K2-4]` |
| empty | `E_NOP`, `E_EXCLUDED` | Every R-17 site is NOP. EXCLUDED renders the same text (the guard is redundant, never wrong). `AT_N` declines: no offset-0 site states it. `MISS` declines: no R-17 site states it, and its outcome would need `on_miss`. |
| end_back | `ZERO`, `ONE` | `hi = n - end_back`, written only under §5's guard |
| result | must be lo's text (in place) | as `walk_applies` |
| miss | the range's end: `MISS_N` at end_back 0, exactly `n - 1` at 1 | `miss_is_end`, re-read at use |
| on_miss | `0`: a stated one declines (R2) | no row runs it. pcrec's `if (pos >= n) return 0;` after the site stays pcrec's |
| on_miss_leaves | `NO` | kept as the define-time witness of an on_miss, as the walk rows (r4gfix) |
| s, n, lo | `IDENT` | pasted raw; side-effect-free bare identifiers, so pasting each more than once is safe (C1-6's "hooks evaluated once" is met by the class, not by binding). `[r4 K1-4]` On a row that keeps storage, `s` and `n` are USE-INVARIANT: the define hooks state them, and `mf_use` REFUSES a use whose `s` or `n` text differs from the define's. `end_back` is the site's, fixed at define, so no use can restate it. `[rev 2.3, r5 K3-2, K3-9]` **Superseded for `pf_terms_mask`:** `mf_locals` BINDS the define's `s`/`n` texts into the struct (and refuses `at` hooks stating different ones); `mf_use` pastes NEITHER and so compares neither: its guard reads the bound `<stem>__c.n` (§5). Only `lo` is pasted at a use. |
| decl_point (W4) | per row: `YES` on a row that keeps storage, `MF_ANY` on the others | R1: a storage row declines where pcrec offers no point |
| floor | unstated or `ZERO` | The stateful forms read below lo, down to 0 (the overlapped block, §8.1). A stated nonzero floor declines (R2). |
| fn_ref (W5) | `REF` (the stem) | R1: unstated declines. No name is presumed. |
| table_ref, table_name | per row (below) | rule 7: a row may ignore the table |
| note | `0` | a stated writer would lose its comment (R2), as the PF rows |
| policy | `MF_ANY` at SIMD-off; SIMD arms read `PORTABLE` (§11.4) | |
| freq (W6) | `MF_ANY`; only under §9.2's gate: the density class `D_SPARSE` | |
| `[rev 2.2]` analysis (W6) | not a field of R-17 (§2.2). When it is appended, the row serves every class except §9.2's decline class (density at or above `T_DENSE` AND a state-losing call pattern) | D162 addendum 1: absence ADMITS, so the selection is total without data |

### 4.3 Per row

| row (deny) | serves beyond §4.2 | text | storage | libc / includes |
|---|---|---|---|---|
| `pf_memchr_set` (`--memfn=no-pf-memchr-set`) | \|S\| = 1, any `table_ref` (not read) | one compound statement `{ const void *<stem>__q = __builtin_memchr(s + lo, b, hi - lo); lo = <stem>__q ? (size_t)(...) : hi; }` under §5's guard. Its OWN braces, so it assumes no enclosing pcrec brace (C3-4). A statement-expression is unnecessary for a STMT form. `[r4 K2-6]` `__builtin_memchr` needs no declaration, so the row is HEADER-FREE (§11.1 item 3); it is still a libc call and is noted as `memchr` in `MEMFN_LIBC` (a source-level inventory) | none (a block-scope pointer) | `memchr` (noted); no include |
| `pf_terms` (`no-pf-terms`) | a cover of ≤ K terms (§3), LOWEST renderings allowed | a file-scope `static inline size_t <stem>__find(const unsigned char *s, size_t lo, size_t hi)`: the SWAR term-OR word loop while `i + 8 <= hi`, then the lane-predicate byte tail. The use is ONE statement under §5's guard: `lo = <stem>__find(s, lo, hi);` | none | none (`__builtin_ctzll`, `__builtin_memcpy`; no `<stdint.h>`: `unsigned long long`, C1-14) |
| `pf_terms_mask` (`no-pf-terms-mask`) | as `pf_terms`, EXACT renderings, `decl_point` `YES` | file scope: a struct type `<stem>__c` `{ size_t base, top; unsigned long long m; }` and `static inline size_t <stem>__find(struct <stem>__c *c, const unsigned char *s, size_t lo, size_t hi)` (§8.1). Body: `struct <stem>__c <stem>__c = { 0, 0, 0 };` at `mf_locals`, then `lo = <stem>__find(&<stem>__c, s, lo, hi);` per use | one struct, 24 bytes | none |
| `pf_terms_ring` (`no-pf-terms-ring`) | as mask | as mask; the struct adds `unsigned short pos[RING]; unsigned rh, rt;` with `RING` `UNMEASURED DEFAULT: 256` (one fill = 4 blocks of 64). Its initialization ASSIGNS the scalar fields (`base`, `top`, `rh`, `rt`). It is never an aggregate initializer: in C, `= { 0 }` zero-fills `pos[]` too, 512 bytes per call (§7.3). `[r4 K1-8]` gcc may report `pos[]` maybe-uninitialized under `-Werror`; the ring witness is compiled at `-O2` and `-O3` in test-codegen | one struct, ~536 bytes | none |
| `pf_terms_adapt` (`no-pf-terms-adapt`) | as mask, plus `table_ref` `REF` at define and `table_name` stated at every use (its walk mode reads pcrec's table, rule 7) | §9.1: mode counters in the same struct; the fast mode is the mask form (or the stateless form, whichever §13 keeps); the walk mode is today's `while (lo < hi && !T[s[lo]]) lo++;`. `[r4 K1-1]` **`T` is a PARAMETER of the file-scope helper** (`..., const unsigned char *T)`), and each use passes `table_name(table_ref)`'s text: `lo = <stem>__find(&<stem>__c, s, lo, hi, <p>_start_set);`. pcrec's tables are function-local statics (`emit_u8_table`, "emitted INSIDE the search function", `emit_dfa.c:3446`), so a helper above the function cannot name one; revision 2's text did not compile. This is `<p>_ofsskip`'s shape (`ofsskip.c` `table_params`) | one struct (+ 2 counters) | none |
| `pf_walk`, `pf_walk_bounded` | unchanged | unchanged | none | none |

Each new row is SCALAR layer (Q50): SWAR on ordinary integers, plus libc for
memchr_set. Its SIMD arms are later rows of the SAME helper (§11.4), each with
its own deny per (form, width) (Q-R9-7).

`[rev 2.2]` **The rows revision 2.2 builds**, superseding the table above for
the forms that were not kept (their lines stay as the record of what was
designed):

| row (deny) | serves beyond §4.2 | body text (the only text inside pcrec's function) | file-scope text | storage |
|---|---|---|---|---|
| `pf_terms_mask` (`--memfn=no-pf-terms-mask`) | a cover of at most K = 4 terms (§3.3), EXACT renderings; `decl_point` `YES`; `table_ref` not read | at `mf_locals`: `struct <stem>__c <stem>__c = { s, n, 0, 0, 0 };` (the hook texts of the define); at each use, under §5's guard: `lo = <stem>__next_candidate(&<stem>__c, lo);` | the struct type `<stem>__c` `{ const unsigned char *s; size_t n; size_t base, top; unsigned long long m; }`; `static inline size_t <stem>__next_candidate(struct <stem>__c *c, size_t lo)`, the §8.1 mask form at W = 8, written over the shared block's SWAR primitives with the set's term constants; the shared block itself (§3.4a), once per file | one struct, 40 bytes |
| SIMD arms of `pf_terms_mask` (`pf-terms-mask-w16`, `pf-terms-mask-w32`; `MF_L_SIMD`) | as the row; `policy` `PORTABLE` read (§11.4) | **identical** to the row's | per-width definitions of `<stem>__next_candidate` (W = 64 from four 16-byte or two 32-byte loads), chosen by the `#if` chain at file scope (§11.4) | the same struct |
| `pf_terms_mask64` (`no-pf-terms-mask64`), NOT BUILT | as the row, plus two facts no site states today: the state survives the whole call (a `reset=inf` call pattern, i.e. [FINDALL-NEXT]'s cross-call state or a stated call-pattern kind) AND a span-length class of at least 64 at every use | the same body | `<stem>__next_candidate` at W = 64 over the SWAR primitives | the same struct |

- **`next_candidate(&state, lo)` is the whole body contract** (D155
  addendum 4.1). The struct binds the two use-invariant inputs, `s` and `n`,
  at the declaration point, so a use passes only the cursor. That is legal
  because pcrec guarantees and the kit checks that `s` and `n` do not change
  across the site's uses (G-S1/G-S2, §7.4): `mf_locals` refuses hook texts for
  `s`/`n` that differ from the define's, and `mf_use` refuses an `n` text that
  differs (the guard names `n`). `[rev 2.3]` The `mf_use` half is withdrawn:
  the guard names the bound `<stem>__c.n` (next bullet but one). The struct
  binds `n`, not `hi`: the helper
  forms `hi` from `c->n` and the site's constant `end_back` and runs only
  under §5's guard, which has already proved `n - end_back > lo`, so `hi` is
  formed only where §5 says it cannot wrap. (Binding `n - end_back` at the
  declaration would also give right answers, because at `n = 0` the wrapped
  value is never read; binding `n` keeps §5's "formed only where it cannot
  wrap" literally true and keeps clang's opt-in unsigned-overflow sanitizer
  quiet.)
- `[rev 2.3, r5 K3-2, K3-9]` **The guard reads the bound `n`, and the
  refusals are ONE comparison, at `mf_locals`.** Revision 2.2's body pasted
  the LIVE `n` hook into the guard while the helper read the BOUND `c->n`.
  Text equality between the two hook texts cannot see a reassignment of the
  variable between the declaration and a use, so the guard and the helper
  could disagree about `hi`. Worse, r4 K1-4's trace re-probe recomputed
  `F(lo)` from the same `c->s`/`c->n` the helper read, so it compared the
  helper with itself. Revision 2.3's body is:

      at mf_locals:  struct <stem>__c <stem>__c = { s, n, 0, 0, 0 };
      at each use:   end_back 0:  if (lo < <stem>__c.n) lo = <stem>__next_candidate(&<stem>__c, lo);
                     end_back 1:  if (lo < <stem>__c.n && <stem>__c.n - lo > 1) lo = <stem>__next_candidate(&<stem>__c, lo);

  (`s`, `n` and `lo` stand for the hook texts.) The guard and the helper now
  read one value, so they cannot disagree. The use pastes only `lo`.
  - **`mf_locals` binds:** it renders the declaration from the DEFINE's `s`/`n`
    texts, and refuses `at` hooks whose `s` or `n` text differs from the
    define's (a different text at the declaration point would bind a
    different variable). This is the one remaining text comparison.
  - **`mf_use` checks neither:** it does not paste `s` or `n`, so there is
    nothing to compare. §8.2, §11.1 and §12.7 are read with this.
  - **K1-4 restored, in the trace rendering (§12.4a):** each use's trace form
    pastes the live hooks and traps unless `<stem>__c.n == n && <stem>__c.s ==
    s`. That compares the bound copy with the live variable, which is the
    reassignment the text refusals cannot see.
  - **And the compiler checks it first (K3-3, §7.4):** R17-b declares the
    holding function's `subject` and `subject_length` const, so at every R-17
    site a reassignment does not compile.
- **The body never changes.** Every width, and any future form behind the
  interface (a ring, an AVX-512 mask), renders the same declaration and the
  same use statement; only the file-scope definitions differ. §12.7's
  body-invariance check holds that.
- **What binding `s`/`n` in the struct costs is OWED.** The measured twins
  passed `s` and `hi` as arguments. With the helper inlined and the struct a
  local of the function, gcc should keep both in registers; the disassembly
  check owed with R17-b (§13.4) reads it, and a measurable cost there is a
  reason to pass `s` explicitly (the body contract would then be
  `next_candidate(&state, s, lo)`, still width-invariant).

**Why a helper, not inline pieces.** Ruling 3: "if the code can be neatly put
into a function then that works too and I agree with A". Every form above
fits one `static inline` helper plus one use statement:
- gcc inlines it, so there is no call on the hot path. That is OWED to the
  follow-up's disassembly check, R17-b's acceptance;
- the floor rule then puts SIMD in the helper's DEFINITION (§11.4), never in
  the body.

The composable-pieces shape (the cache pop inline in the body, the refill a
helper call) is ALLOWED by D155 addendum 3. It is kept as the measured
alternative if a twin shows the inlined helper losing (§13.4, form
`mask64i_swar`).

`[rev 2.2]` **Measured: the shapes are equal.** `mask64i_swar` (the refill as
a separate call) equals `mask64_swar` within noise in every regime of slot2's
answer 1 (0.99 against 0.98 at 300k, 0.67 against 0.73 at 70k, 3.98 against
3.98 at `call`). So composing from pieces costs nothing measurable, which is
what lets each width's `next_candidate` be written as text over the
primitives (D155 addendum 4) rather than as one opaque kernel.

## 5. Range arithmetic: n = 0, NOP, no wrap (C1-1)

The non-wrapping guard, spelled once, in every new row's use:

    end_back 0:  if (lo < n) { <hi is n>     ... }
    end_back 1:  if (lo < n && n - lo > 1) { <hi is n - 1> ... }

- `n - lo` is evaluated only when `lo < n`, so it never wraps.
- `n - lo > end_back` implies `n - end_back > lo >= 0`, so the `hi` text
  (`n - 1`) is formed only where it cannot wrap. That is §14.4's rule spelled
  as a remainder. r17s's `hi = n - end_back` before any test was C1-1's
  BLOCKER.
- `s + lo` (memchr_set) and every subject read sit inside the guard. At
  `n = 0` with `s == NULL` (K27, a legal subject), nothing reads `s` and
  nothing forms `s + lo`. Passing a null `s` into a helper call never happens
  either, because the call is inside the guard.
- `lo > n` is legal and empty (Q-G2-1). It fails `lo < n`.
- `[rev 2.3, r5 K3-2]` On `pf_terms_mask` the `n` in both guard spellings
  above is the bound `<stem>__c.n`, not the hook text (§4.3). The arithmetic is
  unchanged; the guard and the helper read one value.
- `[rev 2.2]` The guard stays in the BODY, around the
  `next_candidate` call, and is part of the width-invariant body text
  (§4.3). The declaration `{ s, n, 0, 0, 0 }` copies the pointer and the
  length only; it reads no subject byte and forms no `s + k`, so it is safe at
  `n = 0` with `s == NULL`.
- **The NOP outcome.** On an empty range NOTHING is written: no `lo`, no
  cache field, no adaptive counter. The stateful cache is therefore untouched
  by an empty use, which §8.2's proof relies on.
- **The cache test's wrap is deliberate and defined.**
  `(size_t)(lo - base) < (size_t)(top - base)` is unsigned modular arithmetic,
  used as a two-sided interval test (§8.2 step 1). It is not a range bound,
  and UBSan's gcc arms do not flag unsigned wrap, which is defined
  behaviour. clang's opt-in `-fsanitize=unsigned-integer-overflow` would flag
  it, but clang is not a target compiler.

## 6. Endianness with no `#if` in body code (C1-2, C3-8)

`[rev 2.2]` **Endianness moves INTO `load_vector`** (D155 addendum 4: "`load_vector`
(owns byte order)"). The one spelling below is now the body of the shared
block's SWAR `load_vector` (§3.4a), and nothing else in the file spells byte
order: not the per-site `next_candidate`, not the search function's body. The
vector widths need no normalization, because their loads put byte `i` in lane
`i` on every target they exist on. Every mask therefore carries the
lowest-address lane at bit 0, and **the body always counts trailing zeros**
(`first_lane` is ctz at every width). That closes C1-2 by construction: there
is no second site that could disagree with the first, so the residual "does
the BE branch compose" reduces to "is `load_vector`'s SWAR normalization
right", which the byte-swapped test below answers. The `_Static_assert`
moves into the shared block with it. S836's plant is now the inverted ternary
inside that `load_vector` (§12.5). The rest of this section stands, read with
"the helper" meaning the shared block's SWAR `load_vector`.

**ONE spelling, at the word LOAD, in the helper.** The loaded word is
normalized so that byte `i` of memory is bits `8i..8i+7`:

    unsigned long long w;
    __builtin_memcpy(&w, s + i, 8);
    w = __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__ ? __builtin_bswap64(w) : w;

It is a constant-folded ternary: no `#if`, and gcc's own predefined macros
(the artifacts are gcc-dialect already). After it, every lane computation is
little-endian logic:
- `ctz(z) >> 3` is the lowest-address flagged lane;
- `z &= z - 1` pops it;
- §8.1's `pack` multiply gathers lane `i`'s flag into bit `i`.

**Why at the load.** A per-use ternary between `ctz` and `clz` (the panel's
suggestion) would need a second ternary at every pop and at the pack. The
load-site form is ONE place, and on LE it compiles to nothing.

**PDP endianness.** The helper region carries a file-scope
`_Static_assert(__BYTE_ORDER__ == __ORDER_LITTLE_ENDIAN__ || __BYTE_ORDER__
== __ORDER_BIG_ENDIAN__, "...")`, a declaration and not an `#if`. A target that
is neither refuses to compile instead of answering wrongly.

**The load is `__builtin_memcpy`** (`[r4 K2-10, r3 C3-8]`: decided now, no
longer a lean). A constant 8-byte copy is a register load, needs no
`<string.h>`, and is not noted as libc (`mf_art_note_libc`'s exclusion). So
the terms rows are header-free (§11.1 item 3). r17s's twins and the follow-up
harness keep `memcpy`; it is the same instruction.

**What a check can reach.**
- On the boxes (x86-64 and arm64, both LE), the rendered helper is compiled
  with `-U__BYTE_ORDER__ -D__BYTE_ORDER__=__ORDER_BIG_ENDIAN__` (C9-style),
  which proves the BE text compiles.
- `[r3 C1-2 residual]` **A byte-swapped LE ANSWER test.** In a test TU under
  `tests/memfn/`, the rendered helper is compiled with `__BYTE_ORDER__`
  flipped to `__ORDER_BIG_ENDIAN__` AND with the load made to return what a
  big-endian load returns: `#define __builtin_memcpy(d, s, n) mf_t_rev_load(d,
  s, n)`, a test function that copies `n` bytes in reverse order (a
  preprocessor macro may shadow a builtin's name in a test TU). The ternary
  then swaps the reversed word back, so the lane logic must give the same
  answers as on LE: the T5 kernel test and the Q1-Q7 sequences run through
  it against the byte loop. This answers "does the BE branch compose to the
  right result", which the compile check could not.
- What stays UNREACHED is a real BE target's code generation; no BE target
  or qemu-user exists here, and that is stated, not claimed.
- S836 (§12.5) plants the inverted ternary. Every LE test catches it, and the
  byte-swapped test catches it in the BE arm.

**C4 needs no change** (`[r4 K2-10, r3 C3-8]`, decided). `__BYTE_ORDER__` and
`__ORDER_*` appear in kit-rendered text only (string literals in `terms.c`)
and in the kit's own tests. C4 scans `src/`, `cli/`, `lib/` and `tests/`
except `tests/memfn/`, and `memfn/` is exempt by design
(`tests/memfn/arch_blind_check.py`'s header), so neither revision 2's
allowlist entry nor a `memfn.h`-only forbid is needed. A check that must name
the tokens lives in `tests/memfn/`.

## 7. Kit-owned local storage: what pcrec provides (main's question)

This section is the answer to main's question, as facts and capabilities
(D157). For each item: what pcrec PROVIDES or GUARANTEES, then per site kind.

### 7.1 A declaration site and scope

**The capability.** A new kit call, PROPOSED (`MF_SITE_ABI` 11):

    /* Writes the declarations (with initializers) of site `handle`'s
     * kit-owned local storage into `body` at pcrec's indent, or nothing when
     * the chosen form needs none. Called once per site, before its first
     * mf_use, at a point that DOMINATES every use (§7.2). */
    int mf_locals(mf_art *, uint32_t handle, const mf_hooks *at, mf_sink *body);

- pcrec states `decl_point = 1` (W4, a host capability) on every site it will
  call this for. With 0 (MLINE, the byte sites) a row that keeps storage
  declines (R1).
- The kit may write NOTHING (D155 addendum 3: "or even decide if it should be
  emitted or not"). pcrec calls it unconditionally where it offered.
- **Ordering, enforced kit-side.** For a row that keeps storage:
  - `mf_use` before `mf_locals` is REFUSED;
  - `[r4 K2-9]` a SECOND `mf_locals` on the same handle is REFUSED ("storage
    placed twice"). The error is sticky, so it surfaces at `mf_art_end` at
    the latest;
  - `mf_art_end` refuses a site whose `mf_locals` never came ("declared
    storage, never placed"), as it refuses an unused handle today;
  - `[r4 K1-8]` `mf_art_end` refuses storage that was placed but that no use
    read ("placed, never read"), which would otherwise be an unused variable
    under `-Werror`.
- This is the kit-declared MIRROR of `count_by_caller` (MF_SITE_ABI 5). There
  the CALLER declares and owns state the kit advances; here the KIT declares
  and owns state at a point the caller provides.

`[r4 K1-6, K2-9]` **The points are in the FORWARD-LOOP CALLERS, not in
`emit_scan_loop`.** Revision 2 put the DFA point inside `emit_scan_loop`,
which is shared: `emit_reverse_block` (`emit_dfa.c:11122`, called once per
seed by the rev-end walk and once by RECOVER's reverse pass) and the anchored
match-here (`:11760`) emit copies of the same loop. Neither copy carries a PF
use, but a point inside the shared loop would place the storage once per
copy, a redeclaration in one function. The point is keyed on the FORWARD PF
site instead and sits in its one caller, `unanch_scan`.

| site kind | the define point (file scope, §11.1) | the declaration point pcrec provides | scope |
|---|---|---|---|
| DFA prefilter (the search body, or the hybrid's inlined prefilter body) | the new `u.pf.emit_block` of the set rows, called at `emit_dfa.c:11387` (`emit_unanchored`), above the body | in `unanch_scan`, immediately before `size_t scan_position = …`, i.e. before its `emit_scan_loop` and so before `emit_init` and the `seedhead` `goto` | function scope of that body, enclosing the `for (;;)` and every PF use |
| DFA hat (`first-class-bounded`) | the same: it is the same loop's PF slot | the same | same |
| the rev-end walk's RELOCATE (a tie with no anchored machine) | the same `emit_block`, called at `:11571` (`emit_rev_end`); in that artifact it is the only forward PF site | the same point in `unanch_scan`, which the relocate calls at function scope after the walk's `if (!revend_tie) { … }` block | function scope of the rev-end body |
| VM hat entry + retry (`<searchfn>_run`) | in `vm_emit_search_body`, beside `pcrec_emit_req_run_blocks` (`emit_vm.c:13130`), above the `_run` head | immediately BEFORE the entry seek (`emit_vm.c:13464`, after K73's `pcrec_emit_start_zero`) | function scope of `_run`, enclosing the entry seek and the `for (;;)` holding the retry seek |

An artifact holds at most one forward PF site or one VM hat, never both: on a
DFA artifact or a hybrid every VM-route row but `none` declines
(`vm_start_row`'s header), and `emit_rev_end` and `emit_unanchored` are
alternative bodies for one `fn`.

### 7.2 Lifetime across candidates within one call

**pcrec guarantees** that the storage is AUTOMATIC (block-scope, no `static`,
no file scope) and lives for one activation of the function that holds the
uses: one search call.
- The matcher stays reentrant. This is [OPT-HYB-RESEED]'s rule: "the state is
  the CALL's, never the artifact's, so the matcher stays reentrant"
  (`emit_vm.c` `reseed_decl`).
- Within the call, every use of the site sees the storage as the previous use
  left it. No pcrec text writes it, and pcrec never takes its address.
- **DOMINANCE.** Every path from the function's entry to any use passes the
  declaration point. NO `goto` or computed `goto` jumps from before the point
  to after it.
  - This is load-bearing: C lets a `goto` skip an initializer, which leaves
    the storage indeterminate.
  - The DFA loop's `goto <p>_..._scan_edge` (`emit_scan_loop`, the `seedhead`
    jump) is emitted AFTER `emit_init`. That is why §7.1 places the point
    before the loop, in `unanch_scan`.
  - pcrec's guarantee is the property, not a line number. A future pcrec
    change that adds a jump past the point breaks it.
  - `[r4 K1-7]` **The property is CHECKED.** test-codegen compiles every
    R17-b mover with `-Wjump-misses-init` and fails on any diagnostic that
    names a `<stem>__` identifier (the filter keeps pcrec's own unrelated
    jumps out of the check). gcc diagnoses a direct `goto` or `switch` that
    skips an initialization; it does not analyze a computed `goto`. Neither
    body that holds a point emits one: the DFA bodies' jumps are the scan
    loop's direct `goto <label>` (`emit_scan_loop`), which the warning does
    analyze, and `_run`'s own text (`emit_vm.c:13136-13600`) writes no `goto`
    (VM dispatch lives in the matcher function it calls). The DFA's computed
    `goto *targets_K[class]` belongs to ENG_ATTEMPT (`emit_dfa.c:4593`), which
    holds no set PF site with storage. A future computed `goto` in a body with
    a point would need its own argument.
- Across calls: nothing. A find-all's next call starts with fresh storage.
  Cross-call state is OUT OF SCOPE (§17, the unlock).

### 7.3 Initialization at entry

**The kit's text initializes**, in the declaration itself (`= { 0, 0, 0 }`),
so the initial state needs no separate pcrec statement.
`[rev 2.2]` The built row's declaration is `= { s, n, 0, 0, 0 }` (§4.3): the
two use-invariant inputs and an empty cache. The ring is not built, so no
built form needs the assigned-fields shape below; the rule is kept for any
later form behind `next_candidate` that holds an array.
- A form whose storage holds an array the initial state never reads (the
  ring's `pos[]`) assigns its scalar fields as statements at the same point
  instead. C's aggregate initializer zero-fills every remaining member, which
  would cost the ring 512 bytes per call (the twins' `sreset`).
- `mf_locals` therefore writes declarations AND statements, all of them at
  the one point. pcrec guarantees that
the declaration executes exactly once per call, before any use (§7.2's
dominance), and never again in that call: the point is not inside a loop.
- On the VM route the declaration sits at function scope above the attempt
  loop.
- On the DFA route it sits above the scan loop. A DFA function that runs its
  forward loop once per call satisfies this today. A future DFA retry loop
  that re-enters the forward scan inside one call would also be fine, as long
  as the point stays above it, since the cache is answer-safe across any
  sequence (§8.2).

### 7.4 pcrec's guarantees about the cursor between uses

**pcrec guarantees, for the storage's whole lifetime:**
- **(G-S1)** the subject pointer's value and the bytes `s[0 .. n)` do not
  change. pcrec's text never writes the subject, and `s` is the function's
  parameter;
- **(G-S2)** the `n` hook's value and the site's `end_back` do not change, so
  `hi` is the same at every use;
- **(G-S3)** each use's `lo` is an arbitrary value, which pcrec MAY have
  moved in any direction since the previous use. **Nothing about the cursor
  is promised.**

`[r4 K1-4]` **G-S1 and G-S2 are CHECKED, not only promised:**
- `mf_use` refuses a use whose `s` or `n` hook text differs from the
  define's (§4.2). `end_back` cannot differ: it is the site's;
- a C-check in test-codegen reads each mover's holding function after the
  `<stem>__c` declaration and fails on any assignment, increment or
  compound assignment to the `s` or `n` identifier (today none exists: the
  end-window clamp writes the position, never `subject_length`,
  `emit_dfa.c:1031`);
- the TRACE rendering (§12.4a) re-probes every cache hit against the byte
  loop and asserts `top <= hi` after every fill, so a corpus run under the
  trace build is a standing oracle for both.

`[rev 2.3, r5 K3-2, K3-3]` **Revised.** The first bullet is now `mf_locals`'s
binding refusal only (§4.3); `mf_use` pastes no `s`/`n`. `[r17c, review
2026-10-12-r1 A-S1]` **Restored at `mf_use` too:** a use's `s`/`n` hooks still
state the range the host asks about, so on a `decl_point` site `mf_use`
refuses a stated `s` or `n` whose text differs from the binding (the same
`same_text` comparison `mf_locals` makes), naming the field. It is a static
refusal; the trace rendering's trap stays the run-time line. C5's gate cases
`use-n-differs`/`use-s-differs`, G2's binding fixture and sabotage S867. The trace rendering
now traps on `<stem>__c.n != n || <stem>__c.s != s` at each use, which compares
the bound copy with the live variable (§12.4a). And the compiler enforces
G-S1's pointer and G-S2 first:
- **R17-b declares the inputs const in every body holding a stateful site.**
  The holding functions take the subject as parameters: `<searchfn>` (and the
  hybrid's static prefilter, which shares its head, `emit_dfa.c:1806`) and
  `<searchfn>_run` (`emit_vm.c:13137`). In those definitions R17-b spells the
  two parameters `const unsigned char *const subject` and
  `size_t const subject_length`. Top-level qualifiers on a parameter in a
  definition do not change the function's type (C11 6.7.6.3¶15), so the
  prototypes in the header and the `_in` delegates are untouched. The
  precedent is already emitted: the VM's match-here entry declares
  `const unsigned char *const subject` and `const size_t subject_length`
  (`emit_vm.c:12786-12787`).
- **No emitted text writes either today.** A grep of every emitted string in
  `src/gen/` for an assignment, increment or compound assignment to `subject`
  or `subject_length` finds only the match-here entries' own initialized
  locals (`emit_dfa.c:11736-11737`, `:11842-11843`, `emit_vm.c:12786-12787`),
  which are other functions. The H3 end-window sites assign `window_end`, never
  `subject_length` (`emit_vm.c:13311-13312`, `:13444-13448`). So the const
  qualifiers compile everywhere and move no answer.
- **It is part of R17-b's one abi event**, and it moves no artifact R17-b does
  not already move: the qualifiers are emitted only in bodies that hold a
  stateful site, and every such body is a mover.
- **The textual C-check becomes the FALLBACK.** It stays in test-codegen as a
  second line over every mover (it reads the artifact text; the compiler reads
  the types), and it is the only line for any future hook text that is not a
  parameter the body can const-qualify. At R17-b every `s`/`n` hook is
  `subject`/`subject_length`. The bytes `s[0..n)` are the caller's: `const`
  stops pcrec's text from writing through the pointer, and G-S1's "the bytes do
  not change" stays the caller's contract (match_api.md).
- The r5 unlock **`inputs_const`** (a host fact stating that the holding
  function's `s`/`n` are const-declared, so the kit could skip its refusals) is
  filed (§17), not built: one stateful site kind does not need it.

The stateful forms are correct under G-S1 and G-S2 alone (§8.2). Monotonicity
does hold today on both routes:
- the DFA forward position only grows within the loop;
- the VM's `attempt_position` grows by the encoding's advance (K49) between
  uses.

**Not requested** (D77, D157): no form needs it. The cache test
`(lo - base) < (top - base)` is ONE compare covering both directions (§8.2
step 1), so a stated monotonicity fact would buy nothing. It is filed as an
unlock (§17).

### 7.5 Several sites in one function

- **One storage per SITE (handle).** Two uses of one site share it. The VM hat
  is ONE site, defined once above `_run` (§7.1), with `mf_locals` once at the
  entry and TWO `mf_use` calls (entry and retry). Today it is two `mf_emit`
  calls (C3-7).
  - Sharing is answer-safe because both uses have the same set, the same
    subject and the same `hi` (G-S1/G-S2, `end_back` 0 at both).
  - It is also the win the stateful form exists for: the retry seek pops from
    the block the entry seek filled.
- **Two different sites in one function** (a future case; today a function
  holds at most one PF site) get two storages, named apart by their stems
  (§7.6).
- A site's uses all lie in ONE function. `[r4 K1-5]` **Revision 2's "refused
  at `mf_use`" is WITHDRAWN as unenforceable, and the r4 disposition's
  replacement (compare the body-sink pointer at `mf_locals` with every
  `mf_use`) cannot work either**: pcrec hands the kit a fresh stack adapter
  per call (`PcrecMfSink ps;` in `pcrec_memfn_define`/`_use`/`_call`,
  `src/gen/memfn_sites.c:357,371,379`), and every function of an artifact
  writes into the one buffer `job->csb`, so neither the sink pointer nor its
  `u` can tell two functions apart. The property holds by two detectors that
  need no kit knowledge of functions:
  - a use in a function where the storage was never declared names an
    undeclared identifier (`<stem>__c`), a compile error in every build that
    compiles the artifact;
  - storage declared in two functions needs two `mf_locals` on the handle,
    refused as "placed twice" (§7.1).

  The kit-side form is the r4 unlock "a function token on `mf_locals`/
  `mf_use`" (§17), whose trigger is a site whose state must be checked
  without a compile.
- The hybrid's prefilter function is a different function from `_run`: its PF
  site is its own site with its own storage, which lives for one call of the
  prefilter function (§17's `state_by_caller` unlock is the cross-call
  variant). `[r4 K2-11]` That function is entered once per VM re-seed, so its
  storage is initialized per entry with few uses: the `reset=1`/`reset=4`
  regime of §13. A row that keeps storage is admitted there only if §13's
  `reset=1` and `reset=4` rows show no loss beyond the band. If they do show
  one, R17-a states a host fact on that site, the r4 unlock "uses per
  activation" (`activation = MF_ACT_PER_RETRY`), and the storage rows (mask,
  ring and adapt) decline on it. The dense protection there then rests on
  whatever §13 keeps without storage, under K-1: a stateless row that loses
  dense is not built at all, so that site keeps today's walk.
  - `[rev 2.2]` **Measured, and now governed by D162 addendum 1.** At 300k
    `mask8_swar` reads 0.98/1.19 at `k4` and 1.65/1.83 at `call` (slot2
    answer 2), so the `reset=1` row does show a loss. Under revision 2.1's
    rule that would make the storage row decline here unconditionally. D162
    addendum 1 replaces that rule: the row ADMITS by default, and declines
    only on positive evidence of density at or above `T_DENSE` together with
    a state-losing call pattern. A per-retry activation IS a state-losing
    call pattern, stated structurally by pcrec, so the `activation` host fact
    becomes the call-pattern half of §9.2's decline predicate, not a decline
    by itself. Without a density kind the hybrid's prefilter site admits
    `pf_terms_mask`, and its measured regret is bounded by the `call` row
    (≤ 1.83 worst at 300k) against wins of 0.35-0.65 at 20k. Whether real
    hybrid cells lose beyond the floor is the bench relay's question
    (§11.2a; the hybrid cells are named there).
  - `[rev 2.3, r5 K3-4]` **WITHDRAWN: "A per-retry activation IS a
    state-losing call pattern".** One activation per re-seed is not "state
    lost". Inside one entry of the hybrid's prefilter function, every candidate
    the inlined DFA REJECTS sends the scan back to the PF site, and each of
    those is one more use of the same storage in the same activation. How many
    uses an activation serves is a property of the subject and the pattern,
    not of the site's structure. So `activation = MF_ACT_PER_RETRY` is a PROXY:
    it says where few uses per activation are possible, never that they occur.
    §9.2's (P) is redefined as a count of uses per activation, and the
    structural fact alone no longer satisfies it.

### 7.6 Hook-safe naming under `-p` (C1-6)

- **The stem is pcrec's.** pcrec states `fn_ref` (W5) on each storage-offering
  STMT site. Its `fn_name` hook returns a stem. `[r4 K2-9]` **The stem is the
  name of the function holding the site's uses, followed by `_pf`**: for
  example `<searchfn>_pf` in the DFA search body, `<prefilter>_pf` in the
  hybrid's prefilter body, `<searchfn>_run_pf` for the VM hat. Two bodies in
  one artifact therefore never share a stem, and the rev-end relocate, whose
  uses sit in the rev-end body, gets its own by construction. Revision 2's
  per-kind tags (`_pf`, `_pfp`, `_vmhat`) would have needed a new tag for
  every new body.
  - It is rendered through D143's placeholder like every pcrec name, so `-p`
    renames it.
  - This follows the FUNC precedent: "A FUNC site's OWN name is always its
    `site.pred.fn_ref`" (memfn.h), and vrun's `<fn>__body`/`<fn>__w16`.
  - `[r4 K1-11]` **The stem is OPAQUE to the kit.** It arrives holding the
    K79 placeholder (`\x01q…`, `src/core/internal.h` `PCREC_PREFIX_PLACEHOLDER`)
    and is rendered to the prefix only when pcrec renders the whole artifact.
    The kit never inspects, compares, case-maps or measures it, and writes it
    only through the sink's `puts`/`vprintf`: never through `cstr`,
    `comment_byte` or `legend_byte`, because a placeholder that passes through
    an escaper is escaped and never rendered (that header's "one seam").
- `[rev 2.3, r5 K3-11]` **Why comparing UNRENDERED text is sound.** The
  kit's one text comparison (`mf_locals`' `s`/`n` against the define's, §4.3)
  compares hook texts as BYTES, before pcrec renders the placeholder
  (`\x01q` → the prefix, `\x01Q` → its upper case; `internal.h`, beside
  `PCREC_PREFIX_PLACEHOLDER`). Rendering is a function of the text, so two
  texts equal before rendering are equal after it: a comparison that ACCEPTS
  is right. Two texts unequal before can be equal after (a hook spelled with
  the placeholder against one spelled with the literal default prefix `rx`),
  so the only possible error is a FALSE REFUSAL, which fails the compile
  loudly and never miscompiles. Today's `s`/`n` hook texts are the literals
  `subject` and `subject_length` on every R-17 site (`emit_dfa.c:6377`,
  `:7206`), which hold no placeholder, so no false refusal arises. The same argument
  covers the stem, which the kit never compares (it only writes it).
- **Every kit-declared identifier for the site is `<stem>__<role>`**: the
  helper `__find`, the struct tag and the variable `__c`, memchr_set's pointer
  `__q`.
- **pcrec reserves the namespace `<stem>__*`.** It declares no identifier
  there and passes no hook text containing one. That is the fact that makes
  capture impossible: a hook text (`s`, `n`, `lo`) can never name a kit local,
  and a kit local can never shadow a hook.
- **Why not handle-derived names** (the panel's suggestion). Handles are
  per-art sequence numbers. A later kit change that defines one more site
  earlier would renumber every following site's names and inflate an
  unrelated change's mover population. pcrec-given stems are stable.
- **G2's check.** A SHADOW hook set: hooks whose texts equal every role name
  and every common local (`q`, `c`, `m`, `base`, `top`, `i`, `w`), so a kit
  local that ignored the stem would capture one. Sabotage S837 plants that.
  `[r4 K1-11]` The shadow set includes a PLACEHOLDER stem (`\x01q_pf`), with
  the fixture rendering the placeholder before compiling, so a kit that
  escaped or inspected the stem fails there.
- `[r4 K1-11]` **The reservation is checked.** A C-check over pcrec's emitter
  sources fails on any format string or literal that produces an identifier
  beginning with a stem followed by `__` (pcrec writes `_pf__` nowhere today).

### 7.7 What the storage does NOT need

- static or file-scope storage (forbidden: reentrancy);
- heap;
- a pcrec statement to reset it;
- a pcrec read of it;
- architecture-specific types.

On the last point: the cache is `size_t` and `unsigned long long` at every
level, because an AVX2 helper returns its 64-bit mask from two 32-byte
compares. So SIMD-on adds no body bytes and the floor rule holds there by
construction (RQ-3's bracket stays in helper definitions).

## 8. The stateful forms and their correctness proof

### 8.1 The mask form (the "truth vector")

`W` is the block width. It is 64 for the 64-bit mask (one `unsigned long
long` of flags), or 8 for the one-word variant `mask8`. Both values are
DERIVED from the mask word's width or the SWAR word's width, not tuned (D149);
the follow-up times both. `M64(p)` is the exact membership mask of
`p[0 .. 64)`, bit `j` = `[p[j] in S]`. At SWAR it is eight normalized word
loads, EXACT terms ORed, each packed by
`((z >> 7) * 0x0102040810204080ull) >> 56` (lane `i`'s flag to bit `i`; no
two partial products collide, so no carry reaches bits 56-63). At SSE2 it is
four 16-byte compare/movemask; at AVX2 two 32-byte.

    size_t <stem>__find(struct <stem>__c *c, const unsigned char *s,
                        size_t lo, size_t hi)        /* precondition lo < hi */
    {
        size_t i = lo;
        if ((size_t)(lo - c->base) < (size_t)(c->top - c->base)) {
            unsigned long long m = c->m >> (lo - c->base);
            if (m) return lo + (size_t)__builtin_ctzll(m);
            i = c->top;                            /* nothing in [lo, top)  */
        }
        while (i + 64 <= hi) {                     /* full blocks           */
            unsigned long long m = M64(s + i);
            if (m) { c->base = i; c->top = i + 64; c->m = m;
                     return i + (size_t)__builtin_ctzll(m); }
            i += 64;
        }
        if (i >= hi) return hi;
        if (hi >= 64) {                            /* the overlapped block  */
            size_t b = hi - 64;
            unsigned long long m = M64(s + b);
            c->base = b; c->top = hi; c->m = m;
            m >>= i - b;
            return m ? i + (size_t)__builtin_ctzll(m) : hi;
        }
        unsigned long long m = MTAIL(s, i, hi);    /* hi < 64: words, bytes */
        c->base = i; c->top = hi; c->m = m;
        return m ? i + (size_t)__builtin_ctzll(m) : hi;
    }

`MTAIL(s, i, hi)` builds the exact mask of `[i, hi)` (fewer than 64 bytes)
from whole normalized words while `i + 8k + 8 <= hi`, then single bytes
through the lane predicate.

`[rev 2.2]` **The chosen W per width, and the form as `next_candidate`.**
- SWAR: **W = 8** (`mask8_swar`), measured best SIMD-off form (slot2 answer 7:
  444 of 574 rows won, 127 lost, worst row 1.87; the whole `reset=inf` 64K
  column, 0.86 at 300k; `call` 1.65 against `mask64_swar`'s 3.98; no L16
  cliff, 0.70). `M64` above reads `MW` = one normalized word through
  `load_vector`, its terms through `eq`/`cube`/`range` and `vor`, packed once
  by `lane_mask`; the overlapped block is `hi - 8`, and the tail below 8 bytes
  is the lane predicate per byte.
- SSE2: **W = 64** (`mask64_sse2`: 434 won, 132 lost, worst 2.21); AVX2:
  **W = 64** (`mask64_avx2`: 446 won, 118 lost, the fewest of any form, worst
  2.05). `MW` is four 16-byte or two 32-byte loads, each `lane_mask`ed and
  shifted into one 64-bit mask.
- The function is `<stem>__next_candidate(struct <stem>__c *c, size_t lo)`:
  the pseudocode above with `s = c->s`, `hi = c->n - end_back` (formed under
  §5's guard), 64 replaced by W, and `__builtin_ctzll` spelled `first_lane`.
  Nothing else changes, so §8.2's proof covers it.

The overlapped block READS BELOW `i`, down to `hi - 64 >= 0`. That is legal:
- the reads stay within `[0, n)`;
- the row serves an unstated `floor` only (§4.2);
- it caches exact membership for those bytes too, which a later backward `lo`
  can use.

### 8.2 The proof: stateful == stateless for every candidate sequence

**Definitions.**
- `B = s[0 .. n)`, immutable for the storage's lifetime (G-S1).
- `hi = n - end_back`, constant (G-S2).
- The STATELESS answer, for `lo < hi`, is `F(lo)` = the least `i` in
  `[lo, hi)` with `B[i] in S`, else `hi`. For `lo >= hi` the use is NOP
  (nothing written).

**The invariant `I`** on the cache `(base, top, m)`:
- `0 <= base <= top <= hi` and `top - base <= 64` (`[rev 2.2]` `<= W`, the
  width's block: 8 at SWAR, 64 at SSE2/AVX2; read every "64" in steps 1-3 as
  W, and the shift `i - b` as lying in `[0, W)`);
- for every `i` in `[base, top)`, bit `i - base` of `m` is `[B[i] in S]`;
- `m`'s bits at and above `top - base` are 0.

The initial `(0, 0, 0)` satisfies `I` vacuously.

**Step 1: the interval test.** Claim: `(lo - base) mod 2^w < top - base`
holds iff `base <= lo < top`, where `w` is `size_t`'s width.
- If `base <= lo`, the subtraction is exact, and the test is `lo < top`.
- If `lo < base`, the residue is `2^w - (base - lo) >= 2^w - base`. Since
  `top <= hi <= n < 2^w`, we have `2^w - base > top - base`, so the test fails.

**Step 2: a hit inside the cache.** If `base <= lo < top`:
- `m >> (lo - base)` has bit `j` = `[B[lo + j] in S]` for `lo + j < top`
  (by `I`), and 0 above.
- If it is nonzero, `lo + ctz` is the least member in `[lo, top)`, which is
  `F(lo)` (it lies below `top <= hi`).
- If it is zero, `[lo, top)` holds no member, so `F(lo)` = the scan's answer
  from `i = top`.

**Step 3: the scan from `i`.** The precondition, established by step 2 or by
`i = lo`, is that `[lo, i)` holds no member.
- **Full blocks.** Each block `[i, i + 64)` lies within `[i, hi)`. The first
  nonzero `M64` gives the least member at or after `i`, so it gives `F(lo)`.
  Writing `(i, i + 64, M64)` establishes `I`: exact over the block, and
  `top <= hi`.
- **The overlapped block** (`i < hi < i + 64`, `hi >= 64`). `b = hi - 64` lies
  in `[0, i]`, and `M64(s + b)` is exact over `[b, hi)`. Writing
  `(b, hi, M64)` establishes `I`. The shift `i - b` is in `[0, 64)`, so
  `m >> (i - b)` answers the least member in `[i, hi)`, else `hi`. That is
  `F(lo)` by the precondition.
- **The short tail** (`hi < 64`). `MTAIL` is exact over `[i, hi)`. Writing
  `(i, hi, MTAIL)` establishes `I`, and the answer is the same.

**Step 4: `I` is preserved.** Every write establishes `I`, and `I` depends
only on `B`, `S` and `hi`, which are invariant. An empty use writes nothing
(§5). So `I` holds before every use.

**Conclusion.** Every use returns `F(lo)`, for ANY sequence of `lo` values.
Each case the panel named is an instance:
- **The cursor moved backwards, or a candidate earlier than the saved
  block:** `lo < base` makes step 1 fail, so the scan runs from `lo` (the
  stateless form); or `lo` falls inside the cache, and step 2 is exact.
- **Reseed:** the DFA hat's re-seed (`pf_emit_moved_reseed`) does not move
  `lo`. A hybrid's prefilter re-seed runs in a different function with its
  own storage (§7.5). A jump is any `lo`.
- **Encoding round-up:** the VM hat's K49 advance moves `lo` by a
  character, and `F` is defined per `lo` whatever produced it. The start set
  holds character starts only (`vm_start_assert_starts`, sabotage S497), so
  the answer needs no round-up, today or here.
- **n = 0 and NOP:** §5. Nothing is read or written, and `I` is untouched.
- **Repeats:** a repeated `lo` takes step 2 again and returns the same
  answer.

**Reads.** Every byte read lies in a block within `[i, hi)`, in
`[hi - 64, hi)`, or in the tail `[i, hi)`. All are within `[0, hi)`, a subset
of `[0, n)`: no read at or past `n`, and none below 0. The guard-page check
(§12.4) holds the claim.

**What would break it**, each one a sabotage row of §12.5 (ids renumbered to
main's allocation, §12.5):
- a validity test without the lower bound (S830);
- a stale base (S831);
- a missing initializer (S832);
- a shift from the wrong origin (S833);
- a block READ past `hi` (S834). `[r4 K1-2]` Revision 2's S833, "the fill
  caches up to `n` at end_back 1", is an EQUIVALENT mutant: the one extra
  byte cached is `n - 1 = hi`, and a member there answers `hi`, which is
  the miss answer anyway. The non-equivalent breakage is an over-read: the
  overlapped block at end_back 0 taken at `hi - 63` reads `s[n]`. Its answers
  are unchanged, so no answer check sees it; the guard page, ASan and the
  trace rendering's `top <= hi` assertion do;
- two sites sharing one storage (S835);
- a LOWEST rendering in a stateful row: not exact, so `I` fails at the false
  lanes (S827/S829 families).

`[rev 2.3, r5 K3-2]` **Read the next paragraph with §4.3's revision:** the
values are bound once, at `mf_locals` (which refuses `s`/`n` texts other than
the define's), and every use, guard and helper alike, reads them from the
struct. "At `mf_use` (the guard's `n` text equals the define's)" is withdrawn:
the guard reads `<stem>__c.n`. So "the same values at every use" holds by
construction for the struct. G-S1's bytes half is still needed as before (`B`
immutable), and G-S1/G-S2's pointer and length halves now mean "the struct's
copy is still the caller's subject". The compiler (the const parameters,
§7.4), the textual C-check and the trace trap hold that.

`[rev 2.2]` **What `next_candidate` changes in the proof, and what it adds.**
- `B` and `hi` are now read from the struct (`c->s`, `c->n`) instead of from
  each use's arguments. The proof needs exactly that they are the same values
  at every use, which is G-S1/G-S2 again, now checked at `mf_locals` (the
  hook texts bound into the struct equal the define's) and at `mf_use` (the
  guard's `n` text equals the define's). The proof is otherwise unchanged.
- Two new ways to break it, each a row of §12.5: `mf_locals` binding `s`/`n`
  hook texts other than the define's (a stale or shadowed `n`, so `hi` is not
  the guard's), caught by the refusal; and a width whose W disagrees with its
  pack (a 64-bit block packed as 8 lanes), which breaks `I`'s exactness above
  bit 8. S834's over-read generalizes to the overlapped block taken at
  `hi - (W - 1)`.

### 8.3 The ring form (the "circle queue")

`[rev 2.2]` **NOT BUILT; a filed note behind `next_candidate`.** The
expected verdict below held, more strongly than predicted (slot2 answer 3):
- the ring loses to the mask in EVERY measured regime: ring/mask is 1.02-1.62
  at `reset=inf` (64K and 1M), 2.1-2.3 at `k16`, 6.6-7.6 at `k4`, and
  8.7-15 at `call` 300k;
- H3's one exception ("the ring may win at 1M, 20k-70k") is falsified:
  1.38-1.47 there;
- the cause, from perf: the ring executes about twice the mask's branches
  (11.3-13.7 against 5.2-7.1 per call) because the drain touches every member
  of a 256-byte fill, most never asked for; its mispredicts are not worse at
  70k/800k. So the loss is instruction count and wasted drain work, which
  grows with every state reset.

Frank's point that the queue's interface is arch-independent is kept by
making the CONTRACT queue-shaped (`next_candidate`), not the state (D155
addendum 4.1). The ring's real advantage, decoupling (any producer can fill
it, e.g. a multi-site or multi-span producer), has no measured case; it is
filed with a trigger (§17). The proof below stays valid for it.

The ring carries the same invariant as the mask form, but spelled as
positions. `pos[0 .. rt)` holds, ascending, EXACTLY the member offsets in
`[base, top)`. A fill computes the masks of up to `RING` bytes (4 blocks of 64
at `RING` 256) and drains each mask's bits into `pos`. `rh` is a HINT: the
first index whose position is at or above the last served `lo`.
- A use with `base <= lo < top` first restores the hint's precondition: if
  `rh > 0 && base + pos[rh - 1] >= lo`, it sets `rh = 0`, because the cursor
  moved back.
- It then advances `rh` past entries below `lo`, and answers
  `base + pos[rh]`, or scans from `top` when `rh == rt`.

The proof is §8.2's, with the mask's exact bits replaced by the exact
ascending list. A dropped hint reset is S842.

**Expected verdict** (UNMEASURED, to falsify): the ring LOSES to the mask
form, because a 64-bit mask IS a compressed ring with no drain loop. The
ring's distinct possible advantage is decoupling: one tight vector pass over
256 bytes and then cheap drains, with better ILP than refilling every 64. Its
twin answers that. If it does not win somewhere, it is not built (D77).

### 8.4 Stateless forms are unchanged in kind

`pf_terms` (the find-first term-OR) and `pf_memchr_set` answer `F(lo)`
directly. r17s's 1,874,741,290-call check covered their kernels, except at
`n = 0` with a NULL `s` and with `lo > n`, which C1-1 named. G2 adds those
(§12.1).

`[rev 2.2]` Neither is built (§4.1). The stateless kernel survives as the
G2 sequence check's second reference (stateful == stateless == byte loop,
§12.2), rendered in the test TU only.

## 9. The adaptive switch, and the fallback density gate

### 9.1 The adaptive switch (`pf_terms_adapt`)

`[rev 2.2]` **NOT BUILT (D77); the design below is a filed note.** Slot2's
answer 4, at the constants below (not swept):
- it beats the better of `table` and its fast form beyond the band on 9 / 4 /
  4 of 574 rows (`adapt_swar` / `adapt_avx2` / `adapt_mask`), best 0.95, and
  loses on 401 / 393 / 447;
- H4 is falsified: `adapt_swar` is 2.25 of `table` at 300k, not a tie. The
  mode branch itself mispredicts (0.63 per call against `table`'s 0.038), and
  the walk mode loses the pattern `table` had learned;
- it gives up sparse wins: `adapt_swar`/`swar` is 1.18 at 20k and 1.45 at 70k;
- under a state reset it only adds bookkeeping (1.05-1.08 of `swar`).

A fixed stateful form beats the switch in every regime where adaptivity could
matter. The one thing that could reopen it is a sweep of GAP/BLOCK0/CAP,
which was not run and which nothing in slot2 suggests would help; that is
its trigger (§17). D162's "decide without data" is met by the admission rule
of §9.2 instead of by run-time learning.

The two-mode machine runs in the same kit-owned struct (two more fields). It
is [OPT-HYB-RESEED]'s shape (`emit_vm.c` `retry_seed`): arm on a short gap,
step a block, double up to a cap, probe at the block's end.

    if (c->steps) {                          /* walk mode                 */
        c->steps--;
        while (lo < hi && !T[s[lo]]) lo++;   /* pcrec's table (rule 7)    */
        return lo;
    }
    a = FAST(c, s, lo, hi);                  /* the mask or stateless form */
    if (a - lo >= GAP)    c->block = 0;      /* a long skip: disarm        */
    else if (!c->block)   c->block = BLOCK0; /* first short skip: arm      */
    else { c->steps = c->block; if (c->block < CAP) c->block *= 2; }
    return a;

- **What it observes.** The SKIP DISTANCE `a - lo` at each use: the bytes
  the fast form moved over. That is exactly the quantity opt3 measured as 0
  on dense text (§15). A short skip means the fast form's setup bought
  nothing, so the next block of uses walks.
- **What the walk mode is.** Today's walk over pcrec's table, byte for byte,
  so a dense subject runs at today's speed after the first BLOCK0 uses. The
  row therefore reads `table_ref` (rule 7). `[r4 K1-1, K2-6]` The table is a
  parameter of the helper, named at each use (§4.3), and the define reports
  `reads_table`, so pcrec emits the table (§11.1).
- **The constants**, each `UNMEASURED DEFAULT:` in place:
  - `GAP` = 8 (one SWAR word: a hit inside the first word paid a whole
    word's test for at most 7 skipped bytes);
  - `BLOCK0` = 16;
  - `CAP` = 1024.

  The follow-up's adaptive twins carry them as `-D` overrides (§13.4).
- **Answer-safe** by construction: both modes compute `F(lo)`, and the
  counters are not part of `I`. In walk mode the mask cache is neither read
  nor written. That is safe by §8.2: `I` does not depend on which uses
  touched the cache.
- **Whether it is built** is the follow-up's verdict. It exists only if it
  beats the plain stateful form somewhere, or the plain stateful form still
  loses dense where adapt does not (D77). The adaptive twin over the
  STATELESS forms (`adapt_swar`, `adapt_avx2`) is measured beside the mask
  forms: Frank's "I like adaptive" names the switch, his second sentence the
  stateful fast form, and the grid decides which composition ships.

### 9.2 The admission rule: ADMIT when density is absent (`[rev 2.2]`, D162 addendum 1)

**REWRITTEN.** Revision 2.1's gate admitted only on POSITIVE evidence of
SPARSE density, and `D_ABSENT` declined. Slot2 and D162 addendum 1 reverse
that. Frank, "Yes agree", to the manager's lean: ADMIT by default (D162
ruling 2: "be ready to make decisions without data"); decline only on
positive evidence of density at or above 300k with a state-losing call
pattern. The revision 2.1 rule, its `T_SPARSE = 70000` and its S839 plant
are WITHDRAWN.

**The predicate.** `pf_terms_mask` DECLINES a site (the walk takes it) iff
BOTH inputs are present AND both say "lose":
- **(D) density:** the set's candidate rate, derived by the kit from the
  analysis object's byte-rate kind (the sum of the members' rates; D162: the
  kit derives per-site answers), has a LOWER bound at or above `T_DENSE`;
- **(P) a state-losing call pattern:** a fact that the site's state survives
  fewer than `B_EVEN` candidates. Either pcrec's structural host fact
  `activation = MF_ACT_PER_RETRY` (the hybrid's prefilter function, entered
  once per VM re-seed, §7.5; the r4 unlock), or a call-pattern / match-density
  kind of the analysis object (the reserved per-site slot, D162 ruling 1,
  "match density the likely first").

`[rev 2.3, r5 K3-4, K3-6]` **(D) and (P), restated.**
- **(P) is USES PER ACTIVATION below `B_EVEN`.** An activation is one
  execution of the storage's declaration (one call of the holding function);
  its uses are the site's `next_candidate` calls before the function returns.
  (P) holds iff the site's uses per activation are below `B_EVEN`, read from
  one of:
  - **the trace counter `mfk-upa`** (filed, §12.4a, §17): the trace rendering
    counts, per site stem, activations and a histogram of uses per activation
    in the buckets 0, 1, 2, 3 and 4 or more (the buckets are `B_EVEN`'s measured
    bracket, below, not a tuning). It prints one line per stem at exit;
  - **the bench's per-subject figure** (candidates per true match, or uses
    per activation; the corrigendum to I-148 asks for it);
  - **a call-pattern or match-density kind** of the analysis object, when one
    exists.

  The statistic is the MEDIAN activation's uses (PROPOSED; readable straight
  off the histogram). A mean would let a few long activations hide many
  one-use ones, and slot2's `k`-rows are fixed lifetimes, so they do not choose
  between the two.

  "Per retry" (`activation = MF_ACT_PER_RETRY`) is a PROXY only (§7.5): it
  marks a site where few uses per activation are possible, and does not
  satisfy (P) by itself. Revision 2.2's "either pcrec's structural host fact
  ... or a call-pattern kind" is withdrawn for its first half. The bench draft's
  "state-losing by construction" is withdrawn with it (the corrigendum).
- **(D) is CORPUS evidence, not subject evidence.** The byte-rate kind is the
  compile's analysis object, built from an exemplar or a shipped prior, never
  from the subject a call sees. A decline on (D) is therefore a compile-time
  bet on the expected subjects. That is why it needs (P) as well, and why the
  bench relay, on real subjects, is the gate.
- **A point-estimate rate is a DEGENERATE INTERVAL.** Where a kind gives a rate
  `r` with no interval, it is read as `[r, r]`, so its lower bound is `r`. This
  is a stated reading, not a presumed value: a kind with no rate at all is
  ABSENT and admits (the first row of the table below).

Every other case ADMITS. **The selection is TOTAL without data:**

| density (D) | call pattern (P) | admitted? |
|---|---|---|
| absent (no object, or no byte-rate kind) | any | **yes** |
| present, lower bound below `T_DENSE` | any | yes |
| present, the interval straddles `T_DENSE` | any | yes (no positive evidence) |
| present, lower bound at or above `T_DENSE` | absent, or state-carrying | yes |
| present, lower bound at or above `T_DENSE` | state-losing | **no** (the walk) |

**The thresholds (D149 labels, each with its measured source).**
- `T_DENSE = 300000` ppm: `MEASURED-UNOFFICIAL (slot2, kit tier, dev box Zen 4,
  gcc 15.2.0 -O2, 64 KiB, i.i.d. placement, reset=call, 14 real cells)`. The
  `reset=call` row, form/`table` median/worst (computed for this revision from
  `out/slot2/times.tsv`; `call` was timed at four densities only):

  | form | 20k | 70k | 300k | 800k |
  |---|---|---|---|---|
  | `mask8_swar` | 0.65/0.84 | 0.97/1.17 | 1.65/1.83 | 0.94/1.07 |
  | `mask64_sse2` | 0.39/0.43 | 0.99/1.12 | 1.88/2.21 | 1.11/1.22 |
  | `mask64_avx2` | 0.35/0.40 | 0.93/1.04 | 1.81/2.05 | 1.03/1.13 |

  So the loss edge lies in (70k, 300k], not located finer (the grid has no
  point between). At 70k the medians tie and the worst cells lose by up to
  1.17, which the rule accepts as regret. Above 300k the loss shrinks again
  (800k ≤ 1.22 worst), so declining at every density at or above 300k gives
  up at most a tie there; the ruled predicate is kept as ruled ("≥ ~300k"),
  and a finer band is the bench's to read.
- `B_EVEN = 3` candidates per state lifetime: `MEASURED-UNOFFICIAL (slot2, same
  tier, 300k only)`. At 300k, stateful/stateless is `mask8_swar`/`swar` 0.69
  (`inf`), 0.82 (`k16`), 0.80 (`k4`), 1.33 (`call`): break-even near 2-3
  candidates. For `mask64_avx2`/`avx2` it is 0.62, 0.72, 0.69, 1.29. Lifetimes
  other than 1/4/16/unbounded were not timed.
- `[rev 2.3, r5 K3-6]` **The two labels above were too strong. Corrected:**
  - `T_DENSE = 300000` ppm: **`MEASURED-BRACKET (70000, 300000]`** (slot2, same
    tier and regime as above). The loss edge lies somewhere in that interval
    (the grid has no point between 70k and 300k at `reset=call`), and 300000 is
    the bracket's upper end, which is the value Frank ruled ("≥ ~300k"). It is
    not a measured point.
  - `B_EVEN = 3` uses per activation: **`UNMEASURED DEFAULT: 3 (an
    interpolation inside the measured bracket (1, 4))`**. slot2 timed
    lifetimes 1, 4, 16 and unbounded only: the stateful form loses at 1 (1.33
    / 1.29) and wins at 4 (0.80 / 0.69). So the break-even is somewhere in
    (1, 4), and 3 is a guess inside it.
  - Both stay byte-neutral at R17-b (no input reaches the decline arm), so
    neither needs a measurement before R17-b. The decline arm's landing (§17)
    owes a finer reading of whichever one its first input sits near.
- **Both come from the pessimistic end.** At 64 KiB `table` costs 0.65 ns/B
  against 1.91 at 1 MiB (0.038 branch misses per call at 300k): the predictor
  has learned the repeated stream (an inference; no 1 MiB perf pass was
  taken). That makes the 64K dense rows the hardest case for every form. The
  bench relay on real subjects (§11.2a) is what decides whether a real cell
  loses beyond the floor.

**Why ADMIT is the right no-data decision.** The measured regret of the
chosen forms is bounded by about 2x (worst rows 1.87 / 2.21 / 2.05 for
`mask8_swar` / `mask64_sse2` / `mask64_avx2`) and confined to three corners:
(a) hit-per-candidate with the state lost at ~300k (`call`, `k4`), (b) dense
percall (300k-800k, spans 16/64), (c) clustered runs of mean 8 or more at
300k. Everywhere else they win, by up to 2-17x (`mask8_swar` 0.54-0.86 of
`table` across the `reset=inf` 64K column; the SIMD masks 0.05-0.22 at 0-20k). The predicate covers (a) and, through a percall
call-pattern fact, (b). (c) is a subject property no site states; it stays
measured regret, and the bench relay reads it on real text.

**What reaches the decline arm today: nothing.** pcrec files no analysis
object yet (D162's consequences: "No request yet: main files one when a
consumer needs the object"). The [FINDINGS] bundle has byte rates but no
call-pattern or match-density kind, and pcrec states no `activation` fact.
So:
- **R17-b reads no density fact.** Every site admits; W6 is not appended
  (§2.2); no byte depends on data. The no-data path is the stated decision,
  not a fallback.
- **The decline arm is a later FORM event**, coded when the object first
  carries a byte-rate kind AND a call-pattern kind (or pcrec states
  `activation`): W6 appended, the row's contract gains the class, the movers
  are the declined sites only, with G1, the abi ritual and a bench reading.
  Coding it now would ship an arm no input can reach (S839 would read
  UNREACHED), which D77 refuses.
  `[rev 2.3, r5 K3-4]` "Or pcrec states `activation`" is withdrawn: the
  structural fact is a proxy and cannot complete (P). The arm's (P) input is a
  uses-per-activation source (the analysis object's call-pattern or
  match-density kind; the `mfk-upa` trace counter feeds the kit's own
  reading, not a compile).
- `[r4 K2-5]` and D162 ruling 1: the object is the ONE density carrier, so
  the gate adds no fourth carrier. Folding `rank_ppm` stays main's to rule
  (chunk 2).
- The gate is still P5's "is the search cheaper than the consumer meeting
  every byte" with the consumer price unknown. Once W9 exists, it may read
  W9 in place of `T_DENSE`: an R-18 form event.

**The state-lost dense residual is [FINDALL-NEXT]'s (main's chunk 5), not
R-17's** (D162 addendum 1). With today's API a true match ends the call, so a
find-all whose candidates are mostly true matches runs in the `call`/`k4`
regime, where `mask8_swar` loses 1.65 at 300k. Cross-call state in the
versioned caller struct turns those rows into `reset=inf` rows (`mask8_swar`
0.86, `mask64_avx2` 0.88 at 300k). The measured break-even it must reach is
2-3 candidates per state lifetime for `mask8_swar`. R-17 does not try to fix
that corner, and the decline arm above only bounds it.

N1 (the analysis object) stays main's promise for other consumers
([START-DENSE], §17); it is not R-17's build trigger.

## 10. The define-time round-trip self-check (C1-3)

At `mf_define` of every term row, after `mf_set_terms`:
1. EXPAND the chosen cover: OR each term's member set, then negate for the
   complement form.
2. Compare the result with `term.set`, bit for bit.
3. Verify each term's purity: its members are a subset of the target.
4. Verify the term count is at most K.

**Any difference is a LOUD REFUSAL**: `kit_fail(art, "pf-terms: the term list
for <set> expands to <set'>: internal error (memfn/src/terms.c)")`. The error
is sticky, so pcrec raises it through `pcrec_ctx_fail`'s internal-error tier
and the compile fails.

**It is never a decline.** A decline would turn a deriver bug into a silent
fallback to the walk, and every check reading answers would stay green. This is
learnings §3's "fails in the silent direction". The check costs 256 bit-tests
per site at compile time.

**Its own control.**
- S826 plants a purity bug with the check ON, and expects the refusal on the
  witnesses.
- S827 plants the same bug with the check OFF, and expects G2's independent
  round-trip test (an expansion written by the blinded author, not the kit's
  expander) to catch it.

The two rows prove the check can fire and that it is not the only line.

## 11. The one routing event

Q-R17-2 = (A): "one routing event, where the code fits neatly in a function".
The timing is per main: after the follow-up measurement (§13) AND main's
chunk-2 D161 note ratifying §2.

`[rev 2.2]` **The shape, settled:**

| step | what lands | bytes | gate |
|---|---|---|---|
| R17-a | the seam: window fields W0-W5, `mf_locals`, `mf_defined`, the define points, the refusals (§11.1). No row uses a primitive, so the shared helper block is ABSENT | none (zero-mover) | the identity gates, mech's [SABANCHOR] count, G2 quick (§11.1's control) |
| R17-b | `pf_terms_mask` at SWAR (`mask8_swar` behind `next_candidate`), `terms.c` with K = 4, the shared helper block's first appearance, the abi bump, the spec hunks | the SIMD-off movers (§11.2) | G1 at both layers, the R17-b checks, **and the bench relay on real subjects before merge** (§11.2a) |
| after | the SIMD arms `mask64_sse2` / `mask64_avx2` as per-width definitions behind the same body | zero SIMD-off movers | per-box pcrec-bench verdicts (D144 addendum 4, §11.4) |

The follow-up has run (§13), so the first precondition is met; main's chunk-2
note ratifying §2 is still owed. The bench relay is a third precondition, of
R17-b only.

### 11.1 R17-a: the zero-mover seam (one commit, `MF_SITE_ABI` 10 → 11)

**The order on every route** (`[r4 K1-6]`): DEFINE at a file-scope point
above the function → `mf_locals` at the declaration point → pcrec's table,
iff the define says the form reads it → `mf_use` at each use. No handle is
used before its define, and no use precedes its storage.

**pcrec side:**
1. **The facts.** `find_site` (`emit_dfa.c:6309`) states W0 = 1, W1 = `d_min`
   (0, or -1 on MLINE) and W2 = 0 on every FIND it builds. On the set sites
   (the DFA prefilter, the DFA hat, the VM hat) it also states W4
   (`decl_point` = 1) and W5 (`fn_ref`, the stem of §7.6); on the byte sites
   and MLINE, W4 = 0 and no `fn_ref`. Every other FIND builder states W0-W2
   the same way. `[r4 K2-4, K2-5]`
2. **Define-then-use** (`[r4 K2-1]`; corrects revision 2's item 3).
   - **DFA:** the three set rows (`byte-class`, `byte-class-bounded`,
     `first-class-bounded`) gain a `u.pf.emit_block`, `pf_block_find`, on
     the offset-skip FUNC's precedent (`pf_block_ofs` / `ofs_site_define`,
     `emit_dfa.c:6757-6781`). It is called where every `emit_block` is, at
     file scope above the body (`emit_dfa.c:11387` in `emit_unanchored`,
     `:11571` in `emit_rev_end`'s relocate), and the VM hybrid's inlined
     prefilter gets it by the same construction ("a block emitted here is a
     block the hybrid gets"). It DEFINES the PF site with that file stream
     as `file_scope`, so any helper the form needs is written there, ahead
     of the function; it keeps the handle on the `DfaForm`, as `ofs_site` is
     kept. Revision 2 named `cand_emit_table`'s buffer as the file-scope
     sink, but that table is FUNCTION-LOCAL: `emit_u8_table` writes it
     "INSIDE the search function" (`emit_dfa.c:3446`), from
     `emit_machine_tables` (`:10877`). The table is emitted there iff the
     define reports `reads_table` (item 3). `mf_locals` is called in
     `unanch_scan` (§7.1), and `pf_emit_find` calls `mf_use` on the handle
     where `pcrec_emit_find` calls `mf_emit` with `file_scope = NULL` today.
   - **VM hat:** DEFINED in `vm_emit_search_body` beside
     `pcrec_emit_req_run_blocks` (`emit_vm.c:13130`, "at file scope above
     the one search loop"), above the `<searchfn>_run` head, when the VM
     route selects `first-class` (`vm_start_row`). At the entry seek
     (`pf_vm_emit_first_class`, `entry`): `mf_locals`, then `start_set` iff
     `reads_table`, then `mf_use`; at the retry, `mf_use` with the same
     handle (C3-7). Revision 2 had the VM helper "recorded pending and
     written by the existing `pcrec_memfn_flush_helpers` in the prologue".
     That cannot work: `mf_flush_helpers` writes only the word-load helpers
     `<p>_w<W>` (`memfn/src/runcmp.c:466-490`), and the prologue runs
     (`emit_vm.c:14000`) BEFORE `vm_emit_search_body` writes `_run`
     (`:14009`), so a helper recorded at the entry would miss it.
   - **No flush change** (`[r4 K2-1]`, stated honestly). Both routes define
     at a point above the function and the kit writes the helper there,
     as a FUNC definition "declares its own ahead of itself" (memfn.h).
     `mf_flush_helpers` stays word-loads-only.
3. **What the define reports** (`[r4 K2-6]`; replaces `mf_plan`, which is
   DROPPED). After `mf_define`, pcrec reads one record:

       /* mf_result gains: */  uint8_t reads_table; uint32_t includes;
       int mf_defined(const mf_art *, uint32_t handle, mf_result *out);

   - `reads_table`: the chosen form reads the term's table (rule 7). pcrec
     emits `can_begin_match` / `start_bytes` / `start_set` iff it is 1
     (C3-3). The define precedes the table on both routes (above), so this
     is a report, not a prediction, and no selection runs twice. This takes
     the r4 unlock "pre-prologue facts via `mf_result`" for this one fact.
   - `includes`: the `MF_INC_*` bits the form's text needs. **It is 0 for
     every R-17 row**: they are header-free (`__builtin_memcpy`,
     `__builtin_memchr`, `__builtin_ctzll`; §4.3, §6). That matters because
     on BOTH routes the prologue, which writes `#include <string.h>`,
     precedes the define (`emit_dfa.c:13459` before `pcrec_emit_dfa_engine`;
     `emit_vm.c:14000` before `:14009`), so a header a row needed could not
     be added at define without a back-patch. The r4 disposition's
     "back-patchable include slot" is therefore NOT built (D77) and is filed
     with a trigger (§17); the existing control already catches a row that
     breaks the rule: `pcrec_memfn_art_end` fails a compile whose kit text
     needs `<string.h>` the prologue did not include (`memfn_sites.c`). The
     r4 note that "the VM needs no prediction" holds for `reads_table` only;
     for includes it holds because the rows need none.
   - At R17-a every existing row answers as today (the walk reads its
     table; memchr's include is the prologue's existing prediction,
     unchanged), so no byte moves.
4. **N4's door assertion** (trace/test builds only, under the existing
   `PCREC_RANK_PROBE` idiom or a sibling define): at `find_site`, `set` equals
   the bytes of the table pcrec will name (C1-13).

**Kit side:**
- `memfn.h` gains W0, W1, W2 (with `MF_MOVE_UNBOUNDED`, `MF_OVER_UNBOUNDED`),
  W4 (`decl_point`), `mf_locals`, `mf_defined` and `mf_result`'s two
  fields, the FIND result meaning (W3) and the STMT `fn_ref` reading (W5).
- `fields.def` gains the fields' classes; `fn_ref`'s doc string gains the
  STMT reading (K2-12). Every existing row serves W0 `1`, W1 `== d_min`, W2
  `ZERO`, W4 `MF_ANY`, W5 `MF_ANY`.
- The refusals: W0 0 on a FIND site, W0 1 on a non-FIND or reverse site,
  `back < 0` (§2.2); `mf_use` before `mf_locals`; storage placed twice;
  never placed; placed and never read; a use whose `s`/`n` text differs from
  the define's (§7.1, §7.4).
- `mf_flush_helpers`: unchanged.

**The control:**
- byte-identical artifacts, read through the four identity gates over the
  corpus and both engines, plus `test-codegen`;
- the `test-memfn-*` suites;
- G2 quick;
- `[r4 K2-7]` **mech**: R17-a edits source text that sabotage anchors quote
  (`find_site`, `pf_vm_emit_first_class`, `pcrec_emit_vm_start_seek`,
  `unanch_scan`, `vm_emit_search_body`, `emit_machine_tables`, the PF row
  table). So the commit carries the [SABANCHOR] exact-count gate (every
  row's anchor still matches exactly once) and a DERIVED re-aim list: an
  edit-set file of the changed hunks, joined against every row's
  `SAB_FILE`/anchor (`start_table.md`'s method), never a hand list. S478
  (the [vm-table] detector's row; its anchor is the set-building line of
  `pf_vm_emit_first_class`, `emit_dfa.c:7209`) is named as the first expected
  member; each re-aim has its intent re-verified (BOILERPLATE).

`[rev 2.2]` **Additions to R17-a:**
- **The shared helper block is NOT emitted.** No R17-a row uses a primitive,
  and the block is emitted only when some site does (§3.4a), so the artifacts
  stay byte-identical. The kit-side block renderer, its guard and its key may
  land here as unused code (no artifact calls it), or with R17-b; either way
  the identity gates are the control.
  `[rev 2.3, r5 K3-10]` **Decided: the renderer lands with R17-b**, not here.
  At R17-a it would be kit code no artifact and no row calls (D77), and its
  only test would be a fixture of its own output. **This is a reconciliation
  with main's note on D155 addendum 4**, which says the shared block "lands in
  R17-a (the no-mover seam)". Read literally that is either dead code at R17-a
  or a mover in a zero-mover commit. Revision 2.2 already made the block's
  first APPEARANCE R17-b's; revision 2.3 makes its renderer's landing R17-b's
  too. Main's note is in decisions.md, which the kit does not edit; the kit
  asks main to annotate it (OWED, `r17r_report.md`).
- **`mf_locals` gains the hook comparison:** it refuses `s`/`n` hook texts
  that differ from the define's, since the stateful row binds them into its
  struct (§4.3, §8.2). At R17-a no row keeps storage, so `mf_locals` writes
  nothing on every site and the refusal is reached only by G2 fixtures.
  `[rev 2.3, r5 K3-9]` This is the ONLY `s`/`n` comparison. The refusal list
  above ("a use whose `s`/`n` text differs from the define's") moves from
  `mf_use` to `mf_locals`: `mf_use` pastes neither (§4.3).
- **W6 is not appended** (§2.2, §9.2).

This is R4e′.0's pattern: a zero-mover seam first, so the byte move that
follows is the only thing that moves.

### 11.2 R17-b: the one SIMD-off byte move (one commit, a pcrec abi event)

- **Kit:**
  - `terms.c` (`mf_set_terms`, the renderer, the round-trip check);
  - the surviving rows of §4 in `pffind.c`, each with its `options.def` row
    (`MF_L_SCALAR`, `MF_B_SCAN`, `MF_OPT_DENY`);
  - `pffind.c`'s header rewritten honestly (C3-10, F-2).
- **pcrec:**
  - `PCREC_ARTIFACT_ABI` bumped, with every reader found by grep (D76/D94;
    coding_guide §3.1);
  - the identity-gate re-pins;
  - the spec hunks (§11.3);
  - `pf_vm_emit_first_class`'s Q-R5 comment rewritten (F-2): "the
    `|S| = 1 -> memchr` cut-over is an unmeasured default" is no longer
    pcrec's to state;
  - `pcrec_emit_vm_start_seek`'s `PF_SCAN_SET` assertion KEPT. It asserts
    pcrec's own row (a table description), which is still true; the kit's
    form is not pcrec's assertion.
- **What moves:** every PF / DFA-hat / VM-hat table site whose set has a
  cover within K (§3), where the chosen row serves (and, if §9.2 is in force,
  the density is `D_SPARSE`). The walk's text becomes `<stem>__find`'s
  helper, one use statement and, for stateful rows, one local. A set with no
  cover does not move.
- **The population** is counted by a pcrec-side artifact diff (the
  `census.py` reader over emitted C, walk → kit form), never by the kit's
  `moved` (§16.2).
- **G1's alpha at both layers** (D147, D144 item 4):
  - **SIMD-off:** default against `--memfn=no-pf-terms,no-pf-terms-mask,...`
    (every surviving row's deny: today's walk), timed by pcrec's own regime;
  - **SIMD-on:** `-fmemfn-simd` against `-fmemfn-simd` plus the same denies.
    Until SIMD arms exist the two layers' artifacts are identical at these
    sites, and the reading says so instead of omitting the column.
- **Stamps.**
  - `<PREFIX>_MEMFN_LIBC` gains `memchr` exactly where `pf_memchr_set`
    renders (Q53's existing spelling).
  - `<PREFIX>_MEMFN_FORMS` stays `none` (no SIMD form).
  - `RX_DFA_PREFILTER` and `RX_VM_START_SCAN` keep their VALUES (§11.3).
  - No new stamp (D77; [STAMP-REVIEW] owns whether stamps survive).
  - `RUN_WORDS` is untouched.
- **Checks that land with the movers** (`[r4]`): the test READERS of the walk
  text, each re-aimed with its before/after population and floor (§12.6,
  K2-8); `-Wjump-misses-init` over the movers (§7.2, K1-7); the ring witness
  at `-O2` and `-O3` (§4.3, K1-8); the s/n C-check (§7.4, K1-4); the dynamic
  cache-path reach (§12.5, K1-9); the trace rendering (§12.4a, K1-4).

`[rev 2.2]` **R17-b, as settled** (read over the list above where they
differ):
- **The rows:** `pf_terms_mask` only, rendered at SWAR as `mask8_swar` behind
  `<stem>__next_candidate` (§4.1, §4.3). Its `options.def` row:
  `no-pf-terms-mask`, `MF_L_SCALAR`, `MF_B_SCAN`, `MF_OPT_DENY`. No adapt,
  ring, stateless or memchr_set row lands.
- **What moves:** every PF / DFA-hat / VM-hat table site whose set has a
  cover within K = 4 (§3.3). There is no density condition (§9.2: every site
  admits). Each mover's text becomes the struct declaration, the guarded
  `next_candidate` use and the per-site helper; the shared helper block
  appears once per artifact that has a mover (§3.4a). A set with no cover
  within 4 terms does not move.
- **The abi event covers the block.** The block's first appearance is part
  of R17-b's one `PCREC_ARTIFACT_ABI` bump; its readers are found by the same
  grep (D76/D94). Its helper-set version starts at 1. `[rev 2.3, r5 K3-8]`
  No version: the sub-block guards carry none (§3.4b). At R17-b only the W8
  sub-block exists.
- `[rev 2.3]` **Also in R17-b's commit:**
  - **the const subject inputs** (K3-3, §7.4): `const unsigned char *const
    subject` and `size_t const subject_length` in the definitions of the bodies
    that hold a stateful site, in the same abi event, on the same movers;
  - **the body guard on the bound `n`** (K3-2, §4.3, §5);
  - **the trace rendering's `c.n == n && c.s == s` trap** (K3-2, §12.4a);
  - **the reserved-prefix refusal N6** (K3-7, §14), as a same-commit pcrec edit
    with its `cli.md` hunk, IF main agrees; otherwise main files it as a
    separate pcrec request that must land no later than R17-b, because the
    stem's names first exist in R17-b's artifacts. It moves no artifact byte
    (it refuses inputs that compiled before), so it adds nothing to the abi
    event; it is caller-observable, so it carries its spec hunk (D80);
  - **the block renderer itself** (K3-10, §11.1).
- **G1's deny arm** is `--memfn=no-pf-terms-mask` (today's walk), at both
  layers.
- **The bench relay gates the merge** (§11.2a). The kit delivers R17-b to
  main as a branch with its alpha numbers; main runs the relay; a real cell
  losing beyond the regression floor returns the branch to the kit before it
  merges.

### 11.2a The bench relay that gates R17-b (`[rev 2.2]`, D162 addendum 1)

Frank's condition on admitting without data: "the bench relay on real
subjects is the gate before the routing event lands: a real cell losing
beyond the regression floor returns to the kit before merge" (D162
addendum 1, D144 addendum 4: the official verdict comes from the targeted
hardware).

**The draft is `setfind_bench_request.md`** (this directory), written to be
relayed as it stands: main carries it to pcrec-bench's inbox (D78) and
schedules the box; the kit never writes to pcrec-bench. It names:
- **the cells:** the R-17 named cells (`lc`, `dig`, `bkn`, `bpr` and the
  rest of the 14 slot2 cells where the bench has a matching pattern), the
  bench's dense controls, and every bench pattern whose artifact moves at
  R17-b by the mover census (§11.2);
- **the arms:** today's table walk (`--memfn=no-pf-terms-mask`) against the
  recommended forms at both layers: SIMD-off (`mask8_swar`) and, once the
  arms exist, SIMD-on (`-fmemfn-simd`: `mask64_sse2`, `mask64_avx2`);
- **the regimes:** find-all and per-call on the bench's own subjects, each
  subject's measured candidate density and run profile reported beside its
  cell;
- **what "loses beyond the regression floor" means numerically** (the draft's
  §4; PROPOSED for main and the bench to confirm). `[rev 2.3, r5 K3-5]`
  Revised, and sent to the bench as a corrigendum to I-148
  (`setfind_bench_corrigendum_I148.md`): a LOSS must reproduce on an immediate
  re-run; F is the bench's standing per-cell spread where it has one, else the
  largest spread of at least three A/A pairs; each A/A pair is
  layout-perturbed (the same program built with a different code layout); the
  absolute criterion applies to every cell; the kit's synthetic 0.05 floor is
  withdrawn. The reason: with about 60 cell × regime × box tests and a
  no-loss-anywhere gate, one same-binary A/A draw as F would reject on noise
  alone, and a same-binary pair cannot see layout effects (K24 measured 1.33x
  from placement alone);
- **the questions for the bench.**

**Why real subjects matter here (the 64K caveat).** At 64 KiB the kit's
harness rescans one subject, and `table` ran at 0.65 ns/B there against
1.91 ns/B at 1 MiB, consistent with the branch predictor having learned the
stream. So the kit's dense verdicts sit at the pessimistic end for the forms,
and its 1 MiB rows at the optimistic end. Which end a real subject is nearer,
with a consumer's work between calls, is exactly what the kit cannot measure
and the bench can.

**What a failing cell does.** It returns R17-b to the kit with the cell, its
regime and its numbers. The kit's options, in order: re-read the cell's
regime against §9.2's corners (a state-lost dense cell is [FINDALL-NEXT]'s
residual, and main rules whether it blocks); narrow the admission by a
stated, measured predicate; or hold R17-b. Each option is a kit decision
recorded with the bench numbers, never a silent retune.

### 11.3 The spec hunks (D80), method-blind

Grep for every reader before the commit (coding_guide §3.6):
- `docs/spec/match_api.md`, `RX_DFA_PREFILTER`'s value-set table (around line
  1658):
  - `"byte-class"` becomes "several bytes at offset 0: the scan to the next
    such byte is the search kit's FIND over the set (its form is the kit's;
    `<prefix>_can_begin_match` is emitted where that form reads it)";
  - `"byte-class-bounded"` and `"first-class-bounded"` change the same way.

  VALUES are unchanged, so the bench adapter's closed enum is unchanged (no
  inbox note needed for the values; the method sentence is caller-observable,
  so the hunk is required).
- `docs/spec/tuning.md` §2.42¶2: "The seek is a 256-entry table walk at any
  size of `S`" becomes "The seek is the search kit's FIND over `S`". ¶4's
  "a `<prefix>_start_bytes` table" becomes conditional.
- `docs/spec/registry.md` §6¶8b: `memfn` section floor 6 → 6 + (the rows
  R17-b lands). `[rev 2.2]` One row (`no-pf-terms-mask`), so 6 → 7; the SIMD
  arms' two denies raise it again when they land.
- `[rev 2.2]` The shared helper block is emitted scaffolding a caller can
  see in the artifact (its guard and names). If `match_api.md` documents the
  shared ABI block's guard (§1¶7, K80), the kit block's guard, its key and its
  reserved stem get a sentence beside it; found by grep at R17-b.
- Any spec sentence promising that a `<prefix>_can_begin_match` /
  `start_bytes` / `start_set` table EXISTS in an artifact (a caller could read
  it). Found by grep at R17-b.
- `[rev 2.3, r5 K3-1, K3-7]` Two more:
  - **the sub-block guards** replace "the kit block's guard, its key": a
    sentence beside match_api.md §1¶7 says that an artifact may carry
    `PCREC_MFK_<W>_H` guards, one per width it uses, that their identifiers
    carry the reserved stem, and that a mixed-abi TU is refused by §1¶7's own
    guard (the sub-blocks carry no number);
  - **N6, the reserved prefix** (if it rides R17-b): `docs/spec/cli.md` §1.6¶1
    and the sentence in `match_api.md` that documents `pcrec_options.prefix`
    and quotes the "invalid symbol prefix" diagnostic (§8.0¶4), found by grep.
    The draft hunk is in §14 (N6).

### 11.4 After: SIMD arms at zero SIMD-off movers

- A SIMD arm of `pf_terms` or `pf_terms_mask` is a guarded per-level variant
  of `M64`/the find helper (`<stem>__find__w16`, `__w32`), with a selector
  whose whole body is the `#if` chain (D155 addendum 1's guideline). The
  alternative, an `#if` inside one helper definition, is allowed by
  addendum 3.
- The SIMD-off artifact is unchanged: it already calls `<stem>__find`, and
  its SIMD-off definition is the SWAR one. C18 checks the floor rule.
- Each arm has its own deny (`pf-terms-w16`, `pf-terms-w32`, `MF_L_SIMD`). It
  is accepted against the CURRENT best scalar row, not the walk (D147). The
  official verdict is pcrec-bench on each targeted box (D144 addendum 4).
- This answers C3-1: the SIMD-off bytes move ONCE, at R17-b.

`[rev 2.2]` **The SIMD arms, as settled.**
- They are per-width definitions of `<stem>__next_candidate`: W = 64 over the
  shared block's 16-byte (`mask64_sse2`) and 32-byte (`mask64_avx2`)
  primitives, chosen at file scope by the `#if` chain (D155 addendum 1's
  selector shape), with the SWAR `mask8_swar` definition as the floor arm.
  The body text is identical at every layer, which is the floor rule in its
  strongest form: the SIMD-on rendering adds guarded DEFINITIONS only.
- The primitives they need are already in the shared block (its bytes do not
  depend on the layer, §3.4a), so the arms move no block byte. If the arms
  need a primitive the block lacks, the helper-set version bumps, which is an
  abi event.
  `[rev 2.3, r5 K3-1]` **Superseded.** The arms bring their own sub-blocks,
  V16 and V32, each emitted only in SIMD-on artifacts with a mover (§3.4b). A
  SIMD-off artifact holds the W8 sub-block only, which the arms do not touch,
  so the SIMD-off mover count of an arm's landing is ZERO by construction, not
  by an argument about unused text. The arms' landing is an abi event for the
  SIMD-on artifacts they move. There is no helper-set version (K3-8).
- **D147's check is open at 64K dense.** `mask64_avx2` loses to the best
  SIMD-off form (`mask8_swar` or a mask64 SWAR form) on 51 `reset=inf` rows,
  all at 64K and at or above 300k (worst 1.28, `bpr` 600k); `mask64_sse2` on
  70 at 64K and 6 at 1M. At 1M and below 300k they beat it by 2-6x. Whether
  the arms pass D147 is therefore decided by the per-box bench verdict, on
  real subjects, not by the kit's 64K rows.
- **AVX-512** is a later width row behind the same interface (D155 addendum
  4.1), UNFILED until requested; its verdict is on the targeted hardware
  (this box runs it; ubuntubudu does not). §17.

## 12. Checks

Before designing: learnings §3. Each check names what it is checked AGAINST,
who chose its inputs, and its population.

### 12.1 G2: the generated set space (D27-blinded family, authored later)

The author is a blinded lane in a D27 cell. It is denied `memfn/src/` and
`src/`, and works from this note's §3, §4, §5, §8 and memfn.h.

**The sets (T1)**, each through `mf_set_terms` and the rendered row:
- all 256 singletons;
- all 32,640 pairs;
- all 6,561 cubes;
- all 32,896 ranges (incl. the 0x80-crossing ranges, C1-10);
- all modular arcs;
- near-cubes (each cube with one member added or removed);
- unions of 2-8 random terms (100k, a fixed seed);
- sets with more than K terms (they must DECLINE);
- the complement of every set above;
- |S| = 0 and |S| = 256 (they must decline).

**The oracle shares no source with the kit:**
- (a) the blinded author's own EXPANSION of the returned term list, compared
  with the set (round trip);
- (b) the author's own brute-force minimal cover, restricted to covers of at
  most 3 terms (cheap), of `S` and of `¬S`, compared on objective 1 (term
  count) only. `[r4 K1-10]` Its term space is the author's OWN: every one of
  the 6,561 cubes and 32,768 arcs (width at most 128) that lies inside the
  target, filtered to those maximal by inclusion. That re-derives §3.2's
  candidate rule from the definitions instead of sharing it, so a candidate
  rule that lost a term (revision 2's end-arcs-only rule) shows as a count
  difference. Objectives 2-4 are the kit's choice and are pinned by T2
  instead.

**T2, a golden pin:** the term lists of every distinct corpus and bench PF
set, as `tests/memfn/pins/setfind_terms.tsv`. It moves only when the deriver
changes, and a move is a byte event (§16.3).

**T3, the BUDGET tripwire:** the maximum nodes used over T1, the corpus and
the bench must stay at most BUDGET/4. The count is printed.

**T4:** the `pcrec_cube_of` cross-check (§3.6).

`[r17d]` **T2 and T4 are BUILT** (lane r17d, 2026-10-12;
`tests/memfn/CLAUDE.md`, run_setfind.sh sections 7-8). T2's population is
T3's 558 corpus and bench FIND sets plus a seeded sample (2,158 sets); the
checker re-expands each pinned and each live cover by its own arithmetic and
holds live == pinned. T4 runs over the pin's sets, the 41 corpus byte classes
and every cube. T1 (the blinded family) and T5 (§12.3) are NOT built; the rows
that name them (§12.5) are held by T2's independent expansion, U1 and G2's
sequences instead, as r17d's report states row by row.

### 12.2 G2: generated CANDIDATE SEQUENCES (the stateful forms' core)

The kit's RENDERED text for each stateful row is compiled into a test TU with
fixture hooks (stems from a shadow set, §7.6). One "call" is one storage
lifetime: the storage is declared fresh, then a sequence of uses runs over one
subject. **Reference:** the byte loop `F(lo)` per use, plus the same row's
stateless twin (`pf_terms`), giving stateful == stateless == byte loop.

**The families**, each at `hi = n` and `n - 1`:
- **Q1 find-all:** `lo = 0`, then `lo = ans + 1` until `hi`.
- **Q2 find-all with jumps:** `lo = ans + 1 + g`, `g` geometric with means 1,
  8, 70 (crosses blocks).
- **Q3 random walk:** 64 uses at arbitrary `lo` in `[0, n + 2]`, backwards
  included.
- **Q4 sweeps:** `lo` descending from `n` to 0, then ascending.
- **Q5 block edges:** after a first use at 0, `lo` at 63, 64, 65, 127, 128,
  129, `hi - 64 ± 1`.
- **Q6 empties:** `lo = n`, `n + 1`, `n + 5`, `lo = hi` (end_back 1),
  interleaved with real uses (an empty use must leave the cache alone).
- **Q7 null:** `n = 0` with `s == NULL`: `lo` 0, 1 (no read, no write;
  UBSan's `nonnull-attribute` arm).
- **Q8 two sites, one function:** two different sets, two stems, uses
  interleaved over one subject. Also two uses of ONE site sharing storage
  (the VM hat's entry/retry shape).
- **Q9 dirty stack:** each call's function is entered after a call that fills
  the stack with a deterministic non-zero pattern. A missing initializer
  (S832) then reads garbage deterministically instead of a lucky zero.
  `[r4 K1-3]` Two ways this control can FAIL SAFE silently, both closed:
  - a UNIFORM fill gives `base == top`, an empty cache, so the missing
    initializer reads as "nothing cached" and every answer stays right. The
    fill is therefore NON-UNIFORM, chosen so the garbage claims a cached
    block: a period-3 word pattern (`0`, `2^31`, `~0`), i.e. `base = 0`,
    `top = 2^31`, `m` all ones, which satisfies `base <= lo < top` for every
    first `lo` and answers `lo` wrongly unless `lo` is a member. The
    struct's phase in the frame is unknown, so Q9 runs at all three word
    phases (the fill shifted by 8 bytes per run); one phase lands it;
  - at `-O2` the struct can live in registers and never see the stack.
    Q9 is therefore ALSO compiled at `-O0`, where it lives in memory.
  - **S832's detector is named as that pair**: Q9 at `-O0` with the period-3
    fill, plus a C-check that the `mf_locals` text initializes every scalar
    field the helper reads (`base`, `top`, `m`; the ring's `rh`, `rt`; the
    adapt counters), read from the struct definition and the declaration.
    `-Wmaybe-uninitialized` in test-codegen stays as a third, unpromised
    line.

`[rev 2.2]` **The rendered row is `pf_terms_mask`**, through its body text
(the struct declaration and the guarded `next_candidate` use, §4.3), at
W = 8 now and at W = 64 for each SIMD arm when it lands. The stateless twin
is rendered for the test TU only (§8.4). Two additions:
- **Q10 width invariance:** the same sequences through every width's
  `next_candidate` definition in one TU (SWAR, and SSE2/AVX2 where the
  arms exist), each answer equal to the byte loop. Until the arms exist this
  runs the SWAR width only and says so.
- **The block edges** of Q5 are taken per width: 7, 8, 9, 15, 16, 17 and
  `hi - 8 ± 1` at W = 8, as well as the 64-byte edges.

`[r17d]` **Q8 and Q10 are BUILT** (lane r17d): Q8 as `g2s_q8.c` (pairs of
sets, sites A at end_back 0 and B at end_back 1 in one function, a second use
statement of A, interleaved at random), with a SHADOW-HOOK batch beside it
(§7.6); Q10 as a width tripwire: every width the kit has a sub-block for must
be one the leg runs, W8 alone today (its run is the O2 leg), the SIMD widths
printed UNREACHED.

**The subjects:**
- r17s's F1-F4 families (every byte at every lane phase, single probes over
  three backgrounds, random alphabet subjects, guard pages), with
  `n <= 160` so that sequences cross two 64-byte blocks;
- clustered runs (geometric run lengths).

**The population is counted and floored (K35):**
- uses answered from the cache (step 2 hits);
- uses that missed the cache;
- refills;
- overlapped-block fills;
- backward-`lo` uses that found the cache invalid.

Each count has a literal floor in the test. A sequence family whose cache
path never fires is otherwise a green no-op: a sabotage of the cache path
would read green because nothing reached it.

### 12.3 The full kernel test (C1-9), with a K35 false-lane floor

**T5:** every term's two SWAR renderings (LOWEST and EXACT) against the scalar
lane predicate, word by word:
- every term of T1's term space (`EQ` 256, `CUBE` 6,561, `ARC` and complement
  ARC ~65k);
- times every byte value at each of the 8 lanes;
- with the other 7 lanes set from 5 backgrounds (all 0x00, all 0xFF, all the
  same value, all a member, all a non-member near the term's edge).

That is about 0.4 G evaluations, minutes. ADJACENT LANE PAIRS, all 65,536
`(a, b)` at lanes `(j, j + 1)` for `j` in 0..6, run over every `EQ`, every
`ARC` with `L` in {0x00, 0x01, 0x7F, 0x80, 0x81, 0xFE, 0xFF}, and 256 sampled
cubes.

**The assertions:**
- EXACT: every flag equals membership;
- LOWEST: every member lane is flagged, and every false flag sits above a
  flagged member lane of the same term.

**The populations, each with a literal floor:**
- the number of LOWEST false flags observed. It must be above zero, or the
  LOWEST assertion is vacuous: the test could not see a false lane. The floor
  is a literal from a hand derivation (the borrow case `lane j` member,
  `lane j+1 == target ^ 0x01`), never from the test's own output;
- the number of evaluations where a member lane sits immediately below a
  non-member whose value triggers a borrow. This is the "danger" population
  the EXACT spelling must survive.

### 12.4 Guard pages, ASan, UBSan on KIT-RENDERED text (C1-11)

- **G2's harness** places Q1-Q9's subjects against a PROT_NONE page on each
  side. That is the rendered text, not twins (r17s's guard pages ran on twins
  only).
- **The same TU** is built with `-fsanitize=address,undefined`
  (`-fno-sanitize-recover`), with Q7 for the null subject. `make ubsan` and
  `make asan` (SAN-1) already compile every generated matcher the suite builds
  under the sanitizers (`GENCFLAGS`), so R17-b's mover population is covered
  at the merge battery by construction. The report names it as the arm that
  covers the movers.

### 12.4a The trace rendering (`[r4 K1-4, K1-2]`)

The r4 unlock "a trace-build re-probe of cache hits as a standing oracle",
taken at its trigger: it lands with the first stateful row (R17-b).
- **How it is asked for.** A pcrec TRACE build (compiled with the existing
  `PCREC_RANK_PROBE` idiom or a sibling define, as N4's door assertion is)
  sets a test-only policy bit on the art. The kit then renders each
  stateful helper in a trace form. It is a different rendering, not an `#if`
  in a body, so D155 addendum 3 and C18 leg (d) hold; default builds never
  see it.
- **What the trace form adds**, inside the helper definition: on a cache
  hit, it recomputes `F(lo)` by the byte loop and calls `__builtin_trap()`
  on a disagreement; after every fill, it traps unless `top <= hi`.
- `[rev 2.3, r5 K3-2]` **And at each USE, the bound-vs-live trap.** The
  re-probe above reads `c->s`/`c->n`, the same values the helper reads, so on
  its own it cannot see the variable it was copied from being reassigned (it
  compares the helper with itself). The trace form of each use statement
  therefore pastes the live hook texts and traps unless `<stem>__c.n == n &&
  <stem>__c.s == s` before the guard. That restores r4 K1-4's check. It is a
  second line: at R17-b the const parameters (§7.4) already make the
  reassignment a compile error, so in the corpus this trap reaches its site
  without being able to fire. Its own control is a G2 fixture whose body is
  not const and reassigns `n` between two uses (§12.5).
- `[rev 2.3, r5 K3-4]` **The uses-per-activation counter `mfk-upa` (FILED,
  not built).** In the same trace rendering, a per-stem pair of test-only
  counters: activations (incremented by the declaration's trace form) and a
  histogram of uses per activation in the buckets 1, 2, 3 and 4 or more (an
  activation's count is binned when the stem's next activation starts, since a
  function return has no hook, and the last one at exit; zero-use activations
  get their own bucket, 0),
  printed as one line per stem at exit (`mfk-upa <stem> act=<a> 0=<.> 1=<.> 2=<.>
  3=<.> 4+=<.>`). It is file-scope static state, which the matcher's
  reentrancy rule forbids in default builds; a trace build is test-only and
  single-threaded. It gives §9.2's (P) and the bench's Q3 figure for every
  corpus mover without bench time. Trigger (the r5 unlock): the decline arm
  is coded, or the bench answers Q3 "cannot count it".
- `[r17d, review r1 A-N2]` **The re-probe's second spelling shares the
  cover.** `__first` loops over `__member`, which is spelled from the same
  cover as `__mask`, so a wrong cover passes the re-probe. It is NOT extended:
  U1 (`tests/memfn/setfind_cover.py`) holds `__member` on all 256 bytes and
  `__mask` at every lane to the deny arm's table, which shares no source with
  the cover, so on every mover U1 reads the re-probe's loop is a loop over
  pcrec's table; T2 holds the cover of every corpus and bench FIND set to its
  set by plain arithmetic. The gap is U1's sample (every 10th distinct
  pattern), closed for the corpus by `SETFIND_COVER_EVERY=1`.
- **Its population**: the corpus and bench movers under the trace build,
  whose every cache hit is then checked against a second spelling of `F`.
  It is not the only line: G2's sequences (§12.2) and the guard pages stay.

### 12.5 Sabotage rows (S820-S824 and S826-S843 allocated)

`[r4]` Main allocated **S826-S843** (`ef3fa88b`; S825 is taken), so revision
2's S825-S842 are renumbered by one: rev 2's S825 is S826, and so on to S842,
which is S843. The r4 review cites rev 2's numbers; §R4 gives both.

Each row names its WITNESS and how REACH is proven ([MECH-REACH]): the planted
text must appear in the witness's compiled artifact, read by grepping the
emitted C for the row's marker (`<stem>__find`) before and after the plant.
`[r4 K1-9]` For the rows whose plant sits on the CACHE PATH (S830-S834, S842),
text reach is not enough: the planted line can be present and never run.
Their reach is DYNAMIC: each R17-b mover witness is compiled with
`--coverage`, run over its own `.rxt` subjects, and the execution count of
the helper's cache-hit line (`if (m) return lo + ctz`, and for S842 the
ring's drain) must be at least the literal 1 per witness: reach, not a
rate, so the floor is chosen by hand and never read off the run. A witness
whose cache path never fires is replaced, not floored at 0.

| id | plant | caught by | reach |
|---|---|---|---|
| S820 | an `ARC` term's upper edge off by one | T5; G2 sequences over a range cell | witness: a corpus pattern whose PF set is one range (a `[0-9]`/`[a-z]` site) renders `pf_terms` |
| S821 | a `CUBE` mask with one bit wrong | T5; T1 round trip (and §10's refusal if the plant is in the deriver) | witness: a two-member cube set (`[sS]`-led) |
| S822 | the SWAR byte tail drops the last byte | Q1/Q5 at `hi - lo` ≡ 1..7 (mod 8) | any `pf_terms` witness |
| S823 | the SIMD overlapped final block's lane mask shifted by one | the SIMD family of G2 | **UNREACHED until §11.4's SIMD arms exist**; re-aimed there, stated so |
| S824 | the non-wrapping guard spelled `n - end_back > lo` (wraps at `n = 0`, end_back 1) | Q7 (`s == NULL`), guard page, ASan | witness: a bounded (`end_back` 1) PF site, `byte-class-bounded` |
| S826 (rev 2 S825) | `mf_set_terms` widens one cube by a free bit (impure), round-trip check ON | §10's REFUSAL on the witness compiles | any coverable witness set |
| S827 (S826) | the same plant with the round-trip check OFF | T1's independent expansion | as S826 |
| S828 (S827) | non-deterministic tie-break (candidate order unstable) | T2's golden pin | witness: a set with two equal-cost covers |
| S829 (S828) | the complement form drops its negation | T1 complement family; T5 | witness: `[^\n]`- or `[^"]`-led PF site |
| S830 (S829) | the cache test keeps only `lo < top` (no lower bound) | Q3/Q4 (backward `lo`) | any `pf_terms_mask` witness, with DYNAMIC reach (above); plus the twin plant (§13.3) |
| S831 (S830) | a refill does not update `base` | Q2 (jumps) | as S830 |
| S832 (S831) | the storage initializer omitted | `[r4 K1-3]` the PAIR: Q9 at `-O0` with the period-3 non-uniform fill at all three phases (§12.2), and the C-check that `mf_locals` initializes every scalar the helper reads; `-Wmaybe-uninitialized` a third, unpromised line | as S830 |
| S833 (S832) | the pop shifts by `lo` instead of `lo - base` | Q1 | as S830 |
| S834 (S833, REPLACED) | `[r4 K1-2]` the overlapped block at end_back 0 taken at `hi - 63` (reads `s[n]`; `top = hi + 1`) | the guard page (§12.4: F4's subjects end at a PROT_NONE page), ASan, and the trace rendering's `top <= hi` trap (§12.4a). Answers do NOT catch it (the one extra byte answers `hi` either way): that is why rev 2's answer-caught plant was equivalent | an end_back-0 stateful witness, DYNAMIC reach on the overlapped-fill line |
| S835 (S834) | the storage name ignores the stem (two sites collide) | Q8; test-codegen (redeclaration) | the two-site fixture (G2), since no corpus artifact has two today; stated so |
| S836 (S835) | the endianness ternary inverted (byte-swap on LE) | every SWAR test on the LE boxes; the byte-swapped LE test (§6) | any `pf_terms` witness |
| S837 (S836) | a kit local named without the stem (`q`, `c`) | G2's shadow-hook set (§7.6) | G2 fixture |
| S838 (S837) | the adaptive walk mode never decrements `steps` (sticks in walk mode); and separately starts at `lo + 1` | a G2 adaptive timing-free probe (mode counts) for the first; dense Q1 for the second | a `pf_terms_adapt` witness, if built |
| S839 (S838) | the density gate reads `cand_ppm_lo` (admits `D_ABSENT`) | an arm-pin gate case: ABSENT must render the walk | **only if §9.2 is in force**; else the row is withdrawn |
| S840 (S839) | pcrec emits the table although `reads_table` is 0 | test-codegen's `-Werror`: the table is a FUNCTION-LOCAL static (`emit_u8_table`), so the warning is `-Wunused-variable` (rev 2 named `-Wunused-const-variable`, which covers file-scope objects); a C-check that no artifact whose form does not read the table holds `_can_begin_match`/`_start_bytes`/`_start_set` | R17-b's movers |
| S841 (S840) | pcrec builds `set` from the wrong table (`start_set` against `can_begin_match`) | N4's door assertion in the trace build | a DFA-hat witness (`first-class-bounded`) |
| S842 (S841) | the ring's hint is not reset on a backward `lo` | Q3/Q4 | a `pf_terms_ring` witness, if built, with DYNAMIC reach on the drain |
| S843 (S842) | `pf_memchr_set`'s guard removed | Q7 (UBSan `nonnull-attribute` on `__builtin_memchr(NULL, b, 0)`) | a VM-hat \|S\| = 1 witness (`bkn`/`bpr`-shaped) |

**Allocated: S826-S843** (18 ids, main, `ef3fa88b`). Rows for forms the
measurement does not keep are withdrawn at R17-b, and their ids are left
unused (they stay reserved under BOILERPLATE's rule).

**Rows revision 2.1 adds, ids NOT yet allocated** (requested with R17-a's
edit set; each plant is in the kit or pcrec source the refusal names):

| plant | caught by | reach |
|---|---|---|
| `mf_use` stops comparing `s`/`n` with the define's (K1-4) | a G2 fixture whose second use states a different `n` text must be refused | G2 fixture |
| the "placed twice" refusal removed (K2-9) | a fixture calling `mf_locals` twice; and test-codegen's redeclaration error on the artifact | G2 fixture |
| the "placed, never read" refusal removed (K1-8) | a fixture placing storage for a handle whose uses read none; test-codegen's `-Werror` (`-Wunused-variable`) | G2 fixture |
| W0 0 accepted on a FIND site (K2-4) | the R17-a refusal test: a FIND builder with W0 unstated must fail the compile loudly | a fixture site |
| a jump past the declaration point (K1-7): pcrec's point moved below the `seedhead` `goto` | test-codegen's `-Wjump-misses-init` filtered to `<stem>__` | an R17-b DFA mover whose start state carries a scan edge |

`[rev 2.2]` **The sabotage plan after the measurement.** Rows for unbuilt
forms are dropped; rows for the shared helper block and for
`next_candidate` are added. The full status of the allocation:

| id | status | plant (changes from the table above in **bold**) | caught by | reach |
|---|---|---|---|---|
| S820 | kept | an `ARC` term's upper edge off by one | T5; G2 sequences over a range cell | a one-range corpus PF set, now rendering **`pf_terms_mask`** |
| S821 | kept | a `CUBE` mask with one bit wrong | T5; T1 round trip | a two-member cube set |
| S822 | re-aimed | the SWAR byte tail drops the last byte; **at W = 8 the tail runs only when `hi < 8`** (otherwise the overlapped block serves) | Q1/Q5 at `hi` 1..7 | G2 subjects with `n - end_back < 8`; and a corpus mover whose subjects reach that (dynamic reach) |
| S823 | kept, UNREACHED | the SIMD overlapped block's lane mask shifted by one | Q10 on the SIMD family | re-aimed at §11.4's arms |
| S824 | kept | the non-wrapping guard spelled `n - end_back > lo` | Q7, guard page, ASan | a bounded PF site |
| S826-S829 | kept | as above | as above | as above |
| S830-S833 | kept | as above | as above | any **`pf_terms_mask`** witness, DYNAMIC reach |
| S834 | re-aimed | the overlapped block at end_back 0 taken at **`hi - (W - 1)`** (`hi - 7` at SWAR) | guard page, ASan, the trace rendering's `top <= hi` trap | an end_back-0 mover, DYNAMIC reach on the overlapped-fill line |
| S835 | kept | the storage name ignores the stem | Q8; test-codegen | the two-site fixture |
| S836 | re-aimed | the byte-order ternary inverted, **now inside the shared block's SWAR `load_vector`** (§6) | every SWAR test on the LE boxes; the byte-swapped LE test | any mover (every mover carries the block) |
| S837 | kept | a kit local named without the stem | G2's shadow-hook set | G2 fixture |
| S838 | **REASSIGNED** (was the adaptive row's; adapt is not built) | the shared block's guard keyed on the abi ONLY (the helper-set version dropped) | a codegen fixture TU including two artifacts whose blocks carry different helper-set versions must fail with the block's `#error` (K80-a's shape) | fixture: two renderings at set versions 1 and 2 |
| S839 | kept RESERVED, UNREACHED | **the reversed rule's failure: the decline arm declines with density ABSENT** (revision 2.1's `D_ABSENT`-declines rule) | an arm-pin case: absent density, a state-losing call pattern, must render `pf_terms_mask` | re-aimed at §9.2's decline arm, when it lands; withdrawn as written (it guarded the reversed rule) |
| S840 | kept | pcrec emits the table although `reads_table` is 0 | `-Wunused-variable`; the C-check | every R17-b mover (`pf_terms_mask` never reads the table) |
| S841 | kept | pcrec builds `set` from the wrong table | N4's door assertion | a DFA-hat witness |
| S842 | **REASSIGNED** (was the ring's; the ring is not built) | the shared block's content depends on the artifact: **it holds only the primitives that artifact's sites use** | the C-check that every emitted block is byte-identical to the kit's one rendering for its key (§12.7) | any mover whose set uses fewer than all term kinds (an `eq`-only set) |
| S843 | **REASSIGNED** (was `pf_memchr_set`'s; it is not built) | the shared block emitted although no site uses a primitive | R17-b's presence census (block present iff some site renders `next_candidate`, §12.7); at R17-a the identity gates | any non-mover artifact |

**Rows that need NEW ids** (the five refusal rows revision 2.1 added above,
plus two):

| plant | caught by | reach |
|---|---|---|
| the five refusal rows of revision 2.1's table above, with K1-4's row widened: **`mf_locals` AND `mf_use`** stop comparing the `s`/`n` hook texts with the define's | as above | as above |
| the use statement differs by width or layer (a SIMD arm renders another body) | §12.7's body-invariance check | UNREACHED until §11.4's arms; then any mover |
| a W = 64 definition packs its block as 8 lanes (W and pack disagree) | Q10 at W = 64; T5 | UNREACHED until §11.4's arms (or a `pf_terms_mask64` row) |

**The count.** The three reassigned ids (S838, S842, S843) cover three new
rows. They are reassigned rather than left unused because no row text, anchor
or ledger entry was ever written for them, and the allocation is R-17's own;
if main prefers them left unused, the ask below grows by three. **R-17 needs
SEVEN more ids**: five for revision 2.1's refusal rows and two for the
width-dependent rows, requested with R17-a's edit set as before.

`[rev 2.3]` **The sabotage plan, re-tabulated with main's new allocation
S846-S852** (seven ids, journal 2026-10-12; main accepted the reassignment of
S838/S842/S843). Every row, its id, its commit and its status. Rows not
mentioned in the "change" column are as in the rev 2.2 table above.

| id | commit | status | plant (rev 2.3 changes in **bold**) | caught by | reach |
|---|---|---|---|---|---|
| S820 | R17-b | kept; BUILT r17d: DETECTED solo (g2setfind, setfind U1) | an `ARC` term's upper edge off by one | T5; G2 sequences | a one-range corpus mover |
| S821 | R17-b | kept; BUILT r17d: DETECTED solo (setfind: the refusal, T2) | a `CUBE` mask with one bit wrong | T5; T1 round trip | a two-member cube set |
| S822 | R17-b | kept (rev 2.2 re-aim); BUILT r17d: DETECTED solo (g2setfind; dynamic reach) | the SWAR byte tail drops the last byte (`hi < 8` only) | Q1/Q5 at `hi` 1..7 | G2 subjects; a corpus mover reaching it (dynamic) |
| S823 | the SSE2/AVX2 arms | kept, UNREACHED; BUILT r17d: UNREACHED (expected; REACH greps for a V16/V32 guard) | the SIMD overlapped block's lane mask shifted by one | Q10 on the SIMD family | §11.4's arms |
| S824 | R17-b | **re-aimed (K3-2)**; BUILT r17d: DETECTED solo (g2setfind) | the non-wrapping guard spelled **`<stem>__c.n - end_back > lo`** (wraps at `n = 0`, end_back 1) | Q7, guard page, ASan | a bounded PF mover |
| S826 | R17-b | kept; BUILT r17d: DETECTED solo (setfind: the refusal) | `mf_set_terms` widens a cube (impure), round-trip check ON | §10's refusal | any coverable set |
| S827 | R17-b | kept; BUILT r17d: DETECTED solo (setfind: T2 live, U1) | the same with the check OFF | T1's independent expansion | as S826 |
| S828 | R17-b | kept; BUILT r17d: DETECTED solo (setfind: T2 equal); plant REPLACED (the dropped key was equivalent) | an unstable tie-break | T2's golden pin | a set with two equal-cost covers |
| S829 | R17-b | kept; BUILT r17d: DETECTED solo (setfind: the refusal, T2) | the complement form drops its negation | T1 complement family; T5 | a `[^\n]`/`[^"]`-led mover |
| S830 | R17-b | kept; BUILT r17d: DETECTED solo (g2setfind; dynamic reach) | the cache test keeps only `lo < top` | Q3/Q4 | any `pf_terms_mask` mover, DYNAMIC reach |
| S831 | R17-b | kept; BUILT r17d: DETECTED solo (g2setfind; dynamic reach) | a refill does not update `base` | Q2 | as S830 |
| S832 | R17-b | kept; BUILT r17d: DETECTED solo (g2setfind O0dirty, setfind init) | the storage initializer omitted | Q9 at `-O0`, period-3 fill, three phases; the initializer C-check | as S830 |
| S833 | R17-b | kept; BUILT r17d: DETECTED solo (g2setfind; dynamic reach) | the pop shifts by `lo` instead of `lo - base` | Q1 | as S830 |
| S834 | R17-b | kept (rev 2.2 re-aim); BUILT r17d: DETECTED solo (g2setfind guard page; dynamic reach) | the overlapped block at end_back 0 taken at `hi - (W - 1)` | guard page, ASan, the trace `top <= hi` trap | an end_back-0 mover, DYNAMIC reach |
| S835 | R17-b | kept; BUILT r17d: DETECTED solo (g2setfind Q8) | the storage name ignores the stem | Q8; test-codegen | the two-site fixture |
| S836 | R17-b | **re-aimed (K3-1)**; BUILT r17d: DETECTED solo (g2setfind, setfind U1) | the byte-order ternary inverted, inside the **W8 sub-block's** `load_vector` | every SWAR test on the LE boxes; the byte-swapped LE test | any mover (every mover carries W8) |
| S837 | R17-b | kept; BUILT r17d: DETECTED solo (g2setfind shadow-hook batch) | a kit local named without the stem | G2's shadow-hook set | G2 fixture |
| S838 | the SSE2/AVX2 arms | **RE-AIMED (K3-1, K3-8)**; was "the guard keyed on the abi only", which is now the design; BUILT r17d: UNREACHED (expected; REACH greps for a V16/V32 guard) | **all widths' sub-blocks share ONE guard** (`PCREC_MFK_H`) | the mixed-layer TU check (§12.7): a SIMD-off mover then a SIMD-on one, at `-mavx2`, must compile and answer as the byte loop; with one guard the second's V16/V32 are skipped and the TU does not compile | **UNREACHED until §11.4's arms**: with W8 alone, one guard per width and one guard in total are the same text (stated, not floored) |
| S839 | the decline arm | kept RESERVED, UNREACHED; BUILT r17d: UNREACHED, RESERVED (expected; REACH greps for a density read) | the decline arm declines with density ABSENT, **or with (P) supplied by the per-retry proxy alone** (K3-4) | an arm-pin case: absent density, or a proxy-only (P), must render `pf_terms_mask` | re-aimed at §9.2's arm when it lands |
| S840 | R17-b | kept; BUILT r17d: DETECTED solo (setfind table, -Werror) | pcrec emits the table although `reads_table` is 0 | `-Wunused-variable`; the C-check | every R17-b mover |
| S841 | R17-b | kept; BUILT r17d: DETECTED solo (setfind N4 door, rank); re-aimed to the forward search's set | pcrec builds `set` from the wrong table | N4's door assertion | a DFA-hat witness |
| S842 | R17-b | **re-aimed (K3-1)**; BUILT r17d: DETECTED solo (setfind identity) | **a sub-block's content depends on the artifact's sites** (W8 holds only the term kinds that artifact's sets use) | §12.7's identity check, per width, against the kit's rendering for that width | an `eq`-only mover |
| S843 | R17-b | **re-aimed (K3-1)**; BUILT r17d: DETECTED solo (setfind presence) | **a width's sub-block emitted where no site in the artifact uses that width** (W8 in an artifact with no mover; at the arms also V16/V32 in a SIMD-off artifact) | §12.7's presence census, per width | any non-mover artifact (W8); SIMD-off movers once the arms exist (V16/V32) |
| S846 | R17-a | NEW (rev 2.1's K1-4 row, **narrowed by K3-9**) | **`mf_locals`** stops comparing the `s`/`n` hook texts with the define's (`mf_use` compares nothing to remove) | a G2 fixture whose `mf_locals` states a different `n` text must be refused | G2 fixture |
| S847 | R17-a | NEW (rev 2.1, K2-9) | the "placed twice" refusal removed | a fixture calling `mf_locals` twice; test-codegen's redeclaration error | G2 fixture |
| S848 | R17-a | NEW (rev 2.1, K1-8) | the "placed, never read" refusal removed | a fixture placing unread storage; `-Wunused-variable` | G2 fixture |
| S849 | R17-a | NEW (rev 2.1, K2-4) | W0 0 accepted on a FIND site | the R17-a refusal test | a fixture site |
| S850 | R17-b | NEW (rev 2.1, K1-7) | a jump past the declaration point (the point moved below the `seedhead` `goto`) | `-Wjump-misses-init` filtered to `<stem>__` | an R17-b DFA mover whose start state carries a scan edge |
| S851 | R17-b | **NEW (K3-2)** | the use's guard pastes the live `n` hook instead of `<stem>__c.n` | §12.7's use-text check (the guard names `<stem>__c.n` and no `s`/`n` hook text). Answers do NOT catch it: with the const parameters the two values are equal; that is why the check is structural | every mover |
| S852 | R17-b | **NEW (K3-3)** | a stateful body's head drops a const (`const unsigned char *subject` or `size_t subject_length`) | test-codegen's head check over movers (§12.7) | every mover |
| (id needed) | R17-b | **NEW (K3-2)** | the trace rendering's bound-vs-live trap removed | a G2 trace fixture whose non-const body reassigns `n` between two uses must trap | G2 fixture (the corpus cannot reach it: its bodies are const) |
| (id needed) | R17-b, or N6's own request | **NEW (K3-7)** | pcrec's reserved-prefix refusal removed (N6) | a CLI case (`-p pcrec_mfk`, `-p PCREC_MFK_x`) and a library case expecting the refusal | the CLI/library tests |
| (id at the arms) | the arms | rev 2.2, kept | the use statement differs by width or layer | §12.7's body-invariance check | UNREACHED until the arms |
| (id at the arms) | the arms | rev 2.2, kept | a W = 64 definition packs its block as 8 lanes | Q10 at W = 64; T5 | UNREACHED until the arms |

`[r17d]` **S820-S843 are built** (lane r17d, 2026-10-12; files
`tests/mech/sabotages/S8xx_r17d_*.sh`, the new mech arm `g2setfind`). Three
places the rows read the table above differently, each stated in its row:
T1 (the blinded family) and T5 (§12.3) are not built, so the rows naming
them are held by T2's independent expansion, U1 and G2's sequences; S834's
trace `top <= hi` trap cannot fire on the planted shape (top stays `hi`), so
its detectors are the guard page, ASan and the cache invariant; S841 plants
the DFA hat's kit set from the forward search's `can_begin_match` set
(the "wrong table" available at that site). S828's first plant (objective 4
dropped) was an equivalent mutant on T2's population and was replaced by the
reversed key. Verdicts and logs: `docs/dev/lanes/r17d_report.md`.

**The count.** S846-S852 cover seven rows: the four R17-a refusal rows and
three R17-b rows. **R-17 needs TWO more ids for R17-b** (the trace trap row;
the N6 row, which moves to N6's own request if N6 does not ride R17-b), and
**two more at the SIMD arms' event** (body invariance by width; the W = 64
pack), requested with the arms. Total 11 new rows against 7 allocated. The two
arm rows are deliberately not asked now: they are UNREACHED until the arms
exist, and their ids would sit unused through R17-b.

### 12.6 The rest of the checklist (C3-9)

- `tests/memfn/rows.tsv` and `row_floors.tsv`: one row per new arm. The floors
  are counted from a pcrec-side artifact census, not from the kit.
- **The `pf_walk` / `pf_walk_bounded` witnesses are RE-PICKED.** Today's
  witnesses may now render a term row. A new walk witness is a set with no
  cover of `S` or `¬S` within K: for example `\w` (`0-9`, `A-Z`, `a-z`, `_` is
  4 terms; uncoverable at K = 3, so it re-picks again if K grows), or a
  scattered set. They are chosen by running `mf_set_terms` over the census,
  and also kept reachable through each row's deny.
  `[rev 2.2]` At K = 4 `\w` IS coverable (exactly 4 terms), so it is no
  longer a walk witness. The re-pick needs a set with no cover of `S` or `¬S`
  within 4 terms (for example a scattered set of five or more isolated bytes,
  or `[\w.-]`-like classes if they derive to five or more terms), found by
  `mf_set_terms` over the census.
- `options.def` rows and the registry floor: §11.3.
- **The tuning hunk:** the `memfn` rows are printed live by `--list-axes`, so
  no `tuning.md` row is needed beyond §11.3's method sentences.
- **S68 / S524 / S478 re-aims** (the panel's list). Their anchors may quote the
  walk's text or `pf_vm_emit_first_class`'s comment. They are re-anchored from
  `git show HEAD:<path>` with their intent re-verified (BOILERPLATE), at R17-b,
  after grepping `tests/mech/sabotages/` for the moved identifiers (coding_guide
  §3.5). `[r4 K2-7]` R17-a carries its own derived re-aim list and the
  [SABANCHOR] exact-count gate (§11.1's control); R17-b repeats both for its
  own edit set.
- `[r4 K2-8]` **The TEST READERS of the walk text, named, with their fates.**
  Revision 2's reader census was spec-only. These checks read the emitted
  walk or table text, and on R17-b's movers that text becomes
  `<stem>__find(…)` and, for a row that does not read it, no table at all,
  so each would go VACUOUS (still green, reaching nothing) without a re-aim:

  | reader | what it reads today | fate at R17-b |
  |---|---|---|
  | `tests/codegen/run_dfa_stamps.sh:254` | `!rx_can_begin_match[subject[scan_position]]`, the bitmap arm's marker (`pf_bc`, and `bnd` for the bounded loop) | reads the walk on the DENY arm (population unchanged); on the default arm it gains the kit marker (`_pf__find(` / `_pf__c`) as a second spelling of "the set arm" |
  | `tests/codegen/run_dfa_stamps.sh:260` | `!rx_start_bytes[subject[scan_position]]`, the DFA hat's marker (`pf_fc`) | the same, for the DFA hat |
  | `tests/assertions/run_mline_diff.sh:189` | `rx_(can_begin_match\|start_bytes)[` to record the `bitmap` mechanism | the same two arms; MLINE's own memchr form does not move |
  | `tests/codegen/run_cpset_structure.sh:932` (and its `EMITTED_BYTES` manifest, `:855`'s history) | byte counts of twelve samples, two of them VM-hat movers whose `rx_start_set` table and seeks it counts | a deliberate re-record with the diff read, as every abi event does there |
  | `tests/codegen/run_anchored_match.sh:213-223` | asserts NO `rx_can_begin_match[`/`rx_start_bytes[` walk inside `rx_match` | gains the kit marker in the same `grep -E`, or the "no PF inside `rx_match`" assertion goes blind to a moved site |
  | `tests/codegen/run_offset_skip.sh` §2c (`:279`) | asserts the `<p>_ofsskip` helper does not read `rx_can_begin_match` | **unchanged**: the offset-skip sites do not move at R-17, so its population is untouched; listed because K2-8 named it |
  | `tests/startset/vmhat_checks.py` `[vm-table]` (sabotage S478's structural detector) | the emitted `start_set` table equals the `start_set` fact | on a mover whose form does not read the table there is no table: the check reads the DENY arm (where it is emitted) and, on the default arm, the trace build's N4 door record of the site's `set` |

  **Population and floor.** Each reader runs on BOTH arms. On the all-deny
  arm (`--memfn=no-pf-terms,…`, today's walk) its population is today's,
  and that count is pinned as a LITERAL floor taken from the tree BEFORE
  R17-b (so it shares no source with the change). On the default arm its
  population is the R17-b mover census's count for the arm it reads (the
  pcrec-side artifact diff of §11.2), never the kit's `moved`. The numbers
  themselves are OWED to that census; this revision ran nothing.
- `tests/memfn/site_manifest.tsv` (C17): unchanged. The sites are already
  `delegated`.
- `memfn/PROVENANCE.md`: one row for `terms.c` (C16).
  `[rev 2.2]` And one for the shared block's renderer.

### 12.7 The shared helper block and `next_candidate` (`[rev 2.2]`)

| check | checked against | population (K35) | sabotage |
|---|---|---|---|
| **block identity:** every emitted block is byte-identical to the kit's one rendering for its (abi, helper-set version) key | a rendering the test asks the kit for directly, keyed only by the version, never by any artifact | every R17-b mover's block, counted, floored by the mover census | S842 |
| **block presence:** a block is present in an artifact iff some site in it renders `next_candidate` | the artifact's own site text (grep `__next_candidate(`), not the kit's report | movers (present) and non-movers (absent), both counted | S843 |
| **the key's `#error`:** a TU including two artifacts whose blocks differ in key fails to compile with the block's message; one with equal keys compiles | the compiler (K80-a/-b's shape) | fixtures: equal keys, different abi, different set version | S838 |
| **mixed-layer TU:** a SIMD-off mover artifact included BEFORE a SIMD-on one, compiled at `-mavx2`, compiles and answers equal to the byte loop | the byte loop | a fixture TU; reachable once §11.4's arms exist, stated UNREACHED until then | (S842's plant also fails it) |
| **byte order in one place:** no kit-rendered text outside the shared block (its SWAR `load_vector` and its `_Static_assert`) names `__BYTE_ORDER__` or `__builtin_bswap` | a grep over the rendered movers | every mover | S836 |
| **body invariance:** at every mover, the search function's text (the declaration and the guarded use) is byte-identical between `-fno-memfn-simd` and `-fmemfn-simd`, and between every width the test can force | the SIMD-off artifact's own text | every mover; vacuous (and stated so) until §11.4's arms exist | the "use differs by width" row |
| **`next_candidate`'s inputs:** `mf_locals` refuses `s`/`n` hook texts that differ from the define's; `mf_use` refuses an `n` text that differs | G2 fixtures stating mismatched hooks | fixtures | the widened K1-4 refusal row |
| **the struct stays local:** the disassembly check owed with R17-b (§13.4) also reads whether `c->s`/`c->n` are reloaded in the hot loop | `objdump` of the movers' inlined helper | a sample of movers per width | none (a measurement, not a check) |

`[rev 2.3]` **The rows revision 2.3 changes or adds** (they replace the rows
of the same name above):

| check | checked against | population (K35) | sabotage |
|---|---|---|---|
| **sub-block identity (K3-1):** every emitted sub-block is byte-identical to the kit's one rendering for its WIDTH | a rendering the test asks the kit for directly, by width only, never read off an artifact | every mover's W8 sub-block (and V16/V32 once the arms exist), counted, floored by the mover census | S842 |
| **sub-block presence (K3-1):** sub-block W is present in an artifact iff some site in it renders a width-W definition; at R17-b, W8 iff a mover | the artifact's own site text (`__next_candidate(` and, at the arms, each width's definition name), not the kit's report | movers (W8 present) and non-movers (absent), both counted; at the arms, SIMD-off movers (V16/V32 absent) | S843 |
| **the key (K3-8):** WITHDRAWN as a kit row. A TU mixing two abis fails at K80's own `#error`, whatever the sub-blocks; K80's existing check (K80-a/-b) covers it. The sub-blocks carry no value to test | — | — | — (S838 re-aimed to the next row) |
| **mixed-layer TU:** a SIMD-off mover artifact and a SIMD-on one, in BOTH orders, compiled at `-mavx2`, compile and answer equal to the byte loop | the byte loop | a fixture TU; UNREACHED until §11.4's arms, stated so | S838 (and S842's plant fails it too) |
| **byte order in one place:** no kit-rendered text outside the W8 sub-block (its `load_vector` and `_Static_assert`) names `__BYTE_ORDER__` or `__builtin_bswap` | a grep over the rendered movers | every mover | S836 |
| **`next_candidate`'s inputs (K3-2, K3-9):** `mf_locals` refuses `s`/`n` texts that differ from the define's; the USE text names `<stem>__c.n` in its guard and pastes no `s`/`n` hook text | G2 fixtures stating mismatched hooks; a grep of each mover's use statement for the bound name and for the hook texts | fixtures; every mover's use statements, counted | S846 (the refusal); S851 (the use text) |
| **the const inputs (K3-3):** every body holding a stateful site declares `const unsigned char *const subject` and `size_t const subject_length` | a grep of each mover's holding-function head, located by the `<stem>__c` declaration it contains | every mover, counted; floored by the mover census | S852 |
| **the bound-vs-live trap (K3-2):** under the trace rendering, a use whose live `n` or `s` differs from the struct's copy traps | a G2 fixture whose non-const body reassigns `n` between two uses | the fixture; the corpus under the trace build reaches the trap's site at every use but cannot fire it (const bodies), which is stated, not floored | (id needed) |

## 13. The follow-up measurement (source text; `[rev 2.2]` RUN 2026-10-12 as slot2, §13.5)

### 13.1 What it adds to step 2, and why

| addition | panel id / ruling | where |
|---|---|---|
| stateful twins: `mask8_swar`, `mask64_swar`, `mask64_sse2`, `mask64_avx2`, `ring_swar`, `ring_avx2`; the composable-pieces variant `mask64i_swar` (pop inline, refill a call) | Q-R17-1 (ruling 2), D155 add. 3 | `gen_twins_r2.py` |
| adaptive twins `adapt_swar`, `adapt_avx2` (stateless fast ↔ table walk) and `adapt_mask` (mask ↔ walk) | Q-R17-1 | `gen_twins_r2.py` |
| THE STATE-RESET AXIS: `reset=inf` (one storage per pass: within-call re-entry), `reset=1` (fresh per FIND: every hit a new call), `reset=4,16` (a fresh call every K hits: true matches among false candidates) | §1.3's correction | `time_r2.c -k` |
| the ppm grid at 64 KiB: 0, 1k, 20k, 70k, 100k, 150k, 200k, 300k, 400k, 500k, 600k, 800k, 900k, 1M; at 1 MiB: 0, 70k, 300k, 600k, 1M | C2-1, C2-3 | `run_time_r2.sh` |
| dense percall (Q-R5): percall at 300k and 800k, spans 16 and 64 | C2-3 | same |
| misaligned `lo` (odd offsets) | C2-3 | `time_r2.c -A` |
| clustered placement: geometric run lengths, mean 2, 8, 32, at 70k and 300k | C2-2 | `time_r2.c -g` |
| real bench subjects for `lc`/`dig`/`bkn`/`bpr` (and any listed) via `SUBJ_TSV`, with their measured ppm and run profile printed per row | C2-2 | `time_r2.c -s`, columns `ppm_meas`, `run_mean` |
| synthetic cells `syn4`/`syn5`/`syn6`/`syn8` (k pairwise non-mergeable members: exactly k terms) and `x80` (a range crossing 0x80) | C2-4, C1-10 | `gen_twins_r2.py` |
| branch-miss counters: one form per `perf stat` run, a fixed rep count, the floor run subtracted | C2-1 | `run_time_r2.sh` perf pass |
| the noise band, raw and `d_floor` both, the per-cell losing set, memchr at 800k per cell | C2-5..C2-8 | `summarize_r2.py` |
| the candidate-SEQUENCE answer check (stateful == stateless == byte loop) with a planted stale-state control | §8.2, §12.2 | `check_r2.c` |

### 13.2 The files (under `probes/r17/`, own CLAUDE.md updated)

- `gen_twins_r2.py`: loads `gen_twins.py` by path (with `python3 -I` the
  script's directory is not on `sys.path`) and reuses its cells and stateless
  forms. It adds the synthetic cells and the stateful/adaptive forms, and
  emits `twins_r2_gen.h` with one table `TW2[]` carrying stateless and
  stateful entries.
- `check_r2.c`: the exhaustive check over sequences Q1-Q7 (§12.2's twin-level
  analogue) on r17s's subject families at `n <= 160`. `PLANT=1` swaps every
  stateful twin's cache test for a no-lower-bound variant (S830's twin), and
  the check must then catch EVERY stateful twin.
- `time_r2.c`: `time.c`'s calibrated, interleaved, checksummed shape, with the
  new axes `-k` (state reset), `-g` (clustered), `-A` (misaligned) and `-P`
  (perf mode: one form, fixed reps, no calibration).
- `run_time_r2.sh`: renders, builds, RE-RUNS THE CHECK FIRST (a red check
  voids the run), then the grid, then the perf pass. Last line:
  `R17R2 TIMING COMPLETE rc=N rows=K void=V perf=P`.
- `summarize_r2.py`: the reading tables and the verdict question.

### 13.3 The exact command, completion line and wall time

From the worktree root, in a QUIET slot: one heavy thing on the box, with the
core and its SMT sibling idle.

    L=build/scratch/r17/slot2 CORE=<idle core> R=7 MIN_MS=50 \
      [SUBJ_TSV=build/scratch/r17/subjects.tsv] \
      nohup bash docs/design/memfn/probes/r17/run_time_r2.sh \
        > build/scratch/r17/slot2.log 2>&1 & disown
    # dry run (prints every pinned invocation, builds nothing):
    DRYRUN=1 L=build/scratch/r17/dry2 CORE=12 bash docs/design/memfn/probes/r17/run_time_r2.sh

- **Completion line:**
  `R17R2 TIMING COMPLETE rc=0 rows=<K> void=<V> perf=<P>`, with `void=0`
  required. `perf=unavailable` is stated, not a failure.
- **Wall time, ESTIMATED** (not run): about 640 timing invocations at about
  15 rows each, R 7, MIN_MS 50. That is about 9 s each, about 96 min, plus the
  check (≤ 10 min) and the perf pass (about 130 single-form runs, about 3 min):
  **about 1 h 45 min ± 30% on one pinned core.** The quick tier
  `R=5 MIN_MS=30` is about 50 min. Base: step 2's 169 invocations at 5-6
  forms took 13 min (22:46-22:59). `[rev 2.1]` Lane r17dry's dry run lists
  619 invocations (574 real + 45 synthetic) and 126 perf runs; its arithmetic
  estimate is ~80 min (65-100). The 1 h 45 min stands as the upper bound.
- **What has run** (lane r17dry, `docs/dev/lanes/r17dry_report.md`): the
  generated header and all three binaries compile warning-free at `-Wall
  -Wextra`; the check gives `R17R2 CHECK: twins=190 calls=4037733349
  mismatches=0` with every mechanism population non-zero; the planted check
  gives `R17R2 PLANT: cache twins caught = 152 of 152`; ASan+UBSan are clean
  on a reduced cell set. Its two harness fixes (an `NMAX >= 129` guard, an
  optional argv cell filter) left `run_time_r2.sh` unchanged.
- **Revision 2.1 leaves the harness unchanged** (`[r4]`: "the harness
  measures forms, not the contract, and it is ready"). K1-2's replaced plant
  (S834) and K1-3's `-O0` dirty-stack control are §12's checks on the KIT'S
  RENDERED text, built with R17-b; the harness's twins declare their state
  fresh per sequence (`check_r2.c`'s `sreset`) and have no end_back-0
  overlapped over-read plant to replace, so neither disposition touches it,
  and the command and completion line above stay valid.
- **The subjects TSV** is regenerated read-only with the lossreview
  instruments (`docs/dev/optloop/lossreview/vm/regen_subjects.sh`'s shape),
  never by writing to pcrec-bench.

### 13.4 The verdict question and how it is read

**The question:** do the stateful/adaptive forms beat `table` at the dense
controls (`dig`, `lc`, `bkn`, `bpr` at 100k-1M ppm, `reset=inf`) while
keeping their sparse wins (0-70k ppm, every cell, every reset)?

**The reading rules (`summarize_r2.py`):**
- **Verdict basis: raw ns per call**, because both forms pay the same driver.
  `d_floor` is printed beside it, and a row where the two disagree in sign is
  named (C2-6).
- **The noise band** is the 95th percentile of `med/min` over all rows. Step
  2's was ≤ 1.05 on 898 of 910 rows. A ratio within the band is a TIE, never a
  win or a loss (C2-5).
- **A form is a candidate** iff it has no LOSS beyond the band in any row its
  sites can be in (K-1), and has a WIN beyond the band somewhere.
  - SIMD rows are read against the best SIMD-off row (D147).
  - The `reset=1` rows answer "what if every hit is a match": a stateful form
    must not lose there (it degenerates to stateless plus its init).
- **The per-cell losing set** and **memchr at 800k per cell** are printed
  (C2-7, C2-8).
- **The branch-miss columns** test the hypotheses below.
- **The disassembly check** (owed with the run, a separate `objdump` read):
  each inlined `<stem>__find`-shaped twin has no call in its hot loop.

**What the verdict decides:**
- which rows of §4.1 exist, and their order;
- whether §9.2's gate is in force;
- K, read from the syn cells as the largest term count winning everywhere
  (the measured boundary);
- whether the mask's W is 8 or 64;
- whether the composable-pieces shape replaces the helper (`mask64i_swar`).

**Hypotheses to falsify** (UNMEASURED):
- **H1.** At 300k `reset=inf`, `mask64_swar` beats `table`: the per-hit cost
  becomes a shift and `ctz`, with no loop-exit misprediction.
- **H2.** At `reset=1`, `mask64_*` ≈ `swar` + about 1 ns (init + the fuller
  block). It may LOSE at percall 16 at sparse density, which the overlapped
  block mitigates.
- **H3.** `ring_*` loses to `mask64_*` everywhere except possibly 1 MiB at
  20k-70k.
- **H4.** `adapt_swar` ties `table` at ≥ 300k (walk mode) and keeps `swar`'s
  sparse wins, minus the probe cost.
- **H5.** `table`'s non-monotone 300k figure (C2-1) is branch-prediction: its
  branch-miss rate per call peaks between 100k and 500k.
- **H6.** K ≥ 4 holds at SWAR on the syn cells sparse, and fails dense
  without state.

### 13.5 RUN: what slot2 measured and what it decided (`[rev 2.2]`)

**The run.** 2026-10-12, 03:48:18-05:37:42 (1 h 49 min, against §13.3's
upper bound of 1 h 45 min and r17dry's ~80 min arithmetic) on the Linux dev
box (7700X Zen 4), core 14 with its SMT sibling idle, gcc 15.2.0 `-O2 -fPIC`,
R 7, MIN_MS 50, a quiet box. Pre-checks: 190 twins, 4,037,733,349 calls, 0
mismatches; planted 152 of 152. Completion line `rows=9654 void=0 perf=126`.
Kit tier, UNOFFICIAL (D144 addendum 4). Data `probes/r17/out/slot2/`; reading
`probes/r17/reading_slot2.md` (lane r17rd), every table recomputed from
`times.tsv` by `analyze_slot2.py`. Noise band 1.016 (p95 of med/min).

**The verdict question** (§13.4). YES at `reset=inf`, by layer: `mask8_swar`
beats `table` at every density from 70k to 1M at 64K (0.86 at 300k, worst
cell 0.93 at 200k) and keeps sparse wins (0.59 at 0 ppm, 0.54 at 20k);
`mask64_sse2` and `mask64_avx2` read 0.88-0.90 at 300k. But NO form passes
K-1 over all 574 real-cell rows, and the losses concentrate in three
corners, all "the hit is within a few bytes AND the state does not carry"
(§9.2's (a)-(c)).

**What it decided:**

| §13.4 decision | outcome | where it lands |
|---|---|---|
| which rows exist, and their order | `pf_terms_mask` only (mask8 at SWAR, mask64 at SSE2/AVX2); adapt, ring, stateless, memchr_set not built; mask64 SWAR designed, not built | §4.1, §4.3 |
| whether §9.2's gate is in force | rewritten by D162 addendum 1: ADMIT when absent, decline only on positive density ≥ ~300k with a state-losing pattern; no input reaches the decline today | §9.2 |
| K | 4, read on the sparse regimes (no K wins dense percall) | §3.3 |
| the mask's W | per width: 8 at SWAR, 64 at SSE2/AVX2; W is not decided by one regime (`mask8_swar` loses to `mask64_swar` at 1M: 2.18 at 70k) | §8.1 |
| the composable-pieces shape | `mask64i_swar` equals `mask64_swar` within noise: pieces cost nothing measurable | §4.3, D155 addendum 4 |

**The hypotheses:**

| H | outcome |
|---|---|
| H1 (`mask64_swar` beats `table` at 300k `inf`) | at 1M yes (0.37); at 64K a TIE (0.98/1.13) |
| H2 (`reset=1` costs about +1 ns) | FALSIFIED: the refill costs `mask64_swar` +8.5 ns, `mask64_avx2` +2.4, `mask8_swar` +2.0 per call at 300k |
| H3 (the ring loses except perhaps 1M 20k-70k) | the exception is FALSIFIED (1.38-1.47 there); the ring loses everywhere |
| H4 (adapt ties `table` at ≥ 300k) | FALSIFIED (2.25 at 300k) |
| H5 (`table`'s miss rate peaks 100k-500k) | FALSIFIED at 64K: it peaks at 800k (0.63 per call) and 300k is a trough (0.038), consistent with the predictor learning the 64K stream |
| H6 (K ≥ 4 holds sparse, fails dense without state) | HELD: K = 4 sparse margins 0.77-0.86; plain `swar` at K = 4 loses 1.05 at 70k and 1.54 at 300k |

**Still OWED from §13** (each now owned elsewhere):
- **Real bench subjects** (C2-2; no `SUBJ_TSV` was given): moved to the bench
  relay that gates R17-b (§11.2a), which measures them on the bench's own
  harness rather than through the kit's.
- **The disassembly check** (no call in an inlined helper's hot loop; the
  syn8 anomaly; whether `c->s`/`c->n` stay in registers): owed with R17-b,
  over the kit-RENDERED movers rather than the twins.
- **A 1 MiB perf pass**, to test the predictor-memorization inference
  directly: not owed by R-17 (the bench relay answers the question it would
  inform); filed as a kit-tier probe if the bench's numbers disagree with the
  64K reading.
- **A GAP/BLOCK0/CAP sweep**: not owed (§9.1; filed).

## 14. pcrec-side needs, drafted as responses.md text

The kit session is the only writer of `memfn/docs/responses.md`. The blocks
below are DRAFT TEXT for the kit manager to file after review. Each states
facts or capabilities (D157), never the kit's method.

> **R-17 rev 2 — what pcrec provides (facts and capabilities; design:
> docs/design/memfn/setfind.md). All items PROPOSED for main's chunk-2 note /
> R-18 ratification.**
>
> **STORAGE (main's question, answered — setfind.md §7).** pcrec PROVIDES, for
> each FIND site that is a DFA prefilter, a DFA hat or the VM hat:
> 1. **a declaration point.** pcrec states `decl_point = 1` on the site and
>    calls `mf_locals(art, handle, hooks, body)` there exactly once, in the
>    function holding every use. The point DOMINATES every use: no
>    `goto`/computed `goto` runs from before it to after it. It is in the
>    forward loop's caller, before the scan loop (DFA), and before the entry
>    seek in `<searchfn>_run` (VM);
> 2. **automatic storage for one call**, written and read only by the kit's
>    text;
> 3. **invariance:** `s`, the bytes `s[0..n)`, `n` and `end_back` do not change
>    across the site's uses. Nothing is promised about the cursor;
> 4. **one handle for every use of one site** (the VM hat's entry and retry);
> 5. **a stem:** `fn_ref` names `<fn>_pf`, after the function holding the
>    uses, and pcrec reserves `<stem>__*`. The stem holds pcrec's prefix
>    placeholder and is opaque.
>
> Cross-call state ([FINDALL-NEXT]/[IFACE-PUSH]) is not asked.
>
> **WINDOW FIELDS (the degenerate case, setfind.md §2.2).** Every FIND builder
> states `window_stated = 1`, `move_back` (signed, from the span's beginning;
> `d_min` on every R-17 site, i.e. 0, and -1 on MLINE; `MF_MOVE_UNBOUNDED`
> reserved) and `overshoot = 0`. FIND's result on a STMT/ASSIGN FIND site is
> documented as the window's beginning, never below `lo`, in a non-wrapping
> spelling. It is not extended to ALL_PRESENT's `ret_pred` reply. Further
> spans, the reply's span, the consumer price and a joint rate are R-18's.
>
> **N1 (workload data), as an ANALYSIS OBJECT (Frank, 2026-10-12).** pcrec
> passes ONE read-only analysis object per compile (`mf_analysis`, defined in
> memfn.h; `mf_site.analysis`, NULL = none stated). It carries every
> compile-wide distribution pcrec has, as a versioned list of tagged kinds:
> byte rates, and whatever else the resolved bundle carries today (`cpfreq`,
> bigram/run-rarity). Each kind is present or explicitly ABSENT, with no
> presumed values. The kit ignores kinds it does not know, and new kinds
> append without a site-contract change. Distributions only, no per-site
> derived answers: the kit derives a set's rate or a ranking itself. A slot
> for per-site facts is reserved, to be filled only when a measured case
> needs a fact the kit cannot derive. `[rev 2.2]` (D162 and its addendum 1.)
> R17-b does NOT read it: R-17's row ADMITS when density is absent, which is
> every site today. Its first R-17 reader is the decline arm (setfind.md
> §9.2), which lands only when the object carries a byte-rate kind AND a
> call-pattern or match-density kind, or when pcrec states the hybrid
> prefilter's `activation` fact. No request is filed for the object by R-17.
> Any regeneration that moves an emitted byte is an abi event.
>
> **N2 (what remains).** Two define points, each with a precedent: the DFA PF
> site is DEFINED from a new `u.pf.emit_block` on its rows (where the
> offset-skip FUNC is defined, file scope above the body); the VM hat beside
> `pcrec_emit_req_run_blocks`, above `<searchfn>_run`. The file stream at
> that point is `file_scope`. No new sink, no flush change, and no table moves
> to file scope.
>
> **N3.**
> - (a) No include is predicted. pcrec's prologue prediction is unchanged;
>   the kit's R-17 text needs no header, and `pcrec_memfn_art_end`'s existing
>   assertion holds that.
> - (b) After the define, pcrec reads `mf_defined(art, handle, &res)` and
>   emits the site's table iff `res.reads_table`.
> - (c) The uniform FIND description (pcrec no longer choosing byte against
>   table) is deferred to R-18 with the stamp question. R-17's sites keep
>   pcrec's PF row split.
>
> **N4.** In trace/test builds, `find_site` asserts that `set` equals the
> table it names. The same builds ask the kit's trace rendering.
>
> **SPEC (D80, at R17-b).** `RX_DFA_PREFILTER`'s `byte-class`,
> `byte-class-bounded` and `first-class-bounded`, `RX_VM_START_SCAN`'s
> `first-class`, and tuning.md §2.42¶2/¶4 are reworded method-blind. VALUES
> are unchanged. The registry `memfn` floor is raised.
>
> **Sabotage ids.** S826-S843 allocated (setfind.md §12.5); about five more
> for the refusals revision 2.1 adds, requested with R17-a's edit set.
> `[rev 2.2]` Three of the allocation (S838, S842, S843) are reassigned from
> forms the measurement did not keep to the shared helper block's rows; R-17
> asks for SEVEN more ids with R17-a's edit set (five refusal rows, two
> width-dependent rows). If main prefers the three left unused, the ask is
> ten.
> `[rev 2.3]` Main allocated S846-S852 and accepted the reassignment. With
> revision 2.3's rows (setfind.md §12.5): S846-S849 are R17-a's four refusal
> rows; S850-S852 are R17-b's jump-past-the-point, live-`n`-guard and
> const-head rows. R-17 asks for **two more for R17-b** (the trace
> bound-vs-live trap; the N6 refusal, which moves to N6's own request if N6
> does not ride R17-b) and will ask for **two at the SIMD arms** (body
> invariance by width; the W = 64 pack), not now: they are UNREACHED until the
> arms exist.
>
> **`[rev 2.2]` THE GATE (D162 addendum 1).** R-17's stateful row ADMITS
> every coverable set site by default. It declines only on positive evidence
> of candidate density at or above ~300k ppm together with a state-losing call
> pattern, and no such evidence reaches the kit today. A bench relay on real
> subjects gates R17-b before merge: the kit delivers the branch with its
> alpha numbers, main relays `docs/design/memfn/setfind_bench_request.md` to
> pcrec-bench (D78) and schedules the box, and a real cell losing beyond the
> regression floor stated there returns R17-b to the kit. The state-lost dense
> residual (`mask8_swar` 1.65x at 300k when every candidate is a true match)
> is [FINDALL-NEXT]'s; its measured break-even is 2-3 candidates per state
> lifetime.
> `[rev 2.3, r5 K3-4, K3-5, K3-6]` Three corrections. (1) The bench's gate rule
> changed: a LOSS must reproduce on an immediate re-run; F comes from the
> bench's standing per-cell spread, else from at least three layout-perturbed
> A/A pairs; the absolute criterion applies to every cell; the kit's 0.05 floor
> is withdrawn. This goes to pcrec-bench as a corrigendum to I-148
> (`docs/design/memfn/setfind_bench_corrigendum_I148.md`). (2) The hybrid
> prefilter site is NOT "state-losing by construction": rejected candidates are
> more uses in one activation, so the call-pattern input is uses per
> activation, and the per-retry fact is only a proxy. (3) The break-even is
> bracketed, not measured: the stateful form loses at one use per activation
> and wins at four, so it lies in (1, 4); `B_EVEN = 3` is an unmeasured value
> inside that bracket, and `T_DENSE`'s loss edge is bracketed in (70k, 300k].
>
> **N5 `[rev 2.2]` (a reserved stem in emitted files).** The kit's shared
> primitive block (D155 addendum 4) is defined once per file, so its names
> cannot carry a prefix. pcrec reserves the kit's file-scope stem (PROPOSED:
> `pcrec_mfk_`, guard `PCREC_MFK_H`) in every emitted file, as it reserves
> `<stem>__*` per site: it declares no identifier there. The block is emitted
> scaffolding: it first appears in R17-b inside that step's abi event, and any
> later byte it moves is a pcrec abi event in the same commit (D155 addendum
> 4's manager note). pcrec's site fields never name a primitive (D157).
>
> **`[rev 2.3]` N5, restated (the per-width block, r5 K3-1, K3-8).** The block
> is one sub-block PER WIDTH (`PCREC_MFK_W8_H`, `PCREC_MFK_V16_H`,
> `PCREC_MFK_V32_H`; PROPOSED spellings), each emitted only in an artifact
> where some site uses that width. A SIMD-off artifact carries the W8
> sub-block only, which holds no SIMD text, so the later SIMD arms move no
> SIMD-off byte, and a new width (AVX-512, NEON) is an event only for the
> artifacts that use it. The guards carry no version and no value: pcrec's
> valued `PCREC_RX_ABI_H` guard, emitted ahead of any kit text in every
> artifact, already refuses a mixed-abi translation unit with its `#error`,
> and within one abi each width has one rendering. pcrec reserves the stem
> `pcrec_mfk_` (and its upper case, `PCREC_MFK_`) in emitted files. The block's
> renderer lands with R17-b, the block's first appearance; main's note on D155
> addendum 4 ("it lands in R17-a") is asked to read so.
>
> **`[rev 2.3]` N6 (pcrec refuses a `-p` prefix inside the kit's stem; r5
> K3-7).** Today `valid_prefix` (`src/core/compile.c:141`) accepts any C
> identifier of at most 60 characters, so `-p pcrec_mfk_x` compiles, and its
> artifact's identifiers `pcrec_mfk_x_search` and macros `PCREC_MFK_X_*` sit
> inside the namespace the kit's shared sub-blocks use. pcrec refuses a prefix
> `P` iff, case-folded, `P` equals `pcrec_mfk` or begins with `pcrec_mfk_`.
> - **The bare `pcrec_mfk` is included on purpose.** Every generated name is
>   `<PREFIX>_<suffix>` (cli.md §1.6¶1), so `-p pcrec_mfk` produces
>   `pcrec_mfk_search` and `PCREC_MFK_<STAMP>` macros, inside the stem, while
>   "begins with `pcrec_mfk_`" would let it through.
> - **Case-folded** because the prefix is also rendered upper-case (the `\x01Q`
>   placeholder) into every `<PREFIX>_` macro, and the guards are upper case:
>   `-p PCREC_MFK_x` is the same collision in the macro namespace.
> - It is a refusal at the same tier as today's "invalid symbol prefix", with
>   its own message (PROPOSED: `symbol prefix 'P' is reserved: the search
>   kit's shared stem is pcrec_mfk_`). D26: the wording is not a contract
>   beyond naming the prefix.
> - It moves no artifact byte (it refuses inputs that compiled before), so it
>   is not an abi event. It is caller-observable, so it carries its spec hunk
>   (D80). Draft for `docs/spec/cli.md` §1.6¶1, appended after "never truncated
>   or mangled.": *"A prefix that, ignoring case, is `pcrec_mfk` or begins with
>   `pcrec_mfk_` is refused: that stem is reserved for the search kit's shared
>   helper definitions, which several artifacts in one translation unit
>   share."* The same sentence goes beside `match_api.md` §8.0¶4's
>   "invalid symbol prefix" contract for `pcrec_options.prefix` (one check
>   serves both surfaces, `compile.c:2132`).
> - **Placement:** a same-commit pcrec edit inside R17-b, if main agrees, so
>   the reservation and the first names in the stem land together. Otherwise
>   main files it as its own pcrec request, landing no later than R17-b. Its
>   sabotage row (the refusal removed) rides whichever commit carries it.

## 15. Reconciling F-R9-7 / opt3 (C3-11)

`docs/dev/opt3_dfa_scan_measurement.md` §4 ("CONTROL 2"): a 7x faster shufti
skip made all three bench subjects SLOWER (+0.4% to +3.9%):
- on English text the candidate-start skip is entered 190,651 times per MiB
  and moves ~0 bytes per entry;
- its vector setup is paid on every entry;
- the crossover is non-candidate runs of about 32 bytes.

integration.md F-R9-7 (and its §R4.9.7 row for the PF byte set, line 2041)
files PF vector forms behind "a cell whose non-candidate runs are long ... with
the dense regime answered".

**Reconciled:**
1. **Same cause, two readings.** opt3's loss and step 2's 300k loss are the
   same per-entry RESTART cost: setup per entry, ~0 bytes skipped. Frank's
   ruling 2 names it, and D161 addendum 2 reads it so.
2. **The stateful form attacks the cause, not the crossover.**
   - An entry INSIDE the cached block costs the interval test, a shift and a
     `ctz`. No setup, no load, and no data-dependent loop-exit branch. opt3's
     190,651 entries per MiB would refill about once per 64 bytes instead of
     once per entry.
   - **What it cannot beat** is the table walk's cost on an entry that skips
     0 bytes: one table load and one well-predicted branch. Where entries skip
     0 bytes AND are predictable, stateful at best TIES, and H5's
     branch-miss columns test whether they are predictable.
   - The adaptive walk mode is exactly today's walk there, so the dense floor
     is today's speed by construction.
3. **The within-call caveat.** Cached state helps re-entries WITHIN a call,
   which is exactly opt3's case: the PF entries before the first accept are
   false candidates in one call. A subject where every candidate is a true
   match crosses a call per hit (`reset=1`), and only cross-call state (§17)
   would help it.
4. **What changes in the filed row.** integration.md:2041's trigger ("non-candidate
   runs ≥ ~32 B ... with the dense regime answered") is answered for the
   SCALAR layer by §13's grid, if H1/H4 hold. The row is updated at R17-b's
   landing: the PF byte set's scalar arm becomes the term rows; its SIMD arms
   keep the filed row's bar (beat the current scalar term rows, per box).

`[rev 2.2]` **Measured (slot2).**
- Item 2 held for the mask: at 300k `reset=inf`, `mask64_swar` executes 5.5
  branches per call against `table`'s 6.7 and mispredicts 0.022 per call
  against 0.038 (64K, perf; the reading's perf table does not report
  `mask8_swar`), and `mask8_swar` reads 0.86 of `table`. H5's branch-miss
  columns show `table`'s entries ARE predictable at 64K 300k (a trough), which
  is the "at best TIES" case; the mask still wins there by not restarting.
- Item 2's last sentence does not survive: the adaptive switch is not built
  (§9.1), so the dense floor is NOT today's speed by construction. It is the
  measured `mask8_swar` row, whose worst corners are §9.2's (a)-(c), bounded
  by about 2x and gated by the bench relay.
- Item 3 is now a number: at `reset=call` (every candidate a true match)
  `mask8_swar` is 1.65 of `table` at 300k against 0.86 at `reset=inf`. That
  gap is [FINDALL-NEXT]'s, per D162 addendum 1.
- Item 4: the integration row is updated at R17-b's landing to name
  `pf_terms_mask` (mask8 at SWAR) as the PF byte set's scalar arm, and
  `mask64_sse2`/`mask64_avx2` as the SIMD arms that must beat it per box.

## 16. Standing design questions

### 16.1 Measurement regime — RELEVANT

- **No number here was measured by this lane.** Every regime this design
  reads is named:
  - step 2's (`reading_slot.md`: dev box 7700X Zen 4, gcc 15.2.0 `-O2 -fPIC`,
    core 14, R 7, MIN_MS 50, i.i.d. placement, findall at 64 KiB/1 MiB,
    percall at 16/64, kit-unofficial);
  - opt3's (bench subjects, search-restart-repeat).
- **The decisions this design makes depend on regime:** the row set and
  order, the fallback gate, K, W, and the adaptive constants.
- **The follow-up names every regime on every row:**
  - findall `reset=inf/16/4/1`;
  - percall, aligned and misaligned;
  - clustered;
  - real subjects;
  - 64 KiB and 1 MiB.
- **The admission rule** is K-1: a form must hold in every regime its sites
  can be in.
- **The dense regime would flip it.** It flipped the r17s leaning, and is why
  the stateful forms exist.
- **The regime this design cannot read on this box:** Zen 1 (ubuntubudu,
  AVX2 at 2×128). The official verdict is the bench's, per box (D144
  addendum 4).
- `[rev 2.2]` **Now measured (slot2), and its regime:** dev box 7700X Zen 4,
  gcc 15.2.0 `-O2 -fPIC`, core 14 with its SMT sibling idle, R 7, MIN_MS 50,
  synthetic i.i.d. and geometric-cluster subjects at 64 KiB (and 1 MiB for
  `reset=inf` findall only), a bare driver loop that rescans one subject. Kit
  tier, unofficial. **The regime that would flip a decision:**
  - the 64K predictor memorization (`table` 0.65 ns/B at 64K against 1.91 at
    1M) makes every 64K dense verdict pessimistic for the forms; a real
    subject with a consumer between calls is somewhere between, which the
    bench relay reads (§11.2a);
  - the state lifetime (`inf` against `k4`/`call`) flips the stateful forms
    from 0.86 to 1.65 at 300k: that is §9.2's call-pattern input, and
    [FINDALL-NEXT]'s case;
  - W flips between 64K and 1M (`mask8_swar` beats `mask64_swar` at 64K and
    loses at 1M, 2.18 at 70k), which is why W is per width and the SWAR
    mask64 row needs stated facts;
  - unmeasured and named: 1M clustered, 1M `reset=k`/`call`, 1M percall,
    DRAM-resident subjects, cold caches, spans other than 16/64, `hi != n`,
    set shapes beyond the 14 cells and 5 synthetic ones, clang, `-O3`,
    `-march`, Zen 1, the Mac (reading_slot2.md §8).

### 16.2 Independent control — RELEVANT

| check | checked against | why it is independent |
|---|---|---|
| T1 (sets) | the blinded author's own expansion and brute-force cover | it shares no source with the kit's deriver |
| T2 (golden pin) | itself | a change detector, by design, not a correctness oracle |
| T4 | `pcrec_cube_of`, pcrec's own analysis | the kit links nothing of `src/` |
| G2 sequences (Q1-Q9) | the byte loop | a second spelling of `F`, not the kit's |
| T5 | the scalar lane predicate | its false-lane population floor is a hand-derived literal |
| §10's round trip | (a self-check by construction) | it refuses rather than declines, and S827 proves G2 catches what it misses |
| G1 | pcrec's timing of the change against its deny | population from a pcrec-side artifact diff, never the kit's `moved` |
| `[r4]` the trace rendering (§12.4a) | the byte loop, recomputed at every cache hit | a second spelling of `F`, inside a rendering default builds never see |
| `[r4 K1-7]` dominance | gcc's `-Wjump-misses-init` | the compiler's flow analysis, not pcrec's placement code |
| `[r4 K1-4]` G-S1/G-S2 | the define's hook text; the emitted function body | the kit compares two statements pcrec made; the C-check reads the artifact, not the emitter |
| `[r4 K1-9]` cache-path reach | gcov execution counts of the movers | dynamic, from the compiled artifact, never a text grep |
| `[r4 K2-8]` the walk-text readers | the deny arm's population, pinned before R17-b | taken from the tree before the change |
| `[r3 C1-2]` the BE arm | the byte loop, through a reversed-load TU | the reversal is the test's, not the kit's |

- **Populations counted (K35):** cache hits, misses, refills, overlapped
  fills and backward-invalid uses (§12.2); LOWEST false flags and the borrow
  danger population (§12.3); the `pcrec_cube_of` population (§3.6).
- **Every sabotage row names its reach** (§12.5).
- The follow-up's check has its planted stale-state control.
- `[rev 2.2]` The shared helper block's identity check is against a
  rendering asked of the kit by KEY only, never read off an artifact (§12.7);
  its presence check reads the artifact's site text, not the kit's report;
  the body-invariance check reads the SIMD-off artifact as the reference and
  is stated vacuous until the SIMD arms exist. The bench relay is the
  admission rule's independent control: the kit chose the rule from its own
  harness, and the bench measures it on subjects and a driver the kit did
  not choose.
- `[rev 2.3]` The sub-block checks are per width, against a rendering asked of
  the kit by width only. The const-input check reads each mover's head, so
  the compiler and the textual C-check are two independent lines for G-S1's
  pointer and G-S2. The bound-vs-live trace trap compares the struct's copy
  with the live variable, which shares no source with the helper. The bench
  gate's F now comes from the bench's own spread or layout-perturbed A/A
  pairs, not from the kit's synthetic band.

### 16.3 What moves when data is regenerated — RELEVANT

- **No data file is born.** The byte-moving constants are kit constants, each
  labelled, and changing any of them is a pcrec abi event in the same commit
  (memfn/CLAUDE.md):
  - K (`UNMEASURED DEFAULT: 3`);
  - BUDGET;
  - W (8 or 64, derived);
  - RING;
  - GAP/BLOCK0/CAP;
  - T_SPARSE (only if §9.2).
- **K and T_SPARSE are MEASURED from §13.** Re-measuring them (a new box, a
  new compiler) can move bytes, so a re-measure that changes either value
  needs the abi ritual and G1.
- **If W6 is filed**, the frequency table is the compile's findings prior
  (D160's authored utf8 prior, or `--analysis`). Regenerating a prior then
  moves R-17 bytes only through the gate's class, which is an abi event of the
  prior's own change and already one under D160.
- **T2's golden pin** moves with the deriver: the pin is the change detector.
- `[rev 2.2]` **After the measurement, the byte-moving constants are:**
  - K = 4, `MEASURED-UNOFFICIAL (slot2)`, read on the sparse regimes (§3.3);
  - BUDGET, `UNMEASURED DEFAULT: 4096` (unchanged);
  - W per width, DERIVED (8 = the SWAR word, 64 = the mask word) and chosen
    per width by slot2;
  - `T_DENSE = 300000` and `B_EVEN = 3`: `MEASURED-UNOFFICIAL (slot2)`, but
    they move NO byte at R17-b, because no input reaches the decline arm
    (§9.2). They become byte-moving when the arm lands;
  - RING and GAP/BLOCK0/CAP leave the list: their forms are not built.
- `[rev 2.2]` **The shared helper block** is generated text keyed by (abi,
  helper-set version). Regenerating it with any byte change is a pcrec abi
  event AND a helper-set version bump in the same commit, and moves every
  artifact that carries it; its readers are found by grep like any abi
  reader. It is caller-visible scaffolding, so a guard or name change also
  carries its spec sentence (§11.3).
- `[rev 2.3, r5 K3-1, K3-8]` **The sub-blocks** are generated text keyed by
  width, under K80's abi. Regenerating any of them with a byte change is a
  pcrec abi event in the same commit (there is no helper-set version to bump)
  and moves exactly the artifacts that carry that width's sub-block: every
  mover for W8, only SIMD-on movers for V16/V32. `T_DENSE` is now labelled
  `MEASURED-BRACKET (70000, 300000]` and `B_EVEN` `UNMEASURED DEFAULT: 3`
  (inside (1, 4)); neither moves a byte at R17-b (§9.2).
- `[rev 2.2]` **The analysis object** moves no R-17 byte at R17-b (§9.2). Once
  the decline arm lands, regenerating a bundle whose byte rates move a set
  across `T_DENSE` moves that site's bytes: an abi event of the bundle's own
  change, as D162 ruling 1 states.

## 17. Unlocks (filed, not built; each with a trigger)

| unlock | what | trigger |
|---|---|---|
| **R-18, the general window request** | W6-W10, FIND over several spans, the reply's span, P5/P6 policies over `mf_set_terms` per position | main's chunk-2 note (the general form; this note's §2 is its degenerate case) |
| **Cross-call state** | the stateful cache lives in the versioned caller struct ([FINDALL-NEXT]/[IFACE-PUSH]) across find-all calls | §13's `reset=1` against `reset=inf` gap is large on a real subject whose candidates are mostly true matches. `[rev 2.2]` The gap is MEASURED: 1.65 against 0.86 for `mask8_swar` at 300k; it is [FINDALL-NEXT]'s (chunk 5) by D162 addendum 1; see the rev 2.2 table below |
| **`state_by_caller`** | the CALLER declares storage and passes it to a site whose uses span calls of a helper function: the hybrid's prefilter function, called per retry. It is `count_by_caller`'s precedent applied to the kit's cache | a hybrid cell whose prefilter re-entry is dense |
| **a `lo`-monotone fact** | pcrec states "lo never decreases between uses" | a form that needs it. None today: the cache test covers both directions in one compare (§7.4) |
| **hoisted per-call constants** | the set's broadcast vectors held in kit-owned locals (gcc rebuilds `set1` per function entry, D155's facts) | a measured broadcast cost at re-entry in a SIMD arm |
| **the exact-lane renderer for SKIP** | first-non-member skip for STAY/EDGE/VMSPAN complements (`[^"]*`) | a measured stay-loop loss with ≤ K exit terms (in-loop spans are short) |
| **COUNT via popcount** of EXACT masks | counted edges | a measured counted-edge loss |
| **a term-based vrun filter position** | KA/KB as a class | a ranked class position with a measured loss |
| **an ofsskip BODY set row** (`offset-set`) | the term renderer at a set offset | pcrec re-prices `prefix_k` (r17s F-1), with ci-moskva as the witness |
| **N4 SETREST over SET terms** | ALL_PRESENT over term lanes | a set-rest cell in a loss table |
| **`$_valid_upto`'s ASCII skip** | the one-range term | R-12's pending listing (Q-R12-5) |
| **a reverse scan (clz)** | REVEND / rev-inner set landmarks | the first rev-inner row with a set landmark |
| **the density fact as a shared fact** | [START-DENSE] and the stay-loop admission read W6 | W6 filed for any consumer |
| **one block mask shared by two sites** | a PF scan and a pre-check over the same subject region in one function | a function with two sites over one region and a measured double scan |

`[r4]` The r4 panel's unlocks, filed (the ones revision 2.1 takes now are
marked):

| unlock | what | trigger / state |
|---|---|---|
| **use-invariance as a field class** | K1-4's `s`/`n` refusal generalized to every multi-use handle, as a `fields.def` class | the second stateful row |
| **a function token on `mf_locals`/`mf_use`** | the host names the function, so the kit can check one-function-per-site and keep state for any site (popcount COUNT) | COUNT is filed, or a site whose state must be checked without a compile (§7.5, K1-5) |
| **a trace-build re-probe of cache hits** | a standing oracle for cached kernels | **TAKEN at its trigger** (the first stateful row): §12.4a |
| **a reverse block cache (`clz`)** | the mask form, mirrored, for MLINE/rev-inner | the first rev-inner set landmark |
| **pre-prologue facts via `mf_result`** | the define reports facts pcrec needs before it writes text | **TAKEN for `reads_table`** (§11.1 item 3, K2-6); a second fact is the next instance |
| **`MF_MOVE_UNBOUNDED` + a fixed origin** | | **TAKEN** (W1, K2-4) |
| **lazy table demand recorded by `table_name`** | the kit records which tables its text named, instead of a per-site report | a second conditional table read |
| **one density carrier** | `freq` (W6), the byte-rate table, is the carrier the other three (`mf_term.ppm_lo/hi`, `mf_site.cand_ppm_lo/hi`, `mf_pred.rank_ppm`) fold into: each is derivable from it plus the site's sets. Folding `rank_ppm` revisits D157's carried array, so it is main's to rule | W6 is filed, or R-18's first density reader |
| **the reply as (window, span) lvalues** | W3 plus W8 as two written lvalues | the first multi-span row |
| **a "uses per activation" host fact** | `activation = MF_ACT_PER_RETRY` on the hybrid's prefilter site (§7.5, K2-11) | a measured stateful-init loss there: §13's `reset=1`/`reset=4` rows |
| **a back-patchable include slot** (revision 2.1's, from K2-6) | an `#include` decided after the define, filled at the prologue's anchor (D143-style) | the first kit row that needs a header it cannot spell as a builtin |

`[rev 2.2]` **The settled directions' unlocks and the measured non-builds**
(each filed, not built):

| unlock / filed note | what | trigger |
|---|---|---|
| **[FINDALL-NEXT] cross-call state** (main's chunk 5) | the `next_candidate` struct lives in the versioned caller struct across find-all calls, so a true match no longer ends the state's life. It turns the `call`/`k4` rows into `reset=inf` rows (`mask8_swar` 1.65 → 0.86 at 300k). The body contract does not change: only where `&state` points | chunk 5's design. The measured bar: the state must survive at least 2-3 candidates (`B_EVEN`) for `mask8_swar` to beat its stateless twin, 8-16 for `mask64_swar` |
| **the stateless-first twin** | a body that tests each word STATELESSLY first (an OR of LOWEST terms, §3.4) and packs and stores the EXACT mask only on a nonzero word. It would keep `swar`'s sparse speed (0.38 of `table` at 0 ppm, where `mask8_swar` is 0.59) and `mask8_swar`'s re-entry. A HYPOTHESIS from slot2's numbers, not measured | written as a twin and timed before it is claimed, when the sparse gap matters: a bench cell where `mask8_swar` loses to the stateless SWAR form beyond the floor, or a kit round with slot time. If it wins, it is a new implementation behind the same `next_candidate` at SWAR, not a new row |
| **AVX-512 width row** | a W = 64 implementation over AVX-512 mask registers, behind the same `next_candidate` and the same body (D155 addendum 4.1; Frank: "avx512 does handle them extremely cleanly") | UNFILED until requested; its verdict is on the targeted hardware (this dev box runs it natively; ubuntubudu does not) |
| **`pf_terms_mask64` at SWAR** | the W = 64 SWAR implementation (the best SIMD-off form at 1M: 0.37 at 300k) | a site that states BOTH: the state survives the whole call (cross-call state above, or a stated call-pattern kind) AND every use's span is at least 64 (a span-length class). Without both it loses 3.98 at `call` and 2.21 at percall L16 |
| **the ring behind `next_candidate`** | §8.3's ring as a width's implementation | a producer that is not one block scan (several sites or spans filling one queue: the decoupling advantage), measured to beat the mask; never on cost alone (slot2: it loses everywhere) |
| **the adaptive switch** | §9.1's two-mode switch over the mask form | a GAP/BLOCK0/CAP sweep that shows it beating the fixed mask beyond the band somewhere it can be; slot2 suggests none |
| **`pf_memchr_set`** | the \|S\| = 1 libc row | a timed \|S\| = 1 cell where `memchr` beats `mask8_swar` (SIMD-off) under the admission rule; slot2 did not time `memchr` |
| **the decline arm of §9.2** | W6 appended, the row's contract gains the decline class | the analysis object carries a byte-rate kind AND a call-pattern or match-density kind, or pcrec states `activation` on the hybrid's prefilter site |
| **the run compare's word loads in the shared block** | `<p>_w<W>` (`runcmp.c`) becomes the block's SWAR `load_vector`, one load spelling per file | the next change to `runcmp.c`'s load helpers (an abi event either way) |
| **primitives for other kit sites** | vrun, ofsskip and the pre-check composite rendered over the same per-width primitives | each site's next form event; the helper-set version bumps with each new primitive. `[rev 2.3]` No version: a new primitive is a byte change of its width's sub-block, an abi event for that width's carriers |

`[rev 2.3]` **The r5 unlocks** (`docs/dev/reviews/2026-10-12-r5-memfn-setfind22.md`),
filed, not built:

| unlock | what | trigger |
|---|---|---|
| **the bound struct as the cross-call state record** | the `<stem>__c` struct, which already binds `s` and `n`, becomes the state record [FINDALL-NEXT] keeps across find-all calls, self-checked at entry (a call whose `s`/`n` differ from the record's starts it fresh) | [FINDALL-NEXT] (main's chunk 5) |
| **the uses-per-activation trace counter `mfk-upa`** | §12.4a: activations and a histogram of uses per activation per stem, in the trace build; gives §9.2's (P) and the bench's Q3 figure with no bench time | the decline arm is coded, or the bench answers Q3 "cannot count it" |
| **a host fact `inputs_const`** | pcrec states that the holding function's `s`/`n` are const-declared (§7.4), so the kit skips its `s`/`n` refusal | the second stateful site kind |
| **per-width sub-blocks for vrun / ofsskip / the run compare** | §3.4b's per-width shape applied to those sites' primitives | the first non-PF site rendered over the primitives |

## R. The panel, by id

All 36 ids. "Changed by ruling" marks a finding whose answer the rulings moved.

| id | sev | where answered | disposition |
|---|---|---|---|
| C1-1 | BLOCKER | §5, §12.2 Q6/Q7, §12.5 S824 | non-wrapping remainder guard; NOP writes nothing; NULL `s` at `n = 0`; S824 re-aimed |
| C1-2 | MUST-FIX | §6 | one constant-folded ternary at the LOAD; `_Static_assert` for PDP; BE compile-checked. `[rev 2.1, r4 residual]` The BE branch is now ANSWER-checked by a byte-swapped LE test (a reversed-load macro plus a flipped `__BYTE_ORDER__` in a `tests/memfn/` TU, through T5 and Q1-Q7); only a real BE target's code generation stays UNREACHED |
| C1-3 | MUST-FIX | §3, §10, §12.1 (T1-T3) | spec + generated set space + loud refusal + golden pin |
| C1-4 | MUST-FIX | §3.2-§3.3 | candidates (prime cubes, arcs), lexicographic objective, IDDFS with labelled BUDGET, purity, determinism |
| C1-5 | SHOULD | §4.3 | new row `pf_memchr_set` with its own store form and deny |
| C1-6 | MUST-FIX | §7.6, §12.5 S837 | stem-derived names (pcrec's `fn_ref`), reserved `<stem>__*`; IDENT hooks; shadow-hook G2 set. **Changed by ruling 3/main's question:** handle-derived names replaced by pcrec stems (stable under renumbering) |
| C1-7 | SHOULD | §4.2 | serves stated: NOP/EXCLUDED, AT_N and MISS decline, offset 0 only, floor unstated, no on_miss, miss = range end |
| C1-8 | SHOULD | §3.1, §3.4 | EXACT/LOWEST tag; wide ranges 129-255 as the complement of a modular ARC; \|S\| 0/256 declines explicit |
| C1-9 | SHOULD | §12.3 (T5) | full kernel test with adjacent-lane pairs and K35 false-lane and danger floors |
| C1-10 | SHOULD | §12.1, §13.1 (`x80`, syn cells), §13.2 PLANT | 0x80-crossing range, K ≥ 4, per-form plants |
| C1-11 | SHOULD | §12.4 | guard page / ASan / UBSan on kit-rendered text; the SAN-1 battery covers R17-b's movers |
| C1-12 | SHOULD | §12.5 | S823 → SIMD family (UNREACHED until §11.4); S824 re-aimed; reach column on every row; 18 more ids requested (`[rev 2.1]` allocated as S826-S843) |
| C1-13 | SHOULD | §11.1 item 4, §14 N4, S841 | the door assertion |
| C1-14 | NIT | §4.3, §6 | `unsigned long long` and `__builtin_ctzll`/`__builtin_memcpy`: no `<stdint.h>`/`<string.h>` dependency in the terms rows; `d` bound once inside the helper (a local, not repeated text) |
| C2-1 | MUST-FIX | §13.1, §13.4 H5 | intermediate grid + branch-miss counters; cause owed to the run |
| C2-2 | MUST-FIX | §13.1 | clustered placement + real subjects with measured ppm/run profile |
| C2-3 | MUST-FIX | §13.1 | 300k/800k at 1 MiB, dense percall, > 800k, misaligned `lo` |
| C2-4 | MUST-FIX | §3.3, §13.1 | 4/5/6/8-term cells; K = `UNMEASURED DEFAULT: 3` until then |
| C2-5 | SHOULD | §13.4 | the noise band computed and applied |
| C2-6 | SHOULD | §13.4 | raw and `d_floor` both; verdict basis raw, disagreements named |
| C2-7 | SHOULD | §13.4 | per-cell losing set |
| C2-8 | NIT | §13.4 | memchr at 800k per cell |
| C3-1 | MUST-FIX | §11 | one routing event: zero-mover seam (R17-a), one SIMD-off byte move (R17-b), SIMD arms at zero SIMD-off movers (§11.4). **Changed by ruling 3:** helpers or composable pieces both allowed; no selector-only constraint |
| C3-2 | MUST-FIX | §11.1 item 3, §14 N3a | `[rev 2.1, r4 K2-6]` `mf_plan` is DROPPED (it duplicated selection). The R-17 rows are header-free (`__builtin_memcpy`, `__builtin_memchr`), so the prologue's prediction of the kit's calls stays exactly right unchanged, and `pcrec_memfn_art_end`'s existing assertion is the control. The prologue precedes every define on both routes, which is why a header could not be decided at define; the back-patchable slot is filed (§17) |
| C3-3 | MUST-FIX | §11.1, §11.3, §12.5 S840 | table emitted iff `reads_table`; spec method-blind; stamps' values kept |
| C3-4 | MUST-FIX | §4.3 | new row; its own compound statement (no reliance on pcrec's brace); a statement-expression is unneeded for STMT |
| C3-5 | SHOULD | §9.2 | the density field with `D_ABSENT` declining. **Changed by ruling 2:** a FALLBACK only, rendered only if the stateful/adaptive forms lose dense |
| C3-6 | SHOULD | §11.1 item 2, §4.3, §14 N2 | **Changed by ruling 3.** `[rev 2.1, r4 K1-1, K2-1]` Revision 2's row was WRONG: it relied on a file-scope buffer at `cand_emit_table` (the tables are function-local) and on the pending-helper flush (word loads only, and run before `_run` is written), and its "term rows do not read `start_set`" was false for adapt, whose file-scope helper named the VM hat's function-local table and would not compile. Re-derived: N2 is two define points with precedents (a new `u.pf.emit_block` on the DFA set rows; the VM hat beside `pcrec_emit_req_run_blocks`), each writing its helper into the file stream there; no flush change; and NO table moves to file scope for ANY row, because a helper that reads pcrec's table takes it as a parameter named at each use (`<p>_ofsskip`'s precedent) |
| C3-7 | SHOULD | §7.5, §11.1 | one site, defined once, `mf_locals` once, two uses sharing one cache (the stateful win itself) |
| C3-8 | SHOULD | §6 | find-first order through the load normalization. `[rev 2.1, r4 K2-10]` DECIDED now, not deferred: the load is `__builtin_memcpy`; C4 needs NO change, because `memfn/` and `tests/memfn/` are exempt from C4's scan by design and the tokens appear only there |
| C3-9 | SHOULD | §12.6, §12.1 | the checklist; the blinded G2 family |
| C3-10 | SHOULD | §3.3, §11.2 | K from a measured boundary, labelled until then; `pffind.c` header rewritten at R17-b. `[rev 2.1, r4 K2-10]` K's derivation path is stated (§3.3): the real and `syn4`-`syn8` cells → `summarize_r2.py`'s per-cell verdict under the band → the largest k with no loss in any regime → a `MEASURED-UNOFFICIAL` label in `terms.c`, with G1 and the abi ritual in the same commit |
| C3-11 | SHOULD | §15 | reconciled; integration.md:2041 updated at landing |
| C3-12 | SHOULD | §14 N3c | deferred to R-18 (the uniform description goes with the stamp question); R-17 keeps pcrec's PF row split |
| C3-13 | NIT | §1.3 | the report's stale facts corrected here; the request text is main's |
| C3-14 | NIT | §3.6 (T4) | the corpus cross-check against `pcrec_cube_of`, with a counted population |

36 of 36: C1 14, C2 8, C3 14.

## R4. The r4 light re-check, by id (revision 2.1)

`docs/dev/reviews/2026-10-12-r4-memfn-setfind.md`: 24 ids, r3's C1-2
residual and the sabotage renumbering. Each disposition was checked against
the code it cites before it was written in. "Applied" means as dispositioned;
"CORRECTED" means the code showed the disposition (or the revision 2 text it
fixes) wrong in a way the disposition did not cover, and the cell says what
was done instead and why. The r4 review cites revision 2's sabotage numbers;
the new number follows in brackets.

| id | sev | where answered | verdict |
|---|---|---|---|
| K1-1 | MUST-FIX | §4.3 (`pf_terms_adapt`), §9.1, §R C3-6 | Applied. Verified: `emit_u8_table` writes every table inside the function (`emit_dfa.c:3446`), and the VM hat's `start_set` is one (`:7215`). T is a helper PARAMETER, named at each use by `table_name`, on `<p>_ofsskip`'s precedent (`ofsskip.c` `table_params`). §R C3-6 corrected |
| K1-2 | MUST-FIX | §8.2, §12.5 S834 (rev 2 S833) | Applied. Verified the equivalence: at end_back 1 the only extra cached byte is `n - 1 = hi`, and a member there answers `hi`, the miss answer. The replacement plant is the end_back-0 overlapped block at `hi - 63`, caught by the guard page, ASan and the trace rendering's `top <= hi` trap, not by answers |
| K1-3 | MUST-FIX | §12.2 Q9, §12.5 S832 (S831) | Applied. Q9 also at `-O0`, with a period-3 word fill (`0`, `2^31`, `~0`) at all three phases, so the garbage satisfies `base <= lo < top`; plus the C-check that `mf_locals` initializes every scalar the helper reads. S832's detector is that pair. The harness is unchanged (§13.3: its twins reset state per sequence) |
| K1-4 | SHOULD | §4.2, §7.4, §12.4a | Applied, NARROWED: `mf_use` compares the `s`/`n` hook text with the define's. "or end_back" cannot be compared at a use, because `end_back` is a field of the site, fixed at define, which no use restates (memfn.h `mf_use` takes hooks only); it is invariant by construction. Plus the C-check that `s`/`n` are not assigned after the storage point, and the trace re-probe with `top <= hi` |
| K1-5 | SHOULD | §7.5, §17 | **CORRECTED.** The finding holds (revision 2's "refused at `mf_use`" was unenforceable), but the disposition's fix cannot work: pcrec builds a fresh stack `PcrecMfSink` per kit call (`memfn_sites.c:357,371,379`), and every function writes into the one `job->csb`, so no sink pointer separates two functions. Instead: a use in a function without the storage is an undeclared-identifier compile error, and storage in two functions is refused as placed twice (K2-9). The function token stays an unlock |
| K1-6 | SHOULD | §7.1, §11.1 (the order) | Applied for the DFA (the point keyed on the forward PF site, in `unanch_scan`, with K2-9). **CORRECTED for the VM half**: the order define → locals → table-if-read → use holds, but the define cannot sit "inside the entry emitter", because its helper must precede `<searchfn>_run` and the prologue (`emit_vm.c:14000`) has already been written before `vm_emit_search_body` (`:14009`). The VM hat is defined at file scope beside `pcrec_emit_req_run_blocks` (`:13130`), above `_run`; locals, table and the entry use stay at the entry |
| K1-7 | SHOULD | §7.2 | Applied. `-Wjump-misses-init` over the R17-b movers, filtered to `<stem>__`. Its limit is stated: gcc does not analyze computed `goto`, and neither holding body emits one (the DFA bodies' jumps are direct scan-loop gotos, which it analyzes; the computed `goto *targets` is ENG_ATTEMPT's, which holds no storage site) |
| K1-8 | SHOULD | §4.3 (ring), §7.1 | Applied. The ring witness at `-O2`/`-O3` in test-codegen; "placed, never read" refused at `mf_art_end` |
| K1-9 | SHOULD | §12.5 (the reach paragraph) | Applied. Dynamic reach by gcov execution counts of the cache-hit line, floor the literal 1 per witness, for S830-S834 and S842 (rev 2's S829-S833, S841) |
| K1-10 | NIT | §3.2, §3.3, §12.1 (b) | Applied, both halves: the claim is restated (exhaustive over CANDIDATE covers; objectives 2-4 rank candidate covers only), the pseudocode searches `S` and `¬S` at every k, AND the candidate rule gains sub-terms (every 128-long arc of a longer run), which makes objective 1 exact over all covers by a stated dominance argument. G2's oracle (b) re-derives the term space from the definitions |
| K1-11 | NIT | §7.6 | Applied. The stem is opaque, written only through `puts`/`vprintf` (never an escaper, `internal.h`'s "one seam"); a placeholder stem in G2's shadow set; a C-check that pcrec writes no `<stem>__` identifier |
| K1-12 | NIT | — | Superseded: `mf_plan` is retired (K2-6) |
| K2-1 | MUST-FIX | §11.1 item 2, §14 N2, §R C3-6 | Applied for the DFA: a new `u.pf.emit_block` on the set rows (`ofs_site_define`'s precedent, `emit_dfa.c:6757`), table emission from the define's report. **The flush half is CORRECTED to "no change"**: both routes define at a file-scope point above the function and the kit writes the helper there, so `mf_flush_helpers` stays word-loads-only (`runcmp.c:466`). Revision 2's flush claim was also wrong on ORDER (the prologue precedes `_run`), which the review did not name |
| K2-2 | MUST-FIX | §0 item 1, §2.1, §2.2 W3 | Applied. "Move once" restated for the PF sites only; W3 is NOT extended to the `ret_pred` reply (not justified: no R-17 row reads it, and it moves pcrec's text after the site); "R-18 needs no re-routing" is withdrawn for the handoff and the offset-skip FUNC |
| K2-3 | SHOULD | §0 item 1, §2.2 | Applied. Routing-once, not bytes-once; W6 lands with R-17 only if §13 puts §9.2's gate in force, otherwise R-17's reading set stays closed |
| K2-4 | SHOULD | §2.1, §2.2 (W0-W3), §4.2, §11.1 | Applied. D161's origin (the span's beginning), which makes W1 SIGNED (MLINE states -1; revision 2's unsigned field could not hold it under that origin); `MF_MOVE_UNBOUNDED` reserved; a non-wrapping W3 keyed on `back = move_back - d_min`; `window_stated` (W0) makes statedness checkable, refused unstated on FIND and stated on non-FIND or reverse sites |
| K2-5 | SHOULD | §2.2 W4, §7.1, §9.2, §14, §17 | Applied. `decl_point`, a host capability; `needs_locals` dropped with `mf_plan`; §14's glosses stripped; `freq` named as the one density carrier (an unlock; folding `rank_ppm` is main's to rule, D157) |
| K2-6 | SHOULD | §11.1 item 3, §14 N3, §17 | Applied for `reads_table` (the define reports it; `mf_defined`). **The include half is CORRECTED**: the prologue precedes the define on BOTH routes (`emit_dfa.c:13459`; `emit_vm.c:14000` vs `:14009`), so the review's "the VM needs no prediction" holds for the table only. Instead of building the back-patchable slot, the R-17 rows are made header-free (`__builtin_memchr`, `__builtin_memcpy`), so no include is needed and the existing `art_end` assertion is the control; the slot is filed with a trigger |
| K2-7 | SHOULD | §11.1 control, §12.6 | Applied. The [SABANCHOR] exact-count gate and a derived re-aim list (an edit set joined against every row's anchor) in R17-a; S478 named (its anchor is `pf_vm_emit_first_class`'s set-building line, `emit_dfa.c:7209`) |
| K2-8 | MUST-FIX | §12.6 (the readers table) | Applied. Each named reader verified at its line and given a fate, both arms, and a floor pinned before R17-b. `run_offset_skip.sh` §2c is recorded as UNCHANGED (the offset-skip sites do not move). The numbers are OWED to the R17-b census |
| K2-9 | SHOULD | §7.1, §7.6 | Applied. The DFA point is in the forward-loop caller (`unanch_scan`); the stem is derived from the holding function, which gives the relocate its own; "placed twice" refused |
| K2-10 | SHOULD | §R C3-6/C3-8/C3-10/C3-2, §3.3, §6 | Applied. C3-6 re-derived; C3-8 decided now (`__builtin_memcpy`; C4 unchanged, its scan exempts `memfn/` and `tests/memfn/`); C3-10's K path stated |
| K2-11 | SHOULD | §7.5, §17 | Applied. The hybrid's prefilter function is entered once per VM re-seed; the storage rows are admitted there only if §13's `reset=1`/`reset=4` rows show no loss, else a host fact (`activation`, the r4 unlock) makes them decline. The dense reliance is stated: without storage that site keeps today's walk under K-1 |
| K2-12 | NIT | §1.3, §2.2 W5 | Applied. `pf_open` is `emit_dfa.c:6228`; `fields.def`'s `fn_ref` doc gains the STMT reading at landing |
| r3 C1-2 | (partial) | §6, §R C1-2 | Applied. A byte-swapped LE answer test (a reversed-load macro over `__builtin_memcpy` plus a flipped `__BYTE_ORDER__` in a `tests/memfn/` TU, through T5 and Q1-Q7). A real BE target stays UNREACHED |
| §12.5 ids | — | §12.5 and every citing section | Applied. S825-S842 → S826-S843 (main's allocation, `ef3fa88b`), by one throughout; five refusal rows added with ids still to request |

All 24 r4 ids are answered: K1 12 (K1-5 corrected; K1-6 corrected in its VM
half; K1-12 superseded), K2 12 (K2-1 and K2-6 corrected in one half each);
plus r3's C1-2 residual and the renumbering.

## R5. Revision 2.2, by settled direction and by slot2 answer

Every direction is SETTLED (§1.1 items 5-8). "Where it lands" names the
sections revision 2.2 changed; nothing that is still true was removed, and
superseded text is kept and marked `[rev 2.2]` where it stands.

### R5.1 The settled directions

| # | direction | source | where it lands |
|---|---|---|---|
| 1 | R-17 is the degenerate one-span window search; §2's mapping and fields stay, PROPOSED for main's chunk-2 note | D161 addendum 3 | §2 (unchanged, W6 row updated), §0 item 1 |
| 2a | body code is readable text over per-WIDTH primitives (vector type, `load_vector`, eq/cube/range masks, `first_lane`) | D155 addendum 3 + 4 | §3.4a (the vocabulary, plus `vor`/`lane_mask`), §4.3, §8.1 |
| 2b | one guarded shared helper block per file, keyed to abi + helper-set version (K80) | D155 addendum 4 | §3.4a (bytes a function of the key only), §12.7, §16.3 |
| 2c | the block is emitted only when a site uses a primitive: absent at R17-a (zero-mover), first in R17-b's abi event | D155 addendum 4, manager note | §0 item 5, §3.4a, §11 (shape table), §11.1 additions |
| 2d | endianness inside `load_vector`; the body always counts trailing zeros; C1-2 closed by construction | D155 addendum 4 | §6 (head), §3.4a, §12.5 S836, §12.7 |
| 2e | helper names carry the reserved kit stem | D155 addendum 4 | §3.4a (`pcrec_mfk_`, PROPOSED), §14 N5 |
| 3 | the stateful contract is `next_candidate(&state, lo)`; the implementation is per width, chosen by measurement; the body never changes | D155 addendum 4.1 | §0 item 2, §4.3 (body text), §5, §8.1, §8.2, §11.4, §12.7 (body invariance) |
| 4a | SWAR `mask8_swar`, SSE2 `mask64_sse2`, AVX2 `mask64_avx2` | reading_slot2.md answer 7 | §4.1, §4.3, §8.1, §11.2, §11.4 |
| 4b | the ring and the adaptive switch NOT built, reasons recorded, kept as filed notes | answers 3, 4 | §4.1, §8.3, §9.1, §17 |
| 4c | `mask64_swar` only where state survives the whole call AND spans ≥ 64; otherwise out | answer 7 | §4.1, §4.3 (`pf_terms_mask64`, not built), §17 |
| 4d | K = 4 for the SIMD-off forms, with how it was read | answer 5 | §3.3, §1.3, §12.6, §16.3 |
| 4e | mask64i == mask64: the composable-pieces shape costs nothing measurable | answers 1, 7 | §4.3 |
| 4f | the "stateless test first, pack only on a nonzero word" hypothesis, filed as an unbuilt twin with a trigger | answer 7 | §3.4, §17 |
| 4g | AVX-512 as an unfiled later width row behind the same interface | D155 addendum 4.1 | §11.4, §17 |
| 5a | workload data is ONE analysis object (W6, N1) | D162 | §2.2 W6, §14 N1 |
| 5b | every selection is TOTAL without data | D162 ruling 2 | §9.2 (the class table) |
| 5c | ADMIT when density is absent; decline only on positive density ≥ ~300k with a state-losing call pattern; rev 2.1's `D_ABSENT`-declines rule reversed; thresholds labelled per D149 with their source | D162 addendum 1 | §9.2 (rewritten), §4.2, §7.5, §12.5 S839 |
| 5d | the state-lost dense residual is [FINDALL-NEXT]'s, break-even 2-3 candidates per state lifetime for `mask8_swar` | D162 addendum 1, answer 2 | §9.2, §15, §17 |
| 6 | a bench relay on real subjects GATES R17-b; a real cell losing beyond the regression floor returns to the kit; drafted self-contained; the 64K predictor caveat | D162 addendum 1, D144 addendum 4 | §11.2a, `setfind_bench_request.md`, §14 (THE GATE) |

### R5.2 The slot2 answers

| answer (reading_slot2.md) | finding | where it lands |
|---|---|---|
| the 64K artifact | `table` 0.65 ns/B at 64K against 1.91 at 1M; H5 falsified at 64K | §9.2 (pessimistic end), §11.2a, §13.5, §16.1, the bench draft's §5 |
| 1, the verdict question | YES at `reset=inf` by layer (`mask8_swar` 0.86, the SIMD masks 0.88-0.90 at 300k); NO form passes K-1 over all rows | §13.5, §9.2 |
| 1, D147 | `mask64_avx2` loses to the best SIMD-off form on 51 rows, all 64K ≥ 300k (worst 1.28); `mask64_sse2` on 70 + 6 | §11.4 |
| 2, the reset axis | state helps only with re-entry; `call` costs the refill (+2.0 ns `mask8_swar`, +8.5 `mask64_swar`); break-even 2-3 / 8-16 candidates | §9.2 (`B_EVEN`), §7.5, §17 |
| 3, mask vs ring | the ring loses everywhere; twice the branches, from drain work | §8.3, §4.1 |
| 3, mask W | `mask8_swar` wins 64K, resets and percall; loses at 1M | §8.1, §16.1, §4.3 (`mask64` SWAR) |
| 4, the adaptive switch | does not pay (4-9 wins, 393-447 losses of 574) | §9.1, §4.1 |
| 5, K | K = 4 sparse; no K wins dense percall; the syn8 anomaly owed to disassembly | §3.3, §13.5 |
| 6, percall | `mask64_swar` 2.21 at L16 (the `hi < 64` tail path); dense percall is `table`'s | §4.1, §9.2 corner (b) |
| 7, per-width recommendation and residuals | the three forms; corners (a)-(c); what the kit lacks per corner | §4.1, §9.2, §17 |
| 7, the fallback gate | ADMIT when absent (ruled) | §9.2 |
| 8, regimes not measured | real subjects, 1M beyond `inf`, cold caches, other spans/shapes/compilers/boxes | §16.1, §13.5 (OWED), the bench draft |

### R5.3 What revision 2.2 adds beyond the brief, stated so it can be refused

- **`vor` and `lane_mask`** join D155 addendum 4's primitive list: two
  connectives the measured forms need to OR terms and pack once (§3.4a).
- **The block's bytes depend only on its key** (it holds every width of its
  helper set), because "first block wins" is otherwise wrong in a mixed-layer
  file (§3.4a).
- **The struct binds `s` and `n`** so the body passes only `lo`; its cost is
  owed to the disassembly check, with a stated fallback contract (§4.3).
- **Three sabotage ids are reassigned** rather than left unused, and seven
  more are requested (§12.5).
- **A proposed numeric regression floor** for the bench relay
  (`setfind_bench_request.md` §4), for main and the bench to confirm.

## R6. The r5 light re-check, by id (revision 2.3)

`docs/dev/reviews/2026-10-12-r5-memfn-setfind22.md`: critic K3, 11 ids, no
blocker. Each disposition was checked against the code it cites before it was
written in. "Applied" means as dispositioned. "REFINED" means the code showed
the disposition's literal text short of its own intent, and the cell says what
was done instead and why.

| id | sev | where answered | verdict |
|---|---|---|---|
| K3-1 | MUST-FIX | §3.4b (new), §0 item 5, §3.4a (two bullets superseded), §11.4, §12.5 (S836, S838, S842, S843), §12.7, §14 N5, §16.3 | Applied. One sub-block per width (W8 / V16 / V32), each under its own guard and emitted only where a site uses that width; first-wins holds per sub-block. A SIMD-off artifact holds **W8 only**, which has no `#if` and no SIMD text, so the SIMD arms add V16/V32 sub-blocks and definitions to SIMD-on artifacts only: zero SIMD-off movers by construction. Verified the finding's premise: x86-64's baseline defines `__SSE2__`, so revision 2.2's guarded SSE2 primitives were live text in every default x86-64 SIMD-off build. V16/V32 are header-free (vector extensions, `__builtin_ia32_*`), so the include question is the arms', not R17-b's |
| K3-2 | MUST-FIX | §4.2, §4.3 (new bullet), §5, §7.4, §8.2, §12.4a, §12.5 (S824, S851, one new row), §12.7 | Applied. The body guard reads `<stem>__c.n`; the use pastes only `lo`. The trace form of each use traps unless `<stem>__c.n == n && <stem>__c.s == s`, which compares the bound copy with the live variable and restores r4 K1-4 (its re-probe alone compared the helper with itself). With K3-3 the trap is a second line: the corpus reaches its site and cannot fire it, so its control is a non-const G2 fixture |
| K3-3 | SHOULD | §7.4, §11.2, §12.5 (S852), §12.7 | Applied. Verified: the holding functions take the subject as parameters (`emit_dfa.c:1806`, `emit_search_head`, shared by the DFA body and the hybrid's static prefilter; `emit_vm.c:13137`, `_run`); no emitted string writes `subject` or `subject_length` (grep over `src/gen/`; the H3 end-window sites write `window_end`, `emit_vm.c:13311-13312`, `:13444-13448`); a const-qualified parameter in a definition leaves the type unchanged (C11 6.7.6.3¶15); the precedent exists (`emit_vm.c:12786-12787`). Part of R17-b's abi event, on R17-b's movers only. The textual C-check is the fallback and a second line |
| K3-4 | SHOULD | §7.5 (withdrawal), §9.2 ((P) restated), §12.4a (`mfk-upa`), §12.5 (S839), §14, §17, the bench draft §2/§5/Q3, the corrigendum | Applied. (P) = uses per activation below `B_EVEN`, statistic the median activation (PROPOSED). `activation = MF_ACT_PER_RETRY` is a proxy and no longer completes (P). The trace counter is named `mfk-upa` (activations and a 0/1/2/3/4+ histogram per stem), filed with the r5 unlock's trigger. "State-losing by construction" is dropped from the bench draft and withdrawn in the corrigendum |
| K3-5 | MUST-FIX | the bench draft §4, §11.2a, §14, the corrigendum | Applied: reproduce-on-rerun for a LOSS; F from the bench's standing per-cell spread (Q6), else the largest of at least three A/A pairs; the A/A pair layout-perturbed (a different `-falign-functions`, or a padded build); the absolute criterion on every cell. The kit's synthetic 0.05 floor is withdrawn from the formula (it was the kit's own band, the r5 finding's "synthetic-tier") |
| K3-6 | SHOULD | §9.2 (labels; (D) and the degenerate interval), §16.3 | Applied. `T_DENSE`: `MEASURED-BRACKET (70000, 300000]`; `B_EVEN`: `UNMEASURED DEFAULT: 3`, an interpolation inside the measured bracket (1, 4) (slot2 timed lifetimes 1, 4, 16, ∞ only); a point-estimate rate reads as `[r, r]`; (D) is corpus evidence, not subject evidence |
| K3-7 | SHOULD | §14 N6 (draft cli.md / match_api.md hunk), §11.2, §11.3, §12.5 (one new row) | **REFINED.** Verified the finding: `valid_prefix` (`compile.c:141`) accepts `pcrec_mfk…`. The disposition's rule ("prefixes beginning `pcrec_mfk_`, case-folded") misses the bare prefix `pcrec_mfk`: every generated name is `<PREFIX>_<suffix>` (cli.md §1.6¶1), so `-p pcrec_mfk` yields `pcrec_mfk_search` and `PCREC_MFK_*` macros inside the stem. N6 refuses `P` iff fold(`P`) is `pcrec_mfk` or begins `pcrec_mfk_`. Proposed as a same-commit pcrec edit inside R17-b if main agrees, else a separate pcrec request landing no later than R17-b. Not an abi event; D80 hunk drafted |
| K3-8 | NIT | §3.4b (the key), §11.2, §12.5 (S838), §12.7 (the key row withdrawn), §14 N5, §16.3 | **Picked: the version is DROPPED, and so is any value in the kit's guards; the key is K80's guard.** The disposition offered "specify the encoding, or drop the version from the key", presuming an abi-valued kit guard. The code shows the kit cannot see pcrec's abi (`memfn.h` has only `MF_SITE_ABI`; `mf_art` carries no `PCREC_ARTIFACT_ABI`, `emit_dfa.c:54`), and that K80's valued guard with its `#error` precedes every kit text in every artifact (`emit_dfa.c:13027`, `:3417`), so any mixed-abi TU already fails, whatever the sub-blocks' order. S838 is re-aimed (its rev 2.2 plant is now the design) to "all widths share one guard", UNREACHED until the arms |
| K3-9 | NIT | §4.2, §4.3, §8.2, §11.1, §12.7 | Applied with K3-2: `mf_locals` binds (renders the define's `s`/`n` and refuses differing `at` texts, the one comparison); `mf_use` checks neither (it pastes neither). The rev 2.2 sentences that put a refusal at `mf_use` are marked withdrawn where they stand |
| K3-10 | NIT | §11.1 (decided), §11.2, §14 N5 | Applied. The renderer lands with R17-b; recorded as a reconciliation with main's note on D155 addendum 4 ("it lands in R17-a"), which the kit cannot edit: main is asked to annotate it |
| K3-11 | NIT | §7.6 | Applied. Byte equality on UNRENDERED text: equal before rendering implies equal after, so an acceptance is right and the only possible error is a false refusal (loud). Today's `s`/`n` hook texts hold no placeholder |

**Sabotage ids.** Main's S846-S852 are assigned (§12.5): S846-S849 to R17-a's
four refusal rows, S850-S852 to R17-b. Two more are needed for R17-b (the
trace trap; the N6 refusal) and two at the SIMD arms (body invariance; the
W = 64 pack), the latter asked with the arms.

All 11 r5 ids are answered: 9 applied, 2 refined (K3-7, K3-8). None reopens a
settled direction.
