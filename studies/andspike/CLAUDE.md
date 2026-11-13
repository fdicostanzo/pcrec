# studies/andspike/ — PCRE2-callout exact-span oracle spike (lane andspike, 2026-11-12)

STUDY CODE, never product: a Python ctypes oracle that answers "does X match
exactly [i, j) of S?" and "which ends does X reach from i, in X's preference
order?" with PCRE2 itself (an end callout that fails or accepts), and builds X & Y
and "the match where a predicate holds" on top. Nothing here is built by
`make`, run by `make test`, or linked into pcrec. Report:
docs/dev/lanes/andspike_report.md. PCRE2 SOURCE IS OFF-LIMITS (D181): the binding
is written from the installed pcre2.h and the man pages only.

## Files

- `p2cb.py` — minimal libpcre2-8 binding with callouts (default: the 10.49 oracle
  build under `$PCREC_TMPDIR/oracle/`; `ANDSPIKE_PCRE2` overrides).
- `spanoracle.py` — the oracle: `ends`, `spans` (in-context or isolated), X & Y as
  `and_sets` (enumerate then check) and `and_inline` (one PCRE2 run, nested check),
  `pred_match`, and the callout-free routes `plain_first`, `lookahead_order`,
  `lookahead_spans`. `ANDSPIKE_SABOTAGE=order|drop|pred` are the controls.
- `refmatch.py` — an independent backtracking reference matcher (regular subset)
  and the random pattern generator.
- `cases.py` — the hard cases with hand-derived expectations (+ PROBE rows).
- `sweep.py` — `cross` (oracle vs re / refmatch / callout-free PCRE2) and `laws`.
- `predicates.py` — the predicate evaluator, demos, and the sweep vs refmatch.
- `cost.py` — enumeration cost on catastrophic patterns, and the bounds.
- `results/` — committed outputs. `Makefile` reruns them (niced).

Run: `make -C studies/andspike` (about a minute or two on the Linux dev box).
