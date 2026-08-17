# [DD-13] format — Frank's design inputs (log)

Accumulates Frank's requirements, rulings-in-direction, and flagged open
decisions for the unified pattern-source/test file format, BEFORE [DD-13a]
runs. The requirements note consumes this file; nothing here is a final
ruling unless marked so. Append-only, dated.

## 2026-08-17 (row creation + same-day elaboration)

**From the row-creation conversation** (also in the [DD-13] plan row):
grown from .rxt; options/config blocks; EXEMPLAR FILE REFERENCES (large
subjects live in external files); FILE INCLUDES (extensive / machine-
generated case sets; per-engine fragments); NAMED patterns with
subroutine referencing; serves compilation source, test carrier, and
pcrec-bench sets; staged requirements → design → adversarial critique
because the format is hard to change once adopted.

**Same-day elaboration (Frank, verbatim points, lightly structured):**

1. **Per-engine options in test cases — the HOW is an open decision.**
   If the format is flexible we can specify pcre2 / python / etc options
   directly or via file reference, for use in the test cases. Frank: "i
   feel there is a decision there around how that happens. its a subtle
   point." → [DD-13b] owns this decision; the subtlety to resolve
   includes WHERE options may appear (file / section / pattern / case
   level) and how they compose across includes.

2. **Bench: ONE pattern reference, not one pattern per library** — do
   not inline every library's specific options into the pattern.
   Instead, a per-library APPLICATION block, shaped like:
   "for 'python3.x', include these files in order, then also add these
   options" — and **options CASCADE to the last reference** (ordered
   includes; later entries add to / override earlier ones). The
   pcrec/version testee is JUST ANOTHER ENTRY in this scheme — no
   special-casing of the home engine.

3. **Per-library pattern TWEAKS are fair game, within the cascade** —
   "it may be fair to tweak a pattern application for a library": a
   library's application block may adjust how the shared pattern is
   applied. Manager's sharpening to carry into [DD-13a]: keep the shared
   pattern CANONICAL and make any per-engine tweak DECLARED and visible
   in the application block (never a silent fork), or "single pattern
   reference" quietly stops being true.

4. **The same sectioning serves NON-bench use: multiple compiled
   configurations.** One source file, several configuration sections —
   e.g. an AVX2 build AND a baseline build for older CPUs — each a
   compiled unit. Convergence worth preserving: this makes a
   "configuration section" the SAME kind of thing as a bench testee —
   pcrec-bench APPROACH.md §2.4's (engine, version, build-config)
   triple — one concept, two uses.

5. **Pattern visibility: interface vs reference-only.** Some patterns
   have an INTERFACE (exported entry points); others exist only to be
   REFERENCED by later patterns (private definitions). Codegen
   consequence: only interface patterns emit entry points;
   reference-only patterns are inlined at their reference sites.
   Tension to resolve at [DD-13a]/[DD-13b]: [V-G] wants every named
   part independently testable — reference-only patterns likely still
   want test cases (testable without being exported); decide whether
   testability implies a (test-only) compiled surface.

Open-decision ledger so far (all [DD-13b] unless noted):
- OD-1: where per-engine options live and their composition rules
  across includes (point 1; cascade direction ruled by point 2 —
  ordered, last reference wins — the remaining question is placement
  and scoping).
- OD-2: the declared-tweak mechanism for per-library pattern
  application (point 3).
- OD-3: configuration-section syntax unifying bench testees and build
  variants (point 4).
- OD-4: interface/reference-only marking, and whether reference-only
  patterns get a test-only surface (point 5).
- OD-5 (inherited from [V-E], Frank's Q2/K4-tier, measured never read):
  PCRE2 (?(DEFINE))/(?&name) desugar vs own reference spelling.
