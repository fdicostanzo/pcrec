# tests/island — [ENG-ISL] the VM's ALTERNATION ISLAND

The axis is `docs/spec/tuning.md` §2.20 (`-fno-alt-island`,
`PCREC_NO_ALT_ISLAND`, bit 23); the stamp is `<PREFIX>_VM_ALT_ISLANDS`
(`docs/spec/match_api.md` §6.3, family (b)); the lowering is `vm_isl_*` in
`src/gen/emit_vm.c`; the measurement that chartered it is
`docs/design/alt_dispatch_study.md` (algorithm (e)).

## Files

- **island.rxt** — what each pattern MATCHES, every expectation produced by
  python3 `re`. BLIND to the island by construction, and that is the point:
  an alternation the island takes and the same alternation under
  `-fno-alt-island` answer identically, which IS the claim, so a corpus that
  could tell them apart would be testing the wrong thing. It carries the
  hazard shapes first — `abc|a|abd` (`src/ir/nfa.c:192`'s rule 1: the answer
  is the LOWEST INDEX that matches, never the longest), `(ab|abc)d` (the
  continuation fails and must backtrack INTO the alternation),
  `(?:abcd|abc|ab|a)z` (four alternatives on one root-to-leaf path, the
  deepest candidate chain the corpus census found), `fo|foo|fo|foo`
  (duplicate alternatives, two accepts at one trie node), `(?:x|)y` (an
  accept at the root) — and then the shapes the island DECLINES. The declines
  are in the same corpus as the takes for the same reason the takes are: a
  decline must answer identically too, and a decline that quietly stopped
  being a decline would otherwise be invisible here.

- **island_caseless.rxt** — the caseless decline, in its own file because
  `flags` is a BLOCK-scoped directive and the fact under test is about the
  whole population: D23 folds a caseless literal to a two-member CLASS at
  parse time, so a caseless alternation is class-leading before
  `src/gen/emit_vm.c` sees it. This is `[FORM-CHAR]`'s axis, not the
  island's, and this file is where that boundary is pinned.

- **run_island_tests.sh** — the STRUCTURAL checks, i.e. everything the two
  `.rxt` files cannot see. Seven blocks: the stamp is unconditional on a VM
  artifact and absent on a DFA one (both directions — a fact readable by a
  macro's ABSENCE is the discriminator [DD-13] had to remove from two
  checks); the island fires and the stamp is a COUNT; **the predicate is
  about the LANGUAGE and not the branch list**; the seven declines, asserted
  against the artifact rather than against the reason; the declined
  population is byte-identical under the flag; the island allocates no slot;
  and the candidate chain exists exactly where an alternative is a prefix of
  another, read off `RX_VM_FRAMELESS`.

  **Block 3 is the one to keep.** It is the check that would have caught the
  defect this lane shipped and then measured: `src/opt/altcls.c`'s stage-2
  factoring runs BEFORE the emitter and rewrites a wide alternation into a
  shared literal plus a nested alternation, so an island whose predicate is
  "each branch is a literal run" declines the top-level alternation and fires
  only on the residues altcls has just created. That build stamped ELEVEN
  islands on the bench's `w-256` — exactly its own `RX_ALTCLS_FACTORED`
  count — and emitted a 3.0% LARGER artifact than the chain it replaced. It
  passed every answer check in this directory. What sees it is the count.

Maintenance: update this file when files are added/removed or change roles.
