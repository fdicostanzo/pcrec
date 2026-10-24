# recpin report: test-recursion-identity (A) after corefix (K128), 2026-10-23

STATE AT HANDOFF: PARTIAL. (B) FILEPIN re-pinned; (A) NOT re-pinned, stopped on a finding.

## What was run
- main (c7f782cd5), `make test-recursion-identity`, KEEP=1. First failure was NOT (A): the (B) file pin
  `813f43ec8` stamps abi 82, subject abi 83 (corefix_report.md "At merge" listed the re-pin as owed).
  Re-pinned FILEPIN to the corefix merge `bf33d2dab` (D76). (B) then passes.
- With (B) green, (A) reproduces the manager's facts exactly: differing default 78 / vm 126 / noprefilter 78 /
  nocaptures 54; bref-rename bucket 366 vs text census 411 (band +-30).
- Baseline at `bf33d2dab^1` (32036bd39), same gate in a scratch worktree: (A) differing = 9 on every axis,
  bref bucket 401 (in band), plus "25 call-FREE patterns accepted by one build and refused by the other" and
  "9 call-free patterns emit DIFFERENT bytes" FAILs. So the gate was already red before corefix.

## Cause split (default axis, 78 differing)
- 69 carry K128 text (marker comments "the last mandatory iteration: record where it began" / "unbounded
  repeat: entered after the mandatory iterations"). base-vs-post (`bf33d2dab^1` vs `bf33d2dab`) sample:
  K128 adds the lastg guard write + entry test, renumbers labels (extra hop labels), and on the counter
  rung splits the old shared guard/counter slot (old RX_SLOT_COUNTER0 doubled as the guard; new
  RX_SLOT_EMPTY_GUARD0 + COUNTER0, slot_values indices shift) and can swap guard numbering
  (`(b*?(a*)*)+`: GUARD0/GUARD1 and slot 6/7 swap).
  Scratch awk canonicalizer (strip K128 lines, merge adjacent labels, renumber by first appearance):
  64/69 EQ base-vs-post; 5 NEQ = `(?:a|()|b){8,}?c`, `{9,}c`, `{16,}?c`, `{17,}?c` (counter-rung slot split) and
  `(b*?(a*)*)+` (guard slot order). Remaining work for a ninth exception: slot-name/index handling for
  those, or a hand manifest of the counter-rung movers.
- 9 do NOT carry K128 text and are NOT K128: `(?U)a*+`, `(?U)a++`, `(?U)a?+`, `(?U)a{2,3}+`, `(?U)a{2,}+`,
  `(?U)a*+a`, `(?U)(a|b)*+`, `(?U:\s*+)b`, `a(?U)\s{,2}+`. Same region (empty, DFA) at base, post and main;
  they are the pre-existing 9 at `bf33d2dab^1`, together with the 25 accept/refuse mismatches.

## Not done
No (A) exception added, no band moved. Pre-existing (?U)-possessive failure needs a ruling first.
