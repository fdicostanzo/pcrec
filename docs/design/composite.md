# [COMPOSITE] — the composite artifact as a general tool; first client [MATCH-SPLIT] (DESIGN NOTE)

Lane `mscomp` (2026-10-12, opus), from main `a080c69a` (abi 76). **Design only.** Nothing under
`src/` is changed. The evidence is a hand-composed twin built from UNCHANGED `build/pcrec`
compiles plus a hand-written controller (`composite/twin/`): an every-startpos differential
against today's artifact and libpcre2 10.46, counted subject loads (no clock), a one-TU
compile probe and a size measurement.

Rulings read: D163 and its addendum 1, D88 and its addendum 1, D156, D158, D76/D94, D80, D104,
D144 addendum 4, D155 addenda 4/4.1. Plan rows: [COMPOSITE], [MATCH-SPLIT], [EMIT-ENTRIES],
[FINDALL-NEXT], [OPT-ATTEMPT-SPLIT], [ADAPTIVE-ARM], [V-E], [EMIT-SET], [IFACE-PUSH]. Supersedes
`match_split_pinonly.md` (D163); the r1 panel's dispositions that still apply are carried in §E.

Read §0 first. §A is the tool, §B the first client, §C the cross-call hook, §D the other
clients, §E the checks, §F the build plan, §G the questions for Frank, §H the standing
questions, §I the findings.

## 0. Answers first

1. **A composite is one artifact (one pattern, one prefix, one `.c` + `.h`, one exported call
   interface, one `rx_info`) whose `.c` holds several PARTS.** Each part is the output of the
   unchanged pipeline run on a DERIVED input (an AST rewrite at the composer hook, plus
   internal emission options). A CONTROLLER, emitted per policy, implements the default
   entry set over the parts. A client is one row of a first-match table `comp_rows[]`: a
   predicate, a part list and a controller emitter (§A.1).
2. **Linkage is [EMIT-ENTRIES]' mechanism, landed first, internal-only, with zero movers.**
   An entry table with per-engine dependency edges gives every entry EXPORTED, KEPT STATIC
   or OMITTED. Today's request (everything exported) reproduces today's text byte for byte,
   so step B0 is not an abi event and needs no spec hunk. The caller-facing request (a flag
   or a `.rxt` attribute) stays with [IFACE-PUSH], where Frank put it. The twin shows why all
   three categories are needed: making the parts' entries `static` without omitting the unused
   ones fails `-Werror` on eleven unused functions and two `static`-after-`extern` `rx_info`s
   (§A.2, `twin/results/one_tu_probe.txt`).
3. **[MATCH-SPLIT]'s controller, CORRECTED.** D163's literal "else return Q's search from
   `from`" is wrong when an atomic or possessive group holds a floor arm. On
   `(?>^a|ab)c`/`"abc"` it reports `(0,3)`, but P (and libpcre2) find no match. The reason:
   at the floor itself the floor arm is LIVE in P and killed in Q, so the atomic commits
   differently. The sound controller searches Q only PAST the floor:
   `Q.search(next_pos(floor))` (§B.2). Measured: the literal controller is wrong on 3 of 94
   twin cases. The corrected one agrees with today and with libpcre2 on all 94 cases,
   1,416,556 cells (`twin/results/split_differential*.tsv`).
4. **Killing `\G` in Q is REQUIRED; killing `^`/`\A` is only a route optimization.** Q is
   searched from a position the controller chose, and a surviving `\G` in Q would assert at
   that position. The twin caught this: two corpus `\G` patterns gave 1,344 and 1,442 wrong
   cells while `\G` was left in Q under `(?m)`. A floor anchor that the derivation cannot kill
   (a `\G` inside a lookbehind) declines the composite (§B.1).
5. **The derivation needs DEAD-ARM PRUNING, not only a kill.** Q's route is chosen by facts
   that are not dead-path aware. Measured: `[^\x00-\xff]\s+|\s+$` stamps `unanchored`, while
   the pruned `\s+$` stamps `rev-end` (§B.1).
6. **Cost by counted loads (§B.5).** Trim `^\s+|\s+$` on `Q·\t^16000·Q` drops from
   128,040,002 loads to 3. The wrapper strip drops from n+3 attempt entries to 1. concat-sqli
   (S+F) needs 0.25-0.33× today's loads. One shape regresses: a trailing run before a final
   newline costs **3.00× today**, because Q's own `rev-end` runs two reverse walks and a tie.
   That cost is rev-end's (D163 places the fix there), so the one-pass two-seed walk is build
   step B3, ahead of the split. Frank's open Q3 is restated in §G.
7. **D158.** Each part's entry starts its own budget, so a composite call spends at most one
   budget per part call. With DFA-only parts no budget exists. The FIRST build admits
   DFA-only parts: 56 of the 79 floor-mixed mssurvey patterns (bench 2: concat-sqli in two
   sets; corpus 24; idioms 30), plus 9 floor-only ones. VM-bearing parts wait for a ruling
   (§G Q3) and a give-up differential.
8. **Stamps and `rx_info`.** A new `<PREFIX>_COMPOSITE` stamp goes on every artifact
   (`"none"` or the policy name). On a composite the route family reads `"composite"`
   (`_DFA_SCAN`, `_DFA_PREFILTER`, `_DFA_START`, `_DFA_MATCH`, and `rx_info.scan` /
   `prefilter` / `search_form` / `match_form`). Each part's own stamp family stays in the
   `.c` under its internal prefix. This is an abi event (§A.4).
9. **The VM hybrid is the informal precedent and stays as it is.** Re-expressing it is a
   later step with every hybrid artifact as a mover. Its trigger is building client 2, which
   would otherwise duplicate it (§A.8, §D.1).
10. **Build plan (§F):** B0 EMIT-ENTRIES internal (zero movers) → B1 part emission mode (zero
    movers) → B2 the derivation hook and `split` derivation (zero movers) → B3 rev-end's
    one-pass two-seed walk (its own abi event, [OPT-REVEND]) → B4 the composite driver and
    the split client (abi event, bit 55) → B5 VM parts on ruling → B6 the cross-call hook with
    [FINDALL-NEXT].

## A. The tool

### A.1 What a client declares

A composite policy is a row of one first-match table at the DRIVER tier (beside
`compile_driver`, in a new `src/core/composite.c`), keeping the house's "decisions as
first-match tables" rule:

```c
typedef struct {
    const char *role;        /* 1-3 chars: renders the part prefix <prefix>__<role> */
    PcrecDeriveFn derive;    /* AST -> AST, run at the composer hook (A.3)        */
    unsigned keep;           /* ENTRY_* bits the controller calls (KEPT STATIC)   */
    unsigned need;           /* PART_NEED_*: what the part's compile must deliver */
} CompPart;

typedef struct {
    const char *name;        /* the policy: stamped <PREFIX>_COMPOSITE "<name>"   */
    uint64_t deny;           /* e.g. PCREC_NO_MATCH_SPLIT (bit 55)                */
    bool (*admits)(const CompIn *in);          /* reads the plain compile + parts */
    const CompPart *parts; int nparts;
    void (*controller)(Ctx *cx, StrBuf *c, const CompEmit *e); /* writes the entries */
} CompRow;

static const CompRow comp_rows[] = {
    { "split", PCREC_NO_MATCH_SPLIT, split_admits, split_parts, 2, split_controller },
    /* later clients, each behind its own trigger (§D) */
};
```

The driver's sequence, per compile:

1. **The plain compile runs first, exactly as today.** It is the FALLBACK, so the refusal
   set cannot grow: a pattern the plain compile refuses gets no composite. It is also the
   admission's first reader, since `CompIn` carries its selections (engine, BOUND row,
   route). Every pattern a policy cannot use pays one predicate test and nothing else. Only
   the plain artifact's selections are read, never its facts re-derived, which follows the
   "one owner per derivation" rule.
2. **Walk `comp_rows[]`.** The first non-denied row whose `admits` passes on the plain
   selections compiles its parts. Each part goes through `compile_driver` with the
   derivation hook and part mode (A.3), under the same `pcrec_options` as P.
3. **A part's own failure declines the row.** A part that refuses, overflows a cap or fails
   the row's post-part conjuncts (`split_admits` reads Q's route too, §B.4) declines the
   row; "optional" covers every resource (the K53 lesson). The walk then continues. If no row
   succeeds, the plain output ships.
