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
it is the obvious way to get this wrong (sabotage S220, §5).

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
**S222** (the liveness conjunct dropped), plus the assertion itself.

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
