# Lane clss3inv: [CLS-TREE] S3 reader inventory (report)

Lane clss3inv, sonnet, read-only against `src/`, 2026-09-29. Branch
`lane/clss3inv` from `lane/clss1` (`7fff7933`). Deliverable:
`docs/dev/cls_s3_reader_inventory.md` (the greps are stated there and
reproduce the counts).

- Real count: 49 `case A_CLASS` arms + 6 comparisons, 20 files, matching the
  design. Dispositions of the 49: 10 walk the child, 1 producer, 8
  unreachable-by-phase (should be loud), 30 structural leaf.
- Five of the 49 AKind switches carry a real `default:` (`-Wswitch` silent);
  one (`vm_isl_words`) silently moves artifacts if `A_WCLASS` is unhandled.
- The existing loud guard (`pcrec_cls_bits`, `hi > 0xFF`) does not cover
  Latin-1-range wide sets under `utf8`; S3 needs a kind guard.
- A wrapper node hides lowered bytes from the CAT-spine flatteners
  (`vm_cat_flatten` etc.): artifact-moving (D-3).
- `lane/ucpu2` adds one reader (`ctxnode.c:50`) plus 45 `A_CTX` arms in the
  same switches: merge-order question (D-7).
- The K53 3,348/3,348 driver was never committed; `emit_sweep.py` has no
  encoding axis, so today's sweeps are vacuous for S3 (D-8).
- Sizing: one opus lane, medium, three commit groups.

No validation run (light lane, no `make`, nothing built).
