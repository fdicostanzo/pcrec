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
  patterns get a test-only surface (point 5). REFINED 2026-08-28 (below):
  a defined pattern has REFERENCE / TEST / TARGET users; the format needs
  a target-set declaration ("of these defined patterns, these are the
  compilation targets"), an included library defaulting to no targets.
- OD-5 (inherited from [V-E], Frank's Q2/K4-tier, measured never read):
  PCRE2 (?(DEFINE))/(?&name) desugar vs own reference spelling.

## 2026-08-28 (from the bench session; refines OD-4 — the target-set tension)

Frank: "there is tension in the file format as discussed in that there
will be patterns referenced which are not built. For instance, a
complex pattern may be made of smaller patterns; an included library
file only uses specific patterns — perhaps only as reference. (Note
the sub patterns may have test references, meaning a test and
compilation user.) So some way to say 'of these defined patterns,
include the following as compilation targets'."

Reading, for the requirements note: a DEFINED pattern has up to three
distinct users, and the format must let a file say which apply —
(a) REFERENCE user: another pattern composes it (a library's
sub-patterns; never an artifact of its own); (b) TEST user: a test
block exercises it directly (a sub-pattern can be tested on its own
even when it ships only inside a composite — a test consumer AND a
compilation consumer, since testing it means compiling it, but as a
test artifact, not a deliverable); (c) TARGET user: it is a
compilation target of the build — the artifact a caller links. The
mechanism asked for is a TARGET-SET declaration: "of these defined
patterns, these are the compilation targets", with the default for an
included library being NONE of its definitions (reference-only unless
named). OD-4 is refined accordingly: reference-only marking is one
end of this; the general form is per-pattern user sets, or a
file-level target list, and the test surface of a non-target pattern
is a separate question from its target-ness.

## 2026-08-29 (forty-fourth session, at the close) — the exemplar-analysis findings file IS an .rxt

Frank: "Further notes for rxt file format and exemplar analysis — the
output of an exemplar analysis is an rxt file, i.e. one settable option
in rxt is a char frequency table which can then be included as a data
file into a pattern target entry."

Reading, for [DD-13b] and [ENG-PGO] (D83 already rules the analysis runs
OUTSIDE pcrec, once per file, delivering a FINDINGS FILE pcrec accepts):
(1) the findings file's FORMAT is the .rxt dialect — no second file kind;
(2) the format gains a DATA block kind — a byte/char FREQUENCY TABLE
(the input the rarest-byte prefilter selection needs, [OPT-A]/D21's
lead) — settable like any other option; (3) a user's pattern file
`include`s/`lib`s the analyzer's .rxt and a TARGET entry (usecases_and_
outline.md §6.4: `target <prefix> = <name> with <config>`) references
the table through its config, so the same pattern can be built against
several exemplars' tables (one target line each). OD-6: the data block's
spelling (inline 256 values vs `@file:` byte-exact reference) and its
name resolution (same namespace as `config`, or its own).
