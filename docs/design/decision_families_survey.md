# Decision families still dispersed — a survey ("forest for the trees")

Lane `decsurvey`, 2026-10-06. READ-ONLY survey: nothing under `src/`, `cli/`,
`lib/` or `tests/` changes. No build was run. Line numbers are from
`lane/decsurvey` at `74379fe0`. The probes read stamps and `--emit-ir` output
from the main tree's `build/pcrec` (mtime 2026-10-06 11:48). They are
compile-only: no matcher was run and nothing was timed.

**Charter (Frank, 2026-10-06).** "We first incrementally build a related
decision set using various dispersed if/then or sub decision tables. It grows
until I explicitly ask for an evaluation on a consistent, generalized, unified
decision table... it makes me wonder what else is out there."

A **decision family** is several places in the compiler that each answer a
variant of ONE question, through if/else chains, ternaries, scattered
`(flags & PCREC_NO_X) && fact` conjunctions, small local tables or duplicated
cost comparisons, rather than through one ordered first-match predicate-row
table (memory `pcrec-decisions-as-first-match-tables`).

**Already unified or being unified (baseline, not re-surveyed):**

- start strategy (`where_to_start.md`, D151)
- engine-capability analyses (`analyses[]`, D124)
- the `DFA_SELECT` tables (`dfa_pfs[]`, `req_admits[]`, `req_uses[]`, `dfa_matches[]`, `dfa_search_starts[]`, `dfa_edges[]`, `dfa_reprs[]`/`views`/`seeds`/`accs`)
- `pcrec_reseed_rows[]`
- `TAB_ROWS[]` (clskit)
- `pcrec_runcmp_rows[]`
- `fit_rungs[]` ([ART-SIZE]/[PF-DROP])
- `pcrec_look_rows[]`
- the axes table (`src/core/axes.def`)
- `TUNE_TABLE`
- `limits.def`
- [OPT-SETS]' constraint table (design)

**Method.** Four sub-surveys read the tree:

- `emit_vm.c`
- `compile.c`/`select_engine.c`/`src/opt`
- `src/facts`/`src/ir`
- the stamp vocabularies in `docs/spec/tuning.md` and `match_api.md`, against their write sites

A fifth note covered `emit_dfa.c`/`clskit.c`/`runcmp.c`/memfn. I then
re-read every claimed inconsistency at its lines. Where it was cheap, I also
probed it with `build/pcrec`. `--list-axes`' `kind` column was the starting
lead: `list` means a real candidate table exists, and `predicate` means the
row is hand-stated over code. 37 of the 52 listed axes are `predicate`.

---

## 0. Answers first

