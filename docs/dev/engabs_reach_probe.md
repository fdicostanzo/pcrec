# [ENG-ABS] reach probe — why `unwrapped` stops at large counts (2026-08-30)

Answer to pcrec-bench O-9 ask (ii) ("is `dfa_match=search-filter` on a
whole-subject artifact intended, or the [ENG-ABS] `unwrapped` path failing
to apply at large counts?"). Read-only probe (lane absprobe, sonnet) on
main b819512's `build/pcrec` (the [ENG-ABS] code is 0f5a98f's, the same
as pin 96e44c2). Every number below is MEASURED unless marked INFERRED;
the commands are in §E. Nothing under the tree was modified.

## A. Verdict: DESIGN LIMIT, not a reach bug

`unwrapped` stops applying exactly when the OPTIONAL anchored machine's
state count exceeds `PCREC_ANCHORED_MAX_STATES = 4096`
(`src/core/limits.h:619-621`), a cap deliberately LOWER than the engine's
own DFA ceiling, charged in `build_anchored_dfa()`
(`src/core/compile.c:270-294`): `pcrec_build_dfa(…, PCREC_ANCHORED_MAX_STATES,
nfa.anch_start, true)`; `if (adfa.overflowed) return;` leaves
`anchored_ok == false`. Selection (`src/gen/emit_dfa.c:3880-3888`, axis G):
`match_unwrapped_applies = anchored_ok && !dfa_engine_is_empty`; the
candidates are `unwrapped` (deny bit `PCREC_NO_ANCHORED_DFA`) then
`search-filter` (always). Documented: `docs/design/anchored_match_unwrapped.md`
§5.2 ("THE OPTIONAL MACHINE HAS ITS OWN CEILING, LOWER THAN THE ENGINE'S …
an overflowed anchored machine selects search-filter. It is stamped, it is
counted, and it is never a diagnostic"); `docs/spec/limits.md`'s [ENG-ABS]
paragraph ("crossing a ceiling there produces no diagnostic and no fallback
engine … the set of patterns pcrec ACCEPTS is unchanged"). The machine is
built LAST (after the mandatory forward+reverse pair) and `Ctx.dfa_overflowed`
is saved/restored around it. There is NO runtime flag to raise the cap
(`--fanchored-dfa` / `--anchored-max-states=N` refused as unknown); the
only override is pcrec's own build-time `-DPCREC_ANCHORED_MAX_STATES=N`,
used by one test (`tests/codegen/run_anchored_match.sh`, lowers it to 6).
Byte-level confirmation: at the last-successful rung of all eight ladders
the emitted `rx_anchored_next_state` table is exactly `[8192]` = 4096
states × 2 byte-classes.

## B. The ladder (`--features all` so `\z` is accepted)

| skeleton | form | last `unwrapped` n | first `search-filter` n |
|---|---|---|---|
| `[a-z]{0,n}` | plain | 4095 | 4096 |
| `[a-z]{0,n}` | `(?:…)\z` | 2047 | 2048 |
| `[a-z]{n,}` | plain | 4095 | 4096 |
| `[a-z]{n,}` | `(?:…)\z` | 4094 | 4095 |
| `(?:\d{1,n}){1,n}` | plain | 63 | 64 |
| `(?:\d{1,n}){1,n}` | `(?:…)\z` | 14 | 15 |
| `(?:(?:\d{1,n}){1,n}){1,n}` | plain | 15 | 16 |
| `(?:(?:\d{1,n}){1,n}){1,n}` | `(?:…)\z` | 6 | 7 |

`[a-z]{0,16384}\z`, `(?:\d{1,64}){1,64}\z` and the 3-level `{1,16}\z`
never reach axis G: the MANDATORY forward+reverse pair overflows
`PCREC_MAX_SUBSET_ELEMS` (48,000,000, the [SEL-1] budget) and [SEL-1]
re-runs as the VM — stamped `RX_ENGINE "vm"`, `RX_ENGINE_SEL
"collapsed-prefilter"`, `RX_ENGINE_WHY "dfa overflowed: subset construction
exceeds 48000000 state-set elements (K7) at pattern offset 0"`.

**Finding — the `\z` wrapper's cost is not uniform.** For `{0,n}` (both
ends bounded) the whole-subject spelling roughly HALVES the reachable n
(2047 vs 4095): the `\z` artifact carries a separate 4096-entry
`rx_anchored_end_view` table the plain form lacks (INFERRED mechanism:
each count-state needs an EOF-aware sibling under subset construction).
For `{n,}` it costs ~nothing (4094 vs 4095). So the bench's own
`(?:BODY)\z` spelling is part of why bounded bodies fall to `search-filter`
at the counts they do.

## C. Controls

`-fno-anchored-dfa` on an `unwrapped` rung → `search-filter` (as
documented); on the failing rung → unchanged. `--list-axes`'s `match` row
has a deny field only, no force (D82: "the flag removes the object;
nothing branches on the flag"). `--engine=vm` on `[a-z]{0,4096}` builds:
`RX_ENGINE "vm"`, `RX_ENGINE_SEL "forced"`, `RX_ENGINE_WHY "--engine=vm"`,
`RX_VM_PREFILTER "none"` — the bench's ×37 baseline, reachable and stamped
distinctly from the DFA's own `search-filter` form.

## D. Ask (i) — `[a-z]{0,65535}` and what distinguishes a refusal

Default: exit 1, no artifact, stderr `pcrec: pattern too large (NFA
exceeds 131072 states) (pattern offset 0)` — `PCREC_MAX_NFA_STATES`
(`src/ir/nfa.c:110-111`), one of the two ceilings limits.md's [SEL-1]
exception excludes from fallback (with `PCREC_MAX_VM_NODES`; INFERRED
that the latter behaves the same — not reached by this ladder).
`--engine=vm`: exit 0, artifact, `RX_ENGINE_SEL "forced"` (no DFA pair is
built under a forced engine). Three distinguishable outcomes, by exit
code + artifact presence, not one field: (1) ceiling refusal = exit 1,
no file, no stamp; (2) [SEL-1]/[OPT-4] fallback = exit 0 + `RX_ENGINE
"vm"` + `RX_ENGINE_SEL` ∈ {overflowed-dfa, overflowed-prefilter,
collapsed-prefilter} + `_WHY` naming the ceiling; (3) [ENG-ABS]'s own
case = DFA stays selected, only `RX_DFA_MATCH` moves, `RX_ENGINE_WHY`
NULL. No timing is printed for any compile or refusal; no exit-code
convention beyond 0/1.

## E. Commands

    gnutimeout 120 build/pcrec --features all -p rx -o OUT.c -- 'PATTERN'
    gnutimeout 120 build/pcrec --features all -fno-anchored-dfa -p rx -o OUT.c -- 'PATTERN'
    gnutimeout 120 build/pcrec --features all --engine=vm -p rx -o OUT.c -- 'PATTERN'
    build/pcrec --list-axes

Largest artifacts ~725-939 KB, a few seconds each; nothing timed out.
Consequence for the plan: raising `PCREC_ANCHORED_MAX_STATES` (or a
raise-only flag on the [ART-SIZE] `--max-emit-*` model) is the bench's
candidate 1 — an optimization-column row PROPOSAL (D86), not chartered.
