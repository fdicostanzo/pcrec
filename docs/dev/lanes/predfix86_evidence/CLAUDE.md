# docs/dev/lanes/predfix86_evidence/ — lane predfix86's evidence

Evidence for docs/dev/lanes/predfix86_report.md: review r86's ruled dispositions (record entry "2026-11-23
MANAGER — review r86 (predfold1123): the dispositions; ..."), with closing-own-label (R1 of the rulings file,
recorded at commit 13fc8aa85 after this lane's cut) and label-hole-full folded where they land. This is design
evidence only: nothing here rules, and no check under `make` reads it.

## Files

- `predfix86_model.py` — a STANDALONE python3 model, the successor of
  `../predfold1123_evidence/predfold1123_model.py`.
  - It LOADS predfold1123's model, executing it up to its line "the checks". The older models load through it.
  - It then replaces named parts, the FIX86 extensions, each switched by `X86[0]`:
    - CLOSE: `_` on a spot is `[_ = ..]`.
    - CLOSEOWN: the caller's own label passes a closing body.
    - EDGES: the edges of the optional entry.
    - BLANK and DEFAULT: the label-parameter rules.
    - CONDARG: a condition passed to a body that lays it beside `&`.
    - NEVER: `pcrec.test.never` for a label never placed.
    - ZERO: a request on `0`; a condition on `0` bound alone.
    - CAPSET: a request inside a set operator.
    - CALLNAME: a sent label through the macro's name.
  - NULLPASS runs the one nullable-loop line through libpcre2 (ctypes, the installed library, never read). It uses
    a per-pass marker group and a callout.
  - The checks are listed by name in its output: CONTROL, ARGLABEL, LABELPARAM, LPRULES, CLOSE, CLOSEOWN, EXPAND
    (the expansion drill), OPTENTRY, EDGES, NULLPASS, CAPTURE, CAPSET, NEGATION, ZEROLOOP, ZEROBIND, ZEROOPEN,
    CONDARG, WHEN, NEVER, CALLNAME, PRINCIPLE, ARGSHAPES, MEANING, READINGS, SWEEP, NULLABLE, SUCCESSOR, QUOTES, DOC.
  - SWEEP runs every printed three-mode line of these documents against the starting commit a05795469 under
    predfold1123's engine (the FIX86 extensions off). History and `rejected:` lines are skipped. Any non-same status
    or moved answer that is not declared fails.
  - SUCCESSOR re-runs the earlier models. Each red is declared with the digest of its own FAIL line.
  - QUOTES checks owner sentences and record titles. R1's are read from the record at the PINNED commit 13fc8aa85
    with `git show`; the model never reads a branch name.
  - DOC checks that every formatted line occurs in the piece its tag names.
  - Its verdict is its last line. It exits non-zero iff that line reports a failure.
  - Run: `timeout 5400 python3 -I -B <this dir>/predfix86_model.py`. `PREDFIX86_LIGHT=1` skips SUCCESSOR.
  - `PREDFIX86_SABOTAGE=sN` (its PLANTSX table) plants one wrong rule or fact per check.
  - `PREDFIX86_SABOTAGE=all` runs every plant, one at a time.
- `predfix86_model.out` — the committed clean run.
- `predfix86_sabotage.out` — the committed plant run. Each plant must turn its target check FAIL with no traceback.
  The file gives each plant's last line and FAIL line.

## Known limits

- predfold1123's limits hold: EVID-4 outside NULLPASS's one program; the capture request's OUTPUT is not modelled;
  `$0` only in a value hole of a one-literal program.
- A label the caller writes inside an argument of a call made INSIDE a binding is not widened to that binding.
- A label-parameter body that writes a fixed group name is refused ("not modelled").
- NULLPASS runs one shape only: one loop `(?:BODY)*` around an optional named group, then literal text, with an
  entry `(h ?: <N)` or `(h: <N)`.

Lane files are historical after merge; never edited then.
