# tests/memfn/pins/r4h_target/ — R4h's frozen ADVANCE target

Lane advtarget, 2026-10-08 (report: docs/dev/lanes/advtarget_report.md).
The EXACT text the kit's generic row renders for each in-loop ADVANCE
shape [MEMFN] R4h migrates (STAY, EDGE, VMSPAN), given the hook texts
pcrec writes at that site today. pcrec's layout-normalization pre-commit
(Q-R4h-1 (b)) normalizes TO these, character for character, so R4h lands
at zero movers.

Each `<fixture>.c` (the name is its tests/memfn/arm_fixtures.c fixture):
- lines 1-3: a header comment naming the witness pattern and flags, the
  hook texts (`more`, `peek`, `step`, the opaque `member`, `count`,
  cursor) and the indent;
- then the kit's `.use` output, byte for byte;
- from the line starting `/* pcrec today:` to EOF: the same site's text
  as build/pcrec emits it before the normalization (the delta to close).

Checked by tests/memfn/run_arm_pins.sh check 8 (`make test-memfn-arms`):
the middle must equal a fresh render. A kit change that moves one of
these re-freezes the file on purpose in the same commit (with its pins).
Shapes: adv-stay-fwd, adv-stay-rev, adv-stay-view, adv-edge-unbounded,
adv-edge-counted-fwd, adv-edge-counted-rev, adv-vmspan-it, adv-vmspan.
