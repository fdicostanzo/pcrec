# advtri -- triage of lane advnorm's three chain reds (2026-10-08, sonnet)

Branch lane/advnorm (tip 9b9ea259 at start). Chain: `build/adv/chain.sh`,
verdict `build/adv/verdict.txt`. REF = main 77b6b37e with only the abi digit
bumped (`build/ref`).

| red | class | evidence | fix |
|---|---|---|---|
| 1. facts stream, 632 movers | legitimate declared mover; the census instrument had no facts arm | the ONLY facts line that moves, over all 563 distinct moving patterns, is `RX_VM_PROGRAM_BYTES` (556 byte + 530 utf8 listings, e.g. 1167 -> 1202); no other key, no line-count change. It is `VmEntry.program_bytes = pcrec_sb_len_uncut(&job->vmsb)` (`emit_vm.c:10863`), the emitted VM program length the entry-shape size term compares, so the layout bytes the lane added must move it. Entry-shape flips: 0 (neut_default/neut_vm). | `scripts/emit_sweep.py --census-facts-keys` (4fbdfb01) |
| 2. KITCTL_RC=1 ok-lines=0 | chain bug | `kitctl.sh` does `cd "$(dirname "$0")/.."`; the chain ran the copy in `build/adv/`, so the cwd became `build/`, the glob `tests/memfn/pins/r4h_target/adv-*.c` matched nothing (kitctl.log: `sed: can't read ...adv-*.c`, `build/kit.c: No such file`). Run from its intended place (`build/kitctl.sh`, same bytes) the emitted text equals the frozen target: 8 ok lines (all eight shapes), rc 0. NOT a text finding. | scratch `chain.sh` now calls `build/kitctl.sh` (not committed; kitctl is scratch) |
| 3. test-memfn-manifest (4 FAIL) and test-memfn-forms (3 FAIL) | stale check (vocabulary), legitimately moved by the declared mover | rule 4 FAILs for `dir_fwd_skip`, `dir_rev_skip`, `emit_scan_edge`, `vm_emit_span_scan` ("spells no vocabulary form") and C12 STALE ceilings `emit_dfa.c walk-open 2 / walk-stmt 2`, `emit_vm.c walk-open 1`. The forms are still spelled (same five loops, same functions); `search_vocab.tsv`'s two regexes only knew the old text: `walk-stmt` needed `...]]) pos++;` and `walk-open` was `while \([^)]*$`, which stops at the first `)`, and the kit layout now parenthesises `more` and the member. | `search_vocab.tsv` widened (6c84e982), rows and ceilings untouched |

## Red 1 detail

The facts stream's own listing carries no loop text, so the lane's
`--census-ref-re` could not explain it (602 off-diagonal). The census is now
the independent text census of the artifact the fact measures: with
`--census-facts-keys byte:RX_VM_PROGRAM_BYTES,utf8:RX_VM_PROGRAM_BYTES`, a facts
mover is EXPLAINED iff (a) every moved listing line has one of those
`kind:KEY` heads and (b) for an encoding whose REF listing has that line, the
pattern's REF `--engine=vm [-e utf8]` `.c` is a census hit. Three predicates
were tried first and read wrong, which is why the final one is per encoding
and per listing line: default-engine `.c` (889 shape-without-move: DFA edge
loops), `--engine=vm` byte only (5 shape-without-move: patterns whose utf8
program has the shape and whose byte listing is DFA).

Result: `movers=602 text-census-hits=602 off-diagonal 0 / 0` (632 keys, 602
distinct after the `[:60]` key truncation the sweep uses). Failing direction:
declaring only the byte key makes 568 movers off-diagonal (red).

## Red 3 detail

`walk-stmt` now also reads the braced form with the step on its own line,
`walk-open` reads one level of balanced parens and a trailing open paren. After
the widening C12 reads `12 forms in 8 groups, every group at its ceiling`
(walk-open 3 = 2+1, walk-stmt 2, the same ceilings main pinned), i.e. no form
was gained or lost; rule 4 passes for all rows; rule 1 unchanged. No ceiling,
row, floor or manifest line was edited. `tests/memfn/CLAUDE.md` carries the
worked example.

## Re-runs (this worktree, -j6)

- facts stream census (emit_sweep, facts only): see above, 0 off-diagonal.
- kit control (`build/kitctl.sh build/pcrec`): 8 ok, rc 0.
- `make test-memfn-manifest test-memfn-forms`: 21/0 and 4/0 (C13 UNREACHED as before).
- `make test-codegen`: 15/15 scripts passed (log `build/adv/tri/codegen.log`).
- Not re-run (manager's full chain): the other streams, plant, neutrality, full `make test`, mech S214/S72.

## For the manager's re-run

Use the updated `build/adv/chain.sh` (facts census flag, kitctl path). The
chain's sweep line for the other five streams is unchanged and still exits
nonzero by design (movers).
