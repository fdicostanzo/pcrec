# [FACT-READS] The consumer side of the pattern facts: inventory, implicit orderings, and a three-layer check sketch

**Status: PROPOSED rev 0 (lane factdeps, 2026-11-12). Inventory and design sketch only. Nothing is built
and there is no build go.** Proposed plan tag: `[FACT-READS]`. It is meant to be the foundation section
of the combined [COND-FAMILY] + [ENG-TDFA] plan, after the current sets (close-before-start).
Code cites are at main `8184f6fb6` (worktree `lane/factdeps`) unless a branch is named.

Owner's direction (Frank, 2026-11-12): "We should put some thought into formalizing these
dependencies ... If interdependency becomes a problem, we should think of how to describe it such that
it can be formally, and via a coded mechanism, be checked." And, on the direction: "You could check
when writing, then at compile time, then with trace."

## Goals

| # | goal | who benefits | measurable form |
|---|---|---|---|
| G1 | every fact read is declared by the code that reads it | reviewers; the [COND-FAMILY] builders, who add readers | the trace build's undeclared-read count over the corpus is 0, and a sabotage row that adds one undeclared ask turns it red |
| G2 | `--emit-facts`' `used` column comes from declarations, not control flow | users of the listing; lanes doing refactors | the 4 "ballast" asks of §3 are deleted with zero listing movers; deleting dead code moves no `used` cell |
| G3 | every value that crosses the kit seam has a declared domain, sentinels included | the kit (D157: facts, not methods) | every integer seam field names its domain; a pcrec sentinel never reaches a kit field whose domain lacks it (a checked refusal) |
| G4 | the orderings that soundness rests on are declared and checked | everyone touching the search entry or the attempt loop | each soundness ordering in §2 has a declaration and a check, or is listed as an open residual |
| G5 | the check extends `facts.def` and the existing selection tables; it adds no parallel mechanism | the owner (memory: general mechanisms, not special cases) | no new table whose rows duplicate an existing table's rows |

Priority on conflict: G4 > G1 > G3 > G2 > G5. Non-goals: no change to any fact's value; no new fact;
no change to the emitted search; no selection change.

## Standing questions (docs/design/CLAUDE.md)

1. **Measurement regime.** Not relevant. No timed quantity is read or produced. The one cost figure
   (trace-build overhead, §6) is a test-build compile cost, and it decides nothing about an artifact.
