# [PATFACTS] STEP 2: THE DESIGN

**Status: PROPOSED** (lane pfdesign, 2026-09-26, from main `e060f2e0`,
with `lane/reqrunenc2` read unmerged). Design only: nothing under `src/`,
`tests/` or `docs/spec/` changes in this lane. A full D6 panel follows,
and its dispositions go inline, marked, in house style. Charter: D120,
plus D125 addendum 1 (step 2 runs now, and [FINDINGS] B1 and
[OPT-LITSCAN] S2 are built as the record's FIRST CUSTOMERS). Evidence:
`inventory.md` (step 1) and its **Delta 2026-09-26** section (R13-R15, N1-N9).
Rulings this design stays inside: D120, D122 plus addenda 1-4, D123 plus
addenda (especially 2 and 4), D124, D77, and the general-mechanisms rule.

Read §0, then §1's table. Everything after §1 argues a row of that table.

---

## 0. Decisions first

1. **The record is a family of LAZY, MEMOIZED ACCESSORS over `Job`, not an
   eager struct filled at one pipeline point** (§2). A fact is computed on
   its first ask, cached for the rest of the compile attempt, and reset
   with the attempt's `Job` (`compile.c:908` callocs one per attempt, so
   the retry ladder resets it for free).
2. **Facts are SEALED BY EPOCH, and there are three epochs, not one** (§3).
   E1 (structural) is sealed after `pcrec_callgraph_build`
   (`compile.c:1397`). E2 (lowered) is sealed after `pcrec_lower_enc`
   (`:1488`). E3 (machine) is sealed after the forward NFA is final
   (`pcrec_nfa_wrap_unanchored`, `:1654`). The charter's "after
   `pcrec_lower_enc`" is E2. E1 exists because `select_engine` asks
   nullability and kind-presence BEFORE lowering (`select_engine.c:568,
   611, 658, 686`). E3 exists because the run pin is an NFA fact. A fact is
   published only once nothing can revoke it, so the step-1 "revocable
   fact" problem (`revbody`) cannot arise inside the record. The
   `revbody` case is a REWRITE correcting a rewrite, and the record does
   not hold rewrites (item 6). An accessor asked before its epoch is an
   internal-error refusal. That turns step 1's implicit `pcrec_minw`
   contract into a checked one.
3. **Core vs derived is a field-level split, and the delta already shows
   it** (§4). CORE facts come from a walk: the necessary SET, the WHOLE
   run, the anchors, the widths, the kind mask, and the k-set walk. DERIVED
   facts are functions of core facts plus a prior or a second core fact:
   the pick, the run's scan member and window, and the pin. A derived fact
   never re-walks a tree. The one cross-derivation dependency that must
   survive migration unchanged is S1's pin, which is over the DERIVED
   window (`litscan_s1.md` R3-2), not the whole run.
4. **ONE owner per derivation, and it stays where it lives today**
   (`reqbyte.c`, `startanch.c`, `endwin.c`, `mrl.c`, `atomic.c`,
   `prefix_k.c`). The record module (`src/opt/facts.c`, NEW) holds only
   the memo, the epoch guard and the DENY application. Consumers call
   accessors, and a structural grep check forbids calling an owner's
   derivation from anywhere else (§5). That cures R1/R2/R14 by construction.
