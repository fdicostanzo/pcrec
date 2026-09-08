# r55 — [TT-4M] 2a/2b panel: the parallel-sizing memo + the harness-batching design note

2026-09-08, fifty-seventh session. Two read-only sonnet critics on the
MERGED deliverables (lane tt4m2, merge on main): `r55num`
(method/numbers lens) and `r55harn` (harness-reality lens — read all
~1,700 lines of run.sh, driver.c, the SIZELOG/tripwire pair, the axis
wiring, all 13 sabotage candidates, tests/codegen). Verdict up front:
**the eight design decisions hold against the real tree; the
recommendation N=64/P=8 stands; but 2c is BLOCKED until the revision
below lands** — one specification gap, one guard-dilution hazard the
note's own §3 names for a different surface, one foreordained-result
framing, one phantom citation, and one tooling attribution bug.

## Findings and dispositions

### Blocking / must-fix (the revision lane's charter)

**R55-1 (harn-1, MUST-FIX) — routed blocks fall through the batching
unit.** Item 1 excludes only `perr` and H11 blocks from batching; item
2's dispatch.c is default-route-only; nothing keeps a `frames-buffer=`
block (needs `_search_in`/`_match_in`/`_match_caps_in`;
driver.c:222-261/:382-426) out of a batch. Live population:
tests/recursion/framebuffer.rxt's `^(a(?1)?b)$ / engine vm` block, 9
directives. DISPOSITION: amend items 1+2 — a block carrying ANY routed
cell (`frames-buffer=`, and enumerate the route grammar from
parse_route, not just the one spelling) is excluded from batching
exactly as perr/H11 are, detected per-block at parse; the fuller
dispatch driver stays a later increment. 2c's brief carries the
exclusion explicitly.

**R55-2 (num-F2, MUST-FIX; + num-F3 resolved by the same edit) — the
N-scaled D45 budget dilutes the guard D45 exists to be.** `N ×
gen_cpu_secs()` lets one pathological compile (D45's own motivating
incident) run ~N× its own budget before the ceiling fires — the exact
dilution mechanism the note's own §3 flags for SIZELOG's tripwire,
unrecognized in §6. And §6's one-wrapped-invocation shape contradicts
§3's N × `-c` + link shape without defining how the wrapper composes.
DISPOSITION: rewrite item 6 on option (a)'s own structure — the D45
wrapper applies PER `-c` SUB-COMPILE at the UNSCALED per-pattern
budget (strictly better than today: same guard, fewer processes), the
link step gets one additional unscaled budget, and the batch-level
N-scaled number survives only as an outer backstop, stated as such.
S43's scaling note updates to match.

**R55-3 (num-F1, BLOCKING) — the N=128/P=12 starvation was
foreordained by the pool, and three documents call the pool
"meaningful" for that cell.** The memo's own arithmetic wants 1,536
patterns for one-batch-per-worker at that cell; the pool is 1,022 → 8
batches for 12 workers by construction. DISPOSITION: reframe in the
memo + report + docs/dev/CLAUDE.md — the cell demonstrates the
starvation MECHANISM (real, and worth keeping) but is not an emergent
sizing discovery; either mark it so, or enlarge the pool and re-run
that one cell (optional — the N=64/P=8 recommendation does not rest on
it; re-run only if the box is free, coordinate with the manager).

**R55-4 (num-F7, BLOCKING as documentation integrity) — phantom
citation.** Item 1 cites a per-file block-count census (1-357, mean
18.7 over 207 files) to the 2a memo's pool-sizing section; the memo
contains no such numbers. DISPOSITION: run the census for real (it is
one grep-and-count pass, read-only), archive the raw numbers where the
citation points (or a small evidence file), and correct the mean if it
moves. A number in a design note traces to data or it comes out.

**R55-5 (num-F4, MUST-FIX) — extract_cases.py attributes cases by
pattern TEXT alone**, so two same-text blocks with different
flags/features (54 files carry the shape) both receive the FIRST
block's cases. Headline wall/CPU/knee cells and the zero-mismatch
identity claim survive (same population reused identically per cell),
but the 7.56-cases/pattern density claim and the module-diversity
framing do not hold as stated. DISPOSITION: fix the keying to
(pattern, flags, features) or block ordinal; re-derive and restate the
density line; one-sentence caveat in the memo naming what the fix
changed. learnings.md §3's exact "population nobody counted" shape —
cite it in the caveat.

### Notes (ride the same revision commit)

- **R55-6 (harn-2)**: dispatch_gen.py's "decode() byte-identical to
  driver.c's" is false on a trailing lone backslash (driver errors,
  study emits literally). Fix the code to match driver.c AND the
  claim; population ~zero today, the claim is the defect.
- **R55-7 (harn-3)**: item 5 should say `SAB_FILE=`-anchored, not rows
  "naming" run.sh — a raw name-grep returns 13 and invites a false
  recount (the critic walked into and out of exactly this).
- **R55-8 (num-F5)**: the 18.65x contention caveat must also name its
  DIRECTION (baseline contention inflates the ratio favorably).
- **R55-9 (num-F6)**: "~1.5-1.7x" → the table's true 1.48-1.66x.
- **R55-10 (num survived-attack NOTE)**: 2a's raw sweep evidence was
  scratch and is not archived — unlike this house's other measurement
  lanes — so no 2a number can be independently re-checked. DISPOSITION:
  state the gap in the memo; 2c/2d MUST archive their own acceptance
  numbers under a docs/dev evidence dir (the flip-to-default-on
  decision rides 2d's fresh archived numbers, not 2a's scratch).

### Survived adversarial verification (recorded so nobody re-litigates)

The P=8 knee cell-by-cell; CPU-vs-P monotonicity (15.45% max at N=16);
the 18.65x composition caveat present at every citation; K44 hedging
honored everywhere; the tab-drop disclosure consistent; SIZELOG option
(c) structurally unavailable (Makefile threads SIZELOG through every
full-corpus run — independently confirmed); all axis wiring as
described (GENCFLAGS one variable into gen_cc; RXTFLAGS reaches
$PCREC, settled before gcc); exactly 8 SAB_FILE-anchored rows, none on
the compile/link line; gen_cc's CCACHE split-then-link already runs a
compile SEQUENCE under one budget (the precedent §6's rewrite builds
on); driver.c protocol reproduced correctly for the default route;
tests/codegen//reject/PC-3 genuinely out of reach of flush_block.

## Outcome

Revision lane `tt4m2f` (sonnet) charters R55-1..9 as one commit
(+ optional R55-3 cell re-run, box permitting); R55-10's archive
requirement moves to 2c/2d's briefs. **2c opens on the revision's
landing**, its brief carrying: the routed-block exclusion (R55-1), the
per-`-c` D45 composition (R55-2), and the evidence-archiving bar
(R55-10).
