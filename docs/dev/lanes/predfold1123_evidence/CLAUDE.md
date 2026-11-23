# docs/dev/lanes/predfold1123_evidence/ — lane predfold1123's evidence

Evidence for docs/dev/lanes/predfold1123_report.md: the fold of every ruling of the record from the 2026-11-22
late entries through "binding-fixed" (2026-11-23), plus zero-open (R1 of the rulings file; recorded on
lane/pred-rev28 after this lane's cut), into the predicate documents. This is design evidence only: nothing here
rules, and no check under `make` reads it.

## Files

- `predfold1123_model.py` — a STANDALONE python3 model, the successor of `../predfix84_evidence/predfix84_model.py`.
  - It LOADS predfix84's model, executing it up to its line "the checks". Through it, the older models load as
    before.
  - It then replaces named parts, the fold extensions: the caller's own label inside an argument (argument-label),
    the label parameter (`A(l:)`, `_:`, `l = x:`, sent inside an argument, passed on), the optional entry `?:`,
    the capture request (`capture("name")` on the set side, `rx & capture("name")`), an effect under negation
    (with `when`'s body read from library.md), `0` in a loop, `0` read open (zero-open), `$0` in a value hole, a
    condition on `0` bound alone, and the label set's precedence beside `|` (the manager's syntax reading).
  - The checks are listed by name in its output: CONTROL, ARGLABEL, LABELPARAM, LPRULES, OPTENTRY, CAPTURE,
    NEGATION, ZEROLOOP, ZEROBIND, PRINCIPLE, ZEROOPEN, ARGSHAPES, READINGS, SWEEP, NULLABLE, SUCCESSOR, QUOTES, DOC.
  - SWEEP runs every printed three-mode line (history and `rejected:` lines skipped) of these documents against
    the starting commit under predfix84's engine; any non-same status or moved answer not declared fails.
  - SUCCESSOR re-runs the earlier models, each red declared with the digest of its own FAIL line.
  - QUOTES checks the owner sentences and record titles cited, R1's against `lane/pred-rev28`'s record (read
    with `git show`, never merged).
  - Its verdict is its last line. It exits non-zero iff that line reports a failure.
  - Run: `timeout 5400 python3 -I -B <this dir>/predfold1123_model.py`. `PREDFOLD_LIGHT=1` skips SUCCESSOR.
  - `PREDFOLD_SABOTAGE=sN` (s1..s24, its PLANTSF table) plants one wrong rule or fact per check.
  - `PREDFOLD_SABOTAGE=all` runs every plant, one at a time.
- `predfold1123_model.out` — the committed clean run.
- `predfold1123_sabotage.out` — the committed plant run. Each plant must turn its target check FAIL with no
  traceback. The file gives each plant's last line and FAIL line.

## Known limits

- predfix84's KNOWN LIMIT (EVID-4) holds unchanged (a nullable loop body past the minimum is not modelled).
- A label the caller writes inside an argument of a call made INSIDE a binding is not widened to that binding.
- `$0` is read in a value hole of a one-literal program only; the `pcrec.test.*` warnings are not modelled.

Lane files are historical after merge; never edited then.
