# tests/callouts/ — module `callouts`' tests

**[INLINE-C] stage 1b, 2026-10-26.** `(?C)`, `(?Cn)`, `(?C"name")`: a call
out of the match to an `extern const rx_callout_ref` the user defines. The
contract is `docs/spec/match_api.md` §11; the design is
`docs/design/inline_c.md`. `make test-callouts` runs
`run_callouts_tests.sh` (mech arm `callouts`).

## Files

- `shapes.rxt` — the named shapes (D1/P7, P8, P9, P10, D2, the `(?s).*`
  start veto, the view shapes, an enclosing group, a consumer between
  literals, numbered callouts with `callout N ATTRS` lines, every string
  delimiter). Runs under `test-corpus` too.
- `harness.manifest` — `link stubs.c`: tests/harness/run.sh links the
  bindings into every driver built for this directory
  (`rxt_format.md` §6¶3).
- `behaviors.h` — the callee BEHAVIOURS, pure functions of the view, the one
  table both sides call. Numbered callout `n` binds check row
  `n % CO_NCHECK`; a consumer row carries the pattern text libpcre2 is asked
  in its place.
- `stubs.c` — the bindings (`rx_callout_<name>` per row, `rx_callout_0..255`)
  and the fire log the firing-class bound reads.
- `co_oracle.c` — libpcre2 10.46 driven with the same behaviours and its
  answer-moving optimizations off (`NO_AUTO_POSSESS | NO_START_OPTIMIZE |
  NO_DOTSTAR_ANCHOR`); `--default` asks at default flags.
- `verify_callouts.py` — this directory's own oracle (its NAME makes
  verify_rxt.py skip the directory): every `m`/`n`/`g` cell against
  co_oracle.
- `gen_diff.py` — the generated differential (floor 1,000 compiled and
  compared patterns; seeded) plus the firing-class bound per artifact,
  read off its own `--emit-ir` listing; populations counted and printed.
- `checks.c` — driver checks no `.rxt` cell can say: the view (A2, A4, A5,
  an enclosing group), give-up propagation and the tier, the step charge,
  DT-4.1, an artifact as a consuming callee, three traps.
- `run_callouts_tests.sh` — the six arms (corpus, oracle, differential,
  driver checks, class table + `once`, refusals); libpcre2 arms skip loudly
  when it is absent. `CALLOUT_GEN_N`/`CALLOUT_GEN_FLOOR` size arm 3.

## Rules

- Fire COUNTS are never asserted (§11.6); a class bound is.
- A new behaviour goes in `behaviors.h` (row order is the binding id order
  stubs.c logs by) and a binding in `stubs.c`.
