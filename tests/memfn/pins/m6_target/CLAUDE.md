# tests/memfn/pins/m6_target/ — M6's frozen strided ADVANCE target

Lane m6, 2026-10-08 (report: docs/dev/lanes/m6_report.md). R-10 / M6
(VMSTRIDE only, RULED Q-R10-2..6): the VM cursor rung's STRIDED span loop
(`vm_stride_loop`, stride W > 1) is the generic row's SKIP / ADVANCE render
over W SET terms (MF_SITE_ABI 8), "one pinned file per strided shape" (the
`../r4h_target/` and `../n7_target/` precedent).

Each `<fixture>.c` (the name is its tests/memfn/arm_fixtures.c fixture,
table `STRIDES`):
- lines 1-3: a header comment naming the witness pattern and flags whose
  artifact the body was cut from, the hook texts and the shape;
- then the strided span loop EXACTLY as build/pcrec emitted it before M6
  (pcrec 00b1f3da), from its `while ((rx_span_cursor + W <= ...` line to
  its closing `        }` line;
- a `/* pcrec today:` line to EOF (here the body IS pcrec's text).

Checked by tests/memfn/run_arm_pins.sh check 12 (`make test-memfn-arms`):
the body must equal a fresh render of the fixture's `.use` (its `.def`
empty). A kit change that moves one re-freezes it on purpose, in the same
commit as its pins and its abi event. Shapes: adv-vmstride-it (possessive,
the caller's `it_` cap), adv-vmstride (possessive, unbounded),
adv-vmstride-lim (greedy, the MRL-folded `lim_`), adv-vmstride-u8w3
(utf8, W = 3), adv-vmstride-w32 (W = 32, the cursor rung's bound),
adv-vmstride-range (range-class members).