5. **Encoding is one rule in two parts** (§6).
   (a) A FACT derivation never reads `cx->opt->encoding`. The lowered tree
   and NFA are already in the encoding's units, and the only
   encoding-STRUCTURE inputs are the lowering's descriptor (`PcrecEnc.
   start_cls`/`max_cp`, which `endwin.c:156` already reads).
   (b) Every DECISION that ranks bytes reads the byte-rate through ONE
   accessor (the findings accessor, `findings/design.md` §6.1). The prior's
   applicability is decided there, from the data's declaration (D123-4),
   and never at a reader. Each of the three RATE QUESTIONS (pick a member,
   compare two bytes, mass of a set or sequence) spells its NONE answer
   ONCE, inside a findings primitive. No reader ever tests `rate == NULL`.
   That is the structural cure for R13, the `[OPT-REQRUN-ENC]` incident.
   It AMENDS `findings/design.md` §6.1-§6.3 (§6.3 below).
6. **The record holds FACTS, not REWRITES and not DECISIONS** (§4.4).
   Rewrites and their annotations stay on the AST (`possessive`,
   `revbody`, `call.link`, discharge): there, "deletion IS the record"
   (step 1). Route and plan decisions stay with their owners and are NOT
   pattern facts: `fit`, the engine, a `DFA_SELECT` choice, `req_admit`,
   `vm_frameless` and `OfsTest`. Such a decision is memoized by its owner
   under the same one-derivation discipline, and only on a named trigger
   (§9). This is D124's line: one table per QUESTION. "What facts does the
   pattern have" is one question, and "which check runs where" (L4) is
   another.
7. **Deny is applied INSIDE the fact's accessor, once, and a denied fact is
   the "nothing to find" element for EVERY consumer** (§7). This is
   `litscan_s1.md` §1.1 invariant 2 and the `compile.c:1497-1500` house
   rule, generalized. So `-fno-req-byte` removing S1's pin is the design,
   not a leak. What was missing is each fact-deny's CONSUMER LIST in the
   spec (R15). No per-consumer use-deny is added: the bench's attribution
   is already spanned by four existing configs (§7.3, measured).
8. **Two grains.** PATTERN-grain facts (one answer per compile) are
   memoized accessors. NODE-grain facts (one answer per AST node:
   `pcrec_minw(node)`, nullability, `pcrec_cls_single`, S2's literal run)
   are PURE FUNCTIONS with ONE definition each, NOT memoized (§4.3). What
   R4/R5 lack is one definition, not a cache. A node memo waits on a
   measured compile-time cost (D77).
9. **First customers** (§8). **B1** builds the record's DATA tier: the
   byte-rate accessor plus three rate primitives. It migrates C1-C4
   (`rb_pick`, `rn_scan_index`/`rn_window_start`,
   `req_byte_dominated_by`, `set_ppm`), and it is the ONE `abi` event
   shared with the gate move (D123-2). **S2a** (`[OPT-VMLIT]` exact) reads
   ONE node-grain fact, the emission-contiguous literal run of an `A_CAT`
   spine, built from `pcrec_cls_single`. It reads nothing pattern-grain.
   **S2b** (D122(3)'s carried facts) is specified here and NOT built: its
   trigger is named.
10. **Migration** (§9): the skeleton first, byte-identical (3.0). Then B1,
    the abi event. Then one existing analysis at a time, each
    byte-identical under a named gate. **A migration step that moves an
    emitted byte is not a migration; it is a FINDING** (two copies
    disagreed). The step stops and files a K-row. It must not be absorbed
    into an abi bump.

11. **The record is INSPECTABLE** (§11, scope addition from Frank,
    2026-09-26). A query `pcrec --emit-facts --pattern P` (spelling: the
    manager's, `--emit-ir`'s query precedent) prints every fact, its status
    and WHY, per encoding. ONE printer renders every row from the record's
    memo, which is the same object the passes read. The fact-valued stamps
    (`REQ_BYTE`, `REQ_RUN`, `VM_START`) render through the same per-fact
    renderer, so a stamp and the dump cannot disagree. It is a DEBUG
    LISTING under a spec page (`ir_listing.md`'s status): a format contract
    with advisory rows, not ABI.

---

## 1. The record in one table

Epoch: E1 structural, E2 lowered, E3 machine (NFA). "Deny" means the
fact-level deny applied inside the accessor (§7). Grain: P = pattern
(memoized), N = node (pure function).

| fact | grain | kind | epoch | owner (derivation, today's site) | deny → empty value | consumers (each with its hat, §4.5) |
|---|---|---|---|---|---|---|
| kind mask `{BREF, CALL, LINKED_CALL, VAR, ATOMIC, LOOK, LIVE_CAPTURE, COLLAPSIBLE_REP}` | P | core | E1 | `atomic.c` predicates (`:59/149/221/565/807/919/954`), `pcrec_has_var` | — | `select_engine` (`:611/658/686`, forcing and prefilter), `emit_vm.c:13191/13208` (the `--emit-ir` listing, R1), `mod_lookaround` (`has_call`), `emit_vm.c:9980` (`mrl_win`) |
| language nullable | P | core | E1 | `pcrec_minw(root) == 0` (`mrl.c:120`), asked today at `select_engine.c:568` | — | `fit.lang_nullable`, `pcrec_startgate_needed` (`nfa.c:1150`), `[OPT-4.1]` gate |
| char widths `cwmin`/`cwmax` (root) | P | core | E1 | `mrl.c:305/444` | — | `endwin.c:88/172`, `startanch.c:78` |
| byte min width (root) | P | core | E2 | `pcrec_minw` | — | `startanch.c:80`, the VM's root checks |
| start anchor | P | core | E2 | `pcrec_start_anchor` (`startanch.c:143`) | `-fno-vm-anchor-bound` → `NONE` | VM attempt bound; DFA's one-directional assertion (`emit_dfa.c:7427`); **G2** (`:5885`, delta D.2) |
| end window | P | core | E2 | `pcrec_end_window` (`endwin.c:154`) | `-fno-end-window` → `-1` | both emitters' window clamp |
| necessary SET | P | core | E2 | `rb_walk` (`reqbyte.c:380`) | `-fno-req-byte` → ∅ | K65 set-rest (no-DFA-scan VM only); the pick (below) |
| necessary WHOLE run | P | core | E2 | `rb_walk`'s `runs.best` | `-fno-req-byte`, `-fno-req-run` → len 0 | K66 whole-run compare (no-DFA-scan VM only); the window (below) |
| necessary byte (pick) | P | derived | E2 | `rb_pick` ← set + byte-rate | as the set | `REQ_BYTE`, the one-byte pre-check, G1 |
| run scan member + window | P | derived | E2 | `rn_scan_index`/`rn_window_start` ← whole run + byte-rate | as the run | `REQ_RUN`, the run pre-check, **S1's pin** |
| k-set walk `k[0..nwalk)` | P | core | E3 | `pcrec_prefix_ksets` walk half (`prefix_k.c:409`) | — (it is a walk over the NFA; each USE has a row deny) | offset-k selection, the pin |
| run PIN `(run_o)` | P | derived | E3 | `prefix_k.c:479-491` ← k-set walk ∩ window | inherits the run's deny (`len 0` → unpinned) | `dfa_pfs[]` run rows, `OfsTest`, G1 (`run_verified`); S2b (not built) |
| byte-rate | P (per compile) | DATA | — | findings accessor (B1), `Ctx`-memoized | — (the data declares; NONE = not declared) | the three rate primitives only |
| `minw(node)`, nullable(node) | N | core | E2 | `pcrec_minw`, `vm_nullable` (R4: two copies, §9 step 3.5) | — | the VM emitter (≥9 sites), `callgraph.c` |
| singleton byte | N | core | E2 | `pcrec_cls_single` (R12) | — | `rb_walk`, `altcls`, `emit_vm.c:3659`, **S2a** |
| emission-contiguous literal run | N | core | E2 | **NEW with S2a**, over `pcrec_cls_single` | — | S2a (VM chain emit, `vm_cost`, `vm_count_slots`: one function, three readers) |

NOT in the record (§4.4): `fit`/engine/`engine_sel`; `DFA_SELECT`
choices; `req_admit`; `OfsTest`/`CandScan`; `vm_frameless`/`has_push`;
`Dfa` equivalence classes/states; AST annotations (`possessive`,
`revbody`, `call.link`/`minw`/`cwmax`); the fold relation (`fold.c`,
P1) and the byte cube (`cube_of`, P2), which are shared pure functions
of their inputs, owned by `src/core/` per D122-2(2).

---

## 2. Lazy memoized accessors, not an eager struct

**Shape** (spellings are the manager's; these are proposals):

```c
/* src/core/internal.h — beside Job */
typedef enum { PF_E0 = 0, PF_E1_STRUCT, PF_E2_LOWERED, PF_E3_MACHINE } PfEpoch;
typedef struct {
    uint32_t have;          /* one bit per memoized fact: "asked and cached" */
    PfEpoch  epoch;         /* advanced ONLY by compile_driver at the three seals */
    unsigned kinds;         /* E1 */
    bool     nullable;      /* E1 */
    int      cwmin, cwmax;  /* E1, character units */
    long long minw;         /* E2, bytes */
    int      start_anchor;  /* E2 */
    long long end_window;   /* E2 */
    ReqSet   req_set;       /* E2 core   (today Job.req_set)  */
    ReqRun   req_run;       /* E2 core `whole` + derived window (today Job.req_run) */
    int      req_byte;      /* E2 derived (today Job.req_byte) */
    PrefixKWalk kwalk;      /* E3 core: the walk half of PrefixKSets */
    bool     run_pinned; int run_o;   /* E3 derived */
} PatFacts;                 /* Job.pf */

