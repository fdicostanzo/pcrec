# docs/dev/reviews/lens_reports/ — the 2026-09-17 code review's per-lens reports

One file per lens of the code review chartered by
`docs/dev/reviews/code_review_criteria_draft.md` (RATIFIED by Frank
2026-09-17). Each is one opus lane's own voice, read-only over the
primary tier (`src/`, `cli/`, `lib/`), delivered REPORT-ONLY — no
refactoring in the review phase. The manager's synthesis
(`docs/dev/reviews/YYYY-MM-DD-code-review.md`) dedupes across them and
ranks per A4; on any disagreement the synthesis wins.

Each report carries the charter's admissibility apparatus: A1 (cite and
argue against any ruled record it contradicts, or drop), A2 (a
duplication finding names the shared abstraction: proposed signature,
call sites replaced, what varies), A3's check-coupling annex (the
sabotage/codegen/abi anchors bound to the code a fix would move), A4's
severity/effort/blast vocabulary, A5 (cite the metric artifact under
`tools/review/out/`), and a PROBED-AND-HELD list, because a seam that is
adequately covered is a result worth as much as a finding and stops the
next wave re-arguing it.

## Files

- `lens1_semantic_duplication.md` — LENS 1 (Frank #1), lane `lens1dup`.
  Twelve ranked extracts X1-X12 over `src/`, `cli/`, `lib/`, each with its
  named abstraction; four detector groups examined and REJECTED with
  reasons; the lens-11 join table (ADDENDUM 1); and the named unreviewed
  remainder (ADDENDUM 2), which asks for a second pass over
  `src/gen/emit_vm.c` and `src/parse/rxt_source.c`. Headline: the clone
  detector's largest group is not one duplication but every function
  containing an AST spine walk, and it under-counts — 75 hand-written
  spine sites, 48 exhaustive `AKind` switches. Read §5 before acting on
  X1: the nine `atomic.c` predicates must NOT be merged into one function,
  only their traversal extracted.
- `lens5_unit_seams.md` — **lens 5, unit-testing recommendations** (lane
  `lens5unit`, base `main` @ `7d444f9e`). **Corrects the charter's own
  premise: the repo already HAS a unit tier** — ten C programs in six
  directories that `#include "core/internal.h"`, link `libpcrec.a` and
  assert an internal helper's property below any answer — with no name,
  no shared build, **four divergent flag policies**, and two of its
  scripts missing from `tests/lib/san_scripts.txt`, so
  `cpset_model_check.c` (the tree's best unit check, whose whole stated
  argument is that it reaches paths the corpus cannot) **has never been
  built under a sanitizer.** Seven recommendations: the tier's shape
  (one `tests/lib/unit_cc.sh` build helper, `san_scripts.txt`
  membership, `tests/core/` as the home for NEW core-helper checks
  rather than a generic `tests/unit/`, and a cost budget expressed as a
  shape — one gcc invocation and one spawn per SUBJECT); a
  `-include`+`BUILD_DIR` allocation-failure injector that needs zero
  `src/` edits and would have found lens 8's F1 directly (reclassified
  from lens 8's DESIGN-EVENT to LOCAL on that spelling); the
  `mrl_sat_add`/`vm_fadd`/`cg_sat_add` agreement check, whose
  requirement the tree states twice in prose and enforces nowhere; and
  unit surfaces SPECIFIED IN ADVANCE for the arena-vector and text-kit
  primitives lens 1 and lens 2 propose, so wave 1 builds them with their
  nets. Its A1 section reads the tree's **only** ruling on a unit test
  (`decisions.md:4602`, [M4.7a]'s reverted hand-built-`Ctx` test) and
  makes its distinction — fabricated input at sample size zero versus a
  helper's own total input domain against an independent oracle — a
  filing requirement for every item. Ten PROBED-AND-HELD entries, headed
  by the standing do-not: **a unit test of a rung's emitted shape would
  duplicate oracle coverage and is the thing this lens must not
  recommend.**
- `lens6_dependency_rxt_cut.md` — **Lens 6, organization / dependency
  hierarchy / the rxt cut** (lane `lens6dep`, opus, 2026-09-17). Six
  findings, none CORRECTNESS-RISK.
  **THE RXT CUT FAILS TODAY** and the drag is exactly one symbol:
  `core/compile.o::compile_driver` → `pcrec_rxt_compose`, which pulls
  `rxt_compose.o` → `rxt_source.o` (`pcrec_rxt_prefix_from_name`, W23's
  derived-identifier lookup) → `rxt_schema.o` (13 accessors). Minimal cut:
  a composer hook `compile_driver` leaves NULL plus splitting
  `pcrec_compile_defs` (one caller, `cli/main.c:1196`) into its own TU —
  2 files edited, 1 added, **0 checks staled** (`grep -rn "rxt_compose"
  tests/` → 0 hits), no `abi` event.
  **But the size case is already discharged by a link flag**: a four-arm
  measurement finds `-Wl,-dead_strip` alone recovers 43,968 of the tier's
  44,448 `__text` bytes with no source change, leaving 480 bytes and two
  live symbols — so the source cut buys archive-member selection and
  dependency honesty, not kilobytes. Cheapest actionable item in the whole
  report is therefore a doc hunk: `match_api.md` §8.0's worked example
  should link with `-dead_strip`.
  **On layering, the sharpest finding is about the INSTRUMENT**: the
  include graph's 6 back-edges are all `src/gen/enc/enc.h`, but a
  call-level layer matrix built from `nm` finds **39**, and 31 of them are
  invisible to any include-based tool because `src/core/internal.h`
  declares them all — `pcrec-check-design-lessons`' controls-share-a-source
  shape at the instrument level. `internal.h` is measured as a god-header
  (5,522 lines, 225 declarations of which **32 are defined in `src/core/`**,
  included by 52 of ~55 TUs, #2 churn hotspot at 171 touches).
  `src/gen/enc/` is judged MISFILED rather than wrongly included — every
  one of the six back-edges reads only the seam's DATA half (`max_cp`,
  `fold`, `start_cls`, `name`) and none reads its TEXT half, because three
  of the four recorded D58 seam events since [M5-SEAM] added a reader
  outside `gen/` and the filing was never revisited; no D-row rules the
  path, so a move to `src/enc/` takes `include_backedges.tsv` to zero for
  6 sabotage re-aims and two recipe sentences. Also: `core/` is two layers
  wearing one name (20 of the 39 back-edges are the pipeline driver, which
  belongs at the TOP), and the four `*_dump.c` CLI surfaces (2,773 lines)
  are filed under `src/parse/` though they are already link-clean — the
  property R1 wants, achieved by construction.
- `lens8_error_cleanup.md` — **lens 8, error-path and cleanup
  consistency** (lane `lens8err`, base `main` @ `7d444f9e`). The
  `ctx_nomem`/`longjmp` discipline, arena ownership, partial-state
  cleanup, audited tree-wide rather than where K7 forced it. Verdict:
  the discipline holds nearly everywhere, and **one live hole is K7's
  own defect verbatim** — `Job.scr_test`/`scr_desc` (added by
  `[ART-SIZE]` after K7 closed) were never given the `Ctx`
  back-pointer, so `sb_grow`'s failure path `abort()`s and kills the
  caller's process, reachable on any VM compile that takes the cursor
  rung. Six further findings (a `libdirs` leak on `cli_parse`'s own
  failure at both call sites; `emit_state_legend` silently changing the
  emitted artifact on OOM; `rxt_source.c` running two disciplines for
  one event; unobserved write errors on the `-o -` path; a half-written
  `.c`/`.h` pair) plus a check-design finding: the discipline has ZERO
  sabotage rows, its one positive control
  (`tests/resource/run_resource_tests.sh` section 2) is SKIPPED on
  darwin and can pass on a budget refusal rather than an allocator
  failure. Thirteen PROBED-AND-HELD entries, headed by the 1:1
  `Ctx`/`setjmp` pairing with no failing allocation in any pre-`setjmp`
  window (R20's tier-1 class structurally closed), the complete
  `volatile` discipline across `setjmp` backed mechanically by
  `-Wclobbered`, zero `free()` of an arena-backed pointer across 76
  sites, and zero function-local statics (library re-entry is clean).
- `lens10_emission_kit_charter.md` — **lens 10, emission-kit unification: the
  WAVE 1 CHARTER** (lane `lens10kit`, opus, review + measurement). Chartered
  from lens 2's mechanism map to be precise enough to brief implementation
  lanes from; delivers the kit API, a five-stage plan with per-stage anchor
  populations / abi verdicts / byte-neutrality proofs / rollback shapes, and
  the risk list. **Its first job was the D77 measurement lens 2 named and
  deliberately did not build, and the answer closes the template layer rather
  than deferring it: the population is 1**, and that one run performs zero
  prefix substitutions.
  Read it for three findings that change the charter rather than confirm it.
  **(1) The metric measured a shape the code had already eliminated** — the
  emitters write contiguous literal blocks as ONE `sb_printf` with a multi-line
  concatenated format, so counting *calls in a row* finds 1 of the **28**
  single-call blocks spanning ≥5 source lines (largest: 369 lines / 8,884
  emitted bytes at `emit_dfa.c:681`); *a proxy metric that counts the symptom
  of a shape goes stale the moment somebody fixes the symptom by hand, and then
  reports the underlying population as absent.* **(2) L2-3's 652 is not what it
  counts** — the `grep -o '%s_'` reproduces exactly, but positional pairing
  shows **306 of 584 (52.4%)** bind the prefix and the rest bind the
  *uppercased* prefix (139), a machine name, a tag or a function name; and
  **460 of 771 calls are MIXED**, holding 49,749 of 77,258 literal bytes, which
  `pcrec_enc_emit_text` structurally cannot reach. **(3) The fragment layer's
  correctness payoff is LATENT and lens 2's acceptance number would pass before
  the wave ran** — **zero** of the 43 `snprintf`-into-a-literal-sized-buffer
  sites can provably truncate at a legal 60-byte `-p` prefix (tightest margin:
  **9 bytes**), which is the K35 shape, so the charter supplies a completeness
  criterion instead.
  Also worth reading for two A3 corrections and one instrument finding: **261
  sabotage rows are 277 ANCHORS** (16 rows carry a second, each independently
  re-aimable), of which **123 are in the two emitters** and only **4** quote the
  fragment idiom directly — not the 24 lens 2 reports, which conflated
  text-call anchors with fragment anchors; the source-text-reading check list
  is **7** `src/gen/` readers, not 5, headed by `run_cpset_structure.sh` at 24
  reads; and **the tree's only long-prefix control compiles the pattern `a`**
  (`tests/cli/run_cli_tests.sh` case 3), a trivial DFA artifact reaching
  essentially none of `emit_vm.c`'s 40 literal-sized buffers — the
  [MECH-REACH] shape, filed independent of whether wave 1 ever runs, and the
  reason the charter inserts a **stage 0** (a long-prefix full-corpus sweep)
  as a precondition rather than a cleanup.
  Its §2.4 judges the brief's own claim that retiring the buffers answers lens
  3's F6: true for L2-1, but for F6 it **DISSOLVES** the question rather than
  answering it — a distinction a lane brief must keep, or it will produce a
  lane that thinks it has audited something it has only deleted.
  Evidence and reproduction: `lens10_evidence/` (own CLAUDE.md).

Maintenance: add a row per lens report as it lands; historical once the
synthesis is written, and never edited afterwards.
