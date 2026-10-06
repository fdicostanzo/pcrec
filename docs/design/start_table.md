# One start-strategy table — the row contract, the inventory, the no-mover refactor

**DESIGN NOTE, PROPOSED, nothing built** (lane `starttable`, 2026-10-06, from main
`74379fe0`, abi 64). Nothing under `src/`, `cli/`, `lib/` or `tests/` changes. The
instruments and their committed output are in `start_table/` (own CLAUDE.md). A
light D6 panel reviews this note before any build. Rulings are Frank's; §6 lists
the open questions, each with a recommendation.

Frank (2026-10-06): "So are we going to reorganize around a single start strategy
decision table?" — then "Agree with direction" to the manager's three-step plan:
(1) this note and a light panel; (2) a NO-MOVER refactor that puts every existing
start mechanism into ONE first-match table under one row contract, gated by
`scripts/emit_sweep.py` at 0 movers; (3) new rows afterwards, each its own abi
event.

Read before writing: `where_to_start.md` (the study, D151), D148 + addenda 1-4 and
`startset.md`, D124, `offset_k_skip.md`, `litscan_k82h.md` §2.1 (why `req_uses[]`
was born separate), `docs/dev/optloop/revend_census.md` ([OPT-REVEND]), K88/K90,
[ARTREV] `generalize.md` I5, `src/facts/facts.def`, `docs/spec/facts_listing.md`,
`docs/design/memfn/integration.md` §8.5 + `tests/memfn/site_manifest.tsv`, and the
table sites in `src/gen/emit_dfa.c` / `src/gen/emit_vm.c` at this pin.

---

## 0. Answers first

1. **Yes, and the table is literally one array.** Today ten separate decision
   sites pick a start mechanism: five first-match arrays (`dfa_pfs[]`, `req_admits[]`,
   `req_uses[]`, `dfa_search_starts[]`, `pcrec_reseed_rows[]`) and five inline
   decisions with no table at all (ENG_ATTEMPT's predecessor-byte skip
   `attempt_cand`, ENG_ATTEMPT's `start_max`, the VM's `attempt_max`, the
   end-window clamp and the root minimum-width check). The design folds all of
   them into ONE array, `cand_rows[]` (D148 Q2's name), of ONE row type,
   `CandRow`, selected by ONE walk.
2. **"One first-match table" needs a SLOT column, and that is not a planner.** An
   artifact today runs several start mechanisms at once: an end-window clamp,
   then a presence pre-check, then a handoff, then an in-loop skip, then a
   reverse pass. A single first-match winner per artifact cannot express that
   without product rows (`set-leads-handoff`, …), which is the parallel-row smell
   `litscan_k82h.md` §2.1 rejected. So each row carries the QUESTION it answers
   (its slot: window, presence, width, first-scan, next-candidate, retry, bound,
   recover), and the walk is first-match per (slot, route). This is the
   mechanism the table already uses for engines: `dfa_pfs[]` carries a `routes`
   mask since START-SET, and the VM route and the DFA route each get their own
   first-match over the one list (`cand_routed`, `emit_dfa.c:5139`). The slot is
   the same filter along a second axis. Composition across slots is fixed by the
   search-body skeleton (§1.3), never selected.
3. **The inventory is 37 rows in 8 slots over 3 routes** (§2.2), and the census
   finds three places where today's dispersed sites disagree (§2.4). None is an
   answer disagreement. A no-mover refactor preserves all three, and each fix is
   named as a separate ruled change. One of them is new: an ENG_ATTEMPT artifact
   stamps `RX_DFA_START "reverse-pass"` though it carries no reverse machine.
4. **The refactor is eight commits, implement-then-replace** (§3.2). Predicate
   and emitter FUNCTIONS stay byte-stable and only the tables and walks move. So
   47 of the 53 sabotage rows anchored in start-family code keep their anchors,
   and 6 must be re-aimed. No abi event: every emitted byte and every stamp value
   is unchanged, and the listing (`--list-axes`, stream 5) is byte-identical
   until one declared listing commit.
5. **`emit_sweep` alone cannot prove the no-mover claim, for three measured
   reasons** (§3.3-§3.4):
   - its argv streams never pass `-e utf8` (`compile_stream_c`,
     `scripts/emit_sweep.py:429`), so the utf8 arm the brief requires does not
     exist yet;
   - `--emit-facts`' `used` column records which facts a predicate ASKED, which
     no emitted byte shows, so a walk that evaluates a predicate today's code
     does not evaluate is invisible to all five streams;
   - a row the corpus never selects is not proven by any byte sweep.

   The plan adds the first two as sweep arms (commit C0) and gives every
   zero-population row a constructed witness.
6. **The new rows each land in one slot** (§4): the D151 reverse-walk row in
   NEXT (the DFA and VM hats) plus `handoff-rev` in FIRST; I5 as a context
   column on the VM hat row; K90's dense-start fix as the RETRY slot's adaptive
   rows gaining the VM-only route. That last is the generalization: K90's
   proposed "density-adaptive disarm" IS [OPT-HYB-RESEED]'s rule, which today
   serves only the hybrid.

---

## 1. The row contract

### 1.1 The fields

One row is one way of answering one start question on one or more routes. Fields
(designated initializers, K84's house rule: an omitted field is its zero value,
so a reader never falls back to the NAME):

| field | what it holds | today's equivalent |
|---|---|---|
| `c.name` | the row's name, which is the stamp value where the slot has a stamp | `DfaCand.name` |
| `c.deny` | the `lib/pcrec.h` bit(s) that REMOVE the row (`uint64_t`, so bits ≥ 32 deny) | `DfaCand.deny` |
| `c.applies` | the admission predicate over [PATFACTS] facts and the compile, `bool (*)(const CandSel *)` | `DfaCand.applies` |
| `slot` | the question answered (§1.2) | implicit: which array the row is in |
| `routes` | `CAND_ON(route)` mask over `CR_DFA` (the ENG_UNANCH scan body), `CR_ATTEMPT` (the ENG_ATTEMPT start loop), `CR_VM` (the VM attempt loop); 0 means `CR_DFA` alone, today's default | `DfaPf.routes` (two values today) |
| `landmark` | the fact(s) the row reads, as `facts.def` names (`start_set`, `kset_walk`, `run_pin`, `req_run`, `req_run_maxoff`, `req_set`, `req_byte`, `end_window`, `start_anchor`) or a machine property (`s0 escapes`, `seed liveness`, `root_minw`) | prose in each predicate's header |
| `scan` | the scanner KIND, and for a scan the memfn site id it is delegated through: `PF`, `PRE`, `OFS`, `SETREST`, `MLINE`, `VMSTART`, or `none` (`tests/memfn/site_manifest.tsv`'s ids; D146) | `DfaPf.scan` (`PF_SCAN_*`), the manifest |
| `map` | the hit→candidate mapping (§1.4) | prose |
| `hat` | the consumer: the DFA (re-seeded or not), the attempt loop, the VM attempt, the reverse machine | `reseeds`, `emit*` hooks |
| `giveup` | the row's give-up posture (§1.5) | prose in two design notes |
| `axis`, `stamp` | the `--list-axes` axis this row is listed under today, and the stamp macro it is reported through. These are PROJECTIONS, kept byte-identical in the refactor | `axes_dump.c`'s per-axis emitters |
| `desc` | the listing's one-line `applies` text, BESIDE the row | `req_admits[].desc`, `pcrec_reseed_rows[].applies_desc`, and for `dfa_pfs[]` a SEPARATE hand table in `axes_dump.c:85-` (§2.4 D-3: it has drifted) |
| `u` | the slot's payload, a typed union: `u.pf` (today's `DfaPf` emit hooks, `reseeds`, `run_term`, `scan_set`, `emit_vm`), `u.admit` (`ReqAdmit` verdict), `u.use` (`ReqUse`), `u.reseed` (action, start column, armed), `u.bound` (the emitted bound string), `u.recover` (none: the form is the name) | the five arrays' own row structs |

A union rather than a `const void *`: each slot's emitter reads its own member
with a compile-time type, and a row initialised with another slot's member is a
`run_cand_rows.sh` failure (§3.5), not a cast.

### 1.2 The slots, in body order

The slot order is the ORDER THE SEARCH BODY ASKS, written once as the skeleton
(§1.3). Within a slot the rows are in information order (`where_to_start.md` §1.4:
EXACT before WINDOW before LOWER-BOUND before PRESENCE; rarity is an admission
conjunct, never an order).

| slot | the question | asked at | today |
|---|---|---|---|
| `WINDOW` | can a match begin before some position computed from the END? | the caller-facing entry, once | `pcrec_emit_end_window_clamp` (inline) |
| `PRESENCE` | does the window hold every necessary landmark at all? | the entry, once | `req_admits[]` |
| `WIDTH` | can the remaining subject hold a match at all? | the VM entry, once | `root_minw` test (inline) |
| `FIRST` | where does the first scan begin? | the entry, once | `req_uses[]` |
| `NEXT` | how is the next candidate start found? | the loop: at `s0` (DFA), between attempts (ATTEMPT, VM entry and retry) | `dfa_pfs[]`, `attempt_cand` (inline) |
| `RETRY` | after a failed VM attempt behind a prefilter, step or re-seed? | the hybrid's loop tail | `pcrec_reseed_rows[]` |
| `BOUND` | how many start positions can match at all? | the loop header | `start_max` (inline, DFA), `attempt_max` (inline, VM) |
| `RECOVER` | given a match END, where does it start? | after the forward scan | `dfa_search_starts[]` |

### 1.3 The walk, and what it does not do

```c
const CandRow *cand_select(CandSlot slot, CandRoute route, const CandSel *s, uint64_t flags);
/* first row with row->slot == slot, !(row->c.deny & flags),
 * routed for `route` (cand_routed's rule), and row->c.applies(s) */
```

- **Total per (slot, route).** Every (slot, route) pair a body asks has a last
  row whose predicate is `cand_always`, so `NULL` stays unreachable (today's
  `dfa_select` property, `emit_dfa.c:5155`). A structural check enumerates the
  pairs (§3.5).
- **No eager plan.** Each body site asks exactly the (slot, route) it asks today,
  when it asks today. A whole-artifact "resolve every slot up front" pass is NOT
  part of the refactor. It would evaluate predicates today's code never reaches,
  and predicates have observable side effects: `pcrec_find_byte_rate` records
  its first ask, the ask is what puts `RX_FINDINGS` into the artifact
  (`pcrec_find_stamp`, `src/core/findings.c:373`), and the facts layer's `used`
  column records every ask (§3.3 item 2).
- **Slots read each other only through the walk.** Three predicates read another
  slot's SELECTION, and that dependency is the slot DAG: `PRESENCE`'s G1 row
  (`dominated`) reads `NEXT`'s choice (`dfa_cand_scan`, `emit_dfa.c:7034`);
  `FIRST`'s handoff row reads `PRESENCE`'s verdict (`req_handoff_applies` calls
  `req_admit`, `:7336`); `RETRY`'s `adaptive-dense` row reads `NEXT`'s scanned
  set (`pcrec_dfa_cand_ppm`, `:7079`). Each keeps its call; none restates the
  other slot's predicate (`litscan_k82h.md` r1 C-C10's rule).

