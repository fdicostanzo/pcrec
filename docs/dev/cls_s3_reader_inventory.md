# [CLS-TREE] S3 — the `A_CLASS` reader inventory

Lane `clss3inv` (sonnet, 2026-09-29), read-only against `src/`. Pin:
`lane/clss1` at `7fff7933` (S1 tip; identical to main for every reader
listed), plus `lane/ucpu2` at `61cbc894` (unmerged; `lane/ucpu3` has the same
reader set). This is S3's first act per `docs/design/cls_tree_design.md` §6
(S3 row) and §7 a2 ("`-Wswitch` forces every site to be TOUCHED, not to be
RIGHT [r1 SEM-1]", "RE-HOMED: this is S3's first act"). Nothing was built.

## 0. Headlines

1. **The design's count is right: 49 `case A_CLASS` arms and 6 `==`/`!=`
   comparisons**, in 20 files (19 with arms, plus `src/core/cpset.c` with a
   comparison). 135 lines under `src/ cli/ lib/` name `A_CLASS` in code (149
   with the four `CLAUDE.md` files). `lane/ucpu2` adds ONE more reader,
   `src/parse/ctxnode.c:50`, plus 45 `case A_CTX` arms in the same switches
   (§6).
2. **`-Wswitch` does not cover five of the 49 switches.** They carry a
   real `default:` on an `AKind` switch (coding_guide §1.3's no-default rule
   has known exceptions): `vm_det_seq`, `vm_cap_offsets`, `vm_isl_words`,
   `vm_rev_emit` (all `emit_vm.c`) and `pcrec_revdet_first`
   (`revdet.c:535`). A new kind falls into the `default:` there without a
   warning even under `make strict`. Of the five, `vm_isl_words`' `default:
   return false` is the one that MOVES ARTIFACTS if `A_WCLASS` reaches it
   unhandled (it is a wide-literal island source today, §3 row 4). And
   plain `make` only WARNS on a missing arm (`WARN = -Wall -Wextra`, no
   `-Werror`); the "forces every site to be touched" claim holds under
   `make strict` only.
3. **The existing "fail loudly" guard is NOT sufficient under `utf8`.**
   `pcrec_cls_bits` (`cpset.c:249`) refuses a node only when an interval's
   `hi > 0xFF`. A wide class whose members are all in U+0080..U+00FF
   (`é`, `[àéè]`, every Latin-1 letter, the most common non-ASCII patterns)
   is lowered under `utf8` (`lower_class_utf8` fast-paths only `hi <= 0x7F`),
   would become an `A_WCLASS`, and a reader that walks its set through
   `pcrec_cls_bits` gets a clean 32-byte bitmap of RAW BYTES 0xC0-0xFF: a
   silent miscompile, exactly r54 E1, which the existing check cannot see.
   The guard must be a KIND check, not a range check (§4).
4. **Wrapping the lowered chain in a node hides bytes from the spine
   flatteners, and that moves artifacts.** A lowered wide class is
   `A_CAT(A_EMPTY, A_ALT|chain)`. When it is the head of a left-leaning
   CAT spine, `vm_cat_flatten` (`emit_vm.c:1998`) unrolls it INTO the
   spine, so `éabc` flattens to `[EMPTY, C3, A9, a, b, c]` and
   `pcrec_lit_run` sees a 5-byte run. With an `A_WCLASS` wrapper the spine
   is `[WCLASS, a, b, c]` and the run is 3. `-Wswitch` cannot see this
   (nobody `case`s on it); the identity gate can, and only if its population
   reaches such a pattern (§7). This is a decision, not an arm (D-3).
5. **Real total S3 touch surface: 49 arms + 5 default sites + ~26 post-
   lowering spine comparisons (~8 need action) + 4 cpset helpers + the
   producer and the node definition.** Only ~14 sites carry engineering;
   the rest are one-line arms. Sizing verdict in §8.

## 1. Reproducible greps

Run at `lane/clss1` = `7fff7933`. `SRC="src cli lib"`.

```
# all mentions (code): 135; with docs: 149
grep -rn "A_CLASS" $SRC --include=*.c --include=*.h | wc -l
grep -rn "A_CLASS" $SRC | wc -l

# the 49 arms and the 6 comparisons
grep -rn "case A_CLASS" $SRC | wc -l                               # 49
grep -rnE "[!=]= *A_CLASS|A_CLASS *[!=]=" $SRC | wc -l             # 6

# every AKind switch (49, ALL of which name A_CLASS) and which carry a real
# default:  (script kept in the lane scratchpad; brace-matched, depth-1
# `default:` only, comments do not count)
python3 sw.py   # -> 49 switches, 49 with A_CLASS, 5 with a real default:

# the interval payload, read directly
grep -rnE "u\.cls\.|->cls\b" $SRC --include=*.c --include=*.h
# the renderers / single-byte / membership helpers and their callers
grep -rn "pcrec_cls_bits\b\|pcrec_cls_bits_widen\|pcrec_cls_single\|pcrec_cls_has\|pcrec_lit_run" $SRC --include=*.c --include=*.h

# comparisons on the lowered form's own kinds (spine loops)
grep -rnE "k *[!=]= *A_(CAT|ALT|EMPTY)" src --include=*.c --include=*.h   # 76

# unmerged lane
git grep -nE "case A_CLASS|[!=]= *A_CLASS|A_CLASS *[!=]=|u\.cls\.|pcrec_cls_bits" lane/ucpu2 -- src cli lib
git grep -n "case A_CTX" lane/ucpu2 -- src | wc -l                 # 45
```

Pipeline order that decides every disposition (`src/core/compile.c`):
parse (+ modules) -> `pcrec_altcls` :1397 -> `pcrec_discharge_atomic` :1413
-> `pcrec_callgraph_build` :1432 -> `pcrec_facts_seal_e1` :1442 ->
`pcrec_select_engine` :1469 (possessify, revdet, ...) ->
`pcrec_postresolve` :1480 -> **`pcrec_lower_enc` :1533** ->
`pcrec_facts_seal_e2` :1549 -> `pcrec_build_nfa`/DFA -> `pcrec_emit_vm` /
`pcrec_emit_dfa`. **`A_WCLASS` can exist only after :1533**, so a reader
that runs strictly above it can never see one (phase P0/P1 below); readers at
or below it (P3) can. `u.rep.revbody` is a detached reversed copy built
above the lowering; `lower_walk` clears it unless it is lowering-identity, so
no wide class survives inside one.

## 2. Codes used in the tables

Phase: **P0** parse/modules, **P1** above the lowering, **P2** the lowering,
**P3** below it (facts E2, NFA/DFA, VM emitter).

Disposition:
- **W** — walk the byte child. Answer must equal today's (byte-identity).
- **L** — leaf-equivalent: structural only, and the answer is provably
  invariant over the child's kinds (`A_CAT/A_ALT/A_EMPTY/A_CLASS`), so
  joining the leaf group is byte-identical. Silent by nature; the proof is
  the review, the gate is the identity sweep.
- **U** — unreachable by phase (P1) or by construction (revbody). Should fail
  loudly, not silently join a group (D-1).
- **P** — the producer.
- **D** — open design decision (numbered, §5).

## 3. The 49 arms

| # | file:line | function | ph | reads the class FOR | S3 disposition | what makes a wrong walk fail |
|---|---|---|---|---|---|---|
| 1 | `core/internal.h:4295` | `pcrec_ast_visit` | P0,P1,P3 | generic pre-order; callbacks look for calls/caps/`\G`/`${}`/pending widths | **L**. Callers: callgraph 14, postresolve 2, mod_vars 1 (all P0/P1, never see one), endwin 1 (P3, looks for `\G`). Child cannot hold any of them | nothing (leaf-group arm); `-Wswitch` only forces the arm |
| 2 | `facts/endwin.c:121` | `ew_walk` | P3 | end-anchor fact: class "consumes a byte" -> `EW_NONE` | **L**: child `CAT`/`ALT` of classes folds to `EW_NONE` by its own arms | nothing |
| 3 | `facts/req.c:408` | `rb_walk` | P3 | necessary byte set + run (`pcrec_cls_single`) | **W**, and it is the live case: under `utf8` the child's leading bytes ARE the answer (`RX_REQ_RUN "ceb1@1"`, S302's reach line). Walking the set would report the empty/multi-member class = no byte, silently dropping a stamp | a moved `RX_REQ_RUN`/`REQ_BYTE` stamp: caught by the identity gate (§7), not by an assertion |
| 4 | `facts/startanch.c:117` | `sa_walk` | P3 | start-anchor fact: "consumes a byte" -> nothing | **L** | nothing |
| 5 | `gen/emit_vm.c:1579` | `vm_det_seq` | P3 | reverse-deterministic body -> per-leaf bitmap via `pcrec_cls_bits` | **U**. **`default:` site** (`-Wswitch` silent). Runs only on a revdet-approved body, which `lower_walk` guarantees is lowering-identity, so no `A_WCLASS`. Today an unhandled kind falls to `default:` = decline (safe). Add an explicit `case A_WCLASS: return 0;` | `pcrec_cls_bits` on it: loud only if the kind guard of §4 exists |
| 6 | `gen/emit_vm.c:1648` | `vm_cap_offsets` | P3 | stride offsets for the same body (`base + 1` per class) | **U**, **`default:` site**; explicit `return -1` | as 5 |
| 7 | `gen/emit_vm.c:1784` | `vm_rev_caps` | P3 | dense capture index of a revdet body; class contributes none | **L** | nothing |
| 8 | `gen/emit_vm.c:2623` | `vm_cost` | P3 | D51 analysis cost: `A_CLASS` = zero cost | **W**. Today the lowered chain's `CAT`/`ALT` nodes are costed; an `L`-style zero would under-charge and desync from `vm_emit` ("every arm's emission must match `vm_cost`'s charge", header). D-4 | cost/emit desync shows as a moved refusal set or moved artifact |
| 9 | `gen/emit_vm.c:2876` | `vm_count_slots` | P3 | resume-point / slot count, "site for site" with `vm_emit` | **W**: the child's `ALT` allocates choice slots. `L` here silently under-counts frames | a moved `RX_*` slot stamp / a `FRAMES` give-up: identity gate only |
| 10 | `gen/emit_vm.c:3626` | `vm_isl_words` | P3 | island source words (`vm_isl_single` -> `pcrec_cls_single`) | **W**. **`default:` site**: an unhandled `A_WCLASS` hits `default: return false` and the wide-literal island vanishes, silently, artifact moved. Must be an explicit arm | none (silent artifact move) |
| 11 | `gen/emit_vm.c:4957` | `vm_rev_emit` | P3 | backward walk of a revdet body (`pcrec_cls_bits`) | **U**; its `default:` is a hard compile error already (loud) | the `default:` internal error; keep it |
| 12 | `gen/emit_vm.c:6950` | `vm_walk_caps` | P3 | collects capture nodes; class has none | **L** | nothing |
| 13 | `gen/emit_vm.c:7034` | `vm_walk_calls` | P3 | collects call nodes; class has none | **L** | nothing |
| 14 | `gen/emit_vm.c:8313` | `vm_emit` | P3 | the forward emission: `pcrec_cls_bits` -> `vm_cls` (the r54 E1 site) | **W**: `case A_WCLASS:` emits the child. `vm_charge(v)` is the first statement of `vm_emit`, so recursing into the child charges one node more than `vm_cost` counted. D-4. **Must not** be added to the `A_CLASS` arm's label list (that compiles, and renders the raw-byte bitmap: headline 3) | the kind guard of §4 makes the mistake loud; today nothing does |
| 15 | `ir/nfa.c:587` | `compile_ast` | P3 | one `N_CLASS` state via `pcrec_cls_bits` | **W**: `return compile_ast(b, a->l)` (after `ast_bare`). D-3 for the spine | as 14 |
| 16 | `opt/altcls.c:400` | `altcls_walk` | P1 | rewrite walker; leaf group | **L** (never reached) | nothing |
| 17-26 | `opt/atomic.c:65,155,229,295,433,587,656,813,925,960` | `pcrec_has_atomic`, `_lookaround`, `_collapsible_rep`, `pcrec_ast_stamped_by`, `dis_walk`, `pcrec_has_bref`, `pcrec_bref_mark`, `pcrec_has_live_capture`, `_linked_call`, `pcrec_has_call` | P1 (`pcrec_bref_mark` also P3: `emit_vm.c` calls it) | structural predicates: does the subtree contain construct X | **L** all ten (the child holds none of them). `pcrec_bref_mark` is the one reachable at P3, so its arm must be a real arm, not a "will never happen" | nothing. Also update `patfacts/design.md` §3's invariance proof: the lowering now allocates a FIFTH kind, and `pcrec_pattern_kinds` (E1) is re-derived on the lowered tree at the E2 seal (S302's cross-check). Every predicate above answers false on it, so the mask holds, but the proof text names four kinds |
| 27 | `opt/lower_enc.c:460` | `subtree_is_identity` | P1/P2 | walks a DETACHED `revbody` asking "does the lowering leave this alone" (`u.cls.iv[i].hi > identity_max`) | **U**: input is un-lowered by definition | none; internal error recommended |
| 28 | `opt/lower_enc.c:502` | `lower_walk` | P2 | **THE PRODUCER**: `Ast *repl = lc->ops->lower_class(lc, a); if (repl) *slot = repl;` | **P**: `repl` becomes `A_WCLASS{set = a's payload, child = today's chain}` when `lower_class` is non-NULL. The group-root address signature (`cap_sig`) stays valid: the replaced node is still a leaf. The empty-set case (`bl.n == 0`, "class matches nothing") returns a byte-confined empty `A_CLASS` today and must stay one | the R2 splice assertion + `cap_sig` |
| 29 | `opt/lower_enc.c:578` | `cap_sig` | P2 | counts `A_CAP` addresses | **L** | S-row for the address signature |
| 30 | `opt/mrl.c:155` | `pcrec_minw` | P3 (6 calls in `emit_vm.c`), P1 | min BYTES | **W**. Today's post-lowering answer is the chain's, not 1 (a two-byte char is 2) | S58 (`minw_underreports`) anchors here; re-verify the anchor |
| 31 | `opt/mrl.c:317` | `pcrec_nullable` | P3 (5 in `emit_vm.c`, 1 in `facts/widths.c`) | nullability | **W** (chain of classes: false; an `L` `false` is equal, `W` is uniform) | S58-class |
| 32 | `opt/mrl.c:518` | `pcrec_cwmax` | P1 (`callgraph`, `mod_lookaround`), P3 (`endwin`, `startanch`, `axes_dump`) | max width in CHARACTERS: "`A_CLASS` IS EXACTLY 1 IN EVERY ENCODING" (header :496) | **W** for byte-identity, **D-2**: today post-lowering it returns the chain's byte width; the documented meaning is 1. Which one `A_WCLASS` answers is a ruling, not an arm | S-U8 (`mrl_bound_loosened_utf8`), S-U4 (`width_rule_byte_units`) anchor on this area |
| 33 | `opt/mrl.c:658` | `pcrec_cwmin` | as 32 | min width in characters | **W** / D-2 | as 32 |
| 34 | `opt/possessify.c:178` | `first_of` | P1 | FIRST set via `pcrec_cls_bits_widen` (out-of-range -> all bytes) | **U** | none |
| 35 | `opt/possessify.c:564` | `gk_build` | P1 | Glushkov position label (`cls_bits_widen`) | **U** | none |
| 36 | `opt/possessify.c:894` | `pss_walk` | P1 | hunts `A_REP` nodes; leaf group | **L** | nothing |
| 37 | `opt/revdet.c:102` | `rd_shape` | P1 | body-shape scan; class is fine | **L** | nothing |
| 38 | `opt/revdet.c:299` | `rd_reverse` | P1 | copies the node (reversal of a class is the identity); the D70 clobber site (S121) | **U** | S121's kind guard |
| 39 | `opt/revdet.c:485` | `pcrec_revdet_first` | P1, P3 (`emit_vm.c:5056`, revdet bodies only) | first-byte set via `cls_bits_widen`. **`default:` site** (widening: sound) | **U**; the `default:` already widens, add the explicit arm | none |
| 40 | `opt/revdet.c:585` | `rd_alt_disjoint` | P1 | leaf = disjoint | **L** | nothing |
| 41 | `opt/revdet.c:712` | `rd_walk` | P1 | hunts `A_REP`; leaf group | **L** | nothing |
| 42 | `opt/select_engine.c:241` | `first_dfa_excluding` | P1 | first row excluding the DFA; leaf group | **L** | nothing |
| 43 | `parse/definitions.c:200` | `pcrec_ast_is_core` | P0 | "core vocabulary" test on a definition's expansion | **L**: add `A_WCLASS` to the core list; a definition tree is never lowered | none |
| 44 | `parse/mod_backrefs.c:610` | `br_strip_caps` | P0 | rewrite; leaf group | **L** | nothing |
| 45 | `parse/mod_lookaround.c:192` | `la_has_kreset` | P0 | leaf -> false | **L** | nothing |
| 46 | `parse/mod_vars.c:225` | `vars_assign` | P0 | leaf group | **L** | nothing |
| 47 | `parse/parse.c:138` | `pcrec_is_bare_anchor` | P0 | class is not an anchor | **L** | nothing |
| 48 | `parse/rxt_compose.c:289` | `rc_remap_caps` | P0 | composition rewrite | **L** | nothing |
| 49 | `parse/rxt_compose.c:446` | `rc_find_root_call` | P0 | composition search | **L** | nothing |

Tally: **W = 10** (#3, 8, 9, 10, 14, 15, 30, 31, 32, 33), **P = 1** (#28),
**U = 8** (#5, 6, 11, 27, 34, 35, 38, 39), **L = 30**. No arm "walks the set
legitimately": every legitimate set reader is strictly above the lowering
and never sees an `A_WCLASS` (they are the `pcrec_cls_bits_widen` callers,
the class merges in `parse.c`, `altcls.c`, and the lowering itself, §3.2).
Decisions: D-1..D-4 attach to specific rows above; D-5..D-8 in §5.

### 3.1 The 6 comparisons

| file:line | function | reads FOR | disposition |
|---|---|---|---|
| `core/cpset.c:319` | `lit_byte` (inside `pcrec_lit_run`) | one-byte literal test for the run | **L**: a wide class is not a literal byte. But the run's ADJACENCY across a wrapper is D-3 |
| `ir/nfa.c:556` | `trie_key` | trie eligibility: every spine leaf must be `A_CLASS` | **L**: today the leaf is a lowered `A_CAT`, ineligible; an `A_WCLASS` leaf is ineligible too. Same answer; `run_trie_identity.sh` is the witness |
| `opt/altcls.c:184` | `altcls_branch_peel` | first atom is a bare `A_CLASS` | **L**, P1 |
| `opt/altcls.c:340`, `:342` | `altcls_walk_alt` | run of adjacent bare classes to merge | **L**, P1 |
| `gen/emit_vm.c:3548` | `vm_isl_single` | single-byte literal for the island | **L**: `A_WCLASS` -> -1 is correct; the island's wide words come through row 10 |

### 3.2 Direct readers of the interval payload (`u.cls.iv` / `u.cls.n`)

| file:line | function | phase | reads FOR | disposition |
|---|---|---|---|---|
| `core/cpset.c:229-230` | `pcrec_cpset_publish` | P0 | the producer of the payload | unchanged; the `A_WCLASS` payload would be published by the same builder in `lower_walk`'s producer arm |
| `core/cpset.c:252-256` | `pcrec_cls_bits` | P3 | **the ONLY byte-bitmap render for the byte tier**; loud on `hi > 0xFF` | needs the kind guard (§4). Callers, all P3: `nfa.c:566`, `:596`; `emit_vm.c:1581`, `:4965`, `:8319` |
| `core/cpset.c:289-293` | `pcrec_cls_bits_widen` | P1 | the sound-direction render (out of range -> all 0xFF) | P1 only (`revdet.c:493`, `possessify.c:188`, `:572`); kind guard so a P3 misuse is loud |
| `core/cpset.c:307-310` | `pcrec_cls_single` | P1,P3 | "exactly one code point that is a byte" | callers `emit_vm.c:3557`, `altcls.c:190`, `facts/req.c:409`, `cpset.c:319`; guard on kind |
| `core/cpset.c:367-369` | `pcrec_cls_has` | — | membership on the node's own list | **NO CALLERS** (`grep -rn pcrec_cls_has`). A dead set-reader, exactly the shape S3 wants gone: delete or kind-guard |
| `parse/parse.c:1332`, `:1370-1371` | `p_class` (module-claim merge) | P0 | ORs a produced set into the class being built | legitimate set reader, P0 |
| `opt/altcls.c:351` | `altcls_walk_alt` | P1 | merges adjacent bare classes (`pcrec_cpset_add_set`) | legitimate, P1 |
| `opt/lower_enc.c:160-165, 312-326, 461-462` | `lower_class_byte`, `lower_class_utf8`, `subtree_is_identity` | P2 | the lowering's own read of the set | legitimate: this is what builds the child |
| `parse/ctxnode.c:50-51` (**`lane/ucpu2` only**) | `lang_charset` | P0 | accumulates a lookaround body's class into `A_CTX`'s set | legitimate, P0; never sees `A_WCLASS` |

## 4. How a wrong walk fails today, and what S3 must add

The design demands a reader that walks the SET instead of the child fail
loudly. Site by site, what enforces it now:

| wrong walk | enforced by | verdict |
|---|---|---|
| a P3 reader calls `pcrec_cls_bits` on the node | the `hi > 0xFF` `pcrec_ctx_fail` | **ENFORCED only for sets containing a code point above U+00FF.** Sets confined to U+0080-U+00FF (`é`, `[àéè]`) render as a valid byte bitmap. Silent miscompile under `utf8`. Needs `a->k == A_WCLASS` -> `pcrec_ctx_fail` in `pcrec_cls_bits`, `_widen`, `_single`, `_has` |
| a reader adds `case A_WCLASS:` to the `A_CLASS` arm's label list | nothing; it compiles and is the SEM-1 hazard | fixed only by the kind guard above (the shared arm calls `pcrec_cls_bits`, which then refuses) |
| a reader reads `a->u.cls.iv/n` directly on an `A_WCLASS` | nothing. If the set lives in `u.cls` it is read successfully; if it lives in a NEW union member, `u.cls` is the arena zero = `{NULL,0}` = the EMPTY class, which reads as "matches nothing": silent and worse | put the set in a distinct member (`u.wcls`, D70's rule: a new kind adds a union member) so the only spelling that reaches it is a kind-checked accessor, and make the accessor the guard |
| a reader groups `A_WCLASS` with the leaf arms and the child mattered (#3, 8, 9, 10, 30-33) | nothing | the identity gate (§7); the reviewer of the 10 W rows |
| an unhandled kind in the 5 `default:` switches (#5, 6, 10, 11, 39) | `-Wswitch` is silent by construction | replace the `default:` with the full enumeration (coding_guide §1.3), or add the explicit arm as in the table; #10 is the one that silently moves artifacts; #11's `default:` is already loud |
| the 6 comparisons | nothing (`k != A_CLASS` reads "not a class", which is the right answer for a wide class) | none needed |
| the ~26 post-lowering spine comparisons (`k == A_CAT/A_ALT` in `emit_vm.c`, `nfa.c`, `req.c`, `mrl.c`) | nothing | D-3 |

Recommended enforcement beyond the guard: (a) a **structural census check**
(K35 shape, `run_cpset_structure.sh`'s neighbourhood) asserting that the
number of `case A_WCLASS` labels equals the number of `AKind` switches
(49 + 45 `A_CTX` if ucpu2 is in) and that no `case A_WCLASS:` shares a label
list with `case A_CLASS:`; (b) two sabotage rows numbered from main's highest
S-id at the time: a plant that ORs `A_WCLASS` into the `A_CLASS` arm of
`vm_emit` (must go DETECTED on a Latin-1-range witness such as `[é]`, NOT
only `\p{L}`, otherwise the row scores the wrong direction) and a plant that
restores `vm_isl_words`' silent `default`.

## 5. Open design decisions for the manager

- **D-1 Unreachable-arm policy.** 8 U rows and the P0/P1 L rows. Silent
  (join the leaf group) or `pcrec_ctx_fail("internal error: A_WCLASS above
  the lowering")`? Recommend loud for the eight U rows (they read the set's
  content) and silent for structural walkers, so a later stage that
  produces `A_WCLASS` earlier (S4's decode may) is caught where it matters.
- **D-2 `pcrec_cwmax`/`cwmin` on `A_WCLASS`.** Byte-identity forces the
  chain's byte width; the documented meaning (`mrl.c:496`) is "one
  character". The two differ for every wide class. S3 keeps the chain's
  answer; the meaning is the S4 ruling.
- **D-3 Spine transparency.** `vm_cat_flatten` (`emit_vm.c:1998`), the spine
  loops in `compile_ast` (`nfa.c:696-722`), `rb_walk`'s CAT arm and
  `pcrec_nullable`/`minw`'s iterative CAT walks all unroll a lowered class
  at a spine HEAD. Either (a) each flattener sees through `A_WCLASS` (one
  helper, `ast_bare`'s precedent: the D31 group erasure is already a see-through helper, 12 uses in `src/`),
  or (b) the wrapper is not produced at a spine head (no: that reintroduces
  a position conditional). Recommend (a), and the artifact-changing case
  (`éabc`'s lit run, `vm_cat`'s label numbering: "each element's `next`
  label is taken just before it is emitted") is the identity gate's first
  witness.
- **D-4 `vm_charge` / `vm_cost` accounting for the wrapper.** One extra
  `vm_emit` entry per wrapper unless the `A_WCLASS` arm calls the child's
  emitter without re-charging, or `vm_cost` counts the wrapper. Must be
  chosen so cost == charge holds (the header's own invariant).
- **D-5 Payload layout.** Recommend distinct `u.wcls = { set iv/n }` with the
  child in `l`, accessed only through kind-checked accessors (§4).
- **D-6 The five `default:` sites.** Convert to full enumeration (recommended;
  it is the coding guide's own rule and makes `-Wswitch` cover them).
- **D-7 Merge order against `lane/ucpu2`.** ucpu2 adds `A_CTX`, a SECOND
  node carrying an interval list (`u.ctx.iv/n`, read at `emit_vm.c:7926` and
  `nfa.c:632` through `pcrec_enc_set_bytes`, gated by a byte-expressibility
  conjunct until U3/U4), 45 `case A_CTX` arms in the very switches S3 edits,
  and the `ctxnode.c:50` reader. Both lanes edit the same label lines, so
  whichever merges second resolves ~45 textual conflicts. Recommend S3 lands
  AFTER ucpu2 (one rebase, and `A_CTX`'s wide sets are the same
  guard-the-set question for S4). Ask: is ucpu2's merge imminent?
- **D-8 Identity gate.** §7: there is no committed instrument for the
  triple sweep.

## 6. Readers that exist only on `lane/ucpu2`

Only one: **`src/parse/ctxnode.c:50-51`** `lang_charset`, P0, a legitimate set
reader (`pcrec_cpset_add_set(acc, a->u.cls.iv, a->u.cls.n)`), never sees an
`A_WCLASS`. Also new there, not `A_CLASS` readers but S3-relevant: 45
`case A_CTX` arms in the same switches, `u.ctx.iv/n` producers/readers
(`parse.c:68-70`, `emit_vm.c:7926`, `nfa.c:632`), and an updated
`internal.h` comment mentioning `A_CLASS`. `lane/ucpu3` = ucpu2's reader set
(diffed). The `case A_CLASS` count on ucpu2 is 50 arms (49 + `ctxnode.c`).

## 7. Byte-identity method S3 must use, and where it lives today

The method (utf8k53 report §3.2, `docs/dev/lanes/utf8k53_report.md:244`;
`known_issues.md:5586`): every distinct `(pattern, encoding, features)` triple
in the corpus, compiled by a compiler built from the branch point and by the
lane's, hashed and compared; 3,348/3,348 identical, 0 stopped compiling, 0
started; **same `-o` basename in different directories** (the `-o`-basename
trap, fourth recorded instance); reference built from `git archive REF`, never
from a checked-in `build/`.

**The driver was never committed.** The K53 report describes it; no script in
the tree is it. The nearest committed instruments and their gaps for S3:

| instrument | has | lacks for S3 |
|---|---|---|
| `scripts/emit_sweep.py` (BSWEEP) | self-check, pinned reach floors, five streams, `--features all` | **no encoding axis at all** (streams are `-p rx --features all`, default `byte`). Under `byte` an `A_WCLASS` is never produced, so today's sweep is vacuous for S3 |
| `docs/dev/optloop/s1/s1_identity.py` | per-commit gate, bench + corpus, `EXTRA` deny flags | no `-e utf8` config |
| `docs/dev/dialtrain_byteid_evidence/byteid_sweep.py` | corpus sweep | default flags only |

So S3's gate is a small NEW piece: `emit_sweep.py`'s reference-build +
same-basename + `--list-source` population, with the `(encoding, features)`
read from each block (the K53 triples) plus a `-e utf8` pass over the
bench population (the `utf8@0.1` subbench) and over `tests/utf8/`. **REACH
control (K35/MECH-REACH):** the pass count is not evidence, because under
`byte` and for ASCII-only `utf8` patterns nothing is lowered. The gate must
report the number of triples in which `lower_class_utf8` returned non-NULL
(a scratch counter in the sweep's compiler build, not landed) and fail below
a floor; the artifact-moving witnesses to name explicitly are `éabc` (D-3),
a wide-literal alternation island (`é|x`, row 10), a `utf8` pattern with a
counted repeat of a Latin-1 class, and `\p{L}`-class captures under
`--engine=vm`. Plus a POSITIVE control: a deliberately wrong `A_WCLASS`
arm (row 10 falling to `default`) must make the gate report movers.
Answer-level suites (`tests/utf8/`, `test-uprops` [STORE], PC-4) ride
`make test` as usual.

## 8. Sizing verdict for the S3 build

**One opus lane, medium size, three commit groups; NOT a sonnet lane** (engine
code, D-1..D-4 rulings needed first).

- Surface: 49 arms in 19 files, 5 `default:` sites, ~8 spine helpers, 4 cpset
  helpers, the node + `u.wcls` in `internal.h`, `lower_walk`'s producer arm,
  `pcrec_ast_is_core`, `patfacts/design.md` §3 text, per-directory
  `CLAUDE.md`s. About 60-70 edit sites, but ~50 are one-line arms; the
  engineering is ~14 (rows 3, 8, 9, 10, 14, 15, 30-33 plus the spine helpers
  and the guards).
- Mech anchors to re-verify (text-anchored rows near these sites): S58,
  S-U8, S-U4, S66, S121, S166, S302, S305 (`tests/mech/sabotages/`), and any
  `SAB_REACH` witness that greps emitted lit-run/req stamps.
- Suggested commit order, each zero-mover by construction of the gate:
  (c1) node + guards + every arm, `A_WCLASS` NEVER PRODUCED (all arms
  compile clean under `make strict`; trivially zero movers; proves the arm
  set is total); (c2) producer switched on with the identity gate; (c3) census
  check + two sabotage rows + docs. Heavy validation (`make test`,
  `test-codegen`, the triple sweep, a `make san` pass for the new
  allocations) is a detached OWED chain per BOILERPLATE.
- No abi event, no `docs/spec/` hunk (nothing caller-observable) — provided
  D-4's charge accounting does not move a refusal set; the sweep's
  refusal-set comparison is what proves it.
- Risk ranking: D-3 (artifact moves in ordinary patterns), row 10 (silent
  island loss), the Latin-1-range hole (§0.3). Everything else is arm
  bookkeeping.

## 9. Questions for the manager

1. D-1..D-8 above; the ones that gate a build are D-3, D-4, D-5 and D-7.
2. Confirm `cwmax` stays the chain's byte answer at S3 (D-2).
3. Should the missing triple-sweep driver be its own small lane first (a
   committed `(encoding, features)` sweep would serve S3, S4 and every
   later encoding-touching change)? Recommend yes, and fold it into c1's
   acceptance.

## 10. Manager rulings (2026-09-29, eighty-sixth session)

All eight recommendations ADOPTED as written:
- D-1: loud (`pcrec_ctx_fail`) for the 8 set-reading U rows; silent for structural walkers.
- D-2: S3 keeps the chain's byte answer for `cwmax`/`cwmin`; the one-character meaning is S4's question.
- D-3 (a): one see-through helper, following the `ast_bare` precedent. Every spine flattener uses it. `éabc`'s lit run is the identity gate's first witness.
- D-4: the wrapper arm emits the child without re-charging, and `vm_cost` agrees. cost == charge stays the invariant, and the identity gate proves it.
- D-5: distinct `u.wcls`, child in `l`, kind-checked accessors. `pcrec_cls_has` (no callers) is deleted.
- D-6: the five `default:` switches become full enumerations.
- D-7: S3 builds AFTER both lane/ucpu2 (U2) and lane/clss1 (S1) merge to main.
- D-8: the (encoding, features) triple-sweep identity instrument is its OWN small lane FIRST (lane clsid). It is committed with a REACH counter and a positive control, and its baseline is recorded on main before S3 starts.

## 11. Build-time corrections (lane s3build, 2026-09-29)

The S3 build measured two rows of §3 wrong. Both are in the lane report
(`docs/dev/lanes/s3build_report.md` §2) with their witnesses; this section
exists so a later reader of the table is not misled by it.

- **Rows 5 and 6 (`vm_det_seq`, `vm_cap_offsets`) are W, not U.** They run
  for the CURSOR rung on ANY quantifier body (`vm_cursor_fits`), not only on
  a revdet-approved one, so a lowered wide class reaches them: `(é)+` under
  `-e utf8` is a two-byte deterministic stride today. The D-1 loud arm would
  have REFUSED that pattern; a decline would have moved its artifact off the
  cursor rung (measured: `(é)+`, `é{3}`, `(?:é)+x`, `x(?:é)*y` all move).
  Both walk the child; `run_wclass_census.sh` W2 is the witness.
- **§4's "u.cls is the arena zero" does not hold for a union.** Every member
  of `Ast.u` starts at offset 0, so `u.wcls` and `u.cls` alias and a `u.cls`
  read on an `A_WCLASS` returns its set, not the empty class. What makes a
  set-reading mistake loud is the KIND guard in the three readers, not the
  member's distinctness; the distinct member buys that no `u.cls.` grep or
  review names the wide set by accident.

The other U rows (11, 27, 34, 35, 38, 39) held: each runs above the lowering
or over a revdet body the lowering keeps byte-level, and each now refuses the
kind by `pcrec_wcls_misplaced`.
