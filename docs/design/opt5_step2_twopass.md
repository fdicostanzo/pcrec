# [OPT-5] STEP 2 — THE TWO-PASS FIX: reverse-pass elision

Lane `opt5d`, 2026-09-01. **Design only** — nothing under `src/` or `tests/`
changed by this lane, and nothing was executed: the lane was launched under a
box HOLD, so every number below is CITED from a measurement document by file
and section, never re-measured here. Where a load-bearing number does not
exist, §7 records it as owed with its trigger (D77) rather than inventing it.

Chartered by Frank 2026-09-01 ("i see no downside"), answering the bench's own
ask (iv) in `pcrec-bench` O-12: *"does Frank charter the TWO-PASS fix (parity's
remaining term) — the same 9-rung surface stands ready as its acceptance
instrument"*.

Every load-bearing claim below is tagged **MEASURED** (a number from a cited
document), **INFERRED** (read off the source but not executed — this lane could
not run the compiler) or **PROPOSED** (this note's own design choice).

---

## 0. The claim, and the frame that would falsify it

**The claim.** `<prefix>_search`'s emitted body runs two scans of the same
bytes: a forward one to find where the match ENDS, and a backwards one to find
where it BEGAN. Since `[OPT-5]` STEP 1 both of those are cursor loops rather
than table walks, so the DFA now does exactly twice the VM's work on a counted
class run — which is why the bench's nine-rung ratio sits at 1.76–2.00 and not
lower (MEASURED: O-12 §3 / ledger `2026-08-31-opt5-step1-acceptance-a7e0bdf.md`
§3). On a large and precisely characterisable family of patterns the backwards
pass computes a value that is **`search_from` on every call, provably, at
compile time** — so the pass, its machine, its tables and its accessor block
can all be deleted from the artifact. That family is exactly the family the
bench's counted ladder is made of.

**The acceptance frame (falsifiable, per rung, on the bench's own standing
instrument — O-12 ask (iv), I-29's `bounded@0.2` surface).**

The instrument is the **`large-subject-throughput` (find-all) band**, plain
form, `auto ÷ vm`, at the nine counted rungs. *This corrects the charter brief's
wording, which named a "MATCH regime": the nine-rung acceptance table in ledger
§3 is headed `auto ÷ vm`, `large-subject-throughput`, plain form. The `match`
band is a different, smaller surface, and `year4`/`nest*` are its residents.*

| axis | today (MEASURED, ledger §3) | STEP 2 predicts | falsified if |
|---|---|---|---|
| letters, 9 counted rungs 64…16384 | 1.764–2.000 | **0.90–1.10 at every rung, and FLAT** | any rung above 1.15, or the ratio still bends with the rung |
| letters rung 32768 | 0.999–1.002 (parity-via-decline: `auto` IS the VM) | unchanged | it moves at all |
| digits, all rungs | 0.596–0.604 | **unchanged, 0.58–0.62** | it moves outside that band |
| digits `×1.04–1.06` entry-cost term | present at every rung | **still present** — it is STEP 1's fixed term, not STEP 2's | STEP 2 is credited with removing it |
| `cls-atleast-4096` | letters 2.107–2.716 | **unmoved** (not start-accepting — §3) | it moves |
| search band, `cls-*` cells | ×2.23–2.25 won at STEP 1 | **moves again** | flat |
| search band, `pw-8-64` / `line-80` / `hex32` / `csv5` / `dotted4` / `year4` / `nest*` | see ledger §7.2 | **unmoved by STEP 2** | any of them moves |

Why `0.90–1.10` and not "parity": under the elision the DFA does ONE
address-independent pass and the VM does one, so the ratio should become the
ratio of two like-for-like loops plus a fixed per-call term that does not
halve. Writing `before = 2s + f` and `after = s + f` (s the per-pass scan cost,
f the fixed term) and solving against the measured `before`, every rung lands
between 0.95 and 1.05 for any plausible f — and the *flatness* is the sharper
half of the prediction, because today's 1.76 → 2.00 spread across the rungs is
itself the fixed term's shrinking share. **A result that halves the ratio but
keeps the bend refutes the mechanism even while confirming the direction.**

**The two controls are inside the instrument already**, which is worth saying
plainly because this project's recurring check defect is a control that shares
a source with what it controls (learnings §3): `cls-upto-N` (nullable → the
elision fires) and `cls-atleast-4096` (non-nullable → it declines) are the same
class, the same subjects, the same band, and STEP 2 must move exactly one of
them.

---

## 1. MECHANISM: where the elision lands

### 1.1 Site (a) — the `<prefix>_match` entry — IS ALREADY BUILT. STEP 2 adds nothing there.

The brief asked whether the anchored form already never runs a reverse pass.
**It does not, and has not since 2026-08-29.** This is finding **F1** and it is
the first correction this note owes the plan row.

`[ENG-ABS]`'s SECOND MECHANISM merged at `dfd112b` and is battery-proven
(plan.md `[ENG-ABS]`, r41 panel). `src/gen/emit_dfa.c`'s
`emit_anchored_match_def` emits, verbatim:

```
    // ---- ANCHORED SCAN: where does the match that begins
    // at ctx->pos end? Same LAST-accept rule as the forward
    // scan, so the longest match wins; no reverse pass,
    // because the start is the caller's.
```

and its body is `emit_scan_loop(c, f)` on the third machine followed by
`return (ptrdiff_t)(last_accept_position - search_from);`. There is no
`rewind_position`, no reverse table, no second loop. `dfa_dir_anchored` is
`dfa_dir_forward` character for character apart from a `-1` range guard and
`prefilter_owns_start = false` (`src/gen/CLAUDE.md`, "[ENG-ABS] AXIS G").

The measurement that opened `[OPT-2]` has therefore already been collected:
matching subjects **1.031×** the VM (from 2.077×) and the 35 short valid emails
**0.482×** (from 1.207×) — MEASURED, plan.md `[OPT-2]` closing note, against the
targets `docs/dev/opt2_anchored_match_measurement.md` §5 set (≤1.046× and
≤0.571×). Both were beaten.

**What is left at site (a), and it is a rider on site (b), not its own work.**
Axis G has two candidates. When `unwrapped` does not apply — the anchored
machine overflowed `PCREC_ANCHORED_MAX_STATES` (4,096; seven named fallback
members are on record, r41 S1), or the build carries `-fno-anchored-dfa`, or
the artifact is a VM hybrid — `<prefix>_match` is `search-filter`: four lines
around `<prefix>_search`, and it pays that function's reverse pass in full.
STEP 2's search-side elision rescues exactly those artifacts, for free, with no
axis-G change. INFERRED (from the two emitters' text, not measured).

### 1.2 Site (b) — the `<prefix>_search` entry — IS STEP 2.

`emit_unanchored` emits (`src/gen/emit_dfa.c`, the block after
`emit_machine_tables(c, &fwd); emit_machine_tables(c, &rev);`):

```c
    // ---- FORWARD SCAN: where does a match end? ----------------
    size_t scan_position = search_from;
    size_t last_accept_position = (size_t)-1;
    <forward scan loop>
    if (last_accept_position == (size_t)-1) return 0;
    {
        size_t match_end_position = last_accept_position;
        size_t match_start_position = (size_t)-1;
        size_t rewind_position = match_end_position;
        <reverse scan loop>
        if (match_start_position == (size_t)-1) return 0;
        if (capture_spans) { capture_spans[0][0] = (ptrdiff_t)match_start_position;
                             capture_spans[0][1] = (ptrdiff_t)match_end_position; }
        return 1;
    }
```

The reverse loop is `emit_scan_loop` over `dfa_dir_reverse`, whose cursor is
`rewind_position`, whose bound is `rewind_position > search_from` and whose
recorded value is `match_start_position`. Since STEP 1 it carries scan edges of
its own — indeed on the shapes at issue the *reverse* machine grows edges more
readily than the forward one (MEASURED, r48sem, cited in plan.md's
RESIDUAL-GAP candidate: `mc2` forward 0 edges vs reverse/anchored 4 each). Two
cursor loops over the same bytes is the whole of the residual ×2.

**PROPOSED: THE START-PINNED SEARCH.** When the forward machine's start state
accepts *unconditionally* — at every position, under every position view, in
every class context — three things follow, and the third is the mechanism:

1. A match exists at `search_from` for every `search_from ≤ n`: at minimum the
   empty one. So `<prefix>_search` returns `1` on every call, and the spec's
   zero-length convention (§3.1: "a zero-length match is a success") is what
   makes that a correct answer rather than a suspicious one.
2. D3's accept-pruning removes the start-anywhere self-loop from the closure of
   any accepting state. `src/gen/emit_dfa.c` states this twice, independently,
   in `unanch_start`'s own comments: *"D3's accept-pruning cuts the unanchored
   start self-loop out of every accepting closure"* and *"the unanchored start
   self-loop is the LOWEST-priority thread, so it is pruned out of every
   accepting state, an accepting state's successors can therefore never be
   `fs`"*. If the start state itself accepts, that pruning has fired **before
   the first byte is read**: no later start is ever spawned, so every accept the
   forward loop records belongs to a thread that began at `search_from`.
3. Therefore `last_accept_position` is the end of the LONGEST match beginning at
   `search_from`, that match is the leftmost one, and
   **`match_start_position == search_from`, on every call, unconditionally.**

The emitted body becomes:

```c
    if (last_accept_position == (size_t)-1) return 0;
    if (capture_spans) { capture_spans[0][0] = (ptrdiff_t)search_from;
                         capture_spans[0][1] = (ptrdiff_t)last_accept_position; }
    return 1;
```

and — the half that buys more than the time — **the reverse machine is not
emitted at all**: no `emit_machine_tables(c, &rev)`, no `rev.repr->emit_token`
accessor block, no stay-skip tables, no reverse scan loop, no reverse membership
tables for its scan edges. This is a size event as much as a speed one (§4, §7).

`capture_spans[0][0] = search_from` and not `= 0`: `docs/spec/match_api.md`
§3.1's "**Every offset written to `caps` is an ABSOLUTE offset into `s`, never
relative to `startpos`**" is a measured property a find-all loop depends on, and
it is the obvious way to get this wrong (sabotage S220, §5).

**The predicate, spelled precisely (PROPOSED).** Let `fd = &job->dfa`, `fs` its
start state.

- **P1** `fd->st[fs].up[UPC_PLAIN].accept != 0` — the start state accepts under
  the PLAIN view. *Not* `state_acc_any`, and that distinction is finding F3
  (§3.4).
- **P2** `fs`'s accept is position- and context-invariant:
  `st->eolvar < 0 && st->endvar < 0`, and `st->up[u].accept == st->up[0].accept`
  for every `u` in `1..UPC_N`. This is **character for character
  `src/opt/scanedge.c`'s `member_ok`**, which exists for the same reason
  (precondition (3) there: "a view makes a state's accept differ at
  `pos == n-1`/`pos == n`, which are positions a scan can pass"). PROPOSED:
  lift `member_ok` to a shared, exported predicate rather than writing a second
  copy — a parallel mechanism for a general fact is exactly what memory
  `pcrec-general-mechanisms-not-special-cases` forbids, and `scanedge.c`'s own
  header already apologises for spelling it locally.
- **P3** If `dfa_needs_seed(fd)` (mechanism 4 — `\b`, `(?m)^` — where a search at
  `startpos > 0` begins in `s1u[u]`/`s1g[u]` rather than in `fs`), then **every
  live seed state satisfies P1 and P2 as well.** Omitting this is sabotage S218:
  the predicate would be a statement about a state the search may never occupy,
  which is the exact defect `unanch_start`'s `fseed` clause was added to fix
  ("[M6.2 wave B] `!fseed` joins the conjunction: the proof is about the ONE
  start state `fs`").
- **P4** The artifact's scan is `unanchored`. `attempt` scans are a different
  emitter with no reverse pass to elide, and `empty` scans are one `return 0`.
- **P5** No `\K`. Free by construction, not by a test: `\K` is module-gated to
  `assertions` and forces the VM engine, so no DFA artifact carries one
  (`docs/spec/match_api.md` §3.1). It matters because `\K` is precisely the
  construct that separates "where reporting begins" from "where matching began",
  and this mechanism identifies the two.

**Blast radius, INFERRED.** `emit_unanchored`'s output is also what a VM HYBRID
inlines as its `static <prefix>_prefilter` (`src/gen/emit_dfa.c`: "the hybrid
inlines `emit_unanchored`'s own output"), so hybrids are in scope by
construction. In practice the hybrid ∩ start-pinned population should be at or
near **zero**, and for a satisfying reason: a start-accepting machine gets no
candidate prefilter at all (`docs/spec/tuning.md` §3: `RX_DFA_PREFILTER
"none"`'s *largest cause* is "the start state ACCEPTS — `\bx*`, `a*`, `.*`,
`$` — where no skip is sound at all"), and `[OPT-4.1]`/`[OPT-4.2]` decline to
build a hybrid prefilter whose language is nullable. The two mechanisms are
declining on nearly the same fact. §5 makes the population a printed number
rather than this paragraph.

### 1.3 What is deliberately STEP 3, and why the plan row's own formula is not the mechanism

The plan row's RESIDUAL-GAP candidate says: *"the forward edge counts from its
own entry cursor, so start = end − count is already in a register at loop
exit"*, generalising to `start = end − Σ count_i` over a chain.

**F2: that is not true of the emitted code, in two ways.** `emit_scan_edge`
declares `unsigned long scan_run_length = 1;` **inside the edge's own `if`
block**; it does not survive to loop exit, and nothing writes it anywhere that
does. And an UNBOUNDED edge (`*`/`+`, `span < 0`) emits **no counter at all** —
its comment says so: *"no counter, and the state does not move — the run's every
position IS this state."* So neither the count nor the entry cursor is "already
in a register"; both would have to be added.

That is a small correction. The larger one is that **the count is the easy half
and the plan row's formula assumes away the hard half.** `end − Σcount` needs an
ORIGIN to subtract from, and the origin is what the forward machine does not
know:

- While the machine sits in `fs`, every start is still live and the origin is
  undetermined.
- Once it leaves `fs`, its state is a SET of threads from several origins, and
  the wrapped machine keeps spawning a fresh one at every position until an
  accept prunes them. The position of the last visit to `fs` is a **lower bound**
  on the winning origin, not the origin: threads from `q`, `q+1`, `q+2` can all
  be live, the `q` one can die, and the surviving `q+2` thread is mid-flight —
  so the state is not `fs` and no cursor in the loop names `q+2`.
- The only sound way to make the origin a single number is to run a machine that
  has ONE origin by construction. That machine exists — it is `[ENG-ABS]`'s
  unwrapped anchored machine — and running it per start position is a search,
  not a match-here.

So the multi-edge form is not blocked by bookkeeping; it is blocked by the same
fact `[ENG-ABS]` had to build a third machine to get around. **Recommended
split:**

| | STEP 2 (this note) | STEP 3 and after (named, not designed here) |
|---|---|---|
| mechanism | start-pinned search: the origin is `search_from` by compile-time proof | forward-tracked origin: the origin as a maintained value, sound only under a single-live-origin proof |
| what it needs | nothing new — the predicate reads the machine the emitter already has | construction-time scan-edge synthesis (STEP 3), so the FORWARD machine grows edges on embedded shapes at all |
| population today | the whole counted ladder + the `RX_DFA_PREFILTER "none"` family (§5 counts it) | **empty** — MEASURED (r48sem): the forward machine has 0 edges on the embedded shape `mc2` against 4 on reverse and anchored, so "the match region is edge-total" is unsatisfiable in the forward direction |
| soundness | proved above from D3's pruning, which the emitter already relies on twice | needs a new proof obligation nobody has written |

**Recommendation: build the start-pinned elision as STEP 2 and nothing else.**
The Σcount form has no population to serve until STEP 3 changes the forward
machine, and building it first would be building ahead of a measured need (D77)
on top of a soundness argument that does not yet exist.

Framed against `pcrec-general-mechanisms-not-special-cases`: the general fact is
*"the reverse pass computes the origin, and is dead wherever the origin is
already known"*. Start-pinned is the instance where the origin is known at
compile time; forward-tracked is the instance where it is known at run time.
STEP 2 builds the first instance and names the second — it does not add a
`{0,n}`-shaped special case, and nothing in the predicate looks at the AST, at
`{m,n}`, or at which construct produced the states.

---

## 2. Ask (iii) answered inside the design: NO, the whole-form edge does not fall out free

O-12 ask (iii): *"the whole-form ladder: is a bounded-prefilter scan edge STEP 2
or STEP 3 territory, and does `[ART-SIZE]` expect its first real customer
there?"*

**Answer: neither half falls out of STEP 2, in either direction — and the second
half is YES.**

The whole form is `(?:[a-z]{0,N})\z` (`docs/spec/match_api.md` §3.6's idiom;
`byte-class-bounded` is its prefilter, and `docs/spec/tuning.md` §3 explains
that the `-bounded` pair *is* the `$`/`\Z`/`\z` view). Two independent things
are true of it and neither is the two-pass structure:

1. **It stamps `edge=none` because of scan-edge precondition (3), not because of
   anything STEP 2 touches.** Under `\z` each count state accepts iff
   `pos == n`, so each carries an `endvar` position view, and `member_ok`
   refuses every member (`eolvar < 0 && endvar < 0`). STEP 2 changes what
   `<prefix>_search` does *after* the forward loop; it does not change which
   states qualify as chain members. **INFERRED** — read off `scanedge.c`'s
   `member_ok` and the `-bounded` prefilter's documented cause, not executed
   (§7 item 3 owes the one-command confirmation).
2. **STEP 2's own predicate also declines it.** `(?:[a-z]{0,N})\z` matches empty
   only at `pos == n`, so its start state accepts under the END view and not
   under PLAIN — P1 fails, P2 fails. The whole forms get nothing from STEP 2 and
   lose nothing to it. That is the correct outcome: this is the same state whose
   view-dependence makes it a miscompile if the widened bit is used (§3.4).

**The mechanism that WOULD get them, named** (PROPOSED, for Frank's charter, not
designed here): relax scan-edge precondition (3) from *"no view on any member"*
to *"the only view is the END view, and the scan's own exit at `pos == n`
evaluates it"*. The shape is already present in `emit_scan_edge`: the emitted
block distinguishes bound-reached from run-stopped and already carries the
direction-aware step-back (`pos-1` forward, `pos+1` reverse) precisely so the
run's accept bit and the fall-through's are recorded separately. A view-tolerant
edge would add a third case at the `pos == n` exit. **Call it the VIEW-TOLERANT
SCAN EDGE and give it its own row.** Per Frank's ruling as relayed in the
charter — "if no, state it as STEP 3" — it is STEP 3 territory in sequence; it
is not STEP 3's *mechanism* (construction-time synthesis), and conflating them
would hide a distinct piece of work inside a row that does not describe it.

**Does `[ART-SIZE]` expect its first real customer there? YES, and the numbers
are already on the record.** O-12 §4 (MEASURED): the two `byte-class-bounded`
whole forms keep their linear tables at **471,204 and 937,248 bytes**, still
**93.7 % of the cap**, still the corpus's largest artifacts, and they *own both
surviving warns* — the plain ladder's three warns are gone. A whole-form edge
would delete the tables the way STEP 1 deleted the plain ladder's. That is the
trigger for the row, and it exists today.

---

## 3. SOUNDNESS

### 3.1 Why `start = end − Σcount` is exact on an edge-total region — and why STEP 2 does not use it

For completeness, since the plan row names it. On a region crossed only by scan
edges, each edge consumes exactly its run length and the ordinary step consumes
exactly one byte, so the bytes between the origin and the accept are the sum of
the runs. The arithmetic is exact. **The exactness was never in question; the
origin is** (§1.3). STEP 2 uses the equivalent-but-stronger fact that the origin
is `search_from`, which needs no arithmetic at all: it is the *same number* the
`end − Σcount` form would compute, obtained without maintaining anything.

### 3.2 The elision's own proof, in full

Assume P1–P5 and `search_from ≤ subject_length` (the forward direction's range
guard `if (search_from > subject_length) return 0;` disposes of the rest).

*Claim A — the forward loop records an accept at `search_from` itself.* The
emitted loop body's order is fixed and documented in `scanedge.c`'s header: *"the
accept probe, the candidate-start prefilter, the stay skips, THE SCAN EDGES, the
position-view select, the viewed accept probe, and the tail (bound check, then
the step)"*. The accept probe therefore runs at `scan_position == search_from`
before anything advances. By P1+P2+P3 the state occupied there accepts under
whatever view holds, so `last_accept_position = search_from`. Hence the
`last_accept_position == (size_t)-1` early return is unreachable.

*Claim B — no later start is ever live.* D3's accept-pruning drops every thread
below the highest-priority accepting one; the start-anywhere self-loop is the
lowest-priority thread. `fs` accepts, so the pruning fires in `fs`'s own closure,
before any byte is consumed, and `δ(fs, c)` contains no fresh start thread for
any `c`. By induction no state reachable from `fs` does either. This is not a
new argument: `emit_dfa.c` makes it twice, for the prefilter's stay set and for
the `last == (size_t)-1` gate, and records that "two independent critics attacked
the gate and neither could build a witness: deleting it produced 0 divergences
over 8.0M oracle-checked comparisons".

*Claim C — the leftmost match begins at `search_from`.* By Claim A a match
exists there. Leftmost-first semantics select it. By Claim B, `last_accept_position`
is the furthest end of a thread from `search_from`, i.e. the longest match at
`search_from` — which is what the reverse pass, run from that end, would have
walked back to. So the two forms report the same span.

*Claim D — the return value is unchanged.* The two-pass form returns `0` when
`last_accept_position == -1` (unreachable, Claim A) or when
`match_start_position == -1` (the reverse machine failed to complete a match;
under Claims B–C it cannot, since a completed forward path from `search_from` to
the end exists). Otherwise `1`. The elided form returns `1`. Identical.

*Claim E — `capture_spans == NULL` and the non-zero `RX_NCAPS` case.* Slots
`1..NCAPS-1` are filled with `PCREC_UNSET` by `emit_search_head` at entry to
`<prefix>_search` (wave G's dead-capture elision), untouched by either form. The
`if (capture_spans)` guard is unchanged.

### 3.3 The `last_accept_position == -1` gate: keep it, do not cite it

Claim A makes it unreachable. **Keep it anyway, and do not present it as part of
the argument** — this is the posture `emit_dfa.c` already takes about its own
redundant gate, in the sentence that follows the 8.0M-comparison measurement:
*"Keep the gate — it is free belt-and-braces — but do not cite it as a premise.
Presenting a redundant condition and a load-bearing one as the same claim is how
someone eventually 'simplifies away' the wrong half."* The same words apply here
verbatim. §5 notes the branch-coverage consequence.

### 3.4 The failure directions

**(a) The widened bit — finding F3, and the sharpest miscompile available
here.** `unanch_start` computes `bool start_acc = state_acc_any(&fd->st[fs]);`
and ORs the seed states in. `state_acc_any` means *accepts under SOME view*.
Its own neighbouring comment says the widening is *"BELT-AND-BRACES, NOT
LOAD-BEARING"* for the prefilter's purpose and instructs the reader **not to cite
it as a premise**. Reusing that bit to gate this elision inverts its meaning:
here the widening is load-bearing in the wrong direction, and a state that
accepts only under the EOL/END view would be treated as accepting at every
position. `$` is the named counter-example the same file already carries: *"`$`
alone is exactly the counter-example: it never leaves `fs` and
`forward_is_accepting[fs]` is 0, but its EOL variant accepts."* On `$` over
`"abc"` from `startpos = 0` the true span is `[3,3)`; the widened predicate would
report `[0,3)` — a wrong `caps[0][0]`, a silent miscompile of the field
learnings §3 names as the historically blind one.

**The discriminating population is already a measured number.** [M6.2] wave C
measured that narrowing this same state's read from `state_acc_any` to
`up[UPC_PLAIN].accept` *"changes 21 corpus artifacts and 0 answers, over 2,247
find-all cells"*. Those **21 artifacts are exactly the population on which P1's
two spellings disagree**, and therefore exactly the population a wrong predicate
miscompiles. They are the positive control §5 builds S217 on. (Caveat, stated
because learnings §3 demands the population be named: the 21 was measured at the
[M6.2] tree for a different consumer of the bit, and §7 item 2 owes its re-count
before the assertion is written.)

**(b) The seed states dropped (P3).** `\bx*` searched at `startpos > 0` begins in
a seeded start state whose accept depends on `subject[search_from - 1]`. If that
state does not accept, there is no empty match at `search_from`, the true origin
is later, and the reported start is too small. Detector: sabotage S218.

**(c) Class-context views (`clsctx`).** A state whose accept differs by the class
of the preceding byte. Covered by P2's `up[u]` comparison; dropped, it is
sabotage S219, and §5 records why S219 needs a witness S217's detector cannot
catch or it is a redundancy finding rather than a check.

**(d) `\K`.** Would break the identification of "where reporting begins" with
"where matching began" (`match_api.md` §3.1: on `a\Kb` over `"ab"` the search
consumes from 0 and reports `[1,2)`). Free by construction (P5), and the
structural check that keeps it free is asserting no DFA artifact carries the
construct — which the module gate already guarantees.

**(e) The absolute-offset trap.** Writing `0` instead of `search_from`. Invisible
to any single-search test at `startpos = 0`, which is most of them. Detector:
sabotage S220 and a find-all differential (§5).

**(f) Direction of harm.** Every failure above produces a `caps[0][0]` that is
**too small** (a span that starts earlier than the match did) — never a missed
match, never a crash. That is the quietest possible failure mode and is the
argument for making `caps[0][0]` an explicitly read field in every check (§5),
not an incidental one.

---

## 4. AXES / FORM placement (D82), stamps, deny flag, abi

### 4.1 A new axis, on the shape axis G established

Axis G (`dfa_matches`) answers *which form `<prefix>_match` takes*. This is its
sibling: *which form `<prefix>_search`'s post-loop block takes*. It has axis G's
properties for axis G's reasons — it is a question about an ENTRY POINT rather
than about one machine's form, so **no `DfaForm`, bare `DfaCand`s, one `if` in
`emit_unanchored`**, and the two bodies (a reverse machine with tables and a
loop, versus two assignments) are far too different for a shared skeleton.

```c
/* PROPOSED — AXIS H: WHICH FORM THE SEARCH ENTRY'S START RECOVERY TAKES */
static const DfaSearchStart dfa_search_starts[] = {
    { { "pinned",       PCREC_NO_START_PINNED, start_pinned_applies } },
    { { "reverse-pass", 0,                     cand_always          } },
};
```

`-fno-start-pinned` is a **`deny` FIELD on the first candidate**, D82's shape:
the flag removes the object and the ordinary walk selects the fallback. Nothing
branches on the flag. `--list-axes` picks the new array up with no edit, because
that walk is generic over `DfaCand`'s common leading member.

**Which existing axis objects change: none.** Axes A–F describe a machine's
form and are consumed by `DfaForm`; the reverse machine's own form is unchanged
— it is either derived and emitted exactly as today, or not derived at all.
Axis G is untouched. That is the point of putting this on its own axis rather
than as a clause inside `emit_unanchored`.

**New candidates gained by existing axes: none**, and the note says so
explicitly because a reader of D82 will look for them.

### 4.2 Stamps

**PROPOSED: `<PREFIX>_DFA_START`, values `"pinned"` / `"reverse-pass"`.** Placed
in `emit_dfa_stamps` (DFA-and-hybrid, since a hybrid inlines this body and
therefore has the fact to report — the `RX_DFA_SCAN_EDGE` precedent, not the
`RX_DFA_MATCH` one, which is DFA-only because a hybrid's `_match` is the VM's).
Spelling is offered, not settled: by the `pcrec-dd13b-syntax-is-managers`
precedent the exact wording is the manager's call, and §8 Q3 records it.

**ONE DERIVATION, TWO READERS**, this file's standing rule: the emitter's `if`
and the stamp read the same `dfa_search_start_of(cx)`, never a restated
predicate. `unanch_start`'s own header is the cautionary tale — *"M2.7 forked a
second copy, and the fork is exactly how the prefilter and skip loops went
missing from the `$` path for a whole milestone."*

**`rx_info` mirror — recommend NO, for now.** `RX_DFA_MATCH` earned its
`match_form` mirror on a stated trigger: it is a caller-visible COST property of
an entry point the caller calls, and a header-less consumer needs to know which
form it linked. `<prefix>_search` is also an entry the caller calls and this is
also a ~2× cost property, so the trigger arguably fires. Against it: adding an
`rx_info` field is a struct-layout event on top of a text event, `RX_DFA_TABLE`
and `RX_DFA_SCAN_EDGE` both declined mirrors on "no such consumer reads them
yet", and the bench — the only consumer in evidence — buckets by reading the
emitted `#define`s, not `rx_info`. Recommend the stamp alone, record the trigger
in `match_api.md` §6.3 the way the other two do, and put the asymmetry with
`RX_DFA_MATCH` in front of Frank (§8 Q2).

**Stamp compositions must stop naming a machine the artifact no longer
contains.** `RX_DFA_TABLE` is an artifact-level composition across machines
(spec §6.3) and `RX_DFA_SCAN_EDGE` folds `dfa` → `rdfa` → `adfa`
(`scan_edge_of` is called three times in `dfa_scan_edge_name`). If the reverse
machine is not emitted it must drop out of both folds, or the artifact stamps a
fact about text that is not in it — the mirror image of the defect `[ENG-ABS]`
avoided when it *added* the anchored machine to `RX_DFA_TABLE`'s composition
("leaving the anchored machine out would let the stamp say `"premultiplied"`
about an artifact holding an indexed table"). A fold that changes from `"mixed"`
to `"premultiplied"` on some artifact is the expected, correct consequence.
§5 owes a check.

### 4.3 The number that is NOT born

STEP 1 introduced `PCREC_MAX_SCAN_EDGES` because it introduced a cap, and D90
says a number is born as a `limits.def` row. **STEP 2 introduces no number**:
the predicate is a property of the machine, the elision is unconditional once it
holds, and there is no threshold, budget or knee anywhere in it. `limits.def`
and `docs/spec/limits.md` are untouched, and the note says so rather than
leaving a reader to check. (The one place a number could appear is O-12 ask
(ii)'s "skip-below-k knob" — which belongs to STEP 1's fixed entry term, not
here; §8 Q7.)

### 4.4 The `abi` bump and its sites (D76)

Deleting a machine's tables, accessor block and loop from the emitted artifact is
far past "scaffolding": it is an `abi` bump, in the same change, with the gate
re-pinned. `src/gen/emit_dfa.c:1441` reads `.abi = 14` at `main`'s `ae3e6ca`
(taken there by `[CC-CLANG]` step 1, `c657ae9`). Lane `w12` is delivered and
unmerged and also claims 14, so **STEP 2 writes the next free number and the
final value is assigned at merge serialization** — the same handling `w12`'s own
charter used.

The four sites, all in one change, `make test-codegen` before delivering:

1. `src/gen/emit_dfa.c` — the `.abi = N` line (1441).
2. `tests/codegen/run_codegen_tests.sh` — `ABI_EXPECT` and the `[DD-14.FB]`
   §10.4 narrative sentence (~2713–2741), which carries one clause per bump and
   gains STEP 2's.
3. `docs/spec/match_api.md` §6 — the "`rx_info.abi` is `14`" sentence (line
   1602).
4. The gate's (B) pin — `RECURSION_IDENTITY_FILEPIN`, re-pinned to this change's
   last `src`-touching commit. (B) compares WHOLE FILES within one abi number,
   so it moves by construction (`tests/codegen/CLAUDE.md`, [TT-11]/D76).

**F5 — THERE IS A FIFTH READER, AND IT IS ALREADY STALE.**
`docs/spec/match_api.md:159` reads "`rx_info.abi` is `13` ([OPT-5], the DFA scan
edge…)" while line 1602 reads `14`. `[CC-CLANG]`'s bump updated the site the
ritual names and not this one. The four-site checklist in `CLAUDE.md` is
therefore incomplete as written. Recommend: STEP 2 fixes line 159 as part of its
own bump, and the `CLAUDE.md` row is amended to say *every* reader of the number
(or line 159 is rewritten to stop carrying one — it is a change-history
narrative, and a history sentence pinned to "today" is a stale site by
construction). §8 Q6.

**Registry.** A new tuning flag is a registry row (`PCREC_NO_START_PINNED`,
bit 22 — bit 21 is `PCREC_NO_SCAN_EDGE`, `lib/pcrec.h:451`). The registry counts
move; this note deliberately does not predict the new numbers, since they depend
on what else lands first.

---

## 5. CHECK AND SABOTAGE PLAN

Written against `docs/dev/learnings.md` §3 and memory
`pcrec-check-design-lessons`. The governing question for every item below is
that section's own: **not "does this check run" but "what would have to be true
for it to fail, and who chose that input".**

### 5.1 The primary control, and why it is a real one

`make test-axes` gains `-fno-start-pinned` and asserts answer-identity over the
whole corpus. **This is a genuine control rather than a source-sharing one**,
which is worth stating because it is the failure mode this project keeps
rediscovering: the denied build computes `match_start_position` with the REVERSE
MACHINE, an independent derivation from an independently built automaton — the
emitter's own comment on the pair is *"The two machines are independent and need
not agree."* The default build computes it from a compile-time proof about the
FORWARD machine. Nothing is shared but the answer.

**The blind field.** The elision moves `caps[0][0]` and nothing else — not the
match/no-match verdict, not the length, not the end. Learnings §3 records that
"offsets were the blind field twice of three". So: **the differential must read
`caps[0][0]` explicitly, at `startpos > 0`, under find-all.** A sweep that
compares match/no-match, or compares lengths, is vacuous against every failure
direction in §3.4 — including the one where every answer is still "matched".

### 5.2 Population accounting (K35)

Three numbers, printed, floored, and failing loudly at zero:

- **N_pinned** — corpus artifacts the predicate ACCEPTS. If 0 the whole gate is
  vacuous. Expected non-trivial: `docs/spec/tuning.md` §3's measured stamp
  census has **380 DFA artifacts** (and 644 across everything containing a DFA
  scan) at `RX_DFA_PREFILTER "none"`, whose *largest* documented cause is the
  start state accepting. That is an ESTIMATE and not a bound in either direction
  — `none` has other causes, and the widened bit that produced it is not P1 —
  so §7 item 1 owes the real count before the panel.
- **N_declined_by_view** — artifacts where P1's widened and narrowed spellings
  disagree. Expected ≈ 21 ([M6.2] wave C, MEASURED; §7 item 2 re-counts). **Every
  one must be DECLINED.** This is the positive control for F3 and it is the
  strongest check in the plan, because its expected value comes from a
  measurement taken for an unrelated purpose at a different site — a control that
  cannot have inherited this mechanism's alphabet.
- **N_hybrid_pinned** — hybrids the predicate accepts. Expected ~0 (§1.2). A
  non-zero value is not a failure; it is a finding that wants reading, and the
  check should print it rather than assert it.

### 5.3 Identity gates

- **(B), the whole-file pin.** Moves by construction on every accepted artifact.
  Re-pinned in the same change (§4.4).
- **(A), the program region against the unchanged `ac4917d`.** (A)'s population is
  call-free patterns and its region delimiters are the VM's
  (`goto <prefix>_L0;` … `<prefix>_accept:`). The obligation is to **run it and
  report the number**, and — if any DFA-side member of the population moves — to
  either argue the move is outside the region or extend the exception list *with
  its reason stated*, the way wave G's four dead-capture patterns are handled.
  This note does not predict the outcome: the lane must read it, not assume it.
- **Object-code neutrality** (`run_object_neutrality.sh`) is NOT applicable —
  STEP 2 deliberately changes executed code.

### 5.4 Structural checks owed (`tests/codegen`)

1. An artifact the predicate accepts contains **no `rewind_position`, no
   `<prefix>_reverse_*` table, and no reverse accessor block** — grepped from the
   emitted text, not from a compiler flag.
2. An artifact it declines still contains all three. (Both directions, or the
   check is a liveness argument rather than a value argument.)
3. **The stamp and the body agree**: `<PREFIX>_DFA_START "pinned"` iff
   `rewind_position` is absent. One derivation, two readers — asserted, not
   assumed.
4. `RX_DFA_TABLE` and `RX_DFA_SCAN_EDGE` never name a machine the artifact does
   not contain (§4.2). Concretely: on an accepted artifact, neither fold reads
   `job->rdfa`.
5. **The `\K`-free premise (P5)**: no DFA artifact carries the construct. This is
   guaranteed by the module gate today; the check exists so that the guarantee
   fails loudly if the gate ever moves, rather than turning into a miscompile.
6. **Branch coverage of the kept `last_accept_position == -1` gate.** It becomes
   unreachable on the accepted population (§3.3). A coverage-style check that
   flags never-taken branches will report it; the answer is to keep the branch
   and record here that it is deliberately dead, not to delete it and not to
   suppress the report silently.

### 5.5 Size

`docs/dev/artifact_size_log.tsv` should move **DOWNWARD** on the accepted
population at the next full-corpus `test-corpus` run — a whole machine's tables
and accessor block leave every accepted artifact. `tests/size/`'s tripwire pins
are maxima, so downward movement cannot trip them, but the log diff is the
reviewer's artifact (`scripts/size_diff`) and the movement should be *predicted
per artifact before the run*, not read off afterwards. §7 item 5.

### 5.6 Sabotage rows and their detectors

Each row must be shown to fail SOLO, and each must be shown to reach the binary
(learnings §3). Where two rows share a detector, the disjointness must be proven
the way S213/S214 were — otherwise the second row is a redundancy finding, not a
check.

| row | the sabotage | detector | note |
|---|---|---|---|
| **S217** | predicate widened from `up[UPC_PLAIN].accept` to `state_acc_any` (F3) | the N_declined_by_view assertion (§5.2) + a `$`-shaped answer differential reading `caps[0][0]` | the strongest row; its expected population is an independently measured number |
| **S218** | the `fseed` clause dropped from the predicate (P3) | `\bx*` searched at `startpos > 0`, `caps[0][0]` differential | must be a witness S217's detector does NOT catch |
| **S219** | P2's view/context clause dropped (`eolvar`/`endvar`/`up[u]`) | a `(?m)$`-view start-accepting pattern | **overlaps S217 by construction** — the row is only a check if it carries its own witness; prove the disjointness or record it as redundancy |
| **S220** | `caps[0][0] = 0` instead of `= search_from` | any find-all cell at `startpos > 0` | invisible to every single-search-at-0 test, which is most of the corpus |
| **S221** | the stamp forked from the selection (a second predicate at the stamp site) | check 5.4(3) | the `unanch_start` M2.7 failure mode, pre-empted |

### 5.7 What the bench's AFTER cannot see, so the in-tree checks must

The bench measures TIME and reads STAMPS over **its own** pattern set. It does
run an answer-agreement pass (O-12 §6 records 3 disagreeing rows of 1,885, 0
groups), so it is not answer-blind — but:

- Its population is the bench's patterns, not the corpus's ~2,772. **None of the
  21 discriminating artifacts is known to be in it.** The miscompile in §3.4(a)
  is therefore entirely the in-tree checks' to catch.
- It cannot see artifact SIZE movement on non-bench patterns, nor compiler CPU.
- It cannot distinguish "the elision fired and was right" from "the elision
  declined" except through the stamp — which is why check 5.4(3), tying the stamp
  to the body, is what makes the bench's stamp-bucketing trustworthy at all.
- Conversely, the in-tree checks cannot see the ~2×. **The division is: in-tree
  owns correctness and structure, the bench owns the number.** Neither is a
  substitute for the other, and the acceptance frame in §0 is only meaningful
  once the in-tree side is green.

---

## 6. D80 spec deltas

Contract changes land in `docs/spec/` in the SAME change; a reviewer rejects a
contract change without its spec hunk.

| file | section | delta |
|---|---|---|
| `docs/spec/tuning.md` | new **§2.19** | `-fno-start-pinned` / `PCREC_NO_START_PINNED` (bit 22): what the axis is, what the denied build does instead, the answer-identity promise, and the D82 note that the flag removes a candidate object rather than branching |
| `docs/spec/tuning.md` | **§3** (the DFA side's own stamps) | a `<PREFIX>_DFA_START` bullet in the existing list: value set, that a HYBRID carries it (with the `RX_DFA_SCAN_EDGE` reason — the hybrid inlines this scan), and that it has **no `rx_info` mirror**, naming the trigger that would make one owed |
| `docs/spec/match_api.md` | **§6.3** | `RX_DFA_START` added to the stamp value-set table |
| `docs/spec/match_api.md` | **§6** | the "`rx_info.abi` is `N`" sentence (line 1602) — and **line 159's stale `13`**, F5 |
| `docs/spec/match_api.md` | **§3.1** | one paragraph, mirroring §3.2's treatment of `RX_DFA_MATCH`: the two search forms are **answer-identical** and differ only in cost; `caps[0][0]`'s contract is unchanged, including the absolute-offset sentence and the zero-length-is-success convention, both of which the elision depends on rather than alters |
| `docs/spec/limits.md` | — | **no change**, deliberately (§4.3) |
| `docs/guide/` | — | a pointer only if an existing page already names the two-pass cost; the guide points at the spec and never restates it |

`docs/design/CLAUDE.md` gains a one-line entry for this note, and
`docs/dev/plan.md`'s `[OPT-5]` row gains the STEP 2 charter text with the
STEP 3 / view-tolerant-edge split recorded so the next reader inherits the
distinction rather than re-deriving it.

---

## 7. Measurements owed, each with its trigger (D77)

None of these could be taken by this lane (box hold; and the design needs none
of them to be *written*). Each names what would make it necessary.

| # | measurement | trigger — do not take it before this |
|---|---|---|
| 1 | **N_pinned**: how many corpus artifacts the predicate accepts, and how many are hybrids | before the D6 panel. The note claims the gate is non-vacuous and estimates from a 380-artifact stamp census that is *not* this predicate; the claim is unsupported until counted |
| 2 | **N_declined_by_view** re-counted at today's tree | before writing S217's assertion. The 21 is a [M6.2] wave C number for a different consumer at an older tree; an assertion pinned to a stale count is a check that disarms itself via its own failure message |
| 3 | **Which precondition declines `(?:[a-z]{0,2048})\z`** — one `pcrec` run reading the stamps | before chartering the view-tolerant scan edge (§2). The note INFERS precondition (3); if it is a different one the row's design changes |
| 4 | **The nine-rung `bounded@0.2` AFTER at the STEP 2 pin** | the acceptance frame itself (§0). The instrument is standing — O-12 ask (iv) — and the per-rung predictions are recorded above BEFORE the run, which is the point |
| 5 | **Artifact-size movement on the accepted population**, per artifact, predicted then compared | at the first full-corpus `test-corpus` run after landing. Predicted downward (§5.5) |
| 6 | **Compiler CPU with the reverse machine's BUILD skipped, not just its emission** | only if (5) or a user report shows the build cost matters. The comparable number exists: `[ENG-ABS]`'s optional machine cost **+46 % compiler CPU** on the resource shapes (24.3 → 35.9 s on `[a-z]{0,30000}`, r41 S1), so the symmetric saving is plausible and measurable. **Not in STEP 2** (§8 Q5) |
| 7 | **The `capture_spans == NULL` run-time skip** — the reverse pass is run today even when no caller reads its result, and `match_start_position` is then used only by an early return | **DO NOT BUILD.** No measured caller exists: the bench's driver reports spans, so its find-all loop needs the end and its agreement pass needs the start. The trigger is a measured caller that searches without captures. Recorded so the observation is not lost, not so it is acted on |
| 8 | O-12 asks (ii)/(v): the per-run edge-selection boundary, the fixed term's size, the hybrid trade | **not STEP 2's.** They are STEP 1's fixed entry term — `year4` ×1.07–1.11 on a 4-count run, `dotted4` ×1.11 (ledger §7.3) — a different mechanism at a different site. A "skip-below-k" knob is a NUMBER and would be born as a `limits.def` row (D90). Its own row |

---

## 8. Open questions for Frank, each with a recommendation

**Q1 — Is STEP 2 the start-pinned elision only?**
**Recommend YES.** The Σcount / multi-edge form has no population today: the
forward machine grows 0 edges on the embedded shape r48sem measured, against 4
on reverse and anchored, so "the match region is edge-total" is unsatisfiable
forward. It also lacks a soundness argument for the origin (§1.3). Building it
now is building ahead of a measured need on top of an unwritten proof.

**Q2 — Does the new stamp get an `rx_info` mirror (`search_form`)?**
**Recommend NO for now**, matching `RX_DFA_TABLE` and `RX_DFA_SCAN_EDGE`, with
the trigger recorded in §6.3. It breaks symmetry with `RX_DFA_MATCH`, which DID
earn one on the "caller-visible cost property of an entry the caller calls"
trigger that arguably fires here too — so this is a genuine call, not a
formality. The cost of yes is an `rx_info` struct-layout change on top of the
text change.

**Q3 — The stamp's spelling** (`<PREFIX>_DFA_START "pinned" | "reverse-pass"`).
Offered, not settled. By the `pcrec-dd13b-syntax-is-managers` precedent this is
the manager's call; flagged here only so it is made deliberately rather than
inherited from this note's draft.

**Q4 — Ask (iii): charter the VIEW-TOLERANT SCAN EDGE as its own row now?**
**Recommend YES, opened on §7 item 3's one-command measurement.** Its trigger
already exists and is the bench's own: the two whole-form artifacts at 471,204
and 937,248 bytes, 93.7 % of the `[ART-SIZE]` cap, owning both surviving warns
(O-12 §4). That answers the second half of ask (iii) — `[ART-SIZE]`'s first real
customer is there — with a measured number rather than an expectation.

**Q5 — Skip the reverse machine's BUILD as well as its emission?**
**Recommend NOT in STEP 2.** Skipping the emission is required for honesty (a
built-but-unemitted machine feeding stamps is the defect §4.2 describes);
skipping the build is a separate compiler-CPU optimization with its own trigger
(§7 item 6). Two changes, two triggers, one at a time.

**Q6 — The fifth `abi` site.** `match_api.md:159` is stale at `13` (F5).
**Recommend** STEP 2 fixes it, and `CLAUDE.md`'s ritual row is amended from
"FOUR sites" to "every reader of the number, found by grep" — a checklist that
enumerates by hand drifts from its subject, which is learnings §3's
reference-build lesson applied to a checklist instead of a source list.

**Q7 — Do O-12 asks (ii) and (v) ride STEP 2's charter?**
**Recommend NO** (§7 item 8). They are STEP 1's fixed per-call entry term. If
they ride here, STEP 2's acceptance frame stops being falsifiable, because a
regression family and an improvement family would move on the same pin for two
different reasons.

---

## 9. Findings against the plan row's own text, collected

For the manager's merge review; each is argued in place above.

- **F1** (§1.1) The plan row's RESIDUAL-GAP candidate reads as though the
  two-pass structure is still in front of both entries. It is not: `[ENG-ABS]`
  built the anchored, reverse-pass-free `<prefix>_match` at `dfd112b` (abi 10)
  and it is battery-proven at 1.031× / 0.482×. STEP 2 is a `<prefix>_search`
  change only.
- **F2** (§1.3) *"start = end − count is already in a register at loop exit"* is
  false of the emitted code: `scan_run_length` is block-scoped inside the edge's
  own `if`, and an unbounded edge emits no counter at all. More importantly the
  count is the easy half — the ORIGIN is what the forward machine cannot name.
- **F3** (§3.4a) `unanch_start`'s `start_acc` is a deliberate widening whose own
  comment forbids citing it as a premise; reusing it to gate the elision is a
  miscompile with a named witness (`$`) and a measured discriminating population
  (21 corpus artifacts, [M6.2] wave C).
- **F4** (§0) The acceptance instrument's nine rungs are the
  `large-subject-throughput` (find-all) band, not a `match` band — the charter
  brief's wording; ledger §3's own table heading is the source.
- **F5** (§4.4) The `abi` ritual's "FOUR sites" is incomplete: a fifth reader,
  `docs/spec/match_api.md:159`, is already stale at `13` after `[CC-CLANG]`'s
  bump to 14.