### 1.4 The mapping column

`where_to_start.md` §1.1's four strengths, sharpened to the cases the inventory
actually contains:

| `map` | a hit (or the slot's event) says | rows |
|---|---|---|
| `EXACT0` | the hit IS a candidate start | `memchr*`, `byte-class*`, `first-*` |
| `EXACTK` | a candidate starts `k` before the hit | `offset-set*`, `run-pinned*` |
| `EXACTPRED` | a candidate starts one AFTER the hit (a predecessor byte) | ENG_ATTEMPT `memchr` |
| `EXACTREV` | (future) a reverse walk from the hit records the candidate | D151's row |
| `WINDOWLO` | no start below `n − W` | `window` |
| `WINDOWHI` | no start above `n − minw` (none at all if the window is too short) | `ceiling` |
| `LOWERBOUND` | no start below `hit − K`; scan forward from there | `handoff` |
| `PRESENCE` | absence of the landmark in the window proves no match | `emitted`, `set-leads` |
| `ONE` | at most one start position exists (0, or `search_from`) | the bound rows |
| `RECOVER` | the start is read from the end (reverse machine) or is `search_from` (pinned) | `reverse-pass`, `pinned` |
| `STEP` / `RESEED` / `ADAPT` | the retry's next candidate: advance one character, re-call the prefilter, or switch by gap | the reseed rows |
| `NONE` | nothing is skipped | every fallback |

The column is DATA for checks and the listing. No emitter branches on it (the K84
rule: a reader tests a field that names a property, and `map` names one).

### 1.5 The give-up posture column

Three postures exist today, and the refactor writes each down per row:

- `NEUTRAL`: the row changes no attempt the VM runs. Every DFA-route row, and the
  presence rows (they answer NOMATCH only where no attempt could succeed).
- `ONE_WAY`: the row skips VM attempts the deny arm runs, so a give-up may become
  an answer, never the reverse (D148 Q6 + Q-R3: steps, work, frames, trail, the
  `_in` buffers). Rows: `first-class` (VM hat), the `anchored`/`gstart` VM bound
  rows, `adaptive-dense`/`adaptive` (`hyb_reseed.md` §4's contract), `ceiling`.
- `FIXED`: the row must never move the give-up surface. Rows: `handoff`
  (Frank's Q10: declined on a count-collapsed prefilter so the deny flag never
  moves it).

D151 Q4 ruled the reverse-walk row `ONE_WAY`. The column makes the K82-vs-D148
difference a visible property instead of a sentence in two notes.

---

## 2. The inventory

### 2.1 How it was counted (K35)

Three instruments, all in `start_table/`, none reading this note:

- `site_census.sh` greps `src/` for every decision table, every inline start
  decision and every reader of either (`site_census.txt`). That gives 5 tables,
  5 inline decisions plus the 2 route-fixed VM seed lines, and the reader
  counts used below.
- `row_census.py` compiles the whole `.rxt` corpus and reads the STAMPS (never
  `src/`) in four arms: engine auto / `--engine=vm` × `-e byte` / `-e utf8`.
  It uses `emit_sweep.py`'s own `enumerate_corpus`, so it and the sweep cannot
  disagree about which patterns exist. 3,595 distinct patterns; 3,221-3,230
  compile per arm (`row_census.txt`, `.tsv`). It also records JOINT keys where
  one stamp conflates two routes' rows (§2.4 D-1).
- `anchor_agree.py` compares the two derivations of "every match starts at one
  position" on the ENG_ATTEMPT population (`anchor_agree.txt`, §2.4 D-2).

### 2.2 The table, in first-match order

Columns:
- **pop** is the corpus artifact count in the arms where the row is reachable.
  `a/b` means auto/byte; `vm/b` means `--engine=vm`/byte; `a/u` and `vm/u` are
  the utf8 twins.
- **today** is the site the row replaces.
- **predicate** is today's function, reused by pointer.

**WINDOW** (routes DFA, ATTEMPT, VM; the caller-facing entry only: on the DFA
under `fit.chosen == ENGM_DFA`, so the VM hybrid's inlined prefilter never clamps
and the VM entry clamps before calling it; `emit_dfa.c:8869`, `:9166`,
`emit_vm.c:13170`):

| # | row | deny | predicate | map | pop |
|---|---|---|---|---|---|
| W1 | `window` | — (the bit is a FACT deny: `-fno-end-window`, bit 29, empties `end_window`, `facts.def`) | `pcrec_fact_end_window(cx) >= 0` (`emit_dfa.c:938`) | `WINDOWLO` | a/b 288, a/u 0 (the fact declines every non-boundary encoding) |
| W2 | `none` | — | `cand_always` | `NONE` | rest |

**PRESENCE** (all routes; the entry; today `req_admits[]`, `emit_dfa.c:7249`,
asked by `pcrec_emit_req_byte_check` `:1375`, `req_lead_byte` `:7280`,
`req_handoff_applies` `:7336`, the `<string.h>` decision `:10007`, the stamp):

| # | row | deny | predicate | map | pop (a/b) |
|---|---|---|---|---|---|
| P1 | `none` | — | `req_none_applies` `:7193` (no `req_byte` and no `req_run` of length ≥ 2) | `NONE` | 1,178 |
| P2 | `one-attempt` | — | `req_one_attempt_applies` → `req_route_one_attempt` `:7135` (VM: `start_anchor` ≠ NONE ∧ (exact hybrid ∨ frameless); DFA: ENG_ATTEMPT ∧ `dfa_interior_dead(s1u)`) | `NONE` | 263 |
| P3 | `dominated` | — | `req_dominated_applies` `:7201` → `req_byte_dominated_by` `:7171` over `dfa_cand_scan` (reads NEXT) | `NONE` | 1,198 |
| P4 | `set-leads` | 45 | `req_set_leads_applies` `:7212` | `PRESENCE` | hidden: stamps `"emitted"` |
| P5 | `emitted` | — | `cand_always` | `PRESENCE` | 582 (incl. P4) |

**WIDTH** (route VM; `emit_vm.c:13234`):

| # | row | deny | predicate | map | pop |
|---|---|---|---|---|---|
| H1 | `ceiling` | — | `v->root_minw >= PCREC_MINW_MAX` | `WINDOWHI` | 6 in every arm |
| H2 | `none` | — | `cand_always` | `NONE` | rest |

The ceiling row's predicate reads a `Vm` field. So `CandSel` gains a
`const CandVmFacts *vm` pointer carrying the five `Vm` fields that rows read
(`root_minw`, `mrl_win`, `nclamp`, `has_push`, and the reseed calibration). It is
filled by the one VM caller and NULL elsewhere. That pointer is the only new
input.

**FIRST** (all routes; today `req_uses[]`, `emit_dfa.c:7364`, asked by
`pcrec_emit_req_byte_check`'s return `:1392`, the body assertion `:8878`, the
stamp `:7391`):

| # | row | deny | predicate | map | pop |
|---|---|---|---|---|---|
| F1 | `handoff` | 46 | `req_handoff_applies` `:7332` (calls PRESENCE; `pcrec_artifact_has_dfa_scan`; K finite; not collapsed; the `\G`-hybrid decline) | `LOWERBOUND` | a/b 163 (37 hybrid), a/u 280 (78 hybrid) |
| F2 | `scan-from-startpos` | — | `cand_always` | `NONE` | rest |

**NEXT**. Today `dfa_pfs[]` (`emit_dfa.c:6863-6898`, asked by `dfa_pf_of`
`:6903` (5 call sites), `vm_start_row` `:6931` (3), `pf_scan_set_of` `:6915`,
`pcrec_dfa_scan_state_written` `:7435`, `dfa_form_derive` `:8378`) plus
`attempt_cand` (`:4105`; 4 readers: emission `:9323`/`:9511`, G1 `:7044`, the
`<string.h>` test `:9997`, the stamp `:10411`). Every DFA row's predicate is gated
on `s->forward` and on `UnanchStart.kind` (`unanch_start` `:4191`, ONE derivation),
so it is only ever reached on the ENG_UNANCH forward machine. The S490 argument,
`emit_dfa.c:6650`.

| # | row | routes | deny | predicate | map | scan | pop (a/b; a/u) |
|---|---|---|---|---|---|---|---|
| N1 | `run-pinned-bounded` | DFA | 16\|32 | `pf_run_bounded_applies` `:6051` | `EXACTK` | OFS + VERIFY | 18; 0 |
| N2 | `run-pinned` | DFA | 16\|32 | `pf_run_applies` `:6054` (common `:6023`) | `EXACTK` | OFS + VERIFY | 114; 3 |
| N3 | `offset-set-bounded` | DFA | 16 | `pf_ofs_bounded_applies` `:5990` | `EXACTK` | OFS | 48; 71 |
| N4 | `offset-set` | DFA | 16 | `pf_ofs_applies` `:5993` (common `:5984`) | `EXACTK` | OFS | 333; 530 |
| N5 | `first-memchr-bounded` | DFA | 47 | `pf_first_memchr_bounded_applies` `:6681` (core `pf_dfa_start_set` `:6648`, T = S, D148 add. 3) | `EXACT0` + re-seed | PF | 36; 25 |
| N6 | `first-class-bounded` | DFA | 47 | `pf_first_class_bounded_applies` `:6679` | `EXACT0` + re-seed | PF | 34; 34 |
| N7 | `first-class` | VM | 47 | `pf_vm_start_applies` `:6806` | `EXACT0` | VMSTART | 66 (vm/b 2,327); 68 (vm/u 2,352) |
| N8 | `memchr-bounded` | DFA | — | `pf_memchr_bounded_applies` `:5798` | `EXACT0` | PF | 162; 151 |
| N9 | `memchr` | DFA | — | `pf_memchr_applies` `:5801` | `EXACT0` | PF | 775 (+33 ATTEMPT, D-1); 722 |
| N10 | `byte-class-bounded` | DFA | — | `pf_bcls_bounded_applies` `:5804` | `EXACT0` | PF | 100; 101 |
| N11 | `byte-class` | DFA | — | `pf_bcls_applies` `:5807` | `EXACT0` | PF | 538; 564 |
| N12 | `pred-memchr` (NEW NAME, row ID only; stamps `"memchr"`) | ATTEMPT | — | `attempt_cand` `:4105` (s1u live ∧ the live-seed set `usable ∧ use_memchr`) | `EXACTPRED` | MLINE | 33; 33 |
| N13 | `none` | DFA, ATTEMPT, VM | — | `cand_always` | `NONE` | — | 677 stamped (355 of them ATTEMPT, up to 64 the empty engine); VM-only 287 (vm/b 895) |

Row N12 needs a row name distinct from N9, because the walk and the checks key on
identity. It still stamps `"memchr"` (its `stamp` projection), so
`RX_DFA_PREFILTER` keeps today's token (D-1). The VM hybrid's inlined prefilter
body is a DFA-route customer of N1-N11/N13. It takes the DFA rows: auto/byte has
1,125 hybrids, with 500 on `memchr`, 198 on `offset-set` and 184 on `none`
(`row_census.txt`'s `HYBRID:` keys).

**RETRY** (route VM, asked only where `fit.prefilter` holds, the caller's guard
kept: `vm_plan_reseed`, `emit_vm.c:11107`; today `pcrec_reseed_rows[]`
`emit_vm.c:11010`, whose predicates are a closed tag read by a `switch`,
`vm_reseed_holds` `:11082`; the refactor turns each tag into a predicate function
with the same body):

| # | row | deny | predicate | map | pop (a/b) |
|---|---|---|---|---|---|
| R1 | `exact` | — | `Vm.mrl_win` | `STEP` (or the clamp recompute) | 562 |
| R2 | `clamped` | — | `Vm.nclamp > 0` | `RESEED` | 112 |
| R3 | `anchored` | — | `start_anchor` ≠ NONE | `STEP` (never reached) | 48 |
| R4 | `adaptive-dense` | 37 | `pcrec_dfa_cand_ppm(cx) · cal.gap > 10⁶` (reads NEXT) | `ADAPT`, armed | 13 |
| R5 | `adaptive` | 37 | `cand_always` | `ADAPT`, probation | 390 |
| R6 | `fixed` | — | `cand_always` | `STEP` | 0 at default (the deny's landing row) |

**BOUND** (`emit_dfa.c:9333-9388` for ATTEMPT, `emit_vm.c:13471-13483` for VM):

| # | row | routes | deny | predicate | map | pop |
|---|---|---|---|---|---|---|
| B1 | `bot` | ATTEMPT | — | `dfa_interior_dead(d, s1u) ∧ dfa_interior_dead(d, s1g)` (`#ifdef PCREC_NO_GSTART` folds the second into the first) | `ONE` (0) | 293 |
| B2 | `gstart` | ATTEMPT | — | `dfa_interior_dead(d, s1u)` | `ONE` (`search_from`) | 21 |
| B3 | `anchored` | VM | — (FACT deny bit 28 empties `start_anchor`) | `start_anchor == BOT` | `ONE` (0, via `attempt_max = search_from`) | a/b 332, vm/b 468 |
| B4 | `gstart` | VM | — (bit 28, as B3) | `start_anchor == GSTART` | `ONE` | a/b 5, vm/b 20 |
| B5 | `all` | ATTEMPT, VM | — | `cand_always` | `NONE` | ATTEMPT 74; VM 1,141 |

Today the VM's two values share ONE emitted line (`attempt_max = search_from`)
and differ only in the stamp (`RX_VM_START`). The rows keep that: `u.bound` is
the same string on B3 and B4. The DFA's `start_max` keeps its three strings.

**RECOVER** (today `dfa_search_starts[]` `emit_dfa.c:7894`, asked by
`dfa_search_start_of` `:7902` and through `dfa_search_is_pinned` at 7 sites):

| # | row | routes | deny | predicate | map | pop (a/b) |
|---|---|---|---|---|---|---|
| S1 | `pinned` | DFA | 22 | `start_pinned_applies` `:7860` (P1-P4) | `RECOVER` (`search_from`) | 183 |
| S2 | `reverse-pass` | DFA, ATTEMPT | — | `cand_always` | `RECOVER` (reverse) | 2,685 (incl. 388 ATTEMPT + 64 empty, D-2) |

**Row count:**
- 37 rows: W 2, P 5, H 2, F 2, N 13, R 6, B 5, S 2.
- 7 deny bits act on these rows directly: 16, 32, 45, 46, 47, 22, 37.
- 5 more act through FACT denies: 28, 29, 30, 31, 44 (`facts.def`'s deny
  column). That makes the 12 start-family bits the deny arms sweep (§3.3).
- No bit is renumbered (§3.7).

### 2.3 Does the table reproduce today's choice on every route?

By construction, before any measurement:

1. Every row's predicate IS today's function (pointer identity, not a re-spelling).
   The two exceptions are mechanical, and each has a sabotage witness that already
   exists:
   - the reseed tags become five two-line functions (S441 plants the `anchored`
     arm);
   - `attempt_cand`'s boolean becomes N12's predicate, with its `CandSet` output
     carried in `CandSel` as `pf_dfa_start_set`'s `t` is today. S81 and S82
     plant it.
2. Within each slot, the rows keep today's relative order. Today's arrays are
   per-question already, so a slot's rows ARE one of today's arrays, or (NEXT) one
   array plus a row on a route no existing row serves. BOUND, WINDOW and WIDTH
   were if/else chains, and their order is the chain's.
3. Routes are disjoint where they need to be. N12 is ATTEMPT-only, and ATTEMPT
   never consulted `dfa_pfs[]` (`dfa_cand_scan`'s branch `:7039`,
   `dfa_prefilter_name`'s branch `:10402`, `pcrec_dfa_scan_state_written`'s
   UNANCH test), so adding the ATTEMPT route cannot move an UNANCH selection, and
   vice versa.
4. Every body site asks the same (slot, route) at the same point (§1.3). So the
   set of predicates EVALUATED, and their order, is today's, which is what keeps
   `RX_FINDINGS` and the facts `used` column still.

Per route, then:
- **DFA unanchored:** W, P, F, N, S.
- **DFA attempt:** W, P, F, B, N (N12), S (S2).
- **pinned:** S1 on the DFA route.
- **VM-only:** W, P, H, N (N7/N13), B.
- **Hybrid:** W, P, H, F on the VM entry; N/S on the inlined DFA body; R and B
  in the VM loop.
- **utf8:** no slot reads the encoding. Rows read facts whose derivations do
  (`end_window`'s decline, `start_set`'s `start_cls` assertion, the
  `req_byte` prior gate), and those are not touched.

The sweep (§3.3) is then the measurement that this argument has no hole.

### 2.4 Where today's sites disagree

The census found three. **None changes an answer.** A no-mover refactor preserves
each; each fix is its own ruled change.

- **D-1. One token, two mechanisms.**
  - **What:** `RX_DFA_PREFILTER "memchr"` means "a `memchr` for the byte a match
    BEGINS with" on ENG_UNANCH (N9, offset 0). On ENG_ATTEMPT it means "a
    `memchr` for the byte BEFORE a candidate" (N12, offset −1:
    `(?m)^ERROR`'s newline).
  - **Population:** 33 ATTEMPT artifacts in auto/byte, inside N9's stamped 808
    (`row_census.txt`, `ATTEMPT:DFA_PREFILTER`).
  - **What disambiguates it:** `RX_DFA_SCAN`. The spec says so.
  - **Who is fooled:** G1 (`dfa_cand_scan` `:7044`) reads N12's byte as "the
    byte scanned", and `req_byte_dominated_by`'s density compare then prices a
    predecessor-byte scan as if it were a start-byte scan. No answer moves (an
    elided pre-check is an optimization). But the dominance argument ("the scan
    already tests the byte the pre-check would") is about a different byte
    position.
  - **Refactor:** keeps the token (N12's `stamp` projection) and the G1 read.
  - **Fix:** a separate change, either G1 declining `EXACTPRED` rows (a `map`
    read) or a stamp value `pred-memchr`. That is an abi event + spec hunk.
    Recommend the first: it moves only the 33 artifacts' pre-check emission, and
    only where it was elided. §6 Q4.
- **D-2. `RX_DFA_START "reverse-pass"` on artifacts with no reverse machine.**
  - **What:** `dfa_search_starts[]`' fallback stamps every non-pinned DFA scan,
    including the 388 ENG_ATTEMPT and the 64 empty-engine artifacts.
    `(?m)^ERROR`'s artifact carries no reverse table and stamps
    `"reverse-pass"`.
  - **The spec:** `docs/spec/match_api.md:4686-4703` documents the value as "the
    artifact carries its reverse machine and walks it backwards", then lists
    "whose scan is `attempt` or `empty`" among its population. The two sentences
    contradict each other.
  - **Refactor:** keeps the token (S2 routes DFA|ATTEMPT).
  - **Fix:** a third value (`attempt-start`) on ATTEMPT/empty. That is an abi
    event and a stamp-vocabulary change (D80 spec hunk, readers by grep). §6 Q5.
- **D-2b. Two derivations of "one start position", disagreeing on one pattern.**
  - **The two derivations:** the ATTEMPT route reads the MACHINE (B1/B2:
    `dfa_interior_dead`). The VM route, G2's VM arm and `RETRY`'s `anchored` row
    read the AST FACT `start_anchor`.
  - **The census** (`anchor_agree.txt`, 388 ATTEMPT artifacts, byte): 293
    agree on `bot`, 20 agree on `gstart` and 74 agree on unanchored. One
    disagrees: `(?(DEFINE)(?<g>\Ga))(?&g)`, where the machine proves `gstart`
    and the fact says unanchored. The fact does not see through the call.
  - **Direction:** this is the direction `emit_dfa.c:9358-9372` calls
    "welcome": a tighter bound on the DFA, a looser one on the VM. It is
    correct either way, and only the VM runs extra attempts that fail.
  - **Refactor:** keeps route-specific predicates (B1/B2 vs B3/B4) and the
    one-way assertion `:9374-9382`.
  - **Fix:** teaching `start_anchor` to see through a non-recursive call is a
    FACT change. It is a mover on the VM route and its own ruling. §6 Q6.
- **D-3. The listing's own text has drifted from the row.**
  - **What:** `--list-axes`' `first-memchr-bounded` row still reads "T = S & E*
    (E* every seed state's escape set; T == S)" (`src/dump/axes_dump.c:106`).
    D148 addendum 3 retracted `S & E*`, and the code reads `T = S`
    (`pf_dfa_start_set` `:6648`).
  - **Cause:** the text lives in a hand table in another file from the row.
    `req_admits[]` and `pcrec_reseed_rows[]` carry theirs beside the row.
  - **Refactor:** moves every `desc` beside its row VERBATIM, the stale text
    included, so stream 5 stays identical.
  - **Fix:** the declared listing commit C7 (§3.2) corrects it.

Not disagreements, but recorded because a reader will ask:
- The K73 offset-0 seek moves `search_from` on the DFA body and
  `attempt_position` on the VM (by design: `\G` reads `search_from`).
- The VM entry clamps before calling the hybrid's prefilter, which itself does
  not (by design: one clamp per search).
- The handoff is declined on VM-only artifacts even where the VM hat seeks
  (`where_to_start.md` §1.3 item 1: computed and thrown away). That is a missing
  row, not a disagreement, and §4.1's `handoff-rev`/VM-first socket is where it
  is served.

### 2.5 What is NOT in the table, and why

Every site below touches "where a match begins". Each stays outside because it
answers a different question:

- **The position domain.** The startpos guard (`-fstartpos-guard`, 3 rows), the
  UTF check (`-futf-check`), K73's offset-0 rule (`pcrec_emit_start_zero`, 7
  call sites in 3 spellings), K50's attempt-loop boundary guard (`:9452`) and
  K49's retry advance (`pcrec_enc_advance`, `emit_vm.c:13270`). These define
  which positions are LEGAL candidates under the encoding and the caller
  contract. They are the encoding backend's text and apply to every row's
  output. They are not alternatives to any row, and no row may move them. They
  stay a fixed layer under the table. Their selections (`startpos-guard`,
  `utf-check`) are caller-contract axes with their own first-match rows in the
  listing.
- **The machine's start STATE.** `dfa_seeds[]` (`seeded`/`constant`) decides how
  an attempt's state is computed at a candidate, which is the verifier, not the
  candidate. The DFA hat's re-seed READS it (`pf_emit_moved_reseed`) and does
  not choose it.
- **The match-here entry** (`dfa_matches[]`, `unwrapped`/`search-filter`): the
  caller supplies the start, so there is nothing to find.
- **Scan edges and stay skips** (`dfa_edges[]`, `dir_fwd_skip`): skips INSIDE an
  attempt's walk, past bytes that keep a non-start state where it is. They read
  no start landmark.
- **Engine selection and prefilter admission** (`select_engine.c`'s `analyses[]`,
  `fit.prefilter` `:862`, `prefilter-lang`, `fit_rungs[]`): these decide which
  ROUTE an artifact is, and the table reads the route. §5.4 argues they stay
  separate tables.

---

## 3. The no-mover refactor plan

### 3.1 Principles

- **Implement, then replace** (memory `pcrec-general-mechanisms-not-special-cases`:
  "implement-then-replace is fine"). The new array and walk exist beside the old
  ones, and readers switch slot by slot.
- **Functions stay; tables and walks move.** Every predicate and every emitter
  function keeps its name, its file and its body text. What changes is the five
  arrays, the inline `if` chains that become rows, `dfa_select`/`vm_plan_reseed`'s
  loop, and each reader's call. This is what keeps 47 of 53 sabotage anchors in
  place (§3.5) and every memfn manifest emitter name valid (C17 reads functions by
  name, `tests/memfn/site_manifest.tsv`).
- **D148 Q2's rename rides the NEXT-slot commit** (C3): `DfaPf` → `CandRow`'s
  `u.pf`, `DfaSel` → `CandSel`, `dfa_pfs[]` → `cand_rows[]`. It is the commit
  D151 Q5 scheduled, widened. D151 Q5 said "until `handoff-rev` exists". Frank's
  2026-10-06 direction moves the fold ahead of that row (§6 Q1).
- **Every commit is a no-mover with no abi event**: abi stays 64, and no spec
  sentence about an artifact moves. The one exception is C7, a declared
  stream-5-only change.

### 3.2 The commit sequence

| commit | what | what moves |
|---|---|---|
| C0 | **instrument** (no `src/`): `emit_sweep.py` gains `--extra ARG` (repeatable, appended to streams 1-4 on both sides) and a sixth stream `--emit-facts` (streams 1/2's patterns, identity required); this note's three census scripts move to `tests/` or stay here (Q7) | nothing in `src/` |
| C1 | **selection trace** under `-DPCREC_CAND_TRACE` (a compile-time knob, `OPTK_DEBUG`'s precedent `emit_dfa.c:4320`; scratch builds only): every one of the 10 decision sites (5 walks, 5 inline) prints `slot route row` to stderr. Reference traces are recorded at C1 over corpus × {auto, vm} × {byte, utf8} × {default, each start-family deny} | nothing in the default build (`#ifdef` text only: no emitted byte, no listing byte) |
| C2 | **implement**: `CandRow`, `CandSlot`, `CandSel` (`DfaSel` + `vm`, typedef'd to the old name), `cand_select`, and `cand_rows[]` holding all 37 rows with today's predicates. No reader switched. Under `PCREC_CAND_TRACE` each old walk ALSO runs `cand_select` and aborts on a different row (a both-walks oracle for C3-C5) | nothing |
| C3 | **replace NEXT + RECOVER**: `dfa_pf_of`, `vm_start_row`, `pf_scan_set_of`'s callers, `pcrec_dfa_scan_state_written`, `dfa_form_derive`, `dfa_search_start_of` and N12's four `attempt_cand` readers read `cand_select`; `dfa_pfs[]`/`dfa_search_starts[]` deleted; D148 Q2's rename; `run_cand_rows.sh` re-aimed (§3.5) | sabotage anchors S283, S284 (re-aimed into `cand_rows[]`) |
| C4 | **replace PRESENCE + FIRST**: `req_admit`/`req_use` read `cand_select`; `req_admits[]`/`req_uses[]` deleted; `pcrec_req_admit_row`/`pcrec_req_use_row` become projections of `cand_rows[]` | S462, S473 |
| C5 | **replace RETRY + BOUND + WINDOW + WIDTH**: `vm_plan_reseed`'s loop → `cand_select`; the `VRS_P_*` tag and `vm_reseed_holds` deleted; the three inline bound strings, the end-window `if` and the root-minw `if` read their slot's row | S372, S441 |
| C6 | **the listing reads the table**: `axes_dump.c`'s `prefilter`, `match`, `search-start`, `req-admit`, `req-use`, `hyb-reseed`, `vm-anchor-bound`, `end-window` sections project `cand_rows[]` by `axis`, printing today's `kind`, order and `desc` text byte for byte; `AXIS_DESC`'s start rows deleted (their text now lives on the rows) | nothing (stream 5 identical) |
| C7 | **declared listing commit, stream 5 only, NOT an abi event**: D-3's stale desc corrected; `kind` becomes `list` for the five start axes that ARE lists now; spec hunk in `docs/spec/registry.md`; `tests/registry/` pins re-read | `--list-axes` text only |

C3-C5 can be one commit if the panel prefers fewer, larger diffs. The split exists
so each re-aimed sabotage row is verified in the commit that moves it.

### 3.3 How each commit proves 0 movers

Every commit C2-C6 runs, against its parent (`--ref HEAD~1`, both sides built by
the script from `git archive`):

1. **`emit_sweep.py`, all five streams, `--features all`**, at default: streams 1
   (`.c`, auto), 2 (`.c`, `--engine=vm`), 3 (`--emit-ir`), 4 (composition over
   every `.rxt`/`.rxtin`), 5 (the seven `--list-*` dumps). Identity required on
   all five, reach at the script's pinned floors.
2. **The same with `--extra -e --extra utf8`** (C0's arm). Today's streams 1-3
   never pass an encoding (`scripts/emit_sweep.py:429-450`), so without C0 the
   utf8 half of every row (`a/u` above: 71 `offset-set-bounded`, 280 handoffs)
   is unswept.
3. **The `--emit-facts` stream** (C0). The facts listing's `used` column is the
   one observable of WHICH predicates a walk evaluated, beyond `RX_FINDINGS`.
   A walk that reorders or eagerly evaluates moves it and moves no `.c` byte
   on any artifact whose byte rate was already asked.
4. **The deny arms**, at C3, C4, C5 only (the commits that rewrite deny
   filtering): streams 1-2 with `--extra -fno-<flag>` for each of the 12 bits
   in §2.2. Each arm also runs at `-e utf8` for bits 16, 32, 46 and 47, whose
   populations differ most by encoding. That is 16 sweep arms per commit. Each
   arm is ~2 × 3,600 compiles, inside the per-change alpha tier's budget (D144
   addendum 3). They run serially and in the background, one heavy run at a time
   (memory `pcrec-box-concurrency`).
5. **The selection trace** (C1's build) diffed against the C1 reference over the
   same arms. It is stronger than bytes: it sees a row change between two rows
   whose emitted text coincides (`run-pinned` vs `offset-set` on a model that
   already tests the run: identical bytes, different rows). It is cheaper, so it
   covers every deny arm at both encodings, all 12 bits × 2 encodings × 2
   engines.
6. `make test-codegen`, the registry suite, `run_cand_rows.sh`, the memfn
   manifest check (C17), and mech on every re-aimed row (§3.5). The full
   `make test` is the manager's at merge.

**The controls and what they share.** The reference side of every comparison is
the PARENT commit's binary, built from `git archive`, so it shares no source with
the change under test (learnings §3). The C1 trace is produced by the OLD walks
and is then the reference the NEW walk must reproduce. The C2 both-walks oracle
is the same reference evaluated in-process. Neither reads `cand_rows[]` to decide
what `cand_rows[]` should say.

### 3.4 Rows the corpus cannot prove

A byte sweep proves a row only where the corpus selects it. From `row_census.txt`:

- **`set-leads` (P4)** is invisible to every stamp: it stamps `"emitted"`. The
  C1 trace shows it, and its witness cells are `run_prechecks.sh` §5.11's
  (S460, S457, S458).
- **`fixed` (R6)** has population 0 at default. It is reached only under
  `-fno-hyb-reseed` (deny arm 4 above).
- **`run-pinned-bounded`** is 0 under utf8, and `window` (W1) is 0 under utf8
  by the fact's own decline. Those arms prove nothing about W1 and N1, and the
  byte arm carries them.
- **Small populations, each needing its named witness rather than a count:**
  - `ceiling` (H1): 6, `tests/mrl/` + `^((?1)a)$`;
  - `gstart` (B4): 5 auto / 20 vm, `tests/assertions/` `\G` blocks;
  - `adaptive-dense` (R4): 13, `docs/dev/reseed/`'s cells;
  - count-collapsed hybrids: 1-2, K39's witness.

C2 adds, under `PCREC_CAND_TRACE`, a per-row hit counter that `row_census.py`
cross-checks against these stamp counts. A row whose counter reads 0 across all
arms is listed in the commit's report as UNPROVEN-BY-SWEEP and needs its
constructed witness run explicitly (the [MECH-REACH] shape).

### 3.5 Gates and sabotage rows that must be re-aimed

`start_table/sabotage_anchors.py` maps every sabotage row whose `SAB_FILE` is
`emit_dfa.c` or `emit_vm.c` to the function its `SAB_BEFORE` text sits in (207
rows; `sabotage_anchors.tsv`). 53 are in start-family code. (The script's 60
FAMILY marks include 7 rows that sit in the three search-body functions but plant
non-start text: S07, S36, S85, S144, S181, S400 and S430.)

- **6 sit inside a table literal or a walk that the refactor deletes, so they
  MUST be re-aimed** in the commit that deletes their site, with intent
  re-verified (BOILERPLATE: "a re-anchor needs its intent re-verified"):
  - S283 and S284 in `dfa_pfs[]` (the run rows' deny bit and `reseeds`);
  - S462 in `req_admits[]` (`set-leads`' deny);
  - S473 in `req_uses[]` (`handoff`'s deny);
  - S372 in `vm_plan_reseed` (the calibration swap);
  - S441 in `vm_reseed_holds` (the `anchored` tag).

  In `cand_rows[]` each plants the same edit on the same row.
- **47 sit in predicate or emitter bodies the plan keeps byte-stable**, so their
  `SAB_BEFORE` text still matches:
  - 6 `pf_dfa_start_set`, 4 `pf_vm_start_applies`, 4 `req_byte_dominated_by`,
    4 `emit_req_handoff`;
  - 3 `start_pinned_applies`, 3 `req_route_one_attempt`, 2 each in the run,
    set-leads and handoff predicates;
  - the 8 in `vm_emit_search_body`: S63, S88, S141, S169, S263, S370, S371,
    S469;
  - 4 in `emit_unanchored`/`emit_attempt` (S82, S221, S223, S235);
  - S81, S264, S460, S475, S479, S490.

  They are RE-RUN, not re-aimed. A row whose site the refactor reroutes (e.g.
  S263's `attempt_max` string now comes from `u.bound`) moves its anchor into
  `cand_rows[]` IF the string literal moves there. The plan keeps each emitted
  literal in the body function and puts a POINTER to it in the row only where
  the literal is shared (none today).
- **Two rows name the old identifiers in comments or probes**: S490 (`dfa_pfs[]`
  in its header) and S495 (`cand_ppm reads a row name`). Their text follows the
  rename. S495's REACH probe must still find a name read.
- **Structural checks that parse the source:**
  - `tests/codegen/cand_rows_check.py` reads `static const DfaPf dfa_pfs[] = {`
    literally (`:130`) and every `DfaSel NAME = {` initializer (`:174`). It is
    re-aimed at `static const CandRow cand_rows[] = {` and `CandSel`.
  - It gains four checks: every (slot, route) pair a body asks ends in a
    `cand_always` row; no row's `u` member mismatches its slot; no comparison
    reads ANY `cand_rows[]` row name (K84's check widened to every start row,
    which is K89's fix shape applied to this family); and every `CandSel`
    initializer names `.slot` and `.route`.
  - `tests/registry/axes_registry_check.sh` and `run_registry_tests.sh` read
    `pcrec_reseed_rows` by name in comments only. At C6 the projection keeps
    `pcrec_reseed_rows`/`pcrec_reseed_nrows` as accessors until C7.
- **Identity gates** (`tests/codegen/run_*_identity.sh`, 11 of them) compare
  emitted artifacts across arms. No emitted byte moves, so none of their pins
  moves. They run unchanged as part of `make test-codegen`.
- **The memfn site manifest (C17).**
  - Its emitter and companion names are all function names the plan keeps:
    `pf_emit_find`, `pf_vm_emit_first_class`, `pcrec_emit_req_byte_check`,
    `emit_req_set_rest`, `emit_attempt` (MLINE).
  - C17_ROW_FLOOR does not move, because no site is added.
  - The row `scan` column (§1.1) names the manifest id, and C17 gains a
    cross-check: every `cand_rows[]` row whose `scan` is a manifest id names an
    id that exists in the manifest.

### 3.6 Stamps whose vocabularies stay byte-identical

Every value set below is untouched through C6. A row's `stamp` projection names
today's token, including where §2.4 says the token is ambiguous:

| stamp | rows that project into it | `rx_info` mirror |
|---|---|---|
| `<PREFIX>_DFA_PREFILTER` | N1-N6, N8-N13 (N12 as `"memchr"`) | `rx_info.prefilter` |
| `<PREFIX>_DFA_PREFILTER_OFFSETS` | N1-N4's offset list | — |
| `<PREFIX>_VM_START_SCAN` | N7, N13 on route VM | — |
| `<PREFIX>_REQ_WHY` | P1-P5 (`req_why_name`: P4 → `"emitted"`) | — |
| `<PREFIX>_REQ_HANDOFF` | F1 (the decimal K), F2 (`"none"`) | — |
| `<PREFIX>_VM_RESEED` | R1-R6 | — |
| `<PREFIX>_VM_START` | B3, B4, B5 (route VM) | — |
| `<PREFIX>_DFA_START` | S1, S2 | `rx_info.search_form` |
| `<PREFIX>_END_WINDOW` | W1 (the bound), W2 (`"none"`) | — |
| `<PREFIX>_REQ_BYTE`, `_REQ_RUN` | facts, not rows (read by P/F) | — |

The fact-valued stamps keep `pcrec_fact_stamp`'s spelling (`facts.c`).

### 3.7 Deny flags and the axes

- **No bit is renumbered or reassigned.** Row denies stay on their rows: 16, 32,
  45, 46, 47, 22 and 37.
- **FACT denies stay on their facts** (`facts.def`): 28 `start_anchor`, 29
  `end_window`, 30/31/44 the `req_*` facts. That split is
  `patfacts/design.md` §7.1's, and it is load-bearing:
  - `-fno-vm-anchor-bound` empties the FACT, so it also turns off G2's VM arm
    (P2), the VM hat's anchoring conjunct (N7) and RETRY's `anchored` row (R3),
    not only the BOUND rows.
  - A refactor that moved bit 28 onto rows B3/B4 would change those three other
    readers. The deny arms (§3.3 item 4) are exactly what would catch it.
  - The listing keeps showing bit 28 on `vm-anchor-bound`'s rows, as a
    projection.
- **Two rows carry two bits** (N1/N2, `16|32`). `cand_select`'s test is
  `deny & flags`, unchanged, so either bit removes the pair.
- **`test-axes`** enumerates its arms from `--list-axes` (deny and force macros
  and CLI flags). Through C6 that surface is byte-identical, so the axis sweep's
  arm set does not move. At C7 only `kind` and one `desc` change, and no flag
  appears or disappears.
- **No new deny or force flag.** D148 Q3's "deny only" is kept for the new rows
  too (§4).

---

## 4. The new-row sockets

Each is its own abi event AFTER C7, with its own movers census, spec hunk and
sabotage rows. Nothing below is built by the refactor.

### 4.1 The reverse-walk row (D151; [ENG-TACTICS] re-scoped)

- **Slot NEXT, two rows**, bounded first (`where_to_start.md` §1.4's order):
  - `rev-inner-bounded` (DFA, `views`);
  - `rev-inner` (routes DFA and VM; D124's two hats).

  They go after N11 and before N13. An offset-0 row that applies is already
  scanning a start; the new row beats it only through its admission (G3, F = 2×
  labelled UNMEASURED per D151 Q6). On the VM route they go after N7.
- **Predicate:** G1 ∧ G2 ∧ G3, each conjunct a separate line with its sabotage
  row from `where_to_start.md` §2.6's mutation table.
- **Mapping:** `EXACTREV`. **Give-up:** `ONE_WAY` (D151 Q4). **Hat:** DFA:
  the anchored forward machine from `s*` (`anchored_match_unwrapped.md`'s
  entry). VM: one anchored attempt.
- **Slot FIRST, one row** `handoff-rev`, before F1: the candidate loop's
  give-up hands the current `s*` to the unanchored scan as its startpos
  (`where_to_start.md` §2.7's measured `fallback`). It is the FIRST slot's
  second LOWER-BOUND row, and with it in place §2.4's VM-only "computed and
  thrown away" gap has its row.
- **New fact:** `inner_split` (`facts.def`, E2, `PF_CORE`, owner
  `src/facts/split.c`): the spine index of the chosen landmark, `P`'s byte
  width `[a, b]`, and the G1/G2 bits. G2's alphabet is a new byte-set union over
  `P`'s consuming nodes, not `first_of`. The census's stand-in reader parses only
  85% / 73%, and D151 names that as the revisit trigger.
- **New machinery:** a PREFIX reverse machine, `pcrec_build_nfa` over `P`'s
  sub-tree, reverse and exact. It is the third reverse machine: [OPT-REVEND]'s
  is the whole pattern seeded at `n`, and the shipped reverse pass is the whole
  pattern seeded at the end. Build it once as a parameter of the existing
  builder, never a second builder (`where_to_start.md` §1.3 item 4).
- **memfn:**
  - The landmark scan is a `FIND` over one literal or run, the PRE/OFS kernel
    the kit already plans to own. No new vocabulary.
  - The reverse walk itself is a DFA step loop, which §8.5 marks "never
    delegated" (T8).
  - The verify chain's `VERIFY` of `L` at the hit is VERIFY's existing site.
  - Request one item: a FIND whose handoff RETURNS each hit and resumes at
    `hit + 1` (self-overlap, `where_to_start.md` §2.1). Today's sites resume at
    `hit + |L|` or return once.
- **Gate:** D151 item 2, the `dup-param-detect` hand twin winning the VM cell,
  and the 10.46 re-run of the soundness model.

### 4.2 [ARTREV] I5: the VM word-start filter

- **Not a new row: a CONTEXT COLUMN on N7** (`first-class`, VM route), which
  `generalize.md` I5 §4 already places "on the same table, its own row,
  sequenced after stage 3".
- **The column:** `ctx`, a predicate on the PREVIOUS byte (`\b` at the
  pattern's start: previous ∉ `\w`). The seek then tests the pair
  (`prev`, `cur`) instead of `cur` alone. Row N7's predicate is unchanged.
- **Why a column and not a row:** the population (bench 2, corpus 1) is a
  subset of N7's, and the same row with a narrower test is the general form. A
  separate `first-class-ctx` row would be a second VM-hat row, the parallel
  special case.
- **New fact:** `start_ctx` (E2, `PF_CORE`): the leading context assertion as a
  previous-byte set, or `none`. It is the zero-width information `start_set`
  erases by design (`startset.md` §3.2). It is the VM analogue of the DFA hat's
  re-seed, which reads the same context off the machine.
- **memfn:** a FIND over a TWO-POSITION predicate (`prev ∈ A ∧ cur ∈ B`), which
  is not in the vocabulary today. It is a kit request (the PF site's predicate
  widened), and the kit decides its form.
- **Give-up:** `NEUTRAL` per `generalize.md` I5 §5 (skipped attempts fail at
  their first instruction, before any charge). The row's posture stays
  `ONE_WAY` because the column narrows the same row.
- **The L5 restart** (skip past a failed attempt's dead span) is a separate
  RETRY-slot question and is not part of I5's column.

### 4.3 K90 (and K88): dense starts

- **Two shapes, two slots, no new mechanism.**
  - **K90 L3 / K88 (a hit at the first position):** a peel, "test the current
    position before the first seek". This is a property of the SEEK, i.e. of
    the row's emission, not a new row. N7's `u.pf.emit_vm` and F1's
    `emit_req_handoff` each gain the peel under one shared helper. The two
    witnesses are the same shape (K90: "same family as K88").
  - **K90 L1/L2 (a dense subject):** this is EXACTLY the RETRY slot's question,
    "after a failed attempt, step or re-seek?". Today that slot serves the
    hybrid (re-call the prefilter). The fix is to give R4/R5 (`adaptive-dense`,
    `adaptive`) the VM-only route, where "re-seed" means "re-seek with the
    VM hat" and "step" means K49's advance alone.
- **The general answer is the existing one:** the gap-armed block rule and its
  calibration rows (`vm_reseed_cal`, frameless/framed) already measure exactly
  this crossover for the hybrid. K90 then adds no mechanism, only a route bit on
  two rows plus a predicate conjunct for the VM-only route (the hat selected
  N7).
- **Owed:** the calibration's regime does not transfer automatically. A seek is
  cheaper than a prefilter call, so the `gap` crossover is re-measured for the
  VM-only route (D149: labelled UNMEASURED until it is). The alpha is K90's
  three cells.
- **Give-up:** `ONE_WAY` already (R4/R5's contract).
- **memfn:** none new.

### 4.4 Where else the table reaches (filed, not designed)

- **[OPT-REVEND]** is a WINDOW-slot row (`EXACTREV` from the subject end). It
  sits before W1, because an exact start beats a window. It shares §4.1's
  reverse builder.
- **[OPT-A]** is NEXT rows with a multi-literal landmark.
- **[OPT-VMSEED] stage 4** (D148 add. 2 Q-R4: filed, not planned) is a FIRST
  slot row on the VM route.

---

## 5. Standing questions and siblings

### 5.1 The measurement regime: RELEVANT, briefly

The refactor measures no time and claims no speed: it is answer- and
byte-identical by requirement. The populations in §2.2 are compile-time
COUNTS, regime-free, read from this lane's build of `74379fe0` on the Mac. They
are corpus counts, not bench counts, so a different corpus moves them and moves
no decision. The new rows of §4 each carry their own regime question:
- §4.1's F (2×, UNMEASURED);
- §4.3's `gap` crossover, re-measured on the VM-only route, which is exactly
  the case where a hybrid-measured number would flip a decision if carried
  over.

### 5.2 The independent control: RELEVANT

See §3.3's "what they share". In addition:
- The census reads STAMPS, never `src/`. Its population is `emit_sweep`'s own
  `enumerate_corpus`, so the census and the gate count the same population.
  That is shared on purpose: it is the population, not the expectation.
- The disagreement probe (`anchor_agree.py`) compares two derivations that
  share no code (the machine's `dfa_interior_dead` vs `src/facts/startanch.c`).
- Witness reach: §3.4's UNPROVEN-BY-SWEEP list is the [MECH-REACH] answer, and
  the re-aimed rows are re-run with their REACH probes.

### 5.3 What moves when data is regenerated: RELEVANT, nothing for the refactor

The refactor regenerates nothing. Through C6 no emitted byte, no stamp, no pin
and no listing byte moves, and no abi event occurs. C7 moves `--list-axes` text
only: a registry-surface change with a `docs/spec/registry.md` hunk, read by
`tests/registry/` (the format readers are found by grep, the `NF != 15`
lesson of `registry_built_status_memo.md`). C7 adds no column, so no
field-count reader moves.

The new rows (§4) are abi events. Two data dependencies arrive with them:
- G3 reads the byte-rate prior, so a regenerated `default_ppm.tsv` moves
  `rev-inner` admissions. That is the same exposure [OPT-REQBYTE] has today.
- K90's re-measured `gap` is a calibration row; changing it moves the adaptive
  text's literals, which `tests/codegen`'s calibration check reads back.

### 5.4 SIBLING-OF-A-FAMILY: which decision families touch the start table

The start table is one member of a family of first-match decisions about a
search. Each sibling below is weighed against the lens "one table per
question" (D124).

| sibling | the question | how it touches the start table | keep separate? |
|---|---|---|---|
| ENGINE selection (`select_engine.c` `analyses[]`, `engine-route`) | which execution core runs the match | it decides the ROUTE (`CR_DFA`/`CR_ATTEMPT`/`CR_VM`), which the table reads as a column | **Yes.** It answers a different question with a different contract (D124 item 3: the cores stay distinct). Its input is the AST and build outcomes, not landmarks |
| PREFILTER admission (`fit.prefilter`, `select_engine.c:862`; `prefilter-lang`; `fit_rungs[]`) | does a VM get a DFA in front, and which language | makes the VM route a hybrid: N on the inlined body, RETRY on the VM side. FIRST's handoff reads it (`pcrec_artifact_has_dfa_scan`) | **Yes, for now.** It is a build-time selection with a retry ladder (`compile_driver`'s one recovery point). Folding it in would put a build outcome into a row predicate. **But** it should become a first-match table itself: it is the one family member still a ternary (`:862`). Filed, §6 Q8 |
| REQ pre-check admission (`req_admits[]`) | — | this note FOLDS it in as PRESENCE, because "no landmark → no candidate" IS a start mapping, and G1 reads NEXT's choice. Keeping it separate would leave a cross-table read as today | **No: folded** |
| The req FACTS (`req_byte`, `req_run`, `req_run_fold`'s pick) | what is necessary | the landmark column; facts, not rows | **Yes**: facts layer (D120) |
| Position domain (startpos guard, UTF check, K73, K50, K49) | which positions are legal | applies to every row's output | **Yes**: §2.5 |
| Machine-form axes (repr, view, seed, accept, scan edge, scan body, match) | how the verifier is emitted | the re-seed rows read `seed` | **Yes**: they answer "how does a candidate get verified" |
| memfn's `DELEG_SITES` and the SIMD switch | how a delegated scan is spelled | the `scan` column names the site | **Yes**: the kit owns the inside of a site (D146) |

**The forest-for-the-trees check:**
- Every sibling that answers WHERE a match may begin is folded.
- Every sibling that answers WHO runs it, WHETHER a prefilter exists, or HOW a
  scan or verify is spelled stays its own table, and reaches this table as a
  route bit, a fact or a site id.
- The one family member that is not yet a first-match table (prefilter
  admission) is filed (§6 Q8), not folded.

---

## 6. Open questions for Frank

- **Q1. Fold now, ahead of `handoff-rev`?** D151 Q5 ruled "two tables stay
  until the `handoff-rev` row exists", and your 2026-10-06 direction puts the
  no-mover fold first. **Recommend YES, as a D151 addendum:** the fold is what
  makes `handoff-rev` (and every §4 row) a one-row addition, and doing it as a
  no-mover now is cheaper than doing it inside a mover later.
- **Q2. One array with a slot column, or one array per slot sharing the row
  type and walk?** **Recommend ONE array.** It is the literal "single table",
  the slot DAG (§1.3) and the cross-slot reads are visible in one place, one
  listing projection walks it, and the `routes` precedent already filters one
  list two ways. Per-slot arrays would keep eight tables with a shared type,
  which is today's structure renamed.
- **Q3. A compile-time selection trace (`-DPCREC_CAND_TRACE`) in `src/`?**
  It is the strongest and cheapest no-mover control (§3.3 item 5) and costs no
  default-build byte. **Recommend YES**, scoped to the refactor's life plus a
  permanent home as the per-row hit counter (§3.4). It is a debug knob, not an
  axis, on `OPTK_DEBUG`'s precedent.
- **Q4. D-1 (the ATTEMPT `memchr` read as a start byte by G1)?** **Recommend:**
  after C7, G1 declines `EXACTPRED` rows (a read of the `map` field; it moves
  only the 33 ATTEMPT artifacts' pre-check emission). Keep the stamp token.
- **Q5. D-2 (`DFA_START "reverse-pass"` on attempt/empty artifacts)?**
  **Recommend** a third value `attempt-start` for ATTEMPT and empty, as its own
  abi event with the spec hunk correcting `match_api.md:4686-4703`'s
  contradiction. It is low priority: no consumer is known to be misled. The
  alternative is a spec-only fix stating that the value means "not pinned".
- **Q6. D-2b (`start_anchor` blind through a non-recursive call)?**
  **Recommend: file, don't fix.** Population 1 (`(?(DEFINE)(?<g>\Ga))(?&g)`).
  The fact change is a VM-route mover with a correctness-neutral gain, so a D77
  trigger is needed.
- **Q7. Where do this note's three census scripts live after the refactor?**
  **Recommend:** `row_census.py` becomes the C2 hit-counter's cross-check under
  `tests/codegen/`, with its arms pinned as floors, D110's shape. The other two
  stay here as design evidence.
- **Q8. Prefilter admission as a first-match table?** It is the sibling still
  spelled as a ternary (`select_engine.c:862`). **Recommend: file as its own
  no-mover row**, not part of this refactor: its retry-ladder interaction is
  `compile_driver`'s, outside the start table.
- **Q9. Panel shape.** **Recommend a LIGHT D6 panel, two critics** (sound: §2.3
  and §3.7; checks: §3.3-§3.5). The refactor changes no answer and no byte, and
  the full bar applies to each §4 row when it lands.

---

## 7. The lenses

- **specific vs general:** general. Eight decision sites become one walk, and
  K90's fix becomes a route bit on existing rows rather than a new mechanism.
- **core vs derived:** the table is derived. It reads facts (core) and the route
  (engine selection), and owns no analysis.
- **applicable vs assumption-changing:** applicable. No contract changes: the
  give-up postures are written down, not altered.
- **fits the architecture vs refactor:** a refactor, by request, and a no-mover
  one. It completes D148 Q2's rename and D151 Q5's fold.
- **shared question / engine hat (D124):** this is D124 item 1 applied to its
  own example, "where can a match start", with the engine as a route column.
- **sibling of a family:** §5.4.
