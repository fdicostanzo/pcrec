# docs/dev/lanes/predfix88_evidence/ — lane predfix88's evidence

Evidence for docs/dev/lanes/predfix88_report.md: review r88's ruled dispositions (record entry "2026-11-23
MANAGER — review r88 (predfold1123b): the dispositions; no owner words") applied to the predicate documents. This
is design evidence only: nothing here rules, and no check under `make` reads it.

## Files

- `predfix88_model.py` — a STANDALONE python3 model, the successor of
  `../predfold1123b_evidence/predfold1123b_model.py`.
  - It LOADS predfold1123b's model unchanged, executing it up to its line "the checks" (the older engines load
    through it), then adds the R88 extensions, each switched by `X8[0]`: NESTED and EXPRARG (refused loudly as
    "not modelled"), SAMELIST (the caller's same-name list), SPOTON (a label is on the spot only when written
    directly around it, the manager's reading), MSGS (refusals that named the wrong mechanism re-worded).
  - A libpcre2 three-mode matcher (`PC8`, ctypes on the installed library, never read: D181) runs the lines whose
    lowering the label engine cannot run: the array-count copies (built from the repeat head READ from
    library.md) and `_` into a capture's whole-name hole.
  - The checks (25), by name in its output: CONTROL, CALLFORMS, ARRAYCOUNT, REPEAT, UNSPEC, COUNT, SHORTHAND,
    NOLABEL, STACK, STACKCHAIN, SPOTON, NESTED, SAMELIST, CAPNAME, OWNERBODY, LIBLINES, TABLE, NAMEGRID, EXPAND,
    READINGS, SWEEP, NULLABLE, SUCCESSOR, QUOTES, DOC.
  - Rule sentences are PINNED per check and read from their piece (B4); TABLE reads the ownership table's header,
    column sentence, rows, cells and three-mode answer from core.md (B3); EXPAND reads its written-out forms from
    the documents; QUOTES pins each owner sentence to its own piece (B5); NAMEGRID prints every UNDECIDED cell with
    its open slug.
  - SWEEP runs every printed three-mode line at the PINNED start commit b63928b48 under predfold1123b's engine
    against today's under this one; every non-same status, move or loss must be declared, and an unused
    declaration (predfix84's inherited ones included) fails as stale.
  - SUCCESSOR re-runs the fourteen earlier in-force models through this file's `--succ MODEL PIN` mode: library.md
    is served from the commit of the model's own committed output (PINS8), nested model runs routed to their own
    pins. Each red must match its FAIL line VERBATIM in `predfix88_succ_decl.tsv`; a traceback is never declarable.
  - Each check is a unit with a timeout that names it (B9); a crash is never an accepted refusal (B7).
  - Its verdict is its last line, `predfix88_model: N checks, F failed`; it exits non-zero iff that line reports one.
  - Run: `timeout 1800 python3 -I -B <this dir>/predfix88_model.py`. `PREDFIX88_LIGHT=1` skips SUCCESSOR.
    `PREDFIX88_SABOTAGE=pN` plants one wrong rule, fact or document text (its PLANTS8 table);
    `PREDFIX88_SABOTAGE=all` runs every plant in turn, a subprocess each, under a unit timeout.
    `PREDFIX88_DUMPSUCC=DIR` writes each re-run model's output there (the declarations' source).
- `predfix88_model.out` — the committed clean run.
- `predfix88_sabotage.out` — the committed plant run: each plant must turn its target check FAIL, with no
  traceback, no engine crash, and its target named on a strict last line.
- `predfix88_succ_decl.tsv` — SUCCESSOR's declarations: model, red check, reason, the FAIL line verbatim.

## Known limits

- predfold1123b's limits hold (its CLAUDE.md), except those B8 fixed.
- A body passing its pattern parameter on to another macro is refused as not modelled (nested bodies are not run).
- A read of a binding passed inside an expression argument is refused as not modelled.
- The caller's same-name list is modelled only over a binding whose text is one rx literal (written in place).
- No caller label passes out through a call's label (`[pub = B([A = A])] & (pub.A.h: ..)` is refused), so the
  export difference of the protected shorthand (A5) is not run; the report says so.
- An unnamed capturing group is not run by the label engine; CAPNAME runs that lowering through libpcre2.
- The SUCCESSOR declarations are by red CLASS reason (documents moved since that model's delivery), each pinned by
  its full FAIL text; any change of text re-opens the red.

Lane files are historical after merge; never edited then.
