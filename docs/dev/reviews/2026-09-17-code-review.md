# THE CODE REVIEW — synthesis (2026-09-17)

Charter: `code_review_criteria_draft.md` (RATIFIED by Frank 2026-09-17,
two addenda). Sources: eleven opus lens reports + the chartered
`emit_vm.c` second pass (EP2), all in `lens_reports/`, normalized by
`lens_reports/synthesis_collation.md` (the collation carries the full
findings table, the eight overlap clusters, and the master
probed-and-held list — this synthesis RANKS and DECIDES; on any
disagreement between a lens report and this file, this file wins, per
the lens_reports CLAUDE.md).

Process telemetry, for the record: 12 review lanes + 1 tools lane +
1 collation lane, all delivered, zero deaths; the tools lane's metric
artifacts (`tools/review/`) were cited by every lens per A5; the second
pass was formally triggered by lens 1 and sequenced by lens 10, as the
charter's own second-pass clause intended.

## 0. The verdict in one paragraph

The tree is healthy where sonnet lanes have been building under panel
review — and the lenses PROVED that in both directions, which is the
review working as chartered: the median function is 10 code lines
(L11), the error-discipline holds at 75 of 76 allocation sites (L8),
the public header leaks no internal type (L9), there is no include
cycle (L6), and the archaeology is three concentrated blocks, not a
diffuse rot (L4). The real findings cluster in FOUR places: (1) a
handful of missing taught primitives each re-implemented dozens of
times by hand (the walk discipline ×75, the prefix interpolation ×652,
the growable array ×~28, the scratch-buffer sizing ×58+); (2) the
emitters' interior — 44% of all sabotage anchors, the tree's longest
functions, and the fragment-buffer population, now mapped by EP2;
(3) INSTRUMENTS that cannot see what they claim to guard (five
independent instances, §5 — the review's most valuable output);
(4) a small set of genuine correctness items, all cheap (§2).

## 1. FIX-NOW — the pre-tour cleanup

Ranked MECHANICAL+safe first per A4. Each is one commit, independently
validatable, staling zero or trivially-re-aimed checks. The collation
§4 carries the full table; the order here is the recommended landing
order.

1. **L8-F1** — attach the Ctx back-pointer to `Job.scr_test`/`scr_desc`
   (one line beside the existing four; reword the "four Job buffers"
   comment to state the rule, not the count). Closes a live
   caller-`abort()` reachable from ordinary VM-route patterns under
   allocation failure. CORRECTNESS-RISK; lands first, independent of
   everything.
2. **L5-R0.2** — add `run_cpset_structure.sh` + `run_mrl_tests.sh` to
   `tests/lib/san_scripts.txt` (2 lines). The tree's best unit check
   has never run under ASan.
3. **L9-P2 (+P7, P8 riding)** — `lib/pcrec.h` header sweep: utf8 is
   shipped (R29's class recurring); `RX_NCAPS`→`<PREFIX>_NCAPS` in
   contract prose; delete the never-true "order of magnitude" clause.
4. **L8-F2 + L8-F5** — `cli_parse`/`apply_target` libdirs leak on the
   failure exits; `write_file`/stdout `ferror()` coverage (`-o -` to a
   full disk currently exits 0 having written nothing). L10-L10-8 is
   the same ferror finding — one commit discharges both cites.
5. **L3-F3** — the FNV-1a constant pair, 9 open-coded sites → one
   helper pair. Zero checks, zero emitted bytes (dfa.c's own comment
   establishes the hash reaches no artifact).
6. **L3-F5** — "missing closing ) for group" to one `#define` (8 sites
   + the ninth undeclared home in `registry_check.c:1482`), and correct
   the parse.c:1902 comment whose "a module owns a DIFFERENT message"
   half is measurably false. NOT a wording change — D26 untouched.
7. **L4-C1 (+C2)** — headers for the 43 ≥50-line functions with none
   (the eight longest in the tree included); move `emit_attempt`'s
   misplaced banner. Cheapest MAINTAINABILITY win in the review; zero
   checks staled. C2's banner move is comment-only but sits in
   emit_dfa.c — verify no SAB_BEFORE quotes it (EP2's method: grep,
   then keep columns).
8. **L6 §5 step 1** — the `-Wl,-dead_strip` doc hunk in match_api.md
   §8.0's worked example (43,968 of 44,448 rxt-tier bytes recovered for
   every consumer who copies it; D80 hunk).
9. **L4-A2** — the one stale superseded-claim-in-present-tense
   (select_engine.c:496), one clause.
10. **L1-X2** — merge `cg_walk`/`pr_walk` into `pcrec_ast_visit`
    (byte-identical pair; 2 caller-text sabotage re-aims, grep-found;
    narrow the src/opt/CLAUDE.md sentence it contradicts per A1). This
    is the PILOT for X1 and deliberately last in the fix-now list —
    it's the first item that moves src/ logic, and its green battery
    is the method proof for wave 2.

## 2. Correctness-risk register

Everything any lens filed at CORRECTNESS-RISK, with the synthesis
disposition:

- **L8-F1** (caller-abort) — FIX-NOW #1 above.
- **L9-P1** (12 unprefixed exported symbols; reproduced duplicate-symbol
  link failure) — RULED same day (D104): renames name-by-name, wave 5.
- **L1-X3** (mrl/vm saturating arithmetic macro-identical, nothing
  checks agreement) — the CODE dedup is MECHANICAL and lands in wave 2;
  the AGREEMENT CHECK is L5-R2 and lands in the nets wave (§3 wave U).
  X3's `CG_EXP_INF` rider joins L5's sharper version: limits.def:358's
  own `where` text names callgraph.c, which re-declares the value —
  one-line fix rides the dedup.
- **L2-L2-1 / L10-F3** (fragment buffers, K38 class) — L10's
  measurement DOWNGRADES to latent (zero provable truncations today,
  tightest margin 9 bytes); retirement is wave 2's stage 3. The
  [MECH-REACH] finding that the only long-prefix control compiles
  pattern `a` files NOW as a check-design issue (§5) regardless of
  waves.
- **L3-F1** (name-keyed limits detector blind spot) — §4 Q6; my
  recommendation is the inversion, it is cheap (14 classified lines).
- **L8-F6** (ctx_nomem discipline has zero sabotage rows; Darwin skip
  means the only positive control hasn't run on the dev box since the
  Mac move) — nets wave; the injector tier disagreement is DECIDED
  (§4, manager row M2): L5's measured LOCAL shape wins over L8's
  assumed DESIGN-EVENT, because L5 specified the mechanism
  (`-include` header + separate BUILD_DIR, the `make ubsan` shape one
  axis over, zero src/ edits) and its acceptance case ("red on F1
  unrepaired") is the failing-direction story the check-design record
  demands. Staged behind F6(a)/(b).
- **L4-A1** (the abi change log in three drifting homes, two
  transitions recorded nowhere) — its own reconciliation-plus-D80
  change, LAST in the wave order per lens 4's own sequencing; a
  maintainer working D76/D94's ritual reads an incomplete record today,
  which is why it outranks its "docs" appearance.

## 3. The wave plan

Waves are one criterion family each, checkpoint battery between
(D102), anchor re-aims travel IN the wave. Two method rules now bind
every wave brief, from EP2 and lens 11: (i) anchor populations are
FLOORS found by `grep -rl <identifier> tests/mech/sabotages/` on the
wave's OWN tree (rows quote CALLERS; ~24 rows' text has already
drifted); (ii) `replace.py` matches whole-file/line-agnostic, so a
verbatim relocation is free and RE-INDENTATION is what breaks anchors —
briefs price "does the moved text keep its column."

- **Wave U (nets first)** — L5-R0 name-the-tier (`unit_cc.sh`, san
  membership, tests/core/), L5-R2 the sat-arithmetic agreement check,
  the allocation-failure injector (M2), L8-F6(a)/(b)/(c) repairs
  (grep-derived census + a steered positive control). Nets precede the
  refactors they exist to catch.
- **Wave 1 (emission kit, outer stages)** — lens 10's stage 0
  (long-prefix full-corpus sweep + EP2's two additions: the
  irsb/run_ir_listing.sh byte-neutrality arm and the listing-reach
  census) then stages 1-2 (dump row/field layer, 2 anchors; CLI
  channel, 0 anchors, D26 keeps every word). Template layer stays
  CLOSED (L10's measurement; population 1). sb_join fixes the
  render_modules out-of-order bug in passing — it is a bug fix, not a
  cleanup. **D108 (Frank) is a wave-1 design constraint**: the kit's
  primitives take DATA and produce TEXT (never reach into the live
  walk/Ctx/DFA), and the walk->event->render boundary stays clean (the
  renderer consumes the event stream, not a re-walk) — so the future
  IR-consuming back-end (D106 item 5) reuses this text layer and render
  path unchanged. Non-foreclosure only; costs the kit nothing today.
- **Wave 2 (emit_vm.c interior)** — EP2's 16-step sequence is the
  authoritative order (it reconciles and corrects lens 11's four-commit
  proposal in three measured places). Opens with the zero-anchor moves
  (E1 `vm_slot_ref` first — retires 8 of the 40 category-(a) buffers in
  one edit; then E0/E2/E3/P1/P2/P4), closes with lens 10's stage 3
  (fragment retirement) under the REPAIRED acceptance criterion (EP2's
  three sizing categories, floor 58/66 for emit_vm.c — the emit_dfa.c
  third-category census runs first, follow-on register item 19).
  X8 (stamps) rides stage 3 (§4, manager row M1). emit_vm.c:8165's
  listing truncation is §4 Q3, decided before this wave's stage 3.
- **Wave 3 (layering)** — lens 6's L1+L3 LAND TOGETHER (enc/ →
  src/enc/ + the base/driver layer model in tool and prose) or the
  instrument reads a false zero while 39 call-level back-edges stand;
  the rxt minimal cut (2 files, 0 anchors, verified by stub); L4-dump
  relocation as the mechanical rider; internal.h declaration-grouping
  (the mechanical first step, split deferred).
- **Wave 4 (CLI + config)** — the cli_parse table (L11's 59-arm guard
  repetition + L2's rank 1 + L1-X10 are one item), the mode
  mutual-exclusion relation written once, L3-F1 filter inversion (per
  Q6), F2/F4's chosen dispositions, X9/axes.def as the one
  design-event candidate this wave PROPOSES but does not build (its
  A3 cost inverts — it deletes two checks — which is the argument for
  bringing it to Frank rather than for building it unruled).
- **Wave 5 (public surface)** — L9's §8 order; the P1 half is ruled
  (D104: renames name-by-name, nfa_* first) and unblocked; the P3/P6
  spec hunks can ride any earlier wave's D80 batch.
- **Last** — L4-A1's abi-log reconciliation as its own change.

**Added deliverable (Frank, 2026-09-17, at the Q1 ruling):** a WIRED
CODING GUIDE — `docs/dev/coding_guide.md`, the review's findings
distilled into the rules a code-writing session follows (house
disciplines, taught primitives in their current state, emitted-text and
anchor-column rules, the altitude rubric, check-writing rules, the
do-nots), wired into the process by a root-CLAUDE.md situation-index
row and a BOILERPLATE.md line so writer lanes read it before their
first edit; rules that a wave will change are marked with the wave
name. Chartered to lane codeguide same day.

Second passes named but NOT chartered (collation §6, nineteen items):
the ones I endorse chartering when their wave arrives are lens 5's
second pass starting at rxt_source.c's total string functions (K57's
shape), the emitted-artifact public surface (L9's other-half), and
the L7-alternation-island mech question (a substantial layer with zero
sabotage anchors is a coverage cell, not a curiosity).

## 4. Rulings

**For Frank** (each carried in the citing report's own words in
collation §3):

- **Q1 (L9-P1)** — **RULED (Frank, 2026-09-17, same day): option A**,
  now D104 — renames land name-by-name, nfa_* first, ctx_fail last;
  localization refused (D2 + archive-member granularity + it hides
  rather than fixes); deliberate export control deferred to L9-P5's v1
  trigger. Wave 5 is unblocked.
- **Q2 (L8-F3)** — **RULED (Frank, 2026-09-17, same day): refuse via
  ctx_nomem**, now D105, with Frank's algorithm rider taken: the fix
  RESTRUCTURES rather than reroutes — `path` becomes a fixed 40-int
  local (the unbounded allocation is deleted), the BFS scratch moves to
  the arena (failure routes through ctx_nomem by the existing general
  mechanism; the bespoke failure path is deleted), brief mode halves
  the scratch. Not an abi event; byte-identity emit-diff is the bar.
  Joins the FIX-NOW wave.
- **Q3 (L10-L10-6)** — is the --emit-ir listing's column width contract
  or free? Decides whether emit_vm.c:8165's slot[48] truncation is a
  bug fix or a formatting change when the buffer retires.
- **Q6 (L3-F1)** — invert the limits detector filter (scan ALL numeric
  defines; classify the 14 currently-invisible ones) vs widen the
  vocabulary a third time. Manager lean: invert; the widening path has
  now failed twice by the check's own comment.
- The X9/axes.def design event (wave 4) when its proposal lands.

**Manager rows** (decided here, re-openable):

- **M1** — X8 rides lens 10's stage 3 (shared 123-anchor blast radius;
  lens 10's recommendation accepted).
- **M2** — the injector is LOCAL, L5's shape (measured mechanism beats
  assumed tier; acceptance = red on F1 unrepaired).
- **M3** — L1-X9 and L2's rank-2/rank-1 CLI items are ONE cluster,
  counted once (wave 4).
- **M4** — L6-L3 stays a model fix (tool + prose), no compile.c file
  move (the lane's own D77 argument accepted).
- **M5** — the growable-array population for wave planning is L5's 13
  by census, with L11's 28-doubling-sites figure noted as the count of
  SITES rather than of extractable arrays; the extract (X5) prices
  against 13 named arrays and the wave brief re-runs the census.

## 5. Method findings — for learnings.md §3 and the check-design memory

Five instrument findings, each the controls-share-a-source /
population-nobody-counts shape, found by DIFFERENT lenses on DIFFERENT
surfaces — this convergence is the review's strongest argument that
the shape is systemic and worth its standing memory entry:

1. L3-F1: the limits detector filters by ceiling-vocabulary in the
   NAME; the repair after its first miss widened the vocabulary
   instead of changing the filter's kind, and the miss recurred.
2. L6-L2: the include-graph instrument cannot see 31 of 39 call-level
   back-edges because internal.h declares everything — the metric
   artifact and the architecture route through the same header.
3. L10 §2.2: the only long-prefix control compiles pattern `a`,
   reaching essentially none of the 48+ buffers it exists to guard
   ([MECH-REACH]'s shape, found by measurement).
4. EP2 (a): lens 10's stage-3 acceptance criterion would pass with the
   third sizing category untouched — the K35 shape appearing INSIDE a
   criterion written days earlier to retire an instance of it.
5. L8-F6(b): the ctx_nomem positive control is Darwin-skipped, so the
   discipline's only detector has not run on the dev box since the
   two-machine split — and F1 shipped in exactly that window.

Also standing: anchor counts are floors (L11/EP2); population counts
differ by instrument and are never citable as site lists without
re-running (L10 §2.4, the 94/49/48/58 buffer family and the
10/7/13/28 array family being the worked examples).

## 6. What was probed and held

Collation §5 is the do-not-reopen record. The entries most likely to
be violated by an eager future wave, restated: the nine atomic.c
predicate walks do not merge (only the traversal extracts); the rung
emitters stay code-driven (EP2 §6, the table would have to carry the
CFG); the four syntax_dump enum mappers stay as they are (D82 bound 3
+ D75); the emitters' single-letter locals are house convention
(L4-P1/L11); the denial bits stay public (D46/D47.3); the 56% comment
ratio is not a finding; the template layer is closed by measurement,
not deferred.

## 7. Reflection

The charter's two addenda earned their place: addendum 1's loop caught
a false join row (X8→vm_render_listing, refuted by L11's own count)
and addendum 2's no-silent-caps rule produced the stopped-at sections
that made the second pass a charter rather than a hope. The report-only
discipline held — twelve lanes, zero src/ edits. The largest residual
risk is not any finding but the FLOOR nature of every anchor count;
the wave briefs carry that rule so it cannot be lost. Three lenses had
their headline seeds refuted by measurement (L2's "emitters don't use
sb", L4's "30-line preambles", L5's "no unit tier exists") — the
charter survived its own author being wrong three times, which is what
A5 is for.
