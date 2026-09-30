# Lane artmgr — report (2026-09-30)

**Task.** DOCS-ONLY requirements/design lane for Frank's 2026-09-30 idea: an
artifact manager for programs that use many pattern artifacts (static
organizer, dynamic `.so` loading, compile-on-demand, unload, a file cache, a
runtime library + CLI, finder tools). Built nothing, ran no make.

**Delivered (branch lane/artmgr).**
- `docs/design/artifact_manager.md`: the direction document. §1 compares
  today's rx_info with [V-E]. §2 covers term collisions, §3 requirements
  R1-R8, §4 layering and hazards, §5 neighbouring rows, §6 stages S1-S7 with
  D77 triggers, §7 the lens table, §8 prior art, and §9 open questions
  Q1-Q9 with recommendations.
- `docs/dev/plan.md`: the `[ART-MGR] STATE:not-started` row, placed in
  "Beyond M7" directly after [V-E]. That section's own text is "direction,
  not scheduled work ... each becomes a milestone", and its siblings
  [V-E]/[LIB] live there. The boonies section is for unscheduled one-off
  concepts.
- `docs/design/CLAUDE.md`: an entry for the new file.
- `REFERENCES.md`: four new software-documentation entries ([ccache],
  [HSserialize], [PCRE2jit], [PCRE2serialize]), each read first-hand
  2026-09-30. [Wan19+]'s cited-by list is extended.

**Findings a resuming agent needs (all in the doc).**
1. rx_info TODAY has no entry pointers, and the PREFIX (artifact identity)
   is not in it. `name` is definition identity: three configs give three
   artifacts with one name. The D115 version appears only as a comment.
2. Five entries have prefix-independent types. The three `_in` entries take
   the deliberately per-prefix `<prefix>_buffers` (match_api.md §10.2), so a
   uniform pointer table cannot carry them without a new decision (Q6).
3. K80 (the ABI guard ignores abi) is a prerequisite of any catalog header.
   K79 (prefix length moves the artifact) blocks a canonical-prefix cache.
4. macOS `dlopen` defaults to RTLD_GLOBAL and Linux to RTLD_LOCAL. Linker
   sections differ per OS (`__start_` is ELF-only), so the recommendation is
   the emitted sorted array.
5. Under compile-on-demand, the emitter's escaping of the pattern into a
   comment and a string literal becomes a code-injection boundary.
6. pcrec has no interpreter, so the cold path has no fallback, unlike
   PCRE2's JIT.
7. pcrec-bench's shim is working prior art for the dynamic loader (per-pattern
   `.so`, dlopen, abi floor). Its lessons are carried into R3.

**First step and trigger.** S1: `const struct rx_entries *entries` (five
entries, counted), plus `prefix` and `version`, appended to rx_info in one
abi event. Trigger: [V-E]'s own, unchanged (the bench shim's first
multi-pattern sub-bench, or retiring `dispatch_gen.sh`'s switch).

**Validation.** Docs only. No build and no suites. Nothing is owed.
