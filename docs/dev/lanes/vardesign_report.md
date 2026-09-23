# vardesign — delivery report

Lane `vardesign` (2026-09-23, opus, design only). Branch `lane/vardesign`
from `1a6d8256`. Nothing under `src/`, `cli/`, `lib/` or `tests/` touched;
no `make`, no suite run. Four notes plus three wiring edits.

## Delivered

`docs/design/variables_common.md` (631), `variables_pattern.md` (495),
`replace_design.md` (541), `variables_roadmap.md` (267); entries in
`docs/design/CLAUDE.md`, a line in `docs/dev/lanes/CLAUDE.md`, this report.

## The four opinions the brief asked for

1. **Pattern-variable call interface.** The artifact's EXISTING entries gain
   a `const rx_var *vars` parameter on var-bearing artifacts only — no new
   entry point, no `rx_bind`, no bound state. A bound state is mutable state,
   which `match_api.md` §5.3 forbids as a binding contract on future
   emitters, and §10.5 already refused the identical convenience for frame
   buffers for exactly that reason. No combinatorial growth, because a
   var-free pattern cannot be handed variables and a var-bearing one cannot
   be matched without them (D18).
2. **Replace interface.** Already ruled: D38's one function with `out ==
   NULL` sizing, not a two-call protocol, not an allocator (which would break
   "allocates nothing, ever"). The sink form is phase 4, gated on `[M3]`, and
   is offered by `subst_template_design.md` §7.2 (c) with that exact trigger.
   Variables ride as a last parameter, same rule as the pattern side.
3. **Null variables.** TWO states, not three — UNSET and EMPTY, which the
   tree already spells (`{-1,-1}` vs a zero-length span) and which is bash's
   own `:-`-vs-`-` distinction. An UNSET value at a bare `${name}` in a
   PATTERN is a refused call (`PCREC_ERR_UNSET_VAR`, `PCREC_ERR_STARTPOS`'s
   class); in a REPLACEMENT it renders empty per D38 Q3's ruled axis. The
   asymmetry is deliberate and argued from blast radius: wrong output is
   visible, a wider language is not.
4. **Caseless viability.** Viable NOW, by the mechanism that ships, and the
   charter's preprocessing proposal is the one to decline — a fold is a
   relation between two sides, the subject side is not folded, and under
   `utf8` there is no canonical byte string to fold to.

## MVP, one line

The shared expansion engine with `${name}` and `:-`/`:+` only, reaching a
VM-route pattern variable (caseless included) and a first/global replacement,
with the entry parameter, the abi ritual and the refusal classes settled.

## Findings a reviewer should check first

- **The replace half is mostly already designed.** `subst_template_design.md`
  is ruled wholesale by D38 (fourteen questions). `replace_design.md` §1
  tabulates it; the note adds the variable layer and nothing else.
- **`${...}` in a pattern can never match.** Measured three ways (shipped
  compiler, python `re`, exhaustive over 0..7-byte subjects); corpus
  population 0 of 4,198. The proof is the evidence, not the zero.
- **`vm_bref` is the mechanism**, not the literal emitter — there is no
  compile-time-literal `memcmp` in the VM to give a runtime operand to.
- **"Callouts that return strings" is `rx_renderfn`**, ruled and reserved
  with no producer; native callouts are match-or-fail only, trap-enforced.
- **The emitted global substitution loop is not `match_api.md` §3.1's caller
  loop with a splice** — §3.1 is lossy for empty-preferring patterns and the
  emitted loop is not. Flagged for `[M4-SUBST]`'s implementation note.

## Owed

Nothing. No validation applies to a docs-only delivery; `make` was not run
and none of the four notes asserts a number that a suite could check.
