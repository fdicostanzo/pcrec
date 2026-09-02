# [OPT-5] STEP 2 — THE TWO-PASS FIX: reverse-pass elision — **REVISION 2, 2026-09-02, r49 worked**

Lane `opt5d`, revision 1 2026-09-01 (`8d36141`), **revision 2 2026-09-02**
working every finding of the D6 panel review
`docs/dev/reviews/2026-09-01-r49-opt5-step2.md` (three critics: r49sound,
r49check, r49cons). **Design only** — nothing under `src/` or `tests/` is
changed by this lane. Revision 1 was written under a box HOLD and could
execute nothing; revision 2 was allowed ONE build, so the emitted witnesses
this revision's proof rests on are quoted from artifacts emitted here at
`build/pcrec` on the merge of `lane/opt5d` with main `05c984b` (abi 15).
Everything else is still CITED from a measurement document by file and
section. Where a load-bearing number does not exist, §7 records it as owed
with its trigger (D77) rather than inventing it.

**§10 is the r49 disposition table** — one row per r49 §2 item, verifiable
item by item.

### Changed from revision 1

1. **The elision proof is re-derived from the emitter code** (§3.2, §3.3).
   Rev 1's Claim A ("the accept probe runs before anything advances") is
   FALSE: the probe is an axis-E object and sits BELOW the scan edges on any
   viewed or by-class artifact. The proof is now *some accept ≥ `search_from`
   is always recorded*, derived site by site from `src/gen/emit_dfa.c` with
   two emitted witnesses reproduced here.
2. **The `last_accept_position == -1` gate is LOAD-BEARING, not dead** (§3.3,
   §5.4). Rev 1's "keep it, do not cite it" framing is withdrawn: on a dead
   seed state at `search_from > 0` the gate is the only correct answer.
3. **P3 gains a LIVENESS conjunct** and a pre-existing-hazard note (§1.2).
4. **The failing-call bound is CLOSED as unsound** and handed to
   [OPT-VEDGE]; no `_match` change in STEP 2 (§3.5, new).
5. **The axis letter is J**, not H — H and I are STEP 1's (§4.1).
6. **The `rx_info.search_form` mirror is APPROVED** by Frank; rev 1
   recommended against it and was ruled the other way (§4.2, §6).
7. **The abi ritual follows D94's grep rule**, not a four-site list; abi is
   15 today and STEP 2 writes 16 (§4.4).
8. **§0's acceptance frame becomes a TWO-INSTRUMENT table** with an explicit
   control/customer split and an O-13/O-14 provenance rule.
9. **The check plan is rebuilt**: named manifests instead of counts, birth-time
   `SAB_REACH`/`SAB_REACH_POP`, sabotage ids S218-S222, and three owed
   measurements that were previously written as facts (§5).

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

**The acceptance frame — TWO INSTRUMENTS, reconciled (r49 item 17 / r49cons
Q3).** Rev 1 named one instrument. There are two, they read different things,
and the panel's reconciliation is that **the `unwrapped` match rungs are a
CONTROL and the `search-filter` rungs and the search band are the CUSTOMERS**.
Conflating them is how a family that must not move and a family that must
would land on one pin for two reasons — exactly what Q7 refuses.

*Provenance rule for every number in this section (r49 item 17).* Readings
sourced to **O-13** (`pcrec-bench` `99de28e`, relayed 2026-09-01 ~18:5x) are
**SCRATCH TIER** and carry O-13's own withdrawal rule: two `pcrecbench quick`
cells at `--trials 3` on a loaded box, both stamped `inconclusive-load`, from
which only the RATIO between two arms measured back to back under one load
with a flat control survives. **O-14** — the overnight full-suite verdict at
pcrec `1989c62`, 29/29 measured, window CLOSED 10:48 on 2026-09-01 — confirms
or withdraws them, section by section, the way O-12 withdrew the 8192 flag.
**O-14 had NOT landed in `/home/duxevents/pcrec-bench/docs/dev/outbox_to_pcrec.md`
when this revision was written** (last write 2026-09-01 18:47, newest message
`## O-13`), so every scratch-tier cell below carries an
**`[O-14 PENDING — manager fills at merge]`** marker. Ledger readings
(`2026-08-31-opt5-step1-acceptance-a7e0bdf.md`) and stamp facts are NOT
scratch tier and carry no marker.

**Instrument 1 — `large-subject-throughput` (find-all) band, plain form,
`auto ÷ vm`, the nine counted rungs.** This is the surface O-12 ask (iv)
offered and I-29's `bounded@0.2` stands ready on. *This corrects the charter
brief's wording, which named a "MATCH regime": the nine-rung acceptance table
in ledger §3 is headed `auto ÷ vm`, `large-subject-throughput`, plain form.
The `match` band is instrument 2, and `year4`/`nest*` are its residents.*

| axis | today (MEASURED, ledger §3) | STEP 2 predicts | falsified if |
|---|---|---|---|
| letters, 9 counted rungs 64…16384 | 1.764–2.000 | **0.90–1.10 at every rung, and FLAT** | any rung above 1.15, or the ratio still bends with the rung |
| letters rung 32768 | 0.999–1.002 (parity-via-decline: `auto` IS the VM) | unchanged | it moves at all |
| digits, all rungs | 0.596–0.604 | **unchanged, 0.58–0.62** | it moves outside that band |
| digits `×1.04–1.06` entry-cost term | present at every rung | **still present** — it is STEP 1's fixed term, not STEP 2's | STEP 2 is credited with removing it |
| `cls-atleast-4096` | letters 2.107–2.716 | **unmoved** — the predicate DECLINES it, and that is now an in-tree NAMED WITNESS (§5.6a) rather than bench prose | it moves |
| search band, `cls-*` cells | ×2.23–2.25 won at STEP 1 | **moves again** | flat |
| search band, `pw-8-64` / `line-80` / `hex32` / `csv5` / `dotted4` / `year4` / `nest*` | see ledger §7.2 | **unmoved by STEP 2** | any of them moves |

