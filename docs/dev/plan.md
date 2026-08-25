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

- [M6.0] STATE:started — milestone (EXPANDED 2026-08-18, thirty-third session, on Frank's standing ruling). Scope per the ruled list: assertions (\b \B, \A \z, (?m) multiline, \G, \K — module `assertions`), lookaround, backrefs, atomic groups + possessive-quantifier SPELLINGS (module `atomic-groups`; the possessify OPTIMIZATION already exists internally — this is the surface syntax, which is SEMANTICS, not an optimization), named groups (module `named-groups`). PREMISES RE-VERIFIED AT EXPANSION (constraint (a); probe on HEAD b95fbe6, 2026-08-18): \b \B \A \z \Z (?m) \G \K all refuse with module `assertions`; (?= (?! (?<= (?<! with `lookaround`; \1 \k (?P= with `backrefs`; (?> and *+ ++ ?+ with `atomic-groups`; (?<n> (?'n' (?P<n> declarations with `named-groups`; (?( with `conditionals`, (?R with `recursion`, (?| with `branch-reset` — those three are NOT in Frank's ruled M6 list, their refusals stand; \d, [[:alpha:]], (?i), (?s), and mid-pattern $ all COMPILE (the 2026-08-16 row correction holds). ABI groundwork verified shipped: `rx_info.groups` (`const rx_group_entry *`, "NULL until named-groups"), `nnames`, and the `rx_group_entry` ABI type all exist in the frozen M4 ABI — named-groups POPULATES an anticipated slot, no ABI change; the groups SORT KEY is the one deliberately-unfixed spec point (match_api.md §6) and is fixed by [M6.3]. INHERITED OBLIGATIONS travelling on substeps: D47.5 possessification-gate test rides whichever wave lands (?m) — see [M6.2]; D58 seam routing — every encoding-sensitive residue (lookbehind back-step, \G advance, caseless backref compare, word-character classification for \b) routes through src/gen/enc/ residual entries FROM BIRTH, never raw byte arithmetic in shared emitter code. MODULE PROGRESS: named-groups DONE ([M6.3], 2026-08-18); assertions DONE ([M6.2], 2026-08-21, 8/8 constructs); atomic-groups DONE ([M6.4], 2026-08-22, (?>...) + *+ ++ ?+ {n,m}+; SR-8 built); lookaround DONE ([M6.6], 2026-08-24, 18 spellings + fixed-per-branch lookbehind); backrefs DONE ([M6.5], 2026-08-22, \1..\N + \g + \k + (?P=n) + DUPNAMES (?J); the seam's second entry); remaining: lookaround [M6.6] — design APPROVED and all asks RULED 2026-08-23; [M6.6.2] implementation CLEARED for the next session. POST-MODULE QUEUE (re-homed here from the [M6.2] row at its close; groupings and status as of 2026-08-21): TRANCHE A IN FLIGHT — (3) seven drifted sabotage anchors S08/S09/S21/S22/S26/S39/S65 (lane/sabanchors: re-anchored, mech validation pending), (5) wordb.rxt shard-split + PROCS note (lane/wordbshard: split done, suite validation pending), (7) heavy differentials on the sanitizer axes — DONE (kreset+gstart under BOTH axes, all four clean on first-ever sanitizer exposure, in the union chain b8cb848); the post-merge full-matrix mech on main also DONE (85/0/0 at 115fbc6), closing (3)+(5)'s verification of record. RE-BASED BY D66 (Frank, 2026-08-21) — (1) DD-7's reverse BOT variant (D63) and (2) D63's second instance (first-byte-at-offset-0, the 83x partial-anchor gap) now DEPEND ON the [DD-11] core-reduction work: optimize the CORE lookbehind-anchor form once (candidate-start derivation from a leading fixed lookbehind + generalized reverse boundary evaluation) so every desugared anchor benefits, rather than implementing against ^'s special case; sequenced behind [M6.6] lookaround + the DD-11 design — see D66 for the two answered questions and the accepted tradeoffs; (4) the registry BUILT-STATUS field — DONE (D65 ratified, implemented, merged 30f5e4b; the two missed FORMAT consumers fixed by the tail lane b7c230d with the complete format-consumer survey in the memo's Correction section; validated by the union battery b8cb848). ARMED, NO WORK — (6) SR-8's second-construct trigger
- [M6.1] archived to plan_completed.md (completed 2026-08-18, thirty-third session — the R30 panel + focused re-checks + N1 verification closed it; design docs/design/assertions_design.md merged at 0beac07; review docs/dev/reviews/2026-08-18-r30-assertions-design.md; Frank rulings Q1/Q3/Q8 carried on [M6.2])
- [M6.2] archived to plan_completed.md (completed 2026-08-21, thirty-fifth session — module `assertions` closed: five waves + repair slice + D27 blinded corpus, all close-validated; the post-module queue re-homed to [M6.0])
- [M6.3] archived to plan_completed.md (completed 2026-08-18, thirty-third session — see that file; D59, merge commits on main)
- [SPEC-M] archived to plan_completed.md (completed 2026-08-21 — spec_mod0 green, (?m) named exceptions with guards; expiry DD-11)
- [M6.4] archived to plan_completed.md (completed 2026-08-22, thirty-sixth session — module `atomic-groups` SHIPPED: design R31 (21e173e), implementation 69f3b93 + fix 8e4af41 (the D27 corpus found a tier-1 miscompile — the MRL follow-bound crossing the cut — fixed at its root), D27 corpus c324091 134/134; union battery all five stages green on the fixed state (test 21,557/0); mech 99 rows 0 undetected, S88-S101 all DETECTED; gate 13/13 at load 0.39, weakest margin 1.43x (34ede2c); SR-8 built (D67); K29 fixed; U9 held LOUD in tests/known_fail pending Frank's ruling)
- [M6.5] archived to plan_completed.md (completed 2026-08-22, thirty-sixth session — module `backrefs` SHIPPED: design R32 (ca9beef), implementation 3aa446f (lane fb97bab: test 23,798/0, its own ubsan+asan green, identity gate 1501/1502/1501 on three axes), D27 corpus 672a2f4 207/207 with ZERO implementation divergences; union battery all five stages green on 3aa446f; mech 118 rows / 0 anomalies / 2 undetected at 5edba64 → S107 corpus gap closed + DETECTED, S108 RETIRED as measured-unobservable → 117 scored rows, 0 outstanding; gate 13/13 at load 0.36, weakest margin 1.43x (41e541a); registry 106/52/48/6 asserted; DUPNAMES (?J) shipped with first-of-run-by-number-that-is-SET resolution and the tiebreak as correctness; the [M5-SEAM]'s second residual entry pair; S102-S120; residuals: wire S103 to `brefidentity` (registered, zero rows); a MULTI-HUNK sabotage mechanism — DONE post-close 2026-08-23 (the matrix's optional second site; S108 RE-INSTATED two-site and DETECTED; tripwire 118 rows / 119 anchor sites); a sabotage row for possessify.c's Glushkov `case A_BREF` arm (load-bearing, no row); FOLLOW-UPS from Frank's read of the `(abc)\1` artifact (2026-08-22 23:0x, measure first per D18): (a) `engine_callable` seam entries should be `static` — rx_bref_match inherited next_pos's external linkage without an external consumer; (b) a DEFINITELY-SET analysis (dominance through A_CAT, not through A_ALT/A_REP bodies) to elide the UNSET test where the referenced group always publishes before the reference; (c) a memcmp fast path on the success path with the failed-prefix walk only on mismatch — the charge's prefix-length contract keeps; (d) STATIC GROUP WIDTH — a fixed-width referenced group (`(abc)`) makes the compare a constant-length compare with one hoisted bounds check, and under the definitely-set analysis pcrec_minw(A_BREF) may soundly become the group's minw (exact for fixed width) instead of the design's deliberate 0, feeding the MRL prune; the full form is the chartered finite-language expansion (`(abc)\1` → `abcabc`), whose only customer is --no-captures; (e) THE WORK UNIT is bytes examined, an effort PROXY calibrated to the VM's per-byte loop — block compares (backref memcmp, memchr prefilter, cursor scans) over-charge relative to effort, the conservative direction for a DD-2 robustness bound; if the unit is ever meant as effort, charge ceil(n/k) for block operations — a ruling for the unit, not a backrefs one-off; (f) THE SINGLETON-LANGUAGE REWRITE, in Frank's core-reduction form (23:3x): NOT a backrefs one-off — under the predicate |L(G)| = 1 under G's own flags, definitely-set, nrefs == 1, `\1` and `\g<1>` mean the same thing (PCRE2 REVERTS a subroutine call's captures, so inlining a non-recursive call IS the non-capturing copy `(?:G')` the rewrite needs), so the rewrite is a one-line node swap A_BREF → subroutine-call in the core-reduction layer (DD-11's principle, D66's precedent) and the `recursion` module's INLINER does the rest — one path for inlining group code, no separate emitter code; lands when that inliner lands; payoff on the DEFAULT build is the hybrid prefilter coming back ON (no A_BREF in the tree; today fit.prefilter = false for every backref pattern); (b) shares its definitely-set analysis with this predicate — one pass; (d) is the only genuinely backref-local item and is dropped unless a measurement asks; none blocks the close)
- [M6.6] STATE:completed (MODULE `lookaround` SHIPS 2026-08-24 ~09:4x — 18 spellings built (6 primaries + 12 aliases), 3 refusals each a PCRE2 fact, lookbehind fixed-per-top-level-branch with variable refused, VM-only per the ruled design, the D70 union + the family field + the substitution driver + K30 landed en route; every wave byte-identity-gated, full matrix 137/0/0 at close, the blinded corpus 1,819/0. DESIGN GATE OPENED 2026-08-23 13:2x on Frank's "how about some design for the next lane" while the [TT-6] battery ran; implementation NOT cleared until the design is panel-approved and Frank says go) — module `lookaround`: last on purpose (hardest; likely its own design gate before code). Lookbehind's back-step is D58-named residue — a seam entry, never raw `pos - k` byte arithmetic in shared emitter code. Substeps:
  - [M6.6.1] STATE:completed (APPROVED 2026-08-23 at 46868d6, merged 9fced73: docs/design/lookaround_design.md 2,756 lines + lookaround_measurements/ (10 probes, archived outputs); R33 three rounds — 25 findings (5 HIGH, incl. the fmin/fdyn follow-scoping miscompile class and the accept-pruned Σ*·L sizing), 12 verifier findings against the revisions (3 blocking, all text), 0 outstanding; reviews/2026-08-23-r33-lookaround-design.md is the record; 18 spellings ship / 3 refuse; lookbehind fixed-per-branch ships, variable refuses; VM-only semantics, DFA deferred to [ENG-LOOK]; §14's five ASKs await Frank; [M6.6.2] NOT cleared unprompted) — formerly STATE:started — DESIGN GATE (lane/ladesign, opus). AMENDED 13:5x (Frank): charter item (iv)'s DFA-eligible subset is RE-SCOPED — NO one-character fold; engine selection is VM for semantics now, and the DFA answer is [ENG-LOOK]'s product construction (see that row); the design states the prefilter-soundness argument and the VM body as a self-contained sub-program (DD-14's call target), and hands [ENG-LOOK] the sizing inputs (component automata sizes for the expanded assertion corpus and the lookaround population). docs/design/lookaround_design.md answering PER CONSTRUCT, every claim marked MEASURED (a probe against libpcre2 10.46 via the house ctypes oracle, or a pcrec artifact on HEAD) or ASSERTED: (i) THE CONSTRUCT TABLE — (?=X) (?!X) (?<=X) (?<!X); PCRE2's alpha spellings (*pla:X) (*positive_lookahead:X) (*nla:) (*negative_lookahead:) (*plb:) (*positive_lookbehind:) (*nlb:) (*negative_lookbehind:) and the NON-ATOMIC forms (?*X) (?<*X) (*napla:) (*naplb:) — which ship, which refuse with "requires module" (D26 tier: a construct's EXISTENCE and owner are exact, its diagnostic wording is not); the LOOKBEHIND LENGTH RULE as PCRE2 10.46 actually implements it (fixed-length alternatives of DIFFERENT lengths are legal; variable-length lookbehind bounded by max_varlookbehind since 10.43 — measure what 10.46 accepts and rule the pcrec subset: fixed-per-alternative ships, variable-length refuses or ships, with the reason); quantified lookaround ((?=a)* and friends — PCRE2's special handling); nested lookaround; lookaround containing backrefs, atomic groups, \K (PCRE2 ≥10.38 REFUSES \K inside lookaround by default — measure, rule), captures inside POSITIVE lookaround (retained after success) vs NEGATIVE (discarded), captures inside lookbehind; the degenerate (?=) (?!) forms; lookaround at pattern start (prefilter interplay) and end; (ii) THE VM LOWERING — lookahead as an ATOMIC sub-match: save pos + frame depth + capture snapshot, run the body, on success CUT to the saved depth (RX_CUT substrate, vm_cut in src/gen/emit_vm.c) and restore pos (positive) / fail (negative); on failure fail (positive) / succeed with pos and captures restored (negative); lookbehind as BACK-STEP-then-forward-body-with-END-CHECK (PCRE2's shape: for each alternative of fixed length k, step back k CHARACTERS, run forward, require the body to end exactly at the original pos) — the emitted code with labels, the trail/slot interactions (the trail restores OLD slot values on backtrack, backrefs_design.md §3.7's model), the step/frame budgets (D42.6: a lookaround body's steps count; empty-iteration guard when a lookaround sits under a quantifier); (iii) THE BACK-STEP as the [M5-SEAM]'s THIRD residual entry (src/gen/enc/enc.h's PcrecEncEntry: id, engine_callable, decls/defs) — signature designed for the UTF-8 backend (k characters, not bytes; what happens at start-of-subject), the D58 record of the seam change, the [M5-SEAM] codegen check's population (backrefs_design.md §4.4's P14 precedent); (iv) ENGINE SELECTION — registry rows VM_ONLY by default (APPROACH §: lookaround is VM), EXCEPT the DFA-ELIGIBLE SUBSET that D66 needs: a ONE-CHARACTER fixed lookaround whose body is a single class (`(?<=\n)`, `(?<!\w)`, `(?=\w)`, `(?!\z)`-shaped end forms) IS the assertions module's alphabet-context assertion (waves B/C) — design the RECOGNIZER (which shapes, where in the pipeline, how the identity gate proves it is a no-op for today's population) and rule whether M6.6 SHIPS it or hands it to [DD-11] with the door built; the PREFILTER SOUNDNESS argument: dropping any lookaround from a pattern yields a SUPERSET language, so the hybrid's DFA prefilter may run the lookaround-erased pattern — state it, then MEASURE it on the candidate-start population (the hybrid's planted-window hazard from backrefs_design.md §11.2 is the precedent for how a "superset" can still change an answer: check the match-START semantics, not just membership); (v) THE D66 HAND-OFF — what the core lookbehind-anchor form needs from this module (the one-byte lookbehind lowering to the context mechanism; the (?m)^ ≡ `\A|(?<=\n)(?!\z)` self-oracle: expansion vs folded implementation as an in-tree differential — design the CHECK's shape even if DD-11 builds it); (vi) THE D27 GOAL-FACTS LIST — python 3.14 `re` vs libpcre2 divergences on lookaround (python REQUIRES every lookbehind alternative to have the SAME fixed width — `(?<=a|bc)` is a python error, legal in PCRE2; python lacks the alpha spellings and the non-atomic forms; python's treatment of captures in negative lookahead; quantified lookaround) so the blinded author knows which oracle rules each cell; (vii) registry visibility of every spelling for D65's built column (SR-8 generic capability check will CATCH rows lacking witnesses — the backrefs precedent); (viii) the identity gate (byte-identity of every pre-module artifact on three axes against a pinned pre-module SHA, the positive control refusing every lookaround pattern) and the sabotage rows (each claim one row; the two-site mechanism exists if a claim needs it); (ix) the size of the module's construct population for the blinded corpus and the acceptance run. Premises RE-VERIFIED on HEAD (the refusals, the assertions context machinery's actual shape in src/, the VM cut's actual interface). D6 panel (R33) BEFORE implementation; Frank says go after.
  - [M6.6.2] STATE:completed-pending-close (ALL BUILD WAVES MERGED 2026-08-24 ~07:2x — wave F at 7307741 (lane/waveF b68ca13): twelve alpha spellings as ALIAS ROWS (family = the primary's canonical syntax; la_kind resolves alias→primary so an alias has no flags of its own to be wrong about; the assignment MEASURED 84 templates × 19 subjects / 0 divergences; §8.2's VerbName-pair recommendation superseded by rows — one home, D24), D71.3's family field + --list-families (118 rows / 106 family lines; recursion joins by setting family="(?N)" on its rows + one 'at most one canonical' relaxation in check_families) + RF_INDEX (arbitrate skip placed BEFORE the REG_SEL_ANY arm — load-bearing) + S142 (registry:2fail DETECTED), D65 tally 106/58 → 118/70 with ZERO out-of-module movement (dump-diffed), K30 CLOSED (S18 1fail/454pass at BOTH widths), compliance refreshed all three components (the (?= annotation had analysed the WRONG ENGINE; [[:<:]] re-measured CORRECT; D71.4's DEFINE substitutes VERIFIED per-startpos), reject rows moved with the FORM-row claim REFUTED by a control build and replaced by four answer-level cli pins, registry_check's verb-arm segfault fixed as a named failure, mod_verbs.c's stale PURE-MIGRATION header corrected; corpus 23,049/0, gate 202 bearing / free unchanged, 29 D69 rows all DETECTED. Two waveF caveats on record: the generated index's engines column emits unescaped `dfa|vm` (pre-existing, one-line md_escape owed); --list-families has no --flavour axis (refused rather than invented — SR-7's shape stated). REMAINING FOR THE MODULE: [M6.6.3] D27 blinded corpus + acceptance, [M6.6.4] close (FULL matrix, battery, gate, archive). WAVE E2 MERGED 154141b at ~05:1x 2026-08-24: the §6.3 substitution driver — 887 patterns / 29,063 three-way comparisons / 0 disagreements (P1 263/8,260; P2 361/12,543 — the design's per-cell parenthetical understated P2 by 52%, amended; control 263/8,260 trivially equal), population EXACT vs the design's table (zero delta, asserted not floored), identity rows counted/asserted/excluded (84 = 37 \A + 47 \z), five anti-tautology controls (§0 table re-verified 2,646 cells + a 16-cell vacuity guard in the failing direction; §1b module guard; §1c cell-fidelity 8,260/0; B==C attribution 8,260/0), runtime 40 s warm — rides make test; the laexpand arm measured PER ROW (8 detected, 7 structurally blind — S131 among them: every §6.1 expansion is atomic, the design's wave-E2 bar corrected in the doc; the census in tests/mech/CLAUDE.md), the SKIP trailer renamed oracle-skipped with the failing direction demonstrated from a real log, and the lane's own witness printer found wrong TWICE (awk -v escape-processing; the fix on the wrong pipeline stage) — now a function under §1d's standing three-cell failing-direction control. Driver re-run GREEN on the MERGED tree (11/0, 16,635 lookaround-bearing comparisons) per the lane's recommendation since wave E touched emit_vm.c. WAVE F OPENED ~05:2x as lane/waveF (opus, brief scratchpad/brief_waveF.md). WAVE E MERGED 6cf861c at ~04:4x 2026-08-24: the §5.6 predicate — THE CEILING BUG WAS LIVE on pre-E main (the measured witness `((?:a(?!q)|aq)(?:xy){0,4}q)` answered NOMATCH on "aqq"; now (0,3), matching both oracles); codegen rule 1 = ceil_drop/ceil_keep over FOUR readers incl. --emit-ir's PRUNING line; prefilter.rxt (9 blocks, every clamping cell QUALIFIED against a pre-wave compiler — 5 of 10 candidates; incl. the non-atomic `(?*!` cell that separates this predicate from atomic's); S140/S141 DETECTED (S141 two-site: both builders sabotaged, stamp left reading the flag — only rule 1(a) catches it); the identity gate caught the lane's own 37-byte generated-comment regression on 54 lookaround-free artifacts (reverted; the wording wart recorded as [M4.6d] obligation (d) — a second why-flag beside mrl_win would be the two-sources defect); the `lookaround` mech arm measured BLIND to S140 (no `q` in its shared subjects — the .rxt is the detector, recorded); merge conflicts resolved by the manager, NPO guard re-derived on the merged tree = 45 (5/0 green); one unexplained one-off: run_vm_identity refusal mismatch under concurrent load, not reproducible. WAVES 0/A/A2/B+C/D/E ALL MERGED — remaining: E2 (in flight), F, then M6.6.3/M6.6.4. WAVE D MERGED e10bad4 at ~04:1x 2026-08-24: the seam's third residual entry $_back_step with ZERO interface change (P-1 held, recorded in enc/CLAUDE.md), the fixed-per-branch lookbehind (widths from the A_ALT spine filled from the END, count asserted vs AltInfo.nbr; unbounded tested before int-representability), end-check on BOTH arms (negative = hard RX_R_FRAMES by elimination — see the D71.1 wave-D note), corpus +175 blocks (22,936/0 total), [M5-SEAM] N=7 + the sentinel detector added, rows S133-S136 + S130/S125 re-homed, FULL mech 134/0/0, gate 168 bearing / 2,049 free control exact 168/168, run_lookaround_diff §1 44 blocks / 4,268 cells / 0; three lane findings: the design §3.4 sentinel-arm sketch was WRONG TWICE (amended in the doc at merge), the width-0 guard tripped -Wtype-limits (condition-gated), S134's first single-row run scored UNDETECTED because the row's detector was uncommitted while mech archives HEAD — a lesson for lanes writing a row and its detector in one wave. WAVE E2 OPENED ~04:2x as lane/waveE2 (opus, brief scratchpad/brief_waveE2.md — the §6.3 substitution driver, tests-only, launched off wave D's merge without waiting for E; disjoint from waveE except an append-shaped CLAUDE.md edit). WAVE B+C MERGED b6338f6 at 2026-08-24 ~00:3x: mod_lookaround.c's one port (three lookahead tails built, the `<` tails declined = the D65 split — --list-syntax 55 built / 45 unbuilt / 6 n/a), vm_look's three lookahead arms with §3.2.1 scoping (measured: `(?=(a+)b)a+b` prunes at 1), tests/lookaround (81 blocks / 118 cells, gen_corpus.py computes `# pcre2-only`; G8/G9 REFUTED — quantified lookaround and the capture axis are 100% python-verifiable; G5 holds), run_lookaround_diff.sh (1,022 pcre2-only cells vs libpcre2; the atomicity discriminator disagrees with itself on exactly 13 cells, asserted), rows S122-S132 incl. S128 (`\K`, in no wave's bar — the lane caught it) and S130 deferred to D, the `lookaround` mech arm, the gate's bucket split (85 bearing / 2,048 free, control 85/85, STRICT_ALL=1 demonstrated red 332 comparisons / 0 in the free bucket), corpus 22,651/0; four lane findings: S101's anchor collision (R33 V-7's prediction arriving at the EXISTING row), a D24 two-homes defect (UNBUILT marker) fixed, the SR-8 capability check re-keyed on D65's built column, a stale population guard that contaminated the first row batch (re-run clean). WAVE D OPENED ~00:4x as lane/waveD (opus, brief scratchpad/brief_waveD.md: the seam's third residual entry $_back_step + the fixed-per-branch lookbehind + end-check on both arms + S-LA6/7/8/11 + S130 re-homed). WAVE E OPENED ~00:5x CONCURRENTLY as lane/waveE (opus, brief scratchpad/brief_waveE.md: the §5.6 predicate at the v.mrl_win site, codegen rule 1 on both sources, --emit-ir's description, prefilter.rxt with the measured witness, S-LA12/13 taken from the end of the id range) — disjoint from D except emit_vm.c, second lander rebases; E2 (the substitution driver) waits for D's lookbehind. WAVES A+A2 MERGED 1187973 at ~22:4x: pcrec_maxw (PCREC_W_UNBOUNDED == PCREC_MINW_MAX, composes with the saturating arithmetic) + tests/mrl/maxw_check.c's two-sided sweep (12,637 nodes / 8,901 oracle spans / 0 violations, three sabotages caught), the A_LOOK enumerator + u.look payload, 24 walker arms (design's 23 confirmed file-for-file + maxw's; the critic's 27 = +4 default-carrying), four default: sites re-inspected SOUND, gate 2056×4 identical, full mech 119/0/0, S58 anchor re-homed; tooling defect FIXED at merge: tests/mech/rows_for.sh printed SAB_IDs the matrix FATALs on (66/67) — D69's targeted tier had never run; it now prints the file's S<id> selector. Cross-milestone obligation recorded: A_CLASS's maxw arm is exact only while UTF-8 refuses by name. WAVE B+C OPENED ~22:5x as lane/waveBC (opus, brief scratchpad/brief_waveBC.md — moves the gate's bucket-split classifier up from wave E and the `lookaround` mech arm up from F); WAVE 0 MERGED a9739e1 at ~21:2x: D70 union, gate 2056×4 identical vs pin eacac76, rd_node/mod_assertions kind-guarded, revdet_highbytes.rxt + S121, corpus 22,485/0, mech 118/0/0 + S121 DETECTED, sizeof(Ast) 104→72; WAVES A+A2 opened ~21:3x as lane/waveA (opus): pcrec_maxw + the A_LOOK enumerator/u.look payload + the budgeted walker arms + the four default: sites; 2026-08-23 ~17:1x, thirty-eighth session, on Frank's "proceed to scheduled build … proceed deliberately"; WAVE 0 = D70 union refactor lane/d70union (opus, worktree) opened first; waves A/A2 → B+C → D → E/E2 → F follow SEQUENTIALLY after D70 lands since all touch the renamed files; the identity gate is built at wave 0 as tests/codegen/run_lookaround_identity.sh in STRICT_ALL pure-refactor mode over the four ruled axes, pin eacac76; wave-0 finding at briefing: 14 mech sabotage rows anchor on the renamed field names — anchor re-homing + D69 targeted rows are on wave 0's landing bar) — IMPLEMENTATION per the approved design (VM lowering, seam entry, registry rows, engine selection, identity gate, sabotage rows, tests/lookaround/ corpus). ASK RULINGS (Frank, 2026-08-23 16:2x-16:4x): ASK 1 RULED — one A_LOOK kind AND the D70 tagged-union refactor lands FIRST as the module's opening wave (pure refactor, byte-identity gate over the full corpus; A_LOOK's payload joins the union; see D70). ASK 2 RULED (Frank, 16:5x): EMIT the end-check on BOTH arms — hard RX_R_* internal-error return on the NEGATIVE arm (a silent decline there is a false match), cheap branch decline on the positive; S-LA11 carries both a (?<= and a (?<! cell. ASK 3 RULED (Frank, 17:0x): YES — the twelve alpha spellings get their own registry/dump rows (spelling-aliases of their six primaries), full D65 built column + SR-8 witness obligations; wave F's module reattribution away from `verbs` stands regardless. ASK 3a RULED (Frank, 17:3x, after the sequencing discussion — 6.6 NOT parked for subroutines; DD-14's design gate runs alongside): the substitution driver BUILDS IN [M6.6.2] wave E2 as designed (263 patterns / 8,260 cells; test infrastructure, not a product mechanism). ASK 4 RULED (Frank, 17:4x): FOUR gate axes — default, the standard second, -fno-prefilter (isolates the §5.6 ceiling-drop conditional, the module's only touch on lookaround-free paths), --no-captures (the backrefs-precedent axis); positive control = every lookaround pattern refuses under the pinned pre-module binary. ALL FIVE §14 ASKS RULED + D70; [M6.6.2] is CLEARED TO START at the next session (Frank, this session: "we'll start implementing next session"). \K-in-lookaround: refusal PERMANENT (Frank: BSK is "bad mojo"; design §2.7 amendment carries the measured old semantics for the record). ASKs 2-5 pending Frank.
  - [M6.6.3] STATE:completed (MERGED 967d795 2026-08-24 ~09:3x: 7 files / 457 blocks / 2,408 oracle assertions authored blinded in the la27 cell; ACCEPTANCE per design §10.3 (cells/failures/triage): first run 1,849 cases / 310 failed / 71 distinct compile failures — ZERO answer mismatches, ZERO pcrec-wrong; triage classes all corpus-wrong: (1) features lines placed before their pattern (the harness attaches directives to the open block; docs/testing.md's after-pattern rule — the author's generator and checker SHARED the misreading, the check-design lesson), (2) missing module names rooted in the manager's brief naming only assertions/backrefs, (3) the §2.5 grouped-alternation boundary — `(?<=(a|ba))c` is ONE variable branch, refused, exactly the boundary the design predicted readers would get wrong, caught as a REFUSAL never a miscompile; final run 1,819/0/0/0. THE BLINDED CORPUS FOUND NO IMPLEMENTATION DIVERGENCE — the backrefs precedent repeated. Corpus lands as tests/lookaround/d27/ riding make test; the cell and la27 worktree removed. 2026-08-24 ~07:5x: cell la27 created via scripts/mk_d27_cell.sh — allowlist la_d27_extract.md (the §2+§7+§10.1 cut, committed 5ae833f) + la_oracle.py with its borrow chain (br_oracle.py, pcre2_ctypes.py) + docs/testing.md + lib/pcrec.h + prebuilt build/; author = sonnet per the brd27 precedent; brief scratchpad/brief_m663_d27.md; the acceptance run happens WITHOUT the author against the merge, every failure triaged corpus-wrong vs pcrec-wrong before any edit) — D27 BLINDED CORPUS (cell author from the goal-facts list; written from PCRE2 semantics and the design's construct table, never from src/) and the ACCEPTANCE RUN against the merge.
  - [M6.6.4] STATE:completed (2026-08-24 ~09:4x — the close ran DURING the corpus authoring, on the F-merged tree 1844a1c: FULL matrix 137 rows / undetected 0 / anomalies 0 / oracle-skipped 0; identity gate 6/0 on the four ruled axes; strict clean; make test rc=0; `make san` green both axes; compliance refreshed at wave F; the final landed-tree make test (corpus + d27 = ~24.9k cases) ran at the merge. Gate-bench re-baseline REMAINS QUEUED (archived COMPILE-SPEED/GCC-TIME numbers predate the timeout swap) — it was NOT cited by this close.) — CLOSE: battery, D69-tier mech (module close = FULL matrix), gate, compliance refresh, archive.
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
- [TT-5] STATE:started (2026-08-23, thirty-seventh session; chartered by
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
- [TT-10] STATE:not-started — tests/resource's 45 s COMPILE-CPU CAP CHECK IS LOAD-SENSITIVE BY CONSTRUCTION (2026-08-24: SIX identical failures across the day's merged-tree batteries on `[a-z]{0,30000}` / `(a|b){0,30000}`, every one green solo, every one under a concurrent lane build — the K31 addendum's shape). The check asserts the cap FIRES within 45 s of CPU, but CPU-time inflation under SMT contention (measured >2× in docs/testing.md) pushes a quiet-box ~25 s compile over 45. Charter: make the check measure what it means — either (a) a RATIO against a calibration compile taken in the same run (the cap fires within k× the calibrated cost), or (b) a load guard that reports INCONCLUSIVE (never PASS, never FAIL) when the 1-minute load average exceeds a threshold, with the D45 budgets themselves untouched. Same class as the k18 san budget: a CPU-bounded assertion is only exact on a quiet box, and a check that lies under load costs a solo re-run per battery. Sonnet lane, small; lands with the next battery-touching wave or at the [DD-14] close.
- [TT-9] STATE:not-started — THE THREE SANITIZER SUITE LISTS ARE HAND-MAINTAINED COPIES (found by [DD-14] wave B+C, 2026-08-24): `make ubsan`/`asan`/`san` each carry their own list of suite scripts and nothing enforces agreement — the lane's first patch added `run_recursion_diff.sh` to ubsan's list only, and the san run silently never executed it (only the `-- san:` stage banner revealed it). Also: `tests/lookaround/`'s diff script is absent from all three lists with no stated reason. Charter: ONE list (a Makefile variable or a manifest file) that the three targets read, plus a check in `tests/codegen`/`make testscripts` that every `tests/*/run_*_diff.sh` is either in the list or named in an exclusion list with a reason (the SKIP-is-not-a-pass shape); add the lookaround diff or record why not. Small; a sonnet lane; lands with the next battery-touching wave.
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
- [REL-META] STATE:not-started — USER-DOCS OBLIGATION (Frank, 2026-08-24, D73): the recursion frame/trail default (2048/3072), the subject size it implies for recursive patterns (`^(a(?1)?b)$` gives up at a 684-byte subject), the musl/small-thread-stack caveat (K33) and the caller-provided buffer (`_in` entries) as the remedy must be in the user docs and the release note — not a footnote. META-PLAN ROW for FIRST-RELEASE +
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
- [LIB] STATE:not-started — SUBPATTERN LIBRARIES (Frank, 2026-08-24, thirty-ninth session; PLANNED — its place relative to the spine is NOT ruled (Frank ~22:0x: "planned but I don't know that I'd put them on the spine"); to be discussed at [DD-14]'s close): (1) the .rxt format grows so a file can carry MULTIPLE patterns that reference each other through SUBROUTINE CALLS (definitions + patterns in one file, the way [DD-14] is being built); (2) the same mechanism user-facing — a user INCLUDES a library of named subpatterns and calls them from a pattern by name; (3) pcrec SHIPS a LIBRARY STORE of tested subpatterns (email address, IP address, quoted string, HTML pieces, …). Relations: [DD-11] (scope-resolved definitions whose values are inserted — this row is that architecture's user-facing form; a library is a definitions scope), [V-E] (multi-pattern compilation units — the unit boundary), [DD-14.G] (splice + dead-capture elision is what makes a library subpattern cost NOTHING: the artifact byte-identical to the hand-inlined pattern — the email specimen's bar), [DD-14.F] (the DEFINE row is the in-pattern spelling of a definition). Design points to settle at charter: NAME RESOLUTION (pattern's own groups first, then included libraries in order; collisions refused by name; PCRE2 has no include, so this is pcrec's compile-time namespace — the oracle sees the EXPANDED pattern, which makes the harness's expansion the SPLICE-vs-LINKAGE `A == B` control by construction); the .rxt directives (`define name <pattern>` / `lib <file>` per file or block; the harness expands for libpcre2 and passes the library to pcrec); the API surface (`pcrec_options` gains a definitions input; CLI `--lib FILE`; versioning per [DD-3]); the STORE's discipline (each entry oracle-verified, a D27-blinded author writes its corpus, pcrec-bench carries it as a benchmark row; the RFC 5322 email specimen is entry #1). Depends on [DD-14] closing (G in particular). Not started unprompted; the charter conversation opens at [DD-14]'s close with the post-spine direction note (journal 2026-08-24).
- [V-E] STATE:not-started — MULTI-PATTERN COMPILATION UNITS and the
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
- [ENG-PGO] STATE:not-started — CROSS-NOTE (Frank, 2026-08-24, thirty-ninth session, direction not decision): the `--profile` emission mode below gains a SECOND CUSTOMER — the post-spine pcrec-bench OPTIMIZATION LOOP (journal 2026-08-24 direction note): a PROFILE ATTACHMENT on a compiled pattern that says where the matcher spends its time BY SECTION (prefilter scan, skip loop, VM attempt, per rung) and, where possible, in smaller increments, run over a variety of scenarios, to guide optimization PRIORITY — `--trace` is the debugging tool, the profile is the optimization tool. Design starting points (manager, same day): time attribution needs cycle deltas (`rdtsc`/`clock_gettime`) at the section boundaries the emitter already names, not counts alone; the computed-goto labels are natural fine increments (count + cycles per label = a per-construct profile with no `perf`/symbolizer), and can carry the pattern offset the [V-H] trace-enrichment note wants; the profile struct is read through an `rx_info`-shaped accessor; the artifact stamps that it is the profile variant (identity gate: the default artifact is byte-identical across the axis). Same [V-H] namespace as D71.1's counter axis — a second diagnostic axis is the trigger D71 names for designing the GROUP rather than the flag. PROFILE-GUIDED GENERATION (Frank,
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
- [DD-13] STATE:not-started — THE UNIFIED PATTERN-SOURCE / TEST FILE
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
  - [DD-13b] DESIGN note: grammar + semantics (include model, config
    scoping/precedence, reference/namespace rules, exemplar-file
    addressing, the machine-generation contract), the migration story
    for the existing ~10k-case corpus, and single-vs-multiple emitted
    outputs.
  - [DD-13c] D6 ADVERSARIAL PANEL on the design, then Frank's ruling.
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
  interface-vs-reference-only pattern distinction.
- [DD-4] STATE:completed-in-place (2026-08-19: [M6.2] wave D answered it — start_max = startpos as a third compile-time string, no wrap toggle needed, §4.1/§4.3; the find-all sentence is in match_api.md §3.1; row retained here rather than archived because its text is cited from DD-7) — formerly STATE:not-started — \G / global-iteration semantics vs startpos (with M6) (R1 A-11)
- [DD-6] STATE:not-started — multiline ^/$ as DFA state context — interacts with state budget (with assertions module) (R1 A-6)
- [DD-11] STATE:not-started (CUSTOMER ADDED 2026-08-21, D66: the
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
- [DD-14] STATE:started (DESIGN APPROVED AND MERGED a59bbb5 at ~22:2x, 2026-08-23: docs/design/subroutines_design.md 3,016 lines after R34's three rounds — 22 panel findings (5 HIGH) + 16 verifier findings (6 HIGH) + 5 re-check residues, ALL fixed, 0 disputed, 0 outstanding; record docs/dev/reviews/2026-08-23-r34-subroutines-design.md. SIX ASKs (design §14). ASK 1 RULED (Frank, 2026-08-23 ~23:1x): SPLIT — (i) the CODE `PCREC_ERR_RECURSE` is reserved NOW and ERR_FLOOR moves −4→−5 across the eight sites unconditionally [WAVE-D NOTE 2026-08-24: the lookbehind end-check's negative-arm hard return currently uses RX_R_FRAMES by elimination (a42cd0e finding (b) — minting a code mid-module would collide with this floor move); when the renumber happens, consider minting an INTERNAL-ERROR code in the same ABI event and re-pointing that return — Frank confirms at DD-14 clearance] (an ABI fact, a one-time pre-v1 renumber); (ii) the COUNTER (increment/decrement/compare + the per-frame `call_mark` field) is NOT in the default artifact — it is a DIAGNOSTIC GENERATION AXIS in [V-H]'s namespace (`--trace`'s shape: a separate emitted variant, never a runtime flag, the artifact stamps it), and even under that axis it is emitted ONLY when the post-discharge tree contains a call (`pcrec_has_call(root)`, the has_atomic/has_lookaround predicate shape) — a call-free pattern's artifact is byte-identical across the axis, which the identity gate asserts as a control; the default artifact's give-up for a deep call is `PCREC_ERR_FRAMES` and the documented story is "rebuild with the diagnostic axis to learn which bound". Design consequences at implementation: S-SR2a becomes a row under the diagnostic axis; the frame struct differs per variant as --trace's does; the axis joins the gate's axis list; ASK 2 simplifies (the default artifact's ceiling IS RX_RESUME_FRAMES; only the diagnostic variant's stamped bound remains to pick). REMAINING: 1 keep PCREC_ERR_RECURSE (rec keep) — RULED above; 2 RX_CALL_DEPTH default — RULED (Frank, 2026-08-23 ~23:1x): (b) — a LARGER stamped default of RX_RESUME_FRAMES for call-bearing patterns (post-ASK-1 the default artifact's recursion ceiling IS the frame capacity; the diagnostic variant's stamped bound defaults to the same number), calibrated at implementation the way the step budget's 500M and the work budget's 10⁹ were, the honest ceiling stamped so a caller can read it, and the RELEASE NOTE states BOTH subject sizes — the legitimate-depth limit on `^(a(?1)?b)$`-shaped input and the runaway cost PCRE2 pays (quadratic, 2.6-5.6 s at n=20k) that pcrec's constant-time refusal does not. MECHANISM ADDED (Frank's question, 2026-08-23 ~23:5x, manager assessment): the resume-frame buffer becomes CALLER-PROVIDED — the run struct holds a pointer + capacity instead of the inline `resume_stack[<PREFIX>_RESUME_FRAMES]` array (emit_vm.c:5827), NULL → the stamped default (unchanged behaviour, byte-identical default artifacts = the gate's control); the caller may hand over an mmap'd lazily-committed reservation and get PCRE2-depth behaviour with pcrec still never allocating; the push-site check reads the capacity field (a load, not an immediate; codegen rule). This resolves ASK 2 rather than tuning it (the stamped number is a DEFAULT, not the limit), takes the frame array off the C stack (the [TS-4]/DD-10 musl 128 KB concern), leaves ASK 1's diagnostic axis untouched. It is a deliberate pre-v1 API ADDITION (a new entry point or a run-state object — shape decided at docs/spec/match_api.md under D40, versioning per [DD-3]); lands with DD-14's implementation; 3 registry row granularity — RULED (Frank, 2026-08-23 ~23:3x): (d), NOT the design's (b). The DISPATCH rows stay exactly as R6 ruled (one literal byte after `(?`, literal-prefix tails, the ten-row digit family deliberate — registry.c's lookup rationale and internal.h's `tail` comment; the linear scan is 33.6 ns against a 90 µs floor); every 'missing' spelling is ALREADY reachable ((?10) via sel '1', (?01) via '0', (?+7) via the tail-less '+' row, (?-01) via '-'/"0") — the defect is the '0' row's DESCRIPTION ("synonym for (?R)") and the index's row=construct assumption, not the key. So: (i) the PORT owns the digit-run rule (whole run as decimal, 0 = root, relative zero = err 126); fix the '0' row's description/witness; (ii) NEW GENERAL MECHANISM — a `family` field on RegRow: rows keep their dispatch identity, `--list-syntax`/compliance print one line per family with a canonical syntax ((?N)) and the rule, D65 `built` derives per member (a family reads built only if EVERY member does), SR-8 witnesses required per RESOLVER-DISTINGUISHED shape ((?1) (?01) (?10) (?00)), not per digit; it LANDS AT [M6.6.2] WAVE F, whose twelve alpha-spelling alias rows are its first customer (recursion's digit families and \g<1>/\g'1' the next two); (iii) the dogfood idea (rows keyed by a pattern, recognizer generated by pcrec) is DECLINED for dispatch (reverses R6's measured ruling for ~23 ns, adds a bootstrap stage, reintroduces the interpretation surface the literal tail removed) and NOTED under [SR-10]/[DD-13] as a future CHECK on the syntax column, never its dispatch; 4 DEFINE — RULED (Frank, 2026-08-23 ~23:4x) and SUPERSEDED: `(?(DEFINE)...)` JOINS MODULE `recursion`'s CHARTER as a TAILED ROW on the `(?(` doorway (the registry's tail mechanism — a tailed row beats the tail-less `(?(` catch-all, which stays `conditionals`' and keeps refusing; the `\N{U+`-over-`\N{` precedent), LOWERED AS THE `{0}`-CALLEE SHAPE the R34 verifier surfaced (§4.4c: no code at the lexical position, a callee region for calls) — one row, zero new mechanism, never a textual substitution (a parallel path). Frank: DEFINE is semantically a subroutine construct; `conditionals` owns it only by doorway accident, and subroutines without DEFINE is half a feature for library patterns. Interim: (c) — the compliance page documents both exact substitutes (`(?:(?<w>X)){0}`, `^(?!)(?<w>X)|BODY`) with the refresh; the diagnostic wording is untouched (D26 tier 3). The design's §2.5/§13 are amended at implementation; 5 single-oracle D27 corpus — RULED (Frank, 2026-08-23 ~23:4x): PROCEED with the SPLICE-vs-LINKAGE self-oracle as a wave-G landing bar, the D27 brief stating python's refusal is an ABSENCE not a divergence, AND ADD A PERL ARM (perl v5.40.1 is on the box — measured): Perl is the construct family's origin and predates PCRE2's own atomicity change, so it is the genuinely independent second lens for the semantic cells (captures on return, backtracking into a returned call, (?J) resolution, left recursion); the oracle wrapper + a divergence list (Perl vs 10.46) are [M6.6.3]-shaped D27 infrastructure for the recursion module; 6 lift of the possessive-rung decline for call-bearing bodies — RULED (Frank, 2026-08-23 ~23:5x): (a) NOW — rung admission declines every call-bearing body (the backtracking rung takes it, bounded by the step budget; S-SR9a is the TIMEOUT row on the possessive path, since vm_poss_star has no guard and no charge, emit_vm.c:918-922/:2919) — and (c) CHARTERED: admit a call-bearing body only when the callee's SCC is provably NON-NULLABLE through the call-graph fixpoint that already answers vm_nullable/minw — the sound subset, eng_brep §2.2's own argument one graph edge further; (b) a measured wave-G lift is NOT chartered (buys nothing (c) does not). ALL SIX ASKs RULED 2026-08-23 23:1x-23:5x; [DD-14] IMPLEMENTATION remains sequenced after [M6.6] and NOT cleared until Frank says go. IMPLEMENTATION NOT CLEARED until Frank rules the ASKs and says go; it sequences AFTER [M6.6]. Design citations into src/ are pinned at eacac76 — D70 moved internal.h +86 lines (LENS3-3), re-verify at implementation. lookaround_design.md P-13 re-pointed d41febb (the hand-off declined — V-10). Final lane commit 77fa209 merged (3,033 lines). OPEN GAP the lane named for the implementation row: probes/check_selfconsistency.py proves archive FRESHNESS and id/file PLACEMENT, not that a number quoted in the prose appears IN the archive it cites — the class the lane committed four times across R34 (V-7, V-11, and twice inside fixes); a fourth check (extract quoted figures, grep them in the cited out/ file) is unscoped and belongs to whichever lane next touches the design. DESIGN DELIVERED 2026-08-23 ~20:5x at lane/dd14design e5181e6 — docs/design/subroutines_design.md 2,159 lines §0-§14 + subroutines_measurements/ (oracle, 8 probes, 2 prototypes incl. the §5 mechanism BUILT and run 45/0 vs libpcre2); R34 CRITIC PANEL OPENED ~21:0x (C1 semantics/opus, C2 mechanism/opus, C3 coverage/sonnet; brief scratchpad/brief_r34_critic.md); five §14 ASKs await Frank after the panel; headline refutations of the charter: NO compile-time left-recursion refusal in 10.46, the plan row's separate call stack is a measured bug (call = a resume frame instead), \K not restored by return, call-vs-backref duplicate-name resolution differs. DESIGN GATE OPENED 2026-08-23 ~17:1x, thirty-eighth session, lane/dd14design (opus, worktree; src/ read-only + probes), running ALONGSIDE [M6.6.2] per the ruling; implementation NOT cleared until the design is panel-approved and Frank says go) — formerly STATE:not-started (RULED IN AND SEQUENCED by Frank 2026-08-23 13:4x: "for the actual substitutions, let's get the group reference piece in so that they share code/handling before we do the substitutions. I don't want parallel mechanisms if we can avoid it" — "subroutines". ORDER: [M6.6] lookaround → [DD-14] subroutine calls (?1) (?&n) \g<n> (?R) — module `recursion`, the label-call primitive — → [DD-11]'s definition substitutions IMPLEMENTED ON that primitive (an insertion = a non-recursive call to the inserted body's entry label; compile-time splicing an optimization of it, never a second mechanism) → D66's core lookbehind-anchor optimizer. The [M6.5] follow-up (f) (A_BREF → subroutine call under the singleton predicate) joins the same primitive. The DD-14 DESIGN GATE may open in parallel with [M6.6.2]'s implementation — disjoint parser hooks; both touch src/gen/emit_vm.c, so the second to land rebases. The M6.6 design's TEST-side substitution driver (textual expansion of the assertions D27 corpus into lookaround patterns) is a corpus generator, not a product mechanism, and stands. DESIGN-GATE CHARTER ADDITIONS from the 2026-08-23 afternoon discussion (manager + Frank): (i) the ADDRESSABLE-BODY emission question — a called group's body exists at its lexical position AND as a call target; rule once-emitted-with-two-linkages vs lexical-occurrence-as-call, measured; (ii) rule whether any LOOKAROUND body should compile as a call — expected NO for single-use bodies (a runtime call is pure loss with no reuse), reason measured; (iii) STATED PREMISE: lookaround's disciplined splice ([M6.6.2] vm_look — self-contained body region, fmin/fdyn scoped, clean entry/exit) IS the inliner's mechanism — a statically-resolved single-continuation non-recursive call splices through it; recursive/shared bodies take the call linkage; one callee contract, two linkages ((f)'s A_BREF reduction is the third consumer); (iv) the callee-side reuse inventory vs the genuinely-new caller side (call stack, addressable entries, per-level captures measured on 10.46, left-recursion refusal, depth capacity + ERR_FLOOR move) — the four gating design questions all live on the new side) (CROSS-NOTE 2026-08-19: [DD-11] now carries
  Frank's GENERALIZED definition/insertion direction — the assertion
  family as scope-resolved definitions whose replacement values are
  inserted rx; this row's call primitive is that idea's substrate, so a
  DD-14 design must read DD-11's generalization block first) — RECURSIVE PATTERN CALLS, the design sketch
  (Frank question + manager sketch, 2026-08-18, thirty-third session;
  UNRULED territory parked at Frank's "save your notes" — module
  `recursion` keeps refusing by name until ruled in). The language is
  non-regular so this is VM-ONLY structurally (joins the forces_* rows;
  --engine=dfa refuses). THE MECHANISM: an explicit call stack of
  computed-goto LABEL ADDRESSES inside the single emitted VM function —
  push the return label, goto the subpattern's entry, pop-and-goto* on
  subpattern success. No C recursion, no interpreter, allocation-free
  with a bounded DEPTH capacity and a NEW typed give-up code (D49
  reserved below ERR_FLOOR for exactly this; the floor moves -4→-5 as a
  deliberate pre-v1 change). NOT inline expansion to depth K — that is
  bounded-repeat replication again, and K19/K22 already paid for that
  lesson; the call stack makes emitted size depth-independent (the
  revdet-rung reason). Four design questions at charter time: (i)
  per-level capture save/restore (PCRE2 semantics MEASURED, not
  recalled); (ii) call atomicity — changed across PCRE versions; if
  atomic, RX_CUT is the tool; measure 10.46, the answer picks the
  machinery; (iii) left-recursion refused at compile time (PCRE2's
  could-loop-indefinitely check equivalent); (iv) the capacity/budget
  accounting joins the D42.6 family. THE CONVERGENCE (ties D61/D64
  threads): a call to a NAMED pattern and a recursive self-call are the
  SAME primitive — once the label-call mechanism exists, match-time
  insertion is a non-recursive call to the inserted body's entry label,
  so the insertion machinery and recursion should be DESIGNED TOGETHER,
  with compile-time splicing remaining an optimization for the
  non-recursive case
  - [DD-14.A] STATE:completed (MERGED 0c75c96 2026-08-24 ~10:2x; lane/srA 3 commits 09b2769/3ca8588/9b8cfda; bars: strict clean, [ABI-NS] 18 constants, gu failing-direction demonstrated, lookaround corpus 2383/0, anchors 137/142, D69 rows 71/71 DETECTED (6 re-run on merged main after srA2's pkill), test-resource clean solo; the corpus's one red block was a load compile-timeout on the K32 cell — the merged-tree battery is the clean reading. SIDE EFFECT: the three pinned pre-module identity gates (lookaround/atomic/backref) RETIRE — their references cannot move past the ABI event; each now refuses with the reason. Was: lane/srA, sonnet) — WAVE A, the give-up code space alone: PCREC_ERR_RECURSE (-5), ERR_FLOOR −4→−5 at design §5.6 sites 1-8, the `_R_RECURSE` sentinel + search-entry propagation, the driver naming every code, the `gu <code>` harness directive (§10.3) exercised in the failing direction; PLUS (D72, CONFIRMED by Frank ~10:2x) PCREC_ERR_INTERNAL (-6) BELOW the floor and the lookbehind end-check's hard return re-pointed to it. No producer, no counter (D71.1), no frame fields (5a/5b are B+C's).
  - [DD-14.A2] STATE:completed (MERGED ac4917d 2026-08-24 ~10:4x; lane/srA2 4822297, 4 commits; strict clean, identity 2657/0, anchors resolve; D69 rows 88/88 DETECTED (single-row sweep, MECH_DONE 13:31); FOUND the u.call.body pass-ordering hazard + la_has_kreset blindness → B+C obligations. Was: lane/srA2, opus) — WAVE A2: `A_CALL` + the `u.call` D70 payload + `CallLink`; the 27 arms of §4.4a (GRAPH sites as loud placeholders until callgraph.c); `pcrec_has_call` external, unwired; the D70 survey's `u.call` answers; the eight switch-less walkers inspected; byte-identity of every corpus artifact vs main as a plain diff. Merges after A, rebased.
  - [DD-14.BC] STATE:completed (MERGED 67e40b9 2026-08-24 ~15:3x; MERGED-TREE BATTERY: make test corpus 25,217/0 every section (the one red was the D45 control catching the un-ruled GENCPU_SAN edit, fixed 06c7ee2, solo green), strict clean, san rc=0 58 min ZERO reports both axes (~16:35) — BATTERY GREEN; lane/srBC 19b3a4c, 18 WIP commits: bars — make test 25,216/0 every section, strict, san 55 min zero reports, tests/recursion 346/0 incl. --no-captures, run_recursion_diff.sh 1,632 oracle cells 0 disagreements, sibling corpora untouched, identity 2198/2198 ctl_bad 0, anchors 162/172, --list-syntax 24 (? rows built / 2 \g unbuilt, depth n=342 then frames, a×200 matches, mech 19 DETECTED / 7 expected-UNDETECTED with measurements (S150-153 S157 S160 S164) — the checked SAB_EXPECT field LANDED as the follow-on (lane/srBC-expect b6311f4, merged ~16:0x: 26 rows 'unexpected: 0' = 19 DETECTED / 7 UNDETECTED(expected), failing direction exercised on S146); refuted/amended: §5.3b axis-C premise, S-SR9a's arm, A2 obligation 1 → bind over the FINAL tree (S166 + codegen rule 3), A2 obligation 2 WITHDRAWN (\K is LEXICAL on 10.46, measured), three non-existent suite names in §9.3; cells 2-3 parked → [DD-14.LB]; cell 1 → corpus fix per P-12. Was: lane/srBC from 086624a, opus) — WAVE B+C: ports, resolver, callgraph.c (SCCs, W fixpoint, minw), RX_CALL/RX_RETURN, save/restore, the fourteen corpora, 23 sabotage rows (§11). Opens when A and A2 are merged and the battery is green.
  - [DD-14.LB] STATE:completed (MERGED 2a9dfeb 2026-08-24 ~17:4x; D+LB-TREE BATTERY GREEN: test 25,271/0, resource 19/19 solo, strict, san rc=0 45 min zero reports; lane/srLB 3b67bd3, 12 commits, +1867/−316: src/opt/postresolve.c = THE POST-RESOLUTION CHECKS pass (every rule that must refuse at an offset and needs the call graph; lookaround's fixed-width rule its first customer, the rule rendered from ONE home in the module), u.look.at, u.call.maxw/maxw_known + the maxw fixpoint; parked cell 1 compiles, cell 2 = the ruled §2.5 limit (its diagnostic corrected from a false 'unbounded' to the true '1..2' at the same offset — the fifth reject row pins that WORDING); known_fail EMPTY; inlookaround.rxt 3→21 blocks; S169-S172 DETECTED; lookaround corpus byte-identical 352/354; identity 2198/2198 + 96/96 call-bearing; make test-recursion-lbsweep 908 patterns × 22 subjects = 9,240/9,240, the over-rejection surface = exactly PCRE2 10.43+'s variable-length lookbehind; full matrix 159 DETECTED / 7 expected; five reject rows pin the refusal OFFSETS (all libpcre2's own); two reject-suite guard defects fixed in passing. Was: lane/srLB from 67e40b9, opus) — INTERIM (srLB 1d42123, ~15:5x): mechanism landed as `src/opt/postresolve.c` (`pcrec_postresolve` after `pcrec_callgraph_build`; the hook RECORDS a call-bearing lookbehind with its offset — `u.look.at`; the pass visits in ascending offset and calls module lookaround's own rule from one home, so the diagnostic bytes are identical at both timings; `u.call.maxw`/`maxw_known` + a maxw Kleene fixpoint in callgraph.c); control 354 blocks, 352 byte-identical incl. all 43 lookaround refusals; parked cell 1 now COMPILES and matches; parked cell 2 was NEVER in the shipped subset — a single variable-width branch (1..2) reached through a call, the twin of refused.rxt's `(?<=(a|bc))x` — so it lands as a RULED perr (tier 2), not a known_fail; the borrow-the-callee's-branches special case rejected (general-mechanism rule; would invert §2.4's longest-first order). known_fail returns to EMPTY. — DEFERRED LOOKBEHIND WIDTH RE-CHECK for call-bearing bodies (found by wave B+C, 2026-08-24): `la_widths` runs in the parse hook (the only place with an offset to refuse at) before `.body` exists, so `(?<=(?&g))` with a fixed-width callee is over-rejected as unbounded (tier-2, never a miscompile; two cells parked in tests/known_fail/dd14_bc_open.rxt, the ratchet fires when they pass). Charter: the hook RECORDS a call-bearing lookbehind (+ offset, a `u.look` field) instead of refusing; a pass after `pcrec_callgraph_build` recomputes widths through the graph (design §3.4(d): recursive callee = UNBOUNDED exact, acyclic = the callee's maxw) and refuses at the recorded offset. Same timing class as A2's `la_has_kreset` obligation — land together. Owner: wave D or E (manager's call at wave D's brief).
  - [DD-14.EMPTY] STATE:completed (MERGED with wave E at 85361cd: MEASURED that engine selection runs BEFORE pcrec_callgraph_build fills u.call.minw (compile.c :216 vs :235) so a root check there can never fire — the site is the EMITTER's search-entry prologue: `if (subject_length - search_from < RX_VM_ROOT_MINW) return 0;` with RX_VM_ROOT_MINW = PCREC_MINW_MAX = 2^40, a WIDTH COMPARISON not an unconditional return (saturation on a merely enormous minimum reaches the same ceiling), emitted only when the root reaches the ceiling (four corpus patterns, all call-bearing — no call-free byte moves); the two sibling cells RULED `n` via the generator's ruling form; S169 DETECTED with the predicted two-red/one-green signature) — UNIFORM ANSWER FOR AN EMPTY-LANGUAGE CALLEE (found by wave B+C): design §12 P-12 rules `minw = infinity` a legal compile meaning "no position can match"; today `^(a?(?1)b)$` answers NOMATCH in O(1) (the `a?` carries the MRL bound) while its siblings `^((?1)a)$` and the indirect cycle GIVE UP (`frames`) because no quantifier carries the bound — the answer depends on an accident of shape. Charter: the general mechanism (root-level minw = infinity → the search entry answers nomatch before any frame is pushed), the sibling cells' expectations flipped to `n` with P-12 cited, `gu frames` cells kept only for genuinely runaway shapes with a base case. Owner: wave E (engine selection is where the root predicate lives). B+C lane's refinement (2026-08-24 ~15:5x): all three siblings already have root minw = ∞ (reasoned from the `mrl_sat_add` chain + the fixpoint seed, corroborated by cell 1's emitted clamp line; NOT instrumented — instrument `pcrec_minw(root)` on the two give-up siblings FIRST, ten minutes); the mechanism is `pcrec_minw(root) >= PCREC_W_UNBOUNDED` → the search entry answers NOMATCH before any frame is pushed — one site, subsumes the quantifier case. Cell 1 now lives in leftrec.rxt as a RULED `n` cell (the generator's GU block generalised to `code=None` + a required `ruling=` citation).
  - [DD-14.D] STATE:completed (MERGED 3a08eae 2026-08-24 ~16:5x; lane/srD 85fddf6, 9 commits: the two `\g` rows carried NO_PORT — the design's 'decline branch' premise was stale — so the job was wiring aport + pcrec_brport_g's `<`/`'` arms via two mod_recursion.c exports; tests/recursion 371/0, run_recursion_diff 7/7, both `\g` rows built, S167 (S-SR15) DETECTED, backrefs corpus unchanged 662/0 + diffs green, strict, anchors 163/173, D69 27 rows all as expected, make test corpus 25,241/0 (the one red = my gentimeout control fix postdating its base), registry/reject populations ±2 as predicted, a reject pin re-pointed; tests/codegen/run_recursion_identity.sh = the wave-E SEED (default axis, pin ac4917d, 2568 patterns / 130 call-bearing / 2198 identical / 0 differing / ctl_bad 0 — its positive control caught a classifier draft that read every atomic group as a call). Was: lane/srD, sonnet) — WAVE D: the `\g` tails and the zero family (§11).
  - [DD-14.E] STATE:completed (MERGED 85361cd 2026-08-24 ~21:4x; lane/srE d69cfc2, 11 commits, +1196/−142, rebased onto post-F main with two conflicts resolved (gen_corpus.py file list; tests/recursion/CLAUDE.md where LB's closure of the parked cells superseded E's stale bullet): [DD-14.EMPTY] at the emitter's search-entry prologue (measured: engine selection precedes the call graph; a width comparison against RX_VM_ROOT_MINW = 2^40; conditional on the root reaching the ceiling — four corpus patterns; identity holds), the sibling cells ruled `n`, S169 DETECTED two-red/one-green; S157 CLOSED AS DETECTED (a deleted match via automatic possessification of the callee's `a?`, not the predicted hang; SAB_EXPECT 20/6); the prefilter predicate was B+C's (S165) — E fixed the listing's phantom flag and added prefilter.rxt (§8.2's counterexample, three doorways, unanchored); the FOUR-AXIS gate: 2610 patterns, 168 call-bearing / 2442 call-free, ctl 168/168 every axis, raw+stripped with stamp-moved a failure, failing direction demonstrated, classifier self-test 22/22 incl. F's DEFINE arm; make test 25,463/0; strict; anchors 168/178; 80 rows unexpected 0. Was: lane/srE, opus) — WAVE E: engine selection, prefilter predicate, the four-axis identity gate; D71.6 rung admission declines call-bearing bodies.
  - [DD-14.F] STATE:completed (MERGED 514f154 2026-08-24 ~19:4x; F-MERGED-TREE BATTERY GREEN: test 25,423/0, resource 19/19 solo, strict, san rc=0 zero reports; lane/srF 1ddb8a1, 11 commits: all four §8.1 families ALREADY compiled and agreed with 10.46 (18/18) — the inventory was missing, not the behaviour — landed as RF_INDEX rows (--list-syntax 118→128, families 106→90 lines, recursion rows 26→36 all built, SR-8 qualifying 66→75); the quant column wrong on THIRTEEN rows not nine (91/91 quantified spellings compile); `(?(DEFINE)` = a tailed row on `(?(` with the `)` in the tail (`(?(define)`/`(?(DEF)` are name conditions on 10.46), ANY_ENGINE (a definition is zero-width; `--engine=dfa` makes a pure DFA of a `{0}` body), lowered as A_REP{0,0} — callgraph.c/emit_vm.c gained no line; no 'non-definition body' refusal exists on 10.46 (measured); codegen rule 4: DEFINE and `{0}` spellings emit the same program byte for byte; check_index_shape_witnesses with the expected refusal DERIVED from pcrec_registry_arbitrate (the `(?01)`-vs-`(?1)` family/row distinction); RF_INDEX generalised past verbs across five surfaces; compliance refresh — the survey row had read REJECTED since B+C, now OK-LIMITED, LB's annotation re-measured (offset 9, err 125 both sides); define.rxt 12 blocks, realworld.rxt = [LIB] entry #1 (orig/factored/DEFINE agree on 85 subjects; 1 MB and deep-repetition subjects excluded pending G/FB), zerodef DEFINE twins; tests/recursion 553/0; make test 25,423/0; anchors 167/177; D69 rows unexpected 0; identity 2199/2199 default axis (the classifier learned DEFINE — the gate caught it). S-SR2a recorded as owed by [V-H]. Was: lane/srF, opus) — WAVE F: registry families (D71.3), the `(?(DEFINE)` row (D71.4), compliance refresh.
  - [DD-14.G] STATE:started (2026-08-24 ~21:5x, lane/srG from 85361cd, opus, brief scratchpad/brief_srG.md. RULING ~22:1x on the elision rule (manager, D26-derived; Frank may veto): OPTION (i) FIDELITY — dead call-only-reached groups are elided from ENGINE SELECTION only; the artifact declares them as PCRE2 reports them (MEASURED: `(?(DEFINE)(?<g>a))(x)(?&g)` CAPTURECOUNT 2, g1 UNSET, g2 (0,1)); the BAR becomes byte-identity modulo the pattern stamp AND a named ~10-line capture-declaration filter (RX_NCAPS, the unset-fill, rx_info.ngroups/nnames/groups, the name table) plus EXACT identity on the `--no-captures` axis; option (ii) (dead groups vanish) rejected as a visible tier-1 divergence. Also approved: a per-emitted-splice-site slot family for the saved W (nesting excluded by the cycle rule); no Σ* approximation arm (unreachable under 'prefilter off iff a LINKED call exists'; the spliced prefilter is EXACT). INTERIM 561adc2 ~22:2x: eligibility + composed size budget + `-fno-splice-calls` landed; discharge hoisted before the call graph (fixing a latent root-discharge drop); nfa.c inlines spliced callees exactly; dead-capture elision GENERAL (`pcrec_has_live_capture`) — four call-free `{0}` corpus patterns move VM→DFA, answers unchanged, the gate states them as an exact both-directions exception (approved); THE SPECIMEN BAR MET IN SUBSTANCE: orig/factored/factored_x all DFA + prefilter, residue = the capture declaration + RX_ALTCLS_FACTORED, every DFA-table and search-loop byte identical; the gate caught a 558-pattern unset-fill leak on its first run) — WAVE G: the splice linkage, nfa.c's approximation, prefilter restored, `A == B` control. BAR RAISED by the email specimen (docs/design/subroutines_measurements/email_specimen/, 2026-08-24): factoring with calls is today strictly worse than the hand-inlined pattern — VM forced (the `{0}` definitions' groups are captures), no prefilter (~23× on a no-`@` MB), no rungs (a STEPS give-up on 1 MB of `a` where the DFA takes 4 ms), a frame per iteration (FRAMES give-ups ~2 K iterations in). All four have one cause (the callee is a CALL) and one cure for an ACYCLIC callee: SPLICE plus DEAD-CAPTURE ELISION — a group reached ONLY through calls (its `{0}` occurrence never matches lexically) can never leave a visible capture because the return restores every slot the callee wrote (§3.1), so engine selection may treat it as non-capturing. CHECKABLE BAR: `factored.rx`'s artifact BYTE-IDENTICAL (modulo the pattern stamp) to `orig.rx`'s — the DFA engine with its prefilter — and the 85-subject + throughput tables reproduced with the three columns equal. General mechanism (Frank's 2026-08-23 rule): 'a capture no caller can observe is not a capture' belongs in the marked-set analysis, not in a DEFINE special case.
  - [DD-14.FB] STATE:started (SPEC HALF MERGED 0f62433 ~18:4x — lane/srFB cdea67c: frame_buffer_design.md 751 lines + match_api.md §10; the CODE half is queued after wave G, 11-item checklist + 3 cells + 6 rows + the `frames-buffer=N` harness directive. ASK-1 RULED by Frank ~18:3x = D73: KEEP 2048/3072; the buffer is the path around it; USER DOCS must carry the capacity, its implied subject size, the musl/small-stack caveat and the `_in` remedy — a [REL-META] obligation. SPEC HALF 2026-08-24 ~18:0x, lane/srFB from bf07d31, opus, docs-only, brief scratchpad/brief_srFB.md: the API shape at docs/spec/match_api.md + docs/design/frame_buffer_design.md with alternatives measured, ASK 2's stamped default calibrated by measurement, the implementation checklist; the CODE half follows wave G) — (specimen note 2026-08-24: a non-recursive `(?&x)*` costs one surviving frame PER ITERATION because a call frame is a resume frame that outlives its return (§5.1, S-SR3) — the 2048-frame default gives up ~2 K iterations in on the factored email pattern; the buffer is the remedy for genuinely recursive depth, SPLICE (wave G) for the acyclic case) D71.2 the CALLER-PROVIDED FRAME BUFFER: API shape at docs/spec/match_api.md under D40, versioning per [DD-3]; a spec lane first, then the emitter change (byte-identical default artifacts).
  - [DD-14.D27] STATE:started (EXTRACT merged 461b361 ~20:2x after the manager scrubbed mechanism names from its withheld list; CELL `worktrees/sr27-cell` built ~20:3x (allowlist: the extract, the sr/la/br oracle chain + pcre2_ctypes, the two specimen .rx, testing.md, pcrec.h, prebuilt build/); BLINDED AUTHOR sr27 (opus) DELIVERED ~20:3x: 10 files, 200 blocks, 569 cases + 433 g = 1,002 expectations, a generator whose intent is oracle-checked, an independent checker, a two-arm features check (found `(?J)` needs `backrefs`), a PERL ARM (414 cells run, 403 exact, 71 spellings perl refuses, the predicted atomicity divergence MEASURED NEGATIVE, 6 divergence rows); copied to worktrees/sr27 b2a8bb3. PRE-E ACCEPTANCE 1,016/1,031: all 15 failures = K34 (pcrec `frames` where libpcre2 concludes nomatch on a runaway left recursion), 0 corpus-wrong. LANDING (brief scratchpad/brief_sr27land.md, after E merges): the K34 cells park in tests/known_fail/k34_leftrec_giveup.rxt under the ratchet, the rest rides make test; the author's findings (1) `\K` reached by a call from inside a lookaround compiles and fires on 10.46 and (2) n=342 matches / 343 gives up become design/extract amendments) — the blinded corpus with the PERL ARM (D71.5), M6.6.3's cell shape; the SPLICE-vs-LINKAGE self-oracle rides wave G.
  - [DD-14.K34] STATE:completed (MEASURED, lane/srK34 471f393 + the manager's R9 correction, merged ~22:4x: the rule pinned from pcre2_match.c — five conjuncts incl. the `last_used_ptr` lookahead high-water mark; 65/65 cells; the START-OPTIMIZE confound neutralised; pcrec's classes measured on the built module (the lane had run pcrec without --features all and misread the refusal as 'unbuilt' — corrected). RECOMMENDATION pending Frank's ruling: do not adopt the guard (a faithful copy threads a high-water mark through every fail site); the 11 D27 cells stay parked as OK-LIMITED's second limit kind) — PCRE2's RECURSION-LOOP RULE, MEASURED, and pcrec's answer (K34, found by the D27 author 2026-08-24): libpcre2 10.46 returns a clean NOMATCH on `(a|(?1)a)b`/"a" and `((?1)a)`/"b" (unanchored runaways), −52 on `^(a|(?1)a)$`/"aaaaab" and `^((?1)a)$`/"a" (anchored), a MATCH on `^(a|(?1)a)$`/"aaaaa" (199-deep same-position recursion with a base case), and −52 on `((?1)?a)`/"a" where pcrec matches (0,1). pcrec answers `frames` on every runaway. Charter: (1) a probe matrix over {anchored, unanchored} × {base case present/absent} × {subject matches/does not} × {recursion at the first item vs after a nullable prefix} reading pcre2_match's actual rule from its source (pcre2_match.c's recursion-loop check — cite the line) — a MEASUREMENT lane, docs only; (2) then a ruling: adopt the same rule as a GENERAL mechanism in the VM (it must preserve §3.3's 199-deep match and [DD-14.EMPTY]'s nomatch), or document the give-up as pcrec's answer (D26: a give-up is not a false answer) and keep the D27 cells parked. Blocks nothing; owed before the module's compliance page can say more than OK-LIMITED about left recursion.
  - [DD-14.CLOSE] STATE:not-started — D69-tier close: full sabotage matrix, battery, gate, compliance refresh, archive.
- [DD-3] STATE:not-started — generated-API versioning/compat policy for vendored consumers (before M3) (R1 A-10)
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
- [OS-4] STATE:not-started — anchoring: ENG_UNANCH vs ENG_ATTEMPT is ALREADY a cartesian split, and it has never passed this test. It exists because the reverse machine cannot check `^` at pp == 0, not because a per-start attempt loop was measured to be faster. Measure the cost of the split on the known-slow shape (`^` on only some branches, D8) and decide whether to close it by building the reverse BOT variant (DD-7) or to keep it with a number attached. An unjustified axis in the shipped compiler is the strongest possible test case for D18's own rule

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
- [OPT-A] STATE:not-started — ALGORITHMIC search optimization, and research is part of the work: pcrec is open source and pulling from other open-source engines is the point. Survey before hand-tuning. Leads recorded in D21: rare-byte prefilter selection (ripgrep/Hyperscan choose the RAREST byte by frequency; we choose memchr only at exactly one escape byte and otherwise fall to a bitmap — this attacks our case (d) path directly), memchr2/memchr3 for the 2-3 escape-byte gap, multi-byte literal search (Two-Way/Boyer-Moore/memmem) instead of scan-to-a-byte-then-step, Teddy/SIMD multi-pattern prefilter for the keyword-alternation shape M2.8 targets, reverse-inner and suffix literal selection when the prefix is weak, shift-or/bitap for short patterns, and transition-table compression (we do alphabet compression via byte equivalence classes but no table packing). Record rejections with the reason — "Teddy does not fit because X" is worth as much as adopting it. LEAD ADDED 2026-08-18 (Frank's observation, manager probe same conversation, thirtieth session; RE-OBSERVED by Frank 2026-08-21 on the [M6-READ] VM style exemplar — the readable artifact makes the per-byte spelling visible at a glance, where the original observation took an objdump session; recorded as a measured side benefit of M6-READ, not a new item): LITERAL-RUN COALESCING on the VERIFY path — the memmem lead above is scan-side; its verify-side half is that a maximal literal run (`aabb` in `(aabbc+)`) is matched byte-at-a-time by BOTH engines, measured on the shipped emitter at HEAD 0d97d31-era main: the VM path emits per-byte `pos < n && s[pos]==c` + goto, and gcc -O2 does NOT merge them (objdump: four separate cmpb at consecutive offsets — the per-byte bounds checks and distinct branch targets defeat load-merging; a broken first grep regex initially read this as zero compares, re-measured looser), while the DFA path pays the general table machinery (rx_fcls class lookup + rx_ftr step per byte) on a degenerate linear chain with no choice structure. FIX SHAPE: coalesce maximal literal runs at emission into ONE bounds check (n-pos >= k, the same many-bytes-one-check move MRL makes for length-viability) + constant-size memcmp (gcc inlines to wide compares). SOUND by the run's own structure: no choice points inside a run (a failed run fails its alternative whole), no capture edges inside a run (an edge ends the run), intra-run failure position unobservable (start++ retry advances by one regardless). NOT [ENG-ISL] territory (no choice structure to determinize — pure spelling of an already-linear chain; a literal ISL island would degenerate to exactly this, so ISL subsumes it, but no island machinery is needed). FAVORABLE ASYMMETRY vs the [OPT-ALTCLS] stage-3 measured-no: the FIRST-set guard optimized the REJECT path, which the hybrid prefilter absorbs; literal runs sit on the ACCEPT path every successful match pays, prefilter or not. D18 unchanged: lands only with a bench-measured win under the compare.sh instruments. LEAD WIDENED same conversation (Frank: "consider multiple potential implementations... at a class of N there is some N where if-a-or-if-b wins"): BYTE-TEST SPELLING MENU — the VM emitter's per-byte-predicate menu today has exactly THREE rungs, measured on emitted artifacts: N=1 → `s[pos]==c`; ONE contiguous range (incl. 2-member `[bc]`) → the subtract/unsigned-compare idiom `(unsigned)(c-lo)<=span`; EVERYTHING ELSE → the 256-bit bitmap `rx_k1[c>>3]>>(c&7)&1`, a per-byte MEMORY LOAD — and "everything else" includes `[a-zA-Z]` (measured: two ranges → bitmap), i.e. the everyday multi-range unions (\w, hex, alnum) all pay the table. MISSING RUNGS, cheap→general: k-range unions as k range-checks (k=2,3); the 0x20-fold collapse (`[a-zA-Z]` → ONE folded range-check, also the (?i) pair shape); a 64-bit IMMEDIATE-mask test for scattered sets whose span<64 (`(mask>>(c-lo))&1`, no memory touch); OR-chains for tiny scattered N. The crossover N/shape is a MEASUREMENT question (branchless-vs-branchy matters as much as op count; and the winning spelling depends on subject BYTE DISTRIBUTION — an [ENG-PGO] hook: exemplar-informed spelling selection). INTERACTION WITH THE EMIT MODEL (Frank's recall, confirmed against the record): [DD-5] is the switch-based no-computed-goto emitter row, and the recorded evidence is engine_m4.md §8.4 (computed goto is the WRONG lever on case (f)) plus the address-taken-label compile-time superlinearity numbers in decisions.md (2004 labels/0 address-taken 2.70s vs 400 address-taken 11.21s; 8000 grinds cc1 100+ min). Address-taken labels also pin RUN-time codegen (frozen block layout/merging — plausibly the same mechanism behind this lead's measured cmpb non-merge), and gcc's own switch lowering already implements exactly this spelling menu (jump table / bit-test / compare chain by its internal cost model), which a switch-shaped emit model would get for free. TWO COUNTERWEIGHTS, both on the record: only backtrack RESUME points take `&&label` (plain goto targets don't pin — the burden is proportional to resume points, which [OPT-ALTCLS] stage 1 already reduces, 2→0 on its exemplar: rung downgrades un-pin gcc as a second-order benefit); and the computed-goto body's UNOUTLINEABILITY is what structurally protected the VM from K24's .part.0 split — any emit-model change re-opens that exposure and must carry K24's regression evidence with it
- [ENG-ABS] STATE:not-started — ENG_UNANCH absorbs `^` (the DD-7
  absorption half, re-homed here 2026-08-14, D42.7): D8 left `^` on
  ENG_ATTEMPT because the reverse machine has no position-dependent BOT
  variant; the recorded slow shape is `^`-on-only-SOME-branches
  (`(^a|b)c`). GATE (D12/D15 discipline): [BENCH-1] must first add a
  `^`-on-some-branches case and measure an actual loss — no bench case
  exercises `^` today, and unmeasured engine work is not scheduled.
  After M4, the change lands in the selection pass
  (src/opt/select_engine.c), not the pipeline driver. SECOND MECHANISM
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
