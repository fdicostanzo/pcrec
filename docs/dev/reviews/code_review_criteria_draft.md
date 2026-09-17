# CODE REVIEW CRITERIA — DRAFT FOR FRANK'S PERSONAL EDIT

Status: DRAFT (manager, 2026-09-17, incorporating Frank's six seed
concerns + four manager additions from the same-day spot perusal).
Frank edits/ratifies this document personally before any review lens
launches (his ruling). Nothing below is binding until his mark.

## The initiative, restated

A full code review of the product tree, REPORT-ONLY first delivery:
ranked findings with file:line citations and concrete suggestions —
no refactoring in the review phase. Refactor waves follow in later
sessions ("after coffee and meditation"), backed by the test suite,
one criterion family per wave with a checkpoint battery between
(D102). Reviewers are opus-tier (sonnet wrote most of the code).
After the report, Frank takes a guided tour; the review handles the
easy stuff first.

## Scope tiers

- **PRIMARY: `src/`, `cli/`, `lib/`** (53,655 lines). All criteria.
- **SECONDARY: `tests/lib/`, `tests/harness/`** (infrastructure the
  suite stands on). Criteria 1-3, 6-8 only; test-code standards
  differ and say so per finding.
- **EXCLUDED (this round)**: emitted C (generated text — per-artifact
  duplication is by design), corpus `.rxt`/section scripts, `studies/`,
  `docs/`.

## Admissibility rules (every lens, every finding)

- **A1 — the ruled-record rule**: a finding that contradicts a
  decisions.md D-row, a design note's ruled section, or a recorded
  panel disposition must CITE it and argue against it explicitly, or
  drop. (Known live examples: D26's diagnostic-wording tier; k49fix
  §2.3's DELIBERATE twice-spelled boundary rule with an agreement
  check; limits.def as the ruled central-config home.)
- **A2 — the abstraction bar**: a duplication finding is admissible
  only with the SHARED ABSTRACTION named — proposed signature, the
  call sites it replaces, what varies per site. "These look similar"
  is inadmissible.
- **A3 — the check-coupling annex**: every finding cluster names the
  checks/anchors that bind to the code it would move (sabotage
  SAB_FILE/anchor greps, codegen text greps, abi-pinned scaffolding),
  so refactor waves price the re-aim burden up front. 261 sabotage
  anchors exist; a wave that moves anchored code carries its re-aims.
- **A4 — severity/effort vocabulary**: every finding carries
  severity (CORRECTNESS-RISK / MAINTAINABILITY / POLISH), effort
  (MECHANICAL / LOCAL / CROSS-CUTTING / DESIGN-EVENT), and blast
  radius (files touched, checks staled). The synthesis ranks
  MECHANICAL+safe first (the pre-tour cleanup), DESIGN-EVENT last.
- **A5 — evidence over vibes**: findings cite the metric artifacts
  (below) where one applies; a "this is repeated" claim cites the
  clone-detector row; a "too long" claim cites the census row.

## The eleven lenses (one opus lane each; Frank's 1-6 + 11, manager's 7-10)