/* src/opt/facts.c — every accessor has this shape */
const ReqSet *pcrec_fact_req_set(Ctx *cx);   /* E2; deny -fno-req-byte -> empty */
```

Each accessor does four things, in this order:
1. **Epoch guard:** `if (cx->job->pf.epoch < E) pcrec_ctx_fail(... "internal error")`.
2. **Memo:** return the cached value if `have` has the bit.
3. **Deny:** if the fact's deny bit is set, store the empty value (§7).
4. **Derive:** otherwise call the owner's derivation ONCE, store the
   result, and set the bit.

**Why lazy, through the lenses:**

| lens | lazy memoized accessors | eager struct at one point |
|---|---|---|
| specific vs general | one discipline for every fact, and a new fact is one accessor | a new fact means editing the fill site and every early-exit path |
| core vs derived | a derived accessor calls its core accessor, so the dependency is a CALL and cannot be misordered | the fill order encodes the dependency, which is step 1's "implicit in call-site position" |
| applicable vs assumption-changing | applicable. `Job` already carries these facts. Accessors replace direct field reads. No pipeline order moves | assumption-changing. It forces every fact to one epoch, which §3 shows is false for E1 and E3 |
| fits the architecture vs a refactor | fits. The positive precedents `dfa_search_is_pinned` (one derivation, five readers) and `OfsTest` are already accessor-shaped, only unmemoized | a refactor of `compile_driver` |
| D124 shared question / engine hat | "which facts does the pattern have" is ONE question for both emissions, and each consumer is a hat on the same accessor (§4.5) | same |
| pay for what you use | a DFA-only artifact never asks VM facts, and a no-DFA route never computes E3 | computes everything |

**Cost:** each accessor after the first ask is a bit test. R14 (the k-set
walk re-run per admission ask) goes away when the E3 walk memoizes. That
is the only case where memoization buys time that is known to be spent,
and even that is unmeasured (§10).

**Ask order cannot change an answer.** Every derivation is a pure function
of (the tree or NFA at its sealed epoch, `cx->opt`). So the memo is
order-independent. The findings consumption record (`findings/design.md`
§6.4) is the one order-SENSITIVE side effect: "asked" is recorded. That
record is findings', and its rule 1-3 (deny-independent asking, stamp
written last) is unchanged by this design. §7.4 says what a fact-deny
does to it.

---

## 3. Epochs: three seals, nothing revocable

| epoch | sealed at (`compile.c`) | why the facts are final there | facts |
|---|---|---|---|
| E1 structural | after `pcrec_callgraph_build` (`:1397`), before `pcrec_select_engine` (`:1424`) | Every later pass rewrites only (a) FLAGS on nodes (`possessive`, `revbody` by select_engine; `u.look.widths` by postresolve), or (b) `A_CLASS` contents, introducing only `A_CLASS`/`A_CAT`/`A_ALT`/`A_EMPTY` (`lower_enc.c:223-382`: the node kinds it allocates). Hence kind-presence is invariant. A non-empty class lowers to a non-empty byte sequence, so nullability is invariant. Character widths are character units by definition (`mrl.c`'s own header) | kind mask, nullable, `cwmin`/`cwmax` |
| E2 lowered | after `pcrec_lower_enc` (`:1488`), i.e. where `start_anchor`/`end_window`/`req_*` are computed today (`:1501-1520`) | `lower_enc` is the last tree rewrite | byte `minw`, start anchor, end window, necessary set, whole run, the pick, the window |
| E3 machine | after the FINAL forward NFA: after the collapse decision's rebuild (`:1648-1649`) and `pcrec_nfa_wrap_unanchored` (`:1654`), before the first DFA build | the count-collapse ladder REBUILDS `Job.nfa` (`:1648-1649`), so any walk before that point can be stale. `pcrec_dfa_scan_state_written` (`:1678`) is today's first `unanch_start` ask, and it comes after the seal | k-set walk, pin |

**E3 exists only on a route that builds a forward NFA** (DFA or hybrid,
`:1538`). On a no-DFA VM route the E3 accessors return NONE: no walk, no
pin. That is already true today (`pcrec_prefix_ksets` is only reached via
`unanch_start`). `[OPT-VMSEED]` (§9, not built) is the fact customer that
will need an AST-level offset bound on exactly that route.

**The E1 invariance claim is a PROOF plus a CHECK.** The proof is the
table's middle column. The check is born with step 3.2: under the existing
debug self-check build shape (`cstart_check_omission`, `nfa.c:1086`, is
the precedent: "a deliberate independent re-derivation"), re-derive the E1
facts on the E2 tree and fail on disagreement. It is not a second source
of truth. It is a cross-check that runs on the same function over a later
tree, and a sabotage row proves it can fire (plant an `A_BREF` in
`lower_enc`'s output).

**The epoch guard closes step 1's `pcrec_minw` gap.** The ROOT byte
`minw` is E2. `select_engine`'s pre-lowering read (`:568`) becomes the E1
`nullable` accessor, whose answer is lowering-invariant (`minw == 0` in
bytes iff `== 0` in characters). The node-grain `pcrec_minw(node)` stays
a pure function. Its callers are all E2 emitters, and `callgraph.c:829`
feeds its own fixpoint by design.

---

## 4. Core vs derived, ownership, and what the record is not

### 4.1 The split, and why it matters now

The delta (D.5 item 1) shows the tree ALREADY publishing core and derived
facts side by side from one call: `ReqRun.whole` next to `bytes/idx/at`,
and `Job.req_set` next to `Job.req_byte`. The record makes this split the
rule:

- A **core** fact depends only on the sealed tree or NFA and on `cx->opt`'s
  structural options. It depends on NO prior and NO other fact's choice. It
  is what a no-DFA route's no-match PROOF may rest on (K65/K66's lesson:
  "the proof must be a fact about the pattern, not a speed choice").
- A **derived** fact is a function of core facts and the byte-rate. It is
  a SPEED choice. By construction it is safe for nothing but speed, which
  is `findings/design.md` §6.2a's per-reader argument turned into a type
  distinction. A future reader on a no-DFA VM route that reads a derived
  fact must bring §6.2a's row (that section's "what this does NOT cover").

**The one derived-on-derived dependency, kept exactly:** the pin (E3,
derived) is over the WINDOW (E2, derived), not the whole run. Moving the
pin to `whole` would be stronger: a pin over a run longer than 8 bytes. It
would also be a MOVER population, and `litscan_s1.md` R3-2 requires the
pin and the pre-check it may dominate to describe the same run. Not done
(§10).

### 4.2 Ownership: one derivation, where it lives

The derivations do not move files. `facts.c` calls them. After migration,
`pcrec_req_byte`, `pcrec_start_anchor`, `pcrec_end_window`, the `atomic.c`
presence predicates at root and the k-set WALK have exactly one caller
each, `facts.c`. A grep check enforces this in `make test-codegen`'s
structural section (the `assertions_design.md` §8.4 grep-check precedent).
The check allows the owner file and `facts.c`, and it is born with a
sabotage row that re-inserts `pcrec_has_bref(root)` in `emit_vm.c`'s
listing.

`pcrec_prefix_ksets` SPLITS (step 3.4) into its walk, the E3 core fact,
and its selection. The selection is a DECISION: the scan offset and its
verifies under the cost model and the rate. It stays in `prefix_k.c`,
called by `unanch_start` with the memoized walk. Today one function does
both, which is why the pin (a fact) sits in the middle of a selection
routine (`prefix_k.c:479`, "a fact this file publishes and does not act
on").

### 4.3 Node grain: one definition, no cache

R4 (`vm_nullable` vs `pcrec_minw == 0`), R5 (`vm_cursor_fits`/`vm_det_seq`
at three sites) and R12 (four "is this one byte" spellings) are all NODE
questions. Their defect is two DEFINITIONS, not a missing cache. The rule:
**one pure function per node question, declared in `internal.h`, and no
emitter-local re-spelling.** Memoizing per node would need an `Ast` field
or an arena side table keyed by node. Neither is justified until a compile
profile shows repeated node walks cost material time (D77, §10). R4's
`A_CALL` arm difference is deliberate (`inventory.md` R4). The unified
function keeps it as that one arm.

### 4.4 What the record is not, and why (D124)

| thing | why not a record fact | where it stays |
|---|---|---|
| rewrites/annotations (`possessive`, `revbody`, discharge, `call.link`) | they are the RESULT of a rewrite and are emission material. "Revocable" (`lower_enc` clearing `revbody`) is a rewrite correcting a rewrite, and an epoch-sealed fact cannot be revoked | the AST |
| route decisions (`fit`, engine, `engine_sel`, `pcrec_artifact_has_dfa_scan`) | a decision about the ARTIFACT, made by `select_engine`, depending on options and caps as well as the pattern | `Job.fit` (already one derivation) |
| emission decisions (`DFA_SELECT`, `req_admit`, `OfsTest`, `CandScan`) | depend on the machine, the deny ROWS and the selection order: L4 ("which check runs where"), a different question from "what the pattern has" | `emit_dfa.c`, one derivation each (`OfsTest`, `req_admit`), re-derived per ask. Memoized there when a reader in ANOTHER file needs one (S2b is that trigger, §8.3) |
| emitter byproducts (`vm_frameless`/`has_push`) | a fact about the emitted PROGRAM, the VM-plan epoch (delta N3) | `Job.vm_frameless`, published by its one owner, as now |
| machine structure (`clsmap`, states, views) | construction, not analysis | `Dfa` |

### 4.5 Per-consumer contracts (D124 item 3)

A shared row states what it guarantees to each consumer. K64 was a shared
decision correct for one consumer and wrong for another. The facts with
more than one consumer:

| fact | consumer | what the fact guarantees to it | the consumer's own obligation |
|---|---|---|---|
| necessary set / whole run | DFA or hybrid pre-check | any member absent ⇒ NOMATCH (speed only: the scan is already linear) | none beyond soundness |
| | no-DFA-scan VM pre-check (K65/K66) | the whole set and the whole run ⇒ a no-match proof that is a fact about the PATTERN | test EVERY member and the WHOLE run, never a derived pick alone |
| window (derived) | run pre-check | any window's absence ⇒ NOMATCH | none on DFA routes. On a no-DFA VM route it is backed by the whole-run compare |
| | S1 pin | the pin describes the SAME bytes the pre-check compares (R3-2) | none |
| start anchor | VM attempt bound | every match starts at `search_from` (or at the `\G` point) | none |
| | DFA assertion | an AST-proved anchor with a live interior start is a miscompile (one-directional) | assert only |
| | G2 | a one-attempt route | G2 adds its own LINEARITY conjunct (K64: exact hybrid or frameless). The fact does not promise linearity |
| pin | `dfa_pfs[]` run rows | every match has the window at `run_o` (true of the superset NFA on a collapsed prefilter, hence of every exact match) | the row checks its own identity clause (scan byte = run member at `run_o + idx`) |
| | G1 | the same | `run_verified` is the SELECTED row's test, never the pin alone |
| nullable | `select_engine`, K50 start gate | lowering-invariant | none |

---

## 5. How consumers read (no consumer re-walks)

1. A consumer reads a pattern fact ONLY through its `pcrec_fact_*`
   accessor. The structural check (§4.2) makes a direct derivation call
   outside the owner or `facts.c` a test failure.
2. A consumer never reads a fact's DENY bit. The accessor already returned
   the empty value. Today's `compile.c:1501-1520` ternaries move into
   `facts.c` (step 3.0). After that, `compile.c` no longer computes any
   fact eagerly. Its only record duties are advancing the epoch at the
   three seals and allocating `Job` as now.
3. A consumer never reads `cx->opt->encoding` to decide a fact or a
   ranking (§6). The findings §11.7 grep check (planned) is widened to
   cover `reqbyte.c`, `prefix_k.c` and `emit_dfa.c`'s G1.
4. `Job.req_byte`, `Job.req_run`, `Job.req_set`, `Job.start_anchor` and
   `Job.end_window` stop being written by `compile.c`. They become
   `Job.pf`'s members, and every reader moves to the accessor in the same
   step (3.0). There is no dual-write period: a field and its accessor
   alive together is the parallel mechanism the house rule forbids, and
   implement-then-replace here is one commit per fact family.

---

## 6. The encoding story

### 6.1 Facts are about a pattern UNDER an encoding, and get that for free

E2/E3 facts are computed on the LOWERED tree and its NFA, whose every
`A_CLASS` is a byte class in the artifact's units. That is why
`reqbyte.c`'s own header can say the walk is encoding-neutral while its
answer differs under `-e utf8` (a lowered `é` is two singleton bytes, and
the run population RISES, `reqpos_2b.md` §2.4 item 7). E1 facts are
lowering-invariant (§3). So the record needs **no encoding key per fact**:
the compile has one encoding, and the record is per compile. The only
legitimate encoding inputs to a fact are the lowering's structural
descriptor (`PcrecEnc.start_cls`, `max_cp`, as `endwin.c:156-164` and
`nfa.c:1141` read). Those are facts about the encoding's byte structure,
not its identity.

### 6.2 The prior: one accessor, one applicability decision

The byte-frequency prior is DATA about a corpus under an encoding
(`reqbyte_freq_pick.md` §3). Its applicability is declared by the data
(D123-4: the default bundle carries `serves byte-rate when byte`), and it
is decided in ONE place, `pcrec_find_byte_rate(cx)` (B1). That is D122
addendum 2 (3)'s "the gate moves into the accessor" and `compare_stack.md`
§7 Q3, answered. It retires R9 (`set_ppm` ungated) and the four scattered
gate spellings (`reqbyte.c:521/543/567`, `emit_dfa.c:5925`).

### 6.3 The non-byte decline is ONE rule per QUESTION, never per reader (R13's cure)

R13 was not a missing gate. Both readers were gated. It was two spellings
of the same NONE ANSWER that diverged, rightmost versus leftmost.
`findings/design.md` §6.2 states "the NONE fallback is each READER's own
rule", and §6.3 has each reader "treat `rate == NULL` exactly as it treats
`!bytekey` today". That is the per-reader shape R13 grew in, and its C2
row's fallback ("leftmost") is already stale after stage 2. **This design
amends it:** the NONE answer is spelled once per QUESTION KIND, inside a
findings primitive, and readers pass candidates and never see `NULL`.

| question kind | primitive (proposed spelling) | NONE answer, spelled once | readers | tie rule (the reader's, passed as candidate ORDER, so every `byte` artifact is byte-identical) |
|---|---|---|---|---|
| PICK: which member to scan | `int pcrec_find_pick(rate, cand[], n, rightmost)` | the candidate at index `rightmost`, which is the reader's POSITIONAL rightmost (PCRE2's LASTCODEUNIT rule) | `rb_pick` (candidates: `s->pick`, then the other members 255→0; `rightmost = 0`), `rn_scan_index` (candidates: `bytes[0..n)`; `rightmost = n-1`) | argmin, ties to the EARLIEST candidate. `rb_pick`: `pick` if among the minima, else the largest byte. `rn_scan_index`: leftmost. Both exactly as today |
| COMPARE: is `p` no commoner than `q` | `bool pcrec_find_no_commoner(rate, p, q)` | `false` (unknown ⇒ no density claim; identity is the caller's separate conjunct) | `req_byte_dominated_by` | — |
| MASS: Σ rate over a set or a sequence | `pcrec_find_set_mass(rate, set)` (findings §6.1) + `pcrec_find_seq_mass(rate, bytes, n)` | the count (`|set|·10⁶/256` for a set, `findings/design.md` §0.8; `n` for a sequence, so every window ties) | `set_ppm` (offset-k), `rn_window_start` | windows: ties to the leftmost, which under NONE is `lo_s`, today's `!bytekey` answer |

With this table, the two readers that diverged in R13 call ONE function
and cannot diverge again. A future reader of an existing kind inherits the
NONE rule. A new KIND of rate question adds one primitive with one NONE
rule and a row here. A grep check (`rate == NULL`, `!rate`, `bytekey`,
`PCREC_ENC_BYTE` in any rate reader) is widened from findings §11.7.

**Byte-identity of the table under `-e byte` + default:** `rate` equals
today's table entry for entry (`findings/design.md` §0.7), and the
candidate orders reproduce each reader's tie rule. The `rb_pick` argument:
today it scans 255→0 keeping the first strict minimum (so ties go to the
largest byte), then returns `pick` if `rate[pick]` equals that minimum.
Candidate order `[pick, 255..0 \ pick]` with ties-to-earliest gives the
same answer in both cases. **Under `-e utf8`:** PICK and COMPARE answer
exactly as today after reqrunenc2. MASS moves offset-k from the ungated
prior to cardinality. That is findings B1's named per-artifact `utf8`
manifest (findings §11.3) and its abi event.

---

## 7. The deny-flag story

### 7.1 Two kinds of deny, and where each applies

| kind | contract | applied | examples |
|---|---|---|---|
| **fact deny** | the build is indistinguishable from a pattern with NOTHING TO FIND for this fact (`compile.c:1497-1500`, `litscan_s1.md` §1.1 inv. 2) | INSIDE the fact's accessor, which stores the empty value | `-fno-req-byte` (set, run, pick), `-fno-req-run` (run, window), `-fno-vm-anchor-bound` (start anchor), `-fno-end-window` (end window) |
| **row deny** | the artifact without that emission FORM, with every fact intact | on the `DFA_SELECT` row or the consumer | `-fno-run-prefilter`, `-fno-offset-skip`, `-fno-premul-table`, … |

A fact deny is answer-identical BY CONSTRUCTION: every consumer already
handles its fact's empty value, because some real pattern produces it.
This is why the rule is not per consumer. A consumer that saw a fact
another consumer could not see would be serving a pattern that does not
exist.

### 7.2 Shared facts: the deny reaches every consumer, and that is the design

`-fno-req-byte` removing S1's pin (K68's rider, `known_issues.md:37`) is
this rule working, not a leak. It is also not the only instance (delta
R15), measured on this lane's build:

| pattern / config | `RX_DFA_PREFILTER` | `REQ_RUN` | `REQ_WHY` |
|---|---|---|---|
| `/user\|/users`, default | `run-pinned` | `2f75736572@0` | `dominated` |
| `-fno-run-prefilter` (row deny) | `memchr` | `2f75736572@0` | `emitted` |
| `-fno-req-run` (fact deny: run) | `memchr` | `none` | `dominated` (identity) |
| `-fno-req-byte` (fact deny: set, run) | `memchr` | `none` | `none` |
| `--engine=vm '^ab[cd]@'`, default | — | — | `one-attempt` (G2) |
| `... -fno-vm-anchor-bound` (fact deny: anchor) | — | — | `emitted` |

**What was missing is documentation, not mechanism.** Each fact deny's spec
text (`tuning.md` §2.x) must list EVERY consumer of the fact it empties
(D80). K68's rider covers `-fno-req-byte` → pin. `-fno-vm-anchor-bound`
→ G2 needs the same sentence, and so does `-fno-req-run` → pin. With the
record, the consumer list is mechanical: the callers of the fact's
accessor. The spec sentence is written from that grep at each migration
step.

### 7.3 No per-consumer "use" deny now (D77)

The bench's attribution question ("what does the pre-check cost, holding
the pin?") is already spanned by the four configs in the table: default,
`-fno-run-prefilter` (pin unused, pre-check back), `-fno-req-run` (no
pin, one-byte pre-check) and `-fno-req-byte` (neither). A "pre-check off,
pin kept" deny would describe an artifact that is today's DEFAULT on every
pinned pattern, where G1 already elides the dominated pre-check. **Trigger
to build a use deny:** a bench attribution request that the four configs
cannot answer, named by the request.

### 7.4 Interaction with the findings stamp

A fact deny stores the empty value WITHOUT running the derivation, so the
pick never asks the rate, and `byte-rate` is not "consumed" on that build.
That is honest: a pattern with nothing to find also consumes nothing.
`findings/design.md` §6.4 rule 3's named-lines exemption for fact-deny
builds already covers it. §6.4 rule 1's "C1/C2 are the named exception"
becomes "every fact-deny's derived facts are the named exception", the
same class stated once.

### 7.5 The K68 class (recommendation, §12 Q7)

Every FACT deny and every ROW deny is answer-neutral by its contract, so
each belongs in `rx_info.flags`' `strategy_denials` mask by construction.
The bit-19 fix and K68 (bits 28/29/30) are two incidents of a bit added
without being classified. That is D120's trigger shape. The general fix
is a `kind` column in `src/core/axes.def` (fact / row / value / answer),
with the mask generated from it. This is not [PATFACTS]'s to build (K68 is
being fixed by hand in its own lane). It is recommended for filing as its
own row after K68 merges.

---

## 8. The first customers, specified

### 8.1 [FINDINGS] B1: the record's DATA tier

**B1 builds** (`findings/design.md` §13 B1, unchanged except where noted):
- `pcrec_find_byte_rate(cx)` in `src/core/findings.c`, memoized in `Ctx`.
  This is the record's one DATA member. The record references it and does
  not copy it: `PatFacts` holds no rate pointer, the same rule as R39's
  `DfaSel`.
- **The three rate primitives of §6.3, with their NONE answers inside.
  This AMENDS findings §6.1** (which lists `pcrec_find_set_mass` only) and
  **§6.3** (readers stop testing `rate == NULL`). `pcrec_find_seq_mass`
  is new, and it is the primitive `rn_window_start` needs.
- The deletion of `pcrec_byte_freq_ppm`/`byte_freq_ppm_tbl`
  (`prefix_k.c:112-165`), as findings §6.1 already plans.

**B1 reads from the record: the DERIVED-fact sites and nothing else.**

| site after step 3.0 | reads | calls |
|---|---|---|
| the pick (`rb_pick`, inside `facts.c`'s derived `req_byte` accessor) | core `pcrec_fact_req_set` | `pcrec_find_pick` |
| the run member + window (`rn_scan_index`/`rn_window_start`) | core whole run | `pcrec_find_pick`, `pcrec_find_seq_mass` |
| G1's density conjunct (`req_byte_dominated_by`) | `CandScan` (an emission decision, unchanged) + derived `req_byte` | `pcrec_find_no_commoner` |
| offset-k selection (`set_ppm`) | E3 k-set walk (after 3.4; before 3.4 it is the same walk inline) | `pcrec_find_set_mass` |

**B1 must NOT:** read `cx->opt->encoding` at any reader; memoize a rate
anywhere but `Ctx`; add a second `req_*` field; or call `rb_walk`. Its
movers are exactly findings §11.3's two manifests. `b1_byte_movers` is
EMPTY. `b1_utf8_movers` is named per artifact: offset-k selection moves,
plus any G1 fallout on the same artifact. Its abi event is the one D123-2
ruled shared with the gate move.

**Sequencing:** B1 rebases onto step 3.0. The three req-fact derivations
it edits are then inside `facts.c`'s accessors, not in `compile.c`. If B1
must land first (the manager's call on lane availability), it edits
today's sites, and step 3.0 moves them afterwards. That is
implement-then-replace, and it is still correct. The only forbidden order
is a findings-local memo of any PATTERN fact.

### 8.2 [OPT-LITSCAN] S2a: `[OPT-VMLIT]` exact, the node-grain customer

S2a turns the VM's per-byte literal chain into P4's exact arm, one
constant-length `memcmp` (`compare_stack.md` §6.1 S2). **What it reads:**

1. **ONE new node-grain fact, the emission-contiguous literal run.** Given
   an `A_CAT` spine child position, it returns the maximal `L ≥ 2`
   consecutive spine children each with `pcrec_cls_single(child) >= 0`,
   and their bytes. The spine is not seen through `A_CAP`, `A_ATOMIC`,
   `A_LOOK`, `A_REP` or anything else: a capture write or a choice point
   between two bytes breaks EMISSION contiguity, whatever the subject says.
   - This is **NOT** `rb_walk`'s run. That run is SUBJECT-contiguous across
     `A_CAP` (`reqbyte.c:398`, "Transparent"), pattern-grain and NECESSARY.
     S2a's run is local, emission-contiguous and not necessary. They are
     two questions, so they get two facts, sharing the one singleton
     primitive `pcrec_cls_single` (R12's anchor). `vmlit_trigger_read.md`
     §3 reached the same verdict from the population: the real VM witnesses
     are per-branch literals with no whole-pattern `REQ_RUN`.
   - It is **NOT** `vm_cls_shape`'s `count == 1` bitmap scan
     (`compare_stack.md` D3). S2a must not grow a third singleton
     spelling.
   - **One function, three readers**: `vm_emit`'s chain emission,
     `vm_cost_*` and `vm_count_slots` must see the SAME run. This is R5's
     lesson: the cost and slot walks re-derive shape questions and have
     disagreed before (`[DD-14 wave B+C]` §4.4c). A pure function
     called by all three is the cure, and no memo is needed (§4.3).
   - Under `-e utf8` a lowered multi-byte literal is a spine of singleton
     byte classes, so the fact is encoding-correct with no encoding read
     (§6.1).
2. **Nothing pattern-grain.** S2a reads no `req_*`, no pin, no rate
   (an L2 exact compare has no form choice: pay-for-what-you-use, D122
   addendum (b)), and no route decision.
3. **The island arm** (`vm_isl_*`'s single-child chains) is the same
   QUESTION over a different structure, the island trie (emitter-local
   `VmIslNode`). It reads its own trie and shares only P4, the compare
   emitter. This is recorded as a site that keeps its own recognizer, with
   the reason: the data structure differs (D122 addendum (a)).

**What S2a owes on its own merits, not the record's:** its own abi event
(the emitted text moves); the D51 step-budget spec sentence (a run charged
as 1 versus `n`); P8's subject-end guard (a constant-length `memcmp` reads
exactly `L` bytes after one `pos + L <= n` check, so there is no
over-read); and its D77 gate, the OWED bench pass on its own cells
(`compare_stack.md` §6.1, D122 addendum 2 (1): S3 before S2).

### 8.3 S2b: D122(3)'s carried verified facts, specified and NOT built

Direction (D122(3)): a pre-pass that verified a literal at a candidate
lets the matcher skip re-checking it. Precisely, per consumer hat:

| hat | what it would skip | facts it would read | status |
|---|---|---|---|
| VM hybrid attempt | the literal compare of the pinned window, when the VM reaches it at the pinned offset | (a) E3 pin `(run_o, len)` (record, core+derived); (b) **the SELECTED axis-B row verifies the run**, i.e. `CandScan.run_verified` (an emission decision, owned by `emit_dfa.c`, which must then be memoized and published for `emit_vm.c` to read: R8's trigger); (c) a NODE-grain "this node sits at fixed offset `d` from the attempt start on every path" fact | (c) does not exist anywhere. `prefix_k.c`'s offsets are NFA-state offsets, not AST-node offsets |
| DFA entry | re-stepping the run: enter at `δ*(s0, run)` after the window | (a); the machine's own `δ*` (construction); `run_o == 0` | a DFA_SELECT row question, D122 addendum 4's full-panel bar |
| bounds checks | the `pos + k < n` tests inside the verified span | (a) + (b) | same as the VM hat |

**Why not now (D77):** no measurement yet shows a per-attempt re-check of
a pinned run costing anything. The VM hat's natural witness,
`wild-secrets-github-pat` (hybrid, `github_pat_` at offset 0), first needs
S2a's own compare, which makes the re-check one fused load. **Trigger:**
after S2a lands, a bench pass on the pinned-run HYBRID cells showing a
residual attributable to the re-verify (a hand twin that skips it, the
litscan S1 hand-twin method). When the trigger fires, (b) becomes a
memoized emission decision published once (never a VM re-derivation of
the DFA's selection, D124 item 2), and (c) is a new node-grain fact with
its own derivation and design review.

---

## 9. Migration order (step 3): implement-then-replace, one family at a time

**The proof tool, owed once and used by every byte-identical step (the
measured need is this table's seven consumers):** a corpus A/B EMIT DIFF.
It compiles every `.rxt` pattern (plus the bench's patterns, read-only)
with the pre-step and post-step compilers, over `-e byte` and `-e utf8` ×
the step's named deny flags, and diffs the whole artifact. Pass means ZERO
MOVERS. Build it by generalizing the S1 census instrument
(`docs/dev/optloop/s1/census_b.py`). It is a named manifest, not a count
(learnings §3), with a REACH line: how many artifacts ASKED the migrated
accessor, so "0 movers" is not vacuous.

| step | what moves | gate that proves it | abi |
|---|---|---|---|
| **3.0 skeleton + E2 req/anchor/window + `--emit-facts`** | `Job.pf`, `PfEpoch`, `facts.c`, `facts.def`; the §11 listing with its four checks; `REQ_*`/`VM_START` render through the shared renderers. The start anchor, end window, set, whole run, pick and window move behind accessors. The `compile.c:1501-1520` deny ternaries move into the accessors. The structural grep check plus its sabotage row | A/B diff ZERO over byte+utf8 × {default, `-fno-req-byte`, `-fno-req-run`, `-fno-end-window`, `-fno-vm-anchor-bound`, `-fno-run-prefilter`, `--engine=vm`}; `run_recursion_identity.sh` (B) with its pin UNMOVED (a re-pin is disqualifying); `run_prechecks.sh`; `make test-codegen`/`make strict` | **no** |
| **3.1 = [FINDINGS] B1** | the data tier; the §6.3 primitives; C1-C4 migrated | findings §11.3 manifests (`byte` EMPTY with REACH; `utf8` named per artifact); findings §13 B1's acceptance list | **YES**: the one D123-2 event |
| **3.2 E1: kinds, nullable, cwidth** | `select_engine`'s locals, the `emit_vm.c:13191/13208` listing re-walk (R1), `emit_vm.c:9980` read the accessors. The E1 invariance cross-check plus its sabotage row | A/B diff ZERO; `run_ir_listing.sh` (the listing is output, not artifact, and must be unchanged); `run_vm_identity.sh` | no |
| **3.3 = S2a** | the node-grain literal-run function; the VM chain | S2a's own gate (its movers are its design, not a migration) plus: cost/slot/emit agreement on every corpus pattern, the R5 check | **YES**, S2a's own |
| **3.4 E3: the k-set walk memo + pin** | `pcrec_prefix_ksets` splits into walk (fact) and selection (decision). The pin moves into the E3 accessor. `unanch_start` reads the memo (R14) | A/B diff ZERO; `run_offset_skip.sh`; the S1 census re-run, identical to `census_b_main.tsv` | no |
| **3.5 node nullable (R4)** | `vm_nullable` becomes the one node-nullable function (with the `A_CALL` arm kept) | A/B diff ZERO; `run_vm_identity.sh`. **A mover here is a found disagreement between the two copies. Stop and file a K-row** | no |
| 3.6 (anytime) R3 | `mrl.c`/`callgraph.c` saturating arithmetic unified | A/B diff ZERO | no |

**Order rationale.** 3.0 first because B1 and every later step edit
through it. It is also the smallest step that retires a real hazard: the
deny application lives in one file. B1 (3.1) next, because it is the
chartered first customer and the only other abi event. 3.2 before 3.4:
E1 has four-plus readers and a debug-listing re-walk, while E3 has one
owner and a cost that is unmeasured. S2a (3.3) is placed where its own
gates allow. It depends only on 3.0's `internal.h` declarations, and it
may land before 3.2 without harm. Each step is one lane. Every
byte-identical step runs its A/B diff as the lane's LAST act (BOILERPLATE
do-then-finish), because the diff is a multi-config corpus run.

**Stop rule, repeated because it is the whole discipline:** a
byte-identical step with a nonzero A/B diff has found two copies of one
fact that disagree. That is R13's class. The lane reports the movers and
files a K-row, and the step does not land as an abi event.

---

## 10. Deliberately NOT built now (D77), each with its trigger

| not built | trigger (the measurement or event that builds it) |
|---|---|
| per-node memoization (an `Ast` field or a side table) | a compile profile showing repeated node walks (`pcrec_minw`, nullable, `vm_cost`) are a material share of compile time on the corpus or bench |
| memoizing `DFA_SELECT`/`req_admit` choices (R8) | a reader in ANOTHER file needs one (S2b is that trigger), or a compile profile names R14's walks after 3.4 |
| S2b carried facts (§8.3) | the bench pass named in §8.3, after S2a |
| a node-grain "fixed offset from attempt start" fact | S2b's trigger (it is S2b's input (c)) |
| pin over the WHOLE run (not the window) | a census of pinned whole runs longer than `PCREC_MAX_REQ_RUN_EMIT` showing movers worth an abi event |
| a per-consumer USE deny | a bench attribution the four configs of §7.3 cannot answer |
| an AKind property table for opaque atoms ([VAR]'s ask) | a THIRD opaque, run-time-valued kind (today `A_BREF`, `A_VAR`). The no-`default:` `-Wswitch` alarm stays the per-site safety. A table would duplicate it |
| an `[OPT-VMSEED]` offset-bound fact (AST-level, for the no-NFA route) | VMSEED's own population census (its plan row's D77 step) |
| [ENG-TACTICS] precondition facts | its tactic census (its plan row) |
| E1/E2 reuse across retry-ladder rungs | `[OPT-RETRY-REUSE]`'s design (K67 is its witness). Sealed E1/E2 facts are rung-invariant, and the record makes them carryable |
| ~~an `--emit-ir` dump of the record~~ | **TRIGGER FIRED 2026-09-26** (two lanes reverse-engineered facts from `#define`s): now §11's `--emit-facts`, landing with step 3.0 |
| the byte cube `cube_of` (P2) | its first customer (S4 / `[CLS-TREE]`), in `src/core/` (D122-2(2)). It is a pure function of a class, not a record entry |
| the `strategy_denials` classification column (§7.5) | filed as its own row after K68 merges (§12 Q7) |