**The ranking.** "Members" counts decision sites, not lines. "Ripe" means
≥3 dispersed members (Frank's pattern).

| # | family (the one question) | members | ripe | live/latent inconsistency | unified table natural? | value / risk | existing rows |
|---|---|---|---|---|---|---|---|
| 1 | **The fallback ladder**: what to do after a refusal, overflow or decline, and how it is reported | ~11 | yes | YES (§4.1 drift; §4.5 listing; §4.6 order) | yes: extend `fit_rungs[]` with the [SEL-1] rows, with stamp tokens as row columns | HIGH / medium | [SEL-1], [PF-DROP], [OPT-4], [LIST-TABLES] |
| 2 | **Which byte of the landmark to scan** (run reader vs offset-k pick vs pin vs set pick) | 6 pickers, 5 tie rules | yes | **LIVE, probed** (§4.2; beyond ties) | partly: it is a RANKING, not a first-match table. One ranking + one tie rule removes the identity clause | HIGH / medium (form movers) | [TIE-ALIGN] (ties only) |
| 3 | **Which rows/bits does a deny flag remove** (mask membership, deny→row maps) | ~7 | yes | **LIVE, probed** (§4.3: two bits unmasked, the K68 shape) | yes: a `kind` column in `axes.def` | HIGH / low | [AXES-DENY-MASK] |
| 4 | **Does this engine shape have a table walk / which route** (`ENG_ATTEMPT`/empty prelude, `mixed` folds) | 11 + 2 folds | yes | latent only (the attempt route bypasses `dfa_pfs[]`) | yes: an attempt route as candidate rows (D148's `cand_rows[]` rename) | medium / low | D148 rename |
| 5 | **Which rung a quantifier takes** (cursor/revdet/counter/frames × cost/count/emit) | 9 reads, 3 walkers | yes | none found (convention holds) | yes: `vm_rung_of()` first-match | medium / medium | [ENG-BREP] lineage |
| 6 | **How a WHY/form stamp gets its token** (the small ternaries) | 7 stamps | yes | **LIVE, probed** (§4.4 prune ceiling; §4.7 precedence) | yes: the token is the row's name | medium / low | [LIST-TABLES] |
| 7 | **Which bytes can begin / is the match anchored** (several derivations of one fact) | 4+1 first-byte, 3 start, 2 end | yes | none (one-way assertions; some twins deliberate) | NO: a fact-consolidation question, not a selection | low-med / medium | [PATFACTS] |
| 8 | **Is this fact derivable through construct K** (decline matrix) | 9 switches, ≥7 zero-width lists | yes | inconsistent REASONS (§3.8), no wrong answer | yes, as a per-`AKind` attribute table (not first-match) | medium (module growth) / low | — |
| 9 | **Effective limit and its crossing behaviour** | ~9 resolutions, 4 refusals, 4 overflow recorders | yes | none found | yes: a resolve accessor + a behaviour column on `limits.def` | low-med / low | [LIM-*] |
| 10 | **Does pass P run** (8 flag-gated passes, 3 gate placements) | 8 | yes | none found | yes: rows {pass, deny, applies} | low-med / low | — |
| 11 | **What a `--tune` position means** | 2 tables + prose | borderline | none found | belongs to [OPT-SETS]/[OPT-DIAL] | low now | [OPT-SETS], [OPT-DIAL], [EST-REGISTRY] |
| 12 | **VM entry shape + tiering** | 2 chains, coupled | no (2) | none | yes, small | low / low | — |
| 13 | **Class read-form plumbing** (after clskit's table chose) | 4 sites + 1 direct flag | borderline | latent (§3.13) | partly | low / low | [CLS-TREE] |
| — | request-contradiction refusals (5 sites, 2 files) | 5 | yes | — | ALREADY DESIGNED: [OPT-SETS] §2.7's constraint table | — | [OPT-SETS] |

**Which to evaluate first** (§6 has the rows):

1. **Family 3 first.** It is a live defect-shaped finding on an already-filed
   row, and the evaluation is one question to the owner: are bits 18/21 left
   unmasked on purpose? If not, [AXES-DENY-MASK] has its third incident.
2. **Family 1 next.** It is the biggest, the most caller-visible (four WHY
   stamps, one contract vocabulary) and holds the one real code drift.
3. **Family 2 third.** It needs [TIE-ALIGN]'s STEP 0 bench reading, re-scoped
   to the non-tie disagreement shown here.

This survey is also, de facto, most of [LIST-TABLES]' STEP 0 census ("any
selection NOT yet a table — the spiderweb Frank named").

---

## 1. Lead sources and how each was used

- **`--list-axes` `kind`.** Every `predicate` axis with more than 2 candidates
  is a hand-stated ladder over code: `engine-route` (8), `size-term` (7),
  `hyb-reseed` (6, a real table but not listed as one), `req-admit` (5),
  `run-overlap` (4), `vm-anchor-bound` (3), `startpos-guard` (3) and
  `utf-check` (3).
- **Stamp vocabularies.** Each stamp is classified as TABLE (a row's name),
  CODE (a ternary or switch at the emit site), FACT (`pcrec_fact_stamp`) or
  NUMBER. The CODE stamps are:
  - `ENGINE_SEL`
  - `ENGINE_WHY`
  - `UNROLL_K_WHY`
  - `VM_PREFILTER`, `VM_PREFILTER_WHY`, `VM_PREFILTER_LANG`, `VM_PREFILTER_LANG_WHY`
  - `VM_PRUNE_CEILING`
  - `STARTPOS_GUARD`
  - `UTF_CHECK`
  - `DFA_SCAN`
  - the `ENG_ATTEMPT` arm of `DFA_PREFILTER`/`_OFFSETS`
  - the `none`/`mixed` compositions of `DFA_TABLE`/`DFA_SCAN_EDGE`
  - the `REQ_WHY` alias switch
- **`PCREC_NO_` reads outside row `.deny` columns.**
  - `compile.c`: 12
  - `select_engine.c`: 4
  - `src/opt` passes: 6
  - `emit_vm.c`: 13
  - `clskit.c`: 3
  - `facts.c`: 1
  - `ctxnode.c`: 1 (a row deny)
- **Repeated conjunctions,** found by reading. They are cited per family below.

---

## 2. What makes a family "natural" vs "forced" for a first-match table

- **Natural:** the members answer with a NAME from a closed vocabulary, the
  conditions are ordered and mostly disjoint, and a deny bit removes a row.
  Families 1, 3, 4, 5, 6, 10 and 12 are natural.
- **Forced:** the members compute a VALUE by ranking (family 2), or derive a
  FACT several ways (family 7). Here unification means one ranking function
  or one derivation, not a row table. Folding them into rows would build a
  planner, which [ENG-TACTICS] rules out.
- **Attribute table:** family 8 is a per-kind property table that every walk
  reads. It is not a selection.

A **no-mover refactor** keeps every artifact byte-identical
(`scripts/emit_sweep.py`, 0 movers) and every `--list-*` output unchanged. The
exceptions are the rows the refactor deliberately adds, re-pinned as D94
requires. Each family section says what that needs.

---

## 3. The families

### 3.1 The fallback ladder — "the attempt failed or declined; what next, and what do we call it"

**The question.** After a DFA overflow, an emitted-size cap refusal, a
nullable decline or a forced engine, which rung runs next, and which token
does each WHY stamp carry?

**Members.**

| site | how it decides today |
|---|---|
| `compile.c:1277-1300` [SEL-1] overflow retry | AD-HOC booleans `ovf_eligible`/`retry_collapse`/`retry_drop`. These are two rungs (collapse, drop the prefilter) shaped exactly like `fit_rungs[]` rows. They re-read `PCREC_NO_PREFILTER_COLLAPSE`, `PCREC_FORCE_PREFILTER` and "engine is auto", which the table rows also read. `--fast-or-fail` does not apply to them, though both rungs degrade run time (consistent with `limits.md`, but nowhere reconciled). |
| `compile.c:723-731` `fit_rungs[]` + `fit_select` | the size-cap ladder, ALREADY A TABLE (unroll-rescue, prefilter-collapse, drop-anchored, drop-premul, drop-prefilter, refuse) |
| `compile.c:681-689` `fit_collapse_applies` | the collapse rung's predicate (§4.1: it lacks the gate's conjuncts) |
| `compile.c:1800-1835` the collapse build gate (`pfc_wanted`, `collapse`) + `prefilter_lang_why` 5-way ternary | the REAL collapse gate, and the LANG_WHY verdict |
| `select_engine.c:~690-866` `prefilter_decision` | the nullable declines (`declined_nullable`, `_default`), `force_off`, the drop on `dfa_disabled` |
| `select_engine.c:943-976` `esel_of` | an 8-arm ternary over side flags written in 4 places (the `ENGINE_SEL` token). The `internal.h:2264-2290` enum ORDER is load-bearing (`>= ESEL_OVERFLOWED_DFA` means "any fallback"). |
| `compile.c:1977-1984` `size_term_why` | a 7-arm ternary (`UNROLL_K_WHY`) |
| `compile.c:350-385` `build_anchored_dfa` | a fourth reader of the drop state (`size_drop_rung >= SDR_NO_ANCHORED`), which saves and restores `dfa_overflowed` |
| `emit_vm.c:11222-11326` | `VM_PREFILTER` ternary, `VM_PREFILTER_WHY` (conditional on `size_drop_rung`), and the `VM_PREFILTER_LANG_WHY` switch over the PFLW codes |
| `emit_vm.c:9387-9484` `--emit-ir` "prefilter" row | a 9-arm first-match chain, its own second derivation of "why no prefilter" (§4.5) |
| `emit_vm.c:9312-9315,9474` | `ENGINE_WHY` text for the [SEL-1] case |

**Disagreements.** Three:

- §4.1: the collapse predicate drifted from its gate.
- §4.5: the listing chain does not know [PF-DROP].
- §4.6: the registry's `engine-route` order is not the code's order.

There is also a structural duplication: "drop the prefilter" has TWO
mechanisms with two stamp vocabularies.

- [SEL-1] rung 2 sets `dfa_disabled` with `CR_NONE` and stamps `overflowed-*`.
- [PF-DROP] ORs `PCREC_NO_PREFILTER` and stamps `size-cap-retry` plus
  `VM_PREFILTER_WHY`.

**Natural table?** Yes. Make `fit_rungs[]` the ONE ladder, keyed by the
failure label (`dfa_overflowed` | `size_cap_refused` | none). The [SEL-1] rows
join it with their own `applies` and deny bits. Each row then carries its
`ENGINE_SEL`/`*_WHY` tokens as columns. `esel_of` and the PFLW ternary become
reads of "which row fired", not reconstructions from side flags. The `kind`
in `--list-axes` would flip `engine-route`, `size-term` and `prefilter-lang`
from `predicate` to `list`.

**Interactions.**

- [SEL-COST]'s design of record (`sel_cost.md` §4) already plans post-build
  rows "through [SEL-1]'s retry". It should land INTO this table, not beside
  it.
- `--fast-or-fail`'s reach becomes a visible column.

**No-mover needs.**

- Token identity: `ENGINE_SEL`/`UNROLL_K_WHY`/`LANG_WHY` are contract
  vocabularies in `match_api.md` §6.3.
- The attempt COUNT and the attempt ORDER must not change. The §4.1 drift
  fix is NOT a no-mover: it removes a wasted attempt, so compile time moves,
  but no artifact does.
- A census of `RX_ENGINE_SEL` over the corpus before and after.

**Value / risk.** HIGH: it is the largest closed caller-visible vocabulary
family, and three disagreements are already in it. Risk is MEDIUM. The retry
loop is the compiler's one `setjmp` recovery point, with `COMPILE_MAX_ATTEMPTS`
arithmetic (`compile.c:479`) that counts rungs by hand.

### 3.2 Which byte of the necessary landmark the scan tests

**The question.** Given a necessary run or set and the offset-k walk, which
byte at which offset does the memchr test, and which run positions are
verified?

**Members** (one rate source and one argmin primitive underneath:
`pcrec_find_byte_rate`, `pcrec_find_pick`, `findings.c:391/433`):

| site | ranking | tie rule |
|---|---|---|
| `req.c:425-451` `rn_better` (which run) | INFORMATION bits, no rarity | leftmost |
| `findings.c:518` `pcrec_find_run_scan_index` (run scan member) | rarity over ALL positions incl. caseless cubes | RIGHTMOST |
| `kset.c:251-277` `pcrec_run_pin` (pinned stretch) | rarity over EXACT positions only | rightmost |
| `prefix_k.c:179-326` `pcrec_prefix_ksets` (offset-k scan) | COST MODEL (`C_MEMCHR`/`C_BITMAP`/`C_VERIFY`/`C_ENTER`/`C_MISPRED` constants) over per-offset ppm | LEFTMOST (strict `<`) |
| `findings.c:476` `pcrec_find_set_pick` via `req.c:677` | rarity | rightmost threaded, else largest byte (`rb_intersect`, a third rule) |
| `emit_dfa.c:7170/7210` dominated / set-leads | rarity compare | tie → elide / tie → keep run |

**How they are reconciled.** By an identity clause, not by a shared choice:
`pf_run_applies_common` (`emit_dfa.c:6023-6040`) DECLINES `run-pinned` unless
the pin's scan offset equals the offset-k model's scan offset. §4.2 probes it:
the clause fails on ties AND on plain rarity-vs-cost-model disagreements.

**Natural table?** No, it is a ranking. The general form is ONE landmark-
candidate ranking (offset range, byte or cube, rate, information) with one
tie rule. The run reader and the offset-k pick become two reads of one
choice, and the identity clause disappears. `where_to_start.md` §1.4 orders
ROWS by information and admits by rarity. This family sits one level below
that: the pick INSIDE a row. D151 does not cover it.

**Interactions.**

- [TIE-ALIGN] (filed 2026-09-29) owns the TIE half and measured 48 of 165
  movers.
- [EST-REGISTRY] owns `prefix_k.c`'s cost constants (memory
  `pcrec-suspect-tuning-constants`).
- [U8-PICK] may be a further instance on utf8.

**No-mover needs.** None: unifying the pick MOVES prefilter forms by
construction. Every result is answer-identical, but form movers need the
bench (D119's measured-gap bar).

**Value / risk.** HIGH, because the run-pinned row (one compare per
candidate) is silently unreachable on common shapes. MEDIUM risk: a perf
movement only, and it needs bench evidence.

### 3.3 Which rows/bits a deny flag removes

**The question.** For flag F, which candidate rows does it remove, and is F
recorded in `rx_info.flags`?

**Members:**

- `emit_dfa.c:2808-3097` `strategy_denials`, a hand-kept OR of about 30 bits
  with a comment per bit (PRE-FIX SNAPSHOT: since K92, abi 65, the mask is
  DERIVED from `core/axes.def`; only the `kept` set is hand-listed).
- Every table row's `.deny` column (`dfa_pfs[]` etc.).
- `clskit.c:835` `DENY_FLAG[]` / `pcrec_clskit_deny_of`, the "ONE mapping"
  per its comment.
- `clskit.c:882` `pcrec_clskit_tabdeny_of`, a second hand mapping
  (`NO_CLS_PACK|NO_CLS_KIT` → ATOM).
- `emit_vm.c:1529` `vm_wcls_bytes`, which reads `PCREC_NO_CLS_KIT` DIRECTLY
  (a third path, with a different deny set from `tabdeny_of`).
- `emit_vm.c:4415`, the island emitter reading `PCREC_NO_LIT_RUN` directly
  instead of through `vm_lit_run`.
- `src/dump/axes_dump.c`'s hand-stated `predicate` rows.
- `tune.c:68`'s deny cell.

**Disagreement.** §4.3: bits 18 and 21 are unmasked on artifacts they cannot
act on.

**Natural table?** Yes, a `kind` column in `axes.def`:
`strategy` (masked) / `engine-selecting` (kept, the documented shape of
`atomic-discharge` and `splice-calls`) / `contract` / `instrument`. The mask
is then derived. That is [AXES-DENY-MASK] exactly, and [OPT-SETS] §2.8 wants
the same column.

**No-mover needs.** Byte identity everywhere except the corrected bits.
Per D76/D94, a corrected bit moves `rx_info.flags` text, so it is an abi
event.

**Value / risk.** HIGH and cheap, LOW risk.

### 3.4 The engine-shape prelude — "is there a table walk; which route"

**The question.** Is this artifact's scan the unanchored table walk, the
`ENG_ATTEMPT` label dispatch, or provably empty? Which candidate route
applies?

**Members:** 11 `PCREC_ENG_ATTEMPT` tests in `emit_dfa.c`.

- `dfa_table_name` 4385-4386 and `dfa_scan_edge_name` 4457-4458 open with the
  same two lines VERBATIM.
- `dfa_scan_name` 10381.
- `dfa_prefilter_name` 10393, where the attempt route hard-branches
  `attempt_cand(...) ? "memchr" : "none"` and NEVER reaches `dfa_pfs[]`.
- `dfa_prefilter_offsets` 10405.
- Further sites at 4518, 6656, 7039/9323/9997/10411/10483 (`attempt_cand`
  readers), 7338, 7428, 7865 and 9176.

Also:

- the `mixed` per-artifact folds (`dfa_table_name` 4383, `scan_edge_of` 4434),
  which re-spell the pinned/unwrapped machine census;
- `compile.c:1876/1914` choosing `ENG_UNANCH` vs `ENG_ATTEMPT`.

**Disagreement.** None found. Latent: the attempt route is a PARALLEL
MECHANISM for "which prefilter". It reports under the same macro with 2 of
the 12 values, chosen outside the table (CLAUDE.md situation index: "add a
parallel mechanism").

**Natural table?** Yes. `CAND_ROUTE_ATTEMPT` rows in `dfa_pfs[]`, the route
idiom START-SET already uses for `CAND_ROUTE_VM`. Plus one machine-census
helper (which machines exist: forward / reverse unless pinned / anchored
when unwrapped) that every fold reads. It slots into D148's scheduled
`dfa_pfs[]` → `cand_rows[]` no-mover rename (D151 Q5).

**No-mover needs.** Fully achievable: same tokens, same text.

**Value / risk.** MEDIUM / LOW.

### 3.5 The VM rung ladder per quantifier

**The question.** Which strategy does this `A_REP` take: cursor, revdet,
counter, or frames (bounded/unbounded)?

**Members.** Three walkers, each re-deriving the ladder by convention (the
comment at `emit_vm.c:1265-1277` says so):

- `vm_cost_rep` 2362-2365 / 2446 / 2499
- `vm_count_slots_rep` 3017 / 3046 / 3075
- `vm_rep` 6351 / 6379 / 6388

Around them:

- `PCREC_NO_COUNTER` is read three times (2364, 3075, 6388).
- Cursor has no deny.
- Revdet's deny is upstream (`select_engine.c:509-514`, beside possessify's
  `:487-492`, the identical `chosen != VM || NO_X` gate).
- The stamp bits are set per emitting function (`vm_rung_mark`, 4760/5534/
  6155/6419), not from a selector.
- The copy formula is spelled twice (`vm_counter_copies` 1298/1313 vs
  3092-3095).

**Disagreement.** None found. The A1 arm asymmetry (counter re-tests cursor
and revdet; revdet tests only cursor) is order-correct.

**Natural table?** Yes. `vm_rung_of(v, a, under_atomic)` as first-match rows
{name, deny, fits, stamp bit}, with three switches over its answer. The
registry's `revdet`/`counter`/`possessify`/`length-prune` rows would become
`list`.

**No-mover needs.** Byte identity is achievable. The `under_atomic` threading
must be preserved.

**Value / risk.** MEDIUM: the next rung costs one row instead of three arms
plus cost arithmetic. MEDIUM risk: it is the VM's core.

### 3.6 Stamp-token derivation (the small ladders)

**The question.** Given what the emitter did, which token does stamp S carry?

**Members:**

| stamp | derivation | site |
|---|---|---|
| `UNROLL_K_WHY` | 7-arm ternary; `option` precedes `denied` (§4.7) | `compile.c:1977` |
| `VM_PRUNE_CEILING` | `nclamp==0 ? none : mrl_win ? prefilter-window : subject-end` | `emit_vm.c:11642` |
| `--emit-ir` `prune-ceiling` | `!mrl ? none : mrl_win ? ...` (§4.4) | `emit_vm.c:9581` |
| `STARTPOS_GUARD` | nested ternary + a TEXT probe (`*pcrec_startpos_guard_text(...)`) | `emit_dfa.c:10053` |
| `UTF_CHECK` | ternary | `emit_dfa.c:10065` |
| `REQ_WHY` | table walk, then the `req_why_name` switch aliasing `set-leads`→`emitted` | `emit_dfa.c:7288` |
| `REQ_HANDOFF` | table row + a hand stamp | `emit_dfa.c:7376/7389` |
| `VM_PREFILTER` | `fit.prefilter` (stamp) vs `v->emitted_prefilter` (listing) | `emit_vm.c:11222` / `12757` |

"Is there a window ceiling" has three predicates across 6+ readers: `!v->mrl`,
`v->nclamp == 0` and `v->mrl_win` (`emit_vm.c:9581, 11642, 13294, 13427`).

**Natural table?** Yes. When the decision is a row, the token is the row's
`name`. Where it already is a table (`REQ_WHY`), the alias switch is a second
hand decision. Either add a `stamp` column (the `.stamp` override
`dfa_pfs[]` already uses at `emit_dfa.c:7966`), or rule the 4-token
vocabulary a verdict class. This is the per-artifact half of [LIST-TABLES].

**No-mover needs.** Token identity per stamp. The §4.4 fix is a listing-text
mover only (a DEBUG surface).

**Value / risk.** MEDIUM / LOW.

### 3.7 One fact, several derivations: first bytes, start/end anchoring

**First-byte set:**

- `start_set` (`startset.c`, AST, erased superset)
- `kset_walk` k[0] (`kset.c:197`, NFA closure)
- the DFA start state's escape set (`cand_from_escapes`, `emit_dfa.c:4062`; `cand_from_live_seeds` :4084)
- `possessify.c:175 first_of` (code points, deliberately separate per `startset.c`'s header)
- the K50 check (`nfa.c:1100`, assertion-only)

**Start-anchored:** the AST fact (`startanch.c`), the DFA interior-dead pair
(`emit_dfa.c:~9340-9385`, asserted one way), and `attempt_cand`'s own loop
(`emit_dfa.c:~4106`).

**End-anchored:** the AST `ew_walk` (`endwin.c`) vs the DFA's `\z`/`$` view
(`dfa.c:~1516`), with NO assertion tying them.

**Natural table?** No. This is a fact-consolidation question. Several twins
are DELIBERATE cross-checks (W7 in the sub-survey: the gate vs
`cstart_check_omission`), and `prefix_k.c:127-170` documents why roles A and
B differ (MISCOMPILE-1).

The evaluation question is narrower: should end-anchoring get the one-way
assertion that start-anchoring has?

Value low-medium. The risk is in changing derivations, so this one is
evaluation-only.

### 3.8 The fact decline matrix — "does fact F see through construct K"

Six AST fact walks plus the width recurrences each hand-list the zero-width
kinds (EMPTY BOL EOL END CTX GSTART KRESET LOOK). That is ≥7 copies, in
`startanch.c`, `endwin.c`, `startset.c`, `req.c`, `mrl.c` ×4, `ctxnode.c` and
`nfa.c`.

Treatment of the same construct differs, and the stated reason is the same:

- **Spliced (acyclic) call.** Declined by all four AST facts (`start_anchor`,
  `start_set`, `end_window`, req), each citing "the callgraph cycle problem /
  D77". `kset_walk` handles it via the NFA.
- **Lookaround.** Erased by `start_set` (superset); skipped by
  `start_anchor`/`end_window` (each "could pin, no consumer"); breaks run
  contiguity in req (`rr_none(0)`); epsilon in `kset_walk`. Four treatments.
- **Structured reasons.** Only `end_window` reports them
  (`facts.c pf_done_why`); the other facts say only "none".

**Natural table?** Yes, a per-`AKind` attribute row {zero_width, transparent,
consumes, opaque_to_ast_facts} that the walks read. It is not first-match.
The exhaustive no-default switch stays as the alarm, and a new module adds
one row instead of ≥7 arm groups.

No wrong answer was found: every divergence errs toward declining. Value
MEDIUM for module growth ([OPT-SETS], UCP, new constructs). LOW risk if the
refactor is no-mover: every fact value stays identical, checkable with
`--emit-facts` over the corpus.

### 3.9 Effective limit and its crossing behaviour

**Value resolution.** `limits.def` single-sources the VALUES. Resolution
(`0` = built-in default, clamp, raise-only) is per site:

- the effective emit cap at `compile.c:1141, 1239, 1241, 2028, 2031`,
  `emit_dfa.c:10587`, `emit_vm.c:11405`;
- the goto and subset caps at `compile.c:1921` and `dfa.c:1291/1306`;
- `dfamemo.c:77-79` compares the raw option fields as the memo key, a
  hand-listed "inputs of the DFA build".

**Crossing behaviour** is also per site:

- four `dfa.c` overflow recorders (ctx decline ~203, state cap 1248, N1
  budget 1315 — the only one that sets `is_budget` — and K7 subset 1330);
- four `emit_vm.c` refusal compares (894, 3135, 10530, plus the caps enforced
  in `compile.c`);
- the runtime `R_*` → `PCREC_ERR_*` propagation, repeated per entry shape
  (`emit_vm.c:13500-13512`).

No disagreement was found. **Natural?** Yes: one `pcrec_limit_effective(id)`
accessor, and a `behaviour` column on `limits.def`
(refuse / decline-to-fallback / give-up / steer). The overflow recorders
become one helper taking a reason code. Value low-medium, LOW risk.

### 3.10 Does optimization pass P run

Eight flag-gated passes use three gate placements:

- **inside the pass:** altcls ×2, atomic, callgraph splice, scanedge ×2;
- **in the caller:** possessify and revdet (`select_engine.c:487-514`), the
  anchored DFA (`compile.c:350-354`);
- **via a drop-state flag OR'd into the options:** premul and prefilter
  (`compile.c:1453/1467`).

Rows {pass, deny, applies(chosen, ...)} fit all eight. Value low-medium: it
makes "which pass ran" listable. LOW risk.

### 3.11 What a `--tune` position means

The meaning is split three ways:

- `tune.c` `TUNE_TABLE` holds the bar, threshold, inline-chain max and deny
  mask.
- `clskit.c` holds its own per-position row masks (`TPOS`, 524-596), the
  largest consumer.
- `axes_dump.c:135-136` restates "size-leaning −2/−1 only" in prose.

[OPT-SETS] already re-expresses the dial as five pinned members (§4 there),
so this family is owned. It is listed so it is not re-discovered.

### 3.12 VM entry shape + tiering (2 members, not ripe)

`vm_plan_entry` (`emit_vm.c:~10895-10962`) is an AUTO chain followed by a
legality clamp that silently coerces an explicit `--vm-entry-shape`. The
tiered entry (`10699-10725`) feeds `may_fwd` into it, a coupling visible only
by reading both. It is a small first-match candidate, worth folding when a
third entry decision appears.

### 3.13 Class read-form plumbing (after clskit chose)

`vm_cls_tables` (`emit_vm.c:1784-1799`) re-selects with read counts obtained
by SCANNING EMITTED TEXT, then maps form→read spelling with a 3-arm chain.
`vm_cls_inline` (1507) is a predicate on the chosen form, and the stamps
count form slices by hand (1583/1590/11504/11510).

The latent case is in §3.3: `vm_wcls_bytes` (1529) tests `NO_CLS_KIT` only,
while `tabdeny_of` treats `NO_CLS_PACK|NO_CLS_KIT` together. I did not
construct an input that splits them. Low value.

---

## 4. Latent and live inconsistencies

These are the most valuable findings: concrete inputs on which two sites
answer one question differently. **PROBED** means observed with
`build/pcrec`. **READ** means confirmed at the lines and not executed.

### 4.1 The collapse rung's predicate is not its gate (READ)

The comment at `compile.c:~1334-1340` says: "THE CONJUNCTS
(`fit_collapse_applies`) ARE THE GATE'S, RESTATED ONLY TO AVOID A POINTLESS
ATTEMPT: no rung for a pattern with nothing to collapse".

`fit_collapse_applies` (`compile.c:681-689`) tests none of that:

```c
return s->collapse_reason != CR_SIZECAP && j && j->fit.chosen != ENGM_DFA &&
       j->fit.prefilter && !j->fit.prefilter_collapsed;
```

The real gate (`compile.c:1807-1823`) requires `pfc_rep`
(`PF_KIND_COLLAPSIBLE_REP`), and the collapse itself requires `!nullable`
unless forced. The [SEL-1] twin `retry_collapse` (`:1280-1282`) omits
`pfc_rep` too.

**Input shape.** A VM hybrid with a prefilter, over an emitted-size cap, with
NO collapsible counted repeat. `fit_select` takes FIT_COLLAPSE, the driver
sets `CR_SIZECAP` and restarts the size term, and the rebuild declines the
collapse (`PFLW_NO_REP`). Unroll has nothing to act on without a counted
repeat, so it emits the same artifact, which is refused again. Only then is
the next rung reached. The cost is one wasted full compile, and the comment
claims the opposite.

The shipped caps are raise-only from the CLI, so this needs a naturally
>1 MB hybrid or a lowered-cap reference build. It was not executed.

### 4.2 Run-pinned is unreachable whenever the run reader and the offset-k pick disagree, ties or not (PROBED)

Default flags, DFA artifacts:

| pattern | `REQ_RUN` (scan idx) | offset-k scan | `DFA_PREFILTER` | `REQ_WHY` |
|---|---|---|---|---|
| `\d\dzq` | `7a71@0` (z at offset 2) | 2 | **run-pinned** | dominated |
| `\d\dzz` | `7a7a@1` (z at offset 3, rightmost tie) | 2 (leftmost tie) | offset-set | emitted |
| `\d\dxyz` | `78797a@2` (z at offset 4, rarest) | 2 (x, cost model) | offset-set | emitted |
| `[0-9][0-9]hello` | `...@3` (second l, offset 5) | 4 (first l) | offset-set | emitted |
| `\d\dzzzz`, `\d\dqqqq`, `\d\dxyzxyz`, `\d\dabab` | rightmost | leftmost | offset-set | emitted |

`\d\dzq` shows the row works when the two pickers coincide.

`\d\dxyz` is NOT a tie. The run reader picks by rarity, `prefix_k` by its
cost model, and they choose different bytes. [TIE-ALIGN] as filed ("on
tied-rate run bytes the two disagree") under-states the family. Aligning tie
rules alone leaves this case.

The consequence is a form movement, not an answer change. The whole-run
single compare is replaced by an offset-set verify plus a separate run
pre-check pass (`REQ_WHY emitted`, where `run-pinned` would have made it
`dominated`).

### 4.3 Two strategy deny bits are unmasked in `rx_info.flags` (PROBED)

On `abc` (a DFA artifact with no counted run, and no VM so no size term):

- `-fno-scan-edge` moves `.flags = 0ULL` to `2097152ULL` (bit 21).
- `-fno-size-term` moves it to `262144ULL` (bit 18).

Byte-identical on the same input:

- `-fno-view-edge`, the view-tolerant HALF of the scan edge, which is masked
  with the comment "masked so an artifact it does not reach is byte-identical
  under the flag" (`emit_dfa.c:3051-3057`);
- `-fno-start-set`, `-fno-req-handoff`, `-fno-start-pinned`, `-fno-cls-kit`,
  `-fno-req-set-lead`, `-fno-ctx-node` and `-fno-hyb-reseed`.

`lib/pcrec.h` documents both bits as answer-identity-preserving ("It changes
no answer either way" at `PCREC_NO_SCAN_EDGE`). Neither has a comment
justifying exclusion from the mask. That is the K68 / bit-19 incident shape
[AXES-DENY-MASK] was filed on. The bits engine-selecting flags keep
(`-fno-splice-calls`, `-fno-atomic-discharge`) are documented as deliberate.

The owner should confirm intent. If it is not deliberate, this is
[AXES-DENY-MASK]'s third incident. Fixing it moves `rx_info.flags` text only
under those flags, so it is an abi event per D76/D94.

### 4.4 `--emit-ir`'s `prune-ceiling` row vs the `VM_PRUNE_CEILING` stamp (PROBED)

The listing row's comment (`emit_vm.c:9571-9579`) says it uses "the same
three words the stamp uses, so the stamp and the listing are comparable by
EQUALITY". With `--engine=vm`:

| pattern | listing | stamp |
|---|---|---|
| `a*` | `subject-end` | **`none`** |
| `b*c`, `a(b\|c)+d`, `x[a-z]{2,5}y` | `subject-end` | `subject-end` |

The listing tests `!v->mrl` and the stamp tests `v->nclamp == 0`. A pattern
with the pass on but no clamp (`RX_VM_PRUNES 0x2u`) splits them.
`tests/codegen` rule 1(d) compares only the `prefilter-window` direction
(`run_codegen_tests.sh:2197-2255`), so this direction is uncovered.

It is a DEBUG surface (D26 tier), but it is exactly what the row claims to
prevent. A third predicate for the same question gates `window_end` emission
(`13294` unconditional on `mrl_win`, `13427` on `nclamp`).

### 4.5 The `--emit-ir` "prefilter" reason chain does not know [PF-DROP] (READ)

`emit_vm.c:9476-9480` reports `no-fno-prefilter` ("-fno-prefilter -- forced
off") whenever `cx->opt->flags & PCREC_NO_PREFILTER`.

The [PF-DROP] rung ORs exactly that bit into the retry's options
(`compile.c:1467`). The listing path runs inside the same retried compile
(`want_ir` threads through `compile_driver`), so a hybrid dropped for size
would be described as a flag the caller never passed. The stamp side gets it
right (`VM_PREFILTER_WHY`, keyed on `size_drop_rung`, `emit_vm.c:11229`).

The chain's own header (9380-9384) states that it exists to avoid naming a
route no flag explains. Reachability is the same as §4.1 (a >1 MB hybrid or a
lowered-cap build).

### 4.6 `ENGINE_SEL`'s listed order is not its evaluated order (READ)

`--list-axes` lists `engine-route` rows in "PREFERENCE order (order 1 is tried
first)":

1. forced
2. declined-nullable-default
3. collapsed-prefilter
4. declined-nullable
5. overflowed-dfa
6. overflowed-prefilter
7. size-cap-retry
8. selected ("always (fallback)")

`esel_of` (`select_engine.c:965-976`) evaluates them in a different order:

1. forced
2. declined-nullable-default
3. declined-nullable
4. size-cap-retry
5. **selected**
6. collapsed-prefilter
7. overflowed-dfa
8. overflowed-prefilter (the true fallback)

The arms are disjoint on `dfa_disabled`, so no artifact gets a wrong token
today. Still, the registry states an order and a fallback reason the code
does not have. The registry's own `kind` column calls this axis `predicate`,
which is the root cause.

### 4.7 `UNROLL_K_WHY` precedence is implicit (PROBED)

`--unroll=8 -fno-size-term --engine=vm` gives `RX_UNROLL_K_WHY "option"`. The
ternary tests `option` before `denied` (`compile.c:1978-1979`), so the denial
leaves no trace. That is defensible (the term never runs under `--unroll`),
but tuning.md §2.16 lists the seven values with no precedence. A first-match
table makes the order the contract.

### 4.8 Near-misses (no split input constructed)

- **The start-set usability predicate is spelled twice.**
  `pf_dfa_start_set` (`emit_dfa.c:6658-6666`: `nt >= 256`, then `nt == 0 ||
  !proper`) vs `pf_vm_start_applies` (6812-6818: `n >= 256` only; it admits
  `n == 0`, which is sound since the seek finds nothing and the result is
  `return 0`). The spec states the predicate four ways (tuning §2.42,
  match_api ×2, registry).
- **`DFA_PREFILTER` "none" and `REQ_WHY` "one-attempt"** both read "the route
  tries exactly one start". Two stamps plus `VM_START` give three readings of
  one fact.
- **Stale spec prose.** tuning.md §3 says `DFA_PREFILTER` has five values
  (twelve today) and lists `DFA_SCAN_EDGE` without `fold`/`kit`, and
  match_api says "the same five values". This is spec drift, not code; it is
  listed so the D80 owner sees it.

### 4.9 Late additions (first-round sub-surveys, delivered after commit; READ, not re-verified)

- **Two retry rules gate a forced engine differently** (family 1). The [SEL-1] overflow retry requires `engine == AUTO` (`compile.c:1277`), so a forced `--engine=dfa` that overflows REFUSES. The `fit_rungs[]` size-cap rungs carry no engine conjunct, so the same forced build over an emit cap DEGRADES (drop-premul, drop-anchored) and stamps `forced`. This can be read as intentional (no rung changes the engine), but no one place states it. The unified ladder should carry it as a column.
- **The scan form of a byte set** (one byte → memchr, several → table) is spelled at about 5 sites: `cand_derive` (`emit_dfa.c:4056`), `prefix_k.c:204/223`, and the `count == 1` arms near `emit_dfa.c:6069-6286`. This is a small family, and it belongs to the [MEMFN] delegation surface (D146) rather than to a new table.
- **One width recurrence in two units**: `req.c`'s `RbRuns.maxw` is a saturating BYTE width ("NOT cwmax"), while `mrl.c`'s `cwmax` counts CHARACTERS, and `endwin.c:171` relies on the two being equal under a single-byte encoding. This sits beside §3.7/§3.8 as a [DEC-KINDATTR] question.

---

## 5. Cross-cutting observations

1. **Stamps that mix "which form" with "why".**
   - `ENGINE_SEL` carries provenance, rung and policy decline in one token.
   - `DFA_PREFILTER` carries form × bounded. `-bounded` is a context test on
     four rows but a CONSTANT on the start-set pair ("a seeded machine always
     carries the D11 bound").
   - `UNROLL_K_WHY` mixes did-not-run reasons with ran-outcomes.
   - `*_LANG_WHY`/`VM_PREFILTER_WHY` are open vocabularies (reason plus
     measurement).

   A row table with `name` + `why` columns would separate these. Whether to
   re-vocabulary is a contract question for Frank (D80). A no-mover refactor
   keeps today's tokens.
2. **Shared macros hide decisions.** `RX_REQ_RUN` carries both `req-run` and
   `req-run-fold`. `RX_DFA_SCAN_EDGE` carries `scan-body`, `view-edge` and the
   scan-edge deny. `RX_DFA_PREFILTER` and `RX_VM_START_SCAN` split one table
   by route. Four deny flags (`-fno-req-run-fold`, `-fno-view-edge`,
   `-fno-req-set-lead`, partly `-fno-scan-edge`) have no distinguishing token.
   This is [LIST-TABLES]' "which row fired" question (its O-74 note:
   `iso-ts`' program moved with none of the six bench-read stamps moving).
3. **The registry's `stamp_value` column is part real token, part row label.**
   Examples: `req-run-fold`'s `cube`/`exact`, `req-use`'s
   `scan-from-startpos`, `view-edge`'s rows. A reader cannot tell which per
   axis.
4. **Every `predicate` axis is a family member by definition.** The axis
   registry already enumerates this survey's population. Flipping `kind` to
   `list` is the measurable completion criterion for each family.

---

## 6. Proposed evaluation rows (filed, not scheduled — D137 shape)

These are ready to paste into `docs/dev/plan.md`. Each is an EVALUATION:
design + census, no build. Builds follow a ruling.

- **[AXES-DENY-MASK] (existing) — ADDENDUM, evaluate FIRST.** "2026-10-06
  decsurvey §4.3: bits 18 (`-fno-size-term`) and 21 (`-fno-scan-edge`) move
  `rx_info.flags` on `abc` while their siblings (`-fno-view-edge`) are masked.
  STEP 0: owner confirms deliberate or not. If not, this is the third incident
  and the row's gate (run_prechecks §6 generalised over the registry) would
  have caught it."
- **[DEC-FALLBACK] STATE:not-started (FILED 2026-10-06, decsurvey §3.1;
  UNSCHEDULED)** — ONE FALLBACK LADDER. Evaluate folding [SEL-1]'s two
  overflow rungs into `fit_rungs[]` (keyed by failure label), with each row
  carrying its `ENGINE_SEL`/`UNROLL_K_WHY`/`*_LANG_WHY`/`VM_PREFILTER_WHY`
  tokens, so `esel_of` and the PFLW ternary read "which row fired".
  - STEP 0: census `RX_ENGINE_SEL`/`*_WHY` over the corpus, plus the attempt
    count per compile (to size §4.1's wasted attempts at a lowered-cap
    reference build).
  - Includes §4.1 (predicate ≠ gate), §4.5 (listing vs [PF-DROP]) and §4.6
    (registry order).
  - Contract question for Frank: keep today's tokens (no-mover) or separate
    name/why.
  - Interacts with [SEL-COST] §4 (its post-build rows land here) and
    `--fast-or-fail`'s reach.
- **[TIE-ALIGN] (existing) — RE-SCOPE ADDENDUM.** "decsurvey §4.2: the
  identity clause also fails WITHOUT a tie (`\d\dxyz`: rarity picks z@4, the
  cost model x@2). The question is one landmark-byte ranking across
  `run_scan_index`/`run_pin`/`prefix_ksets`/`set_pick`, not one tie rule.
  STEP 0 unchanged (the bench speed of the movers) plus a mover census of the
  non-tie population."
- **[DEC-ROUTE] STATE:not-started (FILED 2026-10-06, decsurvey §3.4;
  UNSCHEDULED)** — `ENG_ATTEMPT` as candidate-table rows plus one machine
  census. Evaluate whether `CAND_ROUTE_ATTEMPT` rows in `dfa_pfs[]` and a
  machine-census helper absorb the 11 `ENG_ATTEMPT` guards and the two
  `mixed` folds as a no-mover. Natural companion to D148/D151 Q5's
  `cand_rows[]` rename (same no-mover commit or the next).
- **[DEC-RUNG] STATE:not-started (FILED 2026-10-06, decsurvey §3.5;
  UNSCHEDULED)** — the VM rung ladder as one selector. Evaluate
  `vm_rung_of()` first-match rows replacing the three walkers' re-derivations,
  with stamp bits from the row. Trigger (D77): the next rung proposal
  ([ENG-BREP] lineage), when the cost of adding it is otherwise three arms.
- **[DEC-STAMPS] — fold into [LIST-TABLES] STEP 0 rather than a new row.**
  §3.6's small ladders (`UNROLL_K_WHY`, `VM_PRUNE_CEILING` + listing,
  `STARTPOS_GUARD`, `UTF_CHECK`, `REQ_WHY` alias, `VM_PREFILTER` two sources)
  plus §4.4 and §4.7. This survey is offered as that STEP 0's census input.
- **[DEC-KINDATTR] STATE:not-started (FILED 2026-10-06, decsurvey §3.8;
  UNSCHEDULED)** — the per-`AKind` attribute table for fact walks. Evaluate
  one attribute row per AST kind read by `startanch`/`endwin`/`startset`/
  `req`/`mrl`/`ctxnode`/`nfa`, with no-mover measured by `--emit-facts` over
  the corpus. Also asks whether the four "spliced call declined, D77" copies
  share one trigger. Trigger: the next module that adds an AST kind.
- **[DEC-LIMITS] STATE:not-started (FILED 2026-10-06, decsurvey §3.9;
  UNSCHEDULED)** — an effective-limit accessor plus a `behaviour` column on
  `limits.def`. Low value now. Trigger: the next new limit or default change
  (today a default change touches ~9 sites).

**Not proposed:**

- §3.7: fact twins are partly deliberate cross-checks. The one candidate
  question (an end-anchoring assertion) can ride [DEC-KINDATTR].
- §3.10–§3.13: not ripe, or owned by [OPT-SETS]/[OPT-DIAL]/[CLS-TREE].
- Request contradictions: owned by [OPT-SETS] §2.7.

**Order:**

1. [AXES-DENY-MASK] addendum (a question, then possibly a defect fix).
2. [DEC-FALLBACK].
3. [TIE-ALIGN] re-scope (needs the bench).
4. [DEC-ROUTE] with the D148 rename.
5. The rest stay filed under their triggers.

---

## 7. Standing questions (docs/design/CLAUDE.md)

1. **Measurement regime — NOT RELEVANT.** This note reads and produces no
   timing. The probes are compile-only stamp reads. The two rows that would
   move performance ([TIE-ALIGN], [DEC-FALLBACK]'s wasted attempt) name their
   own measurement in STEP 0.
2. **Independent control — RELEVANT.** Each live inconsistency (§4.2–§4.4,
   §4.7) compares TWO surfaces the compiler computes independently (stamp vs
   listing, run reader vs offset-k pick, masked vs unmasked sibling bits)
   against the code's own stated claim. Neither side is derived from the
   other, which is the finding. The control for every proposed refactor is
   byte identity (`scripts/emit_sweep.py`, 0 movers) plus `--list-axes`/
   `--emit-facts` identity over the corpus. The population is the corpus file
   list, not the refactor's own row list (K35).
3. **What moves when data is regenerated — NOT RELEVANT.** No table,
   calibration or generated file is introduced. Per D76/D94, §4.3's fix would
   be an abi event, and §4.4's fix moves a DEBUG listing only.

## 8. Lenses (brief)

- **Specific vs general:** every proposal replaces N specific chains with one
  general table, except §3.2, where the general form is a ranking.
- **Core vs derived:** §3.7/§3.8 are core (facts); everything else is
  emission/selection.
- **Applicable vs assumption-changing:** only §5.1 (re-vocabulary) changes a
  contract, and it is Frank's call.
- **Fits the architecture vs refactor:** all fit the existing `DFA_SELECT`/
  `fit_rungs` idiom.
- **SIBLING-OF-A-FAMILY** (the 2026-10-06 standing lens) is this note's whole
  subject. Future panels can cite §0's table by family number.
