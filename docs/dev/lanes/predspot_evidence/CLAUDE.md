# docs/dev/lanes/predspot_evidence/ — lane predspot's evidence

Evidence for docs/dev/lanes/predspot_report.md: five owner rulings of 2026-11-22 folded into the predicate
documents. GROUP 1 (labels): argument-default, wrapper-export, transform-export. GROUP 2 (flags): program-options,
hole-flags. The manager's readings of the brief are tested here too. This is design evidence only: nothing here
rules, and no check under `make` reads it.

## Files

- `predspot_model.py` — a STANDALONE python3 model.
  - It LOADS lane predfix83's model, executing it up to its line "the checks". That model loads preddef's,
    predfix82's, predcall's, predref's and predbound's.
  - It then replaces named parts of the label engine. Its header lists them: RULED, TEMPLATE, SPOTLIST,
    SPOTGROUP, OWNTEXT, REASON, LIBRARY.
  - It adds a FLAG engine. A program is a program file and a library file, each a list of `@options(..)`
    statements and bindings. There are two rules: the new one (hole-flags) and the old one (flags-scope,
    2026-11-19).
  - The checks are listed by name in its output: CONTROL ... NULLABLE, SUCCESSOR, FCONTROL ... FSWEEP, QUOTES, DOC.
  - GRID is the name grid, 144 cells. FLAGGRID is the flag grid, 128 cells: 8 flags x 4 places a flag is set x
    4 readers. Each cell names its deciding sentence.
  - SWEEP and FSWEEP compare every printed three-mode line against the starting commit (75d2318bd).
  - SUCCESSOR re-runs the nine earlier models.
  - Its verdict is its last line. It exits non-zero iff that line reports a failure.
  - Run: `timeout 2400 python3 -I -B <this dir>/predspot_model.py`.
  - `PREDSPOT_SABOTAGE=sN` (s1..s29, its PLANTS table) plants one wrong rule or fact per check.
  - `PREDSPOT_SABOTAGE=all` runs every plant, one at a time.
- `predspot_model.out` — the committed clean run (27 checks, 0 failed).
- `predspot_sabotage.out` — the committed plant run. Each plant must turn its target check FAIL with no
  traceback. The file gives each plant's last line and FAIL line.

## Known limit (EVID-4)

KNOWN LIMIT (EVID-4, planned, not fixed here): a NULLABLE loop body past the minimum (PCRE's trailing empty pass)
is not modelled. The check NULLABLE fails if any program the checks run has one. Also not modelled in the flag
engine: `U`, `xx`, `J`. Verified present in both files by
`grep -n 'KNOWN LIMIT (EVID-4' <this dir>/predspot_model.py <this dir>/CLAUDE.md`.

Lane files are historical after merge; never edited then.
