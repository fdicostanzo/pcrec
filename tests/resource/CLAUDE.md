# tests/resource — what compiling a pattern COSTS

Every other suite in this tree asserts something about the LANGUAGE: what a
pattern matches, which diagnostic it draws, which engine it routes to. This one
asserts something about the PROCESS — peak memory, wall and CPU time, and the
manner of failure — because K7 was a bug that no assertion about the language
could see.

## Files

- **run_resource_tests.sh** — the [M4.7b] K7 pin, now SEVEN sections (this list itself was stale — missing 1b — until [SIZECAP-CPU] below; 1c is [K67]'s): 0. **[REVW.U** ...

## Env

`PCREC` (default `build/pcrec`), `K7_MEM`, `K7_SECS`, `K7_CPU` (section 1's
own bound; see the script's own header for its current defaults, which have
moved since this paragraph was written and are not re-copied here per this
file's own K35 lesson). `SIZECAP_CPU` (default `90`, [SIZECAP-CPU]
2026-09-18) is section 1b's OWN, wider CPU budget — see that section's entry
above. Same revisit-when as D45's budgets: a LEGITIMATE case measured needing
more raises the default with the measurement recorded, never silently.

Maintenance: update this file when files are added/removed or their roles change.

History (long narrative moved verbatim, not auto-injected): `docs/dev/history/claude_md/tests__resource.md`.
