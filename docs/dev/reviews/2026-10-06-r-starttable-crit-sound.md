# Light D6 panel, critic `sound`: `docs/design/start_table.md`

**Lens:** is the no-mover claim sound? That covers §2.3 "selection identity by
construction", §3.7, the inventory's completeness, the cross-slot reads, ask
order, and the four disagreements.

**Setup:** read-only critic, main at `b7525b9b` (the note was written from
`74379fe0`; every line cited below was re-read at `b7525b9b`). Probes ran on
`build/pcrec` (abi 64) through a scratch helper in `/tmp/stcrit/` that prints
the start-family stamps. No `make`, nothing built, nothing in the tree touched
except this file.

**Verdict.** I found no BLOCKER. I could not construct an input on which the
refactor, implemented as the note describes, would move an answer and slip
past every one of the note's own controls (§3.3 items 1-5). The C1 selection
trace is the control that catches the worst case below (M1).

But the "by construction" argument has five holes, and the inventory is not
complete:
- A whole route class (ATTEMPT-engine VM hybrids) is described wrongly.
- Two presence sub-decisions and one NEXT admission live outside the 10 sites.
- The slot DAG omits four read-by-restatement edges into BOUND.
- A fifth disagreement exists. The survey already probed it, and it explains
  a population the note treats as a coverage accident.
- The sabotage re-aim count is too low by at least two, and probably three.

Counts: **0 BLOCKER, 6 MAJOR, 6 MINOR, 6 NOTE.**

---

## MAJOR

### M1. ATTEMPT-engine VM hybrids are a fourth routing shape the note misdescribes

The note (§2.2 NEXT, §2.3 "Hybrid") says:
- "The VM hybrid's inlined prefilter body is a DFA-route customer of
  N1-N11/N13";
- per route, "Hybrid: … N/S on the inlined DFA body; R and B in the VM loop".

This is false whenever the hybrid's prefilter machine is `ENG_ATTEMPT`. Any
pattern containing a BOT goes there: `compile.c:1874` sends
`pcrec_nfa_has_bot` patterns to the `ENG_ATTEMPT` arm (`:1913-1914`), and that
branch serves hybrids too.

Probed:

| pattern | ENGINE | VM_PREFILTER | DFA_SCAN | DFA_PREFILTER | REQ_WHY | VM_START |
|---|---|---|---|---|---|---|
| `x\|^(a+)b` | vm | hybrid | **attempt** | none | none | unanchored |
| `(?m)^(a)` | vm | hybrid | **attempt** | memchr (N12, the `\n` predecessor) | **dominated** | unanchored |
| `(?m)^(ERROR\|WARN)(x+)+y` | vm | hybrid | **attempt** | memchr (N12) | emitted | unanchored |
| `^(a)(b\|c)` | vm | hybrid | **attempt** | none | one-attempt | anchored |
| `(?(DEFINE)(?<g>\Ga))(?&g)(b)` | vm | hybrid | **attempt** | none | emitted | **unanchored** |

Consequences for the claim:

1. **The inlined body is a CR_ATTEMPT customer.** It takes N12/N13, not
   N1-N11/N13. It also asks BOUND on the ATTEMPT route inside the prefilter
   (`^(a)(b|c)` emits `const size_t start_max = 0` in the prefilter and
   `const size_t attempt_max = search_from` in the VM loop). So one artifact
   asks BOUND twice, on two routes. The note's per-route skeleton has no such
   case.
2. **D-2b occurs inside one artifact.** `(?(DEFINE)(?<g>\Ga))(?&g)(b)` emits
   `start_max = search_from /* fully \G-anchored */` in its prefilter (B2,
   machine-derived) and an unbounded VM loop (B5, because the `start_anchor`
   fact says unanchored). The note characterises D-2b only as a disagreement
   between routes of different artifacts.
3. **The census conflates the classes.** `row_census.py:52-55` keys `ATTEMPT:`
   on `DFA_SCAN "attempt"` and `HYBRID:` on `VM_PREFILTER "hybrid"`
   independently, so ATTEMPT hybrids count in both. The 184 `HYBRID: "none"`
   and 500 `HYBRID: "memchr"` cited as DFA-route customers include
   ATTEMPT-route rows.
