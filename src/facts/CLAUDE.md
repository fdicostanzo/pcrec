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

- `facts.h` — the CONSUMER header: types, accessors and renderers. No
  derivation. `core/internal.h` includes it so `Job` can carry the record.
- `facts_derive.h` — the FACTS-PRIVATE header: every derivation's
  declaration. Only this directory's files and the OWNER files `facts.def`
  names may include it; `tests/codegen/run_facts_checks.sh` checks that from
  the include graph AND the link symbols.

## What the check cannot catch

A HAND RE-SPELLING: a consumer that writes its own walk calls no
derivation, includes no private header and references no facts symbol, so
no include or link check sees it (R13's shape exactly). The layer limits it
— the walks' helpers are `static` here, so a re-spelling must rewrite a
whole walk, a large visible diff — and `tools/review/clone_candidates.py`
is the review-time instrument. A reviewer looks for it (design §4.2.3).

Maintenance: update this file when a file is added, moved in or removed.
