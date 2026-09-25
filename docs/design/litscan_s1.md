# `[OPT-LITSCAN]` S1: a pinned literal run goes to the prefilter, and a dominated pre-check is elided

**Revision 2 — OPTION B** (lane `s1b`, 2026-09-25, branch `lane/s1b` from
main `4976f385`, abi 32), per D122 ADDENDUM 4. Revision 1 was lane
`s1design` (from `b5c1423b`), light-panelled in
`docs/dev/reviews/2026-09-25-r1-litscan-s1.md` with every disposition applied
by lane `s1rev`. **Design only.** Nothing under `src/`, `cli/`, `lib/` or
`tests/` changed. No darwin clock was read: every number below is a COUNT
taken off an artifact, or a Ryzen measurement from the bench's own records
(`capability@0.1`, reduced with `pcrecbench.reduce`, as in
`cycle2_admitfix_reading.md` §0.1). Predictions are labelled as predictions.
Instruments: `docs/dev/optloop/s1/` (its `CLAUDE.md` lists them).

Governing rulings: D122 and its ADDENDA 1-4 (4 is this revision's charter:
"make sure such a change is well-considered and critiqued — it's close to the
vital organs"), and Frank's §9 rulings (Q1 conversion in S1 as a separate
last commit; Q2 C2 left out; Q3 → `[OPT-VMSEED]`; Q4 closed).
`compare_stack.md` §6.1 S1 is the charter. The row is plan `[OPT-LITSCAN]`.

A FULL D6 panel reviews this revision (addendum 4 item 3: answer soundness,
selection/axis semantics, the hybrid/VM consumer contract) before any build.

---

## R. What changed from the panelled version, and why

Read this first; §0-§11 below are the revised note in full.

