# docs/dev/reviews/lens_reports/ — the code review's per-lens findings

One file per lens of the 2026-09-17 code review
(`docs/dev/reviews/code_review_criteria_draft.md`, RATIFIED). Each is one
opus lane's own voice, written READ-ONLY: findings with `file:line`
citations and concrete suggestions, never a refactor. The manager's
synthesis (`docs/dev/reviews/YYYY-MM-DD-code-review.md`) dedupes across
them and ranks per A4; on any disagreement the synthesis wins.

Every finding in these files is written to the charter's admissibility
rules — A1 (cite and argue against any ruled record it contradicts, or
drop), A2 (a duplication finding names the shared abstraction: proposed
signature, call sites replaced, what varies), A3 (name the sabotage/
codegen/abi anchors bound to the code it would move), A4 (severity /
effort / blast radius), A5 (cite the metric artifact under
`tools/review/out/`).

## Files

- `emitvm_second_pass.md` — THE `src/gen/emit_vm.c` SECOND PASS, lane
  `emitpass2`. Chartered by lens 1 §4 item 1 (which named the need) and
  put on wave 1's critical path by lens 10 §4.3. Delivers the file's
  fifteen-LAYER map with the census/anchor/buffer joins, extraction
  verdicts over the rung/slot/frame layers lens 1 never reached, the
  four non-emitting passes inside `pcrec_emit_vm` with their real seams,
  the full buffer population, and one recommended sequence for all
  `emit_vm.c` work across every wave.
  **Read §0 and §3.5 first.** §3.5 is the finding that should govern
  every wave brief on this file: `tests/mech/lib/replace.py` matches
  `SAB_BEFORE` with a whole-file, line-agnostic `content.count()`, so a
  VERBATIM same-file relocation costs zero anchor re-aims — but 92 of
  the file's 94 anchors carry leading whitespace, so any extraction that
  RE-INDENTS its moved block breaks every anchor inside it. Extraction
  cost is "does the moved text keep its column," not "how many lines
  move," and the report gives the anchors-inside count per candidate.
  Three corrections to prior lens reports, each with its measurement:
  the buffer population is **58 declarations / 66 declarators in three
  sizing categories**, not 40 — and the five in the uncounted third
  category (`DERIVED_CONSTANT + margin`) would pass lens 10's stage-3
  acceptance criterion untouched; `pcrec_emit_vm` holds **29 distinct
  sabotage rows / 32 anchor records**, not lens 11's 26; and lens 11's
  `vm_build_region_saves` signature cannot compile, because the pass
  reads snapshot arrays produced by the counting pass its region table
  treats as elsewhere. Also: the non-emitting passes must NOT move to
  `src/opt/` — `src/core/internal.h:5412-5418` rules the split, and
  `Vm` is 364 lines of file-private state.

Maintenance: add a row per lens report as it lands.
