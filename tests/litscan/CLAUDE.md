# tests/litscan — [OPT-LITSCAN]'s answer-level corpus

The literal-compare kit's (`docs/design/compare_stack.md`) `.rxt` net. Run by
the harness like every other corpus directory (both engines), so a pattern
here is answered by the DFA and by the VM, and the VM side reads the kit's
emitted compare.

## Files

- **litrun.rxt** — S2a (`docs/design/patfacts/design.md` §8.2): the VM's EXACT
  literal run as one constant-length `memcmp` (`pcrec_lit_run`,
  `src/core/cpset.c`; `docs/spec/tuning.md` §2.31). The shapes the mechanism
  must get right: a run ending exactly at the subject's end and one byte
  short of it (P8's `pos + L <= n`), bytes the emitted C string literal must
  escape (quote, backslash, `?`, NUL, control and high bytes, an octal escape
  before a digit), a run beside a capture, a choice point, a star, a repeat
  and a lookahead, and the island's single-child chains. **[OPT-LITSCAN F5,
  D127, 2026-09-28]** the floor moved from two bytes to three, so `ab` now
  demonstrates the declined byte-chain form and `abc` is the new shortest
  compare witness; the run-before-a-choice-point block widened from
  `xy(a|ab)c` to `xyz(a|ab)c` for the same reason. `xyz(a|ab)c` is also
  `tests/codegen/run_ir_listing.sh`'s witness for sabotage S305; the blocks
  that put a non-literal element after a run are S304's detector.
- **gen_litrun.py** — writes `litrun.rxt`; every expectation comes from
  python3 `re`, never by hand. Edit the case list there, not the `.rxt`.

Maintenance: update this file when files are added/removed or change roles.
