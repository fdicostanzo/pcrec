# docs/dev/reviews/lens_reports/ — the 2026-09-17 code review's per-lens reports

One file per lens of the ratified code review
(`docs/dev/reviews/code_review_criteria_draft.md`, RATIFIED by Frank
2026-09-17). Each is a read-only lane's own delivery: ranked findings with
`file:line` citations, A4 severity/effort/blast per finding, A3
check-coupling for anything it proposes moving, A5 citations of the metric
artifacts under `tools/review/out/`, and a PROBED-AND-HELD list. The
manager's synthesis (`docs/dev/reviews/YYYY-MM-DD-code-review.md`) dedupes
across them and is the document Frank tours from; these are the evidence
behind it and are historical once it lands.

Entries are written self-contained by each lane and merged by the manager.

## Files

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
