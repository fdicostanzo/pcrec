# docs/dev/lanes/predfix83_evidence/ — lane predfix83's evidence

Evidence for docs/dev/lanes/predfix83_report.md: review r83's ruled dispositions (record "2026-11-22 MANAGER —
review r83 (preddef1122): dispositions ruled; one correction; idiom-confirm closed on default-export (no owner
words)") applied to the predicate documents; the review's engine fixes (A1, A2, A7, A4, A5, D4 (i), A8) and check
fixes (E1, E2); the NAME-GRID check; the manager's readings of the dispositions tested. Design evidence only;
nothing here rules, and no check under `make` reads it.

## Files

- `predfix83_model.py` — STANDALONE python3 model. It LOADS lane preddef's model by executing
  `../preddef_evidence/preddef_model.py` up to its line "the checks" (definitions only, unchanged; that one loads
  predfix82's, predcall's, predref's and predbound's), then replaces named parts of the loaded engine (its header
  lists them: ANDTAG, LISTX, OWNUSE, EXPR, ARGOWN). GRID is the name grid (6 spellings x 4 occurrences x 4 read
  kinds, each cell its deciding sentence quoted from the documents, the engine's verdict, AGREE / DISAGREE /
  UNDECIDED). SWEEP runs every printed three-mode line under the old engine (`PREDFIX83_ENGINE=old`, a subprocess)
  and the fixed one, both candidates of argument-default; a move must be listed in ANSWERS_CHANGED. SUCCESSOR
  re-runs the eight earlier in-force models (preddef, predfix82, predcall, predref, predbound, predfix77, predarr,
  predscope), reads each LAST LINE and declares every red or traceback superseded, with the digest of its own FAIL
  line (a red whose content changes under its name fails). Every line it formats must occur verbatim in the
  documents (DOC). Its verdict is its last line; it exits non-zero iff that line reports a failure.
  Run: `timeout 1200 python3 -I -B <this dir>/predfix83_model.py`. `PREDFIX83_SABOTAGE=sN` (s1..s25, its header)
  plants one wrong rule or fact per check.
- `predfix83_model.out` — the committed clean run (25 checks, 0 failed).
- `predfix83_sabotage.py` — runs the 25 plants one at a time; each must turn its target check FAIL, no traceback.
- `predfix83_sabotage.out` — its committed run (25 plants, 0 not caught), each plant's last line and FAIL line.

## Known limit (EVID-4)

KNOWN LIMIT (EVID-4, planned, not fixed here): a NULLABLE loop body past the minimum (PCRE's trailing empty pass)
is not modelled; the check NULLABLE fails if any program the checks run has one. Verified present in both files by
`grep -n 'KNOWN LIMIT (EVID-4' <this dir>/predfix83_model.py <this dir>/CLAUDE.md`.

Lane files are historical after merge; never edited then.