---

## 11. The inspection surface: `--emit-facts` (scope addition, Frank 2026-09-26)

**Measured need (D77).** On 2026-09-26 two fact-finding lanes, `utf8reqbyte`
and `bit30`, recovered pcrec's conclusions about a pattern by compiling it
and reverse-engineering the emitted `#define`s. The stamps say WHAT was
emitted. They do not say which analysis ran, which was denied or declined
and why, or which facts nobody asked for. This section also retires §10's
row "an `--emit-ir` dump of the record": its trigger has fired.

### 11.1 The query

`pcrec --emit-facts [compile options] --pattern P` (or on an `.rxt` target).
It is a QUERY, exactly like `--emit-ir` (`docs/spec/cli.md` §2): it takes a
pattern, takes no `-o`, runs the ordinary compile to completion in memory,
prints the listing and exits. Every compile option (`-e`, every `-f`/`-fno-`,
`--engine`, `--analysis` once B2 lands) applies unchanged, so the listing
describes the compile the user would have got.

**Per encoding.** Every row carries an `encoding` column. The flag accepts an
encoding LIST (proposed `--emit-facts=byte,utf8`; the bare flag means the
compile's own `-e`). The CLI runs one complete compile per listed encoding and
concatenates the rows. That is the comparison the two lanes did by hand, and
each compile is an ordinary compile with its own record. There is no
"multi-encoding record". A record is per compile (§6.1).

It is **not VM-only.** Facts are engine-neutral (D124), so the listing works
on a DFA, hybrid or VM artifact. On a route that never reaches an epoch, the
rows say so (below). They are never missing.

### 11.2 What it prints (table contract at birth; three named sections)

`docs/spec/table_contract.md`'s scope rule makes conformance mandatory: "a
new table command that does not conform is a defect". So the output is TSV
with named `#section`s, the Sections mechanism `--emit-ir` and
`--list-schema` already use.

**`#section facts`**: one row per record fact, in the record's table order.

| column | content |
|---|---|
| `encoding` | the compile's encoding |
| `fact` | the fact's name (from `facts.def`, §11.3) |
| `grain` | `pattern` (node-grain facts are not listed; the row gives the root value where one exists, e.g. `minw`) |
| `epoch` | `E1`/`E2`/`E3` |
| `status` | CLOSED vocabulary: `derived` / `denied` / `declined` / `absent` (§11.4) |
| `used` | `yes` if a pass asked for the fact before emission finished, `no` if only the listing asked (§11.4) |
| `value` | rendered by the fact's ONE renderer: the byte as decimal, the run as hex plus `@idx` (the `REQ_RUN` spelling), a set as a sorted byte list, the anchor by `pcrec_start_anchor_name` |
| `why` | CLOSED token + detail: `deny:<flag>` with the flag's spelling from `axes.def` (e.g. `deny:-fno-req-byte`); `decline:<reason>` (e.g. `decline:enc-multibyte` for `end_window` under `utf8`, `endwin.c:164`; `decline:no-forward-nfa` for E3 on a no-DFA VM route); for a derived pick, `rate:<source>` or `rate:none(<encoding>)->rightmost` (the §6.3 NONE rule that answered); empty for a plain derivation |
| `note` | prose, no promise of wording (`ir_listing.md` `note` precedent, D26) |

**`#section rate`**: one row per rate QUERY the compile consumed (§6.3). It
gives the query, the source (bundle name and digest, or `none` with the
undeclared encoding) and the NONE rule applied. The tokens are the ones
`<P>_FINDINGS` stamps (`findings/design.md` §7). Values are NOT repeated:
`--list-analysis NAME` (D123 addendum, B2) prints them, so there is one
printer per datum.

**`#section decisions`**: the emission DECISIONS that read the record
(§4.4). This covers `REQ_WHY`, `DFA_PREFILTER` (+ `OFFSETS`), `ENGINE`/
`ENGINE_WHY`/`ENGINE_SEL`, `VM_PREFILTER`, the search form and every other
stamp the prologue writes, as `(stamp, value)` rows. **These rows are
RECORDED AS THE STAMPS ARE WRITTEN**: the prologue's stamp emitter appends
each `(name, value)` to a per-attempt list in the same call that writes the
`#define`. The listing prints that list. This is `--emit-ir`'s own rule (a
byproduct of the emitter's walk, D106/D108) applied to stamps. The
decisions section therefore IS the artifact's stamp block, and nothing
re-asks `req_admit` or `DFA_SELECT` to fill it. Decisions stay out of the
record (§4.4); they are inspectable anyway.

### 11.3 One printer, never a recomputation

1. **One table defines the facts:** `src/opt/facts.def`, an X-macro
   (`src/core/axes.def`'s precedent) with one row per fact giving name,
   epoch, deny bit, empty value and renderer. From it the build generates the
   `PatFacts` members' accessor declarations, the deny application in
   `facts.c` (§7.1) AND the listing's row order. A fact that exists has a
   row, by construction. The "populations nobody counts" failure (K35) cannot
   hide a fact from the dump.
2. **The printer reads the memo.** `src/dump/facts_dump.c` (NEW, beside
   `axes_dump.c`) iterates `facts.def` and, for each row, reads
   `Job.pf`'s value, status, why and asked bit. It never calls an owner's
   derivation. The §4.2 grep check allows `facts.c` and the owners only, and
   `facts_dump.c` is NOT allowed.
3. **Status and why are STORED, not reconstructed.** The accessor records
   `status`/`why` when it stores the value (§2's four steps). A deny writes
   `deny:<bit>`. A derivation that declines returns a `PfWhy` code with its
   empty value (for example `pcrec_end_window` returns `-1` +
   `PF_WHY_ENC_MULTIBYTE`). The derived pick stores which §6.3 NONE rule
   answered. The listing prints what the pass saw. It never infers "the
   value is -1, so it must have been declined".
4. **The renderer is shared with the stamps.** Each `facts.def` row names a
   renderer, and the prologue's fact-valued stamps call the SAME renderer
   (§11.5). One spelling of each value exists.

### 11.4 Unasked facts, absent epochs, and not perturbing the artifact

The record is lazy (§2), so a compile may finish without asking some facts.
For example, a DFA artifact never asks the VM's facts. The listing must
still show every fact. **After the artifact is complete** (after emission
and after the stamp and findings consumption record are rendered),
`--emit-facts` asks every unasked accessor once. That is the SAME accessor
and the SAME derivation, not a recomputation beside it. Each such row reads
`used no`.

This keeps both halves honest:
- `used` says exactly which facts the passes consumed.
- The listing is complete.
- Because the extra asks happen after the artifact bytes and every stamp
  exist, they cannot move the artifact or the `<P>_FINDINGS` consumption
  record. That one ordering fact is load-bearing, and it has a check (§11.6).

An accessor whose epoch was never reached on this route (E3 on a no-DFA VM
route) is not forced. Forcing it would build an NFA the compile never built.
It lists as `status absent`, `why decline:no-forward-nfa`. Only the FINAL
compile attempt's record is listed (the retry ladder, `findings/design.md`
§6.4's rule). One listing row per attempt would be a different feature
(D77: not asked for).

### 11.5 Should the existing stamps derive from the same record? YES for facts, CAPTURED for decisions

| stamp | kind | after this design | abi |
|---|---|---|---|
| `REQ_BYTE`, `REQ_RUN` | record FACTS (derived pick, window) | the prologue reads the accessor and renders with the fact's `facts.def` renderer, the same one the listing uses. Lands with step 3.0 (§9), which already moves these fields into `Job.pf` | no: byte-identical, and the renderer is today's text moved |
| `VM_START` | record FACT (start anchor) | same, via `pcrec_start_anchor_name` (already the one spelling, `startanch.c:153`) as the fact's renderer | no |
| `REQ_WHY`, `DFA_PREFILTER`, `DFA_PREFILTER_OFFSETS`, `ENGINE*`, `VM_PREFILTER`, `DFA_START` | DECISIONS (§4.4) | unchanged derivation, one owner each (`req_why_name`, `dfa_prefilter_name`, …). Their stamp writes are CAPTURED into §11.2's decisions list | no |
| `<P>_FINDINGS` | the findings consumption record | unchanged (findings §7). The `rate` section reuses its tokens | — (B1's own event) |

**Why not move decisions into the record to derive their stamps from it:**
§4.4's boundary (D124: "which check runs where" is a different question from
"what the pattern has"). Capturing the stamp as it is written gives the same
guarantee, "the listing cannot disagree with the artifact", without
widening the record. **Why facts' stamps must move:** otherwise
`REQ_RUN`'s hex@idx spelling exists twice (prologue and dump). That is the
parallel-renderer version of R13.

### 11.6 Checks (each born with a sabotage row, learnings §3)

1. **Non-perturbation:** for every corpus pattern × {byte, utf8}, the
   artifact from an ordinary compile is byte-identical to the artifact a
   `--emit-facts` compile would have emitted. The query builds the artifact
   in memory, so a test hook writes it. Sabotage: move §11.4's force-all
   pass before stamp rendering. The `<P>_FINDINGS` line then moves (after
   B1) or `used` flips, and the check must fail.
2. **Completeness:** the listing has exactly one `facts` row per `facts.def`
   row, per encoding. Its population is counted against the table and not
   against a literal. Sabotage: a `facts.def` row whose printer arm is
   skipped.
3. **Why-truthfulness against an INDEPENDENT source:** for each fact-deny
   flag in `axes.def`, compiling with that flag lists `deny:<that flag>` on
   exactly the facts `facts.def` says it empties, and on no other.
   Comparing listing against listing would share a source (learnings §3).
   The control is the deny sweep's own flag list, which the listing does not
   produce.
4. **Decisions = stamps:** the `decisions` section equals the artifact's
   `#define` block, parsed from the emitted C. Those are two renderings, one
   of which is the artifact itself.

### 11.7 Contract or debug surface: a DEBUG LISTING with a spec page (recommended)

| option | for | against |
|---|---|---|
| (a) a stable CONTRACT (rows and values promised, D76-style) | tools could key on fact names | every migration step (§9) adds or renames rows. A promised row set would make step 3 an abi-like ritual per step and freeze internal fact names that §9 still has to move. The facts are internal (D80 covers what a CALLER can observe) |
| (b) explicitly unstable, no spec | free to change | it is a CLI flag, and a caller CAN observe it. D80 then requires a spec hunk anyway. Unspecified output also violates the table contract's at-birth rule |
| **(c) `--emit-ir`'s status (RECOMMENDED)** | `docs/spec/ir_listing.md` is the ruled precedent (D106 addendum 2): "a DEBUG listing", with a spec page stating what IS and IS NOT promised | — |

Under (c), a new `docs/spec/facts_listing.md` promises:
- the table-contract framing;
- the three section names and their COLUMNS (append-only);
- the CLOSED `status` and `used` vocabularies and the `why` token grammar
  (`deny:<axes.def spelling>` / `decline:<reason>` / `rate:...`);
- the non-perturbation guarantee (§11.6 item 1).

It does NOT promise the row set (fact names), value spellings beyond those
shared with a stamp (and those are `match_api.md` §6.3's), `why` reason
names, or `note` text. It is not part of the artifact, so there is no `abi`
number. `docs/spec/cli.md` §2 gains the flag's entry (D80), in the same
change that lands it.

**Alignment with [FINDINGS]' D123 inspection.** D123's addendum puts bundle
inspection on `--list-analyses`/`--list-analysis`. Those are the `--list-*`
family: pattern-free REGISTRY tables, table contract at birth.
`--emit-facts` is the `--emit-*` family: a per-compile BYPRODUCT that needs
a pattern, like `--emit-ir`. The two do not overlap. The `rate` section
names the analysis with `<P>_FINDINGS`'s tokens, and `--list-analysis`
prints its values. Each datum has one printer.

### 11.8 When it lands, and what it does not do

It lands WITH step 3.0 (§9). 3.0 creates `facts.def` and `Job.pf` for the
E2 req/anchor/window facts and moves `REQ_*`/`VM_START` to the shared
renderers. The listing's row population then grows with each migration step
for free (§11.3 item 1). B1 adds the `rate` section. It is not an abi event
(§11.5). It does NOT:
- list node-grain facts (per-node output is `--emit-ir`'s territory for the
  VM program; a node-fact listing waits on a named need);
- keep facts from rejected compile attempts;
- print rate VALUES.

## 12. Open questions for Frank

Each is a genuine ruling. Spellings, file names and step sizing are the
manager's.

1. **Three sealed epochs instead of the charter's one point.** D120 says
   "computed after `pcrec_lower_enc`". This design adds E1 (pre-lowering
   structural facts, because `select_engine` needs them before lowering)
   and E3 (NFA facts, because the pin is one). The alternative, moving
   `select_engine` after lowering, changes the pipeline order that
   `possessify`/`revdet` depend on. **Recommend: accept the three epochs.**
2. **Lazy memoized accessors, not an eager struct.** D120 left both open
   ("a `PatFacts` … or a family of memoized queries"). **Recommend: the
   memoized queries** (§2's lens table: pay-for-what-you-use, dependency by
   call, no fill-order hazard).
3. **Fact denies stay FACT-level:** a denied fact is "nothing to find" for
   every consumer, so `-fno-req-byte` keeps removing the pin, and
   `-fno-vm-anchor-bound` keeps removing G2's one-attempt admission. The
   spec lists each fact-deny's consumers (D80). No per-consumer use-deny
   is built until an attribution needs one. **Recommend: yes, as §7.**
4. **The prior's NONE answer is spelled once per QUESTION KIND (pick /
   compare / mass) inside findings primitives, not per reader.** This
   amends the ratified-and-panelled `findings/design.md` §6.2-§6.3. The
   delta's R13 is the reason: the per-reader shape is where the two copies
   diverged. **Recommend: adopt, and apply it to findings §6.1-§6.3 as a
   manager edit before B1 opens.**
5. **The record excludes route and emission DECISIONS** (`req_admit`,
   `DFA_SELECT` choices, `OfsTest`, `vm_frameless`, `fit`). They stay one
   derivation each in their owner, per D124's "one table per question".
   D122(3)'s carried facts are then a DECISION published by its owner, not
   a pattern fact. **Recommend: yes.**
6. **S2b (carried verified facts) is deferred** behind a named bench
   trigger that follows S2a, even though D125 addendum 1 names S2 as a
   first customer. S2a (the VM exact compare) is specified and buildable
   against the record now. **Recommend: build S2a only.**
7. **File a row to derive `rx_info.flags`' `strategy_denials` mask from an
   `axes.def` classification column** (fact / row / value / answer), after
   K68 merges. The bit-19 fix and K68 are this class's two incidents.
   Under D125 it is filed, not scheduled. **Recommend: file it.**

8. **`--emit-facts`' status: a DEBUG LISTING with a spec page**
   (`ir_listing.md`'s precedent: format and vocabularies promised; row set,
   value spellings and reasons advisory; no `abi`), rather than a stable
   contract or an unspecified debug flag (§11.7). **Recommend: (c).**
9. **Fact-valued stamps (`REQ_BYTE`, `REQ_RUN`, `VM_START`) render from
   the record through the listing's renderers. Decision stamps stay with
   their owners and are CAPTURED as written** (§11.5), rather than moving
   decisions into the record. It is byte-identical, with no `abi`.
   **Recommend: yes.**
10. **The listing forces unasked facts AFTER the artifact is complete**
    and marks them `used no`, rather than printing `unasked` rows with no
    value (§11.4). The trade-off is completeness for a debugger versus the
    listing computing something the compile did not. The derivation is the
    same one, and non-perturbation is checked. **Recommend: force, after
    emission.**

---

## 13. Pointers

D120 (`decisions.md:8153`), D122 + addenda (`:8288`), D123 + addenda
(`:8369`), D124 (`:8504`), D125 addendum 1 (`:8573ff`); `inventory.md` +
its Delta; `findings/design.md` §6, §11.3, §13; `litscan_s1.md` §1.1,
§1.5; `compare_stack.md` §1, §4 (P3/P6/P7), §5, §6.1, §7 Q3;
`reqbyte_freq_pick.md` §3; `reqpos_2b.md` §2.3 + its 2026-09-26
amendment (on `lane/reqrunenc2`); `docs/dev/optloop/reqrunenc_census.md`;
`docs/dev/optloop/vmlit_trigger_read.md` §3; `variables_pattern.md` §2;
`known_issues.md` K64-K68. APPROACH.md's "two engines" amendment (D124) is
due after this step. This design supplies its "one analysis record"
paragraph (§0 items 1-8).
