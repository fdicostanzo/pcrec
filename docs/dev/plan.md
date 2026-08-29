# pcrec Project Plan

Working plan derived from ../../APPROACH.md. Milestones M0–M7 mirror APPROACH §9.

## Step-state format (grep'able)

Every step line matches exactly:

    - [Mx.y] STATE:<state> — <title>

States: `not-started` | `started` | `completed` | `blocked` | `deferred`

Find work:

    grep -n "STATE:started" docs/dev/plan.md
    grep -n "STATE:not-started" docs/dev/plan.md
    grep -c "STATE:completed" docs/dev/plan_completed.md

Completed rows are archived in docs/dev/plan_completed.md (this file keeps
zero STATE:completed rows; a completed-count grep here counts nothing but
recipe text).

Rules: update the STATE tag in place when a step changes state; expand a milestone
into substeps only when work on it begins (replace its single `[Mx.0]` line);
note blockers inline after the title with `(blocked: reason)`.

## Queue discipline (Frank, 2026-08-12)

**The BOONIES TIER sits well after the general work.** [M4-CALLOUTS],
[M4-SUBST], [V-E], [V-F], [SR-10] and their kin are PARKING SPOTS, not queue
positions: recorded so nothing is re-derived, started only after the spine —
M3 streaming, M4 captures + backtracking VM engine, M5 UTF-8, M6 feature
modules, M7 differential fuzzing — is done, unless Frank explicitly pulls
one forward. A boonies row growing substeps while spine rows sit not-started
is the smell this note exists to stop.
(Spine order re-ruled 2026-08-13: STD1 → M4 → M5 → M6 → M3 → M7 — see
"Development order" below.)

## Lane structure (Frank, 2026-08-29 — D86)

Lanes are TYPED, within the 3-concurrent ceiling: one FEATURE lane
([DD-13b]/[LIB], [DD-12]/[M5] UTF, modules), one OPTIMIZATION lane
([OPT-*], [ENG-PGO]; from the bench's outliers, measured need first),
and one ADMINISTRATIVE/STRUCTURAL lane AS NEEDED ([DD-11], [SPEC-1]
lanes, checks, doc consolidation) when a row is available and nothing
of higher priority wants the slot. A closed lane's successor comes
from the same column. Rows still open on Frank's word.

## Development order (ratified 2026-08-13)

The spine, in this order, one line of rationale each (full session rationale:
dev_journal.md 2026-08-13, sixteenth session):

- **[STD1]** — its suite re-baseline only widens with time; land it before
  anything else queues behind it.
- **M4 — captures + backtracking VM engine** — the biggest user-visible gap
  (captures) and the owner of the most parked decisions ([DD-2], [DD-7],
  [DD-9], [SR-8]).
- **M5 — UTF-8** — before M6, so feature modules are born CharSet/UTF-aware
  ([DD-12], [DD-1]) instead of being rebuilt once UTF lands.
- **M6 — PCRE feature modules** — lookaround, backrefs, atomic groups,
  named-groups, conditionals, recursion. The assertions module is the one
  M6 piece that needs no VM — a flexible slot, schedulable whenever a lane
  is free.
- **M3 — streaming input** — moved to last-but-one because its API must be
  designed once against the FINAL engine+feature set ([OS-3]'s evidence —
  lookbehind/backref window retention); building it earlier would mean
  rebuilding it.
- **M7 — hardening** — differential fuzzing was already pulled forward (to
  M2); the residue is testdata import and the freestanding/embedded
  profile.

Sequencing notes: the backrefs / atomic-groups / substitution-template
design notes (under M4 below) should be WRITTEN BEFORE M4 starts — they are
M4's design customers, and the substitution template compiler is
matcher-independent (Frank, 2026-08-12), so its design note need not wait
on M4 either. After M7, [BENCH-1] builds the feature-spanning benchmark +
prioritizer; then the OPT waves open, [MECH-3] first, with the prioritizer
setting the work order.

## Next: M4 (milestones start with Frank)

[STD1] completed 2026-08-13 (seventeenth session) — archived in
plan_completed.md. Per the ratified order M4 is next, and all three
pre-freeze design inputs are now LANDED AND RULED (D38, eighteenth
session, 2026-08-14): the [PC-5] flag-disposition table landed (merge
258fd79) and its dispositions are ruled wholesale, archived at
plan_completed.md's 2026-08-14 group; the subst-template design note
merged 3d5a9e8 with all fourteen of §9's questions fully ruled
(docs/design/subst_template_design.md); the M4-CALLOUTS callout-ABI
alignment proposal has its rulings applied
(docs/design/design_callout_abi.md) with only the syntax spelling (§6 Q5)
and the embedded-code restrictions (§6 Q6) left open. [M4.0] EXPANDED
into substeps M4.1–M4.7 (2026-08-14, Frank's go). AS OF THE NINETEENTH
SESSION'S CLOSE (2026-08-14): M4.1, M4.2 and M4.3 are ALL COMPLETED —
both design docs written, paneled (R21), fix-rounded, and the freeze is
DECLARED as the working baseline (D44 + addendum; D41–D44 rounded out
the ruling surface, K17 found-and-fixed, K18 opened and scheduled).
NEXT: [M4.4] — implementation is open.

## M4 — Captures + backtracking VM engine

Expanded 2026-08-14 (eighteenth session; Frank's go — design and panel
first, implementation next session at the earliest). The milestone's two
design docs do not exist yet and NOTHING M4-shaped has been panel-critiqued;
the two ruled pre-freeze docs (design_callout_abi.md, subst_template_design.md)
are themselves unpaneled and are swept into M4.3's panel by their own
stated terms.

- [M4.1] COMPLETED 2026-08-14 (merge 65b16c6) — row archived in
  plan_completed.md; the doc (docs/design/match_api_m4.md) is PROPOSED
  until M4.3's panel closes, and its §13 ASKs (naming picks + the
  rx_ctx-fixed-names confirmation) go to Frank with the panel materials
- [M4.2] COMPLETED 2026-08-14 (merge b726386) — row archived in
  plan_completed.md; the doc (docs/design/engine_m4.md) is PROPOSED
  until M4.3's panel closes. Headlines: DD-9 DECIDED (hybrid cannot own
  case (f) — re-home to BENCH-1's worklist, Frank's confirmation
  pending); SR-8's flip is smaller than its row (zero constructs become
  compilable); three ABI tensions reported (§11) and twelve ASKs (§12)
  ride to Frank/panel; four requirements handed back to
  match_api_m4.md (search-entry negative returns, the capture-delivering
  entry gap, ASK-4 closure per §5.7, symbol spellings)
