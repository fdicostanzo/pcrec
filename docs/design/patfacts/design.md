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

**Revision log.**
- Revision 1, 2026-09-26 (lane pfdesign): the design as panelled.
- **Revision 2, 2026-09-26: D6 panel r1 + Frank's relocation question**
  (lane pfrev; `docs/dev/reviews/2026-09-26-r1-patfacts-design.md`). Every
  FIX row is applied, and each carries its finding ID inline as `[r1 ID]`.
  The largest change answers Frank's question ("does keeping each analysis in
  its first consumer's pass file cause crazy interdependencies?"). The
  PROPOSED layout is now an ANALYSIS LAYER, `src/facts/` (§4.2, ADOPT WITH
  CARVE-OUTS (a)-(e), for Frank as §12 Q11). The one-caller grep check is
  replaced by an include-graph and link check (§4.2.3). Also changed: E1 is
  forced eagerly at its seal and drops the root character widths (§3). E3 is
  sealed per branch (§3). Step 3.4 is flagged as a possible mover (§9). §9
  gains a mover-classification procedure and its per-family relocations.
  §8.1's "B1 first" fallback is deleted. S2a is now stated to exercise none
  of the pattern-grain machinery (§0, §8.2, Q6). Two of §11.6's checks take
  independent oracles, and §11.6's non-perturbation check is born with B1.

---

## 0. Decisions first

1. **The record is a family of LAZY, MEMOIZED ACCESSORS over `Job`, not an
   eager struct filled at one pipeline point** (§2). A fact is computed on
   its first ask, cached for the rest of the compile attempt, and reset
   with the attempt's `Job` (`compile.c:908` callocs one per attempt, so
   the retry ladder resets it for free).
