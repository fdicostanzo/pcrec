# pf35 — [PATFACTS] step 3.5, "node nullable (R4)" (lane report)

Lane pf35, 2026-09-27, opus. Branch `lane/pf35` off main `65482b45` (abi 41,
PATFACTS 3.0-3.4 merged). Charter: `docs/design/patfacts/design.md` §9's 3.5
row, §4.3 (node grain: one definition, a pure function, no memo), §9.1
(classifying a mover); `docs/design/patfacts/inventory.md` R4 and its Delta.
**Not merged.**

## 1. Every node-nullability spelling, found by grep, before any edit

Commands (tree at `65482b45`):

    grep -rn "nullable\|can.*match.*empty\|match.*the empty" src
    grep -rnE "(minw|cwmin)\([^)]*\) *(==|<=|<) *[01]\b|(minw|cwmin)\([^)]*\) *> *0" src
    grep -rnE "static bool [a-z_]*(null|empty|zero|zw|eps)[a-z_]*\(" src
    grep -rn "pcrec_minw(" src
    grep -rn "vm_nullable" src tests scripts tools docs/spec

Each hit was classified by reading it. "Node grain" = answers for any subtree;
"pattern grain" = one answer per compile.

| # | spelling | site | grain | the question it answers | verdict |
|---|---|---|---|---|---|
| 1 | `vm_nullable(a)` | `src/gen/emit_vm.c:1290` (`static`) | node | can this subtree's language contain the empty string? Exhaustive per-kind switch; `A_CALL` arm reads `!a->u.call.nonnullable` | **THE one function** (design §9 3.5). Readers: `:1426/:1433` (itself), `:1487` `vm_lifts`, `:2237/:2412` `vm_cost`, `:2995` `vm_count_slots`, `:5013`, `:6060` the empty-iteration guard, `:7273` the call-target fixpoint |
| 2 | `pcrec_minw(root) == 0` | `src/facts/widths.c:40` `pcrec_pattern_nullable` | node primitive composed at the root → pattern-grain E1 fact | the same question, answered through the byte-width recurrence; `A_CALL` arm reads `u.call.minw` | **R4's duplicate** — the only code spelling of node nullability other than #1. Readers: the E1 seal (`facts.c:194`), the E2 re-derivation cross-check (`facts.c:262`), hence `pcrec_fact_nullable` (`select_engine.c:837`, `compile.c:1632`, `pcrec_startgate_needed` → `nfa.c:1150/1153`, `emit_dfa.c:7978`). Migration target: compose #1 at the root. **Blocked — §2** |
| 3 | `pcrec_minw(a)` | `src/opt/mrl.c:120` | node | the least number of bytes a match consumes | a WIDTH, not a nullability spelling; stays (design §4.2.1 row `widths.c`). Its `> 0` tests in `emit_vm.c:5709/:5743` skip a zero term of the MRL sum (width arithmetic), not a nullability question |
| 4 | `First.nullable` (`first_of`) and `GkParts.nullable` (`gk_parts`) | `src/opt/possessify.c:144-453`, `:508-711` | node | a component of the FIRST / Glushkov first-last algebra: "may the NEXT item's first byte be seen here" | a DIFFERENT question with deliberately different arms: `A_BOL`, conditional `A_EOL`, `A_GSTART`, `\b`/`\B` are modelled NON-nullable with a first set; lookaround/backreference/call are "0xff plus nullable". Joint with the set computation; not a duplicate. Stays |
| 5 | `cstart_check_omission` | `src/ir/nfa.c:1086` | NFA (machine) | does the built machine accept without consuming? | a documented deliberate INDEPENDENT cross-check of #2 over the NFA (inventory R4 last sentence). Stays |
| 6 | "always zero-width" | `src/facts/startanch.c:82`, `src/facts/endwin.c:91` | node | may this subtree consume nothing on EVERY path (`cwmax == 0`) | a different question; both comments say `minw == 0` would be wrong there. Stays |
| 7 | `Ast.u.call.nonnullable` + `vm_resolve_nonnull` | `src/core/internal.h:1464`, `src/gen/emit_vm.c:7263` | per call target | #1's `A_CALL` arm, as a fixpoint over the call graph | not a second predicate — its recurrence IS #1. Runs inside `pcrec_emit_vm` only. Stays (§2 says why it matters) |
| 8 | `Ast.u.call.minw` fixpoint | `src/opt/callgraph.c:820-840` | per call target | #3's `A_CALL` arm | not a nullability spelling. Stays |
| 9 | `dfa_engine_is_empty`, `q_open_is_empty` | `src/gen/emit_dfa.c:3807`, `src/parse/parse.c:260` | — | "is this the empty ENGINE", "is the quantifier's operand empty SYNTAX" | different questions |
| 10 | `lang_nullable_declinable`, the `pfc_wanted` conjunct | `src/opt/select_engine.c:836`, `src/core/compile.c:1632` | pattern | consumers of the E1 accessor | readers, not spellings |
| 11 | `la_widths` | `src/parse/mod_lookaround.c` | node | lookbehind character widths (`cwmin`/`cwmax`) | not nullability |