**R1. The decision moved out of `prefix_k.c` (addendum 4 item 1).**
Revision 1 turned `pcrec_prefix_ksets`' answer into a three-row stage-1
table (`run-pinned` / `cost-model` / `none`) whose output was fed to the
existing `offset-set` rows as an OFFSET SET. That table is WITHDRAWN: it
steered the emitted form through a second selector. Now:
- `prefix_k.c` stays a pure ANALYSIS and additionally PUBLISHES one fact,
  "`Job.req_run` is pinned at offset `o` from every match's start"
  (`PrefixKSets.run_pinned` / `run_o`, §1.1), read off the walk it already
  runs. Its selection code, its constants and its "scan must move" rule are
  untouched, so its comment "`o->k[0]` ALWAYS role B … never the scan" stays
  TRUE and is no longer an edit (S1-4's second invariant edit is dropped, R6).
- The DECISION is a PAIR of new rows at the head of `dfa_pfs[]`,
  `run-pinned-bounded` / `run-pinned` (§1.2), mirroring the existing
  bounded/unbounded pairs. They emit the EXISTING `<p>_ofsskip` machinery
  (`pf_tables_ofs` / `pf_block_ofs` / `pf_emit_ofs[_bounded]`), with the run
  term. No new loop.
- The run term and the scan the rows need reach the emitter through ONE new
  derivation, `OfsTest` ("the candidate test a `<p>_ofsskip` block emits",
  §1.3), which the existing `offset-set` rows are routed through FIRST,
  byte-identically (implement-then-replace). Every reader that asks what the
  block tests (the block, the verify chain, the table params, the OFFSETS
  stamp, G1) reads it.

**R2. The emitted PROGRAM is unchanged from revision 1; only where it is
selected and what it is called moved.** For every artifact both revisions
move, the `<p>_ofsskip` text is the same loop with the same scan, the same
verifies, the same run term and the same widened guard (§2). So S1-3's
soundness evidence and `twin_counts.txt`'s counts carry over unchanged
(§3, §4 say why each does), and the twin instruments were not re-run.

**R3. New stamp VALUES are the main new consequence.** A row's stamp is its
own name ([ENG-FORM]), so `RX_DFA_PREFILTER` (and its `rx_info.prefilter`
mirror) gains `"run-pinned"` and `"run-pinned-bounded"`: 7 → 9 values. In
revision 1 these artifacts stamped the existing `"offset-set"`. Every reader
of that value set moves (§7): the spec table, `run_dfa_stamps.sh`'s
independent TEXT re-derivation (it must learn to tell the run term apart,
or it reads these artifacts as `offset-set` and fails the iff), the form
census's floors and `KNOWN_VALUES`, `run_offset_skip.sh`'s `OFS_VALUES`,
`--list-axes` (two candidate rows; every later prefilter `order` shifts by
two), and the bench's bucketing (an inbox note, §10).

**R4. Found while placing the row: the DFA_SELECT deny plumbing is 32 bits
wide, and bit 32 would silently not deny.** `DfaCand.deny` is `unsigned`,
`dfa_select` takes `unsigned flags`, `dfa_form_derive` copies
`cx->opt->flags` into an `unsigned`, and `PcrecAxisCand.deny` plus
`src/dump/axes_dump.c`'s `axis_macro_name` / `axis_cli_flag` / `bit_of` /
`deny_cols` / `PredAxis` / `emit_pred_row` are all `unsigned`. No row has
carried a deny bit above 31 before. Unwidened, `-fno-run-prefilter` would be
a flag that parses, lands in `rx_info.flags`' mask and removes nothing — an
answer-identical no-op that `make test-axes` cannot see. Widening them to
`uint64_t` is S1's first commit (§7, sabotage row (i)).

**R5. The deny is TWO bits, and that is the honest statement (§1.2).** The run
rows emit `<p>_ofsskip`, so they are members of the offset-skip family:
`deny = PCREC_NO_OFFSET_SKIP | PCREC_NO_RUN_PREFILTER`. Either flag removes
them. With only its own bit, `-fno-offset-skip` would stop being what
`lib/pcrec.h` promises ("emits what the compiler emitted before this axis
existed, to the line") on every class-B/C1 artifact. `dfa_select`'s
`deny & flags` already handles a multi-bit mask. The dump does not, so it
learns to render one (§7).

**R6. S1-4 re-derived.** The offset-0 SCAN (class B) is now the ROW's, not
the model's. Its grounding is unchanged (clause 2's walk singleton
`us.ofsk.k[0]` for the refusal; clause 3(b)'s `k0` singleton for the landing
byte, §3). But the two invariant edits change. `ofsk_emit_verify`'s "offset 0
is always a verify member" is still edited, to "offset 0 is always TESTED".
`prefix_k.c`'s role-A/role-B comment is NOT edited, because it stays true.
Instead, the scan arm in `pf_block_ofs` gains a comment naming the one
selection that reaches `k == 0`.

**R7. Census re-run under B's predicate on every artifact
(`s1/census_b.py`, `s1/census_b_summary.txt`).** The row predicate as B
writes it selects EXACTLY the panelled B ∪ C1 population, plus five corpus
artifacts, and no artifact outside that (§6). The two corrections cancel in
the corpus total, and both are explained:
- **+5, class B-bounded.** `foo\b`, `foo\B`, `foo\b\z`, `(foo\b)`, `(foo\B)`
  take today's `memchr-bounded` form. Revision 1's census read clause 3(b)'s
  "the memchr form" as the plain `memchr` row only and parked them in C0. The
  D11 bound is a view fact, orthogonal to scan identity, and every row pair
  treats it as a twin. So B takes both twins, and a `!views` conjunct on B
  alone would be a special case. The panel's C0 description had their
  shapes reversed too: the true C0 is 3 plain-`memchr` rows whose pick is not
  at offset 0, and 0 of another form.
- **−5, class A2.** Five corpus class-A artifacts verify the whole run but
  SCAN a different member than the pick (e.g. run `fr`, pick `f` at 0, scan
  `r` at 1). §1.2's G1, as panelled, requires `p == q` for a run. So their
  pre-check stays, for C2's reason (Q2). Revision 1's `classify()` counted
  them as elided.
- Totals: **bench 34/235 and corpus 513/3,576 program changes**. The numbers
  are unchanged, but the corpus membership differs by those ten artifacts.
  Every run-row artifact has `REQ_WHY "emitted"` today, so no `one-attempt`
  artifact takes the row (§6.2). No class-B artifact is on a seeded machine,
  so the `reseeds` false → true flip on class B changes no scan edge (§1.2,
  §6.2).

**R8. The engine-neutral direction (addendum 4 item 2) shapes two S1
choices without generalizing anything (§1.5).** (a) The pin fact depends only
on `(Job.nfa, Job.req_run)`, never on the DFA's `k0` or states. (b)
`OfsTest` and the `<p>_ofsskip` block emitter take no `Dfa`, so a VM
consumer hook ([OPT-VMSEED]) can call the same block later. S1 renames
nothing, adds no VM hook, and keeps every `s->forward` clause.

**R9. Sabotage grows from 5 to 10 rows (addendum 4 item 3: one per new
predicate).** Rows (a)-(e) are revision 1's, re-anchored. The new rows are:
(f) clause 3 dropped, (g) the pin's byte-equality dropped, (h) clause 4
dropped, (i) the deny not honoured (R4), and (j) `reseeds` false on the run
rows, whose reach is thin: the census found zero seeded class-B artifacts
and exactly one seeded C1 (§7.1).

---

## 0. Findings first (unchanged in substance from revision 1)

1. **Router is (i) plus (ii). Keyword is (ii) alone.** Read off the
   artifacts at `b5c1423b`:
   - `router-prefix-order` (`/user|/users`) ships `RX_DFA_PREFILTER "memchr"`
     on `/`, and a separate `RX_REQ_RUN "2f75736572@0"` pre-check that also
     scans `/`. The run IS pinned. `prefix_k.c`'s walk proves offsets 0..4 are
     exactly `/`,`u`,`s`,`e`,`r`. The k-set model declines it anyway, because
     `/` is the rarest byte and the measured "scan must move" rule
     (`offset_k_skip.md` §7.4) refuses a scan at offset 0. So the prefilter
     never learns the run.
   - `keyword-prefix-order` (`in|instanceof`) ships `RX_DFA_PREFILTER
     "offset-set"` with `OFFSETS "0,1*"`: scan `n` at offset 1, verify `i` at
     offset 0. **That prefilter already carries the run `in`.** The pre-check
     (`RX_REQ_RUN "696e@1"`, scan `n`) is the same search a second time.
     G1 cannot see this, because `dfa_cand_scan_byte` returns −1 for every
     offset-set prefilter (`emit_dfa.c:5429`). Its comment says an
     offset-set "scans a membership table". That has been false since
     `[OPT-K]` required the scan offset to be a singleton.
2. **Both S1 after-programs are known, and both answer-check.**
   - Keyword's S1 program is main's `-fno-req-byte` artifact. That artifact
     is **program-identical to `25b1984f`'s** (the diff is only the header
     line, `.abi`, `.flags` and `rx_info`'s `vars` pair).
   - Router's S1 program exists as a hand twin (`s1/mk_twin.py`). It returns
     the same spans as the shipped artifact on all 78 bench subjects. Under
     option B the twin is still the program router gets (R2). Only the
     stamps differ: `"run-pinned"` instead of `"offset-set"`.
3. **Counted on the bench's own subjects (`s1/twin_counts.txt`),
   throughput set:**

   | arm | router `memchr` calls | router DFA steps | keyword `memchr` calls |
   |---|---|---|---|
   | (a) as shipped | 77,822 | 78,696 | 88,264 |
   | (c) = `25b1984f`'s program | 39,098 | 79,438 | 44,135 |
   | **(b) S1** | **39,098** | **1,872** | **44,135** |

4. **Predicted after-values (§4):** router thr ≈337k ns (range 330-394k),
   keyword thr ≈731k ns. Both land inside or below `25b1984f`'s band. The
   forced-VM cells are no-move controls, owed to `[OPT-VMSEED]`.
5. **The same double pass exists well beyond the two witnesses.** Census
   (§6, re-run under option B's own predicate): **34 of 235 bench artifacts
   and 513 of 3,576 corpus artifacts** change program under S1 at
   `b5c1423b`. §6.3 gives the same count at `4976f385`.
6. **k64fix interacts, favourably, by construction (§8.1).** Unchanged by B:
   G1 is admission, and its placement did not move.

---

## 1. The mechanism

S1 adds **one published analysis fact, one row pair in `dfa_pfs[]`, one
derivation the offset-skip emitters read, one admission conjunct, and one
extracted primitive**. It adds no new emitted loop.

### 1.1 The fact: `prefix_k.c` publishes "the necessary run is pinned at `o`"

**Where it lives.** Two fields on `PrefixKSets` (`src/core/internal.h`),
which `unanch_start` already carries as `UnanchStart.ofsk`:

```c
    /* [OPT-LITSCAN] S1 — THE NECESSARY RUN'S PIN, an analysis fact and not a
     * selection: true iff `Job.req_run` (len >= 2) sits at offset `run_o` of
     * EVERY match — k[run_o + i] is the singleton req_run.bytes[i] for every
     * i. Read by dfa_pfs[]'s run rows and by G1; decided by neither here. */
    bool     run_pinned;
    int      run_o;          /* meaningful only when run_pinned */
```

`run_pinned` is a `bool` and not "`run_o == -1`" on purpose.
`pcrec_prefix_ksets` begins with `memset(o, 0, …)` and has three early
returns before and inside the walk. A zero-initialized `run_o` means "pinned
at 0", so a sentinel spelled `-1` would be one forgotten assignment away from
a pin nobody proved. A `bool` whose zero is "not pinned" is safe by
construction on every early-return path.

**Who computes it.** `pcrec_prefix_ksets` does, immediately after the walk
loop and BEFORE `if (k0count == 0 || k0count >= 256) return;`. It is a scan
of the walk's own published `k[0..nwalk-1]` for the SMALLEST `o` with
`o + L ≤ nwalk` and `k[o+i].count == 1 && k[o+i].byte == req_run.bytes[i]`
for every `i < L`. That is no second analysis. It reads two facts the tree
already owns, the walk's singletons and `Job.req_run`, and states their
coincidence. The census probe's `pin` is this exact rule (`probe_patch.py`).

**Its invariants** (each is a comment obligation at the site, and the panel's
to attack):
1. **Order.** `Job.req_run` is final before any `unanch_start` call.
   `compile.c:1514` runs `pcrec_req_byte` before the DFA build (`:1654`),
   before scanedge's early `pcrec_dfa_scan_state_written` call (`:1678`), and
   before emission. So the pass-time and emit-time answers read the same
   run: `dfa_form_derive`'s precondition-(8) agreement check keeps holding.
2. **Denial is analysis-level.** Under `-fno-req-run` or `-fno-req-byte`,
   `req_run.len == 0`, so `run_pinned` is false and the run rows cannot
   apply. That is the compile.c rule "a denied build must be
   indistinguishable from a pattern with nothing to find". The row's own
   deny (§1.2) is a separate, row-level switch.
3. **Engine-neutral by construction (§1.5).** The fact depends on
   `(Job.nfa, Job.req_run)` alone. It is computed before, and never reads,
   the `k0` baseline, the cost model, or any DFA state. It is true of the
   language `Job.nfa` accepts. On a count-collapsed hybrid prefilter that is
   the SUPERSET language, and a pin true of every superset match is true of
   every exact match (§3.2).
4. **Smallest `o`.** Several offsets can satisfy the pin when the walk
   repeats the run's bytes. Any of them is a true statement. The smallest is
   deterministic, and it is what both censuses measured. Clause 3 (§1.2) may
   then fail where a larger `o` would pass, which is a lost opportunity and
   never a wrong answer. No census row shows the case.
5. **Only on the forward unanchored scan's walk.** `pcrec_prefix_ksets` is
   called only where `unanch_start` computed `kind != DFA_PF_NONE`. The
   anchored MATCH-HERE machine and ENG_ATTEMPT never compute it, so they
   never publish a pin.

### 1.2 The decision: a row pair at the head of `dfa_pfs[]`

```c
static const DfaPf dfa_pfs[] = {
    { { "run-pinned-bounded",  PCREC_NO_OFFSET_SKIP | PCREC_NO_RUN_PREFILTER, pf_run_bounded_applies },
      pf_tables_ofs,  pf_block_ofs, pf_emit_ofs_bounded,    true  },
    { { "run-pinned",          PCREC_NO_OFFSET_SKIP | PCREC_NO_RUN_PREFILTER, pf_run_applies         },
      pf_tables_ofs,  pf_block_ofs, pf_emit_ofs,            true  },
    { { "offset-set-bounded",  PCREC_NO_OFFSET_SKIP, pf_ofs_bounded_applies },   /* unchanged from here down */
    ...
```

**`PCREC_NO_RUN_PREFILTER`** is new, bit 32, `-fno-run-prefilter`. It is a
`#define` (`PCREC_BIT(32)`, `lib/pcrec.h`'s "every bit above 30" rule), with
its own `axes.def` row, `PCREC_AXIS_DEFAULT_ON`, deny-only.

**The predicate, `pf_run_applies_common(s)`** (the bounded twin adds
`&& u->views`, exactly as `pf_ofs_bounded_applies` does):
0. `s->forward && u->kind != DFA_PF_NONE`. This is the offset-set rows'
   common clause, for its reason: the skip rides the offset-0 verdict
   `unanch_start` proved (`!start_acc`, `cand.usable`).
1. `Job.req_run.len ≥ 2`.
2. `u->ofsk.run_pinned`. Write `o = u->ofsk.run_o` and `L = req_run.len`.
3. **Identity: the scan is the same byte at the same offset it is today.**
   Call the pick's offset `s = o + req_run.idx`. Either
   (a) `u->ofsk.nsel > 0` and the model's scan offset
   `u->ofsk.k[u->ofsk.sel[u->ofsk.scan]].k == s`, or
   (b) `u->ofsk.nsel == 0`, `s == 0`, `u->kind == DFA_PF_MEMCHR`, and
   `u->cand.byte == req_run.bytes[req_run.idx]`.
4. **The row adds something:** NOT `ofs_verifies_run(model selection)`, i.e.
   the model's own selection does not already test every offset `o+i` as the
   singleton `run[i]`. Where it does (class A, keyword), today's
   `offset-set` row already carries the run, G1 elides the pre-check, and
   the artifact keeps its program.

Clause 3(b) reads `u->kind`, not the name of a row below it, for two
reasons. A row must not ask what a later row would select: that is
circular in a first-match walk, and a deny mask between them would make
the answer depend on flags the predicate never sees. `u->kind` is also the
fact the `memchr` and `memchr-bounded` twins both come from. It admits BOTH
twins, which is R7's +5.

Clause 4 does not read which row is selected either. It reads the model's
selection (`u->ofsk.sel`), which is analysis output. On default flags,
`nsel > 0` exactly where an `offset-set` row is selected (the census's
`implm` and `implies` columns agree on every artifact).

**Order: ahead of every existing row, bounded before unbounded.** The claim
to prove is that no currently-selected artifact outside S1's population
changes its row.
- `dfa_select` is a first-match walk over an ordered list, and a deny-masked
  or non-applying entry is transparent. So PREPENDING rows can change an
  artifact's selection only where one of them applies. Everywhere the
  predicate is false (every class except B and C1, the reverse and
  anchored machines through clause 0, ENG_ATTEMPT which never reaches
  `dfa_pfs[]`, and the empty engine through `kind == NONE`), the walk
  continues into today's list in today's order and returns today's row.
- Where the predicate is true:
  - **B** (and B-bounded) has `nsel == 0`, so no `offset-set` row applies,
    and today it takes `memchr` or `memchr-bounded`. It must meet a run row
    before those, and it now takes `run-pinned` or `run-pinned-bounded` by
    the same `views` bit.
  - **C1** has `nsel > 0`, so `offset-set[-bounded]` ALSO applies. The run
    row must sit ahead of both, and C1 now takes `run-pinned[-bounded]` by
    the same `views` bit.
  - The head is therefore the ONLY position that serves both classes: below
    the `offset-set` pair, C1 never reaches the row, and nothing else
    constrains the order.
  - Bounded before unbounded mirrors every existing pair: the unbounded
    predicate does not test `!views`, so its twin must precede it.
- **Class A** (keyword) fails clause 4 and keeps `offset-set`. **Class E**
  fails clause 1 (`L < 2`). **C2** fails clause 3(a). **C0** fails 3(b).
  **D** fails clause 2. **V** has no DFA scan. None of them changes its row.
- Measured, not only argued: `s1/census_b.py` evaluates this predicate on
  every artifact of both populations and cross-tabulates it against the
  panelled classes (§6.2). It is true on B ∪ B-bounded ∪ C1 and on nothing
  else.

**`reseeds` = `true`, and it is not a choice.** The field states whether the
row's emitter writes the state variable. The run rows' emitters ARE
`pf_emit_ofs[_bounded]`, which call `pf_emit_ofs_reseed` on every seeded
machine, because the skip lands past bytes that may leave the start state
(the reason that pair's field is already `true`). Declaring `false`
would make `pcrec_dfa_scan_state_written` wrong, and scanedge's precondition
(8) would let a chain head be a seed target on a machine this form reseeds
mid-body. `dfa_form_derive`'s agreement check could NOT catch that, because
both of its readings would read the same wrong field (sabotage (j)).
- Consequence: a seeded class-B machine flips `memchr` (`false`) →
  `run-pinned` (`true`), and its forward scan edges can then be refused. The
  census found **0** seeded class-B artifacts in either population (every
  class-B machine has a singleton escape set `k0`, and a leading word
  context makes the start state escape on every word byte). C1 was already
  `true` (its one seeded member, bench `wild-secrets-github-pat`, is
  unchanged). So this moves no artifact today, and row (j)'s reach is thin
  (§7.1).

**`deny = PCREC_NO_OFFSET_SKIP | PCREC_NO_RUN_PREFILTER`: either flag removes
the pair.**
- `-fno-run-prefilter` alone: B falls to `memchr[-bounded]` and C1 to
  `offset-set[-bounded]`, today's rows, and G1 then reads today's selection
  and keeps the pre-check (§1.4). So for B/C1 the denied build is TODAY'S
  artifact, a D82 control rather than a third variant. The A/E elisions are
  admission and have no axis (§2.29 of `tuning.md`), so they do not come
  back.
- `-fno-offset-skip` alone: the whole `<p>_ofsskip` family goes, run rows
  included, and the artifact is the pre-`[OPT-K]` one, which is
  `lib/pcrec.h`'s stated promise for that flag. Revision 1 had the same
  behaviour, because its run pin rode the `offset-set` rows.
- The alternatives are rejected. A single-bit deny breaks
  `-fno-offset-skip`'s promise on every B/C1 artifact. Reading
  `PCREC_NO_OFFSET_SKIP` inside `applies` puts a flag in a predicate, the
  shape D82 retired ("the deny flag = a filter on the candidate list").
  Normalizing one flag into the other at option parse makes a second rule
  about the flags. The two-bit mask needs no new mechanism in `dfa_select`,
  only the dump learning to render it.
- Masked out of `rx_info.flags` via `strategy_denials`, for
  `PCREC_NO_OFFSET_SKIP`'s reason (it changes no answer).

### 1.3 The emitter's one new derivation: `OfsTest`, the candidate test

Today `pf_block_ofs`, `ofsk_emit_verify`, `ofsk_emit_params`,
`pf_tables_ofs`, `pf_comment_ofs` and `dfa_prefilter_offsets` each read
`PrefixKSets.{nsel, sel, scan, maxk}` directly. The run rows need a
different scan (class B's offset 0) and a different term list (the run as
ONE term, in-run singleton verifies dropped). Spelling that as
`if (run row)` in six places would be six statements of one fact. So S1
introduces ONE derivation with those six readers, plus G1's:

```c
/* THE CANDIDATE TEST a `<p>_ofsskip` block emits: one scan (offset, byte) and
 * the terms verified at each candidate, ascending by offset -- each either
 * one walk offset (a byte compare or a table probe) or the pinned run (one
 * constant-length compare, P4). ONE derivation, seven readers. */
typedef struct {
    int scan_k, scan_byte;
    int nterm;
    struct { const PrefixK *k; } term[PCREC_OFSK_MAX_SET]; /* k == NULL: the run */
    int run_o, run_len;              /* run_len == 0: no run term */
    const unsigned char *run_bytes;  /* Job.req_run.bytes, never a copy */
    int maxk;                        /* the loop guard: the largest tested offset */
    int noffsets;                    /* distinct offsets tested */
} OfsTest;

static bool ofs_test_of(Ctx *cx, const UnanchStart *us, const DfaPf *pf, OfsTest *t);
```

`ofs_test_of` returns false for a row whose `emit_block` is NULL (no
`<p>_ofsskip`). The run rows are identified by a new `bool run_term` field
on `DfaPf`, declared in the same struct literal as the row's emitter, on
`reseeds`' own argument ("a property of a form … a seventh form cannot be
added without answering it"). It never compares names.
- **`offset-set` rows:** scan = `k[sel[scan]]`. Terms are the other `sel`
  members, ascending. `maxk = ofsk.maxk`. `noffsets = nsel`. No run term.
  This is today's selection re-expressed, and S1's second commit makes that
  re-expression alone and must move zero artifacts (§7).
- **Run rows:** let `s = o + idx`. The scan is `(s, run[idx])`. The terms
  are every model-selected offset OUTSIDE `[o, o+L)` other than the scan,
  plus the run term positioned at `o`, all ascending. `maxk` is
  `max(ofsk.maxk, o + L − 1)` (S1-1, now a field of the one derivation, so
  the `while` guard and the `cand + maxk >= n` early exit cannot disagree).
  `noffsets` = (terms outside the run) + L. Checked, as `pcrec_ctx_fail`s,
  never assumed:
  - on `nsel > 0`, the model's scan offset equals `s` (clause 3(a) read
    back from the emitter's side);
  - on `nsel == 0`, `s == 0` and `k[0].count == 1` and
    `k[0].byte == cand.byte == run[idx]` (clauses 2 and 3(b) together).
  - The first check can fail only if the predicate and the derivation have
    drifted, which is the loud-error class this file prefers
    (`DfaForm.cx`'s own comment).
- **Offset 0 is always TESTED.** In C1 it is a term (the model always
  selects it) or, when `o == 0`, the run term's first byte. In B it is the
  scan. So the landing invariant `[OPT-K]`'s "OFFSET 0 IS ALWAYS IN THE SET"
  rests on is kept, in B through clause 3(b) (§3.1).
- **The term array cannot overflow.** A run row's terms are the model's
  non-scan members outside the run (at most `nsel − 1 ≤ 3`) plus the one
  run term, so at most `nsel ≤ PCREC_OFSK_MAX_SET` (B: exactly one).

`DfaForm` gains `OfsTest ofs` (filled in `dfa_form_derive` from `f->pf`,
beside `f->ofsk`). The block emitter's inputs narrow to `(cx, p, const
OfsTest *)`, and that narrowing is what §1.5 needs.

### 1.4 G1 widened inside `req_admit`: one conjunct, reading the SELECTED row

`req_admit` (`emit_dfa.c:5514`) keeps its order: NONE, then G2, then G1. G1
becomes:

```
let  sel = dfa_pf_of(cx, &us)            -- axis B's SELECTION, after the deny mask
     t   = ofs_test_of(cx, &us, sel)     -- the candidate test it emits, if it has one
     p   = t ? t.scan_byte : (sel is a memchr form ? us.cand.byte : -1)
dominated  ⇔  p ≥ 0
              ∧ ( p == q                                              -- identity, any encoding
                  ∨ (L < 2 ∧ sel is a memchr form ∧ byte enc ∧ ppm(p) ≤ ppm(q)) )  -- today's clause, today's scope
              ∧ ( L < 2 ∨ (t ∧ verifies(t, o, L)) )
```

- `q = Job.req_byte`, which for a run is `req_run.bytes[idx]`, the run's own
  scan member (`internal.h`'s `Job.req_byte` comment).
- **`verifies(t, o, L)` (S1-5, re-derived onto `OfsTest`):** true iff
  `us.ofsk.run_pinned` holds and every offset `o+i`, `i < L`, is tested by
  `t` with exactly the byte `req_run.bytes[i]`. It is tested either inside
  `t`'s run term (whose `(run_o, run_len)` is `(o, L)` on a run row by
  construction), as a `count == 1` term with that byte, or as the scan
  offset with that `scan_byte`. It reads the SELECTED row's test.
  - On a run row this is true by construction.
  - On an `offset-set` row it is revision 1's `implies` (class A).
  - On every other row `t` is absent and a run is never dominated.
- **The post-deny rule (S1-5) falls out of reading the selection.** Under
  `-fno-run-prefilter`, B's selection is `memchr` (no `t`) and C1's is
  `offset-set` with a `t` that does not verify the run. Under
  `-fno-offset-skip`, both are memchr or byte-class. In every case G1 keeps
  the pre-check. The denied build's `REQ_WHY` reads `"emitted"`, today's
  value.
- **`dfa_cand_scan_byte` becomes this `p`** (widened from memchr-only). Its
  "offset-set scans a membership table" comment is deleted as stale.
- **The density clause stays memchr-form-only, EXPLICITLY** (S1-5): a
  conjunct of its own, not an inference from `p`'s shape. Now that `p` is
  non-negative on every `<p>_ofsskip` row, the guard is what keeps it out.
- **The identity conjunct is NOT dropped where `verifies` holds.** Where the
  prefilter verifies the run but scans a different member (A2, five corpus
  artifacts, R7), eliding the pre-check trades a whole-window pass on the
  pick for the prefilter's pass on another run member. That is a density
  judgement between two members, exactly Q2's C2 question, ruled out of S1.
  Soundness would allow it (§3.3). Cost is unmeasured.
- No axis bit (§2.29 of `tuning.md`). `REQ_WHY`'s four-token set is
  unchanged. `"dominated"` now reaches `offset-set` and `run-pinned` artifacts.

### 1.5 The engine-neutral direction (addendum 4 item 2), and what S1 does not do

**The standing reading.** `dfa_pfs[]` IS the engine-neutral CANDIDATE-FINDING
table (`compare_stack.md` L3). Every row answers one question, "the next
position ≥ p where a match could start", and only the CONSUMER differs.
- The DFA re-enters its machine at the answer (the `reseeds` hat: whether
  that re-entry writes the state variable).
- The VM hybrid consumes the DFA's WINDOW, not the row. Its inlined
  `static <p>_prefilter` IS `pcrec_emit_dfa_engine`'s output
  (`emit_vm.c:12109`), so the row lands there by construction, and the VM's
  contract (an answer-identical window) is unchanged (§3.2).
- A no-DFA VM would begin an attempt at the answer. That is `[OPT-VMSEED]`.

**What S1 does NOT change:**
- no rename of `dfa_pfs[]`, `DfaPf`, `DfaSel` or `pf_*`;
- no VM consumer hook, no VM-side row and no VM predicate;
- every row keeps its `s->forward` clause and its DFA-specific emit hook;
- `reseeds` stays a field of the row (it will be a property of the DFA
  consumer's hook once there are two consumers);
- `pcrec_prefix_ksets` keeps its one caller (`unanch_start`).

All of that is `[OPT-VMSEED]`'s, under the addendum-4 process bar, with
implement-then-replace.

**What S1 must not preclude, and how it avoids each:**
1. *The pin must be available where no DFA exists.* The fact depends on
   `(Job.nfa, Job.req_run)` alone and is computed before the `k0`-dependent
   early return (§1.1 invariant 3). VMSEED needs a caller that builds or
   walks the NFA on the VM route, but no change to the fact.
2. *The candidate test must be emittable without a DFA.* `OfsTest` holds no
   `Dfa *` and no `DfaForm *`. The `<p>_ofsskip` block emitter reads
   `(cx, p, const OfsTest *)` and nothing else. The DFA-specific half (the
   call site, the landing, the reseed) stays in `pf_emit_ofs[_bounded]`. A
   VM hook is a second caller of the same block, not a second block (D122's
   "never a VM-local search table").
3. *The deny must name a mechanism, not an engine.* `-fno-run-prefilter`
   says "a run-verified candidate search". When VMSEED serves both
   consumers from the same row, the same bit denies both, and test-axes
   gets both engines' identity for free.
4. *Clause 3 is DFA-shaped, and that is right for S1.* It compares against
   the scan the DFA prefilter runs today (`k0`, the model's scan). A
   no-DFA consumer has no "today's scan", so VMSEED's predicate is its own
   clause on the same row (engine appears "only in a row's predicate and its
   emit hook", addendum 4). Nothing in the pin or in `OfsTest` assumes
   clause 3.

### 1.6 The extracted primitive: P4, the exact compare (unchanged)

`emit_req_run_check`'s `!memcmp(<base>, "<run>", L)` (`emit_dfa.c:723`)
becomes the kit's first primitive, one emitter function (`compare_stack.md`
P4, exact arm). It has two callers:
- **REQ_RUN**, re-emitted BYTE-IDENTICALLY through it (implement-then-replace;
  the identity gate moving zero artifacts on the extraction commit alone is
  its acceptance);
- **the `<p>_ofsskip` run term**, which passes the same `(base, bytes, L)`
  shape. The run term includes the scan byte, as REQ_RUN's compare does, so
  gcc sees the same constant-length `memcmp`.

Pay-for-what-you-use holds: no K/T mask (S1 is exact-only), no SWAR, and no
form choice beyond `memcmp`.

**P5, the search loop.** The run rows use `<p>_ofsskip`, so no second search
is introduced. The floating-run pre-check's loop is converted in S1's LAST
commit, per Frank's Q1 ruling (§7.2).

---

## 2. The emitted shape (router)

Before: the pre-check at the top of `rx_search`, then this prefilter:

```c
if (forward_state == 0 && last_accept_position == (size_t)-1) {
    if (scan_position >= subject_length) return 0;
    const void *q = memchr(subject + scan_position, 47, subject_length - scan_position);
    if (!q) return 0;
    scan_position = (size_t)((const unsigned char *)q - subject);
}
```

After: no pre-check (`RX_REQ_WHY "dominated"`), and `pf_emit_ofs`'s call into:

```c
static inline size_t rx_ofsskip(const unsigned char *subject, size_t n, size_t pos)
{
    while (pos + 4 < n) {
        size_t cand;
        const void *q = memchr(subject + pos, 47, n - pos);
        if (!q) return n;
        cand = (size_t)((const unsigned char *)q - subject);
        if (cand + 4 >= n) return n;
        if (!memcmp(subject + cand, "/user", 5)) return cand;   /* P4 */
        pos = cand + 1;
    }
    return n;
}
```

This is revision 1's text exactly (R2). The stamps are
`RX_DFA_PREFILTER "run-pinned"` (it was `"offset-set"` in revision 1),
`rx_info.prefilter = "run-pinned"`, and `RX_DFA_PREFILTER_OFFSETS
"0*,1,2,3,4"`. OFFSETS names the offsets TESTED, and the run's are listed
individually. `0*` is a new value in that domain: before S1 no selection
scanned offset 0.

Keyword's program is unchanged. Its stamps are `"offset-set"`, `"0,1*"` and
`RX_REQ_WHY "dominated"`.

The block's emitted comment lists each tested offset on its own line through
`legend_byte` as today, marks the run's offsets "(the run, one compare)", and
adds `-fno-run-prefilter` beside `-fno-offset-skip`. It never prints the run
as a string. If a later revision does print it, that string goes through
`emit_comment_safe_byte` (S1-7: class-B member `*/x`). The `offset-set`
rows' comment text is unchanged, byte for byte.

---

## 3. Answer identity

A prefilter may only skip positions that cannot start a match. A pre-check
may only answer NOMATCH where no match exists. S1 touches one of each.

### 3.1 The run rows refuse exactly the positions that cannot start a match

Every refusal is one test in `OfsTest` failing:
- the scan byte at `cand + s`;
- a model term at `cand + k`, unchanged from `[OPT-K]`;
- one byte of the run at `cand + o .. cand + o + L − 1`.

Each is a set of `prefix_k.c`'s walk at its offset: a singleton for the scan
and the run bytes (clause 2), and the model's own set for a term. The walk's
soundness argument (its header, "WHY IT IS SOUND") is universally quantified
over the candidate start and the preceding byte. The walk passes assertions
as though they held, which can only widen a set. So a failed byte is a proof
that no match begins at `cand`. Three facts complete the argument, all
inherited unchanged from `[OPT-K]`:
- the landing state (reseeded where the machine seeds, `pf_emit_ofs_reseed`;
  `reseeds = true`, §1.2);
- the D11 bounded twin (a miss clamps to n−1, with no early return);
- the `pos + t.maxk < n` guard, `t.maxk = max(ofsk.maxk, o + L − 1)` (S1-1).
  It also closes K27's `memchr(NULL, c, 0)`: `n > 0` is implied.

**The offset-0 scan (class B, and B-bounded), grounded per S1-4.** There are
two facts, with two sources, and each is checked by the predicate:
- **Refusal (role B).** A position whose byte is not `run[0]` cannot begin a
  match. The source is clause 2's walk singleton `us.ofsk.k[0] == {run[0]}`,
  never `k0`, which answers a different question (MISCOMPILE-1's
  confusion).
- **Landing (role A).** The byte a returned candidate carries leaves `fs`,
  so the skip never re-runs on a parked position. The source is clause
  3(b)'s `k0 == {cand.byte} == {run[idx]} == {run[0]}`: it is today's
  memchr byte, and `k0` is the escape set.

Together they are why B needs 3(b)'s `u->kind == DFA_PF_MEMCHR` (`k0` a
singleton), not merely `s == 0`. The `pf_block_ofs` scan arm's comment names
this as the only selection reaching `k == 0`.

**B-bounded under a word context (`foo\b` family, R7), for the panel to
attack specifically.** It is a new population. Revision 1's soundness
witnesses (S1-3) had no bounded class-B member. The argument is
`offset-set-bounded`'s, with a larger `maxk`:
- `views` is set by the trailing `\b`'s accept-by-class, not by a leading
  context, and the census reads these machines as unseeded.
- The skip only lands on candidate starts; the parked start state cannot
  accept (`!start_acc`).
- The n−1 clamp leaves the last two positions to the stepped loop.
- Positions in `[n − maxk, n − 1)` are refused because a match starting
  there would need a byte at `≥ n`.

The build owes these five corpus artifacts' answer-identity at every
startpos (§3.4).

### 3.2 The hybrid consumer, and count-collapse

The VM hybrid inlines the DFA search as `static <p>_prefilter` and runs the
VM only inside the window it returns (`emit_vm.c:12090-12109`). The run row
sits inside that DFA's forward scan. So the window is answer-identical by
§3.1, and the VM's contract is untouched: the VM never sees a row.

On a COUNT-COLLAPSED prefilter, `Job.nfa` is rebuilt as the collapsed
superset language (`compile.c:1647`), and both the walk and the pin describe
THAT language.
- A pin true of every superset match is true of every exact match, so the
  run term refuses no exact start.
- Where the collapse makes the run float (`a{3}/user` → `a+/user`), the pin
  fails. The row declines, which is the conservative direction, and the
  pre-check stays.

This covers the §8.1 K64 interaction too: an elided pre-check's NOMATCH is
reached with zero VM attempts.

### 3.3 The elision is a check not run

It can only remove a NOMATCH the engine below returns anyway (§2.29 of
`tuning.md`). The stronger property G1 adds is that the elided NOMATCH is
still reached WITHOUT an attempt:
- Suppose the window lacks the run. Any candidate `c ≥ pos` with
  `c + t.maxk < n` that passed would put the run at `c + o`, inside
  `[pos, n)`. So no candidate passes the run test: `verifies` says every
  run byte is tested at its pinned offset.
- The first skip therefore returns `n`, and the entry returns 0 (or clamps
  to n−1 under a view). S1-6's seeded-machine caveat (H4) is unchanged.

That argument needs `verifies` and NOT `p == q`, which is why A2's retained
pre-check is a cost ruling and not a soundness one (§1.4).

### 3.4 Verification the implementation owes (addendum 4 item 3's bar)

- **Answer-identity:** the corpus × every startpos × all three engines,
  S1 pin against its base, and against each deny flag
  (`-fno-run-prefilter`, `-fno-offset-skip`, `-fno-req-run`,
  `-fno-req-byte`).
- **Identity gates:** zero moves on the plumbing, P4 and `OfsTest`
  commits, and on the pin commit. The mechanism commit's program-region
  movers must equal §6's census, by id.
- **`make test-axes AXES="-fno-run-prefilter -fno-offset-skip -fno-req-run -fno-req-byte"`.**
- **A corpus `.rxt` witness file**, oracle-verified by python3 `re`,
  covering:
  - a run at subject start and at subject end;
  - `cand + maxk == n − 1`;
  - a failed run at every scan hit;
  - a run straddling `startpos`;
  - the empty and NULL subject;
  - a `$`-bearing bounded form, plus the `foo\b`/`foo\B` B-bounded twins;
  - the C1 shapes `[ab]/user` and `a\K/user` on a subject ending `a/us`;
  - `(?i)/1234` (B) and `(?i)x/1234` (C1) (S1-3).
- **`make ubsan` / `make asan`** on both axes over every moved artifact
  (the offset-0 `memchr`, and the widened guard).
- **One sabotage row per new predicate** (§7.1).

---

## 4. Cost model and predicted after-values (unchanged; the program did not move)

Option B changes only which table selects the program and what it is
called, so revision 1's model, constants and predictions stand:
- **Method.** `c_call` = 7.72 ns per `memchr` call; 0.016794 ns per scanned
  byte; a per-step constant ≤ 0.87 ns solved from router's arm (c).
- **Cross-check.** The model reproduces arm (a) − (c) = 326.2k ns measured,
  leaving ≈0.1 ns per inlined `memcmp`.

| config | now | predicted (b) | vs now | vs `25b1984f` |
|---|---|---|---|---|
| router thr auto-caps | 719,995.6 | **337k** (330k if the whole residual is step cost; **393.8k floor case** if the saved steps were free) | −53% | −14% (floor 0%) |
| router thr auto-nocaps | 720,273.3 | **337k** (same range) | −53% | −14% |
| keyword thr auto-caps | 1,238,485.2 | **731,121** (`25b1984f`'s measured value: the SAME program) | −41% | 0 |
| keyword thr auto-nocaps | 1,239,078.3 | **731,390** | −41% | 0 |
| router srch auto ×2 | 711.9 / 712.7 | ≤ now: 94 → 77 calls over 76 calls | ≤ 0 | — |
| keyword srch auto ×2 | 733.6 / 732.5 | 733-774, **inside the srch band (−3.8..+11.9%)** | ≤ +5.6% | 0 |
| router/keyword thr+srch **vm-caps, vm-in-caps** (8 cells) | 4.44-4.64M thr | **unchanged**: no DFA scan, `REQ_WHY "emitted"`, program-identical save the abi line | 0 | +9.2..10.7% (owned by `[OPT-VMSEED]`) |

**The one real uncertainty is router's (i) share, 0 to −14%**, the `bignum`
question (`offset_k_skip.md` §7.4). (ii) is the hard bar. (i) is the
measured question, and arm (b) − (c) answers it directly (§10).

`twin_counts.txt` was NOT re-run. The counted programs are the same text
under option B (R2), and a count off an unchanged program is the same count.

---

## 5. Acceptance cells, and the carve-outs named from the mechanism

**Targets** (D119 rule 4: median gain > IQR, then the band):
- router thr, auto-caps and auto-nocaps: at or below `25b1984f`'s 393.8k plus
  the band (+6.75%). This is (ii)'s bar.
- keyword thr, auto ×2: the same bar, predicted at 731k.
- **(i)'s question**, router (b) against (c): reported as a number, not a bar.

**No-move controls** (program-identical save the abi line; the stamps
confirm it before the window):
- router/keyword vm-caps and vm-in-caps, thr and srch;
- `nested-comment-rec` ×4 (class V);
- `wild-secrets-github-pat` vm ×2 (V).

Frank's Q1 ruling makes the V controls change program in S1's LAST commit
only. They are no-move controls on the S1 mechanism pin and
"changed program, predicted equal" on the conversion pin (§7.2).

**Carve-outs, derived from what the mechanism does** (unchanged by B):

| hazard, from the mechanism | who has it (bench, both auto configs) | today thr / srch (auto-caps) | predicted |
|---|---|---|---|
| **H1. The pre-check WAS the whole answer** (the run is absent), and the prefilter must now dismiss at the same cost | `wild-secrets-slack-webhook-url` (C1, **a 0.77× WIN**); `wild-secrets-github-pat` (C1); `file-ext-order` (B); `wild-semdiv-altorder-foo-foobar-rustregex` (B); `wild-semdiv-dollar-trailing-newline-pcre2` (C1). Run occurrences in the throughput set: **0 for all five**; scan hits 39,095 / 7,861 / 19,436 / 24,889 / 6,569 | 347.7k / 1,201; 129.3k / 1,091; 260.6k / 683; 358.3k / 647; 26.1 / 629 | = now ± band |
| **H2. A run-dense subject** | none in the bench | — | corpus-only; bound hits × 0.1 ns |
| **H3. A one-byte pre-check dropped from an offset-set artifact** (class E) | `wild-validator-uuid-grok` | 82.4k / 776 | ≤ now |
| **H4. A seeded start state skips past the prefilter's first call** (S1-6) | none in the bench | — | performance-only |

**Not a carve-out:** the WAF cells (`942270`, `942160`, `942140`, `942360`
have no run or no prefilter; `942500` is class D). S1 absorbs nothing of
S3/S4.

---

## 6. Census: which artifacts change

### 6.1 Instruments

- `s1/census.py` + `s1/probe_patch.py`: revision 1's classes, unchanged,
  with their committed output `census.tsv` / `census_summary.txt` at
  `b5c1423b`.
- **`s1/probe_b_patch.py` + `s1/census_b.py` (this revision):** the same
  probe line and keys, plus `kind`, `cbyte`, `views`, `seeded`, `se` (today's
  reseeds answer), `implm` (the MODEL's selection verifies the run) and
  `rowb` (§1.2's predicate, clauses 0-4, evaluated on EVERY artifact
  regardless of `REQ_WHY`). `census_b.py` re-uses `census.py`'s `probe` and
  `classify`, splits C → C1/C2/C0 by `class_c_split.py`'s rule, and splits
  A → A/A2 by G1's identity conjunct. It then cross-tabulates `rowb`
  against the classes and computes the program-change total itself, with
  no hand arithmetic (the S1 review C2 lesson). Output: `census_b.tsv` and
  `census_b_summary.txt`.
- Populations are the reqpos census's. The bench is 235 compilable patterns
  × {`--features all`, `--no-captures`}. The corpus is 3,576 compilable
  `.rxt` rows with row options not applied (a prediction, not the gate).

### 6.2 At `b5c1423b` (the panelled base, same populations)

| class | what S1 does | selected row after S1 | bench (per auto config) | corpus |
|---|---|---|---|---|
| A: the model's selection verifies the pinned run AND scans the pick (keyword) | elide | `offset-set[-bounded]`, unchanged | 3 | **74** |
| B: pinned, no k-set, `memchr` scans `run[0]` at offset 0 (router) | run row + elide | `run-pinned` | 12 | 66 |
| **B-bounded**: the same under a view (`foo\b`, `foo\B`, `foo\b\z`, `(foo\b)`, `(foo\B)`) | run row + elide | `run-pinned-bounded` | 0 | **5** |
| C1: pinned, the k-set scans the pick's offset | run row + elide | `run-pinned` 13 / 102; `run-pinned-bounded` 2 / 13 | 15 | 115 |
| E: one-byte pre-check; offset-set scanning the same byte | elide | unchanged | 4 | 253 |
| **program changes** | | | **34** | **513** (14.3%) |
| **A2**: verifies the run, scans a different member | unchanged (G1 identity; Q2's reason) | — | 0 | **5** |
| C0: pinned, no k-set, pick not at offset 0 | unchanged | — | 0 | **3** |
| C2: the k-set scans a different run member | unchanged (Q2) | — | 12 | 40 |
| D: floating run | unchanged | — | 14 | 32 |
| V: no DFA scan | unchanged | — | 13 | 71 |

**Cross-tab (`census_b_summary.txt`).** `rowb = 1` on exactly B (66 corpus
/ 12 bench per config), B-bounded (5 / 0) and C1 (115 / 15), 186 corpus and
27 bench per config in all. It is `0` on every other class in both
populations. So no artifact outside the population takes the row. Also:
- every `rowb` artifact reads `REQ_WHY "emitted"` today (186/186, 27/27),
  so no G2 `one-attempt` artifact takes the row, and the "the prefilter
  already scans the same byte and the pre-check scans it again" framing
  holds for the whole population;
- `seeded = 1` on 0 class-B `rowb` artifacts and on 1 C1 (bench
  `wild-secrets-github-pat`, already `reseeds`), so the class-B `reseeds`
  flip moves nothing;
- `implm == implies` on every artifact (the default-flags equivalence §1.2
  relies on).

**Against revision 1 (explained, R7).** A 79 → 74 (5 → A2). C0 8 → 3 (5 →
B-bounded, the row pair's own twin rule). The totals of 34 and 513 are
unchanged, but the corpus membership differs by those ten. Revision 1's
C0 description had the forms reversed: the rows that now move are
`memchr-bounded`, and the rows that stay are plain `memchr` with the pick
off offset 0.

**Existing test witnesses do not move.** Measured with the probe at
`4976f385`:
- `needleXYZW` (M2.12's pinned prefilter check) is C2: pick `Z` at 8,
  scan `X` at 6.
- `\Bfoo\B` and `\bfoo\B` (`run_scan_edge_census.sh` §3's precondition-(8)
  witnesses) and `\bat [a-z]` (`run_offset_skip.sh`'s `stack-frame`) are
  C2: pick at 0, scan at 1.
- `\d{4}-\d{2}-\d{2}` and the `uuid` prefix have no run.

So none of the six witness pins that name an `offset-set` value is
re-pinned by S1.

### 6.3 At `4976f385` (this revision's branch point)

Filled from `s1/census_b_main_summary.txt` (the same instrument over a probe
build of `4976f385` and its own corpus): see the table appended below this
line.

---

## 7. Stamps, abi, axes, spec, sabotage, plan (D76/D80/D94)

- **abi: ONE bump**, to the next number after main's at landing (k64fix
  takes 33 if it lands first, so S1 is probably 34). The site list is every
  reader of the number, found by grep (D94). Then run the registry, codegen
  and rxtsource suites (the D94 addendum). The Q1 conversion commit rides
  the SAME abi event (Frank's ruling), with no second bump.
- **Axis `-fno-run-prefilter`, `PCREC_NO_RUN_PREFILTER` (bit 32):**
  - a `#define` in `lib/pcrec.h` with the house doc-comment (it names the
    two-bit deny and why);
  - an `axes.def` row (`PCREC_AXIS_DEFAULT_ON`);
  - masked in `strategy_denials`.
  - `tests/axes/run_axes.sh` and `tests/registry/axes_registry_check.sh`
    meet their second `#define`d bit (bit 31, `PCREC_NO_REQ_RUN`, was the
    first). Both must enumerate it.
- **The 64-bit deny plumbing (R4), S1's FIRST commit, zero artifacts and
  zero `--list-axes` bytes moved.** The type goes `unsigned` → `uint64_t` in
  `DfaCand.deny`, `dfa_select`'s `flags` parameter, `dfa_form_derive`'s
  local `flags`, `PcrecAxisCand.deny`, and `axes_dump.c`'s
  `axis_macro_name` / `axis_cli_flag` / `bit_of` / `deny_cols` / `PredAxis`
  / `emit_pred_row`. `make strict` is the tripwire it would otherwise hit
  (gcc's `-Woverflow` on the initializer). The runtime truncation of
  `cx->opt->flags` has no warning at all, and that is the silent half.
- **`--list-axes`, the prefilter axis:**
  - two new candidate rows at `order` 1 and 2, and every later row's
    `order` +2;
  - two `AXIS_DESC` sentences;
  - the deny cells of the two new rows render BOTH bits (macro
    `PCREC_NO_OFFSET_SKIP|PCREC_NO_RUN_PREFILTER`, bits `16|32`, CLI
    `-fno-offset-skip|-fno-run-prefilter`, one `|`-joined convention
    written into `docs/spec/registry.md`);
  - the table contract's columns are unchanged. Only a cell's value domain
    widens, and the registry check's parser learns it.
- **Stamp value sets (every reader, by grep of `offset-set-bounded`):**
  - `docs/spec/match_api.md` §6.3: `RX_DFA_PREFILTER`'s table gains two rows
    (7 → 9 values, `rx_info.prefilter` mirrors them). `OFFSETS` is non-`none`
    on the four `<p>_ofsskip` values, and its domain gains `0*`.
  - `docs/spec/tuning.md`: the §2.14 `[OPT-K]` value sentence and the
    §2.x census bullet.
  - `lib/pcrec.h`'s `PCREC_NO_OFFSET_SKIP` comment (it lists the two values
    and must say the flag also removes the run rows).
  - `tests/codegen/run_dfa_stamps.sh`: `PF_VALUES`, plus an INDEPENDENT text
    marker for the run term (the `!memcmp(subject + cand` inside
    `_ofsskip`), so the text re-derivation tells `run-pinned[-bounded]`
    from `offset-set[-bounded]` without reading the stamp.
  - `tests/codegen/run_form_census.sh`: floors for the two new values
    (predicted ~168 / ~18 on this census's population, floored on first
    sight from the form census's own count, K35), the `offset-set` /
    `offset-set-bounded` / `memchr` floors re-derived (C1 and B leave
    them), and `KNOWN_VALUES`. A synthetic witness is needed if the
    bounded value's corpus population is below a floor worth stating.
  - `tests/codegen/run_offset_skip.sh`: `OFS_VALUES`, plus a `router` and a
    `foo\b` row in its witness table.
  - `src/dump/axes_dump.c` `AXIS_DESC`.
  - `tests/codegen/manifests/m5_stage1_stamps.tsv`: re-pinned only if one of
    its patterns is in §6's population (the implementer greps).
- **Spec hunks (D80), in `docs/spec/tuning.md`:**
  - §2.29 G1's paragraph becomes §1.4's rule;
  - the `[OPT-K]` section gains "the run rows scan offset 0 when a pinned run
    and today's `memchr` byte agree; the run is verified as one term outside
    the k-set cap of 4";
  - a new §2.30 for the flag, including the two-bit deny;
  - `match_api.md` §6.3 as above.
- **`compare_stack.md` updates in the same change:**
  - §2.3's `emit_req_run_check` and `ofsk_emit_verify` rows name P4;
  - §2.4 gains the run rows;
  - §2.5's G1 row loses "blind to an offset-set scan";
  - §1's L3 row and §5's `[OPT-K]` / `[OPT-VMSEED]` rows state the
    engine-neutral reading (§1.5);
  - §5's "sites that keep their own form" loses the floating pre-check loop
    once Q1's commit lands.
- **Implementation obligations beyond the emitter** (S1-4, S1-7,
  re-derived):
  - `ofsk_emit_verify`'s `pcrec_ctx_fail` text ("offset 0 is always a verify
    member") becomes "the chain is never empty: an offset-set row always
    verifies offset 0, and a run row always carries its run term";
  - `pf_block_ofs`'s scan-arm comment names the run rows as the only
    selection reaching `k == 0`, grounded per §3.1;
  - `prefix_k.c`'s role-A/role-B comment is NOT edited, because it stays
    true (R6), but its header gains the pin fact's paragraph (§1.1);
  - REQ_RUN's byte-identity through P4 is by construction, and the
    identity gate on the extraction commit alone is P4's acceptance;
  - run bytes never go raw into a C comment (`emit_comment_safe_byte`, the
    `*/x` class-B member).
- **Directory CLAUDE.md files:** `src/opt/CLAUDE.md` (the published fact),
  `src/gen/CLAUDE.md` (the rows, `OfsTest`), `tests/codegen/CLAUDE.md` if a
  check file is added.

### 7.1 Sabotage (numbered after the highest S-id on main at landing: S273 today, S274+ if k64fix is in)

| row | sabotage | detector | reach witness |
|---|---|---|---|
| (a) | the run term compared at `cand + o + 1` | answer: lost matches | router, `[ab]/user` |
| (b) | the run term one byte longer than proved | answer (the S268 mirror) | router |
| (c) | G1's `verifies` conjunct dropped | structural: a C2/D witness's `REQ_WHY` must read `"emitted"` (`run_prechecks.sh` §6) | `\Bfoo\B` (C2), a class-D pattern |
| (d) | `OfsTest.maxk` not widened (`ofsk.maxk` only) | `make asan`: heap-buffer-overflow READ | `[ab]/user` on a subject ending `a/us` |
| (e) | the density clause's memchr-form guard dropped | structural: `REQ_WHY "dominated"` where `"emitted"` is owed | a constructed offset-set / low-`ppm` witness |
| **(f)** | clause 3 dropped (a C2 artifact takes the run row) | structural: the witness must stamp `"offset-set"` with its model OFFSETS | `\Bfoo\B` |
| **(g)** | the pin's byte-equality test dropped (`run_o` = the first all-singleton window of length L) | answer: lost matches | `/abcd[xy]/user` on `/abcdx/user`. MEASURED with the probe's walk: true pin 6 (row declines, C0); sabotaged pin 0 passes clause 3(b) (`/` at 0) and the run row compares `/user` at offset 0 |
| **(h)** | clause 4 dropped (class A takes the run row) | structural: keyword must stamp `"offset-set"`, OFFSETS `"0,1*"` | `in\|instanceof` |
| **(i)** | the deny not honoured (the bit-32 truncation R4 names, or the deny field left 0) | structural: router under `-fno-run-prefilter` must stamp `"memchr"` and `REQ_WHY "emitted"` | router |
| **(j)** | `reseeds = false` on the run rows | structural: a seeded run-row witness whose forward machine has a scan-edge candidate must show 0 forward edges (`run_scan_edge_census.sh` §3's shape) | the census's ONE seeded run-row artifact is `wild-secrets-github-pat` (bench, C1, `run-pinned-bounded`). The build checks whether its forward machine has a chain whose head is a seed target; if not, it CONSTRUCTS a synthetic seeded C1 witness, or records the row as unreachable with its reason (N3) |

Every row carries a reach witness ([MECH-REACH]). Existing anchors that
move: S267/S268 (in `emit_req_run_check`, moved by the P4 extraction; re-anchor
from `git show HEAD:` and re-verify intent); S269/S270 (G1/G2 in
`req_admit`, edited by S1 and k64fix both); any `[OPT-K]` row anchored in
`pf_block_ofs` / `ofsk_emit_verify` (moved by `OfsTest`).

### 7.2 Implementation plan (commits, in order; one abi event)

1. **Deny plumbing to 64 bits** (R4). Zero moves; `--list-axes`
   byte-identical; `make strict`.
2. **P4 extraction.** REQ_RUN re-emitted through the primitive. Zero moves.
3. **`OfsTest`.** The `offset-set` rows and `dfa_prefilter_offsets` are
   routed through it. Zero moves. This is the implement-then-replace proof
   that the derivation IS today's selection.
4. **The pin fact** in `prefix_k.c` (§1.1). It has no reader yet, so zero
   moves.
5. **The mechanism** (abi bump):
   - 5a: G1 reads the selected row's `OfsTest` (A and E elide: 74 + 253
     corpus, 3 + 4 bench movers);
   - 5b: the flag, the `axes.def` row and the run row pair (B, B-bounded
     and C1 move: 186 corpus, 27 bench).
   Each sub-commit's program-region movers must equal §6's classes, by id.
   With them go the spec hunks, the stamp-reader updates, the witness file,
   sabotage (a)-(j), the directory CLAUDE.md files and `compare_stack.md`.
6. **Q1's conversion, LAST, in the same abi event, measured on its OWN pin**
   (Frank's ruling). The floating-run pre-check's loop becomes a call of the
   one search block. It carries its own safety bar:
   - answer-identity vs commit 5 over corpus × every startpos × all engines;
   - the identity gates;
   - test-axes on the touched axes;
   - ASan/UBSan on the converted artifacts;
   - its own sabotage row.

   Its design detail is the build lane's to write up against this note's
   `OfsTest` / block-emitter split. The block emitter reads no `Dfa`, which
   is what lets a pre-check caller use it.

---

## 8. Interactions

### 8.1 k64fix (unmerged, abi 33)

Unchanged by option B. G1 is admission, and its placement and its
`verifies` conjunct are the same fact, now read off `OfsTest`.
- G1 fires only where a DFA scan exists AND its candidate test implies the
  run. So the elided pre-check's NOMATCH is reached with zero attempts
  (§3.3), which is the no-match proof K64 exists to keep.
- The one-byte density clause is NOT a second K64 gap (S1 review S1-2,
  REFUTED; the argument is unchanged).
- k64fix's `!prefilter_collapsed` conjunct is more conservative than
  needed. That is a fact for its lane, not a change request.
- Textual: both lanes edit `req_admit`'s neighbourhood and re-anchor S269.
  Whichever lands second rebases.

### 8.2 The forced-VM residual → `[OPT-VMSEED]` (Q3, ruled)

The four forced-VM cells (+9.2..10.7% over `25b1984f`) and
`json-array-begin`'s forced-VM pair have no DFA scan. Their lever is the VM
seed, now plan row `[OPT-VMSEED]`, placed by addendum 4 on THIS table as a
consumer hook or rows (§1.5). S1's contribution is the two "must not
preclude" properties there: the pin fact and a DFA-free block emitter.

### 8.3 What S1 must not absorb

- **Caseless is excluded from the run TERM by construction** (S1-3): a folded
  letter is a 2-member walk set, never a run singleton. `(?i)/1234` (B) and
  `(?i)x/1234` (C1) DO take the run rows, soundly.
- No SWAR form row: S1 adds no compare form, and its only new rows are the
  selection pair.
- No change to the model's constants or its "scan must move" rule.
  `prefix_k.c`'s selection is byte-for-byte untouched.
- No multi-literal. D stays.
- No C2 (Q2): the run rows never re-point a scan (clause 3).

---

## 9. Frank's rulings on revision 1's questions (recorded; none reopened)

1. **Q1 RULED:** the floating-run pre-check is converted within S1, as a
   separate last commit inside S1's abi event, on its own bench pin, with its
   own safety bar (§7.2 step 6).
2. **Q2 RULED:** class C2 is left out of S1. It is revisited only as a
   measured follow-up once `[FINDINGS]` run-level values exist. A2 (§1.4)
   is the same question on an A-shaped artifact and is left out with it.
3. **Q3 RULED:** `[OPT-VMSEED]`, placed on `dfa_pfs[]` by addendum 4 (§1.5,
   §8.2).
4. **Q4 CLOSED** (S1 review S1-2, refuted).

**New questions this revision raises, for the panel first, then Frank if
the panel splits:**
- (N1) The two-bit deny (§1.2) versus any alternative the axis lens prefers.
- (N2) B-bounded's inclusion (R7), versus a `!views` conjunct on clause 3(b).
- (N3) Row (j)'s synthetic witness: construct one, or record it as
  unreachable today.

---

## 10. The Linux measurement request (ready to append to the bench inbox; the manager sends it)

> **I-1xx ([OPT-LITSCAN] S1 acceptance, after the lane lands).** Two pins:
> **P1** = the S1 mechanism commit (§7.2 step 5), **P2** = the Q1 conversion
> commit (step 6); each is attributed on its own (Frank's Q1 ruling).
> Testees auto-caps, auto-nocaps, vm-caps, vm-in-caps; `capability@0.1`,
> both regimes.
>
> **Arms on P1:**
> - (a) the base pin (`b5c1423b`, or k64fix's if it has merged);
> - (b) P1;
> - (c) P1 with `-fno-run-prefilter -fno-req-run`. That is router's
>   `25b1984f` program: `-fno-req-run` alone already denies the run row
>   (no run, nothing to pin, §1.1 invariant 2), and the explicit
>   `-fno-run-prefilter` keeps the arm robust. Program identity was verified
>   at `b5c1423b` (`s1/router_c_identity.sh` + its recorded output), and the
>   lane re-verifies it at P1.
>
> **Targets:** router and keyword thr, auto ×2. Bar: (b) ≤ `25b1984f` +
> band. Predicted router 337k (range 330-394k), keyword 731k.
>
> **(i)'s question:** router (b) against (c), reported as a number.
>
> **Carve-outs (H1/H3):** slack-webhook-url, github-pat, file-ext-order,
> foo-foobar, semdiv-dollar, uuid-grok, auto ×2, both regimes. Bar: within
> the band of (a).
>
> **No-move controls on P1** (program-identical; verify the stamps first):
> router/keyword/github-pat/nested-comment-rec on vm-caps/vm-in-caps.
>
> **On P2:** the same cells, P2 against P1. Bar: within band everywhere,
> with the V controls "changed program, predicted equal".
>
> **Stamps to check before timing:**
> - router: `RX_DFA_PREFILTER "run-pinned"`, OFFSETS `"0*,1,2,3,4"`,
>   `REQ_WHY "dominated"`;
> - keyword: `"offset-set"`, `"0,1*"`, `"dominated"`.
>
> **Bucketing note:** `RX_DFA_PREFILTER` (and `rx_info.prefilter`) gains the
> values `"run-pinned"` and `"run-pinned-bounded"` at this abi. Any bench
> bucketing keyed on the prefilter value needs them.
>
> Answer-check every arm before timing (the O-51 precedent). The lane's
> twin (`s1/mk_twin.py`) matched the shipped spans on 78/78 subjects.

A PRE-implementation twin run is NOT requested (D77: the landing is the
measurement).

---

## 11. The four lenses

| lens | reading |
|---|---|
| specific vs general | General: every pinned run with scan identity (186 corpus + 27 bench artifacts take the rows), not a router clause. The run TERM is P3's general record, and `OfsTest` is the one derivation every `<p>_ofsskip` reader already needed |
| core vs derived | Derived from existing facts only: the walk's singletons, `Job.req_run`, and axis B's selection. The pin is a coincidence of two published facts, stated once, not a second analysis |
| applicable vs assumption-changing | One assumption relaxed, "no scan sits at offset 0", only by a row whose predicate proves both of its facts (§3.1). One wider assumption met: a deny bit ≥ 32 on a DFA_SELECT row (R4) |
| fits the architecture vs refactor | Fits, and more squarely than revision 1: ONE selector decides every scan form (addendum 4), the rows mirror the existing pairs, and `OfsTest` is implement-then-replace with a zero-move gate. The engine-neutral generalization is deliberately NOT done here (§1.5) |
