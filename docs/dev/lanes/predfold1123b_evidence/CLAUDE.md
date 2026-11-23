# docs/dev/lanes/predfold1123b_evidence/ — lane predfold1123b's evidence

Evidence for docs/dev/lanes/predfold1123b_report.md: the owner's rulings of 2026-11-23 after zero-open (record
docs/design/plan_row_bodies/COND-FAMILY.md, from count-unspecified through label-doors) folded into the predicate
documents. This is design evidence only: nothing here rules, and no check under `make` reads it.

## Files

- `predfold1123b_model.py` — a STANDALONE python3 model, the successor of
  `../predfix86_evidence/predfix86_model.py`.
  - It LOADS predfix86's model, executing it up to its line "the checks". The older models load through it. During
    the load the library is served from the PINNED starting commit 89d26b6b3 (the older readers assert on its old
    bodies); the documents checked are then re-read from the working tree.
  - It then replaces named parts, the FOLD extensions, each switched by `XB[0]`:
    - CALLFORMS: one head per name; positional entries, then named; defaults (an earlier parameter only).
    - UNSPEC: `_` laid into a position: a count bound by meaning, an option with no letters, a label with no
      label; a compile error elsewhere.
    - SHORTHAND: binding-as-label's four conditions, over user bodies and the provided ones.
    - NOLABEL: `_:` on a spot is the part with no label, not the blank mark.
    - STACK: labels stacked on one spot as equal names; a blank layer closes only itself.
    - OWNREAD: the blank mark over the defining text's own literal leaves its groups to their owner.
  - The checks, by name in its output: CONTROL, CALLFORMS, REPEAT, UNSPEC, COUNT (libpcre2 through ctypes on
    `a{,}`, the installed library, never read), SHORTHAND, NOLABEL, STACK, OWNERBODY, LIBLINES, TABLE (the ownership
    table's cells), EXPAND (the expansion drill), READINGS, SWEEP, NULLABLE, SUCCESSOR, QUOTES, DOC.
  - SWEEP runs every printed three-mode line of these documents against the starting commit under predfix86's
    engine (the FOLD extensions off). Any non-same status or moved or gone answer that is not declared fails.
  - SUCCESSOR re-runs the thirteen earlier models. Each red is declared with the digest of its own FAIL line.
  - QUOTES reads the record at the PINNED commit 89d26b6b3 with `git show`; the model never reads a branch name.
  - Its verdict is its last line. It exits non-zero iff that line reports a failure.
  - Run: `timeout 7200 python3 -I -B <this dir>/predfold1123b_model.py`. `PREDFOLD1123B_LIGHT=1` skips SUCCESSOR.
  - `PREDFOLD1123B_SABOTAGE=sN` (its PLANTSB table) plants one wrong rule or fact per check.
  - `PREDFOLD1123B_SABOTAGE=all` runs every plant, one at a time.
- `predfold1123b_model.out` — the committed clean run.
- `predfold1123b_sabotage.out` — the committed plant run. Each plant must turn its target check FAIL with no
  traceback. The file gives each plant's last line and FAIL line.

## Known limits

- predfix86's limits hold.
- Several values in a count hole are not run (the loaded engine refuses a binding of several numbers).
- The never-pass warning for a caller's label is not modelled (a body that never places its argument is refused,
  the sugar and its expansion alike).
- OWNREAD widens export as well as the owner's read; no printed line reads a blank-marked literal from outside.
- The shorthand is a text rewrite before the loaded engine runs: one binding per read, the first call that passes it.

Lane files are historical after merge; never edited then.
