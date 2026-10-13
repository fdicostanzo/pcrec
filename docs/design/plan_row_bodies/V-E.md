# [V-E] — full plan.md row text

Moved out of docs/dev/plan.md on 2026-10-12 ([PLAN-LINT] step 2, lane plclean): a plan row over ~5 KB is a design document in disguise (docs/dev/reviews/plan_triage_2026-10-12.md, canonical-format rule 4). The row in plan.md keeps a compact charter and the current status and points here; the text below is the row VERBATIM as it stood at the move (indentation removed). The plan.md row is the status of record from the move on; this file is the long-form charter and history.

- [V-E] STATE:not-started (2026-10-09: design pass now paired with [RXINFO-REMODEL] — Frank wants rx_info sectioned into sub-structs AND the searchable array) (D88 2026-08-29: ONE artifact per emitted file, always — an emission set is a DIRECTORY of per-artifact files + a manifest header, composition is LINKING; no multi-pattern TU; R-VE-3's cross-artifact table sharing is link-level, deferred D77) — MULTI-PATTERN COMPILATION UNITS and the DESIGN INPUT (Frank, 2026-08-26 ~21:1x, recorded, NOT chartered — no new effort at 95 % of the subscription): make `struct rx_info` the IDENTITY of a pattern in a multi-pattern unit, not the symbol prefix — (1) a nested struct of ENTRY-POINT function pointers (search / match / match_caps / the `_in` variants / info) in rx_info — the external entry surface only; D82's per-machine inline accessors (step/dead/accept) never go behind a pointer; a direct-call caller keeps the named symbol; (2) the user-facing NAME (today's prefix) + the pattern source in rx_info, so the emitter DERIVES unique C symbols per pattern and nobody types prefixes beyond a few patterns; (3) one unit-level `const struct rx_info *const <unit>_patterns[]` + count, so a caller finds an implementation by ANY rx_info field (name, source, engine, ncaps…) with a linear scan and an emitted 10-line helper (generated code stays dependency-free). Consequences: an abi bump (append at the end, the [DD-13c] shape); the first consumer is pcrec-bench's shim (40 `pb_*` accessors over rx_info today) at its first multi-pattern sub-bench — D77's trigger for the runtime surface. Two additions (Frank, ~21:2x): (4) emit the unit-level array SORTED BY NAME so lookup by name is a binary search (the emitter knows every name at generation time; the sort order is a stated contract and a check reads it off the artifact); (5) the whole surface — entry-point pointers, name, the unit array and its helper — is an OPTIONAL emit ([EMIT-SET]'s shape: a caller who only uses direct symbol calls pays nothing for a table it never reads; the deny flag masks it out of the file, answer-identity unaffected). ADDENDUM 2026-09-08 (fifty-seventh session): Frank RE-PROPOSED this independently ("an optional rx organizer — an array of rx_info structs that can be searched"), confirming the direction; two facts moved since recording — `rx_info.name`/`nentries` LANDED ([DD-13b.W1.2]), so item (2)'s identity half exists, and [TT-4M] (darwin batched-build validation) became a SECOND candidate consumer: its step-1 dispatch main() is a hand-rolled degenerate organizer, and step 2 (harness adoption), if the numbers open it, should consume THIS row's unit array instead of keeping a test-only dispatcher (general-mechanisms rule; implement-then-replace fine). D77 trigger unchanged: the first real consumer (bench shim's first multi-pattern sub-bench, or TT-4M step 2) opens the design pass. DESIGN INPUTS (Frank, 2026-09-08 evening, recorded for the design pass, NOT ruled): (a) ERROR ATTRIBUTION is a first-class requirement of any batched build — per-pattern builds attribute trivially; an .rxt-level build must attribute every error to its block (a future multi-pattern pcrec mode's diagnostic contract is compiler-like: `<file>.rxt:<line>: pattern '<name>': ...`, all errors not first-stops); D88's one-artifact-per-TU already makes GCC-side attribution free (the diagnostic names the file = the pattern), and one gcc process over N TUs keeps that while batching the spawn — the failing-member recovery is drop-the-named-TU-and-relink ([TT-4M] deliverable 4 prices it). (b) THE ORGANIZER IS A SINGLE UNIT REGARDLESS OF BUILD SHAPE — it must include every member however many .rxt files/targets contributed. Two candidate mechanisms for the design pass: the emitted SORTED array (item 4 above, binary search, needs one generation point that sees all members = the composer) vs GNU LINKER-SECTION self-registration (each artifact plants its rx_info pointer in a named section, the organizer walks __start_/__stop_ — link-composed, no central generation point, unsorted so linear scan or sort-at-init; gcc-dialect in-bounds). (c) SEVERAL INDEPENDENT SETS are wanted — a set is a link-time grouping (section name or array per set carries the set name); open sub-question: set membership declared in the .rxt (a target property — the lean, targets already live there) vs at emission (a flag).
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