Every one of the nine rungs is start-pinned. VERIFIED here by emitting the
ladder (`build/pcrec -p rx --features all`, this revision's own build): all of
`[a-z]{0,64}` … `[a-z]{0,16384}` stamp `RX_DFA_PREFILTER "none"`, which by
§3.4's `!start_acc` gate is the observable consequence of the start state
accepting. `[a-z]{0,32768}` routes to the VM, which is the parity-via-decline
rung.

**Instrument 2 — `bounded@0.3` `match` regime, `search-filter` rung ÷
`unwrapped` rung, per subject, forced VM as the flat control.** This is the
instrument O-13 §2 fired, and it is where the CONTROL/CUSTOMER split lives.
The two entry forms sit on the SAME ladder, so the ladder splits in two:

| rung family | `RX_DFA_MATCH` today (VERIFIED, this build) | role | STEP 2 predicts |
|---|---|---|---|
| plain `[a-z]{0,64}` … `{0,2048}` | `unwrapped` | **CONTROL — predicted FLAT.** `_match` has been reverse-pass-free since `dfd112b` (§1.1 F1), so STEP 2's `<prefix>_search` change cannot reach it | unmoved on the `match` regime; the find-all band still moves (instrument 1) |
| plain `[a-z]{0,4096}` / `{0,8192}` / `{0,16384}` | `search-filter` | **CUSTOMER.** `_match` is four lines around `<prefix>_search` and pays its reverse pass in full | the ×2.0 two-pass term goes; and per C3 the fallback's failing calls CEASE rather than get bounded (§3.5) |
| whole-form `(?:[a-z]{0,N})\z`, N ≥ 2048 | `search-filter`, `RX_DFA_PREFILTER "byte-class-bounded"`, `RX_DFA_SCAN_EDGE "none"` | **NOT STEP 2's.** The predicate declines them (view, §2) — they are [OPT-VEDGE]'s customer | **unmoved by STEP 2** |
| hybrid rows (`nest2-64`, `nest3-16`) | `engine=vm`, four cells (O-13 §3, a record read) | pending the FORCE-AXIS census §5.2 owes | no prediction until that census exists (§5.2) |

O-13's own readings on instrument 2, carried here with their tier:
`cls-upto-2048 ÷ cls-upto-1024`, matching letters runs 64–1024 B: **1.97–2.04**
with the VM control at 0.90–0.99 — the ×2.0 residual IS the reverse pass
(SCRATCH TIER; `[O-14 PENDING — manager fills at merge]`). And on a FAILING
anchored match, `d-01024`: **×37.4** (11.6 → 432.4 ns), the `search-filter`
entry scanning the whole subject for candidate starts before rejecting every
one (SCRATCH TIER; `[O-14 PENDING — manager fills at merge]`). **That ×37
exhibit is the whole-form row above, which the predicate DECLINES** — see
§1.1, r49 item 11.

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
STEP 2's search-side elision reaches those artifacts with no axis-G change.
INFERRED (from the two emitters' text, not measured).

**QUANTIFIED, and rev 1's "rescues exactly those artifacts, for free" was
BOTH unquantified and wrong about the exhibit** (r49 item 11 / sound B6 +
check M9). Two separate populations were being run together:

1. **The bench's ×37 exhibit is NOT in the pinned population.** It is the
   whole form `(?:[a-z]{0,N})\z`, and M3 measured that the predicate declines
   it — VERIFIED again here: `(?:[a-z]{0,8192})\z` stamps
   `RX_DFA_PREFILTER "byte-class-bounded"` and `RX_DFA_SCAN_EDGE "none"`,
   the position-view refusal of §2. **STEP 2 leaves the measured exhibit
   exactly where it is.** It is the customer of **[OPT-VEDGE]**
   (`docs/dev/plan.md` `[OPT-VEDGE]`, chartered 2026-09-01 on Frank's Q4
   "agree"), whose relaxed scan-edge precondition (3) collapses the `\z`
   skeletons and drops the anchored machine's state count back under
   `PCREC_ANCHORED_MAX_STATES` — one mechanism, two customers, and the
   ×37 band is the second.
2. **The population that IS pinned and IS `search-filter` is the plain
   counted ladder above the anchored cap**, and what it gets is C3's fact,
   not a bound. VERIFIED, this build:

   | pattern | `RX_DFA_PREFILTER` | `RX_DFA_MATCH` |
   |---|---|---|
   | `[a-z]{0,2048}` | `none` (pinned) | `unwrapped` |
   | `[a-z]{0,4096}` | `none` (pinned) | `search-filter` |
   | `[a-z]{0,8192}` | `none` (pinned) | `search-filter` |
   | `[a-z]{0,16384}` | `none` (pinned) | `search-filter` |

   On these, once the elision lands, `rx_search` returns 1 with
   `caps[0][0] == ctx->pos` on **every** call, so the fallback's
   `found != 1 || caps[0][0] != ctx->pos` filter never fires: the O(subject)
   failing path does not get bounded, it **ceases to exist**, and the
   `return -1` becomes unreachable. That is §3.5's C3 and it is a
   BEHAVIOURAL claim §5.4 asserts, distinct from the throughput claim above.

   `N_pinned ∩ search-filter` is not yet a corpus-wide count; §7 item 9
   records it as owed with its trigger.

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
it is the obvious way to get this wrong (sabotage S221, §5.6d).

**The predicate, spelled precisely (PROPOSED).** Let `fd = &job->dfa`, `fs` its
start state.

- **P1** `fd->st[fs].up[UPC_PLAIN].accept != 0` — the start state accepts under
  the PLAIN view. *Not* `state_acc_any`, and that distinction is finding F3
  (§3.4).
- **P2** `fs`'s accept is position- and context-invariant:
  `st->eolvar < 0 && st->endvar < 0`, and `st->up[u].accept == st->up[0].accept`
  for every `u` in `1..UPC_N`. This is **character for character
  `src/opt/scanedge.c`'s `member_ok`** (`:188-194`), which exists for the same
  reason (precondition (3) there: "a view makes a state's accept differ at
  `pos == n-1`/`pos == n`, which are positions a scan can pass"). PROPOSED:
  lift `member_ok` to a shared, exported predicate rather than writing a second
  copy — a parallel mechanism for a general fact is exactly what memory
  `pcrec-general-mechanisms-not-special-cases` forbids, and `scanedge.c`'s own
  header already apologises for spelling it locally.

  **P2 IS STRICTER THAN SOUNDNESS NEEDS, AND THAT IS A DELIBERATE
  CONSERVATIVE CHOICE** (r49 item 13 / sound B4). The elision needs only the
  variant's **accept bit** to agree; `member_ok` refuses a state that carries a
  view *variant at all*. The variant's state identity matters to the STEP
  (`f->src` feeds the transition — `src/gen/emit_dfa.c:3596-3600`, and the
  emitted `forward_state = rx_forward_step(..., forward_view_state, ...)`), not
  to the ORIGIN; and a variant that accepts pruned its own closure exactly as
  the base view did (Claim B, §3.2), so the elision holds for it too.
  Consequence: some of M1's **47 `view` declines** are not view-*accept*
  dependent, and the accepted population is smaller than it needs to be.
  This note takes the strict form anyway, because reusing `member_ok`
  unchanged is what keeps ONE derivation for a fact two passes read, and
  because the relaxation is a separate soundness argument.
  **The relaxing measurement and its trigger (D77):** partition M1's 47 `view`
  declines into (i) states whose accept bit genuinely differs across views and
  (ii) states that merely CARRY a variant with an equal accept bit; the
  relaxation is worth building only if (ii) is a material share. **Trigger:**
  a bench or corpus customer lands in group (ii). Do not build it before
  that number exists — and note it is not free of interaction with
  [OPT-VEDGE], which moves the same population from the other side.
- **P3** If `dfa_needs_seed(fd)` (`src/gen/emit_dfa.c:2161-2166` — mechanism 4,
  `\b`, `(?m)^`, where a search at `startpos > 0` begins in `s1u[u]`/`s1g[u]`
  rather than in `fs`), then **every seed state is LIVE and satisfies P1 and
  P2 as well** — i.e. the predicate DECLINES when any `d->s1u[u] < 0`.
  Omitting the P1/P2 half is sabotage S219 (§5.6): the predicate would be a
  statement about a state the search may never occupy, the exact defect
  `unanch_start`'s `fseed` clause was added to fix ("[M6.2 wave B] `!fseed`
  joins the conjunction: the proof is about the ONE start state `fs`").

  **The LIVENESS conjunct is new in revision 2** (r49 item 2 / sound A2) and
  it is not a tightening for tidiness. `d->s1u[u]` can be `-1`
  (`src/ir/dfa.c:1249-1258`; `make_state` returns `-1` when no
  `(view, class-context)` closure is live, `:1113-1116`). A search at
  `search_from > 0` that seeds into a DEAD state records no accept, the kept
  `last_accept_position == (size_t)-1` gate returns 0, **and that is the
  correct answer** — no match begins there. Without the conjunct the elision
  would write a fabricated empty match at `search_from`: a match reported
  where there is none, which is a strictly worse failure than §3.4(f)'s
  too-small `caps[0][0]`. `dfa_premul` (`src/gen/emit_dfa.c:2205-2215`)
  refuses pre-multiplication on exactly this condition and its comment records
  a 2026-08-26 sweep finding no negative cell over 1,256 corpus patterns — a
  MEASUREMENT, not a proof, and that transform declines rather than resting on
  it. STEP 2 takes the same posture. **The implementation ASSERTS the
  conjunct**, so a machine that reaches the elision with a dead seed is a loud
  internal error rather than a silent miscompile.

  > **PRE-EXISTING HAZARD, NOT STEP 2's TO FIX.** The accept probe on a dead
  > token is already latent UB: `is_accepting[-1]` in the indexed form,
  > `is_accepting[65535]` in the premultiplied one — the emitter's own note at
  > `src/gen/emit_dfa.c:2205-2215`. **Nothing in STEP 2, or after it, may rely
  > on "a dead token records nothing"**; declining is the only clean posture,
  > which is why P3's liveness conjunct is a conjunct and not a comment. Filing
  > or fixing the hazard is a separate row with its own trigger.
- **P4** The artifact's scan is `unanchored`. `attempt` scans are a different
  emitter with no reverse pass to elide, and `empty` scans are one `return 0`.
- **P5** — **REWORDED IN REVISION 2; rev 1's version was FALSE** (r49 item 12 /
  sound B1). Rev 1 said "no DFA artifact carries `\K`… free by construction,
  not by a test". `\K` forces the **engine** to the VM; it does not keep the
  pattern's machine away from this emitter, because `emit_unanchored` has a
  SECOND customer — the VM hybrid's inlined `static <prefix>_prefilter`
  (`src/gen/emit_dfa.c:1356`, `:4725`, and `emit_search_head`'s own note at
  `:438-447`). VERIFIED here:

  ```
  $ build/pcrec -p rx --features all -fprefilter -o K3.c -- '\Ka*'
  #define RX_ENGINE          "vm"
  #define RX_DFA_SCAN        "unanchored"
  #define RX_DFA_PREFILTER   "none"
      static const unsigned char rx_forward_is_accepting[2] = { 1, 1, };
  ```

  A `\K` pattern whose hybrid prefilter is a one-state start-accepting machine:
  P1 ✓, P2 ✓, P4 ✓, P3 n/a. **The correct statement of P5 is the ENGINE-LEVEL
  fact:** `fit.chosen == ENGM_DFA` implies no `\K`, so no artifact whose
  `<prefix>_match` and `<prefix>_search` this emitter OWNS carries one.

  **And the hybrid case is safe for a different reason, which must be said
  rather than assumed: the span is a BOUND, not an ANSWER.** The emitted
  `rx_search_run` reads

  ```c
  if (rx_prefilter(subject, subject_length, search_from, window) != 1) return 0;
  attempt_position = (size_t)window[0][0];
  window_end = (size_t)window[0][1] < subject_length ? (size_t)window[0][1] : subject_length;
  ```

  `window[0][0]` is a lower bound on the attempt start, and `search_from` is
  the strongest sound lower bound there is; `window[0][1]` is untouched by the
  elision. So on a hybrid the elision is if anything MORE conservative than
  today. §5.4(5) is reworded to assert the engine-level fact, because the
  artifact-level assertion rev 1 wrote would either fire on this artifact or
  pass vacuously (sound F4).

**P0 — THE ROUTING DEPENDENCY THE PREDICATE INHERITS AND MUST STATE**
(r49 item 18 / sound A6). The predicate reads `fs = fd->s0`. That is the right
state at `search_from == 0` only because `ENG_UNANCH` implies `!nfa_has_bot`
(`src/core/compile.c:1096`), i.e. no `N_BOT`, `N_BOT_M` or `N_GSTART`
(`src/ir/nfa.c:990-993`): `s0` is closed with `bot_ok = true, gst_ok = true`
and `s1u[UPC_PLAIN]` with `false, false` (`src/ir/dfa.c:1249-1258`), so with
none of those nodes present the two closures coincide and intern to the same
id — **`fs == s1u[UPC_PLAIN]`**, and `s1g[]` equals `s1u[]` entry for entry.
P3 then covers `search_from > 0`, and there is no third (`\G`) start family to
miss.

**Why this must be WRITTEN and not inherited:** `dfa_needs_seed`
(`src/gen/emit_dfa.c:2161-2166`) compares only `s1u[u]` ACROSS `u` — it would
not notice an `s0 != s1u[PLAIN]` split — and `seed_emit_constant` (`:3496-3502`)
then emits `s0` unconditionally at every `search_from`. The elision is sound
today **only because of the ENG_UNANCH no-BOT routing above**, not because
anything in the predicate checks it. A future engine-selection change that
routed a BOT-bearing machine here would break the elision silently. The
implementation states this as a comment at the predicate and, per §5.4, the
structural checks name `ENG_UNANCH` explicitly rather than assuming it.

**Blast radius, INFERRED for the mechanism, MEASURED for the population.**
`emit_unanchored`'s output is also what a VM HYBRID inlines as its
`static <prefix>_prefilter` (`src/gen/emit_dfa.c:1356`, `:4725`), so hybrids
are in scope by construction. The reason the two rarely coincide is sharper
than rev 1 gave: a start-accepting machine gets no candidate prefilter at all,
and it is the **same widened bit** that gates both —
`if (!start_acc && o->cand.usable)` at `:2581`, with the offset-k selection
riding that same verdict at `:2596`. So the prefilter mechanism and the
elision cannot disagree; they are not "declining on nearly the same fact",
they are reading one bit. A useful corollary for the proof: on the accepted
population there is **no candidate prefilter and no offset-k skip**, so
neither can move the scan's entry position (sound A3).

**M1 MEASURED `N_hybrid_pinned = 0` — AND THAT IS A DEFAULT-AXIS NUMBER, NOT
A POPULATION** (r49 item 12 / sound B2, the K35 shape). M1's census ran default
flags. `pfc_prefilter_forced` (`src/core/compile.c:1060-1063`) lets
`-fprefilter` build a prefilter whose collapsed language is nullable —
do-or-die overrides the `prefilter_lang_nullable` decline, and the comment at
`:1051-1059` says so. A nullable prefilter language is precisely the pinned
shape, as P5's `\Ka*` witness demonstrates. And `make test-axes`
(`Makefile`'s `test-axes` target → `tests/axes/run_axes.sh`) derives its sweep
from the `PCREC_(NO|FORCE)_*` bits, so **`-fprefilter` is inside the gate's own
population**, on a corpus that contains both `\K` patterns and nullable
patterns. §5.2 therefore records `N_hybrid_pinned` under the FORCE axis as an
OWED MEASUREMENT with its command shape, not as a fact.

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
- **Tracking the origin forward on a multi-origin machine is SOUND and NOT
  FREE — a COST argument, not an impossibility one** (r49 item 15 / sound D2;
  revision 2 corrects rev 1, which said "the only sound way" and contradicted
  its own comparison table two paragraphs down). Tagged determinization —
  Laurikari-style TDFA: a start-position register carried per thread set, with
  copy operations attached to transitions — is a standard, sound construction
  that tracks the origin forward on exactly this machine, and it is what
  TNFA-based engines use for submatch extraction in one pass. What it costs is
  a register copy per transition and a substantially larger build — **which is
  precisely the per-step cost STEP 2 exists to remove**, and precisely why it
  should not be built now. The alternative that has no per-step cost is a
  machine with ONE origin by construction; that machine exists — it is
  `[ENG-ABS]`'s unwrapped anchored machine — and running it per start position
  is a search, not a match-here.

  **The D77 trigger, named so the next reader revisits rather than inherits:**
  STEP 3's construction-time scan-edge synthesis changes the economics —
  fewer states, fewer register copies, and counted regions that are
  single-origin by construction. **Re-evaluate forward origin tracking WHEN
  STEP 3 lands, and not before.** Nobody should carry away "forward origin
  tracking is unsound"; it is untaken, on cost.

So the multi-edge form is not blocked by bookkeeping; it is blocked by a cost
the same fact `[ENG-ABS]` paid a third machine to avoid. **Recommended
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
   states qualify as chain members. **MEASURED in revision 2** — rev 1 marked
   this INFERRED and owed a confirmation; §7 item 3 is now taken. Memo M3
   (`docs/dev/opt5_step2_premeasure.md`) confirms precondition (3) with a
   discriminating probe PAIR — removing `\z` alone from the same skeleton flips
   `RX_DFA_SCAN_EDGE` from `"none"` to `"range"` — and `member_ok` (line 190)
   checks `st->endvar >= 0` FIRST, before the class-context loop, so
   precondition (3) refuses every member and precondition (2) is never reached.
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

### 3.2 The elision's own proof, re-derived FROM THE EMITTER (rewritten in revision 2)

Assume P0–P5 and `search_from <= subject_length` (the forward direction's range
guard `if (search_from > subject_length) return 0;` disposes of the rest).

**Revision 1's Claim A was FALSE and is replaced** (r49 item 1 / sound A1).
Rev 1 said: *"The emitted loop body's order is fixed and documented in
`scanedge.c`'s header … The accept probe therefore runs at
`scan_position == search_from` before anything advances."* That misreads the
header. The header's own list names **two** probe sites — "the accept probe,
the candidate-start prefilter, the stay skips, THE SCAN EDGES, the
position-view select, the viewed accept probe, and the tail"
(`src/opt/scanedge.c:107-109`) — and **which of them an artifact has is an
axis-E selection, not a constant.**

#### 3.2.0 Where the loop records an accept — the derivation, site by site

`emit_scan_loop` (`src/gen/emit_dfa.c`) emits the body in this order, and
every line below is a call in that function:

| order | line | what it emits | does it record `last_accept_position`? |
|---|---|---|---|
| 1 | `:4696` | `f->acc->emit_top` | only under axis-E `scalar-plain` |
| 2 | `:4697` | `f->pf->emit` (candidate prefilter) | no — and ABSENT on the accepted population (§3.2.1) |
| 3 | `:4699-4703` | `f->dir->emit_skip` per stay skip | yes, at its LANDING position, when `!views` and the skipped state accepts (`dir_fwd_skip`, `:3992-4014`, the record at `:4011-4012`) |
| 4 | `:4714` | `emit_scan_edge` per edge | yes, at a landing position, in every arm (`:4473-4568`; see below) |
| 5 | `:4715` | `f->view->emit` (position-view select) | no — moves nothing |
| 6 | `:4716` | `f->acc->emit_after_view` | only under axis-E `scalar-viewed` |
| 7 | `:4717` | `f->acc->emit_tail` | under `by-class`, yes — the tail IS the probe |

Axis E is `dfa_accs` (`:3572-3579`) and it has three objects:

- **`scalar-plain`** (`cand_always`) supplies `emit_top` — probe FIRST, above
  everything;
- **`scalar-viewed`** (`acc_viewed_applies`, `:3511`) supplies
  `emit_after_view` — probe BELOW the scan edges;
- **`by-class`** (`acc_by_class_applies`, `:3510`) supplies NEITHER, and
  records inside `acc_emit_tail_by_class` (`:3530-3570`): the class-indexed
  probe at `:3563-3565` in the interior, `emit_bound_accept` at `:3558` at the
  boundary arm.

And `acc_viewed_applies` reads `us->views`, which `unanch_start` builds as
`o->views = o->viewsel || wctx` with `wctx = fd->clsctx || rd->clsctx`
(`:2487-2503`) — **an OR over BOTH machines**, so a `\b` that exists only in
the REVERSE machine demotes the FORWARD probe below the edges.

**Two witnesses, emitted here** (`build/pcrec -p rx --features all`, this
revision's build; both stamp `RX_ENGINE "dfa"`, `RX_DFA_SCAN "unanchored"`,
`RX_DFA_PREFILTER "none"` — start-accepting, i.e. inside the accepted
population):

**(i) `[a-z]{0,8}|9$`** — the loop body OPENS with the scan edge at state 0;
the probe is eight lines later, after the view select:

```c
    for (;;) {
        // [OPT-5] SCAN EDGE: the states between here and state
        // 1 differ only in how many class-2 bytes have been counted, ...
        if (forward_state == 0 && scan_position < subject_length && (unsigned char)(subject[scan_position] - 97) <= 25) {
            unsigned long scan_run_length = 1;
            scan_position++;
            while (scan_position < subject_length && scan_run_length < 8UL
                   && (unsigned char)(subject[scan_position] - 97) <= 25) { scan_position++; scan_run_length++; }
            if (scan_run_length == 8UL) {
                forward_state = 3;
                last_accept_position = scan_position;
            } else {
                last_accept_position = scan_position;   // the run stopped inside the edge
            }
        }
        rx_forward_state forward_view_state = forward_state;
        if (__builtin_expect(scan_position + 1 >= subject_length, 0) && ...)
            forward_view_state = rx_forward_view_take(...);
        if (rx_forward_accepts(rx_forward_is_accepting, forward_view_state)) last_accept_position = scan_position;
```

On `"abc"` at `search_from = 0` the edge consumes the run and records
`last_accept_position = 3`. **Position 0 is never recorded.**

**(ii) `a*|\b9`** — the same shape via `wctx` alone; no view select is emitted
at all, because the machine's only class context comes from the `\b` in the
other branch:

```c
    for (;;) {
        // [OPT-5] SCAN EDGE: every state a run of class 3 would pass IS this state, ...
        if (forward_state == 0 && scan_position < subject_length && subject[scan_position] == 97) {
            scan_position++;
            while (scan_position < subject_length && subject[scan_position] == 97) scan_position++;
            last_accept_position = scan_position;   // every position the run passed accepts
        }
        if (rx_forward_accepts(rx_forward_is_accepting, forward_state)) last_accept_position = scan_position;
```

**(iii) the control — `[a-z]{0,64}`**, the shape rev 1 assumed was universal,
DOES put the probe first:

```c
    for (;;) {
        if (rx_forward_accepts(rx_forward_is_accepting, forward_state)) last_accept_position = scan_position;
        // [OPT-5] SCAN EDGE: ...
```

A second, independent reason rev 1's literal claim fails: `pick_skip_states`
excludes `s0` ONLY (`:4601-4602`, via `dir->prefilter_owns_start`), not the
seed states — so on a SEEDED machine at `search_from > 0` a stay skip can fire
on the first iteration and advance the position before any probe. And
scan-edge heads are excluded from nothing: `dfa_form_derive` takes every state
with `dfa_edge_taken` (`:4609-4610`), `fs` included — which is exactly where
the elision's speed comes from, since on the accepted population the edge sits
AT the start state.

#### 3.2.1 Claim A (repaired) — some accept ≥ `search_from` is ALWAYS recorded

*Claim A.* Under P0–P4, the forward loop's FIRST iteration records
`last_accept_position = q` for some `q >= search_from`. Hence
`last_accept_position != (size_t)-1` when the loop exits.

*Proof, by the table in §3.2.0.* The entry state is `fs` at
`search_from == 0` (P0) or a seed state at `search_from > 0` (P3), and in
either case it is LIVE and accepts under every position view and every class
context (P1 + P2 + P3). Nothing above the recording sites can advance the
position past a recording site without itself recording:

- **The prefilter cannot fire at all.** `start_acc = state_acc_any(&fd->st[fs])`
  OR'd over the seed states (`:2542-2547`), and the prefilter is gated
  `if (!start_acc && o->cand.usable)` (`:2581`). P1
  (`up[UPC_PLAIN].accept != 0`) implies `state_acc_any` implies `start_acc`,
  so the gate is false: **no candidate prefilter, and no offset-k skip either**,
  since the k-selection rides that same verdict (`:2596`). VERIFIED: every
  probe in the accepted population stamps `RX_DFA_PREFILTER "none"`
  (`a*`, `[a-z]{0,64}` … `{0,16384}`, `[a-z]{0,8}|9$`, `a*|\b9`, forced
  `\Ka*`).
- **A stay skip that fires records its landing** when `!views`
  (`dir_fwd_skip:4011-4012`, guarded on the skipped state's PLAIN accept bit,
  which P1+P2 give); when `views` it deliberately does not, because the probe
  BELOW it covers the landing — the emitter says so at `:4009-4011`.
- **A scan edge that fires records a landing in every arm.** With `acc = 1`
  (P1 at the head `fs`): the unbounded arm records at `:4531-4533`; the bounded
  arm records the fall-through's position at `:4556` when the fall-through
  accepts, the step-back position at `:4552` when it does not, and the
  run-stopped position at `:4561-4562`.
- **The view select and both probes move nothing** (`:4715`, `:4696`, `:4716`).
- **If NOTHING above fired**, the position is still `search_from` and the
  axis-E object records there: `scalar-plain` at `:4696`, `scalar-viewed` at
  `:4716`, `by-class` inside the tail at `:3563-3565` (interior) or `:3558`
  (boundary) — the class-indexed bit equalling the base bit by P2, and the
  base bit being 1 by P1. ∎

**What Claim A does NOT say, and rev 1 wrongly assumed it did:** it does not
say the recorded position is `search_from`. Witness (i) records 3, not 0.
`caps[0][0] = search_from` is not Claim A's; it is Claim B's.

*Claim B — no later start is ever live.* `nfa_wrap_unanchored`
(`src/ir/nfa.c:946-955`) sets `st[sp].t1 = nfa->start` (the pattern) and
`st[sp].t2 = any` (the byte self-loop), so the restart thread is the
**lowest**-priority branch of the split. `closure()` walks the pre-set in
priority order and stops the instant an accept is reached
(`src/ir/dfa.c:794`: `if (prune && cl.accept) break;`), and `clo_walk`
discards every deferred branch on accept (`:649-655`). Under P1+P2 every live
`(view, class-context)` closure of `fs` accepts — at most nine of them,
`make_state` at `:1080-1110` — so all of them prune, no restart thread
survives into `fs`'s list, and by induction none reappears downstream
(`any`'s only in-edge is from `sp`). Minimization preserves this: it is a
language-level statement (`L(fs)` is the pattern's own, un-wrapped language),
and `pcrec_minimize_dfa` preserves the language from each state.

*Claim C — the leftmost match begins at `search_from`.* By P1 a match exists
at `search_from`: at minimum the empty one. Leftmost-first semantics select
it. By Claim B every accept the forward loop records belongs to a thread that
began at `search_from`, so `last_accept_position` is the furthest END of such
a thread — the longest match at `search_from`, which is what the reverse pass,
run from that end, would have walked back to. Independently: the reverse
machine is the **unpruned** reverse language (`prune = false`,
`src/core/compile.c:1103`), hence a superset of the pruned forward language, so
anything the forward loop accepted from `search_from` is accepted walking back;
the reverse loop is bounded at `rewind_position > search_from`
(`src/gen/emit_dfa.c:4113-4116`) and records the furthest-back accept, so it
necessarily lands on `search_from`. The two forms report the same span.

*Claim D — the return value is unchanged.* The two-pass form returns `0` when
`last_accept_position == -1` — reachable ONLY in the dead-seed case P3 now
excludes, and there `0` is the correct answer (§3.3) — or when
`match_start_position == -1`, unreachable by Claim C. Otherwise `1`. The
elided form returns `1` on the accepted population. Identical.

*Claim E — `capture_spans == NULL` and the non-zero `RX_NCAPS` case.* Slots
`1..NCAPS-1` are filled with `PCREC_UNSET` by `emit_search_head` at entry to
`<prefix>_search` (`src/gen/emit_dfa.c:428-448`, wave G's dead-capture
elision), above BOTH forms and gated
`cx->job->fit.chosen == ENGM_DFA && dfa_artifact_ncaps(cx) > 1`, so a hybrid's
inlined prefilter never runs it. Neither form touches it, and the
`if (capture_spans)` guard is unchanged.

### 3.3 The `last_accept_position == -1` gate is LOAD-BEARING — keep it, and say why

**Revision 1 got this backwards and revision 2 withdraws it in full.** Rev 1
titled this section "keep it, do not cite it", called the gate unreachable
under Claim A, and borrowed `emit_dfa.c`'s "free belt-and-braces … do not cite
it as a premise" sentence — which is about a DIFFERENT gate, the prefilter's
stay set. Applied here it writes a falsehood a later simplification would act
on (r49 item 1 / sound A2, check F3).

**The gate is the correct answer on a live input.** A search at
`search_from > 0` on a seeded machine can seed into a state that is DEAD:
`d->s1u[u]` is `-1` when no `(view, class-context)` closure is live
(`src/ir/dfa.c:1249-1258`, `make_state`'s return at `:1113-1116`). No accept is
recorded, `last_accept_position` stays `(size_t)-1`, the gate returns 0, and
**there is genuinely no match beginning there**. Delete the gate and the
elision fabricates an empty match at `search_from` — a match reported where
there is none, the failure direction §3.4(f) says cannot happen.

So the posture is the opposite of rev 1's:

1. **P3's liveness conjunct** (§1.2) makes the predicate DECLINE any machine
   with a dead seed, so the gate is not the elision's only defence.
2. **The gate stays, and is named LOAD-BEARING in the emitted comment** and in
   `docs/spec/`, precisely so that nobody reads a coverage report and deletes
   it.
3. **The branch-coverage consequence is a CORPUS fact, not a machine fact**
   (sound F3). A coverage-style check will find the branch never taken on the
   accepted population; the correct record is "this corpus contains no dead
   seed at `startpos > 0`", never "deliberately dead". §5.4(6) is rewritten
   accordingly, and §5.6 gives the dead-seed case a sabotage row rather than a
   coverage exemption.

**Every "dead" / "do not cite" phrasing about this gate is deleted from the
note.** The one sentence that survives from `emit_dfa.c` — "Presenting a
redundant condition and a load-bearing one as the same claim is how someone
eventually 'simplifies away' the wrong half" — now argues the other way: the
gate is the load-bearing half, and rev 1 was the reader it warns about.

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

**The discriminating population is measured, and revision 2 changes both the
number and the way it is pinned.** [M6.2] wave C measured that narrowing this
same state's read from `state_acc_any` to `up[UPC_PLAIN].accept` *"changes 21
corpus artifacts and 0 answers, over 2,247 find-all cells"*. §7 item 2's
re-count is now DONE: **M2 measured 16** at today's tree over 2,845 corpus
patterns (`docs/dev/opt5_step2_premeasure.md` M2), and every one of the 16 is
an `(?m)...$` multiline-EOL shape — exactly this counter-example class.

**Do NOT pin the check to "16", or to any count** (r49 item 7 / check M2). The
strength rev 1 claimed for this control was its independence: a number
measured for an unrelated consumer at a different tree. **That independence
EXPIRED when M2 re-measured it FOR this check**, re-deriving the exact
predicate distinction the sabotage edits, with the `member_ok` body this note
proposes to SHARE with the implementation. Once P2 is a shared exported
predicate, probe and feature call one function, a latent defect appears
identically in "expected" and "actual", and the check greens wrongly. §5.2
replaces the count with a NAMED MANIFEST.

**`$` is the named witness the emitter already carries:** *"`$` alone is
exactly the counter-example: it never leaves `fs` and
`forward_is_accepting[fs]` is 0, but its EOL variant accepts."* On `$` over
`"abc"` from `startpos = 0` the true span is `[3,3)`; the widened predicate
would report `[0,3)`.

**(b) The seed states dropped (P3's P1/P2 half).** A seeded start state whose
accept depends on `subject[search_from - 1]`. If it does not accept, there is
no empty match at `search_from`, the true origin is later, and the reported
start is too small. Detector: sabotage **S219** — **whose witness is the check
plan's hardest problem**, because rev 1's `\bx*` never reaches P3 (P2 declines
it first) and M1 found ZERO P3-stage declines corpus-wide. §5.6b is the whole
of that argument.

**(b′) The seed state DEAD (P3's liveness half) — new in revision 2.** A
search at `search_from > 0` seeding into `s1u[u] < 0`. Here the correct answer
is "no match", the kept `-1` gate delivers it, and an elision without the
liveness conjunct fabricates an empty match instead. This is the ONE failure
direction in this section that is not a too-small `caps[0][0]` (see (f)), and
it is why P3's conjunct is asserted in the implementation. Detector: sabotage
**S219**'s second arm (the liveness conjunct dropped) — and the assertion in
the compiler is the real guard, for the reason §5.6b gives.

**(c) Class-context views (`clsctx`).** A state whose accept differs by the class
of the preceding byte. Covered by P2's `up[u]` comparison; dropped, it is
sabotage **S220**, whose disjointness from S218 is an OWED MEASUREMENT before
shipping (§5.6c) — M1 counted the `classctx` decline population at **8**, and
a population of 8 that may overlap S218's is exactly the S79/S80 shape.

**(d) `\K`.** Would break the identification of "where reporting begins" with
"where matching began" (`match_api.md` §3.1: on `a\Kb` over `"ab"` the search
consumes from 0 and reports `[1,2)`). **Free by ENGINE ROUTING, not by
artifact absence** — see the reworded P5 (§1.2): `fit.chosen == ENGM_DFA`
implies no `\K`, while a `-fprefilter` hybrid CAN put a `\K` machine through
this emitter, where the span is a bound and not an answer. §5.4(5) asserts the
engine-level fact.

**(e) The absolute-offset trap.** Writing `0` instead of `search_from`. Invisible
to any single-search test at `startpos = 0`, which is most of them. Detector:
sabotage **S221** — and §5.6d records that its detector population is not yet
counted, which is r49 item 10.

**(f) Direction of harm — with ONE exception, new in revision 2.** Every
failure above except (b′) produces a `caps[0][0]` that is **too small** (a span
that starts earlier than the match did) — never a missed match, never a crash.
That is the quietest possible failure mode and is the argument for making
`caps[0][0]` an explicitly read field in every check (§5), not an incidental
one. **(b′) is worse**: a dead seed with the liveness conjunct dropped reports
a MATCH WHERE THERE IS NONE. A check plan calibrated only on "offsets are the
blind field" would not be looking for it, so §5.6's S222 asserts the verdict,
not the offset.

### 3.5 The failing-call bound is CLOSED — unsound in every cheap spelling

New in revision 2 (r49 item 3 / sound C1+C2+C3; it also answers the bench's
ask (b) and O-13's ask (i)). Rev 1's §1.1 carried a rider suggesting
`<prefix>_match`'s fallback could bound its search at `start == ctx->pos`.
**It cannot, and the answer for the bench is NO `_match` change in STEP 2.**

**Why no cheap spelling is sound.** The fallback body, from
`build/pcrec -p rx --features all -fno-anchored-dfa -- 'a*b'` (VERIFIED, this
build):

```c
ptrdiff_t rx_match(const rx_ctx *ctx)
{
    ptrdiff_t capture_spans[RX_NCAPS][2] = {{0}};
    int found = rx_search(ctx->subject, ctx->len, ctx->pos, capture_spans);
    if (found < 0) return (ptrdiff_t)found;
    if (found != 1 || (size_t)capture_spans[0][0] != ctx->pos) return -1;
    return capture_spans[0][1] - capture_spans[0][0];
}
```

The wrapped machine's state variable cannot distinguish "the thread from
`ctx->pos` is still alive" from "only a fresh thread spawned here is alive" —
**they are the same DFA state.** The witness, read off the same artifact's
emitted tables:

```
 * State legend -- the shortest input that reaches each state:
 *    0  (start) nothing consumed yet
 *    1  "b"   ACCEPTING
 */
static const unsigned short rx_forward_next_state[6] = { 0, 0, 3, 65535, 65535, 65535 };
                                                          ^     ^
                                              tr[fs]['a'] == fs |  tr[fs]['b'] == state 1
```

Pattern `a*b`, subject `"aab"`, `ctx->pos = 0`, expected `_match == 3` (PCRE2
matches `"aab"` at 0). The machine sits in the start state at positions 0, 1
and 2 and accepts at 3. **Any bound that stops when the scan is back in the
start state, or when "no candidate can still begin at `ctx->pos`", stops at
position 1 and returns −1** — a lost match, not a slow one.

This is §1.3's own origin-unknowability arriving at a second site: §1.3 argues
the forward machine cannot name the origin, and the candidate fix needs exactly
that fact. **The note's §1.3 is the argument against rev 1's §1.1 rider.**

For the record, the two spellings that ARE sound and are still not taken:

- **truncating `subject_length` to `ctx->pos + MRL`** — UNSOUND on any
  view-bearing artifact: it makes `$`/`\Z`/`\z` true at a fake end. That is the
  slice-vs-window trap `seed_emit_seeded`'s own comment names
  (`src/gen/emit_dfa.c:3475-3482`).
- **a separate `window_end` parameter** that bounds the scan without moving the
  views — sound in shape (it is what the hybrid already passes to
  `rx_match_anchored`), but it helps only patterns with a finite maximum match
  length, and `last_accept_position` may still belong to a later origin, so the
  `caps[0][0] != ctx->pos` filter is still what makes it correct.

**Who owns the population.** [OPT-VEDGE] (`docs/dev/plan.md`, chartered
2026-09-01 on Frank's Q4 "agree") already records the mechanism: relaxing
scan-edge precondition (3) collapses the `\z` skeletons AND drops the anchored
machine's state count below `PCREC_ANCHORED_MAX_STATES`, so the `search-filter`
band the bench measured at ×37 shrinks by the same move. That route replaces
the fallback with the `unwrapped` `_match` already battery-proven at `dfd112b`,
**so it needs no new soundness argument at all**, where the bounded fallback
needs one it cannot have. Folding a `_match` change into STEP 2 would also
break §0's acceptance frame for Q7's reason: two families moving on one pin for
two different reasons.

**What STEP 2 DOES do at that site, and it is a different claim from §1.1's**
(C3). On the PINNED population the fallback's failing calls do not get bounded,
they **cease to exist**: `rx_search` returns 1 with `caps[0][0] == ctx->pos` on
every call, so `_match` never takes the O(subject) path and its `return -1` is
**unreachable**. That is a behavioural fact about emitted code, so §5.4 asserts
it as a structural check rather than leaving it as prose.

---

## 4. AXES / FORM placement (D82), stamps, deny flag, abi

### 4.1 A new axis — **AXIS J**, not H (corrected in revision 2)

Axis G (`dfa_matches`) answers *which form `<prefix>_match` takes*. This is its
sibling: *which form `<prefix>_search`'s post-loop block takes*. It has axis G's
properties for axis G's reasons — it is a question about an ENTRY POINT rather
than about one machine's form, so **no `DfaForm`, bare `DfaCand`s, one `if` in
`emit_unanchored`**, and the two bodies (a reverse machine with tables and a
loop, versus two assignments) are far too different for a shared skeleton.

**The letter is J** (r49 item 4 / cons F-B, sound E3). Rev 1 proposed H, which
is TAKEN: [OPT-5] STEP 1 landed **axis H** ("DOES THIS STATE EMIT AN EDGE AT
ALL", `src/gen/emit_dfa.c:4317`) and **axis I** ("THE EDGE'S RUN-EXTENSION
BODY", `:4349`); `scan_edge_of` names both by letter at `:2694-2695` and
`src/gen/CLAUDE.md` does too. A collision here is silent — `--list-axes`
(D82) walks the candidate arrays generically and would print two axes with one
letter — so the rename is global across this note, the axis comment, the deny
flag's spelling, `src/gen/CLAUDE.md`'s axis list, and every stamp discussion.

```c
/* PROPOSED — AXIS J: WHICH FORM THE SEARCH ENTRY'S START RECOVERY TAKES */
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

**`rx_info.search_form` MIRROR — APPROVED. Revision 1 recommended against it
and was RULED THE OTHER WAY** (r49 item 5 / cons F-A, sound E2). Rev 1's
argument, kept here as the trace a reader is owed: `RX_DFA_TABLE` and
`RX_DFA_SCAN_EDGE` both declined mirrors on "no such consumer reads them yet",
and the bench buckets by reading the emitted `#define`s. **Frank ruled the
other way the same day** (`docs/dev/plan.md` `[OPT-5]`: "`rx_info.search_form`
mirror APPROVED, rides the implementation's own abi event (Q2, Frank: 'a great
idea', with a direction note questioning which stamps should remain `#define`s
at all)"). The trigger that fires is `RX_DFA_MATCH`'s own: a caller-visible
COST property of an entry point the caller calls, which a header-less consumer
needs in order to know which form it linked. §8 Q2 records the ruling.

**Consequence: the implementation carries an `rx_info` STRUCT-LAYOUT change on
top of the text change,** and a merge review that follows a spec-delta table
without it ships an incomplete contract. §6 carries the hunk.

**THE HUNK, and a disagreement with the review's wording, recorded rather than
silently deviated from.** The review says "append after `match_form`,
[DD-13c] discipline". [DD-13c]'s discipline as the emitter states it is
*"APPENDED AT THE END, after `match_form`, so no existing member's offset
moves — the [DD-13c] append precedent rather than abi 2's and abi 3's
insertions"* (`src/gen/emit_dfa.c:735-737`). At the time that comment was
written, `match_form` WAS the last member; today `name` and `nentries` follow
it (`:735ff`, added by [DD-13b.W1.2] at abi 15). **Taking "after `match_form`"
literally would INSERT before `name`/`nentries` and move their offsets, which
is the exact thing the discipline exists to prevent.** So the hunk appends at
the END, after `nentries`, and this note records the reading for the merge
review to confirm.

```c
    /* [DD-13b.W1.2] ... name; nentries ...  <- unchanged, still last today */
    const char           *name;
    int                   nentries;
    /* [OPT-5 STEP 2] HOW <prefix>_search recovers the match START:
       "pinned" (the start is search_from by compile-time proof, and the
       artifact carries no reverse machine) or "reverse-pass" (the second
       scan). Mirrors <PREFIX>_DFA_START. NON-NULL on every artifact that
       CONTAINS a DFA scan -- a VM HYBRID inlines this same body, so unlike
       match_form the guard is pcrec_artifact_has_dfa_scan and NOT
       fit.chosen == ENGM_DFA. NULL on a plain VM artifact. */
    const char           *search_form;
```

**The guard is deliberately the OTHER one**, and the emitter's own note at
`:1690-1697` is why: `match_form` is guarded on `fit.chosen == ENGM_DFA`
because "a hybrid's `<prefix>_match` is the VM's own anchored body, which this
axis does not describe". Axis J describes `<prefix>_search`'s post-loop block,
which a hybrid DOES contain (it inlines `emit_unanchored`) — so the field
follows the `RX_DFA_SCAN_EDGE` precedent, exactly as the stamp does. The
comment sits ABOVE the member, not after it, for the measured
`tests/lib/size_count.sh` reason `[ENG-ABS]` records at `match_form`.

**Stamp compositions must stop naming a machine the artifact no longer
contains — CONFIRMED by the panel at exactly two sites** (r49 item 16 /
sound E4). `RX_DFA_TABLE` is an artifact-level composition across machines
(spec §6.3) and `RX_DFA_SCAN_EDGE` folds `dfa` → `rdfa` → `adfa`. If the
reverse machine is not emitted it must drop out of both folds, or the artifact
stamps a fact about text that is not in it — the mirror image of the defect
`[ENG-ABS]` avoided when it *added* the anchored machine to `RX_DFA_TABLE`'s
composition.

The two sites, cited:

| stamp | function | the reverse read to drop |
|---|---|---|
| `RX_DFA_TABLE` | `dfa_table_name`, `src/gen/emit_dfa.c:2664-2666` | `const char *r = dfa_repr_of(cx, &cx->job->rdfa)->c.name;` at `:2665`, and the `if (strcmp(f, r)) return "mixed";` that consumes it |
| `RX_DFA_SCAN_EDGE` | `dfa_scan_edge_name`, `:2706-2715` | `if (strcmp(v, "mixed")) v = scan_edge_of(cx, &cx->job->rdfa, v);` at `:2711` |

**PREDICTED STAMP MOVEMENTS, written BEFORE the change** (this is the
prediction table r49 item 16 asks for; it is a per-artifact prediction the
implementation lane compares against, not a summary read afterwards):

| artifact class | `RX_DFA_TABLE` today | predicted after | `RX_DFA_SCAN_EDGE` today | predicted after |
|---|---|---|---|---|
| pinned, both machines same repr | its form name | **unchanged** | as folded | may change only if the reverse machine was the `"mixed"` cause |
| pinned, forward and reverse reprs DIFFER | `"mixed"` | **the forward machine's form name** — an expected, correct movement | — | — |
| pinned, reverse machine had edges the forward one lacks (the `mc2` shape r48sem measured: forward 0, reverse 4) | — | — | `"mixed"` | **the forward machine's value** (`"none"` where the forward machine has no edge) |
| pinned AND `RX_DFA_MATCH "unwrapped"` | folds three machines | folds **two** (forward + anchored) | same | same |
| declined (any) | unchanged | **unchanged** | unchanged | **unchanged** |

Both stamps are DFA-and-hybrid artifact-level facts, so a hybrid whose inlined
prefilter is pinned moves the same way. §5.4(4) asserts the negative form (on
an accepted artifact neither fold reads `job->rdfa`), because a prediction
table is a reviewer's artifact and an assertion is a check.

### 4.3 The number that is NOT born

STEP 1 introduced `PCREC_MAX_SCAN_EDGES` because it introduced a cap, and D90
says a number is born as a `limits.def` row. **STEP 2 introduces no number**:
the predicate is a property of the machine, the elision is unconditional once it
holds, and there is no threshold, budget or knee anywhere in it. `limits.def`
and `docs/spec/limits.md` are untouched, and the note says so rather than
leaving a reader to check. (The one place a number could appear is O-12 ask
(ii)'s "skip-below-k knob" — which belongs to STEP 1's fixed entry term, not
here; §8 Q7.)

### 4.4 The `abi` bump — D94's GREP RULE, not a site list (rewritten in revision 2)

Deleting a machine's tables, accessor block and loop from the emitted artifact
is far past "scaffolding": it is an `abi` bump, in the same change, with the
gate re-pinned (D76). **STEP 2 also appends an `rx_info` member** (§4.2), so
the bump carries a struct-layout event as well as a text one.

**abi is 15 today and STEP 2 writes 16.** Rev 1 read 14 at `ae3e6ca` and
described a "next free number assigned at merge serialization" because
lane `w12` also claimed 14. That is resolved: `w12` merged, `src/gen/emit_dfa.c:1514`
reads `.abi = 15`, and there is no serialization ambiguity left (r49 item 17 /
cons F-C).

**Rev 1's four-site checklist is DELETED. D94 retired it — on this note's own
finding.** `docs/dev/decisions.md` D94 (Frank, 2026-09-01, ruling this note's
Q6, "agree. this is the right direction"): *"At every abi bump the lane greps
the tree for readers of the number … and moves ALL of them"*, because the
hand-enumerated four drifted exactly the way this project's hand-copied counts
always have. **So this note states the GREP, not the sites:**

```sh
grep -rEn '\.abi = |ABI_EXPECT|`rx_info\.abi` is' src lib cli tests docs Makefile
grep -rn  'RECURSION_IDENTITY_FILEPIN' tests          # the gate's (B) pin
```

Run in this worktree at `05c984b`, that grep returns FIVE readers of the
number today, which is one more than rev 1's list had — the demonstration that
the rule is the right shape:

| reader | what it is |
|---|---|
| `src/gen/emit_dfa.c:1514` | the `.abi = 15` stamp itself |
| `tests/codegen/run_codegen_tests.sh:2735` | `ABI_EXPECT=15` |
| `tests/codegen/run_codegen_tests.sh:2737` | the `[DD-14.FB]` §10.4 narrative sentence, one clause per bump — STEP 2 appends its own |
| `docs/spec/match_api.md:159` | the §3-area "`rx_info.abi` is `15`" sentence |
| `docs/spec/match_api.md:1647` | the §6 "`rx_info.abi` is `15` on every artifact today" sentence |
| `tests/codegen/run_recursion_identity.sh:515` | `FILEPIN="${RECURSION_IDENTITY_FILEPIN:-6dbdf41}"` — the (B) pin, re-pinned to STEP 2's last `src`-touching commit |

**Do not copy that table into the implementation.** It is a snapshot taken
2026-09-02 to show the rule works; the implementation runs the grep itself, at
its own tree, and moves whatever it returns. `make test-codegen` before
delivering.

**F5 and Q6 are DISCHARGED and revision 2 deletes rev 1's text about them**
(r49 item 17 / cons F-C, sound E1). Rev 1 found `match_api.md:159` stale at
`13` while `:1602` read `14`, and recommended fixing it plus amending the
ritual. Both halves landed: the w12 merge renumbered `:159` (it now reads
`15`, VERIFIED by the grep above), and the ritual amendment is **D94**, already
in `docs/dev/decisions.md` and in `CLAUDE.md`'s situation index. Nothing is
owed here; §8 Q6 records it as ruled and closed.

**Registry.** A new tuning flag is a registry row (`PCREC_NO_START_PINNED`,
**bit 22** — bit 21 is `PCREC_NO_SCAN_EDGE` at `lib/pcrec.h:451` and nothing
above it is defined, CONFIRMED by the panel). The registry counts move; this
note deliberately does not predict the new numbers, since they depend on what
else lands first.

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

**One exception, added in revision 2, and it points the other way.** §3.4(b′)
— a dead seed with P3's liveness conjunct dropped — reports a MATCH WHERE
THERE IS NONE, so the VERDICT is what moves, not the offset. A differential
tuned entirely to "offsets are the blind field" would not be looking for it.
So the sweep reads `caps[0][0]` AND the verdict; and because no witness for
that shape can currently be built (§5.6b), the compiler assertion is what
actually stands guard.

**The denied build must also carry the deny flag through the AXIS SWEEP under
the FORCE axis**, not only the default one — `-fno-start-pinned` crossed with
`-fprefilter` is where §5.2's uncounted hybrid population lives (§7 item 9).

### 5.2 Population accounting (K35) — rewritten in revision 2

Rev 1 asked for three numbers as ESTIMATES. Two are now measured, one is owed
under a different axis, and the way they are PINNED has changed.

#### N_pinned = 175 — MEASURED

`docs/dev/opt5_step2_premeasure.md` M1 (lane opt5m2 `24ba0c4`): over 2,845
distinct corpus `pattern` lines (floor 2,620, `LC_ALL=C sort -u` per K35),
default engine, `--features all`. **175 artifacts the predicate accepts, all of
them pure DFA, 0 among hybrids on the default axis** — 9.35% of the
1,872-artifact `unanchored` population the predicate is even asked of, so the
gate is comfortably non-vacuous. Decline reasons: `notacc` 1,642 (96.8%),
`view` 47 (2.8%), `classctx` 8 (0.5%), **seed stage 0**.

That last zero is the check plan's central problem and §5.6b is about it.

#### The view-decline control — a NAMED MANIFEST, never the count

Rev 1 wrote "**Expected ≈ 21** … every one must be DECLINED" and called it the
strongest check in the plan because its expected value came from a measurement
taken for an unrelated purpose. **Revision 2 withdraws the count and the
independence claim** (r49 item 7 / check M2, learnings §3's "exact counts
disarm themselves via their own failure message; the fix is a manifest naming
irreplaceable rows").

*Why the independence expired.* [M6.2] wave C's 21 was a different consumer's
number at an older tree. M2's 16 is **this check's own number, re-measured for
this check, by re-deriving the exact predicate distinction the sabotage
edits — using `member_ok`'s body, which this note proposes to SHARE with the
implementation.** Once P2 is one exported predicate, the probe and the feature
call one function: a latent defect appears identically in "expected" and
"actual" and the check greens wrongly. That is the control-shares-a-source
defect, arriving through the fix for a different one.

*Why a count is not a control even setting that aside.* A count answers "did
someone delete a lot"; it never answers "the right ones". And it disarms
itself: when the corpus grows an `(?m)…$` pattern the assertion fails with
"expected 16, got 17", and the cheapest correct-looking repair is to edit the
16.

**THE MANIFEST — `VIEW_DECLINE_MANIFEST`, shape-defined and floored:**

- **Selector (the definition, not a list):** every corpus pattern whose
  artifact is `RX_DFA_SCAN "unanchored"` and whose forward start state accepts
  under SOME view but NOT under `UPC_PLAIN` — i.e. `state_acc_any(fs)` is true
  and `fs->up[UPC_PLAIN].accept` is 0. This is the population on which P1's
  widened and narrowed spellings disagree, stated as the property rather than
  as its extension.
- **The all-and-only assertion:** every member is DECLINED by the predicate,
  and no member is accepted. The check reports the member list, so a
  disagreement names patterns rather than a delta.
- **The floor:** `>= 12` members (M2 measured 16; the floor is set below it so
  ordinary corpus churn does not trip it, and a drop to single digits is a
  loud finding about the corpus). The floor is a `SAB_REACH_POP` line on
  S218, per §5.6.
- **Named irreplaceable rows** — the shape-anchors, which must never leave the
  corpus without a stated reason: `(?m)$` (the minimal form), `(?m)a*$` (the
  nullable-with-EOL form), `(?m)\bx*$` (the form carrying a class context too),
  `(?m:.*$)` (the scoped-group spelling), `(?m)a{0,4}$(?-m)` (the
  mode-toggled spelling). The full 16 as measured live in
  `docs/dev/opt5m2_m2_changed_patterns.txt`; the five above are the ones whose
  loss would silently narrow the manifest's SHAPE coverage.
- **The independent leg the manifest still needs:** the manifest is derived
  from the same predicate it controls, so it is a MANIFEST, not an oracle. The
  ANSWER leg is what makes it a control: every member is also run through the
  find-all `caps[0][0]` differential of §5.1, whose reference is the reverse
  machine under `-fno-start-pinned` — an independently built automaton. State
  the two legs separately in the check's own output so a reader can see which
  one is asserting what.

#### N_hybrid_pinned — an OWED MEASUREMENT under the FORCE AXIS, not a fact

M1 measured 0 hybrids. **That is a DEFAULT-AXIS number and §5.2 may not assert
it as a population** (r49 item 12 / sound B2, and this is K35's shape: a claim
stated over a narrower set than the check runs on). `pfc_prefilter_forced`
(`src/core/compile.c:1060-1063`) lets `-fprefilter` override the
`prefilter_lang_nullable` decline, and `make test-axes` derives its sweep from
the `PCREC_(NO|FORCE)_*` bits — so `-fprefilter` is INSIDE the gate's own
population, over a corpus holding both `\K` patterns and nullable patterns.
P5's `\Ka*` witness is a member.

**The owed measurement, with its command shape** (D77 — named, not taken here):

```sh
# for each corpus pattern P, under the FORCE axis rather than the default:
build/pcrec --features all -fprefilter -p rx -o art.c -- "$P"
# then read RX_ENGINE == "vm" AND the STEP 2 predicate's verdict on the
# inlined prefilter's forward machine (opt5m2's RX_PROBE_PINNED instrument,
# or the shipped RX_DFA_START stamp once it exists)
```

**Trigger: before §5.2's hybrid line is written as anything but "not yet
counted", and before the implementation's axis sweep is declared complete.**
Until then the check PRINTS `N_hybrid_pinned` and asserts nothing about it —
a non-zero value is a finding that wants reading, not a failure.

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
- **(B)'s pin value today is `6dbdf41`** (`tests/codegen/run_recursion_identity.sh:515`),
  which D94's grep returns alongside the abi readers (§4.4). It is re-pinned to
  STEP 2's own last `src`-touching commit; the gate's structural check then
  requires the pin's stamped abi to equal the compiler's, so a bump without a
  re-pin fails (B) and is told why.

### 5.4 Structural checks owed (`tests/codegen`) — revised

1. An artifact the predicate accepts contains **no `rewind_position`, no
   `<prefix>_reverse_*` table, and no reverse accessor block** — grepped from
   the emitted text, not from a compiler flag.
2. An artifact it declines still contains all three. (Both directions, or the
   check is a liveness argument rather than a value argument.)
3. **The stamp and the body agree**: `<PREFIX>_DFA_START "pinned"` iff
   `rewind_position` is absent. One derivation, two readers — asserted, not
   assumed.
4. `RX_DFA_TABLE` and `RX_DFA_SCAN_EDGE` never name a machine the artifact does
   not contain (§4.2). Concretely: on an accepted artifact, neither fold reads
   `job->rdfa` — the two sites are `dfa_table_name:2665` and
   `dfa_scan_edge_name:2711`.
5. **The `\K`-free premise (P5) — asserted at the ENGINE level, reworded in
   revision 2** (r49 item 12 / sound F4). Rev 1 said "no DFA artifact carries
   the construct", which is FALSE: `-fprefilter '\Ka*'` puts a `\K` machine
   through this emitter as a hybrid, so that assertion would either fire on
   that artifact or pass vacuously. The check is: **`fit.chosen == ENGM_DFA`
   implies the pattern carries no `\K`** — i.e. no artifact whose `_match` and
   `_search` this emitter OWNS. Plus a second, separate assertion for the
   hybrid: on a hybrid whose inlined prefilter is pinned, the emitted
   `rx_search_run` still consumes `window[0][0]` as a lower bound
   (`attempt_position = (size_t)window[0][0];`) and still clamps
   `window_end` from `window[0][1]` — the bound-not-answer shape. Both fail
   loudly if the module gate or the hybrid's window contract ever moves.
6. **The kept `last_accept_position == -1` gate — INVERTED in revision 2**
   (r49 item 1 / sound A2, check F3). Rev 1 said: a coverage check will report
   it never-taken, "the answer is to keep the branch and record here that it is
   deliberately dead". **That records a falsehood.** The gate is load-bearing
   (§3.3); the branch is never taken because THIS CORPUS holds no dead seed at
   `startpos > 0`, which is a corpus fact, not a machine fact. The check
   becomes:
   - the gate is PRESENT in every accepted artifact's emitted text (a grep,
     asserted positively — it must not be "simplified away");
   - a coverage report showing it never-taken is recorded as an observation
     about the corpus, with a pointer to S222, and is NOT an exemption;
   - the emitted comment above the gate names it LOAD-BEARING and says why,
     so the next reader of the artifact gets the fact without this note.
7. **NEW — C3's behavioural fact** (r49 item 3 / sound C3). On an artifact
   that is BOTH predicate-accepted AND `RX_DFA_MATCH "search-filter"`, the
   fallback `<prefix>_match`'s `return -1` is **unreachable**: `rx_search`
   returns 1 with `caps[0][0] == ctx->pos` on every call. Assert it as a
   differential rather than by inspection — over the pinned ∩ search-filter
   population (`[a-z]{0,4096}`, `{0,8192}`, `{0,16384}` are named members,
   VERIFIED this build), at `startpos` values spanning 0 and > 0, on both
   matching and failing subjects, `_match` never returns −1. This is the half
   of rev 1's §1.1 that survives B6, and it is behavioural, so it belongs
   here and not in the bench's column.
8. **NEW — M8: the `rx_info` mirror agrees with the stamp** (r49 item 5 /
   check M8, [DD-13c]'s runtime-mirror pattern). On **every** compiled
   artifact, **both engines**: `rx_info.search_form` equals the
   `<PREFIX>_DFA_START` stamp's value where the artifact contains a DFA scan,
   and is NULL where it does not. This is the fourth structural check and it
   exists because a mirror and a macro are two readers of one derivation — the
   `unanch_start` M2.7 fork is what happens when they are allowed to drift.
   It must run on the VM side too, or it cannot see the NULL case.
9. **NEW — the ENG_UNANCH routing premise (P0)**. The predicate's `fs = fd->s0`
   read is sound only because `ENG_UNANCH` implies `!nfa_has_bot` (§1.2 P0).
   Assert `fs == s1u[UPC_PLAIN]` on every artifact the predicate accepts, in
   the compiler, so that an engine-selection change that routed a BOT-bearing
   machine here fails loudly instead of eliding wrongly.

### 5.5 Size — the prediction NARROWED, and the obvious cleanup is a SEPARATE change

`docs/dev/artifact_size_log.tsv` should move **DOWNWARD** on the accepted
population at the next full-corpus `test-corpus` run. `tests/size/`'s tripwire
pins are maxima, so downward movement cannot trip them, but the log diff is the
reviewer's artifact (`scripts/size_diff`) and the movement should be *predicted
per artifact before the run*, not read off afterwards. §7 item 5.

**What the prediction may claim, and it is less than rev 1 implied** (r49
item 14 / sound B5). Rev 1 said "a whole machine's tables and accessor block
leave every accepted artifact", which invites a reader to expect the artifact's
whole view apparatus to go with it. It does not. `f->viewsel` and `f->views`
come from the SHARED `UnanchStart`, whose `eol`, `endv` and `wctx` are ORs over
`fd` **and** `rd` (`src/gen/emit_dfa.c:2487-2503`). Deleting the reverse
machine's EMISSION leaves in place, on the forward machine:

- its view tables — `if (f->viewsel)` in `emit_machine_tables` (`:4646-4656`)
  emits `<M>_eol_view` / `<M>_end_view` for machine `f` regardless of which
  machine created the flag;
- its demoted (viewed) accept ORDER, i.e. §3.2.0's probe-below-the-edge shape,
  which is exactly what witness (ii) `a*|9` shows: no reverse machine in the
  artifact would still leave the forward probe below the edge.

**So §5.5 predicts the reverse machine's TABLES and ACCESSOR BLOCK only** —
its transition table, accept table, byte-class table, any stay tables, any
scan-edge membership tables, the `<prefix>_reverse_state` accessor block, and
the reverse scan loop's own text. Not the view tables. Not the accept order.

**The views-OR narrowing is its OWN change and must not ride STEP 2.**
Narrowing `views`/`viewsel` to the machine that created the flag would move the
D11 evaluation order — the order that cost 53 divergences — so it needs its own
argument, its own answer-identity evidence and its own sabotage row. Recorded
here as a named candidate with no row and no trigger yet (D77); folding it in
as "a size cleanup" is precisely how a correctness change gets shipped under a
performance heading.

### 5.6 Sabotage rows and their detectors — rebuilt in revision 2

Each row must be shown to fail SOLO, and each must be shown to REACH the
binary (learnings §3, `[MECH-REACH]`). Where two rows share a detector, the
disjointness must be proven the way S213/S214 were — otherwise the second row
is a redundancy finding, not a check.

**IDS: S218–S222, and they are PROVISIONAL.** Rev 1 drafted S217–S221; S217 was
minted the same day by the merged `has_push` row (`tests/mech/sabotages/S217_has_push_npush_estimate_reverts.sh`),
so every id in rev 1 collides (r49 item 6 / check B1). S218–S222 are free as of
`05c984b`, but **a worktree's `sabotages/` is the id space as of ITS branch
point, not the id space** — the S205/S206 incident. Per
`tests/mech/sabotages/CLAUDE.md`, **the range is ARBITRATED BY THE MANAGER AT
MERGE**; the implementation lane numbers from the highest it can see, states
the range in its handback, and renumbers on instruction with a SIMULTANEOUS
substitution.

| row | the sabotage | detector | reach | note |
|---|---|---|---|---|
| **S218** | predicate widened from `up[UPC_PLAIN].accept` to `state_acc_any` (F3) | `VIEW_DECLINE_MANIFEST` all-and-only (§5.2) + a `$`-shaped find-all differential reading `caps[0][0]` | `SAB_REACH` on `$`'s decline; `SAB_REACH_POP` on the manifest floor (≥ 12) | the strongest row; §5.6a |
| **S219** | P3 dropped — TWO ARMS: (i) the P1/P2 conjunct, (ii) the LIVENESS conjunct | none constructed | **UNREACHED, declared** | §5.6b — ships as the phantom-check shape, named |
| **S220** | P2's view/context clause dropped (`eolvar`/`endvar`/`up[u]`) | a `(?m)$`-view start-accepting pattern + `caps[0][0]` | `SAB_REACH_POP` against the classctx manifest | §5.6c — **disjointness from S218 is OWED** |
| **S221** | `caps[0][0] = 0` instead of `= search_from` | a find-all cell at `startpos > 0` reading `caps[0][0]` | `SAB_REACH_POP` on the startpos>0 population | §5.6d — **the population is not counted; that is r49 item 10** |
| **S222** | the stamp forked from the selection (a second predicate at the stamp site) | check 5.4(3) + check 5.4(8) | `SAB_REACH` on the stamp line | §5.6e — **non-vacuity must be demonstrated** |

**SAB_REACH_POP FROM BIRTH on every row whose population [OPT-VEDGE] can
move** (r49 item 9 / check M4 — the S206 / [OPT-4.2] lesson, learned the same
day). [OPT-VEDGE] relaxes scan-edge precondition (3) from "no view on any
member" to "the only view is the END view"; that is the SAME predicate family
S218's and S220's populations are defined by, and it moves them by design.
**S218, S220 and S221 declare `SAB_REACH_POP` in their first commit**, not
after a re-anchor finds them empty:

- **S218** → `docs/dev/opt5m2_m2_changed_patterns.txt | ^\(\?m\) | 12` plus the
  manifest's own all-and-only assertion. (A file floor alone is not enough:
  the file is data, the manifest is the claim. Both, per `[MECH-REACH]`'s
  "a reach probe and a population floor are different claims and expire
  separately".)
- **S220** → the classctx population, floored below M1's measured **8**. A
  population of 8 is thin enough that it must be floored from birth rather
  than watched.
- **S221** → the `startpos > 0` find-all population, floored once §5.6d counts
  it.

#### 5.6a — S218, and why its reach probe is not its population floor

The probe asserts the SITE still answers: on the clean tree, `$` compiles to an
artifact whose predicate verdict is `view`. The floor asserts the WITNESS ROWS
still exist. S70 is why both are needed — a probe alone stays green while
somebody retires every row that reaches it, and the compiler goes on producing
a sentence nobody asks for.

#### 5.6b — S219 has NO CONSTRUCTED WITNESS, and this note says so plainly

r49 item 8 (check M3 + sound F1) asked for a purpose-built synthetic witness
that reaches P3, or an explicit statement that the row ships as the
phantom-check shape. **This lane could not construct one, and the reason is a
derivation rather than a failure of effort. The row ships as the S79/S80
phantom-check shape, named as such.**

*What rev 1 had wrong.* Rev 1 gave `\bx*` as S219's witness. `\bx*` never
reaches P3: M1 measured its verdict as **`classctx`** — P2 declines it first,
because `\b`'s truth depends on the UPCOMING byte and so the start state's
accept varies by class context. And M1 found **ZERO P3-stage declines over
2,845 corpus patterns**.

*Why the P3-discriminating population looks EMPTY, not merely unpopulated.*
Reachability of P3 at all needs `dfa_needs_seed(fd)` (`:2161-2166`), i.e. some
`s1u[u] != s1u[UPC_PLAIN]`. On `ENG_UNANCH`:

1. `(?m)^` and `\G` route to `ENG_ATTEMPT` via `nfa_has_bot`
   (`src/ir/nfa.c:990-993`), so they are not here at all.
2. `(?m)$`'s dependence is on the UPCOMING byte (the class-accept axis,
   `sides_of` at `src/ir/dfa.c:1023`), not on the consumed one, so it creates
   no `s1u` split.
3. `s1u[UPC_PLAIN] == s0 == fs` always (P0 / sound A6).

So only `s1u[WORD]` and `s1u[NL]` can differ from `fs`, and in practice only
`WORD` — a `\b`/`\B` in the start closure. Now the squeeze: **for `fs` to pass
P2, its accept must be invariant in the upcoming byte**, which rules out an
accept reached through `\b`/`\B`, whose truth depends on both neighbours. So a
passing `fs` accepts through a boundary-FREE branch — and a boundary-free
branch sits in the closure under every class context, which makes every seed
state accept as well, and live. P1 passing at `fs` appears to IMPLY P1 and
liveness at every seed.

Candidate shapes this lane worked through and rejected, recorded so the next
author does not repeat them: `\ba|c*` and `\Ba|c*` (the nullable alternative is
in every seed closure, so every seed accepts — P3 passes trivially); `\bz*`
and `\Bz*` (accept varies with the next byte, so `fs` fails P2 and P3 is never
reached); `\bz|c*` (same as the first); `\bz` alone (`s1u[WORD]` is genuinely
dead, but `fs` is not nullable so P1 fails first); `\b(?=\w)` and its
relatives (the lookahead reintroduces the next-byte dependence at `fs`).

*Therefore:*

- **S219 ships with `SAB_EXPECT=UNREACHED` and a `SAB_EXPECT_REASON`** naming
  this derivation, so the matrix scores it as declared-dead rather than
  silently green — and so the `[MECH-REACH]` reverse check reads **NOW
  REACHED** the day somebody builds the witness. That reverse direction is the
  whole value of shipping the row at all.
- **The liveness conjunct's real guard is an ASSERTION IN THE COMPILER**, not
  a sabotage row. An assertion needs no witness: its firing IS the finding.
  This is the correct instrument for a conjunct that defends against a
  machine shape nobody can currently build but nothing forbids.
- **THE OWED MEASUREMENT THAT WOULD SETTLE IT** (D77 — named, not taken here).
  M1 counted P3 *declines* (0). **Nobody has counted P3 EVALUATIONS.** Instrument
  the predicate to emit a stamp distinguishing "P3 not asked" / "P3 asked and
  passed" / "P3 asked and declined" — the same shape as opt5m2's
  `RX_PROBE_PINNED` — and sweep the corpus **under the force axis as well as
  the default**. Three outcomes: a non-zero "asked and passed" count makes the
  conjunct live and the row worth a witness hunt; a zero makes P3 provably
  unreachable on this corpus and the row a documented redundancy; and a
  decline is the witness itself. **Trigger: before the implementation lane
  ships S219 as anything other than `UNREACHED`.**

#### 5.6c — S220's disjointness from S218 is an OWED MEASUREMENT

Rev 1 already noted the overlap. It is still unresolved, the classctx
population is **8** (M1), and 8 is exactly the scale at which "the second row
is a redundancy finding, not a check" becomes the likely answer. **Before
shipping**: run S218 and S220 solo against each other's detectors and show a
member of S220's population that S218's detector does NOT catch. If none
exists, S220 is recorded as a redundancy finding — which is a real result and
is what `unanch_start`'s own wave-C comment does about its widened bit ("it
therefore ships NO sabotage row: a check with no failing direction is exactly
what this file's own neighbouring comment warns about"). This is the S79/S80
rule and it is the MINOR item r49 raised as [check 6].

#### 5.6d — S221's detector population is NOT COUNTED

r49 item 10 / check M5. The row's detector is "any find-all cell at
`startpos > 0`", and nobody has counted them. The reason it is plausibly thin
is structural: plain `m`/`n` `.rxt` cells are `startpos`-0; only the opt-in
`ms`/`ns` forms carry a nonzero `startpos`. There is no suite, floor or
manifest saying which of the **175** pinned artifacts have such coverage.

**Two acceptable discharges, and the row does not ship without one:**

1. **COUNT IT.** Over the 175, count `ms`/`ns` cells with `startpos > 0`
   (`grep -rhE '^(ms|ns) '` across `tests/**/*.rxt`, joined to the pinned
   pattern list), and floor the count in `SAB_REACH_POP`. If the count is
   small, say so in the row's header rather than shipping a thin population
   silently.
2. **BUILD SYNTHETIC WITNESSES.** Add `ms` cells at `startpos > 0` for a named
   handful of pinned patterns — `a*`, `[a-z]{0,64}`, `[a-z]{0,4096}` and one
   seeded shape — reading `caps[0][0]` explicitly, oracle-verified. These are
   corpus additions, so they belong to the implementation lane and are named
   here so it does not discover the gap at check-writing time.

This matters more than its severity suggests, because §3.4(e) is invisible to
every single-search-at-0 test, which is most of the corpus.

#### 5.6e — S222 must be shown NON-VACUOUS

r49's CONFIRMED-7 / [check 7]. The stamp/body third-term check follows the
`run_dfa_stamps` provenance discipline correctly, but a stamp-fork sabotage can
pass vacuously: if the forked second predicate happens to agree with the first
on every corpus artifact, the row is green and certifies nothing.

**How to show non-vacuity**, and it must be demonstrated in the row's own
header with the measurement, not asserted: fork the stamp site to a predicate
that DISAGREES on a named artifact — the natural choice is the widened
`state_acc_any` read, since §5.2's manifest already names ≥ 12 artifacts on
which widened and narrowed disagree. `SAB_REACH` then asserts the stamp LINE
is present on a named artifact, and the failing direction is check 5.4(3)
reporting `<PREFIX>_DFA_START "pinned"` on an artifact that still contains
`rewind_position`. Because that construction reuses S218's discriminating
population, **S222's disjointness from S218 must be argued too**: they sabotage
different SITES (the selection vs the stamp) and 5.4(3) is what distinguishes
them, so the row's header states that rather than leaving it implied.

### 5.7 What the bench's AFTER cannot see, so the in-tree checks must

The bench measures TIME and reads STAMPS over **its own** pattern set. It does
run an answer-agreement pass (O-12 §6 records 3 disagreeing rows of 1,885, 0
groups), so it is not answer-blind — but:

- Its population is the bench's patterns, not the corpus's 2,845. **No member
  of `VIEW_DECLINE_MANIFEST` is known to be in it** — the 16 M2 measured are
  all `(?m)…$` shapes and the bench's sets carry none. The miscompile in
  §3.4(a) is therefore entirely the in-tree checks' to catch.
- It cannot see artifact SIZE movement on non-bench patterns, nor compiler CPU.
- It cannot distinguish "the elision fired and was right" from "the elision
  declined" except through the stamp — which is why check 5.4(3), tying the stamp
  to the body, is what makes the bench's stamp-bucketing trustworthy at all.
- Conversely, the in-tree checks cannot see the ~2×. **The division is: in-tree
  owns correctness and structure, the bench owns the number.** Neither is a
  substitute for the other, and the acceptance frame in §0 is only meaningful
  once the in-tree side is green.

---

## 6. D80 spec deltas — revised

Contract changes land in `docs/spec/` in the SAME change; a reviewer rejects a
contract change without its spec hunk. **This is a design note, so nothing in
`docs/spec/` is edited here** — this table is what the implementation lane
lands under D80.

| # | file | section | delta |
|---|---|---|---|
| 1 | `docs/spec/tuning.md` | new **§2.19** | `-fno-start-pinned` / `PCREC_NO_START_PINNED` (bit 22): what **axis J** is, what the denied build does instead, the answer-identity promise, and the D82 note that the flag removes a candidate object rather than branching |
| 2 | `docs/spec/tuning.md` | **§3** (the DFA side's own stamps) | a `<PREFIX>_DFA_START` bullet: value set `"pinned"` / `"reverse-pass"`, and that a HYBRID carries it (the `RX_DFA_SCAN_EDGE` reason — the hybrid inlines this scan) |
| 3 | `docs/spec/tuning.md` | **§3.2** (the mirror list) | **a THIRD mirror bullet — NEW in revision 2** (r49 MINOR). See the wording below |
| 4 | `docs/spec/match_api.md` | **§6** (the `rx_info` struct block) | **the `search_form` member — NEW in revision 2** (r49 item 5). The hunk is in §4.2; it appends at the END of the struct, after `nentries`, and its guard is `pcrec_artifact_has_dfa_scan`, NOT `fit.chosen == ENGM_DFA` |
| 5 | `docs/spec/match_api.md` | **§6.3** | `RX_DFA_START` added to the stamp value-set table, classified under **(a) SELECTION FACTS** — see below |
| 6 | `docs/spec/match_api.md` | **§6.3** | the mirror-COUNT prose moves from two mirrors to three (`match_form`, plus whatever §6.3 already counts, plus `search_form`) |
| 7 | `docs/spec/match_api.md` | **§6** and elsewhere | the `abi` sentences — found by **D94's grep** (§4.4), not by this list |
| 8 | `docs/spec/match_api.md` | **§3.1** | one paragraph, mirroring §3.2's treatment of `RX_DFA_MATCH`: the two search forms are **answer-identical** and differ only in cost; `caps[0][0]`'s contract is unchanged, including the absolute-offset sentence and the zero-length-is-success convention, both of which the elision depends on rather than alters. **Add one sentence naming the `last_accept_position == -1` gate's role** — a search that seeds into a dead state at `startpos > 0` correctly returns "no match", per §3.3 |
| 9 | `docs/spec/limits.md` | — | **no change**, deliberately (§4.3) |
| 10 | `docs/guide/` | — | a pointer only if an existing page already names the two-pass cost; the guide points at the spec and never restates it |
| 11 | — | — | **NO fallback (`_match`) hunk today**, and that is correct per §3.5 and D77 — the trigger is [OPT-VEDGE]'s landing, recorded so the absence is deliberate rather than forgotten |

### 6.1 The `tuning.md` §3.2 mirror bullet — the wording, for the implementation lane

**This note does NOT edit `tuning.md`.** The bullet the implementation lane
adds should say, in §3.2's existing voice:

> **`rx_info.search_form`** mirrors `<PREFIX>_DFA_START`. It is the third
> `rx_info` mirror of a DFA selection stamp, and it exists for
> `match_form`'s reason rather than a new one: a header-less consumer that
> `dlopen`s an artifact needs to know which form of `<prefix>_search` it
> linked, because the two differ by roughly a factor of two in cost on a
> counted class run and not at all in answers. Unlike `match_form`, it is
> **non-NULL on a VM HYBRID as well**, because a hybrid inlines this same
> search body as its prefilter; it is NULL only on a plain VM artifact with
> no DFA scan.

### 6.2 §6.3's classification: `RX_DFA_START` is a **(a) SELECTION FACT**

r49 item 5 / r49cons's Q2 analysis. `docs/spec/match_api.md` §6.3 sorts the
observability macros into classes, and `RX_DFA_START` joins **(a) SELECTION
FACTS** with the **same IFF** as `<PREFIX>_DFA_TABLE`:

> the macro is defined **iff** the artifact contains a DFA scan, and its value
> names the object axis J selected.

Not a capability macro, not a limit, not a diagnostic. The IFF matters because
it is what makes check 5.4(8) writable at all: a field-equals-stamp assertion
needs a defined predicate for "should this artifact have one", and
"contains a DFA scan" is that predicate for both the macro and the mirror.

---

## 7. Measurements owed, each with its trigger (D77)

None of these could be taken by this lane (box hold; and the design needs none
of them to be *written*). Each names what would make it necessary.

| # | measurement | trigger — do not take it before this |
|---|---|---|
| 1 | ~~**N_pinned**~~ **DONE** — 175, all pure DFA, 0 hybrids on the default axis | *was*: before the D6 panel. TAKEN by lane opt5m2 `24ba0c4`, `docs/dev/opt5_step2_premeasure.md` M1 |
| 2 | ~~**N_declined_by_view** re-counted~~ **DONE, and it changed the check** — 16 at today's tree, all `(?m)…$` | *was*: before writing the widened-bit row's assertion. TAKEN (memo M2) — **and the taking is what expired its independence**, so §5.2 pins a NAMED MANIFEST rather than the number (r49 item 7) |
| 3 | ~~**Which precondition declines `(?:[a-z]{0,2048})\z`**~~ **DONE** — precondition (3), the position view | *was*: before chartering the view-tolerant scan edge. TAKEN (memo M3), confirmed by a discriminating probe pair; the note's §2 INFERENCE was right |
| 4 | **The nine-rung `bounded@0.2` AFTER at the STEP 2 pin** | the acceptance frame itself (§0). The instrument is standing — O-12 ask (iv) — and the per-rung predictions are recorded above BEFORE the run, which is the point |
| 5 | **Artifact-size movement on the accepted population**, per artifact, predicted then compared | at the first full-corpus `test-corpus` run after landing. Predicted downward (§5.5) |
| 6 | **Compiler CPU with the reverse machine's BUILD skipped, not just its emission** | only if (5) or a user report shows the build cost matters. The comparable number exists: `[ENG-ABS]`'s optional machine cost **+46 % compiler CPU** on the resource shapes (24.3 → 35.9 s on `[a-z]{0,30000}`, r41 S1), so the symmetric saving is plausible and measurable. **Not in STEP 2** (§8 Q5) |
| 7 | **The `capture_spans == NULL` run-time skip** — the reverse pass is run today even when no caller reads its result, and `match_start_position` is then used only by an early return | **DO NOT BUILD.** No measured caller exists: the bench's driver reports spans, so its find-all loop needs the end and its agreement pass needs the start. The trigger is a measured caller that searches without captures. Recorded so the observation is not lost, not so it is acted on |
| 8 | O-12 asks (ii)/(v): the per-run edge-selection boundary, the fixed term's size, the hybrid trade | **not STEP 2's.** They are STEP 1's fixed entry term — `year4` ×1.07–1.11 on a 4-count run, `dotted4` ×1.11 (ledger §7.3) — a different mechanism at a different site. A "skip-below-k" knob is a NUMBER and would be born as a `limits.def` row (D90). Its own row |
| **9** | **`N_hybrid_pinned` UNDER THE FORCE AXIS** — the count of hybrids the predicate accepts when `-fprefilter` is in play, with its command shape in §5.2 | **NEW in revision 2** (r49 item 12 / sound B2). M1's 0 is a DEFAULT-axis number and `make test-axes` runs the force axis over a corpus holding `\K` and nullable patterns — the K35 shape. **Trigger: before §5.2's hybrid line is written as anything but "not yet counted", and before the implementation declares its axis sweep complete** |
| **10** | **P3 EVALUATION count** (not decline count): how often the seed conjunct is ASKED, default axis and force axis | **NEW in revision 2** (r49 item 8 / check M3, sound F1). M1 counted declines (0) and nobody counted evaluations, so "P3 is unreachable" and "P3 is reachable but never declines" are not yet distinguished. The instrument is opt5m2's `RX_PROBE_PINNED` shape. **Trigger: before the implementation ships S219 as anything other than `SAB_EXPECT=UNREACHED`** (§5.6b) |
| **11** | **`N_pinned ∩ search-filter`** over the corpus — how many of the 175 also stamp `RX_DFA_MATCH "search-filter"` | **NEW in revision 2** (r49 item 11 / sound B6, C3). This is C3's population, and §1.1 currently names four VERIFIED members rather than a count. **Trigger: before check 5.4(7)'s differential is floored** |
| **12** | **The `startpos > 0` find-all population over the 175** | **NEW in revision 2** (r49 item 10 / check M5). §5.6d names the two acceptable discharges. **Trigger: before S221 ships** |
| **13** | **S220's disjointness from S218** — a member of the classctx population S218's detector does NOT catch | **NEW in revision 2** (r49 MINOR / check 6). **Trigger: before S220 ships**; if empty, S220 is a redundancy finding (§5.6c) |
| **14** | **The P2-relaxation split**: of M1's 47 `view` declines, how many carry a view variant whose accept bit AGREES with the base | **NEW in revision 2** (r49 item 13 / sound B4). P2 is deliberately stricter than soundness needs and it costs population. **Trigger: a bench or corpus customer lands in that group** — and note [OPT-VEDGE] moves the same population from the other side, so the two must be sequenced (§1.2 P2) |

---

## 8. The seven questions — **each with its RULING STATUS** (revision 2)

Frank answered all seven on 2026-09-01, and **the r49 panel left every ruling
standing** (review §1: "Frank's seven Q-rulings stand unchanged by the panel").
Revision 2 keeps the questions and marks each one, because a note that still
reads as "open questions" invites an implementation lane to re-open a settled
call.

**Q1 — Is STEP 2 the start-pinned elision only?**
**RULED YES. Stands.** Rev 1 recommended yes; the panel found no reason to
revisit, and sound D2 strengthens the argument by converting §1.3's
impossibility prose into a cost argument that reaches the same conclusion
(build start-pinned and nothing else). Recorded as settled.

**Q2 — Does the new stamp get an `rx_info` mirror (`search_form`)?**
**RULED YES — AGAINST rev 1's recommendation. Stands, and revision 2
implements it.** Rev 1 recommended NO, matching `RX_DFA_TABLE` and
`RX_DFA_SCAN_EDGE`. Frank ruled the other way ("a great idea", with a direction
note questioning which stamps should remain `#define`s at all). The trace is
kept in §4.2 so a reader sees the argument that lost; the struct hunk, the
guard choice and check 5.4(8) are in §4.2, §6 and §5.4. **This is the only one
of the seven that was ruled against the note's own recommendation**, and it is
the one an implementation lane is most likely to get wrong by reading rev 1.

**Q3 — The stamp's spelling** (`<PREFIX>_DFA_START "pinned" | "reverse-pass"`).
**RULED: the manager's call, per `pcrec-dd13b-syntax-is-managers`. Stands.**
Offered, not settled by this note. Revision 2 adds one consideration the
manager may want: the mirror field's name (`search_form`) is now fixed by
Frank's Q2 ruling and by `match_form`'s precedent, so a stamp spelling that
does not read as that field's macro would break the pairing check 5.4(8)
depends on for readability.

**Q4 — Charter the VIEW-TOLERANT SCAN EDGE as its own row now?**
**RULED YES — it is [OPT-VEDGE], chartered 2026-09-01 ("agree"). Stands, and
its scope GREW.** Rev 1 opened it on §7 item 3's measurement, which is now
taken (precondition (3), memo M3). Revision 2 records that the row has a
SECOND customer nobody had connected to it: the bench's ×37 failing-call band
(§3.5 / sound C2). One mechanism, two customers.

**Q5 — Skip the reverse machine's BUILD as well as its emission?**
**RULED NOT IN STEP 2. Stands.** Skipping the emission is required for honesty
(a built-but-unemitted machine feeding stamps is the defect §4.2 describes);
skipping the build is a separate compiler-CPU optimization with its own trigger
(§7 item 6).

**Q6 — The fifth `abi` site.**
**RULED AND CLOSED — this is D94.** Frank: "agree. this is the right
direction". The ritual now says "every reader of the number, found by grep",
`CLAUDE.md`'s situation-index row says so, and the stale `match_api.md:159`
was fixed at the w12 merge. **Revision 2 deletes rev 1's recommendation text
and replaces §4.4 with the grep** (r49 item 17). Nothing is owed.

**Q7 — Do O-12 asks (ii) and (v) ride STEP 2's charter?**
**RULED NO. Stands** (§7 item 8). Revision 2 adds the reinforcing reason from
§0's two-instrument frame: the acceptance table now carries an explicit
CONTROL family (the `unwrapped` match rungs, predicted flat) alongside the
customers, and folding a second mechanism in would make a moving control
unreadable.

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
  — **16 corpus artifacts at today's tree, all `(?m)…$`** (memo M2; [M6.2]
  wave C's 21 was a different consumer at an older tree). CONFIRMED by the
  panel (check F2), with the caveat that re-measuring it for this check
  expired its independence — §5.2.
- **F4** (§0) The acceptance instrument's nine rungs are the
  `large-subject-throughput` (find-all) band, not a `match` band — the charter
  brief's wording; ledger §3's own table heading is the source.
- **F5** (§4.4) The `abi` ritual's "FOUR sites" is incomplete: a fifth reader,
  `docs/spec/match_api.md:159`, was already stale at `13` after `[CC-CLANG]`'s
  bump to 14. **DISCHARGED**: ruled as **D94** (the site list is every reader
  of the number, found by grep) and the stale site fixed at the w12 merge; the
  grep now returns five readers plus the (B) pin (§4.4).

### Findings raised by revision 2 itself

- **F6** (§3.2) **Revision 1's Claim A was false.** The accept probe is an
  axis-E object (`dfa_accs`, `src/gen/emit_dfa.c:3572-3579`) and sits BELOW the
  scan edges on any `scalar-viewed` or `by-class` artifact; `acc_viewed_applies`
  reads `us->views`, which is an OR over BOTH machines, so a `\b` in the
  REVERSE machine alone demotes the FORWARD probe. Two emitted witnesses,
  `[a-z]{0,8}|9$` and `a*|\b9`. The answer was never at risk; the proof was.
- **F7** (§3.3) **Revision 1 called a load-bearing gate dead.** The
  `last_accept_position == -1` return is the correct answer on a dead seed at
  `startpos > 0`, and rev 1's "record here that it is deliberately dead" would
  have written a falsehood a later simplification acts on.
- **F8** (§4.2) **The [DD-13c] append discipline and the review's wording
  disagree, and the discipline wins.** "Append after `match_form`" was true
  when `match_form` was the last member; `name` and `nentries` now follow it,
  so appending "after `match_form`" would move their offsets — the exact thing
  the discipline exists to prevent. The hunk appends at the END.
- **F9** (§5.6b) **P3's discriminating population appears EMPTY on
  `ENG_UNANCH`, not merely unpopulated** — a derivation, not a census result.
  The row therefore ships declared `UNREACHED` and the liveness conjunct's real
  guard is a compiler assertion. §7 item 10 is the measurement that would
  settle it.
- **F10** (§5.2) **Re-measuring a control's expected value FOR the check it
  controls destroys the property that made it strong.** M2's 16 was taken with
  `member_ok`'s own body — the body this note proposes to share with the
  implementation — so probe and feature would call one function. The manifest
  replaces the count for that reason, not merely because counts drift.

---

## 10. Revision 2 — r49 disposition table

One row per item in `docs/dev/reviews/2026-09-01-r49-opt5-step2.md` §2, plus
each MINOR. **CONFIRMED-class rows name the sentence added**, so a reviewer can
verify item by item without re-reading the note.

### BLOCKER-class

| r49 § | item | disposition | note sections | what changed |
|---|---|---|---|---|
| 1 | [sound A1] Claim A false on axis-E viewed/by-class artifacts | **WORKED** | §3.2 (rewritten), §3.2.0 (new), §3.2.1 (new), §3.3 (rewritten), §5.4(6), §9 F6 | The proof is re-derived FROM THE EMITTER: §3.2.0 is a site-by-site table of every recording site with function name and line (`emit_scan_loop` `:4696`/`:4697`/`:4699-4703`/`:4714`-`:4717`; `dfa_accs` `:3572-3579`; `acc_viewed_applies` `:3511`; `unanch_start`'s views OR `:2487-2503`; `dir_fwd_skip` `:3992-4014`; `emit_scan_edge` `:4473-4568`; `acc_emit_tail_by_class` `:3530-3570`). Claim A now reads "the forward loop's FIRST iteration records `last_accept_position = q` for some `q >= search_from`". Both witnesses (`[a-z]{0,8}\|9$`, `a*\|\b9`) plus the `[a-z]{0,64}` control were EMITTED HERE and quoted. Added sentence: *"What Claim A does NOT say, and rev 1 wrongly assumed it did: it does not say the recorded position is `search_from`."* |
| 2 | [sound A2] P3 gains a LIVENESS conjunct + the dead-token hazard note | **WORKED** | §1.2 P3, §3.4(b′), §5.4(6), §5.6b | P3 reads *"every seed state is LIVE and satisfies P1 and P2 as well — i.e. the predicate DECLINES when any `d->s1u[u] < 0`"*, cited to `src/ir/dfa.c:1249-1258` / `:1113-1116` and `dfa_premul` `:2205-2215`. The hazard is its OWN block-quoted paragraph: *"PRE-EXISTING HAZARD, NOT STEP 2's TO FIX … Nothing in STEP 2, or after it, may rely on 'a dead token records nothing'."* The implementation ASSERTS the conjunct (stated in §1.2 and §5.6b). |
| 3 | [sound C1+C2] the failing-call bound is unsound; C3 joins §5.4 | **CLOSED, as ruled** | §3.5 (new), §1.1, §5.4(7), §7 item 11 | §3.5 records the closure with the witness reproduced from the emitted artifact (`a*b` under `-fno-anchored-dfa`: `rx_forward_next_state[6] = { 0, 0, 3, … }`, `tr[fs]['a'] == fs`, legend state 1 = `"b"` ACCEPTING; `"aab"` at pos 0 expects 3, any stopped-progress bound returns −1). States **"no `_match` change in STEP 2"**, names [OPT-VEDGE] as the population's owner, and records both sound-but-untaken spellings. C3 becomes structural check **5.4(7)**: on a pinned ∩ `search-filter` artifact the fallback's `return -1` is unreachable. |
| 4 | [cons F-B / sound E3] axis letter H is taken; use J | **WORKED** | §4.1, §4.2, §6 rows 1-2, §10 | Global rename. §4.1 cites the collision (`:4317` axis H, `:4349` axis I, `scan_edge_of` `:2694-2695`) and names the silent failure mode (`--list-axes` would print two axes with one letter). Deny flag spelling `-fno-start-pinned` / `PCREC_NO_START_PINNED` unchanged; every stamp/axis mention says J. |
| 5 | [cons F-A / E2] Q2 superseded — the `rx_info.search_form` mirror is approved | **WORKED** | §4.2, §6 rows 3-6, §6.1, §6.2, §5.4(8), §8 Q2 | §4.2's "recommend NO" text is replaced by the ruling, with a one-line trace of the losing argument. The struct hunk is written out with its comment, appending at the END after `nentries` (see MINOR/F8 below). The guard is `pcrec_artifact_has_dfa_scan`, NOT `fit.chosen == ENGM_DFA`, derived from `emit_info_def`'s own note at `:1690-1697`. §6.2 classifies the stamp under **(a) SELECTION FACTS** with the same IFF as `_DFA_TABLE`. §5.4(8) is check **M8**: field == stamp on every artifact, both engines, including the NULL case. |
| 6 | [check B1] sabotage ids S217-S221 are taken | **WORKED** | §5.6 | Ids are **S218-S222**, and §5.6 states *"the range is ARBITRATED BY THE MANAGER AT MERGE"* per `tests/mech/sabotages/CLAUDE.md`, with the S205/S206 incident's rule (a worktree's id space is as of its branch point) and the simultaneous-substitution requirement. |

### MAJOR

| r49 § | item | disposition | note sections | what changed |
|---|---|---|---|---|
| 7 | [check M2] pin the CLASS as a named manifest, never the count 16 | **WORKED** | §5.2, §3.4(a), §9 F10 | `VIEW_DECLINE_MANIFEST` is defined by its SELECTOR (`state_acc_any(fs)` true and `fs->up[UPC_PLAIN].accept` 0, on an `unanchored` artifact), asserted all-and-only, floored at ≥ 12, with five named irreplaceable shape-anchors. §5.2 explains *why* a count is not a control here: the independence expired when M2 re-measured it for this check using `member_ok`'s own body, so probe and feature would call one function once P2 is shared. |
| 8 | [check M3 + sound F1] the fseed/P3 row's witness never reaches P3 | **WORKED — as the "cannot construct" branch the brief allows** | §5.6b, §3.4(b), §7 item 10, §9 F9 | §5.6b gives the DERIVATION that the P3-discriminating population looks empty on `ENG_UNANCH` (routing of `(?m)^`/`\G` away via `nfa_has_bot`; `(?m)$`'s next-byte axis creating no `s1u` split; `s1u[PLAIN] == fs`; and the squeeze — a P2-passing `fs` accepts through a boundary-free branch, which sits in every seed closure). Six candidate shapes are named and rejected. **The row ships declared `SAB_EXPECT=UNREACHED` with a reason — the S79/S80 phantom-check shape, named as such** — and the liveness conjunct's real guard is a compiler assertion. §7 item 10 is the P3-EVALUATION count that would settle reachability. |
| 9 | [check M4] SAB_REACH_POP from birth on rows [OPT-VEDGE] can move | **WORKED** | §5.6 | Marked rows: **S218, S220, S221**, each with its floor named (`opt5m2_m2_changed_patterns.txt` ≥ 12; the classctx population below M1's 8; the startpos>0 population once counted). The paragraph cites the S206/[OPT-4.2] lesson and `[MECH-REACH]`'s "a reach probe and a population floor are different claims and expire separately". |
| 10 | [check M5] the absolute-offset row needs a counted `startpos>0` population | **WORKED as a named obligation** | §5.6d, §7 item 12 | §5.6d states the structural reason it is plausibly thin (plain `m`/`n` cells are startpos-0; only `ms`/`ns` carry nonzero) and gives **two acceptable discharges** — count the `ms`/`ns` cells over the 175 and floor it, or add synthetic `ms` witnesses for named pinned patterns (`a*`, `[a-z]{0,64}`, `[a-z]{0,4096}`, one seeded shape). **The row does not ship without one.** |
| 11 | [check M9 + sound B6] `cls-atleast-4096` becomes an in-tree named witness; quantify §1.1 | **WORKED** | §0 instrument 1, §1.1, §5.4, §7 item 11 | `cls-atleast-4096` = `[a-z]{4096,}`, VERIFIED here: it stamps `RX_DFA_PREFILTER "byte-class"` and `rx_forward_is_accepting[4] = {0,0,1,1}` — the start state does NOT accept, so P1 fails and the predicate DECLINES. §0 names it an in-tree NAMED WITNESS ("must not move") rather than bench prose. §1.1 is rewritten: the ×37 exhibit is the `\z` whole form, view-declined, **[OPT-VEDGE]'s customer, NOT STEP 2's**; the pinned counted-ladder `search-filter` rungs get C3's fact instead, with a VERIFIED four-row stamp table. |
| 12 | [sound B1/B2] P5 is false as worded; N_hybrid_pinned must be counted under the force axis | **WORKED** | §1.2 P5, §1.2 blast radius, §3.4(d), §5.4(5), §5.2, §7 item 9 | P5 is reworded to the ENGINE-level fact (`fit.chosen == ENGM_DFA` implies no `\K`), with the `-fprefilter '\Ka*'` witness EMITTED HERE (`RX_ENGINE "vm"`, `rx_forward_is_accepting[2] = {1,1}`) and the bound-not-answer sentence quoting the emitted `rx_search_run`. §5.4(5) asserts the engine-level fact plus a second hybrid-window assertion. **N_hybrid_pinned is written as an OWED measurement with its command shape (§5.2, §7 item 9), not as ~0** — the check prints it and asserts nothing. |
| 13 | [sound B4] P2 is stricter than soundness needs | **WORKED** | §1.2 P2, §7 item 14 | Recorded as a **DELIBERATE CONSERVATIVE CHOICE** with the reason (one derivation for a fact two passes read) and the cost named (some of M1's 47 `view` declines). The relaxing measurement is §7 item 14 with its D77 trigger, plus the note that [OPT-VEDGE] moves the same population from the other side so the two must be sequenced. |
| 14 | [sound B5] §5.5's size prediction narrows; the views-OR cleanup is its own change | **WORKED** | §5.5 | The prediction is narrowed to **the reverse machine's tables and accessor block only** — enumerated — with the reason (`views`/`viewsel` are ORs over both machines, `:2487-2503`; `emit_machine_tables` `:4646-4656` emits view tables regardless of which machine set the flag; witness (ii) shows the demoted accept order survives). The views-OR narrowing is recorded as **its own candidate change** with no row and no trigger, and the note says folding it in is how a correctness change ships under a performance heading. |
| 15 | [sound D2] §1.3's impossibility prose becomes a cost argument | **WORKED** | §1.3 | The bullet now reads *"Tracking the origin forward on a multi-origin machine is SOUND and NOT FREE — a COST argument, not an impossibility one"*, names Laurikari-style TDFA explicitly, states the cost (a register copy per transition, a larger build — the very per-step cost STEP 2 removes), and carries the **D77 trigger: re-evaluate WHEN STEP 3 lands**. Added sentence: *"Nobody should carry away 'forward origin tracking is unsound'; it is untaken, on cost."* Prose and table now agree. |
| 16 | [sound E4] the two stamp folds must drop the reverse machine; movements go in a prediction table | **WORKED** | §4.2, §5.4(4) | The two sites are cited in a table (`dfa_table_name` `:2664-2666`, the `rdfa` read at `:2665`; `dfa_scan_edge_name` `:2706-2715`, the fold at `:2711`). A **PREDICTED STAMP MOVEMENTS** table follows, written before the change, with five artifact classes including the `"mixed"` → form-name movements and the `mc2` scan-edge case. §5.4(4) asserts the negative form. |
| 17 | [cons F-C/F-D/E1 + Q3] staleness sweep; §0 adopts the two-instrument frame with the O-13/O-14 rule | **WORKED — with one deviation, flagged** | §0, §4.4, §8 Q6, §9 F5 | §4.4 is rewritten around **D94's grep** (the two grep commands are given; the five readers plus the (B) pin are shown as a dated snapshot the implementation must NOT copy). abi is 15, STEP 2 writes 16, and the serialization ambiguity is gone. F5/Q6 are marked DISCHARGED, naming what discharged them (the w12 merge fixed `match_api.md:159`; D94 amended the ritual). §0 becomes a two-instrument table with the CONTROL/CUSTOMER split and a provenance rule. **DEVIATION: the review carries r49cons's frame table only as a Q3 SUMMARY, not verbatim** — the verbatim table is not in the review file — so §0's table is reconstructed from that summary plus O-13 §2/§2(c) and this build's own stamp probes. **`[O-14 PENDING — manager fills at merge]` markers are in place: O-14 had NOT landed** (outbox last written 2026-09-01 18:47, newest message `## O-13`). |
| 18 | [sound A6] state the `fs == s1u[PLAIN]` routing dependency | **WORKED** | §1.2 P0 (new), §5.4(9) | A new predicate clause **P0** states the dependency with its citations (`src/core/compile.c:1096`, `src/ir/nfa.c:990-993`, `src/ir/dfa.c:1249-1258`) and the reason it must be written rather than inherited: `dfa_needs_seed` (`:2161-2166`) compares only `s1u[u]` across `u` and would not notice an `s0 != s1u[PLAIN]` split, and `seed_emit_constant` (`:3496-3502`) then emits `s0` unconditionally. Added sentence: *"A future engine-selection change that routed a BOT-bearing machine here would break the elision silently."* Check **5.4(9)** asserts it in the compiler. |

### MINOR

| item | disposition | where |
|---|---|---|
| [cons Q4] `design/CLAUDE.md` entry rides rev 2 | **WORKED** — the existing rev-1 entry is REVISED in place, not duplicated | `docs/design/CLAUDE.md` |
| the [OPT-VEDGE] back-pointer | **WORKED** — added everywhere the population is discussed | §0 instrument 2, §1.1, §3.5, §1.2 P2, §7 item 14 |
| `tuning.md` §3.2 mirror bullet | **WORKED** — the bullet's WORDING is written out in §6.1; **`tuning.md` itself is NOT edited**, per the brief and D80 (this is a design note) | §6 row 3, §6.1 |
| [check 6] S-classctx row's disjointness measured before shipping | **WORKED as a named obligation** | §5.6c, §7 item 13 |
| [check 7] the stamp-fork sabotage must be shown non-vacuous | **WORKED** — §5.6e says HOW (fork to the widened `state_acc_any` read, which §5.2's manifest already gives ≥ 12 disagreeing artifacts), and requires the demonstration in the row's own header with the measurement; its disjointness from S218 is argued (different SITES, distinguished by check 5.4(3)) | §5.6e |

### Where revision 2 disagrees with the review or the brief

Recorded as findings rather than silent deviations, per the brief:

1. **The `rx_info` hunk appends at the END, after `nentries` — not "after
   `match_form`"** (§9 F8). [DD-13c]'s discipline is "append at the end so no
   existing member's offset moves"; `match_form` was the last member when that
   was written and no longer is.
2. **r49cons's reconciled frame table is not in the review verbatim** (item 17
   above). §0's table is a reconstruction from the Q3 summary plus O-13 and
   this build's stamp probes. The manager should check it against r49cons's
   delivery message.
3. **S219 has no witness and this note says so** (item 8). The brief allowed
   this branch explicitly; the derivation in §5.6b is the argument that the
   population is empty rather than merely unpopulated, and §7 item 10 is how
   to settle it.
4. **The two P3 arms share one id.** The brief said S218-S222 (five ids) and
   rev 1 had five rows; revision 2 has a sixth failure direction (the liveness
   conjunct). Rather than mint a sixth id a worktree cannot safely claim, S219
   carries both arms and the note flags it for the manager's arbitration.
