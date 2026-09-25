# cmpmap: delivery report (lane `cmpmap`, opus, 2026-09-25)

Brief: write `docs/design/compare_stack.md`, the coordination map owned by
`[OPT-LITSCAN]` (D122 + ADDENDUM). The lane was read-only on `src/`, `cli/`, `lib/` and `tests/`. No make and no heavy runs.

## What was delivered

- `docs/design/compare_stack.md`, with findings first, then: the refined layer frame (§1), the site
  inventory with file:line (§2), the duplications and their guards (§3), the shared
  primitives (§4), per-row declarations and the sites that keep their own form (§5),
  the sequence with a D77 gate per step (§6), and four questions for Frank (§7).
- `docs/design/CLAUDE.md` gains an entry for the map.

## Validation

This is a docs-only change and nothing here builds. Every file:line in §2 and §3 was read at
897a97f0 in this worktree. Eleven anchors were re-checked after drafting, and seven that had drifted
by one or more lines were corrected. §6.3's stamps come from the main tree's
`build/pcrec` (main HEAD at read time) compiling seven pcrec-bench
`bench/capability/patterns/*.rx` files with `-p rx --features all`. The pcrec-bench files were read only. The
emitted artifacts went to a scratch directory inside this worktree, which was deleted
before the commit.

## Findings (the eight the manager should read)

1. The layer frame holds with three refinements. The byte cube is a cross-layer
   primitive (L1/L2/L3). The compile-time vs run-time operand is an axis, not
   a layer. The DFA route has no L2 site at all.
2. The literal compare is spelled six ways. Only REQ_RUN's constant-length
   memcmp is fused by gcc.
3. There are four emitted memchr scanners. The router +80.8% is two of them on one byte,
   and it needs no mask.
4. **The four losing WAF cells are DFA-route, with no literal-compare site.**
   Two have no required byte and one has prefilter `none`. `[WORD-FOLD]`'s VM
   compare does not reach them. §6 puts S2 (exact `[OPT-VMLIT]`) and S3 (WAF
   attribution) ahead of any caseless mask. This contradicts the manager's
   expected order, on the census's own §5/§8 text plus fresh stamps.
5. The ASCII fold has four spellings. One of them is unguarded: the `vm_cls_shape` FOLD
   recognizer at `emit_vm.c:1633`.
6. `cube_of` exists three times, all outside `src/`, with no agreement check.
7. The frequency prior's encoding gate is in `reqbyte.c` and `emit_dfa.c:5499`
   but absent from `prefix_k.c`'s offset-k model (`set_ppm`, :305). That is
   correctness-neutral, and whether it hurts selection under utf8 is unmeasured (Q3).
8. The range test is emitted in two different texts (VM vs DFA scan-edge). That is `[CLS-TREE]`'s to unify.

## Not done / owed

- plan.md is NOT edited. The manager owns the `[OPT-LITSCAN]` row, and adding a
  pointer to this map is a one-line cross-note at merge.
- §6.3's "reachable by" column is inspection, not measurement. S3 exists
  to measure it.
