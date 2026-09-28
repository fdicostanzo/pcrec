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

## 3. What landed, commit by commit

| commit | what | gate |
|---|---|---|
| `6e5782aa` | §1-§2 above, before any `src/` edit | — |
| `29f3e168` c1 | **`vm_nullable` becomes `pcrec_nullable`**, moved verbatim (columns kept) from `src/gen/emit_vm.c` to `src/opt/mrl.c` beside `pcrec_minw`, declared in `internal.h` (design §4.3); the `A_CALL` arm kept. The eight `emit_vm.c` readers call it. Prose that said the function was `static` to the emitter is corrected (`internal.h` ×5, `callgraph.c` header, `mrl.c` header, `vm_resolve_nonnull`'s header — which also claimed a LEAST fixpoint and now states the greatest, K69). Sabotage S107/S127/S156 re-anchored by `SAB_FILE` (same lines), S56/S100 by spelling; each row's header says so | A/B c1 (§4) |
| `a1b79e80` | K69 filed; CLAUDE.md (`src/opt`, `src/gen`, `tests/mech`, `docs/dev/lanes`); plan.md 3.5 note (no state flip) | docs |

**Not landed, by the stop rule:** `widths.c` composing `pcrec_nullable(root)`.
It exists only as a scratch build (`scratchpad/swap/`, `pcrec_swap`) used to
measure K69's movers.

## 4. The zero-movers gate

Instrument reused, not rebuilt: `docs/dev/optloop/s1/s1_identity.py`,
unchanged, driven by pf34's `gate.sh` (scratch copy, paths only). BASE =
main `65482b45`'s build. The grid is `{-e byte, -e utf8} × {default,
-fno-req-byte, -fno-req-run, -fno-end-window, -fno-vm-anchor-bound,
-fno-run-prefilter, -fno-offset-skip, -fno-lit-run}`, 16 runs. Each run
covers pcrec-bench's 64 capability patterns × 4 configs and every distinct
corpus pattern × {`--features all`, `+ --engine=vm`}, so `--engine=vm` is
inside every run.

REACH: `pcrec_nullable` is asked by every VM artifact (the slot census,
cost walk and emitter all ask it on every quantifier), so every VM-route
artifact in the grid reached it.

| commit | runs | result |
|---|---|---|
| c1 `29f3e168` | 16 | the first 5 runs were complete at handoff with **0 changed** (byte default: bench 251/5, corpus 5723/715). The rest are OWED: completion line `GATE c1 DONE`, then the chain prints the changed count |

Mover classification (§9.1): none by construction (a verbatim move and a
rename). A nonzero count would be a defect in the move itself.

## 5. K69's mover manifest (informational, not a gate)

The swap variant is diffed over the default deny set, both encodings
(`gate_swap.log`, chain stage `gate swap`). Witnesses measured by hand
before handoff: `(a)?(?1)` 140 diff lines and `(?:(a)|)(?1)` 130 lines, on
both encodings; `(?(DEFINE)(?<g>a))(?&g)` 32 lines under utf8 only (the
DFA gains the start gate). The E1 value flips `no` → `yes` on all of them
and on `(a|(?1))`.

## 6. Validation at handoff

| check | result |
|---|---|
| `make strict` | clean (`-Werror -Wshadow`), at c1 |
| `run_facts_checks.sh` | 8/0, at c1 |
| sabotage anchors (`scripts/m6read_check_sab_anchors.py`) | 314 rows, 330 sites, all resolve |
| spot byte-identity (5 nullable-guard patterns) | identical except the `-o` header name |
| A/B gate c1 (rest), `run_vm_identity.sh`, `run_ir_listing.sh`, gate swap, `make test-codegen`, `run_prechecks.sh`, `make test-recursion-identity`, mech S56/S100/S107/S127/S156, `make test CC=gcc-16` | **OWED — the detached chain, §STATE AT HANDOFF** |

## STATE AT HANDOFF

Everything above is committed on `lane/pf35`. One detached chain runs each
owed stage in series:
`/private/tmp/claude-501/-Users-fdicostanzo-pcrec/pf35/scratchpad/chain.sh`,
log `scratchpad/chain.log`. It prints one `PF35 CHAIN:` line per stage and
ends with `PF35 CHAIN: ALL DONE`. It first waits for gate c1
(`scratchpad/gate_c1.log`, completion line `GATE c1 DONE`).

| stage | log | verdict |
|---|---|---|
| A/B gate c1 | `gate_c1.log` | 32 `identity:` lines, `changed` count 0. Nonzero = a defect in the move: classify per §9.1 |
| `run_vm_identity.sh` | `vmid.log` | rc 0 |
| `run_ir_listing.sh` | `irlisting.log` | rc 0 |
| gate swap (informational) | `gate_swap.log` | K69's corpus mover count. The `changed` lines are EXPECTED; copy them into K69 |
| `make test-codegen` | `codegen.log` | the one accepted red is `FAIL: nm could not read arm_a.o (no rx_search symbol)` |
| `run_prechecks.sh` | `prechecks.log` | rc 0 |
| `make test-recursion-identity` | `recid.log` | rc 0; the (B) pin must NOT move |
| mech S56 S100 S107 S127 S156 | `mech_S*.log` | `mech run COMPLETE ... (unexpected: 0 ...)`, each at its recorded verdict |
| `make test CC=gcc-16` | `make_test.log` | make's `*** [test-X] Error` lines; the known darwin red is `test-codegen`'s nm probe |

## 7. test-recursion red triage (2026-09-27, lane pf35tri)

The chain's `make test CC=gcc-16` (`scratchpad/make_test.log:3828`) failed
`test-recursion` §5 (A==B, `tests/recursion/run_recursion_diff.sh:518`):
`'^((?:a(?1)?))a$' builds by default and NOT under -fno-splice-calls`.
**Verdict: ENVIRONMENTAL — the Mac went to sleep mid-run. Not pf35, not
main, not K69. No fix.**

- **The watchdog line** (`worktrees/pf35/build/watchdog.log:8477`): the
  `-fno-splice-calls` arm's matcher run (`gen_run`) ended
  `verdict=timeout wall=877.12 cpu=0.00 exit=124` at 21:51:19. Zero CPU over
  877 s is a suspended process, not a hang or a slow compile; the default
  arm one line earlier ran `wall=0.30`. `run_arm` returns 1 on any
  compile/cc/run failure, so a run timeout reads as "does not build".
- **The system log** (`pmset -g log`): `21:36:40 Sleep ... 'Maintenance
  Sleep' ... 879 secs` then `21:51:19 Wake ... HID Activity`. The kill
  lands at the wake instant; the 877 s wall is the sleep.
- **Reproduction** (script `scratchpad/../pf35tri/probe.sh`: the section's
  own `run_arm`, extracted verbatim by sed, its FEATS/BATCH/GENCFLAGS and
  its 24-subject grid, both arms on the one pattern): main `d47ea50f`
  (throwaway worktree `worktrees/pf35tri`) and pf35 `50d91f91`, 3 runs
  each: both arms compile and run on every run (102 cells, `wall` 0.5-1.0 s,
  `cpu` 0.01), the arms' answers identical. Does not reproduce on either.
- **Byte identity:** the generated `gen.c`/`gen.h` for this pattern, with
  the section's FEATS, are byte-identical main vs pf35 on both the default
  and the `-fno-splice-calls` linkage — the `pcrec_nullable` move does not
  reach this artifact differently.

Consequence for the chain: `test-recursion` is owed a re-run (the section
alone, `make test-recursion`, on an awake box) before the merge can call
`make test` green; the rest of `make_test.log`'s verdicts stand (the only
other red is `test-codegen`'s accepted darwin nm probe). Lesson for any
detached run on this Mac: a wall-clock `timeout` counts sleep; keep the
box awake (`caffeinate -s`) for unattended chains.
