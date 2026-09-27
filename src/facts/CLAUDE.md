# src/facts/ — the pattern-facts ANALYSIS LAYER ([PATFACTS], D120/D126)

ONE organized record of what a pattern HAS — its necessary bytes and run,
its start anchor, its end window, and (as the migration proceeds) its kind
mask, nullability and the k-set walk — computed once per compile attempt,
behind one accessor per fact, sealed by epoch, with the fact-level `-fno-`
denies applied inside the accessor. The design is
`docs/design/patfacts/design.md` (revision 2, ruled D126: Q1-Q11 yes); §9
is the migration order this directory is built in, one relocation per
commit under a zero-movers A/B emit-diff gate.

## The layer

```
lib -> core(base) -> enc -> parse -> ir -> facts -> opt -> gen -> driver -> dump -> cli
```

A derivation here depends on: the sealed IR (the lowered `Ast`, later the
wrapped `Nfa`) and the node-grain pure functions over it; OTHER facts only
through accessors, along the DEPENDS-ON edges `facts.def` declares; and the
encoding DESCRIPTOR as a declared input (carve-out (d)), never
`cx->opt->encoding`. DECISIONS (G1's domination test, the offset-k
selection, `req_admit`, `DFA_SELECT`) stay in their passes (carve-out (c)).

One layer edge points the wrong way and is named rather than hidden: the
node-grain primitives this layer composes (`pcrec_minw`/`pcrec_cwmax` in
`src/opt/mrl.c`, the `atomic.c` predicates) live under `opt/`, so
`facts -> opt` is a CALL-level back-edge (the include graph cannot see it:
they are declared in `core/internal.h`). Trigger to move them down: a
defect traced to that edge (design §4.2.1, §10).

## Files

- `facts.def` — THE TABLE, one `PF_FACT(ID, name, epoch, kind, deny, owner,
  depends)` row per fact (design §11.3 item 1). The accessor ids, the deny
  application, the epoch guard and the `--emit-facts` row order are
  generated from it; the OWNER column, read as PLAIN TEXT by the check, is
  the list of files allowed to include `facts_derive.h`. One row per line.
- `facts.h` — the CONSUMER header: the facts' value types (`ReqRun`,
  `ReqSet`, `PCREC_SANCH_*`), `PatFacts` (`Job.pf`), the seals, the
  accessors and the renderers. No derivation. Self-contained;
  `core/internal.h` includes it so `Job` can carry the record.
- `facts.c` — the RECORD: every accessor's four steps (epoch guard, memo,
  deny, derive — `pf_enter` is the first three, so no accessor can skip
  one), the E2 seal, and the `used` bit (set by a PASS asking, never by a
  derived fact's own derivation).
- `facts_derive.h` — the FACTS-PRIVATE header: every derivation's
  declaration. Only this directory's files and the OWNER files `facts.def`
  names may include it; `tests/codegen/run_facts_checks.sh` checks that from
  the include graph AND the link symbols (`tests/codegen/run_facts_checks.sh`,
  sabotage rows S295/S296).

- **startanch.c** — [OPT-ANCHOR-VM], `[OPTLOOP.1]` batch 1 (D119): THE START
  ANCHOR. One AST-level predicate, `pcrec_start_anchor`, answering *at which
  positions can a match BEGIN* in three values (`PCREC_SANCH_BOT` /
  `_GSTART` / `_NONE`), read by BOTH emitters through the record's
  `pcrec_fact_start_anchor` accessor ([PATFACTS] step 3.0 moved the file here
  from `src/opt/`, one relocation per commit, zero emitted bytes moved).

  **IT EXISTS BECAUSE THE ANSWER WAS ONLY AVAILABLE TO ONE ENGINE.**
  `src/gen/emit_dfa.c` has derived exactly this fact from its own subset
  construction since `[M6.2]` wave D (`dfa_interior_dead(d->s1u)`/`(d->s1g)`
  -> `start_max`), and a VM-routed pattern has no DFA to ask — the hybrid
  prefilter is declined outright for a backreference or a linked call, which
  is exactly the population `cycle1_analysis.md` M2 measures at 52,122x. So
  the fact moves one layer UP and the DFA's pair becomes a CONFIRMATION:
  `emit_attempt` asserts the implication rather than deriving a second
  answer. Implement-then-replace, not a parallel mechanism.

  **THE IMPLICATION IS ONE-DIRECTIONAL.** `PCREC_SANCH_BOT` must imply the
  DFA's `anchored`; the converse is FALSE and is not asserted, because the
  subset construction has already pruned branches this walk still carries.
  The file's own header carries the whole argument, including why
  `pcrec_cwmax(l) == 0` and not `pcrec_minw(l) == 0` is the `A_CAT` arm's
  test and why `A_BREF`/`A_CALL` decline.

  Tests: `tests/codegen/run_prechecks.sh` §1 (the stamp held to the emitted
  bound, in both directions, with a population floor); failing-direction
  control `tests/mech/sabotages/S263`.

## What the check cannot catch

A HAND RE-SPELLING: a consumer that writes its own walk calls no
derivation, includes no private header and references no facts symbol, so
no include or link check sees it (R13's shape exactly). The layer limits it
— the walks' helpers are `static` here, so a re-spelling must rewrite a
whole walk, a large visible diff — and `tools/review/clone_candidates.py`
is the review-time instrument. A reviewer looks for it (design §4.2.3).

Maintenance: update this file when a file is added, moved in or removed.