2. **Facts are SEALED BY EPOCH, and there are three epochs, not one** (§3).
   E1 (structural) is sealed after `pcrec_callgraph_build`
   (`compile.c:1397`), and its facts are FORCED EAGERLY at that seal, because
   `pcrec_lower_enc` rewrites the tree in place (`:1488`) and a lazy E1 answer
   would depend on when it was asked [r1 A1]. E2 (lowered) is sealed after
   `pcrec_lower_enc` (`:1488`). E3 (machine) is sealed PER BRANCH, and only
   on the branch that wraps the forward NFA (`pcrec_nfa_wrap_unanchored`,
   `:1654`, inside `:1651`'s `ENG_UNANCH` arm). The `ENG_ATTEMPT` arm
   (`:1685-1686`) builds a forward NFA (`:1539`) but never wraps it. Its E3
   facts DECLINE with their own token and are never forced [r1 A3]. The
   charter's "after `pcrec_lower_enc`" is E2. E1 exists because
   `select_engine` asks nullability and kind-presence BEFORE lowering
   (`select_engine.c:568, 611, 658, 686`). E3 exists because the run pin is
   an NFA fact. A fact is
   published only once nothing can revoke it, so the step-1 "revocable
   fact" problem (`revbody`) cannot arise inside the record. The
   `revbody` case is a REWRITE correcting a rewrite, and the record does
   not hold rewrites (item 6). An accessor asked before its epoch is an
   internal-error refusal. That turns step 1's implicit `pcrec_minw`
   contract into a checked one.
3. **Core vs derived is a field-level split, and the delta already shows
   it** (§4). CORE facts come from a walk: the necessary SET, the WHOLE
   run, the anchors, the root byte width and nullability, the kind mask, and
   the k-set walk. A core fact reads no prior, which is why the k-set walk's
   per-offset `ppm` moves into the selection half (§4.2, [r1 A2]). DERIVED
   facts are functions of core facts plus a prior or a second core fact:
   the pick, the run's scan member and window, and the pin. A derived fact
   never re-walks a tree. The one cross-derivation dependency that must
   survive migration unchanged is S1's pin, which is over the DERIVED
   window (`litscan_s1.md` R3-2), not the whole run.
4. **ONE owner per derivation, in an ANALYSIS LAYER, `src/facts/`**
   (§4.2; revision 2, answering Frank's relocation question; for ruling as
   §12 Q11). The layer has one file per fact family: `req.c` (the necessary
   set/run walk lifted out of `reqbyte.c`), `kset.c` (the k-set walk and the
   pin, lifted out of `prefix_k.c`), `startanch.c`, `endwin.c`, `kinds.c`
   and `widths.c`. Beside them sit `facts.c` (memo, epoch guard, deny, the
   listing's force loop) and `facts.def` (the table). A derivation depends
   only on the IR/NFA and the node-grain primitives over it. It reaches other
   facts only through the dependency DAG declared in `facts.def`, and its one
   encoding input is the encoding DESCRIPTOR, which is declared. DECISIONS
   stay in their passes (G1's `req_byte_dominated_by`, the offset-k
   selection). Consumers include only `facts.h`. The derivations are declared
   in a facts-private header, and an include-graph plus link check enforces
   that (§4.2.3). That cures R1/R2/R14 by construction and removes the
   "first consumer's file owns the analysis" shape R13 grew in.
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
   **So S2a exercises none of the pattern-grain machinery: no memo, no
   epoch, no deny.** Its fact is a node-grain pure function (§4.3). Beyond
   the migration itself, the machinery's customers are step 3.0 (the E2
   req/anchor/window accessors and their denies) and B1 (the deny's effect on
   the consumption record, and the rate accessor) [r1 A6]. Whether S2a is
   built now or waits for S2b as the machinery's real outside customer is
   §12 Q6. **S2b** (D122(3)'s carried facts) is specified here and NOT built:
   its trigger is named.
10. **Migration** (§9): the internal.h split and the skeleton first,
    byte-identical (3.0). Then B1, the abi event. Then one existing analysis
    at a time, each byte-identical under a named gate, each family's
    relocation into `src/facts/` riding its own step, one relocation per
    commit. **A migration step that moves an emitted byte is classified
    before anything else happens** (§9.1, [r1 C1]). A SEMANTIC mover (a
    value, a stamp or a code path differs) is a FINDING: two copies
    disagreed. The step stops and files a K-row, and the mover must not be
    absorbed into an abi bump. A SCAFFOLDING mover (text, comment or layout
    only) is the ordinary D76 ritual, with the diff attached to justify the
    class.

11. **The record is INSPECTABLE** (§11, scope addition from Frank,
    2026-09-26). A query `pcrec --emit-facts --pattern P` (spelling: the
    manager's, `--emit-ir`'s query precedent) prints every fact, its status
    and WHY, per encoding. ONE printer renders every row from the record's
    memo, which is the same object the passes read. The fact-valued stamps
    (`REQ_BYTE`, `REQ_RUN`, `VM_START`, `END_WINDOW`) render through the
    same per-fact renderer, so a stamp and the dump cannot disagree. It is a DEBUG
    LISTING under a spec page (`ir_listing.md`'s status): a format contract
    with advisory rows, not ABI.

---

## 1. The record in one table

Epoch: E1 structural, E2 lowered, E3 machine (NFA). "Deny" means the
fact-level deny applied inside the accessor (§7). Grain: P = pattern
(memoized), N = node (pure function). The owner column gives the PROPOSED
home under `src/facts/` (§4.2) and today's site. A consumer is a site that
asks the PATTERN fact at the root. A node-grain call on a subtree is not a
consumer of a pattern fact [r1 A8, F2].

| fact | grain | kind | epoch | owner: proposed file ← today's site | deny → empty value | consumers (each with its hat, §4.5) |
|---|---|---|---|---|---|---|
| kind mask `{BREF, CALL, LINKED_CALL, VAR, ATOMIC, LOOK, LIVE_CAPTURE, COLLAPSIBLE_REP}` | P | core | E1 (eager) | `src/facts/kinds.c` ← the root calls of the `atomic.c` predicates (`:59/149/221/565/807/919/954`) and `pcrec_has_var` (`mod_vars.c:273`); the node predicates stay node-grain (§4.2.1) | — | `select_engine` (`:571/611/658/686`, forcing and prefilter), `fit.prefilter_has_collapsible_rep`'s reader `compile.c:1585` (the copy migrates, [r1 A7]), `emit_vm.c:13191/13208` (the `--emit-ir` listing, R1), `emit_vm.c:9980` (`mrl_win`) |
| language nullable | P | core | E1 (eager) | `src/facts/widths.c` ← `pcrec_minw(root) == 0` (`mrl.c:120`), asked today at `select_engine.c:568` | — | `fit.lang_nullable`'s readers (`compile.c:1620`, `select_engine.c:837`; the copy migrates, [r1 A7]), `pcrec_startgate_needed` (`nfa.c:1150`), `[OPT-4.1]` gate |
| byte min width (root) | P | core | E2 | `src/facts/widths.c` ← `pcrec_minw(root)` | — | the VM's root checks |
| start anchor | P | core | E2 | `src/facts/startanch.c` ← `pcrec_start_anchor` (`startanch.c:143`) | `-fno-vm-anchor-bound` → `NONE` | VM attempt bound; DFA's one-directional assertion (`emit_dfa.c:7860-7867`, [r1 F3]); **G2** (`:5883-5890`, delta D.2) |
| end window | P | core | E2 | `src/facts/endwin.c` ← `pcrec_end_window` (`endwin.c:154`). Declared input: the encoding DESCRIPTOR (§4.2.2 (d)). Its root `pcrec_cwmax` call (`:172`) is internal to this derivation and gated to single-byte encodings (`:164`) | `-fno-end-window` → `-1` | both emitters' window clamp; `END_WINDOW` (`emit_dfa.c:8567-8571`) |
| necessary SET | P | core | E2 | `src/facts/req.c` ← `rb_walk` and its lattice (`reqbyte.c:164-498`) | `-fno-req-byte` → ∅ | K65 set-rest (no-DFA-scan VM only); the pick (below) |
| necessary WHOLE run | P | core | E2 | `src/facts/req.c` ← `rb_walk`'s `runs.best` | `-fno-req-byte`, `-fno-req-run` → len 0 | K66 whole-run compare (no-DFA-scan VM only); the window (below) |
| necessary byte (pick) | P | derived | E2 | beside B1's rate primitives (§4.2.2 (b)) ← `rb_pick` (`reqbyte.c:517`), from set + byte-rate | as the set | `REQ_BYTE`, the one-byte pre-check, G1 |
| run scan member + window | P | derived | E2 | beside B1's rate primitives ← `rn_scan_index`/`rn_window_start` (`reqbyte.c:539/559`), from whole run + byte-rate | as the run | `REQ_RUN`, the run pre-check, **S1's pin** |
| k-set walk `k[0..nwalk)` | P | core | E3 (UNANCH branch only) | `src/facts/kset.c` ← `pcrec_prefix_ksets`' walk half (`prefix_k.c:185-248`, `:409-477`), WITHOUT its per-offset `ppm` (`:443`, `:475`), which moves to the selection [r1 A2] | — (it is a walk over the NFA; each USE has a row deny) | offset-k selection (stays in `prefix_k.c`, §4.2.2 (c)), the pin |
| run PIN `(run_o)` | P | derived | E3 (UNANCH branch only) | `src/facts/kset.c` ← `prefix_k.c:484-491`, from k-set walk ∩ window. A pure NFA+window fact: today's call is gated on the prefilter kind (`emit_dfa.c:3719`), the fact is not | inherits the run's deny (`len 0` → unpinned) | `dfa_pfs[]` run rows, `OfsTest`, G1 (`run_verified`); S2b (not built). **Consumer obligation on every row: the kind gate** (`pf_run_applies_common`'s `u->kind == DFA_PF_NONE` test, `emit_dfa.c:5294`) [r1 A2] |
| byte-rate | P (per compile) | DATA | — | findings accessor (B1), `Ctx`-memoized | — (the data declares; NONE = not declared) | the three rate primitives only |
| `minw(node)`, `cwmin`/`cwmax(node)`, nullable(node) | N | core | E2 (widths: any) | `pcrec_minw`, `pcrec_cwmin`/`pcrec_cwmax` (`mrl.c`), `vm_nullable` (R4: two copies, §9 step 3.5) | — | the VM emitter (≥9 sites), `callgraph.c`, `startanch.c:84`, `endwin.c:93`, `mod_lookaround.c` (`la_widths`) |
| singleton byte | N | core | E2 | `pcrec_cls_single` (`cpset.c:305`, R12) | — | `rb_walk`, `altcls`, `emit_vm.c:3659`, **S2a** |
| emission-contiguous literal run | N | core | E2 | **NEW with S2a**, over `pcrec_cls_single` | — | S2a (VM chain emit, `vm_cost`, `vm_count_slots`: one function, three readers) |

**Root character widths are NOT a record fact** [r1 A1, A8]. Revision 1
listed `cwmin`/`cwmax` (root) at E1. Its only root reader is
`endwin.c:172`, which runs at E2, inside the end-window derivation, gated to
single-byte encodings. `startanch.c:84` and `endwin.c:93` ask subtrees, and
`startanch.c:80` is prose about a rejected alternative. A pattern fact with no
pattern-grain consumer is built ahead of need (D77). It would also carry
A1's hazard: a lazy root `cwmax` asked after `pcrec_lower_enc` computes BYTES
on the lowered tree (`é` gives 2) while labelled characters. So the widths stay
node-grain pure functions.

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
/* src/facts/facts.h — the CONSUMER header (§4.2): types + accessors only.
 * core/internal.h includes it for Job.pf; it declares no derivation. */
typedef enum { PF_E0 = 0, PF_E1_STRUCT, PF_E2_LOWERED, PF_E3_MACHINE } PfEpoch;
typedef struct {
    uint32_t have;          /* one bit per memoized fact: "asked and cached" */
    uint32_t used;          /* one bit per fact: asked by a PASS (§11.4) */
    PfEpoch  epoch;         /* advanced ONLY by compile_driver at the seals */
    bool     e3_sealed;     /* E3 is per BRANCH (§3): set only on ENG_UNANCH */
    unsigned kinds;         /* E1, forced at the seal */
    bool     nullable;      /* E1, forced at the seal */
    long long minw;         /* E2, bytes */
    int      start_anchor;  /* E2 */
    long long end_window;   /* E2 */
    ReqSet   req_set;       /* E2 core   (today Job.req_set)  */
    ReqRun   req_run;       /* E2 core `whole` + derived window (today Job.req_run) */
    int      req_byte;      /* E2 derived (today Job.req_byte) */
    PrefixKWalk kwalk;      /* E3 core: the walk half of PrefixKSets, no ppm */
    bool     run_pinned; int run_o;   /* E3 derived */
    PfWhy    why[PF_NFACTS];/* stored status/why per fact (§11.3 item 3) */
} PatFacts;                 /* Job.pf */

/* src/facts/facts.c — every lazy accessor has this shape */
const ReqSet *pcrec_fact_req_set(Ctx *cx);   /* E2; deny -fno-req-byte -> empty */
```

Revision 1 carried `cwmin`/`cwmax` here. They are gone, because root
character widths are not a record fact (§1, [r1 A1]).

Each LAZY accessor (E2, E3) does four things, in this order:
1. **Epoch guard:** `if (cx->job->pf.epoch < E) pcrec_ctx_fail(... "internal error")`.
   An E3 accessor on a branch that never sealed E3 (`!e3_sealed`) is not an
   internal error. It returns the fact's empty value with its decline token
   (§3, §11.4).
2. **Memo:** return the cached value if `have` has the bit.
3. **Deny:** if the fact's deny bit is set, store the empty value (§7).
4. **Derive:** otherwise call the owner's derivation ONCE, store the
   result, and set the bit.

**E1 facts are EAGER, not lazy** [r1 A1]. `compile_driver` calls one
`pcrec_facts_seal_e1(cx, root)` right after `pcrec_callgraph_build`
(`compile.c:1397`). It derives the kind mask and nullability on the
structural tree and stores them, and the E1 accessors are then pure reads.
The reason is `pcrec_lower_enc`, which rewrites the tree IN PLACE
(`compile.c:1488`, whose own comment says so at `:1464`). A lazy E1
accessor first asked after lowering would walk the lowered tree. Kind-presence
and nullability happen to be invariant under lowering (§3), but an answer
that depends on ask time is the hazard this design exists to remove. Forcing
at the seal makes the answer a function of the seal, not of the asker. It
costs no new work: `select_engine` asks both facts on every compile today
(`select_engine.c:568, 571, 611, 658, 686`).

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
| E1 structural | after `pcrec_callgraph_build` (`:1397`), before `pcrec_select_engine` (`:1424`) | Every later pass rewrites only (a) FLAGS on nodes (`possessive`, `revbody` by select_engine; `u.look.widths` by postresolve), or (b) `A_CLASS` contents, introducing only `A_CLASS`/`A_CAT`/`A_ALT`/`A_EMPTY` (`lower_enc.c:223-382`: the node kinds it allocates). Hence kind-presence is invariant. A non-empty class lowers to a non-empty byte sequence, so nullability is invariant. Both facts are FORCED here, eagerly (§2, [r1 A1]) | kind mask, nullable |
| E2 lowered | after `pcrec_lower_enc` (`:1488`), i.e. where `start_anchor`/`end_window`/`req_*` are computed today (`:1501-1520`) | `lower_enc` is the last tree rewrite | byte `minw`, start anchor, end window, necessary set, whole run, the pick, the window |
| E3 machine | PER BRANCH [r1 A3]. Sealed ONLY inside the `ENG_UNANCH` arm (`:1651`), right after `pcrec_nfa_wrap_unanchored` (`:1654`) and before the first DFA build. The `ENG_ATTEMPT` arm (`:1685-1686`) never seals it | the count-collapse ladder REBUILDS `Job.nfa` (`:1648-1649`), so any walk before that point can be stale. `pcrec_dfa_scan_state_written` (`:1681`, `:1683`, [r1 F1]) is today's first `unanch_start` ask, and it comes after the seal | k-set walk, pin |

**E3 is sealed only where the forward NFA is WRAPPED, and there are two
routes where it is not** [r1 A3]. Revision 1 said "E3 exists on a route that
builds a forward NFA". That is false on `ENG_ATTEMPT`: the forward NFA is built
at `:1539` (and possibly rebuilt collapsed at `:1649`), but only the
`ENG_UNANCH` arm wraps it (`:1651-1654`). The `ENG_ATTEMPT` arm (`:1685-1686`)
builds its DFA from the unwrapped machine. So the seal is written inside the
`ENG_UNANCH` arm and nowhere else, and the E3 accessors answer by route:

| route | E3 sealed | E3 accessors return | listing `why` (§11.4) |
|---|---|---|---|
| `ENG_UNANCH` (DFA or hybrid, `:1651`) | yes, after `:1654` | the derived value (lazy, memoized) | empty, or a deny token |
| `ENG_ATTEMPT` (`:1685`) | NO | the empty value, never derived | `decline:attempt-unwrapped-nfa` |
| no-DFA VM (no `:1538` build) | NO | the empty value, never derived | `decline:no-forward-nfa` |

Both declines are NAMED and neither is ever FORCED by the listing (§11.4). On
`ENG_ATTEMPT` a forced walk would run over an NFA whose meaning (an
anchored-attempt machine) is not the one the pin's contract states. Today
`pcrec_prefix_ksets` is reached only from `unanch_start` (`emit_dfa.c:3720`),
so both declines reproduce today's behaviour exactly. `[OPT-VMSEED]` (§10,
not built) is the fact customer that will need an AST-level offset bound on
the no-DFA route.

**The E1 invariance claim is a PROOF plus a CHECK.** The proof is the
table's middle column. The check is born with step 3.2: under the existing
debug self-check build shape (`cstart_check_omission`, `nfa.c:1086`, is
the precedent: "a deliberate independent re-derivation"), re-derive the E1
facts on the E2 tree and fail on disagreement. It is not a second source
of truth. It is a cross-check that runs on the same function over a later
tree. Now that E1 is forced at the seal, the cross-check cannot be satisfied
by an ask-time accident either: the stored value is the structural tree's,
and the re-derivation is the lowered tree's. The check covers both E1 facts,
so it has one sabotage row per fact [r1 C6]:
- **kind mask:** plant an `A_BREF` in `lower_enc`'s output. The mask's
  `BREF` bit then disagrees.
- **nullability:** make `lower_enc` emit `A_EMPTY` for a non-empty class
  (the one lowering that could break "a non-empty class lowers to a non-empty
  byte sequence"). On a pattern whose only consuming node is that class, the
  E2 re-derivation reads nullable and the stored E1 fact reads not nullable.

Revision 1 also claimed width invariance. That claim is withdrawn, because
root widths are no longer an E1 fact (§1).

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

### 4.2 Ownership: one derivation, in an analysis layer (revision 2)

**Revision 1 said "the derivations do not move files".** `facts.c` would
call each owner where it lives today, and a grep check would forbid other
callers. Frank asked (2026-09-26 evening) whether keeping each analysis in its
first consumer's pass file "cause[s] crazy interdependencies when area A
writes the analysis but it's used by unrelated area B or even C". The
`[OPT-REQRUN-ENC]` incident is that shape. The run pick evolved inside
`reqbyte.c` as a REQPOS-specific choice and silently diverged from its twin
(R13). pfcrit-arch's verdict was **ADOPT WITH CARVE-OUTS**. No core fact
needs a pass's internals:
- `rb_walk` and its lattice (`reqbyte.c:164-498`) read only the `Ast`;
- the k-set walk (`prefix_k.c:185-248`, `:409-477`) reads only the `Nfa`;
- the end window and the start anchor read the `Ast`, plus (end window only)
  the encoding descriptor (`endwin.c:156-164`).

The one real coupling is the pin AS USED TODAY. It is computed only when the
prefilter kind is not `DFA_PF_NONE` (`emit_dfa.c:3719`), i.e. it is gated on
`unanch_start`'s start-state verdict. The cure is to make the pin a pure
NFA+window fact and to make the kind gate an explicit CONSUMER obligation.
`pf_run_applies_common` already carries it (`emit_dfa.c:5294`), and §1's pin
row now states it for every consumer.

This revision drafts the relocation as the PROPOSED layout. It goes to Frank
as §12 Q11.

#### 4.2.1 The layout

`src/facts/` is a new layer directory (the Makefile's `LIBSRCS`,
`Makefile:108-111`, gains `$(wildcard src/facts/*.c)`, and the directory
gets its own `CLAUDE.md`). It holds one file per fact FAMILY:

| file | holds | moves from | moved in step (§9) | stays behind, and why |
|---|---|---|---|---|
| `facts.def` | the X-macro table: one row per fact (name, epoch, grain, deny bit, empty value, renderer, OWNER file, DEPENDS-ON facts) | NEW | 3.0 | — |
| `facts.h` | the CONSUMER header: `PatFacts`, `PfEpoch`, `PfWhy`, the `pcrec_fact_*` accessors, `pcrec_facts_seal_*`. No derivation | NEW | 3.0 | — |
| `facts_derive.h` | the FACTS-PRIVATE header: every derivation's declaration | NEW, from `core/internal.h` (carve-out (a)) | 3.0a | — |
| `facts.c` | the memo, the epoch guard, the deny application, the E1 seal, the listing's force loop | NEW | 3.0 | — |
| `startanch.c` | `pcrec_start_anchor` and `sa_walk` | `src/opt/startanch.c` (whole file) | 3.0 | nothing |
| `endwin.c` | `pcrec_end_window` and its walk | `src/opt/endwin.c` (whole file) | 3.0 | nothing |
| `req.c` | `rb_walk` and its set/run lattice (`reqbyte.c:164-498`), and the core facts' entry | `src/opt/reqbyte.c` | 3.0 | `rb_pick`, `rn_scan_index`, `rn_window_start` (`reqbyte.c:517-588`) stay in `reqbyte.c` until B1 moves them beside the rate primitives (carve-out (b)); `reqbyte.c` is then deleted |
| `kinds.c` | the ROOT kind-mask derivation | NEW (it composes the root calls now at `select_engine.c:571/611/658/686`, `emit_vm.c:9980/13191/13208`) | 3.2 | the recursive node predicates stay in `atomic.c` and `mod_vars.c` (§4.2.2, node grain) |
| `widths.c` | the root nullable (E1) and root byte `minw` (E2) facts | NEW (composes `pcrec_minw(root)`) | 3.2 | `pcrec_minw`/`pcrec_cwmin`/`pcrec_cwmax` stay in `mrl.c`: they are node-grain pure functions (§4.3) |
| `kset.c` | the k-set WALK (`Walk`, `wpush`, `wclose`, `frontier_union`, the walk loop) and the PIN | `src/opt/prefix_k.c:185-248`, `:409-491` | 3.4 | the SELECTION stays in `prefix_k.c` (carve-out (c)): `verify_cost`, `model_cost`, the scan-offset choice, and the per-offset `ppm` the walk reads today (`:443`, `:475`), which moves into the selection so the core walk reads no prior [r1 A2]. `set_ppm` itself (`:325`) joins the rate primitives in B1 (carve-out (b)) |

**Where the layer sits.** `tools/review/include_graph.py`'s `LAYER_ORDER`
(`:113`) gains `facts` between `ir` and `opt`. The layer reads `core`
(`Ast`, `Ctx`, `Job`), `enc` (the descriptor), `ir` (the `Nfa`) and the
node-grain primitives. `opt` and `gen` read `facts.h`. One edge needs saying.
The node-grain primitives the facts compose (`mrl.c`'s widths, `atomic.c`'s
predicates) live under `opt/` today, so `facts → opt` reads as a back-edge in
the layer matrix. It is a pre-existing shape: `parse → opt` already exists at
`mod_lookaround.c:534` → `pcrec_has_call`. Moving the node primitives down is
not part of step 3, because they are node questions with node-grain callers
(`select_engine.c:139`, `mod_lookaround.c:534`, `atomic.c:534`'s pre-seal
discharge). The matrix records the edge as a named exception. The trigger to
move them is a defect traced to that edge (D77).

#### 4.2.2 The inputs, and the carve-outs (all five from the r1 review)

A derivation in `src/facts/` depends on exactly:
1. the sealed IR (the `Ast` at its epoch, or the wrapped `Nfa` at E3), and
   the node-grain pure functions over it (§4.3);
2. OTHER FACTS, only through accessors, and only along the DEPENDS-ON edges
   `facts.def` declares. So the pin's dependency on the window is a declared
   edge, not a field read of `Job.req_run`, and the dependency DAG is
   written down once;
3. the encoding DESCRIPTOR, as a declared input (carve-out (d)).

The carve-outs:
- **(a) Split `core/internal.h` FIRST.** `internal.h` is 6,561 lines and
  is `#include`d by 54 files (52 of them `.c`): every translation unit under
  `src/` except `src/enc/`'s three, plus the CLI. A rule "consumers include only `facts.h`" would pass
  vacuously while the derivations' declarations stay there
  (`pcrec_prefix_ksets`, `internal.h:1698`; the E2 derivations beside
  `Job`, `:2580-2603`). So step 3.0's FIRST commit (3.0a, §9) moves every
  derivation declaration into `src/facts/facts_derive.h` before anything else
  moves. `internal.h` keeps the node-grain declarations (§4.3) and gains one
  `#include "facts/facts.h"` for `Job.pf`.
- **(b) Derived and rate readers go with B1's rate primitives**, not with
  the walk files. `rb_pick`, `rn_scan_index`, `rn_window_start` and
  `set_ppm` are rate READERS: after B1 each is "build the candidate order,
  call `pcrec_find_pick`/`_seq_mass`/`_set_mass`" (§6.3). Putting them beside
  the primitives keeps each question kind's NONE rule and its callers in one
  file. The derived FACTS' accessors (in `facts.c`) call them, and
  `facts.def`'s OWNER column names their file.
- **(c) Decisions stay in their passes.** G1's `req_byte_dominated_by`
  (`emit_dfa.c:5917`) and the offset-k SELECTION (`prefix_k.c`, after 3.4
  everything but the walk) are DECISIONS (§4.4). They read facts and do not
  move.
- **(d) The encoding descriptor is a declared input.** `endwin.c:156` reads
  `pcrec_enc_by_id(cx->opt->encoding)` [r1 A13]. After relocation the
  derivation takes `const PcrecEnc *` as a parameter. `facts.c` resolves it
  once, and `facts.def`'s row for the end window declares the input. §0.5(a)'s
  rule "no fact derivation reads `cx->opt->encoding`" then holds literally.
  The descriptor's structural fields (`start_cls`, `max_cp`) remain the only
  encoding facts a derivation sees (§6.1).
- **(e) One relocation per commit, each under the zero-movers gate.** A move
  is `git mv` plus include edits plus the declaration move. It shares no
  commit with a behaviour change, so the §9 A/B emit diff attributes any
  mover to exactly one relocation.

#### 4.2.3 The check: include graph plus link symbols (replaces the grep)

Revision 1's grep for derivation calls outside the owner and `facts.c` fails
in four ways [r1 A4, C2, C3]:
- It is FILE-granular, so it is blind where owner and consumer share a file.
  That is `prefix_k.c` today: the walk and the selection that consumes it.
- It cannot tell a root call from a subtree call.
- It is blind to a RE-DERIVATION (R13, R4, R12 are all re-spellings, not
  re-calls).
- Its target list was hand-kept, and its sabotage row re-inserted the exact
  string it grepped for, so the control shared a source with the check
  (learnings §3).

The relocation lets a structural check replace it. It is born in step 3.0,
in `make test-codegen`'s structural section. The precedent is the DD-12 (7)
seam check (`tests/codegen/run_codegen_tests.sh:1025-1057`), a codegen
structural check with a declared allowlist [r1 C7: revision 1 cited
`assertions_design.md` §8.4, which is not that precedent]. It asserts two
things:

1. **Include graph.** The set of files that `#include "facts/facts_derive.h"`
   (a regex scan of `#include` lines, `tools/review/include_graph.py`'s
   method, no preprocessing) EQUALS the generated target list. It is not
   "is a subset of": a listed owner that stops including the header is also a
   failure, because it means the target list names a file that no longer owns
   anything.
2. **Link symbols.** For every object file under `build/`, the UNDEFINED
   symbols it references (`nm -u`) that are DEFINED by `src/facts/*.o` and NOT
   declared in `facts.h` must be empty unless that object's source is on the
   target list. The symbol set comes from `nm` over the facts objects, not
   from a list of names. This catches a hand `extern` re-declaration that
   bypasses the header, which the include check alone cannot see.

**The target list is GENERATED.** It is `src/facts/*.c` plus each distinct
OWNER file named in `facts.def`, extracted by a plain-text scan of the
table's row markers (one row per `PF_FACT(` line, the owner field by
position). It is never produced through the X-macro expansion, so a
preprocessor defect cannot hide a row from the check that polices it (C4's
rule, §11.6). A REACH line prints the list's size and the number of symbols
checked, so an empty list reads as vacuous rather than green.

**The sabotage row** (a new S-id, numbered from main's highest at landing)
adds `#include "facts/facts_derive.h"` to `src/gen/emit_vm.c` and nothing
else, and the check must fail on assertion 1. It does not re-insert any
function name, so it is independent of any grep string. A second row adds a
hand `extern` declaration of one derivation plus one call in
`src/gen/emit_vm.c` without the include, and the check must fail on
assertion 2.

**What it cannot catch: a hand RE-SPELLING.** A consumer that writes its
own walk (R13's shape exactly) calls no derivation, includes no private
header and references no facts symbol. No include or link check sees it. The
layer's shape limits this in three ways:
- **Helpers are private.** `rb_union`, `rr_cat`, `wclose`,
  `frontier_union` and the rest are `static` inside their `src/facts/` file.
  A re-spelling therefore cannot reuse half the lattice and diverge in the
  other half, which is how R13 happened (a shared walk, two local picks).
  It must rewrite the whole walk, which makes it a large and visible diff.
- **The answer has one home.** A consumer that needs a pattern fact finds it
  in `facts.h`. The accessor is the cheapest way to get the answer, and the
  memo makes it cheaper than a walk.
- **Review tooling sees clones.** `tools/review/clone_candidates.py` is the
  review-time instrument for a duplicated walk. It is not a gate, and this
  design does not make it one.

The residual is stated in `src/facts/CLAUDE.md` so a reviewer knows to look
for it.

#### 4.2.4 The choice through the lenses

| lens | the `src/facts/` layer | derivations stay in their first consumer's file (revision 1) |
|---|---|---|
| specific vs general | one home for "what the pattern has". A new fact is a `facts.def` row plus one file or function in the layer | the owner is whoever needed the fact first, which is an accident of history (R13) |
| core vs derived | a core fact's file holds only its walk. Derived readers sit with the rate primitives (b), and decisions stay in passes (c). The layer boundary IS the core/derived/decision boundary | walk, pick and selection share a file (`reqbyte.c`, `prefix_k.c`). The pin sits inside a selection routine (`prefix_k.c:477-491`) |
| applicable vs assumption-changing | applicable. Every core walk already reads only the IR (pfcrit-arch). The pin's kind gate becomes a consumer obligation the one consumer already carries | applicable, but the pin stays coupled to `unanch_start` |
| fits the architecture vs a refactor | a directory move in five one-file commits under a zero-movers gate. `src/` already layers by directory (`include_graph.py`'s matrix) | no move at all |
| D124 shared question / engine hat | a fact both emitters ask lives in neither emitter's neighbourhood. Consumers in `emit_dfa.c` and `emit_vm.c` are hats on one accessor | the VM asks a fact whose owner sits beside a DFA pass |
| checkability | include graph plus link symbols, a generated target list, a string-free sabotage row | a file-granular grep that is blind in the shared-file case |

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

Node-grain functions do NOT move into `src/facts/` (§4.2.1). They answer node
questions for node-grain callers, several of them before any seal (the
discharge pass, `atomic.c:534`; module `lookaround`'s width rule,
`mod_lookaround.c:534`). The layer composes them at the root. What a pattern
fact adds is the seal, the deny and the memo, and none of those means anything
for a subtree.

### 4.4 What the record is not, and why (D124)

| thing | why not a record fact | where it stays |
|---|---|---|
| rewrites/annotations (`possessive`, `revbody`, discharge, `call.link`) | they are the RESULT of a rewrite and are emission material. "Revocable" (`lower_enc` clearing `revbody`) is a rewrite correcting a rewrite, and an epoch-sealed fact cannot be revoked | the AST |
| route decisions (`fit`, engine, `engine_sel`, `pcrec_artifact_has_dfa_scan`) | a decision about the ARTIFACT, made by `select_engine`, depending on options and caps as well as the pattern | `Job.fit` (already one derivation). Two `fit` members are NOT decisions but copies of E1 facts: `fit.lang_nullable` (`select_engine.c:568`) and `fit.prefilter_has_collapsible_rep` (`:571`). A copy beside its accessor is the dual home §5.4 forbids, so both are deleted in step 3.2 and their readers (`compile.c:1585`, `:1620`; `select_engine.c:837`, `:856`) read the E1 accessors [r1 A7] |
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
| | EVERY pin consumer | the pin is a pure NFA+window fact (§4.2); it may be set where today's prefilter kind is `DFA_PF_NONE` | **the kind gate**: read the pin only where the prefilter kind is not `DFA_PF_NONE`, as `pf_run_applies_common` does (`emit_dfa.c:5294`) [r1 A2] |
| nullable | `select_engine`, K50 start gate | lowering-invariant, and forced at the E1 seal (§2) | none |

---

## 5. How consumers read (no consumer re-walks)

1. A consumer reads a pattern fact ONLY through its `pcrec_fact_*`
   accessor, declared in `src/facts/facts.h`. The include-graph and link
   check (§4.2.3) makes including the facts-private header, or referencing a
   derivation symbol, outside the generated owner list a test failure. A
   hand re-spelling is the stated residual (§4.2.3).
2. A consumer never reads a fact's DENY bit. The accessor already returned
   the empty value. Today's `compile.c:1501-1520` ternaries move into
   `facts.c` (step 3.0). After that, `compile.c` no longer computes any
   fact inline. Its only record duties are calling the seals (E1 forces
   its two facts, §2; E2 advances the epoch; E3 is set inside the
   `ENG_UNANCH` arm only, §3) and allocating `Job` as now.
3. A consumer never reads `cx->opt->encoding` to decide a fact or a
   ranking (§6). The findings §11.7 grep check (planned) is widened to
   cover `src/facts/`, the rate readers beside B1's primitives, `prefix_k.c`
   and `emit_dfa.c`'s G1. Inside `src/facts/` the rule is structural: the one
   derivation that needs encoding structure takes the descriptor as a
   parameter (§4.2.2 (d)).
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
not its identity. After relocation the descriptor is a declared PARAMETER of
the one derivation that reads it (§4.2.2 (d)), not a lookup through
`cx->opt->encoding` [r1 A13].

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
- **The rate READERS move beside the primitives** (§4.2.2 carve-out (b)):
  `rb_pick`, `rn_scan_index` and `rn_window_start` out of `reqbyte.c`
  (which is then empty and deleted, since 3.0 lifted its walk into
  `src/facts/req.c`), and `set_ppm` out of `prefix_k.c`. Each move is its own
  commit (carve-out (e)). The moves are byte-identical under `-e byte`;
  B1's own movers come from the primitives' NONE rules, in separate commits.
- **§11.6 check 1 (non-perturbation), born here** [r1 A10]. B1 is the first
  step where forcing an unasked fact can change a stamp: a derived pick asks
  the rate, and the rate's consumption is recorded in `<P>_FINDINGS`.

**B1 reads from the record: the DERIVED-fact sites and nothing else.**

| site after step 3.0 | reads | calls |
|---|---|---|
| the pick (`rb_pick`, inside `facts.c`'s derived `req_byte` accessor) | core `pcrec_fact_req_set` | `pcrec_find_pick` |
| the run member + window (`rn_scan_index`/`rn_window_start`) | core whole run | `pcrec_find_pick`, `pcrec_find_seq_mass` |
| G1's density conjunct (`req_byte_dominated_by`) | `CandScan` (an emission decision, unchanged) + derived `req_byte` | `pcrec_find_no_commoner` |
| offset-k selection (`set_ppm`, moved beside the primitives) | E3 k-set walk (after 3.4; before 3.4 it is the same walk inline) | `pcrec_find_set_mass` |

**B1 must NOT:** read `cx->opt->encoding` at any reader; memoize a rate
anywhere but `Ctx`; add a second `req_*` field; or call `rb_walk`. Its
movers are exactly findings §11.3's two manifests. `b1_byte_movers` is
EMPTY. `b1_utf8_movers` is named per artifact: offset-k selection moves,
plus any G1 fallout on the same artifact. Its abi event is the one D123-2
ruled shared with the gate move.

**What B1 exercises of the record's machinery** [r1 A6]. B1 is the
machinery's first customer from OUTSIDE the migration. It uses:
- the DERIVED accessors' memo, because the pick and the window are asked by
  several emitter sites and derived once;
- the fact DENY, because `-fno-req-byte`/`-fno-req-run` store the empty value
  without running the derivation, so the rate is never asked and the
  consumption record says so (§7.4);
- the rate accessor as the one DATA input.

S2a exercises none of these (§8.2).

**Sequencing: step 3.0 is a HARD PREREQUISITE of B1** [r1 A5]. B1 rebases
onto 3.0, where the req-fact derivations are already behind `facts.c`'s
accessors and not in `compile.c`. Revision 1 offered a fallback (B1 lands
first, editing today's sites, and 3.0 moves them afterwards). That is
deleted, because it contradicts D125 addendum 1's reason (2): "built
first, it would be a parallel mechanism that [PATFACTS] then replaces". B1
editing today's sites is exactly that order. The forbidden order stays
forbidden too: no findings-local memo of any PATTERN fact.

### 8.2 [OPT-LITSCAN] S2a: `[OPT-VMLIT]` exact, the node-grain customer

S2a turns the VM's per-byte literal chain into P4's exact arm, one
constant-length `memcmp` (`compare_stack.md` §6.1 S2). **It is a customer
of the record's node-grain RULE (one definition, §4.3), not of its
machinery.** It asks no pattern fact, so it touches no memo, no epoch and no
deny [r1 A6]. §0 item 9 and §12 Q6 say what that means for sequencing.
**What it reads:**

1. **ONE new node-grain fact, the emission-contiguous literal run.** Given
   an `A_CAT` spine child position, it returns the maximal `L ≥ 2`
   consecutive spine children each with
   `child->k == A_CLASS && pcrec_cls_single(child) >= 0`, and their bytes.
   The `A_CLASS` guard is part of the definition [r1 F5].
   `pcrec_cls_single` reads `a->u.cls` unconditionally (`cpset.c:305-311`),
   which is a union read on any other kind (`A_VAR`, `A_BREF`). Every
   caller already guards: `emit_vm.c:3650` returns -1 unless `A_CLASS`,
   `reqbyte.c:453` is inside `case A_CLASS`, and `altcls.c:190`'s operand
   is a class by construction. The spine is not seen through `A_CAP`, `A_ATOMIC`,
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
   - **EXACT only. Caseless is `[OPT-LITSCAN]` S4's** [r1 F4]. Under
     `(?i)` a letter is the two-member class `[Aa]`, so
     `pcrec_cls_single` returns -1 (`cpset.c:307`: `n != 1`) and the run is
     empty. That is the row design (`compare_stack.md` §6.1: S2 is P4's
     EXACT arm, and the caseless mask compare is S4, gated on its own
     measurement), not a hole in the fact. A caseless literal keeps today's
     per-byte chain until S4.
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

Revision 2 puts each fact family's RELOCATION into `src/facts/` (§4.2.1)
inside the migration step that puts that family behind its accessor, and
splits `core/internal.h` first (carve-out (a)). Inside a step, **one
relocation per commit** (carve-out (e)). The A/B diff runs per commit
wherever a commit moves code, so a mover is attributed to one relocation.

| step | what moves (one bullet ≈ one commit) | gate that proves it | abi |
|---|---|---|---|
| **3.0a `internal.h` split** (3.0's first commit, before anything moves) | • `src/facts/` created with `facts.h` (consumer: types and accessors, empty of accessors yet) and `facts_derive.h` (private: derivations). The E2 derivation declarations leave `core/internal.h` for `facts_derive.h`: `pcrec_start_anchor`, `pcrec_end_window`, `pcrec_req_byte`. Their owners and their one caller today (`compile.c:1501-1520`) include it. `pcrec_prefix_ksets` (`internal.h:1698`) does NOT move yet: it is walk plus selection until 3.4 splits it, and its selection half is a pass function that stays declared in `internal.h` | A/B diff ZERO (a declaration move cannot change emitted text, and the diff proves it); `make strict` | **no** |
| **3.0 skeleton + E2 req/anchor/window + `--emit-facts`** | • `Job.pf`, `PfEpoch`, `facts.c`, `facts.def`; the E2 accessors; the `compile.c:1501-1520` deny ternaries move into the accessors, so `compile.c` stops including `facts_derive.h`. The include-graph and link check (§4.2.3) is born in this commit with its two sabotage rows, its target list generated from the new `facts.def`, so every later relocation moves under it. • `git mv src/opt/startanch.c src/facts/`. • `git mv src/opt/endwin.c src/facts/`, the descriptor becoming a parameter (carve-out (d)). • `rb_walk` and its lattice lifted from `reqbyte.c` into `src/facts/req.c` (`rb_pick`/`rn_*` stay in `reqbyte.c` until 3.1). • The §11 listing with its checks 2-4; `REQ_*`/`VM_START`/`END_WINDOW` render through the shared renderers | A/B diff ZERO **per commit** over byte+utf8 × {default, `-fno-req-byte`, `-fno-req-run`, `-fno-end-window`, `-fno-vm-anchor-bound`, `-fno-run-prefilter`, `--engine=vm`}; `run_recursion_identity.sh` (B) with its pin UNMOVED (a re-pin is disqualifying); `run_prechecks.sh`; `make test-codegen`/`make strict` | **no** |
| **3.1 = [FINDINGS] B1** | • the data tier; the §6.3 primitives. • `rb_pick`, `rn_scan_index`, `rn_window_start` move beside the primitives (carve-out (b)); `reqbyte.c` deleted. • `set_ppm` moves beside them. • C1-C4 call the primitives. • §11.6 check 1 (non-perturbation) born, with its sabotage row [r1 A10] | the moves: A/B diff ZERO per commit. The primitives: findings §11.3 manifests (`byte` EMPTY with REACH; `utf8` named per artifact); findings §13 B1's acceptance list | **YES**: the one D123-2 event |
| **3.2 E1: kinds, nullable** (revision 1's "cwidth" is dropped, §1) | • `src/facts/kinds.c` and `src/facts/widths.c` (NEW, composing the node primitives at the root); `pcrec_facts_seal_e1` forces both at `compile.c:1397` [r1 A1]. • `select_engine`'s locals, the `emit_vm.c:13191/13208` listing re-walk (R1) and `emit_vm.c:9980` read the accessors. • `fit.lang_nullable` and `fit.prefilter_has_collapsible_rep` deleted; readers read the accessors [r1 A7]. • The E1 invariance cross-check with its TWO sabotage rows (kind mask, nullability; §3, [r1 C6]) | A/B diff ZERO; `run_ir_listing.sh` (the listing is output, not artifact, and must be unchanged); `run_vm_identity.sh` | no |
| **3.3 = S2a** | the node-grain literal-run function; the VM chain. No `src/facts/` move: its fact is node-grain (§4.3) | S2a's own gate (its movers are its design, not a migration) plus: cost/slot/emit agreement on every corpus pattern, the R5 check | **YES**, S2a's own |
| **3.4 E3: the k-set walk + pin** — **FLAGGED: a POSSIBLE MOVER** [r1 A2] | • the walk half and the pin lifted from `prefix_k.c` into `src/facts/kset.c`; the per-offset `ppm` (`prefix_k.c:443`, `:475`) moves into the selection, which stays in `prefix_k.c` (carve-out (c)). • The E3 seal written inside the `ENG_UNANCH` arm only, and the two decline tokens (§3, [r1 A3]). • `unanch_start` reads the memo (R14). • The pin becomes a pure NFA+window fact, and its kind gate becomes each consumer's obligation (§4.5) | A/B diff ZERO; `run_offset_skip.sh`; the S1 census re-run, identical to `census_b_main.tsv`. Before the lane starts: a grep of every reader of `run_pinned`/`run_o`, each confirmed to carry the kind gate, attached to the lane's report | no |
| **3.5 node nullable (R4)** | `vm_nullable` becomes the one node-nullable function (with the `A_CALL` arm kept) | A/B diff ZERO; `run_vm_identity.sh`. **A mover here is a found disagreement between the two copies. Stop and file a K-row** | no |
| 3.6 (anytime) R3 | `mrl.c`/`callgraph.c` saturating arithmetic unified | A/B diff ZERO | no |

**Why 3.4 is flagged** [r1 A2]. It is the step likeliest to move a byte,
for two reasons revision 1 missed.
- **(i) The pin's domain widens.** Today the pin is computed only when the
  prefilter kind is not `DFA_PF_NONE` (`emit_dfa.c:3719-3720`), so on a
  `DFA_PF_NONE` artifact `run_pinned` is 0. A pure NFA+window pin is TRUE on
  some of those artifacts. No byte moves only if every consumer carries the
  kind gate. `pf_run_applies_common` does (`emit_dfa.c:5294`), and the
  pre-lane grep above confirms the rest. A consumer that lacks it is a
  semantic mover (§9.1): it would have read 0 by accident of call order.
- **(ii) The walk reads the prior today.** `set_ppm` is called inside the
  walk loop (`prefix_k.c:443`, `:475`). Moving it into the selection must
  reproduce each offset's `ppm` exactly. The values are the same function
  of the same sets, so any mover is an ordering defect in the move.
Being flagged changes nothing about the gate. It means the lane does its
pre-lane grep, runs the A/B diff over the widest deny set in the table, and
expects to classify a mover rather than to see none.

### 9.1 Classifying a mover [r1 C1]

Revision 1 said "a mover in a no-abi step is a FINDING, never an abi bump".
That rule had no answer for a genuinely COSMETIC move (a relocated file's
emitted `// from src/opt/...` provenance comment, say), which D76 treats as
an ordinary abi event. So a nonzero A/B diff is CLASSIFIED before anything
else happens:

| class | test (from the diff itself) | what the lane does |
|---|---|---|
| **SEMANTIC** | any mover where a VALUE differs (a stamp's value, a table entry, a constant, a bound), or where a CODE PATH differs (a statement, branch or call present on one side only) | STOP. It found two copies of one fact that disagree (R13's class). File a K-row with the movers, and the step does not land. Never absorbed into an abi bump |
| **SCAFFOLDING** | every differing line is comment text, whitespace, declaration order or layout, and the compiled object's executed bytes and exported symbols are identical (`m6read_samples/check_neutrality.sh`'s definition of "neutral") | the ordinary D76/D94 ritual: an abi bump, identity re-pins, readers found by grep, in the same change. The lane attaches the classified diff to the commit so a reviewer can check the class |

When in doubt the class is SEMANTIC. A mover that is part scaffolding and
part value is semantic. The object-code test is required because the
scaffolding class claims no behaviour moved, and the source diff alone cannot
show that.

**Order rationale.** 3.0a first, because every relocation after it is
checkable only once the private header exists (carve-out (a)). 3.0 next,
because B1 and every later step edit through it, and it retires a real
hazard: the deny application lives in one file. **3.0 is a hard prerequisite
of B1** (§8.1, [r1 A5]). B1 (3.1) next, because it is the chartered first
customer and the only other abi event. 3.2 before 3.4: E1 has four-plus
readers and a debug-listing re-walk, while E3 has one owner, a cost that is
unmeasured and the mover risk above. S2a (3.3) is placed where its own gates
allow. It depends on nothing in the record (§8.2) and may land before 3.2
without harm. Each step is one lane. Every byte-identical step runs its A/B
diff as the lane's LAST act (BOILERPLATE do-then-finish), because the diff
is a multi-config corpus run.

**Stop rule, repeated because it is the whole discipline:** a
byte-identical step with a SEMANTIC mover (§9.1) has found two copies of one
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
| moving the node-grain primitives (`mrl.c`'s widths, `atomic.c`'s predicates) below `src/facts/`, retiring the `facts → opt` layer edge (§4.2.1) | a defect traced to that edge, or a node-grain primitive gaining a caller the layer order forbids |
| a GATE against hand re-spellings of a fact's walk (the §4.2.3 residual) | a second R13-class incident after the relocation, i.e. a re-spelled walk found outside `src/facts/`. `tools/review/clone_candidates.py` is the review-time instrument until then |

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
| `why` | CLOSED token + detail: `deny:<flag>` with the flag's spelling from `axes.def` (e.g. `deny:-fno-req-byte`); `decline:<reason>` (e.g. `decline:enc-multibyte` for `end_window` under `utf8`, `endwin.c:164`; `decline:no-forward-nfa` for E3 on a no-DFA VM route; `decline:attempt-unwrapped-nfa` for E3 on `ENG_ATTEMPT`, §3 [r1 A3]); for a derived pick, `rate:<source>` or `rate:none(<encoding>)->rightmost` (the §6.3 NONE rule that answered); empty for a plain derivation |
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
   hide a fact from the dump. The table lives in `src/facts/` (§4.2.1), and
   each row also names its OWNER file and its DEPENDS-ON facts (§4.2.2).
2. **The printer reads the memo.** `src/dump/facts_dump.c` (NEW, beside
   `axes_dump.c`) iterates `facts.def` and, for each row, reads
   `Job.pf`'s value, status, why and asked bit. It never calls an owner's
   derivation. It includes `facts.h` only. It is not an owner, so it is not
   on the §4.2.3 check's generated target list, and including the private
   header there fails the check.
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

An accessor whose epoch was never sealed on this route is not forced (§3).
On a no-DFA VM route, forcing E3 would build an NFA the compile never built:
it lists as `status absent`, `why decline:no-forward-nfa`. On `ENG_ATTEMPT`
the forward NFA exists but is never wrapped, so the E3 seal is never written
[r1 A3]. Forcing there would walk a machine whose meaning is not the pin's.
It lists as `status absent`, `why decline:attempt-unwrapped-nfa`. Revision
1's claim that `decline:no-forward-nfa` covered every non-E3 route was false
on `ENG_ATTEMPT`.

**The force loop is GUARDED** [r1 A11]. After emission, a forced derivation
can still reach `pcrec_ctx_fail`: an arena allocation failure is a `longjmp`
(`compile.c:48`), and so is the epoch guard. Unguarded, that `longjmp` lands
in `compile_driver`'s catch branch as a failed attempt, and `--emit-facts`
would REFUSE a compile that had already succeeded. The guard does not add a
recovery point. The tree has exactly one `setjmp` by rule
(`compile.c:398-402`, `:623-631`). Instead it reuses K60's shape: a flag set
before the `longjmp`, read in the handler (`cx->failed_nomem`,
`compile.c:41-44`).
- `facts.c` sets `Ctx.pf_forcing` for the duration of the force loop and
  records which fact it is forcing.
- The handler's first test is `pf_forcing`. When it is set, the attempt's
  artifact and stamps are already complete, so the handler does not retry and
  does not refuse. It stores the fact being forced as `status absent`,
  `why decline:force-failed`, and re-enters the force loop at the next row,
  with the `setjmp` re-armed the way the retry loop already re-arms it
  (`compile.c:731-735`). The compile's result is the one emission already
  produced.
- The epoch guard needs no `longjmp` under forcing at all. An unsealed epoch
  is a decline (§3), and forcing never asks past a seal the route did not
  write.

The spec page (§11.7) promises: **the listing never refuses a compile that
succeeded.** Only the FINAL
compile attempt's record is listed (the retry ladder, `findings/design.md`
§6.4's rule). One listing row per attempt would be a different feature
(D77: not asked for).

### 11.5 Should the existing stamps derive from the same record? YES for facts, CAPTURED for decisions

| stamp | kind | after this design | abi |
|---|---|---|---|
| `REQ_BYTE`, `REQ_RUN` | record FACTS (derived pick, window) | the prologue reads the accessor and renders with the fact's `facts.def` renderer, the same one the listing uses. Lands with step 3.0 (§9), which already moves these fields into `Job.pf` | no: byte-identical, and the renderer is today's text moved |
| `VM_START` | record FACT (start anchor) | same, via `pcrec_start_anchor_name` (already the one spelling, `startanch.c:153`) as the fact's renderer | no |
| `END_WINDOW` | record FACT (end window) | same: `emit_dfa.c:8567-8571` renders `none` or the decimal bound today, and that text becomes the fact's renderer [r1 A9] | no |
| `REQ_WHY`, `DFA_PREFILTER`, `DFA_PREFILTER_OFFSETS`, `ENGINE*`, `VM_PREFILTER`, `DFA_START` | DECISIONS (§4.4) | unchanged derivation, one owner each (`req_why_name`, `dfa_prefilter_name`, …). Their stamp writes are CAPTURED into §11.2's decisions list | no |
| `<P>_FINDINGS` | the findings consumption record | unchanged (findings §7). The `rate` section reuses its tokens | — (B1's own event) |

**Capture is scoped to the FINAL attempt's artifact buffer** [r1 A12].
Revision 1 assumed every stamp goes through one primitive
(`pcrec_sb_stamp_str`/`_stampf`/`_stampwf`, `sb.c:348-368`). Raw
`#define`s exist outside it:
- `emit_dfa.c:8966`, `DFA_PREFILTER_OFFSETS`, written by
  `pcrec_sb_printf` with a body `dfa_prefilter_offsets` streams in;
- `emit_vm.c:226`, `:228`, `PCREC_FEATURE_SET`/`PCREC_FEATURE_MODULES`;
- `emit_vm.c:11390-11628`, 15 `#define <P>_…` macro emissions (the
  `TIER_NOTE`, `CHARGE_WORK`, `PRUNE_*`, `TRAIL`, `SET`, `PUSH`, `CUT` and
  `CALL` machinery). These are code, not stamps, and `decisions` excludes
  them by name.

So capture does not hook a primitive. It records the byte range of the
artifact's stamp block in the final attempt's own buffer, and the
`decisions` section is parsed from that range. A rejected attempt's buffer is
discarded with its `Job`, so its stamps cannot leak in. §11.6 check 4
compares against the emitted file independently, so a stamp that escapes the
range is a check failure, not a silent omission. The 3.0 lane converts
`DFA_PREFILTER_OFFSETS` to the primitive if that is byte-identical, and
otherwise names it in the range parser.

**Why not move decisions into the record to derive their stamps from it:**
§4.4's boundary (D124: "which check runs where" is a different question from
"what the pattern has"). Capturing the stamp as it is written gives the same
guarantee, "the listing cannot disagree with the artifact", without
widening the record. **Why facts' stamps must move:** otherwise
`REQ_RUN`'s hex@idx spelling exists twice (prologue and dump). That is the
parallel-renderer version of R13.

### 11.6 Checks (each born with a sabotage row, learnings §3)

1. **Non-perturbation: born with B1 (step 3.1), not with 3.0** [r1 A10].
   For every corpus pattern × {byte, utf8}, the artifact from an ordinary
   compile is byte-identical to the artifact a `--emit-facts` compile would
   have emitted. The query builds the artifact in memory, so a test hook
   writes it. Revision 1 landed this in 3.0, where it cannot fail: before B1
   every fact is a pure function with no side effect, so forcing one early
   moves nothing and the check is green by construction. B1 adds the first
   fact whose asking has a visible side effect: the derived pick asks the
   rate, and the rate's consumption is recorded in `<P>_FINDINGS`. The
   sabotage row is "force before stamps": move §11.4's force loop ahead of
   stamp rendering, on a pattern where some rate-asking fact is UNASKED by
   the ordinary compile. Forcing it early then records a rate consumption the
   ordinary compile did not make, the `<P>_FINDINGS` line moves, and the
   check must fail.

   **The witness population, measured for this revision: EMPTY on today's
   fact set.** `REQ_BYTE` is stamped on every route probed (`ab+c` on the DFA
   and `--engine=vm`; `^abc`; `a|b`; `(a)b` under `--engine=vm`; `éx+` under
   `-e utf8`; stamp site `emit_dfa.c:8596-8599`). So the pick is asked on
   every compile, and forcing it early moves nothing. The window's
   `seq_mass` ask rides the same `REQ_RUN` stamp. So the sabotage row ships
   declared `UNREACHED` ([MECH-REACH]), with its REACH line counting corpus
   artifacts that leave a rate-asking fact unasked. It becomes reachable at
   the first fact whose asking is route-dependent AND rate-reading. The
   check itself still lands with B1, because B1 is where forcing first CAN
   have a side effect. The alternative is to hold the check until a
   reachable witness exists (D77). That is a manager's call, recorded here
   rather than decided.
2. **Completeness:** the listing has exactly one `facts` row per `facts.def`
   row, per encoding. **The expected count comes from a plain-text scan of
   `facts.def`'s row markers** (one per `PF_FACT(` line), never through the
   X-macro expansion the printer itself iterates [r1 C4]. Counting through
   the macro path would share a source with the printer: a row the
   preprocessor drops would vanish from both sides at once. The same scan
   produces §4.2.3's target list. Sabotage: a `facts.def` row whose printer
   arm is skipped.
3. **Why-truthfulness against an INDEPENDENT oracle** [r1 C5]: for each
   fact-deny flag, compiling with that flag lists `deny:<that flag>` on
   exactly the facts **`docs/spec/tuning.md`'s entry for that flag** says it
   empties, and on no other. Revision 1's oracle was `facts.def`'s own deny
   column, which is also what drives the deny logic. A wrong column would be
   agreed with by both. `tuning.md`'s per-flag text is hand-written under
   D80 and already owes the consumer list (§7.2). Each fact-deny entry gains
   one parseable line naming the facts it empties, beside the consumer
   sentence, and the check parses that. The flag set is the deny sweep's own
   list from `axes.def`, which the listing does not produce. Sabotage: flip
   one fact's deny bit in `facts.def`.
4. **Decisions = stamps:** the `decisions` section equals the artifact's
   `#define` stamp block, parsed from the emitted C file. Those are two
   renderings, one of which is the artifact itself. The parser excludes the
   named machinery macros of §11.5 (`emit_vm.c:11390-11628`) and nothing
   else, so a stamp written outside the captured range fails the check
   [r1 A12].

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
- the non-perturbation guarantee (§11.6 item 1);
- **the listing never refuses a compile that succeeded** (§11.4, [r1 A11]).

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
E2 req/anchor/window facts and moves `REQ_*`/`VM_START`/`END_WINDOW` to the
shared renderers. Checks 2-4 land with it. The listing's row population then
grows with each migration step for free (§11.3 item 1). B1 adds the `rate`
section and check 1 (§11.6). It is not an abi event
(§11.5). It does NOT:
- list node-grain facts (per-node output is `--emit-ir`'s territory for the
  VM program; a node-fact listing waits on a named need);
- keep facts from rejected compile attempts;
- print rate VALUES.

## 12. Open questions for Frank

Each is a genuine ruling. Spellings, file names and step sizing are the
manager's. Revision 2 changed Q1 (E1 is eager, E3 is per branch) and Q6
(premise, [r1 A6]), and added Q11 (the relocation).

1. **Three sealed epochs instead of the charter's one point.** D120 says
   "computed after `pcrec_lower_enc`". This design adds E1 (pre-lowering
   structural facts, because `select_engine` needs them before lowering)
   and E3 (NFA facts, because the pin is one). The alternative, moving
   `select_engine` after lowering, changes the pipeline order that
   `possessify`/`revdet` depend on. Revision 2 sharpens two of them (§3): E1's
   facts are FORCED at the seal, because `pcrec_lower_enc` rewrites in place
   and a lazy E1 answer would depend on ask time [r1 A1]. E3 is sealed PER
   BRANCH, only where the forward NFA is wrapped, with named declines
   elsewhere [r1 A3]. **Recommend: accept the three epochs, as revised.**
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
6. **S2a now, or wait for S2b?** [r1 A6 changed this question's premise.]
   Revision 1 asked only whether S2b (carried verified facts) is deferred.
   The panel found that S2a exercises none of the pattern-grain machinery:
   its one fact is a node-grain pure function, so it touches no memo, epoch
   or deny (§8.2). D125 addendum 1 names S2 as a first customer, and S2a is
   a customer of the record's one-definition RULE, not of its machinery. The
   question is therefore:
   (a) build S2a now as an independent step (3.3), with 3.0 plus B1 as the
       machinery's customers; or
   (b) hold S2 until S2b's bench trigger fires (§8.3), so that S2's first
       build is a real outside customer of the machinery.
   S2b stays specified and not built under either option.
   **Recommend (manager's view, adopted here): (a).** B1 uses the deny and
   the rate accessor, and 3.0 uses the memo, the epochs and the deny. So the
   machinery has customers without S2. S2a is independent, is gated by its own
   bench pass (`compare_stack.md` §6.1), and gains nothing by waiting.
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
    same one, and non-perturbation is checked (from B1, §11.6). The force
    loop never forces an unsealed epoch, and it is guarded, so it never
    refuses a compile that succeeded (§11.4, [r1 A11]). **Recommend: force,
    after emission.**
11. **Adopt the `src/facts/` analysis layer** (§4.2; Frank's relocation
    question, 2026-09-26). Revision 1 left each derivation in its first
    consumer's pass file. Revision 2 proposes one directory with one file per
    fact family, a consumer header and a facts-private header. Derivations
    there depend only on the IR/NFA, on other facts through `facts.def`'s
    declared DAG, and on the encoding descriptor as a declared input. The five
    carve-outs apply: (a) split `internal.h` first, (b) rate readers go with
    B1's primitives, (c) decisions stay in their passes, (d) the descriptor
    is declared, (e) one relocation per commit under the zero-movers gate.
    The relocations ride their migration steps (§9). An include-graph plus
    link check replaces the grep (§4.2.3), and a hand re-spelling is its
    stated residual.
    **Recommend: yes.**
    - **The critic's reason** (pfcrit-arch, ADOPT WITH CARVE-OUTS): no core
      fact needs a pass's internals. `rb_walk` reads only the `Ast`, the
      k-set walk only the `Nfa`, and the end window and start anchor the
      `Ast` plus the descriptor. The one coupling, the pin's gate on
      `unanch_start`'s verdict, is cured by making the pin a pure fact and
      the gate a consumer obligation that the one consumer already carries.
    - **The manager's reasons**: it answers Frank's "area A writes, B and C
      use" directly, since a fact's home is no consumer's file. It turns the
      revision-1 check, which was blind in the shared-file case, into a
      structural one with a string-free sabotage row. And R13, the incident
      that reordered the phase, grew in exactly the first-consumer-owns
      shape this removes.

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