4. **D-1 hides the mis-route at stamp level.** N9 and N12 both stamp `"memchr"`.
   Suppose C3 derives the inlined body's route from `fit.chosen` (as the note's
   text invites) rather than from `job->engine`. Then an ATTEMPT hybrid would
   walk the DFA rows over a non-UNANCH machine. Where that lands on N9, the
   `DFA_PREFILTER` stamp does not move. Only G1's byte (and hence `REQ_WHY`) or
   the emitted loop would move, if they move at all. The C1 trace (row
   identity) is the control that catches it. The byte streams alone may not.

**What the note should say.** The route is a function of `job->engine` for
every DFA-shaped body, the hybrid's inlined one included. §2.3 needs a
fifth per-route line ("ATTEMPT hybrid: W, P, H, F on the VM entry; N
(N12/N13), B (B1/B2/B5) and S on the inlined body; R and B (B3-B5) in the VM
loop"). The census should split `HYBRID×ATTEMPT`.

### M2. Inventory miss: two route-keyed PRESENCE sub-decisions (K65, K66)

PRESENCE is not only `req_admits[]`. Two inline decisions add or remove
landmark checks by route, keyed on `pcrec_artifact_has_dfa_scan`:

- **K65 set-rest**, `emit_req_set_rest` (`emit_dfa.c:1258`, the decision at
  `:1265`). On a route with no DFA scan, every other member of the necessary
  set gets its own `memchr`.
- **K66 whole-run**, `req_run_tests` (`emit_dfa.c:1023`, the decision at
  `:1035`). On the same route, it compares the whole run before the window.

These are start mechanisms in the note's own sense ("absence of the landmark
in the window proves no match", `map = PRESENCE`). They are the K64/K65/K66
give-up proofs, so their posture is `FIXED`.

Neither appears among the 37 rows or the 10 sites. Yet the note's `scan`
column lists `SETREST` (§1.1), and no row carries it. Three sabotage rows sit
on exactly these decision lines: S277, S278, S316
(`if (pcrec_artifact_has_dfa_scan(cx)) return;` /
`… || r->whole_len <= r->len) return 1;`).

They are not first-match alternatives. They compose with P5 and P4. So the
(slot, route) first-match model cannot express them as rows without the
product-row smell §0.2 rejects.

**For the no-mover:** they stay byte-stable as function bodies, so they are
not movers. But:
- the C1 trace (§3.3 item 5, "every one of the 10 decision sites") does not
  see them;
- §0.1's "every start mechanism" claim is false;
- the payload `u.admit` has nowhere to state them.

**Recommend:** list them in §2.2 as PRESENCE-slot composition text owned by
P5's emitter, with posture and sabotage rows named. Or give PRESENCE a
`route`-keyed payload column. Either way, add them to C1's trace.

### M3. Inventory miss: the offset rows' real admission lives in `src/opt/prefix_k.c`

N3/N4 (`offset-set[-bounded]`) apply iff `UnanchStart.ofsk.nsel > 0`
(`pf_ofs_applies_common`, `emit_dfa.c:5984`). `nsel` is the output of a cost
model in `pcrec_prefix_ksets` (`src/opt/prefix_k.c:179-326`), which carries
two admission rules:
- the MATERIAL bar (`:280`, `best * MATERIAL_NUM >= base * MATERIAL_DEN →
  return`);
- the measured "scan must move off offset 0" rule (`:281-308`).

It asks the byte-rate prior (`pcrec_find_set_ppm`, `:186`). So the NEXT
slot's choice between N3/N4 and N8-N11 is decided by a selection rule (with
tuning constants) outside the table, in another layer. The table's predicate
only reads the result.

It also decides N1/N2 reachability (M4). Sabotage S187/S188 sit there
(`SAB_FILE=src/opt/prefix_k.c`). The note's sabotage census only maps
`emit_dfa.c`/`emit_vm.c`, so it does not see them.

The note never mentions `prefix_k` or `pcrec_prefix_ksets`. The survey's
family 3.2 ("the pick INSIDE a row … D151 does not cover it") names exactly
this.

**For the no-mover:** unaffected, because prefix_k stays. **For §4's sockets:**
the reverse-walk row's G3 admission, "beats it only through its admission",
competes with a hidden admission in another file. **Recommend:** name it in
§2.2 as N3/N4's admission (landmark `kset_walk`, admission `prefix_k`'s
model), and in §2.5 as the "pick inside a row" level the table deliberately
does not own.

