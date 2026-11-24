# docs/dev/lanes/predfold1124_evidence/ — lane predfold1124's evidence

Evidence for docs/dev/lanes/predfold1124_report.md: the owner's 2026-11-23 (late) rulings folded into the predicate
documents (shorthand-is-callers, capture-in-set, exact-count-unspecified, path-rules; the manager's two closures that
stand; R-1 options-reach-constants and R-2 option-hole-explicit from the lane's rulings file). This is design
evidence only: nothing here rules, and no check under `make` reads it.

## Files

- `predfold1124_model.py` — a STANDALONE python3 model, the successor of
  `../predfix88_evidence/predfix88_model.py`.
  - It LOADS predfix88's model unchanged, executing it up to its first check (`unit("CONTROL"`), and three of its
    later definitions verbatim (the ownership table's readers, predfix84's declarations, `heads8`). The older
    models load through it.
  - Its extensions, each switched by `X9[0]` (off for SWEEP's control):
    - SHORT9: the shorthand label is the caller's own; `B(A)` read through `A.` is `B([A = A])` whatever the body
      does with the spot (condition 1 kept; condition 4 is predfix88's arm for the caller's own labels).
    - PATH9: path rule 2 (no underscore label crossed unless it is the start), and rules 1 and 4 for a middle label
      stacked directly in the step before it (the chain normalised for the loaded engine).
  - The checks, by name in its output: CONTROL, SHORTHAND, PATHS, STACKCHAIN, TABLE (the ownership table's cells,
    read from core.md), NAMEGRID (spelling x occurrences x read kind; each cell's deciding sentence read from its
    piece), LIBLINES, EXACTCOUNT, CAPSET, OPTIONS, FLAGS (R-1, R-2 on predfix84's flag engine), PARKED, EXPAND,
    READINGS, SWEEP, ERRSWEEP, NULLABLE, SUCCESSOR, QUOTES, DOC.
  - SWEEP runs every printed three-mode line of these documents against the starting commit 172930848 under
    predfix88's engine (the extensions off); a non-same status or a moved or gone answer that is not declared fails.
  - ERRSWEEP runs every printed compile-error line of the base files; it lists every line of the starting commit
    whose legality changed.
  - SUCCESSOR re-runs predfix88 and the fourteen models it re-ran, each with library.md served from its PINNED
    delivery commit, through predfix88's `--succ` runner. Each red is declared in `predfold1124_succ_decl.tsv` by
    its FAIL line VERBATIM with a reason; a traceback is never declarable.
  - QUOTES reads the record at the PINNED commit 172930848 (and R-1/R-2's entries at db8382c63) with `git show`.
  - Its verdict is its last line, `predfold1124_model: N checks, F failed`. It exits non-zero iff that line reports
    a failure. Each check is a unit with a timeout that names it.
  - Run: `timeout 5400 python3 -I -B <this dir>/predfold1124_model.py`. `PREDFOLD1124_LIGHT=1` skips SUCCESSOR.
  - `PREDFOLD1124_SABOTAGE=pN` (its PLANTS9 table) plants one wrong rule, fact or document text per check;
    `PREDFOLD1124_SABOTAGE=all` runs every plant, one subprocess each.
- `predfold1124_model.out` — the committed clean run.
- `predfold1124_sabotage.out` — the committed plant run. Each plant must turn its target check FAIL with no
  traceback and no engine crash; it ends `P plants, 0 not caught`.
- `predfold1124_succ_decl.tsv` — SUCCESSOR's declarations: model, red check, reason, its FAIL line verbatim.

## Known limits

- predfix88's limits hold.
- PATH9 is a text check before the loaded engine: it finds part labels in the expression, a binding's text and a
  macro's body at its call (rule 5). A label held deeper, through a used binding inside a used binding, is left to
  the loaded engine.
- The chain normalisation drops only a middle label stacked DIRECTLY in the step before it; any other chain goes to
  the loaded engine as written.
- The never-pass warning is not modelled (a body that never places its argument is refused).
- Path-rules readings (d) (the blank label is never a start) and (g) (no label `t`) are untestable: no program can
  spell them.
- R-1 (b) (a name string is unaffected) is untestable on the flag engine; R-2 (a) for a macro's parameter is not
  modelled (the flag engine resolves an option hole's name as a binding only).
- The loaded engine's refusal text for a capture request in a set still says "open capture-in-set".

Lane files are historical after merge; never edited then.
