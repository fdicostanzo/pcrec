# docs/dev/lanes/predfix84_evidence/ — lane predfix84's evidence

Evidence for docs/dev/lanes/predfix84_report.md: review r84 (predspot1122) applied to the predicate documents,
with the manager's rulings of 2026-11-23. This is design evidence only: nothing here rules, and no check under
`make` reads it.

## Files

- `predfix84_model.py` — a STANDALONE python3 model, the successor of `../predspot_evidence/predspot_model.py`.
  - It LOADS predspot's model, executing it up to its line "the checks", then its FLAG engine segment. Through
    it, the older models (predfix83, preddef, predfix82, predcall, predref, predbound) load as before.
  - It then replaces named parts: RENAME (B1, parameters alpha-renamed), PARTPATH (B2), ARGREF (B3), UPTO (B4,
    `@options` position for arguments and macro bodies), the grids' arms (B5), the sweeps (B7), LIBRARY
    (`prefix_in` with its list, A5), and the candidate switches of the four open slugs (LCAND, FCAND).
  - The checks are listed by name in its output, predspot's plus RENAME, PARTPATH, ARGREF, LISTATOM, PREFIXIN,
    CONTAINS, SPOTNAME, UPTO, OPENFLAGS, PATFLAGS. PREFIXIN and CONTAINS also run the installed libpcre2-8
    through ctypes (the library is run, never read: D181).
  - SWEEP and FSWEEP run every printed three-mode line (history and `rejected:` lines skipped) against the
    starting commit 2d6270c10 under predspot's engine; any non-same status not declared fails.
  - SUCCESSOR re-runs the ten earlier models, each red declared with the digest of its own FAIL line.
  - Its verdict is its last line. It exits non-zero iff that line reports a failure.
  - Run: `timeout 3600 python3 -I -B <this dir>/predfix84_model.py`. `PREDFIX84_LIGHT=1` skips SUCCESSOR and
    SWEEP's run of the starting commit (a subprocess). `PREDFIX84_ENGINE=old` prints the starting commit's sweep table under predspot's
    engine and exits.
  - `PREDFIX84_SABOTAGE=sN` (s1..s43, its PLANTS84 table) plants one wrong rule or fact per check.
  - `PREDFIX84_SABOTAGE=all` runs every plant, one at a time.
- `predfix84_model.out` — the committed clean run.
- `predfix84_sabotage.out` — the committed plant run. Each plant must turn its target check FAIL with no
  traceback. The file gives each plant's last line and FAIL line.

## Known limit (EVID-4)

KNOWN LIMIT (EVID-4, planned, not fixed here): a NULLABLE loop body past the minimum (PCRE's trailing empty pass)
is not modelled. The check NULLABLE fails if any program the checks run has one. Also not modelled in the flag
engine: `U`, `xx`, `J`, `r` and the `a`-family. Verified present in both files by
`grep -n 'KNOWN LIMIT (EVID-4' <this dir>/predfix84_model.py <this dir>/CLAUDE.md`.

Lane files are historical after merge; never edited then.