### M4. A fifth disagreement the note omits (D-4): the run pin vs the offset-k pick

N1/N2 (`run-pinned[-bounded]`) apply only if the pin's scan offset equals the
offset-k model's (`pf_run_applies_common`, `emit_dfa.c:6037-6041`). The two
offsets come from different pickers:
- the run reader picks by rarity, with a rightmost tie;
- prefix_k picks by its cost model, with a leftmost strict `<`.

The survey's §4.2 probed this, and I reproduced it:

| pattern | arm | REQ_RUN | offsets | DFA_PREFILTER | REQ_WHY |
|---|---|---|---|---|---|
| `\d\dzq` | byte | `7a71@0` | `0,2*,3` | run-pinned | dominated |
| `\d\dxyz` | byte | `78797a@2` | `0,2*` | **offset-set** | **emitted** |
| `[0-9][0-9]hello` | byte | `…@3` | `0,4*` | **offset-set** | **emitted** |
| `abc$` | byte | `616263@1` | `0,1*,2` | run-pinned-bounded | dominated |
| `abc$` | **utf8** | `616263@2` | `0,1*` | **offset-set-bounded** | **emitted** (+ `REQ_HANDOFF "0"`) |

The `abc$` pair is the sharp one. Under utf8 the prior is NONE, so the run
reader takes the rightmost member (`c`, offset 2) while prefix_k keeps
offset 1. The pin and the pick then disagree systematically, not on ties.

This explains §3.4's "`run-pinned-bounded` is 0 under utf8 … the byte arm
carries them" and §2.2's N1/N2 utf8 population of 0/3. That is not a coverage
accident: it is a disagreement between two derivations of "which byte the
scan tests", and the refactor preserves it. Like D-1..D-3 it is not an answer
change. But it belongs in §2.4, because:
- it sets N1/N2's reachable population on a whole encoding;
- it decides `REQ_WHY` and `REQ_HANDOFF` on the affected artifacts;
- it is the cross-file identity clause the note's "one table" is meant to
  retire.

### M5. The slot DAG is incomplete: four predicates restate BOUND instead of reading it

§1.3 says three predicates read another slot's selection, and "Each keeps its
call; none restates the other slot's predicate". That holds for G1→NEXT,
F1→PRESENCE and R4→NEXT (verified: `req_dominated_applies` calls
`dfa_cand_scan`, `req_handoff_applies` calls `req_admit`, and
`vm_reseed_holds` calls `pcrec_dfa_cand_ppm`).

It is false for BOUND, which four predicates restate rather than read:

| predicate | what it restates | where |
|---|---|---|
| P2 DFA arm | `engine == ATTEMPT && dfa_interior_dead(&dfa, s1u)`, which is exactly "B1 ∨ B2" | `emit_dfa.c:7135-7141` |
| P2 VM arm | `start_anchor != NONE`, which is exactly "B3 ∨ B4" | same function |
| R3 `anchored` | `start_anchor != NONE` ("so the row and the bound it relies on are one derivation"); a shared FACT, not a shared SELECTION | `emit_vm.c:11088-11090` |
| N7's anchoring conjunct | declines exactly where B3/B4 apply | `emit_dfa.c:6813` |
| `attempt_cand` (N12) | re-spells B1∨B2 as its own loop `for u: if s1u[u] >= 0 anchored = false` | `emit_dfa.c:4108-4111` |