2. **The independent control.** RELEVANT, because §6 proposes three checks. Each one's control must
   not share a source with its subject (learnings §3). The trace layer checks the declaration (a table
   column) against the RUN (the accessor's own `pf_enter`). Those are two sources. The write-time lint
   checks the declaration against the code TEXT. That is a second source too, but it is blind to
   transitive asks (§6.1). The sabotage rows plant an undeclared ask in a predicate. They insert no
   name the check greps for, because the check reads the run, not a string. Population: the trace
   layer counts the readers it saw and the declared readers it never saw. An empty count reads as
   vacuous, not green (the REACH-line rule in `run_facts_checks.sh`).
3. **What moves when the data is regenerated.** RELEVANT. The new columns are generated tables.
   Adding a `reads` column to `cand_nodes[]` or to the fallback rows moves no emitted byte, so it is
   not an abi event. Re-sourcing `used` from declarations moves the `--emit-facts` listing only where
   a declaration differs from today's asks. That is a caller-observable change and needs its
   `docs/spec/facts_listing.md` §4.1¶2 hunk (D80). The step that re-sources the column must show zero
   movers first (§3.3), or declare each one. Seam domains (§4) that change a kit field's meaning are
   a kit ABI event (`MF_SITE_ABI`), filed as a request, never edited here.

---

## 0. The driver's stages, as they really run

One compile ATTEMPT, `compile_driver` in `src/core/compile.c`. The retry ladder re-runs the whole
attempt (§0.1). Stage names are this memo's. They are used in §1's `stage` column.

| stage | what runs (file:line) | seal |
|---|---|---|
| S0 resolve | `pcrec_parse_mods_init` :2738, encoding, `pcrec_memfn_target_derive` :2812, `pcrec_find_resolve` :2821, `pcrec_meas_resolve` :2826, memfn measures/analysis :2827-2833 | — |
| S1 parse + rewrites | parse hooks :2873, `pcrec_callout_sites` :2882, `pcrec_altcls` :2884, `pcrec_discharge_atomic` :2900, `pcrec_callgraph_build` :2919 | **E1** `pcrec_facts_seal_e1` :2929 (forces kinds, nullable, empty_admits, reports_empty) |
| S2 select | `pcrec_select_engine` :2956 (writes `Job.fit`), `pcrec_postresolve` :2974 | — |
| S3 lower | `pcrec_lower_enc` :3027 | **E2** `pcrec_facts_seal_e2` :3043 (re-derives E1, refuses on a move) |
| S4 machines | `pcrec_artifact_has_dfa_scan` :3064 gate; `pcrec_build_nfa` :3073; collapse decision :3120 (reads `kinds`) and rebuild :3191; ENG_UNANCH: `pcrec_nfa_wrap_unanchored` :3196 | **E3** `pcrec_facts_seal_e3` :3200, on ENG_UNANCH only |
| S4b scan edge, rev-end | reverse NFA :3202, min DFAs :3203-3206, `pcrec_scanedge_dfa` :3238 (first E3 ask through `pcrec_dfa_scan_state_written`), `revend_choose_form` :3246 | — |
| S5 machines final | `cx.job->machines_final = true` :3285; NEVER-MATCH gate :3300-3301 | (the "machine-final" point; not a `PfEpoch`) |
| S6 compound | `pcrec_compound_walk` :3362 | — |
| S7 emit | `pcrec_emit_vm` :3365 or `pcrec_emit_dfa` :3366: the start-table selection (`cand_rows[]`), the presence site to the kit, stamps | — |
| S8 measure + size ladder | `pcrec_emit_code_block` :3370, `pcrec_memfn_stamps_render` :3406, size measure + size-term ladder :3413-3585 | — |
| S9 listing | `pcrec_part_layout_render` :3669, **FORCE LOOP** `pcrec_facts_force_all` :3671 (only under `--emit-facts`), prefix render :3677 | — |

### 0.1 Between attempts

A failed attempt `longjmp`s to the one recovery point. The fallback ladder (`compile.c:1330-1500`, a
first-match row table with `.applies`, `.sets`, `.retries`) picks the next attempt's settings. It
writes cross-attempt flags into the next `Ctx` (`anchored_dropped`, `end_mark_dropped` and
`req_handoff_dropped`, :2456-2460). Their readers sit in later attempts' S4 and S7 (§1.3). The
force loop's own failure lands at :2601 (`pcrec_facts_force_failed`).

---

## 1. The consumers

`pass` = a public accessor (sets the `used` bit, `facts.c:144`). `stated` = a `_stated` accessor (no
`used` bit, Q-WR-12). `writes` = state the site leaves that another consumer reads. The emitter
sites are in `src/gen/emit_dfa.c` unless another file is named.

### 1.1 Declared reads: accessor calls (the complete list at `8184f6fb6`)

| site | function | stage | facts | kind | writes something another consumer reads? |
|---|---|---|---|---|---|
| `select_engine.c:141` | `forces_captures` | S2 | kinds | pass | yes: the engine mask feeds `Job.fit.chosen` |
| `select_engine.c:646`, `:673` | `pfa_nullable_exact` / `_collapsed` (rows of `pf_admits[]`) | S2 | empty_admits | pass | yes: the prefilter verdict in `Job.fit` |
| `select_engine.c:951` | `prefilter_decision` | S2 | kinds, empty_admits | pass | yes: `Job.fit` |
| `select_engine.c:1210` | `prefilter_decision` | S2 | empty_admits | pass, **BALLAST** (§3) | no |
| `compile.c:1053-1055` | `fit_collapse_can_help` (fallback ladder) | between attempts | kinds, nullable, empty_admits | pass | yes: the next attempt's collapse |
| `compile.c:1599` | `pflw_worth` (`pflw_rows[]`) | S4 | nullable | pass | yes: the prefilter-look-ahead cell |
| `compile.c:3120` | `compile_driver` | S4 | kinds | pass | **yes: rebuilds `Job.nfa`**, the machine E3 seals |
| `compile.c:573` | `revend_choose_form` | S4b | end_mark | pass | yes: `job->revend_form`, read by `drop-end-mark` (:1122) and `emit_rev_end` |
| `compile.c:3301` | NEVER-MATCH gate | S5 | never_matches | pass | yes: the engine (DFA) or a `--emit-ir` refusal |
| `internal.h:7519` | `pcrec_startgate_needed` | S7 | nullable | pass | no (the K50 gate's text) |
| `emit_dfa.c:966` | `pcrec_emit_end_window_clamp` | S7 | end_window | pass | no |
| `:1112`, `:1191`, `:1240` | `req_run_tests`, `emit_req_handoff_rest`, `req_note_run` | S7 | req_run, req_whole_run | pass | no |
| `:1496-1497` | `req_pres_spans` | S7 | req_set, req_whole_run | stated | **yes: the kit's presence spans** |
| `:1555-1619` | `req_site_define` | S7 | req_byte, req_run, req_whole_run, req_set | pass; `:1602-1603` **BALLAST** | **yes: the whole `mf_site`, `head_max` included (:1648)** |
| `:4810` | `unanch_start` | S7 (E3) | kset_walk | pass | yes: the window statement |
| `:4875` | `locate_rev_end_applies` (LOCATE row) | S7 | end_pin | pass | yes: the LOCATE row |
| `:6870-6871` | `pf_window_of` | S7 | req_run, run_pin | stated | yes: the window statement to the kit |
| `:7409` | `us_run_pin` | S7 (E3) | run_pin | pass (owes the kind gate) | yes: run rows |
| `:7419`, `:7464`, `:7534` | `pf_run_applies_common`, `ofs_test_of`, `ofs_test_verifies_run` | S7 | req_run | pass | yes: `OfsTest`, re-derived per ask |
| `:8182-8225`, `:9154`, `:9225`, `:12000`, `:13080` | `dfa_pf_of`, `dfa_pf_read`, `pf_scan_set_of`, `vm_start_row`, `req_scan_reentered`, `pcrec_dfa_scan_state_written`, `pcrec_cand_lmwalk_next_cf`, `dfa_form_derive` | S4b, S7 | start_set | pass | yes: NEXT's row; the scan state written (S4b) |
| `:8631-8633` | `req_byte_dominated_by` (G1) | S7 | req_run | pass | yes: PRESENCE |
| `:8652` | `req_none_applies` | S7 | req_byte, req_run | pass | no |
| `:8703-8704` | `req_set_leads_applies` | S7 | req_run, req_set | pass; `:8704` **BALLAST** | yes: the kit ask |
| `:8879`, `:9140` | `req_handoff_applies`, `pf_handoff_applies` | S7 | req_landmark_maxoff | pass | yes: FIRST/NEXT |
| `:8909`, `:8956`, `:9018` | `req_parts_in_whole`, `req_handoff_entry_applies`, `req_handoff_k` | S7 | req_whole_run, req_run, req_landmark_maxoff | pass | yes: **K, which becomes `head_max`** |
| `:9039-9044` | `req_landmark_hit_ppm` | S7 | req_run, req_byte | pass | no |
| `:9786`, `:10234`, `:13679` | `start_width_applies`, `cand_min_width`, `unanch_scan` | S7 (E3) | width | pass | yes: WIDTH, `DfaForm.minw` |
| `:9805`, `:9885` | `start_landing_applies`, `pcrec_dfa_landing_guard` | S7 (E3) | land_char | pass | yes |
| `:10220` | `cand_window_applies` (WINDOW row) | S7 | end_window | pass | yes |
| `:10294-10296` | `cand_bound_anchored_vm_applies`, `_gstart_` (BOUND rows) | S7 | start_anchor | pass | yes: BOUND, read by PRESENCE/FIRST/NEXT (slot graph) |
| `:11145-11409` | `req_set_leads_own`, `req_rest_own_sig`, `req_pick_shadow` | S7, trace build only | req_* | stated (one `req_landmark_maxoff` pass ask at :11355) | no (trace records) |
| `:12463` | `pcrec_cand_path_trace` | S7 | kinds | pass | no (trace) |
| `:13908`, `:13974`, `:14655` | `revend_ties`, `pcrec_revend_form_asked`, `emit_rev_end` | S4b, S7 | end_pin | pass | yes: FINISH's tie |
| `:15449-15454` | `emit_attempt` | S7 | start_anchor | pass | no (an internal-error assertion) |
| `:16237-16294` | `pcrec_emit_prologue` | S7 | end_window, req_byte, req_run (stamps) | pass via `pcrec_fact_stamp*` | no (stamps) |
| `emit_vm.c:13891` | `vm_emit_search_body` | S7 | start_anchor | pass | no (stamp text) |
| `emit_iter.c:31` | `retry_none_applies` | S7 | reports_empty | pass | no |
| `known.c:260` | `cc_exact` (the `cover` LOCATE row) | S7 (E3) | span_facts | stated | yes: LOCATE |
| `dump/facts_dump.c:182` | the listing | S9 | all (`pcrec_fact_render`: memo only, asks nothing) | — | no |

Count (a text scan of `pcrec_fact_*(` calls outside `src/facts/`, comments excluded): 60 functions
in 8 files, 95 call sites. `req_run` alone has 20. Five facts have exactly one call site (`end_mark`,
`kset_walk`, `never_matches`, `reports_empty`, `span_facts`). Three are asked by no consumer at all:
`req_pieces` ("no reader but `--emit-facts`", `facts.h`), `req_set_maxoff` and `req_run_maxoff`. These
are reached only through `depends` edges or the force loop.

### 1.2 Undeclared proof uses (not routed through `facts.def`)

| proof | site | what it decides | why it matters |
|---|---|---|---|
| **root minimum width on the VM route** | `emit_vm.c:10602` `v->root_minw = pcrec_minw(root)` → `CandVmFacts.root_minw` (`emit_vm.c:11405`) → `cand_min_width` (`emit_dfa.c:10234`) | WIDTH on CAND_ROUTE_VM; the VM `attempt_max` | **The same question ("minimum width") has two definitions, one per route.** The DFA route reads the declared `width` fact (E3, NFA). The VM route reads an undeclared node-grain call on the AST. Its soundness ORDER (after `pcrec_callgraph_build`'s fixpoint) is stated only in a comment (`emit_vm.c:9651`: "the ORDER is the whole content of this field") |
| node-grain widths inside VM emission | `emit_vm.c:5928, 6516, 6709, 6850, 9270` (`pcrec_minw` on subtrees); `pcrec_nullable` at `:1480, 2493, 2498, 2671, 2675, 3247, 3290, 5558, 6631, 6674` | MRL clamps, guard counts, step costs | node grain: allowed by design §4.3, but never listed |
| node-grain widths before any seal | `mod_lookaround.c:321` (`pcrec_cwmin/cwmax`), `callgraph.c:840-881` (fixpoint) | lookbehind width rule; call widths | by design (§4.3); pre-E1 |
| never-match flips on the machine | `emit_dfa.c:4553`, `:4857-4859` (`pcrec_dfa_accepts_nowhere`); `kset.c:948` (the fact itself reads it) | NEXT's predicate, the `empty` LOCATE, the ATTEMPT route | the fact `never_matches` exists (E2, asked after `machines_final`), but these emitter sites ask the machine directly, not through the fact |
| prefilter admission rows | `select_engine.c` `pf_admits[]` (:780-858): `size-dropped`, `overflow-drop`, `forced-on/off`, `default` | `Job.fit` prefilter | only the two nullable rows read a fact. The rest read `cx->collapse_reason`, `dfa_disabled` and options, which are attempt state, not facts |
| the size-cap ladder | `compile.c:1330-1500` (`fit` rows: `size-term-trial`, `sel1-collapse`, `sel1-drop`, `drop-compound`, `drop-end-mark`, `drop-landmark-walk`, `drop-anchored`, `drop-premul`, `drop-handoff`, `drop-prefilter`, `drop-islands`) | the next attempt | rows declare what they SET (`.sets`), never what they READ |
| req-use rows | `CAND_READ(reader, CAND_SLOT_FIRST, ..., "req-use")` :9029 and the PRESENCE rows | which pre-check is emitted | slot-to-slot reads ARE declared (`cand_nodes[].reads`, §1.4); the fact reads under them are not |
| `pcrec_artifact_has_dfa_scan` | compile.c:3064, emit_dfa.c:1603, select | route | a decision copied from `Job.fit`, read as a fact by `used`'s ballast (`:1603`) |

### 1.3 Cross-attempt and cross-stage state (writer → reader)

| field | writer | readers | what it carries |
|---|---|---|---|
| `Job.fit.*` (chosen, prefilter, `prefilter_collapsed`) | `select_engine` S2 | `pcrec_artifact_has_dfa_scan`, both emitters, `emit_dfa.c:12464` | the route decision every S4 to S7 consumer is gated on |
| `Job.nfa` (rebuilt collapsed) | compile.c:3191 | the E3 seal and every E3 fact | the machine the E3 facts describe |
| `job->revend_form` | `revend_choose_form` S4b | `compile.c:1122` (ladder), `emit_rev_end` | the rev-end form |
| `cx->anchored_dropped` | ladder, :2456 | compile.c:394 | next attempt |
| `cx->end_mark_dropped` | ladder, :2458 | compile.c:582, :1122 | next attempt |
| `cx->req_handoff_dropped` | ladder, :2460 | emit_dfa.c:8958, :9138 | next attempt: no handoff rows |
| `Job.machines_final` | compile.c:3285 | the `never_matches` accessor's precondition | the machine-final point (NMSOUND-2 asks for it to become an epoch) |
| `v->root_minw` | emit_vm.c:10602 | WIDTH (VM), `VmStamp` (:14404) | §1.2 row 1 |

### 1.4 What is already declared on the consumer side (the precedent this design extends)

The start table already has a CHECKED consumer-dependency mechanism at SLOT grain.
`cand_nodes[]` (`emit_dfa.c:10072`; type `CandNode`, :9995) declares, per slot and per route:
- `reads[t]`: which slots' selections this slot's predicates read;
- `under[t]`/`by[t]`: the deny bits a read is made under, which makes a slot cycle acyclic in rows;
- `kask[t]`/`kfields`: the kit asks and the answer fields read;
- `succ` and the progress classes `raise`/`rank`/`entry`: the RUNTIME hand-off order between slots.

The trace build (`PCREC_CAND_TRACE`) traps `undeclared-read` (`cand_read_hit`, :11903), `undeclared-ask`,
`ask-while-open` and `undeclared-ask-field` (:11929-11950). A structural self-check holds the graph
acyclic (:11477). **What is missing is one column: the FACTS each slot's predicates read.** Facts
are the one input a predicate can read without the slot graph seeing it.

`facts.def`'s `depends` column is the producer-side twin. It covers derivation → derivation edges and
is checked by `pf_ask`.

---

## 2. Implicit orderings

**S** = soundness-relevant: getting it wrong can give a wrong answer or an internal-error refusal.
**E** = effect-only: speed, size, a listing or a stamp. `declared?` says where the ordering is
written down today.

| # | ordering | reason | S/E | declared? |
|---|---|---|---|---|
| O1 | E1 seal after `callgraph_build`, before `select_engine` | `lower_enc` rewrites in place; select reads the E1 facts | S | yes: the epoch guard plus `pf_check_e1` |
| O2 | E2 seal after `lower_enc` | the last tree rewrite | S | yes: the epoch guard |
| O3 | E3 seal after the collapse rebuild and the wrap, ENG_UNANCH only | the rebuild replaces `Job.nfa` | S | yes: the guard plus per-route declines |
| O4 | `never_matches` only after `machines_final` | it reads the built machines | S | **comment only** (`facts.h`; NMSOUND-2 asks for an epoch) |
| O5 | `root_minw` read after `callgraph_build`'s fixpoint | `A_CALL` widths come from the fixpoint | S | **comment only** (`emit_vm.c:9651`) |
| O6 | `select_engine` (writes `Job.fit`) before every route-gated consumer | `pcrec_artifact_has_dfa_scan` and the E3 route follow from it | S | by code position |
| O7 | `revend_choose_form` before the drop-end-mark row and `emit_rev_end` | the form is their input | S | by code position |
| O8 | ladder `.sets` before the next attempt's readers of `*_dropped` | cross-attempt | S | half: the row declares the write, the readers are undeclared |
| O9 | in a slot predicate, NEXT's selection CLOSED before a kit ask about it | the ask reads NEXT's site | S | **yes**: `ask-while-open` (trace) |
| O10 | stamps and `<P>_FINDINGS` rendered before the force loop | forced asks must not move the artifact | E (listing) | yes: design §11.4 plus its §11.6 check |
| O11 | the `used` bit set only by pass asks made in S2 to S8 | it is the listing's definition | E (listing) | **control flow** (§3) |
| **emitted (runtime) composition order: the search entry and the attempt loop** |||||
| O12 | VM hat: end-window clamp → min-width → pre-check → handoff `first` → K73 offset-0 seek → start-set entry seek → attempt loop (`emit_vm.c` rpfix :13564, :13575, :13595, :13820-13841, :13849, :13855) | narrowing first; each later bound is a lower bound | S (each must be a sound lower bound alone); E (order) | **prose comments** ("after the clamp, before the pre-check"; startset.md §4.2's order) |
| O13 | attempt loop retry: encoding advance → handoff re-entry → start-set retry seek (rpfix :13959-13964) | "two lower bounds, each sound alone" (comment) | S each, E order | comment |
| O14 | **[REQ-PAST-LAST] stop vs every position move** (incident 1) | the re-ask is placed before the start-set seek; nothing re-checks after the ENTRY seek, so one attempt past the last occurrence can still run and give up | E today (it gives up, it never answers wrong; BASE gives up the same way). It becomes S for any row whose stop is relied on as a NOMATCH proof | **undeclared**; review r2-reqpast EMIT-1/CON-3 |
| O15 | DFA fronts: clamp → min-width → pre-check (`emit_unanchored`; `attempt_entry` :15215 copies the order) | as O12 | S/E | comment ("`emit_unanchored`'s order") |
| O16 | end window × `\G` | both read `search_from` | S | declared as DISJOINT DECLINES (`endwin.c` decline 3, cited at `emit_vm.c` rpfix :13560) |
| O17 | G1 dominance × handoff | G1 must judge the scan WITHOUT the handoff | S | **yes**: `cand_nodes[PRESENCE].under[NEXT] = PCREC_NO_REQ_HANDOFF` |

What follows from the table: the compile-time orderings O1 to O3 and O9 to O10 are declared and
checked. O4 to O8 are code position or comments. The emitted orderings O12 to O15 have no
declaration that a machine can read. Incident 1 is an emitted ordering, not a compile-time read
ordering, so a fact-read check alone cannot catch it (§6).

---

## 3. "Asked": where `used` comes from today, and a declared definition

### 3.1 Today

`used` is bit `f` of `PatFacts.used`. `pf_enter(cx, f, pass=true)` sets it (`facts.c:144`), so any
public accessor call sets it on whatever path reaches it, including a call whose result is discarded
or whose branch emits nothing. `facts_dump.c:177` prints it. The spec defines it as "a compiler pass
asked for the fact while the artifact was built" (`facts_listing.md` §4.1, the `used` column, and
§4.1¶2's re-sourcing rule).

The column is therefore a CONTROL-FLOW TRACE, and a pinned one: `emit_sweep`'s `facts` stream
compares it. To keep it still across refactors, the tree carries asks whose only job is to set the
bit (BALLAST):

| ballast ask | keeps `used yes` for | comment |
|---|---|---|
| `select_engine.c:1210` | `empty_admits` on every compile | "the ask keeps that column where it was (decfbB2 finding 7)" |
| `emit_dfa.c:1602-1603` | `req_whole_run` on every pre-check; `req_set` with no DFA scan | R17-b′ B3b, Q-WR-12 |
| `emit_dfa.c:8704` | `req_set` under set-leads | B3b, Q-WR-12 |
| `emit_dfa.c:15215` on `lane/s1fix` (`296d38e7c`) | `width` on the ATTEMPT route, where it is `absent` | incident 2: a dead branch kept for its ask |

Incident 2, exactly: CHECKS-4 deleted an unreachable `if (minw)` in `attempt_entry`. Its call to
`cand_front_min_width` → `cand_min_width` → `pcrec_fact_width` was the ask, so `width` went
`used no` on 365 attempt-route patterns (`scratch/s1fix/sweep.log`). The fact there is E3 on an
unsealed route. It answers `absent` (`pf_route_unsealed`, `facts.c:129`) and can carry nothing, yet
it counted as "consumed".

### 3.2 A declared definition

> **`used(f)` = some DECLARED READER that RAN on this compile lists `f` in its `reads`.**

A declared reader is one of:
1. a ROW of an existing first-match table: `cand_rows[]` through its slot's `cand_nodes[]` entry
   (§1.4), `pf_admits[]`, the fallback `fit` rows, `pflw_rows[]`. A row "ran" when its predicate was
   evaluated. That is the same event as today's trace `CAND_HIT`. Whether it ran, not whether it was
   CHOSEN, is the right event: a predicate that read the fact and declined still consumed it.
2. a STAGE READER: the handful of non-table consumers in §1.1 (the collapse decision :3120, the
   NEVER-MATCH gate, `emit_attempt`'s assertion, the stamps, `retry_none_applies`, `revend_choose_form`).
   Each is one row of a small table (§6.4).

Then `pf_enter` stops setting `used`. The mark is set once per reader run, from the reader's
declared mask. The four ballast asks are deleted. A dead branch, a discarded result and a helper's
incidental call no longer move the listing. `_stated` accessors stay as they are: they are reads by
a non-pass, and they are declared as such (`reads_stated`).

### 3.3 Migration

1. Add the declarations. Run the trace build over the corpus (§6.3) in SHADOW: compute
   `used_declared` next to today's `used` and diff them per pattern.
2. Each difference is either a missing declaration (fix the table) or a ballast ask (deleting it
   moves nothing once the declaration carries it).
3. When the shadow is 0-diff, switch the column to `used_declared`, delete the ballast, and land the
   spec hunk (`facts_listing.md` §4.1¶2 gains one sentence defining the column by declaration; values
   unchanged).

---

## 4. Seam value domains: what crosses to the kit carrying a sentinel

pcrec's width sentinel is `PCREC_W_UNBOUNDED == PCREC_MINW_MAX == 2^40` (`limits.def:394`,
`internal.h:8385`). Its contract is "a consumer asks `w >= PCREC_W_UNBOUNDED`, never `==`" (the comment
at `internal.h:8378-8384`). A SATURATED finite width is indistinguishable from an unbounded one. The
kit has its own vocabulary: an UNSTATED zero, refused where read; `MF_SPAN_UNBOUNDED == UINT64_MAX`
(`memfn.h:277`); and `MF_ORDER_UNKNOWN == 0xFFFF` (:555).

| seam field (memfn.h) | type | pcrec builder | sentinels it can carry | meaning declared? |
|---|---|---|---|---|
| `mf_site.head_max` (:851-863) | uint64 | `emit_dfa.c:1648` `= handoff ? req_handoff_k(cx) : 0` | **0 = "no handoff" (overloaded with distance 0)**; **2^40 = pcrec's "unbounded"** on the unbounded handoff row (`lane/rpfix`: `(a+)+zq`, fixture C10) | **NO.** memfn.h defines it as "the largest distance, in bytes" with no reserved value. `presence.c:245` reads it as `k` in `k*h` arithmetic (review TH-5: only the trace shadow reads the verdict today) |
| `mf_site.span_lo/span_hi` (:780) | uint64 | `memfn_sites.c:469`, `emit_vm.c:4941`, `emit_dfa.c:9251`, `:12943` | `MF_SPAN_UNBOUNDED` | yes. pcrec translates its `-1`/cap at each builder (`span < 0 ? MF_SPAN_UNBOUNDED : span`). 4 sites, each a hand translation |
| `mf_pred.omin` (:710-727) | int32 | `emit_dfa.c:1520` (`= 0`) | 0 = "sound under-estimate" (PR-6); negative refused | yes |
| `mf_pred.member_order` | uint16 | presence builder | 0 = UNSTATED (refused), `MF_ORDER_UNKNOWN` | yes |
| `mf_term.offset` (:643) | int32 | every term builder | ≥ −`MF_MAX_BACK` | yes (bound) |
| `mf_term.ppm_lo/hi` | uint32 | builders | 0..`MF_PPM_FULL` "when unknown" | yes |
| `mf_term.run_len` | uint32 | builders | 0 refused | yes |
| `mf_pred.fn_ref`, `table_ref` | uint32 | builders | 0 = none | yes |
| window statement W0-W2 (`window_stated`/`move_back`/`overshoot`) | — | `pf_window_of` (:6870) | the changelog names `MF_MOVE_UNBOUNDED`/`MF_OVER_UNBOUNDED` (memfn.h:162-164) | **no `#define` found** in `memfn.h` at this commit: reserved in prose only (not traced further; flagged for the kit) |

pcrec facts that carry sentinels on the pcrec side and FEED seam fields: `end_window` (−1 =
declined), `req_run_maxoff`/`req_landmark_maxoff` (−1 = none; ≥ 2^40 = unbounded), `req_byte` (−1),
`width.bmin` (−1 = unknown), `ReqRun.whole_maxoff` (−1 / ≥ 2^40). `facts.h` declares each in a
comment. **`facts.def` has no column for a fact's value DOMAIN**, so no check can see a −1 or a 2^40
leave the fact layer unconverted.

Incident 3, exactly: `req_handoff_k` returns `whole_maxoff` or `landmark_maxoff` (`emit_dfa.c:9018`),
whose domain includes 2^40. `head_max`'s domain does not include it. D157 already says what the fix
is shaped like: "unbounded" is a FACT the seam should be able to state (TH-5), not a large number.

---

## 5. Work-removing mechanisms that compose

| mechanism (slot / flag) | facts it reads | shares a site or a fact with |
|---|---|---|
| end-window clamp (WINDOW, `-fno-end-window`) | end_window, end_pin | rev-end (end_pin); every later entry check (it narrows their window) |
| min-width (WIDTH, `--harness=no-min-width`) | width (DFA) / `root_minw` (VM, undeclared) | the pre-check, the attempt bound, `pf_close` |
| necessary pre-check (PRESENCE, `-fno-req-byte`/`-fno-req-run`) | req_* | G1, handoff, run-pinned prefilter, offset skip, set-leads (all req_run) |
| handoff (FIRST/NEXT, `-fno-req-handoff`, ladder `drop-handoff`) | req_landmark_maxoff, req_whole_run | the start-set seek (one position variable), G1 (declared `under`), REQ-PAST-LAST stop |
| start-set seek (NEXT, `-fno-start-set`) | start_set | handoff (both move `attempt_position`), K73 offset-0 seek, scan state written |
| run-pinned prefilter / offset skip (NEXT, `-fno-run-prefilter`, `-fno-offset-skip`) | run_pin, kset_walk, req_run | pre-check (G1 dominance), each other |
| landing / start-width (NEXT/RECOVER, `-fno-start-landing`, `-fno-start-width`) | land_char, width | min-width (width) |
| anchor bound (BOUND, `-fno-vm-anchor-bound`) | start_anchor | PRESENCE/FIRST/NEXT read BOUND (declared slot reads) |
| re-seed (RETRY, `-fno-hyb-reseed`) | — (VM facts `has_push`, gap) | the retry seek |
| rev-end / landmark walk (LOCATE, `-fno-rev-end`, `-fno-landmark-walk`) | end_pin, end_mark, start_set (counterfactual NEXT) | NEXT (declared `under[NEXT]`) |
| never-match (`--emit-ir` refusal, `empty` LOCATE) | never_matches, plus machine reads (undeclared) | every NEXT row (`pcrec_dfa_accepts_nowhere` at :4553) |

**Coverage today.** `make test-axes` (`tests/axes/run_axes.sh`) sweeps the corpus with ONE flag at a
time (plus `--engine=`). It checks answer identity against the default, per case. No pair of denies
is swept. Rows are composed pairwise only inside `cand_nodes[]` (O9, O17) and through the slot graph's
acyclicity.

**Declared independent nowhere** (the pairs that share a position variable or a fact and have no
declaration of how they compose): handoff × start-set seek (O13, a comment); REQ-PAST-LAST stop × the
entry seek (O14, incident 1); min-width × pre-check order (O12/O15, comments); clamp × handoff (both
narrow the first position); landing × min-width (both read `width`); never-match machine reads ×
the NEXT rows; ladder drops × their row predicates (O8). The one pair declared DISJOINT is end window
× `\G` (O16). The one pair declared COMPOSED is G1 × handoff (O17).

---

## 6. The three-layer check: a sketch

The rule for all three layers: **declare once, in the tables that already exist; generate everything
else** (`facts.def`'s own shape). Nothing below adds a table whose rows duplicate an existing table's
rows.

### 6.0 The declaration (what gets written)

| where | new column | grain |
|---|---|---|
| `facts.def` | `domain`: the value domain of the fact's integer payload, a token from a small closed vocabulary (`W` width/offset with `UNBOUNDED`, `BYTE` −1..255, `COUNT`, `BOOL`, `STRUCT`), each token defined once (§6.4) | fact |
| `cand_nodes[]` (`CandNode`) | `facts[route]`: a `PF_*` bit mask per route of the facts this slot's predicates read; `facts_stated[route]` likewise | slot × route (the grain the table already declares reads at) |
| `pf_admits[]`, fallback `fit` rows, `pflw_rows[]` | `.reads`: a `PF_*` mask; the fit rows also gain `.reads_x` for the cross-attempt fields they read (O8) | row |
| a stage-reader table (§6.4) | one row per non-table consumer in §1.1: name, stage, `reads` | consumer |
| memfn seam fields (kit side, by request) | the field's domain token, and a reserved `UNBOUNDED` where the domain has one | field |

**Emitted ordering (O12-O15) is a second axis.** The slot graph already declares the runtime
hand-off order (`succ`, `raise`). What it lacks is a POSITION-MOVE column: which rows MOVE a named
position variable (`attempt_position`, `search_from`, `window_end`), and which rows declare an
obligation "re-checked after every move of X" (the REQ-PAST-LAST stop is one). This is one column per
row (`moves`, `after_moves`) in `cand_rows[]`, not a new table.

### 6.1 WRITE time: a lint over the code text

- **What:** a script (`tests/codegen/run_facts_checks.sh` gains a section; pre-commit runs it on
  touched `src/gen/`, `src/opt/`, `src/core/` files) scans each table-row predicate's body (the
  function named in `.applies`, plus its static callees in the same file, one level deep) for
  `pcrec_fact_X(` text. It compares that set with the row's declared mask. A call not declared is
  red. A declared fact that no text in the predicate's reach names is a warning (it may be reached
  transitively).
- **Catches:** a new ask added without its declaration (most of G1 at review time); incident 3's
  shape where it is visible as text: an assignment of a `domain W` accessor's result into a seam
  field without the converter (§6.4) is a text pattern.
- **Misses:** transitive asks through helpers more than one call deep (`cand_front_min_width` →
  `cand_min_width` → `pcrec_fact_width` is two). Incident 2 (the problem there was the DEFINITION of
  `used`, which §3 fixes, not an undeclared read). Incident 1 (runtime order).
- **Cost:** small, about 150 lines of awk/python in the existing check file, plus a sabotage row.
  Precedent: the include-graph check's plain-text table scan (design §4.2.3). Its control is the code
  text, and its subject is the table. Those are two sources.

### 6.2 COMPILE time: the build refuses

C cannot evaluate a `const` array's members in `_Static_assert`, so "compile time" means one of two
shapes, in order of cost:
- **(a) Generated build-time table check (recommended).** `facts.def` already generates the epoch
  array. Extend the generation: a per-stage maximum epoch (`S2 → E1`, `S7 → E3 on ENG_UNANCH`), and
  for every declared reader, `epoch(f) ≤ maxepoch(stage)` for each `f` in `reads`. A derived fact's
  `depends` must be a subset of its readers' declared closure. The check runs as a tiny program
  linked against the tables (`build/pcrec-factcheck`, a `make` prerequisite of `libpcrec.a`'s test
  targets) or as `run_facts_checks.sh`'s plain-text pass. **The build refuses a declaration that
  reads a fact before its seal.** For incident 2, the ATTEMPT route's WIDTH reader would declare
  `width` on CAND_ROUTE_ATTEMPT, an E3 fact on a route that never seals E3. The check then answers
  "declared read of an unsealed-route fact", and the dead ask would be visible at declaration time.
  O4 (machine-final) becomes checkable once NMSOUND-2's machine-final epoch is a `PfEpoch` value.
- **(b) Typed seal tokens (stronger; not recommended now).** `pcrec_facts_seal_e3` returns a
  `PfSealE3` token, and E3 accessors require it as a parameter. A consumer then cannot even CALL an
  E3 accessor outside the ENG_UNANCH arm's dynamic extent unless the token is threaded to it. This is
  a true compiler refusal. The cost is threading a parameter through the S7 emitter's call tree, a
  large diff in `emit_dfa.c` (16k lines). Trigger: a read-before-seal defect that (a) and the trace
  both missed (D77).
- **Domains (G3), compile time proper:** facts of domain `W` return a one-member struct
  (`typedef struct { long long v; } PfW;`) at the seam builders only (`memfn_sites.c`, the presence
  builder). Assigning one to a `uint64_t` kit field then does not compile without the one generated
  converter `pf_w_to_mf(PfW, mf_domain)`. That function maps `≥ PCREC_W_UNBOUNDED` to the kit's
  reserved `UNBOUNDED`, or refuses (an internal error) where the kit field's domain has none. **This
  catches incident 3 at compile time.** It also removes the four hand translations to
  `MF_SPAN_UNBOUNDED` (§4). Cost: about 10 builder sites, plus a kit request for `head_max`'s
  reserved value (D157: the kit decides its spelling; pcrec states the fact).

### 6.3 TRACE: a test-build record compared over the corpus

- **What:** in the existing `PCREC_CAND_TRACE` build, `pf_enter` consults the innermost open READER.
  The trace build already keeps the slot predicate stack (`cand_eval_slot[]`, used by
  `ask-while-open`). The stage-reader table supplies the readers outside it. An ask whose fact is not
  in that reader's declared mask (for the reader's route) is `CANDORACLE undeclared-fact`, the same
  trap family as `undeclared-read`. An ask with no open reader at all is `CANDORACLE unowned-ask`.
  Each declared fact a reader never asked over the whole corpus is reported (over-declaration; a
  warning list, never red).
- **Emitted order:** the trace already prints `CANDTRACE` records in emission order. Add a record
  per position MOVE and per obligated RE-CHECK (§6.0's second axis). A checker over the trace stream
  asserts "every MOVE of X by a row on the path is followed by the obligated re-check before the
  next attempt begins". **This is the layer that catches incident 1**: the entry seek is a MOVE of
  `attempt_position` with no re-ask after it. It catches it on the first corpus pattern that takes
  the unbounded handoff row (C10).
- **Catches:** every undeclared read, transitive ones included (incident-2-like drift). The
  `used`-shadow diff of §3.3. Incident 1 (with the move column). A sentinel at the seam: the trace
  build's `site_check` can refuse a `head_max ≥ 2^40` (incident 3, after the fact).
- **Cost:** one corpus run of the trace build. The trace build already exists, and the C1 trace diff
  already runs over the corpus in `make test`'s start-table section. Exact overhead is UNMEASURED.
  The structural self-check grows by one mask comparison per row.
- **Independent control:** the subject is the declared masks (tables). The control is `pf_enter`'s
  run-time record, a second source. Population: count readers seen, readers declared, and readers
  never reached. A sabotage row adds an undeclared `pcrec_fact_req_set(cx)` call inside one row
  predicate and must go red. A second removes a declaration and must go red. A third, for the
  move axis, moves the REQ-PAST-LAST re-ask before the entry seek, i.e. recreates incident 1.

### 6.4 How it extends `facts.def` rather than adding a parallel mechanism

- The DOMAIN column goes on `facts.def`'s rows. The value vocabulary is one small X-macro
  (`src/facts/domains.def`: token, C type, sentinel, renderer) because the kit side needs the same
  tokens. It is a vocabulary, not a second fact table.
- Fact READS go on the tables that already own the decisions: `cand_nodes[]` (beside `reads`/`kask`,
  same grain, same trap family), `pf_admits[]`, the `fit` rows, `pflw_rows[]`. This is "decisions as
  declared first-match tables" applied to their inputs.
- The one new table is the stage-reader list for the roughly 8 consumers that are not table rows.
  Each such consumer is a candidate to BECOME a table row in its own remodel. Until then, the list is
  their declaration. The table shrinks as rows move into real decision tables. It never grows a
  second home for a row that already has one.
- The `depends` column stays the producer DAG. The new `reads` columns are the consumer edges.
  Together they make the full graph `facts → readers → (writes) → readers`, which §1.3's
  cross-stage fields close.

### 6.5 What each layer catches of the three incidents

| incident | WRITE (lint) | COMPILE (generated check / types) | TRACE |
|---|---|---|---|
| 1 REQ-PAST-LAST stop before the seek | no | no | **yes**, with the move column (§6.0 second axis) |
| 2 a dead branch was the ask | no (nothing undeclared) | partly: an ATTEMPT-route `width` declaration is refused as a read of an unsealed-route fact | **yes, by construction**: §3's declared `used` makes the deletion a 0-mover; the shadow diff finds the ballast |
| 3 2^40 into `head_max` | partly (a text pattern at the builder) | **yes**: typed `PfW` plus the one converter | yes: the seam `site_check` refusal |

### 6.6 Failure modes, today and under the design (rulings R1)

The vocabulary: **loud refusal** (a check, a build or a compile stops and names the cause);
**crash** (an abort without a cause named); **silent wrong answer**; **silent missed optimization**
(work that should have been removed runs, and the answer is right); **silent observable change**
(a listing, a stamp or a give-up moves, and no answer is wrong).

| incident | today | WRITE (lint) | COMPILE | TRACE (compiler debug run, §6.7 a) | MATCHER debug run (§6.7 b) |
|---|---|---|---|---|---|
| 1 stop before the seek | **silent missed optimization**, observable as a give-up: one attempt past the run's last occurrence runs and can hit the step budget (`(a\|aa\|b)+cxyz`, steps=3000: err −2 where PCRE2 says nomatch; inside the allowed direction). Found by a human critic | silent (no text pattern) | silent (an emitted order, not a read) | **loud refusal** on the corpus, with the move column (R8): "a MOVE of `attempt_position` with no re-check after it" | **loud refusal** at run time: the obligation check "no attempt starts past the stop's bound" fires on the first subject that reaches it (C10) |
| 2 a dead branch was the ask | **silent observable change** (the `--emit-facts` `used` column moved on 365 patterns). Caught after the fact by `emit_sweep`'s facts stream | silent | **loud refusal** of the ATTEMPT-route `width` declaration (an E3 read on a route that never seals E3) | **cannot happen**: `used` comes from declarations, so the deletion moves nothing. The R3 shadow diff is loud while the ballast still exists | not applicable (no matcher bytes move) |
| 3 2^40 into `head_max` | **silent**, latent: no answer or pick moves today, because only the trace shadow reads the kit's verdict (TH-5). Once the verdict is routed it becomes a **silent missed optimization** or a wrong pick, and the arithmetic `k*h` on 2^40 can overflow `uint64` | partly loud (the builder's text pattern) | **loud refusal**: the build does not compile without the converter | **loud refusal**: the seam check refuses `head_max ≥ 2^40` | not applicable (a compile-time seam value) |

The target property: every row's design column is LOUD in at least one layer that runs in `make test`
or at commit. No incident stays silent under the design.

### 6.7 Two debug run times (rulings R1, Frank: "If the trace knew the dependencies, it could (in debug mode probably) be used to note errors during run time")

**(a) The COMPILER's own run.** This is §6.3's TRACE layer, made a refusal. In the test builds
(`PCREC_CAND_TRACE`, which `build/pcrec-harness` and the start-table section already use), every
`pf_enter` checks three things against the declarations: the fact is in the innermost open reader's
`reads` for its route; the reader's declared stage is at or after the fact's epoch; and, for a
derived fact, the asked fact is on `depends`'s closure. A miss is `pcrec_ctx_fail(cx, 0, "internal
error: ...")` naming the reader, the fact and the stage. It is the same refusal shape as the epoch
guard (`facts.c` `pf_enter`), so it fails a compile, not the process. `--emit-facts` keeps its rule
that the listing never refuses a compile that succeeded: the force loop is not a reader and is
exempt. The default `build/pcrec` and the library carry none of it.
- *Catches:* every undeclared or early read, transitive ones included; with R8, incident 1's
  emitted-order obligation, checked over the trace stream at the end of the compile.
- *Cost:* one mask test per ask in test builds only. Corpus overhead is UNMEASURED and expected to
  be small (asks are memoized; the slot predicate stack already exists).
- *Lives in:* `src/facts/facts.c` (`pf_enter`, under `#ifdef PCREC_CAND_TRACE`), with the reader
  stack beside `cand_eval_slot[]` in `emit_dfa.c`.

**(b) The GENERATED MATCHER's run.** A debug EMIT MODE in which every work removal that a fact
justifies also emits, at its point of use, a check of the claim it relies on. The corpus and the
fuzzers then verify the PROOFS, not only the answers. Two tiers:
- **Fact checks (cheap).** Re-verify the runtime claim with a naive, independent loop at the point
  where the removal acts:
  - the required-run STOP: when it ends the search, scan the rest of the subject with a byte loop
    (not the kit's scan) and assert no occurrence of the run remains;
  - the REQ-PAST-LAST OBLIGATION: at the top of each attempt, assert the attempt position is not past
    the last occurrence of the run (computed once, naively). **This is the check that catches incident
    1**: it fires on an attempt the missing re-check let through;
  - MIN-WIDTH: when it stops, assert `subject_length − pos < minw`, and assert that no position in the
    stopped range is accepted by the shadow attempt (next tier);
  - the START-SET seek: assert that every skipped byte is outside the start set (a 256-bit table the
    debug mode emits from the fact);
  - the END-WINDOW clamp and the ANCHOR bound: assert that the shadow attempt rejects every position
    the clamp or the bound removes.
- **Proof checks (expensive).** One shared helper, `proof_skip(a, b, why)`: for every start position
  in `[a, b)` that a removal skipped, run the REFERENCE attempt (the anchored attempt function with
  every work removal denied, emitted beside the optimized one) and abort, naming `why`, if any
  position matches. Every removal that moves a position (clamp, min-width, pre-check NOMATCH, handoff
  jump, start-set seek, offset skip, landing, the stop, the anchor bound) calls it with its own
  token. Cost: quadratic in the subject length. That is acceptable on corpus subjects and fuzzer
  inputs, and never acceptable in shipped output.
- *Independent control:* the reference attempt shares pcrec's parser and IR with the optimized one.
  So it verifies that a REMOVAL is sound relative to pcrec's own attempt semantics, which is exactly
  the property in question. The attempt's own semantics stay checked by the PCRE2 answer oracle, as
  today. The naive loops in the fact tier share no code with the kit's scans.
- *Lives in:* a harness lever beside the existing ones (`PcrecHarness` bitfield in
  `src/core/internal.h`, read only by `build/pcrec-harness`; name proposed: `--harness=verify-proofs`).
  The harness's `.rxt` driver turns it on for an opt-in sweep (`make test-proofs`, the `test-axes`
  shape). It is never in default output, and `build/pcrec` refuses the lever. Each emitted check
  carries the removal's row token, so a refusal names the row (the stamp vocabulary already names
  rows).
- *Catches:* incident 1 (the obligation check, at run time, on C10's subject). Any unsound removal
  the answer oracle misses because the removed attempts would not have matched on that subject anyway
  (the proof check sees every skipped position, the answer check sees only the result). It does not
  catch incidents 2 or 3, which never reach matcher bytes.
- *Cost:* an emit path per removal (about 10 sites, each a few lines beside the existing emitter
  call), the reference-attempt emission (the `-fno-*` denies already produce it; the debug mode emits
  both in one artifact), and one opt-in corpus plus fuzzer run per landing that touches a removal.
  No abi event, since default output is unchanged. The debug output's own shape is test-only and has
  no spec entry beyond the lever's line in the harness documentation.

---

## 7. Size of the build, and what the coming plan adds

### 7.1 Units (one commit each, each under the zero-movers emit A/B gate)

| unit | content | moves |
|---|---|---|
| R0 | `facts.def` `domain` column, `domains.def` vocabulary, generated per-fact domain array | nothing |
| R1 | `CandNode.facts[]`/`facts_stated[]` filled for all 10 slots; the trace trap `undeclared-fact`/`unowned-ask`; sabotage rows | nothing (trace build only) |
| R2 | `.reads` on `pf_admits[]`, `fit` rows (plus `.reads_x`), `pflw_rows[]`; the stage-reader table (~8 rows) | nothing |
| R3 | the `used` SHADOW (`used_declared` beside `used`, trace build), the corpus diff to 0 | nothing |
| R4 | switch `used` to the declaration; delete the 4 ballast asks; the `facts_listing.md` §4.1¶2 hunk | the listing only where declared (target: 0 movers) |
| R5 | the write-time lint section plus pre-commit wiring | nothing |
| R6 | the generated epoch-vs-stage check (§6.2 a) | nothing |
| R7 | `PfW` at the seam builders plus the converter; kit request for a reserved `head_max` UNBOUNDED (the kit's ABI event, the kit's lane) | kit ABI; no pcrec emitted byte (the trace shadow only reads `head_max` today) |
| R8 | the position-move column on `cand_rows[]` plus the trace stream checker (emitted-order axis) | nothing |

| R9 | the compiler debug run's refusal (§6.7 a): `pf_enter`'s three tests as `pcrec_ctx_fail` in test builds | nothing (test builds) |
| R10 | the matcher debug emit mode (§6.7 b): the fact tier first (the stop, the REQ-PAST-LAST obligation, min-width, start-set); the proof tier's `proof_skip` plus the reference attempt second; `make test-proofs` | nothing in default output |

That is 11 units. R0 to R4 are the core (G1, G2). R7 is G3. R8 is G4's emitted half. R9 and R10 are
the two debug run times. R10's fact tier is the cheapest way to catch incident 1's class and could go
first if the emitted-order axis waits. R1, R3, R8 and R9 each need a corpus run of the trace build.
R10 needs its own opt-in sweep. The others need `make test-codegen` only. The VM's
`root_minw` (§1.2 row 1) is not in these units. It is one fact question with two definitions, and the
fix (one `width` fact the VM route also reads, or a declared `root_minw` fact at E2) is a fact
change, filed separately (`[FIND-MINW]` already names "a width fact sealed on the attempt machine" as
its trigger).

### 7.2 What [COND-FAMILY] and DFA captures would add

From `docs/design/cond_family.md` §3 and `docs/design/dfa_captures_research.md` §5.2:
- **M1 `A_COND` node:** every no-`default:` derivation switch in `src/facts/` (`kset.c`,
  `startset.c`, `sa_walk`, `ew_walk_marked`, `em_set`, the req walk's kind rows) gains an arm. Those
  are derivations, not consumers, but each new arm can change a fact's value for every consumer at
  once. The `reads` declarations are what lists those consumers mechanically (design §7.2's "the
  consumer list is the callers of the accessor" becomes a table query).
- **New facts:** `tag_shape` (copy-free / fixed-offset / general, [ENG-TDFA]), a `PF_KIND_*` bit for
  conditions, and M12's guard facts ([REQ-LOOKAROUND] span_arms L1-L3). Each is a `facts.def` row
  plus its `domain`.
- **New consumers:** the engine table's tagged-DFA row in `select_engine.c` (reads `tag_shape`,
  kinds); the tagged entry in `emit_dfa.c`; PRESENCE rows reading the lookaround guards; the M10 size
  ladder's new rows (reads plus `.reads_x`); [ENGINE-WHY]'s explanation (a listing-only reader,
  `stated`); [NEVER-MATCH] over an empty intersection (M4).
- **A new ROUTE for E3:** a tagged DFA is a machine E3's route rule must name (sealed, or a named
  decline). The generated epoch-vs-stage check (R6) is what keeps a new consumer from reading E3 on
  it.
- **New emitted orderings:** M7 "honour-on-close" runs a checker inside the VM attempt; the tagged
  entry replaces `rx_match_anchored` inside the hybrid's window protocol. Both add position moves
  and re-checks to O12/O13. That is the reason R8 belongs in the foundation and not after it.

---

## 8. Residuals (what none of the three layers catches)

- A HAND RE-SPELLING of a fact (a consumer's own walk) is the residual already named in
  `src/facts/CLAUDE.md`. `root_minw` is the live instance (§1.2).
- An ordering whose two halves are in different STAGES but in the same function (code position
  inside `compile_driver`, O6/O7). The generated check sees declared stages, not statement order
  inside one function. The trigger for more is a defect traced to one (D77).
- Pairwise deny composition (§5) stays one-flag-at-a-time in `make test-axes`. A pairwise sweep over
  the "declared independent nowhere" pairs is a measurement to file, not part of this build.

## 9. Pointers

`src/facts/facts.def`, `src/facts/facts.c` (`pf_enter`), `src/facts/CLAUDE.md`;
`docs/design/patfacts/design.md` §3, §4.2, §4.5, §7, §11.4; `docs/design/start_table.md` §1.3, §3.3;
`docs/design/locate_finish.md` §2.5, §2.7; `docs/spec/facts_listing.md` §4.1, §4.1¶2;
`memfn/include/memfn.h` (`mf_site`, `mf_pred`); review 2026-11-12-r2-reqpast (EMIT-1/CON-3, TH-5);
`docs/dev/lanes/s1fix_report.md` on `lane/s1fix` (CHECKS-4, s1fix3); D120, D126, D157, D77.
