# rlhtri report (2026-10-11, sonnet) — test-encoding-checks red on lane/rlhbuild

Two FAIL lines, ONE cause, class: stale test expectation moved by the
branch's intended mover (kit R-15's memchr ASSIGN rendering of the handoff
gate). No answer/semantics regression.

- `DD12a(i) 19 of 245 strict-identity pairs differ OUTSIDE the named
  encoding-owned regions` (patterns `\Z`, `a*\Z`, `(?m)^a`, ...) and
  `DD12a(i) [K50] the undeclared-form exception list does NOT match`
  (14 reached-and-diverging vs 8): `excise_handoff` in
  `tests/codegen/run_encoding_checks.sh` excised the ASSIGN line
  `size_t handoff_position = ({ ... });` only with the old 3-line miss test
  (`if (... == (subject_length)) {` / `return 0;` / `}`). R-15 renders the miss
  as the single line `if (handoff_position >= subject_length) return 0;`,
  which was left behind on the utf8 side (byte side has no handoff for
  byte-keyed-prior patterns), so those pairs differed in the hot path. The
  K50 list failure was the same pairs showing up as extra STRICTPAT rows.

Fix: `excise_handoff` accepts the one-line miss test after the ASSIGN line
(4 lines, no pin/manifest change needed).

Re-run: `make test-encoding-checks` under taskset -c 12-15, log
build/tri/enc.log: `checks passed: 11, checks failed: 0`; the verdict grep is
empty. `make strict` clean.
