# The M4 ENGINE design — the backtracking VM as emitted specialized C

> ## PANEL OUTCOME (R21) — READ BEFORE ANY SECTION BELOW
>
> A three-critic panel (R21, `docs/dev/reviews/2026-08-14-r21-m4-design.md`)
> reviewed this document alongside `match_api_m4.md`. Dispositions ratified
> in `docs/dev/decisions.md` D44. Headline: **E-1, a live shipped DFA
> priority miscompile** (K17, `../dev/known_issues.md`), was found by
> running this document's own P-1 probe — the empty-iteration guard
> §3.3 designs is correct, but the priority CONSTRUCTION it feeds has a
> reachable bug in an unrelated shipped path, scheduled as a fix-now code
> lane before [M4.4]. Every FIX-NOW and RULE disposition touching this
> document is applied in place, marked **RULED (D44)**/**(R21)**: §3.3's
> empty-iteration guard narrows to `rmax == -1` only (E-2, MEASURED
> 0/225,240 vs the prior 60/225,240); §6.1's STRUCTURAL mark splits —
> the erasure half held under attack, the semantic half drops to
> BELIEVED-WITH-GATE citing K17 as the live counterexample; §3.7's
> internal differential becomes a GATE running `--engine=vm` with the
> prefilter off; §3.6/§12 ASK-1 re-scopes to a three-way pcrec/python/
> pcre2 comparison with NO pre-built exclusion mechanism, since the
> planned one would have hidden K17; §2.4/§2.5's cursor discipline is
> written out explicitly and extended (D44.1) to deterministic
> capture-bearing bodies, with the residual unbounded class carrying a
> stamped ceiling; §4.2 charges one step per island ENTRY; §5.7.3/§9.2
> add the `--engine=dfa` × captures-default refusal (E-7/D44.6); §8.4(i)'s
> case-(f) numbers are corrected (768 states / 3 classes, not 512/2).
> Superseded text is struck/annotated in place per house style, not
> silently rewritten.

STATUS: **PROPOSED** ([M4.2], 2026-08-14). Nothing here is built and nothing
here is ruled. The [M4.3] D6 adversarial panel reviews this document together
with `match_api_m4.md`, `design_callout_abi.md` and `subst_template_design.md`
before any implementation substep opens; the panel-outcome block lands at the
top of this file when it reports.

This document is written to be attacked. Every load-bearing claim is marked,
every number that does not yet exist is named as a measurement someone must
take, and §13 collects the falsifiable predictions so a critic can go straight
to them.

---

## 0. How to read this

### 0.1 Claim marking (house style)

- **MEASURED** — a number or behaviour taken from an instrument, with its
  source cited. If the source is not cited it is not MEASURED.
- **RULED** — settled by a D-number in `../dev/decisions.md`, or by a plan-row
  ruling of Frank's. Consumed here, not re-litigated.
- **BELIEVED** — the author's reasoning, unmeasured. Every BELIEVED claim in a
  load-bearing position is repeated in §13 with the experiment that would
  refute it.
- **STRUCTURAL** — true by inspection of code that exists today, with the file
  cited. Weaker than MEASURED (no instrument ran) but stronger than BELIEVED
  (no inference chain).

### 0.2 The design, in brief

1. There is no interpreter. The "VM" is a compilation strategy: one C function
   per pattern, straight-line specialized code, one label per pattern position.
2. Backtracking is an explicit fixed-size array plus a capture TRAIL, never C
   recursion. One cold label (`L_fail`) pops and jumps; that indirect jump is
   the only computed goto in the VM.
3. A "step" is one backtrack resumption. It is counted at exactly one place —
   `L_fail` — so forward progress costs nothing and the DD-2 counter is free
   on the path that matters.
4. Allocation-freedom forces a SECOND bound nobody has written down yet: the
   resume stack has a fixed capacity, and overflow needs its own honest
   failure. §4.5.
5. Capture writes are trailed; a resume frame carries a trail mark; popping
   rewinds. One mechanism covers captures, repeat counters and empty-loop
   guards.
6. Leftmost-first is "first complete match wins", not "compare candidates".
   The VM returns on first accept.
7. Capture-free patterns are untouched. Same NFA, same DFA, same emitter, same
   bytes. Zero regression is achieved by not running.
8. For a capture-ONLY pattern the capture-erased DFA is not an approximation —
   it is the SAME MACHINE the compiler builds today (§6.1, STRUCTURAL). So the
   existing forward+reverse pair hands the VM an EXACT anchored window and the
   VM never scans the subject.
9. That is not an optimization, it is a cliff guard: bench case (e) is
   25.4 GB/s on pcrec today and DNF>90s on pcre2-interp. Adding two
   parentheses must not move pcrec onto the DNF side. §6.2.
10. Engine selection becomes a pass with a registered-analysis socket that
    returns a verdict AND, optionally, an enabling REWRITE — run to fixpoint.
    The backrefs-finite and atomic-cut analyses are rewrites, not verdicts.
11. Selection is reported by stamping the artifact (D37's precedent), not by a
    new CLI surface. §5.5.
12. `match_api_m4.md` §13 ASK 4 is ANSWERED: the capture-slot count is a
    property of the ARTIFACT, so a DFA-compiled artifact emits `RX_NCAPS 1`
    and C6 never bends. `RX_NCAPS > 1` implies the VM — one checkable line.
    §5.7.
13. DD-9 (case (f)) is DECIDED: **not the hybrid, and it cannot be.** §8.
14. SR-8's flip is SMALLER than its row implies: zero currently-refused
    constructs become compilable when the VM exists. §9.
15. Three tensions with the ruled D38/D39 ABI are reported, not resolved. §11.

### 0.3 Namespaces and spellings

This document consumes `match_api_m4.md`'s naming decisions rather than
restating them, and every identifier below falls in one of three families
(`match_api_m4.md` §0 and §7):

| family | examples used here | scoped by `--prefix`? |
|---|---|---|
| ABI types, deliberately FIXED literal names | `rx_ctx`, `rx_matchfn`, `rx_callout_ref`, **`rx_info`, `rx_group_entry`** (RULED D44, ratifying R21 C-6 — this row was missing them; `match_api_m4.md` §5's D44.5 hardened layout and D44.3's `slot` column apply to both) | **no** — `match_api_m4.md` §12.7, RULED (D41.1, 2026-08-14); `rx_info`/`rx_group_entry` per D43.1/D44 |
| per-artifact emitted symbols | `<prefix>_match` (§12.6 there), `<prefix>_search` (RESHAPED, D44.2 — see `match_api_m4.md` §1.0), `<prefix>_info`, and everything this document invents (`rx_work`, `RX_NCAPS`, `RX_UNSET`, `RX_ENGINE`, `RX_ERR_STEPS`, `RX_ERR_FRAMES`, `RX_BT_FRAMES`, `RX_TRAIL_FRAMES`, `RX_NSTATE`, `RX_HYBRID_MIN`, and the emitted labels) | yes; written here with the default `rx`/`RX` per that document's convention |
| pcrec's own library surface | `PCREC_*`, `--step-budget`, `--engine` | no (namespace 2) |

**SUPERSEDED (D44.2) — `<prefix>_span` no longer belongs in this table at
all.** A prior version of the middle row listed `<prefix>_span` among the
per-artifact symbols this document consumes; it RETIRES at [M4.4]
(`match_api_m4.md` §1.0, D44.2) rather than merely changing representation,
so every reference to it below (§2.2's `RX_UNSET`/span discussion, §3.4's
delivery description) should be read as referring to `caps[0]`, not a
separate span object.

**This document introduces no new fixed-literal ABI type.** It consumes the
three that exist and invents only per-artifact symbols, which is the family
where prefix-scoping is already settled.

**RULED (D41.1, D41.2, 2026-08-14):** `match_api_m4.md` §12.6 (`<prefix>_match`
as the match-here entry's name) and §12.7 (`rx_ctx`/`rx_matchfn`/
`rx_callout_ref` as fixed literal, unprefixed names) are both ruled exactly
as those sections proposed — Frank did not reverse §12.7, so the "if
reversed" paragraph below is now a counterfactual, kept for the record
rather than as an open risk. `match_api_m4.md` §7's naming table also now
carries a new fourth entry this document did not have when §0.3 was
written: `<prefix>_match_caps` (D41.4), the anchored capture-delivering
entry — per-artifact, `--prefix`-scoped, same family as `<prefix>_match`.
It does not change this table, since it falls in the same "per-artifact
emitted symbols" row already covering `<prefix>_match`.

**If Frank reverses §12.7** (making the ABI types `<prefix>_ctx`-scoped), the
engine design is almost entirely insensitive: the resume stack, the trail, the
budget, selection, the hybrid, islands, DD-9 and SR-8 do not mention those
types. Exactly one thing changes, and it is the thing §12.7 predicts — the
CALLOUT CALL SITE (§3.4, §6.3). A matcher compiled with `--prefix foo` calling
a callout that is itself a matcher compiled with `--prefix bar` would face
incompatible `foo_ctx`/`bar_ctx` types, so the call site would need a cast or a
generated adapter struct, and F2's `__builtin_trap()` check would be
per-type rather than per-ABI. That is a cost on the composition path only.

Separately, and worth stating so a reversal does not look like it dissolves
the finding: **§11.2 (match-here cannot deliver captures) is independent of
the naming question.** It is a property of `rx_matchfn`'s parameter and return
types, whatever those types are called.

---

## 1. The ground this stands on

### 1.1 Inputs consumed, not re-opened

The third column cites where the surface is COLLECTED, so this document can
consume it rather than restate it. `match_api_m4.md` is [M4.1]'s freeze
document (merged on main, itself PROPOSED until [M4.3] closes); the [M4.3]
panel reviews both together.

| Source | What it fixes | Collected at |
|---|---|---|
| D38 §1 / `design_callout_abi.md` §1 | `rx_matchfn = ptrdiff_t (const rx_ctx *)`; `rx_ctx` fields; `rx_callout_ref` binding unit | `match_api_m4.md` §4 |
| D38.3 / F1, F2 | match-here exported unconditionally; call sites emit `if (ret < -1) __builtin_trap();` | §3 (incl. its scope note: no call sites exist to attach the trap to until callouts or V-E land) |
| D38.4 | native abort NONE in v1; return values `< -1` RESERVED | §3 |
| D38.5 / F5 | captures visible IN to a callout, opaque OUT of a composed matcher | §4 |
| D38.6 | `ncap` is a watermark at callout sites, pinned to `ngroups + 1` on a completed match | §2.1 — and note its reconciliation with C6: the two are properties of different MOMENTS, not a contradiction over one field |
| D38 Q12 / subst C4, C5 | caps are `ptrdiff_t[2]` pairs, `{-1,-1}` unset; `rx_span` breaks at the M4 freeze | §1, §2.1; `RX_NCAPS`/`RX_UNSET` spellings at §2.1 |
| subst C1–C11 | the capture-offset contract in full | §2.2's conformance table — consumed wholesale by §3.4 below |
| D39.1 + addendum / F8 | exported `{name, number, ref}` group index per pattern | §5 |
| D36 / F7 | callouts are engine-forcing; selection must answer per-pattern | this document, §5 |
| D22 | DD-2 is ROBUSTNESS, not a security boundary, and is not traded against speed | — |
| D18 | options are compiled away; every option dimension must earn its axis | — |
| D26 | PCRE2 is the source of truth for what MATCHES; diagnostic wording is tier 3 | — |
| D19 / TS-1 | usable from threads, never threaded; all-const tables, no mutable globals | — |
| PC-5 / D38 | `COPY_MATCHED_SUBJECT = NEVER` — allocation-free generated matchers, caller owns buffers | — |
| D40 + addendum | pre-v1, breaks carry no compatibility weight and are governed only in FORM (D37 announcement + DD-3 accounting); the as-built contract graduates to `docs/spec/` at [M4.7]'s close | ruled after this document's brief; consumed at §5.7.3 and §12 ASK-2 |

All RULED (the `match_api_m4.md` sections cited are that document's collection
of them, plus its own PROPOSED-here spellings, which this document adopts —
§0.3). Where engine reality pulls against one of them, §11 reports it rather
than quietly designing around it.

**One question comes back the other way.** `match_api_m4.md` §11 item 7 /
§12.8 / §13 ASK 4 records an open question and assigns it here: what a
DFA-compiled, group-bearing, non-backreference pattern reports through
`caps[1..ngroups]`. It is answered in §5.7, with the M4.4→M4.5 gap covered
explicitly, and §11.2 sharpens the question itself before answering it.

### 1.2 What exists today, by inspection

STRUCTURAL, all of it:

- `src/core/compile.c:120-137` — the whole pipeline and the whole of today's
  engine selection: `if (!nfa_has_bot(&nfa))` picks `PCREC_ENG_UNANCH`, else
  `PCREC_ENG_ATTEMPT`. One `if`, inline in the driver.
- `src/gen/emit_dfa.c:275` `emit_unanchored` — table-driven forward scan
  (leftmost-first END, D3 accept-pruning) + reverse non-pruning scan (match
  START), with a `memchr`/bitmap start-state prefilter (`first[]`,
  `use_memchr`) and up to four self-loop skip loops (`pick_skip_states`).
- `src/gen/emit_dfa.c:482` `emit_attempt` — per-start computed-goto loop for
  `^` patterns, with EOL-variant states.
- `src/gen/emit_dfa.c:104-129` — the file-scope/per-engine naming discipline
  (OS-0b): `emit_span_typedef` once per FILE, `emit_search_decl` /
  `emit_search_head` once per ENGINE, entry name from `engine_entry_name()`.
- The emitted contract is `int <prefix>_search(const unsigned char *s, size_t
  n, size_t startpos, <prefix>_span *m)` returning 1 or 0 (`lib/pcrec.h`).
  **Negative returns are entirely unused today.** §4.4 spends that space.
- **There is no capture node in the AST.** `AKind` is
  `{A_CLASS, A_CAT, A_ALT, A_REP, A_EMPTY, A_BOL, A_EOL}`
  (`src/core/internal.h:41`). `(a|b)` and `(?:a|b)` produce the IDENTICAL tree.
  D31 ruled the erasure STAYS and rejected an `A_GROUP` wrapper on a measured
  compile-time cost. §2.8 and §11.3 deal with this.
- `Ctx.ncap` counts capturing groups at parse time and feeds `--count-groups`
  only (`src/core/internal.h:198`).
- The registry's `engines` column (`ENGM_DFA` / `ENGM_VM`) exists and is
  consumed by nothing until SR-8 (`src/core/internal.h:779`,
  `src/parse/registry.c:82`).
- `--explain` takes a CONSTRUCT, not a pattern (`cli/main.c:34`). It is
  therefore NOT the surface F7 asks for. §5.5.

---

## 2. The backtracking VM as emitted specialized C

### 2.1 The mandate, taken literally

APPROACH's opening sentence is that the generated matcher "has no runtime
interpreter, no dispatch tables to walk generically". A backtracking VM is
the construct most likely to smuggle one back in — the textbook shape is a
bytecode array plus a `switch` in a loop, and that is exactly what pcrec must
not emit.

So: the pattern's program IS the emitted control flow. Each pattern position
gets a label. The continuation of a matched atom is a fallthrough or a direct
`goto`, resolved at compile time. Nothing in the emitted matcher consults a
table to decide what to do next; tables appear only where they already appear
today — as `static const` transition data for a DFA ISLAND (§6.3).

BELIEVED consequence worth stating because it is the structural answer to the
gcc-compile-time problem R1 A-3 found: **the VM's emitted code size is linear
in the PATTERN, not in a determinized state count.** A 1000-node pattern emits
~1000 labels. The measured danger zone for computed-goto functions was 2048
DFA states → 63 s at -O2 and 8192 → DNF (APPROACH §2, MEASURED, R1 A-3), and
DFA state counts are exponential in pattern size where VM label counts are
linear. The VM should therefore never approach it. §12 ASK-7 wants this
measured rather than believed.

### 2.2 The emitted shape

Sketch for `(a|b)+c`, prefix `rx`, one capture group. Illustrative, not a
codegen spec — M4.5 owns the exact text.

```c
/* The mutable working set, declared ONCE by whichever entry owns the call
 * (§2.6): the search entry declares it around its whole start-position loop,
 * the F1 match-here wrapper declares it around its single call. All locals —
 * no globals (TS-1), no allocation (COPY_MATCHED_SUBJECT=NEVER's precedent). */