4. **Assemble.** The composite's header (the prologue, the shared ABI block once, the
   composite's own declarations) is followed by the parts, rendered with their part
   prefixes, then the controller and then ONE `rx_info`. The caps (A.5) are checked on the
   assembled text, and an overflow ships the plain output (A.5).

**Why the driver tier and not a start-table row.** `match_split_pinonly.md` made split a
LOCATE row inside P's attempt body, which is the splice the r1 panel found a miscompile in
(sem B-1) and arch unlock 1 retired. A composite selects among whole artifacts. Its family is
the driver's artifact-shape decisions: `fit_rungs[]` (degrade under caps), [DEC-FALLBACK]'s
tables, and now `comp_rows[]`. It is not a member of `cand_rows[]`, whose rows choose a
strategy inside one machine. Each part keeps its own full start table.

### A.2 Linkage: [EMIT-ENTRIES]' three categories, designed to the depth needed

**The entry table.** One row per caller-visible entry: `search`, `search_in`, `match`,
`match_caps`, `match_in`, `match_caps_in`, `next_pos`, `valid_upto`, `info`, `main`
(`--emit-main`), and `var_valid` (var-bearing, multi-byte). Each row has its DEPENDENCY
EDGES, per engine, read from the emitted shapes:

| entry | DFA artifact depends on | VM artifact depends on |
|---|---|---|
| `match` (search-filter form) | `search` | the anchored body (internal) |
| `match` (unwrapped form) | the anchored machine (internal) | — |
| `match_caps` | `search` (search-filter) or `match` (unwrapped) | the anchored body |
| `*_in` twins | the un-suffixed entry (`emit_in_entry_defs`: `(void)buffers; return <un-suffixed>`) | — |
| un-suffixed `search`/`match`/`match_caps` | — | their `_in` twin (`vm_emit_entries`: forward with `NULL` buffers) |
| `search` under `-futf-check` | `valid_upto` | `valid_upto` |
| `main` | `search` | `search` |
| `info` | none today ([V-E]'s entry pointers would add edges) | none |

**The rule** (Frank's charter text, with D88 add. 1's third category):
`linkage(e) = EXPORTED` if `e` is requested exported; else `KEPT STATIC` if `e` is requested
kept or is reachable through the edges from an EXPORTED or KEPT entry; else `OMITTED`.

The emitters ask one function, `pcrec_entry_linkage(cx, ENTRY_X)`, at each definition site
(`emit_in_entry_defs`, `emit_anchored_entries`, the search head, `vm_emit_entries`, the
`src/enc/` residual templates, `pcrec_emit_info`, `pcrec_emit_main`) and at each declaration
site (the `.h` block at `emit_dfa.c:1862`/`:3458`, the self-contained form's declarations).
The function returns `""`, `"static "` or "skip". A KEPT STATIC entry is declared nowhere in
the `.h`. Where its definition follows a caller, it gets a `static` forward declaration in
the `.c`.

**Why all three categories, measured.** The one-TU probe (`twin/results/one_tu_probe.txt`,
gcc 15.2, the harness's `-O1 -std=gnu11 -Wall -Wextra -Werror`):

- Two self-contained parts plus a controller compile CLEAN with every part entry exported.
  The shared ABI block is guarded, the unguarded `PCREC_FEATURE_SET`/`_MODULES`
  redefinitions are token-identical, and every other name is prefix-scoped.
- The same text with every part entry and `rx_info` made `static`, and nothing omitted,
  FAILS with eleven `-Wunused-function` / `-Wunused-const-variable` errors and two
  `static declaration … follows non-static declaration` errors (the self-contained form's
  `extern const struct rx_info`).

So "make the parts static" is not a mechanism. The closure's OMITTED category, together with
declarations that follow the linkage, is.

**How it lands.** Step B0, with the internal request only (the composite driver is its one
caller).

- Every compile that makes no request gets "all exported", so every emitted byte is today's.
  That means zero movers and NOT an abi event: D76 is about scaffolding that moves, and none
  does.
- No spec hunk is needed, because nothing a caller can observe changes.
- The CALLER-facing request (a CLI flag, a `.rxt` `target` attribute, the reduced artifact's
  stamp) is [EMIT-ENTRIES]' public half. [IFACE-PUSH] lists it as a member, so it waits there.

Finding I-4: the row's sentence "the `rx_info.nentries`/`search_form` stamps already exist to
describe the set" is wrong. `nentries` counts `groups[]` rows (match_api.md §6¶1 row 24). A
reduced public artifact needs its own stamp, which [IFACE-PUSH] designs.

**A composite's exported set is the DEFAULT set.** D88 add. 1 says one exported interface per
file. The composite exports exactly what every artifact exports (match_api.md §3¶1) under the
caller's prefix, from the controller. So a caller cannot tell a composite from a plain
artifact except by its stamps and `rx_info`. It is a drop-in, answer for answer. Every part
entry is KEPT STATIC or OMITTED, and every part `rx_info` is omitted.

### A.3 Parts: derivation and part mode

**Derivation = an AST rewrite at the composer hook.** `compile_driver` already takes a
tree-transform hook at exactly the position a derivation needs. `cx.compose`
(`compile.c:2231`) runs after `pcrec_parse` (so `ncap`, `named_groups` and the group numbers
are fixed) and before `pcrec_altcls`, the atomic discharge, the call graph and selection, so
the rewritten tree gets every optimization any tree gets. B2 turns the one hook into an
ordered list (`compose`, then `derive`).

- The derivation sees the tree the compiler compiles, not pattern text. So it is
  machine-read in the panel's sense (sem MF2): the `\G` it kills is the `\G` the machine has.
- Group numbers live on the `A_CAP` nodes and `ncap` is the parse's, so a derivation that
  deletes a subtree never renumbers a group.

"The unchanged compiler" is literal for the passes. The hook list and part mode are the only
new driver surface. The twin needs no compiler change at all: it derives by text.

**Part mode** is an internal `Ctx` field set by the driver, never a `pcrec_options` bit
(the flags word has 9 free bits and is not spent on internals). It changes emission only:

- **Names.** The part renders with prefix `<prefix>__<role>` (`<PREFIX>__<ROLE>_*` for
  macros). Under K79 the part's emitters see `PCREC_PREFIX_PLACEHOLDER` + `__<role>` (a fixed
  length) and the caller's spelling is written onto the finished text. So no selection inside
  a part depends on the caller's prefix length, which is K79's invariant held per part.
  `PCREC_MAX_EMIT_NAME_LEN` = prefix cap + 96, and the role adds 3 bytes. The long-prefix
  sweep at 60 bytes is the gate (§E.3).
- **The shared blocks.** The shared ABI block, the prologue's includes and
  `PCREC_FEATURE_SET`/`_MODULES` are OMITTED from a part (the composite header has them once).
  The part's header content (its `<P>__<R>_NCAPS`, sizing macros, `<p>__<r>_buffers` typedef)
  goes into the `.c`, as the self-contained form already does. The composite's `.h` is
  structurally a plain artifact's `.h`.
- **Linkage.** The part's entry request is `{exported: ∅, kept: CompPart.keep}`, and the
  closure does the rest.
- **Stamps.** The part's stamp family is KEPT, under its part prefix (`<P>__Q_DFA_SCAN …`).
  These macros cost no object bytes, live in the `.c` only (match_api.md §6.3.1), and are the
  per-part route record (A.4).
- **No `rx_info`, no `main`.**

**The kit's helpers.** Every memfn helper is named from its FUNC, hence from the part prefix
(D155 item 9's per-FUNC helper blocks). Its guarded `#include` lines are idempotent. By grep
over a SIMD-on artifact, the only unprefixed emitted names are the shared ABI block's (guarded)
and the two feature macros (omitted from parts). So the K80 block and the kit's blocks need
nothing new in one TU. The kit's artifact-level stamps on the composite are computed over the
ASSEMBLED text:

- `<PREFIX>_MEMFN_LIBC` from the finishing pass (memfnstamp's mechanism (b) already reads the
  whole artifact);
- `_MEMFN_FORMS` as the union over parts;
- `_SIMD_GUARDED_BYTES` and `_RUN_WORDS` as sums. RQ-3's decision view then excludes the SIMD
  bytes of every part from the composite's caps check, as it does for one artifact.

### A.4 How stamps and `rx_info` describe a composite

**The policy stamp.** `<PREFIX>_COMPOSITE` goes on EVERY artifact. It reads `"none"` on a
plain artifact (the absence value, D156 add. 2's generated-stamp shape) and the row name
(`"split"`) on a composite. It is unconditional for the house's reason (`RX_REQ_HANDOFF`,
Q3 (a)): a reader never has to infer a fact from a macro's absence.

**The route family.** On a composite, `<PREFIX>_DFA_SCAN`, `_DFA_PREFILTER`, `_DFA_START`
and `_DFA_MATCH`, and their mirrors `rx_info.scan`, `prefilter`, `search_form` and
`match_form`, read `"composite"`. That is one new value in each closed set, and the bench
relay is one line.

- Why not mirror a part's value: no single part's value is true of the artifact (`split`
  runs the floor part's attempt AND Q's scan).
- Why not a compound string: that would be a second grammar to parse.

The per-part routes are the parts' own kept stamps (`<P>__F_DFA_SCAN "attempt"`,
`<P>__Q_DFA_SCAN "rev-end"`). A consumer with no preprocessor gets the policy name only. A
`parts` field in `rx_info` is deferred to [RXINFO-REMODEL]/[V-E] under D77 (no consumer
asks).

**Engine and budgets.**

- `<PREFIX>_ENGINE` / `rx_info.engine` is `"vm"` if any part is a VM artifact, else `"dfa"`:
  the field's practical meaning is "can a call give up".
- `step_budget` / `work_budget` / capacities are the PER-PART-CALL values every part was built
  with (P's options; one budget per part entry call, §A.6).
- The caller-buffer sizing facts (§10.4's five) are the MAX over parts, because parts run one
  after another and never at once, so one caller region serves each in turn (§A.6).

**Everything else** (`flags`, `encoding`, `ncaps`, `ngroups`, `nnames`, `groups`, `pattern`,
`name`, `vars`, `findings`, `_TUNE`, `_FINDINGS`) is P's. `ncaps` is the plain compile's,
which equals P's slot count. A part with fewer slots is padded by the controller (§B.2).

**An abi event**, found by grep at build time (§E.4). The policy stamp moves every artifact
by one line, and the value sets grow.

### A.5 Size accounting and the size ladder

- **The unit is still one artifact (D88 item 3).** The caps (`--max-emit-bytes`,
  `--max-emit-code-bytes`), the size log row and `--warn-emit-bytes` all measure the
  composite's ASSEMBLED text. Parts are compiled under the same caps, each with its own
  ladder, so each must fit alone.
- **`comp_fit`, the composite's own drop.** If the assembled text is over a cap, the plain
  output ships. This is the composite's one-row ladder. It is DEGRADING in D135's sense (the
  selection chose the composite), so `--size-cap=refuse` / `--fast-or-fail` refuse instead,
  the same `fof = IN` classification as `drop-anchored`. The refusal set cannot otherwise
  grow, because the plain compile has already succeeded (A.1).
- **Measured** (`twin/results/sizes.tsv`). Linked `.text`+`.rodata`+`.data.rel.ro` with
  `--gc-sections` standing in for the omission:

  | pattern | today | composite | ratio |
  |---|---|---|---|
  | trim | 1,011 B | 3,037 B | 3.0× |
  | wrapper | 1,205 B | 2,813 B | 2.3× |
  | concat-sqli | 194,489 B | 223,029 B | 1.15× |

  concat-sqli agrees with fixes.md cand 7's 0.92-1.21×. The floor part IS today's machine
  (A.3), so a composite is roughly today plus Q's machine plus the controller. The emitted
  text in the twin double-counts the ABI block (each self-contained part carries one, about
  16 KB). Part mode removes it.

### A.6 Budgets under D158

**Each part entry initializes its own budget** (f3search: "initialized ONCE per
`<prefix>_search` call"). A composite search therefore makes at most `nparts` part calls with
one fresh budget each.

D158 asks that no composite turn an answer into a give-up. For `split` (§B) this comes down
to four facts:

- The floor part's call is one attempt of `\G(?:P)` at the floor.
- Today's first attempt is P's attempt at the same position, and on a DFA it reads the same
  loads (§B.2).
- Q's call covers the starts today's later attempts cover.
- Each of the two gets a full budget where today shares one.

**On DFA parts no budget exists**, so the condition holds trivially. The first build admits
DFA-only parts (§B.4).

**On VM parts it is a per-start claim about two DIFFERENT compiled programs.** Q is P with
dead arms removed, which can only shed the steps P spends failing them. But engine choices
(possessification, rungs, the island) are not monotone in the tree, so no structural proof
covers every program. And `\G(?:P)` may cost one more step than P at the floor, which
matters only at an exactly-exhausted budget. So VM-bearing parts wait for Frank's ruling
(§G Q3), with a GIVEUP-direction differential as the gate (§E.3).

**Composition with [EFFORT-BUDGET]'s single shared budget** ([FINDALL-NEXT]'s "composed
matchers charge ONE shared budget") would be the stricter form. A shared budget can only give
up earlier than separate budgets, so adopting it later needs Q's per-start work ≤ P's, the
same claim.

**Caller buffers (VM parts, later).** The composite's `<p>_buffers` is the inert shape on a
DFA-only composite. With VM parts it is one region sized by the max over parts. The
controller builds each part's descriptor from it per call (capacity = bytes ÷ the part's
frame size), with the alignment the max.

### A.7 Where it lives, and the readers

- **Files.** `src/core/composite.c` holds `comp_rows[]`, the driver and the assembler (driver
  tier, the layer of `compile.c`). Part mode and `pcrec_entry_linkage` live in `src/gen/`.
  Derivations live in `src/opt/derive.c` (the `split` kill-and-prune, §B.1), beside the
  rewriting passes.
- **The listing.** `--emit-ir` and `--emit-facts` of a composite print the policy row, then
  each part's own listing under its role. The spec hunks are in `ir_listing.md` and
  `facts_listing.md` (§F B4).
- **Trace.** Each part's compile runs its own start table, so the trace build's records for a
  composite are the parts' records tagged by role. The trace SET gate's site keys grow by
  that, and the growth is declared.

### A.8 The VM hybrid: re-expressed now or later?

**The hybrid is the informal precedent.** `emit_vm.c:12761` emits the capture-erased DFA
search through `pcrec_emit_dfa_engine(cx, prefn, "static ")` under a private name. The VM's
search entry is its controller.

**It differs from a composite in two ways:**

1. The machine comes from the SAME `Job` (D31 erasure at parse), not from a separate compile.
2. Its hand-off is richer than an entry call: the window end becomes the MRL ceiling
   (`mrl_win`), and the reseed rows, the landing and the handoff read DFA internals.

**Re-expressing it now would move every hybrid artifact** (names, order, its stamps becoming
a part's). It would also need a part interface wider than entries (a window, a reseed
protocol), which no other client needs yet.

**Later, with that interface.** Trigger (D77): client 2 (§D.1) is built and would otherwise
duplicate the hybrid's locate-then-finish. The movers are then every `RX_VM_PREFILTER
"hybrid"` artifact, a manifest by ID.

## B. First client: [MATCH-SPLIT]

### B.1 The parts

- **F (role `f`), the floor part = `\G(?:P)`.** The derivation wraps the root:
  `A_CAT(A_GSTART, root)`. Searched from `from`, it is the first iteration of P's own attempt
  loop:
  - BOUND's existing `attempt-gstart` row gives `start_max = search_from` (read on this branch:
    `const size_t start_max = search_from /* fully \G-anchored */;`).
  - P's own `^` and `\G` keep their meaning, because both are true at the floor (`from == 0`
    for `^`; `\G` at `from` in both).
  - utf8: the K73 SEEK moves a mid-character `from` past `start_max`, so no attempt runs.
    That is right: P's first attempt there would be at a later boundary with `\G` false,
    which Q covers. The boundary guard refuses exactly as P's would (same encoding, same
    options, same check first).

  No compiler change and no BOUND row are needed.
- **Q (role `q`) = P with its floor anchors killed, then pruned.** Two passes, in
  `src/opt/derive.c`:
  1. **Kill.** Every `A_GSTART`, and every `A_BOL` with `!u.anch.multiline` (`^` without
     `(?m)`, and `\A`), becomes the never node (an empty `A_CLASS`, which lowers to the
     dead-by-construction `N_CLASS` with an empty set).
     - The kill skips a node inside a lookbehind, or inside a group called from one. Such a
       node can be evaluated at a position below the attempt start, where `^` can be true.
     - `(?m)^` (`A_BOL` multiline, `N_BOT_M`) is NOT killed. Q handles line starts itself,
       which is today's MLINE route. This retires the bot_m deletion hazard (panel sem MF1)
       by construction: Q keeps every path that has no absolute floor anchor.
     - **A `\G` the kill cannot reach declines the composite.** Q's surviving `\G` would
       assert at the position the controller searches Q from (§0 item 4; the twin's
       1,344/1,442 wrong cells).
  2. **Prune, bottom-up.**
     - `CAT` with a never part is never.
     - `ALT` drops never arms (all never → never).
     - `REP{m≥1}` of never is never; `REP{0,…}` of never is `EMPTY`.
     - `CAP`, `ATOMIC` and a positive `LOOK` of never are never; a negative `LOOK` of never
       is `EMPTY`.
     - Calls and conditionals are left as they are (conservative).
     - A pruned `A_CAP` takes its number with it and renumbers nothing.

**Why the prune is needed, measured.** Q's route is chosen by facts (`end_pin`,
`start_anchor`) that are path analyses and do not know a never arm is dead. The unpruned
`[^\x00-\xff]\s+|\s+$` stamps `RX_DFA_SCAN "unanchored"`, while the pruned `\s+$` stamps
`"rev-end"` (read on this branch). Pruning inside the derivation only, rather than in the
default pipeline, keeps every non-composite artifact unmoved. Applying it to the default
pipeline (mssurvey's 75 dead-anchor corpus patterns) would be a separate mover row (U2, §G).

**If Q prunes to never**, every live path of P passes a killed floor anchor, so no match
starts after the floor. The composite is then the floor part alone (§B.6, a fall-out).

### B.2 The controller (emitted text; the twin's `twin/ctrl.c.in`)

```c
int <p>_search(const unsigned char *s, size_t n, size_t from, ptrdiff_t (*caps)[2])
{
    if (from > n) return 0;
    size_t qf = from;
    if (from == 0 || <HAS_G>) {                 /* the floor can be live */
        int r = <p>__f_search(s, n, from, caps);
        if (r != 0) return r;                   /* match, give-up or refusal */
        qf = <p>_next_pos(s, n, from);          /* Q only PAST the floor */
    }
    int r = <p>__q_search(s, n, qf, caps);
    if (r == 1 && caps)                         /* only where Q has fewer slots */
        for (int k = <P>__Q_NCAPS; k < <P>_NCAPS; k++) caps[k][0] = caps[k][1] = PCREC_UNSET;
    return r;
}
```

`<HAS_G>` is a compile-time `0`/`1`: did the derivation see an `A_GSTART`? That is read from
the tree, not from a separate fact. The padding loop is emitted only when
`<P>__Q_NCAPS < <P>_NCAPS`, so the composite never carries dead text and never trips
`-Wtype-limits`.

**The soundness argument.** `f` is the floor position, the first position P's own loop
attempts with a floor anchor true (0 when `from == 0`, `from` when `\G` is present and `from`
is a boundary).

1. **(Floor first.)** Every start a match can have is at least `f`. If F matches at `f`, that
   match is P's priority match at the leftmost possible start, so it is P's answer. F is P's
   own attempt at `f`.
2. **(Past the floor.)** At any start `t > f`, every killed node evaluates false in P too:
   - a `^`/`\A` is read at a position ≥ `t` > 0 (the lookbehind exclusion ensures this);
   - a `\G` at a position ≥ `t` > `from`.

   A false node and a never node behave identically under every construct (alternation
   order, atomic commits, possessive loops, backreferences, lookahead). So P anchored at `t`
   and Q anchored at `t` are the same matcher. Q has no `\G`, so Q's search from `qf` returns
   the leftmost start ≥ `qf` with P's priority there. That is P's answer, since F failed at
   `f` and nothing lies in `(f, qf)`: `qf = next_pos(f)` is P's own retry advance.
3. **(Floor skipped.)** When `from > 0` and there is no `\G`, every start ≥ `from` > 0 is
   "past the floor", so `Q.search(from)` is exact. The twin includes the no-`\G` corpus rows.
4. **(Why not `Q.search(from)` after a failed floor, as D163 reads.)** At `t = f` the floor
   arm is live in P. When an atomic or possessive group holds it, P's commit at `f` differs
   from Q's. `(?>^a|ab)c` on `"abc"`: P commits to `^a` at 0 and then fails on `c`, so P and
   libpcre2 find no match. Q at 0 takes `ab` and reports `(0,3)`. The twin's literal variant
   is wrong on exactly the three atomic/possessive witnesses
   (`twin/results/split_differential_literal.tsv`). The sem critic's 54.2M-cell simulation
   had no such shape. Finding I-1.

**The requirements (match_split_requirements.md §2.1) against this controller:**

- **R1 (leftmost) / R2 (priority).** Items 1-3 above; FINISH is never a class sub-machine.
- **R3 (empty matches, find-all).** The controller changes no reported span (it returns F's
  or Q's answer, each P's). So the §3.1.3 loop reads identically. The witnesses `^|end$` and
  `^|$` are in the twin, 0 differences, find-all included.
- **R4 (`search_from > 0`) / R5 (`\G`).** Item 3, and `<HAS_G>`. The `\G` floor at a
  mid-character `from` is handled by F's own SEEK (§B.1).
- **R6 (`(?m)`).** `(?m)^` stays in Q (§B.1). Q's line-start rule is today's.
- **R7 (`$`/`\Z` before a final newline).** This is Q's own route (rev-end's two seeds). The
  tie witness `^q|a$|a\n$` gives 0 differences.
- **R8 (context at a start).** Q's search reads `s[qf − 1]` exactly as P's attempt at `qf`
  does (N1 of `assertions_design.md`), so `\b`, lookbehind and `(?m)^` are evaluated the same.
- **R9 (captures).**
  - F's and Q's slot layouts are P's (groups keep their numbers, A.3).
  - A slot Q lacks belongs to a pruned floor arm, which is dead past the floor, so it is
    PCREC_UNSET in P's match too. The controller pads it.
  - On a non-1 return `caps` is untouched (§3.1¶4), so Q writes into a clean array after F
    fails.
  - In the twin every Q keeps P's groups, so the padding loop is UNREACHED there. Its
    witness needs a pruned capture on a VM P, which the first build does not admit (§E.2,
    CMP-5).
- **R10 (utf8).** `next_pos` is the encoding's. sem B-1's witness `\Ga\n?|a$|a\n$|$` under
  `-e utf8` and the 2016-outage trim form are in the twin: 0 differences. **The B-1 bug class
  cannot occur**: the controller never writes `from`. It passes `from` to F (whose `\G` must
  see it) and a new `qf` to Q (which has no `\G`).
- **R11 (D158).** §A.6.
- **R12 (every deny).** Parts inherit P's options, so `-fno-rev-end` etc. act inside Q.
  `-fno-match-split` removes the row, and the plain output ships byte for byte (§E.3 G6).
- **`\K`.** Reported starts may exceed attempt starts. F and Q both report P's (the attempt
  order is what the argument uses). `^a\Kb|c$` is VM-routed (`\K` forces the VM), so the
  first build declines it. It is a negative control (§E.2).

### B.3 The other entries

| composite entry | body | why |
|---|---|---|
| `<p>_search` | the controller (B.2) | — |
| `<p>_match`, `<p>_match_caps` | F's (`<p>__f_match`, `<p>__f_match_caps`, KEPT STATIC) | F ≡ P anchored at any position: at `pos > 0` both sides' `^` are false, `\G` is at `pos` in both, and at 0 they are equal |
| `<p>_search_in`, `<p>_match_in`, `<p>_match_caps_in` | the un-suffixed entry, with `(void)buffers` (DFA-only composites) | a DFA artifact's own `_in` shape |
| `<p>_next_pos`, `<p>_valid_upto` | the composite's own (the encoding residual, emitted once) | the parts' copies are OMITTED unless a part body needs them (`-futf-check`'s edge, A.2) |
| `<p>_info` | one, per A.4 | — |

**A side effect of `_match` delegating to F.** On an attempt-route P, today's `_match` is
`"search-filter"` over the WHOLE attempt loop from `pos`, so a failing probe can run every
later attempt. F's search-filter `_match` runs ONE attempt. Answers are identical (the filter
rejects any later start anyway), and a failing probe becomes O(attempt) instead of
O(n · attempt). Finding I-5.

### B.4 Admission: the `split` row's predicate

`split_admits` is a conjunction of facts read off compiles. No constant is hand-set (memory
`pcrec-suspect-tuning-constants`).

| # | conjunct | read from | why |
|---|---|---|---|
| A1 | P's plain compile is on an attempt route with BOUND `all` (DFA `attempt[subject_length]`, a hybrid on the attempt body, or VM-only with no start bound) | the plain compile's selections | today attempts every start: the cost the split removes. A fully anchored P (BOUND `bot`/`attempt-gstart`) is already one attempt, so A1 keeps it byte-identical |
| A2 | the derivation killed ≥ 1 floor anchor and left no `\G` | the derivation's own counts | §B.1 |
| A3 | Q is never, or Q's compile does NOT select BOUND `all` on an attempt route | Q's compile | Q gained a locator, or the composite is floor-only (§B.6). A Q still on the attempt-every-start route (an LS arm on MLINE, a lookbehind-held `^`) buys nothing, so the row declines |
| A4 | every part is a DFA artifact (first build) | the parts' engine selections | D158 (§A.6); widened by ruling (§G Q3) |
| A5 | the assembled composite fits the caps | `comp_fit` (A.5) | D84 |
| A6 | not denied: bit 55 `-fno-match-split` | flags | ruled (Q1) |

**Counted on mssurvey's populations** (`ms_rows.tsv.gz`; floor-mixed = a mix containing S or
G plus another class; Q's route is the survey's free part `fr_*` or END part `en_*` compiled
alone, a proxy the build replaces with Q's own compile):

| mix | today's route | count | Q (proxy) | first build (A4) |
|---|---|---|---|---|
| S+E | dfa-attempt[n] | 20 | dfa-rev-end | admit |
| S+E | hybrid-attempt[n] (captured wrapper) | 1 | (VM part) | decline → B5 |
| G+E | dfa-attempt[n] | 1 | proxy `dfa-attempt` | A3 decides on Q's own compile |
| S+F | dfa-attempt[n] (incl. concat-sqli ×2 bench) | 18 | dfa-unanchored | admit |
| S+F | hybrid-attempt[n] / vm-only | 3 / 5 | VM | decline → B5 |
| G+F | dfa-attempt[n] | 13 | dfa-unanchored | admit |
| G+F | hybrid-attempt[n] / vm-only | 8 / 2 | VM | decline → B5 |
| S+E+F | dfa-attempt[n] | 4 | E∪F, unanchored | admit |
| G+LS, S+LS | dfa-attempt[n] | 2, 1 | MLINE attempt | A3 declines (K109 is Q's own) |
| S+LE | hybrid-attempt[n] | 1 | VM | decline → B5 |
| S, G single-class | attempt[n] | 7 + 2 DFA, 1 VM | never (floor-only) | admit the 9 DFA (§B.6) |

Totals (counted exactly, DFA `attempt[subject_length]` and no LS arm): **56 floor-mixed
patterns admitted by the first build, of 79** (bench 2: concat-sqli in `capability` and
`sentinel`; corpus 24; idioms 30). The one G+E row depends on A3 reading Q's own compile.
Plus **9 floor-only** single-class patterns (7 S, 2 G; a tenth, G on the VM route, waits for
B5).

**The 4a/4b staging dissolves.** START+FREE ([OPT-ATTEMPT-SPLIT], concat-sqli) and
START+END+FREE are admitted by the same predicate with no new build, because Q's locator is
Q's own (arch unlock 1). LS+LE (K106's `(?m)` shapes) and E+LE have no floor, so they are not
`split` material. They stay with 4b.2 / a per-class client (§D.2).

**Dominance.** On every subject and call:

- the composite's loads ≤ today's + Q's start-recovery term, which is
  - `rev-end`'s second seed and tie on a `$`-pinned Q before a final newline, or
  - the reverse pass on an unanchored Q (at most the match length).
- **Why:** F's attempt reads exactly today's first attempt (the same residual languages,
  minimal machines). Q's forward scan reads no more than today's later attempts, which each
  read at least one byte and the successful one to its death point.
- **What the start-recovery term means in practice:** it is a cost of Q's route, not of the
  composite. On `rev-end` it is removed by B3. On an unanchored Q it is at most 2× on the
  matching call, and the twin's S+F cells read 0.25-0.33× overall. Frank's open Q3 is
  whether to admit before B3 (§G).

### B.5 Cost by counted loads (`twin/results/split_loads.tsv`)

The unit is subject-byte loads of a whole find-all (the survey's `qdrv.c` instrument). Q is
pruned by hand, standing in for §B.1. Calls and matches are equal on every row (asserted).

| cell | subject (k = 16,000) | today T | composite T | ratio | growth per 4× k |
|---|---|---|---|---|---|
| trim `^\s+\|\s+$` | `Q·\t^k·Q` | 128,040,002 | **3** | 0.00000002 | today 15.99, composite flat |
| trim | `Q·\t^k` | 16,002 | 16,003 | 1.0001 | linear both |
| trim | `\t^k` | 16,000 | 16,001 | 1.0001 | linear |
| trim | `Q·\t^k·Q\n` | 128,024,003 | **8** | 0.00000006 | — |
| trim | `Q·\t^k·\n` | 16,003 | **48,007** | **3.00** | linear both; Q's rev-end two seeds + tie (the panel's B1) |
| trim | `\t^k·Qx` | 16,003 | 16,003 | 1.0000 | — |
| wrapper `^\s*\{\|\}\s*$` | `Q·}^k·Q` | 32,003 (n+3 attempts) | **3** | 0.0001 | — |
| wrapper | `Q·}^k` | 32,001 | 5 | 0.0002 | — |
| wrapper | `Q·␠^k·}` | 16,002 | 5 | 0.0003 | — |
| concat-sqli (S+F) | `Q·(select␠)^k·Q` | 447,999 | 112,004 | 0.25 | linear both |
| concat-sqli | `Q·(xxxx␠)^k·Q` | 256,005 | 80,004 | 0.31 | linear |
| concat-sqli | `Q·a^k·Q` | 48,005 | 16,004 | 0.33 | linear |

K106's quadratic is gone and the wrapper strip's n+3 attempt entries become one. concat-sqli,
the only bench reach, reads a quarter to a third of today's loads.

**The single regression is the final-newline trailing run.** It is the start-recovery term
of §B.4, measured: Q = `\s+$` on `rev-end` seeds `n` and `n−1`, walks back twice, and
resolves the tie with a forward attempt (≈ 3k). Today's attempt at 1 reads k+1. Step B3
(rev-end's one reverse pass seeding both ends, D163: "the two-seed cost fix belongs to rev-end
itself") is the fix. It also lowers K103's entry floor for every rev-end artifact. The G3 gate
(§E.3) holds the composite to today + c on this shape, so G3 is RED until B3 lands. That
ordering is deliberate.

### B.6 What falls out

- **START+FREE and START+END+FREE.** Same build, same row (§B.4).
- **The floor-only composite.** When Q prunes to never, the composite is F alone: one attempt
  where today attempts every position. That covers the 9 DFA single-class S/G patterns on
  `attempt[n]` (a tenth is on the VM route, B5). They are mssurvey finding 6's start half (an optional consuming prefix before
  `^`/`\A`/`\G`, e.g. `a{0,4}\A`), where the shipped `start_anchor` is conservative. The
  derivation proves what the fact could not, with no change to the fact. The population is
  corpus witnesses only.
- **`_match` becomes one attempt** on admitted patterns (§B.3).
- **Dead floor arms** (`x^a|b$`) are admitted. The floor attempt is wasted but sound, and Q is
  `b$`.

## C. The cross-call state hook (D163 item 1; design only, built with [FINDALL-NEXT])

**Where it lives.** In the caller-owned, versioned struct [FINDALL-NEXT] designs (Frank,
session 108: `_search_in` takes a caller-filled struct "so the interface grows without breaking
callers" and "preserves information between calls").

- The artifact publishes `<PREFIX>_ITER_STATE_WORDS`, the words of opaque per-artifact state
  it wants in that struct.
- A composite's is its controller's, declared by the row (`CompRow.state_words`, plus two
  emitted functions: `<p>__cache_get` / `<p>__cache_put`).
- Today's entries ignore it, so a plain artifact publishes 0.

**What `split` caches** (4 words: `qf`, `qs`, `qe`, `valid`):

1. **Q's result.** A Q search from `qf` returning `(qs, qe)` answers every later call with
   `qf ≤ from' ≤ qs` that reaches Q. Q has no `\G`, so Q's search is monotone in `from`: no Q
   match starts in `[qf, qs)`, and Q's match at `qs` does not depend on `search_from`. A Q
   NOMATCH from `qf` answers every later call with `from' ≥ qf`.
2. **The floor skip.** Once `from > 0` with no `\G`, the floor is dead for the rest of the
   session, which the stateless controller already knows from `from` alone. With `\G` the
   floor moves with `from` and is never skipped.

**Invariants.**

- **History-independence.** An answer from the cache equals the answer a fresh call gives.
  The entry is keyed by the struct's bound `(s, n)` (set at init; a different subject is a
  re-init), and validated by the inequalities above.