- [M4.3] COMPLETED 2026-08-14 (R21; row archived in plan_completed.md) —
  the D6 panel ran (3 critics, 36 findings, 11 tier-1), every tier-1/2
  finding is dispositioned (D44 + the r21-fixes doc round + the k17-fix
  code lane, ubsan+asan green on the composed tree), and **the MATCH-API
  FREEZE IS DECLARED** as the M4 WORKING BASELINE (D44 addendum's
  weight: revisable at M4.7's post-run review, D40 regime 1).
  match_api_m4.md is the frozen surface; engine_m4.md is the design of
  record. Standing consequences: K18 (opened by the K17 fix's own sweep)
  is design-first-before-[M4.6]; the full battery (lint/bench/mech)
  remains owed at [M4.4]'s close per the standing schedule.
  IMPLEMENTATION IS OPEN from [M4.4]
- [M4.4] COMPLETED 2026-08-14 (merge c18e904, break commit 1dbb6ce, lane
  m44-apibreak) — row archived in plan_completed.md. The announced API
  break landed as ONE break commit: `<prefix>_span` RETIRED for the
  caps-array search signature (all emit sites incl. the three from
  D44/A-7, %zu→%td), the six fixed ABI types under the prefix-independent
  `PCREC_RX_ABI_H` guard, `<prefix>_match`/`_match_caps`/`_info`
  emitted unconditionally, `pcrec_error.input`, the `pcrec_options`
  flags word (PCREC_CASELESS/PCREC_EMIT_MAIN; PCREC_NO_CAPTURES
  reserved), RX_ERR_STEPS/RX_ERR_FRAMES reserved, +3 codegen checks
  (34→37: ncaps-is-the-macro, NCAPS>1⇒VM, cross-prefix one-TU compile);
  populations conserved and accounted; S04 sabotage retargeted to
  guard-neutering. FULL battery green at close (test/strict/ubsan/asan/
  lint/bench/mech 35-rows-0-undetected) — the lint/bench/mech debt owed
  since the eighteenth session is DISCHARGED. One as-built deviation
  awaiting a Frank ruling: `rx_info` is emitted as a struct TAG only
  (bare typedef collides with default-prefix `<prefix>_info` = literal
  `rx_info`) — see match_api_m4.md §5's as-built note
- [M4.5] COMPLETED 2026-08-15 — row archived in plan_completed.md.
  VM emitter core LANDED end to end across five substeps (a: capture
  .rxt format + python span oracle; b: src/gen/emit_vm.c, 65k-pair
  oracle sweep, §5.4 byte-identity gate; c: DD-8 tracer + D45 compile
  budget + K19 cap + K20 fix; d: D27-blinded author, 230/230, two
  contract-text gaps -> §2.2 addendum; e: D46 per-quantifier rung
  bitmask + boundary tests + coverage fill). Close battery all seven
  legs green at 7e3ff93; counts: corpus 1704, cli 247, reject 528,
  codegen 38, registry 168, PC-3 163, PC-4 62,872/0, trie 7,
  vm-identity 8, ir-listing 78, vm 28, thread 8, known_fail 1 (K18
  deliberate), mech 44 rows/0 undetected. Standing consequences:
  [M4.6] gate = K18 design-first — **DISCHARGED 2026-08-15**, design
  note paneled (R23) and BUILT by the k18-rewrite lane ([K18-FIX] in
  plan_completed.md; corpus 1704 → 3198); [ENG-BREP] alongside it;
  struct rx_info spelling RULED 2026-08-18 (D57: struct tag blessed);
  K19 residual ruling still open with Frank.
- [M4.7] COMPLETED 2026-08-18 (thirty-first session; fix merge d523a88) —
  row archived in plan_completed.md. M4's hardening wave: seven substeps
  (a-g). Standing consequences: docs/spec/match_api.md is the CONTRACT
  (R29-paneled, fix pass landed — the give-up-code space is now stated
  in BOTH shipped comments); capturediff + test-resource ride make test;
  corpus 10,369; gate 13 cases; D54-D57 placed; K7/K24 closed,
  K25/K26/K27 open; NEXT MILESTONE RULED: M6 first (Frank, 2026-08-18).

Design notes moved here from [MOD-0.1]'s archived entry (docs/dev/plan_completed.md),
2026-08-13 — M4's design customers, per the Development order above:

**DESIGN NOTE FOR `backrefs` (Frank, 2026-08-12 tenth session): the
engines column's blanket VM_ONLY on the digit rows is provisional and
splits under an AOT compiler.** At match time a backreference is a string
compare against the group's captured text — which is exactly what the
backtracking VM will do, and what the DFA engine cannot (subset
construction erases thread identity; no execution point knows a capture,
and `(a*)b\1`'s state would need unbounded text — the pumping-lemma
classic). But when the referenced group's language is FINITE, the backref
is REGULAR and compiles away statically: `(abc)\1` is `abcabc`, `(a|b)\1`
is `aa|bb` — expand each choice with the reference synchronized, pure
DFA, zero runtime cost, and only an ahead-of-time compiler can afford the
expansion (bounded by the existing NFA/DFA caps and gcc-compile-time
budgets; infinite-language groups keep the VM). So the module's engine
answer is per-PATTERN, not per-row: finite-group backrefs → ENGM_DFA via
expansion, infinite-group → ENGM_VM. The `engines` column stays design
intent until then (nothing consumes it before SR-8/M4); do not read the
rows' VM_ONLY as a measured limit.

**SAME-SESSION COMPANION NOTE for `atomic-groups`/possessives (Frank):
the (?> row's VM_ONLY splits the same way, and the naive intuition is
BACKWARDS twice over.** A DFA never backtracks in the first place —
subset construction keeps every alternative alive, which is exactly the
NON-possessive semantics — so `a*+` is not a free annotation: it CHANGES
the language (`a*+ab` matches nothing, `a*ab` matches "aab"), and a
naively-determinized atomic group silently implements the wrong one.
But the language stays REGULAR (atomic/possessive are CUT operators;
Berglund et al., "Cuts in Regular Expressions" — cuts preserve
regularity with possibly-exponential conversion), so pure-DFA
compilation is achievable, and the construction's one primitive —
determine the sub-expression's OWN priority-first match endpoint online,
ignoring the continuation — is precisely the priority accept-pruning
pcrec's subset construction is already built around. Blowup bounded by
the existing caps; the disjoint-follow special case (PCRE2's own
auto-possessification direction, a*b ≡ a*+b when nothing that follows
can start with an `a`) is free in both directions. Engine answer again
per-PATTERN: cut-constructible → ENGM_DFA, else VM.

## M5 — UTF-8

- [M5.0] STATE:not-started — milestone (expand on arrival): byte-wise UTF-8 automata, \p{...} module. CROSS-NOTE 2026-08-23 ([M6.6.2] wave A): `pcrec_maxw`'s A_CLASS arm answers 1 BYTE and is EXACT only because src/core/compile.c refuses PCREC_ENC_UTF8 by name; the day a UTF-8 backend lands that arm must become the encoding's maximum code-unit length (minw's identical-looking arm stays sound as an under-estimate) or the lookbehind fixed-width rule silently accepts variable-width branches. Recorded at both functions and in src/opt/CLAUDE.md; this row owns the change. NOTE ([M5-SEAM], completed 2026-08-18, see plan_completed.md): the residual seam, per-pattern `--encoding` scalar, and `<prefix>_next_pos` already SHIPPED as the D58 prelude — what remains here is the UTF-8 lowering instance (CharSet → byte-sequence fragments), \p{...}, DD-1 folding, the UTF PC-4 oracle twin, and DD-12 (7)(a)'s two M5-time structural checks (hot-loop shape identity ASCII-vs-UTF-8; the second-backend validation of the seam D58's revisit-when names)

## M6 — PCRE feature modules

- [M6.0] archived to plan_completed.md (CLOSED 2026-08-25, fortieth session, on Frank's ruling — D79: the five ruled modules named-groups/assertions/atomic-groups/backrefs/lookaround all shipped 2026-08-18..24 and `recursion` outside the list as [DD-14]; the M6 milestone completed the spine. Residue re-homed: post-module items (1)/(2) live on [DD-11] by D66 — the 83x partial-anchor gap is the kind of thing the bench loop should FIND, and [DD-11]'s core reduction gets its charter through the loop if it shows at rank; (6) is [SR-8]'s armed second-construct trigger)
- [M6.1] archived to plan_completed.md (completed 2026-08-18, thirty-third session — the R30 panel + focused re-checks + N1 verification closed it; design docs/design/assertions_design.md merged at 0beac07; review docs/dev/reviews/2026-08-18-r30-assertions-design.md; Frank rulings Q1/Q3/Q8 carried on [M6.2])
- [M6.2] archived to plan_completed.md (completed 2026-08-21, thirty-fifth session — module `assertions` closed: five waves + repair slice + D27 blinded corpus, all close-validated; the post-module queue re-homed to [M6.0])
- [M6.3] archived to plan_completed.md (completed 2026-08-18, thirty-third session — see that file; D59, merge commits on main)
- [SPEC-M] archived to plan_completed.md (completed 2026-08-21 — spec_mod0 green, (?m) named exceptions with guards; expiry DD-11)
- [M6.4] archived to plan_completed.md (completed 2026-08-22, thirty-sixth session — module `atomic-groups` SHIPPED: design R31 (21e173e), implementation 69f3b93 + fix 8e4af41 (the D27 corpus found a tier-1 miscompile — the MRL follow-bound crossing the cut — fixed at its root), D27 corpus c324091 134/134; union battery all five stages green on the fixed state (test 21,557/0); mech 99 rows 0 undetected, S88-S101 all DETECTED; gate 13/13 at load 0.39, weakest margin 1.43x (34ede2c); SR-8 built (D67); K29 fixed; U9 held LOUD in tests/known_fail pending Frank's ruling)
- [M6.5] archived to plan_completed.md (completed 2026-08-22, thirty-sixth session — module `backrefs` SHIPPED: design R32 (ca9beef), implementation 3aa446f (lane fb97bab: test 23,798/0, its own ubsan+asan green, identity gate 1501/1502/1501 on three axes), D27 corpus 672a2f4 207/207 with ZERO implementation divergences; union battery all five stages green on 3aa446f; mech 118 rows / 0 anomalies / 2 undetected at 5edba64 → S107 corpus gap closed + DETECTED, S108 RETIRED as measured-unobservable → 117 scored rows, 0 outstanding; gate 13/13 at load 0.36, weakest margin 1.43x (41e541a); registry 106/52/48/6 asserted; DUPNAMES (?J) shipped with first-of-run-by-number-that-is-SET resolution and the tiebreak as correctness; the [M5-SEAM]'s second residual entry pair; S102-S120; residuals: wire S103 to `brefidentity` (registered, zero rows); a MULTI-HUNK sabotage mechanism — DONE post-close 2026-08-23 (the matrix's optional second site; S108 RE-INSTATED two-site and DETECTED; tripwire 118 rows / 119 anchor sites); a sabotage row for possessify.c's Glushkov `case A_BREF` arm (load-bearing, no row); FOLLOW-UPS from Frank's read of the `(abc)\1` artifact (2026-08-22 23:0x, measure first per D18): (a) `engine_callable` seam entries should be `static` — rx_bref_match inherited next_pos's external linkage without an external consumer; (b) a DEFINITELY-SET analysis (dominance through A_CAT, not through A_ALT/A_REP bodies) to elide the UNSET test where the referenced group always publishes before the reference; (c) a memcmp fast path on the success path with the failed-prefix walk only on mismatch — the charge's prefix-length contract keeps; (d) STATIC GROUP WIDTH — a fixed-width referenced group (`(abc)`) makes the compare a constant-length compare with one hoisted bounds check, and under the definitely-set analysis pcrec_minw(A_BREF) may soundly become the group's minw (exact for fixed width) instead of the design's deliberate 0, feeding the MRL prune; the full form is the chartered finite-language expansion (`(abc)\1` → `abcabc`), whose only customer is --no-captures; (e) THE WORK UNIT is bytes examined, an effort PROXY calibrated to the VM's per-byte loop — block compares (backref memcmp, memchr prefilter, cursor scans) over-charge relative to effort, the conservative direction for a DD-2 robustness bound; if the unit is ever meant as effort, charge ceil(n/k) for block operations — a ruling for the unit, not a backrefs one-off; (f) THE SINGLETON-LANGUAGE REWRITE, in Frank's core-reduction form (23:3x): NOT a backrefs one-off — under the predicate |L(G)| = 1 under G's own flags, definitely-set, nrefs == 1, `\1` and `\g<1>` mean the same thing (PCRE2 REVERTS a subroutine call's captures, so inlining a non-recursive call IS the non-capturing copy `(?:G')` the rewrite needs), so the rewrite is a one-line node swap A_BREF → subroutine-call in the core-reduction layer (DD-11's principle, D66's precedent) and the `recursion` module's INLINER does the rest — one path for inlining group code, no separate emitter code; lands when that inliner lands; payoff on the DEFAULT build is the hybrid prefilter coming back ON (no A_BREF in the tree; today fit.prefilter = false for every backref pattern); (b) shares its definitely-set analysis with this predicate — one pass; (d) is the only genuinely backref-local item and is dropped unless a measurement asks; none blocks the close)
- [M6.6] ARCHIVED → docs/dev/plan_completed.md ("2026-08-24 (thirty-eighth session — [M6.6]: module `lookaround` ships)"): M6.6, M6.6.1-M6.6.4 all completed; M6.6.2's `completed-pending-close` was discharged by M6.6.4's close. Archived 2026-08-25 by the thirty-ninth session's manager.
- [ABI-NS] archived to plan_completed.md (completed 2026-08-18, thirty-third session — D60+addendum implemented; merge on main; [M6.2]'s wave A is UNBLOCKED)

(2026-08-13: the classes+ and modifiers halves already landed as gated
modules — MOD-0.3 and MOD-0.5, see docs/dev/plan_completed.md. Remaining:
assertions (VM-independent), lookaround, backrefs, atomic groups,
named-groups, conditionals, recursion producers. 2026-08-18 expansion
note: conditionals and recursion are NOT in Frank's ruled M6 list and are
not substeps above — their module refusals stand; they queue behind M6 as
their own future rows if ruled in.)

- [M6-READ] archived to plan_completed.md (completed 2026-08-21, thirty-fifth session — the emitted-code readability pass: approved style shipped from both emitters, legends generated from emitter-owned data, census-proven byte identity; CONVERSION_LOG.md is the findings record; src/gen/CLAUDE.md carries the emitted-vocabulary rules)
## M3 — Streaming input

- [M3.0] STATE:not-started — DESIGN GATE FIRST (R2-A3): D7's "same shape streaming needs" holds only for match-END finding. The reverse pass rescans backward through raw bytes a stream may no longer hold (unbounded for `.*` shapes). Design match-START finding under bounded memory BEFORE writing streaming code; reconcile with APPROACH §6's PARTIAL/WINDOW_EXCEEDED contract
- [M3.1] STATE:not-started — *_stream_* API for the DFA engine, chunk-boundary tests

(2026-08-13: moved after M6 per the Development order above — the streaming
API is designed once against the final engine+feature set; [DD-3] rides
along, [OS-3] feeds the design gate.)

## M7 — Hardening

- [M7.0] STATE:not-started — milestone (expand on arrival): differential fuzzing vs libpcre2, freestanding/embedded build profile, PCRE2 testdata import

## Beyond M7 — long-term vision (Frank, 2026-08-09)

Direction, not scheduled work. Recorded so the architecture is not painted into
a corner that would make these expensive later. Each becomes a milestone only
after the current ladder is complete and the result is something we are happy
with.

**POSITIONING NOTE (Frank + manager, 2026-08-13 sixteenth session).** The
niche, in one sentence: *PCRE2 semantics, compiled to verified,
dependency-free C — fastest where the pattern is known ahead of time, and
the only one that does compiled substitution.* Its elements, each with an
owner: (1) PERFORMANCE, honestly scoped — an AOT compiler wins where the
compiler saw the exact pattern (specialized single-pattern scanning,
startup, latency), and does not chase Hyperscan-scale SIMD multi-pattern;
[BENCH-1]'s prioritizer maps both the worst cells (fix) and the best cells
(advertise). (2) EMBEDDED / NO-LIBRARY — the defensible core. The incumbent
to name is re2c; differentiation is PCRE2 syntax+semantics, leftmost-first,
the future captures/backrefs tier, and the verification story. What the
code already guarantees is the sales sheet: all-const tables (TS-1,
enforced), no malloc/errno/locale in generated code, thread-safe by
construction, deterministic — certifiable vendored source. M7's
freestanding profile cashes this. (3) THE VERIFICATION STORY IS A PRODUCT
FEATURE — "differentially verified against libpcre2; unsupported syntax
fails loudly, never miscompiles" is a claim no neighbor in this niche
makes. (4) LATENCY — time-to-first-match from process start (~zero for us:
tables page in from .rodata; PCRE2 pays pcre2_compile + JIT warmup every
process) and short-subject per-call overhead, the dimension real workloads
(log lines, field validation) are dominated by and benchmarks skip —
measured under [BENCH-1]. (5) COMPILED SUBSTITUTION as the headline
differentiator — see [M4-SUBST]'s beyond-PCRE2 direction. Developer-
experience directions that serve the niche are the [V-*] rows below,
including V-G/V-H (added this session).

- [TT-4] STATE:completed (CLOSED 2026-08-23 on Frank's ruling after [TT-4.1]'s measurement: gcc is 17% of make test's CPU and make test is ~10 of the chain's ~150 minutes — TU-batching's 3.66x on gcc nets ~12% of suite CPU for the most design surface on the list (feature-set collisions, all-or-nothing batches); Frank: "6 and 7 probably not worth it … spend the effort where it has the greatest impact; if test is 10 minutes, spend the least time there". [TT-4.2]/[TT-4.3] NOT started — the measured NO, TT-3's shape; the prototype and numbers stay in studies/tt4_batching/ for the day the profile points at gcc again. The row's lasting yield is the census method and the [TT-6] finding) — formerly STATE:started (2026-08-23, on Frank's "go tt-4"; expanded into [TT-4.1]-[TT-4.3] below) — BATCHED COMPILATION IN THE TEST HARNESS
  (chartered by Frank, 2026-08-22 22:3x, "charter TT-4 after M6.5 closes,
  measurement stage first"; START AFTER [M6.5] CLOSES — the next
  infrastructure row, pulled forward because every lane today paid the
  cost). THE PROBLEM, measured: `make test` is ~120 core-minutes (~10 min at
  -j12) across ~20,000 tiny compile-and-link gcc invocations; the sequential
  per-section wall times from the [M6.5.2] lane's timestamped run were
  assertions+identity gates 458 s (the four identity gates compile ~1,200
  corpus patterns TWICE, ~2,400 gcc calls), the .rxt corpus 392 s (~1,800
  patterns, pcrec→gcc→link→run each), rungselect 242 s, counterk 166 s, mrl
  115 s, atomic diff 100 s. [TT-3] showed caching cannot rescue this shape
  (compile-and-link single invocations; warm ccache 4x SLOWER). THE IDEA
  (Frank's, and [V-E]'s multi-pattern compilation unit with the harness as
  its first real customer): one translation unit per BATCH of N matchers
  (each already carries its own prefix — the emitter was designed for
  coexistence) plus one dispatching driver — one gcc call and one link per
  batch; the saving is the fixed per-call cost (process start, pcrec.h
  parse, link) times N, largest in the gcc-bound suites; matcher RUN time
  unchanged. STAGES: (1) MEASUREMENT FIRST (Frank's order) — instrument
  tests/harness/run.sh and the main differential drivers to split wall
  time per section into pcrec / gcc / link / run and count invocations over
  one `make test`; identify the two worst sections; prototype batching on
  them in a scratch driver and REPORT THE MEASURED SPEED-UP before any
  harness change (TT-3's lesson: the obvious idea measured as a slowdown).
  (2) DESIGN, gated on (1)'s numbers: batching at the gcc/link step ONLY —
  per-pattern .c artifacts keep existing so every per-artifact instrument
  (codegen rules, identity gates, D46 stamps, the anchor tripwire, the D27
  cells' perr attribution) reads exactly what it reads today; FAILURE
  ISOLATION (a member that fails to compile or crashes under a sanitizer
  must not take its batch down — fall back to per-pattern for the failing
  members and attribute the failure to the right pattern; D45's per-pattern
  gen-timeout semantics preserved; GENCFLAGS rides through); an emitter-side
  question only if two matchers cannot coexist in one TU (then [V-E]'s work
  is the prerequisite, measured not assumed). (3) LANDING: the harness
  batches; `make test` wall time and core-minutes re-measured on the same
  box; the sanitizer batteries and mech ride the same path; docs/testing.md
  records the before/after. NOT in scope: the .rxt-as-specification format
  (a separate discussion Frank has deferred; separable from batching).
  - [TT-4.1] STATE:completed (2026-08-23, merge 19ea394; docs/dev/
    tt4_measurement.md + studies/tt4_batching/) — MEASURED: make test =
    3,777 CPU-s, gcc 647 (17%, 4,845 calls — the row's "~20,000" premise
    was wrong by 4x), pcrec 275 (7%); TU-batching beats link-batching at
    every N, best 3.66x (corpus pool, N=16) / 2.73x (atomic, N=8) against
    the 12-way baseline — the sweet spot is batch COUNT near core width,
    N=64/256 REGRESS under parallel execution (0.41-0.96x); ceiling ~12%
    of suite CPU. Two confirmed obstacles: mixed --features sets collide
    on unprefixed PCREC_FEATURE_SET/PCREC_FEATURE_MODULES #defines; a
    batch fails all-or-nothing (recovery of 15 good members 2.99 s).
    THE BIGGER FINDING: this box's `timeout` is uutils 0.8.0 and costs
    ~108 ms WALL per call at zero CPU (GNU /usr/bin/gnutimeout: 4 ms);
    corpus makes 23,252 such calls ≈ 2,430 s of sleep across 12 workers
    ≈ ~200 s (~43%) of its 469 s section wall, paid again on each
    sanitizer axis → chartered as [TT-6]. Exec-batching (one driver run
    per pattern instead of one per case) is a further 5.57x on corpus's
    per-case loop AFTER the timeout swap, corpus-only (the other sections
    already loop inside their own C drivers). — formerly STATE:started — MEASUREMENT (Frank's order: first, before any
    harness change). Census over one `make test` by section (the `test-*`
    targets): invocation counts (pcrec, gcc one-shot, gcc -c, link) and wall
    time split pcrec / gcc / link / run / harness-overhead; name the two
    worst sections; prototype batching on them in a SCRATCH driver (studies/
    tt4_batching/, never the harness) at several batch sizes and REPORT THE
    MEASURED SPEED-UP, or the measured slowdown (TT-3's lesson). Output: a
    measurement memo with method, blind spots and numbers from runs.
  - [TT-4.2] STATE:closed-not-started (Frank, 2026-08-23: not worth it on the numbers) — DESIGN, gated on [TT-4.1]'s numbers
    (gcc/link-step batching only; per-pattern artifacts preserved; failure
    isolation; D45 per-pattern semantics; GENCFLAGS rides through). Panel
    (D6) if the numbers open the row; an honest NO closes it like TT-3.
  - [TT-4.3] STATE:closed-not-started (with [TT-4.2]; exec-batching, the memo's lever 7, likewise) — LANDING: the harness batches; `make test`
    wall and core-minutes re-measured on the same box; sanitizer batteries
    and mech ride the same path; docs/testing.md records before/after.
    FRANK (2026-08-23, 08:3x): if the row proves worthwhile he wants to SEE
    the before/after timings for testing — present them to him at the
    close, whole chain (make test, battery stages, mech), not make test only.
- [TT-6] STATE:completed (MERGED 5935ea9, 2026-08-23 12:1x: tests/lib/timeout_bin.sh resolves TIMEOUT_BIN — GNU when the default is uutils, plain `timeout` elsewhere; every bare call swapped in 9 scripts + scripts/Makefile; MEASURED test-corpus isolated 6:44.24→1:04.08 (6.31x, identical 22,358/0), make -j12 test 10:32.82→10:15.96 (oversubscribed at load 33-41, sleep hidden — the saving shows where sections run serially: the sanitizer axes and mech rows; battery_tt6.log is that number); S43 anchor re-derived, tripwire 118/119; D69 rows S11+S43 DETECTED on the merge in 19 s total; bench COMPILE-SPEED/GCC-TIME budgets had the wrapper's launch cost inside their number — archived gate results predate the swap, flagged in tests/bench/CLAUDE.md) — formerly STATE:started (APPROVED by Frank 2026-08-23 11:1x as #1 of the set; lane/tt6timeout) — THE `timeout` BINARY TAX (found by [TT-4.1]
  2026-08-23, manager-verified: uutils coreutils 0.8.0 `timeout` sleeps
  ~108 ms per call at zero CPU; GNU `gnutimeout` 4 ms). ~10 test scripts
  call `timeout` bare (pcrec calls, every per-case matcher run in
  tests/harness/run.sh:356, gen_cc's wall wrapper). LANDING SHAPE: a
  tests/lib helper resolving TIMEOUT_BIN (prefer GNU when the default is
  uutils; plain `timeout` elsewhere so a stranger's box is unaffected) used
  by every script; before/after `make test` wall on this box (projected
  ≈ −200 s on corpus's 469 s section wall, also on each sanitizer axis
  and per mech row); the D45 timeout semantics (exit 124, SIGTERM→KILL)
  must be re-verified against the GNU binary in the failing direction.
  Measurement is DONE (tt4_measurement.md "The timeout binary itself");
  Frank decides the set with [TT-4.2]/[TT-5] stage 2.
- [TT-5] STATE:completed (CLOSED 2026-08-25 on Frank's ruling, fortieth session. WHOLE-CHAIN BEFORE/AFTER, owed to Frank: BEFORE (m65, 2026-08-22) test 10m14s + ubsan 32m35s + asan 42m25s + mech 60m08s @118 rows ≈ 2h26m; AFTER (the [DD-14] close tree, 2026-08-25) test ~25-37m under -j12 + san ~60m (one combined axis, [TT-7]) + mech ~80m @180 rows PROCS=6 ≈ 2h50m — per row and per case the chain is FASTER ([TT-6] −105 ms × ~23k calls, [TT-7] −18 min, [TT-8]'s PROCS); in wall time it is not, because [DD-14] grew the corpus ~40% and the matrix 52% faster than the moves shrank it. Residue: #5 CCACHE for mech → [CHK-1] item (d), measured in situ before adoption; the [TT-10] load sensitivity → [CHK-1]; D69's premise ("no row observed flipping DETECTED→UNDETECTED from a compiler change alone") has since FAILED — S70 — mitigated by [MECH-REACH], D69 addendum) — formerly STATE:started (2026-08-23, thirty-seventh session; chartered by
  Frank: "we are in the multiple hours for overall testing right now and
  it's slowing development … consider some other testing moves outside
  [TT-4] … perhaps some more profiling will spark ideas") — VALIDATION-
  CHAIN PROFILE AND CANDIDATE MOVES. The per-merge chain measured
  2026-08-22 on 3aa446f/5edba64 (build/battery_m65.log, build/mech_m65.log):
  test 10m14s, strict 6s, ubsan 32m35s, asan 42m25s, lint 33s, mech 60m08s
  (118 rows, PROCS=4) — ~2.5 h, of which the two sanitizer axes + mech are
  ~135 min; `make test` is the SMALLER part, so [TT-4]'s batching only
  reaches the hours if it rides the sanitizer and mech paths ([TT-4.3]).
  STAGE 1 (read-only, from the existing timestamped logs + the drivers'
  source; no runs while the [TT-4.1] census is timing): where the minutes
  go inside each stage (section-level for the sanitizer axes; row-level
  for mech as far as the log allows — it has no per-row timestamps, a
  blind spot to name), what each stage RE-does that another already did
  (the sanitizer axes recompile the whole suite twice; mech rebuilds pcrec
  per row), and a candidate list with the evidence each needs before
  it is a row: e.g. one combined `-fsanitize=address,undefined` axis
  instead of two (halves ~75 min IF the diagnoses stay distinct — docs/
  testing.md SAN-1's reasons for separate axes must be read first),
  mech per-row scoping (which sections a row really needs), CCACHE=1 for
  mech ([TT-3]'s qualified yes), PROCS for mech, pipelining stages on a
  quiet box. STAGE 1 DONE (6f1e941, docs/dev/chain_profile.md: chain
  2h26m on m65; three-log trend; ubsan/asan/mech +20% in one day with no
  growth alarm; SAN-1's separate-axes reason is TSan-specific; mech PROCS=4
  never re-validated at 118 rows and leaks into inner harness sharding;
  CCACHE=1 for mech). CANDIDATE (h), added 2026-08-23 from Frank's
  question "are the sabotage tests dependent on the tests themselves; do
  they need re-running if the tests don't change?": a row's verdict is a
  property of the PAIR (compiler, corpus) — it flips when (1) its
  SAB_HARNESS_TARGET changes (exact, grep-able), (2a) its anchor drifts
  (caught STATICALLY by the tripwire, seconds, already on the bar), or
  (2b) a compiler change elsewhere MASKS or unreaches the sabotaged path
  (S108's single-site shape; NOT derivable from the diff — only a run
  finds it). No row has yet been observed flipping DETECTED→UNDETECTED
  from a compiler change alone. Tiered policy proposed, NOT ruled: docs/
  infra-only → tripwire; tests-only → tripwire + rows targeting the
  changed files; src changed → tripwire + rows whose SAB_FILE or target
  changed, full matrix at module close. MEASUREMENT FIRST: diff the
  2026-08-18..22 mech matrices in build/ (different HEADs, known diffs)
  for any row that flipped without its SAB_FILE/target changing. Frank
  (08:5x): "wait for the census memo and decide as a set". STAGE 2 RULED
  by Frank (11:1x, 2026-08-23): "spend the effort where it has the
  greatest impact; if test is 10 minutes, spend the least time there —
  insofar as it's not called as part of the other tests. Approve 1-3 as
  per your recommendations. #4 I am ok with this risk. 6 and 7 probably
  not worth it. 5 as a follow-on if needed." → #1 [TT-6] timeout swap
  (STARTED); #2 [TT-7] one combined ASan+UBSan axis, measurement first
  (STARTED); #3 [TT-8] mech PROCS re-validation + the PROCS leak into
  inner sharding (STARTED); #4 the tiered mech re-run policy ADOPTED as
  D69 (risk accepted by Frank; the retro-diff of the m64/m65 matrices
  rides [TT-8] as evidence, not as a gate); #5 CCACHE=1 for mech — follow-
  on if the [TT-8] numbers leave mech long; #6/#7 gcc/exec batching —
  closed with [TT-4]. BOX RULE for the three lanes: every timed run is
  box-exclusive and serializes through the manager — [TT-6]'s
  before/after first, then the battery on the merged swap (= the axes'
  "after"), then [TT-7]'s combined-axis run, then [TT-8]'s matrices.
  Frank gets the whole-chain before/after at the end.
- [TT-7] STATE:completed (ADOPTED 2026-08-23 14:2x: `make san` MEASURED 45:50 vs ubsan 26:58 + asan 36:45 = 63:43 on the same tree — −17:54 per chain, identical 1569 PASS lines, zero reports; the battery's sanitizer stage is now `san`, ubsan/asan opt-in singles; docs/testing.md "[TT-7] combined axis — ADOPTED") — formerly STATE:started (2026-08-23, Frank's #2; PREP MERGED 9582091: `make san` target, build-san/, distinctness verified through the real generated-matcher path, D45 budgets byte-identical to either single axis, docs PENDING; LSan is a no-op on this box under ANY axis — K26, ptrace_scope=1; OWED: the manager's timing run `gnutimeout 5400 /usr/bin/time -v make -j12 san` vs the battery_tt6 ubsan+asan walls, then the adoption flip) — ONE
  COMBINED `-fsanitize=address,undefined` AXIS, measurement first: a
  `make san` target building a third separate tree (build-san/) with the
  combined flags on BOTH axes exactly as ubsan/asan do; measure its wall
  against ubsan+asan run back-to-back on the same HEAD (after [TT-6]
  lands, so the axes are measured without the sleep); verify the
  DIAGNOSES stay distinct (the sanitizer findings inventory in
  docs/testing.md lists the historical reports — replant one of each
  kind, or a known UB and a known leak, and show the combined build
  reports both with their own tool names); if the combined axis is
  faster AND as diagnostic, the battery adopts it and ubsan/asan stay as
  opt-in singles. SAN-1's separate-axes reason is TSan-specific
  (Makefile:577-580) — not a blocker.
- [CHK-1] STATE:completed (CLOSED 2026-08-25 18:2x — THE BATTERY IS GREEN on 1879bc2 (matrix tree 44c77fc, docs-only apart): `make test` 26,843 cases with the K32 corpus cell's 29 re-run solo 1,634/0, 1,539 checks / 0, 1 INCONCLUSIVE under -j12 (the load guard doing its job); solo resource 19/0, counterk 24/0; `make san` clean both axes, 33 scripts (1h41m — five previously-dropped diff scripts now run); full matrix 180 rows / unexpected 0 / undetected 6 (S150-S153, S160, S178, all expected) / UNREACHED 0 / anomalies 0 — the FIRST matrix measuring reach on every row, 42 reach lines. Three battery-found defects fixed on the way (c448437, 1879bc2): the sweep's pcrec_run-behind-an-exec-wrapper and unsourced-use shapes, and the 20 s wall on a hostile compile under load. Started 2026-08-25 12:3x; PROGRESS ~14:3x: [MECH-REACH] MERGED 3eb4cc8 (row stays started until the full 180-row matrix measures `unreached` across every row — owed at this batch's battery); K37 FIXED + [TT-9] MERGED ea4504b; CROSS-LANE CATCH at the merge: the K37 structural check went RED on main with 22 sites the srReach merge introduced — 21 `SAB_REACH` probe strings and one help line — because the mech script's witness-probe executor ran `bash -c "$SAB_REACH"` unbounded; fixed the general way (one `$TIMEOUT_BIN` bound at the executor, `SAB_REACH_TIMEOUT` override, two reasoned allowlist entries), verified [K37] PASS 459 sites/77 scripts + S27 solo DETECTED through the bounded executor; [TT-10]/[TT-11]/(d) delivered by srLoad, under review) — THE CHECK-INFRASTRUCTURE BATCH (Frank,
  2026-08-25, fortieth session, ruling 5 of the [DD-14] going-forward
  conversation): [MECH-REACH], K37, [TT-10], [TT-9], [TT-11] — five
  one-way improvements to checks, no `src/` change, disjoint files —
  run as up to three sonnet lanes BEFORE the bench loop starts (every
  battery until then pays K37's hang risk and [TT-10]'s solo re-runs).
  Order by what each protects: [MECH-REACH] (the matrix's meaning), K37
  (the battery hanging on a real bug), then [TT-10]/[TT-9]/[TT-11].
  BRIEF NOTES from the ruling: (a) K37's `pcrec_run` helper routes the
  compiler through `scripts/watchdog` (wall + tree-RSS + CPU + log line),
  not bare coreutils timeout — the same mechanism `gen_run` already uses
  for the other half of the harness's calls; a compiler that
  runaway-allocates instead of looping slips past a plain timeout. (b)
  [TT-10]'s "measure the child's CPU, not wall" is what watchdog's `-c`
  (cpukill, exit 123) already does — try wiring before building. (c)
  every brief: `gnutimeout`, never `timeout` (uutils; docs/testing.md
  "The `timeout` binary itself"); `scripts/safekill PID` to kill.
  (d) CCACHE=1 for mech (Frank, [TT-5]'s #5, 2026-08-25: "test ccache in
  situ because last time we tried it it made the tests take longer") —
  [TT-3] measured NO for `make test` (slower) and a QUALIFIED yes for
  mech; the wiring is already opt-in. Adopt as mech's default ONLY on a
  before/after WIN measured on a full matrix on the same tree,
  box-exclusive (mech rebuilds pcrec per row — that is the cache's
  case); a loss or a wash stays opt-in and the number is recorded.
  MEASURED 2026-08-25 (srLoad, 12 rows, 4-way pool, HEAD 3e771a3, CCACHE_DIR persisted outside the archive tree — the Makefile default resolves INSIDE each row's ephemeral tree and would never hit): 10 measurable rows 348.2 s → 306.8 s (−11.9%), NON-UNIFORM — build-dominated rows −21..−52% (S01 −52%, S11 −34%), suite-execution-dominated rows −3..−4% (S46, S56), the two hang rows S159/S90 unhelped in either condition; ccache 66% hit rate; the ccache pass ran on a QUIETER box (confound disclosed). NOT ADOPTED as default — stays opt-in; revisit only if a full-matrix wall number is ever needed and the build-dominated share justifies it.
- [K38-FIX] STATE:completed (lane srK38, sonnet, 2026-08-26, commit 06c08c9) — the VM emitter's fixed-size name buffers truncate at long prefixes (known_issues K38, FIXED) — was: started (STARTED 2026-08-26 ~12:0x): a 60-char prefix — the documented maximum — yields uncompilable C. General fix: one `PCREC_MAX_PREFIX_LEN`-derived buffer size for every emitted name; a tests/cli witness that emits and COMPILES a max-length-prefix artifact on both engines. Sonnet; the identity gates must stay byte-identical for `rx` (the buffers only grow). CLOSED: reproduced with a real 60-char prefix through gcc rather than trusting the original buffer list (nm[48]/entrypos[32] turned out clean; the real family was vm_slot_expr's sl[64], the span-cursor family, the revdet rung's rv/cur/byte[80]/ga/gs/val — ga/gs truncated to the IDENTICAL wrong string, collapsing the group-span write and group-seen flag onto one name); `src/core/limits.h`'s new `PCREC_MAX_EMIT_NAME_LEN` sizes the whole family plus emit_dfa.c's one prefix-carrying buffer; 1,784-pattern x 2-prefix x 2-engine identity sweep (7,136 compiles) 0 diffs against the pre-fix binary; tests/cli case17 verified DETECTING against that same pre-fix binary; make test-codegen + test-cli (287/287) green, make strict clean.
- [TT-11] STATE:completed (MERGED 2026-08-25 ~14:5x, lane srLoad: run_recursion_identity.sh:311-343 reads `.abi = N` from an artifact of each compiler and refuses on mismatch with D76's message — demonstrated on ac4917d ('.abi = 2' vs 3); default pin 8fc1e51 15/0, (A)/(B) on all four axes at their pinned numbers; subroutines_design.md now says the dead-capture rule is a general src/opt change (D75 addendum)) — formerly STATE:not-started — THE IDENTITY GATE'S WHOLE-FILE PIN FOLLOWS THE
  `abi` NUMBER (Frank, 2026-08-25, fortieth session; D76). Today
  `tests/codegen/run_recursion_identity.sh` comparison (B) pins `8fc1e51`
  and guards the pin with an ad-hoc probe (`RESUME_FRAME_SIZE` present in
  the pin's emit_dfa.c — one wave's boundary, encoded by hand). Make it
  STRUCTURAL: the pin's emitted `rx_info.abi` must equal the compiler's
  (build the pin's compiler as the script already does; emit one
  artifact; read the stamp), refusing with a message that says "the
  scaffolding changed — bump `abi` and re-pin in the same change" when
  they differ. Comparison (A) (program region vs the pre-module
  `ac4917d`) is untouched — it is the module's promise, not the abi's.
  Same change: `docs/testing.md` + `tests/codegen/CLAUDE.md` state the
  two owners (D76), and the gate's comment + `docs/design/
  subroutines_design.md` describe the dead-capture rule as a GENERAL
  engine-selection change that landed with wave G (D75 addendum), not a
  recursion feature. Validation: the refusal must FIRE on a deliberately
  wrong pin (a pre-FB commit) and PASS on `8fc1e51`; the gate's 15/0
  unchanged. Sonnet-sized; no src change.
- [TT-10] STATE:completed (MERGED 2026-08-25 ~14:5x, lane srLoad: tests/lib/load_guard.sh — 1-min-load/nproc > 2.0 (between the 1.0 every budget already prices in and the K31 addendum's measured 2.58 failure point) turns a watchdog 123/124 on a CPU-capped cell into INCONCLUSIVE, a third counter, never PASS never FAIL; tests/resource's K7 cells and a NEW load-guarded K32 compile-cost pin in counterk (20 s CPU ≈ 5× the 4.0 s quiet cost); solo 19/0 and 24/0; forced breach at ratio 2.47 → INCONCLUSIVE, at 1.18 → FAIL (counterk directly; resource's heavy-load direction by the shared mechanism). RESIDUE 2 (found by the c448437 battery, 2026-08-25 14:4x): the four identity sweeps (endvar/wordctx/mlinectx/gstart, and codegen's M4.5b §5.4) score a compile that TIMED OUT (exit 124 under load) as "N patterns changed emitted bytes" — a failed compile is not a byte change; those scripts must distinguish exit 124 (→ INCONCLUSIVE via load_guard, or a named compile failure) from a diff. Mitigated for now by pcrec_run's 3× wall (1879bc2); the general fix is the next battery-touching lane's. RESIDUE, not built: a suite with inconclusive cells still EXITS 0 — the battery procedure must grep `checks inconclusive: [1-9]` after every run until a runner-level aggregate counter exists (next battery-touching lane; the general form)) — formerly STATE:not-started — tests/resource's 45 s COMPILE-CPU CAP CHECK IS LOAD-SENSITIVE BY CONSTRUCTION (2026-08-24: SIX identical failures across the day's merged-tree batteries on `[a-z]{0,30000}` / `(a|b){0,30000}`, every one green solo, every one under a concurrent lane build — the K31 addendum's shape). The check asserts the cap FIRES within 45 s of CPU, but CPU-time inflation under SMT contention (measured >2× in docs/testing.md) pushes a quiet-box ~25 s compile over 45. Charter: make the check measure what it means — either (a) a RATIO against a calibration compile taken in the same run (the cap fires within k× the calibrated cost), or (b) a load guard that reports INCONCLUSIVE (never PASS, never FAIL) when the 1-minute load average exceeds a threshold, with the D45 budgets themselves untouched. Same class as the k18 san budget: a CPU-bounded assertion is only exact on a quiet box, and a check that lies under load costs a solo re-run per battery. Sonnet lane, small; lands with the next battery-touching wave or at the [DD-14] close. **WIDENED 2026-08-25 ~04:37 (journal part 34):** a SINGLE `make -j12 -Otarget test` alone on a quiet box, twice (srFBc's runs 1 and 2), tripped the same two cells — the K32 compile-timeout cell `((a)|ab){4000}c` (exit 124 + 28 dependents) and tests/resource's 45 s CPU cap (`[a-z]{0,30000}`, `(a|b){0,30000}`) — both green solo every time (1634/0 ×3, 19/0 ×2). So the load sensitivity is to the suite's OWN parallelism, not only to three concurrent suites: the fix must make these cells load-aware (a CPU-time cap measured on the child, not wall; or a serialized section for the two cells; or a load-scaled budget with the reading printed), and the battery procedure meanwhile runs `test-resource` and counterk solo after every full run.
- [MECH-REACH] STATE:completed (CLOSED 2026-08-25 18:2x: the full 180-row matrix on 44c77fc scored `unreached: 0` with every retrofitted row's reach line green — the mechanism is measured across the whole population, not only the 22-row solo sweep) — formerly STATE:started — SABOTAGE WITNESSES MUST PROVE THEIR REACH (2026-08-25, from S70 on the merged [DD-14] tree, journal thirty-ninth session part 40 addendum): row S70 (the escape doorway's enabled-but-unbuilt epilogue, src/parse/ext.c:326) certified NOTHING from [M6.5.2] — when its last live witness `\k` gained a producer — until the full matrix on 17469b6 scored it UNDETECTED; its four named escape witnesses had all been implemented by later waves, and the matrix's "NOW DETECTED / expired claim" doctrine watches only the opposite direction. THE GENERAL MECHANISM (not a per-row fix): `tests/mech/run_sabotage_matrix.sh` gains an optional per-row `SAB_REACH` — a command run on the CLEAN tree whose output must contain a stated string (typically the exact diagnostic the witness produces at the sabotaged site) — asserted BEFORE the sabotage is applied; a row whose witness no longer reaches its site is then RED in the wave that implemented the construct, not two milestones later. Retrofit: every row whose SAB_DESC names a witness construct (the `reject_gated` family first, then any row whose detector is a diagnostic string). Ties to K35 (checks whose population silently shrank) and [TT-10] (checks that lie under load): three shapes of a check that goes green for the wrong reason. SECOND INSTANCE, same run: S155's SAB_HARNESS_TARGET (leftrec.rxt) had held ZERO give-up cells since [DD-14.EMPTY] — a witness FILE whose relevant population went to zero; and its sabotage changes a WRITE not an ANSWER (three byte-identical guards from one emitter function; the survivors answer identically one frame later), visible only to run_frame_buffer.sh §2's exact-fit ASan driver — so `SAB_REACH` must also be able to assert a population ('the target file has ≥N `gu` cells') and a row may declare an instrument requirement (`REQUIRE_ASAN`) whose absence is an ANOMALY, not UNDETECTED (ruled 2026-08-25 ~06:5x). Owner: the next mech-touching lane; the [DD-14] close lane RECORDS the row and re-runs S70/S155 solo, it does not build this. **BUILT BY LANE srReach, 2026-08-25 (fortieth session), branch `lane/srReach`.** `SAB_REACH` + `SAB_REACH_EXPECT` (one required literal per LINE, so a row's several witnesses at one site cannot expire one at a time), `SAB_REACH_POP` (`FILE|EREGEX|MIN`, count PRINTED every run), `SAB_REQUIRE` (closed vocabulary, `asan`) and the new verdict `UNREACHED` — counted in the trailer beside undetected/anomalies, RED unless the row declares `SAB_EXPECT=UNREACHED` with a mandatory `SAB_EXPECT_REASON`, scored in BOTH directions (`NOW REACHED`), and the sabotaged tree is not built when a row is UNREACHED. A CLEAN reference tree is `git archive HEAD`'d and built ONCE per run, lazily. 21 rows retrofitted (S15-S20, S27-S35, S70, S110, S111, S119, S155, S172), every witness verified live against the clean binary; NONE was found already unreached (S70's own expiry had been repaired by the close lane — this makes the repair CHECKED). VALIDATED three ways with plants made and removed: an expired `SAB_REACH_EXPECT` -> UNREACHED/exit 1; a population floor above the count -> UNREACHED printing `=29(want>=999)`; `SAB_REQUIRE=asan` under a cc wrapper refusing `-fsanitize=` -> ANOMALY. That third plant found a defect in the mechanism's own prose (the ANOMALY sentence contained the token `UNDETECTED`, which the headline's `grep -c UNDETECTED` counted — a control sharing a source with its own subject); reworded, re-measured `undetected: 0`. Also added `VALIDATE_ONLY=1` (180 definitions checked in seconds, four malformed-field plants each a named FATAL + exit 2, and deliberately NOT the pollable `mech run COMPLETE` trailer). Solo canonical runs: S70 `reach:ok(2/2), reject:2fail/587pass, asrt:0fail/52pass` DETECTED; S155 `require:asan-ok, pop:framebuffer.rxt:/^gu frames /=4(want>=4), reach:ok(1/1), corpus:0fail/16pass, recdiff:0fail/10pass, framebuf:1fail/5pass` DETECTED. `make strict` clean; tripwire 180 sabotages / 191 anchor sites all resolve. **REMAINING BEFORE STATE:completed — the manager's FULL-MATRIX composite at merge (D69's CLOSE tier), which is the first run in which `unreached:` is measured across all 180 rows.**
- [TT-9] STATE:completed (MERGED ea4504b, 2026-08-25 ~14:3x, lane srRun/srRun2: tests/lib/san_scripts.txt is the ONE list `ubsan`/`asan`/`san` read (Makefile SAN_SCRIPTS); FIVE diff scripts were in none of the three — lookaround's two AND assertions' gstart/kreset/mline — all added, exclusion list starts empty; structural check in run_codegen_tests.sh validated red→green; `make -n` shows the three targets expand to one identical 33-script set) — formerly STATE:not-started — THE THREE SANITIZER SUITE LISTS ARE HAND-MAINTAINED COPIES (found by [DD-14] wave B+C, 2026-08-24): `make ubsan`/`asan`/`san` each carry their own list of suite scripts and nothing enforces agreement — the lane's first patch added `run_recursion_diff.sh` to ubsan's list only, and the san run silently never executed it (only the `-- san:` stage banner revealed it). Also: `tests/lookaround/`'s diff script is absent from all three lists with no stated reason. Charter: ONE list (a Makefile variable or a manifest file) that the three targets read, plus a check in `tests/codegen`/`make testscripts` that every `tests/*/run_*_diff.sh` is either in the list or named in an exclusion list with a reason (the SKIP-is-not-a-pass shape); add the lookaround diff or record why not. Small; a sonnet lane; lands with the next battery-touching wave.
- [TT-8] STATE:completed (CLOSED 2026-08-23 15:3x: full 118-row matrices on 6b0ef30 — PROCS=4 36:36, PROCS=6 28:43, both undetected 0 / anomalies 0, rows byte-identical bar S18's reject figure which is shards+1 → K30 (run_reject_tests.sh's --list-syntax guard runs in every shard); PROCS=6 is the documented matrix setting; yesterday's 60:08 → 28:43 (−31 min) from the timeout swap + the leak fix; the lane's 20-row sample one-liner was INVALID — the script takes one id prefix — so the sweep was done as two full matrices; the first full pass through the two-site applier was the no-op expected) — formerly STATE:started (2026-08-23, Frank's #3 + #4; (a)(b)(c) MERGED bbf7847: the leak was LIVE — PROCS=4 on a single row spawned 4 REJECT_SHARD_TOTAL=4 workers; fixed with INNER_PROCS=ncpu/PROCS passed explicitly on the reject/harness arms, S15/S107 figures byte-identical across leaked/serial/fixed; D69 evidence: 99 common rows m64↔m65, ZERO flipped DETECTED→UNDETECTED without their own definition changing; tests/mech/rows_for.sh maps changed paths→rows, failing-direction tested; OWED: the PROCS sweep (~20 rows at 3/4/6) and the full after-matrix — docs/dev/tt8_mech.md has the one-liners) —
  MECH: (a) the PROCS LEAK: run_sabotage_matrix.sh's PROCS (row
  concurrency) reaches the inner tests/harness/run.sh and reject sharding
  through the environment — fix so inner scripts get an explicit per-row
  PROCS budget (JOBS already divides; do the same for the inner shard
  width) and measure the matrix at PROCS=4 before/after, then re-validate
  PROCS at 118 rows (sample of ~20 rows at PROCS=3/4/6, then ONE full
  matrix at the chosen setting = the chain's mech "after" figure); (b)
  D69's evidence: diff the m64 (99 rows) and m65 (118 rows) matrices and
  any earlier matrix in the journal for a row that flipped verdict
  without its SAB_FILE/target changing; (c) document D69's tiered policy
  in docs/testing.md's mech section and tests/mech/CLAUDE.md.
- [SPEC-1] STATE:started (2026-08-25 ~12:5x, fortieth session; STEP 1 DONE — lane srSpec's read-only survey, committed as docs/dev/spec_survey.md: 54 gap rows in 7 sections, a 9-file proposed set, 10 ordered lanes, 5 stale findings — two confirmed by the manager: `cli/main.c:58`'s `--step-budget` help still says "bring-up placeholder" though D51 set 500,000,000 (`src/gen/emit_vm.c:133`), and `docs/pcre2_compliance.md`'s K34 annotation still reads OPEN vs D74. MANAGER RULING on [SPEC-1.9]: `docs/pcre2_compliance.md` is DECLARED SPEC-TIER IN PLACE — its three-component refresh discipline meets docs/spec/CLAUDE.md's bar and its tooling is path-keyed; docs/spec/CLAUDE.md lists it by reference (flagged to Frank; reverse if he wants the move). Sub-rows below; [SPEC-1.1] launched first as lane srLimits) — THE SPEC CONSOLIDATION PASS (Frank,
  2026-08-25, fortieth session, D80: "I think that time is now").
  `docs/spec/` is the dense CONTRACT — what we produce, its quirks and
  shortcomings — for the reader who needs to know EXACTLY what to expect
  (AI and contributor grade). Today it holds match_api.md (2,096 lines,
  the as-built match-API contract incl. §10 the frame buffer) and
  table_contract.md. STEP 1 (a read-only sonnet survey lane, no make):
  inventory every SURFACE pcrec ships against what the spec covers —
  the CLI (every flag, `--features`, `-f` axes, `--emit-*`, exit codes,
  diagnostics' D26 tier), the library entry, the emitted artifact's
  CONTRACT beyond the entries (the D46 stamp family, `rx_info`, the
  identity/abi rules of D76, what a caller may and may not depend on
  across abi bumps), the give-up/limit contract (D22/D49; the step,
  frames, trail, work limits with their numbers — D73's obligation
  lands HERE with the 684-byte example and K33), the module roster with
  each module's quirks and divergences (K34/D74's documented
  divergence; every known_issues K-row that is a shipped behaviour;
  the compliance page's caveats by construct), encodings/options
  (docs/pcre2_options.md is a disposition table — is it spec?), and
  the .rxt format (docs/testing.md owns it today — contributor-facing,
  so spec-tier). Deliverable: a gap table (surface → where it is
  stated today → spec home → size) and the proposed file set, for the
  manager to turn into [SPEC-1.n] rows; NOT the writing. STEP 2..n:
  one lane per document, each claim verified against the shipped
  surface (match_api.md's discipline: cite the header, the artifact,
  the test — never copy from a design doc), D6 critic on each. STANDING
  RULE from birth: any change to a contract updates docs/spec in the
  same change (CLAUDE.md situation index; reviewers check it on every
  merge). Runs concurrently with [CHK-1] — disjoint files.
- [SPEC-1.1] STATE:completed (MERGED fab1b62 + landing items 3dff2a6, 2026-08-25 ~13:1x: docs/spec/limits.md 261 lines, every number cited and re-measured — 684 B matches / 686 B gives up; rx_search frame 131,216 B; the K33 figure drift 131,296→131,216 corrected in known_issues + a D73 correction note; --step-budget/--work-budget help and the two pcrec.h sentinel comments name the D49/D51 defaults; the K34 annotation ruled via the annotation store; strict / test-cli 283/0 / test-registry pc4 62,872 cells 0 / test-stackdepth green solo on main) — formerly STATE:started (lane srLimits, 2026-08-25 ~13:0x) — `docs/spec/limits.md`: the give-up/limit contract consolidated — D22's frame, the four codes (pointer to match_api §4), the numbers (step 500,000,000 D51; work ~10⁹ D49; frames/trail 2048/3072 D73 with the 684-byte `^(a(?1)?b)$` example RE-MEASURED; compile budgets D45), K33 + the `_in` remedy (pointer to §10), K34/D74 the documented divergence; plus the two stale fixes: `cli/main.c:58` wording and the K34 compliance annotation through the annotation store + refresh procedure. THE direct discharge of D73/D80.
- [SPEC-1.2] STATE:completed (MERGED 2026-08-25 ~14:5x, lane srCli: docs/spec/cli.md 386 lines; every flag verified on a live run + cli/main.c line; module table 8 built / 9 unbuilt measured from --list-syntax; exit codes 0/1/3 each with its producing command, 3 being --explain dissent only, currently unreproducible by design (case11 asserts zero); strict + test-cli 283/0) — formerly STATE:not-started — `docs/spec/cli.md`: the full flag reference (survey A1-A14; stubs into tuning/registry/diagnostics). P1; parallel with 1.1.
- [SPEC-1.3] STATE:completed (MERGED 2026-08-25 ~19:0x, lane srTuning: docs/spec/tuning.md 468 lines — every axis's stamp verified by an artifact diff, the masked/unmasked split confirmed against emit_dfa.c's strategy_denials, five differentials re-run with 0 diverged, prefilter named as the one axis without its own differential; FOUND: lib/pcrec.h named a stamp `<PREFIX>_VM_CALLS` that never shipped — fixed by the manager at merge to the two real counts) — formerly STATE:not-started — `docs/spec/tuning.md`: the `-f`/`-fno-` family, `--unroll=`, `--engine=` caller-side; byte-identity vs engine-selecting per flag (survey A7/F5). P1; parallel.
- [SPEC-1.4] STATE:completed (lane srK38, sonnet, 2026-08-26, commit 8d18b93) — match_api.md patches (survey: D3 pointer, C2, C4 D76 abi paragraph, F6 byte-only encoding lead, F9 whole-subject subsection) with a dated revision-log entry — was: started (STARTED 2026-08-26 ~12:0x, after K38-FIX). CLOSED: §4 gains a docs/spec/limits.md pointer for the give-up codes' numeric defaults (D3); §6.3's DFA-stamp-gap caveat re-verified against a fresh DFA/hybrid build — already discharged by [DD-13c], nothing changed in prose (C2, "verified, nothing to change" per the survey's own allowance); §6 gains a caller-facing abi paragraph restating D76 in contract terms, rx_info.abi confirmed 6 (C4); §8.2 now leads with "byte is the only encoding implemented today" (F6); new §3.6 states the (?:P)\z whole-subject idiom, the a|ab counter-example, D77/[OS-4]'s ruled-permanent status, and the idiom's own DFA stamps, every claim verified live against a fresh build rather than asserted (F9). docs/spec/CLAUDE.md's match_api.md entry updated to match; make test-cli (287/287) green after (doc-only change, no code touched).
- [SPEC-1.5] STATE:completed (MERGED cf551d4, 2026-08-25 ~19:4x, lane srReg: docs/spec/registry.md 228 lines — every column of the three TSV surfaces by header name with its value set measured live (128/50/90 rows), the append-only/resolve-by-name promise, built vs status/roadmap, the family rule, what registry_check vs PC-3 pin; drift: tests/registry/CLAUDE.md's '100 rows' → 128, fixed at merge) — formerly STATE:not-started — `docs/spec/registry.md`: the `--list-*` TSV column contract (A8). P2.
- [SPEC-1.6] STATE:completed (MERGED 962e2de, 2026-08-25 ~19:1x, lane srRxt: docs/spec/rxt_format.md 379 lines, the format/driver protocol/how-to-add moved out of testing.md with a line-range table; four prose-vs-parser drifts fixed — `perr` requires exit EXACTLY 1, the driver's exit-4 anchored-entry cross-check was undocumented anywhere, RXTFLAGS had no env row, the 'harness hardening' timeouts were pre-D45; anchors updated tree-wide incl. the manager skill; test-corpus 26,560/0 at PROCS=4) — formerly STATE:not-started — `docs/spec/rxt_format.md`: extraction of the .rxt format/driver protocol from docs/testing.md ~124-435 (F3); testing.md keeps the DEVDOC rest. P2, mechanical.
- [SPEC-1.7] STATE:completed (folded into cli.md §3 by srCli, 2026-08-25) — `diagnostics.md` or a cli.md section: D26 tiers caller-side, the offset-pinning convention (A13). Small.
- [SPEC-1.8] STATE:completed (folded into cli.md §1 `--features` table + §4 by srCli, 2026-08-25) — `modules.md` or cli.md's `--features` section: the 17-name map with status, pointing into pcre2_compliance.md (A10/E). Small.
- [SPEC-1.9] STATE:completed-in-place (CONFIRMED by Frank 2026-08-28 ("6 ok"); manager ruling above: pcre2_compliance.md declared spec-tier in place; docs/spec/CLAUDE.md lists it by reference — lands with 1.1).
- [SPEC-1.11] STATE:not-started (BOONIES TIER — LATE GAME; Frank, 2026-08-29 forty-fifth session, filed UNPLANNED "(ironic)": a doc plan item for a spec on UPGRADING pcrec) — THE EXTENDER'S SPEC, `docs/spec/extending.md` (name provisional): the recipe-per-extension-kind contract for anyone who grows the compiler AFTER 1.0 — how to add a [DD-11] replacement/definition row (predicate + core-syntax definition; the per-row checks and sabotage rows that must land with it; `--list-definitions` shows it), a registry `RegRow` (D24; the four/five registry surfaces it must appear on and the checks that prove it — PC-3, `--list-syntax`, the reject table), a feature MODULE (parser hook + lowering + tests/<module>/ + "requires module" refusal + compliance-refresh), an emitter FORM / representation object ([ENG-FORM]/D82: one object + one accessor block, its stamp, its deny/force axis row, the form-census floor, the `make test-axes` identity sweep), a STAMP (D81 naming, one derivation two readers, the ABSENCE-as-discriminator hazard), a LIMIT (limits.md's cited-and-re-measured rule, raise-only overrides per D84), an .rxt block kind ([DD-13b]'s grammar), and the ABI ritual (D76's four sites) — each recipe naming the checks that must move in the same change and the spec file that must gain its hunk (D80). It is a SPEC (contract) tier document per D80, not a guide: it says what an upgrade MUST do to be accepted, and points at the design notes for why. WHY LATE: every recipe is a restatement of a mechanism that is still moving ([DD-11]'s table, [DD-13b]'s grammar, the abi resetting to 1 at 1.0); written earlier it drifts with each lane (learnings §3's "one derivation" applies to prose too — the recipes should be written against the STABLE surfaces and, where a surface is listable, say "run `--list-X`" instead of restating the table). Trigger: after [DD-11] and [DD-13b]'s parsers land and the registry surfaces stop growing, or at the 1.0 release-doc pass, whichever is first. Starts only on Frank's word.
- [SPEC-1.10] STATE:not-started — survey debt: the sabotage-row format (F4, tests/mech/CLAUDE.md); K2's status (known_issues K2 says "fix with module backrefs" — backrefs shipped 08-22, no FIXED marker); table_contract.md's `--emit-ir` note vs [DD-8] — RESOLVED by srCli: [DD-8] still not-started, the note is CURRENT; README/APPROACH as the stranger's real first read (→ [GUIDE-1]/[REL-META]).
- [GUIDE-1] STATE:not-started — THE USER GUIDE, `docs/guide/` (Frank,
  2026-08-25, D80; LOWER PRIORITY, "basically maintained", NO edge-case
  details). A simplified, human-facing guide organized by USE CASE —
  compile a pattern into your program (search / match / captures /
  named results); the anchored and whole-subject idioms (`(?:P)\z`);
  choosing engine and options; when the matcher gives up and what to do
  (the `_in` entries for deep recursion — D73's obligation at guide
  depth: one paragraph pointing at the spec); embedding the generated
  file (no runtime dependency, the abi stamp); using the CLI vs the
  library. References the spec for details, never restates it. Starts
  after [SPEC-1] has the limits section it would point at; [REL-META]'s
  README pass then references the guide.
- [REL-META] STATE:not-started — (RULED 2026-08-28, Frank: the emitted `abi` number RESETS TO 1 at the 1.0 release — D81 addendum; a release-mechanics item on this row.) USER-DOCS OBLIGATION (Frank, 2026-08-24, D73; RE-HOMED 2026-08-25 by D80 — the numbers and mechanism go in [SPEC-1]'s limits section, the use-case paragraph in [GUIDE-1]; this row's README pass references the guide): the recursion frame/trail default (2048/3072), the subject size it implies for recursive patterns (`^(a(?1)?b)$` gives up at a 684-byte subject), the musl/small-thread-stack caveat (K33) and the caller-provided buffer (`_in` entries) as the remedy must be in the user docs and the release note — not a footnote. META-PLAN ROW for FIRST-RELEASE +
  CONTRIBUTION READINESS (Frank, 2026-08-21, thirty-fifth session:
  "we are within a few solid efforts of having a first release"; this
  row's deliverable is the ROW SET, not the work — [SIMD-META]'s
  pattern). Charter: survey what a first public release and an
  open-to-PRs posture actually require, and propose the concrete rows
  for Frank to ratify. KNOWN CANDIDATES from the chartering
  discussion, to be sized and split by this row: (a) CONTRIBUTING.md +
  PR template + the RUN-STAMP (`make test` emits tree-SHA/dirty-flag/
  counts/duration; the template asks for the paste — catches
  honest-mistake cases: wrong commit, subset, misread red; fraud is
  explicitly a non-goal, provenance-imitation lesson applies) — mostly
  distillation of existing house rules into contributor-sized form
  (oracle-verified expectations WITH the oracle named; module/refusal
  conventions; D26 tiering; CLAUDE.md maintenance travels with
  changes; exact-count checks self-enforce). (b) CI on GitHub Actions
  — FREE for public repos on standard runners (the minutes quota that
  burned Frank's other project is a private-repo constraint);
  fork-PR flow confirmed (fork -> PR, no access granted, first-time
  contributors' workflow runs gated on maintainer approval, no secrets
  exposed — none needed: gcc+make+libpcre2-8-0); TIERING per house
  discipline: per-PR = test+strict; sanitizers/mech = merge or
  nightly; the GATE NEVER runs in CI (shared runners are a loaded box
  — floor-gate-under-load is contamination by our own rule; the gate
  stays maintainer-side quiet-box); self-hosted runners explicitly
  REJECTED for fork PRs (strangers' code on the box). (c) README
  release-adequacy pass + user-facing quickstart. (d) versioning +
  changelog + release mechanics (tag discipline, what "release" means
  for an AOT compiler — source-only vs artifacts). (e) whatever the
  survey finds that this list missed — the survey asks "what does a
  stranger's first hour with this repo hit", which the chartering
  discussion did not walk. Sequencing: the meta-survey is a read-only
  sonnet lane, schedulable any time; the resulting rows land where
  Frank rules
- [V-A] STATE:not-started — PCRE2 compatibility layer: a drop-in surface for callers who already speak PCRE2, so adopting pcrec does not mean rewriting call sites. Interacts with DD-3 (generated-API versioning) — a compat layer is a second consumer of the generated contract. TWO surfaces (Frank, 2026-08-12): the PCRE2-native API, and a POSIX `regex.h` shim (regcomp/regexec/regfree, à la pcre2posix) — a smaller surface with wider adoption reach, since decades of C code speaks regex.h and never touched PCRE2
- [V-B] STATE:not-started — usage libraries for other languages: bindings over the generated C. Note the generated code already has no runtime dependency on pcrec, which is what makes this cheap; keep it that way
- [V-C] STATE:not-started — a grep CLI built on pcrec, the natural end-user demonstration that the speed mandate (D18) actually shows up in a real tool
- [V-D] STATE:not-started (CROSS-NOTE 2026-08-19: [DD-11]'s definitions architecture makes this row cheaper than its design note assumed — a flavour = front end + BINDING LIBRARY over the reduced core; but read DD-11 note (h)'s honest limit: POSIX leftmost-LONGEST is core preference semantics, not a binding) — translators from other regex syntaxes into the base tier: grep/egrep (BRE/ERE), python `re`, and PCRE2-flavour differences. Pairs with V-C (a grep CLI needs BRE/ERE) and with V-A. Design note: these are FRONT-END modules that lower into the existing AST, exactly the shape APPROACH §3's parser extension points already anticipate — no engine work, which is what makes the direction affordable
- [LIB] STATE:not-started — SUBPATTERN LIBRARIES (RULED 2026-08-28, Frank: "depends on rxt format" — the row BLOCKS on [DD-13b], the .rxt format half; the spine question is not asked again until that lands. Frank, 2026-08-24, thirty-ninth session; PLANNED — its place relative to the spine is NOT ruled (Frank ~22:0x: "planned but I don't know that I'd put them on the spine"); to be discussed at [DD-14]'s close): (1) the .rxt format grows so a file can carry MULTIPLE patterns that reference each other through SUBROUTINE CALLS (definitions + patterns in one file, the way [DD-14] is being built); (2) the same mechanism user-facing — a user INCLUDES a library of named subpatterns and calls them from a pattern by name; (3) pcrec SHIPS a LIBRARY STORE of tested subpatterns (email address, IP address, quoted string, HTML pieces, …). Relations: [DD-11] (scope-resolved definitions whose values are inserted — this row is that architecture's user-facing form; a library is a definitions scope), [V-E] (multi-pattern compilation units — the unit boundary), [DD-14.G] (splice + dead-capture elision is what makes a library subpattern cost NOTHING: the artifact byte-identical to the hand-inlined pattern — the email specimen's bar), [DD-14.F] (the DEFINE row is the in-pattern spelling of a definition). Design points to settle at charter: NAME RESOLUTION (pattern's own groups first, then included libraries in order; collisions refused by name; PCRE2 has no include, so this is pcrec's compile-time namespace — the oracle sees the EXPANDED pattern, which makes the harness's expansion the SPLICE-vs-LINKAGE `A == B` control by construction); the .rxt directives (`define name <pattern>` / `lib <file>` per file or block; the harness expands for libpcre2 and passes the library to pcrec); the API surface (`pcrec_options` gains a definitions input; CLI `--lib FILE`; versioning per [DD-3]); the STORE's discipline (each entry oracle-verified, a D27-blinded author writes its corpus, pcrec-bench carries it as a benchmark row; the RFC 5322 email specimen is entry #1). Depends on [DD-14] closing (G in particular). Not started unprompted; the charter conversation opens at [DD-14]'s close with the post-spine direction note (journal 2026-08-24).
- [V-E] STATE:not-started — MULTI-PATTERN COMPILATION UNITS and the DESIGN INPUT (Frank, 2026-08-26 ~21:1x, recorded, NOT chartered — no new effort at 95 % of the subscription): make `struct rx_info` the IDENTITY of a pattern in a multi-pattern unit, not the symbol prefix — (1) a nested struct of ENTRY-POINT function pointers (search / match / match_caps / the `_in` variants / info) in rx_info — the external entry surface only; D82's per-machine inline accessors (step/dead/accept) never go behind a pointer; a direct-call caller keeps the named symbol; (2) the user-facing NAME (today's prefix) + the pattern source in rx_info, so the emitter DERIVES unique C symbols per pattern and nobody types prefixes beyond a few patterns; (3) one unit-level `const struct rx_info *const <unit>_patterns[]` + count, so a caller finds an implementation by ANY rx_info field (name, source, engine, ncaps…) with a linear scan and an emitted 10-line helper (generated code stays dependency-free). Consequences: an abi bump (append at the end, the [DD-13c] shape); the first consumer is pcrec-bench's shim (40 `pb_*` accessors over rx_info today) at its first multi-pattern sub-bench — D77's trigger for the runtime surface. Two additions (Frank, ~21:2x): (4) emit the unit-level array SORTED BY NAME so lookup by name is a binary search (the emitter knows every name at generation time; the sort order is a stated contract and a check reads it off the artifact); (5) the whole surface — entry-point pointers, name, the unit array and its helper — is an OPTIONAL emit ([EMIT-SET]'s shape: a caller who only uses direct symbol calls pays nothing for a table it never reads; the deny flag masks it out of the file, answer-identity unaffected).
  CROSS-PATTERN FINDER (Frank, 2026-08-12; boonies tier by his word —
  recorded now, built with a customer). N named regexes into ONE emitted
  file: per-pattern named entry points exactly as today (a statically-known
  caller pays no dispatch — D20's rule holds), SHARED DATA deduplicated by
  CONTENT (the driver is M5: a dozen patterns each carrying a private copy
  of the unicode tables adds up; share by content hash, so sharing is only
  ever dedup of identical bytes and never forces a pattern's specialized
  table into a common shape), and OS-0's finder generalized by ONE AXIS:
  D20's selector already dispatches over option-combinations of one
  pattern; the same interface selects the PATTERN too. **This is OS-0's
  candidate FIRST CUSTOMER** — the finder was deferred for lack of one.
  D20's two structural properties still bind: dispatch resolves once per
  call and never reaches the hot loop; a single-pattern single-option
  request emits byte-for-byte today's output. Usage modes to design BEFORE
  building (Frank: "we should think about how it's used"): CLI
  multi-pattern args with per-pattern names, and a manifest file for build
  integration ([V-F] is the third consumer). NOTE (Frank, 2026-08-13):
  this row also answers two use-case questions from the positioning
  discussion — the system for ORGANIZING/FINDING the regex functions you
  have compiled is this row's finder + named entry points, and the
  MANIFEST is the user-facing FILE FORMAT for specifying regexes (name,
  pattern, flags, encoding per entry → one compiled unit); design the
  manifest as a first-class user surface, not a build artifact.
  AMENDED 2026-08-13 (Frank, composition discussion; syntax and semantic
  choices TBD, his to rule): the manifest gains NAMED DEFINITIONS with
  CROSS-REFERENCES — `regexa = abc|def` usable inside a later
  `regexb = xyz(<regexa>)*` — making the file a module system for
  regexes, built up in steps. TWO COMPOSITION TIERS, kept distinct:
  SOURCE-LEVEL (manifest references, AST-inlined at compile time — zero
  runtime cost, DFA compilability preserved, the default) and LINK-LEVEL
  (M4-CALLOUTS' aligned ABI, for separately-compiled parts and
  non-regex predicates). OPEN CHOICE (Frank's, Q2/K4-tier — measured,
  never read from docs): PCRE2 spelling via (?(DEFINE))/(?&name) desugar
  — composed pattern is valid PCRE2, libpcre2 becomes the oracle for the
  composed form, but subroutine-call semantics are ATOMIC and shift
  capture numbering — vs own reference spelling with plain inlining
  semantics (beyond-PCRE2, clean namespace, same shape as M4-SUBST's
  ruling). Reference CYCLES are rejected with a clean diagnostic (true
  recursion is non-regular; a future VM-side module's business, never
  inlining's). Positioning parity note: re2c and lex/flex both ship
  named-definition composition — established practice in exactly our
  claimed niche; PCRE2 semantics on top is the differentiator.
  AMENDED 2026-08-14 (D39.2, `docs/dev/decisions.md`): rx-reference group
  numbering is APPENDED — the primary keeps its own 1..N stable; each
  inserted regex's groups append at N+1.. in insertion order; names are
  kept, and D39.1's exported name→number index is the lookup path.
  Backrefs inside an inserted regex renumber to their appended positions
  at insert time (compile-time). The name-collision policy RESOLVED by
  the D39 addendum: caller-supplied LABELED REFERENCES per insertion
  ("a:reg1", "b:reg1"), stored as the index's `ref` column; nested
  insertions compose a path ("c:a"). Still open, ruled at V-E design
  time: path spelling/separator, label mandatory-vs-optional for single
  insertions, and lookup-key semantics (name-alone when unambiguous vs
  ref+name). FORMAT OWNERSHIP MOVED 2026-08-17: the manifest FILE
  FORMAT itself is designed at [DD-13] (one unified format serving the
  manifest, the test carrier, and pcrec-bench's sets); this row keeps
  the compilation-unit + finder BUILD and its semantic rulings, which
  [DD-13] inherits as constraints
- [V-F] STATE:not-started — the SOURCE-SCAN TRANSFORMER (Frank, 2026-08-12,
  same discussion, same tier): scan a C program's sources for regex
  markers — `auto regex = rx/abc|def/` shaped — and rewrite them to
  references into a pcrec-compiled companion unit ([V-E]'s output format is
  the natural target). re2c/lex-shaped build tool. The dogfooding
  constraint IS the design constraint (Frank: the scanner uses a regex we
  compiled): the marker grammar must be REGULAR and unambiguous amid C
  strings/comments — chosen to be findable by the tool being sold, which
  makes the scanner both the demo and the spec. Do not start without a
  marker-grammar design note answering: escaping inside `rx/.../`, flags
  syntax, occurrences inside string literals and comments (skip or honor,
  and how a regular scanner distinguishes them)
- [V-G] STATE:not-started — USER-FACING REGEX TESTING (Frank, 2026-08-13,
  positioning discussion; boonies tier): expose the project's own dev
  testing machinery to a developer wishing to test THEIR regexes — the
  .rxt corpus format, the harness runner, and (where installed) the
  python-re / libpcre2 oracle differentials, as a `pcrec test`-shaped
  surface: write cases for your pattern, run them against your compiled
  matcher, optionally cross-check against the oracles. The machinery
  exists and is battle-proven (docs/testing.md); the work is packaging,
  scope (which harness features are user-grade vs dev-only), and docs —
  a docs/spec/ candidate when built. Nobody in the niche ships a regex
  TESTING story; this makes the verification story a user capability,
  not just an internal discipline. AMENDED 2026-08-13 (Frank, composition
  discussion): rides [V-E]'s named definitions — every named part of a
  manifest is independently compilable, so subpart testing is the .rxt
  harness pointed at each definition, per-part expectations in the same
  file; complex regexes become testable in steps, bottom-up
- [V-H] STATE:not-started — DEBUG / TRACE EMISSION MODES (Frank,
  2026-08-13, same discussion; boonies tier): generation-time variants
  that aid understanding and debugging a matcher — a TRACING build
  (emitted matcher logs state transitions, positions, prefilter/skip
  entry/exit; a SEPARATE emitted variant per D18, zero cost in the normal
  emission — never a runtime flag in the hot loop), a VERBOSE compile
  mode narrating compilation decisions (prefilter chosen, skip states,
  trie factoring, caps hit), and the compile-time introspection DD-8
  already owes (--emit-ir / --emit-dot — that row stays the owner of
  those two surfaces; this row is the run-time half). Pairs with [V-G]:
  a failing user test plus a traced matcher is a debugging story no
  regex library offers. TRACE ENRICHMENT NOTE (Frank, 2026-08-21,
  thirty-fifth session — details/design TBD, stays boonies): revisit
  what --trace's emitted instrumentation SAYS — today it narrates
  engine mechanics (push/pop frames, state transitions); Frank wants it
  to also point at the position IN THE PATTERN being worked on (which
  construct — the `\n`, the quantifier — the engine is currently
  matching against, i.e. a pattern-offset/construct reference on trace
  events) and generally describe MORE than frame traffic. The emitter
  knows the pattern offset per emitted site at generation time, so this
  is plumbing generation-time knowledge into the trace strings — same
  family as the [M6-READ] legends (emitter-owned data rendered for a
  reader), which is the natural design starting point. If an enriched
  trace mode ever emits TABULAR output it adopts docs/spec/
  table_contract.md at birth

- [SAFEKILL] archived to plan_completed.md (completed 2026-08-19, thirty-fourth session — scripts/safekill merged db8ddde, all three phases; scripts/tests/safekill.test 13/13 under make testscripts; row flipped 2026-08-22 at the thirty-sixth session's wake-up, where the omission was found)
- [EMIT-SET] STATE:not-started — CONTROL OF WHAT IS EMITTED INTO THE C FILE (Frank, 2026-08-24, thirty-ninth session): a caller who only uses `match` does not need `search`; one who never reflects does not need `rx_info`; `main` folds into the same switch — `--emit -search,-rx_info,main` (a comma list of named EMISSION UNITS, `-` removes, bare name adds, defaults = today's artifact). The point beyond trimming: once emission is a SET of named units, VALUE-ADD units become drop-ins on the same switch — the results → static-struct copy helper ([V-I]), the compiled search/replace code ([M4-SUBST]), rx code-management helpers (versioning/identity stamps a consumer can query), the diagnostic variants ([V-H] `--trace`/[ENG-PGO] `--profile` are the same shape: a separate emitted variant selected at generation time), the caller-provided-buffer `_in` entries ([DD-14.FB] — a unit a caller may drop), a [LIB] library's shared regions. Design points at charter: the unit graph (dependencies — `main` needs `search`; `_in` needs the run struct; `rx_info` fields some units reference) resolved at generation with a clean refusal for an inconsistent set (D26 tier 3 wording); the [ABI-NS]/structural codegen checks become per-unit (a unit's presence/absence is a byte-level fact the identity gates assert — the default set byte-identical to today's artifact, the control); `--list-emit` prints the units and their defaults; the CLI/library API surface (`pcrec_options` gains the set; DD-3 versioning). D18's principle applied to the artifact's SURFACE: what is not emitted costs nothing, and a unit nobody asked for is not there to be wrong. Relations: `--emit-main` (today's only switch, becomes the `main` unit), OS-0's named-entry-point discipline, [DD-8] (`--emit-ir`/`--emit-dot` are OUTPUT formats, not units — keep them apart). Not started unprompted; PLANNED, its spine status deliberately open (Frank, 2026-08-24 ~22:0x) — the going-forward conversation at [DD-14]'s close decides.
- [PAT-LINT] STATE:not-started — OPTIONAL PATTERN ANALYSIS: an ahead-of-time
  check that names issues in a pattern the engines will accept but that
  behave badly (Frank, 2026-08-25, fortieth session, from the K34 ruling
  D74; PARKED — no queue position; details and design TBD). The charter
  case: ZERO-PROGRESS LEFT RECURSION — `(a|(?1)a)b` re-enters group 1 at
  the same subject position before consuming, so every non-matching
  subject is a runaway (pcrec gives up `frames`, PCRE2 concludes only by
  an implementation artefact, D74); the same language as `(a(?1)?)b` or
  `a+b`, which recurse after consuming and conclude in both engines.
  Rule 1: a call edge to group G reachable from G's own entry through a
  ZERO-MINIMUM-WIDTH prefix (the compiler already computes minimum widths
  — wave E's root-minw guard — so the analysis is a walk over facts it
  has). WARNING, NEVER A REFUSAL: the pattern is legal and matches on
  positive subjects; §3.3's deliberate same-position recursion with a
  base case is not a defect (the analysis says "may not terminate on
  non-matching input", not "wrong"). Other candidates for the same
  surface, each to be measured for a real occurrence before it is built:
  nested unbounded quantifiers over overlapping languages (the classic
  `(a+)+b` catastrophic-backtracking shape — relevant only where pcrec
  picks the VM engine; the DFA is immune, so the analysis must report
  ENGINE-AWARE, else it warns about a pattern that runs in linear time);
  empty-language callees (already refused at wave E — a diagnostic tier
  question whether it moves here); a dead group that never captures
  (wave G's elision list — informational). SURFACE TBD: a CLI flag
  (`--analyze` / `-W`) whose output is text, or a library entry; the
  D38 naming rules apply to any stamped result. Interacts with [V-G]
  (user-facing regex testing — the natural home if that lands first) and
  [V-H] (trace modes show the runaway; this names it before running).
  NOT QUEUED — parks behind the general work per the boonies discipline.
- [V-I] STATE:not-started — NAMED-RESULTS COPY HELPER (Frank, 2026-08-18,
  thirty-third session; LOW PRIORITY, boonies tier; details and design
  TBD): an emitted per-pattern helper that takes a search's results —
  in particular a captures-delivering search, most particularly one with
  NAMED groups — and copies them into a STATIC STRUCTURE keyed by the
  group names (the natural shape: an emitted `struct <prefix>_groups`
  with one span member per named group, plus a copier from the caps
  array). Generation-time is what makes it cheap: pcrec knows every name
  at emit time, and [M6.3]'s name grammar ([A-Za-z_][A-Za-z0-9_]{0,127})
  makes every group name a lexically valid C identifier ALMOST for free
  — the TBD wrinkles already visible: C KEYWORDS are valid group names
  but invalid member names (`(?<int>...)`, `(?<return>...)` need a
  mangling rule), and D61's caps-layout promise plus rx_group_entry.slot
  are the substrate the copier reads through (slot-aware from birth, so
  a future ref-bearing row costs nothing). Interacts with [V-B]
  (bindings would love the same struct) and the D38 naming rules. NOT
  QUEUED — parks behind the general work per the boonies discipline

- [SIMD-META] STATE:not-started — META-PLAN ROW for the studies/simd1
  research (Frank, 2026-08-16, at adoption): a thinking/triage row whose
  DELIVERABLE IS PLAN ROWS — "wrap most of it into a meta-plan item that
  thinks about how to use this research and which would create those plan
  items." Do not spawn per-finding rows ahead of it; this row decides
  which follow-ups exist and their shapes. The two integration hypotheses
  it must weigh (Frank's framing): (1) PRE-SEARCH — the study's §14
  find-all mode as an exact anchor source feeding the engine (its
  contract was designed for exactly this; touches M4.6's
  prefilter/islands territory and V-C's grep CLI); (2) SNIPPETS INTO
  REGEX PROPER — "some findings suggest snippets could be integrated
  into regex proper if the statistical analysis held up": the §3
  position-encoder menu, §15 run extension for [class]+ atoms, and
  literal-factor scanning emitted INLINE in generated matchers as a SIMD
  emission tier under D18 — gated on the §16 exemplar-statistics /
  background-frequency machinery actually predicting well (the
  "statistical analysis holds up" condition; folds in the [ENG-PGO]
  profile-guided-generation idea from the adoption discussion — the
  exemplar axis is an input to BOTH hypotheses, not its own island).
  Constraints the meta-row must answer, not inherit silently: generated
  code is today SELF-CONTAINED gcc-dialect C with no CPU dispatch — a
  SIMD tier raises ISA flags (-mavx2), runtime dispatch vs
  generation-axis targeting, and fallback tiers (the study's §11
  ~10-macro ISA layer is the candidate shape); every study number is
  Zen 1 and must be RE-MEASURED before load-bearing use (D12/bench
  discipline); reconcile with DD-9/[BENCH-1]'s case-(f) worklist row
  (the study's §12-B shift-and measurement bears directly on it —
  studies/simd1/CLAUDE.md flags this) rather than duplicating it.
  Output: a short design note (panel-eligible) + the created rows.
  AMENDED 2026-08-16 (Frank, twenty-seventh session, during the counter-K
  arc): SCALAR-FIRST is the ruled integration posture — figure out how
  SIMD plays in OVERALL before any of it touches current work; the ideal
  shape is "our best non-SIMD approach, then backend VARIANTS on top of
  it". Consequences: (a) in-flight engine lanes take NO SIMD-derived
  design inputs or bench cells (three counter-K bench items sourced from
  studies/simd1 were retracted under this directive the day it was
  given); (b) thinking and planning ARE in-scope and live HERE — two
  parked observations from the counter-K arc are this row's first
  evaluation inputs: (1) counter-K's one-body-copy emission is the
  natural substitution site for a §15-style SIMD run-extension variant
  (one site per quantifier vs N replicated copies — an argument the
  backend-variant layering is cheap over the counter design, worth
  verifying when this row opens); (2) the `#pragma GCC unroll` question
  (simd1 JOURNAL.md:63 — could a pragma replace manual K-copy emission
  on frameless arms?) is parked here, NOT in counter-K's bench, until
  the variants architecture is thought through.

M4-hosted, boonies-queued (Frank's queue discipline places these after the
spine, not before):

- [ENG-THIN] STATE:not-started — MRL CLAMP GATING/THINNING (Frank,
  2026-08-17, twenty-ninth session, ruled at the [M4.6d] accept-as-is
  decision — D51 addendum has the accepted +8% residual this row exists
  to shrink): decide per PATTERN — or per SITE — whether the MRL clamp
  is emitted at all. SOUNDNESS-FREE BY CONSTRUCTION: with or without
  the clamp the VM returns identical answers (the 202,458-cell [M4.6d]
  differential is the demonstration); gating errors cost budget
  exposure or overhead, never wrong answers, so this is pure
  measure-then-implement optimization. TWO HALVES, Frank's two
  questions verbatim: (1) ANALYTIC, compile-time — the k23_design.md
  closed-form step law (validated exact out of sample) gives a
  worst-case unclamped step bound per pattern; clamp only where that
  bound exceeds a threshold against the step budget. Boolean
  is-it-ambiguous gating is NOT sufficient — the +8% shape
  ([a-z]{2,4}){2,8}b IS ambiguous-class; the gate must be
  quantitative. Conservative generalization of the law is this row's
  engineering; when uncertain, KEEP the clamp (wrong-keep costs <=8%
  on a bad shape, wrong-skip costs an honest refusal, neither is
  unsound). Per-site refinement: clamp only quantifiers participating
  in nests whose bound exceeds threshold. (2) EXEMPLAR-STATISTICAL —
  owned by [ENG-PGO], linked: given representative subjects ([DD-13]'s
  exemplar file references are the designed carrier), tune the COST
  side where (1) says the clamp is not strictly needed; exemplar
  stats must never override the safety side (tail inputs are exactly
  what exemplars do not show; DD-2's budget refusal stays the
  backstop). If a caller wants both variants, OS-0's named entry
  points are the D18-compliant shape — no hot-loop dispatch.
  REGRESSION TRIPWIRES already in place: run_mrl_tests.sh §1b (the
  8-step counter-rung acceptance cell) and
  tests/base/d27_k23_ambiguous_decomposition.rxt (89 blinded cells) —
  over-thinning that reintroduces a K23-class blowup fails both,
  loudly. Schedule: boonies-queued with a natural measurement window
  alongside [M4.6e]'s VM perf work.
- [ENG-PGO] STATE:not-started — (CROSS-NOTE 2026-08-29, Frank: the FINDINGS FILE is an .rxt — a `freq <name>` DATA block (a byte-frequency table) that a target's config references; docs/design/dd13_format/frank_inputs.md 2026-08-29, usecases_and_outline.md §6.5; blocks on [DD-13b] wave 2/3.) D83 (2026-08-28) RULES THE SHAPE: exemplar analysis runs OUTSIDE pcrec, once per file, delivering a FINDINGS FILE pcrec accepts; FILE-GENERAL findings (byte frequencies etc., pattern-independent, one exemplar serves many patterns) and PATTERN-SPECIFIC findings (a statistics-recording special compilation, built only for a specific question, later) are two result files and two builds. The bench's [B11.1] presence counts are the first exhibit. FIRST CONCRETE QUESTION for the profile attachment (Frank, 2026-08-25 ~21:2x, at the [OPT-1] two-tier ruling): the tier design is a BET that the fast tier holds the overwhelming majority of real calls; a `--profile` variant run over an EXEMPLAR subject file would put a number on it — the escalation count (FRAMES → deep tier) per call, per pattern, per subject class — and is the trigger D79 names, made concrete: build the profiler when the loop needs this number, and this is the number. CHEAP FIRST STEP (srTier, 2026-08-25): the `-DRX_TEST_TIER_HOOK` build of a tiered artifact already counts escalations per call — a driver over an exemplar subject file yields the escalation rate WITHOUT the profiler; charter that as [OPT-1]'s follow-up measurement before any profiler design. (Cross-note continues.) — CROSS-NOTE (Frank, 2026-08-24, thirty-ninth session, direction not decision): the `--profile` emission mode below gains a SECOND CUSTOMER — the post-spine pcrec-bench OPTIMIZATION LOOP (journal 2026-08-24 direction note): a PROFILE ATTACHMENT on a compiled pattern that says where the matcher spends its time BY SECTION (prefilter scan, skip loop, VM attempt, per rung) and, where possible, in smaller increments, run over a variety of scenarios, to guide optimization PRIORITY — `--trace` is the debugging tool, the profile is the optimization tool. Design starting points (manager, same day): time attribution needs cycle deltas (`rdtsc`/`clock_gettime`) at the section boundaries the emitter already names, not counts alone; the computed-goto labels are natural fine increments (count + cycles per label = a per-construct profile with no `perf`/symbolizer), and can carry the pattern offset the [V-H] trace-enrichment note wants; the profile struct is read through an `rx_info`-shaped accessor; the artifact stamps that it is the profile variant (identity gate: the default artifact is byte-identical across the axis). Same [V-H] namespace as D71.1's counter axis — a second diagnostic axis is the trigger D71 names for designing the GROUP rather than the flag. PROFILE-GUIDED GENERATION (Frank,
  2026-08-16, twenty-seventh session — promoted from the parenthetical
  inside [SIMD-META] to its own row at his ask; the SIMD-META exemplar-axis
  mention now points here). TWO NAMED CUSTOMERS as of 2026-08-17 (D53
  addendum): (1) [ENG-THIN]'s clamp-cost tuning; (2) HYBRID-VS-VM-ONLY
  ENGINE SELECTION per pattern — D53 killed the runtime length branch
  (the deciding variable is match OFFSET, unknowable pre-search), but
  the offset DISTRIBUTION is a static workload fact an exemplar file
  exposes; preferred form is pure PGO (build both variants, run the
  exemplars, keep the measured winner — absorbing per-attempt-cost
  effects no distribution model sees), with OS-0 named entry points
  for mixed/unknown workloads. The idea: compile a pattern exactly as today,
  but with an opt-in `--profile` emission mode whose matcher TRACKS HOW IT
  RAN on the user's exemplar inputs — a PROFILE, not a trace: counters at
  the observation points the emitter already names (D46 stamp points,
  DD-8's tracer sites; same structural constraint — derived from the
  structure the emitter walks, never a parallel description). Stats out
  (candidate-start density, prefilter hit/miss, per-arm hit distribution,
  iteration-count histograms per quantifier, match/fail mix, subject byte
  frequencies), then a RECOMPILE-WITH-STATS channel feeds them back as
  generation inputs. SCALAR CUSTOMERS EXIST — this row is not
  SIMD-contingent: alternation/trie arm ordering by hit frequency;
  prefilter literal choice by measured-rarest byte (scalar memchr benefits
  identically to any SIMD scanner); the §8.1 capture-walk sink knob
  (eager/n-step/accept-time is a match/fail-mix question); [M4.6] engine
  selection; step-budget sizing near K23-style boundaries. RELATION TO
  F-1/D18, stated so the tension is on record as a resolution: per-pattern
  adaptive choices keep getting deferred because an axis must earn itself
  with a measurement — PGO is the EARNING MECHANISM, the standing vehicle
  for every deferred adaptivity question ([ENG-CLAMP], adaptive K, arm
  order), so those rows cite this one instead of re-inventing a
  measurement channel. SEQUENCING: design sketch is panel-eligible any
  time (thinking is cheap); implementation AFTER the M4 spine closes and
  WITH [BENCH-1] (the profile without the bench is a dial with no meter —
  BENCH-1's prioritizer is also this row's proving ground), BEFORE the OPT
  waves it would guide. The stats interface is designed scalar-first;
  later SIMD backend variants ([SIMD-META] hypothesis 2's density/
  statistics dependence) consume the SAME channel — which is exactly the
  "best non-SIMD approach, then backend variants on top" architecture
  Frank ruled.
- [ENG-DIRECT] STATE:not-started — DIRECT-CODED DFA EMISSION (Frank,
  2026-08-18, thirtieth session: "could we implement without state
  transition tables? ... aabbc sets up the table mechanism and the
  loop but really its just a memcmp ... (?:\d{2,3}\.){3}\d{2,3}
  could be a fixed loop of checking digits followed by period ...
  this is what i think of for dfa and for islands of dfa — no
  overhead"). Emit a DFA-tier pattern's verify automaton as DIRECT
  CODE — the program counter IS the state (re2c's model; lex -f,
  Ragel's goto mode) — instead of the rx_fcls/rx_ftr table loop:
  reducible automaton structure becomes structured code (sequences,
  branches, counted loops), byte tests become gcc-optimizable range
  checks/compares (the OPT-A spelling menu falls out of gcc switch
  lowering for FREE in this model, and the address-taken-label
  pinning largely disappears — plain structured flow), literal
  chains become the OPT-A memcmp lead as a special case. THE DEEP
  PAYOFF beyond constant factors: a bounded repeat in direct code is
  a COUNTED LOOP (register + constant code) where the table DFA pays
  STATES linear in n — the exact K7/a{n} family D56 just bounded;
  direct-coded counting re-widens the a{9795} narrowing by making
  the state-set population it guards simply not exist for these
  shapes (the VM's counter/cursor rungs already prove the loop form
  on the capture side). THE HONEST TRADE, which is why tables stay
  the general engine: dense/irregular automata mispredict as branchy
  code where a table lookup is branchless; large/irreducible
  automata blow icache and D45 compile budgets as code (the cap
  moves from state count to code size); so this is a PER-PATTERN
  (or per-island) selection by measured shape — D46 stamp+force
  obligations apply as a new selection axis when built. EVIDENCE
  MACHINE: [BENCH-CEIL] is this row's instrument — the hand-written
  ceiling arm's code IS what direct emission should approach, and
  the per-case gap table is this row's worklist and its acceptance
  measure. CROSS-LINKS: [ENG-ISL]'s islands, once determinized,
  should be EMITTED via this row's mechanism (the "no overhead"
  half of the island idea — record there); DD-5's switch-based
  emitter is the PORTABILITY cousin but still state-variable-driven
  — true direct coding eliminates the state variable where control
  flow carries it; the K24 counterweight (computed-goto
  unoutlineability) applies to any emission-model change and travels
  with this row. Sequencing: with the OPT waves, after [BENCH-CEIL]
  produces the gap table; unmeasured engine work is not scheduled
  (D12/D18). RULED A THIRD ENGINE TYPE (Frank, 2026-08-18, same
  conversation): the roster becomes table-DFA (current) / DIRECT-DFA
  / VM — with the VM potentially carrying direct-DFA ISLANDS — so
  when built this joins the ENGINE SELECTION axis proper
  (select_engine picks per pattern; ENGM_* gains a member; RX_ENGINE
  stamps a third value; OS-0's named-entry-point discipline applies),
  not just the emitter. On re2c, read by Frank at filing: it
  VALIDATES THE MODEL and is deliberately not the tool — its regex
  language is far from PCRE2 (lexer dialect, longest-match
  semantics). pcrec's shape is what makes the model usable inside a
  PCRE2 compiler: full-dialect parse + per-pattern selection routes
  only the shapes that fit. SURVEY LEAD for the capture question:
  re2c's TDFA (tagged-DFA submatch extraction, Trofimovich) is the
  literature for captures in direct-coded DFAs — the road by which
  direct-DFA could someday serve capture-bearing patterns without
  the VM; survey by measurement per OPT-A's rule when this opens.
- [ENG-ISL] STATE:not-started (EMISSION NOTE added 2026-08-18: an island, once determinized, is EMITTED via [ENG-DIRECT]'s direct-coded mechanism — that is the "no overhead" half of the island idea; determinization proves the language/preference exactness, direct coding is what makes the island cheaper than the machinery it replaces) — EXACT DFA ISLANDS, deferred OUT of
  [M4.6] (Frank, 2026-08-17, twenty-eighth session, D50 — the
  [ENG-ABS] pattern: build only behind a MEASURED loss). engine_m4.md
  §6.3's strength-1 mechanism was designed and scheduled before the
  [ENG-BREP] ladder existed; possessify.c/revdet.c now deliver much of
  the same frameless-execution win VM-internally, so the emitter build
  waits for evidence that capture-free VM-FALLBACK FRAGMENTS (not just
  loops — the islands' remaining distinct value) are hot: [BENCH-1]
  floors or [ENG-PGO] profiles showing it. The DESIGN STANDS unbuilt
  (engine_m4.md §6.3, annotated in place): fragment→NFA→DFA→table-emit
  seam inside the VM, reusing possessify's unique-iteration analysis
  (the proof islands need is eng_brep_design.md §2.2's corrected rule,
  NOT a new analysis — scoping sweep 2026-08-17). Carries its own D46
  stamp+force obligation when built. Accept-list islands (strength 2)
  and tagged automata remain deferred beyond this row per §6.3's table.
- [ENG-COUNT] STATE:not-started — LARGE BOUNDED COUNTS ON THE DFA SIDE (Frank, 2026-08-29 ~00:5x, forty-fourth session: "I'd like an unscheduled plan item to look at options for these forms but right now I'm not sure it's worth it as they seem pretty edge case and there is more profitable ways to spend time"). UNSCHEDULED, not on the loop's queue; opens only on a measured need. THE FORMS: a huge bounded repeat that the DFA engine can only express as states — `[a-z]{0,30000}` is 30,001 states by nature, `a{0,25000}`, `a{0,20000}`; today the tests/resource K7 pin guarantees they COMPILE within D45's budget (a robustness fixture, not an endorsement), and r41 S1 (2026-08-29) priced them for the first time against a mechanism — [ENG-ABS]'s optional anchored machine added +46 % compiler CPU on exactly these shapes (24.3 → 35.9 s on `[a-z]{0,30000}`) and its artifact 1.32 → 1.98 MB, answered by giving the optional machine its own state ceiling. THE VM SIDE ALREADY HAS THE LOOP FORM: the bounded-repeat COUNTER RUNG ([ENG-BREP]/counter-K — one body copy per K iterations + a trailed counter), with [ART-SIZE] STEP 2 choosing K by size and [ENG-CLAMP] the deferred per-quantifier downshift. OPTIONS TO LOOK AT when this opens (no design here): (a) a SELECTION rule on repeat magnitude — above a measured count, a pattern whose size IS a bounded repeat is routed to the VM counter rung rather than a giant table (a selection outcome, stamped, on the [SEL-1] shape); (b) a hybrid COUNTING form — a DFA for the body plus a counter (a counting automaton), the general form, sized against the same size term [ART-SIZE] built; (c) leave it: the shapes are edge cases, the caps and the K7 pin bound the cost. MEASURE FIRST (D77): how many real patterns (bench, corpus, the K41 fuzz population) have a DFA-side count above the candidate threshold, and what they cost in states, bytes, compile CPU and throughput on both engines today — the number that would trigger (a) or (b). Related: [ART-SIZE] (the size term and the caps), [ENG-BREP]/[ENG-CLAMP] (the VM counter), tests/resource (the K7 pin), r41 S1.
- [ENG-CLAMP] STATE:not-started — the DEFERRED per-quantifier K downshift
  (Frank, 2026-08-16, twenty-seventh session: F-1 ruled strict-§4.5 on the
  R25 panel — decisions.md D47 ADDENDUM has the full ruling and rationale).
  Charter: the binary tractability clamp (K = the constant, or 1 — never an
  intermediate value) computed by a BOTTOM-UP SUBTREE-PRODUCT pass, so that
  small-count nested towers (K22's family: every count below K, blowup from
  depth) COMPILE instead of hitting the interim product guard's fast
  refusal. Seeded work, already committed on the counterk lane and carried
  at docs/design/counterk_impl/: the respecified algorithm, the
  clamp_arith.py arithmetic probe (towers d=18/30/35/40 collapse to product
  2 under it; carries the {1,2} tower as a MUST-STILL-REFUSE row), and two
  findings that are this row's design constraints — the PRODUCT rule is the
  right mechanism, not the body-contains-a-repeat shape rule (which
  over-clamps `(a(b|c)?){0,4000}`), and the {1,2}-tower residual needs the
  mandatory+optional phases merged into one loop with a runtime ctr>=m test.
  Opening this row is a Frank event and REQUIRES amending eng_brep_design.md
  §4.5 (a fresh ruling — that is the point of the deferral); until then K is
  one per-artifact constant and the interim guard's refusal is the ruled
  behavior for the tower family. When it lands, tests/vm/run_vm_tests.sh's
  K22 block inverts (refusal -> compiles-and-runs, refusal re-pinned under
  the deny flag) per R25 C1's rewrite plan.
- [ENG-LOOK] STATE:not-started — LOOKAROUND BY PRODUCT CONSTRUCTION IN
  THE DFA ENGINE (chartered by Frank, 2026-08-23 13:5x, on the manager's
  analysis; Frank's framing: "my concern is unnecessary special handling
  code and duplicate code paths. Ideally we implement this in such a way
  that it produces the 'best' possible code while not actually knowing
  about the special assertions it's implementing … is the one character
  optimization the best form, or merely one that works for the immediate
  need?" — it is the minimal instance, not the form). THE FORM: a
  lookaround over a regular body is a constraint on the SUBJECT, not the
  match — `(?<=L)` at p ⟺ subject[..p] ∈ Σ*·L, a property of text the
  forward scan has already consumed; `(?=L)` at p ⟺ subject[p..] ∈ L·Σ*,
  the same property for the REVERSE scan. MECHANISM: the PRODUCT of the
  main automaton with each assertion body's recognizer (Σ*·L forward;
  reverse(L)·Σ* in the reverse machine), folded in during determinization
  so an assertion is a predicate on the product state; bounded lookahead
  in the forward pass as a k-byte delayed acceptance; unbounded lookahead
  in the forward pass DROPPED (superset — sound for end-finding) and
  resolved in the reverse pass or by the VM; the context seeded from the
  bytes before startpos by running the component over the prefix
  (mechanism 4 generalized). TODAY'S assertions machinery (assertions_
  design.md waves B/C: the previous-byte context bit in the state
  identity, the class-indexed accept table, mechanism 4) IS this
  construction for one-class bodies — it becomes an INSTANCE, then gets
  DELETED once DD-11 rebinds \b/(?m)^/(?m)$/\Z to their lookaround
  definitions and the identity gate proves the product's artifact byte-
  identical (or measured-equivalent) to the hand-built one; where it is
  not, that is the optimizer's next target, never a reason to keep the
  special code. REACH: every bounded-length regular-body lookaround
  becomes DFA-eligible — `(?<=foo)bar`, `(?<!\d)\d{4}(?!\d)` — not the
  four assertion spellings only. MEASUREMENT FIRST: state growth — wave
  B measured the one-bit context's composed worst case at 38,009 states
  against the 32,000 cap; the product with larger components is not
  free. Size the component automata on (a) the expanded assertion corpus
  ([M6.6.1]'s substitution driver) and (b) the real lookaround population
  from the PCRE2 testdata and the D27 corpus; the construction ESTIMATES
  BEFORE COMMITTING and DECLINES to the VM past the caps ([ENG-CUT]'s
  shape). SEQUENCE: after [M6.6] ships the VM semantics (the VM stays as
  the exact verifier and the engine for captures/backrefs inside bodies);
  design gate with a D6 panel; the expanded-corpus three-way self-oracle
  is this row's acceptance test as well as M6.6's. The hybrid's
  prefilter soundness argument (dropping lookarounds = superset) is
  M6.6's to state and this row's to exploit. NO one-character fold ships
  anywhere — Frank's ruling: it is the duplicate path.
- [ENG-CUT] STATE:not-started — THE FULL CUT CONSTRUCTION (chartered by the [M6.4.1] design, atomic_groups_design.md §5.5, 2026-08-22; plan row added at the design's merge per R31 D4): replace `A_ATOMIC(X)` with an equivalent cut-free sub-automaton — run X's own priority-first-accept determinisation to fix, per entry state, the single endpoint the cut commits to, and splice that deterministic prefix into the enclosing machine (the primitive is src/ir/dfa.c's priority prune). Plugs into engine_m4.md §5.2's `discharge` socket and therefore BUILDS that socket's plumbing (the fixpoint never calls a registered hook today — select_engine.c:283-294, a live defect in unused code; D67's contract applies: output born ANY_ENGINE, copied nodes keep stamps). SIZE ESTIMATE (analytic, unmeasured on real patterns): worst-case exponential, `|D(X)| × |D(rest)|` states against PCREC_MAX_NFA_STATES and the 32,000/10,000 DFA caps — the rewrite must ESTIMATE BEFORE COMMITTING and DECLINE past the cap; a declining rewrite falls back to the VM, i.e. to module atomic-groups. What it buys: capture-free atomic patterns from VM to DFA — the population is the cut-changes-the-language class MINUS what the free discharge rescues, and it is UNMEASURED on real inputs. EVIDENCE GATE (D50's shape, confirmed by the manager 2026-08-22 under the autonomous-run grant): build when a [BENCH-1]/[ENG-PGO]-class customer exists; the measurement that would open it earlier is that population's size and throughput gap on a real corpus. The day it lands, H4 (the match-here entries' rule) is REOPENED (design §4.4 H5), and the lowering must never ignore atomicity (registry.c:615-622's named trap; sabotage S91).
- [M4-CALLOUTS] STATE:not-started (step 1 flip COMPLETED 2026-08-14, merge 84e5956 — all counts held at baseline, K14 check re-scoped to the RS_MODULE population; step 2 behavior awaits M4, its ABI ruled by D38/D39) — module `callouts` (D36: Frank re-scoped
  `(?C` from NEVER to PLANNED, 2026-08-12 — LOW PRIORITY, deliberately in
  the queue boonies). Two separable steps: (1) THE FLIP, schedulable any
  time a lane is free: registry `(?C` row ROADMAP_NEVER → PLANNED, the
  diagnostic moves from "no module will implement" to "requires module
  'callouts'", reject + case11 pins move with it failing-first (NOTE,
  mod08fix lane 2026-08-12: case11 asserts `(?C1)` `roadmap never`,
  `names —`, and the "no module will implement it" status — load-bearing
  against today's tree; they MUST move inside the flip commit or the flip
  lands red), compliance
  prose updated IN THE SAME CHANGE (the K14 prose⇔column check binds them),
  and note the ROADMAP_NEVER live population drops to zero — the never
  branch stays, column-derived, covered the day a second row exists.
  (2) THE BEHAVIOR, M4-hosted and engine-forcing (VM only — the compiled
  DFA erases the pattern positions a callout fires at): static extern
  binding (`extern int rx_callout_n(const rx_callout_block *)` defined by
  the embedding program — compile-time binding, zero cost when absent;
  V-A's compat layer later implements pcre2_set_callout as a trampoline ON
  TOP of this primitive, not instead of it), callback block and return
  semantics (0/positive/negative) mirroring pcre2_callout_block exactly
  (D26-exact tier), fire-point discipline DOCUMENTED as engine-relative
  with PCRE2's own PCRE2_NO_START_OPTIMIZE latitude as the cited precedent.
  AMENDED 2026-08-13 (Frank, composition discussion; syntax and semantic
  choices TBD, his to rule): PROPOSAL — align the callout ABI with an
  anchored MATCH-HERE entry point every generated matcher also exports
  (`(subject, pos, len) -> matched-length-or-fail` shape; OS-0's named
  entry points are the natural vehicle), so a compiled matcher IS a valid
  callout — link-level regex composition. DEADLINE: this is a match-API
  design constraint and must be decided BEFORE M4's match-API freezes
  (same gate as PC-5). Semantics to document honestly: a callout-as-
  submatcher is OPAQUE to the automaton — atomic (no backtracking into
  it) and un-fusable, partitioning the pattern into [M4.0]'s DFA islands
  around call points. TENSION to resolve at design time: this row's
  pcre2_callout_block-exact mirror vs the aligned ABI — possibly
  reconciled by V-A's trampoline direction (the PCRE2-shaped block as a
  compat layer ON TOP of the aligned primitive)
- [M4-SUBST] STATE:not-started — COMPILED SUBSTITUTION (Frank, 2026-08-12:
  the headline xmas item): the `pcre2_substitute` capability as an AOT
  artifact — pattern AND replacement template compiled together into one
  emitted C function (match + splice), first/global modes, caller-buffer
  zero-allocation mode plus an output-sizing mode. **The template compiler
  is almost completely independent of the matcher (Frank's observation,
  recorded because it sequences the work): it consumes only the
  capture-offset CONTRACT, so its design note can precede M4 even though
  end-to-end substitution is capture-gated.** AOT-only win to preserve in
  the design: `$n`/`${name}` references are resolved and BOUNDS-CHECKED AT
  COMPILE TIME against the pattern's own group count — a template naming a
  group that does not exist is a compile error, where PCRE2 discovers it at
  substitute time. Tier the template language: core `$n`/`${name}`/literal
  escapes first; PCRE2_SUBSTITUTE_EXTENDED forms (\u \l case forcing,
  ${n:-default}, ${n:+yes:no}) earn their rows separately under D18's
  earn-its-axis discipline. **BEYOND-PCRE2 DIRECTION (Frank, 2026-08-13:
  "this might be an area where we provide more capability than pcre2"):**
  richer shell-style transforms and C FUNCTION CALLBACKS as template
  segments — a segment that calls an embedder-defined `extern` to render,
  reusing M4-CALLOUTS' static-extern primitive verbatim (compile-time
  bound, zero cost when absent). Discipline: everything past PCRE2's
  surface lives in pcrec's own clearly-flagged namespace (SR-10's rule) so
  the D26 compatibility story stays clean — PCRE2-compatible core,
  pcrec-extended templates opt-in; non-portability is a non-issue for the
  embedded niche, which is compiling in anyway

## Design-debt ledger (from R1; resolve before the milestone that hits each)

- [DD-2] STATE:not-started — VM engine match/step limits (with M4 design) (R1 A-8). DOWNGRADED by D22: adversarial patterns are out of scope, so this is a ROBUSTNESS feature (a pathological pattern should fail honestly rather than hang), NOT a security boundary, and it must not be designed as one or traded against execution speed. AMENDED 2026-08-14 (D42.6): the row names TWO bounds — the step budget (a step = one backtrack resumption, counted only at the fail label) AND the backtrack-frame/trail capacity that allocation-freedom forces — different failures, different diagnoses (RX_ERR_STEPS vs RX_ERR_FRAMES on the search entry; −1 on match-here per D42.3). Design: engine_m4.md §4
- [DD-7] STATE:not-started — engine unification ownership (R2-A6), SPLIT 2026-08-14 (D42.7): the WHICH-machine-is-the-capture-prefilter half is ANSWERED by engine_m4.md §7.1 (both existing machines, unchanged — the capture-erased forward+reverse pair is exact for the capture-only tier), pending the M4.3 panel; the `^`/`$` ABSORPTION half is RE-HOMED to [ENG-ABS] (with the OPT rows) gated on a measured loss existing first — GATE SATISFIED 2026-08-18 (D63): (?m)^'s quadratic crossing-body curve is measured (3.99x/doubling, 1996x at n=64k) and the D63-chartered ENG_ATTEMPT prefilter deliberately does not rescue it; the reverse BOT variant is UNPARKED as sequenced follow-on work queued behind the [M6.2] waves; DD-4 (\G) keeps its note — `nfa_wrap_unanchored` bakes in the self-loop with no toggle (confirmed STRUCTURAL, engine_m4.md §7.3)
- [DD-9] COMPLETED 2026-08-14 (D42.8) — DECIDED by engine_m4.md §8: the DFA-prefilter/VM hybrid does NOT own case (f) and structurally cannot (the pattern is capture-free, so every piece of M4 machinery is inert on it by the same design that guarantees zero regression). Row archived in plan_completed.md; case (f) is now the known HEAD of [BENCH-1]'s prioritizer worklist, carrying engine_m4.md §8.4's three findings (computed goto is the WRONG lever there, contra this row's old hint; ~2x of the 6.61x gap is the reverse pass; bit-parallel shift-and is the algorithmic candidate, detectable from the built DFA). M4 still owes the family a non-regression floor: the capture-bearing sibling joins the bench at M4.6 (engine_m4.md §8.5)
- [DD-8] STATE:not-started — `--emit-ir` / `--emit-dot` promised in APPROACH §6, never built (R2-A7). UPGRADED from filler 2026-08-14: Frank REQUESTED the VM tracer as a debug facility — engine_m4.md §10's form (emitted-program listing: labels, choice points with preference order, capture slot assignments, island boundaries, callout call sites; plus an optional resume-frame push/pop trace for one subject). Schedule with [M4.5]'s bring-up; §10's one constraint stands — the dump derives from the same structure the emitter walks, never a parallel description. Companion facility ruled with it: `--engine=dfa|vm|auto` (engine_m4.md §5.6) is do-or-die (clean refusal, no fallback) and, per the R21 E-6 fix, `--engine=vm` disables the prefilter so the two engines are independently comparable end-to-end (Frank's stated use: compare results between the two). TABLE-CONTRACT CONSIDERATION (Frank, 2026-08-21): when this row next opens, decide whether --emit-ir's tabular SECTIONS (slot legend, label table) adopt docs/spec/table_contract.md, and whether the listing as a whole gets a sibling line-oriented contract (header-declared section structure) — its consumers' extractors went stale once during [M6-READ] and declaration-based parsing is the durable fix; the derive-from-the-emitter's-own-walk constraint holds regardless
- [DD-1] STATE:not-started — case-insensitivity design: UNICODE folding vs byte-wise automata (before M5) (R1 A-7). The ASCII half is CLOSED by OS-1/D23 — it folded into class construction and is a parser change, not an engine question. What remains here is genuinely Unicode: multi-byte fold pairs, one-to-many foldings and the fold-before-negate rule over byte-range trees rather than a 256-bit bitmap
- [DD-12] STATE:not-started — the UTF ARCHITECTURE sketch (Frank,
  2026-08-12 tenth-session close; elaborates APPROACH §4/§10, OS-2, DD-1,
  D33 §7 into one position). (1) ONE parser, no encoding parameter in the
  grammar: the parser's semantic output becomes a CharSet — sorted CODE
  POINT intervals (the D33 §7 widening and DD-1's "byte-range trees" are
  this) — and the encoding is a LOWERING instance, CharSet → byte-level
  NFA fragment: ASCII = identity byte map, UTF-8 = interval-to-byte-
  sequence expansion with suffix sharing (the RE2/Ragel construction, so
  \p{L}-sized sets stay near-linear). Downstream (subset construction,
  minimization, emitter, prefilters) stays encoding-blind and BYTE-WISE —
  OS-2's fold prediction, made concrete. Parser changes only where UTF
  changes the LANGUAGE: \x{>FF} becomes meaningful, a multi-byte atom
  quantifies as one unit (free once atoms are lowered fragments), pattern
  validity. (2) UTF-8 AT MATCH TIME, ALWAYS — never convert the subject:
  UTF-32 conversion costs a decode pass + 4x memory, kills the byte
  prefilters/skips, breaks the byte-offset API (PCRE2 reports byte offsets
  even under UTF) and M3 streaming. Code points exist ONLY at regex-compile
  time, inside the CharSet, between parse and lowering — that is the right
  home for the "convert to UTF-32" instinct. The backtracking worry is
  bounded: the DFA never backtracks; the M4 VM steps back a character by
  skipping ≤3 continuation bytes (self-synchronization), O(1). (3) Invalid
  UTF-8 is a DECISION: byte-wise automata naturally treat invalid
  sequences as nomatch; PCRE2_UTF errors, but PCRE2_MATCH_INVALID_UTF is
  essentially the byte-wise semantics — measure against THAT mode and pick
  deliberately. (4) The oracle pipeline extends with a UTF twin of PC-4
  (compiled PCRE2_UTF), carrying the R13/R14 warning verbatim: a UTF sweep
  needs generators that can PRODUCE multi-byte constructs, or it counts
  the generator. (5) Fold-before-negate and the one-constructor-owns-fold
  seam (OS-1) carry over at the CharSet level; DD-1's Unicode fold pairs
  land there. (6) Scope: ASCII + UTF-8 only (D18 earn-its-axis; UTF-16's
  surrogates make byte automata messy and no consumer asks); encoding is
  a generation-time scalar (D20, --encoding), named entry points via OS-0
  if anyone wants both from one binary. Owners: the CharSet widening is
  MOD-0.6's (D33 §7); the lowering instances and the UTF PC-4 twin are
  M5's; DD-1 folds in at the CharSet level. (7) FRANK'S CONSTRAINTS
  (2026-08-16, twenty-seventh session, ruled into this row as
  requirements): NO encoding conditionals anywhere — no "if utf do x
  else y" in the compiler, the emitter, or the emitted artifact;
  encodings are SEALED backends behind the one lowering interface, all
  specialized code within. The include-package question ANSWERED with
  the two-seam characterization: per-encoding inline-function headers
  are the WRONG seam for the hot path (gcc cannot invert decode+compare
  back into a byte automaton; malformed-input handling degrades from
  automaton structure to runtime branches; the reverse pass would need a
  second backward-decode shim) and the RIGHT seam for the enumerable
  runtime-identity RESIDUE (caseless backref comparison under M6xM5,
  optional subject validation, grapheme \X if ever, trace printing) —
  ONE per-encoding header embedded at generation, so the artifact
  contains exactly one encoding's code and the "switch" is which header
  text was emitted. ENFORCED BY CHECK, NOT CONVENTION, when M5 lands:
  (a) OS-2's hot-loop shape-identity check ASCII-vs-UTF-8 as a pinned
  structural test; (b) a codegen-structural check that no hot-loop label
  calls into the encoding header (allowlist of named residual sites).
  INVARIANTS: subject and all reported offsets are BYTES, permanently,
  third encoding included; fixed-vs-variable width is a PROPERTY the
  backend exploits (fixed-size lowers to fixed-length chains / direct
  indexing), never an interface axis. THIRD-ENCODING RECIPE (the
  planned-for threat): a new backend = one lowering module + one
  residual header, core and emitter untouched — if adding one ever
  requires touching a shared file outside the backend directory, that is
  the derailment signal and a design stop. (8) PER-PATTERN RULING
  (Frank, 2026-08-18, thirty-second session, D58): the generation-time
  scalar is per COMPILE CALL — a pcrec_options field + `--encoding` —
  never process- or file-global; mixed encodings in one compilation
  unit or binary are SUPPORTED BY CONSTRUCTION (self-contained
  artifacts, distinct prefixes, each embedding exactly one encoding's
  residual block). The residual-seam half of this row is built EARLY as
  [M5-SEAM] (D58 ordering: seam → M6 → the rest of M5); the lowering
  instances, oracle twin, and both M5-time structural checks named in
  (7)(a) remain M5's
- [DD-13] STATE:started (STAMPS HALF CLOSED 2026-08-26 00:0x — BATTERY GREEN on 32890e2: test 1,555 checks / 1 load-red (endvar identity, solo 2,353/2,353), K32 corpus cell solo 1,634/0, san clean both axes 1h31m, matrix 180/0/6/0 with UNREACHED 0 at 50346fc (docs-only past 32890e2); bench inbox I-5 sent with the pin. The FORMAT half [DD-13b] stays not-started. STAMPS SHIPPED 2026-08-25 78249e6, lane srStamp — D81: `RX_ENGINE` unconditional, `RX_DFA_SCAN`, `RX_DFA_PREFILTER` with five values incl. the -bounded pair; abi 3→4, D76's first non-layout event; run_dfa_stamps.sh 16/0 with four MEASURED validation reds; corpus 995 DFA: none 380 / memchr 327 / byte-class 176 / memchr-bounded 61 / byte-class-bounded 51, unanchored 815 / attempt 180. The bench's I-3 blocker is cleared once the battery is green (inbox I-5). D6 PANEL r37 (docs/dev/reviews/2026-08-25-r37-dd13-stamps.md): both core claims survived independent measurement; two SCOPE gaps chartered as [DD-13c] (lane srStamp2: the `empty` scan value for the four no-loop artifacts; the VM HYBRID's inlined DFA scan stamps its form); the rest landed 55165a9. THE HAZARD, four sites: any check that used a stamp's ABSENCE as the DFA discriminator broke when RX_ENGINE became unconditional — two in codegen and one in parse (fixed by the lane), and tests/atomic_groups §3 (10 reds, found by the d8608ca battery, fixed at the landing); the discriminator is the VALUE. NEXT stamp candidate: the M2.1 self-loop skip count (family (b), naming owed). The FORMAT half of this row ([DD-13b]) is unchanged — not-started.) — formerly STATE:not-started — INPUTS FROM pcrec-bench (pcrecdev2, 2026-08-24 ~23:5x; Frank ruled the bench-set format BLOCKS on [DD-13], scope NARROW — today's .rxt parsed as-is, per-sub-bench tags in a plain sidecar of R-BENCH fields, no grammar): /home/duxevents/pcrec-bench/docs/design/requirements.md v3 (commit 8c34498) §5 (sub-bench DIRECTORY model + sidecar), §4.4 (per-(pattern,testee) OUTCOME enum), §4.5 (a declared VARIANT per engine — identical results on every subject, the sub-bench's OBJECTIVE preserved: a subroutine sub-bench may not be satisfied by inlining), §3 (per-sub-bench REGIME), a sub-bench-level OBJECTIVE field — for [DD-13b] to absorb when it opens. THE UNIFIED PATTERN-SOURCE / TEST FILE
  FORMAT (Frank, 2026-08-17, twenty-ninth session; name TBD): ONE file
  format, grown from .rxt, serving every consumer that today would need
  its own file kind: (1) the [V-E] MANIFEST — a compilation SOURCE for
  pcrec (N named patterns → one emitted unit, perhaps several; [V-E]'s
  named definitions, cross-references via subroutine referencing, and
  the D39.2 appended-numbering rules all bind here); (2) the TEST
  CARRIER — cases exactly as .rxt carries them today, co-located per
  named pattern ([V-G]'s bottom-up subpart testing rides this); (3) the
  BENCH SET format for ~/pcrec-bench (its APPROACH.md §8 Q1 resolves
  HERE) — which forces the format to understand DIFFERENT ENGINES /
  CONFIGURATIONS, not just pcrec. Features Frank named at creation:
  OPTIONS/CONFIG blocks including EXEMPLAR FILE REFERENCES (large
  subjects/corpora live in external files, referenced rather than
  inlined); FILE INCLUDES (so case sets can be extensive and
  MACHINE-GENERATED without bloating the hand-written source, and so
  per-engine/per-configuration fragments compose for the bench use);
  NAMED patterns referring to one another (subroutine referencing).
  PROCESS, staged and gated — the format is hard to change once
  adopted ("we should get it right"), so it is built DESIGN-FIRST like
  the K23 arc:
  - [DD-13a] STATE:completed 2026-08-17 (lane dd13a, merged 52e2702 —
    docs/design/dd13_format/requirements.md: census 54 files / 1,100
    blocks / 9,977 expectation lines; compatibility answered DIALECT
    with R-COMPAT-1; OD-1..5 carried unresolved; five tensions, seven
    anti-requirements, panel attack list) — REQUIREMENTS note:
    enumerate every consumer's needs
    measured against real corpora — the .rxt harness as-is
    (docs/testing.md), the machine-generated D27 sets, [V-E]'s
    manifest + finder, [V-F]'s transformer target, [V-G]'s user
    testing, M4-SUBST templates if they intersect, and pcrec-bench's
    set needs (feature tags, hazard classes, per-case
    expectation-verification method, engine/config sections). The
    compatibility question is answered here: is .rxt a subset, a
    dialect, or migrated?
  - [DD-13b] STATE:completed (MERGED daa6b6c, 2026-08-29 ~17:4x, forty-fifth session: docs/design/dd13_format/format_design.md, 2,443 lines, revision 2 on the r44 panel + D87 — HEAD/BODY shape, 13 line-kind additions + `description` (a FIELD, `|` block scalar), the three PATTERN-level extensions settled by measurement against libpcre2 (`(?<3>…)`/`(?<name=3>…)`, `(?&^.name)`, `(?&from=email)`/`(?&=email)`), composition AST-level inside pcrec with assigned numbers (D87), the struct view → [V-I], the five-member piece rule, H11 the target build path, `--emit-composed`; the census 179/3,265/26,691 reproduced to the digit by the panel; Q7 (the oracle control's coverage) accepted for W1 with its trigger. NEXT in the feature column: the W1 PARSER + composer ([DD-13b.W1], to be chartered — starts on Frank's word). Lane dd13b, opus, 2026-08-29 14:4x-17:3x) — DESIGN note: grammar + semantics (include model, config
    scoping/precedence, reference/namespace rules, exemplar-file
    addressing, the machine-generation contract), the migration story
    for the existing ~10k-case corpus, and single-vs-multiple emitted
    outputs.
  - [DD-13b.panel] STATE:completed (CLOSED 2026-08-29 ~17:4x: docs/dev/reviews/2026-08-29-r44-dd13b-format.md — r44-grammar confirmed the corpus invariant by run; r44-sem found TWO BLOCKERS on both oracles (absolute refs inverted by relocation; `(?J)` shadowing) + the D61 contradiction; r44-consumers the bench seam gaps; Frank ruled the blockers the OTHER way (D87: renumber, own groups win, the caller-scope prefix, the struct view); revision 2 measured both fixes; syntax settled by the manager) — formerly STATE:started (2026-08-29 ~15:1x, forty-fifth session; FRANK 14:5x: "spelling and syntax details are your decision" — keyword names, line spellings, selector forms (e.g. §0.3 D-e `analysis freq <name>` over §6.5's `freq <name>`, ACCEPTED by the manager on the grammar-ambiguity argument) are ruled by the manager; Frank rules SEMANTICS (what composes, what is refused, what a caller observes) and the §7 questions; review r44 — three read-only critics: r44-grammar (sonnet: §1 grammar re-parsed over the 179-file corpus, ambiguity, keywords, waves, §3 migration), r44-sem (opus: §2.3 EXPAND vs libpcre2 10.46 + pcrec — DEFINE-at-end numbering, capture-transparency's cost to [LIB], closure order, lexical shadowing, §6.0 anchors, config precedence, targets), r44-consumers (sonnet: §4 seams incl. consistency with r43's TAG ruling, §4.5 bench field-by-field, §2.10 freq/provenance, §2.11 accounting, §5 attack answers, §7 the other side). The design note LANDED on lane/dd13b 937c1b9 (1,657 lines): HEAD/BODY shape, 13 additions, `(?&name)` ALWAYS a PCRE2 subroutine call with the definition closure appended as `(?(DEFINE)…)` at the END (D39.2's numbering obtained from PCRE2, MEASURED cells E-J), capture-transparent, four namespaces / one refusal rule, per-option-kind config precedence, waves W1/W2/W3; census re-run 179/3,265/26,691 (3.3× [DD-13a]); THREE corrections to our inputs — the position paper's §3a does not match (anchors in a called body bind the SUBJECT), OD-5's atomicity premise is FALSE on 10.46, `--replace` does not exist; five admitted departures (§0.3); six §7 questions for Frank with recommendations) — D6 ADVERSARIAL PANEL on the design, then Frank's ruling. (Renamed from [DD-13c] 2026-08-25: that tag now names the STAMP SCOPE follow-up below.)
    NO parser is written before (c) closes.
  Scheduling: after the scale work ([M4.6]/[M4.7]) per Frank's
  2026-08-17 sequencing; (a) is read-only fact-gathering and safely
  early-schedulable in a session with spare capacity, but does not
  start unprompted. FRANK'S DESIGN INPUTS accumulate ahead of (a) in
  docs/design/dd13_format/frank_inputs.md (append-only, with the OD-n
  open-decision ledger): per-engine option placement, the
  last-reference-wins options CASCADE over ordered includes, declared
  per-library pattern tweaks, configuration sections unifying bench
  testees with build variants (avx2-vs-baseline), and the
  interface-vs-reference-only pattern distinction. **BENCH-DISCOVERED CANDIDATES (2026-08-25 ~01:0x, pcrecdev2, measured on 8da6120, recorded here as the bench's inputs row — not started):** (a) the DFA artifact has NO prefilter stamp — `RX_VM_PREFILTER` is VM-only and a DFA artifact's only `#define`s are `RX_ALTCLS_*`, so the byte-class skip loop (the email specimen's headline ~23× mechanism) is invisible to the bench except by reading the emitted loop; candidate: an `RX_DFA_PREFILTER`-style stamp in the D46 family (D46: every selection point observable). SECOND INSTANCE (manager, 2026-08-25 03:58): DFA artifacts carry no `#define RX_ENGINE` either — `rx_info.engine` is the only readable selection field on a DFA artifact; the D46 macro family is VM-side on this tree. Same fix, same customer. (b) the `(?:P)\z` form's DFA skip loop is WEAKER than the plain form's — same `rx_can_begin_match` table, but the loop runs `pos + 1 < len` and cannot early-exit at end of subject because the end-of-subject view state (`rx_forward_end_view`) must be evaluated, so the final byte is never skipped; a slightly higher per-scan cost in the match regime, NOT an engine-selection effect; candidate optimization: an end-view the skip loop can fold. Control it verified: `a|ab` on `ab` — anchored `==n` NOMATCH, `(?:a|ab)\z` [0,2), libpcre2 ANCHORED|ENDANCHORED (0,2): the [OS-4] asymmetry is real. **FIRST PRODUCTION SAMPLE (2026-08-25 ~03:3x):** /home/duxevents/pcrec-bench/reports/2026-08-25-email-specimen-0.1-budu-ryzen1600.md (records bf4a415, pin 8da6120 = pre-wave-G); manager feedback and the ranked sub-bench list are in journal part 28 — Frank rules on priorities. **RULED (Frank, 2026-08-25, fortieth session):** sub-bench order 1 log-line search / 2 wide alternations / 3 lookaround+backref / 4 bounded-repeat band / 5 UTF-8 (pcrec-bench inbox I-2); the DFA `RX_ENGINE`/prefilter stamp gap is the first pcrec-side lane after [CHK-1] (a scaffolding change: abi 3→4 + gate re-pin, D76); the edit-test loop's three bench features (scratch tier, `quick`, `pcrec-local`) are bench work, inbox I-4; the durable channel is D78.
- [DD-13c] STATE:completed (CLOSED 2026-08-26 09:1x on the battery-proven tree 6e8edfb: matrix 180/0/6/0/0, full san 33/33 green, test 1,570; bench inbox I-6 sent; MERGED a895184 2026-08-26 ~04:5x — abi 6, (B) pin c940551; the FINAL battery on the combined tree is owed after srAnchor re-anchors S179/S183/S67; launched 2026-08-25 ~20:4x, lane srStamp2, opus) — THE STAMPS' SCOPE (r37 A5/A6) + the RUNTIME MIRRORS (Frank, D40 addendum): `RX_DFA_SCAN "empty"` for the four no-loop artifacts; VM HYBRIDS (1,263 of 1,488 VM artifacts) stamp their inlined DFA scan's `RX_DFA_SCAN`/`RX_DFA_PREFILTER` from the same derivation, the check's leak assertion becomes an iff; `struct rx_info` gains `scan` and `prefilter` string fields (appended; NULL where n/a; one derivation feeds macro and field); abi 5→6 (srTier's 4→5 merged first), (B) re-pinned, (A) unchanged. REBASED onto main 95320df (srR37's shipped run_dfa_stamps.sh, the A7/A8/A4 doc hunks and the atomic_groups §3 value-based discriminator all inherited; my redundant versions dropped). **MEASURED after the rx_info addition:** run_dfa_stamps.sh **29/0** over 2,772 patterns — 995 DFA (4 empty-engine) / 1,488 VM (1,263 HYBRID, 4 of those inlining an empty scan; 225 plain) / 289 refused; DFA prefilter none 380 / memchr 327 / byte-class 176 / memchr-bounded 61 / byte-class-bounded 51 — STILL IDENTICAL to [DD-13]'s recorded figures, the control that neither half of this change moved the DFA side — DFA scan unanchored 811 / attempt 180 / empty 4; hybrid prefilter memchr 825 / none 264 / byte-class 137 / memchr-bounded 20 / byte-class-bounded 17, hybrid scan unanchored 1,071 / attempt 188 / empty 4; the MIRROR assertion (rx_info.scan/.prefilter == the macros, NULL/"none" where absent) runs on all 2,483 compiled artifacts of BOTH engines, with the field LINE COUNT asserted so it cannot go vacuous. FIVE MEASURED validation reds against the 29/0 baseline: hybrid silent 21/5, gate dropped 24/2, empty arm removed 23/3, mirror written from a second spelling 28/1 (376 = 368 attempt + 8 empty exactly), mirror fields not emitted 27/2 (BOTH the line-count red and the counted-denominator red — without them the value comparison would have been vacuously true). TWO CHECK DEFECTS FOUND BY THIS LANE'S OWN VALIDATION and fixed: (i) the [agreement] denominators were arithmetic over bucket sizes, so a plant that routed 1,263 artifacts past a comparison still read "on all 2258" — they are COUNTED at the comparison sites now and the shortfall is asserted; (ii) run_codegen_tests.sh pins rx_info.abi by a hand-spelled literal and fired correctly (104/1) on the first `make test-codegen`, which is a second site every future abi bump must touch. SWEEP for the absence/presence-as-DFA hazard (manager's ask): 17 tests/*.sh read RX_ENGINE/RX_DFA_*; ALL are value-anchored or comment-only, NONE presence-based, and run_dfa_stamps.sh is the only reader of RX_DFA_* at all. abi 5→6 ([OPT-1]/srTier took 4→5 immediately before; LAYOUT event: fields appended at the END, no existing offset moves; the abi comment names BOTH artifact kinds per r37 A12 — the mirror image of [OPT-1]'s VM-only note), (B) re-pinned 469a432 → c940551. ALSO FIXED in passing: docs/spec/tuning.md §3 shipped on main with lane srStamp's editorial wrapper merged into the published spec (d8608ca).
- [DD-4] STATE:completed-in-place (2026-08-19: [M6.2] wave D answered it — start_max = startpos as a third compile-time string, no wrap toggle needed, §4.1/§4.3; the find-all sentence is in match_api.md §3.1; row retained here rather than archived because its text is cited from DD-7) — formerly STATE:not-started — \G / global-iteration semantics vs startpos (with M6) (R1 A-11)
- [DD-6] STATE:not-started — multiline ^/$ as DFA state context — interacts with state budget (with assertions module) (R1 A-6)
- [DD-11] STATE:started (DESIGN NOTE MERGED 3cb6721, 2026-08-29 ~15:3x: docs/design/definitions_table.md after the r43 panel (docs/dev/reviews/2026-08-29-r43-dd11-definitions.md — 5 blockers fixed; the predicate is a TAG from a closed enum with ONE exhaustive-switch evaluator in src/parse; Frank's class-escape + literal-escape families are rows; census 28 replacement rows with a RegRow home + 9 base-tier literal escapes with none — RULED by the manager: they get minimal `RS_BASE` rows, one mechanism (D24), [DD-11.4b]; Option A `RegRow.definitions`; `--flavour` yes; close after [DD-11.1]-.4, [DD-11.5]/.6 a follow-on row when M6.6 lands carrying r43-S3's `pcrec_ast_stamp` precondition). IMPLEMENTATION opens in the same lane: [DD-11.1] the table, [DD-11.2] `--list-definitions`, [DD-11.3] the option-matrix self-oracle with libpcre2 as co-equal leg, [DD-11.4] the synthetic-`\w` resolver test, [DD-11.4b] the base rows — sequential, each gated by its checks; the merge battery is the manager's. 2026-08-29 ~14:4x, forty-fifth session, on Frank's "go on all three"; lane dd11, sonnet, worktree worktrees/dd11 — the D86 ADMIN/STRUCTURAL lane; deliverable docs/design/definitions_table.md: the replacement INVENTORY with file:line, the core set, placement A (RegRow list) vs B (own table) measured against D82 rule 4 / D62, the PCRE2 hazards oracle-checked, `--list-definitions`'s shape, the [DD-11.n] sequence; D6 panel gates the code) — formerly STATE:not-started (D85 RULES THE SHAPE, 2026-08-29: the replacement model is a PREDICATE-SCANNED TABLE on the [ENG-FORM] forms model — an ordered list of (option-scope predicate → definition in core syntax) rows per construct, first applicable wins, last always applies; `--list-definitions` walks the same table; each row is a unit for checks and sabotage; the core rx set becomes the minimal set the optimizer must know. Table placement — the registry rows expanded, or its own — is the design note's question. FRANK ASKED 2026-08-29: "we created the rx replacement model (e.g. `$` is replaced depending on options) — can we `--list` those replacements?" — NOT TODAY, and the reason is the deliverable: the replacements are code arms (`$` → N_EOL/N_EOL_M in src/ir/nfa.c:539 off the parse-resolved multiline field; the possessive-suffix desugaring in parse.c; the NEWLINE constant; D66's assertion expansions exist only as lookaround_design.md §6's corpus GENERATOR), so a dump written now would be a hand-copied restatement — the drift hazard `--list-syntax`/`--list-axes` were built to avoid (learnings §3: one derivation, two readers). WHEN THIS ROW LANDS THE DEFINITIONS AS DATA (construct × option-scope → definition), `--list-definitions` walks that table as the FIFTH registry surface, and the same table is what [DD-13b]'s `name`/`lib` resolution and the [LIB] store consume. CUSTOMER ADDED 2026-08-21, D66: the
  tranche C engine items — D63's second prefilter instance and DD-7's
  reverse BOT variant — are RE-BASED onto this row's core-reduction
  work; Frank's direction is to optimize the CORE lookbehind-anchor
  form the reduction produces, so (?m)^'s desugar
  `(?:\A|(?<=\n)(?!\z))` and every other lookbehind-shaped anchor share
  one optimizer; the start=0 `^` is ALREADY `\A` internally, and a
  one-byte fixed lookbehind lowers to the wave B/C context machinery,
  which becomes the core form's compilation target — see D66) — the
  NEWLINE CONVENTION axis (Frank,
  2026-08-12 tenth-session close). Q1 RULED 2026-08-18 (D64): NO axis
  declared; LF stays hardwired through the assertions module, whose
  newline-reference sites are written DEFINITION-SHAPED (a handed-in
  class, LF the sole definition — never scattered '\n' literals); the
  future shape parked here is newline as a TYPED compile-time
  definition consumed by insertion machinery (class-valued: negatable;
  sequence-valued: class-context use is a compile error) with boundary
  consumers as lookaround uses — revisit after M6.6 + the first
  insertion producer. **GENERALIZED (Frank, 2026-08-19, thirty-fourth
  session, mid-[M6.2]): the definition idea extends beyond `\n` to the
  ASSERTION FAMILY.** `$`, `^`, `\b` (and their multiline/caseless/
  encoding variants) become scope-resolved DEFINITIONS: a construct
  searches up the tree for a rebinding (a flag like `(?m)` = a local
  rebinding of `$`/`^`'s definition in its subtree), falling back to the
  default [SUPERSEDED 2026-08-23, RULED by Frank (journal, thirty-seventh
  session part 4; found stale by R34 C3): resolution is PROPAGATE /
  CAPTURE-AT-BUILD, NEVER WALK-UP — the binding point is a sibling event,
  not an ancestor, and injected subtrees must be position-independent; the
  "searches up the tree" phrasing here describes the SCOPE a binding
  covers, not the lookup mechanism] — the replacement value is an inserted rx (`\Z`≡`(?=\n?\z)`,
  `(?m)$`≡`(?=\n)|\z`, `(?m)^`≡`\A|(?<=\n)(?!\z)` — note the `(?!\z)`
  term IS the U11b carve-out, `\b`≡`(?<=\w)(?!\w)|(?<!\w)(?=\w)` with
  `\w` itself a definition). Value per Frank: shrinks the core rx set
  and simplifies the additions path — "we optimize insertions and we
  optimize them all." Manager assessment recorded with it: D62's
  parse-time resolution is already a degenerate form of this (cx->mods =
  the tree search, the node field = the resolved binding); the win is
  the ADDITIONS path (correct-by-composition on day one, folded fast
  path earned later) plus a SELF-ORACLE property (expansion vs folded
  implementation as an in-tree differential once lookaround exists); the
  cost truth is that folding work relocates to a composition RECOGNIZER
  rather than disappearing — today's zero-cost DFA mechanisms (context
  bits, class-indexed views) must still be reached; and the U11b lesson
  binds: a definition is a CLAIM ABOUT PCRE2 like any other — the tidy
  composition for `(?m)^` was exactly wrong until measured. Same
  parking condition as before (M6.6 lookaround + DD-14's call/insertion
  primitive); cross-noted at [DD-14]. **REFINED (Frank, same session):
  bindings are DIRECT REFERENCES TO RX in the appropriate format — NOT
  flags.** The environment maps construct -> rx VALUE directly; a flag
  letter like `(?m)` is a BINDING-MUTATION OPERATOR at its point of
  introduction (it swaps which replacement rx `$`/`^` are bound to, for
  the remainder of its scope); every later reference just DOES the
  replacement — no modifier state exists to thread, consult, or forget.
  Frank's stated value: simpler, and new replacements (encodings,
  newline conventions, user definitions) are added by adding bindings —
  one mechanism. Manager notes recorded with it: (a) this SUBSUMES
  D62's principle at the future architecture — there is no field either;
  a multiline `$` IS the substituted subtree, so the whole D47.5
  scope-blindness class becomes INEXPRESSIBLE rather than guarded
  (stronger than the compile-alarm the node-kind spelling offered);
  (b) "appropriate format" carries D64's typed-value constraint
  (class-valued where class context demands, negatable; sequence-valued
  a compile error in class contexts); (c) scoping matches PCRE2's own
  inline-flag semantics (references AFTER the mutation see the new
  binding, within the enclosing group); (d) HYGIENE — RULED BY SCOPING
  LAW, NOT MECHANISM (Frank, same session): call vs ref is TBD as an
  implementation choice, because inserted groups arise in REFERENCED rx
  either way and the law answers both: **groups inside an insert are
  locally referenceable BY NUMBER only (an insert's \1 is the insert's
  own first group; outer numbering does not see them), and globally
  referenceable BY NAME** (a named group in an insert is addressable
  from anywhere by name). Numbering is scope-local, names are global —
  which composes with D59/D61's caps-slot architecture (insertions
  append; primary prefix permanent) and [M6.5]'s dupnames machinery
  (name-run resolution already answers what a globally-visible inserted
  name means);
  (e) the U11b measurement obligation binds each binding's VALUE;
  (f) SCOPE OF THE REDUCTION (Frank, same session, confirmed by
  measurement): quantifier sugar is ALREADY collapsed (`+`/`{1,}` etc.
  are one A_REP node, engine bodies byte-identical, only the verbatim
  rx_info.pattern stamp differs); the class escapes are already
  hardwired class-valued bindings (D23/OS-1), \N already the newline
  definition (D64); possessive quantifiers reduce to the atomic cut
  per [M6.4]'s own row. The irreducible core after full reduction:
  classes, cat, alt, {m,n}+preference, atomic cut, capture, \A, \z,
  lookaround, and the path-fact family (\K, backrefs, DD-14 call) —
  \G stays primitive (position vs a RUNTIME value). THE DESIGN LANE'S
  FIRST WORK PRODUCT is the construct-by-construct table: primitive vs
  binding, each binding's value MEASURED against libpcre2;
  (g) OPTIMIZATION CONCENTRATION (Frank, same session): a tight core
  focuses every fold/prefilter/rung on few primitives and bindings
  inherit them free — [M6.2] lived the counter-case, five constructs
  each needing a hand-built folding mechanism;
  (h) THE CORE AS A TARGET IR FOR OTHER FLAVOURS (Frank, same session):
  grep/BRE-ERE, POSIX, oniguruma map as front end + BINDING LIBRARY over
  the same core — [V-D]'s translators and [V-A]'s regex.h shim become
  cheaper than their rows assumed (cross-noted there). HONEST LIMIT: a
  flavour's MATCHING DISCIPLINE does not reduce to bindings — POSIX
  leftmost-LONGEST vs PCRE2/oniguruma leftmost-FIRST is preference
  semantics of the core primitives themselves; a POSIX front end needs
  either a core longest-match mode or documented leftmost-first
  semantics. Measured, not assumed, per the U11b lesson.**
  pcrec is NEWLINE_LF today and that is
  ANCHORED, not assumed: every oracle measurement runs libpcre2 at
  options=0 (build default LF on this box), so \N's generated bitmap is
  the measured complement of {0x0A}, `.` is every-byte-but-0x0A, and `$`
  is before-final-\n; a convention change on either side fails PC-4 and
  the census probe loudly. PCRE2 makes newline a per-pattern CONVENTION
  (CR/LF/CRLF/ANYCRLF/ANY/NUL via the start-only (*CR)-family verbs or the
  API option; \R separately via BSR) — pcrec refuses the verbs cleanly
  today (Q1 tables, start-only), so the axis is closed off LOUDLY, no
  miscompile. COST PREDICTION when a consumer arrives (D18 earn-its-axis):
  `.`/\N fold into the front end per-convention like OS-1's caseless
  (byte-set swap, oracle-generated tables, zero engine cost) for CR/LF/
  NUL/ANYCRLF/ANY; the ENGINE work is `$` (and DD-6's multiline ^/$) —
  an EOL assertion that becomes set-valued under ANY/ANYCRLF and a
  TWO-BYTE SEQUENCE under CRLF, in both the forward and reverse DFAs
  (the M2.7/M2.12 EOL-variant machinery is single-byte shaped), and
  CRLF also complicates `.`'s complement. Decide with the assertions
  module or a real consumer, whichever asks first; measure the
  convention's effect on the censuses through the existing probe
  pipeline before writing any table
- [DD-14] ARCHIVED → docs/dev/plan_completed.md ("2026-08-25 (thirty-ninth session — [DD-14]: module `recursion` ships at D69 tier)"): the parent row and every sub-row A, A2, BC, D, LB, E, EMPTY, F, D27, K34, FB, G, CLOSE — all completed. Close summary: journal thirty-ninth session part 45. Open rows that came out of it stay in plan.md: [MECH-REACH], [TT-10] (widened), [OS-4]'s customer note, [DD-13]'s bench candidates, K36/K37 (known_issues). Archived 2026-08-25 by the manager.
- [DD-3] STATE:not-started — generated-API versioning/compat policy for vendored consumers (before M3) (R1 A-10)
- [FREESTANDING] STATE:not-started (BOONIES TIER — Frank, 2026-08-28: "I think memchr requires glibc. If so, there should be a switch for a no glibc build which in our world is a simple scalar replacement on one of the forms for prefilter. File for boonies") — THE LIBC-FREE EMISSION PROFILE. FACT CHECK first: `memchr` is ISO C (`<string.h>`), so every HOSTED libc has it (glibc, musl, newlib…); the target this row serves is a FREESTANDING build (`-ffreestanding`, no libc at all — kernels, bootloaders, bare-metal firmware, the "freestanding/embedded build profile" [M7.0] already names). SHAPE: one emitter switch (`--freestanding`, a generation axis with its stamp, [CHK-2]'s five things) under which the artifact calls NOTHING from libc: the candidate-scan forms that call `memchr` (the k=0 memchr form and [OPT-K]'s offset-set scan at k*) get a scalar byte loop in the same [ENG-FORM] slot — a SELECTION, not a special case — and the D82 bar applies (the scalar loop is a different representation object, measured, not a `#ifdef` inside the memchr one); every other libc reach in the emitted text is censused and replaced or refused: the emitter string literals today carry `memchr` (20 sites), `memset` (18), `memcpy` (16), `strlen` (18), `memcmp` (2), `malloc`/`free` (10/30 — the default frame/trail storage of the un-suffixed VM entries; under freestanding only the `_in` entries with a caller-provided buffer exist, and the un-suffixed ones are refused or emitted as thin `_in` wrappers over a static region, ruled at design time), and `--emit-main`'s driver (stdio) is simply unavailable. MEASURED on filing (the fuzz witness, a VM artifact with prefilter "none", split form): its .c + .h reach NO libc symbol at all and include only `<stddef.h>`/`<stdint.h>` — so a prefilter-less VM artifact is ALREADY freestanding-clean, and the switch's real scope is the DFA/hybrid artifacts' `memchr` scans plus whatever the un-suffixed entries' default storage and the driver pull in. The census of which sites reach a NON-main artifact (vs only the driver) is the row's first step; gcc's own `-ffreestanding` build of the corpus artifacts under the switch is the gate (a link with `-nostdlib` and a stub `_start`, or at least `-ffreestanding -fno-builtin` compile + `nm` showing no undefined libc symbols). Related: [DD-5] (`--std-c` portable emitter fallback — the same family of "emit for a smaller world" switches; the two should share their axis plumbing), [M7.0], [DD-14.FB] (the `_in` entries are the freestanding calling convention already). Not before the spine (queue discipline); no measured need yet (D77) — recorded so it is not re-derived.
- [DD-5] STATE:not-started — --std-c portable emitter fallback (switch-based) (R1 R-5)
- [DD-10] STATE:not-started — remaining unbounded C-stack recursion in the compiler (R3 critic, critic-perf): trie_build now has an explicit 256-frame/68 KB budget, but compile_ast and clo_visit's t1 edge are still bounded only by pattern structure. A 400-nested-branch-point alternation needs ~192 KB — fine on an 8 MB main thread, not on a musl 128 KB one, and pcrec is a library. Convert clo_visit to an explicit worklist and give compile_ast a stated budget, then the NFA cap can be derived from memory alone

## Option-specialization dimensions (D18) — each must EARN its engine

The caller names a SET of values per dimension and the product is over those
sets (D18). A singleton set is fully specialized and compiled away — asking for
case-insensitive ONLY is hyperspecialization, not an axis. A dimension is an
axis only when its set has 2+ elements. Each dimension below is a candidate for
that case; before it becomes an axis, measure whether specializing buys
anything, since a dimension that folds into the front end, is free at run time,
or is a pure wrapper is NOT an axis even when the caller names it plural. Predictions are in D18 — record the measurement against
the prediction, including when the prediction was wrong.

- [OS-0] STATE:not-started — the optional ENGINE FINDER module (D20). Given the SETS, drive the engine generator once per point of the product and emit the selector over the results. Its set-valued request surface lives HERE, not in `pcrec_options` — D20 deletes the API-change half of this step, because a generator that only ever compiles one point is correctly served by scalars. Two properties from D18 to preserve and to test structurally: dispatch resolves ONCE per search call and never reaches the hot loop, and a request with no plural dimension emits byte-for-byte what pcrec emits today (no dispatcher, no extra parameter, no indirection). Emit named per-combination entry points (`rx_search_ci_utf8`) as well as the selector, so a statically-known caller pays no dispatch at all. DEFERRED BY DESIGN: build this only once a dimension has actually survived D18's earn-its-axis test with a measurement behind it — if the OS-1/OS-2 predictions hold, it has no customer yet, and that is a good outcome rather than a stalled one
- [OS-2] STATE:not-started — encoding ascii/utf8: PREDICTED to fold, since APPROACH §4/§10 already commit to byte-wise UTF-8 automata with no hot-path decode, explicitly so ASCII and UTF-8 share one DFA emitter. Measure when M5 lands: is the emitted hot loop byte-identical in SHAPE between the two encodings for an equivalent pattern? If yes the axis collapses; if the UTF-8 path needs its own loop, that is a real axis and a surprise worth recording
- [OS-3] STATE:not-started — streaming: PREDICTED NOT to be a wrapper, and this is the one prediction with evidence already against the optimistic answer — the reverse pass rescans backward over bytes a stream may no longer hold. Feeds M3.0's design gate; do not write streaming code before it is settled
- [OS-4] STATE:not-started — anchoring: ENG_UNANCH vs ENG_ATTEMPT is ALREADY a cartesian split, and it has never passed this test. It exists because the reverse machine cannot check `^` at pp == 0, not because a per-start attempt loop was measured to be faster. Measure the cost of the split on the known-slow shape (`^` on only some branches, D8) and decide whether to close it by building the reverse BOT variant (DD-7) or to keep it with a number attached. An unjustified axis in the shipped compiler is the strongest possible test case for D18's own rule. **FIRST CUSTOMER (2026-08-25, pcrecdev2 / pcrec-bench):** the bench's whole-subject compliance regime is PCRE2 `ANCHORED|ENDANCHORED`; pcrec has no end-anchored entry, so the adapter's `_match_caps(...) == n` is sufficient-not-necessary (a leftmost-first prefix match that could reach the end by backtracking answers NO). Ruled idiom for now: compile `(?:orig)\z` (NOT `$`, which admits a final newline at options=0) and use the anchored entry — a separate artifact, so bench rows must name which one they timed. `ENDANCHORED` is the GENERATION-AXIS disposition ratified in docs/pcre2_options.md:103; this row is where it would be built. **RULED (Frank, 2026-08-25, fortieth session): NOT NOW — leave the idiom.** The axis is built later UNDER MEASUREMENT if the bench shows the two-artifact cost or the final-byte skip gap at rank; until then `(?:P)\z` + the anchored entry is the answer, and the final-byte fold stays a general-optimization candidate on [DD-13] (a fold on the idiom benefits every `\z` user, not just the bench). Reason in Frank's words: no artificial timeline; if we would be better served building it later under measurement, wait and see, and focus on builds we don't have to rebuild or roll back. This row's ORIGINAL charter (measure the ENG_UNANCH/ENG_ATTEMPT split's cost) stands and comes first — a sibling axis before that measurement is the un-measured cartesian growth D18 forbids

## Parser structure — the syntax construct registry (D24)

**THE AGREED ORDER (R6, 2026-08-10) is COMPLETE — the FIX-1 / PC-3+Q1 / FIX-2 /
Q2+SR-9 / MOD-0 / DOC-1 / PC-4 arc it sequenced is done and archived in
docs/dev/plan_completed.md.** Work these in sequence. Each is a
checkpoint: critic panel (D6), journal entry, plan STATE update, touched
CLAUDE.md files, commit, push.

Sequenced so each step pays for itself before the next is justified. SR-1/SR-2
collapse a duplication that has already produced one shipped bug; everything
after waits for a forcing function. Frank's priority stands throughout: the
95% path stays fast and simple, and exotic constructs earn only the right to be
named, cleanly rejected and queried.

- [TT-2] STATE:completed 2026-08-15 (lane tt2-parallel — relaunched after
  the first lane died mid-work, its sharding adopted with two defects
  fixed; merge ce2a080. Measured: reject 59.5s→5.8s at PROCS=12;
  test-vm 30.4→14.9s and test-codegen 10.1→8.7s via tests/lib/
  run_group.sh; `make -j$(nproc) -Otarget test` composes the full suite
  in ~44.6s vs ~8m49s serial; cli/registry measured and DECLINED with
  a re-measurement trigger (registry is correction-scarred, off the
  critical path); mech already had PROCS since 2026-08-12, verified.
  Sabotages both shapes per new path; serial PROCS=1 full suite green
  8m48.9s; populations conserved. docs/testing.md "Internal
  parallelism" section) — PARALLEL TEST INFRASTRUCTURE (Frank,
  2026-08-15, twenty-first session: "we have 6 cores. we should open it
  up"). Step 1 DONE same day (Makefile commit): make test/test-corpus
  set PROCS=nproc + TMPDIR=/var/tmp for the harness's existing worker
  mechanism — corpus 1449/0 in 56s at PROCS=12, was ~5min serial. The
  REMAINING work, one lane once the D45-stopgap branch merges (its
  timeout wrapper touches the same runner scripts — disjointness):
  internal parallelism for the other serial suites (reject 528, codegen,
  vm, cli, registry — xargs -P or run.sh's worker-reinvocation pattern,
  whichever fits each script), section-level composition (make -j over
  the TT-1 section targets, output legibility preserved), and a mech
  assessment (parallel sabotage rows need per-row build dirs — measure
  whether the win justifies it). DISCIPLINES that travel with it:
  run.sh's own aggregation rules are the house template — a lost worker
  HARD-FAILS (never reads as a pass), summary-line format stays
  grep-identical in both modes (mech reads it); population accounting
  exact at every PROCS; D45 timeouts must hold under full parallel load
  (sub-second compiles × 12 workers is fine at 5s — but MEASURE the
  tail, don't assume); wall-time before/after recorded per suite.
- [SR-5] STATE:not-started — guard the fast path CLAIM, do not just assert it.
  REWRITE THE ASSERTION FIRST (R6): the claim as written here — "base-tier
  patterns must perform ZERO registry lookups (`(?:` excepted)" — is FALSE in
  both directions, measured with an instrumented build on 2026-08-10. `(?:`
  performs zero (parse.c answers it before the registry), while `[abc]` performs
  one and `[a-z]+@[a-z]+\.[a-z]{2,4}` performs three, because the class-bracket
  doorway is on the base-tier path. Written as specified, SR-5 would fail the
  moment it was built, or would have to assert something untrue. The property
  actually worth guarding is a BOUND: lookups <= one per non-negated `[` plus
  one per `[` inside a class, and zero for a pattern with no character class. Use
  an instrumented build with a lookup counter, the way run_trie_identity.sh
  uses `-DPCREC_NO_TRIE`, so no counter exists in the shipped build (TS-1 would
  reject one anyway). Pair with the M2.9 compile-time budgets
- [SR-6] STATE:not-started — MODULE HANDLERS move to their own module TUs as
  each module lands (as-built naming: src/parse/mod_*.c flat in src/parse/ —
  mod_modifiers.c, mod_verbs.c — not the src/parse/ext/*.c subdirectory this
  row originally predicted; R18 docs critic. The verbs entry below remains
  accurately PENDING: MOD-0.4 moved the doorway/tables to mod_verbs.c but no
  verb produces yet, so SR-6's real per-verb handler has not landed)
  (esc_class, esc_assert, esc_backref, esc_uniprop, esc_misc,
  grp_lookaround, grp_named, grp_atomic, grp_cond, grp_recurse, grp_modifier,
  grp_callout, verbs, cls_posix). Not a step to schedule — a rule to follow
  when a module is implemented. NOTE (R4 critic finding): the row does NOT yet
  name a handler — that field arrives with SR-2 — and the status vocabulary has
  no value meaning "implemented by module X"; RS_MODULE unconditionally implies
  rejection today. SR-6 therefore carries an unwritten schema change, not just a
  file move
- [SR-7] STATE:deferred — FLAVOURS (families as named masks: `pcre2-10.46`,
  `pcre2-dfa`, `python-re`, `ere`). Deferred by D18's earn-its-axis rule
  applied to the front end: exactly ONE flavour-varying row is known (`\v`), so
  the selection machinery has a set of size one and no customer. The column
  exists from SR-1; it turns on when a second flavour earns it. Note
  `pcre2-dfa` is the ENGINE-capability axis expressed as a family, so this step
  and DD-7/M4 are related. BLOCKER TO PLAN FOR (R4 critic finding):
  `pcrec_registry_find(kind, sel)` takes no flavour argument and returns the
  first row matching a byte, so SR-1's "short chain for the rare flavour-varying
  byte" is not expressible in the shipped shape — SR-7 must change that
  signature. Today a duplicate selector is caught loudly by tests/registry/
  rather than silently shadowing, so this is a design debt, not a live bug
- [SR-8] STATE:deferred — ENGINE-capability check moves OUT of the parser.
  Today `\1` is rejected by the PARSER as "requires module 'backrefs'", but
  backrefs parse fine and simply cannot LOWER to a DFA. When M4's VM exists the
  honest diagnostic becomes "requires the VM engine", which is a lowering-time
  check against the registry's `engines` column. Blocked on M4 having a second
  engine to choose between. **DISPOSITION (2026-08-17, [M4.7a] + manager
  redirect):** the VM exists now, and lane/m47a found this row's premise
  does not hold in code — `\1` is refused for lack of an implementation
  (no producer), not for engine incapability, so there was never a
  parser-side engine check to relocate; the parser's refusal wording is
  already correct and unchanged. The lowering-time CONSULTATION this row's
  charter describes is DISCHARGED-BY-ARCHITECTURE today rather than built:
  zero producers means zero customers (D18/OS-0/D53), so
  select_engine.c's socket stays unpopulated machinery on purpose, and it
  LANDS WITH THE FIRST VM_ONLY PRODUCER (whichever M6 module gets there
  first) rather than ahead of one guessing at a contract from sample size
  zero. Until then, tests/registry/registry_check.c's
  check_engine_capability_tripwire guards the gap: it asserts every
  VM_ONLY-masked RS_MODULE row has no wired producer, and its failure
  message on the day that stops being true names building this
  consultation as the required next step. This row's own STATE stays
  `deferred` on that basis — not blocked on anything further, but not
  something to build ahead of its first real customer either
- [SR-10] STATE:not-started (CROSS-NOTE 2026-08-23, from the [DD-14] ASK 3 discussion: Frank's 'eat our dogfood' idea — the registry's `syntax` column as a PATTERN pcrec itself compiles, so the row table becomes machine-checkable (witnesses derived from the syntax, a differential over the column) — belongs here/[DD-13] as a CHECK on the table, explicitly NOT as its dispatch, which R6 ruled byte-keyed with measurements.) — SINGLE NAMESPACE DEFINITIONS (Frank,
  2026-08-12: "do we have a single set of 'modules' or 'encodings'? we
  should, and then those should be directly referenced — this enforces
  existence over everyone using string names"). One authoritative table per
  namespace — MODULES, ENCODINGS, (post-D37) NAMED FEATURE SETS, and
  flavours when SR-7 lands — with every renderer and parser of a namespace
  member referencing the table entry (enum/identifier + its one string),
  never a loose literal. Existence becomes a compile-time property: a
  diagnostic cannot name a nonexistent member because the name is not
  reachable except through the table. The both-directions checks then guard
  table⇔docs instead of table⇔scattered-strings. MOTIVATING INSTANCE
  (R20/0.8c): src/core/compile.c:97 hand-wrote "requires module 'utf8'" —
  a member of no namespace — while cli/main.c separately hand-mapped
  "utf8"→PCREC_ENC_UTF8; slice 3's reword fixes the instance, THIS row
  fixes the class. Audit inventory at start: every `module '` /
  `--features` / `-e` string site, the enabled.c parser, the registry
  module column, compile.c's encoding gate
- [DOC-BM] STATE:deferred — **the bound-mode document** (design §18.5):
  full 32-bit option sweep with seeded generators, the `RS_NOT_OFFERED`
  split, the `EXTRA_BAD_ESCAPE_IS_LITERAL` 18-cell migration. Constraint:
  must exist BEFORE §7.1's five escape rows land (their `status` values are
  its output; A1's pins hold the surface meanwhile).

  ~~STATE:blocked (2026-08-11 — the R11 design panel refuted parts of
  D30, exactly as R10 refuted D29, and the resolution is Frank's call.** See
  `docs/dev/reviews/2026-08-11-r11-parse1-mod01.md` and D30's inline R11 marks.
  NOTHING WAS BUILT; the panel ran against a written design and every finding
  cost a paragraph rather than a commit. **Seven dispositions** are listed at the
  end of R11 and they are the specification for the re-resolution, which wants a
  D32 the way D30 answered R10. The three that change the most work: (1) D30
  §2's non-optional check is FALSE as written — "promise a module wherever
  libpcre2 DISPATCHES" has 93 counterexamples in 1,672 probes and ALL 93 are
  pcrec being CORRECT, because "dispatched" does not imply a module is owed;
  (2) rank is almost entirely UNCHECKED — 20 of 22 rows accept any value to 250,
  the single prefix pair is a THRESHOLD not an ordering, and two of D30's three
  required checks fire on identical boundaries in all 5,632 probes, so one of
  them adds nothing; (3) the returning-doorway defect PARSE-1 handed over is
  FOUR call sites across three doorways, and `pcrec_ext_escape`'s pair is
  UNDEFINED BEHAVIOUR — making it return makes `build/pcrec` itself SIGSEGV on
  `[a\qb]` while `a\qb` silently launders the pointer out of `%rax`. Of the
  group-discard class, 7 of 18 generated patterns are byte-identical to a
  SMALLER pattern and 0 of 18 behave as the contract promises.
  Measured facts that survive and should be reused: 100 rows / 18 tails /
  exactly 4 multi-row buckets holding all 18 tailed rows = 22 rows (D30's own
  figure, independently derived); D30's undocumented 0/25/40/70 rank mapping
  recovered and verified 22/22 two ways; `ext.c` never reads `.tail` so its six
  call sites need no change; **[RETRACTED — see R11's addendum: `find()`'s
  same-length tie-break is UNREACHABLE, because it needs an identical
  `(sel,tail)` pair which `registry_check.c:184-193` already forbids, and rank
  would NOT make it loud — two duplicate rows at ranks 25 vs 26 resolve
  silently]**; and existing
  external coverage of tailed rows is 2 prefixes, not the 10,200 probes it
  looks like) — the interface, as D30
  resolves it. **DECLARED RANK**: a row carries an integer rank; every
  recogniser in the bucket runs; the highest-ranked ANSWERING row wins; two
  answering rows at EQUAL rank is the defect. Rank is DATA, so no recogniser
  needs to know its siblings and the bare fallback answering "always" at rank 0
  is correct rather than naive. The doorway's answer is **not an enum** but
  three facts — (dispatched?, compiles?, whose message?) — so that `(*MARK)`'s
  "CLAIM the construct, name NO module" has a cell. Plus `tail_default` and its
  row parameter, and bucket dispatch. THREE checks, and all three are required:
  (a) the **per-row `syntax` check** (C4-6) — a row's own `syntax`, fed to its
  bucket, must be won by THAT row and no other; it is TOTAL over 22 rows, needs
  no generated space and no oracle, and it is the primary instrument; (b) the
  **rank sweep** with `check_tail_precedence`'s **LIVENESS CLAUSE CARRIED OVER**
  — measured, inverting the one prefix-related pair is observable on exactly ONE
  input in 176,544, so a sweep that asserts nothing must SAY so rather than
  print a PASS; (c) the **reachability differential** against libpcre2 — *pcrec
  must promise a module wherever libpcre2 DISPATCHES* — which is the only thing
  that covers the malformed-body class and is NOT optional. Prototyped and
  sabotaged before adoption; see D30 §1-2 for the numbers

## Optimization waves (D21) — algorithmic, then profiled code, then compile time

Not a milestone: a shape applied at appropriate points, in this ORDER. Profiling
a bad algorithm optimizes the wrong loop, and optimizing compile time before
execution speed trades the primary goal (D18) for the secondary one.

- (Frank, 2026-08-12, on this whole block: "this project's greatest benefit
  will be its testing suite. builds confidence and lets us go crazy when we
  get to optimizations" — suite strength is the PREREQUISITE INVESTMENT for
  everything below; an optimization the suite cannot referee does not land)
- [BENCH-1] STATE:not-started — FEATURE-SPANNING BENCHMARK EXPANSION + THE PRIORITIZER (Frank, 2026-08-13 sixteenth session): today's bench is 9 cases (a-i) of deliberately basic shapes — good regression gates, not a capability map (Frank: "whenever i see benchmarks, its usually a series of rather basic benchmarks that do not really exercise the capabilities"). Build a benchmark that SPANS the feature set and the complexity range: per-feature-family case GROUPS (literal/memchr shapes, classes, alternation/trie widths, bounded repeats, anchors/EOL, dense/counting — the case-f family, captures (M4), backrefs/lookaround/atomic (M6), UTF-8/\p (M5), plus real-world-shaped patterns), each family at graded complexities; pattern sources = hand-designed families + the PCRE2 testdata import (M7 — this row is deliberately scheduled around that import so the corpus arrives with it) + generated shapes where a family needs a sweep. STRUCTURED FOR SPOT-CHECKS exactly like TT-1's tiers: every case and group individually addressable (make bench CASE=... / GROUP=...), the full sweep at evaluation points only. TWO INSTRUMENTS, deliberately distinct — M2.11's ruling stands: the regression GATE stays absolute per-case floors (cross-engine ratios move for reasons that are not our regression); the new PRIORITIZER is a cross-engine RELATIVE ranking vs libpcre2 — informational, never a gate — whose output is a worst-first worklist. Frank's stated optimization workflow, recorded as the row's purpose: (1) OPT-A's survey incl. the pattern-generation study, then (2) work the prioritizer list from the relative worst downward. Every number under D12/D17/R3.10 discipline; MECH-3's provenance-refusing wrapper is the intended measurement vehicle and lands first. Sequencing: after the main feature set is built and proven (post-M6, with M7's testdata), BEFORE the OPT waves open — this row is the OPT waves' worklist generator. AMENDED 2026-08-13 (same session, positioning discussion): the case groups include a LATENCY / SHORT-SUBJECT group — time-to-first-match from process start (the AOT structural win: tables page in from .rodata vs pcre2_compile + JIT warmup per process) and per-call overhead on short subjects (log lines, field validation — the dimension real workloads are dominated by and typical benchmarks skip); and the prioritizer gets a second reading — the BEST relative cells feed the positioning note (Beyond M7), not just the worst cells feeding the fix list. AMENDED 2026-08-14 (D42.8): the prioritizer worklist has a KNOWN HEAD before it runs — case (f) at 0.151 relative, re-homed here from [DD-9] (archived) with engine_m4.md §8.4's three findings attached (wrong-lever computed goto; ~2x reverse-pass share; bit-parallel shift-and candidate); [OPT-SIMD] is the adjacent lever row.
- [BENCH-CEIL] STATE:not-started — THE EXPERT-C CEILING ARM (Frank,
  2026-08-18, thirtieth session: "for a set of (dfa?) patterns, i'd
  like to directly write performant C code to implement them and
  consider them one engine to compare against... ideally we should be
  able to match the performance but realistically i'm hoping we can
  get close or at least understand how far off we are"). For a chosen
  set of bench patterns, HAND-WRITTEN performant C matchers ride the
  bench as their own engine arm. WHY THIS ARM IS SPECIAL: unlike
  pcre2-interp/jit (different execution architectures), hand C shares
  pcrec's exact execution model — same compiler, same flags, same
  box — so the pcrec-vs-hand gap DECOMPOSES into attributable
  generator overheads (table dispatch vs specialized control flow,
  per-byte machinery vs wide compares/memcmp, prefilter choices), and
  the per-case gap table is the OPT waves' most direct worklist ("hand
  code does X, the emitter does Y" — the [OPT-A] literal-run and
  spelling-menu leads of 2026-08-18 are exactly the first two entries
  this arm would have generated). Rules recorded at filing: (1) v1
  scope is DFA-TIER patterns (hand-writing a correct backtracking/
  capture matcher is a different order of difficulty; VM-tier cases
  optional later, and a hand VM case would first need its semantics
  pinned against the spec); (2) hand code must be OBSERVABLY
  span-identical on the case's subjects — compare.sh's cross-engine
  agreement check already enforces this per case (INVALID, not timed,
  on mismatch), which is the correctness bar; (3) any technique a C
  programmer would write is allowed — that is the point of a ceiling —
  but each case documents its technique so gaps stay attributable;
  (4) same harness, same pinned-run discipline, floors optional (the
  arm is an INSTRUMENT like the prioritizer, not a gate — hand code
  regressing means nothing about pcrec). SCHEDULING (Frank's stated
  timing): after the main spine, with the benchmarking/perf-iteration
  phase — alongside [BENCH-1]'s build-out and feeding the OPT waves;
  a THIN early slice over today's a-m cases is cheap if wanted sooner.
  Authorship is expert-lane work (opus tier) or Frank's own hand;
  cross-links: [BENCH-1] (home instrument), [OPT-A]/[OPT-SIMD] (gap
  consumers), [ENG-PGO] (hand code embodies workload knowledge = what
  PGO should recover mechanically), D52's pcrec-bench (a hand-C testee
  triple is also natural THERE later; the in-repo arm is the
  fast-iteration instrument).
- [OPT-1] STATE:completed (CLOSED 2026-08-26 ~11:5x on Frank's ruling ("agree with recommendations"): the tiering bet HOLDS on the exemplar workload — 2/165 orig, 7/165 factored escalations, one of them a 25 B subject; STEP 4 (static length thresholds) stays a chartered-NOT-started candidate, reopened only by a population that asks — [B11]'s log-line set through the same counter (D77). The loop's first optimization: chartered from a bench row 2026-08-25 ~14:3x, shipped abi 5/6, measured closed the next morning. STEP 3 MEASURED 2026-08-26 ~13:3x, lane srEsc, sonnet, tests/bench/tier_escalation.sh + tier_escalation_driver.c (new; counts real -DRX_TEST_TIER_HOOK calls per subject, not run_tiered_entry.sh's synthetic depth ladder): the escalation RATE over pcrec-bench's bench/email exemplar (RFC 5322, READ-ONLY sibling repo) — orig.rx/factored.rx forced --engine=vm (confirmed: `auto` selects DFA for BOTH here, which has no tier — a DFA-forced run would measure nothing) in the whole-subject form (`(?:P)\z`, `rx_match_caps`, the 85 compliance subjects) and the search form (`rx_search`, the 77 search_short + 3 x 1MB throughput subjects), plus `floor.rx` (`@`) as a negative control ridden through the same pipeline (single-tier by construction, 0/165 escalations, as required). MEASURED, whole-subject: orig 2/85 (2.35%, s-058 4011B pathological 2000-deep dotted local part + s-061 2008B long many-label domain, BOTH still MATCH through the deep tier — the stamped 2048/3072 default suffices for the hand-inlined pattern) vs factored 6/85 (7.06%, the same two PLUS s-059/s-063/s-064 — and **s-058/s-059/s-061/s-063/s-064 all give up PCREC_ERR_FRAMES(-3) with escalated=1 on every one, exactly the bench inbox's P2**, confirming they do not fit even the stamped default, matching pcrec-bench's independently-measured 32768/131072 `_in` sizing — PLUS s-072 (25B, "quoted string missing closing quote", the exponential-backtracking hazard class NOTES.md names), which escalates and still answers nomatch, the SMALLEST escalating subject in the set (two_tier_entry.md section 7's "deep can be a very short subject" cliff warning confirmed on a REAL subject rather than the synthetic `((a)|(aa))+b` witness). search_short: orig 0/77, factored 1/77 (s-072 again, 25B, still MATCHES here). throughput: 0/3 both patterns — `t-c-long-atom-run` gives up on STEPS/WORK before ever reaching FRAMES (orig giveup:-4 WORK, factored giveup:-2 STEPS, both escalated=0), so it never triggers the mechanism this instrument counts. Boundary sizes (bytes): orig/factored whole-subject maxNoEsc=10252 (s-057, 10KB local part of plain atom chars — LARGE but cheap, not ambiguous); factored whole-subject minEsc=25 (s-072); orig whole-subject minEsc=2008 (s-061); factored search_short maxNoEsc=43 minEsc=25. TOTALS: floor 0/165, orig 2/165 (1.2%), factored 7/165 (4.2%) — **the bet holds on this workload**, so D77's own trigger for STEP 4's static fast/deep predictor is NOT met by this number alone; the five factored FRAMES give-ups are a separate, already-known problem (undersized stamped default for a call-bearing pattern, already fixed by the measured `_in` buffer) that STEP 4's guess-the-boundary heuristic would not change, since it only chooses fast-vs-deep and never grows the deep budget. NO pcrec-internal exemplar subject FILE exists (checked: tests/*/gen_corpus.py generate synthetic .rxt corpora procedurally, tests/bench/run_bench.sh's THROUGHPUT subjects are generated on the fly, neither is a stored real-world population) — bench/email is the only exemplar measured. Full per-cell/per-subject table: `bash tests/bench/tier_escalation.sh` (not archived verbatim here). STEP 2 CLOSED 2026-08-26 09:1x on the battery-proven tree 6e8edfb — the two-tier entries ship at abi 5 (then 6); NEXT = STEP 3, the escalation rate over exemplar subject files via the -DRX_TEST_TIER_HOOK counter, before any fast-size tuning or STEP 4's thresholds; STEP 2 MERGED 48e0c41 2026-08-26 00:02 — its battery on d0a9ab5 GREEN (test 1,558/0, san, matrix 180/0/6/0) with THREE anchor ANOMALIES (S179/S183/S67 drifted under the entry refactor; re-anchoring in lane srAnchor); two abi second sites and one K35 sort the lane missed were fixed on main (bf20427, 31926ca); a 64-byte sentinel buffer vs the 60-char prefix limit fixed (d0a9ab5) and exposed K38; lane srTier — the TWO-TIER DEFAULT ENTRY, design docs/design/two_tier_entry.md written before the code: one emitter for the three un-suffixed entries, fast capacities derived ONCE and read by both the stamps and the bind, `RX_FAST_FRAMES`/`_FAST_TRAIL` on every VM artifact, escalation to a noinline deep function on FRAMES only, `-fno-tiered-entry`; abi 5, (B) pin 469a432, (A) unchanged; run_tiered_entry.sh 17/0 incl. the effectiveness floor and the caps-array span comparison; K33 narrowed; rx_search 131,216 → 3,184 B; 213-268 → 45.6-48.8 ns/call; the numbers and the r38 dispositions are in the merge commit and the review. STEP 1 MEASURED 2026-08-25 ~19:3x, lane srOpt1, no code: REPRODUCED 2.2× on the bench's `quick` (pcrec-vm 29,737 vs vm-in 13,548 ns/call, 77 subjects) and 5.05× on a 16 B fast-matching subject (233.8 vs 46.3 ns/call, N=100k, median of 5, taskset). ATTRIBUTED: (a) gcc STACK-CLASH PROTECTION probing the 98,512 B `rx_run_buffers storage` local (24 pages; `-fstack-usage`: rx_search 98512, rx_search_in 208) — `-fno-stack-clash-protection` alone: 233.8 → 46.2 ns, i.e. ~99 % of the gap; (b) per-call init is 144 B on BOTH paths (excluded by code reading); (c) page faults O(1) per process, a pre-touch control changes nothing (excluded); (d) frame 24 B, SPLICED, no linked call (excluded). GENERALITY: the tax is proportional to the STAMPED default — `(\w+)\s+\1` (2/5 frames, 272 B) and `(?<=foo)bar` (3/3, 240 B) pay NOTHING (0.98×, 0.99×); it hits patterns whose default is large, i.e. the deep-sized ones. STEP 2 — THE FIX, RULED by Frank 2026-08-25 ~21:2x ("an elegant use of the frames error; I agree with the approach"): the TWO-TIER ENTRY — the un-suffixed entries carry a SMALL on-stack buffer (a page or less: e.g. 64 frames / 96 trail = 3,072 B) and, on PCREC_ERR_FRAMES only, call a separate `noinline` deep function that owns the full stamped storage and re-runs the match (the VM is deterministic: byte-identical answers; §5.3's no-allocation/no-thread-local contract kept; the depth ceiling D73 ruled is UNCHANGED; the probing cost moves to the slow path only). D6 CRITIC r38 (docs/dev/reviews/2026-08-25-r38-two-tier-entry.md): NO blockers — identity byte-for-byte across 377 escalations incl. captures, noinline survives LTO; five should-fixes to the lane (the spec blended two specimens' numbers; the ESCALATION CLIFF must be stated — ~1.6× SLOWER above the fast boundary, 2.8× discontinuity at it, on `((a)|(aa))+b` 'deep' is a 22-byte subject; the check needs a floor on the tier's effectiveness and a spans comparison). STEP 3 (next, before any fast-size tuning): the ESCALATION RATE over exemplar subject files via the `-DRX_TEST_TIER_HOOK` counter — the bet's number; capture-heavy patterns (>~145 slots) get no tier and the FAST=16 cutoff has no measured win (r38 note 6); a `--fast-tier=N` knob is the general lever if the number says the default is wrong. STEP 4 CANDIDATE (Frank's question, 2026-08-25 ~22:3x: "could the boundary be predicted?"): YES, statically — frames pushed ≤ subject length × the pattern's worst-case frames-per-byte, a coefficient the emitter can derive from the pattern's structure (the recursion specimen's ~2 frames + ~9 trail per nesting level is the measured instance). Two stamped per-artifact thresholds: `RX_FAST_SAFE_LEN = FAST / k_max` (a subject at or below it CANNOT overflow — the fast attempt is riskless) and `RX_FAST_HOPELESS_LEN = FAST / k_min` (above it the fast attempt is wasted — go straight to the deep path); the band between stays the bet; k_min = 0 degrades to today's behaviour. Zero runtime state (§5.3 forbids a dynamic guess inside the artifact; the caller can hold one and choose `_in`). RULED IN SPIRIT (Frank, ~22:4x): the guess "doesn't have to be 100 %" — a wrong guess never changes an answer, only its cost, and both wrong directions are bounded (deep-on-shallow: one probe loop, ~190 ns; fast-on-deep: the double run, ~1.5×), so the OBJECTIVE is the EXPECTED cost over the subject distribution: one per-pattern rule of thumb (a length threshold from the pattern's typical frames-per-byte, or tuned on the exemplar file) may beat both pure strategies; "if a user is really concerned, they should allocate themselves" (`_in`). BUILD ONLY IF STEP 3's escalation rate says the middle band matters (D77). Alternatives measured/considered: shrinking the stamped default (trades D73's depth ceiling for speed — not general); `no_stack_clash_protection` per entry (a hardening opt-out on emitted code — a posture decision, Frank's, and the attribute's existence in gcc is unverified). It is an emitter change (scaffolding: abi bump + re-pin per D76; the VM program region unchanged) — one opus lane with a design note and a D6 critic, AFTER srStamp lands (both touch entry emission). Original charter follows) — THE LOOP'S FIRST OUTLIER (pcrec-bench O-4,
  2026-08-25 ~14:3x, report reports/2026-08-25-email-specimen-0.1-budu-
  ryzen1600-repin-692c2e8.md, bench 0cf336c): at the SAME pin 692c2e8,
  `pcrec-vm-in` (the `_in` entry with a once-touched 2.75 MiB caller
  buffer) is FASTER than `pcrec-vm` (the un-suffixed entry, stamped
  default 2048/3072) on EVERY regime — orig/short-search 12,546 vs
  28,997 ns/call (2.3×), orig/compliance 62,732 vs 80,228,
  factored/short-search 54,118 vs 69,538. So the un-suffixed VM entries
  pay a PER-CALL cost the `_in` path does not, of the order of 16 µs on
  a ~256 B subject — larger than the whole match. General: every
  VM-selected pattern (backrefs, lookaround, linked recursion — sub-bench
  3's whole population) pays it on every call through the default entry.
  CANDIDATE CAUSES, each one measurement: (a) the 98-131 KB run struct on
  the C stack — gcc's stack-clash protection probes every page of a large
  frame (~24-32 page touches per call) — measure with
  `-fno-stack-clash-protection` and `-fstack-usage`; (b) zeroing or
  initialising the frames/trail arrays per call (`rx_run_state_bind`, any
  memset/`= {0}` on the run struct) — read the emitted entry, count bytes
  written before the first instruction of the match; (c) the first-touch
  page faults of a fresh 131 KB stack region on each call when the stack
  has been unwound past it (the `_in` buffer is touched once and stays
  resident) — `perf stat -e page-faults` on both entries; (d) the trail
  and frame layout (40 B vs 24 B frames — the bench's factored form is
  SPLICED, frame 24, so this is not the linked-call widening). STEP 1 is
  a MEASUREMENT lane (sonnet; no design): reproduce the 2.3× with the
  bench's `quick` or a driver in tests/bench/, then attribute it across
  (a)-(d) with one control each. STEP 2 is the general fix, chartered
  from the number — candidates already visible: lazy initialisation (no
  byte of a frame is written before it is used), a smaller stamped
  default with the `_in` path documented as the depth remedy (D73 kept
  the number; a per-call cost is a NEW input D73 did not have), or
  emitting the default entries as thin wrappers over `_in` with a
  static-thread-local... NO — allocation and thread-locals are forbidden
  by §5.3's contract; the fix must stay on the stack or in the caller's
  buffer. Identity gate: the `_in` entries and every answer byte-identical
  across the fix; the bench row (O-4) is the exercising case (D79 item 4).
  Queued behind [DD-13]'s stamps; the first optimization lane of the loop.
- [OPT-2] STATE:completed (CLOSED 2026-08-29 ~05:4x INTO [ENG-ABS]: the unwrapped-forward match-here it measured as the lever is BUILT and battery-proven on 808740c — matching subjects 1.031× the VM (target ≤ 1.046×, from 2.077×), the 35 short valid emails 0.482× (target ≤ 0.571×, from 1.207×), the failing 1 MB probe 363,305× cheaper; nothing else was owed on this row) — formerly STATE:started (STEP 2 MEASURED 2026-08-28 ~13:5x, lane opt2m, docs/dev/opt2_anchored_match_measurement.md, merged 5c2fdf4 — nothing under src/: THE STEP-1 LEAD IS REFUTED TOO — `rx_match` on the plain `orig` DFA vs the `(?:orig)\z` DFA over the bench's 85 compliance subjects differs by 3.7 % on the set, 3.3 % on the 40 matching subjects (one predictable `scan_position == subject_length` branch per byte + a restructured accept check), not 3.7×; on a `match`-regime subject the plain form scans to the end too, because the subject IS the match. WHAT THE 2× IS (the DFA-vs-VM gap reproduced in-tree at 2.133× set-grain, = the bench's 2.153× re-pin, so [OPT-3] STEP 2 already halved the 692c2e8-era 3.7×): THE REVERSE PASS — a cost-isolation patch (scratch, timing-only, answer-incorrect by construction) that deletes the reverse scan takes matching subjects from 2.077× behind the VM to 1.046× (parity) and the 35 ordinary short valid emails from 1.207× behind to 0.571× (43 % AHEAD); ~50 % of DFA cost on every matching split, 13.9 % on non-matching. MANAGER'S READING CORRECTION on the doc's "a value `rx_match` never needs": with the WRAPPED (self-looping) forward machine an accept can belong to a LATER start, and the reverse pass is what lets `rx_match` reject those — the start is unneeded only when the machine is UNWRAPPED and run from `ctx->pos`, which is exactly lever (a). THE LEVER, ranked by the lane: (a) [ENG-ABS]'s already-recorded second mechanism — anchored match-here via the unwrapped forward DFA from `ctx->pos`, no reverse pass, no candidate skip; NUMBER TO BEAT: the isolation understates it (it still pays the self-loop/skip machinery), so at/below VM on matching subjects, ~0.57× on short ones — this is [ENG-ABS]'s second forcing measurement and its gate is now MET by the numbers; (b) the `\z` view cost folds into [DD-13](b)'s general fold (3-5 %, not its own charter); (c) reverse dead-state exit — moot, the reverse loop already has it. NEXT: [OPT-2] closes into [ENG-ABS]'s unwrapped-forward mechanism when Frank opens it; nothing else is owed on this row. STEP 1 MEASURED 2026-08-25 ~19:3x, lane srOpt1: the dead-state-exit hypothesis is REFUTED for the fail path — anchored `\z` and plain DFA forms cost the same on failing subjects at every length (fail-first ≈0.35 ns/B, a table lookup per byte; fail-late ≈3.3 ns/B, a transition per byte; both ~linear, within 10 %). WHAT THE EMITTED C SAYS: a DFA artifact's `rx_match` (orig_anch_dfa.c:703-711) runs the UNANCHORED `rx_search` and filters `caps[0][0] != ctx->pos` afterwards — the [ENG-ABS] shape — so an anchored match scans for LATER starts it will then reject, and the `\z` end-view only changes acceptance at `scan_position == subject_length`. NEXT MEASUREMENT (the lane's lead, unmeasured): on MATCHING subjects the plain form exits at its last-accept while the `\z` form must scan to the end — likely the 3.7×; measure on the bench's 85 compliance subjects split matching/non-matching. THE GENERAL FIX is a TRUE ANCHORED DFA ENTRY — start at `pos`, stop at the dead state, never scan for later starts — which is [ENG-ABS]'s charter arriving through the loop (D79 item 4). Original charter follows) — THE LOOP'S SECOND OUTLIER (from the manager's
  O-5 reading of the same re-pin report, 2026-08-25 ~14:4x): on orig /
  match-compliance (85 whole-subject cells, 10-1000 B), the DFA
  `(?:P)\z` artifact costs 234,114 ns per set vs 62,732 for the VM form at
  the same pin — 3.7× SLOWER, ~2.7 µs vs ~0.7 µs per subject — far more
  than [DD-13](b)'s last-byte skip cost can explain. HYPOTHESIS to
  measure first: the anchored DFA match scans to the END of every
  non-matching subject instead of stopping at its dead state (a
  table-DFA in a dead state has no way out; the VM fails at the first
  mismatch). MEASUREMENT: emit the `\z` form of orig, run the anchored
  entry on a non-matching 1,000 B subject vs a 100 B one — if cost
  scales with length past the first mismatch, the dead-state exit is
  missing (or `\z`'s end-view state prevents it); read the emitted match
  loop for the dead-state test. If confirmed, the GENERAL fix (dead-state
  early exit in the anchored DFA loop, or the end-view fold [DD-13](b))
  benefits every anchored DFA match, not the bench. Needs the per-subject
  pass/fail split from the bench (requested via O-5 interpretation item)
  to model the cost. Queued with [OPT-1]; one measurement lane can take
  both (same driver, same box-quiet requirement).
- [OPT-3] STATE:started — **STEP 1 MEASURED 2026-08-26** (lane srOpt3, docs/dev/opt3_dfa_scan_measurement.md; measurement only, nothing under src/): the SKIP loop is NOT the loss and SIMD is NOT the fix — it skips ZERO bytes on `t-b`/`t-c` (entered 190,651 times on t-b, skipping nothing: the byte that returns the machine to state 0 is consumed by the TRANSITION loop first, so it can only skip the 2nd..nth byte of a run, and real text's runs are length 1), and a 7x-faster shufti skip makes all three bench subjects SLOWER (+3.9/+0.4/+1.5%); the SIMD crossover is measured at ~32-byte non-candidate runs, which these inputs never reach. ALL the cost is the TRANSITION loop at ~3.2 ns / 10.7 cycles per table step (t-a is 2.000 steps/byte — forward + reverse — hence 6.19; per-match fixed overhead ~0, the extra pass IS the reverse scan), LATENCY-bound on a 7-cycle lea/lea/movslq/load chain with ~2x spare issue width (2 independent streams: 1.97x). LEVER, measured on the real artifact and answer-identical over 40,469 answer lines / 91 subjects: pre-multiply the transition table by its stride — **1.28x on the bench's own three subjects, 1.466x -> 1.149x vs PCRE2-JIT, beating JIT on t-c** (gate on L1 residency, which binds before the short-overflow at states*stride > 32767; surveyed — only the [01]*1[01]{n} explosion family reaches either, and its table is 2.3x L1 by then). Remaining t-a gap is entirely the second pass. STEP 2 is that emitter change. **STEP 2 BUILT 2026-08-26** (lane srPremul, docs/design/premultiplied_dfa_table.md; abi 6 -> 7, all four sites; `<PREFIX>_DFA_TABLE` = premultiplied/indexed/mixed/none + `-fno-premul-table` bit 15, masked out of rx_info.flags; no rx_info mirror, with the trigger named — measured: pcrec-bench's shim.c has no accessor for abi 6's own scan/prefilter either): **MEASURED 1.794x on the bench's set** (t-a 6.2211 -> 3.5158, t-b 3.2683 -> 1.7994, t-c 3.2825 -> 1.8032 ns/byte; taskset -c 3, median of 5, >= 1 s per trial, load1 0.22-1.01, box idle after the battery's trailer), which puts pcrec **AHEAD of PCRE2-JIT on all three** (set 0.819x, i.e. 1.22x faster, against STEP 1's predicted 1.149x behind; JIT figures carried from STEP 1 and justified by the INDEXED column reproducing its baseline within 0.6%). **STEP 1's 1.276x was a FLOOR set by its hand-patched artifact, not a ceiling set by the mechanism** — its own v1 7.751 vs v1b 6.863 puts 0.89 cycles/byte on accept bookkeeping where the shipped indexed loop pays 0.05, the signature of an accept table still indexed by the un-multiplied state; the shipped form indexes accept by the premultiplied value and runs t-c at 5.91 cycles/byte. **THE SIZE BUDGET WAS SPECIFIED AND THEN DELETED ON A MEASUREMENT**: the bound is the RANGE condition alone (n*ncls <= 65,535), because the premultiplied form still wins across the whole L2 band — 1.107x at 18,432 entries, 1.097x at 36,864, **1.287x on the corpus's own largest machine at 40,010** (a REVERSE table, biggest of the four and the biggest gain, which is the opposite of what a cache-eviction story predicts). **TWO IDEAS MEASURED AND REFUSED**: the `__builtin_expect` LAYOUT HINT on the loop exits is a **REGRESSION** (1.263x slower on the set; hinting the dead exit alone is byte-identical because gcc already ranks it unlikely, and hinting the `state == start` guard stops gcc using it as the back-edge, costing a second taken branch per iteration — 1.38x on t-b's 190,651 skip entries, 1.04x on t-c's one), and a `size_t` state variable is a WASH (1.004x) so `unsigned` stays. Frank's DEAD=0 sentinel was BUILT as an answer-gated patched artifact and is also a wash (0.996x); (a) 65535 is kept on the non-speed balance — 3 bytes and a carve-out-free cell invariant against twelve sites that assume state 0 is the start, a `- 1` in the view read, a row on three tables, and the back-edge losing its free `test`. Per-K-byte exit-check unrolling NOT built (D77): after premultiplying, t-b and t-c are within 1.3% of each other, and that is the gap it would have to beat. IDENTITY: 11 patterns x 91 bench subjects x 3 arms (premultiplied / denied / the pre-change compiler), 122,135 answer lines per arm, 0 differences; run_recursion_identity.sh 15/0 with (A) byte-identical against the unchanged pre-module pin and (B) re-pinned. NEW CHECK tests/codegen/run_premul_table.sh (own `make test` section, not smoke), validated red three ways: table-not-premultiplied 13/19, sentinel-collides 12/5 (and it refuted a sentence of the note's — the range conjunct is not redundant with the tighter size one), state-left-`int` 14/1 on the shape arm ALONE, which is the silent regression no answer check can see. COST: the accept table grows n -> n*ncls, visible in emitted LINES only on the K39 family (869 -> 962 at {0,400}, 1,994 -> 2,762 at {0,4000}) — which is the clearest statement of what [OPT-4] would buy. (STEP 1 measurement lane launched 2026-08-26 ~12:0x; the report's per-subject rows now exist — reporter v4 — and half-answer it: on 1 MB of `a` the skip loop never runs, so the 3.26 ns/byte ≈ 11 cycles/byte IS the transition loop; inbox I-7 item 2 — CONFIRMED in part and REFUTED in part by the above) — THE LOOP'S THIRD OUTLIER, with Frank's NAMED WITH ITS NUMBER, NOT CHARTERED (Frank's branch-prediction question, 2026-08-26 ~13:1x): the start-state exit is the loop's one data-dependent branch (1 per ~5.5 bytes on prose, 190,651/MB on t-b); it costs nothing measurable today because mispredict recovery overlaps the dependency-chain stall (t-b vs t-c 3.272 vs 3.265; still ≤ 1.3 % after premultiply, 2.551 vs 2.519) — the general fix if a subject ever makes it move is checking the exit once per K≈32 bytes (OR-accumulated, unrolled), which loses nothing on the skip side because the skip loop only pays on runs ≥ ~32 bytes (STEP 1 §4); `__builtin_expect` layout hints on the exits ride STEP 2 (layout, not prediction). STEP 3 CANDIDATE, NAMED WITH ITS NUMBERS (Frank, 2026-08-26 ~13:2x: "if the next state is often the same, could it speculate?"): MEASURED on the real orig DFA (instrumented loop, scratch): the transition lands on the SAME state 61.5 % of bytes on t-a (runs of 2/3/6), 63.6 % on t-b (runs 2-9), 100 % on t-c. Hardware will not value-predict a load (no x86 does); the software forms are (a) guess-and-verify — branchy; a state change every ~2.6 bytes on address text makes the verify branch fire at token rate, so its worth is a bet on that branch's predictability; and (b) the EXACT form, the skip loop generalized from state 0 to EVERY self-looping state: scan for the run's end with the state's stay-set (a class-membership test, chain-free, bitmap ~1.15 c/byte or shufti ≥32 B) and transition once at the boundary — bounded gain ≈ same-fraction × (chain − scan) ≈ 0.62 × (7.75 − 1.2) ≈ 4 c/byte on t-a after STEP 2, MINUS one data-dependent exit branch per run (every 2-6 bytes; ~19 c per mispredict), i.e. a net LOSS on non-periodic text unless predicted. BLOCKER: the bench's t-a/t-b are PERIODIC (period 26 / 55 — I-10), so every branch-cost figure so far is flattered; the measurement that decides (b) is the same instrumented artifact on a non-periodic 1 MB subject, after STEP 2 lands. D77: not chartered. SECOND STEP 3 CANDIDATE, NAMED (Frank, 2026-08-26 ~13:3x, "keep the failed case free"): the TWO-BYTE transition table — index by (state, c0, c1), one `load, add` per TWO bytes, the chain halves and there is NO miss path because nothing is guessed; cost = table × ncls, so it is for SMALL machines only (states × ncls² ≤ ~16 K entries stays L1-resident: `\w+@\w+\.\w+` 6×4² = 96, IPv4 20×7² = 980 — most of the corpus by count; orig's 249×18² = 80 K is out of L1 and roughly a wash). Ruled OUT by the same principle: guess-and-verify with a branch (a ~19-cycle mispredict at token rate), packing bits into the loaded entry (any on-chain extract costs a cycle — STEP 1 v2 measured +0.34 c/byte), and speculative-cell prefetch (tables are L1-resident; a self-loop's next cell is in the row just loaded). Gated by STEP 2's size rule; needs a non-periodic subject (I-10). D77: not chartered.
  hypothesis (2026-08-25 ~22:5x): orig / large-subject-throughput at
  1 MB, pcrec-auto 13.39 ms vs PCRE2-JIT 9.12 ms (0.68×, i.e. 1.47×
  slower) while 2.1× FASTER than PCRE2's interpreter — "we should
  consider the possibility that a particular piece is slower because we
  are not currently doing SIMD/hardware-specific optimizations; I suspect
  the large-subject numbers are due to that, but it's hard to pick it
  apart". The ordering interp < pcrec < JIT is CONSISTENT with "pcrec
  wins on the algorithm and loses on the vector unit" (the JIT scans
  first bytes/pairs with SSE2/AVX2; interp and pcrec scan with scalar
  code + libc memchr) — consistent is not attributed. STEP 1, a
  MEASUREMENT lane (the [OPT-1] shape): the DFA's per-byte work is two
  loops — the candidate-start SKIP (scalar 256-entry bitmap walk for
  `byte-class`; glibc's AVX2 memchr for `memchr`) and the TRANSITION loop
  (a table lookup per byte, data-dependent). Attribute the 1 MB cost
  between them: subjects that never leave the skip loop (no candidate
  byte) vs all-candidate subjects vs the bench's mixed ones, on the same
  artifact; the `RX_DFA_PREFILTER` stamp says which skip a subject got;
  CONTROL 1: the same subject through a `memchr`-form artifact vs a
  `byte-class`-form one (SIMD vs scalar scan on identical input);
  CONTROL 2: a SIMD "find first byte in class" (the pshufb shufti of
  studies/simd1) dropped into the skip loop in a scratch copy of the
  artifact, timed. Then: if the loss lives in the skip loop, SIMD IS the
  general fix — [OPT-SIMD] earns its charter through the loop (D79 item
  4); if it lives in the transition loop, the levers are table width /
  two-byte transitions / small-DFA SIMD (studies), and SIMD scanning
  alone will not close it. Needs the bench's per-subject rows (three
  1 MB subjects: which carries the loss) and the artifact size beside
  gcc time (repin-v2 reading items). Queued behind [OPT-1] STEP 3.
- [OPT-4] STATE:started (2026-08-29 ~14:4x, forty-fifth session, on Frank's "go on all three"; lane opt4, opus, worktree worktrees/opt4 — the D86 OPTIMIZATION lane; STEP 0 measure/locate → STEP 1 design note docs/design/prefilter_count_independence.md (manager reads before code) → STEP 2 build under the identity gate → STEP 3 before/after; K41 witness 2 is the pinned exemplar, K39 closes on the measurement) — formerly STATE:not-started — (D84 CROSS-NOTE 2026-08-28: K41's second fuzz-gate witness — 1.25 MB, 92 % hybrid-prefilter jump tables, gcc inside budget — is the PINNED exemplar of this row's K39 mechanism; [ART-SIZE] STEP 2 will refuse or price it under its byte cap, this row is what makes it small.) [OPT-3] STEP 2 NOTE (2026-08-26): the hybrid's inlined prefilter is `emit_unanchored`'s own output through `pcrec_emit_dfa_engine`, so it TOOK the pre-multiplied table with no clause of its own and stamps `RX_DFA_TABLE` like any DFA artifact — this row's scan is the same loop, and a fix here does not have to re-derive the table form. The VM hybrid's inlined DFA PREFILTER scales with a bounded-repeat count (K39, found 2026-08-26 when [ENG-BREP]'s size ceiling went red by 6 lines of slack): `((a)|b){0,4000}c` 1,994 lines vs 869 for {0,400} at the default, 573 at any count with the prefilter off. Candidate general fix: build the candidate-start DFA from a count-INDEPENDENT language (the first-byte class / a count-collapsed pattern); answers unchanged (D46: the prefilter axis is answer-identity-preserving), the identity gates the control. Build when a bench row shows the cost (D77); the size checks now print the auto sizes so the number stays visible.
- [ENG-FORM] STATE:completed (MERGED 2026-08-26 ~20:2x, lane srForm; abi 8; emit_unanchored 459/57/5 → 52/4/2, 14 form booleans → 0, a new representation = one object + one accessor block; objdump equality per loop, timing within spread; journal part 9; battery #3 owed on the combined tree) — THE EMITTER'S FORM AS A VALUE, DECISIONS AS SELECTION (Frank + manager, 2026-08-26 ~14:5x-15:0x, forty-first session; D82). Measured need: emit_dfa.c's two big functions carry the axes — emit_unanchored 459 lines / 57 ifs / nesting 7, emit_attempt 447 / 47 / 5 — with the form held as ~14 loose booleans, every one in a forward/reverse PAIR, and every new axis landing twice in the same function ([OPT-3] STEP 2 added ~20 branch sites). SHAPE, two layers: LAYER 1 (emitter) — `DfaForm` derived ONCE per machine by selecting, for each axis with ≥ 2 real forms (table representation: premultiplied-u16 / indexed-i16 / later u32, two-byte; prefilter kind; view handling; seed), the FIRST APPLICABLE object from an explicit preference list of representation objects `{name, applies(), emit_block()}` with an always-applicable fallback; the stamp = the chosen object's name (one derivation, two readers becomes structural); the deny flag = a filter on the candidate list; interactions (the un-multiply at emit_view_select) = a method on the object that owns the representation; the forward/reverse duplication collapses to one path called twice. LAYER 2 (emitted C) — an OPAQUE state token (`typedef` + `static inline` step / dead / accept / index accessors, one block per machine per form) so the loop SKELETON is emitted ONCE, form-independent, and the VM hybrid's inlined prefilter gets the same block by construction; a new representation is a new object + block, never a new if in the assembly. GUARDS: answer identity over the corpus + the bench's 91 subjects; the hot loop's objdump instruction sequence EQUAL to today's hand-written form (D82 bound 1 — always_inline first remedy); the timing driver (tests/bench/fdriver.c) within spread on t-a/t-b/t-c; the loop text moves ONCE (abi bump, four sites, gate re-pin); run_premul_table.sh §4 reads the typedef line instead of hunting the loop; sabotage anchors on loop lines re-anchored once and proved to detect solo. SCOPE: emit_dfa.c first; then MEASURE emit_vm.c (9,747 lines) the same way before deciding. SEQUENCE: after [OPT-3] STEP 2 merges, BEFORE [OPT-5] and STEP 3 (so those land as accessor-block entries). Opus (engine code); design note before code, D6 panel at close. No framework for its own sake (D75 addendum): a one-site boolean stays a boolean.
- [OPT-A] STATE:not-started — (BENCH O-8 2026-08-29, THE MEASURED NEED: after [OPT-K], stack-frame `\bat ` at 1 MB is still 3.0-6.5× BEHIND pcre2-jit (pcrec 0.38-0.56 ns/byte scalar memchr-at-k*+verify vs the JIT's 0.065-0.087 ns/byte SIMD PAIR scan); the search band is within 2× (1.83×), so this is the 1 MB row's ask — the pair scan is this row's territory; the rarest-byte prior needs [DD-13b]'s `freq` block, the pair scan itself does not. Ranked (i) by the bench for the D86 optimization column, after [OPT-4].) ALGORITHMIC search optimization, and research is part of the work: pcrec is open source and pulling from other open-source engines is the point. Survey before hand-tuning. Leads recorded in D21: rare-byte prefilter selection (ripgrep/Hyperscan choose the RAREST byte by frequency; we choose memchr only at exactly one escape byte and otherwise fall to a bitmap — this attacks our case (d) path directly), memchr2/memchr3 for the 2-3 escape-byte gap, multi-byte literal search (Two-Way/Boyer-Moore/memmem) instead of scan-to-a-byte-then-step, Teddy/SIMD multi-pattern prefilter for the keyword-alternation shape M2.8 targets, reverse-inner and suffix literal selection when the prefix is weak, shift-or/bitap for short patterns, and transition-table compression (we do alphabet compression via byte equivalence classes but no table packing). Record rejections with the reason — "Teddy does not fit because X" is worth as much as adopting it. LEAD ADDED 2026-08-18 (Frank's observation, manager probe same conversation, thirtieth session; RE-OBSERVED by Frank 2026-08-21 on the [M6-READ] VM style exemplar — the readable artifact makes the per-byte spelling visible at a glance, where the original observation took an objdump session; recorded as a measured side benefit of M6-READ, not a new item): LITERAL-RUN COALESCING on the VERIFY path — the memmem lead above is scan-side; its verify-side half is that a maximal literal run (`aabb` in `(aabbc+)`) is matched byte-at-a-time by BOTH engines, measured on the shipped emitter at HEAD 0d97d31-era main: the VM path emits per-byte `pos < n && s[pos]==c` + goto, and gcc -O2 does NOT merge them (objdump: four separate cmpb at consecutive offsets — the per-byte bounds checks and distinct branch targets defeat load-merging; a broken first grep regex initially read this as zero compares, re-measured looser), while the DFA path pays the general table machinery (rx_fcls class lookup + rx_ftr step per byte) on a degenerate linear chain with no choice structure. FIX SHAPE: coalesce maximal literal runs at emission into ONE bounds check (n-pos >= k, the same many-bytes-one-check move MRL makes for length-viability) + constant-size memcmp (gcc inlines to wide compares). SOUND by the run's own structure: no choice points inside a run (a failed run fails its alternative whole), no capture edges inside a run (an edge ends the run), intra-run failure position unobservable (start++ retry advances by one regardless). NOT [ENG-ISL] territory (no choice structure to determinize — pure spelling of an already-linear chain; a literal ISL island would degenerate to exactly this, so ISL subsumes it, but no island machinery is needed). FAVORABLE ASYMMETRY vs the [OPT-ALTCLS] stage-3 measured-no: the FIRST-set guard optimized the REJECT path, which the hybrid prefilter absorbs; literal runs sit on the ACCEPT path every successful match pays, prefilter or not. D18 unchanged: lands only with a bench-measured win under the compare.sh instruments. LEAD WIDENED same conversation (Frank: "consider multiple potential implementations... at a class of N there is some N where if-a-or-if-b wins"): BYTE-TEST SPELLING MENU — the VM emitter's per-byte-predicate menu today has exactly THREE rungs, measured on emitted artifacts: N=1 → `s[pos]==c`; ONE contiguous range (incl. 2-member `[bc]`) → the subtract/unsigned-compare idiom `(unsigned)(c-lo)<=span`; EVERYTHING ELSE → the 256-bit bitmap `rx_k1[c>>3]>>(c&7)&1`, a per-byte MEMORY LOAD — and "everything else" includes `[a-zA-Z]` (measured: two ranges → bitmap), i.e. the everyday multi-range unions (\w, hex, alnum) all pay the table. MISSING RUNGS, cheap→general: k-range unions as k range-checks (k=2,3); the 0x20-fold collapse (`[a-zA-Z]` → ONE folded range-check, also the (?i) pair shape); a 64-bit IMMEDIATE-mask test for scattered sets whose span<64 (`(mask>>(c-lo))&1`, no memory touch); OR-chains for tiny scattered N. The crossover N/shape is a MEASUREMENT question (branchless-vs-branchy matters as much as op count; and the winning spelling depends on subject BYTE DISTRIBUTION — an [ENG-PGO] hook: exemplar-informed spelling selection). INTERACTION WITH THE EMIT MODEL (Frank's recall, confirmed against the record): [DD-5] is the switch-based no-computed-goto emitter row, and the recorded evidence is engine_m4.md §8.4 (computed goto is the WRONG lever on case (f)) plus the address-taken-label compile-time superlinearity numbers in decisions.md (2004 labels/0 address-taken 2.70s vs 400 address-taken 11.21s; 8000 grinds cc1 100+ min). Address-taken labels also pin RUN-time codegen (frozen block layout/merging — plausibly the same mechanism behind this lead's measured cmpb non-merge), and gcc's own switch lowering already implements exactly this spelling menu (jump table / bit-test / compare chain by its internal cost model), which a switch-shaped emit model would get for free. TWO COUNTERWEIGHTS, both on the record: only backtrack RESUME points take `&&label` (plain goto targets don't pin — the burden is proportional to resume points, which [OPT-ALTCLS] stage 1 already reduces, 2→0 on its exemplar: rung downgrades un-pin gcc as a second-order benefit); and the computed-goto body's UNOUTLINEABILITY is what structurally protected the VM from K24's .part.0 split — any emit-model change re-opens that exposure and must carry K24's regression evidence with it
- [ENG-ABS] STATE:started (SECOND MECHANISM BATTERY-PROVEN 2026-08-29 ~05:4x on 808740c (code 517be95 = merge dfd112b): strict clean, anchors 186/197 resolve, `make -k -j12 test` 1,711 checks / 0 failed, 27/27 sections (the only reds: counterk's load cell 29 cases + the resource K7 cells INCONCLUSIVE under the load guard — all cleared solo: resource 20/0, counterk 24/0, corpus cell 1,634/0), `make san` rc 0 / 0 report lines both axes, mech 186 rows unexpected 0 / undetected 6 (S150-S153 S160 S178, expected) / unreached 0 / anomalies 0; the battery script's verdict line died on its own `set -u` bug (GUARD unbound — fixed in battery_v3.sh), verdict computed by hand: GREEN. [OPT-2] CLOSES into this row (its measured lever is now built and measured at 1.031×/0.482×). The FIRST mechanism (`^` absorption into ENG_UNANCH) stays gated on [BENCH-1]; this row stays STARTED for it. Bench inbox I-16 sent with the abi-10 pin. SECOND MECHANISM MERGED dfd112b 2026-08-29 ~02:2x — lane/engabs 2e2ce3f, 33 commits; r41 paneled (docs/dev/reviews/2026-08-28-r41-engabs-close.md): NO MISCOMPILE over 148,917 cells, every number reproduced (matching 1.031×/1.036× vs the VM, short emails 0.482×, failing 1 MB probe 363,305×), abi 10, `-fno-anchored-dfa` bit 17, registry 64, `RX_DFA_MATCH` unwrapped/search-filter + `rx_info.match_form`; pre-merge round: the optional machine's OWN ceiling PCREC_ANCHORED_MAX_STATES = 4,096 (S1: +46 % compiler CPU on the resource shapes without it; seven named fallback members — four resource shapes, three counterk 4000-count patterns under --no-captures), the captures-on differential arm (S4, 976 cells, S190 detected by the run), §8 corrected (the anchored machine is LARGER on 26/269, up to 2×). UNION BATTERY PENDING on dfd112b; [OPT-2] closes into this row at the battery; the FIRST mechanism (`^` absorption) stays gated on [BENCH-1]. OPENED 2026-08-28 ~22:3x, forty-fourth session, on Frank's "Go 1&2" — the SECOND MECHANISM only: anchored match-here via the UNWRAPPED forward DFA, lane engabs (opus, worktree lane/engabs); [OPT-2] closes into it. The FIRST mechanism, `^`-absorption into ENG_UNANCH, stays gated on [BENCH-1]'s `^`-on-some-branches case and is NOT opened) — formerly STATE:not-started — ENG_UNANCH absorbs `^` (the DD-7
  absorption half, re-homed here 2026-08-14, D42.7): D8 left `^` on
  ENG_ATTEMPT because the reverse machine has no position-dependent BOT
  variant; the recorded slow shape is `^`-on-only-SOME-branches
  (`(^a|b)c`). GATE (D12/D15 discipline): [BENCH-1] must first add a
  `^`-on-some-branches case and measure an actual loss — no bench case
  exercises `^` today, and unmeasured engine work is not scheduled.
  After M4, the change lands in the selection pass
  (src/opt/select_engine.c), not the pipeline driver. GATE MET 2026-08-28 for the SECOND mechanism: [OPT-2] STEP 2 (docs/dev/opt2_anchored_match_measurement.md) measured the reverse pass at ~50 % of the DFA's cost on every matching subject of the bench's compliance set — 2.077× behind the VM with it, 1.046× (parity) without, 0.571× on short valid emails; the unwrapped-forward match-here entry below is the named lever, its number to beat stated there. SECOND MECHANISM
  RECORDED (Frank + manager design thread, 2026-08-18, thirty-second
  session): ANCHORED MATCH-HERE VIA THE UNWRAPPED FORWARD DFA. Today a
  DFA artifact's `<prefix>_match` runs the ordinary unanchored search
  and filters on `caps[0][0] != ctx->pos` (spec §3.2 documents the
  mechanism as non-contractual) — correct, but a FAILING match-here can
  skim the remainder of the subject hunting a later match it will then
  discard, where the VM's match_impl fails at the first divergent byte.
  A runtime "anchored" flag on the existing tables CANNOT fix this —
  the start-anywhere self-loop is baked into the subset construction
  and the merged states erase which start a thread came from
  (DD-7/engine_m4.md §7.3: the wrap is structural). The generation-time
  form works and is CHEAPER than assumed: emit the pattern's UNWRAPPED
  forward DFA and run it from ctx->pos — anchored match needs NO
  REVERSE PASS (the start is known), so the cost is ONE extra table,
  typically smaller than either search table, derived from the same IR
  (same trust model as the existing forward/reverse pair). Failing
  match-here becomes first-divergent-byte on both engines. Partial
  zero-table fallback, recorded with its hazard: for MRL-bounded
  patterns match could clamp the search to pos+MRL, but clamping n
  changes end-of-subject semantics ($-bearing patterns), so it is a
  fallback only. GATE UNCHANGED: measure the failing-match skim on
  realistic subjects first; unmeasured engine work is not scheduled,
  and this does not queue ahead of M6
- [OPT-SIMD] STATE:not-started — SIMD EMISSION for candidate scanning
  (Frank, 2026-08-14 nineteenth session, D41.6): AOT-composed SIMD
  prefilters emitted directly into generated matchers — multi-literal
  substring scanning, pshufb nibble-table class tests, 0x20-fold
  case-insensitive comparison — operating 32–64 bytes per iteration with
  little or no conditional branching. Frank's motivating example:
  `((?i)abc|dev|bet|[a-f]{5})` built as a composed SIMD scanner, which
  only an ahead-of-time compiler can specialize this way. Framing
  recorded at D41: this EXTENDS the existing memchr/skip-loop lever
  (libc memchr is already SIMD; this emits the multi-byte/class/
  multi-literal generalizations directly), it is prefilter/DFA-engine
  territory orthogonal to M4's captures work, and it overlaps OPT-A's
  Teddy/shift-or leads — the survey there feeds this row; adoption
  measured under BENCH-1's instruments. Portability is part of the
  design: gcc vector extensions vs target-gated intrinsics vs scalar
  fallback is a generation axis that must earn itself (D18), and the
  no-libc/freestanding line must keep a scalar path. Interface
  consequence already ruled (D41.5): one-shot search stays the
  primitive; block-context preservation across matches belongs to
  emitted loops now and the designated `<prefix>_iter` cursor entry
  later — this row does not reopen that
- [OPT-B] STATE:not-started — PROFILED code-level optimization, only after OPT-A. D13's correction says throughput here is dominated by transition PREDICTABILITY, so target branch behaviour and memory layout rather than instruction count. Every number under D12's rules and the R3.10 load guard
- [OPT-C] STATE:not-started — COMPILE-TIME optimization, last. Must include what gcc does with our output, not only what pcrec does: after M2.8, gcc is the LARGER half (0.79 s vs 1.36 s at 3600 words) and M2.9's budgets measure only pcrec's
- [ART-SIZE] STATE:started (STEP 2 BATTERY-PROVEN 2026-08-29 13:37 on 36d5963 (code) — strict clean, anchors 189/200 resolve, `make -k -j12 test` checks 0 failed / 27/27 sections (the counterk load cell red, solo 1,634/0; resource 26/0, counterk 24/0), `make san` rc 0 / 0 report lines both axes, mech 189 rows / unexpected 0 / undetected 6 (S150-S153 S160 S178, expected) / unreached 0 / anomalies 0; the battery script's verdict line reads RED only for the top-level `make test` exit line the load cell produces (a v4 excludes it when the solo stages clear) — verdict by hand GREEN. I-17 sent (pin 36d5963, the consolidated pcrecdev2 worklist). STEP 2 is DONE; the row stays STARTED as the record's home until [ART-SIZE] is archived with STEP 1. BATTERY on 6e37a4c RED 2026-08-29 ~09:4x — `make san`: LeakSanitizer 2 × 256 B on the R1 witness only (tests/size/size_term.rxt:34/35): r42's S3 fix armed vmsb's early abort, whose longjmp orphaned two function-local StrBufs live inside the VM emission; FIXED 36d5963 (Job-owned `scr_test`/`scr_desc`, freed by job_cleanup on every path; san axis on that file 21/0, strict clean, test-codegen 5/5); UNION BATTERY RELAUNCHED on 36d5963 at 10:02. STEP 2 MERGED 6e37a4c 2026-08-29 ~09:1x — lane/artsize3 cf13497, 58 commits; r42 close panel (docs/dev/reviews/2026-08-29-r42-artsize-close.md): identity and answers HOLD under measurement (shipped artifact byte-identical to the explicit-K artifact 7/7; 67,677 cells identical; capacity fields never lowered; 2,002-emit acceptance sweep — zero corpus changes); pre-merge round closed S1 (overflow) / S2 (rescue direction) / S3 (abort on the emission buffer) / S5 / S6 (the bar pinned to 0.73 % by two witnesses; the continuum real on the argmin-rung quantity) / S8, C1 (FILEPIN → b3cf716, 0 differing on four axes) / C2, M1 (quiet size log) / M2 / M5 / M6; the interior census is 159 (147 K=2, 11 K=3, 1 K=4), not the 150-pattern sample's 18; abi 11, bit 18, registry 67, `--list-axes` 47 rows / 19 axes; seven acceptance changes in the tree (three resource shapes, K41 witness 2, the K22 tower — all refused by the total cap, all pinned with `--max-emit-bytes` re-acceptance cells), bench survey 54/54 accept. UNION BATTERY PENDING on 6e37a4c; I-17 follows. STEP 2 DESIGN APPROVED FOR CODE 2026-08-29 ~00:1x at lane/artsize3 e72b57d after three revision passes — r40 close section; code phase opens, sequenced behind [ENG-ABS]'s merge for abi/bit/registry sites: abi 10→11, bit 18, registry 64→65. r40 PANELED 2026-08-28 ~23:0x — REVISION REQUIRED, docs/dev/reviews/2026-08-28-r40-artsize-term.md: the instrument was blind to the hybrid's jump tables (F1), no pre-emission node count exists (S1), K is caller-observable on the give-up surface (S2), the cap must re-run the ladder (S5); FRANK RULED Q2/Q4 = D84: cap overridable upward, and shipped BYTES are their own concern with a second, byte cap — unpredictability the worse half. STEP 2 OPENED 2026-08-28 ~22:3x, forty-fourth session, on Frank's "Go 1&2" — lane artsize3 (opus, worktree lane/artsize3): the [OPT-K] shape, design note `docs/design/artifact_size_term.md` FIRST (the counter rung choosing K from a size model, nesting depth the trigger, `--unroll=K` the override; a hard emitted-size cap with a refusal as the last resort; the three emitter levers PRICED against the corpus, not just the witness; stamps; identity gate as the control), then the D6 panel (r40), then code. STEP 1 CLOSED 2026-08-28 ~20:5x — census 50a3910 + the quiet-box throughput columns 98d0995 (lane artsize2; load1 0.13-1.2). CAVEAT THE RE-RUN TAUGHT: the tension curves' SPEED axis is micro-scale (2-13 µs subjects, 30 iters × 5 trials) and did not separate ±50 % effects between the loaded and the quiet pass — `-fno-premul-table` read 20-34 % slower loaded and direction-INCONSISTENT quiet (2 of 5 patterns "faster" without the table, which the mechanism cannot explain), and a stated size no-op cell swung from cheapest to dearest; the SIZE findings (load-independent) stand in full; the speed side of every lever is the bench's to measure on real 1 MB subjects ([OPT-3] STEP 2 already measured the premultiplied table at 1.79× there; I-15 ask (c)). What the quiet run DID settle: `--unroll=1` is a real WIN on the N=8 nested-repeat outlier (default 13.4 µs vs 5.9 µs), not merely free; `--engine=vm`'s failing-path cost 173,580× (was 359,000× loaded; the denominator is a 0.1-0.2 µs default); witness/-fno-counter has no throughput cell — its ~4.1 MB source cannot link within 180 s regardless of load. THE ANSWER: over 2,772 patterns (2,758 corpus + 14 bench) the shipped `.o` at -O2 is SMALL — median 6,760 B, p99 14,364 B; gcc max 6.995 s CPU (one pattern), everything else < 0.5 s; 0 timeouts, 0 budget kills. The 2 MB witness is NOT in the population: it is ~3× the corpus's own largest (`((a)|ab){4000}c`: 675,555 B source / 202,912 B .o vs the witness's 2,015,594 / 503,344 — self-contained form; the split .c alone undercounts by its .h sidecar, which is what both the plan row's old 2,004,778 and the manager's count were) and it is the SAME MECHANISM as every top-20 outlier: a bounded/exact repeat over a multi-branch alternation forcing the FRAMES-BOUNDED counter rung, body replicated per --unroll=K chunk. Source tracks .o at r = 0.99 once comments are excluded (.o/source ≈ 17 %, p10-p90 0.153-0.194); [M6-READ] prose is 42 % of aggregate SOURCE bytes but rides along, does not drive .o — a size term must price program+tables, not source. THREE LEVERS with different trades (§8): `--unroll=1` free on NESTED-repeat patterns (witness 17× smaller / 54× faster gcc / no speed loss on its subjects; corpus nested outliers 75-79 % smaller, 12× faster gcc) but ~1-3 % on single-level large counts; `-fno-premul-table` the known [OPT-3] trade (~22-25 % smaller, bounded speed cost); `--engine=vm` = the tension itself measured — dropping the hybrid prefilter shrinks .o to 4-9 % at up to a PROVISIONAL 359,000× failing-path cost, because the prefilter IS the size and the speed. Manager's line-kind attribution of the witness (span loops 40 %, label boilerplate 13.5 %, prune guards 8 %, class tests 6 %) is in §6/§7 as the three emitter levers to price in STEP 2. STEP 2 design input: the cap must bind on a measured tail nobody has written yet; the census script re-runs the census) — formerly (STEP 1 census, lane artsize opened 2026-08-28 ~14:4x, sonnet, measurement only) — ARTIFACT SIZE AS A FIRST-CLASS COST, AND THE SIZE-VS-PERFORMANCE TENSION (Frank, 2026-08-28: "I'm concerned about the 2 MB VM artifact. If our compiled artifacts are that big no one will want to use them. It deserves an investigation as well as a size vs performance tension that kicks in at some size"). THE WITNESS: the fuzz gate's seed-1 pattern `1{1,}b1{0}1{2,3}?|(c0{1}.)|((\n.*|.{2}|(?:a{2,3}|0{0,30}cc|c{0,3}bc{2,3}){1,}){5,10}.{2,}|[a-c-e]{1,}?|a$b){28,30}[a-z0-9]{28,30}(\n[^abc]{28,30}?){1,}` → a 2,004,778-byte VM artifact (RX_VM_RUNGS 0x17), gcc -O2 -c 52.9 s / 540 MB (over D45's budget), byte-identical under `--engine=vm`; hidden until [SEL-1] because its auto-prefilter DFA overflowed and refused the compile. STEP 1 — THE CENSUS (D77, before any design): over every corpus pattern (tests/**/*.rxt, --features all, default auto) and every pcrec-bench pattern (read-only), record per artifact: source bytes, `.o` bytes at -O2 (the number a user ships), gcc wall/CPU, engine + rungs + prefilter stamps, and a BYTE ATTRIBUTION by section — the emitted program proper vs tables (DFA transition/accept/class tables, premultiplied) vs the [M6-READ] prose (comments, listings) vs the accessor/scaffolding blocks vs `main`; derive the distribution (median, p90, p99, max), the outliers with their mechanism (counter-rung body replication under nested bounded repeats is the suspect: `{28,30}` × `{5,10}` × `{1,}`; `--unroll=K`'s contribution), and for each outlier the SAME pattern under `--unroll=1`, `-fno-counter`, `-fno-splice-calls` (size, gcc time, AND throughput on a representative subject — the tension has to be measured on both axes to be designed). Deliver docs/dev/artifact_size_census.md (opt3's report shape) + a one-line CLAUDE.md entry. STEP 2 (design, after the census, gated on its numbers): the tension as a GENERAL selection term, not a special case — a size cost in the emitter's candidate selection (the rung ladder's replication choices, unroll K, table forms) that binds past a threshold the census justifies; a hard emitted-size cap with a refusal ("pattern too large for the VM emitter", limits.h + limits.md) as the last resort so a fallback can never ship what gcc cannot compile in D45's budget; stamps for what the size term chose; identity gate as the control. Related: the `.o` size the bench already reports (+30 KB DFA at abi 7/8, O-7 item 2), [OPT-D] (no-impact dedupe — the census tells whether it matters), [OPT-C] (what gcc does with our output), the K-row sel1b files for the fuzz witness. Ask (1) of the same ruling rides the bench inbox I-15: for every bench pattern where auto's DFA fallback tripped, pcrec-VM vs pcre2-jit timing (level-context: 1.55 ms/set vs 115 µs at O-7).
- [OPT-D] STATE:not-started — NO-IMPACT SPACE SAVINGS in the emitted artifact (Frank, 2026-08-28: "no impact space savings. Eg if the class bitmaps are repeated (ex forward and back dfa) then keep one copy"). Deduplicate emitted read-only data that is byte-identical across the artifact's machines — the byte-equivalence-class map / class bitmaps shared by a forward DFA and its backward (reverse-scan) twin, and any other table the emitter writes once per machine when the contents coincide — so one copy is emitted and every machine's accessor block points at it. SCOPE: artifact SIZE only; answers, stamps and the match API unchanged (answer-identity gate + `make test-axes` are the controls); runtime cost must be ZERO, proven the [ENG-FORM] way (objdump of the hot loops + timing within spread — D82), since a shared table is the same load either way. The [ENG-FORM] representation objects are the natural site: dedup is a SELECTION over the candidate lists (a table candidate that resolves to an already-emitted twin), not a special case in a machine's emit path (memory `pcrec-general-mechanisms-not-special-cases`). Measure first (D77): a census of emitted tables per artifact over the corpus — how many bytes are duplicates, on which patterns — names the win before the code; a change to the emitted scaffolding is an abi bump with its four sites (D76). Low priority; queued behind the bench-gated rows

## Thread-safety (D19) — usable FROM threads; guards, not prose

Audited 2026-08-09: generated code and the library are BOTH thread-safe today
(every emitted static is const, no file-scope mutable state anywhere in src/,
Ctx and its jmp_buf are locals of pcrec_compile). These steps exist to keep
that true, because it is invisible to every current test and a one-line change
can destroy it.

- [TS-4] STATE:not-started — DD-10 is a thread-safety item, not just robustness (D19): musl's default THREAD stack is 128 KB against the main thread's 8 MB, and `compile_ast` plus `clo_visit`'s t1 edge are still bounded only by pattern structure (~192 KB for 400 nested branch points). Give `compile_ast` a stated budget the way trie_build has one, and add a `tests/cli` stack case that binds it — case 8 covers branch COUNT, nothing covers nesting DEPTH

## Process mechanization (session 2026-08-09) — turn recurring lessons into tools

Four consecutive checkpoints have found the same failure class: not compiler
defects, but measurement claims about safeguards that were stale, contaminated,
or never made. Writing the lesson down demonstrably does not install it (this
session restated a load-contamination rule and violated it in the same
document). Mechanize instead.

- [SR-11] archived to plan_completed.md (completed 2026-08-22 — the table contract implemented: tests/lib/table.sh + converted consumers + both checks; docs/spec/table_contract.md is the spec)
- [TT-3] archived to plan_completed.md (completed 2026-08-22 — measured NO for make test / qualified YES for mech; CCACHE=1 wiring merged opt-in; docs/testing.md "Compile caching" is the record)
- [MECH-3] STATE:not-started — a measurement wrapper that refuses to emit a number without provenance: interleaved A/B, N trials, load before AND after (R3.10), min/median/max spread, and a stamped record. Every performance overclaim this project has made — the 27%-recorded-as-+40%, this session's 1.5-4.1% deltas taken at load 4.5-9.7 — would have been blocked at the point of measurement rather than caught in review. Frank's precedent: a claude-safe grep that refuses `| tail` and reports what it actually looked at

## PCRE2 compliance tracking

- [DOC-DRV] archived to plan_completed.md (completed 2026-08-22 — the compliance page is annotated derivation: docs/pcre2_compliance_annotations.txt + the extended compliance_section.py checks; the compliance-refresh skill carries the process)
- [PC-2] STATE:not-started — periodic re-survey: re-read pcre2syntax.html,
  re-run tests/reject, move landed modules from REJECTED to OK, re-stamp the
  date. Do this whenever a module lands and at each checkpoint review

## Small-debt shelf (light-session filler; pointers, not new rows)

Pointers, not queue positions — states live on the real rows cited.

- K9 — the public API takes no pattern length, so a pattern containing NUL
  compiles as its prefix; fix before any V-tier consumer exists
  (docs/dev/known_issues.md).
- TS-4 / DD-10 — stack budgets for `compile_ast` and `clo_visit`'s t1 edge.
- DD-8 — `--emit-ir` / `--emit-dot`, useful during M4 bring-up.
- SR-5 — guard the fast-path lookup-count claim with an instrumented build.
- MECH-3 — schedule before [OPT-A] opens.
- module-swap / row-deletion guard — owed, unruled.
- PC-4 missing shapes — caseless-negated, `\N{n,m}`, MODIFIER, zero-tail
  `(?P`.
- PC-2 — re-survey.
