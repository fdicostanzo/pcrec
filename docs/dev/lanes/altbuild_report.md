# Lane altbuild — alternation normal form stages 1, 2p, 2b (BUILD)

STATE: in progress (WIP). Design: `docs/design/alt_normal_form.md` rev 3.
Build go: Frank, 2026-11-06, stages 1, 2p, 2b only.

## Ids taken

- Sabotage ids: **S1880-S1899** (the highest on main and in every worktree at
  this lane's start was S1856; taken from well above it, since another lane
  and the kit are allocating).
- abi: current + 1 at landing (grep at the time; another lane may bump first).

## Premise test (base 80341284e, before any code edit)

Reproduced on `build/pcrec` at the base: utf8 `req_whole_run` lengths
`(?i)abcdÀefgh` 6, `(?i)αβγ` 0, `(?i)Ελληνικά` 0, `(?i)привет мир` 0,
`(?i)naïve café` 8; `--engine=vm -fno-cls-kit` islands `x(?:[éà]1|q2|r3)y` 1,
`x(?:1[éè]|q2|r3)y` 0, `x(?:1[éà]|q2|r3)y` 1, `x(?:[éà]|q2|r3)y` 1,
`a[éÉ]b` 1, `(?i)aéb` 1, `(?i)xé+y` 2 (rungs `0x4u`, 3319 B). All as §5 states.

## Stage 1 — the lowering's merge, the island's set reading

### What was built

- `src/opt/altnf.c` (new): the alternation owner `pcrec_altnf`, rule M only
  (§3.3): branches described as A_CAT spines of A_CLASS positions; grouped by
  the all-but-`p` key (`anf_in_key`, one statement read by the hash and the
  equality test); adjacency rows 1-3 of §3.2 (row 1 some position disjoint,
  row 2 same width and no writes, row 3 otherwise refuse), the reach test
  over the span between partners with a prefix-count fast path; declared
  order (widths ascending, positions last-first, sweeps to a fixpoint);
  duplicates of an earlier mergeable branch dropped without a reach test.
  `PcrecAnfRules {merge, prefix, suffix}` in `internal.h` (a struct, not
  `#define` bits: limits_check scans numeric defines).
- `src/opt/lower_enc.c`: `LowerOps.split` (`split_byte`, `split_utf8`) and the
  exported `pcrec_lower_boxes` (the canonical unmerged split, the island's
  admission source); `lower_class_utf8` hands its boxes to the owner unless
  bit 10 denies; the `A_CAT(A_EMPTY, alt)` seal is deleted (K123's peel makes
  it dead; the A_WCLASS wrapper stays load-bearing).
- `src/gen/emit_vm.c` `vm_isl_words`: the A_WCLASS arm reads the class's SET
  (`pcrec_wcls_set` -> `pcrec_lower_boxes`), admitted iff every box of the
  canonical split is a single string (today's admission, kept as a
  predicate); the A_ALT and A_CAT spine walks step `t->l` (island-local),
  so a head-position class reaches the set arm. `vm_isl_subtree_nodes`
  (the chain-size walk) unchanged.
- Bit 10 `-fno-altcls-merge` re-specified to deny the owner's merge at both
  callers; `RX_ALTCLS_MERGES` does not count the lowering's merges (spec
  hunks: `docs/spec/tuning.md` §2.6¶1-2, §2.20¶2; `docs/spec/match_api.md`
  §6.3.11¶3; `lib/pcrec.h` bit-10 comment; `--list-axes` row text, a declared
  dump-row delta for B0).
- abi 95 -> 96 (provisional, the next number at landing; renumber if
  vlookbehind bumps first). Readers found by `grep -rn '\b95\b'` over the
  tree's abi sites: `src/gen/emit_dfa.c` `PCREC_ARTIFACT_ABI`;
  `tests/codegen/run_codegen_tests.sh` ABI_EXPECT and its transition
  message; `tests/mech/sabotages/S693_abi_not_bumped.sh` SAB_BEFORE;
  `docs/spec/match_api.md` lines 212 (#error example), 1646 (table), 1804
  (§6¶17); `docs/dev/history/abi_changelog.md` new top entry. Identity gate
  (B) FILEPIN self-pinned to `e3df76804` (`run_recursion_identity.sh`, with
  its SELF-PIN line); the manager re-pins to the landing merge.
- `tests/codegen/run_cpset_structure.sh` [2b]: the owner's four interval
  readers (`anf_cls_hash/eq/disjoint/union`) added FUNCTION-scoped to
  `ALLOW_FN` with their rationale. This gate went red on the correct build
  (the owner is a new reader of `u.cls`); the design did not name it. Not a
  STOP in my reading: it is a population check whose documented process is
  "add the reader with its reason on first contact" (every ALLOW_FN entry
  arrived that way), not an answer or identity gate. Flagged for the code
  round.
