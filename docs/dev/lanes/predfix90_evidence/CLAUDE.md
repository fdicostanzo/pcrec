# docs/dev/lanes/predfix90_evidence/ — lane predfix90's evidence

Evidence for docs/dev/lanes/predfix90_report.md: review r90's ruled dispositions (A1-A12, B1-B9, C1-C9; record
"2026-11-25 MANAGER — review r90 (predfold1124): the dispositions; no owner words") applied to the predicate
documents. This is design evidence only: nothing here rules, and no check under `make` reads it.

## Files

- `predfix90_model.py` — a STANDALONE python3 model, the successor of
  `../predfold1124_evidence/predfold1124_model.py`.
  - It LOADS predfold1124's model unchanged, up to its first check (`unit9("CONTROL", `); the older models load
    through it.
  - Its extension PATH10, switched by `X10[0]` (off for the canary's and SWEEP's control):
    - a path walker over the label DAG (rules 1-6 of core/labels/rule/paths), run before the loaded engine. It
      refuses rule 2's and rule 6's walls with their own messages. It hands a part label's content over
      parenthesised (the nested form, which the loaded engine reads fully).
    - It raises "undecided" on a cell no rule decides (an opaque call, an implicit name as a middle).
  - GRID: start kind x stack (labels, walls, an expression, a hole, up to two binding levels, depth 0-3) x every
    skip, 3050 cells. Each cell's expected verdict comes from `g_eval`, a SEPARATE small evaluator written from the
    rule text, quoted in GRULE. Each legal answer is run against a regex built from the stack, in all three modes.
  - The checks, by name in its output:
    - predfold1124's CONTROL .. READINGS, run from its own text with DECLARED patches (PATCH10, each applied
      exactly once; each printed);
    - this lane's checks: CANARY, PATHS10, GRID, READINGS10 (the manager's eight readings), TABLE10 (each
      ownership-table cell's grounds), STACKCHAIN10, SWEEP, ERRSWEEP, NULLABLE (predfold1124's), SUCCESSOR10,
      QUOTES, DOC.
  - SUCCESSOR10 re-runs predfold1124 and, through predfix88's `--succ` runner, predfix88 and the fourteen models
    before it. Each red is declared in `predfix90_succ_decl.tsv` by a key with no document line numbers:
    - DOC/MARKS reds by their set of MISSING lines;
    - a red whose section prints an engine CRASH, or whose verdict counts crashes, as class CRASH;
    - every other red by its FAIL line;
    - a raw traceback is never declarable.
  - Its verdict is its last line, `predfix90_model: N checks, F failed`. It exits non-zero iff that line reports a
    failure.
  - Run: `timeout 3000 python3 -I -B <this dir>/predfix90_model.py`. `PREDFIX90_LIGHT=1` skips SUCCESSOR10.
  - `PREDFIX90_SABOTAGE=qN` (its PLANTS10 table) plants one wrong rule, fact or document text per check.
    `PREDFIX90_SABOTAGE=all` runs every plant, one subprocess each. Each plant must FAIL its target check with
    the fragment the table names, and with no traceback.
  - `PREDFIX90_SABOTAGE=mut` is the mutation gate (C9) over the arms this lane adds. It inverts every arm (the
    check must turn FAIL). It also deletes each plant's named arm under that plant (the plant must go uncaught).
- `predfix90_model.out`, `predfix90_sabotage.out`, `predfix90_mutation.out` — the committed runs at the delivered
  tip.
- `predfix90_succ_decl.tsv` — SUCCESSOR10's declarations: model, red check, class, reason, key.

## Known limits

- predfold1124's limits hold, except its untestable (g): READINGS10 runs it.
- PATH10 decides only what a text walk sees. A call whose body it cannot read, or an implicit name used as a
  middle, is undecided and goes to the loaded engine. GRID declares its 16 alone-as-middle cells undecided.
- The natives peek, atomic and hits have no direct regex in CONTROL (a listed limit).
- ERRSWEEP's reader is predfold1124's. Four compile-error lines worded "for now (" or "at `lim`" are counted and
  declared unread.

Lane files are historical after merge; never edited then.
