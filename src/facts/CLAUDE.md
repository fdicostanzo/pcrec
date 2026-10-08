# src/facts/ — the pattern-facts ANALYSIS LAYER ([PATFACTS], D120/D126)

ONE organized record of what a pattern HAS — its kind mask and
nullability (E1, step 3.2), its necessary bytes and run, its start anchor
and start set,
its end window, and (E3, step 3.4) the k-set walk and the necessary run's
pin on it — computed once per compile attempt,
behind one accessor per fact, sealed by epoch, with the fact-level `-fno-`
denies applied inside the accessor. The design is
`docs/design/patfacts/design.md` (revision 2, ruled D126: Q1-Q11 yes); §9
is the migration order this directory is built in, one relocation per
commit under a zero-movers A/B emit-diff gate.

## The layer

```
lib -> core(base) -> enc -> parse -> ir -> facts -> opt -> gen -> driver -> dump -> cli
```

A derivation here depends on: the sealed IR (the structural `Ast` at E1,
the lowered `Ast` at E2, the wrapped forward `Nfa` at E3) and the node-grain pure functions over it; OTHER facts only
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
  one), the seals, and the `used` bit (set by a PASS asking, never by a
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
  **The E1 seal (step 3.2)** is the one EAGER seal: `pcrec_facts_seal_e1`
  (called by `compile_driver` right after `pcrec_callgraph_build`) FORCES the
  kind mask and nullability on the structural tree, because
  `pcrec_lower_enc` rewrites that tree in place and a lazy answer would
  depend on ask time (design §2). `pcrec_facts_seal_e2` then re-derives both
  on the LOWERED tree and refuses the compile with an internal error if
  either moved (`pf_check_e1`): design §3's invariance proof, checked on
  every compile in `cstart_check_omission`'s shape. Its detector is
  `run_facts_checks.sh` [facts-e1]; sabotage rows S302 (kind mask) and S303
  (nullability) plant the two lowering drifts.
  **The E3 seal (step 3.4) is PER BRANCH**: `pcrec_facts_seal_e3` is called
  inside `compile_driver`'s ENG_UNANCH arm alone, right after
  `pcrec_nfa_wrap_unanchored` (the count-collapse ladder may rebuild the
  machine before that point; ENG_ATTEMPT never wraps it). On a route that
  sealed E2 but not E3, `pf_enter` answers an E3 fact with its empty value,
  status `absent`, and the route's decline — `decline:attempt-unwrapped-nfa`
  where a forward NFA exists (read off the machine: `Job.nfa.n > 0`) or
  `decline:no-forward-nfa` — and the force loop asks it so the listing names
  the reason. Detector `run_facts_checks.sh` [facts-e3]; S306 (the seal
  leaks to ENG_ATTEMPT), S307 (the tokens swap).
- `facts_derive.h` — the FACTS-PRIVATE header: every derivation's
  declaration. Only this directory's files and the OWNER files `facts.def`
  names may include it; `tests/codegen/run_facts_checks.sh` checks that from
  the include graph AND the link symbols (`tests/codegen/run_facts_checks.sh`,
  sabotage rows S296/S297).

- **kinds.c** — [PATFACTS] step 3.2: THE KIND MASK (`pcrec_pattern_kinds`),
  E1. One `PF_KIND_*` bit (facts.h) per construct kind a pass asks about at
  the ROOT — backreference, linked call, `${...}` variable, atomic,
  lookaround, live capture, collapsible repeat — each the root answer of
  the node predicate in `src/opt/atomic.c`/`src/parse/mod_vars.c`, which
  stay node-grain (the discharge pass and module `lookaround` ask them of
  subtrees before any seal). Readers: `select_engine.c` (`forces_captures`,
  the prefilter decision), `compile.c`'s collapse gate, `emit_vm.c`'s
  `mrl_win` and the `--emit-ir` listing's `has_bref`/`has_call`.
  `pcrec_has_call` (any call) has no bit: it has no root-grain reader (D77).

- **widths.c** — [PATFACTS] step 3.2: THE ROOT NULLABILITY
  (`pcrec_pattern_nullable`), E1. Since K69 / step 3.5 it composes
  `pcrec_nullable(root)` — the one node-nullability function
  (`src/opt/mrl.c`) — where it composed `pcrec_minw(root) == 0` until the
  call graph published a call's nullability as the LEAST fixpoint
  (`minw != 0`) before this seal; the two agree on every kind now. Replaced
  `EngineFit.lang_nullable`, the copy the fit site wrote; readers: the two
  prefilter declines, `compile.c`'s collapse gate, the [K50-NULLGATE] start
  gate (`pcrec_startgate_needed`). Its header carries why `pcrec_minw` is the
  right walk and why the count-collapsed language's nullability is the exact
  one's. The root byte `minw` (E2) joins it when a step moves its reader;
  the node-grain widths stay in `src/opt/mrl.c`. Sabotage S206/S207 anchor
  here.

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

- **startset.c** — [START-SET] stage 1 (D148, lane ssbuild01, 2026-10-05;
  `docs/design/startset.md` §3): THE START SET (`pcrec_start_set`, fact
  `start_set`, E2 core, no deny). A SUPERSET of the bytes the first consumed
  byte of a non-empty match can be, on the LOWERED tree (so it reads the
  compile's own `-i`/`--ucp`/encoding by construction, sound-F4), with every
  zero-width node erased (∅, nullable) and `A_BREF`/`A_CALL`/`A_VAR` read as
  all 256 bytes, nullable. Its `nullable` is the ERASED language's (sound-F9):
  `nullable` ⇒ `start_set.nullable`, pinned by `tests/startset/` [ss-null].
  Spines iterative, no `default:`, `Ast.u.call.body` not followed. No pass
  reads it at stage 1; stage 2's VM hat and stage 3's DFA hat will. Checks:
  `tests/startset/` (C-SS\*, [ss-null], [ss-flag]); sabotage S501 (a
  lookaround read as consuming) and S502 (`A_CAT` drops `null(l) ? F(r)`).

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
  LIFTED out of `src/opt/reqbyte.c` (deleted at B1) at [PATFACTS] step 3.0 with its lattice
  (`rb_union`/`rb_intersect`, the seven run operations, `rr_cat`/`rr_alt`),
  every helper `static` here; the walk's output types (`RbSet`, `RbRun`,
  `rb_has`) are in `facts_derive.h`. The walk reads no prior and no option: a
  core fact (design §4.1). **Since [FINDINGS] B1 (= step 3.1) this file also
  OWNS the two DERIVED facts `req_run`/`req_byte`** (`pcrec_req_window`,
  `pcrec_req_pick`, `facts.def`'s owner column): each asks the byte-rate
  accessor FIRST, before any branch (findings design §6.4 rule 1), and hands
  the answer untested to the rate readers in `src/core/findings.c`, which
  take plain byte arrays so the findings layer needs no facts type. The
  readers live beside the primitives (carve-out (b)); the compositions that
  turn their answers into the facts live here, with the walk, because a
  `src/core/` file including `facts_derive.h` would point the include graph
  the wrong way (the findings design named `src/core/findings.c` as the
  owner; B1 recorded why it is this file instead).
  Its header carries the whole analysis account (why the whole window, why a
  SET and a RUN, the declines, why a lookaround's body is a correctness
  decline). Sabotage S268 (`rr_alt`'s common head) is anchored here.
  **[K82] (B) (lane k82hbuild, 2026-10-05, abi 61): THE RUN'S MAXIMUM BYTE
  OFFSET.** The walk also carries each subtree's maximum width in BYTES
  (`RbRuns.maxw`, saturating at `PCREC_W_UNBOUNDED`) and its run's maximum
  offset from the subtree's start (`RbRun.off`): a head at 0, a tail at
  `maxw - n`, a right factor's run `maxw(left)` further in, a repeat's run in
  its first iteration; an annotation only (`rn_better` is unchanged). The
  core half is `ReqRun.whole_maxoff`; `pcrec_req_window` derives the window's
  `maxoff` (`+ at`), published as the new derived row `req_run_maxoff`
  (`facts.def`, `pcrec_fact_req_run_maxoff`). Its consumer is the handoff
  (src/gen/emit_dfa.c, the FIRST rows of `cand_rows[]` — `req_uses[]` until
  [START-TABLE] C4 — `tuning.md` §2.41). Sabotage S465 (a wide
  class counted as one byte) and S466 (an alternation's left width) and S474
  (the choice preferring a bounded run) are anchored here.
  **[OPT-LITSCAN] S4 C3 (lane c3build, 2026-10-03, abi 59): A RUN OF
  POSITIONS.** `RbRun`/`ReqRun` carry a per-position mask K beside the bytes
  T; a position is a byte or a cube of at most `pos_set` members
  (`PCREC_MAX_REQ_RUN_POS_SET` = 2, handed in by `facts.c`, 1 under
  `-fno-req-run-fold`, so the walk reads no option); `rn_better` ranks by
  information (`Σ popcount(K)`); the alternation's common head/tail are the
  CUBE HULL; `rn_put` is the one position constructor and refuses a
  non-canonical pair (`T & ~K != 0`) as an internal error. The floor is in
  bits (`PCREC_MIN_REQ_RUN_BITS` = 16) at `pf_derive_req_walk`. `req_pick`
  returns the run's scan member only where it is exact (else the set's
  pick). `docs/design/litscan_s4.md` §2.3; sabotage S446, S451, S453, S456.

- **kset.c** — [OPT-K] + [OPT-LITSCAN] S1, [PATFACTS] step 3.4: THE K-SET
  WALK (`pcrec_kset_walk`, fact `kset_walk`, E3 core) and THE RUN PIN
  (`pcrec_run_pin`, fact `run_pin`, E3 derived). LIFTED out of
  `src/opt/prefix_k.c`, whose offset-k SELECTION stays there and reads the
  walk through the accessor (carve-out (c)); the per-offset rates the walk
  computed inline moved into the selection, so the walk reads no prior
  (r1 A2). The walk runs from the wrapped NFA's `anch_start` — the thread
  from the candidate start ALONE, which no DFA state isolates — passing every
  assertion as though it held, so a set can only be WIDER than the truth
  (the file's header carries the whole soundness argument). Its `NKind`
  switch has NO `default:`: a new CONSUMING kind silently treated as an
  assertion would be its one unsound direction; it is the SECOND
  hand-maintained exhaustive `NKind` walk in the tree (`src/ir/dfa.c`'s
  closure is the first), paired by nothing but this sentence and
  `-Wswitch`. The walk's scratch is arena, once per attempt: R14's seven
  re-walks per compile (`unanch_start`'s callers) are one.
  **THE PIN IS A PURE NFA+WINDOW FACT** (design §4.5): the smallest offset
  at which the walk's singletons spell `req_run`'s WINDOW (the bytes the
  pre-check compares, litscan_s1.md R3-2), DEPENDS-ON `kset_walk req_run`.
  Before step 3.4 it was computed only inside the selection, so it read 0 on
  every artifact with no offset-0 prefilter by accident of call order; now
  it is true on some of those (`\zabc`), and EVERY READER OWES THE KIND
  GATE — `src/gen/emit_dfa.c` reads it only through `us_run_pin`.
  Sabotage S280 (the pin ignores the run's bytes) is anchored here.
  **[OPT-LITSCAN] S4 C3 (abi 59): the pin is the EXACT STRETCH** — PICK
  (byte candidates, reversed) over the window's exact positions, then the
  maximal exact stretch around the pick, when it has two or more positions;
  `RunPin` gained `at`/`len`/`idx` and the derivation takes the byte-rate. On
  an exact run it is the pre-row pin exactly (the C3 manifest's 0
  off-diagonal); `--emit-facts` renders `o` or `o:at+len`.

## What the check cannot catch

A HAND RE-SPELLING: a consumer that writes its own walk calls no
derivation, includes no private header and references no facts symbol, so
no include or link check sees it (R13's shape exactly). The layer limits it
— the walks' helpers are `static` here, so a re-spelling must rewrite a
whole walk, a large visible diff — and `tools/review/clone_candidates.py`
is the review-time instrument. A reviewer looks for it (design §4.2.3).

Maintenance: update this file when a file is added, moved in or removed.
