# stackfix report (2026-11-07, opus): compiler recursive frames back under the 65722f996 high-water

Main's CI went red on test-stackdepth (run 42377116304, shard 1/3: `optnest@250` killed, exit 139) after the variable-lookbehind stage 1 merge c44649a69. This lane shrinks the recursive frame that grew. Bug fix of landed stage-1 code, so no flag; no re-budget of limits.md §3.10.

## Cause

ONE recursive frame grew: `vm_emit_node` (src/gen/emit_vm.c), 624 -> 672 bytes. It is not edited by c44649a69, but nearly every per-kind emitter is inlined into it (`vm_look` and `vm_look_behind` among them, confirmed by `-fstack-usage`: neither has a frame of its own). Stage 1 added to `vm_look_behind` a `VmLbLabels L` struct (seven pointers) and a seven-entry `int **cols[]` array on the stack. Inlined, they enlarged the frame `vm_emit_node` pays at EVERY nesting level of every VM-emitted pattern, lookbehind or not. optnest and altnest emit two nodes per level (two `vm_emit_node` frames) and grp emits one, which matches the measured growth: about +132 B/level for optnest/altnest and +68 B/level for grp (2 x 48 and 1 x 48, plus alignment).

citri's report also named `pcrec_ast_visit.constprop` 144/160 -> 208. That is an artifact of joining clone lines across files: per file, the ten clones are identical in both trees (4 x 176, 4 x 144, 160, 208). `la_widths`, `pcrec_lookaround_fix_widths`, `vm_r_seek` and `cwmax_walk` did grow, but they are not on these probes' deepest path. The fix leaves every one of them as it is, and the probes still come back under the baseline.

## Fix (commit d9bce0f25)

`vm_look_behind` now allocates its label table from the compile arena: the `VmLbLabels` struct, plus one block of `7 * m` ints sliced into its seven columns, replacing seven separate allocations. Labels are taken in the same order and the table holds the same values, so no emitted byte changes. I did not use `PCREC_OWN_FRAME` (internal.h, the [DD-10] rule) on `vm_look_behind`. That function recurses through `vm_look_behind_branch` -> `vm_emit` into a nested lookbehind's body, so an out-of-line frame would land on the `lookbehind` family's recursion. Moving the table to the arena shrinks the frame without that cost. A comment at the site says why.

## Before / after: RECORD high-water at depth 250 (bytes, this box, gcc 15.2, default flags; budget 442368)

| probe | 65722f996 | main 7474b3e59 | fix d9bce0f25 | altbuild f15a5d4e6 | altbuild + fix |
|---|---|---|---|---|---|
| optnest@250 | 385568 | 418480 | **370672** | 418480 | 370672 |
| altnest@250 | 309032 | 342072 | **294072** | 342072 | 294072 |
| grp@250 | 165608 | 182712 | **158616** | 182712 | 158616 |
| optnest-vm@250 | 291792 | 292832 | 292832 | 292832 | 292832 |
| callouter@250 | 166760 | 183992 | 159704 | - | - |
| callinner@250 | 166184 | 183352 | 159160 | - | - |
| look / lookbehind / atomic / named / starnest / compound / ncgrp / inlineopt @250 | flat | flat | flat | - | - |

Premise test: the 65722f996 and main numbers reproduce citri's figures EXACTLY (0% difference). All three named probes are now below the 65722f996 high-water: optnest -14.9 KB, altnest -15.0 KB, grp -7.0 KB. altbuild adds NO frame growth on these probes; its numbers are main's, and with the fix patched onto it they are the fix's numbers. Logs: `/var/tmp/pcrec-pcrec/scratch/stackfix/{65722f996,7474b3e59,fix1,altbuild,altbuild-fix}.stack.log`.

**optnest-vm is +1040 B over 65722f996 in main, the fix and altbuild alike.** That growth is not per level. It matches `pcrec_emit_vm`'s NON-recursive frame, 3072 -> 4096, which comes from K137's `char retry_adv_doc[1024]` in `vm_emit_search_body` (inlined into `pcrec_emit_vm`, which sits under the whole VM emission). It is not stage-1 lookbehind code and not a recursive frame, so it is outside this lane's build go and is left alone. Should the manager want those 1024 bytes back: `retry_adv_doc` could become an arena buffer (coding.md's fragment rule), a one-line change.

## Per-function `-fstack-usage` (src/*/*.c, `-O2 -g -std=gnu11`, frames that differ)

| function (file) | 65722f996 | main | fix | recursive on these probes? |
|---|---|---|---|---|
| vm_emit_node (emit_vm) | 624 | 672 | **576** | yes: the fix |
| pcrec_emit_vm (emit_vm) | 3072 | 4096 | 4096 | no: once, base of the VM emission (K137 buffer) |
| la_widths.constprop (mod_lookaround) | 80 | 112 | 112 | lookbehind only |
| pcrec_lookaround_fix_widths (mod_lookaround) | 336 | 352 | 352 | no |
| cwmax_walk / pcrec_cwmax (mrl) | - / 48 | 64 / 8 | 64 / 8 | not the deepest phase |
| vm_r_seek (vm_stmt) | 16 | 32 | 32 | no |
| pcrec_vm_b_seek_local (vm_stmt) | - | 800 | 800 | no (new, leaf) |
| vm_isl_emit, vm_wcls (emit_vm) | - | 256, 128 | 256, 128 | no (out-of-line now) |
| pcrec_ast_visit.* (internal.h) | 4x176, 4x144, 160, 208 | same | same | unchanged; citri's diff was a mis-join |

Main vs fix differ in exactly ONE frame (`vm_emit_node`). Tool: `/var/tmp/pcrec-pcrec/scratch/stackfix/su.sh TREE OUT`, tables `su-*.tsv`.

## Validation

- (a) Byte identity: `scripts/emit_sweep.py --ref-bin <main 7474b3e59 scratch build> --bin <worktree build>`, all default streams, then the same again with `--extra-base='-e utf8'`. Queue job `210-stackfix-sweep`. OWED (expected: byte-identical on every stream, VERDICT GREEN; log /var/tmp/pcrec-pcrec/scratch/stackfix/sweep-{byte,utf8}.log, job line `stackfix-sweep: VERDICT GREEN`).
- (b) Stack: `bash tests/thread/run_compile_stack.sh` on the worktree build, rc=0, numbers in the table above.
- (c) `make -k test-stackdepth test-lookaround` on the worktree, solo, niced. Queue job `211-stackfix-sections`. OWED (expected: test-stackdepth and test-lookaround green, no `*** [...test-` line in the job log).

## STATE AT HANDOFF

- Branch lane/stackfix: fix commit d9bce0f25 (src/gen/emit_vm.c only), plus this report and its history-index line.
- No abi bump, no spec hunk: no caller can observe the change, and the budget is unchanged.
- Rulings file stackfix_rulings.md: empty at the last read, so no entry applied.
- OWED: stackfix-sweep (queue job 210-stackfix-sweep: expected byte-identical, `stackfix-sweep: VERDICT GREEN`) and stackfix-sections (queue job 211-stackfix-sections, which runs after the sweep: expected test-stackdepth and test-lookaround green). The manager reads their verdicts from worktrees/.boxqueue/done/. `make test` is the manager's to queue after review.
- Scratch: /var/tmp/pcrec-pcrec/scratch/stackfix/ (scratch builds of 65722f996, 7474b3e59 and altbuild, the stack logs, the su tables, the sweep outputs under sweep-byte/ and sweep-utf8/, the queue job scripts under jobs/).