typedef struct {
    ptrdiff_t stv[RX_NSTATE];                                  /* §2.4 */
    struct { const void *k; size_t pos; unsigned mark; } bt[RX_BT_FRAMES];
    struct { unsigned short slot; ptrdiff_t v; }        tr[RX_TRAIL_FRAMES];
    unsigned btn, trn;
    long     budget;
} rx_work;

static ptrdiff_t rx_match_impl(const rx_ctx *ctx, rx_work *w)
{
    const unsigned char *const s = ctx->subject;
    const size_t n = ctx->len;
    size_t pos = ctx->pos;
    ptrdiff_t *const stv = w->stv;      /* RX_SET/RX_PUSH expand against `w` */

rx_L0:                                  /* group 1 open, iteration entry */
    RX_SET(2*1 + 0, (ptrdiff_t)pos);    /* caps[1][0] = pos, trailed */
rx_L1:
    RX_PUSH(&&rx_L2, pos);              /* 'a' is preferred; 'b' is the resume */
    if (pos < n && s[pos] == 'a') { pos++; goto rx_L3; }
    goto rx_fail;
rx_L2:
    if (pos < n && s[pos] == 'b') { pos++; goto rx_L3; }
    goto rx_fail;
rx_L3:                                  /* group 1 close */
    RX_SET(2*1 + 1, (ptrdiff_t)pos);
    /* '+' is greedy: another iteration is preferred, the exit is the resume */
    RX_PUSH(&&rx_L4, pos);
    goto rx_L0;
rx_L4:
    if (pos < n && s[pos] == 'c') { pos++; goto rx_accept; }
    goto rx_fail;

rx_accept:
    /* the caller's caps array is filled by the ENTRY, not here (§3.4) */
    return (ptrdiff_t)(pos - ctx->pos);

rx_fail:
    if (w->btn == 0) return -1;
    if (--w->budget < 0) return RX_INTERNAL_STEPS;    /* §4.4 */
    { const unsigned b = --w->btn;
      pos = w->bt[b].pos;
      while (w->trn > w->bt[b].mark) {
          --w->trn; stv[w->tr[w->trn].slot] = w->tr[w->trn].v;
      }
      goto *w->bt[b].k; }
}
```

Five properties of that shape, each of which is a decision:

1. **One function per pattern per engine.** Matches the existing emitter and
   OS-0b's naming discipline; label addresses are function-local, which is
   fine WITHIN a call (APPROACH §6's A-4/A-5 note that `&&label` does not
   survive a return is a STREAMING constraint, not a within-call one).
2. **`rx_fail` is the only backtracker**, and the only indirect jump.
3. **Greedy vs lazy is which side is the fallthrough.** Greedy: push the exit,
   fall into the body. Lazy: push the body, fall into the exit. No flag is
   consulted at run time — D18's "options are compiled away" applied to
   quantifier preference.
4. **Alternation is the same shape**: push branch 2's label, fall into branch
   1. N-way alternation pushes a chain, one frame per untried branch, in
   reverse preference order. (BELIEVED optimization, deferred to M4.6: a
   trie-factored alternation — the D9 machinery already in `nfa.c` — should
   emit as a first-byte switch with no pushes at all where branches are
   pairwise-disjoint on their first byte.)
5. **Position is a plain local.** Restored from the resume frame, never
   trailed.

### 2.3 Why an explicit stack and not C recursion

Three independent reasons, any one of which is sufficient:

1. **The project has already paid for unbounded C recursion twice.** DD-10 and
   D10 exist because `compile_ast` and `clo_visit` recursed on pattern
   structure; the R1 R-2 fix flattens `A_CAT`/`A_ALT` spines iteratively for
   exactly this reason (`src/ir/nfa.c`). A recursive matcher re-introduces the
   bug class in the GENERATED code, where we cannot fix it after shipping.
2. **D19's stack budget is a real number.** The threading stance is "usable
   FROM threads"; a 128 KB musl thread stack is the recorded constraint. A
   recursive matcher's depth is data-dependent (one frame per backtrack point,
   i.e. O(n) for `(a|b)*`), so the generated matcher's stack usage would not
   be statable, let alone boundable. An explicit array's is a compile-time
   constant.
3. **You cannot portably check C stack depth, and DD-2 requires that you
   check something.** The budget and the depth bound are both only expressible
   because the stack is ours.

RULED-adjacent: APPROACH §2's table already says "explicit stack, no C
recursion". This section is the argument, not a new decision.

### 2.4 Mutable state: one array, one trail

Everything the engine mutates and a backtrack must undo lives in ONE flat
`ptrdiff_t stv[RX_NSTATE]` whose layout is fixed at compile time:

| slots | contents |
|---|---|
| `0 .. 2*NG+1` | capture pairs (slot `2k` = start of group `k`, `2k+1` = end); slots 0,1 are `$0` |
| next `R` | bounded-repeat counters (`{m,n}`) |
| next `E` | empty-iteration guards (§3.3): the position at which the current iteration of loop *i* began |

Writes go through `RX_SET(slot, v)`, which pushes `{slot, old}` on the trail
and then stores. A resume frame records `trn` at push time as its `mark`;
popping rewinds the trail to the mark.

Why one array rather than three mechanisms: the restore loop is written once,
the overflow bound is one number, and a future slot class (a `\K` mark, a
recursion frame) costs a layout row rather than a new save/restore path.

Two compile-time refinements, both BELIEVED and both cheap:

- A slot written where no live resume frame can reach the write needs no trail
  entry. The common case (`(\d+)-(\d+)`, no quantifier containing a capture)
  trails nothing at all.
- The array is initialised to `RX_UNSET` ONCE per SEARCH call, not per start
  position. On a failed attempt the trail rewind to mark 0 restores every slot
  that was written back to `RX_UNSET` by construction, so the per-attempt
  reset is O(writes-since-attempt-start) rather than O(NG). This matters for
  the VM-only per-start loop (§2.6) on wide patterns; it is worth stating
  because the naive `memset` per start position is O(NG·n).

### 2.5 Two bounds, two capacities

`RX_BT_FRAMES` (resume stack) and `RX_TRAIL_FRAMES` (capture trail) are
compile-time constants placed in the matcher's frame. Where the pattern's
dynamic depth is statically bounded — no choice point inside an unbounded
quantifier — the emitter computes the exact requirement and the array is
exactly that size. Where it is not (`((a)|b)*`), the arrays take a default and
overflow is a distinct honest failure (§4.5).

STRUCTURAL note on why unbounded depth is rarer than it looks: a quantified
SIMPLE item (a single class, no captures, no nested choice) must not push one
frame per iteration — an 8 MB `a*` cannot store 8 M frames in an
allocation-free matcher. It compiles to a **span loop plus a cursor**: consume
greedily to the furthest position, push ONE resume frame recording the loop's
low-water mark, and backtracking decrements the cursor. So the residual
unbounded-depth class is quantifiers CONTAINING a choice point or a capture,
which is small and compile-time detectable.

**RULED (D44, ratifying R21 E-4) — the cursor's HOME and its re-push
discipline, both previously unshown.** The panel found the span-loop
cursor had "no home in §2.4's layout" — §2.4's `stv` table lists capture
pairs, repeat counters and empty-iteration guards, and nothing else, so a
reader could reasonably ask where the cursor's own mutable value lives,
and whether it is trailed (defeating the whole point of a mechanism
designed to avoid per-iteration trail entries). It is not trailed:

- **The cursor is a plain local, UNTRAILED, exactly like `pos` (§2.2
  property 5).** It is restored directly from the resume frame's recorded
  low-water mark on backtrack — `pos = w->bt[b].pos` in §2.2's sketch
  already does this generically for every resume frame, including the
  span loop's; the cursor needs no `RX_SET`/trail entry because a resume
  frame IS its save point, the same relationship `pos` has to every other
  resume frame in the VM. Nothing new is required in `stv`'s layout; the
  cursor was never a candidate for a trail slot, and this section should
  have said so rather than leaving the question open by omission.
- **Re-push discipline, stated explicitly (previously "unshown"):** on
  entry, the span loop consumes greedily to its furthest position and
  pushes exactly ONE resume frame recording the low-water mark (the
  loop's minimum acceptable length, e.g. 0 for `a*`, 1 for `a+`). On
  BACKTRACK into that frame, the engine decrements the cursor one
  position and re-tries the continuation from there. If the decremented
  cursor is still above the low-water mark, the SAME resume frame is
  RE-PUSHED (same label, new `pos`) before falling through to the
  continuation attempt — so a second backtrack into the loop has
  somewhere to land. If the cursor has reached the low-water mark, no
  frame is re-pushed and this backtrack point is exhausted (`w->btn`
  decrements permanently for it, matching `rx_fail`'s ordinary pop). This
  is still O(1) frames on the resume STACK at any instant — never more
  than one live frame per span loop — even though the loop may be
  re-entered up to (furthest − low-water-mark) times across the whole
  match; each re-push replaces the just-popped frame rather than growing
  the stack.

**RULED (D44.1, 2026-08-14) — [M4.5] EXTENDS this scheme to deterministic
capture-bearing bodies, closing E-3's Θ(n) working-set finding.** The
panel MEASURED that `rx_work` arrays are Θ(n) on benign matches
(~68 B/subject byte for `(a|b)+c`) — as locals under D19's 128 KB thread
stack, that caps captured matching at roughly 1.9 KB of subject, three
orders of magnitude below where the step budget would notice (§4). The
root cause: §2.5 as originally written excluded ANY capture-bearing body
from the cursor scheme by definition (a capture write needs an `RX_SET`
call, which the plain span-loop-plus-cursor above never makes), so every
capture-bearing quantifier fell back to one resume frame PER ITERATION
regardless of whether the body was actually deterministic. D44.1 corrects
this: **the cursor scheme extends to any PROVABLY-SINGLE-PATH quantifier
body, including one that writes captures**, on the condition that the
body's own iteration is deterministic (no choice point inside it — the
same "no choice point inside an unbounded quantifier" test the STRUCTURAL
note above already uses, now applied per-quantifier rather than
excluding captures wholesale). Two consequences:

- **Group spans are computed FROM THE CURSOR AT LOOP EXIT**, not written
  per iteration. A deterministic capture-bearing body like `(a)+` need not
  call `RX_SET` on every iteration at all — the group's final `[start,
  end)` is derivable from the cursor's low-water mark and its value at
  exit, written ONCE when the loop's continuation is taken. This is what
  deletes the Θ(n) resume-frame AND trail cost simultaneously: no
  per-iteration frame (already true of the plain cursor scheme) and no
  per-iteration trail entry either (new — a capture-bearing body was
  previously assumed to need one write per iteration for backtracking
  correctness, which the "write on traverse" rule in §3.2 states
  generally; the deterministic case is the one where that generality is
  provably unnecessary, because there is only one path to undo).
- **The residual class — quantifier bodies that are NOT provably
  single-path (contain a choice point) — carries an HONEST STAMPED
  ceiling** in `rx_info` (`match_api_m4.md` §5's `frame_capacity`/
  `subject_ceiling` members, D44.5): rather than silently capping at
  whatever the default frame/trail array size happens to be, the
  artifact states the subject length past which frame/trail exhaustion
  becomes possible for THIS pattern, so a caller can know the limit
  without discovering it by triggering `RX_ERR_FRAMES`. [M4.5] is where
  this extension is BUILT (§14's own scope line); this section records
  the design.

**Alignment note (manager-recorded from Frank's question, 2026-08-14).**
The measured entry sizes are the ALIGNED sizes, not waste: a frame is
24 B (`void *` resume address + `size_t` pos + `unsigned` mark padded
8/8/8) and a trail entry 16 B (`unsigned short` slot padded + `ptrdiff_t`
old value) — both arrays stride at multiples of 8 with every 8-byte
member naturally aligned, and the "~68 B/subject byte" figure is
arithmetic ACROSS the two separately-aligned arrays, never a stride
anything loads at. Any future field-packing (2-byte label index, 32-bit
positions) must keep stride alignment; the clean shape for that is
STRUCTURE-OF-ARRAYS (separate `slots[]`/`vals[]`, each naturally
aligned, ~10 B/entry aggregate), never a packed interleaved struct.
Recorded as a measured-optimization option for [M4.5]/[M4.6]; largely
mooted for common shapes by the D44.1 cursor extension above, which
deletes entries rather than shrinking them.

### 2.6 Search wraps match-here

F1 makes the anchored entry the primitive. Two search strategies sit on it:

- **HYBRID (default whenever a DFA prefilter is available, §6).** The existing
  forward+reverse DFA pair computes the span `[start, end)`. The VM runs once,
  anchored at `start`. The VM never scans the subject.
- **VM-ONLY (no usable prefilter).** The classic loop:

  ```c
  for (size_t start = startpos; start <= n; start++) {
      /* reuse emit_dfa.c's first-byte / memchr skip to advance `start` */
      ptrdiff_t r = rx_match_impl(&ctx_at(start), &w);
      if (r >= 0) { /* copy caps out; $0 = [start, start+r) */ return 1; }
      if (r == RX_INTERNAL_STEPS) return RX_ERR_STEPS;
      rx_unwind(&w, 0);   /* trail back to mark 0: every slot the failed
                             attempt wrote returns to RX_UNSET (§2.4) */
  }
  ```

  Leftmost is the loop's increasing order; first-within-a-start is the VM's
  own return-on-first-accept.

The `rx_work` block (§2.2) is declared by the search entry, around the loop —
so the budget is threaded ACROSS attempts rather than reset per start
(otherwise an O(n) sweep of O(budget) attempts is still unbounded, §4), and the
slot array's `RX_UNSET` initialisation happens once rather than n times
(§2.4).

**RULED (D41.5, 2026-08-14) — this one-shot posture is a CHOSEN primitive,
not merely today's default.** See D41 for the full record: SIMD block
scanning motivated the find-all alternative, but under PCRE2's sequential
semantics "find all" is the same result set as repeated one-shot search, so
the question was redone work only. Both entries above stay exactly as
designed; the ruling's remedies live outside this document — EMITTED LOOPS
own dense-match iteration, and a designated `<prefix>_iter` cursor entry is
the additive extension for a future embedder customer.

### 2.7 Where computed goto is used, and D13

D13's correction (MEASURED, `../dev/decisions.md:358` and its R3.2 addendum)
is that computed goto is ~2.5x SLOWER than a table on data-dependent
transitions and ~3.5x FASTER on predictable ones; the decision "table always"
stands for DFA scanning because unpredictable transitions dominate there.

The VM does not have that choice to make, because it has no per-byte dispatch
at all. Its indirect jump fires once per BACKTRACK, and its frequency is a
property of the pattern, not of the subject. Two consequences:

- No arbitration is owed here. The one indirect jump is on the cold path by
  construction; replacing it with a `switch` would cost a bounds check and a
  jump table lookup on the same cold path for no gain.
- DFA ISLANDS embedded in the VM inherit D13 unchanged: they are DFA scanning,
  they get tables, and they reuse the existing emitters.

### 2.8 Reused vs new

**Reused unchanged:**

| Component | Use |
|---|---|
| `src/parse/` | entirely — the VM changes nothing about parsing |
| `src/ir/nfa.c` `pcrec_build_nfa` | the prefilter's forward and reverse NFAs; island fragments |
| `src/ir/nfa.c` `nfa_wrap_unanchored` | the prefilter's forward machine only (§7.3) |
| `src/ir/dfa.c` | prefilter DFAs and island DFAs, both prune modes |
| `src/opt/minimize.c` | both |
| `src/gen/emit_dfa.c` table emitters (`emit_u8_table`, `emit_tr_table`, `emit_acc_table`, `emit_eol_table`, `emit_stay_table`) | island emission |
| `src/gen/emit_dfa.c` `pick_skip_states`, `first[]`/`use_memchr` prefilter analysis | the VM-only search loop's start skipping |
| `emit_span_typedef` / `emit_search_decl` / `engine_entry_name` (OS-0b) | a third engine joins the same naming discipline |

**New:**

- `src/gen/emit_vm.c` — the VM emitter. APPROACH §8 already names it
  `engine_vm.c`; either spelling, one file.
- A capture-carrying AST/IR path (§11.3 — this is the open one).
- `src/opt/select_engine.c` — the selection pass and its socket (§5).
- A gen-internal header exposing the five table emitters, which are `static`
  in `emit_dfa.c` today. This is the one refactor M4.5 cannot avoid, and it is
  mechanical: their OUTPUT is already function-local `static const`, which is
  exactly what an island inside the VM function needs.

**Explicitly NOT reused:** the D3 accept-pruning subset construction is not the
island machinery for accept-LIST islands. APPROACH §2's A-1 amendment already
says this (the pruning machine prunes exactly the threads an accept list
needs); repeated here so nobody rediscovers it. Accept-list islands are
deferred anyway (§6.3).

### 2.9 Encoding

M4 is ASCII/byte only. The VM's cursor is `s[pos]` and class tests are the
same 256-bit bitmaps the DFA uses. M5 adds an inlined decoder at the VM's
consume sites per APPROACH §4; nothing in this design forecloses it, and
nothing in this design tries to anticipate it.

---

## 3. Captures and PCRE2 leftmost/priority semantics

### 3.1 The semantics, stated as an algorithm

RULED (APPROACH §2, D3's framing): PCRE is leftmost-first with greedy/lazy
preference, NOT POSIX leftmost-longest.

- **Leftmost** = try start positions in increasing order; the first start that
  yields any match owns the match.
- **First** = within a start, explore the preference-ordered tree of choices
  depth-first, preferred branch first; **the first complete match found IS the
  match**. No candidate comparison, no longest-wins, no second pass.

That is the whole semantic. The VM returns from `rx_accept` immediately, and
the capture slots at that instant are the answer.

### 3.2 Write and undo discipline

- **Write on traverse.** `caps[k][0]` is written when control passes the
  group's opening position; `caps[k][1]` when it passes the closing position.
- **Undo is exact restore, never clear.** The trail restores the PREVIOUS
  value, not `RX_UNSET`. This is load-bearing and the naive version is wrong
  in both directions:
  - `(a)*` against `"aa"` must report group 1 = the SECOND `a`. A later
    iteration overwrites, and if the loop then exits normally the overwrite
    must stand.
  - `(a)b|(a)c` against `"ac"`: the first branch writes group 1, fails on
    `b`, and the restore must return group 1 to unset before branch 2 runs —
    but for `((a)|b)+` against `"ab"`, a failed final iteration must restore
    group 2 to the value the SUCCESSFUL earlier iteration left, not to unset.
    Only a per-write old-value trail gets both.
- **Repeat counters and empty-guards are trailed identically** (§2.4), because
  they are undone at exactly the same points.

### 3.3 The empty-iteration rule

A quantifier whose body can match the empty string must not loop forever:
`(a*)*`, `(|a)+`, `((?:))*`.

~~Design: each unbounded (or high-bounded) quantifier whose body is
nullable — a compile-time property — gets an empty-guard slot holding the
position at which the current iteration began. At the iteration's close, if
`pos` equals the guard, the loop does not iterate again; control takes the
exit continuation.~~

**RULED (D44, ratifying R21 E-2) — the guard applies IFF `rmax == -1`
(truly unbounded), and the "or high-bounded" extension above is STRUCK,
not merely narrowed.** The panel MEASURED the "high-bounded" reading
against libpcre2: with the guard applied to bounded repeats too, 60 of
225,240 generated pairs diverge; restricted to `rmax == -1` only, 0 of
225,240 diverge. Witness: `(a*?){1,2}b` on `"ab"` — the guard-extended-to-
bounded design gives `g1=(1,1)`, both oracles (python and PCRE2) give
`(0,1)`. **PCRE2's actual behaviour is that bounded repeats REPLICATE**:
a `{1,2}` body is compiled as body-body?, each copy an independent
opportunity to match (empty or not) — an empty match at iteration 1 does
not suppress iteration 2 the way it suppresses continuation of a truly
unbounded loop, because there IS no "continuation" test at a bounded
count; there is just the next copy. The corrected design: **the
empty-guard mechanism exists ONLY for `rmax == -1`** (`*`, `+`, `{n,}`);
every bounded quantifier (`{m,n}`, `?`) compiles as its `m` mandatory
copies plus `n-m` optional copies, exactly as an unbounded-quantifier-free
design would, with no guard slot and no suppression test at all — the
"loop" framing in §2.2's illustrative code only ever applied to the
`rmax == -1` case to begin with, and this ruling makes that scope
explicit rather than implicit.

**Compliance note (E-2's side-finding, flagged for a
`docs/pcre2_compliance.md` row at implementation time, not resolved
here):** PCRE2 itself REFUSES sufficiently large bounded repeats (`(a*)
{0,5000}` errors "regular expression is too large" on the measured box)
where pcrec's own repeat-count caps allow `(a*){0,10000}` to compile
today. This is not a capture-semantics divergence — it is PCRE2 imposing
a resource limit pcrec does not share — and D26 does not require pcrec to
adopt someone else's resource ceiling. Recorded so it is not later read as
an unnoticed compliance gap.

BELIEVED, and this is where I expect a panel finding: PCRE2's actual
behaviour for the capture VALUES left behind by a suppressed empty iteration
is subtle, and it is exactly the area where **python `re` and PCRE2 are known
to disagree**. That matters more here than usual, because the base-tier oracle
IS python `re` (D4). See §3.6.

### 3.4 Delivery into the D38 caps representation

RULED shape: `ptrdiff_t caps[][2]`, `{-1,-1}` unset, byte offsets (subst C4,
C5, Q9/DD-12), `RX_NCAPS` a compile-time constant equal to `ncaps`
(D44/A-5 vocabulary restatement, `match_api_m4.md` §2 — was "`ngroups + 1`").

**RULED (D44, ratifying R21 C-8) — one clarifying sentence, the two
`ptrdiff_t[2]` arrays this section discusses are DIFFERENT objects.** The
`ptrdiff_t caps[][2]` named just above is the CALLER-OWNED OUTPUT array
`<prefix>_search`/`<prefix>_match_caps` write into on success
(`match_api_m4.md` §1.0/§3.1) — mutable, caller-declared, written by the
entry. It is textually easy to conflate with `const rx_ctx.caps` (§4's
FROZEN INPUT field, read-only, populated by the OUTER engine at a callout
site with captures-so-far) because both are `const`-or-not
`ptrdiff_t[2]` pairs with the same element layout — that sameness is the
POINT (F3's one-representation rule), but it means a reader must track
which ROLE a given `caps` reference plays from context. This section's
`caps` is always the output-array role unless stated otherwise.

- The VM's working slots (`stv`) are LOCAL, and the ENTRY copies the capture
  region into the caller's `caps` array on a completed match — one linear copy
  of `2*(NG+1)` `ptrdiff_t`s, on the success path only. The alternative
  (aliasing the caller's array directly, write-through) was considered and
  rejected: `stv` also holds repeat counters and empty-guards (§2.4), so
  aliasing would split the trail's slot space across two base pointers to save
  a copy whose size is the group count, not the subject length.
- On a completed match every pair is written (subst C6): slots untouched
  during the match hold `RX_UNSET` from the initialisation, and slot 0/1
  (`$0`) is written by the entry from `start` and the returned length.
- On a failed match the caller's array is UNTOUCHED (nothing was copied). The
  contract stays "caps are meaningful only when the return says match", which
  costs nothing to honour under the copy-on-success shape.
- `ncap` at a CALLOUT site is a compile-time constant per site:
  `1 + (highest group number whose opening paren precedes this site in the
  pattern)`. That is the honest reading of D38.6's "capture slots known so
  far", it costs an immediate in the ctx initialiser, and it is deterministic
  across runs — which matters because a callout's behaviour must not depend on
  which backtracking path reached it.
- **`rx_ctx.caps` handed to a callout is valid for the duration of the call
  only.** The engine mutates and rewinds the same storage afterwards. A
  callout that retains the pointer is the embedder's bug. This is not in F1–F8
  and should join the freeze list — §12 ASK-3.

### 3.5 F8's group index

D39.1 + addendum: a sorted `{const char *name; int number; const char *ref;}`
array plus count, `.rodata`, exported. The engine's only obligation is that
group NUMBERS in the index agree with slot indices in `caps` — i.e. group `k`
occupies slots `2k`, `2k+1`. Named groups are module `named_groups` and do not
exist yet; the index is emitted with count 0 for the base tier, which is the
right shape to ship because it makes the ARTIFACT contract complete on day one
(D37's artifacts-carry-their-contract precedent) rather than adding a symbol
later.

### 3.6 Oracle strategy

Base tier (M4.5): python `re`'s `match.span(k)`, via the existing
`tests/harness/verify_rxt.py` channel, with the `.rxt` format extended to
carry per-group expectations. D4's cross-verification discipline is unchanged;
the only new thing is more columns.

M4.7: libpcre2 ovectors, differential, gate-ON per `../testing.md`'s
differential-gate principle, plus the fuzzer extended to compare spans.

**RULED (D44, ratifying R21's E-ASK-1 refutation) — ASK-1 REFUTED as
stated, §3.6/§12 RE-SCOPED.** The panel ran the MEASUREMENT §12 ASK-1
below asked for, before M4.5 writes any test: **python `re` and libpcre2
disagreed ZERO times** across 225,240 generated pairs plus 53 targeted
empty-iteration cases (base tier). The prediction this section made — "they
disagree, and the disagreements cluster in the empty-iteration family" —
did not hold. Every REAL disagreement found this round was pcrec-or-design
vs. BOTH oracles agreeing with each other (E-1/K17 chief among them, and
E-2's bounded-repeat guard finding above), never oracle-vs-oracle.

**~~The warning that belongs in the plan, not just here.~~** ~~python `re`
and PCRE2 do not agree on every capture question, and the disagreements
cluster in exactly the areas §3.3 flags... The M4.5 capture corpus must
carry an explicit oracle-EXCLUSION mechanism for these cases from the
start...~~ **This is the wrong instrument, and building it would have been
actively harmful**: an exclusion mechanism built to protect expectations
from oracle noise would have HIDDEN K17, because the noise it was designed
to guard against measured zero — the one real bug found this round was
pcrec disagreeing with BOTH oracles at once, which a python-vs-PCRE2
exclusion list does nothing to catch and everything to obscure if someone
later mis-scoped an exclusion to cover it. This is the check-design lesson
recurring in a new costume: point instruments at pcrec first, oracles
second.

**RE-SCOPED (D44) — the corpus mechanism is a THREE-WAY comparison, with
NO pre-built exclusion list:**

1. Every capture-bearing corpus expectation is checked against BOTH python
   `re` and libpcre2 (once M4.7's differential exists; python alone at
   M4.5 per D4's staged oracle discipline, unchanged).
2. **A 2-1 split with pcrec in the MINORITY is a bug, never an exclusion
   candidate.** There is no mechanism that lets a corpus author mark a
   cell "expected to diverge from an oracle" ahead of investigating it —
   the three-way comparison always runs, and a disagreement is triaged as
   a finding (fix pcrec, or `../dev/upstream_issues.md` if the minority
   view is actually correct and an oracle is wrong), never silently
   swallowed.
3. The base-tier caveat stands and is narrowed, not removed: the 225,240 +
   53 sweep covered the base tier only (no lookaround, no backrefs);
   disagreements in VM_ONLY-no-producer territory (module-gated, §9.1)
   remain plausible and unmeasured, and the three-way rule applies to them
   too once a producer exists.

§12 ASK-1's own text is UNCHANGED below (kept as the record of what was
asked and why it was worth running) but is now ANSWERED rather than open —
see its own RULED annotation.

### 3.7 The free internal differential

MEASURED-adjacent and worth building: for the capture-only tier the DFA and
the VM compute the match SPAN by completely independent methods (priority
subset construction vs. backtracking). §6.1 argues they must agree exactly.
So M4.5 can assert `span(VM) == span(DFA)` on **the entire existing .rxt
corpus** by re-running each pattern with its groups made capturing — a large,
nearly-free cross-check whose two sides do not share a derivation.

That property is worth calling out against this project's recorded
check-design failure mode (controls sharing a source with the thing they
control): here they genuinely do not.

**RULED (D44, ratifying R21 E-1/E-6) — this differential is a GATE, not
merely a nice-to-have cross-check, and it runs `--engine=vm` with the
prefilter OFF.** Two reasons converge on the same requirement:

1. **§6.1's STRUCTURAL claim is now BELIEVED-WITH-GATE, not held
   unconditionally** (see §6.1's own annotation below) — K17 is a live
   counterexample to the semantic half of the exactness claim this
   differential exists to check, so the differential graduates from
   "worth building" to a REQUIRED gate before [M4.4]/[M4.5] can rely on
   §6.1's claim for anything.
2. **E-6: under the HYBRID, `span(VM) == span(DFA)` is not an independent
   check at all — it is close to a TAUTOLOGY**, because the hybrid feeds
   the VM the DFA's own answer as its anchored window (§2.6): `$0.start`
   is literally the DFA's own computed value, echoed back, not an
   independently-derived one. Comparing "the DFA's span" against "the
   VM's span, which was TOLD the DFA's span as its starting point" proves
   far less than the original framing implied — the VM could still get
   $0.END or a capture wrong while trivially agreeing on $0.START. So the
   differential's GATE mode runs `--engine=vm` (§5.6's override) to force
   the VM-ONLY search loop (§2.6), which scans and matches with NO
   DFA-derived window at all — a genuinely independent second derivation
   of the whole span, not merely the tail of one the DFA already computed.
   Frank independently requested this exact comparison mode (a plain
   `--engine=vm` run with the prefilter disabled) for the same reason
   this finding gives, so the ruling and the request converge.

§5.6 gains this rule explicitly (below): `--engine=vm`'s diagnostic value
now includes being the one mode in which §3.7's differential is actually
independent.

---

## 4. DD-2 — the step budget

### 4.1 Framing, taken from D22 rather than re-argued

RULED (D22): adversarial patterns are out of scope. DD-2 is a ROBUSTNESS
feature — a pathological pattern from a TRUSTED author should fail honestly
rather than hang — it is not a security boundary and **it must not be traded
against execution speed**.

Everything below follows from taking that seriously. In particular: the budget
must cost approximately nothing on patterns that never approach it, which
rules out per-character instrumentation.

### 4.2 What counts as a step

**A step is one backtrack resumption.** Not a character, not an instruction.

The counter lives at exactly one place in the emitted code — the decrement in
`rx_fail` (§2.2) — and therefore:

- Forward progress is FREE. A linear match over 100 MB costs zero steps.
- The budget is subject-length-independent, which is what makes a single
  absolute number defensible at all.
- Pathological behaviour is precisely unbounded resumption, so the counter
  measures the thing it is meant to bound and nothing else.
- The cost is one register decrement and one predictable branch on a path that
  fires once per backtrack. On patterns that do not backtrack it does not
  fire.

Two accounting details:

- A simple-repeat cursor retry (§2.5) goes through `rx_fail` like any other
  resumption, so shrinking `a*` one byte at a time costs one step per byte —
  correct, that IS the backtracking work.
- ~~A DFA island's internal scanning is bounded by `n` by construction and
  charges ZERO steps. An island cannot be the source of unbounded work, and
  instrumenting its inner loop would be exactly the speed trade D22 forbids.~~

**RULED (D44, ratifying R21 E-5) — "an island cannot be the source of
unbounded work" is TOO STRONG, and the counter now charges one step per
island ENTRY, not only at `rx_fail`.** The claim survives for a SINGLE
island scan (still bounded by `n`, still uninstrumented internally — that
half is unchanged and correct). What breaks is REPEATED entry: a
construct like `(ISLAND|x)*` where `ISLAND` is tried first at every outer
iteration can enter the island up to `n` times over the course of one
match, and each entry's internal scan can independently cost up to `O(n)`
(e.g. an island like `[^"]*"` that finds no closing quote scans to the
subject's end before failing). The BACKTRACK from a failed island entry to
the `x` alternative is already charged (one step, ordinary `rx_fail`
accounting) — but that charge reflects the CHOICE POINT, not the island
SCAN that happened before the choice point was reached, and an island
reached via plain forward fallthrough (no preceding choice, hence no
charged backtrack at all) was previously entered for free every time. The
aggregate is `O(n × resumptions)` real scanning work behind an `O(n)`
step count — not unbounded in the sense of non-terminating, but a
complexity gap the "cannot be the source" framing denied existed at all.

**The fix**: the counter decrements by one at island ENTRY — every attempt
to run an island's scan, whether reached via a freshly-charged backtrack
or via forward fallthrough with no choice point at all — in addition to
`rx_fail`'s existing per-resumption charge (the two are not double-counted
when they coincide: a backtrack that IMMEDIATELY re-enters an island is
one resumption event that happens to also be an island entry, charged
once, not twice; they diverge only for forward-fallthrough entries, which
previously had no charge point at all). This makes the TOTAL NUMBER of
island entries over one match subject to the same budget that bounds
ordinary backtracking, closing the loophole regardless of which path led
to the entry. It does not make DD-2 a wall-clock bound (§13's reworded
P-2 states the corrected claim precisely) — it restores the property DD-2
actually needs per D22's ROBUSTNESS framing: a budget that catches
absurd resumption/entry counts, not a guarantee that every budget-passing
match ran in linear wall-clock time.

### 4.3 Where the counter lives

A field of the `rx_work` block (§2.2), which the SEARCH entry declares as a
local around its whole start-position loop and passes by pointer — so it is
shared across all attempts of one search call. Not a global (TS-1: no mutable
globals, thread-safe by construction). Not a field of `rx_ctx` (it is `const`,
and D38 froze its fields).

### 4.4 The failure surface — reconciled with D38 without amending it

The constraint: `rx_matchfn`'s return space is frozen — `>= 0` length, `-1`
fail, `< -1` RESERVED and `__builtin_trap()`-enforced at every call site
(D38.4, F2). Budget exhaustion cannot use `-2` without violating that.

The observation that dissolves it: **`rx_search` is not an `rx_matchfn`.** It
returns `int`, currently `1` or `0`, and every negative value is unused
(`lib/pcrec.h`, STRUCTURAL). D38 says nothing about it.

So the emitted matcher has three layers:

| symbol | type | budget behaviour |
|---|---|---|
| `rx_match_impl` | internal `static`, takes `(const rx_ctx *, rx_work *)` | decrements `w->budget`; returns a private sentinel on exhaustion |
| `rx_match` | F1's export, `rx_matchfn` | fresh local budget; returns `-1` on exhaustion (indistinguishable from no-match, per D38's frozen space) |
| `rx_search` | pcrec's own entry | owns the budget across attempts; returns `RX_ERR_STEPS` (a negative code) |

The frozen ABI is satisfied exactly, the honest diagnosis exists at the entry
that has room for it, no global is introduced, and nothing needs re-ruling.

**The residual, stated rather than hidden:** a compiled matcher used AS a
callout (D38.2's one-line `rx_callout_ref` wrap) reports budget exhaustion to
its caller as "this path failed". The outer engine cannot distinguish "the
callee did not match" from "the callee gave up". §11.1 carries this as the
first ABI tension and §12 ASK-2 offers Frank the amendment if he wants it.

**Requirement handed to [M4.1]:** the search entry must reserve NEGATIVE
returns for engine-give-up conditions and name at least two — `RX_ERR_STEPS`
and `RX_ERR_FRAMES` (§4.5). This is a small, concrete thing the match-API
freeze must carry and it is cheap today because the space is empty.

### 4.5 The SECOND bound nobody wrote down

DD-2's row names a step budget. Allocation-freedom forces a second, distinct
robustness bound: **the resume stack and the capture trail are fixed-size
arrays, and they can fill.**

This is not the same failure as the step budget. A pattern can overflow the
frame array in a handful of steps (`((a)|b){0,10000}` on a long subject), and
a pattern can burn the step budget with a two-frame stack (`(a*)b`). Both need
honest failure; they are different diagnoses.

- Capacity is a compile-time constant, computed exactly where the pattern's
  dynamic depth is statically bounded (§2.5), defaulted otherwise.
- Overflow returns `RX_ERR_FRAMES` from the search entry, `-1` from
  match-here, on the same reasoning as §4.4.
- Precedent worth citing (D26-adjacent, not a compatibility obligation): PCRE2
  itself carries BOTH a `match_limit` and a `match_depth`/heap-frame limit.
  The two-bound shape is the neighbour's shape, arrived at independently here.

DD-2's row should be amended to name both. §12 ASK-4.

### 4.6 Default and override

**The number.** D12 rules that budgets are set from measured medians, not
vibes, and there is no measurement yet — so this design proposes the MECHANISM
and refuses to invent the number. What M4.6 must do: run the whole corpus plus
the bench matrix with the counter instrumented, take the maximum resumption
count any legitimate pattern needs, and set the default with a stated margin.
Provisional placeholder for bring-up only: 1,000,000.

Explicitly NOT adopted: PCRE2's `match_limit` default of 10,000,000. Its unit
is internal `match()` calls, which it also spends on non-backtracking
recursion; our unit is resumptions. Copying the number would be false
precision dressed as compatibility, which D26 tier 3 exists to prevent.

**The surface.** A GENERATION AXIS (D18: options are compiled away), not a
runtime parameter:

- `--step-budget=N` — emit the counter with budget N.
- `--fno-step-budget` — emit no counter at all. Zero cost, and honest because
  the artifact says so.
- `--backtrack-frames=N` — the §4.5 capacity.

Runtime parameterisation is not merely undesirable here, it is **unavailable**:
`rx_matchfn`'s signature is frozen and has no slot for a budget, and adding one
to `rx_ctx` is a DD-3 struct revision D38 reserved for capture export. The
generation-axis answer is the only one the ruled ABI leaves open, which is a
pleasant coincidence rather than a design triumph, and worth noting as such.

**Stamping.** The budget and frame capacity join the artifact stamp (§5.5).
D37's principle is that no artifact is ambiguous about what it was built with,
and "does this matcher have a step budget, and what is it" is exactly that
kind of question.

### 4.7 The ordering rule that keeps DD-2 from being a regression

MEASURED, and this is the sharpest thing in this section. Bench case (e),
`a*b` over 8 MB of all-`a`: pcrec 25,371 MB/s; pcre2-interp DNF>90s; python
DNF>90s; pcre2-jit 3,007 MB/s (pcrec 8.4x the best other engine)
— `tests/bench/compare/results-ubuntubudu-20260811-2.md`.

`(a*)b` is the same pattern with captures. On a naive VM it is O(n²) — roughly
7·10¹³ resumptions — so it would burn ANY budget and "fail honestly" where
pcrec today returns `nomatch` at 25 GB/s.

**A budget-exceeded return on a pattern pcrec answers today is a regression,
not robustness.** Therefore the design rule:

> The DFA prefilter runs BEFORE the VM. A pattern whose prefilter can answer
> must never reach the step budget.

For `(a*)b` the capture-erased forward DFA reports no accepting position
anywhere in one pass, and the VM is never entered. §6.2.

---

## 5. Per-pattern engine selection

### 5.1 The pass

Selection moves out of `compile.c`'s inline `if` (§1.2) into a pass,
`src/opt/select_engine.c`, running after parse and before machine
construction. It answers three things:

```c
typedef struct {
    unsigned engines;      /* ENGM_* mask: which engines CAN compile this */
    unsigned chosen;       /* exactly one ENGM_* bit */
    const char *why;       /* the forcing construct, for the stamp and F7 */
    size_t      why_pos;   /* pattern offset of it */
    bool        prefilter; /* §6: is a DFA prefilter available */
} EngineFit;
```

The `engines` mask is the SAME vocabulary the registry column already uses
(`ENGM_DFA` / `ENGM_VM`, `src/core/internal.h:307`), which is what makes SR-8
a consumption rather than a new schema (§9).

### 5.2 The socket, designed for customers that do not exist

The plan's two design notes (backrefs finite-language expansion; atomic groups
and possessives as cut operators, both Frank 2026-08-12) are named as future
selection customers. Reading them carefully changes the socket's shape, and
this is the most consequential design call in this section:

**They are not analyses that return a verdict. They are REWRITES that discharge
a verdict.** `(abc)\1` is VM-forced until the finite-language expansion turns
it into `abcabc`, at which point it is DFA-compilable. `(?>a+)b` is VM-forced
until the cut construction produces an equivalent DFA. In both cases the
analysis does not observe that the pattern is DFA-compilable; it MAKES it so.

So the socket is:

```c
typedef struct {
    const char *name;
    /* Does this construct force an engine, and where? */
    unsigned  (*forces)(Ctx *, const Ast *, size_t *why_pos);
    /* Optional: rewrite the AST so the forcing no longer applies.
       Returns NULL to decline. Must be semantics-preserving. */
    Ast      *(*discharge)(Ctx *, Ast *);
} EngineAnalysis;
```

and the pass is a FIXPOINT: analyse → if VM-forced, offer each registered
`discharge` a chance → re-analyse → stop when nothing changes or a bound is
hit. Ship it in M4.6 with zero registered `discharge` hooks; the bound exists
from day one so a later rewrite pair cannot loop.

Three properties this buys, each a thing the plan's notes explicitly need:

- The engine answer is per-PATTERN, not per-registry-row — which is exactly
  what both design notes insist on, and what F7 asks selection to be able to
  say.
- A rewrite is bounded by the EXISTING caps (`PCREC_MAX_NFA_STATES`, the DFA
  state caps, and the gcc-compile-time budget behind them). The finite-backref
  expansion note says "bounded by the existing NFA/DFA caps" — with the
  fixpoint shape that is automatic: the rewrite produces a bigger AST, machine
  construction hits its cap, and the cap's existing clean diagnostic fires.
  A rewrite that blows the cap should DECLINE rather than expand, so the
  fixpoint needs a size estimate before committing; that is the rewrite
  author's obligation, recorded here so it is inherited.
- A module owns its analysis, registered from the module's own file. The core
  never names `backrefs` or `atomic_groups`, which is APPROACH §3's rule
  applied to the engine axis.

### 5.3 What forces the VM, today and next

| Construct | Forces VM? | Authority |
|---|---|---|
| capturing group `(...)` with captures REQUESTED | yes | this document |
| callouts | yes, unconditionally | D36, F7 (RULED) |
| `\K` | yes | registry `VM_ONLY`, no module |
| backrefs, infinite-language group | yes | plan design note (RULED by Frank 2026-08-12) |
| backrefs, finite-language group | no, after the expansion rewrite | same note |
| atomic groups / possessives | no, after the cut rewrite | companion note |
| lookaround, recursion, conditionals | yes for now | registry `VM_ONLY`; each module's own call when it lands |
| everything in the base + `classes` + `modifiers` tiers | no | today's engines, unchanged |

Row 1 has a subtlety that deserves its own line, because it is the difference
between M4 being free and M4 being a tax on every existing user:

**Captures force the VM only when the CALLER wants capture offsets.** A
pattern with groups whose caller only asks "did it match, and where" is
capture-free work. Today's generated contract has no capture channel at all,
so today every group is in that position (§9.2). The selection input is
therefore not "does the pattern contain `(`" but "does the requested OUTPUT
contain group offsets" — a property of the generation request, not of the
pattern. §12 ASK-5 asks Frank to rule the default: does `pcrec 'a(b|c)+d'`
emit a capture-tracking matcher, or does the caller opt in?

Recommendation (BELIEVED): captures ON by default, matching PCRE2's own
default and the principle of least surprise, with `--no-captures` as the
generation axis that recovers today's code for callers who do not want it. The
hybrid (§6) is what makes that affordable, because the scanning stays on the
DFA either way.

**RULED (D42.1, 2026-08-14):** the recommendation above is adopted exactly
as stated — captures ON by default post-[M4.5]; `--no-captures` recovers
today's pure-DFA artifact. The generated-contract change for group-bearing
patterns lands on the SAME announced D37 boundary as the `rx_span` break
(§9.2(3)).

### 5.4 Zero regression for capture-free patterns

The mechanism is not "the VM is fast enough for them"; it is that they do not
touch any new code. A capture-free pattern takes the same `pcrec_build_nfa` →
`pcrec_build_dfa` → `pcrec_minimize_dfa` → `pcrec_emit_dfa` path, from the
same AST, and emits the same bytes.

The check that this is true is available and should be a gate, not a promise:
**M4.4/M4.5 must assert that the emitted C for the whole existing corpus is
byte-identical to the pre-M4 emitter, modulo the announced `rx_span` break and
the stamp lines.** The precedent is exact: `tests/codegen/run_trie_identity.sh`
already builds a reference compiler behind `-DPCREC_NO_TRIE` and diffs emitted
C, and `tests/cli` case10 already compares past the D37 stamp lines. Both
techniques transfer directly.

### 5.5 Reporting selection (F7)

`--explain` is the wrong home: it takes a CONSTRUCT and answers from the
registry (`cli/main.c:34`, MOD-0.7's query→doorway router). Selection is a
property of a whole PATTERN. Bending `--explain` to accept patterns would
collide with its designed contract for no gain.

The right home is the ARTIFACT, following D37's precedent verbatim
(`emit_feature_comment` / `emit_feature_macros`, `src/gen/emit_dfa.c`):

```c
/* Engine: vm (forced by: capture group at pattern offset 0) */
/* Step budget: 1000000 backtrack resumptions; backtrack frames: 64 */
#define RX_ENGINE "vm"
#define RX_ENGINE_WHY "capture group at pattern offset 0"
```

Comment in both `.c` and `.h`; macros in the `.c` only (the existing rule, so
a `.c` that includes its own `.h` never sees them twice). This satisfies F7 —
selection can say so per-pattern, and the answer travels with the artifact
forever — at the cost of two emitter functions modelled on two that exist.

A pattern-level `--why` / `--explain-pattern` CLI surface is NOT proposed here.
If one is wanted it belongs with DD-8's bring-up tooling (§10), where it can
share the IR dump's plumbing.

**RULED (D43.1, 2026-08-14) — SUPERSEDED as the canonical record.** The
comment/macro shape above stays, but a NEW machine-readable record —
`rx_info` (`match_api_m4.md` §5) — takes over as the CANONICAL one: every
generated artifact's `<prefix>_info` reflects the selected engine (as a
`const char *`, `"dfa"`/`"vm"`) and the step budget as typed `rx_info`
fields, queryable by any tool that links against or reads the artifact,
not just a human reading the `.c`/`.h` source. This section's comments stay
for humans; the `RX_ENGINE`/`RX_ENGINE_WHY` macros above are RETAINED
(PROPOSED-here, this document's own call, since D43.1 leaves it open
whether they survive) rather than dropped, for a reason D43.1's own text
anticipates ("macros where compile-time-useful"): `rx_info` is a
`.rodata` symbol, readable only by LINKING against the artifact or reading
the compiled binary; `RX_ENGINE`/`RX_ENGINE_WHY` are preprocessor-visible
at COMPILE TIME, which is what a `tests/codegen/` structural check (the
same style as the `RX_NCAPS > 1 ⇒ VM` check, §5.7.2) or a build-time
`#ifdef RX_ENGINE` conditional needs — `rx_info` cannot serve that
consumer, since reading a struct field requires the artifact to be
compiled and either run or objdump'd, not merely preprocessed. The two
records are therefore NOT redundant: macros for compile-time consumers,
`rx_info` for link/runtime ones. `RX_ENGINE_WHY`'s free-text forcing
reason has no `rx_info` equivalent and is NOT proposed as one — D43.1
lists "the selected engine" as a member, not the reason, so the WHY stays
comment/macro-only unless a future ruling adds it.

### 5.6 The override

APPROACH §2 says selection is "automatic per pattern (overridable)". The
override is `--engine=dfa|vm|auto`, default `auto`. Its value is diagnostic
(reproduce a bug, measure the hybrid against VM-only) and it is the ONLY thing
that makes SR-8's honest diagnostic reachable (§9.3). `--engine=dfa` on a
VM-forced pattern is a clean refusal, never a silent fallback.

**RULED (D44, ratifying R21 E-6) — `--engine=vm` DISABLES the DFA
prefilter, and this is now the do-or-die comparison mode.** Stated
explicitly here because §3.7's differential depends on it (§3.7's own
GATE annotation): without this, `--engine=vm` could mean merely "prefer
the VM's construction" while the hybrid's prefilter still runs underneath
and hands the VM its anchored window — which would make `--engine=vm`
useless as an independent check (E-6's own finding). `--engine=vm`
therefore means the VM-ONLY search loop (§2.6) unconditionally: no
forward/reverse DFA pass, no anchored-window handoff, a genuinely
independent scan from `startpos`. This is both the R21 panel's own
ratified reading and something Frank independently requested (a plain
`--engine=vm` comparison mode with the prefilter off) for the identical
reason — the two converge rather than one motivating the other.

**RULED (D44.6, ratifying R21 E-7) — `--engine=dfa` on a captures-default
pattern REFUSES, it does not silently imply `--no-captures`.** A prior
gap: `--engine=dfa` was stated above as refusing a "VM-forced" pattern,
but D42.1 makes CAPTURES THEMSELVES (when requested, i.e. by default post
[M4.5]) a forcing condition (§5.3), and this document's own CLAUDE.md
example, `a(b|c)+d`, is exactly such a pattern — so `--engine=dfa
'a(b|c)+d'` must refuse cleanly rather than either (a) silently compiling
a captures-dropping DFA artifact (surprising: the caller asked for
captures by not passing `--no-captures`, and got none) or (b) crashing
into an undefined state. The refusal names `--no-captures` explicitly as
the way to get a DFA artifact for this pattern — "this pattern requires
captures (default); pass --no-captures for a DFA-only artifact, or omit
--engine=dfa" is the shape of the message, D26 tier 2 (pcrec's own
diagnostic, no PCRE2 wording to match). §5.7.3/§9.2 carry the mechanical
consequence.

### 5.7 What a DFA-compiled artifact promises through `caps` — answering `match_api_m4.md` §13 ASK 4

PROPOSED. This is the freeze document's question, assigned here because it is
engine-selection territory; §11.2 sharpens it first.

#### 5.7.1 Sharpening the question

ASK 4 asks what a group-bearing DFA-compiled pattern reports "through
`caps[1..ngroups]` via the retrofitted match-here entry". That framing has a
prior answer that dissolves half of it:

> **The match-here entry reports NOTHING through `caps`, for ANY engine,
> ever.** `rx_ctx.caps` is `const ptrdiff_t (*)[2]` — an INPUT (the outer
> engine's captures-so-far, R-b) — and `rx_matchfn` returns a length. There is
> no capture output channel in the F1 entry at all (§11.2).

So `<prefix>_match` is not where the question bites, and [M4.4] retrofitting
F1 onto a DFA matcher raises nothing: the retrofitted entry returns a length
or `-1`, which the DFA has always been able to compute. The real question is
about the CAPTURE-DELIVERING entry — `<prefix>_search` — and about what
`RX_NCAPS` says.

Worth recording as a convergence rather than a coincidence: [M4.1] reached
this question mechanically (what does [M4.4] emit?) and this lane reached the
same defect from the ABI side (§11.2, written before `match_api_m4.md` was
readable here). Two independent derivations landing on one gap is the
strongest evidence either lane produced that it is real.

#### 5.7.2 The decision — option (c), a refinement of (b)

> **The capture-slot count is a property of the generated ARTIFACT, not of the
> pattern text. `RX_NCAPS` is emitted by the compiler, and the compiler chooses
> the engine before it emits the macro. A DFA-compiled artifact therefore
> always emits `RX_NCAPS 1`.**

Two invariants follow, both stateable in one line and both checkable:

- **`RX_NCAPS > 1` implies the VM engine.** A `tests/codegen/` structural
  check, live from [M4.4] onward, and the cheapest possible guard against the
  whole failure class ASK 4 is worried about.
- **C6 never bends.** "Every pair `0..ngroups` written on a completed match"
  holds exactly, where `ngroups` is the ARTIFACT's `RX_NCAPS - 1`. For a DFA
  artifact that is precisely `caps[0]`, the whole-match span it has always
  computed. There is no interim population with unwritten slots, because that
  population has no slots.

This is `match_api_m4.md`'s candidate (b) with one correction that matters
(§5.3): the routing trigger is **the requested OUTPUT, not the presence of a
`(`**. (b) as literally phrased — "force ANY capturing group onto the VM" —
would move `a(b|c)+d`, a pure scanning pattern, onto a VM artifact
permanently, for every caller who never wanted groups. Under the hybrid the
scanning still happens on the DFA (§6.1), so the cost is bounded, but the
artifact still carries a backtracker it never needs. `--no-captures` (§5.3,
ASK-5) is what keeps that population on a pure DFA forever, and under this
rule the two questions collapse into one: **if the artifact promises
`RX_NCAPS > 1`, the VM must be selected; if the caller asked for no captures,
`RX_NCAPS` is 1 and today's engine keeps it.**

#### 5.7.3 What holds in the M4.4 → M4.5 gap

[M4.4] retrofits the entry, the pair type and the group index onto EXISTING
DFA matchers before the VM exists. In that window:

- `RX_NCAPS` is **1 for every pattern**, capture-bearing or not, because no
  engine can produce more and the macro states what the artifact does.
- `a(b|c)+d` compiles exactly as it does today plus the new entry, the new
  index and the pair type — which is what [M4.4]'s own plan row asks for
  ("the API break lands mechanically... retrofitted onto the EXISTING DFA
  matchers") and what §5.4's byte-identity gate wants to be able to assert.
- **There is no surface for asking for captures yet, and that is deliberate.**
  The capture REQUEST (whatever [M4.5] spells it) and the engine that can
  honour it land in the SAME substep. So no window exists in which a caller
  can ask for something nothing can deliver, and no diagnostic is needed for a
  state that cannot be reached.
- At [M4.5], `RX_NCAPS` for `a(b|c)+d` goes 1 → 2. That is a generated-contract
  change, and it is the SAME item as §9.2(3) (groups start capturing) — so it
  does not add a break, it dates one this document had already flagged.
- **RULED (D44.6, ratifying R21 E-7) — from [M4.5] onward, `--engine=dfa
  'a(b|c)+d'` REFUSES rather than compiling.** In the [M4.4]→[M4.5] gap
  this bullet describes, `--engine=dfa` on this pattern is a no-op (it is
  already the only engine that exists, so there is nothing to refuse
  FROM), which is presumably why the refusal was not flagged earlier in
  this document — the gap window made the question briefly moot. Once
  [M4.5] makes captures the default (D42.1) and the VM exists, the same
  invocation becomes a genuine engine-forcing conflict (§5.6's new
  ruling): the caller asked for captures (by not passing
  `--no-captures`) and separately asked for the DFA engine, and those two
  requests cannot both be honoured. [M4.5] is therefore where this
  refusal must first exist, not merely where `RX_NCAPS` first grows.

**What D40 changes about that last bullet** (ruled after this document's brief
was written): pre-v1, the break carries no compatibility weight in substance
and is governed only in FORM — D37's announced-boundary shape and DD-3's
versioning-event discipline. So the `RX_NCAPS` 1 → 2 change needs an
announcement and a conserved-populations accounting, not a migration path or a
compat shim. The reason to keep it on ONE boundary with the `rx_span` break is
therefore economy of announcements, not compatibility obligation. Post-v1 the
same change would need a compatibility story, which is an argument for landing
the capture contract's shape before that declaration rather than after —
and D40's addendum already routes the as-built contract into `docs/spec/` at
[M4.7]'s close, which is where the `RX_NCAPS > 1 ⇒ VM` invariant (§5.7.2)
should be written down as a contract line rather than only as a codegen check.

**RULED (D42.1, D42.2, 2026-08-14):** both outstanding pieces of this
section are now confirmed rather than proposed. D42.1 adopts §5.3's
captures-ON-by-default recommendation, which is what makes the `RX_NCAPS`
1 → 2 transition above a REAL event for `a(b|c)+d` specifically (not just
for callers who explicitly opt in) — `--no-captures` is the only way to
keep an artifact at `RX_NCAPS 1` past [M4.5]. D42.2 confirms §5.7.2's rule
itself (ASK-12): the artifact-property framing, the `RX_NCAPS > 1 ⇒ VM`
invariant, and "C6 never bends" all stand as stated, with no amendment.
`match_api_m4.md` folds this into its own §2.1 in the same amendment
round.

#### 5.7.4 Why candidate (a) is rejected

(a) is "leave `caps[1..]` at `RX_UNSET` until selection routes the pattern to
the VM, under-promising C6 for the interim population". Three reasons, in
increasing order of severity:

1. **It makes `RX_UNSET` permanently ambiguous.** A reader of a shipped
   artifact could not distinguish "group 3 did not participate in this match"
   from "this engine does not do groups". The sentinel's whole value is that
   it means one thing.
2. **It puts an asterisk on C6 that outlives the interim.** The freeze
   document is trying to state C6 without one, and a contract weakened for a
   population that will be empty in one substep is a permanent cost for a
   temporary reason.
3. **It has a concrete downstream miscompile-shaped consequence.** D38 ruled
   subst Q3: an unset-but-existing group renders EMPTY by default. So a
   template `$1$2` against an (a)-style artifact renders two empty strings and
   reports success — silently wrong output, no diagnostic, from a matcher that
   is behaving to its stated contract. That is exactly the "never miscompile"
   line the project's compatibility standard draws, reached without anyone
   writing a bug.

Under §5.7.2 none of this is reachable, because a matcher that cannot fill a
slot never advertises one.

---

## 6. The DFA-prefilter hybrid and DFA islands

### 6.1 The exactness claim

APPROACH §2 describes the whole-pattern prefilter as "an over-approximating
DFA (backrefs → their referenced sub-pattern, lookarounds dropped) that cannot
false-negative". For the M4 tier that description is too weak, and the
stronger truth is what makes the hybrid nearly free:

> **CLAIM, MARK SPLIT (RULED D44, ratifying R21 E-1).** For a pattern whose
> only VM-forcing feature is capturing groups — no backrefs, lookaround,
> callouts, `\K`, atomic/possessive, `\G` — the capture-erased pattern has
> the same language (**STRUCTURAL, held**) AND the same leftmost-first
> match span for every subject and startpos (**BELIEVED-WITH-GATE, NOT
> held unconditionally — see below**). The prefilter is EXACT for the
> erasure half; the span-equality half needs the gate §3.7 now provides.

**The panel found a live counterexample to the span-equality half.** The
claim above was marked STRUCTURAL in full until the R21 panel ran this
document's own §13 P-1 probe and found K17
(`../dev/known_issues.md`) — a REAL, shipped DFA priority miscompile:
`(?:b*?(?:a*)*)*` on `"ab"` returns `[0,2)` from pcrec's DFA where both
python and PCRE2 (the ruled leftmost-first standard, D3/D26) give
`[0,1)`. The family that reproduces: a lazy nullable prefix, a nested
nullable star, and an outer star (`(b*?(a*)*)*`, `(b*?(a*)+)*`,
`(b??(a*)*)*`, and their close relatives); it does NOT reproduce with a
non-nullable inner body, no outer star, or a greedy prefix (910/910
random-sweep agreement holds on that wider neighbourhood). K1's residue —
a prior fix in the same neighbourhood did not fully close it.

**Why this splits the mark rather than refuting the whole claim.** K17 is
a bug in the DFA's PRIORITY CONSTRUCTION (the machinery that decides
which of several accepting paths is leftmost-first-preferred), not in the
ERASURE (whether `(a|b)` and `(?:a|b)` build the same automaton — D31's
STRUCTURAL fact, untouched, still true by inspection of
`src/core/internal.h:41`'s `AKind` enum). A capture-only pattern in the
K17 family gets the WRONG span from the DFA itself, entirely independent
of whether captures are erased — so the bug is not evidence that erasure
perturbs anything; it is evidence that the underlying automaton pcrec
ships today already computes the wrong span on this family, which the
hybrid would then faithfully hand to the VM as its anchored window,
propagating the error rather than causing it.

**Disposition (D44.4): FIX-CODE, before [M4.4], as a dedicated lane
independent of M4.** K17 is a shipped miscompile in the DEFAULT engine,
so it is fixed on its own schedule, not folded into M4's captures work —
recorded as oracle-verified corpus tests (the K17 family) plus the
three-way pcrec/python/pcre2 rule (§3.6's re-scope) plus the full battery.
Once fixed, this claim's mark reverts to STRUCTURAL in full; until then,
§3.7's differential is the load-bearing GATE (its own RULED annotation)
that must pass before [M4.5]/[M4.6] may rely on span-equality for a given
pattern family, and `--engine=vm` (§5.6's RULED note) is how that gate
runs independently rather than tautologically.

Why the erasure half stays STRUCTURAL rather than BELIEVED: the erasure is
not a transformation this design proposes. It is what the parser does
today. `(a|b)` and `(?:a|b)` produce the identical `Ast` (§1.2, D31 — the
erasure STAYS), so the DFA built for the capture pattern IS the DFA built
for the erased pattern. There is no approximation step to be wrong about.

**Consequences, in order of importance:**

1. The existing forward+reverse DFA pair hands the VM an EXACT anchored window
   `[start, end)`. The VM's entire job is filling in group offsets inside a
   span it already knows.
2. The VM never scans the subject. D18's speed mandate is honoured on the axis
   that matters (long-text throughput) by the engine that already honours it.
3. §4.7's cliff guard works: the prefilter answers `nomatch` for `(a*)b`
   before the VM exists in the execution.
4. §3.7's internal differential is available for free.
5. M4.6's hybrid is cheap to BUILD: no new machine, no new analysis. The only
   new cost is a second `pcrec_build_nfa` call per capture pattern (the
   unwrapped, capture-preserving one the VM lowers from).

### 6.2 The honest limits of the hybrid

Three, and the panel should hold this section to them:

**(a) The win is bounded by the span/subject ratio.** "The VM runs only on a
small candidate window" is APPROACH's phrasing and it is not always true. Of
the nine existing bench cases, case (f) matches `[0, 8388608)` and case (h)
matches `[0, 1048576)` — span/subject = 1.0. For those shapes the hybrid means
the VM re-walks the whole subject after the DFA already walked it twice. The
hybrid is a WIN on selectivity, not a universal one, and §8 leans on this.

**(b) Short subjects may lose.** Bench case (i) is the 60-byte latency regime
where per-call overhead dominates; running two DFA passes before a VM pass
over 60 bytes is plausibly slower than VM-only. The seam should exist for a
runtime `if (n < RX_HYBRID_MIN)` branch selecting VM-only, with the threshold
MEASURED at M4.6 and possibly zero. Designed now, decided by measurement.
§12 ASK-6.

**(c) Callout patterns.** D36 rules fire-point discipline "engine-relative"
and cites PCRE2's own requirement of `PCRE2_NO_START_OPTIMIZE` for predictable
callout invocation — so a prefilter that skips start positions and thereby
changes callout fire counts is EXPLICITLY permitted. Recommendation: apply the
prefilter to callout patterns uniformly rather than adding a per-pattern axis
for it (D18: an axis must earn itself, and this one has no customer). Document
the fire-count consequence at the callout module's landing.

### 6.3 DFA islands

APPROACH §2 defines three strengths. What M4 does with each:

| Strength | M4 disposition |
|---|---|
| **1. Exact islands** — fragments auto-possessification proves atomic in context (`[^"]*` before `"`) | **DESIGNED AND SCHEDULED (M4.6).** DFA and backtracking semantics coincide, so the island emits a plain table loop with one answer and pushes no frame. This is the hot case (`.*`, class repeats, alternation tries) and it is also what keeps the trail and frame arrays small. |
| **2. Accept-list islands** — monotone-preference fragments, one scan recording accepting positions | **DEFERRED, with reasons.** They need a separate NON-pruning DFA per fragment (R1 A-1: the D3 pruning machine prunes exactly the threads the list needs, so it cannot be reused), memory gated by max-match-length analysis, and the R1 A-1 monotonicity proof per fragment. That is a milestone's worth of work, none of it needed for the captures slice to be correct. |
| **3. VM fallback** | Everything else, including any fragment containing a capture group — islands SPLIT at capture boundaries in v1 (tagged automata are the later upgrade APPROACH already names). |

**Seams, named concretely because the brief asks for real ones, not imagined:**

- Fragment → NFA: `pcrec_build_nfa` on the sub-AST. Exists.
- NFA → DFA: `pcrec_build_dfa` with `prune` true for exact islands. Exists.
- Minimization: `pcrec_minimize_dfa`. Exists.
- Emission: the five table emitters in `emit_dfa.c` (§2.8), which must move
  behind a gen-internal header. Their output is already a function-local
  `static const` block, which is precisely what an island inside the VM
  function needs — no shape change.
- The auto-possessification analysis that PROVES an island exact does NOT
  exist. It is named in APPROACH §5 ("VM-level: atomic-group/possessive
  inference where backtracking provably can't help") and it is the one real
  piece of new analysis M4.6 owes. Its cheap and complete-enough first
  version is the disjoint-follow special case the atomic-groups design note
  already describes as "free in both directions": `a*b ≡ a*+b` when nothing
  that can follow the loop can start with an `a`.
- **Islands may not span a callout call point** (ABI §2: the callee is opaque,
  atomic and un-fusable). Call points partition the pattern into island
  candidates. Structural, cheap, and it is the whole of what the callout ABI
  imposes on the island design.

### 6.4 What is designed now vs deferred to M4.6 measurement

| Item | Status |
|---|---|
| Prefilter = existing forward+reverse pair, exact for capture-only | designed, §6.1 |
| Prefilter-before-VM ordering rule | designed, §4.7 — this one is a correctness-of-expectation rule, not a tuning knob |
| Exact islands + disjoint-follow possessification | designed, built M4.6 |
| Short-subject threshold `RX_HYBRID_MIN` | seam designed, value MEASURED at M4.6 |
| Accept-list islands | deferred, §6.3 |
| Tagged automata (islands spanning captures) | deferred beyond M4 |
| Trie-factored alternation emitting a first-byte switch with no pushes | deferred to M4.6, measured |

---

## 7. DD-7 — engine unification ownership

The row carries three separate things. They get three separate answers.

### 7.1 Which machine becomes the capture prefilter

**Both of them, unchanged.** The forward pruning DFA gives the leftmost-first
match END (D3/D7); the reverse non-pruning DFA gives the match START. Together
they are the exact anchored window of §6.1. No new machine is built, neither
existing machine is modified, and the answer is the same for `ENG_UNANCH` and
(for `^` patterns) `ENG_ATTEMPT`, which already produces a span.

This is a smaller answer than the row anticipates, and the reason is §6.1: for
the captures tier there is nothing to approximate, so there is nothing to
design.

### 7.2 ENG_UNANCH / anchoring absorption

MEASURED history: D8 (M2.7) moved `$` onto `ENG_UNANCH`; `^` stayed on
`ENG_ATTEMPT` because the reverse machine has no position-dependent BOT
variant (checked at `pp == 0`), and D8 records the remaining slow shape as
"`^` on only SOME branches" (`(^a|b)c`).

**Recommendation: M4 does NOT own this, and it should stop being unowned.**

- It is pure DFA-engine work with zero interaction with captures, the VM, or
  the hybrid. Taking it into M4 is scope creep on the milestone that is
  already the largest.
- It has **no measured loss today**: the nine-case bench matrix contains no
  `^` pattern at all. Scheduling engine work whose benefit has never been
  measured inverts D12/D15's discipline ("every optimization needs a bench
  case that exercises it").
- Therefore: re-home the absorption half of DD-7 to a named DFA-engine row,
  and make its PRECONDITION that [BENCH-1] add a `^`-on-some-branches case so
  the loss is measured before the work is scheduled. §12 ASK-8.

**What M4 does contribute to it:** §5's selection pass replaces the inline
`nfa_has_bot()` test. After M4 the absorption work is a change to ONE analysis
in one file rather than an `if` in the pipeline driver — which is the whole
reason to build a socket instead of a second `if`.

### 7.3 DD-4's note: `nfa_wrap_unanchored` bakes in the self-loop with no toggle

Confirmed, STRUCTURAL: `src/core/compile.c:124` calls
`nfa_wrap_unanchored(&cx, &cx.job->nfa)` which mutates the NFA in place; there
is no way to recover the anchored machine from the wrapped one
(`src/ir/nfa.c:590`).

For M4 this costs nothing, because the answer is already in the pipeline's
shape: `pcrec_build_nfa` is called TWICE today (forward and reversed) from the
same AST. A capture pattern calls it a third time, unwrapped, for the VM to
lower from. Cost: one extra NFA build per capture pattern, at pcrec's own
compile time, measurable and small.

For DD-4 (`\G`) the note stands unchanged: `\G` wants the unanchored engine's
SHAPE without the self-loop, which is a toggle on the wrap, not a rebuild.
M4 does not deliver that toggle and does not need it. Recorded so DD-4's owner
does not read §7.3 as already-solved.

---

## 8. DD-9 — case (f), decided

### 8.1 The measurement, restated with its source

MEASURED, `tests/bench/compare/results-ubuntubudu-20260811-2.md` (quiet box,
pinned, median of 5, spreads 1.01–1.02x):

| engine | case (f) `[01]*1[01]{8}`, 8 MB random 0/1 | ratio |
|---|---|---|
| pcrec | 158.765 MB/s | 1.00 |
| pcre2-interp | 1049.168 MB/s | **6.61x faster than pcrec** |
| python-re | 639.547 MB/s | 4.03x |
| pcre2-jit | 213.467 MB/s | 1.34x |

It is pcrec's worst cell in the matrix by a wide margin, and the row is right
that no milestone owns it.

### 8.2 The decision

> **The DFA-prefilter/VM hybrid does NOT own case (f), and structurally
> cannot.**

The reasoning is one line: `[01]*1[01]{8}` is **capture-free**. Per-pattern
selection (§5) keeps it on `ENG_UNANCH`; the VM is never constructed for it;
the prefilter is a thing that runs BEFORE a VM that does not exist. Every
piece of M4 machinery is inert on this pattern by design, and that inertness
is the same property §5.4 sells as "zero regression".

Making M4 own it would mean building a DFA-engine throughput optimization
inside the captures milestone, justified by a case the captures milestone never
touches. That is precisely the kind of milestone-boundary erosion the plan's
queue discipline exists to prevent.

### 8.3 Where it belongs instead

**Own it at [BENCH-1] → OPT wave 1 (D21: algorithmic first).** [BENCH-1]'s
stated purpose is to produce a cross-engine relative ranking whose output is a
worst-first worklist, and Frank's recorded optimization workflow is "work the
prioritizer list from the relative worst downward". Case (f) at 0.151 is that
list's known head. DD-9 does not need a new home so much as it needs to stop
being a floating row: it should be re-tagged as the first entry of the
prioritizer's worklist, with the three findings below attached so the work
does not start from zero.

### 8.4 Three things this design established about case (f)

**(i) Computed goto is the WRONG lever, contra the row's own hint.** The DD-9
row says to "note that the D13 correction makes computed goto a MEASURED win
for predictable transition sequences". It does — and case (f) is the opposite
regime. ~~The DFA of `[01]*1[01]{8}` is a 9-bit shift register over a
two-symbol alphabet~~ — **CORRECTED (D44, ratifying R21 E-8): the BUILT
DFA measures 768 forward states over 3 equivalence classes, not the
naive 512-states/2-classes a bare "9-bit register, two symbols" reading
implies.** `2^9 = 512` is the state count a pure bit-shift-register
abstraction would have, and `{'0','1'}` is a two-symbol reading of the
alphabet — but the ACTUAL construction adds a THIRD equivalence class (a
"reset" class covering every byte that is neither `0` nor `1`, which
resets the run rather than shifting it — the pattern's subject alphabet
is bytes, not bits, and any non-`0`/`1` byte is a real, distinct
transition the naive picture omits), and the extra bookkeeping states
this reset class needs push the count from 512 to 768. The hypothesis
this subsection argues for SURVIVES the correction: its state IS still
effectively the last nine input symbols (the reset class only adds a
"how did we get here" refinement, not a different KIND of dependency),
and the input on the all-`[01]` bench subject is still random bits, so
the maximally-UNPREDICTABLE-transition argument below is unaffected by
which exact numbers describe the automaton. That is D13's
measured 2.5x LOSS regime (144 vs 374 MB/s on random bytes), not its 0.28 win
regime. D13's own sentence — "the predictable case is largely what the skip
loops already cover" — already implied this. Falsifiable: §13 P-4.

**(ii) pcrec pays two passes where pcre2-interp pays about one.** The match is
`[0, 8388608)` — the entire buffer — so the reverse start-finding scan
re-walks all 8 MB after the forward scan already did. Meanwhile pcre2-interp's
shape on this pattern is one greedy class-scan to the end plus a nine-character
backtrack. Structural, and it puts a floor under how much any dispatch tuning
can buy: about 2x of the 6.61x is the pass count. Prediction and instrument:
§13 P-5.

**(iii) The algorithmic candidate is bit-parallelism, and it is detectable
from the constructed DFA rather than from the pattern text.** A DFA whose
states correspond exactly to the last *k* input symbols over a small alphabet
is a shift register, and shift registers admit a shift-and (Baeza-Yates–Gonnet)
formulation: `w = ((w << 1) | bit) & MASK` plus a bitmap accept test — an ALU
dependency chain instead of a table-load dependency chain, per byte.
**SOFTENED (D44, ratifying R21 E-8) — the "L1 load" framing overstated the
table's cost.** A 768-state × 3-class transition table (the corrected
count from (i) above) is on the order of 4.6 KB — comfortably
L1-RESIDENT on any target this project plausibly runs on, so the table
lookup itself is not paying a cache-miss penalty the shift-and
alternative would avoid. The win this subsection argues for is real but
narrower than "avoids an L1 load": it is about the DEPENDENCY CHAIN
(each table lookup depends on the previous state, an inherently
sequential load-use chain, versus shift-and's ALU-only chain, which a
modern out-of-order core can pipeline more aggressively) and about
avoiding the UNPREDICTABLE-BRANCH cost D13 measures for computed-goto
dispatch on this transition pattern — not about cache residency, which
the table already has. BELIEVED, and named here so the OPT wave has a
hypothesis rather than a survey. The detection is a property of the
built machine (does the transition function factor as a shift?), which
means it can be a `src/opt/` pass with no parser or IR change.

### 8.5 What M4 DOES owe DD-9: a non-regression floor

M4 must not make the dense/counting family WORSE. `([01]*)1([01]{8})` is the
capture-bearing sibling; §6.2(a) says the hybrid's win is bounded by the
span/subject ratio, and here that ratio is 1.0 — so the capture version pays
the two DFA passes PLUS a full VM pass over 8 MB.

Obligation on M4.6: add the capture-bearing dense/counting case to the bench
matrix and set an absolute floor for it under D12/M2.11's discipline (absolute
per-case floors, not cross-engine ratios). It is the case most likely to
embarrass the hybrid, which is exactly why it belongs in the gate.

---

## 9. SR-8 — the lowering-time refusal, and what actually flips

### 9.1 The row's premise, checked

SR-8 says: today `\1` is rejected by the PARSER as "requires module
'backrefs'", but backrefs parse fine and simply cannot LOWER to a DFA; when
M4's VM exists the honest diagnostic becomes "requires the VM engine", a
lowering-time check against the registry's `engines` column.

The premise is half right, and the half that is wrong makes SR-8 SMALLER than
it reads. Checked against `src/parse/registry.c` (STRUCTURAL):

- `grep -c VM_ONLY src/parse/registry.c` reports ~52 non-`#define` source
  lines against ~33 for `ANY_ENGINE` (approximate: some rows wrap across
  lines and one occurrence is inside a row-building macro, so read these as
  magnitudes, not a census).
- Every `VM_ONLY` row's module is one of `backrefs`, `lookaround`,
  `named_groups`, `atomic_groups`, `recursion`, `conditionals`, `assertions`
  (for `\K`), `verbs`, `callouts`. **None of those modules has a producer.**
  Implemented producers today are `classes` (`mod_classes.c`) and `modifiers`
  (`mod_modifiers.c`); `unicode-props` is recogniser-only (MOD-0.6, by design
  — `design_notes_mod06.md` §8.2), and `mod_verbs.c` says so about itself in
  its own header ("Building an aport/PORT_FN here would wire a PRODUCER…";
  "if a future slice needs a producer, the seam to extend is
  `verb_rows[0]`"). **RULED (D44, ratifying R21 E-9) — the census GAINS
  `branch_reset`** (`(?|...)`, `src/parse/registry.c:547`), missed by the
  original `VM_ONLY` grep because it is module-gated under a name the
  grep's magnitude count did not individually verify. It has no producer
  either (same population as the rest of this list), so it changes the
  COUNT this bullet's magnitudes describe but not the CONCLUSION below.

> **Therefore: when the VM exists, ZERO currently-refused constructs become
> compilable.** Every `VM_ONLY` construct is refused on the MODULE axis, and
> its module — not its engine — is what is missing. `\1` keeps saying
> "requires module 'backrefs'" after M4, and that answer stays correct.

### 9.2 What DOES change

1. **The `engines` column becomes CONSUMED.** It is currently design intent
   that nothing reads (`src/parse/registry.c:82`, `internal.h:779`); §5's
   selection pass is its first consumer, and the conformance test's
   "well-formed only" assertion can be strengthened to agreement with the
   selection pass's own verdicts.
2. **A SECOND refusal class appears, on a different axis.** Module refusal
   ("requires module 'X'") and engine refusal ("construct X requires the VM
   engine, which `--engine=dfa` excludes") are orthogonal, and they must be
   spelled differently or the diagnostic lies. The engine refusal is reachable
   ONLY through the §5.6 override, because `auto` always picks an engine that
   can compile the pattern. That is the honest scope of SR-8's flip: it makes
   the override's refusal expressible, and nothing else. **RULED (D44.6,
   ratifying R21 E-7) — the engine-refusal population is LARGER than
   "`VM_ONLY` construct under `--engine=dfa`."** §5.7.3's own new bullet
   above records the second trigger: a captures-DEFAULT pattern (any
   group-bearing pattern, post-[M4.5], with `--no-captures` not passed)
   under `--engine=dfa` refuses too, even though the pattern uses no
   `VM_ONLY` construct at all — the forcing condition is "captures were
   requested" (§5.3's routing rule), not "the registry says `VM_ONLY`".
   Both triggers share one mechanism (the §5.6 override making an
   otherwise-`auto`-avoided conflict reachable) and one diagnostic shape
   (D26 tier 2, naming the actual conflict), but a reader should not
   conflate "SR-8's flip" with "every reason `--engine=dfa` can refuse" —
   SR-8 is the `VM_ONLY`-registry half specifically.
3. **A behaviour change to a currently-compiling construct** — which SR-8's
   row does not mention and which is bigger than everything in it.
   `build/pcrec -p rx 'a(b|c)+d'` compiles TODAY (it is the CLAUDE.md example)
   and emits a matcher with NO capture output, because groups are erased. If
   §5.3's recommendation is adopted, the same invocation after M4 emits a
   capture-tracking matcher with a different generated API. That is a
   generated-contract change on top of the `rx_span` break, both landing at
   the same D37-announced boundary — and it should be announced as one
   boundary with two items, not discovered as a surprise by whoever ports
   first. §12 ASK-5 is the ruling that decides it.
4. **The refusal MOVES from parse time to lowering time** for the module axis
   too, eventually — but that is a diagnostic-position change with a
   diagnostic-position cost: `--count-groups` and every reject-table offset
   pin depend on WHERE the leftmost refusal fires (`tests/reject/`,
   `pcrec_count_groups`'s "refusal behaviour is pcrec_compile's exactly").
   Recommendation: SR-8 moves ONLY the engine-axis check to lowering and
   leaves module-axis refusal exactly where it is. Moving both is a
   re-baseline of the reject suite for no user-visible gain, and D26 tiers
   diagnostic position well below what a pattern matches.

### 9.3 The flip, as a work item

Small, and it can ride M4.7 as the row already schedules:

- Selection consults `RegRow.engines` for every construct the pattern used.
- With `--engine=auto`, a `VM_ONLY` construct whose module exists selects the
  VM. No diagnostic.
- With `--engine=dfa`, it refuses, naming the construct, its offset, and the
  engine — a new diagnostic string, D26 tier 2 (pcrec's own convention), not
  a PCRE2 message to reproduce.
- The registry conformance test gains a both-directions check: every row whose
  module has a producer and whose `engines` is `VM_ONLY` must be selectable
  under `auto` and refused under `dfa`. That check is empty today and becomes
  non-empty at the first VM_ONLY module, which is the shape the project
  prefers to shipping a check with no population.

---

## 10. DD-8 — `--emit-ir` / `--emit-dot` as bring-up tooling

One paragraph, as the brief scopes it. A VM emitter is harder to debug than a
DFA emitter for a specific reason: a DFA's correctness is visible in a
transition table a human can read, while a backtracker's correctness is a
sequence of decisions over time. So the useful dump for VM bring-up is not the
automaton picture DD-8's name suggests — it is a listing of the emitted
PROGRAM (labels, choice points with their preference order, capture slot
assignments, island boundaries, callout call sites) alongside, optionally, a
trace of resume-frame pushes and pops for one subject. That is genuinely
useful during M4.5 and it is genuinely filler: nothing in this design depends
on it, and it should be scheduled only when a lane is otherwise idle. One
constraint if it is built: the dump must be derived from the same structure
the emitter walks, never from a parallel description — a second source of
truth for "what the VM does" is worse than no dump.

---

## 11. Tensions with the ruled ABI, reported not resolved

These are the three places where engine reality pulls against D38/D39. Per the
brief, they are findings, not things this document silently fixes.

### 11.1 `rx_matchfn` has no room for "the engine gave up"

D38.4 freezes the return space: `>= 0` length, `-1` fail, `< -1` reserved and
`__builtin_trap()`-enforced at call sites. DD-2's budget and §4.5's frame
overflow are neither a length nor a no-match; they are a third outcome.

§4.4 keeps the freeze intact by putting the honest code on `rx_search`, whose
negative space is untouched by D38. The residual is real and narrow: **a
compiled matcher used as a callout cannot tell its caller it gave up.** It
reports `-1`, the outer engine treats the path as failed, and the outer match
may then report a WRONG RESULT (a match found on a different path, or no
match) where the truthful answer is "unknown".

That is a correctness-of-reporting hole, not a crash, and it is confined to
the composition path, which has no users in v1. Recommend accepting it in v1
and recording it. §12 ASK-2 is the amendment if Frank prefers to close it now.

**RULED (D42.3, 2026-08-14):** the recommendation is accepted — the -1-only
give-up stands, the `< -1` reservation stays intact and untouched, and this
residual is explicitly confined to the composition path, which has no
users. Re-open when a composition customer appears (cheap pre-v1 per D40).
`<prefix>_search`'s own negative space (RX_ERR_STEPS/RX_ERR_FRAMES) is a
separate, unaffected mechanism — see §4.4's own distinction and
`match_api_m4.md` §1's amendment.

### 11.2 `rx_matchfn` cannot deliver captures, so match-here is not the capture primitive

F1 calls the anchored match-here entry "the primitive", and F2 requires it to
accept `ncap = 0, caps = NULL`. But `rx_ctx.caps` is `const ptrdiff_t (*)[2]`
— it is an INPUT (the outer engine's captures-so-far, per R-b) — and the
return value is a length. **There is no output channel for the matcher's own
captures in `rx_matchfn` at all.**

This is internally consistent with D38.5/F5 (captures are opaque OUT of a
composed matcher), so it is not a contradiction. But it means:

- A capture-consuming caller cannot use the F1 entry. The capture-delivering
  entries are `rx_search` and, if M4.1 defines one, an anchored
  capture-delivering sibling.
- "Search wraps match-here, the anchored entry is the primitive" is true
  STRUCTURALLY (§4.4's three layers) but the shared primitive is the INTERNAL
  `rx_match_impl(ctx, w)`. The exported `rx_matchfn` is a capture-dropping
  façade over it. That costs nothing and satisfies F1/F2 exactly — but the
  freeze document should say which entry a capture-consuming caller uses, and
  today no document does.

**Handed to [M4.1]:** does an anchored capture-delivering entry exist, and
what is it called? `match_api_m4.md` §7's symbol table names `<prefix>_search`
and `<prefix>_match` and no third entry, so a caller who knows the start
offset and wants groups (the substitution compiler's likely shape, and anyone
doing tokenisation) has nothing to call. `<prefix>_match_caps` or an extra
argument on a sibling entry — [M4.1]'s pick, but the gap should not survive
the freeze.

**Independently reached from the other side.** `match_api_m4.md` §11 item 7 /
§12.8 / §13 ASK 4 arrives at the same defect by asking what [M4.4] should
emit for a group-bearing DFA pattern's `caps[1..]` "via the retrofitted
match-here entry" — a question whose premise is that the entry has a `caps`
output. It does not. §5.7.1 sharpens the question on that basis and §5.7.2
answers what remains of it.

### 11.3 D31 rejected the AST node that captures now need

D31 RULED that the group node stays erased, and rejected an `A_GROUP` wrapper
after MEASURING its cost: 15x on pcrec's own compile time for a 300-branch
shared-prefix alternation, and only where a group wraps a PROPER SUB-RUN of an
outer alternation (a whole-alternation wrap sits above the spine; a
pass-through recurses).

M4 needs SOME node — the VM must know where to emit `RX_SET`. Three things
make this a manageable tension rather than a reversal, and the third is the
one that needs measuring:

1. **D31's rejection was scoped to its reason.** Candidate A was rejected as a
   node built to recover a top-level branch count that `p_alt` already
   computed — a node with no customer. Captures are a customer. D31's
   "revisit when" list does not name this case, so this is new ground rather
   than a contradiction.
2. **Only CAPTURING groups get a node.** `(?:...)` stays erased, and a
   capture-free pattern's AST is byte-identical to today's — which is what
   §5.4's byte-identity gate would prove.
3. **The measured cost may still bite, in a new place.** The 15x was in
   NFA/trie construction over a shared-prefix alternation, and capture
   patterns still build a prefilter DFA through exactly that path (§6.1). So
   `((a)|b|c|...×300)` could pay it. **This is not resolved here.** §12 ASK-9
   asks for D31's own measurement re-run with capture nodes present before
   M4.5 commits to a node shape; if it reproduces, the mitigation is that the
   PREFILTER can be built from the capture-ERASED AST (which is what it is
   semantically anyway, §6.1), leaving capture nodes only on the VM's own
   lowering path where no trie factoring runs.

That mitigation is probably the answer, and it is pleasingly clean: **two
lowerings from one parse — the erased one for the prefilter, the annotated one
for the VM.** But it should be adopted on a measurement, not on this
paragraph.

---

## 12. ASKs

Numbered so the panel and Frank can answer them individually. Every one of
these is something this lane could not settle from existing evidence; none was
run, per the docs-only scope.

**Measurements wanted (nobody should run these until a lane owns them):**

- **ASK-1 — the python-`re` / PCRE2 capture disagreement surface.** A probe
  (`tests/probes/`, D35 archived output) over empty-iteration and
  repeated-group capture cases: `(a*)*`, `(|a)+`, `(a|b)*`, `(a)*`, `(a)?`
  against subjects that exercise suppressed iterations, comparing python
  spans against libpcre2 ovectors. **Prediction: they disagree on at least
  one case, and the disagreement is in the empty-iteration family.** Wanted
  BEFORE M4.5 writes the capture corpus, because the exclusions must exist
  before the expectations do.
  **RULED (D44, ratifying R21's E-ASK-1 refutation, 2026-08-14): the
  prediction is REFUTED.** The panel ran this exact measurement (225,240
  generated pairs + 53 targeted empty-iteration cases): ZERO python/PCRE2
  disagreements. §3.6's oracle-exclusion mechanism is therefore RE-SCOPED
  rather than built as originally planned — see §3.6's own RULED
  annotation for the three-way replacement rule and why an exclusion
  mechanism built on this (wrong) prediction would have hidden K17 (§6.1).
- **ASK-6 — `RX_HYBRID_MIN`.** The subject length below which hybrid (two DFA
  passes + one VM pass) loses to VM-only. Bench case (i)'s 60-byte regime is
  the target. **Prediction: the threshold is nonzero and small — low hundreds
  of bytes.**
- **ASK-7 — VM compile-time scaling.** gcc's time on the emitted VM as a
  function of pattern size, against R1 A-3's measured DFA curve (2048 states →
  63 s, 8192 → DNF). **Prediction: linear, and nowhere near the DFA curve,
  because label count is linear in the pattern.**
- **ASK-9 — D31's candidate-A cost, re-run with capture nodes.** The
  300-branch shared-prefix alternation with a capture wrapping a proper
  sub-run. **Prediction: it reproduces, at which point §11.3's two-lowerings
  mitigation is adopted.**
- **ASK-10 — case (f)'s pass split.** Instrument the forward and reverse
  scans separately. **Prediction: the reverse pass is ~half the total, so
  about 2x of the 6.61x gap is pass count** (§8.4(ii), §13 P-5).

**Rulings wanted from Frank:**

- **ASK-2 — does DD-2 get `-2`?** D38 reserved everything below `-1` on
  `rx_matchfn` for a future abort semantic, trap-enforced. §4.4 avoids needing
  it; §11.1 is the residual cost. Amending would mean `-2 = RX_STEPS`, F2's
  call-site check becoming `if (ret < -2) __builtin_trap();`, and a defined
  propagate-or-fail rule. **Recommendation: do NOT amend, on the merits — not
  on the cost of amending.** The distinction matters now that D40 is ruled:
  pre-v1 the break itself is free (compat carries no weight, only D37's
  announcement FORM), so "re-opening a freeze item is expensive" would have
  been a bad reason and is withdrawn. The good reason is that the reservation
  should be spent when a real customer appears, and the residual hole is
  confined to a composition path that has none. If a composition customer
  arrives before v1, amending is cheap and this ASK should simply be re-opened
  then.
  **RULED (D42.3, 2026-08-14): the reservation is kept intact, no amendment
  — the recommendation is adopted exactly. See §11.1's own amendment.**
- **ASK-3 — `rx_ctx.caps` lifetime joins the freeze.** "Valid for the
  duration of the call; the engine rewrites the storage afterwards" is a
  contract line F1–F8 does not carry and a callout author will otherwise
  guess wrong. Recommendation: add it to the F-list at M4.1.
  **RULED (D42.5, 2026-08-14): adopted — the line joins the F-list.**
  `match_api_m4.md` §4 carries the applied text.
- **ASK-4 — DD-2's row names TWO bounds.** Step budget AND backtrack-frame
  capacity (§4.5). They are different failures with different diagnoses and
  the row currently names only one.
  **RULED (D42.6, 2026-08-14): adopted — DD-2's row is amended to name
  both bounds.**
- **ASK-5 — are captures ON by default?** Does `pcrec 'a(b|c)+d'` emit a
  capture-tracking matcher after M4, or must the caller opt in? This decides
  §5.3's selection input and §9.2(3)'s announced-boundary content.
  **Recommendation: ON by default** (PCRE2's own default; least surprise),
  with `--no-captures` as the generation axis recovering today's code. The
  hybrid is what makes it affordable.
  **RULED (D42.1, 2026-08-14): ON by default, exactly as recommended.**
  See §5.3's and §5.7.3's own amendments.
- **ASK-8 — re-home DD-7's absorption half** out of M4 to a named DFA-engine
  row, gated on [BENCH-1] adding a `^`-on-some-branches case first (§7.2).
  **RULED (D42.7, 2026-08-14): adopted — re-homed to [ENG-ABS], gated on
  [BENCH-1] adding the `^`-on-some-branches case first; no measured loss
  exists today, and scheduling unmeasured engine work would invert
  D12/D15. The capture-prefilter half of DD-7 stays answered by §7.1,
  pending the panel.**
- **ASK-11 — DD-9's re-tagging.** Accept §8's decision and re-tag DD-9 as the
  head of [BENCH-1]'s prioritizer worklist, carrying §8.4's three findings, so
  it stops being a floating unowned row.
  **RULED (D42.8, 2026-08-14): adopted — DD-9 archives (decided per §8);
  case (f) becomes the known head of [BENCH-1]'s prioritizer worklist,
  carrying §8.4's three findings.**
- **ASK-12 — confirm §5.7's answer to `match_api_m4.md` §13 ASK 4.** Capture
  slot count is an ARTIFACT property; a DFA-compiled artifact emits
  `RX_NCAPS 1`; `RX_NCAPS > 1` implies the VM; the M4.4→M4.5 window has
  `RX_NCAPS 1` everywhere and no capture-request surface. This is the freeze
  document's candidate (b) corrected so the routing trigger is the requested
  OUTPUT rather than the presence of a `(` — so it is answered jointly with
  ASK-5, and answering ASK-5 "opt-in" rather than "on by default" does not
  change §5.7's rule, only which patterns land on which side of it.
  **RULED (D42.2, 2026-08-14): CONFIRMED, exactly as §5.7 states.** See
  §5.7.3's own amendment; `match_api_m4.md` §2.1 and §11 item 7 fold this
  in on the freeze-document side.

**Handed to the sibling [M4.1] lane** (not rulings, requirements):

- The search entry must reserve NEGATIVE returns for engine-give-up, naming
  `RX_ERR_STEPS` and `RX_ERR_FRAMES` (§4.4, §4.5).
- The freeze must say which entry a capture-consuming caller uses, and whether
  an anchored capture-delivering entry exists — `match_api_m4.md` §7's symbol
  table currently names none (§11.2).
- `match_api_m4.md` §13 ASK 4 is answered at §5.7 and can be closed there; its
  §11 item 7 checklist entry for [M4.4] resolves to "emit `RX_NCAPS 1`, and
  add the `RX_NCAPS > 1 ⇒ VM` structural check".
- `RX_NCAPS`, `RX_UNSET`, `<prefix>_match` and the group-index symbol names
  are [M4.1]'s; this document adopts its §7/§12.6 spellings and defers on all
  of them (§0.3). **RULED (D41.1, D41.2, 2026-08-14):** §12.6/§12.7 ruled as
  proposed — see §0.3's amendment. All four handoffs above are now
  DISCHARGED: `RX_ERR_STEPS`/`RX_ERR_FRAMES` by D42.3 (`match_api_m4.md`
  §1), the capture-delivering entry by D41.4/§3.1 (`<prefix>_match_caps`),
  ASK 4 by D42.2 confirming this document's own §5.7 answer, and the
  §7/§12.6 spellings by D41.1/D41.2 exactly as adopted here.

---

## 13. Predictions, for the panel to attack

Stated so a critic can go straight at them rather than reconstructing what
this design is betting on.

- **P-1 (§6.1) — REFUTED IN THE STRONG FORM (K17), NOW A GATE.** ~~For a
  pattern whose only VM-forcing feature is capturing groups, the
  capture-erased DFA computes the EXACT leftmost-first span, not an
  over-approximation.~~ **RULED (D44, ratifying R21 E-1):** the panel ran
  this prediction's own instrument — the exact probe this line names —
  and found K17: `(?:b*?(?:a*)*)*` on `"ab"` gives `[0,2)` from pcrec's
  DFA where both oracles give `[0,1)`. The claim holds on 910/910 random
  sweep cells and fails on a specific, narrow, reproducible family (§6.1's
  own account). Because a real counterexample exists, P-1 can no longer
  be stated as a prediction the panel might refute — it is a property
  that must be CHECKED PER PATTERN FAMILY going forward. §3.7's internal
  differential is therefore promoted from "instrument for this
  prediction" to a GATE: no pattern family may rely on span-equality
  between DFA and VM until the differential has run clean for it, and it
  must run in `--engine=vm` mode (§5.6) so the check is genuinely
  independent rather than tautological (§3.7's own RULED note explains
  why). K17 itself is fixed on its own schedule (D44.4, before [M4.4]);
  once fixed, re-running the full differential is what would justify
  reverting §6.1's mark to unconditional STRUCTURAL again — a claim, not
  an assumption.
- **P-2 (§4.2) — REWORDED (D44, ratifying R21 E-5).** ~~Counting steps
  only at backtrack resumptions bounds every pathological pattern.~~
  **Corrected claim: counting steps at backtrack resumptions AND at
  island entries (§4.2's own RULED fix) bounds the NUMBER of
  entries/resumptions in every pathological pattern — it does NOT bound
  TOTAL WALL-CLOCK WORK**, because each counted island entry can
  independently cost up to `O(n)` internal scanning that the counter
  never sees (E-5's finding: `O(n × resumptions)` real work behind an
  `O(n)`-ish step count is possible and not a violation of this
  narrower claim). *Refuted by:* a pattern whose step count stays well
  under budget while its wall-clock time is unreasonable for a benign
  input — which is now an EXPECTED possibility under the corrected
  claim, not a counterexample to it; what WOULD refute the corrected
  claim is a pattern that runs unboundedly long while making a BOUNDED
  NUMBER of resumptions-plus-entries (forward progress between
  resumptions is still monotone in `pos` and bounded by `n`, so the
  author still cannot construct one — a nullable-loop bug in §3.3 would
  be exactly such a witness, which is why the empty-guard, now scoped to
  `rmax == -1` per E-2, is part of the same design).
- **P-3 (§4.7).** No pattern that pcrec answers today at DFA speed reaches the
  step budget after M4. *Refuted by:* a capture-bearing pattern whose
  capture-erased prefilter says "match somewhere" but whose VM then burns the
  budget on a subject where today's engine is fast. (`(.*)=(.*)`-shaped
  patterns over adversarial subjects are the place to look; D22 puts hostile
  patterns out of scope but not hostile SUBJECTS for benign patterns.)
- **P-4 (§8.4(i)).** Emitting case (f) with computed-goto dispatch measures
  SLOWER than the current table, because a 9-bit shift register over random
  input is D13's maximally-unpredictable regime. *Refuted by:* the probe.
- **P-5 (§8.4(ii)).** Roughly 2x of case (f)'s 6.61x gap is the second
  (reverse) pass; dispatch and algorithm own the remaining ~3x. *Refuted by:*
  ASK-10's instrumentation.
- **P-6 (§2.1, §2.5) — NIT (D44, ratifying R21 P-6 finding).** ~~The VM's
  emitted code size is linear in pattern size~~ — **held, WITH A
  CORRECTION**: linear in the EXPANDED NODE COUNT (post any AST rewrites —
  §5.2's discharge-and-re-analyse fixpoint, the finite-backref expansion
  chief among them — can grow the tree before the VM emitter ever sees
  it), not in raw pattern CHARACTERS, which the original phrasing
  conflated. A pattern with a compact textual form and a large expanded
  node count (post-rewrite) is exactly where this distinction bites; the
  claim about label-count linearity is unaffected, only the independent
  variable it is linear IN. And never approaches R1 A-3's gcc-compile-time
  cliff. *Refuted by:* ASK-7.
- **P-7 (§5.4).** After M4, emitted C for every capture-free corpus pattern is
  byte-identical to pre-M4 output modulo the announced break and the stamp
  lines. *Refuted by:* the diff. This one should be a GATE, not a prediction.
- **P-8 (§6.2(a)).** The hybrid's benefit is proportional to
  `1 - span/subject`, and is approximately zero for two of the nine existing
  bench cases. *Refuted by:* M4.6's measurement of the capture-bearing
  siblings of cases (f) and (h).

---

## 14. Explicitly out of scope for this document

- The match API's own surface — entry names, `RX_NCAPS`/`RX_UNSET` spellings,
  the `pcrec_error` which-input tag, the `rx_span` break mechanics. That is
  [M4.1]'s document; this one consumes it and hands it §12's requirements.
- Callout BEHAVIOUR ([M4-CALLOUTS] step 2, a boonies row). This design must
  merely not preclude its call sites, and §6.3's island-partitioning rule plus
  §3.4's `ncap` rule are the two places it touches.
- The substitution template compiler. It consumes the capture-offset contract
  (subst §2's C1–C11), which §3.4 satisfies; nothing else here concerns it.
- Streaming (M3). The VM's label addresses are function-local and do not
  survive a return, which is APPROACH §6's A-4/A-5 constraint; M3.0's design
  gate owns reconciling the VM with `PARTIAL`/`WINDOW_EXCEEDED`.
- UTF-8 (M5), beyond §2.9's one paragraph.
- Backrefs, lookaround, atomic groups, recursion, conditionals — their
  MODULES. §5.2 designs the socket they plug into; their analyses and
  rewrites are their own.
- Adversarial patterns (D22). DD-2 is robustness. This document does not
  contain a threat model and should not be read as containing one.
