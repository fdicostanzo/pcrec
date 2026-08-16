# src/gen — C code generation

Emits self-contained gcc-dialect C from the DFA machines. Two engines (D7):
ENG_UNANCH for patterns without `^` (including `$`-bearing ones since M2.7/D8) — table-driven O(n) forward scan
(leftmost-first match end) + reverse scan (match start), with a memchr/bitmap
start-state prefilter; ENG_ATTEMPT for `^` patterns — per-start computed-goto
attempt loop with EOL-variant states. Table emission exists because gcc compile
time on huge computed-goto functions is superlinear (R1 A-3). Generated code
has zero dependency on pcrec at build or run time.

`emit_unanchored` handles EOL and non-EOL machines in ONE function on purpose
(M2.12): M2.7 forked a second copy for `$` patterns, and that fork is how the
prefilter and skip loops silently went missing from the `$` path for an entire
milestone. Under EOL every skip is bounded at n-1 and scan avoidance runs
BEFORE the accept/EOL evaluation — see D11, and note the ordering rule is the
subtle half.

## The multi-engine naming surface (OS-0b)

One output file may eventually carry several engines, one per point of the
option product, behind a generated selector (D18/D20). Of the identifiers
this emitter produces, the large majority are FUNCTION-LOCAL statics, so two
engines in two functions cannot collide on them. The file-scope names are:

- `emit_rx_abi_types` — ONCE PER FILE, shared by every engine in it, and
  ([M4.4], D44/A-2) by every DIFFERENTLY-PREFIXED generated header sharing
  one TU too: `rx_ctx`, `rx_matchfn`, `rx_callout_ref`, `rx_group_entry`,
  `rx_info`, `rx_renderfn` are fixed-literal ABI types, never `<prefix>`-
  scoped (match_api_m4.md §7/§12.7 — a compiled matcher must link directly
  as a callout for another, regardless of either one's own `--prefix`).
  Wrapped in a PREFIX-INDEPENDENT `#ifndef PCREC_RX_ABI_H` guard: the R21
  panel MEASURED that a per-prefix guard fails the exact composability case
  it exists for (two differently-prefixed headers in one TU each derive a
  DIFFERENT guard name, so both bodies redefine the same types — a hard
  redefinition error). `<prefix>_span`, the one prior file-scope type,
  RETIRED at [M4.4] (D44.2) — no compatibility alias.
- `emit_ncaps_macros` — ONCE PER FILE, PER-PREFIX (`<PREFIX>_NCAPS`,
  `<PREFIX>_UNSET`, `<PREFIX>_ERR_STEPS`, `<PREFIX>_ERR_FRAMES`).
- `emit_search_decl` / `emit_search_head`, `emit_match_decl`,
  `emit_match_caps_decl`, `emit_info_decl` — ONCE PER ENGINE, under that
  engine's own entry name(s), kept adjacent to their definitions so
  declaration and definition cannot drift apart.

The entry name comes from `engine_entry_name()` / `derived_name()` and is read
nowhere else, so a finder can hand each engine a distinct name without any
emitter learning that options have a product. Today there is one engine per
file and the name is `<prefix>_search` (plus its `<prefix>_match`/
`<prefix>_match_caps`/`<prefix>_info` siblings). Both properties are enforced
by the multi-engine block in tests/codegen/run_codegen_tests.sh, which
compiles a two-engine file; the cross-prefix guard property has its own check
there too (a two-differently-prefixed-headers-in-one-TU build).

## The VM engine joins ([M4.5b])

`emit_vm.c` is the second emitter. It does NOT fork emit_dfa.c: the artifact
prologue, the fixed ABI types, the string-literal escaper, `rx_info`, the
standalone `main()` and — under the hybrid — the whole DFA engine body are
SHARED through five exported entry points (`pcrec_gen_names`,
`pcrec_emit_prologue`, `pcrec_emit_dfa_engine`, `pcrec_emit_info`,
`pcrec_emit_main`). That is the M2.12 lesson applied before the fork happens
rather than after: M2.7 forked a second copy of the unanchored emitter for `$`
patterns, and the fork is exactly how the prefilter and skip loops silently
went missing from that path for an entire milestone. `pcrec_emit_dfa_engine`
takes a NAME and a STORAGE CLASS, so the VM's prefilter is the same emitter's
output under `static` — one copy, two callers.

The DFA-only path's output is unchanged BYTE FOR BYTE by this refactor, which
is not an aspiration: `tests/codegen/run_vm_identity.sh` is the permanent gate
and the landing evidence included a whole-corpus diff against a compiler built
from the pre-[M4.5b] commit (260/260 capture-free patterns identical).

## Files

- **emit_vm.c** — the backtracking VM as emitted specialized C
  (docs/design/engine_m4.md §2). ONE function per pattern, one label per
  pattern position, every continuation resolved at compile time into a
  fallthrough or a direct `goto`, and exactly one indirect jump (the `goto *`
  at the fail label). §2.7 is why D13's table-vs-computed-goto arbitration
  does not arise: the VM has no per-byte dispatch at all, so its one indirect
  jump is on the cold path by construction.

  The pieces worth knowing before editing it:

  - **`stv`, one flat array** (§2.4) holding capture pairs, empty-iteration
    guards and cursor low-water marks. One restore loop, one overflow bound,
    and a future slot class costs a layout row rather than a new save/restore
    path. `vm_count_slots` must mirror the emitter's own rung decisions
    EXACTLY — including the replication a bounded repeat performs — or two
    live loops share one slot.
  - **The trail** is exact old-value undo, never a clear (§3.2). The naive
    version is wrong in both directions and the three cases that pin it are in
    that section; sabotage S36 neuters it.
  - **The cursor ladder** (§2.5, `vm_det_seq`). The deterministic
    fixed-stride rung is NOT an optimization that could be deferred: without
    it an 8 MB `a*` would need 8 M resume frames in an allocation-free
    matcher. D44.1 extends it to capture-bearing bodies by deriving group
    spans from the cursor at loop exit. The rungs NOT built (disjoint-follow
    possessification, the reverse-deterministic backwards walk, the
    boundary-record rung) are named in `vm_det_seq`'s comment so they are not
    mistaken for oversights; §6.4 schedules the first at M4.6.
  - **The empty-iteration rule** (§3.3) applies IFF `rmax == -1`, and takes
    the loop's EXIT continuation rather than failing the path — the empty
    iteration's capture writes STAND. Both readings are available from the
    mechanism and only one is right; the wrong one is sabotage S38 and was
    this emitter's own first-draft bug.
  - **The two capacities** (§2.5, §4.5) are computed exactly where the
    pattern's dynamic depth is statically bounded and defaulted otherwise,
    with an honest `subject_ceiling` stamped for the residual class (D44.1).
    The defaults are BRING-UP PLACEHOLDERS — D12 rules budgets come from
    measured medians and [M4.6] takes the measurement.
  - **[M4.5c fix] the REPLICATION cap and the pre-pass's recursion.** A
    bounded repeat replicates its body (§3.3), so `{0,N}` over a
    choice-bearing body emits N copies — `((a)|b){0,4000}c` is sixteen
    characters and 3.5 MB, and gcc is superlinear in the resulting
    address-taken-label fan-out (K19). `PCREC_MAX_VM_REPEAT_COPIES` is checked
    in the PRE-PASS, before a byte is emitted; limits.h carries the
    measurement and the reason the cap is on replication rather than on size.
    Separately, the pre-pass functions (`vm_nullable`, `vm_count_slots`,
    `vm_cost`) walk `A_CAT`/`A_ALT` spines ITERATIVELY. They did not, and a
    20,000-character pattern SEGFAULTED pcrec (K20) — DD-10/D10/R1 R-2's class
    for the third time. Any new walk over those shapes needs the same
    treatment; `vm_nullable` carries the comment that says so.

    **[K22] the third bound: the REPLICATION PRODUCT, checked DURING the
    pre-pass rather than after it.** The copies cap above bounds ONE
    quantifier's factor and structurally cannot see nesting, where factors
    MULTIPLY: a depth-40 tower of `{0,2}` has a maximum factor of 2 and
    replicates its innermost body 2^40 times. `PCREC_MAX_VM_NODES` would catch
    that, and did — but it is charged during EMISSION, while `vm_count_slots`
    walks the same copy tree BEFORE emission, so the walk itself was the
    Θ(2^d) work nobody bounded and the compiler hung with no diagnostic on a
    365-character pattern. `vm_count_slots` now carries a `repl` argument (the
    product of the enclosing frames-rung factors, 1 at the root) and refuses
    above `PCREC_MAX_VM_REPLICATION_PRODUCT` before it recurses. The bound IS
    `PCREC_MAX_VM_NODES`'s value, and that identity is the check's whole
    safety argument rather than a coincidence: every replicated copy costs at
    least one `vm_charge`, so the product is a lower bound on the node count
    and the guard can only move a refusal earlier, never widen one. The REAL
    fix is [ENG-BREP]'s counter-K rung; this is the interim guard that makes
    the failure honest. Measurements: `docs/design/rungselect_impl/`.
  - **[M4.5c] the LISTING and the TRACE (DD-8, §10).** §10's one constraint —
    "the dump must be derived from the same structure the emitter walks, never
    a parallel description" — is why the listing is an EVENT STREAM (`VEvent`)
    appended by the emitter's own primitives rather than a second walk over the
    AST. `vm_lbl`, `vm_push_at` and `vm_set` each write C *and* record what
    they wrote; every listing SECTION is then a view over that one stream, so
    the sections cannot disagree with each other either. If you add a way to
    emit a label, a push or a slot write, add it THROUGH those primitives —
    the accept label was emitted by a direct `sb_printf` in the first draft and
    `tests/codegen/run_ir_listing.sh` caught it on its first run (sabotage
    S41 restores it). The `role` strings are decoration: they say WHY a choice
    point exists, never that one does, and the check pins the derivable half.

    `--trace` (`PCREC_TRACE`) emits the same program with instrumented
    macros. The traced and untraced forms keep the SAME order of operations on
    purpose — a debug build that took a different path would be a tool that
    lies — and the untraced artifact's bytes are unchanged, which
    `run_ir_listing.sh` and `run_vm_identity.sh` both depend on.

  - **[M4.5e] the D46 RUNG STAMP.** §2.5's rungs (the deterministic
    span-loop cursor, the bounded-frames rung, the unbounded-frames rung)
    are selected silently PER QUANTIFIER BODY — `vm_cursor_fits` is
    consulted once per `A_REP` node, at this file's own three call sites
    (`vm_cost_rep`, `vm_count_slots`, `vm_rep`'s real emission), so a
    pattern with two quantified bodies can and does mix rungs — until this
    close obligation (D46, docs/dev/decisions.md); now the selection is
    OBSERVABLE. **A per-artifact SCALAR summary was the first draft and was
    corrected mid-lane** (Frank's design question) precisely because it
    lies on that mixed case: a single `"cursor"`/`"frames"`/`"mixed"` value
    cannot say WHICH quantifier took which rung, and a caller pinning
    selection for one quantified body has no way to address it. The fix:
    `v->rungs`, a BITMASK (`VmRungKind`: `VM_RUNG_CURSOR`/
    `_FRAMES_BOUNDED`/`_FRAMES_UNBOUNDED`), OR'd in by `vm_rung_mark()` — a
    sixth listing primitive alongside `vm_lbl`/`vm_push_at`/`vm_set`, called
    once per `A_REP` at the same point `vm_cursor_rep` / `vm_rep`'s frames
    fallthrough already knows the rung, appending a `VE_RUNG` event AND
    setting the mask bit in one call so the two views can never drift
    apart. Emitted as three named bit constants plus the artifact's own
    OR'd `#define <PREFIX>_VM_RUNGS 0x...u` next to `RX_ENGINE`/
    `RX_ENGINE_WHY` (same VM-artifacts-only placement and §5.4
    byte-identity rationale), and as a NEW `RUNGS` listing section in
    `--emit-ir` (one row per quantifier, `at L<label> <kind> <role>`) plus
    a header `; rungs ...` summary line — all three read off the same
    `v->rungs`/`VE_RUNG` data the real walk built, never re-derived.
    `rx_info` gains no member for this: the struct's layout is the frozen
    M4 ABI (match_api_m4.md §5, D44.5's "layout below is FINAL"), so a
    field would be an abi-version-bump event this close did not take on —
    flagged for the manager rather than done here. Rung FORCING (D46's
    controllability half) has no producer yet; only the observability half
    landed at [M4.5e]. Tests: `tests/vm/run_vm_tests.sh` §5, including a
    deliberately three-way-mixed pattern (`a*(a|b){0,3}c((x)|y)+z`) that is
    exactly the case the corrected, scalar-first design would have gotten
    wrong.

  - **[ENG-BREP] POSSESSIFICATION, the ladder's first rung** (D47.1;
    docs/design/eng_brep_design.md §2). `src/opt/possessify.c` marks an
    `A_REP` whose loop no retreat can ever profitably re-enter, and this file
    is what that mark BUYS. Two shapes, because the two rungs owe different
    machinery:

    - the CURSOR rung possessified emits the scan and nothing else: no resume
      frame, no low-water slot, no trail entry. The low-water slot exists so
      the RETREAT can tell "still above rmin" from "exhausted"; with no
      retreat there is no reader, and `pos` is still the loop's entry position
      at every point (the scan writes only `<p>_cur`), so the possessive path
      reads `pos` and allocates nothing.
    - the FRAMES rung possessified keeps ONE frame for the whole loop instead
      of one per optional copy, via the new `RX_CUT` primitive: `vm_cut`
      truncates the resume stack back to a depth recorded at loop entry, at
      each COPY BOUNDARY. Not inside a copy — a one-unambiguous body still
      needs its own frames to FIND its match (`(?:a|bc)` on "bc" tries `a`
      first and backtracks); one-unambiguity says at most one branch can
      SUCCEED, not that the emitter guesses right. The cut deliberately does
      NOT rewind the trail: the frames are dead, the capture writes they would
      have rewound are not, because a failure OUTSIDE the loop still has to
      restore the loop's groups.

    Deleting the pushes instead of restructuring is NOT available and this is
    the thing to understand before editing either shape: in this VM a frame at
    an optional copy serves TWO purposes — resume when the CONTINUATION fails
    (the retreat possessification kills) and resume when the BODY fails (this
    copy cannot run, so leave the loop), which stays completely alive.

    The PREFERENCE disappears under a positive verdict, and that is the
    analysis's conclusion rather than a shortcut: on the exact-count arm there
    is one exit, and on the disjointness arm a LAZY loop is FORCED to the same
    maximal exit a greedy one tops out at (at any non-maximal exit the body
    could iterate again, so that byte is in FIRST(X), so by disjointness the
    follow cannot begin there — and the lazy conjunct rules out the match
    simply ENDING there). One emitted shape is correct for both.

    `vm_cost_rep` and `vm_count_slots` carry the matching branches. They must:
    a slot count that under-counts makes two live loops share one slot, and a
    frame requirement that under-counts is a silent cap. The payoff is
    §7's `rx_info` prediction, and it is a GATE in
    tests/possessify/run_possessify_tests.sh rather than a promise —
    `(x)(?:a|bc)+d` stamps a 512-byte `subject_ceiling` today and stamps 0
    ("no limit") truthfully once the loop owes no frames.

    Observed through `<PREFIX>_VM_STRATS`, a bitmask beside `<PREFIX>_VM_RUNGS`
    and for the same reason (the strategy is per-A_REP; a scalar lies on a
    mixed artifact), plus a STRATEGIES section in `--emit-ir`. Both are set by
    the SAME `vm_rung_mark()` call the emitter already makes at the point it
    knows what it is about to emit, so the stamp and the machinery cannot
    disagree. `-fno-possessify` denies the rewrite, and D47.3's do-or-die half
    is asserted against the STAMP rather than against the flag having been
    passed.

- **emit_dfa.c** — both engine emitters (emit_unanchored, emit_attempt), the file-scope/per-engine naming helpers, shared table/label helpers, header/comment/prologue emission. **[STD1] phase A (D37, 2026-08-13)** added the ARTIFACT STAMP: `emit_feature_comment` (a `/* Feature set: NAME (modules: LIST) */` line, in both the .c and, when paired, the .h — mirroring the existing pattern-comment convention) and `emit_feature_macros` (`#define PCREC_FEATURE_SET`/`PCREC_FEATURE_MODULES`, .c ONLY, so a .c that `#include`s its own .h never sees them twice). Both read `pcrec_enabled_set_label`/`pcrec_enabled_set_modules` (src/parse/enabled.c) — the one source for "what does the currently-installed mask mean as names" — rather than recomputing anything here. Emitted unconditionally, including for a bare invocation (which stamps `"none"`, the phase-A default): the point of D37 is that NO artifact is ambiguous about what it was built with, and case10's old `--features all` byte-identity pin (tests/cli/) was updated to compare past these 4 stamp lines rather than the whole file, since the stamp differing IS the fix, not a regression, for a base-tier pattern that never engages the gate at all. **[M4.4] (docs/design/match_api_m4.md, the MATCH-API FREEZE, 2026-08-14)** landed the announced API break mechanically: `emit_span_typedef` is DELETED (`<prefix>_span` retires, D44.2) in favor of `<prefix>_search`'s FINAL `ptrdiff_t (*caps)[2]` fourth-parameter shape; `emit_rx_abi_types` emits the six fixed ABI types once per file under the prefix-independent guard above; `<prefix>_match` and `<prefix>_match_caps` (new, unconditional) are thin wrappers that call through the existing `<prefix>_search` rather than a second, genuinely-anchored automaton — correct by construction, since `<prefix>_search`'s own leftmost-first priority makes "the reported start equals the requested position" exactly equivalent to anchored matching, not an approximation of it; `<prefix>_info` (new, one `.rodata` `struct rx_info` instance per artifact — see the deviation note below) reflects the compiled `pcrec_options.flags`, encoding, pattern text (via a new genuine C-string-literal escaper, `emit_c_string_literal` — NOT `emit_pattern_comment`, which is a comment escaper only, unsafe for a string literal), group counts, and engine choice. **[DEVIATION, REPORTED]**: `struct rx_info` is emitted WITHOUT a bare `typedef` alias, unlike the other five ABI types — `<prefix>_info` under the DEFAULT prefix `"rx"` is the literal identifier `rx_info`, and a bare typedef of that name cannot coexist with a variable of that same name in one C scope (verified directly against gcc: "redeclared as different kind of symbol"). Struct TAGS live in a separate C namespace from ordinary identifiers, so `struct rx_info { ... };` (a tag, no typedef) and a variable named `rx_info` coexist with no conflict; every reference to the type (`emit_info_decl`, `emit_info_def`) spells it `struct rx_info`, never the bare form match_api_m4.md §5's literal C snippet shows. This is the ONE of the six ABI types where the collision is reachable, because "info" is the only per-artifact entry-point suffix that is also, verbatim, a whole fixed ABI type name — flagged for the manager/panel, not silently resolved.

  **[ENG-BREP] the STRATEGY-DENIAL mask.** `emit_info_def` masks
  `PCREC_NO_POSSESSIFY` (and every later member of D47.3's deny family) out of
  the emitted `rx_info.flags`. `rx_info.flags` is D43's record of what the
  artifact DOES, and a strategy denial changes that by exactly nothing — which
  is the claim the flag exists to test. Stamping it would make two
  identically-behaving artifacts differ in their reflection surface over a knob
  with no observable effect, and would destroy the byte-identity gate that is
  possessification's own safety argument: a gate that has to FILTER a
  known-differing line is the check-design failure this project has recorded
  twice. What the ladder's choices ARE recorded in is `<PREFIX>_VM_STRATS`,
  which reports what the emitter did rather than what it was asked.

  Additional [M4.4] entry points in emit_dfa.c: `emit_c_string_literal` (the
  A-11 string-literal escaper — `"`, `\`, control bytes; non-printables use a
  fixed 3-digit OCTAL `\NNN` escape, never `\xNN`, because a hex escape has
  no digit-count limit and would glue onto a following literal hex digit,
  where an always-3-digit octal escape self-terminates), `prefix_upper` (the
  OS-0 uppercased-prefix spelling shared by the NCAPS/UNSET/ERR macros and
  `rx_info`'s `RX_NCAPS` reference), `derived_name` (prefix+suffix identifier
  builder, arena-owned, generalizing the old `engine_entry_name`), and
  `emit_match_def`/`emit_match_caps_def`/`emit_info_def` (the three new
  entries' definitions).

## Conventions

The emitter produces a self-contained .c file (or paired .c/.h if options.header_name is set). Symbols are prefixed with the user's chosen identifier (default "rx"). Emitted code must stay warning-clean under -Wall -Wextra -Werror (the harness enforces this). Future encoding backends (UTF-8) coexist here as separate files, the way emit_vm.c does.

Emitted text is ASCII-only, including inside generated comments: the artifact
is source someone else's toolchain compiles, and this project already
hex-escapes the pattern comment for the same reason.

Maintenance: update this file when files are added/removed or their roles change.
