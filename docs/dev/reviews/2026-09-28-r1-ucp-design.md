# r1 — light D6 panel on `docs/design/ucp_design.md` ([UCP] design note)

2026-09-28, lane `ucpdes`. Two read-only sonnet critics, neither ran `make`:

- **SEM** — PCRE2 UCP semantics and oracle fidelity (re-ran light 10.46/10.48
  probes and fresh `build/pcrec` compiles).
- **GEN** — mechanism generality + measurement honesty (re-ran every
  committed probe locally; read `internal.h`, `dfa.c`, `emit_dfa.c`,
  `scanedge.c`).

**Verdict: one BLOCKER, four SHOULDs, all applied.** Every count in the note
reproduced independently: 57/57 set relations, 209/0/83 (+ controls 131 and
6), 3,368,421/0 (+ controls 267,786 and 1,895,172), 158/172, 46/91, 108, the
three hazard cells, and D129's staging order.

## Findings and dispositions

| ID | sev | finding | disposition |
|---|---|---|---|
| **GEN-1** | BLOCKER | §2.1/§6 U2 said the DFA's class axis already implements `A_CTX` "for W" and "generalizing the SET is the whole change". It does not: `upc_of_class` (`internal.h:3654`) is a fixed priority if-chain over two named global sets, `eqclasses` refines per set behind a boolean (`dfa.c:176-182`), `DState.up[UPC_N]` is fixed at 4 and correct only because the sets are disjoint. `A_CTX` brings several arbitrary, possibly OVERLAPPING sets per machine (the census's own k=2 witness; any `V ⊂ W`); the if-chain would collapse `V∩W` silently. No check covered it. | **APPLIED.** New §2.4: the class axis becomes a per-machine ORDERED LIST of context sets as DATA (`Dfa.ctxsets`, listable per [LIST-TABLES]); a character's context is its ATOM (membership vector) — the SAME atom mechanism U3's island uses, one mechanism; `upc_of_class` → `atom_of_class[]`; `up[]`/`s1u[]`/`s1g[]` sized to the realized atom count; one atom-count `limits.def` row for U2 and U3; identity claim for `{word, newline, start}` stated as a claim with its gate. U2's row now prices the data-structure change, adds byte identity for every non-moving class-axis artifact, and a sabotage row (the old if-chain over two overlapping sets) with two overlap witnesses (the census's k=2 pattern and a synthetic `V ⊂ W`). §2.1's sentence corrected. The manager's framing (the if-chain is the "spiderweb" Frank ruled against; fix as a table) is what §2.4 implements. |
| **GEN-2** | SHOULD | `ctx_sets.py` missed the bare `\xHH` (HH ≥ 80) spelling, so a non-ASCII set could read as ASCII-only. Harmless on the reported run (the one such body, `capability/utf8-lead-no-cont`, is byte-encoded and short-circuits). | **APPLIED.** Regex extended, comment records why the run's numbers did not move; census re-run, output identical (156 / 2 / 14). |
| **GEN-3** | SHOULD | §3/§6 never said how `minimize.c` treats island states / atom columns. | **APPLIED.** §3.1: atoms are alphabet symbols to minimization (one column each, like a byte class); island tokens are an emission-time renumbering after minimization, the scan-edge heads' order (`scanedge.c:624-666`). |
| **SEM-1** | SHOULD | §1.3's side finding under-scoped the `parse.c:652-657` comment: its "all four match once UCP is added" is wrong in BOTH halves — `(?i)[a-z]`/`(?i)[k]` already match U+212A under UTF|CASELESS without UCP. `parse.c:494-496` already has the correctly scoped wording. | **APPLIED.** §1.3 rewritten; U0's fix points at the `:494-496` wording. |
| **SEM-2** | SHOULD | `ctx_sets.py` is UCP-blind: lowercase `\d \w \s` (and POSIX names) are ASCII-only only without UCP — a landmine for re-use once `(*UCP)` patterns exist. Not a wrong claim about today's run (no corpus pattern spells `(*UCP)`). | **APPLIED.** `ascii_only` gains a UCP arm keyed on a leading `(*UCP)`; comment states it is a re-use guard, not a correction. Re-run identical. |

## Semantic checks the SEM critic ran that HELD (recorded so they are not re-run)

`(?aP)` restricts `[:digit:]`/`[:xdigit:]` even with `(?-aT)` — DEF_UCP_T's
`¬aP ∧ ¬aT` conjunct is load-bearing; `(?aS)` touches `\s`/`\S` only, not
`[:space:]`/`[:blank:]`; `\h \v \R . \p{..}` identical under UTF vs UTF|UCP;
`(*UCP)`/`(*UTF)` either order, offset 0 only; the byte-tier Latin-1 cells and
`(?i)(?r)` inertness; `\b` at a combining mark after ASCII (no spurious
boundary under UCP, a correct one without) — the two-boolean prev/next model
needs no extra machinery.

## The "no spiderweb" check (Frank's table rule, added mid-panel)

The table requirement (§0.1, T1-T8) arrived after both critics had finished
their reads; the GEN critic's report predates it and does not cover it. The
lane ran the check itself, and it is disclosed as a SELF-check, not a critic
finding: every selection the note makes was listed and located in a table —
definitions (T1), fold (T2), lookaround lowering (T3), machine form incl. the
dial θ (T4), state cell incl. the self-loop fold (T5), vector producer incl.
the sectioning DP inside `kit` (T6), linkage (T7), VM context test (T8); the
context axis itself was the one if-chain found (GEN-1) and is now §2.4's data
list. `(*UTF)`/`(*UCP)` acceptance is registry rows (already tabular).
Two things are left to the implementer and are not selections: `ENG_ATTEMPT`'s
carried-vector optimization (H6) and the island's per-state predicate order
inside T6 row 3. **A critic-run "no spiderweb" pass is owed at the U2/U3
charter** (recommended in the lane report).