Each is "one derivation" only while BOUND is itself a direct read of that
fact or machine property. Once BOUND is a slot with rows, any new or changed
B row leaves these four behind:
- D-2b's own fix (Q6, teaching `start_anchor` through calls);
- a VM B row that reads the machine on hybrids (M1's intra-artifact split);
- any §4 bound row.

§3.7 notices the shared fact (bit 28), but frames it as a deny-bit property,
not as missing DAG edges.

**For the no-mover:** not a mover. **For the design:** §1.3's slot DAG should
list PRESENCE→BOUND, RETRY→BOUND and NEXT→BOUND (both routes). The refactor
should either route these through `cand_select(BOUND, …)` or state why each
stays a fact read. C-C10's "call, don't restate" rule is the one the note
cites, and these four break it.

### M6. Sabotage re-aim count: at least 8, probably 9, not 6. §2.3(1)'s "two exceptions" is also undercounted

C5 says "the three inline bound strings, the end-window `if` and the
root-minw `if` read their slot's row". Two sabotage rows that §3.5 files
under "47 … RE-RUN, not re-aimed" sit on precisely those lines:
- **S169** `SAB_BEFORE='… if (v->root_minw >= PCREC_MINW_MAX)'`
  (`emit_vm.c:13233`): this is the root-minw `if` C5 rewrites.
- **S263** `SAB_BEFORE='pcrec_sb_puts(c, "    const size_t attempt_max = search_from;\n");'`
  (`emit_vm.c:13479`). §2.2 puts this string in `u.bound` ("`u.bound` is the
  same string on B3 and B4"). §3.5's own rule says a literal moves into the
  row where it is shared, and B3/B4 share it. §3.5 then says "(none today)".
  The note contradicts itself, and either reading moves S263's anchor or its
  guarding `if (pcrec_fact_start_anchor(...) != NONE)`.
- **S371** `SAB_BEFORE='    if (rs->row && rs->row->action != VRS_A_FIXED) {'`
  (`emit_vm.c`, the reseed emission). When `rs->row` becomes a `CandRow *`
  with the action in `u.reseed`, this text changes.

A mech row whose `SAB_BEFORE` no longer matches fails loudly, so this is not
a silent mover. But it is a wrong plan count, and §3.2's "each re-aimed
sabotage row is verified in the commit that moves it" will meet unplanned
re-aims in C5.

Relatedly, §2.3(1) claims every row's predicate is today's function "by
pointer", with two mechanical exceptions. In fact W1
(`pcrec_fact_end_window(cx) >= 0`), H1 (`v->root_minw >= …`) and B1-B5 (the
`a_bot`/`a_gst` ternary with its `#ifdef PCREC_NO_GSTART`, and the VM's
`start_anchor` `if`) are inline conditions today. That makes seven new
predicate functions, not two, and their only existing witnesses are the
anchors above.

The census also undercounts the start family. `sabotage_anchors.family` omits
`emit_req_set_rest`, `req_run_tests`, `emit_req_run_check`, `unanch_start`,
`cand_derive` and `prefix_k.c` (S187/S188/S277/S278/S316/S459 live there).
That does not change the re-aim count, because those bodies stay, but the
"53" is not the population.

---

## MINOR

### m1. C5 reroutes the emitted condition but not its stamp and listing readers

Three readers come out of C5 still spelling the WINDOW/WIDTH/BOUND decision
directly:
- `<PREFIX>_END_WINDOW` renders the fact (`pcrec_fact_stamp(cx,
  PF_END_WINDOW)`, `emit_dfa.c:10114`);
- `<PREFIX>_VM_START` renders `pcrec_start_anchor_name(fact)`
  (`emit_vm.c:11558`);
- `<PREFIX>_VM_ROOT_MINW` and `--emit-ir`'s `root-minw` row each re-test
  `root_minw >= PCREC_MINW_MAX` (`emit_vm.c:11419`, `:9492`). The stamp's own
  comment says "one condition, read twice, never two conditions that could
  disagree".

§3.6 calls these stamps "projections" of rows, but no commit makes them read
the walk. Today the stamp and body share one derivation (the fact). After C5
the body reads the row and the stamp reads the fact. The first row added
ahead of W1 or B3 (§4.4 places [OPT-REVEND] before W1) makes the stamp
describe a mechanism the body did not emit. This is the [ENG-FORM] "the stamp
is the chosen object's name" rule.

### m2. RECOVER's readers need a property the payload does not carry

`dfa_search_is_pinned` answers by pointer identity, `== &dfa_search_starts[0]`
(`emit_dfa.c:7917`, 7 readers). §1.1 gives RECOVER `u.recover` = "none: the
form is the name", and §3.5's widened K84 check forbids comparing any
`cand_rows[]` row name. After the fold, a reader must compare against
`&cand_rows[<S1's index among 37>]`. That is a positional read in a 37-row
array, which is K84's smell in a different spelling. Give S1/S2 a payload
property (`u.recover.pinned`) that the 7 readers test.

### m3. C6's projection rules are underspecified and contradict §2.5 in one place

- C6 lists `match` among the sections that "project `cand_rows[]`". But
  `match` is `dfa_matches[]` (`unwrapped`/`search-filter`), which §2.5
  excludes from the table.
- N12 is a NEXT row. If it carries `axis = prefilter`, `--list-axes` grows a
  13th `prefilter` row and stream 5 moves. The note does not say N12's `axis`
  is empty.
- B5 is named `all` and shared by ATTEMPT and VM. The `vm-anchor-bound`
  listing names its row `unanchored` (order 3), and ATTEMPT's B1/B2/B5 have
  no listing today. The projection needs per-route `axis` and a listed name
  distinct from `c.name`. That contradicts §1.1's "`c.name` … is the stamp
  value where the slot has a stamp".

### m4. The deny arms (§3.3 item 4) omit the force flag that populates three predicates' rarest conjunct

`-fprefilter-collapse` (bit 20, `PCREC_FORCE_PREFILTER_COLLAPSE`) sets
`fit.prefilter_collapsed`, which three predicates read:
- F1's Q10 conjunct;
- P2's VM-arm `!prefilter_collapsed`;
- R1's `mrl_win` (collapse drops it, sending hybrids to R2/R4/R5).

§3.4 lists "count-collapsed hybrids: 1-2, K39's witness" as needing a
constructed witness. One cheap sweep arm (`--extra -fprefilter-collapse`)
would give a corpus-sized population instead. `tests/startset/dfahat_checks.py`
already uses it (`\B(a|b){1,3}`).

### m5. The C1 trace shares a source with the table for the five inline sites

For the five inline sites (and K65/K66, M2), the old code has no walk and no
row identity. The C1 instrumenter decides which branch prints "B2" or "W1",
and the same note then defines C2's rows. If that author's branch→row mapping
is wrong in the same way the table is, the trace agrees with the bug. Bytes
(streams 1/2) remain the only independent control there, and §3.3's "stronger
than bytes" holds only for the five walked sites.

The note also does not say whether trace diffs compare sequences or per-artifact
sets. `dfa_pf_of` is called 5 times and `req_admit` 7 times per artifact, and
`cand_select` call multiplicity may legitimately change.

### m6. The utf8 gap is narrower than stated

§0.5/§3.3 item 2 say emit_sweep never passes `-e utf8`, so "the utf8 half of
every row is unswept". `compile_stream_c` (`emit_sweep.py:429`) indeed adds
no `-e`. But stream 4 composes every `.rxt`, and the `tests/utf8/*.rxt` files
declare `encoding utf8` per block (for example `fold.rxt:50`,
`axis06_caseless_fold.rxt:32`). So the utf8-native corpus is already swept.
What is missing is the byte corpus × utf8 cross-product (the `a/u` arm).
C0's arm is still right to add. The claim should be restated.

---

## NOTE

- **n1. Ask ORDER is not observable anywhere. Only the evaluated SET is.**
  - The facts `used` column is a per-fact yes/no
    (`facts_listing.md:95`; `pf->used |= pf_bit(f)`, `facts.c:115`).
  - `RX_FINDINGS` reads `byte_rate_asked`, a boolean (`findings.c:373-380`),
    and is written after every emitter has run (`emit_dfa.c:2687-2698`).
  - So §2.3(4)'s "the set of predicates EVALUATED, and their order, is
    today's" overclaims, and §3.3 item 3's "a walk that reorders … moves it"
    is false: a pure reorder moves nothing the sweep can see.
  - The one order-sensitive effect is which internal error wins when two
    predicates assert. `pf_dfa_start_set` and `pf_vm_start_applies` call
    `pcrec_ctx_fail` from inside a predicate (`emit_dfa.c:6670-6676`, the
    `vm_start_assert_starts` call). §1.3's side-effect list omits that
    predicates can longjmp.
  - State the invariant as SET equality, plus "no new predicate reaches an
    assertion".
- **n2. "Slot order = body ask order" (§1.2) is not true.**
  - RECOVER is asked first on the DFA body (`dfa_search_is_pinned`,
    `emit_dfa.c:8829`, before W/P/F).
  - RETRY is decided before the VM body (`vm_plan_reseed`, before the stamps).
  - ATTEMPT asks N12 (`:9323`) before B (`:9353`), while §2.3 lists B before N.
  - Harmless under n1, but the skeleton of §1.3 is not what the code does.
- **n3. §2.3's per-route lists miss two asks.**
  - VM-only also asks FIRST: `pcrec_emit_req_byte_check` → `req_use` →
    `req_handoff_applies`, which declines on `!has_dfa_scan`.
  - DFA artifacts ask NEXT on route VM: `vm_start_row` for
    `RX_VM_START_SCAN`, stamped on every artifact (seen on `abc$`, a DFA
    artifact).
- **n4. The route set is coarser than the predicates.** HYBRID vs VM-only
  (`fit.prefilter`, read inside N7 and P2) and EMPTY (`dfa_engine_is_empty`,
  read inside F1 and S1) are route distinctions re-tested in predicates. The
  table's `routes` column cannot express them. That is fine for a no-mover,
  but §0.2's "the slot is the same filter along a second axis" leaves a third
  axis inside the predicates.
- **n5. S490 needs re-verifying after C3.** S490 ships UNDETECTED as an
  EQUIVALENT mutant "while every caller is reached on ENG_UNANCH machines
  only". After C3 that premise moves from "ATTEMPT callers never call
  `dfa_pf_of`" to "the routes column excludes ATTEMPT from N5/N6". Re-verify
  the equivalence argument when the route is added, not only the comment text.
- **n6. D-1, D-2 and D-3 are confirmed as characterized**, with one extension:
  - D-1 also fires on ATTEMPT hybrids. On `(?m)^(a)`, `REQ_WHY "dominated"`
    elides the `a` pre-check on a predecessor-`\n` scan.
  - D-2: confirmed. `(?m)^ERROR` stamps `"reverse-pass"` and the spec at
    `match_api.md:4702` lists `"attempt"`/`"empty"` in that row.
  - D-3: confirmed at `axes_dump.c:106`.
  - R4's read of N12's byte (via `pcrec_dfa_cand_ppm`) is NOT a D-1 victim.
    The predecessor byte IS the scan's stop density, which is what R4 prices.

---

## Claims I tried and could not refute

- **Row order within each array-derived slot.** P1-P5 against `req_admits[]`
  (`emit_dfa.c:7249`), F1/F2 against `req_uses[]` (`:7364`), N1-N11/N13
  against `dfa_pfs[]` (`:6863-6898`), R1-R6 against `pcrec_reseed_rows[]`
  (`emit_vm.c:11010`), S1/S2 against `dfa_search_starts[]` (`:7894`): all
  match, deny bits included.
- **Walk semantics.** `dfa_select` applies deny, then route, then applies
  (`:5155-5162`), and `vm_plan_reseed` applies deny, then predicate. A unified
  walk with slot as an extra pre-applies filter evaluates no predicate today's
  walks skip, provided each caller asks the same route. M1 is the case where
  that proviso is under-specified.
- **Totality per (slot, route).** Every pair asked has a trailing
  `cand_always` row (P5, F2, N13, R6, B5, S2, W2, H2).
- **Cross-slot reads G1→NEXT, F1→PRESENCE, R4→NEXT** call rather than
  restate. All three verified.
- **Deny bit numbers** 16/22/28/29/30/31/32/37/44/45/46/47 match
  `lib/pcrec.h`. §3.7's bit-28 analysis (a fact deny reaching P2, N7 and R3)
  is correct.
- **D-2b direction.** The one-way assertion (`emit_dfa.c:9374-9382`) makes
  "machine stricter than fact" the only reachable disagreement, and that
  direction removes only failing VM attempts.
- **No-eager-plan hazard (§1.3).** I looked for a predicate today's code
  evaluates conditionally that a per-slot walk would evaluate eagerly:
  - `vm_start_row` runs on every artifact, including DFA ones;
  - `req_admit` is gated by `pcrec_emit_req_byte_check`'s pre-test (`:1375`);
  - RETRY runs only under `fit.prefilter`.

  As long as the plan keeps those call sites and guards, none moves.
- **The handoff vs pinned RECOVER.** They are structurally exclusive: pinned
  needs an accepting start, so P1 holds and no run pre-check exists.
  `req_handoff_assert_body` makes the combination loud.