1. **Semantic duplication / missing libraries** (Frank #1). Beyond
   textual clones: separable semantic operations — error paths, text
   handling, table emission, option plumbing — repeated with
   variation. Feeds on the clone-detector candidates but must judge
   semantics. Deliverable ranked by A2's named abstractions —
   these become the refactor waves' "common idioms" (Frank #4).
2. **Domain/tool separation** (Frank #2). "Teach the computer the
   skills": where does policy code inline mechanics that belong in a
   taught primitive? Known seed: the emitters use neither core/sb.c
   nor stdio — the tree appears to carry MULTIPLE text-emission
   mechanisms (sb, the emitters' own, the dump files', cli's raw
   fprintf). Map them; propose the one kit.
3. **Magic numbers, inline strings, config centralization** (Frank
   #3). Anchored to the EXISTING convention: limits.def is the ruled
   home — the finding class is "a number/string that should be a
   limits.def row (or a named constant) and is not," plus
   diagnostic-string formats that should share a table. Judgment
   calls marked as such.
4. **Clarity: naming, comments, structure** (Frank #4). BOTH
   directions per the spot perusal: munged/terse names where they
   hurt, AND the inline-archaeology problem — wave histories and
   panel citations living in code comments (emit_vm.c carries
   30-line change-history preambles). The art: invariants and
   why-not-the-alternative stay in code; HISTORY migrates to docs
   with a pointer. Function/section headers audited for presence and
   truthfulness.
5. **Unit-testing recommendations** (Frank #5). Where the suite's
   answer-level checks leave internal seams untested (helper-level
   properties a future refactor needs as a net): recommend targeted
   unit surfaces, citing what exists (the suite is
   integration-heavy by design — recommendations must not duplicate
   oracle coverage).
6. **Organization / dependency hierarchy / the rxt cut** (Frank #6).
   The include-graph and layering: is there a clean core→parse→ir→
   opt→gen order or cross-reference? VERIFIED deliverable, not
   prose: the dependency matrix from the metric artifacts PLUS a
   live link experiment — can a matcher-only consumer link
   libpcrec.a without rxt_source/rxt_compose/rxt_schema objects
   today; if not, the minimal cut. Serves the linkable-library use
   case directly.
7. **Comment hygiene / archaeology migration** (manager; the
   execution arm of lens 4's finding class — may merge into 4 at
   Frank's edit). Inventory of history-in-code by file, with the
   docs destination named per block.
8. **Error-path and cleanup consistency** (manager). The
   ctx_nomem/longjmp discipline, arena ownership, partial-state
   cleanup on failure paths — audited tree-wide, not only where K7
   forced it. Failure-injection thinking without running injections.
9. **Public-surface tightness** (manager). lib/pcrec.h is 1,072
   lines: what is contract vs leaked internal; what the library use
   case actually needs exported; PCREC_/RX_ prefix discipline.
10. **Emission-kit unification** (manager; lens 2's biggest single
    instance, broken out because it is likely REFACTOR WAVE 1 —
    everything sits on it, and one kit taught once makes waves 2..n
    cheaper. May fold into 2 at Frank's edit.)

11. **Function composition & altitude** (Frank, 2026-09-17, verbatim
    framing). C functions target a code-line limit — the rule of
    thumb is "fits on a screen" — BUT stated with its own warning:
    *"this is the kind of rule that can be perverted into doing
    violence against good design. It's a tool that can be used for
    good and evil."* So length is a TRIGGER, never a verdict: a
    function over N lines (N ≈ a screen; the census supplies the
    over-N population — emit_vm.c alone has functions at 300-527
    lines) gets reviewed against five questions:
    1. Is all the code at the RIGHT LEVEL — not too detailed
       (extract it) and not too general? A function's body should
       sit at roughly ONE semantic level.
    2. Is it all part of the same simple semantic purpose — and is
       that purpose clear from the NAME?
    3. Is it appropriately code-driven vs DATA-driven for what it
       does (a switch ladder that should be a table, or a table
       that should be code)?
    4. Are variations LOOPED rather than inlined N times?
    5. Are optimizations weighed — never taken at the expense of
       clarity and simplicity unless the cost is clearly understood,
       and *"if the code can't explain itself the comments should."*
    A long function that passes all five STAYS LONG, and the finding
    says so (the anti-perversion half). The editing principle governs
    the whole lens: *"Editing is equally as important as writing. Cut
    away everything that is not the elephant."*

## Metric artifacts (built first, by the tools/inventory lane)

Repo-owned python-stdlib scripts under `tools/review/` (no system
installs; reproducible both boxes; outputs committed as evidence):
function census (name/file/line/length/depth via ctags), token-shingle
clone candidates (winnowing), literal census (numbers/strings with
context), include graph + layer matrix, churn×size hotspots (git).
`gcc -fanalyzer` findings ride the existing `make lint`. Heavier
third-party tools (cppcheck, clang-tidy, lizard) require Frank's
explicit ok for machine installs — proposed only if the scripts prove
insufficient.

## Process

1. Frank edits/ratifies THIS DOCUMENT.
2. Tools/inventory lane builds the metric artifacts (sonnet).
3. The lenses launch (opus, read-only, 2-3 at a time vs the box and
   token budget), each citing metric artifacts per A5.
4. Manager synthesis: ONE report (docs/dev/reviews/YYYY-MM-DD-
   code-review.md), findings deduped across lenses, ranked per A4,
   the refactor-wave plan sketched (waves = lens 1's idioms, ordered
   by A3's check-coupling cost, emission kit likely first).
5. Frank's guided tour, with the report as the map.
6. Refactor waves in later sessions: one family per wave, checkpoint
   battery between, anchor re-aims travel IN the wave.

## Open for Frank at ratification

- Merge 7 into 4 and 10 into 2? (Manager's lean: yes for 7/4, keep
  10 separate as the wave-1 charter.)
- The secondary tier (tests/lib+harness): this round or the next?
- Machine installs for heavier static analysis: yes/no.
- Token appetite per lens (one opus lane each is the floor; lens 1
  and 4 may want two passes over the emitters given their size).
