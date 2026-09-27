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

## What the check cannot catch

A HAND RE-SPELLING: a consumer that writes its own walk calls no
derivation, includes no private header and references no facts symbol, so
no include or link check sees it (R13's shape exactly). The layer limits it
— the walks' helpers are `static` here, so a re-spelling must rewrite a
whole walk, a large visible diff — and `tools/review/clone_candidates.py`
is the review-time instrument. A reviewer looks for it (design §4.2.3).

Maintenance: update this file when a file is added, moved in or removed.
