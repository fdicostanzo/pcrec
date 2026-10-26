# docs/design/plan_row_bodies/ — plan rows that outgrew a row

Created 2026-10-12 by [PLAN-LINT] step 2 (lane plclean). A plan.md row over ~5 KB is a design document in disguise (docs/dev/reviews/plan_triage_2026-10-12.md, canonical-format rule 4): the row keeps a compact charter, one dated status and a pointer; the long-form charter and history live here, one file per row, named by the row id.

Each file is the row VERBATIM as it stood when it was moved (2026-10-12), indentation removed, under a short header. From the move on, the plan.md row is the status of record; these files are not edited to track status (a new status goes in the row, a new design in `docs/design/<topic>.md`).

## Files

- `BOXQUEUE.md` — [BOXQUEUE]'s design as agreed in discussion (2026-10-20, written directly as a body rather than moved from a row), plus requirements observed from the ctxp2d validation chain.
- `INLINE-C.md` — [INLINE-C]'s dated notes and rulings (2026-10-26, moved when the row outgrew the lint limit; new notes go here).
- `CAP-SPAN.md` — [CAP-SPAN]'s general form and first-match table as agreed in discussion (2026-10-26, written directly as a body, like BOXQUEUE.md).
- `VAR.md`, `UCP.md`, `V-E.md`, `ENG-TACTICS.md`, `K50-DD12AI-MANIFEST.md`, `OPT-SIMD.md`, `OPT-A.md`, `ENG-PGO.md`, `OPT-VMLIT.md` — the nine plan.md rows that were over 5 KB after the cleanup; each plan.md row points at its file.

Maintenance: add a file here when a plan row is split out; update this list.