- **No statics.** The state is in the caller's struct (§5.3 holds).
- **D158.** A cache only skips work. A give-up is NEVER cached: a fresh call might answer, so
  replaying a give-up would make answers history-dependent.
- **Versioning.** A struct too small for `<PREFIX>_ITER_STATE_WORDS` means "no cache", never
  an error.

**Who it pays for.** Pin-only find-all reports matches that end at or past `qs`, so the next
call's `from` is past `qs` and the cache never hits. That is why D163 builds it later. It pays
for:

- 4c (two racing parts: the loser's result is reused instead of re-scanned, the N2
  repetition);
- [ADAPTIVE-ARM]'s counters;
- callers that re-search overlapping ranges.

Trigger: [FINDALL-NEXT] at [IFACE-PUSH].

## D. Other clients — feasibility sketches, not designs

For each: what the TOOL must offer (so it is not shaped only by split), and its D77 trigger.

### D.1 Captures by DFA LOCATE + VM FINISH

**Not new where P is a hybrid.** The hybrid already runs the capture-erased DFA search and
hands the VM the start (capsurvey F1: pcrec "already implements the RE2/rust two-pass
hybrid").

**New on the VM-only route where the hybrid's prefilter is DECLINED for a reason that does not
apply to a full exact search.**

- The named case is the nullable decline (`lang_nullable_declinable`): a prefilter whose every
  position is a candidate is worthless. But a full DFA SEARCH artifact with its own locator
  (`rev-end` on an end-pinned language) stays linear.
- That is exactly K108's population: `(\s*)$`, `(a*)$` and similar, 10 of 16 shapes
  quadratic on the VM.
- The composite would be: part L = P with captures erased, compiled as an ordinary search;
  part V = P's VM, keeping `_match_caps`. The controller is `L.search(from)` and then
  `V.match_caps(ctx{pos = start})`.
- Exact because L's language is P's (D31) and V gives P's priority at the leftmost start; no
  end hand-off is needed.

**The tool must offer:**

- a derivation by OPTIONS (captures erased: the existing no-captures route, as a part option);
- a part kept for `_match_caps` only;
- a controller pattern "locate, then finish at the start";
- VM-part budgets (§A.6).

**Trigger:** K108 bench reach (a bench or wild cell with the shape). That is also when to
compare it against widening the hybrid (the alternative: drop the nullable decline when the
locator is exact).

### D.2 Per-branch locators / 4c (D151 add. 6 F2)

- **Parts:** one search per arm class (a derivation that keeps one class's arms), plus a
  finisher.
- **Controller:** the minimum start over the class searches, then P at that start.

**The tool must offer an internal entry beyond the public set:**
`<part>_attempt(s, n, search_from, start, caps)`, one attempt at `start` with `\G` at
`search_from`. `_match` cannot serve, because it has no `search_from`, and 4c's finisher runs
at `start > from` with `\G` false. This is arch unlock 2's FINISH `attempt-at`, as a kept
static entry. The tool also needs §C's cache for the losing classes.

**Trigger:** the [ENG-TACTICS] stage-1 census or a bench cell with two racing classes. K106's
`(?m)` trim shapes (4b.2) are the corpus/idiom witnesses.

### D.3 [ADAPTIVE-ARM]

- **Parts:** the same pattern compiled under two option derivations, e.g. the handoff admitted
  versus `-fno-req-handoff` (K105), or reseed `exact` versus `fixed`.
- **Controller:** a counter in §C's state chooses the arm. Both arms are exact, so the choice
  moves cost, never answers. D158 must hold per arm, and an arm switch never turns an answer
  into a give-up (the same separate-budget argument).

**The tool must offer:**

- derivation by deny bits;
- run-time selection state (§C);
- a stamp listing the arms (the parts' kept stamps).

**Trigger:** the row's own (a prior-contradicting cell timed past the null band, `bak-2` vs
`phone-no-start-set`).

### D.4 Arch-specific versions with run-time dispatch

**The kit already selects per SITE inside one artifact** (D155: a per-FUNC selector chain over
guarded per-level helpers, compile-time `-fmemfn-simd`). A whole-artifact arch composite is
the COARSE alternative:

- parts = the same pattern rendered for different levels (`levels.def`);
- each part's functions carry `__attribute__((target(...)))`. Per-function target attributes
  are legal in one TU, unlike a per-file `-march`, so gcc can vectorize or schedule the WHOLE
  body for that level;
- the controller dispatches on the CPU per call through the kit's level query.

**The dispatch mechanism:**

- No artifact-owned static (§5.3). `__builtin_cpu_supports` reads libgcc's
  constructor-initialized model, which memfnisa measured at about a direct call when cached.
- ifunc is ELF-only and answers wrong on Darwin.
- Each part is guarded `#if` per architecture, so the TU still compiles elsewhere (C18's floor
  rule: the SIMD-off rendering plus guarded text).
- D144 add. 4's targeted-hardware verdicts decide each level.

**The tool must offer:**

- part options that set a target level;
- per-part target attributes and arch guards;
- a dispatch controller;
- size accounting that counts every level (A.5).

**Trigger:** a SIMD form that must ship beside its scalar form at the whole-artifact grain,
i.e. a body-wide target attribute measured to beat the kit's per-site selection on a targeted
box (the plan row's trigger, D144 add. 4).

## E. Checks

### E.1 Carried over from the r1 panel (still applicable to the composite)

- **chk M2** (a plant must reach): every row below names a witness whose clean build stamps
  `<PREFIX>_COMPOSITE "split"` (`SAB_REACH`), with a per-ID population floor in
  `SAB_REACH_POP`.
- **chk M3** (MS-4's witness had an empty floor): witnesses are chosen with a live floor.
  `^a|(?m:b$)` and `\Ga$|b$` at startpos > 0 are G1 cells.
- **chk M4** (decline conjuncts): one negative control per conjunct, reach-proved by the
  stamp reading `"none"`:
  - `^a\Kb|c$` (`\K`, VM, A4);
  - `(?<=^a)b|c$` (a lookbehind-held `^`, A3);
  - `^x|\n(?m)^b$` (an LS arm, A3);
  - `(?<=\G)a|b$` (an unkillable `\G`, A2);
  - `^(\s*)\{|\}(\s*)$` (VM part, A4);
  - `^a$` (fully anchored, A1).
- **chk M5** (G3 vacuous-capable): G3 compares against TODAY on the same subject (§E.3). The
  population is a per-ID manifest, not a count.
- **chk M6** (re-pins as a grep recipe): §E.4.
- **chk S1** (breadth): mssurvey's 35 planted C4 witnesses are G1 controls. The cells include
  `a\n\n`, empty, startpos > 0, startpos > n, a utf8 mid-character startpos, a `(?m)` scoped
  arm, and the hybrid floor + E tie.
- **chk S2** (constructed overflow witnesses): one Q that overflows a cap while P fits (the
  composite declines and today ships), and one composite that fits only without the drop
  (CMP-7).
- **chk S3, S4.** The independent controls are libpcre2 (G1, G2) and today's artifact under
  `-fno-match-split`. Neither shares the composite path.
- **sem N1** (interior `$`): `^x|a$\n`, `^x|a$\n?`, `^x|a$(?=\n)` are G1 cells.
- **sem N2.** Q's exactness is now the derivation lemma (§B.2 item 2), checked by G5.
- **sem N3.** The G+E find-all wording is fixed: `\G\n|b$` on `"b\n"` gives `(0,1),(1,2)`, a
  G1 `mc` cell.
- **The grep-derived re-pin list.** §E.4.

### E.2 Sabotage rows

Ids are allocated by the manager. Main's highest is S845 at `a080c69a`; the kit's reserved
ranges in `memfn/docs/requests.md` must be checked first.

| row | plant | direction | detector and reach |
|---|---|---|---|
| CMP-1 | controller searches Q from `from` (D163's literal text) | answer | `(?>^a|ab)c` on `"abc"`: twin-proved (literal variant wrong on 3/94 cases) |
| CMP-2 | `<HAS_G>` emitted 0 on a `\G` pattern | answer | `\Gab|cd`, startpos cells > 0 |
| CMP-3 | the kill skips `A_GSTART` | answer, plus G5 | `(?m)^a|\Gb` (gpos.rxt:453): twin-proved, 1,344 wrong cells |
| CMP-4 | `split_admits` returns false | **efficiency; answers unchanged** | G3 and the per-ID `"split"` population floor, the direction no answer check sees |
| CMP-5 | the padding loop dropped | answer | a pruned capture on a VM P. **UNREACHED in the first build** (A4 declines VM P), declared with its derivation |
| CMP-6 | a part entry left EXPORTED | linkage | G4's symbol-set gate |
| CMP-7 | `comp_fit` deleted | refusal set | lowered-size variant (emit_sweep `stderr`, `lowsize`): the composite refuses where today compiles |
| CMP-8 | F loses its one-attempt bound (the `\G` wrap dropped) | **efficiency; answers unchanged** (F then returns P's whole answer) | G3's wrapper cell (attempt entries ≤ 1) |
| CMP-9 | the prune drops a live `ALT` arm | answer | G2 on the S+F rows |
| CMP-10 | the kill also kills `(?m)^` | answer | `^x|(?m)^y` find-all over `"x\ny"`: Q loses `(2,3)` |

### E.3 Gates and witnesses

- **G1 corpus** `tests/composite/split.rxt` (a new directory with its own CLAUDE.md),
  oracle-first against libpcre2 10.46. It holds:
  - mssurvey's 79 floor-mixed patterns plus the 10 floor-only ones (the VM-route one as a control);
  - the §5.1 witnesses;
  - the atomic and possessive witnesses;
  - the tie, interior-`$`, context-led and nullable cells;
  - the captured wrapper (as a control);
  - a utf8 block with the outage form, ill-formed subjects and sem B-1's witness;
  - `mc` find-all throughout.
- **G2 the every-startpos and find-all differential**: composite vs `-fno-match-split` vs
  libpcre2 over generated subjects for every admitted corpus pattern and idiom, with ASan and
  UBSan arms. This is the twin's `diff.c`, promoted. The bar is 0 differences.
- **G3 counted work**: `tests/composite/run_linear.sh`, promoting `qdrv.c`, at k ∈
  {1000, 4000}. It asserts `T_composite ≤ T_today(-fno-match-split, same subject) + c`
  on named shapes: internal run, trailing run, trailing run + `\n`, no-match + trailing
  `\n`, S+F concat-sqli. c is a small fixed allowance: the twin's largest excess over today
  on any non-regressing shape is 1 load (`split_loads.tsv`), and c = 8 leaves room for the
  two seeds' probe bytes. It also asserts growth ≤ 4.5 per 4× and attempt entries ≤ 1 per
  call on the wrapper. **RED on the final-newline shape
  until B3.**
- **G4 export.** A composite's `nm -g` set equals the default entry set for its prefix (the
  set a plain artifact of that prefix exports). No `<p>__*` symbol is global, no part
  `rx_info` object exists, and the `.h` declares exactly a plain artifact's declarations.
- **G5 derivation soundness.** In the trace build, over every admitted corpus artifact, Q's
  tree has no `A_GSTART`, and every surviving `A_BOL(!multiline)` is inside a lookbehind (or a
  group called from one). Q being never ⇔ the floor-only form.
- **G6 the landing bar.**
  - The five fully-anchored attempt artifacts (`ipv4-near-miss`, `uuid-near-miss`,
    `base10num-near-miss`, `winpath-near-miss`, `wild-validator-email-owasp`; A1 false) are
    byte-identical with the split ON, apart from the abi digits and the `"none"` stamp line.
  - concat-sqli and all five are byte-identical under `-fno-match-split`.
  - Pin by ID.
- **The D158 give-up differential** (the gate for B5): composite vs `-fno-match-split` at
  lowered `--step-budget`/`--work-budget`/frames on every VM-bearing candidate. It must find
  0 cells where today answers and the composite gives up.
- **Long-prefix and K79.** `run_longprefix_sweep.sh` at 60 bytes over composites (part names
  within `PCREC_MAX_EMIT_NAME_LEN`), and `run_prefix_invariance.sh` extended to composites
  (identical modulo names at `-p rx` vs a long prefix).
- **Short-call cell, scratch tier.** trim and wrapper at n ∈ {0, 1, 2, 8, 64}, composite vs
  `-fno-match-split`, interleaved. This is the controller's fixed term (two entry calls). A
  loss beyond the noise floor becomes a K row, not a predicate (D144's disposition precedent).

### E.4 The re-pin and re-aim list, as a grep recipe (D94)

Run at B4, on the branch, before delivering:

```
# abi readers
grep -rn 'PCREC_ARTIFACT_ABI\|abi 76\|\.abi = 76\|PCREC_RX_ABI_H 76\|(abi 76)' src tests docs/spec scripts docs/dev/history
# every enumeration of the route value sets (the new "composite" value)
grep -rln '"rev-end"' tests scripts docs/spec        # RX_DFA_SCAN / rx_info.scan readers
grep -rln '"attempt-start"\|"search-filter"' tests scripts docs/spec
# the bit and axis readers (bit 55)
grep -rn 'PCREC_BIT(54)\|NO_START_LANDING' src/core/axes.def lib/pcrec.h tests/registry docs/spec
# byte-count readers (the new stamp line moves every artifact; D94 addendum: re-derive by measurement)
grep -rln 'EMITTED_BYTES\|762[0-9][0-9][0-9]\|VARIANT_PINS' tests scripts
# the corpus census readers for tests/composite/split.rxt
grep -rln 'CENSUS_FILES\|C3_PASS' tests; ls tests/startset/manifests
# re-aims: anchors in code the build moves (compile.c's driver tail, the emitters' entry sites)
python3 scripts/sabotage_anchors.py --step <B4 commit>
```

The readers already known: the (B) FILEPIN in `run_recursion_identity.sh`,
`docs/dev/history/abi_changelog.md`, the cpset `EMITTED_BYTES` manifest, the resource rescue
pins, the size-term manifests, the registry axis pins and count, `run_dfa_stamps.sh`
(field == macro over the new value), `run_form_census.sh` floors, the emit_sweep
`--emit-facts` stream and `--list-axes` dump, the trace SET gate's site keys, the startset
mover manifests and the rxtsource census.

## F. Build plan

| step | what | movers / abi | size |
|---|---|---|---|
| **B0** | [EMIT-ENTRIES] internal: the entry table, the dependency closure, `pcrec_entry_linkage` at every definition/declaration site, an internal request type; a unit check that an internal `{keep: search}` request compiles `-Werror`-clean and leaves exactly `{search}` plus its closure | **zero movers** (emit_sweep, all streams); not an abi event; no spec hunk | M (~400 lines over emit_dfa/emit_vm/enc) |
| **B1** | part mode: part-prefix rendering under K79, omission of the shared blocks, `rx_info`, `.h` declarations and `main`, header content into the `.c`, stamps kept | zero movers (no default compile is a part) | S-M |
| **B2** | the derivation hook list (`compose`, `derive`) and `src/opt/derive.c`: the floor kill (with the lookbehind exclusion and the `\G` decline) and the never-pruning | zero movers | S |
| **B3** | [OPT-REVEND] the one-pass two-seed walk (seed `n` and `n−1` in one reverse pass; resolve the tie where the seeds' accepting ends decide it). Owned by [OPT-REVEND] | its own abi event; movers = every `$`-pinned rev-end artifact | M |
| **B4** | `src/core/composite.c` (`comp_rows[]`, A1-A6, assembly, `comp_fit`), the split controller emitter, `<PREFIX>_COMPOSITE` on every artifact, the `"composite"` route values, `-fno-match-split` (bit 55, masked in `strategy_denials`, not engine-selecting), G1-G6, CMP-1..10. Spec hunks: match_api.md §1¶2 (`<prefix>__*` reserved internal), §3¶1 (a composite exports the default set), §3.2 (`_match` on a composite), §6 rows 7-15 and 20-22/25 (values and per-part-call budgets), §6.3 (the stamp and value sets); tuning.md a new `-fno-match-split` section; limits.md (caps on the assembled text, `comp_fit`); registry.md (axis, counts); ir_listing.md / facts_listing.md (the composite listing) | **abi event**; movers = every artifact by one stamp line, plus the 56 admitted + 9 floor-only, by ID | M-L |
| **B5** | VM-bearing parts (20 of the 79), on Frank's ruling (§G Q3), behind the give-up differential; caller-buffer composition (§A.6) | movers = those, by ID | M |
| **B6** | §C's hook with [FINDALL-NEXT] at [IFACE-PUSH] | that push's | S (for split) |

B0-B2 are one lane's no-mover train (implement-then-replace is not even needed: nothing
replaces anything). B3 is [OPT-REVEND]'s row and gates B4's G3. B4 is the one user-visible
event.

## G. Questions for Frank (discussion: problem, forces, leaning)

**Q1. The controller corrects D163's literal text.**

- *Problem:* "else return Q's search from `from`" gives a wrong answer when an atomic or
  possessive group holds a floor arm (`(?>^a|ab)c`).
- *Forces:* the ruling's own sentence "past the floor, the floor arms are dead" is the
  correct principle, and searching from `next_pos(floor)` is exactly that, at no cost.
- *Leaning:* treat it as the ruling's intent, recorded as an addendum to D163. It is
  answer-free in cost and only changes which answer is right.

**Q2. Admit before rev-end's two-seed fix (B3)?**

- *Problem:* on a trailing run before a final newline, the composite reads 3.00× today
  (§B.5). The cost is Q's own rev-end, and every rev-end artifact already pays it.
- *Forces:* gating B4 on B3 delays K106's 128M → 3 fix. Admitting first ships one shape that
  is slower than today, linear but 3×.
- *Leaning:* B3 first (it is small, it lowers K103 for every rev-end artifact, and G3 then
  lands green). If B3 slips, admit `\z`-pinned and free Qs at once and `$`-pinned Qs after B3.

**Q3. VM-bearing parts and D158.**

- *Problem:* each part entry starts its own budget. The guarantee that a composite never
  turns an answer into a give-up then rests on Q's per-start work ≤ P's for two different
  compiled programs. That holds structurally for arm deletion and is not provable for every
  engine choice. `\G(?:P)` may also cost one step more at the floor.
- *Forces:* the 20 VM-bearing candidates are corpus witnesses plus the captured wrapper and
  three idioms. No bench cell is among them.
- *Leaning:* the first build is DFA-only. Admit VM parts when the give-up differential shows
  0 composite-loses cells at lowered budgets, or when [EFFORT-BUDGET] lands. If the `\G` step
  shows in that differential, the floor part could use a one-attempt part option instead of
  the `\G` wrap.

**Q4. The route stamps say `"composite"`.**

- *Problem:* `_DFA_SCAN` and its mirrors have no single true value on a composite.
- *Forces:* a new closed-set value is a one-line bench relay. Mirroring a part's value would
  be wrong. A compound string is a second grammar.
- *Leaning:* `"composite"`, with the parts' own stamp families kept in the `.c`. A `parts`
  field in `rx_info` waits for a consumer ([V-E]/[RXINFO-REMODEL]).

**Q5. Size at the default.**

- *Problem:* a composite is roughly today plus Q's machine. Measured linked bytes: 1.15× on
  concat-sqli, 3× on trim (2 KB in absolute terms).
- *Forces:* D119 item 4 allows a `--tune` placement. `comp_fit` already drops a composite that
  breaks the caps.
- *Leaning:* default ON. The size grows only where today attempts every position, which is
  the quadratic-risk population.

**Unlocks.** Each has a trigger; no measurement lane is offered.

- **U1: re-express the VM hybrid as a composite.** Trigger: §D.1 is built.
- **U2: default-pipeline dead-path pruning** (mssurvey's 75 dead-anchor corpus patterns).
  Trigger: a bench cell whose route a dead arm decides.
- **U3: the public [EMIT-ENTRIES] request.** Trigger: [IFACE-PUSH].
- **U4: the floor-only composite generalizes `start_anchor`'s conservative 13** (mssurvey
  finding 6). Trigger: a realistic pattern in that class.
- **U5: row-name denies** (`-fdeny=composite:split`). Trigger: ≤ 4 free bits.

## H. The three standing questions (`docs/design/CLAUDE.md`)

1. **Measurement regime — RELEVANT.**
   - *Loads:* counted subject loads of a whole find-all (ASan kernel-address hooks, no clock),
     Linux dev box (7700X), gcc 15.2. The answers are box-independent counts. A different
     regime (clock, per call) could flip only the short-call cell (§E.3), which is owed as
     scratch tier at landing.
   - *Sizes:* gcc 15.2 `-O2 --gc-sections`. A different compiler moves the ratios, not the
     ordering.
   - *Oracle:* libpcre2 10.46.
2. **Independent control — RELEVANT.**
   - *Answers:* G1/G2 are checked against libpcre2 and against today's artifact under
     `-fno-match-split`. The twin built the composite from separate compiles and a
     hand-written controller, so the composite path shares no code with today's attempt loop.
   - *Cost:* G3 compares against today on the same subject (chk M5's fix).
   - *Population:* counted by ID manifests (K35), and every sabotage witness is reach-proved by
     the stamp (§E.1).
   - *Derivation:* G5 checks Q's tree against the lemma's precondition, which is a different
     source from the differential.
3. **What moves when data is regenerated — RELEVANT.** No table or calibration is involved.
   - The stamp and the value sets are an abi event at B4 (§E.4's recipe, byte-count readers
     re-derived by measurement).
   - The new corpus file moves the census pins.
   - B3 moves rev-end artifacts, as its own abi event.
   - B0-B2 move nothing (emit_sweep is the proof at each).

## I. Findings (for the manager)

1. **D163's literal controller is unsound on atomic/possessive floor arms.** `(?>^a|ab)c` on
   `"abc"` gives `(0,3)` where P and libpcre2 find no match. It is wrong on 3 of 94 twin
   cases. Q must be searched from `next_pos(floor)`, and the corrected controller is 0
   differences over 1,416,556 cells. (§B.2, Q1.)
2. **`\G` must be killed in Q.** Leaving it gave 1,344 and 1,442 wrong cells on two corpus
   patterns. The `^`/`\A` kill is a route optimization only. (§B.1.)
3. **The kill alone does not move Q's route**, because the facts are not dead-path aware. The
   derivation must prune. (§B.1.)
4. **[EMIT-ENTRIES]'s row text misreads `nentries`**, which counts `groups[]` rows, not entry
   points. (§A.2.)
5. **A composite's `_match` becomes one attempt.** Today's attempt-route `_match` filters a
   whole attempt loop. (§B.3.)
6. **The floor-only composite falls out** and covers mssurvey finding 6's start half (9
   attempt[n] single-class DFA witnesses). (§B.6.)
7. **The panel's 3× final-newline cost is confirmed by count** in the composite world (16,003
   → 48,007 loads). It is rev-end's own, hence B3. (§B.5.)
8. **Two self-contained artifacts already compile together in one TU under `-Werror`.** The
   only hazards are linkage-shaped (A.2), which is what B0 solves. (§A.2.)