So R4 is exactly two definitions: #1 (node grain, the emitter's) and #2 (the
same question through `pcrec_minw`, applied at the root by the E1 fact).
Everything else nullable-shaped is either a different question (#4, #6, #9,
#11), a machine-level cross-check (#5), a fixpoint that feeds one of the two
(#7, #8) or a reader (#10).

## 2. The pre-edit finding: the two copies DISAGREE on `A_CALL`, today

For every kind but `A_CALL` the two switches are equivalent: `pcrec_minw`'s
sum/min/`rmin *` arithmetic is 0 exactly where `vm_nullable`'s
and/or/`rmin == 0` logic answers true (saturation only ever holds a positive
value at `PCREC_MINW_MAX`). `A_CALL` is the arm the design calls deliberate,
and reading it against its fixpoints finds that the difference is not only
polarity. **Two mechanisms, either one a SEMANTIC mover under §9.1:**

**(M1) The fixpoints are LEAST vs GREATEST.** `u.call.minw` is iterated from
infinity DOWNWARD (`callgraph.c`), i.e. the least fixpoint of the language:
exact. `u.call.nonnullable` is iterated from `false` = "nullable" and only
ever flips to "non-nullable" (`vm_resolve_nonnull`, `emit_vm.c:7263-7285`),
i.e. the GREATEST fixpoint of nullability: an over-approximation on any cycle
whose only escape runs through the call. (The function's header says the
opposite — "nullability's least fixpoint over a cycle is 'not nullable'" —
but the code's `nn[i] = false; /* == "nullable", the bottom */` starts at the
top.) Witness, measured on `pcrec_base` (= main `65482b45`):

| pattern | `--emit-facts` E1 `nullable` (#2) | emitter's answer (#1): `RX_SLOT_EMPTY_GUARD*` slots | control |
|---|---|---|---|
| `(a\|(?1))` | `no` | — | — |
| `(a\|(?1))*` | — | **1** (body judged nullable) | `(a(?1)?)*` 0, `(a\|b(?1))*` 0 |
| `((?1)\|a)*` | — | **1** | |

Group 1's language is `{a}`: PCRE2 10.48 (local, light probe) matches `a`
on `^(a|(?1))$` and fails `b` with error -52 "nested recursion at the same
subject position" — it never matches empty. So #2 is exact and #1
over-approximates (the safe direction for the guard: one slot and one test,
never an answer).

**(M2) The fixpoints run at different TIMES.** `u.call.minw` is published by
`pcrec_callgraph_build`, before the E1 seal (`compile.c`), which is what
`widths.c`'s header relies on. `u.call.nonnullable` is published only inside
`pcrec_emit_vm`, so at the E1 seal every `A_CALL` reads the arena zero,
"nullable". Composing #1 at the root at the seal would therefore flip E1 on
every pattern whose non-nullability comes through a call — `(a)?(?1)`
(E1 `no` today) would read `yes` — independently of M1.

**Consequence: migrating #2 onto #1 moves a VALUE** (§9.1: SEMANTIC). By the
design's stop rule the E1 migration does not land; K69 (§4) files it for a
ruling. What CAN land byte-identically is the other half of the 3.5 row:
`vm_nullable` becoming the one, exported, node-nullable function (§3).
