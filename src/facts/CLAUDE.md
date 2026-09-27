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
  derived fact's own derivation). A derivation reads other facts only
  through `pf_ask`, along `facts.def`'s DEPENDS-ON edges. Also: each fact's
  ONE RENDERER (`pcrec_fact_render`, a no-default switch) which the
  fact-valued stamps call through `pcrec_fact_stamp` and `--emit-facts`
  prints (design §11.5, ruled Q9); the `why` a derivation REPORTS (a
  decline reason, the rate rule a pick answered by) stored with the value,
  never inferred from it; and `--emit-facts`' FORCE LOOP
  (`pcrec_facts_force_all`/`pcrec_facts_force_failed`), which asks the
  unasked facts only after the artifact is complete and, through the one
  `setjmp`'s first arm in `compile_driver`, turns a forced ask that fails
  into that fact's `absent` row rather than a refused compile (ruled Q10,
  r1 A11). No failing forced ask is reachable today (no E2 derivation
  allocates); the guard was verified with a temporary plant (lane pf30's
  report).
- `facts_derive.h` — the FACTS-PRIVATE header: every derivation's
  declaration. Only this directory's files and the OWNER files `facts.def`
  names may include it; `tests/codegen/run_facts_checks.sh` checks that from
  the include graph AND the link symbols (`tests/codegen/run_facts_checks.sh`,
  sabotage rows S296/S297).

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

- **endwin.c** — [OPT-ENDWIN], `[OPTLOOP.1]` batch 1 (D119): THE END-ANCHOR
  START WINDOW. `pcrec_end_window` answers *how far from the subject's END
  can a match BEGIN* as a byte count, or `-1` where it declines, read by both
  emitters through the record's `pcrec_fact_end_window` accessor ([PATFACTS]
  step 3.0 moved the file here from `src/opt/`; the encoding DESCRIPTOR is now
  a declared parameter, `pcrec_end_window(const PcrecEnc *, const Ast *)`,
  resolved once by `facts.c` — the derivation never reads
  `cx->opt->encoding`, design §4.2.2 carve-out (d)).

  **IT IS THE POSITION VIEW'S SECOND CONSUMER, not a second derivation.**
  `--list-axes`' `view` axis already recognises a `\z`/`$` view and uses it to
  pick the `-bounded` prefilter candidates — the scan's ACCEPT test. This adds
  the consumer D77 named and deferred: the scan's START BOUND, which is the
  larger of the two by the measurement D77 asked for (`abc$` on 1 MiB, 1,401x
  rust, collapsing to a flat 30 ns under the hand-twin).

  **FOUR STRUCTURAL DECLINES, each recorded in the file's own header with its
  reason**: an unbounded `pcrec_cwmax`; a multi-byte encoding (the clamp
  computes a byte offset and a mid-character start is a wrong ANSWER, K49/K50
  — tested as `PcrecEnc.start_cls != NULL`, the same field
  `<PREFIX>_STARTPOS_GUARD` reads, which is also what makes `pcrec_cwmax`'s
  CHARACTER count a BYTE count here); a `\G` anywhere in the pattern, since
  `\G` is the one assertion whose truth is a function of the `search_from`
  the clamp moves; and a multiline `$` (D62 control 3).

  **UNLIKE ITS TWO BATCH SIBLINGS IT CAN LOSE A MATCH IF IT IS WRONG**, which
  is why it has an answer-level net and they do not: it moves the position a
  search starts at rather than removing work that would have failed.

  Tests: `tests/assertions/end_window.rxt` (66 oracle-verified cases, every
  claim at a subject length that leaves the clamp inert AND at one that makes
  it fire); `tests/codegen/run_prechecks.sh` §2 (the stamp held to the emitted
  clamp's own literal, the four declines, both engines, a population floor);
  failing-direction control `tests/mech/sabotages/S264`.

- **req.c** — [OPT-REQBYTE] + [OPT-REQPOS] tier 2b THE NECESSARY SET AND THE
  NECESSARY LITERAL RUN, the two CORE facts from one walk of the lowered tree
  (`pcrec_req_walk`): the whole set with its threaded rightmost member (the
  tiebreak the pick falls back on) and the longest guaranteed contiguous run.
  LIFTED out of `src/opt/reqbyte.c` at [PATFACTS] step 3.0 with its lattice
  (`rb_union`/`rb_intersect`, the seven run operations, `rr_cat`/`rr_alt`),
  every helper `static` here; the walk's output types (`RbSet`, `RbRun`,
  `rb_has`) are in `facts_derive.h`, shared with the pick readers that stayed
  in `src/opt/reqbyte.c` (the DERIVED facts `req_run`/`req_byte`) until
  [FINDINGS] B1. Reads no prior and no option: a core fact (design §4.1).
  Its header carries the whole analysis account (why the whole window, why a
  SET and a RUN, the declines, why a lookaround's body is a correctness
  decline). Sabotage S268 (`rr_alt`'s common head) is anchored here.

## What the check cannot catch

A HAND RE-SPELLING: a consumer that writes its own walk calls no
derivation, includes no private header and references no facts symbol, so
no include or link check sees it (R13's shape exactly). The layer limits it
— the walks' helpers are `static` here, so a re-spelling must rewrite a
whole walk, a large visible diff — and `tools/review/clone_candidates.py`
is the review-time instrument. A reviewer looks for it (design §4.2.3).

Maintenance: update this file when a file is added, moved in or removed.
