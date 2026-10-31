# docs/dev/lanes/p1dsg3_evidence/ — lane p1dsg3 evidence (P1 landmark walk, design rev 2)

Evidence cited by `../p1dsg3_report.md` (2026-10-29, opus; design + measurement only, applying
review 2026-10-29 r5 landwalk2). Historical after merge; never edited.

- `cf_next.py` / `cf_next.txt` — r5 SLOT-1: every bench row that reaches L6 on stage 1, compiled
  default (the counterfactual world, `NEXT_cf`) and `-fno-req-handoff` (the walk-world proxy):
  rev 1's two-fixed-point rows (4), rev 2's one-answer column, the admitted-case lemma (50 compiles).
- `cells.py` / `cells.txt` — the rev-2 test cells: libpcre2-8 10.46 find-all expectations through
  ctypes and each cell's pcrec stamps (6 compiles); the ctypes binding `sound_twin.py` imports.
- `sound_twin.py` / `sound_twin.txt` — r5 SOUND-2: an independent per-hit model (libpcre2 only)
  re-run on the overlapping hit stream, with the non-overlapping sabotage as its control.
