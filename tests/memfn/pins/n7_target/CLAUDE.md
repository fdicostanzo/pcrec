# tests/memfn/pins/n7_target/ — M7's frozen MISMATCH target

Lane m7, 2026-10-08 (report: docs/dev/lanes/m7_report.md). RULED Q-R8-9:
the generic row serves the encoding seam's exact and expression-fold span
compares and the row `mismatch_inplace` its in-place fold, "each with a
pinned target file checked byte for byte" (the `../r4h_target/`
precedent).

Each `<fixture>.c` (the name is its tests/memfn/arm_fixtures.c fixture):
- lines 1-3: a header comment naming the witness pattern and flags whose
  artifact the body was cut from, the hook texts and the indent;
- then the compare loop of the residual entry (`rx_span_match` or
  `rx_span_match_caseless`) EXACTLY as build/pcrec emitted it before M7
  (pcrec 1adead14), from the line after the function's `{` to the line
  before its `    return (ptrdiff_t)reflen;`;
- a `/* pcrec today:` line to EOF (here the body IS pcrec's text).

Checked by tests/memfn/run_arm_pins.sh check 10 (`make test-memfn-arms`):
the body must equal a fresh render of the fixture's `.use` (its `.def`
empty). A kit change that moves one re-freezes it on purpose, in the same
commit as its pins and its abi event. Shapes: mm-exact, mm-ucp-expr,
mm-ascii-inplace.
